"""The numbers of the game, and the small rules that use them."""

import math
from collections import Counter

from .ports import Clock

BAG_SLOTS = 8
ITEMS_PER_SLOT = 3
NAME_MAX_LENGTH = 50
MAX_PLAYERS = 20
RESERVED_NAMES = {"ADMIN"}
START_ENERGY = 12
MAX_ENERGY = 20
RAT_CHANCE = 0.2

ENERGY_FROM = {"BREAD": 5, "BEER": 3}


def market_is_cleaning(clock: Clock) -> bool:
    # Cleaning crew contract (2023): the market is closed from minute 50 to
    # minute 59 of each hour. Ask facilities before you change this.
    # The local wall clock, not UTC (decision 0001).
    return clock.local_now().minute >= 50


def slots_used(names: list[str]) -> int:
    return sum(math.ceil(count / ITEMS_PER_SLOT) for count in Counter(names).values())


def utc_stamp(clock: Clock) -> str:
    """The time stamp of a save, an account action, a chat line or a high score."""
    return clock.utc_now().isoformat(timespec="seconds")
