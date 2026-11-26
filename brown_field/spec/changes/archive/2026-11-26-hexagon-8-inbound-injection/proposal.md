# Proposal — hexagon-8-inbound-injection

Structure adapted from the OpenSpec proposal template (MIT).

Stage 8. Finding F1 of the hexagonal review, its main issue. The REST
adapter depends on the inbound ports, and the composition root hands it
their implementations (decision 0019).

## Need

- Who: the team that regenerates the REST adapter; anybody who tests it.
- Why: `kata.py` declares 16 inbound ports, but no code depends on them.
  The REST adapter imports `GameState` and every `*UseCase` class
  (`adapters/rest/app.py:15-33`) and builds one use case in each route
  (`adapters/rest/app.py:105-208`). So the ports are decorative, and the
  adapter can reach every piece of state.
- Kind: operational
- Measurable as: ARCH-8 (zero imports of `brown_field.application` under
  `adapters/rest/`). Source: decision 0019.

## What changes

- New type in `kata.py`: `InboundPorts`, a dataclass with one field per
  inbound port, each typed as the port's `Protocol`.
- `build_app(ports: InboundPorts)` replaces `build_app(game)`. It imports
  only `kata.py` (ports, view models, errors) and FastAPI.
- The composition root builds the ports once per game:
  `create_app(game=None)` builds `InboundPorts` from the game's use cases.
  `create_app` and `app` keep their names and behavior (ENTRY-1, ENTRY-2).
- The energy gate of MOVE-5 stays in the `move` route until stage 9, but it
  reads the energy through the port `InspectBag`, not through `GameState`.
  A missing player gives the same 404 as today: `InspectBag` raises the
  same `PlayerNotFound` that `Move` raised.
- Does not change: any route, request, response, status or message; any
  frozen name.

## Rules

- Added: ARCH-8
- Modified: none in the specification. ARCH-5 (open in
  `hexagon-4-inbound-ports`) is revised under "Other changes".
- Removed: none
- Renamed: none

## Impact

No outside caller sees this change: no split into expand and contract is
needed.

| Part | Pace layer | Blast radius | Review needed |
| --- | --- | --- | --- |
| `kata.py`, `InboundPorts` | Slow (the ports) | Every driving adapter | Yes |
| `adapters/rest/` | Fast | Every REST client, if a mapping is wrong | Yes, through the contract test |
| `api.py` | Slow (ENTRY-1, ENTRY-2) | Tests and `python -m brown_field` | Yes |

## Decision record

0019 (proposed), whose Change field names this change.
