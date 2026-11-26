"""Saving a player (SAVE-1)."""

from .game import Game
from .state import to_payload


class SaveGameUseCase:
    """The SaveGame port. INC-3110: a laptop sleep lost every bag."""

    def __init__(self, game: Game) -> None:
        self.game = game

    def execute(self, player_sid: str) -> str:
        state = self.game.player(player_sid)
        # 2023: the payload also holds the energy and the move count.
        return self.game.save_store.write_save(state.sid, state.name, to_payload(state))
