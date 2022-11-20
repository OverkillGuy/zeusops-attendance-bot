"""Library-independent object models for the attendance info"""
import json
from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel
from pydantic.json import pydantic_encoder


class AttendanceFlag(str, Enum):
    """Marker for a Discord Attendance message having a reaction emoji"""

    GOOD = "GOOD"
    BAD = "BAD"
    OP_DELIMITER = "OP_DELIMITER"
    """
    Marks the message is the first of a new Op's Attendance, no preceding op separator.

    This marker is manually put as a Discord Reaction on the message, in order to
    palliate to the lack of separator
    """


class AttendanceMsg(BaseModel):
    """Archived message from #attendance channel"""

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
    edited_at: Optional[datetime]
    """The timestamp when the message was last edited, if any"""
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

    def new_from(self, text: str, is_split: bool = True):
        """Create a new (fake) message from a real one, mostly for splitting intent"""
        new = self.copy()
        new.message = text
        new.is_split = is_split
        return new

    @staticmethod
    def sort_by_timestamp(msgs):
        """Sort a list of Attendance Messages by timestamp"""
        return sorted(msgs, key=lambda m: m.created_at)

    @classmethod
    def from_dict(cls, **kwargs):
        """Create a new AttendanceMsg from dictionary values"""
        return cls(**kwargs)

    def as_dict(self) -> dict:
        """Export as dictionary. Customized for timestamp serialization"""
        return dict(self)


def to_json(messages: list[AttendanceMsg]) -> str:
    """Export a list of messages to JSON string"""
    return json.dumps(messages, indent=2, ensure_ascii=False, default=pydantic_encoder)
