"""Accounts: register and log in (ACCOUNT-*, STORE-3)."""

import hashlib

from ..kata import Player
from .errors import InvalidName, NotAllowed
from .game import Game
from .players import MAX_PLAYERS, NAME_MAX_LENGTH, RESERVED_NAMES, RegisterPlayerUseCase
from .state import Account, from_payload


def password_hash(password: str) -> str:
    # TODO: bcrypt (2023)
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


class RegisterAccountUseCase:
    def __init__(self, game: Game) -> None:
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
    def __init__(self, game: Game) -> None:
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
