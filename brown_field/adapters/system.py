"""The clock, the random numbers and the password hash of the real system.

They call the standard library at each call, so the seams of decision 0008
still hold: time-machine moves `datetime.now()`, and a test can patch
`random.random`.
"""

import hashlib
import random
from datetime import datetime, timezone
from typing import Sequence, TypeVar

T = TypeVar("T")


class SystemClock:
    def local_now(self) -> datetime:
        return datetime.now()

    def utc_now(self) -> datetime:
        return datetime.now(timezone.utc)


class StdlibRandom:
    def random(self) -> float:
        return random.random()

    def choice(self, options: Sequence[T]) -> T:
        return random.choice(options)

    def randint(self, low: int, high: int) -> int:
        return random.randint(low, high)


class Sha256PasswordHasher:
    def hash(self, password: str) -> str:
        # TODO: bcrypt (2023). Unsalted: a known scar, kept until a decision changes it.
        return hashlib.sha256(password.encode("utf-8")).hexdigest()
