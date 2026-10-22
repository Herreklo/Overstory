#!/usr/bin/env python3
"""Test 5 of the playable corner's ladder: do the facts agree? (`reviews/lt1/playable/outline.md` §3.)

    python3 tools/playable/facts.py [--json out.json] [--all]

Checks what our authored layer states against the engine's export (`fixtures/engine/understory-world-9989.json`),
by class rather than by a list:
- every field of every event in the five houses' diaries (`reviews/lt1/time/readers/diaries.json`, the arm "real";
  the arm "shuffled" is LT1f's control, false by design, and is only counted) gets a class, and the classes that
  can state a fact are checked: a business at a house, a death, heirs, an empty house, a sale;
- each house's resolved state at the cases' months (seed A, December 1989; seed B, September and October 1998);
- every showable string of the case's documents is scanned for the kinds of claim it can make: a role or lead, a job,
  a kin tie, an age, a death, a cited event and its month, year and visibility, a weekday, an hour against jobs and
  habits, a business at a corner house, a person present at a case's month;
- the engine's own strings: every year it wrote is an engine year, never shifted (counted, an engine matter);
- the upstream copies of the diaries (`fixtures/lt1-corner.json`, `fixtures/records/bld-104.json`) and the heart
  layout's strings, which a later regeneration would carry back.

Labels. `simulated`: read straight from the export. `derived`: rebuilt from it by a stated rule; everything parsed
from free text (job moves, leads, habits, the case's sentences) is derived, and each parser has a test in
`tools/tests/test_facts.py`.

Exit 1 if a contradiction is left in the diaries, or anywhere else without a routed fix (ROUTES).
"""

import argparse
import calendar
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXPORT = ROOT / "fixtures" / "engine" / "understory-world-9989.json"
DIARIES = ROOT / "reviews" / "lt1" / "time" / "readers" / "diaries.json"
CORNER = ROOT / "fixtures" / "lt1-corner.json"
RECORD_104 = ROOT / "fixtures" / "records" / "bld-104.json"
HEART_LAYOUT = ROOT / "blender" / "blockouts" / "heart_layout.py"
RESOLVER = ROOT / "blender" / "resolver"

SHOW = 1989  # the show year: the engine's presentFrom
S = 1959     # the people's start year (FC2, #23): the engine's 1996
MONTHS = [None, "January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
          "November", "December"]
MONTH_RE = "|".join(MONTHS[1:])
WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
VIS = ("private", "local", "public")

# The cases' months: seed A is Agnes Fielding (December 1989, the window evenings in November); seed B is Andy Shaw
# (October 1998, e-8899; his visitors in September, e-8881 to e-8883).
SEEDS = {"A": [(1989, 11), (1989, 12)], "B": [(1998, 9), (1998, 10)]}
CORNER_IDS = {"A": 104, "B": 105, "C": 1203, "D": 1107, "E": 304}

# Names the case uses for engine places (the export's own names are always accepted).
PLACE_ALIASES = {"the bar": "pl-bar", "the fleet": "pl-harbour", "the café": "pl-cafe13", "the cafe": "pl-cafe13"}
# The role word each place's lead goes by in the engine's own text (promoted, stepdown, want:lapsed).
LEAD_WORDS = {"lead", "leader", "owner", "manager", "skipper", "head mechanic", "chief officer", "editor"}

NUMBER_WORDS = {w: i for i, w in enumerate(
    "zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen "
    "eighteen nineteen twenty".split())}

# The case's documents: (path, first line that starts the section or None, line that ends it or None, kind).
# "case" is the case itself and allows no routed fix; "record" is a design record whose contradictions are fixed by
# the route named in ROUTES (the case spec is written from them before test 1 freezes).
DOCS = [
    ("reviews/lt1/playable/case-spec.md", None, None, "case"),
    ("reviews/lt1/playable/pick.md", None, None, "record"),
    ("reviews/lt1/playable/outline.md", "### 5. Do the facts agree?", "### The order and the total", "record"),
    ("reviews/lt1/playable/outline.md", "## 6. Open questions", "## 7.", "record"),
    ("reviews/lt1/playable/premortem.md", None, None, "record"),
    ("reviews/lt1/playable/pitches.md", "## Appendix A", "### B. Chains from real lives", "record"),
    ("reviews/lt1/playable/pitches.md", "#### 1. Before Friday", "#### 2.", "record"),
    ("docs/experiments.md", "## LT1g", "## LT1, the building blocks", "record"),
    ("reviews/lt1/playtests/paper-1/world/atlas-9989.md", "## Casting the corner", "## Six corners", "record"),
]

# The fix for each contradiction outside the diaries, matched by file and a piece of the claim's text.
# (file suffix, text piece, fix, cost)
ROUTES = [
    ("pitches.md", "You run the café at house A",
     "case spec: the player lives at A with no trade (option H) or works at Peter's café (option W); never a café of their own",
     "the play question of outline.md §6 item 2; H costs nothing, W adds an authored coworker"),
    ("pitches.md", "café window",
     "case spec: \"the window at A\" (A's empty shop window, or the attic's)", "wording; the vantage is the same glass"),
    ("pitches.md", "A café opened in 1988",
     "Appendix A: \"the ironmonger's 1931 shop, empty since 1974\"", "wording; the record is history, the case spec carries it"),
    ("pitches.md", "its lead Evan Newman",
     "case spec: the Anchor's lead in December 1989 is Sean Hale (derived from e-7079 and e-7097); Evan Newman is bar staff",
     "the page's answer is Sean; the spread's 'tell the lead' bot targets Sean"),
    ("pitches.md", "Tell Peter Lane at house C first",
     "case spec: between 10:00 and 18:00 Peter Lane is at the Old Bank Café, which he owns (derived), 3.5 min away; at C only before and after",
     "the hours table places him; 'Peter first' costs the walk to the square"),
    ("pitches.md", "Canonical: illness, death, visits, habits, Olive's job",
     "case spec: Olive's job at the Anchor is derived (e-8736, \"after ten years\"; no hire event)", "a label"),
    ("outline.md", "Its owner is Peter Lane of C (e-6545",
     "cite e-6908 (\"will step down as owner\", March 1991) with e-7137; e-6545 is Peter backing Lisa Myers, not ownership",
     "a citation; the premortem's claim check already says so"),
    ("atlas-9989.md", "a café in the 1931 shop, opened 1988",
     "atlas: the diary column follows diaries.json (the shop empty from 1974; the café 2000 to 2009)",
     "wording; the cast column already gives the café no engine life"),
    ("atlas-9989.md", "the owners let the ground floor as a bakery 1997",
     "atlas: the bakery opens in 2000, after the export ends", "wording"),
    ("atlas-9989.md", "lights A's café",
     "atlas: the 1989 evening lights A's attic (Una Waller's from November) and leaves the shop dark", "wording"),
    ("atlas-9989.md", "bakery",
     "atlas: B's bakery opens in 2000, after the export ends; Agnes Tanner seen at B from 1997 stays, without it",
     "wording"),
    ("atlas-9989.md", "the owner dies and the heirs live away",
     "atlas: the diary column follows diaries.json (Tom Vaughan died in November 1985; the house shut up and boarded)",
     "wording; the cast column already redraws it"),
    ("atlas-9989.md", "empty when its last owner dies (1993)",
     "atlas: \"empty from its last owner's death (December 1989), let go by 1993\"", "wording; the cast column already redraws it"),
    ("lt1-corner.json", "", "upstream: carry diaries.json's real arm back into corner_fixture.py, then lt1-corner.json; "
     "until then never rerun time_key.py, which would undo the fixes", "one edit in corner_fixture.py's RULES and houses"),
    ("bld-104.json", "", "golden record probe: leave as test data or regenerate from the fixed fixture with its baseline",
     "a golden baseline update, if regenerated"),
    ("heart_layout.py", "", "W1: A's shop is empty and dark in 1989 (shop=\"empty\"), the label \"A (104)\"",
     "two lines; the lit evening loses one warm window"),
]


# -- the export ----------------------------------------------------------------------------------------------------

class World:
    """The export, with town dates (engine year + shift) and the rosters derived from its event text."""

    def __init__(self, data):
        self.data = data
        self.shift = SHOW - data["presentFrom"]["year"]
        self.people = {p["id"]: p for p in data["people"]}
        self.by_name = {p["name"]: p["id"] for p in data["people"]}
        firsts = Counter(n.split()[0] for n in self.by_name)
        self.by_first = {n.split()[0]: pid for n, pid in self.by_name.items() if firsts[n.split()[0]] == 1}
        self.places = {p["id"]: p for p in data["places"]}
        self.place_by_name = {p["name"].lower(): p["id"] for p in data["places"]}
        self.place_by_name.update(PLACE_ALIASES)
        self.events = sorted(data["events"], key=lambda e: (e["at"]["year"], e["at"]["month"], int(e["id"][2:])))
        self.by_id = {e["id"]: e for e in self.events}
        self.end = self.ym(data["at"])
        self.events_from = self.ym(data["eventsFrom"])
        self._moves = None
        self.cast_pids = set()  # the corner's cast (set by casting()): an ambiguous first name means the cast one

    def ym(self, at):
        return (at["year"] + self.shift, at.get("month") or 1)

    def when(self, e):
        return self.ym(e["at"])

    def name(self, pid):
        return self.people[pid]["name"]

    def person(self, ref):
        """A person from "p-36", a full name, or a first name only one person has; None if unknown or ambiguous."""
        ref = ref.strip()
        if re.fullmatch(r"p-\d+", ref):
            return ref if ref in self.people else None
        hit = self.by_name.get(ref) or self.by_first.get(ref)
        if hit is None and " " not in ref:
            cast = [pid for n, pid in self.by_name.items() if n.split()[0] == ref and pid in self.cast_pids]
            hit = cast[0] if len(cast) == 1 else None
        return hit

    def place(self, text):
        return self.place_by_name.get(text.strip().lower())

    # people (simulated, with derived presence)

    def age(self, pid, ym):
        by, bm = self.ym(self.people[pid]["born"])
        return ym[0] - by - (1 if ym[1] < bm else 0)

    def died(self, pid):
        d = self.people[pid].get("died")
        return self.ym(d) if d else None

    def present(self, pid, ym):
        """(alive and in the town at ym, sources). The month of a death counts as present. Derived from the export's
        status walked back over arrived, left and home events."""
        p = self.people[pid]
        if ym < self.ym(p["born"]):
            return False, []
        d = self.died(pid)
        if d and d < ym:
            return False, []
        here = p["status"] in ("in", "dead")
        srcs = []
        for e in reversed(self.events):
            if self.when(e) <= ym:
                break
            if not e["who"] or e["who"][0] != pid:
                continue
            if e["type"] == "left":
                here, srcs = True, srcs + [e["id"]]
            elif e["type"] in ("arrived", "home"):
                here, srcs = False, srcs + [e["id"]]
        return here, srcs

    # jobs (derived: parsed from event text)

    def moves(self):
        """Every job event, parsed: {pid: [(ym, kind, place, to, role, eid)]} in time order. Derived."""
        if self._moves is None:
            out = defaultdict(list)
            for e in self.events:
                m = parse_job(e, self)
                if m:
                    pid, kind, place, to, role = m
                    out[pid].append((self.when(e), kind, place, to, role, e["id"]))
            self._moves = out
        return self._moves

    def job_at(self, pid, ym):
        """(place id or None or "?", sources): where pid works at ym, walked back from the export's job over the
        parsed job events, with the export's job.since as a start. Derived when any event is used."""
        p = self.people[pid]
        job = p.get("job")
        place = job["place"] if job and p["status"] != "away" else None
        since = self.ym(job["since"]) if job and job.get("since") else None
        srcs = []
        steps = [(t, k, pl, to, role, eid) for (t, k, pl, to, role, eid) in self.moves().get(pid, []) if t > ym]
        if place and since and since > ym:
            steps.append((since, "since", place, place, None, "job.since"))
        for (t, k, pl, to, role, eid) in list(steps):
            n = retired_years(self.by_id[eid]["text"]) if k == "retired" else None
            if n is not None and (t[0] - n, t[1]) > ym:  # "retired after N years": not there yet at ym
                steps.append(((t[0] - n, t[1]), "since", pl, pl, None, eid + " (started)"))
        steps.sort(key=lambda s: (s[0], 0 if s[1] == "since" else 1))
        for (t, k, pl, to, role, eid) in reversed(steps):
            if k in ("hired", "arrived", "since"):
                place = None
            elif k in ("retired", "startover", "moved", "dismiss"):
                place = pl
            elif k in ("promoted", "stepdown"):
                place = pl
            elif k in ("left", "take"):
                place = "?"
            srcs.append(eid)
        if p["status"] == "dead" and not srcs and self.died(pid) and self.died(pid) < ym:
            place = None
        return place, srcs

    def departures(self, place):
        """[(ym, pid, eid)]: people leaving a place by retiring, walking out, moving, being let go, or dying. Derived."""
        out = []
        for pid, ms in self.moves().items():
            for (t, k, pl, to, role, eid) in ms:
                if k in ("retired", "startover", "moved", "dismiss") and pl == place:
                    out.append((t, pid, eid))
        for e in self.events:
            if e["type"] == "death":
                pid = e["who"][0]
                if self.job_at(pid, self.when(e))[0] == place:
                    out.append((self.when(e), pid, e["id"]))
        return sorted(out)

    def lead_at(self, place, ym):
        """(pid or None, sources, rule): the place's lead at ym. Derived by these rules, in order:
        1. the latest promotion at the place at or before ym;
        2. else the first evidence after ym: a step-down names the lead; a promotion names whoever left the place
           last before it (the engine promotes when the lead goes);
        3. else the export's lead, if their job at the place started by ym."""
        promos, downs = [], []
        for pid, ms in self.moves().items():
            for (t, k, pl, to, role, eid) in ms:
                if pl == place and k == "promoted":
                    promos.append((t, pid, eid))
                if pl == place and k == "stepdown":
                    downs.append((t, pid, eid))
        promos.sort()
        downs.sort()
        before = [x for x in promos if x[0] <= ym]
        if before:
            t, pid, eid = before[-1]
            return pid, [eid], "the latest promotion"
        after = [x for x in promos if x[0] > ym]
        downs_after = [x for x in downs if x[0] > ym]
        if downs_after and (not after or downs_after[0][0] <= after[0][0]):
            t, pid, eid = downs_after[0]
            return pid, [eid], "the next step-down names the lead"
        if after:
            t, pid, eid = after[0]
            gone = [d for d in self.departures(place) if ym < d[0] <= t and d[1] != pid]
            if gone:
                return gone[-1][1], [gone[-1][2], eid], "the last to leave before the next promotion"
            return None, [eid], "a promotion with no departure before it"
        lead = self.places[place].get("lead")
        if lead and self.job_at(lead, ym)[0] == place:
            return lead, [], "the export's lead, at the place by then"
        return None, [], "unknown"

    # habits (derived: parsed from event text)

    def habit_on(self, pid, core, ym):
        """(True, False or None, sources): whether pid's habit whose label contains `core` runs at ym. The latest
        habit event at or before ym decides; else the first after it (a habit that stops later was running); else
        the export's habit record (only its latest run is kept)."""
        hits = []
        for e in self.events:
            if not e["who"] or e["who"][0] != pid:
                continue
            h = parse_habit(e, self.name(pid))
            if h and core.lower() in h[1].lower():
                hits.append((self.when(e), h[0], e["id"]))
        past = [x for x in hits if x[0] <= ym]
        if past:
            return past[-1][1] == "on", [past[-1][2]]
        future = [x for x in hits if x[0] > ym]
        if future:
            return future[0][1] == "off", [future[0][2]]
        for hb in self.people[pid].get("habits", []):
            if core.lower() in hb["label"].lower():
                since = self.ym(hb["since"]) if hb.get("since") else None
                broken = self.ym(hb["broken"]) if hb.get("broken") else None
                return (since is None or since <= ym) and (broken is None or broken > ym), []
        return None, []

    # kin (simulated)

    def kin_ok(self, a, rel, b, ym):
        """Is b a's `rel` (b is a's son, wife, mother...) by the export? rel may start with "late "."""
        rel = rel.lower()
        late = rel.startswith("late ")
        rel = rel[5:] if late else rel
        pa, pb = self.people[a], self.people[b]
        sexed = {"son": "m", "daughter": "f", "mother": "f", "father": "m", "wife": "f", "husband": "m",
                 "widow": "f", "widower": "m"}
        if rel in sexed and pb["sex"] != sexed[rel]:
            return False
        if rel in ("son", "daughter", "child"):
            ok = b in pa.get("kids", []) or a in pb.get("parents", [])
        elif rel in ("mother", "father", "parent"):
            ok = b in pa.get("parents", []) or a in pb.get("kids", [])
        elif rel in ("wife", "husband", "partner"):
            ok = (pa.get("partner") or {}).get("id") == b or (pb.get("partner") or {}).get("id") == a
        elif rel in ("widow", "widower"):
            ok = ((pa.get("partner") or {}).get("id") == b or (pb.get("partner") or {}).get("id") == a) and \
                 bool(self.died(a)) and self.died(a) <= ym
        else:
            return False
        if late:
            ok = ok and bool(self.died(b)) and self.died(b) <= ym
        return ok

    def kin(self, pid):
        """The export's kin of pid: partner, kids, parents."""
        p = self.people[pid]
        out = list(p.get("kids", [])) + list(p.get("parents", []))
        if p.get("partner"):
            out.append(p["partner"]["id"])
        for q in self.people.values():
            if (q.get("partner") or {}).get("id") == pid and q["id"] not in out:
                out.append(q["id"])
        return [x for x in out if x in self.people]


JOB_RES = [
    ("hired", r"^{w} started work at (?P<place>.+?)\.$"),
    ("retired", r"^{w} retired after (?P<n>\w+) years? at (?P<place>.+?)\.$"),
    ("startover", r"^{w} walked out of (?P<place>.+?) to start again somewhere else\.$"),
    ("moved", r"^{w} left (?P<place>the (?!town).+?) for a start at (?P<to>.+?)\.$"),
    ("arrived", r"^{w} moved to the town for a job at (?P<to>[^,.]+)"),
    ("promoted", r"^{w} became (?P<role>.+?) at (?P<place>.+?)\.$"),
    ("stepdown", r"^{w} will step down as (?P<role>.+?) at (?P<place>.+?) next year\.$"),
    ("take", r"^{w} took a job in the city\."),
    ("left", r"^{w} left (?:the town )?for "),
]


def parse_job(e, world):
    """(pid, kind, place, to, role) for a job event, or None. Derived from the event's text: the export gives no
    place field. "dismiss" names the boss first and the one let go second."""
    t = e.get("type")
    if t == "dismiss" and len(e["who"]) > 1:
        m = re.match(r"^.+? let (?P<w>.+?) go from (?P<place>.+?)\.$", e["text"])
        if m:
            return e["who"][1], "dismiss", world.place(m.group("place")), None, None
        return None
    if t not in {k for k, _ in JOB_RES} or not e["who"]:
        return None
    pid = e["who"][0]
    w = re.escape(world.name(pid))
    for kind, pat in JOB_RES:
        if kind != t:
            continue
        m = re.match(pat.format(w=w), e["text"])
        if not m:
            return None
        g = m.groupdict()
        place = world.place(g["place"]) if g.get("place") else None
        to = world.place(g["to"]) if g.get("to") else None
        return pid, kind, place, to, g.get("role")
    return None


def parse_habit(e, name):
    """("on"/"off", label) for a habit event's text, or None. Derived. The engine writes "X now ...", "X is now ...",
    "Once again, X ...", "X no longer ..." and "X is no longer ..."."""
    if e.get("type") not in ("takeup", "habit:new", "habit:back", "habit:broke", "keepaway"):
        return None
    n = re.escape(name)
    for state, pat in (("on", r"^Once again, {n} (?:is )?(?P<l>.+?)\.$"), ("off", r"^{n} (?:is )?no longer (?P<l>.+?)\.$"),
                       ("on", r"^{n} (?:is )?now (?P<l>.+?)\.$")):
        m = re.match(pat.format(n=n), e["text"])
        if m:
            return state, m.group("l")
    return None


def retired_years(text):
    """The N of "retired after N years", as a number (words or digits). Derived."""
    m = re.search(r"retired after (\w+) years?", text)
    if not m:
        return None
    w = m.group(1).lower()
    return int(w) if w.isdigit() else NUMBER_WORDS.get(w)


# -- findings ------------------------------------------------------------------------------------------------------

class Report:
    def __init__(self):
        self.items = []
        self.checked = Counter()

    def add(self, cls, where, claim, verdict, why, sources=(), label="derived", kind="record"):
        self.checked[cls] += 1
        if verdict != "ok":
            self.items.append(dict(cls=cls, where=where, claim=claim, verdict=verdict, why=why, sources=list(sources),
                                   label=label, kind=kind))

    def ok(self, cls):
        self.checked[cls] += 1


class Prefixed:
    """A Report whose class names carry a prefix (the upstream copies' findings apart from the diaries')."""

    def __init__(self, rep, prefix):
        self.rep, self.prefix = rep, prefix
        self.checked = _PrefixedCounter(rep.checked, prefix)

    def add(self, cls, *a, **k):
        self.rep.add(self.prefix + cls, *a, **k)

    def ok(self, cls):
        self.rep.ok(self.prefix + cls)


class _PrefixedCounter:
    def __init__(self, c, prefix):
        self.c, self.prefix = c, prefix

    def __getitem__(self, k):
        return self.c[self.prefix + k]

    def __setitem__(self, k, v):
        self.c[self.prefix + k] = v


def route_for(item):
    where = item["where"]
    for suffix, piece, fix, cost in ROUTES:
        if where.split(":")[0].endswith(suffix) and piece in item["claim"]:
            return fix, cost
    return None


# -- the diaries ---------------------------------------------------------------------------------------------------

FORM_PARAMS = {"era", "storeys", "wealth", "roof", "cols", "windows", "scope", "side", "amount", "by", "with", "swatch"}


def casting(world):
    """{letter: dict(residents=[(pid, floor)], late=pid, heirs=[pid], tenants=[pid])} from pitches.md Appendix A's
    table: bold names in the cast cell; "The late X's house"; "heirs are X and Y Surname"; "takes the attic" is a
    tenant; "upstairs"/"downstairs" after a name is its floor. Derived (parsed) and authored (the casting)."""
    text = (ROOT / "reviews/lt1/playable/pitches.md").read_text(encoding="utf-8")
    out = {}
    for line in text.splitlines():
        m = re.match(r"^\| \*\*([A-E])\*\* \((\d+)\) \| [^|]* \| (.*) \|$", line)
        if m:
            out[m.group(1)] = parse_cast_cell(m.group(3), world)
    for line in text.splitlines():
        if line.startswith("**The Gully Steps**") or line.startswith("**On Harbour Row:**"):
            world.cast_pids.update(world.person(n) for n in re.findall(r"\*\*([A-Z]\w+ [A-Z]\w+)\*\*", line))
    for c in out.values():
        world.cast_pids.update(pid for pid, _ in c["residents"])
        world.cast_pids.update(c["heirs"])
    world.cast_pids.discard(None)
    return out


def parse_cast_cell(cell, world):
    c = dict(residents=[], late=None, heirs=[], tenants=[])
    m = re.search(r"The late ([A-Z]\w+ [A-Z]\w+)'s house", cell)
    if m:
        c["late"] = world.person(m.group(1))
    m = re.search(r"heirs are ([A-Z]\w+(?: [A-Z]\w+)?) and ([A-Z]\w+) ([A-Z]\w+)", cell)
    if m:
        first = m.group(1) if " " in m.group(1) else m.group(1) + " " + m.group(3)
        c["heirs"] = [x for x in (world.person(first), world.person(m.group(2) + " " + m.group(3))) if x]
    for m in re.finditer(r"\*\*([A-Z]\w+ [A-Z]\w+)\*\*([^.*]*)", cell):
        pid = world.person(m.group(1))
        if not pid:
            continue
        tail = m.group(2)
        floor = "upper" if "upstairs" in tail else "ground" if "downstairs" in tail else None
        c["residents"].append((pid, floor))
        if "takes the attic" in tail or "lodger" in tail:
            c["tenants"].append(pid)
    return c


def owner_of(cast, scope=None):
    """The person a diary's "owner" means: the late owner, else the residents who are not tenants (of the floor
    named, if any)."""
    if cast.get("late"):
        return [cast["late"]]
    return [pid for pid, fl in cast.get("residents", []) if pid not in cast.get("tenants", []) and (scope is None or fl == scope)]


DEATH_RE = re.compile(r"\b(?:last )?owner (?P<v>dies|died)\b(?:[^;.]*?\b(?:in|at the end of) (?:(?P<m>" + MONTH_RE + r") )?(?P<y>\d{4}))?")


def diary_claims(world, letter, d, cast, rep, where, kind, ws=None):
    """Every field of one diary, classed and, where it can state a fact, checked."""
    rep = Prefixed(rep, "upstream " if kind == "upstream" else "")
    for k in d:
        if k in ("events",):
            continue
        rep.checked["field: house " + k] += 1
    for ev in d["events"]:
        y = ev["year"]
        band = "before S" if y < S else ("engine window" if (y, 1) <= world.end else "after the export")
        tag = "{}:{}:{} {} {}".format(where, letter, ev["id"], y, ev["kind"])
        for k in ev:
            rep.checked["field: event " + k] += 1
        for k in ev.get("params", {}):
            rep.checked["field: param " + (k if k in FORM_PARAMS else k + " (fact)")] += 1
        rep.checked["band: " + band] += 1
        cause = ev.get("cause", "")
        # a business at a house
        if ev["kind"] in ("business_opened", "shop_fitted"):
            if band == "engine window":
                bkind = ev["params"].get("kind", "shop")
                match = [v for v in world.data["ventures"] if v["kind"] == bkind and world.ym(v["since"])[0] == y]
                rep.add("diary: a business opened after S", tag, cause or bkind,
                        "ok" if match else "contradiction",
                        "the engine owns openings after S and has no {} opening in {} (its ventures: {}); a shop the "
                        "engine lacks is stripped or never fitted (facts contract)".format(
                            bkind, y, ", ".join(sorted({v["kind"] for v in world.data["ventures"]}))),
                        [v["id"] for v in match], "simulated", kind)
            else:
                rep.ok("diary: a business outside the engine window")
        if band != "engine window":
            rep.ok("diary: text outside the engine window (ours, or a stand-in)")
            continue
        # a death
        m = DEATH_RE.search(cause)
        if m:
            owners = owner_of(cast)
            for pid in owners:
                dd = world.died(pid)
                if not dd:
                    rep.add("diary: a death", tag, cause, "contradiction",
                            "{} does not die in the export".format(world.name(pid)), [], "simulated", kind)
                    continue
                said_y = int(m.group("y")) if m.group("y") else y
                said_m = MONTHS.index(m.group("m")) if m.group("m") else None
                ok = said_y == dd[0] and (said_m is None or said_m == dd[1])
                rep.add("diary: a death", tag, cause, "ok" if ok else "contradiction",
                        "{} died in {} {}; the line puts the death in {}".format(
                            world.name(pid), MONTHS[dd[1]], dd[0], said_y), [death_event(world, pid)], "simulated", kind)
        # heirs
        if re.search(r"\bheirs?\b", cause):
            owners = owner_of(cast)
            heirs = cast.get("heirs") or [k for o in owners for k in world.kin(o) if world.present(k, (y, 6))[0]]
            if not owners:
                rep.add("diary: heirs", tag, cause, "unsupported", "no owner is cast", [], "derived", kind)
            elif not heirs:
                rep.add("diary: heirs", tag, cause, "unsupported",
                        "{} has no living kin in the export; heirs are request 31".format(
                            ", ".join(world.name(o) for o in owners)), [], "simulated", kind)
            else:
                here = [h for h in heirs if world.present(h, (y, 6))[0]]
                if re.search(r"heirs? (?:live|lives) (?:in|away)", cause) and here:
                    rep.add("diary: heirs", tag, cause, "contradiction",
                            "the heirs {} live in the town in {}".format(
                                " and ".join(world.name(h) + job_words(world, h, (y, 6)) for h in here), y),
                            [], "derived", kind)
                if re.search(r"\b(?:cannot|can't|could not) agree\b|\bquarrel|\bfall out\b", cause):
                    rep.add("diary: heirs", tag, cause, "unsupported",
                            "a claim about engine people after S with no event behind it (FC3): no event joins {}".format(
                                " and ".join(world.name(h) for h in heirs)), [], "derived", kind)
        # an empty house
        if re.search(r"\bempty\b", cause) or ev["kind"] == "boarded":
            for pid, fl in cast.get("residents", []):
                if world.present(pid, (y, 6))[0] and world.present(pid, (y, 12))[0]:
                    rep.add("diary: an empty house", tag, cause, "contradiction",
                            "{} is cast at {} and lives in the town all of {}".format(world.name(pid), letter, y),
                            [], "derived", kind)
            rep.ok("diary: an empty house")
        # a sale
        if re.search(r"\bnew owners?\b|\bbuys?\b|\bbought\b", cause):
            scope = "upper" if "upper flat" in cause else "ground" if "ground-floor" in cause else None
            for pid, fl in cast.get("residents", []):
                if pid in cast.get("tenants", []) or (scope and fl != scope):
                    continue
                if not world.present(pid, (y, 6))[0]:
                    rep.ok("diary: a sale")
                    continue
                own = [a for a in world.people[pid].get("attachments", []) if "house of" in a.get("label", "")]
                sup = [a for a in own if a.get("since") and world.ym(a["since"])[0] == y]
                rep.add("diary: a sale", tag, cause, "ok" if sup or not own else "contradiction",
                        "{} {}".format(world.name(pid), "has \"a house of their own\" from {}".format(y) if sup else
                                       "owns a house of their own since {} and stays".format(
                                           world.ym(own[0]["since"])[0] if own else "?")), [], "simulated", kind)


def death_event(world, pid):
    for e in world.events:
        if e["type"] == "death" and e["who"][0] == pid:
            return e["id"]
    return "died (record)"


def job_words(world, pid, ym):
    place, _ = world.job_at(pid, ym)
    if place and place != "?":
        return " (at {})".format(world.places[place]["name"])
    return ""


def resolved_states(world, diaries, cast_all, rep, where, kind, ws):
    """Each house resolved at the cases' months: no business the engine lacks; no cast resident in a boarded house."""
    sys.path[:0] = [str(RESOLVER), str(ROOT / "blender" / "generators")]
    from resolve import resolve  # noqa: E402
    for seed, months in SEEDS.items():
        year = months[-1][0]
        for letter, d in sorted(diaries.items()):
            plan = resolve(d, year, ws)
            tag = "{}:{} at {} (seed {})".format(where, letter, year, seed)
            if plan is None:
                rep.add("state: a house stands", tag, "", "contradiction", "the house does not stand", [], "derived", kind)
                continue
            b = plan.get("business")
            if b and b["opened"] >= S:
                rep.add("state: a business at a corner house", tag, "{} {} (opened {})".format(b["kind"], b["name"], b["opened"]),
                        "contradiction", "open at {} but not an engine venture".format(year), [], "derived", kind)
            else:
                rep.ok("state: a business at a corner house")
            cast = cast_all.get(letter, {})
            for pid, fl in cast.get("residents", []):
                live = world.present(pid, months[0])[0]
                if live and plan.get("boarded"):
                    rep.add("state: a cast resident in a boarded house", tag, world.name(pid), "contradiction",
                            "boarded while {} lives there".format(world.name(pid)), [], "derived", kind)
                else:
                    rep.ok("state: a cast resident in a boarded house")


# -- the case's strings --------------------------------------------------------------------------------------------

def doc_units(path, start, stop):
    """[(line number, text)]: the section's lines, table rows split into cells; markdown emphasis kept."""
    p = ROOT / path
    if not p.exists():
        return None
    lines = p.read_text(encoding="utf-8").splitlines()
    on = start is None
    out = []
    for i, line in enumerate(lines, 1):
        if start is not None and line.startswith(start):
            on = True
        elif stop is not None and on and line.startswith(stop) and i > 1 and out:
            break
        if on:
            out.append((i, line))
    return out


def sentences(text):
    return [s for s in re.split(r"(?<=[.!?])\s+(?=[A-Z*(])", text) if s.strip()]


def plain(s):
    return s.replace("**", "").replace("*", "").replace("`", "")


class Names:
    """Finds people and places in a string. Full names first, then first names only one person has, then p-ids."""

    def __init__(self, world):
        self.w = world
        full = sorted(world.by_name, key=len, reverse=True)
        self.full_re = re.compile(r"\b(" + "|".join(re.escape(n) for n in full) + r")\b")
        self.firsts = dict(world.by_first)
        for n, pid in world.by_name.items():
            if pid in world.cast_pids and world.person(n.split()[0]) == pid:
                self.firsts[n.split()[0]] = pid
        firsts = sorted(self.firsts, key=len, reverse=True)
        self.first_re = re.compile(r"\b(" + "|".join(re.escape(n) for n in firsts) + r")\b(?! [A-Z][a-z])")
        pl = sorted(world.place_by_name, key=len, reverse=True)
        self.place_re = re.compile(r"(?i)\b(" + "|".join(re.escape(n) for n in pl) + r")\b")

    def people(self, s):
        """[(start, end, pid)] in order."""
        out = [(m.start(), m.end(), self.w.by_name[m.group(1)]) for m in self.full_re.finditer(s)]
        taken = [(a, b) for a, b, _ in out]
        for m in self.first_re.finditer(s):
            if not any(a <= m.start() < b for a, b in taken):
                out.append((m.start(), m.end(), self.firsts[m.group(1)]))
        for m in re.finditer(r"\(p-(\d+)", s):
            pid = "p-" + m.group(1)
            if pid in self.w.people and not any(a <= m.start() <= b + 2 for a, b, _ in out):
                out.append((m.start(), m.end(), pid))
        return sorted(out)

    def places(self, s):
        return [(m.start(), m.end(), self.w.place(m.group(1))) for m in self.place_re.finditer(s)]

    def last_person(self, s, before, skip=(), sex=None, prior=()):
        """The last person named before `before` in the sentence (of that sex, for "his"/"her"), else the first in
        `prior`, the people named earlier in the same line, whose first name is its topic (a table row's resident, a
        bullet's bold name). Derived: a heuristic, tested on the case's sentences."""
        ps = [x[2] for x in self.people(s) if x[1] <= before]
        for pid in list(reversed(ps)) + list(prior):
            if pid not in skip and (sex is None or self.w.people[pid]["sex"] == sex):
                return pid
        return None

    def last_place(self, s, before):
        ps = [x for x in self.places(s) if x[1] <= before]
        return ps[-1][2] if ps else None


NAME = r"(?:[A-Z][a-z]+(?: [A-Z][a-z]+)?)"


def context_ym(s, at, default):
    """The year a claim speaks of: the last year (S to the export's end) written before it in the sentence, else the
    section's."""
    ys = [int(y) for y in re.findall(r"\b(19[5-9]\d)\b", s[:at])]
    if ys:
        y = ys[-1]
        return (y, 12) if y != default[0] else default
    return default


def corner_business(s, row_house, corner_cafe, default_year, end_year):
    """(house letter, year) if the sentence puts a business (a café, a bakery, an ironmonger) at a corner house in a
    year the engine decides (S to the export's end), else (None, None). Derived. The house is a letter named in the
    sentence ("house A", "at A", "A's"), else the table row's, else the café the section already put at a house
    ("the café window"). Questions and denials claim nothing; the Old Bank Café is the engine's."""
    if not re.search(r"\b(?:caf[eé]|bakery|ironmonger)\b", s, re.I) or "Old Bank" in s or s.rstrip().endswith("?"):
        return None, None
    if re.search(r"\b(?:cannot|would invent|without one|no caf[eé]|not|never|lacks?|ruled out|test 5)\b", s):
        return None, None
    ys = [int(y) for y in re.findall(r"\b(1[89]\d\d|20\d\d)\b", s)]
    cy = ys[-1] if ys else default_year
    if not S <= cy <= end_year:
        return None, None
    house = row_house
    m = re.search(r"\b(?:house|at|of) ([A-E])\b|\b([A-E])'s\b", s)
    if m:
        house = m.group(1) or m.group(2)
    if house is None and corner_cafe and re.search(r"\bthe caf[eé]\b", s, re.I):
        house = corner_cafe
    return (house, cy) if house in CORNER_IDS else (None, None)


def check_doc(world, names, path, start, stop, kind, rep, default=(1989, 12)):
    units = doc_units(path, start, stop)
    if units is None:
        rep.ok("docs: absent ({})".format(path))
        return
    para_place = None
    corner_cafe = None
    hours_window = False
    for ln, raw in units:
        cells = [c for c in raw.split("|")] if raw.lstrip().startswith("|") else [raw]
        row_house = None
        if raw.lstrip().startswith("|"):
            m = re.match(r"^\|\s*\*\*([A-E])\*\*", raw)
            row_house = m.group(1) if m else None
        prior = []
        for cell in cells:
            for s0 in sentences(cell):
                s = plain(s0)
                where = "{}:{}".format(path, ln)
                pl = names.places(s)
                if pl:
                    para_place = pl[-1][2]
                check_sentence(world, names, s, where, kind, rep, default, para_place, row_house, prior)
                prior += [x[2] for x in names.people(s)]
                # a business at a corner house
                house, cy = corner_business(s, row_house, corner_cafe, default[0], world.end[0])
                if house:
                    corner_cafe = house
                    rep.add("case: a business at a corner house", where, s0.strip()[:160], "contradiction",
                            "no engine venture stands at a corner house in {}; the town's one café is the Old "
                            "Bank Café (pl-cafe13, opened 1979)".format(cy), ["v-13"], "derived", kind)
                # the case's day window: people found "at house X" during working hours
                if re.search(r"\b\d{1,2}:\d{2} to \d{1,2}:\d{2}\b", s):
                    hours_window = True
                if hours_window:
                    for m in re.finditer(r"(" + NAME + r") at house ([A-E])\b", s):
                        pid = world.person(m.group(1))
                        if not pid:
                            continue
                        place, src = world.job_at(pid, default)
                        if place and place != "?":
                            rep.add("case: hours against jobs", where, s0.strip()[:160], "contradiction",
                                    "{} works at {} in {} {} (derived), so in the day's hours that is where to find them, not at "
                                    "house {}".format(world.name(pid), world.places[place]["name"], MONTHS[default[1]],
                                                      default[0], m.group(2)), src, "derived", kind)
                        else:
                            rep.ok("case: hours against jobs")


def check_sentence(world, names, s, where, kind, rep, default, para_place, row_house, prior=()):
    ppl = names.people(s)
    # roles and leads
    for m in re.finditer(r"\b(?P<role>skipper|owner|lead|manager|head mechanic|chief officer) of (?P<place>the [A-Z][\w']*(?: [A-Z][\w']*)*|the fleet|the bar|the caf[eé])", s):
        place = world.place(m.group("place"))
        pid = names.last_person(s, m.start())
        if place and pid:
            role_claim(world, s, where, kind, rep, pid, place, context_ym(s, m.start(), default), m.end())
    for m in re.finditer(r"\b[Ii]ts (?:(?P<y>\d{4}) )?(?P<role>lead|owner|manager)(?: is)? (?P<name>" + NAME + r")", s):
        pid = world.person(m.group("name"))
        place = names.last_place(s, m.start()) or para_place
        if pid and place:
            ym = (int(m.group("y")), 12) if m.group("y") else context_ym(s, m.start(), default)
            role_claim(world, s, where, kind, rep, pid, place, ym, m.end())
    for m in re.finditer(r"(?P<name>" + NAME + r") leads it in (?P<y>\d{4})", s):
        pid = world.person(m.group("name"))
        place = names.last_place(s, m.start()) or para_place
        if pid and place:
            role_claim(world, s, where, kind, rep, pid, place, min((int(m.group("y")), 12), world.end), m.end())
    for m in re.finditer(r"(?P<name>" + NAME + r") (?:is |owns )?(?:at )?(?P<place>the [A-Z][\w']*(?: [A-Z][\w']*)*|the caf[eé]) in (?P<y>\d{4})", s):
        pid = world.person(m.group("name"))
        place = world.place(m.group("place"))
        if pid and place:
            ym = (int(m.group("y")), 12)
            if " owns " in m.group(0):
                role_claim(world, s, where, kind, rep, pid, place, ym, m.end())
            else:
                got, src = world.job_at(pid, ym)
                rep.add("case: a job", where, m.group(0), "ok" if got == place else "contradiction",
                        "{} is at {} in {} (derived)".format(world.name(pid), world.places[got]["name"] if got and got != "?" else got, ym[0]),
                        src, "derived", kind)
    for m in re.finditer(r"\((?:bar staff|staff|works?) at (?P<place>the [A-Z][\w']*(?: [A-Z][\w']*)*)\)", s):
        pid = names.last_person(s, m.start())
        place = world.place(m.group("place"))
        if pid and place:
            got, src = world.job_at(pid, context_ym(s, m.start(), default))
            rep.add("case: a job", where, m.group(0), "ok" if got == place else "contradiction",
                    "{} works at {} (derived)".format(world.name(pid), got), src, "derived", kind)
    # kin
    for m in re.finditer(r"\b(?:his|her) (?P<rel>(?:late )?(?:mother|father|son|daughter|wife|husband|partner)) (?P<name>" + NAME + r")", s):
        b = pid_at(world, s, m.end(), m.group("name"))
        sex = "m" if m.group(0).startswith("his") else "f"
        a = names.last_person(s, m.start(), skip=(b,), sex=sex, prior=prior)
        if a and b:
            kin_claim(world, s, where, kind, rep, a, m.group("rel"), b, context_ym(s, m.start(), default), m.group(0))
    for m in re.finditer(r"(?P<a>" + NAME + r")'s (?P<rel>(?:late )?(?:mother|father|son|daughter|wife|husband|partner|widow))\b(?: (?P<b>" + NAME + r"))?", s):
        a = world.person(m.group("a"))
        b = pid_at(world, s, m.end(), m.group("b")) if m.group("b") else names.last_person(s, m.start(), skip=(a,))
        if a and b:
            kin_claim(world, s, where, kind, rep, a, m.group("rel"), b, context_ym(s, m.start(), default), m.group(0))
    for m in re.finditer(r"\b(?:widow|widower) of (?P<b>" + NAME + r")", s):
        b = world.person(m.group("b"))
        a = names.last_person(s, m.start(), skip=(b,))
        if a and b:
            kin_claim(world, s, where, kind, rep, b, "widow" if world.people[a]["sex"] == "f" else "widower", a,
                      context_ym(s, m.start(), default), m.group(0))
    m = re.search(r"heirs (?:by the engine's rule )?are (?:his sons )?(?P<a>" + NAME + r")(?: \(p-\d+[^)]*\))? and (?P<b>" + NAME + r")", s)
    if m:
        late = re.search(r"(?:The late )?(?P<o>" + NAME + r")'s house", s)
        o = world.person(late.group("o")) if late else None
        sur = m.group("b").split()[-1]
        heirs = [world.person(m.group("a") if " " in m.group("a") else m.group("a") + " " + sur), world.person(m.group("b"))]
        if o and all(heirs):
            kids = world.people[o].get("kids", [])
            ok = all(h in kids for h in heirs)
            widow = [k for k in world.kin(o) if k not in kids and k not in world.people[o].get("parents", [])]
            rep.add("case: kin", where, m.group(0), "ok" if ok else "contradiction",
                    "{}'s children are {}{}".format(world.name(o), ", ".join(world.name(k) for k in kids),
                                                    "; his widow {} is kin too (heirs are request 31)".format(
                                                        world.name(widow[0])) if widow else ""), [], "simulated", kind)
            if widow:
                rep.add("case: heirs left out", where, m.group(0), "note",
                        "{} was {}'s wife from 1983 and outlives him".format(world.name(widow[0]), world.name(o)),
                        [], "simulated", kind)
    for m in re.finditer(r"\b(?:gives (?P<n1>" + NAME + r") no kin|(?P<n2>" + NAME + r")[^.;]*? (?:has |with )no kin|(?P<pro>He|She) has no kin)", s):
        pid = world.person(m.group("n1") or m.group("n2") or "") if (m.group("n1") or m.group("n2")) else names.last_person(s, m.start())
        if not pid:
            continue
        ym = context_ym(s, m.start(), default)
        living = [k for k in world.kin(pid) if world.present(k, ym)[0] or not world.died(k)]
        rep.add("case: kin", where, m.group(0), "ok" if not living else "contradiction",
                "{}'s living kin in the export: {}".format(world.name(pid), ", ".join(world.name(k) for k in living) or "none"),
                [], "simulated", kind)
    # ages
    for m in re.finditer(r"\(p-(?P<pid>\d+), (?P<age>\d{1,3})\)|(?P<name>" + NAME + r") \(p-\d+\), (?P<age2>\d{1,3})\b|(?P<name3>" + NAME + r"), (?P<age3>\d{2,3}),", s):
        if m.group("pid"):
            pid, age = "p-" + m.group("pid"), int(m.group("age"))
        elif m.group("name"):
            pid, age = world.person(m.group("name")), int(m.group("age2"))
        else:
            pid, age = world.person(m.group("name3")), int(m.group("age3"))
        if not pid or pid not in world.people or not 5 <= age <= 115:
            continue
        ym = context_ym(s, m.start(), default)
        ok = age in (world.age(pid, (ym[0], 1)), world.age(pid, (ym[0], 12)))
        rep.add("case: an age", where, m.group(0), "ok" if ok else "contradiction",
                "{} is {} in {} (born {})".format(world.name(pid), world.age(pid, (ym[0], 12)), ym[0],
                                                  world.ym(world.people[pid]["born"])[0]), [], "simulated", kind)
    # deaths
    for m in re.finditer(r"\b(?:dies|died)\b,? (?:in |at the end of )?(?:(?P<m>" + MONTH_RE + r") )?(?P<y>19\d\d)", s):
        # the subject is the nearest person or pronoun before the verb
        head = s[:m.start()]
        pron = list(re.finditer(r"\b([Ss]he|[Hh]e)\b", head))
        ppl = [x for x in names.people(head)]
        if pron and (not ppl or pron[-1].start() > ppl[-1][0]):
            sex = "f" if pron[-1].group(1).lower() == "she" else "m"
            pid = names.last_person(s, pron[-1].start(), sex=sex, prior=prior)
        else:
            pid = ppl[-1][2] if ppl else None
        if not pid:
            continue
        dd = world.died(pid)
        ok = bool(dd) and dd[0] == int(m.group("y")) and (not m.group("m") or MONTHS.index(m.group("m")) == dd[1])
        rep.add("case: a death", where, m.group(0)[:120], "ok" if ok else "contradiction",
                "{} died {}".format(world.name(pid), "in {} {}".format(MONTHS[dd[1]], dd[0]) if dd else "never"),
                [death_event(world, pid)] if dd else [], "simulated", kind)
    for m in re.finditer(r"\b[Ll]ate (?P<name>" + NAME + r")\b", s):
        pid = world.person(m.group("name"))
        if pid:
            dd = world.died(pid)
            ym = context_ym(s, m.start(), default)
            rep.add("case: a death", where, m.group(0), "ok" if dd and dd <= ym else "contradiction",
                    "{} died {}".format(world.name(pid), dd), [], "simulated", kind)
    # cited events
    for m in re.finditer(r"\be-(\d+)\b", s):
        eid = "e-" + m.group(1)
        rep.add("case: a cited event exists", where, eid, "ok" if eid in world.by_id else "contradiction",
                "no such event", [], "simulated", kind)
    for m in re.finditer(r"\be-(?P<id>\d+)\)?\s*\((?P<inner>[^)]*)\)|\(e-(?P<id2>\d+)(?P<sep>[,;:]) (?P<inner2>[^)]*)\)|(?<!not )(?:(?P<m0>" + MONTH_RE + r") )?(?<!not )(?P<y0>19\d\d),? \(e-(?P<id3>\d+)\)", s):
        eid = "e-" + (m.group("id") or m.group("id2") or m.group("id3"))
        e = world.by_id.get(eid)
        if not e:
            continue
        if m.group("sep") == ";":
            continue  # "(e-N; ...)": what follows the semicolon is a new clause, not a qualifier of e-N
        inner = m.group("inner") or (re.split(r";|\be-\d+", m.group("inner2"))[0] if m.group("inner2") else None) or \
            "{} {}".format(m.group("m0") or "", m.group("y0") or "")
        t = world.when(e)
        months = re.findall(r"\b(" + MONTH_RE + r")\b", inner)
        years = [int(y) for y in re.findall(r"\b(19[5-9]\d|20[0-4]\d)\b", inner)]
        vis = [v for v in VIS if re.search(r"\b" + v + r"\b", inner)]
        if len(months) == 1 and " to " not in inner:
            rep.add("case: a cited event's month", where, "{} ({})".format(eid, inner.strip()),
                    "ok" if MONTHS.index(months[0]) == t[1] else "contradiction",
                    "{} is {} {}".format(eid, MONTHS[t[1]], t[0]), [eid], "simulated", kind)
        if len(years) == 1 and " to " not in inner:
            y = years[0]
            rep.add("case: a cited event's year", where, "{} ({})".format(eid, inner.strip()),
                    "ok" if y == t[0] else "contradiction",
                    "{} is {}{}".format(eid, t[0], "; the line gives the engine's year" if y == t[0] - world.shift else ""),
                    [eid], "simulated", kind)
        if len(vis) == 1:
            rep.add("case: a cited event's visibility", where, "{} ({})".format(eid, inner.strip()),
                    "ok" if vis[0] == e.get("vis") else "contradiction", "{} is {}".format(eid, e.get("vis")),
                    [eid], "simulated", kind)
    # labels: a job called canonical that only text derives
    for m in re.finditer(r"\b[Cc]anonical: ([^.]*)", s):
        for j in re.finditer(r"(" + NAME + r")'s job", m.group(1)):
            pid = world.person(j.group(1))
            if not pid:
                continue
            place, src = world.job_at(pid, default)
            hired = [x for x in src if x in world.by_id and world.by_id[x]["type"] in ("hired", "arrived")]
            rep.add("case: a label", where, s[:160], "contradiction" if src and not hired else "ok",
                    "{}'s job at {} in {} is derived from {} (no hire event)".format(
                        world.name(pid), world.places[place]["name"] if place and place != "?" else place, default[0],
                        ", ".join(src)) if src else "simulated", src, "derived", kind)
    # weekdays
    for m in re.finditer(r"\b(?P<wd>" + "|".join(WEEKDAYS) + r") (?P<d>\d{1,2}) (?P<m>" + MONTH_RE + r")(?: (?P<y>\d{4}))?", s):
        y = int(m.group("y")) if m.group("y") else default[0]
        try:
            wd = WEEKDAYS[calendar.weekday(y, MONTHS.index(m.group("m")), int(m.group("d")))]
        except ValueError:
            wd = "no such day"
        rep.add("case: a weekday", where, m.group(0), "ok" if wd == m.group("wd") else "contradiction",
                "{} {} {} is a {}".format(m.group("d"), m.group("m"), y, wd), [], "derived", kind)
    # hours: a person at the Anchor at a clock time on a Friday
    if re.search(r"\b\d{1,2}:\d{2}\b", s) and re.search(r"\b(?:the bar|the Anchor)\b", s) and re.search(r"Friday|\bbar\b", s):
        subj = [p for (_, _, p) in ppl] or []
        m = re.search(r"\b(she|he) never missed one\b", s)
        if m and not subj:
            pid = names.last_person(s, m.start(), sex="f" if m.group(1) == "she" else "m", prior=prior)
            subj = [pid] if pid else []
        for pid in subj:
            on, src = world.habit_on(pid, "every Friday", default)
            if on is None:
                rep.add("case: hours against habits", where, s[:120], "unsupported",
                        "{} has no Friday habit at the Anchor".format(world.name(pid)), [], "derived", kind)
            else:
                rep.add("case: hours against habits", where, s[:120], "ok" if on else "contradiction",
                        "{}'s Fridays at the Anchor {} in {} {} (derived)".format(
                            world.name(pid), "run" if on else "do not run", MONTHS[default[1]], default[0]),
                        src, "derived", kind)
    # a person of a house at a case's month
    for m in re.finditer(r"(?P<name>" + NAME + r")(?: \(p-\d+[^)]*\))?,? (?:\d+, )?of house (?P<h>[A-E])\b", s):
        pid = world.person(m.group("name"))
        if not pid:
            continue
        ym = context_ym(s, m.start(), default)
        here, src = world.present(pid, ym)
        rep.add("case: present at the case's month", where, m.group(0), "ok" if here or world.died(pid) == ym else "contradiction",
                "{} in the town in {} {}: {}".format(world.name(pid), MONTHS[ym[1]], ym[0], here), src, "derived", kind)
    # unshifted engine years quoted in our text
    for m in ([] if re.search(r"shift", s) else re.finditer(r"[\"“]([^\"”]*\b20[0-3]\d\b[^\"”]*)[\"”]", s)):
        rep.add("case: an engine year quoted unshifted", where, m.group(1)[:120], "contradiction",
                "a year from the engine's text, never shifted", [], "derived", kind)


def pid_at(world, s, end, name):
    """The person a name means, by the "(p-N" right after it if there is one."""
    m = re.match(r"\s*\(p-(\d+)", s[end:])
    if m and "p-" + m.group(1) in world.people:
        return "p-" + m.group(1)
    return world.person(name)


def role_claim(world, s, where, kind, rep, pid, place, ym, end):
    ym = min(ym, world.end)
    lead, src, rule = world.lead_at(place, ym)
    mc = re.match(r"[^.(]{0,15}\(([^)]*)\)", s[end:])
    cites = re.findall(r"e-\d+", mc.group(1)) if mc else []
    ok = lead == pid
    rep.add("case: a role or lead", where, s[:160], "ok" if ok else "contradiction",
            "the lead of {} in {} {} is {} ({}, derived)".format(
                world.places[place]["name"], MONTHS[ym[1]], ym[0], world.name(lead) if lead else "unknown", rule),
            src, "derived", kind)
    if ok and cites and not set(cites) & set(src):
        rep.add("case: a citation supports its claim", where, s[:160], "contradiction",
                "cited {}, but the claim rests on {}".format(", ".join(cites), ", ".join(src) or "the export's lead"),
                src, "derived", kind)
    elif ok and cites:
        rep.ok("case: a citation supports its claim")


def kin_claim(world, s, where, kind, rep, a, rel, b, ym, text):
    ok = world.kin_ok(a, rel, b, ym)
    rep.add("case: kin", where, text, "ok" if ok else "contradiction",
            "{} as {}'s {}: {} by the export".format(world.name(b), world.name(a), rel, "true" if ok else "false"),
            [], "simulated", kind)


# -- the engine's own strings --------------------------------------------------------------------------------------

def engine_years(world):
    """Every year the engine wrote into an event's text or a cause's label: all engine years, never shifted."""
    yre = re.compile(r"\b(19[0-9]\d|20[0-9]\d)\b")
    texts = [e for e in world.events if yre.search(e["text"])]
    labels, by_kind, label_events, uniq = 0, Counter(), set(), set()
    for e in world.events:
        for c in e.get("causes", []) or []:
            if yre.search(c.get("label", "") or ""):
                labels += 1
                by_kind[c.get("kind")] += 1
                label_events.add(e["id"])
                uniq.add(c["label"])
    years = [int(y) for e in world.events for y in yre.findall(e["text"])]
    years += [int(y) for e in world.events for c in e.get("causes", []) or [] for y in yre.findall(c.get("label", "") or "")]
    return dict(texts=len(texts), labels=labels, unique_labels=len(uniq), label_events=len(label_events),
                by_kind=dict(by_kind), lo=min(years) if years else None, hi=max(years) if years else None)


def engine_ages(world, rep):
    """The engine's own "aged N" against its births and deaths (consistency, before any shift)."""
    for e in world.events:
        m = re.search(r"\baged (\d+)", e["text"])
        if m and e["who"]:
            pid = e["who"][0]
            age = world.age(pid, world.when(e))
            rep.add("engine: an age in its text", e["id"], e["text"], "ok" if int(m.group(1)) == age else "contradiction",
                    "{} is {} then".format(world.name(pid), age), [e["id"]], "simulated", "engine")


# -- upstream ------------------------------------------------------------------------------------------------------

def upstream(world, cast, rep, ws):
    """The fixture that writes the diaries, the golden record of A, and the heart layout's strings."""
    corner = json.loads(CORNER.read_text(encoding="utf-8"))
    byid = {b["id"]: b for b in corner["buildings"]}
    for letter, bid in CORNER_IDS.items():
        if bid in byid:
            diary_claims(world, letter, byid[bid], cast.get(letter, {}), rep, "fixtures/lt1-corner.json", "upstream", ws)
    if RECORD_104.exists():
        rec = json.loads(RECORD_104.read_text(encoding="utf-8"))
        evs = rec.get("events") or rec.get("record", {}).get("events") or []
        for ev in evs:
            if ev.get("kind") == "business_opened" and S <= ev.get("year", 0) and (ev["year"], 1) <= world.end:
                rep.add("upstream: a business opened after S", "fixtures/records/bld-104.json:{}".format(ev.get("id")),
                        "{} {}".format(ev.get("year"), ev.get("params", {})), "contradiction",
                        "the same café at A, in the golden record probe", [], "derived", "upstream")
    if HEART_LAYOUT.exists():
        for i, line in enumerate(HEART_LAYOUT.read_text(encoding="utf-8").splitlines(), 1):
            if re.search(r"caf[eé][^\n]*19[5-9]\d|19[5-9]\d[^\n]*caf[eé]", line, re.I) and re.search(r"\bA\b|104", line + " A"):
                rep.add("upstream: a business at a corner house", "blender/blockouts/heart_layout.py:{}".format(i),
                        line.strip()[:120], "contradiction", "A is lit as a café in 1989", [], "derived", "upstream")


# -- main ----------------------------------------------------------------------------------------------------------

def run(world, diaries_doc, report=None):
    rep = report or Report()
    ws = json.loads(CORNER.read_text(encoding="utf-8"))["worldSeed"]
    cast = casting(world)
    names = Names(world)
    real = diaries_doc["real"]
    for letter, d in sorted(real.items()):
        diary_claims(world, letter, d, cast.get(letter, {}), rep, "diaries.json", "diary", ws)
    for letter, d in sorted(diaries_doc.get("shuffled", {}).items()):
        rep.checked["diary (shuffled, LT1f's control, not checked): events"] += len(d["events"])
    resolved_states(world, real, cast, rep, "diaries.json", "diary", ws)
    for path, start, stop, kind in DOCS:
        check_doc(world, names, path, start, stop, kind, rep)
    engine_ages(world, rep)
    upstream(world, cast, rep, ws)
    # the town's cafés at each case's month (simulated)
    for seed, months in SEEDS.items():
        ym = months[-1]
        cafes = [p for p in world.places.values() if "caf" in p["name"].lower() and
                 (not p.get("opened") or world.ym(p["opened"]) <= ym)]
        rep.add("export: the town's cafés", "seed " + seed, "one café", "ok" if len(cafes) == 1 else "contradiction",
                "{} in {} {}".format(", ".join(p["name"] for p in cafes), MONTHS[ym[1]], ym[0]),
                [p["id"] for p in cafes], "simulated", "export")
    return rep, engine_years(world)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--json", help="write the findings as JSON here")
    ap.add_argument("--all", action="store_true", help="list notes too")
    a = ap.parse_args(argv)
    world = World(json.loads(EXPORT.read_text(encoding="utf-8")))
    rep, years = run(world, json.loads(DIARIES.read_text(encoding="utf-8")))
    bad, routed = [], []
    for it in rep.items:
        if it["verdict"] == "note":
            continue
        r = route_for(it) if it["kind"] not in ("diary", "case") else None
        (routed if r else bad).append((it, r))
    print("Test 5, the facts check: {} claims and fields in {} classes".format(sum(rep.checked.values()), len(rep.checked)))
    for cls, n in sorted(rep.checked.items()):
        k = sum(1 for it in rep.items if it["cls"] == cls and it["verdict"] != "note")
        print("  {:<62} {:>5}{}".format(cls, n, "  ({} not ok)".format(k) if k else ""))
    print("\nThe engine's own strings: {texts} event texts and {labels} cause labels ({unique_labels} unique, on "
          "{label_events} events) carry an engine year, never shifted; years {lo} to {hi}; labels by kind {by_kind}."
          .format(**years))
    if routed:
        print("\nContradictions outside the diaries, each with its routed fix:")
        for it, (fix, cost) in routed:
            print("- [{}] {} | {} | {} | sources {} | fix: {} | cost: {}".format(
                it["cls"], it["where"], it["claim"][:100], it["why"], ",".join(it["sources"]) or "-", fix, cost))
    if a.all:
        print("\nNotes:")
        for it in rep.items:
            if it["verdict"] == "note":
                print("- [{}] {} | {} | {}".format(it["cls"], it["where"], it["claim"][:100], it["why"]))
    if bad:
        print("\nOPEN (no fix):")
        for it, _ in bad:
            print("- [{}] {} {} | {} | {} | sources {}".format(it["cls"], it["verdict"], it["where"], it["claim"][:120],
                                                            it["why"], ",".join(it["sources"]) or "-"))
    print("\n{}: {} open, {} routed".format("FAIL" if bad else "PASS", len(bad), len(routed)))
    if a.json:
        Path(a.json).write_text(json.dumps(dict(checked=rep.checked, items=rep.items, engine_years=years), indent=1,
                                           ensure_ascii=False), encoding="utf-8")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
