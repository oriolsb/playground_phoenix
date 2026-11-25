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
