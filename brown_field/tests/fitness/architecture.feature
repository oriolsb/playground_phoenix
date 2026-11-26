@acceptance
Feature: The game rules sit in a core with no I/O, behind a REST adapter with no rule
  The target of change modular-core (decision 0012). A new feature, a new
  store or a test replaces an adapter without editing a rule, and a second
  adapter reuses the rules as they are. These checks read the source; they
  have no way in through a port or the API.

  @fitness @architecture @OPS-2
  Scenario: The core defines every use case of the port tier
    When the architecture check reads the core
    Then each use case of the port tier is defined in a core module

  @fitness @architecture @OPS-2
  Scenario: No core module does I/O
    When the architecture check reads the core
    Then no core module imports an I/O or web module
    And no core module opens a file or reads the clock

  @fitness @architecture @OPS-3
  Scenario: The REST adapter reads no game state
    When the architecture check reads the REST adapter
    Then the REST adapter reads no attribute of the game

  @fitness @architecture @OPS-3
  Scenario: Each route answers through a use case
    When the architecture check reads the REST adapter
    Then each route of the REST adapter calls a use case
