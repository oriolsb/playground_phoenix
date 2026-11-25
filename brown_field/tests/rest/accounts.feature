@acceptance
Feature: Accounts keep a person's game across quits and restarts
  An account is an email, a password and a name. A login gives the
  account's player: the snapshot of its last quit, else its active player,
  else a new player.

  @api @ACCOUNT-1 @PLAYER-2
  Scenario: A client registers an account
    When a client registers "ana@example.org" with the password "pw" and the name " ana "
    Then the account answer is "ana@example.org" named "ANA"

  @api @ACCOUNT-2
  Scenario: An email without @ is refused
    When a client registers "ana.example.org" with the password "pw" and the name "ana"
    Then the request is refused with status 400 and the message "THE EMAIL IS NOT VALID."

  @api @ACCOUNT-2
  Scenario: An email with more than one @ is accepted
    # The only check is that an @ is in the email (game.py:780).
    When a client registers "ana@example@org" with the password "pw" and the name "ana"
    Then the account answer is "ana@example@org" named "ANA"

  @api @ACCOUNT-2 @PLAYER-3
  Scenario: The email check comes before the name check
    When a client registers "ana.example.org" with the password "pw" and the name ""
    Then the request is refused with status 400 and the message "THE EMAIL IS NOT VALID."

  @api @ACCOUNT-3
  Scenario: An email has one account
    Given an account "ana@example.org" with the password "pw" and the name "ana"
    When a client registers "ana@example.org" with the password "other" and the name "bo"
    Then the request is refused with status 405 and the message "THIS EMAIL IS TAKEN."

  @api @PLAYER-3 @ACCOUNT-1
  Scenario Outline: An account name of 1 to 50 characters is accepted: <length> characters
    When a client registers "ana@example.org" with the password "pw" and the name "<name>"
    Then the account answer is "ana@example.org" named "<name>"

    Examples:
      | length | name |
      | 1      | A    |
      | 50     | XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX |

  @api @PLAYER-3 @PLAYER-4
  Scenario Outline: An account name follows the player name rules: "<name>"
    When a client registers "ana@example.org" with the password "pw" and the name "<name>"
    Then the request is refused with status 400 and the message "<message>"

    Examples:
      | name  | message                                 |
      | admin | THIS NAME IS RESERVED.                  |
      |       | THE NAME MUST HAVE 1 TO 50 CHARACTERS.  |

  @api @ACCOUNT-4
  Scenario: The first login gives a new player at BRICK LANE
    Given an account "ana@example.org" with the password "pw" and the name "ana"
    When a client logs in as "ana@example.org" with the password "pw"
    Then the new player is named "ANA" at "BRICK LANE" with energy 12

  @api @ACCOUNT-4
  Scenario: A login while the player is active gives the same player where it stands
    Given an account "ana@example.org" with the password "pw" and the name "ana"
    When a client logs in as "ana@example.org" with the password "pw"
    And the player goes north
    And a client logs in as "ana@example.org" with the password "pw"
    Then the answer names the same player as before
    And the player is at "OLD TRUMAN BREWERY"

  @api @ACCOUNT-5
  Scenario Outline: A wrong <case> is refused with one message
    Given an account "ana@example.org" with the password "pw" and the name "ana"
    When a client logs in as "<email>" with the password "<password>"
    Then the request is refused with status 405 and the message "WRONG EMAIL OR PASSWORD."

    Examples:
      | case     | email           | password |
      | password | ana@example.org | wrong    |
      | email    | bo@example.org  | pw       |

  @api @ACCOUNT-6 @PLAYER-8
  Scenario: A login after a quit restores the snapshot
    Given an account "ana@example.org" with the password "pw" and the name "ana"
    When a client logs in as "ana@example.org" with the password "pw"
    And the player goes north
    And the player takes the "BEER"
    And the player quits
    And a client logs in as "ana@example.org" with the password "pw"
    Then the answer names the same player as before
    And the player is at "OLD TRUMAN BREWERY"
    And the bag holds "BEER"
    And the bag shows gold 5 and energy 11

  @api @ACCOUNT-4 @ACCOUNT-6 @contested
  Scenario: A second login after a quit rolls the active player back to the snapshot
    # The snapshot is kept after the login that restores it, so each later
    # login restores it again (game.py:804-819).
    Given an account "ana@example.org" with the password "pw" and the name "ana"
    When a client logs in as "ana@example.org" with the password "pw"
    And the player goes north
    And the player quits
    And a client logs in as "ana@example.org" with the password "pw"
    And the player goes up
    And a client logs in as "ana@example.org" with the password "pw"
    Then the player is at "OLD TRUMAN BREWERY"
    And the bag shows gold 5 and energy 11

  @api @PLAYER-5 @ACCOUNT-4
  Scenario: A login without an active player is refused when the game is full
    Given an account "ana@example.org" with the password "pw" and the name "ana"
    And 20 players are in the game
    When a client logs in as "ana@example.org" with the password "pw"
    Then the request is refused with status 405 and the message "THE KATACOMBS ARE FULL. TRY AGAIN LATER."

  @api @ACCOUNT-1 @ACCOUNT-4
  Scenario: An account survives a restart of the server
    Given an account "ana@example.org" with the password "pw" and the name "ana"
    When the server restarts
    And a client logs in as "ana@example.org" with the password "pw"
    Then the new player is named "ANA" at "BRICK LANE" with energy 12

  @api @ACCOUNT-4 @ACCOUNT-6 @contested
  Scenario: A login that restores a snapshot is refused when the game is full
    Given an account "ana@example.org" with the password "pw" and the name "ana"
    When a client logs in as "ana@example.org" with the password "pw"
    And the player quits
    And 20 players are in the game
    And a client logs in as "ana@example.org" with the password "pw"
    Then the request is refused with status 405 and the message "THE KATACOMBS ARE FULL. TRY AGAIN LATER."

  @api @ACCOUNT-4 @ACCOUNT-6 @contested
  Scenario: A login skips a snapshot at a lost location and gives the saved player
    # game.py:805: a snapshot whose location is not in the world is not restored.
    Given an account "ana@example.org" with the password "pw" and the name "ana"
    When a client logs in as "ana@example.org" with the password "pw"
    And the player goes north
    And the player quits
    And a client logs in as "ana@example.org" with the password "pw"
    And the player goes up
    And the player saves the game
    And the snapshot location of "ana@example.org" is changed to "NOWHERE" in the database
    And the server restarts
    And a client logs in as "ana@example.org" with the password "pw"
    Then the answer names the same player as before
    And the player is at "BREWERY ROOFTOP"

  @api @ACCOUNT-4 @ACCOUNT-6 @contested
  Scenario: A login skips a snapshot at a lost location and, with no saved player, gives a new player
    Given an account "ana@example.org" with the password "pw" and the name "ana"
    When a client logs in as "ana@example.org" with the password "pw"
    And the player goes north
    And the player quits
    And the snapshot location of "ana@example.org" is changed to "NOWHERE" in the database
    And the server restarts
    And a client logs in as "ana@example.org" with the password "pw"
    Then the new player is named "ANA" at "BRICK LANE" with energy 12

  @api @ACCOUNT-4 @ACCOUNT-6 @contested
  Scenario: A restored snapshot keeps the visited locations, the opened items, the move count and the win
    Given the clock shows minute 10
    And an account "ana@example.org" with the password "pw" and the name "ana"
    When a client logs in as "ana@example.org" with the password "pw"
    And the player goes north
    And the player goes south
    And the player goes east
    And the player opens the "CRATE"
    And the player closes the "CRATE"
    And the player quits
    And a client logs in as "ana@example.org" with the password "pw"
    And the player opens the "CRATE"
    Then the answer is "OPENED."
    When the player goes west
    And the player goes north
    Then the bag shows gold 15 and energy 7
    When the player goes south
    And the player has won through the tunnels
    Then the leaderboard shows "ANA" with score 50 and 15 moves
    When the player quits
    And a client logs in as "ana@example.org" with the password "pw"
    Then the player has won
