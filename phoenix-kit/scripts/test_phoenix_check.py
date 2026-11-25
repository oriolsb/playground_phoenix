"""Tests for phoenix_check.py. Run: python3 -m unittest discover -s <kit>/scripts"""

from __future__ import annotations

import contextlib
import io
import json
import shutil
import subprocess
import tempfile
import textwrap
import unittest
from pathlib import Path

import phoenix_check as pc

BLOCK = """```phoenix
system: Katacombs
spec: spec/specification.md
changes: spec/changes
decisions: spec/decisions
map: spec/test-scenarios.md
tests: tests
code: src
junit: junit.xml
primitives: PHOENIX.md, spec, tests
rule_id: [A-Z]+-\\d+
```
"""

SPEC = """# Spec

## Rules

#### BAG-1 — The bag holds at most 10 items

- Source: brief.
- Rule: When a player with 10 items takes an item, Katacombs shall refuse
  the action.
- Why: the limit forces a choice.
- Observable result: `BAG_FULL`.

#### OPS-1 — Fast

- Source: operations.
- Rule: each command responds in less than 100 ms.
- Why: players wait.
- Observable result: p99 below 100 ms.

### API-1 — One entry point

- Source: workshop.
- Rule: Katacombs shall export one entry point.
- Why: the tests import it.
- Observable result: `build()` exists.
"""


class Project:
    def __init__(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.write("PHOENIX.md", "# PHOENIX\n\n" + BLOCK)
        self.write("spec/specification.md", SPEC)
        self.write("spec/test-scenarios.md", "# Map\n\nApproved:\n\n| BAG-1 | OPS-1 | API-1 |\n")
        self.write("tests/bag.feature", "@BAG-1\nFeature: Bag\n  @OPS-1 @API-1\n  Scenario: Full\n    Given x\n")
        self.write("spec/decisions/0001-one.md", "# 0001 — One\n\n- **Status:** accepted\n- **Date:** 2026-01-01\n- **Change:** `grow`.\n\n## Alternatives rejected\n\n| Alt | Why |\n| --- | --- |\n| Ten | Too few |\n")
        self.write("spec/decisions/adr-index.md", "| [0001](0001-one.md) | One |\n")

    def write(self, rel: str, text: str) -> None:
        p = self.root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")

    def cfg(self) -> pc.Config:
        return pc.Config(self.root)

    def close(self) -> None:
        self.tmp.cleanup()


def messages(report: pc.Report, level: str = "error") -> list[str]:
    return [f["message"] for f in report.findings if f["level"] == level]


class EarsTest(unittest.TestCase):
    def test_patterns(self):
        good = [
            "Katacombs shall keep one world.",
            "The domain code shall not import the adapters.",
            "When a player takes an item, Katacombs shall move it.",
            "While the game is won, when a player sends GO, Katacombs shall refuse.",
            "If the bag is full, then Katacombs shall refuse the action.",
            "Where chat is on, Katacombs shall show messages.",
        ]
        for text in good:
            self.assertIsNone(pc.ears_problem(text), text)
        bad = [
            "each command responds in less than 100 ms.",
            "Two commands can arrive. Then Katacombs shall order them.",
            "If the bag is full, Katacombs shall refuse.",
            "For each exit from A to B, Katacombs shall have an exit back.",
        ]
        for text in bad:
            self.assertIsNotNone(pc.ears_problem(text), text)


class ChecksTest(unittest.TestCase):
    def setUp(self):
        self.p = Project()

    def tearDown(self):
        self.p.close()

    def test_config_allows_a_green_field(self):
        for rel in ("spec", "tests"):
            shutil.rmtree(self.p.root / rel)
        r = pc.check_config(self.p.cfg())
        self.assertEqual(r.count("error"), 0)
        self.assertTrue(any("spec: path does not exist yet" in m for m in messages(r, "warning")))

    def test_config_needs_the_map_of_paths(self):
        (self.p.root / "PHOENIX.md").unlink()
        r = pc.check_config(self.p.cfg())
        self.assertTrue(any("PHOENIX.md is missing" in m for m in messages(r)))

    def test_rules_parse_levels_and_warn_on_ears(self):
        r = pc.check_rules(self.p.cfg())
        self.assertEqual(r.data["rules"], 3)
        self.assertEqual(r.count("error"), 0)
        self.assertTrue(any("OPS-1 is not in EARS form" in m for m in messages(r, "warning")))

    def test_missing_bullet_is_an_error(self):
        self.p.write("spec/specification.md", SPEC.replace("- Why: the limit forces a choice.\n", ""))
        self.assertIn("BAG-1 has no 'Why:' bullet", messages(pc.check_rules(self.p.cfg())))

    def test_trace_finds_untagged_rule_and_unknown_tag(self):
        self.p.write("tests/bag.feature", "Feature: Bag\n  @BAG-1 @BAG-9 @US-01\n  Scenario: Full\n    Given x\n")
        errors = messages(pc.check_trace(self.p.cfg()))
        self.assertTrue(any("@BAG-9, which is not a rule" in m for m in errors))
        self.assertTrue(any("OPS-1 has no scenario" in m for m in errors))
        self.assertFalse(any("US-01" in m for m in errors))

    def test_delta_modified_must_keep_every_bullet(self):
        self.p.write("spec/changes/grow/proposal.md", "# P\n")
        self.p.write("spec/changes/grow/delta.md", "## MODIFIED Rules\n\n#### BAG-1 — Twelve\n\n- Source: b.\n- Rule: When x, Katacombs shall y.\n")
        errors = messages(pc.check_deltas(self.p.cfg(), None, archive=False))
        self.assertTrue(any("drops bullet(s)" in m and "Why" in m for m in errors))

    def test_delta_archive_rejects_placeholders(self):
        self.p.write("spec/changes/grow/proposal.md", "# P\n")
        self.p.write("spec/changes/grow/delta.md", textwrap.dedent("""\
            ## MODIFIED Rules

            #### BAG-1 — Twelve

            - Source: b.
            - Rule: When x, Katacombs shall y.
            - Why: w.
            - Observable result: o.
            - Revised: YYYY-MM-DD. Decision NNNN.
            """))
        self.assertTrue(any("placeholder" in m for m in messages(pc.check_deltas(self.p.cfg(), "grow", archive=True))))

    def test_oldvalues_reads_each_literal_and_flags_a_combined_cell(self):
        self.p.write("spec/changes/grow/proposal.md", "# P\n")
        self.p.write("spec/changes/grow/delta.md", textwrap.dedent("""\
            ## Old values

            | Rule ID | Old value | New value |
            | --- | --- | --- |
            | BAG-1 | `at most 10 items` (title) | `at most 12 items` |
            | BAG-1 | `at most 10 items`, `OPS-1` | `at most 12 items`, `PERF-1` |
            """))
        r = pc.check_oldvalues(self.p.cfg(), "grow")
        self.assertIn("at most 10 items", r.data["patterns"])
        self.assertIn("OPS-1", r.data["patterns"])
        self.assertFalse(any("(title)" in p for p in r.data["patterns"]))
        self.assertTrue(any("one old value per row" in m for m in messages(r, "warning")))
        self.assertTrue(any(h["old"] == "at most 10 items" for h in r.data["hits"]))

    def run_cli(self, *argv: str) -> tuple[int, dict]:
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = pc.main(list(argv))
        return code, json.loads(out.getvalue())

    def test_json_gives_the_data_that_the_text_omits(self):
        self.p.write("spec/changes/grow/proposal.md", "# P\n")
        self.p.write("spec/changes/grow/delta.md", "## Old values\n\n| Rule ID | Old value | New value |\n| --- | --- | --- |\n| BAG-1 | `at most 10 items` | `at most 12 items` |\n")
        self.p.write("tests/steps/test_bag.py", "# BAG-1: at most 10 items\n")
        self.p.write("PHOENIX.md", "# PHOENIX\n\n" + BLOCK + "\n## Units\n\n| Unit | Rules | Interface | Modules | Risk |\n| --- | --- | --- | --- | --- |\n| bag | BAG-1 | `build` | `src` | low |\n")
        root = str(self.p.root)
        _, ov = self.run_cli("oldvalues", "--change", "grow", "--root", root, "--json")
        self.assertIn("tests/steps/test_bag.py", [h["path"] for h in ov["data"]["hits"]])
        _, un = self.run_cli("--root", root, "--json", "units", "show", "bag")
        self.assertEqual(un["data"]["unit"]["rules"], ["BAG-1"])

    def test_strict_makes_an_ears_warning_fail_the_rules_check(self):
        root = str(self.p.root)
        code, _ = self.run_cli("rules", "--root", root, "--json")
        self.assertEqual(code, 0)
        code, out = self.run_cli("rules", "--root", root, "--json", "--strict")
        self.assertEqual(code, 1)
        self.assertTrue(any("OPS-1 is not in EARS form" in f["message"] for f in out["findings"]))

    def test_config_runs_on_a_proposal_in_a_scratch_folder(self):
        scratch = self.p.root / ".phoenix" / "proposal"
        scratch.mkdir(parents=True)
        shutil.move(str(self.p.root / "PHOENIX.md"), scratch / "PHOENIX.md")
        code, r = self.run_cli("config", "--root", str(scratch), "--json")
        self.assertEqual((code, r["errors"]), (0, 0), r["findings"])
        (scratch / "PHOENIX.md").write_text(BLOCK.replace("[A-Z]+-\\d+", "[A-Z+"), encoding="utf-8")
        code, r = self.run_cli("config", "--root", str(scratch), "--json")
        self.assertEqual(code, 1)

    def test_decisions_index_and_change(self):
        self.p.write("spec/decisions/0003-three.md", "# 0003\n\n- **Status:** accepted\n- **Date:** 2026-01-02\n\n## Alternatives rejected\n\n| A | B |\n| --- | --- |\n| | |\n")
        r = pc.check_decisions(self.p.cfg(), "grow")
        errors = messages(r)
        self.assertTrue(any("0003-three.md is linked 0 times" in m for m in errors))
        self.assertTrue(any("names no alternative" in m for m in errors))
        self.assertEqual(r.data["records_for_change"], ["0001-one.md"])
        self.assertTrue(any("0002" in m for m in messages(r, "warning")))

    def test_approval_is_tied_to_the_suite(self):
        cfg = self.p.cfg()
        self.assertFalse(pc.check_approval(cfg, "verify", None).ok(False))
        pc.check_approval(cfg, "stamp", "Ana")
        self.assertTrue(pc.check_approval(cfg, "verify", None).ok(False))
        self.p.write("tests/bag.feature", "@BAG-1\nFeature: changed\n")
        self.assertIn("suite changed", " ".join(messages(pc.check_approval(cfg, "verify", None))))

    def test_status_names_the_next_step(self):
        cfg = self.p.cfg()
        pc.check_approval(cfg, "stamp", "Ana")
        self.assertEqual(pc.check_status(cfg).data["next"], "/phoenix-kit:generate")
        self.p.write("src/app.py", "")
        self.assertEqual(pc.check_status(cfg).data["next"], "/phoenix-kit:deletion-test")

    def test_timestamp_decision_names_are_checked(self):
        self.p.write("spec/decisions/20261030-1310-flag.md", "# Flag\n\n- **Status:** accepted\n")
        errors = messages(pc.check_decisions(self.p.cfg(), None))
        self.assertTrue(any("20261030-1310-flag.md" in m or "Date" in m for m in errors), errors)

    def test_status_includes_the_config_check(self):
        (self.p.root / "PHOENIX.md").unlink()
        r = pc.check_status(self.p.cfg())
        self.assertFalse(r.ok(False))
        self.assertTrue(any("PHOENIX.md is missing" in m for m in messages(r)))
        self.assertIn("PHOENIX.md", r.data["next"])

    def test_expected_failures_from_trailers(self):
        root = self.p.root
        self.p.write("junit.xml", textwrap.dedent("""\
            <testsuites><testsuite>
              <testcase classname="tests.steps.test_bag" name="test_full[? - x]"><failure message="no"/></testcase>
              <testcase classname="tests.steps.test_bag" name="test_ok"/>
            </testsuite></testsuites>"""))
        git = ["git", "-c", "user.name=t", "-c", "user.email=t@l"]
        subprocess.run(["git", "init", "-q"], cwd=root, check=True)
        subprocess.run(git + ["commit", "-q", "--allow-empty", "-m",
                              "remove\n\nPhoenix-Expected-Fail: tests/steps/test_bag.py::test_full[? - x]"], cwd=root, check=True)
        r = pc.check_expected(self.p.cfg(), "check", run=False, rev="HEAD")
        self.assertTrue(r.ok(True), r.findings)
        subprocess.run(git + ["commit", "-q", "--allow-empty", "-m",
                              "remove\n\nPhoenix-Expected-Fail: tests.steps.test_bag::test_ok"], cwd=root, check=True)
        errors = messages(pc.check_expected(self.p.cfg(), "check", run=False, rev="HEAD"))
        self.assertTrue(any("fails but is not expected" in m for m in errors))
        self.assertTrue(any("expected to fail but passes" in m for m in errors))


    def test_config_rejects_an_unknown_key(self):
        self.p.write("PHOENIX.md", "# PHOENIX\n\n" + BLOCK.replace("tests: tests\n", "test: tests\n# a comment: no key\n"))
        cfg = self.p.cfg()
        self.assertEqual(cfg.get("tests"), "tests")
        r = pc.check_config(cfg)
        self.assertTrue(any("unknown key 'test'" in m for m in messages(r)), r.findings)
        self.assertEqual([f["line"] for f in r.findings if "unknown key" in f["message"]], [9])
        self.assertEqual(len([m for m in messages(r) if "unknown key" in m]), 1)

    def test_oldvalues_warns_in_each_scope_and_fails_in_archive_mode(self):
        self.p.write("spec/changes/grow/proposal.md", "# P\n")
        delta = textwrap.dedent("""\
            ## Old values

            | Rule ID | Old value | New value |
            | --- | --- | --- |
            | BAG-1 | `10 items` | `12 items` |
            """)
        self.p.write("spec/changes/grow/delta.md", delta)
        self.p.write("tests/steps/test_bag.py", "# BAG-1: 10 items\n")
        self.p.write("spec/test-scenarios.md", "# Map\n\nApproved:\n\n| BAG-1 10 items | OPS-1 | API-1 |\n")
        self.p.write("spec/decisions/0001-one.md", "# 0001\n\nWe chose 10 items.\n")
        warned = pc.check_oldvalues(self.p.cfg(), "grow")
        self.assertEqual(warned.count("error"), 0)
        scopes = {m.split(":")[0] for m in messages(warned, "warning")}
        self.assertTrue({"specification", "tests", "map", "decision"} <= scopes, scopes)
        failed = pc.check_oldvalues(self.p.cfg(), "grow", archive=True)
        self.assertEqual({m.split(":")[0] for m in messages(failed)}, {"specification", "tests", "map"})
        self.assertTrue(any(m.startswith("decision:") for m in messages(failed, "warning")))
        self.p.write("spec/changes/grow/delta.md", delta + textwrap.dedent("""\

            ## Kept old values

            | File | Old value | Reason |
            | --- | --- | --- |
            | `tests/steps/test_bag.py` | `10 items` | The comment names the old limit on purpose. |
            """))
        kept = pc.check_oldvalues(self.p.cfg(), "grow", archive=True)
        self.assertFalse(any(m.startswith("tests:") for m in messages(kept)))
        self.assertTrue(any("kept: The comment" in m for m in messages(kept, "info")))
        self.assertEqual(pc.check_deltas(self.p.cfg(), "grow", archive=False).count("warning"), 0)

    def test_status_asks_for_a_new_stamp_after_the_map_changes(self):
        cfg = self.p.cfg()
        pc.check_approval(cfg, "stamp", "Ana")
        self.p.write("spec/test-scenarios.md", self.p.root.joinpath("spec/test-scenarios.md").read_text() + "| BAG-2 |\n")
        self.assertIn("approval stamp", pc.check_status(cfg).data["next"])

    def write_junit(self, *cases: str) -> None:
        self.p.write("junit.xml", "<testsuites><testsuite>" + "".join(cases) + "</testsuite></testsuites>")

    def test_expected_check_with_no_trailers_is_the_whole_system_gate(self):
        root = self.p.root
        git = ["git", "-c", "user.name=t", "-c", "user.email=t@l"]
        subprocess.run(["git", "init", "-q"], cwd=root, check=True)
        subprocess.run(git + ["commit", "-q", "--allow-empty", "-m", "the primitives"], cwd=root, check=True)
        fail = '<testcase classname="tests.test_bag" name="test_{0}"><failure message="no"/></testcase>'
        self.write_junit(fail.format("a"), fail.format("b"))
        r = pc.check_expected(self.p.cfg(), "check", run=False, rev="HEAD")
        self.assertTrue(r.ok(True), r.findings)
        self.assertEqual(r.data["mode"], "whole system")
        self.write_junit('<testcase classname="" name="tests.test_bag"><error message="collection failure"/></testcase>')
        self.assertTrue(pc.check_expected(self.p.cfg(), "check", run=False, rev="HEAD").ok(True))
        self.write_junit(fail.format("a"), '<testcase classname="tests.test_bag" name="test_b"/>')
        errors = messages(pc.check_expected(self.p.cfg(), "check", run=False, rev="HEAD"))
        self.assertTrue(any("1 of 2 test(s) pass before the code" in m for m in errors), errors)

    def test_expected_check_outside_git_is_the_whole_system_gate(self):
        fail = '<testcase classname="tests.test_bag" name="test_a"><failure message="no"/></testcase>'
        self.write_junit(fail)
        r = pc.check_expected(self.p.cfg(), "check", run=False, rev="HEAD")
        self.assertEqual(r.count("error"), 0, r.findings)
        self.assertTrue(any("not a git repository" in m for m in messages(r, "warning")))


if __name__ == "__main__":
    unittest.main()
