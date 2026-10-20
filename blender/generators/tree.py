"""A tree assembled from its grown timeline and its species' parts (docs/trees.md, How a tree is made, step 4).

    blender -b --factory-startup --python blender/generators/tree.py -- <species> <seed> <age> [quality] [unity]

The timeline (blender/generators/tree_growth.py, cached) is read at the age: the living nodes, each at its radius then.
From it, two meshes in one FBX (unity/Assets/Art/Trees/<species>/tree_<species>_s<seed>_a<age>.fbx):

- branches: each branch a chain of internodes, swept as a tube, its rings kept only where the branch bends or thins
  (parallel-transport frames, so a tube never twists); the thinnest twigs are left to the leaf sprays; a flare at the
  foot. UV0: bark, round and along in tiles of the species' bark (u wraps a whole number of times). UV1: the branch's
  drawn radius and its height above the ground, in metres, for the bark shader (twig colour, the old trunk's foot);
- leaves: a card from the species' spray atlas on every leafy shoot (the shoots younger than the species keeps leaves
  on), its foot where the shoot ends and its length along it, turned about the shoot to face out of its mass, tied to
  its node by the node's id, so a branch keeps its leaves for life. UV0: the atlas; UV1: the card's rank in the season
  (low turns and falls first: the most exposed, then a seeded order) and its own seed.

The crown's masses: the cards grouped by the limb they hang from, merged to three to five, each a convex hull
dissolved into a few planes (a painter's blocking of a crown). Every card takes its normal from the nearest plane of its
own mass, so a crown shades as a few planes of light and shade, not as a thousand cards. The bake (vertex colour:
sky, ground, openness, 1) says how deep a card or a branch is inside its mass and which way it faces.

Deterministic: the timeline is, and every choice here hashes the tree's seed with a node's id.
"""

import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import tree_growth as G  # noqa: E402

# Each species' parts and how they are fitted. card: the spray card's length and width (m); cells: sprays in the atlas
# (2 by 2); per_node: cards on each leafy shoot, crossing about it; along: more along it where it is out in the light;
# droop: how far a spray hangs from its shoot's line under its own weight; leaf_years: how many years a shoot keeps
# bearing leaves; leaf_tips: the most shoot tips a stem may carry and still bear sprays itself (by the pipe model, so it
# holds whatever the species' tip size); draw_tips: the fewest shoot tips a branch carries to be drawn as a tube
# (lighter ones are in the sprays), raised by draw_tips_per_m for each metre of the tree's height; reach: how far along
# undrawn twigs a spray may hang from drawn wood;
# bark: one bark tile round and along (m); grow_to: how long the timeline is grown (it contains every younger age);
# sag: how much the branches give under their own weight (see sag); atlas: which painted leaves the cards carry (the
# species' sprays, or its clumps: a painter's blocking of its foliage); hang: clumps hang from their shoots' ends,
# sized for a twig's foliage on a grown tree (clump_full: the height at which they reach full size).
PARTS = {
    "birch": dict(sag=0.05, taper=0.55, occlusion=0.05, seam=0.3, atlas="lobes", lobe=0.6, lobe_gap=0.15, lose_tips=40, hang=False, card=(0.50, 0.48), card_u=(0.03, 0.97), cells=4,
                  per_node=2, along=1, droop=0.7, leaf_years=999, leaf_tips=24, draw_tips=2.5, draw_tips_per_m=0.45, reach=0.9,
                  bark=(0.30, 0.60), max_cards=4200, grow_to=80),
    "spruce": dict(card=(0.60, 0.40), cells=4, per_node=2, droop=0.25, leaf_years=7, leaf_tips=30, draw_tips=3.0, draw_tips_per_m=0.45,
                   bark=(0.30, 0.50), max_cards=8000, grow_to=100),
}


def h01(*k):
    """A stable hash of integers to 0..1 (SplitMix64-style), for every seeded choice."""
    x = 0x9E3779B97F4A7C15
    for v in k:
        x = (x ^ (int(v) & 0xFFFFFFFFFFFFFFFF)) * 0xBF58476D1CE4E5B9 & 0xFFFFFFFFFFFFFFFF
        x = (x ^ (x >> 31)) * 0x94D049BB133111EB & 0xFFFFFFFFFFFFFFFF
        x ^= x >> 29
    return (x >> 11) / float(1 << 53)


def drawn_radius(r):
    """The pipe model's radius drawn: true for limbs and the trunk, thinned for twigs, which the model holds a little
    thick because each modelled tip stands for a bundle of real shoots."""
    return np.where(r > 0.02, r, r * (0.4 + 0.6 * r / 0.02))


def read(species, seed, age, quality):
    parts = PARTS[species]
    t = G.cached(species, seed, max(parts["grow_to"], age), quality)
    alive = (t["born"] <= age) & ((t["died"] < 0) | (t["died"] > age))
    pipe = t["radius"][:, age].astype(np.float64)
    tl = dict(parent=t["parent"], start=t["start"].astype(np.float64), end=t["end"].astype(np.float64),
              born=t["born"], order=t["order"], r=drawn_radius(pipe), alive=alive,
              tips=(pipe / G.SPECIES[species]["tip_radius"]) ** G.SPECIES[species]["pipe"])
    sag(tl, pipe, parts, G.SPECIES[species]["tip_radius"])
    return tl


def sag(tl, pipe, parts, tip):
    """The branches bent by their own weight at this age, as loaded cantilevers: each internode turns down by the
    moment of everything beyond it (its foliage, by the pipe model's tips, and its wood) about its start, over its
    stiffness (its radius to the fourth power), so thin twigs under leaves hang, long limbs arch out and the trunk
    stands. Rotations carry down each branch to everything it bears; computed from the timeline at the age, so a
    heavier, older limb sags more. The timeline's own record is left as it grew."""
    k = parts.get("sag", 0.0)
    if k <= 0:
        return
    parent, order, alive = tl["parent"], tl["order"], tl["alive"]
    start, end = tl["start"], tl["end"]
    n = len(parent)
    seg = end - start
    length = np.linalg.norm(seg, axis=1)
    mid = (start + end) / 2
    rr = np.maximum(pipe / tip, 1.0)                       # radius in tips' radii
    own = np.where(alive, 0.15 * length * rr ** 2 / 40.0, 0.0)   # wood
    kids_leafy = np.zeros(n)
    W = own.copy()
    S = own[:, None] * mid
    # leaves: the shoots at the ends (no living child of their own) carry the foliage
    has_kid = np.zeros(n, dtype=bool)
    for i in range(1, n):
        if alive[i]:
            has_kid[parent[i]] = True
    leaf = alive & ~has_kid
    W += leaf * 1.0
    S += (leaf * 1.0)[:, None] * end
    for i in range(n - 1, 0, -1):
        if alive[i]:
            p = parent[i]
            W[p] += W[i]
            S[p] += S[i]
    R = np.zeros((n, 3, 3))
    R[:] = np.eye(3)
    bent = np.zeros(n)                                    # how far each has turned down from how it grew
    new_start, new_end = start.copy(), end.copy()
    down = np.array([0.0, 0.0, -1.0])
    for i in range(n):
        if not alive[i]:
            continue
        p = parent[i]
        Rp = R[p] if i > 0 else np.eye(3)
        d = Rp @ seg[i]
        ns = new_end[p] if i > 0 else start[i]
        if order[i] > 0 and W[i] > 0:
            # the moment about this internode's start: the load beyond it times its reach out from here
            c = S[i] / W[i] - start[i]
            reach = math.hypot(c[0], c[1])
            curv = k * W[i] * reach / rr[i] ** 4
            # a branch's own stiffness limits it: a few degrees an internode, about fifty along all of it
            ang = min(curv * length[i], 0.10, max(0.0, 0.9 - bent[p]))
            dn = d / max(np.linalg.norm(d), 1e-12)
            axis = np.cross(dn, down)
            na = np.linalg.norm(axis)
            if ang > 1e-5 and na > 1e-6:
                axis /= na
                c_, s_ = math.cos(ang), math.sin(ang)
                K = np.array([[0, -axis[2], axis[1]], [axis[2], 0, -axis[0]], [-axis[1], axis[0], 0]])
                Ri = np.eye(3) + s_ * K + (1 - c_) * (K @ K)
                Rp = Ri @ Rp
                d = Ri @ d
            bent[i] = bent[p] + ang
        else:
            bent[i] = bent[p] if i > 0 else 0.0
        R[i] = Rp
        new_start[i] = ns
        new_end[i] = ns + d
    tl["start"], tl["end"] = new_start, new_end


# -- branches -------------------------------------------------------------------------------------------------------

def chains(tl):
    """Each branch as a list of node ids from its base to its tip: from the trunk's first node and from every node
    that starts a branch, along the living child of the same order."""
    parent, order, alive = tl["parent"], tl["order"], tl["alive"]
    n = len(parent)
    main = np.full(n, -1)
    for i in range(1, n):
        p = parent[i]
        if alive[i] and alive[p] and order[i] == order[p] and main[p] < 0:
            main[p] = i
    out = []
    for i in range(n):
        if not alive[i] or (i > 0 and alive[parent[i]] and order[parent[i]] == order[i] and main[parent[i]] == i):
            continue
        c = [i]
        while main[c[-1]] >= 0:
            c.append(main[c[-1]])
        out.append(c)
    return out


def simplify(pts, radii, bend=0.14, thin=0.25):
    """Keep a chain's points where it bends by more than bend (radians, since the last kept) or thins by more than thin
    (a share), and its ends."""
    keep = [0]
    for i in range(1, len(pts) - 1):
        a = pts[keep[-1]]
        d0 = pts[i] - a
        d1 = pts[i + 1] - pts[i]
        n0, n1 = np.linalg.norm(d0), np.linalg.norm(d1)
        if n0 < 1e-9 or n1 < 1e-9:
            continue
        ang = math.acos(max(-1.0, min(1.0, float(np.dot(d0, d1) / (n0 * n1)))))
        if ang > bend or abs(radii[i] - radii[keep[-1]]) > thin * radii[keep[-1]]:
            keep.append(i)
    keep.append(len(pts) - 1)
    return keep


def sides_for(r):
    return 10 if r >= 0.12 else 8 if r >= 0.06 else 6 if r >= 0.03 else 4 if r >= 0.015 else 3


def frames(pts):
    """Tangents, normals and binormals along a polyline by parallel transport."""
    m = len(pts)
    T = np.zeros((m, 3))
    for i in range(m):
        a, b = pts[max(i - 1, 0)], pts[min(i + 1, m - 1)]
        d = b - a
        T[i] = d / max(np.linalg.norm(d), 1e-12)
    N = np.zeros((m, 3))
    t0 = T[0]
    ref = np.array([0.0, 0.0, 1.0]) if abs(t0[2]) < 0.9 else np.array([1.0, 0.0, 0.0])
    N[0] = np.cross(t0, ref)
    N[0] /= np.linalg.norm(N[0])
    for i in range(1, m):
        axis = np.cross(T[i - 1], T[i])
        s = np.linalg.norm(axis)
        if s < 1e-9:
            N[i] = N[i - 1]
            continue
        axis /= s
        c = float(np.dot(T[i - 1], T[i]))
        ang = math.atan2(s, c)
        v = N[i - 1]
        N[i] = v * math.cos(ang) + np.cross(axis, v) * math.sin(ang) + axis * np.dot(axis, v) * (1 - math.cos(ang))
        N[i] -= T[i] * np.dot(N[i], T[i])
        N[i] /= max(np.linalg.norm(N[i]), 1e-12)
    B = np.cross(T, N)
    return T, N, B


def branch_mesh(tl, parts, H, vols=None):
    """Vertices, faces, per-loop UV0 and UV1, and the chain points (for the bake), for every branch thick enough. The
    thinnest drawn grows with the tree: from the street stop a twig thinner than about a pixel is the sprays' to carry."""
    start, end, r, tips = tl["start"], tl["end"], tl["r"], tl["tips"]
    draw = drawn_tips(parts, H)
    tile_round, tile_along = parts["bark"]
    V, F, UV0, UV1 = [], [], [], []
    samples = []                                         # (point, radius) along branches, for the bake
    for c in chains(tl):
        if tips[c[0]] < draw:
            continue
        # spurs and short stubs are carried by the sprays, not drawn as tubes
        if sum(np.linalg.norm(end[i] - start[i]) for i in c) < 0.12:
            continue
        pts = np.array([start[c[0]]] + [end[i] for i in c])
        rad = np.array([r[c[0]]] + [r[i] for i in c])
        tp = np.array([tips[c[0]]] + [tips[i] for i in c])
        # stop where the branch carries too little to be drawn, or where a thin one passes deep into a mass of
        # foliage: there the foliage carries it (a painter loses twigs in the leaves; drawn, they are black scratches)
        stop = len(pts)
        lost = parts.get("lose_tips", 0)
        for k in range(1, len(pts)):
            deep = 0.0
            if vols and tp[k] < lost:
                deep = max((volume_depth(v, pts[k]) for v in vols if v is not None), default=0.0)
            if tp[k] < draw or deep > 0.3:
                stop = k + 1
                break
        pts, rad = pts[:stop], rad[:stop]
        if len(pts) < 2:
            continue
        # rings where a branch bends: tight on the trunk and limbs, looser the thinner it is (a kink in a thin branch
        # is not seen from the street stop)
        keep = simplify(pts, rad, bend=0.06 if rad[0] >= 0.08 else 0.12 if rad[0] >= 0.04 else 0.25)
        pts, rad = pts[keep], rad[keep]
        if c[0] == 0:
            # the trunk thickens towards its foot (the wind's lever on the crown is greatest there; the pipe model alone
            # gives a pole), then flares into the ground
            crown_base = max(H * 0.35, 1e-3)
            rad = rad * (1.0 + parts.get("taper", 0.0) * np.clip((crown_base - pts[:, 2]) / crown_base, 0.0, 1.0) ** 0.6)
            # the trunk's foot: below the ground a little, and flared
            pts = np.vstack([pts[0] - np.array([0.0, 0.0, 0.25]), pts])
            rad = np.concatenate([[rad[0] * 1.35], rad])
            rad[1] *= 1.18
        s = sides_for(rad[0])
        wraps = max(1, int(round(2 * math.pi * rad[0] / tile_round)))
        T, N, B = frames(pts)
        along = np.concatenate([[0.0], np.cumsum(np.linalg.norm(np.diff(pts, axis=0), axis=1))])
        base = len(V)
        for i in range(len(pts)):
            rr = rad[i] if i < len(pts) - 1 else rad[i] * 0.6
            for k in range(s):
                a = 2 * math.pi * k / s
                V.append(pts[i] + rr * (math.cos(a) * N[i] + math.sin(a) * B[i]))
            samples.append((pts[i], rad[i]))
        for i in range(len(pts) - 1):
            for k in range(s):
                k1 = (k + 1) % s
                F.append((base + i * s + k, base + i * s + k1, base + (i + 1) * s + k1, base + (i + 1) * s + k))
                u0, u1 = wraps * k / s, wraps * (k + 1) / s
                v0, v1 = along[i] / tile_along, along[i + 1] / tile_along
                UV0.extend([(u0, v0), (u1, v0), (u1, v1), (u0, v1)])
                UV1.extend([(rad[i], pts[i][2]), (rad[i], pts[i][2]), (rad[i + 1], pts[i + 1][2]),
                            (rad[i + 1], pts[i + 1][2])])
        # the tip closed to a point
        tip = len(V)
        V.append(pts[-1] + T[-1] * rad[-1] * 1.5)
        i = len(pts) - 1
        for k in range(s):
            k1 = (k + 1) % s
            F.append((base + i * s + k, base + i * s + k1, tip))
            UV0.extend([(wraps * k / s, along[i] / tile_along), (wraps * (k + 1) / s, along[i] / tile_along),
                        (wraps * (k + 0.5) / s, (along[i] + rad[-1]) / tile_along)])
            UV1.extend([(rad[-1], pts[-1][2])] * 3)
    return np.array(V), F, UV0, UV1, samples


# -- leaves and masses -------------------------------------------------------------------------------------------------

def drawn_tips(parts, H):
    """How many shoot tips a branch must carry to be drawn as a tube: more on a bigger tree, seen from further off
    (from the street stop a twig under a pixel wide is the sprays' to carry). By the pipe model, so it holds whatever
    the species' tip size."""
    return max(parts["draw_tips"], H * parts["draw_tips_per_m"])


def leafy(tl, parts, age, seed, draw):
    """The nodes that carry a spray at the age: the living shoots younger than the species keeps leaves on, thin
    enough, and near enough drawn wood that the spray is seen to hang from it (no leaves in the air on twigs too thin
    to draw), at most max_cards of them (a seeded choice if there are more)."""
    parent, alive, tips = tl["parent"], tl["alive"], tl["tips"]
    seglen = np.linalg.norm(tl["end"] - tl["start"], axis=1)
    undrawn = np.zeros(len(parent))
    for i in range(1, len(parent)):
        if alive[i]:
            undrawn[i] = 0.0 if tips[i] >= draw else undrawn[parent[i]] + seglen[i]
    ok = alive & (age - tl["born"] < parts["leaf_years"]) & (tl["tips"] <= parts["leaf_tips"]) \
        & (undrawn <= parts.get("reach", 0.9))
    ids = np.nonzero(ok)[0]
    if len(ids) > parts["max_cards"]:
        keep = sorted(ids, key=lambda i: h01(seed, i, 7))[:parts["max_cards"]]
        ids = np.array(sorted(keep))
    return ids


def limbs(tl):
    """Each node's limb: the first-order branch it grows from (its base's id), or -1 on the trunk."""
    parent, order, alive = tl["parent"], tl["order"], tl["alive"]
    limb = np.full(len(parent), -1)
    for i in range(1, len(parent)):
        p = parent[i]
        if order[i] == 0:
            limb[i] = -1
        elif order[i] == 1 and order[p] == 0:
            limb[i] = i
        else:
            limb[i] = limb[p]
    return limb


def masses(points, groups, k):
    """Merge the groups of points into k masses, nearest centroids first (weighted by size, so small groups join
    their neighbours before big ones meet). Returns each point's mass index."""
    keys = sorted(set(groups.tolist()))
    members = {g: [i for i in range(len(points)) if groups[i] == g] for g in keys}
    cl = [members[g] for g in keys]
    while len(cl) > k:
        cents = [points[m].mean(axis=0) for m in cl]
        best, pair = None, None
        for a in range(len(cl)):
            for b in range(a + 1, len(cl)):
                d = np.linalg.norm(cents[a] - cents[b]) * math.sqrt(min(len(cl[a]), len(cl[b])))
                if best is None or d < best:
                    best, pair = d, (a, b)
        a, b = pair
        cl[a] = cl[a] + cl[b]
        del cl[b]
    out = np.zeros(len(points), dtype=int)
    for m, idx in enumerate(cl):
        out[idx] = m
    return out


def spatial_masses(points, k, seed, iters=25):
    """The crown cut into k compact masses by where its foliage is (k-means, seeded from the farthest points so it is
    deterministic): a painter's masses are regions of the crown, each one plane of light or shade, never interleaved."""
    pts = np.asarray(points)
    if len(pts) <= k:
        return np.arange(len(pts))
    # farthest-point start: the top, then each next the farthest from those chosen
    cent = [pts[int(np.argmax(pts[:, 2]))]]
    for _ in range(1, k):
        d = np.min(np.linalg.norm(pts[:, None, :] - np.array(cent)[None, :, :], axis=2), axis=1)
        cent.append(pts[int(np.argmax(d))])
    cent = np.array(cent)
    for _ in range(iters):
        which = np.argmin(np.linalg.norm(pts[:, None, :] - cent[None, :, :], axis=2), axis=1)
        new = np.array([pts[which == m].mean(axis=0) if np.any(which == m) else cent[m] for m in range(k)])
        if np.allclose(new, cent):
            break
        cent = new
    return which


def volumes(points, which, k):
    """Each mass as an ellipsoid fitted to its foliage (centre, axes, radii along them), for smooth volume normals."""
    out = []
    for m in range(k):
        pts = np.asarray(points)[which == m]
        if len(pts) < 6:
            out.append(None)
            continue
        c = pts.mean(axis=0)
        w, v = np.linalg.eigh(np.cov((pts - c).T) + np.eye(3) * 1e-4)
        out.append((c, v, 2.0 * np.sqrt(np.maximum(w, 1e-4))))
    return out


def volume_depth(vol, p):
    """How deep a point lies in a mass's ellipsoid: 0 at its skin (or outside), 1 at its centre."""
    c, axes, radii = vol
    q = axes.T @ (np.asarray(p) - c)
    return float(np.clip(1.0 - np.linalg.norm(q / radii), 0.0, 1.0))


def volume_normal(vol, p, lift=0.25):
    """The outward normal of a mass's ellipsoid at the point (its gradient), tipped a little up: the top of a mass is
    where the sky lights it."""
    c, axes, radii = vol
    q = axes.T @ (np.asarray(p) - c)
    g = axes @ (q / radii ** 2)
    n = g / max(np.linalg.norm(g), 1e-9) + np.array([0.0, 0.0, lift])
    return n / np.linalg.norm(n)


def hulls(points, which, k):
    """Each mass as a convex hull dissolved into a few planes; a BVH tree for each."""
    import bmesh
    from mathutils import Vector
    from mathutils.bvhtree import BVHTree
    trees = []
    for m in range(k):
        pts = points[which == m]
        if len(pts) < 8:
            trees.append(None)
            continue
        bm = bmesh.new()
        for p in pts:
            bm.verts.new(Vector(p))
        bmesh.ops.convex_hull(bm, input=bm.verts[:], use_existing_faces=False)
        loose = [v for v in bm.verts if not v.link_faces]
        bmesh.ops.delete(bm, geom=loose, context="VERTS")
        bmesh.ops.dissolve_limit(bm, angle_limit=math.radians(24), verts=bm.verts[:], edges=bm.edges[:])
        bm.normal_update()
        trees.append((BVHTree.FromBMesh(bm), pts.mean(axis=0), float(np.linalg.norm(pts - pts.mean(axis=0), axis=1).mean()), len(bm.faces)))
        bm.free()
    return trees


def depth_in(trees, m, p):
    """How deep p lies inside mass m (0 at its skin or outside, 1 deep), and the nearest plane's normal."""
    from mathutils import Vector
    t = trees[m]
    if t is None:
        return 0.0, None
    bvh, centre, size, _ = t
    loc, normal, _, dist = bvh.find_nearest(Vector(p))
    if loc is None:
        return 0.0, None
    inside = np.dot(np.array(p) - np.array(loc), np.array(normal)) < 0
    return (min(dist / max(0.55 * size, 1e-3), 1.0) if inside else 0.0), np.array(normal)


def thin(points, keys, gap):
    """A deterministic Poisson thinning: points taken in their seeded order, each kept if none kept lies within gap."""
    order = np.argsort(keys)
    cell = {}
    kept = []
    for j in order:
        p = points[j]
        c = tuple((p // gap).astype(int))
        ok = True
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                for dz in (-1, 0, 1):
                    for q in cell.get((c[0] + dx, c[1] + dy, c[2] + dz), ()):
                        if np.linalg.norm(points[q] - p) < gap:
                            ok = False
                            break
                    if not ok:
                        break
                if not ok:
                    break
            if not ok:
                break
        if ok:
            kept.append(j)
            cell.setdefault(c, []).append(j)
    return np.array(sorted(kept), dtype=int)


def lobe_mesh(tl, parts, age, seed, H):
    """The foliage as a painter's lobes: one painted lobe card (strokes standing for little groups of leaves,
    flat-filled, scalloped at the edge) for each patch of leafy shoots about lobe_gap across, hung a little below them;
    the crown's masses fitted to them; every corner of every card shaded by its mass's smooth volume (the normal and
    how deep it lies), so a mass reads as one shape with a lit top and a shaded underside, never card by card."""
    ids = leafy(tl, parts, age, seed, drawn_tips(parts, H))
    end = tl["end"]
    if len(ids) == 0:
        return np.zeros((0, 3)), [], [], [], [], [], None, None, None
    scale = min(max(H / parts.get("clump_full", 12.0), 0.55), 1.0)
    size = parts["lobe"] * scale
    pts = end[ids]
    keep = thin(pts, np.array([h01(seed, i, 21) for i in ids]), parts["lobe_gap"] * scale)
    ids, pts = ids[keep], pts[keep]
    centres = pts - np.array([0.0, 0.0, 0.38 * size])     # a curtain hangs from its shoot: its top at the shoot
    k = int(min(6, max(3, round(3 + (H - 6) / 5))))
    which = spatial_masses(centres, k, seed)
    vols = volumes(centres, which, k)
    trees = hulls(centres, which, k)
    # sky between the masses: lobes on the seam between two masses are thinned
    seam = parts.get("seam", 0.0)
    if seam > 0 and k > 1:
        keep = []
        for j, i in enumerate(ids):
            own = vols[which[j]]
            if own is None:
                keep.append(True)
                continue
            e_own = np.linalg.norm((own[1].T @ (centres[j] - own[0])) / own[2])
            e = [np.linalg.norm((v[1].T @ (centres[j] - v[0])) / v[2]) for m, v in enumerate(vols) if v is not None and m != which[j]]
            ratio = min(e) / max(e_own, 1e-6) if e else 9.0
            keep.append(not (ratio < 1.0 + seam and h01(seed, i, 15) < 0.9))
        keep = np.array(keep)
        ids, centres, which = ids[keep], centres[keep], which[keep]
    V, F, UV0, UV1, NR, COL = [], [], [], [], [], []
    up_w = np.array([0.0, 0.0, 1.0])
    for j, i in enumerate(ids):
        vol = vols[which[j]]
        c0 = vol[0] if vol is not None else centres.mean(axis=0)
        out = centres[j] - c0
        out[2] *= 0.5
        out /= max(np.linalg.norm(out), 1e-9)
        wob = np.array([h01(seed, i, 11), h01(seed, i, 12), h01(seed, i, 13)]) * 2.0 - 1.0
        face = out + wob * 0.9
        face -= up_w * np.dot(face, up_w) * 0.7               # mostly upright cards: lobes hang
        face /= max(np.linalg.norm(face), 1e-9)
        side = np.cross(up_w, face)
        if np.linalg.norm(side) < 1e-6:
            side = np.array([1.0, 0.0, 0.0])
        side /= np.linalg.norm(side)
        upc = np.cross(face, side)
        roll = (h01(seed, i, 1) - 0.5) * math.radians(24)     # curtains hang plumb, give or take
        side, upc = side * math.cos(roll) + upc * math.sin(roll), upc * math.cos(roll) - side * math.sin(roll)
        s_ = size * (0.6 + 0.9 * h01(seed, i, 14) ** 1.5)
        corners = [centres[j] - side * s_ / 2 - upc * s_ / 2, centres[j] + side * s_ / 2 - upc * s_ / 2,
                   centres[j] + side * s_ / 2 + upc * s_ / 2, centres[j] - side * s_ / 2 + upc * s_ / 2]
        b = len(V)
        V.extend(corners)
        F.append((b, b + 1, b + 2, b + 3))
        cell = int(h01(seed, i, 2) * parts["cells"]) % parts["cells"]
        cx, cy = (cell % 2) * 0.5, 1.0 - (cell // 2) * 0.5 - 0.5
        u0, u1 = (cx, cx + 0.5) if h01(seed, i, 3) < 0.5 else (cx + 0.5, cx)
        UV0.extend([(u0, cy), (u1, cy), (u1, cy + 0.5), (u0, cy + 0.5)])
        depth_c = volume_depth(vol, centres[j]) if vol is not None else 0.0
        zrel = float(np.clip(centres[j][2] / max(H, 1e-3), 0.0, 1.0))
        rank = 0.55 * h01(seed, i, 4) + 0.45 * depth_c
        fall = 0.45 * (1.0 - depth_c) + 0.3 * zrel + 0.25 * h01(seed, i, 9)
        UV1.extend([(rank, fall)] * 4)
        for p in corners:
            n = volume_normal(vol, p) if vol is not None else face
            dep = volume_depth(vol, p) if vol is not None else 0.0
            NR.append(n)
            COL.append((float(0.25 + 0.75 * (1.0 - dep) ** 1.2), float(np.clip(0.15 + 0.35 * max(-n[2], 0.0), 0, 1)), 1.0, 1.0))
    return np.array(V), F, UV0, UV1, NR, COL, trees, which, vols


def leaf_mesh(tl, parts, age, seed, H, species):
    ids = leafy(tl, parts, age, seed, drawn_tips(parts, H))
    start, end = tl["start"], tl["end"]
    L, W = parts["card"]
    # clumps are the size of a twig's foliage, smaller on a young tree
    scale = min(max(H / parts.get("clump_full", 12.0), 0.6), 1.0)
    if len(ids) == 0:
        return np.zeros((0, 3)), [], [], [], [], [], None, None
    d = end[ids] - start[ids]
    d /= np.maximum(np.linalg.norm(d, axis=1, keepdims=True), 1e-9)
    # the spray's line: the shoot's, hanging a little under its own weight
    d = d + np.array([0.0, 0.0, -parts["droop"]])
    d /= np.maximum(np.linalg.norm(d, axis=1, keepdims=True), 1e-9)
    centres = end[ids] + d * (L * 0.45)
    plan = None   # the masses are the limbs' foliage (below); the growth's plan only drew it together
    if plan:
        # the species' plan of masses: the cards gather in them (a few stay outside, seeded), each shading by its own
        inside = np.array([G.in_mass(c, plan, H) for c in centres], dtype=object)
        m = np.array([x[0] for x in inside], dtype=float)
        keep = np.array([m[j] > -0.12 or h01(seed, i, 6) < 0.22 for j, i in enumerate(ids)])
        ids, d, centres = ids[keep], d[keep], centres[keep]
        which = np.array([x[1] for x in inside[keep]], dtype=int)
        used = sorted(set(which.tolist()))
        which = np.array([used.index(w) for w in which])
        k = len(used)
    else:
        k = int(min(5, max(3, round(3 + (H - 6) / 6))))
        which = spatial_masses(centres, k, seed)
    trees = hulls(np.vstack([centres, end[ids] + d * L]), np.concatenate([which, which]), max(k, 1))
    vols = volumes(centres, which, k)
    # sky between the masses: sprays on the seam between two masses (nearly as deep in the neighbour as in their own)
    # are thinned, seeded, so the crown reads as a few masses, never one
    seam = parts.get("seam", 0.0)
    if seam > 0 and k > 1:
        keep = []
        for j, i in enumerate(ids):
            own = vols[which[j]]
            if own is None:
                keep.append(True)
                continue
            e_own = 1.0 - volume_depth(own, centres[j])
            e = [np.linalg.norm((v[1].T @ (centres[j] - v[0])) / v[2]) for m, v in enumerate(vols) if v is not None and m != which[j]]
            ratio = (min(e) / max(np.linalg.norm((own[1].T @ (centres[j] - own[0])) / own[2]), 1e-6)) if e else 9.0
            keep.append(not (ratio < 1.0 + seam and h01(seed, i, 15) < 0.92))
        keep = np.array(keep)
        ids, d, centres, which = ids[keep], d[keep], centres[keep], which[keep]
    V, F, UV0, UV1, NR, COL = [], [], [], [], [], []
    for j, i in enumerate(ids):
        depth, nrm = depth_in(trees, which[j], centres[j])
        if nrm is None:
            c = trees[which[j]][1] if trees[which[j]] is not None else centres.mean(axis=0)
            nrm = centres[j] - c
            nrm /= max(np.linalg.norm(nrm), 1e-9)
        # a little of the card's own way out of the mass, so neighbouring cards on one plane are not identical
        out = centres[j] - (trees[which[j]][1] if trees[which[j]] is not None else centres.mean(axis=0))
        out /= max(np.linalg.norm(out), 1e-9)
        # the mass's own volume: a smooth ellipsoid fitted to its foliage, so light turns across the mass from a lit
        # side to a shadow side (the shader steps it into a painter's few values); never card by card
        n_shade = volume_normal(vols[which[j]], centres[j]) if vols[which[j]] is not None else nrm / max(np.linalg.norm(nrm), 1e-9)
        if vols[which[j]] is not None:
            # how deep inside its own mass the card is: 0 at the skin, 1 at the core
            depth = volume_depth(vols[which[j]], centres[j])
        # the cards' planes hold the spray's line, the first turned about it to face out of its mass with a seeded
        # roll, the others crossing it
        face0 = n_shade - d[j] * np.dot(n_shade, d[j])
        if np.linalg.norm(face0) < 1e-6:
            face0 = np.cross(d[j], [0.0, 0.0, 1.0])
        face0 /= max(np.linalg.norm(face0), 1e-9)
        side0 = np.cross(d[j], face0)
        nz = n_shade[2]
        sky = float(np.clip((1.0 - depth) * (0.72 + 0.28 * nz), 0.12, 1.0))
        ground = float(np.clip(0.1 + 0.3 * max(-nz, 0.0) + 0.2 * depth, 0.0, 1.0))
        opn = float(1.0 - depth)
        # two orders in the season: colour comes to the most exposed first; leaves fall first inside the crown and low
        # in it, so by late October the structure shows through and the outer upper shoots hold on
        rank = 0.55 * h01(seed, i, 4) + 0.45 * depth
        zrel = float(np.clip(end[i][2] / max(H, 1e-3), 0.0, 1.0))
        fall = 0.45 * (1.0 - depth) + 0.3 * zrel + 0.25 * h01(seed, i, 9)
        # the shoot's own sprays at its end, and deeper in a mass more along it: the short shoots a birch carries its
        # leaves on, so a mass is dense while the branches stay open
        extra = parts.get("along", 0) * (1 if sky > 0.55 else 0) + parts.get("along", 0) * (1 if sky > 0.8 else 0)
        for c in range(parts["per_node"] + extra):
            roll = (h01(seed, i, 1, c) - 0.5) * math.radians(50) + c * math.radians(68)
            side = side0 * math.cos(roll) + face0 * math.sin(roll)
            if c < parts["per_node"]:
                foot = end[i] - d[j] * 0.03
            else:
                f = 0.2 + 0.6 * h01(seed, i, 8, c)
                foot = start[i] + (end[i] - start[i]) * f
            b = len(V)
            if parts.get("hang"):
                # a clump hangs from its shoot's end: its top (the atlas's twig) there, the clump below, turned to
                # face out of its mass
                up = np.array([0.0, 0.0, 1.0]) * 0.8 + d[j] * 0.2
                up /= np.linalg.norm(up)
                # turned off the mass's facing by a seeded angle, so many clumps are seen aslant, as leaves are
                wob = np.array([h01(seed, i, 11, c), h01(seed, i, 12, c), h01(seed, i, 13, c)]) * 2.0 - 1.0
                face = n_shade + wob * 0.75
                face = face - up * np.dot(face, up)
                if np.linalg.norm(face) < 1e-6:
                    face = np.cross(up, [1.0, 0.0, 0.0])
                face /= np.linalg.norm(face)
                hs = np.cross(up, face)
                rot = (h01(seed, i, 1, c) - 0.5) * math.radians(70)          # a seeded turn about the facing
                hs, up = hs * math.cos(rot) + up * math.sin(rot), up * math.cos(rot) - hs * math.sin(rot)
                k_ = scale * (0.6 + 0.65 * h01(seed, i, 14, c))           # sprays in a few sizes, overlapping
                sl, sw = L * k_, W * k_
                top = end[i] + up * sl * 0.03
                V.extend([top - up * sl - hs * sw / 2, top - up * sl + hs * sw / 2, top + hs * sw / 2, top - hs * sw / 2])
            else:
                V.extend([foot - side * W / 2, foot + side * W / 2, foot + side * W / 2 + d[j] * L,
                          foot - side * W / 2 + d[j] * L])
            F.append((b, b + 1, b + 2, b + 3))
            cell = int(h01(seed, i, 2, c) * parts["cells"]) % parts["cells"]
            cx, cy = (cell % 2) * 0.5, 1.0 - (cell // 2) * 0.5 - 0.5
            u0, u1 = cx + 0.5 * parts.get("card_u", (0.2, 0.8))[0], cx + 0.5 * parts.get("card_u", (0.2, 0.8))[1]
            if h01(seed, i, 3, c) < 0.5:
                u0, u1 = u1, u0                                 # mirrored
            UV0.extend([(u0, cy), (u1, cy), (u1, cy + 0.5), (u0, cy + 0.5)])
            UV1.extend([(rank, fall)] * 4)
            NR.extend([n_shade] * 4)
            COL.extend([(sky, ground, opn, 1.0)] * 4)
    # what each card sees of an overcast sky through all the others (the growth's own sky, at the cards): the true
    # occlusion of the crown, the value under a grey sky (top and outside light, inside and under dark)
    V = np.array(V)
    if len(V):
        cards = V.reshape(-1, 4, 3).mean(axis=1)
        seen = crown_sky(cards, H, parts.get("occlusion", 0.6))
        for c in range(len(cards)):
            for q in range(4):
                sky_, ground_, _, a_ = COL[c * 4 + q]
                COL[c * 4 + q] = (float(0.1 + 0.9 * min(seen[c] * 1.4, 1.0)), ground_, 1.0, a_)
    return V, F, UV0, UV1, NR, COL, trees, which


def crown_sky(points, H, extinction):
    """The share of an overcast sky each point sees through the crown's cards (rays to the sky through a grid of them;
    tree_growth.Sky)."""
    pts = np.asarray(points)
    radius = float(np.abs(pts[:, :2]).max()) + 2.0
    sky = G.Sky(radius, H * 1.2 + 2.0, 0.35, extinction, 0.0)
    sky.build(pts, np.zeros((0, 3)))
    seen, _ = sky.light(pts)
    return np.clip(seen, 0.0, 1.0)


def branch_bake(samples, V, trees, k):
    """For each branch vertex: sky by its facing and how deep it is in the crown; ground by facing down."""
    pts = np.array([p for p, _ in samples])
    deep = np.zeros(len(pts))
    if trees is not None:
        for j, p in enumerate(pts):
            deep[j] = max((depth_in(trees, m, p)[0] for m in range(k) if trees[m] is not None), default=0.0)
    return pts, deep


# -- in Blender ---------------------------------------------------------------------------------------------------------

def make(name, V, F, UV0, UV1, COL=None, normals=None, smooth=True):
    import bpy
    me = bpy.data.meshes.new(name)
    me.from_pydata([tuple(v) for v in V], [], F)
    me.validate()
    me.update()
    uv0 = me.uv_layers.new(name="uv0")
    uv0.data.foreach_set("uv", np.array(UV0, dtype=np.float32).ravel())
    uv1 = me.uv_layers.new(name="uv1")
    uv1.data.foreach_set("uv", np.array(UV1, dtype=np.float32).ravel())
    if COL is not None:
        attr = me.color_attributes.new("bake", "FLOAT_COLOR", "CORNER")
        attr.data.foreach_set("color", np.array(COL, dtype=np.float32).ravel())
        me.color_attributes.active_color = attr
    me.polygons.foreach_set("use_smooth", [smooth] * len(me.polygons))
    if normals is not None:
        me.normals_split_custom_set([tuple(n) for n in normals])
    me.update()
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    return ob


def build(species, seed, age, quality=1.0, unity=None):
    import bpy
    parts = PARTS[species]
    for ob in list(bpy.data.objects):
        bpy.data.objects.remove(ob, do_unlink=True)
    tl = read(species, seed, age, quality)
    H = float(tl["end"][tl["alive"]][:, 2].max())
    vols = None
    if parts.get("atlas") == "lobes":
        LV, LF, LUV0, LUV1, LN, LC, trees, which, vols = lobe_mesh(tl, parts, age, seed, H)
    else:
        LV, LF, LUV0, LUV1, LN, LC, trees, which = leaf_mesh(tl, parts, age, seed, H, species)
    k = int(which.max()) + 1 if which is not None and len(which) else 0
    BV, BF, BUV0, BUV1, samples = branch_mesh(tl, parts, H, vols)
    # the branches' bake: per loop, from the vertex's facing and the depth of the nearest chain point in the crown
    pts, deep = branch_bake(samples, BV, trees, k)
    from mathutils import kdtree
    kd = kdtree.KDTree(len(pts))
    for j, p in enumerate(pts):
        kd.insert(p, j)
    kd.balance()
    name = f"tree_{species}_s{seed}_a{age}"
    ob_b = make(name + "_branches", BV, BF, BUV0, BUV1)
    me = ob_b.data
    loops = np.zeros(len(me.loops), dtype=np.int64)
    me.loops.foreach_get("vertex_index", loops)
    nrm = np.zeros(len(me.loops) * 3)
    me.corner_normals.foreach_get("vector", nrm) if hasattr(me, "corner_normals") else None
    nrm = nrm.reshape(-1, 3)
    near = np.array([kd.find(BV[v])[1] for v in range(len(BV))])
    dv = deep[near][loops]
    nz = nrm[:, 2]
    sky = np.clip((0.5 + 0.5 * nz) * (1.0 - 0.7 * dv), 0.05, 1.0)
    col = np.stack([sky, np.clip(0.5 - 0.5 * nz, 0, 1), 1.0 - 0.5 * dv, np.ones_like(sky)], -1).astype(np.float32)
    attr = me.color_attributes.new("bake", "FLOAT_COLOR", "CORNER")
    attr.data.foreach_set("color", col.ravel())
    me.color_attributes.active_color = attr
    obs = [ob_b]
    if len(LV):
        obs.append(make(name + "_leaves", LV, LF, LUV0, LUV1, LC, LN))
    tris_b = sum(len(f) - 2 for f in BF)
    tris_l = sum(len(f) - 2 for f in LF)
    info = dict(name=name, height=round(H, 2), trunk_cm=round(200 * float(tl["r"][0]), 1), branch_tris=tris_b,
                leaf_cards=len(LF), leaf_tris=tris_l, masses=k,
                planes=[t[3] for t in (trees or []) if t is not None])
    print("TREE", info)
    if unity:
        path = os.path.join(unity, "Assets", "Art", "Trees", species, name + ".fbx")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        bpy.ops.object.select_all(action="DESELECT")
        for ob in obs:
            ob.select_set(True)
        bpy.context.view_layer.objects.active = obs[0]
        bpy.ops.export_scene.fbx(filepath=path, use_selection=True, object_types={"MESH"}, axis_forward="Z",
                                 axis_up="Y", bake_space_transform=True, apply_unit_scale=True,
                                 apply_scale_options="FBX_SCALE_ALL", mesh_smooth_type="OFF", colors_type="LINEAR",
                                 use_mesh_modifiers=False, add_leaf_bones=False, bake_anim=False, path_mode="STRIP",
                                 embed_textures=False)
        print("FBX", path)
    return info


if __name__ == "__main__":
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    species = argv[0] if argv else "birch"
    seed = int(argv[1]) if len(argv) > 1 else 1
    age = int(argv[2]) if len(argv) > 2 else 30
    quality = float(argv[3]) if len(argv) > 3 else 1.0
    unity = argv[4] if len(argv) > 4 else os.path.join(HERE, "..", "..", "unity")
    build(species, seed, age, quality, unity)
