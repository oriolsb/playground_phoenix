"""The stdlib clock and chance: the seams of decision 0008 (time-machine, random.random)."""

import random as stdlib_random
from datetime import datetime


def local_now() -> datetime:
    return datetime.now()


# The module itself: a test that patches random.random reaches every call.
stdlib = stdlib_random
