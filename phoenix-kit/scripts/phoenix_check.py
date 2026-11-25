#!/usr/bin/env python3
"""Phoenix Kit checker: the contracts between the skills, as code.

Checks the artifact grammars in <kit>/schemas/README.md. Standard library
only, Python 3.11 or later. Run from the project root:

    python3 <kit>/scripts/phoenix_check.py <command> [options]

Commands:
    config                      the machine block of PHOENIX.md
    rules                       rule blocks and their EARS form
    trace                       rules <-> scenario tags <-> map <-> code
    delta [--change N] [--archive]
    decisions [--change N]
    oldvalues --change N [--archive]
    units [show NAME]
    approval hash|stamp --by WHO|verify|clear
    expected record|check [--run] [--rev REV]
    status                      the config check, open changes, approval, and the next step

Every command takes --root DIR, --json, and --strict. The exit code is 1 when the
check finds an error (or a warning, with --strict).
"""

from __future__ import annotations

import argparse
import datetime as dt
import fnmatch
import hashlib
import json
import os
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path

DEFAULTS = {
    "system": "the system",
    "spec": "spec/specification.md",
    "spec_detail": "",
    "changes": "spec/changes",
    "decisions": "spec/decisions",
    "decision_index": "",
    "map": "spec/evaluation/test-scenarios.md",
    "contracts": "",
    "tests": "tests",
    "code": "src",
    "unit_tests": "",
    "test_command": "uv run pytest",
    "junit_command": "",
    "junit": ".phoenix/junit.xml",
    "primitives": "PHOENIX.md, spec, tests",
    "sources": "",
    "rule_id": r"[A-Z]+-\d+",
    "reports": ".phoenix/reports",
}
LIST_KEYS = {"spec_detail", "contracts", "primitives", "sources"}
SKIP_DIRS = {"__pycache__", ".pytest_cache", ".hypothesis", ".mypy_cache", ".git", ".venv", "node_modules", ".phoenix"}
SKIP_SUFFIXES = {".pyc", ".pyo"}
REQUIRED_BULLETS = ("Source", "Rule", "Why", "Observable result")
DECISION_STATUS = re.compile(r"^(proposed|accepted|written after the code|replaced by \d{4})$")
RISKS = {"low", "medium", "high", "critical"}
PLACEHOLDER = re.compile(r"\bNNNN\b|YYYY-MM-DD|<[a-z][^<>]{2,}>")
APPROVED = re.compile(r"^Approved:[ \t]*(.*)$", re.M)
TRAILER = "Phoenix-Expected-Fail"
# A decision file: NNNN-<slug>.md, or YYYYMMDD-HHMM-<slug>.md for parallel branches.
DECISION_FILE = re.compile(r"^(\d{8}-\d{4}|\d{4})-.+\.md$")


# --------------------------------------------------------------------------
# Findings


@dataclass
class Report:
    check: str
    findings: list[dict] = field(default_factory=list)
    data: dict = field(default_factory=dict)

    def add(self, level: str, message: str, path: str = "", line: int = 0) -> None:
        self.findings.append({"level": level, "check": self.check, "path": path, "line": line, "message": message})

    def error(self, message: str, path: str = "", line: int = 0) -> None:
        self.add("error", message, path, line)

    def warn(self, message: str, path: str = "", line: int = 0) -> None:
        self.add("warning", message, path, line)

    def count(self, level: str) -> int:
        return sum(1 for f in self.findings if f["level"] == level)

    def ok(self, strict: bool) -> bool:
        return self.count("error") == 0 and (not strict or self.count("warning") == 0)

    def merge(self, other: "Report") -> None:
        self.findings.extend(other.findings)


# --------------------------------------------------------------------------
# Configuration


class Config:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.values = dict(DEFAULTS)
        self.found_block = False
        self.unknown_keys: list[tuple[str, int]] = []
        self.phoenix_md = root / "PHOENIX.md"
        if self.phoenix_md.exists():
            text = self.phoenix_md.read_text(encoding="utf-8")
            m = re.search(r"^```phoenix[ \t]*\n(.*?)^```", text, re.M | re.S)
            if m:
                self.found_block = True
                first = text.count("\n", 0, m.start(1)) + 1
                for n, raw in enumerate(m.group(1).splitlines(), first):
                    line = raw.strip()
                    if not line or line.startswith("#") or ":" not in line:
                        continue
                    key, value = line.split(":", 1)
                    key = key.strip()
                    if key not in DEFAULTS:
                        # A typo must not fall back to the default in silence.
                        self.unknown_keys.append((key, n))
                        continue
                    self.values[key] = value.strip()
        if not self.values["decision_index"]:
            self.values["decision_index"] = self.values["decisions"].rstrip("/") + "/adr-index.md"
        try:
            self.rule_id = re.compile(self.values["rule_id"])
        except re.error:
            # check_config reports the bad pattern; the other checks use the default.
            self.rule_id = re.compile(DEFAULTS["rule_id"])

    def get(self, key: str) -> str:
        return self.values.get(key, "")

    def list(self, key: str) -> list[str]:
        return [v.strip() for v in self.values.get(key, "").split(",") if v.strip()]

    def path(self, key: str) -> Path:
        return self.root / self.get(key)

    def rel(self, path: Path) -> str:
        try:
            return str(path.relative_to(self.root))
        except ValueError:
            return str(path)


def check_config(cfg: Config) -> Report:
    r = Report("config")
    if not cfg.phoenix_md.exists():
        r.error("PHOENIX.md is missing at the project root; copy a preset from the kit's templates/")
    elif not cfg.found_block:
        r.warn("PHOENIX.md has no ```phoenix machine block; the checker uses its defaults", "PHOENIX.md")
    for key, n in cfg.unknown_keys:
        r.error(f"unknown key '{key}' in the machine block; the known keys are: {', '.join(DEFAULTS)}", "PHOENIX.md", n)
    for key in ("spec", "map", "tests", "decisions"):
        if not cfg.path(key).exists():
            r.warn(f"{key}: path does not exist yet: {cfg.get(key)}; a skill creates it", "PHOENIX.md")
    if not cfg.path("code").exists():
        r.warn(f"code: path does not exist yet: {cfg.get('code')}", "PHOENIX.md")
    for key in ("contracts", "sources", "spec_detail", "primitives"):
        for p in cfg.list(key):
            if not (cfg.root / p).exists():
                r.warn(f"{key}: path does not exist yet: {p}", "PHOENIX.md")
    try:
        re.compile(cfg.get("rule_id"))
    except re.error as exc:
        r.error(f"rule_id is not a valid pattern: {exc}", "PHOENIX.md")
    jc = cfg.get("junit_command")
    if not jc:
        r.warn("junit_command is not set; `expected` cannot run the suite", "PHOENIX.md")
    elif cfg.get("junit") not in jc:
        r.warn(f"junit_command does not mention the junit path {cfg.get('junit')}", "PHOENIX.md")
    gi = cfg.root / ".gitignore"
    if not gi.exists() or ".phoenix" not in gi.read_text(encoding="utf-8"):
        r.warn("add .phoenix/ to .gitignore: it holds reports and test results", ".gitignore")
    r.data = {"values": cfg.values, "machine_block": cfg.found_block}
    return r


# --------------------------------------------------------------------------
# Rule blocks


@dataclass
class Rule:
    rid: str
    title: str
    path: str
    line: int
    bullets: dict[str, str]
    labels: list[str]


def parse_rules(text: str, cfg: Config, path: str, levels: tuple[int, ...] = (3, 4)) -> list[Rule]:
    lines = text.splitlines()
    heading = re.compile(r"^(#{1,6})\s+(" + cfg.rule_id.pattern + r")\s+[—–-]\s+(.*\S)\s*$")
    any_heading = re.compile(r"^(#{1,6})\s")
    rules: list[Rule] = []
    i = 0
    while i < len(lines):
        m = heading.match(lines[i])
        if not m or len(m.group(1)) not in levels:
            i += 1
            continue
        level = len(m.group(1))
        start = i
        i += 1
        body: list[str] = []
        while i < len(lines):
            h = any_heading.match(lines[i])
            if h and len(h.group(1)) <= level:
                break
            body.append(lines[i])
            i += 1
        bullets: dict[str, str] = {}
        labels: list[str] = []
        current = None
        for b in body:
            bm = re.match(r"^- ([A-Z][A-Za-z ()/-]*?):\s*(.*)$", b)
            if bm:
                current = bm.group(1).strip()
                labels.append(current)
                bullets[current] = bm.group(2).strip()
            elif current and (b.startswith("  ") or b.startswith("\t")) and b.strip():
                bullets[current] += " " + b.strip()
            elif not b.strip():
                continue
            else:
                current = None
        rules.append(Rule(m.group(2), m.group(3), path, start + 1, bullets, labels))
    return rules


def rule_text(rule: Rule) -> str:
    for key in ("Rule", "Rule (EARS)"):
        if key in rule.bullets:
            return rule.bullets[key]
    return ""


def first_sentence(text: str) -> str:
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z\"`(])", text.strip(), maxsplit=1)
    return parts[0] if parts else ""


def ears_problem(text: str) -> str | None:
    """Return why the rule text breaks the EARS order, or None."""
    sentence = first_sentence(text)
    lowered = sentence.lower()
    if " shall " not in f" {lowered} ":
        if "shall" in text.lower():
            return 'the first sentence has no "shall"; a preamble comes before the rule'
        return 'no "shall"'
    before = sentence[: lowered.index("shall")].strip()
    m = re.match(r"^(While|When|Where|If)\b", before)
    if m:
        if m.group(1) == "If" and not re.search(r"\bthen\b", before):
            return '"If" with no "then" before "shall"'
        if "," not in before:
            return f'"{m.group(1)}" clause is not closed by a comma before the system name'
        return None
    if "," in before or len(before.split()) > 8:
        return f'not an EARS clause before "shall": "{before[:60]}"'
    return None


def collect_rules(cfg: Config, r: Report) -> dict[str, Rule]:
    spec = cfg.path("spec")
    out: dict[str, Rule] = {}
    if not spec.exists():
        r.error(f"specification not found: {cfg.get('spec')}")
        return out
    for rule in parse_rules(spec.read_text(encoding="utf-8"), cfg, cfg.get("spec")):
        if rule.rid in out:
            r.error(f"{rule.rid} appears twice (first at line {out[rule.rid].line})", rule.path, rule.line)
        out[rule.rid] = rule
    return out


def check_rule_block(rule: Rule, r: Report) -> None:
    for name in REQUIRED_BULLETS:
        present = name in rule.bullets or (name == "Rule" and "Rule (EARS)" in rule.bullets)
        if not present:
            r.error(f"{rule.rid} has no '{name}:' bullet", rule.path, rule.line)
    text = rule_text(rule)
    if text:
        problem = ears_problem(text)
        if problem:
            r.warn(f"{rule.rid} is not in EARS form: {problem}", rule.path, rule.line)
        if len(re.findall(r"\bshall\b", text)) > 2:
            r.warn(f"{rule.rid} has more than two 'shall': one behaviour per rule", rule.path, rule.line)


def check_rules(cfg: Config) -> Report:
    r = Report("rules")
    rules = collect_rules(cfg, r)
    for rule in rules.values():
        check_rule_block(rule, r)
    for change in open_changes(cfg):
        delta = change / "delta.md"
        if delta.exists():
            sections = delta_sections(delta.read_text(encoding="utf-8"))
            for name in ("ADDED Rules", "MODIFIED Rules"):
                for rule in parse_rules(sections.get(name, ""), cfg, cfg.rel(delta)):
                    check_rule_block(rule, r)
    r.data = {"rules": len(rules), "ids": sorted(rules)}
    return r


# --------------------------------------------------------------------------
# Changes and deltas


def open_changes(cfg: Config) -> list[Path]:
    base = cfg.path("changes")
    if not base.is_dir():
        return []
    return sorted(p for p in base.iterdir() if p.is_dir() and p.name != "archive" and not p.name.startswith("."))


def find_change(cfg: Config, name: str) -> Path | None:
    base = cfg.path("changes")
    if (base / name).is_dir():
        return base / name
    archive = base / "archive"
    if archive.is_dir():
        for p in sorted(archive.iterdir()):
            if p.is_dir() and (p.name == name or p.name.endswith("-" + name)):
                return p
    return None


def delta_sections(text: str) -> dict[str, str]:
    sections: dict[str, str] = {}
    current = None
    buf: list[str] = []
    for line in text.splitlines():
        m = re.match(r"^## (.+?)\s*$", line)
        if m:
            if current is not None:
                sections[current] = "\n".join(buf)
            current, buf = m.group(1), []
        elif current is not None:
            buf.append(line)
    if current is not None:
        sections[current] = "\n".join(buf)
    return sections


KNOWN_SECTIONS = {
    "ADDED Rules", "MODIFIED Rules", "REMOVED Rules", "RENAMED Rules",
    "Other changes to the specification", "Old values", "Kept old values", "Unchanged",
}


def table_rows(text: str) -> list[list[str]]:
    rows = []
    for line in text.splitlines():
        s = line.strip()
        if not s.startswith("|") or re.match(r"^\|[\s:|-]+\|$", s):
            continue
        rows.append([c.strip() for c in s.strip("|").split("|")])
    return rows[1:] if rows else []


def strip_code(value: str) -> str:
    return value.strip().strip("`").strip()


def old_value_patterns(cell: str) -> list[str]:
    """The literals in one Old value cell. Backtick spans are the values,
    so a note outside them is not a pattern. With no span, the cell is."""
    spans = [s.strip() for s in re.findall(r"`([^`]+)`", cell) if s.strip()]
    if spans:
        seen: list[str] = []
        for s in spans:
            if s not in seen:
                seen.append(s)
        return seen
    value = strip_code(cell)
    return [value] if value else []


def check_delta(cfg: Config, change: Path, archive: bool, spec_rules: dict[str, Rule]) -> Report:
    r = Report("delta")
    delta = change / "delta.md"
    rel = cfg.rel(delta)
    if not (change / "proposal.md").exists():
        r.error("proposal.md is missing", cfg.rel(change))
    if not delta.exists():
        proposal = change / "proposal.md"
        if proposal.exists() and "No rule changes." in proposal.read_text(encoding="utf-8"):
            return r
        r.error("delta.md is missing (or write 'No rule changes.' in proposal.md)", cfg.rel(change))
        return r
    text = delta.read_text(encoding="utf-8")
    sections = delta_sections(text)
    for name in sections:
        if name not in KNOWN_SECTIONS:
            r.warn(f"unknown section '## {name}'", rel)
    rid = cfg.rule_id
    for rule in parse_rules(sections.get("ADDED Rules", ""), cfg, rel):
        if rule.rid in spec_rules:
            r.error(f"ADDED {rule.rid} already exists in the specification: use MODIFIED", rel)
    for rule in parse_rules(sections.get("MODIFIED Rules", ""), cfg, rel):
        current = spec_rules.get(rule.rid)
        if current is None:
            r.error(f"MODIFIED {rule.rid} does not exist in the specification", rel)
            continue
        missing = [lab for lab in current.labels if lab not in rule.labels
                   and not (lab.startswith("Rule") and any(l.startswith("Rule") for l in rule.labels))]
        if missing:
            r.error(f"MODIFIED {rule.rid} drops bullet(s) of the current rule: {', '.join(missing)}; copy the whole block", rel)
        if "Revised" not in rule.bullets:
            (r.error if archive else r.warn)(f"MODIFIED {rule.rid} has no 'Revised:' bullet", rel)
    for rule in parse_rules(sections.get("REMOVED Rules", ""), cfg, rel):
        if rule.rid not in spec_rules:
            r.error(f"REMOVED {rule.rid} does not exist in the specification", rel)
        for name in ("Reason", "Migration"):
            if name not in rule.bullets:
                r.error(f"REMOVED {rule.rid} has no '{name}:' bullet", rel)
    renamed = sections.get("RENAMED Rules", "")
    froms = re.findall(r"FROM:\s*`?(" + rid.pattern + r")`?", renamed)
    tos = re.findall(r"TO:\s*`?(" + rid.pattern + r")`?", renamed)
    if len(froms) != len(tos):
        r.error("RENAMED: each FROM needs one TO", rel)
    for old, new in zip(froms, tos):
        if old not in spec_rules:
            r.error(f"RENAMED FROM {old} does not exist", rel)
        if new in spec_rules:
            r.error(f"RENAMED TO {new} already exists", rel)
    for row in table_rows(sections.get("Old values", "")):
        if len(row) < 3 or not strip_code(row[1]):
            r.error(f"Old values: a row needs Rule ID, Old value, New value: {' | '.join(row)}", rel)
    for found in rid.findall(sections.get("Unchanged", "")):
        if found not in spec_rules:
            r.error(f"Unchanged names {found}, which does not exist", rel)
    if archive:
        for n, line in enumerate(text.splitlines(), 1):
            if line.lstrip().startswith("<!--"):
                continue
            if PLACEHOLDER.search(line):
                r.error(f"placeholder left: {line.strip()[:80]}", rel, n)
    return r


def check_deltas(cfg: Config, name: str | None, archive: bool) -> Report:
    r = Report("delta")
    spec_rules = collect_rules(cfg, r)
    changes = [find_change(cfg, name)] if name else open_changes(cfg)
    if name and changes[0] is None:
        r.error(f"no change named {name}")
        return r
    for change in changes:
        r.merge(check_delta(cfg, change, archive, spec_rules))
    r.data = {"changes": [cfg.rel(c) for c in changes if c]}
    return r


# --------------------------------------------------------------------------
# Decision records


def parse_decision(path: Path) -> dict[str, str]:
    fields = {}
    for key, value in re.findall(r"^- \*\*([^*:]+):\*\*[ \t]*(.*)$", path.read_text(encoding="utf-8"), re.M):
        fields[key.strip()] = value.strip()
    return fields


def decision_files(cfg: Config) -> list[Path]:
    d = cfg.path("decisions")
    if not d.is_dir():
        return []
    return sorted(p for p in d.iterdir() if DECISION_FILE.match(p.name))


def records_for_change(cfg: Config, name: str) -> list[str]:
    hits = []
    for p in decision_files(cfg):
        value = parse_decision(p).get("Change", "")
        if strip_code(value).rstrip(".").strip("`") == name or re.search(r"`" + re.escape(name) + r"`", value):
            hits.append(p.name)
    return hits


def check_decisions(cfg: Config, change: str | None) -> Report:
    r = Report("decisions")
    spec_rules = collect_rules(cfg, Report("x")) if cfg.path("spec").exists() else {}
    prefixes = {k.split("-")[0] for k in spec_rules}
    files = decision_files(cfg)
    numbers: dict[str, str] = {}
    for p in files:
        rel = cfg.rel(p)
        num = DECISION_FILE.match(p.name).group(1)
        if num in numbers:
            r.error(f"number {num} is used twice: {numbers[num]} and {p.name}", rel)
        numbers[num] = p.name
        f = parse_decision(p)
        for key in ("Status", "Date"):
            if key not in f:
                r.error(f"no '**{key}:**' header field", rel)
        status = f.get("Status", "")
        if status and not DECISION_STATUS.match(status.rstrip(".")):
            r.warn(f"status '{status}' is not one of: proposed, accepted, replaced by NNNN, written after the code", rel)
        rep = re.match(r"replaced by (\d{4})", status)
        if rep and not any(x.name.startswith(rep.group(1)) for x in files):
            r.error(f"replaced by {rep.group(1)}, which does not exist", rel)
        if f.get("Date") and not re.match(r"^\d{4}-\d{2}-\d{2}", f["Date"]):
            r.error(f"date '{f['Date']}' is not YYYY-MM-DD", rel)
        text = p.read_text(encoding="utf-8")
        alt = delta_sections(text).get("Alternatives rejected")
        if alt is None:
            r.error("no '## Alternatives rejected' section", rel)
        elif not [row for row in table_rows(alt) if any(c for c in row)] and not re.search(r"^\s*[-*] \S", alt, re.M):
            r.error("'## Alternatives rejected' names no alternative", rel)
        for found in cfg.rule_id.findall(f.get("Traces to", "")):
            if found.split("-")[0] in prefixes and found not in spec_rules:
                r.warn(f"Traces to {found}, which is not in the specification", rel)
    nums = sorted(int(n) for n in numbers if len(n) == 4)
    gaps = [n for n in range(nums[0], nums[-1] + 1) if n not in nums] if nums else []
    if gaps:
        r.warn(f"numbers missing in the sequence: {', '.join(f'{g:04d}' for g in gaps)}")
    index = cfg.path("decision_index")
    if index.exists():
        itext = index.read_text(encoding="utf-8")
        for p in files:
            n = len(re.findall(r"\(" + re.escape(p.name) + r"\)", itext))
            if n != 1:
                r.error(f"{p.name} is linked {n} times in the index (expected once)", cfg.rel(index))
        for target in re.findall(r"\]\(((?:\d{8}-)?\d{4}-[^)]+\.md)\)", itext):
            if not (cfg.path("decisions") / target).exists():
                r.error(f"the index links {target}, which does not exist", cfg.rel(index))
    elif files:
        r.warn(f"no index at {cfg.get('decision_index')}")
    if change:
        hits = records_for_change(cfg, change)
        if not hits:
            r.error(f"no decision record names the change '{change}' in its Change field")
        r.data["records_for_change"] = hits
    r.data["records"] = len(files)
    return r


# --------------------------------------------------------------------------
# Trace: rules <-> scenarios <-> map <-> code


def walk(base: Path, patterns: tuple[str, ...] = ("*",)):
    if base.is_file():
        yield base
        return
    if not base.is_dir():
        return
    for dirpath, dirnames, filenames in os.walk(base):
        dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS)
        for name in sorted(filenames):
            if Path(name).suffix in SKIP_SUFFIXES or name == ".DS_Store":
                continue
            if any(fnmatch.fnmatch(name, p) for p in patterns):
                yield Path(dirpath) / name


def parse_feature(path: Path) -> list[dict]:
    scenarios = []
    feature_tags: list[str] = []
    pending: list[str] = []
    for n, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw.strip()
        if line.startswith("@"):
            pending += re.findall(r"@([^\s@]+)", line)
        elif re.match(r"^(Feature|Ability|Business Need):", line):
            feature_tags, pending = pending, []
        elif re.match(r"^(Scenario|Scenario Outline|Scenario Template|Example):", line):
            name = line.split(":", 1)[1].strip()
            scenarios.append({"name": name, "tags": feature_tags + pending, "line": n})
            pending = []
        elif re.match(r"^(Examples|Scenarios|Rule|Background):", line):
            pending = []
    return scenarios


def check_trace(cfg: Config) -> Report:
    r = Report("trace")
    rules = collect_rules(cfg, r)
    for change in open_changes(cfg):
        delta = change / "delta.md"
        if delta.exists():
            for rule in parse_rules(delta_sections(delta.read_text(encoding="utf-8")).get("ADDED Rules", ""), cfg, cfg.rel(delta)):
                rules.setdefault(rule.rid, rule)
    prefixes = {k.split("-")[0] for k in rules}
    coverage = {rid: {"scenarios": [], "code": []} for rid in rules}
    for feature in walk(cfg.path("tests"), ("*.feature",)):
        rel = cfg.rel(feature)
        for sc in parse_feature(feature):
            for tag in sc["tags"]:
                if not cfg.rule_id.fullmatch(tag) or tag.split("-")[0] not in prefixes:
                    continue
                if tag in coverage:
                    coverage[tag]["scenarios"].append(f"{rel}:{sc['line']} {sc['name']}")
                else:
                    r.error(f"scenario '{sc['name']}' is tagged @{tag}, which is not a rule", rel, sc["line"])
    for rid, cov in coverage.items():
        if not cov["scenarios"]:
            r.error(f"{rid} has no scenario tagged @{rid}", rules[rid].path, rules[rid].line)
    m = cfg.path("map")
    if m.exists():
        mtext = m.read_text(encoding="utf-8")
        in_map = set(cfg.rule_id.findall(mtext))
        for rid in rules:
            if rid not in in_map:
                r.error(f"{rid} is not in the map", cfg.get("map"))
        for rid in sorted(in_map - set(rules)):
            if rid.split("-")[0] in prefixes:
                r.warn(f"the map names {rid}, which is not a rule", cfg.get("map"))
    else:
        r.error(f"map not found: {cfg.get('map')}")
    code = cfg.path("code")
    for f in walk(code):
        try:
            text = f.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        for rid in set(cfg.rule_id.findall(text)):
            if rid in coverage:
                coverage[rid]["code"].append(cfg.rel(f))
            elif rid.split("-")[0] in prefixes:
                r.warn(f"the code cites {rid}, which is not a rule", cfg.rel(f))
    uncited = sorted(rid for rid, c in coverage.items() if not c["code"]) if code.exists() else []
    if code.exists() and uncited:
        r.add("info", f"rules that no code file cites: {', '.join(uncited)}")
    r.data = {
        "rules": len(rules),
        "with_scenarios": sum(1 for c in coverage.values() if c["scenarios"]),
        "cited_in_code": sum(1 for c in coverage.values() if c["code"]),
        "coverage": {k: {"scenarios": len(v["scenarios"]), "code": len(v["code"])} for k, v in sorted(coverage.items())},
    }
    return r


# --------------------------------------------------------------------------
# Old values


def scope_of(cfg: Config, path: Path) -> str:
    rel = cfg.rel(path)

    def under(key: str) -> bool:
        return any(rel == p or rel.startswith(p.rstrip("/") + "/") for p in cfg.list(key) or [cfg.get(key)] if p)

    if rel == cfg.get("spec"):
        return "specification"
    if cfg.list("spec_detail") and under("spec_detail"):
        return "detail"
    if rel.startswith(cfg.get("decisions").rstrip("/") + "/"):
        return "decision"
    if rel in cfg.list("contracts"):
        return "contract"
    if rel.startswith(cfg.get("tests").rstrip("/") + "/"):
        return "tests"
    if rel == cfg.get("map"):
        return "map"
    return "other"


def check_oldvalues(cfg: Config, name: str, archive: bool = False) -> Report:
    """Each hit is a warning. With archive (after the merge), each hit is
    an error, except in a decision record (a record is not rewritten) and
    a hit that the delta's "Kept old values" table gives a reason for."""
    r = Report("oldvalues")
    change = find_change(cfg, name)
    if change is None or not (change / "delta.md").exists():
        r.error(f"no delta for change {name}")
        return r
    sections = delta_sections((change / "delta.md").read_text(encoding="utf-8"))
    rows = table_rows(sections.get("Old values", ""))
    kept: dict[tuple[str, str], str] = {}
    for row in table_rows(sections.get("Kept old values", "")):
        if len(row) >= 3 and strip_code(row[0]) and strip_code(row[1]) and row[2].strip():
            kept[(strip_code(row[0]), strip_code(row[1]))] = row[2].strip()
    values: list[tuple[str, str]] = []
    for row in rows:
        if len(row) < 2 or not strip_code(row[1]):
            continue
        patterns = old_value_patterns(row[1])
        if len(patterns) > 1:
            r.warn(f"{row[0]}: one old value per row; split '{row[1]}' into {len(patterns)} rows", cfg.rel(change / "delta.md"))
        values.extend((row[0], p) for p in patterns)
    if not values:
        r.warn("the delta has no Old values rows")
    changes_dir = cfg.get("changes").rstrip("/") + "/"
    hits = []
    for base in cfg.list("primitives"):
        for f in walk(cfg.root / base):
            rel = cfg.rel(f)
            if rel.startswith(changes_dir):
                continue
            try:
                lines = f.read_text(encoding="utf-8").splitlines()
            except (UnicodeDecodeError, OSError):
                continue
            for n, line in enumerate(lines, 1):
                for rid, value in values:
                    if value in line:
                        hits.append({"rule": rid, "old": value, "path": rel, "line": n, "scope": scope_of(cfg, f), "text": line.strip()[:120]})
    by_scope: dict[str, int] = {}
    for h in hits:
        by_scope[h["scope"]] = by_scope.get(h["scope"], 0) + 1
    for h in hits:
        reason = kept.get((h["path"], h["old"]))
        h["kept"] = reason or ""
        message = f"{h['scope']}: '{h['old']}' ({h['rule']}): {h['text']}"
        if reason:
            r.add("info", f"{message} (kept: {reason})", h["path"], h["line"])
        elif archive and h["scope"] != "decision":
            r.error(f"{message}; fix it, or give a reason in the delta's Kept old values", h["path"], h["line"])
        else:
            r.warn(message, h["path"], h["line"])
    r.data = {"patterns": [v for _, v in values], "hits": hits, "by_scope": by_scope, "archive": archive}
    return r


# --------------------------------------------------------------------------
# Approval


def suite_hash(cfg: Config) -> str:
    h = hashlib.sha256()
    files = list(walk(cfg.path("tests")))
    m = cfg.path("map")
    for f in sorted(files, key=lambda p: cfg.rel(p)):
        h.update(cfg.rel(f).encode() + b"\0" + f.read_bytes() + b"\0")
    if m.exists():
        text = APPROVED.sub("Approved:", m.read_text(encoding="utf-8"))
        h.update(cfg.get("map").encode() + b"\0" + text.encode() + b"\0")
    return h.hexdigest()[:16]


def check_approval(cfg: Config, action: str, by: str | None) -> Report:
    r = Report("approval")
    m = cfg.path("map")
    if not m.exists():
        r.error(f"map not found: {cfg.get('map')}")
        return r
    text = m.read_text(encoding="utf-8")
    line = APPROVED.search(text)
    current = suite_hash(cfg)
    r.data["suite"] = f"sha256:{current}"
    if action == "hash":
        return r
    if action in ("stamp", "clear"):
        if line is None:
            r.error("the map has no 'Approved:' line; add one from the template")
            return r
        if action == "stamp":
            if not by:
                r.error("stamp needs --by \"<who>\": the person who reviewed the suite")
                return r
            value = f"Approved: {by}, {dt.date.today().isoformat()}, suite sha256:{current}"
        else:
            value = "Approved:"
        m.write_text(text[: line.start()] + value + text[line.end():], encoding="utf-8")
        r.data["line"] = value
        return r
    if line is None or not line.group(1).strip():
        r.error("the map is not approved: a person reviews the suite, then runs `approval stamp --by \"<who>\"`")
        return r
    r.data["line"] = line.group(0)
    hm = re.search(r"sha256:([0-9a-f]{16})", line.group(1))
    if not hm:
        r.error("the approval is not tied to the suite (no sha256); a person runs `approval stamp` after the review")
    elif hm.group(1) != current:
        r.error(f"the suite changed after the approval (approved {hm.group(1)}, now {current}); a person reviews and stamps again")
    return r


# --------------------------------------------------------------------------
# Expected failures (JUnit XML + git trailers)


def run_junit(cfg: Config, r: Report) -> None:
    cmd = cfg.get("junit_command")
    if not cmd:
        r.error("junit_command is not set in PHOENIX.md")
        return
    (cfg.root / cfg.get("junit")).parent.mkdir(parents=True, exist_ok=True)
    proc = subprocess.run(cmd, shell=True, cwd=cfg.root, capture_output=True, text=True)
    r.data["run"] = {"command": cmd, "exit": proc.returncode}


def read_junit(cfg: Config, r: Report) -> dict | None:
    path = cfg.root / cfg.get("junit")
    if not path.exists():
        r.error(f"no JUnit XML at {cfg.get('junit')}; run with --run, or run junit_command first")
        return None
    root = ET.parse(path).getroot()
    result = {"total": 0, "failed": [], "collection_errors": [], "skipped": 0}
    for case in root.iter("testcase"):
        cid = f"{case.get('classname', '')}::{case.get('name', '')}" if case.get("classname") else case.get("name", "")
        result["total"] += 1
        bad = case.find("failure") if case.find("failure") is not None else case.find("error")
        if bad is not None:
            message = (bad.get("message") or "")
            if "collection" in message.lower() or not case.get("classname"):
                result["collection_errors"].append(f"{cid}: {message[:120]}")
            else:
                result["failed"].append(cid)
        elif case.find("skipped") is not None:
            result["skipped"] += 1
    result["failed"].sort()
    return result


def norm_id(cid: str) -> str:
    """One test ID form: JUnit `classname::name`. A pytest node ID
    (`path/to/test_x.py::name`) maps to the same form."""
    cid = cid.strip()
    m = re.match(r"^(.+?)\.py::(.+)$", cid)
    if m:
        return m.group(1).replace("/", ".").replace("\\", ".") + "::" + m.group(2)
    return cid


def expected_from_git(cfg: Config, rev: str, r: Report) -> list[str] | None:
    inside = subprocess.run(["git", "rev-parse", "--is-inside-work-tree"], cwd=cfg.root, capture_output=True, text=True)
    if inside.returncode != 0:
        r.warn("not a git repository: no trailers to read, so the check is for the whole system")
        return []
    proc = subprocess.run(
        ["git", "log", "-1", f"--format=%(trailers:key={TRAILER},valueonly,separator=%x0A)", rev],
        cwd=cfg.root, capture_output=True, text=True,
    )
    if proc.returncode != 0:
        r.error(f"git log failed for {rev}: {proc.stderr.strip()}")
        return None
    ids = [line.strip() for line in proc.stdout.splitlines() if line.strip()]
    if ids:
        return sorted(ids)
    body = subprocess.run(["git", "log", "-1", "--format=%B", rev], cwd=cfg.root, capture_output=True, text=True).stdout
    m = re.search(r"^Expected to fail:\s*\n((?:\s*- .+\n?)+)", body, re.M)
    if m:
        r.warn("the expected failures are a prose list; use Phoenix-Expected-Fail trailers (`expected record`)")
        return sorted(re.sub(r"^\s*- ", "", x).strip() for x in m.group(1).splitlines() if x.strip())
    return []


def check_expected(cfg: Config, action: str, run: bool, rev: str) -> Report:
    r = Report("expected")
    if run:
        run_junit(cfg, r)
    result = read_junit(cfg, r)
    if result is None:
        return r
    r.data["junit"] = {k: (len(v) if isinstance(v, list) else v) for k, v in result.items()}
    def collection_errors() -> None:
        for ce in result["collection_errors"]:
            r.error(f"the suite does not collect: {ce}. A removal deleted a name that other code imports")

    if action == "record":
        collection_errors()
        r.data["trailers"] = [f"{TRAILER}: {cid}" for cid in result["failed"]]
        if not result["failed"]:
            r.error("no test fails: nothing was removed")
        return r
    expected = expected_from_git(cfg, rev, r)
    if expected is None:
        return r
    if not expected:
        # No trailers: the whole system. Before the code exists, the suite
        # does not collect, or every test fails.
        r.data["mode"] = "whole system"
        failed, total = len(result["failed"]), result["total"]
        if result["collection_errors"]:
            r.add("info", f"whole system: the suite does not collect ({len(result['collection_errors'])} error(s)), as expected before the code")
        elif total and failed == total:
            r.add("info", f"whole system: all {total} test(s) fail, as expected before the code")
        elif not total:
            r.error("no test ran: the suite is empty, or junit_command did not write the JUnit XML")
        else:
            r.error(f"whole system: {total - failed} of {total} test(s) pass before the code. For one unit, a person "
                    f"records the expected failures on commit {rev} with `expected record`")
        return r
    collection_errors()
    failed = set(result["failed"])
    exp = {norm_id(x) for x in expected}
    unexpected = sorted(failed - exp)
    passing = sorted(exp - failed)
    if result["total"] and len(failed) == result["total"]:
        r.error("every test fails: the removal went too far, or the suite does not reach the code")
    for cid in unexpected:
        r.error(f"fails but is not expected: {cid}")
    for cid in passing:
        r.error(f"expected to fail but passes: {cid}")
    r.data.update({"expected": len(exp), "failed": len(failed), "unexpected": unexpected, "expected_but_passed": passing})
    return r


# --------------------------------------------------------------------------
# Units


def parse_units(cfg: Config) -> list[dict]:
    if not cfg.phoenix_md.exists():
        return []
    sections = delta_sections(cfg.phoenix_md.read_text(encoding="utf-8"))
    rows = table_rows(sections.get("Units", ""))
    units = []
    for row in rows:
        if len(row) < 5 or not row[0]:
            continue
        units.append({
            "unit": row[0],
            "rules": cfg.rule_id.findall(row[1]),
            "interface": [strip_code(x) for x in row[2].split(",") if strip_code(x)],
            "modules": [strip_code(x) for x in row[3].split(",") if strip_code(x)],
            "risk": row[4].strip().lower(),
        })
    return units


def check_units(cfg: Config, show: str | None) -> Report:
    r = Report("units")
    rules = collect_rules(cfg, r)
    units = parse_units(cfg)
    for u in units:
        for rid in u["rules"]:
            if rid not in rules:
                r.error(f"unit {u['unit']}: {rid} is not a rule", "PHOENIX.md")
        for mod in u["modules"]:
            if not (cfg.root / mod).exists():
                r.warn(f"unit {u['unit']}: module {mod} does not exist", "PHOENIX.md")
        if u["risk"] not in RISKS:
            r.error(f"unit {u['unit']}: risk '{u['risk']}' is not low, medium, high, or critical", "PHOENIX.md")
    if show:
        match = [u for u in units if u["unit"] == show]
        if not match:
            r.error(f"no unit named {show} in the Units table of PHOENIX.md")
        r.data["unit"] = match[0] if match else None
    else:
        r.data["units"] = units
    return r


# --------------------------------------------------------------------------
# Status


def check_status(cfg: Config) -> Report:
    r = Report("status")
    # The setup check: status reports every config finding too.
    r.merge(check_config(cfg))
    if not cfg.phoenix_md.exists():
        r.data = {"machine_block": False, "next": "copy a preset from the kit's templates/ to PHOENIX.md"}
        return r
    approval = check_approval(cfg, "verify", None)
    approved = approval.ok(False)
    changes = []
    spec_rules = collect_rules(cfg, Report("x"))
    for change in open_changes(cfg):
        d = check_delta(cfg, change, False, spec_rules)
        records = records_for_change(cfg, change.name)
        info = {
            "name": change.name,
            "proposal": (change / "proposal.md").exists(),
            "delta": (change / "delta.md").exists(),
            "delta_errors": d.count("error"),
            "decisions": records,
        }
        if not info["proposal"]:
            nxt = f"/phoenix-kit:change propose {change.name}"
        elif info["delta_errors"]:
            nxt = f"fix delta.md (phoenix_check.py delta --change {change.name})"
        elif not records:
            nxt = "a person reviews the proposal; then /phoenix-kit:contract, /phoenix-kit:evaluate, /phoenix-kit:decide"
        elif not approved:
            nxt = "a person reviews the final suite and runs `phoenix_check.py approval stamp --by \"<who>\"`"
        else:
            nxt = "remove the unit on a branch, `expected record`, commit, /phoenix-kit:generate <unit>; then archive"
        info["next"] = nxt
        changes.append(info)
    r.data = {
        "machine_block": cfg.found_block,
        "approval": "valid" if approved else "; ".join(f["message"] for f in approval.findings),
        "open_changes": changes,
    }
    if not changes:
        if not approved and any("suite changed after the approval" in f["message"] for f in approval.findings):
            # For example, an archive updated the map.
            r.data["next"] = "a person reviews the changed suite and map, and runs `phoenix_check.py approval stamp --by \"<who>\"` again"
        elif not approved:
            r.data["next"] = "/phoenix-kit:evaluate, then a person approves the suite"
        elif any(walk(cfg.path("code"))):
            r.data["next"] = "/phoenix-kit:deletion-test"
        else:
            r.data["next"] = "/phoenix-kit:generate"
    return r


# --------------------------------------------------------------------------
# CLI


def emit(report: Report, as_json: bool, strict: bool) -> int:
    ok = report.ok(strict)
    if as_json:
        print(json.dumps({
            "check": report.check, "ok": ok,
            "errors": report.count("error"), "warnings": report.count("warning"),
            "findings": report.findings, "data": report.data,
        }, indent=2, ensure_ascii=False))
    else:
        for f in report.findings:
            where = f"{f['path']}:{f['line']}" if f["line"] else f["path"]
            print(f"{f['level'].upper():7} {where + ': ' if where else ''}{f['message']}")
        if report.check == "expected" and "trailers" in report.data:
            print("\n".join(report.data["trailers"]))
        summary = {k: v for k, v in report.data.items() if not isinstance(v, (list, dict)) or k in ("by_scope", "open_changes", "junit")}
        print(f"{report.check}: {'ok' if ok else 'FAILED'} — {report.count('error')} error(s), {report.count('warning')} warning(s) {json.dumps(summary, ensure_ascii=False)}")
    return 0 if ok else 1


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="phoenix_check.py", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--root", default=".", help="project root (default: the current folder)")
    p.add_argument("--json", action="store_true")
    p.add_argument("--strict", action="store_true", help="warnings fail the check too")
    sub = p.add_subparsers(dest="command", required=True)
    for name in ("config", "rules", "trace", "status"):
        sub.add_parser(name)
    d = sub.add_parser("delta")
    d.add_argument("--change")
    d.add_argument("--archive", action="store_true", help="no placeholder may remain")
    dc = sub.add_parser("decisions")
    dc.add_argument("--change")
    ov = sub.add_parser("oldvalues")
    ov.add_argument("--change", required=True)
    ov.add_argument("--archive", action="store_true", help="after the merge: each hit is an error")
    un = sub.add_parser("units")
    un.add_argument("show", nargs="?", default=None)
    un.add_argument("name", nargs="?", default=None)
    ap = sub.add_parser("approval")
    ap.add_argument("action", choices=["hash", "stamp", "verify", "clear"])
    ap.add_argument("--by")
    ex = sub.add_parser("expected")
    ex.add_argument("action", choices=["record", "check"])
    ex.add_argument("--run", action="store_true", help="run junit_command first")
    ex.add_argument("--rev", default="HEAD")
    for sp in sub.choices.values():
        sp.add_argument("--root", default=argparse.SUPPRESS, help="project root (default: the current folder)")
        sp.add_argument("--json", action="store_true", default=argparse.SUPPRESS)
        sp.add_argument("--strict", action="store_true", default=argparse.SUPPRESS)
    args = p.parse_args(argv)
    cfg = Config(Path(args.root).resolve())
    c = args.command
    if c == "config":
        report = check_config(cfg)
    elif c == "rules":
        report = check_rules(cfg)
    elif c == "trace":
        report = check_trace(cfg)
    elif c == "delta":
        report = check_deltas(cfg, args.change, args.archive)
    elif c == "decisions":
        report = check_decisions(cfg, args.change)
    elif c == "oldvalues":
        report = check_oldvalues(cfg, args.change, args.archive)
    elif c == "units":
        report = check_units(cfg, args.name if args.show == "show" else None)
    elif c == "approval":
        report = check_approval(cfg, args.action, args.by)
    elif c == "expected":
        report = check_expected(cfg, args.action, args.run, args.rev)
    else:
        report = check_status(cfg)
    return emit(report, args.json, args.strict)


if __name__ == "__main__":
    sys.exit(main())
