@acceptance
Feature: A new player wins the game through the REST API
  The shortest proof that the game still works: one player plays from the
  start to the katacombs exit, on the route through the market and the
  manhole. On the way, the market answers both ways of its clock rule.
  The expected values come from the rules, not from the code.

  # Route, energy and gold, from the rules:
  #   BRICK LANE (12) -> N brewery (11, gold 5) -> U rooftop (10), KEY
  #   -> D brewery (9) -> S BRICK LANE (8) -> E market at minute 50: refused (8)
  #   -> E market at minute 49 (7), CRATE: 10 gold -> S BACK YARD (6), KEY, MANHOLE
  #   -> D KATACOMBS (5, gold 45), GOBLET (value 50) -> E KATACOMBS EXIT (4)
  # Score = 45 gold + 50 (GOBLET) = 95.
  # Move count = 8 moves + 6 item actions = 14. The refused move does not
  # count; the refused open of the locked MANHOLE does (ACT-17).

  @api @PLAYER-1 @MOVE-1 @MOVE-2 @MOVE-3 @MOVE-6 @MOVE-7 @GOLD-1 @GOLD-2 @ACT-4 @ACT-10 @ACT-13 @ACT-14 @ACT-17 @BAG-2 @WIN-1 @WIN-2 @WIN-3
  Scenario: A new player wins on the route through the market
    Given a new player named "ana"
    Then the player is at "BRICK LANE"
    And the bag shows gold 0 and energy 12

    # The key, on the brewery rooftop.
    When the player goes north
    Then the player is at "OLD TRUMAN BREWERY"
    And the bag shows gold 5 and energy 11
    When the player goes up
    Then the player is at "BREWERY ROOFTOP"
    When the player takes the "KEY"
    Then the answer is "TAKEN."
    When the player goes down
    Then the bag shows gold 5 and energy 9
    When the player goes south
    Then the player is at "BRICK LANE"

    # The market: closed at minute 50, open at minute 49.
    Given the clock shows minute 50
    When the player goes east
    Then the request is refused with status 405 and the message "THE MARKET IS CLOSED FOR CLEANING. COME BACK LATER."
    And the bag shows gold 5 and energy 8
    Given the clock shows minute 49
    When the player goes east
    Then the player is at "SPITALFIELDS MARKET"
    When the player opens the "CRATE"
    Then the answer is "OPENED. YOU FIND 10 GOLD."
    And the bag shows gold 15 and energy 7

    # The manhole: locked, unlocked with the key, then open.
    When the player goes south
    Then the player is at "BACK YARD"
    And the exits are "north"
    When the player opens the "MANHOLE"
    Then the request is refused with status 405 and the message "THE MANHOLE IS LOCKED."
    When the player uses the "KEY"
    Then the answer is "YOU UNLOCK THE MANHOLE COVER."
    When the player opens the "MANHOLE"
    Then the answer is "OPENED."
    And the exits are "north, down"

    # The katacombs and the exit.
    When the player goes down
    Then the player is at "KATACOMBS"
    And the bag shows gold 45 and energy 5
    When the player takes the "GOBLET"
    Then the answer is "TAKEN."
    And the bag shows score 95
    When the player goes east
    Then the player is at "KATACOMBS EXIT"
    And the location is the katacombs exit
    And the player has won
    And the leaderboard shows "ANA" with score 95 and 14 moves
    And the high-score file holds one line for "ANA" with score 95

    # After the win, the game is over.
    When the player goes west
    Then the request is refused with status 405 and the message "THE GAME IS OVER. YOU ALREADY FOUND THE EXIT."
