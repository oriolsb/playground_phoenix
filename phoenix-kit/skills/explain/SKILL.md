---
name: explain
description: Writes one reader-friendly behavior overview of a system or feature from its tests and its vocabulary, so a newcomer learns what the system does without reading the code. Marks every evidence gap, conflict, and documentation-only claim. Use when the user asks what a system does, when a new maintainer joins, or when the user says "explain the behavior", "write an overview", or "phoenix explain".
argument-hint: "[the feature or unit to explain]"
license: MIT
metadata:
  author: phoenix-kit
  version: "0.1.0"
---

# Explain

A test says what must hold. It does not say what the system does, in words
that a newcomer can follow. This skill writes that document.

It is a behavior guide: not an inventory of test names, not a walk of the
implementation, not a proposed redesign.

## Paths

Read `PHOENIX.md` for the paths: `tests` (the Evaluation), `spec` (the
Terms section of the specification), and `contracts` (the API contract and
the schemas). Take the scope from `$ARGUMENTS`; an explicit path from the
user wins over `PHOENIX.md`.

The vocabulary is the Terms table: Term, Meaning, Avoid
(`/phoenix-kit:contract` writes it). When no such table exists, say so and
label each term that you propose. A vocabulary review
(`/phoenix-kit:vocabulary`) can come first: its shared terms are the best
start for this document.

## Steps

```
- [ ] 1. Scope and inputs — done: the scope, the tests, the vocabulary source, and the output path
- [ ] 2. The vocabulary   — done: each term comes from the specification, or is labeled proposed
- [ ] 3. The evidence map — done: each rule has its scenario, and each gap is named
- [ ] 4. Reader order     — done: the sections follow the reader, not the test layout
- [ ] 5. The document     — done: one short sentence per behavior, one source link per group
- [ ] 6. The check        — done: terms, limits, and links verified against the inputs
```

### 1. Scope and inputs

Name the feature or unit, the test scope, the vocabulary source, and the
output path. When a required input is missing, or two unrelated scopes fit
equally well, ask one focused question. Do not assume a folder named
`tests` or a file named `openapi.yaml`.

### 2. The vocabulary

Extract the actors, concepts, actions, states, and records from the Terms
table. Keep a term whose meaning differs between contexts distinct, and
qualify it.

Use the table over a convenient synonym. Link to it; do not write a
competing glossary. Preserve routes, field names, schemas, and exact
messages, and explain a misleading name instead of renaming it.

### 3. The evidence map

Read the assertions, the setup, the fixtures, the parameterized cases, and
the expected-output files. A test name is not evidence. Follow a helper
far enough to see the operation it exercises: a helper named `take` may
send an action named `pick`.

Record the observable inputs, preconditions, outcomes, side effects, state
scope, limits, error priority, ordering, persistence, and legacy
exceptions. Keep the exact units, boundary values, and case sensitivity.

Mark the evidence:

| Situation | The label |
| --- | --- |
| A conflict between a test and the specification | **Conflict**, with both sources |
| A behavior that only a document states | **Documented, not directly tested** |
| A behavior that no source covers | **Unknown**, a gap, never a negative guarantee |
| Evidence from the implementation only, when the user allows it | **Implementation only**, labeled apart |
| A skipped test or an expected failure | Not current behavior |

Reading a test is not running it. Claim no execution and no runtime
verification unless you ran the suite. This skill needs no test run, and
some suites touch live services: do not run them to write a document.

### 4. Reader order

Order the rules for the reader: the starting state and the actors, the
main workflows, the state and the resources, the limits, the exceptions,
the completion and the records, then the errors and their priority. Adapt
the order to the domain; do not copy the headings of another system.

### 5. The document

Default output: `docs/behavior-overview.md` from the project root, or the
path that the user names. It is a durable document, so it does not go to
`.phoenix/`, which is scaffolding. For several bounded contexts, scope the
filename instead of merging the meanings. Read an existing target first,
and keep its unrelated content.

```markdown
# <System or feature> — behavior overview

Scope and sources, the link to the Terms table, and the evidence basis:
the tests and specifications that you read, and whether they ran.

## Starting state and actors
## Main workflows
## State and resources
## Limits and exceptions
## Completion and records
## Errors and their priority
## Public vocabulary mapping
## Evidence gaps
## Sources
```

Drop a section that does not apply. Name no test function in the
narrative: put a source link per section or per rule group. When a public
field or operation differs from the domain word, add a small mapping
table. Claim no more than the scope covers.

### 6. The check

Recheck the terms, the numbers, the limits, the failure paths, the state
that is shared or per actor, and the legacy exceptions against the inputs.
Check that each link resolves. Check that each in-scope rule is written or
explicitly excluded.

## Report

- The file path, the scope, and the sources that you read.
- Whether the tests ran, and why not when they did not.
- The material evidence gaps, conflicts, and documentation-only claims.

## Guardrails

- Every material claim points to a test, a specification, or a contract.
- An example stays an example, not a universal guarantee.
- Write only the overview. Change no test, term, contract, or code.
- A gap stays visible; never convert it into a rule.
