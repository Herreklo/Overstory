"""A rock part of the Holm tip's kit (kit.json), built the street's way: its levels as geom.to_object builds a house's.

    Blender -b --factory-startup -P blender/parts/rock/kit/part.py -- --part slab-block --out cache/rock/kit/gen/slab-block

A part is one or more plates parted along the foliation (kit.json `plates`), each a convex body: the intersection of
its faces' half-spaces, each face a plane of the tip's own (its foliation, joints and sheeting, from the fixture)
folded back into a few facets, so it reads as a few chunky planes and never one flat panel, and each plate's faces
stepped proud or back of the block's. The plates are joined into one body. Its convex edges are rounded by what wore
them (kit.json `wear`, per face), one round per edge by a bevel's weight, its re-entrant ones left sharp, at the
near level's segments, fewer at the street's and none at the city level, which is the block's outline alone.

Every level's faces sit on the same charts: a face's chart is its plane's in its plate, and a chamfer's faces go to
the face whose plane they are nearest, projected onto it, so the page is one and is baked once from the near level.
A chart's u runs along the foliation's trace on its face, the rock's grain, as a board's runs along the board.
Writes, as house.py does (so the street's bake helpers and its Unity import and materials take a rock unchanged):
house-near.fbx, house-street.fbx, house-city.fbx (one object a level, `<level>_rock`), house.blend, house.json.
Fails over a level's budget (street.json's, by the part's surface: a square metre of rock costs what one of house
does) unless ROCK_OVER=1.
"""

import json
import math
import os
import sys

import bmesh
import bpy
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "blender", "parts", "street"))
sys.path.insert(0, os.path.join(ROOT, "blender", "resolver"))
import geom as G  # noqa: E402
import hashing as HS  # noqa: E402


def args():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    return {argv[i].lstrip("-"): argv[i + 1] for i in range(0, len(argv) - 1, 2)}


def normal(dip, toward):
    """The upward normal of a plane dipping `dip` degrees toward the compass bearing `toward` (x east, y north)."""
    d, a = math.radians(dip), math.radians(toward)
    return Vector((math.sin(d) * math.sin(a), math.sin(d) * math.cos(a), math.cos(d)))


def basis(n):
    """A face's own frame: along its strike, up its dip (or north on a level face), and its normal."""
    s = Vector((0, 0, 1)).cross(n)
    s = s.normalized() if s.length > 1e-6 else Vector((1, 0, 0))
    return s, n.cross(s).normalized()


class Plane:
    def __init__(self, face, n, p, name=None, kind=None, plate=0):
        self.face, self.n, self.p = face, n.normalized(), p
        self.name, self.kind, self.plate = name or face, kind, plate


def families(fix):
    fam = {f["name"]: f for f in fix["rock"]["joints"]}
    fam["foliation"] = fix["rock"]["foliation"]
    return fam


def face_normal(f, fam):
    pl = f["plane"]
    n = normal(fam[pl]["dip"], fam[pl]["dipToward"]) if isinstance(pl, str) else normal(*pl)
    return -n if f.get("flip") else n


def with_facets(f, n, p, chart, kind, plate, facets=True):
    """A face's plane and its facets', each folded back beyond its line."""
    out = [Plane(chart, n, p, f["name"], kind, plate)]
    e_s, e_d = basis(n)
    for fc in f["facets"] if facets else []:
        t = math.radians(fc["dir"])
        u = e_s * math.cos(t) + e_d * math.sin(t)
        a = math.radians(fc["tilt"])
        out.append(Plane(chart, n * math.cos(a) + u * math.sin(a), p + u * fc["fold"], f["name"], kind, plate))
    return out


LAP = 5e-4  # m: how far an inner plate runs into its neighbour


def plates_of(part, fix, K):
    """Each plate's planes, in the part's frame: its origin on the ground under it, its centre at `centre`, so the
    part stands as a house does, its base face sunk where it is below 0. A part without plates is one."""
    fam, c = families(fix), Vector(part["centre"])
    faces = {f["name"]: f for f in part["faces"]}
    pl = part.get("plates")
    if not pl:
        return [[q for f in part["faces"] for q in with_facets(f, face_normal(f, fam), c + face_normal(f, fam) * f["at"], f["name"], f["wear"], 0)]]
    lo_f, hi_f = (faces[k] for k in pl["along"])
    nf = face_normal(hi_f, fam)
    span = lo_f["at"] + hi_f["at"]
    t = [x * span / sum(pl["t"]) for x in pl["t"]]
    edges = [-lo_f["at"] + sum(t[:k]) for k in range(len(t) + 1)]
    out = []
    for k in range(len(t)):
        planes = []
        sh = pl["shift"][k] if k < len(pl["shift"]) else {}
        for f in part["faces"]:
            n = face_normal(f, fam)
            chart = f"{f['name']}.{k}"
            # inner plates overlap their neighbours by LAP: the exact union drops plates that only touch on a plane
            if f is lo_f:
                outer = k == 0
                planes += with_facets(f, -nf, c + nf * (edges[k] - (0 if outer else LAP)), chart, f["wear"] if outer else "parting", k, outer)
            elif f is hi_f:
                outer = k == len(t) - 1
                planes += with_facets(f, nf, c + nf * (edges[k + 1] + (0 if outer else LAP)), chart, f["wear"] if outer else "parting", k, outer)
            else:
                planes += with_facets(f, n, c + n * (f["at"] + sh.get(f["name"], 0.0)), chart, f["wear"], k)
        # a plate's own fresh breaks (`breaks`, one list a plate): faces of its own, cut through the block's
        for f in (pl.get("breaks", [])[k] if k < len(pl.get("breaks", [])) else []):
            n = face_normal(f, fam)
            planes += with_facets(f, n, c + n * f["at"], f"{f['name']}.{k}", f["wear"], k)
        out.append(planes)
    return out


def outline_of(part, fix):
    """The block's own faces, unstepped and unfolded: the city level's body."""
    fam, c = families(fix), Vector(part["centre"])
    return [Plane(f["name"], face_normal(f, fam), c + face_normal(f, fam) * f["at"], f["name"], f["wear"])
            for f in part["faces"]]


def hull(planes):
    """The convex body the planes bound: a big box cut by each, its cut filled."""
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=12.0)
    tag = bm.faces.layers.int.new("plane")
    for f in bm.faces:
        f[tag] = -1
    for k, pl in enumerate(planes):
        geom = list(bm.verts) + list(bm.edges) + list(bm.faces)
        r = bmesh.ops.bisect_plane(bm, geom=geom, dist=1e-6, plane_co=pl.p, plane_no=pl.n, clear_outer=True)
        cut = [e for e in r["geom_cut"] if isinstance(e, bmesh.types.BMEdge)]
        if not cut:
            continue
        new = bmesh.ops.edgenet_fill(bm, edges=cut)["faces"] or bmesh.ops.contextual_create(bm, geom=cut)["faces"]
        for f in new:
            f[tag] = k
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
    bm.normal_update()
    left = [f for f in bm.faces if f[tag] < 0]
    if left:
        raise SystemExit(f"[rock] the planes leave the box open ({len(left)} of its faces)")
    return bm


def union(bodies):
    """The plates joined into one closed body (an exact boolean union; they overlap by LAP, see plates_of), its coplanar faces merged and any face that
    is not convex cut into triangles."""
    objs = []
    for k, bm in enumerate(bodies):
        me = bpy.data.meshes.new(f"plate{k}")
        bm.to_mesh(me)
        bm.free()
        o = bpy.data.objects.new(f"plate{k}", me)
        bpy.context.scene.collection.objects.link(o)
        objs.append(o)
    base = objs[0]
    for o in objs[1:]:
        mod = base.modifiers.new("join", "BOOLEAN")
        mod.operation, mod.solver, mod.object = "UNION", "EXACT", o
    dg = bpy.context.evaluated_depsgraph_get()
    out = bmesh.new()
    out.from_mesh(base.evaluated_get(dg).to_mesh())
    base.evaluated_get(dg).to_mesh_clear()
    for o in objs:
        me = o.data
        bpy.data.objects.remove(o)
        bpy.data.meshes.remove(me)
    bmesh.ops.remove_doubles(out, verts=out.verts, dist=1e-6)
    bmesh.ops.dissolve_degenerate(out, dist=1e-5, edges=out.edges)
    bmesh.ops.dissolve_limit(out, angle_limit=math.radians(0.01), verts=out.verts, edges=out.edges)
    out.normal_update()
    bent = [f for f in out.faces if len(f.verts) > 3 and not convex_face(f)]
    if bent:
        bmesh.ops.triangulate(out, faces=bent, quad_method="BEAUTY", ngon_method="EAR_CLIP")
    out.normal_update()
    return out


def convex_face(f):
    n = f.normal
    vs = [v.co for v in f.verts]
    return all(n.dot((vs[(i + 1) % len(vs)] - vs[i]).cross(vs[(i + 2) % len(vs)] - vs[(i + 1) % len(vs)])) > -1e-9
               for i in range(len(vs)))


SLIVER = 1e-4  # m²: a face of no area (1 cm², below any level's sight; the join of overlapping leaves leaves such)


def tag_faces(bm, planes):
    """Each face's plane: the one it lies on (the first plate's, where two plates share it)."""
    out = {}
    for f in sorted(bm.faces, key=lambda f: f.calc_area() < SLIVER):
        c, n = f.calc_center_median(), f.normal
        if f.calc_area() < SLIVER:  # a sliver the join leaves, of no area: its neighbour's plane
            out[f.index] = next((out[g.index] for e in f.edges for g in e.link_faces if g.index in out), 0)
            continue
        k = next((k for k, pl in enumerate(planes) if n.dot(pl.n) > 0.9999 and abs((c - pl.p).dot(pl.n)) < 2e-4), None)
        if k is None:
            raise SystemExit(f"[rock] a face of the joined plates lies on none of their planes (at {tuple(round(x, 3) for x in c)}, facing {tuple(round(x, 3) for x in n)}, {len(f.verts)} corners, {f.calc_area():.4f} m²)")
        out[f.index] = k
    return out


def convex_edge(e):
    """Whether the edge turns outward: (n1 x n2) along the edge's way round its first face."""
    f1, f2 = e.link_faces
    l = next(l for l in e.link_loops if l.face is f1)
    d = l.link_loop_next.vert.co - l.vert.co
    return f1.normal.cross(f2.normal).dot(d) > 1e-9


def edge_rounds(bm, tags, planes, outline, K, pid):
    """Each edge's round in metres, by the wear of the two faces it parts (kit.json wear), seeded per face pair:
    the larger of the two kinds', or a face of an `own` kind's own; none where a face folds or the body turns
    inward, nor in the ground. Never more than capShare of the block's least width."""
    W = K["wear"]
    span = [-min((v.co - pl.p).dot(pl.n) for v in bm.verts) for pl in outline]
    cap = W["capShare"] * min(span)
    out = {}
    bm.edges.index_update()
    for e in bm.edges:
        if len(e.link_faces) != 2:
            out[e.index] = 0.0
            continue
        a, b = (planes[tags[f.index]] for f in e.link_faces)
        if any(f.calc_area() < SLIVER for f in e.link_faces) or a.face == b.face or "ground" in (a.kind, b.kind) or not convex_edge(e):
            out[e.index] = 0.0
            continue
        u = HS.unit(HS.h(K["world"], pid, "round", *sorted((a.face, b.face))))
        width = lambda k: W[k][0] + (W[k][1] - W[k][0]) * u  # noqa: E731
        own = [k for k in (a.kind, b.kind) if k in W["own"]]
        w = min(width(k) for k in own) if own else max(width(a.kind), width(b.kind))
        out[e.index] = min(w, cap, W["reachShare"] * min(reach(e, f) for f in e.link_faces))
    return out, cap


def reach(e, f):
    """How far the face runs back from the edge before its next corner: a round may take only part of it, so
    rounds on a stepped body never cross one another. A corner on the edge's own line (where the join of the
    plates split it) is no corner across the face."""
    a, b = e.verts[0].co, e.verts[1].co
    d = (b - a).normalized()
    off = [((v.co - a) - d * (v.co - a).dot(d)).length for v in f.verts if v not in e.verts]
    off = [x for x in off if x > 2 * LAP]
    return min(off) if off else 0.0


def level_mesh(bm, rounds, segments, profile):
    """The hull bevelled by its edges' rounds (a bevel's weight per edge), as a new mesh."""
    me = bpy.data.meshes.new("hull")
    bm.to_mesh(me)
    wmax = max(list(rounds.values()) + [1e-6])
    att = me.attributes.new("bevel_weight_edge", "FLOAT", "EDGE")
    att.data.foreach_set("value", [rounds[i] / wmax for i in range(len(me.edges))])
    obj = bpy.data.objects.new("hull", me)
    bpy.context.scene.collection.objects.link(obj)
    if segments:
        mod = obj.modifiers.new("round", "BEVEL")
        mod.limit_method = "WEIGHT"
        mod.offset_type = "OFFSET"
        mod.width = wmax
        mod.segments = segments
        mod.profile = profile
        mod.use_clamp_overlap = False  # each round is held inside its faces already (reach)
        mod.harden_normals = False
    dg = bpy.context.evaluated_depsgraph_get()
    ev = obj.evaluated_get(dg)
    out = bmesh.new()
    out.from_mesh(ev.to_mesh())
    ev.to_mesh_clear()
    bpy.data.objects.remove(obj)
    bpy.data.meshes.remove(me)
    out.normal_update()
    return out


def owner(face, planes):
    """The plane a level's face belongs to: the one it lies on, else (a round's face) the one it is nearest to."""
    c, n = face.calc_center_median(), face.normal
    for k, pl in enumerate(planes):
        if n.dot(pl.n) > 0.9999 and abs((c - pl.p).dot(pl.n)) < 1e-4:
            return k, False
    return max(range(len(planes)), key=lambda k: n.dot(planes[k].n)), True


class Piece:
    def __init__(self, index, pid):
        self.index, self.id = index, pid


def grain(n, nf):
    """A face's own frame with u along the foliation's trace on it (the rock's grain), v across; a face that lies in
    the foliation takes its strike."""
    t = n.cross(nf)
    if t.length < 0.2:
        return basis(n)
    u = t.normalized()
    if u.z < -1e-6 or (abs(u.z) <= 1e-6 and u.x < 0):
        u = -u
    return u, n.cross(u).normalized()


def main():
    a = args()
    pid, out = a["part"], os.path.abspath(a["out"])
    os.makedirs(out, exist_ok=True)
    K = json.load(open(os.path.join(HERE, "kit.json")))
    S = json.load(open(os.path.join(ROOT, K["street"])))
    fix = json.load(open(os.path.join(ROOT, K["fixture"])))
    part = K["parts"][pid]
    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o)
    plates = plates_of(part, fix, K)
    planes = [pl for ps in plates for pl in ps]
    outline = outline_of(part, fix)
    bm = union([hull(ps) for ps in plates])
    tags = tag_faces(bm, planes)
    rounds, cap = edge_rounds(bm, tags, planes, outline, K, pid)
    nf = normal(fix["rock"]["foliation"]["dip"], fix["rock"]["foliation"]["dipToward"])
    # a chart is a face's plane in its plate: projected onto that plane unfolded, so its folds are no seams
    face_plane = {}
    for pl in planes:
        face_plane.setdefault(pl.face, pl)
    frames = {f: grain(pl.n, nf) for f, pl in face_plane.items()}

    def proj(face, v):
        e_u, e_v = frames[face]
        return v.dot(e_u), v.dot(e_v)

    levels = {}
    for lv, L in K["levels"].items():
        whole = L.get("folds", True)
        if whole:
            m = level_mesh(bm, rounds, L.get("segments", 0), L.get("profile", 0.5))
        else:
            m = hull(outline)
        faces = []
        for f in m.faces:
            k, rnd = owner(f, planes)
            if planes[k].kind == "ground":
                continue  # in the ground: never seen
            faces.append((planes[k].face, [v.co.copy() for v in f.verts], rnd, f.calc_area(), whole))
        levels[lv] = faces
        m.free()
    # each face's chart spans the near and street levels' faces on it; the city's outline is laid on those charts
    # as it falls, held inside them
    span = {}
    for faces in levels.values():
        for face, pts, rnd, area, whole in faces:
            if not whole:
                continue
            for p in pts:
                u, v = proj(face, p)
                lo, hi = span.get(face, ((u, v), (u, v)))
                span[face] = ((min(lo[0], u), min(lo[1], v)), (max(hi[0], u), max(hi[1], v)))
    charts = G.Charts()
    P = K["page"]
    for face, (lo, hi) in sorted(span.items()):
        down = face_plane[face].n.z < -0.5
        charts(face, hi[0] - lo[0], hi[1] - lo[1], P["down"] if down else 1.0)
    rects, fill, px, size = charts.fit(P)
    surface = sum(area for face, pts, rnd, area, whole in levels["near"])
    pc = Piece(0, f"rock/{pid}")
    seed = HS.unit(HS.h(K["world"], pid, "seed"))

    objs, counts = {}, {}
    for lv, faces in levels.items():
        fl = []
        for face, pts, rnd, area, whole in faces:
            if face not in span:
                face = min(span, key=lambda c: -face_plane[c].n.dot(face_plane[face].n))
            (lo, hi) = span[face]
            cuv = [(min(max(proj(face, p)[0], lo[0]), hi[0]) - lo[0], min(max(proj(face, p)[1], lo[1]), hi[1]) - lo[1]) for p in pts]
            fl.append((pc, G.Face(pts, cuv, face, cuv, arris=rnd)))
        o = G.to_object(f"{lv}_rock", fl, lambda _pc: Matrix.Identity(4), lambda _pc, w: w, rects, size,
                        lambda _pc, f, w: [1.0 if f.arris else 0.0, seed, 0.0, 1.0])
        objs[lv] = o
        counts[lv] = G.tris_of(o)
    # the street's budgets by surface: near and street by the house's triangles a square metre, the city's too
    m2 = S["budgetSurfaceM2"]["m2"]
    budgets = {lv: [round(b * surface / m2) for b in S["levels"][lv]["budgetTris"]] for lv in ("near", "street", "city")}
    over = [lv for lv in budgets if counts[lv] > budgets[lv][1]]
    print(f"[rock] {pid}: triangles {counts}; budgets {budgets} for {surface:.1f} m²; page {size} px at {px} px/m, "
          f"filled {fill:.2f}; rounds {sorted({round(r, 3) for r in rounds.values()})}, cap {cap:.3f}")
    if over and not os.environ.get("ROCK_OVER"):
        raise SystemExit(f"[rock] over budget: {', '.join(f'{lv} {counts[lv]} > {budgets[lv][1]}' for lv in over)}")

    for lv in levels:
        for o in bpy.context.scene.objects:
            o.select_set(o.name.startswith(lv + "_"))
        bpy.ops.export_scene.fbx(filepath=os.path.join(out, f"house-{lv}.fbx"), use_selection=True,
                                 object_types={"MESH"}, mesh_smooth_type="OFF", use_mesh_modifiers=False,
                                 colors_type="LINEAR", axis_forward="-Z", axis_up="Y", apply_unit_scale=True,
                                 apply_scale_options="FBX_SCALE_ALL", bake_space_transform=True, add_leaf_bones=False)
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(out, "house.blend"))
    lo = [min(v.co[i] for v in objs["near"].data.vertices) for i in range(3)]
    hi = [max(v.co[i] for v in objs["near"].data.vertices) for i in range(3)]
    meta = {
        "house": 0, "part": pid, "world": K["world"], "kind": "rock",
        "size": [hi[0] - lo[0], hi[1] - lo[1]], "bounds": [lo, hi], "centre": part["centre"],
        "triangles": counts, "budgets": budgets, "surfaceM2": round(surface, 2),
        "page": dict(P, pxPerM=px, size=size), "fill": fill, "charts": {k: list(v) for k, v in rects.items()},
        "faces": {k: {"wear": pl.kind, "plate": pl.plate, "n": list(pl.n)} for k, pl in sorted(face_plane.items())},
        "plates": len(plates),
        "rounds": {"cap": cap},
        "lap": {"reach": S["lapReach"], "step": 0.0}, "planeShadow": 0.0,
        "seenWithinM": S["levels"]["near"]["seenWithinM"], "cityFromM": S["levels"]["city"]["seenFromM"],
        "plot": {"w": hi[0] - lo[0], "d": hi[1] - lo[1]},
        "pieces": [{"i": 0, "id": pc.id, "mat": "rock", "kind": "rock", "mode": "rigid", "wall": -1, "group": 0}],
        "uv": {"uv0": "metres in the face's plane", "page": "UV1: the page"},
        "colour": {"r": "arris (a round's face)", "g": "part seed", "b": "under (none)", "a": "1: no lap"},
    }
    json.dump(meta, open(os.path.join(out, "house.json"), "w"), indent=1)
    print(f"[rock] wrote {out}")


if __name__ == "__main__":
    main()
