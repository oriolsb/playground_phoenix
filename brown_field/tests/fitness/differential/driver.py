"""One side of the differential run: one version of Katacombs answers the sessions.

Usage, with PYTHONPATH=<tree>:

    python driver.py <tree> <transcripts.py> <out.jsonl.gz> <seeds>

<tree> holds the `brown_field` package under test; the run fails if Python
imports `brown_field` from anywhere else. <transcripts.py> is the session
generator, always taken from the tree that runs the test, so both versions
get the same requests. Each session is one line of <out>: its key (zone,
start, rat, session) and its normalized answers, with the files at the end.
`test_differential.py` runs it twice and compares.
"""
import contextlib, datetime, gzip, hashlib, importlib.util, json, os, random, sys, tempfile, time
from pathlib import Path

worktree, generator, out, seeds = Path(sys.argv[1]).resolve(), Path(sys.argv[2]), sys.argv[3], int(sys.argv[4])
import brown_field
loaded = Path(brown_field.__file__).resolve()
assert worktree in loaded.parents, f"imported {loaded}, not from {worktree}"
from brown_field.api import create_app
import time_machine
from zoneinfo import ZoneInfo

spec = importlib.util.spec_from_file_location("sessions_src", generator)
src = importlib.util.module_from_spec(spec); spec.loader.exec_module(src)

ZONES = ["UTC", "Asia/Kolkata", "America/New_York"]
STARTS = {"10:10Z": (10, 10), "10:20Z": (10, 20), "10:52Z": (10, 52)}  # Kolkata 15:40, 15:50 (cleaning), 16:22
RATS = ["off", "seeded"]


@contextlib.contextmanager
def world(zone, start, rat, seed):
    with tempfile.TemporaryDirectory(prefix="katacombs-diff-") as folder:
        os.environ["KATACOMBS_DB"] = str(Path(folder) / "katacombs.db")
        os.environ["KATACOMBS_HIGHSCORES"] = str(Path(folder) / "highscores.jsonl")
        os.environ["TZ"] = zone; time.tzset()
        saved = random.random
        random.seed(10_000 + seed)            # the sids and, with the rat on, the rat draws
        if rat == "off":
            random.random = lambda: 0.99
        h, m = STARTS[start]
        # A destination in the zone itself: time-machine then keeps TZ at that zone
        # (with a UTC destination it would set TZ=UTC and hide the local clock).
        moment = datetime.datetime(2026, 1, 5, h, m, tzinfo=datetime.timezone.utc).astimezone(ZoneInfo(zone))
        try:
            with time_machine.travel(moment, tick=False) as t:
                yield src.Recorder(lambda: src.TestClient(create_app()), lambda: t.shift(datetime.timedelta(seconds=1)))
        finally:
            random.random = saved


BREAD = [f"000100-000000000000-{n:08d}" for n in (8, 9, 10)]
UMBRELLA, KEY_SID = "000100-000000000000-00000011", "000100-000000000000-00000002"
ROUTES = [  # each player gathers cheap items elsewhere, then stands in the brewery
    [("move", "north"), ("pick", src.BEER), ("pick", src.BEER_2)],
    [("move", "west"), ("pick", BREAD[0]), ("pick", BREAD[1]), ("pick", UMBRELLA), ("move", "east"), ("move", "north")],
    [("move", "north"), ("move", "up"), ("pick", KEY_SID), ("move", "down")],
]


def rat_session(rec, seed):
    """Players carry cheap items in and out of the cellar, so the rat draws (MOVE-8)."""
    chooser = random.Random(seed)
    sids = []
    for name in ["RAT", "MOUSE", "CAT"]:
        line, body = rec.send("start", "POST", "/game/player", {"name": name})
        sids.append(body["sid"]); yield line
    for sid, route in zip(sids, ROUTES):
        for kind, arg in route:
            path = f"/player/{sid}/move/{arg}" if kind == "move" else f"/player/{sid}/item/{arg}/use/pick"
            yield rec.send(kind, "PUT", path)[0]
    in_cellar = {sid: False for sid in sids}
    for step in range(40):
        sid = chooser.choice(sids)
        bag = rec.client.get(f"/player/{sid}/bag").json()
        food = [i["sid"] for i in bag["items"] if i["name"] in ("BEER", "BREAD")]
        if bag["energy"] <= 1 and food:
            yield rec.send(f"{step} eat", "PUT", f"/player/{sid}/item/{food[0]}/use/use")[0]
            continue
        line, _ = rec.send(f"{step} move", "PUT", f"/player/{sid}/move/{'up' if in_cellar[sid] else 'down'}")
        if line["status"] == 200:
            in_cellar[sid] = not in_cellar[sid]
        yield line
        if chooser.random() < 0.3:
            yield rec.send(f"{step} bag", "GET", f"/player/{sid}/bag")[0]
    for sid in sids:
        yield rec.send("look", "GET", f"/player/{sid}/location")[0]
        yield rec.send("save", "POST", f"/player/{sid}/save")[0]
    yield rec.restart()
    yield rec.send("list after restart", "GET", "/game/player")[0]
    yield from rec.files("at the end")


count = 0
with gzip.open(out, "wt", encoding="utf-8") as f:
    f.write(json.dumps({"loaded": str(loaded)}) + "\n")
    for zone in ZONES:
        for start in STARTS:
            for rat in RATS:
                jobs = [(f"random-{s}", s, lambda r, s=s: src.random_session(r, s)) for s in range(1, seeds + 1)]
                jobs += [(f"rat-{s}", s, lambda r, s=s: rat_session(r, s)) for s in range(1, seeds + 1)]
                jobs.append(("scripted", 0, src.scripted_session))
                for name, seed, session in jobs:
                    with world(zone, start, rat, seed) as rec:
                        lines = [json.dumps(l, ensure_ascii=False, sort_keys=True) for l in session(rec)]
                    key = f"{zone}|{start}|rat-{rat}|{name}"
                    f.write(json.dumps({"key": key, "sha": hashlib.sha256("\n".join(lines).encode()).hexdigest(), "lines": lines}) + "\n")
                    count += sum(1 for l in lines if '"status"' in l)
print(f"{loaded.parent}: {count} requests answered")
