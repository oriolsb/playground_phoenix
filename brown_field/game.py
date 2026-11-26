"""In-memory implementation of the Katacombs use cases."""

import hashlib
import math
from collections import Counter
from dataclasses import dataclass, field
from datetime import timezone

from .adapters.files.high_scores import JsonlHighScores
from .adapters.system.clock import SystemClock
from .adapters.system.random_source import StdRandom
from .adapters.sqlite.stores import SqliteAccounts, SqliteSaves
from .application.ports_out import (
    AccountStore,
    Clock,
    HighScoreSink,
    RandomSource,
    SavedPlayer,
    SaveStore,
    StoredAccount,
)
from .kata import Action, Bag, Direction, Item, Location, Player

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

ENERGY_FROM = {"BREAD": 5, "BEER": 3}


class KatacombsError(Exception):
    pass


class PlayerNotFound(KatacombsError):
    pass


class ItemNotFound(KatacombsError):
    pass


class InvalidName(KatacombsError):
    pass


class NotAllowed(KatacombsError):
    pass


@dataclass
class Place:
    title: str
    description: str
    exits: dict[Direction, str]
    items: list[str]
    gold: int = 0
    is_exit: bool = False


@dataclass
class PlayerState:
    sid: str
    name: str
    location: str
    bag: list[str] = field(default_factory=list)
    gold: int = 0
    energy: int = START_ENERGY
    moves: int = 0
    visited: set[str] = field(default_factory=set)
    opened: set[str] = field(default_factory=set)
    has_won: bool = False


# An account, as the game and the store keep it (decision 0014).
Account = StoredAccount


@dataclass
class ChatMessage:
    location: str
    name: str
    text: str
    at: str


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


def market_is_cleaning(clock: Clock) -> bool:
    # Cleaning crew contract (2023): the market is closed from minute 50 to
    # minute 59 of each hour. Ask facilities before you change this.
    return clock.now().minute >= 50


def slots_used(names: list[str]) -> int:
    return sum(math.ceil(count / ITEMS_PER_SLOT) for count in Counter(names).values())


def password_hash(password: str) -> str:
    # TODO: bcrypt (2023)
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def snapshot_of(state: "PlayerState") -> dict:
    return {
        "location": state.location,
        "bag": list(state.bag),
        "gold": state.gold,
        "energy": state.energy,
        "moves": state.moves,
        "visited": sorted(state.visited),
        "opened": sorted(state.opened),
        "has_won": state.has_won,
    }


class InMemoryGame:
    def __init__(
        self,
        *,
        clock: Clock | None = None,
        random_source: RandomSource | None = None,
        high_scores: HighScoreSink | None = None,
        saves: SaveStore | None = None,
        accounts: AccountStore | None = None,
    ) -> None:
        # The outbound ports (decision 0013). Each default calls the standard
        # library at the moment of each call, as the code did before.
        self.clock: Clock = clock or SystemClock()
        self.random_source: RandomSource = random_source or StdRandom()
        self.high_scores: HighScoreSink = high_scores or JsonlHighScores()
        # The storage ports (decision 0014). The defaults are the database file.
        self.save_store: SaveStore = saves or SqliteSaves()
        self.account_store: AccountStore = accounts or SqliteAccounts()
        self.places = build_places()
        self.items = build_items()
        self.gold_inside = {CRATE: 10}
        self.open_items: set[str] = set()
        self.locked_items: set[str] = {MANHOLE}
        self.players: dict[str, PlayerState] = {}
        self.finished_games: list[dict] = []
        self.accounts: dict[str, Account] = {}
        self.chat: list[ChatMessage] = []
        check_connections(self.places)
        self.load_saves()
        self.load_accounts()

    def load_accounts(self) -> None:
        for account in self.account_store.load_all():
            self.accounts[account.email] = account

    def account_of(self, player_sid: str) -> Account | None:
        for account in self.accounts.values():
            if account.player_sid == player_sid:
                return account
        return None

    def load_saves(self) -> None:
        # A restart reads the saves, so a player keeps the bag and the place.
        # The world is not in the save. Nobody wrote down why.
        for saved in self.save_store.load_all():
            sid, name, data = saved.sid, saved.name, saved.payload
            if data["location"] not in self.places:
                # The world changed under an old save.
                continue
            self.players[sid] = PlayerState(
                sid=sid,
                name=name,
                location=data["location"],
                bag=list(data["bag"]),
                gold=data["gold"],
                energy=data["energy"],
                moves=data["moves"],
                visited=set(data["visited"]),
                opened=set(data["opened"]),
                has_won=data["has_won"],
            )

    def now_iso(self) -> str:
        return self.clock.now().astimezone(timezone.utc).isoformat(timespec="seconds")

    def new_sid(self) -> str:
        while True:
            sid = (
                f"{self.random_source.digits(6)}-"
                f"{self.random_source.digits(12)}-"
                f"{self.random_source.digits(8)}"
            )
            if sid not in self.players and sid not in self.items:
                return sid

    def player(self, sid: str) -> PlayerState:
        if sid not in self.players:
            raise PlayerNotFound(f"PLAYER {sid} NOT FOUND.")
        return self.players[sid]

    def item(self, sid: str) -> Item:
        if sid not in self.items:
            raise ItemNotFound(f"ITEM {sid} NOT FOUND.")
        return self.items[sid]

    def visit(self, state: PlayerState, title: str) -> None:
        state.location = title
        if title not in state.visited:
            state.visited.add(title)
            state.gold += self.places[title].gold

    def connect(self, a: str, direction: Direction, b: str) -> None:
        self.places[a].exits[direction] = b
        self.places[b].exits[OPPOSITE[direction]] = a

    def disconnect(self, a: str, direction: Direction) -> None:
        b = self.places[a].exits.pop(direction)
        self.places[b].exits.pop(OPPOSITE[direction])

    def names_in_bag(self, state: PlayerState) -> list[str]:
        return [self.items[sid].name for sid in state.bag]

    def to_location(self, title: str, note: str = "") -> Location:
        place = self.places[title]
        return Location(
            title=place.title,
            description=f"{place.description} {note}".strip(),
            exits=list(place.exits),
            items=[self.items[sid] for sid in place.items],
            is_exit=place.is_exit,
        )

    def to_bag(self, state: PlayerState) -> Bag:
        return Bag(items=[self.items[sid] for sid in state.bag], gold=state.gold)

    def to_player(self, state: PlayerState) -> Player:
        return Player(
            sid=state.sid,
            name=state.name,
            location=self.to_location(state.location),
            bag=self.to_bag(state),
            has_won=state.has_won,
        )


class RegisterPlayerUseCase:
    def __init__(self, game: InMemoryGame) -> None:
        self.game = game

    def execute(self, name: str) -> Player:
        name = name.strip().upper()
        if not 1 <= len(name) <= NAME_MAX_LENGTH:
            raise InvalidName(f"THE NAME MUST HAVE 1 TO {NAME_MAX_LENGTH} CHARACTERS.")
        if name in RESERVED_NAMES:
            raise InvalidName("THIS NAME IS RESERVED.")
        if len(self.game.players) >= MAX_PLAYERS:
            raise NotAllowed("THE KATACOMBS ARE FULL. TRY AGAIN LATER.")
        state = PlayerState(sid=self.game.new_sid(), name=name, location=START)
        self.game.visit(state, START)
        self.game.players[state.sid] = state
        return self.game.to_player(state)


class ListPlayersUseCase:
    def __init__(self, game: InMemoryGame) -> None:
        self.game = game

    def execute(self) -> list[Player]:
        return [self.game.to_player(state) for state in self.game.players.values()]


class QuitGameUseCase:
    def __init__(self, game: InMemoryGame) -> None:
        self.game = game

    def execute(self, player_sid: str) -> None:
        state = self.game.player(player_sid)
        account = self.game.account_of(player_sid)
        if account is not None:
            account.snapshot = snapshot_of(state)
            self.game.account_store.put(account)
        self.game.places[state.location].items.extend(state.bag)
        del self.game.players[player_sid]


class InspectItemUseCase:
    def __init__(self, game: InMemoryGame) -> None:
        self.game = game

    def execute(self, item_sid: str) -> Item:
        return self.game.item(item_sid)


class InspectBagUseCase:
    def __init__(self, game: InMemoryGame) -> None:
        self.game = game

    def execute(self, player_sid: str) -> Bag:
        return self.game.to_bag(self.game.player(player_sid))


class LookAroundUseCase:
    def __init__(self, game: InMemoryGame) -> None:
        self.game = game

    def execute(self, player_sid: str) -> Location:
        return self.game.to_location(self.game.player(player_sid).location)


class LookInDirectionUseCase:
    def __init__(self, game: InMemoryGame) -> None:
        self.game = game

    def execute(self, player_sid: str, direction: Direction) -> Location:
        state = self.game.player(player_sid)
        exits = self.game.places[state.location].exits
        if direction not in exits:
            raise NotAllowed("THERE IS NOTHING IN THAT DIRECTION.")
        return self.game.to_location(exits[direction])


class MoveUseCase:
    def __init__(self, game: InMemoryGame) -> None:
        self.game = game

    def execute(self, player_sid: str, direction: Direction) -> Location:
        game = self.game
        state = game.player(player_sid)
        if state.has_won:
            raise NotAllowed("THE GAME IS OVER. YOU ALREADY FOUND THE EXIT.")
        exits = game.places[state.location].exits
        if direction not in exits:
            raise NotAllowed("YOU CAN'T GO THAT WAY.")
        target = exits[direction]
        if target == MARKET and market_is_cleaning(game.clock):
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
            game.high_scores.append(state.name, score, game.clock.now())
            game.finished_games.append(
                {"name": state.name, "score": score, "moves": state.moves}
            )
        return game.to_location(state.location, note)

    def rat(self, state: PlayerState) -> str:
        cheap = [sid for sid in state.bag if not self.game.items[sid].value]
        if not cheap or self.game.random_source.chance() >= RAT_CHANCE:
            return ""
        stolen = self.game.random_source.choice(cheap)
        state.bag.remove(stolen)
        self.game.places[TUBE_TUNNEL].items.append(stolen)
        return f"A RAT RUNS OFF WITH YOUR {self.game.items[stolen].name}."


class UseItemUseCase:
    def __init__(self, game: InMemoryGame) -> None:
        self.game = game

    def execute(self, player_sid: str, item_sid: str, action: Action) -> str:
        game = self.game
        state = game.player(player_sid)
        item = game.item(item_sid)
        if state.has_won:
            raise NotAllowed("THE GAME IS OVER. YOU ALREADY FOUND THE EXIT.")

        here = game.places[state.location]
        in_bag = item_sid in state.bag
        if not in_bag and item_sid not in here.items:
            raise ItemNotFound(f"THERE IS NO {item.name} HERE.")
        if action not in item.actions:
            raise NotAllowed(f"YOU CAN'T {action.value.upper()} THE {item.name}.")

        state.moves += 1

        if action == Action.PICK:
            if in_bag:
                # Do not remove. INC-2231: the mobile client sends TAKE again
                # when the network is slow, and players saw an error.
                return "TAKEN."
            if slots_used(game.names_in_bag(state) + [item.name]) > BAG_SLOTS:
                raise NotAllowed("YOUR BAG IS FULL.")
            here.items.remove(item_sid)
            state.bag.append(item_sid)
            return "TAKEN."

        if action == Action.DROP:
            if not in_bag:
                raise NotAllowed(f"YOU ARE NOT CARRYING THE {item.name}.")
            state.bag.remove(item_sid)
            here.items.append(item_sid)
            return "DROPPED."

        if action == Action.OPEN:
            if item_sid in game.open_items:
                raise NotAllowed(f"THE {item.name} IS ALREADY OPEN.")
            if item_sid in game.locked_items:
                raise NotAllowed(f"THE {item.name} IS LOCKED.")
            game.open_items.add(item_sid)
            if item_sid == MANHOLE:
                game.connect(BACK_YARD, Direction.DOWN, KATACOMBS)
            message = "OPENED."
            if item_sid not in state.opened:
                state.opened.add(item_sid)
                gold = game.gold_inside.get(item_sid, 0)
                if gold:
                    state.gold += gold
                    message += f" YOU FIND {gold} GOLD."
            return message

        if action == Action.CLOSE:
            if item_sid not in game.open_items:
                raise NotAllowed(f"THE {item.name} IS ALREADY CLOSED.")
            game.open_items.remove(item_sid)
            if item_sid == MANHOLE:
                game.disconnect(BACK_YARD, Direction.DOWN)
            return "CLOSED."

        # Action.USE
        if not in_bag:
            raise NotAllowed(f"YOU ARE NOT CARRYING THE {item.name}.")
        if item_sid == KEY and state.location == BACK_YARD:
            if MANHOLE not in game.locked_items:
                return "THE MANHOLE COVER IS ALREADY UNLOCKED."
            game.locked_items.remove(MANHOLE)
            return "YOU UNLOCK THE MANHOLE COVER."
        if item.name in ENERGY_FROM:
            state.bag.remove(item_sid)
            state.energy = min(MAX_ENERGY, state.energy + ENERGY_FROM[item.name])
            if item.name == "BEER":
                return "YOU DRINK THE BEER. YOU FEEL BRAVE."
            return "YOU EAT THE BREAD. YOU FEEL STRONGER."
        return "NOTHING HAPPENS."


class SaveGameUseCase:
    """The SaveGame port. INC-3110: a laptop sleep lost every bag."""

    def __init__(self, game: InMemoryGame) -> None:
        self.game = game

    def execute(self, player_sid: str) -> str:
        state = self.game.player(player_sid)
        # 2023: the payload also holds the energy and the move count.
        saved = SavedPlayer(state.sid, state.name, snapshot_of(state))
        return self.game.save_store.save(saved, self.game.clock.now())


class RegisterAccountUseCase:
    def __init__(self, game: InMemoryGame) -> None:
        self.game = game

    def execute(self, email: str, password: str, name: str) -> Account:
        if "@" not in email:
            raise InvalidName("THE EMAIL IS NOT VALID.")
        if email in self.game.accounts:
            raise NotAllowed("THIS EMAIL IS TAKEN.")
        name = name.strip().upper()
        if not 1 <= len(name) <= NAME_MAX_LENGTH:
            raise InvalidName(f"THE NAME MUST HAVE 1 TO {NAME_MAX_LENGTH} CHARACTERS.")
        if name in RESERVED_NAMES:
            raise InvalidName("THIS NAME IS RESERVED.")
        account = Account(email=email, password_hash=password_hash(password), name=name)
        self.game.accounts[email] = account
        self.game.account_store.put(account)
        return account


class LoginUseCase:
    def __init__(self, game: InMemoryGame) -> None:
        self.game = game

    def execute(self, email: str, password: str) -> Player:
        game = self.game
        account = game.accounts.get(email)
        if account is None or account.password_hash != password_hash(password):
            raise NotAllowed("WRONG EMAIL OR PASSWORD.")
        data = account.snapshot
        if data and data["location"] in game.places:
            # Restore the profile.
            sid = account.player_sid or game.new_sid()
            if sid not in game.players and len(game.players) >= MAX_PLAYERS:
                raise NotAllowed("THE KATACOMBS ARE FULL. TRY AGAIN LATER.")
            state = PlayerState(
                sid=sid,
                name=account.name,
                location=data["location"],
                bag=list(data["bag"]),
                gold=data["gold"],
                energy=data["energy"],
                moves=data["moves"],
                visited=set(data["visited"]),
                opened=set(data["opened"]),
                has_won=data["has_won"],
            )
            game.players[sid] = state
        elif account.player_sid in game.players:
            state = game.players[account.player_sid]
        else:
            player = RegisterPlayerUseCase(game).execute(account.name)
            state = game.players[player.sid]
        account.player_sid = state.sid
        self.game.account_store.put(account)
        return game.to_player(state)
