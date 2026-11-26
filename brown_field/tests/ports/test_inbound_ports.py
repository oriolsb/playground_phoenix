"""ENTRY-3: the six commands that had no port, at the port (decision 0015).

The rules are CHAT-1, CHAT-2, CHAT-3, BOARD-1, LEGACY-1, LEGACY-2 and
ACCOUNT-1. The same rules are pinned over REST in `tests/rest/`.
"""

import pytest

from brown_field.game import (
    InMemoryGame,
    LegacyPickupUseCase,
    LoginUseCase,
    MoveUseCase,
    ReadMessagesUseCase,
    RegisterAccountUseCase,
    RegisterPlayerUseCase,
    SendMessageUseCase,
    ShowLeaderboardUseCase,
    UseItemUseCase,
)
from brown_field.kata import AccountView, Action, ChatLine, Direction, FinishedGame

BEER = "000100-000000000000-00000001"
WIN_ROUTE = ["south", "east", "down", "east", "north", "east"]


@pytest.fixture
def game() -> InMemoryGame:
    return InMemoryGame()


def start(game: InMemoryGame, name: str = "ANA") -> str:
    return RegisterPlayerUseCase(game).execute(name).sid


def test_a_chat_message_is_sent_and_counts_a_move(game):
    sid = start(game)
    assert SendMessageUseCase(game).execute(sid, "HI") == "SENT."
    assert game.players[sid].moves == 1


def test_a_player_reads_the_chat_of_the_location_only(game):
    ana, bo = start(game), start(game, "BO")
    SendMessageUseCase(game).execute(ana, "HERE")
    MoveUseCase(game).execute(bo, Direction.NORTH)
    SendMessageUseCase(game).execute(bo, "THERE")
    lines = ReadMessagesUseCase(game).execute(ana)
    assert [(line.name, line.text) for line in lines] == [("ANA", "HERE")]
    assert all(isinstance(line, ChatLine) for line in lines)


def test_the_leaderboard_ranks_the_highest_score_first(game):
    for name in ("LOW", "HIGH"):
        sid = start(game, name)
        if name == "HIGH":
            MoveUseCase(game).execute(sid, Direction.NORTH)  # 5 gold in the brewery
            MoveUseCase(game).execute(sid, Direction.SOUTH)
        for way in WIN_ROUTE:
            MoveUseCase(game).execute(sid, Direction(way))
    board = ShowLeaderboardUseCase(game).execute()
    assert [entry.name for entry in board] == ["HIGH", "LOW"]
    assert all(isinstance(entry, FinishedGame) for entry in board)
    assert board[0].score > board[1].score


def test_the_legacy_pickup_skips_the_move_count(game):
    sid = start(game)
    MoveUseCase(game).execute(sid, Direction.NORTH)
    moves = game.players[sid].moves
    assert LegacyPickupUseCase(game).execute(sid, BEER) == "OK"
    assert BEER in game.players[sid].bag
    assert game.players[sid].moves == moves


def test_the_legacy_pickup_of_an_item_elsewhere_changes_nothing(game):
    sid = start(game)
    assert LegacyPickupUseCase(game).execute(sid, BEER) == "OK"
    assert game.players[sid].bag == []
    assert BEER in game.places["OLD TRUMAN BREWERY"].items


def test_the_registration_answers_no_password_digest(game):
    account = RegisterAccountUseCase(game).execute("bo@example.org", "secret", "Bo")
    assert account == AccountView(email="bo@example.org", name="BO")


def test_the_login_answers_the_player_with_its_energy(game):
    RegisterAccountUseCase(game).execute("bo@example.org", "secret", "Bo")
    player = LoginUseCase(game).execute("bo@example.org", "secret")
    MoveUseCase(game).execute(player.sid, Direction.NORTH)
    UseItemUseCase(game).execute(player.sid, BEER, Action.PICK)
    again = LoginUseCase(game).execute("bo@example.org", "secret")
    assert again.energy == 11
    assert again.bag.energy == 11
