"""Saves and accounts in one SQLite file (decision 0005).

The file is named by KATACOMBS_DB, read at each call as before, so a test or
the support laptop can point it elsewhere.
"""

import json
import os
import sqlite3

from ..core.state import Account

SAVE_SCHEMA = """
CREATE TABLE IF NOT EXISTS saves (
    player_sid TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    payload TEXT NOT NULL,
    saved_at TEXT NOT NULL
)
"""

ACCOUNTS_SCHEMA = """
CREATE TABLE IF NOT EXISTS accounts (
    email TEXT PRIMARY KEY,
    password_hash TEXT NOT NULL,
    name TEXT NOT NULL,
    player_sid TEXT,
    snapshot TEXT
)
"""


def save_path() -> str:
    # The support laptop sets KATACOMBS_DB. Nobody else does.
    return os.environ.get("KATACOMBS_DB", "katacombs.db")


class SqliteSaveStore:
    def write(self, player_sid: str, name: str, payload: dict, saved_at: str) -> str:
        path = save_path()
        connection = sqlite3.connect(path)
        try:
            connection.execute(SAVE_SCHEMA)
            connection.execute(
                "INSERT OR REPLACE INTO saves"
                " (player_sid, name, payload, saved_at) VALUES (?, ?, ?, ?)",
                (player_sid, name, json.dumps(payload), saved_at),
            )
            connection.commit()
        finally:
            connection.close()
        return path

    def load_all(self) -> list[tuple[str, str, dict]]:
        path = save_path()
        if not os.path.exists(path):
            return []
        connection = sqlite3.connect(path)
        try:
            connection.execute(SAVE_SCHEMA)
            rows = connection.execute(
                "SELECT player_sid, name, payload FROM saves ORDER BY saved_at"
            ).fetchall()
        finally:
            connection.close()
        return [(sid, name, json.loads(payload)) for sid, name, payload in rows]


class SqliteAccountStore:
    def write(self, account: Account) -> None:
        connection = sqlite3.connect(save_path())
        try:
            connection.execute(ACCOUNTS_SCHEMA)
            connection.execute(
                "INSERT OR REPLACE INTO accounts"
                " (email, password_hash, name, player_sid, snapshot) VALUES (?, ?, ?, ?, ?)",
                (
                    account.email,
                    account.password_hash,
                    account.name,
                    account.player_sid,
                    json.dumps(account.snapshot) if account.snapshot is not None else None,
                ),
            )
            connection.commit()
        finally:
            connection.close()

    def load_all(self) -> list[Account]:
        path = save_path()
        if not os.path.exists(path):
            return []
        connection = sqlite3.connect(path)
        try:
            connection.execute(ACCOUNTS_SCHEMA)
            rows = connection.execute(
                "SELECT email, password_hash, name, player_sid, snapshot FROM accounts"
            ).fetchall()
        finally:
            connection.close()
        return [
            Account(
                email=email,
                password_hash=hashed,
                name=name,
                player_sid=player_sid,
                snapshot=json.loads(snapshot) if snapshot else None,
            )
            for email, hashed, name, player_sid, snapshot in rows
        ]
