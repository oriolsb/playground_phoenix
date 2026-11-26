# Proposal — hexagon-6-domain-model

Structure adapted from the OpenSpec proposal template (MIT).

Stage 6 of 6 of the move to ports and adapters (decision 0012). The rules
of the game move from the use cases into a domain model (decision 0017).

## Need

- Who: the team that restructures the game-server; the next person who
  changes a game rule.
- Why: the rules live in long `if` chains inside the use cases.
  `UseItemUseCase.execute` is 80 lines with five branches
  (`game.py:656-735`). `MoveUseCase` mixes the move, the rat, the win and
  the high-score line (`game.py:616-655`). `PlayerState` and `Place` hold
  data and no behavior (`game.py:95-117`). `InMemoryGame` holds the
  players, the world state, the accounts, the chat and the leaderboard in
  one object (`game.py:406-417`). A rule change today means a change in a
  use case, with its ports and its mapping around it.
- Kind: operational
- Measurable as: ARCH-1 for the domain layer (it exists after this
  stage, and imports nothing outward). The mutation harness
  (decision 0010) kills the same mutants before and after.

## What changes

- New modules in `brown_field/domain/`: `player.py` (the player with its
  moves, energy, gold, visits and win), `bag.py` (the slot rule and the
  score), `world.py` (locations, exits, the manhole connection, open and
  locked items), `errors.py` (the error types, re-exported by `game.py`).
- Each use case loads what it needs through the ports, calls the domain,
  and saves through the ports. It holds no game rule.
- `InMemoryGame` keeps its name and its keyword arguments. It becomes the
  composition root only: it builds the adapters and holds them.
- Does not change: any rule, response, message, order of checks, or
  stored format.

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
| `domain/` | Medium (the game rules) | Every rule of the Specification | Yes, through the suite and the mutation harness |
| The use cases in `application/` | Medium | Every port test | Yes |
| `InMemoryGame` | Slow (the port tier) | Every port test and the composition root | Yes |

## Decision record

0017 (proposed), whose Change field names this change.
