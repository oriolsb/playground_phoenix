# Delta — hexagon-10-slim-state

Format adapted from the OpenSpec delta spec (MIT). On archive, the delta
merges into the specification and this file moves to the archive.

## ADDED Rules

#### ARCH-9 — The game state holds no rule and no mapping

- Status: accepted (decision 0020).
- Source: this change; finding F3 of the hexagonal review; decision 0020.
- Rule: Katacombs shall keep in `application/state.py` only the outbound
  ports, the aggregates and their lookups. A game rule shall live in
  `brown_field/domain/`, and the mapping to the view models of `kata.py`
  shall live in `application/views.py`.
- Why: a context object that also holds rules and mappings grows into a
  new god object (decision 0012, "Risks that stay"). Each job then has one
  home.
- Observable result: (1) a fitness function finds in `application/state.py`
  no function or method named `to_*`, no import of the view models
  `Player`, `Bag` or `Location`, and no definition of `market_is_cleaning`
  or `password_hash`. (2) A domain test checks `market_is_cleaning` at
  minutes 49, 50 and 59 with no clock. (3) The tests of MOVE-6 and STORE-3
  pass unchanged.

## Unchanged

- `MOVE-6`: the market closes in minutes 50 to 59 of the server's local time.
- `STORE-3`: the password digest keeps its format. It stays contested.
- `ACCOUNT-5`: a wrong email or password is refused.
