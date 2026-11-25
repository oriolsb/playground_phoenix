"""Sessions of requests whose answers the legacy code recorded (the golden transcripts).

Two kinds of session, both through the REST API only:

- a random session: 300 requests chosen by a seeded chooser (moves, looks,
  item actions, the legacy pickup, chat, saves, the leaderboard, unknown sids);
- a scripted session: accounts, quits and logins, restarts, saves, the key
  and the manhole, a win, and the files the server writes.

Each answer becomes one line: the request, the status and the body. Player
sids are replaced by P0, P1, ... in the order they appear, and the folder of
the files by TMP, so a line does not depend on the random source or the
machine. The caller fixes the clock (UTC, one second per request), sets
TZ=UTC, stops the rat, and points the two file variables at an empty folder.

`make_transcripts.py` writes the golden files with the legacy code;
`fitness/test_transcripts.py` replays them against the code under test.
"""

import contextlib
import datetime
import json
import os
import random
import re
import sqlite3
import tempfile
import time
from collections.abc import Callable, Iterator
from pathlib import Path

import time_machine
from fastapi.testclient import TestClient

SEEDS = [1, 2, 3, 4, 5, 6]
STEPS = 300
SID = re.compile(r"\d{6}-\d{12}-\d{8}")
DIRECTIONS = ["north", "south", "east", "west", "up", "down"]
ACTIONS = ["open", "close", "pick", "drop", "use"]
UNKNOWN_ITEM = "000100-000000000000-00000099"
UNKNOWN_PLAYER = "000000-000000000000-00000000"
BEER, BEER_2, KEY, CRATE, MANHOLE = (f"000100-000000000000-0000000{n}" for n in (1, 7, 2, 4, 5))


class Recorder:
    """Sends requests, normalizes each answer, and advances the clock after each one."""

    def __init__(self, new_client: Callable[[], TestClient], tick: Callable[[], None]) -> None:
        self.new_client, self.tick = new_client, tick
        self.client = new_client()
        self.aliases: dict[str, str] = {}
        self.folder = str(Path(os.environ["KATACOMBS_DB"]).parent)

    def norm(self, text: str) -> str:
        text = text.replace(self.folder, "TMP")

        def alias(match: re.Match) -> str:
            sid = match.group(0)
            if sid.startswith("000100-") or sid == UNKNOWN_PLAYER:
                return sid
            return self.aliases.setdefault(sid, f"P{len(self.aliases)}")

        return SID.sub(alias, text)

    def send(self, label: str, method: str, path: str, body=None) -> tuple[dict, object]:
        response = self.client.request(method, path, json=body)
        self.tick()
        try:
            parsed = response.json()
            text = json.dumps(parsed, sort_keys=True, ensure_ascii=False)  # the key order is not the contract
        except ValueError:
            parsed, text = None, response.text
        line = {"label": label, "request": self.norm(f"{method} {path}"), "status": response.status_code, "body": self.norm(text)}
        return line, parsed

    def restart(self) -> dict:
        self.client = self.new_client()
        return {"label": "the server restarts"}

    def files(self, label: str) -> Iterator[dict]:
        scores = Path(os.environ["KATACOMBS_HIGHSCORES"])
        yield {"label": f"{label}: the high-score file", "body": self.norm(scores.read_text()) if scores.exists() else None}
        db = Path(os.environ["KATACOMBS_DB"])
        if not db.exists():
            yield {"label": f"{label}: the database file", "body": None}
            return
        with sqlite3.connect(db) as connection:
            tables = [name for (name,) in connection.execute("SELECT name FROM sqlite_master WHERE type = 'table' ORDER BY name")]
            for table in tables:
                rows = sorted(self.norm(json.dumps(row)) for row in connection.execute(f"SELECT * FROM {table}"))
                # An empty table and a missing one hold the same rows: none. When a
                # table is created is not the contract (STORE-1, STORE-2 name a
                # table once it holds a row), so only a table with rows is recorded.
                if rows:
                    yield {"label": f"{label}: the table {table}", "body": rows}


def random_session(recorder: Recorder, seed: int) -> Iterator[dict]:
    choose = random.Random(seed)
    players: list[str] = []
    for step in range(STEPS):
        if choose.random() < 0.08 or not players:
            name = choose.choice(["ANA", "BO", "CY", "", "ADMIN", "X" * 51])
            line, body = recorder.send(f"{step} start", "POST", "/game/player", {"name": name})
            if line["status"] == 201:
                players.append(body["sid"])
            yield line
            continue
        player = choose.choice(players + [UNKNOWN_PLAYER])
        kind = choose.choice(["move"] * 6 + ["act"] * 4 + ["look", "lookdir", "bag", "chat", "chatread", "save", "board", "list", "pickup", "item", "quit"])
        if kind == "move":
            line, _ = recorder.send(f"{step} move", "PUT", f"/player/{player}/move/{choose.choice(DIRECTIONS)}")
        elif kind == "look":
            line, _ = recorder.send(f"{step} look", "GET", f"/player/{player}/location")
        elif kind == "lookdir":
            line, _ = recorder.send(f"{step} look", "GET", f"/player/{player}/look/{choose.choice(DIRECTIONS)}")
        elif kind == "bag":
            line, _ = recorder.send(f"{step} bag", "GET", f"/player/{player}/bag")
        elif kind in ("act", "pickup"):
            near = []
            if player in players:
                here = recorder.client.get(f"/player/{player}/location").json()["items"]
                bag = recorder.client.get(f"/player/{player}/bag").json()["items"]
                near = [item["sid"] for item in here + bag]
            everything = [f"000100-000000000000-{n:08d}" for n in range(1, 17)] + [UNKNOWN_ITEM]
            item = choose.choice(near) if near and choose.random() < 0.85 else choose.choice(everything)
            if kind == "act":
                line, _ = recorder.send(f"{step} act", "PUT", f"/player/{player}/item/{item}/use/{choose.choice(ACTIONS)}")
            else:
                line, _ = recorder.send(f"{step} legacy pickup", "PUT", f"/player/{player}/pickup/{item}")
        elif kind == "chat":
            line, _ = recorder.send(f"{step} chat", "POST", f"/player/{player}/chat", {"text": choose.choice(["hi", "", "  yo  ", "x" * 300])})
        elif kind == "chatread":
            line, _ = recorder.send(f"{step} chat read", "GET", f"/player/{player}/chat")
        elif kind == "save":
            line, _ = recorder.send(f"{step} save", "POST", f"/player/{player}/save")
        elif kind == "board":
            line, _ = recorder.send(f"{step} leaderboard", "GET", "/leaderboard")
        elif kind == "list":
            line, _ = recorder.send(f"{step} list", "GET", "/game/player")
        elif kind == "item":
            line, _ = recorder.send(f"{step} item", "GET", f"/items/{choose.choice([BEER, KEY, UNKNOWN_ITEM])}")
        else:
            line, _ = recorder.send(f"{step} quit", "DELETE", f"/game/player/{player}")
            if line["status"] == 200:
                players.remove(player)
        yield line
    yield from recorder.files("at the end")


def scripted_session(recorder: Recorder) -> Iterator[dict]:
    send = recorder.send

    def say(label, method, path, body=None):
        line, parsed = send(label, method, path, body)
        lines.append(line)
        return parsed

    lines: list[dict] = []
    ana = {"email": "ana@x.io", "password": "pw"}
    say("register", "POST", "/accounts", {**ana, "name": "Ana"})
    say("register the same email", "POST", "/accounts", {**ana, "name": "Ana"})
    say("register an email with no @", "POST", "/accounts", {"email": "ana", "password": "pw", "name": "Ana"})
    say("register an empty name", "POST", "/accounts", {"email": "b@x.io", "password": "pw", "name": ""})
    say("log in with a wrong password", "POST", "/accounts/login", {"email": "ana@x.io", "password": "no"})
    p = say("log in", "POST", "/accounts/login", ana)["sid"]
    say("log in again", "POST", "/accounts/login", ana)
    say("go north", "PUT", f"/player/{p}/move/north")
    say("take the beer", "PUT", f"/player/{p}/item/{BEER}/use/pick")
    say("save", "POST", f"/player/{p}/save")
    say("quit", "DELETE", f"/game/player/{p}")
    say("quit again", "DELETE", f"/game/player/{p}")
    say("log in after the quit", "POST", "/accounts/login", ana)
    say("the bag", "GET", f"/player/{p}/bag")
    yield from lines
    lines.clear()
    yield from recorder.files("after the quit")
    yield recorder.restart()
    q = say("log in after the restart", "POST", "/accounts/login", ana)
    if isinstance(q, dict) and "sid" in q:
        say("the bag", "GET", f"/player/{q['sid']}/bag")
        say("look around", "GET", f"/player/{q['sid']}/location")
    bo = {"email": "bo@x.io", "password": "pw"}
    say("register bo", "POST", "/accounts", {**bo, "name": "Bo"})
    b = say("log in bo", "POST", "/accounts/login", bo)["sid"]
    say("bo goes north", "PUT", f"/player/{b}/move/north")
    yield from lines
    lines.clear()
    yield recorder.restart()
    say("log in bo after a restart with no save", "POST", "/accounts/login", bo)
    say("list the players", "GET", "/game/player")
    w = say("start cy", "POST", "/game/player", {"name": "Cy"})["sid"]
    for label, method, path in [
        ("go east", "PUT", f"/player/{w}/move/east"),
        ("open the crate", "PUT", f"/player/{w}/item/{CRATE}/use/open"),
        ("open the crate again", "PUT", f"/player/{w}/item/{CRATE}/use/open"),
        ("close the crate", "PUT", f"/player/{w}/item/{CRATE}/use/close"),
        ("open the crate a third time", "PUT", f"/player/{w}/item/{CRATE}/use/open"),
        ("go south", "PUT", f"/player/{w}/move/south"),
        ("open the locked manhole", "PUT", f"/player/{w}/item/{MANHOLE}/use/open"),
        ("use a key not carried", "PUT", f"/player/{w}/item/{KEY}/use/use"),
        ("go north", "PUT", f"/player/{w}/move/north"),
        ("go west", "PUT", f"/player/{w}/move/west"),
        ("go north", "PUT", f"/player/{w}/move/north"),
        ("go up", "PUT", f"/player/{w}/move/up"),
        ("take the key", "PUT", f"/player/{w}/item/{KEY}/use/pick"),
        ("go down", "PUT", f"/player/{w}/move/down"),
        ("go south", "PUT", f"/player/{w}/move/south"),
        ("go east", "PUT", f"/player/{w}/move/east"),
        ("go south", "PUT", f"/player/{w}/move/south"),
        ("use the key", "PUT", f"/player/{w}/item/{KEY}/use/use"),
        ("use the key again", "PUT", f"/player/{w}/item/{KEY}/use/use"),
        ("open the manhole", "PUT", f"/player/{w}/item/{MANHOLE}/use/open"),
        ("look around", "GET", f"/player/{w}/location"),
        ("the bag", "GET", f"/player/{w}/bag"),
        ("go down", "PUT", f"/player/{w}/move/down"),
        ("go east to the exit", "PUT", f"/player/{w}/move/east"),
        ("move after the win", "PUT", f"/player/{w}/move/west"),
        ("drop after the win", "PUT", f"/player/{w}/item/{KEY}/use/drop"),
        ("the leaderboard", "GET", "/leaderboard", ),
        ("save the winner", "POST", f"/player/{w}/save"),
    ]:
        say(label, method, path)
    d = say("start dee", "POST", "/game/player", {"name": "Dee"})["sid"]
    say("dee goes north", "PUT", f"/player/{d}/move/north")
    say("dee takes the second beer", "PUT", f"/player/{d}/item/{BEER_2}/use/pick")
    say("dee drinks it", "PUT", f"/player/{d}/item/{BEER_2}/use/use")
    say("dee's bag", "GET", f"/player/{d}/bag")
    for i in range(14):
        say(f"dee walks {i}", "PUT", f"/player/{d}/move/{['down', 'up'][i % 2]}")
    say("dee's chat", "POST", f"/player/{d}/chat", {"text": "hello"})
    say("the chat", "GET", f"/player/{d}/chat")
    say("the legacy pickup of an item elsewhere", "PUT", f"/player/{d}/pickup/{KEY}")
    yield from lines
    lines.clear()
    yield from recorder.files("before the last restart")
    yield recorder.restart()
    say("list the players after the restart", "GET", "/game/player")
    say("the leaderboard after the restart", "GET", "/leaderboard")
    yield from lines


@contextlib.contextmanager
def recording(new_app: Callable) -> Iterator[Recorder]:
    """The fixed world of a recording: empty files, TZ=UTC, a clock at 10:10:00 UTC
    that moves one second per request, and a rat that never runs."""
    saved_env = {key: os.environ.get(key) for key in ("KATACOMBS_DB", "KATACOMBS_HIGHSCORES", "TZ")}
    saved_random = random.random
    with tempfile.TemporaryDirectory(prefix="katacombs-transcript-") as folder:
        os.environ["KATACOMBS_DB"] = str(Path(folder) / "katacombs.db")
        os.environ["KATACOMBS_HIGHSCORES"] = str(Path(folder) / "highscores.jsonl")
        os.environ["TZ"] = "UTC"
        time.tzset()
        random.random = lambda: 0.99  # the rat never runs (MOVE-8); the sids still come from randint
        start = datetime.datetime(2026, 1, 5, 10, 10, tzinfo=datetime.timezone.utc)
        try:
            with time_machine.travel(start, tick=False) as traveller:
                yield Recorder(lambda: TestClient(new_app()), lambda: traveller.shift(datetime.timedelta(seconds=1)))
        finally:
            random.random = saved_random
            for key, value in saved_env.items():
                if value is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = value
            time.tzset()


def sessions() -> dict[str, Callable[[Recorder], Iterator[dict]]]:
    """Each golden transcript by its file name."""
    found = {f"random-{seed}.jsonl": (lambda recorder, seed=seed: random_session(recorder, seed)) for seed in SEEDS}
    found["scripted.jsonl"] = scripted_session
    return found
