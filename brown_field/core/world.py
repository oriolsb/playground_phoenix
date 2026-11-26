"""The world: the places, the items, and how the places connect.

Built in code at every start; a save does not hold it (decision 0005).
"""

from dataclasses import dataclass

from ..kata import Action, Direction, Item

OPPOSITE = {
    Direction.NORTH: Direction.SOUTH,
    Direction.SOUTH: Direction.NORTH,
    Direction.EAST: Direction.WEST,
    Direction.WEST: Direction.EAST,
    Direction.UP: Direction.DOWN,
    Direction.DOWN: Direction.UP,
}

BRICK_LANE = "BRICK LANE"
BREWERY = "OLD TRUMAN BREWERY"
CELLAR = "BREWERY CELLAR"
ROOFTOP = "BREWERY ROOFTOP"
MARKET = "SPITALFIELDS MARKET"
BACK_YARD = "BACK YARD"
BAKERY = "BRICK LANE BAKERY"
FLOWER_MARKET = "COLUMBIA ROAD"
BOXPARK = "BOXPARK"
ARCHES = "RAILWAY ARCHES"
TUBE_TUNNEL = "OLD TUBE TUNNEL"
JUNCTION = "TUNNEL JUNCTION"
KATACOMBS = "KATACOMBS"
KATACOMBS_EXIT = "KATACOMBS EXIT"

START = BRICK_LANE

# Product asked for a slide from the cellar into the tunnels (2022). The
# world rule "each connection has a way back" does not apply to it.
ONE_WAY = {(CELLAR, Direction.DOWN)}

BEER = "000100-000000000000-00000001"
KEY = "000100-000000000000-00000002"
RING = "000100-000000000000-00000003"
CRATE = "000100-000000000000-00000004"
MANHOLE = "000100-000000000000-00000005"
GOBLET = "000100-000000000000-00000006"
BEER_2 = "000100-000000000000-00000007"
BREAD_1 = "000100-000000000000-00000008"
BREAD_2 = "000100-000000000000-00000009"
BREAD_3 = "000100-000000000000-00000010"
UMBRELLA = "000100-000000000000-00000011"
FLOWERS = "000100-000000000000-00000012"
CANDLE = "000100-000000000000-00000013"
MAP = "000100-000000000000-00000014"
ROPE = "000100-000000000000-00000015"
SKULL = "000100-000000000000-00000016"



@dataclass
class Place:
    title: str
    description: str
    exits: dict[Direction, str]
    items: list[str]
    gold: int = 0
    is_exit: bool = False


def build_items() -> dict[str, Item]:
    takeable = [Action.PICK, Action.DROP]
    usable = [Action.PICK, Action.DROP, Action.USE]
    beer = "A BOTTLE OF CRAFTED BEER FROM THE BREWERY."
    bread = "A WARM LOAF OF BREAD. IT SMELLS GOOD."
    items = [
        Item(BEER, "BEER", beer, usable),
        Item(BEER_2, "BEER", beer, usable),
        Item(
            KEY,
            "KEY",
            "A SMALL IRON KEY. IT HAS A PICTURE OF A MANHOLE ON IT.",
            usable,
        ),
        Item(
            RING,
            "RING",
            "A SILVER RING. SOMEBODY LOST IT A LONG TIME AGO.",
            takeable,
            value=20,
        ),
        Item(
            CRATE,
            "CRATE",
            "A HEAVY WOODEN CRATE WITH A LOOSE LID.",
            [Action.OPEN, Action.CLOSE],
        ),
        Item(
            MANHOLE,
            "MANHOLE",
            "A ROUND IRON MANHOLE COVER WITH A KEYHOLE.",
            [Action.OPEN, Action.CLOSE],
        ),
        Item(
            GOBLET,
            "GOBLET",
            "A GOLDEN GOBLET. IT LOOKS VERY VALUABLE.",
            takeable,
            value=50,
        ),
        Item(BREAD_1, "BREAD", bread, usable),
        Item(BREAD_2, "BREAD", bread, usable),
        Item(BREAD_3, "BREAD", bread, usable),
        Item(UMBRELLA, "UMBRELLA", "A BLACK UMBRELLA WITH A BROKEN RIB.", takeable),
        Item(FLOWERS, "FLOWERS", "A BUNCH OF SUNFLOWERS.", takeable),
        Item(CANDLE, "CANDLE", "A HALF-BURNT CANDLE.", takeable),
        Item(MAP, "MAP", "AN OLD MAP OF THE TUBE. SOME LINES ARE CROSSED OUT.", takeable),
        Item(ROPE, "ROPE", "TEN METRES OF STRONG ROPE.", takeable),
        Item(SKULL, "SKULL", "A SMALL SKULL. IT GRINS AT YOU.", takeable, value=5),
    ]
    return {item.sid: item for item in items}


def build_places() -> dict[str, Place]:
    places = [
        Place(
            BRICK_LANE,
            "YOU ARE STANDING AT THE END OF BRICK LANE BEFORE A SMALL BRICK "
            "BUILDING CALLED THE OLD TRUMAN BREWERY. AROUND YOU IS A FOREST OF "
            "RESTAURANTS. A SMALL STREAM OF CRAFTED BEER FLOWS OUT OF THE "
            "BUILDING AND DOWN A GULLY.",
            {
                Direction.NORTH: BREWERY,
                Direction.EAST: MARKET,
                Direction.WEST: BAKERY,
                Direction.SOUTH: BOXPARK,
            },
            [],
        ),
        Place(
            BREWERY,
            "YOU ARE INSIDE THE OLD BREWERY. COPPER VATS LINE THE WALLS. A "
            "STAIRCASE GOES UP TO THE ROOF AND A TRAPDOOR GOES DOWN TO THE "
            "CELLAR.",
            {
                Direction.SOUTH: BRICK_LANE,
                Direction.UP: ROOFTOP,
                Direction.DOWN: CELLAR,
            },
            [BEER, BEER_2],
            gold=5,
        ),
        Place(
            CELLAR,
            "A COLD CELLAR FULL OF EMPTY BARRELS. SOMETHING SHINES ON THE FLOOR. "
            "IN A CORNER, A METAL SLIDE GOES DOWN INTO THE DARK.",
            {Direction.UP: BREWERY, Direction.DOWN: TUBE_TUNNEL},
            [RING],
            gold=20,
        ),
        Place(
            ROOFTOP,
            "YOU ARE ON THE ROOF OF THE BREWERY. YOU CAN SEE ALL OF SHOREDITCH.",
            {Direction.DOWN: BREWERY},
            [KEY],
        ),
        Place(
            MARKET,
            "THE OLD SPITALFIELDS MARKET. THE STALLS ARE CLOSED FOR THE NIGHT.",
            {Direction.WEST: BRICK_LANE, Direction.SOUTH: BACK_YARD},
            [CRATE],
        ),
        Place(
            BACK_YARD,
            "A SMALL YARD BEHIND THE MARKET. THERE IS A MANHOLE COVER IN THE GROUND.",
            {Direction.NORTH: MARKET},
            [MANHOLE],
        ),
        Place(
            BAKERY,
            "A SMALL BAKERY THAT NEVER CLOSES. THE SHELVES ARE FULL OF BREAD.",
            {Direction.EAST: BRICK_LANE, Direction.NORTH: FLOWER_MARKET},
            [BREAD_1, BREAD_2, BREAD_3, UMBRELLA],
        ),
        Place(
            FLOWER_MARKET,
            "THE COLUMBIA ROAD FLOWER MARKET. SOMEBODY LEFT SOME FLOWERS AND A FEW COINS.",
            {Direction.SOUTH: BAKERY},
            [FLOWERS],
            gold=10,
        ),
        Place(
            BOXPARK,
            "SHIPPING CONTAINERS FULL OF SHOPS. MOST OF THEM ARE EMPTY.",
            {Direction.NORTH: BRICK_LANE, Direction.EAST: ARCHES},
            [CANDLE],
            gold=5,
        ),
        Place(
            ARCHES,
            "OLD RAILWAY ARCHES. A RUSTY LADDER GOES DOWN INTO A TUNNEL.",
            {Direction.WEST: BOXPARK, Direction.DOWN: TUBE_TUNNEL},
            [MAP],
        ),
        Place(
            TUBE_TUNNEL,
            "AN OLD TUBE TUNNEL. NO TRAIN HAS COME HERE FOR FIFTY YEARS. A LADDER "
            "GOES UP.",
            {Direction.UP: ARCHES, Direction.EAST: JUNCTION},
            [ROPE],
        ),
        Place(
            JUNCTION,
            "A TUNNEL JUNCTION. OLD SIGNS POINT IN ALL DIRECTIONS.",
            {Direction.WEST: TUBE_TUNNEL, Direction.NORTH: KATACOMBS},
            [SKULL],
        ),
        Place(
            KATACOMBS,
            "DAMP STONE TUNNELS. SKULLS LINE THE WALLS. A FAINT LIGHT GLOWS TO "
            "THE EAST.",
            {Direction.EAST: KATACOMBS_EXIT, Direction.SOUTH: JUNCTION},
            [GOBLET],
            gold=30,
        ),
        Place(
            KATACOMBS_EXIT,
            "DAYLIGHT! YOU HAVE FOUND THE WAY OUT OF THE KATACOMBS.",
            {Direction.WEST: KATACOMBS},
            [],
            is_exit=True,
        ),
    ]
    titles = [place.title for place in places]
    if len(titles) != len(set(titles)):
        raise ValueError("Each location must have a unique title")
    return {place.title: place for place in places}


def check_connections(places: dict[str, Place]) -> None:
    for place in places.values():
        for direction, target in place.exits.items():
            if (place.title, direction) in ONE_WAY:
                continue
            if places[target].exits.get(OPPOSITE[direction]) != place.title:
                raise ValueError(
                    f"{place.title} goes {direction.value} to {target}, "
                    f"but {target} does not go {OPPOSITE[direction].value} back"
                )

