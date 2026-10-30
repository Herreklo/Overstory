"""A mass's till stones (kit.json `foot`): a few small stones of its own gneiss where it meets the turf, half sunk
beside it, in the levels' frame (the turf z = 0, as game.py cuts and moves the form). The grass round it is the
ground's (ground.py: the tip's community as the growth's instanced tufts, banked against the stone).

The turf line is the sculpted form's outline at the turf (sculpt.py's field without its fine marks, the form the game
mesh follows), read on bearings round the mass; a stone lies where the turf line breaks (seeded stretches of it). Each
stone a faceted hull of a few seeded points, chamfered as the boulder is, half sunk, a little darker than the boulder
(`dL`), in the gneiss's greys with the skin's top and foot rules. Non-semantic texture, seeded from the mass.

Writes foot.fbx (one object `foot`: vertex colour, sRGB, its albedo; normals the stones' faces) and foot.json (with
each stone's middle and radius, `placed`, for ground.py) into the mass's gen.

    Blender -b --factory-startup -P blender/parts/rock/kit/foot.py -- --mass boulder [--gen cache/rock/kit/gen/boulder]
"""
import importlib.util
import json, math, os, sys

import bmesh
import bpy
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import sculpt as SC  # noqa: E402

MS, HS, arg = SC.MS, SC.HS, SC.arg
ROOT = MS.ROOT
sys.path[:0] = [os.path.join(ROOT, "blender", "parts", "growth"), os.path.join(ROOT, "blender", "parts", "finish")]
import tufts as TF  # noqa: E402,F401  (ground.py takes the tufts' shapes from here)
import finishlib as FL  # noqa: E402

_spec = importlib.util.spec_from_file_location("finish_paint", os.path.join(ROOT, "blender", "parts", "finish", "paint.py"))
FP = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(FP)
K = MS.K; F = K["foot"]


def lin(hexrgb):
    c = np.array([int(hexrgb[i:i + 2], 16) / 255.0 for i in (1, 3, 5)])
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def ly(L):
    """CIE L* as linear luminance."""
    f = (L + 16.0) / 116.0
    return f ** 3 if f ** 3 > 216.0 / 24389.0 else L / 903.3


def outline(sc, phi, z, lo=0.2, hi=3.5):
    """The form's reach from its axis on bearings phi at height z (its own frame), by bisection."""
    u = np.stack([np.sin(phi), np.cos(phi)], 1); a = np.full(len(phi), lo); b = np.full(len(phi), hi)
    for _ in range(32):
        m = (a + b) / 2; inside = sc.field(np.column_stack([u * m[:, None], np.full(len(phi), z)]), fine=False) < 0
        a, b = np.where(inside, m, a), np.where(inside, b, m)
    return (a + b) / 2


def turn(axis, a):
    k = axis / np.linalg.norm(axis); X_ = np.array([[0, -k[2], k[1]], [k[2], 0, -k[0]], [-k[1], k[0], 0]])
    return np.eye(3) + math.sin(a) * X_ + (1 - math.cos(a)) * X_ @ X_


def main():
    pid = arg("--mass", "boulder"); X = next(x for x in MS.M["masses"] if x["id"] == pid)
    gen = os.path.abspath(arg("--gen", os.path.join(ROOT, "cache", "rock", "kit", "gen", pid)))
    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o)
    sc = SC.Sculpt(X); sink = X.get("sinkM", MS.M["judge"]["sinkM"]); up = np.array([0.0, 0.0, 1.0])
    rays = F["rays"]; phi = np.arange(rays) * 2 * math.pi / rays
    turf = outline(sc, phi, sink)
    drip = np.max([outline(sc, phi, sink + h) for h in np.linspace(0.0, F["dripM"], 6)], 0)
    at = lambda b: int(round(b / (2 * math.pi) * rays)) % rays  # noqa: E731
    # the stretches where the turf line shows: seeded noise round the line, `gap` of it lowest
    gaps = SC.Noise("lt1-holm-tip", "foot", "gap", pid); rn = float(turf.mean()) / F["gapM"]
    ring = lambda b: gaps(np.column_stack([rn * np.sin(b), rn * np.cos(b), np.full(np.size(b), 0.5)]))  # noqa: E731
    cut = float(np.quantile(ring(phi), F["gap"])); bare = lambda b: ring(np.atleast_1d(b))[0] < cut  # noqa: E731
    Sk = K["skin"]
    V, N, C, T = [], [], [], []  # vertices, their normals, colours (linear), triangles

    # the till stones
    St = F["stones"]; st = HS.Stream("lt1-holm-tip", "foot", "stones", pid); placed = []
    gn = K["materials"][X["material"]]; gc = K["colour"][X["material"]]["paint"]
    for i in range(St["count"]):
        # where the turf line shows, if one of a few tries finds it: a stone lies where the turf breaks
        a = MS.skewed(st, *St["sizeM"], St["skew"]); b = st.uniform(0, 2 * math.pi)
        for _ in range(St["tries"]):
            if bare(b):
                break
            b = st.uniform(0, 2 * math.pi)
        r = turf[at(b)] + 0.5 * a + MS.skewed(st, 0.0, St["withinM"], 2)
        c = np.array([r * math.sin(b), r * math.cos(b), 0.0]); ax = np.array([a / 2, a * st.uniform(0.6, 0.85) / 2, a * St["flat"] / 2])
        pts = []
        for _ in range(St["points"]):
            v = np.array([st.normal(), st.normal(), st.normal()]); v /= np.linalg.norm(v); pts.append(v * ax * st.uniform(0.85, 1.0))
        R_ = turn(up, st.uniform(0, 2 * math.pi)); h = 2 * ax[2]; dz = -h * st.uniform(*St["sink"])
        bm = bmesh.new()
        for p in pts:
            bm.verts.new(R_ @ p + c + [0.0, 0.0, ax[2] + dz])
        hull = bmesh.ops.convex_hull(bm, input=bm.verts)
        bmesh.ops.delete(bm, geom=list({v for v in hull["geom_interior"] + hull["geom_unused"] if isinstance(v, bmesh.types.BMVert)}), context="VERTS")
        bmesh.ops.dissolve_limit(bm, angle_limit=math.radians(4), verts=bm.verts[:], edges=bm.edges[:])
        bmesh.ops.bevel(bm, geom=bm.edges[:], offset=St["chamfer"] * a, segments=1, affect="EDGES", clamp_overlap=True)
        bmesh.ops.triangulate(bm, faces=bm.faces[:])
        bm.normal_update()
        L0 = gn["L"] + St.get("dL", 0) + st.uniform(-1, 1) * St["vary"][0]; tn = np.array(FP.tint(L0, gc[0] + st.uniform(0, St["vary"][1]), gc[1] + st.uniform(-1, 1) * St["vary"][2]))
        top = h + dz
        for f in bm.faces:
            n = np.array(f.normal); z = float(np.mean([v.co.z for v in f.verts]))
            L = L0 + Sk["top"]["L"] * FL.smoothstep(Sk["top"]["up"][0], Sk["top"]["up"][1], n[2]) - Sk["foot"]["L"] * (1 - FL.smoothstep(0.0, max(top, 1e-3), z))
            k0 = len(V)
            for v in f.verts:
                V.append(np.array(v.co)); N.append(n); C.append(ly(L) * tn)
            T += [(k0, k0 + j, k0 + j + 1) for j in range(1, len(f.verts) - 1)]
        bm.free(); placed.append((c, 0.5 * a))

    me = bpy.data.meshes.new("foot"); V = np.array(V); T = np.array(T, np.int32)
    me.vertices.add(len(V)); me.vertices.foreach_set("co", V.astype(np.float32).ravel())
    me.loops.add(T.size); me.loops.foreach_set("vertex_index", T.ravel())
    me.polygons.add(len(T)); me.polygons.foreach_set("loop_start", np.arange(0, T.size, 3, dtype=np.int32))
    me.update(); me.shade_smooth()
    me.normals_split_custom_set([tuple(N[v]) for v in T.ravel()])
    ca = me.color_attributes.new("Col", "FLOAT_COLOR", "CORNER")
    ca.data.foreach_set("color", np.column_stack([np.array(C)[T.ravel()], np.ones(T.size)]).astype(np.float32).ravel())
    ob = bpy.data.objects.new("foot", me); bpy.context.scene.collection.objects.link(ob)
    for o in bpy.context.scene.objects:
        o.select_set(o == ob)
    bpy.ops.export_scene.fbx(filepath=os.path.join(gen, "foot.fbx"), use_selection=True, object_types={"MESH"},
                             mesh_smooth_type="OFF", use_mesh_modifiers=False, colors_type="SRGB", axis_forward="-Z",
                             axis_up="Y", apply_unit_scale=True, apply_scale_options="FBX_SCALE_ALL",
                             bake_space_transform=True, add_leaf_bones=False)
    info = {"part": pid, "stones": len(placed), "tris": int(len(T)),
            "placed": [[round(float(c[0]), 3), round(float(c[1]), 3), round(float(r), 3)] for c, r in placed],
            "turfLineM": round(float(np.sum(turf) * 2 * math.pi / rays), 2), "bareShare": round(float((ring(phi) < cut).mean()), 2),
            "overhangM": [round(float((drip - turf).min()), 3), round(float((drip - turf).max()), 3)]}
    json.dump(info, open(os.path.join(gen, "foot.json"), "w"), indent=1)
    print("[foot]", json.dumps(info))


if __name__ == "__main__":
    main()
