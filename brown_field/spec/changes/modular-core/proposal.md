# Proposal — modular-core

Structure adapted from the OpenSpec proposal template (MIT).

## Need

In order to add features we don't know yet without touching every file,
we restructure the game-server behind the ports. Nothing changes over
REST, in the database file or in the high-score file.

- Who: the team that maintains game-server, and every future adapter
  (mobile client v1 and the web client today; a CLI, a queue or a v2 API
  tomorrow).
- Why: at the moment (2026-11-26) one new feature touches `game.py`,
  `api.py` and often the SQLite code at once.
  - `api.py` holds rules of its own: the energy gate, the whole chat, the
    legacy pickup and the leaderboard sort. A second adapter has to copy
    them or loses them.
  - The use cases open SQLite and append to the high-score file
    themselves, and call `datetime.now()` and `random` directly.
  - The player state is turned into a payload, and back, in 4 places
    (`snapshot_of`, `SaveGameUseCase`, `load_saves`, `LoginUseCase`).
    Energy was the last field added, and `old-save-without-energy.db`
    shows how that went.
  - The world is written twice: `build_places()` / `build_items()` in
    code and `spec/world.json`. The item effects (the key, the manhole,
    bread and beer) are `if` branches on hard-coded sids in
    `UseItemUseCase`.
- Kind: operational.
- Measurable as:
  - `ENTRY-3`, `ENTRY-4`: every command has a port, and a REST route
    adds no rule. Target: for each route, a port scenario that gives the
    same answer; the REST adapter reads no game state (fitness function
    in decision 0012).
  - `WORLD-3`: a new item with a use effect, or a new location, needs an
    edit of the world file only. Target: a test world with one more
    location and one more food item plays through the ports with no code
    change.
  - `ENTRY-6`: a game runs on stores it is given. Target: save, restart
    and login on in-memory stores, with no file written.

## What changes

The port tier becomes the only place that holds rules. Everything else
is an adapter.

- **The energy gate moves into `MoveUseCase`** (`MOVE-5`), as decision
  0011 proposes: at energy 0, first check. The REST route maps the
  `NotAllowed` to 405 as for every other refusal. 0011 is accepted
  (2026-11-26).
- **Four new use cases** for the commands that only exist as routes
  today: `SendMessageUseCase`, `ReadMessagesUseCase`,
  `LeaderboardUseCase`, `LegacyPickupUseCase` (`ENTRY-3`). Their
  protocols go into `kata.py` next to the other 12.
- **Energy through the ports** (`ENTRY-5`): the domain `Player` and `Bag`
  of `kata.py` get an `energy` field, so `api.py` stops reading
  `game.players[sid].energy`.
- **Driven ports for I/O** (`ENTRY-6`, `ENTRY-7`): `SaveStore`,
  `AccountStore`, `HighScoreSink`, `Clock`, `Random`. `InMemoryGame()`
  with no arguments builds the default adapters, so it behaves as today:
  SQLite file of `CONF-1`, JSONL file of `CONF-2`, `datetime.now()` and
  the `random` module (the seams of decision 0008 stay).
- **One player-state codec**, checked against
  `player-state.schema.json`, used by saves, accounts and login.
- **The world is read from `world.json`** (`WORLD-3`). The item use
  effects become data in the file (`MODIFIED WORLD-1`): `unlocks` for the
  key, `energy` plus the message for bread and beer. One small
  interpreter in the items module replaces the hard-coded branches.
- **`game.py` is split by area** into a `brown_field/core/` package. The
  names that decision 0008 freezes stay importable from
  `brown_field.game`, which becomes a re-export.

Target layout:

```
brown_field/
  kata.py              driving ports + domain types (the boundary), 16 use-case protocols
  game.py              re-exports InMemoryGame, the *UseCase classes, the errors (decision 0008)
  api.py               REST adapter only: create_app, app, JSON mapping, error mapping
  core/
    errors.py          KatacombsError and subclasses
    ports.py           SaveStore, AccountStore, HighScoreSink, Clock, Random
    state.py           PlayerState, Account, ChatMessage, the player-state codec
    world.py           World: load from world.json, connect/disconnect, check_connections
    game.py            InMemoryGame: world, players, chat, finished games, the driven ports
    players.py         Register, List, Quit
    looking.py         LookAround, LookInDirection
    movement.py        Move: gate, market, rat, win
    items.py           InspectItem, InspectBag, UseItem, LegacyPickup, the effect interpreter
    winning.py         record a win, Leaderboard
    saving.py          SaveGame
    accounts.py        RegisterAccount, Login
    chat.py            SendMessage, ReadMessages
  adapters/
    sqlite_store.py    saves + accounts (STORE-1, STORE-2, CONF-1)
    highscores.py      JSONL sink (WIN-3, CONF-2)
    system.py          stdlib clock and random
```

What does **not** change:

- Every REST route, status, body and message (`openapi.yaml` stays as
  it is).
- The tables `saves` and `accounts`, the payload and the high-score line.
- The world content: titles, sids, order, gold, values.
- The seams of decision 0008.
- The shared world state (an opened manhole is open for everyone,
  `ACT-8`). We keep it on purpose; per-player world state would be a
  behavior change, with its own change.

Out of scope, each one for its own change:

- The web client (`brown_field/web/`): splitting `App.tsx` by panel and
  reading "can move" from the server. It's a separate unit with its own
  specification, and `WEB-MOVE-2` is still contested.
- The contested rules (`CHAT-1`, `CHAT-3`, `STORE-3`, `API-2`): the
  restructure keeps what the code does.

Order of work, one commit per step, the whole suite green after each:

1. `MOVE-5` into the port, the 4 new use cases, energy in the domain
   types. `api.py` becomes thin.
2. Driven ports, the default adapters, the codec.
3. The world from `world.json`, item effects as data.
4. The split into `core/` and `adapters/`, with `game.py` as a
   re-export.

Step 3 is the one we are afraid of: the 7 transcripts must stay
byte-identical, and the order of exits and items comes from the file
then, not from the code.

## Rules

- Added: `ENTRY-3`, `ENTRY-4`, `ENTRY-5`, `ENTRY-6`, `ENTRY-7`, `WORLD-3`.
- Modified: `MOVE-5`, `WORLD-1`.
- Removed: none.
- Renamed: none.

## Impact

No REST caller sees a change, so no expand/contract split is needed. The
port tier is a boundary since decision 0008: its callers are `api.py`
and the port tests. One port test flips (`MOVE-5`), the rest is additive.

| Part | Pace layer | Blast radius | Review needed |
| --- | --- | --- | --- |
| `openapi.yaml`, REST routes | slow | none, unchanged | no |
| Database file, high-score file | slow | none, unchanged; the codec is pinned by `STORE-1`, `STORE-2`, `SAVE-2` and the golden DBs | yes, a person checks the golden DB tests |
| `world.json`, `world.schema.json` | slow | the schema gets `unlocks`, `energy`, `useMessage`; the content stays | yes |
| Port tier (`kata.py`, `brown_field.game` names) | medium | `MOVE-5` port test flips; 4 protocols and 1 field added | yes |
| Internal modules (`core/`, `adapters/`) | fast | game-server only | no |
| Mutation harness | fast | mutants that name `api.py` or `game.py` text are re-pointed | no |

The `Units` row of `PHOENIX.md` gets the new modules at archive time.

## Decision record

0012 (proposed): `brown_field/decisions/0012-the-rules-live-behind-the-ports.md`.
