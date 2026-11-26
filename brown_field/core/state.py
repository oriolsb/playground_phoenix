"""The state of one running game: the world as it changes, the players, the accounts and the chat.

It lives in memory. At start it restores the saved players and the accounts
through the ports; the world, the chat and the finished games start fresh.
"""

from dataclasses import dataclass, field

from ..kata import Bag, Direction, Item, Location, Player
from .errors import ItemNotFound, PlayerNotFound
from .ports import Ports
from .rules import START_ENERGY
from .world import CRATE, MANHOLE, OPPOSITE, Place, build_items, build_places, check_connections


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


@dataclass
class Account:
    email: str
    password_hash: str
    name: str
    player_sid: str | None = None
    snapshot: dict | None = None


@dataclass
class ChatMessage:
    location: str
    name: str
    text: str
    at: str


@dataclass
class FinishedGame:
    name: str
    score: int
    moves: int


def snapshot_of(state: PlayerState) -> dict:
    """What a save and an account keep of a player. The world is not in it."""
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


def player_from(sid: str, name: str, data: dict) -> PlayerState:
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


class GameState:
    def __init__(self, ports: Ports) -> None:
        self.ports = ports
        self.places = build_places()
        self.items = build_items()
        self.gold_inside = {CRATE: 10}
        self.open_items: set[str] = set()
        self.locked_items: set[str] = {MANHOLE}
        self.players: dict[str, PlayerState] = {}
        self.finished_games: list[FinishedGame] = []
        self.accounts: dict[str, Account] = {}
        self.chat: list[ChatMessage] = []
        check_connections(self.places)
        self.load_saves()
        self.load_accounts()

    def load_accounts(self) -> None:
        for account in self.ports.accounts.load_all():
            self.accounts[account.email] = account

    def account_of(self, player_sid: str) -> Account | None:
        for account in self.accounts.values():
            if account.player_sid == player_sid:
                return account
        return None

    def load_saves(self) -> None:
        # A restart reads the saves, so a player keeps the bag and the place.
        # The world is not in the save. Nobody wrote down why.
        for sid, name, data in self.ports.saves.load_all():
            if data["location"] not in self.places:
                # The world changed under an old save.
                continue
            self.players[sid] = player_from(sid, name, data)

    def new_sid(self) -> str:
        draw = self.ports.random.randint
        while True:
            sid = f"{draw(0, 999999):06d}-{draw(0, 999999999999):012d}-{draw(0, 99999999):08d}"
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
        place: Place = self.places[title]
        return Location(
            title=place.title,
            description=f"{place.description} {note}".strip(),
            exits=list(place.exits),
            items=[self.items[sid] for sid in place.items],
            is_exit=place.is_exit,
        )

    def to_bag(self, state: PlayerState) -> Bag:
        return Bag(items=[self.items[sid] for sid in state.bag], gold=state.gold)

    def to_player(self, state: PlayerState) -> Player:
        return Player(
            sid=state.sid,
            name=state.name,
            location=self.to_location(state.location),
            bag=self.to_bag(state),
            has_won=state.has_won,
            energy=state.energy,
        )
