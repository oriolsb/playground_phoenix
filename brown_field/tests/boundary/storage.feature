@acceptance
Feature: The database file keeps its shape for every saved player and account
  Real saves and accounts live in the database file. These scenarios read
  the file as another version of the server would: by its tables and
  columns, not through the code that wrote it.

  @STORE-1
  Scenario: A save writes one row to the saves table
    Given a new player named "ana"
    When the player saves the game
    Then the database table "saves" has the columns "player_sid, name, payload, saved_at"
    And the saves table holds one row for the player, named "ANA"
    And the saved time of the player is UTC to the second

  @STORE-1
  Scenario: A second save replaces the row of the player
    Given a new player named "ana"
    When the player saves the game
    And the player goes north
    And the player saves the game
    Then the saves table holds one row for the player, named "ANA"
    And the saved location of the player is "OLD TRUMAN BREWERY"

  @STORE-2
  Scenario: An account row fills in as the account is used
    When a client registers "ana@example.org" with the password "pw" and the name "ana"
    Then the database table "accounts" has the columns "email, password_hash, name, player_sid, snapshot"
    And the account row of "ana@example.org" has no player and no snapshot
    When a client logs in as "ana@example.org" with the password "pw"
    Then the account row of "ana@example.org" names the player and has no snapshot
    When the player quits
    Then the account row of "ana@example.org" has a snapshot at "BRICK LANE"

  @STORE-2 @ACCOUNT-6
  Scenario: A quit writes the snapshot to the account of that player only
    # game.py:442-446 finds the account by its player sid, among all accounts.
    When a client registers "ana@example.org" with the password "pw" and the name "ana"
    And a client registers "bo@example.org" with the password "pw" and the name "bo"
    And a client logs in as "bo@example.org" with the password "pw"
    And "BO" goes north
    And a client logs in as "ana@example.org" with the password "pw"
    And "BO" quits
    Then the account row of "ana@example.org" names the player and has no snapshot
    And the account row of "bo@example.org" has a snapshot at "OLD TRUMAN BREWERY"

  @STORE-3
  Scenario: A password is stored as its unsalted SHA-256 digest
    When a client registers "ana@example.org" with the password "golden-password" and the name "ana"
    And a client registers "bo@example.org" with the password "golden-password" and the name "bo"
    Then the stored password of "ana@example.org" is "f1b580fcec5d45d1ad840f4e3409d1c5ed1fa6fe8dae3ad0e70e923c67f131dd"
    And the stored password of "bo@example.org" is "f1b580fcec5d45d1ad840f4e3409d1c5ed1fa6fe8dae3ad0e70e923c67f131dd"

  @STORE-4 @ACCOUNT-1
  Scenario: A registration writes a row to the profiles table
    When a client registers "ana@example.org" with the password "pw" and the name "ana"
    Then the database table "profiles" has the columns "email TEXT, profile_sid TEXT"
    And the profiles table holds the profile sid of "ana@example.org"

  @STORE-4 @ACCOUNT-10
  Scenario: A win of an account's player writes a row to the wins table
    Given an account "ana@example.org" with the password "pw" and the name "ana"
    When a client logs in as "ana@example.org" with the password "pw"
    And the player has won through the tunnels
    Then the database table "wins" has the columns "email TEXT, name TEXT, at TEXT, score INTEGER, moves INTEGER"
    And the wins table holds one win of "ana@example.org" named "ANA" with score 35 and 6 moves, at a UTC second

  @STORE-4
  Scenario: A win of a player with no account writes no row to the wins table
    Given a new player named "bo"
    When the player has won through the tunnels
    Then the wins table is empty

  @STORE-4 @ACCOUNT-4
  Scenario: A server that starts on a legacy file gives each account a profile sid
    Given the database file of the legacy code, with the golden account
    When a client logs in as "golden@example.org" with the password "golden-password"
    Then the login answer carries a profile sid
    And the profiles table holds that profile sid for "golden@example.org"

  @STORE-4 @ACCOUNT-13
  Scenario: A deletion removes the account's rows from every table
    Given an account "ana@example.org" with the password "pw" and the name "ana"
    When a client logs in as "ana@example.org" with the password "pw"
    And the player saves the game
    And the player has won through the tunnels
    And a client deletes the account "ana@example.org" with the password "pw"
    Then no row of the tables "accounts, profiles, wins" names "ana@example.org"
    And the saves table holds no row for the player
