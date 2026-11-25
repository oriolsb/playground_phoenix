"""Step definitions shared by the REST feature files.

Each step reaches the game through the REST API only, with the fixtures of
tests/conftest.py (`client`, `game`, `clock`, `isolated_files`). A step
asserts what a player or a client observes: the location, the bag, the
answer, the status and the message.
"""

import json

import pytest
from pytest_bdd import given, parsers, then, when


class Play:
    """What a scenario has done so far: the player, and the last response."""

    def __init__(self) -> None:
        self.sid: str | None = None
        self.name: str | None = None
        self.response = None


@pytest.fixture
def play() -> Play:
    return Play()


# --- Given ------------------------------------------------------------------------


@given(parsers.parse('a new player named "{name}"'))
def a_new_player(game, play, name):
    play.sid = game.start(name)
    play.name = name.strip().upper()


@given(parsers.parse("the clock shows minute {minute:d}"))
def the_clock_shows(clock, minute):
    clock.set_minute(minute)


# --- When -------------------------------------------------------------------------


@when(parsers.parse("the player goes {direction}"))
def the_player_goes(client, play, direction):
    play.response = client.put(f"/player/{play.sid}/move/{direction}")


@when(parsers.parse('the player takes the "{item}"'))
def the_player_takes(game, play, item):
    play.response = game.act(play.sid, item, "pick")


@when(parsers.parse('the player drops the "{item}"'))
def the_player_drops(game, play, item):
    play.response = game.act(play.sid, item, "drop")


@when(parsers.parse('the player opens the "{item}"'))
def the_player_opens(game, play, item):
    play.response = game.act(play.sid, item, "open")


@when(parsers.parse('the player closes the "{item}"'))
def the_player_closes(game, play, item):
    play.response = game.act(play.sid, item, "close")


@when(parsers.parse('the player uses the "{item}"'))
def the_player_uses(game, play, item):
    play.response = game.act(play.sid, item, "use")


# --- Then -------------------------------------------------------------------------


@then(parsers.parse('the player is at "{title}"'))
def the_player_is_at(game, play, title):
    if play.response is not None and "title" in play.response.json():
        assert play.response.status_code == 200, play.response.text
        assert play.response.json()["title"] == title
    assert game.look(play.sid)["title"] == title


@then(parsers.parse("the bag shows gold {gold:d} and energy {energy:d}"))
def the_bag_shows(game, play, gold, energy):
    bag = game.bag(play.sid)
    assert (bag["gold"], bag["energy"]) == (gold, energy)


@then(parsers.parse("the bag shows score {score:d}"))
def the_bag_shows_score(game, play, score):
    assert game.bag(play.sid)["score"] == score


@then(parsers.parse('the answer is "{message}"'))
def the_answer_is(play, message):
    assert play.response.status_code == 200, play.response.text
    assert play.response.json() == {"message": message}


@then(parsers.parse('the request is refused with status {status:d} and the message "{message}"'))
def the_request_is_refused(play, status, message):
    assert play.response.status_code == status, play.response.text
    assert play.response.json() == {"code": status, "message": message}


@then(parsers.parse('the exits are "{exits}"'))
def the_exits_are(game, play, exits):
    expected = [direction.strip() for direction in exits.split(",")]
    assert game.look(play.sid)["exits"] == expected


@then("the location is the katacombs exit")
def the_location_is_the_exit(game, play):
    assert game.look(play.sid)["isExit"] is True


@then("the player has won")
def the_player_has_won(client, play):
    players = {player["sid"]: player for player in client.get("/game/player").json()}
    assert players[play.sid]["hasWon"] is True


@then(parsers.parse('the leaderboard shows "{name}" with score {score:d} and {moves:d} moves'))
def the_leaderboard_shows(client, name, score, moves):
    assert {"name": name, "score": score, "moves": moves} in client.get("/leaderboard").json()


@then(parsers.parse('the high-score file holds one line for "{name}" with score {score:d}'))
def the_high_score_file_holds(isolated_files, name, score):
    lines = [json.loads(line) for line in isolated_files.highscores.read_text(encoding="utf-8").splitlines()]
    mine = [line for line in lines if line["name"] == name]
    assert len(mine) == 1
    assert mine[0]["score"] == score
    assert set(mine[0]) == {"name", "score", "at"}
