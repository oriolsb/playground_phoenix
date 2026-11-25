@acceptance
Feature: Players take, drop, open, close and use items
  An item allows only its own actions. Open, closed and locked belong to
  the world, so one player's action changes it for every player.

  @api @ITEM-1
  Scenario: A client can inspect an item without a player
    Given a scout has seen the "BEER" at the end of the path "north"
    When a client asks for the item "BEER"
    Then the item is "BEER" with the value 0 and the actions "pick, drop, use"
    And the item description is "A BOTTLE OF CRAFTED BEER FROM THE BREWERY."

  @api @ITEM-2
  Scenario: An unknown item sid is not found
    When a client sends GET /items/unknown with the body -
    Then the request is refused with status 404 and the message "ITEM unknown NOT FOUND."

  @api @ITEM-2 @ACT-3
  Scenario: The unknown item check comes before the win check
    Given a new player named "ana"
    And the player has won through the tunnels
    When a client sends PUT /player/{sid}/item/unknown/use/pick with the body -
    Then the request is refused with status 404 and the message "ITEM unknown NOT FOUND."

  @api @ACT-1
  Scenario: An item that is neither here nor in the bag can't be reached
    Given a scout has seen the "KEY" at the end of the path "north, up"
    And a new player named "ana"
    When the player takes the "KEY"
    Then the request is refused with status 404 and the message "THERE IS NO KEY HERE."

  @api @ACT-2
  Scenario Outline: An item refuses an action it does not allow: <action> the <item>
    Given a new player named "ana"
    When the player goes <direction>
    And the player <verb> the "<item>"
    Then the request is refused with status 405 and the message "YOU CAN'T <action> THE <item>."

    Examples:
      | direction | verb   | item     | action |
      | north     | opens  | BEER     | OPEN   |
      | north     | closes | BEER     | CLOSE  |

  @api @ACT-2
  Scenario: An umbrella has no use
    Given a new player named "ana"
    When the player goes west
    And the player takes the "UMBRELLA"
    And the player uses the "UMBRELLA"
    Then the request is refused with status 405 and the message "YOU CAN'T USE THE UMBRELLA."

  @api @ACT-2
  Scenario: A crate can't be taken
    Given a new player named "ana"
    And the clock shows minute 10
    When the player goes east
    And the player takes the "CRATE"
    Then the request is refused with status 405 and the message "YOU CAN'T PICK THE CRATE."

  @api @ACT-3
  Scenario: A player who has won can't act on items
    Given a new player named "ana"
    When the player goes south
    And the player goes east
    And the player goes down
    And the player goes east
    And the player goes north
    And the player takes the "GOBLET"
    And the player goes east
    And the player drops the "GOBLET"
    Then the request is refused with status 405 and the message "THE GAME IS OVER. YOU ALREADY FOUND THE EXIT."

  @api @ACT-4 @ACT-6
  Scenario: A taken item moves into the bag, and a dropped one into the location
    Given a new player named "ana"
    When the player goes north
    And the player takes the "BEER"
    Then the answer is "TAKEN."
    And the bag holds "BEER"
    And the location holds 1 "BEER"
    When the player goes south
    And the player drops the "BEER"
    Then the answer is "DROPPED."
    And the bag is empty
    And the location holds 1 "BEER"

  @api @ACT-5
  Scenario: Taking an item already in the bag answers TAKEN again and changes nothing
    Given a new player named "ana"
    When the player goes north
    And the player takes the "BEER"
    And the player takes the same item again
    Then the answer is "TAKEN."
    And the bag holds "BEER"
    And the location holds 1 "BEER"

  @api @ACT-7
  Scenario: A player can't drop an item that is here but not in the bag
    Given a new player named "ana"
    When the player goes north
    And the player drops the "BEER"
    Then the request is refused with status 405 and the message "YOU ARE NOT CARRYING THE BEER."

  @api @ACT-7
  Scenario: A player can't use an item that is here but not in the bag
    Given a new player named "ana"
    When the player goes north
    And the player uses the "BEER"
    Then the request is refused with status 405 and the message "YOU ARE NOT CARRYING THE BEER."

  @api @ACT-8 @ACT-9 @ACT-11 @ACT-12 @GOLD-2
  Scenario: The crate is open or closed for every player, and its gold is paid once per player
    Given the clock shows minute 10
    And a new player named "ana"
    And a new player named "bo"
    When "ANA" goes east
    And "BO" goes east
    And "ANA" opens the "CRATE"
    Then the answer is "OPENED. YOU FIND 10 GOLD."
    When "BO" opens the "CRATE"
    Then the request is refused with status 405 and the message "THE CRATE IS ALREADY OPEN."
    When "BO" closes the "CRATE"
    Then the answer is "CLOSED."
    When "ANA" closes the "CRATE"
    Then the request is refused with status 405 and the message "THE CRATE IS ALREADY CLOSED."
    When "BO" opens the "CRATE"
    Then the answer is "OPENED. YOU FIND 10 GOLD."
    When "BO" closes the "CRATE"
    And "ANA" opens the "CRATE"
    Then the answer is "OPENED."
    And the bag of "ANA" shows gold 10 and energy 11
    And the bag of "BO" shows gold 10 and energy 11

  @api @ACT-12
  Scenario: A crate that nobody opened is closed
    Given the clock shows minute 10
    And a new player named "ana"
    When the player goes east
    And the player closes the "CRATE"
    Then the request is refused with status 405 and the message "THE CRATE IS ALREADY CLOSED."

  @api @ACT-10 @ACT-13 @ACT-14
  Scenario: The key unlocks the manhole, and the open manhole adds the way down
    Given the clock shows minute 10
    And a new player named "ana"
    When the player goes north
    And the player goes up
    And the player takes the "KEY"
    And the player goes down
    And the player goes south
    And the player goes east
    And the player goes south
    And the player opens the "MANHOLE"
    Then the request is refused with status 405 and the message "THE MANHOLE IS LOCKED."
    When the player uses the "KEY"
    Then the answer is "YOU UNLOCK THE MANHOLE COVER."
    When the player uses the "KEY"
    Then the answer is "THE MANHOLE COVER IS ALREADY UNLOCKED."
    When the player opens the "MANHOLE"
    Then the answer is "OPENED."
    And the exits are "north, down"
    When the player closes the "MANHOLE"
    Then the answer is "CLOSED."
    And the exits are "north"
    When the player goes down
    Then the request is refused with status 405 and the message "YOU CAN'T GO THAT WAY."

  @api @ACT-13
  Scenario: Through the open manhole, the way up from the katacombs leads back to the back yard
    Given the clock shows minute 10
    And a new player named "ana"
    When the player goes north
    And the player goes up
    And the player takes the "KEY"
    And the player goes down
    And the player goes south
    And the player goes east
    And the player goes south
    And the player uses the "KEY"
    And the player opens the "MANHOLE"
    And the player goes down
    Then the player is at "KATACOMBS"
    And the exits are "east, south, up"
    When the player goes up
    Then the player is at "BACK YARD"

  @api @ACT-13
  Scenario: The open manhole adds the way down for every player
    Given the clock shows minute 10
    And a new player named "ana"
    And a new player named "bo"
    When "ANA" goes north
    And "ANA" goes up
    And "ANA" takes the "KEY"
    And "ANA" goes down
    And "ANA" goes south
    And "ANA" goes east
    And "ANA" goes south
    And "ANA" uses the "KEY"
    And "ANA" opens the "MANHOLE"
    And "BO" goes east
    And "BO" goes south
    And "BO" goes down
    Then "BO" is at "KATACOMBS"

  @api @ACT-15
  Scenario: Bread restores 5 energy, up to 20, and is eaten
    Given a new player named "ana"
    When the player goes west
    And the player takes the "BREAD"
    And the player takes the "BREAD"
    And the player takes the "BREAD"
    And the player uses the "BREAD"
    Then the answer is "YOU EAT THE BREAD. YOU FEEL STRONGER."
    And the bag shows gold 0 and energy 16
    When the player uses the "BREAD"
    Then the bag shows gold 0 and energy 20
    When the player uses the "BREAD"
    Then the bag shows gold 0 and energy 20
    And the bag is empty

  @api @ACT-15
  Scenario: Beer restores 3 energy and is drunk
    Given a new player named "ana"
    When the player goes north
    And the player takes the "BEER"
    And the player uses the "BEER"
    Then the answer is "YOU DRINK THE BEER. YOU FEEL BRAVE."
    And the bag shows gold 5 and energy 14
    And the bag is empty

  @api @ACT-16
  Scenario: The key outside the back yard does nothing
    Given a new player named "ana"
    When the player goes north
    And the player goes up
    And the player takes the "KEY"
    And the player uses the "KEY"
    Then the answer is "NOTHING HAPPENS."
    And the bag holds "KEY"

  @api @BAG-1
  Scenario: The bag shows the items, the gold, the score and the energy
    Given a new player named "ana"
    When the player goes north
    And the player takes the "BEER"
    Then the bag holds "BEER"
    And the bag shows gold 5 and energy 11
    And the bag shows score 5

  @api @BAG-3 @LEGACY-1
  Scenario: A bag of 8 slots, 3 items with the same name per slot, refuses a ninth slot
    # BO brings two BEERs and the KEY to TUNNEL JUNCTION. ANA collects 7
    # slots on the way there: BREAD (3 in one slot), UMBRELLA, FLOWERS,
    # CANDLE, MAP, ROPE, SKULL. Two BEERs fill slot 8; the KEY would be slot 9.
    Given the rat never runs
    And a new player named "bo"
    And a new player named "ana"
    When "BO" goes north
    And "BO" takes the "BEER"
    And "BO" takes the "BEER"
    And "BO" goes up
    And "BO" takes the "KEY"
    And "BO" goes down
    And "BO" goes down
    And "BO" goes down
    And "BO" goes east
    And "BO" drops the "BEER"
    And "BO" drops the "BEER"
    And "BO" drops the "KEY"
    And "ANA" goes west
    And "ANA" takes the "BREAD"
    And "ANA" takes the "BREAD"
    And "ANA" takes the "BREAD"
    And "ANA" takes the "UMBRELLA"
    And "ANA" goes north
    And "ANA" takes the "FLOWERS"
    And "ANA" goes south
    And "ANA" goes east
    And "ANA" goes south
    And "ANA" takes the "CANDLE"
    And "ANA" goes east
    And "ANA" takes the "MAP"
    And "ANA" goes down
    And "ANA" takes the "ROPE"
    And "ANA" goes east
    And "ANA" takes the "SKULL"
    And "ANA" takes the "BEER"
    And "ANA" takes the "BEER"
    Then the answer is "TAKEN."
    When "ANA" takes the "KEY"
    Then the request is refused with status 405 and the message "YOUR BAG IS FULL."
    And the location holds 1 "KEY"
    When "ANA" picks up the "KEY" with the legacy route
    Then the answer is "OK"
    And the bag of "ANA" holds "BREAD, BREAD, BREAD, UMBRELLA, FLOWERS, CANDLE, MAP, ROPE, SKULL, BEER, BEER, KEY"
