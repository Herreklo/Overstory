"""The rock tip's target frame: the block-in's scene from the street stop in Cycles, with what clay cannot carry drawn
by the rules the rock will use, in one designed light (October, 16:00, the low sun in the south-west).

The rules (docs/research/land-rock-and-water.md, Coast and the rock's history): height above the sea sets the bands
(the wet foot, black Verrucaria just above high water, orange and yellow lichens in the spray, grey lichens above);
the phyllite's foliation sets long bands of graphite-dark, grey-green and quartz-light along its strike; grass and
heath hold only in open joints and hollows above the spray. Each is a broad value shape, never noise. The made ground
of 1882 is dressed stone in courses, and the bands cross it as they cross the rock.

    Blender -b --factory-startup -P blender/parts/rock/target.py -- --out DIR [--view street] [--w 2560 --h 1440]
        [--samples 96] [--passes beauty,geo]

Writes <view>-target-raw.png (the render) and <view>-geo.png (16-bit: R distance/400 m, G height/20 + 0.5,
B object/16), which finish.py reads.
"""

import math
import os
import sys

import bpy
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import blockin as B  # noqa: E402

SUN = {"azimuth": 230, "elevation": 12, "color": (1.0, 0.70, 0.46), "energy": 4.2}
# linear albedos
COL = {
    "graphite": (0.085, 0.087, 0.082), "chlorite": (0.155, 0.165, 0.14), "quartz": (0.25, 0.245, 0.22),
    "lichen-grey": (0.36, 0.37, 0.34), "verrucaria": (0.022, 0.022, 0.020), "wrack": (0.07, 0.055, 0.018),
    "caloplaca": (0.40, 0.17, 0.04), "xanthoria": (0.46, 0.34, 0.08),
    "straw": (0.26, 0.19, 0.075), "heath": (0.075, 0.085, 0.035),
    "granite": (0.17, 0.165, 0.155), "mortar": (0.05, 0.05, 0.048), "gravel": (0.15, 0.135, 0.11),
    "falu": (0.21, 0.035, 0.022), "tar": (0.022, 0.022, 0.024), "trim": (0.62, 0.61, 0.57), "glass": (0.008, 0.01, 0.012),
    "rubble": (0.13, 0.125, 0.115), "quay": (0.12, 0.115, 0.105), "far": (0.10, 0.10, 0.095), "sea": (0.010, 0.028, 0.030),
}
INDEX = {"rock": 1, "water": 2, "landing": 3, "path-fill": 4, "pub-quay-end": 3, "land": 9, "breakwater": 8, "light": 8}


class G:
    """A small node writer: sockets in, sockets out."""

    def __init__(s, nt):
        s.nt, s.N, s.L = nt, nt.nodes, nt.links

    def put(s, sock, v):
        if isinstance(v, bpy.types.NodeSocket):
            s.L.new(v, sock)
        elif isinstance(v, (tuple, list)) and len(v) == 3 and sock.type == "RGBA":
            sock.default_value = (*v, 1.0)
        else:
            sock.default_value = v

    def node(s, kind, inputs=None, **props):
        n = s.N.new(kind)
        for k, v in props.items():
            setattr(n, k, v)
        for k, v in (inputs or {}).items():
            sock = next(x for x in n.inputs if x.identifier == k or x.name == k)
            s.put(sock, v)
        return n

    def out(s, n, ident):
        return next(x for x in n.outputs if x.identifier == ident or x.name == ident)

    def math(s, op, a, b=0.0):
        n = s.node("ShaderNodeMath", operation=op)
        s.put(n.inputs[0], a)
        s.put(n.inputs[1], b)
        return n.outputs[0]

    def ss(s, x, a, b):
        """Smoothstep from a to b (a > b runs it downward)."""
        lo, hi, flip = (a, b, False) if a < b else (b, a, True)
        n = s.node("ShaderNodeMapRange", {"Value": x, "From Min": lo, "From Max": hi}, interpolation_type="SMOOTHSTEP")
        r = n.outputs["Result"]
        return s.math("SUBTRACT", 1.0, r) if flip else r

    def mix(s, fac, a, b):
        n = s.node("ShaderNodeMix", {"Factor_Float": fac, "A_Color": a, "B_Color": b}, data_type="RGBA")
        return s.out(n, "Result_Color")

    def mixf(s, fac, a, b):
        n = s.node("ShaderNodeMix", {"Factor_Float": fac, "A_Float": a, "B_Float": b}, data_type="FLOAT")
        return s.out(n, "Result_Float")

    def noise(s, vec, scale, detail=1.0, rough=0.5, dims="3D", w=None):
        n = s.node("ShaderNodeTexNoise", {"Scale": scale, "Detail": detail, "Roughness": rough}, noise_dimensions=dims)
        if vec is not None:
            s.put(n.inputs["Vector"], vec)
        if w is not None:
            s.put(n.inputs["W"], w)
        return n.outputs["Fac"]

    def vec(s, x, y, z):
        return s.out(s.node("ShaderNodeCombineXYZ", {"X": x, "Y": y, "Z": z}), "Vector")

    def scale(s, v, k):
        n = s.node("ShaderNodeVectorMath", operation="SCALE")
        s.put(n.inputs[0], v)
        n.inputs["Scale"].default_value = k
        return n.outputs[0]


def material(name):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    g = G(nt)
    bsdf = g.node("ShaderNodeBsdfPrincipled")
    o = g.node("ShaderNodeOutputMaterial")
    g.L.new(bsdf.outputs[0], o.inputs["Surface"])
    return m, g, bsdf


def geometry(g):
    geo = g.node("ShaderNodeNewGeometry")
    P, N = g.out(geo, "Position"), g.out(geo, "Normal")
    sp = g.node("ShaderNodeSeparateXYZ", {"Vector": P})
    sn = g.node("ShaderNodeSeparateXYZ", {"Vector": N})
    return P, N, g.out(sp, "X"), g.out(sp, "Y"), g.out(sp, "Z"), g.out(sn, "Z")


def sea_bands(g, base, P, z, nz, exposure=1.0):
    """The shore's bands over a surface's own colour: the wet foot, black Verrucaria to a little over high water, then
    orange Caloplaca and yellow Xanthoria in patches in the spray, grey lichens above on the tops. The bands' edges
    wander slowly (a few metres), as spray and shelter vary; their widths grow with exposure."""
    wander = g.math("MULTIPLY", g.math("SUBTRACT", g.noise(P, 0.11, 0.0), 0.5), 0.7)
    zw = g.math("ADD", z, wander)
    black_top = 0.9 + 0.5 * exposure
    black = g.math("MULTIPLY", g.ss(zw, -0.15, 0.12), g.ss(zw, black_top + 0.15, black_top - 0.15))
    spray_top = black_top + 1.6 * exposure
    spray = g.math("MULTIPLY", g.ss(zw, black_top - 0.1, black_top + 0.2), g.ss(zw, spray_top + 0.4, spray_top - 0.4))
    up = g.ss(nz, 0.25, 0.7)
    patch = g.ss(g.noise(P, 0.8, 1.0), 0.60, 0.64)
    orange = g.math("MULTIPLY", g.math("MULTIPLY", spray, patch), up)
    yellow_of = g.ss(zw, black_top + 0.5, black_top + 1.2)
    lichen_col = g.mix(yellow_of, COL["caloplaca"], COL["xanthoria"])
    above = g.ss(zw, spray_top - 0.3, spray_top + 0.6)
    grey_patch = g.ss(g.noise(P, 0.32, 1.5, 0.55), 0.40, 0.55)
    grey = g.math("MULTIPLY", g.math("MULTIPLY", above, grey_patch), g.ss(nz, 0.1, 0.6))
    c = g.mix(g.math("MULTIPLY", grey, 0.8), base, COL["lichen-grey"])
    c = g.mix(g.math("MULTIPLY", orange, 0.85), c, lichen_col)
    c = g.mix(black, c, COL["verrucaria"])
    wrack = g.math("MULTIPLY", g.ss(z, -0.35, -0.12), g.ss(z, 0.22, 0.05))
    c = g.mix(g.math("MULTIPLY", wrack, 0.9), c, COL["wrack"])
    wet = g.ss(zw, 0.45, 0.05)
    dark = g.mixf(wet, 1.0, 0.55)
    grey3 = g.out(g.node("ShaderNodeCombineColor", {"Red": dark, "Green": dark, "Blue": dark}), "Color")
    cm = g.node("ShaderNodeMix", {"Factor_Float": 1.0, "A_Color": c, "B_Color": grey3}, data_type="RGBA",
                blend_type="MULTIPLY")
    return g.out(cm, "Result_Color"), wet


def rock_material():
    m, g, bsdf = material("rock")
    P, N, x, y, z, nz = geometry(g)
    # the foliation: dips 68 toward 250, so its strike runs 160/340; bands of metres across it
    s = g.math("ADD", g.math("MULTIPLY", x, -0.940), g.math("MULTIPLY", y, -0.342))
    band = g.noise(None, 1.0, 2.0, 0.45, dims="1D", w=g.math("MULTIPLY", s, 0.16))
    fine = g.noise(None, 1.0, 0.0, 0.5, dims="1D", w=g.math("MULTIPLY", s, 1.3))
    b = g.math("ADD", g.math("MULTIPLY", band, 0.8), g.math("MULTIPLY", fine, 0.2))
    base = g.mix(g.ss(b, 0.38, 0.50), COL["graphite"], COL["chlorite"])
    base = g.mix(g.ss(b, 0.56, 0.66), base, COL["quartz"])
    # grass and heath only in open joints and hollows above the spray
    ao = g.node("ShaderNodeAmbientOcclusion", {"Distance": 0.9}, samples=8)
    hollow = g.ss(g.out(ao, "AO"), 0.62, 0.40)
    dry = g.ss(z, 3.0, 3.8)
    grass = g.math("MULTIPLY", g.math("MULTIPLY", hollow, dry), g.ss(nz, 0.45, 0.8))
    c, wet = sea_bands(g, base, P, z, nz, exposure=1.0)
    turf = g.mix(g.ss(g.noise(P, 0.9, 1.0), 0.45, 0.6), COL["straw"], COL["heath"])
    c = g.mix(grass, c, turf)
    g.put(bsdf.inputs["Base Color"], c)
    g.put(bsdf.inputs["Roughness"], g.mixf(wet, 0.72, 0.16))
    return m


def stone_material(name, row, length):
    """Dressed stone in courses: rows of `row` m, stones about `length` m long; a top of slabs."""
    m, g, bsdf = material(name)
    P, N, x, y, z, nz = geometry(g)
    wall_uv = g.vec(g.math("ADD", x, y), z, 0.0)
    top_uv = g.vec(x, y, 0.0)
    flat = g.ss(nz, 0.5, 0.8)
    uv = g.node("ShaderNodeMix", {"Factor_Float": flat, "A_Vector": wall_uv, "B_Vector": top_uv}, data_type="VECTOR")
    br = g.node("ShaderNodeTexBrick", {"Vector": g.out(uv, "Result_Vector"), "Color1": COL["granite"],
                                       "Color2": tuple(v * 0.8 for v in COL["granite"]), "Mortar": COL["mortar"],
                                       "Scale": 1.0, "Mortar Size": 0.018, "Mortar Smooth": 0.3, "Bias": 0.0,
                                       "Brick Width": length, "Row Height": row}, offset=0.45, squash=1.0)
    base = g.out(br, "Color")
    c, wet = sea_bands(g, base, P, z, nz, exposure=0.7)
    g.put(bsdf.inputs["Base Color"], c)
    g.put(bsdf.inputs["Roughness"], g.mixf(wet, 0.8, 0.2))
    bump = g.node("ShaderNodeBump", {"Strength": 0.35, "Distance": 0.02, "Height": g.out(br, "Fac")})
    g.put(bsdf.inputs["Normal"], g.out(bump, "Normal"))
    return m


def plain(name, col, rough=0.8):
    m, g, bsdf = material(name)
    g.put(bsdf.inputs["Base Color"], col)
    g.put(bsdf.inputs["Roughness"], rough)
    return m


def timber_material():
    """Falu red board and batten: battens every 0.3 m, a little lighter where the sun has chalked the paint."""
    m, g, bsdf = material("timber-red")
    P, N, x, y, z, nz = geometry(g)
    u = g.math("ADD", g.math("MULTIPLY", x, 0.95), g.math("MULTIPLY", y, 0.31))
    v = g.math("ADD", g.math("MULTIPLY", x, -0.31), g.math("MULTIPLY", y, 0.95))
    along = g.math("ADD", u, v)
    wave = g.node("ShaderNodeTexWave", {"Vector": g.vec(along, 0.0, 0.0), "Scale": 2 * math.pi / (20 * 0.30),
                                         "Distortion": 0.0, "Detail": 0.0}, wave_type="BANDS", bands_direction="X",
                  wave_profile="SAW")
    batten = g.ss(g.out(wave, "Fac"), 0.86, 0.92)
    chalk = g.ss(z, 8.0, 11.0)
    c = g.mix(g.math("MULTIPLY", chalk, 0.35), COL["falu"], (0.30, 0.09, 0.06))
    g.put(bsdf.inputs["Base Color"], c)
    g.put(bsdf.inputs["Roughness"], 0.85)
    bump = g.node("ShaderNodeBump", {"Strength": 0.6, "Distance": 0.02, "Height": batten})
    g.put(bsdf.inputs["Normal"], g.out(bump, "Normal"))
    return m


def water_material():
    m, g, bsdf = material("water")
    P, N, x, y, z, nz = geometry(g)
    st = g.vec(g.math("MULTIPLY", x, 0.35), y, 0.0)
    h = g.math("ADD", g.noise(st, 1.6, 2.0, 0.5), g.math("MULTIPLY", g.noise(st, 0.12, 0.0), 2.0))
    bump = g.node("ShaderNodeBump", {"Strength": 0.4, "Distance": 0.05, "Height": h})
    g.put(bsdf.inputs["Base Color"], COL["sea"])
    g.put(bsdf.inputs["Roughness"], 0.10)
    g.put(bsdf.inputs["Normal"], g.out(bump, "Normal"))
    return m


def world():
    """The designed sky: a cool zenith, a pale horizon warming toward the sun in the south-west."""
    w = bpy.data.worlds.new("target-sky")
    bpy.context.scene.world = w
    w.use_nodes = True
    nt = w.node_tree
    nt.nodes.clear()
    g = G(nt)
    tc = g.node("ShaderNodeTexCoord")
    d = g.node("ShaderNodeVectorMath", operation="NORMALIZE")
    g.put(d.inputs[0], g.out(tc, "Generated"))
    dv = d.outputs[0]
    az, el = math.radians(SUN["azimuth"]), math.radians(SUN["elevation"])
    sdir = (math.sin(az) * math.cos(el), math.cos(az) * math.cos(el), math.sin(el))
    dot = g.node("ShaderNodeVectorMath", operation="DOT_PRODUCT")
    g.put(dot.inputs[0], dv)
    dot.inputs[1].default_value = sdir
    sz = g.out(g.node("ShaderNodeSeparateXYZ", {"Vector": dv}), "Z")
    up = g.ss(sz, 0.0, 0.55)
    hor = g.mix(g.ss(g.out(dot, "Value"), -0.3, 0.9), (0.30, 0.36, 0.42), (0.95, 0.70, 0.45))
    c = g.mix(up, hor, (0.11, 0.19, 0.33))
    glow = g.math("POWER", g.math("MAXIMUM", g.out(dot, "Value"), 0.0), 24.0)
    c = g.mix(g.math("MULTIPLY", glow, 0.6), c, (1.6, 1.1, 0.6))
    bg = g.node("ShaderNodeBackground", {"Color": c, "Strength": 1.5})
    o = g.node("ShaderNodeOutputWorld")
    g.L.new(bg.outputs[0], o.inputs["Surface"])


def windows():
    """The customs house's windows and door, white corner boards: what tells a house's size at the street stop."""
    trim, glass = plain("trim", COL["trim"], 0.6), plain("glass", COL["glass"], 0.08)
    b = next(b for b in B.FIX["buildings"] if b["id"] == "customs-house")
    r = math.radians(b["turn"])
    ex, ey = np.array([math.cos(r), math.sin(r)]), np.array([-math.sin(r), math.cos(r)])
    c = np.array(b["at"], float)
    hx, hy, z0 = b["size"][0] / 2, b["size"][1] / 2, b["base"]

    def panel(name, centre, out, along, w, z_lo, z_hi, depth, mat):
        o, a = np.array(out), np.array(along)
        p = centre + o * depth / 2
        ang = math.degrees(math.atan2(a[1], a[0]))
        B.box(name, p.tolist(), ang, [w, depth], z_lo, z_hi, mat)

    for i, lx in enumerate((-2.9, -1.0, 1.0, 2.9)):
        at = c + ex * lx - ey * hy
        panel(f"win-s{i}-frame", at, -ey, ex, 0.95, z0 + 0.95, z0 + 2.35, 0.10, trim)
        panel(f"win-s{i}", at - ey * 0.02, -ey, ex, 0.75, z0 + 1.05, z0 + 2.25, 0.10, glass)
    at = c + ex * hx
    panel("door-frame", at, ex, ey, 1.25, z0, z0 + 2.3, 0.10, trim)
    panel("door", at + ex * 0.02, ex, ey, 1.0, z0, z0 + 2.15, 0.10, plain("door", (0.035, 0.05, 0.045), 0.6))
    for i, ly in enumerate((-2.0, 2.0)):
        a2 = c + ex * hx + ey * ly
        panel(f"win-e{i}-frame", a2, ex, ey, 0.85, z0 + 1.0, z0 + 2.3, 0.10, trim)
        panel(f"win-e{i}", a2 + ex * 0.02, ex, ey, 0.65, z0 + 1.1, z0 + 2.2, 0.10, glass)
    panel("win-attic-frame", at, ex, ey, 0.75, z0 + 4.9, z0 + 5.9, 0.10, trim)
    panel("win-attic", at + ex * 0.02, ex, ey, 0.55, z0 + 5.0, z0 + 5.8, 0.10, glass)
    for sx in (-1, 1):
        for sy in (-1, 1):
            p = c + ex * hx * sx + ey * hy * sy
            B.box(f"corner{sx}{sy}", p.tolist(), b["turn"], [0.30, 0.30], z0 - 0.05, z0 + b["eaves"], trim)


def assign():
    mats = {
        "rock": rock_material(),
        "landing": stone_material("dressed", 0.45, 1.2),
        "path-fill": plain("gravel", COL["gravel"], 0.9),
        "pub-quay-end": None,
        "water": water_material(),
        "land": plain("quay", COL["quay"], 0.85),
        "plinth": stone_material("plinth-stone", 0.35, 0.7),
        "timber-red": timber_material(),
        "roof": plain("tar", COL["tar"], 0.55),
        "town": plain("town", (0.35, 0.34, 0.32)),
        "breakwater": plain("breakwater-stone", COL["granite"], 0.8),
        "light": plain("light-white", COL["trim"], 0.6),
        "far": plain("far-rock", COL["far"], 0.9),
    }
    mats["pub-quay-end"] = mats["landing"]
    for ob in bpy.data.objects:
        if ob.type != "MESH":
            continue
        n = ob.name
        ob.pass_index = INDEX.get(n, 5 if n.startswith(("customs", "harbour", "win", "door", "corner")) else
                                  6 if n.endswith("plinth") else 7)
        for i, slot in enumerate(ob.material_slots):
            if slot.material is None:
                continue
            key = slot.material.name.split(".")[0]
            if n in mats:
                slot.material = mats[n]
            elif key in mats and mats[key] is not None:
                slot.material = mats[key]


def cycles(w, h, samples):
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    try:
        prefs = bpy.context.preferences.addons["cycles"].preferences
        prefs.compute_device_type = "METAL"
        prefs.get_devices()
        for d in prefs.devices:
            d.use = True
        sc.cycles.device = "GPU"
    except Exception as e:  # CPU is fine, only slower
        print(f"[target] GPU unavailable ({e}); CPU")
    sc.cycles.samples = samples
    sc.cycles.use_denoising = True
    sc.render.resolution_x, sc.render.resolution_y = w, h
    sc.render.resolution_percentage = 100
    sc.view_settings.view_transform = "AgX"
    sc.view_settings.look = "AgX - Base Contrast"
    sc.view_settings.exposure = 0.0
    sc.render.image_settings.file_format = "PNG"
    sc.render.image_settings.color_depth = "8"


def geo_pass(out, name):
    """Distance, height and object for the finish: one emission override, a few samples."""
    sc = bpy.context.scene
    m, g, _ = material("geo-pass")
    nt = m.node_tree
    for n in list(nt.nodes):
        if n.type == "BSDF_PRINCIPLED":
            nt.nodes.remove(n)
    cam = g.node("ShaderNodeCameraData")
    P, N, x, y, z, nz = geometry(g)
    oi = g.node("ShaderNodeObjectInfo")
    col = g.node("ShaderNodeCombineColor", {"Red": g.math("DIVIDE", g.out(cam, "View Distance"), 400.0),
                                             "Green": g.math("ADD", g.math("DIVIDE", z, 20.0), 0.5),
                                             "Blue": g.math("DIVIDE", g.out(oi, "Object Index"), 16.0)})
    em = g.node("ShaderNodeEmission", {"Color": g.out(col, "Color"), "Strength": 1.0})
    o = next(n for n in nt.nodes if n.type == "OUTPUT_MATERIAL")
    g.L.new(em.outputs[0], o.inputs["Surface"])
    vl = sc.view_layers[0]
    vl.material_override = m
    w0 = sc.world
    black = bpy.data.worlds.new("black")
    black.use_nodes = True
    black.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.0
    sc.world = black
    sc.cycles.samples, sc.cycles.use_denoising = 1, False
    sc.render.filter_size = 0.01
    sc.view_settings.view_transform, sc.view_settings.look = "Raw", "None"
    sc.render.image_settings.color_depth = "16"
    sc.render.filepath = os.path.join(out, f"{name}-geo.png")
    bpy.ops.render.render(write_still=True)
    print(f"[target] {sc.render.filepath}")
    vl.material_override = None
    sc.world = w0


def blur(Z, passes=2):
    """A light 3-tap smoothing, so every edge the joints leave is worn round by a hand's width."""
    for _ in range(passes):
        Z = Z.copy()
        Z[1:-1, :] = (Z[:-2, :] + 2 * Z[1:-1, :] + Z[2:, :]) / 4
        Z[:, 1:-1] = (Z[:, :-2] + 2 * Z[:, 1:-1] + Z[:, 2:]) / 4
    return Z


def sculpt(step=0.12):
    """The rock as the target wants it, from the generator's own rules as a fine height field: each block between
    the joints one deliberate plane, tangent to the ice's envelope at its middle, so the back reads as broad planes
    whose edges are its joints; tight joints a worn line, open ones a groove with a broad round-over; the lee plucked
    in whole plates, the stoss's stripped sheets as ledges, the sea's blocks taken at the waterline (the shore runs
    along joints), the 1882 cut to its floor."""
    import outcrop as O
    import hashing as HS
    rec = B.FIX["outcrop"]
    lf = rec["landform"]
    land = O.Landform(lf)
    x0, y0, x1, y1 = rec["region"]
    X, Y = np.meshgrid(np.arange(x0, x1 + 1e-6, step), np.arange(y0, y1 + 1e-6, step))
    Zs = land.smooth(X, Y)
    bed = rec["bed"]
    corners = np.array([[x, y, z] for x in (x0, x1) for y in (y0, y1) for z in (bed, land.top + 2)])

    def lo_hi(n):
        s = corners @ n
        return s.min(), s.max()

    Q = np.stack([X, Y, Zs], -1)
    cell = np.zeros(X.shape, np.int64)
    lower = np.zeros(X.shape)
    for fam in rec["families"]:
        n, offs, gaps = O.family_planes("holm-tip", fam, lo_hi)
        s = Q @ n
        i = np.clip(np.searchsorted(offs, s), 1, len(offs) - 1)
        dl, dr = s - offs[i - 1], offs[i] - s
        near = np.where(dl < dr, i - 1, i)
        d = np.maximum(np.minimum(dl, dr), 0) / max(math.hypot(n[0], n[1]), 0.3)
        g = gaps[near]
        open_ = g > 0.05
        r = np.where(open_, 0.35 + 2.5 * g, 0.10)
        h = np.where(open_, 0.5 * r, 0.03)
        lip = np.where(d < r, (1 - d / r) ** 2, 0.0) * h
        groove = np.where(open_ & (d < g / 2 + step / 2), 0.3 + 3.0 * g, 0.0)
        lower = np.maximum(lower, np.maximum(lip, groove))
        cell = cell * 4096 + i
    uniq, inv = np.unique(cell.ravel(), return_inverse=True)
    cnt = np.bincount(inv)
    cx, cy = np.bincount(inv, X.ravel()) / cnt, np.bincount(inv, Y.ravel()) / cnt
    z0 = land.smooth(cx, cy)
    hh = 0.25
    gx = (land.smooth(cx + hh, cy) - land.smooth(cx - hh, cy)) / (2 * hh)
    gy = (land.smooth(cx, cy + hh) - land.smooth(cx, cy - hh)) / (2 * hh)
    ice = land.ice
    drop, k, gone = np.zeros(len(uniq)), np.zeros(len(uniq)), np.zeros(len(uniq), bool)
    sh, coast = rec["sheets"], rec["coast"]
    for j in range(len(uniq)):
        c = (cx[j], cy[j])
        rng = HS.Stream("holm-tip", "block", f"{c[0]:.2f}", f"{c[1]:.2f}")
        if z0[j] < coast["belowM"] and rng.uniform(0, 1) < coast["share"] * O.exposure(B.FIX["sea"], land, c):
            gone[j] = True
            continue
        dp = land.plucked(c[0], c[1], rng.uniform(-0.45, 0.45))
        dp = min(dp, max(0.0, z0[j] - land.lee["floor"])) if dp > 0 else 0.0
        if dp == 0:
            dp = int(np.floor(O.sheet_field("holm-tip", c[0], c[1], sh["cellM"]) * sh["most"]
                              + rng.uniform(0, 0.6))) * sh["thickM"]
        drop[j] = dp
        k[j] = rng.uniform(*lf["saw"])
    I = inv.reshape(X.shape)
    sv = (X - cx[I]) * ice[0] + (Y - cy[I]) * ice[1]
    Z = z0[I] + gx[I] * (X - cx[I]) + gy[I] * (Y - cy[I]) - drop[I] + np.minimum(k[I] * sv, lf["sawMaxM"])
    Z = np.where(gone[I], np.minimum(Z - 1.5, -1.0), Z)
    Z = Z - lower
    for cut in rec.get("cuts", []):
        d, t = B.seg_dist(X, Y, cut["line"])
        fl = np.interp(t, np.linspace(0, 1, len(cut["floor"])), cut["floor"])
        Z = np.where(d < cut["width"] / 2, np.minimum(Z, fl), Z)
    Z = blur(np.maximum(Z, bed))
    keep = Zs > rec["dropBelow"] - 3
    verts = np.stack([X.ravel(), Y.ravel(), Z.ravel()], 1)
    ny, nx = X.shape
    idx = np.arange(nx * ny).reshape(ny, nx)
    q = keep[:-1, :-1] | keep[1:, 1:]
    a, b_, c_, d_ = idx[:-1, :-1][q], idx[:-1, 1:][q], idx[1:, 1:][q], idx[1:, :-1][q]
    me = bpy.data.meshes.new("rock")
    me.from_pydata(verts.tolist(), [], np.stack([a, b_, c_, d_], 1).tolist())
    me.polygons.foreach_set("use_smooth", np.ones(len(me.polygons), bool))
    me.materials.append(bpy.data.materials["rock"])
    ob = bpy.data.objects.new("rock", me)
    bpy.context.scene.collection.objects.link(ob)
    print(f"[target] rock sculpt: {len(uniq)} blocks, {int(gone.sum())} taken by the sea, {len(me.polygons)} quads")
    return ob


def main():
    out = B.arg("--out", os.path.join(B.ROOT, "cache", "rock", "target"))
    os.makedirs(out, exist_ok=True)
    name = B.arg("--view", "street")
    passes = B.arg("--passes", "beauty,geo").split(",")
    B.build()
    old = bpy.data.objects["rock"]
    bpy.data.objects.remove(old)
    sys.path.insert(0, os.path.join(B.ROOT, "blender", "resolver"))
    sculpt(float(B.arg("--step", 0.12)))
    windows()
    assign()
    sun = bpy.data.lights.new("sun", "SUN")
    sun.energy, sun.color, sun.angle = SUN["energy"], SUN["color"], math.radians(0.8)
    so = bpy.data.objects.new("sun", sun)
    bpy.context.scene.collection.objects.link(so)
    B.aim(so, SUN["azimuth"], SUN["elevation"])
    world()
    v = next(v for v in B.VIEWS["views"] if v["name"] == name)
    bpy.context.scene.camera = B.camera(v)
    cycles(int(B.arg("--w", 2560)), int(B.arg("--h", 1440)), int(B.arg("--samples", 96)))
    if "beauty" in passes:
        bpy.context.scene.render.filepath = os.path.join(out, f"{name}-target-raw.png")
        bpy.ops.render.render(write_still=True)
        print(f"[target] {bpy.context.scene.render.filepath}")
    if "geo" in passes:
        geo_pass(out, name)


if __name__ == "__main__":
    main()
