# 0002 — The high-score file keeps its format for the marketing job

- **Status:** written after the code
- **Date:** 2026-11-25
- **Need:** business. Marketing, whose nightly job reads the file.
- **Traces to:** `WIN-3`, `CONF-2`.
- **Change:** None.
- **Evidence (legacy code only):** `game.py:326-335`, "The marketing
  leaderboard reads this file every night. Keep the format." Each win
  appends one JSON line `{name, score, at}` to `KATACOMBS_HIGHSCORES`,
  else `highscores.jsonl`.

## Context

A consumer outside this repository reads the file. No test here can see
it, so a rewrite could break it without any failure.

## Decision

Each win appends exactly one line with the keys `name`, `score` and `at`
(UTC, to the second, offset `+00:00`), to the file the variable names, else
`highscores.jsonl` in the working directory. The file is only appended to.

## Alternatives rejected

| Alternative | Why you rejected it |
| --- | --- |
| Serve the scores to marketing from `GET /leaderboard` | The in-memory leaderboard is empty after a restart; the job reads a file. |
| Change the line format | The comment forbids it without marketing. |

## Consequences

The format is a contract with an outside team, now in
`spec/highscore-line.schema.json`. A change of the format needs marketing.

## Fitness functions

| Function | Target | How to run it | Need that it protects |
| --- | --- | --- | --- |
| A win's line matches `highscore-line.schema.json` | valid | `uv run pytest brown_field/tests/contract` | The marketing job |
| A win appends to the legacy file | earlier lines kept | `uv run pytest brown_field/tests/harness` | The marketing job |
