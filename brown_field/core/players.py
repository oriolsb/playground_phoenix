"""Players: register, list, quit (PLAYER-*)."""

from ..kata import Player
from .errors import InvalidName, NotAllowed
from .game import Game
from .state import PlayerState, to_payload


NAME_MAX_LENGTH = 50
MAX_PLAYERS = 20
RESERVED_NAMES = {"ADMIN"}


class RegisterPlayerUseCase:
    def __init__(self, game: Game) -> None:
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
    def __init__(self, game: Game) -> None:
        self.game = game

    def execute(self) -> list[Player]:
        return [self.game.to_player(state) for state in self.game.players.values()]


class QuitGameUseCase:
    def __init__(self, game: Game) -> None:
        self.game = game

    def execute(self, player_sid: str) -> None:
        state = self.game.player(player_sid)
        account = self.game.account_of(player_sid)
        if account is not None:
            account.snapshot = to_payload(state)
            self.game.account_store.write_account(account)
        self.game.places[state.location].items.extend(state.bag)
        del self.game.players[player_sid]
