# Grades of the four primitives

## Step 3: the system as it was found

The grade of the legacy system before any primitive was added (commit
`90891ef`, "The original legacy system"), against "What good looks like"
in the README. Step 7 adds its grade in the last column.

| Primitive | Grade (step 3) | Gap | Grade (step 7) |
| --- | --- | --- | --- |
| Specification | absent | Only the brief, which is older than the code and wrong on the bag (10 items; the code has 8 slots of 3). It says nothing of energy, the market hours, the rat, accounts, chat, the save or the restart. No rule has an ID, a source or a reason. Each rule exists only as an `if` in `game.py` or `api.py`. | **strong.** A fresh agent built the game from it in one prompt (run 2): 189 of 189 tests pass, and its answers and files match the original on 4,800 random and 84 scripted requests. Gap: run 1 stopped, because the world (locations, exits, gold, items, sids) was only in `game.py`; now `world.json`, WORLD-1, WORLD-2. 28 reasons are still guesses. |
| Evaluation | absent | No test of the server. The web client has test tools in `package.json` (Vitest, Testing Library, MSW, Playwright) and no test. Nothing tells correct behavior from incorrect without the old code. | **strong.** It caught the one behavior change of the one-prompt rewrite (the energy gate moved into the move port), which 320,000 REST requests of the rewrite's own check could not see. Planted errors fail. Gaps: before step 7 an invented world could have passed; the bare `uv run pytest` fails at collection (`pytest_plugins` in a non-top-level conftest), in this package too. |
| Context Boundary | partial | The ports of `kata.py` exist, small and typed, but the accounts and the login have no port, and the domain Player has no energy. FastAPI generates `/openapi.json` from the code, after the fact: an API that only the code describes. The answers are hand-made dicts; the save payload, the accounts table and the high-score line have no schema and no version. `api.py` and `game.py` both change the player and the world. No vocabulary: "exit" means two things, "move" counts more than moves. | **strong.** Both new versions kept every route, schema, file format, port, error type and seam (decision 0008); the port tier pinned what REST cannot see. Gaps: where the energy gate lives is part of the boundary but undecided (MOVE-5, contested); the web IDs still collide with server prefixes (8 trace warnings). |
| Provenance | partial | No decision record. About 12 comments keep a reason or an incident (INC-2231, INC-3110, "Product asked… (2022)", "Cleaning crew contract (2023)", "Marketing, 2024", the mobile release), and two say outright that the reason is lost ("Nobody wrote down why"). 27 of the 52 items of `archaeology.md` are unknown. | **partial.** 9 decision records and a status on each rule, but the regeneration keeps 31 contested behaviors and 28 guessed reasons because nothing says why. Nobody in the group has confirmed the statuses yet. |

## Step 3: three questions

Can you trust a change of an agent? "Partly" is a no.

| # | Question | Answer | Evidence |
| --- | --- | --- | --- |
| 1 | Can you merge a change that an agent made, without reading every line? | **no** | No test and no contract: nothing but a person's reading can show that a change kept the behavior. |
| 2 | Can an agent implement a change from one prompt, with no corrective prompts? | **no** | 27 behaviors have no written reason, and the brief is wrong; an agent has no source but the old code, and the one-prompt rewrite cannot know which quirks matter. |
| 3 | Can you release the change without anyone watching production? | **no** | Two consumers live outside the repository (the marketing job reads `highscores.jsonl`, mobile client v1 calls the legacy pickup), and stored accounts depend on the unsalted SHA-256 hash; no check of any of them exists. |

## Between step 3 and step 7 (not a grade)

What steps 4 and 5 added, for the step 7 grading:

- **Specification:** 72 server rules and 28 client rules, each with an ID, a
  source (file and line) and an observable result. Every rule records the
  code; none is reviewed yet (step 6 gives each one a status). Only 11
  rules say "Why: unknown" (6 server, 5 client), but the archaeology marks
  27 items unknown: for the others, the rule's "Why" states the agent's
  guess as if it were known (for example PLAYER-3 and PLAYER-4). Step 6 must mark each guessed reason as a guess.
- **Evaluation:** 174 server tests (contract, REST, ports, data at rest,
  start-up, OPS-1) and 54 client tests, all passing on the original code;
  `check trace` covers 72 of 72 rules. The world check (stretch item 7)
  is not done.
- **Context Boundary:** `openapi.yaml` (16 operations), two JSON Schemas,
  Terms with words to avoid, a data-ownership table, and a contract test;
  the mock bodies of the client are checked against the contract.
- **Provenance (step 6):** 8 decision records in `brown_field/decisions/`
  (6 "written after the code" from comments and incidents, 2 "accepted"
  during the exercise: the workshop limits and the seams). Each rule has a
  status: server 49 observed, 12 accepted, 11 contested; client 12
  observed, 7 accepted, 9 contested. 28 reasons are marked as guesses.

## Step 7: the regeneration

Two regenerations, each in a new folder with only the primitives and the
files that do not change (`pyproject.toml`, `uv.lock`, `.gitignore`,
`kata.py`, `__init__.py`, `__main__.py`, `spec/`, `decisions/`, `tests/`),
plus `web/spec/`: `fitness/test_spec_status.py` reads it. Before each run,
`uv run pytest` failed with `ModuleNotFoundError: No module named
'brown_field.api'`. Each run was a new headless Claude session with the
prompt of the README, given no path of this package.

| Run | Folder | Result | Primitives changed |
| --- | --- | --- | --- |
| 1 | `~/katacombs-workspaces/brown-field-regenerate` | Stopped with no code: no primitive held the world. It listed what the tests leak (12 titles, 2 items, gold totals) and what nothing gives (descriptions, 2 unnamed locations, gold per location, item values and actions, exits, the sid scheme, the slide). | none |
| 2 | `~/katacombs-workspaces/brown-field-regenerate-2` | After the world primitive (`32d407c`): `game.py` (770 lines) and `api.py` (203 lines); 189 of 189 tests pass. It stopped on one finding: the bare `uv run pytest` fails at collection; `uv run pytest brown_field/tests` passes. | none |

**Files the agents opened.** Run 1: `spec/`, `web/spec/`, `decisions/`,
`tests/` (with the golden SQLite files, read with `sqlite3`), `kata.py`,
`__init__.py`, `__main__.py`, `pyproject.toml`, and 3 overflow files of its
own tool output. Run 2: the same, and the two files it wrote. Neither read
a file of this package or its history. The logs are stream-json, one tool
call per line.

**Judgement calls of run 2** (outside any rule): the KEY unlocks the
MANHOLE and the bread and beer amounts come from ACT-14 and ACT-15, not
from `world.json`; an invalid email raises a new `InvalidEmail` error
type; a missing database file is never created by a read. The scripted
check below shows that each one answers as the original does.

**A check outside the primitives.** The same command sequences went to the
original and to each new version: 12 seeds of 400 random requests
(moves, looks, item actions, chat, saves, the legacy pickup, unknown sids),
and 84 scripted steps (accounts, login after quit and after a restart,
saves, the key and the manhole, a win, the leaderboard, the high-score
file, every SQLite table). Run 2 and the rewrite differ from the original
in 0 answers and 0 file lines. This check is not a primitive: it needs the
original code.

## Step 7: the one-prompt rewrite

The rewrite of step 1 ran late, in `~/katacombs-workspaces/brown-field-rewrite`,
from the baseline commit `90891ef`. Diff against `legacy`: 7 files, 2195
insertions, 736 deletions, including its own 77 tests (`tests/`) and two
comparison scripts (`.scratch/`).

- **The agent's own check:** 77 tests, written on the legacy code first, and
  a differential run of about 320,000 REST requests against the legacy code
  loaded from git. Both stay in its folder, outside any primitive.
- **Our tests:** 188 of 189 pass (after copying `decisions/` too: the README
  copy list for the rewrite leaves it out, and the status fitness test reads it).
  The failure: `ports/ports.feature`, "the move port has no energy gate".
  The rewrite moved the energy check from the REST route into
  `MovePlayerUseCase`. Over REST nothing changes; a caller of the port is now
  refused. MOVE-5 is contested for exactly this question.
- **Would we merge it?** Not yet. The code reads well and the REST behavior
  is the same, but it decides MOVE-5 without a decision record, and it adds
  `.scratch/`. Merge after the group decides MOVE-5 and the scratch files go.
- **What the rewrite kept:** every quirk that our tests pin, the unsalted
  SHA-256 (it named it as a decision for us), the file formats, the slide.

## Step 7: the three questions again

| # | Question | Answer | Evidence |
| --- | --- | --- | --- |
| 1 | Can you merge a change that an agent made, without reading every line? | **yes**, inside what the tests cover | 189 tests, the contract and the schemas held two new versions; they caught the one change that the rewrite's 320,000 requests missed. Not for a change to a contested rule: that needs a decision first. |
| 2 | Can an agent implement a change from one prompt, with no corrective prompts? | **yes**, after the world primitive | Run 2 had one prompt and no corrections. Run 1 had one prompt too, and stopped, rightly: the fix was a primitive, not a prompt. |
| 3 | Can you release the change without anyone watching production? | **no** | The marketing job and mobile client v1 are still outside the repository: we check their formats, not the consumers. OPS-1 needs production monitoring. The stored passwords tie the code to unsalted SHA-256. |

## Step 7: which unit could you regenerate alone?

**The world**, now: it is data (`world.json`) with its schema and one
feature, and nothing else writes it. **The chat could not be regenerated
alone**, for three reasons:
- it reads and writes the player state (the location, and the move count:
  CHAT-3 counts a message as a move);
- it has no port in `kata.py`;
- it lives in both `api.py` and `game.py` (the rewrite moved it to `game.py`).

Accounts have the same problem: the stored hashes and snapshots tie them to
the save format. The failing tests of step 5 were not sorted into gameplay,
accounts and chat: no time.

## Step 7: recovery score

A decision counts when it is in the Specification or a decision record,
with its source.

| The step that showed it | Count | Which |
| --- | --- | --- |
| Step 1: the archaeology listed it | 52 | The 52 items of `archaeology.md`; items 7 and 10 got their rule (WORLD-2) only in step 7. |
| Step 1: you played the game, or read the code | 0 | Nobody played in step 1; the agent that read the code wrote the archaeology. |
| Step 4: the boundary, and the data ownership table | 2 | Each refused game action answers 405 (`x-status-by-reason`); `game.py` and `api.py` both write the player state, which puts the energy gate in the route (MOVE-5). |
| Step 5: a test that failed | 1 | The market reads the server's local clock, so its hours depend on the time zone (decision 0001). |
| Step 7: the regenerated code lost it | 2 | The world itself (WORLD-1, run 1); the tier of the energy gate is part of the port boundary (the rewrite). |

Setup findings of step 7, not decisions of the game: the bare `uv run
pytest` fails at collection; the README copy lists leave out `web/spec/`
(regeneration) and `decisions/` (rewrite), which `test_spec_status.py` reads.
