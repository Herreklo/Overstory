"""Bake a house's page from its near level (blender/parts/finish/bake.py grown to a whole house).

    Blender -b --factory-startup -P blender/parts/street/bake.py -- --gen cache/street/gen/107 --cache cache/street/bake/107
        [--only roof]

Reads house.blend and house.json (house.py) and writes float maps into the cache, each the page's size (UV1):
  ao, cavity, convex, rest, normal, ident, sky   as the finishing test's (blender/parts/finish/bake.py)
  street-normal   the tangent-space normal (OpenGL: +Y up) of every plane that stands for finer geometry, baked from
                  that geometry: the street level's cladding and plinth from the near boards and stones, and the roof's
                  course planes (at both levels) from the real tiles
A roof course drawn as a plane takes its occlusion, cavity, rest, normal and ident from the bake level's tiles it stands
for (selected to active), so its pans are dark where the tiles' are. `--only roof` bakes only what the roof needs
(ao and street-normal), for a look at the roof alone.
"""

import json
import os
import sys

import bpy
import numpy as np



def finish_bake():
    """The finishing test's bake (blender/parts/finish/bake.py): its nodes and helpers, without running its main."""
    import types
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "finish", "bake.py")
    src = open(path).read().rsplit("\nmain()", 1)[0]
    mod = types.ModuleType("finish_bake")
    exec(compile(src, path, "exec"), mod.__dict__)
    return mod


FB = finish_bake()


def main():
    a = FB.args()
    gen, cache = os.path.abspath(a["gen"]), os.path.abspath(a["cache"])
    only = a.get("only")
    os.makedirs(cache, exist_ok=True)
    bpy.ops.wm.open_mainfile(filepath=os.path.join(gen, "house.blend"))
    meta = json.load(open(os.path.join(gen, "house.json")))
    size = meta["page"]["size"]
    scene = bpy.context.scene
    FB.setup(scene, 64)
    objs = {o.name: o for o in scene.objects}
    mats = sorted({n.split("_", 1)[1] for n in objs})
    FB.MATS[:] = mats
    near = [o for n, o in objs.items() if n.startswith("near_") and n != "near_roof"]
    plane = objs.get("near_roof")
    tiles = [o for n, o in objs.items() if n in ("near_tiles", "bake_tiles")]
    for o in objs.values():
        lay = o.data.uv_layers
        lay.active = lay["page"]
        lay["page"].active_render = True
    # only the near level and the bake level's tiles cast; the near roof's planes stand in front of their tiles
    for n, o in objs.items():
        o.hide_render = n.startswith("street_")
    if plane is not None:
        # a target, never a caster: rays pass through it to the tiles under it
        for k in ("visible_camera", "visible_diffuse", "visible_glossy", "visible_transmission", "visible_volume_scatter",
                  "visible_shadow"):
            setattr(plane, k, False)

    maps = {
        "ao": (FB.emission(FB.ao_socket(0.6, False)), 64),
        "cavity": (FB.emission(FB.ao_socket(0.03, False)), 64),
        "convex": (FB.emission(FB.ao_socket(0.03, True)), 64),
        "rest": (FB.emission(FB.rest_socket), 1),
        "normal": (FB.emission(FB.normal_socket), 1),
        "ident": (FB.emission(FB.ident_socket), 1),
    }
    if only == "roof":
        maps = {"ao": maps["ao"]}
    for name, (build, samples) in maps.items():
        scene.cycles.samples = samples
        img = FB.image(name, size)
        for o in near + [objs["bake_tiles"]]:
            FB.material(o, img, build)
        FB.select(near, near[0])
        bpy.ops.object.bake(type="EMIT", margin=4, use_clear=False)
        # the planes from the tiles they stand for: the shading at the tiles' surface under each plane's texel
        if plane is not None:
            FB.material(plane, img, build)
            FB.select([objs["bake_tiles"], plane], plane)
            bpy.ops.object.bake(type="EMIT", margin=4, use_clear=False, use_selected_to_active=True,
                                cage_extrusion=0.01, max_ray_distance=0.12)
        FB.save(img, os.path.join(cache, f"{name}.exr"))
        print(f"[bake] {name}")

    if only != "roof":
        FB.sky_world(scene)
        scene.cycles.samples = 256
        img = FB.image("sky", size)
        for o in near + [objs["bake_tiles"]]:
            FB.material(o, img, FB.white_diffuse)
        FB.select(near, near[0])
        bpy.ops.object.bake(type="DIFFUSE", pass_filter={"DIRECT", "INDIRECT"}, margin=4, use_clear=False)
        if plane is not None:
            FB.material(plane, img, FB.white_diffuse)
            FB.select([objs["bake_tiles"], plane], plane)
            bpy.ops.object.bake(type="DIFFUSE", pass_filter={"DIRECT", "INDIRECT"}, margin=4, use_clear=False,
                                use_selected_to_active=True, cage_extrusion=0.01, max_ray_distance=0.12)
        FB.save(img, os.path.join(cache, "sky.exr"))
        print("[bake] sky")

    # every plane that stands for finer geometry, from that geometry: supersampled and box-filtered down, so a
    # 4 mm arris shades its texel by its share instead of by a single ray
    scene.cycles.samples = 4
    ss = meta["page"].get("normalSuper", 2)
    big = size * ss
    img = FB.image("street-normal", big)
    img.pixels.foreach_set([0.5, 0.5, 1.0, 0.0] * (big * big))
    flat = lambda nodes, links, obj: nodes.new("ShaderNodeBsdfDiffuse")  # noqa: E731
    pairs = [([objs["near_tiles"], objs["bake_tiles"]], ["near_roof", "street_roof", "street_tiles"], 0.12)]
    if only != "roof":
        pairs = [([objs["near_cladding"]], ["street_cladding"], 0.05), ([objs["near_stone"]], ["street_stone"], 0.05)] + pairs
    for srcs, dsts, ray in pairs:
        for s in srcs:
            FB.material(s, FB.image(f"unused-{s.name}", 8), flat)
        for dn in dsts:
            if dn not in objs:
                continue
            dst = objs[dn]
            dst.hide_render = False
            FB.material(dst, img, flat)
            FB.select(srcs + [dst], dst)
            bpy.ops.object.bake(type="NORMAL", normal_space="TANGENT", normal_r="POS_X", normal_g="POS_Y",
                                normal_b="POS_Z", use_selected_to_active=True, cage_extrusion=0.02,
                                max_ray_distance=ray, margin=4 * ss, use_clear=False)
            dst.hide_render = True
            print(f"[bake] street normal: {dn}")
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
        json.dump({"mats": mats, "size": size, "normalSuper": ss, "only": only}, fh)
    print(f"[bake] wrote {cache}")


main()
