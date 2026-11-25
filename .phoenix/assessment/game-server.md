# Assessment — game-server

Date: 2026-11-25. Scaffolding: delete this file when the primitives it
points to exist.

Started from `brown_field/game.py`. Resized to **game.py + api.py +
kata.py** (see the grain tests). The web client stays a separate unit, a
consumer of this one.

## Unit

- Public contract:
  - Python: `brown_field.api.create_app`, `brown_field.api.app`;
    `InMemoryGame`; the use cases `RegisterPlayerUseCase`,
    `ListPlayersUseCase`, `QuitGameUseCase`, `InspectItemUseCase`,
    `InspectBagUseCase`, `LookAroundUseCase`, `LookInDirectionUseCase`,
    `MoveUseCase`, `UseItemUseCase`, `SaveGameUseCase`,
    `RegisterAccountUseCase`, `LoginUseCase`; errors `KatacombsError`,
    `PlayerNotFound`, `ItemNotFound`, `InvalidName`, `NotAllowed`;
    `now_iso`, `ChatMessage`; the ports and model in `kata.py`.
  - REST (17 routes): `POST|GET /game/player`,
    `DELETE /game/player/{playerSid}`, `GET /leaderboard`,
    `GET /items/{itemSid}`, `GET /player/{playerSid}/bag`,
    `POST /player/{playerSid}/save`, `POST /accounts`,
    `POST /accounts/login`, `POST|GET /player/{playerSid}/chat`,
    `PUT /player/{playerSid}/item/{itemSid}/use/{action}`,
    `PUT /player/{playerSid}/pickup/{itemSid}` (Legacy),
    `GET /player/{playerSid}/location`,
    `GET /player/{playerSid}/look/{direction}`,
    `PUT /player/{playerSid}/move/{direction}`.
  - Error body: `{"code": <status>, "message": "<UPPER CASE>"}`. 404 not
    found, 400 invalid name or invalid request, 405 not allowed, 500 other.
  - Wire names: camelCase `isExit`, `hasWon`; `energy` added to the player
    and the bag responses.
- Consumers: `brown_field/__main__.py` (uvicorn); `brown_field/web/src/api.ts`
  (all routes but `GET /game/player`, `GET /items/{itemSid}`, `look/{direction}`);
  "mobile client v1" (`pickup`, per `api.py:188`, not in this repo);
  the nightly marketing job that reads `highscores.jsonl` (`game.py:327`);
  the support laptop that sets `KATACOMBS_DB` (`game.py:349`).
- Data owned: in-memory world and player state; SQLite `katacombs.db`
  tables `saves` and `accounts`.
- Data shared: `highscores.jsonl`, which this unit appends and a marketing
  job reads, so the format is a contract with a consumer outside the repo.
  Inside the unit, `api.py` writes game state too (`chat`, `moves`, bag via
  `pickup`): a shared write between the two files.
- Pace layer: medium. The world and rules are stable. Accounts, chat and
  mobile tweaks changed often.
- Kind: core.
- Dependencies:
  - Pure rules, the world tables, in-memory state: in process.
  - SQLite file (`KATACOMBS_DB`): local stand-in (temporary folder).
  - `highscores.jsonl` (`KATACOMBS_HIGHSCORES`): local stand-in (temporary
    folder).
  - Wall clock `datetime.now()` (market cleaning, timestamps): in process,
    with **no seam**. It needs a clock port.
  - `random` (rat theft, sids): in process, with **no seam**. It needs a
    seeded or injected source.
  - FastAPI / Pydantic: in process (TestClient).
- Rules: none yet.
- Modules: `brown_field/game.py`, `brown_field/api.py`, `brown_field/kata.py`.
- Risk: high. There are no tests, no contract and no spec. Two consumers sit
  outside the repo (mobile v1, the marketing job). Behavior depends on the
  clock and on chance. Passwords are stored as weak hashes.

### The five grain tests

| Test | Result | Note |
| --- | --- | --- |
| Comprehension | fail → pass after resize | `game.py` alone is 830 lines, but about 300 are world data. You can read the rules in ten minutes. You can't read them without `api.py`, which adds rules of its own: energy, chat and pickup. |
| Isolation | fail → pass after resize | `game.py` alone misses the energy gate (`api.py:212`) and the legacy pickup. Through `create_app(InMemoryGame())` and a TestClient, the merged unit is verifiable with temp `KATACOMBS_DB` / `KATACOMBS_HIGHSCORES`. The clock and the random source still block some scenarios. |
| Data ownership | fail → pass after resize | `api.py` mutates `game.players[...]`, `game.chat` and `game.places[...]` directly (`api.py:168-173`, `190-197`). Merged, one unit writes the state. `highscores.jsonl` stays shared with marketing. |
| Contracts | fail | The data goes out as hand-made dicts (`api.py:57-92`). There is no versioned schema, and `/openapi.json` is generated after the fact. The SQLite payload and the JSONL line have no schema. |
| Feeling | fail | Deleting it is frightening. The INC comments, the "do not remove" notes and the "nobody wrote down why" notes mean hidden knowledge. |

**Resize:** I merged `api.py` and `kata.py` into the unit, because `api.py`
holds game rules and writes game state. I did not split accounts, save
and chat into their own units. They share `PlayerState`, the same SQLite
file and the move counter, so a split would cross shared writes. It can be
revisited on day 3, once the boundary and the tests exist.

### Locality

- Likely need 1: "change the bag limit."
  - Modules it touches: `game.py:15-16, 322-323, 681` (slots rule), and
    `api.py:189-197`, the legacy pickup that **ignores the limit**.
  - Result: several places. The limit can be bypassed.
- Likely need 2: "change when a tired player can move."
  - Modules it touches: `api.py:211-213` (energy ≤ 0 → 405), `game.py:20-21, 71, 631`,
    and `web/src/App.tsx:185` (`tired` at ≤ 1, a different threshold).
  - Result: several places, across two units.
- Likely need 3: "change the market's cleaning hours."
  - Modules it touches: `game.py:316-319`, and `web/src/App.tsx:184` (a copy of the
    minute-50 rule on the client).
  - Result: several places, across two units.
- Flows that pass through the unit's code: every route goes through
  `InMemoryGame`, and `move` runs through the energy gate in `api.py`
  before it reaches the use case.
- Seams to plan:
  1. a clock port for `market_is_cleaning`, `now_iso` and the save and
     high-score timestamps;
  2. an injectable random source for `MoveUseCase.rat` and `new_sid`;
  3. move the energy gate and the legacy pickup into `game.py`, so the rules
     live in one module. This is a day-3 structural change. Today, only
     pin it with tests.

## Scar tissue

24 hits.

| File:line | Behavior | Lesson it probably encodes | Primitive to hold it |
| --- | --- | --- | --- |
| game.py:15-16 | Bag = 8 slots × 3 items of the same name, not the brief's "max 10" | Players wanted to stack consumables (bread, beer). The limit was redesigned without updating the brief | Spec rule + decision |
| game.py:17 | Name 1–50 chars after strip + upper case | A length limit for display or storage. Names are case-insensitive | Spec rule |
| game.py:18 | At most 20 concurrent players, shared by register and login-restore (`game.py:808`) | Capacity limit of a single in-memory server | Spec rule + decision |
| game.py:19 | Name `ADMIN` is reserved, for players and accounts | Stops impersonation of staff in chat or on the leaderboard | Spec rule |
| game.py:20-21, 71 | Start energy 12, max 20; bread +5, beer +3. Not in the brief | The energy mechanic was added for the mobile release | Spec rules + decision |
| game.py:22, 646-654 | 20% chance per cellar entry that a rat steals one zero-value item, which reappears in the Tube Tunnel | A flavour mechanic. It never takes valuables, so it never lowers the score | Spec rule + decision. Needs a random seam |
| game.py:50-52 | Cellar → DOWN is one way, exempt from the two-way check | Product asked for a slide (2022). The world invariant has a named exception | Spec rule + decision |
| game.py:299-313 | Startup fails if a title is duplicated or a connection has no way back | A world-integrity invariant, checked at boot | Fitness function |
| game.py:316-319 | Market closed at minutes 50–59 of every hour, local time | Cleaning-crew contract (2023). An external, contractual constraint, with "ask facilities" | Decision + spec rule. Needs a clock seam |
| game.py:326-335 | Every win appends `{name, score, at}` to `highscores.jsonl` | A marketing job reads it nightly. The format is a contract with a consumer outside the repo | Contract (JSON Schema) + decision |
| game.py:348-350 | DB path from `KATACOMBS_DB`, default `katacombs.db` in the working directory | Only the support laptop overrides it, so the default location matters in production | Spec (operations) + decision |
| game.py:368-370 | Passwords hashed with unsalted SHA-256. "TODO: bcrypt (2023)" | A known security debt. A regeneration must not "fix" it silently, because the stored hashes would stop matching | Decision (+ open question). Flag as a security risk |
| game.py:410-411 | Crate holds 10 gold; manhole starts locked | Win-path state | Spec rules |
| game.py:448-478 | On restart, saved players are reloaded, but the world is not (open and locked items reset) | "Nobody wrote down why." After a restart a player may find the manhole locked again | Open question → decision |
| game.py:466-468 | A save whose location no longer exists is skipped silently | The world changed under old saves. A quiet migration policy | Spec rule + decision |
| game.py:480-488 | Sids are random `6-12-8` digit strings, unique against players **and items** | Item sids share the same format (`000100-…`), so they must not collide | Spec rule (format) |
| game.py:570-578 | Quit drops the whole bag at the player's location. With an account, it first writes a snapshot | Items stay in the world for others. Accounts can resume | Spec rules |
| game.py:629-630 | Market blocked even when the player is already adjacent. The move costs nothing | The order of checks matters: won → exit exists → market → energy cost | Spec rule |
| game.py:631-632 | A move costs energy and counts a move. A refused move costs neither | Only moves that succeed are counted | Spec rule |
| game.py:674 | Every item action that passes the checks adds a move, including a repeated TAKE, open and use | "Moves" is not only movement. It affects the leaderboard | Spec rule + vocabulary ("move") |
| game.py:678-680 | TAKE on an item already in the bag returns "TAKEN." | INC-2231: the client resends TAKE on a slow network. Paired with `web/src/api.ts:93-102`, which **does** resend after 800 ms | Spec rule + decision |
| game.py:700-701, 715-716 | Opening the manhole creates BACK YARD↔KATACOMBS DOWN/UP. Closing it removes the passage, and the world state is shared by all players | One player's action changes the map for everyone | Spec rule + decision |
| game.py:737, 754 | Save writes to SQLite. The payload grew to hold energy and moves (2023) | INC-3110: a laptop sleep lost every bag. Shows an old payload version | Decision + contract (payload schema) |
| api.py:188-197 | Legacy `PUT /pickup/{item}`: no bag limit, no move count, no won check. Returns `OK` even if the item isn't here | Mobile client v1 still calls it, and so does the web client's `quickPick` | Contract + decision |
| api.py:210-213 | Energy ≤ 0 → 405 "TOO TIRED", checked in the API layer before the use case (even for a won player) | Added for the mobile release, in the wrong layer | Spec rule + decision |
| api.py:166-173 | Chat sets the location at send time. Sending counts a move. There is no length limit and the log grows without bound | Location-scoped chat. The move count side effect is probably accidental | Spec rule + open question |
| api.py:119-121 | Any validation error → 400 "INVALID REQUEST." (FastAPI default is 422) | A uniform error format for clients | Contract |

Hits outside the unit, for the web-client unit: `App.tsx:5` leaderboard
hidden (Marketing, 2024), `App.tsx:184` market copy, `App.tsx:185`
`tired ≤ 1` "do not let a player get stuck", the 2 s reconnect and chat
polling, the sid kept in localStorage, and `api.ts:93` the double TAKE
sent after 800 ms.

**Three riskiest:**
1. **Unsalted SHA-256 passwords** (`game.py:368`). A security issue, and a
   compatibility trap: a regeneration that changes the hash locks every
   existing account out.
2. **`highscores.jsonl` format and the legacy `pickup` route.** Both are
   boundaries with consumers outside the repo (marketing, mobile v1) that
   no test in this repo can see. A clean rewrite breaks them silently.
3. **Save and restart semantics** (`game.py:448-478`). Players come back,
   the world doesn't. Saves with an unknown location are dropped. The
   reason was never written down, and it decides whether the win path
   still works after a restart.

## Grades

| Primitive | Grade | Gap |
| --- | --- | --- |
| Specification | absent | Only the brief, which is older than the code and wrong on the bag limit. It is silent on energy, market hours, the rat, accounts, chat and save. There are no rule IDs. |
| Evaluation | absent | No tests in the Python unit. `brown_field/tests/` doesn't exist. The web client has test tooling (Vitest, Playwright) but no tests in the tree. |
| Context Boundary | partial | FastAPI generates `/openapi.json`, but after the fact. Responses are untyped dicts, and the error body and the legacy route aren't described. SQLite and JSONL formats have no schema. No vocabulary ("move", "score", "gold" are overloaded) and no dataset owners. |
| Provenance | partial | No decision records. About 10 code comments hold fragments of reasons, such as INC-2231, INC-3110, "product 2022", "cleaning crew 2023" and "marketing". Several say outright that the reason is lost. |

## Hybrid component

Yes. The unit mixes data movement with business rules.

- **Data movement:** `game.py:338-403` (schemas, `save_path`, `write_account`,
  `snapshot_of`), `game.py:421-478` (`load_accounts`, `load_saves`),
  `game.py:326-335` (`save_high_score` I/O), `game.py:742-773` (the save SQL),
  `api.py:57-99` (JSON mapping, error body).
- **Rules:** `game.py:15-22, 50-71` (limits and world tables), `game.py:304-323`
  (world invariant, market rule, slots), `game.py:500-513` (visit gives gold,
  manhole connect), `game.py:540-735` (use cases), `game.py:779-830` (account
  and login rules).
- **Mixed inside one function:**
  - `MoveUseCase.execute` computes the win, then writes the high-score file
    (`game.py:637-643`).
  - `QuitGameUseCase` writes the account snapshot (`game.py:572-575`).
  - `LoginUseCase` restores state and writes the account (`game.py:829`).
  - `api.py` holds the energy rule, the chat rules and the pickup rule.
- **Separation planned**, before the specification:
  - Name three ports: `SaveStore` (saves + accounts), `HighScoreSink`
    (JSONL) and `Clock`, plus a `Random` source.
  - The rules call the ports. The rest stays I/O.
  - Today, only write the rules and contracts against these names. Day 3
    makes the actual split. The guardrail is that the code stays unchanged
    except for the clock and random seams in step 5.

## Work plan

| Step | Command | Output |
| --- | --- | --- |
| 1. Freeze the boundary | `/phoenix-kit:contract` | `brown_field/spec/openapi.yaml` (all 17 routes as they behave today, including `pickup`, the `{code,message}` error body, 400 for validation, camelCase fields, `energy` extras); JSON Schemas for the high-score line and the save payload; ownership table (game-server owns `saves`, `accounts`; `highscores.jsonl` shared with marketing); vocabulary terms (move, score, gold, energy, slot). |
| 2. Capture current behavior | `/phoenix-kit:specify`, then `/phoenix-kit:evaluate characterization <rule IDs>` | Short rules with `game.py:<line>` sources. Minimum path first: movement, take/drop, gold on first visit, the win route (key → manhole → katacombs → exit; no clock seam needed outside minutes 50–59, or route via Boxpark → Arches → tunnel), save and restart, accounts and chat routes, one error per code. Then `brown_field/tests/` scenarios through `create_app`, with temp `KATACOMBS_DB` and `KATACOMBS_HIGHSCORES`, passing today. |
| 3. Complete the specification | `/phoenix-kit:specify` | Stretch rules by ID: energy, the rat (after the random seam), market hours (after the clock seam), the one-way slide, world reset on restart, sid format, chat scope. |
| 4. Record the provenance | `/phoenix-kit:decide` | One record per scar, status "written after the code". Bag slots, energy, rat, slide, market contract, high-score format, DB path, SHA-256 passwords, world not saved, idempotent TAKE, legacy pickup, energy gate in the API. |
| 5. Deletion Test | `/phoenix-kit:deletion-test` | Verdict, then regenerate in a clean folder (step 7). |

### Progress

- [x] 0. `PHOENIX.md` saved at the package root (2026-11-25)
- [x] 1. Freeze the boundary (2026-11-25): 63 boundary rules, `openapi.yaml`
      (16 operations), 2 JSON Schemas, Terms, ownership, `tests/test_contract.py`
      (30 pass). The status-by-reason decision record is still owed (step 4).
- [ ] 2. Capture current behavior
      - [x] Test setup (2026-11-25): conftest fixtures (isolated files, clock with
        local time, rat, restart, golden), golden fixtures from the legacy code,
        contract test moved to `tests/contract/`; 43 pass
      - [x] End-to-end test through the market (step 3 commit 0183970)
      - [x] REST characterization: 10 feature files, 103 scenarios; `check trace`
        63/63 rules; 145 tests pass; 5 contested scenarios tagged (step 4 commit dd82f9d)
      - [x] Data at rest, configuration and entry points: 8 rules (STORE, CONF,
        ENTRY), 2 features in `tests/boundary/`; 156 pass; trace 71/71 (step 5 commit 587c6a2)
      - [x] OPS-1 rule and fitness scenario (`tests/fitness/`, p99 about 1.5-3 ms);
        17 port scenarios (`tests/ports/`, XUseCase(InMemoryGame())); 174 pass;
        trace 72/72 (step 6 commit 477daa6)
      - [x] Web client (item 8): 28 WEB rules in `brown_field/web/spec/`; Vitest
        component tests with MSW (mocks checked against the contract), type-drift
        and bundle-size fitness, Playwright win; 52 Vitest + 2 Playwright pass
- [ ] 3. Complete the specification
- [ ] 4. Record the provenance
- [ ] 5. Deletion Test and regeneration

**First command:** save `.phoenix/proposal/PHOENIX.md` at the package root,
then run `/phoenix-kit:contract brown_field/api.py`.
