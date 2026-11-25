@acceptance
Feature: Each command responds fast enough for a player
  Players expect instant feedback. The limit is measured in process, so it
  checks the game's own work, not the network.

  # Live tier: production monitoring must check the same limit against real
  # traffic. This scenario simulates it in process.
  @fitness @ops @api @OPS-1
  Scenario: A mix of 100 commands responds in less than 100 ms at p99
    When 100 commands run in process
    Then the 99th percentile response time is less than 100 ms
