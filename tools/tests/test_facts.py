"""Tests for test 5's facts check (tools/playable/facts.py): the derived rosters, the text parsers on the case's own
sentences, and toy diaries built from the lines the check found false. A plain script:

    python3 tools/tests/test_facts.py

Exit 0 when every test passes. Reads the export and the case's documents; writes nothing.
"""
import copy
import json
import os
import sys
import traceback

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(HERE)
ROOT = os.path.dirname(TOOLS)
sys.path.insert(0, os.path.join(TOOLS, "playable"))
import facts as F  # noqa: E402

RESULTS = []
W = F.World(json.load(open(os.path.join(ROOT, "fixtures", "engine", "understory-world-9989.json"))))
CAST = F.casting(W)
NAMES = F.Names(W)
WS = json.load(open(os.path.join(ROOT, "fixtures", "lt1-corner.json")))["worldSeed"]
DEC89 = (1989, 12)


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


def pid(name):
    return W.by_name[name]


def sentence(s, para_place=None, prior=(), row_house=None):
    rep = F.Report()
    F.check_sentence(W, NAMES, s, "t", "record", rep, DEC89, para_place, row_house, [pid(n) for n in prior])
    return rep


def bad(rep, cls=None):
    return [it for it in rep.items if it["verdict"] != "note" and (cls is None or it["cls"] == cls)]


def diary(events, did=1107):
    return dict(id=did, type="house", character="low_road", plot=dict(x=0, w=7000, d=7000), provenance="authored",
                events=[dict(id=i + 1, **e) for i, e in enumerate(events)])


BUILT = dict(year=1828, kind="built", params=dict(era="classical", storeys=1500, wealth=200), cause="a fisherman builds")


def diary_findings(letter, d):
    rep = F.Report()
    F.diary_claims(W, letter, d, CAST.get(letter, {}), rep, "toy", "diary", WS)
    return rep


# -- the export and the shift --------------------------------------------------------------------------------------

@test
def shift_and_ages():
    check(W.shift == -37, "the shift is 1989 - 2026 = -37, got %d" % W.shift)
    check(W.end == (1999, 1), "the export ends January 1999, got %r" % (W.end,))
    check(W.age(pid("Hannah Tanner"), DEC89) == 74, "Hannah is 74 in December 1989")
    check(W.age(pid("Hannah Tanner"), (1989, 7)) == 73, "and 73 before her birthday in August")
    check(W.age(pid("Agnes Fielding"), DEC89) == 103, "Agnes is 103")
    check(W.age(pid("Una Waller"), DEC89) == 23, "Una is 23")
    check(W.died(pid("Agnes Fielding")) == (1989, 12), "Agnes dies in December 1989")
    check(W.died(pid("Tom Vaughan")) == (1985, 11), "Tom Vaughan dies in November 1985")


# -- the parsers (derived) -----------------------------------------------------------------------------------------

@test
def job_parser_on_the_engine_texts():
    want = {
        "e-7079": ("p-31", "startover", "pl-bar", None, None),
        "e-7137": ("p-41", "retired", "pl-cafe13", None, None),
        "e-6908": ("p-41", "stepdown", "pl-cafe13", None, "owner"),
        "e-7097": ("p-81", "promoted", "pl-bar", None, "manager"),
        "e-7478": ("p-11", "moved", "pl-council", "pl-harbour", None),
        "e-6528": ("p-99", "arrived", None, "pl-school", None),
        "e-6641": (W.by_id["e-6641"]["who"][0], "arrived", None, "pl-garage", None),  # "..., with Terry Baker and the children."
        "e-6688": ("p-51", "dismiss", "pl-mill", None, None),  # the one let go is who[1]
        "e-7749": ("p-41", "left", None, None, None),
        "e-7748": ("p-41", "take", None, None, None),
        "e-8736": ("p-37", "retired", "pl-bar", None, None),
    }
    for eid, w in want.items():
        got = F.parse_job(W.by_id[eid], W)
        check(got == w, "%s: %r, want %r" % (eid, got, w))
    check(F.parse_job(W.by_id["e-6557"], W) is None, "a death is not a job event")


@test
def retired_years_words_and_digits():
    check(F.retired_years("Olive Shaw retired after ten years at the Anchor.") == 10, "ten")
    check(F.retired_years("Peter Lane retired after 13 years at the Old Bank Café.") == 13, "13")
    check(F.retired_years("Leo Lyons retired after twelve years at the garage.") == 12, "twelve")


@test
def habit_parser_on_the_engine_texts():
    cases = [
        ("habit:back", "Once again, Vera Holmes rings her mother every Sunday evening.", "Vera Holmes", ("on", "rings her mother every Sunday evening")),
        ("keepaway", "Hannah Tanner is no longer at the Anchor every Friday without fail.", "Hannah Tanner", ("off", "at the Anchor every Friday without fail")),
        ("takeup", "Matt Sayer now has two pints at the Anchor most evenings.", "Matt Sayer", ("on", "has two pints at the Anchor most evenings")),
        ("habit:broke", "Steve Baker no longer walks the shore every evening.", "Steve Baker", ("off", "walks the shore every evening")),
        ("habit:new", "Harry Myers now sings with the choir every Thursday.", "Harry Myers", ("on", "sings with the choir every Thursday")),
    ]
    for typ, text, name, want in cases:
        got = F.parse_habit(dict(type=typ, text=text), name)
        check(got == want, "%r: %r, want %r" % (text, got, want))
    check(F.parse_habit(dict(type="visit", text="Hannah Tanner came round."), "Hannah Tanner") is None, "not a habit event")


# -- the rosters (derived) -----------------------------------------------------------------------------------------

@test
def jobs_in_1989():
    place, src = W.job_at(pid("Olive Shaw"), DEC89)
    check(place == "pl-bar" and "e-8736" in src, "Olive at the Anchor in 1989 from e-8736 (no hire event): %r %r" % (place, src))
    place, src = W.job_at(pid("Peter Lane"), DEC89)
    check(place == "pl-cafe13" and "e-7137" in src, "Peter Lane at the café: %r %r" % (place, src))
    place, src = W.job_at(pid("Sean Hale"), DEC89)
    check(place == "pl-bar" and "e-7079" in src, "Sean Hale at the Anchor before he walks out: %r %r" % (place, src))
    check(W.job_at(pid("Sean Hale"), (1993, 1))[0] == "pl-cafe13", "Sean at the café from 1992 (job.since)")
    check(W.job_at(pid("Jonah Scott"), (1986, 6))[0] == "pl-council", "Jonah at the council office (e-7478)")
    check(W.job_at(pid("Ken Scott"), (1986, 6))[0] == "pl-paper", "Ken at the Courier since 1976 (simulated)")
    check(W.job_at(pid("Leo Lyons"), DEC89)[0] is None, "Leo retired in April 1989 (e-6412)")
    check(W.job_at(pid("Olive Shaw"), (1986, 6))[0] is None, "Olive starts at the Anchor about 1988: 'after ten years' in 1998")


@test
def leads():
    lead, src, _ = W.lead_at("pl-bar", DEC89)
    check(lead == pid("Sean Hale") and src == ["e-7079", "e-7097"], "the Anchor's 1989 lead is Sean Hale: %r %r" % (lead, src))
    lead, src, _ = W.lead_at("pl-bar", W.end)
    check(lead == pid("Evan Newman") and src == ["e-7097"], "Evan leads it in 1999")
    lead, src, _ = W.lead_at("pl-cafe13", DEC89)
    check(lead == pid("Peter Lane") and src == ["e-6908"], "the café's 1989 owner is Peter Lane, from e-6908, not e-6545 or e-7137: %r" % (src,))
    check(W.lead_at("pl-cafe13", (1993, 1))[0] == pid("Lisa Myers"), "Lisa Myers owns it from 1992 (e-7138)")
    check(W.lead_at("pl-harbour", DEC89)[0] == pid("Oliver Brook"), "Oliver Brook leads the fleet")


@test
def habits_in_the_case_month():
    on, src = W.habit_on(pid("Hannah Tanner"), "every Friday", DEC89)
    check(on is True and src == ["e-6589"], "Hannah's Fridays run in December 1989, ended by e-6589: %r %r" % (on, src))
    check(W.habit_on(pid("Hannah Tanner"), "every Friday", (1990, 6))[0] is False, "and stop in January 1990")
    check(W.habit_on(pid("Olive Shaw"), "every Friday", DEC89) == (True, ["e-6590"]), "Olive's Fridays run until e-6590")
    check(W.habit_on(pid("Agnes Fielding"), "every Friday", DEC89)[0] is True, "Agnes never missed one")


@test
def presence():
    j = pid("Jonah Scott")
    check(W.present(j, (1995, 6))[0], "Jonah in town in 1995")
    check(not W.present(j, (1997, 6))[0], "Jonah away from April 1996 (e-8247)")
    check(W.present(j, (1998, 10))[0], "Jonah back in October 1998 (e-8939)")
    check(not W.present(pid("Peter Lane"), (1995, 1))[0], "Peter Lane left in June 1994 (e-7749)")
    check(W.present(pid("Andy Shaw"), (1998, 9))[0], "Andy Shaw alive in September 1998")
    check(W.present(pid("Agnes Fielding"), DEC89)[0] and not W.present(pid("Agnes Fielding"), (1990, 1))[0], "Agnes to December 1989")
    check(not W.present(pid("Una Waller"), (1989, 10))[0] and W.present(pid("Una Waller"), (1989, 11))[0], "Una from November 1989")


@test
def kin():
    check(W.kin_ok(pid("Peter Lane"), "mother", pid("Olive Shaw"), DEC89), "Olive is Peter Lane's mother")
    check(W.kin_ok(pid("Hannah Tanner"), "late wife", pid("Lily Tanner"), DEC89), "Lily is Hannah's late wife")
    check(not W.kin_ok(pid("Hannah Tanner"), "late wife", pid("Lily Tanner"), (1986, 1)), "but not late before July 1987")
    check(W.kin_ok(pid("Tom Vaughan"), "son", pid("Ken Scott"), DEC89), "Ken is Tom Vaughan's son")
    check(not W.kin_ok(pid("Ben Reed"), "son", pid("Sid Tanner"), DEC89), "Sid is not Ben Reed's son")
    agnes = pid("Agnes Fielding")
    check([k for k in W.kin(agnes) if not W.died(k) or W.died(k) > DEC89] == [], "Agnes has no living kin in the export")


@test
def casting_parsed_from_appendix_a():
    d = CAST["D"]
    check(d["late"] == pid("Tom Vaughan"), "D is the late Tom Vaughan's house")
    check(d["heirs"] == [pid("Ken Scott"), pid("Jonah Scott")], "his heirs are Ken and Jonah Scott: %r" % d["heirs"])
    c = dict(CAST["C"]["residents"])
    check(c.get(pid("Leo Lyons")) == "ground" and c.get(pid("Peter Lane")) == "upper", "C: Leo downstairs, Peter upstairs: %r" % c)
    check(CAST["A"]["tenants"] == [pid("Una Waller")], "Una takes A's attic")
    check([p for p, _ in CAST["E"]["residents"]] == [pid("Agnes Fielding")], "Agnes at E")
    check(W.person("Peter") == pid("Peter Lane"), "an ambiguous first name means the cast person")


# -- the case's sentences (derived parsing) ------------------------------------------------------------------------

@test
def the_anchors_lead_in_the_pitch():
    rep = sentence("The page gives Agnes no kin and points at the Anchor: its lead Evan Newman and about 30 regulars.")
    b = bad(rep, "case: a role or lead")
    check(len(b) == 1 and "Sean Hale" in b[0]["why"] and b[0]["sources"] == ["e-7079", "e-7097"], "Evan is not the 1989 lead: %r" % b)
    check(not bad(rep, "case: kin"), "Agnes has no kin: true")
    check(not bad(sentence("The Anchor's 1989 lead is rebuilt, since Evan Newman leads it in 1999.")), "Evan leads it in 1999")


@test
def the_cafes_owner_and_its_citation():
    rep = sentence("Its owner is Peter Lane of C (e-6545; he retires from it in 1992, e-7137).", para_place="pl-cafe13")
    check(not bad(rep, "case: a role or lead"), "Peter owns the café in 1989")
    b = bad(rep, "case: a citation supports its claim")
    check(len(b) == 1 and b[0]["sources"] == ["e-6908"], "the source is e-6908: %r" % b)
    check(not bad(rep, "case: a cited event's year"), "the year after a semicolon belongs to the next clause")
    rep = sentence("Peter Lane (p-41, 32) upstairs: owner of the Old Bank Café, and Olive Shaw's son")
    check(not bad(rep) and rep.checked["case: a role or lead"] == 1 and rep.checked["case: kin"] == 1 and
          rep.checked["case: an age"] == 1, "role, kin and age all true: %r %r" % (rep.items, rep.checked))


@test
def kin_and_pronouns():
    rep = sentence("Tell Peter Lane at house C first, and it can run to his mother Olive, then to Ben Reed, close to both women (e-6414, e-6400).")
    check(rep.checked["case: kin"] == 1 and not bad(rep, "case: kin"), "his mother Olive is Peter's: %r" % rep.items)
    rep = sentence("Ben Reed at her door (e-7322, e-8591); her son Sid \"at her side within the hour\" (e-7335, e-8710).",
                   prior=["Hannah Tanner", "Lily Tanner"])
    check(rep.checked["case: kin"] == 1 and not bad(rep, "case: kin"), "'her son' is Hannah's, not Ben Reed's: %r" % rep.items)
    rep = sentence("Hannah's late wife Lily (p-1) is named plainly if at all, never as story.")
    check(rep.checked["case: kin"] == 1 and not bad(rep), "Hannah's late wife Lily: %r" % rep.items)


@test
def ages_deaths_weekdays():
    check(not bad(sentence("Cast on them: Andy Shaw (p-17, 76), Hannah Tanner (p-2, 74) and Karen Holmes (p-4, 65).")), "ages true")
    check(bad(sentence("Hannah Tanner (p-2, 37) climbs the steps.")), "an age off by the shift is caught")
    check(not bad(sentence("Agnes Fielding (p-36, 103). She dies in December 1989, so the atlas moves the diary's 1993 forward")), "Agnes dies December 1989")
    rep = sentence("Redrawn: she dies in December 1989, not 1993 (e-6557); the house is empty from January 1990.", prior=["Agnes Fielding"])
    check(not bad(rep) and rep.checked["case: a death"] == 1, "a denied year is not a claim: %r" % rep.items)
    check(bad(sentence("Agnes Fielding dies in 1993.")), "a wrong death year is caught")
    check(not bad(sentence("Friday 15 December (authored), 10:00 to 18:00: find people and tell them.")), "15 December 1989 is a Friday")
    check(bad(sentence("Friday 16 December, 10:00 to 18:00.")), "16 December 1989 is not")
    check(not bad(sentence("Our one lit time is authored: 17:50 on Friday 20 October 1989.")), "20 October 1989 is a Friday")


@test
def labels():
    rep = sentence("The real lives. Canonical: illness, death, visits, habits, Olive's job. Authored: player, key, doctor.")
    b = bad(rep, "case: a label")
    check(len(b) == 1 and b[0]["sources"] == ["e-8736"], "Olive's job is derived from e-8736, not canonical: %r" % b)


@test
def cited_events():
    check(not bad(sentence("e-6593 (January 1990, private): Andy stops swimming at seven.")), "month, year and visibility")
    check(bad(sentence("e-6593 (February 1990, private): Andy stops swimming at seven.")), "a wrong month is caught")
    check(bad(sentence("e-6593 (January 2027, private): Andy stops swimming at seven.")), "an engine year is caught")
    check(bad(sentence("Hannah climbs past her own door to E (e-6531, checked: weekly in November, public).")), "a wrong visibility is caught")
    check(bad(sentence("A visit (e-99999).")), "a missing event is caught")


@test
def hours_against_habits():
    rep = sentence("Failure: Hannah hears it at the bar at 18:05, and your questions reached 6 people.")
    check(rep.checked["case: hours against habits"] == 1 and not bad(rep), "Hannah is at the bar on a Friday in December 1989")
    rep = sentence("At 18:00 the Anchor's Friday fills; she never missed one.", prior=["Agnes Fielding"])
    check(rep.checked["case: hours against habits"] == 1 and not bad(rep), "nor did Agnes: %r" % rep.items)


@test
def businesses_at_corner_houses():
    cb = lambda s, row=None, cafe=None: F.corner_business(s, row, cafe, 1989, 1999)  # noqa: E731
    check(cb("Role and goal. You run the café at house A (authored).") == ("A", 1989), "the pitch's café at A")
    check(cb("- 0–4: three November evenings at the café window, after her second heart attack (e-6527).", cafe="A") == ("A", 1989), "its window")
    check(cb("A café opened in 1988 by a couple with no engine life.", row="A") == ("A", 1988), "Appendix A's row")
    check(cb("Should the player work at Peter's café, or live at A with no trade?") == (None, None), "a question claims nothing")
    check(cb("A café at A run by the player would invent a business.") == (None, None), "a denial claims nothing")
    check(cb("Peter Lane, owner of the Old Bank Café.") == (None, None), "the engine's café")
    check(cb("a café in the shop (2000 to 2009)", row="A") == (None, None), "after the export: a stand-in")


@test
def unshifted_years():
    check(bad(sentence("Ben Reed came \"every week (2024)\" to Agnes.")), "an engine year quoted in our text")
    check(not bad(sentence("Years that were never shifted: \"every week (2024)\" in e-6400.")), "naming the bug is not making it")
    y = F.engine_years(W)
    check(y["texts"] == 136 and y["labels"] == 479, "136 event texts and 479 cause labels carry engine years: %r" % y)


# -- toy diaries from the lines the check found false -------------------------------------------------------------

@test
def toy_a_cafe_after_s():
    a = diary([dict(BUILT, year=1912), dict(year=1931, kind="shop_fitted", params=dict(cols=2), cause="a shop"),
               dict(year=1988, kind="business_opened", params=dict(kind="cafe", name="Kaffebrenneriet"),
                    cause="a young couple open a café in the empty shop; the rent is low after the crash")], 104)
    b = bad(diary_findings("A", a), "diary: a business opened after S")
    check(len(b) == 1, "the 1988 café is a shop the engine lacks: %r" % b)
    a["events"][2]["year"] = 2000
    check(not bad(diary_findings("A", a)), "a café after the export is a stand-in")
    a["events"][2]["year"] = 1931
    check(not bad(diary_findings("A", a)), "a shop before S is ours")


@test
def toy_d_heirs_in_oslo():
    d = diary([BUILT, dict(year=1986, kind="boarded", params=dict(scope="all"), cause="the owner dies; the heirs live in Oslo"),
               dict(year=1995, kind="neglected", params=dict(amount=200), cause="still empty; the heirs cannot agree to sell, and the roof lets in water")])
    rep = diary_findings("D", d)
    deaths, heirs = bad(rep, "diary: a death"), bad(rep, "diary: heirs")
    check(len(deaths) == 1 and "November 1985" in deaths[0]["why"], "Tom Vaughan died in 1985, not 1986: %r" % deaths)
    check(any("Ken Scott" in h["why"] and h["verdict"] == "contradiction" for h in heirs), "the heirs live in the town: %r" % heirs)
    check(any(h["verdict"] == "unsupported" for h in heirs), "'cannot agree' has no event behind it")
    d["events"][1]["cause"] = "the owner died at the end of 1985; the house is shut up and boarded"
    d["events"][2]["cause"] = "still empty, and the roof lets in water"
    check(not bad(diary_findings("D", d)), "the fixed lines are clean")


@test
def toy_e_dies_1993():
    e = diary([BUILT, dict(year=1993, kind="neglected", params=dict(amount=600),
                           cause="the last owner dies; the heirs live away and leave the house empty")], 304)
    rep = diary_findings("E", e)
    check(any("December 1989" in x["why"] for x in bad(rep, "diary: a death")), "Agnes died in December 1989: %r" % rep.items)
    check(any(x["verdict"] == "unsupported" for x in bad(rep, "diary: heirs")), "Agnes has no kin to be heirs")
    e["events"][1]["cause"] = "empty since its last owner died in December 1989; nobody takes it on, and it is let go"
    check(not bad(diary_findings("E", e)), "the fixed line is clean")
    e["events"][1]["year"] = 1989
    e["events"][1]["cause"] = "empty"
    check(bad(diary_findings("E", e), "diary: an empty house"), "empty in 1989 while Agnes lives there is caught")


@test
def toy_b_bakery_in_seed_b():
    real = json.load(open(F.DIARIES))["real"]
    b = copy.deepcopy(real["B"])
    for ev in b["events"]:
        if ev["kind"] in ("shop_fitted", "business_opened"):
            ev["year"] = 1997
    rep = F.Report()
    F.resolved_states(W, {"B": b}, CAST, rep, "toy", "diary", WS)
    check(bad(rep, "state: a business at a corner house"), "a bakery open at B in 1998 is caught: %r" % rep.items)
    check(len(bad(diary_findings("B", b), "diary: a business opened after S")) == 2, "and both its events")


@test
def the_real_diaries_are_clean():
    rep, _ = F.run(W, json.load(open(F.DIARIES)))
    diary_bad = [it for it in rep.items if it["kind"] == "diary" and it["verdict"] != "note"]
    check(not diary_bad, "diaries.json's real arm agrees with the export: %r" % diary_bad)
    open_ = [it for it in rep.items if it["verdict"] != "note" and (it["kind"] in ("diary", "case") or not F.route_for(it))]
    check(not open_, "everything else has a routed fix: %r" % open_)
    check(rep.checked["export: the town's cafés"] == 2 and not bad(rep, "export: the town's cafés"), "one café in 1989 and 1998")


def main():
    for ok, name, why in RESULTS:
        print("%s %s%s" % ("ok  " if ok else "FAIL", name, "" if ok else ": " + why))
    n_bad = sum(1 for ok, _, _ in RESULTS if not ok)
    print("%d of %d passed (Python %s)" % (len(RESULTS) - n_bad, len(RESULTS), sys.version.split()[0]))
    return 1 if n_bad else 0


if __name__ == "__main__":
    sys.exit(main())
