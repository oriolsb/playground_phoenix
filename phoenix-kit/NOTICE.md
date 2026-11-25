# Notices

Phoenix Kit is MIT licensed. It adapts material from the projects below.
Each adapted file names its source.

## GitHub Spec Kit

<https://github.com/github/spec-kit> — MIT License, Copyright GitHub, Inc.

Adapted: the specification quality checklist
(`skills/specify/assets/checklist.md`), the clarification question
table and the `[NEEDS CLARIFICATION]` marker (`skills/specify/SKILL.md`),
and the ambiguity scan taxonomy
(`skills/specify/references/ambiguity-scan.md`).

## OpenSpec

<https://github.com/Fission-AI/OpenSpec> — MIT License, Copyright (c)
2024 OpenSpec Contributors.

Adapted: the change folder and archive layout, the proposal template
(`skills/change/assets/proposal.md`), the delta format with ADDED,
MODIFIED, REMOVED, and RENAMED sections (`skills/change/assets/delta.md`),
the merge rules on archive, and the planning boundary wording
(`skills/change/SKILL.md`).

## chad/phoenix

<https://github.com/chad/phoenix> — MIT License, Copyright (c) Chad
Fowler.

Adapted: the four properties a deletion reveals (boundary clarity,
evaluation coverage, coupling depth, replaceability) and the verdict
replaceable / risky / unverifiable (`skills/deletion-test/SKILL.md`).

## Matt Pocock, skills

<https://github.com/mattpocock/skills> — MIT License, Copyright (c) 2026
Matt Pocock.

Adapted, in the kit's own words: the tautological test
(`skills/evaluate/SKILL.md`, from `tdd`); the review of the code against
its spec in a separate context (`skills/generate/assets/rule-review.md`,
from `code-review`); expand, migrate, contract
(`skills/change/references/expand-contract.md`, from `to-tickets`); the
Avoid column of the glossary (`skills/contract/SKILL.md`, from
`domain-modeling`); one round of questions with a recommended answer,
and facts found by the agent (`skills/specify/SKILL.md`, from
`grilling`); design it twice (`skills/decide/references/design-it-twice.md`,
from `codebase-design`); locality and the dependency kinds
(`skills/assess/SKILL.md`, from `codebase-design`); and the completion
criteria and positive guardrails of every skill (from
`writing-for-agents`).

## Workshop participants

Three skills come from participants in the workshop that the kit was made
for: the behavior overview (`skills/explain`), the vocabulary review
(`skills/vocabulary`), and the legacy decision timeline
(`skills/timeline`). They were written for a general repository, then
adapted to the kit's format, its `PHOENIX.md` paths, and its four
primitives. MIT License, held with the rest of the kit.

## Ideas cited, no text copied

- Chad Fowler, *The Phoenix Architecture* essays,
  <https://aicoding.leaflet.pub/>: the four primitives, the Deletion
  Test, the regenerative grain, scar tissue, pace layers.
- Thomas Bartz-Beielstein, *Deleting Code Without Losing Knowledge*,
  arXiv:2610.17197: the unit record with contract, consumers, pace, and
  risk (`skills/assess`).
- Alistair Mavin, EARS: the rule patterns (`skills/specify`).
- DDD Crew, Bounded Context Canvas (CC BY-SA 4.0): the vocabulary and
  ownership questions (`skills/contract`).
- Pedro Santos, Pedro's L3 Law: the one controlled implementation prompt
  (`skills/generate`).

## MIT License

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the
"Software"), to deal in the Software without restriction, including
without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to permit
persons to whom the Software is furnished to do so, subject to the
following conditions:

The above copyright notice and this permission notice shall be included
in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN
NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE
USE OR OTHER DEALINGS IN THE SOFTWARE.
