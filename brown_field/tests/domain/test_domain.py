"""The domain model with no port, no fake and no game (decision 0017).

These tests pin the rules where they live. The same rules are pinned over
REST and at the ports, so a regeneration that changes the domain's shape
deletes these and keeps those.
"""

import pytest

from brown_field.domain.bag import has_room, slots_used
from brown_field.domain.errors import InvalidName, NotAllowed
from brown_field.domain.names import check_email, player_name
from brown_field.domain.player import PlayerState
from brown_field.domain.world import Place, World, WorldData
from brown_field.kata import Action, Direction, Item

KEY = "000100-000000000000-00000002"
MANHOLE = "000100-000000000000-00000005"


def item(sid: str, name: str, value: int = 0, actions=(Action.PICK, Action.DROP, Action.USE)) -> Item:
    return Item(sid, name, f"A {name}.", list(actions), value=value)


def small_world() -> World:
    yard = Place("BACK YARD", "A YARD.", {Direction.NORTH: "LANE"}, [MANHOLE])
    lane = Place("LANE", "A LANE.", {Direction.SOUTH: "BACK YARD"}, [], gold=5)
    below = Place("KATACOMBS", "DARK.", {}, [])
    manhole = item(MANHOLE, "MANHOLE", actions=(Action.OPEN, Action.CLOSE))
    return World(WorldData(
        start="LANE",
        places={p.title: p for p in (yard, lane, below)},
        items={MANHOLE: manhole, KEY: item(KEY, "KEY")},
        locked={MANHOLE},
    ))


@pytest.mark.parametrize("raw, kept", [("  ana ", "ANA"), ("x" * 50, "X" * 50)])
def test_a_name_is_trimmed_and_upper_case(raw, kept):
    assert player_name(raw) == kept


@pytest.mark.parametrize("raw", ["", "   ", "x" * 51, "admin"])
def test_a_bad_name_is_refused(raw):
    with pytest.raises(InvalidName):
        player_name(raw)


def test_an_email_needs_an_at():
    check_email("a@b")
    with pytest.raises(InvalidName, match="THE EMAIL IS NOT VALID."):
        check_email("ab")


def test_a_slot_holds_three_items_with_one_name():
    assert slots_used(["BREAD"] * 3) == 1
    assert slots_used(["BREAD"] * 4) == 2
    assert has_room(["X"] * 7 * 3 + ["BREAD"] * 3, "BREAD") is False
    assert has_room(["X"] * 7 * 3 + ["BREAD"] * 2, "BREAD") is True


def test_the_first_visit_adds_the_gold_once():
    lane = Place("LANE", "A LANE.", {}, [], gold=5)
    player = PlayerState("1", "ANA", "START")
    player.walk_to(lane)
    player.walk_to(lane)
    assert (player.gold, player.energy, player.moves) == (5, 10, 2)


def test_bread_restores_energy_up_to_20_and_is_eaten():
    bread = item("B", "BREAD")
    player = PlayerState("1", "ANA", "LANE", bag=["B"], energy=18)
    assert player.eat_or_drink(bread) == "YOU EAT THE BREAD. YOU FEEL STRONGER."
    assert (player.energy, player.bag) == (20, [])


def test_the_rat_takes_only_an_item_without_value():
    items = {"R": item("R", "RING", value=20), "C": item("C", "CANDLE")}
    player = PlayerState("1", "ANA", "CELLAR", bag=["R", "C"])
    assert player.lose_to_the_rat(items, lambda: 0.0, lambda cheap: cheap[0]) == "C"
    assert player.bag == ["R"]


def test_the_rat_draws_no_chance_when_nothing_is_cheap():
    items = {"R": item("R", "RING", value=20)}
    player = PlayerState("1", "ANA", "CELLAR", bag=["R"])

    def no_draw() -> float:
        raise AssertionError("the chance was drawn")

    assert player.lose_to_the_rat(items, no_draw, lambda cheap: cheap[0]) is None


def test_a_player_who_has_won_can_not_act():
    player = PlayerState("1", "ANA", "EXIT")
    player.win()
    with pytest.raises(NotAllowed, match="THE GAME IS OVER."):
        player.ensure_playing()


def test_the_key_unlocks_the_manhole_in_the_back_yard_only():
    world = small_world()
    assert world.use_key(KEY, "LANE") is None
    assert world.use_key(KEY, "BACK YARD") == "YOU UNLOCK THE MANHOLE COVER."
    assert world.use_key(KEY, "BACK YARD") == "THE MANHOLE COVER IS ALREADY UNLOCKED."


def test_the_open_manhole_connects_the_back_yard_and_the_katacombs():
    world = small_world()
    manhole = world.items[MANHOLE]
    with pytest.raises(NotAllowed, match="IS LOCKED"):
        world.open(manhole)
    world.use_key(KEY, "BACK YARD")
    world.open(manhole)
    assert world.places["BACK YARD"].exits[Direction.DOWN] == "KATACOMBS"
    assert world.places["KATACOMBS"].exits[Direction.UP] == "BACK YARD"
    world.close(manhole)
    assert Direction.DOWN not in world.places["BACK YARD"].exits
    with pytest.raises(NotAllowed, match="IS ALREADY CLOSED"):
        world.close(manhole)


@pytest.mark.parametrize("minute, closed", [(0, False), (49, False), (50, True), (59, True)])
def test_the_market_closes_in_the_last_ten_minutes_with_no_clock(minute, closed):
    """MOVE-6, decision 0020: a pure function of the minute."""
    from brown_field.domain.world import market_is_cleaning

    assert market_is_cleaning(minute) is closed
