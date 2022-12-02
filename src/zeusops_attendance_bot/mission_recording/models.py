"""Model the OCAP2 JSON recording format as Pydantic objects

Derived from: https://github.com/OCAP2/OCAP/wiki/JSON-Recording-Format
Format Version: 1.1.0.
"""

from typing import Any, Literal, NamedTuple, Optional, Tuple, Union

from pydantic import BaseModel, Field


def to_camel(string: str) -> str:
    """Convert a string to lowerCamelCase"""
    camelCase = "".join(word.capitalize() for word in string.split("_"))
    lowered_firstletter = camelCase[0].lower()
    return lowered_firstletter + camelCase[1:]


class Entity(BaseModel):
    """A mission entity (player or vehicle)"""

    id: int
    type: Literal["unit", "vehicle"]
    group: Optional[str]
    name: str
    is_player: Optional[int] = Field(alias="isPlayer")
    positions: Any  # TODO: Elaborate these models
    frames_fired: Any = Field(alias="framesFired")
    role: Optional[str]
    side: Optional[str]
    start_frame_num: int = Field(alias="startFrameNum")


class Position3D(NamedTuple):
    """A position in 3D space"""

    x: float
    y: float
    z: float


class Position2D(NamedTuple):
    """A position in 2D space"""

    x: float
    y: float


class MarkerPosition(NamedTuple):
    """A map marker's position at a point in time"""

    frame: int
    position: Union[Position3D, Position2D, list[Position2D]]
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
