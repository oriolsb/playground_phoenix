# 0013 — The clock, randomness and the high-score file sit behind outbound ports

- **Status:** accepted
- **Replaces:** 0008.
- **Date:** 2026-11-26
- **Need:** operational. The Evaluation needs to control the time and the
  chance without patching the standard library. Decision 0008 says: "Day 3
  can replace these seams with real ports, in a change with its own record."
- **Traces to:** `ARCH-3`, `MOVE-6`, `MOVE-8`, `PLAYER-1`, `WIN-3`, `CONF-2`, `ENTRY-1`, `ENTRY-2`.
- **Change:** hexagon-2-outbound-ports
- **Evidence (legacy code only):**
  - `game.py:316-319`: `market_is_cleaning()` calls `datetime.now()`.
  - `game.py:480-488`: `new_sid()` calls `random.randint()`.
  - `game.py:646-654`: the rat calls `random.random()` and `random.choice()`.
  - `game.py:326-337`: `save_high_score()` opens the file and calls
    `datetime.now(timezone.utc)`.
  - `game.py:364-365`: `now_iso()`, for the chat and the saves.
  - `tests/conftest.py:119-172`: the tests patch `datetime` through
    `time_machine` and `random.random` through `monkeypatch`.

## Context

The rules call the standard library for the time, the chance and one
file. Decision 0008 made these calls seams of the boundary, so the tests
could control them with no edit of the code. That works, but it ties every
test fake to the standard library: a regeneration that uses `secrets` or
binds `from random import random` at import escapes the fakes, and the
clock and rat tests then pass by luck (0008, Consequences).

## Decision

Three outbound ports, in `brown_field/application/ports_out.py`:

```python
class Clock(Protocol):
    def now(self) -> datetime: ...              # local, aware

class RandomSource(Protocol):
    def chance(self) -> float: ...              # in [0, 1)
    def choice(self, items: Sequence[T]) -> T: ...
    def digits(self, count: int) -> str: ...    # for the sid parts

class HighScoreSink(Protocol):
    def append(self, name: str, score: int, at: datetime) -> None: ...
```

In Java terms: `java.time.Clock`, a small `RandomGenerator` facade, and a
one-method writer interface.

The default adapters call the standard library **at the moment of each
call, through the module**: `datetime.now()`, `random.random()`,
`random.choice()`, `random.randint()`. They never bind a function at
import. So every seam of 0008 still works, and the tests of today pass with
no edit. The high-score adapter keeps the path rule of CONF-2 and the line
of WIN-3 (decision 0002).

`InMemoryGame` takes `clock`, `random_source` and `high_scores` as keyword
arguments, each with its default adapter.

This record restates every seam of 0008, so it can replace it:

- `brown_field.api.create_app(game=None)` and `brown_field.api.app`;
- the default clock adapter reads `datetime.now()`, so `time_machine`
  controls it;
- the default random adapter calls the module `random`, so a test can
  force or stop the rat by patching `random.random`;
- the two files are named by `KATACOMBS_DB` and `KATACOMBS_HIGHSCORES`;
- the port tier: `InMemoryGame`, the `*UseCase` classes with `execute`, and
  the error types, all in `brown_field.game`;
- **new:** the keyword arguments `clock`, `random_source` and `high_scores`
  of `InMemoryGame`.

## Alternatives rejected

| Alternative | Why you rejected it |
| --- | --- |
| Keep the stdlib seams of 0008, with no port | Works today. Every fake stays a patch of a global, and a regeneration that draws chance another way escapes it silently. |
| Default adapters that bind at import (`from random import random`) | The import binds the function before the test patches the module, so every rat test of today breaks. |
| One `Environment` port for the clock, chance and files | Fewer names. A test that fakes only the clock must then fake the files too, and the high-score file has an outside reader (decision 0002) with a slower pace than the clock. |
| Move the time stamps of the chat and the saves to the clock port in a later stage | They are the same call as the market rule. Two clocks in one game, one faked and one real, would give a test a chat line from another hour. |

## Consequences

**Easier:** a port test builds `InMemoryGame(clock=FixedClock(minute=55))`
and checks MOVE-6 with no `time_machine`. A test forces the rat with
`FixedChance(0.0)`.

**More difficult:** three more names in the port tier. The harness tests
of 0008 now test the default adapters, not the rules.

**Risks that stay:** a test that builds a game with a fake clock and then
uses `time_machine` gets the fake: the explicit port wins. The harness
documents it.

## Fitness functions

| Function | Target | How to run it | Need that it protects |
| --- | --- | --- | --- |
| No clock, chance or `open` outside the adapters | zero hits | `uv run pytest brown_field/tests/fitness -m ARCH-3` (to write) | Every fake goes through a port |
| The harness tests still reach the clock and the rat | pass | `uv run pytest brown_field/tests/harness` | The seams of 0008 |
| A fixed clock and a fixed chance drive MOVE-6 and MOVE-8 at the port | pass | `uv run pytest -m "MOVE-6 or MOVE-8"` (scenarios to add) | The ports are real seams |
| The golden high-score file | pass | `uv run pytest -m WIN-3` | The marketing job (decision 0002) |
