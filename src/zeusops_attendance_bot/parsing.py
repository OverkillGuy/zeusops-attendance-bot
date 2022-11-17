"""Parse attendance via regexes"""

import re
from pathlib import Path

REGEX_OP_SEPARATOR = re.compile(r"""(---+|===+)""")
"""Match an operation's separator"""

REGEX_SQUAD = re.compile(
    r"""
   ([A-Za-z0-9]+)         # A squad name (TODO check for SPACES?)
   \s*[:\-;]\s*         # Separator between squad: team
   ([a-zA-Z0-9\(\),;\. ]+)  # Attendance for squad, unparsed
""",
    re.VERBOSE,
)
"""Match a single line of squad attendance"""


def main():
    """Parse the cleaned up attendance text"""
    attendance_txt = Path("attendance.txt").read_text()
    op_separator_locations = [
        (match.start(), match.end())
        for match in re.finditer(REGEX_OP_SEPARATOR, attendance_txt)
    ]
    in_between_locations = [
        (end0, start1)
        for ((start0, end0), (start1, end1)) in zip(
            op_separator_locations[:-1], op_separator_locations[1:]
        )
    ]
    for start, end in in_between_locations:
        print("---")
        start_offset, end_offset = start + 1, end - 1
        op_attendance_text = attendance_txt[start_offset:end_offset]  # FIXME: Offset \n
        # print(f"Attendance for op is:\n{op_attendance_text}")
        squad_matches = re.findall(REGEX_SQUAD, op_attendance_text)
        for squad, attendance_of_squad in squad_matches:
            print(f"For {squad=}, attendance: '{attendance_of_squad}'")
            # TODO: Process the squad's attendance as regex
