# Phoenix Kit — maintainers

Read this file only when you change the kit. A participant does not need
it. The README is the user guide.

## Add or change a skill

- One skill is one primitive, or one test from the cheat sheet. Three
  skills are the exception: `timeline`, `explain`, and `vocabulary` write
  one reader document and change no primitive. Keep that split when you
  add one.
- Keep a `SKILL.md` under 150 lines. Put templates in `assets/` and long
  reference material in `references/`, one level deep.
- A skill reads `PHOENIX.md` for paths. Do not hard-code a path in a new
  skill.
- A skill that chooses between alternatives tells the user to run
  `/phoenix-kit:decide`. Provenance is recorded at the moment of the
  decision.
- Keep each meaning in one place. The hand-off of a change lives only in
  `skills/change/SKILL.md`, step 4; other files point to it.
- End each step on a check the agent can see: the `— done:` part of each
  checklist line. State each guardrail as the rule to follow.
- Add a grammar to `schemas/README.md` and a command to
  `scripts/phoenix_check.py` before a new artifact crosses two skills. A
  reader document (`timeline`, `explain`, `vocabulary`) is read by a
  person, never by another skill: it needs no grammar and no command.
- Validate from the `phoenix-kit/` folder. The kit has its own
  `pyproject.toml`; a project that holds the kit does not run its tests.
  - `uv run pytest`: the checker unit tests. With no uv,
    `python3 -m unittest discover -s scripts -p "test_*.py"`.
  - `python3 scripts/eval_kit.py`: frontmatter, line budget, links,
    contracts, checker commands, presets, tests.
  - `claude plugin validate .`
- `uv run pytest` creates `.venv/` in the kit folder, and the tests make
  `.pytest_cache/` and `__pycache__/`. Delete these three folders before
  you copy or package the kit. The workshop packaging rejects a kit that
  holds `.venv/`.

## Known exceptions

- Decision records use sequential `NNNN` numbers, as the workshop
  templates do. Pedro's L3 Law prefers a timestamp and a slug for teams
  on parallel branches. `decide` says when to switch.
