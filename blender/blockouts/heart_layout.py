"""The heart of the town laid out in clay: what stands where, and the ground cut to take it.

Pure Python with numpy, no bpy, so the layout can be checked and drawn outside Blender; heart_build.py
turns it into meshes in Blender and exports them to Unity.

The heart is the Basin and its two shores, the Holm and the Cut, Watch Knoll, Market Square and the
cathedral, and Herring Hill's west slope round the beauty corner (docs/town-plan.md, The centre in detail).
Laid out by hand: every lane, stair, quay, square, landmark, the corner's houses and the Holm's warehouses.
The terraces follow the land's own contours (traced from centre_land), and the old town's rows take their
plot sizes from Stavanger's measured grain (docs/research/stavanger-centre.md), seeded, with every plot
checked against its neighbours, the lanes and the stairs.

Street coordinates in metres: x towards the Basin's head (about south), y up Herring Hill (about east), z up.
"""

import math
import random

import numpy as np

import centre_land as L

SEED = 1989
SEA = -0.2            # the water's surface; quays stand about two metres over it
HEART = (-390.0, -480.0, 540.0, 330.0)  # x0, y0, x1, y1 of the fine ground


# -- tracing the land's contours, so terraces bend with the hill ---------------------------------------------------

def contour_y(z, xs, y_from, y_to):
    """For each x, the first y between y_from and y_to (going uphill) where the natural ground reaches z."""
    ys = np.arange(y_from, y_to, 0.5)
    X, Y = np.meshgrid(np.asarray(xs, float), ys, indexing="ij")
    Z = L.heights(X, Y)
    out = []
    for i, x in enumerate(xs):
        k = np.argmax(Z[i] >= z)
        out.append(float(ys[k]) if Z[i, k] >= z else None)
    return out


def smooth(vals, n=3):
    v = [x for x in vals]
    for _ in range(n):
        v = [v[0]] + [(v[i - 1] + 2 * v[i] + v[i + 1]) / 4 for i in range(1, len(v) - 1)] + [v[-1]]
    return v


def terrace(z, x0, x1, y_from=0.0, y_to=220.0, step=6.0):
    xs = list(np.arange(x0, x1 + 0.01, step))
    ys = contour_y(z, xs, y_from, y_to)
    pts = [(x, y) for x, y in zip(xs, ys) if y is not None]
    yy = smooth([p[1] for p in pts])
    return [(p[0], y, z) for p, y in zip(pts, yy)]


# -- lanes, stairs, quays: (name, width, points (x, y, z)) -----------------------------------------------------------

LOW = terrace(3.0, -232, 276, 4.0)
HIGH = terrace(8.0, -226, 296, 12.0)
TOP = terrace(16.0, -214, 300, 30.0)
CREST = terrace(28.0, -196, 262, 60.0)


def lane_y(lane, x):
    for (x1, y1, _), (x2, y2, _) in zip(lane, lane[1:]):
        if x1 <= x <= x2:
            return y1 + (y2 - y1) * (x - x1) / (x2 - x1)
    return None


# The Landing sits on High Terrace at the corner; Gully Steps cross every terrace in the stream's gully.
LANDING_Z = 8.0
_yl, _yh, _yt = lane_y(LOW, 49.0), lane_y(HIGH, 47.0), lane_y(TOP, 47.0)
LANDING = [(42.0, _yh - 6.0), (52.0, _yh - 6.0), (52.0, _yh + 6.5), (42.0, _yh + 6.5)]
GULLY_STEPS = [(49.3, 0.0, 2.1), (49.3, 9.0, 2.4), (49.3, _yl - 1.6, 3.0), (49.1, _yl + 1.6, 3.0),
               (48.0, _yh - 6.0, 8.0), (46.5, _yh + 6.5, 8.0), (46.5, _yt - 1.4, 16.0), (46.5, _yt + 1.4, 16.0)]
# beyond Top Terrace a path goes round E and on up through the Heights to Lookout Park
LOOKOUT_PATH = [(58.0, _yt + 1.0, 16.0), (60.0, _yt + 22.0, 21.0), (50.0, lane_y(CREST, 50.0) - 2.0, 28.0),
                (40.0, 170.0, 35.0), (12.0, 226.0, 45.6)]
_y2l, _y2h, _y2t, _y2c = lane_y(LOW, -110), lane_y(HIGH, -110), lane_y(TOP, -110), lane_y(CREST, -110)
TANNERS_STEPS = [(-110.0, 0.0, 1.9), (-110.0, _y2l - 1.6, 3.0), (-110.0, _y2l + 1.6, 3.0), (-110.0, _y2h - 1.6, 8.0),
                 (-110.0, _y2h + 1.6, 8.0), (-110.0, _y2t - 1.6, 16.0), (-110.0, _y2t + 1.6, 16.0), (-108.0, _y2c, 28.0)]
_y3h, _y3t, _y3c = lane_y(HIGH, 196), lane_y(TOP, 196), lane_y(CREST, 196)
BISHOPS_STEPS = [(196.0, -2.0, 2.0), (196.0, lane_y(LOW, 196) - 1.6, 3.0), (196.0, lane_y(LOW, 196) + 1.6, 3.0),
                 (196.0, _y3h - 1.6, 8.0), (196.0, _y3h + 1.6, 8.0), (196.0, _y3t - 1.6, 16.0),
                 (196.0, _y3t + 1.6, 16.0), (200.0, _y3c, 28.0)]
HUNDRED_STEPS = [(-248.0, -1.0, 2.0), (-262.0, 22.0, 9.0), (-252.0, 36.0, 9.0), (-268.0, 58.0, 18.0),
                 (-256.0, 72.0, 18.0), (-262.0, 96.0, 26.0), (-236.0, 100.0, 26.0), (-206.0, 100.0, float(L.z_at(-206.0, 100.0)))]

# Harbour Row's building line, 15.4 m in from the quay's edge, with the quay's kink
HR_LINE = [(-250.0, 0.0), (-160.0, 0.0), (-60.0, 3.0), (150.0, 0.4), (250.0, -6.6), (300.0, -16.6), (334.0, -34.6)]


def hr_line(x):
    """The building line's y at x, and its direction in degrees."""
    for (x1, y1), (x2, y2) in zip(HR_LINE, HR_LINE[1:]):
        if x1 <= x <= x2:
            return y1 + (y2 - y1) * (x - x1) / (x2 - x1), math.degrees(math.atan2(y2 - y1, x2 - x1))
    return HR_LINE[-1][1], 0.0


HARBOUR_ROW = [(-250.0, -7.7, 1.9), (-160.0, -7.7, 1.9), (-60.0, -4.7, 1.9), (150.0, -7.3, 1.9), (250.0, -15.0, 2.0), (300.0, -25.0, 2.1), (330.0, -40.0, 2.2), (344.0, -48.0, 2.4)]

# The west shore: Barrel Quay on the Holm and the mainland, Holm Street above it, the Cut's two bridges
BARREL_QUAY = [(-196.0, -168.0, 1.9), (0.0, -162.0, 1.9), (38.0, -157.0, 1.9)]
BARREL_QUAY_SOUTH = [(56.0, -157.0, 1.9), (150.0, -147.0, 2.0), (240.0, -137.0, 2.1), (300.0, -131.0, 2.2), (334.0, -126.0, 2.4), (342.0, -129.0, 2.5)]
HOLM_STREET = [(-214.0, -224.0, 7.0), (-120.0, -224.0, 8.0), (0.0, -222.0, 8.0), (60.0, -218.0, 8.0),
               (150.0, -204.0, 8.0), (236.0, -190.0, 6.4), (300.0, -170.0, 4.0), (346.0, -150.0, 2.6), (343.0, -130.0, 2.5)]
CUT_BRIDGE_HIGH = [(30.0, -221.0, 8.0), (64.0, -219.0, 8.0)]   # Holm Street's stone bridge, six metres over the Cut
CUT_BRIDGE_LOW = [(30.0, -158.0, 2.2), (64.0, -156.0, 2.2)]    # the quay's footbridge, at the water
STAIR_LANES = []  # from Barrel Quay up to Holm Street, between the warehouses (filled in with the Holm below)

# Broad Street: the fire-break street, thirty metres wide, straight down from the Grid to the Basin
BROAD_STREET = [(250.0, -470.0, 21.0), (250.0, -300.0, 12.0), (250.0, -190.0, 6.4), (250.0, -138.0, 2.1)]


def _on_ground(pts, z0=None, step=6.0):
    """A way laid on the land as it lies: points every few metres, each at the ground's height; z0 pins its start
    to the street it leaves."""
    out = []
    for (xa, ya), (xb, yb) in zip(pts, pts[1:]):
        n = max(1, int(math.hypot(xb - xa, yb - ya) / step))
        out += [(xa + (xb - xa) * i / n, ya + (yb - ya) * i / n) for i in range(n)]
    out.append(pts[-1])
    pts3 = [(x, y, float(L.z_at(x, y))) for x, y in out]
    if z0 is not None:
        pts3[0] = (pts3[0][0], pts3[0][1], z0)
    return pts3


# Watch Knoll (centre_land.KNOLL): the Fire Watch on its crown, in a small walled yard; the Crack, steps up through
# a cleft in the rock from Holm Street; the path up its gentle south side from Broad Street, through the park
WATCH_YARD = [(127.0, -331.0), (153.0, -331.0), (153.0, -305.0), (127.0, -305.0)]
WATCH_Z = 43.4
CRACK_STEPS = _on_ground([(134.0, -209.0), (135.0, -226.0), (136.0, -246.0), (138.0, -266.0), (139.0, -286.0), (140.0, -303.0)], z0=8.0, step=4.0)
CRACK_STEPS[-1] = (140.0, -303.0, WATCH_Z)
KNOLL_PATH = _on_ground([(236.0, -345.0), (212.0, -366.0), (182.0, -386.0), (152.0, -392.0), (126.0, -380.0),
                         (114.0, -358.0), (120.0, -338.0), (134.0, -329.0)], z0=14.4)
KNOLL_PATH[-1] = (134.0, -329.0, WATCH_Z)

MARKET_SQUARE = [(338.0, -132.0), (432.0, -158.0), (446.0, -34.0), (338.0, -40.0)]
MARKET_Z = 2.5

def _gl(pts, step=10.0):
    """A way laid on the ground as it lies: the points, filled in every ten metres, with the ground's height."""
    out = []
    for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
        n = max(1, int(math.hypot(x2 - x1, y2 - y1) / step))
        for i in range(n):
            x, y = x1 + (x2 - x1) * i / n, y1 + (y2 - y1) * i / n
            out.append((x, y, float(L.z_at(x, y))))
    out.append((pts[-1][0], pts[-1][1], float(L.z_at(*pts[-1]))))
    return out


# The Grid's streets: twelve metres between its blocks, straight over the slope
GRID_X = [(267.0, 323.0), (335.0, 391.0), (403.0, 459.0), (471.0, 527.0)]
GRID_Y = [(-252.0, -292.0), (-304.0, -344.0), (-356.0, -396.0), (-408.0, -448.0)]
GRID_STREETS = [dict(name=f"the Grid's street at x {x:.0f}", width=10.4, kind="lane", pts=_gl([(x, -246.0), (x, -454.0)]))
                for x in (329.0, 397.0, 465.0, 533.0)]
GRID_STREETS += [dict(name=f"the Grid's street at y {y:.0f}", width=10.4, kind="lane", pts=_gl([(262.0, y), (539.0, y)]))
                 for y in (-246.0, -298.0, -350.0, -402.0, -454.0)]
# Bluff Road: up Herring Hill's north end, gathering the terraces' north ends, to the Heights
BLUFF_ROAD = dict(name="Bluff Road", width=4.0, kind="lane", pts=_gl([(-250.0, -6.0), (-234.0, 6.0), (-232.0, 6.0), (-226.0, 30.0),
                                                                    (-214.0, 68.0), (-196.0, 125.0)], 6.0))
# Bishop's Hill: up its south end from Harbour Row's end, gathering the terraces' south ends
BISHOPS_HILL = dict(name="Bishop's Hill", width=4.6, kind="lane", pts=_gl([(338.0, -36.0), (276.0, 4.0), (296.0, 24.0), (300.0, 60.0),
                                                                          (296.0, 122.0), (260.0, 170.0)], 6.0))
# School Lane: past the cathedral school to the square's east side; Bishop's Gate up to the bishop's house
SCHOOL_LANE = dict(name="School Lane", width=5.0, kind="lane", pts=_gl([(300.0, 31.0), (380.0, 31.0), (429.0, 27.0), (429.0, -36.0)], 6.0))
BISHOPS_GATE = dict(name="Bishop's Gate", width=3.0, kind="lane", door=True, pts=_gl([(381.0, 31.0), (381.0, 77.0)], 6.0))
# round the Holm's tip, from Barrel Quay up to Holm Street; the breakwater out from it
TIP_LANE = dict(name="Customs Lane", width=3.6, kind="lane", pts=[(-196.0, -168.0, 1.9), (-208.0, -178.0, 3.0),
                                                                    (-216.0, -200.0, 5.0), (-214.0, -224.0, 7.0)])
BREAKWATER_WAY = dict(name="the breakwater", width=5.0, kind="mole", pts=[(-206.0, -186.0, 2.5), (-270.0, -160.0, 2.5), (-312.0, -112.0, 2.5)])
# the Cut's footbridge at the quay
CUT_FOOTBRIDGE = dict(name="the Cut's footbridge", width=3.0, kind="bridge", pts=[(30.0, -158.0, 2.2), (64.0, -156.0, 2.2)])
# Lookout Park: a level place on Herring Hill's top
LOOKOUT_PARK = [(-8.0, 212.0), (32.0, 212.0), (32.0, 250.0), (-8.0, 250.0)]


def _on(lane, x, z):
    return (x, lane_y(lane, x), z)


RAMPS = [  # diagonal lanes between the terraces, so the hill is a net and not a comb
    dict(name="Cooper's Rise", width=3.0, pts=[_on(LOW, -40.0, 3.0), _on(HIGH, 12.0, 8.0)], kind="lane"),
    dict(name="Sailmaker's Rise", width=3.0, pts=[_on(HIGH, 118.0, 8.0), _on(TOP, 168.0, 16.0)], kind="lane"),
    dict(name="Rope Lane", width=2.8, pts=[_on(TOP, -110.0, 16.0), (-70.0, lane_y(TOP, -70.0) + 18.0, 20.0),
                                           _on(CREST, -24.0, 28.0)], kind="lane"),
]
PASSAGES = []  # short stepped passages between houses, from one terrace to the next
for _x, _a, _b, _za, _zb in [(-172.0, LOW, HIGH, 3.0, 8.0), (92.0, LOW, HIGH, 3.0, 8.0), (152.0, LOW, HIGH, 3.0, 8.0),
                             (-62.0, HIGH, TOP, 8.0, 16.0), (8.0, HIGH, TOP, 8.0, 16.0), (232.0, HIGH, TOP, 8.0, 16.0),
                             (-150.0, TOP, CREST, 16.0, 28.0), (110.0, TOP, CREST, 16.0, 28.0)]:
    PASSAGES.append(dict(name=f"passage at {_x:.0f}", width=1.6, kind="steps",
                         pts=[(_x, lane_y(_a, _x) + 1.6, _za), (_x + 2.0, lane_y(_b, _x + 2.0) - 1.6, _zb)]))


def _place(lane, x, w, d, z):
    y = lane_y(lane, x)
    return [(x - w / 2, y - d / 2), (x + w / 2, y - d / 2), (x + w / 2, y + d / 2), (x - w / 2, y + d / 2)], z


SMALL_PLACES = [  # widenings where lanes meet: a well, a bench, a lantern
    ("Lookout Park", LOOKOUT_PARK, 45.6),
    ("the Well", *_place(HIGH, 12.0, 14.0, 11.0, 8.0)),
    ("Coopers' Corner", *_place(LOW, -40.0, 12.0, 10.0, 3.0)),
    ("Ropewalk Head", *_place(TOP, -110.0, 12.0, 10.0, 16.0)),
    ("the Watch's yard", WATCH_YARD, WATCH_Z),
]

LANES = [
    dict(name="Harbour Row", width=15.0, pts=HARBOUR_ROW, kind="quay"),
    dict(name="Low Terrace", width=3.6, pts=LOW, kind="lane"),
    dict(name="High Terrace", width=3.4, pts=HIGH, kind="lane"),
    dict(name="Top Terrace", width=3.2, pts=TOP, kind="lane"),
    dict(name="Crest Lane", width=4.2, pts=CREST, kind="lane"),
    dict(name="Gully Steps", width=3.2, pts=GULLY_STEPS, kind="steps"),
    dict(name="the path to Lookout Park", width=2.0, pts=LOOKOUT_PATH, kind="steps"),
    dict(name="Tanner's Steps", width=2.6, pts=TANNERS_STEPS, kind="steps"),
    dict(name="Bishop's Steps", width=3.0, pts=BISHOPS_STEPS, kind="steps"),
    dict(name="the Hundred Steps", width=2.2, pts=HUNDRED_STEPS, kind="steps"),
    dict(name="Barrel Quay", width=12.0, pts=BARREL_QUAY, kind="quay"),
    dict(name="Barrel Quay south", width=12.0, pts=BARREL_QUAY_SOUTH, kind="quay"),
    dict(name="Holm Street", width=6.0, pts=HOLM_STREET, kind="lane"),
    dict(name="Broad Street", width=30.0, pts=BROAD_STREET, kind="lane"),
    dict(name="the Crack", width=2.4, pts=CRACK_STEPS, kind="steps"),
    dict(name="the knoll path", width=2.4, pts=KNOLL_PATH, kind="lane"),
    # the 1960s road from Harbour Row's end into the tunnel under the Bluff, in its rock cutting
    dict(name="the way to the tunnel's portal", width=7.0, kind="road", door=True,
         pts=[(-250.0, -6.0, 1.9), (-262.0, 3.0, 1.9)]),
] + RAMPS + PASSAGES + GRID_STREETS + [BLUFF_ROAD, BISHOPS_HILL, SCHOOL_LANE, BISHOPS_GATE, TIP_LANE,
                           BREAKWATER_WAY, CUT_FOOTBRIDGE]


# -- buildings: oriented boxes with a roof ---------------------------------------------------------------------------
# A building: origin at its front-left corner on the ground; local x along the front, local y back from it.
# roof: "eaves" (ridge along the front), "gable" (ridge front to back), "hip", "mansard", "flat", "tower",
# "cathedral". role: corner, row, landmark, warehouse, context.

BUILDINGS = []


def building(name, ox, oy, angle, w, d, base, eave, pitch=44.0, roof="eaves", role="row", low=None):
    BUILDINGS.append(dict(name=name, ox=ox, oy=oy, angle=angle, w=w, d=d, base=base, eave=eave, pitch=pitch,
                          roof=roof, role=role, low=low))


def footprint(b, grow=0.0):
    c, s = math.cos(math.radians(b["angle"])), math.sin(math.radians(b["angle"]))
    to = lambda x, y: (b["ox"] + x * c - y * s, b["oy"] + x * s + y * c)
    return [to(-grow, -grow), to(b["w"] + grow, -grow), to(b["w"] + grow, b["d"] + grow), to(-grow, b["d"] + grow)]


def _sat_overlap(a, b):
    for poly in (a, b):
        for i in range(4):
            x1, y1 = poly[i]
            x2, y2 = poly[(i + 1) % 4]
            nx, ny = y2 - y1, x1 - x2
            pa = [nx * x + ny * y for x, y in a]
            pb = [nx * x + ny * y for x, y in b]
            if max(pa) < min(pb) or max(pb) < min(pa):
                return False
    return True


def _seg_dist(px, py, a, b):
    (x1, y1), (x2, y2) = a, b
    dx, dy = x2 - x1, y2 - y1
    t = max(0.0, min(1.0, ((px - x1) * dx + (py - y1) * dy) / (dx * dx + dy * dy or 1e-9)))
    return math.hypot(px - (x1 + dx * t), py - (y1 + dy * t))


def clear_of_lanes(fp, skip=None):
    """A footprint stays out of every lane and stair (and their half-metre margins)."""
    for lane in LANES:
        if lane["name"] == skip:
            continue
        hw = lane["width"] / 2 + 0.4
        pts = [(p[0], p[1]) for p in lane["pts"]]
        for corner in fp + [((fp[0][0] + fp[2][0]) / 2, (fp[0][1] + fp[2][1]) / 2)]:
            for a, b in zip(pts, pts[1:]):
                if _seg_dist(corner[0], corner[1], a, b) < hw:
                    return False
        # and no lane runs under it
        for a, b in zip(pts, pts[1:]):
            for t in (0.0, 0.25, 0.5, 0.75, 1.0):
                px, py = a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t
                if L._inside([(x, y) for x, y in fp], np.array([px]), np.array([py]))[0]:
                    return False
    return True


_LANE_ARRAYS = {}


def _lane_arrays(lane):
    key = (id(lane), len(lane["pts"]))
    if key not in _LANE_ARRAYS:
        p = np.array([(q[0], q[1]) for q in lane["pts"]], dtype=float)
        _LANE_ARRAYS[key] = (p[:-1], p[1:], p.min(0), p.max(0))
    return _LANE_ARRAYS[key]


def _edge_points(fp, step=0.5):
    out = []
    for (x1, y1), (x2, y2) in zip(fp, fp[1:] + fp[:1]):
        t = np.linspace(0.0, 1.0, max(2, int(math.hypot(x2 - x1, y2 - y1) / step) + 1))
        out.append(np.stack([x1 + (x2 - x1) * t, y1 + (y2 - y1) * t], -1))
    return np.concatenate(out)


def intrusion(fp, lane, margin=0.15):
    """How far a footprint reaches into a lane (its edges sampled every half metre); 0 when it is clear."""
    a, b, lo, hi = _lane_arrays(lane)
    r = lane["width"] / 2 + margin
    P = _edge_points(fp)
    if (P.min(0) > hi + r).any() or (P.max(0) < lo - r).any():
        return 0.0
    ab = b - a
    l2 = np.maximum((ab ** 2).sum(1), 1e-9)
    t = np.clip(((P[:, None, :] - a[None]) * ab[None]).sum(2) / l2[None], 0.0, 1.0)
    d = np.sqrt(((P[:, None, :] - (a[None] + t[..., None] * ab[None])) ** 2).sum(2)).min()
    return max(0.0, float(r - d))


def clear(fp, skip=None, margin=0.4):
    """A footprint stays out of every lane and stair, edges and all; a lane may not run under it either."""
    return clear_of_lanes(fp, skip) and all(intrusion(fp, l, margin) <= 0.0 for l in LANES if l["name"] != skip)


def step_back(b, lane):
    """Where a lane bends towards a house, or its owner turned it, the house steps back until its whole front is clear."""
    for _ in range(6):
        into = intrusion(footprint(b), lane)
        if into <= 0.0:
            return
        c, s = math.cos(math.radians(b["angle"])), math.sin(math.radians(b["angle"]))
        b["ox"] -= s * (into + 0.05)
        b["oy"] += c * (into + 0.05)


def free(fp):
    for b in BUILDINGS:
        if _sat_overlap(fp, footprint(b, -0.15)):  # touching is neighbourly, overlapping is not
            return False
    return True


def at_s(pts, s):
    for (ax, ay, az), (bx, by, bz) in zip(pts, pts[1:]):
        run = math.hypot(bx - ax, by - ay)
        if s <= run:
            t = s / run
            return ax + (bx - ax) * t, ay + (by - ay) * t, az + (bz - az) * t, math.degrees(math.atan2(by - ay, bx - ax))
        s -= run
    return None


def length(pts):
    return sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(pts, pts[1:]))


def row(lane, side, s0, s1, rng, grain="old", base_up=0.4, name="row", skip_lane=None, keep_out=()):
    """Houses along a lane, fronts to it, plot sizes from the measured grain. side +1: uphill (left of travel)."""
    pts = next(l for l in LANES if l["name"] == lane)["pts"]
    hw = next(l for l in LANES if l["name"] == lane)["width"] / 2
    s = s0
    k = 0
    while s < s1:
        if grain == "old":  # Gamle Stavanger: median 9.8 x 7.5 m, quartiles 8.7 to 11.7 long
            w = min(14.0, max(6.0, rng.gauss(9.6, 1.9)))
            d = min(10.0, max(6.0, rng.gauss(7.6, 1.0)))
            storeys = rng.choices([1.5, 2.0, 2.5], [0.58, 0.36, 0.06])[0]
            eave = {1.5: rng.uniform(4.0, 4.8), 2.0: rng.uniform(5.6, 6.4), 2.5: rng.uniform(6.8, 7.4)}[storeys]
            roof = rng.choices(["eaves", "gable"], [0.72, 0.28])[0]
            pitch = rng.uniform(40.0, 48.0)
        else:  # villas
            w = rng.uniform(12.0, 16.0)
            d = rng.uniform(10.0, 13.0)
            eave = rng.uniform(6.0, 7.2)
            roof = rng.choices(["hip", "eaves", "gable"], [0.4, 0.35, 0.25])[0]
            pitch = rng.uniform(32.0, 42.0)
        setback = 0.0 if rng.random() < 0.8 or grain == "old" and side < 0 else rng.uniform(1.5, 3.2)
        if grain == "villa":
            setback = rng.uniform(5.0, 9.0)
        if side > 0:
            p = at_s(pts, s)
            if p is None:
                break
            x, y, z, a = p
            off = hw + setback
            ox, oy = x - math.sin(math.radians(a)) * off, y + math.cos(math.radians(a)) * off
            angle = a
        else:
            p = at_s(pts, s + w)
            if p is None:
                break
            x, y, z, a = p
            off = hw + setback
            ox, oy = x + math.sin(math.radians(a)) * off, y - math.cos(math.radians(a)) * off
            angle = a + 180.0
        base = z + (base_up if side > 0 else 0.0)
        if grain == "old":
            angle += rng.uniform(-5.0, 5.0)  # as their owners placed them, not to a line
        b = dict(name=f"{name} {k}", ox=ox, oy=oy, angle=angle, w=w, d=d, base=base, eave=eave, pitch=pitch,
                 roof=roof, role="row", low=None)
        # where the lane bends towards it, or its owner turned it, the house steps back until its whole front is clear
        own = next(l for l in LANES if l["name"] == lane)
        step_back(b, own)
        fp = footprint(b)
        ok = intrusion(fp, own) <= 0.0 and free(fp) and clear(fp, skip=lane) and not any(
            L._inside(poly, np.array([sum(q[0] for q in fp) / 4]), np.array([sum(q[1] for q in fp) / 4]))[0] for poly in keep_out)
        if ok:
            BUILDINGS.append(b)
            k += 1
            gap = rng.choices([0.0, rng.uniform(0.6, 1.6), rng.uniform(3.0, 5.0)], [0.62, 0.3, 0.08])[0]
            s += w + gap
        else:
            s += 2.0


# -- the corner, the landmarks and the Holm, by hand -------------------------------------------------------------

YARDS = []  # level pads made with walls: (polygon, z)


def grid_block(x0, x1, y0, y1, rng):
    """A perimeter block: buildings along all four sides facing out, a yard in the middle."""
    def base_at(x, y):
        return float(L.z_at(x, y))
    depth = 11.0
    sides = [  # (start point, direction angle, length): fronts face out
        ((x0, y1), -90.0, y1 - y0),   # the side facing -x (north), running -y
        ((x0, y0), 0.0, x1 - x0),     # the side facing -y (west), running +x
        ((x1, y0), 90.0, y1 - y0),    # the side facing +x (south), running +y
        ((x1, y1), 180.0, x1 - x0),   # the side facing +y (east), running -x
    ]
    for (sx, sy), a, run in sides:
        s = 0.0
        while s < run - 6.0:
            w = min(run - s, rng.uniform(9.0, 15.0))
            c, sn = math.cos(math.radians(a)), math.sin(math.radians(a))
            ox, oy = sx + c * s, sy + sn * s
            mid = (ox + c * w / 2 - sn * depth / 2, oy + sn * w / 2 + c * depth / 2)
            b = dict(name=f"the Grid {len(BUILDINGS)}", ox=ox, oy=oy, angle=a, w=w, d=depth,
                     base=base_at(*mid) + 0.2, eave=rng.choice([6.6, 7.2, 9.8, 10.4]), pitch=rng.uniform(30, 40),
                     roof=rng.choice(["eaves", "eaves", "hip"]), role="row", low=None)
            fp = footprint(b)
            if free(fp) and clear_of_lanes(fp):
                BUILDINGS.append(b)
            s += w


def lay_out():
    BUILDINGS.clear()
    YARDS.clear()
    rng = random.Random(SEED)

    # the corner (docs/experiments.md, LT1, the reset): A and B at the foot of Gully Steps on Harbour Row,
    # C beside the Landing, D on the knuckle, E closing the view where the steps meet Top Terrace
    building("A (104, café 1988)", 37.2, hr_line(37.2)[0], hr_line(37.2)[1], 9.8, 9.2, 1.9, 6.8, 54.0, "mansard", "corner")
    building("B (105)", 52.0, hr_line(52.0)[0], hr_line(52.0)[1], 9.4, 8.4, 1.9, 6.9, 12.0, "hip", "corner")
    building("C (1203, cooper 1879)", 41.4, 38.3, 180.0, 7.2, 7.4, 8.2, 4.4, 45.0, "gable", "corner")
    building("D (1107, empty since 1986)", 53.6, _yh + 6.3, -90.0, 7.6, 7.0, 12.65, 4.0, 46.0, "gable", "corner")
    building("E (304, 1826)", 50.0, _yt + 3.1, 90.0, 7.0, 6.8, 16.6, 4.0, 46.0, "eaves", "corner")
    YARDS.append(([(36.0, _yl + 2.2), (45.4, _yl + 2.2), (45.4, 30.6), (36.0, 30.6)], 5.2))

    # Harbour Row: merchants' houses and warehouses on the quay road, gables and eaves mixed
    hx = -244.0
    for w, d, eave, pitch, roof in [(12.0, 10.0, 8.6, 40.0, "gable"), (10.6, 9.0, 6.8, 42.0, "eaves"), (9.0, 8.5, 5.8, 46.0, "gable"),
                                    (11.4, 9.0, 7.4, 40.0, "eaves"), (8.0, 8.0, 5.4, 46.0, "eaves"), (10.0, 14.0, 9.0, 40.0, "gable"),
                                    (12.4, 9.0, 7.6, 40.0, "eaves"), (9.6, 8.5, 6.2, 44.0, "eaves"), (8.6, 9.5, 6.0, 46.0, "gable"),
                                    (12.0, 9.0, 7.8, 40.0, "eaves"), (10.8, 9.0, 6.6, 42.0, "eaves"), (9.2, 8.0, 5.6, 46.0, "eaves"),
                                    (11.0, 9.0, 7.2, 40.0, "eaves"), (8.4, 9.5, 6.0, 46.0, "gable"), (10.2, 9.0, 6.8, 42.0, "eaves"),
                                    (11.6, 10.0, 7.6, 40.0, "eaves"), (9.6, 9.0, 6.0, 44.0, "gable"), (10.4, 9.0, 7.0, 42.0, "eaves"),
                                    (12.8, 9.0, 7.8, 40.0, "eaves"), (9.4, 8.5, 6.2, 44.0, "eaves"), (10.6, 15.0, 9.4, 40.0, "gable"),
                                    (11.8, 9.0, 7.4, 40.0, "eaves"), (9.0, 8.5, 5.8, 46.0, "eaves"), (10.4, 9.0, 6.6, 42.0, "gable"),
                                    (12.2, 9.0, 7.6, 40.0, "eaves"), (10.0, 9.0, 6.4, 42.0, "eaves"), (9.8, 9.0, 6.8, 42.0, "eaves"),
                                    (11.2, 9.0, 7.2, 40.0, "eaves"), (10.0, 9.0, 6.0, 44.0, "gable"), (12.0, 9.0, 7.6, 40.0, "eaves")]:
        if hx > 150:
            break
        yb, ab = hr_line(hx)
        b = dict(name=f"Harbour Row {len(BUILDINGS)}", ox=hx, oy=yb, angle=ab, w=w, d=d, base=1.9, eave=eave,
                 pitch=pitch, roof=roof, role="row", low=None)
        fp = footprint(b)
        if free(fp) and clear(fp, skip="Harbour Row"):
            BUILDINGS.append(b)
        hx += w + rng.choice([0.0, 0.0, 0.4, 0.8, 1.2])
    # round the head's curve to the square
    for x0, w in [(156.0, 11.0), (169.0, 10.0), (181.0, 12.0), (215.0, 10.0), (227.0, 11.0), (240.0, 10.0), (262.0, 12.0), (276.0, 10.0)]:
        oy, ang = hr_line(x0)
        b = dict(name=f"Harbour Row {len(BUILDINGS)}", ox=x0, oy=oy, angle=ang, w=w, d=9.0, base=2.0,
                 eave=rng.uniform(6.2, 8.0), pitch=rng.uniform(38, 46), roof=rng.choice(["eaves", "eaves", "gable"]), role="row", low=None)
        fp = footprint(b)
        if free(fp) and clear_of_lanes(fp, skip="Harbour Row"):
            BUILDINGS.append(b)

    # the landmarks
    # the cathedral fronts the square: its west door and the nave's south door open to it and to School Lane
    building("the cathedral, nave", 433.0, 18.0, -90.0, 60.0, 19.0, 9.6, 14.0, 50.0, "eaves", "landmark")
    building("the cathedral, west tower", 433.0, -40.0, -90.0, 12.0, 19.0, 9.6, 34.0, 60.0, "tower", "landmark")
    building("the cathedral, choir", 445.0, 36.0, -90.0, 18.0, 11.0, 9.6, 12.0, 50.0, "eaves", "landmark")
    building("the Fish Hall", 348.5, -133.0, 0.0, 30.0, 12.0, 2.5, 6.0, 30.0, "gable", "landmark")
    building("the Fire Watch", 136.0, -322.0, 0.0, 8.0, 8.0, WATCH_Z - 0.2, 23.0, 0.0, "tower", "landmark")  # 27 m to the top
    building("the breakwater's light", -314.0, -114.0, 0.0, 4.0, 4.0, 2.5, 9.0, 0.0, "tower", "landmark")
    building("the beacon on the Pip", -372.0, -62.0, 0.0, 3.0, 3.0, 6.0, 7.0, 0.0, "tower", "landmark")
    building("the customs house", -198.0, -208.0, 90.0, 14.0, 9.0, 3.4, 5.2, 42.0, "eaves", "landmark")
    building("the harbour master", -196.0, -248.0, 90.0, 9.0, 8.0, 4.6, 4.6, 44.0, "gable", "landmark")
    building("the bandstand in Lookout Park", 6.0, 232.0, 0.0, 6.0, 6.0, 46.0, 3.0, 30.0, "hip", "landmark")
    building("the tunnel's portal", -266.0, 4.0, 0.0, 8.0, 3.0, 1.9, 6.0, 0.0, "flat", "landmark")

    # the Holm: sea houses (sjøhus) side by side on Barrel Quay, gables to the water, three or four storeys,
    # 18 to 26 m deep, a hoist in each gable; a stair-lane up to Holm Street every few houses
    STAIR_LANES.clear()
    x = -186.0
    k = 0
    while x < 28.0:
        w = rng.uniform(8.0, 12.0)
        if x + w > 34.0:
            break
        yq = lane_y(BARREL_QUAY, x + w / 2) or -162.0
        front = yq - 6.0 - rng.uniform(0.0, 0.8)
        building(f"Holm sea house {k}", x + w, front, 180.0, w, rng.uniform(18.0, 26.0), 2.1,
                 rng.uniform(9.4, 12.6), rng.uniform(45, 52), "gable", "warehouse")
        step_back(BUILDINGS[-1], LANES[[l["name"] for l in LANES].index("Barrel Quay")])
        k += 1
        if k % 4 == 0:
            sx = x + w + 1.4
            STAIR_LANES.append(dict(name=f"stair-lane {len(STAIR_LANES)}", width=2.2, kind="steps",
                                    pts=[(sx, yq - 6.2, 2.0), (sx, -220.4, 8.0)]))
            x += w + 2.8
        else:
            x += w + rng.choice([0.0, 0.0, 0.4, 0.9])
    LANES[:] = [l for l in LANES if not l["name"].startswith("stair-lane")] + STAIR_LANES
    # the Holm's west side: small houses and pubs facing Holm Street, backs to Slipway Cove
    for k, (x0, w) in enumerate([(-176, 9.0), (-165, 8.0), (-154, 10.0), (-142, 9.0), (-128, 11.0), (-114, 8.0), (-103, 10.0),
                                 (-90, 9.0), (-78, 12.0), (-62, 8.0), (-51, 10.0), (-38, 9.0), (-26, 11.0), (-12, 8.0), (-1, 10.0), (12, 9.0), (24, 8.0)]):
        building(f"Holm Street west {k}", x0, -227.4, 0.0, w, rng.uniform(8.0, 11.0), 8.0, rng.uniform(5.0, 7.4),
                 rng.uniform(40, 48), rng.choice(["eaves", "eaves", "gable"]), "row")
        BUILDINGS[-1]["oy"] = -227.4
        BUILDINGS[-1]["angle"] = 0.0
        # these face +y (Holm Street) with the house behind them to -y: flip the frame
        b = BUILDINGS[-1]
        b["ox"], b["oy"], b["angle"] = x0 + w, -227.4, 180.0
    row("Holm Street", +1, 6.0, 250.0, rng, name="Holm Street, quay side on the Holm")
    # the mainland's west quay: warehouses on Barrel Quay, houses and pubs above on Holm Street (St. John's)
    stairs = (94.0, 166.0, 214.0)
    for sx in stairs:
        yq = lane_y(BARREL_QUAY_SOUTH, sx) or -150.0
        STAIR_LANES.append(dict(name=f"stair-lane {len(STAIR_LANES)}", width=2.2, kind="steps",
                                pts=[(sx, yq - 6.4, 2.1), (sx, (lane_y(HOLM_STREET, sx) or -200.0) + 3.2, 8.0)]))
    LANES[:] = [l for l in LANES if not l["name"].startswith("stair-lane")] + STAIR_LANES
    x0 = 58.0
    k = 0
    while x0 < 228.0:
        w = rng.uniform(8.5, 12.0)
        if 232 < x0 + w and x0 < 268:
            x0 = 268.0
            continue  # Broad Street
        gap = next((sx for sx in stairs if x0 - 1.6 < sx < x0 + w + 1.6), None)
        if gap is not None:
            x0 = gap + 1.6  # the stair-lane's gap between two warehouses
            continue
        yq = lane_y(BARREL_QUAY_SOUTH, x0 + w / 2) or -150.0
        building(f"Barrel Quay sea house {k}", x0 + w, yq - 6.4, 180.0, w, rng.uniform(16.0, 22.0), 2.2,
                 rng.uniform(9.0, 12.0), rng.uniform(44, 52), "gable", "warehouse")
        step_back(BUILDINGS[-1], LANES[[l["name"] for l in LANES].index("Barrel Quay south")])
        k += 1
        x0 += w + rng.choice([0.0, 0.4, 0.8, 3.0])
    for k, x0 in enumerate(range(62, 228, 11)):
        if 228 < x0 + 10 and x0 < 268:
            continue
        yh = lane_y(HOLM_STREET, x0 + 5) or -205.0
        w = rng.uniform(8.0, 10.4)
        b = dict(name=f"Holm Street south {k}", ox=x0 + w, oy=yh - 3.4, angle=180.0, w=w, d=rng.uniform(8.0, 10.0),
                 base=8.2, eave=rng.uniform(5.0, 7.0), pitch=rng.uniform(40, 48), roof=rng.choice(["eaves", "gable"]),
                 role="row", low=None)
        if free(footprint(b)) and clear(footprint(b)):
            BUILDINGS.append(b)

    # Market Square's edges: an irregular room, streets entering at its corners
    for name, ox, oy, a, w, d, eave in [("the square's south side 1", 434.6, -130.0, -90.0, 22.0, 12.0, 9.0),
                                        ("the square's south side 2", 437.4, -110.0, -90.0, 16.0, 12.0, 10.0),
                                        ("the square's south side 3", 440.4, -84.0, -90.0, 24.0, 12.0, 8.6),
                                        ("the bank", 396.0, -139.0, 180.0, 24.0, 13.0, 11.0),
                                        ("the hotel", 434.0, -152.0, 180.0, 30.0, 16.0, 13.0)]:
        building(name, ox, oy, a, w, d, 2.6, eave, 36.0, "hip", "landmark")

    # the Grid: rebuilt straight after the fires, laid over the slope regardless of it; perimeter blocks of
    # two- and three-storey buildings round yards, 12 m streets, Broad Street (30 m) one of its lines
    for bx0, bx1 in GRID_X:
        for by0, by1 in GRID_Y:
            grid_block(bx0, bx1, by1, by0, rng)

    # Holm Street's mainland stretch, both sides; Broad Street's north side
    hs = length(HOLM_STREET)
    row("Holm Street", -1, 292.0, hs - 6.0, rng, name="Holm Street, quay side")
    row("Holm Street", +1, 292.0, hs - 6.0, rng, name="Holm Street, knoll side")
    row("Broad Street", +1, 8.0, length(BROAD_STREET) - 50.0, rng, name="Broad Street north")
    # the square's east side, facing it; the cathedral school and the bishop's house behind
    for k, (x0, w) in enumerate([(340.0, 20.0), (362.0, 21.4), (386.0, 21.6), (410.0, 14.6)]):
        rng.random()
        building(f"the square's east side {k}", x0, -37.0, 0.0, w, 12.0, MARKET_Z + 0.1,
                 rng.uniform(8.0, 11.0), 38.0, rng.choice(["hip", "eaves"]), "landmark")
    building("the cathedral school", 312.0, 36.0, 0.0, 52.0, 14.0, float(L.z_at(338.0, 43.0)), 9.0, 40.0, "hip", "landmark")
    building("the bishop's house", 372.0, 80.0, 0.0, 18.0, 13.0, float(L.z_at(381.0, 86.0)), 8.0, 38.0, "hip", "landmark")

    # the old town's rows along its terraces, uphill and downhill sides
    keep = [p for _, p, _ in SMALL_PLACES] + [LANDING, [(36.0, _yl + 1.0), (47.6, _yl + 1.0), (47.6, LANDING[0][1]), (36.0, LANDING[0][1])],
            [(53.0, _yh - 9.0), (68.0, _yh - 9.0), (68.0, _yh + 10.0), (53.0, _yh + 10.0)]]
    for lane, z in [("Low Terrace", 3.0), ("High Terrace", 8.0), ("Top Terrace", 16.0)]:
        pts = next(l for l in LANES if l["name"] == lane)["pts"]
        row(lane, +1, 2.0, length(pts) - 4, rng, name=f"{lane} up", keep_out=keep)
        row(lane, -1, 3.0, length(pts) - 4, rng, name=f"{lane} down", keep_out=keep)
    row("Crest Lane", -1, 4.0, length(CREST) - 6, rng, name="Crest Lane down", keep_out=keep)
    row("Crest Lane", +1, 4.0, length(CREST) - 6, rng, grain="villa", name="the Heights", keep_out=keep)
    for r in RAMPS:
        row(r["name"], +1, 3.0, length(r["pts"]) - 3, rng, name=f"{r['name']} up", keep_out=keep)
        row(r["name"], -1, 3.0, length(r["pts"]) - 3, rng, name=f"{r['name']} down", keep_out=keep)
    door_paths()
    details(rng)


EXEMPT = ("the beacon on the Pip", "the tunnel's portal", "the bandstand in Lookout Park")  # reached by boat; a road's mouth; in the park


def _door(b):
    c, s_ = math.cos(math.radians(b["angle"])), math.sin(math.radians(b["angle"]))
    u, v = b["w"] / 2, -0.4
    return b["ox"] + u * c - v * s_, b["oy"] + u * s_ + v * c


def _nearest_on_ways(x, y):
    best = (1e9, None, None)
    for lane in LANES:
        pts = [(p[0], p[1], p[2]) for p in lane["pts"]]
        for (x1, y1, z1), (x2, y2, z2) in zip(pts, pts[1:]):
            dx, dy = x2 - x1, y2 - y1
            t = max(0.0, min(1.0, ((x - x1) * dx + (y - y1) * dy) / (dx * dx + dy * dy or 1e-9)))
            px, py = x1 + dx * t, y1 + dy * t
            d = math.hypot(x - px, y - py) - lane["width"] / 2
            if d < best[0]:
                # the point on the way's edge nearest the door
                k = (lane["width"] / 2) / max(math.hypot(x - px, y - py), 1e-6)
                best = (d, (px + (x - px) * k, py + (y - py) * k, z1 + (z2 - z1) * t), lane)
    for name, poly, z in SMALL_PLACES + [("the Landing", LANDING, LANDING_Z), ("Market Square", MARKET_SQUARE, MARKET_Z)]:
        if L._inside(poly, np.array([x]), np.array([y]))[0]:
            return (-1.0, None, None)
    return best


def door_paths():
    """Every door gets its way: a garden path or steps from the door to the nearest street, lane or stair."""
    added = []
    for b in BUILDINGS:
        if b["name"] in EXEMPT:
            continue
        x, y = _door(b)
        d, p, lane = _nearest_on_ways(x, y)
        if d <= 2.5 or p is None or d > 25.0:
            continue
        rise = abs(b["base"] - p[2])
        added.append(dict(name=f"the way to {b['name']}", width=1.4, door=True, kind="steps" if rise / max(d, 0.1) > 0.12 else "path",
                          pts=[(p[0], p[1], p[2]), (x, y, b["base"])]))
    LANES.extend(added)


DETAILS = []    # small masses between the buildings: (kind, centre x, y, base z, length, width, height, angle)
FAR = []        # landmarks beyond the heart: built on the land where they stand


def detail(kind, x, y, z, l, w, h, a=0.0):
    DETAILS.append(dict(kind=kind, x=x, y=y, z=z, l=l, w=w, h=h, a=a))


def _local(b, u, v):
    c, s = math.cos(math.radians(b["angle"])), math.sin(math.radians(b["angle"]))
    return b["ox"] + u * c - v * s, b["oy"] + u * s + v * c


# -- the town at night: its lamps and who is in -------------------------------------------------------------------
# Every light on screen is a fact. Until the engine gives them, they are authored here for one evening: 17:50 on
# Friday 20 October 1989, blue hour, sea fog.

# Lamps by the era their street was lit: the old town's lanes and stairs got lanterns with warm bulbs in 1955; Holm
# Street's were replaced with mercury lamps in the 1960s; the quays, Broad Street and the Grid's streets were lit
# with high-pressure sodium on poles in the 1970s.
LAMP_ERAS = {"warm": "1955, lanterns, incandescent", "mercury": "the 1960s, mercury vapour", "sodium": "the 1970s, high-pressure sodium"}


def lamp_kind(lane):
    if lane["kind"] in ("quay", "road") or lane["name"] in ("Broad Street",) or lane["name"].startswith("the Grid"):
        return "sodium"
    if lane["name"].startswith("Holm Street"):
        return "mercury"
    return "warm"


def key(b):
    """A building's own name for seeding: its name, and where it stands for the unnamed ones."""
    return f"{b['name']}@{b['ox']:.1f},{b['oy']:.1f}"


def evening(b):
    """Who is in at 17:50 that Friday, for one building (authored, seeded by its name so it never changes between
    frames): the share of its upper windows lit, and its ground floor's front: a lit shop, pub or café, a closed or
    empty one, or none. Which of its windows glow is seeded texture; that someone is home is the fact."""
    r = random.Random(f"evening:{key(b)}")
    name, role = b["name"], b["role"]
    shop = None
    if role == "context":  # the town round the heart, by its district's use
        use = b.get("use", "home")
        if use == "night":
            return dict(upper=0.3, shop="open" if r.random() < 0.7 else "closed")
        if use in ("work", "civic"):
            return dict(upper=0.2 if r.random() < 0.6 else 0.0, shop=None)
        return dict(upper=0.35 if r.random() < 0.85 else 0.0, shop=None)
    if name.startswith("D (1107"):
        return dict(upper=0.0, shop=None)  # empty and boarded since 1986
    if name.startswith("A (104"):
        return dict(upper=0.4, shop="open")  # the café, opened in 1988
    if role == "corner":
        return dict(upper=0.45, shop=None)
    if name.startswith("Harbour Row"):
        shop = r.choices(["open", "closed", "empty"], [0.45, 0.35, 0.2])[0]  # a boom town in a slump
        return dict(upper=0.3 if r.random() < 0.8 else 0.0, shop=shop)
    if name.startswith(("Holm Street", "Holm Street west")):
        shop = r.choices(["open", "closed"], [0.7, 0.3])[0]  # pubs, a club, a chip shop
        return dict(upper=0.3, shop=shop)
    if role == "warehouse":
        shop = "open" if r.random() < 0.28 else None  # sea houses turned bars and restaurants
        return dict(upper=0.08, shop=shop)
    if name.startswith("the Grid"):
        shop = r.choices(["open", "closed", "empty"], [0.4, 0.45, 0.15])[0]
        return dict(upper=0.25, shop=shop)
    if role == "landmark":
        upper = {"the hotel": 0.6, "the bishop's house": 0.4, "the harbour master": 0.5, "the customs house": 0.1,
                 "the bank": 0.05}.get(name, 0.0)
        if name.startswith("the square's"):
            return dict(upper=0.3, shop=r.choices(["open", "closed"], [0.5, 0.5])[0])
        return dict(upper=upper, shop=None)
    # the old town's houses and the Heights' villas: someone is home in most
    return dict(upper=0.35 if r.random() < 0.85 else 0.0, shop=None)


# The harbour's own lights, lit every night: the breakwater's head (red) and the beacon on the Pip (white)
BEACONS = [("the breakwater's light", "red"), ("the beacon on the Pip", "white")]


def details(rng):
    """Yards, walls, sheds, stoops, fences, bollards, quay steps, boats, lamps, benches, the square's furniture."""
    DETAILS.clear()
    FAR.clear()
    lanes_by = {l["name"]: l for l in LANES}
    for b in BUILDINGS:
        if b["role"] != "row" or b["name"].startswith(("the Grid", "Harbour Row", "Holm")):
            continue
        uphill = " up" in b["name"] or "the Heights" in b["name"]
        # a yard behind, its back wall, sometimes a shed in it; cut short where a lane runs behind, never in it
        want = rng.uniform(3.0, 5.5)
        yard = None
        for yd in (want, 2.6, 1.6):
            poly = [_local(b, 0, b["d"]), _local(b, b["w"], b["d"]), _local(b, b["w"], b["d"] + yd), _local(b, 0, b["d"] + yd)]
            if free(poly) and clear(poly, margin=0.2):
                yard = poly
                break
        if yard is not None:
            mx, my = _local(b, b["w"] / 2, b["d"] + yd)
            detail("wall", mx, my, b["base"] - 0.2, b["w"], 0.42, 1.5, b["angle"])
            if rng.random() < 0.35 and yd > 2.0:
                sx, sy = _local(b, b["w"] * rng.uniform(0.2, 0.8), b["d"] + yd - 1.2)
                detail("shed", sx, sy, b["base"], 2.4, 2.0, 2.3, b["angle"] + rng.uniform(-6, 6))
            if rng.random() < 0.3:
                ax, ay = _local(b, 0.6, b["d"] + yd * 0.5)
                cx, cy = _local(b, b["w"] - 0.6, b["d"] + yd * 0.5)
                detail("line", (ax + cx) / 2, (ay + cy) / 2, b["base"] + 1.8, math.hypot(cx - ax, cy - ay), 0.04, 0.04, b["angle"])
        # a stoop where the door stands above the lane
        lane = None
        for name, l in lanes_by.items():
            if b["name"].startswith(name):
                lane = l
        if uphill and lane is not None:
            fx, fy = _local(b, b["w"] * 0.5, -0.8)
            _, zl = L._line_dist_z(np.array([fx]), np.array([fy]), [(p[0], p[1], p[2]) for p in lane["pts"]])
            rise = b["base"] - float(zl[0])
            if rise > 0.25:
                detail("stoop", fx, fy, float(zl[0]), 1.6, 1.4, rise, b["angle"])
    # quays: bollards along the edges, stone steps down to the water, the Penny Ferry's stages
    for edge, every in [([(-250.0, -15.2), (-160.0, -15.2), (-60.0, -12.2), (150.0, -14.8)], 12.0),
                        ([(-188.0, -157.0), (0.0, -156.6), (38.0, -151.0)], 11.0),
                        ([(58.0, -151.0), (150.0, -141.0), (240.0, -131.0), (298.0, -125.0)], 12.0)]:
        run = 0.0
        for (x1, y1), (x2, y2) in zip(edge, edge[1:]):
            L_ = math.hypot(x2 - x1, y2 - y1)
            a = math.degrees(math.atan2(y2 - y1, x2 - x1))
            t = (every - run % every) if run else 0.0
            while t < L_:
                px, py = x1 + (x2 - x1) * t / L_, y1 + (y2 - y1) * t / L_
                detail("bollard", px, py, 1.9, 0.5, 0.5, 0.7, a)
                t += every
            run += L_
        for k in range(1, 4):
            (x1, y1), (x2, y2) = edge[min(k, len(edge) - 1) - 1], edge[min(k, len(edge) - 1)]
            px, py = (x1 + x2) / 2, (y1 + y2) / 2
            detail("quay steps", px, py, -0.6, 6.0, 1.6, 2.5, math.degrees(math.atan2(y2 - y1, x2 - x1)))
    detail("pontoon", 60.0, -19.5, -0.1, 10.0, 4.0, 0.5, 0.0)
    detail("pontoon", 60.0, -147.0, -0.1, 10.0, 4.0, 0.5, 0.0)
    # boats moored along the quays, a few gaps; the tall ship at Barrel Quay for the summer
    for (x1, x2, yq, side) in [(-230.0, 140.0, -15.2, -1), (-180.0, 30.0, -156.8, +1), (70.0, 290.0, -138.0, +1)]:
        x = x1 + rng.uniform(0, 8)
        while x < x2:
            if rng.random() < 0.7:
                Lb = rng.choice([7.0, 9.0, 14.0, 18.0, 22.0])
                Wb = 2.6 if Lb < 10 else 5.2
                detail("boat", x + Lb / 2, yq + side * (Wb / 2 + 0.8), SEA - 0.6, Lb, Wb, 2.2 if Lb < 10 else 3.0, 0.0)
                if Lb >= 14:
                    detail("wheelhouse", x + Lb * 0.66, yq + side * (Wb / 2 + 0.8), SEA + 2.2, 3.4, 3.2, 2.6, 0.0)
                x += Lb + rng.uniform(1.0, 4.0)
            else:
                x += rng.uniform(10.0, 24.0)
    detail("tall ship", 196.0, -126.0, SEA - 1.0, 44.0, 8.0, 4.2, 6.0)
    for k, mx in enumerate((-14.0, 0.0, 13.0)):
        detail("mast", 196.0 + mx * math.cos(math.radians(6)), -126.0 + mx * math.sin(math.radians(6)), SEA + 3.0, 0.5, 0.5, 30.0 - 4 * abs(k - 1), 6.0)
    # lamps: lanterns on posts along the old town's lanes, poles along the quays and Broad Street; each lamp the
    # kind its lane was lit with (LAMP_ERAS)
    for lane in LANES:
        if lane["kind"] == "steps" and lane["width"] < 2.5:
            continue
        pole = lane["kind"] == "quay" or lane["name"] == "Broad Street"
        light = lamp_kind(lane)
        every = 30.0 if pole else 24.0
        s, total, k = 6.0, length(lane["pts"]), 0
        while s < total:
            p = at_s(lane["pts"], s)
            if p is None:
                break
            x, y, z, a = p
            off = lane["width"] / 2 + 0.3
            side = 1 if k % 2 == 0 else -1
            lx, ly = x - math.sin(math.radians(a)) * off * side, y + math.cos(math.radians(a)) * off * side
            if not any(_sat_overlap([(lx - 0.2, ly - 0.2), (lx + 0.2, ly - 0.2), (lx + 0.2, ly + 0.2), (lx - 0.2, ly + 0.2)], footprint(b)) for b in BUILDINGS):
                detail("pole" if pole else "lantern", lx, ly, z, 0.25, 0.25, 7.0 if pole else 3.6, a)
                DETAILS[-1]["light"] = light
                DETAILS[-1]["arm"] = ((x - lx) / off, (y - ly) / off)  # towards the lane it lights
            s += every
            k += 1
    # the corner's lantern on the Landing, put up in 1955 when the council brought electric light to the lane
    detail("lantern", 44.2, LANDING[0][1] + 1.0, LANDING_Z, 0.25, 0.25, 3.6, 0.0)
    DETAILS[-1]["light"] = "warm"
    # benches on the Hundred Steps' landings and in Lookout Park; the square's fountain and stalls
    for (x, y, z) in HUNDRED_STEPS[2::2]:
        detail("bench", x + 1.5, y, z, 1.8, 0.5, 0.45, 90.0)
    detail("bench", 10.0, 226.0, 45.6, 1.8, 0.5, 0.45, 0.0)
    detail("fountain", 400.0, -92.0, MARKET_Z, 6.0, 6.0, 0.8, 0.0)
    detail("fountain", 400.0, -92.0, MARKET_Z + 0.8, 1.2, 1.2, 2.6, 0.0)
    for i in range(4):
        for j in range(2):
            detail("stall", 362.0 + i * 7.0, -120.0 + j * 9.0, MARKET_Z, 3.2, 2.4, 2.6, 0.0)
    detail("well", 12.0, lane_y(HIGH, 12.0), 8.0, 1.6, 1.6, 0.9, 0.0)
    detail("crane", 330.0, -124.0, 2.4, 1.2, 1.2, 9.0, 0.0)

    # beyond the heart: the adventure's landmarks, standing on the land where they are
    FAR.extend([
        dict(name="the cannery's chimney", kind="chimney", x=-130.0, y=470.0, w=4.0, h=42.0),
        dict(name="the wreck: a mast", kind="mast", x=-470.0, y=-32.0, w=0.6, h=11.0),
        dict(name="the wreck: its bow", kind="bow", x=-466.0, y=-26.0, w=5.0, h=2.4),
        dict(name="the platform in the fjord", kind="condeep", x=-2100.0, y=1500.0, w=110.0, h=150.0),
        dict(name="the High Bridge", kind="bridge", x=-470.0, y=1030.0, x2=-640.0, y2=620.0, w=14.0, h=42.0),
        dict(name="the monastery on Gull Island", kind="ruin", x=-628.0, y=-392.0, w=30.0, h=12.0),
        dict(name="the Supply Base's cranes", kind="cranes", x=-300.0, y=-820.0, w=60.0, h=38.0),
        dict(name="the funicular", kind="funicular", x=300.0, y=640.0, x2=440.0, y2=850.0, w=4.0, h=0.0),
        dict(name="the water tower", kind="tower", x=440.0, y=860.0, w=14.0, h=24.0),
        dict(name="the Culture House", kind="block", x=700.0, y=-300.0, w=50.0, h=18.0),
        dict(name="the Expo Hall", kind="block", x=980.0, y=-620.0, w=90.0, h=16.0),
    ])


def _box(x, y, a, l, w):
    c, s = math.cos(math.radians(a)), math.sin(math.radians(a))
    return [(x + u * c - v * s, y + u * s + v * c) for u, v in [(-l / 2, -w / 2), (l / 2, -w / 2), (l / 2, w / 2), (-l / 2, w / 2)]]


def wall_clear(fp, own=None):
    """A wall may stand along a way but never across another: not where a lane, a stair or a door path joins it,
    and not into a square, the Landing or a small place."""
    for l in LANES:  # its own way too: on the inside of a bend or a switchback a wall would cut the next flight
        if intrusion(fp, l, -0.1) > 0.0:  # touching a way's edge is fine, standing in it is not
            return False
    xs = np.array([p[0] for p in fp])
    ys = np.array([p[1] for p in fp])
    for poly in [LANDING, MARKET_SQUARE] + [p for _, p, _ in SMALL_PLACES]:
        if L._inside(poly, xs, ys).any():
            return False
    return True


def ground_walls(ground):
    """The retaining walls the ground needs: along every lane and stair cut into the slope or standing over it, and
    round the Landing, the small places and the yards where they stand over the ground. ground(x, y) is the carved
    ground's height. Each wall: dict(x, y, a, l, w, z0, z1), a box l long at angle a."""
    walls = []
    for lane in LANES:
        if lane["kind"] not in ("lane", "steps") or lane["width"] > 8.0:
            continue
        pts = lane["pts"]
        hw = lane["width"] / 2
        s, total = 1.0, length(pts)
        while s < total - 1.0:
            p = at_s(pts, s)
            if p is None:
                break
            x, y, z, a = p
            nx, ny = -math.sin(math.radians(a)), math.cos(math.radians(a))
            for side in (1, -1):
                ex, ey = x + nx * (hw + 0.3) * side, y + ny * (hw + 0.3) * side
                out = ground(x + nx * (hw + 3.0) * side, y + ny * (hw + 3.0) * side)
                if out - z > 1.0:
                    z0, z1 = z - 0.3, min(out, z + 4.0)
                elif z - out > 1.0:
                    z0, z1 = out - 0.3, z + 0.9
                else:
                    continue
                if wall_clear(_box(ex, ey, a, 2.05, 0.45), own=lane):
                    walls.append(dict(x=ex, y=ey, a=a, l=2.05, w=0.45, z0=z0, z1=z1))
            s += 2.0
    for poly, z in [(LANDING, LANDING_Z)] + [(p, z) for _, p, z in SMALL_PLACES] + YARDS:
        cx = sum(p[0] for p in poly) / len(poly)
        cy = sum(p[1] for p in poly) / len(poly)
        for (x1, y1), (x2, y2) in zip(poly, poly[1:] + poly[:1]):
            a = math.degrees(math.atan2(y2 - y1, x2 - x1))
            run = math.hypot(x2 - x1, y2 - y1)
            n = max(1, int(round(run / 2.0)))
            for i in range(n):  # in pieces, so a way that enters the place leaves its gap
                t = (i + 0.5) / n
                mx, my = x1 + (x2 - x1) * t, y1 + (y2 - y1) * t
                r = max(math.hypot(mx - cx, my - cy), 1e-6)
                out = ground(mx + (mx - cx) * 0.2 + (mx - cx) / r, my + (my - cy) * 0.2 + (my - cy) / r)
                if z - out <= 0.8:
                    continue
                fp = _box(mx, my, a, run / n + 0.02, 0.45)
                if any(intrusion(fp, l, -0.1) > 0.0 for l in LANES):
                    continue
                walls.append(dict(x=mx, y=my, a=a, l=run / n + 0.02, w=0.45, z0=out - 0.3, z1=z + 0.9))
    return walls


def paving(X, Y):
    """What the ground is at points X, Y: the swatch of the shared palette it sits on. Granite setts on the quays,
    the old town's lanes, stairs and squares; asphalt on the streets cars took over; elsewhere earth and grass, where
    no puddle lies."""
    out = np.full(X.shape, "ground", dtype=object)
    for lane in LANES:
        d, _ = L._line_dist_z(X, Y, [(p[0], p[1], p[2]) for p in lane["pts"]])
        on = d <= lane["width"] / 2 + 0.3
        road = lane["kind"] == "road" or lane["name"] in ("Broad Street", "Holm Street") or lane["name"].startswith("the Grid")
        out[on] = "asphalt" if road else "setts_mean"
    for poly in [MARKET_SQUARE, LANDING] + [p for _, p, _ in SMALL_PLACES]:
        out[L._inside(poly, X, Y)] = "setts_mean"
    return out


def carve(X, Y, Z):
    """Cut the heart's lanes, stairs, quays, squares, yards and house pads into the ground (arrays, in place)."""
    rock = np.zeros(X.shape, dtype=bool)
    for o in L.OUTCROPS:
        rock |= np.hypot((X - o["x"]) / o["sx"], (Y - o["y"]) / o["sy"]) < o["r"]
    for r in L.ROCKS:
        rock |= L._inside(r["outline"], X, Y)
    water = L.water_mask(X, Y)
    ways = np.zeros(X.shape, dtype=bool)
    for lane in LANES:
        d, zl = L._line_dist_z(X, Y, [(p[0], p[1], p[2]) for p in lane["pts"]])
        hw = lane["width"] / 2 + 0.3
        on = (d <= hw) & ~water
        Z[on] = zl[on]
        ways |= on
        bank = (d > hw) & (d < hw + 14.0) & ~water
        lo = zl - (d - hw) * 0.75
        hi = zl + (d - hw) * 0.95
        Zb = np.where(rock, np.maximum(Z, lo), np.minimum(np.maximum(Z, lo), hi))
        Z[bank] = Zb[bank]
    sq = L._inside(MARKET_SQUARE, X, Y)
    Z[sq] = MARKET_Z
    lz = L._inside(LANDING, X, Y)
    Z[lz] = LANDING_Z
    for _, poly, z in SMALL_PLACES:
        Z[L._inside(poly, X, Y)] = z
    for poly, z in YARDS:
        m = L._inside(poly, X, Y) & ~ways  # a yard never lifts a way
        Z[m] = z
    for b in BUILDINGS:
        if b["role"] == "context":
            continue
        fp = footprint(b, 0.6)
        xs = [p[0] for p in fp]
        ys = [p[1] for p in fp]
        sel = (X >= min(xs)) & (X <= max(xs)) & (Y >= min(ys)) & (Y <= max(ys))
        if not sel.any():
            continue
        m = np.zeros(X.shape, dtype=bool)
        m[sel] = L._inside(fp, X[sel], Y[sel])
        Z[m] = np.minimum(Z[m], b["base"] - 0.05)
    return Z


lay_out()
