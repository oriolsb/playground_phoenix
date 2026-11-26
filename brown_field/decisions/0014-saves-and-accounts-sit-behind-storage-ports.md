# 0014 — Saves and accounts sit behind storage ports

- **Status:** proposed
- **Date:** 2026-11-26
- **Need:** operational. A port test must build a game with no file. The
  support laptop and every stored account must see no change (decision 0005).
- **Traces to:** `ARCH-4`, `STORE-1`, `STORE-2`, `SAVE-1`, `SAVE-2`, `ACCOUNT-4`, `ACCOUNT-6`, `CONF-1`, `ENTRY-1`, `ENTRY-2`.
- **Change:** hexagon-3-storage
- **Evidence (legacy code only):**
  - `game.py:419-420`: the constructor of `InMemoryGame` calls
    `load_saves()` and `load_accounts()`, which open SQLite.
  - `game.py:736-772`: `SaveGameUseCase` builds the payload inline and
    writes the row with `sqlite3`.
  - `game.py:373-383`: `snapshot_of()` builds the same payload for the
    snapshot. Two copies of one shape.
  - `game.py:386-403`: `write_account()` opens SQLite for each write.
  - `game.py:463-465`: a save whose location left the world is skipped.

## Context

Storage is called from the constructor and from three use cases. Each
call opens a new connection and runs `CREATE TABLE IF NOT EXISTS`. The
payload has two builders. Every port test needs `KATACOMBS_DB` pointed at a
temporary file (`tests/conftest.py:81-89`), because building a game reads
the disk.

The database file is a boundary with stored data. Its tables, columns and
payload are accepted rules (STORE-1, STORE-2, decision 0005). The password
digest is contested (STORE-3).

## Decision

Two outbound ports, in `brown_field/application/ports_out.py`:

```python
class SaveStore(Protocol):
    def load_all(self) -> list[SavedPlayer]: ...      # ordered by saved_at
    def save(self, player: SavedPlayer, at: datetime) -> str: ...  # answers the path

class AccountStore(Protocol):
    def load_all(self) -> list[StoredAccount]: ...
    def put(self, account: StoredAccount) -> None: ...
```

In Java terms: two repository interfaces, with a JDBC adapter and an
in-memory adapter.

- `adapters/sqlite/` holds the two SQLite adapters, with the tables of
  STORE-1 and STORE-2, on the file of CONF-1. The path rule lives there.
- `adapters/memory/` holds two memory adapters, for tests and tools.
- One function builds the player-state payload, for the save and for the
  snapshot. It matches `player-state.schema.json`. A save from before
  2023, with no energy, still stops the start, as SAVE-2 records. That
  open question is not answered here.
- `InMemoryGame` takes `saves` and `accounts` as keyword arguments. With
  none, it builds the SQLite adapters and loads both stores when it is
  built, as today. So `create_app()` and `brown_field.api.app` still read
  the file at their start (ENTRY-1, ENTRY-2).
- The rule "a save whose location left the world is skipped" stays in the
  game, not in the adapter. It is a game rule (SAVE-2), not a storage rule.
- The password digest stays where it is in this stage. A `PasswordHasher`
  port belongs to the answer of STORE-3, which is still contested.

## Alternatives rejected

| Alternative | Why you rejected it |
| --- | --- |
| One `Storage` port for saves and accounts | They share a file today, but not a lifecycle: a save is written on request, an account on register, login and quit. One port makes a fake of saves also fake accounts. |
| Load lazily, on the first request, not when the game is built | ENTRY-2 says `app` reads the file once, at the import. A lazy load changes the moment of the first read, and an error in the file then shows on a request, not at start. |
| Keep one connection open for the life of the game | Faster. It changes the behavior when two processes share the file (the support laptop), and OPS-1 already passes with one connection per call. |
| Add a `PasswordHasher` port now | STORE-3 is contested: the stronger hash and the migration of stored accounts are open. A port now would fix an answer nobody gave. |

## Consequences

**Easier:** `InMemoryGame(saves=MemorySaves(), accounts=MemoryAccounts())`
builds a game with no file. The payload has one builder.

**More difficult:** the SQLite adapters must keep the tables byte for byte.
The old save without energy (`tests/golden/old-save-without-energy.db`)
is the oracle: it must fail the start exactly as it does today.

**Risks that stay:** the password digest (STORE-3) and the shared file
between processes.

## Fitness functions

| Function | Target | How to run it | Need that it protects |
| --- | --- | --- | --- |
| `sqlite3` is imported only under `adapters/sqlite/` | zero hits | `uv run pytest brown_field/tests/fitness -m ARCH-4` (to write) | Rules do not depend on SQLite |
| A game with memory stores writes no file | pass | `uv run pytest -m ARCH-4` (to write) | Port tests with no disk |
| The tables, the payload and the old save | pass | `uv run pytest brown_field/tests/boundary -m "STORE-1 or STORE-2 or SAVE-2"` | Every stored save and account (decision 0005) |
