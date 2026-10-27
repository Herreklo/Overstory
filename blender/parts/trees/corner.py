"""The walked corner's trees, drawn from their facts at their levels (reviews/lt1/art-direction/README.md, the trees:
three to five masses, never leaves, the crown lost upward). A birch grows from its timeline (tree_growth.py), leans as
its facts say, and its foliage is gathered by limb into a few masses; each mass is drawn as bold mass cards
(mass_card.py) on the skin of its lobes, all lit by the mass's one smooth normal, so a crown reads as a few lit tops
and shaded undersides with seams of sky between, never as leaves. The spruce is a fitted silhouette: a spire of
drooping tiers. Every value is corner.json's or a fact's.

Writes cache/trees/corner/<id>.<level>.tre and cache/trees/corner/trees.json (each level's triangles), read by
unity/Assets/Code/Editor/LT1CornerTrees.cs. Numpy only (run with Blender's Python 3.13):

    python3.13 blender/parts/trees/corner.py [id ...]
"""

import json
import math
import os
import struct
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "blender", "generators"))
sys.path.insert(0, os.path.join(ROOT, "blender"))
import tree as T                # noqa: E402
import tree_growth as G         # noqa: E402
from resolver import hashing as HS     # noqa: E402

OUT = os.path.join(ROOT, "cache", "trees", "corner")
CELLS = {"round": 0, "wide": 1, "notched": 2, "thin": 3}


# -- the mesh -----------------------------------------------------------------------------------------------------------

class Mesh:
    """Vertices (street axes, z up) with normal, colour, uv0, uv1, uv2, and triangles in named submeshes."""

    def __init__(self):
        self.P, self.N, self.C, self.U0, self.U1, self.U2 = [], [], [], [], [], []
        self.sub = {}

    def vert(self, p, n, c=(1, 0, 1, 0), u0=(0, 0), u1=(0, 0), u2=(0, 0)):
        self.P.append(p), self.N.append(n), self.C.append(c), self.U0.append(u0), self.U1.append(u1), self.U2.append(u2)
        return len(self.P) - 1

    def tri(self, sub, a, b, c):
        self.sub.setdefault(sub, []).append((a, b, c))

    def tris(self, sub):
        return len(self.sub.get(sub, ()))

    def write(self, path):
        """TRE1: count, then per vertex position and normal (Unity axes: x, z, y), colour, uv0, uv1, uv2; then each
        submesh's name (16 bytes) and its triangles, wound for Unity (the axes' swap mirrors them)."""
        n = len(self.P)
        P = np.asarray(self.P, np.float32)[:, [0, 2, 1]]
        N = np.asarray(self.N, np.float32)[:, [0, 2, 1]]
        data = np.concatenate([P, N, np.asarray(self.C, np.float32), np.asarray(self.U0, np.float32),
                               np.asarray(self.U1, np.float32), np.asarray(self.U2, np.float32)], axis=1)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as f:
            f.write(b"TRE1" + struct.pack("<ii", n, len(self.sub)))
            f.write(data.astype("<f4").tobytes())
            for name, t in self.sub.items():
                idx = np.asarray(t, np.int32)[:, [0, 2, 1]].reshape(-1)
                f.write(name.encode()[:16].ljust(16, b"\0") + struct.pack("<i", len(idx)))
                f.write(idx.astype("<i4").tobytes())


# -- the birch ----------------------------------------------------------------------------------------------------------

def lean(tl, d, deg, upright, H):
    """The whole tree leaned as its facts say: its trunk leaves the ground at deg from upright towards d and rights
    itself as it rises (upright, the share of the lean its top takes back); everything above moves with it."""
    if deg <= 0:
        return
    t0 = math.tan(math.radians(deg))
    d = np.array([d[0], d[1], 0.0]) / max(math.hypot(d[0], d[1]), 1e-9)
    for key in ("start", "end"):
        P = tl[key]
        z = np.clip(P[:, 2], 0.0, None)
        zc = np.minimum(z, H)
        off = t0 * (zc - upright * zc * zc / (2.0 * H)) + t0 * (1.0 - upright) * (z - zc)
        tl[key] = P + off[:, None] * d[None, :]


def fib(n):
    """n directions spread evenly over the sphere (a Fibonacci lattice)."""
    i = np.arange(n) + 0.5
    phi = np.arccos(1.0 - 2.0 * i / n)
    th = math.pi * (1.0 + 5.0 ** 0.5) * i
    return np.stack([np.cos(th) * np.sin(phi), np.sin(th) * np.sin(phi), np.cos(phi)], axis=1)


def ell_area(r):
    a, b, c = r
    p = 1.6075
    return 4.0 * math.pi * (((a * b) ** p + (a * c) ** p + (b * c) ** p) / 3.0) ** (1.0 / p)


def inside(vol, p):
    c, axes, radii = vol
    q = (np.asarray(p) - c) @ axes / radii
    return 1.0 - np.linalg.norm(q, axis=-1)


def normal_of(vol, p):
    c, axes, radii = vol
    q = (np.asarray(p) - c) @ axes
    g = (q / radii ** 2) @ axes.T
    return g / np.maximum(np.linalg.norm(g, axis=-1, keepdims=True), 1e-9)


def grow_birch(tid, fact, kind):
    """The birch's timeline at its age, at the height its facts give (the site's quality found so the grown tree
    stands that tall), leaned as they say."""
    age = 1989 - int(fact["planted"])
    seed = HS.h("tree", tid, "habit") % 100000
    g = G.genotype(G.SPECIES["birch"], seed)
    H = float(fact["height"])
    q = round(H / G.height_curve(g, age, 1.0), 2)
    ex, origin = float(fact.get("exposure", 0.0)), fact.get("origin", "self-seeded")
    for _ in range(3):
        tl = T.read("birch", seed, age, q, (), ex, origin)
        top = float(tl["end"][tl["alive"]][:, 2].max())
        if abs(top - H) < 0.35:
            break
        q = round(q * H / top, 2)
    shed(tl, float(kind.get("shed", 0.0)) * top)
    narrow(tl, float(kind.get("narrow", 1.0)), top)
    lean(tl, fact.get("lean", (1.0, 0.0)), float(fact.get("lean_deg", 0.0)), float(fact.get("lean_upright", 0.0)), top)
    return tl, seed, age, q, top


def shed(tl, z):
    """The lower limbs a birch has shed (self-pruning: a pioneer that cannot bear its own shade): every branch whose
    whole reach stays under z, gone with what it carries; limbs that climb past z keep their upper wood."""
    if z <= 0.0:
        return
    parent, order, alive, end = tl["parent"], tl["order"], tl["alive"], tl["end"]
    reach = end[:, 2].copy()
    for i in range(len(parent) - 1, 0, -1):         # children come after their parents
        if alive[i]:
            j = int(parent[i])
            reach[j] = max(reach[j], reach[i])
    dead = np.zeros(len(parent), bool)
    for i in range(1, len(parent)):
        dead[i] = dead[int(parent[i])] or (order[i] >= 1 and reach[i] < z)
    alive &= ~dead
    tl["children_of"] = {k: [c for c in v if alive[c]] for k, v in tl["children_of"].items()}


def narrow(tl, k, H):
    """The crown drawn narrower than grown, about the trunk's line (the downy birch's ascending limbs: the habit's
    outline, a style value): full width at the foot, k of it from a third of the height up."""
    if k >= 1.0:
        return
    trunk = np.nonzero(tl["order"] == 0)[0]
    tz = tl["end"][trunk][:, 2]
    o = np.argsort(tz)
    tz, txy = tz[o], tl["end"][trunk][o][:, :2]
    for key in ("start", "end"):
        P = tl[key]
        ax = np.stack([np.interp(P[:, 2], tz, txy[:, 0]), np.interp(P[:, 2], tz, txy[:, 1])], axis=1)
        f = 1.0 - (1.0 - k) * np.clip((P[:, 2] - 0.15 * H) / (0.2 * H), 0.0, 1.0)
        P[:, :2] = ax + (P[:, :2] - ax) * f[:, None]


def crown_masses(tl, kind, seed, age, H):
    """The foliage gathered by limb into the habit's masses, each split into lobes; ellipsoids for both."""
    parts = T.PARTS["birch"]
    ids = T.leafy(tl, parts, age, seed, T.drawn_tips(parts, H), cap=False)
    P = tl["end"][ids]
    P = P[P[:, 2] >= 0.9 * float(kind.get("shed", 0.0)) * H]
    k = int(kind["masses"])
    # the masses: compact regions of the foliage, stacked more than side by side (z counts tiers times), so the
    # seams between them run across the crown as a painter's do
    tier = float(kind.get("tiers", 1.0))
    which = T.spatial_masses(P * np.array([1.0, 1.0, tier]), k, seed)
    vols = T.volumes(P, which, k)
    lobes = []
    for m in range(k):
        Pm = P[which == m]
        if len(Pm) < 12:
            lobes.append([])
            continue
        size = float(np.linalg.norm(Pm - Pm.mean(axis=0), axis=1).mean())
        lo, hi = kind["lobes"]
        nl = int(np.clip(round(size / 0.9), lo, hi))
        lw = T.spatial_masses(Pm, nl, seed + m)
        lv = [v for v in T.volumes(Pm, lw, nl) if v is not None]
        lobes.append(lv)
    # each mass moved out from the crown's middle, its lobes with it: the seams of sky open between them
    seam = float(kind.get("seam", 0.0))
    mid = P.mean(axis=0)
    for m in range(k):
        if vols[m] is None:
            continue
        d = vols[m][0] - mid
        d[2] *= 0.6
        d = d / max(np.linalg.norm(d), 1e-6) * seam
        vols[m] = (vols[m][0] + d, vols[m][1], vols[m][2])
        lobes[m] = [(c + d, a, r) for (c, a, r) in lobes[m]]
    return P, which, vols, lobes


def cards(mesh, tl, kind, lv, seed, H, vols, lobes, base):
    """The mass cards on each mass's lobes' skin: turned to the eye in the shader, lit by the mass's smooth normal."""
    shell = float(kind["shell"])
    card0 = float(lv["card"])
    dens = float(lv["density"])
    w_mass = float(kind["mass_normal"])
    lift = float(kind["lift"])
    lost0, lost_drop = kind["lost_up"]
    fallen = float(kind["fallen"])
    zb = base
    # each mass drawn inside its foliage's skin (its lobes drawn in towards its middle, still overlapping), so seams
    # of sky open between masses, never inside one
    lobe_k = float(kind.get("lobe_shell", 0.92))
    allshell = [[(vols[m][0] + (c - vols[m][0]) * shell, a, r * lobe_k * (0.5 + 0.5 * shell)) for (c, a, r) in L]
                if vols[m] is not None else [] for m, L in enumerate(lobes)]
    count = 0
    for m, L in enumerate(allshell):
        if not L or vols[m] is None:
            continue
        msize = float(np.mean(vols[m][2]))
        card = card0 * float(np.clip(msize / 2.2, 0.75, 1.25))
        for li, vol in enumerate(L):
            n = max(int(math.ceil(dens * ell_area(vol[2]) / (0.55 * card * card))), 6)
            d = fib(n)
            # each lobe's lattice turned its own seeded way, so no two lobes' cards line up
            a = HS.unit(HS.h("lobe", seed, m, li)) * 2 * math.pi
            rot = np.array([[math.cos(a), -math.sin(a), 0], [math.sin(a), math.cos(a), 0], [0, 0, 1]])
            d = d @ rot.T
            c, axes, radii = vol
            pts = c + (d * radii) @ axes.T
            for j, p in enumerate(pts):
                # on the mass's outer skin only: never inside another lobe of it, nor inside another mass (its seam)
                deep = max([inside(v, p) for i2, v in enumerate(L) if i2 != li] + [-1.0])
                if deep > 0.12:
                    continue
                other = max([inside(v, p) for m2, L2 in enumerate(allshell) if m2 != m for v in L2] + [-1.0])
                if other > -0.05:
                    continue
                if p[2] < 1.0:
                    continue
                hs = float(np.clip((p[2] - zb) / max(H - zb, 1e-3), 0.0, 1.0))
                key = HS.h("card", seed, m, li, j)
                u = HS.unit(key)
                nl = normal_of(vol, p)
                nm = normal_of(vols[m], p)
                nn = w_mass * nm + (1.0 - w_mass) * nl + np.array([0.0, 0.0, lift])
                nn /= np.linalg.norm(nn)
                # the autumn's fall: inside and low first; the top thinning as the crown loses itself upward
                drop = fallen * (1.2 - hs) * (0.6 + 0.8 * max(-nn[2], 0.0))
                if hs > lost0:
                    drop = max(drop, lost_drop * (hs - lost0) / (1.0 - lost0))
                if HS.unit(HS.h(key, "fall")) < drop:
                    continue
                cell = "thin" if hs > lost0 + 0.5 * (1.0 - lost0) else "wide" if nn[2] < kind["underside"] else \
                    ("notched" if HS.unit(HS.h(key, "cell")) < 0.3 else "round")
                size = card * (0.8 + 0.4 * HS.unit(HS.h(key, "size"))) * (0.8 if cell == "thin" else 1.0)
                pivot = p - nl * 0.28 * size
                # the sky it sees: by its facing, under the masses above it
                sky = 0.45 + 0.55 * max(nn[2], 0.0) + 0.15 * min(nn[2], 0.0)
                for m2, v2 in enumerate(vols):
                    if m2 != m and v2 is not None and v2[0][2] > p[2]:
                        q = p.copy()
                        q[2] = v2[0][2]
                        if inside(v2, q) > 0.0:
                            sky *= 0.6
                ground = 0.3 * max(-nn[2], 0.0)
                up = 0.5 + 0.5 * float(nl[2])
                ci = CELLS[cell]
                cu, cv = (ci % 2) * 0.5, 0.5 - (ci // 2) * 0.5      # the cell's corner in the atlas (v up)
                ang = HS.unit(HS.h(key, "turn")) * 2 * math.pi
                ca, sa = math.cos(ang), math.sin(ang)
                col = (float(np.clip(sky, 0, 1)), hs, up, u)
                vs = []
                for ox, oy in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
                    rx, ry = 0.5 * size * (ox * ca - oy * sa), 0.5 * size * (ox * sa + oy * ca)
                    vs.append(mesh.vert(tuple(pivot), tuple(nn), col, (cu + 0.25 + 0.25 * ox, cv + 0.25 + 0.25 * oy),
                                        (m, u), (rx, ry)))
                mesh.tri("crown", vs[0], vs[1], vs[2])
                mesh.tri("crown", vs[0], vs[2], vs[3])
                count += 1
    return count


def bark(mesh, tl, lv, kind, H, sub="bark", vols=()):
    """The trunk and limbs (tree.py's wood), its tips drawn only as the level shows them, the foot rooted; wood inside
    a mass sees little sky (its limbs dark in the crown's shade, white only where they come out of it)."""
    parts = dict(T.PARTS["birch"])
    parts["draw_tips_per_m"] = float(lv["draw_tips_per_m"])
    parts["winter_tips"] = T.drawn_tips(parts, H)
    sides0 = T.sides_for
    cap = int(lv["sides"])
    T.sides_for = lambda r: max(3, min(sides0(r), cap))
    try:
        V, F, UV0, UV1, samples, APPEAR, wood = T.branch_mesh(tl, parts, H)
    finally:
        T.sides_for = sides0
    V = np.asarray(V, np.float64)
    # the foot roots into the soil: buttresses round the trunk's first metre, spreading as they go down
    rt = kind["root"]
    foot = tl["start"][0]
    r0 = float(tl["r"][0])
    near = (V[:, 2] < rt["height"] * 3) & (np.hypot(V[:, 0] - foot[0], V[:, 1] - foot[1]) < 3.0 * r0)
    a = np.arctan2(V[:, 1] - foot[1], V[:, 0] - foot[0])
    ph = HS.unit(HS.h("roots", int(r0 * 1e4))) * 2 * math.pi
    lob = np.maximum(np.cos(rt["lobes"] * a + ph), 0.0) ** 2
    k = 1.0 + rt["amp"] * lob * np.exp(-np.maximum(V[:, 2], 0.0) / rt["height"])
    V[near, 0] = foot[0] + (V[near, 0] - foot[0]) * k[near]
    V[near, 1] = foot[1] + (V[near, 1] - foot[1]) * k[near]
    # smooth normals by welded vertex
    Nacc = np.zeros_like(V)
    for f in F:
        p = V[list(f)]
        n = np.cross(p[1] - p[0], p[2] - p[0])
        for i in f:
            Nacc[i] += n
    Nn = Nacc / np.maximum(np.linalg.norm(Nacc, axis=1, keepdims=True), 1e-12)
    # how deep each vertex is in the foliage (each mass's whole skin, its seams too: the leaves round a limb shade
    # it even where the drawn masses part)
    deep = np.full(len(V), -1.0)
    for v in vols:
        if v is not None:
            deep = np.maximum(deep, inside(v, V))
    k_in = float(kind.get("limb_sky", 1.0))
    shade = 1.0 - (1.0 - k_in) * np.clip((deep + 0.3) / 0.5, 0.0, 1.0)
    # and under a mass: wood in a seam between masses sees the sky only from the side
    k_under = float(kind.get("limb_under", 1.0))
    for v in vols:
        if v is not None:
            q = V.copy()
            q[:, 2] = v[0][2]
            under = (V[:, 2] < v[0][2]) & (inside(v, q) > 0.0)
            shade = np.where(under, np.minimum(shade, k_under), shade)
    li = 0
    for f in F:
        vs = []
        for i in f:
            sky = (0.6 + 0.4 * max(Nn[i][2], 0.0)) * float(shade[i])
            # r the sky it sees (its facing and the foliage round it), b the foliage's shade alone
            vs.append(mesh.vert(tuple(V[i]), tuple(Nn[i]), (sky, 0.2, float(shade[i]), 0.0), tuple(UV0[li]), tuple(UV1[li])))
            li += 1
        for j in range(1, len(vs) - 1):
            mesh.tri(sub, vs[0], vs[j], vs[j + 1])


def proxies(mesh, vols, shell, sub="shadow"):
    """Each mass as a low ellipsoid that casts the crown's shadow (cards cast none)."""
    d = fib(42)
    for v in vols:
        if v is None:
            continue
        c, axes, radii = v
        P = c + (d * radii * shell) @ axes.T
        base = len(mesh.P)
        for p, n in zip(P, normal_of(v, P)):
            mesh.vert(tuple(p), tuple(n))
        # a hull of the lattice's points: its convex triangles by brute force (few points)
        pts = d
        for i in range(len(pts)):
            for j in range(i + 1, len(pts)):
                for k in range(j + 1, len(pts)):
                    n = np.cross(pts[j] - pts[i], pts[k] - pts[i])
                    side = (pts - pts[i]) @ n
                    if np.all(side <= 1e-9) or np.all(side >= -1e-9):
                        if np.dot(n, pts[i]) < 0:
                            mesh.tri(sub, base + i, base + k, base + j)
                        else:
                            mesh.tri(sub, base + i, base + j, base + k)


def birch(tid, fact, kind, levels):
    tl, seed, age, q, H = grow_birch(tid, fact, kind)
    P, which, vols, lobes = crown_masses(tl, kind, seed, age, H)
    base = float(np.percentile(P[:, 2], 3))
    out = {}
    for name in levels:
        lv = kind["levels"][name]
        mesh = Mesh()
        bark(mesh, tl, lv, kind, H, vols=vols)
        n = cards(mesh, tl, kind, lv, seed, H, vols, lobes, base)
        if lv.get("shadow"):
            proxies(mesh, vols, float(kind["shell"]))
        out[name] = (mesh, dict(cards=n))
    info = dict(seed=seed, age=age, quality=q, height=round(H, 2), masses=len([v for v in vols if v is not None]),
                crown_base=round(base, 2))
    return out, info


# -- the spruce: a fitted silhouette ------------------------------------------------------------------------------------

def spruce(tid, fact, kind, levels):
    """A spire of drooping tiers: each whorl's branches as broad sheets that droop and hang their curtains, wider
    down the crown; lit as one cone (each sheet carries the cone's normal), so from the street it reads as one dark
    toothed silhouette."""
    H = float(fact["height"])
    seed = HS.h("tree", tid, "habit") % 100000
    R0 = 0.5 * kind["width"] * H
    zb = kind["crown_base"]
    out = {}
    for name in levels:
        lv = kind["levels"][name]
        mesh = Mesh()
        # the trunk to its leader's tip
        s = int(lv["sides"])
        rings = [(0.0 - 0.4, 0.26), (0.0, 0.25), (0.5, 0.21), (H * 0.5, 0.13), (H - 1.0, 0.03), (H, 0.005)]
        idx = []
        for z, r in rings:
            row = []
            for k in range(s):
                a = 2 * math.pi * k / s
                row.append(mesh.vert((r * math.cos(a), r * math.sin(a), z), (math.cos(a), math.sin(a), 0.0),
                                     (0.5, 0.2, 1.0, 0.0), (k / s, z), (r, z)))
            idx.append(row)
        for i in range(len(rings) - 1):
            for k in range(s):
                a, b, c, d = idx[i][k], idx[i][(k + 1) % s], idx[i + 1][(k + 1) % s], idx[i + 1][k]
                mesh.tri("bark", a, b, c)
                mesh.tri("bark", a, c, d)
        # the whorls, from the top down
        st = HS.Stream("spruce", tid)
        z = H - kind["leader"]
        wi = 0
        segs = int(lv["segments"])
        while z > zb:
            t = (H - z) / (H - zb)                       # 0 at the top, 1 at the foot
            R = R0 * (t ** 0.85) * (0.9 + 0.2 * st.uniform(0, 1))
            nb = int(round(kind["branches"][0] + (kind["branches"][1] - kind["branches"][0]) * t))
            ph = st.uniform(0, 2 * math.pi)
            for b in range(nb):
                a = ph + 2 * math.pi * (b + st.uniform(-0.25, 0.25)) / nb
                L = R * (0.8 + 0.35 * st.uniform(0, 1))
                if L < 0.15:
                    continue
                dirv = np.array([math.cos(a), math.sin(a), 0.0])
                side = np.array([-math.sin(a), math.cos(a), 0.0])
                droop = kind["droop"] * L
                hang = kind["curtain"] * min(L, 2.5) * t
                prev = None
                for j in range(segs + 1):
                    u = j / segs
                    c = dirv * (L * u) + np.array([0.0, 0.0, z - droop * u * u])
                    w = (0.12 + 0.9 * u) * L * 0.5 * (2 * math.pi / nb) * 0.75
                    # the cone's normal: outward and up
                    nrm = dirv * 0.85 + np.array([0.0, 0.0, 0.53])
                    hs = 1.0 - t
                    col = (0.5 + 0.4 * hs, hs, 0.5, HS.unit(HS.h(tid, wi, b)))
                    top_l = mesh.vert(tuple(c - side * w), tuple(nrm), col, (0, 0), (0, 0))
                    top_r = mesh.vert(tuple(c + side * w), tuple(nrm), col, (0, 0), (0, 0))
                    low = c + np.array([0.0, 0.0, -hang * u])
                    bot = mesh.vert(tuple(low + dirv * 0.05), tuple(nrm), col, (0, 0), (0, 0))
                    if prev is not None:
                        pl, pr, pb = prev
                        mesh.tri("solid", pl, pr, top_r)
                        mesh.tri("solid", pl, top_r, top_l)
                        if hang > 0.05:
                            mesh.tri("solid", pl, top_l, bot)
                            mesh.tri("solid", pr, bot, top_r)
                    prev = (top_l, top_r, bot)
            step = kind["whorl"][0] + (kind["whorl"][1] - kind["whorl"][0]) * t
            z -= step * lv["whorl_scale"]
            wi += 1
        out[name] = (mesh, {})
    return out, dict(seed=seed, height=H)


# -- the corner -----------------------------------------------------------------------------------------------------------

def load():
    with open(os.path.join(ROOT, "fixtures", "lt1-corner.json")) as f:
        record = json.load(f)
    with open(os.path.join(ROOT, "fixtures", "lt1-corner-trees.json")) as f:
        extra = json.load(f)
    with open(os.path.join(HERE, "corner.json")) as f:
        kinds = json.load(f)
    facts = {t["id"]: t for t in record["trees"]}
    trees = []
    for e in extra["trees"]:
        f = dict(facts[e["id"]])
        f.update(e)
        trees.append(f)
    return trees, kinds


def main(only=()):
    trees, kinds = load()
    os.makedirs(OUT, exist_ok=True)
    index_path = os.path.join(OUT, "trees.json")
    index = {"trees": []}
    if os.path.exists(index_path):
        with open(index_path) as f:
            index = json.load(f)
    have = {t["id"]: t for t in index["trees"]}
    for f in trees:
        tid = f["id"]
        if only and tid not in only:
            continue
        habit = f["habit"]
        levels = f["levels"]
        if habit == "spruce":
            built, info = spruce(tid, f, kinds["spruce"], levels)
        else:
            kind = kinds["birch_heath"] if levels == ["far"] else kinds["birch"]
            built, info = birch(tid, f, kind, levels)
        lv_out = []
        for name, (mesh, extra) in built.items():
            path = os.path.join(OUT, f"{tid}.{name}.tre")
            mesh.write(path)
            tris = {k: mesh.tris(k) for k in mesh.sub}
            lv_out.append(dict(level=name, file=os.path.relpath(path, ROOT), tris=tris,
                               drawn=sum(v for k, v in tris.items() if k != "shadow"), **extra))
            print(tid, name, tris, extra)
        street = f["position"] if "position" in f else None
        have[tid] = dict(id=tid, habit=habit, at=[f["x"] / 1000.0, f["y"] / 1000.0] if "x" in f else street,
                         levels=lv_out, **info)
    index["trees"] = [have[t["id"]] for t in trees if t["id"] in have]
    with open(index_path, "w") as fo:
        json.dump(index, fo, indent=1)
    return index


if __name__ == "__main__":
    main(tuple(sys.argv[1:]))
