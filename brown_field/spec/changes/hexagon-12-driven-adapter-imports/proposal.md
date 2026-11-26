# Proposal — hexagon-12-driven-adapter-imports

Structure adapted from the OpenSpec proposal template (MIT).

Stage 12. Finding G2 of the stage 11 hexagonal review
(`brown_field/spec/reviews/hexagonal-review-2026-11-26-stage-11.md`). A
driven adapter depends only on the outbound ports and the domain
(decision 0022).

## Need

- Who: the team that regenerates a driven adapter or the inbound ports.
- Why: `adapters/files/world_json.py:11` imports `Action`, `Direction` and
  `Item` from `kata.py`, the contract of the driving side. They are the same
  objects as in `domain/types.py` (decision 0018), so nothing breaks today.
  But a change of the inbound ports can now reach a driven adapter, and no
  check stops a second such import.
- Kind: operational
- Measurable as: ARCH-10 (a driven adapter imports from `brown_field` only
  `application.ports_out` and `domain`). Source: decision 0022.

## What changes

- `adapters/files/world_json.py` imports `Action`, `Direction` and `Item`
  from `domain/types.py`.
- New fitness function for ARCH-10, with a planted break, and a scenario
  tagged `@ARCH-10` in `fitness/structure.feature`.
- Does not change: any name, route, response, rule or stored format.

Out of scope, as the review recommends: G1 (the context object of decision
0012) and G3 (the win handling in `MoveUseCase`). Each waits for its trigger.

## Rules

- Added: ARCH-10
- Modified: none
- Removed: none
- Renamed: none

## Impact

No outside caller sees this change: no split into expand and contract is
needed.

| Part | Pace layer | Blast radius | Review needed |
| --- | --- | --- | --- |
| `adapters/files/world_json.py` | Fast | The start of the server, if the import is wrong | No |
| `tests/fitness/` | Medium | The test suite | Yes, with the suite |

## Decision record

0022 (proposed), whose Change field names this change.
