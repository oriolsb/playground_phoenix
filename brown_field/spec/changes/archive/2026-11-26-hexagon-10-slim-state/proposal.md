# Proposal — hexagon-10-slim-state

Structure adapted from the OpenSpec proposal template (MIT).

Stage 10. Finding F3 of the hexagonal review. The game rules and the view
mapping leave `GameState`. Decision 0012 stays: each use case still takes
the game as its only argument (decision 0020).

## Need

- Who: the next person who changes a rule or a response shape.
- Why: `application/state.py` mixes four jobs: it holds the outbound ports,
  stores the aggregates (players, chat, accounts, finished games), maps to
  the view models (`to_player`, `to_bag`, `to_location`), and holds two
  rules (`market_is_cleaning`, `password_hash`) (`application/state.py:37-48`,
  `application/state.py:84-197`).
- Kind: operational
- Measurable as: ARCH-9 (`state.py` holds no rule and no mapping). Source: decision 0020.

## What changes

- `market_is_cleaning(clock)` becomes a domain function that takes the
  minute as a value, for example `domain/world.py market_is_cleaning(minute)`.
  `MoveUseCase` reads the clock and passes the minute.
- `password_hash` moves to the domain (`domain/accounts.py`). It keeps the
  digest of STORE-3 exactly.
- `to_player`, `to_bag`, `to_location` move to `application/views.py`.
- `GameState` keeps the ports, the aggregates and the lookups (`player`,
  `item`, `new_sid`, `now_iso`, the loads).
- Does not change: any rule, response, digest or stored format; decision
  0012; any frozen name.

## Rules

- Added: ARCH-9
- Modified: none
- Removed: none
- Renamed: none

## Impact

No outside caller sees this change: no split into expand and contract is
needed.

| Part | Pace layer | Blast radius | Review needed |
| --- | --- | --- | --- |
| `application/state.py` | Slow (the context object of decision 0012) | Every use case | Yes |
| `application/views.py` | Fast | Every response, through the use cases | Yes, through the contract test |
| `domain/` | Medium (the game rules) | MOVE-6, STORE-3 | Yes |

## Decision record

0020 (proposed), whose Change field names this change.
