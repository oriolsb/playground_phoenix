"""The inbound ports of Katacombs, and the view models they answer.

The domain owns `Direction`, `Action`, `Item` and the error types (decision
0018). This module re-exports them, so their public names stay the same.
"""

from dataclasses import dataclass, field
from typing import Protocol

from .domain.errors import InvalidName, ItemNotFound, KatacombsError, NotAllowed, PlayerNotFound
from .domain.types import Action, Direction, Item

__all__ = [
    "AccountView", "Action", "Bag", "ChatLine", "Direction", "FinishedGame", "InboundPorts", "InspectBag",
    "InspectItem", "InvalidName", "Item", "ItemNotFound", "KatacombsError", "LegacyPickup",
    "ListPlayers", "Location", "Login", "LookAround", "LookInDirection", "Move", "NotAllowed",
    "Player", "PlayerNotFound", "QuitGame", "ReadMessages", "RegisterAccount", "RegisterPlayer",
    "SaveGame", "SendMessage", "ShowLeaderboard", "UseItem",
]


@dataclass
class Bag:
    items: list[Item] = field(default_factory=list)
    gold: int = 0
    # Added for the ports (decision 0015). The REST adapter reads it here.
    energy: int = 0

    @property
    def score(self) -> int:
        return self.gold + sum(item.value for item in self.items)


@dataclass
class Location:
    title: str
    description: str
    exits: list[Direction]
    items: list[Item]
    is_exit: bool = False


@dataclass
class Player:
    sid: str
    name: str
    location: Location
    bag: Bag
    has_won: bool = False
    # Added for the ports (decision 0015). The REST adapter reads it here.
    energy: int = 0


class RegisterPlayer(Protocol):
    def execute(self, name: str) -> Player: ...


class ListPlayers(Protocol):
    def execute(self) -> list[Player]: ...


class QuitGame(Protocol):
    def execute(self, player_sid: str) -> None: ...


class InspectItem(Protocol):
    def execute(self, item_sid: str) -> Item: ...


class InspectBag(Protocol):
    def execute(self, player_sid: str) -> Bag: ...


class UseItem(Protocol):
    def execute(self, player_sid: str, item_sid: str, action: Action) -> str: ...


class LookAround(Protocol):
    def execute(self, player_sid: str) -> Location: ...


class LookInDirection(Protocol):
    def execute(self, player_sid: str, direction: Direction) -> Location: ...


class Move(Protocol):
    def execute(self, player_sid: str, direction: Direction) -> Location: ...


class SaveGame(Protocol):
    def execute(self, player_sid: str) -> str: ...


# Added by decision 0015: the commands that had no port.


@dataclass
class ChatLine:
    name: str
    text: str
    at: str


@dataclass
class FinishedGame:
    name: str
    score: int
    moves: int


@dataclass
class AccountView:
    email: str
    name: str


class SendMessage(Protocol):
    def execute(self, player_sid: str, text: str) -> str: ...


class ReadMessages(Protocol):
    def execute(self, player_sid: str) -> list[ChatLine]: ...


class ShowLeaderboard(Protocol):
    def execute(self) -> list[FinishedGame]: ...


class RegisterAccount(Protocol):
    def execute(self, email: str, password: str, name: str) -> AccountView: ...


class Login(Protocol):
    def execute(self, email: str, password: str) -> Player: ...


class LegacyPickup(Protocol):
    def execute(self, player_sid: str, item_sid: str) -> str: ...


@dataclass
class InboundPorts:
    """Every inbound port, for a driving adapter to receive (decision 0019).

    The composition root fills it with the use cases. A test fills it with fakes.
    """

    register_player: RegisterPlayer
    list_players: ListPlayers
    quit_game: QuitGame
    inspect_item: InspectItem
    inspect_bag: InspectBag
    use_item: UseItem
    look_around: LookAround
    look_in_direction: LookInDirection
    move: Move
    save_game: SaveGame
    send_message: SendMessage
    read_messages: ReadMessages
    show_leaderboard: ShowLeaderboard
    register_account: RegisterAccount
    login: Login
    legacy_pickup: LegacyPickup
