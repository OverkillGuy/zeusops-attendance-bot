"""
Split and clean up discord messages ahead of any parsing

Split multi-line messages into separate per-line submessages, and strip messages of
their formatting if any.
"""

import json
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Literal

AttendanceFlag = Literal["GOOD", "BAD", "OP_DELIMITER"]


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
    created_at: datetime
    """The timestamp when the message was created/sent"""
    # FIXME: Add edited_at field
    flags: list[AttendanceFlag]
    """Emoji-based flags for that message. Informs parsing"""
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
            created_at=msg.created_at,
            flags=msg.flags,
            is_split=True,
        )

    @staticmethod
    def sort_by_timestamp(msgs):
        """Sort a list of Attendance Messages by timestamp"""
        return sorted(msgs, key=lambda m: m.created_at)

    @classmethod
    def from_dict(cls, created_at: str, **kwargs):
        """Create a new AttendanceMsg from dictionary values"""
        return cls(created_at=datetime.fromisoformat(created_at), **kwargs)

    def as_dict(self) -> dict:
        """Export as dictionary. Customized for timestamp serialization"""
        out = asdict(self)
        out["created_at"] = self.created_at.isoformat()
        return out


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
        for line in after_newline:
            messages_out.append(AttendanceMsg.new_from(msg, text=line))
    return messages_out


def clean_bold(msg: AttendanceMsg) -> AttendanceMsg:
    """Remove decorative markdown from given message"""
    text = msg.message.strip().replace("**", "").strip()
    return AttendanceMsg.new_from(msg, text)


def preprocess_history(messages: list[AttendanceMsg]) -> list[AttendanceMsg]:
    """Preprocess the given messages, splitting to line, cleaning text of format"""
    preprocessed = [clean_bold(split) for split in newline_separate(messages)]
    print(f"{len(messages)} msgs input, processed into {len(preprocessed)}")
    return preprocessed


def main():
    """Parse entrypoint"""
    loaded = load_attendance(Path("attendance.json"))
    processed = preprocess_history(loaded)
    with open("processed_attendance.json", "w") as processed_fd:
        json.dump([msg.as_dict() for msg in processed], processed_fd, indent=2)
