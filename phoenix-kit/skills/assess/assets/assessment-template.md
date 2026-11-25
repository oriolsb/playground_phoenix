# Assessment — <unit>

Date: <YYYY-MM-DD>. Scaffolding: delete this file when the primitives it
points to exist.

## Unit

- Public contract: <names other code imports, routes served>
- Consumers: <callers, from grep>
- Data owned: <datasets it writes>
- Data shared: <datasets with another writer>
- Pace layer: fast | medium | slow
- Kind: core | supporting | generic
- Dependencies: <each one: in process | local stand-in | remote, owned | external>
- Rules: <rule IDs of the unit; "none yet" until work plan step 2>
- Modules: <each file of the unit's code, as a path from the project root>
- Risk: low | medium | high — <why>

### The five grain tests

| Test | Result | Note |
| --- | --- | --- |
| Comprehension | pass / fail | |
| Isolation | pass / fail | |
| Data ownership | pass / fail | |
| Contracts | pass / fail | |
| Feeling | pass / fail | |

### Locality

- Likely need: <for example, "change the limit">
- Modules it touches: <list>
- Flows that pass through the unit's code: <list, or none>
- Result: one place | several places — <resize, or the seam to plan>

## Scar tissue

| File:line | Behavior | Lesson it probably encodes | Primitive to hold it |
| --- | --- | --- | --- |
| | | | |

## Grades

| Primitive | Grade | Gap |
| --- | --- | --- |
| Specification | | |
| Evaluation | | |
| Context Boundary | | |
| Provenance | | |

## Hybrid component

<None, or: the lines that move data, the lines that hold rules, and the
separation planned.>

## Work plan

| Step | Command | Output |
| --- | --- | --- |
| 1. Freeze the boundary | `/phoenix-kit:contract` | `spec/openapi.yaml`, ownership table |
| 2. Capture current behavior | `/phoenix-kit:specify`, then `/phoenix-kit:evaluate characterization <rule IDs>` | short rules with file:line sources; `tests/` scenarios that pass today |
| 3. Complete the specification | `/phoenix-kit:specify` | the rules of step 2, revised by ID |
| 4. Record the provenance | `/phoenix-kit:decide` | one record per scar |
| 5. Deletion Test | `/phoenix-kit:deletion-test` | verdict, then regenerate |
