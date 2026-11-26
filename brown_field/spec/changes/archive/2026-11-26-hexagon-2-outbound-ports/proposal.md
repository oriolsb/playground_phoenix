# Proposal — hexagon-2-outbound-ports

Structure adapted from the OpenSpec proposal template (MIT).

Stage 2 of 6 of the move to ports and adapters (decision 0012). It puts
the clock, randomness and the high-score file behind outbound ports
(decision 0013).

## Need

- Who: the team that restructures the game-server, and the Evaluation.
- Why: the market rule, the rat, the sids and the high-score line call
  the standard library directly (`game.py:316-319`, `game.py:480-488`,
  `game.py:646-654`, `game.py:326-337`). Decision 0008 accepted these
  calls as seams, and said that day 3 can replace them with real ports.
  These are the three dependencies with the smallest blast radius, so
  they go first.
- Kind: operational
- Measurable as: ARCH-3 (zero calls to the clock, to `random` or to
  `open` outside `brown_field/adapters/`). Source: decisions 0008, 0013.

## What changes

- New outbound ports `Clock`, `RandomSource` and `HighScoreSink`, in
  `brown_field/application/ports_out.py`.
- New default adapters in `brown_field/adapters/system/` and
  `brown_field/adapters/files/`. Each default adapter calls the standard
  library at call time, through the module: `datetime.now()`,
  `random.random()`, `random.choice()`, `random.randint()`. So
  `time_machine` and `monkeypatch.setattr(random, ...)` keep working
  (`tests/conftest.py:119-172`).
- New keyword arguments of `InMemoryGame`: `clock`, `random_source`,
  `high_scores`. Each has the default adapter as its default value.
  `InMemoryGame()` with no argument behaves as today.
- Does not change: the market hours (MOVE-6), the rat chance (MOVE-8),
  the sid format (PLAYER-1), the high-score line and its file
  (WIN-3, CONF-2), the response of any route.

## Rules

- Added: ARCH-3
- Modified: none
- Removed: none
- Renamed: none

## Impact

No outside caller sees this change: no split into expand and contract is
needed. The port tier (decision 0008) grows by three keyword arguments
with defaults. Each existing call keeps working.

| Part | Pace layer | Blast radius | Review needed |
| --- | --- | --- | --- |
| `application/ports_out.py` | Slow (the ports) | Every adapter and every test fake | Yes |
| `adapters/system/`, `adapters/files/` | Fast | The market, the rat, the sids, the marketing job | Yes, for the high-score file (decision 0002) |
| `InMemoryGame` constructor | Slow (the port tier, decision 0008) | 17 port tests, the composition root | Yes |

## Decision record

0013 (proposed), whose Change field names this change.
