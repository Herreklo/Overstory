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
          (118.0, 38.4), (140.0, 44.0), (175.0, 54.0), (230.0, 75.0), (320.0, 110.0), (600.0, 160.0)],
    tilt=dict(cell=80.0, amp=0.2),                       # the slope's change along the bay: contours drawn in and out
    noise=[(46.0, 2.2), (17.0, 0.6)],                    # (lattice m, amplitude m): the contours' own wander
    gully=dict(x=50.0, width=12.0, depth=4.4, s0=4.0, s1=100.0),
    knoll=dict(x=114.0, s=54.0, rx=40.0, rs=28.0, h=3.0),
    # beyond the quay's ends the hill meets the water as rock: the blend's run along x, the bank's height and reach
    banks=dict(fade=22.0, height=9.0, reach=9.0),
    # the bay opens to the sea at one end (+1 the +x end, the south-west): a low coast of skerries there, hills at the
    # other; skerry is their height per metre of the far land's wander
    mouth=dict(side=1, skerry=0.12),
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
    # the sea side of the quay: sjøhus on its edge in groups, gable to the water, built out on stone; between them
    # open quay with jetties; the steamer pier before the square (x of its middle, length, width)
    sea=dict(x=(-30.0, 147.0), open=[(18.0, 48.0)], run=[(1, 2), (2, 4), (3, 3), (4, 1)], within=(0.0, 0.3),
             gap=(9.0, 22.0), width=[((6.5, 8.5), 2), ((8.5, 11.0), 3)], depth=(11.0, 17.0), built=(1770, 1885),
             pier=dict(x=33.0, length=20.0, width=7.0), jetty=0.75),
    square=dict(lane="lane-1", x=32.0, w=14.0, d=10.0),  # Torget: on Strandgata at Kirkebakken's foot
    church=dict(id=900, x=114.0, s=54.0, built=1854, nave=(19.0, 11.0), tower=5.6),
    forest=dict(above=14.0, cell=5.0),                   # the wild trees: starting above the top lane, on a lattice
    # the spruce plantings on the hill: blocks set out in rows (centre x, s inland, width, depth, turn in degrees)
    plantings=[dict(id="planting-1", x=-48.0, s=196.0, w=86.0, d=62.0, angle=7.0, planted=1957),
               dict(id="planting-2", x=104.0, s=222.0, w=96.0, d=70.0, angle=-5.0, planted=1962),
               dict(id="planting-3", x=188.0, s=170.0, w=52.0, d=58.0, angle=12.0, planted=1949)],
)

GRID = dict(x0=-90.0, y0=-90.0, x1=210.0, y1=330.0, step=1.0)
# a lane's bank: its width per metre it climbs, and the widest it gets
BANK = dict(run=1.6, widest=6.0)
COARSE = dict(x0=-1400.0, y0=-1200.0, x1=1500.0, y1=1800.0, step=25.0)

GRAIN = {  # how a lane's plots are cut, by the age of the lane
    "old": dict(run=[(3, 3), (4, 4), (5, 3), (6, 2), (8, 1)], within=0.2, passage=(0.6, 1.6), yard=(0.15, 0.8), turn=2.5,
                fence=dict(gate=1.9, front=0.0),
                width=[((5.5, 7.5), 1), ((7.5, 10.5), 5), ((10.5, 14.0), 4)], depth=(5.8, 7.8), wing=0.5,
                outhouse=0.45, back=0.4, garden=0.4, fit=dict(depth=5.0, width=5.6, yard=0.1, strip=0.15),
                close=[("plank", 4), ("picket", 2), ("hedge", 2), ("stone", 2), (None, 2)]),
    "mid": dict(run=[(3, 3), (4, 4), (5, 2)], within=0.2, passage=(0.8, 2.0), yard=(0.3, 1.8), turn=1.5,
                fence=dict(gate=1.6, front=1.0),
                width=[((6.5, 8.5), 2), ((8.5, 11.0), 5), ((11.0, 13.0), 2)], depth=(6.4, 8.4), wing=0.4,
                outhouse=0.5, back=0.25, garden=0.7, fit=dict(depth=5.6, width=6.2, yard=0.2, strip=0.3),
                close=[("picket", 4), ("hedge", 4), ("plank", 1), ("stone", 1), (None, 2)]),
    "villa": dict(run=[(1, 1)], within=0.0, passage=(3.0, 7.0), yard=(2.0, 4.5), turn=4.0,
                  fence=dict(gate=0.0, front=1.0),
                  width=[((8.5, 11.0), 1)], depth=(8.0, 10.0), wing=0.15, outhouse=0.4, back=0.0, garden=1.4,
                  close=[("hedge", 6), ("picket", 3), (None, 1)]),
}

# trees: their height at full age, how fast they get there (years), crown radius per metre of height, kind of crown
SPECIES = {
    "sycamore": (20.0, 35.0, 0.36, "round"),
    "birch": (16.0, 20.0, 0.26, "tall"),
    "rowan": (9.0, 15.0, 0.38, "round"),
    "apple": (6.0, 12.0, 0.55, "round"),
    "spruce": (24.0, 40.0, 0.2, "cone"),
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
    # the knoll: a rock rise with a level top, the slope drawn up to it and falling away steeper round its front
    k = SITE["knoll"]
    d2 = ((x - k["x"]) / k["rx"]) ** 2 + ((s - k["s"]) / k["rs"]) ** 2
    w = math.exp(-d2 ** 1.2) * min(1.0, max(0.0, s / 12.0))
    z = z * (1.0 - w) + (rise(k["s"] * tilt(k["x"])) + k["h"]) * w
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


def roof_material(year):
    """The covering a roof laid in this year takes (town.json, roofs)."""
    return next(r["material"] for r in TOWN_PACK["roofs"] if year < r["to"])


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
    # the roof relaid as its covering's life comes round (its own stream, so the rest of the life stays as it was)
    rr = HS.Stream(WORLD, hid, "roof")
    life = ROOF_LIFE[roof_material(built)]
    laid = built + int(rr.uniform(*life))
    while laid < 1989:
        ev.append(dict(id=n, year=laid, kind="roof_retiled", params=dict(),
                       cause="the roof stripped and relaid on new battens, its good tiles cleaned and put back"))
        n += 1
        laid += int(rr.uniform(*life))
    ev.sort(key=lambda e: (e["year"], e["id"]))
    return dict(id=hid, type="house", character=character, events=ev)


def storey_height(storeys, era):
    return {1000: 3.0, 1500: 4.3, 2000: 5.7, 2500: 6.9, 3000: 8.2}[storeys] + (0.2 if era == "chalet" else 0.0)


STOREYS = {"old": [(1000, 2), (1500, 6), (2000, 3)], "mid": [(1500, 4), (2000, 5)],
           "villa": [(1500, 2), (2000, 6), (2500, 1)]}


def placement(pid, kind, of, lane, side, fp, base, eave, pitch, roof):
    (x0, y0), (x1, y1) = fp[0], fp[1]
    return dict(id=pid, kind=kind, of=of, lane=lane, side=side,
                x=mm((x0 + x1) / 2), y=mm((y0 + y1) / 2), angle=round(math.degrees(math.atan2(y1 - y0, x1 - x0)), 2),
                w=mm(math.hypot(x1 - x0, y1 - y0)), d=mm(math.hypot(fp[3][0] - x0, fp[3][1] - y0)),
                base=mm(base), eave=mm(eave), pitch=int(round(pitch)), roof=roof,
                footprint=[v for x, y in fp for v in (mm(x), mm(y))])


PACK = os.path.join(ROOT, "packs", "stavanger-1989")
TIMBER = json.load(open(os.path.join(PACK, "timber.json")))
TOWN_PACK = json.load(open(os.path.join(PACK, "town.json")))
WORKING_OF = TOWN_PACK["workingOf"]
# how many years each roof covering lies before it is relaid (materials/*.json, relaidYears)
ROOF_LIFE = {r["material"]: json.load(open(os.path.join(PACK, "materials", r["material"] + ".json")))["relaidYears"]
             for r in TOWN_PACK["roofs"]}

# how a house grows over its life (a stand-in for the engine's fabric pass): the share of houses of an era that were
# built with the part, the share that had it added later and when. An ark through the long eave of a low house; a porch
# (bislag) at the door where the yard has room for it; a lean-to at the back or a gable end
GROWN = {
    "ark": dict(built={"chalet": 0.5}, later={"classical": 0.3}, years=(1885, 1950)),
    "porch": dict(built={"chalet": 0.6}, later={"classical": 0.35}, years=(1890, 1935), yard=1.9),
    "lean-to": dict(built={}, later={"classical": 0.3, "chalet": 0.25}, years=(1905, 1975)),
}


def working(era):
    w = TIMBER["workings"]
    return w[era] if era in w else w[WORKING_OF[era]]


def bays(length, op):
    """Where a wall's openings sit (their centres), as blender/parts/house/house.py sets them."""
    b0, b1, edge = op["bayMm"][0] / 1000.0, op["bayMm"][1] / 1000.0, op["edgeMm"] / 1000.0
    room = length - 2 * edge
    if room < b0 * 0.75:
        return [length / 2]
    gaps = max(1, math.ceil(room / b1 - 1e-6))
    return [edge + room * i / gaps for i in range(gaps + 1)]


def grow_parts(house, dy, fp, era, yardd, ground, placements, lane, side):
    """What the house grew over its life, each part a placement of its own and, where it came later, an event in its
    diary: an ark, a porch, a lean-to (GROWN). A part is only grown where it fits."""
    hid = house["id"]
    rs = HS.Stream(WORLD, hid, "grown")
    built = next(e for e in dy["events"] if e["kind"] == "built")
    by, storeys = built["year"], built["params"]["storeys"]
    (fx0, fy0), (fx1, fy1) = fp[0], fp[1]
    w = math.hypot(fx1 - fx0, fy1 - fy0)
    ux, uy = (fx1 - fx0) / w, (fy1 - fy0) / w
    nx, ny = -uy, ux
    d = math.hypot(fp[3][0] - fx0, fp[3][1] - fy0)
    base, eave, pitch = house["base"] / 1000.0, house["eave"] / 1000.0, house["pitch"]
    wk = working(era)

    def when(part):
        g = GROWN[part]
        r = rs.random()
        b, later = g["built"].get(era, 0.0), g["later"].get(era, 0.0)
        y = int(rs.uniform(*g["years"]))
        if r < b:
            return by
        if r < b + later and by + 5 < y < WORLD:
            return y
        return None

    def grew(part, year, cause):
        if year == by:
            built["params"].setdefault("parts", []).append(part)
        else:
            dy["events"].append(dict(id=max(e["id"] for e in dy["events"]) + 1, year=year, kind="extended",
                                     params=dict(part=part), cause=cause))

    def part(pid, kind, pfp, b, e, p, roof, year):
        pl = placement(pid, kind, hid, lane, side, pfp, b, e, p, roof)
        pl["year"] = year
        placements.append(pl)

    # an ark: the front wall carried up through the long eave under a gable of its own, the loft made a room
    if house["kind"] == "house" and house["roof"] == "eaves" and storeys in (1500, 2500) and w >= 8.0:
        y = when("ark")
        if y:
            aw = min(4.2, max(2.6, w * rs.uniform(0.3, 0.4)))
            ap = pitch if era == "classical" else rs.uniform(44, 50)
            ridge = eave + d / 2 * math.tan(math.radians(pitch))
            # its ridge a little under the house's
            ae = min(eave + rs.uniform(1.3, 1.8), ridge - 0.25 - aw / 2 * math.tan(math.radians(ap)))
            if ae > eave + 0.9:
                cx, cy = (fx0 + fx1) / 2, (fy0 + fy1) / 2
                part(hid * 100 + 4, "ark", rect(cx, cy, ux, uy, aw, d / 2 + 0.4), eave - 0.5, ae, ap, "gable", y)
                grew("ark", y, "the loft made into rooms")
    # a porch at the door, its gable to the lane, where the yard in front has room
    if house["kind"] == "house" and yardd >= GROWN["porch"]["yard"]:
        y = when("porch")
        if y:
            op = wk["openings"]
            s = w / 2 if op["door"] == "centre" else bays(w, op)[0]
            pw, pd = rs.uniform(2.2, 2.8), min(yardd - 0.5, rs.uniform(1.6, 2.2))
            s = min(max(s, pw / 2 + 0.2), w - pw / 2 - 0.2)
            px, py = fx0 + ux * s - nx * pd, fy0 + uy * s - ny * pd
            pfp = rect(px, py, ux, uy, pw, pd)
            if pd >= 1.2 and ground.free(pfp, 0.05, 0.3, ignore=(fp,)):
                ground.claim(pfp)
                part(hid * 100 + 3, "porch", pfp, base, base + 2.55, rs.uniform(38, 46), "gable", y)
                grew("porch", y, "a porch to keep the weather from the door")
    # a lean-to against the back or a gable end, its roof falling away from the house
    y = when("lean-to")
    if y:
        lw, ld = rs.uniform(2.4, 4.0), rs.uniform(1.8, 2.6)
        (bx1, by1), (bx0, by0) = fp[2], fp[3]
        spots = [((bx0 + bx1) / 2 + ux * e * (w / 2 - lw / 2 - 0.3), (by0 + by1) / 2 + uy * e * (w / 2 - lw / 2 - 0.3), ux, uy)
                 for e in (-1.0, 1.0)]
        spots += [((fx0 + bx0) / 2, (fy0 + by0) / 2, nx, ny), ((fx1 + bx1) / 2, (fy1 + by1) / 2, -nx, -ny)]
        order = sorted(range(len(spots)), key=lambda i: rs.random())
        for i in order:
            cx, cy, lux, luy = spots[i]
            lfp = rect(cx, cy, lux, luy, lw if i < 2 else min(lw, d - 1.0), ld)
            if (i < 2 or d - 1.0 >= 2.2) and ground.free(lfp, 0.3, ignore=(fp,)):
                ground.claim(lfp)
                lb = min(base, natural(cx, cy) + 0.15)
                part(hid * 100 + 5, "lean-to", lfp, lb, lb + 2.3, rs.uniform(14, 22), "shed", y)
                grew("lean-to", y, "more room at the back")
                break
    dy["events"].sort(key=lambda e: (e["year"], e["id"]))


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


BOATS = {  # length, beam (m) and what the boat has on deck
    "faering": ((4.2, 5.4), (1.4, 1.7), "open"),
    "snekke": ((5.8, 8.0), (2.0, 2.5), "open"),
    "sjark": ((9.0, 12.5), (3.0, 3.8), "wheelhouse"),
    "cruiser": ((7.5, 10.0), (2.6, 3.2), "cabin"),
}


def waterfront(buildings, placements, ground):
    """The quay's sea side: the sjøhus in groups along its edge, each built out over the water on stone with its gable
    to the sea; the open stretches between with a jetty for the small boats; the steamer pier before the square. The
    boats are the evening's: moored along the jetties and the open quay, and out on their buoys facing the wind
    (seeded scene, not facts)."""
    sea = SITE["sea"]
    q = SITE["quay"]
    edge = [(x, shore_y(x), 0.0) for x in [q["x0"] + 1.0 * i for i in range(int(q["x1"] - q["x0"]) + 1)]]
    acc = along(edge)
    piers, boats = [], []
    rs = HS.Stream(WORLD, "harbour-sea", "plots")
    t = t_at_x(edge, acc, sea["x"][0])
    t_end = t_at_x(edge, acc, sea["x"][1])
    sid = 700
    open_ = [(t_at_x(edge, acc, a), t_at_x(edge, acc, b)) for a, b in sea["open"]]
    while t < t_end - 6.0:
        n = rs.weighted(sea["run"])
        for _ in range(n):
            w = rs.uniform(*rs.weighted(sea["width"]))
            if t + w > t_end or any(a - 1.0 < t + w and t < b + 1.0 for a, b in open_):
                break
            d = rs.uniform(*sea["depth"])
            (cx, cy, _), (ux, uy) = at(edge, acc, t + w / 2)
            # the front on the quay's edge, facing the Row; the back d out over the water
            fp = rect(cx, cy, -ux, -uy, w, d)
            ground.claim(fp)
            sid += 1
            rh = HS.Stream(WORLD, sid, "diary")
            built = int(rh.uniform(*sea["built"]))
            era = "classical" if built < 1870 else era_for(built, HS.h(WORLD, sid, "era"))
            dy = diary(sid, built, era, rh, "sea", [(2000, 2), (2500, 4), (3000, 2)])
            dy["type"] = "warehouse"
            buildings.append(dy)
            st = dy["events"][0]["params"]["storeys"]
            placements.append(placement(sid, "warehouse", 0, "quay", "sea", fp, 0.3, 0.3 + storey_height(st, era),
                                        rh.uniform(38, 46), "gable"))
            t += w + rs.uniform(*sea["within"])
        g0 = t
        t += rs.uniform(*sea["gap"])
        for a, b in open_:
            if a - 1.0 < t and g0 < b + 1.0:
                t = max(t, b + 1.0)
    # the open stretches: every run of the edge with no sjøhus on it
    stretches = []
    t0 = t_at_x(edge, acc, sea["x"][0])
    taken = []
    for p_ in placements:
        if p_["kind"] == "warehouse" and p_["lane"] == "quay":
            xs = [p_["footprint"][i] / 1000.0 for i in (0, 2)]
            taken.append((t_at_x(edge, acc, min(xs)), t_at_x(edge, acc, max(xs))))
    taken.sort()
    cur = t0
    for a, b in taken:
        if a - cur > 6.0:
            stretches.append((cur, a))
        cur = max(cur, b)
    if t_end - cur > 6.0:
        stretches.append((cur, t_end))
    # the open quay before the square is a stretch of its own
    for oa, ob in open_:
        split = []
        for a, b in stretches:
            for lo, hi in ((a, min(b, oa)), (max(a, oa), min(b, ob)), (max(a, ob), b)):
                if hi - lo > 6.0:
                    split.append((lo, hi))
        stretches = split

    def moor(bid, kind, x, y, heading, rb):
        (l0, l1), (b0, b1), deck = BOATS[kind]
        boats.append(dict(id=bid, kind=kind, deck=deck, x=mm(x), y=mm(y), angle=round(heading, 1),
                          length=mm(rb.uniform(l0, l1)), beam=mm(rb.uniform(b0, b1))))

    pr = sea["pier"]
    (px, py, _), (pux, puy) = at(edge, acc, t_at_x(edge, acc, pr["x"]))
    out = (puy, -pux)
    piers.append(dict(id="pier-steamer", kind="pier", width=mm(pr["width"]), z=mm(-0.05),
                      points=[mm(px - out[0] * 0.5), mm(py - out[1] * 0.5),
                              mm(px + out[0] * pr["length"]), mm(py + out[1] * pr["length"])]))
    bn = 0
    for k, (a, b) in enumerate(stretches):
        rb = HS.Stream(WORLD, "harbour-sea", "stretch", k)
        mid = (a + b) / 2
        (ex, ey, _), (ux, uy) = at(edge, acc, mid)
        ox, oy = uy, -ux                                  # seaward
        steamer = a <= t_at_x(edge, acc, pr["x"]) <= b
        if not steamer and b - a > 9.0 and rb.random() < sea["jetty"]:
            L = rb.uniform(12.0, 24.0)
            piers.append(dict(id=f"jetty-{k + 1}", kind="jetty", width=mm(rb.uniform(1.8, 2.4)), z=mm(SITE["water"] + 0.45),
                              points=[mm(ex), mm(ey), mm(ex + ox * L), mm(ey + oy * L)]))
            # small boats moored along both sides, bow out
            for side in (-1.0, 1.0):
                f = rb.uniform(2.0, 4.0)
                while f < L - 2.0:
                    if rb.random() < 0.7:
                        kind = rb.weighted([("faering", 3), ("snekke", 5), ("cruiser", 2)])
                        bn += 1
                        off = 1.0 + BOATS[kind][1][1] / 2
                        moor(f"boat-{bn}", kind, ex + ox * f + ux * side * off, ey + oy * f + uy * side * off,
                             math.degrees(math.atan2(oy, ox)) + rb.uniform(-4, 4), rb)
                    f += rb.uniform(3.4, 5.5)
        else:
            # alongside the quay's face, bow east or west
            f = a + rb.uniform(1.0, 4.0)
            while f < b - 6.0:
                if rb.random() < (0.85 if steamer else 0.6):
                    kind = rb.weighted([("sjark", 4), ("snekke", 2), ("cruiser", 1)])
                    (bx, by, _), (bux, buy) = at(edge, acc, f + 5.0)
                    if steamer and abs(bx - pr["x"]) < pr["width"] / 2 + 3.0:
                        f += 6.0
                        continue
                    bn += 1
                    off = 1.4 + BOATS[kind][1][1] / 2
                    hd = math.degrees(math.atan2(buy, bux)) + (0.0 if rb.random() < 0.5 else 180.0)
                    moor(f"boat-{bn}", kind, bx + buy * off, by - bux * off, hd + rb.uniform(-2, 2), rb)
                f += rb.uniform(10.0, 15.0)
    # out on their buoys, all swung to the wind from the south-west
    for i in range(16):
        rb = HS.Stream(WORLD, "harbour-sea", "buoy", i)
        x = rb.uniform(q["x0"] + 10.0, q["x1"] - 10.0)
        y = shore_y(x) - rb.uniform(26.0, 80.0)
        if any(math.hypot(x - bb["x"] / 1000.0, y - bb["y"] / 1000.0) < 9.0 for bb in boats):
            continue
        bn += 1
        moor(f"boat-{bn}", rb.weighted([("snekke", 4), ("sjark", 2), ("cruiser", 2), ("faering", 1)]), x, y,
             225.0 + rb.uniform(-9, 9), rb)
    return piers, boats


def chimneys(p):
    """Where a building's chimneys stand on its ridge, from its kind and era (seeded by its id): flat, as along the
    ridge from its middle, off the ridge towards the back, size and rise above the ridge (mm)."""
    rs = HS.Stream(WORLD, p["id"], "chimneys")
    kind = p["kind"]
    ridge = (p["w"] if p["roof"] != "gable" else p["d"]) / 1000.0
    out = []
    if kind in ("house", "church"):
        n = 1 if ridge < 9.0 else rs.weighted([(1, 2), (2, 3)])
        if kind == "church":
            n = 1
        size = rs.uniform(0.55, 0.75) if ridge > 7.0 else rs.uniform(0.45, 0.55)   # a stack of one or two flues
        for k in range(n):
            along_ = 0.0 if n == 1 else (-1 if k == 0 else 1) * ridge * rs.uniform(0.18, 0.3)
            along_ += rs.uniform(-0.12, 0.12) * ridge * (0.5 if n == 1 else 0.2)
            out += [mm(along_), 0, mm(size), mm(rs.uniform(0.7, 1.2))]
    elif kind in ("wing", "outhouse") and rs.random() < (0.45 if kind == "wing" else 0.25):
        out += [mm(rs.uniform(-0.3, 0.3) * ridge), mm(rs.uniform(0.0, 0.8)), mm(rs.uniform(0.4, 0.55)),
                mm(rs.uniform(0.5, 0.8))]
    elif kind == "warehouse" and rs.random() < 0.12:
        out += [mm(rs.uniform(-0.3, 0.3) * ridge), mm(rs.uniform(0.3, 1.5)), mm(0.35), mm(0.9)]
    return out


BACK_OF = {}   # a back house's id: the house whose plot it was built on


def close_plots(placements, buildings, ground, fences):
    """Each house's back plot, closed as its lane's grain closes them: a plank or picket fence, a hedge, a dry-stone
    wall, or left open. The plot runs back from the house to the lane or place behind it, or halfway to the next
    house that is not its own (its wing, outhouse and back house are). A back line across a fall of more than 0.6 m
    is a terrace wall whatever the grain. A hedge left since the house was let go has grown out. Returns the plots,
    with whether each is kept, for the ground's cover."""
    grain_of = {s["id"]: s["grain"] for s in SITE["lanes"]}
    grain_of["harbour-row"] = "old"
    diaries = {b["id"]: b for b in buildings}

    def owner(p):
        o = p["of"] or p["id"]
        return BACK_OF.get(o, o)

    def fp_of(p):
        return [(p["footprint"][i] / 1000.0, p["footprint"][i + 1] / 1000.0) for i in range(0, 8, 2)]

    cell = 12.0
    index = {}
    for p in placements:
        fp = fp_of(p)
        x0, y0, x1, y1 = box(fp)
        for i in range(int(math.floor(x0 / cell)), int(math.floor(x1 / cell)) + 1):
            for j in range(int(math.floor(y0 / cell)), int(math.floor(y1 / cell)) + 1):
                index.setdefault((i, j), []).append((fp, owner(p)))

    def let_go(hid):
        d = diaries.get(hid)
        if not d:
            return False
        last = {}
        for e in d["events"]:
            last[e["kind"]] = e["year"]
        return last.get("neglected", 0) > last.get("restored", 0)

    plots = []
    for p in placements:
        if p["kind"] != "house" or p["side"] == "back" or p["lane"] not in grain_of:
            continue
        hid = p["id"]
        f0, f1, b1, b0 = fp_of(p)
        w = math.hypot(f1[0] - f0[0], f1[1] - f0[1])
        ux, uy = (f1[0] - f0[0]) / w, (f1[1] - f0[1]) / w
        nx, ny = -uy, ux
        mx, my = (b0[0] + b1[0]) / 2, (b0[1] + b1[1]) / 2
        near = [(a, b, hw) for pts, hw in ground.strips for a, b in zip(pts, pts[1:])
                if seg_dist(mx, my, a, b) < 22.0 + hw]
        depth, hit = 16.0, None
        s_ = 0.5
        while s_ <= 16.0 and hit is None:
            for lat in (-(w / 2 - 0.4), 0.0, w / 2 - 0.4):
                qx, qy = mx + nx * s_ + ux * lat, my + ny * s_ + uy * lat
                if any(seg_dist(qx, qy, a, b) < hw + 0.5 for a, b, hw in near) or \
                        any(inside(pl, qx, qy) for pl in ground.places):
                    hit, depth = "way", s_ - 0.4
                    break
                k = (int(math.floor(qx / cell)), int(math.floor(qy / cell)))
                if any(o != hid and inside(fp, qx, qy) for fp, o in index.get(k, ())):
                    hit, depth = "house", s_ / 2
                    break
            s_ += 0.5
        if depth < 1.2:
            continue
        rs = HS.Stream(WORLD, hid, "plot", "close")
        close = GRAIN[grain_of[p["lane"]]]["close"]
        back = rs.weighted(close)
        sides = back if rs.random() < 0.6 else rs.weighted(close)
        # across a fall the back line is a terrace wall
        bx, by = mx + nx * depth, my + ny * depth
        if abs(natural(bx + nx * 0.7, by + ny * 0.7) - natural(bx - nx * 0.7, by - ny * 0.7)) > 0.6:
            back = "stone"
        plots.append(dict(hid=hid, b0=b0, b1=b1, n=(nx, ny), depth=depth, back=back, sides=sides,
                          kept=not let_go(hid), rs=rs, grain=grain_of[p["lane"]]))

    def run(kind, a, b, rs, kept, pid):
        if kind is None:
            return
        rec = dict(id=f"close-{pid}-{len(fences)}", kind=kind, points=[mm(a[0]), mm(a[1]), mm(b[0]), mm(b[1])])
        if kind == "picket":
            rec["height"] = mm(1.0)
        elif kind == "plank":
            rec["height"] = mm(rs.uniform(1.5, 1.9))
        elif kind == "hedge":
            grown = 0.0 if kept else rs.uniform(0.6, 1.0)
            rec["height"] = mm(rs.uniform(1.2, 1.8) + grown)
            rec["width"] = mm(rs.uniform(0.7, 0.9) + grown)
        else:
            rec["height"] = mm(rs.uniform(0.8, 1.1))
            rec["width"] = mm(0.55)
        fences.append(rec)

    # neighbours share a side: the left side is left out where the plot before closes its right
    for q in plots:
        b0 = q["b0"]
        q["left"] = not any(o is not q and math.hypot(o["b1"][0] - b0[0], o["b1"][1] - b0[1]) < 1.2 for o in plots)
        for o in plots:
            if o is not q and math.hypot(o["b1"][0] - b0[0], o["b1"][1] - b0[1]) < 1.2:
                o["right"] = max(o.get("right", o["depth"]), q["depth"])
    yards = []
    for q in plots:
        (nx, ny), d = q["n"], q["depth"]
        b0, b1 = q["b0"], q["b1"]
        e0, e1 = (b0[0] + nx * d, b0[1] + ny * d), (b1[0] + nx * d, b1[1] + ny * d)
        run(q["back"], e0, e1, q["rs"], q["kept"], q["hid"])
        dr = q.get("right", d)
        run(q["sides"] if q["sides"] != "stone" else "plank", b1, (b1[0] + nx * dr, b1[1] + ny * dr), q["rs"], q["kept"],
            q["hid"])
        if q["left"]:
            run(q["sides"] if q["sides"] != "stone" else "plank", b0, e0, q["rs"], q["kept"], q["hid"])
        yards.append(dict(poly=[b0, b1, e1, e0], kept=q["kept"], patch=int(HS.unit(HS.h(WORLD, q["hid"], "plot", "tone")) * 16)))
    return yards


def grow():
    lanes, placements, buildings, stairs = [], [], [], []
    gardens, fences = [], []
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
        lanes.append(dict(id=spec["id"], name=spec["name"], surface=spec["surface"], grain=spec["grain"], laid=spec["laid"],
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
            (px, py, pz), (lux, luy) = at(line, acc, t)
            # level across the lane: the flight starts and ends at its edges
            reach = spec["width"] / 2 / max(abs(lux), 0.3) + 0.3
            pts += [(px, py - reach, pz), (px, py, pz), (px, py + reach, pz)]
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

    piers, boats = waterfront(buildings, placements, ground)

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

        def site_house(t, w, d, yardd, side, turn=0.0):
            """The footprint of a house fronting the lane at arc length t (its front's centre), turned a little off the
            lane as old plots are, or None."""
            (cx, cy, cz), (ux, uy) = at(line, acc, t)
            nx, ny = -uy, ux                                   # left of the lane's run
            if ny < 0:
                nx, ny = -nx, -ny                              # inland
            sgn = 1.0 if side == "up" else -1.0
            off = spec["width"] / 2 + yardd
            fx, fy = cx + nx * off * sgn, cy + ny * off * sgn
            # the front runs so that its left, where rect puts the back, points away from the lane
            ca, sa = math.cos(math.radians(turn)), math.sin(math.radians(turn))
            fux, fuy = ny * sgn, -nx * sgn
            return rect(fx, fy, fux * ca - fuy * sa, fux * sa + fuy * ca, w, d), cz

        def blocked(t, w):
            return any(abs(t - c_) < w / 2 + 2.0 for c_ in crossings.get(lid, []))

        def add_house(hid_, fp, cz, side, built, era, dy, rs_, roof_w, yardd):
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
                    BACK_OF[hid] = hid_
                    placements.append(placement(hid, "house", 0, lid, "back", bfp, bb, bb + storey_height(bst, bera),
                                                rb.uniform(34, 44), "eaves"))
            yard_things(house, fp, spec["grain"], base, built, ground, placements, gardens, rs_, lid, side)
            grow_parts(house, dy, fp, era, yardd, ground, placements, lid, side)

        # lt1-street.json's houses for this lane stand on its uphill side in their authored order, each taking the
        # first plot at or past its authored x
        queue = sorted((b for b in street["buildings"] if spec.get("authored") and
                        b["id"] // 100 == spec["authored"] // 100), key=lambda b: b["plot"]["x"])
        fence = g["fence"]
        for side in ("up", "down"):
            rs = HS.Stream(WORLD, lid, side, "plots")
            t = rs.uniform(1.0, 4.0)
            run = 0
            prev = None                                        # the last house's front corner ahead along the lane
            while t < acc[-1] - 4.0:
                if run == 0:
                    run = rs.weighted(g["run"])
                    run_turn = rs.uniform(-g["turn"], g["turn"])  # a run is built along one line
                w = rs.uniform(*rs.weighted(g["width"]))
                d = rs.uniform(*g["depth"])
                yardd = rs.uniform(*g["yard"])
                turn = run_turn + rs.uniform(-0.4, 0.4)
                (px, _, _), _ = at(line, acc, t + w / 2)
                auth = queue[0] if side == "up" and queue and px >= queue[0]["plot"]["x"] / 1000.0 else None
                if auth:
                    w, d = auth["plot"]["w"] / 1000.0 - 0.3, auth["plot"]["d"] / 1000.0
                # where a plot has less room than the house drawn for it, the house is built to the room: shallower,
                # its front yard narrower, then narrower itself, as old plots were cut (fit); never below fit's least
                sizes = [(w, d, yardd)]
                fit = g.get("fit")
                if fit and not auth:
                    sizes += [(w, max(fit["depth"], d * 0.82), min(yardd, fit["yard"])), (w, fit["depth"], min(yardd, fit["yard"])),
                              (max(fit["width"], w * 0.72), fit["depth"], min(yardd, fit["yard"]))]
                fp = None
                for nudge in (0.0, 0.3, 0.6, 1.0, 1.5) if run > 0 else (0.0,):
                    for w_, d_, y_ in sizes:
                        mid = t + nudge + w_ / 2
                        if blocked(mid, w_):
                            break
                        fp, cz = site_house(mid, w_, d_, y_, side, turn)
                        if ground.free(fp, 0.12 if g["within"] else 0.6, fit["strip"] if fit else 0.5, strip_n):
                            t += nudge
                            w, d, yardd = w_, d_, y_
                            break
                        fp = None
                    if fp is not None or blocked(t + nudge + w / 2, w):
                        break
                if fp is None:
                    run = 0
                    prev = None
                    t += 1.5
                    continue
                # the fences: a plank fence and gate across the passage from the last house, and a front fence along
                # the lane before a front garden
                _, (tux, tuy) = at(line, acc, mid)
                behind, ahead = sorted(fp[:2], key=lambda q: q[0] * tux + q[1] * tuy)
                fid = f"fence-{lid}-{side}-{len(fences)}"
                if fence["gate"] and prev and 0.6 < math.hypot(behind[0] - prev[0], behind[1] - prev[1]) < 4.5:
                    fences.append(dict(id=fid, kind="plank", height=mm(fence["gate"]),
                                       points=[mm(prev[0]), mm(prev[1]), mm(behind[0]), mm(behind[1])]))
                if fence["front"] and yardd > fence["front"]:
                    bx_, by_ = fp[3][0] - fp[0][0], fp[3][1] - fp[0][1]
                    bl = math.hypot(bx_, by_)
                    bx_, by_ = bx_ / bl * (yardd - 0.3), by_ / bl * (yardd - 0.3)
                    ex_, ey_ = ahead[0] - behind[0], ahead[1] - behind[1]
                    el = math.hypot(ex_, ey_)
                    ex_, ey_ = ex_ / el, ey_ / el
                    a_ = (behind[0] - bx_ - ex_ * 0.9, behind[1] - by_ - ey_ * 0.9)
                    b_ = (ahead[0] - bx_ + ex_ * 0.9, ahead[1] - by_ + ey_ * 0.9)
                    gm = rs.uniform(0.3, 0.7)
                    g0 = (a_[0] + (b_[0] - a_[0]) * gm, a_[1] + (b_[1] - a_[1]) * gm)
                    for q0, q1 in ((a_, (g0[0] - ex_ * 0.6, g0[1] - ey_ * 0.6)), ((g0[0] + ex_ * 0.6, g0[1] + ey_ * 0.6), b_)):
                        fences.append(dict(id=f"{fid}-{len(fences)}", kind="picket", height=mm(1.0),
                                           points=[mm(q0[0]), mm(q0[1]), mm(q1[0]), mm(q1[1])]))
                prev = ahead
                if auth:
                    queue.pop(0)
                    rh = HS.Stream(WORLD, auth["id"], "harbour", "plot")
                    built = next(e for e in auth["events"] if e["kind"] == "built")
                    add_house(auth["id"], fp, cz, side, built["year"], built["params"]["era"], auth, rh, 0.45, yardd)
                else:
                    hid += 1
                    rh = HS.Stream(WORLD, hid, "diary")
                    built = int(rh.uniform(b0, b1))
                    era = era_for(built, HS.h(WORLD, hid, "era"))
                    dy = diary(hid, built, era, rh, spec["grain"], STOREYS[spec["grain"]])
                    add_house(hid, fp, cz, side, built, era, dy, rh, 0.55 if spec["grain"] == "villa" else 0.45, yardd)
                run -= 1
                t += w + (g["within"] if run > 0 else rs.uniform(*g["passage"]))
    yards = close_plots(placements, buildings, ground, fences)
    for p in placements:
        p["chimneys"] = chimneys(p)
    return lanes, stairs, buildings, placements, lines, gardens, ground, (yard, square, cbase, platform), piers, boats, \
        fences, yards


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
                u = -pl["w"] / 2 + (iu + 0.5 + rs.uniform(-0.3, 0.3)) * row
                v = -pl["d"] / 2 + (iv + 0.5 + rs.uniform(-0.3, 0.3)) * row
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
            # wild trees come up in clumps with open ground between, never evenly: a seed tree and its seedlings
            clump = 1.8 if noise(x, y, [(15.0, 1.0), (6.0, 0.5)]) > 0.2 else 0.25
            if any(in_planting(pl, x, y) for pl in SITE["plantings"]):
                continue                                         # planted in its own rows, above
            if above > 0:
                # the heath, grazed until the 1950s: birch coming up in groves along the town's edge and the hollows,
                # a few pines and rowans out on it
                grove = patch > 0.15 and above < 70
                p = (0.5 * clump if grove else 0.006) - (0.15 if above < 10 else 0.0)
                pool = [("birch", 6), ("rowan", 1)] if grove else [("pine", 3), ("birch", 2), ("rowan", 1)]
                age = rs.uniform(15, 40) if grove else rs.uniform(20, 90)
                cause = "birch coming up as grazing stopped" if grove else "self-seeded on the heath"
            elif e > 0.2:
                p = (0.22 * e + 0.15 * patch) * clump
                pool = [("pine", 4), ("birch", 3), ("rowan", 1)]
                age = rs.uniform(15, 90)
                cause = "self-seeded on the rock"
            else:
                p = (0.10 + 0.08 * patch) * clump
                pool = [("birch", 4), ("rowan", 2), ("sycamore", 2)]
                age = rs.uniform(10, 60)
                cause = "self-seeded on the slope"
            if rs.random() >= p:
                continue
            if not ground.clear_point(x, y, 2.2):
                continue
            trees.append(tree(f"tree-w{i}-{j}", rs.weighted(pool), x, y, int(WORLD - age), cause))
    return trees


def stands():
    """The spruce plantings as stands: each block's corners and its trees' mean height in 1989, for the closed canopy
    the rows make once they have grown together."""
    out = []
    hmax, k, _, _ = SPECIES["spruce"]
    for pl in SITE["plantings"]:
        a = math.radians(pl["angle"])
        pts = []
        for u, v in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
            u_, v_ = u * pl["w"] / 2, v * pl["d"] / 2
            x = pl["x"] + u_ * math.cos(a) - v_ * math.sin(a)
            s_ = pl["s"] + u_ * math.sin(a) + v_ * math.cos(a)
            pts += [mm(x), mm(building_line(x) + s_)]
        out.append(dict(id=pl["id"], planted=pl["planted"], h=mm(hmax * (1.0 - math.exp(-(WORLD - pl["planted"]) / k))),
                        points=pts))
    return out


def walls(poly, level, parapet, step=2.0):
    """A retaining wall round a level place, a little outside its edge: at each point its foot and its top, holding
    the slope back where the place is cut in and standing a parapet above it where the place is built up (mm, flat:
    x, y, foot, top)."""
    pts = []
    cx = sum(p[0] for p in poly) / len(poly)
    cy = sum(p[1] for p in poly) / len(poly)
    for i in range(len(poly)):
        a, b = poly[i], poly[(i + 1) % len(poly)]
        L = math.hypot(b[0] - a[0], b[1] - a[1])
        n = max(1, int(round(L / step)))
        for k in range(n):
            u = k / n
            x, y = a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u
            ox, oy = x - cx, y - cy
            o = math.hypot(ox, oy) or 1.0
            x, y = x + ox / o * 0.3, y + oy / o * 0.3
            outside = natural(x + ox / o * 1.4, y + oy / o * 1.4)
            foot = min(level, outside) - 0.3
            top = max(level + parapet, outside + 0.25)
            pts += [mm(x), mm(y), mm(foot), mm(top)]
    return pts


# -- the ground, carved where the town stands ----------------------------------------------------------------------------

COVER = ["grass", "garden", "heath", "rock", "forest floor", "made", "litter"]
SHEDS = {"birch", "rowan", "sycamore", "apple"}   # the trees that drop their leaves in October
LITTER = 0.9                                         # how far out under its crown a tree's fallen leaves lie


def cover(Z, kind, gardens, top_line, yards=(), trees=()):
    """What covers the ground at each point, for its tone (index in COVER) and a patch value 0-15 from the land's
    own lattice: made ground; the rock of the banks and of slopes too steep to hold soil; the spruce stands' needles;
    October's fallen leaves under the crowns of the trees that shed them; the heath above the top lane; the gardens
    behind the houses; grass on the rest of the town's slopes."""
    g = GRID
    ny, nx = len(Z), len(Z[0])
    tacc = along(top_line)
    top_y = []
    for i in range(nx):
        x = g["x0"] + i * g["step"]
        tt = t_at_x(top_line, tacc, x)
        top_y.append(at(top_line, tacc, tt)[0][1] if tt is not None else building_line(x) + 150.0)
    garden = set()
    for gd in gardens:
        ci, cj = int(round((gd["x"] - g["x0"]) / g["step"])), int(round((gd["y"] - g["y0"]) / g["step"]))
        for dj in range(-4, 5):
            for di in range(-4, 5):
                if di * di + dj * dj <= 16:
                    garden.add((ci + di, cj + dj))
    plot = {}
    for yd in yards:
        x0, y0, x1, y1 = box(yd["poly"])
        for j in range(max(0, int(math.floor((y0 - g["y0"]) / g["step"]))), min(ny, int(math.ceil((y1 - g["y0"]) / g["step"])) + 1)):
            for i in range(max(0, int(math.floor((x0 - g["x0"]) / g["step"]))), min(nx, int(math.ceil((x1 - g["x0"]) / g["step"])) + 1)):
                if inside(yd["poly"], g["x0"] + i * g["step"], g["y0"] + j * g["step"]):
                    plot[(i, j)] = yd
    litter = set()
    for tr in trees:
        if tr["species"] not in SHEDS:
            continue
        rr = tr["r"] / 1000.0 * LITTER
        ci, cj = int(round((tr["x"] / 1000.0 - g["x0"]) / g["step"])), int(round((tr["y"] / 1000.0 - g["y0"]) / g["step"]))
        n = int(rr / g["step"]) + 1
        for dj in range(-n, n + 1):
            for di in range(-n, n + 1):
                if (di * di + dj * dj) * g["step"] ** 2 <= rr * rr:
                    litter.add((ci + di, cj + dj))
    out = []
    for j in range(ny):
        y = g["y0"] + j * g["step"]
        for i in range(nx):
            x = g["x0"] + i * g["step"]
            k = kind[j][i]
            zc = Z[j][i]
            slope = max(abs(Z[j][min(nx - 1, i + 1)] - Z[j][max(0, i - 1)]), abs(Z[min(ny - 1, j + 1)][i] - Z[max(0, j - 1)][i])) / 2
            if k not in (0, 3):
                c = 5
            elif y < shore_y(x) or bank_weight(x) > 0.25 or slope > 0.95:
                c = 3
            elif any(in_planting(pl, x, y) for pl in SITE["plantings"]):
                c = 4
            elif (i, j) in litter:
                c = 6
            elif (i, j) in plot:
                yd = plot[(i, j)]
                out.append((1 if yd["kept"] else 2) * 16 + yd["patch"])
                continue
            elif y > top_y[i] + 6.0:
                c = 2
            elif (i, j) in garden:
                c = 1
            else:
                c = 0
            patch = noise(x, y, [(23.0, 0.7), (7.0, 0.3)])
            out.append(c * 16 + max(0, min(15, int((patch + 1.0) * 7.5))))
    return out


def carve(lines, placements, places, gardens, top_line, yards=(), stairs=(), trees=()):
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

    def bench(pts, hw, shoulder, mark, keep=()):
        """A level strip along pts (x, y, z): within hw level at the nearest point's z, easing back over a bank as
        wide as the height it climbs needs (no steeper than about one in one, so the grid draws it smooth).
        Each cell takes the nearest segment only, so overlapping segments never ripple the shoulder."""
        best = {}
        for a, b in zip(pts, pts[1:]):
            r = hw + BANK["widest"] + 1
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
                    if d <= hw + BANK["widest"] and ((i, j) not in best or d < best[(i, j)][0]):
                        best[(i, j)] = (d, zl)
        for (i, j), (d, zl) in best.items():
            if kind[j][i] in keep:
                continue
            if d <= hw:
                Z[j][i] = zl
                kind[j][i] = mark
            elif kind[j][i] in (0, 3):
                wide = min(BANK["widest"], max(shoulder, BANK["run"] * abs(Z[j][i] - zl)))
                if d - hw < wide:
                    v = (d - hw) / wide
                    Z[j][i] = zl + (Z[j][i] - zl) * v * v * (3 - 2 * v)

    for k, spec in enumerate(SITE["lanes"]):
        line = lines[spec["id"]]
        if line:
            bench(line, spec["width"] / 2, 1.5, 2)
    # the smau: the ground follows each flight between the lanes it joins, the lanes left level
    for st in stairs:
        p = st["points"]
        bench([(p[i] / 1000.0, p[i + 1] / 1000.0, p[i + 2] / 1000.0) for i in range(0, len(p), 3)],
              st["width"] / 2000.0 + 0.3, 1.0, 4, keep=(1, 2))
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
                elif dd < 1.2 and kind[j][i] == 0:
                    v = dd / 1.2
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
                z=[mm(v) for row in Z for v in row], kind=[v for row in kind for v in row],
                cover=cover(Z, kind, gardens, top_line, yards, trees))


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
            seaward = y - shore_y(max(-200.0, min(320.0, x))) <= 0
            if seaward and (x - 58) * SITE["mouth"]["side"] > 260:
                # the bay's mouth: the low coast's skerries, awash or a few metres up
                z = max(z, SITE["water"] + SITE["mouth"]["skerry"] * far)
            elif not seaward or abs(x - 58) > 260:
                z = max(z, 18.0 + far + 0.12 * max(0.0, abs(x - 58) - 140)) if abs(x - 58) > 140 else z
            row.append(mm(z))
        Z.append(row)
    return dict(x0=mm(c["x0"]), y0=mm(c["y0"]), step=mm(c["step"]), nx=nx, ny=ny, z=[v for row in Z for v in row])


def main(argv):
    out = os.path.join(ROOT, "fixtures", "lt1-harbour-town.json")
    if "--out" in argv:
        out = argv[argv.index("--out") + 1]
    lanes, stairs, buildings, placements, lines, gardens, ground, places, piers, boats, fences, yards = grow()
    top = max(SITE["lanes"], key=lambda s: s.get("z", 0.0))["id"]
    trees = plant(gardens, ground, places, lines[top])
    grid = carve(lines, placements, places, gardens, lines[top], yards, stairs, trees)
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
        piers=piers, boats=boats, stands=stands(), fences=fences,
        walls=[dict(id="churchyard-wall", points=walls(places[3], places[2] - 0.3, 0.9)),
               dict(id="square-wall", points=walls(places[1], lines["lane-1"][0][2], 0.0))],
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
    print(f"[grow_harbour] {kinds}, {len(trees)} trees, {len(lanes)} lanes, {len(stairs)} smau, "
          f"{len(piers)} piers, {len(boats)} boats, {len(fences)} fences -> "
          f"{os.path.relpath(out, ROOT)} ({os.path.getsize(out) // 1024} KB)")


if __name__ == "__main__":
    main(sys.argv[1:])
