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
        if "@" not in email:
            raise InvalidName("THE EMAIL IS NOT VALID.")
        if email in self.game.accounts:
            raise NotAllowed("THIS EMAIL IS TAKEN.")
        name = name.strip().upper()
        if not 1 <= len(name) <= NAME_MAX_LENGTH:
            raise InvalidName(f"THE NAME MUST HAVE 1 TO {NAME_MAX_LENGTH} CHARACTERS.")
        if name in RESERVED_NAMES:
            raise InvalidName("THIS NAME IS RESERVED.")
        account = Account(email=email, password_hash=self.game.ports.hasher.hash(password), name=name)
        self.game.accounts[email] = account
        self.game.ports.accounts.write(account)
        return AccountView(email=account.email, name=account.name)


class LoginUseCase:
    def __init__(self, game: GameState) -> None:
        self.game = game

    def execute(self, email: str, password: str) -> Player:
        game = self.game
        account = game.accounts.get(email)
        if account is None or account.password_hash != game.ports.hasher.hash(password):
            raise NotAllowed("WRONG EMAIL OR PASSWORD.")
        data = account.snapshot
        if data and data["location"] in game.places:
            # Restore the profile.
            sid = account.player_sid or game.new_sid()
            if sid not in game.players and len(game.players) >= MAX_PLAYERS:
                raise NotAllowed("THE KATACOMBS ARE FULL. TRY AGAIN LATER.")
            state = player_from(sid, account.name, data)
            game.players[sid] = state
        elif account.player_sid in game.players:
            state = game.players[account.player_sid]
        else:
            player = RegisterPlayerUseCase(game).execute(account.name)
            state = game.players[player.sid]
        account.player_sid = state.sid
        game.ports.accounts.write(account)
        return game.to_player(state)
