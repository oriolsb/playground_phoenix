---
name: decide
description: Records one decision as a decision record (ADR) — the Provenance primitive — with its context, the rejected alternatives, the consequences, and the fitness functions that protect it. Use at the moment a design choice is made, when a rule is revised, when a legacy behavior gets a reason, or when the user says "record a decision", "write an ADR", or "phoenix decide".
argument-hint: "[the decision in one sentence, or the question to decide]"
license: MIT
metadata:
  author: phoenix-kit
  version: "0.1.0"
---

# Decide

Record why the system has its current form. A new team must understand the
reasons with no access to the first team. Record at the moment of the
decision: a record written later is a reconstruction.

## Paths

Read `PHOENIX.md` at the project root for the decisions folder. Default:
`spec/decisions/`, with `adr-index.md` as the index. Create both if they
are missing. `check` means `python3
<kit>/scripts/phoenix_check.py`, from the project root; `<kit>`
is two folders above this file. Run the Requires first and the Ensures
last ([CONTRACTS.md](../../CONTRACTS.md), "Run the checks").

## Steps

```
- [ ] 1. Number and scope — done: `check config` passes; an unused number; the scope read
- [ ] 2. Write the record — done: every section of the template is filled
- [ ] 3. Alternatives     — done: at least one real alternative, with its reason
- [ ] 4. Links            — done: replaced records and revised rules point to this one
- [ ] 5. Index, report    — done: `check decisions` passes (in a change: `--change <name>`)
```

### 1. Number and scope

List the decisions folder. The next number is the highest `NNNN` plus
one, zero-padded to four digits. The file name is
`NNNN-<short-slug>.md`. Read the rules that `$ARGUMENTS` touches, the
open deltas in `spec/changes/`, and the earlier decisions those rules
cite.

Sequential numbers are a deliberate exception: a timestamp and a slug
are safer, because two branches can take the same number. For a small
team, and in a repository with NNNN records already, the readable number
wins. A team that works on parallel branches switches to
`YYYYMMDD-HHMM-<slug>.md` and says so in `PHOENIX.md`. The checker reads
both forms.

### 2. Write the record

Use [assets/decision-record.md](assets/decision-record.md). Fill every
section. Keep it short: a page is enough.

- **Need**: who has the need, and whether it is a business need or an
  operational need. "Not applicable" is a valid answer when no need
  drives the decision.
- **Traces to**: the rule IDs this decision covers.
- **Change**: the change in `spec/changes/` this decision belongs to, by
  name. `/phoenix-kit:change archive` looks for it. "None" otherwise.
- **Evidence**: legacy code only. The file and the behavior you saw.
- **Context**: the problem, and the constraints that forced the choice.
- **Decision**: what you decided, in the present tense.

### 3. Rejected alternatives

Name at least one alternative, and why you rejected it. A decision with no
alternative is a finding: either it was not a decision, or the alternatives
were never looked at. Say which.

A real alternative is one that a competent team could choose. When the
alternatives are weak, or the decision sets a boundary or sits in a slow
pace layer, design it twice first:
[references/design-it-twice.md](references/design-it-twice.md).

### 4. Links

- If this decision replaces an earlier one, set the earlier record's
  status to `replaced by NNNN`, and keep its file.
- If a rule changes because of this decision, add the "Revised" note to
  the rule, naming this record. While a change is open, the rule and its
  note are in the change's `delta.md`: edit them there.
- Each fitness function names the need it protects and how to run it.
  Leave the table empty if none exists yet, and say so in the report.

### 5. Index

If `adr-index.md` is missing, or is one plain table, regenerate it from
the folder: one line per record, in order, with number, title, status,
rules, and change, read from each file's header. Link each record once,
with a markdown link to its file name, for example to `0007-title.md`.

If it has a structure of its own (sections, groups, notes), keep that
structure. Add the new record's line where it belongs, and update the
status of a record it replaces. Every other line stays where it is.

Then run `check decisions`: the header fields, the alternatives, and the
index against the folder (each record linked once, each link resolves).
In a change, `check decisions --change <name>` also finds the record
that names the change. If it gives an error, fix the record or the index
line that it names, and run it again, three passes at most
([CONTRACTS.md](../../CONTRACTS.md), rule 2). If it still fails, stop,
and report each error with its file and line.

## Report

- The record path and its number.
- The rules revised, and the earlier decisions replaced.
- Fitness functions still to write, if any: `/phoenix-kit:evaluate`.
- Next, in a change: the item after `decide` in the hand-off list
  ([`/phoenix-kit:change`](../change/SKILL.md), step 4): the person's
  review of the final suite and `check approval stamp`.

## Guardrails

- Each record names at least one rejected alternative.
- An accepted record stays as written. A new record replaces it.
- The decision lives in a record. A code comment or a commit message can
  point to it.
