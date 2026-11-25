# Day 2, Brown Field

Read `brown_field/README.md`. Run and explore the legacy system before you
write a rule or a test.

## Run the system

The system has a server and a web client. Use two terminals. Start the
server first.

1. The server. From the package root:

   ```sh
   uv sync
   uv run python -m brown_field
   ```

   It runs at `http://127.0.0.1:8000`. Its interactive page is at
   `http://127.0.0.1:8000/docs`.

2. The web client. It needs Node.js 24.18 or later (24 LTS or 26).
   From the package root:

   ```sh
   cd brown_field/web
   npm ci
   npm run dev
   ```

   Open `http://127.0.0.1:5173`. The web client sends its requests to the
   server on port 8000.

To stop each part, press `Ctrl+C` in its terminal. The section "Run the
game" of `brown_field/README.md` has the other commands, for example
for the tests.

Use a new regeneration folder for step 7. That folder must not contain
`game.py`, `api.py`, the `.git` folder of this package, or an old agent
conversation.

Do the exercise in the folder of this package. At the end of day 2, copy
its `brown_field/` folder to the results folder. From the package root:

```sh
rm -rf ~/katacombs-results/brown_field
mkdir -p ~/katacombs-results
cp -R brown_field ~/katacombs-results/brown_field
```

Do not change the behavior of the original system. You can edit the
code to make a seam (step 5). Today, you recover the knowledge of the
system. On day 3, you change the structure of the system.

## Optional: the Phoenix Kit

`phoenix-kit/` holds eleven agent skills for Claude Code. Plain files are
enough for this exercise. Read `phoenix-kit/README.md` before you use it.

If you use the kit:

1. Start the agent at the root of this package with
   `claude --plugin-dir ./phoenix-kit`.
2. Run `/phoenix-kit:assess brown_field/game.py`. No preset fits this
   layout, so the assessment proposes a `PHOENIX.md`. Review it, then
   save it at the root of the package.
3. For step 7, copy `PHOENIX.md` and `phoenix-kit/` into the
   regeneration folder too.
