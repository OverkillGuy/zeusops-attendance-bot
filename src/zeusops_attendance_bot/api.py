"""Client bindings to a REST API"""

import json
from datetime import datetime, timedelta

from discord import Client, Guild, Intents, Message, TextChannel

from zeusops_attendance_bot.attendance import AttendanceMsg
from zeusops_attendance_bot.parsing import process_one_line

Secret = str

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
        await save_history(self.attendance_channel, debug=self.debug)
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
        message_dict = to_dict(message)
        print(json.dumps(message_dict, indent=2))
        message_obj = AttendanceMsg(**message_dict)
        parsed = process_one_line(message_obj, datetime.now().date().isoformat())
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


def to_dict(message: Message) -> dict:
    """Format a message for archival"""
    return {
        "timestamp": message.created_at.isoformat(),
        "message": message.content,
        "author_display": message.author.display_name,
        "author_id": message.author.id,
        "id": message.id,
        "flags": flag(message),
    }


async def save_history(channel: TextChannel, debug: bool):
    """Save the entire message history of the given channel to ndJson file"""
    if debug:
        messages = [
            to_dict(message)
            async for message in channel.history(
                limit=5, oldest_first=True, after=datetime.now() - timedelta(days=3)
            )
        ]
    else:
        messages = [
            to_dict(message)
            async for message in channel.history(limit=None, oldest_first=True)
        ]
    with open("attendance.json", "w") as json_fd:
        json.dump(messages, json_fd, indent=2)
        print("Completed")
