# Brown Field Retrospective

The retrospective is a conversation first. This file holds the share-out
and the lessons that the record of the day supports. **An agent wrote
this draft** from the commits, `grades.md`, `archaeology.md` and the
session logs. Every "we" below means the group and its agent. Sections 3
and 4 belong to the group: they are left for the conversation.

Group: (to fill in)
Date: 2026-11-25
Repository: `https://github.com/oriolsb/playground_phoenix`, baseline `90891ef`

## 1. Share-out summary

### Primitive grades from step 3 and step 7

| Primitive | Grade in step 3 | Grade in step 7 | Evidence |
| --- | --- | --- | --- |
| Specification | absent | strong | 74 server and 28 client rules, each with a source, a status and a result. With `world.json` added, a fresh agent rebuilt the server from one prompt. The first run stopped: the world was only in the code. |
| Evaluation | absent | strong | 189 server tests, 52 client tests, 2 browser tests; `check trace` 74 of 74. They caught the one behavior change of the rewrite. Before step 7, a made-up world could have passed. |
| Context Boundary | partial | strong | `openapi.yaml` (16 operations), 3 JSON Schemas, Terms, data ownership, the seams of decision 0008. Both new versions kept every name. Open: the tier of the energy gate (MOVE-5). |
| Provenance | partial | partial | 9 decision records and a status on each rule, but 31 rules are contested and 28 reasons are guesses. |

### The three questions, in step 3 and step 7

| Question | Step 3 | Step 7 |
| --- | --- | --- |
| Can you merge an agent's change without reading every line? | no: no test, no contract | yes, inside what the tests cover; not a change to a contested rule |
| Can an agent implement a change from one prompt? | no: 27 behaviors with no reason, a wrong brief | yes, after the world primitive (run 2: one prompt, no corrections) |
| Can you release the change without anyone watching production? | no | no: the marketing job and mobile client v1 are outside the repository; OPS-1 needs production monitoring |

### The archaeology of step 1

| Items on the list | Known | Unknown | Wrong |
| --- | --- | --- | --- |
| 52 (38 server, 14 client) | 25 | 27 | 0 |

The marks are the agent's proposals. The group has not confirmed them.
No item is wrong, but the same agent read the code and wrote the tests, so
a misreading could pass both.

### Decisions that nobody wrote down

The full list is the 52 items of `archaeology.md`. The ones that shaped
the day:

| Decision | How you found it | Decision record or source tag |
| --- | --- | --- |
| The market closes in minutes 50 to 59, on the server's local clock | archaeology; a failed test showed the time zone | 0001, MOVE-6 |
| The high-score file keeps its format for the marketing job | archaeology (comment) | 0002, WIN-3, CONF-2 |
| The legacy pickup route stays for mobile client v1 | archaeology (comment) | 0003, LEGACY-1, LEGACY-2 |
| A repeated take succeeds (INC-2231) | archaeology (incident) | 0004, ACT-5 |
| The game is saved to SQLite (INC-3110) | archaeology (incident) | 0005, SAVE-1, STORE-1 |
| The cellar slide goes one way | archaeology; got a rule only in step 7 | 0009, WORLD-2 |
| The world itself: titles, exits, gold, items, sids | the regeneration lost it (step 7) | WORLD-1, `spec/world.json` |
| The energy gate lives in the REST route, not the port | the boundary (step 4); the rewrite moved it | MOVE-5, contested |
| Each refused game action answers 405 | the boundary (step 4) | `x-status-by-reason`, API-2 |
| A login rolls the player back to the last quit | archaeology | ACCOUNT-6, contested |

### Regeneration in step 7

| Item | Result |
| --- | --- |
| In the regeneration folder, before the agent runs, `pytest` fails with an `ImportError`: yes or no | yes, both runs: `ModuleNotFoundError: No module named 'brown_field.api'` |
| Files that the agent opened | only the folder: `spec/`, `web/spec/`, `decisions/`, `tests/` with the golden SQLite files, `kata.py`, `__init__.py`, `__main__.py`, `pyproject.toml`, and its own tool-output files |
| Tests that passed | run 1: none (it wrote no code); run 2: 189 of 189 |
| Tests that failed | none in run 2. A bare `uv run pytest` fails at collection, in this package too |
| Knowledge that each failure showed | run 1: the world was in no primitive. Run 2: the test command depends on a path. Our copy list needed `web/spec/` |
| Boundary terms with more than one meaning | none new. Open since step 4: "exit" (a direction, and the katacombs exit); "move" (the move count also counts actions and chat) |

### The one-prompt rewrite of step 1

| Item | Result |
| --- | --- |
| Would you merge it after the 5-minute reading? Why? | Not judged by a person: the agent ran it late and nobody read it in 5 minutes. On the record: not yet. It decides MOVE-5 with no record, and leaves `.scratch/` in the tree |
| Tests that failed on the rewrite | 1 of 189: "the move port has no energy gate" (`ports/ports.feature`) |
| Changes that the reading did not see | the rewrite's report says "all game rules live here now", with no hint that a port caller now gets a refusal |
| Tests that failed because the rewrite moved a boundary name | none moved a name; it moved a behavior across the port boundary |
| Did the agent check its own work? Where is that check now? | Yes: 77 tests and about 320,000 differential REST requests against the legacy code. Both are in its folder (`tests/`, `.scratch/`), outside any primitive, and they need the legacy code to run |

## 2. Lessons

1. **Which decisions nobody wrote down, and how we found them.** The
   archaeology found 52, and the comments gave a reason for 25. The
   regeneration found the biggest one: the world. The archaeology had
   listed its parts (items 7, 9 and 10), but a rule ID in its last column
   looked like coverage. GOLD-1 named the gold and held no amount. The
   boundary found two (the 405 map, the energy gate in the route). A failed
   test found one (the market's local clock). Nobody played the game.
2. **The most difficult primitive was Provenance.** The code holds the
   "what" completely: a script can characterize it. It holds the "why" only
   where someone left a comment or an incident number. For 27 items no
   reading of the code can give the reason; only a person can.
3. **Rules not reachable from outside, and the seams.** No code was edited
   for a seam (decision 0008): `create_app(game)`, the stdlib clock and
   `random.random`, `KATACOMBS_DB` and `KATACOMBS_HIGHSCORES`, and the port
   tier. The start-up world check (WORLD-2) can't be reached at all. The
   world is fixed, so the check never fails from outside; it is only in
   the rule.
4. **The regenerated code and the rewrite.** The regeneration passed 189 of
   189. The rewrite passed 188 of 189. Both matched the original on 4,800
   random and 84 scripted requests. The one failure was the most
   instructive result of the day: a change that every REST check called
   equal, and that only the port tier saw. Nobody read the rewrite in
   5 minutes, so the reading-versus-tests comparison is still open.
5. **The three questions.** Questions 1 and 2 moved to yes. Question 3
   stays no. It would change with a check of each outside consumer, and
   with production monitoring for OPS-1:
   - a contract test that the marketing job runs on the high-score file;
   - a test of the mobile v1 route from the mobile side.
6. **Green field or brown field?** For the group: the agent was not part of
   day 1. On the record, recovering the "what" was cheap (characterization,
   scripts). The "why" was not.

**What the agent got wrong today, and how it was caught:**
- It wrote guessed reasons as if they were known, until step 6 marked
  them.
- It miscounted the comments (13, then 12).
- Its first differential check compared the original with itself: the
  installed package shadowed the path. Checking which module each run
  imported caught it.
- The copy lists of the README missed two folders that our own fitness
  test reads.

## 3. Apply it in your team

For the group to answer in the conversation.

| Question | Answer |
| --- | --- |
| Which component in your team does someone want to rewrite? Ask an agent to list its scars, and mark them. How long is the unknown column? | |
| Which system in your team is most similar to this brown field? It works, but it has no written primitives. | |
| Which knowledge in that system exists only in the code, or only in the memory of one person? | |
| What is the smallest first step for that system: a contract, characterization tests, or decision records? | |
| Where does your team keep decision records that you write after the code? | |
| How does your team add seams to legacy code, and keep the behavior the same? | |
| An AI coding agent changes legacy code. Which checks must pass before the change can merge? | |

## 4. What will you try?

For the group: one sentence. Choose the practice, its owner and its start
date at the workshop close, on day 3.
