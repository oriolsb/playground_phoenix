---
name: change
description: Changes a system behind a stable boundary — proposes a change as a need plus a delta of rules (ADDED, MODIFIED, REMOVED, RENAMED), hands off to the contract, evaluation, and decision skills before any code, then archives the change by merging the delta into the living specification. Use when a new need arrives on a system whose primitives exist, or when the user says "propose a change", "archive the change", or "phoenix change".
argument-hint: 'propose <name> "<the need>" | archive <name>'
license: MIT
metadata:
  author: phoenix-kit
  version: "0.1.0"
---

# Change

A change starts from a need, becomes a delta of rules, and ends merged
into the specification with a decision record; the code is regenerated
last. The layout and the delta format come from OpenSpec (MIT).

## Paths and checks

Read `PHOENIX.md` at the project root. Changes live in `spec/changes/`
by default: `spec/changes/<name>/` while in flight,
`spec/changes/archive/YYYY-MM-DD-<name>/` when done. `check` means
`python3 <kit>/scripts/phoenix_check.py`; `<kit>` is two folders above
this file. Requires first, Ensures last ([CONTRACTS.md](../../CONTRACTS.md)).
`$ARGUMENTS` starts with `propose` or `archive`. With neither, ask which.

## Propose

This mode writes only `proposal.md` and `delta.md`, then stops.

```
- [ ] 1. Name the need     — done: `check config` passes; a rule with a target and a source
- [ ] 2. Write proposal.md — done: each part has a pace layer and a blast radius
- [ ] 3. Write delta.md    — done: `check delta --change <name>` passes, in three passes at most
- [ ] 4. Hand off          — done: the user has the order of step 4
```

### 1. The need

Who has the need? Why? Is it a business need or an operational need?
Make it measurable: a rule with a target and a source. No need, no
change. If the need is unclear, ask in one round, as `/phoenix-kit:specify`
step 4 does: at most 3 questions, each with a recommended answer.

### 2. proposal.md

Create `spec/changes/<name>/proposal.md` from
[assets/proposal.md](assets/proposal.md). State the pace layer and the
blast radius of each part the change touches. A change in a slow layer
needs a person's review: say so.

### 3. delta.md

Create `spec/changes/<name>/delta.md` from
[assets/delta.md](assets/delta.md). Use the rule format of the
specification. Eight sections, each optional:

- **ADDED**: new rules, with new IDs in the existing prefixes.
- **MODIFIED**: copy the whole existing rule, then edit it. A partial
  copy loses detail at archive time.
- **REMOVED**: the rule ID, a reason, and a migration.
- **RENAMED**: `FROM: OLD-ID` / `TO: NEW-ID`, for a name change only.
- **Other changes**: Terms rows and sections that are not rules, in full.
- **Old values**: each literal the change replaces, for the archive.
- **Kept old values**: at archive, each old-value hit that stays, and why.
- **Unchanged**: the rule IDs next to the change that keep their behaviour.

No rule change: no delta. Write `No rule changes.` in proposal.md; decide.

A delta that changes what an outside caller sees (a route, a response,
an error reason) breaks each caller at the merge. Split it in three:
[references/expand-contract.md](references/expand-contract.md).

### 4. Hand off

This list is the one copy of the hand-off. While the change is open,
each skill reads `delta.md` as part of the Specification, and writes its
specification edits into it. `contract` edits the contract files in
place, and names each edit in the delta. `check status` names the next item:

1. A person reviews `proposal.md` and `delta.md`.
2. `/phoenix-kit:contract` if a rule crosses the boundary: the scenarios
   use its shapes.
3. `/phoenix-kit:evaluate` for the delta rules: the scenarios and the
   fitness functions, before any code.
4. `/phoenix-kit:decide` with the need in its Need field, this change in
   its Change field, and the fitness functions in its table.
5. A person reviews the final suite, runs `check approval stamp --by
   "<who>"`, and commits the primitives.
6. On a branch, a person removes the unit's behavior by hand and keeps
   each name that other code imports: a check that other flows pass
   through becomes a no-op; a constant becomes `None`. Run `check
   expected record --run`, and end the commit message with the trailers
   it prints. Each listed test must reach the unit; if one does not,
   narrow the removal. Then `/phoenix-kit:generate <unit>`, new session.
7. Archive the change. The archive edits the map, so the approval stops
   matching: a person reviews the map diff, runs `check approval stamp
   --by "<who>"`, and commits. Then `/phoenix-kit:deletion-test <unit>`.

## Archive

```
- [ ] 1. Check      — done: the suite passes; the checks of step 1 pass; first oldvalues kept
- [ ] 2. Merge      — done: `check rules` passes; only the named rules changed
- [ ] 3. Old values — done: both outputs are in the report; each hit that stays has a reason
- [ ] 4. The map    — done: `check trace` passes; the report asks a person to stamp again
- [ ] 5. Move it    — done: it is in archive/YYYY-MM-DD-<name>/, with one date only
```

### 1. Checks

Run the test command: it must pass. Run `check delta --change <name>
--archive` (no placeholder left) and `check decisions --change <name>`
(a record names the change). If one fails, stop and say what is missing.
Archive with a warning only when the user confirms.
Then run `check oldvalues --change <name> --json`; keep the output.

### 2. Merge

Apply the delta to the specification, in place, with the rules in
[references/merge-rules.md](references/merge-rules.md): ADDED, MODIFIED
(one "Revised" line), REMOVED, RENAMED, and Other changes. Every rule the
delta does not name stays exactly as it is.

### 3. Old values

Run `check oldvalues --change <name> --archive --json`: a hit is an
error, except in a decision record. `data.hits` gives the file, line,
and scope. Fix each hit that states the replaced value, or give its
reason in the delta's "Kept old values" table ([merge rules](references/merge-rules.md)).
Run it again, three passes at most. Put the step 1 and the last output
in the report.

### 4. The map

Update the rule-to-scenario map: new rules appear, removed rules leave,
renamed rules follow their new ID.

## Report

Propose: the need, the delta by rule ID, and the hand-off order, starting
with the human review. Archive: the rules merged by section, the decision
number, the two old-value searches, the archive path, and any warning,
in a report file ([CONTRACTS.md](../../CONTRACTS.md), "Reports"). Next:
a person stamps the approval again; then `/phoenix-kit:deletion-test <unit>`.

## Guardrails

- Merge only a delta whose Evaluation passes, and only the rules it names.
- The approval stamp and the expected-failure record are a person's
  steps. The agent prints the commands and waits.
