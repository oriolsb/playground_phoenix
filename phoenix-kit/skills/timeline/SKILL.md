---
name: timeline
description: Reconstructs how a legacy system reached its present shape, as one Markdown document for a new maintainer, keeping what changed, when it changed, and why it changed as three separate confidences. Works with or without git history. Use before changing code that nobody on the team designed, or when the user says "how did this evolve", "tell me the history", or "phoenix timeline".
argument-hint: "[the repository, folder, or unit in scope]"
license: MIT
metadata:
  author: phoenix-kit
  version: "0.1.0"
---

# Timeline

The code remembers. The reasons are gone. This skill writes the story of
how the system reached its present shape, so a new maintainer can change
it without breaking what the story protects. It is a reconstruction, not
a claim to know what the first team thought: a useful story is selective,
the turning points that still shape decisions, not a changelog.

## Paths

Read `PHOENIX.md` for the paths of the primitives: `spec`, `decisions`,
`tests`, `sources`. Take the scope from `$ARGUMENTS`; when it is empty,
the whole project. An explicit path from the user wins over `PHOENIX.md`.

A legacy project often has no `PHOENIX.md`. Then use the folders that
hold the specification, the decision records, and the tests, and say in
the report which paths you used.

## Steps

```
- [ ] 1. Scope and baseline — done: the scope, the exclusions, the baseline source or "none exists", and the present-state sources
- [ ] 2. Evidence          — done: each candidate has a before, an after or "unknown", and one source pointer
- [ ] 3. Selection         — done: each kept event says why knowing it changes maintenance
- [ ] 4. Chronology        — done: change, placement, and why are judged separately, and each guess is visible in its event
- [ ] 5. The story         — done: the four sections are written, the links resolve, the weakest guesses are named
```

### 1. Scope and baseline

Fix the repository or subdirectory in scope, the oldest available brief,
design, or earlier implementation, and the present implementation. Honor
the exclusions that the user names, in searches and in git commands.

A brief is evidence of an *intended* baseline, not proof that production
ever implemented it. When two readings would change the story, ask one
focused question.

Read the existing ADRs, specification, contracts, tests, release notes,
and incident references before you write a word. If the project already
has an account of its history, preserve it: update it, do not replace it
silently.

### 2. Evidence

With git, inspect history **read only**: `log --follow` for renames, the
patch of each important commit, blame, tags, and the documentation and
test changes near them. Read the patch, never the title alone.

A commit date is evidence of when the *code* arrived, not when the
product decision was made. Check whether the history is shallow,
imported, or starts after the design.

Without usable git, say so and continue with the artifacts that exist.

Compare the baseline with the code and the observable tests. Search the
scoped material for comments about requests, clients, incidents,
migrations, operational constraints, and deprecations. Keep a source's
*claim* ("Product asked for this in 2022") apart from a verified
provenance. Trace each candidate through behavior, API, data ownership,
consumers, and tests, and record where the account and the code disagree.

### 3. Selection

Keep a decision when it has broad consequences, is hard to reverse,
explains surprising behavior, or holds a trade-off that a maintainer must
understand. Group dependent changes into one event. Separate unrelated
changes that share a commit.

Drop mechanical refactors, isolated fixes, and rules that the brief
already states, unless they explain a bigger turn. Do not invent
alternatives, and do not claim that every behavior was deliberate.

### 4. Chronology

For each event, record three independent judgments:

| Judgment | The values |
| --- | --- |
| Change | confirmed in the code or history, reported by a document, inferred |
| Placement | commit date, date reported by a source, order implied by a dependency, speculative |
| Why | stated by a source, inferred from the effects, unknown |

Anchor the dated events first. Infer only the order that a dependency
supports: a destination must exist when a route to it is deployed, but
both can arrive together. A difference between an old brief and the code
proves divergence, not the sequence of deployments.

Use "undated; tentatively before X" instead of an invented year. When two
events cannot be ordered, group them in an undated phase. Give a reason
and a credible alternative for the weakest placement.

Ask a focused question only when a missing answer would change the story.
Otherwise label the hypothesis and put the question in the report.

### 5. The story

Default output: `docs/legacy-decision-timeline.md` from the project root,
or the path that the user names. If the file exists, update it and keep
what the evidence has not disproven.

```markdown
# <System> — how it reached its present shape

## Scope and evidence limits
The baseline, the present system, the exclusions, whether git covers the
scope, and what confirmed, inferred, and speculative mean here.

## Timeline
| When | What changed | Evidence | Change | Placement | Why |

## The story for a new maintainer
The turning points in a readable order: the constraints that accumulated,
the seams and scar tissue that remain, and what a future change risks.

## Unresolved links
The orders that still compete, the reasons that are missing, and the
short questions that a former maintainer could answer.
```

Make each guess visible inside its event, not only in a disclaimer.

A turning point whose reason is now known becomes a decision record with
`/phoenix-kit:decide`, so the next maintainer finds it without the
timeline. The two documents do not repeat each other: the timeline keeps
the order, the record keeps the argument.

## Report

- The file path, and the scope that it covers.
- The three weakest assumptions, and why they are weak.
- The questions that only a former maintainer can answer.

## Guardrails

- Report a change, its date, and its reason as separate claims.
- Cite a file and a line, or a commit and a path, for each event.
- Record a dated comment as a comment, not as the request itself.
- Write no ADR and change no code: this skill produces a timeline.
- A gap stays a gap; never fill it with narrative convenience.
