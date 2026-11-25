# PHOENIX.md — where the primitives live

Every Phoenix skill reads this file first. Edit the paths to match the
project. This file is itself part of the Specification: it survives the
Deletion Test, and a regeneration starts from it.

This preset is the larger layout: the architecture and the operations
detail have their own folders under `spec/`. The handout layout of the
exercises is in `PHOENIX.workshop.md`.

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
primitives: PHOENIX.md, spec, tests, docs/katacombs.md
sources: docs/katacombs.md
rule_id: [A-Z]+-\d+
reports: .phoenix/reports
```

## The four primitives

| Primitive | Artifact | Path | How to check it |
| --- | --- | --- | --- |
| Specification | Behavioral rules, EARS form, one ID per rule | `spec/specification.md` | Each rule has an ID, a source, a why, and an observable result |
| Specification | The brief: the root source, with the world data | `../../docs/katacombs.md`; in a deletion copy, `docs/katacombs.md` | Copy it into the deletion folder: the rules point to it |
| Specification | Operational limits (latency, cost, reliability) | `spec/specification.md`, prefix `OPS`; targets in `spec/operations/` | One measured test per limit |
| Specification | Terms, one meaning each | `spec/specification.md`, section Terms, with an Avoid column | No synonym, no term with two meanings, no avoided word in the spec, the contracts, or the tests |
| Specification | Detail: the brief summary, the domain model, the architecture design | `spec/architecture/` | It agrees with the rules; a rule wins over the detail |
| Specification | Open changes: a delta rule replaces the rule with its ID | `spec/changes/<name>/delta.md` | Each open change has a proposal and a delta |
| Context Boundary | API contract | `spec/openapi.yaml` | The contract test validates each response |
| Context Boundary | Data shapes the system accepts | `spec/*.schema.json` | Schema validation in a test |
| Context Boundary | Module boundaries | `spec/architecture/component-boundaries.md` | An import checker in the fitness tests |
| Evaluation | Acceptance scenarios and fitness functions | `tests/` | The command below |
| Evaluation | Rule-to-scenario map, the rules with a partial check, the approval line | `spec/evaluation/test-scenarios.md` | Every rule ID appears once; `Approved:` is filled by a person |
| Provenance | Decision records, `NNNN-<slug>.md` | `spec/decisions/` | Each record names the rejected alternatives and its change |
| Provenance | Archived changes | `spec/changes/archive/` | Each archived change has a decision record |

Scaffolding (not a primitive, delete when done): assessments of legacy
units go in `.phoenix/assessment/`.

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

The code is the output of the primitives. A regeneration deletes it and
rebuilds it from the table above.

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

Fill this in before the first change, on day 3 in the workshop. See the
pace layers in the workshop cheat sheet.

| Part | Layer (fast, medium, slow) | Kind (core, supporting, generic) |
| --- | --- | --- |
| | | |

## Phases

One table per phase of a larger change. The table shows each primitive
in the phase, the artifact that holds it, and how to check it.

### Phase 1

| Primitive | Artifact | How to check it |
| --- | --- | --- |
| Specification | `spec/specification.md`, rules ID-1 to ID-3 | Review the need and its constraints |
| Evaluation | `tests/fitness/` | Run `uv run pytest` |
| Context Boundary | The vocabulary and the published ports | Read the vocabulary and run the import checker |
| Provenance | `spec/decisions/NNNN-phase-1.md` | Read the named need and the alternatives |
