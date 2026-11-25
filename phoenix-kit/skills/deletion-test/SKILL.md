---
name: deletion-test
description: Runs the Deletion Test on a unit or a whole system — what survives a deletion, what knowledge is lost, which consumers break, whether an evaluation would notice, and a verdict (replaceable, risky, unverifiable). Use before calling work complete, on a legacy component, before a regeneration, or when the user says "deletion test", "can we regenerate this", or "phoenix deletion-test".
argument-hint: '[the unit to delete, or "all"]'
license: MIT
metadata:
  author: phoenix-kit
  version: "0.1.0"
---

# Deletion Test

"If I deleted this codebase and regenerated it from scratch, what would I
rely on to decide whether the result was correct?" If the honest answer is
"the old code", the code is the specification, the test suite, and the
documentation at the same time. This skill makes the two lists.

This is the Phoenix Deletion Test: what survives when the code goes.
Some design guides use the same name for a module test (is a module
only a pass-through?). That test is not this one.

## Paths

Read `PHOENIX.md` at the project root for the primitives and the code
path. Defaults: `spec/` and `tests/`. With no `PHOENIX.md`, `check
config` fails: stop, and tell the user to copy a preset from the kit's
`templates/` to the project root (README, "Set up a project"). `check` means `python3 <kit>/scripts/phoenix_check.py`,
from the project root; `<kit>` is two folders above this
file. Run the Requires first and the Ensures last
([CONTRACTS.md](../../CONTRACTS.md), "Run the checks").

## Steps

```
- [ ] 1. Unit, inventory — done: `check config` passes; each file has one class
- [ ] 2. What survives   — done: each surviving file is named with its primitive
- [ ] 3. What is lost    — done: each item has a file, a line, and a primitive to hold it
- [ ] 4. Four properties — done: each property has a finding
- [ ] 5. Grades, verdict — done: each grade uses the table of step 5
- [ ] 6. Empirical pass  — done (optional): the suite failed without the code, then ran
- [ ] 7. Report          — done: the report file is written; the summary is in the conversation
```

### 1. Unit and inventory

The unit is `$ARGUMENTS`: one module, one service, or `all`. Enumerate
with `git ls-files`. In a folder that is not a git repository, use
`find . -type f -not -path '*/.git/*' -not -path '*/.venv/*'` instead.
Also list `.phoenix/` with `find .phoenix -type f`: git ignores it, so
`git ls-files` does not show its reports and assessments.
Then give each file one class: **primitive** (it survives, step 2),
**code** (under the code path, or its unit tests), **tool** (the build
files, the lock file, the kit), or **scaffolding** (reports,
conversations, caches, assessments). Assess this inventory, not a list
that someone hands you: a supplied scope can omit exactly the
scaffolding the test exists to find.

### 2. What survives

Specifications, contracts, schemas, the vocabulary, decision records, the
Evaluation suite, the rule-to-scenario map, the open deltas in
`spec/changes/`, `PHOENIX.md`. Name each file.

### 3. What is lost

Read the unit's code for knowledge that no primitive holds:

- A rule that exists only as code behavior.
- A timeout, a retry count, a limit, a special case, or a defensive check
  with no rule and no decision (scar tissue).
- A name that other code imports, with no contract that declares it.
- A term the code uses that Terms does not define.
- A test that only an implementation detail can satisfy.

Each item is one line: file, line, what it knows, which primitive should
hold it. This list is the work plan.

### 4. The four properties

A single deletion reveals four properties (from Chad Fowler's `phoenix`
reference implementation, MIT):

| Property | Question | How to check |
| --- | --- | --- |
| Boundary clarity | Which consumers break that the contract did not declare? | Grep for imports and calls into the unit. Compare with the contract and the ownership table. |
| Evaluation coverage | Would any durable check notice the deletion? | `check trace --json`: `data.coverage` gives the number of scenarios of each rule. None means the unit is dead weight or an evaluation gap: say which. |
| Coupling depth | How far does the blast reach? | Follow the consumers of the consumers. Three hops or more is deep. |
| Replaceability | Can it be regenerated and verified without the old code? | The verdict below. |

### 5. Grades and verdict

Grade each primitive for the unit: **strong**, **partial** (gaps; a
regeneration is incomplete), or **absent** (a regeneration fails in
silence). Strong means, for each primitive:

| Primitive | Strong means |
| --- | --- |
| Specification | Every rule of the unit has an ID, a why, and a durable scenario in the map |
| Evaluation | The scenarios run at the boundary, and the suite fails when the unit is absent |
| Context Boundary | The contract is machine-checked by a test, and each dataset has one owner |
| Provenance | Each decision of the unit has a record with rejected alternatives |

Name each gap.

Verdict:

- **replaceable**: covered by durable checks, no undeclared consumer.
- **risky**: covered, but an undeclared consumer could break in silence.
- **unverifiable**: no durable check covers it. A regenerated replacement
  cannot be proven equivalent.

### 6. The empirical pass (optional, recommended before "done")

Work in a copy. Copy the survivors from step 2 into an
empty folder. Run `check config` there. If it fails, copy the missing
file that it names, and run it again. Run the test command there: it must fail, because the code
is absent. If it passes, the suite does not use the folder; stop and fix.
Then run `/phoenix-kit:generate` in that folder, in a new session, and run
the Evaluation. Each failure is knowledge that was in the old code and
not in the primitives. Add it to the list of step 3.

To prove the unit's scenarios can fail, break one rule at a time in a
second copy: change a limit, reorder two checks, widen the scope of a
count, change a message. Run the suite after each one. A broken copy
that passes every test is an Evaluation gap: add it to step 3.

### 7. Report

Use [assets/report-template.md](assets/report-template.md). Write the
report file as [CONTRACTS.md](../../CONTRACTS.md), "Reports", says, and
give the verdict and the lost list in the conversation. The report is scaffolding: the primitives it points to
are the deliverable.

## Guardrails

- Work on a copy. The working tree keeps every file where it is.
- A grade of strong needs the evidence in the table of step 5, not only
  a document that exists.
- The "lost" list stays complete. A long list is the finding.
