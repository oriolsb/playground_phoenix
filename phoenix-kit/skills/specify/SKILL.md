---
name: specify
description: Writes or extends the Specification primitive — behavioral rules and operational limits as EARS rules, each with an ID, a source, a why, and an observable result. Use when a project starts, when a rule is added or revised, when legacy behavior must be written down, or when the user says "write the spec", "add a rule", or "phoenix specify".
argument-hint: "[what the system must do, or a rule ID to revise]"
license: MIT
metadata:
  author: phoenix-kit
  version: "0.1.0"
---

# Specify

Write rules that a competent implementer can build from, with no access to
the code. The code is the output of this document. It is never its source.

## Paths

Read `PHOENIX.md` at the project root. It names the specification file,
the Terms section, and the decisions folder. With no `PHOENIX.md`,
`check config` fails: stop, say that `PHOENIX.md` is missing, and tell
the user to copy a preset from the kit's `templates/` to the project
root (README, "Set up a project"). `check` means `python3
<kit>/scripts/phoenix_check.py`, from the project root; `<kit>` is two
folders above this file. Run the Requires first and the Ensures last
([CONTRACTS.md](../../CONTRACTS.md), "Run the checks").

## Steps

Copy this list and tick each step:

```
- [ ] 1. Read what exists — done: `check config` passes; rules, Terms, decisions, deltas known
- [ ] 2. Extract          — done: a list of actors, actions, data, and limits
- [ ] 3. Write the rules  — done: each has an ID, a source, a why, and a result
- [ ] 4. Open questions   — done: at most 3, asked in one round, answered
- [ ] 5. Checklist        — done: `check rules --strict` passes; each checklist item passes
- [ ] 6. Record, report   — done: each choice has a record; in a change, the spec is unchanged
```

### 1. Read what exists

Read the specification, its Terms section, and the decisions index. Also
read every open delta, `spec/changes/<name>/delta.md` outside `archive/`:
a delta rule replaces the rule with the same ID, and its IDs are taken.
Reuse the existing prefixes (for example `PLAYER`, `BAG`, `OPS`) and take
the next free number. Reuse existing terms. A new term goes into Terms
with one meaning, and the words to avoid for it.

While a change is open, write into its `delta.md`, not into the
specification: a new rule under ADDED, a revised rule under MODIFIED, a
term under "Other changes". Write only what the change needs, and put
any other finding in the report. The archive merges the delta.

### 2. Extract

From `$ARGUMENTS` and the sources it names (a brief, a user, legacy code),
list the actors, the actions, the data, the constraints, and the limits.
An operational limit (latency, cost, reliability, capacity) is a rule with
the prefix `OPS`. It is a requirement, not an implementation detail.

### 3. Write each rule

Use [assets/rule-template.md](assets/rule-template.md). Keep these
properties:

- One behavior per rule. Split a rule that says "and".
- The EARS order: an optional "While", "When", "Where", or "If ...
  then" clause, then the system name, then "shall". A rule that always
  holds has no clause ("Katacombs shall ..."). Say "shall", not "should"
  or "may". The rule is the first sentence; context goes in "Why".
- The rule names no class, no method, and no data structure.
- "Why" gives the reason. A later reader learns why the rule exists.
- "Observable result" names what a test sees at the boundary: a message,
  an error reason, a value, a state that a later query shows.
- A rule that replaces an earlier position gets a "Revised" note with the
  date, and a decision record.

### 4. Open questions

Where a reasonable default exists, choose it and record it under
"Assumptions" in the specification. Mark `[NEEDS CLARIFICATION: question]`
only when the answer changes the scope, the observable behavior, or the
compatibility with other systems. Keep at most 3 markers. Find each
fact yourself, in the input, the code, and the decisions; ask the user
only for a decision. Ask all the questions in one round, in this form,
then wait for the answers:

```markdown
## Question 1: <topic>

**Context**: <quote of the rule or the input>
**What we need to know**: <the question, worded so that "yes" accepts the recommendation>
**Recommended**: <the option, and why>

| Option | Answer | Implications |
| --- | --- | --- |
| A | <answer> | <what changes> |
| B | <answer> | <what changes> |
| Custom | Your own answer | |
```

Replace each marker with the answer. Record the answer as a decision if
it chose between alternatives.

### 5. Quality checklist

Run `check rules --strict`: it checks the form of each rule block and its
EARS order; with `--strict`, a warning fails it too. Then run
[assets/checklist.md](assets/checklist.md) against the rules you wrote,
for what a script cannot judge. Fix each failing item and run both
again, three passes at most. If one still fails, stop and report it. For
a specification with more than about 30 rules, also run the ambiguity
scan in [references/ambiguity-scan.md](references/ambiguity-scan.md) once.

### 6. Record and report

If you chose between alternatives at any step, run `/phoenix-kit:decide` now,
before the report. Provenance is recorded at the moment of the decision. A
decision recorded later is a reconstruction.

While a change is open, run `git diff --quiet -- <spec>`. If it fails,
move the edits of the specification into the delta, and run it again.

## Report

- The rules you added or revised, by ID, one line each.
- The assumptions you recorded.
- The open questions, if any remain.
- The decisions you recorded, by number.
- Next: a person reviews the rules. Then `/phoenix-kit:contract` for each
  rule that crosses the boundary, and `/phoenix-kit:evaluate` for each
  rule.

## Guardrails

- A rule names behavior only: no class, method, framework, or data
  structure.
- Each rule has an ID, a source, a why, and an observable result.
- A rule that changes meaning gets a "Revised" note and a decision.
- This skill writes the specification only. The code comes from
  `/phoenix-kit:generate`.
