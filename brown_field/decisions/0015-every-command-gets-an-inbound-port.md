# 0015 — Chat, the leaderboard, accounts and the legacy pickup get inbound ports

- **Status:** proposed
- **Date:** 2026-11-26
- **Need:** operational. Every adapter after REST must reach every command
  through a port. Mobile client v1 must see no change of the legacy pickup
  (decision 0003).
- **Traces to:** `ENTRY-3`, `ARCH-5`, `CHAT-1`, `CHAT-2`, `CHAT-3`, `BOARD-1`, `LEGACY-1`, `LEGACY-2`, `ACCOUNT-1`, `ACCOUNT-4`, `BAG-1`.
- **Change:** hexagon-4-inbound-ports
- **Evidence (legacy code only):**
  - `api.py:166-182`: chat writes `game.chat` and adds to the move count in
    the route.
  - `api.py:139-141`: the leaderboard is sorted in the route.
  - `api.py:189-197`: the legacy pickup moves the item in the route.
  - `api.py:123-124`, `api.py:149-150`: the energy is read from
    `game.players` in the route, because `kata.Player` and `kata.Bag` have
    no energy.
  - `game.py:775-830`: `RegisterAccountUseCase` and `LoginUseCase` exist,
    with no port in `kata.py`. The first returns `Account`, with
    `password_hash`.

## Context

`kata.py` publishes ten ports. Six commands have none. Four of them have
no use case either, so their rules live in routes. A second adapter would
copy them, and a regeneration of the REST adapter alone would lose them.
The legacy pickup is a weaker TAKE on purpose (decision 0003). A careless
move into `UseItemUseCase` would give it the bag limit and the win check.

## Decision

`kata.py` grows. Nothing in it is renamed or removed.

```python
@dataclass
class ChatLine:      name: str; text: str; at: str
@dataclass
class FinishedGame:  name: str; score: int; moves: int
@dataclass
class AccountView:   email: str; name: str

class SendMessage(Protocol):     def execute(self, player_sid: str, text: str) -> str: ...
class ReadMessages(Protocol):    def execute(self, player_sid: str) -> list[ChatLine]: ...
class ShowLeaderboard(Protocol): def execute(self) -> list[FinishedGame]: ...
class RegisterAccount(Protocol): def execute(self, email: str, password: str, name: str) -> AccountView: ...
class Login(Protocol):           def execute(self, email: str, password: str) -> Player: ...
class LegacyPickup(Protocol):    def execute(self, player_sid: str, item_sid: str) -> str: ...
```

`Player` and `Bag` get a last field, `energy`, with a default value, so
the REST adapter reads the energy from the result of a use case.

The port tier gets `SendMessageUseCase`, `ReadMessagesUseCase`,
`ShowLeaderboardUseCase` and `LegacyPickupUseCase`, each built as
`XUseCase(game)`. `LegacyPickupUseCase` keeps LEGACY-1 and LEGACY-2 exactly:
no bag limit, no win check, no move count, `OK` for an item elsewhere.

Each route parses, calls one use case, and maps the result (ARCH-5). The
one exception is the energy gate of MOVE-5. It stays in the route until
the group decides 0011.

## Alternatives rejected

| Alternative | Why you rejected it |
| --- | --- |
| Map the legacy pickup to `UseItemUseCase` with the action `pick` | Gives it the bag limit, the win check and the move count. That is a change for mobile client v1, against decision 0003. |
| Put the new ports in a new module, keep `kata.py` as is | `kata.py` is where a reader and a regeneration look for the ports. Two homes for ports split the boundary. The group chose to let `kata.py` grow. |
| A new view type `PlayerWithEnergy`, not a field on `Player` | Every port that answers a player would need a second type, and `Login` and `RegisterPlayer` would differ from `ListPlayers`. One field is smaller. |
| Move the energy gate into `MoveUseCase` in this stage | It changes what a port caller sees. Decision 0011 holds that question for the group. |

## Consequences

**Easier:** every command has a port test. A new adapter needs no copy of
a rule. The digest of a password no longer crosses a port.

**More difficult:** `kata.py` doubles in size. The field `energy` with a
default value can hide a use case that forgets to set it. The contract test
catches it over REST, because `energy` is required in the responses.

**Risks that stay:** until 0011 is decided, ARCH-5 has one exception, and
the fitness function must name it.

## Fitness functions

| Function | Target | How to run it | Need that it protects |
| --- | --- | --- | --- |
| No game state named in the REST adapter, except the energy gate | zero hits | `uv run pytest brown_field/tests/fitness -m ARCH-5` (to write) | Rules live in use cases |
| Each new use case at the port | pass | `uv run pytest brown_field/tests/ports -m ENTRY-3` (to write) | Every adapter reaches every command |
| The legacy pickup over REST | pass | `uv run pytest -m "LEGACY-1 or LEGACY-2"` | Mobile client v1 (decision 0003) |
| The contract test | pass | `uv run pytest brown_field/tests/contract` | Every REST client |
