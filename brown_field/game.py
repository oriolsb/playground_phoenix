"""The composition root of the game-server (decision 0012).

`InMemoryGame` builds the game with the default adapters. This module also
re-exports every name of the frozen boundary (decision 0008, ENTRY-3), so
`from brown_field.game import MoveUseCase, NotAllowed` keeps working.
"""

from .adapters.files.high_scores import JsonlHighScores
from .adapters.files.world_json import JsonWorld
from .adapters.sqlite.stores import SqliteAccounts, SqliteSaves
from .adapters.system.clock import SystemClock
from .adapters.system.random_source import StdRandom
from .application.ports_out import (
    AccountStore,
    Clock,
    HighScoreSink,
    RandomSource,
    SaveStore,
    WorldSource,
)
from .application.state import Account, ChatMessage, GameState, PlayerState
from .domain.world import Place
from .application.use_cases import (
    InspectBagUseCase,
    InspectItemUseCase,
    LegacyPickupUseCase,
    ListPlayersUseCase,
    LoginUseCase,
    LookAroundUseCase,
    LookInDirectionUseCase,
    MoveUseCase,
    QuitGameUseCase,
    ReadMessagesUseCase,
    RegisterAccountUseCase,
    RegisterPlayerUseCase,
    SaveGameUseCase,
    SendMessageUseCase,
    ShowLeaderboardUseCase,
    UseItemUseCase,
)
from .domain.errors import InvalidName, ItemNotFound, KatacombsError, NotAllowed, PlayerNotFound

__all__ = [
    "Account",
    "ChatMessage",
    "InMemoryGame",
    "InspectBagUseCase",
    "InspectItemUseCase",
    "InvalidName",
    "ItemNotFound",
    "KatacombsError",
    "LegacyPickupUseCase",
    "ListPlayersUseCase",
    "LoginUseCase",
    "LookAroundUseCase",
    "LookInDirectionUseCase",
    "MoveUseCase",
    "NotAllowed",
    "Place",
    "PlayerNotFound",
    "PlayerState",
    "QuitGameUseCase",
    "ReadMessagesUseCase",
    "RegisterAccountUseCase",
    "RegisterPlayerUseCase",
    "SaveGameUseCase",
    "SendMessageUseCase",
    "ShowLeaderboardUseCase",
    "UseItemUseCase",
]


class InMemoryGame(GameState):
    """The game with one adapter per outbound port, each with a default."""

    def __init__(
        self,
        *,
        clock: Clock | None = None,
        random_source: RandomSource | None = None,
        high_scores: HighScoreSink | None = None,
        saves: SaveStore | None = None,
        accounts: AccountStore | None = None,
        world: WorldSource | None = None,
    ) -> None:
        # Each default calls the standard library or the database file at the
        # moment of each call, as the code did before (decisions 0013, 0014).
        super().__init__(
            clock=clock or SystemClock(),
            random_source=random_source or StdRandom(),
            high_scores=high_scores or JsonlHighScores(),
            saves=saves or SqliteSaves(),
            accounts=accounts or SqliteAccounts(),
            world=world or JsonWorld(),
        )
