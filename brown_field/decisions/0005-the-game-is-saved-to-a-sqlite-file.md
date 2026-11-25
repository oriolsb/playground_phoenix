# 0005 — A player's state is saved to a SQLite file

- **Status:** written after the code
- **Date:** 2026-11-25
- **Need:** operational. Players, after a restart of the server.
- **Traces to:** `SAVE-1`, `STORE-1`, `STORE-2`, `CONF-1`.
- **Change:** None.
- **Evidence (legacy code only):** `game.py:737`, "The SaveGame port.
  INC-3110: a laptop sleep lost every bag." `game.py:754`, "2023: the
  payload also holds the energy and the move count." `game.py:348-350`,
  "The support laptop sets KATACOMBS_DB. Nobody else does."

## Context

The game keeps every player in memory. Incident INC-3110: a sleep of the
laptop that ran the server lost every bag.

## Decision

`POST /player/{playerSid}/save` writes the player's state as a JSON payload
to the table `saves` of the SQLite file named by `KATACOMBS_DB`, else
`katacombs.db`. Accounts live in the table `accounts` of the same file. A
start of the server reads both.

## Alternatives rejected

| Alternative | Why you rejected it |
| --- | --- |
| Save automatically after each command | Not done; the save is a command. |
| Save the world too | Not done (SAVE-2, contested: "nobody wrote down why"). |

## Consequences

The tables and the payload are a contract with every file already written
(`spec/player-state.schema.json`, STORE-1, STORE-2). Open questions for the
group, kept on the rules: the save answer names the server's file path
(SAVE-1); the world is not saved, and a save from before 2023 stops the
start (SAVE-2).

## Fitness functions

| Function | Target | How to run it | Need that it protects |
| --- | --- | --- | --- |
| The golden database written by the legacy code loads | the saved player and the account come back | `uv run pytest brown_field/tests/harness` | Players' saved games |
| The table columns | unchanged | `uv run pytest brown_field/tests -m "STORE-1 or STORE-2"` | Files already written |
