"""Hewn setts alone, judged in grey light (docs/foundations.md, The judging views; the board, 02, 13, 14): a patch of
old setts laid in rows across a lane, each its own size and set a little high or low, its top crowned and its edges
worn round by wheels and feet, sand and grit between; one grey for every face, a low raking sun and a soft sky, seen
from eye level and from above. Fast enough to change the part and look again in a minute.

    blender -b --factory-startup --python blender/tools/sett_sheet.py -- OUT.png [seed] [kw=value ...]

Keyword values go to the slab part (blender/parts/stone/slate/slab.py) for every sett.
"""

import math
import os
import random
import sys

import bpy
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "parts", "stone", "slate"))
import slab as SL  # noqa: E402


def patch(seed, kw, width=2.2, length=1.6):
    """Rows across the lane (x), each row a sett's width (y), setts of their own lengths along it, every joint off the
    one in the row before."""
    rng = random.Random(f"setts-{seed}")
    V_all, F_all = [], []
    y = 0.0
    below = []
    while y < length:
        rw = rng.uniform(0.095, 0.13)
        x = -width / 2
        joints = []
        while x < width / 2:
            for _ in range(20):
                L = rng.uniform(0.11, 0.22)
                if all(abs(x + L - j) > 0.04 for j in below):
                    break
            w = min(L, width / 2 - x)
            if w < 0.05:
                break
            p = SL.slab(f"sett-{seed}-{y:.3f}-{x:.3f}", w - rng.uniform(0.005, 0.009), rw - rng.uniform(0.005, 0.008),
                        0.11, grid=0.03, **kw)
            V = p["V"].copy()
            V[:, 0] += x
            V[:, 1] += y
            V[:, 2] += rng.uniform(-0.004, 0.004) - 0.11 + (V[:, 0] - x) * rng.uniform(-0.03, 0.03)
            base = sum(len(v) for v in V_all)
            V_all.append(V)
            F_all.extend(tuple(base + q for q in f) for f in p["F"])
            joints.append(x + L)
            x += L
        below = joints
        y += rw
    me = bpy.data.meshes.new("setts")
    me.from_pydata([tuple(v) for v in np.concatenate(V_all)], [], F_all)
    me.validate()
    me.polygons.foreach_set("use_smooth", [True] * len(me.polygons))
    me.set_sharp_from_angle(angle=math.radians(30))
    ob = bpy.data.objects.new("setts", me)
    bpy.context.scene.collection.objects.link(ob)
    return ob


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    out = argv[0] if argv else "/tmp/sett_sheet.png"
    seed = int(argv[1]) if len(argv) > 1 else 1
    kw = {}
    for a in argv[2:]:
        k, v = a.split("=")
        kw[k] = int(v) if v.lstrip("-").isdigit() else float(v)
    for ob in list(bpy.data.objects):
        bpy.data.objects.remove(ob, do_unlink=True)
    sc = bpy.context.scene
    ob = patch(seed, kw)
    mat = bpy.data.materials.new("grey")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (0.18, 0.18, 0.18, 1)
    bsdf.inputs["Roughness"].default_value = 0.85
    ob.data.materials.append(mat)
    # the sand bed between them
    bpy.ops.mesh.primitive_plane_add(size=6, location=(0, 0.8, -0.012))
    sand = bpy.data.materials.new("sand")
    sand.use_nodes = True
    sand.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.1, 0.1, 0.1, 1)
    bpy.context.active_object.data.materials.append(sand)
    sun = bpy.data.objects.new("sun", bpy.data.lights.new("sun", "SUN"))
    sun.data.energy = 3.5
    sun.data.angle = math.radians(2)
    sun.rotation_euler = (math.radians(74), 0, math.radians(-40))
    sc.collection.objects.link(sun)
    sc.world = bpy.data.worlds.new("w")
    sc.world.use_nodes = True
    sc.world.node_tree.nodes["Background"].inputs[0].default_value = (0.5, 0.52, 0.56, 1)
    sc.world.node_tree.nodes["Background"].inputs[1].default_value = 0.6
    sc.render.engine = "CYCLES"
    sc.cycles.samples = 48
    sc.cycles.device = "CPU"
    sc.render.resolution_x, sc.render.resolution_y = 1280, 720
    sc.view_settings.view_transform = "Standard"
    for name, loc, tgt in (("eye", (0.2, -1.4, 1.55), (0.0, 0.9, 0.0)), ("above", (0.9, -0.6, 2.4), (0.0, 0.8, 0.0))):
        cam = bpy.data.objects.new(name, bpy.data.cameras.new(name))
        cam.data.lens = 35
        cam.location = loc
        d = np.subtract(tgt, loc)
        cam.rotation_euler = (math.atan2(math.hypot(d[0], d[1]), -d[2]), 0, math.atan2(d[1], d[0]) - math.pi / 2)
        sc.collection.objects.link(cam)
        sc.camera = cam
        sc.render.filepath = out[:-4] + f"-{name}.png"
        bpy.ops.render.render(write_still=True)
    print("SHEET", out)


main()
