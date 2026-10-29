"""The Bluff's target frame: the grey Bluff (bluff.py) at the street stop with its landscape, in one designed light.

What the clay cannot carry is drawn by the rules the rock and the land will use, each a broad value shape: the
phyllite's foliation bands and the shore's lichen bands (target.py's rock), the turf on the top in Jæren's greens with
real grass along the crest and near the eye, an earth scarp under the turf's edge, the Roads in waves from the north-
west with white water where they meet the foot, fields walled in stone on the far shores, the air between in haze,
people at true size. It is a target, heavier than the game; the rock itself is the game's (bluff.py's budget).

    Blender -b --factory-startup -P blender/parts/rock/target_bluff.py -- --out DIR [--view shore] [--w 1600] [--h 900]
        [--samples 64] [--exposure -0.8] [--pos x,y[,z]] [--target x,y,z] [--lens 30]
"""

import math
import os
import sys
import time

import bpy
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bluff as BL  # noqa: E402
import cliff as CF  # noqa: E402
import hashing as HS  # noqa: E402
import target as T  # noqa: E402

LIGHT = BL.FIX["lights"]["lowsun"]
T.SUN = {"azimuth": LIGHT["azimuth"], "elevation": LIGHT["elevation"], "color": LIGHT["color"],
         "energy": LIGHT["energy"]}
COL = dict(T.COL)
COL.update({
    "turf": (0.050, 0.120, 0.022), "turf-pale": (0.115, 0.170, 0.040), "turf-deep": (0.028, 0.070, 0.016),
    "earth": (0.060, 0.040, 0.024), "sand": (0.40, 0.34, 0.24), "hay": (0.20, 0.17, 0.06),
    "wall": (0.035, 0.035, 0.032), "grass": (0.060, 0.150, 0.025), "foam": (0.78, 0.80, 0.79),
    "sea-deep": (0.006, 0.020, 0.024),
})
CLOTHES = [(0.45, 0.025, 0.02), (0.55, 0.38, 0.03), (0.025, 0.04, 0.11), (0.10, 0.17, 0.07), (0.40, 0.40, 0.38)]


def attr(g, name):
    return g.out(g.node("ShaderNodeAttribute", attribute_name=name), "Fac")


def eq(g, v, k):
    n = g.node("ShaderNodeMath", operation="COMPARE")
    g.put(n.inputs[0], v)
    n.inputs[1].default_value = k
    n.inputs[2].default_value = 0.5
    return n.outputs[0]


def rock_material(fol):
    """The phyllite, answering light by what each face is (bluff.py writes it per face). Its foliation faces carry the
    mica's silky lustre (smoother, a little silvery); faces across the foliation are matte and show the lamination as
    fine ribs. Open joints, long wet with seepage, are stained rust by the iron; a face bared lately (a fall's scar,
    its blocks' breaks) is pale blue-grey and clean, and lichens come with the years; worn edges are lighter where
    they are abraded. Over it the shore's bands by height (target.py), and below the tide the rock is wet and dark.
    The foliation's own normal `fol` sets its broad bands of graphite, grey-green chlorite and silvery sericite."""
    m, g, bsdf = T.material("phyllite")
    P, N, x, y, z, nz = T.geometry(g)
    plane, gap, age = attr(g, "plane"), attr(g, "gap"), attr(g, "age")
    dot = g.node("ShaderNodeVectorMath", operation="DOT_PRODUCT")
    g.put(dot.inputs[0], P)
    dot.inputs[1].default_value = tuple(float(v) for v in fol)
    f = g.out(dot, "Value")
    band = g.noise(None, 1.0, 2.0, 0.45, dims="1D", w=g.math("MULTIPLY", f, 0.22))
    base = g.mix(g.ss(band, 0.40, 0.52), COL["graphite"], COL["chlorite"])
    base = g.mix(g.ss(band, 0.60, 0.70), base, (0.23, 0.235, 0.22))
    on_fol = eq(g, plane, 0.0)
    base = g.mix(g.math("MULTIPLY", on_fol, 0.35), base, (0.24, 0.25, 0.24))  # the mica's silver on its own planes
    fresh = g.ss(age, 160.0, 15.0)
    opened = g.math("MULTIPLY", g.ss(gap, 0.03, 0.12), g.math("SUBTRACT", 1.0, fresh))
    rust_patch = g.ss(g.noise(P, 0.45, 2.0, 0.6), 0.42, 0.62)
    base = g.mix(g.math("MULTIPLY", g.math("MULTIPLY", opened, rust_patch), 0.85), base, (0.17, 0.075, 0.03))
    worn = eq(g, plane, 6.0)
    base = g.mix(g.math("MULTIPLY", worn, 0.45), base, g.scale(base, 1.9))
    # moss and grass only in hollows above the spray
    ao = g.node("ShaderNodeAmbientOcclusion", {"Distance": 0.9}, samples=8)
    hollow = g.ss(g.out(ao, "AO"), 0.62, 0.40)
    green = g.math("MULTIPLY", g.math("MULTIPLY", hollow, g.ss(z, 3.0, 3.8)), g.ss(nz, 0.45, 0.8))
    c, wet = T.sea_bands(g, base, P, z, nz, exposure=1.0)
    c = g.mix(green, c, COL["turf-deep"])
    clean = g.mix(g.ss(band, 0.4, 0.7), (0.15, 0.16, 0.17), (0.22, 0.23, 0.24))  # a fresh fracture: pale, unlichened
    c = g.mix(g.math("MULTIPLY", fresh, 0.9), c, clean)
    g.put(bsdf.inputs["Base Color"], c)
    rough = g.mixf(on_fol, 0.78, 0.36)
    g.put(bsdf.inputs["Roughness"], g.mixf(wet, rough, 0.14))
    # the lamination: fine ribs across the foliation, and the joint face's own waviness
    lam = g.noise(None, 1.0, 1.0, 0.5, dims="1D", w=g.math("MULTIPLY", f, 9.0))
    wav = g.noise(P, 0.5, 2.0, 0.55)
    h = g.math("ADD", g.math("MULTIPLY", lam, g.math("SUBTRACT", 1.0, on_fol)), g.math("MULTIPLY", wav, 3.0))
    bump = g.node("ShaderNodeBump", {"Strength": 0.35, "Distance": 0.03, "Height": h})
    g.put(bsdf.inputs["Normal"], g.out(bump, "Normal"))
    return m


def turf_material():
    m, g, bsdf = T.material("turf")
    P, N, x, y, z, nz = T.geometry(g)
    big = g.noise(g.scale(P, 1.0), 0.025, 1.0)
    mid = g.noise(P, 0.18, 2.0, 0.5)
    c = g.mix(g.ss(big, 0.35, 0.65), COL["turf-deep"], COL["turf"])
    c = g.mix(g.math("MULTIPLY", g.ss(mid, 0.55, 0.75), 0.6), c, COL["turf-pale"])
    # the wind-burnt grass at the crest and the earth of the scarp under it
    c = g.mix(g.ss(nz, 0.75, 0.55), c, COL["hay"])
    c = g.mix(g.ss(nz, 0.45, 0.30), c, COL["earth"])
    g.put(bsdf.inputs["Base Color"], c)
    g.put(bsdf.inputs["Roughness"], 0.9)
    g.put(bsdf.inputs["Sheen Weight"], 0.35)
    g.put(bsdf.inputs["Sheen Tint"], (0.6, 0.75, 0.4))
    return m


def land_material():
    """The far shores: a pale beach at the water, turf and heath on the slopes, fields walled in stone on the gentle
    ground far off (Jæren's farms); the near ground plain turf."""
    m, g, bsdf = T.material("land")
    P, N, x, y, z, nz = T.geometry(g)
    vor = g.node("ShaderNodeTexVoronoi", {"Vector": P, "Scale": 1 / 55.0, "Randomness": 0.85})
    cell = g.out(g.node("ShaderNodeSeparateColor", {"Color": g.out(vor, "Color")}), "Red")
    field = g.mix(g.ss(cell, 0.15, 0.85), COL["turf-deep"], COL["turf-pale"])
    field = g.mix(g.ss(cell, 0.80, 0.92), field, COL["hay"])
    edge = g.node("ShaderNodeTexVoronoi", {"Vector": P, "Scale": 1 / 55.0, "Randomness": 0.85},
                  feature="DISTANCE_TO_EDGE")
    wall = g.ss(g.out(edge, "Distance"), 0.012, 0.004)
    field = g.mix(wall, field, COL["wall"])
    far = g.ss(g.out(g.node("ShaderNodeVectorMath", {"Vector": P}, operation="LENGTH"), "Value"), 300.0, 450.0)
    flat = g.ss(nz, 0.9, 0.97)
    rough = g.mix(g.ss(g.noise(P, 0.03, 1.0), 0.4, 0.6), COL["turf-deep"], COL["heath"])
    c = g.mix(g.math("MULTIPLY", far, flat), rough, field)
    c = g.mix(g.ss(z, 1.2, 0.5), c, COL["sand"])
    c = g.mix(g.ss(z, -0.1, -0.5), c, COL["sea-deep"])
    g.put(bsdf.inputs["Base Color"], c)
    g.put(bsdf.inputs["Roughness"], 0.9)
    return m


def grass_material():
    m, g, bsdf = T.material("grass")
    P, N, x, y, z, nz = T.geometry(g)
    c = g.mix(g.ss(g.noise(P, 0.4, 1.0), 0.3, 0.7), COL["grass"], COL["turf-pale"])
    g.put(bsdf.inputs["Base Color"], c)
    g.put(bsdf.inputs["Roughness"], 0.6)
    g.put(bsdf.inputs["Transmission Weight"], 0.0)
    g.put(bsdf.inputs["Subsurface Weight"], 0.25)
    g.put(bsdf.inputs["Subsurface Radius"], (0.2, 0.4, 0.1))
    return m


def sea_material():
    """The Roads: dark green water, whitecaps from the waves' own foam, white water where they meet the rock."""
    m = bpy.data.materials.new("roads")
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    g = T.G(nt)
    P, N, x, y, z, nz = T.geometry(g)
    water = g.node("ShaderNodeBsdfPrincipled", {"Base Color": COL["sea"], "Roughness": 0.07, "IOR": 1.33})
    foam = g.node("ShaderNodeBsdfPrincipled", {"Base Color": COL["foam"], "Roughness": 0.85})
    caps = g.out(g.node("ShaderNodeAttribute", attribute_name="foam"), "Fac")
    shore = g.out(g.node("ShaderNodeAttribute", attribute_name="shore"), "Fac")
    lace = g.noise(g.vec(g.math("MULTIPLY", x, 1.0), y, 0.0), 0.9, 3.0, 0.6)
    streak = g.noise(g.vec(x, y, 0.0), 0.35, 2.0, 0.55)
    surf = g.math("MULTIPLY", g.ss(shore, 1.8, 0.15), g.ss(lace, 0.38, 0.55))
    wash = g.math("MULTIPLY", g.math("MULTIPLY", g.ss(shore, 4.0, 1.2), g.ss(streak, 0.62, 0.72)), 0.5)
    f = g.math("MAXIMUM", g.math("MAXIMUM", surf, wash), g.math("MULTIPLY", g.ss(caps, 0.55, 0.9), 0.8))
    mix = g.node("ShaderNodeMixShader")
    g.put(mix.inputs[0], f)
    g.L.new(water.outputs[0], mix.inputs[1])
    g.L.new(foam.outputs[0], mix.inputs[2])
    o = g.node("ShaderNodeOutputMaterial")
    g.L.new(mix.outputs[0], o.inputs["Surface"])
    return m


def plain(name, col, rough=0.7):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    p = m.node_tree.nodes["Principled BSDF"]
    p.inputs["Base Color"].default_value = (*col, 1)
    p.inputs["Roughness"].default_value = rough
    return m


def blade_clump():
    """A clump of grass: a dozen tapered, bent blades, 12 to 35 cm."""
    import bmesh
    rng = HS.Stream("lt1-bluff", "grass-clump")
    bm = bmesh.new()
    for _ in range(12):
        a = rng.uniform(0, 2 * math.pi)
        r = rng.uniform(0.0, 0.05)
        h = rng.uniform(0.12, 0.35)
        lean = rng.uniform(0.15, 0.6)
        w = rng.uniform(0.006, 0.011)
        base = np.array([r * math.cos(a), r * math.sin(a), 0.0])
        d = np.array([math.cos(a), math.sin(a), 0.0])
        side = np.array([-d[1], d[0], 0.0])
        prev = None
        for k in range(4):
            t = k / 3
            p = base + d * lean * h * t * t + np.array([0, 0, h * t * (1 - 0.25 * lean * t)])
            ww = w * (1 - t) + 0.0005
            pair = [bm.verts.new(p - side * ww), bm.verts.new(p + side * ww)]
            if prev:
                bm.faces.new([prev[0], prev[1], pair[1], pair[0]])
            prev = pair
    me = bpy.data.meshes.new("clump")
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new("clump", me)
    bpy.context.scene.collection.objects.link(ob)
    ob.hide_render = True
    ob.hide_viewport = True
    me.materials.append(grass_material())
    return ob


def grass(turf_ob, rock, cam):
    """Grass on the turf: thick along the crest, where it stands against the sky, and near the eye; the rest of the turf
    is its colour alone."""
    me = turf_ob.data
    V = np.zeros(len(me.vertices) * 3)
    me.vertices.foreach_get("co", V)
    V = V.reshape(-1, 3)
    T = rock.turf_grid
    fringe = BL.smooth(4.0, 0.5, CF.bilinear(T["f"], T["xs"], T["ys"], V[:, 0], V[:, 1]))
    near = BL.smooth(70.0, 25.0, np.linalg.norm(V - np.asarray(cam), axis=1))
    a = me.attributes.new("gw", "FLOAT", "POINT")
    a.data.foreach_set("value", np.maximum(fringe, near).astype(np.float32))
    clump = blade_clump()
    ng = bpy.data.node_groups.new("grass", "GeometryNodeTree")
    ng.interface.new_socket("Geometry", in_out="INPUT", socket_type="NodeSocketGeometry")
    ng.interface.new_socket("Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry")
    N, L = ng.nodes, ng.links
    gi, go = N.new("NodeGroupInput"), N.new("NodeGroupOutput")
    attr = N.new("GeometryNodeInputNamedAttribute")
    attr.data_type = "FLOAT"
    attr.inputs["Name"].default_value = "gw"
    dens = N.new("ShaderNodeMath")
    dens.operation = "MULTIPLY"
    L.new(attr.outputs["Attribute"], dens.inputs[0])
    dens.inputs[1].default_value = 140.0
    dist = N.new("GeometryNodeDistributePointsOnFaces")
    dist.distribute_method = "RANDOM"
    L.new(gi.outputs[0], dist.inputs["Mesh"])
    L.new(dens.outputs[0], dist.inputs["Density"])
    info = N.new("GeometryNodeObjectInfo")
    info.inputs["Object"].default_value = clump
    info.inputs["As Instance"].default_value = True
    rot = N.new("FunctionNodeRandomValue")
    rot.data_type = "FLOAT_VECTOR"
    rot.inputs["Min"].default_value = (-0.12, -0.12, 0.0)
    rot.inputs["Max"].default_value = (0.12, 0.12, 6.283)
    sc = N.new("FunctionNodeRandomValue")
    sc.data_type = "FLOAT"
    lo, hi = [x for x in sc.inputs if x.type == "VALUE" and x.name in ("Min", "Max")]
    lo.default_value, hi.default_value = 0.6, 1.5
    inst = N.new("GeometryNodeInstanceOnPoints")
    L.new(dist.outputs["Points"], inst.inputs["Points"])
    L.new(info.outputs["Geometry"], inst.inputs["Instance"])
    L.new(rot.outputs[0], inst.inputs["Rotation"])
    L.new(next(x for x in sc.outputs if x.type == "VALUE"), inst.inputs["Scale"])
    join = N.new("GeometryNodeJoinGeometry")
    L.new(inst.outputs[0], join.inputs[0])
    L.new(gi.outputs[0], join.inputs[0])
    L.new(join.outputs[0], go.inputs[0])
    mod = turf_ob.modifiers.new("grass", "NODES")
    mod.node_group = ng


def roads(centre, rock_obs):
    """The Roads near the Bluff: an ocean surface, waves from the north-west, foam; its distance to the rock stored."""
    bpy.ops.mesh.primitive_plane_add(size=2, location=(centre[0], centre[1], BL.SEA["level"] + 0.05))
    ob = bpy.context.object
    ob.name = "roads"
    oc = ob.modifiers.new("ocean", "OCEAN")
    oc.geometry_mode = "GENERATE"
    oc.resolution = 14
    oc.spatial_size = 36
    oc.repeat_x = oc.repeat_y = 16
    oc.wave_scale = 0.45
    oc.choppiness = 1.1
    oc.wind_velocity = 9.0
    oc.wave_direction = math.radians(-35.0)
    oc.wave_alignment = 0.5
    oc.depth = 40.0
    oc.use_normals = True
    oc.use_foam = True
    oc.foam_coverage = 0.25
    oc.foam_layer_name = "foam"
    oc.random_seed = 7
    # the generated grid runs from the object's origin: centre it
    dg = bpy.context.evaluated_depsgraph_get()
    bb = np.array([v[:] for v in ob.evaluated_get(dg).bound_box])
    mid = (bb.min(0) + bb.max(0)) / 2
    ob.location.x -= mid[0]
    ob.location.y -= mid[1]
    ng = bpy.data.node_groups.new("shore", "GeometryNodeTree")
    ng.interface.new_socket("Geometry", in_out="INPUT", socket_type="NodeSocketGeometry")
    ng.interface.new_socket("Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry")
    N, L = ng.nodes, ng.links
    gi, go = N.new("NodeGroupInput"), N.new("NodeGroupOutput")
    join = N.new("GeometryNodeJoinGeometry")
    for r in rock_obs:
        info = N.new("GeometryNodeObjectInfo")
        info.inputs["Object"].default_value = r
        info.transform_space = "RELATIVE"
        L.new(info.outputs["Geometry"], join.inputs[0])
    prox = N.new("GeometryNodeProximity")
    L.new(join.outputs[0], prox.inputs[0])
    store = N.new("GeometryNodeStoreNamedAttribute")
    store.data_type = "FLOAT"
    store.domain = "POINT"
    store.inputs["Name"].default_value = "shore"
    L.new(gi.outputs[0], store.inputs["Geometry"])
    L.new(prox.outputs["Distance"], store.inputs["Value"])
    L.new(store.outputs[0], go.inputs[0])
    mod = ob.modifiers.new("shore", "NODES")
    mod.node_group = ng
    ob.data.materials.append(sea_material())
    for p in ob.data.polygons:
        p.use_smooth = True
    return ob


def haze():
    """The air: a thin, sunlit haze over the Roads, bluer and denser with distance."""
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 40))
    ob = bpy.context.object
    ob.name = "haze"
    ob.scale = (5000, 5000, 120)
    m = bpy.data.materials.new("haze")
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    v = nt.nodes.new("ShaderNodeVolumePrincipled")
    v.inputs["Color"].default_value = (0.78, 0.84, 0.93, 1)
    v.inputs["Density"].default_value = 0.00028
    v.inputs["Anisotropy"].default_value = 0.55
    o = nt.nodes.new("ShaderNodeOutputMaterial")
    nt.links.new(v.outputs[0], o.inputs["Volume"])
    ob.data.materials.append(m)
    return ob


def person(x, y, rock, k):
    obs = CF.figure(x, y, rock, f"fig{k}")
    obs[0].data.materials.append(plain(f"coat{k}", CLOTHES[k % len(CLOTHES)], 0.6))
    obs[1].data.materials.append(plain("skin", (0.42, 0.27, 0.19), 0.5))


def main():
    out = BL.arg("--out")
    os.makedirs(out, exist_ok=True)
    t = time.time()
    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o)
    rock, src, tu = CF.build(out, reuse=bool(BL.arg("--reuse")))
    gr = CF.far_ground(rock, CF.BOX)
    se = BL.sea()
    tu.data.materials.append(turf_material())
    gr.data.materials.append(land_material())
    se.location.z -= 0.1
    se.data.materials.append(T.water_material())
    # the camera first: the grass gathers near it
    views = {vw["name"]: vw for vw in BL.FIX["views"]}
    view = dict(views[BL.arg("--view", "shore")])
    if BL.arg("--pos"):
        view["pos"] = [float(v) for v in BL.arg("--pos").split(",")]
    if BL.arg("--target"):
        view["target"] = [float(v) for v in BL.arg("--target").split(",")]
    if BL.arg("--lens"):
        view["lens"] = float(BL.arg("--lens"))
    BL.camera(view, rock)
    cam = list(bpy.context.scene.camera.location)
    ro = CF.view_rock(rock, src, np.array(cam))
    ro.data.materials.clear()  # the source's empty slot would otherwise take every face
    ro.data.materials.append(rock_material(rock.fol))
    grass(tu, rock, cam)
    roads(((cam[0] + view["target"][0]) / 2, (cam[1] + view["target"][1]) / 2), [ro])
    haze()
    people = [tuple(p) for p in BL.FIX.get("figures", [])]
    for u in (64.0, 70.0, 121.0):  # walkers on the top, back from the edge
        b = BL.point_on_crest(u)
        fr = BL.crest_frame(np.array([b[0]]), np.array([b[1]]))
        n = np.array([fr[2][0], fr[3][0]])
        d = np.arange(-30.0, 30.0, 0.5)
        on = CF.in_turf(rock, b[0] + n[0] * d, b[1] + n[1] * d, margin=3.5)
        if on.any():
            people.append(tuple(b + n * d[on][np.abs(d[on]).argmin()]))
    for k, (x, y) in enumerate(people):
        person(x, y, rock, k)
    T.world()
    BL.sun(LIGHT)
    BL.cycles(int(BL.arg("--w", 1600)), int(BL.arg("--h", 900)), int(BL.arg("--samples", 64)))
    print(f"scene: {time.time() - t:.0f}s")
    name = BL.arg("--name", view["name"])
    bpy.context.scene.render.filepath = os.path.join(out, f"{name}-target.png")
    bpy.ops.render.render(write_still=True)
    print("wrote", bpy.context.scene.render.filepath, f"{time.time() - t:.0f}s")


if __name__ == "__main__":
    main()
