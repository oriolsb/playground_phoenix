@acceptance
Feature: A person changes the name of the account, or deletes it
  Both commands take the account's email and password, as a login does.
  A change of name follows the name rules. A deletion removes what
  identifies the person; the account's wins stay on the leaderboard as
  DELETED PLAYER.

  # --- Proof of ownership ----------------------------------------------------------

  @api @ACCOUNT-12
  Scenario Outline: A <command> with a wrong <case> is refused, and changes nothing
    Given an account "ana@example.org" with the password "pw" and the name "ana"
    When <step>
    Then the request is refused with status 405 and the message "WRONG EMAIL OR PASSWORD."
    When a client reads the profile of "ana@example.org"
    Then the profile shows the name "ANA", 0 games won and the best score none

    Examples:
      | command        | case     | step                                                                         |
      | change of name | password | a client changes the name of "ana@example.org" with the password "wrong" to "bob" |
      | change of name | email    | a client changes the name of "bo@example.org" with the password "pw" to "bob"     |
      | deletion       | password | a client deletes the account "ana@example.org" with the password "wrong"          |
      | deletion       | email    | a client deletes the account "bo@example.org" with the password "pw"              |

  # --- Change the name -------------------------------------------------------------

  @api @ACCOUNT-11 @PLAYER-2
  Scenario: A person changes the name of the account
    Given an account "ana@example.org" with the password "pw" and the name "ana"
    When a client changes the name of "ana@example.org" with the password "pw" to " bob "
    Then the name answer is "ana@example.org" named "BOB"
    When a client reads the profile of "ana@example.org"
    Then the profile shows the name "BOB", 0 games won and the best score none

  @api @ACCOUNT-11 @ACCOUNT-7
  Scenario: A change of name ignores the letter case of the email
    Given an account "ana@example.org" with the password "pw" and the name "ana"
    When a client changes the name of "ANA@EXAMPLE.ORG" with the password "pw" to "bob"
    Then the name answer is "ana@example.org" named "BOB"

  @api @ACCOUNT-11
  Scenario: The active player takes the new name
    Given an account "ana@example.org" with the password "pw" and the name "ana"
    When a client logs in as "ana@example.org" with the password "pw"
    And a client changes the name of "ana@example.org" with the password "pw" to "bob"
    And a client lists the players
    Then the list holds "BOB", each with energy 12

  @api @ACCOUNT-11 @WIN-2 @CHAT-1
  Scenario: Wins and chat messages keep the name they were made with
    Given an account "ana@example.org" with the password "pw" and the name "ana"
    When a client logs in as "ana@example.org" with the password "pw"
    And the player sends the chat message "hello"
    And the player reads the chat
    Then the chat shows "ANA: hello"
    When the player has won through the tunnels
    And a client changes the name of "ana@example.org" with the password "pw" to "bob"
    # The chat message counts as a move (CHAT-3): 6 moves and 1 chat message.
    Then the leaderboard shows "ANA" with score 35 and 7 moves for the profile of "ana@example.org"
    And the profile of "ana@example.org" shows the name "BOB", 1 games won

  @api @ACCOUNT-11 @PLAYER-3 @PLAYER-4
  Scenario Outline: A new name follows the name rules: "<name>"
    Given an account "ana@example.org" with the password "pw" and the name "ana"
    When a client changes the name of "ana@example.org" with the password "pw" to "<name>"
    Then the request is refused with status 400 and the message "<message>"
    When a client reads the profile of "ana@example.org"
    Then the profile shows the name "ANA", 0 games won and the best score none

    Examples:
      | name           | message                                |
      | admin          | THIS NAME IS RESERVED.                 |
      | deleted player | THIS NAME IS RESERVED.                 |
      |                | THE NAME MUST HAVE 1 TO 50 CHARACTERS. |

  # --- The reserved name -----------------------------------------------------------

  @api @PLAYER-4
  Scenario: Nobody can start a game as DELETED PLAYER
    When a client starts a game with the name " deleted player "
    Then the request is refused with status 400 and the message "THIS NAME IS RESERVED."

  @api @PLAYER-4 @ACCOUNT-1
  Scenario: Nobody can register as DELETED PLAYER
    When a client registers "ana@example.org" with the password "pw" and the name "Deleted Player"
    Then the request is refused with status 400 and the message "THIS NAME IS RESERVED."

  # --- Delete the account ----------------------------------------------------------

  @api @ACCOUNT-13
  Scenario: A deleted account can't log in, and its profile is gone
    Given an account "ana@example.org" with the password "pw" and the name "ana"
    When a client deletes the account "ana@example.org" with the password "pw"
    Then the answer is "ACCOUNT DELETED."
    When a client logs in as "ana@example.org" with the password "pw"
    Then the request is refused with status 405 and the message "WRONG EMAIL OR PASSWORD."
    When a client reads the deleted profile of "ana@example.org"
    Then the deleted profile of "ana@example.org" is not found

  @api @ACCOUNT-13 @ACCOUNT-7
  Scenario: A deletion ignores the letter case of the email
    Given an account "ana@example.org" with the password "pw" and the name "ana"
    When a client deletes the account "Ana@Example.org" with the password "pw"
    Then the answer is "ACCOUNT DELETED."
    When a client logs in as "ana@example.org" with the password "pw"
    Then the request is refused with status 405 and the message "WRONG EMAIL OR PASSWORD."

  @api @ACCOUNT-13 @PLAYER-9 @PLAYER-8
  Scenario: A deletion removes the active player, and its bag stays in its location
    Given an account "ana@example.org" with the password "pw" and the name "ana"
    And a new player named "bo"
    When a client logs in as "ana@example.org" with the password "pw"
    And the player goes north
    And the player takes the "BEER"
    And "BO" goes north
    And a client deletes the account "ana@example.org" with the password "pw"
    And the player looks around
    Then the request is refused because the player is unknown
    And the location of "BO" holds 1 "BEER"

  @api @ACCOUNT-13 @CHAT-2
  Scenario: A deletion removes the chat messages of the account's player
    Given an account "ana@example.org" with the password "pw" and the name "ana"
    And a new player named "bo"
    When a client logs in as "ana@example.org" with the password "pw"
    And the player sends the chat message "I am Ana"
    And "BO" sends the chat message "hi"
    And a client deletes the account "ana@example.org" with the password "pw"
    And "BO" reads the chat
    Then the chat shows "BO: hi"

  @api @ACCOUNT-13 @SAVE-2
  Scenario: A deletion removes the save, so a restart does not bring the player back
    Given an account "ana@example.org" with the password "pw" and the name "ana"
    When a client logs in as "ana@example.org" with the password "pw"
    And the player saves the game
    And a client deletes the account "ana@example.org" with the password "pw"
    And the server restarts
    And the player looks around
    Then the request is refused because the player is unknown

  @api @ACCOUNT-13 @ACCOUNT-6
  Scenario: A deletion removes the snapshot of the last quit
    Given an account "ana@example.org" with the password "pw" and the name "ana"
    When a client logs in as "ana@example.org" with the password "pw"
    And the player goes north
    And the player quits
    And a client deletes the account "ana@example.org" with the password "pw"
    And a client registers "ana@example.org" with the password "pw" and the name "ana"
    And a client logs in as "ana@example.org" with the password "pw"
    Then the new player is named "ANA" at "BRICK LANE" with energy 12

  @api @ACCOUNT-14 @BOARD-1
  Scenario: A deleted account's wins stay on the leaderboard as DELETED PLAYER, in their rank
    Given an account "ana@example.org" with the password "pw" and the name "ana"
    And a new player named "bo"
    When a client logs in as "ana@example.org" with the password "pw"
    And the player has won through the tunnels
    And "BO" has won through the tunnels
    And a client deletes the account "ana@example.org" with the password "pw"
    Then the leaderboard lists "DELETED PLAYER, BO" in this order
    And the leaderboard shows "DELETED PLAYER" with score 35 and 6 moves with no profile

  @api @ACCOUNT-14 @WIN-3
  Scenario: A deletion leaves the high-score file as it was
    # No marketing support for these features (review of 2026-11-26).
    Given an account "ana@example.org" with the password "pw" and the name "ana"
    When a client logs in as "ana@example.org" with the password "pw"
    And the player has won through the tunnels
    And the high-score file is noted
    And a client deletes the account "ana@example.org" with the password "pw"
    Then the answer is "ACCOUNT DELETED."
    And the high-score file is byte for byte as noted
    And the high-score file holds one line for "ANA" with score 35

  @api @ACCOUNT-15
  Scenario: The email of a deleted account registers again, with a new and empty profile
    Given an account "ana@example.org" with the password "pw" and the name "ana"
    When a client logs in as "ana@example.org" with the password "pw"
    And the player has won through the tunnels
    And a client deletes the account "ana@example.org" with the password "pw"
    And a client registers "ana@example.org" with the password "new" and the name "ana"
    Then the account answer is "ana@example.org" named "ANA"
    And the profile of "ana@example.org" differs from the deleted one
    When a client reads the profile of "ana@example.org"
    Then the profile shows the name "ANA", 0 games won and the best score none
