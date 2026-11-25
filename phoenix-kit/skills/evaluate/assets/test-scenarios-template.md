# Test scenarios — <system>

The rule-to-scenario map. Every rule ID appears once. This file survives
a regeneration: it says what the Evaluation proves, and what it does not.

Command of the canonical run: `uv run pytest`.

Approved:

Do not type this line by hand. After the review, a person runs
`python3 <kit>/scripts/phoenix_check.py approval stamp --by "<who>"`. The
checker fills in the name, the date, and the hash of the suite. The
generator refuses to run without a valid stamp. `/phoenix-kit:evaluate`
clears the line each time it changes the suite.

## How to read the tables

- "Way in": `port` (the published ports), `api` (the REST contract),
  `-` (a check of data or code, with no port).
- "Tier": durable (survives a rewrite), ephemeral (deleted with the
  implementation), live (production monitoring, simulated here).

## Rules and their scenarios

| Rule | Scenario | Way in | Tier | Feature file |
| --- | --- | --- | --- | --- |
| BAG-1 | A full bag refuses another item; over the network, it gives 409 | port, api | durable | `bag.feature` |
| OPS-1 | A command responds in less than 100 ms at p99, over 100 calls, in process | port | live (simulated) | `ops.feature` |

## Fitness functions

| Decision | Function | How to run it | Need that it protects |
| --- | --- | --- | --- |
| 0033 | The domain imports no framework | `uv run pytest -m fitness` | Layer separation |

## Rules with a partial check

What a green suite does not prove. Name the rule, the gap, and why the gap
stays.

| Rule | What the check does not prove | Why |
| --- | --- | --- |
| OPS-1 | The limit under production traffic | The project has no production yet; monitoring must check it |

## Ephemeral tests that the audit found

| Test | Sign | What was done |
| --- | --- | --- |
| | | |
