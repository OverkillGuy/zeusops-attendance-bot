"""Convert the models into sqlite tables"""


from random import randint

import sqlite_utils

from zeusops_attendance_bot.mission_recording.models import (
    ConnectionEvent,
    HitInfo,
    HitKilledEvent,
    Mission,
)


def create_tables(db):
    """Create the DB tables for attendance"""
    db["operations"].create(
        {
            "name": str,
            "id": int,
            "date": str,
            "map_name": str,
            "mission_author": str,
            "frame_count": int,
        },
        pk="id",
    )
    opinfo_fields = {"mission_id": int}
    opinfo_fk = ("mission_id", "operations", "id")
    base_entity_fields = {
        "entity_id": int,
        "group": str,
        "name": str,
        "is_player": int,
        "side": str,
        **opinfo_fields,
    }
    db["entities"].create(
        base_entity_fields, pk=("mission_id", "entity_id"), foreign_keys=[opinfo_fk]
    )
    # db["unit_position"].create({"entity_id": int,"name": str, "is_player": int, "alive": int})
    db["connection_events"].create(
        {
            "frame": int,
            "event_id": int,
            "is_connection": int,
            "player": str,
            **opinfo_fields,
        },
        pk=("mission_id", "event_id"),
        foreign_keys=[opinfo_fk],
    )
    db["hits"].create(
        {
            "frame": int,
            "event_id": int,
            "hit_entity": int,
            "hitter_entity": int,
            "weapon": str,
            **opinfo_fields,
        },
        foreign_keys=[
            opinfo_fk,
            ("hit_entity", "entities", "entity_id"),
            ("hitter_entity", "entities", "entity_id"),
        ],
        pk=("mission_id", "event_id"),
    )
    db["kills"].create(
        {
            "frame": int,
            "event_id": int,
            "entity": int,
            "killer_entity": int,
            "weapon": str,
            **opinfo_fields,
        },
        foreign_keys=[
            opinfo_fk,
            ("entity", "entities", "entity_id"),
            ("killer_entity", "entities", "entity_id"),
        ],
        pk=("mission_id", "event_id"),
    )


def populate(db_path, missions: list[Mission]):
    """Populate the database of attendance"""
    db = sqlite_utils.Database(db_path)
    create_tables(db)
    for mission in missions:
        save_mission(db, mission)


def save_mission(db, mission: Mission):
    """Save a signle mission into database"""
    # FIXME Find better ID source (Timestamp?)
    mission_id = randint(1, 1000)  # noqa: S311, "generator not suitable for crypto"
    print(f"Saving mission {mission.mission_name} as {mission_id=}")
    db["operations"].insert(
        {
            "name": mission.mission_name,
            "id": mission_id,
            "date": "today",
            "map_name": mission.world_name,
            "mission_author": mission.mission_author,
            "frame_count": mission.end_frame,
        }
    )
    for entity in mission.entities:
        db["entities"].insert(
            {
                "mission_id": mission_id,
                "entity_id": entity.id,
                "group": entity.group,
                "name": entity.name,
                "side": entity.side,
                "is_player": entity.is_player,
            }
        )
    for event_id, event in enumerate(mission.events):
        if isinstance(event, ConnectionEvent):
            db["connection_events"].insert(
                {
                    "mission_id": mission_id,
                    "frame": event.frame_id,
                    "event_id": event_id,
                    "is_connection": event.event_type == "connected",
                    "player": event.player_name,
                }
            )
        if isinstance(event, HitKilledEvent) and event.event_type == "hit":
            db["hits"].insert(
                {
                    "mission_id": mission_id,
                    "frame": event.frame_id,
                    "event_id": event_id,
                    "hit_entity": event.entity_id,
                    "hitter_entity": event.source_info.source_id
                    if isinstance(event.source_info, HitInfo)
                    else event.source_info,
                    "weapon": event.source_info.weapon
                    if isinstance(event.source_info, HitInfo)
                    else event.source_info,
                }
            )
        if isinstance(event, HitKilledEvent) and event.event_type == "killed":
            db["kills"].insert(
                {
                    "mission_id": mission_id,
                    "frame": event.frame_id,
                    "event_id": event_id,
                    "entity": event.entity_id,
                    "killer_entity": event.source_info.source_id
                    if isinstance(event.source_info, HitInfo)
                    else event.source_info,
                    "weapon": event.source_info.weapon
                    if isinstance(event.source_info, HitInfo)
                    else event.source_info,
                }
            )

    # for op in ops:
    #     op_date = op.op_date.isoformat()
    #     db["operations"].insert({"date": op_date, "attendance_count": op.user_count})
    #     for squad_attendance in op.attendance:
    #         for member, role in squad_attendance.members:
    #             db["attendance"].insert(
    #                 {
    #                     "operation_date": op_date,
    #                     "user": member,
    #                     "squad": squad_attendance.squad,
    #                     "role": role,
    #                 }
    #             )


def main():
    """Run entrypoint of the module"""
    print("Loading first mission")
    m0 = Mission.parse_file("data/2022_12_03__19_54_Zeus_221203_TollV2.json")
    print("Loading second mission")
    m1 = Mission.parse_file("data/2022_12_04__19_30_Zeus_221204_Roth.json")
    missions = [m0, m1]
    print("Exporting to DB...")
    populate("mission.db", missions)
    print("Exported")


if __name__ == "__main__":
    main()
