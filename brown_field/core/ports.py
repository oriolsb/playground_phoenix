"""The driven ports: what a game needs from outside the rules (decision 0012)."""

from collections.abc import Sequence
from datetime import datetime
from typing import Any, Protocol

from .state import Account


class SaveStore(Protocol):
    def load_saves(self) -> list[tuple[str, str, dict]]:
        """The saves as (player sid, name, payload), oldest first."""
        ...

    def write_save(self, player_sid: str, name: str, payload: dict) -> str:
        """Write or replace the save of a player; answer where it is."""
        ...


class AccountStore(Protocol):
    def load_accounts(self) -> list[Account]: ...

    def write_account(self, account: Account) -> None: ...


class HighScoreSink(Protocol):
    def append(self, name: str, score: int) -> None: ...


class Clock(Protocol):
    def __call__(self) -> datetime:
        """The local time of the server."""
        ...


class Random(Protocol):
    def random(self) -> float: ...

    def choice(self, seq: Sequence[Any]) -> Any: ...

    def randint(self, a: int, b: int) -> int: ...
