"""Write the golden fixtures with the legacy code, through its REST API.

Run it from the package root, only against the original code:

    uv run python brown_field/tests/golden/make_golden.py

The fixtures are test data. They hold what the legacy server writes, so a
rewrite must still read them. Do not run this script against a rewrite:
that would make the fixtures agree with the new code by construction.

The random source is seeded and the clock is fixed, so a second run gives
the same sids and the same times.
"""

import datetime
import json
import os
import random
import shutil
import sqlite3
import sys
import tempfile
from pathlib import Path

import time_machine

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2]))

WORK = Path(tempfile.mkdtemp())
os.environ["KATACOMBS_DB"] = str(WORK / "katacombs.db")
os.environ["KATACOMBS_HIGHSCORES"] = str(WORK / "highscores.jsonl")

from fastapi.testclient import TestClient  # noqa: E402

from brown_field.api import create_app  # noqa: E402

WIN_ROUTE = ["south", "east", "down", "east", "north", "east"]
ACCOUNT = {"email": "golden@example.org", "password": "golden-password", "name": "golden"}


def items_named(client, path: str, name: str) -> str:
    return next(item["sid"] for item in client.get(path).json()["items"] if item["name"] == name)


def main() -> None:
    random.seed(20261125)
    moment = datetime.datetime(2026, 1, 5, 10, 15, tzinfo=datetime.timezone.utc)
    with time_machine.travel(moment, tick=False):
        client = TestClient(create_app())

        # 1. A saved player: one move north, the BEER taken, then a save.
        saver = client.post("/game/player", json={"name": "golden saver"}).json()["sid"]
        client.put(f"/player/{saver}/move/north")
        beer = items_named(client, f"/player/{saver}/location", "BEER")
        client.put(f"/player/{saver}/item/{beer}/use/pick")
        client.post(f"/player/{saver}/save")
        saved = client.get(f"/player/{saver}/bag").json()

        # 2. An account whose player quit at the rooftop: the snapshot.
        client.post("/accounts", json=ACCOUNT)
        player = client.post(
            "/accounts/login", json={"email": ACCOUNT["email"], "password": ACCOUNT["password"]}
        ).json()["sid"]
        client.put(f"/player/{player}/move/north")
        client.put(f"/player/{player}/move/up")
        snapshot_bag = client.get(f"/player/{player}/bag").json()
        client.delete(f"/game/player/{player}")

        # 3. Two wins: two lines in the high-score file.
        winners = []
        for name in ["golden winner", "golden second"]:
            sid = client.post("/game/player", json={"name": name}).json()["sid"]
            for direction in WIN_ROUTE:
                client.put(f"/player/{sid}/move/{direction}")
            winners.append(name.upper())

    for name in ["katacombs.db", "highscores.jsonl"]:
        shutil.copyfile(WORK / name, HERE / name)

    # 4. A save of before 2023: the payload had no energy and no move count
    #    ("2023: the payload also holds the energy and the move count",
    #    game.py:754). The legacy code no longer writes this shape, so the
    #    script derives it from the saved player of step 1.
    old = HERE / "old-save-without-energy.db"
    shutil.copyfile(WORK / "katacombs.db", old)
    with sqlite3.connect(old) as connection:
        connection.execute("DELETE FROM accounts")
        (payload,) = connection.execute(
            "SELECT payload FROM saves WHERE player_sid = ?", (saver,)
        ).fetchone()
        data = json.loads(payload)
        del data["energy"], data["moves"]
        connection.execute(
            "UPDATE saves SET payload = ? WHERE player_sid = ?", (json.dumps(data), saver)
        )

    manifest = {
        "written_by": "brown_field/tests/golden/make_golden.py, legacy code of 2026-11-25",
        "saver": {
            "sid": saver,
            "name": "GOLDEN SAVER",
            "location": "OLD TRUMAN BREWERY",
            "bag_item_names": [item["name"] for item in saved["items"]],
            "gold": saved["gold"],
            "energy": saved["energy"],
        },
        "account": {
            **ACCOUNT,
            "stored_name": "GOLDEN",
            "player_sid": player,
            "snapshot_location": "BREWERY ROOFTOP",
            "snapshot_gold": snapshot_bag["gold"],
            "snapshot_energy": snapshot_bag["energy"],
        },
        "highscores": {"lines": len(winners), "names": winners},
        "old_save": {"sid": saver, "missing_keys": ["energy", "moves"]},
    }
    (HERE / "golden.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    shutil.rmtree(WORK)
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
