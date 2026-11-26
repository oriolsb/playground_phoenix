# Proposal — hexagon-1-guards

Structure adapted from the OpenSpec proposal template (MIT).

Stage 1 of 6 of the move to ports and adapters (decision 0012). It adds
the checks that protect the structure, before any code moves.

## Need

- Who: the team that restructures the game-server on day 3, and every
  later regeneration of a unit.
- Why: today nothing stops a use case from opening SQLite or a route from
  changing state. The assessment calls `game.py` a hybrid component
  (`.phoenix/assessment/game-server.md`). A rule of structure that no test
  checks erodes at the first regeneration. The guards come first, so they
  catch each later stage.
- Kind: operational
- Measurable as: ARCH-1 (zero forbidden imports), ARCH-2 (zero type
  errors between each use case and its port). Source: decision 0012.

## What changes

- New: a "Structure" section in the Specification, with ARCH-1 and ARCH-2.
- New: Terms rows for Port, Inbound port, Outbound port, Adapter, Domain
  model and Composition root.
- New: two fitness functions in `brown_field/tests/fitness/`. They are
  written by `/phoenix-kit:evaluate`, not by this proposal.
- Does not change: any route, response, error, file format or behavior.
  The code of today already passes ARCH-1, because the layers it names do
  not exist yet. ARCH-2 needs the type checker in the dev dependencies.

## Rules

- Added: ARCH-1, ARCH-2
- Modified: none
- Removed: none
- Renamed: none

## Impact

No outside caller sees this change: no split into expand and contract is
needed.

| Part | Pace layer | Blast radius | Review needed |
| --- | --- | --- | --- |
| Specification, section Structure | Slow (the ports, the boundary) | The team, every later regeneration | Yes |
| `brown_field/tests/fitness/` | Medium | The test suite only | Yes, with the suite |
| `pyproject.toml`, dev dependencies | Fast | Developers only | No |

## Decision record

0012 (proposed), whose Change field names this change.
