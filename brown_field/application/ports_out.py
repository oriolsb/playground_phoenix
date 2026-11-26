"""The outbound ports: what the game needs from the outside (decision 0012).

Each port is a `Protocol`, like a Java interface that a class satisfies by
its shape. An adapter in `brown_field/adapters/` implements it, and
`InMemoryGame` takes one adapter per port, with a default.
"""

from collections.abc import Sequence
from datetime import datetime
from typing import Protocol, TypeVar

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
