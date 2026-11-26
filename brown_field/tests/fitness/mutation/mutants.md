# Mutants of the game-server

The mutation fitness function (decision 0010). `run_mutants.py` breaks the
legacy code one rule at a time, in a copy, and runs the suite. This table
holds the result of each mutant, and the reason for each mutant that
survives. A survivor with no row here fails the run.

Last run: 2026-11-25, on `brown_field/game.py` and `brown_field/api.py` of
the original code.

| Mutant | Rule | Result | Reason |
| --- | --- | --- | --- |
| bag slots 8 -> 9 | BAG-3 | killed | |
| items per slot 3 -> 2 | BAG-3 | killed | |
| slot count: ceil -> floor + 1 | BAG-3 | killed | |
| name max 50 -> 49 | PLAYER-3 | killed | |
| max players 20 -> 21 | PLAYER-5 | killed | |
| no reserved names | PLAYER-4 | killed | |
| start energy 12 -> 13 | PLAYER-1 | killed | |
| max energy 20 -> 21 | ACT-15 | killed | |
| rat chance 0.2 -> 0.3 | MOVE-8 | killed | |
| rat chance 0.2 -> 0.1 | MOVE-8 | killed | |
| bread energy 5 -> 4 | ACT-15 | killed | |
| beer energy 3 -> 4 | ACT-15 | killed | |
| market closes at 51 | MOVE-6 | killed | |
| market reads UTC | MOVE-6 | killed | |
| default database file name | CONF-1 | killed | |
| password hash sha256 -> sha3 | STORE-2 | killed | |
| old save at an unknown location loads | SAVE-2 | killed | |
| description keeps a trailing space | WORLD-1 | killed | |
| player name not stripped | PLAYER-2 | killed | |
| player limit off by one | PLAYER-5 | killed | |
| rat takes value < 10 | MOVE-8 | killed | |
| rat leaves the item in the cellar | MOVE-8 | killed | |
| email needs exactly one @ | ACCOUNT-2 | killed | |
| login restores a snapshot at an unknown location | ACCOUNT-4 | killed | |
| login restore ignores the player limit | ACCOUNT-4 | killed | |
| gold on every visit | GOLD-1 | killed | |
| bag-full message | BAG-3 | killed | |
| key unlocks anywhere | ACT-14 | killed | |
| nothing-happens message | ACT-16 | killed | |
| no energy cap | ACT-15 | killed | |
| closing the manhole keeps the exit | ACT-13 | killed | |
| high-score time with microseconds | WIN-3 | killed | |
| sid collision check removed | PLAYER-1 | survives | Not observable: a new sid is random in a space of about 10^26, so a repeat never happens in a test. The rule (PLAYER-1) states that a sid is unique. |
| world check disabled | WORLD-2 | killed | |
| a quit finds the first account with a player | ACCOUNT-6 | killed | |
| saves load in sid order | SAVE-2 | killed | |
| chat does not count a move | CHAT-3 | killed | |
| chat shows every location | CHAT-2 | killed | |
| energy gate at -1 | MOVE-5 | killed | |
| legacy pickup counts a move | LEGACY-1 | killed | |
| unknown error status 500 -> 400 | API-2 | survives | Not reachable: no code path raises a game error outside the four reasons. The 500 status is not in `x-status-by-reason`. |
| malformed request 400 -> 422 | API-1 | killed | |

## mutmut: generated mutants

`mutmut` mutates any implementation, so it also runs on a regenerated one.
Run it from the package root (about 3 minutes; it writes `mutants/`, which
git ignores):

```sh
uv run mutmut run --max-children 8
uv run mutmut results
```

Its configuration is `[tool.mutmut]` in `pyproject.toml`. It skips two
test files:
- `boundary/test_startup.py` starts the server in a subprocess, outside
  mutmut's trampolines;
- `fitness/test_invariants.py` is random, so mutmut's timings vary.

The hand-written mutants above cover both.

Last run, 2026-11-25, on the original code, from the package root: **1,084
mutants, 1,030 killed, 3 timeouts** (each one makes `new_sid` loop forever,
so it counts as caught), **51 survived**. A run in a temporary copy of the
package killed 14 more: the test-to-mutant mapping of mutmut depends on the
folder. The run from the package root is the reference. Each survivor has
its reason:

| Survivors | Where | Reason |
| --- | --- | --- |
| 12 | `SaveGameUseCase`, `write_account`, `load_accounts`, `load_saves` | Equivalent: an SQL keyword or name in another case. SQLite reads them the same. |
| 1 | `password_hash` | Equivalent: `"UTF-8"` and `"utf-8"` name the same codec. |
| 7 | `new_sid` | Not observable: a bound moved by one (for example `randint(1, …)`), or `and` → `or` in the collision check. A sid keeps its form in all but about 1 in 10^6 draws, and a collision never happens in a test. |
| 1 | `RegisterPlayerUseCase` | Equivalent: `location=None`, then `visit()` sets the start location on the next line. |
| 2 | `UseItemUseCase` | Equivalent: the gold default `0` becomes `None` or nothing, and `if gold:` treats both as no gold. |
| 6 | `build_places`, `check_connections` | Not reachable: the start-up world check. The world is fixed data, so it never fails from outside (as the hand-written mutant "world check disabled"). |
| 8 | `save_path`, `save_high_score` | Covered outside mutmut: the defaults `katacombs.db` and `highscores.jsonl` are pinned by `boundary/startup.feature` (CONF-1, CONF-2), which mutmut skips. The hand-written mutant "default database file name" is killed. |
| 3 | `save_high_score` | Equivalent on a UTF-8 locale: the encoding of the high-score file changes from `utf-8` to the locale's default. **An assumption, not a proof:** a server with a non-UTF-8 locale would write a non-ASCII name (`JOSÉ`) in another encoding for the marketing job. |
| 11 | `create_app` | Not the contract: the title, version and description of FastAPI's generated `/openapi.json`. The contract is `spec/openapi.yaml`. |

The first run, before five new scenarios, also left 11
real gaps. Each one has a scenario now:
- the way up from the katacombs through the open manhole (ACT-13);
- a lost save that stopped the saves after it (SAVE-2);
- a restored save or snapshot that dropped its moves, visited locations,
  opened items or win (SAVE-2, ACCOUNT-4);
- account names of 1 and 50 characters (PLAYER-3).
