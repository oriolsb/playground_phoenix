# 0004 — A repeated take succeeds, and the client sends it again when slow

- **Status:** written after the code
- **Date:** 2026-11-25
- **Need:** business. Players on a slow network.
- **Traces to:** `ACT-5`, `WEB-ITEM-2`.
- **Change:** None.
- **Evidence (legacy code only):** `game.py:676-680`, "Do not remove.
  INC-2231: the mobile client sends TAKE again when the network is slow,
  and players saw an error." `api.ts:93-102`, "Slow network on the train.
  Do not remove." The client sends the take again after 800 ms without an
  answer; the server answers `TAKEN.` to a take of an item already in the
  bag.

## Context

Incident INC-2231: on a slow network, a second take reached the server
after the first and answered an error.

## Decision

A take of an item already in the bag answers `TAKEN.` and changes
nothing. The web client sends the take again after 800 ms without an
answer, and shows the second answer.

## Alternatives rejected

| Alternative | Why you rejected it |
| --- | --- |
| Refuse the repeat with an error | That was the incident. |
| Deduplicate with a request id | Not done; needs a change of the contract. |

## Consequences

A repeated take still counts a move (ACT-17, contested), so a slow
network can raise a player's move count.

## Fitness functions

| Function | Target | How to run it | Need that it protects |
| --- | --- | --- | --- |
| The repeated take scenario | `TAKEN.`, bag unchanged | `uv run pytest brown_field/tests -m ACT-5` | Players on a slow network |
| The client's double take | 2 requests after 800 ms | `npm test` in `brown_field/web` | Players on a slow network |
