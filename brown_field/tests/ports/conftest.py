"""Steps that reach the game through its use-case ports.

Each step builds a use case as `XUseCase(game)` and calls `execute`, as
README item 8 describes. This is the one folder whose steps import from
game.py: the use-case classes, `InMemoryGame` and the error types are the
names of this way in. A rewrite that renames them breaks these tests and no
other; the map lists them as a port tier that holds only while the seam is
kept (see the decision records).
"""

import re

import pytest
from pytest_bdd import given, parsers, then, when

from brown_field import game as legacy
from brown_field.kata import Action, Direction

VERBS = {"takes": Action.PICK, "drops": Action.DROP, "opens": Action.OPEN, "closes": Action.CLOSE, "uses": Action.USE}


class Ports:
    """The game behind the ports, the players, and the last answer or error."""

    def __init__(self) -> None:
        self.game = legacy.InMemoryGame()
        self.players: dict[str, str] = {}
        self.current: str | None = None
        self.result = None
        self.error: Exception | None = None
        self.last_item: str | None = None

    def sid(self) -> str:
        return self.players[self.current]

    def call(self, use_case, *args):
        self.result, self.error = None, None
        try:
            self.result = use_case(self.game).execute(*args)
        except legacy.KatacombsError as error:
            self.error = error
        return self.result

    def item_here_or_in_bag(self, name: str, prefer: str) -> str:
        here = legacy.LookAroundUseCase(self.game).execute(self.sid()).items
        bag = legacy.InspectBagUseCase(self.game).execute(self.sid()).items
        for item in (bag + here) if prefer == "bag" else (here + bag):
            if item.name == name:
                return item.sid
        raise AssertionError(f"no {name} here or in the bag")


@pytest.fixture
def ports() -> Ports:
    raise RuntimeError("a scenario of ports.feature must start with: Given a game behind the ports")


@given("a game behind the ports", target_fixture="ports")
def a_game_behind_the_ports():
    return Ports()


@when("a new game starts behind the ports")
def a_new_game_starts(ports):
    ports.game = legacy.InMemoryGame()


def directions(text: str) -> list[Direction]:
    repeat = re.fullmatch(r"(\w+) and (\w+) (\d+) times", text)
    if repeat:
        there, back, times = repeat.groups()
        return [Direction(there), Direction(back)] * int(times)
    return [Direction(word) for word in re.split(r",\s*|\s+and\s+", text)]


# --- Players --------------------------------------------------------------------------


@when(parsers.re(r'the port registers a player named "(?P<name>[^"]*)"'))
def the_port_registers(ports, name):
    player = ports.call(legacy.RegisterPlayerUseCase, name)
    if player is not None:
        ports.players[player.name] = player.sid
        ports.current = player.name


@given(parsers.re(r'the port has registered a player named "(?P<name>[^"]*)"'))
def the_port_has_registered(ports, name):
    the_port_registers(ports, name)
    assert ports.error is None, ports.error


@given(parsers.parse("the port has registered {count:d} players"))
def the_port_has_registered_many(ports, count):
    for number in range(count):
        legacy.RegisterPlayerUseCase(ports.game).execute(f"P{number}")


@when("the port lists the players")
def the_port_lists(ports):
    ports.call(legacy.ListPlayersUseCase)


@when("the port quits the player")
def the_port_quits(ports):
    ports.call(legacy.QuitGameUseCase, ports.sid())


# --- Looking and moving ---------------------------------------------------------------


@when("the port looks around")
def the_port_looks_around(ports):
    ports.call(legacy.LookAroundUseCase, ports.sid())


@when(parsers.re(r"the port looks (?P<direction>(?!around)\w+)"))
def the_port_looks(ports, direction):
    ports.call(legacy.LookInDirectionUseCase, ports.sid(), Direction(direction))


@when(parsers.re(r"the port moves the player (?P<route>.+)"))
def the_port_moves(ports, route):
    for direction in directions(route):
        ports.call(legacy.MoveUseCase, ports.sid(), direction)
        if ports.error is not None:
            return


# --- Items ----------------------------------------------------------------------------


@when(parsers.parse('the port inspects the item "{name}" here'))
def the_port_inspects_here(ports, name):
    ports.call(legacy.InspectItemUseCase, ports.item_here_or_in_bag(name, prefer="here"))


@when(parsers.parse('the port inspects the item sid "{sid}"'))
def the_port_inspects_sid(ports, sid):
    ports.call(legacy.InspectItemUseCase, sid)


@when(parsers.re(r'the port (?P<verb>takes|drops|opens|closes|uses) the "(?P<name>[^"]+)"'))
def the_port_acts(ports, verb, name):
    action = VERBS[verb]
    ports.last_item = ports.item_here_or_in_bag(name, prefer="bag" if action in (Action.DROP, Action.USE) else "here")
    ports.call(legacy.UseItemUseCase, ports.sid(), ports.last_item, action)


@when(parsers.re(r"the port (?P<verb>takes|drops) the same item again"))
def the_port_acts_again(ports, verb):
    ports.call(legacy.UseItemUseCase, ports.sid(), ports.last_item, VERBS[verb])


@when("the port saves the game")
def the_port_saves(ports):
    ports.call(legacy.SaveGameUseCase, ports.sid())


# --- Accounts -------------------------------------------------------------------------


@when(parsers.parse('the port registers the account "{email}" with the password "{password}" and the name "{name}"'))
def the_port_registers_the_account(ports, email, password, name):
    ports.call(legacy.RegisterAccountUseCase, email, password, name)
    assert ports.error is None, ports.error


@when(parsers.parse('the port logs in as "{email}" with the password "{password}"'))
def the_port_logs_in(ports, email, password):
    player = ports.call(legacy.LoginUseCase, email, password)
    if player is not None:
        ports.players[player.name] = player.sid
        ports.current = player.name


# --- Then -----------------------------------------------------------------------------


@then(parsers.parse('the port answers a player named "{name}" at "{title}" who has not won'))
def the_port_answers_a_player(ports, name, title):
    assert ports.error is None, ports.error
    assert (ports.result.name, ports.result.location.title, ports.result.has_won) == (name, title, False)


@then(parsers.re(r'the port refuses with (?P<error>\w+) "(?P<message>[^"]*)"'))
def the_port_refuses(ports, error, message):
    assert type(ports.error).__name__ == error, ports.error or ports.result
    assert str(ports.error) == message


@then("the port refuses the unknown player with PlayerNotFound")
def the_port_refuses_the_unknown_player(ports):
    assert isinstance(ports.error, legacy.PlayerNotFound), ports.error or ports.result
    assert str(ports.error) == f"PLAYER {ports.sid()} NOT FOUND."


@then(parsers.parse('the port answers the location "{title}"'))
def the_port_answers_the_location(ports, title):
    assert ports.error is None, ports.error
    assert ports.result.title == title


@then(parsers.re(r'the port answers "(?P<text>[^"]*)"'))
def the_port_answers(ports, text):
    assert ports.error is None, ports.error
    assert ports.result == text


@then(parsers.parse('the port answers the item "{name}" with the value {value:d} and the actions "{actions}"'))
def the_port_answers_the_item(ports, name, value, actions):
    assert ports.error is None, ports.error
    item = ports.result
    assert (item.name, item.value, [a.value for a in item.actions]) == (
        name,
        value,
        [a.strip() for a in actions.split(",")],
    )


@then("the port answers the katacombs exit")
def the_port_answers_the_exit(ports):
    assert ports.error is None, ports.error
    assert ports.result.is_exit is True


@then(parsers.parse('the port lists "{names}"'))
def the_port_lists_names(ports, names):
    assert sorted(player.name for player in ports.result) == sorted(n.strip() for n in names.split(","))


@then("the player through the port has won")
def the_player_has_won(ports):
    players = {p.sid: p for p in legacy.ListPlayersUseCase(ports.game).execute()}
    assert players[ports.sid()].has_won is True


@then(parsers.parse("the bag through the port shows gold {gold:d} and score {score:d}"))
def the_bag_through_the_port(ports, gold, score):
    bag = legacy.InspectBagUseCase(ports.game).execute(ports.sid())
    assert (bag.gold, bag.score) == (gold, score)


@then(parsers.re(r'the bag through the port holds "(?P<items>[^"]*)"'))
def the_bag_through_the_port_holds(ports, items):
    held = sorted(item.name for item in legacy.InspectBagUseCase(ports.game).execute(ports.sid()).items)
    assert held == sorted(n.strip() for n in items.split(",") if n.strip())


@then("the port answers the path of the database file")
def the_port_answers_the_path(ports, isolated_files):
    assert ports.error is None, ports.error
    assert ports.result == str(isolated_files.db)
