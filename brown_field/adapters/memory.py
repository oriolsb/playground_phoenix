"""Stores that keep everything in memory: no file is written (ENTRY-6)."""

import copy

from ..core.state import Account


class MemoryStore:
    """A SaveStore and an AccountStore in memory. Share one between games to simulate a restart."""

    def __init__(self) -> None:
        self.saves: dict[str, tuple[str, dict]] = {}
        self.accounts: dict[str, Account] = {}

    def load_saves(self) -> list[tuple[str, str, dict]]:
        return [(sid, name, copy.deepcopy(payload)) for sid, (name, payload) in self.saves.items()]

    def write_save(self, player_sid: str, name: str, payload: dict) -> str:
        self.saves.pop(player_sid, None)  # a new save goes last, as ORDER BY saved_at does
        self.saves[player_sid] = (name, copy.deepcopy(payload))
        return ":memory:"

    def load_accounts(self) -> list[Account]:
        return [copy.deepcopy(account) for account in self.accounts.values()]

    def write_account(self, account: Account) -> None:
        self.accounts[account.email] = copy.deepcopy(account)


class MemoryHighScores:
    def __init__(self) -> None:
        self.lines: list[tuple[str, int]] = []

    def append(self, name: str, score: int) -> None:
        self.lines.append((name, score))
