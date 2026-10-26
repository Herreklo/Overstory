"""R2b's look loop for the step: a short flight of slab steps laid from the pack's walling (packs/stavanger-1989/
walling.json, the dry-split-1874 working's steps) with the slab step (blender/parts/stone/slate/slabstep.py, its params
the definition's), written as a triangle soup for LT1R2b.cs to draw (x across the flight, y up, z up the flight; then
UV0 to UV7 as Stone.shader's contract has them).

    python3 tools/r2b_steps.py OUT.bin [--steps 7] [--width 1.8] [--seed 1989] [--wear 8] [--year 1989]
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
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import hashing as HS  # noqa: E402
import slabstep  # noqa: E402
from r2b_wall import normals  # noqa: E402

PACK = os.path.join(ROOT, "packs", "stavanger-1989")
MM = 0.001


def load():
    walling = json.load(open(os.path.join(PACK, "walling.json")))["workings"]["dry-split-1874"]
    defn = json.load(open(os.path.join(PACK, "parts", "stone", "step.json")))
    p = {k: v["value"] for k, v in defn["params"].items()}
    return walling, p, defn


def cuts(rng, W, S, below):
    """A tread's pieces: their count by the working's weights, no piece shorter than its least, no joint within the
    clearance of a joint in the step below. Returns the pieces' [x0, x1]."""
    least = S["pieceLeastMm"] * MM
    clear = S["jointClearMm"] * MM
    for _ in range(20):
        k = rng.weighted([(int(c), int(w)) for c, w in S["piecesPerTread"]])
        k = max(1, min(k, int(W // least)))
        xs = sorted(rng.uniform(least, W - least) for _ in range(k - 1))
        if all(b - a >= least for a, b in zip([0.0] + xs, xs + [W])) and \
                all(abs(x - j) > clear for x in xs for j in below):
            return xs
    return []


def piece(key, X0, L, H, D, going, zf, bed, ends, p, S, walk, wear_mm, years, A):
    """One slab of a tread, its front at zf up the flight and its bed at bed, made, worn where the walking line
    keeps (wear_mm at the nosing) and settled, its corners' attributes appended to A. Returns its corners and their
    normals in the flight's frame (x across, y up, z up the flight). Its seed for the material (UV1.y) is drawn from
    its key."""
    def wear(x, z, X0=X0):
        along = 1.0 if z < 0.0 else math.exp(-((z - S["wearPeakMm"] * MM) / (S["wearSpreadMm"] * MM)) ** 2)
        return wear_mm * walk(X0 + x) * (0.25 + 0.75 * along) if z < going else 0.0
    s = slabstep.step(key, L, H, D, going, ends, p, wear)
    Pl = s["P"]
    # settled: the front sunk as the fill under it went, about the back's bed; a roll; the whole a little down
    st = HS.Stream(key, "settle")
    pitch = math.radians(st.uniform(*S["settlePitchDeg"]))
    roll = math.radians(st.uniform(-1.0, 1.0) * S["settleRollDeg"])
    drop = st.uniform(0.0, S["settleDropMm"]) * MM
    d = Pl - np.array([L / 2, 0.0, D])
    y1 = d[:, 1] * math.cos(pitch) + d[:, 2] * math.sin(pitch)
    z1 = -d[:, 1] * math.sin(pitch) + d[:, 2] * math.cos(pitch)
    yaw = math.radians(st.uniform(-1.0, 1.0) * S["settleYawDeg"])
    x2 = d[:, 0] * math.cos(roll) - y1 * math.sin(roll)
    y2 = d[:, 0] * math.sin(roll) + y1 * math.cos(roll)
    x3 = x2 * math.cos(yaw) + z1 * math.sin(yaw)
    z3 = -x2 * math.sin(yaw) + z1 * math.cos(yaw)
    P = np.column_stack([x3 + L / 2 + X0, y2 + bed - drop, z3 + D + zf])
    soft = s["soft"]
    N = normals(P, soft)
    n = len(P)
    var = st.random()
    ou, ov = st.uniform(0, 8), st.uniform(0, 8)
    for t in range(n // 3):
        a3, b3, c3 = P[3 * t:3 * t + 3]
        nrm = np.cross(b3 - a3, c3 - a3)
        nrm /= np.linalg.norm(nrm)
        k = int(s["kind"][t])
        ax = int(np.argmax(np.abs(nrm)))
        for ci, q in enumerate((a3, b3, c3)):
            lx, ly, lz = Pl[3 * t + ci]
            uv0 = (q[0] + ou, q[2] + ov) if ax == 1 else ((q[0] + ou, q[1] + ov) if ax == 2 else (q[2] + ou, q[1] + ov))
            fx = X0 + lx
            worn = walk(fx) * (1.0 if lz < going else 0.0) if k in (0, 1) and nrm[1] > 0.3 else 0.0
            wd = wear(lx, lz) / max(wear_mm, 1e-6) if k == 0 else 0.0
            # (the sky a corner sees: less at the foot of the next riser and of its own front)
            open_ = 1.0
            if k == 0 and nrm[1] > 0.5:
                open_ = 0.5 + 0.5 * min(1.0, max(0.0, (going - lz) / 0.12))
            elif k == 2 and abs(nrm[1]) < 0.5:
                open_ = 0.5 + 0.5 * min(1.0, ly / 0.10)
            elif k == 3:
                open_ = 0.4
            moss = S["moss"]["base"]
            if k == 0 and lz > going - S["moss"]["backMm"] * MM:
                moss = S["moss"]["back"]
            elif k == 0 and nrm[1] > 0.5 and ly < H - 0.01:
                moss = S["moss"]["ledge"]
            if ends[0] == "joint" and lx < 0.02 or ends[1] == "joint" and lx > L - 0.02:
                moss = max(moss, S["moss"]["joint"])
            # (at the foot of a lamina standing back, as at the tread's back: the corner holds moss and water)
            foot = 2.0 * (1.0 - s["sky"][3 * t + ci])
            moss = max(moss, S["moss"]["back"] * foot)
            A[0].append(uv0)
            A[1].append((years, var))
            A[2].append((k, 0.3 * wd))
            open_ *= s["sky"][3 * t + ci]
            A[3].append(((0.5 + 0.5 * nrm[1]) * open_, (0.5 - 0.5 * nrm[1]) * open_))
            A[4].append((worn * min(1.0, wear_mm / 8.0), years * (1.0 - 0.95 * worn)))
            A[5].append((moss, max(0.5 * wd, 0.5 * foot)))
            A[6].append((1.0, 1.0))
            A[7].append((1.0, 7.0))
    return P, N


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--steps", type=int, default=7)
    ap.add_argument("--width", type=float, default=1.8)
    ap.add_argument("--seed", default="1989")
    ap.add_argument("--wear", type=float, default=8.0, help="mm the feet took at the walking line's nosing (the record's)")
    ap.add_argument("--year", type=int, default=1989)
    ap.add_argument("--rise", type=float, default=165.0)
    ap.add_argument("--stride", type=float, default=630.0)
    a = ap.parse_args()
    W, p, defn = load()
    S = W["steps"]
    rise = a.rise * MM
    going = (a.stride - 2 * a.rise) * MM
    years = (a.year - W["built"]) / 200.0
    rng = HS.Stream(HS.h(a.seed, "flight"), "lay")
    # the walking line: where people keep on the flight, and how wide the feet spread about it
    xw = a.width * S["walkLineShare"]
    half = S["walkHalfMm"] * MM

    def walk(x):
        return math.exp(-((x - xw) / half) ** 2)

    Ps, Ns, A = [], [], {k: [] for k in range(8)}
    tri_counts = []
    below = []
    joint_x = []
    for i in range(a.steps):
        lap = rng.uniform(*S["lapMm"]) * MM
        D = going + lap
        zf = i * going + rng.uniform(-1.0, 1.0) * S["frontOutMm"] * MM
        bed = i * rise
        xs = cuts(rng, a.width, S, below)
        below = xs
        edges = [0.0] + xs + [a.width]
        for pi_, (x0, x1) in enumerate(zip(edges[:-1], edges[1:])):
            g0 = 0.0 if pi_ == 0 else 0.5 * rng.uniform(*S["jointMm"]) * MM
            g1 = 0.0 if pi_ == len(edges) - 2 else 0.5 * rng.uniform(*S["jointMm"]) * MM
            X0, L = x0 + g0, (x1 - g1) - (x0 + g0)
            H = rise + rng.uniform(-1.0, 1.0) * S["thickMm"] * MM
            ends = ("open" if pi_ == 0 else "joint", "open" if pi_ == len(edges) - 2 else "joint")
            key = HS.h(a.seed, "step", i, pi_)

            P, N = piece(key, X0, L, H, D, going, zf, bed, ends, p, S, walk, a.wear, years, A)
            Ns.append(N)
            tri_counts.append(len(P) // 3)
            Ps.append(P)
    # the fill under the flight seen past its open ends, and the rest behind its top step: soil, kind 6
    quads = []
    for i in range(a.steps):
        z0, z1, y1 = i * going, (i + 1) * going, i * rise + 0.02
        for xe, sx in ((0.04, -1.0), (a.width - 0.04, 1.0)):
            quads.append(([(xe, -0.2, z0), (xe, -0.2, z1), (xe, y1, z1), (xe, y1, z0)], (sx, 0.0, 0.0)))
    zt, yt = a.steps * going, a.steps * rise - 0.01
    quads.append(([(0, yt, zt), (a.width, yt, zt), (a.width, yt, zt + 1.5), (0, yt, zt + 1.5)], (0.0, 1.0, 0.0)))
    T = []
    for q, want in quads:
        q = np.array(q, float)
        for t in ((q[0], q[1], q[2]), (q[0], q[2], q[3])):
            t = np.array(t)
            if np.dot(np.cross(t[1] - t[0], t[2] - t[0]), want) < 0:
                t = t[[0, 2, 1]]
            T.append(t)
    F = np.array(T).reshape(-1, 3)
    for q in F:
        A[0].append((q[0], q[2]))
        A[1].append((years, 0.5))
        A[2].append((6.0, 0.0))
        A[3].append((0.3, 0.1))
        A[4].append((0.0, years))
        A[5].append((0.6, 0.0))
        A[6].append((1.0, 1.0))
        A[7].append((1.0, 7.0))
    Ps.append(F)
    Ns.append(normals(F, np.zeros(len(F) // 3, bool)))
    P = np.vstack(Ps)
    N = np.vstack(Ns)
    # the bottom step's bed 30 mm into the ground (LT1R2b sets the panel's y 0.15 into the ground)
    P = P + np.array([0.0, 0.12, 0.0])
    # (LT1R2b.Load turns each triangle's winding for Unity's: give it the other way round)
    U = P.reshape(-1, 3, 3)[:, [0, 2, 1]].reshape(-1, 3).astype(np.float32)
    Nn = N.reshape(-1, 3, 3)[:, [0, 2, 1]].reshape(-1, 3).astype(np.float32)
    with open(a.out, "wb") as f:
        f.write(struct.pack("<4si", b"R2B2", len(U)))
        f.write(U.tobytes())
        f.write(Nn.tobytes())
        for k in range(8):
            arr = np.array(A[k], dtype=np.float32).reshape(-1, 3, 2)[:, [0, 2, 1]].reshape(-1, 2)
            f.write(arr.tobytes())
    tc = np.array(tri_counts)
    budget = defn["levels"]["l0"]["triangles"]
    print(f"{a.steps} steps, {len(tc)} pieces, triangles per piece {tc.min()} to {tc.max()} (mean {tc.mean():.1f}; "
          f"L0's budget {budget}: {'pass' if tc.max() <= budget else 'FAIL'}), {len(U) // 3} in all; {a.out}")
    if tc.max() > budget:
        sys.exit(1)


if __name__ == "__main__":
    main()
