# Delta — accounts

Format adapted from the OpenSpec delta spec (MIT). Each section is
optional. Rules use the format of the specification. On archive, the
delta merges into the specification and this file moves to the archive.

The routes and shapes named here are the proposal's. `/phoenix-kit:contract`
fixes them in `openapi.yaml` and names each edit below.

## ADDED Rules

#### ACCOUNT-7 — Login ignores the letter case of the email

- Status: accepted (decision 0013). Decided by change accounts.
- Source: change accounts; the need of Product, 2026-11-26: "one email, and one person".
- Rule: When a client logs in with an email that matches no account
  exactly but matches accounts when letter case is ignored, Katacombs
  shall log in to the matching account whose password matches, and if
  more than one matches, the first one stored.
- Why: a person types their email in any case; for the player it is one
  email. Accounts that already exist as case variants are kept, and an
  exact match still reaches each one.
- Observable result: after registering `Ana@example.com`, a login with
  `ana@example.com` and the right password gives the account's player
  (`ACCOUNT-4`). An exact match comes first: with `Ana@example.com` and
  `ana@example.com` both stored, a login with `ana@example.com` reaches
  `ana@example.com`. A wrong password still gets `ACCOUNT-5`.

#### ACCOUNT-8 — Anybody can read a profile

- Status: accepted (decision 0013). Decided by change accounts.
- Source: change accounts; the need of Product, 2026-11-26: "Each player has a public profile".
- Rule: When a client reads the profile of a profile sid, Katacombs shall
  respond with the account's name, its games won and its best score.
- Why: players can see each other's results.
- Observable result: `GET /profiles/{profileSid}`, status 200, body
  `{"profileSid", "name", "gamesWon", "bestScore"}`. An account with no
  win has `gamesWon` 0 and `bestScore` null. The request needs no
  credential.

#### ACCOUNT-9 — No public answer shows an email

- Status: accepted (decision 0013). Decided by change accounts.
- Source: change accounts; the need of Product, 2026-11-26: "The email is never public".
- Rule: Katacombs shall leave the email out of every answer except the
  answers to the account's own registration and change of name.
- Why: the email identifies the person, and the profile is public.
- Observable result: a fitness function registers an account with a
  unique email, wins, chats, and then reads the profile, the leaderboard,
  the players, the chat and the location. No answer body contains the
  email, in any letter case.

#### ACCOUNT-10 — A win of an account's player counts for its profile

- Status: accepted (decision 0013). Decided by change accounts.
- Source: change accounts; the need of Product, 2026-11-26: "the games won, and the best score".
- Rule: When the player of an account wins, Katacombs shall keep the win
  with the account, so that the profile counts it after a restart.
- Why: the leaderboard is in memory (`WIN-2`), and a profile must not be
  empty after each restart.
- Observable result: after a win of a logged-in player with score 40,
  the profile has `gamesWon` 1 and `bestScore` 40, and the same values
  after a restart. A win of a player who started with `POST /game` and
  no account counts for no profile. Wins from before this change count
  for no profile.

#### ACCOUNT-11 — A person can change the name of the account

- Status: accepted (decision 0013). Decided by change accounts.
- Source: change accounts; the need of Product, 2026-11-26: "A player can change the name of the profile".
- Rule: When a client sends the email and password of an account with a
  valid name, Katacombs shall make it the name of the account, its
  profile and its active player.
- Why: a person chooses how others see them.
- Observable result: `PUT /accounts/name` with `{"email", "password",
  "name"}`, status 200, body `{"email", "name", "profileSid"}` with the
  name trimmed and upper case. The name follows `PLAYER-2` to `PLAYER-4`,
  with their statuses and messages. The profile and the active player in
  `GET /game/player` show the new name. Finished games already on the
  leaderboard, high-score lines and chat messages keep the name they were
  made with. The email lookup follows `ACCOUNT-7`.

#### ACCOUNT-12 — A change of name or a deletion needs the email and the password

- Status: accepted (decision 0013). Decided by change accounts.
- Source: change accounts; the review answer of 2026-11-26: the email and password in the body, as login does.
- Rule: If a client changes the name of an account or deletes it with an
  email that has no account, or with a wrong password, then Katacombs
  shall refuse the request and change nothing.
- Why: only the owner can change or delete the account, and there is no
  token or session. One message for both cases does not tell which emails
  exist (`ACCOUNT-5`).
- Observable result: status 405, error reason `NOT_ALLOWED`, message
  `WRONG EMAIL OR PASSWORD.` The account, its profile and its player are
  as they were.

#### ACCOUNT-13 — Deleting an account removes what identifies the person

- Status: accepted (decision 0013). Decided by change accounts.
- Source: change accounts; the need of Product, 2026-11-26: "After that, the game holds nothing that identifies the player".
- Rule: When a client deletes an account with its email and password,
  Katacombs shall remove the account, its profile, its kept wins, the
  save and the snapshot of its player, its active player and the chat
  messages that player sent.
- Why: a person can leave the game and take their data with them.
- Observable result: `POST /accounts/delete` with `{"email", "password"}`,
  status 200, body `{"message": "ACCOUNT DELETED."}`. Afterwards a login
  gets `ACCOUNT-5`, the profile sid gets `ACCOUNT-16`, and the player sid
  gets `PLAYER-9`. The player's bag stays in its location, as `PLAYER-8`
  does on a quit. A fitness function searches the database file and the
  answers of every read route for the email, the name and the player sid
  (the name is unique in the test) and finds none, before and after a
  restart. The high-score file is outside this rule: it keeps the name
  of each win (`ACCOUNT-14`).

#### ACCOUNT-14 — A deleted account's wins stay, without its name

- Status: accepted (decision 0013). Decided by change accounts.
- Source: change accounts; the review answer of 2026-11-26: the wins are anonymized.
- Rule: When a client deletes an account, Katacombs shall show each win
  of the account on the leaderboard with the name `DELETED PLAYER`, with
  the same score and move count.
- Why: the other players' ranks stay as they were, and the name goes.
  The high-score file is left alone: the review of 2026-11-26 gives
  marketing no support for these features, and decision 0002 stands.
- Observable result: `GET /leaderboard` holds the win with `name`
  `DELETED PLAYER` and `profileSid` null, in its rank. The high-score
  file is byte for byte as it was before the deletion: the account's
  lines keep its name. This is a known gap in the need "nothing that
  identifies the player", and decision 0013 records it.

#### ACCOUNT-15 — The email of a deleted account can register again

- Status: accepted (decision 0013). Decided by change accounts.
- Source: change accounts; follows from `ACCOUNT-13`.
- Rule: When a client registers with the email of a deleted account,
  Katacombs shall create a new account with a new profile sid and an
  empty profile.
- Why: nothing links the email to the old account any more.
- Observable result: status 201 (`ACCOUNT-1`). The new profile has
  `gamesWon` 0, and its profile sid differs from the deleted one.

#### ACCOUNT-16 — An unknown profile sid is not found

- Status: accepted (decision 0013). Decided by change accounts.
- Source: change accounts.
- Rule: If a request names a profile sid that belongs to no account, then
  Katacombs shall refuse the request.
- Why: the account was deleted, or never existed.
- Observable result: status 404, error reason `NOT_FOUND`, message
  `PROFILE <sid> NOT FOUND.`

#### STORE-4 — The database file holds a profiles table and a wins table

- Status: accepted (decision 0013). Decided by change accounts.
- Source: change accounts; decision 0005 (the database file is a
  contract with every server version).
- Rule: When a client registers, or an account's player wins, Katacombs
  shall keep one row per account in the table `profiles`, with the text
  columns `email` and `profile_sid`, and one row per win in the table
  `wins`, with the text columns `email`, `name`, `at` and the integer
  columns `score` and `moves`.
- Why: profiles and wins must survive a restart. New tables leave the
  `accounts` table of `STORE-2` as it is, so an older server still reads it.
- Observable result: the two tables have those columns. The `email` is the
  account's email as stored in `accounts`. A server that starts on a file
  without the two tables creates them, and gives a profile sid to each
  account that has none. A deletion removes the account's rows from both.

## MODIFIED Rules

#### ACCOUNT-1 — A client can register an account

- Status: accepted (decision 0013). Revised by change accounts.
- Source: legacy code (game.py:779-792, api.py:157-160), revised by change accounts.
- Rule: When a client registers with an email, a password and a valid name,
  Katacombs shall create an account and its profile.
- Why: an account lets a person come back to their game, and its profile
  shows their results to other players.
- Observable result: status 201, body `{"email": "<email>", "name":
  "<NAME>", "profileSid": "<profile sid>"}`. The profile sid is new, in
  the digit form of a player sid, and is the sid of no player and no
  item. The email is stored as it was typed.
- Revised: 2026-11-26. The answer gains `profileSid`, and a profile is created (decision 0013).

#### ACCOUNT-3 — An email has one account, whatever its letter case

- Status: accepted (decision 0013). Revised by change accounts.
- Source: legacy code (game.py:782-783), revised by change accounts; the need of Product, 2026-11-26.
- Rule: If a client registers with an email that matches the email of an
  account when letter case is ignored, then Katacombs shall refuse the
  registration.
- Why: the email identifies the person. For players, `Ana@example.com` and
  `ana@example.com` are one email.
- Observable result: status 405, error reason `NOT_ALLOWED`, message
  `THIS EMAIL IS TAKEN.` After `Ana@example.com`, a registration of
  `ana@example.com` or `ANA@EXAMPLE.COM` is refused. Case variants stored
  before this change stay as separate accounts.
- Revised: 2026-11-26. The match ignores letter case; before, only the exact email was taken (decision 0013).

#### ACCOUNT-4 — Logging in gives the account's player and its profile sid

- Status: contested. Open question: Should a later login restore the snapshot again? Today a second login after a quit rolls the active player back.
- Source: legacy code (game.py:799-830, api.py:162-164), revised by change accounts; the review answer of 2026-11-26: always return the profile sid.
- Rule: When a client logs in with the email and password of an account,
  Katacombs shall respond with the account's player, the snapshot of its
  last quit, else its active player, else a new player at BRICK LANE,
  together with the account's profile sid.
- Why: a person resumes their game from any client, and a client that
  only logs in can still show and share its own profile.
- Observable result: status 200, a Player with its energy and the
  account's `profileSid`. A snapshot
  whose location is not in the world is not restored: the login gives the
  active player, else a new player at BRICK LANE (game.py:805). A login
  that restores a snapshot while 20 players are active, and the account's
  player is not one of them, is refused with status 405 and the message
  `THE KATACOMBS ARE FULL. TRY AGAIN LATER.` (game.py:808-809). The email
  lookup follows `ACCOUNT-7`.
- Revised: 2026-11-26. The answer gains `profileSid`, the same in every login (decision 0013).

#### PLAYER-4 — The names ADMIN and DELETED PLAYER are reserved

- Status: accepted (decision 0013). Revised by change accounts.
- Source: legacy code (game.py:19, game.py:548-549, game.py:787-788), revised by change accounts.
- Rule: If a trimmed, upper-case name is `ADMIN` or `DELETED PLAYER`, then
  Katacombs shall refuse the request and create nothing.
- Why: A guess for `ADMIN`: a player must not pass for the staff in the
  chat or on the leaderboard. `DELETED PLAYER` marks the wins of deleted
  accounts (`ACCOUNT-14`), and no living player may use it.
- Observable result: status 400, error reason `INVALID_VALUE`, message
  `THIS NAME IS RESERVED.` The check holds for a new game, a registration
  and a change of name (`ACCOUNT-11`).
- Revised: 2026-11-26. `DELETED PLAYER` joins `ADMIN` (decision 0013).

#### WIN-2 — A win adds a finished game to the leaderboard

- Status: observed. The code does it; nobody has decided it (2026-11-25).
- Source: legacy code (game.py:639-643); brief, "Leaderboard", revised by change accounts.
- Rule: When a player wins, Katacombs shall add a finished game with the
  player's name, score, move count and the profile sid of the player's
  account to the leaderboard.
- Why: players compare their wins, and a win leads to the winner's profile.
- Observable result: `GET /leaderboard` holds `{"name", "score", "moves",
  "profileSid"}` for the win. `profileSid` is null for a player without an
  account. The leaderboard is empty after a restart.
- Revised: 2026-11-26. A finished game gains `profileSid` (decision 0013).

## Other changes to the specification

### Terms: Account

| Account | An email, a password, a name and a profile, that survives a restart and resumes a player. Two emails that differ only in letter case are one email. | user |

### Terms: Profile (new row, after Account)

| Profile | The public view of an account: its name, its games won and its best score. Never its email. | account (for this idea), user page |

### Terms: Profile sid (new row, after Profile)

| Profile sid | The public identifier of a profile, in the digit form of a player sid. It grants nothing. | profile id, account id |

### Terms: Deleted player (new row, after Finished game)

| Deleted player | The name `DELETED PLAYER` that the wins of a deleted account show. A reserved name. | anonymous, removed user |

### Data ownership: two new rows, after "Accounts with snapshots"

| Profiles (SQLite table `profiles` in `KATACOMBS_DB`) | game-server (register, delete) | game-server (profile, start) |
| Kept wins (SQLite table `wins` in `KATACOMBS_DB`) | game-server (win, change of name, delete) | game-server (profile, delete) |

### Contract: brown_field/spec/openapi.yaml

- To be written by `/phoenix-kit:contract`: `GET /profiles/{profileSid}`
  (`ACCOUNT-8`, `ACCOUNT-9`, `ACCOUNT-16`), `PUT /accounts/name`
  (`ACCOUNT-11`, `ACCOUNT-12`, `PLAYER-2`..`PLAYER-4`), `POST /accounts/delete`
  (`ACCOUNT-12`..`ACCOUNT-14`); `profileSid` on `Account` (`ACCOUNT-1`),
  on `FinishedGame` (`WIN-2`) and on the login answer (`ACCOUNT-4`, a new
  schema `LoginResult`: Player plus `profileSid`); new schemas `Profile`
  and `NameChange`. No backward compatibility for clients that reject
  unknown fields (review, round 2);
  `x-rules` of `/accounts` and `/accounts/login` gain `ACCOUNT-3`, `ACCOUNT-7`.

## Old values

| Rule ID | Old value | New value |
| --- | --- | --- |
| PLAYER-4 | `The name ADMIN is reserved` | `The names ADMIN and DELETED PLAYER are reserved` |
| ACCOUNT-3 | `An email has one account` | `An email has one account, whatever its letter case` |
| WIN-2 | `{"name", "score", "moves"}` | `{"name", "score", "moves", "profileSid"}` |
| ACCOUNT-4 | `Logging in gives the account's player` | `Logging in gives the account's player and its profile sid` |
| ACCOUNT-1 | `{"email": "<email>", "name": "<NAME>"}` | `{"email": "<email>", "name": "<NAME>", "profileSid": "<profile sid>"}` |

## Unchanged

- `ACCOUNT-2`: the email check (`@`) stays the only check of its form.
- `ACCOUNT-5`: a wrong email or password at login keeps its status and message.
- `ACCOUNT-6`: quitting with an account still keeps a snapshot.
- `STORE-2`: the `accounts` table keeps its five columns; emails are stored as typed.
- `STORE-3`: the password digest stays as it is, unsalted (still contested).
- `WIN-3`: each win still appends one line in the schema's format, and
  nothing rewrites the file (decision 0002; no marketing support here).
- `BOARD-1`: the ranking order stays; an anonymized win keeps its rank.
- `PLAYER-2`, `PLAYER-3`: the name rules apply to a change of name as they are.
- `PLAYER-7`, `PLAYER-8`: a quit still removes the player and leaves the bag.
- `CHAT-1`, `CHAT-2`: chat messages keep the name they were sent with,
  except the ones a deletion removes.
