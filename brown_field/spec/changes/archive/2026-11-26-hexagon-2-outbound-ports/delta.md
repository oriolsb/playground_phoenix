# Delta — hexagon-2-outbound-ports

Format adapted from the OpenSpec delta spec (MIT). On archive, the delta
merges into the specification and this file moves to the archive.

## ADDED Rules

#### ARCH-3 — The game reads the time, draws chance and writes high scores through outbound ports

- Status: accepted (decision 0013).
- Source: this change; decisions 0008 and 0013.
- Rule: Katacombs shall read the time only through the port `Clock`,
  draw random numbers only through the port `RandomSource`, and append
  high-score lines only through the port `HighScoreSink`. Where
  `InMemoryGame` gets no adapter for one of these ports, Katacombs shall
  use the default adapter, which calls `datetime.now()`, the functions of
  the module `random`, or the file of CONF-2, at the moment of each call.
- Why: a rule that calls the standard library directly can be faked only
  by patching the standard library. A port lets a test or a new adapter
  give the time or the chance directly. The default adapters keep the
  seams of decision 0008, so the tests of today still control the clock
  and the rat.
- Observable result: (1) a fitness function finds no call to
  `datetime.now`, `random.` or `open(` under `brown_field/domain/` and
  `brown_field/application/`. (2) A game built with a fixed clock at
  minute 55 refuses a move into SPITALFIELDS MARKET, and one at minute 10
  allows it, with no `time_machine`. (3) A game built with a random source
  that answers 0.0 lets the rat steal, as MOVE-8 says. (4) The harness
  tests (`tests/harness/`) pass unchanged.

## Other changes to the specification

### Data ownership: the row "High-score file"

| High-score file (`KATACOMBS_HIGHSCORES`, JSON lines) | game-server (win), through the port `HighScoreSink` | the nightly marketing job, outside this repository |

## Unchanged

- `MOVE-6`: the market closes in minutes 50 to 59, read from the clock port.
- `MOVE-8`: the rat steals with a chance of 1 in 5, drawn from the random port.
- `PLAYER-1`: the sid keeps its digit form and its uniqueness.
- `WIN-3`: the high-score line keeps its three fields and its format.
- `CONF-2`: the high-score file keeps its variable and its default.
- `ENTRY-1`: `create_app()` with no game still builds a game with the default adapters.
