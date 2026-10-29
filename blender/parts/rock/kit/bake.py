"""Bake a rock part's page from its near level, as the street's bake bakes a house's (blender/parts/street/bake.py).

    Blender -b --factory-startup -P blender/parts/rock/kit/bake.py -- --gen cache/rock/kit/gen/slab-block --cache cache/rock/kit/bake/slab-block

Reads house.blend and house.json (part.py) and writes the finishing test's float maps (ao, cavity, convex, rest,
normal, ident, sky; finish/bake.py's nodes, called as they are) from the near level, and street-normal: the near
level's rounds and folds baked onto the street level's faces in their tangent space, as the street level's cladding
takes the near boards'. As the house's, no ground is in the bake: the foot's dark is the paint's junction rule.
"""

import json
import os
import sys

import bpy
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))


def finish_bake():
    """The finishing test's bake (blender/parts/finish/bake.py): its nodes and helpers, without running its main."""
    import types
    path = os.path.join(ROOT, "blender", "parts", "finish", "bake.py")
    src = open(path).read().rsplit("\nmain()", 1)[0]
    mod = types.ModuleType("finish_bake")
    exec(compile(src, path, "exec"), mod.__dict__)
    return mod


FB = finish_bake()


def main():
    a = FB.args()
    gen, cache = os.path.abspath(a["gen"]), os.path.abspath(a["cache"])
    os.makedirs(cache, exist_ok=True)
    bpy.ops.wm.open_mainfile(filepath=os.path.join(gen, "house.blend"))
    meta = json.load(open(os.path.join(gen, "house.json")))
    size = meta["page"]["size"]
    scene = bpy.context.scene
    FB.setup(scene, 64)
    objs = {o.name: o for o in scene.objects}
    mats = sorted({n.split("_", 1)[1] for n in objs})
    FB.MATS[:] = mats
    near = [o for n, o in objs.items() if n.startswith("near_")]
    for o in objs.values():
        lay = o.data.uv_layers
        lay.active = lay["page"]
        lay["page"].active_render = True
        o.hide_render = not o.name.startswith("near_")
    casters = near

    maps = {
        "ao": (FB.emission(FB.ao_socket(0.6, False)), 64),
        "cavity": (FB.emission(FB.ao_socket(0.03, False)), 64),
        "convex": (FB.emission(FB.ao_socket(0.03, True)), 64),
        "rest": (FB.emission(FB.rest_socket), 1),
        "normal": (FB.emission(FB.normal_socket), 1),
        "ident": (FB.emission(FB.ident_socket), 1),
    }
    for name, (build, samples) in maps.items():
        scene.cycles.samples = samples
        img = FB.image(name, size)
        for o in casters:
            FB.material(o, img, build)
        FB.select(near, near[0])
        bpy.ops.object.bake(type="EMIT", margin=4, use_clear=False)
        FB.save(img, os.path.join(cache, f"{name}.exr"))
        print(f"[bake] {name}")

    FB.sky_world(scene)
    scene.cycles.samples = 256
    img = FB.image("sky", size)
    for o in casters:
        FB.material(o, img, FB.white_diffuse)
    FB.select(near, near[0])
    bpy.ops.object.bake(type="DIFFUSE", pass_filter={"DIRECT", "INDIRECT"}, margin=4, use_clear=False)
    FB.save(img, os.path.join(cache, "sky.exr"))
    print("[bake] sky")

    # the near level's forms onto the street level, supersampled and box-filtered down as the street's
    scene.cycles.samples = 4
    ss = meta["page"].get("normalSuper", 2)
    big = size * ss
    img = FB.image("street-normal", big)
    img.pixels.foreach_set([0.5, 0.5, 1.0, 0.0] * (big * big))
    flat = lambda nodes, links, obj: nodes.new("ShaderNodeBsdfDiffuse")  # noqa: E731
    for m in mats:
        src, dst = objs.get(f"near_{m}"), objs.get(f"street_{m}")
        if src is None or dst is None:
            continue
        FB.material(src, FB.image(f"unused-{src.name}", 8), flat)
        dst.hide_render = False
        FB.material(dst, img, flat)
        FB.select([src, dst], dst)
        bpy.ops.object.bake(type="NORMAL", normal_space="TANGENT", normal_r="POS_X", normal_g="POS_Y",
                            normal_b="POS_Z", use_selected_to_active=True, cage_extrusion=0.05,
                            max_ray_distance=0.15, margin=4 * ss, use_clear=False)
        dst.hide_render = True
        print(f"[bake] street normal: {dst.name}")
    px = np.empty(big * big * 4, np.float32)
    img.pixels.foreach_get(px)
    n = px.reshape(size, ss, size, ss, 4)[..., :3] * 2.0 - 1.0
    n = n.mean(axis=(1, 3))
    n /= np.maximum(np.linalg.norm(n, axis=-1, keepdims=True), 1e-6)
    cover = px.reshape(size, ss, size, ss, 4)[..., 3].max(axis=(1, 3))
    small = FB.image("street-normal-1x", size)
    small.pixels.foreach_set(np.concatenate([n * 0.5 + 0.5, cover[..., None]], axis=-1).ravel())
    FB.save(small, os.path.join(cache, "street-normal.exr"))
    with open(os.path.join(cache, "bake.json"), "w") as fh:
        json.dump({"mats": mats, "size": size, "normalSuper": ss}, fh)
    print(f"[bake] wrote {cache}")


main()
