# Delta — modular-core

Format adapted from the OpenSpec delta spec (MIT). Each section is
optional. Rules use the format of the specification. On archive, the
delta merges into the specification and this file moves to the archive.

## ADDED Rules

#### OPS-2 — The game rules do no I/O

- Source: change modular-core; the need of Product, 2026-11-26: a modular
  core that new features can extend without touching the existing rules.
- Rule: Katacombs shall keep its game rules and use cases in core modules
  that reach the database file, the high-score file, the clock, the
  random numbers and the password hash only through outbound ports.
- Why: a new feature, a new store or a test can then replace one of these
  without editing a rule, and a second adapter can reuse the rules as
  they are.
- Observable result: a fitness function reads the source of the core
  modules. Each of the 12 `*UseCase` classes of the port tier is defined
  in a core module, so the check cannot pass on an empty core. No core
  module imports `sqlite3`, `os`, `random`, `hashlib`, `json`, `fastapi`,
  `pydantic` or `starlette`, and none calls `open(` or `.now(`. Today it
  fails: the rules live in `game.py`, which imports `sqlite3`, `os`,
  `random`, `hashlib` and `json`.

#### OPS-3 — The REST adapter holds no game rule

- Source: change modular-core; the need of Product, 2026-11-26.
- Rule: When a client sends a request, the REST adapter of Katacombs shall
  answer it through the use cases, and read no game state of its own.
- Why: a rule that lives in one adapter is lost when a second adapter
  appears; decision 0011 shows it for the energy gate.
- Observable result: a fitness function reads the source of `api.py`. It
  finds no read or write of the game state (`game.<attribute>`), and each
  route calls at least one use case. Today it fails: `api.py` reads `game.players`,
  `game.places`, `game.chat` and `game.finished_games`, and holds the
  energy gate (`MOVE-5`), the chat (`CHAT-1` to `CHAT-3`) and the legacy
  pickup (`LEGACY-1`).

## MODIFIED Rules

#### MOVE-5 — A player with no energy can't move

- Status: accepted (decision 0011). Kept on purpose, in the move port, at 0.
- Source: legacy code (api.py:210-213, "Added for the mobile release"), revised by change modular-core.
- Rule: If a player with an energy of 0 or less moves, then Katacombs shall
  refuse the move.
- Why: A guess: energy is the cost of moving; food and drink restore it.
- Observable result: over REST, status 405, error reason `NOT_ALLOWED`,
  message `YOU ARE TOO TIRED TO MOVE. EAT OR DRINK SOMETHING.` Through the
  move port, the error `NotAllowed` with the same message. This check comes
  before every other move check, the win included.
- Revised: 2026-11-26. The gate moves from the REST route into the move port, at energy 0; over REST nothing changes (decision 0011).

## Other changes to the specification

### Scope

Scope: the game-server unit: `brown_field/kata.py`, `api.py`, `game.py`,
and the core and adapter modules that change modular-core adds. The web
client has its own specification in `brown_field/web/spec/`.

## Unchanged

Every rule keeps its behavior. These are the ones next to the change,
because their code moves or a seam they use must hold:

- `MOVE-6`: the market reads the local wall clock, now through the clock port.
- `MOVE-8`: the rat draws from `random`, now through the random port.
- `PLAYER-1`: the sids draw from `random`, in the same order.
- `WIN-3`: the high-score line keeps its format, now behind the high-score port.
- `BOARD-1`: the leaderboard moves out of `api.py`, with the same order.
- `SAVE-1`: the save answer keeps the path.
- `SAVE-2`: a restart restores the saved players, and not the world.
- `ACCOUNT-1`: registering moves out of `game.py`, unchanged.
- `ACCOUNT-2`: the email check stays as it is.
- `ACCOUNT-3`: one account per email.
- `ACCOUNT-4`: a login restores the profile as today.
- `ACCOUNT-5`: a wrong email or password is refused as today.
- `ACCOUNT-6`: a quit with an account keeps its snapshot, now through the account port.
- `CHAT-1`: sending moves out of `api.py`, unchanged.
- `CHAT-2`: a player reads only the messages of the location.
- `CHAT-3`: a chat line still counts as a move.
- `API-1`: a malformed request is refused as today.
- `API-2`: each error keeps its status and message.
- `STORE-1`: the saves table keeps its columns.
- `STORE-2`: the accounts table keeps its columns.
- `STORE-3`: the password stays an unsalted digest; the hash moves behind a port, unchanged.
- `CONF-1`: `KATACOMBS_DB` names the database file, read at each call.
- `CONF-2`: `KATACOMBS_HIGHSCORES` names the high-score file.
- `CONF-3`: the server listens where it does today.
- `ENTRY-1`: `create_app` serves the game it is given.
- `ENTRY-2`: `brown_field.api.app` stays.
- `OPS-1`: each command stays under 100 ms at p99.
- `LEGACY-1`: the pickup moves out of `api.py`, still with no checks.
- `LEGACY-2`: a pickup of an item elsewhere still changes nothing.
