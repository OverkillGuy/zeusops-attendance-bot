"""Client bindings to a REST API"""

from datetime import datetime, timedelta
from typing import Any

from discord import Client, Guild, Intents, Message, TextChannel

from zeusops_attendance_bot.models import AttendanceMsg, to_json
from zeusops_attendance_bot.parsing import (
    parse_full_attendance_history,
    process_one_line,
)
from zeusops_attendance_bot.preprocess import preprocess_history

Secret = str

ChannelAttendance = list[AttendanceMsg]
"""The sum of all messages of the Attendance channel, as objects"""

DiscordID = int
"""A type alias for valid Discord IDs"""

BAD_ENTRY_MARKER_EMOJI: str = "❌"
"""The CROSS MARKER Emoji in Discord for the bad-attendance-line flag"""
GOOD_ENTRY_MARKER_EMOJI: str = "✅"
"""The WHITE HEAVY CHECK MARK Emoji for good attendance line"""
NEW_OP_MARKER_EMOJI: str = "🆕"
"""The SQUARED NEW Emoji to mark next-op separator jsut before this message"""

ZEUSOPS_ATTENDANCE_CHANNEL_ID: DiscordID = 817815909565202493
ZEUSOPS_TEST_CHANNEL_ID: DiscordID = 530411066585382912


class AttendanceClient(Client):
    """A discord Client for recording attendance"""

    zeusops_guild: Guild
    attendance_channel: TextChannel
    debug: bool = False

    def __init__(self, debug, *args, **kwargs):
        """Initialize the Client"""
        super().__init__(*args, **kwargs)
        self.debug = debug
        self.listen_channels = [ZEUSOPS_ATTENDANCE_CHANNEL_ID, ZEUSOPS_TEST_CHANNEL_ID]

    async def on_ready(self):
        """Entrypoint on app connected to discord"""
        print(f"We have logged in as {self.user}")
        # For debug purposes:
        # await self.print_memberships()
        self.zeusops_guild = get_zeusops_server(self)
        self.attendance_channel = get_attendance_channel(self.zeusops_guild, self.debug)
        print(
            f"Found attendance channel with {len(self.attendance_channel.members)} members"
        )
        history_dict = await grab_history(self.attendance_channel, debug=self.debug)
        save_attendance(history_dict)
        parse_attendance_history(history_dict)
        # Exit on completion
        # await self.close()

    async def print_memberships(self):
        """Print guilds/channels we're member of"""
        for guild in self.guilds:
            print(f"Member of guild: {guild.name}, ID={guild.id}")
            for channel in guild.channels:
                print(f"Member of channel: {channel.name}, ID={channel.id}")

    async def on_message(self, message):
        """Hear messages of attendance LIVE, posting it to stdout (no parsing)"""
        if message.channel.id not in self.listen_channels:
            return
        message_obj = to_obj(message)
        print(message_obj.json(indent=2))
        message_objs = preprocess_history([message_obj])
        for msg_obj in message_objs:
            parsed = process_one_line(msg_obj, datetime.now().date().isoformat())
            if not parsed:
                return
            squad, attendance_of_squad = parsed
            print(f"For {squad=}, attendance: '{attendance_of_squad}'")


def get_client(debug_mode: bool) -> Client:
    """Get a Discord client with necessary intents"""
    intents = Intents.default()
    intents.message_content = True
    client = AttendanceClient(intents=intents, debug=debug_mode)
    return client


def run(client: Client, token: Secret):
    """Run a client's main event loop"""
    client.run(token)


def get_zeusops_server(client: Client) -> Guild:
    """Grab the Zeusops server by ID"""
    ZEUSOPS_GUILD_ID: DiscordID = 219564389462704130
    return client.get_guild(ZEUSOPS_GUILD_ID)


def get_attendance_channel(zeusops_guild: Guild, debug: bool) -> TextChannel:
    """Grab the Zeusops attendance channel by ID"""
    channel_id = ZEUSOPS_TEST_CHANNEL_ID if debug else ZEUSOPS_ATTENDANCE_CHANNEL_ID
    return zeusops_guild.get_channel(channel_id)


def is_flagged(msg: Message, emoji: str) -> bool:
    """Detect if a message was reacted to with a specific  emoji; >1 reaction suffices"""
    return any(r.emoji == emoji for r in msg.reactions if isinstance(r.emoji, str))


def flag(message: Message) -> list[str]:
    """Detect if a message was flagged (reacted for attendance)"""
    bad_flags = ["BAD"] if is_flagged(message, BAD_ENTRY_MARKER_EMOJI) else []
    good_flags = ["GOOD"] if is_flagged(message, GOOD_ENTRY_MARKER_EMOJI) else []
    newline_flags = ["OP_DELIMITER"] if is_flagged(message, NEW_OP_MARKER_EMOJI) else []
    flags: list[str] = [] + bad_flags + good_flags + newline_flags
    return flags


def to_obj(message: Message) -> AttendanceMsg:
    """Format a message for archival"""
    edited = message.edited_at.isoformat() if message.edited_at is not None else None
    return AttendanceMsg(
        **{
            "created_at": message.created_at.isoformat(),
            "edited_at": edited,
            "message": message.content,
            "author_display": message.author.display_name,
            "author_id": message.author.id,
            "id": message.id,
            "flags": flag(message),
        }
    )


async def grab_history(channel: TextChannel, debug: bool) -> ChannelAttendance:
    """Grab the entire message history of the Attendances channel as dict"""
    args: dict[str, Any] = {"limit": None, "oldest_first": True}
    if debug:
        args = {
            "limit": 20,
            "oldest_first": True,
            "after": datetime.now() - timedelta(days=5),
        }
    messages = [to_obj(message) async for message in channel.history(**args)]
    return messages


def save_attendance(messages: ChannelAttendance):
    """Save a given attendance message history to JSON file"""
    with open("attendance.json", "w") as json_fd:
        json_fd.write(to_json(messages))
        print("Completed")


def parse_attendance_history(history_msgs: ChannelAttendance):
    """Process the JSON-able dict of history into full attendance"""
    preprocessed = preprocess_history(history_msgs)
    parse_full_attendance_history(preprocessed)
