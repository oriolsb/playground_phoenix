# Golden fixtures

Data that the **legacy** server wrote. A rewrite must still read it: real
players and accounts live in these files in production.

| File | Holds | Written by |
| --- | --- | --- |
| `katacombs.db` | One save (GOLDEN SAVER, at OLD TRUMAN BREWERY, with a BEER, gold 5, energy 11). One account (`golden@example.org`, password `golden-password`, unsalted SHA-256) whose player quit at BREWERY ROOFTOP and left a snapshot. | the legacy code, through the REST API |
| `highscores.jsonl` | Two high-score lines, as the marketing job reads them | the legacy code, two wins |
| `old-save-without-energy.db` | One save with the payload of before 2023: no `energy`, no `moves` (`game.py:754`) | derived from the save above. The legacy code no longer writes this shape. |
| `golden.json` | The manifest: the sids, the credentials, and the expected state | `make_golden.py` |
| `transcripts/*.jsonl` | 7 sessions of requests and the legacy answers to each, then the files: 6 random sessions of 300 requests, 1 scripted session (accounts, restarts, the manhole, a win). Sids are P0, P1…; the folder is TMP; the clock is 10:10:00 UTC plus one second per request; the rat never runs. | `make_transcripts.py`, with the sessions of `transcripts.py` |

Tests get them through the `golden` and `golden_old_save` fixtures in
`conftest.py`. The fixtures copy the files into `tmp_path`, so the committed
files never change.

To rebuild them, only from the original code:

```sh
uv run python brown_field/tests/golden/make_golden.py
```

The random source is seeded and the clock is fixed, so a rebuild is
identical. Never rebuild them from a rewrite: the fixtures would then agree
with the new code by construction, and they would stop testing anything.

The transcripts the same way, only from the original code, or from the code
of a decision that changes a behavior on purpose (decision 0010):

```sh
uv run python brown_field/tests/golden/make_transcripts.py
```
