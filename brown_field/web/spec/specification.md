# Katacombs web client — Specification

Status: recovered from the legacy client on 2026-11-25 (`src/App.tsx`,
`src/api.ts`). Each rule records what the client does today. The tests in
`brown_field/web/tests/` name the rule ID in each test title. The server's
rules are in `brown_field/spec/specification.md`; where the client and the
server disagree, both sides are pinned as they are.

## The routes the client calls

All under `/api`, which the development and preview servers send to
`http://127.0.0.1:8000` with the prefix removed (`vite.config.ts:4-9`).

| Client function | Route | Server operation |
| --- | --- | --- |
| `startGame` | `POST /game/player` | `startGame` |
| `register` | `POST /accounts` | `registerAccount` |
| `login` | `POST /accounts/login` | `login` |
| `look` | `GET /player/{sid}/location` | `lookAround` |
| `bag` | `GET /player/{sid}/bag` | `inspectBag` |
| `move` | `PUT /player/{sid}/move/{direction}` | `move` |
| `act`, `pick` | `PUT /player/{sid}/item/{item}/use/{action}` | `actOnItem` |
| `quickPick` | `PUT /player/{sid}/pickup/{item}` | `legacyPickup` |
| `quit` | `DELETE /game/player/{sid}` | `quitGame` |
| `save` | `POST /player/{sid}/save` | `saveGame` |
| `chat` | `GET /player/{sid}/chat` | `readChat` |
| `say` | `POST /player/{sid}/chat` | `sendChatMessage` |
| `leaderboard` | `GET /leaderboard` | `readLeaderboard` (never called while the flag is off) |

The client never calls `GET /game/player`, `GET /items/{itemSid}` or
`GET /player/{sid}/look/{direction}`.

## The names of the controls

Tests find each control by its role and accessible name.

| Control | Role | Accessible name |
| --- | --- | --- |
| Name box | textbox | `NAME` |
| Email box, password box | textbox | `EMAIL`, `PASSWORD` |
| Start, log in, register | button | `START`, `LOG IN`, `REGISTER` |
| Moves | navigation | `moves` |
| One button per direction | button | `GO NORTH`, `GO SOUTH`, `GO EAST`, `GO WEST`, `GO UP`, `GO DOWN` |
| Items in the location | region | `items here` |
| An action on an item | button | `<ACTION> <ITEM>`, for example `PICK BEER` |
| Bag | region | `bag` |
| Chat | region | `chat`; its box: textbox `chat message`; button `SEND` |
| Save, quit | button | `SAVE`, `QUIT` |
| Messages | list | `messages` |
| Market banner | alert | `THE MARKET IS CLOSED FOR CLEANING.` |
| Exit and lost connection | status | the text shown |
| Start again | button | `NOT YOU? START AGAIN` |
| Legacy pickup | **none**: a double-click on the item's text in `items here` | — |

## Rules

### Start

#### WEB-START-1 — START sends the name trimmed and in upper case

- Source: legacy client (App.tsx:93, App.tsx:52).
- Rule: When a person presses START, the client shall send the name
  without leading or trailing spaces, in upper case, and keep the new
  player sid in the browser as `katacombs.sid`.
- Why: the server does the same cleaning; the sid lets a reload resume.
- Observable result: the request body is `{"name": "ANA"}` for `  ana `;
  `localStorage["katacombs.sid"]` holds the sid; the game screen shows.

#### WEB-START-2 — The NAME box stops at 40 characters

- Source: legacy client (App.tsx:203). The server allows 1 to 50 (PLAYER-3).
- Rule: The client shall accept at most 40 characters in the NAME box.
- Why: unknown; the limit differs from the server's.
- Observable result: typing 45 characters leaves 40 in the box.

#### WEB-START-3 — REGISTER registers, then logs in

- Source: legacy client (App.tsx:100-116).
- Rule: When a person presses REGISTER, the client shall register the
  account with the email, the password and the cleaned name, and then log
  in with the email and the password.
- Why: one press opens the game for a new account.
- Observable result: `POST /accounts`, then `POST /accounts/login`; LOG IN
  alone sends only the login.

### Messages

#### WEB-MSG-1 — A refusal shows the server's message

- Source: legacy client (api.ts:48-58, App.tsx:42-44).
- Rule: When the server refuses a command with a JSON `message`, the client
  shall show that message at the top of the messages list.
- Why: the server's messages are written for the player.
- Observable result: `THIS NAME IS RESERVED.` in the list `messages`.

#### WEB-MSG-2 — A refusal without a message shows SOMETHING WENT WRONG.

- Source: legacy client (api.ts:55-56).
- Rule: If a refused answer has no JSON `message`, then the client shall
  show `SOMETHING WENT WRONG.`
- Why: a fallback for a body that is not the game's error format.
- Observable result: a plain-text 500, or FastAPI's `{"detail": ...}`,
  shows `SOMETHING WENT WRONG.` A successful answer that is not JSON shows
  nothing.

### Moves

#### WEB-MOVE-1 — A GO button is enabled only for an exit

- Source: legacy client (App.tsx:239-248).
- Rule: The client shall show one GO button per direction, enabled only
  for the exits of the location.
- Observable result: at BRICK LANE, GO UP and GO DOWN are disabled.
- Why: a person can't choose a wall.

#### WEB-MOVE-2 — Every GO button is disabled at energy 1 or below

- Source: legacy client (App.tsx:185, "Do not let a player get stuck at 0."). The server refuses only at 0 (MOVE-5).
- Rule: While the bag shows an energy of 1 or less, or the bag has not
  loaded, the client shall disable every GO button.
- Why: the comment says it keeps a player from reaching 0.
- Observable result: with energy 1 every GO button is disabled; while the
  bag request is open, the location shows and every GO button is disabled.

#### WEB-MOVE-3 — GO moves the player and shows the new location

- Source: legacy client (App.tsx:118-127).
- Rule: When a person presses an enabled GO button, the client shall send
  the move and show the location of the answer.
- Observable result: `PUT /player/{sid}/move/north`; the heading is the
  new title.
- Why: moving is how a person explores.

#### WEB-MOVE-4 — At the katacombs exit the client shows the score

- Source: legacy client (App.tsx:123, App.tsx:236).
- Rule: While the location is the katacombs exit, the client shall show
  `YOU FOUND THE EXIT. SCORE <score>.` as a status.
- Why: the person sees the end of the game.
- Observable result: the status text, and `YOU FOUND THE EXIT.` in messages.

### Items

#### WEB-ITEM-1 — An item here shows every action but DROP

- Source: legacy client (App.tsx:256-266).
- Rule: The client shall show a button for each action of an item in the
  location, except `drop`.
- Why: unknown; it also shows USE, which the server refuses for an item
  not carried (ACT-7).
- Observable result: `PICK BEER` and `USE BEER`, no `DROP BEER`.

#### WEB-ITEM-2 — PICK sends the take again after 800 ms

- Source: legacy client (api.ts:93-102, "Slow network on the train. Do not remove."). Pairs with the server's INC-2231 (ACT-5).
- Rule: If the server has not answered a take after 800 ms, then the
  client shall send the same take again and show the second answer.
- Why: a slow network; the server answers TAKEN. to the repeat.
- Observable result: one request when the answer is fast; two when the
  first answer takes longer than 800 ms.

#### WEB-ITEM-3 — USE on an item here is sent, and the refusal shown

- Source: legacy client (App.tsx:129-138).
- Rule: When a person presses USE on an item in the location, the client
  shall send the use and show the server's answer.
- Why: see WEB-ITEM-1.
- Observable result: `YOU ARE NOT CARRYING THE BEER.` in messages.

#### WEB-ITEM-4 — A double-click on an item here calls the legacy pickup

- Source: legacy client (App.tsx:140-148, App.tsx:255).
- Rule: When a person double-clicks an item in the location, the client
  shall call the legacy pickup route for it.
- Why: unknown. The target has no role and no accessible name.
- Observable result: `PUT /player/{sid}/pickup/{item}`.

#### WEB-BAG-1 — The bag shows gold, score, energy, DROP and USE

- Source: legacy client (App.tsx:271-290).
- Rule: The client shall show the bag's gold, score and energy, and for
  each item only its DROP and USE buttons.
- Why: the person sees what they carry.
- Observable result: `GOLD 5 · SCORE 5 · ENERGY 11`; `DROP KEY`, `USE KEY`,
  no `PICK KEY`.

### Session

#### WEB-SESSION-1 — A sid in the browser resumes the game

- Source: legacy client (App.tsx:29, App.tsx:58-70).
- Rule: When the page opens with a sid in `katacombs.sid`, the client shall
  load that player's location and bag instead of the start screen.
- Why: a reload must not lose the game.
- Observable result: the game screen, with no START button.

#### WEB-SESSION-2 — A failed load shows CONNECTION LOST and retries

- Source: legacy client (App.tsx:58-70, App.tsx:186-193).
- Rule: If loading the player fails, then the client shall show
  `CONNECTION LOST. RETRYING...`, retry once at once and then every 2 s,
  and offer `NOT YOU? START AGAIN`.
- Why: a short network loss must not end the game. An unknown sid (for
  example after a restart without a save) retries for ever.
- Observable result: 2 requests at once, one more each 2 s; START AGAIN
  clears `katacombs.sid`.

#### WEB-SESSION-3 — SAVE shows the server's answer

- Source: legacy client (App.tsx:150-157).
- Rule: When a person presses SAVE, the client shall save the game and show
  the answer's message.
- Observable result: `GAME SAVED.` in messages.
- Why: the person knows the save worked.

#### WEB-SESSION-4 — QUIT returns to the start, whatever the server answers

- Source: legacy client (App.tsx:167-170).
- Rule: When a person presses QUIT, the client shall send the quit, clear
  `katacombs.sid` and show the start screen, even if the quit fails.
- Why: unknown; a failed quit leaves the player active on the server.
- Observable result: the start screen after a 500 answer.

### Chat

#### WEB-CHAT-1 — The chat asks the server every 2 s

- Source: legacy client (App.tsx:72-79).
- Rule: While a game is open and the connection is not lost, the client
  shall read the chat every 2 s.
- Why: messages from other players appear without a click.
- Observable result: no chat request at the start; one per 2 s.

#### WEB-CHAT-2 — SEND posts the text and clears the box

- Source: legacy client (App.tsx:172-181).
- Rule: When a person presses SEND with text in the box, the client shall
  send it, clear the box and read the chat again.
- Observable result: `{"text": "hello"}`; an empty box; a chat request.
- Why: the person sees their message at once.

#### WEB-CHAT-3 — SEND with an empty box sends nothing

- Source: legacy client (App.tsx:174). The server accepts an empty text (CHAT-1).
- Rule: If the chat box is empty, then the client shall send nothing on SEND.
- Why: unknown; the server would accept it.
- Observable result: no `POST /player/{sid}/chat`.

### Market and leaderboard

#### WEB-MARKET-1 — A banner shows the market closed in minutes 50 to 59

- Source: legacy client (App.tsx:184, App.tsx:234). The server refuses from its own clock (MOVE-6).
- Rule: While the browser's local time is in minutes 50 to 59 of an hour,
  the client shall show the banner `THE MARKET IS CLOSED FOR CLEANING.`
- Why: the person learns why the market refuses.
- Observable result: an alert at minutes 50 and 59; none at 0 and 49.

#### WEB-MARKET-2 — The screen redraws every 30 s

- Source: legacy client (App.tsx:81-84).
- Rule: While the page is open, the client shall redraw every 30 s.
- Why: the market banner follows the clock without a click.
- Observable result: the banner appears within 30 s of minute 50.

#### WEB-MARKET-3 — The banner disables no button

- Source: legacy client (App.tsx:239-248).
- Rule: The client shall keep GO EAST enabled while the banner shows.
- Why: only the server decides; the two clocks may differ.
- Observable result: GO EAST is enabled at minute 55.

#### WEB-BOARD-1 — The leaderboard is hidden behind a flag

- Source: legacy client (App.tsx:5, "Marketing, 2024: hide until the season starts.").
- Rule: Where `SHOW_LEADERBOARD` is off, the client shall show no
  leaderboard and shall not request it.
- Why: marketing hides it until the season starts.
- Observable result: no region `leaderboard`; no `GET /leaderboard`.

### Fitness and end to end

#### WEB-FIT-1 — The client's types match the server's contract, with one known drift

- Source: legacy client (api.ts:3-37); contract (brown_field/spec/openapi.yaml).
- Rule: The client shall declare types that every response of the contract
  fits, except `Player`, whose `bag` requires an `energy` that the server
  does not send.
- Why: `api.ts` repeats the JSON shapes by hand.
- Observable result: `tsc` accepts `tests/fitness/contract-types.check.ts`
  against types generated from the contract.

#### WEB-OPS-1 — The production bundle is at most 250 KB gzipped

- Source: the workshop (brown_field/README.md:465).
- Rule: The client shall ship a production JavaScript bundle of at most
  250 KB, gzipped.
- Why: players open the game on a slow network.
- Observable result: a production build measures about 70 KB today.

#### WEB-E2E-1 — A person can win in a real browser

- Source: the workshop (brown_field/README.md, "Web client, in parallel").
- Rule: When a person plays the slide route in a browser against the real
  server, the client shall show the win with a score of 55.
- Why: the shortest proof that the client and the server still work
  together.
- Observable result: `YOU FOUND THE EXIT. SCORE 55.`; a reload resumes the
  game.
