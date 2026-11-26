"""The name rules, for players and for accounts (PLAYER-2..4, ACCOUNT-2)."""

from .constants import NAME_MAX_LENGTH, RESERVED_NAMES
from .errors import InvalidName


def player_name(name: str) -> str:
    """The name as the game keeps it: trimmed, upper case, 1 to 50, not reserved."""
    name = name.strip().upper()
    if not 1 <= len(name) <= NAME_MAX_LENGTH:
        raise InvalidName(f"THE NAME MUST HAVE 1 TO {NAME_MAX_LENGTH} CHARACTERS.")
    if name in RESERVED_NAMES:
        raise InvalidName("THIS NAME IS RESERVED.")
    return name


def check_email(email: str) -> None:
    if "@" not in email:
        raise InvalidName("THE EMAIL IS NOT VALID.")
