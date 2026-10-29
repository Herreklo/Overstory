"""The Bluff in grey: Herring Hill's point, its north-west face over the Roads, built of its own joint cells.

The mass is designed (fixtures/lt1-bluff.json, face): the face's foot on the plan's crest line, a sea-cut lower wall,
a ledge, an upper slope to a rounded turf shoulder, each varying slowly along the face; bays set back and turned by the
big joints; clefts the sea cut along J3; caves along the foliation. The rock is the cells the four joint families
cut, each kept where its middle lies within the mass by its own seeded erosion, the softer foliation slabs worn back
further. So every face of the Bluff is one of its own joint planes, exactly (BB3), and the face is a staircase of
them. A cell's face is dropped where a standing neighbour covers it, so the whole rock is a few tens of thousands of
triangles, checked against the fixture's budget. Dated falls take whole cells from the face and leave them, broken,
on the foot.

Site metres: x east, y north, z up over mean sea level; the origin is street (-290, 60).

    Blender -b --factory-startup -P blender/parts/rock/bluff.py -- --out DIR [--view foot] [--w 1600] [--h 900]
        [--samples 64] [--exposure -0.8]
"""

import json
import math
import os
import sys
import time

import bpy
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "blender", "resolver"))
sys.path.insert(0, os.path.join(ROOT, "blender", "blockouts"))
import centre_land as CL  # noqa: E402
import hashing as HS  # noqa: E402
import hull as H  # noqa: E402
import outcrop as O  # noqa: E402

_ARGS = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
FIX = json.load(open(_ARGS[_ARGS.index("--fix") + 1] if "--fix" in _ARGS  # a variant of the fixture, to compare
                     else os.path.join(ROOT, "fixtures", "lt1-bluff.json")))
CREST_STREET = [c for c in CL.CLIFFS if c["name"] == "the bluff"][0]["line"]
CL.CLIFFS = []  # the top is the ground without the cliff term (see the fixture's note)
X0, Y0 = FIX["street_origin"]
CREST = np.array([(sy - Y0, X0 - sx) for sx, sy in CREST_STREET])
FACE, FOOT, SOIL, ROCK, SEA = FIX["face"], FIX["foot"], FIX["soil"], FIX["rock"], FIX["sea"]
SEC = FACE["section"]
BED = -3.0  # the rock is built down to here; below it the sea hides it


def arg(name, default=None):
    a = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    return a[a.index(name) + 1] if name in a else default


def ground(x, y):
    return CL.heights(X0 - np.asarray(y, float), Y0 + np.asarray(x, float))


def water(x, y):
    return CL.is_water(X0 - np.asarray(y, float), Y0 + np.asarray(x, float))


def smooth(a, b, v):
    t = np.clip((v - a) / (b - a), 0.0, 1.0)
    return t * t * (3 - 2 * t)


def crest_frame(x, y):
    """Signed distance to the crest line (> 0 seaward, on the line's left), the distance along it, the seaward normal."""
    best = np.full(x.shape, 1e9)
    s = np.zeros(x.shape)
    u = np.zeros(x.shape)
    nx = np.zeros(x.shape)
    ny = np.zeros(x.shape)
    acc = 0.0
    for a, b in zip(CREST[:-1], CREST[1:]):
        d = b - a
        L = float(np.hypot(*d))
        t = np.clip(((x - a[0]) * d[0] + (y - a[1]) * d[1]) / L ** 2, 0.0, 1.0)
        dd = np.hypot(x - a[0] - d[0] * t, y - a[1] - d[1] * t)
        side = (d[0] * (y - a[1]) - d[1] * (x - a[0])) / L
        c = dd < best
        best = np.where(c, dd, best)
        s = np.where(c, np.where(side >= 0, dd, -dd), s)
        u = np.where(c, acc + t * L, u)
        nx = np.where(c, -d[1] / L, nx)
        ny = np.where(c, d[0] / L, ny)
        acc += L
    return s, u, nx, ny, acc


def point_on_crest(u):
    acc = 0.0
    for a, b in zip(CREST[:-1], CREST[1:]):
        L = float(np.hypot(*(b - a)))
        if u <= acc + L:
            return a + (b - a) * (u - acc) / L
        acc += L
    return CREST[-1].copy()


# -- the plan fields ------------------------------------------------------------------------------------------------

class Plan:
    """The fields over the plan at `step` m: the crest frame, the ground's top, the designed foot."""

    def __init__(self, x0, x1, y0, y1, step=0.25):
        self.x0, self.y0, self.step = x0, y0, step
        xs = np.arange(x0, x1 + step, step)
        ys = np.arange(y0, y1 + step, step)
        X, Y = np.meshgrid(xs, ys, indexing="ij")
        self.shape = X.shape
        s, u, nx, ny, self.length = crest_frame(X, Y)
        top = ground(X, Y)
        wet = water(X, Y)
        to_sea, to_land = edt(wet, step), edt(~wet, step)
        # the face stands up out of the slope at the crest's ends
        w = smooth(0.0, 22.0, u) * (1 - smooth(self.length - 12.0, self.length, u))
        t = np.clip(s / np.maximum(s + to_sea, 1e-3), 0, 1) ** 0.8
        land_foot = FACE["footZ"] + (FOOT["edgeZ"] - FACE["footZ"]) * t
        sea_bed = np.maximum(FOOT["edgeZ"] - FOOT["bedSlope"] * to_land, FOOT["bedFloor"])
        foot = np.where(wet, sea_bed, np.where(s > 0, land_foot, FACE["footZ"]))
        foot = np.where(wet, foot, top + (foot - top) * w)
        soft = (1 - smooth(0.15, 0.35, w)) * (~wet)  # where the face fades into the slope, the slope keeps its turf
        foot = foot - SOIL["depthM"] * soft
        self.F = dict(s=s, u=u, nx=nx, ny=ny, top=top, foot=foot, w=w, wet=wet.astype(float), soft=soft)

    def at(self, name, x, y):
        G = self.F[name]
        fu = np.clip((x - self.x0) / self.step, 0, self.shape[0] - 1.001)
        fv = np.clip((y - self.y0) / self.step, 0, self.shape[1] - 1.001)
        i, j = fu.astype(int), fv.astype(int)
        a, b = fu - i, fv - j
        return (G[i, j] * (1 - a) * (1 - b) + G[i + 1, j] * a * (1 - b) + G[i, j + 1] * (1 - a) * b
                + G[i + 1, j + 1] * a * b)

    def grad(self, f, x, y, h=0.5):
        return (f(x + h, y) - f(x - h, y)) / (2 * h), (f(x, y + h) - f(x, y - h)) / (2 * h)


def edt(mask, step, reach=60.0):
    """Distance (m) from each cell to the nearest True cell, by repeated 8-neighbour relaxation (no scipy)."""
    D = np.where(mask, 0.0, 1e9)
    k = [(1, 0, 1.0), (-1, 0, 1.0), (0, 1, 1.0), (0, -1, 1.0), (1, 1, 1.4142), (1, -1, 1.4142), (-1, 1, 1.4142),
         (-1, -1, 1.4142)]
    for _ in range(int(reach / step)):
        prev = D
        for di, dj, c in k:
            S = np.roll(np.roll(D, di, 0), dj, 1) + c * step
            D = np.minimum(D, S)
        if np.array_equal(prev, D):
            break
    return np.minimum(D, reach)


def vnoise(t, key):
    """A smooth 1D value noise in [0, 1] over t, seeded by key."""
    t = np.maximum(np.asarray(t, float), 0.0)
    rng = HS.Stream("lt1-bluff", key)
    n = int(np.max(t)) + 3 if t.size else 3
    v = np.array([rng.random() for _ in range(n + 1)])
    i = np.clip(np.floor(t).astype(int), 0, n - 1)
    f = t - np.floor(t)
    f = f * f * (3 - 2 * f)
    return v[i] * (1 - f) + v[i + 1] * f


# -- seeded numbers per cell ----------------------------------------------------------------------------------------

M1, M2 = np.uint64(0xBF58476D1CE4E5B9), np.uint64(0x94D049BB133111EB)
PRIMES = [np.uint64(p) for p in (0x9E3779B97F4A7C15, 0xC2B2AE3D27D4EB4F, 0x165667B19E3779F9, 0x27D4EB2F165667C5)]
BASE = np.uint64(HS.h("lt1-bluff", "cells") & 0xFFFFFFFFFFFFFFFF)


def mix(z):
    with np.errstate(over="ignore"):
        z = (z ^ (z >> np.uint64(30))) * M1
        z = (z ^ (z >> np.uint64(27))) * M2
        return z ^ (z >> np.uint64(31))


def cell_random(ids, salt):
    with np.errstate(over="ignore"):
        z = BASE + np.uint64(salt) * PRIMES[0]
        for k, i in enumerate(ids):
            z = mix(z ^ (np.asarray(i).astype(np.uint64) * PRIMES[k % 4]))
    return (z >> np.uint64(11)).astype(np.float64) / float(1 << 53)


def vnoise2(a, b, key):
    """A smooth 2D value noise in [0, 1] over (a, b), seeded per lattice corner."""
    ia, ib = np.floor(a), np.floor(b)
    fa, fb = a - ia, b - ib
    fa, fb = fa * fa * (3 - 2 * fa), fb * fb * (3 - 2 * fb)
    ia, ib = ia.astype(np.int64) + 4096, ib.astype(np.int64) + 4096
    v = lambda i, j: cell_random([i, j], key)  # noqa: E731
    return ((v(ia, ib) * (1 - fa) + v(ia + 1, ib) * fa) * (1 - fb)
            + (v(ia, ib + 1) * (1 - fa) + v(ia + 1, ib + 1) * fa) * fb)


def key4(I):
    """One int64 per cell from its four slab indices."""
    I = np.asarray(I, np.int64)
    return ((I[..., 0] * 32768 + I[..., 1]) * 32768 + I[..., 2]) * 32768 + I[..., 3]


# -- the rock -------------------------------------------------------------------------------------------------------

class Rock:
    def __init__(self, plan, box):
        self.P = plan
        self.box = box
        lo = np.array(box[0], float)
        hi = np.array(box[1], float)
        corners = np.array([[a, b, c] for a in (lo[0], hi[0]) for b in (lo[1], hi[1]) for c in (lo[2], hi[2])])

        def lo_hi(n):
            s = corners @ n
            return s.min() - 1.0, s.max() + 1.0

        self.fams = []
        for fam in ROCK["families"]:
            n, offs, gaps = O.family_planes("lt1-bluff", fam, lo_hi)
            self.fams.append((fam["name"], n, offs, gaps))
        self.fam = {f[0]: f for f in self.fams}
        self.N = np.array([f[1] for f in self.fams])
        self.pinv = np.linalg.pinv(self.N)
        self.acts = [dict(a) for a in FIX["acts"]]
        for a in self.acts:
            s, u, nx, ny, _ = crest_frame(np.array([a["at"][0]]), np.array([a["at"][1]]))
            a["_u"], a["_n"] = float(u[0]), np.array([nx[0], ny[0]])
        fol = self.fol = self.fam["foliation"][1]
        h = np.array([fol[0], fol[1], 0.0])
        h /= np.linalg.norm(h)
        self.strike = np.array([-h[1], h[0], 0.0])  # horizontal, in the foliation's plane

    # the designed mass

    def slab(self, name, P):
        """Each point's slab of a family: its index, its distance from the slab's middle, the slab's half width."""
        _, n, offs, _ = self.fam[name]
        sv = P @ n
        i = np.clip(np.searchsorted(offs, sv), 1, len(offs) - 1)
        return i, sv - (offs[i - 1] + offs[i]) / 2, (offs[i] - offs[i - 1]) / 2

    def middles(self, I):
        """The middle of each cell (rows of four slab indices): the point nearest every family's slab middle."""
        mids = []
        for k, f in enumerate(self.fams):
            i = np.clip(I[:, k], 1, len(f[2]) - 1)
            mids.append((f[2][i - 1] + f[2][i]) / 2)
        return (self.pinv @ np.stack(mids, 0)).T

    def section(self, u):
        f = lambda key, r: r[0] + (r[1] - r[0]) * vnoise(u / SEC["cellM"], key)  # noqa: E731
        return f("low-wall", SEC["lowWallM"]), f("ledge", SEC["ledgeM"]), np.tan(np.radians(f("up", SEC["upLeanDeg"])))

    def face_line(self, z, u):
        """The face's distance out from the crest line at height z: the lower wall, the ledge, the upper slope."""
        hL, dL, tu = self.section(u)
        tl = math.tan(math.radians(SEC["lowLeanDeg"]))
        zl = FACE["footZ"] + hL
        return np.where(z < zl, -(z - FACE["footZ"]) * tl, -hL * tl - dL - (z - zl) * tu)

    def bay(self, P):
        """How far each point's bay stands back, never forward: each big cell (J1 by J3) one plane, set back and
        turned about the vertical by its own seeded amounts."""
        i1, _, _ = self.slab("J1", P)
        i3, l3, h3 = self.slab("J3", P)
        a, b = FACE["bigSetbackM"]
        turn = math.tan(math.radians(FACE["turnDeg"])) * (2 * cell_random([i1, i3], 21) - 1)
        return a + (b - a) * cell_random([i1, i3], 20) + turn * l3 + np.abs(turn) * h3

    def crest_s(self, x, y):
        """Where the face meets the top: the crest's distance out from the crest line."""
        P = self.P
        top = P.at("top", x, y) - SOIL["depthM"]
        wg = smooth(0.1, 0.4, P.at("w", x, y))
        return self.face_line(top, P.at("u", x, y)) - self.bay(np.stack([x, y, top], -1)) * wg

    def top_at(self, x, y, s=None, sc=None):
        """The ground's top with its shoulder rounded down over the crest."""
        P = self.P
        s = P.at("s", x, y) if s is None else s
        sc = self.crest_s(x, y) if sc is None else sc
        R, drop = FACE["shoulder"]["RM"], FACE["shoulder"]["dropM"]
        k = np.clip((s - (sc - R)) / R, 0, 1)
        return P.at("top", x, y) - drop * k * k * smooth(0.1, 0.4, P.at("w", x, y))

    def parts(self, x, y, z):
        """The mass at points: (distance out of it, the foot's term, the top's term, the face's term, s, u)."""
        P = self.P
        s, u, w = P.at("s", x, y), P.at("u", x, y), P.at("w", x, y)
        sc = self.crest_s(x, y)
        top = self.top_at(x, y, s, sc) - SOIL["depthM"]
        wg = smooth(0.1, 0.4, w)
        face = s - (self.face_line(z, u) - self.bay(np.stack([x, y, z], -1)) * wg)
        face = np.where(w > 0.02, face, 1e3)
        foot = z - P.at("foot", x, y)
        tp = z - top
        return np.minimum(foot, np.maximum(tp, face)), foot, tp, face, s, u

    def turf_edge(self, x, y):
        """The turf's edge as a distance out from the crest line: back from the crest by the soil's seeded amount."""
        e0, e1 = SOIL["edgeBackM"]
        u = self.P.at("u", x, y)
        return self.crest_s(x, y) - (e0 + (e1 - e0) * vnoise(u / SOIL["edgeCellM"], "turf-edge"))

    # what took cells away

    def cave(self, act, Pt):
        A = np.array([act["at"][0], act["at"][1], SEA["level"]])
        into = -np.array([act["_n"][0], act["_n"][1], 0.0])
        ax = self.strike if self.strike @ into > 0 else -self.strike
        q = Pt - A
        a = q @ ax
        b = q @ self.fol
        t = np.clip(a / act["depthM"], 0, 1)
        roof = SEA["level"] - 0.4 + act["heightM"] * (1 - 0.55 * t)
        half = act["widthM"] / 2 * (1 - 0.4 * t)
        return np.maximum.reduce([np.abs(b) - half, -(a + 6.0), a - act["depthM"], SEA["level"] - 1.4 - Pt[:, 2],
                                  Pt[:, 2] - roof])

    def taken(self, C, s, u):
        """Which cells (by their middles) the sea's clefts and caves took, and which each dated fall took."""
        z = C[:, 2]
        into = self.face_line(z, u) - s  # how far into the face from its designed line
        gone = np.zeros(len(C), bool)
        for cl in FIX["clefts"]["list"]:
            gone |= (np.abs(u - cl["u"]) < cl["widthM"] / 2) & (into < cl["depthM"]) & (z > BED)
        for act in self.acts:
            if act["kind"] == "cave":
                gone |= self.cave(act, C) < 0
        fell = {}
        for act in self.acts:
            if act["kind"] == "rockfall":
                fell[act["id"]] = ((np.abs(u - act["_u"]) < act["widthM"] / 2) & (z > act["zM"][0])
                                   & (z < act["zM"][1]) & (into < act["depthM"]) & ~gone)
        return gone, fell

    # the cells

    def cells(self, step=0.45):
        """The slab indices of every cell within bandM of the mass's surface, from a lattice of points over it."""
        P = self.P
        (x0, y0, _), (x1, y1, _) = self.box
        xs = np.arange(x0, x1, step)
        ys = np.arange(y0, y1, step)
        X, Y = np.meshgrid(xs, ys, indexing="ij")
        X, Y = X.ravel(), Y.ravel()
        s = P.at("s", X, Y)
        near = (s > -40) & (P.at("foot", X, Y) > BED - 0.5) & (P.at("w", X, Y) > 0.02)
        X, Y = X[near], Y[near]
        top = P.at("top", X, Y) + 1.0
        found = []
        zs = np.arange(BED + step / 2, float(top.max()), step)
        chunk = 400000 // len(zs) + 1
        for k in range(0, len(X), chunk):
            x, y, tz = X[k:k + chunk], Y[k:k + chunk], top[k:k + chunk]
            xx = np.repeat(x, len(zs))
            yy = np.repeat(y, len(zs))
            zz = np.tile(zs, len(x))
            m = zz < np.repeat(tz, len(zs))
            xx, yy, zz = xx[m], yy[m], zz[m]
            d = self.parts(xx, yy, zz)[0]
            m = (d < 1.2) & (d > -FACE["bandM"])
            Pt = np.stack([xx[m], yy[m], zz[m]], -1)
            I = np.stack([self.slab(f[0], Pt)[0] for f in self.fams], -1)
            found.append(np.unique(I, axis=0))
        return np.unique(np.concatenate(found), axis=0)

    def foot_planes(self, I, C, soft):
        """The sea's platform over each foot cell: the foot's plane at the cell, worn down in the tide by the slab's
        softness, its top turned about the strike (a fin's saw profile along it), most at the tide."""
        P = self.P
        x, y = C[:, 0], C[:, 1]
        z0 = P.at("foot", x, y)
        gx, gy = P.grad(lambda a, b: P.at("foot", a, b), x, y)
        a, b = FOOT["ribM"]
        tide = smooth(FACE["footZ"] + 1.5, FOOT["edgeZ"] - 0.5, z0)
        _, n, offs, _ = self.fam["foliation"]
        iF = np.clip(I[:, 0], 1, len(offs) - 1)
        mid = (offs[iF - 1] + offs[iF]) / 2
        half = (offs[iF] - offs[iF - 1]) / 2
        tt = math.tan(math.radians(FOOT["finTurnDeg"])) * (2 * cell_random([iF], 13) - 1) * tide
        drop = (a + (b - a) * soft) * tide + np.abs(tt) * half
        # z <= z0 + g.(p - c) - drop - tt (n.p - mid)
        m = np.stack([-gx + tt * n[0], -gy + tt * n[1], 1.0 + tt * n[2]], -1)
        d = z0 - gx * x - gy * y - drop + tt * mid
        ln = np.linalg.norm(m, axis=1)
        return m / ln[:, None], d / ln

    def top_planes(self, C):
        """The shoulder's plane over each cell (the turf lies on it)."""
        x, y = C[:, 0], C[:, 1]
        zt = self.top_at(x, y) - SOIL["depthM"]
        gx, gy = self.P.grad(self.top_at, x, y)
        m = np.stack([-gx, -gy, np.ones_like(gx)], -1)
        ln = np.linalg.norm(m, axis=1)
        return m / ln[:, None], (zt - gx * x - gy * y) / ln

    def body(self, ids, extra):
        """One cell: its eight joint planes (an open joint's two walls parted by its gap), then the extra planes."""
        planes = []
        for k, (name, n, offs, gaps) in enumerate(self.fams):
            i = ids[k]
            g0, g1 = gaps[i - 1], gaps[i]
            planes.append((-n, -(offs[i - 1] + g0 / 2), ("joint", k, -1, g0)))
            planes.append((n, offs[i] - g1 / 2, ("joint", k, 1, g1)))
        planes += extra
        planes.append((np.array([0, 0, -1.0]), -BED, "bed"))
        b = H.body(np.array(self.box[0]) - 5, np.array(self.box[1]) + 5, planes)
        if b is None or H.volume(b) < 0.02:
            return None
        return b

    def build(self):
        """The standing cells as convex bodies with their hidden faces dropped; the fallen cells by their act."""
        t = time.time()
        I = self.cells()
        C = self.middles(I)
        d, foot, tp, face, s, u = self.parts(C[:, 0], C[:, 1], C[:, 2])
        E = FACE["erosion"]
        rs = cell_random([I[:, 0]], 12)
        soft = smooth(1 - E["softShare"], 1.0, rs)  # the soft slabs, worn deepest
        la, lb = E["layerAmpM"]
        pa, pb = E["patchAmpM"]
        ca, cb = E["cellM"]
        ba, bb = E["crestBiteM"]
        iL = I[:, 3].astype(float)
        crest = smooth(-E["crestDepthM"], 0.0, tp)  # how near the top the cell lies
        erode = (la + (lb - la) * vnoise2(u / E["layerM"], iL * 1.0, 3)  # each layer its own, along the face
                 + pa + (pb - pa) * vnoise2(u / E["patchM"][0], C[:, 2] / E["patchM"][1], 2)
                 + ca + (cb - ca) * cell_random([I[:, k] for k in range(4)], 1) - E["softM"] * soft
                 - crest * (ba + (bb - ba) * vnoise(u / E["crestCellM"], "crest-bite") ** 2))
        gone, fell = self.taken(C, s, u)
        on_foot = foot <= np.maximum(tp, face)
        # cells under the turf well back from its edge are hidden by it: left solid, unbuilt
        under = (~on_foot) & (tp >= face) & (s < self.turf_edge(C[:, 0], C[:, 1]) - 3.0)
        stand0 = np.where(on_foot, C[:, 2] < self.P.at("foot", C[:, 0], C[:, 1]) + 2.5, d < erode) & ~gone & ~under
        for k in fell:
            fell[k] &= stand0
        stand = stand0.copy()
        for f in fell.values():
            stand &= ~f
        print(f"cells: {len(I)} near the surface, {stand.sum()} standing, {under.sum()} under the turf,"
              f" {sum(f.sum() for f in fell.values())} fallen, {time.time() - t:.1f}s")
        # each standing cell's planes beyond its joints: the top's, and the foot's where the foot governs
        tn, td = self.top_planes(C)
        fn, fd = self.foot_planes(I, C, soft)
        bodies, clips = {}, {}
        for j in np.where(stand)[0]:
            extra = [(tn[j], td[j], "top")]
            if on_foot[j]:
                extra.append((fn[j], fd[j], "foot"))
            bd = self.body(I[j], extra)
            if bd is not None:
                bodies[j] = bd
                clips[j] = [(n_, d_) for n_, d_, _ in extra]
        # a neighbour not found near the surface is solid if its middle lies inside the mass (deep), else open air
        idx = {k: j for j, k in enumerate(key4(I).tolist())}
        J = np.array(sorted(bodies))
        inside = {}
        for k in range(4):
            for side in (-1, 1):
                nb = I[J].copy()
                nb[:, k] += side
                Cn = self.middles(nb)
                dn = self.parts(Cn[:, 0], Cn[:, 1], Cn[:, 2])[0]
                for j, kk, dv in zip(J.tolist(), key4(nb).tolist(), dn.tolist()):
                    inside[(j, k, side)] = (idx.get(kk), dv < 0)
        fallen_at = {}
        for act in self.acts:
            if act["kind"] == "rockfall":
                for j in np.where(fell[act["id"]])[0]:
                    fallen_at[int(j)] = FIX["date"] - act["year"]
        out, dropped, slots, bared = [], 0, [], {}
        for j, faces in bodies.items():
            keep = []
            for fc in faces:
                if fc.label in ("bed", "box"):
                    continue
                if isinstance(fc.label, tuple):
                    _, k, side, gap = fc.label
                    jb, deep = inside[(j, k, side)]
                    if jb is None:
                        hidden = deep
                    elif jb in bodies:
                        # the neighbour's face on this plane is the same polygon cut by its own top or foot: this one
                        # is covered where every corner lies within the neighbour's cuts
                        hidden = all(np.all(fc.V @ n_ <= d_ + 0.03) for n_, d_ in clips[jb])
                        if hidden and gap > 1e-6:
                            slots.append((len(out), fc))  # an open joint's wall: hidden only where it lies deep
                            continue
                    else:
                        hidden = bool(under[jb])
                        if jb in fallen_at:
                            bared[(j, fc.label)] = fallen_at[jb]  # the fall's scar: bare since it fell
                    if hidden:
                        dropped += 1
                        continue
                keep.append(fc)
            out.append(keep)
        if slots:
            V = np.concatenate([fc.V for _, fc in slots])
            dv = self.parts(V[:, 0], V[:, 1], V[:, 2])[0]
            k = 0
            for i, fc in slots:
                if dv[k:k + len(fc.V)].max() > -ROCK["openDepthM"]:
                    out[i].append(fc)
                else:
                    dropped += 1
                k += len(fc.V)
        # the wear: every edge between two faces open to the air, cut back by one plane
        tide = smooth(FACE["footZ"] + 1.5, FOOT["edgeZ"] - 0.5, C[:, 2])
        worn = []
        for (j, faces), keep in zip(bodies.items(), out):
            kept = {fc.label for fc in keep}
            w = wear(faces, kept, HS.Stream("lt1-bluff", "wear", int(key4(I[j]))), float(tide[j]))
            if w is None:
                continue
            age = min([bared.get((j, lab), OLD) for lab in kept] + [OLD])
            worn.append([(fc, bared.get((j, fc.label), age if fc.label == "worn" else OLD)) for fc in w
                         if fc.label in kept or fc.label == "worn"])
        falls = {}
        for aid, f in fell.items():
            falls[aid] = [self.body(I[j], [(tn[j], td[j], "top")]) for j in np.where(f)[0]]
        print(f"bodies: {len(worn)}, {dropped} hidden faces dropped, {time.time() - t:.1f}s")
        return worn, falls


OLD = 10000.0  # years bare: since the ice


def wear(faces, kept, rng, tide):
    """A body with every edge between two of its open faces worn back by one plane through the edge's line, wider
    facing up and in the tide (FIX wear); the plane's face is labelled "worn". Rigid: a cut, never a bend."""
    W = FIX["wear"]
    ex = [f for f in faces if f.label in kept]
    cuts = []
    for a in range(len(ex)):
        for b in range(a + 1, len(ex)):
            A, B = ex[a], ex[b]
            common = [v for v in A.V if np.min(np.linalg.norm(B.V - v, axis=1)) < 1e-4]
            if len(common) < 2:
                continue
            n = A.n + B.n
            ln = np.linalg.norm(n)
            if ln < 0.3:
                continue  # a knife edge: leave it
            n = n / ln
            w = rng.uniform(*W["edgeM"]) * (1 + W["upFactor"] * max(n[2], 0.0)) * (1 + W["tideFactor"] * tide)
            cuts.append((n, float(n @ common[0]) - w))
    for n, d in cuts:
        faces = H.clip(faces, n, d, "worn")
        if faces is None:
            return None
    return faces


def rot(yaw, pitch, roll):
    cy, sy, cp, sp, cr, sr = (math.cos(yaw), math.sin(yaw), math.cos(pitch), math.sin(pitch), math.cos(roll),
                              math.sin(roll))
    Rz = np.array([[cy, -sy, 0], [sy, cy, 0], [0, 0, 1]])
    Rx = np.array([[1, 0, 0], [0, cp, -sp], [0, sp, cp]])
    Ry = np.array([[cr, 0, sr], [0, 1, 0], [-sr, 0, cr]])
    return Rz @ Rx @ Ry


def fallen(rock, falls):
    """Each dated fall's cells on the foot below its scar, broken along their shut joints into its count of blocks, turned
    as they landed; the old fall's blocks worn at their corners by the years (each a plane: rigid)."""
    P = rock.P
    out = []
    for act in rock.acts:
        if act["kind"] != "rockfall":
            continue
        rng = HS.Stream("lt1-bluff", act["id"], "blocks")
        age = FIX["date"] - act["year"]
        pieces = [c for c in falls[act["id"]] if c is not None]
        tries = 0
        while pieces and len(pieces) < act["blocks"] and tries < 4 * act["blocks"]:
            # the biggest block breaks along a shut joint of one of its families, the foliation most often: slabs
            tries += 1
            big = max(range(len(pieces)), key=lambda k: H.volume(pieces[k]))
            q = pieces.pop(big)
            fam = rock.fams[rng.weighted([(0, 5), (1, 2), (2, 1), (3, 3)])]
            n = fam[1] + np.array([rng.normal(), rng.normal(), rng.normal()]) * 0.06
            n /= np.linalg.norm(n)
            sv = np.concatenate([f.V for f in q]) @ n
            cut = sv.min() + (sv.max() - sv.min()) * rng.uniform(0.3, 0.7)
            for sgn in (1, -1):
                r = H.clip(q, sgn * n, sgn * cut, "break")
                if r is not None and H.volume(r) > 0.05:
                    pieces.append(r)
        for q in pieces:
            c = O.centroid(q)
            if age > 30:
                V = np.unique(np.round(np.concatenate([f.V for f in q]), 4), axis=0)
                for v in V:
                    dv = v - c
                    L = np.linalg.norm(dv)
                    if L < 1e-3 or q is None:
                        continue
                    q = H.clip(q, dv / L, float(dv @ c) / L + 0.72 * L, "worn")
                if q is None:
                    continue
                q = wear(q, {f.label for f in q}, rng, 0.5)  # and a century of sea on its edges
                if q is None:
                    continue
                c = O.centroid(q)
            for _ in range(40):
                uu = act["_u"] + rng.uniform(-act["widthM"] * 0.8, act["widthM"] * 0.8)
                base = point_on_crest(uu)
                fr = crest_frame(np.array([base[0]]), np.array([base[1]]))
                x, y = base + np.array([fr[2][0], fr[3][0]]) * rng.uniform(1.0, 6.0 + 0.08 * age)
                if P.at("wet", np.array([x]), np.array([y]))[0] < 0.5:
                    break
            R = rot(rng.uniform(0, 2 * math.pi), rng.uniform(-0.5, 0.5), rng.uniform(-0.5, 0.5))
            faces = [H.Face((f.V - c) @ R.T, R @ f.n, 0.0, f.label) for f in q]
            zmin = min(f.V[:, 2].min() for f in faces)
            z = float(P.at("foot", np.array([x]), np.array([y]))[0])
            off = np.array([x, y, z - zmin - 0.25])
            out.append([(H.Face(f.V + off, f.n, 0.0, f.label), float(age)) for f in faces])
    return out


def boulders(rock):
    """Old stones on the foot from falls long gone, rounded by the sea: low hulls of a few points each."""
    P = rock.P
    bd = FIX["boulders"]
    rng = HS.Stream("lt1-bluff", bd["seed"])
    out = []
    tries = 0
    while len(out) < bd["count"] and tries < bd["count"] * 40:
        tries += 1
        u = rng.uniform(4.0, P.length - 6.0)
        base = point_on_crest(u)
        fr = crest_frame(np.array([base[0]]), np.array([base[1]]))
        x, y = base + np.array([fr[2][0], fr[3][0]]) * rng.uniform(1.0, 26.0)
        z0 = P.at("foot", np.array([x]), np.array([y]))[0]
        if z0 > 1.6 or z0 < -1.2 or rng.random() > 0.35 + 0.65 * smooth(1.6, -0.6, z0):
            continue
        a, b = bd["sizeM"]
        L = a + (b - a) * rng.random() ** 2.2
        half = np.array([L, L * rng.uniform(0.6, 0.95), L * rng.uniform(0.4, 0.7)]) / 2
        R = rot(rng.uniform(0, 2 * math.pi), rng.uniform(-0.2, 0.2), rng.uniform(-0.2, 0.2))
        pts = []
        for _ in range(16):
            v = np.array([rng.normal(), rng.normal(), rng.normal()])
            pts.append((v / np.linalg.norm(v)) * half)
        out.append((np.array(pts) @ R.T + np.array([x, y, z0 - 0.3 + half[2] * 0.5])))
    return out


# -- meshes -------------------------------------------------------------------------------------------------------

PLANE = {"top": 4, "foot": 5, "worn": 6, "break": 7}


def faces_object(name, bodies):
    """The bodies' faces as one flat-shaded mesh, each face carrying what made it (the shader answers light by it):
    plane (0 to 3 the joint family, 4 the top's cut, 5 the sea's platform, 6 worn, 7 a fresh break), gap (the joint's
    opening, m) and age (years since it was bared)."""
    V, T, plane, gap, age = [], [], [], [], []
    for faces in bodies:
        for f, a in faces:
            b = len(V)
            V.extend(f.V.tolist())
            T.append(list(range(b, b + len(f.V))))
            lab = f.label
            plane.append(lab[1] if isinstance(lab, tuple) else PLANE.get(lab, 7))
            gap.append(lab[3] if isinstance(lab, tuple) else 0.0)
            age.append(a)
    me = bpy.data.meshes.new(name)
    me.from_pydata(V, [], T)
    for nm, kind, vals in (("plane", "INT", plane), ("gap", "FLOAT", gap), ("age", "FLOAT", age)):
        at = me.attributes.new(nm, kind, "FACE")
        at.data.foreach_set("value", np.array(vals, np.int32 if kind == "INT" else np.float32))
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    return ob


def hulls_object(name, clouds):
    import bmesh
    bm = bmesh.new()
    for pts in clouds:
        vs = [bm.verts.new(p.tolist()) for p in pts]
        bmesh.ops.convex_hull(bm, input=vs)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    return ob


def tris(ob):
    return sum(len(p.vertices) - 2 for p in ob.data.polygons)


def grid_object(name, X, Y, Z, keep, any_=False):
    """A grid mesh of the points kept (a quad where all four corners are kept, or any one with any_)."""
    ni, nj = X.shape
    vid = np.arange(ni * nj).reshape(ni, nj)
    q = np.stack([vid[:-1, :-1], vid[1:, :-1], vid[1:, 1:], vid[:-1, 1:]], -1).reshape(-1, 4)
    k = keep.ravel()
    q = q[k[q].any(1) if any_ else k[q].all(1)]
    used = np.unique(q)
    remap = np.full(ni * nj, -1)
    remap[used] = np.arange(len(used))
    V = np.stack([X.ravel(), Y.ravel(), Z.ravel()], -1)[used]
    me = bpy.data.meshes.new(name)
    me.from_pydata(V.tolist(), [], remap[q].tolist())
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    return ob, me


def turf(rock, x0, x1, y0, y1, step=0.5):
    P = rock.P
    xs = np.arange(x0, x1 + step, step)
    ys = np.arange(y0, y1 + step, step)
    X, Y = np.meshgrid(xs, ys, indexing="ij")
    sh = X.shape
    X, Y = X.ravel(), Y.ravel()
    s, edge = P.at("s", X, Y), rock.turf_edge(X, Y)
    nx, ny, soft = P.at("nx", X, Y), P.at("ny", X, Y), P.at("soft", X, Y)
    keep = (((s < edge + 0.5 * step) | (soft > 0.5)) & ~(P.at("wet", X, Y) > 0.5)).reshape(sh)
    # every point on the cut slides onto the edge, inner corners out and outer ones in, so the edge is a line
    K = np.pad(keep, 1, constant_values=True)
    rim = keep & ~(K[:-2, 1:-1] & K[2:, 1:-1] & K[1:-1, :-2] & K[1:-1, 2:] & K[:-2, :-2] & K[2:, 2:] & K[:-2, 2:]
                   & K[2:, :-2])
    on = rim.ravel() & (np.abs(s - edge) < 1.5 * step) & (soft < 0.5)
    X = np.where(on, X - nx * (s - edge), X)
    Y = np.where(on, Y - ny * (s - edge), Y)
    Z = rock.top_at(X, Y)
    ob, me = grid_object("turf", X.reshape(sh), Y.reshape(sh), Z.reshape(sh), keep)
    # the earth scarp: the edge's vertices drawn down by the soil's depth
    import bmesh
    bm = bmesh.new()
    bm.from_mesh(me)
    edges = [e for e in bm.edges if e.is_boundary]
    S = np.array([[v.co.x, v.co.y] for v in bm.verts])
    sv = P.at("s", S[:, 0], S[:, 1]) - rock.turf_edge(S[:, 0], S[:, 1])
    lip = {v.index for v in bm.verts if sv[v.index] > -0.05}
    ext = bmesh.ops.extrude_edge_only(bm, edges=[e for e in edges if e.verts[0].index in lip
                                                 and e.verts[1].index in lip])
    for v in [g for g in ext["geom"] if isinstance(g, bmesh.types.BMVert)]:
        v.co.z -= SOIL["depthM"] + 0.15
    bm.to_mesh(me)
    bm.free()
    me.shade_smooth()
    return ob


def far_ground(rock, rock_box, turf_box):
    """The town's ground round the site at 4 m, gone where the rock's face or the turf stands. Its shore follows the
    drawn coast's true distance, so the waterline is a line, not the grid's staircase."""
    P = rock.P
    step = 4.0
    xs = np.arange(-900, 1300, step)
    ys = np.arange(-700, 1200, step)
    X, Y = np.meshgrid(xs, ys, indexing="ij")
    wet = water(X, Y)
    sx, sy = X0 - Y, Y0 + X
    d = CL._poly_dist(sx, sy, CL.COAST_LINE)
    for poly, _ in CL.ISLAND_LINES:
        d = np.minimum(d, CL._poly_dist(sx, sy, poly))
    Z = np.where(wet, np.maximum(SEA["level"] - 0.3 - FOOT["bedSlope"] * d, FOOT["bedFloor"]),
                 np.minimum(ground(X, Y) - 0.12, SEA["level"] + 0.3 + 0.25 * d))
    (a0, a1), (b0, b1) = turf_box
    in_turf = (X > a0) & (X < a1) & (Y > b0) & (Y < b1)
    turfed = np.zeros(X.shape, bool)
    xt, yt = X[in_turf], Y[in_turf]
    turfed[in_turf] = (P.at("wet", xt, yt) < 0.5) & ((P.at("s", xt, yt) < rock.turf_edge(xt, yt))
                                                     | (P.at("soft", xt, yt) > 0.5))
    in_rock = (X > rock_box[0][0] + 2) & (X < rock_box[1][0] - 2) & (Y > rock_box[0][1] + 2) & (Y < rock_box[1][1] - 2)
    shown = in_rock & ((P.at("w", X, Y) > 0.02) | wet)  # where the rock's face, foot or sea bed is the ground
    ob, me = grid_object("ground", X, Y, Z, ~(turfed | shown), any_=True)
    me.shade_smooth()
    return ob


def sea():
    bpy.ops.mesh.primitive_plane_add(size=6000, location=(0, 0, SEA["level"]))
    ob = bpy.context.object
    ob.name = "sea"
    return ob


def figure(x, y, rock, name):
    """A person, 1.75 m: a body and a head."""
    P = rock.P
    xa, ya = np.array([x], float), np.array([y], float)
    on_top = P.at("s", xa, ya)[0] < rock.turf_edge(xa, ya)[0]
    z = float(rock.top_at(xa, ya)[0] if on_top else max(P.at("foot", xa, ya)[0], SEA["level"]))
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.19, depth=1.5, location=(x, y, z + 0.75))
    body = bpy.context.object
    bpy.ops.mesh.primitive_uv_sphere_add(segments=8, ring_count=6, radius=0.12, location=(x, y, z + 1.63))
    head = bpy.context.object
    body.name, head.name = name, name + "-head"
    return [body, head]


# -- light, camera, render ---------------------------------------------------------------------------------------

def material(name, col, rough):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    p = m.node_tree.nodes["Principled BSDF"]
    p.inputs["Base Color"].default_value = (*col, 1)
    p.inputs["Roughness"].default_value = rough
    return m


def world(light):
    w = bpy.data.worlds.new("sky")
    bpy.context.scene.world = w
    w.use_nodes = True
    nt = w.node_tree
    bg = nt.nodes["Background"]
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(tc.outputs["Generated"], sep.inputs[0])
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position = 0.0
    ramp.color_ramp.elements[0].color = (0.62, 0.62, 0.64, 1)
    ramp.color_ramp.elements[1].position = 0.45
    ramp.color_ramp.elements[1].color = (0.26, 0.30, 0.38, 1)
    nt.links.new(sep.outputs["Z"], ramp.inputs[0])
    nt.links.new(ramp.outputs[0], bg.inputs["Color"])
    bg.inputs["Strength"].default_value = light.get("sky", 1.0)


def sun(light):
    import mathutils
    lamp = bpy.data.lights.new("sun", "SUN")
    lamp.energy = light["energy"]
    lamp.color = light["color"]
    lamp.angle = math.radians(1.0)
    ob = bpy.data.objects.new("sun", lamp)
    bpy.context.scene.collection.objects.link(ob)
    az, el = math.radians(light["azimuth"]), math.radians(light["elevation"])
    d = np.array([math.sin(az) * math.cos(el), math.cos(az) * math.cos(el), math.sin(el)])
    ob.rotation_euler = mathutils.Vector(tuple(-d)).to_track_quat("-Z", "Y").to_euler()


def camera(view, rock):
    import mathutils
    P = rock.P
    p = view["pos"]
    if len(p) == 2:
        z = max(float(P.at("foot", np.array([p[0]]), np.array([p[1]]))[0]), SEA["level"]) + view["eye"]
        p = [p[0], p[1], z]
    cam = bpy.data.cameras.new("cam")
    cam.lens = view["lens"]
    cam.clip_end = 6000
    ob = bpy.data.objects.new("cam", cam)
    bpy.context.scene.collection.objects.link(ob)
    ob.location = p
    ob.rotation_euler = (mathutils.Vector(view["target"]) - mathutils.Vector(p)).to_track_quat("-Z", "Y").to_euler()
    bpy.context.scene.camera = ob
    print("camera", [round(c, 2) for c in p])


def cycles(w, h, samples):
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    try:
        prefs = bpy.context.preferences.addons["cycles"].preferences
        prefs.compute_device_type = "METAL"
        prefs.get_devices()
        for d in prefs.devices:
            d.use = True
        sc.cycles.device = "GPU"
    except Exception as e:  # noqa: BLE001
        print("GPU unavailable:", e)
    sc.cycles.samples = samples
    sc.cycles.use_denoising = True
    sc.render.resolution_x, sc.render.resolution_y = w, h
    sc.view_settings.view_transform = "AgX"
    sc.view_settings.look = "AgX - Base Contrast"
    sc.view_settings.exposure = float(arg("--exposure", -0.8))


def main():
    out = arg("--out")
    os.makedirs(out, exist_ok=True)
    t = time.time()
    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o)
    box = [(-58.0, -60.0, BED), (206.0, 80.0, 33.0)]
    plan = Plan(box[0][0] - 45, box[1][0] + 5, box[0][1] - 45, box[1][1] + 5)
    print(f"plan fields: {time.time() - t:.1f}s, crest {plan.length:.0f} m")
    rock = Rock(plan, box)
    bodies, falls = rock.build()
    ro = faces_object("rock", bodies)
    fo = faces_object("fallen", fallen(rock, falls))
    bo = hulls_object("boulders", boulders(rock))
    n = {k: tris(o) for k, o in (("rock", ro), ("fallen", fo), ("boulders", bo))}
    total = sum(n.values())
    print(f"triangles: {n}, total {total}; budget {FIX['budget']['trisL1']}"
          f" -> {'within' if total <= FIX['budget']['trisL1'] else 'OVER'}")
    tb = ((box[0][0] - 40, box[1][0]), (box[0][1] - 40, box[1][1]))
    tu = turf(rock, tb[0][0], tb[0][1], tb[1][0], tb[1][1])
    gr = far_ground(rock, box, tb)
    se = sea()
    grey = material("clay", (0.20, 0.20, 0.20), 0.8)
    for ob in (ro, fo, bo, tu, gr):
        ob.data.materials.clear()
        ob.data.materials.append(grey)
    se.data.materials.append(material("sea", (0.02, 0.025, 0.03), 0.12))
    for k, (x, y) in enumerate(FIX.get("figures", [])):
        for f in figure(x, y, rock, f"fig{k}"):
            f.data.materials.append(grey)
    light = FIX["lights"]["lowsun"]
    world(light)
    sun(light)
    views = {vw["name"]: vw for vw in FIX["views"]}
    cycles(int(arg("--w", 1600)), int(arg("--h", 900)), int(arg("--samples", 64)))
    if arg("--blend"):
        bpy.ops.wm.save_as_mainfile(filepath=arg("--blend"))
    for name in arg("--view", "foot").split(","):
        for o in [o for o in bpy.data.objects if o.type == "CAMERA"]:
            bpy.data.objects.remove(o)
        camera(views[name], rock)
        bpy.context.scene.render.filepath = os.path.join(out, f"{name}-grey.png")
        bpy.ops.render.render(write_still=True)
        print("wrote", bpy.context.scene.render.filepath, f"{time.time() - t:.0f}s")


if __name__ == "__main__":
    main()
