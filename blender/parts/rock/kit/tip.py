"""The Holm tip's grey masses around 107, the target frame's grey-box: blockin.py's build as it is, with 107 standing
where kit.json's `tip.stand` stands, moved into 107's frame (x along its front, y back from it, z up from its ground),
as one FBX and its greys for LT1HolmTip.

    Blender -b --factory-startup -P blender/parts/rock/kit/tip.py -- --out cache/rock/kit/gen/tip
    Blender -b --factory-startup -P blender/parts/rock/kit/tip.py -- --plan <grey-box still> --to <target.png>

With --plan, the target's form plan (kit.json `tip.plan`): the tip's faces by zone, drawn from the street's street stop
and laid over the grey-box still LT1HolmTip drew from it, 107 and everything else showing through as drawn.
"""

import json
import math
import os
import sys

import bpy
import numpy as np
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.dirname(HERE))
import blockin as BI  # noqa: E402


def zone_mesh(K, mats):
    """The tip's blocks as blockin.py's rock_mesh builds them, each face given its zone's material."""
    import outcrop
    Q, rec, sea = K["tip"]["plan"], BI.FIX["outcrop"], BI.FIX["sea"]
    land = outcrop.Landform(rec["landform"])
    names = list(Q["zones"])
    lee = math.cos(math.radians(Q["leeFacing"]))
    V, T, Z = [], [], []
    for faces, _ in outcrop.build(rec, "holm-tip", sea):
        for f in faces:
            kind = f.label.replace("-open", "").replace("-seam", "")
            c = f.V.mean(axis=0)
            nh = f.n[:2] / max(float(np.hypot(*f.n[:2])), 1e-6)
            if kind == "cut":
                z = "made"
            elif c[2] < BI.shore_levels(K["tip"]["grey"]["bands"], c)[1][1]:
                z = "storm"
            elif kind in ("ice",) or kind.endswith("-worn"):
                z = "ice"
            elif kind == "plate" or (abs(f.n[2]) < 0.8 and float(nh @ land.ice) > lee):
                z = "lee"
            elif kind == "foliation":
                z = "foliation"
            else:
                z = "joint"
            b = len(V)
            V.extend(f.V.tolist())
            for i in range(1, len(f.V) - 1):
                T.append((b, b + i, b + i + 1))
                Z.append(names.index(z))
    me = bpy.data.meshes.new("rock-plan")
    me.from_pydata(V, [], T)
    for n in names:
        me.materials.append(mats[n])
    me.polygons.foreach_set("material_index", np.array(Z, np.int32))
    ob = bpy.data.objects.new("rock-plan", me)
    bpy.context.scene.collection.objects.link(ob)
    print(f"[tip] plan: " + ", ".join(f"{n} {Z.count(i)}" for i, n in enumerate(names)))
    return ob


def zone_material(name, rgb, lines, turn):
    """Emission in the zone's colour, darkened along each (normal in the fixture's frame, spacing, width) line family,
    measured in 107's frame (the fixture's turned by -turn)."""
    m = bpy.data.materials.new("plan-" + name)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    em = nt.nodes.new("ShaderNodeEmission")
    pos = nt.nodes.new("ShaderNodeNewGeometry")
    dark = None
    for n, (spacing, width) in lines:
        n = Matrix.Rotation(-math.radians(turn), 3, "Z") @ Vector(n)
        dot = nt.nodes.new("ShaderNodeVectorMath")
        dot.operation = "DOT_PRODUCT"
        dot.inputs[1].default_value = tuple(n / spacing)
        nt.links.new(pos.outputs["Position"], dot.inputs[0])
        fr = nt.nodes.new("ShaderNodeMath")
        fr.operation = "PINGPONG"                       # distance to the nearest line, in spacings, 0..0.5
        fr.inputs[1].default_value = 0.5
        nt.links.new(dot.outputs["Value"], fr.inputs[0])
        lt = nt.nodes.new("ShaderNodeMath")
        lt.operation = "LESS_THAN"
        lt.inputs[1].default_value = 0.5 * width / spacing
        nt.links.new(fr.outputs[0], lt.inputs[0])
        if dark is None:
            dark = lt
        else:
            mx = nt.nodes.new("ShaderNodeMath")
            mx.operation = "MAXIMUM"
            nt.links.new(dark.outputs[0], mx.inputs[0])
            nt.links.new(lt.outputs[0], mx.inputs[1])
            dark = mx
    mix = nt.nodes.new("ShaderNodeMix")
    mix.data_type = "RGBA"
    mix.inputs["A"].default_value = (*rgb, 1)
    mix.inputs["B"].default_value = tuple(0.25 * c for c in rgb) + (1,)
    if dark is not None:
        nt.links.new(dark.outputs[0], mix.inputs["Factor"])
    else:
        mix.inputs["Factor"].default_value = 0.0
    nt.links.new(mix.outputs["Result"], em.inputs["Color"])
    nt.links.new(em.outputs[0], out.inputs["Surface"])
    return m


def holdout():
    m = bpy.data.materials.new("plan-holdout")
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    nt.links.new(nt.nodes.new("ShaderNodeHoldout").outputs[0], nt.nodes.new("ShaderNodeOutputMaterial").inputs["Surface"])
    return m


def plane_normal(dip, toward):
    a, b = math.radians(dip), math.radians(toward)
    return (math.sin(a) * math.sin(b), math.sin(a) * math.cos(b), math.cos(a))


def main():
    out = os.path.abspath(BI.arg("--out", os.path.join(ROOT, "cache", "rock", "kit", "gen", "tip")))
    os.makedirs(out, exist_ok=True)
    K = json.load(open(os.path.join(HERE, "kit.json")))
    house = json.load(open(os.path.join(ROOT, K["beside"]["gen"], "house.json")))
    w, d = house["size"]
    BI.build(K["tip"]["grey"])
    stand = next(b for b in BI.FIX["buildings"] if b["id"] == K["tip"]["stand"])
    plan = BI.arg("--plan")
    if plan:
        Q, rock = K["tip"]["plan"], BI.FIX["rock"]
        fol = plane_normal(rock["foliation"]["dip"], rock["foliation"]["dipToward"])
        lines = {"storm": [], "ice": [],
                 "lee": [(fol, Q["foliationLineM"]), ((0, 0, 1), Q["sheetLineM"])], "foliation": [],
                 "joint": [(fol, Q["foliationLineM"])], "made": []}
        mats = {n: zone_material(n, z["rgb"], lines[n], stand["turn"]) for n, z in Q["zones"].items()}
        hold = holdout()
        for ob in list(bpy.data.objects):
            if ob.type == "MESH":
                ob.data.materials.clear()
                ob.data.materials.append(mats["made"] if ob.name in ("landing", "path-fill") else hold)
        bpy.data.objects.remove(bpy.data.objects["rock"])
        zone_mesh(K, mats)

    # the stand's box and plinth go; 107's plinth stands in their place, laid on the rock to its base
    objs = {o.name: o for o in bpy.data.objects}
    plinth = objs[stand["id"] + "-plinth"].data.materials[0]
    for n in (stand["id"], stand["id"] + "-plinth"):
        bpy.data.objects.remove(objs[n])
    BI.stone_plinth("stand-plinth", stand["at"], stand["turn"], [w + 0.2, d + 0.2], stand["base"], mats["made"] if plan else plinth,
                    rock="rock-plan" if plan else "rock")
    # --lone: the shore block alone (kit.json shore.lone) in place of the outcrop, at the near level's rounds
    lone = BI.arg("--lone")
    if lone:
        sys.path.insert(0, HERE)
        import shore
        rec = K["shore"]["lone"]
        bpy.data.objects.remove(bpy.data.objects["rock"])
        s = shore.bearing(rec["face"])
        c = np.array([rec["at"][0] - s.x * rec["depth"] / 2, rec["at"][1] - s.y * rec["depth"] / 2, 1.0])
        e, (wet, storm, _) = BI.shore_levels(K["tip"]["grey"]["bands"], c)
        for r in shore.row(rec, K, BI.FIX):
            shore.build("rock" if r is rec else f"rock-{r['id']}", r, K, BI.FIX, (e, wet, storm),
                        [bpy.data.materials[n] for n in shore.BANDS], K["levels"]["near"]["segments"])

    # into 107's frame: its front-left corner at the origin, its front along x, its ground at the stand's base
    t = math.radians(stand["turn"])
    ex, ey = Vector((math.cos(t), math.sin(t), 0)), Vector((-math.sin(t), math.cos(t), 0))
    corner = Vector((stand["at"][0], stand["at"][1], stand["base"])) - ex * (w / 2) - ey * (d / 2)
    M = Matrix.Rotation(-t, 4, "Z") @ Matrix.Translation(-corner)
    for ob in bpy.data.objects:
        ob.matrix_world = M @ ob.matrix_world
        ob.select_set(ob.type == "MESH")
    if plan:
        return draw_plan(K, house, plan, hold)
    bpy.ops.export_scene.fbx(filepath=os.path.join(out, "tip.fbx"), use_selection=True, axis_forward="-Z", axis_up="Y",
                             apply_scale_options="FBX_SCALE_ALL", mesh_smooth_type="FACE")
    # the tip's own views and the site's low sun, in 107's frame (the sun as LT1HolmTip's offset: 0 toward 107's front,
    # 90 along it, x)
    to107 = lambda p: list(M @ Vector(p))
    views = [dict(v, name=n, pos=to107(v["pos"]), target=to107(v["target"]))
             for n, v in (K["shore"]["lone"] if lone else K["tip"])["views"].items() if n != "describes"]
    sun = BI.VIEWS["lights"]["lowsun"]["azimuth"]
    json.dump({"mats": BI.MATS, "stand": stand["id"], "corner": list(corner), "turn": stand["turn"], "views": views,
               "sunOff": (180 - stand["turn"] - sun) % 360},
              open(os.path.join(out, "tip.json"), "w"), indent=1)
    print(f"[tip] {len([o for o in bpy.data.objects if o.type == 'MESH'])} masses, 107 at {stand['id']}; wrote {out}")


def draw_plan(K, house, still, hold):
    """107 (its street level, from its blend) as a holdout, the street's street stop, the plan drawn and laid over the
    grey-box still; the zones' key in the frame's corner."""
    w, d = house["size"]
    with bpy.data.libraries.load(os.path.join(ROOT, K["beside"]["gen"], "house.blend")) as (src, dst):
        dst.objects = [n for n in src.objects if n.startswith("street_")]
    for ob in dst.objects:
        bpy.context.scene.collection.objects.link(ob)
        ob.data = ob.data.copy()
        ob.data.materials.clear()
        ob.data.materials.append(hold)
    sc = bpy.context.scene
    W, H = 2560, 1440
    sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage = W, H, 100
    cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
    sc.collection.objects.link(cam)
    sc.camera = cam
    pos, tgt = Vector((w / 2 - 9.0, -19.0, 1.6)), Vector((w / 2, 1.0, 3.0))   # LT1Street.Views' street stop
    cam.location = pos
    cam.rotation_euler = (tgt - pos).to_track_quat("-Z", "Y").to_euler()
    cam.data.sensor_fit = "VERTICAL"
    cam.data.angle = math.radians(38)
    cam.data.clip_start, cam.data.clip_end = 0.1, 500
    # the key: one line a zone, in the frame's top left, a metre in front of the lens
    Q = K["tip"]["plan"]
    th = math.tan(math.radians(19))
    plate_m = bpy.data.materials.new("plan-plate")
    plate_m.use_nodes = True
    plate_m.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0, 0, 0, 1)
    rows = list(Q["zones"].items())
    size, gap, x0, y0 = 0.019 * th / 0.344, 0.034 * th / 0.344, -th * W / H + 0.02, th - 0.03
    for i, (n, z) in enumerate(rows):
        y = y0 - i * gap
        bpy.ops.mesh.primitive_plane_add(size=size, location=(x0 + size / 2, y, -1))
        sw = bpy.context.object
        sw.data.materials.append(zone_material("key-" + n, z["rgb"], [], 0))
        sw.parent = cam
        cu = bpy.data.curves.new("key-" + n, "FONT")
        cu.body = z["says"]
        cu.size = size * 0.95
        tx = bpy.data.objects.new("key-" + n, cu)
        sc.collection.objects.link(tx)
        tx.location = (x0 + size * 1.6, y - size * 0.35, -1)
        tx.data.materials.append(zone_material("text-" + n, (1, 1, 1), [], 0))
        tx.parent = cam
    bpy.context.view_layer.update()
    wide = size * 1.6 + max(o.dimensions.x for o in sc.objects if o.name.startswith("key-") and o.type == "FONT") + 0.02
    bpy.ops.mesh.primitive_plane_add(size=1, location=(x0 - 0.01 + wide / 2, y0 - gap * (len(rows) - 1) / 2, -1.001))
    pl = bpy.context.object
    pl.scale = (wide, gap * len(rows) + 0.01, 1)
    pl.data.materials.append(zone_material("plate", (0.02, 0.02, 0.02), [], 0))
    pl.parent = cam
    for e in ("BLENDER_EEVEE", "BLENDER_EEVEE_NEXT"):
        try:
            sc.render.engine = e
            break
        except TypeError:
            continue
    sc.render.film_transparent = True
    sc.view_settings.view_transform = "Standard"
    sc.render.image_settings.file_format = "PNG"
    sc.render.image_settings.color_mode = "RGBA"
    raw = os.path.join(os.path.dirname(os.path.abspath(BI.arg("--to"))), "plan-raw.png")
    sc.render.filepath = raw
    bpy.ops.render.render(write_still=True)
    # laid over the still: the zone's hue at the still's own value, so the light and forms stay readable
    a = np.array(bpy.data.images.load(os.path.abspath(still)).pixels[:], np.float32).reshape(H, W, 4)
    p = np.array(bpy.data.images.load(raw).pixels[:], np.float32).reshape(H, W, 4)
    luma = (a[..., :3] @ np.array([0.2126, 0.7152, 0.0722], np.float32))[..., None]
    key = p[..., :3].max(axis=-1, keepdims=True) < 0.05      # the key's plate stays black
    tint = np.where(key, p[..., :3], np.clip(luma * p[..., :3] * 1.9, 0, 1))
    k = Q["blend"] * p[..., 3:4]
    k = np.where(key & (p[..., 3:4] > 0.5), 0.85, k)
    o = a.copy()
    o[..., :3] = a[..., :3] * (1 - k) + tint * k
    img = bpy.data.images.new("plan", W, H, alpha=True)
    img.pixels.foreach_set(o.ravel())
    img.filepath_raw = os.path.abspath(BI.arg("--to"))
    img.file_format = "PNG"
    img.save()
    print(f"[tip] plan over {still}: {BI.arg('--to')}")


if __name__ == "__main__":
    main()
