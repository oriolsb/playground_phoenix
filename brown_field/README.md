# Brown Field — The Past

A team built the Katacombs game from the brief. Then the team changed the
game for two years, and did not update the brief. It added a save,
accounts, a chat, and a web client, each one in the code that already
existed. The game has a REST API, so that players can play over the
network, and a web client in a browser. The code works. But the team
left no specification, no tests, no API contract, and no record of their
decisions. Your task is to add the four Phoenix primitives to this
system.

## Goal

At the end of this exercise, you have primitives to generate `game.py`
and `api.py` again, in a separate folder. Step 7 shows how much of the
behavior your primitives hold. Do not delete the original files.

After today, you can:

- find the decisions that live only in legacy code, with an agent and
  without one, and judge which ones nobody can explain;
- pin the current behavior with tests before you change anything;
- show with a regeneration which knowledge your primitives still miss.

The web client is part of the system. A group with a frontend developer
also recovers the primitives of the client, in parallel. A group with no
frontend developer can leave the client out, and use it only to play.

Each person in the group has work today. The agent can draft most of the
tests. A person who does not write code can play the game through the
web client in step 1, and note each surprise. That person can also own
the rules, the open questions, the decision records, and the vocabulary.
The vocabulary gives one meaning to each term. That person checks each
test against its rule.

## What is here

| File | What it is |
| --- | --- |
| [`../docs/katacombs.md`](../docs/katacombs.md) | The original brief that the team built from. It is older than the code. |
| `kata.py` | The domain model and the use-case ports. |
| `game.py` | The implementation: the world, the rules, the accounts, the chat, an in-memory store, and a save to a SQLite file. Since day 3 (decision 0012) it is the composition root, and the code lives in `core/` and `adapters/`. |
| `core/` | Since day 3: the rules, the state and the use cases, with no I/O. Its outbound ports are in `core/ports.py`. |
| `adapters/` | Since day 3: SQLite, the high-score file, the clock, `random` and the password hash. |
| `api.py` | The REST API. |
| `__init__.py` | Makes `brown_field` a package. |
| `__main__.py` | Starts the REST API server. |
| `web/` | The web client: React, TypeScript, and Vite. Players use it to play, to log in, and to chat. |

The code does not always follow the brief. The brief is older than the
code, and it does not answer all questions. The code gives an answer to
each question. Each answer is a decision that nobody wrote down. Find
these decisions. When the brief and the code do not agree, the code shows
what the game does today.

Nobody wrote a contract for the REST API. FastAPI makes `/openapi.json`
and `/docs` from `api.py`. These generated artifacts describe the
implementation after it exists. They are not a Specification. You cannot
regenerate the implementation from them independently.

## Run the game

The system has two parts: the server, and the web client. Start the
server first. The web client needs it.

### The server

In a terminal, from the package root:

```sh
uv sync
uv run python -m brown_field
```

The server runs at `http://127.0.0.1:8000`. Open
`http://127.0.0.1:8000/docs` in a browser to play the game through an
interactive page. You can also use `curl`:

```sh
curl -X POST http://127.0.0.1:8000/game/player \
  -H "Content-Type: application/json" -d '{"name": "Ana"}'
```

To stop the server, press `Ctrl+C`.

### The web client

The web client needs Node.js 24.18 or later (24 LTS or 26). In a second
terminal, from the package root:

```sh
cd brown_field/web
npm ci
npm run dev
```

Open `http://127.0.0.1:5173` in a browser. The development server sends
each request under `/api` to the server on port 8000, so keep the server
running. To stop the web client, press `Ctrl+C`.

Other commands, in `brown_field/web/`:

| Command | What it does |
| --- | --- |
| `npm run build` | Checks the types, and builds the production files in `dist/`. |
| `npm test` | Runs the Vitest tests. |
| `npx playwright test` | Runs the Playwright tests. Run `npx playwright install chromium` once before. |

`npm ci` is needed only once, and again after a change to
`package-lock.json`.

## Where your work goes

Put your primitives in these folders:

| Path | What it holds |
| --- | --- |
| `brown_field/spec/` | The Specification, and the API contract in `openapi.yaml`. |
| `brown_field/decisions/` | The decision records. |
| `brown_field/tests/` | The characterization tests, the contract test, and the fitness function. |
| `brown_field/web/spec/` | The Specification of the web client: its own rules, the routes that it uses, and the names of its controls. |
| `brown_field/web/tests/` | The tests of the web client: component tests, browser tests, and its fitness function. |
| `brown_field/archaeology.md` | The archaeology list of step 1, with your marks. |
| `brown_field/grades.md` | The grades of the primitives in step 3 and step 7, and your answers to the questions of both steps. |
| `brown_field/retrospective.md` | The answers to the retrospective. |

At the end of the day, copy the `brown_field/` folder of this package to
`~/katacombs-results/brown_field/`, to keep your work. Copy the original
code with your primitives, not the regenerated code of step 7.

## Steps

**Timebox:** 4 hours 50 minutes for steps 1 to 7, then a 90-minute retro
block: the retrospective, the comparison, and the close. Each step has its own timebox.

**Minimum path:** if you are late, make the scope smaller. In steps 5 and
6, do only these rules:

- movement,
- take and drop,
- the gold on the first visit to a location,
- the route to the win,
- the save and the restart,
- the routes of the accounts and the chat in the contract, and one
  characterization test for each,
- one error code of each kind.

Item 5 of step 5, the clock seam, can wait: choose a route to the win
that needs no seam. Rules that need a new seam are stretch items. Always
do step 7.
The regeneration shows what your primitives do not have yet.

### 1. Explore

**Timebox:** 25 minutes.

First, make the package folder a git repository. Then you can commit
each step, and step 7 can show what changed. From the package root:

```sh
git init
git add -A
git commit -m "The original legacy system"
```

Then start two agent sessions. They work while you play.

**A one-prompt rewrite.** This is the move that most teams want to make
with legacy code and an agent. Make it now, in a folder outside the
package. Step 7 asks if you would merge it, and how you know. From the
package root:

```sh
R=~/katacombs-workspaces/brown-field-rewrite
mkdir -p $R/brown_field
cp pyproject.toml uv.lock .gitignore $R/
cp brown_field/*.py $R/brown_field/
cd $R
git init -q
git add -A
git commit -qm "the legacy code, before the rewrite"
git tag legacy
```

Start a new LLM session in `$R`, and send this prompt:

```text
This folder holds a legacy game with a REST API, in brown_field/.
Rewrite brown_field/game.py and brown_field/api.py as high-quality,
modern code. Keep the same REST API and the same behavior. Do not
change brown_field/kata.py. Keep create_app and app in
brown_field/api.py. Do not ask me questions. Work until you are done.
```

Do not look at the result yet. Step 7 tests it.

**A read-only archaeology.** In a second session, in the package folder,
send this prompt:

```text
Read brown_field/game.py, brown_field/api.py, brown_field/kata.py, and
brown_field/web/src/. Do not change any file. List each limit, timeout,
retry, special case, magic number, and comment about an old problem.
For each one, give the file and the line, what you think it is for, and
how sure you are: sure, a guess, or no idea. Write the list to
brown_field/archaeology.md, and change no other file.
```

When the archaeology ends, check that it changed no other file. Use a
terminal at the package root, not the terminal of the rewrite. The
output of this command must be empty:

```sh
git diff --stat -- brown_field
```

Do not use `git status` for this check. It also shows the new list, and
the files that the game writes while you play.

The list of the agent does not replace your own list. Your list of
rules and differences from the brief comes from you.

Play the game until you win, through the web client, or through the
REST API. You can also read `game.py` and `api.py`, but this is
optional: the archaeology reads the code first, and step 4 reads it for
the contract. A frontend developer reads `web/src/` in parallel, with
the network tab of the browser open. Write down each rule that you see.
Also write down each place where the code does something that the brief
does not mention.

Example questions:

- Which rules of the brief does the code keep, and which does it change?
- What does the code do when two players use the same thing?
- Does a behavior change from one game to the next? Why?
- Which HTTP status code does each error return?
- Which data leaves the process? Where does it go, and what names the path?
- What survives a restart of the server, and what does not?
- Which rules exist in the web client and in the server? Do they agree?
- Which features share data with the game? What does each one change?

After the play, mark each item of the archaeology list, with the brief
and what you saw in the game:

- **known:** the brief or a comment in the code says why;
- **unknown:** nobody in your group can say why;
- **wrong:** the game or the code shows that the agent's reading is
  wrong.

Count the unknown items. That count is the risk of a rewrite: the
knowledge that only the code holds. A person who does not write code can
do most of this marking.

**Done when:** you won the game once, you have a list of rules and a
list of differences from the brief, the rewrite agent is working, and
the archaeology list is marked. You can finish the marking in step 2.

Also look for the signals in the
[legacy checklist](../docs/cheat-sheet.md#2-the-past--add-phoenix-primitives-to-legacy-code)
of the cheat sheet:

- **The grain:** which unit can you delete and regenerate on its own?
  Gameplay, accounts, and chat: can you separate them?
- **Hybrid components:** a component that mixes storage, data, and game
  rules is difficult to regenerate.
- **Scar tissue:** checks and special cases with no written reason, or
  with a short comment about an old problem. Ask: "What does this code
  know that we have forgotten?"

### 2. The Deletion Test, part 1: the two lists

**Timebox:** 10 minutes. Steps 2 and 3 share 20 minutes.

Do not delete the files. Answer this question: if `game.py` and `api.py`
do not exist, what do you lose? Make two lists:

- What stays: the brief and `kata.py`.
- What you lose: each rule and each decision that exists only in
  `game.py`. You also lose the full API contract, because it exists only
  in `api.py`. You also lose the vocabulary that explains those rules, and
  the names that other code imports from these two files.

If your group recovers the web client, ask the same question about
`web/src/`.

Compare your list of step 1 with the archaeology list. Which items are
only on your list, and which are only on the list of the agent?

Each unknown item of the archaeology goes on the second list. The second
list is your work plan.

**Done when:** you have both lists.

### 3. Grade the four primitives

**Timebox:** 10 minutes.

Give each primitive of the current system a grade: strong, partial, or
absent. For each grade below strong, name the gap. Use
[What good looks like](#what-good-looks-like) as the standard for "strong".

| Primitive | Grade | Gap |
| --- | --- | --- |
| Specification | | |
| Evaluation | | |
| Context Boundary | | |
| Provenance | | |

Write this table in `brown_field/grades.md`. Step 7 adds a second grade
to each row.

Also answer three questions about this system, yes or no, with one line
of evidence each. Together, they say if you can trust a change of an
agent.

1. Can you merge a change that an agent made, without reading every
   line?
2. Can an agent implement a change from one prompt, with no corrective
   prompts?
3. Can you release the change without anyone watching production?

A "partly" is a no. Step 7 asks the three questions again.

**Done when:** `brown_field/grades.md` has a grade and a gap for each
primitive, and the three answers.

### 4. Freeze the Context Boundary

**Timebox:** 50 minutes.

The boundary is the set of names that other code uses to reach the game.
Your tests use these names too. Do not change them during this exercise.
The regenerated code in step 7 must keep all of them:

- The use-case ports in `kata.py`, and the domain types that they use.
- The REST routes in `api.py`.
- `create_app(game=None)` in `api.py`. Tests call it to start a new game.
- `app` in `api.py`. `__main__.py` starts the server with it.
- The error types in `game.py`: `KatacombsError`, `PlayerNotFound`,
  `ItemNotFound`, `InvalidName`, and `NotAllowed`.
- A way to build the use cases for port-level tests: `InMemoryGame` and
  the use-case classes in `game.py`. These are `RegisterPlayerUseCase`,
  `ListPlayersUseCase`, `QuitGameUseCase`, `InspectItemUseCase`,
  `InspectBagUseCase`, `UseItemUseCase`, `LookAroundUseCase`,
  `LookInDirectionUseCase`, `MoveUseCase`, `SaveGameUseCase`,
  `RegisterAccountUseCase`, and `LoginUseCase`. Each one takes the game
  as its only argument.
- For the web client: the routes of the contract that it calls, and the
  role and the accessible name of each control, for example the button
  "GO NORTH". The browser tests find the controls by these names.

Then do this work:

- Write the API contract from what the code does, as an OpenAPI file in
  `brown_field/spec/openapi.yaml`. FastAPI generates a draft at
  `/openapi.json`. The agent can start from it. Your group reviews each
  path against what the code does. Include each path, each request, each
  response, and each error code. Put each response schema in
  `components/schemas`. The contract test in step 5 reads them there.
- Start the Specification in `brown_field/spec/`. Write down the boundary
  names from the list above in it. The agent in step 7 must see them.
- Decide which part of the code owns each piece of data: players, the
  world, the state of each item, the saved games, the accounts, and the
  chat messages. Write down each place where one feature changes the
  data of another.
- Define the terms exposed at the boundary. Give each term one meaning.
  Start with Player, Account, Bag, Item, Gold, Location, and Message.

**Done when:** `openapi.yaml` lists each route, the accounts and the chat
too, and the Specification lists the boundary names.

### 5. Capture the current behavior

**Timebox:** 90 minutes.

Write characterization tests in `brown_field/tests/`. Each test records
what the system does today, not the behavior you expect.

- Test through the REST API, and through the use-case ports in `kata.py`.
  Do not test internal helper methods.
- Use `create_app()` from `api.py` with the FastAPI test client, so that
  each test starts with a new game.
- Assert what a player can observe: the location, the bag, the gold, the
  messages, the status codes, and the errors.

Do the work in this order. Items 1 to 5 are **core**. Items 6 to 8 are
**stretch**. When the timebox ends, stop.

1. **REST characterization tests for the minimum path.** Include one
   end-to-end test. It plays a full game through the REST API, from a new
   player to a win. Step 7 runs it against the regenerated code: it is
   the shortest proof that the game still works.
2. **The OPS-1 fitness function.** Add this operational constraint to the
   Specification: "OPS-1: each command responds in less than 100 ms at
   the 99th percentile (p99), over 100 calls, measured in process."
   Source: the workshop. Players expect instant feedback.
3. **The contract test.** Each response matches the contract in
   `brown_field/spec/openapi.yaml`. `pyyaml` and `jsonschema` are dev
   dependencies. You can use this helper:

   ```python
   import pathlib

   import jsonschema
   import yaml

   SPEC_FILE = pathlib.Path(__file__).resolve().parents[1] / "spec" / "openapi.yaml"
   SPEC = yaml.safe_load(SPEC_FILE.read_text())


   def validate(body, schema_name):
       schema = {"$ref": f"#/components/schemas/{schema_name}", "components": SPEC["components"]}
       jsonschema.validate(body, schema)
   ```

   Call it with a response body and a schema name from your contract, for
   example `validate(response.json(), "Location")`.
4. **The save and the restart.** Write one test that saves a player,
   starts the application again, and finds the player with the same bag,
   gold, and location. Give each test its own database path in a temporary
   folder, so that the test writes nothing into the repository. Then write
   down what a save does **not** hold.
5. **One seam: the clock.** One rule on the way to the win depends on
   the clock: a test that passes now can fail later in the same hour.
   Find the rule. Put it on the path of your end-to-end test. Control
   the clock in the test, and check both answers: a time when the rule
   allows the command, and a time when it refuses it, with the exact
   status and message. Michael Feathers gives this definition: "A seam is
   a place where you can alter behavior in your program without editing
   in that place." Do not edit `game.py` for this seam.
6. **Other seams.** A test cannot always reach a rule through the REST API
   or the ports. Then use a seam.
   - First, look for an enabling point that exists already. For example,
     `create_app(game=...)` accepts a game that the test builds.
   - If you must edit the code to make a seam, commit that edit
     separately. Run the characterization tests before and after the edit.
   - Do not change the ports or the routes.
   - Record each seam in a decision record. A seam becomes part of the
     frozen boundary. The regenerated code in step 7 must keep it.
   - A rule that needs a new seam is a stretch item.
7. **The world check.** Check the world rules: each title is unique, and
   each connection has a reverse connection that matches it. No port
   lists all locations. Use one of these two approaches. Each one is
   allowed:
   - Build a test world. `InMemoryGame()` takes no world, but its
     `places` attribute is public: make a game, replace `places` with the
     test world, and give the game to `create_app(game=...)`. Set the
     database path to a temporary file first, or the game reads the saves
     of another test. This edits no code. Record it as a seam. You can use
     Hypothesis to generate the test worlds.
   - Write a crawler test. It visits all locations through the REST API.

   The check must not call internal helpers such as `build_places()` or
   `check_connections()` directly.
8. **Port-level tests**, if time remains. Build each use case with the
   game, for example `UseItemUseCase(InMemoryGame())`.

**Web client, in parallel.** A frontend developer writes the tests of the
client in `brown_field/web/tests/`, through the screen, not through the
code of the components:

- Component tests with Vitest and Testing Library. Find each control by
  its role and its accessible name. Use MSW to answer the requests of the
  client, from the contract.
- One browser test with Playwright that plays to a win against the real
  server.
- WEB-OPS-1: "the production JavaScript bundle is at most 250 KB,
  gzipped." Source: the workshop. Players open the game on a slow
  network. A test builds the client and measures it.

**Done when:** items 1 to 5 pass against the original code.

### 6. Complete the Specification and the Provenance

**Timebox:** 60 minutes.

- Write each rule from your list in step 1 as a behavioral rule. Put the
  Specification in `brown_field/spec/`.
- Give each rule its source. For a rule that you keep as the code does
  it, a one-line tag is enough: "Source: observed in the code, kept."
- Give each rule one status: observed (the code does it, and nobody
  decided it), accepted (you keep it on purpose), or contested (you doubt
  it, and you record the question). Step 7 keeps the current behavior of
  each rule, for each status. Day 2 changes no behavior.
- Write a full decision record only for a decision that you discuss and
  keep on purpose, or that you change.
- One decision record can cover a group of related rules, for example
  "error codes" or "shared world state".
- Start each record from
  [`templates/decision-record.md`](../templates/decision-record.md), with
  the status "written after the code". Fill in the Evidence field: the
  file and the behavior that you saw.
- Put the decision records in `brown_field/decisions/`.
- The rules of the web client go into `brown_field/web/spec/`: each rule
  that the client adds, hides, or decides on its own. When a rule exists
  on both sides, for example a limit, write down where the two sides
  disagree.

**Done when:** each rule from step 1 is in the Specification with a
source, and each decision that you kept or changed on purpose has a
record.

### 7. Regenerate: the Deletion Test, part 2

**Timebox:** 45 minutes. Do not skip this step.

Keep the original code for the comparison. Regenerate in a new folder
outside this package. The folder holds only your primitives and the
files that do not change. The git history of the folder holds only the
files of the folder. Thus, the agent cannot read the original code.

Do not copy the full `brown_field/` folder. If you copy it, the tests
find the original code, and they pass for the wrong reason.

1. Commit your primitives and your tests.
2. Make the folder, and copy the files into it. From the package root:

   ```sh
   W=~/katacombs-workspaces/brown-field-regenerate
   mkdir -p $W/brown_field
   cp pyproject.toml uv.lock .gitignore $W/
   cp brown_field/__init__.py brown_field/__main__.py brown_field/kata.py \
     $W/brown_field/
   cp -R brown_field/spec brown_field/decisions brown_field/tests \
     $W/brown_field/
   cd $W
   git init -q
   git add -A
   git commit -qm "the primitives, before the regeneration"
   ```

3. Run `uv run pytest` once. Expected result: `pytest` fails with an
   `ImportError`, for example `ModuleNotFoundError: No module named 'brown_field.api'`. If
   the tests pass, they still use the original code. Stop and fix the
   setup.
4. Start a new LLM session in the folder. Do not give it the path of
   this package. Use this prompt:

   ```text
   Implement brown_field/game.py and brown_field/api.py in this folder.
   Use only pyproject.toml and these files in brown_field/: spec/,
   decisions/, tests/, kata.py, __init__.py, and __main__.py. Keep each
   port, route, and boundary name that brown_field/spec/ and
   brown_field/decisions/ name. Run `uv run pytest` until it passes. Do
   not change brown_field/spec/, brown_field/decisions/, or
   brown_field/tests/. If a primitive is incomplete, stop, and report
   the rule and the evidence.
   ```
5. When the agent stops, check that it changed no primitive. In `$W`,
   the output of this command must be empty:

   ```sh
   git status --porcelain -- brown_field/spec brown_field/tests brown_field/decisions
   ```

   If the output names a file, the agent changed a primitive. Write down
   the file. Restore it with `git restore <file>`, or delete a file that
   is new. Then run your tests. Each failure shows knowledge that your
   primitives do not hold yet.
6. Record which files the agent opened. Most agents show each file that
   they read. If the agent read a file outside the folder, write down the
   file name. In that case, the result does not prove your primitives.
7. Grade the four primitives again: strong, partial, or absent. Add the
   grades to `brown_field/grades.md`, next to the step 3 grades. Answer
   the three questions of step 3 again.
8. Answer this question in `brown_field/grades.md`: "Which unit could
   you regenerate alone, for example the chat, and what stops you?" If
   time allows, sort each failing test of step 5 into gameplay, accounts,
   or chat.
9. Keep the folder for the retrospective.

**Judge the one-prompt rewrite of step 1.** Do this at any time after
step 5, for example while the step 7 agent works.

1. Read the rewrite for 5 minutes, as you review a merge request. In
   `~/katacombs-workspaces/brown-field-rewrite/`, run `git add -A`, then
   read `git diff --cached legacy`. Decide: would you merge it? Write down
   why, and what you think it changed.
2. Copy your tests and your contract into the rewrite folder, and run
   the tests. From the package root:

   ```sh
   R=~/katacombs-workspaces/brown-field-rewrite
   cp -R brown_field/tests brown_field/spec $R/brown_field/
   cd $R
   uv run pytest
   ```

3. Compare the result with your decision from the reading. A test can
   fail because the rewrite moved a name that the test uses, for example
   the clock of a seam. That is a finding: the name was part of the
   boundary, and nobody wrote it down.
4. Take three unknown items of your archaeology list that no test
   covers. What did the rewrite do with each one?
5. Read the agent's report of the rewrite. Did it check its own work?
   Where is that check now?

A rewrite can be good. The question is how you know. Reading cannot show
you a rule that is missing. Your tests can, but only for the rules that
they cover. The regeneration got only your primitives, and the rewrite
got all the code: compare what each one kept, and what each one
changed.

Stretch, for a group that recovered the web client: regenerate
`web/src/` the same way, in a folder of its own, from `web/spec/`,
`web/tests/`, the contract, and the other files of `web/`. Then run
`npm test` and `npx playwright test`.

**Recovery score.** Count the decisions that nobody wrote down, and the
step that showed each one to you:

| The step that showed it | Count |
| --- | --- |
| Step 1: the archaeology listed it | |
| Step 1: you played the game, or read the code | |
| Step 4: the boundary, and the data ownership table | |
| Step 5: a test that failed | |
| Step 7: the regenerated code lost it | |

A decision counts when it is in your Specification or in a decision
record, with its source. Bring the table to the retrospective.

**Done when:** `brown_field/grades.md` has a second grade for each row and
the answer to the unit question, you recorded the files that the agent
opened, and the recovery score has a count in each row.

## What good looks like

Use this section to grade the primitives in step 3. Also use it to check
your work in steps 4–6. In a legacy system, each primitive must also say
where its knowledge came from: the brief, the code, or a decision.

### Specification

**Good looks like:**

- Each rule states what the game does and why. It does not state how.
- Each rule names its source: the brief, observed behavior in the code,
  or a decision record.
- Operational constraints are explicit, for example each limit and each
  size.
- A person who does not know `game.py` can build a correct version from
  the Specification alone.

**Warning signs:** a rule that names an internal class or an internal
helper, for example `build_places()`. A rule that exists only as an `if`
statement in the code.

A rule can name the boundary names from step 4, for example `create_app`
or `NotAllowed`. The warning is only about internal names.

**Example:**

```markdown
### ITEM-2 — A player cannot use an item that is not here

- Source: observed in the code. The brief does not give the error.
- Rule: when a player uses an item that is not in the location and not
  in the bag, the game refuses. Nothing changes.
- Observable result: HTTP 404, with the message "THERE IS NO RING HERE."
```

**Read more:**

- [The Phoenix Primitives](https://aicoding.leaflet.pub/3mjfruwwuck2d) —
  Chad Fowler's definition of all four primitives.
- [Production Is a Compiler Input](https://aicoding.leaflet.pub/3mjx4erlboc2l) —
  why operational constraints belong in the Specification.
- [EARS](https://alistairmavin.com/ears/) — a simple sentence pattern for
  clear, testable requirements.
- [Gherkin reference](https://cucumber.io/docs/gherkin/reference/) —
  Given-When-Then scenarios as executable specifications.

### Evaluation

**Good looks like:**

- Tests call the REST API or the use-case ports, and assert what a player
  can observe.
- Tests are oracles. An oracle is a durable check. It tells correct
  behavior from incorrect behavior without the old code. It still passes
  after a correct rewrite of `game.py` and `api.py`.
- Tests can import the boundary names from step 4, for example
  `create_app` and `NotAllowed`. Tests do not call internal helpers.
- Contract tests compare each API response with the contract that you
  wrote.
- The world check covers all locations, not one example.
- Language test: if you rewrite the game in another language, each test
  still makes sense.

**Warning signs:** tests that read `game.players` or other internal
fields. Tests that call internal helpers such as `build_places()`. Tests
that check calls to a mock. These are ephemeral tests. They are coupled
to the implementation, so a rewrite breaks them. Also look for tests that
pass only because of an accident in the current code.

**Example:**

```python
import pytest

from brown_field.game import NotAllowed
from brown_field.kata import Direction


# Good: an oracle. It survives a rewrite of game.py.
# move and look_around are the Move and LookAround ports. new_player gives
# the sid of a new player at the start location.
def test_a_wall_stops_the_player(move, look_around, new_player):
    with pytest.raises(NotAllowed):
        move.execute(new_player, Direction.UP)
    assert look_around.execute(new_player).title == "BRICK LANE"


# Good: a characterization test through the REST API.
def test_moving_into_a_wall_is_refused(client, new_player):
    response = client.put(f"/player/{new_player}/move/up")
    assert response.status_code == OBSERVED_STATUS  # the status the code returns today


# Bad: an ephemeral test. It is coupled to the internal data structure,
# so a rewrite breaks it.
def test_pick_appends_to_the_bag_list(game, player_sid):
    game.players[player_sid].bag.append("PEBBLE")
    assert game.players[player_sid].bag[-1] == "PEBBLE"
```

**Read more:**

- [Evaluations Are the Real Codebase](https://aicoding.leaflet.pub/3mb526js42k26) —
  ephemeral tests, durable evaluations, and the three tiers of evaluation.
- [The Deletion Test](https://aicoding.leaflet.pub/3md5ftetaes2e) — the
  question that your tests must answer, and the idea of an oracle.
- [Characterization Testing](https://michaelfeathers.silvrback.com/characterization-testing) —
  Michael Feathers on tests that record what legacy code does today.
- [Approval Tests](https://approvaltests.com/) — a tool to capture large
  outputs as characterization tests.
- [Hypothesis](https://hypothesis.readthedocs.io/en/latest/) —
  property-based testing for Python.

### Context Boundary

**Good looks like:**

- Each use case has one small, typed port. The ports in `kata.py` are a
  start.
- The REST API has a written, machine-readable contract. A contract test
  proves that the API matches the contract when it runs.
- Only one part of the system owns each piece of data. Only that part can
  change the data.
- The types that cross the boundary are explicit and have a version.
- You can check each part at its boundary. You do not have to start the
  full game.
- The Specification defines each boundary term once. The code does not use
  one term for two meanings.

**Warning signs:** two parts of the code change the same data. A client
that reads internal state and does not call a port. An API that only the
code describes.

**Example:**

```markdown
| Data                           | Owner in `game.py`      | Changed through                          |
| ------------------------------ | ----------------------- | ---------------------------------------- |
| Players: position, bag, gold   | `InMemoryGame.players`  | RegisterPlayer, QuitGame, Move, UseItem  |
| World connections              | `InMemoryGame.places`   | UseItem (special connections only)       |
```

This example is not complete. Find the other data in `game.py`, and each
use case that changes it.

**Read more:**

- [The Regenerative Grain](https://aicoding.leaflet.pub/3mfai4nqg6224) —
  five tests to find a unit you can safely delete and regenerate.
- [Compile to Architecture](https://aicoding.leaflet.pub/3mgfsrk75ac2l) —
  architecture as the target of generation.
- [Hexagonal Architecture](https://alistair.cockburn.us/hexagonal-architecture/) —
  Alistair Cockburn's original article on ports and adapters.
- [Bounded Context](https://martinfowler.com/bliki/BoundedContext.html) —
  Martin Fowler on boundaries in Domain-Driven Design.
- [Contract Test](https://martinfowler.com/bliki/ContractTest.html) — how
  to check that both sides keep a contract.
- [OpenAPI examples](https://learn.openapis.org/examples/) — example API
  contracts to model yours on.

### Provenance

**Good looks like:**

- Each rule that the brief does not state has a source: a decision
  record, or a one-line source tag in the Specification.
- Each decision record links to one or more rules in the Specification.
- Each decision record gives its evidence: the file and the behavior that
  you saw.
- You wrote down the scar tissue. Each strange check in the code has a
  reason, or an open question.

**Warning signs:** "we do this because the code does it" with no reason.
A decision that exists only in a chat or in someone's memory.

**Example:**

```markdown
# 0001 — Store the game state in memory

- **Status:** written after the code
- **Date:** 2026-09-24
- **Need:** operational. The brief asks for an in-memory database.
- **Traces to:** Specification rule STORE-1.
- **Evidence:** `InMemoryGame` in `game.py` holds all players and the
  world.

## Context

The brief asks for an in-memory database.

## Decision

Keep all game state in memory, in one process.

## Alternatives rejected

| Alternative | Why you rejected it |
| --- | --- |
| A database on disk | The brief asks for memory. Nobody asked to keep games after a restart. |

## Consequences

A restart loses all games.

## Fitness functions

None yet.
```

**Read more:**

- [Provenance Is the New Version Control](https://aicoding.leaflet.pub/3mcbiyal7jc2y) —
  record the reasons, not only the changes.
- [The Implementation Remembers](https://aicoding.leaflet.pub/3mobohx4fq22x) —
  scar tissue in legacy code, and how to extract it.
- [Documenting Architecture Decisions](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions) —
  Michael Nygard's original ADR article.
- [MADR](https://adr.github.io/madr/) — a lightweight decision record
  template.
- [ADR examples](https://github.com/joelparkerhenderson/architecture-decision-record) —
  a large collection of templates and real examples.

## Retrospective

This retrospective is a conversation. Start with your own questions about
the day, and follow them. The steps, the questions, and the template below
are ice breakers. Use them only if your group needs a gentle push to
find its own questions.

**Timebox:** 60 minutes. If you use the template, copy
[`templates/brown-field-retrospective.md`](../templates/brown-field-retrospective.md)
to `brown_field/retrospective.md`, and write the answers there.

### 1. Share out

Each group has 3 minutes. The facilitator uses a timer. With more than
five groups, five groups present, and each other group writes one result
on the board. Show your primitive grades from step 3 and
step 7, the decisions you found, the result of the regeneration in
step 7, and your judgment of the one-prompt rewrite: would you merge it,
and how do you know?

### 2. Lessons

1. Which decisions did you find that nobody wrote down? How did you find
   them? Did the archaeology list them? Did you play the game, read the
   code, or see a test fail?
2. Which primitive was the most difficult to recover from the code? Why?
3. Which rules were not possible to reach from outside? Which seams did
   you add?
4. Did the regenerated code pass your tests? And the one-prompt rewrite?
   What did each failure show? What did your reading of the rewrite tell
   you, and what did the tests tell you?
5. Look at your three answers from step 3 and step 7. Which one moved
   toward yes? Which one is still a no, and what would change it?
6. Which was easier: to write the primitives before the code (green
   field), or to recover them from code that exists (brown field)? What
   did each one cost? Answer this question at 16:40, in the comparison.

### 3. Apply it in your team

1. Which component in your team does someone want to rewrite? Ask an
   agent to list its scars, as in step 1, and mark them. How long is the
   unknown column?
2. What is the smallest first step for that component: a contract,
   characterization tests, or decision records?
3. What will you try in your team?

The template has more questions, if you want them.

## Evidence at the end

The minimum path deliberately leaves some legacy decisions undiscovered.
That is valid. Record the scope that you tested. Do not claim that an
untested decision is recovered. Each step above says when it is done.
The regeneration of step 7 counts even when it fails: say which
knowledge was missing.
