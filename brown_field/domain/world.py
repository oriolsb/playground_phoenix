"""The fixed world: locations, items, and the checks it must pass (WORLD-1, WORLD-2)."""

from dataclasses import dataclass, field

from ..kata import Direction, Item
from .constants import BACK_YARD, KATACOMBS, KEY, MANHOLE, OPPOSITE
from .errors import NotAllowed


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


class World:
    """The world of one game: shared by every player (ACT-8, ACT-11)."""

    def __init__(self, data: WorldData) -> None:
        check_world(list(data.places), data.places, data.one_way)
        self.start = data.start
        self.places = data.places
        self.items = data.items
        self.gold_inside = data.gold_inside
        self.open_items: set[str] = set()
        self.locked: set[str] = set(data.locked)

    def connect(self, a: str, direction: Direction, b: str) -> None:
        self.places[a].exits[direction] = b
        self.places[b].exits[OPPOSITE[direction]] = a

    def disconnect(self, a: str, direction: Direction) -> None:
        b = self.places[a].exits.pop(direction)
        self.places[b].exits.pop(OPPOSITE[direction])

    def open(self, item: Item) -> None:
        """ACT-8, ACT-9, ACT-10, ACT-13."""
        if item.sid in self.open_items:
            raise NotAllowed(f"THE {item.name} IS ALREADY OPEN.")
        if item.sid in self.locked:
            raise NotAllowed(f"THE {item.name} IS LOCKED.")
        self.open_items.add(item.sid)
        if item.sid == MANHOLE:
            self.connect(BACK_YARD, Direction.DOWN, KATACOMBS)

    def close(self, item: Item) -> None:
        """ACT-11, ACT-12, ACT-13."""
        if item.sid not in self.open_items:
            raise NotAllowed(f"THE {item.name} IS ALREADY CLOSED.")
        self.open_items.remove(item.sid)
        if item.sid == MANHOLE:
            self.disconnect(BACK_YARD, Direction.DOWN)

    def use_key(self, item_sid: str, location: str) -> str | None:
        """ACT-14: the key unlocks the manhole, in the back yard only."""
        if item_sid == KEY and location == BACK_YARD:
            if MANHOLE not in self.locked:
                return "THE MANHOLE COVER IS ALREADY UNLOCKED."
            self.locked.remove(MANHOLE)
            return "YOU UNLOCK THE MANHOLE COVER."
        return None
