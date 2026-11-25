# Expand, migrate, contract

Adapted from the wide-refactor rule of Matt Pocock's `to-tickets` skill
(MIT), and applied to a delta of rules.

Use it when a delta changes what a caller outside the project sees: a
route, a request or a response shape, an error reason or its status, or a
rule that a caller depends on and that the delta removes or renames. One
change that does all of this at once breaks every caller on the day of
the merge.

## Three changes, in order

Split the work into three changes. Each one is a normal change, with its
own proposal, delta, evaluation, decision, approval, generation, and
archive.

| Stage | Change name | Delta | Evaluation |
| --- | --- | --- | --- |
| 1. Expand | `<name>-1-expand` | ADDED: the new form, beside the old one. The old rules stay. | Scenarios for the new form. The old scenarios still pass. |
| 2. Migrate | `<name>-2-migrate` | Often no rule change. The proposal lists each caller and who moves it to the new form. | The old scenarios still pass. One check names or counts the callers still on the old form. |
| 3. Contract | `<name>-3-contract` | REMOVED or MODIFIED: the old form goes, with its migration line. Old values listed. | The scenarios of the old form leave the suite. The new ones stay. |

## Rules

- A stage starts only when the stage before it is archived.
- Each stage has its own decision record. The record of stage 1 names
  the whole plan, and the date or the condition for stage 3.
- Stage 3 needs evidence that no caller uses the old form: a log count,
  a usage metric, or a date that the callers accepted. Put the evidence
  in its decision record.
- Stages 1 and 2 are easy to undo. Stage 3 is not: it needs a person's
  review, as a change in a slow layer does.
- Inside one process, a feature flag can stand in for stage 2. The flag
  selects the old or the new route, and a parity check runs both and
  compares the results. Stage 3 then removes the flag and the old route.

## When not to split

A change that only callers inside the project see, and that one
generation updates in one commit, needs no split. Say so in the
proposal.
