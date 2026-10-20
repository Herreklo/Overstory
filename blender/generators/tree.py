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
# holds whatever the species' tip size); twig_r: the thinnest branch drawn as a tube (thinner ones are in the sprays);
# bark: one bark tile round and along (m); grow_to: how long the timeline is grown (it contains every younger age).
PARTS = {
    "birch": dict(card=(0.60, 0.38), cells=4, per_node=2, along=1, droop=0.7, leaf_years=25, leaf_tips=24, twig_r=0.004,
                  bark=(0.30, 0.60), max_cards=6000, grow_to=80),
    "spruce": dict(card=(0.60, 0.40), cells=4, per_node=2, droop=0.25, leaf_years=7, leaf_tips=30, twig_r=0.004,
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
    return dict(parent=t["parent"], start=t["start"].astype(np.float64), end=t["end"].astype(np.float64),
                born=t["born"], order=t["order"], r=drawn_radius(pipe), alive=alive,
                tips=(pipe / G.SPECIES[species]["tip_radius"]) ** G.SPECIES[species]["pipe"])


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
    return 10 if r >= 0.08 else 8 if r >= 0.03 else 6 if r >= 0.012 else 4 if r >= 0.005 else 3


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


def branch_mesh(tl, parts):
    """Vertices, faces, per-loop UV0 and UV1, and the chain points (for the bake), for every branch thick enough."""
    start, end, r = tl["start"], tl["end"], tl["r"]
    tile_round, tile_along = parts["bark"]
    V, F, UV0, UV1 = [], [], [], []
    samples = []                                         # (point, radius) along branches, for the bake
    for c in chains(tl):
        if r[c[0]] < parts["twig_r"]:
            continue
        pts = np.array([start[c[0]]] + [end[i] for i in c])
        rad = np.array([r[c[0]]] + [r[i] for i in c])
        # stop where the branch gets thinner than the thinnest drawn: the sprays carry it on
        stop = len(pts)
        for k in range(1, len(pts)):
            if rad[k] < parts["twig_r"]:
                stop = k + 1
                break
        pts, rad = pts[:stop], rad[:stop]
        if len(pts) < 2:
            continue
        keep = simplify(pts, rad, bend=0.05 if rad[0] >= 0.04 else 0.10 if rad[0] >= 0.012 else 0.14)
        pts, rad = pts[keep], rad[keep]
        if c[0] == 0:
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

def leafy(tl, parts, age, seed):
    """The nodes that carry a spray at the age: the living shoots younger than the species keeps leaves on, thin
    enough, at most max_cards of them (a seeded choice if there are more)."""
    ok = tl["alive"] & (age - tl["born"] < parts["leaf_years"]) & (tl["tips"] <= parts["leaf_tips"])
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


def leaf_mesh(tl, parts, age, seed, H, species):
    ids = leafy(tl, parts, age, seed)
    start, end = tl["start"], tl["end"]
    L, W = parts["card"]
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
        limb = limbs(tl)[ids]
        k = int(min(5, max(3, round(3 + (H - 6) / 6))))
        k = min(k, len(set(limb.tolist())))
        which = masses(centres, limb, max(k, 1))
    trees = hulls(np.vstack([centres, end[ids] + d * L]), np.concatenate([which, which]), max(k, 1))
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
        n_shade = nrm * 0.85 + out * 0.15
        n_shade /= np.linalg.norm(n_shade)
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
        opn = float(1.0 - 0.6 * depth)
        rank = 0.55 * h01(seed, i, 4) + 0.45 * depth          # the season's order: the most exposed first, then seeded
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
            V.extend([foot - side * W / 2, foot + side * W / 2, foot + side * W / 2 + d[j] * L,
                      foot - side * W / 2 + d[j] * L])
            F.append((b, b + 1, b + 2, b + 3))
            cell = int(h01(seed, i, 2, c) * parts["cells"]) % parts["cells"]
            cx, cy = (cell % 2) * 0.5, 1.0 - (cell // 2) * 0.5 - 0.5
            u0, u1 = cx + 0.5 * 0.2, cx + 0.5 * 0.8
            if h01(seed, i, 3, c) < 0.5:
                u0, u1 = u1, u0                                 # mirrored
            UV0.extend([(u0, cy), (u1, cy), (u1, cy + 0.5), (u0, cy + 0.5)])
            UV1.extend([(rank, h01(seed, i, 5, c))] * 4)
            NR.extend([n_shade] * 4)
            COL.extend([(sky, ground, opn, 1.0)] * 4)
    return np.array(V), F, UV0, UV1, NR, COL, trees, which


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
    LV, LF, LUV0, LUV1, LN, LC, trees, which = leaf_mesh(tl, parts, age, seed, H, species)
    k = int(which.max()) + 1 if which is not None and len(which) else 0
    BV, BF, BUV0, BUV1, samples = branch_mesh(tl, parts)
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
