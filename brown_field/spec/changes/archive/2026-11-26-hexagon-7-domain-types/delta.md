# Delta — hexagon-7-domain-types

Format adapted from the OpenSpec delta spec (MIT). On archive, the delta
merges into the specification and this file moves to the archive.

## ADDED Rules

#### ARCH-7 — The domain imports nothing outside the domain

- Status: accepted (decision 0018).
- Source: this change; finding F4 of the hexagonal review; decision 0018.
- Rule: Katacombs shall define every type that a game rule uses in
  `brown_field/domain/`, and no module of the domain shall import
  `brown_field.kata` or any other module outside `brown_field/domain/`.
  `kata.py` shall re-export `Item`, `Action`, `Direction` and the error
  types, so their public names stay importable from it.
- Why: the domain is the innermost ring. A domain that imports the API
  module breaks when the API changes, and cannot be regenerated alone.
- Observable result: (1) a fitness function finds no import of
  `brown_field.kata` under `brown_field/domain/`. (2)
  `from brown_field.kata import Item, Action, Direction, NotAllowed` works,
  and each name is the same object as its domain definition. (3) The whole
  suite passes unchanged.

## Other changes to the specification

### Revision of ARCH-1 (open in `hexagon-1-guards`), to apply when that change is archived

#### ARCH-1 — Each layer imports only the layers inside it

- Status: accepted (decisions 0012, 0018).
- Source: change `hexagon-1-guards`, revised by `hexagon-7-domain-types`.
- Rule: Katacombs shall keep five layers in the package `brown_field`,
  from the inside out: the domain (`brown_field/domain/`), the ports
  (`kata.py`), the application (`brown_field/application/`), the adapters
  (`brown_field/adapters/`), and the composition root (`game.py`,
  `api.py`, `__main__.py`). A module shall import only its own layer and
  the layers inside it. The domain and the application shall not import
  `sqlite3`, `os`, `fastapi`, `pydantic`, `uvicorn`, or the functions
  `datetime.now`, `open`, and the module `random`.
- Why: the rules of the game must survive a change of storage, of
  transport, of clock, or of the public API.
- Observable result: the fitness function of ARCH-1 uses the five layers
  above, and fails on a planted import from the domain into `kata.py`.
- Revised: 2026-11-26. The ports move outside the domain (decision 0018).

## Unchanged

- `WORLD-1`: the world and its items keep every field.
- `API-2`: every error keeps its status and its message.
- `ENTRY-1`: `create_app(game=None)` keeps its behavior.
