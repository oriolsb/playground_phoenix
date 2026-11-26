"""REST API for Katacombs: the entry points of the frozen boundary (ENTRY-1, ENTRY-2).

The routes live in `brown_field/adapters/rest/app.py`. They receive the
inbound ports, which `game.inbound_ports` builds from the game (decision 0019).
"""

from .adapters.rest.app import build_app
from .game import InMemoryGame, inbound_ports


def create_app(game: InMemoryGame | None = None):
    return build_app(inbound_ports(game or InMemoryGame()))


app = create_app()
