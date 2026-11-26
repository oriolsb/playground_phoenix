"""The bag limit (BAG-3). The score is `kata.Bag.score` (BAG-2)."""

import math
from collections import Counter

from .constants import BAG_SLOTS, ITEMS_PER_SLOT


def slots_used(names: list[str]) -> int:
    return sum(math.ceil(count / ITEMS_PER_SLOT) for count in Counter(names).values())


def has_room(names: list[str], name: str) -> bool:
    """Whether a bag that holds `names` can take one more item called `name`."""
    return slots_used(names + [name]) <= BAG_SLOTS
