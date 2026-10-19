"""Trees, by species, built as a painter would simplify them.

build(params, seed) makes one tree at its mature size, pivot at the foot of the trunk. A crown is a
few soft masses, not leaves; every vertex of a crown carries a normal pointing out from the crown's
centre, so light models the whole crown as one rounded form (the soft-foliage method in
docs/research/nature.md). Unity scales each tree by its age: planting is a fact, size follows from it.

Species (mature height, metres):
- birch: tall and narrow, loose, light; October yellow.
- rowan: small, rounded; October red.
- sycamore: broad, dense, the big garden tree; October amber.
- spruce: a dark cone in tiers, the same all year.
"""

import math
import random

from mathutils import Vector

from kit import Builder, WORLD

SPECIES = {
    # crown: (bottom, top) as shares of the height; width: the crown's half-width as a share of the height
    "birch": dict(height=14.0, trunk=0.2, crown=(0.3, 1.0), width=0.2, lumps=22, lump=0.16, leaf="leaf_birch"),
    "rowan": dict(height=8.0, trunk=0.16, crown=(0.28, 0.98), width=0.3, lumps=18, lump=0.2, leaf="leaf_rowan"),
    "sycamore": dict(height=15.0, trunk=0.34, crown=(0.24, 1.0), width=0.38, lumps=30, lump=0.17, leaf="leaf_sycamore"),
    "spruce": dict(height=17.0, trunk=0.24, crown=(0.06, 1.0), width=0.2, lumps=0, lump=0, leaf="leaf_spruce"),
}


def name(variant):
    return f"kit_tree_{variant}_lod0"


def _icosphere(subdiv):
    """Unit icosphere: vertices and triangles."""
    t = (1 + math.sqrt(5)) / 2
    vs = [Vector(v).normalized() for v in ((-1, t, 0), (1, t, 0), (-1, -t, 0), (1, -t, 0), (0, -1, t), (0, 1, t),
                                           (0, -1, -t), (0, 1, -t), (t, 0, -1), (t, 0, 1), (-t, 0, -1), (-t, 0, 1))]
    fs = [(0, 11, 5), (0, 5, 1), (0, 1, 7), (0, 7, 10), (0, 10, 11), (1, 5, 9), (5, 11, 4), (11, 10, 2), (10, 7, 6), (7, 1, 8),
          (3, 9, 4), (3, 4, 2), (3, 2, 6), (3, 6, 8), (3, 8, 9), (4, 9, 5), (2, 4, 11), (6, 2, 10), (8, 6, 7), (9, 8, 1)]
    for _ in range(subdiv):
        cache, out = {}, []

        def mid(a, b):
            k = (min(a, b), max(a, b))
            if k not in cache:
                vs.append(((vs[a] + vs[b]) / 2).normalized())
                cache[k] = len(vs) - 1
            return cache[k]

        for a, b, c in fs:
            ab, bc, ca = mid(a, b), mid(b, c), mid(c, a)
            out += [(a, ab, ca), (b, bc, ab), (c, ca, bc), (ab, bc, ca)]
        fs = out
    return vs, fs


SPHERE = _icosphere(1)


def build(params, seed=0):
    """params: a species from SPECIES. Returns the tree object; its crown's normals are soft."""
    import palette

    sp = SPECIES[params]
    rng = random.Random(seed)
    b = Builder()
    H = sp["height"]
    c0, c1 = sp["crown"][0] * H, sp["crown"][1] * H
    half = H * sp["width"]
    centre = Vector((0, 0, (c0 + c1) / 2))
    axes = Vector((half, half, (c1 - c0) / 2))  # the crown's envelope, an ellipsoid
    # the trunk, tapering, well up into the crown
    b.prism(WORLD, 0, 0, 0.0, c0 + (c1 - c0) * 0.6, sp["trunk"], sp["trunk"] * 0.35, 8, "bark")
    first_leaf = len(b.faces)
    if params == "spruce":
        tiers = 7
        for i in range(tiers):
            t0 = i / tiers
            z0 = c0 + (c1 - c0) * t0 * 0.9
            z1 = z0 + (c1 - c0) * 0.3
            r = half * (1.0 - t0 * 0.85) * rng.uniform(0.92, 1.08)
            b.prism(WORLD, 0, 0, z0, z1, r, 0.0, 14, sp["leaf"], phase=rng.random())
    else:
        vs, fs = SPHERE
        for i in range(sp["lumps"]):
            # a point inside the envelope, pushed towards its surface so the outline is full
            while True:
                q = Vector((rng.uniform(-1, 1), rng.uniform(-1, 1), rng.uniform(-1, 1)))
                if q.length <= 1.0:
                    break
            q = q.normalized() * (0.55 + 0.4 * q.length)
            lc = centre + Vector((q.x * axes.x, q.y * axes.y, q.z * axes.z)) * 0.8
            r = H * sp["lump"] * rng.uniform(0.75, 1.25)
            jitter = [rng.uniform(0.82, 1.15) for _ in vs]  # each lump irregular, so the silhouette breaks
            for f in fs:
                pts = [lc + vs[k] * r * jitter[k] for k in f]
                b.face(pts, sp["leaf"], outward=lc)
    obj = b.build(name(params), palette.material())
    # soft foliage: crown normals are the envelope's own, blended a little with the face's, so light
    # models the whole crown as one rounded form while its edge stays broken
    mesh = obj.data
    normals = []
    for p in mesh.polygons:
        for li in p.loop_indices:
            if p.index < first_leaf:
                normals.append(tuple(p.normal))
                continue
            v = mesh.vertices[mesh.loops[li].vertex_index].co
            e = Vector(((v.x - centre.x) / axes.x ** 2, (v.y - centre.y) / axes.y ** 2, (v.z - centre.z) / axes.z ** 2))
            n = (e.normalized() * 0.85 + p.normal * 0.15).normalized()
            normals.append(tuple(n))
    for p in mesh.polygons:
        p.use_smooth = True
    mesh.normals_split_custom_set(normals)
    return obj
