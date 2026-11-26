"""The world of a game, built from world.json (WORLD-1, WORLD-2, WORLD-3)."""

import json
from dataclasses import dataclass, field
from pathlib import Path

from ..kata import Action, Direction, Item

WORLD_FILE = Path(__file__).resolve().parents[1] / "spec" / "world.json"

OPPOSITE = {
    Direction.NORTH: Direction.SOUTH,
    Direction.SOUTH: Direction.NORTH,
    Direction.EAST: Direction.WEST,
    Direction.WEST: Direction.EAST,
    Direction.UP: Direction.DOWN,
    Direction.DOWN: Direction.UP,
}


@dataclass
class Place:
    title: str
    description: str
    exits: dict[Direction, str]
    items: list[str]
    gold: int = 0
    is_exit: bool = False


@dataclass
class World:
    start: str
    places: dict[str, Place]
    items: dict[str, Item]
    gold_inside: dict[str, int] = field(default_factory=dict)
    locked: set[str] = field(default_factory=set)
    uses: dict[str, dict] = field(default_factory=dict)
    # item sid -> (from, direction, to): the exit that exists while the item is open (ACT-13)
    opened_exits: dict[str, tuple[str, Direction, str]] = field(default_factory=dict)
    # Product asked for a slide from the cellar into the tunnels (2022). The
    # world rule "each connection has a way back" does not apply to it.
    one_way: set[tuple[str, Direction]] = field(default_factory=set)


def load_world(data: dict | None = None) -> World:
    """A new world from `data` (world.schema.json), else from world.json. Each call builds new objects."""
    if data is None:
        data = json.loads(WORLD_FILE.read_text(encoding="utf-8"))
    titles = [location["title"] for location in data["locations"]]
    if len(titles) != len(set(titles)):
        raise ValueError("Each location must have a unique title")
    world = World(
        start=data["start"],
        places={
            location["title"]: Place(
                title=location["title"],
                description=location["description"],
                exits={Direction(d): target for d, target in location["exits"].items()},
                items=list(location["items"]),
                gold=location["gold"],
                is_exit=location["isExit"],
            )
            for location in data["locations"]
        },
        items={
            item["sid"]: Item(
                item["sid"], item["name"], item["description"], [Action(a) for a in item["actions"]], item["value"]
            )
            for item in data["items"]
        },
        gold_inside={item["sid"]: item["goldInside"] for item in data["items"] if "goldInside" in item},
        locked={item["sid"] for item in data["items"] if item.get("locked")},
        uses={item["sid"]: dict(item["use"]) for item in data["items"] if "use" in item},
        opened_exits={
            exit["item"]: (exit["from"], Direction(exit["direction"]), exit["to"]) for exit in data["openedExits"]
        },
        one_way={(exit["from"], Direction(exit["direction"])) for exit in data["oneWayExits"]},
    )
    check_connections(world)
    return world


def check_connections(world: World) -> None:
    places = world.places
    for place in places.values():
        for direction, target in place.exits.items():
            if (place.title, direction) in world.one_way:
                continue
            if places[target].exits.get(OPPOSITE[direction]) != place.title:
                raise ValueError(
                    f"{place.title} goes {direction.value} to {target}, "
                    f"but {target} does not go {OPPOSITE[direction].value} back"
                )
