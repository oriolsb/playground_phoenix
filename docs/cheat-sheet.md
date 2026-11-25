# Spec-Driven Development and Phoenix Architecture — Cheat Sheet

**This file is a reference.** It distills the principles of spec-driven
development with Phoenix Architecture: what to write, in which order, and
how to check it. Use it when you start a project, when you add the
primitives to legacy code, and when you evolve a system.

## How to use this sheet

Start with [the sheet on one page](#the-sheet-on-one-page). It holds the
four primitives, the order of work in each pillar, and seven rules of
daily work. Each rule links to its detail.

The sheet has these parts:

1. [The core idea](#0-the-core-idea): the four primitives, and the
   Deletion Test.
2. [The Three Pillars](#the-three-pillars): one recipe for each state of
   the system, with its checklist.
3. [Practices for every pillar](#practices-for-every-pillar): how to
   write the primitives, check them, and generate the code from them.
4. [Anti-patterns](#anti-patterns).

The appendices hold the notations, the catalogue of documents, the
toolkits, and the critiques and the evidence. Use the
[glossary](#glossary) when a term is not clear. The
[references](#references) give the source of each idea.

## The sheet on one page

**The question.** "If I deleted this codebase and regenerated it from
scratch, what would I rely on to decide whether the result was correct?"
Your answer is four primitives.

| Primitive | It holds | Test it with one question |
| --- | --- | --- |
| Specification | The rules, the limits, and their reasons | Can a person build a correct system from it, with no access to the code? |
| Evaluation | The checks that every correct version passes | Do the checks stay valid after a rewrite in another language? |
| Context Boundary | The contracts and the vocabulary | Is it machine-readable, with one owner for each dataset and one meaning for each term? |
| Provenance | The reasons for the current form | Can a new team learn why, with no access to the first team? |

**The three pillars.** In each pillar, record the Provenance at the
moment of each decision.

| You find | Pillar | Order of work | Checklist |
| --- | --- | --- | --- |
| No code | The Present | Specification, Context Boundary, Evaluation, then the code | [Start a green field project](#checklist--start-a-green-field-project) |
| Code that holds knowledge that nobody wrote down | The Past | Context Boundary, Evaluation, Specification, then the Evaluation again | [Assess a legacy component](#checklist--assess-a-legacy-component) |
| The primitives, and a new need | The Future | Two separate steps. Architecture first, only if the need asks for it: a failing fitness function, then the design change. Then the behavior: Specification, Evaluation, then one increment | [Evolve a system](#checklist--evolve-a-system) |

**Seven rules of daily work.**

1. Choose the risk tier first. It sets how much specification the work
   needs. ([Size the specification to the risk](#size-the-specification-to-the-risk))
2. Work in thin vertical slices. The first slice holds the slow
   decisions. ([How to start](#how-to-start))
3. Give each rule an ID and a reason.
   ([What a specification can look like](#what-a-specification-can-look-like))
4. Check the behavior at a stable boundary: an oracle, not an ephemeral
   test. ([Oracle or ephemeral test](#oracle-or-ephemeral-test))
5. Generate the code with one controlled implementation prompt. If the
   code is wrong, fix the primitive, not the code.
   ([Pedro's L3 Law](#pedros-l3-law--specifications-first-code-second))
6. Triage each gap that the agent reports. Keep only what must survive
   a regeneration.
   ([Pedro's L3 Law](#pedros-l3-law--specifications-first-code-second))
7. Prove the result with the Deletion Test.
   ([The Deletion Test](#the-deletion-test))

## 0. The core idea

A regenerative system is a system that you can delete and rebuild
correctly from its primitives alone. Code is temporary. Intent is durable.

This idea comes from the [Phoenix
Architecture](https://aicoding.leaflet.pub/) series by Chad Fowler. Fowler
asks one core question:

> "If I deleted this codebase and regenerated it from scratch, what would I
> rely on to decide whether the result was correct?"

If the honest answer is "the old code", then the code is the specification,
the test suite, and the documentation at the same time. Fowler calls this
entanglement.

The four primitives are your answer to that question.

### The four primitives

[The Phoenix
Primitives](https://aicoding.leaflet.pub/3mjfruwwuck2d) defines them:
"Delete the implementation, keep those four artifacts, and you can
regenerate a working system. Delete any one of the four, and you can't."
The article gives no test for each primitive. The tests in the table are
the synthesis of this sheet, from several sources (see below the table).
Apply each test to find a gap.

| Primitive            | What it holds                                                               | The test                                                                                                 | The failure                                         |
| -------------------- | --------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------- | --------------------------------------------------- |
| **Specification**    | The behavioral rules, the operational constraints, and the decisions behind them | Can a competent implementer build a correct system from this document alone, with no access to the code? | A rule exists only as code behavior                 |
| **Evaluation**       | Runnable checks that each correct implementation must pass                  | If you rewrote the system in a different language, would the checks still be valid?                      | The checks pin internal details                     |
| **Context Boundary** | The contracts and vocabulary that other systems depend on                   | Is the boundary machine-readable? Does one component own each dataset? Does each term have one meaning?  | Contract drift, shared writes, or an ambiguous term |
| **Provenance**       | The record of why the system has its current form                           | Can a new team understand why the system behaves this way, with no access to the first team?             | A decision exists only in memory                    |

Lose one primitive, and you cannot regenerate safely.

The sources of the tests:

- **Evaluation:** [Evaluations Are the Real
  Codebase](https://aicoding.leaflet.pub/3mb526js42k26): "if
  reimplementing your service in a different language would invalidate
  your test suite, your tests are specified at the wrong boundary."
- **Context Boundary:** one owner for each dataset comes from [Compile to
  Architecture](https://aicoding.leaflet.pub/3mgfsrk75ac2l), which
  "assigns exclusive mutation authority for each dataset to a single
  component". One meaning for each term comes from Domain-Driven Design,
  see [the two layers](#the-two-layers-of-a-context-boundary).
- **Specification and Provenance:** this sheet, from the definitions of
  the article.

Fowler calls the Deletion Test "a diagnostic": one question. [The
Deletion Test](#the-deletion-test) below turns it into a procedure with
two lists. The Past pillar gives a way to [grade each
primitive](#grade-each-primitive) of a component that operates now.

The essay series names four primitives, and this sheet teaches those
four. Fowler's book _Regenerative
Software_ ([O'Reilly](https://www.oreilly.com/library/view/regenerative-software/0642572383954/),
an early release) counts seven. The
[spotregen](https://arxiv.org/abs/2610.17197) paper quotes them as
"intent, compilation, evaluation, provenance, pace, deletion, and
compaction", and [chad/phoenix](https://github.com/chad/phoenix) has a
similar list. Context Boundary is not a name in that list. This sheet
keeps the four of the essays. Pace layers, the Deletion Test, and
compaction appear in this sheet as tests and tools.

### The Deletion Test

Use the **[Deletion
Test](https://aicoding.leaflet.pub/3md5ftetaes2e)** as a quick check on one
unit. It turns Fowler's question into a procedure. Make two lists.

1. List what stays after a deletion: specifications, tests, schemas, the
   vocabulary, and decision records.
2. List what you lose: knowledge that exists only in the code.

A long second list means a high regeneration risk.

Apply the test to each new system. Apply it again to each legacy
component in the Past pillar.

## The Three Pillars

Each pillar is a recipe for one state of the system: no code (the
Present), legacy code (the Past), or a new need (the Future). [The sheet
on one page](#the-sheet-on-one-page) gives the order of work in each
pillar. In every pillar, record the Provenance at the moment of each
decision. A decision that you record later is a reconstruction, and a
reconstruction is unreliable.

### 1. The Present — spec-driven development with Phoenix Architecture

**Spec-driven development** is the practice of writing the specification
first and deriving the code from it. GitHub states the rule in one line:
"Define what to build and why, then turn the specification into a plan,
tasks, and working code" (the Spec Kit README, 2026). The specification is
the artifact that lasts. The code is the output. The [toolkits
appendix](#appendix--the-toolkits) gives the current tooling.

The counterexample is **vibe coding**: an LLM generates the solution
directly from a prompt, with no specification. It can give high-quality
code, but high-quality code is not durable system knowledge.

Vibe coding is fast, and it is not the opposite of skill. It loses the
reasons. Nobody records which alternatives the agent rejected, or which
constraint forced a choice. So the next change starts from the code alone.

#### How to start

**When the problem is clear, the Specification leads.** An empty folder
gives you nothing else to start from.

**When the problem is not clear, explore first.** Fowler rejects the
reading "write the specification first, and only then are you allowed to
program": "That's not what I mean." ([The Spec Can Come
Later](https://aicoding.leaflet.pub/3mwlzitykzc27), 28 September 2026.)
"The first implementation is how you discover what you mean. The second
is how you find out whether you wrote it down." So the order is a
choice. Build a first version to learn, write the primitives from what
you learned, and then regenerate. Both ways end with the same test: the
primitives must pass the Deletion Test.

Exploration is part of the specification work, also when the problem is
clear. A spike can discover a behavioral rule, an operational constraint
such as a latency limit, or an architecture choice and its boundaries.
Keep what it teaches you in the primitives, not in the throwaway code.

**In thin vertical slices.** Do not write the primitives of the whole
system before the first line of code. Do the steps of the checklist
below for one thin vertical slice: one behavior that a user can see. Then
do the next slice. Put the slow decisions in the first slice: the
architecture, the entry point, the error type, and the data formats. If
one decision can wait, record in the slice plan why. A later slice can
add to them. It must not change them.

**Provenance, at each step.** Each step of the checklist is a sequence of choices.
Record each choice as you make it: the option you took, the alternatives
you rejected, and the constraint that forced the choice. In a green
field, no code holds the reason for a choice.

#### Checklist — start a green field project

Choose the [risk tier](#size-the-specification-to-the-risk) first. It
tells you how much of each step below the work needs. Then split the
work into thin vertical slices. Do steps 1 to 6 for each slice, and step
7 at the end. The first slice holds the slow decisions.

1. Write the behavioral rules first. Give each rule an identifier.
   (`/phoenix-kit:specify`)
2. Add the operational constraints to the specification. Latency, cost, and
   reliability are requirements. (`/phoenix-kit:specify`, prefix `OPS`)
3. Record each decision as you make it, with its rejected alternatives and
   its forcing constraint. (`/phoenix-kit:decide`)
4. Write the machine-readable contracts next, for example OpenAPI or JSON
   Schema. (`/phoenix-kit:contract`)
5. Write durable checks against those contracts, not against the internal
   code. (`/phoenix-kit:evaluate`)
6. Generate the code last, with one controlled implementation prompt. If
   the result is wrong, fix the primitive, not the code. Triage each gap
   that the agent reports. (`/phoenix-kit:generate`,
   in a new session)
7. Apply the Deletion Test before you call the work complete.
   (`/phoenix-kit:deletion-test`)

### 2. The Past — add Phoenix primitives to legacy code

Add the primitives to a system that operates now. First find if the
system is ready for regeneration. Then write specifications that record the
current behavior. Use those specifications as a safe base for change.

Legacy code holds knowledge that nobody wrote down. Fowler calls this
knowledge **[scar
tissue](https://aicoding.leaflet.pub/3mobohx4fq22x)**. Examples are
timeouts with no explanation, defensive checks, and strange conditional
statements. Each one records a lesson from a past problem.

> "The implementation remembers. The organization forgets."

Move that knowledge into a specification before you change or delete the
code that holds it.

Spec Kit gives the opposite advice, and the difference is worth knowing.
Its brownfield guide asks for a specification of the next bounded change,
and ["not a retroactive specification of every existing
behavior"](https://github.github.io/spec-kit/guides/existing-projects.html).
It warns against making "document the entire existing system" the first
feature.

Both positions are sound, because the goals differ. Spec Kit serves the
next delivery. This pillar serves the knowledge that only the code holds.
Scar tissue disappears in a rewrite, so record it first. Then keep the
scope to the unit that you assess, and not to the whole system. The next
section finds that unit.

#### Find the unit to assess

A unit is the natural part that you can delete and rebuild on its own.
Fowler calls it the [regenerative
grain](https://aicoding.leaflet.pub/3mfai4nqg6224). The unit is not a
primitive, and you need it before the primitives. Apply five tests.

1. **Comprehension** — can a reader understand the rules and the edge cases
   in about ten minutes?
2. **Isolation** — can you verify the unit at its boundary, without the
   rest of the system?
3. **Data ownership** — does this unit alone write its data? Shared writes
   hide coupling. Fowler calls it "mutation ownership": read models do not
   matter.
4. **Contracts** — does the unit communicate through a versioned,
   schema-checked interface?
5. **Feeling** — how does deleting the unit feel? A trivial loss means
   that the unit is too small. A small inconvenience means the unit is
   the correct size. Fear means the unit holds hidden knowledge.

Data ownership is a strong signal. Fowler writes that it defines seams
"far more reliably than file boundaries ever will" ([Compile to
Architecture](https://aicoding.leaflet.pub/3mgfsrk75ac2l)).

#### Grade each primitive

Step 3 of the checklist below asks for a grade. Give each primitive of the
unit one grade. Name the gap for each grade below strong.

- **Strong** — the primitive is explicit and machine-checkable. A
  regeneration can depend on it.
- **Partial** — the primitive has gaps. A regeneration is incomplete or
  incorrect.
- **Absent** — the primitive is missing, or it is too weak to use. A
  regeneration fails in silence.

A grade of partial or absent is not a failure of the team. It is the list
of what to write down first.

#### Checklist — assess a legacy component

1. **Find the unit.** Apply the five tests above.
2. **Look for scar tissue.** Find timeouts, retries, and special cases with
   no explanation. Ask: "what does this code know that we have forgotten?"
3. **Grade the four primitives.** Use strong, partial, or absent. Name each
   gap.
4. **Look for a hybrid component.** A component that mixes data movement
   with business rules is difficult to regenerate. Mark it, and plan the
   split. Do the split after step 5 records its behavior.
5. **Work in the sequence of risk.** Freeze the Context Boundary first, and
   name one owner for each dataset. Record the current behavior in
   characterization checks next. Write the Specification after that. Then
   aim the checks at the contract, so that they survive a
   reimplementation. Record the Provenance as you make each decision.

Optional: `/phoenix-kit:assess` runs steps 1 to 4 and writes the work
plan of step 5, with the command for each part. The plan ends with
`/phoenix-kit:deletion-test`, then a regeneration.

#### Why this order

**Context Boundary leads, for two reasons.** The first is risk: a boundary
change reaches other teams, and an internal change does not. The second is
practical: you cannot place a characterization check until you know where
the seam is. A check at the wrong seam becomes an ephemeral test, and it
dies on the first reimplementation.

**Give each recovered rule a status:**

- **Observed:** the code does it, and nobody decided it.
- **Accepted:** you keep it on purpose.
- **Contested:** you doubt it, and you record the question.

Fowler: "extraction is not authority". A rule that you regenerate faithfully is not yet a rule that
you want.

**Provenance, at each step.** This pillar has two Provenance activities,
not one. Record each new choice as you make it, as in the other pillars.
Also find the Provenance that nobody wrote down: the scar tissue. For each
timeout, retry, and special case, ask one question: what does this code
know that we have forgotten? Write the answer into the Specification
before you change the code that holds it.

### 3. The Future — evolve systems with Phoenix and Evolutionary Architecture

Neal Ford, Rebecca Parsons, and Patrick Kua give this definition of an
[evolutionary
architecture](https://evolutionaryarchitecture.com/precis.html): it
"supports guided, incremental change across multiple dimensions."

Phoenix Architecture gives you the primitives to change one part safely.
Evolutionary Architecture gives you the discipline to decide when and how
to change it.

#### Two kinds of change, never in one step

A need can ask for two kinds of change. Keep them apart. Do not change
the behavior and the architecture in the same step.

| Change | It serves | It starts with | It is done when |
| --- | --- | --- | --- |
| **Behavior** (functional, business) | The need itself | The Specification and the Evaluation: the new rule, and its check that fails | The new check passes, and each earlier check still passes |
| **Architecture** (design) | A behavior change. It is never a goal of its own. | A fitness function that fails. It states the characteristic that the design must reach. | The fitness function passes, and the Evaluation of the behavior did not change and still passes |

When a need asks for both, change the architecture first. Kent Beck:
"make the change easy (warning: this may be hard), then make the easy
change." The architecture step changes no behavior, so the Evaluation
of the behavior is its safety net. The behavior step changes no
architecture, so the fitness functions are its safety net.

Optional: `/phoenix-kit:change propose <name> "<the need>"` writes the
need and the rules that change as a delta: added, modified, removed,
renamed. While the change is open, every skill reads the delta as part
of the Specification and writes its edits into it. The skill prints the
hand-off, the order of the work from the review to the regeneration.
`/phoenix-kit:change archive <name>` merges the delta into the
specification when the Evaluation is green and a decision names the
change. The change layout comes from OpenSpec.

#### Core ideas

- **Guided by a need** — each architecture change serves a named
  business need or operational need. Without a need, do not change the
  architecture. Write the target of the architecture as a fitness
  function that fails today.
- **Fitness functions** — automatic checks that define "fit" for your
  system. Run them on each change to find drift.
- **Incremental change** — build and deliver one small increment at a
  time. A small increment is easy to verify and easy to reverse.
- **Many dimensions** — a system changes on the technical axis and on the
  domain axis at the same time. Monitor both axes.
- **Appropriate coupling** — keep components loosely coupled at their
  Context Boundaries. Then one part can change, and the other parts stay
  the same.

#### Fitness function examples

A fitness function must fail when the system drifts. These examples come
from the Katacombs game, the text-based adventure game that the workshop
builds.

| Characteristic          | Fitness function                                                             | How it fails                          |
| ----------------------- | ---------------------------------------------------------------------------- | ------------------------------------- |
| Layer separation        | An import checker asserts that the domain imports no framework               | A new import breaks the contract      |
| Simplicity              | A checker asserts cyclomatic complexity of 10 or less for each function      | A long function fails the gate        |
| Latency                 | A test sends 100 calls and asserts the 99th percentile is below 100 ms       | A slow change fails the gate          |
| Test coverage of a rule | A checker asserts that each rule has a test through each way into the system | A rule with one way in fails the gate |
| Correctness under load  | Two parallel commands must give one success and one refusal                  | A lost update fails the test          |

In this sheet, a fitness function is part of the Evaluation primitive:
it checks an architecture characteristic. This link is our interpretation.
Fowler discusses fitness functions as checks that maintain architecture
constraints, in [Most of Your Architecture Was Just Expensive
Code](https://aicoding.leaflet.pub/3mtmk6ot6oc2i).

#### Pace layers

Different parts of a system change at different speeds.
**[Pace layers](https://aicoding.leaflet.pub/3maob46kbz22v)** match the
regeneration speed to the part.

| Layer  | Examples                                                        | How frequently to regenerate                   |
| ------ | --------------------------------------------------------------- | ---------------------------------------------- |
| Fast   | The REST adapter, the code behind the user interface            | Hours to days                                  |
| Medium | The game rules, the business logic                              | Weeks to months, with checks on the invariants |
| Slow   | The data model, the ports, the contracts, the security boundary | Rarely, and a person must review               |

The user interface itself, and the messages that players learn, change
slowly. Fowler calls the interface "the human protocol" in [UI Is a
Conservation Layer](https://aicoding.leaflet.pub/3mcxo5ojob22c). The code
behind it can still change fast.

Use three questions to find the layer of a part:

1. **Blast radius** — if this part breaks, does it break something that you
   do not own? Then the layer is slower than it looks.
2. **Recovery time** — does a repair take days instead of minutes? Then the
   layer is deeper than it looks.
3. **Dependency count** — do many parts depend on this one, and it depends
   on few? Then the part is infrastructure.

Do not regenerate a slow layer at the speed of a fast layer. Fowler calls
that erosion, not acceleration.

Pace layers answer how fast a part changes. They do not answer what the
part is worth. [Core Domain
Charts](https://github.com/ddd-crew/core-domain-charts) add that second
axis, and they sort each part into one of three kinds.

| Kind       | The part                                    | What it means for a regeneration                                           |
| ---------- | ------------------------------------------- | -------------------------------------------------------------------------- |
| Core       | It differentiates the business              | The most scar tissue. It earns the heaviest Provenance and a human review. |
| Supporting | Necessary, and it differentiates nothing    | Regenerate it with normal care.                                            |
| Generic    | Everybody needs it, and nobody wins with it | The safest to regenerate, and the first to buy instead.                    |

The two axes are independent. An established authentication mechanism is
often slow and generic. Use a provider when it meets the need. The game
rules are medium and core, so guard them. The pace tells you how often to
regenerate. The kind tells you how much care each regeneration earns.

#### Keep the system small

Generation is cheap. Each new abstraction adds weight that a person and an
agent must hold to make a safe change. Fowler calls the reduction of that
weight **compaction**.

Apply the **concept rent test** to each abstraction: does this concept
justify its existence? If you can remove it with no change in behavior,
then it had no purpose.

> "Refactoring is reorganizing the closet. Compaction is realizing you do
> not need the closet."

Use the **n=1 test** as a limit ([n=1 Is a Design
Constraint](https://aicoding.leaflet.pub/3mbuc4mohwc2k)): if one competent engineer cannot
understand, change, and regenerate the system from its specification, then
the system is already too complex.

#### Checklist — evolve a system

1. **Name the need.** Write down who has the need, and why. Decide if
   the current architecture can serve it. Without a need, do not change
   the architecture. (`/phoenix-kit:change propose`)

The architecture step comes first, and only if the need asks for it:

2. **Write the fitness function that fails.** It states the
   characteristic that the design must reach, with a target and its
   source. (`/phoenix-kit:evaluate`)
3. **Decide what stays stable.** Name the Context Boundary that does not
   move while the inside changes. (`/phoenix-kit:contract`)
4. **Record the decision.** Write the need that it serves, the option
   that you took, the alternatives that you rejected, and the pace layer
   of the part. (`/phoenix-kit:decide`)
5. **Change the design,** with one controlled implementation prompt. The
   step is done when the fitness function passes, and the Evaluation of
   the behavior passes with no change. (`/phoenix-kit:generate`)

The behavior step comes next:

6. **Write the new rule and its check.** Add the rule to the
   Specification and the check to the Evaluation. The check fails.
   (`/phoenix-kit:evaluate`)
7. **Deliver one increment,** with one controlled implementation prompt,
   at the pace layer of the part. (`/phoenix-kit:generate`)
8. **Run all the checks and all the fitness functions,** also those of
   the earlier needs. Then archive the change.
   (`/phoenix-kit:change archive`)

**A check that fails opens each step.** The behavior step opens with a
check of the Evaluation. The architecture step opens with a fitness
function. A check that you add after the change cannot tell you what the
change broke.

**Provenance, at each step.** Record the need that forced the change, the
option you took, and the pace layer that you chose for the part. Each
architecture change adds a link to the chain. A later reader must be able
to learn why the architecture moved, and not only that it moved.

## Practices for every pillar

The checklists point to these practices.

### Write the Specification

#### What a specification can look like

A specification is not one file format. Choose the form that makes each
rule hard to misread. Most projects use several forms together.

| Form                                                           | Use it for                                                                   | Note                                                                                                                                                                                                                                                     |
| -------------------------------------------------------------- | ---------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| A numbered rule with an identifier                             | A behavioral rule, or an operational constraint                              | The plainest form. An identifier such as `MOVE-1` lets a test, a decision record, and a code comment all cite the same rule.                                                                                                                             |
| [EARS](https://alistairmavin.com/ears/) keywords               | A rule that a reader must not be able to misread                             | The clauses always appear in the same order. See [the EARS patterns](#the-ears-patterns) below.                                                                                                                                                          |
| [Given-When-Then](https://cucumber.io/docs/gherkin/reference/) | A rule with concrete examples                                                | Serves two primitives at once. A reader reads it as a specification, and a runner such as [pytest-bdd](https://pytest-bdd.readthedocs.io/en/stable/) executes it as Evaluation. See [the Given-When-Then patterns](#the-given-when-then-patterns) below. |
| A table of examples                                            | A rule with many cases: the messages, the error reasons, a reference journey | Specification by example. A reader checks a table faster than a paragraph, and a missing row is visible.                                                                                                                                                 |
| A machine-readable schema                                      | The shape of an API, or the shape of data                                    | [OpenAPI](https://spec.openapis.org/oas/v3.1.0.html) and JSON Schema. A violation fails a test, so drift cannot pass in silence. This form is also the Context Boundary.                                                                                 |
| A decision record                                              | Why the design is what it is                                                 | This form is the Provenance primitive. See [the decision record structure](#the-decision-record-structure) below.                                                                                                                                        |
| A formal model, or a contract in code                          | A rule where a mistake is expensive: a protocol, a concurrency rule, money  | Design by Contract, [Alloy](https://alloytools.org/), or [TLA+](https://lamport.azurewebsites.net/tla/tla.html). A tool checks the model. Fowler: a specification "can define a space of acceptable programs". The cost is a new language for the team. |

Two current toolkits give a ready structure, and you can copy either one:

- Spec Kit has a
  [specification template](https://github.com/github/spec-kit/blob/main/templates/spec-template.md).
- Kiro splits a feature into
  [requirements, design, and tasks](https://kiro.dev/docs/specs/feature-specs/).

Whichever form you pick, keep two properties. Give each rule an
identifier, so that a test can name the rule that it checks. State the
reason, so that a later reader learns why the rule exists.

#### How long a specification lives

Birgitta Böckeler compared three of these toolkits and found three
different ambitions behind the one term. The level tells you how long the
team expects the specification to live.

| Level          | The specification is                                    | After the task                          |
| -------------- | ------------------------------------------------------- | --------------------------------------- |
| Spec-first     | Written before the code, for the task at hand           | It can rot, and often does              |
| Spec-anchored  | Kept, and used for each later change of that feature    | It stays the source of truth            |
| Spec-as-source | The only file a person edits. An agent writes the code. | The code carries a "do not edit" marker |

Most tools reach spec-first. Fewer aim at spec-anchored.

Spec-first names a lifetime, not the order of work. A start with the
specification can still be spec-anchored.

**Phoenix Architecture needs spec-anchored.** The Deletion Test asks what survives
when the code goes. A specification that a team abandons after the first
delivery survives nothing, so spec-first alone does not pass. You do not
need spec-as-source to pass, and [What to watch for](#what-to-watch-for)
gives a reason to doubt it.

The rule "fix the primitive, not the code" is close to spec-as-source for
the code that you regenerate. The L3 Law keeps an exit: a person can edit
the code when the team records the edit as "an approved manual change
that will not be regenerated".

#### Check the rules against each other

A runnable specification already checks itself in one direction. A
Given-When-Then scenario fails when the code stops obeying the rule, and
you cannot automate a rule that stays vague. That is one axis, and it is
not the only one.

A runner executes each rule on its own. It cannot report a rule that you
never wrote. It cannot find two rules that disagree. It cannot run a
decision record or an operational constraint at all. Both current toolkits add
that second check.

- Spec Kit generates a checklist for each specification. Its documentation
  calls that checklist ["unit tests for your
  requirements"](https://github.github.io/spec-kit/quickstart.html). A
  separate read-only step reports the conflicts and the gaps across the
  specification, the plan, and the tasks.
- Kiro ["checks your requirements for contradictions and gaps using
  automated reasoning techniques"](https://kiro.dev) before it writes any
  code. This is an optional step, "Analyze Requirements", since May
  2026. Its home page gives the reason in the same terms as [the three
  tiers of evaluation](#the-three-tiers-of-evaluation): "'All tests
  passed' doesn't mean the code matches your intent."

Two vendors reached this practice on their own, which is a signal. Read
each rule and ask three questions. Does another rule contradict it? Can a
reader read it two ways? Does an Evaluation name it?

#### Size the specification to the risk

A specification costs time to write and to review. Böckeler shows the
risk in [What to watch for](#what-to-watch-for): one small bug became
sixteen acceptance criteria.

Length is also no proof of quality. In a study of 88,052 pull requests,
the pull requests with a specification artifact did not have fewer
defects ([the studies](#the-studies)).

The L3 Law gives the answer. The depth of the specification must match
the risk and the complexity of the change. The law sets the minimum
specification for each level of risk. We define three risk tiers from it,
and each tier adds to the tier below it. When a change matches two
tiers, the higher tier applies. Record the tiers of your team in the
repository guidance, for example in `AGENTS.md`.

| Risk tier  | When it applies (our interpretation)                                                                                    | Minimum specification (the L3 Law)                                                                                                                                       | Katacombs example                                                              |
| ---------- | ----------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------ |
| **Low**    | One rule changes. No contract changes, and the data model does not change.                                              | The behavior, the scope and the non-scope, the units and the boundaries that the change touches, and the acceptance tests                                                | The bag limit changes from 10 to 12 items                                      |
| **Medium** | New behavior, a change to a contract that a caller uses, or a new dependency                                            | Low, plus the interface or API contract, the errors and the edge cases, the fitness functions, and a decision record for each architecture decision                         | The leaderboard: a new query port and a new endpoint                           |
| **High**   | A slow layer: the data model, a security boundary, a contract that other teams use, infrastructure, a significant change of cost or capacity, or a change that you cannot reverse | Medium, plus:<br>• the architecture and its decision records<br>• security, privacy, and compliance<br>• observability, deployment, rollback, and recovery<br>• a named human approver | A change to the data model of the game, for example durable storage of players |

The L3 Law sets the minimums. The second column is our interpretation,
and each team decides when each tier applies. The column links the tiers
to the [pace layers](#pace-layers) of the Future pillar: a slower layer means a
higher tier.

Choose the tier before you write the specification. The tier then tells
you which documents from the
[catalogue](#appendix--the-sdd-document-catalogue) you need. A Low change
can need only one changed rule and its scenarios. A High change needs
most of the catalogue.

Agree with your team on one rule: which work is safe to vibe code? The
tiers give you a start for that rule.

### Check the behavior

#### The three tiers of evaluation

A green test suite is not proof of a correct system. Evaluation has three
tiers. A safe regeneration needs all three.

| Tier          | What it checks                                                                        | Does it survive a regeneration?                               |
| ------------- | ------------------------------------------------------------------------------------- | ------------------------------------------------------------- |
| **Ephemeral** | One implementation decision, for example an exact retry count                         | No. Delete it with the implementation.                        |
| **Durable**   | A behavioral contract at a stable boundary, for example a property or an API contract | Yes. This tier is the real codebase.                          |
| **Live**      | Production reality, through monitoring and alerts                                     | Yes. Production telemetry is evidence. A person decides which evidence becomes a rule. |

A check of the Ephemeral tier is an ephemeral test. It can help during one
implementation. It is not an oracle: when a regeneration must pass it, it
is a smell.

[Evaluations Are the Real
Codebase](https://aicoding.leaflet.pub/3mb526js42k26) gives the three
tiers. Most projects have the Ephemeral tier and call the work complete.
Fowler also warns: "Production is not the specification. Production
teaches the specification." ([The Specification Is Not a
Document](https://aicoding.leaflet.pub/3mtgs36dnq22o).)

A test suite cannot perform the Live tier. An operational check simulates
one constraint in a controlled environment. Production monitoring must
then check the same constraint against real traffic.

#### Oracle or ephemeral test

[The Deletion Test](https://aicoding.leaflet.pub/3md5ftetaes2e) calls a
durable check an oracle: "a way to mechanically distinguish 'correct' from
'incorrect' without referring to history".

- An **oracle** checks observable behavior. It survives a rewrite.
- An **ephemeral test** checks how the code does the work. It fails on a
  correct rewrite.

**The language-reimplementation test.** Ask one question about your test
suite: if you rewrote this system in a different language, would the suite
still be valid? If the answer is no, the tests check the wrong boundary.

Signs of an ephemeral test:

- It counts calls to a mock.
- It asserts an exact log message.
- It asserts the order of calls when the order is not part of the contract.
- It reads internal state.

### Define the boundary

#### The two layers of a Context Boundary

A schema states what crosses the boundary. It does not state what the terms
mean inside it. Those are two layers, and a regeneration can keep the first
and lose the second.

| Layer        | The artifact                                               | What a regeneration loses without it           |
| ------------ | ---------------------------------------------------------- | ---------------------------------------------- |
| The contract | OpenAPI, or JSON Schema                                    | A caller cannot check contract drift.          |
| The language | The vocabulary of the unit, with one meaning for each term | The reason that the rules read the way they do |

Domain-Driven Design calls the second layer the **ubiquitous language**. It
calls a unit that holds one such language a **bounded context**. The
[Bounded Context
Canvas](https://github.com/ddd-crew/bounded-context-canvas) gives a ready
template for both layers, and you can copy it as you copy a specification
template.

Name the terms of the unit, and give each term one meaning. The Terms
table of the Specification holds this vocabulary. Two names for
one idea, or one name for two ideas, is the first sign that the boundary
sits in the wrong place.

### Generate the code

#### Pedro's L3 Law — specifications first, code second

[Pedro's L3
Law](https://vistaprint.atlassian.net/wiki/spaces/~694541598/pages/6783795271/Pedro+s+L3+Law+Specifications+First+Code+Second)
states the discipline of Level 3 agentic engineering. At Level 3, an agent
does a multi-step workflow: it plans, writes the code, runs the checks,
and corrects its own defects. The human defines the specification, the
checks, and the boundaries. (Level 3 is a level of agentic engineering.
It is not a level of the Böckeler table above.)

> "Use as many rich, iterative prompts as you need to create the
> specifications. Then with ONE prompt: generate the code and associated
> unit tests."

The law adds: "The implementation prompt and its autonomous loop MUST NOT
introduce new requirements or design decisions."

The rule is not a count of messages. The agent can iterate alone inside
the one prompt. The rule is that the implementation prompt adds no new
requirement and no new design decision.

|                               | Specification work             | Implementation                       |
| ----------------------------- | ------------------------------ | ------------------------------------ |
| Prompts                       | As many as you need            | One controlled implementation prompt |
| Purpose                       | Explore, challenge, and decide | Generate the code from the decisions |
| Output                        | The four primitives            | The code and its unit tests          |

**Prompt-local knowledge.** A prompt that changes code can hold a
decision. If that decision is not in a primitive, it exists only in the
conversation. A later prompt can contradict it, and a regeneration loses
it. Ask about each prompt: "If this prompt disappears, where is the
knowledge it introduced?"

**Two kinds of failure.**

- **Implementation failure:** the primitives are correct, but the code
  does not satisfy them. The agent corrects the code inside the same
  prompt.
- **Specification failure:** the code shows a gap, a contradiction, or an
  error in a primitive. The agent stops and reports it. You fix the
  primitive. The next generation uses the fixed primitive.

The agent must not weaken a test, bypass a boundary, or reinterpret a rule
to make the checks pass.

**Generated unit tests are not the oracle.** The agent writes them with
the code, so they share the assumptions of the code. Your reviewed
Evaluation is the oracle.

The law has two more rules that change daily work.

- **Thin vertical slices.** "Teams MUST refine specifications in thin
  vertical slices instead of designing the whole system upfront." Each
  slice gets its own controlled implementation prompt.
- **Triage the gaps.** Ask the agent to list each gap that
  no test reaches, and the reading that it chose. For each reading, ask:
  "If I throw this implementation away and generate another one, does
  this information have to survive?" Move a reading into a primitive
  only if the answer is yes. Chad Fowler gives this test in
  [When Does a Specification Become a Program?](https://aicoding.leaflet.pub/3msssevtkqc2c)

The law also asks for traceability: "revise and version the
specification before regenerating". In each pull request, record the
version of the specification, the prompt, the agent, and the model. The
result of a regeneration depends on the model, so record it.

The Deletion Test checks that the law held. The full text needs a
Vistaprint login.

### Keep each piece of knowledge in its place

#### The documents of spec-driven development

The toolkits use many file names, but their documents are of few kinds.
Sort each document by how long it lives. The lifetime tells you if the
document must survive the Deletion Test.

| Lifetime          | What the document holds                                                                 | Examples                                                              | After a deletion                      |
| ----------------- | --------------------------------------------------------------------------------------- | --------------------------------------------------------------------- | ------------------------------------- |
| **Always loaded** | The instructions that every session needs: the [memory bank](#the-memory-bank-agentsmd) | `AGENTS.md`, the Spec Kit constitution, the Kiro steering files       | It stays                              |
| **Durable**       | The four primitives                                                                     | The specification, the scenarios, the contracts, the decision records | It stays                              |
| **One change**    | One need, and the plan to deliver it                                                    | A proposal, a delta, a plan, a task list                              | You archive it when the change closes |
| **Transition**    | The path from one decision to the next, for example from ADR 0004 to ADR 0007           | A migration plan: the steps, their order, the rollback                | You delete it when the migration ends. The two decision records stay. |
| **Scaffolding**   | Help for one session or one person                                                      | Research notes, progress notes                                        | You do not copy it                    |

The conversations are evidence for the Provenance, not agent input. They
stay outside the [deletion folder](#glossary).

The first two rows hold the system knowledge. The other rows hold work
in progress.

A decision record is stable. It states one decision, and it does not
depend on the path to it. The transition plan holds the path, and only
until the migration ends.

Watch the third row. A plan or a task list often holds a decision: a
library, a module split, a retry count. When you archive the change, the
decision goes into the archive with it. A decision in a plan is
prompt-local knowledge with a file name. Move it into a primitive before
you archive the change.

A study of practice found the same risk: implementation detail in a
specification "may help agents while making specs prone to decay"
([the studies](#the-studies)).

The [catalogue](#appendix--the-sdd-document-catalogue) at the end of this
sheet lists each document. It gives the question that each document
answers, and the toolkits that use it.

#### The memory bank: AGENTS.md

[AGENTS.md](https://agents.md/) is an open format, "a README for agents".
Most coding agents read it automatically at the start of each session,
for example Codex, Cursor, and OpenCode. GitHub Copilot reads it in some
of its surfaces, for example the CLI and the cloud agent. [Claude
Code](https://code.claude.com/docs/en/memory) reads it when the project
has no `CLAUDE.md`, from v2.1.277 (September 2026). A `CLAUDE.local.md`
file also stops Claude Code from reading `AGENTS.md`. If the project has a `CLAUDE.md`, put the line
`@AGENTS.md` in it.

The agent reads the file in every session, so each line costs tokens and
attention every time. Write only what the agent cannot find alone.

| Include                                                            | Do not include                                                           |
| ------------------------------------------------------------------ | ------------------------------------------------------------------------ |
| The exact commands: install, test, lint, and the fitness functions | An overview of the repository. The agent reads the file tree itself.     |
| The conventions that differ from the defaults of the language      | The content of the README                                                |
| Three lists: **Always**, **Ask first**, and **Never**              | The rules of the system. They belong in the Specification. Link to them. |
| One line that points to `PHOENIX.md`, the map of the primitives    | Text that an agent generated and nobody edited                           |

The three lists tell the agent where to stop.

- **Always:** actions with no question, for example to run the tests
  before it reports a task as done.
- **Ask first:** actions that need a person, for example a new dependency.
- **Never:** hard stops, for example an edit to the oracle during an
  implementation prompt.

Three studies support this shape: ETH Zurich, Vercel, and GitHub.
[The studies](#the-studies) give their results.

A Never line is a request, not a control. V.I.K.I., an agent set at
Vista, states the rule: "Prose states intent; configuration states fact."
An agent permission that denies the edit makes the Never line a fact.

`AGENTS.md` is not a fifth primitive. Each line in it belongs to a
primitive, or to the tooling. A command is tooling. A convention is a
decision, so it needs a decision record. A Never line protects a
primitive.

A controlled implementation prompt can carry the three lists for one
generation. For a repository, write the file. The catalogue has an
[example for Katacombs](#an-agentsmd-for-katacombs).

## Anti-patterns

Watch for these in your work.

| Anti-pattern                   | What you see                                                                | What to do                                                 |
| ------------------------------ | --------------------------------------------------------------------------- | ---------------------------------------------------------- |
| **Throughput without yield**   | The agent generates a large amount of code. No part looks safe to delete.   | Write durable checks before you generate more.             |
| **Mutation in place**          | Someone edits generated code by hand and does not update the specification. | Change the specification, then regenerate. Or record the edit as an approved manual change that will not be regenerated. |
| **Ephemeral-only tests**       | A rewrite in another language would invalidate the whole suite.             | Move the checks to a stable boundary.                      |
| **Framework as architecture**  | The answer to "what is the architecture?" is the name of a framework.       | Name the boundaries, the invariants, and the data owners.  |
| **Uniform regeneration speed** | The data model changes as frequently as the user interface.                 | Assign a pace layer to each part.                          |
| **Conceptual mass**            | The file count grows, and the behavior does not.                            | Apply the concept rent test.                               |
| **Mixed change**               | One step changes the behavior and the architecture together.                | Split it. Change the architecture first, with a fitness function that fails. Then change the behavior. |
| **Provenance debt**            | Nobody can answer "why does this code look like this?"                      | Record the decision, its alternatives, and its constraint. |

## Appendix — specification notations

Two of the [specification forms](#what-a-specification-can-look-like)
have a published notation. This appendix holds the detail, so that the
practices keep to the method.

### The EARS patterns

[EARS](https://alistairmavin.com/ears/) is the Easy Approach to
Requirements Syntax. Alistair Mavin and colleagues at Rolls-Royce
developed it while they analysed the airworthiness regulations of the
control system of a jet engine. Those regulations mixed high-level
objectives, implicit and explicit requirements, lists, and guidelines.
While he simplified them, Mavin saw that the requirements read most easily
when the clauses always appeared in the same order. He published the
notation in 2009. Airbus, Bosch, Dyson, Honeywell, Intel, NASA,
Rolls-Royce, and Siemens use it now.

The generic syntax:

```text
While <optional pre-condition>, when <optional trigger>,
the <system name> shall <system response>
```

The ruleset: zero or many preconditions, zero or one trigger, one system
name, and one or many system responses. A rule needs no trigger, so the
fixed order of the clauses does the work, not a mandatory keyword.

| Pattern            | Keyword       | Example                                                                                                                   |
| ------------------ | ------------- | ------------------------------------------------------------------------------------------------------------------------- |
| Ubiquitous         | none          | The mobile phone shall have a mass of less than XX grams.                                                                 |
| State driven       | `While`       | While there is no card in the ATM, the ATM shall display "insert card to begin".                                          |
| Event driven       | `When`        | When "mute" is selected, the laptop shall suppress all audio output.                                                      |
| Optional feature   | `Where`       | Where the car has a sunroof, the car shall have a sunroof control panel on the driver door.                               |
| Unwanted behaviour | `If ... then` | If an invalid credit card number is entered, then the website shall display "please re-enter credit card details".        |
| Complex            | two or more   | While the aircraft is on ground, when reverse thrust is commanded, the engine control system shall enable reverse thrust. |

One warning on the first row. EARS uses "Ubiquitous" for a rule that holds
with no condition. Domain-Driven Design uses "ubiquitous language" for the
vocabulary of one context. Both names come from their own sources, so this
sheet keeps both. The two senses are unrelated.

EARS reduces the common problems of natural-language requirements. It does
not remove every ambiguity. It needs no tool, and it needs little training,
which is why a team can adopt it in one day.

### The Given-When-Then patterns

Given-When-Then comes from behaviour-driven development. Dan North built
BDD while he taught test-driven development, because the word "test" made
programmers ask the wrong questions. He replaced "test" with "behaviour".
Chris Matts, a business analyst, then set him thinking about business
value, and in 2004 the two of them applied the same thinking to
requirements. Eric Evans had just published Domain-Driven Design, so they
took his idea of a ubiquitous language and built one for analysis. North
published the result in 2006. Gojko Adzic's _Specification by Example_
(2011) comes from the same root: a specification that holds concrete
examples becomes the test suite and the living documentation at the same
time.

Their template for the acceptance criteria of a story:

```text
Given some initial context,
When an event occurs,
Then ensure some outcomes.
```

[Gherkin](https://cucumber.io/docs/gherkin/reference/) is the concrete
syntax that a runner executes. This feature file uses each part of it.
The idea of an annotated feature file comes from Gáspár Nagy and Seb
Rose, [Effective Behavior-Driven
Development](https://www.manning.com/books/effective-behavior-driven-development)
(Manning, early access). The example is our own. It runs with pytest-bdd
8.1.

```gherkin
# language: en
@bag
Feature: The bag
  A player carries items in a bag. The bag has a limit,
  so that a player must choose what to keep.

  Background:
    Given a test world with these items at BRICK LANE:
      | item   | count |
      | PEBBLE | 11    |
    And a new player Ana at BRICK LANE

  Rule: BAG-1 — The bag holds at most 10 items

    # The world of the brief has only 4 items that a player can take.
    @BAG-1
    Scenario: A full bag refuses another item
      Given Ana carries 10 pebbles
      When Ana takes a pebble
      Then the game refuses with BAG_FULL
      And Ana's bag still holds 10 items

    @BAG-1
    Scenario Outline: A take with <count> items in the bag
      Given Ana carries <count> pebbles
      When Ana takes a pebble
      Then the result is <result>

      Examples: Below the limit
        | description    | count | result |
        | an empty bag   | 0     | TAKEN  |
        | one place left | 9     | TAKEN  |

      @edge
      Examples: At the limit
        | description | count | result   |
        | a full bag  | 10    | BAG_FULL |
```

| Element | In the example | What it does in this method |
| --- | --- | --- |
| Language line | `# language: en` | Sets the language of the keywords. Gherkin has keywords in more than 70 languages. |
| `Feature` | `The bag` | One behavior, named as the user sees it. One file holds one feature. |
| Free-text description | The two lines under `Feature` | The reason for the rules. This is the "why" of the Specification. |
| `Background` | The test world, and the new player | The givens that every scenario of the feature shares. Keep it short. |
| Data table | `item` and `count` | Structured data for one step, for example a test world. The step code reads it as rows. |
| `Rule` | `BAG-1 — The bag holds at most 10 items` | One rule of the Specification, with its ID. The scenarios under it illustrate the rule. |
| Comment | `# The world of the brief …` | A note for a person. The runner ignores it. |
| Tag on a scenario | `@BAG-1` | Traces the scenario to its rule ID. Put the rule ID on each scenario, not on the `Rule` line. |
| `Scenario`, or `Example` | `A full bag refuses another item` | One concrete example of the rule. |
| `Given`, `When`, `Then` | The steps | The context, the action, and the observable outcome. |
| `And`, `But` | `And Ana's bag still holds 10 items` | A second step of the same kind. |
| `Scenario Outline` | `A take with <count> items in the bag` | One scenario, run once for each row of each `Examples` table. `<count>` is a placeholder. |
| Named `Examples` blocks | `Below the limit`, `At the limit` | The edges of the rule become visible. |
| Description column | `description` | Says which case each row shows. The runner does not need it. This is specification by example. |
| Tag on an `Examples` block | `@edge` | Selects a part of the suite: `uv run pytest -m edge`. |
| Tag on the feature | `@bag` | Each scenario of the file inherits it. |

pytest-bdd turns each tag into a pytest marker. A tag that is not
registered gives the warning "Unknown pytest.mark.BAG-1". The test still
runs. To remove the warning, register the tags in the `markers` list of
`pyproject.toml`.

Three rules of the form matter more than the keywords.

- **Assert an observable output.** Cucumber states the rule plainly. An
  outcome must be:

  > "something that comes out of the system (report, user interface,
  > message), and not a behaviour deeply buried inside the system (like a
  > record in a database)"

  That rule is the oracle test of this sheet, in other words.

- **Keep three to five steps in a scenario.** More steps cost the scenario
  its power as a specification.
- **Write each example as if the year were 1922.** Cucumber gives this
  test: describe the behaviour with no assumption about the technology or
  the interface. The step definitions hold the implementation detail, and
  the scenario does not.

A scenario serves two primitives at once. A reader reads it as
Specification. A runner executes it as Evaluation.

### The decision record structure

A decision record is the Provenance primitive in file form. Michael Nygard
proposed the practice in
[Documenting architecture decisions](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions).
[MADR](https://adr.github.io/madr/) gives a fuller template. Nygard's
sections are Title, Context, Decision, Status, and Consequences. MADR
adds the decision drivers and the considered options. This sheet uses
four parts, with the rejected alternatives from MADR.

| Part                  | Holds                                                | Why it matters                                                                      |
| --------------------- | ---------------------------------------------------- | ----------------------------------------------------------------------------------- |
| Context               | The force that required a decision                   | A later reader learns what problem existed, not only what was chosen                |
| Decision              | The option taken, in one or two sentences            | The rule that the code must follow                                                  |
| Alternatives rejected | Each option not taken, and the reason                | Stops a later team from re-opening a settled question, or repeating a known mistake |
| Consequences          | What the decision makes easy, and what it makes hard | Names the cost that was accepted on purpose                                         |

Two habits keep the records useful.

- **Write one record for each decision, and number it.** A rule of a
  specification then cites a number, such as `0021`, and a reader follows
  one hop to the reason. Sequential numbers are safe for one person or one
  agent. When branches or agents work in parallel, two of them take the
  same number. The L3 Law then says: "Teams MUST NOT use sequential
  numbers as identifiers." Use a UTC timestamp and a slug, for example
  `ADR-20261009T1530Z-asset-repository-boundary`.
- **Never edit a record to change its decision.** Write a new record, and
  mark the old one superseded. The superseded record is provenance, because
  it holds a position that the team once held for a reason.

The rejected alternatives carry most of the value. A record that gives only
the decision tells a reader what to do. A record that gives the rejected
alternatives tells a reader why every other road was worse, which is the part
that nobody can reconstruct later.

## Appendix — the SDD document catalogue

[The documents of spec-driven development](#the-documents-of-spec-driven-development) sorts the documents
of spec-driven development by lifetime. This appendix lists them. No
project needs all of them. The [risk
tier](#size-the-specification-to-the-risk) tells you which ones a change
needs.

The file names differ between the toolkits. The question that each
document answers stays the same. The last column names one or two places
where you can see the document.

### Always loaded — the memory bank

| Document                    | It answers                                                                                                          | Primitive                                            | Seen in                                                      |
| --------------------------- | ------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------- | ------------------------------------------------------------ |
| `AGENTS.md`, or `CLAUDE.md` | Which commands do I run? Which conventions differ from the defaults? What must I always do, ask first, or never do? | None. It holds tooling and points to the primitives. | [AGENTS.md](https://agents.md/); the BMAD block in `AGENTS.md`   |
| Constitution                | Which principles must every feature obey? Which quality gates apply?                                                | Specification                                        | Spec Kit `constitution.md`                                   |
| Product overview            | What is the product for, and for whom?                                                                              | Specification                                        | Kiro `product.md`; GSD `PROJECT.md`; the BMAD product brief  |
| Stack and structure         | Which technology, which layout, which names?                                                                        | Provenance: each choice is a decision                | Kiro `tech.md` and `structure.md`                            |
| Glossary                    | What does each term mean in this unit?                                                                              | Context Boundary                                     | The Terms table of the Specification; the Bounded Context Canvas |
| Risk tiers and pace         | How much specification does a change need? Where must the agent stop?                                               | Specification                                        | The L3 Law; the pace-layer table in `PHOENIX.md`             |

### Durable — the specification of each capability

| Document                     | It answers                                                                 | Primitive                    | Seen in                                                                     |
| ---------------------------- | -------------------------------------------------------------------------- | ---------------------------- | --------------------------------------------------------------------------- |
| Specification                | Which rules hold, and why? What is out of scope? Which questions are open? | Specification                | Spec Kit `spec.md`; Kiro `requirements.md`; the BMAD PRD; OpenSpec `specs/` |
| Scenarios                    | Which concrete examples show each rule?                                    | Specification and Evaluation | `.feature` files; OpenSpec scenarios                                        |
| Contracts and data model     | What crosses the boundary, and in which shape?                             | Context Boundary             | OpenAPI and JSON Schema; Spec Kit `contracts/` and `data-model.md`          |
| Design                       | Which components, which flows, which error strategy?                       | Specification and Provenance | Kiro `design.md`; the BMAD architecture; C4 diagrams                        |
| Operational constraints      | How fast, how reliable, and at what cost?                                  | Specification                | The `OPS` rules of the Specification; service level objectives            |
| User interface specification | Which screens, and which interactions?                                     | Specification                | The BMAD UX design. Only for a product with a user interface.               |

### One change — archived when the change closes

| Document               | It answers                                                              | Primitive                                        | Seen in                                            |
| ---------------------- | ----------------------------------------------------------------------- | ------------------------------------------------ | -------------------------------------------------- |
| Proposal               | Why this change? What is in scope?                                      | Provenance                                       | OpenSpec `proposal.md`; `/phoenix-kit:change`      |
| Delta                  | Which rules does the change add, modify, remove, or rename?             | Specification, until the archive merges it       | OpenSpec delta specs; `/phoenix-kit:change`        |
| Bugfix specification   | What does the system do now? What must it do? What must stay unchanged? | Specification and Evaluation                     | Kiro `bugfix.md`                                   |
| Plan                   | How do we deliver the change, and in which phases?                      | None. Move each decision in it into a primitive. | Spec Kit `plan.md`; HumanLayer `plan.md`           |
| Task list              | Which steps, in which order, for which requirement?                     | None                                             | Kiro and Spec Kit `tasks.md`; the BMAD sprint plan |
| Transition plan        | How do we move from one decision record to the next, and in which order? | None. The two decision records hold the start and the target. | A migration plan; the expand-contract steps        |
| Requirements checklist | Is each requirement complete, clear, and testable?                      | Evaluation of the Specification                  | Spec Kit checklists; `/phoenix-kit:specify`        |

The third question of the bugfix specification is also useful on legacy
code. The behavior that must stay unchanged is a characterization check.

### Scaffolding — progress and memory

| Document       | It answers                                              | Primitive                                                                | Seen in                                          |
| -------------- | ------------------------------------------------------- | ------------------------------------------------------------------------ | ------------------------------------------------ |
| Research notes | What does the current code do, and where?               | None                                                                     | Spec Kit `research.md`; HumanLayer `research.md` |
| Progress notes | What is done? What is next?                             | None                                                                     | GSD `STATE.md`; BMAD `sprint-status.yaml`        |
| Learnings      | What did the agent or the team learn for the next time? | None, until a person moves a lesson into a primitive or into `AGENTS.md` | Compound Engineering `docs/solutions/`           |
| Agent record   | Which model made the change? Which files did it touch?  | Provenance, if you keep it                                               | The Implementation Notes of a BMAD build spec   |

### Provenance and evaluation

| Document                               | It answers                                                       | Primitive  | Seen in                                                                                           |
| -------------------------------------- | ---------------------------------------------------------------- | ---------- | ------------------------------------------------------------------------------------------------- |
| Decision records                       | Why does the design have this form? Which options did we reject? | Provenance | `/phoenix-kit:decide`; the [decision record structure](#the-decision-record-structure)            |
| Conversations                          | What did the person and the agent say, and why?                  | Provenance, as evidence. Never agent input. Do not copy them into the deletion folder. | A `conversations/` folder; Fowler, [The Conversation Is the Commit](https://aicoding.leaflet.pub/3mhxvpam4z22z) |
| Archive of changes                     | Which changes made the specification what it is?                 | Provenance | OpenSpec `changes/archive/`; `/phoenix-kit:change archive`                                        |
| Approval record                        | Who approved the oracle, and when?                               | Provenance | The `Approved:` line of the rule-to-scenario map                                                  |
| Acceptance tests and fitness functions | What is correct?                                                 | Evaluation | Spec Kit and OpenSpec leave this to you. See [What each toolkit holds](#what-each-toolkit-holds). |
| Rule-to-scenario map                   | Does each rule have a check?                                     | Evaluation | `/phoenix-kit:evaluate`                                                                           |

### An AGENTS.md for Katacombs

This example uses a `spec/`, `tests/`, and `decisions/` layout. It holds
only what an agent cannot find alone.

```markdown
# AGENTS.md — Katacombs

PHOENIX.md maps the primitives. Read it first.

## Commands

- Install: `uv sync`
- All checks: `uv run pytest`
- Fitness functions only: `uv run pytest -m fitness`

## Conventions

- Each rule has an ID, for example `BAG-1`. Cite it in each test and each decision record.
- The tests import only `build(world=None)` from `katacombs/app.py`, and use only HTTP. Keep `build`.

## Always

- Run `uv run pytest` before you report a task as done.

## Ask first

- Add a dependency to `pyproject.toml`.
- Change `spec/openapi.yaml`.

## Never

- Edit `spec/`, `tests/`, or `decisions/` during an implementation prompt.
- Weaken, skip, or delete a failing test.
- Make a design decision that no decision record holds. Stop and report it.
```

## Appendix — the toolkits

The method needs no tool. Plain files are enough for each pillar. Each
tool below gives a structure, and each one holds a part of the
primitives.

### What each toolkit holds

No external toolkit holds all four primitives. Apply the Deletion Test to
the tool as well as to the code: which primitive does it hold, and which
does it leave to you?

| Primitive        | Spec Kit                                                                                | OpenSpec                                                                                         | Phoenix Kit                                                                                        |
| ---------------- | --------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------ | -------------------------------------------------------------------------------------------------- |
| Specification    | One `spec.md` for each feature. Spec-first by default: the core merges no features into one truth. The docs offer a "living spec" model as an option. | One living `spec.md` for each capability. Spec-anchored: the archive merges each change into it. | `specification.md` with one ID per rule, EARS, a why, and an observable result. Spec-anchored.     |
| Evaluation       | Optional test tasks, written first when a team asks for them. `analyze` and `converge` are LLM judgements. | None. `verify` is an LLM judgement.                                                              | Scenarios bound to rule IDs at a stable boundary, fitness functions, and the rule-to-scenario map. |
| Context Boundary | `contracts/` and `data-model.md` under the plan. No glossary file. `analyze` flags terminology drift. | None.                                                                                            | OpenAPI and JSON Schema with `x-rules`, the Terms table, one owner for each dataset.               |
| Provenance       | The constitution, and `research.md` for each feature, with "Alternatives considered". They live as long as the feature folder. | `proposal.md`, and `design.md` with "alternatives considered for each decision". The archive of the change holds them. | One decision record for each decision, with the rejected alternatives and the fitness functions.   |
| Regeneration     | No. `implement` edits the code task by task.                                            | No. `apply` edits the code task by task.                                                         | One controlled implementation prompt. It stops on a specification failure.                              |

Spec Kit and OpenSpec record rejected alternatives, in a file of one
change. The difference is the lifetime: the reason stays with the change,
not with the system. A third tool, Kiro, holds the most Evaluation. It
extracts properties from the EARS requirements and generates
property-based tests that name the requirement that they validate. The
tests are optional, and they run in the IDE only
([Kiro](https://kiro.dev/docs/specs/correctness/)).

The row "Regeneration" does not mean that tasks are wrong. Each tool
splits the work into tasks, and a regeneration also needs a plan inside
the agent. The Phoenix Kit uses the unit, the grain, as its split. When
one prompt cannot regenerate a unit, the grain is too coarse.

Phoenix Kit is a set of eleven agent skills for Claude Code: one for
each step of the checklists, and three readers that explain a system,
review its words, and reconstruct its history. It borrows the parts of
Spec Kit and OpenSpec that fit, and it says so in each file. It is a
starting point, not a framework. Copy it and change it.

The kit comes as its own zip file, `09-phoenix-kit.zip`, with this
sheet. Its README tells you how to start. The kit is optional. A
scenario that the kit writes is not the oracle until you review it. The
generator refuses a map with no `Approved:` line. The commands in the
checklists of the pillars are the optional shortcut for each step, not
the step.

| Command                      | What it does                                                                 | Pillar  |
| ---------------------------- | ---------------------------------------------------------------------------- | ------- |
| `/phoenix-kit:specify`       | Rules with an ID, a source, a why, an observable result; a quality checklist | 1, 2, 3 |
| `/phoenix-kit:decide`        | One decision record, with the rejected alternatives                          | all     |
| `/phoenix-kit:contract`      | The API contract, the data shapes, the vocabulary, the data owners           | 1, 2, 3 |
| `/phoenix-kit:evaluate`      | Given-When-Then scenarios bound to rule IDs; the audit for ephemeral tests   | 1, 2, 3 |
| `/phoenix-kit:generate`      | The one controlled implementation prompt                                     | 1, 2, 3 |
| `/phoenix-kit:deletion-test` | What survives, what is lost, a verdict                                       | all     |
| `/phoenix-kit:assess`        | Legacy: the grain, the scar tissue, the grades, the work plan                | 2       |
| `/phoenix-kit:change`        | A need as a delta of rules; archive it into the specification                | 3       |
| `/phoenix-kit:timeline`      | Legacy: how the system reached its shape, each turn with its confidence      | 2       |
| `/phoenix-kit:explain`       | The behavior of a system, in its own words, from the tests                   | 1, 2, 3 |
| `/phoenix-kit:vocabulary`    | The words that drifted, and one minimal correction for each                  | 1, 2, 3 |

Every skill reads one file, `PHOENIX.md` at the project root. It maps
each primitive to a path and gives the test command. Keep it up to date
as the system evolves: it is the map of where each primitive lives. The
kit ships presets for common layouts.

The kit also ships a checker, `phoenix-kit/scripts/phoenix_check.py`.
It reads the same files and reports a broken form: a rule with no source,
a scenario with no rule, a decision with no rejected alternative, a
change that still holds a placeholder. It needs Python 3.11 or later and
no install. The commands are optional, like the skills: the forms are
plain markdown, and you can check each one by hand.

### The toolkits in brief

| Source                                                                                                                                               | What it gives                                                                                                                                                                                                                                                                                                                                                                                       |
| ---------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [GitHub Spec Kit](https://github.com/github/spec-kit)                                                                                                | An open-source toolkit and a documented method: write a constitution once for each project, then specify, clarify, plan, checklist, tasks, analyze, implement, and converge for each feature. Only specify comes before plan. The other steps are optional quality gates.                                                                                                                                                                 |
| [Kiro](https://kiro.dev)                                                                                                                             | An agentic development environment built on spec-driven development. Its FAQ contrasts a specification with vibe coding: with vibe coding, "it's difficult to keep track of all the decisions that were made along the way".                                                                                                                                                          |
| [OpenSpec](https://github.com/Fission-AI/OpenSpec)                                                                                                   | An open-source toolkit for spec-anchored development: a living specification for each capability, a change folder with a proposal and a delta of requirements, and an archive step that merges the delta into the specification. The change layout of `/phoenix-kit:change` comes from it.                                                                                                          |
| [chad/phoenix](https://github.com/chad/phoenix)                                                                                                      | Chad Fowler's reference implementation of the Phoenix Architecture: a pipeline from a specification to code, with a provenance journal, `phoenix why`, and a deletion test. Alpha. Its own bench records a case where the pipeline passed every gate and still served the wrong routes. Read `bench/FINDINGS.md` for that lesson. The four properties of `/phoenix-kit:deletion-test` come from it. |
| [BMAD Method](https://docs.bmad-method.org/)                                                                                                         | A method with agent roles and a chain of documents: a brief, a PRD, an architecture, and epics. Version 6.11 (August 2026) replaced the story files with one build step, `bmad-build`.                                                                                                                                                                                                                           |
| [GSD](https://github.com/open-gsd/gsd-core)                                                                                                          | A context-engineering framework. It keeps the project, the requirements, the roadmap, and the state in files. It gives each agent and each plan executor a new context.                                                                                                                                                                                                                                                   |
| [AWS AI-DLC](https://github.com/awslabs/aidlc-workflows)                                                                                             | The AI-driven development lifecycle from AWS. Version 2 has five phases: initialization, ideation, inception, construction, and operation. It splits the intent into units of work, and it records each human approval.                                                                                                                                                                                                                                 |
| HumanLayer, [research, plan, implement](https://github.com/humanlayer/advanced-context-engineering-for-coding-agents)                                | A lighter workflow: a research document, then a plan, then the code, each in a new context. In 2025, a person reviewed the research and the plan, because they are shorter than the code. In March 2026, HumanLayer changed this advice: read the code too.                                                                                                                                                                                                                     |
| [Compound Engineering](https://github.com/EveryInc/compound-engineering-plugin)                                                                      | A plugin that writes the learnings of each change to `docs/solutions/`. The next plan reads them.                                                                                                                                                                                                                                                                                                   |
| [AGENTS.md](https://agents.md/)                                                                                                                      | The open format for the memory bank. The Agentic AI Foundation, under the Linux Foundation, maintains it.                                                                                                                                                                                                                                                                                           |

Böckeler's third toolkit, the **Tessl Framework**, is the one that aimed at
spec-as-source. Böckeler describes generated code that carries the marker
`// GENERATED FROM SPEC - DO NOT EDIT`. It was in private beta when she
wrote. Tessl paused the Framework on 14 November 2025, and the company
now sells agent skills. Read the article for the idea, and not the
website. The pause is also evidence for the doubt about spec-as-source.

## Appendix — critiques and evidence

Check the date of each critique and each study, and the date of this
sheet. The tools change fast.

### What to watch for

Birgitta Böckeler's survey, [Understanding Spec-Driven-Development: Kiro,
spec-kit, and Tessl](https://martinfowler.com/articles/exploring-gen-ai/sdd-3-tools.html)
(October 2025), is the most useful critique of the practice. Read it
before you trust a toolkit.

- **The workflow does not scale down.** Böckeler gave Kiro one small bug.
  It produced four user stories and sixteen acceptance criteria, which she
  calls "using a sledgehammer to crack a nut".
- **Review moves from code to markdown, and grows.** Of Spec Kit she
  writes: "I'd rather review code than all these markdown files."
- **Templates do not buy control.** The agent ignored instructions even
  with the files, the templates, and the checklists in place. A larger
  context window does not mean the agent reads all of it.
- **Spec-as-source looks like model-driven development.** MDD generated
  code from models, and it never took hold for business applications.
  Böckeler asks a question, and it covers spec-anchored too: "I wonder if
  spec-as-source, and even spec-anchoring, might end up with the downsides
  of both MDD and LLMs: Inflexibility and non-determinism." The Phoenix
  answer: the Evaluation, not the code, decides if a regenerated version
  is correct. So the code can differ at each generation.
- **The term is diffusing.** She has heard "spec" used as a synonym for
  "detailed prompt".

One of these points has aged, which is itself a lesson. Böckeler wrote in
October 2025. Spec Kit now documents a [shorter path for small
features](https://github.github.io/spec-kit/quickstart.html) next to the
full path and its quality gates. It also treats git branches as optional.
The problem of scale is real, and the tools move. Check the date on any
tool critique, and on this sheet.

### The debates of 2026

The critique continued after October 2025. Check the date of each source.

- **Waterfall or not.** François Zaninotto calls SDD "an echo of the
  Waterfall era" ([Marmelab](https://marmelab.com/blog/2025/11/12/spec-driven-development-waterfall-strikes-back.html)).
  Colin Eberhardt measured one increment of a hobby app. Spec Kit gave
  2,577 lines of markdown and 3.5 hours of review. Without it, the review
  took 24 minutes ([Scott Logic](https://blog.scottlogic.com/2025/11/26/putting-spec-kit-through-its-paces-radical-idea-or-reinvented-waterfall.html)).
  Marc Brooker answers that SDD "isn't about pulling designs *up-front*,
  it's about pulling designs *up*" ([2026](https://brooker.co.za/blog/2026/04/09/waterfall-vs-spec.html)).
  Thin vertical slices are the answer of this sheet.
- **Is a detailed spec just code?** Gabriella Gonzalez says yes
  ([A sufficiently detailed spec is code](https://haskellforall.com/2026/03/a-sufficiently-detailed-spec-is-code)).
  Hillel Wayne answers that a specification is "a *set* of possible
  implementations" ([2026](https://buttondown.com/hillelwayne/archive/a-sufficiently-comprehensive-spec-is-not/)).
  Fowler answers with the Deletion Test: "The format tells us very
  little. The regeneration test tells us much more." ([When Does a
  Specification Become a
  Program?](https://aicoding.leaflet.pub/3msssevtkqc2c))
- **The Thoughtworks Radar.** It puts SDD in Assess: "We may be
  relearning a bitter lesson — that handcrafting detailed rules for AI
  ultimately doesn't scale"
  ([Radar](https://www.thoughtworks.com/radar/techniques/spec-driven-development)).
  It puts "agent instruction bloat" in Caution.
- **Guides and sensors.** Böckeler's 2026 article splits the controls of
  a coding agent into guides (feedforward) and sensors (feedback)
  ([Harness engineering](https://martinfowler.com/articles/harness-engineering.html)).
  The Specification, the Context Boundary, and the Provenance guide the
  agent. The Evaluation is the sensor.
- **Conformance suites.** Simon Willison: "I strongly recommend including
  a language-agnostic conformance suite as part of your project"
  ([2025](https://simonwillison.net/2025/Dec/31/the-year-in-llms/)).
  Drew Breunig published a library with only a specification and
  language-independent tests. An agent built it "in one shot" in each
  language that he tried
  ([whenwords](https://www.dbreunig.com/2026/01/08/a-software-library-with-no-code.html)).
  This is the language-reimplementation test in practice.

### The studies

- **Agarwal and colleagues (2026)** interviewed 21 practitioners and read
  266 repositories
  ([Spec-Driven Development as Prescribed and as Practiced](https://arxiv.org/abs/2608.25202)).
  Teams used SDD selectively, mostly for new features. The authors
  conclude that implementation detail "may help agents while making specs
  prone to decay". The participants compared the specification with the
  code "mainly when changes are completed". The authors give this advice:
  "turn acceptance criteria into tests the agent must pass", and they
  warn of "verification debt" when one agent writes the specification,
  the code, and the tests.
- **Hill (ESEM 2026)** compared 88,052 pull requests in 119 open-source
  repositories
  ([Specification Artifacts in Open-Source Pull Request Workflows Do Not Reduce Defects](https://doi.org/10.4230/LIPIcs.ESEM.2026.84)).
  The pull requests with a specification artifact did not have fewer
  defects. The artifacts showed that a task was complex, not that the
  result was good. Know the limit of that study: most artifacts were
  links to tickets, not the output of an SDD toolkit.
- **ETH Zurich (2026)** tested context files on real tasks. The files did
  not reliably improve task success, and they increased the cost by about
  20%. The agents followed the instructions. A repository overview did
  not help them. The authors give three pieces of advice:

  - Omit generated files.
  - Write only what the README does not hold.
  - Evaluate the file before you adopt it.

  Version 3 of the paper (September 2026) changed some numbers.
  ([Gloaguen and colleagues](https://arxiv.org/abs/2602.11988))
- **Vercel (2026)** compared an index in `AGENTS.md` with a skill that the
  agent loads when it decides to. The index passed 100% of their evals.
  The skill passed 53%, the same result as no documentation. In 56% of the
  cases, the agent did not load the skill. With an explicit instruction to
  use the skill, it passed 79%. Put the knowledge that the agent always
  needs in the file that it always reads. A skill that a person calls by
  name, as each Phoenix Kit command, does not depend on the agent's
  choice.
  ([Vercel](https://vercel.com/blog/agents-md-outperforms-skills-in-our-agent-evals))
- **GitHub (2025)** read more than 2,500 agent files of Copilot custom
  agents. The useful files put the commands early, show examples of good
  output, and use the three lists. The post describes the files. It
  measures no outcome.
  ([GitHub](https://github.blog/ai-and-ml/github-copilot/how-to-write-a-great-agents-md-lessons-from-over-2500-repositories/))

None of this argues for vibe coding. It argues for a specification that
earns its length. Write the rule, the limit, and the reason. Generate the
rest. [Size the specification to the
risk](#size-the-specification-to-the-risk) gives a way to decide that
length.

Spec-driven development and Phoenix Architecture agree that the
specification must outlive the code. They differ on the order: Phoenix
accepts a first version that explores, as the Present pillar explains. Phoenix
also asks what survives when you delete the code, so it adds Evaluation,
Context Boundary, and Provenance next to the Specification.

## Glossary

This glossary defines the main terms of the sheet. Use these terms in your
specifications and your decision records.

| Term                                 | Meaning                                                                                                                                          |
| ------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Spec-driven development**          | Write the specification first. Derive the code from it.                                                                                          |
| **Vibe coding**                      | Generate a solution directly from a prompt, with no specification.                                                                               |
| **Controlled implementation prompt** | The one prompt that tells an agent to generate the code from the primitives. It adds no requirement and no design decision.                      |
| **Corrective prompt**                | A prompt after the implementation prompt that tells the agent what to change in the code. Each one shows a gap in a primitive or in the context. |
| **Prompt-local knowledge**           | A decision that influenced the code but exists only in a prompt or a conversation.                                                               |
| **Memory bank**                      | The instructions and descriptions that every session needs. `AGENTS.md`, a constitution, and steering files are forms of it.                     |
| **Risk tier**                        | The class of a change: low, medium, or high. It sets the minimum specification that the change needs.                                            |
| **Regenerate**                       | Delete an implementation and build it again from the primitives.                                                                                 |
| **Deletion folder**                  | A new folder that holds only the primitives and their tools. The Deletion Test regenerates the code there.                                       |
| **Primitive**                        | One of the four artifacts that a regeneration needs: Specification, Evaluation, Context Boundary, Provenance.                                    |
| **Unit**                             | The part that you assess or regenerate as one piece. Fowler calls it the grain.                                                                  |
| **Ubiquitous language**              | The vocabulary of one unit, with one meaning for each term. The second layer of a Context Boundary.                                              |
| **Bounded context**                  | A unit that holds one ubiquitous language. Domain-Driven Design names it.                                                                        |
| **Oracle**                           | A check that distinguishes correct from incorrect behavior, with no reference to the implementation.                                             |
| **Ephemeral test**                   | A test that is coupled to one implementation, so that a regeneration breaks it. It can help during one implementation. When a regeneration must pass it, it is a test smell. It is not an oracle. |
| **Scar tissue**                      | A lesson from a past problem that exists only in the code.                                                                                       |
| **Fitness function**                 | An automatic check that protects one architecture characteristic.                                                                                |
| **Pace layer**                       | The speed group of a part: fast, medium, or slow.                                                                                                |
| **Core domain**                      | The part that differentiates the business. It earns the heaviest Provenance.                                                                     |
| **Compaction**                       | The active reduction of the concepts that a change must hold.                                                                                    |
| **Entanglement**                     | The state in which the code is the only specification.                                                                                           |

## References

- [Evolutionary Architecture Meets Regenerative Software](https://vistaprint.atlassian.net/wiki/spaces/~694541598/pages/5898699042/Evolutionary+Architecture+Meets+Regenerative+Software)
  (you must have a Vistaprint login)
- [Evolutionary Architecture - A Step-by-Step Approach](https://vistaprint.atlassian.net/wiki/spaces/DSMA/pages/4578476096/Evolutionary+Architecture+-+A+Step-by-Step+Approach)
  (you must have a Vistaprint login)
- [Pedro's L3 Law: Specifications First, Code Second](https://vistaprint.atlassian.net/wiki/spaces/~694541598/pages/6783795271/Pedro+s+L3+Law+Specifications+First+Code+Second)
  (you must have a Vistaprint login)
- [evolutionaryarchitecture.com](https://evolutionaryarchitecture.com/) —
  the book by Neal Ford, Rebecca Parsons, and Patrick Kua.

### Phoenix Architecture — key articles

The Phoenix Architecture series by Chad Fowler is at
[aicoding.leaflet.pub](https://aicoding.leaflet.pub/). The full series has
28 articles (November 2026). This list has the key articles for this sheet.
The body of the sheet links to other articles of the series.

| Article                                        | Link                                         | Why it is important here                                                                       |
| ---------------------------------------------- | -------------------------------------------- | ---------------------------------------------------------------------------------------------- |
| Regenerative Software                          | <https://aicoding.leaflet.pub/3majnyfydzs2y> | The introduction to the series. It states the core idea: code is temporary, intent is durable. |
| The Phoenix Primitives                         | <https://aicoding.leaflet.pub/3mjfruwwuck2d> | It defines Specification, Evaluation, Context Boundary, and Provenance.                        |
| The Deletion Test                              | <https://aicoding.leaflet.pub/3md5ftetaes2e> | The diagnostic question behind each pillar. It defines an oracle.                              |
| The Spec Can Come Later                        | <https://aicoding.leaflet.pub/3mwlzitykzc27> | The order of work is a choice. Explore first, then write the primitives.                       |
| The Regenerative Grain                         | <https://aicoding.leaflet.pub/3mfai4nqg6224> | Five tests to find the correct unit to assess or regenerate.                                   |
| Evaluations Are the Real Codebase              | <https://aicoding.leaflet.pub/3mb526js42k26> | Ephemeral tests and durable evaluations. The language-reimplementation test.                   |
| Pace Layers and AI Integration                 | <https://aicoding.leaflet.pub/3maob46kbz22v> | Fast, medium, and slow layers. Each layer has its own regeneration speed.                      |
| The Implementation Remembers                   | <https://aicoding.leaflet.pub/3mobohx4fq22x> | Scar tissue: team knowledge that exists only in legacy code.                                   |
| Provenance Is the New Version Control          | <https://aicoding.leaflet.pub/3mcbiyal7jc2y> | The intent graph. The reasons behind the code are as important as the code.                    |
| The Conversation Is the Commit                 | <https://aicoding.leaflet.pub/3mhxvpam4z22z> | Provenance again: the reason is the unit of change, not the line of code.                      |
| Production Is a Compiler Input                 | <https://aicoding.leaflet.pub/3mjx4erlboc2l> | The Live tier of the evaluation tiers.                                            |
| Conceptual Mass and the Compaction Discipline  | <https://aicoding.leaflet.pub/3mbhnolyzds2d> | "Keep the system small" in the Future pillar. The concept rent test.                                   |
| Immutable Infrastructure, Immutable Code       | <https://aicoding.leaflet.pub/3mbaguyrjek2g> | Why you regenerate a component instead of editing it in place.                                 |
| Code Was Never the Asset                       | <https://aicoding.leaflet.pub/3maqpvianlc2a> | A system is its behavior, its interfaces, its invariants, and its data.                        |
| The Gradient of Trust                          | <https://aicoding.leaflet.pub/3mb2qb6odxc2d> | Why pure, typed, stateless code is cheaper to verify and safer to replace.                     |
| Relocating Rigor                               | <https://aicoding.leaflet.pub/3mbrvhyye4k2e> | Where the rigor goes when generation becomes cheap.                                            |
| The Industrialization of Regenerative Software | <https://aicoding.leaflet.pub/3men54inhes2d> | Throughput against yield: how much of what you generate survives.                              |
| UI Is a Conservation Layer                     | <https://aicoding.leaflet.pub/3mcxo5ojob22c> | Why you do not regenerate the interface at the speed of the code.                              |
| The Death and Rebirth of Programming           | <https://aicoding.leaflet.pub/3malrv6poy22a> | The wider context of the series.                                                               |

That is 19 of the 28 articles. See the
[full article index](https://aicoding.leaflet.pub/) for the rest.

### Sources by concept

Each row gives one concept of this sheet and the source that defines it.
The day slides cite these same sources, so a question during a session has
one answer.

| Concept                                               | Where in this sheet                   | Source                                                                                                                                                                                                                                                                                                                                                                                                |
| ----------------------------------------------------- | ------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Spec-driven development, current tools                | Appendix, the toolkits                | Birgitta Böckeler, [Understanding Spec-Driven-Development: Kiro, spec-kit, and Tessl](https://martinfowler.com/articles/exploring-gen-ai/sdd-3-tools.html)                                                                                                                                                                                                                                                                                   |
| Specification by example                              | Practices, specification forms        | Gojko Adzic, [Specification by Example](https://gojko.net/books/specification-by-example/); Fowler, [SpecificationByExample](https://martinfowler.com/bliki/SpecificationByExample.html)                                                                                                                                                                                                              |
| Pedro's L3 Law: one controlled implementation prompt  | Practices, generate the code          | Pedro Santos, [Pedro's L3 Law: Specifications First, Code Second](https://vistaprint.atlassian.net/wiki/spaces/~694541598/pages/6783795271/Pedro+s+L3+Law+Specifications+First+Code+Second) (you must have a Vistaprint login)                                                                                                                                                                        |
| Vibe coding                                           | The Present                           | [Vibe coding](https://en.wikipedia.org/wiki/Vibe_coding); Simon Willison, [Not all AI-assisted programming is vibe coding](https://simonwillison.net/2025/Mar/19/vibe-coding/)                                                                                                                                                                                                                        |
| A rule in EARS keywords                               | Practices, specification forms        | Alistair Mavin, [EARS](https://alistairmavin.com/ears/)                                                                                                                                                                                                                                                                                                                                               |
| Given-When-Then, as a runnable specification          | Practices, specification forms        | [Gherkin reference](https://cucumber.io/docs/gherkin/reference/); [pytest-bdd](https://pytest-bdd.readthedocs.io/en/stable/)                                                                                                                                                                                                                                                                          |
| The anatomy of a feature file | Appendix, the Given-When-Then patterns | Gáspár Nagy and Seb Rose, [Effective Behavior-Driven Development](https://www.manning.com/books/effective-behavior-driven-development) (Manning, early access) |
| The documents of spec-driven development, by lifetime | Practices, and the catalogue appendix | Böckeler, [Understanding spec-driven development](https://martinfowler.com/articles/exploring-gen-ai/sdd-3-tools.html); Agarwal and colleagues, [SDD as practiced](https://arxiv.org/abs/2608.25202)                                                                                                                                                                                                  |
| The memory bank, `AGENTS.md`                          | Practices, the memory bank            | [AGENTS.md](https://agents.md/); Gloaguen and colleagues, [Evaluating AGENTS.md](https://arxiv.org/abs/2602.11988); Vercel, [AGENTS.md outperforms skills](https://vercel.com/blog/agents-md-outperforms-skills-in-our-agent-evals); GitHub, [Lessons from over 2,500 repositories](https://github.blog/ai-and-ml/github-copilot/how-to-write-a-great-agents-md-lessons-from-over-2500-repositories/) |
| Risk tiers                                            | Practices, size the specification     | Pedro Santos, [Pedro's L3 Law](https://vistaprint.atlassian.net/wiki/spaces/~694541598/pages/6783795271/Pedro+s+L3+Law+Specifications+First+Code+Second) (you must have a Vistaprint login); Hill, [ESEM 2026](https://doi.org/10.4230/LIPIcs.ESEM.2026.84)                                                                                                                                           |
| A ready specification template                        | Practices, specification forms        | [Spec Kit template](https://github.com/github/spec-kit/blob/main/templates/spec-template.md); [Kiro feature specs](https://kiro.dev/docs/specs/feature-specs/)                                                                                                                                                                                                                                        |
| Oracle                                                | Practices, "Oracle or ephemeral test" | [Test oracle](https://en.wikipedia.org/wiki/Test_oracle)                                                                                                                                                                                                                                                                                                                                              |
| Contract test                                         | Practices, specification forms        | The contract test of this sheet checks each response against the OpenAPI schema. Fowler's [ContractTest](https://martinfowler.com/bliki/ContractTest.html) is a related idea: it checks test doubles against the real service. For contracts between teams, see [consumer-driven contracts](https://martinfowler.com/articles/consumerDrivenContracts.html). |
| Property-based test                                   | Appendix, what each toolkit holds     | [Hypothesis](https://hypothesis.readthedocs.io/en/latest/)                                                                                                                                                                                                                                                                                                                                            |
| A machine-readable contract                           | Practices, specification forms        | [OpenAPI 3.1](https://spec.openapis.org/oas/v3.1.0.html)                                                                                                                                                                                                                                                                                                                                              |
| Characterization check                                | The Past, the checklist               | Michael Feathers, [Characterization testing](https://michaelfeathers.silvrback.com/characterization-testing)                                                                                                                                                                                                                                                                                          |
| Seam                                                  | The Past, why this order              | Fowler, [LegacySeam](https://martinfowler.com/bliki/LegacySeam.html)                                                                                                                                                                                                                                                                                                                                  |
| Decision record                                       | Appendix, the decision record structure | Michael Nygard, [Documenting architecture decisions](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions); [MADR](https://adr.github.io/madr/)                                                                                                                                                                                                                                   |
| Fitness function                                      | The Future                            | Thoughtworks, [Fitness-function-driven development](https://www.thoughtworks.com/insights/articles/fitness-function-driven-development)                                                                                                                                                                                                                                                               |
| An import contract                                    | The Future, fitness function examples | [Import Linter](https://import-linter.readthedocs.io/en/stable/)                                                                                                                                                                                                                                                                                                                                      |
| Cyclomatic complexity of 10 or less                   | The Future, fitness function examples | [Radon](https://radon.readthedocs.io/en/latest/); McCabe, [A Complexity Measure](https://www.mccabe.com/pdf/mccabe-nist235r.pdf)                                                                                                                                                                                                                                                                      |
| Pace layers                                           | The Future                            | Stewart Brand, [Pace Layering](https://web.archive.org/web/20250105153943/https://jods.mitpress.mit.edu/pub/issue3-brand/release/2)                                                                                                                                                                                                                                                                   |
| Evolutionary architecture                             | The Future                            | Neal Ford, Rebecca Parsons, Patrick Kua, [Building Evolutionary Architectures](https://nealford.com/books/buildingevolutionaryarchitectures.html)                                                                                                                                                                                                                                                     |
| The name "Phoenix"                                    | References, key articles (Immutable Infrastructure, Immutable Code) | Fowler, [PhoenixServer](https://martinfowler.com/bliki/PhoenixServer.html); Chad Fowler, [Immutable deployments](http://web.archive.org/web/20201208034457/http://chadfowler.com/2013/06/23/immutable-deployments.html)                                                                                                                                                                               |
| Ports and adapters                                    | The Future, pace layers               | Alistair Cockburn, [Hexagonal architecture](https://alistair.cockburn.us/hexagonal-architecture/)                                                                                                                                                                                                                                                                                                     |

This table holds only the sources that define a concept of this sheet.
