"""ARCH-3: a test gives the game its time and its chance through the ports.

No `time_machine`, no patch of `random`: the fakes are adapters, handed to
`InMemoryGame` (decision 0013). The rules are MOVE-6 and MOVE-8.
"""

from datetime import datetime

import pytest

from brown_field.game import InMemoryGame, MoveUseCase, NotAllowed, RegisterPlayerUseCase, UseItemUseCase
from brown_field.application.views import to_bag
from brown_field.kata import Action, Direction

BEER = "000100-000000000000-00000001"


class FixedClock:
    def __init__(self, minute: int) -> None:
        self.moment = datetime(2026, 1, 5, 10, minute).astimezone()

    def now(self) -> datetime:
        return self.moment


class FixedChance:
    def __init__(self, value: float) -> None:
        self.value = value

    def chance(self) -> float:
        return self.value

    def choice(self, items):
        return items[0]

    def digits(self, count: int) -> str:
        self.value_digits = getattr(self, "value_digits", 0) + 1
        return f"{self.value_digits:0{count}d}"


class Recorder:
    def __init__(self) -> None:
        self.lines: list[tuple[str, int, datetime]] = []

    def append(self, name: str, score: int, at: datetime) -> None:
        self.lines.append((name, score, at))


def start(game: InMemoryGame) -> str:
    return RegisterPlayerUseCase(game).execute("ANA").sid


@pytest.mark.parametrize("minute, refused", [(49, False), (50, True), (55, True), (59, True), (10, False)])
def test_the_clock_port_drives_the_market(minute, refused):
    game = InMemoryGame(clock=FixedClock(minute))
    sid = start(game)
    if refused:
        with pytest.raises(NotAllowed, match="CLOSED FOR CLEANING"):
            MoveUseCase(game).execute(sid, Direction.EAST)
    else:
        assert MoveUseCase(game).execute(sid, Direction.EAST).title == "SPITALFIELDS MARKET"


@pytest.mark.parametrize("chance, stolen", [(0.0, True), (0.19, True), (0.2, False), (0.99, False)])
def test_the_random_port_drives_the_rat(chance, stolen):
    game = InMemoryGame(random_source=FixedChance(chance))
    sid = start(game)
    MoveUseCase(game).execute(sid, Direction.NORTH)
    UseItemUseCase(game).execute(sid, BEER, Action.PICK)
    cellar = MoveUseCase(game).execute(sid, Direction.DOWN)
    assert cellar.description.endswith("A RAT RUNS OFF WITH YOUR BEER.") is stolen


def test_the_random_port_makes_the_sid():
    game = InMemoryGame(random_source=FixedChance(0.99))
    assert start(game) == "000001-000000000002-00000003"


def test_the_high_score_port_gets_the_win():
    clock, sink = FixedClock(10), Recorder()
    game = InMemoryGame(clock=clock, high_scores=sink, random_source=FixedChance(0.99))
    sid = start(game)
    for way in ("south", "east", "down", "east", "north", "east"):
        MoveUseCase(game).execute(sid, Direction(way))
    assert game.players[sid].has_won, game.players[sid].location
    assert sink.lines == [("ANA", to_bag(game, game.players[sid]).score, clock.moment)]
