"""The types that the game rules use: directions, actions, items (decision 0018).

`kata.py` re-exports them, so their public names stay importable from it.
"""

from dataclasses import dataclass
from enum import Enum


class Direction(Enum):
    NORTH = "north"
    SOUTH = "south"
    EAST = "east"
    WEST = "west"
    UP = "up"
    DOWN = "down"


class Action(Enum):
    OPEN = "open"
    CLOSE = "close"
    PICK = "pick"
    DROP = "drop"
    USE = "use"


@dataclass
class Item:
    sid: str
    name: str
    description: str
    actions: list[Action]
    value: int = 0

