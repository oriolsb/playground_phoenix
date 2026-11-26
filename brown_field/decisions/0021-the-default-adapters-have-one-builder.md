# 0021 — The default adapters have one builder

- **Status:** proposed
- **Date:** 2026-11-26
- **Need:** not applicable to a caller. A reader of the composition root
  must see where the defaults come from (finding F5 of the hexagonal review).
- **Traces to:** `ENTRY-1`.
- **Change:** hexagon-11-composition-factory
- **Evidence (legacy code only):**
  - `game.py:73-95`: `InMemoryGame` extends `GameState` only to pass default
    adapters; the defaults are SQLite and files, not memory.

## Context

The name `InMemoryGame` is frozen (decision 0008), and tests and the type
check use it as a type. It can't become a function or change its name.

## Decision

A function `default_adapters(**overrides)` in `game.py` answers the six
default adapters. `InMemoryGame` stays a subclass of `GameState`; its
constructor calls `default_adapters` and keeps its keyword signature. Its
docstring says that the defaults are the database file and the files.

## Alternatives rejected

| Alternative | Why you rejected it |
| --- | --- |
| Make `InMemoryGame` a factory function | Tests and `ports_check.py` annotate `game: InMemoryGame`. A function is not a type. |
| Rename it to `DefaultGame` and keep an alias | A second name for one thing, and every caller keeps the old one (decision 0008). |
| Do nothing | A reasonable choice: the finding is minor. Rejected only because the builder costs a few lines and helps tools that need the defaults. |

## Consequences

**Easier:** a tool builds the defaults and overrides one adapter.

**More difficult:** nothing material.

**Risks that stay:** the name still says "in memory".

## Fitness functions

| Function | Target | How to run it | Need that it protects |
| --- | --- | --- | --- |
| The whole suite, unchanged | pass | `uv run pytest brown_field/tests` | Decision 0008 |
| The port check with `game: InMemoryGame` | zero type errors | `uv run pytest brown_field/tests/fitness/test_structure.py -k port` | ARCH-2 |
