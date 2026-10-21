"""World 9989 with the lives off: the control arm of paper playtest 1.

Reads the real engine run (fixtures/engine/understory-world-9989.json) and writes
world-9989-off.json beside this folder: the same cast (names, sexes, ages, jobs,
workplaces, households, partners, bands, ventures), the same number of events per
person and year with the same visibility and notability bands, but every life event
is a generic, cause-free line from a shallow life sim. No causes, no reasons, no
memory: nothing refers back, no grudges or debts carry. Deaths have no illness arc
and no grief after. Band and festival events keep their counts; their outcomes are
re-dealt at random from the real outcomes.

Usage (from anywhere; run with -I so nothing beside the data is imported):
  python3 -I lives_off.py              generate world-9989-off.json, then check it
  python3 -I lives_off.py check        check an existing world-9989-off.json
  python3 -I lives_off.py person NAME [FROM TO]
                                       one person's real and off events side by side,
                                       in town years (default 1989 1999)

Seeded and deterministic: the same inputs and SEED give a byte-identical file.
Dates in the file stay in engine years, like the real file; the town year is the
engine year - 37 (2026-2036 is 1989-1999).
"""
import collections
import json
import os
import random
import re
import sys

SEED = "world-9989-lives-off-1"
VERSION = "lives-off 1"
SHIFT = -37

HERE = os.path.dirname(os.path.abspath(__file__))
WORLD = os.path.dirname(HERE)
ROOT = os.path.abspath(os.path.join(WORLD, *[".."] * 5))
REAL = os.path.join(ROOT, "fixtures", "engine", "understory-world-9989.json")
OUT = os.path.join(WORLD, "world-9989-off.json")


def rng(stage):
    """A separate seeded stream per stage, so a change in one stage leaves the others alone."""
    return random.Random(f"{SEED}:{stage}")


# ---------------------------------------------------------------- dates


def mi(at):
    return at["year"] * 12 + at["month"] - 1


def at_of(m):
    return {"year": m // 12, "month": m % 12 + 1}


def ty(m):
    """Town year of a month index."""
    return m // 12 + SHIFT


def band(n):
    """Notability bands, per mille: texture, minor, notable, major."""
    return "A" if n < 500 else "B" if n < 1000 else "C" if n < 2000 else "D"


BAND_NAME = {"A": "under 500", "B": "500-999", "C": "1000-1999", "D": "2000 and over"}

# ---------------------------------------------------------------- the real run


class World:
    """The real run and the states the off arm keeps: presence, jobs, partners, bands."""

    def __init__(self, path):
        self.D = json.load(open(path))
        D = self.D
        self.P = {p["id"]: p for p in D["people"]}
        self.order = [p["id"] for p in D["people"]]
        self.E = sorted(D["events"], key=lambda e: (mi(e["at"]), int(e["id"][2:])))
        self.EID = {e["id"]: e for e in self.E}
        self.PL = {pl["id"]: pl for pl in D["places"]}
        self.PLNAME = {pl["name"]: pl["id"] for pl in D["places"]}
        self.START = mi(D["presentFrom"])
        self.END = mi(D["at"])
        self.MONTHS = list(range(self.START, self.END + 1))
        self.born = {i: mi(p["born"]) for i, p in self.P.items()}
        self.died = {i: mi(p["died"]) for i, p in self.P.items() if p.get("died")}
        self.bands = {g["name"]: g["id"] for g in D["groups"]}
        self._presence()
        self._jobs()
        self._couples()
        self._band_members()
        self._family()

    # where a place is named in a line
    def place_in(self, text):
        hits = [(text.find(n), pid) for n, pid in self.PLNAME.items() if n in text]
        return [pid for _, pid in sorted(hits)]

    def age(self, p, m):
        return (m - self.born[p]) // 12

    def age_class(self, p, m):
        a = self.age(p, m)
        return "c" if a < 13 else "t" if a < 18 else "d" if a < 65 else "o"

    # -------------------------------------------------- presence in town
    def _presence(self):
        """Months each person is in town. Born, arrived and came home start it; left and died end it
        (they are still here in that month). Someone who left with others brings them home too; a hiring
        brings back someone the record forgot to bring home."""
        changes = collections.defaultdict(list)  # p -> [(m, "in" | "out" | "hired")]
        went_with = {}
        for e in self.E:
            m, t, who = mi(e["at"]), e["type"], e["who"]
            if t == "born":
                changes[who[0]].append((m, "in"))
            elif t == "arrived":
                for w in who:
                    changes[w].append((m, "in"))
            elif t == "home":
                for w in went_with.get(who[0], [who[0]]):
                    changes[w].append((m, "in"))
            elif t == "hired":
                changes[who[0]].append((m, "hired"))
            elif t == "left":
                for w in who:
                    changes[w].append((m, "out"))
                    went_with[w] = list(who)
            elif t == "death":
                changes[who[0]].append((m, "out"))
        self.present = {}
        for p in self.order:
            ch = changes.get(p, [])
            person = self.P[p]
            strong = [c for c in ch if c[1] != "hired"]
            if self.born[p] >= self.START or (p in self.died and self.died[p] < self.START):
                state = False
            elif strong:
                state = strong[0][1] == "out"
            else:
                state = person["status"] == "in"
            months = set()
            k = 0
            for m in self.MONTHS:
                leave_after = False
                while k < len(ch) and ch[k][0] == m:
                    if ch[k][1] in ("in", "hired"):
                        state = True
                    else:
                        leave_after = True
                    k += 1
                if state or leave_after:
                    months.add(m)
                if leave_after:
                    state = False
            self.present[p] = months
        # months a generic event may fall in: present and alive, not the month of death
        self.free = {
            p: {m for m in ms if not (p in self.died and m >= self.died[p])} for p, ms in self.present.items()
        }

    # -------------------------------------------------- jobs
    def _jobs(self):
        steps = collections.defaultdict(list)  # p -> [(m, place or None, from_place)]
        for e in self.E:
            m, t, who, x = mi(e["at"]), e["type"], e["who"], e["text"]
            pl = self.place_in(x)
            if t == "hired" or t == "promoted":
                steps[who[0]].append((m, pl[0], pl[0] if t == "promoted" else None))
            elif t == "arrived" and pl:
                steps[who[0]].append((m, pl[0], None))
            elif t == "moved":
                steps[who[0]].append((m, pl[1] if len(pl) > 1 else pl[0], pl[0]))
            elif t == "retired":
                steps[who[0]].append((m, None, pl[0] if pl else None))
            elif t == "dismiss":
                steps[who[1]].append((m, None, pl[0] if pl else None))
            elif t == "startover":
                steps[who[0]].append((m, None, pl[0] if pl else None))
            elif t in ("left", "death"):
                for w in who if t == "left" else who[:1]:
                    steps[w].append((m, None, "?"))
        self.job = {}
        for p in self.order:
            st = steps.get(p, [])
            final = self.P[p]["job"]
            if st:
                start = st[0][2] if st[0][2] not in (None, "?") else None
                if st[0][2] == "?" and final and mi(final["since"]) < self.START:
                    start = final["place"]
            else:
                start = final["place"] if final and mi(final["since"]) < self.START else None
            line, cur, k = {}, start, 0
            for m in self.MONTHS:
                while k < len(st) and st[k][0] == m:
                    cur = st[k][1]
                    k += 1
                line[m] = cur
            self.job[p] = line

    # -------------------------------------------------- couples
    def _couples(self):
        """Intervals [start, end) when two people are a couple, and when they married."""
        ev = collections.defaultdict(list)
        for e in self.E:
            m, t, who = mi(e["at"]), e["type"], e["who"]
            if t in ("dating", "married", "split", "divorce"):
                ev[tuple(sorted(who[:2]))].append((m, t))
        self.couples = []  # dicts: a, b, start, end, married, ends_how
        seen = set()
        for pair, xs in ev.items():
            seen.add(pair)
            cur = None
            if xs[0][1] in ("married", "split", "divorce"):
                cur = {"a": pair[0], "b": pair[1], "start": self.START - 1, "end": None, "married": None}
                if xs[0][1] == "divorce":
                    cur["married"] = self.START - 1
            for m, t in xs:
                if t == "dating":
                    cur = {"a": pair[0], "b": pair[1], "start": m, "end": None, "married": None}
                elif t == "married":
                    cur["married"] = m
                else:
                    cur["end"] = m
                    cur["ends_how"] = t
                    self.couples.append(cur)
                    cur = None
            if cur:
                self.couples.append(cur)
        # a death names the partner who was there; some widowed records have dropped the partner
        for e in self.E:
            if e["type"] == "death" and len(e["who"]) > 1:
                pair = tuple(sorted(e["who"][:2]))
                if pair not in seen and not any({c["a"], c["b"]} == set(pair) for c in self.couples):
                    seen.add(pair)
                    self.couples.append({"a": pair[0], "b": pair[1], "start": self.START - 1, "end": None,
                                         "married": self.START - 1})
        for p in self.order:
            q = self.P[p]["partner"]
            if not q:
                continue
            pair = tuple(sorted((p, q["id"])))
            if pair in seen:
                continue
            seen.add(pair)
            s = mi(q["since"])
            self.couples.append(
                {"a": pair[0], "b": pair[1], "start": s, "end": None, "married": s if q["kind"] == "married" else None}
            )
        # deaths and leaving end a couple
        for c in self.couples:
            for w in (c["a"], c["b"]):
                if w in self.died and (c["end"] is None or self.died[w] < c["end"]) and self.died[w] >= c["start"]:
                    c["end"] = self.died[w]
                    c["ends_how"] = "death"
        for e in self.E:
            if e["type"] == "left" and "end of the marriage" in e["text"]:
                m = mi(e["at"])
                for c in self.couples:
                    if e["who"][0] in (c["a"], c["b"]) and c["start"] <= m and (c["end"] is None or c["end"] > m):
                        c["end"] = m
                        c["ends_how"] = "left"
        for c in self.couples:
            if c["end"] is None:
                c["end"] = self.END + 1

    def partner_at(self, p, m):
        for c in self.couples:
            if p in (c["a"], c["b"]) and c["start"] <= m < c["end"]:
                return c["b"] if c["a"] == p else c["a"]
        return None

    def couple_of(self, p, q, m):
        for c in self.couples:
            if {p, q} == {c["a"], c["b"]} and c["start"] <= m < c["end"]:
                return c
        return None

    # -------------------------------------------------- bands
    def _band_members(self):
        self.member = collections.defaultdict(dict)  # g -> p -> [start, end]
        for e in self.E:
            g = self.band_of(e)
            if not g or e["type"] == "notpicked":
                continue
            m, t = mi(e["at"]), e["type"]
            who = e["who"]
            for w in who:
                iv = self.member[g].setdefault(w, [m, self.END + 1])
                iv[0] = min(iv[0], m)
            if t == "group:left":
                self.member[g][who[0]][1] = m
            if t == "group:split":
                for w in who:
                    self.member[g][w][1] = m
        for g in self.member:
            for w, iv in self.member[g].items():
                if w in self.died:
                    iv[1] = min(iv[1], self.died[w])
        for g in self.D["groups"]:
            for w in g["members"]:
                iv = self.member[g["id"]].setdefault(w, [mi(g["since"]), self.END + 1])
                if mi(g["since"]) < self.START:
                    iv[0] = min(iv[0], self.START)

    def band_of(self, e):
        if e["type"] not in BAND_T and e["type"] not in ("group:joined", "group:left", "group:formed", "group:split"):
            return None
        for name, g in self.bands.items():
            if name in e["text"]:
                return g
        # lines about a song name no band: it is the band its people play in that month
        if hasattr(self, "member"):
            m = mi(e["at"])
            hits = [g for g, ms in sorted(self.member.items())
                    if all(w in ms and ms[w][0] <= m < ms[w][1] for w in e["who"])]
            hits = hits or [g for g, ms in sorted(self.member.items())
                            if e["who"][0] in ms and ms[e["who"][0]][0] <= m < ms[e["who"][0]][1]]
            if hits:
                return hits[0]
        return None

    def bandmates(self, p, q, m):
        for g, ms in self.member.items():
            if p in ms and q in ms and ms[p][0] <= m < ms[p][1] and ms[q][0] <= m < ms[q][1]:
                return True
        return False

    # -------------------------------------------------- family
    def _family(self):
        self.fam = collections.defaultdict(set)
        for p, x in self.P.items():
            for q in x["parents"] + x["kids"]:
                self.fam[p].add(q)
                self.fam[q].add(p)
        for p, x in self.P.items():
            for par in x["parents"]:
                for sib in self.P[par]["kids"]:
                    if sib != p:
                        self.fam[p].add(sib)
                for gp in self.P[par]["parents"]:
                    self.fam[p].add(gp)
                    self.fam[gp].add(p)

    def relation(self, p, q, m):
        if self.partner_at(p, m) == q:
            return "partner"
        if q in self.fam[p]:
            return "family"
        jp, jq = self.job[p].get(m), self.job[q].get(m)
        if jp and jp == jq:
            return "coworker"
        if self.bandmates(p, q, m):
            return "bandmate"
        return "other"


# ---------------------------------------------------------------- what each real event becomes

STATE_T = {
    "born", "death", "married", "divorce", "split", "dating", "hired", "retired", "promoted", "dismiss",
    "arrived", "left", "moved", "home", "stayed", "group:joined", "group:left", "group:formed", "group:split",
    "startover",
}
BAND_T = {"group:show", "group:work", "cheer", "claimsong", "resentsong", "backsong", "group:creditrow", "stayfor",
          "notpicked"}
OPEN_T = {"performed"}
HARBOUR_T = {"harbour:ran", "harbour:ok", "harbour:chaos", "stepup"}
FEST_ROLE = {"plan": "plan", "pitchin": "ask", "notthetime": "ask", "council:yes": "council", "deliver": "part",
             "redo": "part", "allnighter": "part", "late": "part", "rough": "part", "night:good": "night",
             "night:bad": "night"}


def classify(W):
    fest = {}
    for v in W.D["ventures"]:
        for x in v["events"]:
            if x in W.EID:
                fest[x] = v["id"]
    kinds = {}
    for e in W.E:
        t = e["type"]
        if t in STATE_T:
            k = "state"
        elif e["id"] in fest:
            k = "fest:" + FEST_ROLE[t]
        elif t in BAND_T:
            k = "band"
        elif t in OPEN_T:
            k = "opennight"
        elif t in HARBOUR_T:
            k = "harbour"
        else:
            k = "generic"
        kinds[e["id"]] = k
    return kinds, fest


# ---------------------------------------------------------------- texts

PRON = {"m": {"his": "his", "he": "he", "him": "him"}, "f": {"his": "her", "he": "she", "him": "her"}}


def names(W, ids):
    ns = [W.P[i]["name"] for i in ids]
    return ns[0] if len(ns) == 1 else ", ".join(ns[:-1]) + " and " + ns[-1]


def fill(W, text, who, m, extra=None):
    f = {}
    for k, p in zip("abcd", who):
        f[k] = W.P[p]["name"]
        for key, word in PRON[W.P[p]["sex"]].items():
            f[f"{k}_{key}"] = word
    f["all"] = names(W, who)
    f["others"] = names(W, who[1:]) if len(who) > 1 else ""
    job = W.job[who[0]].get(m)
    f["place"] = W.PL[job]["name"] if job else "work"
    f["age"] = str(W.age(who[0], m))
    f.update(extra or {})
    return text.format(**f)


def state_text(W, e):
    """The kept states, said flatly: no cause, no reason, no span that reaches back."""
    t, who, x = e["type"], e["who"], e["text"]
    n = lambda i: W.P[who[i]]["name"]
    pl = W.place_in(x)
    plname = lambda i: W.PL[pl[i]]["name"]
    if t == "born":
        return f"{n(0)} was born to {names(W, who[1:])}." if len(who) > 1 else f"{n(0)} was born."
    if t == "death":
        return f"{n(0)} died, aged {W.age(who[0], mi(e['at']))}."
    if t == "married":
        return f"{n(0)} and {n(1)} got married."
    if t == "divorce":
        return f"{n(0)} and {n(1)} divorced."
    if t == "split":
        return f"{n(0)} and {n(1)} split up."
    if t == "dating":
        return f"{n(0)} and {n(1)} started seeing each other."
    if t == "hired":
        return f"{n(0)} started work at {plname(0)}."
    if t == "retired":
        return f"{n(0)} retired from {plname(0)}."
    if t == "promoted":
        role = re.search(r"became (.+?) at ", x).group(1)
        return f"{n(0)} became {role} at {plname(0)}."
    if t == "dismiss":
        return f"{n(0)} let {n(1)} go from {plname(0)}."
    if t == "startover":
        return f"{n(0)} left {PRON[W.P[who[0]]['sex']]['his']} job at {plname(0)}."
    if t == "arrived":
        s = f"{n(0)} moved to the town and started work at {plname(0)}"
        if "and the children" in x:
            s += f", with {n(1)} and the children"
        elif len(who) > 1:
            s += f", with {names(W, who[1:])}"
        return s + "."
    if t == "left":
        if "university" in x:
            return f"{n(0)} left for university in the city."
        if "went too" in x:
            return f"{n(0)} left the town for the city, and {names(W, who[1:])} went too."
        m = re.search(r"\. (.+?) stayed, and that was the end of the marriage", x)
        if m:
            return f"{n(0)} left the town for the city; {m.group(1)} stayed, and the marriage ended."
        return f"{n(0)} left the town for the city."
    if t == "moved":
        return f"{n(0)} moved from {plname(0)} to {plname(1)}."
    if t == "home":
        return f"{n(0)} came back to the town."
    if t == "stayed":
        return f"{n(0)} turned eighteen."
    g = W.band_of(e)
    gname = next(k for k, v in W.bands.items() if v == g) if g else "the band"
    if t == "group:joined":
        return f"{n(0)} joined {gname}."
    if t == "group:left":
        return f"{gname} went on without {n(0)}."
    if t == "group:formed":
        return f"{names(W, who)} started a band: {gname}."
    if t == "group:split":
        return f"{gname} split up."
    raise ValueError(t)


def cap(s):
    return s[0].upper() + s[1:]


# outcome tiers read from the real lines, re-dealt at random in the off arm
def show_tier(x):
    if any(k in x for k in ("called back", "room went quiet", "stayed for the last song", "in her hand", "in his hand")):
        return "great"
    if "did well" in x or "full room" in x:
        return "good"
    return "plain"


def song_tier(x):
    if "best thing they had" in x:
        return "best"
    if "it was good" in x:
        return "good"
    if "did not come to much" in x:
        return "flop"
    return "plain"


def open_tier(x):
    return "great" if "room went quiet" in x else "good" if "did well" in x else "bad"


SHOW_TXT = {
    "great": "{band} played the Anchor to a packed room and were called back for more.",
    "good": "{band} played the Anchor, and it went down well.",
    "plain": "{band} played the Anchor; it was an ordinary night.",
}
SONG_TXT = {
    "best": '{a} brought a new song to {band}, "{title}", and it went straight into the set.',
    "good": '{a} brought a new song to {band}, "{title}", and the others liked it.',
    "flop": '{a} brought a new song to {band}, "{title}", and it did not catch on.',
    "plain": '{a} brought a new song to {band}, "{title}".',
}
OPEN_TXT = {
    "great": "{a} played the Anchor's open night, and the room went quiet.",
    "good": "{a} played the Anchor's open night and did well.",
    "bad": "{a} played the Anchor's open night, and it fell apart.",
}
BAND_TALK = [
    "{a} and {b} ran through the set with {band}.",
    "{a} and {b} worked out a new arrangement for {band}.",
    "{a} and {b} stayed late after {band}'s practice.",
    "{a} tuned {b}'s guitar before {band} practised.",
    "{a} and {b} carried {band}'s gear down to the Anchor.",
    "{a} and {b} listened back to a tape of {band}'s practice.",
]
BAND_TALK3 = [
    "{all} ran through the set with {band}.",
    "{all} practised with {band} until late.",
]
SONG_A = ["Grey", "Blue", "Late", "Cold", "Small", "Bright", "Quiet", "Silver", "Long", "Low", "Green", "Slow",
          "Salt", "Paper", "Open", "Winter"]
SONG_B = ["Water", "Weather", "Morning", "Lights", "Tide", "Hours", "Road", "Window", "Rain", "Boats", "Street",
          "Summer", "Shoes", "Radio", "Ferry", "Lanterns"]
PART_TXT = {
    "deliver": "{a} had {a_his} part of the summer festival ready in good time.",
    "redo": "{a} got {a_his} part of the summer festival done at the last minute.",
    "allnighter": "{a} worked through the night to get {a_his} part of the summer festival done.",
    "late": "{a} was late with {a_his} part of the summer festival.",
    "rough": "{a} got {a_his} part of the summer festival done, roughly.",
}
HARBOUR_TXT = {
    "harbour:ran": "The harbour day ran smoothly, with {a} in charge.",
    "harbour:ok": "The harbour day went off well enough, with {a} in charge.",
    "harbour:chaos": "The harbour day was a muddle, with {a} in charge.",
}

# ---------------------------------------------------------------- the generic pool
# Each template: n people, visibilities (p private, l local, u public), notability bands (A-D),
# the ages it suits for the subject (a) and the others (b): c child, t teen, d adult, o over 65,
# the relation it needs (partner, family, coworker, close = partner or family, any),
# whether it needs a job, tags for the arc guards, and a once-only key.

TPL = []


def T(cat, n, vis, bands, text, a="do", b="do", rel="any", job=False, tags=(), once=None, special=None, w=1.0):
    TPL.append(dict(cat=cat, n=n, vis=vis, bands=bands, text=text, a=a, b=b, rel=rel, job=job, tags=set(tags),
                    once=once, special=special, w=w))


# ---- one person, private
T("everyday", 1, "p", "A", "{a} had a quiet night in.", a="tdo")
T("everyday", 1, "p", "A", "{a} spent the evening in front of the television.", a="tdo")
T("everyday", 1, "p", "A", "{a} did the crossword in the paper.")
T("everyday", 1, "p", "A", "{a} had an early night.", a="cdo")
T("everyday", 1, "p", "A", "{a} fell asleep in the armchair.")
T("everyday", 1, "p", "A", "{a} tried a new recipe.")
T("everyday", 1, "p", "A", "{a} read a library book in one sitting.", a="tdo")
T("everyday", 1, "p", "A", "{a} listened to the radio all afternoon.")
T("everyday", 1, "p", "A", "{a} had a lie-in on Sunday.", a="tdo")
T("everyday", 1, "p", "A", "{a} wrote a letter to a cousin in the city.")
T("everyday", 1, "p", "A", "{a} spent an hour looking for the house keys.")
T("everyday", 1, "p", "AB", "{a} ate too much at dinner.", a="ctdo")
T("everyday", 1, "p", "A", "{a} stayed up late watching a film.", a="tdo")
T("everyday", 1, "p", "AB", "{a} built a den in the back garden.", a="c")
T("everyday", 1, "p", "A", "{a} drew a picture of a boat.", a="c")
T("everyday", 1, "p", "AB", "{a} played records in {a_his} room all evening.", a="t")
T("everyday", 1, "p", "A", "{a} did {a_his} homework at the last minute.", a="t")
T("mood", 1, "p", "BC", "{a} had a good day.", a="ctdo")
T("mood", 1, "p", "B", "{a} had a bad day.", a="tdo", tags=["mood-"])
T("mood", 1, "p", "B", "{a} felt a bit low for a few days.", a="tdo", tags=["mood-"])
T("mood", 1, "p", "B", "{a} couldn't sleep one night.", a="tdo", tags=["mood-"])
T("everyday", 1, "p", "B", "{a} put together a new bookcase.")
T("everyday", 1, "p", "B", "{a} cleared out the cupboard under the stairs.")
T("everyday", 1, "p", "AB", "{a} started a thousand-piece jigsaw.")
T("purchase", 1, "p", "B", "{a} treated {a_him}self to a new pair of shoes.", a="tdo")
T("everyday", 1, "p", "B", "{a} baked a loaf of bread.")
T("health", 1, "p", "B", "{a} had a cold.", a="ctdo", tags=["health"])
T("health", 1, "p", "C", "{a} was off sick for a week.", tags=["health"])
T("mood", 1, "p", "C", "{a} had a terrible week.", a="tdo", tags=["mood-"])
T("mood", 1, "p", "CD", "{a} had a wonderful week.", a="tdo")
T("luck", 1, "p", "C", "{a} won a little money on the pools.")
T("everyday", 1, "p", "C", "{a} lost {a_his} wallet and found it the next day.")
T("health", 1, "p", "C", "{a} spent a day at the dentist in the city.", a="ctdo", tags=["health"])
T("everyday", 1, "p", "C", "{a} gave the whole house a spring clean.")
T("mood", 1, "p", "C", "{a} lay awake for nights on end.", tags=["mood-"])
T("health", 1, "p", "C", "{a} had chickenpox.", a="c", tags=["health"])
T("everyday", 1, "p", "BC", "{a} learned to ride a bike.", a="c", once="bike")
T("school", 1, "p", "C", "{a} got a bad mark in a maths test.", a="t")
T("school", 1, "p", "C", "{a} got top marks in a spelling test.", a="ct")
T("health", 1, "p", "D", "{a} had a health scare that came to nothing.", tags=["health"])
T("mood", 1, "p", "D", "{a} had the best week of the year.", a="ctdo")
T("mood", 1, "p", "D", "{a} had the worst week of the year.", a="tdo", tags=["mood-"])
T("luck", 1, "p", "D", "{a} won a good sum on the pools.")
T("health", 1, "p", "D", "{a} had a bad bout of flu and spent a week in bed.", a="ctdo", tags=["health"])

# ---- one person, local
T("work", 1, "l", "AC", "{a} had a long week at {place}.", a="tdo", job=True)
T("work", 1, "l", "A", "{a} had a quiet week at {place}.", a="tdo", job=True)
T("work", 1, "l", "AB", "{a} had a busy week at {place}.", a="tdo", job=True)
T("everyday", 1, "l", "A", "{a} went into town to do the shopping.")
T("everyday", 1, "l", "A", "{a} walked the shore on Sunday.", a="tdo")
T("everyday", 1, "l", "A", "{a} had a pint at the Anchor.")
T("everyday", 1, "l", "A", "{a} went for a swim in the harbour.", a="tdo")
T("everyday", 1, "l", "A", "{a} hung out the washing.")
T("everyday", 1, "l", "A", "{a} took the bus to the city.", a="tdo")
T("everyday", 1, "l", "A", "{a} fed the gulls on the quay.", a="ctdo")
T("everyday", 1, "l", "A", "{a} sat on the bench by the quay for an hour.")
T("everyday", 1, "l", "A", "{a} went to the library.", a="tdo")
T("everyday", 1, "l", "A", "{a} fished off the end of the quay.", a="tdo")
T("everyday", 1, "l", "A", "{a} had a coffee at the Old Bank Café.")
T("everyday", 1, "l", "AB", "{a} played on the quay with the other children.", a="c")
T("everyday", 1, "l", "A", "{a} lost a tooth at school.", a="c")
T("everyday", 1, "l", "AB", "{a} hung about on the gully steps with friends.", a="t")
T("everyday", 1, "l", "AB", "{a} went to the school disco.", a="t")
T("purchase", 1, "l", "BC", "{a} bought a new coat.", a="tdo")
T("everyday", 1, "l", "B", "{a} had a haircut that everyone noticed.", a="tdo")
T("luck", 1, "l", "B", "{a} won the meat raffle at the Anchor.")
T("everyday", 1, "l", "B", "{a} caught a good bag of mackerel off the quay.", a="tdo")
T("purchase", 1, "l", "B", "{a} got a new bicycle.", a="ctdo", once="bicycle")
T("health", 1, "l", "B", "{a} was off sick for a few days.", a="tdo", tags=["health"])
T("health", 1, "l", "B", "{a} cut a finger at {place}.", a="tdo", job=True, tags=["health"])
T("health", 1, "l", "B", "{a} twisted an ankle on the gully steps.", a="tdo", tags=["health"])
T("work", 1, "l", "BC", "{a} worked a double shift at {place}.", a="tdo", job=True)
T("work", 1, "l", "B", "{a} was late for work at {place} one morning.", a="tdo", job=True, tags=["work-"])
T("health", 1, "l", "B", "{a} fell off {a_his} bike and grazed a knee.", a="c", tags=["health"])
T("school", 1, "l", "BC", "{a} came top in the school's spelling test.", a="ct")
T("health", 1, "l", "C", "{a} was off sick for a week.", a="tdo", tags=["health"])
T("party", 1, "l", "C", "{a} had a birthday party at the Anchor.", special="bday")
T("milestone", 1, "l", "C", "{a} passed {a_his} driving test.", a="td", once="driving", special="young")
T("purchase", 1, "l", "C", "{a} bought a second-hand car.", once="car", special="car")
T("luck", 1, "l", "C", "{a} won the Anchor's quiz night.")
T("health", 1, "l", "C", "{a} sprained a wrist and was off work for two weeks.", job=True, tags=["health"])
T("everyday", 1, "l", "C", "{a} had family to stay for a fortnight.")
T("everyday", 1, "l", "C", "{a} sang a solo at the choir's spring concert.")
T("school", 1, "l", "C", "{a} got a part in the school play.", a="ct")
T("health", 1, "l", "D", "{a} was in hospital in the city for a week.", a="tdo", tags=["health"])
T("party", 1, "l", "D", "{a} turned {age} and had a party at the Anchor.", special="round")
T("luck", 1, "l", "D", "{a} won the big prize in the Anchor's raffle.")
T("health", 1, "l", "D", "{a} had a bad fall on the steps and was laid up for a month.", tags=["health"])
T("everyday", 1, "l", "D", "{a} went abroad for a fortnight's holiday.")
T("health", 1, "l", "D", "{a} had an operation in the city and was home within the week.", tags=["health"])
T("school", 1, "l", "D", "{a} won the school's prize for the year.", a="ct")

# ---- one person, public
T("everyday", 1, "u", "AB", "{a} was in the Courier's photograph of the quay.", a="ctdo")
T("everyday", 1, "u", "AB", "{a}'s letter about the bus times was printed in the Courier.")
T("purchase", 1, "u", "C", "{a} bought a car.", once="car", special="car")
T("purchase", 1, "u", "C", "{a} bought a small boat.", once="boat", special="boat")
T("luck", 1, "u", "C", "{a} was in the Courier with the biggest cod of the season.", a="tdo")
T("luck", 1, "u", "C", "{a} won the top prize in the Anchor's raffle.")
T("party", 1, "u", "D", "{a} turned {age}, and half the town came to the party at the Anchor.", special="round")
T("luck", 1, "u", "D", "{a} won a prize for the best garden in the county.")

# ---- one person away from the town (the real run talks about some who live away)
T("away", 1, "l", "ABC", "{a} rang home from the city.", a="tdo", special="away")
T("away", 1, "l", "ABC", "{a} sent a postcard home.", a="tdo", special="away")
T("away", 1, "pl", "ABCD", "{a} wrote a long letter home.", a="tdo", special="away")
T("away", 1, "l", "BCD", "{a} sent a photograph home.", a="tdo", special="away")
T("away", 1, "u", "BCD", "{a} was in a city paper, and someone brought a copy to the Anchor.", a="tdo", special="away")

# ---- two people, private
T("social", 2, "p", "A", "{a} and {b} had a cup of tea together.", a="tdo", b="tdo")
T("social", 2, "p", "A", "{a} made {b} a sandwich.", a="tdo", b="ctdo")
T("social", 2, "p", "A", "{a} and {b} watched a film on the television.", a="ctdo", b="ctdo")
T("social", 2, "p", "AB", "{a} told {b} a joke.", a="ctdo", b="ctdo")
T("social", 2, "p", "A", "{a} and {b} did the washing-up together.", a="tdo", b="tdo", rel="close")
T("social", 2, "p", "A", "{a} complimented {b}'s cooking.")
T("social", 2, "p", "A", "{a} and {b} talked about the weather.", rel="apart")
T("social", 2, "p", "A", "{a} and {b} played a game of cards.", a="ctdo", b="ctdo")
T("social", 2, "p", "A", "{a} helped {b} with the crossword.")
T("social", 2, "p", "A", "{a} gave {b} a hug.", a="ctdo", b="ctdo", rel="close")
T("quarrel", 2, "p", "A", "{a} and {b} bickered about the television.", a="tdo", b="tdo", rel="close", tags=["conflict"])
T("social", 2, "p", "A", "{a} and {b} chatted on the phone for an hour.", a="tdo", b="tdo", rel="apart")
T("social", 2, "p", "AB", "{a} and {b} went for a walk along the shore.", a="ctdo", b="ctdo")
T("family", 2, "p", "AB", "{a} read {b} a bedtime story.", a="tdo", b="c", rel="family")
T("family", 2, "p", "AB", "{a} helped {b} with {b_his} homework.", a="tdo", b="ct", rel="family")
T("couple", 2, "p", "AB", "{a} and {b} had a cosy night in.", rel="partner")
T("couple", 2, "p", "AB", "{a} brought {b} breakfast in bed.", rel="partner")
T("social", 2, "p", "B", "{a} and {b} had a heart-to-heart.", a="tdo", b="tdo")
T("quarrel", 2, "p", "B", "{a} and {b} argued about nothing much.", a="tdo", b="tdo", tags=["conflict"])
T("social", 2, "p", "B", "{a} and {b} laughed until they cried at a comedy on the television.", a="ctdo", b="ctdo")
T("social", 2, "p", "B", "{a} surprised {b} with a cake.", a="tdo", b="ctdo")
T("quarrel", 2, "p", "C", "{a} and {b} fell out.", a="tdo", b="tdo", tags=["conflict"], w=0.5)
T("quarrel", 2, "p", "B", "{a} snapped at {b}.", a="tdo", b="tdo", tags=["conflict"])
T("social", 2, "p", "B", "{a} and {b} had a long chat.", a="tdo", b="tdo")
T("social", 2, "p", "BC", "{a} gave {b} a little present.", a="ctdo", b="ctdo")
T("couple", 2, "p", "B", "{a} and {b} planned the week's meals.", rel="partner")
T("social", 2, "p", "B", "{a} teased {b} about {b_his} haircut.", a="ctdo", b="ctdo")
T("quarrel", 2, "p", "C", "{a} and {b} had a row.", a="tdo", b="tdo", tags=["conflict"])
T("social", 2, "p", "C", "{a} and {b} had a lovely evening together.")
T("couple", 2, "p", "CD", "{a} and {b} had a romantic evening.", rel="partner")
T("outing", 2, "p", "C", "{a} and {b} went away for the weekend.", rel="close")
T("social", 2, "p", "C", "{a} and {b} talked late into the night.", a="tdo", b="tdo")
T("quarrel", 2, "p", "C", "{a} and {b} had a falling-out over the washing-up.", a="tdo", b="tdo", rel="close",
  tags=["conflict"])
T("social", 2, "p", "C", "{a} gave {b} a surprise present.", a="tdo", b="ctdo")
T("quarrel", 2, "p", "D", "{a} and {b} had a blazing row.", a="tdo", b="tdo", tags=["conflict"])
T("social", 2, "p", "D", "{a} and {b} had a perfect day out.", a="ctdo", b="ctdo")
T("social", 2, "p", "D", "{a} and {b} talked all night.", a="tdo", b="tdo")
T("outing", 2, "p", "D", "{a} and {b} had a weekend in the city together.", rel="close")

T("couple", 2, "p", "A", "{a} and {b} did the crossword together.", rel="partner")
T("couple", 2, "p", "A", "{a} and {b} cooked dinner together.", rel="partner")
T("couple", 2, "p", "A", "{a} and {b} watched the news together.", rel="partner")
T("couple", 2, "p", "B", "{a} and {b} moved the furniture round in the front room.", rel="partner")
T("couple", 2, "p", "B", "{a} and {b} talked about where to go on holiday.", rel="partner")
T("couple", 2, "p", "C", "{a} and {b} had a long lie-in together on Sunday.", rel="partner")
T("quarrel", 2, "p", "BC", "{a} and {b} argued about whose turn it was to cook.", rel="partner", tags=["conflict"])
T("social", 2, "p", "B", "{a} and {b} did a jigsaw together.", a="ctdo", b="ctdo")
T("social", 2, "p", "B", "{a} and {b} listened to records together.", a="tdo", b="tdo")
T("social", 2, "p", "B", "{a} showed {b} how to make pancakes.", a="tdo", b="ctdo")
T("social", 2, "p", "C", "{a} and {b} cooked a big dinner together.", a="tdo", b="tdo")
T("social", 2, "p", "C", "{a} cut {b}'s hair in the kitchen.", a="tdo", b="ctdo", rel="close")
T("work", 2, "p", "AB", "{a} and {b} walked home from {place} together.", a="tdo", b="tdo", rel="coworker")
T("work", 2, "p", "BC", "{a} and {b} moaned about the week at {place}.", a="tdo", b="tdo", rel="coworker")

# ---- two people, local
T("couple", 2, "l", "A", "{a} and {b} walked arm in arm along the quay.", rel="partner")
T("couple", 2, "l", "A", "{a} and {b} did the big shop in town.", rel="partner")
T("couple", 2, "l", "B", "{a} and {b} had dinner at the Old Bank Café.", rel="partner")
T("couple", 2, "l", "C", "{a} and {b} went to the pictures in the city.", rel="partner")
T("work", 2, "l", "A", "{a} and {b} took their break together at {place}.", a="tdo", b="tdo", rel="coworker")
T("work", 2, "l", "AB", "{a} showed {b} a quicker way of doing a job at {place}.", a="tdo", b="tdo", rel="coworker")
T("work", 2, "l", "B", "{a} and {b} had a laugh at {place}.", a="tdo", b="tdo", rel="coworker")
T("work", 2, "l", "C", "{a} and {b} got a big job done early at {place}.", a="tdo", b="tdo", rel="coworker")
T("quarrel", 2, "l", "BC", "{a} and {b} had words at {place}.", a="tdo", b="tdo", rel="coworker", tags=["conflict"])
T("social", 2, "l", "B", "{a} and {b} shared a taxi home from the Anchor.")
T("social", 2, "l", "B", "{a} and {b} watched the boats come in.", a="ctdo", b="ctdo")
T("social", 2, "l", "C", "{a} and {b} sang a duet at the Anchor.")
T("social", 2, "l", "C", "{a} and {b} took the ferry for a day out.", a="ctdo", b="ctdo")
T("social", 2, "l", "A", "{a} and {b} had a drink at the Anchor.")
T("social", 2, "l", "A", "{a} and {b} chatted outside the shop.", a="ctdo", b="ctdo", rel="apart")
T("social", 2, "l", "A", "{a} ran into {b} on the quay.", a="ctdo", b="ctdo", rel="apart")
T("social", 2, "l", "A", "{a} gave {b} a lift into town.", b="ctdo")
T("social", 2, "l", "A", "{a} and {b} played cards at the Anchor.")
T("social", 2, "l", "A", "{a} and {b} sat together at choir practice.")
T("social", 2, "l", "A", "{a} and {b} walked up the gully steps together.", a="ctdo", b="ctdo")
T("social", 2, "l", "A", "{a} waved to {b} across the harbour.", a="ctdo", b="ctdo", rel="apart")
T("work", 2, "l", "AB", "{a} and {b} worked late at {place}.", a="tdo", b="tdo", rel="coworker")
T("social", 2, "l", "A", "{a} and {b} shared a table at the Old Bank Café.", a="tdo", b="tdo")
T("social", 2, "l", "A", "{a} helped {b} carry the shopping up the steps.", a="tdo", b="ctdo")
T("social", 2, "l", "A", "{a} and {b} took the bus to the city together.", a="tdo", b="ctdo")
T("quarrel", 2, "l", "B", "{a} and {b} had words at the Anchor.", tags=["conflict"])
T("social", 2, "l", "B", "{a} and {b} had a good laugh at the Anchor.")
T("social", 2, "l", "B", "{a} helped {b} move a wardrobe.", a="tdo")
T("social", 2, "l", "B", "{a} and {b} went fishing off the quay.", a="ctdo", b="ctdo")
T("social", 2, "l", "B", "{a} and {b} had lunch at the Old Bank Café.", a="tdo", b="tdo")
T("work", 2, "l", "BC", "{a} and {b} covered a busy shift together at {place}.", a="tdo", b="tdo", rel="coworker")
T("social", 2, "l", "B", "{a} bumped into {b} at the shop, and they talked for an hour.", a="tdo", b="tdo",
  rel="apart")
T("quarrel", 2, "l", "C", "{a} and {b} fell out.", a="tdo", b="tdo", tags=["conflict"], w=0.5)
T("quarrel", 2, "l", "C", "{a} and {b} fell out at the Anchor.", tags=["conflict"])
T("social", 2, "l", "C", "{a} and {b} went to the city for the day.", a="ctdo", b="ctdo")
T("social", 2, "l", "C", "{a} and {b} won the quiz night at the Anchor.", w=0.3)
T("social", 2, "l", "C", "{a} and {b} had a night out at the Anchor.")
T("couple", 2, "l", "CD", "{a} got engaged to {b}.", rel="partner", special="engaged")
T("quarrel", 2, "l", "C", "{a} and {b} argued in the street.", a="tdo", b="tdo", tags=["conflict"])
T("social", 2, "l", "C", "{a} and {b} danced together at the Anchor on Saturday.")
T("social", 2, "l", "C", "{a} took {b} out on a boat for the afternoon.", b="ctdo")
T("quarrel", 2, "l", "D", "{a} and {b} had a shouting match at the Anchor.", tags=["conflict"])
T("luck", 2, "l", "D", "{a} and {b} won the big prize in the Anchor's raffle.")
T("party", 2, "l", "D", "{a} and {b} threw a party for their friends at the Anchor.")
T("social", 2, "l", "D", "{a} and {b} had a day out in the city that everyone heard about.", a="ctdo", b="ctdo")

# ---- two people, public
T("everyday", 2, "u", "ABCD", "{a} and {b} were in the Courier's photograph of the quay.", a="ctdo", b="ctdo")
T("luck", 2, "u", "BCD", "{a} and {b} won the quiz night at the Anchor.", w=0.5)

# ---- three or four people
T("social", 3, "p", "ABCD", "{all} had a cup of tea together.", a="tdo", b="tdo")
T("social", 3, "p", "ABCD", "{all} talked late into the night.", a="tdo", b="tdo")
T("social", 3, "l", "ABCD", "{all} had a drink at the Anchor.")
T("social", 3, "l", "ABCD", "{all} played cards at the Anchor.")
T("social", 3, "l", "ABCD", "{a} had {others} round for dinner.", b="ctdo")
T("social", 3, "l", "ABCD", "{all} went out on a boat for the day.", b="ctdo")
T("social", 3, "l", "ABCD", "{all} walked the coast road on Sunday.", a="tdo", b="tdo")
T("quarrel", 3, "l", "BCD", "{all} argued about the football at the Anchor.", tags=["conflict"])
T("everyday", 3, "u", "ABCD", "{all} were in the Courier's photograph of the quay.", a="ctdo", b="ctdo")
T("luck", 3, "u", "BCD", "{all} won the quiz night at the Anchor.")

RELS = ("partner", "family", "coworker", "bandmate", "other")


# ---------------------------------------------------------------- the generator


class Off:
    def __init__(self, W):
        self.W = W
        self.kinds, self.fest = classify(W)
        self.log = []
        # guards
        self.couple_end = {}  # pair -> month a couple ends by split, divorce or leaving
        for c in W.couples:
            if c.get("ends_how") in ("split", "divorce", "left"):
                self.couple_end[(c["a"], c["b"])] = c["end"]
        self.dismissed = {e["who"][1]: mi(e["at"]) for e in W.E if e["type"] == "dismiss"}
        self.bereaved = collections.defaultdict(list)  # p -> months of a close death
        for d, m in W.died.items():
            if m < W.START:
                continue
            close = set(W.fam[d]) | {W.partner_at(d, m - 1)} - {None}
            for p in close:
                if p:
                    self.bereaved[p].append(m)
        # how often the real run's pairs are partners, family, workmates, bandmates or others, for
        # someone with or without a partner and a job that year: people meet the people they live and
        # work with as often as in the real run, though what they do together is generic
        share = collections.defaultdict(collections.Counter)
        for e in W.E:
            if self.kinds[e["id"]] == "generic" and len(e["who"]) >= 2:
                s, m = e["who"][0], mi(e["at"])
                share[self.profile(s, m // 12)][W.relation(s, e["who"][1], m)] += 1
        self.rel_share = {pr: {r: (c[r] + 0.5) / (sum(c.values()) + 2.5) for r in RELS} for pr, c in share.items()}
        self.once = set()
        self.conflict_pairs = set()
        self.purchases = collections.defaultdict(list)  # p -> [(key, label, m)]

    def profile(self, s, y):
        W = self.W
        ms = [m for m in W.free[s] if m // 12 == y]
        partner = any(W.partner_at(s, m) and m in W.free[W.partner_at(s, m)] for m in ms)
        job = any(W.job[s].get(m) for m in ms)
        return (partner, job)

    # ------------------------------------------------ guards for one template at one month
    def allowed(self, tpl, who, m):
        W = self.W
        s = who[0]
        if "health" in tpl["tags"] and s in W.died and 0 <= W.died[s] - m <= 24:
            return False
        if "mood-" in tpl["tags"] and any(0 <= m - d <= 12 for d in self.bereaved.get(s, [])):
            return False
        if "work-" in tpl["tags"] and s in self.dismissed and 0 <= self.dismissed[s] - m <= 12:
            return False
        if "conflict" in tpl["tags"]:
            for q in who[1:]:
                pair = tuple(sorted((s, q)))
                end = self.couple_end.get(pair)
                if end is not None and 0 <= end - m <= 12:
                    return False
                if (pair, ty(m)) in self.conflict_pairs:
                    return False
        if tpl["once"] and (s, tpl["once"]) in self.once:
            return False
        sp = tpl["special"]
        if sp == "young" and not 17 <= W.age(s, m) <= 40:
            return False
        if sp in ("bday", "round") and (m % 12) != (W.born[s] % 12):
            return False
        if sp == "round" and (W.age(s, m) % 10 != 0 or W.age(s, m) < 30):
            return False
        if sp == "engaged":
            c = W.couple_of(s, who[1], m)
            if not c or c["married"] is not None or ("engaged", c["a"], c["b"]) in self.once:
                return False
            later = [x for x in W.couples if {x["a"], x["b"]} == {s, who[1]} and x["married"]]
            if not any(0 < x["married"] - m <= 24 for x in later):
                return False
        if sp in ("car", "boat") and W.age(s, m) < 18:
            return False
        return True

    def fits(self, tpl, who, m, vis, nb):
        W = self.W
        n = min(len(who), 3)
        s = who[0]
        if tpl["special"] == "away":
            if m in W.present[s] or (s in W.died and m >= W.died[s]):
                return False
        elif m not in W.free[s]:
            return False
        if tpl["n"] != n or {"private": "p", "local": "l", "public": "u"}[vis] not in tpl["vis"]:
            return False
        if nb is not None and nb not in tpl["bands"]:
            return False
        if W.age_class(who[0], m) not in tpl["a"]:
            return False
        if any(W.age_class(q, m) not in tpl["b"] for q in who[1:]):
            return False
        if tpl["job"] and not W.job[who[0]].get(m):
            return False
        if n == 2:
            r = W.relation(who[0], who[1], m)
            need = tpl["rel"]
            if need == "partner" and r != "partner":
                return False
            if need == "family" and r != "family":
                return False
            if need == "close" and r not in ("partner", "family"):
                return False
            if need == "coworker" and r != "coworker":
                return False
            if need == "apart" and r == "partner":
                return False
        return self.allowed(tpl, who, m)

    def pick_template(self, R, who, months, vis, nb):
        """Choose a month and a template; a birthday template moves the event to the birth month."""
        W = self.W
        ms = sorted(months)
        m = R.choice(ms)
        bm = [x for x in ms if x % 12 == W.born[who[0]] % 12]
        for relax in (False, True):
            cands = [(t, m) for t in TPL if self.fits(t, who, m, vis, None if relax else nb)]
            if bm and not relax:
                cands += [(t, bm[0]) for t in TPL if t["special"] in ("bday", "round")
                          and self.fits(t, who, bm[0], vis, nb)]
            if cands:
                # specials are rare by nature: weight them down
                weights = [t["w"] * (0.25 if t["special"] in ("bday", "round", "car", "boat") else 1.0)
                           for t, _ in cands]
                t, mm = R.choices(cands, weights)[0]
                return t, mm
        return None, m

    def commit(self, tpl, who, m):
        s = who[0]
        if tpl["once"]:
            self.once.add((s, tpl["once"]))
        if tpl["special"] == "engaged":
            c = self.W.couple_of(s, who[1], m)
            self.once.add(("engaged", c["a"], c["b"]))
        if "conflict" in tpl["tags"]:
            for q in who[1:]:
                self.conflict_pairs.add((tuple(sorted((s, q))), ty(m)))
        if tpl["special"] == "car":
            self.purchases[s].append(("car", "a car", m))
        if tpl["special"] == "boat":
            self.purchases[s].append(("boat", "a boat of {} own".format(PRON[self.W.P[s]["sex"]]["his"]), m))

    # ------------------------------------------------ build
    def build(self):
        W = self.W
        out = []  # dicts with real id kept as _src for the check
        kinds = self.kinds

        # 1. outcomes re-dealt: shows, songs, open nights, harbour days, festival parts and nights
        R = rng("outcomes")
        deal = {}
        for name, sel, tier in (
            ("show", lambda e: e["type"] == "group:show", show_tier),
            ("song", lambda e: e["type"] == "group:work", song_tier),
            ("open", lambda e: kinds[e["id"]] == "opennight", open_tier),
            ("harbour", lambda e: e["type"].startswith("harbour:"), lambda x: None),
            ("part", lambda e: kinds[e["id"]] == "fest:part", lambda x: None),
        ):
            evs = [e for e in W.E if sel(e)]
            pool = [((tier(e["text"]) if name not in ("harbour", "part") else e["type"]), e["notability"]) for e in evs]
            R.shuffle(pool)
            for e, o in zip(evs, pool):
                deal[e["id"]] = o
        # festivals: the council's answer drawn at the real rate for festivals, then the nights re-dealt
        fest_kind = [v for v in W.D["ventures"] if v["kind"] == "festival"]
        yes_rate = sum(v["council"] == "yes" for v in fest_kind) / len(fest_kind)
        present_v = [v for v in W.D["ventures"] if any(x in W.EID for x in v["events"])]
        council = {v["id"]: ("yes" if R.random() < yes_rate else "no") for v in present_v}
        nights = [e for e in W.E if kinds[e["id"]] == "fest:night" and council[self.fest[e["id"]]] == "yes"]
        npool = [(e["type"], e["notability"]) for e in W.E if kinds[e["id"]] == "fest:night"]
        R.shuffle(npool)
        for e, o in zip(nights, npool):
            deal[e["id"]] = o
        self.council = council

        # 2. the generic slots: one per real generic event, keeping subject, year, visibility,
        #    notability and size. Months and others are drawn later.
        slots = []
        for e in W.E:
            if kinds[e["id"]] == "generic":
                slots.append({"src": e["id"], "s": e["who"][0], "y": e["at"]["year"], "vis": e["vis"],
                              "nb": e["notability"], "n": len(e["who"]), "realm": mi(e["at"])})

        # 3. festival helpers re-drawn: a new helper takes the festival line and hands one of their
        #    own generic slots of the same year, visibility, band and size to the old helper.
        R = rng("helpers")
        swap = {}  # real festival event id -> new subject
        helpers = collections.defaultdict(list)
        for v in present_v:
            evs = [W.EID[x] for x in v["events"] if x in W.EID]
            old = []
            for e in evs:
                if kinds[e["id"]] in ("fest:ask", "fest:part") and e["who"][0] not in old:
                    old.append(e["who"][0])
            # the real crew came because of who the owner regards; the off crew is drawn from everyone else
            taken = {v["owner"]} | set(v["helpers"]) | {e["who"][0] for e in evs if e["type"] == "notthetime"}
            for h in old:
                mine = [e for e in evs if kinds[e["id"]] in ("fest:ask", "fest:part") and e["who"][0] == h]
                cands = [p for p in W.order if p not in taken and p != h and
                         all(mi(e["at"]) in W.free[p] and W.age(p, mi(e["at"])) >= 18 for e in mine)]
                R.shuffle(cands)
                done = False
                # first someone with a free line of the same band; failing that, of any band
                for strict in (True, False):
                    for c in cands:
                        picks, used = [], set()
                        for e in mine:
                            nb = deal[e["id"]][1] if e["id"] in deal else e["notability"]
                            ok = [i for i, sl in enumerate(slots) if i not in used and sl["s"] == c and
                                  sl["y"] == e["at"]["year"] and sl["vis"] == e["vis"] and sl["n"] == len(e["who"])
                                  and (band(sl["nb"]) == band(nb) or not strict)]
                            if not ok:
                                break
                            i = R.choice(ok)
                            used.add(i)
                            picks.append(i)
                        if len(picks) == len(mine):
                            for e, i in zip(mine, picks):
                                swap[e["id"]] = c
                                # the old helper keeps the line's place in their year as a generic slot
                                slots[i]["s"] = h
                            taken.add(c)
                            done = True
                            break
                    if done:
                        break
                if not done:
                    taken.add(h)
                    for e in mine:
                        swap[e["id"]] = h
                    self.log.append(f"helper kept: {W.P[h]['name']} on {v['id']}")
            for e in evs:
                if e["type"] == "pitchin":
                    helpers[v["id"]].append(swap[e["id"]])

        # 4. the others in generic events and festival nights come from each year's pool of real
        #    co-participations, so every person keeps their number of events per year.
        R = rng("others")
        need = []  # (key, subject, k, months, prefer)
        for i, sl in enumerate(slots):
            if sl["n"] > 1:
                need.append((("slot", i), sl["s"], sl["n"] - 1, sl["y"], ()))
        for e in W.E:
            if kinds[e["id"]] == "fest:night":
                need.append((("night", e["id"]), e["who"][0], len(e["who"]) - 1, e["at"]["year"],
                             tuple(helpers[self.fest[e["id"]]])))
        pool = collections.defaultdict(collections.Counter)
        for e in W.E:
            if kinds[e["id"]] in ("generic", "fest:night"):
                for w in e["who"][1:]:
                    pool[e["at"]["year"]][w] += 1
        months_of = lambda p, y: {m for m in W.free[p] if m // 12 == y}
        assigned = {}
        for y in sorted({n[3] for n in need}):
            ny = [n for n in need if n[3] == y]
            R.shuffle(ny)
            # each event first draws the kind of tie it will be, at the real shares for its subject's
            # profile; partners are matched first, as they are the scarcest
            want = {}
            for key, s, k, _, prefer in ny:
                sh = self.rel_share.get(self.profile(s, y)) or self.rel_share[(False, False)]
                want[key] = R.choices(RELS, [sh[r] for r in RELS])[0]
            ny.sort(key=lambda n: (-(W.age_class(n[1], y * 12) in "ct"), RELS.index(want[n[0]])))
            left = pool[y]
            unfilled = []
            for key, s, k, _, prefer in ny:
                chosen = []
                ms = months_of(s, y) or {y * 12}
                for _ in range(k):
                    # first the kind of tie, at the real run's shares (people meet partners, workmates and
                    # family as often as in the real run), then the person, weighted by what they have left
                    by_rel = collections.defaultdict(list)
                    for q in sorted(left):
                        if left[q] <= 0 or q == s or q in chosen:
                            continue
                        mq = ms & months_of(q, y)
                        if not mq:
                            continue
                        m0 = min(mq)
                        if not self.age_ok(s, q, m0):
                            continue
                        by_rel[W.relation(s, q, m0)].append((q, left[q] * (5.0 if q in prefer else 1.0)))
                    if not by_rel:
                        break
                    r = want[key] if not chosen and by_rel[want[key]] else None
                    if r is None:
                        sh = self.rel_share.get(self.profile(s, y)) or self.rel_share[(False, False)]
                        kinds_ = [x for x in RELS if by_rel[x]]
                        r = R.choices(kinds_, [sh[x] for x in kinds_])[0]
                    q = R.choices([x for x, _ in by_rel[r]], [w for _, w in by_rel[r]])[0]
                    chosen.append(q)
                    left[q] -= 1
                    ms = ms & months_of(q, y)
                assigned[key] = chosen
                if len(chosen) < k:
                    unfilled.append((key, s, k))
            # repair: swap a leftover person into an event that can take them, freeing someone who fits
            for key, s, k in unfilled:
                while len(assigned[key]) < k:
                    spare = [q for q in sorted(left) if left[q] > 0]
                    placed = False
                    for q in spare:
                        if self.can_join(s, assigned[key], q, y, months_of):
                            assigned[key].append(q)
                            left[q] -= 1
                            placed = True
                            break
                    if not placed:
                        for okey, os_, ok_, _, _ in ny:
                            if okey == key:
                                continue
                            for j, r in enumerate(assigned[okey]):
                                rest = assigned[okey][:j] + assigned[okey][j + 1:]
                                if r in assigned[key] or not self.can_join(s, assigned[key], r, y, months_of):
                                    continue
                                for q in spare:
                                    if self.can_join(os_, rest, q, y, months_of):
                                        assigned[okey][j] = q
                                        left[q] -= 1
                                        assigned[key].append(r)
                                        placed = True
                                        break
                                if placed:
                                    break
                            if placed:
                                break
                    if not placed:
                        # nobody fits: take anyone present (logged; the check reports the count)
                        ms = months_of(s, y)
                        anyone = [q for q in W.order if q != s and q not in assigned[key] and ms & months_of(q, y)
                                  and self.age_ok(s, q, min(ms & months_of(q, y)))]
                        q = R.choice(anyone)
                        assigned[key].append(q)
                        self.log.append(f"{y}: no pooled partner for {W.P[s]['name']}; took {W.P[q]['name']}")
            for q, c in left.items():
                if c > 0:
                    self.log.append(f"{y}: {c} unused co-appearance(s) of {W.P[q]['name']}")

        # 5. write every event
        R = rng("texts")
        title_r = rng("titles")
        titles = {}
        for e in W.E:
            k = kinds[e["id"]]
            m = mi(e["at"])
            src = e["id"]
            if k == "state":
                out.append(self.ev(e["at"], e["type"], list(e["who"]), state_text(W, e), e["vis"], e["notability"],
                                   src, "cast"))
            elif k == "band":
                g = W.band_of(e)
                gname = next(n for n, v in W.bands.items() if v == g)
                if e["type"] == "group:show":
                    tier, nb = deal[src]
                    txt = SHOW_TXT[tier].format(band=gname)
                    typ = "band:show"
                elif e["type"] == "group:work":
                    tier, nb = deal[src]
                    while True:
                        t = f"{title_r.choice(SONG_A)} {title_r.choice(SONG_B)}"
                        if t not in titles.values():
                            break
                    titles[src] = t
                    txt = fill(W, SONG_TXT[tier], e["who"], m, {"band": gname, "title": t})
                    typ = "band:song"
                elif e["type"] == "notpicked":
                    nb = e["notability"]
                    txt = fill(W, "{a} tried out for {band}; {b} got the place.", e["who"], m, {"band": gname})
                    typ = "band:tryout"
                else:
                    nb = e["notability"]
                    pool_ = BAND_TALK if len(e["who"]) == 2 else BAND_TALK3
                    txt = fill(W, R.choice(pool_), e["who"], m, {"band": gname})
                    typ = "band:practice"
                out.append(self.ev(e["at"], typ, list(e["who"]), cap(txt), e["vis"], nb, src, "lives-off"))
            elif k == "opennight":
                tier, nb = deal[src]
                out.append(self.ev(e["at"], "opennight", list(e["who"]), fill(W, OPEN_TXT[tier], e["who"], m),
                                   e["vis"], nb, src, "lives-off"))
            elif k == "harbour":
                if e["type"] == "stepup":
                    txt = fill(W, "{a} is organising the harbour day this year.", e["who"], m)
                    nb = e["notability"]
                else:
                    o, nb = deal[src]
                    txt = fill(W, HARBOUR_TXT[o], e["who"], m)
                out.append(self.ev(e["at"], "harbourday", list(e["who"]), txt, e["vis"], nb, src, "lives-off"))
            elif k.startswith("fest:"):
                role = k[5:]
                v = self.fest[src]
                yes = council[v] == "yes"
                owner = next(x for x in W.D["ventures"] if x["id"] == v)["owner"]
                nb = e["notability"]
                if role == "plan":
                    who = [owner]
                    txt = fill(W, "{a} is putting on a summer festival on the quay this year.", who, m)
                elif role == "ask":
                    who = [swap[src], owner]
                    if e["type"] == "pitchin":
                        txt = fill(W, "{a} said yes to helping {b} with the summer festival.", who, m)
                    else:
                        txt = fill(W, "{a} said no to helping {b} with the summer festival.", who, m)
                elif role == "council":
                    who = list(e["who"])
                    txt = fill(W, "The council said " + ("yes" if yes else "no") + " to {a}'s summer festival.",
                               who, m)
                elif role == "part":
                    who = [swap[src]]
                    o, nb = deal[src]
                    txt = fill(W, PART_TXT[o] if yes else "{a} had been getting ready for the summer festival.",
                               who, m)
                else:  # night
                    who = [owner] + assigned[("night", src)]
                    if yes:
                        o, nb = deal[src]
                        txt = fill(W, "The summer festival {a} put on was a fine night on the quay." if o == "night:good"
                                   else "The summer festival {a} put on was a washout.", who, m)
                    else:
                        txt = fill(W, "The summer festival {a} planned did not go ahead.", who, m)
                out.append(self.ev(e["at"], "festival", who, txt, e["vis"], nb, src, "lives-off"))
        # generic events, in a seeded order
        order = list(range(len(slots)))
        R.shuffle(order)
        for i in order:
            sl = slots[i]
            who = [sl["s"]] + assigned.get(("slot", i), [])
            ms = {m for m in W.free[sl["s"]] if m // 12 == sl["y"]}
            for q in who[1:]:
                ms &= W.free[q]
            if not ms and len(who) == 1:
                # someone away all that year: lines about them come from away
                ms = {m for m in range(sl["y"] * 12, sl["y"] * 12 + 12) if W.START <= m <= W.END
                      and m not in W.present[sl["s"]] and not (sl["s"] in W.died and m >= W.died[sl["s"]])}
            if not ms:
                ms = {sl["realm"]}
                self.log.append(f"no free month for {W.P[sl['s']]['name']} in {sl['y'] + SHIFT}; kept the real one")
            tpl, m = self.pick_template(R, who, ms, sl["vis"], band(sl["nb"]))
            if tpl is None:
                raise RuntimeError(f"no template for {who} {sl}")
            self.commit(tpl, who, m)
            out.append(self.ev(at_of(m), tpl["cat"], who, cap(fill(W, tpl["text"], who, m)), sl["vis"], sl["nb"],
                               sl["src"], "lives-off", tpl=tpl))
        out.sort(key=lambda x: (mi(x["at"]), int(x["_src"][2:])))
        idmap = {}
        for k, x in enumerate(out):
            x["id"] = f"e-{10001 + k}"
            idmap[x["_src"]] = x["id"]
        self.idmap = idmap
        self.helpers = helpers
        return out

    def age_ok(self, s, q, m):
        """Children meet family and other children; teens meet anyone, adults meet adults."""
        W = self.W
        cs, cq = W.age_class(s, m), W.age_class(q, m)
        if "c" in (cs, cq):
            return W.relation(s, q, m) == "family" or (cs in "ct" and cq in "ct")
        return True

    def can_join(self, s, others, q, y, months_of):
        if q == s or q in others:
            return False
        ms = {m for m in self.W.free[s] if m // 12 == y}
        for o in others + [q]:
            ms &= months_of(o, y)
        return bool(ms) and self.age_ok(s, q, min(ms))

    def ev(self, at, typ, who, text, vis, nb, src, prov, tpl=None):
        x = {"id": None, "at": {"year": at["year"], "month": at["month"]}, "type": typ, "who": who, "text": text,
             "causes": [], "vis": vis, "notability": nb, "provenance": prov, "_src": src}
        if tpl is not None:
            x["_tags"] = sorted(tpl["tags"])
        return x


# ---------------------------------------------------------------- the file


HABIT_NEEDS = {
    "is first in at work every morning": "job",
    "rings their mother every Sunday evening": "mother",
    "has two pints at the Anchor most evenings": "adult",
    "is at the Anchor every Friday without fail": "adult",
    "plays cards at the Anchor on Tuesdays": "adult",
    "is out on the boat every weekend": "adult",
}


def write_world(W, off, events):
    D = W.D
    R = rng("cast")
    habit_def = {}
    for p in D["people"]:
        for h in p["habits"]:
            habit_def.setdefault(h["label"], {k: h[k] for k in ("kind", "place") if k in h})
    labels = sorted(habit_def)
    people = []
    for p in D["people"]:
        q = dict(p)
        pid = p["id"]
        # routines: as many as the real person has, drawn fresh, never lapsed
        ok = []
        for lab in labels:
            need = HABIT_NEEDS.get(lab)
            last_age = (min(W.died.get(pid, W.END), W.END) - W.born[pid]) // 12
            if need == "job" and not p["job"]:
                continue
            if need == "adult" and last_age < 18:
                continue
            if need == "mother":
                mothers = [x for x in p["parents"] if W.P[x]["sex"] == "f" and W.P[x]["status"] != "dead"]
                if not mothers:
                    continue
            ok.append(lab)
        picks = R.sample(ok, min(len(p["habits"]), len(ok)))
        lo = W.born[pid] + 16 * 12
        home_since = mi(next(a for a in p["attachments"] if a["key"] == "home")["since"])
        lo = max(lo, home_since)
        hi = max(lo, min(W.START - 1, W.died.get(pid, W.START) - 1))
        habits = []
        for lab in sorted(picks):
            h = {"label": lab}
            h.update(habit_def[lab])
            h["since"] = at_of(R.randint(lo, hi) if hi > lo else lo)
            habits.append(h)
        q["attachments"] = [a for a in p["attachments"] if a["key"] == "home"] + [
            {"key": key, "label": label, "since": at_of(m)} for key, label, m in off.purchases.get(pid, [])
        ]
        q["habits"] = habits
        q["provenance"] = "cast"
        people.append(q)

    ventures = []
    Rv = rng("ventures")
    rates = {}
    for kind in sorted({v["kind"] for v in D["ventures"]}):
        vs = [v for v in D["ventures"] if v["kind"] == kind]
        rates[kind] = sum(v["status"] == "done" for v in vs) / len(vs)
    for v in D["ventures"]:
        x = dict(v)
        present = any(e in W.EID for e in v["events"])
        if present:
            yes = off.council[v["id"]] == "yes"
            x["helpers"] = off.helpers[v["id"]]
            x["events"] = [off.idmap[e] for e in v["events"] if e in off.idmap]
        else:
            if v.get("place"):
                yes = True  # the café that is a place of work today
            elif v["kind"] == "cafe":
                yes = False  # a café that opened would be a place that does not exist
            else:
                yes = Rv.random() < rates[v["kind"]]
            # the town has no history: a past venture keeps its kind, owner and dates for shape, and
            # nobody backed or fought it
            x["helpers"] = []
            x["events"] = []
        others = [p for p in W.order if p not in x["helpers"] and p != v["owner"] and W.born[p] + 18 * 12 <= mi(v["since"])
                  and W.died.get(p, 10 ** 9) > mi(v["since"])]
        x["opponents"] = sorted(Rv.sample(others, len(v["opponents"])), key=lambda p: int(p[2:])) if present else []
        x["status"] = "done" if yes else "failed"
        x["council"] = "yes" if yes else "no"
        x["provenance"] = "lives-off"
        ventures.append(x)

    groups = []
    for g in D["groups"]:
        x = dict(g)
        if "how" in x:
            x["how"] = "they stopped playing"
        x["events"] = [off.idmap[e] for e in g["events"] if e in off.idmap]
        x["provenance"] = "cast"
        groups.append(x)

    evs = []
    for e in events:
        evs.append({k: e[k] for k in ("id", "at", "type", "who", "text", "causes", "vis", "notability", "provenance")})

    doc = {
        "schemaVersion": D["schemaVersion"],
        "rulesetVersion": f"{VERSION} over {D['rulesetVersion']}",
        "worldSeed": D["worldSeed"],
        "runSeed": SEED,
        "at": D["at"],
        "presentFrom": D["presentFrom"],
        "eventsFrom": D["eventsFrom"],
        "notes": [
            "The lives-off control arm of paper playtest 1 (reviews/lt1/playtests/paper-1/world/world-9989-off.md), "
            "written by world/tools/lives_off.py from understory-world-9989.json. Game masters only; players never "
            "see a file.",
            "The cast is the real run's: names, sexes, births, deaths, jobs and workplaces, households, partners, "
            "bands and ventures, with their dates. Every life event is replaced by a generic, cause-free line of "
            "the same person, year, visibility, notability band and size. No causes, no reasons, no memory.",
            "Band shows, songs, open nights, harbour days and festival parts and nights keep their counts and "
            "dates; their outcomes are re-dealt at random from the real ones. Festival helpers are re-drawn.",
            "Routines are drawn fresh and never lapse; attachments are only home and what the off events buy. "
            "The town has no history: past ventures and bands are kept for shape only and never shown.",
            "Dates are engine years, like the real file: the town year is the engine year - 37. "
            "Weights and notability are per mille; every causes list is empty.",
        ],
        "people": people,
        "households": D["households"],
        "places": D["places"],
        "ventures": ventures,
        "groups": groups,
        "events": evs,
    }
    with open(OUT, "w") as f:
        json.dump(doc, f, indent=1, ensure_ascii=False)
        f.write("\n")
    return doc


# ---------------------------------------------------------------- the check

BANNED = re.compile(
    r"\b(again|still|finally|at last|since|because|ever|anymore|any more|remember\w*|forgave|forgive\w*|owed?|owes|owing|"
    r"lent|borrow\w*|promis\w*|secret\w*|grudge|blame\w*|found out|never did|after \d+|years? of|"
    r"the first time|third time|happened before|19\d\d|20\d\d)\b",
    re.I,
)


def check(W, doc, off=None):
    real = W.E
    offe = doc["events"]
    print(f"World 9989, lives off: check ({doc['rulesetVersion']}, seed {doc['runSeed']})")
    print(f"  events: real {len(real)}, off {len(offe)}")
    print(f"  people {len(doc['people'])}, households {len(doc['households'])}, places {len(doc['places'])}, "
          f"ventures {len(doc['ventures'])}, bands {len(doc['groups'])}")

    def table(evs):
        subj = collections.Counter()
        inv = collections.Counter()
        vis = collections.Counter()
        nb = collections.Counter()
        for e in evs:
            y = e["at"]["year"]
            s = e["who"][0]
            subj[(s, y)] += 1
            vis[(s, y, e["vis"])] += 1
            nb[(s, y, band(e["notability"]))] += 1
            for w in e["who"]:
                inv[(w, y)] += 1
        return subj, inv, vis, nb

    rs, ri, rv, rb = table(real)
    os_, oi, ov, ob = table(offe)
    keys = sorted(set(rs) | set(os_))
    ikeys = sorted(set(ri) | set(oi))

    def per_py(rc, oc, cats):
        same = 0
        diff = []
        for k in keys:
            a = tuple(rc.get(k + (c,), 0) for c in cats)
            b = tuple(oc.get(k + (c,), 0) for c in cats)
            if a == b:
                same += 1
            else:
                diff.append((k, a, b))
        return same, diff

    same_s = sum(rs.get(k, 0) == os_.get(k, 0) for k in keys)
    same_i = sum(ri.get(k, 0) == oi.get(k, 0) for k in ikeys)
    sv, dv = per_py(rv, ov, ("private", "local", "public"))
    sb, db = per_py(rb, ob, "ABCD")
    print(f"\n  per person-year ({len(keys)} person-years with events as subject, {len(ikeys)} with any part):")
    print(f"    events as subject      same in {same_s}/{len(keys)}")
    print(f"    events taking part in  same in {same_i}/{len(ikeys)}")
    print(f"    visibility mix         same in {sv}/{len(keys)}")
    print(f"    notability-band mix    same in {sb}/{len(keys)}")
    if db:
        moved = sum(sum(abs(x - y) for x, y in zip(a, b)) for _, a, b in db) // 2
        # every difference must come from a re-dealt outcome or a festival helper: the generic lines keep
        # their notability exactly
        dealt = {"band:show", "band:song", "opennight", "harbourday", "festival"}
        touched = {(e["who"][0], e["at"]["year"]) for e in offe if e["type"] in dealt}
        touched |= {(e["who"][0], e["at"]["year"]) for e in real if e["type"] in
                    ("group:show", "group:work", "performed", "harbour:ran", "harbour:ok", "harbour:chaos")
                    or e["type"] in FEST_ROLE}
        other = [k for k, _, _ in db if k not in touched]
        print(f"      the {len(db)} that differ: {moved} event(s) moved one band or more; "
              f"{len(db) - len(other)} of {len(db)} are people with a re-dealt outcome or a festival line that year")
        for (p, y), a, b in db[:6]:
            print(f"        {W.P[p]['name']} {y + SHIFT}: real A-D {a}, off {b}")
    if same_i != len(ikeys):
        for k in ikeys:
            if ri.get(k, 0) != oi.get(k, 0):
                print(f"      taking part differs: {W.P[k[0]]['name']} {k[1] + SHIFT}: real {ri.get(k, 0)}, off "
                      f"{oi.get(k, 0)}")

    def dist(evs, f):
        return collections.Counter(f(e) for e in evs)

    print("\n  whole run, real -> off:")
    for label, f, cats in (
        ("visibility", lambda e: e["vis"], ("private", "local", "public")),
        ("notability band", lambda e: band(e["notability"]), "ABCD"),
        ("people per event", lambda e: min(len(e["who"]), 4), (1, 2, 3, 4)),
    ):
        a, b = dist(real, f), dist(offe, f)
        print(f"    {label:17s} " + "  ".join(f"{c}: {a[c]}->{b[c]}" for c in cats))
    a = dist(real, lambda e: e["at"]["year"])
    b = dist(offe, lambda e: e["at"]["year"])
    print("    per town year      " + "  ".join(f"{y + SHIFT}: {a[y]}->{b[y]}" for y in sorted(a)))
    st = sorted(STATE_T)
    a = dist([e for e in real if e["type"] in STATE_T], lambda e: e["type"])
    b = dist([e for e in offe if e["type"] in STATE_T], lambda e: e["type"])
    print("    kept states        " + ", ".join(f"{t} {a[t]}/{b[t]}" for t in st if a[t] or b[t]))
    a = sum(1 for e in real if e["causes"])
    b = sum(1 for e in offe if e["causes"])
    print(f"    events with causes {a} -> {b}; with a decision {sum('decision' in e for e in real)} -> "
          f"{sum('decision' in e for e in offe)}")

    # outcomes
    print("\n  outcomes, real -> off (re-dealt at the real rates):")
    rshow = collections.Counter(show_tier(e["text"]) for e in real if e["type"] == "group:show")
    oshow = collections.Counter(next(k for k, v in SHOW_TXT.items() if e["text"].endswith(v.split("Anchor")[1]))
                                for e in offe if e["type"] == "band:show")
    print(f"    band shows         {dict(rshow)} -> {dict(oshow)}")
    rn = collections.Counter(e["type"] for e in real if e["type"] in ("night:good", "night:bad"))
    on = collections.Counter("night:good" if "fine night" in e["text"] else "night:bad" if "washout" in e["text"]
                             else "off" for e in offe if e["type"] == "festival" and "summer festival" in e["text"]
                             and ("fine night" in e["text"] or "washout" in e["text"] or "did not go" in e["text"]))
    print(f"    festival nights    {dict(rn)} -> {dict(on)}")
    if off:
        same_h = []
        for v in doc["ventures"]:
            rv_ = next(x for x in W.D["ventures"] if x["id"] == v["id"])
            if v["events"]:
                same_h.append(len(set(v["helpers"]) & set(rv_["helpers"])))
        print(f"    festival helpers   kept from the real crew per present festival: {same_h}")

    # consistency
    print("\n  consistency:")
    bad = []
    srcs = {}
    for e in offe:
        m = mi(e["at"])
        who = e["who"]
        if len(set(who)) != len(who):
            bad.append(f"{e['id']} repeats a person")
        if e["type"] in STATE_T:
            continue
        for w in who:
            if e["type"] == "away" and m not in W.present[w] and not (w in W.died and m >= W.died[w]):
                continue
            if m not in W.free[w] and not (e["type"] in ("band:show", "band:song", "band:practice", "band:tryout",
                                                         "opennight", "harbourday", "festival")
                                           and m in W.present[w]):
                bad.append(f"{e['id']} {W.P[w]['name']} not in town or not alive in {ty(m)}-{m % 12 + 1:02d}")
        if BANNED.search(e["text"]):
            bad.append(f"{e['id']} reaches back or carries a reason: {e['text']}")
    # arcs
    arcs = []
    for e in offe:
        if e["type"] == "health" and e["who"][0] in W.died and 0 <= W.died[e["who"][0]] - mi(e["at"]) <= 24:
            arcs.append(f"{e['id']} illness before a death: {e['text']}")
        if e["type"] == "couple" and W.partner_at(e["who"][0], mi(e["at"])) != e["who"][1]:
            arcs.append(f"{e['id']} couple line for people who are not a couple: {e['text']}")
        if e["type"] == "work" and not W.job[e["who"][0]].get(mi(e["at"])):
            arcs.append(f"{e['id']} work line for someone without a job: {e['text']}")
        for w in e["who"]:
            if W.age(w, mi(e["at"])) < 18 and any(k in e["text"] for k in ("a drink", "a pint", "pints", "played cards at the Anchor")):
                arcs.append(f"{e['id']} a child at the bar: {e['text']}")
    dead_named = 0  # by id: two Evan Newmans and two Amelia Wallers share a name
    for e in offe:
        if e["type"] in STATE_T:
            continue
        dead_named += sum(1 for w in e["who"] if w in W.died and mi(e["at"]) >= W.died[w])
    print(f"    people in town and alive at every event they take part in: "
          f"{'yes' if not [b for b in bad if 'not in town' in b] else 'NO'}")
    print(f"    lines that reach back or give a reason (again, still, since, because, a year, owed, promised, "
          f"secret...): {len([b for b in bad if 'reaches back' in b])}")
    print(f"    illness before a death, couple lines for non-couples, work lines without a job, children at the "
          f"bar: {len(arcs)}")
    print(f"    the dead named after their death outside the kept states: {dead_named}")
    for b in (bad + arcs)[:10]:
        print("      " + b)
    if off and off.log:
        print(f"\n  generator notes ({len(off.log)}):")
        for x in off.log[:12]:
            print("    " + x)
    ok = (same_s == len(keys) and sv == len(keys) and not bad and not arcs and dead_named == 0
          and (not db or not other))
    print(f"\n  result: {'PASS' if ok else 'CHECK THE LINES ABOVE'}: same events per person-year "
          f"{same_s}/{len(keys)}, same visibility {sv}/{len(keys)}, same notability bands {sb}/{len(keys)}, "
          f"taking part {same_i}/{len(ikeys)}")
    return ok


# ---------------------------------------------------------------- a person, side by side


def person(W, doc, name, y0=1989, y1=1999):
    pid = next(p for p in W.order if W.P[p]["name"].lower() == name.lower() or p == name)
    print(f"{W.P[pid]['name']} ({pid}), town years {y0}-{y1}")
    for label, evs in (("REAL", W.E), ("OFF", doc["events"])):
        print(f"\n  {label}")
        for e in evs:
            if pid in e["who"] and y0 <= e["at"]["year"] + SHIFT <= y1:
                why = ""
                if e.get("causes"):
                    why = "  [" + "; ".join(re.sub(r"\b(20[0-4]\d)\b", lambda m: str(int(m.group(1)) + SHIFT),
                                                     c["label"]) for c in e["causes"][:3]) + "]"
                txt = re.sub(r"\b(20[0-4]\d)\b", lambda m: str(int(m.group(1)) + SHIFT), e["text"])
                print(f"    {e['at']['year'] + SHIFT}-{e['at']['month']:02d} {e['vis'][:3]} {e['notability']:>4} "
                      f"{txt}{why}")


def main(argv):
    W = World(REAL)
    cmd = argv[0] if argv else "generate"
    if cmd == "generate":
        off = Off(W)
        events = off.build()
        doc = write_world(W, off, events)
        print(f"wrote {os.path.relpath(OUT, ROOT)}\n")
        ok = check(W, doc, off)
        return 0 if ok else 1
    doc = json.load(open(OUT))
    if cmd == "check":
        return 0 if check(W, doc) else 1
    if cmd == "person":
        rest = argv[1:]
        if len(rest) >= 3 and rest[-1].isdigit() and rest[-2].isdigit():
            person(W, doc, " ".join(rest[:-2]), int(rest[-2]), int(rest[-1]))
        else:
            person(W, doc, " ".join(rest))
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
