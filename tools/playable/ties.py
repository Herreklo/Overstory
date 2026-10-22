#!/usr/bin/env python3
"""Test 1 of the playable corner's ladder: is the first telling a decision? The tie script.

    python3 tools/playable/ties.py [--seed A|B|both] [--json OUT] [--quick]

(`reviews/lt1/playable/outline.md` §3, test 1; `premortem.md` §4, must 3.) Over the engine's export only, for the
case frozen in `reviews/lt1/playable/case-spec.md` (its JSON block, hashed: FROZEN below):

1. **The tie table** at the seed's month, every row with its source and label, and the tie counts first:
   - kin: parents and children (simulated); partners at the month, dated (simulated from the export's partner and
     its `since`; derived from split, divorce and couple events, since the export's partners are 1999's);
   - coworkers: the same place at the month (derived: `facts.World.job_at`, which walks the 1999 staff lists back
     over the job events' text);
   - liking: the sum of the signs of the pair events up to the month (friends, confide, keep +1; cold, coolto,
     dislike, contempt −1), undirected. The export has no liking field; this is a reading of those events.
2. **The spread** (the spec's one rule), the clock, the hours and the walking minutes (from `heart_layout`'s lanes,
   dumped by `layout_dump.py`), and **the score** (the pick's rule).
3. **Every line:** every order of up to four tellings from 10:00, back to back; every first telling; the 27 vantage
   plans; the named lines (the page's, Peter first, the two back to back). Then the sweeps: each spread parameter
   at ½ and 1½ times, each authored hour an hour either side. Seed B last.

The referee (`simulate`, `score`) is kept apart from the parsing (`TieTable`) and has its own toy cases in
`tools/tests/test_ties.py`: the premortem's warning that one script refereeing two tests passes one bug twice.
"""

import argparse
import hashlib
import heapq
import itertools
import json
import math
import re
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import facts  # noqa: E402  (the export's World: dates, people, jobs, habits, kin)

ROOT = Path(__file__).resolve().parents[2]
SPEC = ROOT / "reviews" / "lt1" / "playable" / "case-spec.md"
LAYOUT = ROOT / "reviews" / "lt1" / "playable" / "ladder" / "2a-layout.json"
FROZEN = "876b3185a318b02b396eba56d509412bf17a452fd32c8f07a3c5da2e549d27e4"  # sha256 of case-spec.md's JSON block

PAIR_TYPES = ("friends", "confide", "keep", "cold", "coolto", "dislike", "contempt")
PARTNER_ENDS = ("split", "divorce", "endit")
PARTNER_STARTS = ("dating", "married")
COUPLE_STATES = ("couple:apart", "couple:pattern")
DISLIKE_RE = re.compile(r"^(?P<a>.+?) (?:can't stand|has no time for|cannot be in a room with) (?P<b>.+?)(?: any more| for long)?\.$")


def hhmm(m):
    return "{:02d}:{:02d}".format(int(m) // 60, int(m) % 60)


# -- the frozen case -----------------------------------------------------------------------------------------------

def spec_block(path=SPEC):
    """(the case's frozen JSON, the sha256 of its text) from the spec's one ```json block."""
    text = Path(path).read_text(encoding="utf-8")
    m = re.search(r"```json\n(.*?)\n```", text, re.S)
    if not m:
        raise SystemExit("no ```json block in {}".format(path))
    block = m.group(1)
    return json.loads(block), hashlib.sha256(block.encode("utf-8")).hexdigest()


# -- the tie table (derived from the export; parsing only, no refereeing) -----------------------------------------

def pair_of(world, e):
    """(a, b) for a pair event, or None. A dislike names only its actor in `who`; the other is read from its text."""
    if e["type"] == "dislike":
        m = DISLIKE_RE.match(e["text"])
        if not m:
            return None
        a, b = world.by_name.get(m.group("a")), world.by_name.get(m.group("b"))
        return (a, b) if a and b and a != b else None
    if len(e["who"]) >= 2 and e["who"][0] != e["who"][1]:
        return e["who"][0], e["who"][1]
    return None


def partners_at(world, ym):
    """{frozenset(a, b): (label, sources)}: who is whose partner at ym. The export's partner with its since
    (simulated); a pair that splits, divorces or ends it after ym and did not start after ym (derived); a pair the
    engine calls a couple at or before ym with no end between (derived)."""
    out = {}
    for p in world.people.values():
        q = (p.get("partner") or {}).get("id")
        if q and q in world.people and world.ym(p["partner"]["since"]) <= ym:
            out[frozenset((p["id"], q))] = ("simulated", ["partner.since"])
    starts, ends, states = defaultdict(list), defaultdict(list), defaultdict(list)
    for e in world.events:
        if len(e["who"]) < 2:
            continue
        k = frozenset(e["who"][:2])
        t = world.when(e)
        if e["type"] in PARTNER_STARTS:
            starts[k].append((t, e["id"]))
        elif e["type"] in PARTNER_ENDS:
            ends[k].append((t, e["id"]))
        elif e["type"] in COUPLE_STATES:
            states[k].append((t, e["id"]))
    for k, es in ends.items():
        later = [x for x in es if x[0] > ym]
        if not later:
            continue
        t_end, eid = min(later)
        if any(ym < t <= t_end for t, _ in starts.get(k, [])):
            continue  # they got together after ym
        if any(t <= ym for t, _ in es):
            continue  # an end at or before ym, and nothing restarting it is known
        out.setdefault(k, ("derived", [eid]))
    for k, ss in states.items():
        seen = [x for x in ss if x[0] <= ym]
        if not seen:
            continue
        t0, eid = max(seen)
        if any(t0 <= t <= ym for t, _ in ends.get(k, [])):
            continue
        out.setdefault(k, ("derived", [eid]))
    return out


class TieTable:
    """Every tie at a month: {a: {b: dict(kin, partner, cowork, like, sources)}}, undirected, with labels."""

    def __init__(self, world, ym):
        self.world, self.ym = world, ym
        self.alive = {pid for pid in world.people if world.present(pid, ym)[0] and not
                      (world.died(pid) and world.died(pid) <= ym)}
        self.ties = defaultdict(lambda: defaultdict(lambda: dict(kin=0, partner=0, cowork=0, like=0, sources=[])))
        for pid in self.alive:
            p = world.people[pid]
            for k in list(p.get("kids", [])) + list(p.get("parents", [])):
                if k in self.alive:
                    self._add(pid, k, "kin", 1, "export: parents/kids (simulated)")
        for k, (label, src) in partners_at(world, ym).items():
            a, b = sorted(k)
            if a in self.alive and b in self.alive:
                self._add(a, b, "partner", 1, "partner {} ({})".format(",".join(src), label))
        self.job = {}
        for pid in self.alive:
            place, src = world.job_at(pid, ym)
            if place and place != "?":
                self.job[pid] = (place, src)
        by_place = defaultdict(list)
        for pid, (place, _) in self.job.items():
            by_place[place].append(pid)
        for place, ps in by_place.items():
            for a, b in itertools.combinations(sorted(ps), 2):
                self._add(a, b, "cowork", 1, "{} (derived)".format(place))
        for e in world.events:
            if e["type"] not in PAIR_TYPES or world.when(e) > ym:
                continue
            ab = pair_of(world, e)
            if not ab or ab[0] not in self.alive or ab[1] not in self.alive:
                continue
            sign = -1 if e["type"] in ("cold", "coolto", "dislike", "contempt") else 1
            self._add(ab[0], ab[1], "like", sign, "{} {} (derived)".format(e["id"], e["type"]))

    def _add(self, a, b, kind, n, source):
        for x, y in ((a, b), (b, a)):
            t = self.ties[x][y]
            if kind == "like":
                t["like"] += n
            else:
                t[kind] = 1
            t["sources"].append(source)

    def closeness(self, a, b, rule):
        t = self.ties.get(a, {}).get(b)
        if not t:
            return 0.0
        return rule["w_kin"] * t["kin"] + rule["w_partner"] * t["partner"] + rule["w_cowork"] * t["cowork"] + \
            rule["w_like"] * t["like"]

    def hearers(self, a, rule):
        """a's close hearers, best first: closeness above nothing; ties by id. "A stranger is nobody's."""
        out = [(self.closeness(a, b, rule), b) for b in self.ties.get(a, {}) if b in self.alive]
        out = [(c, b) for c, b in out if c > 0]
        out.sort(key=lambda x: (-x[0], int(x[1][2:])))
        return [b for _, b in out]

    def counts(self, pid):
        ts = self.ties.get(pid, {})
        return dict(kin=sum(t["kin"] for t in ts.values()), partner=sum(t["partner"] for t in ts.values()),
                    cowork=sum(t["cowork"] for t in ts.values()),
                    liked=sum(1 for t in ts.values() if t["like"] > 0), disliked=sum(1 for t in ts.values() if t["like"] < 0),
                    any=len(ts))


# -- the walk: minutes between points over heart_layout's lanes --------------------------------------------------

def poly_dist(x, y, poly):
    """Distance from (x, y) to a polygon: 0 inside, else to its nearest edge."""
    inside = False
    d = 1e18
    n = len(poly)
    for i in range(n):
        (x1, y1), (x2, y2) = poly[i], poly[(i + 1) % n]
        if (y1 > y) != (y2 > y) and x < x1 + (y - y1) * (x2 - x1) / (y2 - y1):
            inside = not inside
        dx, dy = x2 - x1, y2 - y1
        t = max(0.0, min(1.0, ((x - x1) * dx + (y - y1) * dy) / (dx * dx + dy * dy or 1.0)))
        d = min(d, math.hypot(x - x1 - t * dx, y - y1 - t * dy))
    return 0.0 if inside else d


class Walk:
    """Shortest walking times over the dumped lanes: 1.4 m/s, at the spec's share of it on flights (a lane of kind
    "steps", or a slope over 12 percent). A point joins the nearest lane within its half width plus 3 m. The open
    places (the squares, the Landing) are crossed straight: every lane node in one joins every other, and a door on
    one's edge (within 15 m) joins its nearest node."""

    def __init__(self, layout, speed=1.4, flight=0.55, step=4.0):
        self.speed, self.flight = speed, flight
        self.nodes, self.adj = [], defaultdict(list)
        self.lane_nodes = []
        for lane in layout["lanes"]:
            pts = lane["pts"]
            ids = []
            for (x1, y1, z1), (x2, y2, z2) in zip(pts, pts[1:]):
                seg = math.hypot(x2 - x1, y2 - y1)
                n = max(1, int(math.ceil(seg / step)))
                for i in range(n + (1 if (x2, y2) == tuple(pts[-1][:2]) else 0)):
                    t = i / n
                    ids.append(self._node(x1 + (x2 - x1) * t, y1 + (y2 - y1) * t, z1 + (z2 - z1) * t))
            for u, v in zip(ids, ids[1:]):
                self._edge(u, v, lane["kind"])
            self.lane_nodes.append((lane, ids))
        # lanes join where they touch: a node of one within the other's half width (plus half a metre)
        grid = defaultdict(list)
        for li, (lane, ids) in enumerate(self.lane_nodes):
            for u in ids:
                x, y, _ = self.nodes[u]
                grid[(int(x // 10), int(y // 10))].append((li, u))
        for li, (lane, ids) in enumerate(self.lane_nodes):
            for u in ids:
                x, y, _ = self.nodes[u]
                for gx in (-1, 0, 1):
                    for gy in (-1, 0, 1):
                        for lj, v in grid.get((int(x // 10) + gx, int(y // 10) + gy), []):
                            if lj == li:
                                continue
                            other = self.lane_nodes[lj][0]
                            x2, y2, _ = self.nodes[v]
                            if math.hypot(x - x2, y - y2) <= (lane["width"] + other["width"]) / 2 + 0.5:
                                self._edge(u, v, "lane")

        self.squares = []
        for place in layout.get("places", []):
            inside = [u for u in range(len(self.nodes)) if poly_dist(self.nodes[u][0], self.nodes[u][1], place["poly"]) <= 3.0]
            for u, v in itertools.combinations(inside, 2):
                self._edge(u, v, "square")
            if inside:
                self.squares.append((place, inside))

    def _node(self, x, y, z):
        self.nodes.append((x, y, z))
        return len(self.nodes) - 1

    def _edge(self, u, v, kind):
        (x1, y1, z1), (x2, y2, z2) = self.nodes[u], self.nodes[v]
        d = math.hypot(x2 - x1, y2 - y1)
        steep = d > 0 and abs(z2 - z1) / d > 0.12
        sp = self.speed * (self.flight if kind == "steps" or steep else 1.0)
        t = d / sp
        self.adj[u].append((v, t))
        self.adj[v].append((u, t))

    def join(self, x, y):
        best = None
        for lane, ids in self.lane_nodes:
            for u in ids:
                nx, ny, _ = self.nodes[u]
                d = math.hypot(x - nx, y - ny)
                if d <= lane["width"] / 2 + 3.0 and (best is None or d < best[0]):
                    best = (d, u)
        if best is None:
            for place, inside in self.squares:
                if poly_dist(x, y, place["poly"]) <= 15.0:
                    for u in inside:
                        nx, ny, _ = self.nodes[u]
                        d = math.hypot(x - nx, y - ny)
                        if best is None or d < best[0]:
                            best = (d, u)
        if best is None:
            raise ValueError("no lane within reach of ({:.1f}, {:.1f})".format(x, y))
        return best

    def minutes(self, a, b):
        """Walking minutes between two (x, y) points."""
        da, ua = self.join(*a)
        db, ub = self.join(*b)
        dist = {ua: da / self.speed}
        pq = [(dist[ua], ua)]
        while pq:
            t, u = heapq.heappop(pq)
            if u == ub:
                return (t + db / self.speed) / 60.0
            if t > dist.get(u, 1e18):
                continue
            for v, w in self.adj[u]:
                if t + w < dist.get(v, 1e18):
                    dist[v] = t + w
                    heapq.heappush(pq, (t + w, v))
        raise ValueError("no way between {} and {}".format(a, b))


# -- the case: where everyone is, minute by minute (the spec's hours; authored) -----------------------------------

class Case:
    """One seed of the case at its Friday: who is where, when; the walking minutes; the visitors and their values."""

    def __init__(self, spec, seed, world, ties, layout=None, walk=None, hours=None, rule=None):
        self.spec, self.seed, self.world, self.ties = spec, seed, world, ties
        self.s = spec["seeds"][seed]
        self.rule = dict(spec["rule"], **(rule or {}))
        self.hours = dict(spec["hours"], **(hours or {}))
        self.ym = tuple(self.s["month"])
        self.dead = self.s["dead"]
        self.visitors = list(self.s["visitors"])
        self.points = {}
        if layout is not None:
            doors = {b["name"]: tuple(b["door"]) for b in layout["buildings"]}
            for b in layout["buildings"]:
                if len(b["name"]) > 1 and b["name"][0] in "ABCDE" and b["name"][1] == " ":
                    doors[b["name"][0]] = tuple(b["door"])
            for key, where in spec["points"].items():
                self.points[key] = tuple(where) if isinstance(where, list) else doors[where]
        self.walk = walk
        self._minutes = {}
        self.home = {}
        for pid in ties.alive:
            self.home[pid] = self.s["homes"].get(pid, "elsewhere")
        self.player_home = self.s["player_home"]
        self.friday = {pid for pid in ties.alive
                       if any(world.habit_on(pid, core, self.ym)[0] for core in spec["anchor_habits"])}
        self.job = {pid: place for pid, (place, _) in ties.job.items()}
        self.lead = {}
        for place in set(self.job.values()):
            lead, _, _ = world.lead_at(place, self.ym)
            self.lead[place] = lead
        self.bar_from = self.at_anchor_from()

    def at_anchor_from(self):
        """{pid: minute}: when each person is at the Anchor from, until the day's end (its staff by their shift, its
        Friday regulars from the regulars' hour)."""
        out = {}
        for pid in self.ties.alive:
            ts = []
            if pid in self.friday:
                ts.append(self.hours["regulars"])
            sh = self.shift(pid)
            if sh and self.job.get(pid) == "pl-bar":
                ts.append(sh[0])
            if ts:
                out[pid] = min(ts)
        return out

    # where a place or a home is
    def point_of(self, where):
        if where in self.spec["place_points"]:
            where = self.spec["place_points"][where]
        if where == "elsewhere" or where not in self.points:
            return "elsewhere"
        return where

    def minutes(self, a, b):
        """Walking minutes between two locations (point keys or "elsewhere")."""
        a, b = self.point_of(a), self.point_of(b)
        if a == b:
            return 0.0 if a != "elsewhere" else float(self.rule["elsewhere"])
        if "elsewhere" in (a, b):
            return float(self.rule["elsewhere"])
        k = (a, b) if a < b else (b, a)
        if k not in self._minutes:
            self._minutes[k] = self.walk.minutes(self.points[a], self.points[b]) if self.walk else 1.0
        return self._minutes[k]

    def shift(self, pid):
        """(start, end) minutes at work on the Friday, or None. Authored by the spec's hours."""
        place = self.job.get(pid)
        if not place:
            return None
        h = self.hours
        if place == "pl-bar":
            start = h["bar_lead"] if self.lead.get(place) == pid else h["bar_staff"]
            return start, 24 * 60
        if place in h.get("place_hours", {}):
            return tuple(h["place_hours"][place])
        return h["work"][0], h["work"][1]

    def where(self, pid, t):
        """(location, at work?) for pid at minute t of the Friday (cached: the hours do not change within a case)."""
        k = (pid, t)
        c = self.__dict__.setdefault("_where", {})
        if k not in c:
            c[k] = self._where_now(pid, t)
        return c[k]

    def hearers(self, a, r):
        c = self.__dict__.setdefault("_hearers", {})
        k = (a, tuple(sorted(r.items())))
        if k not in c:
            c[k] = self.ties.hearers(a, r)
        return c[k]

    def _where_now(self, pid, t):
        if t >= self.hours["regulars"] and pid in self.friday:
            return "pl-bar", False
        sh = self.shift(pid)
        if sh and sh[0] <= t < sh[1]:
            return self.job[pid], True
        return "home:" + self.home[pid], False

    def location_key(self, loc):
        """A location's walking key: a point key or "elsewhere"."""
        if loc.startswith("home:"):
            return self.point_of(loc[5:])
        return self.point_of(loc)


# -- the referee: the spread, the clock and the score (kept apart from the parsing above) -------------------------

def simulate(case, line, rule=None, start=None):
    """Run the Friday with the player's tellings (a list of pids, told back to back from `start`).

    Returns dict(heard={pid: (minute, channel, source)}, tellings=[(pid, start, end, location)], skipped=[...]).
    Channels: "player" (told by the player), "spread" (told by someone who had heard, outside the Anchor), "bar"
    (heard at the Anchor: said aloud there, or at 18:00 when the Anchor says it)."""
    r = dict(case.rule, **(rule or {}))
    h = case.hours
    t = h["day"][0] if start is None else start
    end = h["deadline"]
    heard = {}
    pq = []  # (time, order, kind, data)
    order = itertools.count()
    tellings, skipped = [], []
    loc = "home:" + case.player_home
    # the player's tellings: walk, then tell; each hearer has heard at the telling's end
    for pid in line:
        if pid not in case.ties.alive or pid == case.dead:
            skipped.append((pid, "not alive"))
            continue
        # where they will be when the player arrives: walk to where they are now, then follow if they moved
        target = case.where(pid, t)[0]
        walk = case.minutes(case.location_key(loc), case.location_key(target))
        arrive = t + walk
        target2 = case.where(pid, arrive)[0]
        if target2 != target:
            arrive += case.minutes(case.location_key(target), case.location_key(target2))
            target = target2
        done = arrive + r["tell"]
        if done > end:
            skipped.append((pid, "after {}".format(hhmm(end))))
            break
        tellings.append((pid, arrive, done, target))
        heapq.heappush(pq, (done, next(order), "player", (pid, target)))
        t, loc = done, target
    bar = {"since": None}  # when the Anchor first had it said aloud

    def hear(pid, when, channel, source):
        if pid in heard or pid == case.dead or pid not in case.ties.alive:
            return False
        heard[pid] = (when, channel, source)
        heapq.heappush(pq, (when + r["tau"], next(order), "tell", pid))
        return True

    def aloud(when):
        """Said aloud at the Anchor: everyone there hears it now, and whoever comes in later hears it as they come."""
        if bar["since"] is None:
            bar["since"] = when
            for p, t0 in case.bar_from.items():
                if t0 > when:
                    heapq.heappush(pq, (t0, next(order), "arrive", p))
        for p, t0 in case.bar_from.items():
            if t0 <= when:
                hear(p, when, "bar", "the Anchor")

    while pq:
        when, _, kind, data = heapq.heappop(pq)
        if when >= end:
            break
        if kind == "player":
            pid, target = data
            hear(pid, when, "player", "player")
            if target == "pl-bar":
                aloud(when)  # told at the Anchor: said aloud there
            continue
        if kind == "arrive":
            hear(data, when, "bar", "the Anchor")
            continue
        a = data  # a "tell": a has heard, and tells one close hearer within reach, or says it aloud at the Anchor
        here, working = case.where(a, when)
        if here == "pl-bar":
            aloud(when)
            continue  # all there have it; whoever comes later hears it as they come
        left = [b for b in case.hearers(a, r) if b not in heard and b != case.dead]
        if not left and a not in case.bar_from:
            continue  # everyone close to them has it, and they will not be at the Anchor: they stop
        for b in left:
            there, b_working = case.where(b, when)
            if there == "pl-bar":
                continue  # to tell someone at the Anchor is to say it there; a teller does not go in to
            if there == here or (not working and not b_working):
                hear(b, when, "spread", a)
                break
        heapq.heappush(pq, (when + r["tau"], next(order), "tell", a))
    # the deadline: the Anchor says it aloud to everyone there
    for p, t0 in case.bar_from.items():
        if t0 <= end and p not in heard:
            heard[p] = (end, "bar", "the Anchor at {}".format(hhmm(end)))
    bar_since = bar["since"]
    return dict(heard=heard, tellings=tellings, skipped=skipped, bar_since=bar_since)


def score(case, out):
    """The pick's score, out of the spec's points: each visitor's share if they heard it from the player, half if from
    someone else outside the Anchor, nothing from the Anchor or not at all; minus the leak cost per person who heard it
    before the Anchor said it (anyone but the visitors and the dead), however they heard; minus the exposure cost per
    private act said aloud (none: every telling in this script says the death only)."""
    s = case.spec["score"]
    share = s["points"] / len(case.visitors)
    end = case.hours["deadline"]
    total, parts = 0.0, {}
    for v in case.visitors:
        h = out["heard"].get(v)
        got = 0.0
        if h and h[0] <= end:
            if h[1] == "player":
                got = share
            elif h[1] == "spread":
                got = share * s["spread_share"]
        parts[v] = got
        total += got
    leaks = sorted(p for p, (when, ch, src) in out["heard"].items()
                   if p not in case.visitors and when < end)
    total -= s["leak"] * len(leaks)
    return dict(total=total, parts=parts, leaks=leaks, reached=len([p for p, h in out["heard"].items() if h[0] < end]))


# -- every line -----------------------------------------------------------------------------------------------------

def candidates(case):
    """The people a line may tell: the visitors, the page's lead, Peter (seed A), and each visitor's close hearers
    (the only people through whom a telling can reach a visitor outside the Anchor in one step)."""
    out = set(case.visitors)
    for k in ("page", "peter"):
        if case.s.get(k):
            out.add(case.s[k])
    for v in case.visitors:
        out |= set(case.ties.hearers(v, case.rule))
        out |= {a for a in case.ties.alive if v in case.ties.hearers(a, case.rule)}
    out.discard(case.dead)
    return sorted(out, key=lambda p: int(p[2:]))


def all_lines(cands, k):
    yield ()
    for n in range(1, k + 1):
        for line in itertools.permutations(cands, n):
            yield line


_JOB = {}


def _score_lines(lines):
    case, rule, start = _JOB["case"], _JOB["rule"], _JOB["start"]
    return [(line, score(case, simulate(case, line, rule, start))["total"]) for line in lines]


def run_lines(case, lines, rule=None, start=None, workers=6):
    """{line: score} for every line. Large sets are scored in forked workers (the same code, the same answers)."""
    lines = list(lines)
    _JOB.update(case=case, rule=rule, start=start)
    if len(lines) < 20000 or workers <= 1:
        return dict(_score_lines(lines))
    import multiprocessing
    chunks = [lines[i::workers * 8] for i in range(workers * 8)]
    with multiprocessing.get_context("fork").Pool(workers) as pool:
        return dict(x for part in pool.map(_score_lines, chunks) for x in part)


def named(case):
    v = case.visitors
    out = {"the page's line ({} first)".format(case.world.name(case.s["page"])): (case.s["page"],)}
    if case.s.get("peter"):
        out["Peter first"] = (case.s["peter"],)
    if len(v) >= 2:
        out["{} then {}, back to back".format(*(case.world.name(p).split()[0] for p in v[:2]))] = tuple(v[:2])
        out["{} then {}, back to back".format(*(case.world.name(p).split()[0] for p in v[1::-1]))] = tuple(v[1::-1])
    if len(v) == 3:
        for perm in itertools.permutations(v):
            out["{}, back to back".format(", ".join(case.world.name(p).split()[0] for p in perm))] = perm
    return out


def best_by_first(case, res):
    """{first telling: (best score, best line)} over lines that start with it; () for telling nobody."""
    out = {}
    for line, sc in res.items():
        k = line[0] if line else None
        if k not in out or sc > out[k][0] or (sc == out[k][0] and len(line) < len(out[k][1])):
            out[k] = (sc, line)
    return out


def plans(case, res):
    """The 27 vantage plans: for each choice of vantage on each evening, which visitors the player has seen go to the
    dead's door (the spec's sightings), and the best line that tells only visitors seen (others may still hear it)."""
    ev = case.s["evenings"]
    vs = list(case.spec["vantages"])
    out = []
    for plan in itertools.product(vs, repeat=len(ev)):
        seen = set()
        for evening, v in zip(ev, plan):
            seen |= set(evening["sightings"].get(v, []))
        best = max(((sc, line) for line, sc in res.items()
                    if not (set(line) & (set(case.visitors) - seen))), key=lambda x: (x[0], -len(x[1])))
        out.append((plan, sorted(seen), best))
    return out


def name_line(world, line):
    return " → ".join(world.name(p) for p in line) if line else "(tell nobody)"


def evaluate(case, k, cands=None, rule=None, start=None):
    cands = cands or candidates(case)
    res = run_lines(case, all_lines(cands, k), rule, start)
    best_line = max(res, key=lambda l: (res[l], -len(l)))
    return res, best_line


def verdicts(case, res, best_line):
    """The pass lines of outline.md §3, test 1, for this seed: a dict of name → (value, ok)."""
    w = case.world
    bf = best_by_first(case, res)
    v = case.visitors
    firsts = {p: bf[p][0] for p in v if p in bf}
    best = res[best_line]
    nm = named(case)
    page_line = nm[next(k for k in nm if k.startswith("the page"))]
    page = (res[page_line], simulate(case, page_line))
    peter = (res[nm["Peter first"]],) if "Peter first" in nm else None
    out = {}
    if len(firsts) >= 2:
        vals = sorted(firsts.values())
        out["branches at the first telling differ by ≥16"] = (vals[-1] - vals[0], vals[-1] - vals[0] >= 16)
        out["(kill line) branches within 8"] = (vals[-1] - vals[0], vals[-1] - vals[0] <= 8)
    out["best beats the page's line by ≥16"] = (best - page[0], best - page[0] >= 16)
    if peter:
        out["best beats Peter first by ≥16"] = (best - peter[0], best - peter[0] >= 16)
    b2b = [res[nm[k]] for k in nm if "back to back" in k]
    out["the two back to back is not the best line"] = (max(b2b), max(b2b) < best)
    reached = len([p for p, hh in page[1]["heard"].items() if hh[0] < case.hours["deadline"]])
    out["the page's line reaches ≥6 by 18:00"] = (reached, reached >= 6)
    return out


def ranking(case, res):
    """The named lines, best first, with their scores (ties keep the names' order)."""
    nm = named(case)
    return sorted(((res[l], k) for k, l in nm.items()), key=lambda x: -x[0])


# -- the report -----------------------------------------------------------------------------------------------------

def tie_rows(case, pids):
    w, T = case.world, case.ties
    rows = []
    for a in pids:
        for b, t in sorted(T.ties.get(a, {}).items(), key=lambda x: -T.closeness(a, x[0], case.rule)):
            kinds = [k for k in ("kin", "partner", "cowork") if t[k]] + (["like {:+d}".format(t["like"])] if t["like"] else [])
            rows.append((w.name(a), w.name(b), ", ".join(kinds), T.closeness(a, b, case.rule), "; ".join(sorted(set(t["sources"])))))
    return rows


def run_seed(spec, seed, world, layout, walk, k, quick=False, log=print):
    ym = tuple(spec["seeds"][seed]["month"])
    ties = TieTable(world, ym)
    case = Case(spec, seed, world, ties, layout, walk)
    w = world
    out = dict(seed=seed)
    log("\n=== Seed {}: {} ({}), the Friday {} ===".format(seed, w.name(case.dead), spec["seeds"][seed]["death"],
                                                          spec["seeds"][seed]["day"]))
    # 1. tie counts first
    log("\nTie counts at {}-{:02d} (kin and partners simulated or derived as labelled; coworkers and liking derived):".format(*ym))
    focus = list(case.visitors) + [p for p in (case.s.get("page"), case.s.get("peter")) if p]
    counts = {}
    for p in focus:
        c = ties.counts(p)
        counts[w.name(p)] = c
        log("  {:<16} kin {kin}  partner {partner}  coworkers {cowork}  liked {liked}  disliked {disliked}  "
            "(people tied: {any})".format(w.name(p), **c))
    total_pairs = sum(len(v) for v in ties.ties.values()) // 2
    log("  the town: {} living people, {} tied pairs".format(len(ties.alive), total_pairs))
    out["counts"] = counts
    log("\nThe visitors' ties (closeness by the spec's weights):")
    for row in tie_rows(case, case.visitors):
        log("  {} — {}: {} = {:g}  [{}]".format(*row))
    # hours and walks
    log("\nWhere the case's people are on the Friday (authored hours):")
    cands = candidates(case)
    for p in cands:
        sh = case.shift(p)
        log("  {:<16} home {:<22} {}{}".format(w.name(p), case.home[p],
                                              "work {} {}–{}".format(case.job[p], hhmm(sh[0]), hhmm(min(sh[1], 1440))) if sh else "free",
                                              ", the Anchor from {}".format(hhmm(case.hours["deadline"])) if p in case.friday else ""))
    keys = sorted(case.points)
    log("\nWalking minutes from the player's home ({}):".format(case.player_home) + "".join(
        "  {} {:.1f}".format(k2, case.minutes(case.player_home, k2)) for k2 in keys if k2 != case.player_home))
    # 2. every line
    res, best_line = evaluate(case, k, cands)
    out["lines"] = len(res)
    log("\n{} lines tried (every order of up to {} tellings from {} candidates, from {}).".format(
        len(res), k, len(cands), hhmm(case.hours["day"][0])))
    bsc = res[best_line]
    log("Best line: {} = {:g}".format(name_line(w, best_line), bsc))
    log("  " + describe(case, simulate(case, best_line)))
    out["best"] = (name_line(w, best_line), bsc)
    log("\nBest by first telling:")
    bf = best_by_first(case, res)
    for p, (sc, line) in sorted(bf.items(), key=lambda x: -x[1][0])[:12]:
        log("  {:<16} {:>6.1f}  {}".format(w.name(p) if p else "(nobody)", sc, name_line(w, line)))
    out["firsts"] = {w.name(p) if p else "(nobody)": sc for p, (sc, _) in bf.items()}
    log("\nThe named lines:")
    rk = ranking(case, res)
    for sc, nmk in rk:
        line = named(case)[nmk]
        log("  {:<40} {:>6.1f}  {}".format(nmk, sc, describe(case, simulate(case, line))))
    out["named"] = rk
    v = verdicts(case, res, best_line)
    log("\nPass lines:")
    for kk, (val, ok) in v.items():
        log("  {:<48} {:>7.1f}  {}".format(kk, val, "yes" if ok else "no"))
    out["verdicts"] = {kk: (val, ok) for kk, (val, ok) in v.items()}
    # waiting: the same lines started later
    log("\nThe same lines started later (the spec's check on waiting; not a pass line):")
    waits = {}
    for st in range(case.hours["day"][0], case.hours["deadline"], 60):
        r2, b2 = evaluate(case, min(k, 2), cands, start=st)
        bf2 = best_by_first(case, r2)
        fv = {w.name(v).split()[0]: bf2[v][0] for v in case.visitors if v in bf2}
        waits[hhmm(st)] = (r2[b2], name_line(w, b2), fv)
        log("  from {}: best of up to 2 tellings {:>6.1f}  {:<34} first-telling branches {}".format(
            hhmm(st), r2[b2], name_line(w, b2), "  ".join("{} {:g}".format(k2, v2) for k2, v2 in fv.items())))
    out["waits"] = waits
    # 3. the vantage plans
    pl = plans(case, res)
    vals = sorted(x[2][0] for x in pl)
    log("\nThe {} vantage plans: best informed score min {:g}, median {:g}, max {:g}".format(
        len(pl), vals[0], vals[len(vals) // 2], vals[-1]))
    by_seen = defaultdict(list)
    for plan, seen, (sc, line) in pl:
        by_seen[tuple(seen)].append((plan, sc, line))
    for seen, xs in sorted(by_seen.items(), key=lambda x: -len(x[0])):
        log("  seen {:<28} {:>2} plans, best {:>6.1f}: {}".format(
            ", ".join(w.name(p) for p in seen) or "nobody", len(xs), xs[0][1], name_line(w, xs[0][2])))
    out["plans"] = {", ".join(w.name(p) for p in s) or "nobody": (len(xs), xs[0][1]) for s, xs in by_seen.items()}
    if quick:
        return out
    # 4. the sweeps
    log("\nThe sweep: each spread parameter at ½ and 1½ times, each authored hour an hour either side.")
    base_rank = [nmk for _, nmk in rk]
    base_best = best_line
    flips = []
    sweeps = []
    for name in spec["sweep"]["rule"]:
        for f in (0.5, 1.5):
            val = case.rule[name] * f
            sweeps.append(("{} ×{:g} ({:g})".format(name, f, val), dict(rule={name: val})))
    for name in spec["sweep"]["hours"]:
        for d in (-60, 60):
            hv = case.hours[name]
            if isinstance(hv, list):
                nv = [x + d for x in hv]
            elif isinstance(hv, dict):
                nv = {kk: [x + d for x in vv] for kk, vv in hv.items()}
            else:
                nv = hv + d
            sweeps.append(("{} {:+d} h".format(name, d // 60), dict(hours={name: nv})))
    out["sweeps"] = []
    for label, kw in sweeps:
        c2 = Case(spec, seed, world, ties, layout, walk, hours=kw.get("hours"), rule=kw.get("rule"))
        c2._minutes = case._minutes if "elsewhere" not in (kw.get("rule") or {}) else {}
        r2, b2 = evaluate(c2, k, cands)
        rk2 = ranking(c2, r2)
        v2 = verdicts(c2, r2, b2)
        order2 = [nmk for _, nmk in rk2]
        inv = inversions(rk, rk2)
        strict_flip = bool(inv)
        fails = [kk for kk, (val, ok) in v2.items() if not kk.startswith("(") and not ok]
        log("  {:<28} best {:>6.1f} {:<44} ranking {}  {}".format(
            label, r2[b2], name_line(w, b2)[:44], "flips" if strict_flip else "holds",
            ("fails: " + "; ".join(fails)) if fails else "all pass lines hold"))
        for x, y in inv:
            log("      flips: {} / {}".format(x, y))
        out["sweeps"].append(dict(label=label, best=r2[b2], line=name_line(w, b2), flips=inv, fails=fails,
                                  ranking=rk2))
        if strict_flip:
            flips.append(label)
    out["flips"] = flips
    return out


def inversions(rk, rk2):
    """Pairs of named lines strictly ordered one way in rk and strictly the other way in rk2 (a tie that opens or
    closes is not a flip)."""
    a, b = {k: sc for sc, k in rk}, {k: sc for sc, k in rk2}
    out = []
    for x, y in itertools.combinations(sorted(a), 2):
        if (a[x] - a[y]) * (b[x] - b[y]) < 0:
            out.append((x, y))
    return out


def describe(case, out):
    w = case.world
    parts = []
    for v in case.visitors:
        h = out["heard"].get(v)
        parts.append("{} {}".format(w.name(v).split()[0], "{} {}{}".format(hhmm(h[0]), h[1], " from " + w.name(h[2]).split()[0]
                                                                           if h[1] == "spread" else "") if h else "never"))
    early = [p for p, h in out["heard"].items() if h[0] < case.hours["deadline"]]
    return "; ".join(parts) + "; {} heard before {}".format(len(early), hhmm(case.hours["deadline"]))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--seed", default="both", choices=["A", "B", "both"])
    ap.add_argument("--json", help="write the results here")
    ap.add_argument("--quick", action="store_true", help="no sweeps")
    ap.add_argument("--unfrozen", action="store_true", help="run on a spec whose hash is not FROZEN (never for a result)")
    a = ap.parse_args(argv)
    spec, sha = spec_block()
    print("Test 1, the tie script. case-spec.md's frozen block: sha256 {}".format(sha))
    if sha != FROZEN and not a.unfrozen:
        print("The spec is not the frozen case (FROZEN {}): a change after a result is a new case.".format(FROZEN))
        return 2
    world = facts.World(json.loads(facts.EXPORT.read_text(encoding="utf-8")))
    layout = json.loads(LAYOUT.read_text(encoding="utf-8"))
    walk = Walk(layout, spec["rule"]["speed"], spec["rule"]["flight"])
    results = {}
    for seed in (["A", "B"] if a.seed == "both" else [a.seed]):  # seed B last
        results[seed] = run_seed(spec, seed, world, layout, walk, spec["rule"]["max_tellings"], a.quick)
    if a.json:
        Path(a.json).write_text(json.dumps(results, indent=1, ensure_ascii=False, default=str), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
