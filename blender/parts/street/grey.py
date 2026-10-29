"""A house's form in grey: the cheapest look at it (Cycles, one grey for every part, a neutral sky and one sun).
Views in the house's own frame.

    Blender -b --factory-startup -P blender/parts/street/grey.py -- --dir cache/street/gen/107 --level near
        --out cache/street/grey/107 [--size 1600x900] [--views street,eye] [--tag x]
        [--roof planes --bake cache/street/bake/107 | --roof tiles]

--roof planes draws the roof's course planes with their baked normal and occlusion (bake.py --only roof); --roof
tiles draws every course tile by tile instead (the bake level's tiles), the floor the planes are judged against.
"""

import json
import math
import os
import sys

import bpy
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:]
a = {argv[i].lstrip("-"): argv[i + 1] for i in range(0, len(argv) - 1, 2)}
src = os.path.abspath(a["dir"])
out = os.path.abspath(a["out"])
level = a.get("level", "near")
W, H = (int(v) for v in a.get("size", "1600x900").split("x"))
os.makedirs(out, exist_ok=True)
meta = json.load(open(os.path.join(src, "house.json")))
w, d = meta["size"]
ridge = meta["heights"]["ridge"]

bpy.ops.wm.open_mainfile(filepath=os.path.join(src, "house.blend"))
sc = bpy.context.scene
roof = a.get("roof")
keep = (level + "_",) + (("bake_",) if roof == "tiles" else ())
drop = {"near": ("near_roof",), "street": ("street_roof", "street_tiles")}[level] if roof == "tiles" else ()
# the street's roof as tiles: the near level's tiles (the lowest courses and the ridge) with the bake level's
also = ("near_tiles",) if roof == "tiles" and level == "street" else ()
for o in list(sc.objects):
    if (not o.name.startswith(keep) and o.name not in also) or o.name in drop:
        bpy.data.objects.remove(o)
grey = bpy.data.materials.new("grey")
grey.use_nodes = True
bsdf = grey.node_tree.nodes["Principled BSDF"]
bsdf.inputs["Base Color"].default_value = (0.55, 0.55, 0.55, 1)
bsdf.inputs["Roughness"].default_value = 0.8
dark = bpy.data.materials.new("dark")
dark.use_nodes = True
dark.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.2, 0.2, 0.2, 1)
baked = None
if roof == "planes":
    # the planes' baked tiles: the page's normal (tangent space, +Y up) and the tiles' occlusion as the base's value
    bd = os.path.abspath(a["bake"])
    baked = bpy.data.materials.new("baked")
    baked.use_nodes = True
    nt = baked.node_tree
    b = nt.nodes["Principled BSDF"]
    b.inputs["Roughness"].default_value = 0.8
    uv = nt.nodes.new("ShaderNodeUVMap")
    uv.uv_map = "page"
    tn = nt.nodes.new("ShaderNodeTexImage")
    tn.image = bpy.data.images.load(os.path.join(bd, "street-normal.exr"))
    tn.image.colorspace_settings.name = "Non-Color"
    ta = nt.nodes.new("ShaderNodeTexImage")
    ta.image = bpy.data.images.load(os.path.join(bd, "ao.exr"))
    ta.image.colorspace_settings.name = "Non-Color"
    for t in (tn, ta):
        nt.links.new(uv.outputs["UV"], t.inputs["Vector"])
    nm = nt.nodes.new("ShaderNodeNormalMap")
    nm.uv_map = "page"
    nt.links.new(tn.outputs["Color"], nm.inputs["Color"])
    nt.links.new(nm.outputs["Normal"], b.inputs["Normal"])
    mul = nt.nodes.new("ShaderNodeMix")
    mul.data_type = "RGBA"
    mul.blend_type = "MULTIPLY"
    mul.inputs["Factor"].default_value = 1.0
    mul.inputs[6].default_value = (0.2, 0.2, 0.2, 1)
    nt.links.new(ta.outputs["Color"], mul.inputs[7])
    nt.links.new(mul.outputs[2], b.inputs["Base Color"])
for o in sc.objects:
    o.data.materials.clear()
    if baked is not None and o.name in ("near_roof", "street_roof", "street_tiles"):
        o.data.materials.append(baked)
    else:
        o.data.materials.append(dark if o.name.endswith(("_tiles", "_roof")) else grey)
# ground
bpy.ops.mesh.primitive_plane_add(size=80, location=(w / 2, d / 2 - 6, 0))
g = bpy.context.object
g.data.materials.append(grey)
# light: a sun from the south-west, low, and a grey sky
sun = bpy.data.objects.new("sun", bpy.data.lights.new("sun", "SUN"))
sc.collection.objects.link(sun)
sun.data.energy = 3.0
sun.data.angle = math.radians(1.5)
az, el = math.radians(a and float(a.get("az", 215))), math.radians(float(a.get("el", 28)))
# the sun's direction: from azimuth az (degrees from north, clockwise; the house's -y is the street, south)
dvec = Vector((math.sin(az), math.cos(az), 0)) * math.cos(el) + Vector((0, 0, math.sin(el)))
sun.rotation_euler = (-dvec).to_track_quat("-Z", "Y").to_euler()
world = bpy.data.worlds.new("w")
sc.world = world
world.use_nodes = True
world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.5, 0.5, 0.5, 1)
world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.6
sc.render.engine = "CYCLES"
sc.cycles.device = "GPU"
prefs = bpy.context.preferences.addons["cycles"].preferences
prefs.compute_device_type = "METAL"
prefs.get_devices()
for dv in prefs.devices:
    dv.use = True
sc.cycles.samples = 48
sc.cycles.use_denoising = True
sc.render.resolution_x, sc.render.resolution_y = W, H
sc.view_settings.view_transform = "Standard"
cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
sc.collection.objects.link(cam)
sc.camera = cam
views = {
    "street": ((w / 2 - 9.0, -19.0, 1.6), (w / 2, 1.0, 3.0), 38),
    "eyeroof": ((w / 2 - 2.5, -5.0, 1.6), (w / 2, 1.5, 5.2), 64),
    "eye": ((1.2, -4.6, 1.6), (2.4, 0.0, 2.2), 62),
    "raised": ((-7.0, -12.0, 12.0), (w / 2, d / 2, 2.5), 42),
    "back": ((w + 7.0, d + 11.0, 2.2), (w / 2, d, 2.6), 44),
    # joints close to: the chimney on the ridge, the lean-to against the back wall
    # ref 10's stand: across the street from a front corner, looking up at the gable
    "ref10": ((-4.5, -15.5, 1.6), (w * 0.5, 2.0, 4.6), 50),
    # ref 10's stand, close on the front left corner's eave
    "ref10corner": ((-4.5, -15.5, 1.6), (-0.3, -0.3, meta["heights"]["top"] + 0.2), 9),
    # a front window close, at eye level
    "window": ((2.2, -3.2, 1.6), (2.2, 0.0, meta["openings"][0]["z0"] + 0.5), 50),
    # the street stop's camera, close on the right rake of a gable front
    "rake": ((w / 2 - 9.0, -19.0, 1.6), (w * 0.78, 0.0, (meta["heights"]["top"] + ridge) / 2), 5),
    # a front corner's eave and verge from below
    "corner": ((-1.8, -2.6, 2.4), (0.0, 0.0, meta["heights"]["top"]), 60),
}
if meta["leanTo"]:
    views["leanto"] = ((meta["leanTo"]["x"][1] + 2.5, d + meta["leanTo"]["depth"] + 3.0, 2.0),
                       (meta["leanTo"]["x"][1] - 0.5, d + 0.3, meta["leanTo"]["z_hi"] - 0.2), 50)
if meta["features"].get("chimney"):
    views["chimney"] = ((meta["features"]["chimney"][0] - 2.5, -1.5, ridge + 1.2), tuple(meta["features"]["chimney"][:2]) + (ridge,), 40)
if meta["features"].get("ark"):
    ak = meta["features"]["ark"]
    # the ark from the street below it, and its side from across the gable
    views["ark"] = ((w / 2 - 3.5, -7.5, 1.6), (w / 2, -0.4, ak["zB"] + 1.6), 52)
    views["arkroof"] = ((-5.0, -10.0, ridge + 3.5), (w / 2, -0.5, ridge - 1.5), 40)
    views["arkside"] = ((-3.0, -4.0, ak["zB"] - 0.5), (ak["aS"], -0.4, ak["zB"] + 0.8), 55)
want = a.get("views", ",".join(views)).split(",")
tag = a.get("tag", "")
for name, (pos, at, fov) in views.items():
    if name not in want:
        continue
    cam.location = pos
    cam.rotation_euler = (Vector(at) - Vector(pos)).to_track_quat("-Z", "Y").to_euler()
    cam.data.angle = math.radians(fov)
    sc.render.filepath = os.path.join(out, f"{level}-{name}{tag}.png")
    bpy.ops.render.render(write_still=True)
    print("[grey] wrote", sc.render.filepath)
