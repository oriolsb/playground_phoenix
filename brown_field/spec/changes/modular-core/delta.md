# Delta — modular-core

Format adapted from the OpenSpec delta spec (MIT). Each section is
optional. Rules use the format of the specification. On archive, the
delta merges into the specification and this file moves to the archive.

## ADDED Rules

#### ENTRY-3 — Every command has a port

- Status: proposed (decision 0012).
- Source: change modular-core; the need: every adapter gets the same
  rules. Today chat, the leaderboard and the legacy pickup exist only as
  REST routes (api.py:139-141, api.py:165-182, api.py:187-197).
- Rule: Katacombs shall offer one use case with `execute` for each
  command of the REST API, in `brown_field.game`: the 12 of decision 0008
  plus `SendMessageUseCase`, `ReadMessagesUseCase`, `LeaderboardUseCase`
  and `LegacyPickupUseCase`.
- Why: a rule that lives in one adapter is lost when a second adapter
  appears. The step 7 rewrite already moved the energy gate on its own.
- Observable result: `XUseCase(InMemoryGame()).execute(...)` works for
  the 4 new names. Through them: a sent chat message answers `SENT.`
  and adds one to the move count (`CHAT-1`, `CHAT-3`); reading gives the
  messages of the present location, oldest first (`CHAT-2`); the
  leaderboard is ranked highest score first (`BOARD-1`); the legacy
  pickup takes an item with no bag limit, win check or move count, and
  of an item elsewhere changes nothing (`LEGACY-1`, `LEGACY-2`).

#### ENTRY-4 — A REST route adds no rule to its port

- Status: proposed (decision 0012).
- Source: change modular-core; api.py:166-173, api.py:188-197,
  api.py:210-213 hold rules today.
- Rule: When a client calls a REST route, Katacombs shall answer what the
  route's use case answers, mapped to JSON and to the status of its error
  reason, and nothing else.
- Why: one copy of each rule. Two copies drift, as the client and the
  server already did on the energy limit (0 and 1).
- Observable result: for each route, the REST scenario and the port
  scenario of the same rule give the same location, bag, message or
  error message. The REST adapter reads no game state outside the use
  cases (fitness function in decision 0012).

#### ENTRY-5 — The ports show the energy

- Status: proposed (decision 0012).
- Source: change modular-core; api.py:123-124 and api.py:149-150 add the
  energy that the domain types of kata.py don't carry.
- Rule: When a use case answers a Player or a Bag, Katacombs shall
  include the player's energy in it.
- Why: the REST routes show the energy (`BAG-1`, `PLAYER-1`); without
  it in the domain types, each adapter reads the internal state.
- Observable result: after one move from the start, the bag through the
  port shows energy 11, and the player through the register port shows
  energy 12. Over REST the bodies stay as they are.

#### ENTRY-6 — A game reads and writes its data through the stores it is given

- Status: proposed (decision 0012).
- Source: change modular-core; game.py:326-335, game.py:386-403,
  game.py:421-478, game.py:742-772 open the files from inside the rules.
- Rule: Where code builds `InMemoryGame` with a save store, an account
  store or a high-score sink, Katacombs shall read and write the saves,
  the accounts and the high-score lines only through them, and otherwise
  through the database file of `CONF-1` and the high-score file of
  `CONF-2`.
- Why: a feature that needs another storage, or a test that needs none,
  replaces one adapter and no rule.
- Observable result: a game built with in-memory stores saves a player;
  a second game built on the same stores lists the player (`SAVE-2`);
  register, quit and login restore the snapshot (`ACCOUNT-4`,
  `ACCOUNT-6`); a win reaches the sink (`WIN-3`). No file appears in the
  working directory. `InMemoryGame()` with no stores passes every
  `STORE-*`, `CONF-1` and `CONF-2` scenario as today.

#### ENTRY-7 — A game reads the time and the chance from the sources it is given

- Status: proposed (decision 0012).
- Source: change modular-core; game.py:316-319, game.py:480-488,
  game.py:646-654; the stdlib seams of decision 0008.
- Rule: Where code builds `InMemoryGame` with a clock or a random source,
  Katacombs shall use them for the market hours, the rat and the sids,
  and otherwise `datetime.now()` and the standard `random` module.
- Why: the seams of decision 0008 keep working for the tests we have,
  and a new feature with time or chance gets an injectable source from
  the start.
- Observable result: a game with a clock fixed at minute 55 refuses a
  move into SPITALFIELDS MARKET (`MOVE-6`); a game with a random source
  that always answers 0 makes the rat steal (`MOVE-8`). With no sources,
  the harness tests (`tests/harness`) still control both through
  `time-machine` and `random.random`.

#### WORLD-3 — The world file is the one definition of the world

- Status: proposed (decision 0012).
- Source: change modular-core; game.py:34-69 and game.py:135-301 build
  the same world that `brown_field/spec/world.json` describes.
- Rule: When a game starts with no world given, Katacombs shall build the
  world from `brown_field/spec/world.json`, and where code passes a world
  of the same schema, Katacombs shall build the world from it.
- Why: today a new location or item is written twice, in code and in the
  file, and only the tests compare them. A content feature should be an
  edit of data.
- Observable result: a test world with one more location, reachable from
  BRICK LANE, and one more item with `energy` 2 and its own use message,
  plays through the ports: the move reaches it, the take works, the use
  answers the message and raises the energy by 2. No code changes. With
  no world given, every `WORLD-*` scenario and the 7 transcripts pass
  as today.

## MODIFIED Rules

#### MOVE-5 — A player with no energy can't move

- Status: accepted (decisions 0011 and 0012).
- Source: legacy code (api.py:210-213, "Added for the mobile release"),
  revised by change modular-core.
- Rule: If a player with an energy of 0 or less moves, then Katacombs shall
  refuse the move, in the move use case, before every other move check.
- Why: A guess: energy is the cost of moving; food and drink restore it.
  The gate lives in the port so that every adapter gets it (decision
  0011).
- Observable result: status 405, error reason `NOT_ALLOWED`, message
  `YOU ARE TOO TIRED TO MOVE. EAT OR DRINK SOMETHING.` This check comes
  before every other move check, the win included. Through the move port
  the same refusal is a `NotAllowed` with the same message, and the
  energy never goes below 0.
- Revised: 2026-11-26. The gate moves from the REST route into
  `MoveUseCase`, at energy 0, as decision 0011 proposes (decision 0012).
  The open question is answered: the port, at 0.

#### WORLD-1 — The game is played in the world of world.json

- Status: observed. The code does it; nobody has decided it (2026-11-25).
- Source: legacy code (game.py:34-69, game.py:135-301, game.py:408-412);
  characterized into `brown_field/spec/world.json`, with its schema
  `brown_field/spec/world.schema.json`, revised by change modular-core.
- Rule: Katacombs shall start each game in the world that
  `brown_field/spec/world.json` describes: each location with its title,
  description, exits, items and gold, and each item with its sid, name,
  description, actions, value, gold inside, lock and use effect.
- Why: the world is the content of the game. Saves, the golden files, the
  high-score file and the mobile client v1 refer to its titles and its item
  sids, so a changed world breaks them.
- Observable result: a look around in each location shows the title,
  description, exits (in this order) and items of `world.json`; a look in
  each direction shows the location that `exits` names; the first visit
  adds the location's `gold`; `GET /items/{sid}` answers the item of
  `world.json` for each sid. The use effects of `world.json` give the
  answers of `ACT-14` (the KEY unlocks the MANHOLE COVER in BACK YARD)
  and `ACT-15` (BREAD gives 5 energy, BEER 3, with their messages).
- Revised: 2026-11-26. The item use effects of `ACT-14` and `ACT-15`
  move from the code into `world.json` (decision 0012).

## Other changes to the specification

### Terms: Port

| Port | A use case with `execute`: the one entry of one command, for every adapter. The REST API is one adapter. | endpoint (for this idea), service, handler |

### Terms: Store

| Store | Where a game keeps the data that survives a restart: the saves, the accounts, the high-score lines. The default stores are the database file and the high-score file. | repository, DAO, database (alone) |

### Data ownership: the note under the table

No dataset has two writers across units. Inside game-server, only the
use cases write the player and the world state; the REST adapter writes
none (`ENTRY-4`).

### Contract: brown_field/spec/world.schema.json

Planned, edited in place by `/phoenix-kit:contract` after the review:

- `item` gets an optional `use` object, `WORLD-1`, `WORLD-3`:
  - `unlocks`: the sid of a locked item, with `where` (the title where
    the use works), `message` and `alreadyMessage`, for `ACT-14`.
  - `energy`: the energy the use gives, up to the maximum of 20, with
    `message`; the item leaves the bag, for `ACT-15`.
- `world.json` gets `use` on KEY, BEER and the 3 BREAD items. No other
  value changes.

### Contract: brown_field/kata.py

- `Player` and `Bag` get `energy: int`, `ENTRY-5`.
- 4 new protocols: `SendMessage`, `ReadMessages`, `Leaderboard`,
  `LegacyPickup`, `ENTRY-3`.

## Old values

The port test that pins "no gate" gets a new name.

| Rule ID | Old value | New value |
| --- | --- | --- |
| MOVE-5 | `The move port has no energy gate` | `The move port refuses a tired player` |

## Unchanged

- `MOVE-1`, `MOVE-2`, `MOVE-3`, `MOVE-4`: the same use case gets the gate
  first; the order of the checks stays.
- `MOVE-6`: the clock becomes an injectable source.
- `MOVE-7`: the gate comes before the win check, as today.
- `MOVE-8`: the random source becomes injectable.
- `ACT-8`, `ACT-11`, `ACT-13`: the world state stays shared by every
  player.
- `ACT-14`, `ACT-15`, `ACT-16`: the effects move into the world file.
- `WORLD-2`: the world is loaded from the file now.
- `WIN-1`, `WIN-2`, `WIN-3`, `BOARD-1`: the win moves into its own module
  and the high-score file goes behind a sink.
- `SAVE-1`, `SAVE-2`, `STORE-1`, `STORE-2`, `STORE-3`, `CONF-1`,
  `CONF-2`: the stores and the codec are new code over the same data.
- `ACCOUNT-4`, `ACCOUNT-6`: login and quit use the same codec.
- `CHAT-1`, `CHAT-2`, `CHAT-3`, `LEGACY-1`, `LEGACY-2`: they move from
  the routes into use cases.
- `ENTRY-1`, `ENTRY-2`: `create_app` and `app` stay where they are.
- `API-1`, `API-2`: the error mapping stays in the REST adapter.
- `OPS-1`: one more indirection per command.
