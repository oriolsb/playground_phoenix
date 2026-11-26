# Proposal — accounts

Structure adapted from the OpenSpec proposal template (MIT).

## Need

- Who: the players, through Product (need "1. Accounts", 2026-11-26).
- Why: players have accounts today and want more from them. One email
  is one person, whatever its letter case. Each person has a public
  profile that other players can see, without the email. A person can
  change the name, and can delete the account so that the game holds
  nothing that identifies them.
- Kind: business.
- Measurable as:
  - `ACCOUNT-3`: a registration of `ana@example.com` after
    `Ana@example.com` is refused (0 new accounts). Today it is accepted.
  - `ACCOUNT-9`: no answer of the API that shows a profile, the leaderboard
    or the players holds an email (0 hits of the email in any answer).
  - `ACCOUNT-13`: after a deletion, a search of the database file and
    every answer of the API for the account's email, the account's name
    and the player sid finds 0 hits. The high-score file is out of this
    measure (review answer 3, round 2): it keeps the name of each win.
  - Source: this change, and Product's need of 2026-11-26.

## What changes

- **One account for each person.** A registration with an email that
  differs from an existing one only in letter case is refused
  (`ACCOUNT-3`). Login ignores letter case: the exact email first, then
  the match that ignores case (`ACCOUNT-7`). The accounts that already
  exist as case variants stay. Each one keeps logging in by its exact
  email, and nothing is merged.
- **A profile.** Each account gets a profile sid, a public identifier that
  is not the email and not the player sid (the player sid acts as a
  credential today). `GET /profiles/{profileSid}` shows the name, the
  games won and the best score (`ACCOUNT-8`, `ACCOUNT-16`). No answer shows
  an email except the account's own register and rename answers
  (`ACCOUNT-9`). A win by an account's player is kept with the account
  and survives a restart (`ACCOUNT-10`). Only wins from this change on
  count: older wins carry only a name, names are not unique, and so they
  can't be traced to an account. Every account answer carries the
  profile sid: the register, login and rename answers (`ACCOUNT-1`,
  `ACCOUNT-4`, `ACCOUNT-11`). The leaderboard carries it too, so other
  players can find a profile (`WIN-2`).
- **Change the name.** With the email and password, a person changes the
  account's name. The new name follows the name rules (`PLAYER-2` to
  `PLAYER-4`) and shows in the profile and on the active player
  (`ACCOUNT-11`). Wins already on the leaderboard keep the name they were
  won with.
- **Delete the account.** With the email and password, a person deletes
  the account (`ACCOUNT-13`). The email can then register again, with an empty
  profile (`ACCOUNT-15`). The deletion removes the account row, the profile, the
  kept wins, the save and the snapshot, the active player and its chat
  messages. The account's wins stay on the leaderboard, with the name
  `DELETED PLAYER` and the same score and move count (`ACCOUNT-14`).
  `DELETED PLAYER` becomes a reserved name (`PLAYER-4`). The high-score
  file isn't touched. Marketing gets nothing from this change, decision
  0002 stands, and the file keeps the name of each win, a deleted
  account's included. This is a known gap in "nothing that identifies
  the player", and decision 0013 must record it.
- **Proof of ownership.** A change of name and a deletion take the email
  and the password in the body, as login does. A wrong pair is refused
  with the login's message (`ACCOUNT-12`). There is no token and no
  session.

**What does not change, and guards the change:**

- the player that login gives, quit and snapshot (`ACCOUNT-4` to
  `ACCOUNT-6`), apart from the case lookup of `ACCOUNT-7` and the
  `profileSid` in the login answer;
- the `accounts` table (`STORE-2`) and the password digest (`STORE-3`,
  still contested). The emails are stored as they were typed. The new
  data lives in new tables (`STORE-4`);
- the high-score file (`WIN-3`, `highscore-line.schema.json`, decision
  0002): each win still appends one line, and nothing rewrites it;
- the leaderboard is still in memory and still empty after a restart
  (`WIN-2`). The profile counts come from the database file;
- the existing routes and their messages.

**Out of scope:** a login token or session, a stronger password hash, a
change of email or password, a profile search or list, the profile sid
in the player list (`PLAYER-6`), merging the case-variant accounts
that already exist, any marketing support for profiles or deletions
(nothing new in the high-score file), and compatibility with clients
that reject unknown fields.

## Answers of the review round (2026-11-26, oriolsb)

1. **Proof of ownership:** the email and password in the body, as login does.
2. **Case variants that already exist:** keep them; the exact match wins
   at login; there is no merge.
3. **The wins of a deleted account:** anonymized as `DELETED PLAYER` on
   the leaderboard. Round 2 overrode the high-score file part (see below).
4. **The wins a profile counts:** from this change on.

## Answers of the review, round 2 (2026-11-26, oriolsb)

1. **The profile sid at login:** always return it. Every account answer
   carries `profileSid`, the login answer too (`ACCOUNT-4` is modified).
2. **Clients that reject unknown fields (mobile v1):** no backward
   compatibility. The added `profileSid` fields ship as they are, with no
   expand-contract split and no version of the old shapes.
3. **Marketing:** no marketing support for these features. The high-score
   file isn't rewritten on a deletion, and decision 0002 isn't revised.
   As a result, a deleted account's name stays in the high-score file.

## Rules

- Added: `ACCOUNT-7`, `ACCOUNT-8`, `ACCOUNT-9`, `ACCOUNT-10`, `ACCOUNT-11`,
  `ACCOUNT-12`, `ACCOUNT-13`, `ACCOUNT-14`, `ACCOUNT-15`, `ACCOUNT-16`, `STORE-4`.
- Modified: `ACCOUNT-1`, `ACCOUNT-3`, `ACCOUNT-4`, `PLAYER-4`, `WIN-2`.
- Removed: none.
- Renamed: none.

## Impact

Contracts that change: `openapi.yaml` (three new operations;
`profileSid` on `Account`, `FinishedGame` and the login answer). The data
at rest gains two tables. The high-score file doesn't change. Consumers:
the web client (in the repo; its MSW mocks validate against
`openapi.yaml`) and mobile client v1 (outside). No backward compatibility
is kept for a client that rejects unknown fields. The marketing job sees
no change.

| Part | Pace layer | Blast radius | Review needed |
| --- | --- | --- | --- |
| Account rules (`core/accounts.py`) | medium | register and login of every client; the account tests guard them | no, beyond this proposal |
| REST routes and shapes (`api.py`, `openapi.yaml`) | fast for the new routes; slow for the added fields | the web client; mobile v1 breaks if it rejects unknown fields (accepted, round 2) | done: round 2 |
| The database file (new tables `profiles`, `wins`) | slow | every server version that reads the file (decision 0005) | **yes** |
| Reserved names (`PLAYER-4`) | medium | anyone who registers or starts a game as `DELETED PLAYER` | no |

## Decision record

<!-- Filled on archive: the NNNN whose Change field names this change. -->
