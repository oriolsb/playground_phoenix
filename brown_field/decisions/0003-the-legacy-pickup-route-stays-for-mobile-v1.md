# 0003 — The legacy pickup route stays for mobile client v1

- **Status:** written after the code
- **Date:** 2026-11-25
- **Need:** business. Players of mobile client v1.
- **Traces to:** `LEGACY-1`, `LEGACY-2`, `WEB-ITEM-4`.
- **Change:** None.
- **Evidence (legacy code only):** `api.py:188-197`, "Mobile client v1
  still calls this route. Do not remove it." `PUT
  /player/{playerSid}/pickup/{itemSid}` moves an item here into the bag
  with no bag limit, no win check and no move count, and answers `OK` even
  when the item is not here. The web client calls it on a double-click
  (`App.tsx:255`).

## Context

The route is older than the bag limit (BAG-3), the win check (ACT-3) and
the move count (ACT-17). An old client still depends on it.

## Decision

The route stays, with today's behavior, for as long as mobile client v1
is in use.

## Alternatives rejected

| Alternative | Why you rejected it |
| --- | --- |
| Remove the route | The comment says mobile v1 still calls it. |
| Add the bag limit and the move count to it | It changes the behavior that mobile v1 sees; nobody asked. |

## Consequences

A player can overfill the bag, and take items without counting moves.
Open question for the group: when is mobile v1 retired, and should the web
client keep its double-click on this route?

## Fitness functions

| Function | Target | How to run it | Need that it protects |
| --- | --- | --- | --- |
| The legacy pickup scenarios | pass | `uv run pytest brown_field/tests -m "LEGACY-1 or LEGACY-2"` | Mobile client v1 |
