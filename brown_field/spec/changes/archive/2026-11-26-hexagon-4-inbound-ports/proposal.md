# Proposal — hexagon-4-inbound-ports

Structure adapted from the OpenSpec proposal template (MIT).

Stage 4 of 6 of the move to ports and adapters (decision 0012). It gives
each command a use case and a port, and leaves the REST adapter with no
rule and no state (decision 0015).

## Need

- Who: the team that restructures the game-server; every adapter after
  REST (a CLI, a socket, a test); mobile client v1, whose legacy pickup
  must not change (decision 0003).
- Why: four commands live only in `api.py`. Chat (`api.py:166-182`), the
  leaderboard (`api.py:139-141`) and the legacy pickup (`api.py:189-197`)
  have no use case. The energy is added to responses by reading
  `game.players` directly (`api.py:123-124`, `api.py:149-150`), because
  the public `Player` and `Bag` carry no energy. Accounts and login have
  use cases with no port, and `RegisterAccountUseCase` returns the
  internal `Account` with its password digest (`game.py:792`). The
  assessment records that `game.py` and `api.py` both write the player and
  world state.
- Kind: operational
- Measurable as: ENTRY-3 (six new ports and use cases in the port tier),
  ARCH-5 (the REST adapter writes no state). Source: decision 0015.

## What changes

- New inbound ports in `kata.py`, added after the ten of today:
  `SendMessage`, `ReadMessages`, `ShowLeaderboard`, `RegisterAccount`,
  `Login`, `LegacyPickup`.
- New public types in `kata.py`: `ChatLine` (name, text, at),
  `FinishedGame` (name, score, moves), `AccountView` (email, name).
- New field `energy` on the public `Player` and `Bag`, added last, with a
  default value. The REST adapter reads it there.
- New use cases in the port tier: `SendMessageUseCase`,
  `ReadMessagesUseCase`, `ShowLeaderboardUseCase`, `LegacyPickupUseCase`.
  `RegisterAccountUseCase` and `LoginUseCase` exist and gain their ports.
- `RegisterAccountUseCase.execute` returns an `AccountView`, not the
  internal `Account`.
- Each route parses, calls one use case, and maps the result.
- Does not change: any route, request, response, status or message. The
  legacy pickup keeps its weak checks (LEGACY-1, LEGACY-2). The energy
  gate of MOVE-5 stays in the route while decision 0011 is proposed.
- Does not remove or rename any name of `kata.py` or of the port tier.

## Rules

- Added: ENTRY-3, ARCH-5
- Modified: none
- Removed: none
- Renamed: none

## Open questions for the review

1. The default value of the new field `energy` on `Player` and `Bag`.
   Recommended: no default in practice, because every use case sets it,
   and a default of `0` only keeps old call sites working. A port test
   that builds a `Player` by hand is the only such call site.
2. The return type of `RegisterAccountUseCase.execute` changes from
   `Account` to `AccountView`. Both have `email` and `name`. A port test
   that reads `password_hash` from the result would break. None does
   today. Recommended: change it, because the digest must not cross the
   port.

## Impact

No outside caller of the REST API sees this change: no split into expand
and contract is needed. The port tier grows. Nothing in it is removed or
renamed, so every port test keeps working.

| Part | Pace layer | Blast radius | Review needed |
| --- | --- | --- | --- |
| `kata.py`, new ports and types | Slow (the ports, the contracts) | Every adapter, every regeneration | Yes |
| The use cases in `application/` | Medium (the game rules) | Chat, leaderboard, accounts, legacy pickup | Yes |
| `adapters/rest/` | Fast | Every REST client, if a mapping is wrong | Yes, through the contract test |

## Decision record

0015 (proposed), whose Change field names this change.
