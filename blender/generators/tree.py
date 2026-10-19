"""Trees, by species, built the way painted game trees are: a trunk with a few branches, and a crown
of leaf-cluster cards.

build(params, seed) makes one tree at its mature size, pivot at the foot of the trunk. The crown is
about a hundred cards, each a soft, ragged cluster of leaves cut out by the shader (the card's
coordinates ride in a second UV layer, offset by one so the shader knows a card from a wall). Every
card's normals point out from the crown's centre, so light models the whole crown as one rounded mass
(the soft-foliage method in docs/research/nature.md), and cards deep inside the crown see less sky and
come out darker (bake.py). Unity scales each tree by its age: planting is a fact, size follows from it.

Species (mature height, metres):
- birch: tall, narrow, loose, light; October yellow.
- rowan: small, rounded; October red.
- sycamore: broad, dense, the big garden tree; October amber.
- spruce: a dark cone in tiers, the same all year.
"""

import math
import random

from mathutils import Vector

from kit import Builder, Frame, WORLD

SPECIES = {
    # crown: (bottom, top) as shares of the height; width: crown half-width as a share of the height
    "birch": dict(height=14.0, trunk=0.19, crown=(0.32, 1.0), width=0.2, cards=90, card=1.9, branches=4, leaf="leaf_birch"),
    "rowan": dict(height=8.0, trunk=0.15, crown=(0.3, 0.98), width=0.3, cards=70, card=1.5, branches=4, leaf="leaf_rowan"),
    "sycamore": dict(height=15.0, trunk=0.33, crown=(0.26, 1.0), width=0.38, cards=130, card=2.6, branches=5, leaf="leaf_sycamore"),
    "spruce": dict(height=17.0, trunk=0.24, crown=(0.06, 1.0), width=0.21, cards=0, card=0, branches=0, leaf="leaf_spruce"),
}


def name(variant):
    return f"kit_tree_{variant}_lod0"


def _branch(b, base, direction, length, r0, r1):
    d = direction.normalized()
    t = Vector((0, 0, 1)) if abs(d.z) < 0.95 else Vector((1, 0, 0))
    u = d.cross(t).normalized()
    n = d.cross(u).normalized()
    b.prism(Frame(base, u, d, n), 0, 0, 0.0, length, r0, r1, 6, "bark")


def build(params, seed=0):
    """params: a species from SPECIES. Returns the tree object."""
    import palette

    sp = SPECIES[params]
    rng = random.Random(seed)
    b = Builder()
    H = sp["height"]
    c0, c1 = sp["crown"][0] * H, sp["crown"][1] * H
    half = H * sp["width"]
    centre = Vector((0, 0, (c0 + c1) / 2))
    axes = Vector((half, half, (c1 - c0) / 2))

    # trunk, and a few branches reaching into the crown
    trunk_top = c0 + (c1 - c0) * 0.55
    b.prism(WORLD, 0, 0, 0.0, trunk_top, sp["trunk"], sp["trunk"] * 0.4, 8, "bark")
    for k in range(sp["branches"]):
        z = c0 + (trunk_top - c0) * (0.15 + 0.7 * k / max(1, sp["branches"] - 1))
        ang = k * 2.4 + rng.uniform(-0.4, 0.4)
        d = Vector((math.cos(ang), math.sin(ang), rng.uniform(0.7, 1.3)))
        _branch(b, Vector((0, 0, z)), d, half * rng.uniform(0.7, 1.0), sp["trunk"] * 0.45, sp["trunk"] * 0.12)

    first_leaf = len(b.faces)
    cards = []  # (face index, centre) for the second UV layer
    if params == "spruce":
        tiers = 7
        for i in range(tiers):
            t0 = i / tiers
            z0 = c0 + (c1 - c0) * t0 * 0.9
            z1 = z0 + (c1 - c0) * 0.3
            r = half * (1.0 - t0 * 0.85) * rng.uniform(0.92, 1.08)
            b.prism(WORLD, 0, 0, z0, z1, r, 0.0, 14, sp["leaf"], phase=rng.random())
    else:
        for i in range(sp["cards"]):
            while True:
                q = Vector((rng.uniform(-1, 1), rng.uniform(-1, 1), rng.uniform(-1, 1)))
                if q.length <= 1.0:
                    break
            q = q.normalized() * (0.35 + 0.65 * q.length ** 0.5)  # most cards near the crown's surface
            c = centre + Vector((q.x * axes.x, q.y * axes.y, q.z * axes.z))
            # each card faces roughly out of the crown, turned at random about that direction
            out = (c - centre).normalized() if (c - centre).length > 1e-3 else Vector((0, 0, 1))
            out = (out + Vector((rng.uniform(-0.6, 0.6), rng.uniform(-0.6, 0.6), rng.uniform(-0.3, 0.6)))).normalized()
            t = Vector((0, 0, 1)) if abs(out.z) < 0.9 else Vector((1, 0, 0))
            u = out.cross(t).normalized()
            v = out.cross(u).normalized()
            spin = rng.uniform(0, math.pi)
            u, v = u * math.cos(spin) + v * math.sin(spin), v * math.cos(spin) - u * math.sin(spin)
            s = sp["card"] * rng.uniform(0.75, 1.25) / 2
            quad = [c - u * s - v * s, c + u * s - v * s, c + u * s + v * s, c - u * s + v * s]
            b.face(quad, sp["leaf"], outward=c - out)          # the face towards the outside
            cards.append(len(b.faces) - 1)
            b.face(list(reversed(quad)), sp["leaf"], outward=c + out)  # and the face towards the inside
            cards.append(len(b.faces) - 1)
    obj = b.build(name(params), palette.material())
    mesh = obj.data

    # card coordinates in a second UV layer, offset by one (walls and roofs read zero there)
    cardlayer = mesh.uv_layers.new(name="Card")
    corner_uv = [(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)]
    for p in mesh.polygons:
        for k, li in enumerate(p.loop_indices):
            cardlayer.data[li].uv = (corner_uv[k % 4][0] + 1.0, corner_uv[k % 4][1] + 1.0) if p.index >= first_leaf and params != "spruce" else (0.0, 0.0)

    # soft foliage: crown normals point out of the crown's envelope
    normals = []
    for p in mesh.polygons:
        for li in p.loop_indices:
            if p.index < first_leaf:
                normals.append(tuple(p.normal))
                continue
            v = mesh.vertices[mesh.loops[li].vertex_index].co
            e = Vector(((v.x - centre.x) / axes.x ** 2, (v.y - centre.y) / axes.y ** 2, (v.z - centre.z) / axes.z ** 2))
            n = (e.normalized() * 0.9 + p.normal * 0.1).normalized() if params != "spruce" else (e.normalized() * 0.6 + p.normal * 0.4).normalized()
            normals.append(tuple(n))
    for p in mesh.polygons:
        p.use_smooth = True
    mesh.normals_split_custom_set(normals)
    return obj
