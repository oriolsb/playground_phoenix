"""The REST API for Katacombs: the driving adapter.

Each route parses the request, calls the use cases, and turns the answer into
JSON. It holds no game rule and reads no game state (OPS-3, decision 0012).
"""

from typing import Annotated

from fastapi import FastAPI, Path, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from .game import (
    InMemoryGame,
    InspectBagUseCase,
    InspectItemUseCase,
    InvalidName,
    ItemNotFound,
    KatacombsError,
    ListPlayersUseCase,
    LoginUseCase,
    LookAroundUseCase,
    LookInDirectionUseCase,
    MoveUseCase,
    NotAllowed,
    PickUpUseCase,
    PlayerNotFound,
    QuitGameUseCase,
    ReadMessagesUseCase,
    RegisterAccountUseCase,
    RegisterPlayerUseCase,
    SaveGameUseCase,
    SendMessageUseCase,
    ShowLeaderboardUseCase,
    UseItemUseCase,
    ViewPlayerUseCase,
)
from .kata import Action, Bag, Direction, Item, Location, Player

PlayerSid = Annotated[str, Path(alias="playerSid")]
ItemSid = Annotated[str, Path(alias="itemSid")]


class NewPlayer(BaseModel):
    name: str


class NewAccount(BaseModel):
    email: str
    password: str
    name: str


class Credentials(BaseModel):
    email: str
    password: str


class NewMessage(BaseModel):
    text: str


def item_json(item: Item) -> dict:
    return {
        "sid": item.sid,
        "name": item.name,
        "description": item.description,
        "actions": [action.value for action in item.actions],
        "value": item.value,
    }


def bag_json(bag: Bag) -> dict:
    return {
        "items": [item_json(item) for item in bag.items],
        "gold": bag.gold,
        "score": bag.score,
    }


def location_json(location: Location) -> dict:
    return {
        "title": location.title,
        "description": location.description,
        "exits": [direction.value for direction in location.exits],
        "items": [item_json(item) for item in location.items],
        "isExit": location.is_exit,
    }


def player_json(player: Player) -> dict:
    return {
        "sid": player.sid,
        "name": player.name,
        "location": location_json(player.location),
        "bag": bag_json(player.bag),
        "hasWon": player.has_won,
        "energy": player.energy,
    }


def error(status: int, message: str) -> JSONResponse:
    return JSONResponse(
        status_code=status, content={"code": status, "message": message}
    )


def create_app(game: InMemoryGame | None = None) -> FastAPI:
    game = game or InMemoryGame()
    app = FastAPI(
        title="Katacombs API",
        version="1.0.0",
        description="This API allows playing a text-based adventure game called Katacombs",
    )

    @app.exception_handler(KatacombsError)
    def katacombs_error(request: Request, exc: KatacombsError) -> JSONResponse:
        if isinstance(exc, (PlayerNotFound, ItemNotFound)):
            return error(404, str(exc))
        if isinstance(exc, InvalidName):
            return error(400, str(exc))
        if isinstance(exc, NotAllowed):
            return error(405, str(exc))
        return error(500, str(exc))

    @app.exception_handler(RequestValidationError)
    def invalid_request(request: Request, exc: RequestValidationError) -> JSONResponse:
        return error(400, "INVALID REQUEST.")

    @app.post("/game/player", status_code=201, tags=["Game"])
    def start_game(body: NewPlayer) -> dict:
        return player_json(RegisterPlayerUseCase(game).execute(body.name))

    @app.get("/game/player", tags=["Game"])
    def list_players() -> list[dict]:
        return [player_json(player) for player in ListPlayersUseCase(game).execute()]

    @app.delete("/game/player/{playerSid}", tags=["Game"])
    def quit_game(player_sid: PlayerSid) -> dict:
        QuitGameUseCase(game).execute(player_sid)
        return {"message": "Game Over"}

    @app.get("/leaderboard", tags=["Game"])
    def leaderboard() -> list[dict]:
        return [
            {"name": entry.name, "score": entry.score, "moves": entry.moves}
            for entry in ShowLeaderboardUseCase(game).execute()
        ]

    @app.get("/items/{itemSid}", tags=["Player"])
    def inspect_item(item_sid: ItemSid) -> dict:
        return item_json(InspectItemUseCase(game).execute(item_sid))

    @app.get("/player/{playerSid}/bag", tags=["Player"])
    def inspect_bag(player_sid: PlayerSid) -> dict:
        bag = bag_json(InspectBagUseCase(game).execute(player_sid))
        return {**bag, "energy": ViewPlayerUseCase(game).execute(player_sid).energy}

    @app.post("/player/{playerSid}/save", tags=["Player"])
    def save_game(player_sid: PlayerSid) -> dict:
        path = SaveGameUseCase(game).execute(player_sid)
        return {"message": "GAME SAVED.", "path": path}

    @app.post("/accounts", status_code=201, tags=["Accounts"])
    def register_account(body: NewAccount) -> dict:
        account = RegisterAccountUseCase(game).execute(body.email, body.password, body.name)
        return {"email": account.email, "name": account.name}

    @app.post("/accounts/login", tags=["Accounts"])
    def login(body: Credentials) -> dict:
        return player_json(LoginUseCase(game).execute(body.email, body.password))

    @app.post("/player/{playerSid}/chat", status_code=201, tags=["Chat"])
    def send_message(player_sid: PlayerSid, body: NewMessage) -> dict:
        SendMessageUseCase(game).execute(player_sid, body.text)
        return {"message": "SENT."}

    @app.get("/player/{playerSid}/chat", tags=["Chat"])
    def read_messages(player_sid: PlayerSid) -> list[dict]:
        return [
            {"name": message.name, "text": message.text, "at": message.at}
            for message in ReadMessagesUseCase(game).execute(player_sid)
        ]

    @app.put("/player/{playerSid}/item/{itemSid}/use/{action}", tags=["Player"])
    def use_item(player_sid: PlayerSid, item_sid: ItemSid, action: Action) -> dict:
        return {"message": UseItemUseCase(game).execute(player_sid, item_sid, action)}

    # Mobile client v1 still calls this route. Do not remove it.
    @app.put("/player/{playerSid}/pickup/{itemSid}", tags=["Legacy"])
    def pickup(player_sid: PlayerSid, item_sid: ItemSid) -> dict:
        return {"message": PickUpUseCase(game).execute(player_sid, item_sid)}

    @app.get("/player/{playerSid}/location", tags=["Player"])
    def look_around(player_sid: PlayerSid) -> dict:
        return location_json(LookAroundUseCase(game).execute(player_sid))

    @app.get("/player/{playerSid}/look/{direction}", tags=["Player"])
    def look_in_direction(player_sid: PlayerSid, direction: Direction) -> dict:
        return location_json(
            LookInDirectionUseCase(game).execute(player_sid, direction)
        )

    @app.put("/player/{playerSid}/move/{direction}", tags=["Player"])
    def move(player_sid: PlayerSid, direction: Direction) -> dict:
        return location_json(MoveUseCase(game).execute(player_sid, direction))

    return app


app = create_app()
