"""Bind privacy.feature: the fitness functions of ACCOUNT-9 and ACCOUNT-13.

Each search reads only what a client or another program can read: the
answers of the read routes, and the database file as raw bytes. Raw bytes
catch a value that a row no longer holds but the file still does.
"""

from pytest_bdd import parsers, scenarios, then

scenarios("privacy.feature")


def public_answers(play, sids: list[str]) -> list[str]:
    """The bodies of every read route that needs no credential, and of each sid's own views."""
    client = play.client
    bodies = [client.get("/leaderboard").text, client.get("/game/player").text]
    bodies += [client.get(f"/profiles/{sid}").text for sid in play.profiles.values()]
    bodies += [client.get(f"/profiles/{sid}").text for sid in play.deleted_profiles.values()]
    for sid in sids:
        for route in ("location", "bag", "chat"):
            bodies.append(client.get(f"/player/{sid}/{route}").text)
    return bodies


@then(parsers.parse('no answer of the public read routes holds "{email}" in any letter case'))
def no_answer_holds_the_email(play, email):
    for body in public_answers(play, list(play.players.values())):
        assert email.lower() not in body.lower(), body


@then(parsers.parse('nothing identifies "{email}", "{name}" or the player'))
def nothing_identifies(play, isolated_files, email, name):
    player_sid = play.sid(name)
    others = [sid for key, sid in play.players.items() if key != name]
    needles = [email.lower(), name.lower(), player_sid]
    for body in public_answers(play, others):
        for needle in needles:
            assert needle not in body.lower(), (needle, body)
    stored = isolated_files.db.read_bytes().lower()
    for needle in needles:
        assert needle.encode("utf-8") not in stored, f"{needle} is still in the database file"
