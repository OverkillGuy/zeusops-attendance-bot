"""Parse attendance via regexes"""

import re
from pathlib import Path
from typing import Optional, Tuple

from zeusops_attendance_bot.models import AttendanceFlag, AttendanceMsg
from zeusops_attendance_bot.preprocess import load_attendance

REGEX_OP_SEPARATOR = re.compile(r"""([-=:\.\+])\1\1+""")
"""Match an operation's separator: same character 3 or more times"""

REGEX_SQUAD = re.compile(
    r"""
   \*?\s*                   # Junk prefix
   ([A-Za-z0-9\-/ ]+?)      # A squad name
   \s*[:\-;]\s*             # Separator between squad: team
   ([a-zA-Z0-9\(\),;\.& ]+) # Attendance for squad, unparsed
   \*?\s*                   # Junk suffix
""",
    re.VERBOSE,
)
"""Match a single line of squad attendance"""

OperationAttendance = list[AttendanceMsg]
"""An operation's attendance can be seen as the aggregate of all the attendance messages of that op"""

Span = tuple[int, int]
"""A range of indices spanning between first item and second item"""


def split_ops_delimiter(
    sorted_attendance: list[AttendanceMsg],
) -> list[OperationAttendance]:
    """Find and group the operations by op delimiter"""
    # Check which messages match the Operation Separator regex
    opsep_matches = [
        re.fullmatch(REGEX_OP_SEPARATOR, msg.message) for msg in sorted_attendance
    ]
    # Find their index in the message list
    opsep_locations: list[int] = [
        idx for idx, match in enumerate(opsep_matches) if match is not None
    ]
    # Find iter-opsep message-index range
    in_between_locs: list[Span] = [
        (marker0 + 1, marker1)
        for marker0, marker1 in zip(opsep_locations[:-1], opsep_locations[1:])
        if abs(marker0 - marker1) > 1  # Skip multiple opseps
    ]
    first_op = [(0, opsep_locations[0])] if opsep_locations else []
    last_op = [(opsep_locations[-1] + 1, len(sorted_attendance))]
    # Recover first + last message group too, as their own range
    all_op_ranges: list[Span] = [] + first_op + in_between_locs + last_op
    return [sorted_attendance[start:end] for start, end in all_op_ranges]


def split_ops_flagged(
    grouped_attendance: list[OperationAttendance],
) -> list[OperationAttendance]:
    """
    Find and group operations flagged via reaction as lacking a separator message

    The flag OPSEP_DELIMITER on a message should imply the flagged message is actually
    the first line of attendance of a new op that is missing an actual separator
    message. This effectively replaces delimiter message, except there is now no actual
    separator message to skip anymore, so the message index offsets needs computed.

    Effectively this is a "part 2" of :py:func:`split_ops_delimiter`.
    """
    ops: list[OperationAttendance] = []
    for op_msgs in grouped_attendance:
        flag_locations: list[int] = [
            idx
            for idx, attendance in enumerate(op_msgs)
            if AttendanceFlag.OP_DELIMITER in attendance.flags
        ]
        if not flag_locations:  # No flags inside this opgroup to split
            ops.append(op_msgs)
            continue
        op_msgs_index = 0
        for flag_location in flag_locations:
            print(f"NEWFLAG: {op_msgs[flag_location].created_at.date().isoformat()}")
            msgs_before_flag = op_msgs[op_msgs_index:flag_location]
            ops.append(msgs_before_flag)
            op_msgs_index = flag_location
        if op_msgs_index != len(op_msgs):
            # Un-flagged remainers = last op
            msgs_after_lastflag = op_msgs[flag_location:]
            ops.append(msgs_after_lastflag)
    return ops


def split_ops(attendance_list: list[AttendanceMsg]) -> list[OperationAttendance]:
    """Find/group all ops, both by delimiter and by reactions flag"""
    sorted_attendance = AttendanceMsg.sort_by_timestamp(attendance_list)
    ops_by_delimiter = split_ops_delimiter(sorted_attendance)
    ops = split_ops_flagged(ops_by_delimiter)
    return ops


def process_one_line(msg: AttendanceMsg, op_date: str) -> Optional[Tuple[str, str]]:
    """Process a single attendance line, without context"""
    if "BAD" in msg.flags:
        # print(f"BADFLAGGED: Skipping message '{msg.message}'")
        return None
    squad_match = re.fullmatch(REGEX_SQUAD, msg.message)
    if squad_match is None:
        msg_author = msg.author_display
        msg_text = msg.message
        print(f"Bad squad match on {op_date} by {msg_author}. Message: '{msg_text}'")
        return None
    squad, attendance_of_squad = squad_match.groups()
    return squad, attendance_of_squad


def parse_full_attendance_history(attendance_msgs: list[AttendanceMsg]):
    """Parse a preprocessed history into sequence of messages"""
    ops = split_ops(attendance_msgs)
    for op_attendance in ops:
        if not op_attendance:
            continue  # Skip empty attendance
        # FIXME: Badflagged messages not filtered out for op date check!
        op_date = op_attendance[0].created_at.date().isoformat()
        print(f"Op date: {op_date}, {len(op_attendance)} lines")
        for attendance_msg in op_attendance:
            parsed = process_one_line(attendance_msg, op_date)
            if not parsed:
                continue
            squad, attendance_of_squad = parsed
            print(f"For {squad=}, attendance: '{attendance_of_squad}'")
            # TODO: Process the squad's attendance as regex


def main():
    """Parse the cleaned up attendance data"""
    attendance_msgs = load_attendance(Path("processed_attendance.json"))
    parse_full_attendance_history(attendance_msgs)
