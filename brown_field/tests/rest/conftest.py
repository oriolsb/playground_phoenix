"""Step definitions shared by the REST feature files.

Each step reaches the game through the REST API only, plus the two files a
client of the boundary can see: the SQLite file and the high-score file. A
step asserts what a player or a client observes: the location, the bag, the
answer, the status and the message.

A step about "the player" acts for the last player who started or logged in.
A step about a quoted name ("BO") acts for that player.
"""

import json
import sqlite3

import pytest
from fastapi.testclient import TestClient
from pytest_bdd import given, parsers, then, when

from brown_field.api import create_app
from brown_field.tests.driver import Game

# "the player" or a quoted player name, for example "BO".
WHO = r'(?:the player|"(?P<name>[^"]+)")'
# The route to the win through the tunnels, with no market and no cellar:
# BOXPARK, RAILWAY ARCHES, OLD TUBE TUNNEL, TUNNEL JUNCTION, KATACOMBS, EXIT.
TUNNEL_ROUTE = ["south", "east", "down", "east", "north", "east"]
# The shape of the "pick" action on the wire, for the item steps.
ACTIONS = {"takes": "pick", "drops": "drop", "opens": "open", "closes": "close", "uses": "use"}


class Play:
    """What a scenario has done so far: the players, the server, the last answer."""

    def __init__(self, client: TestClient) -> None:
        self.client = client
        self.game = Game(client)
        self.players: dict[str, str] = {}
        self.current: str | None = None
        self.known_items: dict[str, str] = {}
        self.response = None
        self.previous_sid: str | None = None
        self.last_item: str | None = None

    def sid(self, name: str | None = None) -> str:
        return self.players[name.upper()] if name else self.players[self.current]

    def add(self, name: str, sid: str) -> None:
        self.players[name] = sid
        self.current = name

    def item(self, who: str, item: str, prefer: str) -> str:
        """The sid of an item: here or in the bag (in `prefer` order), else one a scout saw."""
        sid = self.sid(who)
        here = self.game.look(sid)["items"]
        bag = self.game.bag(sid)["items"]
        for item_json in (bag + here) if prefer == "bag" else (here + bag):
            if item_json["name"] == item:
                return item_json["sid"]
        return self.known_items[item]

    def restart(self) -> None:
        self.client = TestClient(create_app())
        self.game = Game(self.client)


@pytest.fixture
def play(client) -> Play:
    return Play(client)


def names(text: str) -> list[str]:
    return [part.strip() for part in text.split(",") if part.strip()]


# --- Given: players, clock, rat, scouts -------------------------------------------


@given(parsers.re(r'a new player named "(?P<name>[^"]*)"'))
def a_new_player(play, name):
    play.add(name.strip().upper(), play.game.start(name))


@given(parsers.parse("{count:d} players are in the game"))
def players_in_the_game(play, count):
    for number in range(1, count + 1):
        play.players[f"P{number}"] = play.game.start(f"P{number}")


@given(parsers.parse("the clock shows minute {minute:d}"))
def the_clock_shows(clock, minute):
    clock.set_minute(minute)


@given("the rat always runs")
def the_rat_always_runs(rat):
    rat.always()


@given("the rat never runs")
def the_rat_never_runs(rat):
    rat.never()


@given(parsers.parse('a scout has seen the "{item}" at the end of the path "{path}"'))
def a_scout_has_seen(play, item, path):
    """A throwaway player walks the path, notes the item's sid, and quits."""
    scout = play.game.start("SCOUT")
    play.game.go(scout, *names(path))
    play.known_items[item] = next(i["sid"] for i in play.game.look(scout)["items"] if i["name"] == item)
    play.client.delete(f"/game/player/{scout}")


@given(parsers.re(WHO + r" has won through the tunnels"))
@when(parsers.re(WHO + r" has won through the tunnels"))
def has_won_through_the_tunnels(play, name):
    play.game.go(play.sid(name), *TUNNEL_ROUTE)


@given(parsers.parse('an account "{email}" with the password "{password}" and the name "{name}"'))
def an_account(play, email, password, name):
    response = play.client.post("/accounts", json={"email": email, "password": password, "name": name})
    assert response.status_code == 201, response.text


@given("the golden database holds a save from before 2023")
def the_golden_old_save(golden_old_save):
    return golden_old_save


# --- When: the player's commands ----------------------------------------------------


@when(parsers.re(WHO + r" goes (?P<direction>\w+)"))
def goes(play, name, direction):
    play.response = play.client.put(f"/player/{play.sid(name)}/move/{direction}")


@when(parsers.re(WHO + r" looks around"))
def looks_around(play, name):
    play.response = play.client.get(f"/player/{play.sid(name)}/location")


@when(parsers.re(WHO + r" looks (?P<direction>(?!around)\w+)"))
def looks(play, name, direction):
    play.response = play.client.get(f"/player/{play.sid(name)}/look/{direction}")


@when(parsers.re(WHO + r' (?P<verb>takes|drops|opens|closes|uses) the "(?P<item>[^"]+)"'))
def acts(play, name, verb, item):
    action = ACTIONS[verb]
    sid = play.item(name, item, prefer="bag" if action in ("drop", "use") else "here")
    play.last_item = sid
    play.response = play.client.put(f"/player/{play.sid(name)}/item/{sid}/use/{action}")


@when(parsers.re(WHO + r" takes the same item again"))
def takes_the_same_item_again(play, name):
    play.response = play.client.put(f"/player/{play.sid(name)}/item/{play.last_item}/use/pick")


@when(parsers.re(WHO + r' picks up the "(?P<item>[^"]+)" with the legacy route'))
def legacy_pickup(play, name, item):
    sid = play.item(name, item, prefer="here")
    play.response = play.client.put(f"/player/{play.sid(name)}/pickup/{sid}")


@when(parsers.re(WHO + r" saves the game"))
def saves(play, name):
    play.response = play.client.post(f"/player/{play.sid(name)}/save")


@when(parsers.re(WHO + r" quits"))
def quits(play, name):
    play.response = play.client.delete(f"/game/player/{play.sid(name)}")


@when(parsers.re(WHO + r' sends the chat message "(?P<text>[^"]*)"'))
def sends_chat(play, name, text):
    play.response = play.client.post(f"/player/{play.sid(name)}/chat", json={"text": text})


@when(parsers.re(WHO + r" reads the chat"))
def reads_chat(play, name):
    play.response = play.client.get(f"/player/{play.sid(name)}/chat")


# --- When: a client, the server -----------------------------------------------------


@when(parsers.re(r'a client starts a game with the name "(?P<name>[^"]*)"'))
def a_client_starts(play, name):
    play.response = play.client.post("/game/player", json={"name": name})
    if play.response.status_code == 201:
        play.add(play.response.json()["name"], play.response.json()["sid"])


@when(parsers.parse("a client starts a game with a name of {length:d} characters"))
def a_client_starts_with_length(play, length):
    play.response = play.client.post("/game/player", json={"name": "A" * length})


@when(parsers.re(r'a client registers "(?P<email>[^"]*)" with the password "(?P<password>[^"]*)" and the name "(?P<name>[^"]*)"'))
def a_client_registers(play, email, password, name):
    play.response = play.client.post("/accounts", json={"email": email, "password": password, "name": name})


@when(parsers.parse('a client logs in as "{email}" with the password "{password}"'))
def a_client_logs_in(play, email, password):
    play.response = play.client.post("/accounts/login", json={"email": email, "password": password})
    if play.response.status_code == 200:
        name = play.response.json()["name"]
        play.previous_sid = play.players.get(name)
        play.add(name, play.response.json()["sid"])


@when(parsers.parse('a client asks for the item "{item}"'))
def a_client_asks_for_the_item(play, item):
    play.response = play.client.get(f"/items/{play.known_items[item]}")


@when("a client lists the players")
def a_client_lists_the_players(play):
    play.response = play.client.get("/game/player")


@when(parsers.parse("a client sends {method} {path} with the body {body}"))
def a_client_sends(play, method, path, body):
    if play.current is not None:
        path = path.replace("{sid}", play.sid())
    kwargs = {} if body == "-" else {"json": json.loads(body)}
    play.response = play.client.request(method, path, **kwargs)


@when("the server restarts")
def the_server_restarts(play):
    play.restart()


@pytest.fixture
def start_outcome() -> dict:
    return {}


@when("the server starts")
def the_server_starts(start_outcome):
    """Start a server on the files as they are. No `play`: it would start one first."""
    try:
        TestClient(create_app())
    except Exception as error:  # the observable result is the failure itself
        start_outcome["error"] = error


@when(parsers.re(r'the saved location of ' + WHO + r' is changed to "(?P<title>[^"]+)" in the database'))
def the_saved_location_is_changed(play, isolated_files, name, title):
    sid = play.sid(name)
    with sqlite3.connect(isolated_files.db) as connection:
        (payload,) = connection.execute("SELECT payload FROM saves WHERE player_sid = ?", (sid,)).fetchone()
        data = {**json.loads(payload), "location": title}
        connection.execute("UPDATE saves SET payload = ? WHERE player_sid = ?", (json.dumps(data), sid))


# --- Then: the answer ---------------------------------------------------------------


@then(parsers.parse('the answer is "{message}"'))
def the_answer_is(play, message):
    assert play.response.status_code == 200, play.response.text
    assert play.response.json() == {"message": message}


@then(parsers.parse('the request is refused with status {status:d} and the message "{message}"'))
def the_request_is_refused(play, status, message):
    assert play.response.status_code == status, play.response.text
    assert play.response.json() == {"code": status, "message": message}


@then(parsers.re(r"the request is refused because " + WHO + r" is unknown"))
def refused_unknown_player(play, name):
    sid = play.sid(name)
    assert play.response.status_code == 404, play.response.text
    assert play.response.json() == {"code": 404, "message": f"PLAYER {sid} NOT FOUND."}


@then(parsers.parse("the response is {status:d} with the body {body}"))
def the_response_is(play, status, body):
    assert play.response.status_code == status, play.response.text
    assert play.response.json() == json.loads(body)


@then(parsers.parse('the new player is named "{name}" at "{title}" with energy {energy:d}'))
def the_new_player_is(play, name, title, energy):
    assert play.response.status_code in (200, 201), play.response.text
    player = play.response.json()
    assert (player["name"], player["location"]["title"], player["energy"]) == (name, title, energy)
    assert player["hasWon"] is False


@then(parsers.parse('the account answer is "{email}" named "{name}"'))
def the_account_answer(play, email, name):
    assert play.response.status_code == 201, play.response.text
    assert play.response.json() == {"email": email, "name": name}


@then(parsers.re(r"the answer names the same player as before"))
def the_same_player(play):
    assert play.previous_sid is not None
    assert play.response.json()["sid"] == play.previous_sid


@then("the save answer names the database file")
def the_save_answer(play, isolated_files):
    assert play.response.status_code == 200, play.response.text
    assert play.response.json() == {"message": "GAME SAVED.", "path": str(isolated_files.db)}


@then(parsers.parse('the server does not start, for want of "{key}"'))
def the_server_does_not_start(start_outcome, key):
    error = start_outcome.get("error")
    assert isinstance(error, KeyError), error
    assert error.args == (key,)


# --- Then: the location -------------------------------------------------------------


@then(parsers.re(WHO + r' is at "(?P<title>[^"]+)"'))
def is_at(play, name, title):
    """Where the game says the player is now (a look around, not the last answer)."""
    assert play.game.look(play.sid(name))["title"] == title


@then(parsers.parse("the response status is {status:d}"))
def the_response_status_is(play, status):
    assert play.response.status_code == status, play.response.text


@then(parsers.parse('the answer shows the location "{title}"'))
def the_answer_shows_the_location(play, title):
    assert play.response.status_code == 200, play.response.text
    assert play.response.json()["title"] == title


@then(parsers.parse('the exits are "{exits}"'))
def the_exits_are(play, exits):
    """The exits as a set: no rule fixes their order."""
    assert sorted(play.game.look(play.sid())["exits"]) == sorted(names(exits))


@then(parsers.re(r'the location holds (?P<count>\d+) "(?P<item>[^"]+)"'))
def the_location_holds(play, count, item):
    here = [i["name"] for i in play.game.look(play.sid())["items"]]
    assert here.count(item) == int(count), here


@then(parsers.parse('the description ends with "{text}"'))
def the_description_ends_with(play, text):
    assert play.response.json()["description"].endswith(text)


@then(parsers.parse('the description does not mention "{text}"'))
def the_description_does_not_mention(play, text):
    assert text not in play.response.json()["description"]


@then("the location is the katacombs exit")
def the_location_is_the_exit(play):
    assert play.game.look(play.sid())["isExit"] is True


# --- Then: the bag ------------------------------------------------------------------


@then(parsers.re(r"(?:the bag|the bag of " + WHO + r") shows gold (?P<gold>\d+) and energy (?P<energy>\d+)"))
def the_bag_shows(play, gold, energy, name=None):
    bag = play.game.bag(play.sid(name))
    assert (bag["gold"], bag["energy"]) == (int(gold), int(energy))


@then(parsers.parse("the bag shows score {score:d}"))
def the_bag_shows_score(play, score):
    assert play.game.bag(play.sid())["score"] == score


@then(parsers.re(r'(?:the bag|the bag of ' + WHO + r') holds "(?P<items>[^"]*)"'))
def the_bag_holds(play, items, name=None):
    """The item names in the bag, as a multiset: no rule fixes their order."""
    held = [i["name"] for i in play.game.bag(play.sid(name))["items"]]
    assert sorted(held) == sorted(names(items)), held


@then("the bag is empty")
def the_bag_is_empty(play):
    assert play.game.bag(play.sid())["items"] == []


# --- Then: items, players, leaderboard, chat, files ---------------------------------


@then(parsers.parse('the item is "{item}" with the value {value:d} and the actions "{actions}"'))
def the_item_is(play, item, value, actions):
    assert play.response.status_code == 200, play.response.text
    body = play.response.json()
    assert (body["name"], body["value"], body["actions"]) == (item, value, names(actions))


@then(parsers.parse('the item description is "{description}"'))
def the_item_description(play, description):
    assert play.response.json()["description"] == description


@then(parsers.parse('the list holds "{players}", each with energy {energy:d}'))
def the_list_holds(play, players, energy):
    assert play.response.status_code == 200, play.response.text
    listed = {p["name"]: p["energy"] for p in play.response.json()}
    assert listed == {player: energy for player in names(players)}


@then("the player has won")
def the_player_has_won(play):
    players = {p["sid"]: p for p in play.client.get("/game/player").json()}
    assert players[play.sid()]["hasWon"] is True


@then(parsers.parse('the leaderboard shows "{name}" with score {score:d} and {moves:d} moves'))
def the_leaderboard_shows(play, name, score, moves):
    assert {"name": name, "score": score, "moves": moves} in play.client.get("/leaderboard").json()


@then(parsers.parse('the leaderboard lists "{players}" in this order'))
def the_leaderboard_lists(play, players):
    assert [entry["name"] for entry in play.client.get("/leaderboard").json()] == names(players)


@then("the leaderboard is empty")
def the_leaderboard_is_empty(play):
    assert play.client.get("/leaderboard").json() == []


@then(parsers.parse('the chat shows "{lines}"'))
def the_chat_shows(play, lines):
    """Lines as `NAME: text`, separated by `;`, oldest first."""
    assert play.response.status_code == 200, play.response.text
    shown = [f"{line['name']}: {line['text']}".strip() for line in play.response.json()]
    assert shown == [line.strip() for line in lines.split(";")]


@then("the chat is empty")
def the_chat_is_empty(play):
    assert play.response.status_code == 200, play.response.text
    assert play.response.json() == []


@then(parsers.parse('the high-score file holds one line for "{name}" with score {score:d}'))
def the_high_score_file_holds(isolated_files, name, score):
    lines = [json.loads(line) for line in isolated_files.highscores.read_text(encoding="utf-8").splitlines()]
    mine = [line for line in lines if line["name"] == name]
    assert len(mine) == 1
    assert mine[0]["score"] == score
    assert set(mine[0]) == {"name", "score", "at"}
