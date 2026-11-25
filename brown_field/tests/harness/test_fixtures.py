"""Each fixture of conftest.py reaches the game, and the golden files load.

These tests prove that the test harness controls what it claims to control.
Each one also pins a behavior of today's code, with the rule it reaches.
"""

import json

import pytest


# The win route that needs no market and no cellar.
WIN_ROUTE = ["south", "east", "down", "east", "north", "east"]


def test_the_files_stay_in_tmp_path(game, client, isolated_files):
    """SAVE-1: the save goes to KATACOMBS_DB, here inside tmp_path."""
    sid = game.start()
    response = client.post(f"/player/{sid}/save")
    assert response.json() == {"message": "GAME SAVED.", "path": str(isolated_files.db)}
    assert isolated_files.db.exists()


@pytest.mark.parametrize(
    "minute, status, body",
    [
        (49, 200, None),
        (50, 405, {"code": 405, "message": "THE MARKET IS CLOSED FOR CLEANING. COME BACK LATER."}),
        (59, 405, {"code": 405, "message": "THE MARKET IS CLOSED FOR CLEANING. COME BACK LATER."}),
        (0, 200, None),
    ],
)
def test_the_clock_opens_and_closes_the_market(game, client, clock, minute, status, body):
    """MOVE-6: the clock fixture sets the server's local minute."""
    sid = game.start()
    clock.set_minute(minute)
    response = client.put(f"/player/{sid}/move/east")
    assert response.status_code == status
    if body is None:
        assert response.json()["title"] == "SPITALFIELDS MARKET"
    else:
        assert response.json() == body


def test_a_forced_rat_steals_an_item_without_value(game, rat):
    """MOVE-8: with the rat forced, entering the cellar loses the BEER."""
    sid = game.start()
    game.go(sid, "north")
    assert game.act(sid, "BEER", "pick").status_code == 200
    rat.always()
    cellar = game.go(sid, "down")
    assert cellar["description"].endswith("A RAT RUNS OFF WITH YOUR BEER.")
    assert game.bag(sid)["items"] == []


def test_a_stopped_rat_steals_nothing(game, rat):
    """MOVE-8: with the rat stopped, the BEER stays in the bag."""
    sid = game.start()
    game.go(sid, "north")
    game.act(sid, "BEER", "pick")
    rat.never()
    cellar = game.go(sid, "down")
    assert "RAT" not in cellar["description"]
    assert [item["name"] for item in game.bag(sid)["items"]] == ["BEER"]


def test_a_restart_reads_the_save(game, client, restart):
    """SAVE-2: the restart fixture starts a second server on the same files."""
    sid = game.start()
    game.go(sid, "north")
    game.act(sid, "BEER", "pick")
    client.post(f"/player/{sid}/save")
    again = restart()
    assert again.get(f"/player/{sid}/location").json()["title"] == "OLD TRUMAN BREWERY"
    assert [item["name"] for item in again.get(f"/player/{sid}/bag").json()["items"]] == ["BEER"]


def test_a_player_saved_by_the_legacy_code_comes_back(golden, client):
    """SAVE-2, on the golden katacombs.db."""
    saver = golden["saver"]
    assert client.get(f"/player/{saver['sid']}/location").json()["title"] == saver["location"]
    bag = client.get(f"/player/{saver['sid']}/bag").json()
    assert [item["name"] for item in bag["items"]] == saver["bag_item_names"]
    assert (bag["gold"], bag["energy"]) == (saver["gold"], saver["energy"])


def test_an_account_stored_by_the_legacy_code_logs_in(golden, client):
    """ACCOUNT-4, ACCOUNT-6: the stored password hash and snapshot still work."""
    account = golden["account"]
    response = client.post(
        "/accounts/login", json={"email": account["email"], "password": account["password"]}
    )
    assert response.status_code == 200
    player = response.json()
    assert player["sid"] == account["player_sid"]
    assert player["name"] == account["stored_name"]
    assert player["location"]["title"] == account["snapshot_location"]
    assert (player["bag"]["gold"], player["energy"]) == (
        account["snapshot_gold"],
        account["snapshot_energy"],
    )


def test_a_wrong_password_for_a_legacy_account_is_refused(golden, client):
    """ACCOUNT-5, on the golden account."""
    response = client.post(
        "/accounts/login", json={"email": golden["account"]["email"], "password": "wrong"}
    )
    assert response.status_code == 405
    assert response.json() == {"code": 405, "message": "WRONG EMAIL OR PASSWORD."}


def test_a_win_appends_to_the_legacy_high_score_file(golden, game, isolated_files):
    """WIN-3: the earlier lines stay, and one line is added."""
    before = isolated_files.highscores.read_text(encoding="utf-8").splitlines()
    assert len(before) == golden["highscores"]["lines"]
    game.go(game.start("NEW WINNER"), *WIN_ROUTE)
    after = isolated_files.highscores.read_text(encoding="utf-8").splitlines()
    assert after[: len(before)] == before
    assert len(after) == len(before) + 1
    assert json.loads(after[-1])["name"] == "NEW WINNER"
