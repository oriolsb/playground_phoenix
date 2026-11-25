@acceptance
Feature: Players chat with the players at the same location
  A chat message belongs to the location it was sent from. Sending one
  counts as a command.

  @api @CHAT-1
  Scenario: A player sends a chat message
    Given a new player named "ana"
    When the player sends the chat message "hello"
    Then the response is 201 with the body {"message": "SENT."}

  @api @CHAT-1 @contested
  Scenario: An empty chat message is accepted
    Given a new player named "ana"
    When the player sends the chat message ""
    Then the response is 201 with the body {"message": "SENT."}
    When the player reads the chat
    Then the chat shows "ANA: "

  @api @CHAT-2
  Scenario: The players at the location read its messages, oldest first
    Given a new player named "ana"
    And a new player named "bo"
    When "ANA" sends the chat message "hi"
    And "BO" sends the chat message "hello ana"
    And "BO" reads the chat
    Then the chat shows "ANA: hi; BO: hello ana"

  @api @CHAT-2
  Scenario: A message stays with the location it was sent from
    Given a new player named "ana"
    And a new player named "bo"
    When "ANA" sends the chat message "hi"
    And "BO" goes north
    And "BO" reads the chat
    Then the chat is empty
    When "ANA" goes north
    And "ANA" reads the chat
    Then the chat is empty
    When "BO" goes south
    And "BO" reads the chat
    Then the chat shows "ANA: hi"

  @api @CHAT-3 @MOVE-3
  Scenario: Each chat message adds one to the move count
    # 6 moves on the tunnel route + 2 chat messages = 8.
    Given a new player named "ana"
    When the player sends the chat message "one"
    And the player sends the chat message "two"
    And the player has won through the tunnels
    Then the leaderboard shows "ANA" with score 35 and 8 moves
