# 0012 — The game-server moves to ports and adapters behind the frozen boundary

- **Status:** accepted
- **Date:** 2026-11-26
- **Need:** operational. Day 3 changes the structure of the system
  (`README.md`, "Today, you recover the knowledge of the system. On day 3,
  you change the structure"). The team that regenerates a unit needs each
  unit to be small, with its dependencies named.
- **Traces to:** `ARCH-1`, `ARCH-2`, `ENTRY-1`, `ENTRY-2`.
- **Change:** hexagon-1-guards
- **Evidence (legacy code only):**
  - `kata.py:60-97`: ten inbound ports as `Protocol`s, with no
    implementation and no I/O. The one clean layer.
  - `game.py:406-538`: `InMemoryGame` holds the players, the world state,
    the accounts, the chat and the leaderboard, and its constructor opens
    SQLite (`game.py:419-420`).
  - `game.py:316-404`: the clock, randomness, the high-score file, SQLite
    and the password digest, called from the use cases directly.
  - `api.py:139-197`, `api.py:209-214`: chat, the leaderboard, the legacy
    pickup and the energy gate live in the routes.
  - `.phoenix/assessment/game-server.md`: `game.py` is a hybrid component.

## Context

The code has the shape of ports and adapters at its edge only. The inbound
ports exist. Behind them, one module mixes the rules, the state, the
storage and the outside world, and the REST module holds rules of its own.

Three constraints shape the target:

1. **The frozen boundary** (README step 4, decision 0008). Every name
   stays: `create_app(game=None)`, `app`, `InMemoryGame`, the twelve
   `*UseCase(game)` classes, the error types, every route, every name of
   `kata.py`. A use case takes the game as its **only** argument.
2. **The seams of the tests** (decision 0008). The tests fake the clock
   with `time_machine` and the rat with `monkeypatch.setattr(random, ...)`
   (`tests/conftest.py:119-172`).
3. **No behavior changes.** The REST API, the stored formats and every
   rule stay. The one contested move (MOVE-5) has its own record (0011).

## Decision

The game-server takes four layers, from the inside out. Each layer imports
only `kata.py`, its own layer and the layers inside it (ARCH-1).

| Layer | Path | Holds | Java analogy |
| --- | --- | --- | --- |
| Domain | `brown_field/domain/` | The rules as objects with behavior. No I/O. | `domain` package, rich entities |
| Application | `brown_field/application/` | The use cases, and the outbound ports in `ports_out.py` | `@Service` classes and their `interface`s |
| Adapters | `brown_field/adapters/{rest,sqlite,files,system,memory}/` | FastAPI, SQLite, the high-score file, the clock and chance, memory stores | `adapter.in.web`, `adapter.out.persistence` |
| Composition root | `game.py`, `api.py`, `__main__.py` | `InMemoryGame`, `create_app`, `app`, and re-exports of every frozen name | `@Configuration` and `main` |

**`InMemoryGame` is the context object.** It takes one keyword argument per
outbound port, each with a default adapter:
`InMemoryGame(clock=..., random_source=..., high_scores=..., saves=..., accounts=..., world=...)`.
A use case keeps the signature `XUseCase(game)` and reads its ports from
the game, for example `game.clock`. `InMemoryGame()` with no argument
behaves as today.

**`kata.py` may grow, and never shrinks.** New ports and public types are
added after the existing ones. No name is renamed or removed.

**Each use case satisfies its port, and a type checker proves it** (ARCH-2).

**The work goes in six changes, in the order of risk.** Each change has its
own proposal, delta, record, evaluation and regeneration:

| Order | Change | Record |
| --- | --- | --- |
| 1 | `hexagon-1-guards`: the fitness functions of the structure | 0012 |
| 2 | `hexagon-2-outbound-ports`: the clock, randomness, the high-score file | 0013 |
| 3 | `hexagon-3-storage`: saves and accounts | 0014 |
| 4 | `hexagon-4-inbound-ports`: chat, leaderboard, accounts, legacy pickup | 0015 |
| 5 | `hexagon-5-world-data`: the world from `world.json` | 0016 |
| 6 | `hexagon-6-domain-model`: the rules move into the domain | 0017 |

The energy gate (MOVE-5) is outside this plan. It moves only if the group
accepts decision 0011.

## Alternatives rejected

| Alternative | Why you rejected it |
| --- | --- |
| Use cases take their ports in the constructor, `MoveUseCase(players, world, clock)` | The purest form. It breaks the frozen boundary: the port tests and the step 7 regeneration build `XUseCase(game)`. It needs a record that replaces 0008 and a rewrite of the port tests, for no change a caller sees. |
| Two constructors per use case: `XUseCase(game)` and one with explicit ports | Keeps the boundary and allows pure injection. It doubles the ways to build each of sixteen use cases, and each way needs its own tests. The context object gives the same testability with one way. |
| Split by feature (gameplay, accounts, chat), not by layer | Each feature would still mix rules and I/O inside it. The shared player state (accounts restore it, chat adds to its move count) crosses every feature, so the slices would import each other. Layers first; a later record can slice the application layer by feature. |
| Keep the structure, and add only tests | The suite already pins the behavior (decision 0010). It does not make a unit smaller or name its dependencies, so a regeneration of `game.py` stays a regeneration of everything. |
| One regeneration of `game.py` and `api.py` in the new shape | One change of everything at once. The step 7 rewrite shows the risk: it moved the energy gate without a decision. Six small changes each fail alone. |

## Consequences

**Easier:** a test builds a game with memory stores, a fixed clock and a
fixed chance, and no file or patch. A new adapter (a CLI, a socket) reuses
every rule. Each stage regenerates one layer, with a smaller prompt.

**More difficult:** the code has more modules. `InMemoryGame` is a service
locator: a use case can read any port from it, not only the ones it needs.
The type checker and the import rule are new tools in the dev setup.

**Risks that stay:** concurrent requests share dictionaries with no lock.
This record does not change that. The context object can grow into a new
god object. Decision 0017 limits it to building and holding the adapters.

## Fitness functions

None of these exist yet. `/phoenix-kit:evaluate` writes them for the
change `hexagon-1-guards`.

| Function | Target | How to run it | Need that it protects |
| --- | --- | --- | --- |
| The import rule: no import points outward; no I/O name in the domain or the application | zero violations | `uv run pytest brown_field/tests/fitness -m ARCH-1` (to write) | Each layer regenerates alone |
| The port check: each use case is accepted where its port is expected | zero type errors | `uv run pyright brown_field/tests/fitness/ports_check.py` (to write) | The ports stay the contract |
| The whole suite, unchanged, after each stage | pass | `uv run pytest brown_field/tests` | No behavior changes |
| The mutation harness kills the same mutants after each stage | the same score | `uv run python brown_field/tests/fitness/mutation/run_mutants.py` | The Evaluation stays sharp (decision 0010) |
