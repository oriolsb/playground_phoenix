"""The errors that the use cases raise. The REST adapter maps each one to a status."""


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
