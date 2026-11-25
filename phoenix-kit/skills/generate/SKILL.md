---
name: generate
description: The one controlled implementation prompt. Generates the production code and its unit tests from the four primitives only, runs the Evaluation until it passes, and stops with a report when a primitive is incomplete, contradictory, or impossible. Adds no requirement and makes no design decision. Runs only when the user invokes `/phoenix-kit:generate`, after the primitives exist, in a fresh session.
argument-hint: "[optional: the unit to regenerate]"
disable-model-invocation: true
license: MIT
metadata:
  author: phoenix-kit
  version: "0.1.0"
---

# Generate

The primitives hold every decision; this prompt adds none. It turns them
into code and stops when they are not enough. Run it in a new session.

## Paths and checks

Read `PHOENIX.md` at the project root: the primitives, the code path, the
entry point, and the test commands. If it is missing, stop. `check` means
`python3 <kit>/scripts/phoenix_check.py`; `<kit>` is two folders
above this file. Its Requires, Ensures, rules, and report file:
[CONTRACTS.md](../../CONTRACTS.md).

## Steps

```
- [ ] 1. Approval and baseline — done: `check approval verify` passes; git status is empty
- [ ] 2. Read every primitive  — done: each one in scope read from disk in this session
- [ ] 3. Run the Evaluation    — done: the check of step 3 passes
- [ ] 4. Generate              — done: code and unit tests written; each module cites its rule IDs
- [ ] 5. Repair loop           — done: the suite passes, or 3 runs, or a specification failure
- [ ] 6. Specification failure — done: the report is written; nothing was guessed
- [ ] 7. Rule review           — done: each finding is fixed in the code or reported
- [ ] 8. Integrity and report  — done: git status empty; `check trace` passes; report file
```

### 1. Approval and baseline

Run `check approval verify`. It passes only when a person stamped this
exact suite and map, after the contract and the decisions were final. A
human-approved Evaluation is the oracle. If the check fails, stop.

The primitives must be committed, approval line included. Run
`git status --porcelain -- <primitive paths from PHOENIX.md>`. The output
must be empty; if it is not, stop and ask the user to commit. Git ignores
caches, so a test run is not a change. Outside git, record a baseline as
[assets/outside-git.md](assets/outside-git.md) says.

### 2. Read

Read the specification, the Terms, every decision record, the contracts,
the rule-to-scenario map, and the Evaluation suite. Read them from disk,
not from memory of an earlier turn.

Old code: for the whole system, read none. For one unit, read the code
outside the unit, because the new code must fit the names it imports and
exports. The removed unit stays removed: recover nothing of it with
`git show`, `git log -p`, `git diff`, or `git stash`.

The open deltas are part of the Specification: read every
`spec/changes/<name>/delta.md` outside `archive/`. A delta rule replaces
the rule with the same ID.

If `$ARGUMENTS` names one unit, `check units show <unit> --json` gives
its rules, interface, and modules in `data.unit`. Read only the rules,
decisions, and scenarios that cite it, the contracts it crosses, and the
open deltas it touches.

### 3. The scenarios in scope must fail

Before you write code, run `check expected check --run`: it runs the suite.

- Whole system: with no trailers on the commit, it passes only when the
  suite does not collect or every test fails. With no `junit_command`,
  run the test command and judge by hand. If a test passes, stop.
- One unit, after a change: a person removed the unit's behavior on a
  branch, kept each name that other code imports, and ended the commit
  with `Phoenix-Expected-Fail` trailers (`/phoenix-kit:change`, step 6).
  The check compares the failures with the trailers. It needs git:
  outside git, regenerate the whole system. Stop on each error, and here:
  - no list (`data.mode` is `whole system`): ask the person to run
    `check expected record`;
  - the suite does not collect, or every test fails: the removal deleted
    a name that other code imports; list the names;
  - a failure not on the list: the removal went too far;
  - a listed test passes: this is not the branch the person tested.

  A stop is final, even when the cause looks harmless: the person
  decides, then runs this skill again. The unit stays as the person left
  it. Use the "Generation stopped" report in
  [assets/reports.md](assets/reports.md).

### 4. Generate

Write the production code in the code path, with the entry point the
Evaluation imports. Follow each decision record: the architecture style,
the module boundaries, the technology stack. Each module docstring cites
the rule IDs it implements. Write unit tests for the code in the
unit-test path. Take each expected value from a rule, the brief, or a
worked example: a test that computes its expected value the way the
code does cannot fail. These tests share the assumptions of the code;
the Evaluation is the oracle.

### 5. Repair loop

Run the test command. For each failure, find its kind:

- **Implementation failure**: the primitives are correct, and the code
  does not satisfy them. Fix the code. Run again. Count the iteration.
- **Specification failure**: the code, or the attempt to write it, shows
  a gap, a contradiction, or an impossibility in a primitive: step 6.

Stop after three iterations of this loop, and report what still fails.

### 6. Stop on a specification failure

The primitives, the tests, and the design choice stay with the person.
Write the "Specification failure" report from [assets/reports.md](assets/reports.md)
and stop. The user fixes the primitive, runs `/phoenix-kit:decide`, and
runs this skill again in a new session.

### 7. Rule review

A second, independent check reads the code against the rules. Start a
subagent in a new context with [assets/rule-review.md](assets/rule-review.md),
and handle each finding as that file says. A finding that needs a rule
change is a specification failure: go to step 6.

### 8. Integrity check and report

Run `git status --porcelain -- <primitive paths>` again (outside git,
compare with the baseline). Run `check trace`: each rule has a scenario;
list the rules that no module cites. Report each output as it is. If a
primitive changed or a rule has no scenario, stop: write the "Generation
stopped" report with the paths or rule IDs. The person decides. Else
write the "Generation report" from [assets/reports.md](assets/reports.md).
These checks run inside the agent, so a person or CI also runs
`git diff --exit-code -- <primitive paths>` before the merge.

## Guardrails

- The specification, the decisions, the contracts, and the suite stay
  as they came in.
- Each requirement and design choice comes from a primitive. A missing
  one is a specification failure.
- A failing test is repaired in the code; the test keeps its meaning.
- Knowledge comes from the primitives only. A gap in them is the finding.
- A stop in step 1, 3, or 8 is final. The checker decides it, not a
  judgement of the cause: [assets/excuses.md](assets/excuses.md).
