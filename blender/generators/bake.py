"""What each face of a part sees, baked into it at assembly.

Nothing in our world can be baked into lightmaps (places change), so the generator writes what
light needs into the mesh itself, under a sky-and-ground ambient light: for every face, a fixed
fan of rays over its hemisphere finds how much of it opens to the sky, how much to open ground
(where the bounce comes from), and how enclosed it is close by (crevices, contact).

The colour attribute "bake" (one value per face, written to its vertices; linear, 0-1):
- r: sky, the share of the hemisphere that sees open sky;
- g: ground, the share that sees open ground (the building stands on z = 0);
- b: openness, one minus the share blocked within half a metre;
- a: reserved (weather exposure, for the coat stack).

The ray fan is the same for every face, so the bake is deterministic. Neighbours are not in the
bake: a part only knows itself; contact between buildings is left to screen-space occlusion.
"""

import math

from mathutils import Vector
from mathutils.bvhtree import BVHTree

RAYS = 14  # cosine-weighted directions over the hemisphere
REACH = 14.0  # metres a ray looks for something in the way
NEAR = 0.5  # metres within which a hit counts as enclosing
LIFT = 0.004  # start each ray just off the surface

# A fixed spiral of cosine-weighted directions about +z (golden-angle spiral over the disc, lifted).
_FAN = []
for i in range(RAYS):
    r = math.sqrt((i + 0.5) / RAYS)
    a = i * 2.399963229728653
    x, y = r * math.cos(a), r * math.sin(a)
    _FAN.append((x, y, math.sqrt(max(0.0, 1.0 - x * x - y * y))))


def _basis(n):
    """Two tangents completing n into an orthonormal frame."""
    t = Vector((0, 0, 1)) if abs(n.z) < 0.9 else Vector((1, 0, 0))
    u = n.cross(t).normalized()
    return u, n.cross(u)


def bake(obj):
    """Write the "bake" colour attribute on obj's mesh. Returns the mean sky value, for reports.

    Each face is sampled inside itself (its centre and halfway to each corner) and its vertices take
    the face's mean. Corners alone would lie: a long clapboard course has vertices only at its ends,
    tucked under the corner boards, and would come out black along its whole length.
    """
    mesh = obj.data
    verts = [v.co.copy() for v in mesh.vertices]
    polys = [list(p.vertices) for p in mesh.polygons]
    tree = BVHTree.FromPolygons(verts, polys, epsilon=0.0)
    out = [(1.0, 0.0, 1.0)] * len(verts)
    total = 0.0
    for p in mesh.polygons:
        n = p.normal.copy()
        u, w = _basis(n)
        centre = p.center
        dirs = [u * x + w * y + n * z for x, y, z in _FAN]
        corners = [verts[vi] for vi in p.vertices]
        step = max(1, len(corners) // 4)
        samples = [centre] + [c.lerp(centre, 0.5) for c in corners[::step]]
        sky = ground = near = 0
        for s in samples:
            o = s + n * LIFT
            for d in dirs:
                hit, _, _, dist = tree.ray_cast(o, d, REACH)
                if hit is not None:
                    if dist < NEAR:
                        near += 1
                    continue
                if d.z < -1e-4 and o.z > 0.0 and -o.z / d.z < REACH:
                    ground += 1
                else:
                    sky += 1
        k = float(len(samples) * RAYS)
        value = (sky / k, ground / k, 1.0 - near / k)
        total += value[0]
        for vi in p.vertices:
            out[vi] = value
    attr = mesh.color_attributes.get("bake") or mesh.color_attributes.new("bake", "FLOAT_COLOR", "POINT")
    flat = []
    for r, g, b in out:
        flat.extend((r, g, b, 1.0))
    attr.data.foreach_set("color", flat)
    mesh.color_attributes.active_color = attr
    return total / max(1, len(mesh.polygons))
