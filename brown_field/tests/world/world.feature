Feature: The world
  The world of the game is fixed data, in brown_field/spec/world.json.
  These scenarios walk the live world through the REST API and compare
  each location and each item with that file, so a regenerated game that
  invents or changes the world fails.

  @WORLD-1 @api
  Scenario: The world file is valid and complete
    Given the world file
    Then the world file is valid against its schema
    And each item of the world file starts in exactly one location
    And each exit of the world file leads to a location of the world file

  @WORLD-1 @api
  Scenario: Each location is as the world file states
    Given the clock shows minute 10
    And the rat never runs
    And the world file
    When a scout walks to each location of the world file
    Then each location shows the title, description, exits and items of the world file
    And each look in a direction shows the location that the exit names
    And each first visit adds the gold of the location

  @WORLD-1 @api
  Scenario: Each item is as the world file states
    Given the world file
    When a client asks for each item of the world file
    Then each answer is the item of the world file

  @WORLD-1 @api
  Scenario: Each item with gold inside gives it on the first opening, and each locked item refuses to open
    Given the clock shows minute 10
    And the rat never runs
    And the world file
    When a scout opens each item of the world file that has gold inside or a lock
    Then each item with gold inside answered "OPENED. YOU FIND <gold> GOLD."
    And each locked item answered "THE <name> IS LOCKED."

  @WORLD-2 @api
  Scenario: The slide from the cellar has no way back
    Given the rat never runs
    And a new player named "ANA"
    When "ANA" goes north
    And "ANA" goes down
    And "ANA" goes down
    And "ANA" goes up
    Then "ANA" is at "RAILWAY ARCHES"

  @WORLD-2 @api
  Scenario: Every other exit of the world has a way back
    Given the clock shows minute 10
    And the rat never runs
    And the world file
    When a scout walks to each location of the world file
    Then from each location, each exit but the one-way exits has a way back in the opposite direction
