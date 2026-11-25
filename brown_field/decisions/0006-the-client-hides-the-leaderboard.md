# 0006 — The web client hides the leaderboard until the season starts

- **Status:** written after the code
- **Date:** 2026-11-25
- **Need:** business. Marketing.
- **Traces to:** `WEB-BOARD-1`.
- **Change:** None.
- **Evidence (legacy code only):** `App.tsx:5`, `SHOW_LEADERBOARD = false;
  // Marketing, 2024: hide until the season starts.` The client shows no
  leaderboard and never calls `GET /leaderboard`.

## Context

The server keeps a leaderboard (BOARD-1). Marketing asked in 2024 to hide
it in the client.

## Decision

A constant in the client hides the leaderboard. The server still serves it.

## Alternatives rejected

| Alternative | Why you rejected it |
| --- | --- |
| Remove the leaderboard from the server | The constant is a temporary switch, not a removal. |

## Consequences

Nobody sees the leaderboard in the web client. Open question for the
group: has the season started, and who flips the switch?

## Fitness functions

| Function | Target | How to run it | Need that it protects |
| --- | --- | --- | --- |
| No leaderboard region, no leaderboard request | none | `npm test` in `brown_field/web` | Marketing's season |
