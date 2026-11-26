"""The high-score file, the default `HighScoreSink` (WIN-3, CONF-2)."""

import json
import os
from datetime import datetime, timezone


class JsonlHighScores:
    def append(self, name: str, score: int, at: datetime) -> None:
        # The marketing leaderboard reads this file every night. Keep the format.
        path = os.environ.get("KATACOMBS_HIGHSCORES", "highscores.jsonl")
        line = {
            "name": name,
            "score": score,
            "at": at.astimezone(timezone.utc).isoformat(timespec="seconds"),
        }
        with open(path, "a", encoding="utf-8") as file:
            file.write(json.dumps(line) + "\n")
