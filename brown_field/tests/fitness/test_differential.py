"""Fitness: the code answers every session as a baseline version does (decision 0012).

A differential run. A baseline revision of the repository (by default
`10a5221`, the legacy code before change modular-core) and the tree under
test answer the same REST sessions, and every answer and every file row
must be the same:

- 50 seeded random sessions of 300 requests (`golden/transcripts.py`),
  50 rat sessions, and the scripted session;
- under 18 conditions: the time zones UTC, Asia/Kolkata (+5:30, so the local
  minute differs from the UTC minute) and America/New_York; the start times
  10:10, 10:20 and 10:52 UTC, which put the market inside and outside its
  cleaning window in local time; the rat stopped, and the rat drawing from
  a seeded `random`.

A second test is the control: a copy of the tree with the market reading
UTC must differ from the tree, or the comparison cannot see a difference.

It needs the git history and takes about 10 minutes, so it is opt-in:

    KATACOMBS_DIFFERENTIAL=1 uv run pytest brown_field/tests -m differential

`KATACOMBS_BASELINE` sets the baseline revision, `KATACOMBS_DIFF_SEEDS` the
seeds per condition (default 50). A behavior change that a decision record
accepts moves the baseline to the revision that holds it.
"""

import gzip
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
DRIVER = Path(__file__).parent / "differential" / "driver.py"
GENERATOR = ROOT / "brown_field" / "tests" / "golden" / "transcripts.py"
BASELINE = os.environ.get("KATACOMBS_BASELINE", "10a5221")
SEEDS = int(os.environ.get("KATACOMBS_DIFF_SEEDS", "50"))
CONTROL_SEEDS = 3

pytestmark = [
    pytest.mark.fitness,
    pytest.mark.differential,
    pytest.mark.skipif(not os.environ.get("KATACOMBS_DIFFERENTIAL"), reason="opt-in: set KATACOMBS_DIFFERENTIAL=1"),
]


def start(tree: Path, out: Path, seeds: int) -> subprocess.Popen:
    env = {k: v for k, v in os.environ.items() if k != "VIRTUAL_ENV"}
    env["PYTHONPATH"] = str(tree)
    return subprocess.Popen(
        [sys.executable, str(DRIVER), str(tree), str(GENERATOR), str(out), str(seeds)],
        cwd=tree, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
    )


def finish(run: subprocess.Popen) -> None:
    output, _ = run.communicate()
    assert run.returncode == 0, output[-3000:]


def load(path: Path) -> tuple[str, dict[str, dict]]:
    with gzip.open(path, "rt", encoding="utf-8") as file:
        rows = [json.loads(line) for line in file]
    return rows[0]["loaded"], {row["key"]: row for row in rows[1:]}


def differences(a: Path, b: Path) -> tuple[list[str], int]:
    """The sessions of `a` whose answers differ in `b`, and the requests compared."""
    (loaded_a, left), (loaded_b, right) = load(a), load(b)
    assert loaded_a != loaded_b, f"both runs imported {loaded_a}"
    found, requests = [], 0
    for key, row in left.items():
        assert key in right, f"{key} is missing from {b.name}"
        requests += sum(1 for line in row["lines"] if '"status"' in line)
        if row["sha"] != right[key]["sha"]:
            first = next(i for i, (x, y) in enumerate(zip(row["lines"] + [None], right[key]["lines"] + [None])) if x != y)
            found.append(f"{key}, line {first}:\n  {row['lines'][first] if first < len(row['lines']) else None}\n"
                         f"  {right[key]['lines'][first] if first < len(right[key]['lines']) else None}")
    return found, requests


@pytest.fixture(scope="module")
def current_run(tmp_path_factory) -> Path:
    """The tree under test answers the sessions; the baseline runs beside it in its own worktree."""
    folder = tmp_path_factory.mktemp("differential")
    baseline = folder / "baseline"
    subprocess.run(["git", "-C", str(ROOT), "worktree", "add", "--detach", str(baseline), BASELINE],
                   check=True, capture_output=True, text=True)
    try:
        runs = [start(baseline, folder / "baseline.jsonl.gz", SEEDS), start(ROOT, folder / "current.jsonl.gz", SEEDS)]
        for run in runs:
            finish(run)
    finally:
        subprocess.run(["git", "-C", str(ROOT), "worktree", "remove", "--force", str(baseline)], capture_output=True)
    return folder


def test_every_session_answers_as_the_baseline(current_run):
    found, requests = differences(current_run / "baseline.jsonl.gz", current_run / "current.jsonl.gz")
    assert requests > 0
    assert not found, f"{len(found)} sessions differ from {BASELINE}:\n" + "\n".join(found[:5])


def test_the_comparison_sees_a_planted_difference(current_run, tmp_path):
    """The control: the market reads UTC instead of the local wall clock (MOVE-6)."""
    tree = tmp_path / "planted"
    shutil.copytree(ROOT / "brown_field", tree / "brown_field",
                    ignore=shutil.ignore_patterns("web", "tests", "__pycache__", ".pytest_cache"))
    rules = tree / "brown_field" / "core" / "rules.py"
    source = rules.read_text(encoding="utf-8")
    assert source.count("clock.local_now().minute") == 1, "the market rule moved: update the control"
    rules.write_text(source.replace("clock.local_now().minute", "clock.utc_now().minute"), encoding="utf-8")
    finish(start(tree, tmp_path / "planted.jsonl.gz", CONTROL_SEEDS))
    found, _ = differences(tmp_path / "planted.jsonl.gz", current_run / "current.jsonl.gz")
    assert found, "a market that reads UTC answers like the tree: the comparison sees nothing"
    assert all(entry.startswith("Asia/Kolkata|") for entry in found), found[:3]
