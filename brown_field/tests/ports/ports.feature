@acceptance
Feature: The use-case ports answer as the REST routes do, with their own differences
  Each scenario builds a use case as `XUseCase(InMemoryGame())` and calls
  `execute`, as README item 8 describes. The ports return the domain types
  of kata.py and raise the error types of game.py. The bag carries the
  energy (ENTRY-5), and the energy gate (MOVE-5) is in the move port
  (decision 0011).

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
    # 12 moves spend the start energy of 12; the 13th is refused, as over REST.
    Given the port has registered a player named "ana"
    When the port moves the player north and south 6 times
    Then the port answers the location "BRICK LANE"
    And the bag through the port shows energy 0
    When the port moves the player north
    Then the port refuses with NotAllowed "YOU ARE TOO TIRED TO MOVE. EAT OR DRINK SOMETHING."
    And the bag through the port shows energy 0

  @port @ENTRY-5 @MOVE-2
  Scenario: The bag through the port shows the energy
    Given the port has registered a player named "ana"
    Then the port answers a player with energy 12
    When the port moves the player north
    Then the bag through the port shows energy 11

  @port @ENTRY-3 @CHAT-1 @CHAT-2
  Scenario: The chat ports send and read the messages of the location
    Given the port has registered a player named "ana"
    And the port has registered a player named "bo"
    When the port sends the chat message "hello"
    Then the port answers "SENT."
    When the player "ANA" moves north through the port
    And the player "ANA" reads the chat through the port
    Then the port answers the chat messages ""
    When the player "BO" reads the chat through the port
    Then the port answers the chat messages "BO: hello"

  @port @ENTRY-3 @LEGACY-1 @LEGACY-2
  Scenario: The legacy pickup port takes an item here, and changes nothing elsewhere
    Given the port has registered a player named "ana"
    When the port picks up the item "BEER" of "OLD TRUMAN BREWERY" the legacy way
    Then the port answers "OK"
    And the bag through the port holds ""
    When the port moves the player north
    And the port picks up the item "BEER" of "OLD TRUMAN BREWERY" the legacy way
    Then the port answers "OK"
    And the bag through the port holds "BEER"

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

  @port @WIN-1 @BAG-2 @MOVE-7 @ENTRY-3 @BOARD-1
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
    When the port shows the leaderboard
    Then the port answers the finished games "ANA 85"

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

  @port @ENTRY-6 @SAVE-1 @SAVE-2 @WIN-3
  Scenario: A game on in-memory stores saves, restarts and records a win, and writes no file
    Given the game behind the ports runs on in-memory stores
    And the port has registered a player named "ana"
    When the port moves the player north
    And the port saves the game
    And a new game starts on the same stores
    And the port looks around
    Then the port answers the location "OLD TRUMAN BREWERY"
    When the port moves the player south, south, east, down, east and north
    And the port takes the "GOBLET"
    And the port moves the player east
    Then the port answers the katacombs exit
    And the high-score sink holds "ANA"
    And no file is written

  @port @ENTRY-6 @ACCOUNT-4 @ACCOUNT-6
  Scenario: A game on in-memory stores keeps an account and its snapshot across a restart
    Given the game behind the ports runs on in-memory stores
    When the port registers the account "ana@example.org" with the password "pw" and the name "ana"
    And the port logs in as "ana@example.org" with the password "pw"
    And the port moves the player north
    And the port quits the player
    And a new game starts on the same stores
    And the port logs in as "ana@example.org" with the password "pw"
    Then the port answers a player named "ANA" at "OLD TRUMAN BREWERY" who has not won
    And no file is written

  @port @ENTRY-7 @MOVE-6
  Scenario Outline: The move port reads the clock it is given: minute <minute>
    Given the game behind the ports runs on a clock fixed at minute <minute>
    And the port has registered a player named "ana"
    When the port moves the player east
    Then the port <result>

    Examples:
      | minute | result                                                                        |
      | 49     | answers the location "SPITALFIELDS MARKET"                                    |
      | 55     | refuses with NotAllowed "THE MARKET IS CLOSED FOR CLEANING. COME BACK LATER." |

  @port @ENTRY-7 @MOVE-8
  Scenario: The move port reads the chance it is given: the rat always steals
    Given the game behind the ports runs on a random source that always answers 0
    And the port has registered a player named "ana"
    When the port moves the player north
    And the port takes the "BEER"
    And the port moves the player down
    Then the location through the port ends with "A RAT RUNS OFF WITH YOUR BEER."
    And the bag through the port holds ""

  @port @WORLD-3 @ACT-15
  Scenario: A world given to the game plays a new location and a new food item with no code change
    Given the game behind the ports runs on the world file with a pantry up from BRICK LANE
    And the port has registered a player named "ana"
    When the port moves the player up
    Then the port answers the location "PANTRY"
    When the port takes the "APPLE"
    And the port uses the "APPLE"
    Then the port answers "YOU EAT THE APPLE."
    And the bag through the port shows energy 13

  @port @WORLD-3 @WORLD-2
  Scenario: A world given to the game with an exit that has no way back is refused at the start
    When a game starts behind the ports on the world file where BRICK LANE goes up to KATACOMBS EXIT
    Then the start is refused with "BRICK LANE goes up to KATACOMBS EXIT, but KATACOMBS EXIT does not go down back"
