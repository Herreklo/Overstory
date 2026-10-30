"""t13: the shore block as one whole scanned roche moutonnee (kit.json `scan`), placed rigidly from the record.

Levelled by the plane of its own open rim (the ground it was scanned in), turned so its stoss-to-lee axis (read from
its form: the long abraded stoss, the plucked lee) runs the record's ice direction, scaled uniformly so its crest
stands at the record's back with its scanned ground `groundM` under the sea, its crest on t09's, its ground skirt
trimmed at `trimM` (the rock alone, its rim under the sea). Then the kit's grey check: Eevee, one neutral sun
(az 330, el 35) and one raking (az 255, el 7), t09's views (eye, 12 m, sea, lee) and the tip's water frame with
107 on its stand for scale, t09's outline drawn over each in red.

    Blender -b --factory-startup -P scan.py -- --glb SCAN.glb --out DIR [--subject scan|t09]

The scan is downloaded data: read it with --factory-startup only, never run anything from its folder.
"""
import json, math, os, sys
from collections import deque

import bpy
import numpy as np
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path[:0] = [HERE, os.path.dirname(HERE)]
import blockin as BI  # noqa: E402
import outcrop  # noqa: E402


def arg(n, d=None):
    a = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    return a[a.index(n) + 1] if n in a else d


K = json.load(open(os.path.join(HERE, "kit.json")))
REC = K["scan"]
OUT = os.path.abspath(arg("--out")); os.makedirs(OUT, exist_ok=True)
SUBJECT = arg("--subject", "scan")
for o in list(bpy.data.objects):
    bpy.data.objects.remove(o)


def link(name, V, T, mat, UV=None):
    me = bpy.data.meshes.new(name); me.from_pydata(V.tolist(), [], T.tolist())
    if UV is not None:
        me.uv_layers.new(name="UVMap").data.foreach_set("uv", UV.reshape(-1))
    me.materials.append(mat)
    ob = bpy.data.objects.new(name, me); bpy.context.scene.collection.objects.link(ob)
    return ob


def clay(name, rgb, rough=0.8, emit=False):
    m = bpy.data.materials.new(name); m.use_nodes = True; b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*rgb, 1); b.inputs["Roughness"].default_value = rough
    if emit:
        b.inputs["Emission Color"].default_value = (*rgb, 1); b.inputs["Emission Strength"].default_value = 1.0
        b.inputs["Base Color"].default_value = (0, 0, 0, 1); b.inputs["Specular IOR Level"].default_value = 0
    return m


# ---------------------------------------------------------------- the scan, rigid
def rim_plane(V, T):
    """The plane of the largest open rim loop: the ground the scan was made in."""
    _, wid = np.unique(np.round(V, 5), axis=0, return_inverse=True); wid = wid.reshape(-1)
    TW = wid[T]
    E = np.sort(np.concatenate([TW[:, [0, 1]], TW[:, [1, 2]], TW[:, [2, 0]]]), axis=1)
    Eu, cnt = np.unique(E, axis=0, return_counts=True); Eb = Eu[cnt == 1]
    rep = np.zeros(wid.max() + 1, int); rep[wid] = np.arange(len(V))
    adj = {}
    for a_, b_ in Eb:
        adj.setdefault(a_, []).append(b_); adj.setdefault(b_, []).append(a_)
    seen, best = set(), []
    for s in adj:
        if s in seen:
            continue
        st, comp = [s], []
        while st:
            x = st.pop()
            if x not in seen:
                seen.add(x); comp.append(x); st.extend(adj[x])
        best = max(best, comp, key=len)
    P = V[rep[np.array(best)]]
    c = P.mean(0); w, U = np.linalg.eigh(np.cov((P - c).T)); n = U[:, 0]
    cr = np.cross(V[T[:, 1]] - V[T[:, 0]], V[T[:, 2]] - V[T[:, 0]])
    if n @ cr.sum(0) < 0:
        n = -n
    return n, c, np.percentile(np.abs((P - c) @ n), 50)


def to_z(n):
    z = np.array([0, 0, 1.0]); v = np.cross(n, z); s = np.linalg.norm(v); c = n @ z
    Kx = np.array([[0, -v[2], v[1]], [v[2], 0, -v[0]], [-v[1], v[0], 0]])
    return np.eye(3) + Kx + Kx @ Kx * ((1 - c) / s ** 2)


def crest_component(L, h, cs=0.25):
    """Faces' cells of the heightfield over h connected to the crest (the rock, not its skirt's lumps)."""
    ij = np.floor(L[:, :2] / cs).astype(int); lo = ij.min(0); ij -= lo
    H = np.full(ij.max(0) + 1, -np.inf); np.maximum.at(H, (ij[:, 0], ij[:, 1]), L[:, 2])
    ci = np.unravel_index(np.argmax(H), H.shape); m = H > h
    seen = np.zeros_like(m); seen[ci] = True; q = deque([ci])
    while q:
        i, j = q.popleft()
        for a_, b_ in ((i + 1, j), (i - 1, j), (i, j + 1), (i, j - 1)):
            if 0 <= a_ < m.shape[0] and 0 <= b_ < m.shape[1] and m[a_, b_] and not seen[a_, b_]:
                seen[a_, b_] = True; q.append((a_, b_))
    return seen, lo, cs


def place_scan(rock_mat):
    bpy.ops.import_scene.gltf(filepath=arg("--glb"))
    ob = max((o for o in bpy.data.objects if o.type == "MESH"), key=lambda o: len(o.data.vertices))
    me = ob.data; me.transform(ob.matrix_world); me.calc_loop_triangles()
    V = np.empty(len(me.vertices) * 3); me.vertices.foreach_get("co", V); V = V.reshape(-1, 3)
    T = np.empty(len(me.loop_triangles) * 3, int); me.loop_triangles.foreach_get("vertices", T); T = T.reshape(-1, 3)
    TL = np.empty(len(me.loop_triangles) * 3, int); me.loop_triangles.foreach_get("loops", TL); TL = TL.reshape(-1, 3)
    UV = np.empty(len(me.loops) * 2); me.uv_layers[0].data.foreach_get("uv", UV); UV = UV.reshape(-1, 2)
    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o)
    n, c, off = rim_plane(V, T)
    L = (V - c) @ to_z(n).T
    L[:, :2] -= (L[:, :2].min(0) + L[:, :2].max(0)) / 2
    crest = L[np.argmax(L[:, 2])]; H = float(crest[2])
    # turn: the scan's own ice bearing onto the record's (a turn about z by phi lowers every bearing by phi)
    phi = math.radians(REC["iceToward"] - BI.FIX["rock"]["ice"]["toward"])
    Rz = np.array([[math.cos(phi), -math.sin(phi), 0], [math.sin(phi), math.cos(phi), 0], [0, 0, 1]])
    back = K["shore"]["lone"]["back"]
    s = (back + REC["groundM"]) / H
    a = math.radians(BI.FIX["rock"]["ice"]["toward"]); e = np.array([math.sin(a), math.cos(a), 0]); w = np.array([-e[1], e[0], 0])
    at = np.array([*REC["crestAt"], back]) + w * REC["landwardM"]  # w: across the ice, toward the land (bearing toward + 270)
    P = ((L - crest) @ Rz.T) * s + at
    # trim: the rock is the crest's connected cells over trimM; the skirt goes
    comp, lo, cs = crest_component(L, (REC["trimM"] + REC["groundM"]) / s)
    FC = L[T].mean(1); ij = np.floor(FC[:, :2] / cs).astype(int) - lo
    keep = comp[np.clip(ij[:, 0], 0, comp.shape[0] - 1), np.clip(ij[:, 1], 0, comp.shape[1] - 1)]
    Tk = T[keep]
    used, inv = np.unique(Tk, return_inverse=True)
    Pk, Tk = P[used], inv.reshape(-1, 3)
    # the rim left: how high does any open edge stand
    ob = link("scan", Pk, Tk, rock_mat, UV[TL[keep]])
    import bmesh  # the scan's own pinholes closed, its loose crumbs of skirt dropped; nothing is added
    bm = bmesh.new(); bm.from_mesh(ob.data); bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
    bm.faces.ensure_lookup_table(); seen, isl = set(), []
    for f0 in bm.faces:
        if f0.index in seen:
            continue
        st, comp = [f0], []
        seen.add(f0.index)
        while st:
            f = st.pop(); comp.append(f)
            for e_ in f.edges:
                for g in e_.link_faces:
                    if g.index not in seen:
                        seen.add(g.index); st.append(g)
        isl.append(comp)
    isl.sort(key=len, reverse=True)
    bmesh.ops.delete(bm, geom=[f for c in isl[1:] for f in c], context="FACES")
    holes = [e_ for e_ in bm.edges if e_.is_boundary and min(v.co.z for v in e_.verts) > REC["trimM"] + 0.3]
    bmesh.ops.holes_fill(bm, edges=holes, sides=REC["holeSides"])
    rz = np.array([max(v.co.z for v in e_.verts) for e_ in bm.edges if e_.is_boundary])
    bm.to_mesh(ob.data); bm.free()
    for p in ob.data.polygons:
        p.use_smooth = False
    info = {"rimPlaneMedianOff": round(float(off), 3), "crestOverGround": round(H, 3), "scale": round(s, 4),
            "tris": len(ob.data.polygons), "islandsDropped": len(isl) - 1, "holesFilledEdges": len(holes),
            "rimMaxZ": round(float(rz.max()), 3), "rimOverSea": int((rz > 0).sum()), "rimEdges": int(len(rz))}
    for z in (0.0, -0.8):
        q = Pk[Pk[:, 2] > z]
        info[f"along@{z}"] = round(float(np.ptp(q @ e)), 2); info[f"across@{z}"] = round(float(np.ptp(q @ w)), 2)
    return ob, info


def t09(rock_mat):
    with bpy.data.libraries.load(os.path.join(ROOT, "cache", "rock", "kit", "gen", "carve", "W.blend")) as (_, dst):
        dst.objects = ["W-high"]
    ob = dst.objects[0]; bpy.context.scene.collection.objects.link(ob); bpy.context.view_layer.update()
    ob.data.materials.clear(); ob.data.materials.append(rock_mat)
    return ob


# ---------------------------------------------------------------- the frame: sea, the record's land, 107
def land(mat, clear):
    """The record's landform (outcrop.Landform's smooth back) round the block, above the sea only, none within `clear`
    of the crest (the outcrop is not built: the land is the frame's back and 107's ground, not the block's contact)."""
    L = outcrop.Landform(BI.FIX["outcrop"]["landform"])
    x0, x1, y0, y1, st = *REC["landRegion"], 0.25
    xs, ys = np.arange(x0, x1 + 1e-6, st), np.arange(y0, y1 + 1e-6, st)
    X, Y = np.meshgrid(xs, ys, indexing="ij"); Z = L.smooth(X.ravel(), Y.ravel()).reshape(X.shape) - REC["landBelowM"]
    nx, ny = X.shape; idx = np.arange(nx * ny).reshape(nx, ny)
    q = np.stack([idx[:-1, :-1], idx[1:, :-1], idx[1:, 1:], idx[:-1, 1:]], -1).reshape(-1, 4)
    zq = Z.ravel()[q]; cx, cy = clear
    far = np.hypot(X.ravel()[q].mean(1) - cx, Y.ravel()[q].mean(1) - cy) > REC["landClearM"]
    q = q[(zq > -0.3).any(1) & far]
    me = bpy.data.meshes.new("land"); me.from_pydata(np.stack([X.ravel(), Y.ravel(), Z.ravel()], 1).tolist(), [], q.tolist())
    me.materials.append(mat); bpy.context.scene.collection.objects.link(bpy.data.objects.new("land", me))


def house(mat):
    """107 on its stand (fixture `buildings`), as tip.py puts it: its front-left corner, its front along x."""
    hj = json.load(open(os.path.join(ROOT, K["beside"]["gen"], "house.json"))); w, d = hj["size"]
    stand = next(b for b in BI.FIX["buildings"] if b["id"] == K["tip"]["stand"])
    t = math.radians(stand["turn"]); ex, ey = Vector((math.cos(t), math.sin(t), 0)), Vector((-math.sin(t), math.cos(t), 0))
    corner = Vector((stand["at"][0], stand["at"][1], stand["base"])) - ex * (w / 2) - ey * (d / 2)
    M = Matrix.Translation(corner) @ Matrix.Rotation(t, 4, "Z")
    before = set(bpy.data.objects)
    bpy.ops.import_scene.fbx(filepath=os.path.join(ROOT, K["beside"]["gen"], "house-near.fbx"))
    for o in set(bpy.data.objects) - before:
        if o.type == "MESH":
            o.matrix_world = M @ o.matrix_world
            o.data.materials.clear(); o.data.materials.append(mat)
    # the plinth: dry stone down to the land
    L = outcrop.Landform(BI.FIX["outcrop"]["landform"])
    zl = float(L.smooth(np.array([stand["at"][0]]), np.array([stand["at"][1]]))[0]) - REC["landBelowM"]
    bpy.ops.mesh.primitive_cube_add(size=1)
    p = bpy.context.active_object; p.name = "plinth"
    p.scale = (w + 0.2, d + 0.2, stand["base"] - zl + 0.3); p.rotation_euler = (0, 0, t)
    p.location = (stand["at"][0], stand["at"][1], (stand["base"] + zl - 0.3) / 2)
    p.data.materials.append(mat)


# ---------------------------------------------------------------- the grey check
def main():
    sc = bpy.context.scene
    rock = clay("rock", (0.32, 0.32, 0.32))
    soil = clay("land", tuple(REC["landRGB"]), 0.95)
    water = clay("water", (0.05, 0.055, 0.06), 0.3)
    wall = clay("house", (0.4, 0.4, 0.4), 0.7)
    info = {}
    if SUBJECT == "scan":
        subj, info = place_scan(rock)
    else:
        subj = t09(rock)
    print("[scan]", json.dumps(info))
    link("water", np.array([(-400, -400, 0), (400, -400, 0), (400, 400, 0), (-400, 400, 0.0)]), np.array([(0, 1, 2), (0, 2, 3)]), water)
    a = math.radians(BI.FIX["rock"]["ice"]["toward"])
    cxy = np.array(REC["crestAt"]) + np.array([-math.cos(a), math.sin(a)]) * REC["landwardM"]
    land(soil, cxy)
    house(wall)
    sc.render.engine = "BLENDER_EEVEE"; sc.render.resolution_x, sc.render.resolution_y = 1280, 720
    sc.view_settings.view_transform = "AgX"
    wo = bpy.data.worlds.new("w"); sc.world = wo; wo.use_nodes = True
    bg = wo.node_tree.nodes["Background"]; bg.inputs[0].default_value = (0.8, 0.8, 0.8, 1); bg.inputs[1].default_value = 0.6
    sun = bpy.data.objects.new("sun", bpy.data.lights.new("sun", "SUN")); sc.collection.objects.link(sun); sun.data.angle = math.radians(3)
    cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam")); sc.collection.objects.link(cam); sc.camera = cam
    rec = K["shore"]["lone"]
    views = {n: dict(v) for n, v in rec["views"].items() if n in ("loneeye", "lone12", "lonesea")}
    sh = Vector((-math.cos(a), math.sin(a), 0)) * REC["landwardM"]  # the scan's landward move (w)
    views["lone12"] = {"pos": list(Vector(views["lone12"]["pos"]) + sh), "target": list(Vector(views["lone12"]["target"]) + sh), "fov": REC["fov12"]}
    tg = Vector(views["lone12"]["target"]); r = math.radians(215)
    views["lee"] = {"pos": list(tg + Vector((math.sin(r) * 7, math.cos(r) * 7, 3.0))), "target": list(tg + Vector((0, 0, 0.3))), "fov": 45}
    views["water"] = K["tip"]["views"]["water"]
    for n, v in views.items():
        for o in bpy.data.objects:
            if o.type == "MESH" and o is not subj and o.name != "water":
                o.hide_render = n not in REC["landViews"]
        cam.location = Vector(v["pos"]); cam.rotation_euler = (Vector(v["target"]) - Vector(v["pos"])).to_track_quat("-Z", "Y").to_euler()
        cam.data.sensor_fit = "VERTICAL"; cam.data.angle = math.radians(v["fov"]); cam.data.clip_start = 0.05
        for light, (A, B, en) in {"neutral": (330, 35, 3.0), "raking": (255, 7, 4.5)}.items():
            A, B = math.radians(A), math.radians(B)
            dv = Vector((math.sin(A) * math.cos(B), math.cos(A) * math.cos(B), math.sin(B)))
            sun.rotation_euler = (-dv).to_track_quat("-Z", "Y").to_euler(); sun.data.energy = en
            sc.render.filepath = os.path.join(OUT, f"{SUBJECT}-{n}-{light}.png"); bpy.ops.render.render(write_still=True)
    if SUBJECT == "t09":  # the outline's mask: t09 white, everything else black, nothing lit
        white, black = clay("white", (1, 1, 1), emit=True), clay("black", (0, 0, 0), emit=True)
        for o in bpy.data.objects:
            if o.type == "MESH":
                o.data.materials.clear(); o.data.materials.append(white if o is subj else black)
        bg.inputs[1].default_value = 0.0; sun.data.energy = 0.0; sc.view_settings.view_transform = "Standard"
        sc.eevee.use_shadows = False if hasattr(sc.eevee, "use_shadows") else None
        for n, v in views.items():
            cam.location = Vector(v["pos"]); cam.rotation_euler = (Vector(v["target"]) - Vector(v["pos"])).to_track_quat("-Z", "Y").to_euler()
            cam.data.angle = math.radians(v["fov"])
            for o in bpy.data.objects:
                if o.type == "MESH" and o is not subj and o.name != "water":
                    o.hide_render = n not in REC["landViews"]
            sc.render.filepath = os.path.join(OUT, f"mask-{n}.png"); bpy.ops.render.render(write_still=True)
    json.dump(info, open(os.path.join(OUT, f"{SUBJECT}.json"), "w"), indent=1)
    if SUBJECT == "scan":
        bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "scan.blend"))


main()
