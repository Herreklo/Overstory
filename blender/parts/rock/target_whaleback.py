"""The Bluff's target frame (look-in 2): the rock as the ice left it and the sea keeps it, in its landscape, painted.

A coarse block-out, no generator. Ice-rounded masses (whalebacks: long smooth backs up-ice, shorter stepped ends
down-ice, turfed) end at the Roads in one sheer face the ice and the sea plucked along the steep joint, stepped where
blocks came out between the cross joints, every edge still rounded. The foliation dips steeply across it as fine
ribs, and a tall cave slot is cut along it at the foot. Before it an ice-polished shelf (svaberg), rounded skerries, a
cove of pale shingle, erratics; behind it Jæren's green. On the rock the shore's zones: barnacles, black Verrucaria,
orange Xanthoria where the birds sit, grey lichen above; rust run from the joints, the mica's sheen on the foliation.
Then the painter's finish: air by distance, strokes (Kuwahara) finer near than far.

Site frame of its own: x along the face (world bearing 45), y inland (world 135), z over mean sea level; the face
looks north-west over the Roads. Bearings in this frame are compass-style (0 = +y, 90 = +x), so the pack's low sun
(world 254, 8 up) stands at 241: from the left of the face, raking it.

    Blender -b --factory-startup -P blender/parts/rock/target_whaleback.py -- --out DIR [--grey 1] [--rebuild 1]
        [--cam x,y,lookx,looky,lookz,lens] [--samples 96]
"""

import math
import os
import sys
import time

import bpy
import mathutils
import numpy as np
import openvdb as vdb

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bluff as BL  # noqa: E402
import target as T  # noqa: E402

H = 0.25  # voxel (m)
LO, HI = np.array([-112.0, -40.0, -5.0]), np.array([62.0, 62.0, 27.0])
T.SUN = {"azimuth": 241.0, "elevation": 7.0, "color": (1.0, 0.60, 0.34), "energy": 7.5}
CAM = (44.0, -36.0, -24.0, 8.0, 10.0, 20.0)  # on a knoll of the shelf, looking along the face into the sun


def frame_dir(bearing):
    """A world bearing as a horizontal unit vector in this frame."""
    a = math.radians(bearing - 45.0)
    return np.array([math.cos(a), math.sin(a)])


def plane_normal(dip, toward):
    h = frame_dir(toward) * math.sin(math.radians(dip))
    return np.array([h[0], h[1], math.cos(math.radians(dip))])


NFOL = plane_normal(68.0, 250.0)  # the phyllite's foliation (the research note: steep, dipping west-south-west)


# -- small noise, smooth maxima ---------------------------------------------------------------------------------------

def vnoise2(a, b, seed):
    """Smooth value noise over two coordinates (lattice 1), in [-1, 1]."""
    g = np.random.default_rng(seed).uniform(-1, 1, (257, 257)).astype(np.float32)
    a, b = np.asarray(a, np.float32), np.asarray(b, np.float32)
    ia, ib = np.floor(a).astype(np.int64), np.floor(b).astype(np.int64)
    fa, fb = a - ia, b - ib
    fa, fb = fa * fa * (3 - 2 * fa), fb * fb * (3 - 2 * fb)
    ia, ib = ia % 256, ib % 256
    v00, v10, v01, v11 = g[ia, ib], g[ia + 1, ib], g[ia, ib + 1], g[ia + 1, ib + 1]
    return (v00 * (1 - fa) + v10 * fa) * (1 - fb) + (v01 * (1 - fa) + v11 * fa) * fb


def fbm2(a, b, seed, oct=3):
    return sum(vnoise2(a * 2 ** k, b * 2 ** k, seed + k) * 0.5 ** k for k in range(oct)) / 1.75


def saw(u, at):
    """Ribs: a slow ramp, then a steep fall along the foliation plane."""
    f = u - np.floor(u)
    return f * (1 - ss(at, 1.0, f))


def smax(a, b, k):
    h = np.maximum(k - np.abs(a - b), 0) / k
    return np.maximum(a, b) + h * h * k / 4


def smin(a, b, k):
    return -smax(-a, -b, k)


def ss(a, b, x):
    t = np.clip((x - a) / (b - a), 0, 1)
    return t * t * (3 - 2 * t)


# -- the land ---------------------------------------------------------------------------------------------------------

MASSES = [  # x, y, height, up-ice slope, down-ice slope, seed: the ice ran from +x to -x
    (8.0, 13.0, 29.0, 0.30, 1.05, 1),
    (-50.0, 12.0, 24.0, 0.34, 0.95, 2),
    (-98.0, 10.0, 19.0, 0.36, 0.9, 3),
    (50.0, 17.0, 21.0, 0.30, 1.0, 4),
    (-22.0, 62.0, 26.0, 0.28, 0.8, 5),
]
FACE = ([-140, -112, -96, -86, -80, -74, -68, -62, -40, -22, -6, 4, 16, 30, 42, 70],  # the face's foot, y by x:
        [-4.0, -4.0, -4.0, -3.0, 2.0, 9.0, 4.0, -2.5, -2.0, -1.0, 0.5, 0.0, -1.0, 1.0, 4.0, 6.0])  # the cove at -74
POCKET = (26.0, -14.0, 6.0)  # a hollow in the shelf, open to the sea, where the shingle lies
SHELF = dict(x=(-6.0, 56.0), knoll=(44.0, -36.0, 3.6))


def hull(x, y, cx, cy, hm, stoss, lee, seed, k):
    """An ice-worn mass as a few big planes, their meeting edges rounded over k: a top, a gentle stoss toward +x,
    steeper flanks, a steep lee toward -x."""
    rng = np.random.default_rng(seed)
    roof = (hm + 0.03 * (x - cx) + 0 * y).astype(np.float32)
    for az, sl in ((0, stoss), (35, stoss * 1.3), (-35, stoss * 1.3), (75, 0.6 * lee), (-75, 0.6 * lee),
                   (115, 0.85 * lee), (-115, 0.85 * lee), (155, lee), (-155, lee), (180, lee * 1.1)):
        a = math.radians(az + rng.uniform(-12, 12))
        s = sl * rng.uniform(0.8, 1.25)
        c = rng.uniform(1.5, 4.5) if abs(az) < 60 else rng.uniform(0.5, 2.5)
        z = hm + c - s * ((x - cx) * math.cos(a) + (y - cy) * math.sin(a))
        roof = smin(roof, z.astype(np.float32), k)
    return roof


def tops(x, y):
    """The masses' backs: ice-worn domes of a few big planes, stepped where the ice plucked their down-ice ends;
    behind them Jæren's rolling ground."""
    h = 13.0 * ss(10.0, 60.0, y) + 2.5 * fbm2(x / 45.0, y / 45.0, 7) - 1.0
    for cx, cy, hm, stoss, lee, seed in MASSES:
        dome = hull(x, y, cx, cy, hm, stoss, lee, seed, 3.0)
        terr = ss(-4.0, -14.0, x - cx) * ss(0.0, 3.0, dome)  # down-ice: steps, the blocks the ice pulled away
        dome = dome - terr * 0.85 * (2.8 / (2 * np.pi)) * np.sin(2 * np.pi * dome / 2.8)
        dome = dome + 0.5 * fbm2(x / 9.0, y / 9.0, 11)
        h = smax(h, dome, 3.0)
    return h.astype(np.float32)


def face_line(x):
    return np.interp(x, *FACE).astype(np.float32)


def plucks(x, z):
    """How far the face stands back (m) over x and height: a few big planes, each where a block came out or stayed,
    in cells drawn out along the foliation's steep trace (so no lattice, no boxes), their meeting edges worn round."""
    rng = np.random.default_rng(1989)
    nn = np.array([NFOL[0], NFOL[2]]) / math.hypot(NFOL[0], NFOL[2])  # across the foliation, on the face
    tr = np.array([nn[1], -nn[0]])  # along its trace
    n = 90
    cx, cz = rng.uniform(x[0], x[-1], n), rng.uniform(z[0], z[-1] + 4.0, n)
    base = rng.uniform(-0.8, 3.6, n)
    sx, sz = rng.uniform(-0.35, 0.35, n), rng.uniform(-0.08, 0.35, n)
    X, Zg = np.meshgrid(x, z, indexing="ij")
    best, cell = np.full(X.shape, np.inf, np.float32), np.zeros(X.shape, np.int64)
    for j in range(n):
        dx, dz = X - cx[j], Zg - cz[j]
        d = ((dx * tr[0] + dz * tr[1]) / 2.4) ** 2 + (dx * nn[0] + dz * nn[1]) ** 2
        take = d < best
        best, cell = np.where(take, d, best), np.where(take, j, cell)
    back = base[cell] + sx[cell] * (X - cx[cell]) + sz[cell] * (Zg - cz[cell])
    back = np.clip(back, -1.0, 4.5)
    back = box(box(back, 2), 1)  # the edges worn round over half a metre
    return back.astype(np.float32)


def land_sdf(xs, ys, zs):
    """Rock and turf < 0 on the grid (x, y, z)."""
    X, Y, Z = xs[:, None, None], ys[None, :, None], zs[None, None, :]
    x2, y2 = xs[:, None], ys[None, :]
    top = tops(x2, y2)
    bare = ss(0.22, 0.4, fbm2(x2 / 7.0, y2 / 7.0, 51))  # the windswept knolls, where the rock stands through the turf
    dome = (Z - (top + 0.65 * bare)[:, :, None]) * 0.8
    yf = face_line(xs)[:, None] + 0.1 * zs[None, :] + plucks(xs, zs)  # battered back 6 degrees, plucked
    yf += 0.4 * fbm2(xs[:, None] / 6.0, zs[None, :] / 5.0, 21)
    q = NFOL[0] * X + NFOL[1] * Y + NFOL[2] * Z  # across the foliation
    wob = 0.6 * fbm2(xs[:, None] / 5.0, zs[None, :] / 5.0, 23)[:, None, :]
    amp = (0.7 + 0.3 * fbm2(xs[:, None] / 9.0, zs[None, :] / 7.0, 25))[:, None, :]
    ribs = amp * (0.42 * saw(q / 3.3 + wob, 0.8) + 0.09 * saw(q / 0.9 + 1.7 * wob, 0.5))
    face = (yf[:, None, :] - Y) * 0.99 + ribs
    rock = smax(dome, face, 2.2)  # the lip rounded where the back meets the face
    del face, dome
    # the cave slot: along the foliation, tall and pointed, 12 m in, its lips worn round
    cx = 2.0
    cy = float(face_line(np.array([cx]))[0])
    across = NFOL[0] * (X - cx) + NFOL[1] * (Y - cy) + NFOL[2] * Z
    w = 2.8 * np.maximum(1 - (Z / 11.0) ** 2, 0) ** 0.55
    slot = np.maximum(np.maximum(np.abs(across) - w / 2, Y - (cy + 12.0)), -1.5 - Z)
    rock = smax(rock, -slot, 0.5)
    del across, slot, w
    # the shelf the ice polished, a knoll of it the camera stands on, and the skerries
    sh = 3.0 + 0.13 * (y2 - face_line(x2)) + 0.01 * (x2 - 20)  # slabs dipping to the sea, stepped along the strike
    along = (x2 * 0.42 - y2 * 0.91) / 6.0 + 0.4 * fbm2(x2 / 20.0, y2 / 20.0, 33)
    sh = sh - 0.7 * (np.floor(along) + ss(0.75, 1.0, along - np.floor(along)))
    sh = sh + 0.3 * fbm2(x2 / 8.0, y2 / 8.0, 31)
    px, py, pr = POCKET
    sh = sh - 2.6 * ss(1.0, 0.55, np.hypot((x2 - px) / pr, (y2 - py) / (pr * 0.7)))  # the pocket the shingle lies in
    kx, ky, kh = SHELF["knoll"]
    sh = smax(sh, hull(x2, y2, kx, ky, kh, 0.22, 0.5, 9, 1.2), 1.0)
    sh = sh - 5.0 * (1 - ss(SHELF["x"][0] - 6.0, SHELF["x"][0], x2)) - 4.0 * ss(SHELF["x"][1], SHELF["x"][1] + 8, x2)
    rock = smin(rock, (Z - sh[:, :, None].astype(np.float32)) * 0.85, 1.4)
    for i, (sx, sy, shh) in enumerate(((-16.0, -14.0, 2.0), (-33.0, -12.0, 2.6), (-2.0, -30.0, 1.4),
                                       (-62.0, -18.0, 1.8), (-90.0, -14.0, 2.4), (8.0, -20.0, 1.2))):
        hk = hull(x2, y2, sx, sy, shh, 0.22, 0.7, 20 + i, 0.6) + 0.12 * fbm2(x2 / 3.0, y2 / 3.0, 41)
        rock = smin(rock, (Z - hk[:, :, None].astype(np.float32)) * 0.85, 0.8)
    rock = np.maximum(rock, LO[2] + 0.5 - Z)
    # the turf: on the backs, over the lip and a little down it, torn ragged; bare on the windswept knolls
    tt = 0.16
    tface = (yf[:, None, :] - 0.12 - Y) * 0.99
    turf = smax((Z - top[:, :, None] - tt) * 0.8, tface, 1.6)
    del tface
    edge = tops(xs, face_line(xs) + 2.5)
    torn = 0.5 + 1.0 * (0.5 + 0.5 * fbm2(xs / 2.5, xs * 0 + 3.0, 61))
    turf = np.maximum(turf, (edge - torn)[:, None, None] - Z)
    turf = np.maximum(turf, 4.5 - Z)
    return rock.astype(np.float32), turf.astype(np.float32)


def surface(D):
    """The surface D = 0 as points and faces, through openvdb (a narrow band, so the grid stays sparse)."""
    D = np.clip(D, -1.0, 1.0)
    g = vdb.FloatGrid(1.0)
    g.copyFromArray(np.ascontiguousarray(D))
    p, t, q = g.convertToPolygons(0.0, 0.0)
    p = (LO + np.asarray(p) * H).astype(np.float32)
    t, q = np.asarray(t, np.int32).reshape(-1, 3), np.asarray(q, np.int32).reshape(-1, 4)
    if len(q):  # the topmost face must look up
        c = p[q].mean(1)
        i = int(np.argmax(c[:, 2]))
        n = np.cross(p[q[i, 2]] - p[q[i, 0]], p[q[i, 3]] - p[q[i, 1]])
        if n[2] < 0:
            q, t = q[:, ::-1].copy(), t[:, ::-1].copy()
    return p, t, q


def mesh(name, p, t, q):
    me = bpy.data.meshes.new(name)
    loops = np.concatenate([q.ravel(), t.ravel()]).astype(np.int32)
    sizes = np.concatenate([np.full(len(q), 4), np.full(len(t), 3)]).astype(np.int32)
    me.vertices.add(len(p))
    me.vertices.foreach_set("co", p.ravel())
    me.loops.add(len(loops))
    me.loops.foreach_set("vertex_index", loops)
    me.polygons.add(len(sizes))
    me.polygons.foreach_set("loop_start", np.concatenate([[0], np.cumsum(sizes)[:-1]]).astype(np.int32))
    me.update(calc_edges=True)
    me.validate()
    me.shade_smooth()
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    return ob


def build_land(out):
    cache = os.path.join(out, "land.npz")
    if os.path.exists(cache) and not BL.arg("--rebuild"):
        L = np.load(cache)
    else:
        t0 = time.time()
        xs, ys, zs = (np.arange(LO[i], HI[i] + 1e-6, H, dtype=np.float32) for i in range(3))
        rock, turf = land_sdf(xs, ys, zs)
        print(f"land sdf {rock.shape}: {time.time() - t0:.0f}s")
        rp, rt, rq = surface(rock)
        tp, tt, tq = surface(turf)
        at_sea = rock[:, :, int(round((0.0 - LO[2]) / H))] < 0
        np.savez(cache, rp=rp, rt=rt, rq=rq, tp=tp, tt=tt, tq=tq, at_sea=at_sea)
        L = np.load(cache)
        print(f"surfaces: {time.time() - t0:.0f}s")
    r, tu = mesh("rock", L["rp"], L["rt"], L["rq"]), mesh("turf", L["tp"], L["tt"], L["tq"])
    print(f"rock {len(r.data.polygons)} faces, turf {len(tu.data.polygons)}")
    return r, tu, L["at_sea"]


# -- the rest of the frame --------------------------------------------------------------------------------------------

def heightfield(name, x0, x1, y0, y1, step, fz):
    xs, ys = np.arange(x0, x1 + 1e-6, step), np.arange(y0, y1 + 1e-6, step)
    Xg, Yg = np.meshgrid(xs, ys, indexing="ij")
    Zg = fz(Xg, Yg)
    nx, ny = Xg.shape
    v = np.stack([Xg, Yg, Zg], -1).reshape(-1, 3).astype(np.float32)
    i = (np.arange(nx - 1)[:, None] * ny + np.arange(ny - 1)[None, :]).ravel()
    f = np.stack([i, i + ny, i + ny + 1, i + 1], -1).astype(np.int32)
    return mesh(name, v, np.zeros((0, 3), np.int32), f)


def far_land(x, y):
    """Jæren beyond the grid: rolling green behind the coast, low ground running out of the frame's left."""
    coast = np.where(x < 0, -4.0, 6.0)
    inland = y - coast
    h = (9.0 + 8.0 * fbm2(x / 160.0, y / 160.0, 91)) * ss(0.0, 30.0, inland) + 22.0 * ss(500.0, 2000.0, y) - 2.5
    h = h + 3.0 * fbm2(x / 30.0, y / 30.0, 93) * ss(0.0, 30.0, inland)
    inside = (x > LO[0] + 2) & (x < HI[0] - 2) & (y < HI[1] - 2)
    return np.where(inside, -6.0, h)


def swell_height(x, y):
    """A light swell running in from the Roads, its crests along the shore, sharp-topped; it dies at the edges
    of the near sea, where the flat far sea takes over."""
    u = (y + 0.18 * x) / 13.0 * 2 * np.pi + 0.8 * fbm2(x / 40.0, y / 40.0, 101)
    h = 0.75 * (0.5 + 0.5 * np.cos(u)) ** 3 - 0.22 + 0.08 * fbm2(x / 3.0, y / 3.0, 103)
    edge = ss(-170.0, -120.0, x) * ss(90.0, 60.0, x) * ss(-150.0, -110.0, y)
    return h * edge - 0.25 * (1 - edge)


def islands(x, y):
    """The Roads' islands on the horizon, low and whale-backed like the land they were ground from."""
    h = np.full(x.shape, -8.0)
    for cx, cy, r, hm in ((-2500.0, -170.0, 110.0, 22.0), (-1800.0, -200.0, 70.0, 12.0), (-3300.0, -260.0, 240.0, 34.0),
                          (-1350.0, -150.0, 40.0, 6.0)):
        rr = np.hypot((x - cx) / (r * 1.8), (y - cy) / r)
        h = np.maximum(h, hm * np.maximum(1 - rr * rr, 0) ** 0.6 * (1 + 0.15 * fbm2(x / 60.0, y / 60.0, 97)) - 1.0)
    return h


def erratic(name, x, y, z, r, squash, seed):
    """A boulder the ice brought: a few worn faces (a hull of points on an ellipsoid, rounded once)."""
    import bmesh
    rng = np.random.default_rng(seed)
    d = rng.normal(size=(18, 3))
    d = d / np.linalg.norm(d, axis=1, keepdims=True) * np.array([r, r * 0.8, r * squash]) * rng.uniform(0.85, 1.0, (18, 1))
    bm = bmesh.new()
    vs = [bm.verts.new(v) for v in d]
    bmesh.ops.convex_hull(bm, input=vs)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    ob.location = (x, y, z + r * squash * 0.55)
    ob.rotation_euler[2] = seed * 0.7
    sub = ob.modifiers.new("worn", "SUBSURF")
    sub.levels = sub.render_levels = 2
    me.shade_smooth()
    return ob


def ground_at(x, y):
    dg = bpy.context.evaluated_depsgraph_get()
    hit = bpy.context.scene.ray_cast(dg, mathutils.Vector((x, y, 60.0)), mathutils.Vector((0, 0, -1)))
    return hit[1].z if hit[0] else 0.0


# -- materials --------------------------------------------------------------------------------------------------------

def rock_material():
    """Phyllite by the sea: graphite and grey-green in the foliation's bands, its own planes silky (low roughness,
    not paint), rust run from the joints; the shore's zones by height, riding higher where the swell runs up."""
    m, g, bsdf = T.material("phyllite")
    P, N, x, y, z, nz = T.geometry(g)
    dot = g.node("ShaderNodeVectorMath", operation="DOT_PRODUCT")
    g.put(dot.inputs[0], P)
    dot.inputs[1].default_value = tuple(float(v) for v in NFOL)
    q = g.out(dot, "Value")
    ndf = g.node("ShaderNodeVectorMath", operation="DOT_PRODUCT")
    g.put(ndf.inputs[0], N)
    ndf.inputs[1].default_value = tuple(float(v) for v in NFOL)
    on_fol = g.ss(g.math("ABSOLUTE", g.out(ndf, "Value")), 0.70, 0.92)
    steep = g.ss(nz, 0.75, 0.45)
    band = g.noise(None, 1.0, 3.0, 0.6, dims="1D", w=g.math("MULTIPLY", q, 0.45))
    base = g.mix(g.ss(band, 0.40, 0.60), (0.048, 0.050, 0.048), (0.075, 0.088, 0.068))  # graphite, grey-green
    ny = g.out(g.node("ShaderNodeSeparateXYZ", {"Vector": N}), "Y")
    seaward = g.math("MAXIMUM", g.math("MULTIPLY", ny, -1.0), 0.0)
    zz = g.math("DIVIDE", g.math("ADD", z, g.math("MULTIPLY", g.math("SUBTRACT", g.noise(P, 0.25, 0.0), 0.5), 0.6)),
                g.math("ADD", 1.0, g.math("MULTIPLY", seaward, 0.5)))  # the zones ride higher where the swell runs up
    streak = g.noise(g.vec(g.math("MULTIPLY", x, 1.8), g.math("MULTIPLY", y, 1.8), g.math("MULTIPLY", z, 0.15)),
                     1.0, 2.0, 0.6)
    rust = g.math("MULTIPLY", g.ss(streak, 0.58, 0.70), g.ss(g.noise(P, 0.1, 1.0), 0.48, 0.6))
    rust = g.math("MULTIPLY", g.math("MULTIPLY", rust, steep), g.ss(zz, 2.0, 3.0))
    base = g.mix(g.math("MULTIPLY", rust, 0.8), base, (0.15, 0.06, 0.02))
    grey = g.math("MULTIPLY", g.math("MULTIPLY", g.ss(zz, 4.5, 7.0), g.ss(g.noise(P, 0.4, 3.0, 0.6), 0.45, 0.6)),
                  g.ss(nz, 0.15, 0.6))  # grey lichen on what faces the sky, above the spray
    c = g.mix(g.math("MULTIPLY", grey, 0.8), base, (0.26, 0.27, 0.24))
    perch = g.math("MULTIPLY", g.ss(nz, 0.45, 0.8), g.ss(g.noise(P, 0.45, 2.0), 0.5, 0.6))  # where the birds sit
    under = g.math("MULTIPLY", g.math("MULTIPLY", steep, g.ss(streak, 0.66, 0.74)), 0.25)  # and what runs from it
    orange = g.math("MULTIPLY", g.math("MULTIPLY", g.ss(zz, 1.7, 2.4), g.ss(zz, 9.0, 6.0)),
                    g.math("MAXIMUM", perch, under))
    c = g.mix(g.math("MULTIPLY", orange, 0.85), c, (0.42, 0.17, 0.025))
    black = g.math("MULTIPLY", g.ss(zz, 0.45, 0.75), g.ss(zz, 2.1, 1.7))
    c = g.mix(g.math("MULTIPLY", black, 0.95), c, (0.012, 0.012, 0.011))
    barn = g.math("MULTIPLY", g.ss(zz, -0.15, 0.05), g.ss(zz, 0.6, 0.4))
    c = g.mix(g.math("MULTIPLY", barn, g.ss(g.noise(P, 3.0, 2.0), 0.35, 0.5)), c, (0.25, 0.24, 0.21))
    wrack = g.math("MULTIPLY", g.ss(zz, 0.05, -0.3), g.ss(nz, -0.3, 0.3))
    c = g.mix(wrack, c, (0.05, 0.035, 0.012))
    wet = g.ss(z, 0.9, 0.2)
    c = g.mix(g.math("MULTIPLY", wet, 0.5), c, g.scale(c, 0.55))
    g.put(bsdf.inputs["Base Color"], c)
    dry = g.math("MAXIMUM", grey, g.math("MAXIMUM", orange, barn))
    rough = g.mixf(g.math("MULTIPLY", on_fol, g.math("SUBTRACT", 1.0, dry)), 0.72, 0.26)
    g.put(bsdf.inputs["Roughness"], g.mixf(wet, rough, 0.15))
    g.put(bsdf.inputs["Specular IOR Level"], g.mixf(on_fol, 0.5, 0.75))
    wob = g.math("MULTIPLY", g.noise(P, 0.15, 1.0), 1.2)  # planar: the foliation does not wander
    ribs = g.math("FRACT", g.math("ADD", g.math("DIVIDE", q, 0.31), wob))
    ribs = g.math("MULTIPLY", g.math("MULTIPLY", ribs, g.ss(ribs, 1.0, 0.75)), steep)
    ribs = g.math("MULTIPLY", ribs, g.ss(g.noise(P, 0.6, 2.0), 0.35, 0.6))  # here and there, not as a pattern
    h = g.math("ADD", g.math("MULTIPLY", ribs, 0.35), g.math("MULTIPLY", g.noise(P, 1.4, 4.0, 0.6), 1.6))
    bump = g.node("ShaderNodeBump", {"Strength": 0.35, "Distance": 0.03, "Height": h})
    g.put(bsdf.inputs["Normal"], g.out(bump, "Normal"))
    return m


def shingle_material():
    """Shingle the sea rolled: rounded cobbles of what the ice brought (granite, gneiss, quartz) with the local
    phyllite, pale above the wash, dark and glossy where the swash reaches."""
    m, g, bsdf = T.material("shingle")
    P, N, x, y, z, nz = T.geometry(g)
    vo = g.node("ShaderNodeTexVoronoi", {"Vector": P, "Scale": 9.0, "Randomness": 0.9}, feature="F1")
    d, cc = g.out(vo, "Distance"), g.out(vo, "Color")
    sep = g.node("ShaderNodeSeparateColor", {"Color": cc})
    r, gg = g.out(sep, "Red"), g.out(sep, "Green")
    c = g.mix(g.ss(r, 0.3, 0.7), (0.20, 0.19, 0.17), (0.40, 0.38, 0.34))
    c = g.mix(g.ss(gg, 0.75, 0.8), c, (0.06, 0.06, 0.058))
    c = g.mix(g.math("MULTIPLY", g.ss(gg, 0.1, 0.05), 0.8), c, (0.52, 0.48, 0.42))
    wet = g.ss(z, 0.5, 0.0)
    c = g.mix(g.math("MULTIPLY", wet, 0.6), c, g.scale(c, 0.5))
    g.put(bsdf.inputs["Base Color"], c)
    g.put(bsdf.inputs["Roughness"], g.mixf(wet, 0.6, 0.15))
    b = g.node("ShaderNodeBump", {"Strength": 0.9, "Distance": 0.05, "Height": g.math("SUBTRACT", 1.0, g.ss(d, 0.0, 0.5))})
    g.put(bsdf.inputs["Normal"], g.out(b, "Normal"))
    return m


def plain(name, c, rough, bump=0.0, scale=1.0, c2=None):
    m, g, bsdf = T.material(name)
    P, N, x, y, z, nz = T.geometry(g)
    col = c if c2 is None else g.mix(g.ss(g.noise(P, scale, 3.0, 0.6), 0.35, 0.65), c, c2)
    g.put(bsdf.inputs["Base Color"], col)
    g.put(bsdf.inputs["Roughness"], rough)
    if bump:
        b = g.node("ShaderNodeBump", {"Strength": bump, "Distance": 0.05, "Height": g.noise(P, scale * 6, 3.0)})
        g.put(bsdf.inputs["Normal"], g.out(b, "Normal"))
    return m


def turf_material():
    """Unkept turf by the sea: grass and heath in patches, bleached straw where the wind and the spray reach (the
    lip and the knolls), sea pinks on the edge."""
    m, g, bsdf = T.material("turf")
    P, N, x, y, z, nz = T.geometry(g)
    green = g.mix(g.ss(g.noise(P, 0.12, 3.0, 0.6), 0.38, 0.62), (0.045, 0.11, 0.012), (0.10, 0.16, 0.018))
    heath = g.math("MULTIPLY", g.ss(g.noise(P, 0.3, 3.0, 0.6), 0.56, 0.66), 0.8)
    c = g.mix(heath, green, (0.06, 0.045, 0.03))
    lip = g.ss(nz, 0.9, 0.55)
    straw = g.math("MAXIMUM", g.math("MULTIPLY", lip, g.ss(g.noise(P, 1.2, 2.0), 0.35, 0.55)),
                   g.math("MULTIPLY", g.ss(g.noise(P, 0.5, 3.0, 0.6), 0.64, 0.72), 0.55))
    c = g.mix(g.math("MULTIPLY", straw, 0.8), c, (0.20, 0.16, 0.075))
    thrift = g.math("MULTIPLY", g.ss(g.noise(P, 4.0, 1.0), 0.70, 0.75), lip)
    c = g.mix(g.math("MULTIPLY", thrift, 0.7), c, (0.40, 0.15, 0.22))
    g.put(bsdf.inputs["Base Color"], c)
    g.put(bsdf.inputs["Roughness"], 0.9)
    b = g.node("ShaderNodeBump", {"Strength": 0.7, "Distance": 0.1, "Height": g.noise(P, 3.0, 4.0, 0.7)})
    g.put(bsdf.inputs["Normal"], g.out(b, "Normal"))
    return m


def fields_material():
    m, g, bsdf = T.material("fields")
    P, N, x, y, z, nz = T.geometry(g)
    c = g.mix(g.ss(g.noise(P, 0.01, 2.0), 0.4, 0.6), (0.05, 0.088, 0.024), (0.085, 0.10, 0.035))
    c = g.mix(g.math("MULTIPLY", g.ss(g.noise(P, 0.05, 1.0), 0.6, 0.66), 0.7), c, (0.16, 0.13, 0.06))
    g.put(bsdf.inputs["Base Color"], c)
    g.put(bsdf.inputs["Roughness"], 0.9)
    return m


def sea_material(foam_img):
    m, g, bsdf = T.material("sea")
    P, N, x, y, z, nz = T.geometry(g)
    st = g.vec(g.math("MULTIPLY", x, 0.35), y, 0.0)
    h = g.math("ADD", g.noise(st, 1.6, 2.0, 0.5), g.math("MULTIPLY", g.noise(st, 0.12, 0.0), 2.0))
    bump = g.node("ShaderNodeBump", {"Strength": 0.35, "Distance": 0.05, "Height": h})
    uv = g.vec(g.math("DIVIDE", g.math("SUBTRACT", x, float(LO[0])), float(HI[0] - LO[0])),
               g.math("DIVIDE", g.math("SUBTRACT", y, float(LO[1])), float(HI[1] - LO[1])), 0.0)
    tex = g.node("ShaderNodeTexImage", {"Vector": uv}, image=foam_img, extension="CLIP")
    near = g.out(tex, "Color")
    lace = g.noise(g.vec(g.math("MULTIPLY", x, 0.45), g.math("MULTIPLY", y, 1.4), 0.0), 1.1, 4.0, 0.7)
    lace = g.ss(g.math("ADD", lace, g.math("MULTIPLY", near, 0.35)), 0.62, 0.7)  # streaks drawn out along the shore
    foam = g.math("MAXIMUM", g.ss(near, 0.55, 0.85), g.math("MULTIPLY", lace, g.ss(near, 0.08, 0.3)))
    g.put(bsdf.inputs["Base Color"], g.mix(foam, T.COL["sea"], (0.62, 0.64, 0.62)))
    g.put(bsdf.inputs["Roughness"], g.mixf(foam, 0.08, 0.7))
    g.put(bsdf.inputs["Normal"], g.out(bump, "Normal"))
    return m


def foam_image(rock_at_sea):
    """Foam where the swell meets the rock: thick at the rock, a second band a few metres out."""
    occ = rock_at_sea.astype(bool)
    d = BL.edt(occ, H, 12.0)
    wob = 0.5 + 0.5 * vnoise2(np.arange(occ.shape[0])[:, None] * H / 3.0, np.arange(occ.shape[1])[None, :] * H / 3.0, 71)
    band = np.exp(-d / 1.3) + 0.55 * np.exp(-((d - 3.0) / 0.9) ** 2) * wob + 0.15 * np.exp(-d / 4.0)
    band = np.where(occ, 1.0, band)
    ex, ey = np.arange(occ.shape[0]) * H, np.arange(occ.shape[1]) * H  # let go before the grid's edge
    band *= (ss(0.0, 10.0, ex) * ss(0.0, 10.0, ex[-1] - ex))[:, None] * (ss(0.0, 10.0, ey) * ss(0.0, 10.0, ey[-1] - ey))[None, :]
    im = bpy.data.images.new("foam", occ.shape[0], occ.shape[1], float_buffer=True)
    im.colorspace_settings.name = "Non-Color"  # before the pixels: a generated image regenerates when it changes
    px = np.ones((occ.shape[1], occ.shape[0], 4), np.float32)
    px[..., :3] = band.T[..., None]
    im.pixels = px.ravel()
    im.pack()
    return im


# -- light, camera, the finish ----------------------------------------------------------------------------------------

def rig():
    T.world()
    bg = next(n for n in bpy.context.scene.world.node_tree.nodes if n.type == "BACKGROUND")
    bg.inputs["Strength"].default_value = 1.0  # the shade lit by the sky, but the sun the key
    lamp = bpy.data.lights.new("sun", "SUN")
    lamp.energy = T.SUN["energy"]
    lamp.color = T.SUN["color"]
    lamp.angle = math.radians(0.6)
    ob = bpy.data.objects.new("sun", lamp)
    bpy.context.scene.collection.objects.link(ob)
    az, el = math.radians(T.SUN["azimuth"]), math.radians(T.SUN["elevation"])
    d = mathutils.Vector((math.sin(az) * math.cos(el), math.cos(az) * math.cos(el), math.sin(el)))
    ob.rotation_euler = (-d).to_track_quat("-Z", "Y").to_euler()


def camera(cam):
    x, y, lx, ly, lz, lens = cam
    p = mathutils.Vector((x, y, ground_at(x, y) + 1.6))
    cd = bpy.data.cameras.new("cam")
    cd.lens, cd.sensor_width = lens, 36.0
    ob = bpy.data.objects.new("cam", cd)
    bpy.context.scene.collection.objects.link(ob)
    ob.location = p
    ob.rotation_euler = (mathutils.Vector((lx, ly, lz)) - p).to_track_quat("-Z", "Y").to_euler()
    bpy.context.scene.camera = ob
    print(f"camera at {tuple(round(v, 2) for v in p)}")


def pixels(path):
    im = bpy.data.images.load(path)
    im.colorspace_settings.name = "Non-Color"
    w, h = im.size
    a = np.array(im.pixels[:], np.float32).reshape(h, w, 4)[::-1, :, :3]
    bpy.data.images.remove(im)
    return a


def box(a, k):
    """Mean over a (2k+1) square, by integral images."""
    p = np.pad(a, ((k + 1, k), (k + 1, k)) + ((0, 0),) * (a.ndim - 2), mode="edge")
    c = p.cumsum(0).cumsum(1)
    n = 2 * k + 1
    return (c[n:, n:] - c[:-n, n:] - c[n:, :-n] + c[:-n, :-n]) / (n * n)


def kuwahara(img, k):
    """Each pixel takes the mean of the least varied of its four quadrants: flat strokes that keep their edges."""
    lum = img.mean(-1)
    m, l1, l2 = box(img, k), box(lum, k), box(lum * lum, k)
    var = l2 - l1 * l1
    best = np.full(lum.shape, np.inf, np.float32)
    out = img.copy()
    h, w = lum.shape

    def shift(a, dy, dx):  # a[y + dy, x + dx], the border held
        p = np.pad(a, ((k, k), (k, k)) + ((0, 0),) * (a.ndim - 2), mode="edge")
        return p[k + dy:k + dy + h, k + dx:k + dx + w]

    for dy in (-k, k):
        for dx in (-k, k):
            v = shift(var, dy, dx)
            take = v < best
            best = np.where(take, v, best)
            out = np.where(take[..., None], shift(m, dy, dx), out)
    return out


def paint(out, name):
    """The painter's finish: air by distance, strokes finer near than far, the edges of the frame let go, canvas."""
    srgb = pixels(os.path.join(out, f"{name}-render.png"))
    d = pixels(os.path.join(out, f"{name}-geo.png"))[..., 0] * 400.0
    sky = d <= 0.0
    d = np.where(sky, 4000.0, d)
    air = (1 - np.exp(-np.maximum(d - 25.0, 0) / 260.0)) * ~sky
    haze = np.array([0.72, 0.70, 0.69], np.float32)
    img = srgb * (1 - air[..., None] * 0.72) + haze * air[..., None] * 0.72
    k1, k2, k3 = kuwahara(img, 1), kuwahara(img, 2), kuwahara(img, 5)
    t1, t2 = ss(25.0, 70.0, d)[..., None], ss(120.0, 400.0, d)[..., None]
    pt = k1 * (1 - t1) + k2 * t1
    pt = pt * (1 - t2) + k3 * t2
    pt = 0.8 * pt + 0.2 * img  # the drawing kept under the strokes
    lum = pt.mean(-1, keepdims=True)  # the value plan: darks deeper, lights warmer, the shade cool
    curve = lum + 0.55 * (lum - 0.42) * lum * (1 - lum) * 4 * 0.5
    pt = pt * (curve / np.maximum(lum, 1e-3))
    warm = ss(0.45, 0.85, lum)
    pt = pt * (1 + warm * np.array([0.05, 0.0, -0.06], np.float32)) * (1 + (1 - warm) * np.array([-0.03, 0.0, 0.04], np.float32))
    h, w = d.shape
    yy, xx = np.mgrid[0:h, 0:w]
    r = np.hypot((xx - w * 0.55) / w, (yy - h * 0.45) / h)
    pt = pt * (1 - 0.22 * ss(0.35, 0.75, r))[..., None]
    canvas = box(np.random.default_rng(1989).random((h, w)).astype(np.float32), 1)
    pt = np.clip(pt + (canvas[..., None] - 0.5) * 0.035, 0, 1)
    o = bpy.data.images.new("painted", w, h, alpha=False)
    o.colorspace_settings.name = "Non-Color"
    px = np.ones((h, w, 4), np.float32)
    px[..., :3] = pt[::-1]
    o.pixels = px.ravel()
    o.filepath_raw = os.path.join(out, f"{name}-target.png")
    o.file_format = "PNG"
    o.save()
    print("wrote", o.filepath_raw)


def main():
    out = BL.arg("--out")
    os.makedirs(out, exist_ok=True)
    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o)
    t0 = time.time()
    grey = bool(BL.arg("--grey"))
    cam = tuple(float(v) for v in BL.arg("--cam").split(",")) if BL.arg("--cam") else CAM
    rock, turf, at_sea = build_land(out)
    px, py, pr = POCKET
    shingle = heightfield("shingle", px - pr, px + pr, py - pr, py + pr, 0.25,
                          lambda x, y: np.where(np.hypot((x - px) / pr, (y - py) / (pr * 0.7)) < 0.95,
                                                -0.4 + 0.22 * (y - py + pr * 0.6) - 0.012 * (x - px) ** 2
                                                + 0.05 * fbm2(x / 1.2, y / 1.2, 81), -3.0))
    far = heightfield("far", -1600.0, 1600.0, -12.0, 2000.0, 8.0, far_land)
    sea = heightfield("sea", -4000.0, 4000.0, -4000.0, 80.0, 40.0, lambda x, y: x * 0 - 0.25)
    swell = heightfield("swell", -170.0, 90.0, -150.0, 62.0, 0.5, swell_height)
    isles = heightfield("isles", -3700.0, -1200.0, -600.0, -20.0, 10.0, islands)
    errs = []
    for i, (x, y, r, sq) in enumerate(((38.0, -31.0, 1.3, 0.7), (41.5, -28.0, 0.8, 0.75), (-71.0, 4.0, 1.2, 0.7),
                                       (14.0, 8.0, 1.9, 0.7), (-40.0, 6.0, 1.5, 0.75), (-4.0, 18.0, 1.2, 0.7),
                                       (-60.0, 4.0, 2.2, 0.7), (22.0, -12.0, 1.1, 0.7))):
        errs.append(erratic(f"erratic{i}", x, y, ground_at(x, y), r, sq, 3 + 2 * i))
    if grey:
        clay = BL.material("clay", (0.20, 0.20, 0.20), 0.8)
        for o in (rock, turf, shingle, far, *errs):
            o.data.materials.append(clay)
        sea.data.materials.append(BL.material("sea", (0.02, 0.025, 0.03), 0.12))
        swell.data.materials.append(sea.data.materials[0])
        isles.data.materials.append(clay)
    else:
        rock.data.materials.append(rock_material())
        turf.data.materials.append(turf_material())
        shingle.data.materials.append(shingle_material())
        far.data.materials.append(fields_material())
        granite = plain("granite", (0.25, 0.24, 0.22), 0.7, 0.3, 1.2, (0.33, 0.33, 0.31))
        for e in errs:
            e.data.materials.append(granite)
        sm = sea_material(foam_image(at_sea))
        sea.data.materials.append(sm)
        swell.data.materials.append(sm)
        isles.data.materials.append(fields_material())
    rig()
    camera(cam)
    T.cycles(int(BL.arg("--w", 1600)), int(BL.arg("--h", 900)), int(BL.arg("--samples", 96)))
    bpy.context.scene.view_settings.exposure = float(BL.arg("--exposure", 0.0))
    name = "grey" if grey else "cave"
    sc = bpy.context.scene
    sc.render.filepath = os.path.join(out, f"{name}-render.png")
    bpy.ops.render.render(write_still=True)
    print("wrote", sc.render.filepath, f"{time.time() - t0:.0f}s")
    if not grey:
        T.geo_pass(out, name)
        paint(out, name)
    print(f"done {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
