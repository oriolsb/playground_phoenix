# Rule template

Each rule is one heading in the specification, under its prefix section.
The EARS patterns are in the second table.

```markdown
#### PREFIX-N — <Short title, the behavior in five to eight words>

- Source: <brief | user | legacy code (file:line) | decision NNNN>.
- Rule: When <trigger>, <the system> shall <response>.
- Why: <the reason the rule exists>.
- Observable result: <what a test sees at the boundary>.
```

A revised rule adds one line:

```markdown
- Revised: <YYYY-MM-DD>. <What changed, and the decision NNNN that changed it.>
```

## The EARS patterns

| Pattern | Form | Use it for |
| --- | --- | --- |
| Ubiquitous | The system shall <response>. | A rule that always holds. |
| Event-driven | When <trigger>, the system shall <response>. | A rule that a command or an event starts. |
| State-driven | While <state>, the system shall <response>. | A rule that holds only in one state. |
| Unwanted behavior | If <condition>, then the system shall <response>. | An error, a refusal, a limit. |
| Optional feature | Where <feature>, the system shall <response>. | A rule that holds only with a feature on. |

## Example

```markdown
#### BAG-1 — The bag holds at most 10 items

- Source: brief ("max 10 in bag", "Bag limit: 10 items").
- Rule: If a player takes an item while the bag holds 10 items, then the
  system shall refuse the command and change nothing.
- Why: the limit forces a choice about what to carry.
- Observable result: the error reason `BAG_FULL`. The bag still holds 10
  items. The item stays in the location.
```

## An operational limit is a rule

```markdown
#### OPS-1 — A command responds fast

- Source: operations.
- Rule: When a client sends a command, the system shall respond in less
  than 100 ms at p99, over 100 calls, measured in process.
- Why: a player waits for each response.
- Observable result: a test runs 100 commands in process and reports the
  99th percentile.
```
