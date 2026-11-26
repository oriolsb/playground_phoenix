"""The state of one game, and the ports it reaches the outside through.

`GameState` is the context object of decision 0012: it holds the outbound
ports and the state, and each use case reads both from it. `InMemoryGame` in
`brown_field/game.py` builds it with the default adapters.
"""

from dataclasses import dataclass
from datetime import timezone

from ..domain.player import PlayerState
from ..domain.world import Place, World
from ..domain.errors import ItemNotFound, PlayerNotFound
from ..kata import Item
from .ports_out import (
    AccountStore,
    Clock,
    HighScoreSink,
    RandomSource,
    SaveStore,
    StoredAccount,
    WorldSource,
)


# An account, as the game and the store keep it (decision 0014).
Account = StoredAccount


@dataclass
class ChatMessage:
    location: str
    name: str
    text: str
    at: str

def player_from_payload(sid: str, name: str, data: dict) -> PlayerState:
    """A player from a save or a snapshot (player-state.schema.json).

    A payload from before 2023 has no energy: the `KeyError` stops the start,
    as SAVE-2 records.
    """
    return PlayerState(
        sid=sid,
        name=name,
        location=data["location"],
        bag=list(data["bag"]),
        gold=data["gold"],
        energy=data["energy"],
        moves=data["moves"],
        visited=set(data["visited"]),
        opened=set(data["opened"]),
        has_won=data["has_won"],
    )


def snapshot_of(state: "PlayerState") -> dict:
    return {
        "location": state.location,
        "bag": list(state.bag),
        "gold": state.gold,
        "energy": state.energy,
        "moves": state.moves,
        "visited": sorted(state.visited),
        "opened": sorted(state.opened),
        "has_won": state.has_won,
    }




class GameState:
    """The players, the world state, the accounts, the chat and the ports."""

    def __init__(
        self,
        *,
        clock: Clock,
        random_source: RandomSource,
        high_scores: HighScoreSink,
        saves: SaveStore,
        accounts: AccountStore,
        world: WorldSource,
    ) -> None:
        # The outbound ports (decisions 0013, 0014).
        self.clock = clock
        self.random_source = random_source
        self.high_scores = high_scores
        self.save_store = saves
        self.account_store = accounts
        # The fixed world, a fresh copy for this game (decisions 0016, 0017).
        self.world = World(world.load())
        self.players: dict[str, PlayerState] = {}
        self.finished_games: list[dict] = []
        self.accounts: dict[str, Account] = {}
        self.chat: list[ChatMessage] = []
        self.load_saves()
        self.load_accounts()

    # The world, read through `self.world` (decision 0017). These names stay
    # for the code and the tests that read them.
    @property
    def start(self) -> str:
        return self.world.start

    @property
    def places(self) -> dict[str, Place]:
        return self.world.places

    @property
    def items(self) -> dict[str, Item]:
        return self.world.items

    def load_accounts(self) -> None:
        for account in self.account_store.load_all():
            self.accounts[account.email] = account

    def account_of(self, player_sid: str) -> Account | None:
        for account in self.accounts.values():
            if account.player_sid == player_sid:
                return account
        return None

    def load_saves(self) -> None:
        # A restart reads the saves, so a player keeps the bag and the place.
        # The world is not in the save. Nobody wrote down why.
        for saved in self.save_store.load_all():
            sid, name, data = saved.sid, saved.name, saved.payload
            if data["location"] not in self.places:
                # The world changed under an old save.
                continue
            self.players[sid] = player_from_payload(sid, name, data)

    def now_iso(self) -> str:
        return self.clock.now().astimezone(timezone.utc).isoformat(timespec="seconds")

    def new_sid(self) -> str:
        while True:
            sid = (
                f"{self.random_source.digits(6)}-"
                f"{self.random_source.digits(12)}-"
                f"{self.random_source.digits(8)}"
            )
            if sid not in self.players and sid not in self.items:
                return sid

    def player(self, sid: str) -> PlayerState:
        if sid not in self.players:
            raise PlayerNotFound(f"PLAYER {sid} NOT FOUND.")
        return self.players[sid]

    def item(self, sid: str) -> Item:
        if sid not in self.items:
            raise ItemNotFound(f"ITEM {sid} NOT FOUND.")
        return self.items[sid]

    def names_in_bag(self, state: PlayerState) -> list[str]:
        return [self.items[sid].name for sid in state.bag]

