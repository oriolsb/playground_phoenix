"""Looking around and in a direction (LOOK-*)."""

from ..kata import Direction, Location
from .errors import NotAllowed
from .game import Game


class LookAroundUseCase:
    def __init__(self, game: Game) -> None:
        self.game = game

    def execute(self, player_sid: str) -> Location:
        return self.game.to_location(self.game.player(player_sid).location)


class LookInDirectionUseCase:
    def __init__(self, game: Game) -> None:
        self.game = game

    def execute(self, player_sid: str, direction: Direction) -> Location:
        state = self.game.player(player_sid)
        exits = self.game.places[state.location].exits
        if direction not in exits:
            raise NotAllowed("THERE IS NOTHING IN THAT DIRECTION.")
        return self.game.to_location(exits[direction])
