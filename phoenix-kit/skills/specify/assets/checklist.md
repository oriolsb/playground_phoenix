# Specification quality checklist

Adapted from the requirements checklist of GitHub Spec Kit (MIT). Spec Kit
calls this "unit tests for your requirements". A runner cannot find a rule
that you never wrote, or two rules that disagree. This list can.

Mark an item `[x]` only when every rule in scope satisfies it.

## Content

- [ ] No implementation detail: no language, framework, class, method, or
      data structure in a rule
- [ ] Each rule has an ID, a source, a why, and an observable result
- [ ] Each rule states one behavior
- [ ] Each rule is in EARS order: an optional While, When, Where, or
      If ... then clause, the system name, then "shall" (`check rules`)

## Completeness

- [ ] No `[NEEDS CLARIFICATION]` marker remains
- [ ] Each rule is testable at a boundary without reading the code
- [ ] Each operational limit has a number, a unit, and a measurement method
- [ ] Each error path has a rule and a named error reason
- [ ] Each rule says whose data it reads or changes: one actor's, or all
      actors'
- [ ] The assumptions are written down

## Consistency

- [ ] No two rules contradict each other
- [ ] No rule can be read two ways
- [ ] Each term in a rule is in Terms, with one meaning
- [ ] No two terms name one idea, and no term names two ideas
- [ ] No word from the Avoid column of Terms appears in a rule
- [ ] A revised rule has a "Revised" note and a decision record

## Traceability

- [ ] A rule that chose between alternatives cites its decision record
- [ ] A rule from legacy code cites the file and the behavior it records
