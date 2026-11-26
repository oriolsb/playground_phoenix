# Delta — hexagon-9-energy-gate

Format adapted from the OpenSpec delta spec (MIT). On archive, the delta
merges into the specification and this file moves to the archive.

## MODIFIED Rules

#### MOVE-5 — A player with no energy can't move

- Status: accepted (decision 0011). The gate is at the port, at energy 0.
- Source: legacy code (api.py:210-213, "Added for the mobile release"), revised by this change.
- Rule: If a player with an energy of 0 or less moves, then Katacombs shall
  refuse the move, at the move port and so over every adapter.
- Why: energy is the cost of moving; food and drink restore it. The gate
  came with the mobile release. At the port, every adapter gets it.
- Observable result: status 405, error reason `NOT_ALLOWED`, message
  `YOU ARE TOO TIRED TO MOVE. EAT OR DRINK SOMETHING.` This check comes
  before every other move check, the win included. At the port,
  `MoveUseCase` raises `NotAllowed` with the same message, and the energy
  and the move count do not change.
- Revised: 2026-11-26. The gate moves from the REST route to the move port, at 0 (decision 0011).

## Other changes to the specification

### Revision of ARCH-5 (open in `hexagon-4-inbound-ports`), to apply after `hexagon-8-inbound-injection`

#### ARCH-5 — The REST adapter holds no rule and changes no state

- Status: accepted (decisions 0015, 0019, 0011).
- Source: change `hexagon-4-inbound-ports`, revised by `hexagon-8-inbound-injection` and `hexagon-9-energy-gate`.
- Rule: Katacombs shall make each route of the REST adapter parse the
  request, call one inbound port, and map the result or the error to the
  response. A route shall hold no game rule and reach the state only
  through the ports, with no exception.
- Why: a rule in a route is lost when the REST adapter is regenerated
  alone, and a second adapter must copy it.
- Observable result: the `move` route calls only `Move`. The fitness
  function of ARCH-5 has no exception. The transcripts pass unchanged.
- Revised: 2026-11-26. The MOVE-5 exception ends (decision 0011).

## Old values

The scenario name below is the old wording of the port test.

| Rule ID | Old value | New value |
| --- | --- | --- |
| MOVE-5 | `The move port has no energy gate` | `The move port refuses a tired player` |

## Unchanged

- `MOVE-2`: a move costs 1 energy.
- `MOVE-7`: a player who has won can't move; the gate still comes first.
- `ACT-15`: bread and beer restore energy.
- `PLAYER-9`: an unknown player sid is not found.
- `API-2`: every error keeps its status and its message.
