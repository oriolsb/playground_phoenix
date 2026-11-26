"""The standard `random` module, the default `RandomSource` (decision 0013)."""

import random
from collections.abc import Sequence
from typing import TypeVar

T = TypeVar("T")


class StdRandom:
    # Each call goes through the module at the moment of the call, never a
    # function bound at import: a test patches `random.random` to force or
    # stop the rat (decision 0008, kept by 0013).

    def chance(self) -> float:
        return random.random()

    def choice(self, items: Sequence[T]) -> T:
        return random.choice(items)

    def digits(self, count: int) -> str:
        return f"{random.randint(0, 10**count - 1):0{count}d}"
