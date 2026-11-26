# Plan — modular-core, the code step

The implementation plan for change `modular-core`, written after the
proposal, the delta, the Evaluation and decision 0012. It changes code
only: no rule, scenario, contract or record changes in this step.

**Done when:**
- the five scenarios that fail today pass: the four of
  `fitness/architecture.feature` (`OPS-2`, `OPS-3`) and "The move port
  refuses a tired player" (`MOVE-5`);
- every other test passes with no edit: the 216 that pass today, the 7
  transcripts, the contract tests;
- the hand-written mutants report as `mutation/mutants.md` lists them.

**Source of the code.** The layout of decision 0012 was first written in
a dropped attempt (commit `58355a2`, dropped for its order of work, not
its design). This step starts from that code and changes it where 0012
differs: the energy gate moves into the move port.

## Steps

Each step keeps the suite runnable. The behavior checks must stay green
after every step, except the five target scenarios, which turn green
along the way.

| # | Step | Files | Check after the step |
| --- | --- | --- | --- |
| 1 | Domain model: add `energy` to `Player`; add `Message`, `Score`, `AccountView`, and the inbound ports for the accounts, the chat, the pickup, the leaderboard and one player | `kata.py` | suite unchanged |
| 2 | Core without I/O: errors, rules, world, state (`GameState`), and the use cases by area. The clock, `random`, the hash and the stores are reached through `Ports` | `core/*.py` | OPS-2 green |
| 3 | Outbound ports: `SaveStore`, `AccountStore`, `HighScoreSink`, `Clock`, `RandomSource`, `PasswordHasher`, bundled in `Ports` | `core/ports.py` | OPS-2 green |
| 4 | Driven adapters: SQLite with the same SQL, the high-score file with the same line, the system clock, `random` and SHA-256, each calling the standard library at each use; the environment variables read at each call | `adapters/*.py` | transcripts, `boundary/`, `harness/` green |
| 5 | The energy gate moves into `MoveUseCase`: the first check after the player is found, at energy 0, before the win check (decision 0011) | `core/moving.py` | MOVE-5 port scenario green; `rest/moving.feature` and transcript `scripted` line 53 unchanged |
| 6 | Composition root: `default_ports()`, `InMemoryGame(ports=None)`, and the names of decision 0008 | `game.py` | `ports/` green |
| 7 | REST adapter: every route calls the use cases; no `game.<attribute>`; no gate | `api.py` | OPS-3 green; `contract/` green |
| 8 | Mutation harness: re-point each mutant to its new file; the energy-gate mutant to `core/moving.py`; `mutmut` reads `core/`, `adapters/`, `api.py` | `tests/fitness/mutation/run_mutants.py`, `pyproject.toml` | 42 applicable, survivors as listed |

Step 8 edits test infrastructure, not a check: the mutants name the code
text, so they follow the code (decision 0012, Consequences).

## Verification

1. `uv run pytest brown_field/tests`: everything passes, the five targets
   included.
2. `uv run pytest brown_field/tests -m architecture`, `-m MOVE-5`: green.
3. `python3 phoenix-kit/scripts/phoenix_check.py trace`: ok.
4. `uv run python brown_field/tests/fitness/mutation/run_mutants.py`: no
   survivor that `mutants.md` does not accept.

## Not in this step

- The approval stamp: a person runs it.
- The archive of the change: the merge of the delta into the
  specification, the update of `PHOENIX.md`'s unit row, and the line
  citations. It comes after the review.
- Every scar and every new feature.
