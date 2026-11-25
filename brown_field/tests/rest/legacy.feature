@acceptance
Feature: The legacy pickup route of mobile client v1
  An older way to take an item. It skips the bag limit, the win check and
  the move count, and answers OK even when the item is not here.

  @api @LEGACY-1
  Scenario: The legacy pickup takes an item and does not count a move
    # 1 + 1 moves to the brewery and back, then 6 on the tunnel route = 8.
    # The legacy pickup adds none. Gold: brewery 5 + tunnels 35 = 40.
    Given a new player named "ana"
    When the player goes north
    And the player picks up the "BEER" with the legacy route
    Then the answer is "OK"
    And the bag holds "BEER"
    And the location holds 1 "BEER"
    When the player goes south
    And the player has won through the tunnels
    Then the leaderboard shows "ANA" with score 40 and 8 moves

  @api @LEGACY-2
  Scenario: The legacy pickup of an item elsewhere answers OK and changes nothing
    Given a scout has seen the "KEY" at the end of the path "north, up"
    And a new player named "ana"
    When the player picks up the "KEY" with the legacy route
    Then the answer is "OK"
    And the bag is empty

  @api @ITEM-2
  Scenario: The legacy pickup of an unknown item is not found
    Given a new player named "ana"
    When a client sends PUT /player/{sid}/pickup/unknown with the body -
    Then the request is refused with status 404 and the message "ITEM unknown NOT FOUND."
