"""Decision 0021: the default adapters have one builder, and InMemoryGame keeps its signature."""

import inspect

from brown_field.adapters.memory.stores import MemoryAccounts, MemorySaves
from brown_field.adapters.sqlite.stores import SqliteAccounts, SqliteSaves
from brown_field.adapters.system.clock import SystemClock
from brown_field.game import InMemoryGame, default_adapters


def test_the_builder_gives_each_default_and_keeps_an_override():
    saves = MemorySaves()
    adapters = default_adapters(saves=saves)
    assert adapters["saves"] is saves
    assert isinstance(adapters["accounts"], SqliteAccounts)
    assert isinstance(adapters["clock"], SystemClock)
    assert not isinstance(default_adapters()["saves"], MemorySaves)
    assert isinstance(default_adapters()["saves"], SqliteSaves)


def test_in_memory_game_keeps_its_keyword_signature():
    names = list(inspect.signature(InMemoryGame).parameters)
    assert names == ["clock", "random_source", "high_scores", "saves", "accounts", "world"]
    assert all(p.kind is p.KEYWORD_ONLY for p in inspect.signature(InMemoryGame).parameters.values())


def test_in_memory_game_passes_its_adapters_through():
    saves, accounts = MemorySaves(), MemoryAccounts()
    game = InMemoryGame(saves=saves, accounts=accounts)
    assert (game.save_store, game.account_store) == (saves, accounts)
