@acceptance
Feature: Players look and move through the exits
  A player sees the location, can look through an exit without moving, and
  moves through the exits. A move costs energy; a refused move costs none.

  Background:
    Given a new player named "ana"

  @api @LOOK-1
  Scenario: Looking around shows the start location
    When the player looks around
    Then the answer shows the location "BRICK LANE"
    And the exits are "north, east, south, west"
    And the location holds 0 "BEER"

  @api @LOOK-2 @GOLD-1
  Scenario: Looking through an exit shows the next location without moving
    When the player looks north
    Then the answer shows the location "OLD TRUMAN BREWERY"
    And the player is at "BRICK LANE"
    And the bag shows gold 0 and energy 12

  @api @LOOK-3
  Scenario: Looking where there is no exit is refused
    When the player looks up
    Then the request is refused with status 405 and the message "THERE IS NOTHING IN THAT DIRECTION."

  @api @MOVE-4
  Scenario: Moving where there is no exit is refused and costs nothing
    When the player goes up
    Then the request is refused with status 405 and the message "YOU CAN'T GO THAT WAY."
    And the bag shows gold 0 and energy 12

  @api @GOLD-1
  Scenario: The gold of a location is added on the first visit only
    When the player goes north
    And the player goes south
    And the player goes north
    Then the bag shows gold 5 and energy 9

  @api @MOVE-5
  Scenario: A player with no energy can't move
    # 12 moves between BRICK LANE and the brewery use all 12 energy.
    When the player goes north
    And the player goes south
    And the player goes north
    And the player goes south
    And the player goes north
    And the player goes south
    And the player goes north
    And the player goes south
    And the player goes north
    And the player goes south
    And the player goes north
    And the player goes south
    Then the bag shows gold 5 and energy 0
    When the player goes north
    Then the request is refused with status 405 and the message "YOU ARE TOO TIRED TO MOVE. EAT OR DRINK SOMETHING."

  @api @MOVE-5
  Scenario: The tired check comes before the exit check
    When the player goes north
    And the player goes south
    And the player goes north
    And the player goes south
    And the player goes north
    And the player goes south
    And the player goes north
    And the player goes south
    And the player goes north
    And the player goes south
    And the player goes north
    And the player goes south
    And the player goes up
    Then the request is refused with status 405 and the message "YOU ARE TOO TIRED TO MOVE. EAT OR DRINK SOMETHING."

  @api @MOVE-6
  Scenario Outline: At minute <minute> the market is <state>
    Given the clock shows minute <minute>
    When the player goes east
    Then the response status is <status>

    Examples:
      | minute | state  | status |
      | 0      | open   | 200    |
      | 49     | open   | 200    |
      | 50     | closed | 405    |
      | 59     | closed | 405    |

  @api @MOVE-8
  Scenario: The rat in the cellar takes an item without value to the tube tunnel
    Given the rat always runs
    When the player goes north
    And the player takes the "BEER"
    And the player goes down
    Then the description ends with "A RAT RUNS OFF WITH YOUR BEER."
    And the bag is empty
    When the player goes down
    Then the player is at "OLD TUBE TUNNEL"
    And the location holds 1 "BEER"

  @api @MOVE-8
  Scenario: The rat never takes an item with value
    Given the rat always runs
    When the player goes north
    And the player goes down
    And the player takes the "RING"
    And the player goes up
    And the player goes down
    Then the description does not mention "RAT"
    And the bag holds "RING"

  @api @MOVE-8
  Scenario: Without the rat, the cellar takes nothing
    Given the rat never runs
    When the player goes north
    And the player takes the "BEER"
    And the player goes down
    Then the description does not mention "RAT"
    And the bag holds "BEER"
