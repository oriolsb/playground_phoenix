# Phoenix Kit

Eleven agent skills: eight for the four Phoenix primitives, and three
readers that explain a system, audit its words, and reconstruct its
history. A starting point, not a framework: copy it, run it, change it.

A regenerative system is a system you can delete and rebuild correctly
from its primitives alone. Code is temporary. Intent is durable. The
primitives come from Chad Fowler's [Phoenix
Architecture](https://aicoding.leaflet.pub/) series. The method is in
the cheat sheet, `docs/cheat-sheet.md`, next to the kit in its package.

| Primitive | What it holds | The test |
| --- | --- | --- |
| Specification | The rules, the limits, and the reasons | Can an implementer build from it with no code? |
| Evaluation | Runnable checks each correct implementation passes | Does the suite survive a rewrite in another language? |
| Context Boundary | The contracts and the vocabulary others depend on | Is it machine-readable? One owner per dataset? One meaning per term? |
| Provenance | Why the system has its current form | Can a new team understand it with no access to the first? |

The four primitives come from Fowler's essays. The cheat sheet builds the
tests in the table from several sources. It names the source of each
test.

## Before you start

The kit is optional. Plain files are enough: the method is in the cheat
sheet, and each skill names the section it follows.

When you use `evaluate`, a person reviews the scenarios before they count
as the oracle. The generator refuses a map with no `Approved:` line.

## The skills

| Command | Primitive | What it does | Pillar |
| --- | --- | --- | --- |
| `/phoenix-kit:specify` | Specification | EARS rules with an ID, a source, a why, an observable result; a quality checklist | 1, 2, 3 |
| `/phoenix-kit:decide` | Provenance | One decision record, with rejected alternatives and fitness functions | all |
| `/phoenix-kit:contract` | Context Boundary | OpenAPI and JSON Schema with `x-rules`, the vocabulary, data ownership | 1, 2, 3 |
| `/phoenix-kit:evaluate` | Evaluation | Given-When-Then bound to rule IDs at a stable boundary: they fail before the code, or, in characterization mode for legacy code, pass on the code of today; the audit for ephemeral tests; the rule-to-scenario map | 1, 2, 3 |
| `/phoenix-kit:generate` | the code | The one controlled implementation prompt: needs an approved map, adds no requirement, stops on a specification failure, checks with `git status` that no primitive changed | 1, 3 |
| `/phoenix-kit:deletion-test` | all four | What survives, what is lost, four properties, a verdict | all |
| `/phoenix-kit:assess` | all four | Legacy: the grain, scar tissue, grades, the work plan in the sequence of risk | 2 |
| `/phoenix-kit:change` | all four | Propose a need as a delta of rules; archive it into the living specification | 3 |

Pillar 1 is a green field, 2 is legacy code, 3 is a system that evolves.
The order of work in each pillar is in the cheat sheet. While a change is
open, every skill reads its `delta.md` as part of the Specification.

## The reader skills

The first eight skills write primitives or the code. These three read the
system back and write one document for a person. They change no primitive
and no code.

| Command | Reads | What it does | Pillar |
| --- | --- | --- | --- |
| `/phoenix-kit:timeline` | Specification, decisions, tests, git | Reconstructs how a legacy system reached its shape: the turning points, each with the change, the date, and the reason judged apart | 2 |
| `/phoenix-kit:explain` | Tests, Terms, contracts | One behavior overview for a newcomer, in the words of the Terms table, with each evidence gap visible | 1, 2, 3 |
| `/phoenix-kit:vocabulary` | Tests, Terms, contracts, the overview | The words that drifted between the tests, the contract, and the specification, with one minimal correction for each | 1, 2, 3 |

Run `timeline` before `assess` on legacy code: the story names which
decisions must survive. Run `explain` and `vocabulary` after the
primitives exist, so a new maintainer reads the system and not the code.
A finding of `vocabulary` goes back into the Terms table with
`/phoenix-kit:contract`; a finding of `timeline` becomes a decision
record with `/phoenix-kit:decide`.

## The checker

The skills read and write the same artifacts. `scripts/phoenix_check.py`
turns those agreements into checks: the machine block of `PHOENIX.md`,
the rule blocks, the trace from rules to scenarios to code, the open
changes, the decision records, the old-value search, the units, the
approval, and the expected failures. It needs Python 3.11 or later and
nothing else.

```sh
python3 <kit>/scripts/phoenix_check.py status
python3 <kit>/scripts/phoenix_check.py rules
```

Run it from the project root. `<kit>` is the folder of this plugin, for
example `./phoenix-kit`. `status` also runs the `config` check, so it is
the setup check. The `expected` command needs git: it reads the trailers of a
commit. `generate` and `deletion-test` work outside git, with the
fallbacks that each skill names.

[CONTRACTS.md](CONTRACTS.md) is the one table of what each skill needs
and guarantees. [schemas/README.md](schemas/README.md) is the one copy of
each artifact grammar. An error fails a check; `--strict` also fails on a
warning. Without Python, a skill checks by hand against the grammars.

## Install

The plugin name is `phoenix-kit`, so each command is `/phoenix-kit:<skill>`.

Try it from the folder, with no install:

```sh
claude --plugin-dir ./phoenix-kit
```

To use it in a project, copy the folder into the project, and start the
agent there with `claude --plugin-dir ./phoenix-kit`. The agent then
needs no path outside the project.

Only for a published copy: when a Claude Code plugin marketplace lists
the kit, install it with this line. Replace `<owner>/<repo>` with the
repository of that marketplace.

```
/plugin install phoenix-kit --marketplace <owner>/<repo>
```

The commands are Claude Code commands. The body of each `SKILL.md`
follows the open [Agent Skills](https://agentskills.io) format, so
another agent that reads that format can load the instructions. Three
frontmatter fields (`argument-hint`, `disable-model-invocation`, and the
`$ARGUMENTS` placeholder) are Claude Code extensions that other agents
ignore. To use one skill alone, copy `skills/<name>` to
`.claude/skills/phoenix-<name>/`, set `name: phoenix-<name>` in its
frontmatter, and edit its references to `/phoenix-kit:<other>`. The
plugin install is simpler.

## Set up a project

1. Copy one preset to the project root as `PHOENIX.md`, and edit the
   paths and the machine block. Every skill and the checker read it
   first.
   - [`templates/PHOENIX.md`](templates/PHOENIX.md): the larger layout
     (`spec/` holds all four primitives except `tests/`, code in
     `katacombs/`).
   - [`templates/PHOENIX.workshop.md`](templates/PHOENIX.workshop.md):
     the flat layout (`spec/` holds the specification, the contract, and
     the map; `tests/`; `decisions/`; code in `katacombs/`).

   Fill in the pace-layer table when you know the pace layer of each
   part (the cheat sheet tells how). `change` and `assess` read it.
   While the table is empty, each of them guesses the layers. Fill in the Units
   table when a unit first changes: `generate <unit>`, the removal step
   of `change`, and `deletion-test` read the same row. Add `.phoenix/` to
   `.gitignore`: it holds reports and test results.
2. Check the setup: `python3 <kit>/scripts/phoenix_check.py status`. Fix
   each error before the first skill runs.
3. Green field: `/phoenix-kit:specify`, `/phoenix-kit:contract`,
   `/phoenix-kit:evaluate`, `/phoenix-kit:decide` as you go. When the
   suite is final, review it, approve the map, and commit. Then
   `/phoenix-kit:generate` in a new session, then
   `/phoenix-kit:deletion-test`.
4. Legacy code: `/phoenix-kit:assess`, then its work plan.
5. A new need: `/phoenix-kit:change propose <name> "<the need>"`. It
   prints the hand-off: the order of the skills, from the review to the
   archive and the Deletion Test. The one copy of that order is step 4
   of [`skills/change/SKILL.md`](skills/change/SKILL.md).

`PHOENIX.md` can also hold one table for each phase of a larger change,
so one file holds the paths and the plan.

## What is borrowed

Each piece names its source in the file. [NOTICE.md](NOTICE.md) has the
licenses.

| From | What | Where |
| --- | --- | --- |
| GitHub Spec Kit (MIT) | The requirements checklist, the clarification question table, the ambiguity taxonomy | `specify` |
| OpenSpec (MIT) | The change folder, the proposal, the delta (ADDED / MODIFIED / REMOVED / RENAMED), the merge-on-archive rules, the planning boundary | `change` |
| chad/phoenix (MIT) | The four properties of a deletion and the replaceability verdict | `deletion-test` |
| Matt Pocock's skills (MIT) | The tautological test, the review against the spec in a new context, expand–contract, the Avoid column, the question round, design it twice, locality, the step completion criteria | `evaluate`, `generate`, `change`, `contract`, `specify`, `decide`, `assess`, all |
| spotregen (arXiv 2610.17197) | The unit card: contract, consumers, pace, risk | `assess` (idea only) |
| Workshop participants | The behavior overview, the vocabulary review, and the legacy decision timeline | `explain`, `vocabulary`, `timeline` |
| The workshop that the kit was made for | The rule format, the decision record, the three tiers, the grain tests, the sequence of risk | all |

## What it is not

It is not a regeneration engine: `/phoenix-kit:generate` is a prompt,
and the approved Evaluation is the judge. It is not a task tracker: there
is no `tasks.md`, because the code is regenerated, not worked through.
It holds no state outside the project's own `spec/`, `tests/`, and
`decisions/`.

## Change the kit

[MAINTAINERS.md](MAINTAINERS.md) tells you how to add a skill, how to
validate the kit, and the known exceptions.
