---
name: evaluate
description: Writes the Evaluation primitive — durable checks that every correct implementation must pass — as Given-When-Then scenarios bound to rule IDs at a stable boundary, plus fitness functions, and the rule-to-scenario map. Also writes characterization scenarios for legacy code, and reviews existing tests for checks that pin implementation details. Use after the rules and contracts exist, before the code, when a rule changes, or when the user says "write the tests", "write the acceptance scenarios", or "phoenix evaluate".
argument-hint: '[rule IDs to cover, "characterization <rule IDs>" for code that exists, or "review" to audit existing tests]'
license: MIT
metadata:
  author: phoenix-kit
  version: "0.1.0"
---

# Evaluate

Write the checks that outlive the code. The test is one question: if the
system were rewritten in another language, would this suite still be
valid? If not, the suite checks the wrong boundary.

## Paths

Read `PHOENIX.md` at the project root for the tests folder, the test
command, and the rule-to-scenario map. `check` means `python3
<kit>/scripts/phoenix_check.py`, from the project root; `<kit>` is two
folders above this file. Run the Requires first and the Ensures last
([CONTRACTS.md](../../CONTRACTS.md), "Run the checks").

## Steps

```
- [ ] 1. Read            — done: `check rules` passes; rules, deltas, contracts, conventions known
- [ ] 2. Scenarios       — done: each rule in scope has a scenario at a stable boundary
- [ ] 3. Limits          — done: each OPS rule has one measured test
- [ ] 4. Fitness         — done: each row of each Fitness functions table has a check
- [ ] 5. Audit           — done: each check is an oracle, moved, or marked Ephemeral
- [ ] 6. Map and run     — done: `check trace` passes; new scenarios fail (characterization: pass); approval cleared
```

With `review` as the argument, do only step 5 on the existing tests.
Write no new check. Report each finding.

With `characterization` first (from `/phoenix-kit:assess`), the code
exists and the rules record what it does today: do all the steps, and
in step 6 the new scenarios must pass. Otherwise they must fail first.

### 1. Read

The rules give the observable results. The contract gives the shapes. The
existing tests show the conventions (tags, fixtures, the ways in): keep
them. The open deltas are part of the Specification: read every
`spec/changes/<name>/delta.md` outside `archive/`. A delta rule replaces
the rule with the same ID, and it needs a scenario like any other rule.

### 2. Scenarios

Use [assets/scenario-template.feature](assets/scenario-template.feature).
The runner is pytest-bdd: bind each `<name>.feature` in
`tests/steps/test_<name>.py`, with `scenarios("../<name>.feature")` and
the step functions. For each rule in `$ARGUMENTS`, or with no scenario:

- Tag the scenario with the rule ID (`@BAG-1`) and the way in
  (`@port` or `@api`). A rule that both ways reach gets both.
- Given the state, When the command, Then the observable result from the
  rule. Nothing else.
- Each error path is a scenario. Its Then names the error reason.
- A rule with many cases is a scenario outline with an examples table.
- Reach the system only through its boundary: the published ports or the
  API contract.

### 3. Operational limits

Each `OPS` rule gets one test that measures the number the rule names and
asserts the target. Mark it so it can run on its own. It simulates the
Live tier: say in the map that production monitoring must check the
same limit against real traffic.

### 4. Fitness functions

Each decision record with a Fitness functions table gets one automatic
check per row: an import rule, a complexity limit, a latency measure, a
"each rule has a scenario" check. Tag it `@fitness` and the decision
number: in Python, `@pytest.mark.fitness`, with the marker registered in
`pyproject.toml`. A fitness function must fail when the system drifts.

### 5. Audit: oracle or ephemeral test

An oracle checks observable behavior and survives a rewrite. An ephemeral
test checks how the code does the work and fails on a correct rewrite.
Signs of an ephemeral test:

- It counts calls to a mock.
- It asserts an exact log message.
- It asserts the order of calls when the order is not in the contract.
- It reads internal state, or imports an internal module.

Move each ephemeral test to the boundary, or mark it **Ephemeral** and
keep it next to the code, outside the Evaluation. Report each one.

Two more faults make a check worthless, oracle or not (adapted from
Matt Pocock's `tdd` skill, MIT):

- **Tautological**: the expected value is computed the way the code
  computes it, so the check passes by construction. Take the expected
  value from the rule, the brief, or a worked example.
- **Cannot fail**: no assertion, an assertion that holds for any
  result, or a setup that never reaches the rule. Name one wrong
  implementation that each check catches, or fix the check. The empirical
  pass of `/phoenix-kit:deletion-test` proves it on a copy.

### 6. The map

Update the rule-to-scenario map with
[assets/test-scenarios-template.md](assets/test-scenarios-template.md).
Every rule ID appears once, open deltas included. The table "Rules with a
partial check" is the honest record of what a green suite does not prove.
Run `check trace`: each rule has a scenario tagged with its ID, each tag
names a rule, and each rule is in the map. If it fails, fix the tag or
the map row that it names. Then run the test command. Normal mode:
before the code exists, the new scenarios must fail; one that passes
does not reach the system, so fix the setup. Characterization mode: the
new scenarios must pass against the existing code; one that fails shows
that the test or the observed rule is wrong, so fix that, not the code.
After each fix, run the check again, three passes at most. If it still
fails, stop and report the finding with its file and line (CONTRACTS
rule 2).

Then run `check approval clear`. The scenarios are not the oracle until
a person reviews them and runs `check approval stamp`: this skill, as the
generator, writes tests that share its assumptions.

## Report

- Scenarios, operational tests, and fitness functions, by rule ID and way in.
- Ephemeral tests, tautological checks, and checks that cannot fail, and
  what you did with each.
- Rules with a partial check, and why.
- Next: in a change, the item after `evaluate` in the hand-off list
  ([`/phoenix-kit:change`](../change/SKILL.md), step 4). From `assess`,
  its work plan. Otherwise `/phoenix-kit:decide` if the rules need it;
  then a person reviews the suite and runs `check approval stamp`.

## Guardrails

- Each check reaches the system through its boundary: the published
  ports or the API contract.
- Each check asserts an observable result of a rule: a message, an error
  reason, a value, or a state that a later query shows.
- A scenario that fails before the code exists is correct. It keeps its
  meaning until the rule changes. Characterization keeps the code as is.
- Tests and comments name the rule ID and the decision, not the name of
  the open change: that name goes stale on archive.
- The unit tests of the implementation belong to `/phoenix-kit:generate`:
  they share the assumptions of the code.
