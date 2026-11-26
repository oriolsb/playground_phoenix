"""Accounts: register, and log in to restore the profile of the last quit."""

from ..kata import AccountView, Player
from .errors import InvalidName, NotAllowed
from .players import RegisterPlayerUseCase
from .rules import MAX_PLAYERS, NAME_MAX_LENGTH, RESERVED_NAMES
from .state import Account, GameState, player_from


class RegisterAccountUseCase:
    def __init__(self, game: GameState) -> None:
        self.game = game

    def execute(self, email: str, password: str, name: str) -> AccountView:
        # Removed by hand for the regeneration of change accounts (decision 0013).
        raise NotImplementedError("RegisterAccountUseCase: regenerate from the specification")


class LoginUseCase:
    def __init__(self, game: GameState) -> None:
        self.game = game

    def execute(self, email: str, password: str) -> Player:
        # Removed by hand for the regeneration of change accounts (decision 0013).
        raise NotImplementedError("LoginUseCase: regenerate from the specification")
