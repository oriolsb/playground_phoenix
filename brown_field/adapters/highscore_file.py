"""The high-score file: one JSON line per win (decision 0002)."""

import json
import os


class JsonlHighScoreSink:
    def append(self, name: str, score: int, at: str) -> None:
        # The marketing leaderboard reads this file every night. Keep the format.
        path = os.environ.get("KATACOMBS_HIGHSCORES", "highscores.jsonl")
        line = {
            "name": name,
            "score": score,
            "at": at,
        }
        with open(path, "a", encoding="utf-8") as file:
            file.write(json.dumps(line) + "\n")
