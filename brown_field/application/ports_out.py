"""The outbound ports: what the game needs from the outside (decision 0012).

Each port is a `Protocol`, like a Java interface that a class satisfies by
its shape. An adapter in `brown_field/adapters/` implements it, and
`InMemoryGame` takes one adapter per port, with a default.
"""

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Protocol, TypeVar

from ..domain.world import WorldData

T = TypeVar("T")


class Clock(Protocol):
    """The time (decision 0013). `now` answers the local time, aware."""

    def now(self) -> datetime: ...


class RandomSource(Protocol):
    """Chance (decision 0013): the rat, and the digits of a sid."""

    def chance(self) -> float:
        """A number in [0, 1)."""
        ...

    def choice(self, items: Sequence[T]) -> T: ...

    def digits(self, count: int) -> str:
        """`count` random decimal digits, zero-padded."""
        ...


class HighScoreSink(Protocol):
    """Where a win appends its high-score line (WIN-3, decision 0002)."""

    def append(self, name: str, score: int, at: datetime) -> None: ...


@dataclass
class SavedPlayer:
    """One row of the saves: a player sid, a name, and its player-state payload."""

    sid: str
    name: str
    payload: dict[str, Any]


@dataclass
class StoredAccount:
    """One account, as the account store keeps it (STORE-2)."""

    email: str
    password_hash: str
    name: str
    player_sid: str | None = None
    snapshot: dict[str, Any] | None = None


class SaveStore(Protocol):
    """The saves (decision 0014, STORE-1, SAVE-2)."""

    def load_all(self) -> list[SavedPlayer]:
        """Every save, in the order of its save time."""
        ...

    def save(self, player: SavedPlayer, at: datetime) -> str:
        """Write or replace the save of one player; answer where it went."""
        ...


class AccountStore(Protocol):
    """The accounts with their snapshots (decision 0014, STORE-2)."""

    def load_all(self) -> list[StoredAccount]: ...

    def put(self, account: StoredAccount) -> None: ...


class WorldSource(Protocol):
    """The fixed world (decision 0016, WORLD-1). Each load answers a fresh copy."""

    def load(self) -> WorldData: ...
