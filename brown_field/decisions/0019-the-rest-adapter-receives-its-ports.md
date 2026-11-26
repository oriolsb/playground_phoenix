# 0019 — The REST adapter receives its inbound ports

- **Status:** accepted
- **Date:** 2026-11-26
- **Need:** operational. The inbound ports must be the real contract of the
  driving side, so the REST adapter can be regenerated and tested alone
  (finding F1 of the hexagonal review).
- **Traces to:** `ARCH-8`, `ARCH-5`, `ENTRY-1`, `ENTRY-2`, `MOVE-5`, `PLAYER-9`.
- **Change:** hexagon-8-inbound-injection
- **Evidence (legacy code only):**
  - `adapters/rest/app.py:15-33`: imports `GameState` and every `*UseCase`.
  - `adapters/rest/app.py:105-208`: each route builds a use case from the game.
  - `adapters/rest/app.py:199-205`: the move route reads `game.players`.
  - `api.py:10-14`: `create_app` passes the whole game to `build_app`.

## Context

Decision 0015 gave every command a port, but nothing depends on the ports:
the adapter uses the concrete classes and the game. A Python `Protocol` is
structural, so the check of ARCH-2 proves the use cases fit their ports, and
no caller uses that fact.

## Decision

`kata.py` gets `InboundPorts`, a dataclass with one field per inbound port,
each typed as the port. In Java terms, a constructor that takes 16
interfaces, bundled in one value. `build_app(ports: InboundPorts)` replaces
`build_app(game)`, and `adapters/rest/` imports only `kata.py` and FastAPI
(ARCH-8). It takes its error types from `kata.py` too, which re-exports the
domain errors (decision 0018), so the ports keep raising the errors of
API-2.

`create_app(game=None)` builds one `InboundPorts` per game from its use
cases, and passes it in. The use cases hold no state of their own, so one
instance per game behaves as one per request.

Until decision 0011 is accepted, the energy gate of MOVE-5 stays in the
`move` route, and reads the energy through `InspectBag`. For an unknown
player, `InspectBag` raises the same `PlayerNotFound` with the same message
that `Move` raised, so the answer stays the same.

## Alternatives rejected

| Alternative | Why you rejected it |
| --- | --- |
| Pass 16 keyword arguments to `build_app` | The same dependencies, with no single type to fake or to check. |
| Pass a factory, `build_app(make_ports: Callable[[], InboundPorts])` | One use case per request is not needed: the use cases hold no state. A factory adds an indirection for no behavior. |
| Port-level error types in `kata.py` | A second error hierarchy to keep in step with API-2. The group kept the domain errors. |
| Keep `build_app(game)` and only stop importing `state` | The adapter would still build the use cases, and could still reach the state through them. |

## Consequences

**Easier:** a test builds the REST adapter from fakes, with no game. A new
driving adapter (a CLI, a socket) takes the same `InboundPorts`.

**More difficult:** one more public type in `kata.py`. The composition root
must list every port.

**Risks that stay:** the MOVE-5 gate stays a rule in a route until 0011 is
accepted (change `hexagon-9-energy-gate`).

## Fitness functions

| Function | Target | How to run it | Need that it protects |
| --- | --- | --- | --- |
| No import of `application` or `domain` under `adapters/rest/` | zero hits | `uv run pytest brown_field/tests/fitness -m ARCH-8` (to write) | The adapter depends on the ports |
| The REST adapter from fake ports, with no `GameState` | pass | `uv run pytest -m ARCH-8` (to write) | The ports are the contract |
| The contract test and the transcripts | pass | `uv run pytest brown_field/tests/contract brown_field/tests/fitness/test_transcripts.py` | Every REST client |
