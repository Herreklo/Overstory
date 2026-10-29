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


def twinless(tiles, other):
    """A copy of `tiles` without the faces `other` repeats in place (within a millimetre): a caster only."""
    import bmesh
    from mathutils.bvhtree import BVHTree
    bm = bmesh.new()
    bm.from_mesh(other.data)
    bm.transform(tiles.matrix_world.inverted() @ other.matrix_world)
    tree = BVHTree.FromBMesh(bm)
    bm.free()
    bm = bmesh.new()
    bm.from_mesh(tiles.data)
    twins = [f for f in bm.faces if (lambda h: h[0] is not None and h[3] < 1e-3)(tree.find_nearest(f.calc_center_median()))]
    bmesh.ops.delete(bm, geom=twins, context="FACES")
    # named <level>cast_<material>: the page's material is read from the name after its level (ident)
    level, mat = tiles.name.split("_", 1)
    me = bpy.data.meshes.new(f"{level}cast_{mat}")
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new(me.name, me)
    o.matrix_world = tiles.matrix_world
    o.hide_render = True
    bpy.context.scene.collection.objects.link(o)
    print(f"[bake] {tiles.name}: {len(twins)} faces are {other.name}'s too, in place")
    return o


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
    # a window's mark from afar (house.py, window) is drawn only far off, in front of the window: never a caster, and
    # never a material of the page
    objs = {o.name: o for o in scene.objects if not o.name.endswith("_mark")}
    for o in scene.objects:
        if o.name.endswith("_mark"):
            o.hide_render = True
    mats = sorted({n.split("_", 1)[1] for n in objs if n != "bake_target"})
    FB.MATS[:] = mats + ["target"]  # the target last, so every material's index is the page's (bake.json mats)
    near = [o for n, o in objs.items() if n.startswith("near_") and n != "near_roof"]
    plane = objs.get("near_roof")
    target = objs.get("bake_target")
    tiles = [o for n, o in objs.items() if n in ("near_tiles", "bake_tiles")]
    for o in objs.values():
        lay = o.data.uv_layers
        lay.active = lay["page"]
        lay["page"].active_render = True
    # only the near level and the bake level's tiles cast; the near roof's planes stand in front of their tiles
    for n, o in objs.items():
        o.hide_render = n.startswith(("street_", "city_"))
    for p in (plane, target):
        # a target, never a caster: rays pass through it to the tiles under it
        if p is None:
            continue
        p.hide_render = False
        for k in ("visible_camera", "visible_diffuse", "visible_glossy", "visible_transmission", "visible_volume_scatter",
                  "visible_shadow"):
            setattr(p, k, False)
    # every course's chart from the tiles' top surface under it: the planes from the bake level's tiles, the near
    # tiles' own charts from the near tiles (their charts overlap where they lap, so baking them directly darkens them)
    transfers = [(p, src) for p, src in ((plane, "bake_tiles"), (target, "near_tiles")) if p is not None and src in objs]
    # the bake level's tiles cast with the near level; a house roofed in another way has none
    casters = near + [objs[n] for n in ("bake_tiles",) if n in objs]
    # some of the near level's tiles are the bake level's too, in place, and two coincident surfaces take each
    # other's every ray (the verge's pans baked half black): while one level's tiles are shaded, the other casts as a
    # copy without those twins, so every call sees each tile once
    pair = ("near_tiles", "bake_tiles")
    cast = {a: twinless(objs[a], objs[b]) for a, b in (pair, pair[::-1])} if set(pair) <= objs.keys() else {}
    casters += list(cast.values())

    def seen(src):
        """Who casts while `src`'s surface is shaded (None: the near level's own bake, its tiles among it)."""
        for n, c in cast.items():
            shaded = n == (src or "near_tiles")
            objs[n].hide_render, c.hide_render = not shaded, shaded

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
        for o in casters:
            FB.material(o, img, build)
        FB.select(near, near[0])
        seen(None)
        bpy.ops.object.bake(type="EMIT", margin=4, use_clear=False)
        # the planes from the tiles they stand for: the shading at the tiles' surface under each plane's texel
        for p, src in transfers:
            seen(src)
            FB.material(p, img, build)
            FB.select([objs[src], p], p)
            bpy.ops.object.bake(type="EMIT", margin=4, use_clear=False, use_selected_to_active=True,
                                cage_extrusion=0.01, max_ray_distance=0.12)
        FB.save(img, os.path.join(cache, f"{name}.exr"))
        print(f"[bake] {name}")

    if only != "roof":
        FB.sky_world(scene)
        scene.cycles.samples = 256
        img = FB.image("sky", size)
        for o in casters:
            FB.material(o, img, FB.white_diffuse)
        FB.select(near, near[0])
        seen(None)
        bpy.ops.object.bake(type="DIFFUSE", pass_filter={"DIRECT", "INDIRECT"}, margin=4, use_clear=False)
        for p, src in transfers:
            seen(src)
            FB.material(p, img, FB.white_diffuse)
            FB.select([objs[src], p], p)
            bpy.ops.object.bake(type="DIFFUSE", pass_filter={"DIRECT", "INDIRECT"}, margin=4, use_clear=False,
                                use_selected_to_active=True, cage_extrusion=0.01, max_ray_distance=0.12)
        FB.save(img, os.path.join(cache, "sky.exr"))
        print("[bake] sky")
    # the normals are the surfaces' own, not their shading: both levels' tiles as before, the copies out of it
    for n, c in cast.items():
        objs[n].hide_render, c.hide_render = False, True

    # every plane that stands for finer geometry, from that geometry: supersampled and box-filtered down, so a
    # 4 mm arris shades its texel by its share instead of by a single ray
    scene.cycles.samples = 4
    ss = meta["page"].get("normalSuper", 2)
    big = size * ss
    img = FB.image("street-normal", big)
    img.pixels.foreach_set([0.5, 0.5, 1.0, 0.0] * (big * big))
    flat = lambda nodes, links, obj: nodes.new("ShaderNodeBsdfDiffuse")  # noqa: E731
    pairs = [(["near_tiles", "bake_tiles"], ["near_roof", "street_roof", "street_tiles"], 0.12)]
    if only != "roof":
        pairs = [(["near_cladding"], ["street_cladding"], 0.05), (["near_stone"], ["street_stone"], 0.05)] + pairs
    for srcs, dsts, ray in pairs:
        srcs = [objs[n] for n in srcs if n in objs]
        if not srcs:
            continue
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
