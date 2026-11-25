@acceptance
Feature: The server starts from its configuration and its entry points
  The people who run the server set two environment variables, or rely on
  their defaults. Code starts the server through create_app or app.

  Background:
    Given the working directory is an empty folder

  @CONF-1
  Scenario: Without KATACOMBS_DB, the database file is katacombs.db in the working directory
    Given the environment variables of the files are not set
    And a new player named "ana"
    When the player saves the game
    Then the answer is the save of the path "katacombs.db"
    And the working directory holds the file "katacombs.db"

  @CONF-1
  Scenario: With KATACOMBS_DB, the database file is the one it names
    Given a new player named "ana"
    When the player saves the game
    Then the save answer names the database file
    And the working directory does not hold the file "katacombs.db"

  @CONF-2 @WIN-3
  Scenario: Without KATACOMBS_HIGHSCORES, a win writes highscores.jsonl in the working directory
    Given the environment variables of the files are not set
    And a new player named "ana"
    When the player has won through the tunnels
    Then the working directory holds the file "highscores.jsonl"

  @CONF-3 @ENTRY-2
  Scenario: python -m brown_field serves the API on 127.0.0.1, port 8000
    Given port 8000 on 127.0.0.1 is free
    When a person runs "python -m brown_field"
    Then GET http://127.0.0.1:8000/leaderboard answers 200

  @ENTRY-1
  Scenario: Two servers made from one game share its players
    Given two servers made from one game
    When a player named "ana" starts on the first server
    Then the second server lists the player "ANA"

  @ENTRY-1
  Scenario: Two servers made with no game do not share players
    Given two servers made with no game
    When a player named "ana" starts on the first server
    Then the second server does not list the player "ANA"

  @ENTRY-2
  Scenario: The module brown_field.api holds a ready server
    When a client calls GET /leaderboard on brown_field.api.app
    Then the response status is 200
