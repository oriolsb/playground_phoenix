# 0013 — Accounts get a public profile, a change of name and a deletion; one email is one person

- **Status:** accepted
- **Date:** 2026-11-26
- **Need:** business. The players, through Product (need "1. Accounts",
  2026-11-26): one account for each person, whatever the letter case of
  the email; a public profile with the name, the games won and the best
  score, never the email; a change of name; a deletion after which the
  game holds nothing that identifies the player.
- **Traces to:** `ACCOUNT-1`, `ACCOUNT-3`, `ACCOUNT-4`, `ACCOUNT-7`, `ACCOUNT-8`,
  `ACCOUNT-9`, `ACCOUNT-10`, `ACCOUNT-11`, `ACCOUNT-12`, `ACCOUNT-13`, `ACCOUNT-14`,
  `ACCOUNT-15`, `ACCOUNT-16`, `PLAYER-4`, `WIN-2`, `STORE-4`.
- **Change:** `accounts`. Accepted on 2026-11-26 by oriolsb, after two
  review rounds of the proposal ("the proposal makes sense").
- **Evidence (legacy code only):**
  - `core/accounts.py`: registration and login look an email up by exact
    key (`email in self.game.accounts`), so `Ana@example.com` and
    `ana@example.com` are two accounts.
  - `core/state.py`: a finished game holds only `name`, `score` and
    `moves`, and the leaderboard lives in memory; a high-score line holds
    only `name`, `score` and `at` (decision 0002). No win names an account.
  - There is no session and no token: a login takes the email and the
    password, and the player sid then acts as the credential of every
    command.

## Context

Players want more from their accounts, and the account model of today
cannot carry it. An email in two letter cases is two accounts. Nothing
links a win to an account, and the leaderboard is gone after a restart.
There is no way to change a name or to delete an account, and the name
is written into the saves, the snapshot, the chat, the leaderboard and
the high-score file.

The constraints:

- The `accounts` table is a contract with every stored account and every
  server version (decision 0005, `STORE-2`); the password digest stays as
  it is (`STORE-3`, still contested).
- The high-score file is read by a marketing job outside this repository
  (decision 0002), and Product gives marketing no support for these
  features.
- There is no login session, and adding one is out of scope.
- The player sid acts as a credential: anyone who knows it can play the
  player. It must not become public.

## Decision

1. **One email, one person.** A registration is refused when its email
   matches an account ignoring letter case (`ACCOUNT-3`). A login, a change
   of name and a deletion match the exact email first, then the email
   ignoring letter case, and among case variants the one whose password
   matches, the first one stored (`ACCOUNT-7`). The accounts that already
   exist as case variants stay as they are, and nothing is merged.
2. **Proof of ownership.** A change of name and a deletion take the email
   and the password in the body, as a login does. A wrong pair is refused
   with the login's message and status, and changes nothing (`ACCOUNT-12`).
3. **A public profile with its own sid.** Each account has a profile sid,
   in the digit form of a player sid, that grants nothing.
   `GET /profiles/{profileSid}` shows the name, the games won and the best
   score, with no credential and no email (`ACCOUNT-8`, `ACCOUNT-9`,
   `ACCOUNT-16`). The register, login and rename answers and the leaderboard
   carry the profile sid (`ACCOUNT-1`, `ACCOUNT-4`, `ACCOUNT-11`, `WIN-2`).
4. **Wins count from this change on.** A win of an account's player is kept
   with the account in the database file (`ACCOUNT-10`). Older wins count for
   no profile.
5. **A change of name** renames the account, its profile and its active
   player. Wins, high-score lines and chat messages keep the name they were
   made with (`ACCOUNT-11`).
6. **A deletion** removes the account, its profile, its kept wins, the save
   and the snapshot of its player, its active player and that player's chat
   messages (`ACCOUNT-13`). The account's wins stay on the leaderboard, named
   `DELETED PLAYER`, in their rank (`ACCOUNT-14`), and that name is reserved
   (`PLAYER-4`). The email can register again, with a new and empty profile
   (`ACCOUNT-15`).
7. **The high-score file is not touched.** Each win still appends its line,
   and a deletion does not rewrite it. Decision 0002 stands.
8. **New tables, not new columns.** Profiles and wins live in the tables
   `profiles` and `wins` of the database file (`STORE-4`). A server that
   starts on an older file creates them, and gives each account a profile
   sid.
9. **Contract 2.0.0, with no backward compatibility.** `openapi.yaml` adds
   three operations and the key `profileSid`, and keeps no form of the old
   shapes for a client that rejects unknown keys.

## Alternatives rejected

| Alternative | Why you rejected it |
| --- | --- |
| A login token or a session for the change of name and the deletion | A larger change, with its own lifetime and revocation rules; out of scope for this need. The email and password give the same proof today. |
| The player sid as the proof of ownership | It shows up in URLs and in the list of players; anyone who saw it could delete the account. |
| Merge the case-variant accounts at start | It must pick one password, one name and one snapshot: a person loses a game, or gets locked out. |
| Refuse to start while case variants exist | It stops every player until a person fixes rows by hand. |
| Store emails in lower case, and change the existing rows | It edits the `accounts` table, a contract with every server version (decision 0005), and it collides the existing variants. |
| The player sid, or the email, as the public profile identifier | The player sid is a credential; the email must never be public (`ACCOUNT-9`). |
| Count the older wins, matched by name in the high-score file | Names are not unique: two players named ANA would share wins. |
| Remove a deleted account's wins from the leaderboard | It changes the ranks of every other player. |
| Rewrite the high-score file on a deletion, with `DELETED PLAYER` in the account's lines | It breaks decision 0002 ("the file is only appended to") and needs marketing to accept changed lines; Product gives marketing no support for these features. |
| Stop writing the high-score line for an account's player | It changes `WIN-3` for marketing, which this change does not support. |
| New columns on the `accounts` table for the profile sid and the wins | It changes `STORE-2`, which an older server reads; new tables leave it as it is. |
| Expand, migrate and contract the answer shapes (keep 1.0.0 beside 2.0.0) | The review of 2026-11-26 asks for no backward compatibility; nothing is removed or renamed, only keys are added. |

Design it twice was not run: each choice was reviewed as a question with
its alternatives in the proposal's two review rounds.

## Consequences

- **A known gap in the need.** "Nothing that identifies the player" does not
  hold for the high-score file: it keeps the name of each win, a deleted
  account's included, and the copies the marketing job has already read are
  out of reach. `ACCOUNT-13` and its fitness function exclude that file on
  purpose. A later need that gives marketing support closes the gap, and
  replaces this point and decision 0002.
- **An account wins at most once today.** After a win, a login gives back the
  won player (`ACCOUNT-4`), who can't move (`MOVE-7`); `gamesWon` is 0 or 1,
  and "best score" has one value. A rule that lets an account start a new
  game is a later need.
- **Deleted rows must leave the file.** The fitness function of `ACCOUNT-13`
  searches the database file byte by byte, and SQLite keeps deleted rows in
  free pages. The code needs `PRAGMA secure_delete` or a `VACUUM` after a
  deletion.
- **Consumers break.** Mobile client v1 breaks if it rejects unknown keys.
  The web client's mock `Account` (`web/tests/mocks/bodies.ts`) fails the
  contract, and its generated types are stale: a web change follows.
- **The recorded answers change.** The transcripts of decision 0010 hold the
  old answers of register, login and the leaderboard; they are recorded
  again from the code of this decision, and only from it.
- **Case variants remain.** The accounts stored as case variants before this
  change stay two accounts; a login in a third letter case reaches the first
  one whose password matches.
- **The password digest stays unsalted** (`STORE-3`): the change of name and
  the deletion add two more routes that check it.
- The code calls the snapshot a "profile" (`core/accounts.py`); a
  regeneration renames it, so that "profile" means the public view only.

## Fitness functions

| Function | Target | How to run it | Need that it protects |
| --- | --- | --- | --- |
| No public answer holds the email (`ACCOUNT-9`, `fitness/privacy.feature`) | pass; fails today | `uv run pytest brown_field/tests -m ACCOUNT-9` | The email is never public |
| After a deletion, the API and the database file, byte by byte, hold neither the email, the name nor the player sid, before and after a restart (`ACCOUNT-13`, `fitness/privacy.feature`) | pass; fails today | `uv run pytest brown_field/tests -m ACCOUNT-13` | The game holds nothing that identifies a deleted player (the high-score file excepted) |
| The contract test covers the 19 operations (`tests/contract/test_contract.py`) | pass; fails today on the 6 new or changed operations | `uv run pytest brown_field/tests/contract` | Every client sees the shapes of `openapi.yaml` 2.0.0 |
| The other rules do not change | every scenario outside the change passes before and after | `uv run pytest brown_field/tests` | Players, the web client and the marketing job keep what they have |
