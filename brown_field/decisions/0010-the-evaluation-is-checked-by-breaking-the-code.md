# 0010 — The Evaluation is checked by breaking the code, by invariants and by recorded answers

- **Status:** accepted
- **Date:** 2026-11-25
- **Need:** a regenerated game-server must not change an observable behavior with every test green.
- **Traces to:** `MOVE-8`, `MOVE-6`, `ACCOUNT-2`, `ACCOUNT-4`, `SAVE-2`, `BAG-2`, `BAG-3`, `API-2`.
- **Change:** None to the code. New checks only.
- **Evidence:** the Deletion Test after step 7
  (`.phoenix/reports/deletion-test-20261125-1519.md`). 40 mutants of the legacy
  code were run: 11 passed every test, and 6 of those were observable. Before
  that, the one-prompt rewrite moved the energy gate. Its own 320,000 REST
  requests did not see the move; only the port tier did.

## Context

The characterization suite covered every rule: `check trace` gave 74 of 74.
But a rule with a scenario can still have a gap. The rat's 1 in 5 was in
MOVE-8, and no test pinned the threshold. A green suite says nothing about
the behaviors that no scenario names.

## Decision

The Evaluation gets three fitness functions on top of the scenarios:

1. **Mutation** (`tests/fitness/mutation/`). `run_mutants.py` breaks the
   code one rule at a time, in a copy, and runs the suite. Each survivor
   needs a row in `mutants.md` with its reason: not observable, or not
   reachable. A survivor with no row fails the run. It runs on demand,
   because it takes minutes.
2. **Invariants** (`tests/fitness/test_invariants.py`). A Hypothesis state
   machine plays random commands through the REST API. After each one it
   checks that:
   - no item is in two places;
   - the score is the gold plus the item values;
   - energy stays in 0 to 20, and there are at most 8 bag slots and 20
     players;
   - gold never goes down, and a win is never undone;
   - each answer matches the contract.

   Restarts, saves and accounts are left out: SAVE-2 and ACCOUNT-4 can
   copy an item by design.
3. **Recorded answers** (`tests/fitness/test_transcripts.py`). Seven
   sessions of requests that the legacy code answered:
   `golden/transcripts/`, written by `golden/make_transcripts.py`. The code
   under test must give the same answers and write the same files. This is
   the step 7 differential, without the old code.

A new check is kept only if it passes on the original code and on the step 7
regeneration (run 2). That proves it pins behavior, not the implementation.

## Alternatives rejected

| Alternative | Why you rejected it |
| --- | --- |
| A kill-rate target (for example 90 %) | A percentage hides which behaviors are open. A named survivor with its reason does not. |
| Only a generic mutation tool (mutmut) | It mutates any implementation, but its mutants have no rule and no reason. The hand-written mutants each trace to a rule. Both can run. |
| The differential against the old code | The old code is what a Deletion Test deletes. The recorded answers survive it. |
| Record transcripts with the real rat and the real clock | Then the answers would depend on the order of calls to `random`, and on the machine's time zone: implementation details. |

## Consequences

- A behavior change on purpose has to record the transcripts again
  (`make_transcripts.py`) in the commit of its decision record. Otherwise
  the replay fails.
- The hand-written mutants match the text of the legacy code. On a
  regenerated implementation they report "not applicable": use mutmut there.
- The suite takes about 15 s instead of 4 s. The hand-written mutants take
  about 10 minutes, and mutmut about 3.
- When a table is created is not recorded. An empty table and a missing one
  read the same: the run 2 regeneration creates `accounts` early, and the
  legacy code creates it on the first account.

## Fitness functions

| Function | Target | How to run it | Need that it protects |
| --- | --- | --- | --- |
| Every mutant killed or listed | 0 unlisted survivors | `uv run python brown_field/tests/fitness/mutation/run_mutants.py`; `uv run mutmut run` | No silent change in a regeneration |
| Invariants after any sequence | pass, 50 examples; 2,000 on demand | `KATACOMBS_EXAMPLES=2000 uv run pytest -k invariants` | Item conservation, score, limits |
| Recorded answers | 7 of 7 transcripts match | `uv run pytest -k transcripts` | Every observable answer of the legacy code |
