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

  @STORE-3
  Scenario: A password is stored as its unsalted SHA-256 digest
    When a client registers "ana@example.org" with the password "golden-password" and the name "ana"
    And a client registers "bo@example.org" with the password "golden-password" and the name "bo"
    Then the stored password of "ana@example.org" is "f1b580fcec5d45d1ad840f4e3409d1c5ed1fa6fe8dae3ad0e70e923c67f131dd"
    And the stored password of "bo@example.org" is "f1b580fcec5d45d1ad840f4e3409d1c5ed1fa6fe8dae3ad0e70e923c67f131dd"
