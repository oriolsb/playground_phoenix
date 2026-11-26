# 0008 — The seams that the tests use become part of the boundary

- **Status:** replaced by 0013
- **Date:** 2026-11-25
- **Need:** operational. The Evaluation, and the regeneration of step 7.
- **Traces to:** `ENTRY-1`, `ENTRY-2`, `MOVE-6`, `MOVE-8`.
- **Change:** None.
- **Evidence (legacy code only):** no code was edited for a seam. The tests
  use places that exist: `create_app(game)` (`api.py:101-102`); the module
  attribute `app` (`api.py:220`); the stdlib calls `datetime.now()`
  (`game.py:319`) and `random.random()`, `random.choice()` and
  `random.randint()` (`game.py:483-485`, `game.py:647-650`); the files of
  `KATACOMBS_DB` and `KATACOMBS_HIGHSCORES`; and the use cases built as
  `XUseCase(InMemoryGame())` (`tests/ports/`).

## Context

The README of the exercise says: "Record each seam in a decision record. A
seam becomes part of the frozen boundary. The regenerated code in step 7
must keep it." Michael Feathers: "A seam is a place where you can alter
behavior in your program without editing in that place."

## Decision

A regenerated server keeps these seams:

- `brown_field.api.create_app(game=None)` and `brown_field.api.app`;
- the market rule reads the wall clock through the standard library
  (`datetime.now()`), so `time-machine` controls it;
- the rat and the sids draw from the standard `random` module, so a test
  can force or stop the rat by patching `random.random`;
- the two files are named by the two environment variables;
- the port tier: `InMemoryGame`, the 12 `*UseCase` classes with
  `execute`, and the error types `KatacombsError`, `PlayerNotFound`,
  `ItemNotFound`, `InvalidName`, `NotAllowed`, all in `brown_field.game`.

## Alternatives rejected

| Alternative | Why you rejected it |
| --- | --- |
| Edit the code for a Clock and a Random port | The exercise changes no behavior on day 2; the stdlib seams work without an edit. |
| Leave the port tier out of the boundary | Then a correct rewrite breaks 17 port tests that are oracles today. |

## Consequences

A rewrite that uses its own random generator, `secrets`, or an injected
clock silently escapes the fakes: the clock and rat tests then fail, or
pass by luck. Day 3 can replace these seams with real ports, in a change
with its own record.

## Fitness functions

| Function | Target | How to run it | Need that it protects |
| --- | --- | --- | --- |
| The harness tests reach the clock and the rat | pass | `uv run pytest brown_field/tests/harness` | The control of the tests |
| The port tier | pass | `uv run pytest brown_field/tests -m port` | The step 7 regeneration |
