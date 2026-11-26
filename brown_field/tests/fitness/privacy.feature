@acceptance
Feature: The email is never public, and a deletion leaves nothing that identifies the person
  Two fitness functions for the need "1. Accounts" (decision 0013). Each
  one plays a full session through the API, then searches what anybody can
  read: the answers of the read routes, and the database file byte by
  byte. The high-score file is out of the deletion search: it keeps the
  name of each win (ACCOUNT-14).

  @fitness @api @ACCOUNT-9
  Scenario: No public answer holds the email
    Given an account "Zed.Private@example.org" with the password "pw" and the name "zedprivate"
    And a new player named "bo"
    When a client logs in as "zed.private@example.org" with the password "pw"
    And the player sends the chat message "hi"
    And the player has won through the tunnels
    And a client changes the name of "Zed.Private@example.org" with the password "pw" to "zedrenamed"
    Then the name answer is "Zed.Private@example.org" named "ZEDRENAMED"
    And the profile of "Zed.Private@example.org" shows the name "ZEDRENAMED", 1 games won
    And no answer of the public read routes holds "Zed.Private@example.org" in any letter case

  @fitness @api @ACCOUNT-13
  Scenario: After a deletion, nothing in the database file or the API identifies the person
    Given an account "zed.unique@example.org" with the password "pw" and the name "zedunique"
    And a new player named "bo"
    When a client logs in as "zed.unique@example.org" with the password "pw"
    And the player sends the chat message "hi"
    And the player saves the game
    And the player has won through the tunnels
    And the player quits
    And a client logs in as "zed.unique@example.org" with the password "pw"
    And a client deletes the account "zed.unique@example.org" with the password "pw"
    Then nothing identifies "zed.unique@example.org", "ZEDUNIQUE" or the player
    When the server restarts
    Then nothing identifies "zed.unique@example.org", "ZEDUNIQUE" or the player
