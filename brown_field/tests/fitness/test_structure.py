"""Bind structure.feature: the structure of decision 0012, checked with ast."""

import ast
from pathlib import Path

from pytest_bdd import parsers, scenarios, then, when

ROOT = Path(__file__).resolve().parents[2]

scenarios("structure.feature")


def uses_of_game(tree: ast.AST) -> list[ast.AST]:
    """Every load of the name `game` that is not a use-case argument."""
    allowed: set[int] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id.endswith("UseCase"):
            allowed.update(id(arg) for arg in node.args)
        if isinstance(node, ast.BoolOp):  # game = game or InMemoryGame()
            allowed.update(id(value) for value in node.values)
    return [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.Name) and node.id == "game" and isinstance(node.ctx, ast.Load) and id(node) not in allowed
    ]


@when(parsers.parse('the check reads "{source}"'), target_fixture="reads")
def the_check_reads(source):
    return [(source, node.lineno) for node in uses_of_game(ast.parse((ROOT / source).read_text(encoding="utf-8")))]


@when(parsers.parse('the check reads the code "{code}"'), target_fixture="reads")
def the_check_reads_the_code(code):
    return uses_of_game(ast.parse(code.encode().decode("unicode_escape")))


@then("the game is only built or passed to a use case")
def only_built_or_passed(reads):
    assert not reads, f"the game is read outside a use case at {reads} (ENTRY-4)"


@then(parsers.parse("the check finds {count:d} read of the game"))
def the_check_finds(reads, count):
    assert len(reads) == count


@when(parsers.parse('the check reads the imports and calls of "{source}"'), target_fixture="tree")
def the_check_reads_the_imports(source):
    return ast.parse((ROOT / source).read_text(encoding="utf-8"))


@then(parsers.parse('it imports none of "{modules}" and never calls open'))
def it_does_no_io(tree, modules):
    banned = {name.strip() for name in modules.split(",")}
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name.split(".")[0] for alias in node.names)
        if isinstance(node, ast.ImportFrom) and node.level == 0:
            imported.add(node.module.split(".")[0])
    opens = [n.lineno for n in ast.walk(tree) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == "open"]
    assert not imported & banned, f"imports {sorted(imported & banned)} (ENTRY-6)"
    assert not opens, f"calls open at lines {opens} (ENTRY-6)"
