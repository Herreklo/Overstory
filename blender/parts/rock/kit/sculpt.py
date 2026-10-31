"""Stage 2, the high-poly sculpt (kit.json `sculpt`): a mass's designed planes (the blockout's, `mass.py --step block`)
as one signed-distance form, each face gently domed by its kind (`bow`, mass.py's bulge) so its arrises and silhouette
bow, shaded by its own plane's normal so it keeps one value (the high-poly's normals are the planes', blended across
each arris); each old arris a small round (`chamfer`, sized by the weather it faces, tapering end to end) wandering
softly along its length (`wander`), a fresh one crisp. Then the edges' line by age (stage 10), every mark a planar cut
from the mass's record, each a chip as rock breaks (chip(): a fracture floor running out at one end, one slanted riser
on the structure at the other): the breaks (`breaks`: the dated spall, a few on the fresh face's arrises, one at the
foot), small chips along the fresh arrises (`nick`), the old top/side borders' long steps (`border`), the crack's mouth
notched by a V at the arris (`notch`, on the trace `crack` chooses for sculpt.py and paint.py both). The boulder takes
only the dated ones: its old edges are worn, so its chips are off in the data, and its two dated breaks (the spall,
the plucked face) have their outlines broken along the layers in bites of creased facets (ragged(): the core of every
dated break). Meshed by openvdb at `voxelM`, evaluated only in bands refined from coarser
levels, finer near the crisp marks (refine()); checked for pinches (no arris under `leastArrisM`) and splinters
(mass.py's measure); shot in grey from the blockout's views and saved for the bake as `high_<id>` in `<gen>/high.blend`.

    Blender -b --factory-startup -P sculpt.py -- --out DIR [--gen DIR] [--masses boulder] [--views front,near] [--voxel M]
"""
import json, math, os, sys
from types import SimpleNamespace

import bpy
import numpy as np
import openvdb as vdb

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mass as MS  # noqa: E402

HS, S, arg = MS.HS, MS.K["sculpt"], MS.arg
OUT = os.path.abspath(arg("--out", os.path.join(MS.ROOT, "cache", "rock", "kit", "renders", "r04", "s2")))


def smax(a, b, k):
    """The larger of a and b, its crease rounded over k (a polynomial smooth maximum; k a number or per point)."""
    return np.maximum(a, b) + np.maximum(k - np.abs(a - b), 0.0) ** 2 / (4 * k)


def blend(a, b, k):
    """smax's share of b at each point: its gradient is blend * grad b + (1 - blend) * grad a."""
    return np.clip(0.5 + (b - a) / (2 * k), 0.0, 1.0)


def ss(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0.0, 1.0)
    return t * t * (3 - 2 * t)


class Noise:
    """Value noise in [-1, 1] on the integer lattice, its table drawn from a seeded stream (choices integer-hashed)."""

    def __init__(self, *key):
        st = HS.Stream(*key); self.t = np.array([st.uniform(-1.0, 1.0) for _ in range(4096)])

    def __call__(self, P):
        i = np.floor(P).astype(np.int64); f = P - i; u = f * f * (3 - 2 * f); out = np.zeros(len(P))
        for dx in (0, 1):
            for dy in (0, 1):
                for dz in (0, 1):
                    h = ((i[:, 0] + dx) * 73856093 ^ (i[:, 1] + dy) * 19349663 ^ (i[:, 2] + dz) * 83492791) & 4095
                    w = (u[:, 0] if dx else 1 - u[:, 0]) * (u[:, 1] if dy else 1 - u[:, 1]) * (u[:, 2] if dz else 1 - u[:, 2])
                    out += w * self.t[h]
        return out


def skewed(st, lo, hi, k):
    return MS.skewed(st, lo, hi, k)


def polygon_area(n, pts):
    """The area of the convex polygon of points pts lying in a plane of normal n."""
    if len(pts) < 3:
        return 0.0
    u = np.cross(n, [0.3, 0.5, 0.8]); u /= np.linalg.norm(u); v = np.cross(n, u)
    q = np.array([[p @ u, p @ v] for p in pts]); c = q.mean(0); q = q[np.argsort(np.arctan2(q[:, 1] - c[1], q[:, 0] - c[0]))]
    return 0.5 * abs(float(np.dot(q[:, 0], np.roll(q[:, 1], 1)) - np.dot(q[:, 1], np.roll(q[:, 0], 1))))


class Sculpt:
    def __init__(self, X):
        self.X, self.id = X, X["id"]
        bow = {k: S["bow"][k] for k in ("share", "reach", "shift", "amp", "power")}
        self.ms = MS.Mass(X, over={"bulge": {**MS.M["bulge"], **bow}}, wear=False)  # the designed planes, domed by kind
        T = X["structure"]; R_ = MS.lean(X)[0]  # its own structure leans with it
        self.sets = [("foliation", R_ @ MS.unit(T["foliation"]["dipToward"], T["foliation"]["dip"]))] + \
            [(j["name"], R_ @ MS.unit(j["dipToward"], j["dip"])) for j in T["joints"]]
        self.nf = self.sets[0][1]
        w = S["chamfer"]["weather"]; self.weather = MS.unit(w[0], 90 - w[1])
        fs = self.ms.faces; self.N = np.array([f[0] for f in fs]); self.O = np.array([f[1] for f in fs])
        self.kind = [f[2] for f in fs]; self.fresh = set(S["fresh"]); self.sink = X.get("sinkM", 0.0)
        self.pairs = self.arris_table()
        self.cracks, self.chips = self.place_cracks(), self.place_chips()
        self.taken = {}  # (i, j) -> [(s0, s1)] metres along the designed arris already marked
        self.trace = self.crack_trace()
        self.notch = self.place_notch()
        self.breaks = self.place_breaks()
        self.nicks = self.place_nicks()
        self.borders = self.place_borders()
        self.faces_cut = self.place_faces()
        self.regions = self.notch + self.breaks + self.nicks + self.borders + self.faces_cut

    # ------------------------------------------------------------ the domed planes
    def lift(self, i, P):
        wp = self.ms.faces[i][4]
        return wp[0](P) if wp is not None else 0.0

    def val(self, i, P):
        """Face i's signed distance at P, domed: the plane lifted by its bulge."""
        return P @ self.N[i] - self.O[i] - self.lift(i, P)

    def tangent(self, i, Q):
        """Face i's domed surface's outward normal at a point Q."""
        n, wp = self.N[i], self.ms.faces[i][4]
        if wp is None:
            return n
        w, a, b = wp; e = 0.01; Q = np.asarray(Q)[None]
        du = float((w(Q + e * a) - w(Q - e * a))[0]) / (2 * e); dv = float((w(Q + e * b) - w(Q - e * b))[0]) / (2 * e)
        G = n - du * a - dv * b
        return G / np.linalg.norm(G)

    def arris_at(self, p, s):
        """The domed faces' sharp arris at share s along the designed arris p (Newton across it, square to it)."""
        i, j = p["i"], p["j"]; Q = p["P0"] + s * p["ln"] * p["t"]; A = np.array([self.N[i], self.N[j], p["t"]])
        for _ in range(5):
            Q = Q + np.linalg.solve(A, np.array([-self.val(i, Q[None])[0], -self.val(j, Q[None])[0], 0.0]))
        return Q

    # ------------------------------------------------------------ the arrises
    def edges(self):
        """The designed arrises out of the base: [(i, j, end, end)], each pair of faces meeting along a line between two
        corners, the base's arrises and a turn past 120 degrees left out."""
        fs = self.ms.faces; cs = MS.corners([(f[0], f[1]) for f in fs]); out = []
        for i in range(len(fs)):
            for j in range(i + 1, len(fs)):
                ends = [p for p, s in cs if i in s and j in s]
                if "base" in (fs[i][2], fs[j][2]) or float(fs[i][0] @ fs[j][0]) <= -0.5 or len(ends) < 2:
                    continue
                out.append((i, j, ends[0], ends[-1]))
        return out

    def arris_table(self):
        """Each designed arris's round and wander. A worn arris is rounded back `w` into each face: `big` where its
        bisector faces the weather (toward `weather`, over `at`), `small` in shelter, its width changing end to end by a
        seeded share of `taper` (the transport wore it unevenly); a fresh one crisp, `fresh`. The round is the smooth
        maximum of the two domed faces over k = w times the sine of their turn, so it follows the arris's bow; any
        other two faces meet crisp to `soft`. An old arris wanders softly (`wander`): one face pushed in and out along
        it by a seeded line of knots `waveM` apart, at most `amp`, fading over `fade` of its length at each end and
        within `bandM` of the arris.
        [dict] the arrises; per pair of faces the tables form() reads."""
        Ch, Wd = S["chamfer"], S["wander"]; nf = len(self.N)
        st = HS.Stream("lt1-holm-tip", "sculpt", "taper", self.id); sw = HS.Stream("lt1-holm-tip", "sculpt", "wander", self.id)
        self.K0 = np.full((nf, nf), Ch["soft"]); self.K1 = self.K0.copy(); self.PA = np.zeros((nf, nf, 3))
        self.TA = np.zeros((nf, nf, 3)); self.TA[..., 0] = 1.0; self.LN = np.ones((nf, nf)); self.wand = {}; out = []
        for i, j, P0, P1 in self.edges():
            nA, nB = self.N[i], self.N[j]; c = float(nA @ nB); sphi = math.sqrt(max(1.0 - c * c, 1e-6))
            t = P1 - P0; ln = float(np.linalg.norm(t)); t = t / ln
            fresh = bool({self.kind[i], self.kind[j]} & self.fresh)
            if fresh:
                w0 = w1 = Ch["fresh"]
            else:
                b = (nA + nB) / np.linalg.norm(nA + nB); k = float(np.clip((b @ self.weather - Ch["at"][0]) / (Ch["at"][1] - Ch["at"][0]), 0, 1))
                w = Ch["small"] + (Ch["big"] - Ch["small"]) * k * k * (3 - 2 * k)
                a = st.uniform(*Ch["taper"]) * (1 if st.random() < 0.5 else -1); w0, w1 = w * (1 - a), w * (1 + a)
            for p_, q_ in ((i, j), (j, i)):
                self.K0[p_, q_], self.K1[p_, q_] = w0 * sphi, w1 * sphi
                self.PA[p_, q_], self.TA[p_, q_], self.LN[p_, q_] = P0, t, ln
            if not fresh:
                xs = [0.0]
                while xs[-1] < ln:
                    xs.append(xs[-1] + Wd["waveM"] * sw.uniform(0.6, 1.4))
                ys = [Wd["amp"] * sw.uniform(-1.0, 1.0) for _ in xs]
                self.wand[(i, j)] = self.wand[(j, i)] = (np.array(xs) / ln, np.array(ys))
            out.append(dict(i=i, j=j, P0=P0, P1=P1, t=t, ln=ln, w=(round(w0, 4), round(w1, 4)), fresh=fresh,
                            turn=math.degrees(math.acos(np.clip(c, -1, 1)))))
        self.wnb = {j: [i for (i, j_) in self.wand if j_ == j] for j in range(nf)}
        return out

    def form(self, P):
        """The domed planes at P, each arris rounded by its own k, the old ones wandering: (signed distance, the shading
        normal: each face's own plane's, blended across a round as the smooth maximum blends the faces)."""
        Wd = S["wander"]; d = self.val(0, P); g = np.tile(self.N[0], (len(P), 1)); own = np.zeros(len(P), int)
        for j in range(1, len(self.N)):
            v = self.val(j, P)
            for i in self.wnb[j]:
                m = own == i
                if not m.any():
                    continue
                s = np.einsum("ij,j->i", P[m] - self.PA[i, j], self.TA[i, j]) / self.LN[i, j]; xs, ys = self.wand[(i, j)]
                fall = np.clip(1.0 - np.abs(v[m] - d[m]) / Wd["bandM"], 0.0, 1.0) ** 2
                v[m] += np.interp(s, xs, ys) * ss(0.0, Wd["fade"], s) * ss(1.0, 1.0 - Wd["fade"], s) * fall
            s = np.clip(np.einsum("ij,ij->i", P - self.PA[own, j], self.TA[own, j]) / self.LN[own, j], 0.0, 1.0)
            k = self.K0[own, j] + (self.K1[own, j] - self.K0[own, j]) * s
            h = blend(d, v, k); own = np.where(v > d, j, own); d = smax(d, v, k)
            g = h[:, None] * self.N[j] + (1 - h)[:, None] * g
        return d, g / np.maximum(np.linalg.norm(g, axis=1), 1e-12)[:, None]

    def surface(self, a, b):
        """The form's surface between a (outside) and b (inside), by bisection."""
        for _ in range(30):
            m = (a + b) / 2
            if self.form(m[None])[0][0] > 0:
                a = m
            else:
                b = m
        return (a + b) / 2

    # ------------------------------------------------------------ placing: shared
    def free(self, key, s0, s1):
        """Whether metres s0..s1 along arris key are clear of every mark on it by `gapM`."""
        g = S["breaks"]["gapM"]
        return all(s1 + g <= a or s0 - g >= b for a, b in self.taken.get(key, []))

    def runs(self, p, lo, hi):
        """The free runs along arris p between metres lo and hi (clear of every mark by `gapM` and of the crack's trace),
        longest first: [(s0, s1)]."""
        g = S["breaks"]["gapM"]; cut = sorted((a - g, b + g) for a, b in self.taken.get((p["i"], p["j"]), []))
        Tr = self.trace
        if Tr is not None and Tr["A"] in (p["i"], p["j"]):  # the trace's crossing, `clearM` and more each side
            a0, a1 = p["P0"] @ Tr["n"] - Tr["x"], (p["P0"] + p["ln"] * p["t"]) @ Tr["n"] - Tr["x"]
            if a0 * a1 < 0:
                x = a0 / (a0 - a1) * p["ln"]; c = self.trace_clear(p)
                cut = sorted(cut + [(x - c, x + c)])
        out, x = [], lo
        for a, b in cut:
            if a > x:
                out.append((x, min(a, hi)))
            x = max(x, b)
        if x < hi:
            out.append((x, hi))
        return sorted([r for r in out if r[1] > r[0]], key=lambda r: r[0] - r[1])

    def take(self, p, s0, s1):
        self.taken.setdefault((p["i"], p["j"]), []).append((s0, s1))

    def upper(self, p):
        """(upper face, lower face) of an arris: the one facing more up first."""
        return (p["i"], p["j"]) if self.N[p["i"]][2] >= self.N[p["j"]][2] else (p["j"], p["i"])

    def riser(self, t):
        """The plane of the structure a step along direction t stands on, crossing t at a slant (rock steps where the
        fracture met a layer or a joint, never square to the arris): of the sets crossing t by `riser.least` to
        `riser.most` (cosines), the foliation if it is one, else the most square; with none, the set nearest that range.
        (normal along +t, name)"""
        Rs = S["breaks"]["riser"]; c = lambda n: abs(n @ t)  # noqa: E731
        ok = [s_ for s_ in self.sets if Rs["least"] <= c(s_[1]) <= Rs["most"]]
        name, n = (ok[0] if ok[0][0] == "foliation" else max(ok, key=lambda s_: c(s_[1]))) if ok else \
            min(self.sets, key=lambda s_: min(abs(c(s_[1]) - Rs["least"]), abs(c(s_[1]) - Rs["most"])))
        return n * (1 if n @ t >= 0 else -1), name

    def faces_at(self, p, Qm, t):
        """An arris's two faces at Qm: (upper, lower, their domed normals, the directions into each square to t)."""
        U, L = self.upper(p); nU, nL = self.tangent(U, Qm), self.tangent(L, Qm)
        uU = np.cross(t, nU); uU *= -1 if uU @ nL > 0 else 1; uL = np.cross(t, nL); uL *= -1 if uL @ nU > 0 else 1
        return U, L, nU, nL, uU, uL

    def chip(self, p, s0, s1, D, ratio, soft, why, small=None, st=None, onto=False):
        """A chip knocked off arris p, as rock breaks: a wedge of two planes. Its floor the fracture, one plane cutting
        the corner from nothing at share s0 (it runs out along the arris) to D down the lower face and ratio of D into
        the upper one at share s1; there one riser on the structure (riser(), at a slant), removing toward s0. small
        (`breaks.small`, with st): beyond the riser, at its share, a small chip running out the other way, so the deep
        end steps down twice. onto: its ends on the form's own worn arris (its round and wander) rather than the domed
        planes' sharp one, which stands up to a centimetre proud of it: a shallow step measured from the stone. [region]"""
        Q0, Q1 = self.arris_at(p, s0), self.arris_at(p, s1); t = Q1 - Q0; t /= np.linalg.norm(t)
        U, L, nU, nL, uU, uL = self.faces_at(p, Q1, t)
        if onto:
            bi = (nU + nL) / np.linalg.norm(nU + nL)
            for _ in range(4):
                Q0, Q1 = Q0 - self.form(Q0[None])[0][0] * bi, Q1 - self.form(Q1[None])[0][0] * bi
        f = np.cross(Q1 + D * uL - Q0, Q1 + ratio * D * uU - Q0); f /= np.linalg.norm(f); f *= 1 if f @ (nU + nL) > 0 else -1
        m, name = self.riser(t); walls = [(-m, float(-m @ Q1))]
        Lm = float(np.linalg.norm(Q1 - Q0)); c = (Q0 + Q1) / 2
        out = [dict(f=f, of=float(f @ Q0), walls=walls, planes=[(f, float(f @ Q0))] + walls, soft=soft, why=why, riser=name,
                    c=c, r=Lm / 2 + 3 * D * (1 + ratio) + 0.05, at=c.round(3).tolist(), lenM=round(Lm, 3), depthM=round(D, 3))]
        if small and st.random() < small["share"]:
            a = st.uniform(*small["lenM"]) / p["ln"] * (1 if s1 > s0 else -1)
            if 0.0 < s1 + a < 1.0:
                out += self.chip(p, s1 + a, s1, min(st.uniform(*small["depthM"]), 0.5 * D), ratio, soft, why)
        return out

    # ------------------------------------------------------------ placing: the crack and its notch
    def crack_trace(self):
        """Where the one drawn crack runs (kit.json `skin.crack`, read here for sculpt.py and paint.py both): the `set`
        joint's trace down the biggest side facing the mass's front (facing it at least `front`, its slope within 0.6
        of level, out of the turf, an old face), at a seeded offset of up to `offset` of the face's span about its
        middle; its mouth where that trace crosses the arris at the side's top, onto the face above. None if no side."""
        Cr = MS.K["skin"]["crack"]
        if not Cr["use"]:
            return None
        nj = dict(self.sets)[Cr["set"]]; front = MS.unit(self.X["front"], 90); cs = MS.corners([(f[0], f[1]) for f in self.ms.faces])
        def area(i):
            pts = [p for p, s in cs if i in s]; pts = [q for q in pts if q[2] >= self.sink] + \
                [p + (q - p) * (self.sink - p[2]) / (q[2] - p[2]) for a_, p in enumerate(pts) for q in pts[a_ + 1:] if (p[2] - self.sink) * (q[2] - self.sink) < 0]
            return polygon_area(self.N[i], pts)
        sides = [i for i in range(len(self.N)) if self.N[i] @ front >= Cr["front"] and abs(self.N[i][2]) <= 0.6 and self.kind[i] not in self.fresh | {"base"}]
        if not sides:
            return None
        A = max(sides, key=area); tA = np.array([p @ nj for p, s in cs if A in s and p[2] >= self.sink])
        rc = HS.Stream(MS.K["world"], "rock", self.id, "paint", "crack")  # paint.py's own stream: its first draw
        x = float((tA.min() + tA.max()) / 2) + Cr["offset"] * float(np.ptp(tA)) * rc.uniform(-1.0, 1.0)
        best = None
        for p in self.pairs:
            if A not in (p["i"], p["j"]):
                continue
            o = p["j"] if p["i"] == A else p["i"]
            if self.N[o][2] <= self.N[A][2]:
                continue
            a0, a1 = p["P0"] @ nj - x, p["P1"] @ nj - x
            if a0 * a1 < 0:
                s = a0 / (a0 - a1); z = (p["P0"] + s * (p["P1"] - p["P0"]))[2]
                if best is None or z > best[0]:
                    best = (z, p, o, s)
        if best is None:
            return None
        _, p, U, s = best
        for _ in range(4):  # on the domed arris: the share where its sharp line meets the trace's plane
            a_ = self.arris_at(p, s) @ nj - x; s = float(np.clip(s - a_ / (p["ln"] * (p["t"] @ nj)), 0, 1))
        return dict(A=A, U=U, keyA=self.ms.faces[A][3], keyU=self.ms.faces[U][3], n=nj, x=x, pair=p, s=s,
                    mouth=self.arris_at(p, s), set=Cr["set"])

    def place_notch(self):
        """The crack's mouth notched where its trace meets the arris (`notch`): a V across the arris on the trace,
        `alongM` wide along it, its two planes meeting on a line from `downM` down the side along the trace to `backM`
        into the top, each through one end; old, rounded to `soft`. [region]"""
        Tr, Nt = self.trace, S["notch"]
        if Tr is None or not Nt["use"]:
            return []
        p, s, A, U, nj = Tr["pair"], Tr["s"], Tr["A"], Tr["U"], Tr["n"]; M = Tr["mouth"]
        h = Nt["alongM"] / 2 / p["ln"]; E1, E2 = self.arris_at(p, s - h), self.arris_at(p, s + h)
        nA, nU = self.tangent(A, M), self.tangent(U, M); t = (E2 - E1) / np.linalg.norm(E2 - E1)
        dA = np.cross(nj, nA); dA /= np.linalg.norm(dA); dA *= -1 if dA @ nU > 0 else 1
        dU = np.cross(t, nU); dU /= np.linalg.norm(dU); dU *= -1 if dU @ nA > 0 else 1
        B, T = M + Nt["downM"] * dA, M + Nt["backM"] * dU; planes = []
        for P_, away in ((E1, E2), (E2, E1)):  # each removes toward the other end
            n = np.cross(T - B, P_ - B); n /= np.linalg.norm(n); n *= 1 if (away - B) @ n > 0 else -1
            planes.append((n, float(n @ B)))
        self.take(p, (s - h) * p["ln"], (s + h) * p["ln"])
        return [dict(f=planes[0][0], of=planes[0][1], walls=planes[1:], planes=planes, soft=Nt["soft"], why="notch",
                     c=(B + T + E1 + E2) / 4, r=Nt["alongM"] + Nt["downM"] + 0.06, at=M.round(3).tolist(), lenM=Nt["alongM"],
                     depthM=Nt["downM"])]

    # ------------------------------------------------------------ placing: the breaks
    def place_breaks(self):
        """Breaks (`breaks`), as rock breaks (chip()): few and big, as 58's. `corner` the top corner the mass's record
        says frost spalled off (its `spall` [bearing, says]: the true top corner nearest that bearing), taken off whole
        by one plane across it facing its faces' mean (turned up to `jitterDeg`) `depthM` deep, no wider than `capM`;
        `fresh` a few chips along the fresh face's arrises (59's jagged accent); `foot` one big chip off the foot arris
        facing the front most, its floor falling toward the turf (more down the lower face than into the upper one,
        `ratio`). Each chip `lenM` long and `depthM` deep at its stepped end, on arrises turning `minDeg` or more and
        falling at most a place's `steepest`, never over another mark (`gapM`), never past `along` of an arris from its
        ends; its stepped end at either end (seeded), stepping twice by `small`. A break dated by the record (the spall;
        the fresh face's, by the frost that made it) is crisp (`soft` fresh); an undated one has weathered as its
        faces (`soft` old). [region]"""
        B = S["breaks"]; st = HS.Stream("lt1-holm-tip", "sculpt", "break", self.id); out = []
        front = MS.unit(self.X["front"], 90)
        E = [p for p in self.pairs if p["turn"] >= B["minDeg"]]
        flat = lambda why: [p for p in E if abs(p["P1"][2] - p["P0"][2]) / p["ln"] <= B[why]["steepest"]]  # noqa: E731
        fresh_e = [p for p in flat("fresh") if p["fresh"] and min(p["P0"][2], p["P1"][2]) > self.sink + B["fresh"]["aboveM"]]
        foot_e = [p for p in flat("foot") if not p["fresh"] and float((self.N[p["i"]] + self.N[p["j"]]) @ front) > 0
                  and B["foot"]["bandM"][0] < min(p["P0"][2], p["P1"][2]) - self.sink and max(p["P0"][2], p["P1"][2]) - self.sink < B["foot"]["bandM"][1]]
        soft = lambda why: B["soft"]["fresh" if why in B["dated"] else "old"]  # noqa: E731
        if B["corner"]["count"] and self.X.get("spall"):
            Bc = B["corner"]; tow = MS.unit(self.X["spall"][0], 90)
            # a true corner: three faces or more each turning `minDeg` or more from every other (a kink on a border is
            # no corner: a flake there runs out along it as a sliver), one a top (facing `up` or more up)
            def true(ks):
                return len(ks) >= 3 and all(self.N[a] @ self.N[b] <= math.cos(math.radians(B["minDeg"])) for x, a in enumerate(ks) for b in ks[x + 1:])
            cs = [(q, [k for k in ks if self.kind[k] != "base"]) for q, ks in MS.corners([(f[0], f[1]) for f in self.ms.faces])]
            P1, on = max(((q, ks) for q, ks in cs if true(ks) and max(self.N[k][2] for k in ks) >= Bc["up"]),
                         key=lambda c: float(c[0] @ tow) + c[0][2])
            u = sum(self.N[k] for k in on); u /= np.linalg.norm(u)
            v = np.array([st.normal(), st.normal(), st.normal()]); v -= (v @ u) * u
            u = u + math.tan(math.radians(st.uniform(0, Bc["jitterDeg"]))) * v / max(np.linalg.norm(v), 1e-9); u /= np.linalg.norm(u)
            c = self.surface(P1 + 0.3 * u, P1 - 0.8 * u); dep = skewed(st, *Bc["depthM"], 1)
            fl = [(f[0], f[1]) for f in self.ms.faces]
            for _ in range(4):  # no wider than `capM` from the corner: its depth held
                ext = max(float(np.linalg.norm(q - P1)) for q, ks in MS.corners(fl + [(u, float(u @ c) - dep)]) if len(fl) in ks)
                dep *= min(1.0, Bc["capM"] / ext)
            ext = max(float(np.linalg.norm(q - P1)) for q, ks in MS.corners(fl + [(u, float(u @ c) - dep)]) if len(fl) in ks)
            of = float(u @ c) - dep
            out += [dict(f=u, of=of, walls=[], planes=[(u, of)], soft=soft("corner"), why="corner", riser="", c=P1,
                         r=ext + Bc["reachM"], at=P1.round(3).tolist(), slab=0, face=None, capM=round(ext, 3),
                         lenM=round(ext, 3), depthM=round(dep, 3))]
            out += self.ragged(u, of, fl + [(u, of)], len(fl), soft("corner"), "corner", st, cap=dep)  # its outline
            for p in E:  # the arrises it took from its corner
                for e in (0, 1):
                    if np.linalg.norm(p["P" + str(e)] - P1) < 1e-3:
                        self.take(p, 0.0, ext) if e == 0 else self.take(p, p["ln"] - ext, p["ln"])
        for why, pool in (("fresh", fresh_e), ("foot", foot_e)):
            R = B[why]; want = st.randint(*R["count"]); tries = 0; got = 0
            pool = [p for p in pool if B["along"][1] - B["along"][0] > R["lenM"][0] / p["ln"]]
            while pool and got < want and tries < 60:
                tries += 1
                first = why == "foot" and got == 0
                p = max(pool, key=lambda q: float((self.N[q["i"]] + self.N[q["j"]]) @ front)) if first else pool[st.randint(0, len(pool) - 1)]
                if self.chip_on(p, R, st, soft(why), why, out):
                    got += 1
        return out

    def ragged(self, u, of, planes, bi, soft, why, st, face=None, cap=None):
        """A dated break's outline broken along the layers (`breaks.ragged`, 58's broken slabs): on `runs` of its border
        arrises (seeded, of those a set of the structure crosses at `crossLeast` or more; only their stretch `aboveM`
        clear of the turf, within `along`), a run of `bites` bites, `facets` facets in all, each `facetM` along (skewed
        small). A bite's floor is the break's plane (planes[bi], u.x = of) sunk toward the arris by a depth that rises
        and falls along it, `stepM` at its knots (skewed small, the last the deepest or `fallShare` of it, so no facet
        runs as an even band; a cut's at most `capShare` of its depth `cap`), each
        facet one plane, so the facets meet in creases and the outline, where they run out on the old face, zigzags.
        Each facet rises inward to meet the break's plane `inM` in (skewed) at its deepest, its turn off the plane within
        `tiltDeg` and `turnShare` of the arris's own so it runs out on the old face a little past the arris. A bite runs
        out at its first end and stops at its last on the set's plane: a riser standing its depth there, running out to
        nothing inward. Each region reaches the polytope that holds what it can take. [regions]"""
        Rg = S["breaks"]["ragged"]
        if not Rg["use"]:
            return []
        cs = [(q, ks) for q, ks in MS.corners(planes) if bi in ks]; cen = np.mean([q for q, _ in cs], 0); E = []
        for a in range(len(cs)):
            for b in range(a + 1, len(cs)):
                sh = (set(cs[a][1]) & set(cs[b][1])) - {bi}
                if len(sh) != 1:
                    continue
                j = sh.pop(); Pa, Pb = cs[a][0], cs[b][0]; t = Pb - Pa; ln = float(np.linalg.norm(t)); t = t / ln
                if j >= len(self.N) or self.kind[j] == "base":
                    continue
                zc = self.sink + Rg["aboveM"]; lo, hi = Rg["along"][0] * ln, Rg["along"][1] * ln  # clear of the turf
                if abs(t[2]) > 1e-6:
                    sz = (zc - Pa[2]) / t[2]
                    lo, hi = (max(lo, sz), hi) if t[2] > 0 else (lo, min(hi, sz))
                elif Pa[2] < zc:
                    continue
                st_ = next(((nm, n) for nm, n in sorted(self.sets, key=lambda s_: s_[0] != Rg["set"])
                            if abs(n @ t) >= Rg["crossLeast"] and np.linalg.norm(np.cross(n, u)) > 0.3), None)
                if st_ is None or hi - lo < Rg["facets"][0] * Rg["facetM"][0]:
                    continue
                uin = np.cross(u, t); uin = uin if uin @ (cen - Pa) > 0 else -uin
                E.append(dict(j=j, Pa=Pa, t=t, ln=ln, lo=lo, hi=hi, set=st_, uin=uin,
                              beta=math.acos(float(np.clip(u @ self.N[j], -1, 1)))))
        out = []; want = st.randint(*Rg["runs"][why])
        for e in sorted(E, key=lambda _: st.random())[:want]:
            Pa, t, lo, hi = e["Pa"], e["t"], e["lo"], e["hi"]
            if st.random() < 0.5:  # which end it runs out at
                Pa, t, lo, hi = Pa + e["ln"] * t, -t, e["ln"] - hi, e["ln"] - lo
            uin = e["uin"]; nm, ns = e["set"]; sg = 1.0 if ns @ t > 0 else -1.0
            tmax = math.tan(min(math.radians(Rg["tiltDeg"]), Rg["turnShare"] * e["beta"]))
            nb = st.randint(*Rg["bites"]); nf = st.randint(*Rg["facets"]); nf = max(nf, 2 * nb)
            per = [nf // nb + (1 if k < nf % nb else 0) for k in range(nb)]
            L = [np.array([skewed(st, *Rg["facetM"], Rg["skew"]) for _ in range(p)]) for p in per]
            tot = sum(x.sum() for x in L); L = [x * min(1.0, (hi - lo) / tot) for x in L]; tot = sum(x.sum() for x in L)
            s0 = st.uniform(lo, hi - tot)
            for bk in range(nb):
                q = s0 + sum(x.sum() for x in L[:bk]) + np.concatenate([[0.0], np.cumsum(L[bk])])
                dmax = lambda i: 0.7 * tmax * min(L[bk][max(i - 1, 0)], L[bk][min(i, len(L[bk]) - 1)])  # noqa: E731
                d = [0.0] + [skewed(st, *Rg["stepM"], Rg["skew"]) for _ in range(len(L[bk]))]
                if len(d) > 2:  # its riser the deepest, or `fallShare` of the deepest before it: no facet a band
                    d[-1] = max(max(d[1:-1]) * 1.3, d[-1]) if st.random() < 0.5 else min(d[-1], st.uniform(*Rg["fallShare"]) * max(d[1:-1]))
                    d[-1] = max(d[-1], Rg["stepM"][0])  # a riser that reads
                d = [min(x, dmax(i), Rg["capShare"] * cap if cap is not None else 9.0) for i, x in enumerate(d)]
                keep = [0]  # the knots on its upper hull: the depth rises then falls, a facet to each span
                for i in range(1, len(q)):
                    while len(keep) >= 2 and (d[keep[-1]] - d[keep[-2]]) * (q[i] - q[keep[-1]]) <= (d[i] - d[keep[-1]]) * (q[keep[-1]] - q[keep[-2]]):
                        keep.pop()
                    keep.append(i)
                fl_ = []
                for i0, i1 in zip(keep, keep[1:]):
                    b_ = (d[i1] - d[i0]) / (q[i1] - q[i0]); a_ = d[i0] - b_ * q[i0]; dm = max(d[i0], d[i1])
                    c_ = -min(dm / skewed(st, *Rg["inM"], 1), math.sqrt(max(tmax ** 2 - b_ * b_, 0.0)) or 1e-3)
                    n_ = np.cross(t - b_ * u, uin - c_ * u); n_ = n_ if n_ @ u > 0 else -n_; n_ /= np.linalg.norm(n_)
                    fl_.append((n_, float(n_ @ (Pa - a_ * u))))
                walls = [(-sg * ns, float(-sg * ns @ (Pa + q[-1] * t)))]
                hold = [(-n_, -o_) for n_, o_ in fl_ + walls] + [(u, of + 0.01), (self.N[e["j"]], self.O[e["j"]] + 0.01)]
                P = np.array([p for p, _ in MS.corners(hold)]); c = P.mean(0) if len(P) >= 4 else Pa + q.mean() * t
                r = (float(np.linalg.norm(P - c, axis=1).max()) if len(P) >= 4 else float(q[-1] - q[0])) + 0.03
                out.append(dict(f=fl_[0][0], of=fl_[0][1], walls=fl_[1:] + walls, planes=fl_ + walls, soft=soft, why=why,
                                riser=nm, c=c, r=r, at=c.round(3).tolist(), slab=bk, face=face,
                                edge=self.ms.faces[e["j"]][3], facets=len(fl_), lenM=round(float(q[-1] - q[0]), 3),
                                depthM=round(float(max(d)), 3), riserM=round(float(d[-1]), 3)))
        return out

    def place_faces(self):
        """The fresh faces (`fresh` kinds: the plucked face, dated by the frost that broke it), their outline broken
        along the layers as the spall's (ragged()), crisp (`breaks.soft.fresh`). [regions]"""
        st = HS.Stream("lt1-holm-tip", "sculpt", "face", self.id); out = []; fl = [(f[0], f[1]) for f in self.ms.faces]
        for i, f in enumerate(self.ms.faces):
            if f[2] in self.fresh:
                out += self.ragged(f[0], f[1], fl, i, S["breaks"]["soft"]["fresh"], "pluck", st, face=i)
        return out

    def chip_on(self, p, R, st, soft, why, out):
        """One chip (chip()) of place R's `lenM` (skewed) somewhere free along arris p, within `along`, clear of the
        crack's trace (within R's own `along` if it has one), its stepped end at either end (seeded); appended to out. Its floor at the stepped end: `depthM`
        down the lower face (skewed) and `ratio` of that into the upper one; or, where R has `toward`, turned from the
        upper face by that share of the arris's turn (floor()), `wideM` wide (skewed). The small chip beyond its riser
        (`breaks.small`) unless R's `small` is false. R's `fit`: into the longest free run (runs()), shortened to fit it,
        never under `lenM`'s least. Whether placed."""
        B = S["breaks"]; al = R.get("along", B["along"]); Lm = min(skewed(st, *R["lenM"], B["skew"]), (al[1] - al[0]) * p["ln"])
        if R.get("fit"):  # into the free runs: the longest that holds lenM's least, the step no longer than it
            runs = self.runs(p, al[0] * p["ln"], al[1] * p["ln"])
            if not runs or runs[0][1] - runs[0][0] < R["lenM"][0]:
                return False
            a0, a1 = runs[0]; Lm = min(Lm, a1 - a0); x0 = st.uniform(a0, a1 - Lm)
        else:
            x0 = st.uniform(al[0] * p["ln"], al[1] * p["ln"] - Lm)
        if not self.free((p["i"], p["j"]), x0, x0 + Lm) or not self.clear_of_trace(p, x0, x0 + Lm):
            return False
        a, b = x0 / p["ln"], (x0 + Lm) / p["ln"]; a, b = (a, b) if st.random() < 0.5 else (b, a)
        if R.get("riserFaces") == "front":  # of the two ends, the one whose riser faces the mass's front
            m = self.riser(p["t"] * (1 if b > a else -1))[0]
            a, b = (a, b) if -m @ MS.unit(self.X["front"], 90) > 0 else (b, a)
        if "toward" in R:
            r, al = self.floor(p, b, R, st); band = skewed(st, *R["wideM"], B["skew"])
            D = band / math.sqrt(1.0 + r * r - 2.0 * r * math.cos(al))
        else:
            D, r = skewed(st, *R["depthM"], 1), st.uniform(*R["ratio"])
        out += self.chip(p, a, b, D, r, soft, why, B["small"] if R.get("small", True) else None, st, onto="toward" in R)
        self.take(p, x0, x0 + Lm); return True

    def floor(self, p, s, R, st):
        """A step's floor across arris p at share s, as a layer parts: near the bisector of the two faces, so it takes
        its own value between theirs. Turned from the upper face by a seeded `toward` share of the arris's turn; where a
        set of the structure crosses the arris within `onDeg` of that floor (the foliation first), on that set, held
        `hold` of the turn off each face. (ratio for chip(): how far into the upper face against down the lower, the
        faces' angle at the arris in radians)"""
        Q = self.arris_at(p, s); e = 1e-3 / p["ln"]
        t = self.arris_at(p, min(s + e, 1.0)) - self.arris_at(p, max(s - e, 0.0)); t /= np.linalg.norm(t)
        U, L, nU, nL, uU, uL = self.faces_at(p, Q, t)
        nU, nL = nU - (nU @ t) * t, nL - (nL @ t) * t; nU /= np.linalg.norm(nU); nL /= np.linalg.norm(nL)
        turn = math.acos(float(np.clip(nU @ nL, -1, 1))); e2 = nL - (nL @ nU) * nU; e2 /= np.linalg.norm(e2)
        th = st.uniform(*R["toward"]) * turn; f = math.cos(th) * nU + math.sin(th) * e2
        for name, n in sorted(self.sets, key=lambda s_: s_[0] != "foliation"):
            n = n if n @ (nU + nL) > 0 else -n
            if math.degrees(math.acos(float(np.clip(n @ f, -1, 1)))) <= R["onDeg"]:
                q = n - (n @ t) * t; th = float(np.clip(math.atan2(q @ e2, q @ nU), R["hold"] * turn, (1 - R["hold"]) * turn))
                break
        r = math.sin(turn - th) / math.sin(th); al = math.acos(float(np.clip(uU @ uL, -1, 1)))
        return r, al

    def clear_of_trace(self, p, s0, s1):
        """Whether metres s0..s1 along arris p stay clear of the crack's trace and its notch (trace_clear())."""
        Tr = self.trace
        if Tr is None or Tr["A"] not in (p["i"], p["j"]):
            return True
        a = (p["P0"] + s0 * p["t"]) @ Tr["n"] - Tr["x"]; b = (p["P0"] + s1 * p["t"]) @ Tr["n"] - Tr["x"]
        return a * b > 0 and min(abs(a), abs(b)) / max(abs(p["t"] @ Tr["n"]), 1e-3) > self.trace_clear(p)

    def trace_clear(self, p):
        """How far along arris p a mark keeps off the crack's trace: `clearM` and more on the face, and off its notch by
        half the notch's width and `breaks.apartM`, so two marks on one arris read as two (metres along the arris)."""
        return max((MS.K["skin"]["crack"]["clearM"] + 0.05) / max(abs(p["t"] @ self.trace["n"]), 1e-3),
                   S["notch"]["alongM"] / 2 + S["breaks"]["apartM"])

    def place_nicks(self):
        """A fresh arris's small chips (`nick`): along it in runs `stepM` long (skewed), `share` of its free runs out of
        the turf (seeded which) a chip (chip()) `depthM` deep (skewed small) down the lower face, `ratio` of it into the
        upper, running out at either end (seeded); crisp. [region]"""
        Nk = S["nick"]; st = HS.Stream("lt1-holm-tip", "sculpt", "nick", self.id); out = []
        for p in self.pairs:
            if not p["fresh"] or max(p["P0"][2], p["P1"][2]) < self.sink + 0.05:
                continue
            x, runs = Nk["along"][0] * p["ln"], []
            while True:
                a = skewed(st, *Nk["stepM"], Nk["skew"])
                if x + a > Nk["along"][1] * p["ln"]:
                    break
                if self.free((p["i"], p["j"]), x, x + a) and (p["P0"] + (x + a / 2) * p["t"])[2] > self.sink + 0.03:
                    runs.append((x, a))
                x += a
            order = sorted(range(len(runs)), key=lambda k: st.random())
            for k in sorted(order[:int(round(Nk["share"] * len(runs)))]):
                x, a = runs[k]; dp = skewed(st, *Nk["depthM"], Nk["skew"]); r = st.uniform(*Nk["ratio"])
                a0, a1 = (x / p["ln"], (x + a) / p["ln"]) if st.random() < 0.5 else ((x + a) / p["ln"], x / p["ln"])
                out += self.chip(p, a0, a1, dp, r, Nk["soft"], "nick")
                self.take(p, x, x + a)
        return out

    def place_borders(self):
        """The old top/side borders' long steps (`border`, 58's large boulder: a layer taking the edge off): each old
        arris turning `minDeg` or more between a top (facing `up` or more up) and a steeper face, `minM` long or more,
        out of the turf, gets a chip (chip_on()) at `share`, a second at `second` where it is `twoM` long or more; old,
        rounded to `soft`. [region]"""
        Bd = S["border"]; st = HS.Stream("lt1-holm-tip", "sculpt", "border", self.id); out = []
        for p in self.pairs:
            nz = sorted([self.N[p["i"]][2], self.N[p["j"]][2]])
            if p["fresh"] or p["turn"] < Bd["minDeg"] or not (nz[1] >= Bd["up"] > nz[0]) or p["ln"] < Bd["minM"] \
                    or min(p["P0"][2], p["P1"][2]) < self.sink + 0.1:
                continue
            for k, share in enumerate((Bd["share"], Bd["second"] if p["ln"] >= Bd["twoM"] else 0.0)):
                if st.random() < share:
                    for _ in range(6):
                        if self.chip_on(p, Bd, st, Bd["soft"], "border", out):
                            break
        return out

    def place_cracks(self):
        """Cracks on the mass's own planes of weakness (`crack`): per set a seeded count, each on a plane at a seeded
        offset through the body, reaching `reachM` (skewed: a few long, more short) round a point where the plane meets
        the surface `fromUpDeg` down from its top toward the mass's front; a clean V `widthM` open at the surface and
        `depthM` deep, both closing toward the reach's end."""
        C = S["crack"]; st = HS.Stream("lt1-holm-tip", "sculpt", "crack", self.id); out = []
        V = np.array([p for p, _ in MS.corners([(f[0], f[1]) for f in self.ms.faces])]); mid = V.mean(0); mid[2] = 0.55 * self.ms.H
        front = MS.unit(self.X["front"], 90)
        for name, n in self.sets:
            for _ in range(st.randint(*C["count"][name])):
                t = V @ n; x = st.uniform(t.min() + C["marginM"], t.max() - C["marginM"])
                p0 = mid - (mid @ n - x) * n
                up = np.array([0.0, 0.0, 1.0]) - n[2] * n; up /= np.linalg.norm(up); side = np.cross(n, up)
                a = math.radians(st.uniform(*C["fromUpDeg"])); side = side if side @ front >= 0 else -side
                u = math.cos(a) * up + math.sin(a) * side
                c = self.surface(p0 + 3.0 * u, p0)
                out.append(dict(n=n, x=x, c=c, rho=skewed(st, *C["reachM"], C["skew"]), w=st.uniform(*C["widthM"]),
                                k=st.uniform(*C["depthM"]), wander=Noise("lt1-holm-tip", "sculpt", "wander", self.id, len(out)), set=name))
        return out

    def place_chips(self):
        """Chips (`chip`): a corner knocked off where it stands out (its faces turn from each other by `minDeg` or more),
        by its kind's `share` (fresh: a plucked face meets there; worn: weathered faces only, above `above` of the
        height), at most `most`: a planar facet across it, facing the corner's mean normal turned by up to `jitterDeg`,
        sunk `depthM` (skewed small) past the surface, its creases crisp to `soft`; a plane that would run more than
        `reach` times its depth from the corner along any arris is not cut, so it never shaves a face."""
        C = S["chip"]; st = HS.Stream("lt1-holm-tip", "sculpt", "chip", self.id); fs = self.ms.faces
        planes = [(f[0], f[1]) for f in fs]; out = []
        for p, s in MS.corners(planes):
            s = [k for k in s if fs[k][2] != "base"]
            if len(s) < 3 or p[2] < self.sink + 0.08:
                continue
            N = [fs[k][0] for k in s]
            if min(math.degrees(math.acos(np.clip(a @ b, -1, 1))) for ai, a in enumerate(N) for b in N[ai + 1:]) < C["minDeg"]:
                continue
            kind = "fresh" if {fs[k][2] for k in s} & self.fresh else "worn"; K = C[kind]
            if (kind == "worn" and p[2] < K["above"] * self.ms.H) or st.random() >= K["share"] or len(out) >= C["most"]:
                continue
            u = sum(N); u /= np.linalg.norm(u)
            v = np.array([st.normal(), st.normal(), st.normal()]); v -= (v @ u) * u
            u = u + math.tan(math.radians(st.uniform(0, C["jitterDeg"]))) * v / max(np.linalg.norm(v), 1e-9); u /= np.linalg.norm(u)
            q = self.surface(p + 0.3 * u, p - 0.8 * u); dp = skewed(st, *K["depthM"], C["skew"]); o = float(u @ q) - dp
            cut = [c for c, cs in MS.corners(planes + [(u, o)]) if len(planes) in cs]
            if max(np.linalg.norm(c - p) for c in cut) > C["reach"] * dp:
                continue
            out.append(dict(u=u, o=o, q=q, soft=K["soft"], kind=kind))
        return out

    # ------------------------------------------------------------ the field
    def field(self, P, fine=True, grad=False):
        """The sculpted form's signed distance at P (negative in the rock), and with grad its shading normal; not fine,
        the form a game mesh follows: its domed planes, rounds and chips, without the marks the bake carries (the
        breaks, nicks, borders, the notch and cracks: concave, so the high-poly's alone)."""
        d, g = self.form(P)
        for c in self.chips:
            v = P @ c["u"] - c["o"]; h = blend(d, v, c["soft"]); d = smax(d, v, c["soft"]); g = h[:, None] * c["u"] + (1 - h)[:, None] * g
        if fine:
            for R in self.regions:
                ix = np.nonzero(((P - R["c"]) ** 2).sum(1) < R["r"] ** 2)[0]
                if not len(ix):
                    continue
                Q = P[ix]; Nn = np.array([n for n, o in R["planes"]]); V = Q @ Nn.T - np.array([o for n, o in R["planes"]])
                v, gv = V[:, 0], np.tile(Nn[0], (len(ix), 1))
                for p in range(1, len(Nn)):  # its own creases rounded as its edge (a smooth minimum): a riser too
                    hb = blend(-v, -V[:, p], R["soft"]); v = -smax(-v, -V[:, p], R["soft"])  # small to mesh melts in
                    gv = hb[:, None] * Nn[p] + (1 - hb)[:, None] * gv
                h = blend(d[ix], v, R["soft"]); d[ix] = smax(d[ix], v, R["soft"])
                g[ix] = h[:, None] * gv + (1 - h)[:, None] * g[ix]
            Ck = S["crack"]; L, amp = Ck["wander"]
            for c in self.cracks:
                # a clean V whose trace is the joint's plane on the surface, wandering a little, cut square into the
                # surface; its width held on the surface, its depth fading out where the plane meets the surface
                # shallower than `steep`; width and depth closing together toward the reach's end
                q = P - c["c"]; r = np.linalg.norm(q - np.outer(q @ c["n"], c["n"]), axis=1); tp = np.clip(1 - (r / c["rho"]) ** 2, 0, 1)
                s = P @ c["n"] - c["x"] - d * (g @ c["n"]) + amp * c["wander"](P / L)
                sn = np.linalg.norm(np.cross(g, c["n"]), axis=1)
                deep = c["k"] * tp * np.clip((sn - Ck["steep"][0]) / (Ck["steep"][1] - Ck["steep"][0]), 0, 1)
                half = 0.5 * c["w"] * tp * sn * np.clip(1 + d / np.maximum(deep, 1e-6), 0, 1)
                d = smax(d, half - np.abs(s) - 0.0005, Ck["soft"])
        if grad:
            return d, g / np.maximum(np.linalg.norm(g, axis=1), 1e-12)[:, None]
        return d

    # ------------------------------------------------------------ meshing
    def mesh(self, mat, vs, fine=True, name=None):
        """The surface by openvdb at vs; each level evaluated only where the coarser one says the surface may be (its
        lookup error at most 1.2 times half a cell's diagonal), the coarsest everywhere. Its normals the field's
        shading normal at each vertex (the planes', blended across the rounds and marks)."""
        lo, hi = self.ms.lo, self.ms.hi; hs = [h for h in S["levels"] if h > 2 * vs] + [vs]; bg = 2 * vs
        E = [1.2 * 0.87 * h for h in hs]; prev = None
        for L, h in enumerate(hs):
            n = (np.ceil((hi - lo) / h).astype(int) + 1); last = L == len(hs) - 1
            band = bg + sum(E[L - 1:len(hs) - 1]) if L else None
            if last:
                grid = vdb.FloatGrid(bg); grid.transform = vdb.createLinearTransform(voxelSize=h)
            else:
                A = np.empty(tuple(n), np.float32)
            X_, Y_ = np.meshgrid(lo[0] + np.arange(n[0]) * h, lo[1] + np.arange(n[1]) * h, indexing="ij")
            step = max(1, int(2e6 // (n[0] * n[1]))); ev = 0
            for k0 in range(0, n[2], step):
                k = np.arange(k0, min(n[2], k0 + step)); sh = (n[0], n[1], len(k))
                P = np.stack([np.repeat(X_[..., None], len(k), 2), np.repeat(Y_[..., None], len(k), 2),
                              np.broadcast_to(lo[2] + k * h, sh)], -1).reshape(-1, 3)
                if prev is None:
                    a = self.field(P, fine); ev += len(P)
                else:
                    ph, PA = prev; i = np.clip(np.rint((P - lo) / ph).astype(int), 0, np.array(PA.shape) - 1)
                    c = PA[i[:, 0], i[:, 1], i[:, 2]]; a = np.where(c < 0, -1.0, 1.0) * (bg if last else 1.0)
                    m = np.abs(c) < band; a[m] = self.field(P[m], fine); ev += int(m.sum())
                if last:
                    grid.copyFromArray(np.clip(a, -bg, bg).astype(np.float32).reshape(sh), ijk=(0, 0, k0), tolerance=0)
                else:
                    A[:, :, k0:k0 + len(k)] = a.reshape(sh)
            print(f"[sculpt] level {h} m: {ev} evaluations", flush=True)
            if not last:
                prev = (h, A)
        pts, tris, quads = grid.convertToPolygons(isovalue=0.0, adaptivity=0.0)
        V = np.asarray(pts, float) + lo; T = np.asarray(tris, np.int64).reshape(-1, 3); Q = np.asarray(quads, np.int64).reshape(-1, 4)
        F = np.concatenate([T, Q[:, [0, 1, 2]], Q[:, [0, 2, 3]]])
        a, b, c = V[F[:, 0]], V[F[:, 1]], V[F[:, 2]]
        if np.einsum("ij,ij->i", a, np.cross(b, c)).sum() < 0:  # outward
            F = F[:, ::-1]
        name = name or f"high_{self.id}"; me = bpy.data.meshes.new(name)
        me.vertices.add(len(V)); me.vertices.foreach_set("co", V.astype(np.float32).ravel())
        me.loops.add(3 * len(F)); me.loops.foreach_set("vertex_index", F.astype(np.int32).ravel())
        me.polygons.add(len(F)); me.polygons.foreach_set("loop_start", np.arange(0, 3 * len(F), 3, dtype=np.int32))
        me.update(); me.validate()
        if fine:
            self.refine(me)
        me.shade_smooth(); me.materials.append(mat)
        Vm = np.empty(len(me.vertices) * 3); me.vertices.foreach_get("co", Vm); Vm = Vm.reshape(-1, 3)
        Gn = np.concatenate([self.field(Vm[i:i + 500000], fine, grad=True)[1] for i in range(0, len(Vm), 500000)])
        me.normals_split_custom_set_from_vertices(Gn.tolist())
        ob = bpy.data.objects.new(name, me); bpy.context.scene.collection.objects.link(ob)
        return ob

    def refine(self, me):
        """Finer than the voxels along a crisp mark's creases (`refine`): the faces within a mark of `marks`' reach where
        two of its surfaces meet (two of the form and the marks' planes within `nearM`), each edge cut `cuts` times and
        laid back onto the surface (`steps` along each vertex's own normal, each no more than `stepCapM`), so a crease runs as a line, not a voxel
        staircase."""
        import bmesh
        Rf = S["refine"]; Rs = [R for R in self.regions if R["why"] in Rf["marks"]]
        if not Rs:
            return
        V = np.empty(len(me.vertices) * 3); me.vertices.foreach_get("co", V); V = V.reshape(-1, 3)
        F = np.empty(len(me.polygons) * 3, np.int64); me.polygons.foreach_get("vertices", F); C = V[F.reshape(-1, 3)].mean(1)
        inn = np.zeros(len(C), bool)
        for R in Rs:
            inn |= ((C - R["c"]) ** 2).sum(1) < R["r"] ** 2
        ix = np.nonzero(inn)[0]; Ci = C[ix]; fd = np.abs(self.form(Ci)[0]) < Rf["nearM"]; near = np.zeros(len(ix), bool)
        for R in Rs:  # on a mark's own surface, where it meets the form or two of its planes meet
            m = ((Ci - R["c"]) ** 2).sum(1) < R["r"] ** 2
            Nn = np.array([n for n, o in R["planes"]]); V = Ci @ Nn.T - np.array([o for n, o in R["planes"]])
            near |= m & (np.abs(V.min(1)) < Rf["nearM"]) & (fd | ((V < Rf["nearM"]).sum(1) >= 2))
        sel = np.zeros(len(C), bool); sel[ix[near]] = True
        bm = bmesh.new(); bm.from_mesh(me); bm.faces.ensure_lookup_table()
        edges = list({e for i in np.nonzero(sel)[0] for e in bm.faces[int(i)].edges})
        bmesh.ops.subdivide_edges(bm, edges=edges, cuts=Rf["cuts"], use_grid_fill=True)
        bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if len(f.verts) > 3])
        bm.to_mesh(me); bm.free(); me.update()
        V = np.empty(len(me.vertices) * 3); me.vertices.foreach_get("co", V); V = V.reshape(-1, 3)
        m = np.zeros(len(V), bool)
        for R in Rs:
            m |= ((V - R["c"]) ** 2).sum(1) < R["r"] ** 2
        Nv = np.empty(len(me.vertices) * 3); me.vertices.foreach_get("normal", Nv); Nv = Nv.reshape(-1, 3)[m]
        P = V[m]  # each laid back along its own normal, never sliding along the surface: at a concave crease the
        for _ in range(Rf["steps"]):  # field's normal would pull a vertex onto the crease and fold its triangles
            d, g = self.field(P, True, grad=True); c = np.maximum(np.einsum("ij,ij->i", g, Nv), 0.3)
            P = P - np.clip(d / c, -Rf["stepCapM"], Rf["stepCapM"])[:, None] * Nv
        F = np.empty(len(me.polygons) * 3, np.int64); me.polygons.foreach_get("vertices", F); F = F.reshape(-1, 3)
        U = V.copy(); U[m] = P; tn = lambda X: np.cross(X[F[:, 1]] - X[F[:, 0]], X[F[:, 2]] - X[F[:, 0]])  # noqa: E731
        n0 = tn(V)
        for _ in range(4):  # a vertex whose move turns a triangle over stays where the cut left it
            back = np.einsum("ij,ij->i", n0, tn(U)) <= 0.0
            if not back.any():
                break
            ix_ = np.unique(F[back]); U[ix_] = V[ix_]
        print(f"[sculpt] refine: {int((np.einsum('ij,ij->i', n0, tn(U)) <= 0.0).sum())} triangles turned over", flush=True)
        me.vertices.foreach_set("co", U.ravel()); me.update()
        print(f"[sculpt] refined {int(sel.sum())} faces near {len(Rs)} marks: {len(me.polygons)} faces", flush=True)

    def arrises(self):
        """The designed planes' arrises out of the turf (both ends above `sinkM`), shortest first: [(metres, keys)]."""
        fs = self.ms.faces; cs = MS.corners([(f[0], f[1]) for f in fs]); turf = self.sink; out = []
        for a in range(len(cs)):
            for b in range(a + 1, len(cs)):
                sh = [k for k in set(cs[a][1]) & set(cs[b][1]) if fs[k][2] != "base"]
                if len(sh) >= 2 and min(cs[a][0][2], cs[b][0][2]) > turf:
                    out.append((round(float(np.linalg.norm(cs[a][0] - cs[b][0])), 3), sorted(fs[k][3] for k in sh)))
        return sorted(out)

    def bows(self):
        """Each arris out of the turf's bow: its domed line's greatest rise off its chord, a share of its length."""
        out = []
        for p in self.pairs:
            if max(p["P0"][2], p["P1"][2]) < self.sink:
                continue
            ss_ = np.linspace(0, 1, 21); Q = np.array([self.arris_at(p, s) for s in ss_]); ch = Q[-1] - Q[0]; L = float(np.linalg.norm(ch))
            off = Q - Q[0] - np.outer((Q - Q[0]) @ ch / L, ch / L)
            out.append((self.ms.faces[p["i"]][3], self.ms.faces[p["j"]][3], "fresh" if p["fresh"] else "old", round(p["ln"], 2),
                        round(float(np.linalg.norm(off, axis=1).max()) / L, 4)))
        return out

    def spikes(self):
        f = lambda P: (self.field(P),)  # noqa: E731
        return MS.Mass.spikes(SimpleNamespace(form=f, lattice=self.ms.lattice, chunks=self.ms.chunks))


def main():
    os.makedirs(OUT, exist_ok=True)
    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o)
    MS.M["judge"] = {**MS.M["judge"], **S["judge"]}; J = MS.M["judge"]
    rock = MS.clay("rock", [J["rock"]] * 3, J["rough"]); sun, cam = MS.judge_scene()
    only = arg("--masses", "boulder"); views = arg("--views", ",".join(S["views"])).split(",")
    vs = float(arg("--voxel", S["voxelM"])); info = {}
    for X in MS.M["masses"]:
        if X["id"] not in only.split(","):
            continue
        sc = Sculpt(X); least = sc.arrises()[:3]
        if least[0][0] < S["leastArrisM"]:
            raise SystemExit(f"[sculpt] {sc.id}: a pinch, the arris {least[0][1]} is {least[0][0]} m (leastArrisM {S['leastArrisM']})")
        bw = sc.bows()
        for b in bw:
            print("[sculpt] bow", *b, flush=True)
        for r in sc.regions:
            print("[sculpt] mark", r["why"], r["at"], r["lenM"], r["depthM"], r.get("riser", ""), flush=True)
        ob = sc.mesh(rock, vs); ob.location.z = -sc.sink
        Tr = sc.trace
        info[sc.id] = {"tris": len(ob.data.polygons), "leastArris": least, "bows": bw,
                       "trace": None if Tr is None else {"A": Tr["keyA"], "U": Tr["keyU"], "x": round(Tr["x"], 4), "mouth": Tr["mouth"].round(3).tolist()},
                       "marks": {w: sum(r["why"] == w for r in sc.regions) for w in ("notch", "corner", "fresh", "foot", "nick", "border")},
                       "regions": [{k: r[k] for k in ("why", "at", "lenM", "depthM")} for r in sc.regions], **sc.spikes()}
        print("[sculpt]", sc.id, json.dumps({k: v for k, v in info[sc.id].items() if k not in ("regions", "bows")}), flush=True)
        for v in views:
            off, fit = S["views"][v]; J["fit"] = fit
            MS.aim(sun, cam, sc.ms, X["front"] + off)
            bpy.context.scene.render.filepath = os.path.join(OUT, f"{sc.id}-{v}.png"); bpy.ops.render.render(write_still=True)
        gen = os.path.abspath(arg("--gen", os.path.join(MS.ROOT, "cache", "rock", "kit", "gen", sc.id))); os.makedirs(gen, exist_ok=True)
        ob.location.z = 0.0; bpy.data.libraries.write(os.path.join(gen, "high.blend"), {ob}, fake_user=True)
        ob.hide_render = True
    json.dump(info, open(os.path.join(OUT, "sculpt.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
