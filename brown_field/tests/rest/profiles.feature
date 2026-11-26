@acceptance
Feature: Each account has a public profile
  A profile shows an account's name, its games won and its best score.
  Anybody can read it by its profile sid, with no credential. It never
  shows the email. The wins it counts are kept with the account, so they
  survive a restart; the leaderboard does not.

  @api @ACCOUNT-8
  Scenario: Anybody can read a profile with no win
    Given an account "ana@example.org" with the password "pw" and the name "ana"
    When a client reads the profile of "ana@example.org"
    Then the profile shows the name "ANA", 0 games won and the best score none

  @api @ACCOUNT-10 @ACCOUNT-8
  Scenario: A win of an account's player counts for its profile
    # The tunnel route gives 35 gold in 6 moves.
    Given an account "ana@example.org" with the password "pw" and the name "ana"
    When a client logs in as "ana@example.org" with the password "pw"
    And the player has won through the tunnels
    And a client reads the profile of "ana@example.org"
    Then the profile shows the name "ANA", 1 game won and the best score 35

  @api @ACCOUNT-10
  Scenario: The profile keeps its wins after a restart, and the leaderboard does not
    Given an account "ana@example.org" with the password "pw" and the name "ana"
    When a client logs in as "ana@example.org" with the password "pw"
    And the player has won through the tunnels
    And the server restarts
    And a client reads the profile of "ana@example.org"
    Then the profile shows the name "ANA", 1 game won and the best score 35
    And the leaderboard is empty

  @api @ACCOUNT-10
  Scenario: A win of a player with no account counts for no profile
    Given an account "ana@example.org" with the password "pw" and the name "ana"
    And a new player named "ana"
    When the player has won through the tunnels
    And a client reads the profile of "ana@example.org"
    Then the profile shows the name "ANA", 0 games won and the best score none

  @api @WIN-2 @ACCOUNT-10
  Scenario: The leaderboard links a win to the winner's profile, or to none
    Given an account "ana@example.org" with the password "pw" and the name "ana"
    And a new player named "bo"
    When "BO" has won through the tunnels
    And a client logs in as "ana@example.org" with the password "pw"
    And the player has won through the tunnels
    Then the leaderboard shows "ANA" with score 35 and 6 moves for the profile of "ana@example.org"
    And the leaderboard shows "BO" with score 35 and 6 moves with no profile

  @api @ACCOUNT-16
  Scenario: An unknown profile sid is not found
    When a client reads the profile sid "000000-000000000000-00000000"
    Then the profile sid "000000-000000000000-00000000" is not found

  @api @ACCOUNT-16
  Scenario: A player sid is not a profile sid
    Given a new player named "ana"
    When a client sends GET /profiles/{sid} with the body -
    Then the player sid is not found as a profile sid
