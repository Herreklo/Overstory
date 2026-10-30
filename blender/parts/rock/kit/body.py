"""r02: the Holm tip's shore block as designed signed-distance bodies (kit.json `body`), silhouette first.

The record constrains it (the crest at the record's back over t09's crest, the ice's way, t09's seaward waterline, 107
on its stand); the form is drawn: a long section along the crest line, a plan of half widths and a cross section's
power each side make one smooth back. Blocks part along the record's joints, each the back on one side of a joint,
then cut by planes and plucked (convex pieces taken out); the joints are real gaps. Every cut is a rolling-ball round
of its kind's radius, so its width on each face is r tan(angle / 2) and planes meeting gently keep their flats. Meshed
by openvdb in a narrow band round a coarse grid.

    Blender -b --factory-startup -P body.py -- --out DIR [--step 1|2] [--fine M]

Step 1 renders flat silhouettes of r02, t09 (W.blend's W-high) and the t13 study (its scan.blend, measured and drawn
only, never built on) from the same cameras (the lone views and tip.views' water frame, with 107), and draws the long
section and the plan of all three. Step 2 checks for splinters (`spike`), meshes the blocks, cuts the near level to
the street's budget by surface, and shoots the grey check: Eevee, a neutral sun (az 330, el 35) and a raking one (az
255, el 7), the eye, 12 m, sea, lee and water views, with 107; `body.json` holds the measures.
"""
import json, math, os, sys

import bpy
import numpy as np
import openvdb as vdb
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path[:0] = [HERE, os.path.dirname(HERE)]
import blockin as BI  # noqa: E402
import outcrop  # noqa: E402


def arg(n, d=None):
    a = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    return a[a.index(n) + 1] if n in a else d


K = json.load(open(os.path.join(HERE, "kit.json")))
B = K["body"]
FIX = BI.FIX
OUT = os.path.abspath(arg("--out", os.path.join(ROOT, "cache", "rock", "kit", "renders", "r02")))
A = math.radians(FIX["rock"]["ice"]["toward"])
E = np.array([math.sin(A), math.cos(A)])  # down-ice, s
W = np.array([-math.cos(A), math.sin(A)])  # landward, t
C0 = np.array(B["crestAt"], float)
R = B["round"]


def way(b):
    b = math.radians(b)
    return np.array([math.sin(b), math.cos(b)])


def to_site(s, t, z):
    return np.stack([C0[0] + E[0] * s + W[0] * t, C0[1] + E[1] * s + W[1] * t, z], -1)


# ---------------------------------------------------------------- the smooth back
def pchip(xs, ys, x):
    """Monotone cubic through the stations (Fritsch-Carlson), held flat past the ends."""
    xs, ys = np.asarray(xs, float), np.asarray(ys, float)
    h = np.diff(xs); dl = np.diff(ys) / h; m = np.zeros_like(ys)
    for k in range(1, len(xs) - 1):
        if dl[k - 1] * dl[k] > 0:
            w1, w2 = 2 * h[k] + h[k - 1], h[k] + 2 * h[k - 1]
            m[k] = (w1 + w2) / (w1 / dl[k - 1] + w2 / dl[k])
    m[0], m[-1] = dl[0], dl[-1]
    x = np.clip(x, xs[0], xs[-1]); i = np.clip(np.searchsorted(xs, x) - 1, 0, len(h) - 1)
    u = (x - xs[i]) / h[i]
    return ((1 + 2 * u) * (1 - u) ** 2 * ys[i] + u * (1 - u) ** 2 * h[i] * m[i]
            + u * u * (3 - 2 * u) * ys[i + 1] + u * u * (u - 1) * h[i] * m[i + 1])


SEC = np.array(B["section"], float)
HS_, HSEA, HLAND = B["half"]["s"], B["half"]["sea"], B["half"]["land"]


def height(s, t):
    """The back's top: the section along the crest line, falling across it by the cross section's power each side."""
    top = pchip(SEC[:, 0], SEC[:, 1], s); foot = B["footM"]
    t = t - pchip(B["crestLine"]["s"], B["crestLine"]["t"], s)
    sea = t < 0
    w = np.where(sea, pchip(HS_, HSEA, s), pchip(HS_, HLAND, s))
    p = np.where(sea, B["cross"]["sea"], B["cross"]["land"])
    u = np.abs(t) / w
    return foot + (top - foot) * (1 - u ** p)


def back(s, t, z):
    """The back's distance (first order: the height's gap over its slope) and its unit gradient in (s, t, z)."""
    e = 0.01
    h = height(s, t)
    hs = (height(s + e, t) - height(s - e, t)) / (2 * e)
    ht = (height(s, t + e) - height(s, t - e)) / (2 * e)
    k = np.sqrt(1 + hs * hs + ht * ht)
    return (z - h) / k, np.stack([-hs / k, -ht / k, 1 / k], -1)


# ---------------------------------------------------------------- planes and rounds, in the ice frame (s, t, z)
def plane(spec, off=0.0, flip=False):
    """[facing, slope, [s, t, z], kind]: a face facing bearing `facing`, `slope` degrees from level, through the point;
    the rock where n.p <= d. `off` moves it outward; `flip` takes its far side (the rock beyond it)."""
    face, slope, p, kind = spec[:4]
    a = math.radians(slope); h = way(face) * math.sin(a)
    n = np.array([h @ E, h @ W, math.cos(a)])  # site bearing into the ice frame
    d = float(n @ np.asarray(p, float)) + off
    if flip:
        n, d = -n, -d
    return n, d, kind


def cut(d, g, n, dn, r):
    """The body (d, g) cut by the half-space n.p <= dn with its arris rounded by a rolling ball of radius r: the exact
    distance to the wedge both eroded by r, less r. The wedge's angle is read from the body's gradient here."""
    a1, b1 = d + r, dn + r
    c = np.clip(np.einsum("ij,j->i", g, n), -0.9999, 0.9999); s2 = 1 - c * c
    inside = (a1 <= 0) & (b1 <= 0)
    r1 = (a1 > 0) & (b1 - a1 * c <= 0)
    r2 = ~r1 & (b1 > 0) & (a1 - b1 * c <= 0)
    corner = ~(inside | r1 | r2)
    D = np.where(a1 >= b1, a1, b1); G = np.where((a1 >= b1)[:, None], g, n[None, :])
    D = np.where(r1, a1, D); G = np.where(r1[:, None], g, G)
    D = np.where(r2, b1, D); G = np.where(r2[:, None], n[None, :], G)
    q = np.sqrt(np.maximum(a1 * a1 + b1 * b1 - 2 * a1 * b1 * c, 0) / s2)
    gc = ((a1 - b1 * c) / s2)[:, None] * g + ((b1 - a1 * c) / s2)[:, None] * n[None, :]
    gc /= np.maximum(np.linalg.norm(gc, axis=1), 1e-9)[:, None]
    D = np.where(corner, q, D); G = np.where(corner[:, None], gc, G)
    return D - r, G


FOOT = (np.array([0.0, 0.0, -1.0]), -B["footM"], "base")


def removed(d, g, P, faces):
    """The body (d, g) less a convex region: the rock where it is behind any one of the region's faces (each a rock
    face, its normal into the region), each face's arris its kind's round; the corners inside the region stay crisp."""
    out = None
    for n, dn, kind in faces:
        di, gi = cut(d, g, n, P @ n - dn, R[kind])
        if out is None:
            out = [di, gi]
        else:
            k = di < out[0]; out[0] = np.where(k, di, out[0]); out[1] = np.where(k[:, None], gi, out[1])
    return out[0], out[1]


def face(x, gap):
    """A rock face: a plane, or a joint's side by name (`J` its near side, `~J` its far side, across the gap)."""
    if isinstance(x, list):
        return plane(x)
    n, dn, kind = plane(B["joints"][x.lstrip("~")])
    return (-n, -dn - gap / 2, kind) if x.startswith("~") else (n, dn - gap / 2, kind)


def joint(x, gap):
    """A joint as a real gap `gap` wide: its two faces, and with `fromS` its end, the gap only down-ice of it."""
    j = x if isinstance(x, str) else x["joint"]
    n, dn, kind = plane(B["joints"][j])
    faces = [(n, dn - gap / 2, kind), (-n, -dn - gap / 2, kind)]
    if isinstance(x, dict):
        faces.append((np.array([1.0, 0.0, 0.0]), x["fromS"], kind))
    return faces


def block(P, X):
    """One rigid block of the back: the smooth back on its `side` of a joint (across half the gap), cut by its `cuts`,
    parted by the joints in its `split` and plucked: each of `pluck` a joint-bounded region taken out, its faces the
    rock left (a riser, a tread, a side on a joint)."""
    d, g = back(P[:, 0], P[:, 1], P[:, 2])
    if "side" in X:
        (j, sign), gap = X["side"], B["gapM"]
        n, dn, kind = plane(B["joints"][j])
        d, g = cut(d, g, n, P @ n - dn + gap / 2, R[kind]) if sign > 0 else cut(d, g, -n, dn - P @ n + gap / 2, R[kind])
    for n, dn, kind in [plane(x) for x in X.get("cuts", [])]:
        d, g = cut(d, g, n, P @ n - dn, R[kind])
    for x in X.get("split", []):
        d, g = removed(d, g, P, joint(x, B["gapM"]))
    for Y in X.get("pluck", []):
        d, g = removed(d, g, P, [face(f, B["gapM"]) for f in Y["faces"]])
    return d, g


def bodies():
    """The blocks, each as (name, how to evaluate it)."""
    return [(X["id"], lambda P, X=X: block(P, X)) for X in B["blocks"]]


BOUNDS = {}


def sdf(P):
    """The union of the bodies, each evaluated only within its bounds (`fit_bounds`), and the foot."""
    d = np.ones(len(P))
    for name, f in bodies():
        lo, hi = BOUNDS.get(name, (None, None))
        m = np.ones(len(P), bool) if lo is None else np.all((P >= lo) & (P <= hi), 1)
        if m.any():
            d[m] = np.minimum(d[m], f(P[m])[0])
    return np.maximum(d, P @ FOOT[0] - FOOT[1])


def lattice(vs):
    (s0, s1), (t0, t1), (z0, z1) = B["box"]
    return np.array([s0, t0, z0]), (int((s1 - s0) / vs) + 1, int((t1 - t0) / vs) + 1, int((z1 - z0) / vs) + 1)


def chunks(vs):
    """The box's lattice points at vs, a z-slab of about 4 million at a time: (first k, slab shape, points)."""
    o, (ns, nt, nz) = lattice(vs)
    S_, T_ = np.meshgrid(o[0] + np.arange(ns) * vs, o[1] + np.arange(nt) * vs, indexing="ij")
    step = max(1, int(4e6 // (ns * nt)))
    for k0 in range(0, nz, step):
        k = np.arange(k0, min(nz, k0 + step))
        yield k0, (ns, nt, len(k)), np.stack([np.repeat(S_[..., None], len(k), 2), np.repeat(T_[..., None], len(k), 2),
                                              np.broadcast_to(o[2] + k * vs, (ns, nt, len(k)))], -1).reshape(-1, 3)


def banded(P, coarse, bg):
    """sdf at P, evaluated only within bandM of the surface by the coarse field (cvs, array); beyond it, +-bg."""
    if coarse is None:
        return sdf(P)
    cvs, C = coarse; o, _ = lattice(cvs)
    i = np.clip(np.rint((P - o) / cvs).astype(int), 0, np.array(C.shape) - 1)
    c = C[i[:, 0], i[:, 1], i[:, 2]]; a = np.where(c < 0, -bg, bg).astype(float); m = np.abs(c) < B["bandM"]
    a[m] = sdf(P[m])
    return a


def dense(vs, coarse=None):
    o, shape = lattice(vs); A = np.empty(shape, np.float32)
    for k0, sh, P in chunks(vs):
        A[:, :, k0:k0 + sh[2]] = banded(P, coarse, 1.0).reshape(sh)
    return A


def fit_bounds(vs=0.1):
    """Each body's bounds from a coarse pass, two voxels round what it holds."""
    BOUNDS.clear()
    P = np.concatenate([P for _, _, P in chunks(vs)])
    for name, f in bodies():
        m = f(P)[0] < vs
        BOUNDS[name] = (P[m].min(0) - 2 * vs, P[m].max(0) + 2 * vs)


def spikes():
    """Splinters measured: at each surface voxel, the share of a cube `ballM` round it that is rock (a flat face 0.5,
    a square edge 0.25, a square corner 0.125, a splinter far less). Voxels above `aboveM` under `least` are spikes,
    gathered by half-metre cell as [s, t, z, voxels, least share]."""
    sp = B["spike"]; vs = sp["voxelM"]; o, _ = lattice(vs)
    I = (dense(vs, (0.08, dense(0.08))) < 0).astype(np.int32)
    r = int(round(sp["ballM"] / vs)); k = 2 * r + 1
    J = np.pad(I, r + 1)
    for ax in range(3):
        J = np.cumsum(J, ax, dtype=np.int32)
    a, b = slice(k, None), slice(None, -k)
    sl = lambda x, y, z: J[x][:, y][:, :, z]  # noqa: E731
    box = (sl(a, a, a) - sl(b, a, a) - sl(a, b, a) - sl(a, a, b) + sl(b, b, a) + sl(b, a, b) + sl(a, b, b) - sl(b, b, b))
    cov = box[:I.shape[0], :I.shape[1], :I.shape[2]] / k ** 3
    out = np.zeros_like(I, bool)
    for ax in range(3):
        for sh in (1, -1):
            out |= np.roll(I, sh, ax) == 0
    surf = (I == 1) & out
    zz = o[2] + np.arange(I.shape[2]) * vs
    bad = surf & (cov < sp["least"]) & (zz >= sp["aboveM"])[None, None, :]
    ii = np.argwhere(bad); P = o + ii * vs; c = cov[bad]
    cells = {}
    for p, v in zip(P, c):
        key = tuple(np.floor(p / 0.5).astype(int))
        n, lo, q = cells.get(key, (0, 1.0, p))
        cells[key] = (n + 1, min(lo, float(v)), q)
    return {"spikeVoxels": int(bad.sum()), "leastShare": round(float(cov[surf & (zz >= sp["aboveM"])[None, None, :]].min()), 3),
            "spikes": sorted([[round(float(x), 1) for x in q] + [n, round(lo, 3)] for n, lo, q in cells.values()], key=lambda e: e[4])}


# ---------------------------------------------------------------- meshing
def mesh(name, mat, vs=None):
    """The body's zero level meshed by openvdb from a voxel grid in the ice frame, then turned into the site."""
    vs = vs or B["voxelM"]; o, _ = lattice(vs)
    bg = 3 * vs; grid = vdb.FloatGrid(bg); grid.transform = vdb.createLinearTransform(voxelSize=vs)
    coarse = (0.08, dense(0.08)) if vs < 0.03 else None
    for k0, sh, P in chunks(vs):
        a = np.clip(banded(P, coarse, bg), -bg, bg).astype(np.float32).reshape(sh)
        grid.copyFromArray(a, ijk=(0, 0, k0), tolerance=0)
    pts, tris, quads = grid.convertToPolygons(isovalue=0.0, adaptivity=0.0)
    pts = np.asarray(pts, float) + o
    V = to_site(pts[:, 0], pts[:, 1], pts[:, 2])
    me = bpy.data.meshes.new(name)
    me.from_pydata(V.tolist(), [], [list(f) for f in np.asarray(tris)] + [list(f) for f in np.asarray(quads)])
    me.validate(); me.materials.append(mat)
    for p in me.polygons:
        p.use_smooth = True
    ob = bpy.data.objects.new(name, me); bpy.context.scene.collection.objects.link(ob)
    ob.select_set(True); bpy.context.view_layer.objects.active = ob
    bpy.ops.object.mode_set(mode="EDIT"); bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.mesh.normals_make_consistent(inside=False); bpy.ops.object.mode_set(mode="OBJECT")
    return ob


# ---------------------------------------------------------------- the frame
def flat(name, v):
    m = bpy.data.materials.new(name); m.diffuse_color = (v, v, v, 1)
    return m


def append(blend, name, mat):
    with bpy.data.libraries.load(blend) as (_, dst):
        dst.objects = [name]
    ob = dst.objects[0]; bpy.context.scene.collection.objects.link(ob)
    ob.data.materials.clear(); ob.data.materials.append(mat)
    return ob


def smooth(a, b, x):
    q = np.clip((x - a) / (b - a), 0, 1)
    return q * q * (3 - 2 * q)


def lowered(X, Y):
    """The record's smooth landform lowered round the block (kit.json body.ground): most in the lee's hollow, less on
    the land flank, fading with distance from the crest."""
    G = B["ground"]; L = outcrop.Landform(FIX["outcrop"]["landform"]).smooth(X.ravel(), Y.ravel()).reshape(X.shape)
    s = (X - C0[0]) * E[0] + (Y - C0[1]) * E[1]
    low = G["lowerFlankM"] + (G["lowerLeeM"] - G["lowerFlankM"]) * smooth(*G["leeFromS"], s)
    return L - low * (1 - smooth(G["nearM"], G["farM"], np.hypot(X - C0[0], Y - C0[1])))


def land(mat, st=0.25):
    """The ground round the block, above the sea: the frame's back and 107's ground, and where the land flank sinks."""
    x0, x1, y0, y1 = K["scan"]["landRegion"]
    X, Y = np.meshgrid(np.arange(x0, x1 + 1e-6, st), np.arange(y0, y1 + 1e-6, st), indexing="ij")
    Z = lowered(X, Y); nx, ny = X.shape; idx = np.arange(nx * ny).reshape(nx, ny)
    q = np.stack([idx[:-1, :-1], idx[1:, :-1], idx[1:, 1:], idx[:-1, 1:]], -1).reshape(-1, 4)
    q = q[(Z.ravel()[q] > -0.3).any(1)]
    me = bpy.data.meshes.new("land"); me.from_pydata(np.stack([X.ravel(), Y.ravel(), Z.ravel()], 1).tolist(), [], q.tolist())
    me.materials.append(mat); ob = bpy.data.objects.new("land", me); bpy.context.scene.collection.objects.link(ob)
    return ob


def house(mat):
    """107 on its stand (fixture `buildings`), as tip.py puts it, on a plinth down to the lowered land."""
    hj = json.load(open(os.path.join(ROOT, K["beside"]["gen"], "house.json"))); w_, d_ = hj["size"]
    stand = next(b for b in FIX["buildings"] if b["id"] == K["tip"]["stand"])
    t = math.radians(stand["turn"]); ex, ey = Vector((math.cos(t), math.sin(t), 0)), Vector((-math.sin(t), math.cos(t), 0))
    corner = Vector((stand["at"][0], stand["at"][1], stand["base"])) - ex * (w_ / 2) - ey * (d_ / 2)
    M = Matrix.Translation(corner) @ Matrix.Rotation(t, 4, "Z")
    before = set(bpy.data.objects); out = []
    bpy.ops.import_scene.fbx(filepath=os.path.join(ROOT, K["beside"]["gen"], "house-near.fbx"))
    for o in set(bpy.data.objects) - before:
        if o.type == "MESH":
            o.matrix_world = M @ o.matrix_world; o.data.materials.clear(); o.data.materials.append(mat); out.append(o)
    zl = float(lowered(np.array([[stand["at"][0]]]), np.array([[stand["at"][1]]]))[0, 0])
    bpy.ops.mesh.primitive_cube_add(size=1)
    p = bpy.context.active_object; p.name = "plinth"
    p.scale = (w_ + 0.2, d_ + 0.2, stand["base"] - zl + 0.3); p.rotation_euler = (0, 0, t)
    p.location = (stand["at"][0], stand["at"][1], (stand["base"] + zl - 0.3) / 2); p.data.materials.clear(); p.data.materials.append(mat)
    return out + [p]


def views():
    V = {n: dict(v) for n, v in K["shore"]["lone"]["views"].items() if n in ("loneeye", "lone12", "lonesea")}
    V["lone12"].update(B["view12"])  # wider, to hold the whole block
    b, out, up = B["leeView"]; tg = Vector(V["lone12"]["target"])
    V["lee"] = {"pos": list(tg + Vector((math.sin(math.radians(b)) * out, math.cos(math.radians(b)) * out, up))),
                "target": list(tg + Vector((0, 0, 0.3))), "fov": 45}
    V["water"] = dict(K["tip"]["views"]["water"])
    return V


def camera(cam, v):
    cam.location = Vector(v["pos"]); cam.rotation_euler = (Vector(v["target"]) - Vector(v["pos"])).to_track_quat("-Z", "Y").to_euler()
    cam.data.sensor_fit = "VERTICAL"; cam.data.angle = math.radians(v["fov"]); cam.data.clip_start = 0.05; cam.data.clip_end = 2000


# ---------------------------------------------------------------- step 1: silhouettes, section and plan
def silhouettes(subjects, frame):
    sc = bpy.context.scene; sl = B["silhouette"]
    sc.render.engine = "BLENDER_WORKBENCH"; sc.display.shading.light = "FLAT"; sc.display.shading.color_type = "MATERIAL"
    sc.render.resolution_x, sc.render.resolution_y = 1280, 720; sc.view_settings.view_transform = "Standard"
    wo = bpy.data.worlds.new("w"); sc.world = wo; wo.color = (sl["sky"],) * 3
    cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam")); sc.collection.objects.link(cam); sc.camera = cam
    for n, v in views().items():
        camera(cam, v)
        for tag, ob in subjects.items():
            for o in subjects.values():
                o.hide_render = o is not ob
            sc.render.filepath = os.path.join(OUT, f"sil-{tag}-{n}.png"); bpy.ops.render.render(write_still=True)


def outline(P):
    """A rock's long section (its top over s, seen across the ice) and its plan at mean sea level (t over s each side)."""
    s = (P[:, :2] - C0) @ E; t = (P[:, :2] - C0) @ W; z = P[:, 2]
    bins = np.arange(-14.0, 9.0, 0.1); i = np.digitize(s, bins)
    top = np.full(len(bins), np.nan); lo = top.copy(); hi = top.copy()
    np.fmax.at(top, i.clip(0, len(bins) - 1), z)
    m = z > 0; lo_ = np.full(len(bins), np.inf); hi_ = np.full(len(bins), -np.inf)
    np.minimum.at(lo_, i[m].clip(0, len(bins) - 1), t[m]); np.maximum.at(hi_, i[m].clip(0, len(bins) - 1), t[m])
    lo[np.isfinite(lo_)] = lo_[np.isfinite(lo_)]; hi[np.isfinite(hi_)] = hi_[np.isfinite(hi_)]
    return bins - 0.05, top, lo, hi


def points(ob):
    dg = bpy.context.evaluated_depsgraph_get(); me = ob.evaluated_get(dg).to_mesh()
    V = np.empty(len(me.vertices) * 3); me.vertices.foreach_get("co", V)
    M = np.array(ob.matrix_world); P = V.reshape(-1, 3) @ M[:3, :3].T + M[:3, 3]
    ob.evaluated_get(dg).to_mesh_clear()
    return P


def drawing(subjects, path):
    """The long section (top) and the plan at mean sea level (bottom) of each subject, 50 px a metre, drawn in numpy:
    r02 black, t09 red, t13 blue; the sea level and the crest's s grey; a tick every metre."""
    px, s0, s1 = 50, -14.0, 9.0; Wd = int((s1 - s0) * px); Hs, Hp = int(5 * px), int(16 * px)
    img = np.ones((Hs + Hp + 20, Wd, 4))
    col = {"r02": (0, 0, 0), "t09": (0.85, 0.1, 0.05), "t13": (0.1, 0.3, 0.9)}

    def put(x, y, c, r=1):
        x = np.asarray(x); y = np.asarray(y); ok = np.isfinite(x) & np.isfinite(y)
        xi = ((x[ok] - s0) * px).astype(int); yi = y[ok].astype(int)
        for dx in range(-r, r + 1):
            for dy in range(-r, r + 1):
                k = (xi + dx >= 0) & (xi + dx < Wd) & (yi + dy >= 0) & (yi + dy < img.shape[0])
                img[yi[k] + dy, xi[k] + dx, :3] = c

    ys = lambda z: Hp + 20 + (z + 1.0) * px  # noqa: E731  section: z -1 .. 4 (row 0 is the image's bottom)
    yp = lambda t: Hp / 2 - t * px  # noqa: E731  plan: t -8 .. 8, the sea (t < 0) at the top
    xs = np.arange(s0, s1, 0.01)
    put(xs, np.full_like(xs, ys(0.0)), (0.6, 0.6, 0.6), 0); put(xs, np.full_like(xs, yp(0.0)), (0.8, 0.8, 0.8), 0)
    for m in np.arange(np.ceil(s0), s1):
        put(np.full(20, m), np.linspace(ys(-1.0), ys(-0.8), 20), (0.5, 0.5, 0.5), 0)
    put(np.zeros(200), np.linspace(0, img.shape[0] - 1, 200), (0.75, 0.75, 0.75), 0)
    for tag, ob in subjects.items():
        b, top, lo, hi = outline(points(ob))
        put(b, ys(top), col[tag]); put(b, yp(lo), col[tag]); put(b, yp(hi), col[tag])
    o = bpy.data.images.new("drawing", Wd, img.shape[0], alpha=False); o.pixels = img.ravel()
    o.filepath_raw = path; o.file_format = "PNG"; o.save()


def measure(ob, shown=False):
    """Lengths at mean sea level, or (shown) of what stands above both the sea and the designed ground."""
    P = points(ob); s = (P[:, :2] - C0) @ E; t = (P[:, :2] - C0) @ W; z = P[:, 2]
    m = z > (np.maximum(0, lowered(P[:, :1], P[:, 1:2])[:, 0]) + 0.02 if shown else 0)
    k = np.argmax(z)
    return {"crest": round(float(z[k]), 2), "crestS": round(float(s[k]), 2), "alongAtSea": round(float(np.ptp(s[m])), 2),
            "acrossAtSea": round(float(np.ptp(t[m])), 2), "stossToe": round(float(s[m].min()), 2), "leeToe": round(float(s[m].max()), 2),
            "seaward": round(float(t[m].min()), 2), "landward": round(float(t[m].max()), 2),
            "crestShare": round(float((s[k] - s[m].min()) / np.ptp(s[m])), 2)}


# ---------------------------------------------------------------- step 2: the near level and the grey check
def evaluated(ob, mod):
    """`ob` with modifier `mod` applied."""
    dg = bpy.context.evaluated_depsgraph_get(); me = bpy.data.meshes.new_from_object(ob.evaluated_get(dg))
    old = ob.data; ob.modifiers.remove(mod); ob.data = me; bpy.data.meshes.remove(old)
    return ob


def near_level(ob):
    """The near level: faces `trimM` under the sea's or the ground's cover dropped; planar faces dissolved; collapsed to
    the street's near budget a square metre (street.json levels.near over budgetSurfaceM2) for the surface left; normals
    weighted by face area. No bevel: the rounds are the body's own."""
    import bmesh
    ST = json.load(open(os.path.join(ROOT, "blender", "parts", "street", "street.json")))
    per = np.mean(ST["levels"]["near"]["budgetTris"]) / ST["budgetSurfaceM2"]["m2"]
    bm = bmesh.new(); bm.from_mesh(ob.data)
    V = np.array([v.co for v in bm.verts]); cover = np.maximum(lowered(V[:, :1], V[:, 1:2])[:, 0], -0.6) - B["trimM"]
    low = V[:, 2] < cover; bm.verts.ensure_lookup_table()
    bmesh.ops.delete(bm, geom=[f for f in bm.faces if all(low[v.index] for v in f.verts)], context="FACES")
    area = sum(f.calc_area() for f in bm.faces); bm.to_mesh(ob.data); bm.free()
    m = ob.modifiers.new("planar", "DECIMATE"); m.decimate_type = "DISSOLVE"; m.angle_limit = math.radians(0.5); evaluated(ob, m)
    m = ob.modifiers.new("tri", "TRIANGULATE"); evaluated(ob, m)
    target = per * area; n0 = len(ob.data.polygons)
    m = ob.modifiers.new("collapse", "DECIMATE"); m.ratio = min(1.0, target / n0); evaluated(ob, m)
    for f in ob.data.polygons:
        f.use_smooth = True
    m = ob.modifiers.new("weighted", "WEIGHTED_NORMAL"); m.mode = "FACE_AREA"; m.weight = 50; m.keep_sharp = True
    return {"areaM2": round(area, 1), "budget": int(target), "voxelTris": n0, "tris": len(ob.data.polygons)}


def clay(name, v, rough):
    m = bpy.data.materials.new(name); m.use_nodes = True; b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (v, v, v, 1); b.inputs["Roughness"].default_value = rough
    return m


def shoot(V, tag):
    """The kit's grey check (design.py's): Eevee, a neutral sun (az 330, el 35) and a raking one (az 255, el 7)."""
    sc = bpy.context.scene
    sc.render.engine = "BLENDER_EEVEE"; sc.render.resolution_x, sc.render.resolution_y = 1280, 720
    sc.view_settings.view_transform = "AgX"
    wo = bpy.data.worlds.new("w"); sc.world = wo; wo.use_nodes = True
    bg = wo.node_tree.nodes["Background"]; bg.inputs[0].default_value = (0.8, 0.8, 0.8, 1); bg.inputs[1].default_value = 0.6
    sun = bpy.data.objects.new("sun", bpy.data.lights.new("sun", "SUN")); sc.collection.objects.link(sun); sun.data.angle = math.radians(3)
    cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam")); sc.collection.objects.link(cam); sc.camera = cam
    for n, v in V.items():
        camera(cam, v)
        for light, (az, el, en) in {"neutral": (330, 35, 3.0), "raking": (255, 7, 4.5)}.items():
            az, el = math.radians(az), math.radians(el)
            dv = Vector((math.sin(az) * math.cos(el), math.cos(az) * math.cos(el), math.sin(el)))
            sun.rotation_euler = (-dv).to_track_quat("-Z", "Y").to_euler(); sun.data.energy = en
            sc.render.filepath = os.path.join(OUT, f"{tag}-{n}-{light}.png"); bpy.ops.render.render(write_still=True)


def step2():
    G = B["grey"]; rock = clay("rock", G["rock"], G["rough"])
    fit_bounds(); info = spikes()
    print("[body] spikes", json.dumps(info))
    ob = mesh("r02", rock, float(arg("--fine", B["fineM"]))); info.update(near_level(ob)); info.update(measure(ob, True))
    print("[body]", json.dumps({k: v for k, v in info.items() if k != "spikes"}))
    json.dump(info, open(os.path.join(OUT, "body.json"), "w"), indent=1)
    water = bpy.data.meshes.new("water"); water.from_pydata([(-400, -400, 0), (400, -400, 0), (400, 400, 0), (-400, 400, 0)], [], [(0, 1, 2, 3)])
    wm = bpy.data.materials.new("water"); wm.use_nodes = True; bs = wm.node_tree.nodes["Principled BSDF"]
    bs.inputs["Base Color"].default_value = (0.05, 0.055, 0.06, 1); bs.inputs["Roughness"].default_value = 0.3
    water.materials.append(wm); bpy.context.scene.collection.objects.link(bpy.data.objects.new("water", water))
    land(clay("ground", G["ground"], 0.92)); house(clay("house", G["house"], 0.7))
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "r02.blend"))
    shoot(views(), "r02")


def main():
    os.makedirs(OUT, exist_ok=True)
    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o)
    if arg("--step", "1") == "2":
        return step2()
    sl = B["silhouette"]; rock = flat("rock", sl["rock"])
    subjects = {"r02": mesh("r02", rock),
                "t09": append(os.path.join(ROOT, "cache", "rock", "kit", "gen", "carve", "W.blend"), "W-high", rock),
                "t13": append(os.path.join(ROOT, "cache", "rock", "kit", "renders", "t13", "r3", "scan.blend"), "scan", rock)}
    sea = bpy.data.meshes.new("sea"); sea.from_pydata([(-400, -400, 0), (400, -400, 0), (400, 400, 0), (-400, 400, 0)], [], [(0, 1, 2, 3)])
    sea.materials.append(flat("sea", sl["sea"])); bpy.context.scene.collection.objects.link(bpy.data.objects.new("sea", sea))
    frame = [land(flat("land", sl["land"]))] + house(flat("house", sl["house"]))
    info = {k: measure(o) for k, o in subjects.items()}
    info.update({k + "shown": measure(o, True) for k, o in subjects.items()})
    info["r02"]["tris"] = len(subjects["r02"].data.polygons)
    print("[body]", json.dumps(info))
    json.dump(info, open(os.path.join(OUT, "body.json"), "w"), indent=1)
    drawing(subjects, os.path.join(OUT, "drawing.png"))
    silhouettes(subjects, frame)
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "r02.blend"))


if __name__ == "__main__":
    main()
