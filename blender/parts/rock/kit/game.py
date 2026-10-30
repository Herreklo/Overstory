"""Stage 3, a mass's game mesh (kit.json `game`), built for the street's pipeline as part.py builds a part's levels.

    Blender -b --factory-startup -P blender/parts/rock/kit/game.py -- --mass boulder [--out cache/rock/kit/gen/boulder]

The mass's sculpted form (sculpt.py, its chamfers and chips, without the cracks the bake carries) is
meshed at `voxelM`, cut `underM` below the turf (the mass sinks `sinkM`; the turf is the levels' z = 0) and decimated to
each level's budget (`fill` of street.json's ceiling, by the mass's surface: a square metre of rock costs what one of
house does). Every level's faces sit on the same charts: a face's chart is the designed plane (the blockout's) its
normal is nearest, projected onto that plane, so a convex mass's chart is one-to-one; u along the foliation's trace.
The city level is laid on the near and street levels' charts as it falls, held inside them.

Writes, as part.py does: house-near.fbx, house-street.fbx, house-city.fbx (`<level>_<material>`, the mass's `material`),
house.json, and house.blend with the high-poly beside the levels as `high_<material>` (sculpt.py's `<gen>/high.blend`, moved to the turf), carrying what
the bake reads from it: `rest`, `piece` and `Col` (R its arris: the smooth form's mean curvature between `arris`, so the
page's edges are drawn where the form turns; G the part's seed).
"""
import json, os, sys

import bmesh
import bpy
import numpy as np
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import sculpt as SC  # noqa: E402
import part as PT  # noqa: E402  (its geom, hashing and chart frames)

MS, G, HS, arg = SC.MS, PT.G, PT.HS, SC.arg
ROOT = MS.ROOT


def evaluated(ob, name):
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(ob.evaluated_get(dg)); me.name = name
    return me


def even_normals(o, hard):
    """A baked level's normals: the plain corner-angle average, so a round's turn spreads over its width and the page
    corrects it smoothly (the house's face-area weighting, made for unbaked chamfers, crowds the turn into the few small
    triangles of a round, steeper than the page's texels can carry); a turn over `hard` degrees stays a hard edge."""
    me = o.data
    if "custom_normal" in me.attributes:
        me.attributes.remove(me.attributes["custom_normal"])
    me.set_sharp_from_angle(angle=np.radians(hard)); me.update()


def arris(sc, V, lo, hi, h):
    """The smooth form's mean curvature at V (half the field's Laplacian, by central differences h apart), as 0..1
    between lo and hi a metre."""
    out = np.empty(len(V))
    for i in range(0, len(V), 100000):
        P = V[i:i + 100000]; lap = -6.0 * sc.form(P)[0]
        for ax in range(3):
            e = np.zeros(3); e[ax] = h
            lap += sc.form(P + e)[0] + sc.form(P - e)[0]
        out[i:i + 100000] = np.clip((0.5 * lap / (h * h) - lo) / (hi - lo), 0.0, 1.0)
    return out


def main():
    pid = arg("--mass", "boulder"); X = next(x for x in MS.M["masses"] if x["id"] == pid)
    out = os.path.abspath(arg("--out", os.path.join(ROOT, "cache", "rock", "kit", "gen", pid))); os.makedirs(out, exist_ok=True)
    K = MS.K; GM = K["game"]; S = json.load(open(os.path.join(ROOT, K["street"])))
    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o)
    sc = SC.Sculpt(X); sink = X.get("sinkM", MS.M["judge"]["sinkM"]); down = Matrix.Translation((0, 0, -sink))
    mname = X.get("material", "rock"); mat = bpy.data.materials.new(mname)

    # the form, cut under the turf and moved down onto it
    form = sc.mesh(mat, GM["voxelM"], fine=False, name="form")
    bm = bmesh.new(); bm.from_mesh(form.data)
    bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], plane_co=(0, 0, sink - GM["underM"]),
                           plane_no=(0, 0, 1), clear_inner=True)
    bm.to_mesh(form.data); bm.free(); form.data.transform(down)
    me = form.data; me.calc_loop_triangles()
    V = np.array([v.co for v in me.vertices]); T = np.array([t.vertices[:] for t in me.loop_triangles])
    C = V[T].mean(1); A = np.linalg.norm(np.cross(V[T[:, 1]] - V[T[:, 0]], V[T[:, 2]] - V[T[:, 0]]), axis=1) / 2
    surface = float(A[C[:, 2] > 0].sum())
    m2 = S["budgetSurfaceM2"]["m2"]
    budgets = {lv: [round(b * surface / m2) for b in S["levels"][lv]["budgetTris"]] for lv in ("near", "street", "city")}

    # each level decimated to its budget
    meshes = {}
    for lv in ("near", "street", "city"):
        ob = bpy.data.objects.new(f"d_{lv}", form.data.copy()); bpy.context.scene.collection.objects.link(ob)
        md = ob.modifiers.new("d", "DECIMATE"); md.decimate_type = "COLLAPSE"; md.use_collapse_triangulate = True
        md.ratio = GM["fill"] * budgets[lv][1] / len(T)
        meshes[lv] = evaluated(ob, f"m_{lv}"); bpy.data.objects.remove(ob)
    bpy.data.objects.remove(form)

    # charts: the designed planes, each face on the one its normal is nearest
    planes = [(Vector(f[0]), f[3], f[2]) for f in sc.ms.faces if f[2] != "base"]
    frames = {key: PT.grain(n, Vector(sc.nf)) for n, key, kind in planes}

    def proj(key, p):
        e_u, e_v = frames[key]
        return p.dot(e_u), p.dot(e_v)

    levels = {}
    for lv, me in meshes.items():
        faces = []
        for f in me.polygons:
            pts = [me.vertices[i].co.copy() for i in f.vertices]
            key = max(planes, key=lambda pl: pl[0].dot(f.normal))[1]
            faces.append((key, pts, f.area, lv != "city"))
        levels[lv] = faces
    span = {}
    for faces in levels.values():
        for key, pts, area, whole in faces:
            if not whole:
                continue
            for p in pts:
                u, v = proj(key, p); lo, hi = span.get(key, ((u, v), (u, v)))
                span[key] = ((min(lo[0], u), min(lo[1], v)), (max(hi[0], u), max(hi[1], v)))
    charts = G.Charts(); P = K["page"]; normal = {key: n for n, key, kind in planes}
    for key, (lo, hi) in sorted(span.items()):
        charts(key, hi[0] - lo[0], hi[1] - lo[1], P["down"] if normal[key].z < -0.5 else 1.0)
    rects, fill, px, size = charts.fit(P)
    pc = PT.Piece(0, f"rock/{pid}"); seed = HS.unit(HS.h(K["world"], pid, "seed"))

    objs, counts = {}, {}
    for lv, faces in levels.items():
        fl = []
        for key, pts, area, whole in faces:
            if key not in span:
                key = max(span, key=lambda c: normal[c].dot(normal[key]))
            lo, hi = span[key]
            cuv = [(min(max(proj(key, p)[0], lo[0]), hi[0]) - lo[0], min(max(proj(key, p)[1], lo[1]), hi[1]) - lo[1]) for p in pts]
            fl.append((pc, G.Face(pts, cuv, key, cuv)))
        o = G.to_object(f"{lv}_{mname}", fl, lambda _pc: Matrix.Identity(4), lambda _pc, w: w, rects, size,
                        lambda _pc, f, w: [0.0, seed, 0.0, 1.0])
        even_normals(o, GM["hardDeg"]); objs[lv] = o; counts[lv] = G.tris_of(o)
    for me in meshes.values():
        bpy.data.meshes.remove(me)
    over = [lv for lv in budgets if counts[lv] > budgets[lv][1]]
    print(f"[game] {pid}: triangles {counts}; budgets {budgets} for {surface:.1f} m²; page {size} px at {px} px/m, filled {fill:.2f}")
    if over:
        raise SystemExit(f"[game] over budget: {', '.join(f'{lv} {counts[lv]} > {budgets[lv][1]}' for lv in over)}")

    for lv in objs:
        for o in bpy.context.scene.objects:
            o.select_set(o.name.startswith(lv + "_"))
        bpy.ops.export_scene.fbx(filepath=os.path.join(out, f"house-{lv}.fbx"), use_selection=True,
                                 object_types={"MESH"}, mesh_smooth_type="OFF", use_mesh_modifiers=False,
                                 colors_type="LINEAR", axis_forward="-Z", axis_up="Y", apply_unit_scale=True,
                                 apply_scale_options="FBX_SCALE_ALL", bake_space_transform=True, add_leaf_bones=False)

    # the high-poly beside the levels, on the turf, with what the bake reads from it
    with bpy.data.libraries.load(os.path.join(out, "high.blend")) as (src, dst):
        dst.objects = [f"high_{pid}"]
    hi_ob = dst.objects[0]; bpy.context.scene.collection.objects.link(hi_ob); hi_ob.name = f"high_{mname}"
    hm = hi_ob.data; Vh = np.empty(len(hm.vertices) * 3); hm.vertices.foreach_get("co", Vh); Vh = Vh.reshape(-1, 3)
    ar = arris(sc, Vh, *GM["arris"], GM["curveM"])
    hm.transform(down); Vh[:, 2] -= sink
    hm.attributes.new("rest", "FLOAT_VECTOR", "POINT").data.foreach_set("vector", Vh.ravel())
    hm.attributes.new("piece", "INT", "FACE").data.foreach_set("value", np.zeros(len(hm.polygons), np.int32))
    col = np.stack([ar, np.full(len(ar), seed), np.zeros(len(ar)), np.ones(len(ar))], 1)
    hm.color_attributes.new("Col", "FLOAT_COLOR", "POINT").data.foreach_set("color", col.ravel())
    hm.materials.clear(); hm.materials.append(mat); hi_ob.hide_render = True
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(out, "house.blend"))

    lo = [min(v.co[i] for v in objs["near"].data.vertices) for i in range(3)]
    hi = [max(v.co[i] for v in objs["near"].data.vertices) for i in range(3)]
    meta = {
        "house": 0, "part": pid, "world": K["world"], "kind": "rock",
        "size": [hi[0] - lo[0], hi[1] - lo[1]], "bounds": [lo, hi], "centre": X.get("centre", [0, 0]),
        "triangles": counts, "budgets": budgets, "surfaceM2": round(surface, 2),
        "page": dict(P, pxPerM=px, size=size), "fill": fill, "charts": {k: list(v) for k, v in rects.items()},
        "faces": {key: {"wear": kind, "plate": 0, "n": list(n)} for n, key, kind in planes if key in span},
        "plates": 1, "high": {"tris": len(hm.polygons), "arris": GM["arris"], "rays": GM["rays"]},
        "lap": {"reach": S["lapReach"], "step": 0.0}, "planeShadow": 0.0,
        "seenWithinM": S["levels"]["near"]["seenWithinM"], "cityFromM": S["levels"]["city"]["seenFromM"],
        "plot": {"w": hi[0] - lo[0], "d": hi[1] - lo[1]},
        "pieces": [{"i": 0, "id": pc.id, "mat": mname, "kind": "rock", "mode": "rigid", "wall": -1, "group": 0}],
        "uv": {"uv0": "metres in the designed plane", "page": "UV1: the page"},
        "colour": {"r": "arris (on the high-poly: its form's curvature)", "g": "part seed", "b": "under (none)", "a": "1: no lap"},
    }
    json.dump(meta, open(os.path.join(out, "house.json"), "w"), indent=1)
    print(f"[game] wrote {out}")


if __name__ == "__main__":
    main()
