# Archaeology — what the legacy code knows

Step 1 of the exercise. A read of `game.py`, `api.py`, `kata.py` and
`web/src/` for each limit, timeout, retry, special case, magic number, and
comment about an old problem. The code was not changed.

**How this list was made.** The README asks for a separate, read-only agent
session. This list was written by the same agent session that wrote the
characterization tests afterwards. Each item therefore also names the
scenario that pins it. The reading of each item ("what it is for") is the
agent's.

**The marks are proposals for the group to confirm:**

- **known**: the brief or a comment in the code says why;
- **unknown**: nobody can say why;
- **wrong**: the game or the tests show that the reading is wrong.

The list of rules and of differences from the brief is the specification
itself (`spec/specification.md`, `web/spec/specification.md`).

## The server: game.py, api.py, kata.py

| # | File:line | What it is | What it is probably for | Sure? | Mark | Pinned by |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | game.py:15-16 | Bag of 8 slots, 3 items with one name per slot | Let players stack food and drink. The brief says "max 10 in bag". | a guess | unknown | BAG-3 |
| 2 | game.py:17 | Name of 1 to 50 characters | Fit the display and the storage | a guess | unknown | PLAYER-3 |
| 3 | game.py:18 | At most 20 active players, also at login (game.py:808) | Keep one in-memory server small | a guess | unknown | PLAYER-5 |
| 4 | game.py:19 | The name ADMIN is reserved | Stop a player from posing as the staff | a guess | unknown | PLAYER-4 |
| 5 | game.py:20-21, 71 | Energy: 12 at the start, 20 at most; BREAD +5, BEER +3 | A cost for moving. Not in the brief. | a guess | unknown | MOVE-2, ACT-15 |
| 6 | game.py:22, 646-654 | A 1-in-5 rat in the cellar takes an item with value 0 to the tube tunnel | A flavour event that never lowers the score | a guess | unknown | MOVE-8 |
| 7 | game.py:50-52 | The cellar slide goes down only: an exception to the way-back rule | "Product asked for a slide from the cellar into the tunnels (2022)" | sure | known | (no rule yet: a world rule) |
| 8 | game.py:154, 173, 183 | Item values: RING 20, GOBLET 50, SKULL 5 | The treasures of the brief | sure | known | BAG-2 |
| 9 | game.py:215, 223, 254, 261, 288 | Location gold: 5, 20, 10, 5, 30 | "Gold on the first visit" of the brief; the amounts are not in it | a guess | unknown | GOLD-1 |
| 10 | game.py:299-313 | The start fails on a repeated title or a connection with no way back | A world-integrity check at boot | sure | known | (no rule yet: a world rule) |
| 11 | game.py:316-319 | The market is closed in minutes 50 to 59 of each hour, local time | "Cleaning crew contract (2023)… Ask facilities before you change this." | sure | known | MOVE-6 |
| 12 | game.py:326-335 | Each win appends `{name, score, at}` to the high-score file | "The marketing leaderboard reads this file every night. Keep the format." | sure | known | WIN-3, CONF-2 |
| 13 | game.py:348-350 | `KATACOMBS_DB`, else `katacombs.db` in the working directory | "The support laptop sets KATACOMBS_DB. Nobody else does." | sure | known | CONF-1 |
| 14 | game.py:368-370 | Passwords as unsalted SHA-256 | "TODO: bcrypt (2023)": a known debt, never paid | sure | known | STORE-3 |
| 15 | game.py:410 | The CRATE holds 10 gold | The "gold in an item" of the brief; the amount is not in it | a guess | unknown | GOLD-2 |
| 16 | game.py:412 | The MANHOLE starts locked | The key puzzle on the short way | sure | known | ACT-10, ACT-14 |
| 17 | game.py:448-478 | A restart brings saved players back, but not the world | "The world is not in the save. Nobody wrote down why." | sure | unknown | SAVE-2 (contested: items duplicate) |
| 18 | game.py:466-468 | A save whose location no longer exists is skipped | "The world changed under an old save." | sure | known | SAVE-2 |
| 19 | game.py:470-474 | The start reads `energy` and `moves` with no default | Saves of before 2023 crash the start | sure | unknown | SAVE-2 (contested) |
| 20 | game.py:480-488 | Sids of 6-12-8 random digits, unique against players and items | Item sids share the format, so they must not collide | a guess | unknown | contract `Sid` |
| 21 | game.py:577 | A quit drops the whole bag at the location | Items stay in the world for others | a guess | unknown | PLAYER-8 |
| 22 | game.py:623-631 | The order of the move checks: won, exit, market, then the cost | A refused move costs nothing | a guess | unknown | MOVE-4, MOVE-6, MOVE-7 |
| 23 | game.py:674 | Each item action that passes the checks counts a move, even a refused open or a repeated take | "Moves" also counts actions | no idea | unknown | ACT-17 |
| 24 | game.py:676-680 | A take of an item already in the bag answers TAKEN. | "INC-2231: the mobile client sends TAKE again when the network is slow" | sure | known | ACT-5 |
| 25 | game.py:700-701, 715-716 | Opening the MANHOLE adds a way down for every player; closing it removes it | One player changes the map for all | a guess | unknown | ACT-13 |
| 26 | game.py:722-726 | The KEY works only in BACK YARD | The puzzle | sure | known | ACT-14, ACT-16 |
| 27 | game.py:737 | The save | "INC-3110: a laptop sleep lost every bag" | sure | known | SAVE-1 |
| 28 | game.py:754 | The save holds the energy and the move count | "2023: the payload also holds the energy and the move count" | sure | known | STORE-1 |
| 29 | game.py:804-819 | A login restores the snapshot of the last quit each time; the snapshot is never cleared | Resume after a quit; the rollback looks accidental | a guess | unknown | ACCOUNT-6 (contested: rollback) |
| 30 | api.py:111-117 | Not found 404, invalid name 400, refusal 405, other 500 | One status per error kind; 405 is not HTTP's meaning | a guess | unknown | API-2 |
| 31 | api.py:119-121 | A malformed request answers 400 "INVALID REQUEST.", not the framework's 422 | One error format for clients | a guess | unknown | API-1 |
| 32 | api.py:123-124, 150 | `energy` added to the player and the bag answers | The client shows the energy | a guess | unknown | BAG-1, contract |
| 33 | api.py:166-173 | A chat message is stored with the location; it counts a move; no length limit | Location chat; the move count looks accidental | no idea | unknown | CHAT-1, CHAT-3 |
| 34 | api.py:188-197 | The legacy pickup: no bag limit, no win check, no move count, OK when the item is not here | "Mobile client v1 still calls this route. Do not remove it." | sure | known | LEGACY-1, LEGACY-2 |
| 35 | api.py:210-213 | The energy gate: 405 at energy 0 or less, in the route, not in the use case | "Added for the mobile release" | sure | known | MOVE-5 (the port has no gate: contested) |
| 36 | api.py:220 | `app` made at the import, which reads the database file once | The name that uvicorn starts | sure | known | ENTRY-2 |
| 37 | __main__.py:6 | 127.0.0.1, port 8000 | The address that the web client's proxy calls | sure | known | CONF-3 |
| 38 | kata.py:39-41 | Score = gold + item values | The brief: "a score from the value of the treasures" | sure | known | BAG-2 |

## The web client: web/src/, vite.config.ts

| # | File:line | What it is | What it is probably for | Sure? | Mark | Pinned by |
| --- | --- | --- | --- | --- | --- | --- |
| 39 | App.tsx:5 | `SHOW_LEADERBOARD = false` | "Marketing, 2024: hide until the season starts." | sure | known | WEB-BOARD-1 |
| 40 | App.tsx:26, 29, 52 | The sid kept as `katacombs.sid` in the browser | Resume after a reload | sure | known | WEB-SESSION-1 |
| 41 | App.tsx:58-70 | On a failed load: retry at once, then every 2000 ms, for ever | Survive a short network loss | a guess | unknown | WEB-SESSION-2 |
| 42 | App.tsx:72-79 | The chat is read every 2000 ms | Show other players' messages | a guess | unknown | WEB-CHAT-1 |
| 43 | App.tsx:81-84 | A redraw every 30000 ms | Keep the market banner current | a guess | unknown | WEB-MARKET-2 |
| 44 | App.tsx:174 | SEND with an empty box sends nothing; the server would accept it | Avoid empty messages | a guess | unknown | WEB-CHAT-3 |
| 45 | App.tsx:184 | The market banner at minutes 50 to 59 of the browser's clock | A copy of the server's rule (item 11), on another clock | sure | known | WEB-MARKET-1 |
| 46 | App.tsx:185 | GO disabled at energy 1 or less; the server stops at 0 | "Do not let a player get stuck at 0." | sure | known | WEB-MOVE-2 |
| 47 | App.tsx:203 | The NAME box stops at 40 characters; the server allows 50 | Unknown | no idea | unknown | WEB-START-2 |
| 48 | App.tsx:255 | A double-click on an item calls the legacy pickup; no accessible name | A shortcut, older than PICK | no idea | unknown | WEB-ITEM-4 |
| 49 | App.tsx:258 | An item here shows USE, which the server refuses for an item not carried | Unknown | no idea | unknown | WEB-ITEM-1, WEB-ITEM-3 |
| 50 | api.ts:56 | The fallback message "SOMETHING WENT WRONG." | A body that is not the game's error format | sure | known | WEB-MSG-2 |
| 51 | api.ts:93-102 | PICK is sent again after 800 ms without an answer | "Slow network on the train. Do not remove." Pairs with INC-2231 (item 24). | sure | known | WEB-ITEM-2 |
| 52 | vite.config.ts:4-9 | `/api` goes to 127.0.0.1:8000, with the prefix removed | The development and preview proxy | sure | known | CONF-3 |

## Count

| Mark | Server | Client | Total |
| --- | --- | --- | --- |
| known | 18 | 7 | 25 |
| unknown | 20 | 7 | 27 |
| wrong | 0 | 0 | 0 |

**27 unknown items: that is the risk of a rewrite**, the knowledge that only
the code holds. Each one is pinned by a characterization test today, so a
rewrite that loses one fails a test, but nobody can yet say whether it
should be kept.

No item is marked **wrong**. The tests confirmed every reading that they
reach. That is weaker than it sounds: the same agent read the code and
wrote the tests, so a misreading could pass in both. The group's marking
and the regeneration of step 7 are the independent checks.

Two items have no rule yet (7 and 10, the world rules). Stretch item 7 of
step 5, the world check, would add them.

## Deletion Test, part 1: the two lists

Step 2 of the exercise. If `game.py` and `api.py` did not exist:

**What stays**

- The brief, `docs/katacombs.md`: older than the code, wrong on the bag.
- `kata.py`: the domain types (Item, Bag, Location, Player, Direction,
  Action) and the 10 use-case ports. It holds the score rule (item 38),
  and no other rule.
- The web client, `web/src/`, which still states the routes it calls and
  its own copies of two server rules (items 45 and 46).

**What you lose**

- Every rule of the game except the score: the world map, the items and
  their values, the gold, energy, the bag slots, the market hours, the
  rat, the key and the manhole, the win, the leaderboard (items 1-29).
- The API contract: the 16 routes, the JSON shapes, the error body and
  the status of each error (items 30-36). It exists only in `api.py`.
- The data formats that other programs depend on: the save payload, the
  account table, the password hash, the high-score line (items 12, 14, 19,
  28).
- The vocabulary: what a "move" counts (items 23, 33), "exit" for two
  things, pick/TAKE/pickup for one, save and snapshot for one shape.
- The names that other code imports: `create_app`, `app`, the use-case
  classes, `InMemoryGame`, the error types.
- The reasons. In the server, 12 comments hold the only record of a
  decision or an incident (items 7, 11-14, 17-18, 24, 27-28, 34-35).
- Every unknown item: the 27 above. They are the work plan.

**Without `web/src/`**, you lose the client's own rules: the 40-character
name, the double take after 800 ms, energy 1, the banner, the hidden
leaderboard, the retry for ever (items 39-51).

**Today**, after steps 4 and 5, most of the second list is in the
primitives: the rules in `spec/`, the contract in `spec/openapi.yaml`, the
formats in two JSON Schemas, and a test for each rule. What is still only
in the code: the reasons of the unknown items, and the two world rules.
