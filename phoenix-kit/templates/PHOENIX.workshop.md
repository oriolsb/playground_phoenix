# PHOENIX.md — where the primitives live

The handout layout of the workshop exercises (Run 2 and the deletion
copy): `spec/`, `tests/`, `decisions/`, and the code in `katacombs/`.
Copy this file to the workspace root as `PHOENIX.md`. Every Phoenix
skill reads it first. It is part of the Specification: copy it into the
deletion folder with `spec/`, `tests/`, `decisions/`, `pyproject.toml`,
`uv.lock`, `requirement.md`, and `katacombs.md` (Run 2, step 6).

The handout does not give a file name in `spec/` or an index in
`decisions/`. This file names them, and the kit's skills create them:

- `spec/specification.md`: your rules and Terms (`/phoenix-kit:specify`).
  If your rules are in a different file, change the `spec` line.
- `spec/test-scenarios.md`: the rule-to-scenario map and the approval
  line (`/phoenix-kit:evaluate`).
- `decisions/adr-index.md`: one line for each decision record
  (`/phoenix-kit:decide`).
- `spec/openapi.yaml`: the API contract of Run 2, step 2
  (`/phoenix-kit:contract`).

Until a skill creates a file, `check status` gives a warning for it, not
an error.

On day 3, the code is under `brown_field/`. Put that folder in front of
each path in the block, for example `spec: brown_field/spec/specification.md`
and `code: brown_field`. `PHOENIX.md` stays at the workspace
root, so do not change the `PHOENIX.md` entry or the `.phoenix/` paths.

```phoenix
# On day 3, put brown_field/ in front of each path,
# except PHOENIX.md and the .phoenix/ paths.
system: Katacombs
spec: spec/specification.md
changes: spec/changes
decisions: decisions
decision_index: decisions/adr-index.md
map: spec/test-scenarios.md
contracts: spec/openapi.yaml
tests: tests
code: katacombs
unit_tests: implementation_tests
test_command: uv run pytest
junit_command: uv run pytest -q --junitxml=.phoenix/junit.xml
junit: .phoenix/junit.xml
primitives: PHOENIX.md, spec, tests, decisions, katacombs.md, requirement.md
sources: katacombs.md, requirement.md
rule_id: [A-Z]+-\d+
reports: .phoenix/reports
```

## The four primitives

| Primitive | Artifact | Path | How to check it |
| --- | --- | --- | --- |
| Specification | Behavioral rules, EARS form, one ID per rule | `spec/specification.md` | Each rule has an ID, a source, a why, and an observable result |
| Specification | The brief and the shared requirement | `katacombs.md`, `requirement.md` | The rules cite them as sources |
| Specification | Operational limits | `spec/specification.md`, prefix `OPS` | One measured test per limit |
| Specification | Terms, one meaning each | `spec/specification.md`, section Terms, with an Avoid column | No synonym, no term with two meanings, no avoided word in the spec, the contracts, or the tests |
| Specification | Open changes (day 3) | `spec/changes/<name>/delta.md` | Each open change has a proposal and a delta |
| Context Boundary | API contract | `spec/openapi.yaml` | The contract test validates each response |
| Context Boundary | The entry point and the ports | `spec/specification.md`, section Context Boundary | The Evaluation imports only the entry point |
| Evaluation | Acceptance scenarios and fitness functions | `tests/` | The command below |
| Evaluation | Rule-to-scenario map and the approval line | `spec/test-scenarios.md` | Every rule ID appears once; `Approved:` is filled by a person, last |
| Provenance | Decision records, `NNNN-<slug>.md` | `decisions/` | Each record names the rejected alternatives |
| Provenance | Archived changes (day 3) | `spec/changes/archive/` | Each archived change has a decision record |

Scaffolding (not a primitive): `conversations/` holds one file per LLM
session, and `.phoenix/assessment/` holds a legacy assessment. Neither goes
into the deletion folder.

## Commands

| Purpose | Command |
| --- | --- |
| Run the whole Evaluation | `uv run pytest` |
| Run the fitness functions only | `uv run pytest -m fitness` |

The fitness command selects the tests with the `fitness` marker. Mark
each fitness test `@pytest.mark.fitness`, or tag its scenario `@fitness`.
Register the marker once in `pyproject.toml`, under
`[tool.pytest.ini_options]`: `markers = ["fitness: a fitness function"]`.

## The code

| What | Path |
| --- | --- |
| Production code | `katacombs/` |
| Entry point that the Evaluation imports | `katacombs/app.py`, `build(world=None)` |
| Unit tests that the generator writes with the code | `implementation_tests/` |

## Units

The regeneration units, one row for each. `generate <unit>`, the removal
step of `change`, and `deletion-test` read the same row. Add a row when
the unit first changes.

| Unit | Rules | Interface | Modules | Risk |
| --- | --- | --- | --- | --- |

## Pace layers

Fill this in before Phase 1 on day 3.

| Part | Layer (fast, medium, slow) | Kind (core, supporting, generic) |
| --- | --- | --- |
| | | |

## State

On day 3, one line at 11:30, 12:30, and 14:30: what is done, and what is
next.

- 11:30:
- 12:30:
- 14:30:
