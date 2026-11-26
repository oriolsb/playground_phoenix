@fitness
Feature: The structure of decision 0012, checked on the code
  The rules live behind the ports; the REST adapter only maps HTTP to a
  use case and back. A route that reads the game state holds a rule that a
  second adapter would lose.

  @ENTRY-4
  Scenario: The REST adapter reads no game state outside a use case
    When the check reads "api.py"
    Then the game is only built or passed to a use case

  @ENTRY-4
  Scenario: The check sees a route that reads the game
    When the check reads the code "def route(game):\n    return game.players\n"
    Then the check finds 1 read of the game

  @ENTRY-6
  Scenario Outline: The rules do no I/O and know no adapter: <source>
    When the check reads the imports and calls of "<source>"
    Then it imports none of "sqlite3, os, fastapi" and never calls open
    And it imports nothing from the adapters

    Examples:
      | source             |
      | core/accounts.py   |
      | core/chat.py       |
      | core/errors.py     |
      | core/game.py       |
      | core/items.py      |
      | core/looking.py    |
      | core/movement.py   |
      | core/players.py    |
      | core/ports.py      |
      | core/saving.py     |
      | core/state.py      |
      | core/winning.py    |
      | core/world.py      |

  @WORLD-3
  Scenario Outline: The rules name no item: <source>
    When the check reads the string literals of "<source>"
    Then none of them is an item sid

    Examples:
      | source             |
      | core/accounts.py   |
      | core/chat.py       |
      | core/errors.py     |
      | core/game.py       |
      | core/items.py      |
      | core/looking.py    |
      | core/movement.py   |
      | core/players.py    |
      | core/ports.py      |
      | core/saving.py     |
      | core/state.py      |
      | core/winning.py    |
      | core/world.py      |

  Scenario Outline: A module of the rules stays small: <source>
    When the check counts the lines of "<source>"
    Then it has at most 300 lines

    Examples:
      | source             |
      | core/accounts.py   |
      | core/chat.py       |
      | core/errors.py     |
      | core/game.py       |
      | core/items.py      |
      | core/looking.py    |
      | core/movement.py   |
      | core/players.py    |
      | core/ports.py      |
      | core/saving.py     |
      | core/state.py      |
      | core/winning.py    |
      | core/world.py      |
