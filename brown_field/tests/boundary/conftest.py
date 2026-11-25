"""Steps for the boundaries outside the REST API.

They read the database file as another program would (sqlite3, by table
and column), look at the working directory, start the real process, and
call the Python entry points `create_app` and `app`.
"""

import json
import os
import re
import socket
import sqlite3
import subprocess
import sys
import time
from pathlib import Path

import httpx
import pytest
from fastapi.testclient import TestClient
from pytest_bdd import given, parsers, then, when

from brown_field.api import create_app

ROOT = Path(__file__).resolve().parents[3]
UTC_SECOND = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\+00:00$")


def rows(db: Path, query: str, *args) -> list[tuple]:
    with sqlite3.connect(db) as connection:
        return connection.execute(query, args).fetchall()


# --- The database file --------------------------------------------------------------


@then(parsers.parse('the database table "{table}" has the columns "{columns}"'))
def the_table_has_the_columns(isolated_files, table, columns):
    info = rows(isolated_files.db, f"PRAGMA table_info({table})")
    assert [(column[1], column[2]) for column in info] == [
        (name.strip(), "TEXT") for name in columns.split(",")
    ]


@then(parsers.parse('the saves table holds one row for the player, named "{name}"'))
def one_save_row(play, isolated_files, name):
    found = rows(isolated_files.db, "SELECT name FROM saves WHERE player_sid = ?", play.sid())
    assert found == [(name,)]


@then("the saved time of the player is UTC to the second")
def the_saved_time(play, isolated_files):
    [(saved_at,)] = rows(isolated_files.db, "SELECT saved_at FROM saves WHERE player_sid = ?", play.sid())
    assert UTC_SECOND.match(saved_at), saved_at


@then(parsers.parse('the saved location of the player is "{title}"'))
def the_saved_location(play, isolated_files, title):
    [(payload,)] = rows(isolated_files.db, "SELECT payload FROM saves WHERE player_sid = ?", play.sid())
    assert json.loads(payload)["location"] == title


def account_row(db: Path, email: str) -> dict:
    [(player_sid, snapshot)] = rows(db, "SELECT player_sid, snapshot FROM accounts WHERE email = ?", email)
    return {"player_sid": player_sid, "snapshot": snapshot}


@then(parsers.parse('the account row of "{email}" has no player and no snapshot'))
def account_without_player(isolated_files, email):
    assert account_row(isolated_files.db, email) == {"player_sid": None, "snapshot": None}


@then(parsers.parse('the account row of "{email}" names the player and has no snapshot'))
def account_with_player(play, isolated_files, email):
    assert account_row(isolated_files.db, email) == {"player_sid": play.sid(), "snapshot": None}


@then(parsers.parse('the account row of "{email}" has a snapshot at "{title}"'))
def account_with_snapshot(isolated_files, email, title):
    snapshot = account_row(isolated_files.db, email)["snapshot"]
    assert snapshot is not None
    assert json.loads(snapshot)["location"] == title


@then(parsers.parse('the stored password of "{email}" is "{digest}"'))
def the_stored_password(isolated_files, email, digest):
    assert rows(isolated_files.db, "SELECT password_hash FROM accounts WHERE email = ?", email) == [(digest,)]


# --- Configuration and the working directory ----------------------------------------


@pytest.fixture
def work_dir(tmp_path, monkeypatch) -> Path:
    """An empty working directory, so no file of another run can mislead a check."""
    folder = tmp_path / "work"
    folder.mkdir()
    monkeypatch.chdir(folder)
    return folder


@given("the working directory is an empty folder")
def an_empty_working_directory(work_dir):
    return work_dir


@given("the environment variables of the files are not set")
def the_variables_are_not_set(monkeypatch):
    monkeypatch.delenv("KATACOMBS_DB", raising=False)
    monkeypatch.delenv("KATACOMBS_HIGHSCORES", raising=False)


@then(parsers.parse('the answer is the save of the path "{path}"'))
def the_save_of_the_path(play, path):
    assert play.response.status_code == 200, play.response.text
    assert play.response.json() == {"message": "GAME SAVED.", "path": path}


@then(parsers.parse('the working directory holds the file "{name}"'))
def the_working_directory_holds(work_dir, name):
    assert (work_dir / name).is_file()


@then(parsers.parse('the working directory does not hold the file "{name}"'))
def the_working_directory_does_not_hold(work_dir, name):
    assert not (work_dir / name).exists()


# --- The process --------------------------------------------------------------------


@given("port 8000 on 127.0.0.1 is free")
def port_8000_is_free():
    with socket.socket() as probe:
        if probe.connect_ex(("127.0.0.1", 8000)) == 0:
            pytest.skip("port 8000 is in use, for example by a development server")


@pytest.fixture
def server_process(isolated_files, work_dir):
    holder = {}
    yield holder
    process = holder.get("process")
    if process is not None:
        process.terminate()
        process.wait(timeout=10)


@when(parsers.parse('a person runs "{command}"'))
def a_person_runs(server_process, isolated_files, work_dir, command):
    env = {
        **os.environ,
        "PYTHONPATH": str(ROOT),
        "KATACOMBS_DB": str(isolated_files.db),
        "KATACOMBS_HIGHSCORES": str(isolated_files.highscores),
    }
    args = [sys.executable, *command.split()[1:]]
    server_process["process"] = subprocess.Popen(
        args, cwd=work_dir, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )


@then(parsers.parse("GET {url} answers {status:d}"))
def get_answers(server_process, url, status):
    deadline = time.monotonic() + 15
    while True:
        try:
            response = httpx.get(url, timeout=1)
            break
        except httpx.TransportError:
            assert server_process["process"].poll() is None, "the server process exited"
            assert time.monotonic() < deadline, "the server did not answer within 15 s"
            time.sleep(0.1)
    assert response.status_code == status


# --- The entry points ---------------------------------------------------------------


@pytest.fixture
def servers() -> dict:
    return {}


@given("two servers made from one game")
def two_servers_from_one_game(servers):
    # The game type is the parameter of create_app: the one name of game.py
    # that this seam needs.
    from brown_field.game import InMemoryGame

    game = InMemoryGame()
    servers["first"], servers["second"] = TestClient(create_app(game)), TestClient(create_app(game))


@given("two servers made with no game")
def two_servers_with_no_game(servers):
    servers["first"], servers["second"] = TestClient(create_app()), TestClient(create_app())


@when(parsers.parse('a player named "{name}" starts on the first server'))
def a_player_starts_on_the_first(servers, name):
    assert servers["first"].post("/game/player", json={"name": name}).status_code == 201


@then(parsers.parse('the second server lists the player "{name}"'))
def the_second_lists(servers, name):
    assert name in [player["name"] for player in servers["second"].get("/game/player").json()]


@then(parsers.parse('the second server does not list the player "{name}"'))
def the_second_does_not_list(servers, name):
    assert name not in [player["name"] for player in servers["second"].get("/game/player").json()]


@when("a client calls GET /leaderboard on brown_field.api.app")
def call_the_module_app(play):
    from brown_field.api import app

    play.response = TestClient(app).get("/leaderboard")
