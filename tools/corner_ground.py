"""The corner's rock and ground for the painted corner ([CornerElement("rock")], Code/Editor/Corner/CornerRock.cs).

The knuckle from its jointing (blender/generators/bedrock.py, fixtures/lt1-corner-ground.json), each vertex with the
sky it sees (rays against the rock, the land and the houses), its foot and its nearest joint, and the lichen and moss
those give (blender/generators/growth.py, on_rock); and the ground where the knuckle's clay is cut away (the patch:
the land without the knuckle, meeting the clay exactly at the boxes' edges). Written as R2B2 triangle soups (the
gully port's format and vertex layout, tools/r2b_wall.py, so Stone.shader and the painted surface both read them) at
three levels, with a manifest of hashes and triangle counts beside the element's data. Run with Blender's python:

    $PY tools/corner_ground.py [--check]

--check prints each level against its budget (the element's rock.json) and the 60 % rule, and fails over either.
"""

import argparse
import hashlib
import json
import math
import os
import struct
import subprocess
import sys

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "blender", "generators"))
sys.path.insert(0, os.path.join(ROOT, "blender", "resolver"))
import bedrock as BR  # noqa: E402
import growth as GR  # noqa: E402
import hashing as HS  # noqa: E402

FIX = os.path.join(ROOT, "fixtures", "lt1-corner-ground.json")
CACHE = os.path.join(ROOT, "cache", "ground")
DATA = os.path.join(ROOT, "unity", "Assets", "Experiments", "LT1", "Corner", "Elements", "rock")
# the corner's cameras (Paint.json's views): what stands near them is drawn finest
EYES = np.array([[49.3, 12.0, 5.6], [49.8, 21.4, 4.7]])


def site():
    if not os.path.exists(os.path.join(CACHE, "site.json")):
        subprocess.check_call([sys.executable, os.path.join(ROOT, "tools", "corner_site.py")])
    return json.load(open(os.path.join(CACHE, "site.json"))), np.load(os.path.join(CACHE, "site.npz"))


# --- the sky a point sees: rays against a grid of what stands round it ---

class Blockers:
    """What shades the rock and the patch: the rock's own cells, the land and the houses, and the gully's cheek walls,
    as a grid of filled cells (step m)."""

    def __init__(self, bodies, env, S, step=0.2, lo=(44.0, 20.0, 0.0), hi=(68.0, 56.0, 24.0)):
        self.lo, self.step = np.array(lo), step
        self.n = np.ceil((np.array(hi) - self.lo) / step).astype(int)
        nx, ny, nz = self.n
        xs = self.lo[0] + (np.arange(nx) + 0.5) * step
        ys = self.lo[1] + (np.arange(ny) + 0.5) * step
        zs = self.lo[2] + (np.arange(nz) + 0.5) * step
        X, Y = np.meshgrid(xs, ys, indexing="ij")
        H = env.ground(X, Y)
        for b in S["buildings"]:
            fp = np.array(b["fp"])
            inside = np.ones_like(X, bool)
            for i in range(len(fp)):
                p, q = fp[i], fp[(i + 1) % len(fp)]
                cr = (q[0] - p[0]) * (Y - p[1]) - (q[1] - p[1]) * (X - p[0])
                inside &= cr >= 0 if _ccw(fp) else cr <= 0
            # (to the eaves and a little over: the roof's mass)
            H = np.where(inside, np.maximum(H, b["eave"] + 1.0), H)
        G = zs[None, None, :] < H[:, :, None]
        for B in bodies:
            for k in B.solid:
                c = B.cells[k][0]
                P = np.vstack([V for V, *_ in c])
                i0 = np.clip(((P.min(0) - self.lo) / step).astype(int), 0, self.n - 1)
                i1 = np.clip(((P.max(0) - self.lo) / step).astype(int) + 1, 0, self.n)
                sx, sy, sz = xs[i0[0]:i1[0]], ys[i0[1]:i1[1]], zs[i0[2]:i1[2]]
                Q = np.stack(np.meshgrid(sx, sy, sz, indexing="ij"), -1)
                m = np.ones(Q.shape[:3], bool)
                for V, n, d, lab in c:
                    m &= Q @ n <= d
                G[i0[0]:i1[0], i0[1]:i1[1], i0[2]:i1[2]] |= m
        walls = os.path.join(ROOT, "cache", "r2b", "gully-walls.bin")
        if os.path.exists(walls):
            P = read_points(walls)
            idx = ((P - self.lo) / step).astype(int)
            ok = np.all((idx >= 0) & (idx < self.n), axis=1)
            idx = idx[ok]
            G[idx[:, 0], idx[:, 1], idx[:, 2]] = True
        self.G = G

    def sky(self, pts, nrm, rays=64, reach=16.0, start=0.1, lift=0.2):
        """The share of a point's cosine-weighted hemisphere that reaches the sky (open and level: 1; open and
        upright: 0.5), and the share that looks down (the ground's light). The rays leave a cell's width off the face
        (lift), so its own grid cells never shade it; what lies closer (a joint's slit) is the joint shade's.)"""
        # (a fixed spiral of directions, cosine-weighted about +z)
        i = np.arange(rays) + 0.5
        r = np.sqrt(i / rays)
        a = i * math.pi * (3 - math.sqrt(5))
        D0 = np.stack([r * np.cos(a), r * np.sin(a), np.sqrt(1 - r * r)], -1)
        steps = np.arange(start, reach, self.step * 0.9)
        out_s, out_g = np.zeros(len(pts)), np.zeros(len(pts))
        for c0 in range(0, len(pts), 256):
            p, n = pts[c0:c0 + 256], nrm[c0:c0 + 256]
            t = np.where(np.abs(n[:, 2:3]) < 0.9, np.array([[0, 0, 1.0]]), np.array([[1.0, 0, 0]]))
            u = np.cross(t, n)
            u /= np.linalg.norm(u, axis=1, keepdims=True)
            v = np.cross(n, u)
            D = D0[None, :, 0:1] * u[:, None] + D0[None, :, 1:2] * v[:, None] + D0[None, :, 2:3] * n[:, None]
            Q = p[:, None, None, :] + lift * n[:, None, None, :] + D[:, :, None, :] * steps[None, None, :, None]
            idx = np.floor((Q - self.lo) / self.step).astype(int)
            inb = np.all((idx >= 0) & (idx < self.n), axis=-1)
            idc = np.clip(idx, 0, self.n - 1)
            hit = self.G[idc[..., 0], idc[..., 1], idc[..., 2]] & inb
            blocked = hit.any(-1)
            up = D[..., 2] > 0
            out_s[c0:c0 + 256] = (up & ~blocked).sum(1) / rays
            out_g[c0:c0 + 256] = (~up).sum(1) / rays
        return out_s, out_g


def _ccw(fp):
    a = 0.0
    for i in range(len(fp)):
        p, q = fp[i], fp[(i + 1) % len(fp)]
        a += p[0] * q[1] - q[0] * p[1]
    return a > 0


def read_points(path):
    b = open(path, "rb").read()
    n = struct.unpack("<i", b[4:8])[0]
    P = np.frombuffer(b[8:8 + 12 * n], np.float32).reshape(-1, 3)
    return P[:, [0, 2, 1]].astype(float)


# --- the knuckle's faces as triangles, each corner with its data ---

def joints_of(F, rings, env):
    """Each face's joints: the stretches of its edge it shares with a face of another cell (a crack, a shed plate's
    step, a joint between blocks), as segments. A tight joint is no joint: the face runs on across it."""
    own = {}
    for fi, ((V, n, lab, b, k), ring) in enumerate(zip(F, rings)):
        for i in range(len(ring)):
            a, c = ring[i], ring[(i + 1) % len(ring)]
            key = tuple(sorted([tuple(np.round(a, 4)), tuple(np.round(c, 4))]))
            own.setdefault(key, set()).add(BR.supercell(env, k))
    out = []
    for (V, n, lab, b, k), ring in zip(F, rings):
        segs = []
        for i in range(len(ring)):
            a, c = ring[i], ring[(i + 1) % len(ring)]
            key = tuple(sorted([tuple(np.round(a, 4)), tuple(np.round(c, 4))]))
            if len(own.get(key, ())) > 1:
                segs.append((a, c))
        out.append(segs)
    return out


def seg_dist(P, segs):
    if not segs:
        return np.full(len(P), 5.0)
    best = np.full(len(P), 1e9)
    for a, c in segs:
        ab = c - a
        t = np.clip((P - a) @ ab / max(ab @ ab, 1e-12), 0, 1)
        best = np.minimum(best, np.linalg.norm(P - a - t[:, None] * ab, axis=1))
    return best


def kind_of(lab, fams):
    """Stone.shader's kind: the foliation's and the sheeting's planes and the ice's (bedding planes, 0); the cross
    joints, the cuts and the clay's edge (split faces, 2)."""
    if isinstance(lab[0], int):
        return int(fams[lab[0]]["kind"])
    return 0 if lab[0] == "top" else 2


def face_basis(n):
    t = np.array([0, 0, 1.0]) if abs(n[2]) < 0.9 else np.array([1.0, 0, 0])
    u = np.cross(t, n)
    u /= np.linalg.norm(u)
    return u, np.cross(n, u)


def knuckle(fix, S, npz, look, level):
    K = fix["knuckle"]
    bodies, env, N = BR.build(fix, S, npz)
    L = look["levels"][level]
    F = BR.faces(bodies, env, K["id"], K.get("spall") if L.get("spall", True) else None)
    rings = BR.fix_tjunctions(F)
    J = joints_of(F, rings, env)
    near, far = L["nearM"], L["farM"]

    def he(a, b):
        m = (a + b) / 2
        return near if np.min(np.linalg.norm(EYES - m, axis=1)) < look["nearEyeM"] else far
    tris, fid = [], []
    for i, ((V, n, lab, b, k), ring) in enumerate(zip(F, rings)):
        c = V.mean(0)
        h = near if np.min(np.linalg.norm(EYES - c, axis=1)) < look["nearEyeM"] else far
        T = BR.tessellate(V, n, h, ring, he, L.get("insetM", 0.0))
        tris.append(T)
        fid += [i] * len(T)
    return bodies, env, F, J, np.concatenate(tris), np.array(fid)


def corner_data(T, fid, F, J, fams, key, blk, env, look, years):
    """Per corner of each triangle: (points, normals, the eight UV pairs) in Stone's layout."""
    P = T.reshape(-1, 3)
    fi = np.repeat(fid, 3)
    Nn = np.array([F[i][1] for i in fi])
    # (each point once per face: the sky, the foot and the joint)
    keyp = np.column_stack([fi, np.round(P, 4)])
    uq, inv = np.unique(keyp, axis=0, return_inverse=True)
    inv = inv.reshape(-1)
    Up, Un, Uf = uq[:, 1:], np.array([F[int(i)][1] for i in uq[:, 0]]), uq[:, 0].astype(int)
    sky, grd = blk.sky(Up, Un)
    foot = Up[:, 2] - env.ground(Up[:, 0], Up[:, 1])
    joint = np.full(len(Up), 5.0)
    for f in np.unique(Uf):
        m = Uf == f
        joint[m] = seg_dist(Up[m], J[f])
    # (growth's north is +y: the street's north is -x, its east +y)
    gn = np.column_stack([Un[:, 1], -Un[:, 0], Un[:, 2]])
    lichen, moss = GR.on_rock(Up, gn, sky, foot, joint, years)
    # (the contact shade: the dark foot where the rock goes into the ground, the dark margin at a joint)
    B = look["bake"]
    sm = lambda x, w: np.clip(x / w, 0, 1) ** 2 * (3 - 2 * np.clip(x / w, 0, 1))
    shade = (B["footDark"] + (1 - B["footDark"]) * sm(np.maximum(foot, 0), B["footM"])) * \
            (B["jointDark"] + (1 - B["jointDark"]) * sm(joint, B["jointM"]))
    A = [np.zeros((len(P), 2)) for _ in range(8)]
    seeds = {}
    for f in np.unique(fi):
        V, n, lab, b, k = F[f]
        if (b, k) not in seeds:
            seeds[(b, k)] = HS.unit(HS.h(key, "cell", b, *k))
        s = seeds[(b, k)]
        m = fi == f
        u, v = face_basis(n)
        A[0][m] = np.column_stack([P[m] @ u + 8 * s, P[m] @ v + 8 * HS.unit(HS.h(key, "v", b, *k))])
        A[1][m] = (years / 200.0, s)
        A[2][m] = (kind_of(lab, fams), 0.0)
    A[3] = np.column_stack([(sky * shade)[inv], (grd * shade)[inv]])
    A[4][:, 1] = (lichen)[inv]
    A[5][:, 0] = moss[inv]
    A[6][:] = (1.0, 1.0)
    A[7][:] = (1.0, 7.0)
    stats = dict(sky=[float(sky.min()), float(np.median(sky)), float(sky.max())],
                 lichen=float(np.mean(lichen > 0.01)), moss=float(np.mean(moss > 0.05)))
    return P, Nn, A, stats


# --- the patch: the land without the knuckle where its clay is cut away ---

def patch(fix, S, npz, env, bodies, step=0.5):
    """The ground inside the boxes: on their edges the clay's own (linear between its 1.5 m grid's corners), so the
    clay outside meets it with no step; inside, the land without the knuckle, eased in over a clay cell."""
    C = S["clay"]
    clay = npz["clay"]

    def clayz(x, y):
        u = np.clip((x - C["x0"]) / C["step"], 0, clay.shape[0] - 1.001)
        v = np.clip((y - C["y0"]) / C["step"], 0, clay.shape[1] - 1.001)
        i, j = u.astype(int), v.astype(int)
        fu, fv = u - i, v - j
        return (clay[i, j] * (1 - fu) + clay[i + 1, j] * fu) * (1 - fv) + (clay[i, j + 1] * (1 - fu) + clay[i + 1, j + 1] * fu) * fv
    solid = [B.cells[k][0] for B in bodies for k in B.solid]

    def under_rock(p):
        for c in solid:
            if all(p @ n <= d - 0.05 for V, n, d, lab in c):
                return True
        return False
    tris = []
    for bx in fix["patch"]["boxes"]:
        (x0, y0), (x1, y1) = bx["min"], bx["max"]
        nx, ny = int(round((x1 - x0) / step)), int(round((y1 - y0) / step))
        xs, ys = np.linspace(x0, x1, nx + 1), np.linspace(y0, y1, ny + 1)
        X, Y = np.meshgrid(xs, ys, indexing="ij")
        edge = np.minimum.reduce([X - x0, x1 - X, Y - y0, y1 - Y])
        # (a box's edge that meets another box is not the clay's edge)
        for o in fix["patch"]["boxes"]:
            if o is bx:
                continue
            (a0, b0), (a1, b1) = o["min"], o["max"]
            shared = ((np.abs(X - a1) < 1e-6) | (np.abs(X - a0) < 1e-6) | (np.abs(Y - b1) < 1e-6) | (np.abs(Y - b0) < 1e-6)) & \
                     (X >= a0 - 1e-6) & (X <= a1 + 1e-6) & (Y >= b0 - 1e-6) & (Y <= b1 + 1e-6)
            edge = np.where(shared & (edge < 1e-6), C["step"], edge)
        w = np.clip(edge / C["step"], 0, 1)
        Z = clayz(X, Y) * (1 - w) + env.ground(X, Y) * w
        Pg = np.stack([X, Y, Z], -1)
        for i in range(nx):
            for j in range(ny):
                a, b, c, d = Pg[i, j], Pg[i + 1, j], Pg[i + 1, j + 1], Pg[i, j + 1]
                for t in ((a, b, c), (a, c, d)):
                    if all(under_rock(q) for q in t):
                        continue
                    tris.append(t)
    return np.array(tris)


def patch_data(T, blk, env, look, years):
    P = T.reshape(-1, 3)
    n = np.cross(T[:, 1] - T[:, 0], T[:, 2] - T[:, 0])
    n /= np.linalg.norm(n, axis=1, keepdims=True)
    Nn = np.repeat(n, 3, axis=0)
    uq, inv = np.unique(np.round(P, 4), axis=0, return_inverse=True)
    inv = inv.reshape(-1)
    # (the ground's own normal at a point: the mean of its triangles')
    un = np.zeros((len(uq), 3))
    np.add.at(un, inv, Nn)
    un /= np.linalg.norm(un, axis=1, keepdims=True)
    sky, grd = blk.sky(uq, un)
    A = [np.zeros((len(P), 2)) for _ in range(8)]
    A[0] = P[:, :2].copy()
    A[1][:] = (years / 200.0, 0.5)
    A[2][:] = (0.0, 0.0)
    A[3] = np.column_stack([sky[inv], grd[inv]])
    A[6][:] = (1.0, 1.0)
    A[7][:] = (1.0, 7.0)
    return P, np.repeat(n, 3, axis=0), A


def write(path, P, N, A):
    """R2B2: corners (x, z, y) as Unity has them, their normals, the eight UV pairs (LT1R2b.Load turns the winding)."""
    with open(path, "wb") as f:
        f.write(struct.pack("<4si", b"R2B2", len(P)))
        f.write(P[:, [0, 2, 1]].astype(np.float32).tobytes())
        f.write(N[:, [0, 2, 1]].astype(np.float32).tobytes())
        for a in A:
            f.write(a.astype(np.float32).tobytes())
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="fail over a budget or the 60 %% rule")
    ap.add_argument("--levels", default="l0,l1,l2")
    args = ap.parse_args()
    fix = json.load(open(FIX))
    look = json.load(open(os.path.join(DATA, "rock.json")))["generator"]
    S, npz = site()
    K = fix["knuckle"]
    fams = K["jointing"]["families"]
    years = fix["date"] - K["bareSince"]
    os.makedirs(CACHE, exist_ok=True)
    man = {"_": "tools/corner_ground.py; the binaries are rebuilt, not tracked (cache/ground/)", "fixture":
           hashlib.sha256(open(FIX, "rb").read()).hexdigest(), "levels": {}}
    blk = None
    counts = []
    for lv in args.levels.split(","):
        bodies, env, F, J, T, fid = knuckle(fix, S, npz, look, lv)
        if blk is None:
            blk = Blockers(bodies, env, S)
        P, N, A, st = corner_data(T, fid, F, J, fams, K["id"], blk, env, look, years)
        h = write(os.path.join(CACHE, f"knuckle-{lv}.bin"), P, N, A)
        e = np.linalg.norm(T[:, 1] - T[:, 0], axis=1)
        man["levels"][lv] = {"file": f"cache/ground/knuckle-{lv}.bin", "sha256": h, "triangles": len(T),
                             "faces": len(F), "medianEdgeM": round(float(np.median(e)), 3)}
        counts.append((lv, len(T)))
        print(f"knuckle {lv}: {len(T)} triangles, {len(F)} faces, median edge {np.median(e):.2f} m, sky {np.round(st['sky'], 2)}, "
              f"lichen on {st['lichen']:.0%}, moss on {st['moss']:.0%}")
    Tp = patch(fix, S, npz, env, bodies)
    P, N, A = patch_data(Tp, blk, env, look, years)
    h = write(os.path.join(CACHE, "patch-l0.bin"), P, N, A)
    man["patch"] = {"file": "cache/ground/patch-l0.bin", "sha256": h, "triangles": len(Tp)}
    print(f"patch: {len(Tp)} triangles")
    json.dump(man, open(os.path.join(DATA, "manifest.json"), "w"), indent=2)
    if args.check:
        bad = []
        for i, (lv, n) in enumerate(counts):
            budget = look["levels"][lv]["triangles"]
            ok = n <= budget
            rule = i == 0 or n <= 0.6 * counts[i - 1][1]
            print(f"  {lv}: {n} of {budget} {'ok' if ok else 'OVER'}" + ("" if i == 0 else f", {n / counts[i - 1][1]:.0%} of {counts[i - 1][0]} {'ok' if rule else 'OVER the 60 % rule'}"))
            if not (ok and rule):
                bad.append(lv)
        if bad:
            sys.exit(f"over budget: {', '.join(bad)}")


if __name__ == "__main__":
    main()
