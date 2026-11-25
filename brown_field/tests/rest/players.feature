@acceptance
Feature: Players start, list and quit games
  A player is one game of one person. The name is cleaned and checked, the
  game holds at most 20 players, and a quit leaves the bag behind.

  @api @PLAYER-2
  Scenario: A name is trimmed and upper case
    When a client starts a game with the name "  ana "
    Then the new player is named "ANA" at "BRICK LANE" with energy 12

  @api @PLAYER-3
  Scenario Outline: A name of <length> characters is <result>
    When a client starts a game with a name of <length> characters
    Then the response status is <status>

    Examples: Valid names
      | length | result   | status |
      | 1      | accepted | 201    |
      | 50     | accepted | 201    |

    Examples: Invalid names
      | length | result  | status |
      | 0      | refused | 400    |
      | 51     | refused | 400    |

  @api @PLAYER-3
  Scenario: A name of only spaces is refused
    When a client starts a game with the name "   "
    Then the request is refused with status 400 and the message "THE NAME MUST HAVE 1 TO 50 CHARACTERS."

  @api @PLAYER-3
  Scenario: A name of 51 characters gets the length message
    When a client starts a game with a name of 51 characters
    Then the request is refused with status 400 and the message "THE NAME MUST HAVE 1 TO 50 CHARACTERS."

  @api @PLAYER-4
  Scenario Outline: The name ADMIN is reserved, written as "<name>"
    When a client starts a game with the name "<name>"
    Then the request is refused with status 400 and the message "THIS NAME IS RESERVED."

    Examples:
      | name  |
      | ADMIN |
      | admin |
      | Admin |

  @api @PLAYER-5
  Scenario: The 21st player is refused, and a quit frees a place
    Given 20 players are in the game
    When a client starts a game with the name "late"
    Then the request is refused with status 405 and the message "THE KATACOMBS ARE FULL. TRY AGAIN LATER."
    When "P1" quits
    And a client starts a game with the name "late"
    Then the new player is named "LATE" at "BRICK LANE" with energy 12

  @api @PLAYER-6
  Scenario: The list of players shows every active player with energy
    Given a new player named "ana"
    And a new player named "bo"
    When a client lists the players
    Then the list holds "ANA, BO", each with energy 12

  @api @PLAYER-7 @PLAYER-9
  Scenario: A player who quits is gone
    Given a new player named "ana"
    When the player quits
    Then the answer is "Game Over"
    When the player looks around
    Then the request is refused because the player is unknown

  @api @PLAYER-8
  Scenario: A quitting player leaves the bag at the location
    Given a new player named "ana"
    When "ANA" goes north
    And "ANA" takes the "BEER"
    And "ANA" goes south
    And "ANA" quits
    And a client starts a game with the name "bo"
    Then the location holds 1 "BEER"

  @api @PLAYER-9
  Scenario Outline: An unknown player sid is not found on <method> <path>
    When a client sends <method> <path> with the body <body>
    Then the request is refused with status 404 and the message "PLAYER 000000-000000000000-00000000 NOT FOUND."

    Examples:
      | method | path                                                       | body              |
      | GET    | /player/000000-000000000000-00000000/location              | -                 |
      | GET    | /player/000000-000000000000-00000000/look/north            | -                 |
      | PUT    | /player/000000-000000000000-00000000/move/north            | -                 |
      | GET    | /player/000000-000000000000-00000000/bag                   | -                 |
      | POST   | /player/000000-000000000000-00000000/save                  | -                 |
      | GET    | /player/000000-000000000000-00000000/chat                  | -                 |
      | POST   | /player/000000-000000000000-00000000/chat                  | {"text": "hi"}    |
      | DELETE | /game/player/000000-000000000000-00000000                  | -                 |
      | PUT    | /player/000000-000000000000-00000000/item/unknown/use/pick | -                 |
      | PUT    | /player/000000-000000000000-00000000/pickup/unknown        | -                 |
