# look.py -- --out DIR [--gen DIR] [--views eye,back,street] [--lights lowsun,overcast] [--samples 48] [--margin 0.15]
# The sculpt's high-poly alone, in grey, from LT1HolmTip's own cameras and suns (kit.json `beside`; the street stop as
# probe/faces.py places it), at the frame's full size but rendered only in a window round the part: a minute's look at
# the form before the bake and Unity's twelve. Writes <view>-<light>.png, the window only.
import json, math, os, sys
import bpy
import numpy as np
from mathutils import Vector

ROOT = "/Users/oystein/code/Overstory"
a = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
arg = lambda k, d: a[a.index(k) + 1] if k in a else d  # noqa: E731
K = json.load(open(f"{ROOT}/blender/parts/rock/kit/kit.json")); B = K["beside"]
OUT = os.path.abspath(arg("--out", "")); GEN = arg("--gen", f"{ROOT}/cache/rock/kit/gen/boulder")
part = B["parts"][0]; X = next(m for m in K["mass"]["masses"] if m["id"] == part["part"]); at = np.array(part["at"], float)
W, H = 2560, 1440; w = 7.0
VIEWS = {"eye": (at + B["eye"]["from"], np.array(B["eye"]["look"]), B["eye"]["fov"]),
         "back": (at + B["back"]["from"], np.array(B["back"]["look"]), B["back"]["fov"]),
         "street": (np.array([w / 2 - 9, -19, 1.6]), np.array([w / 2, 1, 3]) - np.array([w / 2 - 9, -19, 1.6]), 38)}
# LT1Street's lights (azimuth toward the sun in the house's x, y; elevation), the low sun turned by TIP_SUN -10
SUN = {"lowsun": ((math.sin(math.radians(-10)), -math.cos(math.radians(-10))), 18, 4.0, 0.35),
       "overcast": ((-0.5, -1.0), 65, 1.2, 1.6)}

for o in list(bpy.data.objects):
    bpy.data.objects.remove(o)
with bpy.data.libraries.load(os.path.join(GEN, "high.blend")) as (src, dst):
    dst.objects = [n for n in src.objects if n.startswith("high_")]
ob = dst.objects[0]; sc = bpy.context.scene; sc.collection.objects.link(ob)
ob.location = (at[0], at[1], -X["sinkM"])
grey = bpy.data.materials.new("grey"); grey.use_nodes = True
bs = grey.node_tree.nodes["Principled BSDF"]; bs.inputs["Base Color"].default_value = (0.42, 0.42, 0.42, 1); bs.inputs["Roughness"].default_value = 0.85
ob.data.materials.clear(); ob.data.materials.append(grey)
g = bpy.data.meshes.new("ground"); g.from_pydata([(-200, -200, 0), (200, -200, 0), (200, 200, 0), (-200, 200, 0)], [], [(0, 1, 2, 3)])
gm = bpy.data.materials.new("gm"); gm.use_nodes = True; gm.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.18, 0.18, 0.18, 1)
g.materials.append(gm); sc.collection.objects.link(bpy.data.objects.new("ground", g))
sc.render.engine = "CYCLES"; sc.cycles.samples = int(arg("--samples", 48)); sc.cycles.use_denoising = True
pr = bpy.context.preferences.addons["cycles"].preferences; pr.compute_device_type = "METAL"; pr.get_devices()
for d in pr.devices:
    d.use = True
sc.cycles.device = "GPU"; sc.view_settings.view_transform = "Standard"
sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage = W, H, 100
wo = bpy.data.worlds.new("w"); sc.world = wo; wo.use_nodes = True; bg = wo.node_tree.nodes["Background"]
sun = bpy.data.objects.new("sun", bpy.data.lights.new("sun", "SUN")); sc.collection.objects.link(sun); sun.data.angle = math.radians(1.0)
cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam")); sc.collection.objects.link(cam); sc.camera = cam
cam.data.sensor_fit = "VERTICAL"; cam.data.clip_start = 0.1
V = np.empty(len(ob.data.vertices) * 3); ob.data.vertices.foreach_get("co", V); V = V.reshape(-1, 3)[::50] + np.array(ob.location)
V = V[V[:, 2] > -0.02]
mg = float(arg("--margin", 0.15)); os.makedirs(OUT, exist_ok=True)
for v in arg("--views", "eye,back,street").split(","):
    pos, look, fov = VIEWS[v]; f = look / np.linalg.norm(look); r = np.cross(f, [0, 0, 1]); r /= np.linalg.norm(r); u = np.cross(r, f)
    cam.location = Vector(pos); cam.rotation_euler = Vector(f).to_track_quat("-Z", "Y").to_euler(); cam.data.angle = math.radians(fov)
    d = V - pos; z = d @ f; t = math.tan(math.radians(fov) / 2)
    x = W / 2 + (d @ r) / z / t * H / 2; y = H / 2 - (d @ u) / z / t * H / 2
    x0, x1, y0, y1 = x.min(), x.max(), y.min(), y.max(); m = mg * max(x1 - x0, y1 - y0)
    x0, x1, y0, y1 = max(0, x0 - m), min(W, x1 + m), max(0, y0 - m), min(H, y1 + m)
    sc.render.use_border = True; sc.render.use_crop_to_border = True
    sc.render.border_min_x, sc.render.border_max_x = x0 / W, x1 / W
    sc.render.border_min_y, sc.render.border_max_y = 1 - y1 / H, 1 - y0 / H
    for ln in arg("--lights", "lowsun,overcast").split(","):
        (ax, ay), el, se, we = SUN[ln]; n = math.hypot(ax, ay); e = math.radians(el)
        to = Vector((math.cos(e) * ax / n, math.cos(e) * ay / n, math.sin(e)))
        sun.rotation_euler = (-to).to_track_quat("-Z", "Y").to_euler(); sun.data.energy = se
        bg.inputs[0].default_value = (0.75, 0.78, 0.82, 1); bg.inputs[1].default_value = we
        sc.render.filepath = os.path.join(OUT, f"{v}-{ln}.png"); bpy.ops.render.render(write_still=True)
        print("[look]", v, ln, "window", int(x0), int(y0), int(x1), int(y1), flush=True)
