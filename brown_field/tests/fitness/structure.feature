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
  Scenario Outline: The rules do no I/O: <source>
    When the check reads the imports and calls of "<source>"
    Then it imports none of "sqlite3, os, fastapi" and never calls open

    Examples:
      | source         |
      | game.py        |
      | core/state.py  |
      | core/ports.py  |
