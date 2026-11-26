# 0012 — The game-server becomes a hexagon, with the behavior unchanged

- **Status:** accepted
- **Date:** 2026-11-26
- **Need:** day 3. New work on accounts, chat and a subscription is coming.
  Each one needs a core that a second adapter can call, and I/O that a test
  or a new store can replace.
- **Traces to:** `ENTRY-1`, `ENTRY-2`, `MOVE-5`, `MOVE-6`, `MOVE-8`, `SAVE-1`, `STORE-1`, `CHAT-3`, `LEGACY-1`.
- **Change:** Structure only. No observable behavior changes: the same 217
  tests pass, with the same skip, and the 42 hand-written mutants are re-pointed.
- **Evidence:** the legacy code at commit `10a5221`. Every line citation in
  the specification, `archaeology.md` and records 0001–0011 refers to that
  commit, not to the new files.

## Context

Before this change, `game.py` held everything: the world, the rules, the
state, the use cases, SQLite, the high-score file, the clock, `random` and
the password hash. `api.py` held three rules of its own: the energy gate,
the whole chat, and the legacy pickup. The use cases took the concrete
`InMemoryGame` and did their own I/O, so no port could be replaced.

## Decision

| Layer | Where | What it holds |
| --- | --- | --- |
| Domain model, inbound ports | `kata.py` | The dataclasses, and one `Protocol` per use case. New: `energy` on `Player`; `Message`, `Score`, `AccountView`; ports for accounts, chat, the pickup, the leaderboard and one player. |
| Core | `core/` | `errors`, `rules`, `world`, `state` (`GameState`, the old `InMemoryGame` without I/O), and the use cases by area: `players`, `looking`, `moving`, `items`, `saving`, `accounts`, `chat`, `legacy`. |
| Outbound ports | `core/ports.py` | `SaveStore`, `AccountStore`, `HighScoreSink`, `Clock`, `RandomSource`, `PasswordHasher`, bundled in `Ports`. |
| Driven adapters | `adapters/` | `sqlite_store` (saves, accounts), `highscore_file`, `system` (clock, `random`, SHA-256). |
| Composition root | `game.py` | `default_ports()`, and `InMemoryGame(ports=None)`, which is `GameState` with the real adapters. |
| Driving adapter | `api.py` | Parses, calls one use case, writes JSON. It never reads the game state. |

**What stays as it was, on purpose:**

- **The seams of decision 0008.** `brown_field.game` still exports
  `InMemoryGame`, the 12 use cases and the 5 error types, and
  `XUseCase(InMemoryGame())` still works. The system adapters call
  `datetime.now()` and `random.random()` at each call, so time-machine and a
  patched `random` still reach them.
- **The order of the random draws**, so the recorded transcripts still match.
- **The energy gate stays in `api.py`.** Decision 0011 is proposed and not
  accepted. The route now asks `ViewPlayerUseCase` for the energy instead of
  reading `game.players`.
- **The environment variables are read at each call**, as before.
- **The scars:** unsalted SHA-256, the path in the save answer, a chat line
  counting as a move, the pickup skipping every rule of `UseItem`.

## Alternatives rejected

| Alternative | Why you rejected it |
| --- | --- |
| Inject each port into each use case | Then `XUseCase(InMemoryGame())` breaks, and with it the 17 port tests that decision 0008 freezes. The game carries its `Ports` instead. |
| Read the environment variables once, at start | A behavior change: today a test or the support laptop can change `KATACOMBS_DB` between two calls. |
| Fix the scars in the same change | A refactor and a behavior change in one diff hide each other. Each scar gets its own record. |
| Move the energy gate into `MoveUseCase` now | Decision 0011 is open for the group. |

## Consequences

- A new adapter, such as a CLI, a webhook, a WebSocket or an in-memory test
  store, needs no change to the core.
- The new features have a place: accounts and chat already have their own
  modules, and a subscription gets new outbound ports (`Entitlements` or
  `EventPublisher`, once its meaning is decided).
- The mutation harness names the new files, and `mutmut` reads `core/`,
  `adapters/` and `api.py`.
- The line citations of the specification are now history (see Evidence).

## Fitness functions

| Function | Target | How to run it | Need that it protects |
| --- | --- | --- | --- |
| The hexagon keeps its shape | pass | `uv run pytest brown_field/tests/fitness/test_architecture.py` | The core stays free of I/O; `api.py` calls only use cases |
| The behavior is unchanged | the whole suite passes, as at `10a5221` | `uv run pytest` | Every client sees no change |
| No new surviving mutant | the hand-written mutants report as in `mutants.md` | `uv run python brown_field/tests/fitness/mutation/run_mutants.py` | The tests still see each rule in its new place |
