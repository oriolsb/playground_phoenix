"""Items: inspect, the bag, the item actions and their effects, the legacy pickup (ITEM-*, BAG-*, ACT-*, LEGACY-*)."""

import math
from collections import Counter

from ..kata import Action, Bag, Item
from .errors import ItemNotFound, NotAllowed
from .game import Game


BAG_SLOTS = 8
ITEMS_PER_SLOT = 3
MAX_ENERGY = 20


def slots_used(names: list[str]) -> int:
    return sum(math.ceil(count / ITEMS_PER_SLOT) for count in Counter(names).values())


class InspectItemUseCase:
    def __init__(self, game: Game) -> None:
        self.game = game

    def execute(self, item_sid: str) -> Item:
        return self.game.item(item_sid)


class InspectBagUseCase:
    def __init__(self, game: Game) -> None:
        self.game = game

    def execute(self, player_sid: str) -> Bag:
        return self.game.to_bag(self.game.player(player_sid))


class UseItemUseCase:
    def __init__(self, game: Game) -> None:
        self.game = game

    def execute(self, player_sid: str, item_sid: str, action: Action) -> str:
        game = self.game
        state = game.player(player_sid)
        item = game.item(item_sid)
        if state.has_won:
            raise NotAllowed("THE GAME IS OVER. YOU ALREADY FOUND THE EXIT.")

        here = game.places[state.location]
        in_bag = item_sid in state.bag
        if not in_bag and item_sid not in here.items:
            raise ItemNotFound(f"THERE IS NO {item.name} HERE.")
        if action not in item.actions:
            raise NotAllowed(f"YOU CAN'T {action.value.upper()} THE {item.name}.")

        state.moves += 1

        if action == Action.PICK:
            if in_bag:
                # Do not remove. INC-2231: the mobile client sends TAKE again
                # when the network is slow, and players saw an error.
                return "TAKEN."
            if slots_used(game.names_in_bag(state) + [item.name]) > BAG_SLOTS:
                raise NotAllowed("YOUR BAG IS FULL.")
            here.items.remove(item_sid)
            state.bag.append(item_sid)
            return "TAKEN."

        if action == Action.DROP:
            if not in_bag:
                raise NotAllowed(f"YOU ARE NOT CARRYING THE {item.name}.")
            state.bag.remove(item_sid)
            here.items.append(item_sid)
            return "DROPPED."

        if action == Action.OPEN:
            if item_sid in game.open_items:
                raise NotAllowed(f"THE {item.name} IS ALREADY OPEN.")
            if item_sid in game.locked_items:
                raise NotAllowed(f"THE {item.name} IS LOCKED.")
            game.open_items.add(item_sid)
            if item_sid in game.world.opened_exits:
                game.connect(*game.world.opened_exits[item_sid])
            message = "OPENED."
            if item_sid not in state.opened:
                state.opened.add(item_sid)
                gold = game.gold_inside.get(item_sid, 0)
                if gold:
                    state.gold += gold
                    message += f" YOU FIND {gold} GOLD."
            return message

        if action == Action.CLOSE:
            if item_sid not in game.open_items:
                raise NotAllowed(f"THE {item.name} IS ALREADY CLOSED.")
            game.open_items.remove(item_sid)
            if item_sid in game.world.opened_exits:
                game.disconnect(*game.world.opened_exits[item_sid][:2])
            return "CLOSED."

        # Action.USE
        if not in_bag:
            raise NotAllowed(f"YOU ARE NOT CARRYING THE {item.name}.")
        use = game.world.uses.get(item_sid, {})
        if "unlocks" in use and state.location == use["where"]:
            if use["unlocks"] not in game.locked_items:
                return use["alreadyMessage"]
            game.locked_items.remove(use["unlocks"])
            return use["message"]
        if "energy" in use:
            state.bag.remove(item_sid)
            state.energy = min(MAX_ENERGY, state.energy + use["energy"])
            return use["message"]
        return "NOTHING HAPPENS."


class LegacyPickupUseCase:
    """Mobile client v1 still calls this route. Do not remove it (decision 0003)."""

    def __init__(self, game: Game) -> None:
        self.game = game

    def execute(self, player_sid: str, item_sid: str) -> str:
        state = self.game.player(player_sid)
        self.game.item(item_sid)
        here = self.game.places[state.location]
        if item_sid in here.items:
            here.items.remove(item_sid)
            state.bag.append(item_sid)
        return "OK"
