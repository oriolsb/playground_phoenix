from dataclasses import dataclass, field
from enum import Enum
from typing import Protocol


class Direction(Enum):
    NORTH = "north"
    SOUTH = "south"
    EAST = "east"
    WEST = "west"
    UP = "up"
    DOWN = "down"


class Action(Enum):
    OPEN = "open"
    CLOSE = "close"
    PICK = "pick"
    DROP = "drop"
    USE = "use"


@dataclass
class Item:
    sid: str
    name: str
    description: str
    actions: list[Action]
    value: int = 0


@dataclass
class Bag:
    items: list[Item] = field(default_factory=list)
    gold: int = 0
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


@dataclass
class ChatMessage:
    name: str
    text: str
    at: str


@dataclass
class FinishedGame:
    name: str
    score: int
    moves: int


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


class SendMessage(Protocol):
    def execute(self, player_sid: str, text: str) -> str: ...


class ReadMessages(Protocol):
    def execute(self, player_sid: str) -> list[ChatMessage]: ...


class Leaderboard(Protocol):
    def execute(self) -> list[FinishedGame]: ...


class LegacyPickup(Protocol):
    def execute(self, player_sid: str, item_sid: str) -> str: ...
