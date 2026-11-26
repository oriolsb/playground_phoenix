# Proposal — hexagon-3-storage

Structure adapted from the OpenSpec proposal template (MIT).

Stage 3 of 6 of the move to ports and adapters (decision 0012). It puts
the saves and the accounts behind storage ports (decision 0014).

## Need

- Who: the team that restructures the game-server; the support laptop and
  every stored account (decision 0005).
- Why: SQLite is called in four places: the constructor of `InMemoryGame`
  (`game.py:419-420`, `load_saves`, `load_accounts`), `SaveGameUseCase`
  (`game.py:736-772`), `write_account` (`game.py:386-403`). The save
  payload is built twice, once inline in `SaveGameUseCase` and once in
  `snapshot_of` (`game.py:373-383`). A port test cannot build a game
  without touching the file system, so each test needs `KATACOMBS_DB`.
- Kind: operational
- Measurable as: ARCH-4 (`sqlite3` imported only under
  `brown_field/adapters/sqlite/`; a game built with memory stores writes no
  file). Source: decision 0014.

## What changes

- New outbound ports `SaveStore` and `AccountStore`, in
  `brown_field/application/ports_out.py`.
- New adapters: `adapters/sqlite/` (the tables of STORE-1 and STORE-2, in
  the file of CONF-1) and `adapters/memory/` (for tests and tools).
- One function builds the player-state payload, for the save and for the
  snapshot. It matches `player-state.schema.json`.
- New keyword arguments of `InMemoryGame`: `saves`, `accounts`. With no
  argument, `InMemoryGame()` builds the SQLite adapters on the file of
  CONF-1 and loads the saves and the accounts, as today (ENTRY-1,
  ENTRY-2, SAVE-2).
- Does not change: the tables, their columns, the payload, the path in the
  save answer, the password digest (STORE-3), the moment of each write.

## Rules

- Added: ARCH-4
- Modified: none
- Removed: none
- Renamed: none

## Impact

No outside caller sees this change: no split into expand and contract is
needed. The database file is a boundary with stored data (section "Data
at rest"). Its shape does not change.

| Part | Pace layer | Blast radius | Review needed |
| --- | --- | --- | --- |
| `application/ports_out.py`, `SaveStore`, `AccountStore` | Slow (the ports, the data model) | Every stored save and account | Yes |
| `adapters/sqlite/` | Slow (the data at rest) | Every stored save and account; the support laptop | Yes |
| `adapters/memory/` | Fast | Tests and tools only | No |

## Decision record

0014 (proposed), whose Change field names this change.
