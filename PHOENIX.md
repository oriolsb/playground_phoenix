# PHOENIX — Katacombs, brown field

The legacy Katacombs server: the game rules, accounts, chat, save, and
the REST API. The paths follow `brown_field/README.md`, "Where your work
goes". The web client (`brown_field/web/`) is a separate unit and a
consumer of this one.

```phoenix
system: Katacombs
spec: brown_field/spec/specification.md
decisions: brown_field/decisions
decision_index: brown_field/decisions/adr-index.md
changes: brown_field/spec/changes
map: brown_field/spec/evaluation/test-scenarios.md
contracts: brown_field/spec/openapi.yaml, brown_field/spec/player-state.schema.json, brown_field/spec/highscore-line.schema.json, brown_field/spec/world.schema.json
tests: brown_field/tests
code: brown_field
test_command: uv run pytest brown_field/tests
junit_command: uv run pytest brown_field/tests -q --junitxml=.phoenix/junit.xml
junit: .phoenix/junit.xml
primitives: PHOENIX.md, brown_field/spec, brown_field/decisions, brown_field/tests
sources: docs/katacombs.md
rule_id: [A-Z]+-\d+
reports: .phoenix/reports
```

## Units

| Unit | Rules | Interface | Modules | Risk |
| --- | --- | --- | --- | --- |
| game-server | none yet | `create_app`, `app`, `InMemoryGame`, the `*UseCase` classes, `KatacombsError` and subclasses; REST routes under `/game`, `/player`, `/items`, `/accounts`, `/leaderboard` | `brown_field/game.py`, `brown_field/api.py`, `brown_field/kata.py` | high |
