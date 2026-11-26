"""A win and the leaderboard (WIN-1, WIN-2, WIN-3, BOARD-1)."""

from ..kata import FinishedGame
from .game import Game
from .state import PlayerState


def record_win(game: Game, state: PlayerState, score: int) -> None:
    game.highscores.append(state.name, score)
    game.finished_games.append(
        {"name": state.name, "score": score, "moves": state.moves}
    )


class LeaderboardUseCase:
    def __init__(self, game: Game) -> None:
        self.game = game

    def execute(self) -> list[FinishedGame]:
        ranked = sorted(self.game.finished_games, key=lambda entry: -entry["score"])
        return [FinishedGame(**entry) for entry in ranked]
