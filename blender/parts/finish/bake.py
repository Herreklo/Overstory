"""Bake the corner's place page from its near level, and the street level's laps from the near boards.

    Blender -b --factory-startup -P blender/parts/finish/bake.py -- --gen <corner.py's out> --cache cache/finish

Reads corner.blend (corner.py) and writes float maps into the cache, each 1,024 square on the page (UV1):
  ao       occlusion within 0.6 m, real falloff (the AO node, outside)
  cavity   occlusion within 30 mm (outside); convex the same inside, so curvature is their difference
  sky      the upper sky's light on the surface, the sample shading itself (diffuse, direct, sky white above the
           horizon, black below)
  rest     the surface's rest position (+2 m, so it stays positive), before the frame's bends
  normal   its world normal, 0.5 + n / 2
  ident    R the piece's index, G the material's, B the arris flag (a chamfer face), A coverage
and street-normal.exr, the street level's tangent-space normal (OpenGL: +Y up), baked from the near boards and
stones onto the street level's cladding and plinth: their laps and pillows. The marks (marks.py) read the rest.
"""

import json
import os
import sys

import bpy
import numpy as np

MATS = ["cladding", "trims", "sheet", "batten", "stone", "tiles", "zinc"]


def args():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    out = {}
    for i in range(0, len(argv) - 1, 2):
        out[argv[i].lstrip("-")] = argv[i + 1]
    return out


def setup(scene, samples):
    scene.render.engine = "CYCLES"
    prefs = bpy.context.preferences.addons["cycles"].preferences
    try:
        prefs.compute_device_type = "METAL"
        prefs.get_devices()
        for d in prefs.devices:
            d.use = True
        scene.cycles.device = "GPU"
    except Exception:
        scene.cycles.device = "CPU"
    scene.cycles.samples = samples
    scene.cycles.use_denoising = False
    scene.cycles.max_bounces = 0
    scene.render.bake.margin = 4
    scene.render.bake.margin_type = "EXTEND"


def image(name, size, float_=True):
    img = bpy.data.images.new(name, size, size, alpha=True, float_buffer=float_)
    img.colorspace_settings.name = "Non-Color"
    img.pixels.foreach_set([0.0] * (size * size * 4))
    return img


def material(obj, img, build):
    """Give `obj` one material whose output is `build(nodes, links)` and whose active node is the bake target."""
    mat = bpy.data.materials.new(f"{obj.name}-{img.name}")
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    shader = build(nt.nodes, nt.links, obj)
    nt.links.new(shader.outputs[0], out.inputs["Surface"])
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = img
    nt.nodes.active = tex
    obj.data.materials.clear()
    obj.data.materials.append(mat)


def emission(colour_socket_fn):
    def build(nodes, links, obj):
        em = nodes.new("ShaderNodeEmission")
        em.inputs["Strength"].default_value = 1.0
        links.new(colour_socket_fn(nodes, links, obj), em.inputs["Color"])
        return em
    return build


def ao_socket(distance, inside):
    def f(nodes, links, obj):
        ao = nodes.new("ShaderNodeAmbientOcclusion")
        ao.samples = 16
        ao.inside = inside
        ao.only_local = False
        ao.inputs["Distance"].default_value = distance
        comb = nodes.new("ShaderNodeCombineXYZ")
        for k in "XYZ":
            links.new(ao.outputs["AO"], comb.inputs[k])
        return comb.outputs[0]
    return f


def rest_socket(nodes, links, obj):
    at = nodes.new("ShaderNodeAttribute")
    at.attribute_name = "rest"
    add = nodes.new("ShaderNodeVectorMath")
    add.operation = "ADD"
    add.inputs[1].default_value = (2.0, 2.0, 2.0)
    links.new(at.outputs["Vector"], add.inputs[0])
    return add.outputs[0]


def normal_socket(nodes, links, obj):
    geo = nodes.new("ShaderNodeNewGeometry")
    mad = nodes.new("ShaderNodeVectorMath")
    mad.operation = "MULTIPLY_ADD"
    mad.inputs[1].default_value = (0.5, 0.5, 0.5)
    mad.inputs[2].default_value = (0.5, 0.5, 0.5)
    links.new(geo.outputs["Normal"], mad.inputs[0])
    return mad.outputs[0]


def ident_socket(nodes, links, obj):
    piece = nodes.new("ShaderNodeAttribute")
    piece.attribute_name = "piece"
    col = nodes.new("ShaderNodeVertexColor")
    col.layer_name = "Col"
    sep = nodes.new("ShaderNodeSeparateColor")
    links.new(col.outputs["Color"], sep.inputs[0])
    comb = nodes.new("ShaderNodeCombineXYZ")
    links.new(piece.outputs["Fac"], comb.inputs["X"])
    comb.inputs["Y"].default_value = float(MATS.index(obj.name.split("_", 1)[1]))
    links.new(sep.outputs[0], comb.inputs["Z"])
    return comb.outputs[0]


def white_diffuse(nodes, links, obj):
    d = nodes.new("ShaderNodeBsdfDiffuse")
    d.inputs["Color"].default_value = (1, 1, 1, 1)
    return d


def sky_world(scene):
    w = bpy.data.worlds.new("sky")
    w.use_nodes = True
    nt = w.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputWorld")
    bg = nt.nodes.new("ShaderNodeBackground")
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    gt = nt.nodes.new("ShaderNodeMath")
    gt.operation = "GREATER_THAN"
    gt.inputs[1].default_value = 0.0
    nt.links.new(tc.outputs["Generated"], sep.inputs[0])
    nt.links.new(sep.outputs["Z"], gt.inputs[0])
    nt.links.new(gt.outputs[0], bg.inputs["Strength"])
    bg.inputs["Color"].default_value = (1, 1, 1, 1)
    nt.links.new(bg.outputs[0], out.inputs["Surface"])
    scene.world = w


def select(objs, active):
    for o in bpy.context.scene.objects:
        o.select_set(o in objs)
    bpy.context.view_layer.objects.active = active


def save(img, path):
    img.filepath_raw = path
    img.file_format = "OPEN_EXR"
    img.save()


def main():
    a = args()
    gen, cache = os.path.abspath(a["gen"]), os.path.abspath(a["cache"])
    os.makedirs(cache, exist_ok=True)
    bpy.ops.wm.open_mainfile(filepath=os.path.join(gen, "corner.blend"))
    meta = json.load(open(os.path.join(gen, "corner.json")))
    size = meta["page"]["size"]
    scene = bpy.context.scene
    setup(scene, 64)
    near = [o for o in scene.objects if o.name.startswith("near_")]
    street = {o.name.split("_", 1)[1]: o for o in scene.objects if o.name.startswith("street_")}
    for o in scene.objects:
        lay = o.data.uv_layers
        lay.active = lay["page"]
        lay["page"].active_render = True
    # street objects stay out of the near bakes' rays
    for o in street.values():
        o.hide_render = True

    maps = {
        "ao": (emission(ao_socket(0.6, False)), 64),
        "cavity": (emission(ao_socket(0.03, False)), 64),
        "convex": (emission(ao_socket(0.03, True)), 64),
        "rest": (emission(rest_socket), 1),
        "normal": (emission(normal_socket), 1),
        "ident": (emission(ident_socket), 1),
    }
    for name, (build, samples) in maps.items():
        scene.cycles.samples = samples
        img = image(name, size)
        for o in near:
            material(o, img, build)
        select(near, near[0])
        bpy.ops.object.bake(type="EMIT", margin=4, use_clear=False)
        save(img, os.path.join(cache, f"{name}.exr"))
        print(f"[bake] {name}")

    sky_world(scene)
    scene.cycles.samples = 256
    img = image("sky", size)
    for o in near:
        material(o, img, white_diffuse)
    select(near, near[0])
    bpy.ops.object.bake(type="DIFFUSE", pass_filter={"DIRECT", "INDIRECT"}, margin=4, use_clear=False)
    save(img, os.path.join(cache, "sky.exr"))
    print("[bake] sky")

    # the street level's laps and pillows: near onto street, tangent space on the page's UVs, baked at four times
    # the page and box-filtered down, so a 4 mm arris shades its texel by its share instead of by a single ray
    scene.cycles.samples = 4
    ss = 4
    big = size * ss
    img = image("street-normal", big)
    img.pixels.foreach_set([0.5, 0.5, 1.0, 0.0] * (big * big))
    flat = lambda nodes, links, obj: nodes.new("ShaderNodeBsdfDiffuse")  # noqa: E731
    for kind in ("cladding", "stone"):
        src = scene.objects[f"near_{kind}"]
        dst = street[kind]
        dst.hide_render = False
        material(dst, img, flat)
        material(src, image(f"unused-{kind}", 8), flat)
        select([src, dst], dst)
        bpy.ops.object.bake(type="NORMAL", normal_space="TANGENT", normal_r="POS_X", normal_g="POS_Y",
                            normal_b="POS_Z", use_selected_to_active=True, cage_extrusion=0.02,
                            max_ray_distance=0.05, margin=4 * ss, use_clear=False)
        dst.hide_render = True
        print(f"[bake] street normal: {kind}")
    px = np.empty(big * big * 4, np.float32)
    img.pixels.foreach_get(px)
    n = px.reshape(size, ss, size, ss, 4)[..., :3] * 2.0 - 1.0
    n = n.mean(axis=(1, 3))
    n /= np.maximum(np.linalg.norm(n, axis=-1, keepdims=True), 1e-6)
    cover = px.reshape(size, ss, size, ss, 4)[..., 3].max(axis=(1, 3))
    small = image("street-normal-1x", size)
    out = np.concatenate([n * 0.5 + 0.5, cover[..., None]], axis=-1)
    small.pixels.foreach_set(out.ravel())
    save(small, os.path.join(cache, "street-normal.exr"))
    print(f"[bake] wrote {cache}")


main()
