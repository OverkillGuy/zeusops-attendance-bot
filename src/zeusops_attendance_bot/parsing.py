"""Parse attendance via regexes"""

import re
from pathlib import Path

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
        # print("---")
        start_offset, end_offset = start + 1, end - 1
        op_attendance_text = attendance_txt[start_offset:end_offset]  # FIXME: Offset \n
        # print(f"Attendance for op is:\n{op_attendance_text}")
        for op_attendance_line in op_attendance_text.splitlines():
            squad_match = re.fullmatch(REGEX_SQUAD, op_attendance_line)
            # print(squad_match)
            if squad_match is None:
                print(f"Bad match: {op_attendance_line}")
                continue
            # squad, attendance_of_squad = squad_match.groups()
            # print(f"For {squad=}, attendance: '{attendance_of_squad}'")
            # TODO: Process the squad's attendance as regex
