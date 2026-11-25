"""Write the golden transcripts with the legacy code, through its REST API.

Run it from the package root, only against the original code:

    uv run python brown_field/tests/golden/make_transcripts.py

Like make_golden.py: never run it against a rewrite, or the transcripts
would agree with the new code by construction. Record them again only on
purpose, in the commit of the decision record that changes a behavior.
"""

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2]))

from brown_field.api import create_app  # noqa: E402
from brown_field.tests.golden.transcripts import recording, sessions  # noqa: E402

OUT = HERE / "transcripts"


def main() -> None:
    OUT.mkdir(exist_ok=True)
    for name, session in sessions().items():
        with recording(create_app) as recorder:
            lines = [json.dumps(line, ensure_ascii=False) for line in session(recorder)]
        (OUT / name).write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(f"{name}: {len(lines)} lines")


if __name__ == "__main__":
    main()
