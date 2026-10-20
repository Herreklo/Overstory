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
HEART = (-340.0, -480.0, 540.0, 330.0)  # x0, y0, x1, y1 of the fine ground


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
GULLY_STEPS = [(49.3, 0.0, 1.9), (49.3, 9.0, 1.9), (49.3, _yl - 1.6, 3.0), (49.1, _yl + 1.6, 3.0),
               (48.0, _yh - 6.0, 8.0), (46.5, _yh + 6.5, 8.0), (46.5, _yt - 1.4, 16.0), (46.5, _yt + 1.4, 16.0),
               (47.0, _yt + 18.0, 21.0), (40.0, 150.0, 32.0)]
_y2l, _y2h, _y2t, _y2c = lane_y(LOW, -110), lane_y(HIGH, -110), lane_y(TOP, -110), lane_y(CREST, -110)
TANNERS_STEPS = [(-110.0, 0.0, 1.9), (-110.0, _y2l - 1.6, 3.0), (-110.0, _y2l + 1.6, 3.0), (-110.0, _y2h - 1.6, 8.0),
                 (-110.0, _y2h + 1.6, 8.0), (-110.0, _y2t - 1.6, 16.0), (-110.0, _y2t + 1.6, 16.0), (-108.0, _y2c, 28.0)]
_y3h, _y3t, _y3c = lane_y(HIGH, 196), lane_y(TOP, 196), lane_y(CREST, 196)
BISHOPS_STEPS = [(196.0, 0.0, 2.0), (196.0, lane_y(LOW, 196) - 1.6, 3.0), (196.0, lane_y(LOW, 196) + 1.6, 3.0),
                 (196.0, _y3h - 1.6, 8.0), (196.0, _y3h + 1.6, 8.0), (196.0, _y3t - 1.6, 16.0),
                 (196.0, _y3t + 1.6, 16.0), (200.0, _y3c, 28.0)]
HUNDRED_STEPS = [(-246.0, 4.0, 2.0), (-262.0, 22.0, 9.0), (-252.0, 36.0, 9.0), (-268.0, 58.0, 18.0),
                 (-256.0, 72.0, 18.0), (-262.0, 96.0, 26.0)]

HARBOUR_ROW = [(-250.0, -8.0, 1.9), (150.0, -8.0, 1.9), (250.0, -15.0, 2.0), (300.0, -25.0, 2.1), (330.0, -40.0, 2.2)]

# The west shore: Barrel Quay on the Holm and the mainland, Holm Street above it, the Cut's two bridges
BARREL_QUAY = [(-196.0, -168.0, 1.9), (0.0, -162.0, 1.9), (38.0, -157.0, 1.9)]
BARREL_QUAY_SOUTH = [(56.0, -157.0, 1.9), (150.0, -147.0, 2.0), (240.0, -137.0, 2.1), (300.0, -131.0, 2.2), (334.0, -126.0, 2.4)]
HOLM_STREET = [(-214.0, -224.0, 7.0), (-120.0, -224.0, 8.0), (0.0, -222.0, 8.0), (60.0, -218.0, 8.0),
               (150.0, -204.0, 8.0), (236.0, -190.0, 6.4), (300.0, -170.0, 4.0), (346.0, -150.0, 2.6)]
CUT_BRIDGE_HIGH = [(30.0, -221.0, 8.0), (64.0, -219.0, 8.0)]   # Holm Street's stone bridge, six metres over the Cut
CUT_BRIDGE_LOW = [(30.0, -158.0, 2.2), (64.0, -156.0, 2.2)]    # the quay's footbridge, at the water
STAIR_LANES = []  # from Barrel Quay up to Holm Street, between the warehouses (filled in with the Holm below)

# Broad Street: the fire-break street, thirty metres wide, straight down from the Grid to the Basin
BROAD_STREET = [(250.0, -470.0, 21.0), (250.0, -300.0, 12.0), (250.0, -190.0, 6.4), (250.0, -138.0, 2.1)]
# The Crack: steps up through Watch Knoll's cleft from Holm Street to the Fire Watch
CRACK_STEPS = [(112.0, -292.0, 8.0), (136.0, -318.0, 18.0), (150.0, -336.0, 27.0), (152.0, -330.0, 30.0)]

MARKET_SQUARE = [(338.0, -132.0), (432.0, -158.0), (446.0, -34.0), (338.0, -40.0)]
MARKET_Z = 2.5

LANES = [
    dict(name="Harbour Row", width=15.0, pts=HARBOUR_ROW, kind="quay"),
    dict(name="Low Terrace", width=3.6, pts=LOW, kind="lane"),
    dict(name="High Terrace", width=3.4, pts=HIGH, kind="lane"),
    dict(name="Top Terrace", width=3.2, pts=TOP, kind="lane"),
    dict(name="Crest Lane", width=4.2, pts=CREST, kind="lane"),
    dict(name="Gully Steps", width=3.2, pts=GULLY_STEPS, kind="steps"),
    dict(name="Tanner's Steps", width=2.6, pts=TANNERS_STEPS, kind="steps"),
    dict(name="Bishop's Steps", width=3.0, pts=BISHOPS_STEPS, kind="steps"),
    dict(name="the Hundred Steps", width=2.2, pts=HUNDRED_STEPS, kind="steps"),
    dict(name="Barrel Quay", width=12.0, pts=BARREL_QUAY, kind="quay"),
    dict(name="Barrel Quay south", width=12.0, pts=BARREL_QUAY_SOUTH, kind="quay"),
    dict(name="Holm Street", width=6.0, pts=HOLM_STREET, kind="lane"),
    dict(name="Broad Street", width=30.0, pts=BROAD_STREET, kind="lane"),
    dict(name="the Crack", width=2.4, pts=CRACK_STEPS, kind="steps"),
]


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


def free(fp):
    for b in BUILDINGS:
        if _sat_overlap(fp, footprint(b, 0.3)):
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
        b = dict(name=f"{name} {k}", ox=ox, oy=oy, angle=angle, w=w, d=d, base=base, eave=eave, pitch=pitch,
                 roof=roof, role="row", low=None)
        fp = footprint(b)
        ok = free(fp) and clear_of_lanes(fp, skip=lane) and not any(
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


def lay_out():
    BUILDINGS.clear()
    YARDS.clear()
    rng = random.Random(SEED)

    # the corner (docs/experiments.md, LT1, the reset): A and B at the foot of Gully Steps on Harbour Row,
    # C beside the Landing, D on the knuckle, E closing the view where the steps meet Top Terrace
    building("A (104, café 1988)", 37.2, 0.0, 0.0, 9.8, 9.2, 1.9, 6.8, 54.0, "mansard", "corner")
    building("B (105)", 52.0, 0.0, 0.0, 9.4, 8.4, 1.9, 6.9, 12.0, "hip", "corner")
    building("C (1203, cooper 1879)", 41.4, LANDING[0][1] + 1.0, 90.0, 7.2, 7.4, 8.4, 4.4, 45.0, "gable", "corner")
    building("D (1107, empty since 1986)", 60.6, _yh - 2.0, 90.0, 7.6, 7.0, 12.65, 4.0, 46.0, "gable", "corner")
    building("E (304, 1826)", 50.0, _yt + 2.6, 90.0, 7.0, 6.8, 16.6, 4.0, 46.0, "eaves", "corner")
    YARDS.append(([(36.0, _yl + 2.2), (47.2, _yl + 2.2), (47.2, LANDING[0][1] - 0.6), (36.0, LANDING[0][1] - 0.6)], 5.2))

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
        b = dict(name=f"Harbour Row {len(BUILDINGS)}", ox=hx, oy=0.0, angle=0.0, w=w, d=d, base=1.9, eave=eave,
                 pitch=pitch, roof=roof, role="row", low=None)
        fp = footprint(b)
        if free(fp) and clear_of_lanes(fp, skip="Harbour Row"):
            BUILDINGS.append(b)
        hx += w + rng.choice([0.0, 0.0, 0.4, 0.8, 1.2])
    # round the head's curve to the square
    for x0, w in [(156.0, 11.0), (169.0, 10.0), (181.0, 12.0), (215.0, 10.0), (227.0, 11.0), (240.0, 10.0), (262.0, 12.0), (276.0, 10.0)]:
        oy = lane_y([(p[0], p[1] + 8.0, p[2]) for p in HARBOUR_ROW], x0 + w / 2) or 0.0
        b = dict(name=f"Harbour Row {len(BUILDINGS)}", ox=x0, oy=oy, angle=0.0, w=w, d=9.0, base=2.0,
                 eave=rng.uniform(6.2, 8.0), pitch=rng.uniform(38, 46), roof=rng.choice(["eaves", "eaves", "gable"]), role="row", low=None)
        fp = footprint(b)
        if free(fp) and clear_of_lanes(fp, skip="Harbour Row"):
            BUILDINGS.append(b)

    # the landmarks
    building("the cathedral, nave", 452.0, -42.0, 90.0, 60.0, 19.0, 9.6, 14.0, 50.0, "gable", "landmark")
    building("the cathedral, west tower", 452.0, -52.0, 90.0, 12.0, 19.0, 9.6, 34.0, 60.0, "tower", "landmark")
    building("the cathedral, choir", 456.0, 18.0, 90.0, 18.0, 11.0, 9.6, 12.0, 50.0, "gable", "landmark")
    building("the Fish Hall", 300.0, -128.0, -8.0, 34.0, 13.0, 2.4, 6.0, 30.0, "gable", "landmark")
    building("the Fire Watch", 147.0, -331.0, 0.0, 9.0, 9.0, 30.0, 15.0, 0.0, "tower", "landmark")
    building("the breakwater's light", -314.0, -114.0, 0.0, 4.0, 4.0, 2.5, 9.0, 0.0, "tower", "landmark")
    building("the beacon on the Pip", -372.0, -62.0, 0.0, 3.0, 3.0, 6.0, 7.0, 0.0, "tower", "landmark")
    building("the customs house", -224.0, -200.0, 90.0, 14.0, 9.0, 4.0, 5.2, 42.0, "eaves", "landmark")
    building("the harbour master", -206.0, -236.0, 90.0, 9.0, 8.0, 5.0, 4.6, 44.0, "gable", "landmark")
    building("the bandstand in Lookout Park", 6.0, 232.0, 0.0, 6.0, 6.0, 46.0, 3.0, 30.0, "hip", "landmark")
    building("the tunnel's portal", -258.0, 6.0, 0.0, 10.0, 3.0, 1.9, 6.0, 0.0, "flat", "landmark")

    # the Holm: Bryggen's double rows, gables to Barrel Quay, a private passage between each pair, then
    # Holm Street; a stair-lane up from the quay between every second pair
    STAIR_LANES.clear()
    x = -186.0
    i = 0
    while x < 26.0:
        for j, (dx, w) in enumerate([(0.0, 7.0), (10.6, 7.0)]):
            bx = x + dx
            if bx + w > 34.0:
                break
            yq = lane_y([(p[0], p[1], p[2]) for p in BARREL_QUAY], bx + w / 2) or -162.0
            front = yq - 6.0 - 0.4
            back = -217.5
            building(f"Holm warehouse {i}.{j}", bx + w, front, 180.0, w, front - back, 2.1,
                     rng.uniform(7.6, 9.4), rng.uniform(42, 50), "gable", "warehouse")
        if i % 2 == 1:
            sx = x + 18.4
            yq = lane_y(BARREL_QUAY, sx) or -162.0
            STAIR_LANES.append(dict(name=f"stair-lane {len(STAIR_LANES)}", width=2.2, kind="steps",
                                    pts=[(sx, yq - 6.2, 2.0), (sx, -220.4, 8.0)]))
        x += 21.0
        i += 1
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
    # the mainland's west quay: warehouses on Barrel Quay, houses and pubs above on Holm Street (St. John's)
    for k, x0 in enumerate([60, 72, 86, 98, 112, 126, 140, 154, 168, 182, 198, 212, 226]):
        w = rng.uniform(9.0, 12.0)
        yq = lane_y(BARREL_QUAY_SOUTH, x0 + w / 2) or -150.0
        front = yq - 6.4
        if 232 < x0 + w and x0 < 268:
            continue  # Broad Street
        building(f"Barrel Quay warehouse {k}", x0 + w, front, 180.0, w, rng.uniform(13.0, 17.0), 2.2,
                 rng.uniform(7.2, 9.6), rng.uniform(40, 48), "gable", "warehouse")
    for k, x0 in enumerate(range(62, 228, 11)):
        if 228 < x0 + 10 and x0 < 268:
            continue
        yh = lane_y(HOLM_STREET, x0 + 5) or -205.0
        w = rng.uniform(8.0, 10.4)
        b = dict(name=f"Holm Street south {k}", ox=x0 + w, oy=yh - 3.4, angle=180.0, w=w, d=rng.uniform(8.0, 10.0),
                 base=8.2, eave=rng.uniform(5.0, 7.0), pitch=rng.uniform(40, 48), roof=rng.choice(["eaves", "gable"]),
                 role="row", low=None)
        if free(footprint(b)) and clear_of_lanes(footprint(b)):
            BUILDINGS.append(b)
    for sx in (94.0, 166.0, 214.0):
        yq = lane_y(BARREL_QUAY_SOUTH, sx) or -150.0
        STAIR_LANES.append(dict(name=f"stair-lane {len(STAIR_LANES)}", width=2.2, kind="steps",
                                pts=[(sx, yq - 6.4, 2.1), (sx, (lane_y(HOLM_STREET, sx) or -200.0) + 3.2, 8.0)]))
    LANES[:] = [l for l in LANES if not l["name"].startswith("stair-lane")] + STAIR_LANES

    # Market Square's edges: an irregular room, streets entering at its corners
    for name, ox, oy, a, w, d, eave in [("the square's south side 1", 444.0, -150.0, 90.0, 22.0, 12.0, 9.0),
                                        ("the square's south side 2", 448.0, -124.0, 90.0, 16.0, 12.0, 10.0),
                                        ("the square's south side 3", 450.0, -104.0, 90.0, 24.0, 12.0, 8.6),
                                        ("the bank", 360.0, -150.0, 0.0, 26.0, 14.0, 11.0),
                                        ("the hotel", 400.0, -168.0, 0.0, 30.0, 16.0, 13.0)]:
        building(name, ox, oy, a, w, d, 2.6, eave, 36.0, "hip", "landmark")

    # the old town's rows along its terraces, uphill and downhill sides
    keep = [LANDING, [(36.0, _yl + 1.0), (47.6, _yl + 1.0), (47.6, LANDING[0][1]), (36.0, LANDING[0][1])],
            [(53.0, _yh - 9.0), (68.0, _yh - 9.0), (68.0, _yh + 10.0), (53.0, _yh + 10.0)]]
    for lane, z in [("Low Terrace", 3.0), ("High Terrace", 8.0), ("Top Terrace", 16.0)]:
        pts = next(l for l in LANES if l["name"] == lane)["pts"]
        row(lane, +1, 2.0, length(pts) - 4, rng, name=f"{lane} up", keep_out=keep)
        row(lane, -1, 3.0, length(pts) - 4, rng, name=f"{lane} down", keep_out=keep)
    row("Crest Lane", -1, 4.0, length(CREST) - 6, rng, name="Crest Lane down", keep_out=keep)
    row("Crest Lane", +1, 4.0, length(CREST) - 6, rng, grain="villa", name="the Heights", keep_out=keep)


def carve(X, Y, Z):
    """Cut the heart's lanes, stairs, quays, squares, yards and house pads into the ground (arrays, in place)."""
    rock = np.zeros(X.shape, dtype=bool)
    for o in L.OUTCROPS:
        rock |= np.hypot((X - o["x"]) / o["sx"], (Y - o["y"]) / o["sy"]) < o["r"]
    water = L.water_mask(X, Y)
    for lane in LANES:
        d, zl = L._line_dist_z(X, Y, [(p[0], p[1], p[2]) for p in lane["pts"]])
        hw = lane["width"] / 2 + 0.3
        on = (d <= hw) & ~water
        Z[on] = zl[on]
        bank = (d > hw) & (d < hw + 14.0) & ~water
        lo = zl - (d - hw) * 0.75
        hi = zl + (d - hw) * 0.95
        Zb = np.where(rock, np.maximum(Z, lo), np.minimum(np.maximum(Z, lo), hi))
        Z[bank] = Zb[bank]
    sq = L._inside(MARKET_SQUARE, X, Y)
    Z[sq] = MARKET_Z
    lz = L._inside(LANDING, X, Y)
    Z[lz] = LANDING_Z
    for poly, z in YARDS:
        m = L._inside(poly, X, Y)
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
