"""The legacy pickup route of mobile client v1."""

from .state import GameState


class PickUpUseCase:
    """Mobile client v1 still calls this. Do not remove it (decision 0003).

    It skips every rule of UseItem: no bag limit, no move count, no game-over
    check, and it answers "OK" even when the item is not here.
    """

    def __init__(self, game: GameState) -> None:
        self.game = game

    def execute(self, player_sid: str, item_sid: str) -> str:
        state = self.game.player(player_sid)
        self.game.item(item_sid)
        here = self.game.places[state.location]
        if item_sid in here.items:
            here.items.remove(item_sid)
            state.bag.append(item_sid)
        return "OK"
