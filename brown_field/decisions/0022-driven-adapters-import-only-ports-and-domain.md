# 0022 — Driven adapters import only the outbound ports and the domain

- **Status:** proposed
- **Date:** 2026-11-26
- **Need:** operational. A driven adapter must not depend on the driving
  side, so each side can be regenerated alone (finding G2 of the stage 11
  hexagonal review).
- **Traces to:** `ARCH-10`.
- **Change:** hexagon-12-driven-adapter-imports
- **Evidence (legacy code only):**
  - `adapters/files/world_json.py:11`: `from ...kata import Action, Direction, Item`.
  - `adapters/sqlite/stores.py`, `adapters/memory/stores.py`,
    `adapters/files/high_scores.py`, `adapters/system/*.py`: they import
    from `brown_field` only `application.ports_out`, or nothing.

## Context

ARCH-1 lets an adapter import every layer inside it, the ports of
`kata.py` and the application included. That fits the REST adapter, which
drives the game through the inbound ports (ARCH-8). It is too loose for a
driven adapter: in Java terms, a JDBC repository that imports the REST
controller's interfaces. Since decision 0018, the types such an adapter
needs live in `domain/`, so the loose import has no reason left.

## Decision

A driven adapter, every module under `adapters/` outside `adapters/rest/`,
imports from `brown_field` only `application.ports_out` and `domain/`
(ARCH-10). `world_json.py` takes `Action`, `Direction` and `Item` from
`domain/types.py`. A fitness function with a planted break checks the rule.

## Alternatives rejected

| Alternative | Why you rejected it |
| --- | --- |
| Forbid only `kata` in driven adapters (the review's minimal criterion) | A driven adapter could still import the use cases or `GameState`. The strict rule costs no more, and every driven adapter already complies once `world_json.py` is fixed. |
| Leave it: the re-exports are the same objects | Nothing breaks today, but nothing stops the next such import either. |
| Move `kata.py` under `application/`, next to `ports_out.py` (review, open question 3) | The import path `brown_field.kata` is frozen (decision 0008). A move needs a shim and a record of its own, for no change in behavior. |

## Consequences

**Easier:** each driven adapter depends on its port and the domain types
only; the driving side can change without touching storage or files.

**More difficult:** a new driven adapter that needs a view model must get
it through a port record in `ports_out.py`, not from `kata.py`.

**Risks that stay:** none known.

## Fitness functions

| Function | Target | How to run it | Need that it protects |
| --- | --- | --- | --- |
| Driven adapters import only `application.ports_out` and `domain/` | zero hits | `uv run pytest brown_field/tests/fitness -m ARCH-10` (to write) | Each side regenerates alone |
| A planted import from `kata` fails the check | pass | `uv run pytest brown_field/tests/fitness/test_structure.py` (to write) | The check can fail |
