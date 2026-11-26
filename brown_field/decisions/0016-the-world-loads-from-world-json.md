# 0016 — The world loads from world.json through a world port

- **Status:** proposed
- **Date:** 2026-11-26
- **Need:** operational. One copy of the world, owned by the Specification.
  Anybody who changes the content of the game changes data, not code.
- **Traces to:** `ARCH-6`, `WORLD-1`, `WORLD-2`.
- **Change:** hexagon-5-world-data
- **Evidence (legacy code only):**
  - `game.py:34-69`: the location titles and the item sids as constants.
  - `game.py:135-301`: `build_items()` and `build_places()`, the world in code.
  - `game.py:304-313`: `check_connections()` refuses a world with a missing
    way back, except `ONE_WAY`.
  - `brown_field/spec/world.json` and `world.schema.json`: the same world
    as data, characterized on day 2 (decision 0009 for the slide).
  - `tests/world/conftest.py:22`: the world tests compare the game with
    `world.json`.

## Context

The world exists twice: in code, and in `world.json`. The tests keep the
two equal. On day 2 the code was the source and the data was the copy.
WORLD-1 already names `world.json` as the world. A change of content today
needs a change of code and of data, and a test to see that they agree.

## Decision

An outbound port, in `brown_field/application/ports_out.py`:

```python
class WorldSource(Protocol):
    def load(self) -> WorldData: ...   # locations, items, start, one-way exits
```

The default adapter reads `brown_field/spec/world.json` from the package,
checks the unique titles and the way-back rule of WORLD-2, and raises an
error that names the location and the direction, as `check_connections()`
did. The game runs the way-back check again on any world source. The
schema check stays in the tests (`tests/world/`), so the server needs no
`jsonschema` at run time. `InMemoryGame` takes `world` as a keyword
argument, with this adapter as its default.

The start comes from `start` in the data (PLAYER-1). The code keeps a
constant only for a title or a sid that a rule names: SPITALFIELDS MARKET (MOVE-6), BREWERY CELLAR and
OLD TUBE TUNNEL (MOVE-8), BACK YARD, KATACOMBS, the manhole and the key
(ACT-13, ACT-14), and the names BREAD and BEER (ACT-15). Every other title,
sid, exit and description comes from the data.

## Alternatives rejected

| Alternative | Why you rejected it |
| --- | --- |
| Keep the world in code, and the test that compares | Works today. Two copies stay, and the code copy is the one a regeneration must reproduce by hand, 200 lines of it. |
| Generate a Python module from `world.json` at build time | One source, no file read at start. It adds a build step that the exercise does not have, and a generated file that a person can edit by mistake. |
| Copy `world.json` into the code folder | Two files again, with a test to keep them equal. |
| Read the world from the database file | The world is fixed content, not state (Data ownership). It would make the world change with each support laptop. |

## Consequences

**Easier:** a change of content is a change of `world.json`, checked by
the way-back rule at start and by the schema in the tests. The code loses about 200 lines.

**More difficult:** the server now reads a file of `spec/` at start. A
package build must include it. A bad edit of `world.json` stops the server
at start, which is the intent.

**Risks that stay:** the constants that rules name must match the data.
A test checks that each one exists in `world.json`.

## Fitness functions

| Function | Target | How to run it | Need that it protects |
| --- | --- | --- | --- |
| The world tests | pass | `uv run pytest brown_field/tests/world` | WORLD-1, WORLD-2 |
| A bad world refuses to build, and names the location | pass | `uv run pytest -m ARCH-6` (to write) | The start check of today |
| No title or sid in the code that no rule names | zero hits | `uv run pytest brown_field/tests/fitness -m ARCH-6` (to write) | One copy of the world |
