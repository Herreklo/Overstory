"""The stair generator's variety sheet (docs/foundations.md, the judging; docs/experiments.md, LT1, the second part: no
two flights alike, every difference saying something true): every chosen flight in the town plan built from its facts
(blender/generators/stair_facts.py) and rendered alone, looking up it from below and to one side, in a quick preview
shader that shows the history channels as colour (lichen pale, moss green, polish darker, cement grey, a joint's soil
brown). It judges variety and truth, not beauty, which is judged in Unity.

    blender -b --factory-startup --python blender/tools/stair_variety.py -- OUTDIR [lane name ...]

Writes one tile a flight, OUTDIR/<n>.png, and OUTDIR/facts.json with each flight's facts.
"""

import json
import math
import os
import sys

import bpy
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "generators"))
sys.path.insert(0, os.path.join(HERE, "..", "blockouts"))
import stone as ST  # noqa: E402
import stair_facts as SF  # noqa: E402

DEFAULT = ["Gully Steps", "Tanner's Steps", "Bishop's Steps", "the Hundred Steps", "the path to Lookout Park",
           "passage at -172", "passage at 92", "passage at 110", "stair-lane 2", "stair-lane 6",
           "the way to D (1107, empty since 1986)", "the Crack"]


def preview_material():
    """The history channels as colour, on a slate grey."""
    m = bpy.data.materials.new("history")
    m.use_nodes = True
    nt = m.node_tree
    bsdf = nt.nodes["Principled BSDF"]
    bsdf.inputs["Roughness"].default_value = 0.8

    def attr(name):
        a = nt.nodes.new("ShaderNodeAttribute")
        a.attribute_name = name
        sep = nt.nodes.new("ShaderNodeSeparateXYZ")
        nt.links.new(a.outputs["Vector"], sep.inputs[0])
        return sep

    def mix(a, b, f):
        m_ = nt.nodes.new("ShaderNodeMix")
        m_.data_type = "RGBA"
        nt.links.new(f, m_.inputs["Factor"])
        if isinstance(a, tuple):
            m_.inputs[6].default_value = a
        else:
            nt.links.new(a, m_.inputs[6])
        m_.inputs[7].default_value = b
        return m_.outputs[2]

    def math_(op, x, v=None, clamp=True):
        n = nt.nodes.new("ShaderNodeMath")
        n.operation = op
        n.use_clamp = clamp
        nt.links.new(x, n.inputs[0])
        if v is not None:
            n.inputs[1].default_value = v
        return n.outputs[0]

    u4, u5, u2 = attr("uv4"), attr("uv5"), attr("uv2")
    col = (0.11, 0.115, 0.12, 1.0)
    # polish: the worn line darker
    c = mix(col, (0.07, 0.072, 0.075, 1.0), math_("MULTIPLY", u4.outputs["X"], 0.8))
    # lichen: its years as a pale film (the coverage its years give, about a third of a quiet place at a century)
    c = mix(c, (0.42, 0.43, 0.39, 1.0), math_("MULTIPLY", math_("SUBTRACT", u4.outputs["Y"], 0.05), 1.0))
    # moss
    c = mix(c, (0.07, 0.12, 0.02, 1.0), math_("MULTIPLY", u5.outputs["X"], 1.2))
    # cement (kind 4, 5) and a joint's soil (kind 6)
    c = mix(c, (0.32, 0.31, 0.29, 1.0), math_("GREATER_THAN", u2.outputs["X"], 3.5))
    c = mix(c, (0.05, 0.045, 0.035, 1.0), math_("GREATER_THAN", u2.outputs["X"], 5.5))
    nt.links.new(c, bsdf.inputs["Base Color"])
    return m


def render_flight(lane, spec, out, mat):
    for ob in list(bpy.data.objects):
        bpy.data.objects.remove(ob, do_unlink=True)
    meshes, origin = ST.lay(spec)
    obs = [ST.make(name, m) for name, m in meshes]
    for ob in obs:
        ob.data.materials.append(mat)
    # every flight from the same place: a person at its foot, a little to one side, looking up its first metres (the
    # mesh is laid from the first flight's foot at the origin)
    fl = ST.flights_of(lane)
    d = (fl[0]["b"] - fl[0]["a"])[:2]
    run = float(np.linalg.norm(d))
    d = d / max(run, 1e-6)
    slope = float(fl[0]["b"][2] - fl[0]["a"][2]) / max(run, 1e-6)
    right = np.array([d[1], -d[0]])
    cam_pos = np.array([-d[0] * 3.2 + right[0] * 0.9, -d[1] * 3.2 + right[1] * 0.9, 1.65])
    c = np.array([d[0] * 3.0, d[1] * 3.0, slope * 3.0 * 0.75 + 0.2])
    sc = bpy.context.scene
    cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
    cam.data.lens = 28
    cam.location = cam_pos
    dv = c - cam_pos
    cam.rotation_euler = (math.atan2(math.hypot(dv[0], dv[1]), -dv[2]), 0, math.atan2(dv[1], dv[0]) - math.pi / 2)
    sc.collection.objects.link(cam)
    sc.camera = cam
    bpy.ops.render.render(write_still=False)
    sc.render.filepath = out
    bpy.ops.render.render(write_still=True)


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    outdir = argv[0] if argv else "/tmp/stair_variety"
    names = argv[1:] or DEFAULT
    os.makedirs(outdir, exist_ok=True)
    import heart_layout as H
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    sc.cycles.samples = 24
    sc.cycles.device = "CPU"
    sc.render.resolution_x, sc.render.resolution_y = 720, 480
    sc.view_settings.view_transform = "Standard"
    sc.world = bpy.data.worlds.new("w")
    sc.world.use_nodes = True
    sc.world.node_tree.nodes["Background"].inputs[0].default_value = (0.55, 0.57, 0.6, 1)
    sc.world.node_tree.nodes["Background"].inputs[1].default_value = 1.0
    mat = preview_material()
    facts = []
    for k, name in enumerate(names):
        lane = next((l for l in H.LANES if l["name"] == name), None)
        if lane is None:
            continue
        spec = SF.facts_for(lane)
        if spec is None:
            continue
        sun = bpy.data.lights.get("sun") or bpy.data.lights.new("sun", "SUN")
        render_flight(lane, spec, os.path.join(outdir, f"{k:02d}.png"), mat)
        sob = bpy.data.objects.new("sun", sun)
        sun.energy = 2.5
        sob.rotation_euler = (math.radians(55), 0, math.radians(30))
        sc.collection.objects.link(sob)
        bpy.ops.render.render(write_still=True)
        facts.append(dict(tile=k, name=name, built=spec["built"], built_as=spec.get("built_as"),
                          finish=spec.get("finish", "split"), footfall=spec["footfall"],
                          keepers=[(u["by"], u["since"], u["care"]) for u in spec["upkeep"]],
                          works=[(w["kind"], w["year"]) for w in spec["works"]]))
        print("FLIGHT", k, name, spec["built"], spec.get("finish"), spec["footfall"])
    with open(os.path.join(outdir, "facts.json"), "w") as fh:
        json.dump(facts, fh, indent=1)


main()
