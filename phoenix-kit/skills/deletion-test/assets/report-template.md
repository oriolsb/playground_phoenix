---
skill: deletion-test
verdict: replaceable | risky | unverifiable
evidence:
  - command: <each command you ran, for example the suite in the empty folder>
    exit: <its exit code>
    summary: <its last line>
---

# Deletion Test — <unit>

Date: <YYYY-MM-DD>. Inventory: `git ls-files`, <N> files.

## Verdict: <replaceable | risky | unverifiable>

<One sentence: the main reason.>

## What survives

| File | Primitive |
| --- | --- |
| `spec/specification.md` | Specification |
| `spec/openapi.yaml` | Context Boundary |
| `tests/` | Evaluation |
| `spec/decisions/` | Provenance |

## What is lost

| File:line | What the code knows | Primitive that should hold it |
| --- | --- | --- |
| | | |

## The four properties

| Property | Finding |
| --- | --- |
| Boundary clarity | <undeclared consumers, or none> |
| Evaluation coverage | <scenarios that cover the unit, or none> |
| Coupling depth | <hops, and the furthest consumer> |
| Replaceability | <verdict and reason> |

## Grades

| Primitive | Grade | Gap |
| --- | --- | --- |
| Specification | | |
| Evaluation | | |
| Context Boundary | | |
| Provenance | | |

## Empirical pass

<Not run, or: folder, test command, result, and each failure with the
knowledge it revealed.>

## Work plan

The "What is lost" rows, in the sequence of risk: Context Boundary first,
then Evaluation, then Specification, with Provenance throughout.
