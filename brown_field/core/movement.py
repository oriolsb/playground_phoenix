"""Moving: the energy gate, the exits, the market hours, the rat and the win (MOVE-*, WIN-1)."""

from datetime import datetime

from ..kata import Direction, Location
from .errors import NotAllowed
from .game import Game
from .state import PlayerState
from .winning import record_win


RAT_CHANCE = 0.2

# The locations that the market hours (MOVE-6) and the rat (MOVE-8) name.
MARKET = "SPITALFIELDS MARKET"
CELLAR = "BREWERY CELLAR"
TUBE_TUNNEL = "OLD TUBE TUNNEL"


def market_is_cleaning(now: datetime) -> bool:
    # Cleaning crew contract (2023): the market is closed from minute 50 to
    # minute 59 of each hour. Ask facilities before you change this.
    return now.minute >= 50


class MoveUseCase:
    def __init__(self, game: Game) -> None:
        self.game = game

    def execute(self, player_sid: str, direction: Direction) -> Location:
        game = self.game
        state = game.player(player_sid)
        # Added for the mobile release: a tired player cannot move (decision 0011).
        if state.energy <= 0:
            raise NotAllowed("YOU ARE TOO TIRED TO MOVE. EAT OR DRINK SOMETHING.")
        if state.has_won:
            raise NotAllowed("THE GAME IS OVER. YOU ALREADY FOUND THE EXIT.")
        exits = game.places[state.location].exits
        if direction not in exits:
            raise NotAllowed("YOU CAN'T GO THAT WAY.")
        target = exits[direction]
        if target == MARKET and market_is_cleaning(game.clock()):
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
            record_win(game, state, score)
        return game.to_location(state.location, note)

    def rat(self, state: PlayerState) -> str:
        cheap = [sid for sid in state.bag if not self.game.items[sid].value]
        if not cheap or self.game.rng.random() >= RAT_CHANCE:
            return ""
        stolen = self.game.rng.choice(cheap)
        state.bag.remove(stolen)
        self.game.places[TUBE_TUNNEL].items.append(stolen)
        return f"A RAT RUNS OFF WITH YOUR {self.game.items[stolen].name}."
