"""Joining, listing, finding and quitting players, and the leaderboard."""

from ..kata import Player, Score
from .errors import InvalidName, NotAllowed
from .rules import MAX_PLAYERS, NAME_MAX_LENGTH, RESERVED_NAMES
from .state import GameState, PlayerState, snapshot_of
from .world import START


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
        state = PlayerState(sid=self.game.new_sid(), name=name, location=START)
        self.game.visit(state, START)
        self.game.players[state.sid] = state
        return self.game.to_player(state)


class ListPlayersUseCase:
    def __init__(self, game: GameState) -> None:
        self.game = game

    def execute(self) -> list[Player]:
        return [self.game.to_player(state) for state in self.game.players.values()]


class ViewPlayerUseCase:
    def __init__(self, game: GameState) -> None:
        self.game = game

    def execute(self, player_sid: str) -> Player:
        return self.game.to_player(self.game.player(player_sid))


class QuitGameUseCase:
    def __init__(self, game: GameState) -> None:
        self.game = game

    def execute(self, player_sid: str) -> None:
        state = self.game.player(player_sid)
        account = self.game.account_of(player_sid)
        if account is not None:
            account.snapshot = snapshot_of(state)
            self.game.ports.accounts.write(account)
        self.game.places[state.location].items.extend(state.bag)
        del self.game.players[player_sid]


class ShowLeaderboardUseCase:
    """Finished games of this run, best score first. A restart empties it."""

    def __init__(self, game: GameState) -> None:
        self.game = game

    def execute(self) -> list[Score]:
        ranked = sorted(self.game.finished_games, key=lambda entry: -entry.score)
        return [Score(name=entry.name, score=entry.score, moves=entry.moves) for entry in ranked]
