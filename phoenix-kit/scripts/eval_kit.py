"""Deterministic evals for the kit itself.

Run from anywhere:

    python3 scripts/eval_kit.py
    python3 scripts/eval_kit.py frontmatter links --json

Each case reads the kit's own files. No model runs, no network. Exit 1
when any case finds a problem.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
KIT = HERE.parent
sys.path.insert(0, str(HERE))

import phoenix_check as pc

CASES: list[tuple[str, object]] = []


def case(fn):
    CASES.append((fn.__name__.removeprefix("case_").replace("_", "-"), fn))
    return fn


def skills() -> list[Path]:
    return sorted(p for p in (KIT / "skills").iterdir() if (p / "SKILL.md").exists())


def frontmatter(text: str) -> dict[str, str]:
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---\n", 4)
    if end < 0:
        return {}
    data: dict[str, str] = {}
    for line in text[4:end].splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            data[key.strip()] = value.strip().strip('"')
    return data


def plain_scalar_problems(text: str) -> list[str]:
    """Top-level values that strict YAML cannot read as one plain string."""
    if not text.startswith("---\n"):
        return []
    end = text.find("\n---\n", 4)
    problems = []
    for line in text[4:end].splitlines():
        if not line or line[0] in " \t#" or ":" not in line:
            continue
        key, value = line.split(":", 1)
        value = value.strip()
        if not value or value[0] in "\"'[{|>&*!":
            continue
        if ": " in value or " #" in value:
            problems.append(f"{key.strip()}: quote the value, it holds ': ' or ' #'")
    return problems


def markdown_files() -> list[Path]:
    return sorted(KIT.rglob("*.md"))


@case
def case_frontmatter() -> list[str]:
    problems = []
    for skill in skills():
        text = (skill / "SKILL.md").read_text(encoding="utf-8")
        data = frontmatter(text)
        problems += [f"{skill.name}: {p}" for p in plain_scalar_problems(text)]
        for key in ("name", "description", "license"):
            if not data.get(key):
                problems.append(f"{skill.name}: frontmatter has no {key}")
        if not (data.get("author") and data.get("version")):
            problems.append(f"{skill.name}: metadata needs author and version")
        if data.get("name") and data["name"] != skill.name:
            problems.append(f"{skill.name}: name is {data['name']}")
    return problems


@case
def case_budget() -> list[str]:
    problems = []
    for skill in skills():
        lines = len((skill / "SKILL.md").read_text(encoding="utf-8").splitlines())
        if lines > 150:
            problems.append(f"{skill.name}: SKILL.md is {lines} lines (limit 150)")
    return problems


@case
def case_links() -> list[str]:
    problems = []
    link = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
    for md in markdown_files():
        for target in link.findall(md.read_text(encoding="utf-8")):
            path = target.split("#")[0].strip()
            if not path or path.startswith(("http://", "https://", "mailto:")):
                continue
            if not (md.parent / path).resolve().exists():
                problems.append(f"{md.relative_to(KIT)}: {target} does not resolve")
    return problems


@case
def case_contracts() -> list[str]:
    text = (KIT / "CONTRACTS.md").read_text(encoding="utf-8")
    rows = [line.split("|")[1].strip().strip("`").strip()
            for line in text.splitlines() if line.startswith("|") and line.count("|") > 2]
    problems = []
    for skill in skills():
        if not any(row == skill.name or row.startswith(skill.name + " ") for row in rows):
            problems.append(f"{skill.name}: no row in CONTRACTS.md")
    return problems


@case
def case_commands() -> list[str]:
    source = (HERE / "phoenix_check.py").read_text(encoding="utf-8")
    known = set(re.findall(r'add_parser\("([a-z]+)"\)', source))
    for group in re.findall(r"for name in \(([^)]+)\)", source):
        known.update(re.findall(r'"([a-z]+)"', group))
    actions = {"approval": {"hash", "stamp", "verify", "clear"},
               "expected": {"record", "check"},
               "units": {"show"}}
    problems = []
    span = re.compile(r"`(check [^`]+)`")
    for md in markdown_files():
        if ".venv" in str(md):
            continue
        for text in span.findall(md.read_text(encoding="utf-8")):
            words = text.split()
            command = words[1] if len(words) > 1 else ""
            if command not in known:
                problems.append(f"{md.relative_to(KIT)}: `{text}` names no checker command")
                continue
            if command in actions and len(words) > 2 and not words[2].startswith("--"):
                if words[2] not in actions[command]:
                    problems.append(f"{md.relative_to(KIT)}: `{text}` names no {command} action")
    return problems


@case
def case_presets() -> list[str]:
    problems = []
    for name in ("PHOENIX.md", "PHOENIX.workshop.md"):
        text = (KIT / "templates" / name).read_text(encoding="utf-8")
        match = re.search(r"```phoenix\n(.*?)```", text, re.S)
        if not match:
            problems.append(f"templates/{name}: no phoenix machine block")
            continue
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "PHOENIX.md").write_text(text, encoding="utf-8")
            cfg = pc.Config(root)
            if not cfg.found_block:
                problems.append(f"templates/{name}: the block does not parse")
                continue
            for key in ("spec", "map", "tests", "code", "primitives", "rule_id"):
                if not cfg.get(key):
                    problems.append(f"templates/{name}: no {key}")
            if pc.check_config(cfg).count("error"):
                problems.append(f"templates/{name}: check config fails on a new project")
    return problems


@case
def case_checker_tests() -> list[str]:
    result = subprocess.run(
        [sys.executable, "-m", "unittest", "-q", "test_phoenix_check"],
        cwd=HERE, capture_output=True, text=True,
    )
    if result.returncode:
        return [f"scripts/test_phoenix_check.py fails:\n{result.stderr.strip()}"]
    return []


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("cases", nargs="*", help="case names (default: all)")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    chosen = [(name, fn) for name, fn in CASES if not args.cases or name in args.cases]
    unknown = sorted(set(args.cases) - {name for name, _ in CASES})
    if unknown:
        parser.error(f"unknown case(s): {', '.join(unknown)}")

    results = []
    for name, fn in chosen:
        problems = fn()
        results.append({"case": name, "ok": not problems, "findings": problems})

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        for result in results:
            verdict = "PASS" if result["ok"] else "FAIL"
            print(f"{verdict} {result['case']}")
            for problem in result["findings"]:
                print(f"     {problem}")
        failed = sum(not r["ok"] for r in results)
        print(f"{len(results) - failed} passed, {failed} failed")
    return 0 if all(r["ok"] for r in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
