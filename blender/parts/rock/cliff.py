"""The Bluff's land as its history made it: the forms first, so that the cover can follow from their causes.

In order (fixtures/lt1-bluff.json, land):
1. The mass. The hill's rock under its soil. The face stands on the plan's crest line with the fixture's section: a
   sea-cut lower wall, a ledge and an upper slope. It wanders slowly along the crest. Where the top's water went over
   the edge along a steep joint, a gully runs down the face, deepest at the crest, so the face is buttresses and
   gullies rather than a wall.
2. The ice rounded every convex edge of the old mass.
3. The sea since. A notch at the face's foot where storms reach it; grooves worn into the soft foliation slabs of the
   shore; caves along the foliation; clefts along J3.
4. Frost and gravity took blocks out of the face along its joints. Each fracture is a finite plane of its family,
   turned from the family's mean by a seeded spread and sized by a power law, so a few big planes and many small ones
   overlap at every scale (a discrete fracture network, as engineering geology models a rock mass). A fracture that
   faces out of the rock took the block between it, the two cross families most nearly square to it and the free
   face; one that faces into the rock held. The dated falls are the fixture's acts.
5. Weather rounds each scar's edges by its years, and the sea rounds what it reaches.
6. The blocks lie on the foot where they fell. They lie flat on their broad side, sharp or rounded by their years, the
   bigger ones thrown farther. The old stones lie in the coves and the tide.

The rock is a signed distance, sampled in bricks into an OpenVDB grid and meshed by Blender's Volume to Mesh. Loose
bits and the faces hidden under the turf are dropped. The rest is collapsed to the triangle count asked, and its
normals are weighted by face area, so the planes shade flat. Every face carries the fact that made it, which the
material reads:
- plane: the family whose fracture it is (0 to 3), the top (4), the foot (5), worn by ice or sea (6), a fallen
  block (7);
- age: its years bare;
- gap: its joint's opening.

    Blender -b --factory-startup -P blender/parts/rock/cliff.py -- --out DIR [--view cave,raised] [--w 1600]
        [--h 900] [--samples 32] [--exposure -0.8] [--dense 1] [--reuse 1]
"""

import math
import os
import sys
import time

import bpy
import numpy as np
import openvdb as vdb

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import bluff as BL  # noqa: E402
import hashing as HS  # noqa: E402

FIX, SEA, FOOT, FACE, SOIL, ROCK = BL.FIX, BL.SEA, BL.FOOT, BL.FACE, BL.SOIL, BL.ROCK
LAND = FIX["land"]
NAMES = [f["name"] for f in ROCK["families"]]
TOP, FOOTK, WORN, BLOCK = 4, 5, 6, 7
GOVB = 1_000_000  # a block's index in `gov` starts here
OLD = float(LAND["weather"]["sinceIceYears"])
arg = BL.arg
smooth = BL.smooth


def smin(a, b, k):
    h = np.clip(0.5 + 0.5 * (b - a) / k, 0.0, 1.0)
    return b + (a - b) * h - k * h * (1 - h)


def smax(a, b, k):
    return -smin(-a, -b, k)


def unit(v):
    return v / np.linalg.norm(v)


def spread(n, deg, g):
    """n turned by a seeded angle (half-normal, deg) about a seeded axis square to it."""
    t = unit(np.cross(n, [0.0, 0.0, 1.0]) if abs(n[2]) < 0.9 else np.cross(n, [1.0, 0.0, 0.0]))
    b = np.cross(n, t)
    a = g.uniform(0, 2 * math.pi)
    th = math.radians(abs(g.normal(0, deg)))
    return unit(n * math.cos(th) + (t * math.cos(a) + b * math.sin(a)) * math.sin(th))


def rbox(Q, C, R, half, r):
    q = np.abs((Q - C) @ R) - (half - r)
    return np.linalg.norm(np.maximum(q, 0), axis=-1) + np.minimum(np.max(q, -1), 0) - r


class Land(BL.Rock):
    def __init__(self, plan, box):
        super().__init__(plan, box)
        self.nf = {f["name"]: BL.H.normal(f["dip"], f["dipToward"]) for f in ROCK["families"]}
        self.gullies = self.make_gullies()
        self.clefts = self.make_clefts()
        self.D = None
        self.blocks = []

    # 1. the mass

    def make_gullies(self):
        G = LAND["gullies"]
        rng = HS.Stream("lt1-bluff", "gullies")
        out = []
        u = rng.uniform(*G["spacingM"]) * 0.5
        while u < self.P.length - 10.0:
            c = BL.point_on_crest(u)
            t = unit(BL.point_on_crest(u + 1.0) - c)
            fam = max(("J1", "J3", "foliation"), key=lambda k: abs(unit(self.nf[k][:2]) @ t))
            m = unit(self.nf[fam][:2])
            a = math.radians(rng.normal(0, G["spreadDeg"]))
            m = np.array([m[0] * math.cos(a) - m[1] * math.sin(a), m[0] * math.sin(a) + m[1] * math.cos(a)])
            out.append(dict(c=c, m=m, p=np.array([-m[1], m[0]]), d=rng.uniform(*G["depthM"]),
                            w=rng.uniform(*G["widthM"]) / 2))
            u += rng.uniform(*G["spacingM"])
        return out

    def exposure(self, x, y):
        nx, ny = self.P.at("nx", x, y), self.P.at("ny", x, y)
        E = SEA["exposure"]
        e = np.where(ny > 0, E["north"], E["south"]) * ny ** 2 + np.where(nx > 0, E["east"], E["west"]) * nx ** 2
        return e / np.maximum(nx ** 2 + ny ** 2, 1e-6)

    def bay(self, P):
        """How far the face stands back of its section: the slow wander, the gullies (deepest at the crest, where the
        water went over) and the storm notch at the foot."""
        x, y, z = P[..., 0], P[..., 1], P[..., 2]
        u = self.P.at("u", x, y)
        a, b = LAND["wanderM"]
        g = a + (b - a) * BL.vnoise(u / LAND["wanderCellM"], "wander")
        H = np.maximum(self.P.at("top", x, y) - FACE["footZ"], 1.0)
        up = 0.25 + 0.75 * smooth(0.0, 0.8, (z - FACE["footZ"]) / H)
        for gl in self.gullies:
            qx, qy = x - gl["c"][0], y - gl["c"][1]
            t = np.abs(qx * gl["m"][0] + qy * gl["m"][1]) / gl["w"]
            along = 1 - smooth(18.0, 28.0, np.abs(qx * gl["p"][0] + qy * gl["p"][1]))
            g = g + np.where(t < 1, gl["d"] * (1 - np.minimum(t, 1) ** 2) ** 2, 0.0) * up * along
        N = LAND["notch"]
        depth = N["depthM"][0] + (N["depthM"][1] - N["depthM"][0]) * self.exposure(x, y)
        return g + depth * np.exp(-((z - N["z"]) / N["hM"]) ** 2)

    def groove(self, x, y, z, slope=False):
        """How far the sea wore the shore down at a point: the soft foliation slabs in the tide and the spray; with
        slope, also how steep the groove's wall is there."""
        R = LAND["ribs"]
        i, l, hw = self.slab("foliation", np.stack([x, y, z], -1))
        soft = BL.cell_random([i], 31) < R["softShare"]
        depth = R["depthM"][0] + (R["depthM"][1] - R["depthM"][0]) * BL.cell_random([i], 32)
        tide = 1 - smooth(R["topZ"] - 1.0, R["topZ"], z)
        k = np.where(soft, depth, 0.0) * tide * (1 - self.P.at("wet", x, y) * 0.5)
        t = np.clip((hw - np.abs(l)) / R["edgeM"], 0.0, 1.0)
        g = k * t * t * (3 - 2 * t)
        return (g, k * 6 * t * (1 - t) / R["edgeM"]) if slope else g

    def rest(self, x, y, R, half):
        """The height a block rests at: on the highest of the shore under its corners."""
        c = np.array([[sx * half[0], sy * half[1], 0.0] for sx in (-1, 0, 1) for sy in (-1, 0, 1)]) @ R.T
        X, Y = x + c[:, 0], y + c[:, 1]
        zf = self.P.at("foot", X, Y)
        return float(np.max(zf - self.groove(X, Y, zf)))

    def mass(self, x, y, z):
        """The rock's distance before the frost, and which surface governs: the face (worn by the ice and the sea),
        the top under its soil, the foot with its grooves."""
        P = self.P
        s, u, w = P.at("s", x, y), P.at("u", x, y), P.at("w", x, y)
        Q = np.stack([x, y, z], -1)
        wg = smooth(0.1, 0.4, w)
        face = np.where(w > 0, (s - (self.face_line(z, u) - self.bay(Q) * wg)) * 0.92, 1e3)  # its height is w's
        zt, zf = self.top_at(x, y, s) - SOIL["depthM"], P.at("foot", x, y)
        top = z - zt
        g, gs = self.groove(x, y, z, slope=True)
        foot = (z - (zf - g)) / np.sqrt(1 + gs * gs)  # a height's distance, over its slope
        ice = LAND["ice"]
        k = np.clip(ice["heightShare"] * (zt - zf), 0.3, ice["roundM"])
        d = smin(foot, smax(top, face, k), ice["footRoundM"])
        kind = np.where(foot < np.maximum(top, face), FOOTK, np.where(top > face, TOP, WORN))
        return d, kind

    # 3. the sea's own cuts

    def make_clefts(self):
        out = []
        for k, cl in enumerate(FIX["clefts"]["list"]):
            g = np.random.default_rng(HS.h("lt1-bluff", "cleft", k) & 0xFFFFFFFF)
            c = BL.point_on_crest(cl["u"])
            t = unit(BL.point_on_crest(cl["u"] + 1.0) - c)
            out.append(dict(c=np.array([c[0], c[1], 0.0]), m=spread(self.nf["J3"], 5.0, g),
                            into=np.array([t[1], -t[0], 0.0]), w=cl["widthM"] / 2, d=cl["depthM"]))
        return out

    def sea_cut(self, Q):
        d = np.full(len(Q), 1e3)
        z = Q[:, 2]
        for act in self.acts:
            if act["kind"] == "cave":
                d = np.minimum(d, self.cave(act, Q))
        for cl in self.clefts:
            q = Q - cl["c"]
            up = smooth(FACE["footZ"], 22.0, z)
            d = np.minimum(d, np.maximum.reduce([np.abs(q @ cl["m"]) - cl["w"] * (0.75 + 0.35 * up),
                                                 q @ cl["into"] - cl["d"] * (1 - 0.45 * up),
                                                 SEA["level"] - 1.2 - z]))
        return d

    # 4. frost and gravity: the fractures that took blocks

    def starts(self, box, h=0.5, shell=0.5, c=2.0):
        """Where fractures may start: in each cell of an h lattice, one seeded point, kept if it lies within shell/2 of
        the face. Each start is keyed by its cell, so a change to the rock moves only the starts where the face moved
        (the coarse c cells first find the face)."""
        lo, hi = np.array(box[0], float), np.array(box[1], float)
        n = np.ceil((hi - lo) / c).astype(int)
        Ic = np.stack(np.meshgrid(*[np.arange(k) for k in n], indexing="ij"), -1).reshape(-1, 3)
        C = lo + (Ic + 0.5) * c
        d = np.concatenate([self.mass(*C[i:i + 300_000].T)[0] for i in range(0, len(C), 300_000)])
        Ic = Ic[np.abs(d) < 2.5 * c]  # the top's and the foot's terms are heights, steeper than distances
        f = int(round(c / h))
        sub = np.stack(np.meshgrid(*[np.arange(f)] * 3, indexing="ij"), -1).reshape(-1, 3)
        J = (Ic[:, None, :] * f + sub[None]).reshape(-1, 3)
        X = lo + (J + np.stack([BL.cell_random(list(J.T), 40 + k) for k in range(3)], -1)) * h
        keep, kinds = [], []
        for i in range(0, len(X), 300_000):
            x = X[i:i + 300_000]
            dd, kind = self.mass(*x.T)
            ok = (np.abs(dd) < shell / 2) & (x[:, 2] > BL.BED + 0.5)
            ok &= self.sea_cut(x) > 0.3
            T = ok & (kind == TOP)
            if T.any():
                sc = self.crest_s(x[T, 0], x[T, 1])
                ok[np.where(T)[0][self.P.at("s", x[T, 0], x[T, 1]) < sc - 3.0]] = False
            keep.append(ok)
            kinds.append(kind)
        keep = np.concatenate(keep)
        return X[keep], J[keep], np.concatenate(kinds)[keep], keep.sum() * h ** 3 / shell

    def fracture(self, box):
        F = LAND["fractures"]
        S, SJ, SK, area = self.starts(box)
        print(f"fractures: face {area:.0f} m2, {len(S)} starts")
        h = 0.3
        grad = np.stack([(self.mass(*(S + e * h).T)[0] - self.mass(*(S - e * h).T)[0]) / (2 * h)
                         for e in np.eye(3)], -1)
        out0 = grad / np.maximum(np.linalg.norm(grad, axis=1, keepdims=True), 1e-6)
        fams = NAMES
        wts = np.array([F["shares"][k] for k in fams])
        wts = wts / wts.sum()
        rec = {k: [] for k in ("c", "n", "m1", "m2", "a", "b", "h", "k", "age", "fam", "gap", "R")}
        self.D = None
        self.bc, self.br, self.blocks = np.zeros((0, 3)), np.zeros(0), []
        side = sum(F["sideM"]) / 2
        for o_, oc in enumerate(F["octaves"]):
            r0, r1 = oc["rM"]
            rm = (r0 + r1) / 2
            n_oc = int(oc["cover"] * area / (4 * side ** 2 * rm ** 2))
            # each start tried in its own seeded order, with its own draws
            pick = np.argsort(BL.cell_random(list(SJ.T), 50 + o_))
            if r0 >= F["tabularBelowM"]:  # the sea plucks slabs from the foot, never the face's big blocks
                pick = pick[SK[pick] != FOOTK]
            pick = pick[:3 * n_oc + 50]
            seeds = (BL.cell_random(list(SJ[pick].T), 60 + o_) * 2.0 ** 53).astype(np.int64)
            P0, O0 = S[pick], out0[pick]
            # onto the face as the bigger breaks left it
            d0 = self.at(P0, track=False)[0] if self.D is not None else np.zeros(len(P0))
            Pc = P0 - O0 * d0[:, None]
            hs = 0.2
            st = np.concatenate([Pc] + [Pc + s * hs * e for e in np.eye(3) for s in (1, -1)]
                                + [Pc + s * F["edge"]["scale"] * rm * e for e in np.eye(3) for s in (1, -1)])
            dd = (self.at(st, track=False)[0] if self.D is not None else self.mass(*st.T)[0]).reshape(13, -1)
            on = np.stack([dd[1] - dd[2], dd[3] - dd[4], dd[5] - dd[6]], -1)
            on /= np.maximum(np.linalg.norm(on, axis=1, keepdims=True), 1e-6)
            conv = (dd[7:].sum(0) - 6 * dd[0]) / (6 * F["edge"]["scale"] * rm)
            c0, c1 = F["edge"]["c"]
            chance = oc["floor"] + (1 - oc["floor"]) * smooth(c0, c1, conv)
            took = 0
            for p, o, ch, dp, sd in zip(Pc, on, chance, dd[0], seeds):
                if took >= n_oc:
                    break
                g = np.random.default_rng(int(sd))
                if abs(dp) > 0.35 or g.random() > ch:
                    continue
                if self.cut_at(rec, p, o, g.uniform(r0, r1), g):
                    took += 1
                    self.D = {k: np.array(v) for k, v in rec.items()}
            self.D = {k: np.array(v) for k, v in rec.items()}
            print(f"  octave {r0}-{r1} m: {took} of {n_oc} taken")
        for act in self.acts:
            if act["kind"] == "rockfall":
                self.add_fall(rec, act, np.random.default_rng(HS.h("lt1-bluff", act["id"], "fall") & 0xFFFFFFFF))
        D = {k: np.array(v) for k, v in rec.items()}
        order = np.argsort(-D["age"])  # oldest first
        self.D = {k: v[order] for k, v in D.items()}
        print(f"fractures: {len(self.D['age'])} cuts")

    def cut_at(self, rec, p, on, r, g):
        """The block a fracture of size r took at p, if one faces out of the rock there."""
        F = LAND["fractures"]
        fam = None
        for _ in range(4):
            f = NAMES[g.choice(len(NAMES), p=np.array([F["shares"][k] for k in NAMES]) / sum(F["shares"].values()))]
            nn = spread(self.nf[f], F["spreadDeg"], g)
            nn = nn if nn @ on > 0 else -nn
            if nn @ on >= F["facing"]:
                fam = f
                break
        if fam is None:
            return False
        fol = ROCK["families"][NAMES.index("foliation")]
        if r < F["tabularBelowM"] and fam != "foliation":
            # a slab of the foliation: its thickness from the foliation's spacing
            third = min((k for k in NAMES if k not in (fam, "foliation")), key=lambda k: abs(self.nf[k] @ nn))
            m1, m2 = spread(self.nf["foliation"], F["spreadDeg"], g), spread(self.nf[third], F["spreadDeg"], g)
            a = min(g.uniform(*fol["spacingM"]) / 2, r)
        else:
            k1, k2 = sorted((k for k in NAMES if k != fam), key=lambda k: abs(self.nf[k] @ nn))[:2]
            m1, m2 = spread(self.nf[k1], F["spreadDeg"], g), spread(self.nf[k2], F["spreadDeg"], g)
            a = r * g.uniform(*F["sideM"])
        a, b = max(a, F["minSideM"]), max(r * g.uniform(*F["sideM"]), F["minSideM"])
        if abs(np.linalg.det(np.array([nn, m1, m2]))) < 0.3:
            return False
        dep = min(max(g.uniform(*F["depth"]) * r, F["minDepthM"]), F["maxDepthM"])
        if not self.stands(p, on, p - on * dep, nn, m1, m2, a, b, dep):
            return False
        hcap = dep / max(nn @ on, 0.3) + 0.5 * r + 1.0
        age = OLD * g.random() ** F["ageShape"]
        share, g0, g1 = ROCK["families"][NAMES.index(fam)].get("open", [0, 0, 0])
        gap = g.uniform(g0, g1) if g.random() < share else 0.0
        self.add_cut(rec, p - on * dep, nn, m1, m2, a, b, hcap, age, NAMES.index(fam), r, gap)
        return True

    def stands(self, p, on, c, nn, m1, m2, a, b, dep):
        """Whether the rock a block at p leaves can stand: no overhang deeper than overhangM over its roof, and no fin
        thinner than finM beside it."""
        F = LAND["fractures"]
        q = p - c
        sides = [(s * m, ext - s * (q @ m)) for m, ext in ((m1, a), (m2, b)) for s in (1, -1)]
        pts, tests = [], []
        roof, dr = max(sides, key=lambda t: t[0][2])
        if roof[2] > 0.5 and dep > F["overhangM"]:
            pts.append(p + roof * (dr + 0.25) - on * 0.3 * dep)
            tests.append("roof")
        for u, du in sides:
            if abs(u[2]) < 0.7:
                base = p + u * du - on * 0.25
                w = unit(u - on * (u @ on))  # across the face, at the same depth behind it
                pts += [base + w * 0.2, base + w * F["finM"]]
                tests.append("fin")
        if not pts:
            return True
        d = self.at(np.array(pts), track=False)[0] if self.D is not None else self.mass(*np.array(pts).T)[0]
        i = 0
        for t in tests:
            if t == "roof":
                if d[i] < 0:
                    return False
                i += 1
            else:
                if d[i] < 0 and d[i + 1] > 0:
                    return False
                i += 2
        return True

    def add_cut(self, rec, c, nn, m1, m2, a, b, hcap, age, fam, r, gap):
        W = LAND["weather"]
        k = W["roundM"][0] + (W["roundM"][1] - W["roundM"][0]) * math.log1p(age) / math.log1p(OLD)
        sea = 1 - float(smooth(W["seaTopZ"] - 1.5, W["seaTopZ"] + 1.5, c[2]))
        k += W["seaRoundM"] * sea * float(self.exposure(np.array([c[0]]), np.array([c[1]]))[0])
        k = max(min(k, 0.4 * r), 0.5 * LAND["voxelM"])  # finer rounding than half a voxel is the normal map's
        M = np.array([nn, m1, m2])
        Minv = np.linalg.inv(M)
        V = np.array([[s0, s1 * a, s2 * b] for s0 in (0.0, hcap) for s1 in (-1, 1) for s2 in (-1, 1)]) @ Minv.T
        for key, v in (("c", c), ("n", nn), ("m1", m1), ("m2", m2), ("a", a), ("b", b), ("h", hcap), ("k", k),
                       ("age", age), ("fam", fam), ("gap", gap), ("R", np.linalg.norm(V, axis=1).max() + k)):
            rec[key].append(v)

    def add_fall(self, rec, act, g):
        """A dated fall: the block between the steep joint that faces out most, the cross joint square to it and
        two low joints, and a few smaller breaks inside its scar."""
        age = FIX["date"] - act["year"]
        u = act["_u"]
        z0, z1 = act["zM"]
        zc = (z0 + z1) / 2
        c2 = BL.point_on_crest(u)
        on = np.array([act["_n"][0], act["_n"][1], 0.0])
        s = float(self.face_line(np.array([zc]), np.array([u]))[0])
        p = np.array([c2[0], c2[1], zc]) + on * s
        steep = [k for k in NAMES if k != "L"]
        back = max(steep, key=lambda k: abs(self.nf[k] @ on))
        side = min((k for k in steep if k != back), key=lambda k: abs(self.nf[k] @ self.nf[back]))
        nn = self.nf[back] if self.nf[back] @ on > 0 else -self.nf[back]
        for k in range(1 + 3):
            big = k == 0
            sc = 1.0 if big else g.uniform(0.25, 0.45)
            q = p if big else p + g.uniform(-0.3, 0.3, 3) * np.array([act["widthM"], act["widthM"], z1 - z0])
            dep = act["depthM"] * (1.0 if big else g.uniform(0.2, 0.5))
            n1 = spread(nn, 4.0, g)
            m1 = spread(self.nf[side], 4.0, g)
            m2 = spread(self.nf["L"], 4.0, g)
            a, b = act["widthM"] / 2 * sc, (z1 - z0) / 2 * sc
            self.add_cut(rec, q - on * dep, n1, m1, m2, a, b, dep / max(n1 @ on, 0.3) + 4.0, age,
                         NAMES.index(back), max(a, b), 0.0)

    # 5. what cannot stand

    def topple(self):
        """What cannot stand falls (the fixture's topple): each column too slender for phyllite breaks off along a low
        joint at its foot, between the steep joints round it, and lies at its foot as blocks."""
        T = LAND["topple"]
        st = T["stepM"]
        P = self.P
        X, Y = np.meshgrid(np.arange(BOX[0][0], BOX[1][0], st), np.arange(BOX[0][1], BOX[1][1], st), indexing="ij")
        near = self.crest_s(X, Y) - P.at("s", X, Y) < 3.0
        H = self.top_at(X, Y) - SOIL["depthM"]
        zt = rock_top(self, X[near], Y[near], np.full(near.sum(), BOX[1][2]), up=0.0, down=BOX[1][2] - BL.BED, dz=st)
        H[near] = np.where(np.isnan(zt), BL.BED, zt)
        r = int(round(T["widthM"] / st))
        offs = [(i, j) for i in range(-r, r + 1) for j in range(-r, r + 1) if i * i + j * j <= r * r]

        def filt(A, f):
            Pd = np.pad(A, r, mode="edge")
            out = A.copy()
            for i, j in offs:
                out = f(out, Pd[r + i:r + i + A.shape[0], r + j:r + j + A.shape[1]])
            return out

        O = filt(filt(H, np.minimum), np.maximum)
        M = near & (H - O > T["heightM"])
        lab, n = np.zeros(M.shape, int), 0
        for s0 in zip(*np.where(M)):
            if lab[s0]:
                continue
            n += 1
            lab[s0], stack = n, [s0]
            while stack:
                i, j = stack.pop()
                for a_, b_ in ((i + 1, j), (i - 1, j), (i, j + 1), (i, j - 1)):
                    if 0 <= a_ < M.shape[0] and 0 <= b_ < M.shape[1] and M[a_, b_] and not lab[a_, b_]:
                        lab[a_, b_] = n
                        stack.append((a_, b_))
        rec = {k: list(v) for k, v in self.D.items()}
        nn = self.nf["L"] if self.nf["L"][2] > 0 else -self.nf["L"]
        m1, m2 = self.nf["J1"], self.nf["J3"]
        fell, area = 0, 0.0
        for k in range(1, n + 1):
            sel = lab == k
            ring = np.zeros_like(sel)
            ring[1:] |= sel[:-1]
            ring[:-1] |= sel[1:]
            ring[:, 1:] |= sel[:, :-1]
            ring[:, :-1] |= sel[:, 1:]
            ring &= ~sel
            if sel.sum() < 2 or H[ring].max() > H[sel].max() - T["heightM"]:
                continue  # held by the rock beside it: a buttress stands
            i0, j0 = np.argwhere(sel)[0]  # the column's own draws, keyed by where it stands
            g = np.random.default_rng(HS.h("lt1-bluff", "topple", int(i0), int(j0)) & 0xFFFFFFFF)
            px, py = X[sel], Y[sel]
            zb, ztop = float(np.median(O[sel])) + T["stumpM"], float(H[sel].max())
            c = np.array([px.mean(), py.mean(), zb])
            pts = np.concatenate([np.stack([px, py, np.full(len(px), z)], -1) for z in (zb, ztop)]) - c
            mg = T["marginM"] + st / 2
            a, b = np.abs(pts @ m1).max() + mg, np.abs(pts @ m2).max() + mg
            age = OLD * g.random() ** LAND["fractures"]["ageShape"]
            self.add_cut(rec, c, nn, m1, m2, a, b, (pts @ nn).max() + 1.0, age, NAMES.index("L"), max(a, b), 0.0)
            self.lay(c, sel.sum() * st * st * (ztop - zb), ztop - zb, age, g)
            fell += 1
            area += sel.sum() * st * st
        self.settle(rec)
        print(f"topple: {fell} columns fell, {area:.0f} m2 of them")

    def settle(self, rec):
        """The cuts oldest first again, and the blocks' index refreshed, after a pass added to them."""
        D = {k: np.array(v) for k, v in rec.items()}
        order = np.argsort(-D["age"])
        self.D = {k: v[order] for k, v in D.items()}
        self.bc = np.array([b[0] for b in self.blocks])
        self.br = np.array([np.linalg.norm(b[2]) for b in self.blocks])

    def lay(self, c, vol, fall, age, g):
        """What fell at c (its volume, from fall metres up) as a few blocks at the foot seaward of it, tilted as they
        landed, their edges rounded by their years in the swash."""
        r0, r1 = LAND["weather"]["blockRound"]
        fr = BL.crest_frame(c[:1], c[1:2])
        out = np.array([fr[2][0], fr[3][0]])
        nb = int(np.clip(round(vol / 1.5), 1, 5))
        L = float(np.clip((vol / nb / 0.29) ** (1 / 3), 0.5, 2.5))
        half = np.array([L, 0.8 * L, 0.45 * L]) / 2
        for _ in range(nb):
            x, y = c[:2] + out * g.uniform(1.0, 1.0 + 0.5 * fall) + g.uniform(-1.0, 1.0, 2)
            tilt = math.radians(14 if age < 30 else 6)
            R = BL.rot(g.uniform(0, 2 * math.pi), g.normal(0, tilt), g.normal(0, tilt))
            rr = float(min(half)) * (r0 + (r1 - r0) * min(age / LAND["weather"]["blockRoundYears"], 1.0))
            self.blocks.append((np.array([x, y, self.rest(x, y, R, half) + half[2] * 0.75]), R, half,
                                max(rr, 0.02), float(age)))

    def overhangs(self):
        """What cannot stand, too (the fixture's overhang): a roof (rock with air under it) stands out from the rock
        that holds it no farther than share of its own thickness. What holds it is rock at its mid height that stands
        on the bed, or a standing roof stiffK times as thick. Beyond that it broke at the steep joint most nearly
        square to its reach, in pieces between the cross joints, and lies at the foot."""
        T = LAND["overhang"]
        st, dz, cap = T["stepM"], T["dzM"], T["capM"]
        t0 = time.time()
        X, Y = np.meshgrid(np.arange(BOX[0][0], BOX[1][0], st), np.arange(BOX[0][1], BOX[1][1], st), indexing="ij")
        near = self.crest_s(X, Y) - self.P.at("s", X, Y) < T["bandM"]
        Z = np.arange(BL.BED + dz / 2, BOX[1][2], dz)  # the layers, bottom up
        nz, kk = len(Z), np.arange(len(Z))
        x, y = X[near], Y[near]
        Rn = np.empty((len(x), nz), bool)
        for part in np.array_split(np.arange(len(x)), max(1, len(x) * nz // 3_000_000)):
            Q = np.stack([np.repeat(x[part], nz), np.repeat(y[part], nz), np.tile(Z, len(part))], -1)
            Rn[part] = (self.at(Q, track=False)[0] < 0).reshape(len(part), nz)
        R = np.ones(X.shape + (nz,), bool)  # inland of the band the land stands whole
        R[near] = Rn
        del Rn

        def runs(A):
            """Each layer's run of A along z: its bottom and top layer."""
            lo = np.concatenate([np.zeros(A.shape[:2] + (1,), bool), A[..., :-1]], -1)
            hi = np.concatenate([A[..., 1:], np.zeros(A.shape[:2] + (1,), bool)], -1)
            bot = np.maximum.accumulate(np.where(A & ~lo, kk, -1), axis=-1)
            top = np.flip(np.minimum.accumulate(np.flip(np.where(A & ~hi, kk, nz), -1), axis=-1), -1)
            return bot, top

        ab, at_ = runs(~R)  # a gap lower than gapM between rock is no roof's air: the rock bears across it
        R |= ~R & (ab > 0) & (at_ < nz - 1) & ((at_ - ab + 1) * dz < T["gapM"])
        bot, top = runs(R)
        t = (top - bot + 1) * dz
        grounded = R & (bot == 0)
        roof = R & ~grounded
        mid = (bot + top) // 2
        q = roof & (kk == mid)  # each roof asks once, at its mid height
        lim = np.maximum(T["minM"], T["share"] * t)
        lay_k = np.unique(np.nonzero(q)[2])

        def reach(S, ks):
            """Plan distance (m) from each cell to the nearest S in its layer, for the layers ks; capped at cap."""
            D = np.where(S[..., ks], 0.0, cap).astype(np.float32)
            n, m = D.shape[:2]
            for _ in range(int(cap / st) + 1):
                moved = False
                for di, dj in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)):
                    c = st * math.hypot(di, dj)
                    dst = D[max(di, 0):n + min(di, 0), max(dj, 0):m + min(dj, 0)]
                    new = np.minimum(dst, D[max(-di, 0):n + min(-di, 0), max(-dj, 0):m + min(-dj, 0)] + c)
                    moved |= bool((new < dst).any())
                    dst[...] = new
                if not moved:
                    break
            return D

        D1 = reach(grounded, lay_k)
        falls = np.zeros(R.shape, bool)
        falls[..., lay_k] = q[..., lay_k] & (D1 > lim[..., lay_k])
        standing = roof & ~np.take_along_axis(falls, mid, -1)
        k_ = 1.0  # a thinner roof leans on a standing one stiffK times as thick: once more, by classes of thickness
        while falls.any() and k_ <= t.max():
            cls = falls & (t <= k_) & (t > k_ / 2 if k_ > 1.0 else True)
            ks = np.unique(np.nonzero(cls)[2])
            if len(ks):
                D2 = reach(grounded | (standing & (t >= T["stiffK"] * k_)), ks)
                falls[..., ks] &= ~(cls[..., ks] & (D2 <= lim[..., ks]))
            k_ *= 2
        F = roof & np.take_along_axis(falls, mid, -1)
        held = R & ~F
        print(f"overhang: {q.sum()} roofs, {int(falls.sum())} cannot stand ({F.sum() * st * st * dz:.0f} m3); "
              f"{time.time() - t0:.0f}s")
        # the pieces: what fell together (touching), then cut between the cross joints
        lab = np.zeros(F.shape, np.int32)
        n = 0
        for s0 in zip(*np.nonzero(F)):
            if lab[s0]:
                continue
            n += 1
            lab[s0], stack = n, [s0]
            while stack:
                i, j, k = stack.pop()
                for a_, b_, c_ in ((i + 1, j, k), (i - 1, j, k), (i, j + 1, k), (i, j - 1, k), (i, j, k + 1),
                                   (i, j, k - 1)):
                    if (0 <= a_ < F.shape[0] and 0 <= b_ < F.shape[1] and 0 <= c_ < nz and F[a_, b_, c_]
                            and not lab[a_, b_, c_]):
                        lab[a_, b_, c_] = n
                        stack.append((a_, b_, c_))
        rec = {k: list(v) for k, v in self.D.items()}
        up = self.nf["L"] if self.nf["L"][2] > 0 else -self.nf["L"]
        steep = [f for f in NAMES if abs(self.nf[f][2]) < 0.5]
        gx, gy = np.gradient(D1, st, axis=(0, 1))  # outward: away from what holds it, at each roof's mid height
        fell, vol_all, kept = 0, 0.0, 0
        for comp in range(1, n + 1):
            I = np.argwhere(lab == comp)
            g = np.random.default_rng(HS.h("lt1-bluff", "overhang", *map(int, I[0])) & 0xFFFFFFFF)
            Pv = np.stack([X[I[:, 0], I[:, 1]], Y[I[:, 0], I[:, 1]], Z[I[:, 2]]], -1)
            Im = (I[:, 0], I[:, 1], np.searchsorted(lay_k, mid[tuple(I.T)]))
            away = np.array([gx[Im].sum(), gy[Im].sum(), 0.0])
            if np.linalg.norm(away) < 1e-6:
                fr = BL.crest_frame(Pv[:1, 0], Pv[:1, 1])
                away = np.array([fr[2][0], fr[3][0], 0.0])
            away = unit(away)
            fam = max(steep, key=lambda f: abs(self.nf[f] @ away))
            nn = self.nf[fam] if self.nf[fam] @ away > 0 else -self.nf[fam]
            side = min((f for f in steep if f != fam), key=lambda f: abs(self.nf[f] @ nn))
            m1, m2 = self.nf[side], up
            cell = np.floor(np.stack([Pv @ m1, Pv @ nn], -1) / T["pieceM"]).astype(int)  # between the joints
            age = OLD * g.random() ** LAND["fractures"]["ageShape"]
            v_comp = 0.0
            for cc in np.unique(cell, axis=0):
                sel = (cell == cc).all(1)
                if sel.sum() < 4:
                    continue
                pv = Pv[sel]
                c = pv.mean(0)
                c = c + nn * ((pv @ nn).min() - st / 2 - c @ nn)  # the break: the joint behind the innermost of it
                a = np.abs((pv - c) @ m1).max() + st / 2 + T["marginM"]
                b = np.abs((pv - c) @ m2).max() + dz / 2 + T["marginM"]
                h = ((pv - c) @ nn).max() + st / 2 + T["marginM"]
                # what the box would take besides: held rock inside it, on the layers' grid
                i0, i1 = np.searchsorted(X[:, 0], [pv[:, 0].min() - h, pv[:, 0].max() + h])
                j0, j1 = np.searchsorted(Y[0], [pv[:, 1].min() - h, pv[:, 1].max() + h])
                k0, k1 = np.searchsorted(Z, [pv[:, 2].min() - b, pv[:, 2].max() + b])
                sub = held[i0:i1, j0:j1, k0:k1]
                W = np.stack(np.meshgrid(X[i0:i1, 0], Y[0, j0:j1], Z[k0:k1], indexing="ij"), -1)[sub] - c
                inside = ((W @ nn >= 0) & (W @ nn <= h) & (np.abs(W @ m1) <= a) & (np.abs(W @ m2) <= b)).sum()
                if inside > T["heldShare"] * sel.sum():
                    kept += 1
                    continue
                self.add_cut(rec, c, nn, m1, m2, a, b, h, age, NAMES.index(fam), max(a, b), 0.0)
                fell += 1
                v_comp += sel.sum() * st * st * dz
            if v_comp:  # what fell together lies together
                self.lay(Pv.mean(0), v_comp, max(float(Pv[:, 2].min() - SEA["level"]), 0.0), age, g)
                vol_all += v_comp
        self.settle(rec)
        print(f"overhang: {fell} pieces fell ({vol_all:.0f} m3), {kept} left where the cut would take held rock; "
              f"{time.time() - t0:.0f}s")

    # 6. the blocks on the foot

    def debris(self):
        """The blocks on the foot: each dated fall's below its scar, the old stones in the coves and the tide."""
        sp = {f["name"]: f["spacingM"] for f in ROCK["families"]}
        P = self.P
        out = []
        for act in self.acts:
            if act["kind"] != "rockfall":
                continue
            rng = HS.Stream("lt1-bluff", act["id"], "blocks")
            age = FIX["date"] - act["year"]
            Hf = sum(act["zM"]) / 2 - FACE["footZ"]
            for k in range(act["blocks"]):
                t = rng.uniform(*sp["foliation"]) * rng.uniform(0.3, 0.6)
                L = rng.uniform(0.9, 2.8)
                half = np.array([L, L * rng.uniform(0.5, 0.9), min(t, L * 0.5)]) / 2
                for _ in range(40):
                    uu = act["_u"] + rng.uniform(-0.6, 0.6) * act["widthM"]
                    out_m = rng.uniform(0.25, 0.6) * Hf * (0.6 + 0.4 * L / 2.8) + rng.uniform(0, 0.12) * age
                    base = BL.point_on_crest(uu)
                    fr = BL.crest_frame(np.array([base[0]]), np.array([base[1]]))
                    s0 = float(self.face_line(np.array([FACE["footZ"]]), np.array([uu]))[0])
                    x, y = base + np.array([fr[2][0], fr[3][0]]) * (s0 + out_m)
                    zf = float(P.at("foot", np.array([x]), np.array([y]))[0])
                    if zf > SEA["level"] - 0.8:
                        break
                tilt = math.radians(14 if age < 30 else 6)
                R = BL.rot(rng.uniform(0, 2 * math.pi), rng.normal(0, tilt), rng.normal(0, tilt))
                r0, r1 = LAND["weather"]["blockRound"]
                r = float(min(half)) * (r0 + (r1 - r0) * min(age / LAND["weather"]["blockRoundYears"], 1.0))
                z = self.rest(x, y, R, half) + half[2] * 0.75
                out.append((np.array([x, y, z]), R, half, max(r, 0.02), float(age)))
        bd = FIX["boulders"]
        tries = n = 0
        while n < bd["count"] and tries < bd["count"] * 80:
            tries += 1
            rng = HS.Stream("lt1-bluff", bd["seed"], tries)  # each try its own draws
            u = rng.uniform(4.0, P.length - 6.0)
            base = BL.point_on_crest(u)
            fr = BL.crest_frame(np.array([base[0]]), np.array([base[1]]))
            o = rng.uniform(0.5, 26.0)
            x, y = base + np.array([fr[2][0], fr[3][0]]) * o
            z0 = float(P.at("foot", np.array([x]), np.array([y]))[0])
            lo_z, hi_z = bd["zM"]
            if z0 > hi_z or z0 < lo_z:
                continue
            cleft = any(abs(u - cl["u"]) < cl["widthM"] for cl in FIX["clefts"]["list"])
            if rng.random() > (0.9 if cleft else self.shelter(x, y) ** 2):
                continue
            a, b = bd["sizeM"]
            L = a + (b - a) * rng.random() ** 2.2
            half = np.array([L, L * rng.uniform(0.6, 0.9), L * rng.uniform(*bd["flat"])]) / 2
            R = BL.rot(rng.uniform(0, 2 * math.pi), rng.uniform(-0.12, 0.12), rng.uniform(-0.12, 0.12))
            z = self.rest(x, y, R, half) + half[2] * 0.4
            out.append((np.array([x, y, z]), R, half, float(min(half)) * bd["round"], OLD))
            n += 1
        self.blocks = out
        self.bc = np.array([b[0] for b in out])
        self.br = np.array([np.linalg.norm(b[2]) for b in out])

    def shelter(self, x, y):
        """The share of land within the boulders' shelterM of a point: high in a cove, low on a point."""
        if not hasattr(self, "_shelter"):
            P = self.P
            k = max(1, int(FIX["boulders"]["shelterM"] / P.step))
            land = 1.0 - P.F["wet"]
            I = np.pad(land, ((k + 1, k), (k + 1, k)), mode="edge").cumsum(0).cumsum(1)
            n = land.shape
            box = (I[2 * k + 1:2 * k + 1 + n[0], 2 * k + 1:2 * k + 1 + n[1]] - I[:n[0], 2 * k + 1:2 * k + 1 + n[1]]
                   - I[2 * k + 1:2 * k + 1 + n[0], :n[1]] + I[:n[0], :n[1]])
            P.F["shelter"] = box / (2 * k + 1) ** 2
            self._shelter = True
        return float(self.P.at("shelter", np.array([x]), np.array([y]))[0])

    def surface_z(self, x, y, z0=40.0, step=0.05):
        """The height of the first solid ground under a point, rock or turf."""
        zs = np.arange(z0, BL.BED, -step)
        Q = np.stack([np.full(len(zs), x), np.full(len(zs), y), zs], -1)
        d = self.at(Q, track=False)[0]
        hit = np.where(d < 0)[0]
        zr = float(zs[hit[0]]) if len(hit) else SEA["level"]
        if hasattr(self, "turf_grid") and in_turf(self, np.array([x]), np.array([y]))[0]:
            zr = max(zr, float(turf_z(self, np.array([x]), np.array([y]))[0]))
        return max(zr, SEA["level"])

    # the whole

    def near(self, lo, hi):
        """The cuts and blocks that can reach a box."""
        c, h = (lo + hi) / 2, np.linalg.norm(hi - lo) / 2
        cuts = (np.where(np.linalg.norm(self.D["c"] - c, axis=1) < self.D["R"] + h)[0]
                if self.D is not None and len(self.D["R"]) else [])
        blocks = np.where(np.linalg.norm(self.bc - c, axis=1) < self.br + h + 0.2)[0] if len(self.blocks) else []
        return cuts, blocks

    def sdf(self, Q, cuts, blocks, track=False):
        d, kind = self.mass(Q[:, 0], Q[:, 1], Q[:, 2])
        ds = self.sea_cut(Q)
        age = np.full(len(Q), OLD)
        gap = np.zeros(len(Q))
        gov = np.full(len(Q), -1)
        if track:
            kind = np.where(-ds > d, WORN, kind)
        d = smax(d, -ds, 0.5)
        D = self.D
        for k in cuts:
            q = Q - D["c"][k]
            a = q @ D["n"][k]
            dc = np.maximum(np.maximum(-a, a - D["h"][k]),
                            np.maximum(np.abs(q @ D["m1"][k]) - D["a"][k], np.abs(q @ D["m2"][k]) - D["b"][k]))
            if track:
                hit = -dc > d
                kind[hit], age[hit], gap[hit], gov[hit] = D["fam"][k], D["age"][k], D["gap"][k], k
            d = smax(d, -dc, D["k"][k])
        for k in blocks:
            C, R, half, r, ag = self.blocks[k]
            db = rbox(Q, C, R, half, r)
            if track:
                hit = db < d
                kind[hit], age[hit], gap[hit], gov[hit] = BLOCK, ag, 0.0, GOVB + k
            d = smin(d, db, 0.06)
        return d, kind, age, gap, gov

    def at(self, Q, cell=6.0, track=True, gov=False):
        """The distance and facts at any points, the cuts and blocks found per cell; with gov, which cut (its index)
        or block (GOVB on) made the surface there, -1 for the mass."""
        out = [np.zeros(len(Q)), np.zeros(len(Q), int), np.zeros(len(Q)), np.zeros(len(Q)), np.zeros(len(Q), int)]
        key = np.floor(Q / cell).astype(np.int64)
        order = np.lexsort(key.T)
        ks = key[order]
        brk = np.where(np.any(np.diff(ks, axis=0) != 0, axis=1))[0] + 1
        for grp in np.split(order, brk):
            lo = np.floor(Q[grp[0]] / cell) * cell
            cuts, blocks = self.near(lo, lo + cell)
            res = self.sdf(Q[grp], cuts, blocks, track)
            for o, r in zip(out, res):
                o[grp] = r
        return out if gov else out[:4]


# -- the grid and the mesh -------------------------------------------------------------------------------------------

def thinless(D, v, H):
    """The brick without rock or air thinner than two voxels. A fin or a prong that thin between two breaks cannot be
    drawn as a solid (the grid catches it every other voxel, as a row of slits) and would have fallen with the blocks
    round it; a crack that thin is the material's dark line, not a slot the grid would draw as a zigzag. D carries a
    halo of H voxels; the brick inside it is returned."""
    B = D.shape[0] - 2 * H
    c = (slice(H, H + B),) * 3
    out = D[c].copy()
    n = 0
    for solid, sign in ((D > 0, 1.0), (D <= 0, -1.0)):  # thin rock (air both sides), then thin air
        thin = np.zeros((B, B, B), bool)
        for ax in range(3):
            def at(k):
                sl = list(c)
                sl[ax] = slice(H + k, H + k + B)
                return solid[tuple(sl)]
            thin |= (at(-1) & at(1)) | (at(-1) & at(2)) | (at(-2) & at(1))
        thin &= ~solid[c]
        out[thin] = sign * 0.5 * v
        n += int(thin.sum())
    return out, n


def build_grid(land, box, v, path):
    B = 32
    lo = np.array(box[0], float)
    n = np.ceil((np.array(box[1]) - lo) / (v * B)).astype(int)
    grid = vdb.FloatGrid(-1.0)
    grid.name = "density"
    grid.transform = vdb.createLinearTransform(voxelSize=v)
    g = (np.arange(5) / 4.0) * (B - 1) * v
    lat = np.stack(np.meshgrid(g, g, g, indexing="ij"), -1).reshape(-1, 3)
    idx = np.stack(np.meshgrid(*[np.arange(k) for k in n], indexing="ij"), -1).reshape(-1, 3)
    pts = (lo + idx[:, None, :] * B * v + lat[None]).reshape(-1, 3)
    env, _ = land.mass(pts[:, 0], pts[:, 1], pts[:, 2])
    env = smax(env, -land.sea_cut(pts), 0.5).reshape(len(idx), -1)
    gap = (B - 1) * v / 4 * math.sqrt(3) / 2 + 0.3
    deep = LAND["fractures"]["maxDepthM"] + 3.0
    caves = []
    for a in land.acts:
        if a["kind"] == "cave":
            c = np.array([a["at"][0], a["at"][1], SEA["level"]])
            caves.append((c - a["depthM"] - 7, c + a["depthM"] + 7))
    for cl in land.clefts:
        caves.append((cl["c"] - cl["d"] - 6 - np.array([0, 0, 2]), cl["c"] + cl["d"] + 6 + np.array([0, 0, 30])))
    t = time.time()
    k_fill = k_comp = 0
    H = 2  # a halo, so the thin test sees across the brick's faces
    ii = np.arange(-H, B + H) * v
    L = np.stack(np.meshgrid(ii, ii, ii, indexing="ij"), -1).reshape(-1, 3)
    k_thin = 0
    for b, (ix, iy, iz) in enumerate(idx):
        o = lo + np.array([ix, iy, iz]) * B * v
        e = o + B * v
        cuts, blocks = land.near(o, e)
        nc = any(np.all(c1 > o) and np.all(c0 < e) for c0, c1 in caves)
        if env[b].min() > gap + 0.8 and not len(blocks):
            continue
        if env[b].max() < -(gap + deep) and not nc:
            grid.fill((ix * B, iy * B, iz * B), (ix * B + B - 1, iy * B + B - 1, iz * B + B - 1), 1.0, True)
            k_fill += 1
            continue
        D = land.sdf(o + L, cuts, blocks)[0].reshape(B + 2 * H, B + 2 * H, B + 2 * H)
        D, n_thin = thinless(D, v, H)
        k_thin += n_thin
        grid.copyFromArray((-D).astype(np.float32), ijk=(ix * B, iy * B, iz * B), tolerance=0)
        k_comp += 1
        if k_comp % 200 == 0:
            print(f"  {k_comp} bricks, {time.time() - t:.0f}s", flush=True)
    print(f"rock grid: {k_comp} bricks sampled, {k_fill} filled, {k_thin} thin voxels dropped or filled, "
          f"{time.time() - t:.1f}s")
    vdb.write(path, grids=[grid])
    return lo


def node(nt, kind, **kw):
    n = nt.nodes.new(kind)
    for k, v in kw.items():
        setattr(n, k, v)
    return n


def rock_mesh(path, lo, share=0.05):
    """The grid's surface as a mesh with only its body kept: a piece the fractures cut free would have fallen, so any
    island under `share` of the vertices is dropped."""
    bpy.ops.object.volume_import(filepath=path)
    vol = bpy.context.object
    vol.location = lo
    vol.hide_render = True
    host = bpy.data.objects.new("rock", bpy.data.meshes.new("rock"))
    bpy.context.scene.collection.objects.link(host)
    ng = bpy.data.node_groups.new("v2m", "GeometryNodeTree")
    ng.interface.new_socket("Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry")
    go = ng.nodes.new("NodeGroupOutput")
    oi = ng.nodes.new("GeometryNodeObjectInfo")
    oi.inputs["Object"].default_value = vol
    oi.transform_space = "RELATIVE"
    vm = ng.nodes.new("GeometryNodeVolumeToMesh")
    vm.inputs["Threshold"].default_value = 0.0
    isl = ng.nodes.new("GeometryNodeInputMeshIsland")
    acc = node(ng, "GeometryNodeAccumulateField", data_type="FLOAT", domain="POINT")
    acc.inputs[0].default_value = 1.0
    cmp = node(ng, "FunctionNodeCompare", data_type="FLOAT", operation="LESS_THAN")
    size = ng.nodes.new("GeometryNodeAttributeDomainSize")
    mul = node(ng, "ShaderNodeMath", operation="MULTIPLY")
    mul.inputs[1].default_value = share
    ng.links.new(vm.outputs[0], size.inputs[0])
    ng.links.new(size.outputs["Point Count"], mul.inputs[0])
    ng.links.new(mul.outputs[0], cmp.inputs[1])
    dl = node(ng, "GeometryNodeDeleteGeometry", domain="POINT")
    ng.links.new(oi.outputs["Geometry"], vm.inputs[0])
    ng.links.new(isl.outputs["Island Index"], acc.inputs[1])
    ng.links.new(acc.outputs["Total"], cmp.inputs[0])
    ng.links.new(vm.outputs[0], dl.inputs["Geometry"])
    ng.links.new(cmp.outputs[0], dl.inputs["Selection"])
    ng.links.new(dl.outputs[0], go.inputs[0])
    host.modifiers.new("v2m", "NODES").node_group = ng
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(host.evaluated_get(dg))
    host.modifiers.clear()
    host.data = me
    bpy.data.objects.remove(vol)
    print(f"rock mesh: {len(me.polygons)} faces")
    return host


def drop_faces(ob, mask):
    import bmesh
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    bm.faces.ensure_lookup_table()
    bmesh.ops.delete(bm, geom=[bm.faces[i] for i in np.where(mask)[0]], context="FACES")
    bm.to_mesh(ob.data)
    bm.free()


def centres(me):
    C = np.zeros(len(me.polygons) * 3)
    me.polygons.foreach_get("center", C)
    N = np.zeros(len(me.polygons) * 3)
    me.polygons.foreach_get("normal", N)
    return C.reshape(-1, 3), N.reshape(-1, 3)


def snap(land, ob):
    """Each vertex inside a break's plane onto that plane, and each on a block onto the block. The mesher steps along
    a plane it crosses at a slant; a break is a plane. Vertices where two surfaces meet stay where the mesher put
    them, on the rounding between them; a face the move would fold keeps its place."""
    me = ob.data
    V0 = np.zeros(len(me.vertices) * 3)
    me.vertices.foreach_get("co", V0)
    V0 = V0.reshape(-1, 3)
    me.calc_loop_triangles()
    F = np.zeros(len(me.loop_triangles) * 3, int)
    me.loop_triangles.foreach_get("vertices", F)
    F = F.reshape(-1, 3)
    E = np.zeros(len(me.edges) * 2, int)
    me.edges.foreach_get("vertices", E)
    E = E.reshape(-1, 2)
    D = land.D
    V = V0.copy()
    gov = land.at(V, gov=True)[4]
    key = np.full(len(V), -1, np.int64)
    # each vertex's tangent plane, n.x = d: its cut's plane, its block's surface, the mass's gradient
    PN, PD = np.zeros_like(V), np.zeros(len(V))
    c = np.where((gov >= 0) & (gov < GOVB))[0]
    k = gov[c]
    q = V[c] - D["c"][k]
    n, m1, m2 = D["n"][k], D["m1"][k], D["m2"][k]
    a_ = np.einsum("ij,ij->i", q, n)
    p1, p2 = np.einsum("ij,ij->i", q, m1), np.einsum("ij,ij->i", q, m2)
    T = np.stack([-a_, a_ - D["h"][k], np.abs(p1) - D["a"][k], np.abs(p2) - D["b"][k]], -1)
    t = T.argmax(1)
    key[c] = k * 4 + t
    t = t[:, None]
    side = np.where(t == 2, np.sign(p1)[:, None] * m1, np.sign(p2)[:, None] * m2)
    U = np.where(t == 0, -n, np.where(t == 1, n, side))
    PN[c], PD[c] = U, np.einsum("ij,ij->i", U, V[c]) - T.max(1)
    for j in np.unique(gov[gov >= GOVB]):
        sel = np.where(gov == j)[0]
        C, R, half, r, _ = land.blocks[j - GOVB]
        p = (V[sel] - C) @ R
        e = np.abs(p) - (half - r)
        o = np.maximum(e, 0)
        L = np.linalg.norm(o, axis=1)
        ax = e.argmax(1)
        gl = np.where((L > 1e-9)[:, None], o / np.maximum(L, 1e-9)[:, None], np.eye(3)[ax]) * np.sign(p)
        nb = gl @ R.T
        key[sel] = j * 8 + ax * 2 + (p[np.arange(len(sel)), ax] > 0)
        PN[sel], PD[sel] = nb, np.einsum("ij,ij->i", nb, V[sel]) - (L + np.minimum(e.max(1), 0) - r)
    edge = np.zeros(len(V), bool)
    diff = key[E[:, 0]] != key[E[:, 1]]
    edge[E[diff, 0]] = edge[E[diff, 1]] = True
    ring = edge.copy()
    ring[E[edge[E[:, 0]], 1]] = ring[E[edge[E[:, 1]], 0]] = True
    # near an edge, the true surface's own tangent plane: a crease stays sharp, a rounded edge stays round
    ms = np.where(ring)[0]
    h = 0.03
    tet = np.array([[1, 1, 1], [1, -1, -1], [-1, 1, -1], [-1, -1, 1]], float)
    dv = [land.at(V[ms] + h * s_, track=False)[0] for s_ in tet]
    g = sum(d_[:, None] * s_ for d_, s_ in zip(dv, tet))
    g /= np.maximum(np.linalg.norm(g, axis=1), 1e-9)[:, None]
    PN[ms], PD[ms] = g, np.einsum("ij,ij->i", g, V[ms]) - sum(dv) / 4
    # off the edges, onto the plane where the plane is the surface (not on an edge's rounding); on them, the point
    # nearest all the planes round it, as dual contouring does
    inner = np.where(~edge & (gov >= 0))[0]
    off = np.einsum("ij,ij->i", PN[inner], V[inner]) - PD[inner]
    W = V[inner] - off[:, None] * PN[inner]
    ok = (np.abs(off) < 0.2) & (np.abs(land.at(W, track=False)[0]) < 0.01)
    V[inner[ok]] = W[ok]
    ev = np.where(edge)[0]
    ix = np.full(len(V), -1)
    ix[ev] = np.arange(len(ev))
    # the move from where the mesher put it, only along the directions the planes fix: two breaks of one family a
    # few degrees apart fix only their common normal (onto the plane), two families a crease (onto its line)
    A = np.zeros((len(ev), 3, 3))
    b = np.zeros((len(ev), 3))
    for i_, j_ in ((E[:, 0], E[:, 1]), (E[:, 1], E[:, 0]), (ev, ev)):
        m = (ix[i_] >= 0) & (np.abs(PN[j_]).sum(1) > 0)
        I, J = ix[i_[m]], j_[m]
        res = PD[J] - np.einsum("ij,ij->i", PN[J], V0[i_[m]])
        for r_ in range(3):
            b[:, r_] += np.bincount(I, PN[J, r_] * res, len(ev))
            for s_ in range(3):
                A[:, r_, s_] += np.bincount(I, PN[J, r_] * PN[J, s_], len(ev))
    w, Q = np.linalg.eigh(A)
    inv = np.where(w > 0.05 * w[:, -1:], 1 / np.maximum(w, 1e-12), 0.0)  # planes under ~25 degrees apart: one
    mv = np.einsum("nij,nj,nkj,nk->ni", Q, inv, Q, b)
    ln = np.linalg.norm(mv, axis=1)
    V[ev] = V0[ev] + mv * np.minimum(1.0, LAND["voxelM"] / np.maximum(ln, 1e-9))[:, None]

    def normals(W):
        return np.cross(W[F[:, 1]] - W[F[:, 0]], W[F[:, 2]] - W[F[:, 0]])

    n0 = normals(V0)
    kept = 0
    for _ in range(12):
        n1 = normals(V)
        l0, l1 = np.linalg.norm(n0, axis=1), np.linalg.norm(n1, axis=1)
        # a face pressed flat onto an edge line has no area left to fold; only one that turned over and kept its area
        bad = (np.einsum("ij,ij->i", n0, n1) < 0.3 * l0 * l1) & (l1 > 0.2 * l0)
        if not bad.any():
            break
        kept += bad.sum()
        back = np.unique(F[bad])
        V[back] = V0[back] if _ == 11 else 0.5 * (V[back] + V0[back])
    moved = np.linalg.norm(V - V0, axis=1)
    mm = moved[moved > 0.005].mean() * 100
    print(f"snap: {(moved > 0.005).mean():.0%} of vertices onto their planes, mean move {mm:.1f} cm, "
          f"{kept} faces kept from folding, {int(bad.sum())} left")
    me.vertices.foreach_set("co", V.ravel())
    me.update()


def collapse(ob, tris):
    me = ob.data
    me.calc_loop_triangles()
    have = len(me.loop_triangles)
    if tris and have > tris:
        m = ob.modifiers.new("lod", "DECIMATE")
        m.decimate_type = "COLLAPSE"
        m.ratio = tris / have
        m.use_collapse_triangulate = True
        dg = bpy.context.evaluated_depsgraph_get()
        new = bpy.data.meshes.new_from_object(ob.evaluated_get(dg))
        ob.modifiers.clear()
        ob.data = new
    return ob


def write_facts(land, ob):
    """Each face's fact: the governing cut's family, its years bare and its joint's opening."""
    me = ob.data
    C, N = centres(me)
    _, kind, age, gap = land.at(C - N * 0.02)
    for name, typ, vals in (("plane", "INT", kind), ("age", "FLOAT", age), ("gap", "FLOAT", gap)):
        a = me.attributes.new(name, typ, "FACE")
        a.data.foreach_set("value", vals.astype(int if typ == "INT" else float))


def shade(ob):
    me = ob.data
    me.shade_smooth()
    me.set_sharp_from_angle(angle=math.radians(34))
    wn = ob.modifiers.new("planes", "WEIGHTED_NORMAL")
    wn.mode = "FACE_AREA"
    wn.keep_sharp = True


def view_rock(land, src, cam, factor=12.0):
    """The rock as the game draws it from cam: each square metre at its distance tier's triangles (the budget's
    tiers), the facts written on its faces, its planes shaded flat."""
    T = FIX["budget"]["tiers"]
    me = src.data
    n = len(me.vertices)
    V = np.zeros(n * 3)
    me.vertices.foreach_get("co", V)
    dv = np.linalg.norm(V.reshape(-1, 3) - cam, axis=1)
    tier = np.searchsorted([t["toM"] for t in T], dv)
    C, _ = centres(me)
    A = np.zeros(len(me.polygons))
    me.polygons.foreach_get("area", A)
    ft = np.searchsorted([t["toM"] for t in T], np.linalg.norm(C - cam, axis=1))
    per = np.array([t["perM2"] for t in T])
    target = int((A * per[ft]).sum())
    ob = bpy.data.objects.new("rock", me.copy())
    bpy.context.scene.collection.objects.link(ob)
    vg = ob.vertex_groups.new(name="far")
    for k in range(len(T)):
        vg.add(np.where(tier == k)[0].tolist(), float(1 - per[k] / per.max()), "REPLACE")
    m = ob.modifiers.new("lod", "DECIMATE")
    m.decimate_type = "COLLAPSE"
    me.calc_loop_triangles()
    m.ratio = min(1.0, target / len(me.loop_triangles))
    m.use_collapse_triangulate = True
    m.vertex_group = "far"
    m.vertex_group_factor = factor
    dg = bpy.context.evaluated_depsgraph_get()
    new = bpy.data.meshes.new_from_object(ob.evaluated_get(dg))
    ob.modifiers.clear()
    ob.vertex_groups.clear()
    ob.data = new
    C2, _ = centres(new)
    A2 = np.zeros(len(new.polygons))
    new.polygons.foreach_get("area", A2)
    t2 = np.searchsorted([t["toM"] for t in T], np.linalg.norm(C2 - cam, axis=1))
    got = [f"{(t2 == k).sum() / max(A2[t2 == k].sum(), 1):.1f}" for k in range(len(T))]
    print(f"rock in view: {len(new.polygons)} triangles (target {target}); per m2 by tier {got} "
          f"(asked {[t['perM2'] for t in T]})")
    write_facts(land, ob)
    shade(ob)
    return ob


def tri_count(ob):
    ob.data.calc_loop_triangles()
    return len(ob.data.loop_triangles)


# -- the turf on it --------------------------------------------------------------------------------------------------

def blur(A, cells):
    """Three box passes of half-width `cells` (near a gaussian), edges held."""
    k = max(1, int(round(cells)))
    for _ in range(3):
        for ax in (0, 1):
            C = np.pad(A, [(k + 1, k) if i == ax else (0, 0) for i in range(2)], mode="edge").cumsum(ax)
            n = A.shape[ax]
            A = (np.take(C, np.arange(2 * k + 1, 2 * k + 1 + n), axis=ax)
                 - np.take(C, np.arange(n), axis=ax)) / (2 * k + 1)
    return A


def fill(A, keep, n=6):
    """A's values outside keep, each the mean of its filled neighbours, n cells out."""
    A = np.where(keep, A, np.nan)
    with np.errstate(all="ignore"):
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            for _ in range(n):
                Pd = np.pad(A, 1, constant_values=np.nan)
                m = np.nanmean(np.stack([Pd[:-2, 1:-1], Pd[2:, 1:-1], Pd[1:-1, :-2], Pd[1:-1, 2:]]), 0)
                A = np.where(np.isnan(A), m, A)
    return A


def bilinear(G, xs, ys, x, y):
    fx = np.clip((x - xs[0]) / (xs[1] - xs[0]), 0, len(xs) - 1.001)
    fy = np.clip((y - ys[0]) / (ys[1] - ys[0]), 0, len(ys) - 1.001)
    i, j = fx.astype(int), fy.astype(int)
    tx, ty = fx - i, fy - j
    return (G[i, j] * (1 - tx) * (1 - ty) + G[i + 1, j] * tx * (1 - ty) + G[i, j + 1] * (1 - tx) * ty
            + G[i + 1, j + 1] * tx * ty)


def rock_top(land, x, y, z0, up=1.0, down=7.0, dz=0.25):
    """The rock's top under points: the first rock met going down from z0 + up to z0 - down; NaN where none."""
    L = np.arange(up, -down, -dz)
    n = len(x)
    Q = np.empty((n * len(L), 3))
    Q[:, 0], Q[:, 1] = np.repeat(x, len(L)), np.repeat(y, len(L))
    Q[:, 2] = (z0[:, None] + L[None, :]).ravel()
    D = land.at(Q, track=False)[0].reshape(n, len(L))
    ins = D < 0
    first = ins.argmax(1)
    i = np.clip(first, 1, len(L) - 1)
    r = np.arange(n)
    d0, d1 = D[r, i - 1], D[r, i]
    z = z0 + L[i - 1] - dz * np.clip(d0 / np.maximum(d0 - d1, 1e-6), 0, 1)
    z = np.where(first == 0, z0 + up, z)
    return np.where(ins.any(1), z, np.nan)


def turf(land, x0, x1, y0, y1, step=0.4):
    """The soil drapes the rock and the turf grows on it (the fixture's soil): on the top and on the broad ledges, deep
    in hollows and thin on knolls, back from the edges the spray strips; at its edge the root mat overhangs a raw
    earth scarp down to the rock."""
    S_ = SOIL
    P = land.P
    xs = np.linspace(x0, x1, int(round((x1 - x0) / step)) + 1)
    ys = np.linspace(y0, y1, int(round((y1 - y0) / step)) + 1)
    X, Y = np.meshgrid(xs, ys, indexing="ij")
    gx = np.linspace(x0, x1, int(round((x1 - x0) / GROUND["step"])) + 1)
    gy = np.linspace(y0, y1, int(round((y1 - y0) / GROUND["step"])) + 1)
    far = bilinear(town_z(*np.meshgrid(gx, gy, indexing="ij")), gx, gy, X, Y)
    on_land = P.at("wet", X, Y) < 0.5
    zr = np.full(X.shape, np.nan)
    z0 = land.top_at(X, Y) - S_["depthM"]
    back_of = land.crest_s(X, Y) - P.at("s", X, Y)
    for m, down in ((on_land & (back_of > 20.0), 3.0), (on_land & (back_of <= 20.0), 14.0)):
        zr[m] = rock_top(land, X[m], Y[m], z0[m], down=down)
    has = ~np.isnan(zr)
    zf = np.where(has, zr, SEA["level"] - 2.0)
    gx, gy = np.gradient(blur(zf, S_["bridgeM"] / step / 2), step)  # the root mat spans a narrow crack
    slope = np.degrees(np.arctan(np.hypot(gx, gy)))
    sm = np.pad(blur(zf, S_["curveCellM"] / step / 2), 1, mode="edge")
    lap = (sm[:-2, 1:-1] + sm[2:, 1:-1] + sm[1:-1, :-2] + sm[1:-1, 2:] - 4 * sm[1:-1, 1:-1]) / step ** 2
    d0, d1 = S_["drapeM"]
    soil = np.clip(S_["midM"] + S_["curveM2"] * lap, d0, d1) * (1 - 0.6 * smooth(15.0, S_["maxSlopeDeg"], slope))
    soil = np.maximum(soil, d0)
    ex = land.exposure(X, Y)
    b0, b1 = S_["bareBelowM"]
    ok = has & (slope < S_["maxSlopeDeg"]) & (zr > SEA["level"] + b0 + (b1 - b0) * ex)
    pw = int(8.0 / step) + 1  # the distance's rolls wrap: pad by its reach, so the grid's own border is no edge
    okp = np.pad(ok, pw, mode="edge")
    sd = np.where(okp, BL.edt(~okp, step, 8.0), -BL.edt(okp, step, 8.0))[pw:-pw, pw:-pw]
    e0, e1 = S_["edgeBackM"]
    back = e0 + (e1 - e0) * ex * BL.vnoise(P.at("u", X, Y) / S_["edgeCellM"], "turf-edge") ** 0.7
    f = blur(sd - back, 1)
    keep = f > 0
    # at the grid's border the turf is the far ground, as it draws it: the same heights along the same lines
    nb = np.minimum.reduce([X - xs[0], xs[-1] - X, Y - ys[0], ys[-1] - Y])
    edge_w = smooth(0.0, 4.0, nb)
    zt = fill(np.where(has, zr + soil, z0 + S_["depthM"]) * edge_w + far * (1 - edge_w), keep)
    soil_f = fill(soil, keep)
    land.turf_grid = dict(xs=xs, ys=ys, f=f, keep=keep, z=zt, soil=soil_f, has=has, slope=slope, ok=ok, sd=sd, zr=zr)
    print(f"turf: {keep.mean() * np.prod(X.shape) * step ** 2:.0f} m2, soil {soil[keep].min():.2f}-"
          f"{soil[keep].max():.2f} m")
    # the edge between the grid's points: each point outside it onto it, along the slope of f
    fx, fy = np.gradient(f, step)
    gg = np.maximum(fx ** 2 + fy ** 2, 1e-3)
    Xm = np.where(keep, X, X - f * fx / gg)
    Ym = np.where(keep, Y, Y - f * fy / gg)
    Zm = np.where(keep, zt, bilinear(zt, xs, ys, Xm, Ym))
    Zm = np.where(np.isnan(Zm), np.nanmean(zt), Zm)
    ob, me = BL.grid_object("turf", Xm, Ym, Zm, keep, any_=True)
    import bmesh
    bm = bmesh.new()
    bm.from_mesh(me)
    rim = {}
    l0, l1 = S_["lipM"]
    for e in [e for e in bm.edges if e.is_boundary]:
        for v in e.verts:
            if v.index in rim:
                continue
            x, y = v.co.x, v.co.y
            if min(x - xs[0], xs[-1] - x, y - ys[0], ys[-1] - y) < 1.5 * step:
                continue  # the grid's own border, not an edge of the turf
            ax = np.array([x]), np.array([y])
            o = -np.array([bilinear(fx, xs, ys, *ax)[0], bilinear(fy, xs, ys, *ax)[0]])
            o /= max(np.linalg.norm(o), 1e-6)
            sl = float(bilinear(soil_f, xs, ys, *ax)[0]) if not np.isnan(bilinear(soil_f, xs, ys, *ax)[0]) else d0
            lip = l0 + (l1 - l0) * smooth(d0, d1, sl) * (0.4 + 0.6 * float(BL.vnoise2(ax[0] / 1.5, ax[1] / 1.5, 71)[0]))
            top = v.co.copy()
            v.co.x, v.co.y = x + o[0] * lip, y + o[1] * lip
            mat = bm.verts.new((v.co.x, v.co.y, top.z - 0.09))
            foot = bm.verts.new((x - o[0] * lip * S_["undercutShare"], y - o[1] * lip * S_["undercutShare"],
                                 top.z - sl - 0.15))
            rim[v.index] = (mat, foot)
    scarp = []
    for e in [e for e in bm.edges if e.is_boundary and e.link_loops]:
        lp = e.link_loops[0]
        a, b = lp.vert, lp.link_loop_next.vert
        if a.index not in rim or b.index not in rim:
            continue
        (am, af), (bm_, bf) = rim[a.index], rim[b.index]
        bm.faces.new((b, a, am, bm_))
        scarp.append(bm.faces.new((bm_, am, af, bf)))
    bm.faces.index_update()
    sc = np.zeros(len(bm.faces), np.int8)
    sc[[fc.index for fc in scarp]] = 1
    bm.to_mesh(me)
    bm.free()
    me.attributes.new("scarp", "INT8", "FACE").data.foreach_set("value", sc)
    me.shade_smooth()
    me.set_sharp_from_angle(angle=math.radians(40))
    return ob


def turf_z(land, x, y):
    """The turf's top where it is, the rock's town top elsewhere."""
    T = land.turf_grid
    z = bilinear(T["z"], T["xs"], T["ys"], x, y)
    return np.where(np.isnan(z), land.top_at(x, y), z)


def in_turf(land, x, y, margin=0.0):
    T = land.turf_grid
    xs, ys, f = T["xs"], T["ys"], T["f"]
    i = np.clip(np.round((x - xs[0]) / (xs[1] - xs[0])).astype(int), 0, len(xs) - 1)
    j = np.clip(np.round((y - ys[0]) / (ys[1] - ys[0])).astype(int), 0, len(ys) - 1)
    inside = (x >= xs[0]) & (x <= xs[-1]) & (y >= ys[0]) & (y <= ys[-1])
    return inside & (f[i, j] > margin)


def figure(x, y, land, name):
    """A person, 1.75 m, standing on the ground there."""
    z = land.surface_z(x, y)
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.19, depth=1.5, location=(x, y, z + 0.75))
    body = bpy.context.object
    bpy.ops.mesh.primitive_uv_sphere_add(segments=8, ring_count=6, radius=0.12, location=(x, y, z + 1.63))
    head = bpy.context.object
    body.name, head.name = name, name + "-head"
    return [body, head]


GROUND = dict(step=4.0, x=(-900.0, 1300.0), y=(-700.0, 1200.0))


def on_ground_lines(v, axis, up):
    """v moved onto the far ground's grid lines along an axis (0 x, 1 y), up or down."""
    o, st = GROUND["xy"[axis]][0], GROUND["step"]
    return o + st * (math.ceil if up else math.floor)((v - o) / st - 1e-9 * (1 if up else -1))


def town_z(X, Y):
    """The town's ground: the sea bed under the water, the land down to the shore."""
    wet = BL.water(X, Y)
    sx, sy = BL.X0 - Y, BL.Y0 + X
    d = BL.CL._poly_dist(sx, sy, BL.CL.COAST_LINE)
    for poly, _ in BL.CL.ISLAND_LINES:
        d = np.minimum(d, BL.CL._poly_dist(sx, sy, poly))
    return np.where(wet, np.maximum(SEA["level"] - 0.3 - FOOT["bedSlope"] * d, FOOT["bedFloor"]),
                    np.minimum(BL.ground(X, Y) - 0.12, SEA["level"] + 0.3 + 0.25 * d))


def far_ground(land, rock_box):
    """The town's ground round the site on its 4 m grid, gone where the turf or the rock's face is the ground; the
    turf's grid ends on its lines, so the two share their edge."""
    P = land.P
    st = GROUND["step"]
    X, Y = np.meshgrid(np.arange(GROUND["x"][0], GROUND["x"][1], st), np.arange(GROUND["y"][0], GROUND["y"][1], st),
                       indexing="ij")
    Z, wet = town_z(X, Y), BL.water(X, Y)
    covered = in_turf(land, X, Y, margin=-2.5)
    in_rock = ((X > rock_box[0][0] + 2) & (X < rock_box[1][0] - 2) & (Y > rock_box[0][1] + 2)
               & (Y < rock_box[1][1] - 2))
    shown = in_rock & ((P.at("w", X, Y) > 0.02) | wet)
    ob, me = BL.grid_object("ground", X, Y, Z, ~(covered | shown), any_=True)
    me.shade_smooth()
    return ob


# -- the build ---------------------------------------------------------------------------------------------------------

BOX = [(-58.0, -60.0, BL.BED), (206.0, 80.0, 33.0)]


def build(out, reuse=False, source=700_000):
    """The land: its history, its rock as a mesh (reduced once to `source` triangles, the normal map's source and
    every view's start), its turf."""
    t = time.time()
    plan = BL.Plan(BOX[0][0] - 45, BOX[1][0] + 5, BOX[0][1] - 45, BOX[1][1] + 5)
    land = Land(plan, BOX)
    land.fracture(BOX)
    land.debris()
    land.topple()
    land.overhangs()
    print(f"history: {time.time() - t:.0f}s, {len(land.blocks)} blocks")
    path = os.path.join(out, "bluff-land.vdb")
    if reuse and os.path.exists(path):
        lo = np.array(BOX[0], float)
        print("rock grid: reused", path)
    else:
        lo = build_grid(land, BOX, LAND["voxelM"], path)
    ro = rock_mesh(path, lo)
    snap(land, ro)
    tb = ((on_ground_lines(BOX[0][0] - 40, 0, False), on_ground_lines(BOX[1][0] + 2, 0, False)),
          (on_ground_lines(BOX[0][1] - 40, 1, False), on_ground_lines(BOX[1][1] + 2, 1, False)))
    tu = turf(land, tb[0][0], tb[0][1], tb[1][0], tb[1][1])
    # the faces the turf hides: inside its edge, under its soil, and away from the sea's cuts
    C, _ = centres(ro.data)
    top = turf_z(land, C[:, 0], C[:, 1])
    hid = in_turf(land, C[:, 0], C[:, 1], margin=0.6) & (C[:, 2] < top - 0.05) & (land.sea_cut(C) > 1.5)
    hid |= C[:, 2] < BL.BED + 0.2
    drop_faces(ro, hid)
    dense = tri_count(ro)
    collapse(ro, source)
    ro.hide_render = True
    print(f"rock: {dense} triangles dense, {tri_count(ro)} as the source; {time.time() - t:.0f}s")
    return land, ro, tu


def main():
    out = arg("--out")
    os.makedirs(out, exist_ok=True)
    t = time.time()
    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o)
    land, src, tu = build(out, reuse=bool(arg("--reuse")))
    gr = far_ground(land, BOX)
    se = BL.sea()
    grey = BL.material("clay", (0.20, 0.20, 0.20), 0.8)
    for ob in (tu, gr):
        ob.data.materials.clear()
        ob.data.materials.append(grey)
    se.data.materials.append(BL.material("sea", (0.02, 0.025, 0.03), 0.12))
    for k, (x, y) in enumerate(FIX.get("figures", [])):
        for f in figure(x, y, land, f"fig{k}"):
            f.data.materials.append(grey)
    light = FIX["lights"]["lowsun"]
    BL.world(light)
    BL.sun(light)
    views = {vw["name"]: vw for vw in FIX["views"]}
    BL.cycles(int(arg("--w", 1600)), int(arg("--h", 900)), int(arg("--samples", 32)))
    for name in arg("--view", "cave").split(","):
        for o in [o for o in bpy.data.objects if o.type == "CAMERA" or o.name.startswith("rock-view")]:
            bpy.data.objects.remove(o)
        BL.camera(views[name], land)
        cam = np.array(bpy.context.scene.camera.location)
        if arg("--dense"):
            ro = src.copy()
            bpy.context.scene.collection.objects.link(ro)
            ro.hide_render = False
            shade(ro)
        else:
            ro = view_rock(land, src, cam)
        ro.name = "rock-view"
        ro.data.materials.clear()
        ro.data.materials.append(grey)
        if arg("--blend"):
            bpy.ops.wm.save_as_mainfile(filepath=arg("--blend"))
        bpy.context.scene.render.filepath = os.path.join(out, f"{name}-grey.png")
        bpy.ops.render.render(write_still=True)
        print("wrote", bpy.context.scene.render.filepath, f"{time.time() - t:.0f}s")


if __name__ == "__main__":
    main()
