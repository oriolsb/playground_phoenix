"""Fitness: what holds after any sequence of commands, through the REST API.

A Hypothesis state machine starts players, moves them, acts on items, uses
the legacy pickup, chats and quits, in random order. After each command it
checks what must always hold, whatever the sequence:

- each item is in one place at most: no two bags, and no bag and an observed
  location, hold the same item sid (the rat, a drop, a quit and the legacy
  pickup move an item; nothing copies one);
- the score of each bag is its gold plus the value of each item (BAG-2);
- energy stays from 0 to 20 (PLAYER-1, ACT-15, MOVE-2);
- a bag holds at most 8 slots of 3 items with one name (BAG-3), except after
  the legacy pickup, which skips the limit (LEGACY-1);
- at most 20 players are active (PLAYER-5);
- the gold of a player never goes down, and a win is never undone (GOLD-1,
  GOLD-2, WIN-1, MOVE-7);
- each answer matches its schema in openapi.yaml, and each refusal has a
  status of `x-status-by-reason` and a body `{code, message}` (API-2).

Out of the machine, on purpose: restarts, saves and accounts. A restart puts
a saved item back in its location too, and a login can roll a player back
(SAVE-2, ACCOUNT-4, both contested), so items can appear twice by design.
The clock is fixed at minute 10 and the rat never runs.

A failing sequence is shrunk to a short one: pin it as a scenario.
Run longer with `KATACOMBS_EXAMPLES=2000 uv run pytest -m fitness -k invariants`.
"""

import json
import math
import os
from collections import Counter
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from hypothesis import HealthCheck, settings
from hypothesis import strategies as st
from hypothesis.stateful import Bundle, RuleBasedStateMachine, consumes, invariant, rule, run_state_machine_as_test

from brown_field.api import create_app

pytestmark = pytest.mark.fitness

WORLD = json.loads((Path(__file__).resolve().parents[2] / "spec" / "world.json").read_text(encoding="utf-8"))
ITEMS = {item["sid"]: item for item in WORLD["items"]}
UNKNOWN_ITEM = "000100-000000000000-00000099"
UNKNOWN_PLAYER = "000000-000000000000-00000000"
DIRECTIONS = ["north", "south", "east", "west", "up", "down"]
ACTIONS = ["open", "close", "pick", "drop", "use"]
STATUSES = {400, 404, 405}  # x-status-by-reason: INVALID_REQUEST, INVALID_VALUE 400; NOT_FOUND 404; NOT_ALLOWED 405
WHERE = ["here", "here", "bag", "any"]
EXAMPLES = int(os.environ.get("KATACOMBS_EXAMPLES", "50"))


def make_machine(validate, files):
    class Katacombs(RuleBasedStateMachine):
        players = Bundle("players")

        def __init__(self) -> None:
            super().__init__()
            for path in (files.db, files.highscores):
                path.unlink(missing_ok=True)
            self.client = TestClient(create_app())
            self.active: set[str] = set()
            self.used_legacy_pickup: set[str] = set()
            self.gold: dict[str, int] = {}
            self.won: set[str] = set()
            self.counter = 0

        # --- the answer of every command ------------------------------------------

        def check(self, response, schema: str | None = None, ok=(200,)):
            if response.status_code in ok:
                if schema:
                    validate(response.json(), schema)
                return response
            assert response.status_code in STATUSES, f"{response.request.url}: {response.status_code} {response.text}"
            body = response.json()
            validate(body, "Error")
            assert body["code"] == response.status_code, body
            return response

        # --- the commands -----------------------------------------------------------

        @rule(target=players, name=st.sampled_from(["ANA", "BO", "", "ADMIN", "X" * 51, "  cy  "]))
        def start(self, name):
            self.counter += 1
            response = self.check(self.client.post("/game/player", json={"name": name}), "PlayerWithEnergy", ok=(201,))
            if response.status_code != 201:
                return UNKNOWN_PLAYER
            sid = response.json()["sid"]
            self.active.add(sid)
            self.gold[sid] = 0
            return sid

        @rule(player=players, direction=st.sampled_from(DIRECTIONS))
        def move(self, player, direction):
            self.check(self.client.put(f"/player/{player}/move/{direction}"), "Location")

        @rule(player=players, index=st.integers(0, 5))
        def walk(self, player, index):
            """A move through a real exit of the player's location, to explore further."""
            if player not in self.active:
                return
            exits = self.client.get(f"/player/{player}/location").json()["exits"]
            if exits:
                self.check(self.client.put(f"/player/{player}/move/{exits[index % len(exits)]}"), "Location")

        @rule(player=players, direction=st.sampled_from(DIRECTIONS))
        def look(self, player, direction):
            self.check(self.client.get(f"/player/{player}/look/{direction}"), "Location")

        @rule(player=players, where=st.sampled_from(WHERE), index=st.integers(0, 50), action=st.sampled_from(ACTIONS))
        def act(self, player, where, index, action):
            item = self.pick_item(player, where, index)
            self.check(self.client.put(f"/player/{player}/item/{item}/use/{action}"))

        @rule(player=players, where=st.sampled_from(WHERE), index=st.integers(0, 50))
        def legacy_pickup(self, player, where, index):
            item = self.pick_item(player, where, index)
            if self.check(self.client.put(f"/player/{player}/pickup/{item}")).status_code == 200:
                self.used_legacy_pickup.add(player)

        @rule(player=players, text=st.sampled_from(["hi", "", "  yo  ", "x" * 300]))
        def chat(self, player, text):
            self.check(self.client.post(f"/player/{player}/chat", json={"text": text}), ok=(201,))
            self.check(self.client.get(f"/player/{player}/chat"))

        @rule(player=consumes(players))
        def quit(self, player):
            self.check(self.client.delete(f"/game/player/{player}"))
            self.active.discard(player)

        @rule(item=st.sampled_from([*ITEMS, UNKNOWN_ITEM]))
        def inspect(self, item):
            self.check(self.client.get(f"/items/{item}"), "Item")

        def pick_item(self, player, where, index):
            """An item at the player's location, in the bag, or any item of the world."""
            choices = []
            if player in self.active and where == "here":
                choices = [item["sid"] for item in self.client.get(f"/player/{player}/location").json()["items"]]
            elif player in self.active and where == "bag":
                choices = [item["sid"] for item in self.client.get(f"/player/{player}/bag").json()["items"]]
            if choices:
                return choices[index % len(choices)]
            return [*ITEMS, UNKNOWN_ITEM][index % (len(ITEMS) + 1)]

        # --- what always holds ------------------------------------------------------

        @invariant()
        def what_always_holds(self):
            listed = self.client.get("/game/player")
            assert listed.status_code == 200
            players = {p["sid"]: p for p in listed.json()}
            assert set(players) == self.active, "the active players are not the ones that started and did not quit"
            assert len(players) <= 20, "PLAYER-5: more than 20 active players"
            seen = Counter()
            locations = {}
            for sid, player in players.items():
                validate(player, "PlayerWithEnergy")
                bag = self.client.get(f"/player/{sid}/bag").json()
                assert 0 <= player["energy"] <= 20, f"energy {player['energy']}"
                assert bag["score"] == bag["gold"] + sum(item["value"] for item in bag["items"]), "BAG-2"
                assert bag["gold"] >= self.gold[sid], "the gold of a player went down"
                self.gold[sid] = bag["gold"]
                if sid in self.won:
                    assert player["hasWon"], "a win was undone"
                if player["hasWon"]:
                    self.won.add(sid)
                if sid not in self.used_legacy_pickup:
                    names = Counter(item["name"] for item in bag["items"])
                    slots = sum(math.ceil(count / 3) for count in names.values())
                    assert slots <= 8, f"BAG-3: {slots} slots"
                seen.update(item["sid"] for item in bag["items"])
                location = player["location"]
                locations[location["title"]] = [item["sid"] for item in location["items"]]
            for items in locations.values():
                seen.update(items)
            twice = [sid for sid, count in seen.items() if count > 1]
            assert not twice, f"an item is in two places: {[ITEMS[sid]['name'] for sid in twice]}"
            assert set(seen) <= set(ITEMS), "an item that the world does not hold"

    return Katacombs


def test_what_holds_after_any_sequence_of_commands(validate, isolated_files, clock, rat):
    clock.set_minute(10)
    rat.never()
    run_state_machine_as_test(
        make_machine(validate, isolated_files),
        settings=settings(
            max_examples=EXAMPLES,
            stateful_step_count=40,
            deadline=None,
            suppress_health_check=[HealthCheck.too_slow, HealthCheck.function_scoped_fixture],
        ),
    )
