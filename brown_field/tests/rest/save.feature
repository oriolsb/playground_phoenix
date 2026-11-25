@acceptance
Feature: A save survives a restart of the server
  A save stores the player's state. A restart brings saved players back,
  but the world starts fresh: open, closed and locked items, and the items
  in the locations, are as at the first start.

  @api @SAVE-1
  Scenario: A save answers with the path of the database file
    Given a new player named "ana"
    When the player saves the game
    Then the save answer names the database file

  @api @SAVE-2
  Scenario: A saved player comes back after a restart with the same state
    Given a new player named "ana"
    When the player goes north
    And the player takes the "BEER"
    And the player saves the game
    And the server restarts
    Then the player is at "OLD TRUMAN BREWERY"
    And the bag holds "BEER"
    And the bag shows gold 5 and energy 11

  @api @SAVE-2
  Scenario: A player who did not save is gone after a restart
    Given a new player named "ana"
    When the server restarts
    And the player looks around
    Then the request is refused because the player is unknown

  @api @SAVE-2
  Scenario: A move after the save is lost in a restart
    Given a new player named "ana"
    When the player saves the game
    And the player goes north
    And the server restarts
    Then the player is at "BRICK LANE"
    And the bag shows gold 0 and energy 12

  @api @SAVE-2 @contested
  Scenario: A restart puts a saved item back in its location too
    # The world is not in the save (game.py:449-450), so the BEER is in the
    # bag and in the brewery: the brewery shows both of its beers again.
    Given a new player named "ana"
    When the player goes north
    And the player takes the "BEER"
    And the player saves the game
    And the server restarts
    Then the bag holds "BEER"
    And the location holds 2 "BEER"

  @api @SAVE-2 @GOLD-2
  Scenario: A restart closes the crate again, but its gold stays paid
    Given the clock shows minute 10
    And a new player named "ana"
    When the player goes east
    And the player opens the "CRATE"
    And the player saves the game
    And the server restarts
    And the player opens the "CRATE"
    Then the answer is "OPENED."
    And the bag shows gold 10 and energy 11

  @api @SAVE-2
  Scenario: After a restart, the saved players are listed in the order they saved
    # game.py:458 loads the saves ORDER BY saved_at; the time has seconds only.
    Given a new player named "ana"
    And a new player named "bo"
    And a new player named "cy"
    And a new player named "dee"
    When the clock shows minute 10
    And "DEE" saves the game
    And the clock shows minute 11
    And "BO" saves the game
    And the clock shows minute 12
    And "CY" saves the game
    And the clock shows minute 13
    And "ANA" saves the game
    And the server restarts
    And a client lists the players
    Then the list names "DEE, BO, CY, ANA" in this order

  @api @SAVE-2
  Scenario: A save at a lost location is skipped, and the saves after it still load
    Given a new player named "ana"
    And a new player named "bo"
    When the clock shows minute 10
    And "ANA" saves the game
    And the clock shows minute 11
    And "BO" saves the game
    And the saved location of "ANA" is changed to "NOWHERE" in the database
    And the server restarts
    And a client lists the players
    Then the list names "BO" in this order

  @api @SAVE-2 @WIN-2
  Scenario: A restored save keeps the visited locations and the move count
    Given the clock shows minute 10
    And a new player named "ana"
    When the player goes north
    And the player saves the game
    And the server restarts
    And the player goes south
    And the player goes north
    Then the bag shows gold 5 and energy 9
    When the player goes south
    And the player has won through the tunnels
    Then the leaderboard shows "ANA" with score 40 and 10 moves

  @api @SAVE-2 @MOVE-7
  Scenario: A restored save keeps the win
    Given a new player named "ana"
    When the player has won through the tunnels
    And the player saves the game
    And the server restarts
    Then the player has won
    When the player goes west
    Then the request is refused with status 405 and the message "THE GAME IS OVER. YOU ALREADY FOUND THE EXIT."

  @api @SAVE-2
  Scenario: A save whose location no longer exists is skipped at the start
    Given a new player named "ana"
    When the player saves the game
    And the saved location of the player is changed to "NOWHERE" in the database
    And the server restarts
    And the player looks around
    Then the request is refused because the player is unknown

  @SAVE-2 @contested
  Scenario: A save from before 2023 stops the server from starting
    # The payload of before 2023 has no energy and no move count
    # (game.py:754). The start reads both keys without a default.
    Given the golden database holds a save from before 2023
    When the server starts
    Then the server does not start, for want of "energy"
