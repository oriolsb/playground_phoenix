# Grades of the four primitives

## Step 3: the system as it was found

The grade of the legacy system before any primitive was added (commit
`90891ef`, "The original legacy system"), against "What good looks like"
in the README. Step 7 adds its grade in the last column.

| Primitive | Grade (step 3) | Gap | Grade (step 7) |
| --- | --- | --- | --- |
| Specification | absent | Only the brief, which is older than the code and wrong on the bag (10 items; the code has 8 slots of 3). It says nothing of energy, the market hours, the rat, accounts, chat, the save or the restart. No rule has an ID, a source or a reason. Each rule exists only as an `if` in `game.py` or `api.py`. | |
| Evaluation | absent | No test of the server. The web client has test tools in `package.json` (Vitest, Testing Library, MSW, Playwright) and no test. Nothing tells correct behavior from incorrect without the old code. | |
| Context Boundary | partial | The ports of `kata.py` exist, small and typed, but the accounts and the login have no port, and the domain Player has no energy. FastAPI generates `/openapi.json` from the code, after the fact: an API that only the code describes. The answers are hand-made dicts; the save payload, the accounts table and the high-score line have no schema and no version. `api.py` and `game.py` both change the player and the world. No vocabulary: "exit" means two things, "move" counts more than moves. | |
| Provenance | partial | No decision record. About 12 comments keep a reason or an incident (INC-2231, INC-3110, "Product asked… (2022)", "Cleaning crew contract (2023)", "Marketing, 2024", the mobile release), and two say outright that the reason is lost ("Nobody wrote down why"). 27 of the 52 items of `archaeology.md` are unknown. | |

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
