# Delta — hexagon-8-inbound-injection

Format adapted from the OpenSpec delta spec (MIT). On archive, the delta
merges into the specification and this file moves to the archive.

## ADDED Rules

#### ARCH-8 — The REST adapter depends on the inbound ports only

- Status: accepted (decision 0019).
- Source: this change; finding F1 of the hexagonal review; decision 0019.
- Rule: Katacombs shall build the REST adapter from an `InboundPorts`
  value, whose fields are typed as the inbound ports of `kata.py`. No
  module under `brown_field/adapters/rest/` shall import
  `brown_field.application` or `brown_field.domain`; it shall take its
  ports, view models and error types from `kata.py`.
- Why: a driving adapter that depends on concrete use cases and on the
  game state can bypass every port. With the ports injected, the adapter
  can be tested with fakes, and the ports become the real contract.
- Observable result: (1) a fitness function finds no import of
  `brown_field.application` or `brown_field.domain` under
  `adapters/rest/`. (2) A test builds the REST adapter from fake ports,
  with no `GameState`, and `POST /game/player` answers 201 with the
  player that the fake `RegisterPlayer` returns. (3) The contract test and
  every REST feature pass unchanged.

## Other changes to the specification

### Revision of ARCH-5 (open in `hexagon-4-inbound-ports`), to apply when that change is archived

#### ARCH-5 — The REST adapter holds no rule and changes no state

- Status: accepted (decisions 0015, 0019).
- Source: change `hexagon-4-inbound-ports`, revised by `hexagon-8-inbound-injection`.
- Rule: Katacombs shall make each route of the REST adapter parse the
  request, call the inbound ports it needs, and map the result or the
  error to the response. A route shall reach the state only through the
  ports. The one exception is the energy gate of MOVE-5, which reads the
  energy through `InspectBag` while decision 0011 is proposed.
- Why: a rule in a route is lost when the REST adapter is regenerated
  alone, and a second adapter must copy it.
- Observable result: the adapter has no access to the game state (ARCH-8).
  The contract test and every REST feature pass unchanged.
- Revised: 2026-11-26. The gate reads the energy through a port (decision 0019).

### Contract: brown_field/spec/openapi.yaml

- No edit.

## Unchanged

- `MOVE-5`: the gate refuses at energy 0 or less, before every other move check.
- `PLAYER-9`: an unknown player sid is not found, on the move route too.
- `API-2`: every error keeps its status and its message.
- `ENTRY-1`: `create_app(game)` serves the game it is given.
- `ENTRY-2`: `brown_field.api.app` stays.
