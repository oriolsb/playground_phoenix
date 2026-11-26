# 0011 — Where the energy gate lives, and at which energy it closes

- **Status:** accepted
- **Date:** 2026-11-26
- **Need:** operational. Day 3 restructures the code behind the ports; the
  move rule must hold the same for every caller. The comment ties the gate
  to the mobile release, so mobile client v1 and the web client are the
  callers with the need.
- **Traces to:** `MOVE-5`, `WEB-MOVE-2`, `MOVE-2`, `ACT-15`.
- **Change:** `modular-core`. Accepted on 2026-11-26 by oriolsb, as
  proposed: the port, at 0. The code moves with that change.
- **Evidence (legacy code only):**
  - `api.py:210-214`, "Added for the mobile release: a tired player cannot
    move." The REST route refuses a move at energy 0 or less, before it
    calls the port.
  - `game.py:616-631`: `MoveUseCase` has no gate. It lowers the energy on
    every move, so through the port the energy goes below 0
    (`ports/ports.feature`, "The move port has no energy gate").
  - `App.tsx:185`, "Do not let a player get stuck at 0.": the web client
    disables every GO button at energy 1 or less (WEB-MOVE-2).
  - The gate comes before the win check. In
    `golden/transcripts/scripted.jsonl`, line 53, a winner at energy 0 who
    moves gets `YOU ARE TOO TIRED TO MOVE…`, not `THE GAME IS OVER…`.
  - In step 7, the one-prompt rewrite moved the gate into `MoveUseCase`.
    Its 320,000 REST requests saw no difference; only the port test failed.

## Context

One rule, three answers:
- **The REST route** refuses at energy 0.
- **The port** never refuses.
- **The web client** stops one move earlier, at 1.

Only `api.py` calls the port today (grep), so no live caller sees the
difference yet. On day 3 the ports become the boundary that the new
structure is built on. A gate that lives in one adapter is lost when a
second adapter appears.

**Two questions.**
1. **Where does the gate live?**
2. **At which energy does it close?**

A player with no food in the bag is stuck in both cases, at 0 or at 1:
the game has no other way to restore energy (ACT-15).

## Decision

**Proposed, for the group to accept or change:**

1. **The gate lives in the move port** (`MoveUseCase`), as the first check
   after the player is found. It runs before the win check, as today.
   - The REST route keeps no gate of its own. It maps the port's
     `NotAllowed` to 405, with the same message.
   - Over REST nothing changes: the status, the message and the order of
     the checks stay the same.
2. **The gate closes at energy 0,** as the server does today.
   - The client's stop at 1 (WEB-MOVE-2) is a client choice that the
     server does not enforce.
   - Whether the client keeps it is a second, smaller decision, for the
     client's owner. This record does not make it.

## Alternatives rejected

| Alternative | Why you rejected it |
| --- | --- |
| Keep the gate in the REST route only (today) | Any second adapter, such as a CLI, a queue or a new API version, would have to copy it or lose it. The step 7 rewrite moved it on its own. The port tier would keep pinning "no gate" as a feature. |
| Gate in both the route and the port | Two copies of one rule. They can drift, as the client and the server already have (0 and 1). |
| Close the gate at energy 1 on the server, to match the client | It changes what every REST client sees: a player at energy 1 is refused today's last move. That breaks `rest/moving.feature` (the 13th move), the mobile client v1, and the transcripts. It is a behavior change, not a restructure, so it needs its own need and its own record. |
| Remove the gate, as the port does today | A player could move forever with energy below 0, so energy and food would stop meaning anything. The comment ties the gate to the mobile release. |

## Consequences

**If the group accepts this proposal:**
- MOVE-5 becomes **accepted** and cites 0011. Its open question is
  answered: the port, at 0.
- **One test flips:** `ports/ports.feature`, "The move port has no energy
  gate", becomes "The move port refuses a tired player". It is a port test,
  and nothing changes over REST.
- **Tests that stay as they are:** the 217 others, the 7 transcripts, the
  Playwright tests, and every Vitest test. A regeneration must put the gate
  in the port; the one-prompt rewrite of step 7 already does.
- **The mutation harness:** the hand-written mutant "energy gate at -1"
  names the text of `api.py`. After the move it reports "not applicable",
  and gets a new line for `game.py`.
- **WEB-MOVE-2 stays contested.** A client at energy 1 still cannot use a
  move that the server allows.

**If the group keeps the gate in the route:**
- MOVE-5 becomes accepted with that answer, and the port test stays.
- The rewrite of step 7 stays unmergeable: it moved the gate.

**The risk either way:** a player with no food is stuck. That is a game
design question, outside this record.

## Fitness functions

| Function | Target | How to run it | Need that it protects |
| --- | --- | --- | --- |
| The move gate answers the same over REST before and after | the 7 transcripts and `rest/moving.feature` pass | `uv run pytest -k "transcripts or moving"` | Mobile client v1 and the web client see no change |
| The port refuses a tired player (after acceptance) | `ports/ports.feature` | `uv run pytest -m MOVE-5` | Every adapter gets the gate |
