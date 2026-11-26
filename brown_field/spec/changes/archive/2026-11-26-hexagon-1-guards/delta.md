# Delta — hexagon-1-guards

Format adapted from the OpenSpec delta spec (MIT). On archive, the delta
merges into the specification and this file moves to the archive.

## ADDED Rules

#### ARCH-1 — Each layer imports only the layers inside it

- Status: accepted (decision 0012).
- Source: this change, and the need of decision 0012.
- Rule: Katacombs shall keep four layers in the package `brown_field`,
  from the inside out: the domain (`brown_field/domain/`), the
  application (`brown_field/application/`), the adapters
  (`brown_field/adapters/`), and the composition root (`game.py`,
  `api.py`, `__main__.py`). A module shall import only `kata.py`, its own
  layer, and the layers inside it. The domain and the application shall
  not import `sqlite3`, `os`, `fastapi`, `pydantic`, `uvicorn`, or the
  functions `datetime.now`, `open`, and the module `random`.
- Why: the rules of the game must survive a change of storage, of
  transport, or of clock. A dependency that points outward ties a rule to
  one adapter, and a regeneration of that adapter then breaks the rule.
- Observable result: a fitness function walks the import statements of
  every module under `brown_field/` (the tests excluded) and reports zero
  imports that point outward and zero forbidden names in the domain and
  the application. With one forbidden import added, it fails and names the
  file and the line.

#### ARCH-2 — Each use case satisfies its port

- Status: accepted (decision 0012).
- Source: this change, and the need of decision 0012.
- Rule: Katacombs shall make each `*UseCase` class satisfy the port of the
  same name in `kata.py`, so that a static type checker accepts each
  use case where its port is expected.
- Why: a Python `Protocol` is structural, and nothing checks it at run
  time. Without a type check, a use case drifts from its port and only the
  REST tests notice, late. In Java the compiler does this check.
- Observable result: a check file assigns each use case to its port, for
  example `move: Move = MoveUseCase(InMemoryGame())`. The type checker
  (pyright or mypy, strict on that file) reports zero errors. With one
  parameter of `MoveUseCase.execute` renamed, it reports one error.

## Other changes to the specification

### Section "Structure", a new section after "Operations"

These rules hold the shape of the code behind the boundary. A caller of
the REST API or of the ports does not see them. A regeneration must keep
them, and the fitness functions check them.

### Terms: six new rows, after "Error reason"

| Term | Meaning | Avoid |
| --- | --- | --- |
| Port | An interface that the core of the game publishes or needs. | interface (alone), API (for this idea) |
| Inbound port | A port that a caller uses to drive the game: one `Protocol` in `kata.py` with one method `execute`. | service, endpoint |
| Outbound port | A port that the game uses to reach the outside: the clock, randomness, files, storage. A `Protocol` in `brown_field/application/ports_out.py`. | repository (alone), driver |
| Adapter | Code that connects a port to one technology: FastAPI, SQLite, the file system, the system clock. | implementation (alone), plugin |
| Domain model | The rules of the game as objects with behavior, with no input or output. | entities, model (alone) |
| Composition root | The one place that builds the adapters and hands them to the game: `InMemoryGame` and `create_app`. | container, context (alone), wiring |

## Unchanged

- `ENTRY-1`: `create_app(game=None)` keeps its behavior and its name.
- `ENTRY-2`: `brown_field.api.app` stays.
- `OPS-1`: the guards run in the test suite, not in a request.
