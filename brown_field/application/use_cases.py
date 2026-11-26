"""The use cases: one class per inbound port of `kata.py` (decision 0012).

Each one takes the game as its only argument (decision 0008) and reaches the
outside only through the ports that the game holds.
"""

from ..domain.constants import (
    BACK_YARD,
    BAG_SLOTS,
    CELLAR,
    ENERGY_FROM,
    KATACOMBS,
    KEY,
    MANHOLE,
    MARKET,
    MAX_ENERGY,
    MAX_PLAYERS,
    NAME_MAX_LENGTH,
    RAT_CHANCE,
    RESERVED_NAMES,
    TUBE_TUNNEL,
)
from ..domain.errors import InvalidName, ItemNotFound, NotAllowed
from ..kata import AccountView, Action, Bag, ChatLine, Direction, FinishedGame, Item, Location, Player
from .ports_out import SavedPlayer
from .state import (
    Account,
    GameState,
    PlayerState,
    ChatMessage,
    market_is_cleaning,
    password_hash,
    slots_used,
    snapshot_of,
)


class RegisterPlayerUseCase:
    def __init__(self, game: GameState) -> None:
        self.game = game

    def execute(self, name: str) -> Player:
        name = name.strip().upper()
        if not 1 <= len(name) <= NAME_MAX_LENGTH:
            raise InvalidName(f"THE NAME MUST HAVE 1 TO {NAME_MAX_LENGTH} CHARACTERS.")
        if name in RESERVED_NAMES:
            raise InvalidName("THIS NAME IS RESERVED.")
        if len(self.game.players) >= MAX_PLAYERS:
            raise NotAllowed("THE KATACOMBS ARE FULL. TRY AGAIN LATER.")
        state = PlayerState(sid=self.game.new_sid(), name=name, location=self.game.start)
        self.game.visit(state, self.game.start)
        self.game.players[state.sid] = state
        return self.game.to_player(state)


class ListPlayersUseCase:
    def __init__(self, game: GameState) -> None:
        self.game = game

    def execute(self) -> list[Player]:
        return [self.game.to_player(state) for state in self.game.players.values()]


class QuitGameUseCase:
    def __init__(self, game: GameState) -> None:
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
    def __init__(self, game: GameState) -> None:
        self.game = game

    def execute(self, item_sid: str) -> Item:
        return self.game.item(item_sid)


class InspectBagUseCase:
    def __init__(self, game: GameState) -> None:
        self.game = game

    def execute(self, player_sid: str) -> Bag:
        return self.game.to_bag(self.game.player(player_sid))


class LookAroundUseCase:
    def __init__(self, game: GameState) -> None:
        self.game = game

    def execute(self, player_sid: str) -> Location:
        return self.game.to_location(self.game.player(player_sid).location)


class LookInDirectionUseCase:
    def __init__(self, game: GameState) -> None:
        self.game = game

    def execute(self, player_sid: str, direction: Direction) -> Location:
        state = self.game.player(player_sid)
        exits = self.game.places[state.location].exits
        if direction not in exits:
            raise NotAllowed("THERE IS NOTHING IN THAT DIRECTION.")
        return self.game.to_location(exits[direction])


class MoveUseCase:
    def __init__(self, game: GameState) -> None:
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
    def __init__(self, game: GameState) -> None:
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

    def __init__(self, game: GameState) -> None:
        self.game = game

    def execute(self, player_sid: str) -> str:
        state = self.game.player(player_sid)
        # 2023: the payload also holds the energy and the move count.
        saved = SavedPlayer(state.sid, state.name, snapshot_of(state))
        return self.game.save_store.save(saved, self.game.clock.now())


class RegisterAccountUseCase:
    def __init__(self, game: GameState) -> None:
        self.game = game

    def execute(self, email: str, password: str, name: str) -> AccountView:
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
        # The digest of the password does not cross the port (decision 0015).
        return AccountView(email=account.email, name=account.name)


class LoginUseCase:
    def __init__(self, game: GameState) -> None:
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


class SendMessageUseCase:
    """The SendMessage port (CHAT-1, CHAT-3). It was a route before decision 0015."""

    def __init__(self, game: GameState) -> None:
        self.game = game

    def execute(self, player_sid: str, text: str) -> str:
        state = self.game.player(player_sid)
        self.game.chat.append(
            ChatMessage(location=state.location, name=state.name, text=text, at=self.game.now_iso())
        )
        state.moves += 1
        return "SENT."


class ReadMessagesUseCase:
    """The ReadMessages port (CHAT-2)."""

    def __init__(self, game: GameState) -> None:
        self.game = game

    def execute(self, player_sid: str) -> list[ChatLine]:
        state = self.game.player(player_sid)
        return [
            ChatLine(name=message.name, text=message.text, at=message.at)
            for message in self.game.chat
            if message.location == state.location
        ]


class ShowLeaderboardUseCase:
    """The ShowLeaderboard port (BOARD-1, WIN-2)."""

    def __init__(self, game: GameState) -> None:
        self.game = game

    def execute(self) -> list[FinishedGame]:
        ranked = sorted(self.game.finished_games, key=lambda entry: -entry["score"])
        return [FinishedGame(**entry) for entry in ranked]


class LegacyPickupUseCase:
    """The LegacyPickup port (LEGACY-1, LEGACY-2, decision 0003).

    Mobile client v1 still calls this route. Do not remove it. It skips the
    bag limit, the win check and the move count on purpose.
    """

    def __init__(self, game: GameState) -> None:
        self.game = game

    def execute(self, player_sid: str, item_sid: str) -> str:
        game = self.game
        state = game.player(player_sid)
        game.item(item_sid)
        here = game.places[state.location]
        if item_sid in here.items:
            here.items.remove(item_sid)
            state.bag.append(item_sid)
        return "OK"
