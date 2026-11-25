# Phoenix Kit — the artifact grammars

Each artifact that one skill writes and another skill reads has a fixed
form. This file defines each form once. `scripts/phoenix_check.py`
checks each form, so a skill reads the checker's result, not its own
memory of the file.

The forms are plain markdown. A person reads and edits each file as
before. The checker adds a test, not a new format.

Levels: an **error** fails the check. A **warning** is guidance. With
`--strict`, a warning fails the check too.

## 1. The machine block of `PHOENIX.md`

One fenced block with the info string `phoenix`, one `key: value` per
line. A list is comma-separated. Paths are relative to the project root.
A line that starts with `#` is a comment. A key that is not in the table
below is an error, so a typo does not fall back to the default.

````markdown
```phoenix
system: Katacombs
spec: spec/specification.md
spec_detail: spec/architecture, spec/operations
changes: spec/changes
decisions: spec/decisions
decision_index: spec/decisions/adr-index.md
map: spec/evaluation/test-scenarios.md
contracts: spec/openapi.yaml, spec/world.schema.json
tests: tests
code: katacombs
unit_tests: implementation_tests
test_command: uv run pytest
junit_command: uv run pytest -q --junitxml=.phoenix/junit.xml
junit: .phoenix/junit.xml
primitives: PHOENIX.md, spec, tests
sources: docs/katacombs.md
rule_id: [A-Z]+-\d+
reports: .phoenix/reports
```
````

| Key | Meaning | Default |
| --- | --- | --- |
| `system` | The system name that a rule uses before "shall" | `the system` |
| `spec` | The specification file | `spec/specification.md` |
| `spec_detail` | Folders of specification detail | none |
| `changes` | The folder of changes; `archive/` inside it | `spec/changes` |
| `decisions`, `decision_index` | The decision records and their index | `spec/decisions`, `<decisions>/adr-index.md` |
| `map` | The rule-to-scenario map | `spec/evaluation/test-scenarios.md` |
| `contracts` | Machine-readable contracts | none |
| `tests` | The Evaluation suite; the approval hash covers it | `tests` |
| `code`, `unit_tests` | The code and its unit tests; never primitives | `src`, none |
| `test_command` | Runs the whole Evaluation | `uv run pytest` |
| `junit_command`, `junit` | Runs the Evaluation and writes JUnit XML to `junit` | none |
| `primitives` | Paths that `generate` leaves unchanged | `PHOENIX.md, spec, tests` |
| `sources` | Inputs that the rules cite and a deletion copy needs | none |
| `rule_id` | The pattern of a rule ID | `[A-Z]+-\d+` |
| `reports` | Where skills write their reports; git-ignored | `.phoenix/reports` |

JUnit XML is the result format, not the test framework. pytest writes it
with `--junitxml`; most other runners write it too, some with a plug-in.

A path that does not exist yet is a warning: the skill that owns that
artifact creates it. A missing `PHOENIX.md`, or a value that does not
parse, is an error. With `--strict`, a missing path fails the check too,
so CI runs it after the primitives exist.

## 2. A rule block

In the specification, and in the ADDED and MODIFIED sections of a delta:

```markdown
#### BAG-1 — The bag holds at most 12 items

- Source: brief ("max 10 in bag"), revised by change bag-limit-12.
- Rule: When a player with 12 items in the bag takes an item, Katacombs
  shall refuse the action and keep the bag unchanged.
- Why: the limit forces a player to choose.
- Observable result: the error reason `BAG_FULL`. The item stays in the
  location.
- Revised: 2026-10-19. The limit rises from 10 to 12 (decision 0036).
```

- The heading is level 3 or 4: `<ID> — <title>`. The ID matches
  `rule_id` and appears once in the specification.
- Required bullets: `Source`, `Rule` (or `Rule (EARS)`), `Why`,
  `Observable result`. Other bullets are allowed. A bullet continues on
  lines indented by two spaces.
- **EARS form** (warning): the first sentence of `Rule` holds "shall",
  in one of these orders:

  | Pattern | Before "shall" |
  | --- | --- |
  | Ubiquitous | `<system>` alone: a short name, no comma |
  | State driven | `While <state>, <system>` |
  | Event driven | `When <trigger>, <system>` |
  | Optional feature | `Where <feature>, <system>` |
  | Unwanted behaviour | `If <condition>, then <system>` |
  | Complex | Two or more of `While`, `When`, `Where`, then `<system>` |

- More than two "shall" in one rule is a warning: one behaviour per rule.

## 3. A delta: `spec/changes/<name>/delta.md`

| Section heading | Holds | Check |
| --- | --- | --- |
| `## ADDED Rules` | Rule blocks | The ID is new |
| `## MODIFIED Rules` | Whole rule blocks | The ID exists; the block keeps every bullet label of the current rule; a `Revised` bullet |
| `## REMOVED Rules` | `#### <ID> — <title>` with `Reason` and `Migration` bullets | The ID exists |
| `## RENAMED Rules` | `- FROM: \`<ID>\`` and `- TO: \`<ID>\`` | FROM exists; TO is new |
| `## Other changes to the specification` | `### <heading>` and the full new text. A contract file is edited in place: its entry is `### Contract: <file>` and the operations and schemas that changed | none |
| `## Old values` | A table: `Rule ID`, `Old value`, `New value` | Each row has one old literal, in backticks; a cell with more than one is a warning |
| `## Kept old values` | Optional, at archive: a table: `File`, `Old value`, `Reason`, one row for each hit that stays | `oldvalues --archive` accepts a hit in that file with that value |
| `## Unchanged` | Optional: the rule IDs that must keep their behaviour | Each ID exists |

With `--archive`, no placeholder may remain: `NNNN`, `YYYY-MM-DD`, or
`<...>`.

## 4. A decision record: `<decisions>/NNNN-<slug>.md`

```markdown
# 0036 — The bag holds at most 12 items

- **Status:** accepted
- **Date:** 2026-10-19
- **Need:** business. The product owner, for the players.
- **Traces to:** `BAG-1`, `HELP-1`; decisions `0008`.
- **Change:** `bag-limit-12`.

## Context
## Decision
## Alternatives rejected
## Consequences
## Fitness functions
```

- `Status`: `proposed`, `accepted`, `replaced by NNNN`, or
  `written after the code`. `Date`: `YYYY-MM-DD`. Both are required.
- `## Alternatives rejected` holds at least one table row.
- `Change` names a change, or `None`. `change archive` needs one record
  that names the change.
- The index links each record file once, and each link resolves.

## 5. The map: the approval line

The map holds one line:

```text
Approved: <who>, <YYYY-MM-DD>, suite sha256:<16 hex digits>
```

The hash covers every file under `tests` and the map itself, without
this line. A person writes the line with
`phoenix_check.py approval stamp --by "<who>"`, after the review.
`evaluate` clears it with `phoenix_check.py approval clear`. Any change
to the suite after the stamp makes `approval verify` fail. The archive
of a change edits the map, so a person stamps again after the archive.

## 6. Expected failures: git trailers

The commit that removes a unit ends with one trailer per failing test:

```text
Phoenix-Expected-Fail: <classname>::<name>
```

The test ID is the JUnit `classname` and `name`, joined by `::`.
`phoenix_check.py expected record` prints the trailers;
`phoenix_check.py expected check` compares them with a new run. With no
trailers on the commit, or outside git, `expected check` is the gate for
the whole system: it passes only when the suite does not collect or every
test fails.

Other trailers: `Phoenix-Change: <name>` on the commits of a change, and
`Phoenix-Rules: <ID>, <ID>` where useful. `git log` reads them back.

## 7. A report: `<reports>/<skill>-<YYYYMMDD-HHMM>.md`

```markdown
---
skill: generate
verdict: passed | stopped | specification-failure | replaceable | risky | unverifiable
evidence:
  - command: uv run pytest -q
    exit: 0
    summary: 262 passed
---
```

The body follows the skill's report template. Each claim in the body
points to an evidence entry, a file and line, or a checker result. A
claim with no evidence is marked "not verified". The reports folder is
git-ignored scaffolding.

## 8. Units: the `## Units` table of `PHOENIX.md`

| Unit | Rules | Interface | Modules | Risk |
| --- | --- | --- | --- | --- |
| bag-limit | BAG-1 | `Bag.LIMIT` | `katacombs/domain/bag.py` | medium |

- Each rule ID exists. Each module path exists. Risk is `low`, `medium`,
  `high`, or `critical`.
- `generate <unit>`, the removal step of `change`, and `deletion-test`
  read the same row.
