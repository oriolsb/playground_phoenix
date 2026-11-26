"""One player, with the rules that change it (decision 0017).

MOVE-2, MOVE-3, MOVE-7, GOLD-1, GOLD-2, ACT-3..7, ACT-15, ACT-17, MOVE-8.
"""

from collections.abc import Callable
from dataclasses import dataclass, field

from .types import Item
from .bag import has_room
from .constants import ENERGY_FROM, MAX_ENERGY, RAT_CHANCE, START_ENERGY
from .errors import NotAllowed
from .world import Place

GAME_OVER = "THE GAME IS OVER. YOU ALREADY FOUND THE EXIT."


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

    def ensure_rested(self) -> None:
        """MOVE-5: a player with no energy can't move (decision 0011, the port, at 0).

        Added for the mobile release. It comes before every other move check.
        """
        if self.energy <= 0:
            raise NotAllowed("YOU ARE TOO TIRED TO MOVE. EAT OR DRINK SOMETHING.")

    def ensure_playing(self) -> None:
        """MOVE-7, ACT-3: after a win, a player can't move or act on items."""
        if self.has_won:
            raise NotAllowed(GAME_OVER)

    def visit(self, place: Place) -> None:
        """GOLD-1: the first visit to a location adds its gold."""
        self.location = place.title
        if place.title not in self.visited:
            self.visited.add(place.title)
            self.gold += place.gold

    def walk_to(self, place: Place) -> None:
        """MOVE-2, MOVE-3: a move costs 1 energy and adds one to the move count."""
        self.energy -= 1
        self.moves += 1
        self.visit(place)

    def count_command(self) -> None:
        """ACT-17, CHAT-3: an item action or a chat message adds one move."""
        self.moves += 1

    def take(self, item: Item, here: Place, names_in_bag: list[str]) -> str:
        """ACT-4, ACT-5, BAG-3."""
        if item.sid in self.bag:
            # Do not remove. INC-2231: the mobile client sends TAKE again
            # when the network is slow, and players saw an error.
            return "TAKEN."
        if not has_room(names_in_bag, item.name):
            raise NotAllowed("YOUR BAG IS FULL.")
        here.items.remove(item.sid)
        self.bag.append(item.sid)
        return "TAKEN."

    def drop(self, item: Item, here: Place) -> str:
        """ACT-6, ACT-7."""
        self.ensure_carrying(item)
        self.bag.remove(item.sid)
        here.items.append(item.sid)
        return "DROPPED."

    def ensure_carrying(self, item: Item) -> None:
        """ACT-7: a player can only drop or use an item in the bag."""
        if item.sid not in self.bag:
            raise NotAllowed(f"YOU ARE NOT CARRYING THE {item.name}.")

    def first_open(self, item_sid: str, gold_inside: int) -> int:
        """GOLD-2: the first opening of an item with gold adds its gold, once per player."""
        if item_sid in self.opened:
            return 0
        self.opened.add(item_sid)
        self.gold += gold_inside
        return gold_inside

    def eat_or_drink(self, item: Item) -> str | None:
        """ACT-15: bread and beer restore energy, up to 20, and are used up."""
        if item.name not in ENERGY_FROM:
            return None
        self.bag.remove(item.sid)
        self.energy = min(MAX_ENERGY, self.energy + ENERGY_FROM[item.name])
        if item.name == "BEER":
            return "YOU DRINK THE BEER. YOU FEEL BRAVE."
        return "YOU EAT THE BREAD. YOU FEEL STRONGER."

    def lose_to_the_rat(
        self,
        items: dict[str, Item],
        chance: Callable[[], float],
        choose: Callable[[list[str]], str],
    ) -> str | None:
        """MOVE-8: a rat can steal an item without value, with a chance of 1 in 5.

        `chance` is drawn only when the bag holds such an item, as before.
        """
        cheap = [sid for sid in self.bag if not items[sid].value]
        if not cheap or chance() >= RAT_CHANCE:
            return None
        stolen = choose(cheap)
        self.bag.remove(stolen)
        return stolen

    def win(self) -> None:
        """WIN-1."""
        self.has_won = True
