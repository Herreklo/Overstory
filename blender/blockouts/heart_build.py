"""Build the heart in clay in Blender from heart_layout, and export it to Unity.

    blender -b --factory-startup --python blender/blockouts/heart_build.py -- <unity project dir>

or, in a running Blender: runpy.run_path("blender/blockouts/heart_build.py", run_name="__main__").

What is built (all grey masses; parts come later, one at a time):
- the ground: 1.5 m in the heart with every lane, quay, square, yard and pad cut in; 6 m round it; 60 m out to
  seven kilometres, the Roads open to the north;
- the water, and the Mere;
- stairs as steps; retaining walls and parapets where a lane is cut into the slope or stands above it;
- every building as masses (plinth to the lowest ground, body, roof, chimney), the landmarks shaped by hand;
- the space between the buildings: yard walls, sheds, stoops, bollards, quay steps, boats, lamps, benches;
- the landmarks beyond the heart (the platform in the fjord, the High Bridge, the cannery's chimney, the
  monastery's ruin, the wreck, the cranes, the funicular, the water tower) and quiet context massing by use.

Every face carries a "bake" colour (sky, ground, openness) from its facing, as the street shader expects.
Each category is one mesh, exported to <unity>/Assets/Art/Blockout/heart/<name>.fbx.
"""

import math
import os
import random
import sys

import bpy
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import centre_land as L  # noqa: E402
import heart_layout as H  # noqa: E402

ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
COLLECTION = "heart"


class Mesh:
    """Vertices and faces gathered for one category, made into one object at the end."""

    def __init__(self, name):
        self.name = name
        self.v = []
        self.f = []

    def quad(self, a, b, c, d):
        n = len(self.v)
        self.v += [a, b, c, d]
        self.f.append((n, n + 1, n + 2, n + 3))

    def tri(self, a, b, c):
        n = len(self.v)
        self.v += [a, b, c]
        self.f.append((n, n + 1, n + 2))

    def box(self, corners, z0, z1):
        """A prism over a convex outline (counter-clockwise seen from above), from z0 to z1."""
        k = len(corners)
        n = len(self.v)
        self.v += [(x, y, z0) for x, y in corners] + [(x, y, z1) for x, y in corners]
        self.f.append(tuple(range(n + k - 1, n - 1, -1)))
        self.f.append(tuple(range(n + k, n + 2 * k)))
        for i in range(k):
            j = (i + 1) % k
            self.f.append((n + i, n + j, n + k + j, n + k + i))

    def obox(self, x, y, a, l, w, z0, z1):
        """An oriented box centred at x, y: length l along the angle a, width w across it."""
        c, s = math.cos(math.radians(a)), math.sin(math.radians(a))
        pts = [(-l / 2, -w / 2), (l / 2, -w / 2), (l / 2, w / 2), (-l / 2, w / 2)]
        self.box([(x + u * c - v * s, y + u * s + v * c) for u, v in pts], z0, z1)


def ccw(pts):
    area = sum(x1 * y2 - x2 * y1 for (x1, y1), (x2, y2) in zip(pts, pts[1:] + pts[:1]))
    return pts if area > 0 else list(reversed(pts))


# -- the ground -----------------------------------------------------------------------------------------------------


def grid(x0, y0, x1, y1, step):
    xs = np.arange(x0, x1 + step / 2, step)
    ys = np.arange(y0, y1 + step / 2, step)
    return np.meshgrid(xs, ys, indexing="ij")


def ground_mesh(m, X, Y, Z, skip=None):
    nx, ny = X.shape
    idx = np.arange(nx * ny).reshape(nx, ny)
    base = len(m.v)
    m.v += list(zip(X.ravel().tolist(), Y.ravel().tolist(), Z.ravel().tolist()))
    a = idx[:-1, :-1].ravel()
    b = idx[1:, :-1].ravel()
    c = idx[1:, 1:].ravel()
    d = idx[:-1, 1:].ravel()
    keep = np.ones(a.shape, dtype=bool)
    if skip is not None:
        cx = (X[:-1, :-1] + X[1:, 1:]).ravel() / 2
        cy = (Y[:-1, :-1] + Y[1:, 1:]).ravel() / 2
        keep = ~skip(cx, cy)
    for qa, qb, qc, qd in zip(a[keep], b[keep], c[keep], d[keep]):
        m.f.append((base + int(qa), base + int(qb), base + int(qc), base + int(qd)))


def skirt(m, X, Y, Z, drop=5.0):
    """A skirt round a grid's edge, down into the coarser ground, so no seam shows."""
    for line in (list(zip(X[0], Y[0], Z[0])), list(zip(X[-1], Y[-1], Z[-1])),
                 list(zip(X[:, 0], Y[:, 0], Z[:, 0])), list(zip(X[:, -1], Y[:, -1], Z[:, -1]))):
        for (x1, y1, z1), (x2, y2, z2) in zip(line, line[1:]):
            m.quad((x1, y1, z1), (x2, y2, z2), (x2, y2, z2 - drop), (x1, y1, z1 - drop))
            m.quad((x1, y1, z1 - drop), (x2, y2, z2 - drop), (x2, y2, z2), (x1, y1, z1))


HX0, HY0, HX1, HY1 = H.HEART
RX0, RY0, RX1, RY1 = (-1300.0, -1400.0, 1800.0, 1700.0)


def far_heights(X, Y):
    Z = L.heights(X, Y)
    open_sea = (X < -1350.0) & ~(np.hypot(X + 2100.0, Y - 1500.0) < 0)  # the Roads run on north to the fjord
    return np.where(open_sea, -6.0, Z)


# -- buildings ----------------------------------------------------------------------------------------------------


def building_mesh(m, b, ground):
    W, D, z0 = b["w"], b["d"], b["base"]
    c, s = math.cos(math.radians(b["angle"])), math.sin(math.radians(b["angle"]))
    to = lambda x, y: (b["ox"] + x * c - y * s, b["oy"] + x * s + y * c)
    low = min(ground(*to(x, y)) for x in (0, W / 2, W) for y in (0, D / 2, D))
    parts = []  # (local outline, z0, z1)

    def lbox(x0, y0, x1, y1, za, zb):
        m.box([to(x0, y0), to(x1, y0), to(x1, y1), to(x0, y1)], za, zb)

    if low < z0 - 0.1:
        lbox(0.05, 0.05, W - 0.05, D - 0.05, low - 0.4, z0)  # the plinth takes up the slope
    ze = z0 + b["eave"]
    roof = b["roof"]
    lbox(0, 0, W, D, z0, ze)
    o = 0.45
    if roof == "flat":
        lbox(-0.15, -0.15, W + 0.15, D + 0.15, ze, ze + 0.5)
        return
    if roof == "tower":
        if b["name"].startswith("the cathedral"):
            cap = b["eave"] * 1.1   # a tall spire
        else:
            cap = min(W, D) * 0.45
        lbox(-0.3, -0.3, W + 0.3, D + 0.3, ze, ze + 0.6)
        n = len(m.v)
        m.v += [(*to(-0.3, -0.3), ze + 0.6), (*to(W + 0.3, -0.3), ze + 0.6), (*to(W + 0.3, D + 0.3), ze + 0.6),
                (*to(-0.3, D + 0.3), ze + 0.6), (*to(W / 2, D / 2), ze + 0.6 + cap)]
        m.f += [(n, n + 1, n + 4), (n + 1, n + 2, n + 4), (n + 2, n + 3, n + 4), (n + 3, n, n + 4)]
        return
    if roof == "hip":
        inset = min(W, D) / 2
        rise = math.tan(math.radians(b["pitch"])) * inset
        n = len(m.v)
        m.v += [(*to(-o, -o), ze), (*to(W + o, -o), ze), (*to(W + o, D + o), ze), (*to(-o, D + o), ze),
                (*to(inset, D / 2), ze + rise), (*to(W - inset, D / 2), ze + rise)]
        m.f += [(n, n + 1, n + 5, n + 4), (n + 1, n + 2, n + 5), (n + 2, n + 3, n + 4, n + 5), (n + 3, n, n + 4), (n + 3, n + 2, n + 1, n)]
        return
    along = roof in ("eaves", "mansard")
    span = D if along else W
    rise = math.tan(math.radians(b["pitch"])) * (span / 2 + o)
    n = len(m.v)
    if roof == "mansard":  # a steep lower slope and a shallow top, the gambrel of the jugend house
        k = 0.32 * span
        h1 = rise * 0.75
        h2 = rise * 0.95
        m.v += [(*to(-o * 0.6, -o), ze), (*to(W + o * 0.6, -o), ze), (*to(W + o * 0.6, k), ze + h1), (*to(-o * 0.6, k), ze + h1),
                (*to(-o * 0.6, D / 2), ze + h2), (*to(W + o * 0.6, D / 2), ze + h2),
                (*to(-o * 0.6, D - k), ze + h1), (*to(W + o * 0.6, D - k), ze + h1), (*to(-o * 0.6, D + o), ze), (*to(W + o * 0.6, D + o), ze)]
        m.f += [(n, n + 1, n + 2, n + 3), (n + 3, n + 2, n + 5, n + 4), (n + 4, n + 5, n + 7, n + 6), (n + 6, n + 7, n + 9, n + 8),
                (n, n + 3, n + 4, n + 6, n + 8), (n + 1, n + 9, n + 7, n + 5, n + 2)]
    elif along:
        m.v += [(*to(-o * 0.6, -o), ze), (*to(W + o * 0.6, -o), ze), (*to(W + o * 0.6, D + o), ze), (*to(-o * 0.6, D + o), ze),
                (*to(-o * 0.6, D / 2), ze + rise), (*to(W + o * 0.6, D / 2), ze + rise)]
        m.f += [(n, n + 1, n + 5, n + 4), (n + 2, n + 3, n + 4, n + 5), (n + 1, n + 2, n + 5), (n + 3, n, n + 4), (n + 3, n + 2, n + 1, n)]
    else:
        m.v += [(*to(-o, -o * 0.6), ze), (*to(W + o, -o * 0.6), ze), (*to(W + o, D + o * 0.6), ze), (*to(-o, D + o * 0.6), ze),
                (*to(W / 2, -o * 0.6), ze + rise), (*to(W / 2, D + o * 0.6), ze + rise)]
        m.f += [(n + 1, n + 2, n + 5, n + 4), (n + 3, n, n + 4, n + 5), (n, n + 1, n + 4), (n + 2, n + 3, n + 5), (n + 3, n + 2, n + 1, n)]
    # the gable walls up into the roof
    n = len(m.v)
    if along:
        m.v += [(*to(0, 0), ze), (*to(0, D), ze), (*to(0, D / 2), ze + rise - 0.2), (*to(W, 0), ze), (*to(W, D), ze), (*to(W, D / 2), ze + rise - 0.2)]
        m.f += [(n, n + 2, n + 1), (n + 3, n + 4, n + 5)]
    else:
        m.v += [(*to(0, 0), ze), (*to(W, 0), ze), (*to(W / 2, 0), ze + rise - 0.2), (*to(0, D), ze), (*to(W, D), ze), (*to(W / 2, D), ze + rise - 0.2)]
        m.f += [(n, n + 1, n + 2), (n + 3, n + 5, n + 4)]
    if b["role"] == "warehouse" and not along:
        # the hoist beam in the gable, over the loading doors
        lbox(W / 2 - 0.25, -1.2, W / 2 + 0.25, 0.0, ze + rise * 0.62, ze + rise * 0.72)
        return
    if b["role"] in ("row", "corner", "warehouse") and b["name"] != "the Fish Hall":
        cx = W * 0.62 if along else W / 2
        cy = D / 2 if along else D * 0.62
        lbox(cx - 0.35, cy - 0.35, cx + 0.35, cy + 0.35, ze + rise * 0.4, ze + rise + 1.1)


def detail_mesh(m, d):
    k, x, y, z, l, w, h, a = d["kind"], d["x"], d["y"], d["z"], d["l"], d["w"], d["h"], d["a"]
    if k == "lantern":
        m.obox(x, y, a, 0.18, 0.18, z, z + h - 0.6)
        m.obox(x, y, a, 0.5, 0.5, z + h - 0.6, z + h)
    elif k == "pole":
        m.obox(x, y, a, 0.24, 0.24, z, z + h)
        m.obox(x + 0.8 * math.sin(math.radians(a)), y - 0.8 * math.cos(math.radians(a)), a + 90, 1.8, 0.4, z + h - 0.3, z + h)
    elif k == "boat" or k == "tall ship":
        c, s = math.cos(math.radians(a)), math.sin(math.radians(a))
        pts = [(-l / 2, -w / 2), (l * 0.25, -w / 2), (l / 2, 0.0), (l * 0.25, w / 2), (-l / 2, w / 2)]
        m.box(ccw([(x + u * c - v * s, y + u * s + v * c) for u, v in pts]), z, z + h)
    elif k == "quay steps":
        for i in range(4):
            m.obox(x, y, a, l, w, z + i * 0.6, z + (i + 1) * 0.6)
    elif k == "line":
        m.obox(x, y, a, l, 0.05, z, z + 0.05)
    else:
        m.obox(x, y, a, l, w, z, z + h)


def far_mesh(m, f, ground):
    k = f["kind"]
    gz = ground(f["x"], f["y"])
    if k == "chimney":
        m.box(ccw([(f["x"] - 2, f["y"] - 2), (f["x"] + 2, f["y"] - 2), (f["x"] + 2, f["y"] + 2), (f["x"] - 2, f["y"] + 2)]), gz, gz + f["h"])
    elif k in ("mast",):
        m.obox(f["x"], f["y"], 20.0, f["w"], f["w"], H.SEA - 2.0, H.SEA + f["h"])
    elif k == "bow":
        m.box(ccw([(f["x"] - 4, f["y"] - 1.5), (f["x"] + 2, f["y"] - 1.5), (f["x"] + 4, f["y"]), (f["x"] + 2, f["y"] + 1.5), (f["x"] - 4, f["y"] + 1.5)]), H.SEA - 1.5, H.SEA + f["h"])
    elif k == "condeep":
        # a base of cells and three shafts rising out of it, under construction
        for i in range(-2, 3):
            for j in range(-2, 3):
                if abs(i) + abs(j) > 3:
                    continue
                cx, cy = f["x"] + i * 20.0 + (10.0 if j % 2 else 0.0), f["y"] + j * 17.3
                ring = [(cx + 10 * math.cos(t * math.pi / 4), cy + 10 * math.sin(t * math.pi / 4)) for t in range(8)]
                m.box(ring, H.SEA - 20.0, H.SEA + 36.0)
        for (dx, dy) in ((-20.0, -12.0), (20.0, -12.0), (0.0, 22.0)):
            cx, cy = f["x"] + dx, f["y"] + dy
            for seg in range(6):
                r = 7.0 - seg * 0.5
                ring = [(cx + r * math.cos(t * math.pi / 4), cy + r * math.sin(t * math.pi / 4)) for t in range(8)]
                m.box(ring, H.SEA + 36.0 + seg * 19.0, H.SEA + 36.0 + (seg + 1) * 19.0)
    elif k == "bridge":
        x1, y1, x2, y2 = f["x"], f["y"], f["x2"], f["y2"]
        L_ = math.hypot(x2 - x1, y2 - y1)
        a = math.degrees(math.atan2(y2 - y1, x2 - x1))
        n = 80
        for i in range(n):
            t0, t1 = i / n, (i + 1) / n
            mx, my = x1 + (x2 - x1) * (t0 + t1) / 2, y1 + (y2 - y1) * (t0 + t1) / 2
            arch = f["h"] * math.sin(math.pi * (t0 + t1) / 2) ** 0.35  # a high deck, lower at the ends
            m.obox(mx, my, a, L_ / n + 1.2, f["w"], H.SEA + arch - 2.6, H.SEA + arch)
        for t in (0.33, 0.67):
            px, py = x1 + (x2 - x1) * t, y1 + (y2 - y1) * t
            arch = f["h"] * math.sin(math.pi * t) ** 0.35
            m.obox(px, py, a, 6.0, f["w"] + 6.0, H.SEA - 2.0, H.SEA + arch + 18.0)  # the towers
    elif k == "ruin":
        x, y = f["x"], f["y"]
        for (dx, dy, l, w) in ((0, 0, 30, 0.9), (0, 10, 30, 0.9), (-15, 5, 0.9, 10), (15, 5, 0.9, 10), (0, -12, 20, 0.8), (-10, -6, 0.8, 12)):
            m.obox(x + dx, y + dy, 0.0, l, w, gz, gz + f["h"] * (0.6 + 0.4 * ((dx * 7 + dy) % 3) / 2))
    elif k == "cranes":
        for i, (dx, dy, a, h) in enumerate([(0.0, 0.0, 20.0, f["h"]), (34.0, -16.0, -35.0, f["h"] * 0.85), (70.0, 6.0, 70.0, f["h"] * 1.1)]):
            cx, cy = f["x"] + dx, f["y"] + dy
            c, s_ = math.cos(math.radians(a)), math.sin(math.radians(a))
            m.obox(cx, cy, a, 2.4, 2.4, gz, gz + h)                                  # the tower
            m.obox(cx + c * 12.0, cy + s_ * 12.0, a, 30.0, 1.4, gz + h - 1.6, gz + h)    # the jib
            m.obox(cx - c * 6.0, cy - s_ * 6.0, a, 10.0, 2.0, gz + h - 2.4, gz + h)      # the counter-jib
            m.obox(cx - c * 9.5, cy - s_ * 9.5, a, 3.0, 2.6, gz + h - 5.0, gz + h - 2.4) # its weight
            m.obox(cx, cy, a, 1.0, 1.0, gz + h, gz + h + 5.0)                            # the top mast
    elif k == "funicular":
        x1, y1, x2, y2 = f["x"], f["y"], f["x2"], f["y2"]
        n = 30
        a = math.degrees(math.atan2(y2 - y1, x2 - x1))
        for i in range(n):
            t = (i + 0.5) / n
            px, py = x1 + (x2 - x1) * t, y1 + (y2 - y1) * t
            m.obox(px, py, a, math.hypot(x2 - x1, y2 - y1) / n + 0.3, 3.0, ground(px, py) + 0.2, ground(px, py) + 1.0)
        for t in (0.3, 0.7):
            px, py = x1 + (x2 - x1) * t, y1 + (y2 - y1) * t
            m.obox(px, py, a, 7.0, 2.8, ground(px, py) + 1.0, ground(px, py) + 4.0)
    elif k == "tower":
        r = f["w"] / 2
        ring = [(f["x"] + r * math.cos(t * math.pi / 4), f["y"] + r * math.sin(t * math.pi / 4)) for t in range(8)]
        m.box(ring, gz, gz + f["h"])
    elif k == "block":
        m.obox(f["x"], f["y"], 0.0, f["w"], f["w"] * 0.6, gz, gz + f["h"])


# -- context massing outside the hand-laid heart ---------------------------------------------------------------------

HAND = {"the Holm: pubs, a club", "Holm Street", "Watch Knoll and the Fire Watch",
        "Market Square, the cathedral, the Fish Hall", "Harbour Row", "the old town on Herring Hill",
        "the Heights and Lookout Park", "the Grid", "the Bluff and the Hundred Steps",
        "the cathedral school and the bishop's garden"}
SPACING = {"home": 15.0, "civic": 40.0, "work": 42.0, "farm": 150.0}


def context_mesh(m, ground):
    rng = random.Random(H.SEED + 7)
    occupied = [H.footprint(b, 1.0) for b in H.BUILDINGS]
    boxes = [(min(p[0] for p in fp), min(p[1] for p in fp), max(p[0] for p in fp), max(p[1] for p in fp)) for fp in occupied]
    count = 0
    for name, kind, poly in L.USES:
        if name in HAND or kind not in SPACING:
            continue
        sp = SPACING[kind]
        xs = [p[0] for p in poly]
        ys = [p[1] for p in poly]
        X, Y = np.meshgrid(np.arange(min(xs), max(xs), sp), np.arange(min(ys), max(ys), sp), indexing="ij")
        X = X + np.array([[rng.uniform(-sp * 0.25, sp * 0.25) for _ in range(X.shape[1])] for _ in range(X.shape[0])])
        Y = Y + np.array([[rng.uniform(-sp * 0.25, sp * 0.25) for _ in range(X.shape[1])] for _ in range(X.shape[0])])
        inside = L._inside(poly, X, Y) & ~L.is_water(X, Y)
        for x, y in zip(X[inside].tolist(), Y[inside].tolist()):
            if any(b0 <= x <= b2 and b1 <= y <= b3 for b0, b1, b2, b3 in boxes):
                continue
            if HX0 + 20 < x < HX1 - 20 and HY0 + 20 < y < HY1 - 20 and name in HAND:
                continue
            if rng.random() < 0.12:
                continue  # a gap, a yard, a garden
            a = rng.uniform(-10, 10)
            z = ground(x, y)
            if kind == "home":
                b = dict(name="context", ox=x, oy=y, angle=a, w=rng.uniform(8, 11), d=rng.uniform(7, 9), base=z + 0.2,
                         eave=rng.choice([4.4, 5.8, 6.4]), pitch=rng.uniform(36, 46), roof=rng.choice(["eaves", "gable"]), role="context")
                building_mesh(m, b, ground)
            elif kind == "civic":
                b = dict(name="context", ox=x, oy=y, angle=a, w=rng.uniform(20, 30), d=rng.uniform(13, 18), base=z + 0.2,
                         eave=rng.uniform(11, 20), pitch=0.0, roof="flat", role="context")
                building_mesh(m, b, ground)
            elif kind == "work":
                b = dict(name="context", ox=x, oy=y, angle=a, w=rng.uniform(18, 28), d=rng.uniform(12, 16), base=z + 0.2,
                         eave=rng.uniform(6, 9), pitch=22.0, roof="gable", role="context")
                building_mesh(m, b, ground)
            elif kind == "farm":
                for (dx, dy, w, d, e) in ((0, 0, 12, 9, 5.0), (18, 6, 24, 12, 6.5)):
                    b = dict(name="context", ox=x + dx, oy=y + dy, angle=a, w=w, d=d, base=ground(x + dx, y + dy) + 0.2,
                             eave=e, pitch=40.0, roof="eaves", role="context")
                    building_mesh(m, b, ground)
            count += 1
    return count


# -- assembling and exporting -------------------------------------------------------------------------------------


def make_object(m, coll):
    me = bpy.data.meshes.new(m.name)
    me.from_pydata(m.v, [], m.f)
    me.validate()
    me.update()
    # what each face sees, from its facing: up-facing faces see sky, down-facing see ground
    normals = np.zeros(len(me.polygons) * 3)
    me.polygons.foreach_get("normal", normals)
    nz = normals.reshape(-1, 3)[:, 2]
    attr = me.color_attributes.new("bake", "FLOAT_COLOR", "CORNER")
    loop_poly = np.zeros(len(me.loops), dtype=np.int64)
    for p in me.polygons:
        loop_poly[p.loop_start:p.loop_start + p.loop_total] = p.index
    sky = 0.5 + 0.5 * nz[loop_poly]
    cols = np.stack([sky, 1.0 - sky, np.ones_like(sky), np.ones_like(sky)], -1).astype(np.float32)
    attr.data.foreach_set("color", cols.ravel())
    me.color_attributes.active_color = attr
    ob = bpy.data.objects.new(m.name, me)
    coll.objects.link(ob)
    return ob


def export_fbx(ob, path):
    bpy.ops.object.select_all(action="DESELECT")
    ob.select_set(True)
    bpy.context.view_layer.objects.active = ob
    os.makedirs(os.path.dirname(path), exist_ok=True)
    bpy.ops.export_scene.fbx(filepath=path, use_selection=True, object_types={"MESH"}, axis_forward="Z", axis_up="Y",
                             bake_space_transform=True, apply_unit_scale=True, apply_scale_options="FBX_SCALE_ALL",
                             mesh_smooth_type="OFF", colors_type="LINEAR", use_mesh_modifiers=True, add_leaf_bones=False,
                             bake_anim=False, path_mode="STRIP", embed_textures=False)


def build(unity=None):
    scene = bpy.context.scene
    old = bpy.data.collections.get(COLLECTION)
    if old:
        for ob in list(old.objects):
            bpy.data.objects.remove(ob, do_unlink=True)
        bpy.data.collections.remove(old)
    for me in [x for x in bpy.data.meshes if x.users == 0]:
        bpy.data.meshes.remove(me)
    coll = bpy.data.collections.new(COLLECTION)
    scene.collection.children.link(coll)
    report = {}

    # the ground: the heart, carved; the ring round it; the far land and the Roads
    X, Y = grid(HX0, HY0, HX1, HY1, 1.5)
    Zh = H.carve(X, Y, L.heights(X, Y))
    heart_ground = lambda x, y: float(_sample(X, Y, Zh, x, y))
    g = Mesh("ground_heart")
    ground_mesh(g, X, Y, Zh)
    skirt(g, X, Y, Zh)
    RX, RY = grid(RX0, RY0, RX1, RY1, 6.0)
    Zr = L.heights(RX, RY)
    r = Mesh("ground_ring")
    ground_mesh(r, RX, RY, Zr, skip=lambda cx, cy: (cx > HX0 + 3) & (cx < HX1 - 3) & (cy > HY0 + 3) & (cy < HY1 - 3))
    skirt(r, RX, RY, Zr)
    FX, FY = grid(-7000.0, -7000.0, 7000.0, 7000.0, 60.0)
    Zf = far_heights(FX, FY)
    fm = Mesh("ground_far")
    ground_mesh(fm, FX, FY, Zf, skip=lambda cx, cy: (cx > RX0 + 30) & (cx < RX1 - 30) & (cy > RY0 + 30) & (cy < RY1 - 30))

    def ground(x, y):
        if HX0 <= x <= HX1 and HY0 <= y <= HY1:
            return heart_ground(x, y)
        return float(L.heights(np.array([x]), np.array([y]))[0])

    water = Mesh("water")
    water.quad((-7000, -7000, H.SEA), (7000, -7000, H.SEA), (7000, 7000, H.SEA), (-7000, 7000, H.SEA))
    lake = Mesh("water_mere")
    lake.box(ccw([(p[0], p[1]) for p in L.LAKE_LINE]), L.LAKE_LEVEL - 0.5, L.LAKE_LEVEL)

    # stairs as steps; walls where a lane is cut into the slope or stands over it
    steps = Mesh("steps")
    walls = Mesh("walls")
    for lane in H.LANES:
        pts = lane["pts"]
        hw = lane["width"] / 2
        if lane["kind"] == "steps":
            for (ax, ay, az), (bx, by, bz) in zip(pts, pts[1:]):
                run = math.hypot(bx - ax, by - ay)
                if run < 0.1:
                    continue
                a = math.degrees(math.atan2(by - ay, bx - ax))
                rise = bz - az
                if abs(rise) / run < 0.06:
                    continue
                n = max(1, int(abs(rise) / 0.17))
                for i in range(n):
                    t = (i + 0.5) / n
                    top = az + rise * ((i + 1) / n if rise > 0 else i / n) + 0.02
                    steps.obox(ax + (bx - ax) * t, ay + (by - ay) * t, a, run / n + 0.02, lane["width"], top - abs(rise) / n - 0.3, top)
        if lane["kind"] in ("lane", "steps") and lane["width"] <= 8.0:
            s, total = 1.0, H.length(pts)
            while s < total - 1.0:
                p = H.at_s(pts, s)
                if p is None:
                    break
                x, y, z, a = p
                nx, ny = -math.sin(math.radians(a)), math.cos(math.radians(a))
                for side in (1, -1):
                    ex, ey = x + nx * (hw + 0.3) * side, y + ny * (hw + 0.3) * side
                    out = ground(x + nx * (hw + 3.0) * side, y + ny * (hw + 3.0) * side)
                    if out - z > 1.0:
                        walls.obox(ex, ey, a, 2.05, 0.45, z - 0.3, min(out, z + 4.0))
                    elif z - out > 1.0:
                        walls.obox(ex, ey, a, 2.05, 0.45, out - 0.3, z + 0.9)
                s += 2.0
    # walls round the Landing and the small places where they stand over the ground
    for poly, z in [(H.LANDING, H.LANDING_Z)] + [(p, z) for _, p, z in H.SMALL_PLACES] + H.YARDS:
        for (x1, y1), (x2, y2) in zip(poly, poly[1:] + poly[:1]):
            mx, my = (x1 + x2) / 2, (y1 + y2) / 2
            out = ground(mx + (mx - sum(p[0] for p in poly) / len(poly)) * 0.2, my + (my - sum(p[1] for p in poly) / len(poly)) * 0.2)
            if z - out > 0.8:
                walls.obox(mx, my, math.degrees(math.atan2(y2 - y1, x2 - x1)), math.hypot(x2 - x1, y2 - y1), 0.45, out - 0.3, z + 0.9)

    corner = Mesh("buildings_corner")
    houses = Mesh("buildings_heart")
    marks = Mesh("landmarks")
    for b in H.BUILDINGS:
        building_mesh(corner if b["role"] == "corner" else marks if b["role"] == "landmark" else houses, b, ground)
    det = Mesh("details")
    for d in H.DETAILS:
        detail_mesh(det, d)
    far = Mesh("landmarks_far")
    for f in H.FAR:
        far_mesh(far, f, ground)
    ctx = Mesh("context")
    report["context buildings"] = context_mesh(ctx, ground)

    meshes = [g, r, fm, water, lake, steps, walls, corner, houses, marks, det, far, ctx]
    objs = [make_object(m, coll) for m in meshes]
    report.update({m.name: len(m.f) for m in meshes})
    if unity:
        out = os.path.join(unity, "Assets", "Art", "Blockout", "heart")
        for ob in objs:
            export_fbx(ob, os.path.join(out, f"{ob.name}.fbx"))
        report["exported to"] = out
    return report


def _sample(X, Y, Z, x, y):
    step = X[1, 0] - X[0, 0]
    u = min(max((x - X[0, 0]) / step, 0), X.shape[0] - 1.001)
    v = min(max((y - Y[0, 0]) / step, 0), X.shape[1] - 1.001)
    i, j = int(u), int(v)
    fu, fv = u - i, v - j
    a = Z[i, j] + (Z[i + 1, j] - Z[i, j]) * fu
    b = Z[i, j + 1] + (Z[i + 1, j + 1] - Z[i, j + 1]) * fu
    return a + (b - a) * fv


if __name__ == "__main__":
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    unity = argv[0] if argv else os.path.join(ROOT, "unity")
    print(build(unity))
