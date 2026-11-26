"""The errors of the game: each one has an error reason (API-2)."""


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
