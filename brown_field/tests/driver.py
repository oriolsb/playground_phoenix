"""A player's view of the game, through the REST API only."""

from fastapi.testclient import TestClient


class Game:
    """Plays through the REST API, and finds items by name, as a player does."""

    def __init__(self, client: TestClient) -> None:
        self.client = client

    def start(self, name: str = "ANA") -> str:
        response = self.client.post("/game/player", json={"name": name})
        assert response.status_code == 201, response.text
        return response.json()["sid"]

    def go(self, sid: str, *directions: str) -> dict:
        """Move through each direction; each move must succeed."""
        body = {}
        for direction in directions:
            response = self.client.put(f"/player/{sid}/move/{direction}")
            assert response.status_code == 200, f"{direction}: {response.text}"
            body = response.json()
        return body

    def look(self, sid: str) -> dict:
        return self.client.get(f"/player/{sid}/location").json()

    def bag(self, sid: str) -> dict:
        return self.client.get(f"/player/{sid}/bag").json()

    def item_sid(self, sid: str, name: str) -> str:
        """The sid of the first item with this name, in the location or in the bag."""
        for item in self.look(sid)["items"] + self.bag(sid)["items"]:
            if item["name"] == name:
                return item["sid"]
        raise AssertionError(f"no {name} at {self.look(sid)['title']} or in the bag")

    def act(self, sid: str, item_name: str, action: str):
        item = self.item_sid(sid, item_name)
        return self.client.put(f"/player/{sid}/item/{item}/use/{action}")
