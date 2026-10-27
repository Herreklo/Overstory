"""The harbour town grown from its site: a stand-in for the engine's fabric pass (reviews/lt1/town/).

    python3 blender/tools/grow_harbour.py [--out fixtures/lt1-harbour-town.json]

The site is designed as a few big shapes (SITE): a curved bay with a stone quay; the land rising behind it, steeper in
some stretches than others; the church knoll; the gully; rock banks where the hill meets the water beyond the quay;
the heath and the forest above. The grower lays the town on them as a town of this kind grows, oldest first:
- Harbour Row along the quay (lt1-street.json's houses 101-110, authored, and older houses filling its ends);
- the church on the knoll and Kirkebakken climbing to it from the square;
- lanes along the contours at the levels the site gives, each running as far as the land lets it;
- smau up the fall line between them;
- houses packed along both sides of each lane, their fronts to it. The old lanes are packed in touching runs broken
  by passages, the newer ones with gaps, and the villa road has gardens. Many houses have a back wing or an outhouse
  in the yard.
- trees planted in the gardens as the houses age, and the wild trees on the slopes, the banks and the hill above.

Each grown house gets a diary: era by the lane's age, storeys, wealth, and the dated events the town's history puts
on it. lt1-street.json's houses 201-208 and 301-307 stand on the first two lanes at their authored x. The ground is
carved where the town stands: each lane a bench at its level, each house's floor a platform, the square and the
churchyard level. Every choice is seeded from stable ids or a fixed lattice (hashing.py); nothing is seeded by where
a thing ends up.

Lengths in the fixture are integer millimetres in the street frame: x along the harbour, y inland, z up. z 0 is
Harbour Row's carriageway, and the water stands at -2.1 m.
"""

import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "blender", "resolver"))

import hashing as HS  # noqa: E402

WORLD = 1989

# -- the site: the big shapes, as facts (metres) -------------------------------------------------------------------------

SITE = dict(
    water=-2.1,
    # the quay's edge: a bay curving towards the eye at both ends, y = edge - bow * (x - centre)^2
    quay=dict(centre=58.0, edge=-15.4, bow=0.0021, x0=-34.0, x1=150.0, width=7.2),
    row=dict(carriageway=6.4, pavement=1.8),             # Harbour Row between the quay and the building line
    # the land's rise inland from the building line (s, z): steep where the old town climbs, easing to the heath,
    # rising again to the ridge
    rise=[(0.0, 0.0), (6.0, 0.6), (14.0, 3.6), (30.0, 9.8), (52.0, 17.0), (74.0, 24.4), (96.0, 31.6),
          (118.0, 38.4), (140.0, 44.0), (175.0, 54.0), (230.0, 75.0), (320.0, 110.0), (600.0, 190.0)],
    tilt=dict(cell=80.0, amp=0.2),                       # the slope's change along the bay: contours drawn in and out
    noise=[(46.0, 2.2), (17.0, 0.6)],                    # (lattice m, amplitude m): the contours' own wander
    gully=dict(x=50.0, width=12.0, depth=4.4, s0=4.0, s1=100.0),
    knoll=dict(x=114.0, s=54.0, rx=26.0, rs=20.0, h=6.0),
    # beyond the quay's ends the hill meets the water as rock: the blend's run along x, the bank's height and reach
    banks=dict(fade=22.0, height=9.0, reach=9.0),
    lanes=[  # oldest first: contour lanes at a height between two x; a climbing lane from a lane at a grade
        dict(id="lane-1", name="Strandgata", kind="contour", z=7.5, x=(-32.0, 148.0), width=3.4, surface="setts",
             laid=1880, built=(1790, 1850), grain="old", authored=200),
        dict(id="lane-2", name="Øvre Strandgate", kind="contour", z=14.0, x=(-30.0, 150.0), width=3.2,
             surface="setts", laid=1885, built=(1805, 1860), grain="old", authored=300),
        dict(id="lane-3", name="Kirkebakken", kind="climb", start=("lane-1", 40.0), grade=0.2, heading=1.0,
             width=3.2, surface="setts", laid=1890, built=(1825, 1875), grain="old"),
        dict(id="lane-4", name="Øvre gate", kind="contour", z=22.5, x=(-30.0, 96.0), width=4.2, surface="asphalt",
             laid=1968, built=(1845, 1890), grain="mid"),
        dict(id="lane-5", name="Bakkegata", kind="contour", z=31.0, x=(-26.0, 156.0), width=3.4, surface="gravel",
             laid=1900, built=(1868, 1905), grain="mid"),
        dict(id="lane-6", name="Utsikten", kind="contour", z=41.0, x=(-18.0, 168.0), width=3.6, surface="gravel",
             laid=1912, built=(1898, 1932), grain="villa"),
    ],
    smau=[-6.0, 23.7, 50.0, 85.5, 134.0],               # where the stairs run up the fall line (x at the row)
    square=dict(lane="lane-1", x=32.0, w=14.0, d=10.0),  # Torget: on Strandgata at Kirkebakken's foot
    church=dict(id=900, x=114.0, s=54.0, built=1854, nave=(19.0, 11.0), tower=5.6),
    forest=dict(above=14.0, cell=5.0),                   # the wild trees: starting above the top lane, on a lattice
    # the spruce plantings on the hill: blocks set out in rows (centre x, s inland, width, depth, turn in degrees)
    plantings=[dict(id="planting-1", x=-48.0, s=196.0, w=86.0, d=62.0, angle=7.0, planted=1957),
               dict(id="planting-2", x=104.0, s=222.0, w=96.0, d=70.0, angle=-5.0, planted=1962),
               dict(id="planting-3", x=188.0, s=170.0, w=52.0, d=58.0, angle=12.0, planted=1949)],
)

GRID = dict(x0=-90.0, y0=-90.0, x1=210.0, y1=330.0, step=1.0)
COARSE = dict(x0=-1400.0, y0=-1200.0, x1=1500.0, y1=1800.0, step=25.0)

GRAIN = {  # how a lane's plots are cut, by the age of the lane
    "old": dict(run=[(2, 3), (3, 4), (4, 3), (5, 2), (6, 1)], within=0.2, passage=(1.0, 2.6), yard=(0.15, 0.8),
                width=[((5.5, 7.5), 1), ((7.5, 10.5), 5), ((10.5, 14.0), 4)], depth=(5.8, 7.8), wing=0.5,
                outhouse=0.45, back=0.3, garden=0.4),
    "mid": dict(run=[(1, 3), (2, 4), (3, 2)], within=0.3, passage=(1.6, 4.0), yard=(0.6, 2.6),
                width=[((6.5, 8.5), 2), ((8.5, 11.0), 5), ((11.0, 13.0), 2)], depth=(6.4, 8.4), wing=0.4,
                outhouse=0.35, back=0.12, garden=0.7),
    "villa": dict(run=[(1, 1)], within=0.0, passage=(5.0, 12.0), yard=(3.0, 6.0),
                  width=[((8.5, 11.0), 1)], depth=(8.0, 10.0), wing=0.15, outhouse=0.25, back=0.0, garden=1.4),
}

# trees: their height at full age, how fast they get there (years), crown radius per metre of height, kind of crown
SPECIES = {
    "sycamore": (20.0, 35.0, 0.36, "round"),
    "birch": (16.0, 20.0, 0.26, "tall"),
    "rowan": (9.0, 15.0, 0.38, "round"),
    "apple": (6.0, 12.0, 0.55, "round"),
    "spruce": (24.0, 40.0, 0.17, "cone"),
    "pine": (15.0, 40.0, 0.32, "flat"),
}


def mm(v):
    return int(round(v * 1000.0))


# -- the land, before the town ------------------------------------------------------------------------------------------

def shore_y(x):
    q = SITE["quay"]
    return q["edge"] - q["bow"] * (x - q["centre"]) ** 2


def building_line(x):
    r = SITE["row"]
    return shore_y(x) + SITE["quay"]["width"] + r["carriageway"] + r["pavement"]


def rise(s):
    pts = SITE["rise"]
    if s <= pts[0][0]:
        return pts[0][1]
    for (s0, z0), (s1, z1) in zip(pts, pts[1:]):
        if s <= s1:
            t = (s - s0) / (s1 - s0)
            t = t * t * (3 - 2 * t) * 0.35 + t * 0.65   # eased a little at each knot, never flat
            return z0 + (z1 - z0) * t
    return pts[-1][1]


def _lattice(ix, iy, layer):
    return HS.unit(HS.h(WORLD, "harbour-site", "noise", layer, ix, iy)) * 2.0 - 1.0


def _smooth(t):
    return t * t * (3 - 2 * t)


def noise(x, y, layers=None):
    z = 0.0
    for layer, (cell, amp) in enumerate(layers or SITE["noise"]):
        fx, fy = x / cell, y / cell
        ix, iy = math.floor(fx), math.floor(fy)
        tx, ty = _smooth(fx - ix), _smooth(fy - iy)
        a = _lattice(ix, iy, layer) * (1 - tx) + _lattice(ix + 1, iy, layer) * tx
        b = _lattice(ix, iy + 1, layer) * (1 - tx) + _lattice(ix + 1, iy + 1, layer) * tx
        z += amp * (a * (1 - ty) + b * ty)
    return z


def tilt(x):
    """How much steeper or gentler the slope is at x than the rise gives (a factor on the distance inland)."""
    t = SITE["tilt"]
    fx = x / t["cell"]
    ix = math.floor(fx)
    u = _smooth(fx - ix)
    return 1.0 + t["amp"] * (_lattice(ix, 0, 9) * (1 - u) + _lattice(ix + 1, 0, 9) * u)


def bank_weight(x):
    """0 along the quay, rising to 1 beyond its ends, where the hill meets the water as rock."""
    q, b = SITE["quay"], SITE["banks"]
    out = max(q["x0"] - x, x - q["x1"], 0.0)
    return _smooth(min(1.0, out / b["fade"]))


def natural(x, y, gully=True):
    """The land's height before the town (m): the rise from the building line, the slope's change along the bay, its
    wander, the gully, the knoll and the rock banks. Seaward of the shore it falls to the sea bed. The lanes are laid
    on the land without the gully (gully=False): they cross it on fill."""
    s = y - building_line(x)
    z = rise(s * tilt(x)) if s > 0 else 0.0
    # the wander grows in from the row (the quay and the row are level)
    z += noise(x, y) * max(0.0, min(1.0, (s - 4.0) / 20.0))
    g = SITE["gully"]
    if gully and g["s0"] < s:
        across = abs(x - g["x"]) / (g["width"] * 0.5)
        along_ = min(1.0, (s - g["s0"]) / 14.0) * max(0.0, min(1.0, (g["s1"] - s) / 30.0))
        if across < 1.6:
            z -= g["depth"] * along_ * max(0.0, 1.0 - across * across / 2.56)
    k = SITE["knoll"]
    z += k["h"] * math.exp(-((x - k["x"]) / k["rx"]) ** 2 - ((s - k["s"]) / k["rs"]) ** 2) * min(1.0, max(0.0, s / 12.0))
    sh = y - shore_y(x)
    e = bank_weight(x)
    if e > 0.0:
        b = SITE["banks"]
        rock = SITE["water"] + 0.3 + b["height"] * (1.0 - math.exp(-max(sh, 0.0) / b["reach"])) \
            + noise(x * 1.9, y * 1.9, [(13.0, 1.4), (5.0, 0.5)]) * min(1.0, max(sh, 0.0) / 3.0)
        z = z * (1.0 - e) + (rock + z) * e
    if sh < 0.0:
        return SITE["water"] - 1.0 + sh * 0.25          # the sea bed
    return z


# -- lines ----------------------------------------------------------------------------------------------------------------

def contour(zk, x):
    """Where the land reaches zk inland of the building line at x (y), or None."""
    y0 = building_line(x) + 2.0
    lo, hi = y0, y0 + 300.0
    if natural(x, lo, False) >= zk or natural(x, hi, False) < zk:
        return None
    for _ in range(40):
        mid = 0.5 * (lo + hi)
        if natural(x, mid, False) < zk:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def smooth(pts, passes=3):
    for _ in range(passes):
        pts = [pts[0]] + [tuple((a[i] + 2 * b[i] + c[i]) / 4 for i in range(len(a)))
                          for a, b, c in zip(pts, pts[1:], pts[2:])] + [pts[-1]]
    return pts


def contour_line(zk, x0, x1):
    """The lane at height zk between x0 and x1: its contour, kept where it runs clear of the row and of slopes too steep
    to cut a lane into (the longest such run)."""
    runs, cur = [], []
    x = x0
    while x <= x1:
        y = contour(zk, x)
        ok = y is not None and y - building_line(x) > 16.0
        if ok:
            ok = natural(x, y + 6.0, False) - natural(x, y - 6.0, False) < 9.0
        if ok:
            cur.append((x, y, zk))
        elif cur:
            runs.append(cur)
            cur = []
        x += 2.0
    if cur:
        runs.append(cur)
    best = max(runs, key=len) if runs else []
    return smooth(best, 4)


def slope_at(x, y):
    gx = natural(x + 0.5, y, False) - natural(x - 0.5, y, False)
    gy = natural(x, y + 0.5, False) - natural(x, y - 0.5, False)
    return gx, gy


def climb_line(x, y, z, grade, heading, stop, length=240.0):
    """A lane climbing from (x, y, z) at a steady grade, heading along the slope east (+1) or west (-1): each step
    turns from the contour uphill just enough for the land to rise at the grade. It stops where stop(x, y, z) says."""
    pts = [(x, y, z)]
    step = 2.0
    while len(pts) * step < length:
        gx, gy = slope_at(x, y)
        g = math.hypot(gx, gy) or 1e-6
        ux, uy = gx / g, gy / g
        tx, ty = uy, -ux
        if tx * heading < 0:
            tx, ty = -tx, -ty
        sa = min(1.0, grade / g)
        ca = math.sqrt(max(0.0, 1.0 - sa * sa))
        x, y = x + (tx * ca + ux * sa) * step, y + (ty * ca + uy * sa) * step
        z += grade * step
        pts.append((x, y, z))
        if stop(x, y, z):
            break
    return smooth(pts, 3)


def along(line):
    """Cumulative arc length of a polyline (in plan)."""
    acc = [0.0]
    for a, b in zip(line, line[1:]):
        acc.append(acc[-1] + math.hypot(b[0] - a[0], b[1] - a[1]))
    return acc


def at(line, acc, t):
    """The point (x, y, z) and unit tangent in plan at arc length t."""
    t = max(0.0, min(acc[-1], t))
    for i in range(len(acc) - 1):
        if acc[i + 1] >= t:
            u = (t - acc[i]) / max(acc[i + 1] - acc[i], 1e-9)
            a, b = line[i], line[i + 1]
            dx, dy = b[0] - a[0], b[1] - a[1]
            L = math.hypot(dx, dy) or 1.0
            z = a[2] + (b[2] - a[2]) * u if len(a) > 2 else 0.0
            return (a[0] + dx * u, a[1] + dy * u, z), (dx / L, dy / L)
    a, b = line[-2], line[-1]
    L = math.hypot(b[0] - a[0], b[1] - a[1]) or 1.0
    return tuple(b) + (() if len(b) > 2 else (0.0,)), ((b[0] - a[0]) / L, (b[1] - a[1]) / L)


def t_at_x(line, acc, x):
    for i in range(len(line) - 1):
        lo, hi = sorted((line[i][0], line[i + 1][0]))
        if lo <= x <= hi:
            u = (x - line[i][0]) / (line[i + 1][0] - line[i][0]) if line[i + 1][0] != line[i][0] else 0.0
            return acc[i] + u * (acc[i + 1] - acc[i])
    return None


# -- footprints and clearances ---------------------------------------------------------------------------------------------

def rect(cx, cy, ux, uy, w, d):
    """A footprint's corners: front-left, front-right, back-right, back-left; the front centred on (cx, cy) along u,
    the back d away on u's left."""
    nx, ny = -uy, ux
    hw = w / 2
    return [(cx - ux * hw, cy - uy * hw), (cx + ux * hw, cy + uy * hw),
            (cx + ux * hw + nx * d, cy + uy * hw + ny * d), (cx - ux * hw + nx * d, cy - uy * hw + ny * d)]


def box(poly, pad=0.0):
    xs, ys = [p[0] for p in poly], [p[1] for p in poly]
    return min(xs) - pad, min(ys) - pad, max(xs) + pad, max(ys) + pad


def overlaps(a, b, gap):
    """Whether two convex footprints come within gap of each other (separating axes, with the gap as margin)."""
    for poly in (a, b):
        for i in range(len(poly)):
            p, q = poly[i], poly[(i + 1) % len(poly)]
            ax, ay = q[1] - p[1], p[0] - q[0]
            L = math.hypot(ax, ay) or 1.0
            ax, ay = ax / L, ay / L
            pa = [x * ax + y * ay for x, y in a]
            pb = [x * ax + y * ay for x, y in b]
            if max(pa) + gap <= min(pb) or max(pb) + gap <= min(pa):
                return False
    return True


def inside(poly, x, y):
    c = False
    j = len(poly) - 1
    for i in range(len(poly)):
        xi, yi = poly[i]
        xj, yj = poly[j]
        if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / (yj - yi + 1e-12) + xi:
            c = not c
        j = i
    return c


def seg_dist(px, py, a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]
    L2 = dx * dx + dy * dy
    u = 0.0 if L2 == 0 else max(0.0, min(1.0, ((px - a[0]) * dx + (py - a[1]) * dy) / L2))
    return math.hypot(px - a[0] - dx * u, py - a[1] - dy * u)


def poly_dist(poly, x, y):
    if inside(poly, x, y):
        return 0.0
    return min(seg_dist(x, y, poly[i], poly[(i + 1) % len(poly)]) for i in range(len(poly)))


class Ground:
    """What the town has claimed so far: footprints, and the strips of lanes, smau and level places, each with a
    clearance. A spatial hash keeps the checks cheap."""

    CELL = 12.0

    def __init__(self):
        self.polys = {}
        self.strips = []           # (points, half width) for lanes and smau
        self.places = []           # level places (the square, the churchyard): polygons kept clear of houses

    def _cells(self, bx):
        c = self.CELL
        for i in range(int(math.floor(bx[0] / c)), int(math.floor(bx[2] / c)) + 1):
            for j in range(int(math.floor(bx[1] / c)), int(math.floor(bx[3] / c)) + 1):
                yield i, j

    def claim(self, fp):
        for k in self._cells(box(fp)):
            self.polys.setdefault(k, []).append(fp)

    def near(self, bx):
        seen = set()
        for k in self._cells(bx):
            for p in self.polys.get(k, ()):
                if id(p) not in seen:
                    seen.add(id(p))
                    yield p

    def free(self, fp, gap, strip_gap=1.0, skip_strip=None, ignore=()):
        bx = box(fp, gap)
        if any(overlaps(fp, o, gap) for o in self.near(bx) if all(o is not i for i in ignore) and
               not (box(o)[0] > bx[2] or box(o)[2] < bx[0] or box(o)[1] > bx[3] or box(o)[3] < bx[1])):
            return False
        for place in self.places:
            if overlaps(fp, place, 0.6):
                return False
        for n, (pts, hw) in enumerate(self.strips):
            if n == skip_strip:
                continue
            for a, b in zip(pts, pts[1:]):
                if max(a[0], b[0]) < bx[0] - hw or min(a[0], b[0]) > bx[2] + hw or \
                        max(a[1], b[1]) < bx[1] - hw or min(a[1], b[1]) > bx[3] + hw:
                    continue
                # the strip's centre line within its half width (and the gap) of the footprint
                if any(seg_dist(q[0], q[1], a, b) < hw + strip_gap for q in fp) or \
                        any(poly_dist(fp, p[0], p[1]) < hw + strip_gap for p in (a, b, ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2))):
                    return False
        return True

    def clear_point(self, x, y, r):
        bx = (x - r, y - r, x + r, y + r)
        for o in self.near(bx):
            if poly_dist(o, x, y) < r:
                return False
        for place in self.places:
            if poly_dist(place, x, y) < r * 0.5:
                return False
        for pts, hw in self.strips:
            for a, b in zip(pts, pts[1:]):
                if max(a[0], b[0]) < x - r - hw or min(a[0], b[0]) > x + r + hw or \
                        max(a[1], b[1]) < y - r - hw or min(a[1], b[1]) > y + r + hw:
                    continue
                if seg_dist(x, y, a, b) < hw + r:
                    return False
        return True


# -- houses ----------------------------------------------------------------------------------------------------------------

def era_for(year, key):
    if year < 1870:
        return "classical"
    if year < 1890:
        return "classical" if HS.unit(key) < 0.55 else "chalet"
    return "chalet"


def diary(hid, built, era, rs, character, storeys_w):
    """A grown house's life to 1989: what the town's history puts on a house of its age and kind (a stand-in for the
    engine's fabric pass). The coats are the care rule's (paint.json), not events, unless the house was let go."""
    storeys = rs.weighted(storeys_w)
    wealth = int(rs.uniform(260, 900))
    ev = [dict(id=1, year=built, kind="built", params=dict(era=era, storeys=storeys, wealth=wealth),
               cause="built as the town climbed the hill")]
    n = 2
    if rs.random() < 0.32:
        ev.append(dict(id=n, year=int(rs.uniform(1952, 1981)), kind="windows_replaced",
                       params=dict(scope=rs.choice(["street", "all"])), cause="new windows, the fashion of the day"))
        n += 1
    let_go = rs.random()
    if let_go < 0.14:
        y = int(rs.uniform(1968, 1984))
        ev.append(dict(id=n, year=y, kind="neglected", params=dict(amount=int(rs.uniform(350, 650))),
                       cause="the old owner dies; the heirs live elsewhere"))
        n += 1
        if rs.random() < 0.3:
            ev.append(dict(id=n, year=min(1988, y + int(rs.uniform(2, 8))), kind="boarded", params=dict(scope="ground"),
                           cause="empty"))
            n += 1
    elif let_go < 0.22:
        ev.append(dict(id=n, year=int(rs.uniform(1979, 1988)), kind="restored", params=dict(amount=400),
                       cause="a young family buys it and does it up"))
        n += 1
    ev.sort(key=lambda e: (e["year"], e["id"]))
    return dict(id=hid, type="house", character=character, events=ev)


def storey_height(storeys, era):
    return {1000: 3.0, 1500: 4.3, 2000: 5.7, 2500: 6.9}[storeys] + (0.2 if era == "chalet" else 0.0)


STOREYS = {"old": [(1000, 2), (1500, 6), (2000, 3)], "mid": [(1500, 4), (2000, 5)],
           "villa": [(1500, 2), (2000, 6), (2500, 1)]}


def placement(pid, kind, of, lane, side, fp, base, eave, pitch, roof):
    (x0, y0), (x1, y1) = fp[0], fp[1]
    return dict(id=pid, kind=kind, of=of, lane=lane, side=side,
                x=mm((x0 + x1) / 2), y=mm((y0 + y1) / 2), angle=round(math.degrees(math.atan2(y1 - y0, x1 - x0)), 2),
                w=mm(math.hypot(x1 - x0, y1 - y0)), d=mm(math.hypot(fp[3][0] - x0, fp[3][1] - y0)),
                base=mm(base), eave=mm(eave), pitch=int(round(pitch)), roof=roof,
                footprint=[v for x, y in fp for v in (mm(x), mm(y))])


def yard_things(house, fp, grain, base, built, ground, placements, gardens, rs, lane, side):
    """A house's wing and outhouse, and where its garden trees may stand: all behind it, on its plot."""
    hid = house["id"]
    g = GRAIN[grain]
    (fx0, fy0), (fx1, fy1), (bx1, by1), (bx0, by0) = fp
    w = math.hypot(fx1 - fx0, fy1 - fy0)
    ux, uy = (fx1 - fx0) / w, (fy1 - fy0) / w
    nx, ny = -uy, ux
    eave = house["eave"] / 1000.0
    # a back wing at one end of the back wall, lower than the house, its ridge across the house's
    if rs.random() < g["wing"] and w > 6.0:
        ww = rs.uniform(3.4, min(6.0, w - 2.0))
        wd = rs.uniform(3.0, 5.0)
        end = rs.choice([-1.0, 1.0])
        inset = rs.uniform(0.0, 1.2)
        off = end * (w / 2 - ww / 2 - inset)
        cx, cy = (bx0 + bx1) / 2 + ux * off, (by0 + by1) / 2 + uy * off
        wfp = rect(cx, cy, ux, uy, ww, wd)
        if ground.free(wfp, 0.4, ignore=(fp,)):
            ground.claim(wfp)
            weave = max(base + 2.6, eave - rs.uniform(1.0, 1.8))
            placements.append(placement(hid * 100 + 1, "wing", hid, lane, side, wfp, base, weave, rs.uniform(34, 42),
                                        "gable"))
    # an outhouse in the yard: a shed, a wash house or a store
    if rs.random() < g["outhouse"]:
        ow, od = rs.uniform(3.0, 5.2), rs.uniform(2.6, 4.0)
        back = rs.uniform(1.6, 4.5)
        lat = rs.uniform(-0.5, 0.5) * max(0.0, w - ow)
        cx = (bx0 + bx1) / 2 + nx * back + ux * lat
        cy = (by0 + by1) / 2 + ny * back + uy * lat
        ofp = rect(cx, cy, ux, uy, ow, od)
        if ground.free(ofp, 0.5):
            ground.claim(ofp)
            ob = natural(cx + nx * od / 2, cy + ny * od / 2) + 0.1
            placements.append(placement(hid * 100 + 2, "outhouse", hid, lane, side, ofp, ob, ob + rs.uniform(2.2, 2.7),
                                        rs.uniform(26, 36), rs.choice(["eaves", "gable"])))
    # the garden: where trees may be planted behind the house
    n = g["garden"]
    count = int(n) + (1 if rs.random() < n - int(n) else 0)
    for i in range(count):
        back = rs.uniform(2.5, 8.0)
        lat = rs.uniform(-0.6, 0.6) * w
        x = (bx0 + bx1) / 2 + nx * back + ux * lat
        y = (by0 + by1) / 2 + ny * back + uy * lat
        gardens.append(dict(of=hid, n=i, x=x, y=y, built=built, grain=grain))


def grow():
    lanes, placements, buildings, stairs = [], [], [], []
    gardens = []
    ground = Ground()
    street = json.load(open(os.path.join(ROOT, "fixtures", "lt1-street.json")))
    authored = {b["id"]: b for b in street["buildings"]}

    # the church on its knoll, first: the landmark the town grew towards
    c = SITE["church"]
    cy_mid = building_line(c["x"]) + c["s"]
    cbase = natural(c["x"], cy_mid) + 0.3
    L, D = c["nave"]
    nave = rect(c["x"], cy_mid - D / 2, 1.0, 0.0, L, D)
    T = c["tower"]
    tower = rect(c["x"] - L / 2 - T / 2 + 0.3, cy_mid - T / 2, 1.0, 0.0, T, T)
    yard = rect(c["x"] - 3.0, cy_mid - 13.0, 1.0, 0.0, L + T + 14.0, 26.0)
    platform = rect(c["x"] - T / 2 - 0.5, cy_mid - D / 2 - 3.0, 1.0, 0.0, L + T + 7.0, D + 6.0)
    ground.claim(nave)
    ground.claim(tower)
    ground.places.append(yard)
    buildings.append(dict(id=c["id"], type="church", character="knoll",
                          events=[dict(id=1, year=c["built"], kind="built", params=dict(era="classical", storeys=2500,
                                                                                        wealth=900),
                                       cause="the town builds its church on the knoll"),
                                  dict(id=2, year=1962, kind="restored", params=dict(amount=500),
                                       cause="the parish restores the church for its centenary")]))
    placements.append(placement(c["id"], "church", 0, "", "", nave, cbase, cbase + 7.6, 46, "eaves"))
    placements.append(placement(c["id"] * 100 + 1, "tower", c["id"], "", "", tower, cbase, cbase + 17.5, 77, "spire"))

    # Harbour Row: lt1-street.json's houses 101-110 on the building line, at their plots' x
    row_line = [(x, building_line(x), 0.0) for x in [SITE["quay"]["x0"] + 2.0 * i for i in range(93)]]
    row_acc = along(row_line)
    row_spans = []
    for b in street["buildings"]:
        if b["id"] // 100 != 1:
            continue
        p = b["plot"]
        built = next(e for e in b["events"] if e["kind"] == "built")
        x0, w, d = p["x"] / 1000.0, p["w"] / 1000.0, p["d"] / 1000.0
        t0 = t_at_x(row_line, row_acc, x0)
        rs = HS.Stream(WORLD, b["id"], "harbour", "plot")
        gap = rs.uniform(0.4, 1.0)
        (cx, cy, _), (ux, uy) = at(row_line, row_acc, t0 + w / 2)
        fw = w - gap
        era = built["params"]["era"]
        fp = rect(cx, cy, ux, uy, fw, d)
        ground.claim(fp)
        row_spans.append((t0, t0 + w))
        buildings.append(b)
        storeys = built["params"].get("storeys", 2000)
        roof = "gable" if b["type"] == "warehouse" or (era == "chalet" and "ark" not in built["params"].get("with", [])
                                                        and rs.random() < 0.4) else "eaves"
        placements.append(placement(b["id"], b["type"], 0, "harbour-row", "up", fp, 0.25,
                                    0.25 + storey_height(storeys, era if era in ("classical", "chalet") else "classical"),
                                    rs.uniform(36, 42) if era != "chalet" else rs.uniform(42, 48), roof))
        yard_things(placements[-1], fp, "old", 0.25, built["year"], ground, placements, gardens, rs, "harbour-row", "up")

    # the lanes, oldest first, and the smau up the fall line through them
    lines, strips = {}, {}
    for spec in SITE["lanes"]:
        if spec["kind"] == "contour":
            line = contour_line(spec["z"], *spec["x"])
        else:
            src, sx = spec["start"]
            sl = lines[src]
            sacc = along(sl)
            (px, py, pz), _ = at(sl, sacc, t_at_x(sl, sacc, sx))
            cxk, cyk = c["x"], cy_mid

            def stop(x, y, z):
                return math.hypot(x - cxk, y - cyk) < 20.0 or z > cbase - 0.3
            line = climb_line(px, py, pz, spec["grade"], spec["heading"], stop)
        lines[spec["id"]] = line
        lanes.append(dict(id=spec["id"], name=spec["name"], surface=spec["surface"], laid=spec["laid"],
                          z=mm(line[0][2]), width=mm(spec["width"]),
                          points=[v for x, y, z in line for v in (mm(x), mm(y), mm(z))]))
        strips[spec["id"]] = len(ground.strips)
        ground.strips.append(([(x, y) for x, y, _ in line], spec["width"] / 2))
    # the Row as a strip, so nothing grows onto it
    ground.strips.append(([(x, y - (SITE["row"]["carriageway"] / 2 + SITE["row"]["pavement"])) for x, y, _ in row_line],
                          SITE["row"]["carriageway"] / 2 + 0.3))
    # the square: level, on Strandgata's uphill side
    sq = SITE["square"]
    l1 = lines[sq["lane"]]
    a1 = along(l1)
    (qx, qy, qz), (qux, quy) = at(l1, a1, t_at_x(l1, a1, sq["x"]))
    square = rect(qx, qy + SITE["lanes"][0]["width"] / 2, qux, quy, sq["w"], sq["d"])
    ground.places.append(square)
    crossings = {}
    for i, sx in enumerate(SITE["smau"]):
        pts = [(sx, building_line(sx), 0.0)]
        for spec in SITE["lanes"]:
            line = lines[spec["id"]]
            if spec["kind"] != "contour" or not line or not (line[0][0] < sx < line[-1][0]):
                continue
            acc = along(line)
            t = t_at_x(line, acc, sx)
            (px, py, pz), _ = at(line, acc, t)
            pts.append((px, py, pz))
            crossings.setdefault(spec["id"], []).append(t)
        pts.sort(key=lambda p: p[1])
        gully = abs(sx - SITE["gully"]["x"]) < 1
        width = 2.0 if gully else 1.6
        stairs.append(dict(id=f"smau-{i + 1}", name="Gully Steps" if gully else f"smau {i + 1}", width=mm(width),
                           points=[v for x, y, z in pts for v in (mm(x), mm(y), mm(z))]))
        ground.strips.append(([(x, y) for x, y, _ in pts], width / 2 + 0.4))

    # the Row's ends: older houses and stores fill it beyond the authored plots
    hid = 1000
    rs = HS.Stream(WORLD, "harbour-row", "fill")
    for (t_from, t_to) in [(1.0, row_spans[0][0] - 0.6) if row_spans else (1.0, row_acc[-1]),
                           (max(e for _, e in row_spans) + 0.6, row_acc[-1] - 1.0)]:
        t = t_from
        while t < t_to - 5.0:
            store = rs.random() < 0.3
            w = min(t_to - t, rs.uniform(8.0, 10.0) if store else rs.uniform(7.0, 12.0))
            d = rs.uniform(11.0, 14.0) if store else rs.uniform(7.5, 9.5)
            (cx, cy, _), (ux, uy) = at(row_line, row_acc, t + w / 2)
            fp = rect(cx, cy, ux, uy, w - 0.3, d)
            if w > 5.0 and ground.free(fp, 0.15, 0.6):
                ground.claim(fp)
                hid += 1
                rh = HS.Stream(WORLD, hid, "diary")
                built = int(rh.uniform(1790, 1880))
                era = era_for(built, HS.h(WORLD, hid, "era"))
                dy = diary(hid, built, era, rh, "harbour", [(2000, 5), (2500, 3)])
                if store:
                    dy["type"] = "warehouse"
                buildings.append(dy)
                st = dy["events"][0]["params"]["storeys"]
                placements.append(placement(hid, dy["type"], 0, "harbour-row", "up", fp, 0.25,
                                            0.25 + storey_height(st, era),
                                            rh.uniform(36, 44), "gable" if store else "eaves"))
                if not store:
                    yard_things(placements[-1], fp, "old", 0.25, built, ground, placements, gardens, rh, "harbour-row",
                                "up")
                t += w + rs.weighted([(0.0, 3), (rs.uniform(1.4, 3.0), 2)])
            else:
                t += 1.5

    # the lanes' houses: the authored ones first at their x, then the plots packed along both sides
    for spec in SITE["lanes"]:
        line = lines[spec["id"]]
        if len(line) < 4:
            continue
        lid = spec["id"]
        g = GRAIN[spec["grain"]]
        acc = along(line)
        b0, b1 = spec["built"]
        strip_n = strips[lid]

        def site_house(t, w, d, yardd, side):
            """The footprint of a house fronting the lane at arc length t (its front's centre), or None."""
            (cx, cy, cz), (ux, uy) = at(line, acc, t)
            nx, ny = -uy, ux                                   # left of the lane's run
            if ny < 0:
                nx, ny = -nx, -ny                              # inland
            sgn = 1.0 if side == "up" else -1.0
            off = spec["width"] / 2 + yardd
            fx, fy = cx + nx * off * sgn, cy + ny * off * sgn
            # the front runs so that its left, where rect puts the back, points away from the lane
            return rect(fx, fy, ny * sgn, -nx * sgn, w, d), cz

        def blocked(t, w):
            return any(abs(t - c_) < w / 2 + 2.0 for c_ in crossings.get(lid, []))

        def add_house(hid_, fp, cz, side, built, era, dy, rs_, roof_w):
            nonlocal hid
            ground.claim(fp)
            buildings.append(dy)
            st = dy["events"][0]["params"]["storeys"]
            base = cz + (0.45 if side == "up" else 0.2)
            gable = era == "chalet" and rs_.random() < roof_w
            pitch = rs_.uniform(36, 42) if era == "classical" else rs_.uniform(42, 50)
            house = placement(hid_, "house", 0, lid, side, fp, base,
                              base + storey_height(st, era if era in ("classical", "chalet") else "classical"),
                              pitch, "gable" if gable else "eaves")
            placements.append(house)
            # a back house on the plot, reached by a passage: the yard built over as the town filled
            if rs_.random() < g["back"]:
                (fx0, fy0), (fx1, fy1), (bx1, by1), (bx0, by0) = fp
                w_ = math.hypot(fx1 - fx0, fy1 - fy0)
                ux, uy = (fx1 - fx0) / w_, (fy1 - fy0) / w_
                bw, bd = rs_.uniform(6.0, min(10.0, w_ + 1.5)), rs_.uniform(5.0, 6.6)
                gap_ = rs_.uniform(2.2, 4.0)
                lat = rs_.uniform(-0.4, 0.4) * max(0.0, w_ - bw)
                cx, cy = (bx0 + bx1) / 2 - uy * gap_ + ux * lat, (by0 + by1) / 2 + ux * gap_ + uy * lat
                bfp = rect(cx, cy, ux, uy, bw, bd)
                if ground.free(bfp, 0.5, 0.8):
                    ground.claim(bfp)
                    hid += 1
                    rb = HS.Stream(WORLD, hid, "diary")
                    bbuilt = int(rb.uniform(min(built + 8, 1900), min(built + 50, 1935)))
                    bera = era_for(bbuilt, HS.h(WORLD, hid, "era"))
                    bdy = diary(hid, bbuilt, bera, rb, "back", [(1000, 3), (1500, 5), (2000, 1)])
                    buildings.append(bdy)
                    bb = natural(cx, cy) + 0.2
                    bst = bdy["events"][0]["params"]["storeys"]
                    placements.append(placement(hid, "house", 0, lid, "back", bfp, bb, bb + storey_height(bst, bera),
                                                rb.uniform(34, 44), "eaves"))
            yard_things(house, fp, spec["grain"], base, built, ground, placements, gardens, rs_, lid, side)

        # lt1-street.json's houses for this lane stand on its uphill side in their authored order, each taking the
        # first plot at or past its authored x
        queue = sorted((b for b in street["buildings"] if spec.get("authored") and
                        b["id"] // 100 == spec["authored"] // 100), key=lambda b: b["plot"]["x"])
        for side in ("up", "down"):
            rs = HS.Stream(WORLD, lid, side, "plots")
            t = rs.uniform(1.0, 4.0)
            run = 0
            while t < acc[-1] - 4.0:
                if run == 0:
                    run = rs.weighted(g["run"])
                w = rs.uniform(*rs.weighted(g["width"]))
                d = rs.uniform(*g["depth"])
                yardd = rs.uniform(*g["yard"])
                (px, _, _), _ = at(line, acc, t + w / 2)
                auth = queue[0] if side == "up" and queue and px >= queue[0]["plot"]["x"] / 1000.0 else None
                if auth:
                    w, d = auth["plot"]["w"] / 1000.0 - 0.3, auth["plot"]["d"] / 1000.0
                fp = None
                for nudge in (0.0, 0.3, 0.6, 1.0, 1.5) if run > 0 else (0.0,):
                    mid = t + nudge + w / 2
                    if blocked(mid, w):
                        break
                    fp, cz = site_house(mid, w, d, yardd, side)
                    if ground.free(fp, 0.12 if g["within"] else 0.6, 0.5, strip_n):
                        t += nudge
                        break
                    fp = None
                if fp is None:
                    run = 0
                    t += 1.5
                    continue
                if auth:
                    queue.pop(0)
                    rh = HS.Stream(WORLD, auth["id"], "harbour", "plot")
                    built = next(e for e in auth["events"] if e["kind"] == "built")
                    add_house(auth["id"], fp, cz, side, built["year"], built["params"]["era"], auth, rh, 0.45)
                else:
                    hid += 1
                    rh = HS.Stream(WORLD, hid, "diary")
                    built = int(rh.uniform(b0, b1))
                    era = era_for(built, HS.h(WORLD, hid, "era"))
                    dy = diary(hid, built, era, rh, spec["grain"], STOREYS[spec["grain"]])
                    add_house(hid, fp, cz, side, built, era, dy, rh, 0.55 if spec["grain"] == "villa" else 0.45)
                run -= 1
                t += w + (g["within"] if run > 0 else rs.uniform(*g["passage"]))
    return lanes, stairs, buildings, placements, lines, gardens, ground, (yard, square, cbase, platform)


# -- trees ------------------------------------------------------------------------------------------------------------------

def tree(tid, species, x, y, planted, cause):
    hmax, k, rr, crown = SPECIES[species]
    age = max(3, WORLD - planted)
    hgt = hmax * (1.0 - math.exp(-age / k)) * (0.85 + 0.3 * HS.unit(HS.h(WORLD, tid, "vigour")))
    return dict(id=tid, species=species, crown=crown, x=mm(x), y=mm(y), z=mm(natural(x, y)), h=mm(hgt),
                r=mm(max(0.8, hgt * rr)), planted=planted, cause=cause)


def in_planting(pl, x, y):
    s = y - building_line(x)
    a = math.radians(pl["angle"])
    dx, ds = x - pl["x"], s - pl["s"]
    u, v = dx * math.cos(a) + ds * math.sin(a), -dx * math.sin(a) + ds * math.cos(a)
    return abs(u) < pl["w"] / 2 and abs(v) < pl["d"] / 2


def plant(gardens, ground, places, top_line):
    """The trees: in the gardens as the houses aged, around the churchyard, and wild on the slopes the town left,
    the rock banks and the hill above the top lane."""
    trees = []
    for gd in gardens:
        tid = f"tree-{gd['of']}-{gd['n']}"
        rs = HS.Stream(WORLD, tid, "plant")
        species = rs.weighted({"old": [("sycamore", 3), ("apple", 4), ("birch", 2), ("rowan", 3)],
                               "mid": [("sycamore", 3), ("apple", 3), ("birch", 3), ("rowan", 2), ("spruce", 1)],
                               "villa": [("sycamore", 3), ("apple", 3), ("birch", 3), ("spruce", 2), ("rowan", 1)]}[gd["grain"]])
        if not ground.clear_point(gd["x"], gd["y"], 1.0):
            continue
        planted = min(1984, gd["built"] + int(rs.uniform(4, 70)))
        trees.append(tree(tid, species, gd["x"], gd["y"], planted, "planted in the garden"))
    # the churchyard's trees: a ring of sycamores planted when the church was new
    churchyard, square, cbase, platform = places
    cx = sum(p[0] for p in churchyard) / 4
    cy = sum(p[1] for p in churchyard) / 4
    for i in range(14):
        rs = HS.Stream(WORLD, "churchyard", i)
        a = 2 * math.pi * i / 14 + rs.uniform(-0.15, 0.15)
        x, y = cx + math.cos(a) * 18.5, cy + math.sin(a) * 14.5
        if ground.clear_point(x, y, 1.0):
            trees.append(tree(f"tree-church-{i}", "sycamore", x, y, 1858 + int(rs.uniform(0, 14)),
                              "planted round the new churchyard"))
    # wild trees, on a fixed lattice: dense above the top lane (the planting and the birch coming up as grazing
    # stopped), thinner on the rock banks and on the slopes in the town that nobody built on
    f = SITE["forest"]
    cell = f["cell"]
    for pl in SITE["plantings"]:
        a = math.radians(pl["angle"])
        row = 3.6
        for iu in range(int(pl["w"] / row)):
            for iv in range(int(pl["d"] / row)):
                rs = HS.Stream(WORLD, pl["id"], iu, iv)
                if rs.random() > 0.88:
                    continue
                u = -pl["w"] / 2 + (iu + 0.5 + rs.uniform(-0.15, 0.15)) * row
                v = -pl["d"] / 2 + (iv + 0.5 + rs.uniform(-0.15, 0.15)) * row
                x = pl["x"] + u * math.cos(a) - v * math.sin(a)
                s_ = pl["s"] + u * math.sin(a) + v * math.cos(a)
                y = building_line(x) + s_
                if not (GRID["x0"] < x < GRID["x1"] and GRID["y0"] < y < GRID["y1"]) or not ground.clear_point(x, y, 2.0):
                    continue
                trees.append(tree(f"tree-{pl['id']}-{iu}-{iv}", "spruce", x, y, pl["planted"] + int(rs.uniform(-1, 2)),
                                  "the spruce planting on the hill"))
    tacc = along(top_line)
    for j in range(int((GRID["y1"] - GRID["y0"]) / cell)):
        for i in range(int((GRID["x1"] - GRID["x0"]) / cell)):
            key = HS.h(WORLD, "harbour-wild", i, j)
            rs = HS.Stream(key)
            x = GRID["x0"] + (i + rs.uniform(0.1, 0.9)) * cell
            y = GRID["y0"] + (j + rs.uniform(0.1, 0.9)) * cell
            sh = y - shore_y(x)
            if sh < 2.0:
                continue
            e = bank_weight(x)
            tt = t_at_x(top_line, tacc, x)
            top_y = at(top_line, tacc, tt)[0][1] if tt is not None else building_line(x) + 140.0
            above = y - top_y - f["above"]
            patch = noise(x, y, [(70.0, 1.0), (23.0, 0.5)])
            if any(in_planting(pl, x, y) for pl in SITE["plantings"]):
                continue                                         # planted in its own rows, above
            if above > 0:
                # the heath, grazed until the 1950s: birch coming up in groves along the town's edge and the hollows,
                # a few pines and rowans out on it
                grove = patch > 0.15 and above < 70
                p = (0.5 if grove else 0.035) - (0.15 if above < 10 else 0.0)
                pool = [("birch", 6), ("rowan", 1)] if grove else [("pine", 3), ("birch", 2), ("rowan", 1)]
                age = rs.uniform(15, 40) if grove else rs.uniform(20, 90)
                cause = "birch coming up as grazing stopped" if grove else "self-seeded on the heath"
            elif e > 0.2:
                p = 0.22 * e + 0.15 * patch
                pool = [("pine", 4), ("birch", 3), ("rowan", 1)]
                age = rs.uniform(15, 90)
                cause = "self-seeded on the rock"
            else:
                p = 0.10 + 0.08 * patch
                pool = [("birch", 4), ("rowan", 2), ("sycamore", 2)]
                age = rs.uniform(10, 60)
                cause = "self-seeded on the slope"
            if rs.random() >= p:
                continue
            if not ground.clear_point(x, y, 2.2):
                continue
            trees.append(tree(f"tree-w{i}-{j}", rs.weighted(pool), x, y, int(WORLD - age), cause))
    return trees


# -- the ground, carved where the town stands ----------------------------------------------------------------------------

def carve(lines, placements, places):
    g = GRID
    nx = int(round((g["x1"] - g["x0"]) / g["step"])) + 1
    ny = int(round((g["y1"] - g["y0"]) / g["step"])) + 1
    Z = [[natural(g["x0"] + i * g["step"], g["y0"] + j * g["step"]) for i in range(nx)] for j in range(ny)]
    kind = [[0] * nx for _ in range(ny)]   # 0 land, 1 quay and row, 2 lane, 3 a house's ground, 4 stair, 5 a level place

    def cell(x, y):
        return int(round((x - g["x0"]) / g["step"])), int(round((y - g["y0"]) / g["step"]))

    # the quay and the row: level from the quay's edge to the building line
    for j in range(ny):
        y = g["y0"] + j * g["step"]
        for i in range(nx):
            x = g["x0"] + i * g["step"]
            if SITE["quay"]["x0"] - 6 <= x <= SITE["quay"]["x1"] + 6 and shore_y(x) <= y <= building_line(x) + 0.5:
                if Z[j][i] < 6.0:
                    Z[j][i] = 0.0
                    kind[j][i] = 1

    def bench(pts, hw, shoulder, mark):
        """A level strip along pts (x, y, z): within hw level at the nearest point's z, easing back over the shoulder."""
        for a, b in zip(pts, pts[1:]):
            r = hw + shoulder + 1
            i0, j0 = cell(min(a[0], b[0]) - r, min(a[1], b[1]) - r)
            i1, j1 = cell(max(a[0], b[0]) + r, max(a[1], b[1]) + r)
            for j in range(max(0, j0), min(ny, j1 + 1)):
                for i in range(max(0, i0), min(nx, i1 + 1)):
                    px, py = g["x0"] + i * g["step"], g["y0"] + j * g["step"]
                    dx, dy = b[0] - a[0], b[1] - a[1]
                    L2 = dx * dx + dy * dy or 1e-9
                    u = max(0.0, min(1.0, ((px - a[0]) * dx + (py - a[1]) * dy) / L2))
                    d = math.hypot(px - a[0] - dx * u, py - a[1] - dy * u)
                    zl = a[2] + (b[2] - a[2]) * u
                    if d <= hw:
                        Z[j][i] = zl
                        kind[j][i] = mark
                    elif d <= hw + shoulder and kind[j][i] in (0, 3):
                        v = (d - hw) / shoulder
                        Z[j][i] = zl + (Z[j][i] - zl) * v * v

    for k, spec in enumerate(SITE["lanes"]):
        line = lines[spec["id"]]
        if line:
            bench(line, spec["width"] / 2, 1.5, 2)
    # the level places: the square at Strandgata's level, the churchyard at the church's floor
    churchyard, square, cbase, platform = places
    l1 = lines["lane-1"]
    for poly, z in ((square, l1[0][2]), (platform, cbase - 0.3)):
        xs, ys = [p[0] for p in poly], [p[1] for p in poly]
        i0, j0 = cell(min(xs) - 2.5, min(ys) - 2.5)
        i1, j1 = cell(max(xs) + 2.5, max(ys) + 2.5)
        for j in range(max(0, j0), min(ny, j1 + 1)):
            for i in range(max(0, i0), min(nx, i1 + 1)):
                px, py = g["x0"] + i * g["step"], g["y0"] + j * g["step"]
                dd = poly_dist(poly, px, py)
                if dd == 0.0:
                    Z[j][i] = z
                    kind[j][i] = 5
                elif dd < 5.0 and kind[j][i] == 0:
                    v = dd / 5.0
                    Z[j][i] = z + (Z[j][i] - z) * v * v
    # each house's ground: its floor's platform where the land stands above it (cut); where it falls away the
    # plinth goes down to it (left as it is)
    for p in placements:
        fp = [(p["footprint"][i] / 1000.0, p["footprint"][i + 1] / 1000.0) for i in range(0, 8, 2)]
        base = p["base"] / 1000.0
        xs, ys = [q[0] for q in fp], [q[1] for q in fp]
        i0, j0 = cell(min(xs) - 1.5, min(ys) - 1.5)
        i1, j1 = cell(max(xs) + 1.5, max(ys) + 1.5)
        for j in range(max(0, j0), min(ny, j1 + 1)):
            for i in range(max(0, i0), min(nx, i1 + 1)):
                px, py = g["x0"] + i * g["step"], g["y0"] + j * g["step"]
                if inside(fp, px, py):
                    if Z[j][i] > base - 0.15:
                        Z[j][i] = base - 0.15
                    if kind[j][i] == 0:
                        kind[j][i] = 3
    return dict(x0=mm(g["x0"]), y0=mm(g["y0"]), step=mm(g["step"]), nx=nx, ny=ny,
                z=[mm(v) for row in Z for v in row], kind=[v for row in kind for v in row])


def coarse():
    c = COARSE
    nx = int(round((c["x1"] - c["x0"]) / c["step"])) + 1
    ny = int(round((c["y1"] - c["y0"]) / c["step"])) + 1
    Z = []
    for j in range(ny):
        y = c["y0"] + j * c["step"]
        row = []
        for i in range(nx):
            x = c["x0"] + i * c["step"]
            if GRID["x0"] < x < GRID["x1"] and GRID["y0"] < y < GRID["y1"]:
                row.append(mm(natural(x, y) - 1.5))   # under the fine ground, never through it
                continue
            # beyond the town: the far hills, the bay's open sea behind the eye
            z = natural(x, y)
            far = noise(x / 6.0, y / 6.0) * 30.0
            if y - shore_y(max(-200.0, min(320.0, x))) > 0 or abs(x - 58) > 260:
                z = max(z, 18.0 + far + 0.12 * max(0.0, abs(x - 58) - 140)) if abs(x - 58) > 140 else z
            row.append(mm(z))
        Z.append(row)
    return dict(x0=mm(c["x0"]), y0=mm(c["y0"]), step=mm(c["step"]), nx=nx, ny=ny, z=[v for row in Z for v in row])


def main(argv):
    out = os.path.join(ROOT, "fixtures", "lt1-harbour-town.json")
    if "--out" in argv:
        out = argv[argv.index("--out") + 1]
    lanes, stairs, buildings, placements, lines, gardens, ground, places = grow()
    top = max(SITE["lanes"], key=lambda s: s.get("z", 0.0))["id"]
    trees = plant(gardens, ground, places, lines[top])
    grid = carve(lines, placements, places)
    fixture = dict(
        schemaVersion=1,
        note="LT1's harbour town grown by blender/tools/grow_harbour.py from its site (a stand-in for the engine's "
             "fabric pass). lt1-street.json's 25 diaries are authored and stand on the Row and the first two lanes; "
             "the rest are grown. Lengths in millimetres, street frame (x along the harbour, y inland, z up; z 0 the "
             "row, the water at -2.1 m).",
        worldSeed=WORLD,
        provenance="generated-past",
        site=dict(SITE, lanes=[dict(s, x=list(s["x"]) if "x" in s else None, built=list(s["built"]),
                                    start=list(s["start"]) if "start" in s else None) for s in SITE["lanes"]]),
        quay=dict(edge=[v for x in [SITE["quay"]["x0"] + 2.0 * i for i in range(93)] for v in (mm(x), mm(shore_y(x)))],
                  top=0, water=mm(SITE["water"]),
                  row=mm(SITE["quay"]["width"] + SITE["row"]["carriageway"] + SITE["row"]["pavement"])),
        lanes=lanes, stairs=stairs, buildings=buildings, placements=placements, trees=trees,  # points flat: x, y, z, ...
        places=[dict(id="square", name="Torget", z=mm(lines["lane-1"][0][2]),
                     points=[v for x, y in places[1] for v in (mm(x), mm(y))]),
                dict(id="churchyard", name="the church's platform", z=mm(places[2] - 0.3),
                     points=[v for x, y in places[3] for v in (mm(x), mm(y))])],
        ground=grid, coarse=coarse(),
    )
    with open(out, "w") as f:
        json.dump(fixture, f, separators=(",", ":"))
    kinds = {}
    for p in placements:
        kinds[p["kind"]] = kinds.get(p["kind"], 0) + 1
    print(f"[grow_harbour] {kinds}, {len(trees)} trees, {len(lanes)} lanes, {len(stairs)} smau -> "
          f"{os.path.relpath(out, ROOT)} ({os.path.getsize(out) // 1024} KB)")


if __name__ == "__main__":
    main(sys.argv[1:])
