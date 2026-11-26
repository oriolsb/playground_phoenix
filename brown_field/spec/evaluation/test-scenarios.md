# Test scenarios — Katacombs game-server

The rule-to-scenario map. Every rule ID appears once. This file survives
a regeneration: it says what the Evaluation proves, and what it does not.

Mode: characterization. Every scenario records what the legacy code does
today, and passes against it (2026-11-25).

Command of the canonical run: `uv run pytest brown_field/tests`.

Approved: Matte, 2026-11-26, suite sha256:ce939f6bbc9f3027

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
| PLAYER-1 | A new player wins on the route through the market (+1 more) | api, port | durable (api); port while the seam holds | `ports/ports.feature`, `rest/win.feature` |
| PLAYER-2 | A client registers an account (+2 more) | api, port | durable (api); port while the seam holds | `ports/ports.feature`, `rest/accounts.feature`, `rest/players.feature` |
| PLAYER-3 | The email check comes before the name check (+5 more) | api, port | durable (api); port while the seam holds | `ports/ports.feature`, `rest/accounts.feature`, `rest/players.feature` |
| PLAYER-4 | An account name follows the player name rules: "<name>" (+2 more) | api, port | durable (api); port while the seam holds | `ports/ports.feature`, `rest/accounts.feature`, `rest/players.feature` |
| PLAYER-5 | A login without an active player is refused when the game is full (+2 more) | api, port | durable (api); port while the seam holds | `ports/ports.feature`, `rest/accounts.feature`, `rest/players.feature` |
| PLAYER-6 | The list of players shows every active player with energy (+1 more) | api, port | durable (api); port while the seam holds | `ports/ports.feature`, `rest/players.feature` |
| PLAYER-7 | A player who quits is gone (+1 more) | api, port | durable (api); port while the seam holds | `ports/ports.feature`, `rest/players.feature` |
| PLAYER-8 | A login after a quit restores the snapshot (+1 more) | api | durable | `rest/accounts.feature`, `rest/players.feature` |
| PLAYER-9 | A player who quits is gone (+2 more) | api, port | durable (api); port while the seam holds | `ports/ports.feature`, `rest/players.feature` |
| WORLD-1 | The world file is valid; each location, each look, each first-visit gold, each item, each gold inside and lock match `world.json` (+3 more) | api | durable | `world/world.feature` |
| WORLD-2 | The slide from the cellar has no way back; every other exit has one (+1 more) | api | durable | `world/world.feature` |
| WORLD-3 | A world given to the game plays a new location and a new food item with no code change (+2 more) | port, - | port while the seam holds; durable (fitness) | `ports/ports.feature`, `fitness/structure.feature` |
| LOOK-1 | Looking around shows the start location (+1 more) | api, port | durable (api); port while the seam holds | `ports/ports.feature`, `rest/moving.feature` |
| LOOK-2 | Looking through an exit shows the next location without moving (+1 more) | api, port | durable (api); port while the seam holds | `ports/ports.feature`, `rest/moving.feature` |
| LOOK-3 | Looking where there is no exit is refused (+1 more) | api, port | durable (api); port while the seam holds | `ports/ports.feature`, `rest/moving.feature` |
| MOVE-1 | A new player wins on the route through the market (+1 more) | api, port | durable (api); port while the seam holds | `ports/ports.feature`, `rest/win.feature` |
| MOVE-2 | A new player wins on the route through the market | api | durable | `rest/win.feature` |
| MOVE-3 | Each chat message adds one to the move count (+1 more) | api | durable | `rest/chat.feature`, `rest/win.feature` |
| MOVE-4 | Moving where there is no exit is refused and costs nothing (+1 more) | api, port | durable (api); port while the seam holds | `ports/ports.feature`, `rest/moving.feature` |
| MOVE-5 | A player with no energy can't move (+2 more) | api, port | durable (api); port while the seam holds | `ports/ports.feature`, `rest/moving.feature` |
| MOVE-6 | At minute <minute> the market is <state> (+3 more) | api, port | durable (api); port while the seam holds | `ports/ports.feature`, `rest/moving.feature`, `rest/win.feature` |
| MOVE-7 | A new player wins on the route through the market (+1 more) | api, port | durable (api); port while the seam holds | `ports/ports.feature`, `rest/win.feature` |
| MOVE-8 | The rat in the cellar takes an item without value to the tube tunnel (+4 more) | api | durable | `rest/moving.feature` |
| GOLD-1 | Looking through an exit shows the next location without moving (+3 more) | api, port | durable (api); port while the seam holds | `ports/ports.feature`, `rest/moving.feature`, `rest/win.feature` |
| GOLD-2 | The crate is open or closed for every player, and its gold is paid once per player (+2 more) | api | durable | `rest/items.feature`, `rest/save.feature`, `rest/win.feature` |
| BAG-1 | The bag shows the items, the gold, the score and the energy | api | durable | `rest/items.feature` |
| BAG-2 | The highest score comes first, and equal scores keep the order of the wins (+2 more) | api, port | durable (api); port while the seam holds | `ports/ports.feature`, `rest/leaderboard.feature`, `rest/win.feature` |
| BAG-3 | A bag of 8 slots, 3 items with the same name per slot, refuses a ninth slot | api | durable | `rest/items.feature` |
| ITEM-1 | A client can inspect an item without a player (+1 more) | api, port | durable (api); port while the seam holds | `ports/ports.feature`, `rest/items.feature` |
| ITEM-2 | An unknown item sid is not found (+3 more) | api, port | durable (api); port while the seam holds | `ports/ports.feature`, `rest/items.feature`, `rest/legacy.feature` |
| ACT-1 | An item that is neither here nor in the bag can't be reached | api | durable | `rest/items.feature` |
| ACT-2 | An item refuses an action it does not allow: <action> the <item> (+3 more) | api, port | durable (api); port while the seam holds | `ports/ports.feature`, `rest/items.feature` |
| ACT-3 | The unknown item check comes before the win check (+1 more) | api | durable | `rest/items.feature` |
| ACT-4 | A taken item moves into the bag, and a dropped one into the location (+2 more) | api, port | durable (api); port while the seam holds | `ports/ports.feature`, `rest/items.feature`, `rest/win.feature` |
| ACT-5 | Taking an item already in the bag answers TAKEN again and changes nothing (+1 more) | api, port | durable (api); port while the seam holds | `ports/ports.feature`, `rest/items.feature` |
| ACT-6 | A taken item moves into the bag, and a dropped one into the location (+1 more) | api, port | durable (api); port while the seam holds | `ports/ports.feature`, `rest/items.feature` |
| ACT-7 | A player can't drop an item that is here but not in the bag (+2 more) | api, port | durable (api); port while the seam holds | `ports/ports.feature`, `rest/items.feature` |
| ACT-8 | The crate is open or closed for every player, and its gold is paid once per player | api | durable | `rest/items.feature` |
| ACT-9 | The crate is open or closed for every player, and its gold is paid once per player | api | durable | `rest/items.feature` |
| ACT-10 | The key unlocks the manhole, and the open manhole adds the way down (+1 more) | api | durable | `rest/items.feature`, `rest/win.feature` |
| ACT-11 | The crate is open or closed for every player, and its gold is paid once per player | api | durable | `rest/items.feature` |
| ACT-12 | The crate is open or closed for every player, and its gold is paid once per player (+1 more) | api | durable | `rest/items.feature` |
| ACT-13 | The key unlocks the manhole, and the open manhole adds the way down (+2 more) | api | durable | `rest/items.feature`, `rest/win.feature` |
| ACT-14 | The key unlocks the manhole, and the open manhole adds the way down (+1 more) | api | durable | `rest/items.feature`, `rest/win.feature` |
| ACT-15 | Bread restores 5 energy, up to 20, and is eaten (+2 more) | api, port | durable (api); port while the seam holds | `ports/ports.feature`, `rest/items.feature` |
| ACT-16 | The key outside the back yard does nothing | api | durable | `rest/items.feature` |
| ACT-17 | A new player wins on the route through the market | api | durable | `rest/win.feature` |
| WIN-1 | A new player wins on the route through the market (+1 more) | api, port | durable (api); port while the seam holds | `ports/ports.feature`, `rest/win.feature` |
| WIN-2 | The highest score comes first, and equal scores keep the order of the wins (+2 more) | api | durable | `rest/leaderboard.feature`, `rest/win.feature` |
| WIN-3 | A new player wins on the route through the market (+1 more) | api | durable | `boundary/startup.feature`, `rest/win.feature` |
| BOARD-1 | The highest score comes first, and equal scores keep the order of the wins | api | durable | `rest/leaderboard.feature` |
| SAVE-1 | A save answers with the path of the database file (+1 more) | api, port | durable (api); port while the seam holds | `ports/ports.feature`, `rest/save.feature` |
| SAVE-2 | A saved player comes back after a restart with the same state (+8 more) | api, port | durable (api); port while the seam holds | `ports/ports.feature`, `rest/save.feature` |
| ACCOUNT-1 | A client registers an account (+2 more) | api, port | durable (api); port while the seam holds | `ports/ports.feature`, `rest/accounts.feature` |
| ACCOUNT-2 | An email without @ is refused (+2 more) | api | durable | `rest/accounts.feature` |
| ACCOUNT-3 | An email has one account | api | durable | `rest/accounts.feature` |
| ACCOUNT-4 | The first login gives a new player at BRICK LANE (+8 more) | api, port | durable (api); port while the seam holds | `ports/ports.feature`, `rest/accounts.feature` |
| ACCOUNT-5 | A wrong <case> is refused with one message (+1 more) | api, port | durable (api); port while the seam holds | `ports/ports.feature`, `rest/accounts.feature` |
| ACCOUNT-6 | A login after a quit restores the snapshot (+4 more) | api | durable | `rest/accounts.feature` |
| CHAT-1 | A player sends a chat message (+1 more) | api | durable | `rest/chat.feature` |
| CHAT-2 | The players at the location read its messages, oldest first (+1 more) | api | durable | `rest/chat.feature` |
| CHAT-3 | Each chat message adds one to the move count | api | durable | `rest/chat.feature` |
| API-1 | A malformed request is refused: <case> | api | durable | `rest/errors.feature` |
| API-2 | A malformed request is refused: <case> (+1 more) | api | durable | `rest/errors.feature` |
| STORE-1 | A save writes one row to the saves table (+1 more) | - | durable | `boundary/storage.feature` |
| STORE-2 | An account row fills in as the account is used | - | durable | `boundary/storage.feature` |
| STORE-3 | A password is stored as its unsalted SHA-256 digest | - | durable | `boundary/storage.feature` |
| CONF-1 | Without KATACOMBS_DB, the database file is katacombs.db in the working directory (+1 more) | - | durable | `boundary/startup.feature` |
| CONF-2 | Without KATACOMBS_HIGHSCORES, a win writes highscores.jsonl in the working directory | - | durable | `boundary/startup.feature` |
| CONF-3 | python -m brown_field serves the API on 127.0.0.1, port 8000 | - | durable | `boundary/startup.feature` |
| ENTRY-1 | Two servers made from one game share its players (+1 more) | - | durable | `boundary/startup.feature` |
| ENTRY-2 | The module brown_field.api holds a ready server (+1 more) | - | durable | `boundary/startup.feature` |
| ENTRY-3 | The chat ports send and read the messages of the location (+2 more) | port | port while the seam holds | `ports/ports.feature` |
| ENTRY-4 | The REST adapter reads no game state outside a use case (+1 more) | - | durable | `fitness/structure.feature` |
| ENTRY-5 | The bag through the port shows the energy | port | port while the seam holds | `ports/ports.feature` |
| ENTRY-6 | A game on in-memory stores saves, restarts and records a win, and writes no file (+4 more) | port, - | port while the seam holds; durable (fitness) | `ports/ports.feature`, `fitness/structure.feature` |
| ENTRY-7 | The move port reads the clock it is given (+1 more) | port | port while the seam holds | `ports/ports.feature` |
| OPS-1 | A mix of 100 commands responds in less than 100 ms at p99 | api | live (simulated) | `fitness/ops.feature` |
| LEGACY-1 | A bag of 8 slots, 3 items with the same name per slot, refuses a ninth slot (+1 more) | api | durable | `rest/items.feature`, `rest/legacy.feature` |
| LEGACY-2 | The legacy pickup of an item elsewhere answers OK and changes nothing | api | durable | `rest/legacy.feature` |

## Operational limits and fitness functions

| Rule or decision | Function | How to run it | Need that it protects |
| --- | --- | --- | --- |
| OPS-1 | 100 mixed commands in process, p99 below 100 ms (measured today: about 1.5 to 3 ms) | `uv run pytest brown_field/tests -m ops` | Instant feedback for players. Live tier: production monitoring must check the same limit against real traffic. |

The status of every rule (observed, accepted, contested) is on the rule in
the specification. `fitness/test_spec_status.py` checks that each rule a
`@contested` scenario pins is contested, and that each accepted rule cites
a decision record that traces to it.

| Fitness | What it checks | How to run it |
| --- | --- | --- |
| `fitness/test_spec_status.py` | Each rule has one status; accepted cites its record; contested asks its question; the banners count right | `uv run pytest brown_field/tests -m fitness` |
| `fitness/test_invariants.py` (decision 0010) | After any random sequence of commands through the API: no item in two places, score = gold + values, energy 0 to 20, at most 8 slots and 20 players, gold never lower, a win never undone, every answer in the contract | `uv run pytest -k invariants`; longer with `KATACOMBS_EXAMPLES=2000` |
| `fitness/test_transcripts.py` (decision 0010) | 7 sessions that the legacy code answered (6 random, 1 scripted, 1,896 lines with the files) give the same answers and files | `uv run pytest -k transcripts`; record again only with `golden/make_transcripts.py`, from the code of a decision |
| `fitness/mutation/run_mutants.py` (decision 0010) | 42 hand-written mutants of the legacy code, one at a time, in a copy: each is killed, or listed in `mutation/mutants.md` with its reason. Also `uv run mutmut run`: 1,084 generated mutants, each survivor grouped by reason in the same file | `uv run python brown_field/tests/fitness/mutation/run_mutants.py` (about 10 minutes); `uv run mutmut run --max-children 8` (about 3 minutes) |

**Coverage of the code (2026-11-25):** 99 % of the branches of `game.py` and
`api.py` (`uv run pytest --cov=brown_field.game --cov=brown_field.api
--cov-branch`). The lines that no test runs are the four unreachable or
unobservable paths in `mutation/mutants.md`: the start-up world check
(game.py:300, 310), the sid collision retry (game.py:487) and the 500
answer (api.py:117).

## The port tier

`ports/ports.feature` builds each use case as `XUseCase(InMemoryGame())`
(README item 8). It is the one folder that imports names from `game.py`. It
holds while a rewrite keeps those names; until a decision record freezes
them as a seam, a correct rewrite may break it. The REST scenarios of the
same rules stay the durable check.

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
| `rest/save.feature`: the save answer holds the server's file path | SAVE-1 |

## Rules with a partial check

| Rule | What the check does not prove | Why |
| --- | --- | --- |
| MOVE-6 | The market rule in production (+3 more) | The clock is faked in process; the real server's local time zone is not tested |
| WIN-3 | That the marketing job can still read the file (+1 more) | The job is outside this repository; only the line format is checked |
| MOVE-8 | The 1 in 5 chance (+4 more) | The rat is forced or stopped; the rate itself is not measured |
| LEGACY-1 | The skipped win check (+1 more) | No item can be at the katacombs exit for a player who has won |
| CONF-3 | The address when port 8000 is taken | The scenario skips itself when another process, such as a development server, holds the port |
| STORE-3 | That the digest can log in after a restart | The golden account in `harness/test_fixtures.py` checks it on the legacy file |
| BAG-3 | A fourth item of the same name in one slot | The world holds at most 3 items with one name (BREAD) |

## Ephemeral tests that the audit found

| Test | Sign | What was done |
| --- | --- | --- |
| | | |
