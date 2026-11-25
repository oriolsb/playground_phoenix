"""Steps for the world: compare the live game with brown_field/spec/world.json.

The scout reaches each location by the shortest path that the world file
gives, one new player per location (the energy of one player does not reach
every location). Every observation goes through the REST API.
"""

import json
from collections import deque
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator
from pytest_bdd import given, parsers, then, when

SPEC = Path(__file__).resolve().parents[2] / "spec"
OPPOSITE = {"north": "south", "south": "north", "east": "west", "west": "east", "up": "down", "down": "up"}


class World:
    def __init__(self) -> None:
        self.data = json.loads((SPEC / "world.json").read_text(encoding="utf-8"))
        self.locations = {location["title"]: location for location in self.data["locations"]}
        self.items = {item["sid"]: item for item in self.data["items"]}
        self.one_way = {(exit["from"], exit["direction"]) for exit in self.data["oneWayExits"]}
        self.seen: dict[str, dict] = {}
        self.looks: dict[str, dict[str, str]] = {}
        self.gold_added: dict[str, int] = {}
        self.answers: dict[str, object] = {}

    def paths(self) -> dict[str, list[str]]:
        """The shortest path of directions from the start to each location."""
        start = self.data["start"]
        paths, queue = {start: []}, deque([start])
        while queue:
            title = queue.popleft()
            for direction, target in self.locations[title]["exits"].items():
                if target not in paths:
                    paths[target] = paths[title] + [direction]
                    queue.append(target)
        return paths

    def location_of(self, item_sid: str) -> str:
        return next(t for t, location in self.locations.items() if item_sid in location["items"])


@pytest.fixture
def world() -> World:
    return World()


@given("the world file")
def the_world_file(world):
    assert world.data


@then("the world file is valid against its schema")
def valid_against_its_schema(world):
    schema = json.loads((SPEC / "world.schema.json").read_text(encoding="utf-8"))
    errors = list(Draft202012Validator(schema).iter_errors(world.data))
    assert not errors, "; ".join(error.message for error in errors)


@then("each item of the world file starts in exactly one location")
def each_item_in_one_location(world):
    placed = [sid for location in world.data["locations"] for sid in location["items"]]
    assert sorted(placed) == sorted(world.items), "an item is missing, repeated or unknown"
    assert len(world.locations) == len(world.data["locations"]), "a title is repeated"


@then("each exit of the world file leads to a location of the world file")
def each_exit_leads_somewhere(world):
    assert world.data["start"] in world.locations
    for location in world.data["locations"]:
        for target in location["exits"].values():
            assert target in world.locations, f"{location['title']} leads to an unknown {target}"


@when("a scout walks to each location of the world file")
def a_scout_walks(play, world):
    paths = world.paths()
    assert set(paths) == set(world.locations), f"unreachable: {set(world.locations) - set(paths)}"
    for number, (title, path) in enumerate(paths.items()):
        sid = play.game.start(f"SCOUT {number}")
        if path:
            play.game.go(sid, *path[:-1])
            before = play.game.bag(sid)["gold"]
            play.game.go(sid, path[-1])
            world.gold_added[title] = play.game.bag(sid)["gold"] - before
        else:
            world.gold_added[title] = play.game.bag(sid)["gold"]
        world.seen[title] = play.game.look(sid)
        world.looks[title] = {}
        for direction in world.seen[title]["exits"]:
            response = play.client.get(f"/player/{sid}/look/{direction}")
            assert response.status_code == 200, response.text
            world.looks[title][direction] = response.json()["title"]


@then("each location shows the title, description, exits and items of the world file")
def each_location_as_the_file(world):
    for title, expected in world.locations.items():
        seen = world.seen[title]
        assert seen["title"] == title
        assert seen["description"] == expected["description"], title
        assert seen["exits"] == list(expected["exits"]), title
        assert [item["sid"] for item in seen["items"]] == expected["items"], title
        assert seen["isExit"] is expected["isExit"], title
        for item in seen["items"]:
            assert item == {key: world.items[item["sid"]][key] for key in item}, item["sid"]


@then("each look in a direction shows the location that the exit names")
def each_look_as_the_file(world):
    for title, expected in world.locations.items():
        assert world.looks[title] == expected["exits"], title


@then("each first visit adds the gold of the location")
def each_visit_adds_gold(world):
    assert world.gold_added == {title: location["gold"] for title, location in world.locations.items()}


@when("a client asks for each item of the world file")
def asks_for_each_item(play, world):
    for sid in world.items:
        response = play.client.get(f"/items/{sid}")
        assert response.status_code == 200, f"{sid}: {response.text}"
        world.answers[sid] = response.json()


@then("each answer is the item of the world file")
def each_answer_as_the_file(world):
    for sid, item in world.items.items():
        expected = {key: item[key] for key in ("sid", "name", "description", "actions", "value")}
        assert world.answers[sid] == expected, sid


@when("a scout opens each item of the world file that has gold inside or a lock")
def opens_each_special_item(play, world):
    paths = world.paths()
    for number, (sid, item) in enumerate(world.items.items()):
        if "goldInside" not in item and not item.get("locked"):
            continue
        player = play.game.start(f"OPENER {number}")
        play.game.go(player, *paths[world.location_of(sid)])
        response = play.client.put(f"/player/{player}/item/{sid}/use/open")
        world.answers[sid] = (response.status_code, response.json())


@then(parsers.parse('each item with gold inside answered "OPENED. YOU FIND <gold> GOLD."'))
def gold_inside_answers(world):
    for sid, item in world.items.items():
        if "goldInside" in item:
            status, body = world.answers[sid]
            assert status == 200, body
            assert body["message"] == f"OPENED. YOU FIND {item['goldInside']} GOLD.", body


@then(parsers.parse('each locked item answered "THE <name> IS LOCKED."'))
def locked_answers(world):
    for sid, item in world.items.items():
        if item.get("locked"):
            status, body = world.answers[sid]
            assert status == 405, body
            assert body["message"] == f"THE {item['name']} IS LOCKED.", body


@then("from each location, each exit but the one-way exits has a way back in the opposite direction")
def each_exit_has_a_way_back(world):
    for title, looks in world.looks.items():
        for direction, target in looks.items():
            if (title, direction) in world.one_way:
                assert world.looks[target].get(OPPOSITE[direction]) != title, f"{title} {direction} has a way back"
                continue
            assert world.looks[target].get(OPPOSITE[direction]) == title, f"{title} {direction}: no way back"
