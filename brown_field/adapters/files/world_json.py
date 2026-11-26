"""The world of `brown_field/spec/world.json`, the default `WorldSource` (decision 0016).

The Specification names this file as the world (WORLD-1). Each load reads it
again, so each game gets its own copy to change (the manhole, the items).
"""

import json
from pathlib import Path

from ...domain.world import Place, WorldData, check_world
from ...domain.types import Action, Direction, Item

WORLD_FILE = Path(__file__).resolve().parents[2] / "spec" / "world.json"


class JsonWorld:
    def __init__(self, path: Path = WORLD_FILE) -> None:
        self.path = path

    def load(self) -> WorldData:
        data = json.loads(self.path.read_text(encoding="utf-8"))
        items = {
            entry["sid"]: Item(
                entry["sid"],
                entry["name"],
                entry["description"],
                [Action(action) for action in entry["actions"]],
                value=entry["value"],
            )
            for entry in data["items"]
        }
        titles = [entry["title"] for entry in data["locations"]]
        places = {
            entry["title"]: Place(
                entry["title"],
                entry["description"],
                {Direction(way): target for way, target in entry["exits"].items()},
                list(entry["items"]),
                gold=entry["gold"],
                is_exit=entry["isExit"],
            )
            for entry in data["locations"]
        }
        one_way = {(entry["from"], Direction(entry["direction"])) for entry in data["oneWayExits"]}
        check_world(titles, places, one_way)
        return WorldData(
            start=data["start"],
            places=places,
            items=items,
            gold_inside={e["sid"]: e["goldInside"] for e in data["items"] if "goldInside" in e},
            locked={e["sid"] for e in data["items"] if e.get("locked")},
            one_way=one_way,
        )
