# Proposal — hexagon-11-composition-factory

Structure adapted from the OpenSpec proposal template (MIT).

Stage 11. Finding F5 of the hexagonal review, a minor one. The default
adapters are built in one named place, and the name `InMemoryGame` is
documented for what it is (decision 0021).

## Need

- Who: a reader of the composition root.
- Why: `InMemoryGame` extends `GameState` only to supply default adapters
  (`game.py:73-95`). Its defaults are SQLite and files, not memory, so the
  name misleads. The name is frozen (decision 0008), so it can't change.
- Kind: operational
- Measurable as: the suite passes unchanged; `InMemoryGame(...)` keeps its
  keyword signature.

## What changes

- New function in `game.py`: `default_adapters(**overrides)` answers the
  six adapters, each overridable by keyword.
- `InMemoryGame` stays a class, a subclass of `GameState`, so the tests and
  the type check that annotate `game: InMemoryGame` keep working. Its
  constructor calls `default_adapters` and its docstring says that the
  defaults are the database file and the files, not memory.
- Does not change: any name, signature or behavior.

No rule changes.

## Rules

- Added: none
- Modified: none
- Removed: none
- Renamed: none

## Impact

No outside caller sees this change: no split into expand and contract is
needed.

| Part | Pace layer | Blast radius | Review needed |
| --- | --- | --- | --- |
| `game.py` | Slow (the frozen names) | None, if the signature holds | Yes, a short one |

## Decision record

0021 (proposed), whose Change field names this change.
