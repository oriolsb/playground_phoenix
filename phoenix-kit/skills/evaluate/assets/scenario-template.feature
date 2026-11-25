@acceptance
Feature: <One behavior, named as the user sees it>
  <Two or three lines. The rule in plain words, and why it matters.>

  # The givens that every scenario of this file shares. Keep it short.
  Background:
    Given a new game

  # One Rule block for each rule ID. Put the rule ID tag on each scenario:
  # the checker does not pass a tag on a Rule line to its scenarios.
  Rule: BAG-1 — The bag holds at most 10 items

    # Tags: the rule ID, and the way in. @port reaches the published ports.
    # @api reaches the REST contract. A rule that both reach gets both.
    # A data table gives structured data to one step, for example a test world.
    @port @BAG-1
    Scenario: A full bag refuses another item
      Given a world with these items at "BRICK LANE":
        | item   | count |
        | PEBBLE | 11    |
      And Ana carries 10 pebbles
      When Ana takes a pebble
      Then the command is refused with BAG_FULL
      And Ana's bag still holds 10 items

    @api @BAG-1
    Scenario: A full bag gives 409 over the network
      Given a world with 11 pebbles at "BRICK LANE"
      And Ana carries 10 pebbles
      When the client posts a take for a pebble
      Then the status is 409
      And the error reason is BAG_FULL

  Rule: PLAYER-2 — A name has 1 to 30 characters after trimming

    # Gherkin trims each table cell, so a table cannot hold the spaces of a
    # name. Test the trimming with a quoted value in the step instead.
    @port @PLAYER-2
    Scenario: The spaces around a name are removed
      When a person registers with the name "  Priya  "
      Then the player's name is "Priya"

    # Many cases of one rule: an outline with examples tables. The
    # description column says which case each row shows. Named blocks show
    # the edges. A tag on a block selects it: uv run pytest -m edge.
    @port @PLAYER-2
    Scenario Outline: A name of <description> is <result>
      When a person registers with the name "<name>"
      Then the result is <result>

      Examples: Valid names
        | description   | name                           | result     |
        | one character | P                              | registered |
        | 30 characters | aaaaaaaaaaaaaaaaaaaaaaaaaaaaaa | registered |

      @edge
      Examples: Invalid names
        | description   | name                            | result       |
        | no character  |                                 | INVALID_NAME |
        | 31 characters | aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa | INVALID_NAME |

  # An operational limit. Tag it so it runs on its own.
  Rule: OPS-1 — Each command responds in less than 100 ms at p99

    @ops @port @OPS-1
    Scenario: A command responds in less than 100 ms at p99
      Given a registered player
      When 100 look commands run in process
      Then the 99th percentile response time is less than 100 ms

  # A fitness function. It cites the decision it protects.
  Rule: The domain imports no framework (decision 0033)

    @fitness @0033
    Scenario: The domain imports no framework
      When the import checker runs
      Then no module in the domain imports a web framework
