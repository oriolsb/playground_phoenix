# 0009 — The slide from the cellar goes one way

- **Status:** written after the code
- **Date:** 2026-11-25
- **Need:** product. A shortcut from the brewery into the tunnels.
- **Traces to:** `WORLD-2`, `WORLD-1`, `WEB-E2E-1`.
- **Change:** None.
- **Evidence (legacy code only):** `game.py:50-52`, "Product asked for a
  slide from the cellar into the tunnels (2022). The world rule 'each
  connection has a way back' does not apply to it." `check_connections`
  (`game.py:304-313`) skips that one exit and refuses any other exit with
  no way back when the game starts. `down` from BREWERY CELLAR leads to
  OLD TUBE TUNNEL; `up` from there leads to RAILWAY ARCHES.

## Context

Every other exit of the world has a way back: the game checks it at start.
In 2022, product asked for a slide from the cellar into the tunnels. The
slide breaks the world rule on purpose, so the code names it as the only
exception. The archaeology marks the reason known (item 7). The browser
test WEB-E2E-1 wins through the slide.

## Decision

The world keeps the slide as its only one-way exit, listed in
`oneWayExits` of `brown_field/spec/world.json`. Each other exit keeps its
way back.

## Alternatives rejected

| Alternative | Why you rejected it |
| --- | --- |
| Give the slide a way back | Product asked for a slide; a way up the slide is a different world. |
| Drop the start-up world check | It is what keeps a changed world from trapping a player. |

## Consequences

A player who slides down cannot climb back; the way out of the tunnels is
the ladder to RAILWAY ARCHES. A regenerated game must read the exception
from the world data, not find it by accident. The rat (MOVE-8) leaves what
it steals in OLD TUBE TUNNEL, below the slide.

## Fitness functions

| Function | Target | How to run it | Need that it protects |
| --- | --- | --- | --- |
| The live world matches `world.json`, and each exit but the slide has a way back | pass | `uv run pytest brown_field/tests -m "WORLD-1 or WORLD-2"` | The world, and the product's slide |
