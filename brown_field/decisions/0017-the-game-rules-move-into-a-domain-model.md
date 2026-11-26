# 0017 — The game rules move into a domain model

- **Status:** proposed
- **Date:** 2026-11-26
- **Need:** operational. The next person who changes a game rule changes
  one object of the domain, not a use case with its ports and its mapping.
- **Traces to:** `ARCH-1`.
- **Change:** hexagon-6-domain-model
- **Evidence (legacy code only):**
  - `game.py:95-117`: `Place` and `PlayerState` hold data and no behavior.
  - `game.py:406-417`: `InMemoryGame` holds the players, the world state,
    the open and locked items, the accounts, the chat and the leaderboard.
  - `game.py:616-655`: `MoveUseCase` does the move, the rat, the win and
    the high-score line in one method.
  - `game.py:656-735`: `UseItemUseCase.execute`, 80 lines, five branches
    on the action.
  - `game.py:545-549`, `game.py:784-788`: the name rules are written twice,
    for players and for accounts.

## Context

After stages 1 to 5, each use case reaches the outside only through ports.
The rules themselves still sit in the use cases, as procedures over plain
data. This is a transaction script. It works, and the suite pins it. But a
rule has no home of its own: the slot rule, the energy, the first-visit
gold and the win are spread over several methods.

## Decision

The rules move into `brown_field/domain/`, as objects with behavior:

| Module | Holds | Rules |
| --- | --- | --- |
| `domain/player.py` | The player: location, energy, move count, visits, opened items, win | MOVE-1..5, MOVE-7, GOLD-1, GOLD-2, WIN-1, ACT-3, ACT-15, ACT-17 |
| `domain/bag.py` | The bag: items, gold, the slot rule, the score | BAG-2, BAG-3, ACT-4..7 |
| `domain/world.py` | Locations, exits, the slide, open and locked items, the manhole | WORLD-2, ACT-8..14 |
| `domain/names.py` | The name rules, used by players and accounts | PLAYER-2..4, ACCOUNT-2 |
| `domain/errors.py` | `KatacombsError` and its subclasses | API-2 |

Each use case loads what it needs through the ports, calls the domain, and
writes back through the ports. It holds no game rule. The order of the
checks of each command stays as it is, because the messages depend on it.

`InMemoryGame` keeps its name, its keyword arguments and its re-exports.
It builds the adapters and holds them, and holds nothing else.
`game.py` re-exports the error types and every use case, so
`from brown_field.game import NotAllowed` still works.

## Alternatives rejected

| Alternative | Why you rejected it |
| --- | --- |
| Stop after stage 5, keep the transaction script | Stages 1 to 5 give most of the gain: ports, adapters, testability. The rules stay readable in the use cases. This is a real option. It is rejected because `UseItemUseCase` and `MoveUseCase` stay the two largest units to regenerate, and the name rules stay written twice. |
| One class per action (a strategy for TAKE, DROP, OPEN, CLOSE, USE) | Five classes for 78 lines. The rules of the actions share the location, the bag and the world. A method per action on the domain objects is smaller. |
| An event-sourced player, with commands and events | It would change the save payload (STORE-1) and the snapshot, both accepted formats. No need asks for history. |

## Consequences

**Easier:** a rule has one home. A unit test of the domain needs no port,
no fake and no game. The name rules are written once.

**More difficult:** the use cases and the domain must keep the order of
the checks of today. The mutation harness (decision 0010) is the guard: it
must kill the same mutants after the move. Its hand-written mutants name
lines of `game.py`, so they move with the code.

**Risks that stay:** the shared world state across players (ACT-8,
ACT-11) stays shared. It is a rule, not a defect of the structure.

## Fitness functions

| Function | Target | How to run it | Need that it protects |
| --- | --- | --- | --- |
| The domain imports nothing outward and no I/O name | zero violations | `uv run pytest brown_field/tests/fitness -m ARCH-1` (from stage 1) | Rules with no I/O |
| The whole suite, unchanged | pass | `uv run pytest brown_field/tests` | No behavior changes |
| The mutation harness | the same score as before stage 6 | `uv run python brown_field/tests/fitness/mutation/run_mutants.py` | The Evaluation stays sharp (decision 0010) |
| The 7 transcripts | pass | `uv run pytest brown_field/tests/fitness/test_transcripts.py` | The order of checks and the messages |
