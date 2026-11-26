# 0018 — The domain owns its types, and kata.py re-exports them

- **Status:** proposed
- **Date:** 2026-11-26
- **Need:** operational. The domain must be the innermost ring, so it can be
  regenerated without the public API (finding F4 of the hexagonal review).
- **Traces to:** `ARCH-7`, `ARCH-1`.
- **Change:** hexagon-7-domain-types
- **Evidence (legacy code only):**
  - `domain/world.py:5`, `domain/player.py:9`, `domain/constants.py:7`:
    the domain imports `Item` and `Direction` from `kata.py`.
  - `kata.py`: `Bag.energy` and `Player.energy` carry the comment "Added for
    the ports (decision 0015). The REST adapter reads it here", so the same
    module serves the domain and the REST adapter.

## Context

Decision 0012 put `kata.py` at the center of the layer order. In stage 6 the
domain became real, and it now depends on the module of the inbound ports.
A rule then breaks when the API changes. The names of `kata.py` are frozen
(decision 0008), so none of them can leave it.

## Decision

`Item`, `Action` and `Direction` move to `brown_field/domain/`. `kata.py`
re-exports them, and the domain error types, under the same names: in Java
terms, the domain package owns the types and the API package re-exports
them. `kata.py` keeps the port contracts and the view models (`Player`,
`Bag`, `Location`, `ChatLine`, `FinishedGame`, `AccountView`).

The layer order becomes domain < ports (`kata.py`) < application <
adapters < root (ARCH-1, revised). ARCH-7 forbids any import from the
domain to a module outside it.

## Alternatives rejected

| Alternative | Why you rejected it |
| --- | --- |
| Keep the domain on `kata.py`, as ARCH-1 allows today | The domain stays tied to the API module, and a view-model field added for an adapter (`energy`) is a domain change. |
| Two sets of types: domain types and view types, with a mapping | `Item` and `Direction` mean the same thing in both places. A mapping for identical shapes adds code and no protection. The view models that differ (`Player`, `Bag`) stay in `kata.py`. |
| Move every type of `kata.py` to the domain | `Player` and `Bag` are views: they carry `energy` and `score` for callers. They belong to the ports. |

## Consequences

**Easier:** the domain has no outside dependency; a regeneration of the
ports can't break a rule.

**More difficult:** `kata.py` now imports the domain. The re-exports must
stay the same objects, or `isinstance` checks break.

**Risks that stay:** a re-export that is forgotten breaks a frozen name; the
fitness function checks it.

## Fitness functions

| Function | Target | How to run it | Need that it protects |
| --- | --- | --- | --- |
| No import of `kata` under `domain/` | zero hits | `uv run pytest brown_field/tests/fitness -m ARCH-7` (to write) | The domain regenerates alone |
| The frozen names of `kata.py` import, and are the domain objects | pass | `uv run pytest -m ARCH-7` (to write) | Decision 0008 |
| ARCH-1 with five layers | zero violations | `uv run pytest brown_field/tests/fitness/test_structure.py` | Decision 0012 |
