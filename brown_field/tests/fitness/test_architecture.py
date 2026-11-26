"""Fitness: the hexagon keeps its shape (decision 0012).

- the core imports no I/O: no files, no SQLite, no clock, no random, no web;
- the core and the domain model never import an adapter or the composition root;
- the adapters never import the REST API;
- the REST adapter reaches the game only through the use cases.
"""

import ast
import re
from pathlib import Path

import pytest

PACKAGE = Path(__file__).resolve().parents[2]
CORE = sorted((PACKAGE / "core").glob("*.py"))
ADAPTERS = sorted((PACKAGE / "adapters").glob("*.py"))

# The standard library modules that hold no I/O. `datetime` is here for the type
# of the Clock port: the core never calls `datetime.now()`.
PURE_STDLIB = {"collections", "dataclasses", "datetime", "enum", "math", "typing"}


def imports(path: Path) -> list[tuple[int, str]]:
    """Each import as (level, module): level 0 is absolute, 1 is `.x`, 2 is `..x`."""
    found = []
    for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
        if isinstance(node, ast.Import):
            found += [(0, alias.name) for alias in node.names]
        elif isinstance(node, ast.ImportFrom):
            found.append((node.level, node.module or ""))
    return found


@pytest.mark.fitness
@pytest.mark.parametrize("path", CORE, ids=lambda p: p.name)
def test_the_core_imports_only_pure_modules(path):
    for level, module in imports(path):
        if level == 0:
            assert module.split(".")[0] in PURE_STDLIB, f"{path.name} imports {module}"
        elif level == 2:
            assert module == "kata", f"{path.name} imports ..{module}: the core sees only the domain model"


@pytest.mark.fitness
@pytest.mark.parametrize("path", CORE, ids=lambda p: p.name)
def test_the_core_reads_the_clock_only_through_its_port(path):
    source = path.read_text(encoding="utf-8")
    # `random` is not a pure module, so the import check already stops it.
    assert not re.search(r"\.(now|today|utcnow)\(", source), f"{path.name} reads the clock without the Clock port"


@pytest.mark.fitness
def test_the_domain_model_imports_nothing_of_the_package():
    assert all(level == 0 for level, _ in imports(PACKAGE / "kata.py"))


@pytest.mark.fitness
@pytest.mark.parametrize("path", ADAPTERS, ids=lambda p: p.name)
def test_an_adapter_never_imports_the_rest_api_or_the_composition_root(path):
    for level, module in imports(path):
        if level == 2:
            assert module.split(".")[0] == "core", f"{path.name} imports ..{module}"


@pytest.mark.fitness
def test_the_rest_adapter_reaches_the_game_only_through_use_cases():
    source = (PACKAGE / "api.py").read_text(encoding="utf-8")
    reached = sorted(set(re.findall(r"\bgame\.(\w+)", source)))
    assert reached == [], f"api.py reads the game state directly: {reached}"
    for level, module in imports(PACKAGE / "api.py"):
        if level == 1:
            assert module in {"game", "kata"}, f"api.py imports .{module}: it takes use cases from the composition root"
