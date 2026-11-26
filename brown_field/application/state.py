"""The state of one game, and the ports it reaches the outside through.

`GameState` is the context object of decision 0012: it holds the outbound
ports and the state, and each use case reads both from it. `InMemoryGame` in
`brown_field/game.py` builds it with the default adapters.
"""

import hashlib
import math
from collections import Counter
from dataclasses import dataclass, field
from datetime import timezone

from ..domain.constants import (
    CRATE,
    ITEMS_PER_SLOT,
    MANHOLE,
    ONE_WAY,
    OPPOSITE,
    START_ENERGY,
)
from ..domain.errors import ItemNotFound, PlayerNotFound
from ..kata import Bag, Direction, Item, Location, Player
from .ports_out import AccountStore, Clock, HighScoreSink, RandomSource, SaveStore, StoredAccount


@dataclass
class Place:
    title: str
    description: str
    exits: dict[Direction, str]
    items: list[str]
    gold: int = 0
    is_exit: bool = False


@dataclass
class PlayerState:
    sid: str
    name: str
    location: str
    bag: list[str] = field(default_factory=list)
    gold: int = 0
    energy: int = START_ENERGY
    moves: int = 0
    visited: set[str] = field(default_factory=set)
    opened: set[str] = field(default_factory=set)
    has_won: bool = False


# An account, as the game and the store keep it (decision 0014).
Account = StoredAccount


@dataclass
class ChatMessage:
    location: str
    name: str
    text: str
    at: str

def check_connections(places: dict[str, Place]) -> None:
    for place in places.values():
        for direction, target in place.exits.items():
            if (place.title, direction) in ONE_WAY:
                continue
            if places[target].exits.get(OPPOSITE[direction]) != place.title:
                raise ValueError(
                    f"{place.title} goes {direction.value} to {target}, "
                    f"but {target} does not go {OPPOSITE[direction].value} back"
                )


def market_is_cleaning(clock: Clock) -> bool:
    # Cleaning crew contract (2023): the market is closed from minute 50 to
    # minute 59 of each hour. Ask facilities before you change this.
    return clock.now().minute >= 50


def slots_used(names: list[str]) -> int:
    return sum(math.ceil(count / ITEMS_PER_SLOT) for count in Counter(names).values())


def password_hash(password: str) -> str:
    # TODO: bcrypt (2023)
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


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
        places: dict[str, Place],
        items: dict[str, Item],
    ) -> None:
        # The outbound ports (decisions 0013, 0014).
        self.clock = clock
        self.random_source = random_source
        self.high_scores = high_scores
        self.save_store = saves
        self.account_store = accounts
        self.places = places
        self.items = items
        self.gold_inside = {CRATE: 10}
        self.open_items: set[str] = set()
        self.locked_items: set[str] = {MANHOLE}
        self.players: dict[str, PlayerState] = {}
        self.finished_games: list[dict] = []
        self.accounts: dict[str, Account] = {}
        self.chat: list[ChatMessage] = []
        check_connections(self.places)
        self.load_saves()
        self.load_accounts()

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
            self.players[sid] = PlayerState(
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

    def visit(self, state: PlayerState, title: str) -> None:
        state.location = title
        if title not in state.visited:
            state.visited.add(title)
            state.gold += self.places[title].gold

    def connect(self, a: str, direction: Direction, b: str) -> None:
        self.places[a].exits[direction] = b
        self.places[b].exits[OPPOSITE[direction]] = a

    def disconnect(self, a: str, direction: Direction) -> None:
        b = self.places[a].exits.pop(direction)
        self.places[b].exits.pop(OPPOSITE[direction])

    def names_in_bag(self, state: PlayerState) -> list[str]:
        return [self.items[sid].name for sid in state.bag]

    def to_location(self, title: str, note: str = "") -> Location:
        place = self.places[title]
        return Location(
            title=place.title,
            description=f"{place.description} {note}".strip(),
            exits=list(place.exits),
            items=[self.items[sid] for sid in place.items],
            is_exit=place.is_exit,
        )

    def to_bag(self, state: PlayerState) -> Bag:
        return Bag(
            items=[self.items[sid] for sid in state.bag], gold=state.gold, energy=state.energy
        )

    def to_player(self, state: PlayerState) -> Player:
        return Player(
            sid=state.sid,
            name=state.name,
            location=self.to_location(state.location),
            bag=self.to_bag(state),
            has_won=state.has_won,
            energy=state.energy,
        )


