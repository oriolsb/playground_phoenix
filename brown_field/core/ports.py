"""The outbound ports: everything the core needs from the outside world.

The inbound ports, one per use case, are the Protocols in `brown_field.kata`.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING, Protocol, Sequence, TypeVar

if TYPE_CHECKING:
    from .state import Account

T = TypeVar("T")


class Clock(Protocol):
    def local_now(self) -> datetime:
        """The wall clock in the server's time zone. The market rule reads it."""

    def utc_now(self) -> datetime:
        """The time in UTC. Every stored time stamp uses it."""


class RandomSource(Protocol):
    def random(self) -> float: ...

    def choice(self, options: Sequence[T]) -> T: ...

    def randint(self, low: int, high: int) -> int: ...


class PasswordHasher(Protocol):
    def hash(self, password: str) -> str: ...


class SaveStore(Protocol):
    def write(self, player_sid: str, name: str, payload: dict, saved_at: str) -> str:
        """Store one player's save, and return where it went."""

    def load_all(self) -> list[tuple[str, str, dict]]:
        """Every save as (player_sid, name, payload), oldest save first."""


class AccountStore(Protocol):
    def write(self, account: "Account") -> None: ...

    def load_all(self) -> list["Account"]: ...


class HighScoreSink(Protocol):
    def append(self, name: str, score: int, at: str) -> None: ...


@dataclass
class Ports:
    """The adapters that one game uses. `brown_field.game` builds the defaults."""

    saves: SaveStore
    accounts: AccountStore
    high_scores: HighScoreSink
    clock: Clock
    random: RandomSource
    hasher: PasswordHasher
