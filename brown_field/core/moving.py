"""Moving: the market's cleaning hours, the rat in the cellar, and the win."""

from ..kata import Direction, Location
from .errors import NotAllowed
from .rules import RAT_CHANCE, market_is_cleaning, utc_stamp
from .state import FinishedGame, GameState, PlayerState
from .world import CELLAR, MARKET, TUBE_TUNNEL


class MoveUseCase:
    # The energy gate is not here: it lives in the REST adapter until decision
    # 0011 is accepted (MOVE-5, contested).

    def __init__(self, game: GameState) -> None:
        self.game = game

    def execute(self, player_sid: str, direction: Direction) -> Location:
        game = self.game
        state = game.player(player_sid)
        if state.has_won:
            raise NotAllowed("THE GAME IS OVER. YOU ALREADY FOUND THE EXIT.")
        exits = game.places[state.location].exits
        if direction not in exits:
            raise NotAllowed("YOU CAN'T GO THAT WAY.")
        target = exits[direction]
        if target == MARKET and market_is_cleaning(game.ports.clock):
            raise NotAllowed("THE MARKET IS CLOSED FOR CLEANING. COME BACK LATER.")
        state.energy -= 1
        state.moves += 1
        game.visit(state, target)
        note = ""
        if target == CELLAR:
            note = self.rat(state)
        if game.places[state.location].is_exit:
            state.has_won = True
            score = game.to_bag(state).score
            game.ports.high_scores.append(state.name, score, at=utc_stamp(game.ports.clock))
            game.finished_games.append(FinishedGame(name=state.name, score=score, moves=state.moves))
        return game.to_location(state.location, note)

    def rat(self, state: PlayerState) -> str:
        cheap = [sid for sid in state.bag if not self.game.items[sid].value]
        if not cheap or self.game.ports.random.random() >= RAT_CHANCE:
            return ""
        stolen = self.game.ports.random.choice(cheap)
        state.bag.remove(stolen)
        self.game.places[TUBE_TUNNEL].items.append(stolen)
        return f"A RAT RUNS OFF WITH YOUR {self.game.items[stolen].name}."
