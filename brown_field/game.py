"""The composition root of the game-server (decision 0012).

`InMemoryGame` builds the game with the default adapters. This module also
re-exports every name of the frozen boundary (decision 0008, ENTRY-3), so
`from brown_field.game import MoveUseCase, NotAllowed` keeps working.
"""

from typing import Any

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
from .kata import InboundPorts
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
    "default_adapters",
    "inbound_ports",
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


def default_adapters(
    *,
    clock: Clock | None = None,
    random_source: RandomSource | None = None,
    high_scores: HighScoreSink | None = None,
    saves: SaveStore | None = None,
    accounts: AccountStore | None = None,
    world: WorldSource | None = None,
) -> dict[str, Any]:
    """The six adapters of a game: each given one, or its default (decision 0021).

    Each default calls the standard library or the database file at the
    moment of each call, as the code did before (decisions 0013, 0014).
    """
    return {
        "clock": clock or SystemClock(),
        "random_source": random_source or StdRandom(),
        "high_scores": high_scores or JsonlHighScores(),
        "saves": saves or SqliteSaves(),
        "accounts": accounts or SqliteAccounts(),
        "world": world or JsonWorld(),
    }


class InMemoryGame(GameState):
    """The game built from `default_adapters`.

    The name is frozen (decision 0008). Despite it, the defaults are the
    database file, the high-score file and `world.json`, not memory. For a
    game with no file, pass the stores of `adapters/memory/`.
    """

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
        super().__init__(
            **default_adapters(
                clock=clock,
                random_source=random_source,
                high_scores=high_scores,
                saves=saves,
                accounts=accounts,
                world=world,
            )
        )


def inbound_ports(game: GameState) -> InboundPorts:
    """The use cases of one game, as the inbound ports a driving adapter receives.

    The use cases hold no state of their own, so one instance per game
    behaves as one per request (decision 0019).
    """
    return InboundPorts(
        register_player=RegisterPlayerUseCase(game),
        list_players=ListPlayersUseCase(game),
        quit_game=QuitGameUseCase(game),
        inspect_item=InspectItemUseCase(game),
        inspect_bag=InspectBagUseCase(game),
        use_item=UseItemUseCase(game),
        look_around=LookAroundUseCase(game),
        look_in_direction=LookInDirectionUseCase(game),
        move=MoveUseCase(game),
        save_game=SaveGameUseCase(game),
        send_message=SendMessageUseCase(game),
        read_messages=ReadMessagesUseCase(game),
        show_leaderboard=ShowLeaderboardUseCase(game),
        register_account=RegisterAccountUseCase(game),
        login=LoginUseCase(game),
        legacy_pickup=LegacyPickupUseCase(game),
    )
