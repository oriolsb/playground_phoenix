@fitness
Feature: The shape of the code behind the boundary
  The rules of the section "Structure" of the Specification, and the port
  tier of ENTRY-3. A caller of the REST API does not see them. A
  regeneration must keep them. Each scenario runs one check of
  test_structure.py; the planted-break tests there show that each check can fail.

  @ARCH-1
  Scenario: Each layer imports only the layers inside it
    Then the structure check "layers" finds no break

  @ARCH-2
  Scenario: Each use case satisfies its port
    Then the structure check "ports" finds no break

  @ARCH-3
  Scenario: Only adapters read the clock, draw chance or open files
    Then the structure check "outside world" finds no break

  @ARCH-4
  Scenario: Only the SQLite adapter imports sqlite3
    Then the structure check "sqlite" finds no break

  @ARCH-5
  Scenario: The REST adapter holds no rule and changes no state
    Then the structure check "rest state" finds no break

  @ARCH-6
  Scenario: A world with a missing way back refuses to build
    Then the structure check "world source" finds no break

  @ARCH-7
  Scenario: The domain imports nothing outside the domain
    Then the structure check "domain" finds no break

  @ARCH-8
  Scenario: The REST adapter imports only the ports
    Then the structure check "rest imports" finds no break

  @ARCH-9
  Scenario: The game state holds no rule and no mapping
    Then the structure check "state" finds no break

  @ENTRY-3
  Scenario: The port tier offers a use case for each command
    Then the structure check "port tier" finds no break

  @ARCH-10
  Scenario: A driven adapter imports only the outbound ports and the domain
    Then the structure check "driven adapters" finds no break
