"""The items: inspecting them, the bag, and the five actions."""

from ..kata import Action, Bag, Direction, Item
from .errors import ItemNotFound, NotAllowed
from .rules import BAG_SLOTS, ENERGY_FROM, MAX_ENERGY, slots_used
from .state import GameState
from .world import BACK_YARD, KATACOMBS, KEY, MANHOLE


class InspectItemUseCase:
    def __init__(self, game: GameState) -> None:
        self.game = game

    def execute(self, item_sid: str) -> Item:
        return self.game.item(item_sid)


class InspectBagUseCase:
    def __init__(self, game: GameState) -> None:
        self.game = game

    def execute(self, player_sid: str) -> Bag:
        return self.game.to_bag(self.game.player(player_sid))


class UseItemUseCase:
    def __init__(self, game: GameState) -> None:
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
            if item_sid == MANHOLE:
                game.connect(BACK_YARD, Direction.DOWN, KATACOMBS)
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
            if item_sid == MANHOLE:
                game.disconnect(BACK_YARD, Direction.DOWN)
            return "CLOSED."

        # Action.USE
        if not in_bag:
            raise NotAllowed(f"YOU ARE NOT CARRYING THE {item.name}.")
        if item_sid == KEY and state.location == BACK_YARD:
            if MANHOLE not in game.locked_items:
                return "THE MANHOLE COVER IS ALREADY UNLOCKED."
            game.locked_items.remove(MANHOLE)
            return "YOU UNLOCK THE MANHOLE COVER."
        if item.name in ENERGY_FROM:
            state.bag.remove(item_sid)
            state.energy = min(MAX_ENERGY, state.energy + ENERGY_FROM[item.name])
            if item.name == "BEER":
                return "YOU DRINK THE BEER. YOU FEEL BRAVE."
            return "YOU EAT THE BREAD. YOU FEEL STRONGER."
        return "NOTHING HAPPENS."
