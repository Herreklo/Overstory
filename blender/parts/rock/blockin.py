"""The Holm's rock tip in grey block-in: the masses the target frame is painted over, and nothing more.

The rock as a few broad planes (a whaleback: gentle stoss planes to the sea, a stepped lee to the Holm), the Holm's
ground, the 1882 landing and path cut, the customs house and harbour master's office as boxes, the breakwater and the
islets beyond, from fixtures/lt1-holm-tip.json. Judges nothing; the rock generator replaces the rock.

    Blender -b --factory-startup -P blender/parts/rock/blockin.py -- --out DIR [--render VIEWS] [--light lowsun]
"""

import json
import math
import os
import sys

import bpy
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
FIX = json.load(open(os.path.join(ROOT, "fixtures", "lt1-holm-tip.json")))
VIEWS = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "views.json")))


def arg(name, default=None):
    a = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    return a[a.index(name) + 1] if name in a else default


def grey(L):
    """CIE L* as a linear grey."""
    return ((L + 16) / 116) ** 3 if L > 8 else L / 903.3


def compass(b):
    r = math.radians(b)
    return np.array([math.sin(r), math.cos(r)])


def inside(poly, X, Y):
    c = np.zeros(X.shape, bool)
    P = list(poly)
    for (x1, y1), (x2, y2) in zip(P, P[1:] + P[:1]):
        cond = (y1 > Y) != (y2 > Y)
        xi = x1 + (Y - y1) * (x2 - x1) / ((y2 - y1) if y2 != y1 else 1e-9)
        c ^= cond & (X < xi)
    return c


def seg_dist(X, Y, line):
    d = np.full(X.shape, 1e9)
    t_at = np.zeros(X.shape)
    acc = 0.0
    total = sum(math.dist(a, b) for a, b in zip(line, line[1:]))
    for (x1, y1), (x2, y2) in zip(line, line[1:]):
        dx, dy = x2 - x1, y2 - y1
        L2 = dx * dx + dy * dy
        t = np.clip(((X - x1) * dx + (Y - y1) * dy) / L2, 0, 1)
        dd = np.hypot(X - (x1 + t * dx), Y - (y1 + t * dy))
        m = dd < d
        d[m] = dd[m]
        t_at[m] = (acc + t[m] * math.sqrt(L2)) / total
        acc += math.sqrt(L2)
    return d, t_at


def heights(X, Y):
    """The Holm behind the tip (Holm Street's end on the spine, the pub quays either side), the sea's bed elsewhere."""
    h = FIX["holm"]
    lift = np.clip((h["streetHalfWidth"] + h["slopeM"] - np.abs(X)) / h["slopeM"], 0, 1)
    holm = h["quay"] + (h["street"] - h["quay"]) * lift
    on = Y < h["from"]
    z = np.where(on, holm, -6.0)
    return z, on.astype(int)


def slab(name, poly, z_top, z_base, mat):
    """Made ground: a polygon raised from its base to its top (a quay's fill, with its wall straight down)."""
    n = len(poly)
    v = [(x, y, z_base) for x, y in poly] + [(x, y, z_top) for x, y in poly]
    f = [tuple(range(n - 1, -1, -1)), tuple(range(n, 2 * n))]
    f += [(i, (i + 1) % n, n + (i + 1) % n, n + i) for i in range(n)]
    me = bpy.data.meshes.new(name)
    me.from_pydata(v, [], f)
    me.materials.append(mat)
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    return ob


def ribbon(name, line, width, floors, z_base, mat):
    """A path's fill where the rock falls below it: its corridor raised to its floor, sloping along the line."""
    v, f = [], []
    for i, (a, b) in enumerate(zip(line, line[1:])):
        a, b = np.array(a, float), np.array(b, float)
        d = (b - a) / np.linalg.norm(b - a)
        n = np.array([-d[1], d[0]]) * width / 2
        k = len(v)
        for p, z in ((a, floors[i]), (b, floors[i + 1])):
            v += [tuple(p - n) + (z_base,), tuple(p - n) + (z,), tuple(p + n) + (z,), tuple(p + n) + (z_base,)]
        f += [(k, k + 4, k + 5, k + 1), (k + 1, k + 5, k + 6, k + 2), (k + 2, k + 6, k + 7, k + 3),
              (k, k + 1, k + 2, k + 3), (k + 4, k + 7, k + 6, k + 5)]
    me = bpy.data.meshes.new(name)
    me.from_pydata(v, [], f)
    me.materials.append(mat)
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    return ob


def grid_mesh(name, x0, x1, y0, y1, step, mats):
    nx, ny = int((x1 - x0) / step) + 1, int((y1 - y0) / step) + 1
    xs, ys = np.linspace(x0, x1, nx), np.linspace(y0, y1, ny)
    X, Y = np.meshgrid(xs, ys)
    Z, K = heights(X, Y)
    verts = np.stack([X.ravel(), Y.ravel(), Z.ravel()], 1)
    i = np.arange(nx * ny).reshape(ny, nx)
    a, b, c_, d = i[:-1, :-1].ravel(), i[:-1, 1:].ravel(), i[1:, 1:].ravel(), i[1:, :-1].ravel()
    faces = np.stack([a, b, c_, d], 1)
    kf = np.maximum.reduce([K.ravel()[a], K.ravel()[b], K.ravel()[c_], K.ravel()[d]])
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts.tolist(), [], faces.tolist())
    for m in mats:
        me.materials.append(m)
    me.polygons.foreach_set("material_index", kf.astype(np.int32))
    me.polygons.foreach_set("use_smooth", np.zeros(len(faces), bool))
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    return ob


def rock_mesh(name, mat):
    """The outcrop's blocks as one mesh: joint, cut and worn faces flat; the ice's worn tops carry their back's own
    normal (outcrop.py Back), so the abraded surface shades smooth across its facets and its seams."""
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import hull as H
    import outcrop
    rec = FIX["outcrop"]
    land = outcrop.Landform(rec["landform"])
    blocks = outcrop.build(rec, "holm-tip", FIX["sea"])
    V, T, NL = [], [], []
    for faces, info in blocks:
        grad = info.get("grad", land.grad)
        for f in faces:
            b = len(V)
            V.extend(f.V.tolist())
            for i in range(1, len(f.V) - 1):
                T.append((b, b + i, b + i + 1))
            if f.label in (outcrop.ICE, outcrop.PLATE):
                for x, y, _ in f.V:
                    g = grad(x, y)
                    n = np.array([-g[0], -g[1], 1.0])
                    NL.append(n / np.linalg.norm(n))
            else:
                NL.extend([f.n] * len(f.V))
    me = bpy.data.meshes.new(name)
    me.from_pydata(V, [], T)
    me.materials.append(mat)
    me.polygons.foreach_set("use_smooth", np.ones(len(T), bool))
    loop_n = [NL[me.loops[l].vertex_index] for p in me.polygons for l in p.loop_indices]
    me.normals_split_custom_set([tuple(n) for n in loop_n])
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    print(f"[blockin] rock: {len(blocks)} blocks, {len(T)} triangles")
    return ob


MATS = []


def material(name, L, rough=0.85):
    MATS.append({"name": name, "L": L, "smooth": round(1 - rough, 3)})
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    v = grey(L)
    b.inputs["Base Color"].default_value = (v, v, v, 1)
    b.inputs["Roughness"].default_value = rough
    return m


def box(name, at, turn, size, z0, z1, mat, gable=None, roof=None):
    """A box on its footprint (at, turn, size), from z0 to z1, with a gable roof to `gable` along its length."""
    cx, cy = at
    r = math.radians(turn)
    ex, ey = np.array([math.cos(r), math.sin(r)]), np.array([-math.sin(r), math.cos(r)])
    hx, hy = size[0] / 2, size[1] / 2
    corners = [np.array([cx, cy]) + sx * hx * ex + sy * hy * ey for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
    v = [(p[0], p[1], z0) for p in corners] + [(p[0], p[1], z1) for p in corners]
    f = [(0, 3, 2, 1), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
    if gable is None:
        f.append((4, 5, 6, 7))
    else:
        # ridge along ex (the length): two ridge points over the short ends' middles, eaves overhang 0.3 m
        m0 = (corners[0] + corners[3]) / 2
        m1 = (corners[1] + corners[2]) / 2
        v += [(m0[0], m0[1], gable), (m1[0], m1[1], gable)]
        f += [(4, 5, 9, 8), (6, 7, 8, 9), (7, 4, 8), (5, 6, 9)]
    me = bpy.data.meshes.new(name)
    me.from_pydata(v, [], f)
    me.materials.append(mat)
    if roof is not None and gable is not None:
        me.materials.append(roof)
        idx = [0] * 5 + [1, 1, 0, 0]
        me.polygons.foreach_set("material_index", idx)
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    return ob


def stone_plinth(name, at, turn, size, base, mat, step=0.4, bed=0.3, sill=0.12, rock="rock"):
    """A dry-stone plinth laid on the rock and taking up its slope (act-customs-1862): its top the floor's base, its
    foot the rock under each point of its edge, bedded `bed` into it; tall where the rock falls away, a sill of
    `sill` where the rock comes up near the floor. The rock as drawn (the object `rock`) is read by casting down."""
    from mathutils import Vector
    from mathutils.bvhtree import BVHTree
    rock = bpy.data.objects[rock]
    tree = BVHTree.FromPolygons([v.co.copy() for v in rock.data.vertices], [tuple(p.vertices) for p in rock.data.polygons])
    r = math.radians(turn)
    ex, ey = np.array([math.cos(r), math.sin(r)]), np.array([-math.sin(r), math.cos(r)])
    hx, hy = size[0] / 2, size[1] / 2
    corners = [np.array(at, float) + sx * hx * ex + sy * hy * ey for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
    ring = []
    for a, b in zip(corners, corners[1:] + corners[:1]):
        n = max(1, int(math.ceil(np.linalg.norm(b - a) / step)))
        ring += [a + (b - a) * k / n for k in range(n)]
    v = []
    for p in ring:
        hit = tree.ray_cast(Vector((p[0], p[1], base + 10)), Vector((0, 0, -1)))[0]
        foot = min(hit.z if hit else base - 3.0, base - sill) - bed
        v += [(p[0], p[1], foot), (p[0], p[1], base)]
    m = len(ring)
    f = [(2 * i, 2 * ((i + 1) % m), 2 * ((i + 1) % m) + 1, 2 * i + 1) for i in range(m)]
    f += [tuple(2 * i + 1 for i in range(m)), tuple(2 * i for i in reversed(range(m)))]
    me = bpy.data.meshes.new(name)
    me.from_pydata(v, [], f)
    me.materials.append(mat)
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    h = [base - z - bed for z, _ in zip(v[0::2], v[1::2]) for z in [z[2]]]
    print(f"[blockin] {name}: {min(h):.2f}-{max(h):.2f} m over the rock")
    return ob


def prism_along(name, line, w_top, w_base, z_top, z_base, mat):
    v, f = [], []
    for i, (a, b) in enumerate(zip(line, line[1:])):
        a, b = np.array(a, float), np.array(b, float)
        d = (b - a) / np.linalg.norm(b - a)
        n = np.array([-d[1], d[0]])
        k = len(v)
        for p in (a, b):
            v += [tuple(p - n * w_base / 2) + (z_base,), tuple(p - n * w_top / 2) + (z_top,),
                  tuple(p + n * w_top / 2) + (z_top,), tuple(p + n * w_base / 2) + (z_base,)]
        f += [(k, k + 4, k + 5, k + 1), (k + 1, k + 5, k + 6, k + 2), (k + 2, k + 6, k + 7, k + 3),
              (k, k + 1, k + 2, k + 3), (k + 4, k + 7, k + 6, k + 5)]
    me = bpy.data.meshes.new(name)
    me.from_pydata(v, [], f)
    me.materials.append(mat)
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    return ob


def dome(name, at, r, top, mat, n=48):
    v = [(at[0], at[1], top)]
    rings = 6
    for k in range(1, rings + 1):
        rr = r * k / rings
        zz = top * (1 - (k / rings) ** 1.6) - (2.0 if k == rings else 0)
        for j in range(n):
            a = 2 * math.pi * j / n
            v.append((at[0] + rr * math.cos(a), at[1] + rr * math.sin(a), zz))
    f = [(0, 1 + j, 1 + (j + 1) % n) for j in range(n)]
    for k in range(rings - 1):
        b0, b1 = 1 + k * n, 1 + (k + 1) * n
        f += [(b0 + j, b1 + j, b1 + (j + 1) % n, b0 + (j + 1) % n) for j in range(n)]
    me = bpy.data.meshes.new(name)
    me.from_pydata(v, [], f)
    me.materials.append(mat)
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    return ob


def build():
    for ob in list(bpy.data.objects):
        bpy.data.objects.remove(ob)
    rock = material("rock", 52)
    holm = material("holm-ground", 40)
    made = material("made-ground", 46)
    grid_mesh("land", -80, 100, -90, FIX["holm"]["from"], 0.5, [holm, holm])
    rock_mesh("rock", rock)
    act = {a["id"]: a for a in FIX["acts"]}
    slab("landing", act["act-landing-1882"]["apron"], act["act-landing-1882"]["top"], -4.0, made)
    p = act["act-path-1882"]
    ribbon("path-fill", p["line"], p["width"] + 0.6, p["floor"], -1.0, made)
    slab("pub-quay-end", [[50, -60], [90, -60], [90, -42], [58, -38]], 2.1, -4.0, made)
    water = material("water", 28, rough=0.06)
    me = bpy.data.meshes.new("water")
    me.from_pydata([(-3000, -3000, 0), (3000, -3000, 0), (3000, 3000, 0), (-3000, 3000, 0)], [], [(0, 1, 2, 3)])
    me.materials.append(water)
    bpy.context.scene.collection.objects.link(bpy.data.objects.new("water", me))
    red, roofm, plinth = material("timber-red", 38), material("roof", 24), material("plinth", 50)
    for b in FIX["buildings"]:
        stone_plinth(b["id"] + "-plinth", b["at"], b["turn"], [b["size"][0] + 0.2, b["size"][1] + 0.2], b["base"], plinth)
        box(b["id"], b["at"], b["turn"], b["size"], b["base"], b["base"] + b["eaves"], red, gable=b["base"] + b["ridge"], roof=roofm)
    # the Holm's warehouses behind, as masses only (stand-ins for the frame's back; not judged here)
    sys.path.insert(0, os.path.join(ROOT, "blender", "resolver"))
    import hashing as HS
    rng = HS.Stream("holm-tip", "blockin", "town")
    town = material("town", 44)
    x = -70.0
    while x < 60:
        w = rng.uniform(7, 13)
        d = rng.uniform(9, 16)
        y = -38 - d / 2 - rng.uniform(0, 5)
        g = 2.9 + max(0.0, -y - 30) * 0.18
        eav = rng.uniform(4.5, 7.5)
        box(f"town-{int(x)}", [x + w / 2, y], rng.uniform(-4, 4), [w, d], g, g + eav, town,
            gable=g + eav + rng.uniform(2.5, 4.5), roof=roofm)
        x += w + rng.uniform(0.4, 6)
    bw = FIX["breakwater"]
    prism_along("breakwater", bw["line"], 4.0, 15.0, bw["crest"], -4.0, material("breakwater", 50))
    lx, ly = bw["light"]
    box("light", [lx, ly], 0, [1.6, 1.6], bw["crest"], bw["crest"] + 6.0, material("light", 85))
    far = material("far", 46)
    for isl in FIX["far"]["islets"]:
        dome(isl["name"], isl["at"], isl["r"], isl["top"], far)
    far_land(FIX["far"].get("land"), material("far-land", 44))
    return water


def far_land(rec, mat):
    """The town's land beyond the tip as centre_land.py designs it (the Bluff and Herring Hill behind, the frame's
    back), on a coarse grid over the record's site region; quads under the sea's bed left out."""
    if not rec:
        return None
    sys.path.insert(0, os.path.join(ROOT, "blender", "blockouts"))
    import centre_land
    x0, y0, x1, y1 = rec["region"]
    step = rec["stepM"]
    ox, oy = FIX["street_origin"]
    xs, ys = np.arange(x0, x1 + step, step), np.arange(y0, y1 + step, step)
    X, Y = np.meshgrid(xs, ys)
    Z = centre_land.heights(ox - Y, oy + X)                 # street x = ox - y, street y = oy + x
    ny, nx = X.shape
    i = np.arange(nx * ny).reshape(ny, nx)
    q = np.stack([i[:-1, :-1].ravel(), i[:-1, 1:].ravel(), i[1:, 1:].ravel(), i[1:, :-1].ravel()], 1)
    q = q[Z.ravel()[q].max(1) > -1.0]
    me = bpy.data.meshes.new("far-land")
    me.from_pydata(np.stack([X.ravel(), Y.ravel(), Z.ravel()], 1).tolist(), [], q.tolist())
    me.materials.append(mat)
    ob = bpy.data.objects.new("far-land", me)
    bpy.context.scene.collection.objects.link(ob)
    return ob


def rig(light):
    sc = bpy.context.scene
    sc.render.engine = "BLENDER_EEVEE"
    sc.render.resolution_x, sc.render.resolution_y = int(arg("--w", 1280)), int(arg("--h", 720))
    sc.view_settings.view_transform = "Standard"
    sc.view_settings.look = "None"
    w = bpy.data.worlds.new("sky")
    sc.world = w
    w.use_nodes = True
    bg = w.node_tree.nodes["Background"]
    L = VIEWS["lights"][light]
    v = grey(L["skyL"])
    bg.inputs["Color"].default_value = (v, v, v, 1)
    bg.inputs["Strength"].default_value = L["sky"]
    sun = bpy.data.lights.new("sun", "SUN")
    sun.energy = L["sun"]
    sun.angle = math.radians(L.get("angle", 1.0))
    ob = bpy.data.objects.new("sun", sun)
    sc.collection.objects.link(ob)
    aim(ob, L["azimuth"], L["elevation"])
    sc.view_settings.exposure = L.get("exposure", 0.0)
    return ob


def aim(sun, azimuth, elevation):
    from mathutils import Vector
    az, el = math.radians(azimuth), math.radians(elevation)
    to_sun = np.array([math.sin(az) * math.cos(el), math.cos(az) * math.cos(el), math.sin(el)])
    sun.rotation_euler = Vector(to_sun.tolist()).to_track_quat("Z", "Y").to_euler()


def camera(v):
    from mathutils import Vector
    cam = bpy.data.cameras.new(v["name"])
    cam.lens = v["lens"]
    cam.sensor_width = 36.0
    cam.sensor_fit = "HORIZONTAL"
    cam.clip_end = 5000
    ob = bpy.data.objects.new(v["name"], cam)
    bpy.context.scene.collection.objects.link(ob)
    p, t = Vector(v["pos"]), Vector(v["target"])
    ob.location = p
    ob.rotation_euler = (t - p).to_track_quat("-Z", "Y").to_euler()
    return ob


def main():
    out = arg("--out", os.path.join(ROOT, "cache", "rock", "blockin"))
    os.makedirs(out, exist_ok=True)
    build()
    light = arg("--light", "lowsun")
    sun = rig(light)
    names = arg("--render", ",".join(v["name"] for v in VIEWS["views"])).split(",")
    for v in VIEWS["views"]:
        if v["name"] not in names:
            continue
        bpy.context.scene.camera = camera(v)
        if "azimuth" in v:                  # a study view may carry its own sun (finding the frame, not the light)
            aim(sun, v["azimuth"], VIEWS["lights"][light]["elevation"])
        bpy.context.scene.render.filepath = os.path.join(out, f"{v['name']}-{light}.png")
        bpy.ops.render.render(write_still=True)
        print(f"[blockin] {bpy.context.scene.render.filepath}")
    if arg("--save"):
        bpy.ops.wm.save_as_mainfile(filepath=arg("--save"))
    if arg("--digest"):
        lights = [dict(v, name=k) for k, v in VIEWS["lights"].items()]
        json.dump({"mats": MATS, "views": VIEWS["views"], "lights": lights}, open(arg("--digest"), "w"), indent=1)
        print(f"[blockin] {arg('--digest')}")
    if arg("--fbx"):
        for ob in bpy.data.objects:
            ob.select_set(ob.type == "MESH")
        bpy.ops.export_scene.fbx(filepath=arg("--fbx"), use_selection=True, axis_forward="-Z", axis_up="Y",
                                 apply_scale_options="FBX_SCALE_ALL", mesh_smooth_type="FACE")
        print(f"[blockin] {arg('--fbx')}")


if __name__ == "__main__":
    main()
