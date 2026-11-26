"""In-memory implementation of the Katacombs use cases."""

import hashlib
import math
from collections import Counter
from datetime import datetime, timezone

from . import kata
from .adapters.highscores import JsonlHighScores
from .adapters.sqlite_store import SqliteStore
from .adapters.system import local_now, stdlib
from .core.ports import AccountStore, Clock, HighScoreSink, Random, SaveStore
from .core.world import OPPOSITE, Place, load_world
from .core.state import START_ENERGY, Account, ChatMessage, PlayerState, from_payload, to_payload
from .kata import Action, Bag, Direction, FinishedGame, Item, Location, Player

BAG_SLOTS = 8
ITEMS_PER_SLOT = 3
NAME_MAX_LENGTH = 50
MAX_PLAYERS = 20
RESERVED_NAMES = {"ADMIN"}
MAX_ENERGY = 20
RAT_CHANCE = 0.2

# The locations that the market hours (MOVE-6) and the rat (MOVE-8) name.
MARKET = "SPITALFIELDS MARKET"
CELLAR = "BREWERY CELLAR"
TUBE_TUNNEL = "OLD TUBE TUNNEL"
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


def market_is_cleaning(now: datetime) -> bool:
    # Cleaning crew contract (2023): the market is closed from minute 50 to
    # minute 59 of each hour. Ask facilities before you change this.
    return now.minute >= 50


def slots_used(names: list[str]) -> int:
    return sum(math.ceil(count / ITEMS_PER_SLOT) for count in Counter(names).values())


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def password_hash(password: str) -> str:
    # TODO: bcrypt (2023)
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


class InMemoryGame:
    def __init__(
        self,
        saves: SaveStore | None = None,
        accounts: AccountStore | None = None,
        highscores: HighScoreSink | None = None,
        clock: Clock | None = None,
        rng: Random | None = None,
        world: dict | None = None,
    ) -> None:
        store = SqliteStore()
        self.save_store = saves or store
        self.account_store = accounts or store
        self.highscores = highscores or JsonlHighScores()
        self.clock = clock or local_now
        self.rng = rng or stdlib
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
        start = self.game.world.start
        state = PlayerState(sid=self.game.new_sid(), name=name, location=start)
        self.game.visit(state, start)
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
            account.snapshot = to_payload(state)
            self.game.account_store.write_account(account)
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
        # Added for the mobile release: a tired player cannot move (decision 0011).
        if state.energy <= 0:
            raise NotAllowed("YOU ARE TOO TIRED TO MOVE. EAT OR DRINK SOMETHING.")
        if state.has_won:
            raise NotAllowed("THE GAME IS OVER. YOU ALREADY FOUND THE EXIT.")
        exits = game.places[state.location].exits
        if direction not in exits:
            raise NotAllowed("YOU CAN'T GO THAT WAY.")
        target = exits[direction]
        if target == MARKET and market_is_cleaning(game.clock()):
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
            game.highscores.append(state.name, score)
            game.finished_games.append(
                {"name": state.name, "score": score, "moves": state.moves}
            )
        return game.to_location(state.location, note)

    def rat(self, state: PlayerState) -> str:
        cheap = [sid for sid in state.bag if not self.game.items[sid].value]
        if not cheap or self.game.rng.random() >= RAT_CHANCE:
            return ""
        stolen = self.game.rng.choice(cheap)
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
            if item_sid in game.world.opened_exits:
                game.connect(*game.world.opened_exits[item_sid])
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
            if item_sid in game.world.opened_exits:
                game.disconnect(*game.world.opened_exits[item_sid][:2])
            return "CLOSED."

        # Action.USE
        if not in_bag:
            raise NotAllowed(f"YOU ARE NOT CARRYING THE {item.name}.")
        use = game.world.uses.get(item_sid, {})
        if "unlocks" in use and state.location == use["where"]:
            if use["unlocks"] not in game.locked_items:
                return use["alreadyMessage"]
            game.locked_items.remove(use["unlocks"])
            return use["message"]
        if "energy" in use:
            state.bag.remove(item_sid)
            state.energy = min(MAX_ENERGY, state.energy + use["energy"])
            return use["message"]
        return "NOTHING HAPPENS."


class LegacyPickupUseCase:
    """Mobile client v1 still calls this route. Do not remove it (decision 0003)."""

    def __init__(self, game: InMemoryGame) -> None:
        self.game = game

    def execute(self, player_sid: str, item_sid: str) -> str:
        state = self.game.player(player_sid)
        self.game.item(item_sid)
        here = self.game.places[state.location]
        if item_sid in here.items:
            here.items.remove(item_sid)
            state.bag.append(item_sid)
        return "OK"


class SendMessageUseCase:
    def __init__(self, game: InMemoryGame) -> None:
        self.game = game

    def execute(self, player_sid: str, text: str) -> str:
        state = self.game.player(player_sid)
        self.game.chat.append(
            ChatMessage(location=state.location, name=state.name, text=text, at=now_iso())
        )
        state.moves += 1
        return "SENT."


class ReadMessagesUseCase:
    def __init__(self, game: InMemoryGame) -> None:
        self.game = game

    def execute(self, player_sid: str) -> list[kata.ChatMessage]:
        state = self.game.player(player_sid)
        return [
            kata.ChatMessage(name=message.name, text=message.text, at=message.at)
            for message in self.game.chat
            if message.location == state.location
        ]


class LeaderboardUseCase:
    def __init__(self, game: InMemoryGame) -> None:
        self.game = game

    def execute(self) -> list[FinishedGame]:
        ranked = sorted(self.game.finished_games, key=lambda entry: -entry["score"])
        return [FinishedGame(**entry) for entry in ranked]


class SaveGameUseCase:
    """The SaveGame port. INC-3110: a laptop sleep lost every bag."""

    def __init__(self, game: InMemoryGame) -> None:
        self.game = game

    def execute(self, player_sid: str) -> str:
        state = self.game.player(player_sid)
        # 2023: the payload also holds the energy and the move count.
        return self.game.save_store.write_save(state.sid, state.name, to_payload(state))


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
        self.game.account_store.write_account(account)
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
            state = from_payload(sid, account.name, data)
            game.players[sid] = state
        elif account.player_sid in game.players:
            state = game.players[account.player_sid]
        else:
            player = RegisterPlayerUseCase(game).execute(account.name)
            state = game.players[player.sid]
        account.player_sid = state.sid
        game.account_store.write_account(account)
        return game.to_player(state)
