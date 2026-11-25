---
name: contract
description: Defines the Context Boundary primitive — the machine-readable contracts (OpenAPI, JSON Schema), the vocabulary with one meaning per term, and the owner of each dataset. Use after the rules exist and before the evaluation, when a boundary changes, when freezing a legacy boundary, or when the user says "write the API contract", "define the boundary", or "phoenix contract".
argument-hint: "[the boundary to define, or the rule IDs that cross it]"
license: MIT
metadata:
  author: phoenix-kit
  version: "0.1.0"
---

# Contract

State what crosses the boundary, in a form a machine can check, and what
the terms mean inside it. A regeneration keeps the first and loses the
second unless both are written.

## Paths

Read `PHOENIX.md` at the project root for the contract files and the
Terms section. Defaults: `spec/openapi.yaml`, `spec/*.schema.json`, and
the Terms section of `spec/specification.md`. `check` means `python3 <kit>/scripts/phoenix_check.py`, from the project
root; `<kit>` is two folders above this file. Run the Requires first and
the Ensures last ([CONTRACTS.md](../../CONTRACTS.md), "Run the checks").

While a change is open (`spec/changes/<name>/`, outside `archive/`),
write each edit to the specification, a term or the ownership table,
into the "Other changes" section of its `delta.md`, not into the
specification. The archive merges it. Edit the contract files in place:
the contract test and the scenarios read them. Then add one
`### Contract: <file>` entry to "Other changes" for each contract file
you edit: the operations and schemas that changed, with their rule IDs.
Edit only what the change needs. A finding outside the change goes in
the report, not into a file.

## Steps

```
- [ ] 1. Boundary rules — done: `check config` passes; the rule IDs whose result a caller sees
- [ ] 2. API contract   — done: each operation cites its rules in x-rules
- [ ] 3. Data shapes    — done: each accepted shape has a JSON Schema and a test
- [ ] 4. Vocabulary     — done: each term has one meaning; the Avoid search is clean
- [ ] 5. Ownership      — done: each dataset has one writer
- [ ] 6. Checks         — done: `test_command` passes; each by-hand check of step 6 passes
```

### 1. Rules that cross the boundary

A rule crosses the boundary when its observable result is a request, a
response, an identifier, an error reason, or a message that a caller sees.
List those rule IDs. A rule that only changes internal state is not in the
contract. Read the open deltas too, `spec/changes/<name>/delta.md` outside
`archive/`: a delta rule replaces the rule with the same ID.

### 2. The API contract

OpenAPI 3.1, in the contract file. Start from
[assets/openapi-skeleton.yaml](assets/openapi-skeleton.yaml) if the file
does not exist. For each operation:

- `x-rules`: the rule IDs the operation satisfies. One operation cites at
  least one rule. One boundary rule is cited by at least one operation.
- Each response schema lives under `components/schemas`. Write one
  contract test in the tests folder, for example `tests/test_contract.py`:
  it validates a live response of each operation against its schema.
- Each error reason maps to exactly one HTTP status. Put the map in
  `x-status-by-reason` on the error reason schema, and state the reason
  for each status in a decision record.

### 3. Data shapes

For each shape the system accepts from outside (a configuration, a world
file, an import), write a JSON Schema (draft 2020-12). A violation must
fail a test, so drift cannot pass in silence.

### 4. Vocabulary

Read the Terms section: Term, Meaning, and Avoid. Avoid lists the words
that the project does not use for that idea (from Matt Pocock's
`domain-modeling` skill, MIT). If the column is missing, give Avoid
words only to the terms you add or change, and report the missing column.
For each term the contract uses:

- The term is in Terms, with one meaning.
- No second term names the same idea. No term names two ideas.
- The schema property names use the term, not a synonym.

Search the specification, the contracts, and the tests for each word in
the Avoid column. Each hit is a finding: use the term, or report it.
When code exists, compare each term with the code. A code name with a
different meaning, or a type that Terms names and the code lacks, is a
finding too.

Two names for one idea, or one name for two ideas, is the first sign that
the boundary sits in the wrong place. Report it as a finding.

### 5. Data ownership

Write a short table in the specification, or in the open delta: dataset,
the one component that writes it, the components that read it. Shared writes hide coupling. A
dataset with two writers is a finding.

### 6. Checks

Run `test_command` from `PHOENIX.md`. Before the code exists, the
contract test must collect and fail, because no live response exists
yet. After `/phoenix-kit:generate`, it must pass. The checker has no
command for the other checks below. Do them by hand
against the contract files, and say in the report that you did them by
hand, with the file and line of each finding.

- Every boundary rule from step 1 appears in an `x-rules` list.
- Every operation has a success response and its error reasons.
- Every error reason has one status.
- Every term in the contract is in Terms.
- While a change is open, `git diff --quiet -- <spec>` passes: the
  specification is unchanged, and the edits are in the delta. Each file
  in `git diff --name-only -- <contracts>` has its `### Contract:` entry.
- If a check fails, fix the contract or the test, and run it again.
  After three passes, stop and report the finding.
- A contract change that chose between alternatives gets a decision:
  run `/phoenix-kit:decide`. A boundary with more than one plausible
  shape: `decide` can design it twice first.

## Report

- The operations and schemas added or changed, with their rule IDs.
- Terms added, and any synonym or double meaning found.
- The checks of step 6 that you did by hand, and their findings.
- Datasets with two writers, if any.
- Next: in a change, the item after `contract` in the hand-off list
  ([`/phoenix-kit:change`](../change/SKILL.md), step 4). Otherwise
  `/phoenix-kit:evaluate` for the scenarios of the rules.

## Guardrails

- Derive the contract from the rules. For legacy code, record what the
  code does, and mark each item with its evidence.
- The contract names only what a caller sees: no internal class, table,
  or module.
- Each error reason has exactly one status, and each status a reason.
- While a change is open, the specification stays as it is: edit the
  delta. The contract files change in place, and the delta names them.

## See also

The Bounded Context Canvas (DDD Crew, CC BY-SA) is a ready template for
the vocabulary and the ownership table:
<https://github.com/ddd-crew/bounded-context-canvas>.
