"""The game: the world, the players, the chat and the finished games, behind the driven ports."""

from ..kata import Bag, Direction, Item, Location, Player
from .errors import ItemNotFound, PlayerNotFound
from .ports import AccountStore, Clock, HighScoreSink, Random, SaveStore
from .state import Account, ChatMessage, PlayerState, from_payload
from .world import OPPOSITE, load_world


class Game:
    """The state of one game, and the driven ports it reads and writes through (ENTRY-6, ENTRY-7)."""

    def __init__(
        self,
        saves: SaveStore,
        accounts: AccountStore,
        highscores: HighScoreSink,
        clock: Clock,
        rng: Random,
        world: dict | None = None,
    ) -> None:
        self.save_store = saves
        self.account_store = accounts
        self.highscores = highscores
        self.clock = clock
        self.rng = rng
        self.world = load_world(world)
        self.places = self.world.places
        self.items = self.world.items
        self.gold_inside = self.world.gold_inside
        self.open_items: set[str] = set()
        self.locked_items: set[str] = set(self.world.locked)
        self.players: dict[str, PlayerState] = {}
        self.finished_games: list[dict] = []
        self.accounts: dict[str, Account] = {}
        self.chat: list[ChatMessage] = []
        self.load_saves()
        self.load_accounts()

    def load_accounts(self) -> None:
        for account in self.account_store.load_accounts():
            self.accounts[account.email] = account

    def account_of(self, player_sid: str) -> Account | None:
        for account in self.accounts.values():
            if account.player_sid == player_sid:
                return account
        return None

    def load_saves(self) -> None:
        # A restart reads the saves, so a player keeps the bag and the place.
        # The world is not in the save. Nobody wrote down why.
        for sid, name, data in self.save_store.load_saves():
            if data["location"] not in self.places:
                # The world changed under an old save.
                continue
            self.players[sid] = from_payload(sid, name, data)

    def new_sid(self) -> str:
        while True:
            sid = (
                f"{self.rng.randint(0, 999999):06d}-"
                f"{self.rng.randint(0, 999999999999):012d}-"
                f"{self.rng.randint(0, 99999999):08d}"
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
        return Bag(items=[self.items[sid] for sid in state.bag], gold=state.gold, energy=state.energy)

    def to_player(self, state: PlayerState) -> Player:
        return Player(
            sid=state.sid,
            name=state.name,
            location=self.to_location(state.location),
            bag=self.to_bag(state),
            has_won=state.has_won,
        )
