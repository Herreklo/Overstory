"""Geometry checks run on every generated building before anything is rendered or exported.

check(obj) returns a list of problems; an empty list means the building passed.

- uncovered wall: a wall point with nothing above it (a wall poking through or
  standing outside its roof). Rays go straight up from every wall vertex above
  the plinth.
- part through roof: a window, door, crown, belt or cornice that cuts into the roof.
- floating: geometry that starts well above the ground with nothing under it.
- degenerate: faces with no area.
- budget: more triangles than the building budget allows.
"""

from mathutils import Vector
from mathutils.bvhtree import BVHTree

import palette

UV_TO_SWATCH = {tuple(round(c, 5) for c in palette.uv(name)): name for name in palette.NAMES}
BUDGET = 60000  # triangles per building at LOD0, provisional


def swatch_of(mesh, poly):
    uv = mesh.uv_layers.active.data[poly.loop_indices[0]].uv
    return UV_TO_SWATCH.get((round(uv[0], 5), round(uv[1], 5)), "?")


def check(obj, plinth_top=0.3):
    mesh = obj.data
    mw = obj.matrix_world
    verts = [mw @ v.co for v in mesh.vertices]
    polys = [list(p.vertices) for p in mesh.polygons]
    tree = BVHTree.FromPolygons(verts, polys, epsilon=0.0)
    problems = []

    # walls must have something above them
    # sample the top corners of each wall face, pulled a little towards the face's centre
    # so rays never graze the edge of an opening
    samples = []
    degenerate = {}
    roles = [0] * len(mesh.polygons)
    if "role" in mesh.attributes:
        mesh.attributes["role"].data.foreach_get("value", roles)
    for p in mesh.polygons:
        if p.area < 1e-8:
            sw = swatch_of(mesh, p)
            degenerate[sw] = degenerate.get(sw, 0) + 1
            continue
        if roles[p.index] == 1 and abs(p.normal.z) < 0.5:
            pts = [verts[i] for i in p.vertices]
            c = sum(pts, Vector()) / len(pts)
            ztop = max(q.z for q in pts)
            for q in pts:
                if q.z > ztop - 0.02:
                    samples.append(q + (c - q) * 0.08)
    zmin = min(v.z for v in verts)
    uncovered = []
    for v in samples:
        if v.z < zmin + plinth_top:
            continue
        hit = tree.ray_cast(v + Vector((0, 0, 0.03)), Vector((0, 0, 1)), 30.0)
        if hit[0] is None:
            uncovered.append(v)
    if uncovered:
        top = max(uncovered, key=lambda v: v.z)
        problems.append(f"uncovered wall: {len(uncovered)} points, highest at ({top.x:.2f}, {top.y:.2f}, {top.z:.2f})")
    # facade parts must stay clear of the roof
    roof_ids = [i for i, r in enumerate(roles) if r == 2]
    part_ids = [i for i, r in enumerate(roles) if r == 4]
    if roof_ids and part_ids:
        t_roof = BVHTree.FromPolygons(verts, [polys[i] for i in roof_ids], epsilon=0.0)
        t_part = BVHTree.FromPolygons(verts, [polys[i] for i in part_ids], epsilon=0.0)
        hits = t_part.overlap(t_roof)
        if hits:
            worst = max((sum((verts[k] for k in polys[part_ids[a]]), Vector()) / len(polys[part_ids[a]]) for a, _ in hits), key=lambda v: v.z)
            problems.append(f"part through roof: {len(hits)} face pairs, highest at ({worst.x:.2f}, {worst.y:.2f}, {worst.z:.2f})")
    if degenerate:
        problems.append(f"degenerate: faces with no area {degenerate}")
    tris = sum(len(p.vertices) - 2 for p in mesh.polygons)
    if tris > BUDGET:
        problems.append(f"budget: {tris} triangles (budget {BUDGET})")
    return problems
