# Delta — hexagon-4-inbound-ports

Format adapted from the OpenSpec delta spec (MIT). On archive, the delta
merges into the specification and this file moves to the archive.

## ADDED Rules

#### ENTRY-3 — The port tier offers a use case for each command

- Status: accepted (decision 0015).
- Source: this change, and decision 0015. It extends the port tier of
  decision 0008.
- Rule: Katacombs shall offer, in the module `brown_field.game`, the use
  cases `SendMessageUseCase`, `ReadMessagesUseCase`,
  `ShowLeaderboardUseCase` and `LegacyPickupUseCase`, beside the twelve of
  decision 0008. Each one shall take the game as its only argument, and
  shall satisfy the port of the same name in `kata.py` (ARCH-2).
  `RegisterAccountUseCase` and `LoginUseCase` shall satisfy the ports
  `RegisterAccount` and `Login`.
- Why: a command with no use case can be reached only over HTTP, so a
  port test cannot pin it and a new adapter must copy its rule. Chat, the
  leaderboard and the legacy pickup are such commands today.
- Observable result: `SendMessageUseCase(game).execute(sid, "HI")` answers
  `SENT.` and adds one to the move count (CHAT-1, CHAT-3).
  `ReadMessagesUseCase(game).execute(sid)` answers the chat lines of the
  player's location (CHAT-2). `ShowLeaderboardUseCase(game).execute()`
  answers the finished games, highest score first (BOARD-1).
  `LegacyPickupUseCase(game).execute(sid, item_sid)` answers `OK` and
  behaves as LEGACY-1 and LEGACY-2. `RegisterAccountUseCase(game).execute`
  answers an email and a name, and no password digest.

#### ARCH-5 — The REST adapter holds no rule and changes no state

- Status: accepted (decision 0015).
- Source: this change, and decision 0015.
- Rule: Katacombs shall make each route of the REST adapter parse the
  request, call one use case, and map its result or its error to the
  response. A route shall not change the state of a player, of the world,
  of the chat or of the leaderboard, and shall not read that state except
  through a use case. The one exception is the energy gate of MOVE-5,
  while decision 0011 is proposed.
- Why: a rule in a route is lost when the REST adapter is regenerated
  alone, and a second adapter must copy it. The assessment found the
  player and world state written in two modules.
- Observable result: (1) a fitness function finds no attribute of the game
  (`players`, `places`, `chat`, `finished_games`, `accounts`) named under
  `brown_field/adapters/rest/`, except the energy gate. (2) The contract
  test and every REST feature pass unchanged.

## Other changes to the specification

### Data ownership: the paragraph after the table

No dataset has two writers across units. Inside game-server, only the
use cases write the player and world state. The REST adapter reads and
writes it only through the use cases (ARCH-5), except the energy gate of
MOVE-5 while decision 0011 is proposed.

### Contract: brown_field/spec/openapi.yaml

- No edit. Each route, request, response and error stays as it is.

## Unchanged

- `CHAT-1`: a chat message is sent, and the answer is `SENT.`
- `CHAT-2`: a player reads the chat lines of the location only.
- `CHAT-3`: a chat message adds one to the move count.
- `BOARD-1`: the leaderboard ranks the highest score first.
- `WIN-2`: a win adds a finished game to the leaderboard.
- `LEGACY-1`: the legacy pickup skips the bag limit, the win check and the move count.
- `LEGACY-2`: the legacy pickup of an item elsewhere answers OK and changes nothing.
- `ACCOUNT-1`: the registration answers the email and the name.
- `ACCOUNT-4`: the login answers the account's player, with the energy.
- `BAG-1`: the bag answer keeps its energy.
- `MOVE-5`: the energy gate stays in the route until decision 0011 is accepted.
- `API-2`: every error keeps its status and its message.
