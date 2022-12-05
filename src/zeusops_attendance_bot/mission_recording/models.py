"""Model the OCAP2 JSON recording format as Pydantic objects

Derived from: https://github.com/OCAP2/OCAP/wiki/JSON-Recording-Format
Format Version: 1.1.0.
"""

from typing import Annotated, Any, Literal, NamedTuple, Optional, Tuple, Union

from pydantic import BaseModel, Field

EntityID = int
"""An ID unique across the mission, specifying a given Entity"""

FrameNumber = int
"""A frame number in the mission"""

FrameRange = tuple[FrameNumber, FrameNumber]
"""A range of frames, from start to end frame number"""


class Position3D(NamedTuple):
    """A position in 3D space"""

    x: float
    y: float
    z: float


class Position2D(NamedTuple):
    """A position in 2D space"""

    x: float
    y: float


Position = Union[Position2D, Position3D]


class MarkerPosition(NamedTuple):
    """A map marker's position at a point in time"""

    frame: FrameNumber
    position: Union[Position, list[Position2D]]  # TODO Disambiguate on type/id?
    direction: float  # 0-360
    alpha: int  # Purpose unclear: transparency?


class Marker(NamedTuple):
    """A map marker"""

    marker_type: str
    marker_text: str
    start_frame: int
    end_frame: int
    placer: int
    color: str
    side: int
    positions: list[MarkerPosition]
    marker_size: Tuple[int, int]
    marker_shape: str
    marker_brush: str


class UnitEntityPosition(NamedTuple):
    """A unit entity's position, frozen in unspecified time"""

    position: Position3D
    direction: float
    alive: int
    is_in_vehicle: int
    name_this_frame: str
    is_player_or_ai_this_frame: int
    role_specialty: str


class VehicleEntityPosition(NamedTuple):
    """The position-update of a Vehicle entity"""

    position: Position3D
    direction: float
    is_alive: int
    crew: list[EntityID]
    capture_frame_numbers: FrameRange


class GunFireEvent(NamedTuple):
    """A record of a gun being fired, without info about who did it

    Implementation just tells us the position of the guy who did fire
    """

    frame_number: FrameNumber
    position: Position3D


class BaseEntity(BaseModel):
    """The shared base for all entities, unit or vehicle"""

    id: EntityID
    group: Optional[str]
    name: str
    is_player: Optional[int] = Field(alias="isPlayer")
    frames_fired: list[GunFireEvent] = Field(alias="framesFired")
    role: Optional[str]
    side: Optional[str]
    start_frame_num: FrameNumber = Field(alias="startFrameNum")


class UnitEntity(BaseEntity):
    """A unit entity in mission"""

    type: Literal["unit"]
    positions: list[UnitEntityPosition]


class VehicleEntity(BaseEntity):
    """A vehicle entity in mission

    The official format description (see module-wide link) is WRONG here:
    This struct is derived from source code for vehicle updates:
    https://github.com/OCAP2/addon/blob/9bf85531f89f78c906df15c5c7af304b81fcd38c/addons/%40ocap/addons/ocap/functions/fn_startCaptureLoop.sqf#L198

    """

    type: Literal["vehicle"]
    positions: list[VehicleEntityPosition]


Entity = Annotated[Union[UnitEntity, VehicleEntity], Field(discriminator="type")]


class ConnectionEvent(NamedTuple):
    """The record of a player's connection or disconnection"""

    frame_id: int
    event_type: Literal["connected", "disconnected"]
    player_name: str


class MissionEndEvent(NamedTuple):
    """The end of the mission"""

    frame_id: int
    event_type: Literal["endMission"]
    more_info: tuple[str, str]


class HitInfo(NamedTuple):
    """The details of what hit/killed somebody"""

    source_id: int
    """Who did the hitting/killing"""
    weapon: str
    """The weapon that source_id was using"""


NullText = Literal["null"]


class HitKilledEvent(NamedTuple):
    """A record of a player/AI being hit or killed"""

    frame_id: int
    event_type: Literal["hit", "killed"]
    entity_id: int
    source_info: Union[HitInfo, tuple[NullText], tuple[int]]
    distance: int


Event = Union[ConnectionEvent, MissionEndEvent, HitKilledEvent]


class Mission(BaseModel):
    """A mission, as recorded in JSON file"""

    markers: list[Marker] = Field(alias="Markers")
    entities: list[Entity]
    events: list[Event]
    addon_version: str = Field(alias="addonVersion")
    capture_delay: int = Field(alias="captureDelay")
    end_frame: int = Field(alias="endFrame")
    extension_build: str = Field(alias="extensionBuild")
    extension_version: str = Field(alias="extensionVersion")
    mission_author: str = Field(alias="missionAuthor")
    mission_name: str = Field(alias="missionName")
    world_name: str = Field(alias="worldName")
    times: Any  # TODO: Parse timestamp
    # Cannot use the alias_generator as it interferes with the NamedTuples

    class Config:
        """The pydantic config object"""

        allow_population_by_field_name = True  # Still allow underscores
