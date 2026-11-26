"""Saves and accounts in memory: a game that touches no file (ARCH-4)."""

import copy
from datetime import datetime

from ...application.ports_out import SavedPlayer, StoredAccount


class MemorySaves:
    def __init__(self) -> None:
        self.rows: dict[str, tuple[datetime, SavedPlayer]] = {}

    def load_all(self) -> list[SavedPlayer]:
        ordered = sorted(self.rows.values(), key=lambda row: row[0])
        return [copy.deepcopy(player) for _, player in ordered]

    def save(self, player: SavedPlayer, at: datetime) -> str:
        self.rows[player.sid] = (at, copy.deepcopy(player))
        return ":memory:"


class MemoryAccounts:
    def __init__(self) -> None:
        self.rows: dict[str, StoredAccount] = {}

    def load_all(self) -> list[StoredAccount]:
        return [copy.deepcopy(account) for account in self.rows.values()]

    def put(self, account: StoredAccount) -> None:
        self.rows[account.email] = copy.deepcopy(account)
