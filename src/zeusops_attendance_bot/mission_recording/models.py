"""Model the OCAP2 JSON recording format as Pydantic objects

Derived from: https://github.com/OCAP2/OCAP/wiki/JSON-Recording-Format
Format Version: 1.1.0.
"""

from typing import Any, Literal, NamedTuple, Optional, Tuple, Union

from pydantic import BaseModel, Field


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

    frame: int
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


class EntityPosition(NamedTuple):
    """An entity's position, frozen in unspecified time"""

    position: Position3D
    direction: float
    alive: int
    is_in_vehicle: int
    name_this_frame: str
    is_player_or_ai_this_frame: int
    role_specialty: str


class BaseEntity(BaseModel):
    """The shared base for all entities, unit or vehicle"""

    id: int
    group: Optional[str]
    name: str
    is_player: Optional[int] = Field(alias="isPlayer")
    frames_fired: Any = Field(alias="framesFired")
    role: Optional[str]
    side: Optional[str]
    start_frame_num: int = Field(alias="startFrameNum")


class UnitEntity(BaseEntity):
    """A unit entity in mission"""

    type: Literal["unit"]
    positions: list[EntityPosition]


class VehicleEntity(BaseEntity):
    """A vehicleentity in mission"""

    type: Literal["vehicle"]
    positions: list[Any]  # FIXME: Determine what kind of list it is


Entity = Union[UnitEntity, VehicleEntity]


class Mission(BaseModel):
    """A mission, as recorded in JSON file"""

    markers: list[Marker] = Field(alias="Markers")
    entities: list[Entity]
    addon_version: str = Field(alias="addonVersion")
    capture_delay: int = Field(alias="captureDelay")
    end_frame: int = Field(alias="endFrame")
    extension_build: str = Field(alias="extensionBuild")  # TODO: Parse as datetime
    extension_version: str = Field(alias="extensionVersion")
    mission_author: str = Field(alias="missionAuthor")
    mission_name: str = Field(alias="missionName")
    world_name: str = Field(alias="worldName")
    # Cannot use the alias_generator as it interferes with the NamedTuples

    class Config:
        """The pydantic config object"""

        allow_population_by_field_name = True  # Still allow underscores
