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
