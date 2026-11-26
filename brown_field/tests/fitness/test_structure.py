"""Fitness: the shape of the code behind the boundary (section "Structure").

ARCH-1: each layer imports only `kata.py`, its own layer, and the layers
inside it. The domain and the application touch no I/O.

ARCH-2: each use case satisfies its port in `kata.py`. mypy proves it on
`ports_check.py`, as a Java compiler would for `implements`.

Each check also runs on a planted break, so a check that always passes
fails here first.
"""

import ast
import subprocess
import sys
from pathlib import Path

import pytest

pytestmark = pytest.mark.fitness

PACKAGE = Path(__file__).resolve().parents[2]
NOT_CODE = {"tests", "web", "spec", "__pycache__"}

# Inner first. A module may import its own layer and every layer before it.
# The domain is innermost; the ports (kata.py) sit outside it (decision 0018).
LAYERS = ("domain", "kata", "application", "adapters", "root")
RANK = {name: rank for rank, name in enumerate(LAYERS)}
NO_IO = {"domain", "application"}
IO_MODULES = {"sqlite3", "os", "fastapi", "pydantic", "uvicorn", "random", "starlette"}


def code_modules() -> list[Path]:
    return sorted(
        path
        for path in PACKAGE.rglob("*.py")
        if not NOT_CODE & set(path.relative_to(PACKAGE).parts)
    )


def module_name(path: Path) -> list[str]:
    parts = ["brown_field", *path.relative_to(PACKAGE).with_suffix("").parts]
    return parts[:-1] if parts[-1] == "__init__" else parts


def layer_of(parts: list[str]) -> str:
    """The layer of a module, from its dotted name inside `brown_field`."""
    if len(parts) < 2:
        return "root"
    head = parts[1]
    if head == "kata":
        return "kata"
    if head in ("domain", "application", "adapters"):
        return head
    if head == "tests":
        return "tests"
    return "root"


def imported(tree: ast.AST, own: list[str], is_package: bool) -> list[tuple[int, list[str]]]:
    """Every module that a tree imports, as (line, dotted parts)."""
    found = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                found.append((node.lineno, alias.name.split(".")))
        elif isinstance(node, ast.ImportFrom):
            if node.level:
                base = own if is_package else own[:-1]
                base = base[: len(base) - (node.level - 1)]
                target = base + (node.module.split(".") if node.module else [])
            else:
                target = node.module.split(".")
            if node.module is None:
                for alias in node.names:
                    found.append((node.lineno, target + [alias.name]))
            else:
                found.append((node.lineno, target))
    return found


def io_calls(tree: ast.AST) -> list[tuple[int, str]]:
    """Calls of `datetime.now` and of the builtin `open`."""
    found = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if isinstance(func, ast.Name) and func.id == "open":
            found.append((node.lineno, "open()"))
        if isinstance(func, ast.Attribute) and func.attr == "now":
            owner = func.value
            name = owner.id if isinstance(owner, ast.Name) else getattr(owner, "attr", "")
            if name == "datetime":
                found.append((node.lineno, "datetime.now()"))
    return found


def violations(source: str, parts: list[str], is_package: bool, where: str) -> list[str]:
    """Each break of ARCH-1 in one module."""
    tree = ast.parse(source)
    own = layer_of(parts)
    broken = []
    for line, target in imported(tree, parts, is_package):
        if target[0] == "brown_field":
            other = layer_of(target)
            if other == "tests" or RANK[other] > RANK[own]:
                broken.append(f"{where}:{line}: the {own} layer imports {'.'.join(target)} ({other})")
        elif own in NO_IO and target[0] in IO_MODULES:
            broken.append(f"{where}:{line}: the {own} layer imports {target[0]}")
    if own in NO_IO:
        for line, call in io_calls(tree):
            broken.append(f"{where}:{line}: the {own} layer calls {call}")
    return broken


def test_each_layer_imports_only_the_layers_inside_it():
    """ARCH-1."""
    broken = []
    for path in code_modules():
        broken += violations(
            path.read_text(encoding="utf-8"),
            module_name(path),
            path.name == "__init__.py",
            str(path.relative_to(PACKAGE.parent)),
        )
    assert broken == [], "\n".join(broken)


@pytest.mark.parametrize(
    "parts, source, expected",
    [
        (["brown_field", "domain", "bag"], "from brown_field.adapters import x\n", "imports brown_field.adapters"),
        (["brown_field", "domain", "bag"], "from ..game import InMemoryGame\n", "imports brown_field.game"),
        (["brown_field", "application", "move"], "import sqlite3\n", "imports sqlite3"),
        (["brown_field", "application", "move"], "from datetime import datetime\ndatetime.now()\n", "calls datetime.now()"),
        (["brown_field", "domain", "bag"], "open('x')\n", "calls open()"),
        (["brown_field", "domain", "world"], "from ..kata import Item\n", "imports brown_field.kata"),
        (["brown_field", "kata"], "from brown_field.application import state\n", "imports brown_field.application"),
    ],
)
def test_the_import_check_sees_a_planted_break(parts, source, expected):
    """ARCH-1: one forbidden import or call fails, and names its line."""
    found = violations(source, parts, False, "planted.py")
    assert len(found) == 1 and expected in found[0], found


def mypy(path: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-m", "mypy", "--strict", "--follow-imports=silent",
         "--no-incremental", "--no-error-summary", str(path)],
        capture_output=True, text=True, cwd=PACKAGE.parent,
    )


def test_each_use_case_satisfies_its_port():
    """ARCH-2."""
    result = mypy(Path(__file__).with_name("ports_check.py"))
    assert result.returncode == 0, result.stdout + result.stderr


def test_the_port_check_sees_a_planted_break(tmp_path):
    """ARCH-2: a use case whose `execute` drifts from its port is a type error."""
    planted = tmp_path / "planted_check.py"
    planted.write_text(
        "from brown_field import kata\n"
        "class Drifted:\n"
        "    def execute(self, player_sid: str, way: str) -> kata.Location: ...\n"
        "def check() -> None:\n"
        "    move: kata.Move = Drifted()\n",
        encoding="utf-8",
    )
    result = mypy(planted)
    assert result.returncode == 1 and "planted_check.py:5" in result.stdout, result.stdout


def test_only_adapters_read_the_clock_draw_chance_or_open_files():
    """ARCH-3: the clock, `random` and `open` appear only under adapters/."""
    broken = []
    for path in code_modules():
        parts = module_name(path)
        if layer_of(parts) == "adapters":
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"))
        where = path.relative_to(PACKAGE.parent)
        broken += [f"{where}:{line}: calls {call}" for line, call in io_calls(tree)]
        broken += [
            f"{where}:{line}: imports random"
            for line, target in imported(tree, parts, path.name == "__init__.py")
            if target[0] == "random"
        ]
    assert broken == [], "\n".join(broken)


def test_only_the_sqlite_adapter_imports_sqlite3():
    """ARCH-4: the saves and the accounts reach SQLite only through adapters/sqlite/."""
    broken = []
    for path in code_modules():
        parts = module_name(path)
        if parts[:3] == ["brown_field", "adapters", "sqlite"]:
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"))
        broken += [
            f"{path.relative_to(PACKAGE.parent)}:{line}: imports sqlite3"
            for line, target in imported(tree, parts, path.name == "__init__.py")
            if target[0] == "sqlite3"
        ]
    assert broken == [], "\n".join(broken)


GAME_STATE = {"players", "places", "chat", "finished_games", "accounts", "items", "open_items", "locked_items"}


def state_reads(tree: ast.AST) -> list[tuple[int, str, str]]:
    """Each `game.<state>` in a module, as (line, attribute, innermost function)."""
    found = []

    def visit(node: ast.AST, function: str) -> None:
        if isinstance(node, ast.FunctionDef):
            function = node.name
        if (
            isinstance(node, ast.Attribute)
            and node.attr in GAME_STATE
            and isinstance(node.value, ast.Name)
            and node.value.id == "game"
        ):
            found.append((node.lineno, node.attr, function))
        for child in ast.iter_child_nodes(node):
            visit(child, function)

    visit(tree, "<module>")
    return found


def test_the_rest_adapter_holds_no_rule_and_changes_no_state():
    """ARCH-5: routes reach the game state only through the ports.

    Since decision 0019 the adapter receives only the ports, so no route names
    the game. Since decision 0011 the MOVE-5 gate lives in the move port.
    """
    rest = PACKAGE / "adapters" / "rest"
    broken = []
    for path in sorted(rest.rglob("*.py")):
        for line, attribute, function in state_reads(ast.parse(path.read_text(encoding="utf-8"))):
            broken.append(f"{path.relative_to(PACKAGE.parent)}:{line}: {function} reads game.{attribute}")
    assert broken == [], "\n".join(broken)


def test_the_rest_check_sees_a_planted_rule():
    """ARCH-5: a route that writes the state is found, and named."""
    planted = "def build_app(game):\n    def send_message(sid):\n        game.chat.append(sid)\n"
    assert state_reads(ast.parse(planted)) == [(3, "chat", "send_message")]


def test_the_domain_imports_nothing_outside_the_domain():
    """ARCH-7: no module of the domain imports a module outside brown_field/domain/."""
    broken = []
    for path in code_modules():
        parts = module_name(path)
        if layer_of(parts) != "domain":
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"))
        broken += [
            f"{path.relative_to(PACKAGE.parent)}:{line}: imports {'.'.join(target)}"
            for line, target in imported(tree, parts, path.name == "__init__.py")
            if target[0] == "brown_field" and layer_of(target) != "domain"
        ]
    assert broken == [], "\n".join(broken)


def test_kata_re_exports_the_domain_types_as_the_same_objects():
    """ARCH-7: the frozen names of kata.py are the domain's own objects."""
    from brown_field import kata
    from brown_field.domain import errors, types

    for name in ("Item", "Action", "Direction"):
        assert getattr(kata, name) is getattr(types, name), name
    for name in ("KatacombsError", "PlayerNotFound", "ItemNotFound", "InvalidName", "NotAllowed"):
        assert getattr(kata, name) is getattr(errors, name), name


def test_the_rest_adapter_imports_only_the_ports():
    """ARCH-8: nothing under adapters/rest/ imports the application or the domain."""
    broken = []
    for path in sorted((PACKAGE / "adapters" / "rest").rglob("*.py")):
        parts = module_name(path)
        tree = ast.parse(path.read_text(encoding="utf-8"))
        broken += [
            f"{path.relative_to(PACKAGE.parent)}:{line}: imports {'.'.join(target)}"
            for line, target in imported(tree, parts, path.name == "__init__.py")
            if target[0] == "brown_field" and layer_of(target) in ("application", "domain")
        ]
    assert broken == [], "\n".join(broken)
