"""The fixed world: locations, items, and the checks it must pass (WORLD-1, WORLD-2)."""

from dataclasses import dataclass, field

from ..kata import Direction, Item
from .constants import OPPOSITE


@dataclass
class Place:
    title: str
    description: str
    exits: dict[Direction, str]
    items: list[str]
    gold: int = 0
    is_exit: bool = False


@dataclass
class WorldData:
    """One fresh copy of the world, as a `WorldSource` loads it (decision 0016)."""

    start: str
    places: dict[str, Place]
    items: dict[str, Item]
    gold_inside: dict[str, int] = field(default_factory=dict)
    locked: set[str] = field(default_factory=set)
    one_way: set[tuple[str, Direction]] = field(default_factory=set)


def check_world(titles: list[str], places: dict[str, Place], one_way: set[tuple[str, Direction]]) -> None:
    """Refuse a world with a repeated title or a missing way back (WORLD-2)."""
    if len(titles) != len(set(titles)):
        raise ValueError("Each location must have a unique title")
    for place in places.values():
        for direction, target in place.exits.items():
            if (place.title, direction) in one_way:
                continue
            if places[target].exits.get(OPPOSITE[direction]) != place.title:
                raise ValueError(
                    f"{place.title} goes {direction.value} to {target}, "
                    f"but {target} does not go {OPPOSITE[direction].value} back"
                )
