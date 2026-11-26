"""The high-score file for the marketing job (WIN-3, CONF-2, decision 0002)."""

import json
import os
from datetime import datetime, timezone


class JsonlHighScores:
    def append(self, name: str, score: int) -> None:
        # The marketing leaderboard reads this file every night. Keep the format.
        path = os.environ.get("KATACOMBS_HIGHSCORES", "highscores.jsonl")
        line = {
            "name": name,
            "score": score,
            "at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        }
        with open(path, "a", encoding="utf-8") as file:
            file.write(json.dumps(line) + "\n")
