"""R2b's stones in the gully: R1's laying (blender/generators/masonry.py, made from its facts at the pinned commit,
through stones.Data) built with R2b's parts and set in the street, each stone rigid (moved and turned, never bent).

- each face stone, through stone and head, on each face it shows: split.py's wall stone in its cell, set as the
  working sets it (r2b_wall.stone); a head at a wall's end shows on the end too, and where the top steps up the
  upper run's end is closed by end stones, a course or two;
- each coping run and topstone: slabstep.py's coping, laid as the working lays a run (r2b_wall.coping);
- each step, rest and landing slab: slabstep.py's step, worn and settled (r2b_steps.piece);
- behind each face, the joints' soil (kind 6).

A battered face over a climbing foot is a plane whose line at any height runs in a little uphill, so each stone is
turned about the vertical to lie in it. Every stone's seed (its key, from which its material seed on UV1.y is drawn)
is the world seed and its stable id, through hashing.py.

Written as two R2B2 triangle soups in Unity's frame for LT1R2b.Gully: <out>-walls.bin (the rubble walls) and
<out>-slabs.bin (the slate: steps and copings). Fails on any piece over its part's L0 budget.

    $PY tools/r2b_gully.py cache/r2b/gully [--year 1989] [--wear 8]
"""

import argparse
import hashlib
import json
import math
import os
import struct
import sys
import types

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "blender", "parts", "stone", "slate"))
sys.path.insert(0, os.path.join(ROOT, "blender", "resolver"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import hashing as HS  # noqa: E402
import stones as ST  # noqa: E402  (stones.Data: R1's laying and facts at the pinned commit)
import r2b_steps  # noqa: E402
import r2b_wall  # noqa: E402

PACK = os.path.join(ROOT, "packs", "stavanger-1989")
MM = 0.001
Z = np.array([0.0, 0.0, 1.0])


def _defn(part):
    d = json.load(open(os.path.join(PACK, "parts", "stone", f"{part}.json")))
    return {k: v["value"] for k, v in d["params"].items()}, d["levels"]["l0"]["triangles"]


def _yaw(P, psi):
    """Turned about the local vertical through x = 0, w = 0 (x along, y up, w out)."""
    c, s = math.cos(psi), math.sin(psi)
    return np.column_stack([P[:, 0] * c - P[:, 2] * s, P[:, 1], P[:, 0] * s + P[:, 2] * c])


def _foot(A, h, F):
    """A piece's corners near the ground (h above it): the sky they see closed by the ground and the soil at it, their
    skin damp and mossed from the splash, each fading out by the foot's reach (the working's foot)."""
    t = np.clip(h / (F["reachMm"] * MM), 0.0, 1.0)
    c = F["sky"] + (1.0 - F["sky"]) * t * t * (3.0 - 2.0 * t)
    for i in np.nonzero(t < 1.0)[0]:
        A[3][i] = (A[3][i][0] * c[i], A[3][i][1] * c[i])
        A[5][i] = (max(A[5][i][0], F["moss"] * (1.0 - t[i]) ** 2), max(A[5][i][1], F["water"] * (1.0 - t[i])))


class Soup:
    """Triangles in the street's frame (x east, y north, z up), each its own three corners, outward by the right hand,
    with their normals and the eight UV pairs (Stone.shader's contract)."""

    def __init__(self, F):
        self.P, self.N, self.A = [], [], {k: [] for k in range(8)}
        self.F = F

    def add(self, P, N, A, O, U, V, W, ground=None):
        """Corners in a local frame (x, y, w) put at O with axes U, V, W; mirrored frames have their winding turned.
        ground: the ground's height under each corner, where the piece stands in it (its foot)."""
        M = np.column_stack([U, V, W])
        Pw = P @ M.T + O
        if ground is not None:
            _foot(A, Pw[:, 2] - ground(Pw), self.F)
        Nw = N @ M.T
        order = np.arange(len(P)).reshape(-1, 3)
        if np.linalg.det(M) < 0:
            order = order[:, [0, 2, 1]]
        order = order.reshape(-1)
        self.P.append(Pw[order])
        self.N.append(Nw[order])
        for k in range(8):
            self.A[k] += [A[k][i] for i in order]

    def write(self, path):
        P, N = np.vstack(self.P), np.vstack(self.N)
        # Unity's frame (x, z, y): a mirror, so LT1R2b.Load's turn of the winding sets it right
        U = P[:, [0, 2, 1]].astype(np.float32)
        Nu = N[:, [0, 2, 1]].astype(np.float32)
        with open(path, "wb") as f:
            f.write(struct.pack("<4si", b"R2B2", len(U)))
            f.write(U.tobytes())
            f.write(Nu.tobytes())
            for k in range(8):
                f.write(np.array(self.A[k], dtype=np.float32).tobytes())
        return len(U) // 3, hashlib.sha256(open(path, "rb").read()).hexdigest()[:16]


class Line:
    """A wall line in the street: its flight's foot, uphill and right, its side, its faces' planes (d: the distance
    from the flight's middle line, at s along the flight and z up), smoothed through its stepped footing and top."""

    def __init__(self, ln, w, fl, W):
        self.w = w
        self.a = np.array(fl["a"], float) * MM
        d = (np.array(fl["b"], float) - np.array(fl["a"], float))[:2]
        self.up = np.array([*(d / np.hypot(*d)), 0.0])
        self.right = np.array([self.up[1], -self.up[0], 0.0])
        self.sd = ln["side"]
        self.hw = fl["width"] * MM / 2 + 0.006
        self.b = W["batterPerHeight"][0] / W["batterPerHeight"][1]
        self.T = W["topThickMm"] * MM
        f = w["footing"]["stair"]
        self.fs = np.array([(a + b) / 2 for a, b, z in f]) * MM
        self.fz = np.array([z for a, b, z in f]) * MM
        self.cs = np.array([(c["s"][0] + c["s"][1]) / 2 for c in w["ceiling"]]) * MM
        g = w["footing"]["bank"]
        self.gs = np.array([(a + b) / 2 for a, b, z in g]) * MM
        self.gz = np.array([z for a, b, z in g]) * MM
        self.ct = np.array([c["top"] for c in w["ceiling"]]) * MM

    def zf(self, s):
        return float(np.interp(s, self.fs, self.fz))

    def ground(self, face):
        """The ground at a face's foot under street points: the treads' on the stair face, the bank's on the other."""
        fs, fz = (self.fs, self.fz) if face == "stair" else (self.gs, self.gz)
        return lambda Pw: np.interp((Pw[:, :2] - self.a[:2]) @ self.up[:2], fs, fz)

    def foot(self, face, s):
        """The footing's own height at s (stepped, as laid)."""
        return min((z for p, q, z in self.w["footing"][face] if p * MM <= s <= q * MM), default=-1.0) * MM

    def top(self, s):
        return float(np.interp(s, self.cs, self.ct))

    def d(self, face, s, z):
        if face == "stair":
            return self.hw + (z - self.zf(s)) * self.b
        return self.hw + (self.top(s) - self.zf(s)) * self.b + self.T + (self.top(s) - z) * self.b

    def out(self, face):
        """The face's outward normal in plan: the stair's towards the flight, the bank's away."""
        return (-1.0 if face == "stair" else 1.0) * self.sd * self.right

    def frame(self, face, s, z):
        """A face's frame at (s, z): its origin on the face's plane, x along it (so that x, up, out is right-handed),
        and the turn about the vertical that lays a stone in the plane."""
        n = self.out(face)
        sig = 1.0 if np.dot(np.cross(self.up, Z), n) > 0 else -1.0
        O = self.a + s * self.up + self.sd * self.d(face, s, z) * self.right
        O[2] = z
        e = 1e-3
        # (w = the face's outward distance from O; its slope along x)
        sign = -1.0 if face == "stair" else 1.0
        slope = sign * (self.d(face, s + sig * e, z) - self.d(face, s, z)) / e
        return O, sig * self.up, n, math.atan(slope), sig


class Rake:
    """A wall's top under its copings, as masons set out a ramped wall (research-masonry.md, 1 and 5; the working's
    rake): level on each rest and wherever the laying keeps it level; along a flight, one line set from its runs' bed
    corners, kept leastMm above each, leaving the rest below at a knee level with that rest's coping top, its last run
    easing it onto the rest above's coping top. Under the line each run's top course is brought up to it by a raking
    stone, its bed level, its top cut to the line. segs: the coping's bed (s0, s1, t0, t1); pieces: the coping's straight
    runs (s0, t0, s1, t1, ends, key); wedges: the raking stones (run, s0, s1, h0, h1, key)."""

    def __init__(self, w, W, seed):
        C = w["ceiling"]
        e = W["rake"]["leastMm"] * MM
        cop = [i for i, c in enumerate(C) if c["kind"] == "coping"]
        s0 = {i: C[i]["s"][0] * MM for i in cop}
        s1 = {i: C[i]["s"][1] * MM for i in cop}
        z = {i: C[i]["z"] * MM for i in cop}
        self.key = {i: HS.h(seed, C[i].get("owner") or f"{w['id']}/ceiling-{i}") for i in cop}
        bed = 0.5 * sum(W["copeBedMm"]) * MM
        th = {i: HS.Stream(HS.h(self.key[i], "coping"), "lay").uniform(*W["copeThickMm"]) * MM + bed for i in cop}
        med = float(np.median([s1[i] - s0[i] for i in cop]))
        self.flight = {i: i + 1 in z and z[i + 1] > z[i] + 0.02 and s1[i] - s0[i] < 2.0 * med for i in cop}
        fl = self.flight
        self.segs, self.pieces, self.wedges, knee, head = [], [], [], {}, set()
        self.ends = {}
        for i in cop:
            if not fl[i] or fl.get(i - 1, False):
                continue
            run = [i]
            while fl.get(run[-1] + 1, False):
                run.append(run[-1] + 1)
            k, at = run[-1], run[-1] + 1
            m = (np.polyfit([s0[r] for r in run], [z[r] for r in run], 1)[0] if len(run) > 1
                 else (z[at] - z[i]) / (s0[at] - s0[i]))
            b = max(z[r] + e - m * s0[r] for r in run)
            P = (s0[at], z[at] + th[at])
            head.add(at)
            p = i - 1
            foot = (s0[i], m * s0[i] + b)
            if p == 0 and C[0]["kind"] == "topstone":
                # (a flight from the wall's foot: the rake carried down over the head to the wall's end, a raking stone
                # under it, the end closed to the coping's bed; never a coping's foot hung over a lower head)
                a0, a1, zp = C[0]["s"][0] * MM, C[0]["s"][1] * MM, C[0]["z"] * MM
                foot = (a0, m * a0 + b)
                self.ends[0] = (zp, foot[1])
                ov = W["rake"]["headOverMm"] * MM
                self.wedges.append((0, a0 - ov, a1, foot[1] - m * ov - zp, m * a1 + b - zp,
                                    HS.h(seed, w["id"], "rake-head")))
                self.segs.append((a0, a1, foot[1], m * a1 + b))
            elif p in z and not fl[p]:
                sk = min(max((z[p] + th[p] - b) / m, s0[p] + 0.15), s1[p])
                if sk < s1[p] - 0.01:
                    knee[p] = sk
                    foot = (sk, m * sk + b)
                    self.wedges.append((p, sk, s1[p], foot[1] - z[p], m * s1[p] + b - z[p], HS.h(self.key[p], "knee")))
                    self.segs.append((sk, s1[p], foot[1], m * s1[p] + b))
            knot = (s0[k], m * s0[k] + b)
            sid = HS.h(seed, w["id"], "rake", round(foot[0] / MM))
            if knot[0] - foot[0] > 0.01:
                self.pieces.append((*foot, *knot, ("j" if p in knee else "o") + "j", sid))
                self.segs.append((foot[0], knot[0], foot[1], knot[1]))
            self.pieces.append((*knot, *P, ("j" if knot[0] - foot[0] > 0.01 or p in knee else "o") + "o",
                                HS.h(sid, "ease")))
            self.segs.append((knot[0], P[0], knot[1], P[1]))
            for r in run:
                t = (lambda s: m * s + b) if r != k else (lambda s: knot[1] + (P[1] - knot[1]) * (s - knot[0]) / (P[0] - knot[0]))
                self.wedges.append((r, s0[r], s1[r], t(s0[r]) - z[r], t(s1[r]) - z[r], HS.h(self.key[r], "rake")))
        # the level runs: on their own bed, to their knee if a rake leaves them
        for i in cop:
            if fl[i]:
                continue
            se = knee.get(i, s1[i])
            self.pieces.append((s0[i], z[i], se, z[i], ("j" if i in head else "o") + ("j" if i in knee else "o"),
                                self.key[i]))
            self.segs.append((s0[i], se, z[i], z[i]))
        self.covered = {i for i in cop if fl[i] or i in knee} | set(self.ends)
        self.knees = sorted(knee.values())

    def bed(self, s, default):
        for a, b, t0, t1 in self.segs:
            if a - 1e-6 <= s <= b + 1e-6:
                return t0 + (t1 - t0) * (s - a) / max(b - a, 1e-9)
        return default


def build(a):
    data = ST.Data()
    lay = data.laying()
    facts = data.r1_facts()
    seed = facts["worldSeed"]
    W = data.walling["workings"]["dry-split-1874"]
    # (R1 laid by the working at its pinned commit; what R2b's laying added since comes from the pack as it is)
    now = json.load(open(os.path.join(PACK, "walling.json")))["workings"]["dry-split-1874"]
    W = {**now, **W, "steps": {**now["steps"], **W["steps"]}}
    pw, bw = _defn("wallstone")
    pw["jointHalfMm"] = [W["jointMm"][0] / 2, W["jointMm"][1] / 2]
    pw["bedJointHalfMm"] = [W["bedJointMm"][0] / 2, W["bedJointMm"][1] / 2]
    # (the top course under a coping picked to the line: flat and square on top)
    picked = dict(pw, topSlope=[0.0, 0.0], topStepChance=0.0, knockMm=dict(pw["knockMm"], top=W["pickedKnockMm"]))
    raking = dict(picked, endSlant=W["rake"]["endSlant"])
    FT = W["foot"]
    sink = FT["sinkMm"] * MM
    pc, bc = _defn("coping")
    ps, bs = _defn("step")
    S = W["steps"]
    years = (a.year - W["built"]) / 200.0
    gap = 0.5 * (W["jointMm"][0] + W["jointMm"][1]) * MM
    walls, slabs = Soup(FT), Soup(FT)
    counts = dict(wallstone=[], coping=[], step=[])
    flights = facts["stair"]["flights"]

    def end_stone(L, key, s_end, n, z0, z1, p=picked, ground=None):
        """A stone whose end shows across the wall at s_end, facing n along the line, the wall's thickness wide, plumb."""
        zm = (z0 + z1) / 2
        r = sorted((L.sd * L.d("stair", s_end, zm), L.sd * L.d("bank", s_end, zm)))
        U = np.cross(Z, n)
        U = U if np.dot(np.cross(U, Z), n) > 0 else -U
        rc = (r[0] + r[1]) / 2
        O = L.a + s_end * L.up + rc * L.right
        O[2] = z0
        ux = sorted((np.dot(L.right, U) * (r[0] - rc), np.dot(L.right, U) * (r[1] - rc)))
        cell = ((ux[0], 0.0), (ux[1], 0.0), (ux[1], z1 - z0), (ux[0], z1 - z0))
        A = {k: [] for k in range(8)}
        P, N = r2b_wall.stone(key, cell, p, W, 0.0, years, gap, A)
        walls.add(P, N, A, O, U, Z, n, ground)
        counts["wallstone"].append(len(P) // 3)

    lines, fronts = [], []
    for ln, w in zip(facts["walls"]["lines"], lay["walls"]):
        L = Line(ln, w, flights[ln["flight"]], W)
        R = Rake(w, W, seed)
        s_lo, s_hi = w["s"][0] * MM, w["s"][1] * MM
        lines.append((L, s_lo, s_hi))
        tops = {}
        for st in w["stones"]:
            if st["kind"] not in ("face", "through", "head"):
                continue
            o = np.array(st["outline"], float) * MM
            s0, s1, z0, z1 = o[:, 0].min(), o[:, 0].max(), o[:, 1].min(), o[:, 1].max()
            sc = (s0 + s1) / 2
            zc = min((c["z"] for c in w["ceiling"] if c["s"][0] * MM <= sc <= c["s"][1] * MM), default=1e9) * MM
            p = picked if z1 > zc - 0.005 else pw
            # (the faces each run's top course shows: a stone counts under every run it reaches whose bed it is under)
            for ci, c in enumerate(w["ceiling"]):
                if c["s"][0] * MM < s1 - 0.01 and c["s"][1] * MM > s0 + 0.01 and z1 > c["z"] * MM - 0.005:
                    tops.setdefault(ci, set()).update(st["faces"])
            for face in st["faces"]:
                # (the bottom course set into the ground, its bed hidden: a wall stands in it, never on it)
                zb = z0 - sink if abs(z0 - L.foot(face, sc)) < 0.005 else z0
                O, U, n, psi, sig = L.frame(face, sc, zb)
                x0, x1 = sorted((sig * (s0 - sc), sig * (s1 - sc)))
                cell = ((x0, 0.0), (x1, 0.0), (x1, z1 - zb), (x0, z1 - zb))
                A = {k: [] for k in range(8)}
                P, N = r2b_wall.stone(HS.h(seed, st["id"], face), cell, p, W, L.b, years, gap, A)
                walls.add(_yaw(P, psi), _yaw(N, psi), A, O, U, Z, n, L.ground(face))
                counts["wallstone"].append(len(P) // 3)
            # a head at the wall's end shows on the end too, the wall's thickness wide, plumb
            for end, s_end, n in (("lo", s_lo, -L.up), ("hi", s_hi, L.up)):
                if st["kind"] != "head" or abs((s0 if end == "lo" else s1) - s_end) > 1e-6:
                    continue
                street = abs(z0 - L.foot("stair", s_end)) < 0.005
                end_stone(L, HS.h(seed, st["id"], "end"), s_end, n, z0 - sink if street else z0, z1,
                          picked if z1 > zc - 0.005 else pw, L.ground("stair") if street else None)
        # where the top steps up, the upper run's end shows below its coping: closed by end stones, a course or two
        for ci, (c, c2) in enumerate(zip(w["ceiling"][:-1], w["ceiling"][1:])):
            if ci in R.covered:
                continue
            lo, hi = c["top"] * MM, c2["z"] * MM
            if abs(hi - lo) < 0.02:
                continue
            n = -L.up if hi > lo else L.up
            lo, hi = (lo, hi) if hi > lo else (c2["top"] * MM, c["z"] * MM)
            rows = max(1, int(math.ceil((hi - lo) / 0.28)))
            for r in range(rows):
                end_stone(L, HS.h(seed, w["id"], "step", c["s"][1], r), c["s"][1] * MM,
                          n, lo + (hi - lo) * r / rows, lo + (hi - lo) * (r + 1) / rows)
        # the raking stones: on each face the run's top course shows, a level bed, the top cut to the rake
        for r, sa, sb, h0, h1, key in R.wedges:
            zb, sc = w["ceiling"][r]["z"] * MM, (sa + sb) / 2
            for face in sorted(tops.get(r, {"stair"})):
                O, U, n, psi, sig = L.frame(face, sc, zb)
                x0, x1 = sorted((sig * (sa - sc), sig * (sb - sc)))
                ha, hb = (h0, h1) if sig > 0 else (h1, h0)
                A = {k: [] for k in range(8)}
                P, N = r2b_wall.stone(HS.h(key, face), ((x0, 0.0), (x1, 0.0), (x1, hb), (x0, ha)), raking, W, L.b,
                                      years, gap, A)
                walls.add(_yaw(P, psi), _yaw(N, psi), A, O, U, Z, n)
                counts["wallstone"].append(len(P) // 3)
        # the copings along the top, each straight run laid on its bed from the stair face's top, the rake's turned
        # to it (rigid: each slab only moved and turned)
        for sa, ta, sb, tb, ends, key in R.pieces:
            def face(s, t):
                q = L.a + s * L.up + L.sd * L.d("stair", s, t) * L.right
                q[2] = t
                return q
            sig = L.frame("stair", sa, ta)[4]
            A0, A1 = (face(sa, ta), face(sb, tb)) if sig > 0 else (face(sb, tb), face(sa, ta))
            U = A1 - A0
            run = types.SimpleNamespace(seed=key, length=float(np.linalg.norm(U)), height=0.0,
                                        ends=ends if sig > 0 else ends[::-1])
            U = U / run.length
            n = L.out("stair") - np.dot(L.out("stair"), U) * U
            n = n / np.linalg.norm(n)
            A = {k: [] for k in range(8)}
            Ps, Ns = [], []
            cnt, _ = r2b_wall.coping(run, W, L.b, years, Ps, Ns, A)
            slabs.add(np.vstack(Ps), np.vstack(Ns), A, A0, U, np.cross(n, U), n)
            counts["coping"] += cnt
        for i, (zp, zt) in R.ends.items():
            end_stone(L, HS.h(seed, w["id"], "rake-end"), s_lo, -L.up, zp, zt)
        for i, c in enumerate(w["ceiling"]):
            if c["kind"] == "coping" or i in R.ends:
                continue
            c0, c1 = c["s"][0] * MM, c["s"][1] * MM
            zb = c["z"] * MM
            # (the run's x from 0 at its start: its s end where the face's x runs from)
            O, U, n, psi, sig = L.frame("stair", c0, zb)
            if sig < 0:
                O, U, n, psi, sig = L.frame("stair", c1, zb)
            run = types.SimpleNamespace(seed=HS.h(seed, c.get("owner") or f"{w['id']}/ceiling-{i}"), length=c1 - c0,
                                        height=0.0)
            Wc = dict(W, copeThickMm=[c["top"] - c["z"]] * 2, copeVaryMm=0.0)
            A = {k: [] for k in range(8)}
            Ps, Ns = [], []
            cnt, _ = r2b_wall.coping(run, Wc, L.b, years, Ps, Ns, A)
            slabs.add(_yaw(np.vstack(Ps), psi), _yaw(np.vstack(Ns), psi), A, O, U, Z, n)
            counts["coping"] += cnt
        # the joints' soil behind each face, a column a quarter metre wide from its footing to its top's bed, broken
        # where the footing or the top steps (else a column stands up out of the lower run's end)
        for face in ("stair", "bank"):
            foot = w["footing"][face]
            cuts = [s_lo + k * 0.25 for k in range(int(math.ceil((s_hi - s_lo) / 0.25)))] + [s_hi]
            cuts += [v * MM for c in w["ceiling"] for v in c["s"]] + [v * MM for p, q, z in foot for v in (p, q)]
            cuts += R.knees
            cuts = sorted(v for v in set(cuts) if s_lo <= v <= s_hi)
            for sa, sb in zip(cuts[:-1], cuts[1:]):
                if sb - sa < 0.005:
                    continue
                sm = (sa + sb) / 2
                zl = min((z for p, q, z in foot if p * MM <= sm <= q * MM), default=None)
                zt = min((c["z"] for c in w["ceiling"] if c["s"][0] * MM <= sm <= c["s"][1] * MM), default=None)
                if zl is None or zt is None:
                    continue
                zl = zl * MM - 0.05
                za, zb = (R.bed(v, zt * MM) + 0.02 for v in (sa + 1e-4, sb - 1e-4))
                back = 0.045 * (1.0 if face == "stair" else -1.0)

                def at(s, z):
                    q = L.a + s * L.up + L.sd * (L.d(face, s, z) + back) * L.right
                    q[2] = z
                    return q
                Q = [at(sa, zl), at(sb, zl), at(sb, zb), at(sa, za)]
                n = L.out(face)
                T = []
                for t in ((Q[0], Q[1], Q[2]), (Q[0], Q[2], Q[3])):
                    t = np.array(t)
                    if np.dot(np.cross(t[1] - t[0], t[2] - t[0]), n) < 0:
                        t = t[[0, 2, 1]]
                    T.append(t)
                F = np.vstack(T)
                A = {0: [(np.dot(q, L.up), q[2]) for q in F], 1: [(years, 0.5)] * 6, 2: [(6.0, 0.0)] * 6,
                     3: [(0.2, 0.1)] * 6, 4: [(0.0, years)] * 6, 5: [(0.6, 0.0)] * 6, 6: [(1.0, 1.0)] * 6,
                     7: [(1.0, 7.0)] * 6}
                walls.add(F, np.tile(n, (6, 1)), A, np.zeros(3), np.array([1.0, 0, 0]), np.array([0, 1.0, 0]), Z)

    # the steps, rests and landings: each slab worn where the walking line keeps, and settled
    for fl, f in zip(lay["steps"], flights):
        a0 = np.array([f["a"][0], f["a"][1], 0.0]) * MM     # (a slab's corners are at their own heights)
        d = (np.array(f["b"], float) - np.array(f["a"], float))[:2]
        up = np.array([*(d / np.hypot(*d)), 0.0])
        right = np.array([up[1], -up[0], 0.0])
        width = f["width"] * MM
        xw = width * S["walkLineShare"]
        half = S["walkHalfMm"] * MM

        def walk(x):
            return math.exp(-((x - xw) / half) ** 2)

        def feet(x):
            return math.exp(-((x - xw) / (S["feetHalfMm"] * MM)) ** 2)
        steps = {s["id"]: s for s in fl["steps"]}
        for s in fl["steps"]:
            if "y" not in s:
                s["y"] = [s["rows"][0]["y"][0], s["rows"][-1]["y"][1]]     # (a turn's landing: its rows')
        y0s = sorted(s["y"][0] for s in fl["steps"])
        # (the flight's foot on the ground: its first step set into it, as the walls' bottom course is)
        street = f["a"][2] * MM
        first = min(fl["steps"], key=lambda s: s["y"][0])
        grounded = abs(first["z"][0] * MM - street) < 0.005
        if grounded:
            fronts.append((a0, right, up, first["y"][0] * MM, street, f["width"] * MM / 2))
        for st in fl["stones"]:
            o = np.array(st["outline"], float) * MM
            x0, x1, y0, y1 = o[:, 0].min(), o[:, 0].max(), o[:, 1].min(), o[:, 1].max()
            sp = steps[st["step"]]
            top = sp["z"][1] * MM
            nxt = [y for y in y0s if y > sp["y"][0]]
            going = (nxt[0] - sp["y"][0]) * MM if nxt else y1 - y0
            key = HS.h(seed, st["id"])
            rng = HS.Stream(key, "cut")
            rise = (sp["z"][1] - sp["z"][0]) * MM if st["kind"] == "step" else 0.165
            H = min(rise, 0.2) + rng.uniform(-1.0, 1.0) * S["thickMm"] * MM
            foot = grounded and sp is first
            H += sink if foot else 0.0
            # (an end in the wall is unseen: drawn as a joint's, near square)
            ends = ("joint", "joint")
            A = {k: [] for k in range(8)}
            P, N = r2b_steps.piece(key, x0 + width / 2, x1 - x0, H, y1 - y0, going, y0, top - H, ends, ps, S, walk,
                                   a.wear, years, A, feet)
            P = P - np.array([width / 2, 0.0, 0.0])
            slabs.add(P, N, A, a0, right, Z, up, (lambda Pw: np.full(len(Pw), street)) if foot else None)
            counts["step"].append(len(P) // 3)
    # the soil against each foot on the ground, sloping from the stone into it: its bedding
    sk = FT["skirtMm"] * MM

    def skirt(Q):
        T = []
        for tri in ((Q[0], Q[1], Q[2]), (Q[0], Q[2], Q[3])):
            tri = np.array(tri)
            if np.cross(tri[1] - tri[0], tri[2] - tri[0])[2] < 0:
                tri = tri[[0, 2, 1]]
            T.append(tri)
        P = np.vstack(T)
        N = np.repeat([np.cross(q[1] - q[0], q[2] - q[0]) / np.linalg.norm(np.cross(q[1] - q[0], q[2] - q[0]))
                       for q in T], 3, axis=0)
        A = {0: [(q[0], q[1]) for q in P], 1: [(years, 0.5)] * 6, 2: [(6.0, 0.0)] * 6, 3: [(0.35, 0.1)] * 6,
             4: [(0.0, years)] * 6, 5: [(FT["moss"], FT["water"])] * 6, 6: [(1.0, 1.0)] * 6, 7: [(1.0, 7.0)] * 6}
        walls.add(P, N, A, np.zeros(3), np.array([1.0, 0, 0]), np.array([0, 1.0, 0]), Z)

    for L, s_lo, s_hi in lines:
        street = L.a[2]

        def at(s, dd, z, L=L):
            q = L.a + s * L.up + L.sd * dd * L.right
            q[2] = z
            return q
        for face, sgn in (("bank", 1.0), ("stair", -1.0)):
            g = L.ground(face)
            for k in range(int(math.ceil((s_hi - s_lo) / 0.25))):
                sa, sb = s_lo + k * 0.25, min(s_hi, s_lo + (k + 1) * 0.25)
                # (the stair face meets the ground only before the flight's foot: elsewhere it stands on the treads)
                if face == "stair" and abs(L.foot("stair", (sa + sb) / 2) - street) > 0.005:
                    continue
                za, zb = (float(g(np.array([L.a + s * L.up]))[0]) for s in (sa, sb))
                da, db = L.d(face, sa, za), L.d(face, sb, zb)
                skirt([at(sa, da, za + 0.03), at(sb, db, zb + 0.03), at(sb, db + sgn * sk, zb - 0.015),
                       at(sa, da + sgn * sk, za - 0.015)])
        if abs(L.foot("stair", s_lo) - street) < 0.005:
            ds, db = L.d("stair", s_lo, street), L.d("bank", s_lo, street)
            skirt([at(s_lo, ds, street + 0.03), at(s_lo, db, street + 0.03), at(s_lo - sk, db, street - 0.015),
                   at(s_lo - sk, ds, street - 0.015)])
    for a0, right, up, y0, street, hw in fronts:
        def at(x, s, z):
            q = a0 + x * right + s * up
            q[2] = z
            return q
        skirt([at(-hw, y0, street + 0.03), at(hw, y0, street + 0.03), at(hw, y0 - sk, street - 0.015),
               at(-hw, y0 - sk, street - 0.015)])
    return walls, slabs, counts, dict(wallstone=bw, coping=bc, step=bs)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--year", type=int, default=1989)
    ap.add_argument("--wear", type=float, default=8.0, help="mm the feet took at the walking line's nosing")
    a = ap.parse_args()
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    walls, slabs, counts, budget = build(a)
    fail = False
    for part, c in counts.items():
        c = np.array(c)
        ok = c.max() <= budget[part]
        fail = fail or not ok
        print(f"{part}: {len(c)} pieces, {c.min()} to {c.max()} triangles (mean {c.mean():.1f}; L0's budget "
              f"{budget[part]}: {'pass' if ok else 'FAIL'}), {c.sum()} in all")
    kw = json.load(open(os.path.join(ROOT, "kinds", "wall.json")))["levels"]["l0"]["triangles"]
    ks = json.load(open(os.path.join(ROOT, "kinds", "stair.json")))["levels"]["l0"]["triangles"]
    tw = sum(counts["wallstone"]) + sum(counts["coping"])
    print(f"the walls' stones and copings: {tw} triangles (the wall kind's L0 {kw}: {'pass' if tw <= kw else 'FAIL'}); "
          f"the steps: {sum(counts['step'])} (the stair kind's L0 {ks}: {'pass' if sum(counts['step']) <= ks else 'FAIL'})")
    fail = fail or tw > kw or sum(counts["step"]) > ks
    for name, soup in (("walls", walls), ("slabs", slabs)):
        n, h = soup.write(f"{a.out}-{name}.bin")
        print(f"{a.out}-{name}.bin: {n} triangles, sha256 {h}")
    if fail:
        sys.exit(1)


if __name__ == "__main__":
    main()
