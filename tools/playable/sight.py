#!/usr/bin/env python3
"""Test 2a of the playable corner's ladder: is the clue in line of sight? A number, Unity-free.

    python3 tools/playable/sight.py [--json OUT]

(`reviews/lt1/playable/outline.md` §3, test 2; `premortem.md` §4, should 1.) Over the heart's layout as
`layout_dump.py` dumped it (`reviews/lt1/playable/ladder/2a-layout.json`: the carved ground on its 1.5 m grid, every
building's footprint with its base, eave, pitch and roof, the retaining walls, the yard walls, sheds and stoops), plus:
- **A's real windows**, from its 1989 plan (`blender/resolver/resolve.py` on `diaries.json`'s record), placed as
  `export_time.placement` places the house: each window's opening, the glass 0.14 m behind the wall's face
  (`parts.py`), an eye 0.35 m behind the glass at 1.6 m above its floor, free to lean 0.3 m either side;
- **the birch** at (44.5, 28.0) (`LT1Perf.BirchAt`; ground 5.20 m, 16.7 m tall from the walk's build), its trunk always
  and its crown either bare (November: the crown's twigs are left out, so this is the best case) or opaque (the worst);
- the routes, as the walk's lanes give them (`ties.Walk`): Hannah's climb from her door to E's, Olive's from the Anchor
  along the Row and up, and seed B's three visitors to Andy's door; doors from the case spec's homes.

For each vantage (the windows at A, the Row, the Anchor's door) and route it gives the share of the route in sight
(the head; and the whole figure), whether each door is in sight, a figure's height in pixels (2560x1440 at the eye
views' fields of view: Lens35 37.8 degrees vertical, Lens28 46.4), and whether the visible part fits one frame. Then
the sun's height at each authored hour, at Stavanger (58.97 N, 5.73 E; CET, CEST in summer).

Limits: the five houses are the heart's masses here (the walk swaps in the generated houses, a little smaller), roofs
are simple prisms, lamps, rails and people are left out, and A itself never blocks its own windows' view beyond the
opening.
"""

import argparse
import datetime
import json
import math
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ties  # noqa: E402  (Walk, the spec)

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "blender" / "resolver"))
from resolve import resolve  # noqa: E402

LAYOUT = ROOT / "reviews" / "lt1" / "playable" / "ladder" / "2a-layout.json"
DIARIES = ROOT / "reviews" / "lt1" / "time" / "readers" / "diaries.json"
CORNER_FIXTURE = ROOT / "fixtures" / "lt1-corner.json"

FRAME = (2560, 1440)
LENSES = {"Lens35": 37.8, "Lens28": 46.4}  # vertical fields of view, degrees
FIGURE = 1.75                                # a figure's height, m
HEADS = (0.25, 0.9, 1.6)                     # points on a figure: legs, body, head
BIRCH = dict(x=44.5, y=28.0, z=5.20, h=16.7, trunk_r=0.2, crown_base=0.35, crown_r=3.5)
GLASS_BACK, EYE_BACK, EYE_UP, LEAN, FRAME_W = 0.14, 0.35, 1.6, 0.3, 0.05
STEP = 0.15
CELL = 4.0
LAT, LON = 58.97, 5.73


# -- solids: everything that can block a line ------------------------------------------------------------------------

class Box:
    """An oriented box (centre, half sizes along its own axes, a turn in degrees), from z0 to z1, with an optional roof
    profile over its top (a function of the box's local u in [0, w] and v in [0, d])."""

    def __init__(self, name, ox, oy, angle, w, d, z0, z1, roof=None):
        self.name = name
        self.ox, self.oy, self.w, self.d, self.z0, self.z1 = ox, oy, w, d, z0, z1
        self.c, self.s = math.cos(math.radians(angle)), math.sin(math.radians(angle))
        self.roof = roof
        top = z1 + (roof(w / 2, d / 2, peak=True) if roof else 0.0)
        xs = [ox + u * self.c - v * self.s for u in (0, w) for v in (0, d)]
        ys = [oy + u * self.s + v * self.c for u in (0, w) for v in (0, d)]
        self.bb = (min(xs), max(xs), min(ys), max(ys), z0, top)

    def inside(self, x, y, z):
        if z < self.z0 or z > self.bb[5]:
            return False
        dx, dy = x - self.ox, y - self.oy
        u, v = dx * self.c + dy * self.s, -dx * self.s + dy * self.c
        if not (0 <= u <= self.w and 0 <= v <= self.d):
            return False
        if z <= self.z1:
            return True
        return bool(self.roof) and z <= self.z1 + self.roof(u, v)


def roof_fn(kind, w, d, pitch):
    t = math.tan(math.radians(pitch))
    if kind in ("eaves", "mansard"):
        return lambda u, v, peak=False: t * (d / 2 if peak else min(v, d - v))
    if kind == "gable":
        return lambda u, v, peak=False: t * (w / 2 if peak else min(u, w - u))
    if kind == "flat":
        return None
    m = min(w, d) / 2
    return lambda u, v, peak=False: t * (m if peak else min(u, w - u, v, d - v))


def centred_box(name, x, y, a, l, w, z0, z1):
    """A box given by its centre, its length along a and its width across."""
    c, s = math.cos(math.radians(a)), math.sin(math.radians(a))
    ox, oy = x - (l / 2) * c + (w / 2) * s, y - (l / 2) * s - (w / 2) * c
    return Box(name, ox, oy, a, l, w, z0, z1)


class Cylinder:
    def __init__(self, name, x, y, r, z0, z1):
        self.name, self.x, self.y, self.r, self.z0, self.z1 = name, x, y, r, z0, z1
        self.bb = (x - r, x + r, y - r, y + r, z0, z1)

    def inside(self, x, y, z):
        return self.z0 <= z <= self.z1 and (x - self.x) ** 2 + (y - self.y) ** 2 <= self.r ** 2


class Ellipsoid:
    def __init__(self, name, x, y, z, r, rz):
        self.name, self.x, self.y, self.z, self.r, self.rz = name, x, y, z, r, rz
        self.bb = (x - r, x + r, y - r, y + r, z - rz, z + rz)

    def inside(self, x, y, z):
        return ((x - self.x) ** 2 + (y - self.y) ** 2) / self.r ** 2 + ((z - self.z) / self.rz) ** 2 <= 1.0


class Scene:
    def __init__(self, layout, crown=False, skip=()):
        g = layout["ground"]
        self.gx0, self.gy0, self.gs, self.nx, self.ny, self.gz = g["x0"], g["y0"], g["step"], g["nx"], g["ny"], g["z"]
        self.solids = []
        for b in layout["buildings"]:
            if b["name"] in skip:
                continue
            self.solids.append(Box(b["name"], b["ox"], b["oy"], b["angle"], b["w"], b["d"], b["base"] - 8.0,
                                   b["base"] + b["eave"], roof_fn(b["roof"], b["w"], b["d"], b["pitch"])))
        for i, wl in enumerate(layout["walls"]):
            self.solids.append(centred_box("retaining wall {}".format(i), wl["x"], wl["y"], wl["a"], wl["l"], wl["w"],
                                           wl["z0"] - 1.0, wl["z1"]))
        for i, d in enumerate(layout["details"]):
            if d["kind"] in ("wall", "shed", "stoop", "well", "lantern", "quay steps"):
                self.solids.append(centred_box("{} {}".format(d["kind"], i), d["x"], d["y"], d["a"], d["l"], d["w"],
                                               d["z"] - 0.5, d["z"] + d["h"]))
        bz = BIRCH["z"]
        self.solids.append(Cylinder("the birch's trunk", BIRCH["x"], BIRCH["y"], BIRCH["trunk_r"], bz - 1, bz + BIRCH["h"] * 0.8))
        if crown:
            cb = bz + BIRCH["h"] * BIRCH["crown_base"]
            top = bz + BIRCH["h"]
            self.solids.append(Ellipsoid("the birch's crown", BIRCH["x"], BIRCH["y"], (cb + top) / 2, BIRCH["crown_r"],
                                         (top - cb) / 2))
        self.grid = defaultdict(list)
        for o in self.solids:
            x0, x1, y0, y1 = o.bb[:4]
            for i in range(int(math.floor(x0 / CELL)), int(math.floor(x1 / CELL)) + 1):
                for j in range(int(math.floor(y0 / CELL)), int(math.floor(y1 / CELL)) + 1):
                    self.grid[(i, j)].append(o)

    def ground(self, x, y):
        u = min(max((x - self.gx0) / self.gs, 0.0), self.nx - 1.001)
        v = min(max((y - self.gy0) / self.gs, 0.0), self.ny - 1.001)
        i, j = int(u), int(v)
        fu, fv = u - i, v - j
        z = self.gz
        a = z[i][j] + (z[i + 1][j] - z[i][j]) * fu
        b = z[i][j + 1] + (z[i + 1][j + 1] - z[i][j + 1]) * fu
        return a + (b - a) * fv

    def blocker(self, p, q, skip_start=0.3, skip_end=0.35):
        """The first thing between p and q (3-tuples), or None. The ends are skipped (the eye's sill, the figure's own
        ground); the ground blocks where the line runs more than 0.1 m under it."""
        dx, dy, dz = q[0] - p[0], q[1] - p[1], q[2] - p[2]
        L = math.sqrt(dx * dx + dy * dy + dz * dz)
        n = max(1, int(L / STEP))
        for k in range(n + 1):
            t = k / n
            dist = t * L
            if dist < skip_start or L - dist < skip_end:
                continue
            x, y, z = p[0] + dx * t, p[1] + dy * t, p[2] + dz * t
            if z < self.ground(x, y) - 0.1:
                return "the ground"
            for o in self.grid.get((int(math.floor(x / CELL)), int(math.floor(y / CELL))), ()):
                if o.inside(x, y, z):
                    return o.name
        return None


# -- A's windows ---------------------------------------------------------------------------------------------------

def a_windows(layout):
    """Each of A's windows in 1989: dict(name, centre, normal, u-axis, half width, z0, z1, eyes)."""
    src = json.loads(DIARIES.read_text(encoding="utf-8"))
    ws = json.loads(CORNER_FIXTURE.read_text(encoding="utf-8"))["worldSeed"]
    plan = resolve(src["real"]["A"], 1989, ws)
    m = plan["main"]
    W, D, P = m["W"] / 1000.0, m["D"] / 1000.0, m["plinth"] / 1000.0
    heart = next(b for b in layout["buildings"] if b["name"].startswith("A "))
    a = math.radians(heart["angle"])
    c, s = math.cos(a), math.sin(a)
    ax, ay = heart["ox"] + heart["w"] / 2 * c, heart["oy"] + heart["w"] / 2 * s
    ox, oy = ax - (0 * c - (-D / 2) * s), ay - (0 * s + (-D / 2) * c)  # export_time.placement
    floor = heart["base"]
    to = lambda lx, ly: (ox + lx * c - ly * s, oy + lx * s + ly * c)
    rot = lambda vx, vy: (vx * c - vy * s, vx * s + vy * c)
    frames = {"front": ((0, -D / 2), (0, -1), (1, 0)), "right": ((W / 2, 0), (1, 0), (0, 1)),
              "back": ((0, D / 2), (0, 1), (-1, 0)), "left": ((-W / 2, 0), (-1, 0), (0, -1))}
    out = []
    storey = m["storey_h"] / 1000.0
    for cell in plan["cells"]:
        part = cell.get("part", {})
        if part.get("type") not in ("window", "shopfront") or cell["facade"] not in frames or "covered" in cell:
            continue
        (fx, fy), nrm, uax = frames[cell["facade"]]
        al = cell["a"] / 1000.0
        cx, cy = to(fx + uax[0] * al, fy + uax[1] * al)
        n, u = rot(*nrm), rot(*uax)
        b0, b1 = cell["b0"] / 1000.0, cell["b1"] / 1000.0
        level = 0 if b0 < storey else 1
        eye_z = floor + level * storey + EYE_UP
        name = "{} {} {}, {}".format(cell["facade"], "ground floor" if level == 0 else "first floor",
                                     part["type"], "x {:.1f} y {:.1f}".format(cx, cy))
        eyes = []
        for lean in (-LEAN, 0.0, LEAN):
            back = GLASS_BACK + EYE_BACK
            eyes.append((cx - n[0] * back + u[0] * lean, cy - n[1] * back + u[1] * lean, eye_z))
        out.append(dict(name=name, facade=cell["facade"], level=level, c=(cx, cy), n=n, u=u, hw=cell["w"] / 2000.0 - FRAME_W,
                        z0=floor + b0 + FRAME_W, z1=floor + b1 - FRAME_W, eyes=eyes, kind=part["type"]))
    return out, dict(W=W, D=D, plinth=P, centre=(ox, oy), floor=floor)


def through_opening(win, eye, q):
    """Does the line from eye to q pass the window's glass and its outer face within the opening?"""
    n, u = win["n"], win["u"]
    cx, cy = win["c"]
    d = (q[0] - eye[0], q[1] - eye[1], q[2] - eye[2])
    dn = d[0] * n[0] + d[1] * n[1]
    if dn <= 0:
        return False
    for depth in (-GLASS_BACK, 0.0):  # the glass, then the wall's face
        # plane: points p with (p - c) . n = depth
        t = (depth - ((eye[0] - cx) * n[0] + (eye[1] - cy) * n[1])) / dn
        x, y, z = eye[0] + d[0] * t, eye[1] + d[1] * t, eye[2] + d[2] * t
        lat = (x - cx) * u[0] + (y - cy) * u[1]
        if abs(lat) > win["hw"] or not (win["z0"] <= z <= win["z1"]):
            return False
    return True


# -- routes ----------------------------------------------------------------------------------------------------------

def route(walk, a, b, every=1.0):
    """The walking path from a to b (x, y points) as (x, y, z) samples every `every` metres along it."""
    da, ua = walk.join(*a)
    db, ub = walk.join(*b)
    import heapq
    dist, prev = {ua: 0.0}, {}
    pq = [(0.0, ua)]
    while pq:
        t, x = heapq.heappop(pq)
        if x == ub:
            break
        if t > dist.get(x, 1e18):
            continue
        for v, wgt in walk.adj[x]:
            if t + wgt < dist.get(v, 1e18):
                dist[v], prev[v] = t + wgt, x
                heapq.heappush(pq, (t + wgt, v))
    nodes = [ub]
    while nodes[-1] != ua:
        nodes.append(prev[nodes[-1]])
    nodes.reverse()
    pts = [walk.nodes[k] for k in nodes]
    out = []
    for (x1, y1, z1), (x2, y2, z2) in zip(pts, pts[1:]):
        L = math.hypot(x2 - x1, y2 - y1)
        n = max(1, int(L / every))
        for i in range(n):
            t = i / n
            out.append((x1 + (x2 - x1) * t, y1 + (y2 - y1) * t, z1 + (z2 - z1) * t))
    out.append(pts[-1])
    return out


def px_height(d, lens):
    return FRAME[1] * (FIGURE / max(d, 0.1)) / (2 * math.tan(math.radians(LENSES[lens] / 2)))


def hfov(lens):
    return math.degrees(2 * math.atan(math.tan(math.radians(LENSES[lens] / 2)) * FRAME[0] / FRAME[1]))


# -- seeing ----------------------------------------------------------------------------------------------------------

def sees(scene, vantage, p):
    """(seen, blocker or reason, eye) for the point p from a vantage: a window (any of its eyes, through its opening)
    or a free eye."""
    eyes = vantage["eyes"]
    why = None
    for eye in eyes:
        if vantage.get("window") and not through_opening(vantage["window"], eye, p):
            why = why or "the window's opening"
            continue
        start = 0.6 if vantage.get("window") else 0.3
        b = scene.blocker(eye, p, skip_start=start)
        if b is None:
            return True, None, eye
        why = b if why in (None, "the window's opening") else why
    return False, why, None


def figure_at(scene, x, y, z):
    zg = max(z, scene.ground(x, y))
    return [(x, y, zg + h) for h in HEADS]


def judge_route(scene, vantage, pts):
    rows = []
    for (x, y, z) in pts:
        fig = figure_at(scene, x, y, z)
        res = [sees(scene, vantage, q) for q in fig]
        head = res[-1]
        eye = head[2] or (res[1][2]) or vantage["eyes"][len(vantage["eyes"]) // 2]
        d = math.dist(eye, fig[1])
        bearing = math.degrees(math.atan2(fig[1][1] - eye[1], fig[1][0] - eye[0]))
        rows.append(dict(p=(x, y, fig[0][2] - HEADS[0]), head=head[0], whole=all(r[0] for r in res),
                         any=any(r[0] for r in res), why=head[1] if not head[0] else None, d=d, bearing=bearing))
    return rows


def summarise(rows):
    n = len(rows)
    vis = [r for r in rows if r["head"]]
    out = dict(samples=n, head=len(vis) / n, whole=sum(r["whole"] for r in rows) / n, any=sum(r["any"] for r in rows) / n)
    blockers = defaultdict(int)
    for r in rows:
        if not r["head"]:
            blockers[r["why"]] += 1
    out["blocked_by"] = sorted(blockers.items(), key=lambda x: -x[1])[:4]
    if vis:
        ds = sorted(r["d"] for r in vis)
        out["d"] = (ds[0], ds[len(ds) // 2], ds[-1])
        out["px35"] = tuple(round(px_height(d, "Lens35")) for d in (ds[-1], ds[len(ds) // 2], ds[0]))
        out["px28"] = tuple(round(px_height(d, "Lens28")) for d in (ds[-1], ds[len(ds) // 2], ds[0]))
        bs = [r["bearing"] for r in vis]
        ref = bs[0]
        rel = [((b - ref + 180) % 360) - 180 for b in bs]
        out["spread_deg"] = max(rel) - min(rel)
        out["fits35"] = out["spread_deg"] <= hfov("Lens35")
        # the longest unbroken run in sight, in samples (metres)
        best = cur = 0
        for r in rows:
            cur = cur + 1 if r["head"] else 0
            best = max(best, cur)
        out["run"] = best
    return out


# -- the sun ---------------------------------------------------------------------------------------------------------

def sun_elevation(when_local, utc_offset_h, lat=LAT, lon=LON):
    """The sun's elevation in degrees (NOAA's approximation, ±0.5 degrees)."""
    t = when_local - datetime.timedelta(hours=utc_offset_h)
    doy = t.timetuple().tm_yday
    hour = t.hour + t.minute / 60.0
    g = 2 * math.pi / 365 * (doy - 1 + (hour - 12) / 24)
    eqt = 229.18 * (0.000075 + 0.001868 * math.cos(g) - 0.032077 * math.sin(g) - 0.014615 * math.cos(2 * g)
                    - 0.040849 * math.sin(2 * g))
    decl = (0.006918 - 0.399912 * math.cos(g) + 0.070257 * math.sin(g) - 0.006758 * math.cos(2 * g)
            + 0.000907 * math.sin(2 * g) - 0.002697 * math.cos(3 * g) + 0.00148 * math.sin(3 * g))
    tst = hour * 60 + eqt + 4 * lon
    ha = math.radians(tst / 4 - 180)
    la = math.radians(lat)
    cosz = math.sin(la) * math.sin(decl) + math.cos(la) * math.cos(decl) * math.cos(ha)
    return 90 - math.degrees(math.acos(max(-1.0, min(1.0, cosz))))


def utc_offset(day):
    """Norway: CET, and CEST from the last Sunday of March to the last Sunday of September (1989, 1998 rules: the EU's
    switch to October came in 1996)."""
    y = day.year

    def last_sunday(month):
        d = datetime.date(y, month, 31 if month in (3, 10) else 30)
        return d - datetime.timedelta(days=(d.weekday() + 1) % 7)
    end = last_sunday(10) if y >= 1996 else last_sunday(9)
    return 2 if last_sunday(3) <= day < end else 1


def sunset(day):
    off = utc_offset(day)
    t = datetime.datetime(day.year, day.month, day.day, 12, 0)
    while sun_elevation(t, off) > -0.833:
        t += datetime.timedelta(minutes=1)
    return t.strftime("%H:%M"), off


# -- the run ---------------------------------------------------------------------------------------------------------

def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--json", help="write the results here")
    a = ap.parse_args(argv)
    spec, sha = ties.spec_block()
    layout = json.loads(LAYOUT.read_text(encoding="utf-8"))
    walk = ties.Walk(layout, spec["rule"]["speed"], spec["rule"]["flight"])
    doors = {b["name"]: tuple(b["door"]) for b in layout["buildings"]}
    for b in layout["buildings"]:
        if b["name"][:2] in ("A ", "B ", "C ", "D ", "E "):
            doors[b["name"][0]] = tuple(b["door"])
    pt = {k: (tuple(v) if isinstance(v, list) else doors[v]) for k, v in spec["points"].items()}
    print("Test 2a, sight. Layout {} (heart_layout {}); case-spec block {}".format(
        LAYOUT.name, layout["source"]["heart_layout"][:8], sha[:8]))

    wins, a_info = a_windows(layout)
    a_name = next(b["name"] for b in layout["buildings"] if b["name"].startswith("A "))
    print("A's 1989 plan: {:.1f} x {:.1f} m, floor {:.2f}, centre ({:.2f}, {:.2f}); {} windows and its shopfront".format(
        a_info["W"], a_info["D"], a_info["floor"], *a_info["centre"], len([w for w in wins if w["kind"] == "window"])))

    routes = {
        "Hannah's climb (her door to E's)": route(walk, pt["ltu18"], pt["E"]),
        "Olive's (the Anchor along the Row and up to E)": route(walk, pt["row22"], pt["E"]),
        # W3 cast the Anchor onto Harbour Row 24 (fixtures/lt1-places-1989.json, authored) after the case froze Row 22
        "Olive's, from Row 24 (the Anchor as W3 cast it)": route(walk, doors["Harbour Row 24"], pt["E"]),
        "seed B: Ben (Row 23 to Andy's door)": route(walk, pt["row23"], pt["ltd9"]),
        "seed B: Oliver (B to Andy's door)": route(walk, pt["B"], pt["ltd9"]),
        "seed B: Trevor (the Low Terrace from the west)": route(walk, (20.0, 20.45), pt["ltd9"]),
    }
    door_pts = {"Hannah's door (Low Terrace up 18)": pt["ltu18"], "E's door": pt["E"],
                "Andy's door (Low Terrace down 9)": pt["ltd9"], "Karen's door (High Terrace up 21)": pt["htu21"]}

    def eye_free(x, y, scene):
        return [(x, y, scene.ground(x, y) + 1.65)]

    results = {}
    for crown in (False, True):
        mode = "crown opaque" if crown else "crown bare"
        sc_a = Scene(layout, crown=crown, skip=(a_name,))
        sc = Scene(layout, crown=crown)
        vantages = []
        for w in wins:
            vantages.append((dict(name="A: " + w["name"], eyes=w["eyes"], window=w), sc_a))
        row = (49.3, -12.0)
        vantages.append((dict(name="the Row (49.3, -12.0)", eyes=eye_free(*row, sc)), sc))
        anchor = (pt["row22"][0], pt["row22"][1] - 0.8)
        vantages.append((dict(name="the Anchor's door (Harbour Row 22)", eyes=eye_free(*anchor, sc)), sc))
        a24 = (doors["Harbour Row 24"][0], doors["Harbour Row 24"][1] - 0.8)
        vantages.append((dict(name="the Anchor's door as W3 cast it (Harbour Row 24)", eyes=eye_free(*a24, sc)), sc))
        # other places the outline names if the window fails ("the vantage moves, for example the window becomes the
        # steps' foot"): the foot, where the Low Terrace crosses the steps, the Landing
        for nm, (x, y) in (("the steps' foot (49.3, 2.5)", (49.3, 2.5)), ("the Low Terrace at the steps (51.5, 23.8)", (51.5, 23.8)),
                           ("the Landing (45.0, 42.0)", (45.0, 42.0))):
            vantages.append((dict(name="elsewhere: " + nm, eyes=eye_free(x, y, sc)), sc))
        res = {}
        for v, scene in vantages:
            rr = {}
            for rn, pts in routes.items():
                rr[rn] = summarise(judge_route(scene, v, pts))
            dd = {}
            for dn, (x, y) in door_pts.items():
                z = scene.ground(x, y)
                fig = figure_at(scene, x, y, z)
                dd[dn] = sees(scene, v, fig[-1])[0] or sees(scene, v, fig[1])[0]
            # every door in the layout: which a viewer here could see a figure leave
            seen = []
            for b in layout["buildings"]:
                x, y = b["door"]
                fig = figure_at(scene, x, y, scene.ground(x, y))
                if sees(scene, v, fig[-1])[0] or sees(scene, v, fig[1])[0]:
                    seen.append(b["name"])
            res[v["name"]] = dict(routes=rr, doors=dd, all_doors=seen)
        # the Row swept: from the Anchor's stretch to B, on the quay's line in front of the houses
        sweep = []
        for x in range(-10, 75, 5):
            v = dict(name="the Row at x {}".format(x), eyes=eye_free(float(x), -8.0, sc))
            s = summarise(judge_route(sc, v, routes["Hannah's climb (her door to E's)"]))
            sweep.append((x, s["head"], s.get("px35")))
        res["the Row swept (y -8)"] = sweep
        results[mode] = res

    # the report
    for mode, res in results.items():
        print("\n=== The birch's {} ===".format(mode.split()[1]))
        rows = []
        for vn, r in res.items():
            if vn.startswith("the Row swept"):
                continue
            h = r["routes"]["Hannah's climb (her door to E's)"]
            rows.append((h["head"], vn, r, h))
        rows.sort(key=lambda x: -x[0])
        for share, vn, r, h in rows:
            d = r["doors"]
            print("{:<62} Hannah's climb: head {:>4.0%}, whole {:>4.0%}, longest run {:>3} m; doors: hers {}, E's {}; "
                  "px (Lens35, far/median/near) {}; spread {}".format(
                      vn, h["head"], h["whole"], h.get("run", 0), "yes" if d["Hannah's door (Low Terrace up 18)"] else "no",
                      "yes" if d["E's door"] else "no", h.get("px35", "-"),
                      "{:.0f} deg ({})".format(h["spread_deg"], "fits" if h["fits35"] else "wider than") if "spread_deg" in h else "-"))
            if h["blocked_by"]:
                print("{:<62}   blocked by {}".format("", ", ".join("{} ({})".format(k, n) for k, n in h["blocked_by"])))
        print("\nOther routes, from the best window, the Row and the Anchor's door:")
        best_win = rows[0][1] if rows[0][1].startswith("A:") else next(vn for _, vn, _, _ in rows if vn.startswith("A:"))
        for vn in (best_win, "the Row (49.3, -12.0)", "the Anchor's door (Harbour Row 22)",
                   "the Anchor's door as W3 cast it (Harbour Row 24)"):
            r = res[vn]
            for rn, s in r["routes"].items():
                if rn.startswith("Hannah"):
                    continue
                print("  {:<52} {:<48} head {:>4.0%}, whole {:>4.0%}, px35 {}".format(vn[:52], rn, s["head"], s["whole"], s.get("px35", "-")))
            print("  {:<52} doors: {}".format(vn[:52], ", ".join("{} {}".format(k, "yes" if v else "no") for k, v in r["doors"].items())))
        print("\nEvery door in sight, by vantage (a figure's head or chest at the door):")
        for vn, r in res.items():
            if not vn.startswith("the Row swept"):
                print("  {:<62} {}".format(vn[:62], "; ".join(r["all_doors"]) or "none"))
        print("\nThe Row swept along y -8 (Hannah's climb, head in sight; px Lens35 far/median/near):")
        print("  " + "  ".join("x {}: {:.0%}".format(x, s) for x, s, _ in res["the Row swept (y -8)"]))

    print("\nThe sun at Stavanger (58.97 N, 5.73 E), elevation in degrees at the authored hours:")
    sun = {}
    days = [(datetime.date(1989, 11, d), ["15:30", "16:30"]) for d in (15, 22, 29)] + \
           [(datetime.date(1989, 12, 15), ["10:00", "12:00", "14:00", "16:00", "18:00"])] + \
           [(datetime.date(1998, 9, d), ["15:30", "16:30"]) for d in (9, 16, 23)] + \
           [(datetime.date(1998, 10, 16), ["10:00", "12:00", "14:00", "16:00", "18:00"])]
    for day, hours in days:
        off = utc_offset(day)
        el = {}
        for hh in hours:
            h, m = map(int, hh.split(":"))
            el[hh] = sun_elevation(datetime.datetime(day.year, day.month, day.day, h, m), off)
        ss, _ = sunset(day)
        sun[day.isoformat()] = dict(utc=off, sunset=ss, elevation=el)
        print("  {} ({}, UTC+{}): {}; sunset {}".format(day.strftime("%A %d %B %Y"), "CEST" if off == 2 else "CET", off,
                                                      ", ".join("{} {:+.1f}".format(k, v) for k, v in el.items()), ss))
    if a.json:
        Path(a.json).write_text(json.dumps(dict(results=results, sun=sun), indent=1, default=str), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
