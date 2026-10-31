"""Bake a rock part's page from its near level, as the street's bake bakes a house's (blender/parts/street/bake.py).

    Blender -b --factory-startup -P blender/parts/rock/kit/bake.py -- --gen cache/rock/kit/gen/slab-block --cache cache/rock/kit/bake/slab-block

Reads house.blend and house.json (part.py) and writes the finishing test's float maps (ao, cavity, convex, rest,
normal, ident, sky; finish/bake.py's nodes, called as they are) from the near level, and street-normal: the near
level's rounds and folds baked onto the street level's faces in their tangent space, as the street level's cladding
takes the near boards'. As the house's, no ground is in the bake: the foot's dark is the paint's junction rule.

A sculpted mass's house.blend (game.py) holds its high-poly beside the levels as `high_<material>`: then every map is the
high-poly's, baked onto the near and the street levels' faces on their one page (selected to active, the cage and
reach house.json's `high.rays`), its occlusion its own (the levels take the bake, never shade it), and each level
takes its own tangent-space normal from it: near-normal and street-normal.
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
    if any(n.startswith("high_") for n in objs):
        return bake_high(scene, objs, meta, cache, size, mats)
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


def ao_own(distance, inside):
    """finish/bake.py's occlusion, the high-poly's own: the levels beside it never shade it."""
    def f(nodes, links, obj):
        sock = FB.ao_socket(distance, inside)(nodes, links, obj)
        for n in nodes:
            if n.type == "AMBIENT_OCCLUSION":
                n.only_local = True
        return sock
    return f


def bake_high(scene, objs, meta, cache, size, mats):
    high = next(o for n, o in objs.items() if n.startswith("high_")); rays = meta["high"]["rays"]
    lv = {k: next(o for n, o in objs.items() if n.startswith(k + "_")) for k in ("near", "street")}
    for o in objs.values():
        o.hide_render = o.name.startswith("city_")
        if o is not high:
            o.data.uv_layers.active = o.data.uv_layers["page"]; o.data.uv_layers["page"].active_render = True
            o.visible_shadow = o.visible_diffuse = o.visible_glossy = o.visible_transmission = o.visible_volume_scatter = False
    flat = lambda nodes, links, obj: nodes.new("ShaderNodeBsdfDiffuse")  # noqa: E731

    def onto(img, build, kind, levels, margin=4, **kw):
        FB.material(high, img, build)
        for k in levels:
            FB.material(lv[k], img, flat); FB.select([high, lv[k]], lv[k])
            bpy.ops.object.bake(type=kind, use_selected_to_active=True, cage_extrusion=rays[k][0], max_ray_distance=rays[k][1],
                                margin=margin, use_clear=False, **kw)

    maps = {
        "ao": (FB.emission(ao_own(0.6, False)), 64),
        "cavity": (FB.emission(ao_own(0.03, False)), 256),  # a step's shallow floor is half open: fewer samples speckle it
        "convex": (FB.emission(ao_own(0.03, True)), 256),
        "rest": (FB.emission(FB.rest_socket), 1),
        "normal": (FB.emission(FB.normal_socket), 1),
        "ident": (FB.emission(FB.ident_socket), 1),
    }
    for name, (build, samples) in maps.items():
        scene.cycles.samples = samples; img = FB.image(name, size)
        onto(img, build, "EMIT", ("near", "street"))
        FB.save(img, os.path.join(cache, f"{name}.exr")); print(f"[bake] {name} (high)")
    FB.sky_world(scene); scene.cycles.samples = 256; img = FB.image("sky", size)
    onto(img, FB.white_diffuse, "DIFFUSE", ("near", "street"), pass_filter={"DIRECT", "INDIRECT"})
    FB.save(img, os.path.join(cache, "sky.exr")); print("[bake] sky (high)")

    # each level's own normal from the high-poly, supersampled and box-filtered down as the street's
    scene.cycles.samples = 4; ss = meta["page"].get("normalSuper", 2); big = size * ss
    for k in ("near", "street"):
        img = FB.image(f"{k}-normal", big); img.pixels.foreach_set([0.5, 0.5, 1.0, 0.0] * (big * big))
        onto(img, flat, "NORMAL", (k,), margin=4 * ss, normal_space="TANGENT", normal_r="POS_X", normal_g="POS_Y", normal_b="POS_Z")
        px = np.empty(big * big * 4, np.float32); img.pixels.foreach_get(px)
        n = (px.reshape(size, ss, size, ss, 4)[..., :3] * 2.0 - 1.0).mean(axis=(1, 3))
        n /= np.maximum(np.linalg.norm(n, axis=-1, keepdims=True), 1e-6)
        cover = px.reshape(size, ss, size, ss, 4)[..., 3].max(axis=(1, 3))
        small = FB.image(f"{k}-normal-1x", size)
        small.pixels.foreach_set(np.concatenate([n * 0.5 + 0.5, cover[..., None]], axis=-1).ravel())
        FB.save(small, os.path.join(cache, f"{k}-normal.exr")); print(f"[bake] {k} normal (high)")
    with open(os.path.join(cache, "bake.json"), "w") as fh:
        json.dump({"mats": mats, "size": size, "normalSuper": ss, "high": True}, fh)
    print(f"[bake] wrote {cache}")


main()
