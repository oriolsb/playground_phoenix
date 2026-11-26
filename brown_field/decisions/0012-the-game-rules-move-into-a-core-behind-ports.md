# 0012 — The game rules move into a core behind ports, and the REST adapter keeps no rule

- **Status:** proposed
- **Date:** 2026-11-26
- **Need:** business. Product, for the features that come next: more
  accounts, more chat, and a subscription of a type not known yet. Each
  one needs its own place, and the existing rules must stay as they are.
- **Traces to:** `OPS-2`, `OPS-3`, `MOVE-5`, `ENTRY-1`, `ENTRY-2`, `CONF-1`, `CONF-2`.
- **Change:** `modular-core`.
- **Evidence (legacy code only):**
  - `game.py:1-13`: the module that holds every rule imports `sqlite3`,
    `os`, `random`, `hashlib` and `json`.
  - `game.py:316-404`: the clock, the high-score file, the SQLite paths
    and schemas and the password hash are module functions, called by
    name from the use cases (`game.py:629`, `640`, `648`, `756`).
  - `game.py:406-478`: `InMemoryGame.__init__` reads the SQLite file.
  - `api.py:166-197`, `209-214`: the chat, the legacy pickup and the
    energy gate live in the routes; `api.py:122-155` read `game.players`
    and `game.finished_games` directly.

## Context

One file holds the world, the rules, the state, the use cases and all
the I/O. A new feature lands in the same two files, and no part can be
replaced: not the store, not the clock, not the random numbers. The
constraints:

- No behavior changes, except the one that decision 0011 accepts (the
  energy gate in the move port). The 216 tests that pass today, the 7
  transcripts and the contracts are the safety net.
- The seams of decision 0008 hold: `create_app`, `app`, and the port tier
  (`InMemoryGame`, the 12 use cases, the 5 errors in `brown_field.game`,
  built as `XUseCase(InMemoryGame())`); `datetime.now()` and `random` are
  called at each use, so time-machine and a patched `random` reach them.
- The environment variables are read at each call (`CONF-1`, `CONF-2`).

## Decision

The code takes this layout:

| Part | Where | Pace layer |
| --- | --- | --- |
| Domain model and inbound ports | `kata.py`: the dataclasses, and one `Protocol` per use case. `Player` gains `energy`; new ports for the accounts, the chat, the legacy pickup, the leaderboard and one player. | slow |
| Core | `core/`: errors, rules, the world, the state (`GameState`), and the use cases by area: players, looking, moving, items, saving, accounts, chat, legacy. No I/O (`OPS-2`). | medium |
| Outbound ports | `core/ports.py`: `SaveStore`, `AccountStore`, `HighScoreSink`, `Clock`, `RandomSource`, `PasswordHasher`, bundled in one `Ports` value that the state carries. | slow |
| Driven adapters | `adapters/`: SQLite (saves, accounts), the high-score file, and the system clock, `random` and SHA-256, each calling the standard library at each use. | fast |
| Composition root | `game.py`: builds the default adapters; `InMemoryGame(ports=None)` is `GameState` with them. It exports the names of decision 0008. | slow (the seam) |
| Driving adapter | `api.py`: parses, calls the use cases, writes JSON, maps the errors. No rule, no game state (`OPS-3`). | fast |

- **The energy gate** is the first check of `MoveUseCase` after the
  player is found, at energy 0 (decision 0011, `MOVE-5`).
- **The chat, the legacy pickup and the leaderboard** become use cases,
  with their quirks: a chat line counts as a move (`CHAT-3`); the pickup
  skips every take rule (`LEGACY-1`, decision 0003).
- **The order of the random draws** stays, so the transcripts match.

## Alternatives rejected

| Alternative | Why you rejected it |
| --- | --- |
| Inject each port into each use case's constructor | The cleanest for one use case, but `XUseCase(InMemoryGame())` breaks, and with it the port tier that decision 0008 freezes. The state carries one `Ports` value instead. |
| Package by feature now: `game/`, `accounts/`, `chat/`, each with its own state and adapters | The three share one state (a login creates a player, a chat line counts a move) and one SQLite file. Splitting the state is a behavior risk with no feature to need it yet. Modules by area inside one core keep the door open; the subscription can start the first separate package. |
| Move the I/O functions into an `adapters` module, and let the use cases call them by name | Fewer types, but the rules still depend on concrete I/O: no test or new store can replace one, and `OPS-2` would pass only in name. |
| Read the environment variables once, at start | A behavior change: today a test or the support laptop changes `KATACOMBS_DB` between calls (`CONF-1`). |
| Fix the scars in the same change (bcrypt, the path in the save answer) | A refactor and a behavior change in one diff hide each other. Each scar needs its own need and record. |

Design it twice was not run: the alternatives above come from a first
attempt that was dropped for its order of work, not for its design.

## Consequences

- A new adapter (a CLI, a webhook, a WebSocket, an in-memory store for a
  test) needs no edit in the core. The subscription gets its outbound port
  in `core/ports.py` once its type is known.
- A port is a slow layer: a change to `core/ports.py` or to the names of
  `game.py` needs a person's review.
- `Ports` on the state is a small service locator: a use case can reach
  every port, not only the ones it needs. Accepted for the seam; revisit
  when 0008 is replaced.
- The hand-written mutants name the code text (decision 0010). With the
  code change, each one is re-pointed to its new file, with no new
  survivor; the mutant "energy gate at -1" moves to the move use case.
- The line citations of the specification and of records 0001-0011 stay
  as evidence of the legacy code at commit `10a5221`.
- `PHOENIX.md` lists the new modules of the unit at archive.

## Fitness functions

| Function | Target | How to run it | Need that it protects |
| --- | --- | --- | --- |
| The core does no I/O (`OPS-2`, `fitness/architecture.feature`) | pass; fails today | `uv run pytest brown_field/tests -m OPS-2` | New features and tests replace an adapter without editing a rule |
| The REST adapter holds no rule (`OPS-3`, `fitness/architecture.feature`) | pass; fails today | `uv run pytest brown_field/tests -m OPS-3` | A second adapter gets every rule, the energy gate included |
| The behavior does not change | every other scenario, the 7 transcripts and the contract tests pass before and after | `uv run pytest brown_field/tests` | Mobile client v1, the web client and the marketing job see no change |
| The move port refuses a tired player (`MOVE-5`) | pass; fails today | `uv run pytest brown_field/tests -m MOVE-5` | Every adapter gets the gate (decision 0011) |
| The tree answers like the legacy code (`fitness/test_differential.py`) | 0 sessions differ from `10a5221` over REST; the control differs | `KATACOMBS_DIFFERENTIAL=1 uv run pytest brown_field/tests -m differential` | Every client sees no change, also under a local time zone and with the rat on |
| No new surviving mutant | as in `mutation/mutants.md` | `uv run python brown_field/tests/fitness/mutation/run_mutants.py` | The tests still see each rule in its new place |
