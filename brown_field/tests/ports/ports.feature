@acceptance
Feature: The use-case ports answer as the REST routes do, with their own differences
  Each scenario builds a use case as `XUseCase(InMemoryGame())` and calls
  `execute`, as README item 8 describes. The ports return the domain types
  of kata.py and raise the error types of game.py. They show no energy:
  the domain Player has no energy field, and the energy gate (MOVE-5) is in
  the REST route only.

  Background:
    Given a game behind the ports

  @port @PLAYER-1 @PLAYER-2
  Scenario: Registering a player gives a player at BRICK LANE
    When the port registers a player named "  ana "
    Then the port answers a player named "ANA" at "BRICK LANE" who has not won
    And the bag through the port shows gold 0 and score 0

  @port @PLAYER-3 @PLAYER-4
  Scenario Outline: The register port refuses the name "<name>"
    When the port registers a player named "<name>"
    Then the port refuses with InvalidName "<message>"

    Examples:
      | name  | message                                |
      | admin | THIS NAME IS RESERVED.                 |
      |       | THE NAME MUST HAVE 1 TO 50 CHARACTERS. |

  @port @PLAYER-5
  Scenario: The register port refuses the 21st player
    Given the port has registered 20 players
    When the port registers a player named "late"
    Then the port refuses with NotAllowed "THE KATACOMBS ARE FULL. TRY AGAIN LATER."

  @port @PLAYER-6
  Scenario: The list port gives every active player
    Given the port has registered a player named "ana"
    And the port has registered a player named "bo"
    When the port lists the players
    Then the port lists "ANA, BO"

  @port @PLAYER-7 @PLAYER-9
  Scenario: After the quit port, the player is not found
    Given the port has registered a player named "ana"
    When the port quits the player
    And the port looks around
    Then the port refuses the unknown player with PlayerNotFound

  @port @LOOK-1 @LOOK-2 @LOOK-3
  Scenario: The look ports show the location and the one through an exit
    Given the port has registered a player named "ana"
    When the port looks around
    Then the port answers the location "BRICK LANE"
    When the port looks north
    Then the port answers the location "OLD TRUMAN BREWERY"
    When the port looks up
    Then the port refuses with NotAllowed "THERE IS NOTHING IN THAT DIRECTION."

  @port @MOVE-1 @MOVE-4 @GOLD-1
  Scenario: The move port moves through an exit and refuses a wall
    Given the port has registered a player named "ana"
    When the port moves the player north
    Then the port answers the location "OLD TRUMAN BREWERY"
    And the bag through the port shows gold 5 and score 5
    When the port moves the player west
    Then the port refuses with NotAllowed "YOU CAN'T GO THAT WAY."

  @port @MOVE-5
  Scenario: The move port refuses a tired player
    # A new player has 12 energy. The 13th move is refused at the port, as it
    # is over REST (decision 0011: the gate is at the port, at 0).
    Given the port has registered a player named "ana"
    When the port moves the player north and south 6 times
    And the port moves the player north
    Then the port refuses with NotAllowed "YOU ARE TOO TIRED TO MOVE. EAT OR DRINK SOMETHING."

  @port @MOVE-6
  Scenario Outline: The move port follows the market clock: minute <minute>
    Given the port has registered a player named "ana"
    And the clock shows minute <minute>
    When the port moves the player east
    Then the port <result>

    Examples:
      | minute | result                                                                                |
      | 49     | answers the location "SPITALFIELDS MARKET"                                            |
      | 50     | refuses with NotAllowed "THE MARKET IS CLOSED FOR CLEANING. COME BACK LATER."         |

  @port @ITEM-1 @ITEM-2
  Scenario: The item port inspects an item, and refuses an unknown one
    Given the port has registered a player named "ana"
    When the port moves the player north
    And the port inspects the item "BEER" here
    Then the port answers the item "BEER" with the value 0 and the actions "pick, drop, use"
    When the port inspects the item sid "unknown"
    Then the port refuses with ItemNotFound "ITEM unknown NOT FOUND."

  @port @ACT-4 @ACT-5 @ACT-6 @ACT-7
  Scenario: The use port takes, takes again, drops, and refuses a drop of an item not carried
    Given the port has registered a player named "ana"
    When the port moves the player north
    And the port takes the "BEER"
    Then the port answers "TAKEN."
    When the port takes the same item again
    Then the port answers "TAKEN."
    And the bag through the port holds "BEER"
    When the port drops the "BEER"
    Then the port answers "DROPPED."
    When the port drops the same item again
    Then the port refuses with NotAllowed "YOU ARE NOT CARRYING THE BEER."

  @port @ACT-2 @ACT-15
  Scenario: The use port refuses an action the item lacks, and a beer is drunk
    Given the port has registered a player named "ana"
    When the port moves the player north
    And the port opens the "BEER"
    Then the port refuses with NotAllowed "YOU CAN'T OPEN THE BEER."
    When the port takes the "BEER"
    And the port uses the "BEER"
    Then the port answers "YOU DRINK THE BEER. YOU FEEL BRAVE."
    And the bag through the port holds ""

  @port @WIN-1 @BAG-2 @MOVE-7
  Scenario: The move port wins at the katacombs exit, then refuses moves
    Given the port has registered a player named "ana"
    When the port moves the player south, east, down, east and north
    And the port takes the "GOBLET"
    And the port moves the player east
    Then the port answers the katacombs exit
    And the player through the port has won
    And the bag through the port shows gold 35 and score 85
    When the port moves the player west
    Then the port refuses with NotAllowed "THE GAME IS OVER. YOU ALREADY FOUND THE EXIT."

  @port @SAVE-1 @SAVE-2
  Scenario: The save port answers the path, and a new game reads the save
    Given the port has registered a player named "ana"
    When the port moves the player north
    And the port saves the game
    Then the port answers the path of the database file
    When a new game starts behind the ports
    And the port looks around
    Then the port answers the location "OLD TRUMAN BREWERY"

  @port @ACCOUNT-1 @ACCOUNT-4 @ACCOUNT-5
  Scenario: The account use cases register and log in
    When the port registers the account "ana@example.org" with the password "pw" and the name "ana"
    And the port logs in as "ana@example.org" with the password "pw"
    Then the port answers a player named "ANA" at "BRICK LANE" who has not won
    When the port logs in as "ana@example.org" with the password "wrong"
    Then the port refuses with NotAllowed "WRONG EMAIL OR PASSWORD."
