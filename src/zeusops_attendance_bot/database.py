"""Generate a sqlite database from the parsed attendance data"""


import json
from pathlib import Path

import sqlite_utils

from zeusops_attendance_bot.models import OperationAttendance


def create_tables(db):
    """Create the DB tables for attendance"""
    db["users"].create({"name": str}, pk="name")
    db["operations"].create(
        {
            "date": str,
            "attendance_count": int,  # How many joined
        },
        pk="date",
    )
    db["attendance"].create(
        {"id": int, "operation_date": str, "user": str, "role": str},
        # pk=("operation_date", "user"),
        pk=("id"),
        foreign_keys=[
            ("operation_date", "operations", "date"),
            # ("user", "users", "name"),
        ],
    )


def populate(db_path, ops: list[OperationAttendance]):
    """Populate the database of attendance"""
    db = sqlite_utils.Database(db_path)
    create_tables(db)
    for op in ops:
        op_date = op.op_date.isoformat()
        db["operations"].insert({"date": op_date, "attendance_count": op.user_count})
        for squad_attendance in op.attendance:
            for member, role in squad_attendance.members:
                db["attendance"].insert(
                    {
                        "operation_date": op_date,
                        "user": member,
                        "role": squad_attendance.squad + " " + role
                        if role is not None
                        else squad_attendance.squad,
                    }
                )


# Compare: 245 ops in #attendance chan = 245 rows in operations table
# vs
# 245 rows (in #attendance) where role in
# ["HQCO Zeus",
#  "HQCO",
#  "HQ/CO Zeus",
#  "HQCO zeus",
#  "HQ1PLT Zeus",
#  "HQCO Z",
#  "Zeus L",
#  "CO Z",
#  "CO zeus",
#  "COPLT Zeus",
#  "Zeus"] sorted by id


def main():
    """Save to database the data"""
    ops = load_attendance("parsed_attendance.json")
    populate("attendance.db", ops)


def load_attendance(filename: Path) -> list[OperationAttendance]:
    """Process the attendance JSON"""
    with open(filename) as json_fd:
        ops_json = json.load(json_fd)
    return [OperationAttendance(**entry) for entry in ops_json]
