"""The game with its default adapters, and the names of the port tier (decision 0008).

The rules live in `brown_field/core/`; this module wires the SQLite file,
the high-score file and the stdlib clock and chance into `InMemoryGame()`.
"""

from .adapters.highscores import JsonlHighScores
from .adapters.sqlite_store import SqliteStore
from .adapters.system import local_now, stdlib
from .core.accounts import LoginUseCase, RegisterAccountUseCase
from .core.chat import ReadMessagesUseCase, SendMessageUseCase
from .core.errors import InvalidName, ItemNotFound, KatacombsError, NotAllowed, PlayerNotFound
from .core.game import Game
from .core.items import InspectBagUseCase, InspectItemUseCase, LegacyPickupUseCase, UseItemUseCase
from .core.looking import LookAroundUseCase, LookInDirectionUseCase
from .core.movement import MoveUseCase
from .core.players import ListPlayersUseCase, QuitGameUseCase, RegisterPlayerUseCase
from .core.ports import AccountStore, Clock, HighScoreSink, Random, SaveStore
from .core.saving import SaveGameUseCase
from .core.winning import LeaderboardUseCase


class InMemoryGame(Game):
    """A game on the given ports; each one left out is the default adapter of today (ENTRY-6, ENTRY-7)."""

    def __init__(
        self,
        saves: SaveStore | None = None,
        accounts: AccountStore | None = None,
        highscores: HighScoreSink | None = None,
        clock: Clock | None = None,
        rng: Random | None = None,
        world: dict | None = None,
    ) -> None:
        store = SqliteStore()
        super().__init__(
            saves=saves or store,
            accounts=accounts or store,
            highscores=highscores or JsonlHighScores(),
            clock=clock or local_now,
            rng=rng or stdlib,
            world=world,
        )


__all__ = [
    "InMemoryGame",
    "KatacombsError",
    "PlayerNotFound",
    "ItemNotFound",
    "InvalidName",
    "NotAllowed",
    "RegisterPlayerUseCase",
    "ListPlayersUseCase",
    "QuitGameUseCase",
    "InspectItemUseCase",
    "InspectBagUseCase",
    "UseItemUseCase",
    "LookAroundUseCase",
    "LookInDirectionUseCase",
    "MoveUseCase",
    "SaveGameUseCase",
    "RegisterAccountUseCase",
    "LoginUseCase",
    "SendMessageUseCase",
    "ReadMessagesUseCase",
    "LeaderboardUseCase",
    "LegacyPickupUseCase",
]
