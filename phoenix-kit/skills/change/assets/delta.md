# Delta — <change name>

Format adapted from the OpenSpec delta spec (MIT). Each section is
optional. Rules use the format of the specification. On archive, the
delta merges into the specification and this file moves to the archive.

## ADDED Rules

#### PREFIX-N — <title>

- Source: <this change, and the need>.
- Rule: When <trigger>, the system shall <response>.
- Why: <reason>.
- Observable result: <what a test sees>.

## MODIFIED Rules

<!-- Copy the WHOLE existing rule block, then edit it. A partial copy
     loses detail at archive time. -->

#### PREFIX-N — <title>

- Source: <original source>, revised by this change.
- Rule: <the full new rule>.
- Why: <the full reason, updated>.
- Observable result: <the full result, updated>.
- Revised: <YYYY-MM-DD>. <What changed, and the decision NNNN.>

## REMOVED Rules

#### PREFIX-N — <title>

- Reason: <why the rule goes>.
- Migration: <what a caller does instead>.

## RENAMED Rules

- FROM: `OLD-ID`
- TO: `NEW-ID`

## Other changes to the specification

<!-- Terms rows, the data ownership table, and other sections that are
     not rules. Each entry names its heading and gives the full new text.
     /phoenix-kit:contract and /phoenix-kit:specify write here while the
     change is open. -->

### <heading, for example "Terms: Bag limit">

<the full new row or section>

<!-- A contract file is edited in place, not here. Name each edit, so
     the review and the archive see it. -->

### Contract: <file, for example spec/openapi.yaml>

- <the operation or schema that changed, and its rule IDs>

## Old values

<!-- Each literal that the change replaces. One literal per row, in
     backticks: a change that replaces three literals writes three rows.
     Put a note in a sentence above the table, never in a cell. On
     archive, the change skill searches every primitive path for each
     literal and reports every hit. -->

| Rule ID | Old value | New value |
| --- | --- | --- |
| PREFIX-N | `<old literal, for example 10>` | `<new literal>` |

## Kept old values

<!-- Optional. Fill it in at archive time only. One row for each hit of
     `check oldvalues --archive` that stays, with the reason. A hit in a
     decision record needs no row. Delete this section if no hit stays. -->

| File | Old value | Reason |
| --- | --- | --- |

## Unchanged

<!-- Optional. The rule IDs next to this change whose behaviour must stay
     as it is: each one needs a scenario that passes before and after. -->

- `PREFIX-N`: <why it is close to the change>
