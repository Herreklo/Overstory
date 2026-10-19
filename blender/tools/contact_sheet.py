"""Contact sheets: many variants of a generator on one image, same camera and neutral light.

A Blender contact sheet checks that a generator works and shows its shape language.
It is not where beauty is judged: that happens in Unity with the real shading.

    python contact_sheet.py house out.png --rows straight,gentle,strong --seeds 1,2,3,4,5

Runs in Blender (via the MCP or `blender -b -P`) or with the `bpy` module.
"""

import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "generators"))

import bpy  # noqa: E402
from mathutils import Vector  # noqa: E402

import palette  # noqa: E402


def clear(name):
    """A clean scene. Headless: reset Blender. Interactive: a new scene, so the open file and add-ons are left alone."""
    if bpy.app.background:
        bpy.ops.wm.read_factory_settings(use_empty=True)
        return bpy.context.scene
    old = bpy.data.scenes.get(name)
    if old:
        for ob in list(old.collection.all_objects):
            bpy.data.objects.remove(ob, do_unlink=True)
        bpy.data.scenes.remove(old)
    scene = bpy.data.scenes.new(name)
    bpy.context.window.scene = scene
    return scene


def neutral_world(scene):
    world = bpy.data.worlds.new("neutral")
    world.use_nodes = True
    bg = world.node_tree.nodes["Background"]
    bg.inputs["Color"].default_value = (0.62, 0.66, 0.72, 1.0)
    bg.inputs["Strength"].default_value = 0.55
    scene.world = world
    sun = bpy.data.lights.new("sun", "SUN")
    sun.energy = 3.2
    sun.angle = math.radians(4)
    sun.color = (1.0, 0.96, 0.9)
    obj = bpy.data.objects.new("sun", sun)
    obj.rotation_euler = (math.radians(52), 0, math.radians(-38))
    scene.collection.objects.link(obj)


def ground(scene, size, mat):
    me = bpy.data.meshes.new("ground")
    s = size
    me.from_pydata([(-s, -s, 0), (s, -s, 0), (s, s, 0), (-s, s, 0)], [], [(0, 1, 2, 3)])
    uvl = me.uv_layers.new()
    u, v = palette.uv("ground")
    for loop in uvl.data:
        loop.uv = (u, v)
    me.materials.append(mat)
    ob = bpy.data.objects.new("ground", me)
    scene.collection.objects.link(ob)


def label(scene, text, loc, size=0.9):
    cu = bpy.data.curves.new(text, "FONT")
    cu.body = text
    cu.size = size
    cu.align_x = "CENTER"
    ob = bpy.data.objects.new("label_" + text, cu)
    ob.location = loc
    ob.rotation_euler = (math.radians(90), 0, 0)
    m = bpy.data.materials.new("label")
    m.diffuse_color = (0.08, 0.08, 0.09, 1)
    m.use_nodes = True
    m.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.03, 0.03, 0.035, 1)
    cu.materials.append(m)
    scene.collection.objects.link(ob)


def sheet(family, out, rows, seeds, cell=16.0, res=(3000, 1900), samples=48, engine=None):
    scene = clear(f"sheet_{family}")
    engine = engine or ("CYCLES" if bpy.app.background else "EEVEE")
    mat = palette.material(save_dir=os.path.join(HERE, ".."))
    gen = __import__(family)
    neutral_world(scene)
    tris = []
    for r, style in enumerate(rows):
        for c, seed in enumerate(seeds):
            ob = gen.build({"style": style}, seed=seed, material=mat)
            ob.location = (c * cell, r * cell * 1.15, 0)
            tris.append(ob["triangles"])
            label(scene, f"{style} · seed {seed}", (c * cell, r * cell * 1.15 - 7.0, 0.05), size=0.7)
    w = (len(seeds) - 1) * cell
    h = (len(rows) - 1) * cell * 1.15
    ground(scene, max(w, h) + 60, mat)

    cam = bpy.data.cameras.new("cam")
    cam.type = "ORTHO"
    cam.ortho_scale = max(w + cell * 1.2, (h + cell * 1.6) * res[0] / res[1]) * 1.02
    camo = bpy.data.objects.new("cam", cam)
    centre = Vector((w / 2, h / 2, 2.5))
    direction = Vector((-0.55, -1.0, 0.72)).normalized()
    camo.location = centre + direction * 120
    camo.rotation_euler = (-direction).to_track_quat("-Z", "Y").to_euler()
    scene.collection.objects.link(camo)
    scene.camera = camo

    if engine == "EEVEE":
        ids = [e.identifier for e in bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items]
        engine = "BLENDER_EEVEE" if "BLENDER_EEVEE" in ids else "BLENDER_EEVEE_NEXT"
    scene.render.engine = engine
    if engine == "CYCLES":
        scene.cycles.samples = samples
        scene.cycles.use_denoising = True
        scene.cycles.device = "CPU"
    scene.render.resolution_x, scene.render.resolution_y = res
    scene.render.resolution_percentage = 100
    scene.render.film_transparent = False
    scene.view_settings.view_transform = "AgX"
    scene.render.filepath = out
    bpy.ops.render.render(write_still=True)
    return dict(out=out, triangles=tris)


if __name__ == "__main__":
    argv = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else sys.argv[1:]
    family, out = argv[0], os.path.abspath(argv[1])
    opts = dict(zip(argv[2::2], argv[3::2]))
    rows = opts.get("--rows", "straight,gentle,strong").split(",")
    seeds = [int(x) for x in opts.get("--seeds", "1,2,3,4,5").split(",")]
    samples = int(opts.get("--samples", 48))
    print(sheet(family, out, rows, seeds, samples=samples))
