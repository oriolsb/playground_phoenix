# Rule review — step 7 of `generate`

The suite passed. That proves only what the suite checks. A separate
reader compares the code with the rules, in a new context, so that the
generator's own reasoning does not steer it.

Adapted from the "Spec" axis of Matt Pocock's `code-review` skill (MIT).

## What the subagent gets

- The text of each rule in scope, open deltas included. A delta rule
  replaces the rule with the same ID.
- The decision records that those rules cite.
- The diff command for this run, for example
  `git diff <commit before step 4> -- <code path>`, or the code path
  when the whole system is new.
- The brief below.

It gets no conversation, no test files, and no reasoning of the
generator. A reviewer that reads the tests checks the tests, not the
rules.

## The brief

> You review generated code against its rules. For each rule ID below,
> find the code that implements it. Report three kinds of finding, and
> quote the rule line for each one:
>
> 1. **Missing**: a rule, or a part of a rule, with no code path.
> 2. **Wrong**: code that disagrees with the rule, its observable result,
>    or a decision it cites. Name an input that shows the difference.
>    Check the scope of each rule: whose data it counts, which state it
>    reads, and the order of its error reasons.
> 3. **Not asked for**: behavior in the diff that no rule, decision, or
>    contract asks for.
>
> Write "none" for a kind with no finding. Report only these three kinds.
> Use at most 400 words.

## What the generator does with each finding

| Finding | Action |
| --- | --- |
| Missing or wrong, and the rule is clear | Fix the code. Run the suite again. Report the finding as an Evaluation gap with its rule ID: the suite passed without the fix, so a scenario is missing. The person runs `/phoenix-kit:evaluate` for it. |
| Missing or wrong, and the rule is not clear | A specification failure: step 6. |
| Not asked for | Remove the behavior and run the suite again. If the code needs the behavior, it is a specification failure: step 6. |
| A finding you disagree with | Keep the code. Report the finding and your reason, with the rule line. The person decides. |

The tests stay as they are in every case. Put each finding and its
action in the "Rule review" line of the generation report.
