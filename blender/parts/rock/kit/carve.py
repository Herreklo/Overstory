"""The shore block carved high and baked to a game mesh (kit.json `carve`): natural rock as studios make it.

    Blender -b --factory-startup --python-exit-code 1 -P blender/parts/rock/kit/carve.py -- --arm A|B [--out DIR]

Arm A's big mass is shore.py's pieces before their rounds, since the bands and joints are facts. Each piece is remeshed
to a fine body and carved at three scales, each by its place:
- chips plucked off the lee's arrises and all round the plucked pockets, each bounded by the foliation and J1
  (booleans before the remesh, so their floors are the planes they broke on);
- the round where the swell washes, and only there, larger the lower (a weighted smoothing); elsewhere the arrises stay
  as the voxels leave them, a few millimetres;
- the foliation's sheets: a column of sheets across the foliation, each weathered back by its own depth and laminated
  finer, their traces crenulated as phyllite's are; stepped sharp on the lee and the plucked faces, faint on the ice's
  top, rounded where the sea washes; a few sheets plucked deeper along a stretch of their strike, the hollows and steps
  along the bands.
Arm B takes a downloaded scan's form (kit.json carve.scan) instead, set rigidly on the block's place: turned so its
long side runs along the shore, scaled whole to the block's plan, bedded as it was scanned (or tilted toward the sea by
`tilt` of the ice's fall) with its foot in the water.
Either high is baked onto its game mesh, the high remeshed coarse and reduced to the near level's triangles per square
metre, on one page: normal (tangent space), AO and curvature. Out: DIR/<arm>.blend with `<arm>-high` and `<arm>-game`
(in the block's frame, at its place), and DIR/<arm>-normal.png, -ao.png, -curv.png.
"""

import json
import math
import os
import sys

import bmesh
import bpy
import numpy as np
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
import blockin as BI  # noqa: E402
import part as PT  # noqa: E402
import shore  # noqa: E402

Z = Vector((0.0, 0.0, 1.0))
sat = lambda x: np.clip(x, 0.0, 1.0)  # noqa: E731


def link(name, me):
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    return ob


def applied(ob):
    """The object with its modifiers applied to its own mesh."""
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(ob.evaluated_get(dg))
    old = ob.data
    ob.modifiers.clear()
    ob.data = me
    bpy.data.meshes.remove(old)
    return ob


def remesh(ob, voxel):
    m = ob.modifiers.new("remesh", "REMESH")
    m.mode, m.voxel_size, m.adaptivity, m.use_smooth_shade = "VOXEL", voxel, 0.0, True
    return applied(ob)


def planes(fix):
    """The frame chips break in: the foliation's normal, J1's across it, and the line where they meet."""
    fam = PT.families(fix)
    nf = PT.normal(fam["foliation"]["dip"], fam["foliation"]["dipToward"])
    n1 = PT.normal(fam["J1"]["dip"], fam["J1"]["dipToward"])
    e2 = (n1 - nf * n1.dot(nf)).normalized()
    return nf, e2, nf.cross(e2).normalized()


def box(bm, p, half, axes):
    vs = [bm.verts.new(p + axes[0] * (half[0] * i) + axes[1] * (half[1] * j) + axes[2] * (half[2] * k))
          for i, j, k in ((-1, -1, -1), (1, -1, -1), (1, 1, -1), (-1, 1, -1), (-1, -1, 1), (1, -1, 1), (1, 1, 1), (-1, 1, 1))]
    for f in ((0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)):
        bm.faces.new([vs[i] for i in f])


def nearest(tree, P, reach):
    """Each point's nearest (location, face index) on a BVH tree within reach, or (None, -1)."""
    out = []
    for p in P:
        loc, _, i, _ = tree.find_nearest(Vector(p), reach)
        out.append((loc, -1 if i is None else i))
    return out


def mass(rec, K, fix, levels):
    """Arm A's high before its carving (module doc): shore.py's pieces fused to one mass, swelled by the ice, chipped
    at its arrises on the planes it breaks on and remeshed fine. With it, for each of its vertices: across the nearest
    crack the pieces stood apart at (0 at the gap's middle, inf where none is near), that gap, and 1 in a plucked pocket."""
    C = K["carve"]
    e, wet, storm = levels
    cells, info, draw = shore.drawn(rec, K, fix, levels)
    s, a, nf = shore.frame(rec, fix)
    seaw, lee = np.array((s.x, s.y, 0.0)), -np.array(a)
    frame = planes(fix)
    rng = PT.HS.Stream(K["world"], "carve", rec["id"], "mass")
    nr = np.random.default_rng(rng.next())

    # the pieces, each face's cell kept, and the crack walls among them: a wall whose outward ray meets a neighbour
    pcs, kinds = bmesh.new(), []
    for c in cells:
        b, _, _ = shore.assemble([c])
        me = bpy.data.meshes.new("t")
        b.to_mesh(me)
        kinds += [c["kind"] == "pluck"] * len(b.faces)
        b.free()
        pcs.from_mesh(me)
        bpy.data.meshes.remove(me)
    pcs.faces.ensure_lookup_table()
    tree = BVHTree.FromBMesh(pcs)
    walls, gaps = bmesh.new(), []
    for f in pcs.faces:
        if abs(f.normal.z) > 0.8:
            continue
        hit = tree.ray_cast(f.calc_center_median() + f.normal * 1e-4, f.normal, C["cracks"]["reachM"])
        if hit[0] is not None:
            walls.faces.new([walls.verts.new(v.co) for v in f.verts])
            gaps.append((hit[3], Vector(f.normal)))
    cracks = BVHTree.FromBMesh(walls)

    ob = link(f"mass", bpy.data.meshes.new("mass"))
    pcs.to_mesh(ob.data)
    remesh(ob, C["fuseM"])

    # the ice's long swell on what it planed (the walls stay on their joints), across the foliation and along the ice's
    # way, so the backs run long with the strike
    W = C["swell"]
    hf = Vector((nf.x, nf.y, 0)).normalized()
    sw = waves(rng, W["waves"], W["lambdaM"], lambda L: W["share"] * L, (np.array(hf), np.array(shore.bearing(fix["rock"]["ice"]["toward"]))))
    sw2 = waves(rng, W["waves"], W["shortM"], lambda L: W["share"] * L, (np.array(hf), np.array((0.0, 0.0, 1.0))))
    M = Mesh(ob.data)
    N = M.normals()
    M.P += N * ((sw(M.P) + sw2(M.P)) * sat((N[:, 2] - W["upFrom"]) / 0.3))[:, None]
    N = M.normals()

    # chips at three sizes off the arrises, on the foliation and J1 a little turned: most on the lee and round the
    # pockets, few where the swell washes
    H = C["chips"]
    bend = 1 - np.einsum("ij,ij->i", N, M.mean(N))
    pl = np.array([kinds[i] if i >= 0 else False for _, i in nearest(tree, M.P, 0.2)], dtype=float)
    z = M.P[:, 2]
    washed = sat((storm - z) / 0.3) * sat((N @ seaw + 0.2) / 0.5)
    w = (bend > H["bend"]) * (H["elsewhere"] + (1 - H["elsewhere"]) * np.maximum(sat((N @ lee - 0.1) / 0.4), pl)) * (1 - H["wash"] * washed)
    col = bpy.data.collections.new("chips")
    bpy.context.scene.collection.children.link(col)
    nchips = 0
    for cl in H["classes"]:
        idx = nr.choice(len(w), size=min(cl["count"], int((w > 0).sum())), replace=False, p=w / w.sum())
        for i in idx:
            size = nr.uniform(*cl["sizeM"]) / 2
            half = (size * nr.uniform(*H["fol"]), size, size * nr.uniform(*H["along"]))
            ax = Vector(nr.normal(size=3)).normalized()
            R = Matrix.Rotation(math.radians(nr.uniform(-H["turn"], H["turn"])), 3, ax)
            bm = bmesh.new()
            box(bm, Vector(M.P[i] - N[i] * min(half) * H["bite"]), half, [R @ v for v in frame])
            me = bpy.data.meshes.new("chip")
            bm.to_mesh(me)
            bm.free()
            col.objects.link(bpy.data.objects.new("chip", me))
            nchips += 1
    m = ob.modifiers.new("chips", "BOOLEAN")
    m.operation, m.operand_type, m.collection, m.solver = "DIFFERENCE", "COLLECTION", col, "MANIFOLD"
    applied(ob)
    for o in list(col.objects):
        bpy.data.objects.remove(o)
    bpy.data.collections.remove(col)
    remesh(ob, C["voxelM"])

    # each fine vertex's place among the cracks and the pockets
    M = Mesh(ob.data)
    x, gap = np.full(len(M.P), np.inf), np.zeros(len(M.P))
    for k, (loc, i) in enumerate(nearest(cracks, M.P, C["cracks"]["reachM"])):
        if i >= 0:
            g, n = gaps[i]
            x[k], gap[k] = (Vector(M.P[k]) - loc).dot(n) - g / 2, g
    pluck = np.array([kinds[i] if i >= 0 else False for _, i in nearest(tree, M.P, 0.2)], dtype=float)
    pcs.free()
    walls.free()
    print(f"[carve] {rec['id']} (draw {draw}): {len(cells)} pieces fused, {len(gaps)} crack walls, {nchips} chips, "
          f"{len(M.P)} vertices")
    return ob, x, gap, pluck


class Mesh:
    """A mesh's vertices, edges and normals as arrays, written back after each change."""

    def __init__(self, me):
        self.me = me
        n = len(me.vertices)
        self.P = np.empty(n * 3)
        me.vertices.foreach_get("co", self.P)
        self.P = self.P.reshape(n, 3)
        E = np.empty(len(me.edges) * 2, dtype=np.int64)
        me.edges.foreach_get("vertices", E)
        self.E = E.reshape(-1, 2)
        self.deg = np.maximum(np.bincount(self.E.ravel(), minlength=n), 1).astype(float)

    def put(self):
        self.me.vertices.foreach_set("co", self.P.ravel())
        self.me.update()

    def normals(self):
        self.put()
        N = np.empty(len(self.P) * 3)
        self.me.vertex_normals.foreach_get("vector", N)
        return N.reshape(-1, 3)

    def mean(self, X):
        """Each vertex's neighbours' mean of X (n, k)."""
        i, j = self.E[:, 0], self.E[:, 1]
        return np.stack([np.bincount(i, X[j, c], len(X)) + np.bincount(j, X[i, c], len(X))
                         for c in range(X.shape[1])], 1) / self.deg[:, None]

    def smooth(self, w, iters, lam):
        for _ in range(iters):
            self.P += lam * w[:, None] * (self.mean(self.P) - self.P)


def waves(rng, count, lam, amp, plane):
    """A sum of sines along random directions in a plane (n): crenulation."""
    out = []
    for _ in range(count):
        t = rng.uniform(0, 2 * math.pi)
        u = (plane[0] * math.cos(t) + plane[1] * math.sin(t))
        L = rng.uniform(*lam)
        out.append((np.array(u) * 2 * math.pi / L, rng.uniform(0, 2 * math.pi), amp(L)))
    return lambda P: sum(A * np.sin(P @ d + ph) for d, ph, A in out)


def column(rng, lo, hi, thick):
    """Sheet boundaries along a line from lo to hi, each sheet `thick` (a range) thick."""
    b = [lo - rng.uniform(*thick)]
    while b[-1] < hi:
        b.append(b[-1] + rng.uniform(*thick))
    return np.array(b)


def carve(me, rec, K, fix, levels, x, gap, pluck):
    """Arm A's carving by place on its fine mass (module doc): the wash's round, the cracks, then the sheets. `x`,
    `gap` and `pluck` are mass()'s."""
    C = K["carve"]
    H = C["sheets"]
    e, wet, storm = levels
    s, a, nf = shore.frame(rec, fix)
    seaw = np.array((s.x, s.y, 0.0))
    lee = -np.array(a)
    nfa = np.array(nf)
    strike = np.array(nf.cross(Z).normalized())
    up = np.cross(nfa, strike)
    M = Mesh(me)
    N = M.normals()
    z = M.P[:, 2]

    # the swell rounds what faces it below the storm top, larger the lower, little on the lee; elsewhere only the
    # voxels' few mm
    depth = sat((storm - z) / max(storm, 0.3))
    w = (sat((storm - z) / 0.3) * (0.4 + 0.6 * depth) * (0.5 + 0.5 * e) * sat((N @ seaw + C["wash"]["face"]) / 0.5)
         * (1 - (1 - C["wash"]["lee"]) * sat((N @ lee - 0.2) / 0.4)))
    top = sat((N[:, 2] - 0.5) / 0.3) * (1 - w)
    w = np.maximum(np.maximum(w, C["ice"] * top), C["edge"])
    for _ in range(3):
        w = M.mean(w[:, None])[:, 0]
    M.smooth(w, C["wash"]["iters"], C["wash"]["lam"])
    N = M.normals()
    z = M.P[:, 2]

    # the cracks the pieces stood apart at, cut again where the fusing closed them: a groove down each, wider and
    # deeper where the sea washes it, its line wandering on the sheets
    G = C["cracks"]
    washed = sat((storm - z) / 0.3)
    wander = waves(PT.HS.Stream(K["world"], "carve", rec["id"], "cracks"), G["waves"], G["wanderLambdaM"],
                   lambda L: G["wanderM"], (strike, np.array((0.0, 0.0, 1.0))))
    half = gap / 2 + G["widthM"] * (1 + (G["wash"] - 1) * washed)
    groove = G["depthM"] * (1 + (G["wash"] - 1) * washed) * sat(1 - np.abs(x - wander(M.P)) / half) ** 2
    M.P -= N * groove[:, None]
    N = M.normals()
    z = M.P[:, 2]

    # the sheets: where each surface cuts them, each sheet stands back by its own depth and its laminae finer, their
    # traces crenulated; stepped on the lee and in the pockets, faint on the ice's top, rounded where the sea washes
    rng = PT.HS.Stream(K["world"], "carve", rec["id"], "sheets")
    nr = np.random.default_rng(rng.next())
    warp = waves(rng, H["warp"]["waves"], H["warp"]["lambdaM"], lambda L: H["warp"]["share"] * L, (strike, up))
    fine = waves(rng, H["warp"]["fine"]["waves"], H["warp"]["fine"]["lambdaM"], lambda L: H["warp"]["fine"]["ampM"], (strike, up))
    t = M.P @ nfa + warp(M.P) + fine(M.P)
    lo, hi = t.min(), t.max()
    sheets = column(rng, lo, hi, H["sheetM"])
    lam = column(rng, lo, hi, H["lamM"])
    rs = nr.random(len(sheets)) ** H["pow"]
    rl = nr.random(len(lam))
    i = np.clip(np.searchsorted(sheets, t), 1, len(sheets) - 1)
    j = np.clip(np.searchsorted(lam, t), 1, len(lam) - 1)
    u = (t - lam[j - 1]) / (lam[j] - lam[j - 1])
    us = (t - sheets[i - 1]) / (sheets[i] - sheets[i - 1])
    crisp = H["sheetDepthM"] * rs[i] + H["fineM"] * rl[j]
    soft = H["sheetDepthM"] * rs[i] * (1 - (2 * us - 1) ** 8) + H["fineM"] * rl[j] * 4 * u * (1 - u)
    washed = sat((storm - z) / 0.3)
    leeish = np.maximum(sat((N @ lee - 0.2) / 0.4), pluck)
    topish = sat((N[:, 2] - 0.6) / 0.25) * (1 - leeish)
    amp = (1 + (H["lee"] - 1) * leeish) * (1 - (1 - H["top"]) * topish) * (1 - (1 - H["wash"]) * washed)
    d = amp * ((1 - washed) * crisp + washed * soft)

    # a few sheets plucked deeper along a stretch of their strike, their ends wandering: hollows and steps on the bands
    D = H["deep"]
    ends = waves(rng, 3, D["wanderLambdaM"], lambda L: D["wanderM"], (nfa, up))
    us_ = M.P @ strike + ends(M.P)
    deep = np.zeros(len(t))
    for _ in range(rng.randint(*D["count"])):
        k = int(rng.uniform(1, len(sheets) - 1))
        c0 = rng.uniform(us_.min(), us_.max())
        half = rng.uniform(*D["lengthM"]) / 2
        win = sat((half - np.abs(us_ - c0)) / 0.06)
        deep = np.maximum(deep, (i == k) * win * rng.uniform(*D["depthM"]))
    d += deep * (1 - 0.5 * washed) * (1 - 0.6 * topish)
    M.P -= N * d[:, None]
    M.put()
    print(f"[carve] sheets {len(sheets)}, laminae {len(lam)}; relief {d.min() * 1000:.1f}-{d.max() * 1000:.1f} mm, "
          f"wash round on {int((w > 0.2).sum())} of {len(w)} vertices")


def scan(rec, K, fix, centre):
    """Arm B's high: the scan's form set rigidly on the block's place (module doc), its plan's middle on `centre` (arm
    A's pieces' middle, in the block's frame) and its foot in the water at carve.game.cutZ."""
    C = K["carve"]["scan"]
    before = set(bpy.context.scene.objects)
    bpy.ops.import_scene.gltf(filepath=os.path.expanduser(C["file"]))
    new = [o for o in bpy.context.scene.objects if o not in before]
    obs = [o for o in new if o.type == "MESH"]
    bm = bmesh.new()
    for o in obs:
        t = bmesh.new()
        t.from_mesh(o.data)
        t.transform(o.matrix_world)
        me = bpy.data.meshes.new("t")
        t.to_mesh(me)
        bm.from_mesh(me)
        t.free()
    for o in new:
        bpy.data.objects.remove(o)
    P = np.array([v.co for v in bm.verts])
    # its long side along the shore: the plan's principal axis turned onto a
    xy = P[:, :2] - P[:, :2].mean(0)
    ev = np.linalg.eigh(xy.T @ xy)[1][:, -1]
    s, a, nf = shore.frame(rec, fix)
    turn = math.atan2(a.y, a.x) - math.atan2(ev[1], ev[0])
    R = Matrix.Rotation(turn, 4, "Z")
    bm.transform(R)
    P = np.array([v.co for v in bm.verts])
    k = min(rec["width"] / np.ptp(P @ np.array(a)), rec["depth"] / np.ptp(P @ np.array(s)))
    fall = math.atan2(rec["back"] - rec["lip"], rec["depth"]) * C["tilt"]
    T = Matrix.Rotation(fall, 4, Z.cross(s)) @ Matrix.Scale(k, 4)
    bm.transform(T)
    P = np.array([v.co for v in bm.verts])
    c = (P.max(0) + P.min(0)) / 2
    bm.transform(Matrix.Translation(Vector((centre[0] - c[0], centre[1] - c[1], K["carve"]["game"]["cutZ"] - P[:, 2].min()))))
    print(f"[carve] scan {os.path.basename(C['file'])}: {len(bm.faces)} faces, turned {math.degrees(turn):.0f}, scaled {k:.2f}, "
          f"tilted {math.degrees(fall):.0f} toward the sea")
    return bm


def bands(ob, mats, levels):
    """Each face to its band's material by its centre's height (wet, wash, rock)."""
    e, wet, storm = levels
    me = ob.data
    me.materials.clear()
    for m in mats:
        me.materials.append(m)
    n = len(me.polygons)
    c = np.empty(n * 3)
    me.polygons.foreach_get("center", c)
    zc = c.reshape(n, 3)[:, 2]
    me.polygons.foreach_set("material_index", np.where(zc < wet, 0, np.where(zc < storm, 1, 2)).astype(np.int32))


def game(high, target, G):
    """The game mesh: the high remeshed coarse (if it is closed: a scan's open foot is not), cut under the water, and
    reduced to `target` triangles."""
    ob = link(high.name.replace("high", "game"), high.data.copy())
    ob.data.materials.clear()
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    closed = all(e.is_manifold for e in bm.edges)
    bm.free()
    if closed:
        remesh(ob, G["voxelM"])
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    bmesh.ops.delete(bm, geom=[f for f in bm.faces if all(v.co.z < G["cutZ"] for v in f.verts)], context="FACES")
    area = sum(f.calc_area() for f in bm.faces)
    bm.to_mesh(ob.data)
    bm.free()
    tris = sum(len(p.vertices) - 2 for p in ob.data.polygons)
    m = ob.modifiers.new("reduce", "DECIMATE")
    m.decimate_type, m.ratio, m.use_collapse_triangulate = "COLLAPSE", min(1.0, target / tris), True
    applied(ob)
    m = ob.modifiers.new("tri", "TRIANGULATE")
    applied(ob)
    for p in ob.data.polygons:
        p.use_smooth = True
    print(f"[carve] game {ob.name}: {len(ob.data.polygons)} triangles on {area:.1f} m2 ({len(ob.data.polygons) / area:.0f} per m2)")
    return ob


def select(*obs, active):
    for o in bpy.context.scene.objects:
        o.select_set(o in obs or o is active)
    bpy.context.view_layer.objects.active = active


def unwrap(ob):
    ob.data.uv_layers.new(name="page")
    select(active=ob)
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.smart_project(angle_limit=math.radians(66), island_margin=0.004, area_weight=0.0, correct_aspect=True,
                             scale_to_bounds=False)
    bpy.ops.object.mode_set(mode="OBJECT")


def bake(high, low, out, arm, B):
    """The high onto the game mesh's page: normal (tangent), AO, curvature; the game's materials then wear the normal."""
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    try:
        pr = bpy.context.preferences.addons["cycles"].preferences
        pr.compute_device_type = "METAL"
        pr.get_devices()
        for d in pr.devices:
            d.use = True
        sc.cycles.device = "GPU"
    except Exception as err:  # noqa: BLE001
        print(f"[carve] bake on the CPU ({err})")
    if sc.world is None:
        sc.world = bpy.data.worlds.new("bake")
    sc.world.light_settings.distance = B["aoM"]
    rb = sc.render.bake
    rb.use_selected_to_active, rb.cage_extrusion, rb.max_ray_distance, rb.margin = True, B["cageM"], B["rayM"], 8
    low.visible_diffuse = low.visible_glossy = low.visible_shadow = low.visible_transmission = False
    maps = {}
    for kind in ("normal", "ao", "curv"):
        img = bpy.data.images.new(f"{arm}-{kind}", B["size"], B["size"], alpha=False)
        img.colorspace_settings.name = "Non-Color"
        for m in low.data.materials:
            nd = m.node_tree.nodes.new("ShaderNodeTexImage")
            nd.name, nd.image = kind, img
            m.node_tree.nodes.active = nd
        keep = list(high.data.materials)
        if kind == "curv":
            cm = bpy.data.materials.new("curv")
            cm.use_nodes = True
            nt = cm.node_tree
            nt.nodes.clear()
            g, r, em, o = (nt.nodes.new(t) for t in ("ShaderNodeNewGeometry", "ShaderNodeMapRange", "ShaderNodeEmission",
                                                      "ShaderNodeOutputMaterial"))
            r.inputs["From Min"].default_value, r.inputs["From Max"].default_value = B["curv"]
            nt.links.new(g.outputs["Pointiness"], r.inputs["Value"])
            nt.links.new(r.outputs["Result"], em.inputs["Color"])
            nt.links.new(em.outputs["Emission"], o.inputs["Surface"])
            for k in range(len(high.data.materials)):
                high.data.materials[k] = cm
        sc.cycles.samples = B["aoSamples"] if kind == "ao" else B["samples"]
        select(high, active=low)
        bpy.ops.object.bake(type={"normal": "NORMAL", "ao": "AO", "curv": "EMIT"}[kind], normal_space="TANGENT")
        for k, m in enumerate(keep):
            high.data.materials[k] = m
        img.filepath_raw = os.path.join(out, f"{arm}-{kind}.png")
        img.file_format = "PNG"
        img.save()
        maps[kind] = img
    low.visible_diffuse = low.visible_glossy = low.visible_shadow = low.visible_transmission = True
    for m in low.data.materials:
        nt = m.node_tree
        nm = nt.nodes.new("ShaderNodeNormalMap")
        nm.uv_map = "page"
        nt.links.new(nt.nodes["normal"].outputs["Color"], nm.inputs["Color"])
        nt.links.new(nm.outputs["Normal"], nt.nodes["Principled BSDF"].inputs["Normal"])
    return maps


def main():
    arm = BI.arg("--arm", "A")
    out = os.path.abspath(BI.arg("--out", os.path.join(ROOT, "cache", "rock", "kit", "gen", "carve")))
    os.makedirs(out, exist_ok=True)
    K = json.load(open(os.path.join(HERE, "kit.json")))
    C = K["carve"]
    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o)
    rec = dict(K["shore"]["lone"], row=0)
    s = shore.bearing(rec["face"])
    c = np.array([rec["at"][0] - s.x * rec["depth"] / 2, rec["at"][1] - s.y * rec["depth"] / 2, 1.0])
    e, (wet, storm, _) = BI.shore_levels(K["tip"]["grey"]["bands"], c)
    levels = (e, wet, storm)
    G = K["tip"]["grey"]["values"]
    mats = [BI.material(n, *G[n]) for n in shore.BANDS]
    baked = [BI.material(n + "-baked", *G[n]) for n in shore.BANDS]

    if arm == "A":
        high, x, gap, pluck = mass(rec, K, BI.FIX, levels)
        high.name = high.data.name = "A-high"
        carve(high.data, rec, K, BI.FIX, levels, x, gap, pluck)
    else:
        cells = shore.drawn(rec, K, BI.FIX, levels)[0]
        P = np.array([p for c in cells for col in c["cols"] for _, p in col])
        bm = scan(rec, K, BI.FIX, (P.max(0) + P.min(0)) / 2)
        high = link(f"{arm}-high", bpy.data.meshes.new(f"{arm}-high"))
        bm.to_mesh(high.data)
        bm.free()
    for p in high.data.polygons:
        p.use_smooth = True
    bands(high, mats, levels)
    low = game(high, int(C["game"]["trisPerM2"] * rec["width"] * rec["depth"]), C["game"])
    bands(low, baked, levels)
    unwrap(low)
    bake(high, low, out, arm, C["bake"])
    for ob in (high, low):
        ob.location = (rec["at"][0], rec["at"][1], 0.0)
    json.dump({"levels": levels, "high": len(high.data.polygons), "game": len(low.data.polygons)},
              open(os.path.join(out, f"{arm}.json"), "w"))
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(out, f"{arm}.blend"))
    print(f"[carve] {arm}: high {len(high.data.polygons)} faces, game {len(low.data.polygons)} triangles; wrote {out}")


if __name__ == "__main__":
    main()
