# Proposal — hexagon-5-world-data

Structure adapted from the OpenSpec proposal template (MIT).

Stage 5 of 6 of the move to ports and adapters (decision 0012). The game
reads its world from `world.json` through a world port, instead of
building it in code (decision 0016).

## Need

- Who: the team that restructures the game-server; anybody who changes
  the content of the game.
- Why: the world is described twice. `game.py` builds it in code
  (`game.py:34-69`, `game.py:135-301`, about 200 lines of constants and
  builders), and `brown_field/spec/world.json` describes it as data
  (WORLD-1). The world tests compare the two
  (`tests/world/conftest.py:22`). Two copies can drift. The data copy is
  the one that the Specification names.
- Kind: operational
- Measurable as: ARCH-6 (the code holds no location title, item sid or
  exit of the world, except the titles and sids that a rule names).
  Source: decision 0016.

## What changes

- New outbound port `WorldSource`, in `brown_field/application/ports_out.py`.
- New default adapter that reads `brown_field/spec/world.json`, checks it
  against `world.schema.json` and the way-back rule (WORLD-2), and refuses
  to start on a bad world, as `check_connections` does today
  (`game.py:304-313`).
- New keyword argument of `InMemoryGame`: `world`. Its default is the
  JSON adapter.
- The code keeps a constant only for a title or a sid that a rule names:
  the start (PLAYER-1), the market (MOVE-6), the cellar and the tunnel
  (MOVE-8), the back yard, the katacombs, the manhole and the key
  (ACT-13, ACT-14), bread and beer (ACT-15).
- Does not change: any location, exit, item, sid, value, gold or lock of
  the world. `world.json` does not change.

## Rules

- Added: ARCH-6
- Modified: none
- Removed: none
- Renamed: none

## Impact

No outside caller sees this change: no split into expand and contract is
needed. The world is a boundary with every save, golden file and the
mobile client v1 (WORLD-1). Its content does not change. Its owner does:
the data file, not the code.

| Part | Pace layer | Blast radius | Review needed |
| --- | --- | --- | --- |
| `world.json` becomes the source the code reads | Slow (the data model) | Every save, golden file, high-score line, mobile client v1 | Yes |
| `WorldSource` and its JSON adapter | Medium | The start of the server | Yes |
| The constants removed from `game.py` | Fast | None, if the world tests pass | No |

## Decision record

0016 (proposed), whose Change field names this change.
