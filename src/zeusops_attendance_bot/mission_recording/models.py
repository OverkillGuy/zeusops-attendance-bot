"""Model the OCAP2 JSON recording format as Pydantic objects

Derived from: https://github.com/OCAP2/OCAP/wiki/JSON-Recording-Format
Format Version: 1.1.0.
"""

from typing import Any, Optional

from pydantic import BaseModel, Field


def to_camel(string: str) -> str:
    """Convert a string to lowerCamelCase"""
    camelCase = "".join(word.capitalize() for word in string.split("_"))
    lowered_firstletter = camelCase[0].lower()
    return lowered_firstletter + camelCase[1:]


class Entity(BaseModel):
    """A mission entity (player or vehicle)"""

    id: int
    group: Optional[str]
    name: str
    is_player: Optional[bool]
    positions: Any  # TODO: Elaborate these models
    frames_fired: Any


class Mission(BaseModel):
    """A mission, as recorded in JSON file"""

    markers: list[Any] = Field(alias="Markers")
    entities: list[Entity]
    addon_version: str
    capture_delay: int
    end_frame: int
    extension_build: str  # TODO: Parse as datetime
    extension_version: str
    mission_author: str
    mission_name: str
    world_name: str

    class Config:
        """Pydantic model config"""

        # Fall back to detecting lowerCamelCase fields
        alias_generator = to_camel
