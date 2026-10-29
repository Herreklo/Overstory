"""The shore block as the ice left it (kit.json `whaleback`): one smooth hull, cut on the rock's own planes.

    Blender -b --factory-startup --python-exit-code 1 -P blender/parts/rock/kit/whaleback.py -- [--bake 1] [--out DIR]

The ice made the big form, so it comes first: a whaleback (roche moutonnee), its long back smooth toward where the ice
came from and falling to the sea. One heightfield hull in the ice's frame (u the way it went, v across it toward the
sea): over a superellipse plan, longer up-ice and seaward, a round cap falling to straight slabs, with a few long low
flutes along the ice's way, its crest at the record's back. Then it is cut, never smoothed, by exact plane
booleans on that clean hull:
- the back's sheets: the ice planed across the foliation, so each sheet is a few broad planar treads, each rising
  toward the dip so the next sheet's edge crops out lower as a low riser on the foliation, with leaves plucked from
  the edges between J1 joints (the sea's round kept under the wet line);
- the plucked lee: steep steps down-ice, each block gone above its tread on the sheeting (falling gently down-ice) and
  beyond its front, which crosses the whole width on the planes that cross the ice's way, in strips between J1 joints
  that run on through every step: a J2 face on the sea side, the foliation's riser (leaning back toward its dip), a J3
  face to the land side;
  each lower and further until under the sea; and a few leaves plucked out at the risers' feet between minor J1 joints;
- the main joints across the back (kit.json `cracks`, one a family), straight-sided cracks through the block, their
  lips chipped by small wedges falling into them.
The back's lower edge keeps the hull's own round where the sea washes it; the cut arrises stay crisp. Out: DIR/W.blend
with `W-high` (and with --bake 1 `W-game` and its page, baked as carve.py bakes) in the block's frame at its place.
"""

import json
import os
import sys

import bmesh
import bpy
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
import blockin as BI  # noqa: E402
import carve  # noqa: E402
import hull as HL  # noqa: E402
import part as PT  # noqa: E402
import shore  # noqa: E402


def frame(fix):
    """The ice's frame (u its way, v across toward the sea, both level) and the planes the rock breaks on."""
    fam = PT.families(fix)
    toward = fix["rock"]["ice"]["toward"]
    du, dv = np.array(shore.bearing(toward))[:2], np.array(shore.bearing(toward + 90))[:2]
    n = {k: np.array(PT.normal(fam[k]["dip"], fam[k]["dipToward"])) for k in ("foliation", "J1", "J2", "J3")}
    return du, dv, n, toward


def profile(s, H):
    """The back's fall from its crest (s 0) to the datum (s 1): a round cap out to `cap`, then straight slabs."""
    s0 = H["cap"]
    g = np.where(s < s0, 1 - s * s / (2 * s0), 1 - s0 / 2 - (s - s0))
    return H["crestM"] * (g - s0 / 2) / (1 - s0 / 2)


def surface(W, crest, du, dv, rng):
    """The hull's height over a grid of the plan, longer up-ice and seaward."""
    H = W["hull"]
    cell, m = H["cellM"], H["plan"]
    us = np.arange(-H["stossM"] * 1.35, H["leeM"] * 1.35 + cell, cell)
    vs = np.arange(-H["landM"] * 1.35, H["seaM"] * 1.35 + cell, cell)
    U, V = np.meshgrid(us, vs, indexing="ij")
    a = np.where(U < 0, H["stossM"], H["leeM"])
    b = np.where(V < 0, H["landM"], H["seaM"])
    h = profile(((np.abs(U) / a) ** m + (np.abs(V) / b) ** m) ** (1 / m), H)
    for _ in range(H["waves"]):  # long low flutes the ice left along its way, a few centimetres
        lam = rng.uniform(*H["lambdaM"])
        t = np.pi / 2 + np.radians(rng.uniform(-1, 1) * H["acrossDeg"])
        k = 2 * np.pi / lam * np.array([np.cos(t), np.sin(t)])
        h += H["share"] * lam * np.sin(U * k[0] + V * k[1] + rng.uniform(0, 2 * np.pi))
    h = np.maximum(h, H["footM"])
    X = crest[0] + U * du[0] + V * dv[0]
    Y = crest[1] + U * du[1] + V * dv[1]
    return X, Y, h


def mesh_of(name, X, Y, h, foot):
    """A closed hull: the heightfield, its rim taken down under the foot and closed flat."""
    nu, nv = h.shape
    P = np.stack([X.ravel(), Y.ravel(), h.ravel()], 1)
    idx = np.arange(nu * nv).reshape(nu, nv)
    Q = np.stack([idx[:-1, :-1], idx[1:, :-1], idx[1:, 1:], idx[:-1, 1:]], -1).reshape(-1, 4)
    me = bpy.data.meshes.new(name)
    me.from_pydata(P.tolist(), [], Q.tolist())
    bm = bmesh.new()
    bm.from_mesh(me)
    rim = [e for e in bm.edges if e.is_boundary]
    ret = bmesh.ops.extrude_edge_only(bm, edges=rim)
    for v in ret["geom"]:
        if isinstance(v, bmesh.types.BMVert):
            v.co.z = foot - 0.3
    bmesh.ops.holes_fill(bm, edges=[e for e in bm.edges if e.is_boundary], sides=0)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(me)
    bm.free()
    return carve.link(name, me)


def body_mesh(faces, name):
    """A convex body (hull.py's faces) as a closed mesh, its corners welded."""
    V, T, _, _ = HL.triangles(faces)
    me = bpy.data.meshes.new(name)
    me.from_pydata(V.tolist(), [], T.tolist())
    bm = bmesh.new()
    bm.from_mesh(me)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(me)
    bm.free()
    return me


def sheets(W, X, Y, h, n, spacing, wet, lo, hi, rng):
    """What the ice planed off the back across the foliation: in each sheet (between two of its planes `spacing` apart),
    everything above a few broad planar treads fitted just under the hull, `alongM` each along the strike. Each tread
    rises toward the foliation's dip by its own `riseM`, so at a sheet edge the next sheet crops out that much lower, a
    riser on the foliation leaning back down-ice as the plucked side of a step, growing and dying out along the strike; the hull's own round stays
    where the sea washes the lower edge (under `wet`, which no tread is fitted to). Along each edge the ice plucked
    `bites`: a leaf `deepM` thick gone from the higher sheet's edge, `longM` long between two J1 joints, down to the
    lower sheet's tread, so the edge jogs back and on as it runs."""
    S, H, B, nf = W["sheets"], W["hull"], W["sheets"]["bites"], n["foliation"]
    k = max(1, int(round(S["fitM"] / H["cellM"])))
    P = np.stack([X[::k, ::k].ravel(), Y[::k, ::k].ravel(), h[::k, ::k].ravel()], 1)
    P = P[P[:, 2] > wet]
    f = P @ nf
    st = np.array([-nf[1], nf[0]]) / np.linalg.norm(nf[:2])  # along the strike, level
    a = P[:, :2] @ st
    d = [f.min() - rng.uniform(0, spacing[1])]
    while d[-1] < f.max():
        d.append(d[-1] + rng.uniform(*spacing))
    bodies, treads = [], []
    for d0, d1 in zip(d[:-1], d[1:]):
        treads.append([])
        inside = (f >= d0) & (f < d1)
        Q, A, t = P[inside], a[inside], (d1 - f[inside]) / (d1 - d0)  # t 1 at the sheet's up-dip edge, 0 at its down-dip
        if len(Q) < S["fewest"]:
            continue
        ends = [A.min() - rng.uniform(0, S["alongM"][1])]
        while ends[-1] < A.max():
            ends.append(ends[-1] + rng.uniform(*S["alongM"]))
        for i, (a0, a1) in enumerate(zip(ends[:-1], ends[1:])):
            sel = (A >= a0) & (A < a1)
            if sel.sum() < S["fewest"]:
                continue
            M = np.c_[Q[sel, :2], np.ones(sel.sum())]
            target = Q[sel, 2] - rng.uniform(*S["riseM"]) * t[sel]  # each tread its own rise: an edge grows and dies out
            co = np.linalg.lstsq(M, target, rcond=None)[0]
            co[2] -= max(0.0, float((M @ co - target).max()))  # all of it under the hull: a cut, never a fill
            treads[-1].append((a0, a1, co))
            m = np.array([co[0], co[1], -1.0])
            o = S["overlapM"] * (1 + 0.3 * i)  # neighbouring bodies overlap a little, never sharing a face
            bodies.append(HL.body(lo, hi, [(nf, d1 + o, "foliation"), (-nf, -(d0 - o), "foliation"),
                                           (m / np.linalg.norm(m), -co[2] / np.linalg.norm(m), "tread")]))
    n1 = n["J1"] if n["J1"][:2] @ st > 0 else -n["J1"]
    for j, edge in enumerate(d[1:-1]):  # the edge between sheet j (up-dip) and j + 1
        on = np.abs(f - edge) < S["fitM"]
        if not on.any() or not treads[j + 1]:
            continue
        E, Ea = P[on], a[on]
        x = Ea.min()
        while x < Ea.max():
            x += rng.uniform(*B["gapM"])
            if rng.random() > B["chance"]:
                continue
            pb = E[np.argmin(np.abs(Ea - x))]
            under = [co for a0, a1, co in treads[j + 1] if a0 <= x < a1] or [treads[j + 1][0][2]]
            co, ln = under[0], rng.uniform(*B["longM"])
            m = np.array([co[0], co[1], -1.0])
            bodies.append(HL.body(lo, hi, [(nf, edge + S["overlapM"] * rng.uniform(4, 5), "foliation"),
                                           (-nf, -(edge - rng.uniform(*B["deepM"])), "foliation"),
                                           (n1, n1 @ pb + ln / 2, "J1"), (-n1, -(n1 @ pb - ln / 2), "J1"),
                                           (m / np.linalg.norm(m), (rng.uniform(*B["dropM"]) - co[2]) / np.linalg.norm(m),
                                            "tread")]))
    return [b for b in bodies if b is not None]


def lips(W, crest, surf, du, dv, n, walls, lo, hi, rng):
    """Chips plucked off the main joints' lips: small wedges broken from an edge on a plane falling from the surface,
    `inM` back from the wall, to the wall `downM` under it, `longM` long between two joints of the crossing family."""
    L = W["lips"]
    bodies = []
    for c in W["cracks"]:
        nc, ne = n[c["family"]], n[L["endOn"][c["family"]]]
        tc = np.cross(nc, [0.0, 0.0, 1.0])
        tc /= np.linalg.norm(tc)
        ne = ne if ne @ tc > 0 else -ne
        nh = nc[:2] / np.linalg.norm(nc[:2])
        p0 = crest + du * c["at"][0] + dv * c["at"][1]
        d = sum(walls[c["family"]]) / 2
        w = walls[c["family"]][1] - walls[c["family"]][0]
        s = -L["reachM"]
        while s < L["reachM"]:
            s += rng.uniform(*L["gapM"])
            side = 1 if rng.random() < 0.5 else -1
            cin, e, ln = rng.uniform(*L["inM"]), rng.uniform(*L["downM"]), rng.uniform(*L["longM"])
            D = d + side * w / 2
            q = p0 + tc[:2] * s
            for _ in range(3):  # onto the wall at the surface
                z = surf(q + side * nh * cin / 2)
                if z is None:
                    break
                q = q + nh * (D - nc @ np.array([q[0], q[1], z])) / (nc[:2] @ nh)
            if z is None or rng.random() > L["chance"]:
                continue
            k = e / cin
            m = side * k * nc - np.array([0.0, 0.0, 1.0])  # above the break plane, on the wall's side of it
            q3 = np.array([q[0], q[1], z])
            bodies.append(HL.body(lo, hi, [
                (m / np.linalg.norm(m), (-(z - e) + side * k * D) / np.linalg.norm(m), "lip"),
                (-side * nc, -side * (D - side * w * rng.uniform(0.3, 0.6)), "crack"),
                (side * nc, side * (D + side * 2 * cin), "lip"),
                (ne, ne @ (q3 + tc * ln / 2), L["endOn"][c["family"]]),
                (-ne, -(ne @ (q3 - tc * ln / 2)), L["endOn"][c["family"]])]))
    return [b for b in bodies if b is not None]


def cutters(W, crest, z_at, du, dv, n, toward, lo, hi, rng):
    """The bodies the lee and the joints lost, each the intersection of half-spaces on the rock's own planes."""
    L, C = W["lee"], W["cracks"]
    nf, n1 = n["foliation"], n["J1"]
    nt = np.array(PT.normal(L["treadDip"], toward))
    up = lambda p, z: np.array([p[0], p[1], z])  # noqa: E731
    bodies = []
    # the main joints across the back: narrow, straight-sided, through the block
    walls = {}
    for c in C:
        p = crest + du * c["at"][0] + dv * c["at"][1]
        w = rng.uniform(*W["crackM"])
        d = HL.through(n[c["family"]], up(p, z_at(p)))
        walls[c["family"]] = (d - w / 2, d + w / 2)
        bodies.append(HL.body(lo, hi, [(n[c["family"]], d + w / 2, "crack"), (-n[c["family"]], -(d - w / 2), "crack")]))
    # the plucked lee: step after step down-ice, each block gone above its tread on the sheeting and beyond its front.
    # Only J2 and J3 cross the ice's way, so a front crosses the width in three strips between J1 joints that run on
    # through every step (the main J1 joint, and one `landM` toward the land): a J2 face in the sea strip, the
    # foliation's riser in the middle one, a J3 face in the land strip, each strip stepping down on its own
    n2, n3 = n["J2"], n["J3"]
    sgn = 1 if n1[:2] @ dv < 0 else -1  # n1 toward the land (+1) or the sea (-1)
    j = sum(walls["J1"]) / 2
    j_land = j + sgn * rng.uniform(*L["landM"])
    o = 0.003  # neighbouring strips overlap a little (inside the main joint's crack), so no two cuts share a face
    strips = [[(sgn * n1, sgn * j + o, "J1")],
              [(-sgn * n1, -sgn * j + o, "J1"), (sgn * n1, sgn * j_land + o, "J1")],
              [(-sgn * n1, -sgn * j_land + o, "J1")]]
    for (nm, sg, fam), strip in zip([(n2, 1, "J2"), (nf, -1, "foliation"), (n3, 1, "J3")], strips):
        x, k = L["startM"] + rng.uniform(*L["jogM"]), 0  # each strip plucked on its own: no step runs on across a joint
        top = z_at(crest + du * x)
        while top > L["underM"] and k < L["most"]:
            p = crest + du * x
            z = top - rng.uniform(*L["riseM"])
            d = HL.through(nm, up(p, top))
            over = (-nt, -HL.through(nt, up(p, z)), "sheeting")
            bodies.append(HL.body(lo, hi, [(sg * nm, sg * d, fam), *strip, over]))
            if fam == "foliation" and rng.random() < L["pluck"]:  # a leaf plucked at the riser's foot, between minor J1 joints
                t, wj = rng.uniform(*L["leafM"]), rng.uniform(*L["pocketM"])
                a = HL.through(n1, up(p + dv * rng.uniform(-1.2, 0.4), z))
                floor = HL.through(nt, up(p, z - rng.uniform(*L["pocketDepthM"])))
                bodies.append(HL.body(lo, hi, [(-nf, -(d - t), "foliation"), (nf, d + 0.02, "foliation"),
                                               (-nt, -floor, "sheeting"), (n1, a + wj, "J1"),
                                               (-n1, -a, "J1")]))
            x += rng.uniform(*L["spacingM"])
            top = z
            k += 1
    return [b for b in bodies if b is not None], walls


def tidy(ob):
    """Drop the crumbs a cut left loose (pieces under a hundredth of the largest); the blocks the joints part stay."""
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    bm.faces.ensure_lookup_table()
    seen, pieces = set(), []
    for f0 in bm.faces:
        if f0.index in seen:
            continue
        piece, todo = [], [f0]
        seen.add(f0.index)
        while todo:
            f = todo.pop()
            piece.append(f)
            for e in f.edges:
                for g in e.link_faces:
                    if g.index not in seen:
                        seen.add(g.index)
                        todo.append(g)
        pieces.append(piece)
    pieces.sort(key=len)
    crumbs = [f for piece in pieces if len(piece) < len(pieces[-1]) / 100 for f in piece]
    if crumbs:
        bmesh.ops.delete(bm, geom=list({v for f in crumbs for v in f.verts}), context="VERTS")
        bm.to_mesh(ob.data)
    bm.free()


def cut(ob, bodies, solver):
    """Take the bodies (hull.py's) off the mesh in one exact boolean."""
    col = bpy.data.collections.new("cuts")
    for i, b in enumerate(bodies):
        col.objects.link(bpy.data.objects.new(f"cut{i}", body_mesh(b, f"cut{i}")))
    m = ob.modifiers.new("cuts", "BOOLEAN")
    m.operation, m.operand_type, m.collection, m.solver = "DIFFERENCE", "COLLECTION", col, solver
    carve.applied(ob)
    tidy(ob)
    for o in list(col.objects):
        bpy.data.objects.remove(o)
    bpy.data.collections.remove(col)


def main():
    out = os.path.abspath(BI.arg("--out", os.path.join(ROOT, "cache", "rock", "kit", "gen", "carve")))
    os.makedirs(out, exist_ok=True)
    K = json.load(open(os.path.join(HERE, "kit.json")))
    W, C = K["whaleback"], K["carve"]
    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o)
    rec = dict(K["shore"]["lone"], row=0)
    s = shore.bearing(rec["face"])
    c = np.array([-s.x * rec["depth"] / 2, -s.y * rec["depth"] / 2])  # the block's middle, in its frame
    e, (wet, storm, _) = BI.shore_levels(K["tip"]["grey"]["bands"], np.array([rec["at"][0] + c[0], rec["at"][1] + c[1], 1.0]))
    levels = (e, wet, storm)
    rng = np.random.default_rng(W["seed"])
    du, dv, n, toward = frame(BI.FIX)
    crest = c + du * W["hull"]["crestAt"][0] + dv * W["hull"]["crestAt"][1]

    X, Y, h = surface(W, crest, du, dv, rng)
    high = mesh_of("W-high", X, Y, h, W["hull"]["footM"])
    H = W["hull"]

    def z_at(p):  # the hull's height at a point of the plan, without its swells
        q = p - crest
        u, v = q @ du, q @ dv
        a, b = (H["stossM"] if u < 0 else H["leeM"]), (H["landM"] if v < 0 else H["seaM"])
        return float(profile(((abs(u) / a) ** H["plan"] + (abs(v) / b) ** H["plan"]) ** (1 / H["plan"]), H))

    lo = np.array([X.min() - 1, Y.min() - 1, H["footM"] - 1])
    hi = np.array([X.max() + 1, Y.max() + 1, H["crestM"] + 1])
    spacing = PT.families(BI.FIX)["foliation"]["spacingM"]
    cut(high, sheets(W, X, Y, h, n, spacing, wet, lo, hi, rng), W["solver"])
    tree = BVHTree.FromPolygons([v.co.copy() for v in high.data.vertices], [p.vertices[:] for p in high.data.polygons])

    def surf(p):  # the sheeted back's height at a point of the plan, or None off the rock
        hit = tree.ray_cast(Vector((p[0], p[1], hi[2])), Vector((0, 0, -1)))[0]
        return hit.z if hit is not None and hit.z > H["footM"] + 0.05 else None

    bodies, walls = cutters(W, crest, lambda p: surf(p) if surf(p) is not None else z_at(p), du, dv, n, toward, lo, hi, rng)
    cut(high, bodies + lips(W, crest, surf, du, dv, n, walls, lo, hi, rng), W["solver"])
    high.data.set_sharp_from_angle(angle=np.radians(W["sharpDeg"]))
    for p in high.data.polygons:
        p.use_smooth = True

    G = K["tip"]["grey"]["values"]
    mats = [BI.material(nm, *G[nm]) for nm in shore.BANDS]
    carve.bands(high, mats, levels)
    obs = [high]
    if BI.arg("--bake"):
        baked = [BI.material(nm + "-baked", *G[nm]) for nm in shore.BANDS]
        low = carve.game(high, int(C["game"]["trisPerM2"] * rec["width"] * rec["depth"]), C["game"])
        carve.bands(low, baked, levels)
        carve.unwrap(low)
        carve.bake(high, low, out, "W", C["bake"])
        obs.append(low)
    for ob in obs:
        ob.location = (rec["at"][0], rec["at"][1], 0.0)
    bpy.context.view_layer.update()
    json.dump({"levels": levels, "high": len(high.data.polygons), "game": len(obs[-1].data.polygons) if len(obs) > 1 else 0},
              open(os.path.join(out, "W.json"), "w"))
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(out, "W.blend"))
    print(f"[whaleback] high {len(high.data.polygons)} faces" + (f", game {len(obs[1].data.polygons)}" if len(obs) > 1 else "")
          + f"; wrote {out}")


if __name__ == "__main__":
    main()
