"""
Split and clean up discord messages ahead of any parsing

Split multi-line messages into separate per-line submessages, and strip messages of
their formatting if any.
"""

import json
from pathlib import Path

from zeusops_attendance_bot.models import AttendanceMsg, to_json


def load_attendance(filename: Path) -> list[AttendanceMsg]:
    """Process the attendance JSON"""
    with open(filename) as json_fd:
        history_json = json.load(json_fd)
    return [AttendanceMsg(**msg) for msg in history_json]


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
    text = msg.message.strip().replace("*", "").strip()
    return AttendanceMsg.new_from(msg, text, is_split=False)


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
        processed_fd.write(to_json(processed))
