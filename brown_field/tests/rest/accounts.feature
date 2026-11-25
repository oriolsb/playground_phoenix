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

  @api @ACCOUNT-2 @PLAYER-3
  Scenario: The email check comes before the name check
    When a client registers "ana.example.org" with the password "pw" and the name ""
    Then the request is refused with status 400 and the message "THE EMAIL IS NOT VALID."

  @api @ACCOUNT-3
  Scenario: An email has one account
    Given an account "ana@example.org" with the password "pw" and the name "ana"
    When a client registers "ana@example.org" with the password "other" and the name "bo"
    Then the request is refused with status 405 and the message "THIS EMAIL IS TAKEN."

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
