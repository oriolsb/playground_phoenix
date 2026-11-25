# Phoenix Kit — the contracts between the skills

Each skill reads some artifacts and writes others. This table is the one
copy of what each skill needs before it starts (**Requires**) and what
must hold when it ends (**Ensures**). The forms of the artifacts are in
[schemas/README.md](schemas/README.md).

`check` means the kit's checker, run from the project root:

```sh
python3 <kit>/scripts/phoenix_check.py <command>
```

`<kit>` is the folder of this plugin: the folder that holds `skills/`.
From a skill, it is two folders above the `SKILL.md`. Python 3.11 or
later; no package to install. A check passes when it reports no error.
Add `--json` for a result that another tool reads.

## Run the checks

Each skill follows these three rules for the checks in its row below.

1. **Requires first.** Before the first step, run each Requires check. If
   one fails, stop. Report the finding and the fix that it names. Do not
   start the work.
2. **Ensures last.** Before the report, run each Ensures check. If one
   fails, fix the artifact that the finding names, and run the check
   again, three passes at most. If it still fails, stop. Report the
   finding with its file and line. Do not report the work as done.
3. **No Python.** Say so in the report, and check by hand against the
   grammars. See "Without the checker" below. Do not skip the check.

## The skills

| Skill | Reads | Writes | Requires | Ensures | Next |
| --- | --- | --- | --- | --- | --- |
| `specify` | `PHOENIX.md`, the specification, the open deltas, the decision index | Rules in the specification, or in the open delta | `check config` | `check rules --strict` (an EARS warning fails it). While a change is open, `git diff --quiet -- <spec>` | `contract`, `evaluate` |
| `contract` | The rules, the open deltas, the contracts, Terms | The contracts, in place; the contract test; Terms rows and the ownership table, in the open delta while a change is open; one `### Contract: <file>` entry in the open delta for each contract file it edits | `check config` | The contract test collects and fails when `test_command` runs before the code exists, and passes after `generate`. The other checks of step 6 are done by hand, and the report says so. While a change is open, `git diff --quiet -- <spec>`, and each file in `git diff --name-only -- <contracts>` has its entry in the delta | `evaluate` |
| `evaluate` | The rules, the open deltas, the contracts, the suite, the map | Scenarios and fitness functions in `tests`; the map | `check rules` | `check trace`. Normal mode: the new scenarios fail before the code. Characterization mode (from `assess`): the new scenarios pass against the existing code. `check approval clear` ran | `decide`; then a person runs `check approval stamp` |
| `decide` | The rules, the open deltas, the decisions | One record; one index line; the `Revised` notes | `check config` | `check decisions` (in a change: `check decisions --change <name>`) | In a change: a person runs `check approval stamp` |
| `change propose` | `PHOENIX.md`, the specification, the map, the decisions | `proposal.md`, `delta.md` | `check config` | `check delta --change <name>` | A person reviews; `contract`, then `evaluate` |
| `change archive` | The delta, the specification, the map, the decisions | The specification and its detail; the map; the "Kept old values" table of the delta; the archived change | `check delta --change <name> --archive`; `check decisions --change <name>`; the suite passes | `check oldvalues --change <name> --json` before the merge and `check oldvalues --change <name> --archive --json` after it, both outputs in the report file (in archive mode a hit is an error, except in a decision record or with a row in "Kept old values"); `check rules`; `check trace` | A person stamps the approval again (the map changed); then `deletion-test <unit>` |
| `generate` | All primitives; the unit row (`check units show <unit> --json`) | The code; its unit tests; a report | `check approval verify`; `git status --porcelain -- <primitives>` is empty; `check expected check --run`. Whole system (no trailers on the commit, or outside git): it passes when the suite does not collect, or every test fails. One unit: it compares the failures with the trailers | The suite passes; `check trace`; `git status --porcelain -- <primitives>` is empty; the report file | `change archive`, or `deletion-test` |
| `deletion-test` | The repository inventory, the primitives, the code | A report | `check config` | The report file, with a verdict and its evidence | The skills of its work plan |
| `assess` | The unit's code and its callers | An assessment in `.phoenix/assessment/`; a proposed `PHOENIX.md` block and Units row | none | Before the person saves it, the proposed block passes `check config --root .phoenix/proposal` | `contract` |
| `timeline` | `PHOENIX.md` when it exists, the specification, the decisions, the tests, the sources, the git history | `docs/legacy-decision-timeline.md` | none: a legacy project can have no `PHOENIX.md` | The four sections, one source pointer for each event, and the change, the placement, and the why kept apart | `assess`, `specify`, `decide` |
| `explain` | The tests, the Terms table, the contracts, the decisions | `docs/behavior-overview.md` | none | Each material claim points to a test, a specification, or a contract; the gaps, the conflicts, and the documentation-only claims are visible | `vocabulary` |
| `vocabulary` | The tests, the Terms table, the contracts, the behavior overview when it exists | `docs/vocabulary-review.md` | none | Each finding names two meanings with evidence; the defined and the proposed terms are separate; the public names are unchanged | `contract` (the Terms table), `specify` |

## The steps that only a person takes

| Step | Command | Where |
| --- | --- | --- |
| Approve the suite, after the review | `check approval stamp --by "<who>"` | `change` hand-off, item 5 |
| Approve the suite again, after the archive changed the map | `check approval stamp --by "<who>"` | `change` hand-off, item 7 |
| Record the failures of a removal | `check expected record`, then paste its trailers at the end of the removal commit message | `change` hand-off, item 6 |

An agent runs neither command. An approval that an agent writes is not
a review.

## Reports

Three skills write a report file: `generate`, `deletion-test`, and
`change archive`. Their Ensures name it. The other skills give the
report in the conversation only. A report file goes to
`<reports>/<skill>-<YYYYMMDD-HHMM>.md` (default `.phoenix/reports/`), with
the front matter of [schemas/README.md](schemas/README.md), section 7,
and gives a short summary in the conversation. Each claim points to an
evidence entry, a file and line, or a checker result. The folder is
git-ignored scaffolding: add `.phoenix/` to `.gitignore`.

A reader document (`timeline`, `explain`, `vocabulary`) is not a report.
It is a durable file in `docs/`, beside the other project documents, and
a person keeps it. It is not git-ignored, and no skill reads it except
`vocabulary`, which reads the overview when one exists.

## Without the checker

The forms are plain markdown, so a person can check each one by hand
with the grammar in [schemas/README.md](schemas/README.md). A skill that
cannot run Python says so in its report and checks by hand; it does not
skip the check.
