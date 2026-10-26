"""R2b's look loop: a panel of dry wall laid from the pack's walling (packs/stavanger-1989/walling.json, the
dry-split-1874 working) with the split wall stone (blender/parts/stone/slate/split.py, its params the definition's),
written as a triangle soup for LT1R2b.cs to draw (positions in Unity's frame: x along, y up, z into the wall; then
UV0 to UV7 as Stone.shader's contract has them).

    python3 tools/r2b_wall.py OUT.bin [--length 8] [--height 1.8] [--seed 1989] [--coping]

--coping lays a run of coping slabs on its top (slabstep.py's coping, its params the coping's definition), a standing
wall's: the run's ends open.
"""

import argparse
import json
import math
import os
import struct
import sys

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "blender", "parts", "stone", "slate"))
sys.path.insert(0, os.path.join(ROOT, "blender", "resolver"))
import hashing as HS  # noqa: E402
import slabstep  # noqa: E402
import split  # noqa: E402

PACK = os.path.join(ROOT, "packs", "stavanger-1989")
MM = 0.001


def load():
    walling = json.load(open(os.path.join(PACK, "walling.json")))["workings"]["dry-split-1874"]
    defn = json.load(open(os.path.join(PACK, "parts", "stone", "wallstone.json")))
    p = {k: v["value"] for k, v in defn["params"].items()}
    p["jointHalfMm"] = [walling["jointMm"][0] / 2, walling["jointMm"][1] / 2]
    return walling, p


def lay(seed, W, length, height, level=False):
    """Random coursed, as a mason builds it: always on the lowest place along the wall's top so far, a stone as long
    as the place allows, its top brought level with a neighbour's where it nearly is (so courses form and break), no
    end over a joint below it; a slot too short for a stone filled with flat pieces to its lower neighbour. Returns
    the cells (rectangles: bed left, bed right, top right, top left). Level (under a coping): the top course
    picked to the height, and where a stone falls short, brought up to it with flat pinnings, where deep enough."""
    rng = HS.Stream(seed, "r2b-panel")
    ph = W["stonePerHeight"]
    p0, p1 = W["courseDrawPower"]
    snap = W["snapMm"] * MM
    bond = W["bondLeastMm"] * MM
    short = W["shortMm"] * MM
    least = W["courseMm"][0] * MM * 0.5
    # the top so far: segments [u0, u1, top, the joints below that top inside the segment]
    sky = [[0.0, length, 0.0, []]]
    cells = []
    while True:
        i = min(range(len(sky)), key=lambda k: (sky[k][2], sky[k][0]))
        u0, u1, base, joints = sky[i]
        if base > height - least:
            break
        w = u1 - u0
        left = sky[i - 1][2] if i > 0 else None
        right = sky[i + 1][2] if i + 1 < len(sky) else None
        lo, hi = (W["foundationMm"] if base < 1e-6 else W["courseMm"])
        h = (lo + (hi - lo) * rng.random() ** (p0 + (p1 - p0) * base / height)) * MM
        for nb in (left, right):
            if nb is not None and abs(base + h - nb) < snap and nb - base >= least:
                h = nb - base
                break
        if w < max(short, ph[0] * h):
            # a slot: flat pieces up to the lower neighbour, as long as the slot
            tops = [t for t in (left, right) if t is not None]
            h = min(min(tops) - base, max(least, w / ph[0])) if tops else h
        if height - base - h < least:
            h = min(h, height - base)
            if level:
                # (under a coping the top course is picked to the line; now and then one falls short, and is pinned)
                h = height - base
                if rng.random() < W["topShortChance"]:
                    h -= min(rng.uniform(*W["topShortMm"]) * MM, 0.5 * h)
        lmin = max(W["stoneMm"][0] * MM, ph[0] * h, short)
        lmax = min(W["stoneMm"][1] * MM, ph[1] * h)
        l = math.exp(rng.uniform(math.log(min(lmin, lmax)), math.log(max(lmin, lmax))))
        if l >= w or w - l < max(short, lmin * 0.8):
            l = w
        else:
            for _ in range(4):
                near = [j for j in joints if abs(j - (u0 + l)) < bond]
                if not near:
                    break
                l = near[0] + bond - u0
            if l >= w or w - l < max(short, lmin * 0.8):
                l = w
        cells.append(((u0, base), (u0 + l, base), (u0 + l, base + h), (u0, base + h)))
        # the top raised over the stone; the rest of the segment keeps its own joints
        seg = [[u0, u0 + l, base + h, []]]
        if l < w:
            seg.append([u0 + l, u1, base, [j for j in joints if j > u0 + l]])
        sky[i:i + 1] = seg
        # level neighbours run together, their meeting a joint below their top
        merged = [sky[0]]
        for sgm in sky[1:]:
            if abs(sgm[2] - merged[-1][2]) < 1e-6:
                merged[-1] = [merged[-1][0], sgm[1], sgm[2], merged[-1][3] + [sgm[0]] + sgm[3]]
            else:
                merged.append(sgm)
        sky = merged
    if level:
        for u0, u1, base, _ in sky:
            if height - base < W["pinLeastMm"] * MM:
                continue
            # (wedged in where the coping rocked, short voids between them; each a stack of thin pieces of varied
            # thickness, a little short of the top)
            u = u0 + rng.uniform(*W["pinGapMm"]) * MM
            while u1 - u > W["pinLengthMm"][0] * MM:
                l = min(rng.uniform(*W["pinLengthMm"]) * MM, u1 - u)
                t = height - rng.uniform(0.0, min(W["pinShortMm"] * MM, 0.5 * (height - base)))
                y = base
                while t - y > 1e-6:
                    h = rng.uniform(*W["pinThickMm"]) * MM
                    h = t - y if t - y - h < W["pinThickMm"][0] * MM else h
                    a, b = u + rng.uniform(0.0, 0.15) * l, u + l - rng.uniform(0.0, 0.15) * l
                    cells.append(((a, y), (b, y), (b, y + h), (a, y + h)))
                    y += h
                u += l + rng.uniform(*W["pinGapMm"]) * MM
    return cells


def normals(P, soft):
    """Each corner's normal: its triangle's, or on the soft triangles (the face and its arris) the area-weighted
    mean of the soft triangles meeting at its point."""
    T = P.reshape(-1, 3, 3)
    F = np.cross(T[:, 1] - T[:, 0], T[:, 2] - T[:, 0])
    N = np.repeat(F / np.linalg.norm(F, axis=1)[:, None], 3, axis=0)
    acc = {}
    keys = [tuple(np.round(q, 5)) for q in P]
    for t in np.nonzero(soft)[0]:
        for c in range(3):
            acc[keys[3 * t + c]] = acc.get(keys[3 * t + c], 0) + F[t]
    for t in np.nonzero(soft)[0]:
        for c in range(3):
            m = acc[keys[3 * t + c]]
            N[3 * t + c] = m / np.linalg.norm(m)
    return N


def rigid(P, piv, pitch, yaw, dw):
    """The stone moved and turned as one: pitched about the u axis through its bed's front (positive: its face looks
    up, its top goes back), turned about the v axis through its middle, then set out by dw."""
    d = P - piv
    cp, sp = math.cos(pitch), math.sin(pitch)
    dv = d[:, 1] * cp + d[:, 2] * sp
    dwp = d[:, 2] * cp - d[:, 1] * sp
    cy, sy = math.cos(yaw), math.sin(yaw)
    du = d[:, 0] * cy - dwp * sy
    dww = d[:, 0] * sy + dwp * cy
    return np.column_stack([du, dv, dww + dw]) + piv


def coping(a, W, batter, years, Ps, Ns, A):
    """A run of coping slabs along the wall's top, laid as the working lays them: each as long as the working allows
    and no shorter than its least, a joint between; the run's thickness one, each slab a little off it; its front proud
    of the face under it, the rest of the overhang behind; the run level on the wall's levelled top, each slab on
    its pinnings and sat a little off true. Its corners'
    attributes go on as the stones' do (flat, per triangle). Returns each slab's triangles and L0's budget."""
    defn = json.load(open(os.path.join(PACK, "parts", "stone", "coping.json")))
    p = {k: v["value"] for k, v in defn["params"].items()}
    rng = HS.Stream(HS.h(a.seed, "coping"), "lay")
    run = rng.uniform(*W["copeThickMm"]) * MM
    D = (W["topThickMm"] + W["copeOverMm"]) * MM
    lo, hi, least = (v * MM for v in (*W["copeLengthMm"], W["copeLeastMm"]))
    xs = [0.0]
    while a.length - xs[-1] > hi:
        l = rng.uniform(lo, hi)
        xs.append(xs[-1] + (l if a.length - xs[-1] - l >= least else 0.5 * (a.length - xs[-1])))
    xs.append(a.length)
    face = -a.height * batter
    counts = []
    for i, (x0, x1) in enumerate(zip(xs[:-1], xs[1:])):
        key = HS.h(a.seed, "coping", i)
        st = HS.Stream(key, "set")
        g0 = 0.0 if i == 0 else 0.5 * st.uniform(*W["jointMm"]) * MM
        g1 = 0.0 if i == len(xs) - 2 else 0.5 * st.uniform(*W["jointMm"]) * MM
        ends = ("open" if i == 0 else "joint", "open" if i == len(xs) - 2 else "joint")
        H = run + st.uniform(-1.0, 1.0) * W["copeVaryMm"] * MM
        L = x1 - x0 - g0 - g1
        s = slabstep.coping(key, L, H, D, ends, p)
        # (its frame: z back from the front; the panel's: z out of the wall) its bed on the top, its front proud
        pitch, roll, yaw = (math.radians(st.uniform(-1.0, 1.0) * d) for d in W["copeSetDeg"])
        Pl = s["P"]
        q = Pl - np.array([L / 2, 0.0, D / 2])
        y1 = q[:, 1] * math.cos(pitch) - q[:, 2] * math.sin(pitch)
        z1 = q[:, 1] * math.sin(pitch) + q[:, 2] * math.cos(pitch)
        x2 = q[:, 0] * math.cos(roll) - y1 * math.sin(roll)
        y2 = q[:, 0] * math.sin(roll) + y1 * math.cos(roll)
        x3 = x2 * math.cos(yaw) + z1 * math.sin(yaw)
        z3 = -x2 * math.sin(yaw) + z1 * math.cos(yaw)
        proud = st.uniform(*W["copeProudMm"]) * MM
        bed = a.height + st.uniform(*W["copeBedMm"]) * MM
        P = np.column_stack([x3 + L / 2 + x0 + g0, y2 + bed + abs(math.sin(roll)) * L / 2, face + proud - (z3 + D / 2)])
        # (the mirror in z turns each triangle inward: its corners the other way round)
        P = P.reshape(-1, 3, 3)[:, [0, 2, 1]].reshape(-1, 3)
        sky = s["sky"].reshape(-1, 3)[:, [0, 2, 1]].reshape(-1)
        Ns.append(normals(P, s["soft"]))
        counts.append(len(P) // 3)
        var = st.random()
        ou, ov = st.uniform(0, 8), st.uniform(0, 8)
        for t in range(len(P) // 3):
            a3, b3, c3 = P[3 * t:3 * t + 3]
            nrm = np.cross(b3 - a3, c3 - a3)
            nrm /= np.linalg.norm(nrm)
            k = int(s["kind"][t])
            ax = int(np.argmax(np.abs(nrm)))
            for ci, qq in enumerate((a3, b3, c3)):
                uv0 = (qq[0] + ou, qq[1] + ov) if ax == 2 else ((qq[0] + ou, qq[2] + ov) if ax == 1 else (qq[2] + ou, qq[1] + ov))
                open_ = (0.4 if k == 3 else 1.0) * sky[3 * t + ci]
                A[0].append(uv0)
                A[1].append((years, var))
                A[2].append((k, 0.0))
                A[3].append(((0.5 + 0.5 * nrm[1]) * open_, (0.5 - 0.5 * nrm[1]) * open_))
                A[4].append((0.0, years))
                A[5].append((0.05 if k in (1, 2) else 0.25, 0.0))
                A[6].append((1.0, 1.0))
                A[7].append((1.0, 7.0))
        Ps.append(P)
    return counts, defn["levels"]["l0"]["triangles"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--length", type=float, default=8.0)
    ap.add_argument("--height", type=float, default=1.8)
    ap.add_argument("--seed", default="1989")
    ap.add_argument("--year", type=int, default=1989)
    ap.add_argument("--coping", action="store_true")
    a = ap.parse_args()
    W, p = load()
    batter = W["batterPerHeight"][0] / W["batterPerHeight"][1]
    gap = 0.5 * (W["jointMm"][0] + W["jointMm"][1]) * MM
    cells = lay(HS.h(a.seed, "panel"), W, a.length, a.height, level=a.coping)
    years = (a.year - W["built"]) / 200.0
    Ps, Ns, A = [], [], {k: [] for k in range(8)}
    tri_counts = []
    for i, cell in enumerate(cells):
        key = HS.h(a.seed, "stone", i)
        s = split.wallstone(key, cell, p)
        rng = HS.Stream(key, "set")
        piv = np.array([s["centre"][0], s["bed"], 0.0])
        pitch = math.atan(batter) + math.radians(rng.uniform(*W["setPitchDeg"]))
        yaw = math.radians(rng.uniform(*W["setYawDeg"]))
        dw = -s["bed"] * batter + rng.uniform(*W["setOutMm"]) * MM
        P = rigid(s["P"], piv, pitch, yaw, dw)
        n = len(P)
        Ns.append(normals(P, s["soft"]))
        tri_counts.append(n // 3)
        var = rng.random()
        ou, ov = rng.uniform(0, 8), rng.uniform(0, 8)
        # the corners' attributes, per triangle (flat: each triangle its own three corners)
        for t in range(n // 3):
            a3, b3, c3 = P[3 * t:3 * t + 3]
            nrm = np.cross(b3 - a3, c3 - a3)
            nrm /= np.linalg.norm(nrm)
            k = int(s["kind"][t])
            for ci, q in enumerate((a3, b3, c3)):
                ax = int(np.argmax(np.abs(nrm)))
                uv0 = (q[0] + ou, q[1] + ov) if ax == 2 else ((q[0] + ou, q[2] + ov) if ax == 1 else (q[2] + ou, q[1] + ov))
                # (the sky a corner sees: in its joint, a slit a joint wide, the share a slit lets in at that depth)
                slit = float(s["slit"][3 * t + ci])
                open_ = gap / (gap + 2.0 * slit)
                A[0].append(uv0)
                A[1].append((years, var))
                A[2].append((k, 0.0))
                A[3].append(((0.5 + 0.5 * nrm[1]) * open_, (0.5 - 0.5 * nrm[1]) * open_))
                # (lichen needs light: none deeper in a joint than the sky reaches)
                A[4].append((0.0, years * max(0.0, 1.0 - slit / 0.03)))
                A[5].append((0.05 if k in (1, 2) else 0.25, 0.0))
                A[6].append((1.0, 1.0))
                A[7].append((1.0, 7.0))
        Ps.append(P)
    cope = coping(a, W, batter, years, Ps, Ns, A) if a.coping else None
    # the joints' fill behind the faces: soil and the dark of the hearting, kind 6
    back = 0.045
    top = max(c[2][1] for c in cells) + (0.02 if a.coping else -0.03)
    q = [(0.0, -0.3), (a.length, -0.3), (a.length, top), (0.0, top)]
    Q = [np.array([u, v, -back - v * batter]) for u, v in q]
    soil = np.array([Q[0], Q[1], Q[2], Q[0], Q[2], Q[3]])
    for qq in soil:
        A[0].append((qq[0], qq[1]))
        A[1].append((years, 0.5))
        A[2].append((6.0, 0.0))
        A[3].append((0.2, 0.1))
        A[4].append((0.0, years))
        A[5].append((0.6, 0.0))
        A[6].append((1.0, 1.0))
        A[7].append((1.0, 7.0))
    Ps.append(soil)
    Ns.append(normals(soil, np.zeros(2, bool)))
    P = np.vstack(Ps)
    N = np.vstack(Ns)
    # Unity's frame: z into the wall
    U = np.column_stack([P[:, 0], P[:, 1], -P[:, 2]]).astype(np.float32)
    with open(a.out, "wb") as f:
        f.write(struct.pack("<4si", b"R2B2", len(U)))
        f.write(U.tobytes())
        f.write(np.column_stack([N[:, 0], N[:, 1], -N[:, 2]]).astype(np.float32).tobytes())
        for k in range(8):
            f.write(np.array(A[k], dtype=np.float32).tobytes())
    tc = np.array(tri_counts)
    budget = json.load(open(os.path.join(PACK, "parts", "stone", "wallstone.json")))["levels"]["l0"]["triangles"]
    print(f"{len(cells)} stones, triangles per stone {tc.min()} to {tc.max()} (mean {tc.mean():.1f}; L0's budget "
          f"{budget}: {'pass' if tc.max() <= budget else 'FAIL'}), {len(U) // 3} in all; {a.out}")
    fail = tc.max() > budget
    if cope:
        cc, cb = np.array(cope[0]), cope[1]
        print(f"{len(cc)} copings, triangles per slab {cc.min()} to {cc.max()} (mean {cc.mean():.1f}; L0's budget {cb}: "
              f"{'pass' if cc.max() <= cb else 'FAIL'})")
        fail = fail or cc.max() > cb
    if fail:
        sys.exit(1)


if __name__ == "__main__":
    main()
