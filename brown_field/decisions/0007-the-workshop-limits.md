# 0007 — The limits and checks that the workshop sets

- **Status:** accepted
- **Date:** 2026-11-25
- **Need:** business. The workshop, for players: instant feedback and a
  game that opens on a slow network.
- **Traces to:** `OPS-1`, `WEB-OPS-1`, `WEB-E2E-1`.
- **Change:** None.
- **Evidence (legacy code only):** `brown_field/README.md:391-393` (OPS-1),
  `brown_field/README.md:465` (WEB-OPS-1), and the "Web client, in
  parallel" section (one browser test to a win). Today's code meets them:
  a p99 of about 1.5 to 3 ms, and a bundle of about 70 KB gzipped.

## Context

These are requirements of the exercise, not behaviors found in the code.

## Decision

Each command responds in less than 100 ms at the 99th percentile over 100
calls, in process. The production bundle is at most 250 KB gzipped. One
browser test plays to a win against the real server.

## Alternatives rejected

| Alternative | Why you rejected it |
| --- | --- |
| Measure latency over the network | The workshop states "in process"; the network is not the game's work. |

## Consequences

Production monitoring must check OPS-1 against real traffic: the test
simulates the live tier only.

## Fitness functions

| Function | Target | How to run it | Need that it protects |
| --- | --- | --- | --- |
| 100 mixed commands in process | p99 below 100 ms | `uv run pytest brown_field/tests -m ops` | Instant feedback |
| A production build, gzipped | at most 250 KB | `npm test` in `brown_field/web` | A slow network |
| A win in a real browser | score 55 | `npx playwright test` in `brown_field/web` | The client and server together |
