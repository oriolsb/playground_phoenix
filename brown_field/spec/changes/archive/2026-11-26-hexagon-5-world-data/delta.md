# Delta — hexagon-5-world-data

Format adapted from the OpenSpec delta spec (MIT). On archive, the delta
merges into the specification and this file moves to the archive.

## ADDED Rules

#### ARCH-6 — The game reads its world through a world port

- Status: accepted (decision 0016).
- Source: this change, and decision 0016.
- Rule: When a game is built, Katacombs shall read the fixed world through
  the port `WorldSource`. Where `InMemoryGame` gets no world source,
  Katacombs shall read `brown_field/spec/world.json`. If the world repeats a
  title or breaks the way-back rule of WORLD-2, then Katacombs shall refuse
  to build the game, with an error that names the location. The tests check
  `world.json` against `world.schema.json`.
- Why: the Specification names `world.json` as the world (WORLD-1). One
  copy cannot drift from another. A change of content is then a change of
  data, reviewed as data.
- Observable result: (1) the world tests (`tests/world/`) pass unchanged.
  (2) A game built with a world source that has a missing way back fails
  to build, and the error names the location and the direction, as
  `check_connections` does today. (3) A fitness function finds in the code
  no location title and no item sid that no rule names.

## Unchanged

- `WORLD-1`: the game is played in the world of `world.json`.
- `WORLD-2`: each exit has a way back, except the slide from the cellar.
- `PLAYER-1`: every game starts at BRICK LANE.
- `GOLD-1`: the first visit adds the gold of the location.
- `GOLD-2`: the first opening of the crate adds its gold.
- `ACT-13`: the open manhole connects the back yard and the katacombs.
- `ACT-14`: the key unlocks the manhole in the back yard.
- `SAVE-2`: a save whose location is not in the world is skipped at start.
