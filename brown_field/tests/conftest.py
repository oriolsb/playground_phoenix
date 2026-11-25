"""Shared fixtures for the characterization tests of the game-server.

Every test reaches the game through its boundaries only: the REST API
(`create_app()` and HTTP), the SQLite file, the high-score file, and the
environment variables. No fixture imports from `brown_field.game`, so the
suite survives a rewrite of game.py and api.py.

Real stand-ins, no mocks: SQLite and the JSONL file run for real in
`tmp_path`. Faked inputs: the wall clock (time-machine) and the stdlib
`random` module. The fakes patch the standard library, never a name inside
the game's modules.
"""

import datetime
import json
import random
import re
import shutil
from dataclasses import dataclass
from pathlib import Path

import pytest
import time_machine
import yaml
from fastapi.testclient import TestClient
from jsonschema import Draft202012Validator
from referencing import Registry, Resource
from referencing.jsonschema import DRAFT202012

from brown_field.api import create_app

TESTS = Path(__file__).resolve().parent
SPEC = TESTS.parent / "spec"
GOLDEN = TESTS / "golden"

OPENAPI = yaml.safe_load((SPEC / "openapi.yaml").read_text(encoding="utf-8"))
OPENAPI_URI = "urn:katacombs:openapi"
REGISTRY = Registry().with_resource(
    OPENAPI_URI, Resource.from_contents(OPENAPI, default_specification=DRAFT202012)
)


# --- Markers for the feature tags --------------------------------------------------


def pytest_configure(config):
    """Register the tags of the feature files as pytest markers.

    pytest-bdd turns each tag (`@WIN-1`, `@api`) into a mark. A rule-ID tag is
    registered from the specification, so a tag that names no rule still
    fails under --strict-markers.
    """
    for way_in, meaning in [
        ("acceptance", "a feature of the Evaluation"),
        ("api", "the way in is the REST contract"),
        ("port", "the way in is a published port"),
    ]:
        config.addinivalue_line("markers", f"{way_in}: {meaning}")
    text = (SPEC / "specification.md").read_text(encoding="utf-8")
    for rule_id, title in re.findall(r"^#{3,4} ([A-Z]+-\d+) — (.+)$", text, flags=re.MULTILINE):
        config.addinivalue_line("markers", f"{rule_id}: {title}")


# --- Isolated files ---------------------------------------------------------------


@dataclass
class Files:
    """The files that the server writes, all inside the test's tmp_path."""

    db: Path
    highscores: Path


@pytest.fixture(autouse=True)
def isolated_files(tmp_path, monkeypatch) -> Files:
    """Point KATACOMBS_DB and KATACOMBS_HIGHSCORES at tmp_path, for every test.

    Without this, a test would read and write katacombs.db and
    highscores.jsonl in the working directory (game.py:328, game.py:350).
    """
    files = Files(db=tmp_path / "katacombs.db", highscores=tmp_path / "highscores.jsonl")
    monkeypatch.setenv("KATACOMBS_DB", str(files.db))
    monkeypatch.setenv("KATACOMBS_HIGHSCORES", str(files.highscores))
    return files


# --- The server ---------------------------------------------------------------------


@pytest.fixture
def client() -> TestClient:
    """A server started on the isolated files."""
    return TestClient(create_app())


@pytest.fixture
def restart():
    """Start the server again on the same files, as after a crash or a deploy.

    Call it after the requests that must survive: `client = restart()`.
    """
    return lambda: TestClient(create_app())


# --- A player's view of the game --------------------------------------------------


class Game:
    """Plays through the REST API, and finds items by name, as a player does."""

    def __init__(self, client: TestClient) -> None:
        self.client = client

    def start(self, name: str = "ANA") -> str:
        response = self.client.post("/game/player", json={"name": name})
        assert response.status_code == 201, response.text
        return response.json()["sid"]

    def go(self, sid: str, *directions: str) -> dict:
        """Move through each direction; each move must succeed."""
        body = {}
        for direction in directions:
            response = self.client.put(f"/player/{sid}/move/{direction}")
            assert response.status_code == 200, f"{direction}: {response.text}"
            body = response.json()
        return body

    def look(self, sid: str) -> dict:
        return self.client.get(f"/player/{sid}/location").json()

    def bag(self, sid: str) -> dict:
        return self.client.get(f"/player/{sid}/bag").json()

    def item_sid(self, sid: str, name: str) -> str:
        """The sid of the first item with this name, in the location or in the bag."""
        for item in self.look(sid)["items"] + self.bag(sid)["items"]:
            if item["name"] == name:
                return item["sid"]
        raise AssertionError(f"no {name} at {self.look(sid)['title']} or in the bag")

    def act(self, sid: str, item_name: str, action: str):
        item = self.item_sid(sid, item_name)
        return self.client.put(f"/player/{sid}/item/{item}/use/{action}")


@pytest.fixture
def game(client) -> Game:
    return Game(client)


# --- Faked inputs: the clock and randomness ---------------------------------------


class Clock:
    """Sets the server's local wall clock to a minute of the hour.

    The market rule reads the local time (game.py:316-319). time-machine
    reads a naive datetime as UTC, so the clock attaches the local time zone:
    minute 50 is then local minute 50 in every zone, half-hour zones included.
    """

    def __init__(self) -> None:
        self._traveller = None

    def set_minute(self, minute: int, hour: int = 10) -> datetime.datetime:
        self.stop()
        moment = datetime.datetime(2026, 1, 5, hour, minute).astimezone()
        self._traveller = time_machine.travel(moment, tick=True)
        self._traveller.start()
        return moment

    def stop(self) -> None:
        if self._traveller is not None:
            self._traveller.stop()
            self._traveller = None


@pytest.fixture
def clock():
    """`clock.set_minute(49)` lets a player into the market; 50 closes it."""
    fake = Clock()
    yield fake
    fake.stop()


class Rat:
    """Forces or stops the cellar rat (game.py:646-654), through stdlib random.

    The rat runs when `random.random()` is below 0.2. Patching the stdlib
    function leaves the sids random, because they come from `randint`.
    """

    def __init__(self, monkeypatch) -> None:
        self._monkeypatch = monkeypatch

    def always(self) -> None:
        self._monkeypatch.setattr(random, "random", lambda: 0.0)

    def never(self) -> None:
        self._monkeypatch.setattr(random, "random", lambda: 0.99)


@pytest.fixture
def rat(monkeypatch) -> Rat:
    return Rat(monkeypatch)


# --- Golden fixtures: data written by the legacy code -----------------------------


@pytest.fixture
def golden(isolated_files) -> dict:
    """Copy the legacy katacombs.db and highscores.jsonl into the isolated paths.

    Returns the manifest (golden/golden.json): the sids, the account
    credentials and the state each file holds. Start the server after this
    fixture, so it reads the copied files. The committed files never change.
    """
    shutil.copyfile(GOLDEN / "katacombs.db", isolated_files.db)
    shutil.copyfile(GOLDEN / "highscores.jsonl", isolated_files.highscores)
    return json.loads((GOLDEN / "golden.json").read_text(encoding="utf-8"))


@pytest.fixture
def golden_old_save(isolated_files) -> dict:
    """Copy a database whose save has the payload of before 2023 (game.py:754)."""
    shutil.copyfile(GOLDEN / "old-save-without-energy.db", isolated_files.db)
    return json.loads((GOLDEN / "golden.json").read_text(encoding="utf-8"))["old_save"]


# --- The contract --------------------------------------------------------------------


@pytest.fixture
def validate():
    """`validate(body, "Location")` checks a body against a schema of openapi.yaml."""

    def check(body, schema_name: str) -> None:
        schema = {"$ref": f"{OPENAPI_URI}#/components/schemas/{schema_name}"}
        errors = list(Draft202012Validator(schema, registry=REGISTRY).iter_errors(body))
        assert not errors, "; ".join(error.message for error in errors)

    return check
