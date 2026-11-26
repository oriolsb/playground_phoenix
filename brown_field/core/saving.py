"""Saving a player, so that a restart restores the bag and the place."""

from .rules import utc_stamp
from .state import GameState, snapshot_of


class SaveGameUseCase:
    """The SaveGame port. INC-3110: a laptop sleep lost every bag."""

    def __init__(self, game: GameState) -> None:
        self.game = game

    def execute(self, player_sid: str) -> str:
        """Save the player, and return where the save went (SAVE-1 leaks it)."""
        state = self.game.player(player_sid)
        # 2023: the payload also holds the energy and the move count.
        payload = snapshot_of(state)
        return self.game.ports.saves.write(state.sid, state.name, payload, utc_stamp(self.game.ports.clock))
