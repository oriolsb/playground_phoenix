---
name: assess
description: Assesses a legacy component for regeneration — finds the unit (the regenerative grain), hunts scar tissue, grades the four primitives, flags hybrid components, and writes the work plan in the sequence of risk. Use on code that operates now and holds knowledge nobody wrote down, before adding primitives to it, or when the user says "assess this component", "is this legacy code ready to regenerate", or "phoenix assess".
argument-hint: "[the component, module, or folder to assess]"
license: MIT
metadata:
  author: phoenix-kit
  version: "0.1.0"
---

# Assess

The implementation remembers. The organization forgets. Before you change
or delete legacy code, find out what it knows, and write that down in a
primitive.

## Paths

Read `PHOENIX.md` at the project root. On a legacy system it is often
missing: then propose one, the machine block of the kit's
`schemas/README.md` (section 1) and a Units row (section 8) from the
unit card. Write it to `.phoenix/proposal/PHOENIX.md` and run `check
config --root .phoenix/proposal`; only the errors count, as the paths do
not exist there. Fix each error and run it again, three passes at most;
if one stays, stop and report it. The person saves it at the root.
`check` means `python3 <kit>/scripts/phoenix_check.py`, from the project
root; `<kit>` is two folders above this file ([CONTRACTS.md](../../CONTRACTS.md), "Run the checks").

## Steps

```
- [ ] 1. The unit        — done: it passes the five grain tests and the locality check
- [ ] 2. Scar tissue     — done: each hit has a file, a line, a behavior, and a lesson
- [ ] 3. The unit card   — done: each field filled, each dependency has a kind
- [ ] 4. Grades          — done: each primitive graded, each gap named
- [ ] 5. Hybrid          — done: the data-movement lines and the rule lines are named
- [ ] 6. Work plan       — done: the five steps in the order of risk, first command named
```

### 1. The unit

Start from `$ARGUMENTS`. Apply the five tests. The unit is the natural
part you can delete and rebuild on its own.

| Test | Question | Signal |
| --- | --- | --- |
| Comprehension | Can a reader understand the rules and the edge cases in about ten minutes? | Longer means the unit is too big. |
| Isolation | Can you verify it at its boundary, without the rest of the system? | A test needs the whole system: too coupled. |
| Data ownership | Does this unit alone write its data? | Shared writes hide coupling. The most reliable signal. |
| Contracts | Does it communicate through a versioned, schema-checked interface? | Ad-hoc dicts and tuples: no contract. |
| Feeling | How does deleting it feel? | A small inconvenience means the right size. Fear means hidden knowledge. |

Folder boundaries are the least reliable signal. Resize the unit until
the tests pass, and say what you merged or split.

Then check **locality** (from Matt Pocock's `codebase-design` skill,
MIT): one need changes the unit in one place. Take a likely need, for
example "change the limit", and list the modules it touches. Several
modules, or a check that other flows pass through, means no clean seam:
to remove the unit breaks other flows. Say so, and resize or plan a seam.

### 2. Scar tissue

Read the unit's code. Grep for: `timeout`, `retry`, `sleep`, `except`
with a bare `pass`, `TODO`, `hack`, `workaround`, `legacy`, a numeric
constant with no name, a special-case `if` on one value, and a check that
the brief or the rules do not mention. For each hit, ask: "what does this
code know that we have forgotten?" Record file, line, the behavior, and
the lesson it probably encodes. Keep all of it for now.

### 3. The unit card

```markdown
## Unit: <name>

- Public contract: <the names other code imports, the routes it serves>
- Consumers: <who calls it, from grep>
- Data owned: <datasets it writes> — Data shared: <datasets with another writer>
- Pace layer: fast | medium | slow — Kind: core | supporting | generic
- Dependencies: <each one, and its kind from the table below>
- Rules: <the rule IDs of the unit; "none yet" until work plan step 2>
- Modules: <each file of the unit's code, as a path from the project root>
- Risk: <low | medium | high>, and why
```

The Units row takes Rules, Modules, Risk, and the Public contract as its
Interface. A row with no rule ID is not complete: fill it after work
plan step 2.

The kind of each dependency decides how the Evaluation reaches the unit:

| Kind | Example | How the Evaluation reaches it |
| --- | --- | --- |
| In process | Pure rules, in-memory state | Through the unit's interface, with nothing replaced |
| Local stand-in | An in-memory store, a temporary folder | The stand-in runs in the suite |
| Remote, owned | Your own service over a network | A port, with a test adapter |
| External | A third-party API | A port, with a fake adapter |

### 4. Grades

Grade each primitive: **strong** (explicit, machine-checkable),
**partial** (gaps), **absent** (missing or too weak to use). Name the
gap. A low grade is not a team failure: it lists what to write first.

### 5. Hybrid component

A component that mixes data movement with business rules is difficult to
regenerate. If the unit does both, say which lines are which, and plan the
separation before the specification.

### 6. The work plan, in the sequence of risk

Freeze the Context Boundary first, because a boundary change reaches other
teams. An internal change does not.

1. **Freeze the boundary.** List every name other code uses: ports,
   routes, entry points, error types. Write the contract from what the
   code does, with `/phoenix-kit:contract`. Name one owner per dataset.
2. **Capture current behavior.** Each scenario needs a rule ID: first
   write each behavior as a short rule with `/phoenix-kit:specify`,
   Source: the file and the line. Then run `/phoenix-kit:evaluate
   characterization <rule IDs>`: through the boundary, aimed at the
   contract so it survives a rewrite, each scenario passes today.
3. **Complete the specification.** With `/phoenix-kit:specify`, revise
   the rules of step 2 by ID; a behavior keeps one ID. A new rule gets
   its characterization scenario as in step 2.
4. **Record the provenance.** One decision per piece of scar tissue, with
   `/phoenix-kit:decide`. Status "written after the code". Evidence: file and
   behavior.
5. **Run the Deletion Test** with `/phoenix-kit:deletion-test`, then
   regenerate.

Write the assessment to `.phoenix/assessment/<unit>.md`, with
[assets/assessment-template.md](assets/assessment-template.md). It is
scaffolding, outside the primitive paths, so `generate` can still start
on a clean tree. Delete it when the primitives it points to exist.

## Report

- The unit, and how you resized it.
- The scar tissue count, and the three riskiest items.
- The four grades.
- The work plan with the first command to run.

## Guardrails

- Scar tissue stays in the code until its lesson is in a rule or a
  decision.
- Specify the unit, not the whole system.
- Each boundary name stays as it is during the assessment.
