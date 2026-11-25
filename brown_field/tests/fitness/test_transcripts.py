"""Fitness: replay the golden transcripts that the legacy code recorded.

Each transcript is a session of requests (`golden/transcripts.py`). The
code under test plays the same session, and every answer, status and file
must match the line that the legacy code wrote. This is the differential
check of step 7 without the old code: the old answers are the oracle.

A transcript pins everything, including behavior that nobody decided. It
is not in the rule map. When the group changes a behavior on purpose,
record the transcripts again with `golden/make_transcripts.py` from the
code that implements the decision, in the commit of its decision record.
"""

import json
from pathlib import Path

import pytest

from brown_field.api import create_app
from brown_field.tests.golden.transcripts import recording, sessions

pytestmark = pytest.mark.fitness

FOLDER = Path(__file__).resolve().parents[1] / "golden" / "transcripts"


@pytest.mark.parametrize("name", sorted(sessions()))
def test_the_answers_match_the_recorded_transcript(name):
    expected = [json.loads(line) for line in (FOLDER / name).read_text(encoding="utf-8").splitlines()]
    with recording(create_app) as recorder:
        actual = list(sessions()[name](recorder))
    for number, (want, got) in enumerate(zip(expected, actual), start=1):
        assert got == want, f"{name}, line {number} ({want.get('label')}): the answer differs\n  recorded: {want}\n  now:      {got}"
    assert len(actual) == len(expected), f"{name}: {len(actual)} lines now, {len(expected)} recorded"
