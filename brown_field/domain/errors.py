"""The errors of the game. Each one has one HTTP status (API-2)."""


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
