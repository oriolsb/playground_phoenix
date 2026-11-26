# Decision records — Katacombs

Each record has the status "written after the code" when it recovers a
decision that the code and its comments show, and "accepted" when it is a
decision made during this exercise. A "proposed" record answers the open
question of a contested rule, for the group to accept or change; until then
the rule stays contested. The other contested behaviors have no record yet:
each one keeps its open question on its rule.

| Record | Title | Status | Rules | Change |
| --- | --- | --- | --- | --- |
| [0001](0001-the-market-closes-for-cleaning.md) | The market closes for cleaning in the last ten minutes of each hour | written after the code | `MOVE-6`, `WEB-MARKET-1`, `WEB-MARKET-2`, `WEB-MARKET-3` | None |
| [0002](0002-the-high-score-file-keeps-its-format.md) | The high-score file keeps its format for the marketing job | written after the code | `WIN-3`, `CONF-2` | None |
| [0003](0003-the-legacy-pickup-route-stays-for-mobile-v1.md) | The legacy pickup route stays for mobile client v1 | written after the code | `LEGACY-1`, `LEGACY-2`, `WEB-ITEM-4` | None |
| [0004](0004-a-repeated-take-succeeds.md) | A repeated take succeeds, and the client sends it again when slow | written after the code | `ACT-5`, `WEB-ITEM-2` | None |
| [0005](0005-the-game-is-saved-to-a-sqlite-file.md) | A player's state is saved to a SQLite file | written after the code | `SAVE-1`, `STORE-1`, `STORE-2`, `CONF-1` | None |
| [0006](0006-the-client-hides-the-leaderboard.md) | The web client hides the leaderboard until the season starts | written after the code | `WEB-BOARD-1` | None |
| [0007](0007-the-workshop-limits.md) | The limits and checks that the workshop sets | accepted | `OPS-1`, `WEB-OPS-1`, `WEB-E2E-1` | None |
| [0008](0008-the-seams-that-the-tests-use.md) | The seams that the tests use become part of the boundary | accepted | `ENTRY-1`, `ENTRY-2`, `MOVE-6`, `MOVE-8` | None |
| [0009](0009-the-slide-from-the-cellar-goes-one-way.md) | The slide from the cellar goes one way | written after the code | `WORLD-2`, `WORLD-1`, `WEB-E2E-1` | None |
| [0010](0010-the-evaluation-is-checked-by-breaking-the-code.md) | The Evaluation is checked by breaking the code, by invariants and by recorded answers | accepted | `MOVE-8`, `MOVE-6`, `ACCOUNT-2`, `ACCOUNT-4`, `SAVE-2`, `BAG-2`, `BAG-3`, `API-2` | None |
| [0011](0011-where-the-energy-gate-lives.md) | Where the energy gate lives, and at which energy it closes | proposed | `MOVE-5`, `WEB-MOVE-2`, `MOVE-2`, `ACT-15` | hexagon-9-energy-gate |
| [0012](0012-the-game-server-moves-to-ports-and-adapters.md) | The game-server moves to ports and adapters behind the frozen boundary | proposed | `ARCH-1`, `ARCH-2`, `ENTRY-1`, `ENTRY-2` | hexagon-1-guards |
| [0013](0013-the-clock-randomness-and-high-scores-sit-behind-ports.md) | The clock, randomness and the high-score file sit behind outbound ports | proposed. Replaces 0008 if accepted | `ARCH-3`, `MOVE-6`, `MOVE-8`, `PLAYER-1`, `WIN-3`, `CONF-2`, `ENTRY-1`, `ENTRY-2` | hexagon-2-outbound-ports |
| [0014](0014-saves-and-accounts-sit-behind-storage-ports.md) | Saves and accounts sit behind storage ports | proposed | `ARCH-4`, `STORE-1`, `STORE-2`, `SAVE-1`, `SAVE-2`, `ACCOUNT-4`, `ACCOUNT-6`, `CONF-1`, `ENTRY-1`, `ENTRY-2` | hexagon-3-storage |
| [0015](0015-every-command-gets-an-inbound-port.md) | Chat, the leaderboard, accounts and the legacy pickup get inbound ports | proposed | `ENTRY-3`, `ARCH-5`, `CHAT-1`, `CHAT-2`, `CHAT-3`, `BOARD-1`, `LEGACY-1`, `LEGACY-2`, `ACCOUNT-1`, `ACCOUNT-4`, `BAG-1` | hexagon-4-inbound-ports |
| [0016](0016-the-world-loads-from-world-json.md) | The world loads from world.json through a world port | proposed | `ARCH-6`, `WORLD-1`, `WORLD-2` | hexagon-5-world-data |
| [0017](0017-the-game-rules-move-into-a-domain-model.md) | The game rules move into a domain model | proposed | `ARCH-1` | hexagon-6-domain-model |
| [0018](0018-the-domain-owns-its-types.md) | The domain owns its types, and kata.py re-exports them | proposed | `ARCH-7`, `ARCH-1` | hexagon-7-domain-types |
| [0019](0019-the-rest-adapter-receives-its-ports.md) | The REST adapter receives its inbound ports | proposed | `ARCH-8`, `ARCH-5`, `ENTRY-1`, `ENTRY-2`, `MOVE-5`, `PLAYER-9` | hexagon-8-inbound-injection |
| [0020](0020-the-game-state-holds-no-rules.md) | The game state holds no rules and no view mapping | proposed | `ARCH-9`, `MOVE-6`, `STORE-3` | hexagon-10-slim-state |
| [0021](0021-the-default-adapters-have-one-builder.md) | The default adapters have one builder | proposed | `ENTRY-1` | hexagon-11-composition-factory |
