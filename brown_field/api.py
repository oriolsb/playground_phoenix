"""REST API for Katacombs: the entry points of the frozen boundary (ENTRY-1, ENTRY-2).

The routes live in `brown_field/adapters/rest/app.py` (decision 0015).
"""

from .adapters.rest.app import build_app
from .game import InMemoryGame


def create_app(game: InMemoryGame | None = None):
    return build_app(game or InMemoryGame())


app = create_app()
