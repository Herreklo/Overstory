"""r01: the Holm tip's shore block designed as a sculptor would (kit.json `design`), in the kit's grey check.

The record constrains it (the crest at the record's back over t09's crest, the ice's way, t09's seaward waterline,
107 where it stands); the form is drawn: section lines out from the crest, each segment one plane facing its way, the
planes' intersection one faceted mass; a few broad foliation steps on the seaward flank; two deep joints, J1 along the
back and J2 across it, as real gaps; the plucked lee in three big blocks; the arrises softened by a bevel weighted by
what each face is. Round it: the record's landform lowered near the block, turf over the soil line with its edge
rolled over, a cut bank of till under that edge, the pack's tufts, and a few loose stones at the foot. Then Eevee, one
neutral sun (az 330, el 35) and one raking (az 255, el 7), t09's views (eye, 12 m, sea), a lee view and the tip's
water frame with 107.

    Blender -b --factory-startup -P design.py -- --out DIR
"""
import json, math, os, sys

import bmesh
import bpy
import numpy as np
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path[:0] = [HERE, os.path.dirname(HERE), os.path.join(ROOT, "blender", "resolver"),
                os.path.join(ROOT, "blender", "generators"), os.path.join(ROOT, "blender", "parts", "growth")]
import blockin as BI  # noqa: E402
import outcrop  # noqa: E402
import hashing as HS  # noqa: E402
import growth  # noqa: E402
import tufts as TU  # noqa: E402


def arg(n, d=None):
    a = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    return a[a.index(n) + 1] if n in a else d


K = json.load(open(os.path.join(HERE, "kit.json")))
D = K["design"]
FIX = BI.FIX
OUT = os.path.abspath(arg("--out", os.path.join(ROOT, "cache", "rock", "kit", "renders", "r01")))
SEED = json.load(open(os.path.join(ROOT, "packs", "stavanger-1989", "pack.json")))["worldSeed"]
LF = outcrop.Landform(FIX["outcrop"]["landform"])
BANDS = K["tip"]["grey"]["bands"]
MHWS = FIX["sea"]["meanLevel"] + FIX["sea"]["springRange"] / 2
A = math.radians(FIX["rock"]["ice"]["toward"])
E = np.array([math.sin(A), math.cos(A)])  # down-ice, s
W = np.array([-math.cos(A), math.sin(A)])  # landward, t
C0 = np.array(D["crestAt"], float)


def site(s, t):
    return C0 + E * s + W * t


def way(b):
    b = math.radians(b)
    return np.array([math.sin(b), math.cos(b)])


# ---------------------------------------------------------------- planes: (n, d, kind), the rock where n.p <= d
def facing_plane(face, slope, p):
    """A plane facing bearing `face`, `slope` degrees from level, through the site point p (x, y, z)."""
    a = math.radians(slope); h = way(face) * math.sin(a)
    n = np.array([h[0], h[1], math.cos(a)])
    return n, float(n @ np.asarray(p, float))


def ice_point(s, t, z):
    x, y = site(s, t)
    return np.array([x, y, z])


def plane(spec, dz=0.0):
    """[facing, slope, [s, t, z], kind]: the plane, lowered dz."""
    n, d = facing_plane(spec[0], spec[1], ice_point(*spec[2]))
    return n, d - n[2] * dz, spec[3]


def section_planes():
    """The back's section lines as planes: each segment of a profile [out, height] from the crest one plane facing its
    section's bearing, named section.index."""
    out = {}
    for name, (face, pts) in D["sections"].items():
        for i, ((r0, z0), (r1, z1)) in enumerate(zip(pts[:-1], pts[1:])):
            out[f"{name}.{i}"] = [face, math.degrees(math.atan2(z0 - z1, r1 - r0)), [*(np.array([r0 * math.cos(math.radians(face - FIX["rock"]["ice"]["toward"])), r0 * math.cos(math.radians(face - FIX["rock"]["ice"]["toward"] + 90))])), z0], "ice"]
    return out


def expand(tokens):
    """`*` all the section planes, `*s` section s's, `*s@dz` those lowered dz; other names as they are."""
    out = []
    for r in tokens:
        if r.startswith("*"):
            name, _, dz = r[1:].partition("@")
            out += [k + (f"@{dz}" if dz else "") for k in SECTIONS if not name or k.split(".")[0] == name]
        else:
            out.append(r)
    return out


def ref(r, risers, drop=0.0, drops=()):
    """A plane by name (or a lee block's riser by its id): `~p` its far side, 4 cm into it; `J<` and `J>` a joint's near
    and far side, its gap between; `p@dz` lowered dz; the `drops` planes lowered `drop` more."""
    far = r.startswith("~"); r = r.lstrip("~"); dz = 0.0
    if "@" in r:
        r, z = r.split("@"); dz = float(z)
    side = r[-1] if r[-1] in "<>" else None; r = r.rstrip("<>")
    dz += drop if (r in drops or r.split(".")[0] in drops) else 0.0
    if r in risers:
        n, d, kind = risers[r]; d -= n[2] * dz; gap = 0.0
    else:
        spec = PLANES[r]; n, d, kind = plane(spec, dz); gap = spec[4] if len(spec) > 4 else 0.0
    if side == "<":
        d -= gap / 2
    elif side == ">":
        n, d = -n, -d - gap / 2
    if far:
        n, d = -n, -d + 0.04
    return n, d, kind


FOOT = (np.array([0, 0, -1.0]), -D["footM"], "foot")
SECTIONS = section_planes()
PLANES = {**D["planes"], **SECTIONS}


# ---------------------------------------------------------------- pieces
def convex(name, planes, mat):
    """The convex block the planes bound, or None."""
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=80.0)
    bmesh.ops.translate(bm, verts=bm.verts, vec=Vector((C0[0], C0[1], 0.0)))
    for n, d, _ in planes:
        if not bm.faces:
            break
        bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], dist=1e-6, plane_co=Vector(n * d), plane_no=Vector(n), clear_outer=True)
        edges = [e for e in bm.edges if e.is_boundary]
        if edges:
            bmesh.ops.holes_fill(bm, edges=edges, sides=0)
    if len(bm.faces) < 4:
        bm.free(); return None
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    me.materials.append(mat)
    ob = bpy.data.objects.new(name, me); bpy.context.scene.collection.objects.link(ob)
    return ob


def union(name, obs, mat):
    """One mass from overlapping convex blocks (an exact boolean union)."""
    obs = [o for o in obs if o is not None]
    if not obs:
        return None
    base = obs[0]
    for o in obs[1:]:
        m = base.modifiers.new("u", "BOOLEAN"); m.operation = "UNION"; m.object = o; m.solver = "EXACT"
        dg = bpy.context.evaluated_depsgraph_get()
        me = bpy.data.meshes.new_from_object(base.evaluated_get(dg))
        base.modifiers.clear(); old = base.data; base.data = me; bpy.data.meshes.remove(old)
        bpy.data.objects.remove(o)
    base.name = name
    clean(base.data)
    base.data.materials.clear(); base.data.materials.append(mat)
    return base


def clean(me):
    """The boolean's slivers gone: near vertices merged, degenerate edges and faces dissolved, coplanar faces made one."""
    bm = bmesh.new(); bm.from_mesh(me)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=2e-3)
    bmesh.ops.dissolve_degenerate(bm, edges=bm.edges, dist=2e-3)
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context="VERTS")
    bmesh.ops.dissolve_limit(bm, angle_limit=math.radians(1.0), verts=bm.verts, edges=bm.edges)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(me); bm.free()


def soften(ob, slices, soft=1.0):
    """The arrises softened: each face takes the kind of the plane it lies on; an edge's bevel the geometric mean of its
    two faces' weights by kind (the ice's planes worn most, the joints and plucked risers crispest), none at the foot."""
    bv = D["bevel"]; wt = dict(bv["weights"], foot=0.0); me = ob.data; planes = [p for P in slices for p in P]
    N = np.array([p[0] for p in planes]); Dd = np.array([p[1] for p in planes])
    fw = []
    for p in me.polygons:
        ok = (N @ np.array(p.normal) > 0.995) & (np.abs(N @ np.array(p.center) - Dd) < 0.03)
        fw.append(wt[planes[int(np.argmax(ok))][2]] if ok.any() else 1.0)
    ew = {}
    for p, w_ in zip(me.polygons, fw):
        for ek in p.edge_keys:
            ew.setdefault(ek, []).append(w_)
    at = me.attributes.get("bevel_weight_edge") or me.attributes.new("bevel_weight_edge", "FLOAT", "EDGE")
    at.data.foreach_set("value", [math.sqrt(v[0] * v[1]) if len(v) == 2 else 0.0 for v in (ew.get(tuple(sorted(e.vertices)), [0]) for e in me.edges)])
    m = ob.modifiers.new("soft", "BEVEL"); m.width = bv["widthM"] * soft; m.segments = bv["segments"]; m.limit_method = "WEIGHT"
    m.profile = 0.5; m.use_clamp_overlap = True; m.harden_normals = True; m.miter_outer = "MITER_ARC"
    for p in me.polygons:
        p.use_smooth = True


def rock(mat):
    """The back's pieces (each its listed planes, parted by the joints' gaps, the sea flank's stepped by the foliation),
    then the lee's blocks; every piece one rigid mass."""
    st = D["steps"]; Fs = [plane([st["face"], st["slope"], c["at"], "step"]) for c in st["list"]]
    parts, used = [], {}
    for pc in D["back"]:
        cuts = Fs if pc.get("steps") else []; blocks, every, drop = [], [], 0.0
        for k in range(len(cuts) + 1):
            P = [ref(r, {}, drop, st["drops"]) for r in expand(pc["planes"])] + [FOOT]
            if k < len(cuts):
                P.append(cuts[k])
            if k > 0:
                n, d, kind = cuts[k - 1]; P.append((-n, -d + 0.03, kind))
            blocks.append(convex(f"{pc['id']}-{k}", P, mat)); every.append(P)
            if k < len(cuts):
                drop += st["list"][k]["dropM"]
        u = union(pc["id"], blocks, mat)
        if u is not None:
            parts.append(u); used[u.name] = (every, pc.get("soft", 1.0))
    risers = {}
    for L in D["lee"]:
        P = [ref(r, risers) for r in expand(L["planes"])] + [plane(L["tread"]), plane(L["riser"])] + [plane(x) for x in L.get("sides", [])] + [FOOT]
        risers[L["id"]] = plane(L["riser"])
        ob = convex(L["id"], P, mat)
        if ob is not None:
            clean(ob.data); parts.append(ob); used[ob.name] = ([P], L.get("soft", 1.0))
    for o in parts:
        soften(o, *used[o.name])
    lift = D["crestM"] - max(float(evaluated_points([o])[:, 2].max()) for o in parts)  # the crest the record's, the whole moved
    for o in parts:
        o.location.z += lift
    return parts


# ---------------------------------------------------------------- the ground (as t14's trial, by the record's bands)
def ground(X, Y):
    L = LF.smooth(X.ravel(), Y.ravel()).reshape(X.shape)
    t = np.clip((np.hypot(X - C0[0], Y - C0[1]) - D["lowerNearM"]) / (D["lowerFarM"] - D["lowerNearM"]), 0, 1)
    return L - D["lowerM"] * (1 - t * t * (3 - 2 * t))


def noise(key, x, y, scale):
    """growth._value_noise, its lattice drawn once."""
    gx, gy = np.asarray(x, float) / scale, np.asarray(y, float) / scale
    ix, iy = np.floor(gx).astype(np.int64), np.floor(gy).astype(np.int64)
    fx, fy = gx - ix, gy - iy
    fx, fy = fx * fx * (3 - 2 * fx), fy * fy * (3 - 2 * fy)
    ox, oy = ix.min(), iy.min()
    tab = np.array([[HS.unit(HS.h(*key, int(a), int(b))) for b in range(oy, iy.max() + 2)] for a in range(ox, ix.max() + 2)])
    at = lambda i, j: tab[i - ox, j - oy]  # noqa: E731
    return (at(ix, iy) * (1 - fx) + at(ix + 1, iy) * fx) * (1 - fy) + (at(ix, iy + 1) * (1 - fx) + at(ix + 1, iy + 1) * fx) * fy


def exposure(b):
    """The record's compass weights (outcrop.exposure), read for ground facing bearing b (radians)."""
    e = FIX["sea"]["exposure"]; deg = np.degrees(b) % 360
    ways = [(0, e["north"]), (90, e["east"]), (180, e["south"]), (270, e["west"]), (360, e["north"])]
    out = np.zeros_like(deg)
    for (b0, w0), (b1, w1) in zip(ways, ways[1:]):
        m = (deg >= b0) & (deg <= b1); out[m] = w0 + (w1 - w0) * (deg[m] - b0) / 90
    return out


def soil_line(b):
    """The soil's lowest height over ground facing b: the storm top (tip.grey bands) and soilM over it."""
    return MHWS + BANDS["surgeM"] + BANDS["runupM"] * exposure(b) + BANDS["soilM"]


def blur(Z, r, cs):
    k = max(1, int(round(r / cs))); out = Z.copy()
    for ax in (0, 1):
        c = np.cumsum(np.pad(out, [(k + 1, k) if a == ax else (0, 0) for a in (0, 1)], mode="edge"), axis=ax)
        out = (np.take(c, np.arange(2 * k + 1, c.shape[ax]), axis=ax) - np.take(c, np.arange(0, c.shape[ax] - 2 * k - 1), axis=ax)) / (2 * k + 1)
    return out


def facing(Z, cs):
    gx, gy = np.gradient(Z, cs)
    return np.arctan2(-gx, -gy)


def dist_in(M, cs, most):
    """Each node's distance to the nearest node outside M (0 outside), to `most`."""
    d = np.where(M, np.inf, 0.0); r2 = cs * math.sqrt(2)
    for _ in range(int(most / cs) + 2):
        for di, dj, w_ in ((1, 0, cs), (-1, 0, cs), (0, 1, cs), (0, -1, cs), (1, 1, r2), (1, -1, r2), (-1, 1, r2), (-1, -1, r2)):
            sh = np.full_like(d, np.inf)
            sh[max(di, 0):d.shape[0] + min(di, 0), max(dj, 0):d.shape[1] + min(dj, 0)] = \
                d[max(-di, 0):d.shape[0] + min(-di, 0), max(-dj, 0):d.shape[1] + min(-dj, 0)]
            d = np.minimum(d, sh + w_)
    return np.minimum(d, most)


def quads(M):
    return M[:-1, :-1] | M[1:, :-1] | M[1:, 1:] | M[:-1, 1:]


def grid_mesh(name, X, Y, Z, keep, mats, face_mat=None):
    nx, ny = X.shape; idx = np.arange(nx * ny).reshape(nx, ny)
    q = np.stack([idx[:-1, :-1], idx[1:, :-1], idx[1:, 1:], idx[:-1, 1:]], -1)[keep]
    used, inv = np.unique(q, return_inverse=True)
    P = np.stack([X.ravel(), Y.ravel(), Z.ravel()], 1)[used]
    me = bpy.data.meshes.new(name); me.from_pydata(P.tolist(), [], inv.reshape(-1, 4).tolist())
    for m in mats:
        me.materials.append(m)
    if face_mat is not None:
        me.polygons.foreach_set("material_index", face_mat.astype(np.int32))
    ob = bpy.data.objects.new(name, me); bpy.context.scene.collection.objects.link(ob)
    return ob


def evaluated_points(obs):
    dg = bpy.context.evaluated_depsgraph_get(); out = []
    for o in obs:
        me = o.evaluated_get(dg).to_mesh()
        V = np.empty(len(me.vertices) * 3); me.vertices.foreach_get("co", V)
        Mw = np.array(o.matrix_world); out.append(V.reshape(-1, 3) @ Mw[:3, :3].T + Mw[:3, 3])
        o.evaluated_get(dg).to_mesh_clear()
    return np.concatenate(out)


def turn(yaw, axis=None, tilt=0.0):
    R = Matrix.Rotation(yaw, 3, "Z")
    if axis is not None and tilt:
        R = Matrix.Rotation(tilt, 3, Vector(axis)) @ R
    return np.array(R)


def soup(name, parts, mat):
    P, F, o = [], [], 0
    for p, f in parts:
        P.append(p); F.append(f + o); o += len(p)
    me = bpy.data.meshes.new(name); me.from_pydata(np.concatenate(P).tolist(), [], np.concatenate(F).tolist())
    me.materials.append(mat)
    ob = bpy.data.objects.new(name, me); bpy.context.scene.collection.objects.link(ob)
    return ob


def land(rock_parts, mats):
    info = {}
    cs, H = D["cellM"], D["nearHalfM"]
    xs = np.arange(C0[0] - H, C0[0] + H + 1e-6, cs); ys = np.arange(C0[1] - H, C0[1] + H + 1e-6, cs)
    X, Y = np.meshgrid(xs, ys, indexing="ij"); nx, ny = X.shape
    G = ground(X, Y)
    V = evaluated_points(rock_parts)
    ij = np.round((V[:, :2] - [xs[0], ys[0]]) / cs).astype(int)
    ok = (ij[:, 0] >= 0) & (ij[:, 0] < nx) & (ij[:, 1] >= 0) & (ij[:, 1] < ny)
    R = np.full((nx, ny), -np.inf); np.maximum.at(R, (ij[ok, 0], ij[ok, 1]), V[ok, 2])
    # big flat faces leave nodes no vertex fell on: a node takes the rock top by a ray from above
    dg = bpy.context.evaluated_depsgraph_get()
    inside = np.zeros_like(R, bool)
    lo, hi = V[:, :2].min(0), V[:, :2].max(0)
    box = (X >= lo[0]) & (X <= hi[0]) & (Y >= lo[1]) & (Y <= hi[1])
    sc = bpy.context.scene; names = {o.name for o in rock_parts}
    for a, b_ in zip(*np.nonzero(box)):
        hit, loc, _, _, ob, _ = sc.ray_cast(dg, Vector((X[a, b_], Y[a, b_], 10.0)), Vector((0, 0, -1)))
        if hit and ob.name in names and loc.z > D["footM"] + 0.01:
            R[a, b_] = max(R[a, b_], loc.z); inside[a, b_] = True
    Gs = blur(G, 1.0, cs)
    SL = soil_line(facing(Gs, cs))
    M = (G > R + 0.02) & (G > SL)
    d = dist_in(M, cs, D["lipM"] + cs)
    u = np.maximum(SL - G, 0.0); b = D["bankM"] / D["bankSteep"]
    Gb = np.where(G > SL, G, np.where(u <= b, G - u * (D["bankSteep"] - 1), G - (D["bankM"] - b)))
    rockTop = R > Gb + 0.02
    dd = np.clip((d - 0.5 * cs) / D["lipM"], 0, 1)
    Zt = np.where(M, G + D["turfM"] * np.sqrt(1 - (1 - dd) ** 2), Gb - 0.06)
    grid_mesh("turf", X, Y, Zt, quads(M), [mats["turf"]])
    under = M & (d >= D["lipM"])
    grid_mesh("till", X, Y, Gb, quads(~under & (Gb > -1.5)), [mats["till"]])
    info["turfSqm"] = round(float(M.sum() * cs * cs), 1)
    fc = D["farCellM"]; x0, x1, y0, y1 = K["scan"]["landRegion"]
    FX, FY = np.meshgrid(np.arange(x0, x1 + 1e-6, fc), np.arange(y0, y1 + 1e-6, fc), indexing="ij")
    FG = ground(FX, FY); FS = soil_line(facing(blur(FG, 1.0, fc), fc))
    cx, cy = (FX[:-1, :-1] + FX[1:, 1:]) / 2, (FY[:-1, :-1] + FY[1:, 1:]) / 2
    inner = (np.abs(cx - C0[0]) < H - fc) & (np.abs(cy - C0[1]) < H - fc)
    keepF = quads(FG > -0.5) & ~inner
    up = ((FG - FS)[:-1, :-1] + (FG - FS)[1:, 1:]) > 0
    grid_mesh("land", FX, FY, FG - 0.03, keepF, [mats["till"], mats["turf"]], up[keepF].astype(int))
    return dict(X=X, Y=Y, G=G, Gb=Gb, R=R, M=M, d=d, Zt=Zt, SL=SL, rockTop=rockTop, cs=cs, xs=xs, ys=ys, info=info)


def growth_on(g, mats):
    """The pack's tufts: a fringe along the turf's lip, the heath on its mat, and in the joints and on the lee's treads
    above the soil line."""
    T = growth.pack()["tufts"]; TM = {}
    for name, spec in T["species"].items():
        for v in range(4):
            tris = TU.mesh(TU.blades(spec, name, v, SEED), spec, 0)
            P = np.array([vt[0] for t in tris for vt in t], float)
            TM[name, v] = (P, np.arange(len(P)).reshape(-1, 3))
    X, Y, d, Zt, cs, xs, ys = g["X"], g["Y"], g["d"], g["Zt"], g["cs"], g["xs"], g["ys"]
    nx, ny = X.shape; parts = []; count = {"heath": 0, "fringe": 0, "joints": 0}

    def put(species, v, at, yaw, axis=None, tilt=0.0):
        P, F = TM[species, v]; parts.append((P @ turn(yaw, axis, tilt).T + at, F))

    def node(p):
        a, b_ = int(round((p[0] - xs[0]) / cs)), int(round((p[1] - ys[0]) / cs))
        return (a, b_) if (0 <= a < nx and 0 <= b_ < ny) else None

    hab = T["habitats"]["heath"]; step = 1 / math.sqrt(hab["perSqm"])
    mix = [(k, int(round(w_ * 1000))) for k, w_ in hab["mix"].items()]
    lx, ly = np.meshgrid(np.arange(xs[0], xs[-1], step), np.arange(ys[0], ys[-1], step), indexing="ij")
    cn = noise(("r01 heath clump",), lx, ly, hab["clump"][0])
    keep = (1.0 - hab["clump"][1]) + hab["clump"][1] * np.clip((cn - 0.3) / 0.4, 0.0, 1.0)
    for (i, j), k in np.ndenumerate(keep):
        Sd = HS.Stream(SEED, "r01 heath", i, j)
        p = np.array([lx[i, j] + Sd.random() * step, ly[i, j] + Sd.random() * step])
        q = node(p)
        if Sd.random() > k or q is None or np.hypot(*(p - C0)) > D["heathWithinM"] or not g["M"][q] or d[q] < D["lipM"]:
            continue
        put(Sd.weighted(mix), Sd.randrange(4), [p[0], p[1], Zt[q] - 0.02], Sd.uniform(0, 2 * math.pi)); count["heath"] += 1
    gx, gy = np.gradient(d, cs); fr = D["fringe"]
    for a, b_ in zip(*np.nonzero((d > 0) & (d <= cs * 1.5))):
        Sd = HS.Stream(SEED, "r01 fringe", int(a), int(b_))
        if Sd.random() > cs / fr["stepM"]:
            continue
        o = -np.array([gx[a, b_], gy[a, b_]]); o = o / max(np.linalg.norm(o), 1e-9)
        put(fr["species"], Sd.randrange(4), [X[a, b_], Y[a, b_], Zt[a, b_] - 0.02], Sd.uniform(0, 2 * math.pi),
            (-o[1], o[0], 0.0), math.radians(Sd.uniform(*fr["leanOut"]))); count["fringe"] += 1
    # in the joints' gaps, and along the foot of each lee riser on the tread below it
    jt = D["joint"]; jmix = [(k, int(w_)) for k, w_ in jt["species"].items()]
    R = g["R"]; Rb = blur(np.where(np.isfinite(R), R, g["Gb"]), 1.0, cs); RF = facing(Rb, cs)
    lines = []
    for name in ("J1", "J2"):
        spec = D["planes"][name]; n, d, _ = plane(spec); h = n[:2] / np.linalg.norm(n[:2]); along = np.array([-h[1], h[0]])
        p0 = site(*spec[2][:2]); lines += [(p0 + along * r, h * (spec[4] / 2 + 0.12), None) for r in np.arange(-14, 14, jt["stepM"])]
    prev = plane(PLANES["lip"])
    for L in D["lee"]:
        tr = plane(L["tread"]); A = np.array([prev[0], tr[0]]); c = np.array([C0[0], C0[1], 2.0])
        x0 = c + np.linalg.pinv(A) @ (np.array([prev[1], tr[1]]) - A @ c); u = np.cross(prev[0], tr[0]); u /= np.linalg.norm(u)
        h = prev[0][:2] / np.linalg.norm(prev[0][:2])
        lines += [((x0 + u * r)[:2] + h * 0.22, None, tr) for r in np.arange(-6, 6, jt["stepM"])]
        prev = plane(L["riser"])
    for i, (p, off, tr) in enumerate(lines):
        q = node(p)
        if q is None or not np.isfinite(R[q]) or not g["rockTop"][q]:
            continue
        if off is not None:
            q1, q2 = node(p + off), node(p - off)
            if q1 is None or q2 is None or not (np.isfinite(R[q1]) and np.isfinite(R[q2])):
                continue
            z = min(R[q1], R[q2]) - 0.08
        else:
            z = (tr[1] - tr[0][0] * p[0] - tr[0][1] * p[1]) / tr[0][2]
            if abs(R[q] - z) > 0.2:
                continue
            z = R[q] - 0.04
        if z < soil_line(np.array([RF[q]]))[0]:
            continue
        Sd = HS.Stream(SEED, "r01 joint", i)
        if Sd.random() > jt["share"]:
            continue
        ax = Sd.uniform(0, 2 * math.pi)
        put(Sd.weighted(jmix), Sd.randrange(4), [p[0], p[1], z], Sd.uniform(0, 2 * math.pi),
            (math.cos(ax), math.sin(ax), 0.0), math.radians(Sd.uniform(0, 10))); count["joints"] += 1
    if parts:
        soup("tufts", parts, mats["grass"])
    return count


def stones(g, mat):
    """A few loose blocks at the foot, by eye, each the same making as the rock (a convex hull, its edges softened),
    lying on the ground, sunk a share of their height; rigid."""
    sd = D["stones"]; out = []
    for i, ((s_, t_), size) in enumerate(sd["list"]):
        Sd = HS.Stream(SEED, "r01 stone", i)
        bm = bmesh.new()
        for _ in range(sd["stonePoints"]):
            u, v_ = Sd.uniform(-1, 1), Sd.uniform(0, 2 * math.pi); r = math.sqrt(1 - u * u)
            bm.verts.new((size * 0.5 * r * math.cos(v_), size * 0.38 * r * math.sin(v_), size * 0.24 * u))
        bmesh.ops.convex_hull(bm, input=bm.verts[:])
        bmesh.ops.dissolve_limit(bm, angle_limit=math.radians(6), verts=bm.verts, edges=bm.edges)
        me = bpy.data.meshes.new(f"stone{i}"); bm.to_mesh(me); bm.free(); me.materials.append(mat)
        ob = bpy.data.objects.new(f"stone{i}", me); bpy.context.scene.collection.objects.link(ob)
        p = site(s_, t_); a, b_ = int(round((p[0] - g["xs"][0]) / g["cs"])), int(round((p[1] - g["ys"][0]) / g["cs"]))
        z = g["Zt"][a, b_] if g["M"][a, b_] else g["Gb"][a, b_]
        ob.matrix_world = Matrix.Translation((p[0], p[1], z + size * 0.24 * (1 - 2 * sd["sink"]))) @ \
            Matrix(turn(Sd.uniform(0, 2 * math.pi), (1, 0, 0), math.radians(Sd.uniform(-8, 8)))).to_4x4()
        m = ob.modifiers.new("soft", "BEVEL"); m.width = sd["stoneBevel"] * size * 0.5; m.segments = 3
        m.limit_method = "ANGLE"; m.angle_limit = math.radians(25); m.use_clamp_overlap = True; m.harden_normals = True
        for f in me.polygons:
            f.use_smooth = True
        out.append(ob)
    return out


# ---------------------------------------------------------------- the frame and the grey check
def clay(name, v, rough=0.8):
    m = bpy.data.materials.new(name); m.use_nodes = True; b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (v, v, v, 1); b.inputs["Roughness"].default_value = rough
    return m


def house(mat):
    """107 on its stand (fixture `buildings`), as tip.py puts it, on a plinth down to the record's land."""
    hj = json.load(open(os.path.join(ROOT, K["beside"]["gen"], "house.json"))); w_, d_ = hj["size"]
    stand = next(b for b in FIX["buildings"] if b["id"] == K["tip"]["stand"])
    t = math.radians(stand["turn"]); ex, ey = Vector((math.cos(t), math.sin(t), 0)), Vector((-math.sin(t), math.cos(t), 0))
    corner = Vector((stand["at"][0], stand["at"][1], stand["base"])) - ex * (w_ / 2) - ey * (d_ / 2)
    M = Matrix.Translation(corner) @ Matrix.Rotation(t, 4, "Z")
    before = set(bpy.data.objects)
    bpy.ops.import_scene.fbx(filepath=os.path.join(ROOT, K["beside"]["gen"], "house-near.fbx"))
    for o in set(bpy.data.objects) - before:
        if o.type == "MESH":
            o.matrix_world = M @ o.matrix_world; o.data.materials.clear(); o.data.materials.append(mat)
    zl = float(ground(np.array([[stand["at"][0]]]), np.array([[stand["at"][1]]]))[0, 0])
    bpy.ops.mesh.primitive_cube_add(size=1)
    p = bpy.context.active_object; p.name = "plinth"
    p.scale = (w_ + 0.2, d_ + 0.2, stand["base"] - zl + 0.3); p.rotation_euler = (0, 0, t)
    p.location = (stand["at"][0], stand["at"][1], (stand["base"] + zl - 0.3) / 2); p.data.materials.append(mat)


def views():
    V = {n: dict(v) for n, v in K["shore"]["lone"]["views"].items() if n in ("loneeye", "lone12", "lonesea")}
    V["lone12"]["fov"] = D["fov12"]
    b, out, up = D["leeView"]; tg = Vector(V["lone12"]["target"])
    V["lee"] = {"pos": list(tg + Vector((math.sin(math.radians(b)) * out, math.cos(math.radians(b)) * out, up))), "target": list(tg + Vector((0, 0, 0.3))), "fov": 45}
    V["water"] = K["tip"]["views"]["water"]
    return V


def shoot(V, tag):
    sc = bpy.context.scene
    sc.render.engine = "BLENDER_EEVEE"; sc.render.resolution_x, sc.render.resolution_y = 1280, 720
    sc.view_settings.view_transform = "AgX"
    wo = bpy.data.worlds.new("w"); sc.world = wo; wo.use_nodes = True
    bg = wo.node_tree.nodes["Background"]; bg.inputs[0].default_value = (0.8, 0.8, 0.8, 1); bg.inputs[1].default_value = 0.6
    sun = bpy.data.objects.new("sun", bpy.data.lights.new("sun", "SUN")); sc.collection.objects.link(sun); sun.data.angle = math.radians(3)
    cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam")); sc.collection.objects.link(cam); sc.camera = cam
    for n, v in V.items():
        cam.location = Vector(v["pos"]); cam.rotation_euler = (Vector(v["target"]) - Vector(v["pos"])).to_track_quat("-Z", "Y").to_euler()
        cam.data.sensor_fit = "VERTICAL"; cam.data.angle = math.radians(v["fov"]); cam.data.clip_start = 0.05
        for light, (az, el, en) in {"neutral": (330, 35, 3.0), "raking": (255, 7, 4.5)}.items():
            az, el = math.radians(az), math.radians(el)
            dv = Vector((math.sin(az) * math.cos(el), math.cos(az) * math.cos(el), math.sin(el)))
            sun.rotation_euler = (-dv).to_track_quat("-Z", "Y").to_euler(); sun.data.energy = en
            sc.render.filepath = os.path.join(OUT, f"{tag}-{n}-{light}.png"); bpy.ops.render.render(write_still=True)


def main():
    os.makedirs(OUT, exist_ok=True)
    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o)
    g_ = D["rgb"]
    mats = {k: clay(k, v, 0.8 if k == "rock" else 0.92) for k, v in g_.items()}
    parts = rock(mats["rock"])
    water = bpy.data.meshes.new("water"); water.from_pydata([(-400, -400, 0), (400, -400, 0), (400, 400, 0), (-400, 400, 0)], [], [(0, 1, 2, 3)])
    wm = bpy.data.materials.new("water"); wm.use_nodes = True; bs = wm.node_tree.nodes["Principled BSDF"]
    bs.inputs["Base Color"].default_value = (0.05, 0.055, 0.06, 1); bs.inputs["Roughness"].default_value = 0.3
    water.materials.append(wm); bpy.context.scene.collection.objects.link(bpy.data.objects.new("water", water))
    g = land(parts, mats)
    count = growth_on(g, mats)
    st = stones(g, mats["rock"])
    house(clay("house", 0.4, 0.7))
    P = evaluated_points(parts)
    a0 = P[P[:, 2] > 0.0]; s_, t_ = (a0[:, :2] - C0) @ E, (a0[:, :2] - C0) @ W
    dg = bpy.context.evaluated_depsgraph_get()
    info = {"parts": len(parts), "tris": int(sum(len(o.evaluated_get(dg).to_mesh().loop_triangles) for o in parts)),
            "crest": round(float(P[:, 2].max()), 3), "alongAtSea": round(float(np.ptp(s_)), 2), "acrossAtSea": round(float(np.ptp(t_)), 2),
            "seawardAtSea": round(float(-t_.min()), 2), "stray": int((np.hypot(*(P[:, :2] - C0).T) > 14).sum()), "tufts": count, "stones": len(st), **g["info"]}
    print("[design]", json.dumps(info))
    json.dump(info, open(os.path.join(OUT, "r01.json"), "w"), indent=1)
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "r01.blend"))
    shoot(views(), "r01")


if __name__ == "__main__":
    main()
