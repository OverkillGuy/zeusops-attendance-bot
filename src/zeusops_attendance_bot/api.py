"""Client bindings to a REST API"""

import json

from discord import Client, Guild, Intents, TextChannel

Secret = str


class AttendanceClient(Client):
    """A discord Client for recording attendance"""

    zeusops_guild: Guild
    attendance_channel: TextChannel

    async def on_ready(self):
        """Entrypoint on app connected to discord"""
        print(f"We have logged in as {self.user}")
        # For debug purposes:
        # await self.print_memberships()
        self.zeusops_guild = get_zeusops_server(self)
        self.attendance_channel = get_attendance_channel(self.zeusops_guild)
        print(
            f"Found attendance channel with {len(self.attendance_channel.members)} members"
        )
        await save_history(self.attendance_channel)

    async def print_memberships(self):
        """Print guilds/channels we're member of"""
        for guild in self.guilds:
            print(f"Member of guild: {guild.name}, ID={guild.id}")
            for channel in guild.channels:
                print(f"Member of channel: {channel.name}, ID={channel.id}")


def get_client() -> Client:
    """Get a Discord client with necessary intents"""
    intents = Intents.default()
    intents.message_content = True
    client = AttendanceClient(intents=intents)
    return client


def run(client: Client, token: Secret):
    """Run a client's main event loop"""
    client.run(token)


def get_zeusops_server(client: Client) -> Guild:
    """Grab the Zeusops server by ID"""
    ZEUSOPS_GUILD_ID = 219564389462704130
    return client.get_guild(ZEUSOPS_GUILD_ID)


def get_attendance_channel(zeusops_guild: Guild) -> TextChannel:
    """Grab the Zeusops attendance channel by ID"""
    ZEUSOPS_ATTENDANCE_CHANNEL_ID = 817815909565202493
    return zeusops_guild.get_channel(ZEUSOPS_ATTENDANCE_CHANNEL_ID)


async def save_history(channel: TextChannel):
    """Save the entire message history of the given channel to ndJson file"""
    with open("attendance.json", "w") as json_fd:
        messages = [
            {
                "timestamp": message.created_at.isoformat(),
                "message": message.content,
                "author": message.author.display_name,
            }
            async for message in channel.history(limit=None, oldest_first=True)
        ]
        json.dump(messages, json_fd, indent=2)
        print("Completed")
