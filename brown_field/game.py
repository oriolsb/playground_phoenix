"""The composition root: a Katacombs game wired to the real adapters.

The rules live in `brown_field.core`; the I/O lives in `brown_field.adapters`.
This module puts them together, and keeps the names that the port tests and
decision 0008 freeze: `InMemoryGame`, the use cases, and the error types.
"""

from .adapters.highscore_file import JsonlHighScoreSink
from .adapters.sqlite_store import SqliteAccountStore, SqliteSaveStore
from .adapters.system import Sha256PasswordHasher, StdlibRandom, SystemClock
from .core.accounts import LoginUseCase, RegisterAccountUseCase
from .core.chat import ReadMessagesUseCase, SendMessageUseCase
from .core.errors import InvalidName, ItemNotFound, KatacombsError, NotAllowed, PlayerNotFound
from .core.items import InspectBagUseCase, InspectItemUseCase, UseItemUseCase
from .core.legacy import PickUpUseCase
from .core.looking import LookAroundUseCase, LookInDirectionUseCase
from .core.moving import MoveUseCase
from .core.players import (
    ListPlayersUseCase,
    QuitGameUseCase,
    RegisterPlayerUseCase,
    ShowLeaderboardUseCase,
    ViewPlayerUseCase,
)
from .core.ports import Ports
from .core.saving import SaveGameUseCase
from .core.state import GameState

__all__ = [
    "InMemoryGame",
    "default_ports",
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
    "LookAroundUseCase",
    "LookInDirectionUseCase",
    "MoveUseCase",
    "UseItemUseCase",
    "SaveGameUseCase",
    "RegisterAccountUseCase",
    "LoginUseCase",
    "ViewPlayerUseCase",
    "ShowLeaderboardUseCase",
    "PickUpUseCase",
    "SendMessageUseCase",
    "ReadMessagesUseCase",
]


def default_ports() -> Ports:
    return Ports(
        saves=SqliteSaveStore(),
        accounts=SqliteAccountStore(),
        high_scores=JsonlHighScoreSink(),
        clock=SystemClock(),
        random=StdlibRandom(),
        hasher=Sha256PasswordHasher(),
    )


class InMemoryGame(GameState):
    """A game in memory, with saves and accounts in SQLite, unless other ports are given."""

    def __init__(self, ports: Ports | None = None) -> None:
        super().__init__(ports or default_ports())
