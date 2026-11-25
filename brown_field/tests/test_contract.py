"""The contract test of the game-server.

It validates a live response of each operation in brown_field/spec/openapi.yaml
against the schema the contract gives for that status, checks that each error
reason answers with the status of `x-status-by-reason`, and validates the data
the server writes for others to read (the player state, the high-score line)
against their JSON Schemas.

It goes through the REST boundary only: `create_app()` and HTTP. Items are
found by name through the API, not by internal constants, so the test survives
a rewrite. It never moves into SPITALFIELDS MARKET, so the clock (MOVE-6) does
not matter.
"""

import json
import re
import sqlite3
from pathlib import Path

import pytest
import yaml
from fastapi.testclient import TestClient
from jsonschema import Draft202012Validator
from referencing import Registry, Resource
from referencing.jsonschema import DRAFT202012

from brown_field.api import create_app

SPEC = Path(__file__).resolve().parents[1] / "spec"
OPENAPI = yaml.safe_load((SPEC / "openapi.yaml").read_text(encoding="utf-8"))
PLAYER_STATE = json.loads((SPEC / "player-state.schema.json").read_text(encoding="utf-8"))
HIGHSCORE_LINE = json.loads((SPEC / "highscore-line.schema.json").read_text(encoding="utf-8"))
OPENAPI_URI = "urn:katacombs:openapi"
REGISTRY = Registry().with_resource(
    OPENAPI_URI, Resource.from_contents(OPENAPI, default_specification=DRAFT202012)
)
STATUS_BY_REASON = OPENAPI["components"]["schemas"]["ErrorReason"]["x-status-by-reason"]

# The win route that needs no market: BOXPARK, RAILWAY ARCHES, OLD TUBE TUNNEL,
# TUNNEL JUNCTION, KATACOMBS, KATACOMBS EXIT.
WIN_ROUTE = ["south", "east", "down", "east", "north", "east"]


# --- Reading the contract -------------------------------------------------------


def operations() -> dict[str, tuple[str, str, dict]]:
    found = {}
    for path, item in OPENAPI["paths"].items():
        for method, operation in item.items():
            found[operation["operationId"]] = (path, method, operation)
    return found


def response_schema(operation_id: str, status: int) -> dict:
    _, _, operation = operations()[operation_id]
    responses = operation["responses"]
    assert str(status) in responses, (
        f"{operation_id} answered {status}, which the contract does not list"
    )
    response = responses[str(status)]
    if "$ref" in response:
        name = response["$ref"].rsplit("/", 1)[-1]
        response = OPENAPI["components"]["responses"][name]
    return response["content"]["application/json"]["schema"]


def assert_matches(operation_id: str, response) -> None:
    schema = response_schema(operation_id, response.status_code)
    resolved = {"$ref": f"{OPENAPI_URI}#" + schema["$ref"][1:]} if "$ref" in schema else _rebase(schema)
    validator = Draft202012Validator(resolved, registry=REGISTRY)
    errors = sorted(validator.iter_errors(response.json()), key=str)
    assert not errors, f"{operation_id} {response.status_code}: " + "; ".join(e.message for e in errors)


def _rebase(schema):
    """Point the local $refs of an inline schema at the OpenAPI document."""
    if isinstance(schema, dict):
        return {
            key: (f"{OPENAPI_URI}#" + value[1:] if key == "$ref" else _rebase(value))
            for key, value in schema.items()
        }
    if isinstance(schema, list):
        return [_rebase(value) for value in schema]
    return schema


# --- A game through the API ------------------------------------------------------


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("KATACOMBS_DB", str(tmp_path / "katacombs.db"))
    monkeypatch.setenv("KATACOMBS_HIGHSCORES", str(tmp_path / "highscores.jsonl"))
    return TestClient(create_app())


def start(client, name="ANA") -> str:
    response = client.post("/game/player", json={"name": name})
    assert response.status_code == 201, response.text
    return response.json()["sid"]


def item_here(client, sid: str, name: str) -> str:
    items = client.get(f"/player/{sid}/location").json()["items"]
    return next(item["sid"] for item in items if item["name"] == name)


def go(client, sid: str, *directions: str):
    response = None
    for direction in directions:
        response = client.put(f"/player/{sid}/move/{direction}")
        assert response.status_code == 200, response.text
    return response


# --- 1. Each operation's success response matches its schema --------------------


def call_start_game(client):
    return client.post("/game/player", json={"name": "  ana "})


def call_list_players(client):
    start(client)
    return client.get("/game/player")


def call_quit_game(client):
    return client.delete(f"/game/player/{start(client)}")


def call_read_leaderboard(client):
    sid = start(client)
    go(client, sid, *WIN_ROUTE)
    return client.get("/leaderboard")


def call_inspect_item(client):
    sid = start(client)
    go(client, sid, "north")
    return client.get(f"/items/{item_here(client, sid, 'BEER')}")


def call_inspect_bag(client):
    sid = start(client)
    go(client, sid, "north")
    client.put(f"/player/{sid}/item/{item_here(client, sid, 'BEER')}/use/pick")
    return client.get(f"/player/{sid}/bag")


def call_save_game(client):
    return client.post(f"/player/{start(client)}/save")


def call_register_account(client):
    return client.post("/accounts", json={"email": "ana@example.org", "password": "pw", "name": "ana"})


def call_login(client):
    client.post("/accounts", json={"email": "ana@example.org", "password": "pw", "name": "ana"})
    return client.post("/accounts/login", json={"email": "ana@example.org", "password": "pw"})


def call_send_chat_message(client):
    return client.post(f"/player/{start(client)}/chat", json={"text": "hello"})


def call_read_chat(client):
    sid = start(client)
    client.post(f"/player/{sid}/chat", json={"text": "hello"})
    return client.get(f"/player/{sid}/chat")


def call_act_on_item(client):
    sid = start(client)
    go(client, sid, "north")
    return client.put(f"/player/{sid}/item/{item_here(client, sid, 'BEER')}/use/pick")


def call_legacy_pickup(client):
    sid = start(client)
    go(client, sid, "north")
    return client.put(f"/player/{sid}/pickup/{item_here(client, sid, 'BEER')}")


def call_look_around(client):
    return client.get(f"/player/{start(client)}/location")


def call_look_in_direction(client):
    return client.get(f"/player/{start(client)}/look/north")


def call_move(client):
    return client.put(f"/player/{start(client)}/move/north")


SUCCESS_CALLS = {
    "startGame": call_start_game,
    "listPlayers": call_list_players,
    "quitGame": call_quit_game,
    "readLeaderboard": call_read_leaderboard,
    "inspectItem": call_inspect_item,
    "inspectBag": call_inspect_bag,
    "saveGame": call_save_game,
    "registerAccount": call_register_account,
    "login": call_login,
    "sendChatMessage": call_send_chat_message,
    "readChat": call_read_chat,
    "actOnItem": call_act_on_item,
    "legacyPickup": call_legacy_pickup,
    "lookAround": call_look_around,
    "lookInDirection": call_look_in_direction,
    "move": call_move,
}


def test_every_operation_of_the_contract_has_a_live_call():
    assert set(SUCCESS_CALLS) == set(operations())


@pytest.mark.parametrize("operation_id", sorted(SUCCESS_CALLS))
def test_the_success_response_matches_the_contract(client, operation_id):
    response = SUCCESS_CALLS[operation_id](client)
    assert response.status_code < 300, response.text
    assert_matches(operation_id, response)


def test_a_list_or_leaderboard_is_not_empty_when_checked(client):
    """The array checks above must validate real elements, not an empty list."""
    assert call_list_players(client).json()
    assert call_read_leaderboard(client).json()


# --- 2. Each error reason has its one status ------------------------------------


def error_invalid_request(client):
    return "startGame", client.post("/game/player", json={})


def error_invalid_value(client):
    return "startGame", client.post("/game/player", json={"name": "admin"})


def error_not_found(client):
    return "lookAround", client.get("/player/000000-000000000000-00000000/location")


def error_not_allowed(client):
    return "move", client.put(f"/player/{start(client)}/move/up")


ERROR_CALLS = {
    "INVALID_REQUEST": error_invalid_request,
    "INVALID_VALUE": error_invalid_value,
    "NOT_FOUND": error_not_found,
    "NOT_ALLOWED": error_not_allowed,
}


def test_every_error_reason_has_a_live_call():
    assert set(ERROR_CALLS) == set(STATUS_BY_REASON)


@pytest.mark.parametrize("reason", sorted(ERROR_CALLS))
def test_an_error_reason_answers_with_its_status(client, reason):
    operation_id, response = ERROR_CALLS[reason](client)
    assert response.status_code == STATUS_BY_REASON[reason]
    assert response.json()["code"] == response.status_code
    assert_matches(operation_id, response)


def test_each_status_of_an_error_has_a_reason():
    statuses = {
        int(status)
        for _, _, operation in operations().values()
        for status in operation["responses"]
        if int(status) >= 400
    }
    assert statuses <= set(STATUS_BY_REASON.values())


# --- 3. The data that others read ------------------------------------------------


def test_a_save_writes_a_player_state_of_the_contract(client, tmp_path):
    sid = start(client)
    go(client, sid, "north")
    client.put(f"/player/{sid}/item/{item_here(client, sid, 'BEER')}/use/pick")
    client.post(f"/player/{sid}/save")
    with sqlite3.connect(tmp_path / "katacombs.db") as connection:
        (payload,) = connection.execute("SELECT payload FROM saves").fetchone()
    Draft202012Validator(PLAYER_STATE).validate(json.loads(payload))


def test_a_quit_with_an_account_writes_a_snapshot_of_the_contract(client, tmp_path):
    client.post("/accounts", json={"email": "ana@example.org", "password": "pw", "name": "ana"})
    sid = client.post("/accounts/login", json={"email": "ana@example.org", "password": "pw"}).json()["sid"]
    go(client, sid, "north")
    client.delete(f"/game/player/{sid}")
    with sqlite3.connect(tmp_path / "katacombs.db") as connection:
        (snapshot,) = connection.execute("SELECT snapshot FROM accounts").fetchone()
    Draft202012Validator(PLAYER_STATE).validate(json.loads(snapshot))


def test_a_win_appends_a_high_score_line_of_the_contract(client, tmp_path):
    go(client, start(client), *WIN_ROUTE)
    lines = (tmp_path / "highscores.jsonl").read_text(encoding="utf-8").splitlines()
    assert len(lines) == 1
    Draft202012Validator(HIGHSCORE_LINE).validate(json.loads(lines[0]))


@pytest.mark.parametrize(
    "schema, broken",
    [
        (PLAYER_STATE, {"location": "BRICK LANE", "bag": [], "gold": 0}),
        (HIGHSCORE_LINE, {"name": "ANA", "score": 5, "at": "yesterday"}),
    ],
    ids=["player-state", "highscore-line"],
)
def test_a_schema_rejects_a_drifted_shape(schema, broken):
    assert list(Draft202012Validator(schema).iter_errors(broken))


# --- 4. The contract cites rules that exist --------------------------------------


def test_each_cited_rule_exists_in_the_specification():
    text = (SPEC / "specification.md").read_text(encoding="utf-8")
    rule_ids = set(re.findall(r"^#{3,4} ([A-Z]+-\d+) — ", text, flags=re.MULTILINE))
    for operation_id, (_, _, operation) in operations().items():
        cited = operation.get("x-rules", [])
        assert cited, f"{operation_id} cites no rule"
        assert set(cited) <= rule_ids, f"{operation_id} cites {set(cited) - rule_ids}"
