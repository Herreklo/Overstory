"""Tests for test 1's tie script (tools/playable/ties.py): toy cases for the referee (the spread, the clock and the
score), run before it referees the case, and the parsers that build the tie table from the export's text. A plain
script:

    python3 tools/tests/test_ties.py

Exit 0 when every test passes. Reads the export and the case spec; writes nothing.
"""
import json
import os
import sys
import traceback
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(HERE)
ROOT = os.path.dirname(TOOLS)
sys.path.insert(0, os.path.join(TOOLS, "playable"))
import facts as F  # noqa: E402
import ties as T  # noqa: E402

RESULTS = []
W = F.World(json.load(open(os.path.join(ROOT, "fixtures", "engine", "understory-world-9989.json"))))
DEC89, OCT98 = (1989, 12), (1998, 10)


def check(cond, what):
    if not cond:
        raise AssertionError(what)


def test(fn):
    try:
        fn()
        RESULTS.append((True, fn.__name__, ""))
    except Exception as e:  # report each test, keep going
        RESULTS.append((False, fn.__name__, "%s\n%s" % (e, traceback.format_exc())))
    return fn


# -- toy cases: a town of a few people, hand-made, with the referee's answers worked by hand ----------------------

RULE = {"w_kin": 3, "w_partner": 3, "w_cowork": 1, "w_like": 1, "tau": 30, "tell": 15, "elsewhere": 10,
        "speed": 1.4, "flight": 0.55, "max_tellings": 4}
HOURS = {"day": [600, 1080], "deadline": 1080, "work": [540, 1020], "place_hours": {}, "bar_lead": 660,
         "bar_staff": 720, "regulars": 1080}
SCORE = {"points": 80, "spread_share": 0.5, "leak": 5, "exposure": 10, "pass": 60}


def toy(people, ties=(), jobs=None, homes=None, regulars=(), visitors=("p-1", "p-2"), dead="p-99", lead=None):
    """A Case over a toy town. people: ids alive; ties: (a, b, kind, n); jobs: {pid: place}; homes: {pid: point}.
    Every point is a minute from every other; "elsewhere" is 10 minutes; the Anchor is the point "bar"."""
    tt = object.__new__(T.TieTable)
    tt.alive = set(people)
    tt.ties = defaultdict(lambda: defaultdict(lambda: dict(kin=0, partner=0, cowork=0, like=0, sources=[])))
    for a, b, kind, n in ties:
        tt._add(a, b, kind, n, "toy")
    tt.job = {p: (pl, []) for p, pl in (jobs or {}).items()}
    c = object.__new__(T.Case)
    c.spec = {"score": SCORE, "place_points": {"pl-bar": "bar"}}
    c.s = {"homes": homes or {}}
    c.rule, c.hours, c.ties = dict(RULE), dict(HOURS), tt
    c.visitors, c.dead = list(visitors), dead
    c.points = {k: (0.0, 0.0) for k in ["A", "bar", "h1", "h2", "h3", "h4"]}
    c.walk, c._minutes = None, {}
    c.home = {p: (homes or {}).get(p, "elsewhere") for p in people}
    c.player_home = "A"
    c.friday = set(regulars)
    c.job = {p: pl for p, (pl, _) in tt.job.items()}
    c.lead = {"pl-bar": lead}
    c.bar_from = c.at_anchor_from()
    return c


def run(c, line):
    out = T.simulate(c, line)
    return out, T.score(c, out)


@test
def toy_1_telling_nobody_scores_nothing_and_leaks_nothing():
    c = toy(["p-1", "p-2", "p-3"], ties=[("p-1", "p-3", "like", 1)], homes={"p-1": "h1", "p-2": "h2"},
            regulars=["p-1", "p-2", "p-3"])
    out, sc = run(c, ())
    check(sc["total"] == 0 and sc["leaks"] == [], "nobody told: 0, no leaks (%r)" % sc)
    check(all(h[1] == "bar" and h[0] == 1080 for h in out["heard"].values()) and len(out["heard"]) == 3,
          "at 18:00 the Anchor says it to its three regulars: %r" % out["heard"])


@test
def toy_2_two_isolated_visitors_told_directly_score_80():
    c = toy(["p-1", "p-2"], homes={"p-1": "h1", "p-2": "h2"})
    out, sc = run(c, ("p-1", "p-2"))
    check(sc["total"] == 80 and sc["leaks"] == [], "both told by the player, nobody else: 80 (%r)" % sc)
    t = out["tellings"]
    # A to h1 is a minute, then 15 to tell; h1 to h2 a minute, then 15
    check([(p, a, d) for p, a, d, _ in t] == [("p-1", 601, 616), ("p-2", 617, 632)], "the clock: %r" % t)


@test
def toy_3_a_chain_through_a_friend_scores_half_less_a_leak():
    # p-3 is p-1's friend; both free. The player tells p-3 and p-2: p-3 tells p-1 half an hour later.
    c = toy(["p-1", "p-2", "p-3"], ties=[("p-1", "p-3", "like", 1)], homes={"p-1": "h1", "p-2": "h2", "p-3": "h3"})
    out, sc = run(c, ("p-3", "p-2"))
    check(out["heard"]["p-1"] == (616 + 30, "spread", "p-3"), "p-1 hears from p-3 at 10:46: %r" % (out["heard"]["p-1"],))
    check(sc["parts"] == {"p-1": 20, "p-2": 40} and sc["leaks"] == ["p-3"] and sc["total"] == 55,
          "20 + 40 - 5 = 55: %r" % sc)


@test
def toy_4_said_at_the_anchor_everyone_there_hears_and_later_comers_too():
    # p-4 leads the Anchor (in from 11:00), p-5 is its staff (from 12:00), p-2 a visitor who is a Friday regular.
    c = toy(["p-1", "p-2", "p-4", "p-5"], jobs={"p-4": "pl-bar", "p-5": "pl-bar"}, lead="p-4",
            homes={"p-1": "h1", "p-2": "h2"}, regulars=["p-2"])
    # at 10:00 p-4 is at home elsewhere: 10 minutes away, told 10:10 to 10:25; at 11:00 he is in and says it aloud
    out, sc = run(c, ("p-4",))
    check(out["heard"]["p-4"] == (625, "player", "player"), "p-4 told at home: %r" % (out["heard"]["p-4"],))
    check(out["bar_since"] == 685, "said aloud at the first half hour he is in (10:25 + 30 + 30 = 11:25): %r" % out["bar_since"])
    check(out["heard"]["p-5"] == (720, "bar", "the Anchor"), "p-5 hears as she comes in at 12:00: %r" % (out["heard"]["p-5"],))
    check(out["heard"]["p-2"][:2] == (1080, "bar"), "the regular hears it at the bar at 18:00: %r" % (out["heard"]["p-2"],))
    check(sc["total"] == -10 and sc["leaks"] == ["p-4", "p-5"], "0 + 0 - 10: %r" % sc)


@test
def toy_5_reach_workers_tell_coworkers_not_free_people():
    # p-6 works at the mill with p-7; p-1 is p-6's son (kin 3) but free; p-7 a coworker (1). p-6 hears at work.
    c = toy(["p-1", "p-2", "p-6", "p-7"], ties=[("p-6", "p-1", "kin", 1), ("p-6", "p-7", "cowork", 1)],
            jobs={"p-6": "pl-mill", "p-7": "pl-mill"}, homes={"p-1": "h1", "p-2": "h2"})
    out, _ = run(c, ("p-6",))
    check(out["heard"]["p-7"][1:] == ("spread", "p-6"), "the coworker in reach hears first: %r" % out["heard"])
    check(out["heard"]["p-1"] == (1045, "spread", "p-6"),
          "the son hears at p-6's first half hour off work (17:00 ends the shift; 10:25 + 14 x 30 = 17:25): %r"
          % (out["heard"].get("p-1"),))


@test
def toy_6_a_telling_that_would_end_after_the_deadline_is_not_made():
    c = toy(["p-1", "p-2"], homes={"p-1": "h1", "p-2": "h2"})
    out = T.simulate(c, ("p-1", "p-2"), start=1060)
    check([p for p, _ in out["skipped"]] == ["p-2"] and "p-1" in out["heard"], "p-1 by 17:16, p-2 not: %r" % out)


@test
def toy_7_the_dead_hear_nothing_and_strangers_are_nobodys():
    c = toy(["p-1", "p-2", "p-8"], homes={"p-1": "h1", "p-2": "h2"})
    out, sc = run(c, ("p-99", "p-1"))
    check(out["skipped"] == [("p-99", "not alive")] and "p-8" not in out["heard"], "%r" % out)


# -- the parsers, on the export ------------------------------------------------------------------------------------

@test
def dislike_names_its_other_person_in_the_text():
    ds = [e for e in W.events if e["type"] == "dislike"]
    pairs = [T.pair_of(W, e) for e in ds]
    check(len(ds) == 22 and all(pairs), "every dislike parses to two people: %r" %
          [e["text"] for e, p in zip(ds, pairs) if not p])
    for e, (a, b) in zip(ds, pairs):
        check(a == e["who"][0], "the actor is who[0]: %s" % e["id"])


@test
def partners_at_a_month_are_dated():
    p89, p98 = T.partners_at(W, DEC89), T.partners_at(W, OCT98)
    olive, ben, matt = "p-37", "p-72", W.by_name["Matt Sayer"]
    check(frozenset((olive, matt)) not in p89, "Olive and Matt split in January 1989 (e-6379)")
    check(frozenset((olive, ben)) not in p89 and frozenset((olive, ben)) in p98, "Olive and Ben from 1992")
    audrey, trevor = W.by_name["Audrey Scott"], W.by_name["Trevor Lane"]
    check(p89.get(frozenset((audrey, trevor)), ("", ""))[0] == "derived", "Audrey and Trevor, married until 1991 (e-7087)")


@test
def rosters_at_1989_are_derived_from_text():
    tt = T.TieTable(W, DEC89)
    cafe = sorted(p for p, (pl, _) in tt.job.items() if pl == "pl-cafe13")
    check(set(cafe) == {W.by_name[n] for n in ("Peter Lane", "Eddie Lane", "Lisa Myers")}, "the café's 1989 people: %r" % cafe)
    bar = {p for p, (pl, _) in tt.job.items() if pl == "pl-bar"}
    check({"p-31", "p-37", "p-81"} <= bar, "Sean, Olive and Evan at the Anchor: %r" % bar)
    check(W.lead_at("pl-bar", DEC89)[0] == "p-31", "Sean leads the Anchor in December 1989")
    check(W.lead_at("pl-bar", OCT98)[0] == "p-81", "Evan leads it in October 1998")


@test
def hannahs_ties_are_thin():
    tt = T.TieTable(W, DEC89)
    c = tt.counts("p-2")
    check(c["kin"] == 1 and "p-3" in tt.ties["p-2"], "her son Sid: %r" % c)
    check(tt.ties["p-2"]["p-72"]["like"] >= 1, "Ben Reed (e-6400, confide)")
    check("p-36" not in tt.alive, "Agnes is dead at the case's month")
    check(c["any"] <= 3, "two or three ties at most: %r" % dict(tt.ties["p-2"]))


@test
def the_spec_is_the_frozen_case():
    spec, sha = T.spec_block()
    check(sha == T.FROZEN, "case-spec.md's block is the frozen case (%s)" % sha)
    check(spec["seeds"]["A"]["page"] == "p-31" and spec["seeds"]["A"]["player_home"] == "A", "Sean; the player at A")


def main():
    for ok, name, why in RESULTS:
        print("%s %s%s" % ("ok  " if ok else "FAIL", name, "" if ok else ": " + why))
    n_bad = sum(1 for ok, _, _ in RESULTS if not ok)
    print("%d of %d passed (Python %s)" % (len(RESULTS) - n_bad, len(RESULTS), sys.version.split()[0]))
    return 1 if n_bad else 0


if __name__ == "__main__":
    sys.exit(main())
