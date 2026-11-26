# Proposal — hexagon-9-energy-gate

Structure adapted from the OpenSpec proposal template (MIT).

Stage 9. Finding F2 of the hexagonal review. The energy gate of MOVE-5
moves from the REST route into the core, at energy 0, as decision 0011
proposes. Accepting this change accepts decision 0011.

## Need

- Who: mobile client v1 and the web client (the gate came with the mobile
  release); every adapter after REST, which must get the gate too.
- Why: the gate lives in the `move` route (`adapters/rest/app.py:199-205`).
  The move port lets the energy go below 0. A second adapter, or a test at
  the port, gets no gate. ARCH-5 carries an exception only for it.
- Kind: operational
- Measurable as: MOVE-5 (the port refuses a tired player), ARCH-5 with no
  exception. Source: decision 0011.

## What changes

- New domain behavior: `PlayerState.ensure_rested()` raises `NotAllowed`
  with `YOU ARE TOO TIRED TO MOVE. EAT OR DRINK SOMETHING.` at energy 0 or
  less.
- `MoveUseCase.execute` calls it right after it finds the player, before
  the win check, as the route does today.
- The `move` route only calls the port. The `KatacombsError` handler maps
  the error to 405, as it maps every `NotAllowed`.
- Does not change: the status, body or message over REST; the order of the
  checks (the gate first, the win second).
- Changes at the port: `MoveUseCase` refuses a tired player. One port
  scenario flips: "The move port has no energy gate" becomes "The move
  port refuses a tired player".
- Stays open: WEB-MOVE-2 (the client stops at 1). Out of scope.

## Rules

- Added: none
- Modified: MOVE-5
- Removed: none
- Renamed: none

## Impact

A caller of the port sees a change; a caller of the REST API sees none.
The port tier is inside the project, and one regeneration updates it, so
no split into expand and contract is needed.

| Part | Pace layer | Blast radius | Review needed |
| --- | --- | --- | --- |
| MOVE-5 and the move port | Slow (the ports) | Port tests, every adapter | Yes |
| `domain/player.py` | Medium (the game rules) | The move | Yes |
| `adapters/rest/` | Fast | None, if the transcripts pass | No |

## Decision record

0011 (proposed), whose Change field names this change.
