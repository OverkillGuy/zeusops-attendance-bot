"""
Split and clean up discord messages ahead of any parsing

Split multi-line messages into separate per-line submessages, and strip messages of
their formatting if any.
"""

import json
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path


@dataclass
class AttendanceMsg:
    """Message as loaded in attendance"""

    id: int
    """Discord Message ID"""
    author_display: str
    """The display name of the author of the message"""
    author_id: int
    """The Discord ID of the author of the message"""
    message: str
    """The message's content"""
    timestamp: datetime
    """The timestamp of the message"""
    is_split: bool = False
    """
    Is the message split off = should the message text be very different from discord?

    This is commonly the case when someone posts multiple lines of attendance in one
    message,or the op separator and an attendance line, which needs recorded as
    multiple things to parse.

    Defaults to False, because normally injected messages aren't processed much.
    """

    @classmethod
    def new_from(cls, msg, text: str):
        """Create a new (fake) message from a real one, for splitting intent"""
        return cls(
            id=msg.id,
            message=text,
            author_display=msg.author_display,
            author_id=msg.author_id,
            timestamp=msg.timestamp,
            is_split=True,
        )

    @staticmethod
    def sort_by_timestamp(msgs):
        """Sort a list of Attendance Messages by timestamp"""
        return sorted(msgs, key=lambda m: m.timestamp)

    @classmethod
    def from_dict(cls, timestamp: str, **kwargs):
        """Create a new AttendanceMsg from dictionary values"""
        return cls(timestamp=datetime.fromisoformat(timestamp), **kwargs)


def load_attendance(filename: Path) -> list[AttendanceMsg]:
    """Process the attendance JSON"""
    with open(filename) as json_fd:
        history_json = json.load(json_fd)
    return [AttendanceMsg.from_dict(**msg) for msg in history_json]


def newline_separate(messages: list[AttendanceMsg]) -> list[AttendanceMsg]:
    """Split messages containing newlines into new messages"""
    messages_out = []
    for msg in messages:
        if "\n" not in msg.message:
            messages_out.append(msg)
            continue
        # Newline caught: split the message
        before_newline, *after_newline = msg.message.splitlines()
        messages_out.append(AttendanceMsg.new_from(msg, text=before_newline))
        after_newline = [
            line for line in after_newline if line
        ]  # Skip evaluating repeated \n
        if len(after_newline) > 1:
            # print(
            #     f"This message is weird, multiple separate newlines: '{msg.message=}'"
            # )
            continue
        new_message = after_newline[0]
        # print(f"Split message: '{new_message}'")
        messages_out.append(AttendanceMsg.new_from(msg, text=new_message))
    return messages_out


def clean_bold(msg: AttendanceMsg) -> AttendanceMsg:
    """Remove decorative markdown from given message"""
    text = msg.message.strip().replace("**", "").strip()
    return AttendanceMsg.new_from(msg, text)


def main():
    """Parse entrypoint"""
    h = load_attendance(Path("attendance.json"))
    h2 = newline_separate(h)
    h3 = [clean_bold(message) for message in h2]
    print(f"{len(h)} msgs from Discord, Processed into {len(h3)}")
    with open("processed_attendance.json", "w") as processed_fd:
        json.dump([asdict(msg) for msg in h3], processed_fd, indent=2)
