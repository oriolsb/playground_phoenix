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
| PLAYER-2 | No scenario yet (A name is trimmed and upper case) | - | - | - |
| PLAYER-3 | No scenario yet (A name has 1 to 50 characters) | - | - | - |
| PLAYER-4 | No scenario yet (The name ADMIN is reserved) | - | - | - |
| PLAYER-5 | No scenario yet (At most 20 players are active) | - | - | - |
| PLAYER-6 | No scenario yet (A client can list the active players) | - | - | - |
| PLAYER-7 | No scenario yet (Quitting removes the player) | - | - | - |
| PLAYER-8 | No scenario yet (A quitting player leaves the bag behind) | - | - | - |
| PLAYER-9 | No scenario yet (An unknown player sid is not found) | - | - | - |
| LOOK-1 | No scenario yet (A player can look around) | - | - | - |
| LOOK-2 | No scenario yet (A player can look in a direction without moving) | - | - | - |
| LOOK-3 | No scenario yet (Looking where there is no exit is refused) | - | - | - |
| MOVE-1 | A new player wins on the route through the market | api | durable | `rest/win.feature` |
| MOVE-2 | A new player wins on the route through the market | api | durable | `rest/win.feature` |
| MOVE-3 | A new player wins on the route through the market | api | durable | `rest/win.feature` |
| MOVE-4 | No scenario yet (Moving where there is no exit is refused) | - | - | - |
| MOVE-5 | No scenario yet (A player with no energy can't move) | - | - | - |
| MOVE-6 | A new player wins on the route through the market | api | durable | `rest/win.feature` |
| MOVE-7 | A new player wins on the route through the market | api | durable | `rest/win.feature` |
| MOVE-8 | No scenario yet (A rat in the cellar can steal an item without value) | - | - | - |
| GOLD-1 | A new player wins on the route through the market | api | durable | `rest/win.feature` |
| GOLD-2 | A new player wins on the route through the market | api | durable | `rest/win.feature` |
| BAG-1 | No scenario yet (A player can inspect the bag) | - | - | - |
| BAG-2 | A new player wins on the route through the market | api | durable | `rest/win.feature` |
| BAG-3 | No scenario yet (The bag holds 8 slots of up to 3 items with the same name) | - | - | - |
| ITEM-1 | No scenario yet (A client can inspect an item) | - | - | - |
| ITEM-2 | No scenario yet (An unknown item sid is not found) | - | - | - |
| ACT-1 | No scenario yet (An item must be here or in the bag) | - | - | - |
| ACT-2 | No scenario yet (An item allows only its own actions) | - | - | - |
| ACT-3 | No scenario yet (A player who has won can't act on items) | - | - | - |
| ACT-4 | A new player wins on the route through the market | api | durable | `rest/win.feature` |
| ACT-5 | No scenario yet (Taking an item already in the bag succeeds again) | - | - | - |
| ACT-6 | No scenario yet (Dropping moves an item into the location) | - | - | - |
| ACT-7 | No scenario yet (A player can only drop or use an item in the bag) | - | - | - |
| ACT-8 | No scenario yet (Opening an item opens it for everyone) | - | - | - |
| ACT-9 | No scenario yet (Opening an open item is refused) | - | - | - |
| ACT-10 | A new player wins on the route through the market | api | durable | `rest/win.feature` |
| ACT-11 | No scenario yet (Closing an item closes it for everyone) | - | - | - |
| ACT-12 | No scenario yet (Closing a closed item is refused) | - | - | - |
| ACT-13 | A new player wins on the route through the market | api | durable | `rest/win.feature` |
| ACT-14 | A new player wins on the route through the market | api | durable | `rest/win.feature` |
| ACT-15 | No scenario yet (Bread and beer restore energy) | - | - | - |
| ACT-16 | No scenario yet (Using any other item does nothing) | - | - | - |
| ACT-17 | A new player wins on the route through the market | api | durable | `rest/win.feature` |
| WIN-1 | A new player wins on the route through the market | api | durable | `rest/win.feature` |
| WIN-2 | A new player wins on the route through the market | api | durable | `rest/win.feature` |
| WIN-3 | A new player wins on the route through the market | api | durable | `rest/win.feature` |
| BOARD-1 | No scenario yet (The leaderboard ranks the highest score first) | - | - | - |
| SAVE-1 | No scenario yet (A player can save the game) | - | - | - |
| SAVE-2 | No scenario yet (A restart brings saved players back, but not the world) | - | - | - |
| ACCOUNT-1 | No scenario yet (A client can register an account) | - | - | - |
| ACCOUNT-2 | No scenario yet (An email needs an @) | - | - | - |
| ACCOUNT-3 | No scenario yet (An email has one account) | - | - | - |
| ACCOUNT-4 | No scenario yet (Logging in gives the account's player) | - | - | - |
| ACCOUNT-5 | No scenario yet (A wrong email or password is refused) | - | - | - |
| ACCOUNT-6 | No scenario yet (Quitting with an account keeps a snapshot) | - | - | - |
| CHAT-1 | No scenario yet (A player can send a chat message) | - | - | - |
| CHAT-2 | No scenario yet (A player reads the chat messages of the location) | - | - | - |
| CHAT-3 | No scenario yet (A chat message adds one to the move count) | - | - | - |
| API-1 | No scenario yet (A malformed request is refused) | - | - | - |
| API-2 | No scenario yet (Every error has a status and a message) | - | - | - |
| LEGACY-1 | No scenario yet (The legacy pickup takes an item without the checks) | - | - | - |
| LEGACY-2 | No scenario yet (The legacy pickup of an item elsewhere changes nothing) | - | - | - |

## Checks outside the feature files

These pytest tests are not scenarios, so `check trace` does not count them.

| Test | What it checks | Rules it reaches |
| --- | --- | --- |
| `contract/test_contract.py` | Every live response, error status and written file matches the contract | all operations in `openapi.yaml` |
| `harness/test_fixtures.py` | Each fixture reaches the game; the golden files load | MOVE-6, MOVE-8, SAVE-1, SAVE-2, ACCOUNT-4, ACCOUNT-5, ACCOUNT-6, WIN-3 |

## Contested behaviors pinned as they are

| Test | Behavior | Rule |
| --- | --- | --- |
| `harness/test_fixtures.py::test_a_save_from_before_2023_stops_the_server_from_starting` | A save without `energy` stops the server from starting | SAVE-2 |

## Rules with a partial check

| Rule | What the check does not prove | Why |
| --- | --- | --- |
| MOVE-6 | The market rule in production | The clock is faked in process; the real server's local time zone is not tested |
| WIN-3 | That the marketing job can still read the file | The job is outside this repository; only the line format is checked |

## Ephemeral tests that the audit found

| Test | Sign | What was done |
| --- | --- | --- |
| | | |
