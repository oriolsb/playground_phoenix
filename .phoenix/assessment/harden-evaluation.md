# Plan: harden the Evaluation of game-server

Date: 2026-11-25. Starting point: the Deletion Test after step 7
(`.phoenix/reports/deletion-test-20261125-1519.md`). Verdict: risky. Grade
of the Evaluation: partial. 40 mutants were run: 29 were killed, 11
survived, and 6 of the survivors are observable.

**Goal:** a regenerated game-server cannot change an observable behavior
with every test green. **Constraint:** characterize only. No change to
`game.py` or `api.py`. Every new check passes on the original code today.

**Done when:**
- The Deletion Test grades the Evaluation strong.
- Every surviving mutant is either killed or listed as unobservable, with
  its reason.
- A bare `uv run pytest` runs the suite.
- Every new check also passes on the regeneration of run 2, so it pins
  behavior, not the implementation.

## Phases, in the order of risk

### 1. The test command (15 min)

- Add `testpaths = ["brown_field/tests"]` to `[tool.pytest.ini_options]`.
  A bare `uv run pytest` fails at collection today: `pytest_plugins` is in
  a conftest that is not top-level.
- Make the inputs of `fitness/test_spec_status.py` explicit. It reads
  `web/spec/` and `decisions/`, which the README copy lists leave out.
  Fail with a message that names the missing folder, not a bare
  `FileNotFoundError`.

**Check:** `uv run pytest` runs 189 tests from the package root.

### 2. Close the 6 observable survivors (1 h)

One characterization scenario for each, through the REST API:

| Survivor | Scenario | Rule |
| --- | --- | --- |
| The rat's chance is 1 in 5 | At `random.random()` 0.19 the rat steals; at 0.2 it does not. The `rat` fixture gains `at(value)`. | MOVE-8 |
| The rat takes only an item of value 0 | A player carries the SKULL (value 5) into the cellar with the rat always running; the SKULL stays | MOVE-8 |
| An email needs one `@` at least | `a@b@c` registers; `abc` is refused | ACCOUNT-2 |
| A login skips a snapshot at a lost location | The golden database gets a snapshot at `NOWHERE`; the login gives the active player, else a new one | ACCOUNT-4 |
| A login restore at 20 players is refused | 20 players are active; the login of an account with a snapshot answers 405 `THE KATACOMBS ARE FULL. TRY AGAIN LATER.` | ACCOUNT-4 |
| Saves load in the order of `saved_at` | Two players save in turn; after a restart, `GET /game/player` lists them in save order | STORE-1 |

Also:
- Extend the rules ACCOUNT-4 and STORE-1 with these results, and state in
  PLAYER-1 that a sid is unique.
- Mark the two login cases contested. They follow the rollback that
  ACCOUNT-4 already questions.

**Check:** run the mutation harness again. The 6 survivors are killed.

### 3. The clock in another time zone (15 min)

The clock test cannot tell local time from UTC on a machine that is a
whole number of hours from UTC. Run the MOVE-6 scenarios a second time
under `TZ=Asia/Kolkata` (UTC+5:30): a pytest parameter that sets `TZ` and
calls `time.tzset()`.

**Check:** the "market reads UTC" mutant is killed.

### 4. Find what no test runs (30 min)

Measure branch coverage of `game.py` and `api.py` under the suite. This
needs `pytest-cov`, a new dev dependency. Each unexecuted branch is a
candidate survivor: write one more mutant for it, and a scenario when it is
observable. Do not chase a percentage. The list of unexecuted branches is
the finding.

### 5. Invariants that hold for any sequence (1–2 h)

A Hypothesis stateful test (`RuleBasedStateMachine`) plays random
commands through the REST API and checks, after each one, what must
always hold:

- **Conservation:** each item of `world.json` is in exactly one place, a
  location or one bag. The rat and the legacy pickup move items and never
  copy them.
- **Score:** BAG-2 holds at every step: score = gold + the value of each
  item.
- **Limits:**
  - energy stays from 0 to 20;
  - the bag uses at most 8 slots of 3 items, except after the legacy pickup
    (LEGACY-1);
  - at most 20 players are active.
- **Monotonic:** the move count and the gold never decrease; a player who
  has won stays won.
- **Boundary:** every answer validates against `openapi.yaml`, and every
  error has its status from `x-status-by-reason`.

The clock is fixed at minute 10 and the rat never runs. This finds classes
of bug that no single scenario names. A failing example is shrunk to a
short sequence; pin it as a scenario.

**Check:** run 200 examples by default, and 5,000 in the mutation run.

### 6. Recorded answers: the differential check without the old code (1 h)

The step 7 differential needed the original code. Record its answers
instead:
- Store the 12 seeds × 400 requests and the 84 scripted steps as golden
  transcripts in `tests/golden/transcripts/`, written by the original code.
  Sids are normalized, the clock is fixed and the rat never runs.
- Add a replay test that sends each request and compares each answer and
  each file.

The transcripts then survive a deletion.

**Risk:** a transcript pins everything, including behavior that nobody
decided. Keep it out of the rule map. Mark it `@contested`-aware: when the
group changes a contested rule, they record the transcript again on
purpose, in the same commit as the decision record.

### 7. Mutation as a fitness function (1 h)

Make the mutation pass repeatable and independent of the implementation:
- Use `mutmut`, a new dev dependency, on `brown_field/game.py` and
  `brown_field/api.py`. It works on any implementation, so it also runs on
  a regenerated one. The hand-written mutants match only the legacy text.
- Keep the 40 hand-written mutants as `tests/fitness/mutants.md`: each one,
  its rule and its result.
- Run it on demand (`-m mutation`), not on every commit. It takes minutes.
- **Target:** every surviving mutant is listed with a reason ("not
  observable", "equivalent", "contested") or killed.
- Record the target in a decision record (0010), with the rejected
  alternative of a kill-rate percentage.

### 8. Across tiers (30 min)

- Run the 52 Vitest tests and the 2 Playwright tests against the run 2
  regeneration. The browser test starts `python -m brown_field`, so point
  it at that folder.
- For a group with a frontend developer: regenerate `web/src/` the same
  way (the README stretch item), then run `npm test` and
  `npx playwright test`.

## After the plan

1. Run the Deletion Test again. The Evaluation must grade strong.
2. Regenerate once more (run 3) from the hardened primitives.
3. Then Provenance:
   - decide MOVE-5;
   - write a record for each contested rule the group decides, and for the
     password hash;
   - confirm or move the 28 guessed reasons.

## Result (2026-11-25, branch `worktree-harden-evaluation`)

| Phase | Done | What it added |
| --- | --- | --- |
| 1 | yes | `testpaths`; a bare `uv run pytest` runs the suite. `test_spec_status.py` names a missing input folder. |
| 2 | yes | 6 scenarios: the rat at 0.19 and 0.2, the SKULL, `ana@example@org`, the login restore when the game is full, a snapshot at a lost location (2 cases), the save order. Wording added to PLAYER-1, ACCOUNT-2, ACCOUNT-4 and SAVE-2. |
| 3 | yes | MOVE-6 under Asia/Kolkata and America/St_Johns. |
| 4 | yes | 99 % branch coverage. 1 real gap (a quit with two accounts), now a scenario; the rest are unreachable. |
| 5 | yes | `fitness/test_invariants.py`: a Hypothesis state machine, 50 examples. A planted copying bug is caught in 8 of 8 runs. |
| 6 | yes | 7 golden transcripts (1,896 lines), and the replay test. |
| 7 | yes | `fitness/mutation/` (42 hand-written mutants) and mutmut (1,084 generated). 11 more real gaps found by mutmut, now 5 scenarios. Every survivor is listed with its reason. Decision 0010. |
| 8 | yes | Playwright, 2 of 2, against the run 2 server. Vitest does not reach a server. |

Every new check passes on the original code and on the run 2 regeneration
(218 of 218). The one-prompt rewrite fails exactly 1: the energy gate in the
move port.
