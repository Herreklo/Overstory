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

Every face carries a "bake" colour (sky, ground, openness) from its facing, as the street shader expects, and UVs
on one swatch of the shared palette: in clay every surface is one grey, but the palette still says which faces are
glass, which glow and as what (a lit window, a lamp of its era), and which ground is paved, where puddles lie.
Each category is one mesh, exported to <unity>/Assets/Art/Blockout/heart/<name>.fbx, with the palette's maps and the
lamps as lights (lights.json: where each lamp stands and what kind it is).
"""

import json
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

sys.path.insert(0, os.path.join(HERE, "..", "generators"))
import palette  # noqa: E402

ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
COLLECTION = "heart"


class Mesh:
    """Vertices and faces gathered for one category, made into one object at the end."""

    def __init__(self, name, swatch="render_white"):
        self.name = name
        self.v = []
        self.f = []
        self.marks = [(0, swatch)]  # (first face, swatch or a list of swatches face by face) as they were set

    def paint(self, swatch):
        """Every face added from now on sits on this swatch of the palette."""
        self.marks.append((len(self.f), swatch))

    def swatches(self):
        """The swatch of each face."""
        out = [None] * len(self.f)
        for k, (start, sw) in enumerate(self.marks):
            end = self.marks[k + 1][0] if k + 1 < len(self.marks) else len(self.f)
            if isinstance(sw, str):
                out[start:end] = [sw] * (end - start)
            else:
                out[start:start + len(sw)] = sw
                if start + len(sw) < end:
                    out[start + len(sw):end] = [sw[-1]] * (end - start - len(sw))
        return out

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


def ground_mesh(m, X, Y, Z, skip=None, paving=None):
    """A grid of ground; paving(cx, cy) names each face's swatch (else plain ground)."""
    nx, ny = X.shape
    idx = np.arange(nx * ny).reshape(nx, ny)
    base = len(m.v)
    m.v += list(zip(X.ravel().tolist(), Y.ravel().tolist(), Z.ravel().tolist()))
    a = idx[:-1, :-1].ravel()
    b = idx[1:, :-1].ravel()
    c = idx[1:, 1:].ravel()
    d = idx[:-1, 1:].ravel()
    keep = np.ones(a.shape, dtype=bool)
    cx = (X[:-1, :-1] + X[1:, 1:]).ravel() / 2
    cy = (Y[:-1, :-1] + Y[1:, 1:]).ravel() / 2
    if skip is not None:
        keep = ~skip(cx, cy)
    m.paint(list(paving(cx[keep], cy[keep])) if paving is not None else "ground")
    for qa, qb, qc, qd in zip(a[keep], b[keep], c[keep], d[keep]):
        m.f.append((base + int(qa), base + int(qb), base + int(qc), base + int(qd)))
    m.paint("ground")


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
    """A building's masses and its windows."""
    _massing(m, b, ground)
    windows(m, b)
    m.paint("render_white")


def _massing(m, b, ground):
    W, D, z0 = b["w"], b["d"], b["base"]
    c, s = math.cos(math.radians(b["angle"])), math.sin(math.radians(b["angle"]))
    to = lambda x, y: (b["ox"] + x * c - y * s, b["oy"] + x * s + y * c)
    low = min(ground(*to(x, y)) for x in (0, W / 2, W) for y in (0, D / 2, D))
    parts = []  # (local outline, z0, z1)

    def lbox(x0, y0, x1, y1, za, zb):
        m.box([to(x0, y0), to(x1, y0), to(x1, y1), to(x0, y1)], za, zb)

    if low < z0 - 0.1:
        m.paint("stone")
        lbox(0.05, 0.05, W - 0.05, D - 0.05, low - 0.4, z0)  # the plinth takes up the slope
    ze = z0 + b["eave"]
    roof = b["roof"]
    m.paint("render_white")
    lbox(0, 0, W, D, z0, ze)
    m.paint("roof_red")
    o = 0.45
    if roof == "flat":
        lbox(-0.15, -0.15, W + 0.15, D + 0.15, ze, ze + 0.5)
        return
    if roof == "tower":
        if b["name"].startswith("the cathedral"):
            cap = b["eave"] * 1.1   # a tall spire
        else:
            cap = min(W, D) * 0.45
        beacon = dict(H.BEACONS).get(b["name"])
        if beacon:
            m.paint(f"lamp_{beacon}")  # the lantern room of a harbour light
        lbox(-0.3, -0.3, W + 0.3, D + 0.3, ze, ze + 0.6)
        m.paint("roof_red")
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
    m.paint("render_white")
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
        m.paint("brick")
        cx = W * 0.62 if along else W / 2
        cy = D / 2 if along else D * 0.62
        lbox(cx - 0.35, cy - 0.35, cx + 0.35, cy + 0.35, ze + rise * 0.4, ze + rise + 1.1)


# -- windows: openings in the clay, lit where someone is in (heart_layout.evening) ----------------------------------

STOREY = 2.75                    # an old timber house's storey, floor to floor
PANE = dict(w=0.9, h=1.3, sill=0.85)


def _facades(W, D, along):
    """The four walls in the building's frame: (start, end, is_front, is_gable_end). Running from start to end with
    up, the outward side is to the right, so a quad laid that way faces out."""
    return [((0.0, 0.0), (W, 0.0), True, not along), ((W, D), (0.0, D), False, not along),
            ((0.0, D), (0.0, 0.0), False, along), ((W, 0.0), (W, D), False, along)]


def windows(m, b):
    W, D, z0 = b["w"], b["d"], b["base"]
    ze = z0 + b["eave"]
    name, role, roof = b["name"], b["role"], b["roof"]
    if name in H.EXEMPT or name in ("the bandstand in Lookout Park", "the breakwater's light", "the beacon on the Pip"):
        return
    c, s = math.cos(math.radians(b["angle"])), math.sin(math.radians(b["angle"]))
    to = lambda x, y: (b["ox"] + x * c - y * s, b["oy"] + x * s + y * c)
    ev = H.evening(b)
    r = random.Random(f"windows:{H.key(b)}")
    along = roof in ("eaves", "mansard")
    span = D if along else W
    rise = math.tan(math.radians(b["pitch"])) * (span / 2) if roof in ("eaves", "gable", "mansard") else 0.0

    def pane(a, e, t0, t1, za, zb, swatch, out=0.04):
        (ax, ay), (ex, ey) = a, e
        lx, ly = ex - ax, ey - ay
        ln = math.hypot(lx, ly)
        nx, ny = ly / ln, -lx / ln  # outward, in the building's frame
        p0 = to(ax + lx * t0 + nx * out, ay + ly * t0 + ny * out)
        p1 = to(ax + lx * t1 + nx * out, ay + ly * t1 + ny * out)
        m.paint(swatch)
        m.quad((*p0, za), (*p1, za), (*p1, zb), (*p0, zb))

    def lit_runs(n, share):
        """Which of n windows on a floor are lit: rooms are lit together, so a run of one to three."""
        on = [False] * n
        if n and r.random() < min(1.0, share * 1.6):
            k = r.randint(1, min(3, n))
            i = r.randint(0, n - k)
            on[i:i + k] = [True] * k
        return on

    # landmarks with their own openings
    if name.startswith("the cathedral"):
        if "tower" in name:
            for a, e, _, _ in _facades(W, D, along):
                pane(a, e, 0.4, 0.6, ze - 6.0, ze - 2.0, "glass")  # the belfry
            return
        for a, e, _, _ in _facades(W, D, along):
            ln = math.hypot(e[0] - a[0], e[1] - a[1])
            n = max(1, int(ln / 6.0))
            for i in range(n):
                t = (i + 0.5) / n
                pane(a, e, t - 0.7 / ln, t + 0.7 / ln, z0 + 3.0, z0 + 8.5, "glass")
        return
    if name == "the Fire Watch":
        for a, e, _, _ in _facades(W, D, along):
            for k in range(1, int(b["eave"] / 4.5)):
                pane(a, e, 0.42, 0.58, z0 + k * 4.5, z0 + k * 4.5 + 1.1, "glass")
            pane(a, e, 0.3, 0.7, ze - 2.2, ze - 0.6, "glass")  # the watchman's room, shut in the evening
        return

    warehouse = role == "warehouse"
    storey = 3.0 if warehouse else (3.4 if role == "landmark" else STOREY)
    floors = max(1, int((ze - z0 - 0.5) / storey + 0.2))
    for a, e, front, gable_end in _facades(W, D, along):
        ln = math.hypot(e[0] - a[0], e[1] - a[1])
        if warehouse and front and gable_end:
            # the sea house's gable to the quay: loading doors up the middle, a small window either side
            for k in range(floors):
                zb = z0 + k * storey
                if k == 0 and ev["shop"] == "open":  # turned into a bar: its ground floor glazed and lit
                    pane(a, e, 0.08, 0.42, zb + 0.3, zb + 2.5, "glass_shop_lit")
                    pane(a, e, 0.58, 0.92, zb + 0.3, zb + 2.5, "glass_shop_lit")
                    pane(a, e, 0.44, 0.56, zb, zb + 2.3, "door_brown")
                    continue
                pane(a, e, 0.5 - 0.7 / ln, 0.5 + 0.7 / ln, zb + 0.1, zb + 2.3, "wood")
                for t in (0.2, 0.8):
                    lit = r.random() < ev["upper"]
                    pane(a, e, t - 0.35 / ln, t + 0.35 / ln, zb + 1.0, zb + 1.9, "glass_lit" if lit else "glass")
            continue
        bays = max(1, int(ln / (4.5 if warehouse else 2.6)))
        w = min(PANE["w"], ln / bays * 0.5) / ln
        for k in range(floors):
            zb = z0 + k * storey
            za, zt = zb + PANE["sill"], zb + PANE["sill"] + PANE["h"]
            if zt > ze - 0.25:
                break
            if k == 0 and front and ev["shop"] is not None:
                # the ground floor's front: a shop, a pub or a café, two panes either side of a door, a sign over
                lit = ev["shop"] == "open"
                glass = "glass_shop_lit" if lit else "glass_shop"
                pane(a, e, 0.1, 0.43, zb + 0.35, zb + 2.55, glass)
                pane(a, e, 0.57, 0.9, zb + 0.35, zb + 2.55, glass)
                pane(a, e, 0.45, 0.55, zb + 0.02, zb + 2.3, "door_brown")
                if ev["shop"] != "empty":
                    pane(a, e, 0.14, 0.86, zb + 2.7, zb + 3.1, "sign_lit" if lit else "sign")
                continue
            on = lit_runs(bays, ev["upper"] if k > 0 or not front else ev["upper"])
            for i in range(bays):
                t = (i + 0.5) / bays
                pane(a, e, t - w / 2, t + w / 2, za, zt, "glass_lit" if on[i] else "glass")
        if gable_end and rise > 2.6 and not warehouse:
            lit = r.random() < ev["upper"] * 0.5
            pane(a, e, 0.5 - 0.4 / ln, 0.5 + 0.4 / ln, ze + 0.5, ze + 1.5, "glass_lit" if lit else "glass")


def detail_mesh(m, d):
    k, x, y, z, l, w, h, a = d["kind"], d["x"], d["y"], d["z"], d["l"], d["w"], d["h"], d["a"]
    if k == "lantern":
        m.paint("metal_post")
        m.obox(x, y, a, 0.18, 0.18, z, z + h - 0.6)
        m.obox(x, y, a, 0.56, 0.56, z + h - 0.12, z + h)        # its cap
        m.paint(f"lamp_{d.get('light', 'warm')}")
        m.obox(x, y, a, 0.46, 0.46, z + h - 0.6, z + h - 0.12)  # its glass
        m.paint("render_white")
    elif k == "pole":
        ax, ay = d.get("arm", (math.sin(math.radians(a)), -math.cos(math.radians(a))))
        m.paint("metal_post")
        m.obox(x, y, a, 0.24, 0.24, z, z + h)
        m.obox(x + 0.8 * ax, y + 0.8 * ay, math.degrees(math.atan2(ay, ax)), 1.8, 0.2, z + h - 0.2, z + h)
        m.paint(f"lamp_{d.get('light', 'sodium')}")
        m.obox(x + 1.5 * ax, y + 1.5 * ay, math.degrees(math.atan2(ay, ax)), 0.7, 0.32, z + h - 0.38, z + h - 0.2)
        m.paint("render_white")
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
STREET_SPACING = {"home": 34.0, "civic": 60.0, "work": 64.0}


def _ribbon(m, pts, width, ground, lift=0.12, step=6.0):
    """A road laid on the ground as a strip just over it."""
    for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
        L_ = math.hypot(x2 - x1, y2 - y1)
        n = max(1, int(L_ / step))
        nx, ny = -(y2 - y1) / L_ * width / 2, (x2 - x1) / L_ * width / 2
        for i in range(n):
            ax, ay = x1 + (x2 - x1) * i / n, y1 + (y2 - y1) * i / n
            bx, by = x1 + (x2 - x1) * (i + 1) / n, y1 + (y2 - y1) * (i + 1) / n
            za, zb = ground(ax, ay) + lift, ground(bx, by) + lift
            if za < H.SEA + 0.2 or zb < H.SEA + 0.2:
                continue  # no road on water
            m.quad((ax + nx, ay + ny, za), (ax - nx, ay - ny, za), (bx - nx, by - ny, zb), (bx + nx, by + ny, zb))


def context_mesh(m, roads, ground):
    """The town round the heart: the old roads, and in each district a street grid along its length with its
    houses along the streets, fronts to them, so every house has its street. Quiet massing, not judged."""
    rng = random.Random(H.SEED + 7)
    occupied = [H.footprint(b, 1.0) for b in H.BUILDINGS]
    boxes = [(min(p[0] for p in fp), min(p[1] for p in fp), max(p[0] for p in fp), max(p[1] for p in fp)) for fp in occupied]
    placed = []

    def free(fp):
        xs = [p[0] for p in fp]; ys = [p[1] for p in fp]
        b = (min(xs), min(ys), max(xs), max(ys))
        if any(not (b[2] < o[0] or b[0] > o[2] or b[3] < o[1] or b[1] > o[3]) for o in boxes):
            return False
        if any(not (b[2] < o[0] or b[0] > o[2] or b[3] < o[1] or b[1] > o[3]) for o in placed):
            return False
        return not L.is_water(np.array(xs), np.array(ys)).any()

    for r in L.OLD_ROADS:
        _ribbon(roads, r["pts"], r["width"], ground)
    count = 0
    for name, kind, poly in L.USES:
        if name in HAND or kind not in STREET_SPACING and kind != "farm":
            continue
        xs = [p[0] for p in poly]; ys = [p[1] for p in poly]
        # the district's length runs along its longest edge
        best = max(zip(poly, poly[1:] + poly[:1]), key=lambda e: math.hypot(e[1][0] - e[0][0], e[1][1] - e[0][1]))
        ang = math.atan2(best[1][1] - best[0][1], best[1][0] - best[0][0])
        ca, sa = math.cos(ang), math.sin(ang)
        cx, cy = sum(xs) / len(xs), sum(ys) / len(ys)
        span = max(max(xs) - min(xs), max(ys) - min(ys)) * 0.8
        if kind == "farm":
            # farmsteads along a farm lane down the valley's middle
            lane = [(cx - ca * span, cy - sa * span), (cx + ca * span, cy + sa * span)]
            _ribbon(roads, lane, 4.0, ground)
            t = -span
            while t < span:
                fx, fy = cx + ca * t + (-sa) * 14.0, cy + sa * t + ca * 14.0
                if L._inside(poly, np.array([fx]), np.array([fy]))[0]:
                    for (du, dv, w, d, e) in ((0, 0, 12, 9, 5.0), (16, 4, 24, 12, 6.5)):
                        ox, oy = fx + ca * du - sa * dv, fy + sa * du + ca * dv
                        b = dict(name="context", use=kind, ox=ox, oy=oy, angle=math.degrees(ang), w=w, d=d, base=ground(ox, oy) + 0.2,
                                 eave=e, pitch=40.0, roof="eaves", role="context")
                        if free(H.footprint(b)):
                            building_mesh(m, b, ground)
                            placed.append(tuple(f(v) for f, v in zip((min, min, max, max), ([p[0] for p in H.footprint(b)], [p[1] for p in H.footprint(b)], [p[0] for p in H.footprint(b)], [p[1] for p in H.footprint(b)]))))
                    count += 1
                t += rng.uniform(140.0, 200.0)
            continue
        sp = STREET_SPACING[kind]
        k = -int(span / sp)
        while k * sp < span:
            off = k * sp
            # a street across the district, then houses on both sides of it, fronts to it
            sx0, sy0 = cx - ca * span - sa * off, cy - sa * span + ca * off
            sx1, sy1 = cx + ca * span - sa * off, cy + sa * span + ca * off
            seg = []
            t = 0.0
            L_ = 2 * span
            while t < L_:
                px, py = sx0 + ca * t, sy0 + sa * t
                if L._inside(poly, np.array([px]), np.array([py]))[0] and not L.is_water(np.array([px]), np.array([py]))[0]:
                    seg.append((px, py))
                elif len(seg) > 1:
                    _ribbon(roads, seg, 7.0 if kind == "home" else 10.0, ground)
                    seg = []
                else:
                    seg = []
                t += 4.0
            if len(seg) > 1:
                _ribbon(roads, seg, 7.0 if kind == "home" else 10.0, ground)
            for side in (1, -1):
                t = rng.uniform(0, 6)
                while t < L_:
                    w = rng.uniform(8, 11) if kind == "home" else rng.uniform(20, 30)
                    d = rng.uniform(7, 9) if kind == "home" else rng.uniform(13, 18)
                    hw = 3.5 if kind == "home" else 5.0
                    fx, fy = sx0 + ca * t, sy0 + sa * t  # the front's start on the street's edge
                    if side > 0:
                        ox, oy, a = fx - sa * (hw + 1.0), fy + ca * (hw + 1.0), math.degrees(ang)
                    else:
                        ox, oy, a = fx + ca * w + sa * (hw + 1.0), fy + sa * w - ca * (hw + 1.0), math.degrees(ang) + 180.0
                    mx, my = fx + ca * w / 2, fy + sa * w / 2
                    if L._inside(poly, np.array([mx]), np.array([my]))[0] and rng.random() > 0.1:
                        z = ground(mx, my)
                        if kind == "home":
                            b = dict(name="context", use=kind, ox=ox, oy=oy, angle=a, w=w, d=d, base=z + 0.2, eave=rng.choice([4.4, 5.8, 6.4]),
                                     pitch=rng.uniform(36, 46), roof=rng.choice(["eaves", "gable"]), role="context")
                        elif kind == "civic":
                            b = dict(name="context", use=kind, ox=ox, oy=oy, angle=a, w=w, d=d, base=z + 0.2, eave=rng.uniform(11, 20),
                                     pitch=0.0, roof="flat", role="context")
                        else:
                            b = dict(name="context", use=kind, ox=ox, oy=oy, angle=a, w=w, d=d, base=z + 0.2, eave=rng.uniform(6, 9),
                                     pitch=22.0, roof="gable", role="context")
                        fp = H.footprint(b)
                        if free(fp):
                            building_mesh(m, b, ground)
                            placed.append((min(p[0] for p in fp), min(p[1] for p in fp), max(p[0] for p in fp), max(p[1] for p in fp)))
                            count += 1
                    t += w + rng.uniform(0.5, 3.0)
            k += 1
    return count


# -- assembling and exporting -------------------------------------------------------------------------------------


def make_object(m, coll):
    me = bpy.data.meshes.new(m.name)
    me.from_pydata(m.v, [], m.f)
    names = sorted(set(m.swatches()))
    ids = np.array([names.index(n) for n in m.swatches()], dtype=np.int32)
    me.attributes.new("swatch", "INT", "FACE").data.foreach_set("value", ids)
    me.validate()
    me.update()
    # every corner of a face on its swatch's centre
    ids = np.zeros(len(me.polygons), dtype=np.int32)
    me.attributes["swatch"].data.foreach_get("value", ids)
    centres = np.array([palette.uv(n) for n in names], dtype=np.float32)
    loop_poly = np.zeros(len(me.loops), dtype=np.int64)
    starts = np.zeros(len(me.polygons), dtype=np.int64)
    totals = np.zeros(len(me.polygons), dtype=np.int64)
    me.polygons.foreach_get("loop_start", starts)
    me.polygons.foreach_get("loop_total", totals)
    loop_poly = np.repeat(np.arange(len(me.polygons)), totals)
    uv = me.uv_layers.new(name="palette")
    uv.data.foreach_set("uv", centres[ids[loop_poly]].ravel())
    me.attributes.remove(me.attributes["swatch"])
    # what each face sees, from its facing: up-facing faces see sky, down-facing see ground
    normals = np.zeros(len(me.polygons) * 3)
    me.polygons.foreach_get("normal", normals)
    nz = normals.reshape(-1, 3)[:, 2]
    attr = me.color_attributes.new("bake", "FLOAT_COLOR", "CORNER")
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
    ground_mesh(g, X, Y, Zh, paving=H.paving)
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
    for w in H.ground_walls(ground):
        walls.obox(w["x"], w["y"], w["a"], w["l"], w["w"], w["z0"], w["z1"])

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
    roads = Mesh("roads")
    report["context buildings"] = context_mesh(ctx, roads, ground)
    # the railway: its bed and track on the ground, its station by the Mere
    rail = Mesh("railway")
    _ribbon(rail, [(p[0], p[1]) for p in L.RAILWAY], 9.0, ground, lift=0.3)
    _ribbon(rail, [(p[0], p[1]) for p in L.GOODS_LINE], 5.0, ground, lift=0.2)
    building_mesh(marks, dict(name="the station", ox=672.0, oy=-196.0, angle=30.0, w=40.0, d=14.0, base=ground(690.0, -190.0) + 0.3,
                              eave=8.0, pitch=36.0, roof="hip", role="landmark"), ground)

    meshes = [g, r, fm, water, lake, steps, walls, corner, houses, marks, det, far, ctx, roads, rail]
    objs = [make_object(m, coll) for m in meshes]
    report.update({m.name: len(m.f) for m in meshes})
    lamps = lamp_lights()
    report["lamps"] = len(lamps)
    if unity:
        out = os.path.join(unity, "Assets", "Art", "Blockout", "heart")
        for ob in objs:
            export_fbx(ob, os.path.join(out, f"{ob.name}.fbx"))
        with open(os.path.join(out, "lights.json"), "w") as f:
            json.dump({"lamps": lamps}, f, indent=0)
        palette.save_maps(os.path.join(unity, "Assets", "Art", "Palette"))
        report["exported to"] = out
    return report


def lamp_lights():
    """Every lamp as a light, where its glass is, in street metres: {x, y, z, kind}. Kinds: warm, mercury, sodium (the
    era its street was lit), red and white (the harbour's own lights)."""
    out = []
    for d in H.DETAILS:
        if d["kind"] == "lantern":
            out.append(dict(x=round(d["x"], 2), y=round(d["y"], 2), z=round(d["z"] + d["h"] - 0.36, 2), kind=d.get("light", "warm")))
        elif d["kind"] == "pole":
            ax, ay = d.get("arm", (0.0, 0.0))
            out.append(dict(x=round(d["x"] + 1.5 * ax, 2), y=round(d["y"] + 1.5 * ay, 2), z=round(d["z"] + d["h"] - 0.45, 2),
                            kind=d.get("light", "sodium")))
    for b in H.BUILDINGS:
        colour = dict(H.BEACONS).get(b["name"])
        if colour:
            out.append(dict(x=round(b["ox"] + b["w"] / 2, 2), y=round(b["oy"] + b["d"] / 2, 2),
                            z=round(b["base"] + b["eave"] + 0.3, 2), kind=colour))
    return out


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
