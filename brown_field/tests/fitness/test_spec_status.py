"""Fitness: the status of each rule tells a reader whether anybody decided it.

README step 6: each rule has one status, observed, accepted or contested.
This check fails when the labels drift from the evidence:

- every rule of both specifications has exactly one Status;
- an accepted rule cites a decision record that exists and traces to it;
- a contested rule states its open question;
- every rule that a @contested scenario pins is contested;
- the banner of each specification counts the statuses right.
"""

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SPECS = [ROOT / "spec" / "specification.md", ROOT / "web" / "spec" / "specification.md"]
DECISIONS = ROOT / "decisions"
FEATURES = ROOT / "tests"
RULE = re.compile(r"^#### ([A-Z][A-Z0-9-]*-\d+) — .+?\n(.*?)(?=^#### |^### |^## |\Z)", re.M | re.S)
STATUS = re.compile(r"^- Status: (observed|accepted|contested)\b(.*)$", re.M)

pytestmark = pytest.mark.fitness


@pytest.fixture(autouse=True, scope="module")
def the_inputs_exist():
    """Name a missing input folder: a copy of the primitives must hold all three."""
    for needed in (*SPECS, DECISIONS):
        assert needed.exists(), (
            f"{needed.relative_to(ROOT.parent)} is missing: this check reads both "
            "specifications and the decision records; copy brown_field/web/spec/ "
            "and brown_field/decisions/ with the tests"
        )


def rules(spec: Path) -> dict[str, str]:
    return {m.group(1): m.group(2) for m in RULE.finditer(spec.read_text(encoding="utf-8"))}


def statuses(spec: Path) -> dict[str, tuple[str, str]]:
    found = {}
    for rule_id, body in rules(spec).items():
        lines = STATUS.findall(body)
        assert len(lines) == 1, f"{rule_id} in {spec.name} has {len(lines)} Status lines"
        found[rule_id] = lines[0]
    return found


def decision_traces() -> dict[str, str]:
    traces = {}
    for record in DECISIONS.glob("[0-9][0-9][0-9][0-9]-*.md"):
        text = record.read_text(encoding="utf-8")
        traces[record.name[:4]] = re.search(r"\*\*Traces to:\*\* (.+?)\n- \*\*", text, re.S).group(1)
    return traces


@pytest.mark.parametrize("spec", SPECS, ids=["server", "client"])
def test_every_rule_has_one_status(spec):
    assert statuses(spec)


@pytest.mark.parametrize("spec", SPECS, ids=["server", "client"])
def test_an_accepted_rule_cites_a_record_that_traces_to_it(spec):
    traces = decision_traces()
    for rule_id, (status, rest) in statuses(spec).items():
        if status != "accepted":
            continue
        cited = re.search(r"decision (\d{4})", rest)
        assert cited, f"{rule_id} is accepted but cites no decision"
        assert cited.group(1) in traces, f"{rule_id} cites decision {cited.group(1)}, which does not exist"
        assert f"`{rule_id}`" in traces[cited.group(1)], f"decision {cited.group(1)} does not trace to {rule_id}"


@pytest.mark.parametrize("spec", SPECS, ids=["server", "client"])
def test_a_contested_rule_states_its_open_question(spec):
    for rule_id, (status, rest) in statuses(spec).items():
        if status == "contested":
            assert "Open question:" in rest, f"{rule_id} is contested but states no open question"
            assert "?" in rest.split("Open question:", 1)[1], f"{rule_id}: its open question asks nothing"


def test_every_rule_that_a_contested_scenario_pins_is_contested():
    status = {**statuses(SPECS[0]), **statuses(SPECS[1])}
    for feature in FEATURES.rglob("*.feature"):
        pending: list[str] = []
        for line in feature.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line.startswith("@"):
                pending += re.findall(r"@([^\s@]+)", line)
            elif line.startswith(("Scenario:", "Scenario Outline:")):
                if "contested" in pending:
                    for tag in pending:
                        if tag in status:
                            assert status[tag][0] == "contested", f"{feature.name}: {tag} is pinned as contested"
                pending = []
            elif line.startswith("Feature:"):
                pending = []


@pytest.mark.parametrize("spec", SPECS, ids=["server", "client"])
def test_the_banner_counts_the_statuses(spec):
    text = spec.read_text(encoding="utf-8")
    counted = [status for status, _ in statuses(spec).values()]
    for name in ("observed", "accepted", "contested"):
        assert f"**{counted.count(name)} {name}**" in text, f"the banner of {spec.name} miscounts {name}"
