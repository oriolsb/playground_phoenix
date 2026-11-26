# Proposal — hexagon-7-domain-types

Structure adapted from the OpenSpec proposal template (MIT).

Stage 7. Finding F4 of the hexagonal review
(`brown_field/spec/reviews/hexagonal-review-2026-11-26.md`).
The domain becomes the innermost ring (decision 0018). It needs stages 1 to 6
archived first, because it revises ARCH-1.

## Need

- Who: the team that regenerates the domain or the ports; any reader of `kata.py`.
- Why: `domain/world.py:5`, `domain/player.py:9` and `domain/constants.py:7`
  import `Item` and `Direction` from `kata.py`, the module of the inbound
  ports. So the domain depends on the API module, and a change of the
  public API can break a game rule. ARCH-1 allows this today, because its
  layer order puts `kata.py` inside the domain.
- Kind: operational
- Measurable as: ARCH-7 (zero imports of `kata` under `domain/`). Source: decision 0018.

## What changes

- `Item`, `Action` and `Direction` move to `domain/` (for example
  `domain/types.py`). `kata.py` re-exports them, so
  `from brown_field.kata import Item, Direction` keeps working.
- The domain errors are re-exported by `kata.py` too, for the REST adapter
  of stage 8 (decision 0019).
- `kata.py` keeps the port contracts and the view models: `Player`, `Bag`,
  `Location`, `ChatLine`, `FinishedGame`, `AccountView`.
- The layer order of ARCH-1 becomes domain < ports (`kata.py`) <
  application < adapters < root.
- Does not change: any name, route, response or rule.

## Rules

- Added: ARCH-7
- Modified: none in the specification. ARCH-1 (open in `hexagon-1-guards`)
  is revised under "Other changes".
- Removed: none
- Renamed: none

## Impact

No outside caller sees this change: no split into expand and contract is
needed. Every public name of `kata.py` stays importable.

| Part | Pace layer | Blast radius | Review needed |
| --- | --- | --- | --- |
| `domain/` types | Medium (the game rules) | Every module that uses an item or a direction | Yes |
| `kata.py` | Slow (the ports) | Every adapter, every regeneration | Yes |
| `tests/fitness/test_structure.py` | Medium | The test suite | Yes, with the suite |

## Decision record

0018 (proposed), whose Change field names this change.
