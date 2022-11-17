"""Parse the attendance messages as string"""

import json
from dataclasses import dataclass
from datetime import datetime


@dataclass
class AttendanceMsg:
    """Message as loaded in attendance"""

    author: str
    """The author of the message"""
    message: str
    """The message's content"""
    timestamp: datetime
    """The timestamp of the message"""


LoadedAttendanceHistory = list[AttendanceMsg]


def load_attendance() -> LoadedAttendanceHistory:
    """Process the attendance JSON"""
    with open("attendance.json") as json_fd:
        history_json = json.load(json_fd)
    return [
        AttendanceMsg(
            message=msg["message"], author=msg["author"], timestamp=msg["timestamp"]
        )
        for msg in history_json
    ]


def newline_separate(messages: LoadedAttendanceHistory) -> LoadedAttendanceHistory:
    """Split messages containing newlines into new messages"""
    messages_out = []
    for msg in messages:
        messages_out.append(msg)
        if "\n" not in msg.message:
            continue
        before_newline, *after_newline = msg.message.splitlines()
        after_newline = [
            line for line in after_newline if line
        ]  # Skip evaluating repeated \n
        if len(after_newline) > 1:
            print(
                f"This message is weird, multiple separate newlines: '{msg.message=}'"
            )
            continue
        new_message = after_newline[0]
        print(f"Split message: '{new_message}'")
        messages_out.append(
            AttendanceMsg(
                message=new_message, author=msg.author, timestamp=msg.timestamp
            )
        )
    return messages_out


def clean_formatting(msg: str) -> str:
    """Remove decorative markdown from given message"""
    return msg.strip().replace("**", "").strip()


def main():
    """Parse entrypoint"""
    h = load_attendance()
    h2 = newline_separate(h)
    print(f"Before: {len(h)}, After: {len(h2)}")
