# Test scenarios — Katacombs game-server

The rule-to-scenario map. Every rule ID appears once. This file survives
a regeneration: it says what the Evaluation proves, and what it does not.

Mode: characterization. Every scenario records what the legacy code does
today, and passes against it (2026-11-25).

Command of the canonical run: `uv run pytest brown_field/tests`.

Approved:

Do not type this line by hand. After the review, a person runs
`python3 phoenix-kit/scripts/phoenix_check.py approval stamp --by "<who>"`.

## How to read the tables

- "Way in": `port` (the published ports), `api` (the REST contract),
  `-` (a check of data or code, with no port, or no scenario yet).
- "Tier": durable (survives a rewrite), ephemeral (deleted with the
  implementation), live (production monitoring, simulated here).

## Rules and their scenarios

| Rule | Scenario | Way in | Tier | Feature file |
| --- | --- | --- | --- | --- |
| PLAYER-1 | A new player wins on the route through the market | api | durable | `rest/win.feature` |
| PLAYER-2 | A client registers an account (+1 more) | api | durable | `rest/accounts.feature`, `rest/players.feature` |
| PLAYER-3 | The email check comes before the name check (+4 more) | api | durable | `rest/accounts.feature`, `rest/players.feature` |
| PLAYER-4 | An account name follows the player name rules: "<name>" (+1 more) | api | durable | `rest/accounts.feature`, `rest/players.feature` |
| PLAYER-5 | A login without an active player is refused when the game is full (+1 more) | api | durable | `rest/accounts.feature`, `rest/players.feature` |
| PLAYER-6 | The list of players shows every active player with energy | api | durable | `rest/players.feature` |
| PLAYER-7 | A player who quits is gone | api | durable | `rest/players.feature` |
| PLAYER-8 | A login after a quit restores the snapshot (+1 more) | api | durable | `rest/accounts.feature`, `rest/players.feature` |
| PLAYER-9 | A player who quits is gone (+1 more) | api | durable | `rest/players.feature` |
| LOOK-1 | Looking around shows the start location | api | durable | `rest/moving.feature` |
| LOOK-2 | Looking through an exit shows the next location without moving | api | durable | `rest/moving.feature` |
| LOOK-3 | Looking where there is no exit is refused | api | durable | `rest/moving.feature` |
| MOVE-1 | A new player wins on the route through the market | api | durable | `rest/win.feature` |
| MOVE-2 | A new player wins on the route through the market | api | durable | `rest/win.feature` |
| MOVE-3 | Each chat message adds one to the move count (+1 more) | api | durable | `rest/chat.feature`, `rest/win.feature` |
| MOVE-4 | Moving where there is no exit is refused and costs nothing | api | durable | `rest/moving.feature` |
| MOVE-5 | A player with no energy can't move (+1 more) | api | durable | `rest/moving.feature` |
| MOVE-6 | At minute <minute> the market is <state> (+1 more) | api | durable | `rest/moving.feature`, `rest/win.feature` |
| MOVE-7 | A new player wins on the route through the market | api | durable | `rest/win.feature` |
| MOVE-8 | The rat in the cellar takes an item without value to the tube tunnel (+2 more) | api | durable | `rest/moving.feature` |
| GOLD-1 | Looking through an exit shows the next location without moving (+2 more) | api | durable | `rest/moving.feature`, `rest/win.feature` |
| GOLD-2 | The crate is open or closed for every player, and its gold is paid once per player (+2 more) | api | durable | `rest/items.feature`, `rest/save.feature`, `rest/win.feature` |
| BAG-1 | The bag shows the items, the gold, the score and the energy | api | durable | `rest/items.feature` |
| BAG-2 | The highest score comes first, and equal scores keep the order of the wins (+1 more) | api | durable | `rest/leaderboard.feature`, `rest/win.feature` |
| BAG-3 | A bag of 8 slots, 3 items with the same name per slot, refuses a ninth slot | api | durable | `rest/items.feature` |
| ITEM-1 | A client can inspect an item without a player | api | durable | `rest/items.feature` |
| ITEM-2 | An unknown item sid is not found (+2 more) | api | durable | `rest/items.feature`, `rest/legacy.feature` |
| ACT-1 | An item that is neither here nor in the bag can't be reached | api | durable | `rest/items.feature` |
| ACT-2 | An item refuses an action it does not allow: <action> the <item> (+2 more) | api | durable | `rest/items.feature` |
| ACT-3 | The unknown item check comes before the win check (+1 more) | api | durable | `rest/items.feature` |
| ACT-4 | A taken item moves into the bag, and a dropped one into the location (+1 more) | api | durable | `rest/items.feature`, `rest/win.feature` |
| ACT-5 | Taking an item already in the bag answers TAKEN again and changes nothing | api | durable | `rest/items.feature` |
| ACT-6 | A taken item moves into the bag, and a dropped one into the location | api | durable | `rest/items.feature` |
| ACT-7 | A player can't drop an item that is here but not in the bag (+1 more) | api | durable | `rest/items.feature` |
| ACT-8 | The crate is open or closed for every player, and its gold is paid once per player | api | durable | `rest/items.feature` |
| ACT-9 | The crate is open or closed for every player, and its gold is paid once per player | api | durable | `rest/items.feature` |
| ACT-10 | The key unlocks the manhole, and the open manhole adds the way down (+1 more) | api | durable | `rest/items.feature`, `rest/win.feature` |
| ACT-11 | The crate is open or closed for every player, and its gold is paid once per player | api | durable | `rest/items.feature` |
| ACT-12 | The crate is open or closed for every player, and its gold is paid once per player (+1 more) | api | durable | `rest/items.feature` |
| ACT-13 | The key unlocks the manhole, and the open manhole adds the way down (+2 more) | api | durable | `rest/items.feature`, `rest/win.feature` |
| ACT-14 | The key unlocks the manhole, and the open manhole adds the way down (+1 more) | api | durable | `rest/items.feature`, `rest/win.feature` |
| ACT-15 | Bread restores 5 energy, up to 20, and is eaten (+1 more) | api | durable | `rest/items.feature` |
| ACT-16 | The key outside the back yard does nothing | api | durable | `rest/items.feature` |
| ACT-17 | A new player wins on the route through the market | api | durable | `rest/win.feature` |
| WIN-1 | A new player wins on the route through the market | api | durable | `rest/win.feature` |
| WIN-2 | The highest score comes first, and equal scores keep the order of the wins (+2 more) | api | durable | `rest/leaderboard.feature`, `rest/win.feature` |
| WIN-3 | A new player wins on the route through the market | api | durable | `rest/win.feature` |
| BOARD-1 | The highest score comes first, and equal scores keep the order of the wins | api | durable | `rest/leaderboard.feature` |
| SAVE-1 | A save answers with the path of the database file | api | durable | `rest/save.feature` |
| SAVE-2 | A saved player comes back after a restart with the same state (+6 more) | api | durable | `rest/save.feature` |
| ACCOUNT-1 | A client registers an account (+1 more) | api | durable | `rest/accounts.feature` |
| ACCOUNT-2 | An email without @ is refused (+1 more) | api | durable | `rest/accounts.feature` |
| ACCOUNT-3 | An email has one account | api | durable | `rest/accounts.feature` |
| ACCOUNT-4 | The first login gives a new player at BRICK LANE (+4 more) | api | durable | `rest/accounts.feature` |
| ACCOUNT-5 | A wrong <case> is refused with one message | api | durable | `rest/accounts.feature` |
| ACCOUNT-6 | A login after a quit restores the snapshot (+1 more) | api | durable | `rest/accounts.feature` |
| CHAT-1 | A player sends a chat message (+1 more) | api | durable | `rest/chat.feature` |
| CHAT-2 | The players at the location read its messages, oldest first (+1 more) | api | durable | `rest/chat.feature` |
| CHAT-3 | Each chat message adds one to the move count | api | durable | `rest/chat.feature` |
| API-1 | A malformed request is refused: <case> | api | durable | `rest/errors.feature` |
| API-2 | A malformed request is refused: <case> (+1 more) | api | durable | `rest/errors.feature` |
| LEGACY-1 | A bag of 8 slots, 3 items with the same name per slot, refuses a ninth slot (+1 more) | api | durable | `rest/items.feature`, `rest/legacy.feature` |
| LEGACY-2 | The legacy pickup of an item elsewhere answers OK and changes nothing | api | durable | `rest/legacy.feature` |

## Checks outside the feature files

These pytest tests are not scenarios, so `check trace` does not count them.

| Test | What it checks | Rules it reaches |
| --- | --- | --- |
| `contract/test_contract.py` | Every live response, error status and written file matches the contract | all operations in `openapi.yaml` |
| `harness/test_fixtures.py` | Each fixture reaches the game; the golden files written by the legacy code load | MOVE-6, MOVE-8, SAVE-1, SAVE-2, ACCOUNT-4, ACCOUNT-5, ACCOUNT-6, WIN-3 |

## Contested behaviors pinned as they are

Tagged `@contested` (`uv run pytest brown_field/tests -m contested`). Each
one records today's behavior; a decision record must confirm or change it.

| Scenario | Rules |
| --- | --- |
| `rest/accounts.feature`: A second login after a quit rolls the active player back to the snapshot | ACCOUNT-4, ACCOUNT-6 |
| `rest/chat.feature`: An empty chat message is accepted | CHAT-1 |
| `rest/errors.feature`: A URL that is not a route answers with the framework's body | API-2 |
| `rest/save.feature`: A restart puts a saved item back in its location too | SAVE-2 |
| `rest/save.feature`: A save from before 2023 stops the server from starting | SAVE-2 |
| `rest/legacy.feature` and `rest/items.feature`: the legacy pickup skips the bag limit and the move count | LEGACY-1 |
| `rest/save.feature`: the save answer holds the server's file path | SAVE-1 |

## Rules with a partial check

| Rule | What the check does not prove | Why |
| --- | --- | --- |
| MOVE-6 | The market rule in production | The clock is faked in process; the real server's local time zone is not tested |
| WIN-3 | That the marketing job can still read the file | The job is outside this repository; only the line format is checked |
| MOVE-8 | The 1 in 5 chance | The rat is forced or stopped; the rate itself is not measured |
| LEGACY-1 | The skipped win check | No item can be at the katacombs exit for a player who has won |
| BAG-3 | A fourth item of the same name in one slot | The world holds at most 3 items with one name (BREAD) |

## Ephemeral tests that the audit found

| Test | Sign | What was done |
| --- | --- | --- |
| | | |
