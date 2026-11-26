"""The state that a game keeps per player and per account, and the one codec of the player state."""

from dataclasses import dataclass, field

START_ENERGY = 12


@dataclass
class PlayerState:
    sid: str
    name: str
    location: str
    bag: list[str] = field(default_factory=list)
    gold: int = 0
    energy: int = START_ENERGY
    moves: int = 0
    visited: set[str] = field(default_factory=set)
    opened: set[str] = field(default_factory=set)
    has_won: bool = False


@dataclass
class Account:
    email: str
    password_hash: str
    name: str
    player_sid: str | None = None
    snapshot: dict | None = None


@dataclass
class ChatMessage:
    location: str
    name: str
    text: str
    at: str


def to_payload(state: PlayerState) -> dict:
    """The payload of a save and of a snapshot (player-state.schema.json)."""
    return {
        "location": state.location,
        "bag": list(state.bag),
        "gold": state.gold,
        "energy": state.energy,
        "moves": state.moves,
        "visited": sorted(state.visited),
        "opened": sorted(state.opened),
        "has_won": state.has_won,
    }


def from_payload(sid: str, name: str, data: dict) -> PlayerState:
    # A payload from before 2023 has no energy: the KeyError is pinned (SAVE-2, contested).
    return PlayerState(
        sid=sid,
        name=name,
        location=data["location"],
        bag=list(data["bag"]),
        gold=data["gold"],
        energy=data["energy"],
        moves=data["moves"],
        visited=set(data["visited"]),
        opened=set(data["opened"]),
        has_won=data["has_won"],
    )
