# Generate — the reports

Write each report file as the kit's `CONTRACTS.md`, "Reports", says:
`<reports>/generate-<YYYYMMDD-HHMM>.md`, and a short summary in the
conversation. Each report starts with this front matter
(`schemas/README.md`, section 7):

```markdown
---
skill: generate
verdict: passed | stopped | specification-failure
evidence:
  - command: <each check or test command you ran>
    exit: <its exit code>
    summary: <its last line>
---
```

Each claim in the body points to an evidence entry, a file and line, or
a checker result. Mark a claim with no evidence "not verified".

## Specification failure

Write this report and stop. The design choice stays with the person.

```markdown
## Specification failure

**Rule IDs**: <the rules involved>
**Evidence**: <what the code or the test showed, with file and line>
**Kind**: gap | contradiction | impossible
**Options**: <two or three ways to resolve it, with the rule each changes>
```

## Generation stopped

Write this report when step 1, step 3, or step 8 stops.

```markdown
## Generation stopped

**Step**: 1 (approval or baseline) | 3 (scenarios in scope) | 8 (integrity)
**Evidence**: <the command and its output, as it is>
**Checker output**: <the errors of `check approval verify`, `check expected check`, or `check trace`, as they are>
**Missing names**: <for an import break: each module or name that other code imports and the removal deleted>
**What the person does**: <commit the primitives | review and run `check approval stamp` | restore the names | narrow the removal | run `check expected record` | restore or review the changed primitive | add the missing scenario>
```

## Generation report

```markdown
## Generation report

**Unit**: <all, or the unit>
**Approved by**: <who, date, from the map>
**Evaluation**: <passed / failed>, <N> tests, command `<cmd>`
**Iterations**: <N> repair runs
**Files written**: <list>
**Rules with no code path**: <rule IDs the suite did not exercise>
**Rule review**: <each finding: rule ID, kind, and the action; or "none">
**Evaluation gaps**: <rule IDs the review found and the suite did not; the person runs /phoenix-kit:evaluate>
**Trace**: <the result line of `check trace`, and the rules no module cites>
**Primitive integrity**: <"unchanged (git status)" or the output>
```
