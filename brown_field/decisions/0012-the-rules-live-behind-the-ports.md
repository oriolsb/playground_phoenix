# 0012 — The rules live behind the ports, the rest is adapters

- **Status:** proposed
- **Date:** 2026-11-26
- **Need:** operational. The team that maintains game-server needs to add
  features we don't know yet, and each new adapter (a CLI, a queue, a v2
  API) needs the same rules as the REST API.
- **Traces to:** `ENTRY-3`, `ENTRY-4`, `ENTRY-5`, `ENTRY-6`, `ENTRY-7`,
  `WORLD-3`, `MOVE-5`, `WORLD-1`; decisions `0008`, `0011`.
- **Change:** `modular-core`.
- **Evidence (legacy code only):**
  - `api.py:165-197`, `api.py:210-213`: chat, the legacy pickup and the
    energy gate are rules in the routes, with no use case.
  - `api.py:123-124`, `api.py:149-150`: the routes read
    `game.players[sid].energy`, because the domain types of `kata.py`
    have no energy.
  - `game.py:326-335`, `game.py:386-478`, `game.py:742-772`,
    `game.py:799-830`: the use cases open SQLite and the high-score file
    themselves.
  - `game.py:373-384`, `game.py:448-478`, `game.py:742-756`,
    `game.py:806-820`: four copies of the player-state payload.
  - `game.py:135-301` vs `spec/world.json`: the world written twice.
    `game.py:719-734`: the effects of KEY, BREAD and BEER are `if`
    branches on sids and names.

## Context

At the moment (2026-11-26) `game.py` is 830 lines and holds the world,
the rules, the SQLite code and the file writes. `api.py` holds 4 rules
of its own. The features to come are not known yet, so we optimise for
the shape of change we see in the history:

- a new field on the player (energy, in 2023);
- a new route that a second client calls (the mobile pickup);
- new content in the world (the slide, in 2022);
- a new store or a new reader of the data (the marketing file).

Decision 0008 freezes the port tier and the stdlib seams. Decision 0011
proposes the gate in the port. This record builds on both and changes
neither: `brown_field.game` keeps every name of 0008, and
`InMemoryGame()` with no arguments keeps the stdlib seams.

## Decision

**Proposed, for review:**

1. **Driving ports.** Every command has one use case (`ENTRY-3`). The
   REST adapter only maps HTTP to a use case and back (`ENTRY-4`). The
   domain `Player` and `Bag` carry the energy (`ENTRY-5`).
2. **Driven ports.** `SaveStore`, `AccountStore`, `HighScoreSink`,
   `Clock` and `Random` are protocols in `core/ports.py`, passed to
   `InMemoryGame` as optional constructor arguments (`ENTRY-6`,
   `ENTRY-7`). The defaults are the SQLite, JSONL and stdlib adapters of
   today. No DI framework: constructor arguments are enough.
3. **One codec** for the player state, in `core/state.py`, checked
   against `player-state.schema.json`. Saves, accounts and login use it.
4. **The world is data.** `core/world.py` loads `world.json` (`WORLD-3`).
   The item use effects are declared in the file (`WORLD-1`) and run by
   one interpreter in `core/items.py`. The market (`MOVE-6`) and the rat
   (`MOVE-8`) stay in code as named rules: they are behavior with time
   and chance, not content.
5. **Modules by area**, the layout of `proposal.md`: `core/` holds the
   rules and depends on nothing outside the standard library and
   `kata.py`; `adapters/` holds the I/O; `api.py` is the REST adapter;
   `game.py` re-exports the names of 0008.
6. **Four steps, one commit each**, the suite green after each: the
   ports and the gate; the driven ports and the codec; the world as
   data; the split into modules.

## Alternatives rejected

| Alternative | Why you rejected it |
| --- | --- |
| Leave the structure, add features into `game.py` and `api.py` | Each feature keeps touching the rules, the SQL and the routes at once. A second adapter would copy the 4 route rules or lose them. |
| A full rewrite from the specification (generate) | The step 7 rewrite shows it works, but it is all or nothing. Four reviewable steps behind the same suite are cheaper to review and to revert. |
| A DI container, a repository layer over the in-memory dicts, an event bus | Abstractions with one implementation each and no feature asking for them. Constructor arguments and protocols cover the need. |
| Make the world state per player | It changes `ACT-8`, `ACT-11`, `ACT-13`: a behavior change, not a restructure. Its own change when a feature needs it. |
| Move the market and the rat into `world.json` too | It turns two rules with time and chance into a rule language in a data file. Two named rules in `core/movement.py` are easier to read. |
| Replace the stdlib seams with the new ports only | It breaks the harness tests and the seams that 0008 freezes. The defaults keep them. |
| Include the web client in this change | Separate unit, own specification, `WEB-MOVE-2` still contested. Its own change. |

## Consequences

- **Easier:**
  - a new adapter gets every rule by calling the use cases;
  - a new player field is one edit in the codec, one in the schema;
  - new content with a known effect is an edit of `world.json`;
  - a new store is one adapter;
  - tests can run on in-memory stores.
- **Harder:**
  - one more indirection per command (`OPS-1` keeps the budget);
  - the order of exits and items now comes from the file, so a
    reordered `world.json` changes the answers.
- **One port test flips:** `ports/ports.feature`, "The move port has no
  energy gate", becomes "The move port refuses a tired player" (from
  0011).
- **The mutation harness:** each hand-written mutant that names the text
  of `api.py` or `game.py` reports "not applicable" after the move, and
  gets a new line for its new module.
- **What we are afraid of:** step 3. If the loader reads the file in
  another order than the code builds it today, the transcripts break in
  ways that are hard to read. We run them after each step, not only at
  the end.
- **Depends on 0011.** If the group keeps the gate in the route, this
  record drops `MOVE-5` and `ENTRY-4` gets one named exception.

## Fitness functions

| Function | Target | How to run it | Need that it protects |
| --- | --- | --- | --- |
| The REST answers stay the same | the whole suite and the 7 transcripts pass, byte-identical | `uv run pytest brown_field/tests` | Mobile client v1, the web client |
| The REST adapter reads no game state | an AST test: in `api.py`, the game is only passed to use-case constructors | `uv run pytest -m ENTRY-4` | Every adapter gets the rules |
| The rules do no I/O | an AST test: no module in `brown_field/core/` imports `sqlite3`, `fastapi`, `os` or calls `open` | `uv run pytest -m ENTRY-6` | Stores can change |
| One player-state codec | only `core/state.py` builds a payload or reads one; the golden DBs, `old-save-without-energy.db` included, load | `uv run pytest -k "save or account or codec"` | A new player field is one edit |
| The world is data | no item sid literal in `brown_field/core/`; a test world with one more location and item plays through the ports | `uv run pytest -m WORLD-3` | Content features |
| The port tier of 0008 stays | every name of 0008 imports from `brown_field.game`; the port tests pass | `uv run pytest brown_field/tests -m port` | The regeneration, the port tests |
| Modules stay small | no module in `brown_field/core/` over 300 lines | `uv run pytest -m modular-core` | Reviewable changes |
| The Evaluation still bites | the mutation harness kills what it kills today, re-pointed | `uv run python brown_field/tests/fitness/mutation/run_mutants.py` | The suite as oracle |
