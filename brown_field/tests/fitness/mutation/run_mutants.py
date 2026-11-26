"""Break the game-server one rule at a time, and report each break that no test sees.

A fitness function of the Evaluation (decision 0010). Each mutant changes one
line of the game-server code in a copy of the package,
and runs the suite there. A killed mutant fails a test; a surviving one passes
every test, so a regenerated game could make that change in silence.

The mutants are written against the text of the legacy code. A mutant whose
text is not found is reported as "not applicable": on a regenerated
implementation, use a generic tool (for example mutmut) instead.

Run from the package root:

    uv run python brown_field/tests/fitness/mutation/run_mutants.py

It works in a temporary copy, and never changes the working tree. Exit code 1
when a mutant survives that `mutants.md` does not list as accepted.
"""

import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
HS = "brown_field/adapters/files/high_scores.py"
DB = "brown_field/adapters/sqlite/stores.py"
CONST = "brown_field/domain/constants.py"
STATE = "brown_field/application/state.py"
CASES = "brown_field/application/use_cases.py"
REST = "brown_field/adapters/rest/app.py"
WORLD = "brown_field/domain/world.py"
BAG = "brown_field/domain/bag.py"
NAMES = "brown_field/domain/names.py"
PLAYER = "brown_field/domain/player.py"

# (file, old text, new text, label). Each old text must occur exactly once.
MUTANTS = [
    (CONST, "BAG_SLOTS = 8", "BAG_SLOTS = 9", "bag slots 8 -> 9"),
    (CONST, "ITEMS_PER_SLOT = 3", "ITEMS_PER_SLOT = 2", "items per slot 3 -> 2"),
    (BAG, 'math.ceil(count / ITEMS_PER_SLOT)', '(count // ITEMS_PER_SLOT + 1)', 'slot count: ceil -> floor + 1'),
    (CONST, "NAME_MAX_LENGTH = 50", "NAME_MAX_LENGTH = 49", "name max 50 -> 49"),
    (CONST, "MAX_PLAYERS = 20", "MAX_PLAYERS = 21", "max players 20 -> 21"),
    (CONST, 'RESERVED_NAMES = {"ADMIN"}', "RESERVED_NAMES = set()", "no reserved names"),
    (CONST, "START_ENERGY = 12", "START_ENERGY = 13", "start energy 12 -> 13"),
    (CONST, "MAX_ENERGY = 20", "MAX_ENERGY = 21", "max energy 20 -> 21"),
    (CONST, "RAT_CHANCE = 0.2", "RAT_CHANCE = 0.3", "rat chance 0.2 -> 0.3"),
    (CONST, "RAT_CHANCE = 0.2", "RAT_CHANCE = 0.1", "rat chance 0.2 -> 0.1"),
    (CONST, '"BREAD": 5', '"BREAD": 4', "bread energy 5 -> 4"),
    (CONST, '"BEER": 3}', '"BEER": 4}', "beer energy 3 -> 4"),
    (STATE, "clock.now().minute >= 50", "clock.now().minute >= 51", "market closes at 51"),
    (STATE, "clock.now().minute >= 50", "clock.now().astimezone(timezone.utc).minute >= 50", "market reads UTC"),
    (DB, 'os.environ.get("KATACOMBS_DB", "katacombs.db")', 'os.environ.get("KATACOMBS_DB", "game.db")', "default database file name"),
    (STATE, "hashlib.sha256(password", "hashlib.sha3_256(password", "password hash sha256 -> sha3"),
    (STATE, "                # The world changed under an old save.\n                continue", "                pass", "old save at an unknown location loads"),
    (STATE, 'f"{place.description} {note}".strip()', 'f"{place.description} {note}"', "description keeps a trailing space"),
    (NAMES, '    name = name.strip().upper()', '    name = name.upper()', 'player name not stripped'),
    (CASES, "if len(self.game.players) >= MAX_PLAYERS:", "if len(self.game.players) > MAX_PLAYERS:", "player limit off by one"),
    (PLAYER, 'cheap = [sid for sid in self.bag if not items[sid].value]', 'cheap = [sid for sid in self.bag if items[sid].value < 10]', 'rat takes value < 10'),
    (CASES, 'game.places[TUBE_TUNNEL].items.append(stolen)', 'game.places[CELLAR].items.append(stolen)', 'rat leaves the item in the cellar'),
    (NAMES, 'if "@" not in email:', 'if email.count("@") != 1:', 'email needs exactly one @'),
    (CASES, 'if data and data["location"] in game.places:', "if data:", "login restores a snapshot at an unknown location"),
    (CASES, "if sid not in game.players and len(game.players) >= MAX_PLAYERS:", "if False:", "login restore ignores the player limit"),
    (PLAYER, 'if place.title not in self.visited:', 'if True:', 'gold on every visit'),
    (PLAYER, '"YOUR BAG IS FULL."', '"THE BAG IS FULL."', 'bag-full message'),
    (WORLD, 'if item_sid == KEY and location == BACK_YARD:', 'if item_sid == KEY:', 'key unlocks anywhere'),
    (CASES, '"NOTHING HAPPENS."', '"NOTHING HAPPENED."', "nothing-happens message"),
    (PLAYER, 'self.energy = min(MAX_ENERGY, self.energy + ENERGY_FROM[item.name])', 'self.energy = self.energy + ENERGY_FROM[item.name]', 'no energy cap'),
    (WORLD, '            self.disconnect(BACK_YARD, Direction.DOWN)', '            pass', 'closing the manhole keeps the exit'),
    (HS, '"at": at.astimezone(timezone.utc).isoformat(timespec="seconds"),', '"at": at.astimezone(timezone.utc).isoformat(),', "high-score time with microseconds"),
    (STATE, "if sid not in self.players and sid not in self.items:", "if True:", "sid collision check removed"),
    (WORLD, "if (place.title, direction) in one_way:\n                continue", "if True:\n                continue", "world check disabled"),
    (STATE, "            if account.player_sid == player_sid:\n                return account", "            if account.player_sid:\n                return account", "a quit finds the first account with a player"),
    (DB, "ORDER BY saved_at", "ORDER BY player_sid", "saves load in sid order"),
    (CASES, '        state.count_command()\n        return "SENT."', '        return "SENT."', 'chat does not count a move'),
    (CASES, "if message.location == state.location", "if True", "chat shows every location"),
    (REST, "if state is not None and state.energy <= 0:", "if state is not None and state.energy < 0:", "energy gate at -1"),
    (CASES, "            state.bag.append(item_sid)\n        return \"OK\"", "            state.bag.append(item_sid)\n            state.moves += 1\n        return \"OK\"", "legacy pickup counts a move"),
    (REST, "return error(500, str(exc))", "return error(400, str(exc))", "unknown error status 500 -> 400"),
    (REST, 'return error(400, "INVALID REQUEST.")', 'return error(422, "INVALID REQUEST.")', "malformed request 400 -> 422"),
]


def accepted_survivors() -> dict[str, str]:
    """The survivors that mutants.md accepts, with their reason."""
    table = (Path(__file__).parent / "mutants.md").read_text(encoding="utf-8")
    found = {}
    for line in table.splitlines():
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) >= 4 and cells[2] == "survives":
            found[cells[0]] = cells[3]
    return found


def copy_package(target: Path) -> None:
    for name in ("pyproject.toml", "uv.lock"):
        shutil.copy(ROOT / name, target / name)
    ignore = shutil.ignore_patterns("__pycache__", "node_modules", "dist", "test-results", ".pytest_cache")
    shutil.copytree(ROOT / "brown_field", target / "brown_field", ignore=ignore)


def run_suite(folder: Path) -> subprocess.CompletedProcess:
    env = {k: v for k, v in os.environ.items() if k != "VIRTUAL_ENV"}
    return subprocess.run(
        ["uv", "run", "--quiet", "pytest", "-q", "-x", "-p", "no:warnings", "-p", "no:cacheprovider"],
        cwd=folder, capture_output=True, text=True, env=env,
    )


def main() -> int:
    accepted = accepted_survivors()
    with tempfile.TemporaryDirectory(prefix="katacombs-mutants-") as tmp:
        folder = Path(tmp)
        copy_package(folder)
        baseline = run_suite(folder)
        if baseline.returncode != 0:
            print("The suite fails on the unchanged copy:\n" + baseline.stdout[-2000:])
            return 2
        unexpected, killed, survived, skipped = [], 0, 0, 0
        for path, old, new, label in MUTANTS:
            source_file = folder / path
            source = source_file.read_text(encoding="utf-8")
            if source.count(old) != 1:
                skipped += 1
                print(f"n/a       {label}")
                continue
            source_file.write_text(source.replace(old, new), encoding="utf-8")
            result = run_suite(folder)
            source_file.write_text(source, encoding="utf-8")
            if result.returncode != 0:
                killed += 1
                failed = re.search(r"^FAILED \S+::(\S+)", result.stdout, re.M)
                print(f"killed    {label:46} {failed.group(1)[:70] if failed else ''}")
            else:
                survived += 1
                reason = accepted.get(label)
                print(f"SURVIVED  {label:46} {('accepted: ' + reason) if reason else 'NOT ACCEPTED'}")
                if not reason:
                    unexpected.append(label)
        print(f"\n{killed} killed, {survived} survived ({survived - len(unexpected)} accepted), {skipped} not applicable, of {len(MUTANTS)}")
        if unexpected:
            print("Survivors with no reason in mutants.md: " + "; ".join(unexpected))
            return 1
        return 0


if __name__ == "__main__":
    sys.exit(main())
