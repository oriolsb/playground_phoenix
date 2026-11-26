"""ARCH-8: the REST adapter runs on fake inbound ports, with no game (decision 0019)."""

from fastapi.testclient import TestClient

from brown_field.adapters.rest.app import build_app
from brown_field.kata import Bag, InboundPorts, Location, Player, PlayerNotFound


class Unused:
    def execute(self, *args):
        raise AssertionError("this port is not part of the test")


class FakeRegisterPlayer:
    def execute(self, name: str) -> Player:
        here = Location(title="FAKE ROOM", description="A ROOM OF A FAKE.", exits=[], items=[])
        return Player(sid="1", name=name.upper(), location=here, bag=Bag(energy=7), energy=7)


class TiredBag:
    def execute(self, player_sid: str) -> Bag:
        if player_sid != "1":
            raise PlayerNotFound(f"PLAYER {player_sid} NOT FOUND.")
        return Bag(energy=0)


def fake_ports(**overrides) -> InboundPorts:
    names = InboundPorts.__dataclass_fields__
    return InboundPorts(**{name: overrides.get(name, Unused()) for name in names})


def test_the_adapter_answers_from_a_fake_port():
    client = TestClient(build_app(fake_ports(register_player=FakeRegisterPlayer())))
    response = client.post("/game/player", json={"name": "ana"})
    assert response.status_code == 201
    body = response.json()
    assert (body["name"], body["location"]["title"], body["energy"]) == ("ANA", "FAKE ROOM", 7)


def test_the_energy_gate_reads_the_energy_through_a_port():
    client = TestClient(build_app(fake_ports(inspect_bag=TiredBag())))
    tired = client.put("/player/1/move/north")
    assert (tired.status_code, tired.json()["message"]) == (405, "YOU ARE TOO TIRED TO MOVE. EAT OR DRINK SOMETHING.")
    unknown = client.put("/player/2/move/north")
    assert (unknown.status_code, unknown.json()["message"]) == (404, "PLAYER 2 NOT FOUND.")
