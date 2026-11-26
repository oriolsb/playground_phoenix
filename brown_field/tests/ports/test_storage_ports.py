"""ARCH-4: with memory stores, the game saves, registers, logs in and quits with no file.

The stores are adapters handed to `InMemoryGame` (decision 0014). The rules
are SAVE-1, ACCOUNT-1, ACCOUNT-4 and ACCOUNT-6.
"""

from brown_field.adapters.memory.stores import MemoryAccounts, MemorySaves
from brown_field.game import (
    InMemoryGame,
    LoginUseCase,
    MoveUseCase,
    QuitGameUseCase,
    RegisterAccountUseCase,
    RegisterPlayerUseCase,
    SaveGameUseCase,
)
from brown_field.kata import Direction


def test_a_game_with_memory_stores_writes_no_file(tmp_path, monkeypatch, isolated_files):
    empty = tmp_path / "empty"
    empty.mkdir()
    monkeypatch.chdir(empty)
    monkeypatch.delenv("KATACOMBS_DB")
    saves, accounts = MemorySaves(), MemoryAccounts()
    game = InMemoryGame(saves=saves, accounts=accounts)

    sid = RegisterPlayerUseCase(game).execute("ANA").sid
    MoveUseCase(game).execute(sid, Direction.NORTH)
    assert SaveGameUseCase(game).execute(sid) == ":memory:"
    RegisterAccountUseCase(game).execute("bo@example.org", "secret", "Bo")
    player = LoginUseCase(game).execute("bo@example.org", "secret")
    QuitGameUseCase(game).execute(player.sid)

    assert list(empty.iterdir()) == []
    assert not isolated_files.db.exists()
    assert [saved.sid for saved in saves.load_all()] == [sid]
    assert accounts.rows["bo@example.org"].snapshot["location"] == "BRICK LANE"


def test_a_new_game_on_the_same_stores_brings_the_saved_player_back(isolated_files):
    saves, accounts = MemorySaves(), MemoryAccounts()
    first = InMemoryGame(saves=saves, accounts=accounts)
    sid = RegisterPlayerUseCase(first).execute("ANA").sid
    MoveUseCase(first).execute(sid, Direction.NORTH)
    SaveGameUseCase(first).execute(sid)

    second = InMemoryGame(saves=saves, accounts=accounts)
    assert second.players[sid].location == "OLD TRUMAN BREWERY"
    assert not isolated_files.db.exists()
