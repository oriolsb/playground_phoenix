# Archive — the merge rules and the old-value search

The merge rules come from OpenSpec (MIT). The old-value search is from
this kit: an end-to-end run found an archive that reported an edit
it did not make.

## Merge

Apply the delta to the specification, in place:

- ADDED: append each rule under its prefix section. A rule that already
  exists with that ID is a MODIFIED in disguise: treat it so.
- MODIFIED: replace the whole rule block. The delta's block already
  carries the "Revised" line; fill in its date and decision number. Do
  not add a second one.
- REMOVED: delete the rule block. Add one line under a "Removed rules"
  table: ID, reason, migration, decision.
- RENAMED: rename the heading and every reference to the old ID in the
  specification, the contracts, the tests, and the map.
- Other changes: replace or add each named row or section. A
  `### Contract: <file>` entry is already in that file, because
  `/phoenix-kit:contract` edits the contracts in place. Do not apply it
  again. Check that the file holds the change, and name the file in the
  report.
- Old values: this table stays in the archived delta, outside the
  specification.

Leave every rule the delta does not name exactly as it is.

## Old-value search

Run `check oldvalues --change <name> --json` (the kit's checker, see
`CONTRACTS.md`). It searches every primitive path of `PHOENIX.md`, except
the changes folder, for each row of the "Old values" table, and gives the
scope of each hit. Each hit is a warning. Before the merge, keep this
output.

After the merge, run it with `--archive`. Then each hit is an error,
except a hit in a decision record, and a hit that the delta's "Kept old
values" table names. For each hit:

| Scope | Action |
| --- | --- |
| `specification`, `detail` | Change the hit if it states the replaced value. If it names a different thing, keep it, with a reason. |
| `decision` | Leave it. A record is not rewritten. It stays a warning. |
| `contract` | Stop the archive. `/phoenix-kit:contract` owns the contracts: it fixes the hit, or the hit is kept with a reason. |
| `tests`, `map` | Stop the archive. `/phoenix-kit:evaluate` owns the tests and the map: it fixes the hit, or the hit is kept with a reason. |
| `other` | Fix the hit, or keep it with a reason. |

To keep a hit, add one row to the "Kept old values" table of the delta:
the file, the old value, and the reason. The row covers each hit of that
value in that file.

```markdown
## Kept old values

| File | Old value | Reason |
| --- | --- | --- |
| `spec/specification.md` | `10 items` | HELP-2 names the size of the help page, not the bag. |
```

A short value such as `10` hits many lines. Put the value with its
context in the Old values table instead, for example `LIMIT = 10` and
`10 items`, one row each.

Run the check with `--archive` again after the edits, until it passes.
Put the first output and the last output in the report. Report a file as updated only
when the second output shows it: that output is the evidence.
