@acceptance
Feature: The leaderboard ranks the finished games
  A win adds a finished game. The leaderboard shows the highest score
  first, and equal scores in the order of their wins.

  @api @BOARD-1 @WIN-2 @BAG-2
  Scenario: The highest score comes first, and equal scores keep the order of the wins
    # The tunnel route gives 35 gold. BO also takes the GOBLET (value 50): 85.
    Given a new player named "ana"
    And a new player named "bo"
    And a new player named "cy"
    When "ANA" has won through the tunnels
    And "BO" goes south
    And "BO" goes east
    And "BO" goes down
    And "BO" goes east
    And "BO" goes north
    And "BO" takes the "GOBLET"
    And "BO" goes east
    And "CY" has won through the tunnels
    Then the leaderboard lists "BO, ANA, CY" in this order
    And the leaderboard shows "BO" with score 85 and 7 moves
    And the leaderboard shows "ANA" with score 35 and 6 moves
    And the leaderboard shows "CY" with score 35 and 6 moves

  @api @WIN-2
  Scenario: The leaderboard is empty after a restart
    Given a new player named "ana"
    When the player has won through the tunnels
    And the server restarts
    Then the leaderboard is empty
