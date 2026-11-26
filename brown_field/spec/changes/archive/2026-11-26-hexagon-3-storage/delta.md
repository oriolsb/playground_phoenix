# Delta — hexagon-3-storage

Format adapted from the OpenSpec delta spec (MIT). On archive, the delta
merges into the specification and this file moves to the archive.

## ADDED Rules

#### ARCH-4 — Saves and accounts are stored through storage ports

- Status: accepted (decision 0014).
- Source: this change, and decision 0014.
- Rule: Katacombs shall read and write the saves only through the port
  `SaveStore`, and the accounts only through the port `AccountStore`.
  Where `InMemoryGame` gets no store, Katacombs shall use the SQLite
  adapters on the database file of CONF-1, and shall load the saves and
  the accounts when the game is built.
- Why: the rules of saving, logging in and quitting must not depend on
  SQLite. A test or a tool can then build a game with no file. The default
  keeps the start of today, so a restart still brings the players back
  (SAVE-2) and `brown_field.api.app` still reads the file once (ENTRY-2).
- Observable result: (1) a fitness function finds `sqlite3` imported only
  under `brown_field/adapters/sqlite/`. (2) A game built with memory
  stores, in an empty working directory with `KATACOMBS_DB` unset,
  registers, saves, logs in and quits a player, and no file appears.
  (3) The tests of STORE-1, STORE-2, SAVE-2 and the old save without
  energy (`tests/golden/old-save-without-energy.db`) pass unchanged.

## Other changes to the specification

### Data ownership: the rows "Saves" and "Accounts with snapshots"

| Saves (SQLite table `saves` in the file `KATACOMBS_DB`) | game-server (save), through the port `SaveStore` | game-server (start), through the port `SaveStore` |
| Accounts with snapshots (SQLite table `accounts` in `KATACOMBS_DB`) | game-server (register, login, quit), through the port `AccountStore` | game-server (start, login), through the port `AccountStore` |

## Unchanged

- `STORE-1`: the table `saves` keeps its four text columns.
- `STORE-2`: the table `accounts` keeps its five text columns.
- `STORE-3`: the password digest keeps its format. It stays contested.
- `CONF-1`: the database file keeps its variable and its default.
- `SAVE-1`: the save answer still names the path of the database file.
- `SAVE-2`: a restart brings saved players back, but not the world.
- `ACCOUNT-4`: a login restores the snapshot, or resumes, or starts a player.
- `ACCOUNT-6`: a quit with an account writes the snapshot.
- `ENTRY-1`: `create_app()` with no game still reads the files at its start.
- `ENTRY-2`: `brown_field.api.app` still reads the database file once, at the import.
