"""The limits of the game, and the names that its rules use (decisions 0012, 0016).

The world itself is data, in `brown_field/spec/world.json`. A title or an item
sid appears here only when a rule names it.
"""

from .types import Direction

BAG_SLOTS = 8
ITEMS_PER_SLOT = 3
NAME_MAX_LENGTH = 50
MAX_PLAYERS = 20
RESERVED_NAMES = {"ADMIN"}
START_ENERGY = 12
MAX_ENERGY = 20
RAT_CHANCE = 0.2

OPPOSITE = {
    Direction.NORTH: Direction.SOUTH,
    Direction.SOUTH: Direction.NORTH,
    Direction.EAST: Direction.WEST,
    Direction.WEST: Direction.EAST,
    Direction.UP: Direction.DOWN,
    Direction.DOWN: Direction.UP,
}

# The titles that rules name.
CELLAR = "BREWERY CELLAR"  # MOVE-8: the rat
TUBE_TUNNEL = "OLD TUBE TUNNEL"  # MOVE-8: where the rat drops the item
MARKET = "SPITALFIELDS MARKET"  # MOVE-6: closed for cleaning
BACK_YARD = "BACK YARD"  # ACT-13, ACT-14: the manhole
KATACOMBS = "KATACOMBS"  # ACT-13: below the open manhole

# The item sids that rules name.
KEY = "000100-000000000000-00000002"  # ACT-14
MANHOLE = "000100-000000000000-00000005"  # ACT-13, ACT-14

ENERGY_FROM = {"BREAD": 5, "BEER": 3}  # ACT-15, by item name
