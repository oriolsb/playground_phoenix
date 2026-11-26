# Delta — hexagon-12-driven-adapter-imports

Format adapted from the OpenSpec delta spec (MIT). On archive, the delta
merges into the specification and this file moves to the archive.

## ADDED Rules

#### ARCH-10 — A driven adapter depends only on the outbound ports and the domain

- Status: accepted (decision 0022).
- Source: this change; finding G2 of the stage 11 hexagonal review; decision 0022.
- Rule: Katacombs shall make each driven adapter, every module under
  `brown_field/adapters/` outside `adapters/rest/`, import from the package
  `brown_field` only `brown_field.application.ports_out` and modules of
  `brown_field/domain/`.
- Why: a driven adapter implements an outbound port. A dependency on the
  inbound ports, on the use cases or on the game state ties it to the
  driving side, so a change there can break storage, files or the clock.
- Observable result: (1) a fitness function finds no other import from
  `brown_field` in a driven adapter. (2) A planted `from ...kata import Item`
  in a driven adapter fails it, and names the file and the line. (3) The
  whole suite passes unchanged.

## Unchanged

- `WORLD-1`: the world of `world.json` keeps every field.
- `WORLD-2`: the start check of the way back stays.
