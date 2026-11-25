> **Characterization record, 2026-11-25.** Every rule below records what the legacy code does
> today, and a test pins it. A rule's `Status` says whether anybody decided it:
> **50 observed** (the code does it; nobody decided it), **13 accepted** (kept on purpose; it cites its decision record), **11 contested** (in doubt; it states its open question).
> "Why: A guess:" marks a reason that nobody wrote down; it is the reader's inference.

# Katacombs — Specification (game-server)

Status: recovered from the legacy code on 2026-11-25. Each rule records
what the code does today, not what the brief asked for. A rule's Source
names the file and line that show the behavior. Where the brief and the
code disagree, the rule follows the code, and the decision records
(`brown_field/decisions/`) say why when anybody knows.

Scope: the game-server unit (`brown_field/game.py`, `api.py`, `kata.py`).
The web client has its own specification in `brown_field/web/spec/`.

This first version holds the **boundary rules**: the rules whose result a
caller sees. The internal rules and the operational limits come next
(items 2 and 3 of the work plan).

## Assumptions

- "A client" is any caller of the REST API: the web client, the mobile
  client v1, or a script.
- The world map, the items and their values are fixed data, in
  `brown_field/spec/world.json` (WORLD-1). A rule that names a location or
  an item uses its title or name as the API shows it.
- Error messages are part of the contract: clients show them to players
  as they are.

## Terms

| Term | Meaning | Avoid |
| --- | --- | --- |
| Player | One active game of one person, with a sid, a name, a location, a bag, energy and a move count. | user, character, session |
| Player sid | The identifier of a player: digits in the form `NNNNNN-NNNNNNNNNNNN-NNNNNNNN`. | id, player id, token |
| Account | An email, a password and a name, that survives a restart and resumes a player. | user, profile |
| Location | A place in the world, with a title, a description, exits and items. | place, room, area, scene |
| Title | The unique name of a location, in upper case. | location name, place name |
| Exits | The directions in which a player can leave a location. | connections, doors, ways |
| Direction | One of `north`, `south`, `east`, `west`, `up`, `down`. | heading, cardinal |
| The katacombs exit | The location `KATACOMBS EXIT`. Entering it wins the game. On the wire: `isExit`. | the exit (alone), finish, goal |
| Item | A thing in a location or in a bag, with a sid, a name, a description, actions and a value. | thing (for an item), treasure |
| Item sid | The identifier of an item, in the same digit form as a player sid. | item id |
| Action | One of `pick`, `drop`, `open`, `close`, `use`. On the wire, `pick` is the action that messages call TAKE. | verb |
| Command | One request of a player to the game: a move, a look, an item action, a chat message, a save or a quit. | action (for this idea), turn |
| Take | The `pick` action: move an item from the location into the bag. | pick up, grab, collect |
| Bag | The items a player carries, the gold, the score, and on its own route the energy. | inventory, backpack |
| Slot | One place in the bag. One slot holds up to 3 items with the same name. A bag has 8 slots. | space, cell |
| Gold | Coins a player finds. Gold is a number in the bag, not an item. | coins, money |
| Value | The points an item adds to the score while it is in the bag. | worth, price, points |
| Score | Gold plus the value of each item in the bag. | points, total |
| Energy | The strength a player needs to move. One move costs 1. | stamina, health, HP |
| Move count | The number of commands a player has carried out: moves, item actions and chat messages. On the wire: `moves`. | turns, steps |
| Win | Entering the katacombs exit. After a win the player can't move or act on items. | finish, complete |
| Finished game | The record of a win: name, score, move count. | high score (for this idea), game result |
| Leaderboard | The list of finished games since the server started, highest score first. | high scores, ranking |
| High-score line | One line that a win appends to the high-score file, for the marketing job. | leaderboard entry |
| Save | A copy of a player's state, written on request, that a restart reads back. | snapshot (for this idea), checkpoint |
| Snapshot | A copy of a player's state, written into the account when the player quits. | save (for this idea) |
| Chat message | A text one player sends to the players at the same location. | message (alone), chat post |
| Response message | The `message` text of a command's response or of an error. | chat (for this idea) |
| Database file | The SQLite file that holds the saves and the accounts: `KATACOMBS_DB`, else `katacombs.db`. | database (alone), DB |
| High-score file | The file of high-score lines: `KATACOMBS_HIGHSCORES`, else `highscores.jsonl`. | scores file |
| Error reason | The kind of an error: `INVALID_REQUEST`, `INVALID_VALUE`, `NOT_FOUND`, `NOT_ALLOWED`. Each has one HTTP status. Not sent on the wire today. | error type, error code |

## Data ownership

| Dataset | Writer | Readers |
| --- | --- | --- |
| The fixed world (`brown_field/spec/world.json`): the start, each location and item, the slide | nobody at run time: the specification | game-server (start), the tests |
| World state: items per location, open items, locked items, exits | game-server | game-server, every client through the API |
| Player state: location, bag, gold, energy, move count, visited, opened, won | game-server | game-server, every client through the API |
| Saves (SQLite table `saves` in the file `KATACOMBS_DB`) | game-server (save) | game-server (start) |
| Accounts with snapshots (SQLite table `accounts` in `KATACOMBS_DB`) | game-server (register, login, quit) | game-server (start, login) |
| Leaderboard (in memory) | game-server (win) | clients through `GET /leaderboard` |
| High-score file (`KATACOMBS_HIGHSCORES`, JSON lines) | game-server (win) | the nightly marketing job, outside this repository |
| Chat log (in memory) | game-server (send) | clients through `GET /player/{playerSid}/chat` |
| Player sid in the browser (`katacombs.sid`) | web client | web client |

No dataset has two writers across units. Inside game-server, both
`game.py` and `api.py` write the player and world state (see the
assessment); that is an internal finding, not a boundary one.

## Rules

### Players

#### PLAYER-1 — Starting a game creates a player at Brick Lane

- Status: observed. The code does it; nobody has decided it (2026-11-25).
- Source: legacy code (game.py:544-556, api.py:126-128); brief, "Game Start".
- Rule: When a client starts a game with a valid name, Katacombs shall
  create a player at BRICK LANE and respond with the player.
- Why: each game has its own player, and every game starts at the same location.
- Observable result: status 201. A Player with a new player sid,
  `location.title` `BRICK LANE`, an empty bag with gold 0, `hasWon` false,
  and energy 12. The new sid is unique: it is the sid of no active player
  and of no item (game.py:480-488).

#### PLAYER-2 — A name is trimmed and upper case

- Status: observed. The code does it; nobody has decided it (2026-11-25).
- Source: legacy code (game.py:545, game.py:784).
- Rule: When a client gives a name for a player or an account, Katacombs
  shall keep the name without leading or trailing spaces, in upper case.
- Why: A guess: names show in the game's upper-case style, and `ana` and `ANA` are one name.
- Observable result: the name `  ana ` comes back as `ANA`.

#### PLAYER-3 — A name has 1 to 50 characters

- Status: observed. The code does it; nobody has decided it (2026-11-25).
- Source: legacy code (game.py:17, game.py:546-547, game.py:785-786).
- Rule: If a trimmed name has fewer than 1 or more than 50 characters, then
  Katacombs shall refuse the request and create nothing.
- Why: A guess: an empty name can't show, and a long one breaks the display.
- Observable result: status 400, error reason `INVALID_VALUE`, message
  `THE NAME MUST HAVE 1 TO 50 CHARACTERS.`

#### PLAYER-4 — The name ADMIN is reserved

- Status: observed. The code does it; nobody has decided it (2026-11-25).
- Source: legacy code (game.py:19, game.py:548-549, game.py:787-788).
- Rule: If a trimmed, upper-case name is `ADMIN`, then Katacombs shall
  refuse the request and create nothing.
- Why: A guess: a player must not pass for the staff in the chat or on the leaderboard.
- Observable result: status 400, error reason `INVALID_VALUE`, message
  `THIS NAME IS RESERVED.`

#### PLAYER-5 — At most 20 players are active

- Status: observed. The code does it; nobody has decided it (2026-11-25).
- Source: legacy code (game.py:18, game.py:550-551, game.py:808-809).
- Rule: If 20 players are active when a client starts a game or logs in to
  an account without an active player, then Katacombs shall refuse the
  request.
- Why: A guess: one server holds every game in memory.
- Observable result: status 405, error reason `NOT_ALLOWED`, message
  `THE KATACOMBS ARE FULL. TRY AGAIN LATER.`

#### PLAYER-6 — A client can list the active players

- Status: observed. The code does it; nobody has decided it (2026-11-25).
- Source: legacy code (game.py:562-563, api.py:130-132).
- Rule: When a client lists the players, Katacombs shall respond with every
  active player.
- Why: a client can see who else is in the game.
- Observable result: status 200. An array of Player, each with its energy.

#### PLAYER-7 — Quitting removes the player

- Status: observed. The code does it; nobody has decided it (2026-11-25).
- Source: legacy code (game.py:570-578, api.py:134-137).
- Rule: When a player quits, Katacombs shall remove the player from the game.
- Why: a quit ends the game and lets another player start (PLAYER-5).
- Observable result: status 200, body `{"message": "Game Over"}`. A later
  request with that player sid gets PLAYER-9.

#### PLAYER-8 — A quitting player leaves the bag behind

- Status: observed. The code does it; nobody has decided it (2026-11-25).
- Source: legacy code (game.py:577).
- Rule: When a player quits, Katacombs shall put each item of the player's
  bag into the player's location.
- Why: A guess: items stay in the world for the other players.
- Observable result: another player at that location sees the items in
  the location. The gold is not left behind.

#### PLAYER-9 — An unknown player sid is not found

- Status: observed. The code does it; nobody has decided it (2026-11-25).
- Source: legacy code (game.py:490-493, api.py:111-112).
- Rule: If a request names a player sid that is not active, then Katacombs
  shall refuse the request.
- Why: the player quit, never existed, or was lost in a restart without a save.
- Observable result: status 404, error reason `NOT_FOUND`, message
  `PLAYER <sid> NOT FOUND.`

### The world

#### WORLD-1 — The game is played in the world of world.json

- Status: observed. The code does it; nobody has decided it (2026-11-25).
- Source: legacy code (game.py:34-69, game.py:135-301, game.py:408-412);
  characterized into `brown_field/spec/world.json`, with its schema
  `brown_field/spec/world.schema.json`.
- Rule: Katacombs shall start each game in the world that
  `brown_field/spec/world.json` describes: each location with its title,
  description, exits, items and gold, and each item with its sid, name,
  description, actions, value, gold inside and lock.
- Why: the world is the content of the game. Saves, the golden files, the
  high-score file and the mobile client v1 refer to its titles and its item
  sids, so a changed world breaks them.
- Observable result: a look around in each location shows the title,
  description, exits (in this order) and items of `world.json`; a look in
  each direction shows the location that `exits` names; the first visit
  adds the location's `gold`; `GET /items/{sid}` answers the item of
  `world.json` for each sid.

#### WORLD-2 — Each exit has a way back, except the slide from the cellar

- Status: accepted. Kept on purpose; see decision 0009.
- Source: legacy code (game.py:50-52, game.py:297-299, game.py:304-313,
  game.py:417), "Product asked for a slide from the cellar into the
  tunnels (2022)".
- Rule: Katacombs shall give each exit of a location a way back in the
  opposite direction, except each exit in `oneWayExits` of `world.json`:
  the slide `down` from BREWERY CELLAR.
- Why: Product asked for the slide in 2022. The way back keeps a player
  from being trapped. At start, the code refuses a world with a repeated
  title or a missing way back.
- Observable result: from BREWERY CELLAR, `down` leads to OLD TUBE TUNNEL,
  and `up` from OLD TUBE TUNNEL leads to RAILWAY ARCHES, not to the cellar.
  For every other exit, a look in the opposite direction from the target
  shows the location the player came from.

### Looking

#### LOOK-1 — A player can look around

- Status: observed. The code does it; nobody has decided it (2026-11-25).
- Source: legacy code (game.py:600-601, api.py:199-201); brief, `LOOK`.
- Rule: When a player looks around, Katacombs shall respond with the
  player's location.
- Why: the player needs the description, the exits and the items to choose
  the next command.
- Observable result: status 200. A Location: title, description, exits,
  items, and `isExit`.

#### LOOK-2 — A player can look in a direction without moving

- Status: observed. The code does it; nobody has decided it (2026-11-25).
- Source: legacy code (game.py:608-613, api.py:203-207); brief, `LOOK [direction]`.
- Rule: When a player looks in a direction that is one of the exits,
  Katacombs shall respond with the location in that direction and keep the
  player where the player is.
- Why: A guess: a player can check a location before spending energy on it.
- Observable result: status 200 and the Location in that direction. The
  energy and the move count do not change, and no gold is added.

#### LOOK-3 — Looking where there is no exit is refused

- Status: observed. The code does it; nobody has decided it (2026-11-25).
- Source: legacy code (game.py:611-612).
- Rule: If a player looks in a direction that is not one of the exits, then
  Katacombs shall refuse the request.
- Why: there is nothing to show.
- Observable result: status 405, error reason `NOT_ALLOWED`, message
  `THERE IS NOTHING IN THAT DIRECTION.`

### Moving

#### MOVE-1 — A player moves through an exit

- Status: observed. The code does it; nobody has decided it (2026-11-25).
- Source: legacy code (game.py:620-644, api.py:209-214); brief, `GO`.
- Rule: When a player moves in a direction that is one of the exits,
  Katacombs shall put the player in the location in that direction and
  respond with that location.
- Why: moving is how a player explores.
- Observable result: status 200 and the new Location. A later look around
  shows the same location.

#### MOVE-2 — A move costs 1 energy

- Status: observed. The code does it; nobody has decided it (2026-11-25).
- Source: legacy code (game.py:20, game.py:631).
- Rule: When a player moves through an exit, Katacombs shall lower the
  player's energy by 1.
- Why: A guess: energy limits how far a player goes without food or drink. Not in the brief.
- Observable result: after one move from the start, the bag shows energy 11.

#### MOVE-3 — A move adds one to the move count

- Status: observed. The code does it; nobody has decided it (2026-11-25).
- Source: legacy code (game.py:632).
- Rule: When a player moves through an exit, Katacombs shall add one to the
  player's move count.
- Why: the leaderboard shows how many commands a win took.
- Observable result: the finished game of a win shows the move count.

#### MOVE-4 — Moving where there is no exit is refused

- Status: observed. The code does it; nobody has decided it (2026-11-25).
- Source: legacy code (game.py:626-627).
- Rule: If a player moves in a direction that is not one of the exits, then
  Katacombs shall refuse the move.
- Why: locations connect only through their exits.
- Observable result: status 405, error reason `NOT_ALLOWED`, message
  `YOU CAN'T GO THAT WAY.` Energy and move count do not change.

#### MOVE-5 — A player with no energy can't move

- Status: contested. Open question: The gate is in the REST route only: the move port lets the energy go below 0, and the client stops at 1 (WEB-MOVE-2). Where does the rule belong, and is the limit 0 or 1?
- Source: legacy code (api.py:210-213, "Added for the mobile release").
- Rule: If a player with an energy of 0 or less moves, then Katacombs shall
  refuse the move.
- Why: A guess: energy is the cost of moving; food and drink restore it.
- Observable result: status 405, error reason `NOT_ALLOWED`, message
  `YOU ARE TOO TIRED TO MOVE. EAT OR DRINK SOMETHING.` This check comes
  before every other move check, the win included.

#### MOVE-6 — The market is closed for cleaning in the last ten minutes of each hour

- Status: accepted (decision 0001). Kept on purpose, as the code does it.
- Source: legacy code (game.py:316-319, game.py:629-630, "Cleaning crew contract (2023)").
- Rule: While the server's local time is in minutes 50 to 59 of an hour,
  when a player moves into SPITALFIELDS MARKET, Katacombs shall refuse the
  move.
- Why: a cleaning contract closes the market. Not in the brief.
- Observable result: status 405, error reason `NOT_ALLOWED`, message
  `THE MARKET IS CLOSED FOR CLEANING. COME BACK LATER.` Energy and move
  count do not change.

#### MOVE-7 — A player who has won can't move

- Status: observed. The code does it; nobody has decided it (2026-11-25).
- Source: legacy code (game.py:623-624).
- Rule: If a player who has won moves, then Katacombs shall refuse the move.
- Why: the game is over.
- Observable result: status 405, error reason `NOT_ALLOWED`, message
  `THE GAME IS OVER. YOU ALREADY FOUND THE EXIT.`

#### MOVE-8 — A rat in the cellar can steal an item without value

- Status: observed. The code does it; nobody has decided it (2026-11-25).
- Source: legacy code (game.py:22, game.py:633-635, game.py:646-654).
- Rule: When a player enters BREWERY CELLAR with an item of value 0 in the
  bag, Katacombs shall move one such item to OLD TUBE TUNNEL with a chance
  of 1 in 5.
- Why: A guess: a flavour event. It never takes an item with value, so it never
  lowers the score. Not in the brief.
- Observable result: the location description ends with
  `A RAT RUNS OFF WITH YOUR <NAME>.`; the item is gone from the bag and lies
  in OLD TUBE TUNNEL.

### Gold, score and the bag

#### GOLD-1 — The first visit to a location adds its gold

- Status: observed. The code does it; nobody has decided it (2026-11-25).
- Source: legacy code (game.py:500-504); brief, "Gold Collection".
- Rule: When a player enters a location for the first time, Katacombs shall
  add the gold of that location to the player's bag.
- Why: exploring is rewarded once per location, per player.
- Observable result: after the first move into OLD TRUMAN BREWERY the bag
  shows gold 5. A second visit adds nothing.

#### GOLD-2 — The first opening of an item with gold adds its gold

- Status: observed. The code does it; nobody has decided it (2026-11-25).
- Source: legacy code (game.py:410, game.py:702-708); brief, "Gold Collection".
- Rule: When a player opens an item that holds gold for the first time,
  Katacombs shall add that gold to the player's bag.
- Why: opening is rewarded once per item, per player.
- Observable result: response message `OPENED. YOU FIND 10 GOLD.` for the
  CRATE; the bag gold grows by 10. A later opening by the same player
  answers `OPENED.`

#### BAG-1 — A player can inspect the bag

- Status: observed. The code does it; nobody has decided it (2026-11-25).
- Source: legacy code (game.py:592-593, api.py:147-150); brief, `BAG`.
- Rule: When a player inspects the bag, Katacombs shall respond with the
  items, the gold, the score and the energy.
- Why: the player sees what they carry and how strong they are.
- Observable result: status 200. A Bag with `items`, `gold`, `score` and
  `energy`.

#### BAG-2 — The score is the gold plus the item values

- Status: observed. The code does it; nobody has decided it (2026-11-25).
- Source: legacy code (kata.py:39-41); brief, "get a score from the value of the treasures".
- Rule: Katacombs shall compute the score as the gold plus the value of
  each item in the bag.
- Why: treasures and gold both count for the leaderboard.
- Observable result: with gold 35 and the GOBLET (value 50), the score is 85.

#### BAG-3 — The bag holds 8 slots of up to 3 items with the same name

- Status: contested. Open question: The brief says 10 items; the code has 8 slots of 3 items with one name. Which is the rule?
- Source: legacy code (game.py:15-16, game.py:322-323, game.py:681-682). The brief says "max 10 in bag"; the code differs.
- Rule: If a player takes an item and the bag would then need more than 8
  slots, where one slot holds up to 3 items with the same name, then
  Katacombs shall refuse the take.
- Why: unknown; the limit changed from the brief's 10 items without a record.
- Observable result: status 405, error reason `NOT_ALLOWED`, message
  `YOUR BAG IS FULL.` The item stays in the location.

### Items

#### ITEM-1 — A client can inspect an item

- Status: observed. The code does it; nobody has decided it (2026-11-25).
- Source: legacy code (game.py:584-585, api.py:143-145); brief, `LOOK [item]`.
- Rule: When a client asks for an item by its item sid, Katacombs shall
  respond with the item.
- Why: a client can show an item's description and the actions it allows.
- Observable result: status 200. An Item: sid, name, description,
  actions, value. No player is needed.

#### ITEM-2 — An unknown item sid is not found

- Status: observed. The code does it; nobody has decided it (2026-11-25).
- Source: legacy code (game.py:495-498).
- Rule: If a request names an item sid that does not exist, then Katacombs
  shall refuse the request.
- Why: there is no such item.
- Observable result: status 404, error reason `NOT_FOUND`, message
  `ITEM <sid> NOT FOUND.` This check comes before the player's win and the
  item's location.

#### ACT-1 — An item must be here or in the bag

- Status: observed. The code does it; nobody has decided it (2026-11-25).
- Source: legacy code (game.py:668-670).
- Rule: If a player acts on an item that is neither in the player's location
  nor in the bag, then Katacombs shall refuse the action.
- Why: a player can only reach what is near.
- Observable result: status 404, error reason `NOT_FOUND`, message
  `THERE IS NO <NAME> HERE.`

#### ACT-2 — An item allows only its own actions

- Status: observed. The code does it; nobody has decided it (2026-11-25).
- Source: legacy code (game.py:671-672).
- Rule: If a player asks an item for an action that the item does not
  allow, then Katacombs shall refuse the action.
- Why: each item lists its actions, for example a CRATE can't be taken.
- Observable result: status 405, error reason `NOT_ALLOWED`, message
  `YOU CAN'T <ACTION> THE <NAME>.`, with the action in upper case
  (`PICK`, `DROP`, `OPEN`, `CLOSE`, `USE`).

#### ACT-3 — A player who has won can't act on items

- Status: observed. The code does it; nobody has decided it (2026-11-25).
- Source: legacy code (game.py:664-665).
- Rule: If a player who has won acts on an item, then Katacombs shall refuse
  the action.
- Why: the game is over.
- Observable result: status 405, error reason `NOT_ALLOWED`, message
  `THE GAME IS OVER. YOU ALREADY FOUND THE EXIT.`

#### ACT-4 — Taking moves an item into the bag

- Status: observed. The code does it; nobody has decided it (2026-11-25).
- Source: legacy code (game.py:676-685); brief, `TAKE`.
- Rule: When a player takes an item from the location, Katacombs shall move
  the item into the bag.
- Why: a player collects treasures and tools.
- Observable result: status 200, body `{"message": "TAKEN."}`. The item
  is in the bag and gone from the location.

#### ACT-5 — Taking an item already in the bag succeeds again

- Status: accepted (decision 0004). Kept on purpose, as the code does it.
- Source: legacy code (game.py:677-680, "INC-2231").
- Rule: When a player takes an item that is already in the bag, Katacombs
  shall answer that it is taken and change nothing.
- Why: a client on a slow network sends the take twice, and players saw an error.
- Observable result: status 200, body `{"message": "TAKEN."}`. The bag is
  unchanged.

#### ACT-6 — Dropping moves an item into the location

- Status: observed. The code does it; nobody has decided it (2026-11-25).
- Source: legacy code (game.py:687-692); brief, `DROP`.
- Rule: When a player drops an item from the bag, Katacombs shall move the
  item into the location.
- Why: a player frees a slot, or leaves an item for others.
- Observable result: status 200, body `{"message": "DROPPED."}`.

#### ACT-7 — A player can only drop or use an item in the bag

- Status: observed. The code does it; nobody has decided it (2026-11-25).
- Source: legacy code (game.py:688-689, game.py:720-721).
- Rule: If a player drops or uses an item that is not in the bag, then
  Katacombs shall refuse the action.
- Why: the player must carry the item.
- Observable result: status 405, error reason `NOT_ALLOWED`, message
  `YOU ARE NOT CARRYING THE <NAME>.`

#### ACT-8 — Opening an item opens it for everyone

- Status: observed. The code does it; nobody has decided it (2026-11-25).
- Source: legacy code (game.py:694-710); brief, `OPEN`.
- Rule: When a player opens a closed, unlocked item, Katacombs shall mark the
  item open for every player.
- Why: A guess: open and closed belong to the world, not to one player.
- Observable result: status 200, body `{"message": "OPENED."}` (or the
  GOLD-2 message). Another player who opens it gets ACT-9.

#### ACT-9 — Opening an open item is refused

- Status: observed. The code does it; nobody has decided it (2026-11-25).
- Source: legacy code (game.py:695-696).
- Rule: If a player opens an item that is open, then Katacombs shall refuse
  the action.
- Why: nothing to do.
- Observable result: status 405, error reason `NOT_ALLOWED`, message
  `THE <NAME> IS ALREADY OPEN.`

#### ACT-10 — Opening a locked item is refused

- Status: observed. The code does it; nobody has decided it (2026-11-25).
- Source: legacy code (game.py:412, game.py:697-698).
- Rule: If a player opens an item that is locked, then Katacombs shall
  refuse the action.
- Why: the MANHOLE starts locked; the KEY unlocks it (ACT-14).
- Observable result: status 405, error reason `NOT_ALLOWED`, message
  `THE <NAME> IS LOCKED.`

#### ACT-11 — Closing an item closes it for everyone

- Status: observed. The code does it; nobody has decided it (2026-11-25).
- Source: legacy code (game.py:711-717); brief, `CLOSE`.
- Rule: When a player closes an open item, Katacombs shall mark the item
  closed for every player.
- Why: A guess: open and closed belong to the world.
- Observable result: status 200, body `{"message": "CLOSED."}`.

#### ACT-12 — Closing a closed item is refused

- Status: observed. The code does it; nobody has decided it (2026-11-25).
- Source: legacy code (game.py:712-713).
- Rule: If a player closes an item that is closed, then Katacombs shall
  refuse the action.
- Why: nothing to do.
- Observable result: status 405, error reason `NOT_ALLOWED`, message
  `THE <NAME> IS ALREADY CLOSED.`

#### ACT-13 — The open manhole connects the back yard and the katacombs

- Status: observed. The code does it; nobody has decided it (2026-11-25).
- Source: legacy code (game.py:700-701, game.py:715-716, game.py:506-512).
- Rule: While the MANHOLE is open, Katacombs shall show `down` among the
  exits of BACK YARD, leading to KATACOMBS, and `up` among the exits of
  KATACOMBS, leading back.
- Why: A guess: the manhole is the short way to the katacombs exit. Closing it
  removes both exits, for every player.
- Observable result: a look around in BACK YARD shows `down` while the
  MANHOLE is open, and not while it is closed.

#### ACT-14 — The key unlocks the manhole in the back yard

- Status: observed. The code does it; nobody has decided it (2026-11-25).
- Source: legacy code (game.py:722-726).
- Rule: When a player uses the KEY in BACK YARD while the MANHOLE is
  locked, Katacombs shall unlock the MANHOLE for every player.
- Why: the key is the puzzle on the short way to the exit.
- Observable result: status 200, body `{"message": "YOU UNLOCK THE MANHOLE COVER."}`.
  When it is already unlocked: `{"message": "THE MANHOLE COVER IS ALREADY UNLOCKED."}`.

#### ACT-15 — Bread and beer restore energy

- Status: observed. The code does it; nobody has decided it (2026-11-25).
- Source: legacy code (game.py:21, game.py:71, game.py:727-732).
- Rule: When a player uses a BREAD or a BEER from the bag, Katacombs shall
  remove it from the bag and raise the energy by 5 for BREAD or by 3 for
  BEER, to at most 20.
- Why: A guess: energy (MOVE-2) needs a way back up.
- Observable result: status 200, body `{"message": "YOU EAT THE BREAD. YOU FEEL STRONGER."}`
  or `{"message": "YOU DRINK THE BEER. YOU FEEL BRAVE."}`. The bag shows the
  new energy and no longer holds the item.

#### ACT-16 — Using any other item does nothing

- Status: observed. The code does it; nobody has decided it (2026-11-25).
- Source: legacy code (game.py:733).
- Rule: When a player uses an item from the bag that has no use at that
  location, Katacombs shall answer that nothing happens.
- Why: a use outside its location has no effect.
- Observable result: status 200, body `{"message": "NOTHING HAPPENS."}`.
  For example, the KEY anywhere but BACK YARD.

#### ACT-17 — An item action adds one to the move count

- Status: contested. Open question: Should a refused or a repeated item action count as a move? It changes the leaderboard.
- Source: legacy code (game.py:674).
- Rule: When a player's item action passes the checks of ITEM-2, ACT-3,
  ACT-1 and ACT-2, Katacombs shall add one to the move count, even if the
  action is then refused or changes nothing.
- Why: unknown. A repeated take (ACT-5) and a refused open (ACT-9) both
  count.
- Observable result: the move count of a later finished game includes these
  actions.

### Winning and the leaderboard

#### WIN-1 — Entering the katacombs exit wins the game

- Status: observed. The code does it; nobody has decided it (2026-11-25).
- Source: legacy code (game.py:637-638); brief, "find KATACOMBS EXIT to win".
- Rule: When a player enters KATACOMBS EXIT, Katacombs shall mark the
  player as having won.
- Why: finding the way out is the aim of the game.
- Observable result: the Location has `isExit` true; the Player in the
  list of players has `hasWon` true.

#### WIN-2 — A win adds a finished game to the leaderboard

- Status: observed. The code does it; nobody has decided it (2026-11-25).
- Source: legacy code (game.py:639-643); brief, "Leaderboard".
- Rule: When a player wins, Katacombs shall add a finished game with the
  player's name, score and move count to the leaderboard.
- Why: players compare their wins.
- Observable result: `GET /leaderboard` holds `{"name", "score", "moves"}`
  for the win. The leaderboard is empty after a restart.

#### WIN-3 — A win appends a high-score line for marketing

- Status: accepted (decision 0002). Kept on purpose, as the code does it.
- Source: legacy code (game.py:326-335, game.py:640, "The marketing leaderboard reads this file every night. Keep the format.").
- Rule: When a player wins, Katacombs shall append one high-score line with
  the player's name, the score and the time of the win to the high-score
  file.
- Why: a nightly marketing job outside this repository reads the file.
- Observable result: the file named by `KATACOMBS_HIGHSCORES` (default
  `highscores.jsonl`) gains one line that matches
  `highscore-line.schema.json`.

#### BOARD-1 — The leaderboard ranks the highest score first

- Status: observed. The code does it; nobody has decided it (2026-11-25).
- Source: legacy code (api.py:139-141); brief, "ranked by score, highest first".
- Rule: When a client reads the leaderboard, Katacombs shall respond with
  the finished games, highest score first, and equal scores in the order of
  their wins.
- Why: the best wins show first.
- Observable result: status 200, an array of FinishedGame in that order.

### Saving

#### SAVE-1 — A player can save the game

- Status: contested. Open question: Should the save answer name the server's file path? It shows the server's file system to every client.
- Source: legacy code (game.py:742-773, api.py:152-155, "INC-3110: a laptop sleep lost every bag").
- Rule: When a player saves, Katacombs shall store a copy of the player's
  state that a restart reads back.
- Why: a restart of the server lost every bag.
- Observable result: status 200, body `{"message": "GAME SAVED.", "path": "<file path>"}`.
  The path is the server's database file.

#### SAVE-2 — A restart brings saved players back, but not the world

- Status: contested. Open question: Should a restart restore the world? Today an item saved in a bag also comes back in its location, and a save from before 2023 stops the server from starting.
- Source: legacy code (game.py:448-478, "The world is not in the save. Nobody wrote down why.").
- Rule: When the server starts, Katacombs shall make each saved player
  active again with the saved location, bag, gold, energy, move count,
  visited locations, opened items and win.
- Why: unknown for the world. The open, closed and locked items, and the
  items in the locations, start fresh.
- Observable result: after a restart, the saved player sid works and shows
  the saved state. A save that names a location that no longer exists is
  skipped. The saved players come back in the order of their `saved_at`,
  so `GET /game/player` lists them in the order they saved (game.py:458).

### Accounts

#### ACCOUNT-1 — A client can register an account

- Status: observed. The code does it; nobody has decided it (2026-11-25).
- Source: legacy code (game.py:779-792, api.py:157-160).
- Rule: When a client registers with an email, a password and a valid name,
  Katacombs shall create an account.
- Why: an account lets a person come back to their game.
- Observable result: status 201, body `{"email": "<email>", "name": "<NAME>"}`.

#### ACCOUNT-2 — An email needs an @

- Status: observed. The code does it; nobody has decided it (2026-11-25).
- Source: legacy code (game.py:780-781).
- Rule: If a client registers with an email that has no `@`, then Katacombs
  shall refuse the registration.
- Why: A guess: a minimal check that the email is an email.
- Observable result: status 400, error reason `INVALID_VALUE`, message
  `THE EMAIL IS NOT VALID.` This check comes before the name checks. It is
  the only check of the email: `ana@example@org` registers.

#### ACCOUNT-3 — An email has one account

- Status: observed. The code does it; nobody has decided it (2026-11-25).
- Source: legacy code (game.py:782-783).
- Rule: If a client registers with an email that has an account, then
  Katacombs shall refuse the registration.
- Why: the email identifies the account.
- Observable result: status 405, error reason `NOT_ALLOWED`, message
  `THIS EMAIL IS TAKEN.`

#### ACCOUNT-4 — Logging in gives the account's player

- Status: contested. Open question: Should a later login restore the snapshot again? Today a second login after a quit rolls the active player back.
- Source: legacy code (game.py:799-830, api.py:162-164).
- Rule: When a client logs in with the email and password of an account,
  Katacombs shall respond with the account's player: the snapshot of its
  last quit, else its active player, else a new player at BRICK LANE.
- Why: a person resumes their game from any client.
- Observable result: status 200, a Player with its energy. A snapshot
  whose location is not in the world is not restored: the login gives the
  active player, else a new player at BRICK LANE (game.py:805). A login
  that restores a snapshot while 20 players are active, and the account's
  player is not one of them, is refused with status 405 and the message
  `THE KATACOMBS ARE FULL. TRY AGAIN LATER.` (game.py:808-809).

#### ACCOUNT-5 — A wrong email or password is refused

- Status: observed. The code does it; nobody has decided it (2026-11-25).
- Source: legacy code (game.py:802-803).
- Rule: If a client logs in with an email that has no account, or with a
  wrong password, then Katacombs shall refuse the login.
- Why: A guess: only the owner of an account gets its player. One message for both
  cases does not tell which emails exist.
- Observable result: status 405, error reason `NOT_ALLOWED`, message
  `WRONG EMAIL OR PASSWORD.`

#### ACCOUNT-6 — Quitting with an account keeps a snapshot

- Status: contested. Open question: Should the snapshot be cleared once it is restored? See ACCOUNT-4.
- Source: legacy code (game.py:572-575, game.py:805-819).
- Rule: When a player of an account quits, Katacombs shall keep a snapshot
  of the player's state in the account.
- Why: A guess: the next login resumes the game where the person left it.
- Observable result: a login after the quit gives a player with the same
  location, bag, gold, energy and move count.

### Chat

#### CHAT-1 — A player can send a chat message

- Status: contested. Open question: Should an empty chat message be accepted? The client never sends one (WEB-CHAT-3), and the log has no length limit.
- Source: legacy code (api.py:166-173).
- Rule: When a player sends a chat message, Katacombs shall store it with
  the player's name, the player's location and the time.
- Why: players at the same location can talk.
- Observable result: status 201, body `{"message": "SENT."}`. An empty text
  is accepted.

#### CHAT-2 — A player reads the chat messages of the location

- Status: observed. The code does it; nobody has decided it (2026-11-25).
- Source: legacy code (api.py:175-182).
- Rule: When a player reads the chat, Katacombs shall respond with the chat
  messages that were sent from the player's present location, oldest first.
- Why: A guess: the chat belongs to the location, like a conversation between people who stand together.
- Observable result: status 200, an array of ChatMessage: `name`, `text`,
  `at`. A message stays with the location it was sent from.

#### CHAT-3 — A chat message adds one to the move count

- Status: contested. Open question: Should a chat message count as a move? It changes the leaderboard.
- Source: legacy code (api.py:173).
- Rule: When a player sends a chat message, Katacombs shall add one to the
  player's move count.
- Why: unknown.
- Observable result: the move count of a later finished game includes the
  chat messages.

### The API

#### API-1 — A malformed request is refused

- Status: observed. The code does it; nobody has decided it (2026-11-25).
- Source: legacy code (api.py:119-121).
- Rule: If a request has a missing or mistyped field, or a direction or an
  action that does not exist, then Katacombs shall refuse the request.
- Why: A guess: one error format for every client, instead of the framework's 422.
- Observable result: status 400, error reason `INVALID_REQUEST`, message
  `INVALID REQUEST.`

#### API-2 — Every error has a status and a message

- Status: contested. Open question: Should a game refusal answer 405, which HTTP keeps for a wrong method? Should a URL that is not a route answer the game's error body?
- Source: legacy code (api.py:95-117).
- Rule: Katacombs shall answer each refused request on a game route with a
  body that holds the HTTP status as `code` and an upper-case `message`.
- Why: A guess: clients show the message to the player as it is.
- Observable result: body `{"code": <status>, "message": "<TEXT>"}`, where
  the status is the one of the error reason (see `x-status-by-reason` in
  `openapi.yaml`). A URL that is not a route answers with the framework's
  `{"detail": ...}` instead.

### Data at rest, configuration and start

These rules hold a boundary with stored data and with the people who run
the server. Real saves and accounts live in the database file; a server
of another version must read them.

#### STORE-1 — The database file holds a saves table with fixed columns

- Status: accepted (decision 0005). Kept on purpose, as the code does it.
- Source: legacy code (game.py:338-345, game.py:757-768).
- Rule: When a player saves, Katacombs shall write one row per player to
  the table `saves` of the database file, with the text columns
  `player_sid`, `name`, `payload` and `saved_at`.
- Why: a start of the server reads this table back (SAVE-2), so its shape
  is a contract with every save already written.
- Observable result: the table has those four columns. The row of a saved
  player holds the player sid, the name, a payload that matches
  `player-state.schema.json`, and the time in UTC to the second, for
  example `2026-11-25T11:11:46+00:00`. A second save replaces the row.

#### STORE-2 — The database file holds an accounts table with fixed columns

- Status: accepted (decision 0005). Kept on purpose, as the code does it.
- Source: legacy code (game.py:353-361, game.py:386-403).
- Rule: When a client registers, logs in or quits with an account,
  Katacombs shall keep one row per account in the table `accounts` of the
  database file, with the text columns `email`, `password_hash`, `name`,
  `player_sid` and `snapshot`.
- Why: accounts must survive a restart and a new version of the server.
- Observable result: the table has those five columns. After the
  registration, `player_sid` and `snapshot` are empty; after the first
  login `player_sid` holds the player sid; after a quit `snapshot` holds a
  payload that matches `player-state.schema.json`.

#### STORE-3 — A password is stored as an unsalted SHA-256 digest

- Status: contested. Open question: Unsalted SHA-256, with a TODO for bcrypt since 2023: how do the stored accounts move to a stronger hash?
- Source: legacy code (game.py:368-370, "TODO: bcrypt (2023)").
- Rule: When a client registers an account, Katacombs shall store the
  password as the lower-case hex SHA-256 digest of its UTF-8 bytes, with
  no salt.
- Why: unknown; the TODO says a stronger hash was planned. Every stored
  account depends on this format: a server that hashes in another way can
  no longer log them in.
- Observable result: the password `golden-password` is stored as
  `f1b580fcec5d45d1ad840f4e3409d1c5ed1fa6fe8dae3ad0e70e923c67f131dd`. Two
  accounts with one password store the same value.

#### CONF-1 — The database file is KATACOMBS_DB, else katacombs.db

- Status: accepted (decision 0005). Kept on purpose, as the code does it.
- Source: legacy code (game.py:348-350, "The support laptop sets KATACOMBS_DB. Nobody else does.").
- Rule: Where the environment variable `KATACOMBS_DB` is set, Katacombs
  shall use its value as the path of the database file, and otherwise the
  path `katacombs.db` in the working directory.
- Why: the support laptop moves the file; everywhere else the default holds.
- Observable result: with the variable unset, a save creates `katacombs.db`
  in the working directory and the save answer names the path
  `katacombs.db`.

#### CONF-2 — The high-score file is KATACOMBS_HIGHSCORES, else highscores.jsonl

- Status: accepted (decision 0002). Kept on purpose, as the code does it.
- Source: legacy code (game.py:328).
- Rule: Where the environment variable `KATACOMBS_HIGHSCORES` is set,
  Katacombs shall append the high-score lines to the file it names, and
  otherwise to `highscores.jsonl` in the working directory.
- Why: the marketing job reads the file from a known place.
- Observable result: with the variable unset, a win creates
  `highscores.jsonl` in the working directory.

#### CONF-3 — The server listens on 127.0.0.1, port 8000

- Status: observed. The code does it; nobody has decided it (2026-11-25).
- Source: legacy code (__main__.py:6); web client (vite.config.ts:6).
- Rule: When a person runs `python -m brown_field`, Katacombs shall serve
  the REST API on the address 127.0.0.1, port 8000.
- Why: the web client's development proxy sends every `/api` request to
  that address.
- Observable result: while the process runs, `GET
  http://127.0.0.1:8000/leaderboard` answers 200. The server answers only
  on the local machine.

#### ENTRY-1 — create_app serves the game it is given

- Status: accepted (decision 0008). Kept on purpose, as the code does it.
- Source: legacy code (api.py:101-102).
- Rule: When code calls `create_app` with a game, Katacombs shall serve
  that game, and when it calls `create_app` with no game, Katacombs shall
  serve a new game that reads the files at its start.
- Why: tests and tools start a server on a game they hold; the README of
  the exercise names it an enabling point.
- Observable result: two servers made from one game list the same players.
  Two servers made with no game do not share players.

#### ENTRY-2 — The module brown_field.api holds a ready server named app

- Status: accepted (decision 0008). Kept on purpose, as the code does it.
- Source: legacy code (api.py:220, __main__.py:6).
- Rule: Katacombs shall offer a ready server as `app` in the module
  `brown_field.api`, made when the module is first imported.
- Why: `python -m brown_field` and any ASGI server start it by the name
  `brown_field.api:app`.
- Observable result: `brown_field.api.app` answers `GET /leaderboard` with
  200. It reads the database file once, at the import.

### Operations

#### OPS-1 — Each command responds in less than 100 ms at p99

- Status: accepted (decision 0007). Kept on purpose, as the code does it.
- Source: the workshop (brown_field/README.md:391-393).
- Rule: When a client sends a command, Katacombs shall respond in less
  than 100 ms at the 99th percentile, over 100 calls, measured in process.
- Why: players expect instant feedback.
- Observable result: a test sends 100 commands through the REST API in
  process, a mix of looks, the bag, moves, item actions, chat and a save,
  and the 99th percentile of their response times (nearest rank: the 99th
  of the 100 sorted times) is below 100 ms.

### Legacy

#### LEGACY-1 — The legacy pickup takes an item without the checks

- Status: accepted (decision 0003). Kept on purpose, as the code does it.
- Source: legacy code (api.py:188-197, "Mobile client v1 still calls this route. Do not remove it.").
- Rule: When a client calls the legacy pickup for an item in the player's
  location, Katacombs shall move the item into the bag without the bag
  limit, the win check or the move count.
- Why: mobile client v1 still calls it; the web client calls it too (quick
  pick). It is older than BAG-3, ACT-3 and ACT-17.
- Observable result: status 200, body `{"message": "OK"}`. The item is in
  the bag.

#### LEGACY-2 — The legacy pickup of an item elsewhere changes nothing

- Status: accepted (decision 0003). Kept on purpose, as the code does it.
- Source: legacy code (api.py:194-196).
- Rule: When a client calls the legacy pickup for an item that is not in
  the player's location, Katacombs shall answer OK and change nothing.
- Why: unknown.
- Observable result: status 200, body `{"message": "OK"}`. The bag and the
  location do not change.
