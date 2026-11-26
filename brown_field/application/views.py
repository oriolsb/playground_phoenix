"""The mapping from the game state to the view models of `kata.py` (decision 0020).

The ports answer these views. The REST adapter maps them to JSON.
"""

from ..domain.player import PlayerState
from ..kata import Bag, Location, Player
from .state import GameState


def to_location(game: GameState, title: str, note: str = "") -> Location:
    place = game.places[title]
    return Location(
        title=place.title,
        description=f"{place.description} {note}".strip(),
        exits=list(place.exits),
        items=[game.items[sid] for sid in place.items],
        is_exit=place.is_exit,
    )


def to_bag(game: GameState, state: PlayerState) -> Bag:
    return Bag(items=[game.items[sid] for sid in state.bag], gold=state.gold, energy=state.energy)


def to_player(game: GameState, state: PlayerState) -> Player:
    return Player(
        sid=state.sid,
        name=state.name,
        location=to_location(game, state.location),
        bag=to_bag(game, state),
        has_won=state.has_won,
        energy=state.energy,
    )
