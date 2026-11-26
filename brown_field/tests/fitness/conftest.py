"""Steps for the operational limits (OPS rules)."""

import math
import time

import pytest
from pytest_bdd import parsers, then, when


@pytest.fixture
def timings() -> list[float]:
    return []


def run_cycle(client, timings: list[float], budget: int) -> int:
    """One cycle of up to 10 commands that a new player sends; returns how many ran.

    Each cycle starts its own player (a command too), so the energy never runs
    out: 1 move per cycle, 12 energy each. 10 cycles stay under 20 players.
    """
    state: dict = {}

    def timed(call):
        start = time.perf_counter()
        response = call()
        timings.append((time.perf_counter() - start) * 1000)
        assert response.status_code < 300, response.text
        return response

    def beer():
        here = client.get(f"/player/{state['sid']}/location").json()["items"]
        return next(item["sid"] for item in here if item["name"] == "BEER")

    steps = [
        lambda: state.update(sid=timed(lambda: client.post("/game/player", json={"name": "ops"})).json()["sid"]),
        lambda: timed(lambda: client.get(f"/player/{state['sid']}/location")),
        lambda: timed(lambda: client.get(f"/player/{state['sid']}/look/north")),
        lambda: timed(lambda: client.put(f"/player/{state['sid']}/move/north")),
        lambda: timed(lambda: client.get(f"/player/{state['sid']}/bag")),
        lambda: state.update(beer=beer()) or timed(lambda: client.put(f"/player/{state['sid']}/item/{state['beer']}/use/pick")),
        lambda: timed(lambda: client.put(f"/player/{state['sid']}/item/{state['beer']}/use/drop")),
        lambda: timed(lambda: client.post(f"/player/{state['sid']}/chat", json={"text": "hi"})),
        lambda: timed(lambda: client.get(f"/player/{state['sid']}/chat")),
        lambda: timed(lambda: client.post(f"/player/{state['sid']}/save")),
    ]
    for step in steps[:budget]:
        step()
    return min(budget, len(steps))


@when(parsers.parse("{count:d} commands run in process"))
def commands_run(play, timings, count):
    sent = 0
    while sent < count:
        sent += run_cycle(play.client, timings, count - sent)


@then(parsers.parse("the 99th percentile response time is less than {limit:d} ms"))
def the_p99_is_below(timings, limit):
    ordered = sorted(timings)
    p99 = ordered[math.ceil(0.99 * len(ordered)) - 1]
    assert len(ordered) == 100
    assert p99 < limit, f"p99 = {p99:.1f} ms over {len(ordered)} commands"


# --- The architecture (OPS-2, OPS-3, decision 0012) -----------------------------------
#
# These steps read the source with `ast`; they import nothing of the game. The
# names of the port tier come from decision 0008, not from the code.

import ast  # noqa: E402
from pathlib import Path  # noqa: E402

PACKAGE = Path(__file__).resolve().parents[2]
PORT_TIER_USE_CASES = {
    "RegisterPlayerUseCase", "ListPlayersUseCase", "QuitGameUseCase", "InspectItemUseCase",
    "InspectBagUseCase", "LookAroundUseCase", "LookInDirectionUseCase", "MoveUseCase",
    "UseItemUseCase", "SaveGameUseCase", "RegisterAccountUseCase", "LoginUseCase",
}
IO_MODULES = {"sqlite3", "os", "random", "hashlib", "json", "fastapi", "pydantic", "starlette", "uvicorn"}


@pytest.fixture
def source() -> dict:
    return {}


@when("the architecture check reads the core")
def reads_the_core(source):
    core = PACKAGE / "core"
    assert core.is_dir(), f"no core package at {core.relative_to(PACKAGE.parent)}: the rules are not in a core"
    source["modules"] = {path.name: ast.parse(path.read_text(encoding="utf-8")) for path in sorted(core.glob("*.py"))}


@when("the architecture check reads the REST adapter")
def reads_the_rest_adapter(source):
    source["api"] = ast.parse((PACKAGE / "api.py").read_text(encoding="utf-8"))


@then("each use case of the port tier is defined in a core module")
def every_use_case_in_the_core(source):
    defined = {node.name for tree in source["modules"].values() for node in ast.walk(tree) if isinstance(node, ast.ClassDef)}
    missing = sorted(PORT_TIER_USE_CASES - defined)
    assert not missing, f"use cases outside the core: {missing}"


@then("no core module imports an I/O or web module")
def no_io_imports(source):
    found = []
    for name, tree in source["modules"].items():
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                found += [f"{name}: {alias.name}" for alias in node.names if alias.name.split(".")[0] in IO_MODULES]
            elif isinstance(node, ast.ImportFrom) and node.level == 0 and (node.module or "").split(".")[0] in IO_MODULES:
                found.append(f"{name}: {node.module}")
    assert not found, f"I/O imports in the core: {found}"


@then("no core module opens a file or reads the clock")
def no_io_calls(source):
    found = []
    for name, tree in source["modules"].items():
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            if isinstance(node.func, ast.Name) and node.func.id == "open":
                found.append(f"{name}:{node.lineno} open()")
            if isinstance(node.func, ast.Attribute) and node.func.attr in {"now", "today", "utcnow"}:
                found.append(f"{name}:{node.lineno} .{node.func.attr}()")
    assert not found, f"I/O calls in the core: {found}"


@then("the REST adapter reads no attribute of the game")
def no_game_state_in_the_adapter(source):
    reads = sorted({
        node.attr for node in ast.walk(source["api"])
        if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name) and node.value.id == "game"
    })
    assert not reads, f"api.py reads the game state: game.{', game.'.join(reads)}"


def routes(tree: ast.AST) -> list[ast.FunctionDef]:
    """The functions decorated with @app.get, .post, .put or .delete."""
    return [
        node for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef) and any(
            isinstance(d, ast.Call) and isinstance(d.func, ast.Attribute)
            and d.func.attr in {"get", "post", "put", "delete"} for d in node.decorator_list
        )
    ]


@then("each route of the REST adapter calls a use case")
def every_route_calls_a_use_case(source):
    found = routes(source["api"])
    assert len(found) >= 16, f"found {len(found)} routes; the contract has 16 operations"
    without = [
        route.name for route in found
        if not any(isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id.endswith("UseCase") for n in ast.walk(route))
    ]
    assert not without, f"routes that answer without a use case: {without}"
