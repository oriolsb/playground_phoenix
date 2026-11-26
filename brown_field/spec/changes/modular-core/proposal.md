# Proposal — modular-core

Structure adapted from the OpenSpec proposal template (MIT).

## Need

- Who: Product.
- Why: new features are coming: more accounts, more chat, and a
  subscription whose type is not known yet. Today one file,
  `brown_field/game.py`, holds the world, the rules, the state, the use
  cases and every kind of I/O, and `brown_field/api.py` holds three rules
  of its own. Each new feature would land in the same two files, and no
  part can change, or be tested, without the others. Product wants the
  current architecture more modular, so that each new feature has its own
  place and the existing rules stay as they are.
- Kind: business. The architecture step serves the features that follow;
  it changes no behavior on its own (cheat sheet, "Evolve a system").
- Measurable as: `OPS-2` (the game rules do no I/O) and `OPS-3` (the REST
  adapter holds no game rule). Each one is a fitness function that fails
  today. Source: this change, and Product's need of 2026-11-26.

## What changes

- **New:** two operational rules, `OPS-2` and `OPS-3`, and their fitness
  functions. They state the target of the design, not a behavior.
- **Changed:** through the move port only, a player with no energy is
  now refused (`MOVE-5`, decision 0011). Over REST, nothing that a caller
  sees changes. Every route, status, message,
  file and time stamp stays as it is. The code moves behind outbound
  ports (for the database file, the high-score file, the clock, the
  random numbers and the password hash), in a later step, after the
  review and the decision.
- **Removed:** nothing.

**What does not change, and guards the change:**

- the 74 rules of the specification, their scenarios, the 7 recorded
  transcripts and the contracts (`openapi.yaml` and the three schemas);
- the seams of decision 0008: `create_app`, `app`, and the port tier
  (`InMemoryGame`, the 12 `*UseCase` classes and the 5 error types in
  `brown_field.game`); the clock and the random numbers still come from
  the standard library at each call, so time-machine and a patched
  `random` keep working;
- the data at rest: the SQLite tables and the high-score line;
- the known scars: the unsalted password digest (`STORE-3`), the path in the save
  answer (`SAVE-1`), a chat line counting as a move (`CHAT-3`), the
  pickup skipping the take rules (`LEGACY-1`). Each one is a behavior
  change, with its own need and its own record.

**Out of scope:** the subscription itself, any login or token, and a new
password hash. Each one is a behavior step that comes after this one.

## Answers of the review (2026-11-26, oriolsb)

1. **The energy gate (`MOVE-5`).** Decision 0011 is accepted: the gate
   moves into the move use case, at energy 0. `MOVE-5` is modified by this
   change. Over REST nothing changes; through the move port, a tired
   player is now refused.
2. **Where the core starts.** `brown_field/core/` holds the rules and the
   use cases; `brown_field/adapters/` holds the I/O; `game.py` wires them,
   so the port tier of decision 0008 keeps its names.

## Rules

- Added: `OPS-2`, `OPS-3`.
- Modified: `MOVE-5` (decision 0011: the gate moves into the move port).
- Removed: none.
- Renamed: none.

## Impact

No contract changes, and no consumer sees a difference: the web client,
mobile client v1, the marketing job and the support laptop use the same
routes and files.

| Part | Pace layer | Blast radius | Review needed |
| --- | --- | --- | --- |
| The REST adapter (`api.py`) | fast | every client, if an answer changed; the transcripts and the contract tests guard it | no, beyond this proposal |
| The game rules and use cases (`game.py`, to be split) | medium | every rule; the 218 tests guard it | done: 0011 accepted |
| The outbound ports (new) | slow | every adapter written from now on, the subscription's included | **yes** |
| The port tier seam (decision 0008) | slow | the port tests and every regeneration | **yes**: the names stay |
| The data at rest (`katacombs.db`, `highscores.jsonl`) | slow | the marketing job, the support laptop | no: not touched |
| The contracts (`openapi.yaml`, the schemas) | slow | every client | no: not touched |

## Decision record

<!-- Filled on archive: the NNNN whose Change field names this change. -->
