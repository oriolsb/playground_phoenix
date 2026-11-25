---
name: vocabulary
description: Reviews the words that the tests, the specification, the contracts, and a behavior overview use for the same thing, and writes one Markdown review of the conflicts, with a small minimal wording correction for each. Use before a rewrite, before a new team joins, when a term starts to drift, or when the user says "review the vocabulary", "check the terminology", or "phoenix vocabulary".
argument-hint: "[the context, feature, or unit to review]"
license: MIT
metadata:
  author: phoenix-kit
  version: "0.1.0"
---

# Vocabulary

One meaning per term is the test of the Context Boundary. In a living
system the words drift first: the tests, the contract, and the
specification start to name the same thing differently. This skill finds
the drift and writes it down.

It reviews the language of observable behavior, not the naming of the
code.

## Paths

Read `PHOENIX.md` for the paths: `tests`, `spec` (the Terms section),
`contracts`, and `decisions`. Take the scope from `$ARGUMENTS`; an
explicit path from the user wins over `PHOENIX.md`.

The authority is the Terms table: Term, Meaning, Avoid
(`/phoenix-kit:contract` writes it). A mapping table in the review is a
review artifact, not a new glossary.

When a behavior overview exists beside the specification
([`explain`](../explain/SKILL.md) writes it), review it too. Do not create
one as a side effect.

## Steps

```
- [ ] 1. Scope and inputs   — done: the scope, the sources, and whether an overview is present
- [ ] 2. Defined terms      — done: each term has its meaning, its context, and its public names
- [ ] 3. Terms in use       — done: the words of the tests, the contracts, and the overview are collected
- [ ] 4. Compare meanings   — done: each finding names two meanings, not two spellings
- [ ] 5. Rank and correct   — done: the findings are ordered by impact, each with one minimal fix
- [ ] 6. The review         — done: the four sections are written, the links resolve, the gaps are separate
```

### 1. Scope and inputs

Name the context and the sources. Read an existing review before you
write. When an input is missing, or the scope is ambiguous, ask one
focused question. Report an absent source as absent; never compare with a
document that you did not read.

### 2. Defined terms

Extract each defined term, its alias, its context, and the public field,
route, or operation that carries it. A term that means different things
in different bounded contexts is two rows, not one.

### 3. Terms in use

Collect the words from the tests, the contracts, and the overview. Read
the assertions, the descriptions, and the fixtures: a test name is not
evidence. Follow a helper only to understand the action that it sends.

### 4. Compare meanings

Compare meanings, not spellings. Look for:

- two synonyms that hide one concept;
- one word that names two concepts;
- an action that the prose calls an operation;
- an event that the prose calls a counter;
- an identifier that the prose calls a display name;
- a state that the prose calls a lifecycle;
- an in-memory record that the prose calls a persistent one.

Check that a different description does not hide a limit, a unit, a
refusal, an ordering, a state scope, or a legacy exception. Flag a
coverage gap as a gap, not as a vocabulary defect.

Literal messages and historical API names may differ from the prose when
the mapping is explicit: explain the mapping, and keep the name.

### 5. Rank and correct

Order the findings by the damage they do: a description that misleads
about behavior comes before a cosmetic drift. For each, give one minimal
correction. Mark a new term as proposed, and link to the definition that
already exists. When two definitions disagree, record the open choice
instead of choosing silently.

### 6. The review

Default output: `docs/vocabulary-review.md` from the project root, or the
path that the user names. Scope the filename when contexts would collide.

```markdown
# <System or feature> — vocabulary review

## Scope
The inputs, the exclusions, and whether an overview or a contract existed.

## Findings
Each finding, ordered by impact: Issue, Evidence, Impact, Shared wording,
Minimal correction.

## Shared vocabulary
| Term | Meaning | Status or source | Public names and aliases |

## Behavioral conflicts and coverage gaps
Documentation-only claims, conflicts, and gaps, kept apart.

## Recommended follow-up
The small, concrete wording changes, and any check that is missing.
```

Give the path and the line of each source, and say that a line number can
move. Group repeated instances of one mismatch into one finding. Report
"none found" rather than inventing a finding.

## Report

- The review path, and the most important findings.
- The inputs that were missing, and what that limits.
- Whether the tests ran; a review needs no run.

## Guardrails

- A finding names two meanings, with evidence for both.
- Defined and proposed terms stay separate.
- Preserve public names, routes, fields, and literal messages.
- Write only the review. Rename no test, edit no glossary, change no code.
- An applied correction is reported as applied; a recommendation stays one.
