# 0020 — The game state holds no rules and no view mapping

- **Status:** accepted
- **Date:** 2026-11-26
- **Need:** operational. Each job of the context object gets one home, so it
  does not grow into a new god object (finding F3 of the hexagonal review;
  decision 0012, "Risks that stay").
- **Traces to:** `ARCH-9`, `MOVE-6`, `STORE-3`.
- **Change:** hexagon-10-slim-state
- **Evidence (legacy code only):**
  - `application/state.py:37-48`: `market_is_cleaning` and `password_hash`.
  - `application/state.py:84-197`: `GameState` holds the ports, the
    aggregates, the lookups and the mappers `to_player`, `to_bag`, `to_location`.

## Context

Decision 0012 made `GameState` the context object, so that `XUseCase(game)`
stays frozen. It now holds four jobs. The group chose to move the rules and
the mapping out, and to keep 0012.

## Decision

- `market_is_cleaning` becomes a domain function that takes the minute as a
  value. `MoveUseCase` reads `game.clock` and passes the minute.
- `password_hash` moves to `domain/accounts.py`, byte for byte (STORE-3).
- `to_player`, `to_bag`, `to_location` move to `application/views.py`.
- `GameState` keeps the outbound ports, the aggregates and their lookups.
- Every use case keeps `XUseCase(game)` (decision 0012).

## Alternatives rejected

| Alternative | Why you rejected it |
| --- | --- |
| Give each use case only the ports it needs | It shows each dependency, but it replaces decision 0012 and needs a second constructor path to keep `XUseCase(game)` (decision 0008). The group deferred it. |
| Keep `market_is_cleaning(clock)` in the application | It is a rule of MOVE-6. A domain function on a minute can be tested with no clock. |
| Put the view mapping in the REST adapter | The ports answer view models (`Player`, `Bag`), so the mapping is the application's job. The adapter maps view models to JSON. |

## Consequences

**Easier:** `state.py` is a holder and a store. MOVE-6 is a pure function.

**More difficult:** one more module in the application.

**Risks that stay:** `GameState` is still a service locator. A later record
can replace 0012.

## Fitness functions

| Function | Target | How to run it | Need that it protects |
| --- | --- | --- | --- |
| No rule and no `to_*` in `state.py` | zero hits | `uv run pytest brown_field/tests/fitness -m ARCH-9` (to write) | One home per job |
| MOVE-6 at minutes 49, 50, 59, with no clock | pass | `uv run pytest brown_field/tests/domain` (to add) | The market rule |
| The golden digest | pass | `uv run pytest -m STORE-3` | Every stored account |
