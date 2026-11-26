"""ARCH-6: the game reads its world through the port `WorldSource` (decision 0016).

The rules are WORLD-1 and WORLD-2. `tests/world/` compares the live game with
`world.json`; these tests check the port and the start check.
"""

import ast
import json
from pathlib import Path

import pytest

from brown_field.adapters.files.world_json import WORLD_FILE, JsonWorld
from brown_field.domain import constants
from brown_field.game import InMemoryGame, RegisterPlayerUseCase
from brown_field.kata import Direction

PACKAGE = Path(__file__).resolve().parents[2]


class ChangedWorld:
    """The world of world.json, with one change applied after each load."""

    def __init__(self, change) -> None:
        self.change = change

    def load(self):
        data = JsonWorld().load()
        self.change(data)
        return data


def test_a_world_with_a_missing_way_back_refuses_to_build():
    def break_the_stairs(data):
        del data.places["BREWERY ROOFTOP"].exits[Direction.DOWN]

    with pytest.raises(ValueError, match="OLD TRUMAN BREWERY goes up to BREWERY ROOFTOP, but BREWERY ROOFTOP does not go down back"):
        InMemoryGame(world=ChangedWorld(break_the_stairs))


def test_a_world_file_with_a_repeated_title_refuses_to_load(tmp_path):
    data = json.loads(WORLD_FILE.read_text(encoding="utf-8"))
    data["locations"].append(dict(data["locations"][0]))
    broken = tmp_path / "world.json"
    broken.write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(ValueError, match="unique title"):
        JsonWorld(broken).load()


def test_the_world_source_gives_the_start():
    def start_in_the_bakery(data):
        data.start = "BRICK LANE BAKERY"

    game = InMemoryGame(world=ChangedWorld(start_in_the_bakery))
    assert RegisterPlayerUseCase(game).execute("ANA").location.title == "BRICK LANE BAKERY"


def test_each_game_gets_its_own_copy_of_the_world():
    first, second = InMemoryGame(), InMemoryGame()
    first.places["OLD TRUMAN BREWERY"].items.clear()
    assert second.places["OLD TRUMAN BREWERY"].items


def test_the_code_names_only_the_titles_and_sids_that_rules_name():
    data = json.loads(WORLD_FILE.read_text(encoding="utf-8"))
    world_names = {entry["title"] for entry in data["locations"]} | {entry["sid"] for entry in data["items"]}
    named_by_rules = {
        constants.CELLAR, constants.TUBE_TUNNEL, constants.MARKET,
        constants.BACK_YARD, constants.KATACOMBS, constants.KEY, constants.MANHOLE,
    }
    found = []
    for path in sorted(PACKAGE.rglob("*.py")):
        if {"tests", "web", "spec"} & set(path.relative_to(PACKAGE).parts):
            continue
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            if isinstance(node, ast.Constant) and node.value in world_names - named_by_rules:
                found.append(f"{path.relative_to(PACKAGE.parent)}:{node.lineno}: {node.value}")
    assert found == [], "\n".join(found)
