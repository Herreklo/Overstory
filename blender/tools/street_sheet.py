"""Street sheets: buildings from a fixture, resolved for a year, lined up and rendered from the street.

    python street_sheet.py ../../fixtures/lt1-street.json out.png --year 1989 --styles gentle,strong,wild --ids 101,102,103

Each style is one row, rendered from the same camera; rows are tiled into one image
with labels. A second mode renders one building across several years:

    python street_sheet.py ../../fixtures/lt1-street.json out.png --ids 101 --years 1900,1935,1989 --styles strong
"""

import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [os.path.join(HERE, "..", "generators"), os.path.join(HERE, "..", "resolver")]

import bpy  # noqa: E402
from mathutils import Vector  # noqa: E402

import palette  # noqa: E402
import building  # noqa: E402
from resolve import resolve  # noqa: E402
from eras import DEFAULT_STYLE  # noqa: E402


def fresh_scene(name):
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


def light(scene):
    world = bpy.data.worlds.new("overcast")
    world.use_nodes = True
    bg = world.node_tree.nodes["Background"]
    bg.inputs["Color"].default_value = (0.66, 0.7, 0.76, 1.0)
    bg.inputs["Strength"].default_value = 0.7
    scene.world = world
    sun = bpy.data.lights.new("sun", "SUN")
    sun.energy = 2.6
    sun.angle = math.radians(6)
    sun.color = (1.0, 0.95, 0.88)
    ob = bpy.data.objects.new("sun", sun)
    ob.rotation_euler = (math.radians(55), 0, math.radians(-35))
    scene.collection.objects.link(ob)


def ground(scene, mat, x0, x1):
    me = bpy.data.meshes.new("ground")
    me.from_pydata([(x0, -30, 0), (x1, -30, 0), (x1, 40, 0), (x0, 40, 0)], [], [(0, 1, 2, 3)])
    uvl = me.uv_layers.new()
    u, v = palette.uv("ground")
    for loop in uvl.data:
        loop.uv = (u, v)
    me.materials.append(mat)
    ob = bpy.data.objects.new("ground", me)
    scene.collection.objects.link(ob)


def render_row(fixture, items, style, out, res, samples, mat=None):
    """items: [(building, year)]. Lines them up and renders one image."""
    scene = fresh_scene("street_" + style)
    mat = palette.material()
    light(scene)
    ws = fixture["worldSeed"]
    x = 0.0
    lo = None
    for bd, year in items:
        plan = resolve(bd, year, ws)
        if plan is None:
            continue
        ob = building.build(plan, style, material=mat)
        bb = [ob.matrix_world @ Vector(c) for c in ob.bound_box]
        xmin, xmax = min(p.x for p in bb), max(p.x for p in bb)
        ob.location.x = x - xmin
        x += (xmax - xmin) + 1.6
        lo = 0.0 if lo is None else lo
    width = x - 1.6
    ground(scene, mat, -8, width + 8)
    cam = bpy.data.cameras.new("cam")
    cam.lens = 35
    camo = bpy.data.objects.new("cam", cam)
    target = Vector((width / 2, 0, 5.0))
    direction = Vector((-0.12, -1.0, 0.12)).normalized()
    hfov = 2 * math.atan(36 / 2 / cam.lens)
    dist = (width / 2 + 3.0) / math.tan(hfov / 2) + 4.0
    camo.location = target + direction * dist
    camo.rotation_euler = (-direction).to_track_quat("-Z", "Y").to_euler()
    scene.collection.objects.link(camo)
    scene.camera = camo
    scene.render.engine = "CYCLES" if bpy.app.background else _eevee()
    if scene.render.engine == "CYCLES":
        scene.cycles.samples = samples
        scene.cycles.use_denoising = True
        scene.cycles.device = "CPU"
    scene.render.resolution_x, scene.render.resolution_y = res
    scene.render.resolution_percentage = 100
    scene.view_settings.view_transform = "AgX"
    scene.render.filepath = out
    bpy.ops.render.render(write_still=True)
    return out


def _eevee():
    ids = [e.identifier for e in bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items]
    return "BLENDER_EEVEE" if "BLENDER_EEVEE" in ids else "BLENDER_EEVEE_NEXT"


def tile(paths, labels, out, title):
    from PIL import Image, ImageDraw, ImageFont

    ims = [Image.open(p).convert("RGB") for p in paths]
    w = max(i.width for i in ims)
    pad, head = 70, 90
    H = head + sum(i.height + pad for i in ims)
    sheet = Image.new("RGB", (w, H), (236, 234, 228))
    d = ImageDraw.Draw(sheet)
    try:
        font = ImageFont.truetype("DejaVuSans.ttf", 34)
        big = ImageFont.truetype("DejaVuSans-Bold.ttf", 44)
    except OSError:
        font = big = ImageFont.load_default()
    d.text((24, 24), title, fill=(30, 30, 32), font=big)
    y = head
    for im, label in zip(ims, labels):
        d.text((24, y + 14), label, fill=(40, 40, 44), font=font)
        sheet.paste(im, (0, y + pad))
        y += im.height + pad
    sheet.save(out, quality=92)
    return out


def main(argv):
    fixture_path, out = argv[0], os.path.abspath(argv[1])
    opts = dict(zip(argv[2::2], argv[3::2]))
    fx = json.load(open(fixture_path))
    ids = [int(x) for x in opts.get("--ids", ",".join(str(b["id"]) for b in fx["buildings"])).split(",")]
    by_id = {b["id"]: b for b in fx["buildings"]}
    styles = opts.get("--styles", DEFAULT_STYLE).split(",")
    res = tuple(int(v) for v in opts.get("--res", "2400x900").split("x"))
    samples = int(opts.get("--samples", 24))
    tmp = os.path.splitext(out)[0]
    paths, labels = [], []
    if "--years" in opts:
        years = [int(y) for y in opts["--years"].split(",")]
        for style in styles:
            items = [(by_id[i], y) for i in ids for y in years]
            p = render_row(fx, items, style, f"{tmp}-{style}.png", res, samples)
            paths.append(p)
            labels.append(f"{style}:  " + "   ".join(f"{i} in {y}" for i in ids for y in years))
        title = f"One building through time ({', '.join(opts['--years'].split(','))})"
    else:
        year = int(opts.get("--year", 1989))
        for style in styles:
            items = [(by_id[i], year) for i in ids]
            p = render_row(fx, items, style, f"{tmp}-{style}.png", res, samples)
            paths.append(p)
            labels.append(f"{style}")
        title = f"{fx.get('street', 'Street')} in {year}: buildings {', '.join(str(i) for i in ids)}"
    return tile(paths, labels, out, title)


if __name__ == "__main__":
    argv = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else sys.argv[1:]
    print(main(argv))
