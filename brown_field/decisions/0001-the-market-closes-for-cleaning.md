# 0001 — The market closes for cleaning in the last ten minutes of each hour

- **Status:** written after the code
- **Date:** 2026-11-25
- **Need:** business. Facilities, for the cleaning crew's contract.
- **Traces to:** `MOVE-6`, `WEB-MARKET-1`, `WEB-MARKET-2`, `WEB-MARKET-3`.
- **Change:** None.
- **Evidence (legacy code only):** `game.py:316-319`, "Cleaning crew
  contract (2023): the market is closed from minute 50 to minute 59 of
  each hour. Ask facilities before you change this." A move into
  SPITALFIELDS MARKET at minutes 50 to 59 answers 405. The client copies
  the hours into a banner (`App.tsx:184`).

## Context

A cleaning contract of 2023 closes the market for ten minutes every hour.
The brief does not mention it. The rule reads the server's local clock,
so its effect depends on the time zone of the server.

## Decision

The game refuses a move into the market while the server's local time is
in minutes 50 to 59. A refused move costs no energy and no move. The client
shows a banner from the browser's clock and disables no button; only the
server decides.

## Alternatives rejected

| Alternative | Why you rejected it |
| --- | --- |
| Drop the rule | The comment ties it to a contract; facilities must agree first. |
| Read the hours from configuration | Not done in the code; the hours are fixed in two places. |

## Consequences

The win route through the market works for 50 minutes of each hour. Tests
must control the clock (the `clock` fixture, decision 0008). The server's
and the browser's clocks can disagree; the banner is advisory only.

## Fitness functions

| Function | Target | How to run it | Need that it protects |
| --- | --- | --- | --- |
| The market answers at minutes 0, 49, 50 and 59 | 200, 200, 405, 405 | `uv run pytest brown_field/tests -m MOVE-6` | The cleaning contract |
