"""A slate slab part alone, judged in grey light (docs/foundations.md, The judging views; the grey-light rule): three
block steps of the slab part (blender/parts/stone/slate/slab.py), each resting on the one below, one grey for every
face, lit by a low raking sun and a soft sky, seen from eye level at their foot and from above. Fast enough to change
the part and look again in a minute, before the town is rendered.

    blender -b --factory-startup --python blender/tools/slab_sheet.py -- OUT.png [seed] [kw=value ...]

Keyword values are passed to slab() for every block (e.g. edge_jag=0.025 chip=0.03).
"""

import math
import os
import sys

import bpy
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "parts", "stone", "slate"))
import slab as SL  # noqa: E402

SHARP = float(os.environ.get("SHARP", 20))


def block_stair(seed, kw):
    """Three block steps, 0.17 m rises, 0.35 m goings, each slab 0.23 m thick resting on the back of the one below,
    two slabs across a 2.2 m flight."""
    objs = []
    for i in range(3):
        x = -1.1
        for k, w in enumerate((1.25, 0.95) if i % 2 == 0 else (0.85, 1.35)):
            p = SL.slab(f"sheet-{seed}-{i}-{k}", w - 0.008, 0.45, 0.23, **kw)
            V = p["V"].copy()
            V[:, 0] += x
            V[:, 1] += i * 0.35
            V[:, 2] += (i + 1) * 0.17 - 0.23
            me = bpy.data.meshes.new(f"b{i}{k}")
            me.from_pydata([tuple(v) for v in V], [], p["F"])
            me.validate()
            me.polygons.foreach_set("use_smooth", [True] * len(me.polygons))
            me.set_sharp_from_angle(angle=math.radians(SHARP))
            ob = bpy.data.objects.new(me.name, me)
            bpy.context.scene.collection.objects.link(ob)
            objs.append(ob)
            x += w
    return objs


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    out = argv[0] if argv else "/tmp/slab_sheet.png"
    seed = int(argv[1]) if len(argv) > 1 else 1
    kw = {}
    for a in argv[2:]:
        k, v = a.split("=")
        kw[k] = int(v) if v.lstrip("-").isdigit() else float(v)
    for ob in list(bpy.data.objects):
        bpy.data.objects.remove(ob, do_unlink=True)
    sc = bpy.context.scene
    objs = block_stair(seed, kw)
    mat = bpy.data.materials.new("grey")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (0.18, 0.18, 0.18, 1)
    bsdf.inputs["Roughness"].default_value = 0.85
    for ob in objs:
        ob.data.materials.append(mat)
    # the ground
    bpy.ops.mesh.primitive_plane_add(size=8, location=(0, 0.5, 0))
    bpy.context.active_object.data.materials.append(mat)
    # a low raking sun from the front left, and a soft grey sky
    sun = bpy.data.objects.new("sun", bpy.data.lights.new("sun", "SUN"))
    sun.data.energy = 3.5
    sun.data.angle = math.radians(2)
    sun.rotation_euler = (math.radians(72), 0, math.radians(-35))
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
    frames = []
    for name, loc, tgt in (("eye", (0.3, -2.2, 1.0), (0.0, 0.35, 0.25)), ("above", (1.2, -1.2, 2.1), (0.0, 0.4, 0.3))):
        cam = bpy.data.objects.new(name, bpy.data.cameras.new(name))
        cam.data.lens = 35
        cam.location = loc
        d = np.subtract(tgt, loc)
        cam.rotation_euler = (math.atan2(math.hypot(d[0], d[1]), -d[2]), 0, math.atan2(d[1], d[0]) - math.pi / 2)
        sc.collection.objects.link(cam)
        sc.camera = cam
        path = out[:-4] + f"-{name}.png"
        sc.render.filepath = path
        bpy.ops.render.render(write_still=True)
        frames.append(path)
    print("SHEET", frames)


main()
