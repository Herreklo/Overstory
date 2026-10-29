"""The shore block as the ice left it (kit.json `whaleback`): one smooth hull, cut on the rock's own planes.

    Blender -b --factory-startup --python-exit-code 1 -P blender/parts/rock/kit/whaleback.py -- [--bake 1] [--out DIR]

The ice made the big form, so it comes first: a whaleback (roche moutonnee), its long back smooth toward where the ice
came from and falling to the sea. One heightfield hull in the ice's frame (u the way it went, v across it toward the
sea): over a superellipse plan, longer up-ice and seaward, a round cap falling to straight slabs, with a few long low
flutes along the ice's way. Then it is cut,
never smoothed, by exact plane booleans on that clean hull:
- the plucked lee: steep steps down-ice, each block gone above its tread on the sheeting (falling gently down-ice) and
  beyond its front, which crosses the whole width on the planes that cross the ice's way, in strips between J1 joints
  that run on through every step: a J2 face on the sea side, the foliation's riser (leaning back toward its dip), a J3
  face to the land side;
  each lower and further until under the sea; and a few leaves plucked out at the risers' feet between minor J1 joints;
- the main joints across the back (kit.json `cracks`, one a family), narrow straight-sided cracks through the block.
The back's lower edge keeps the hull's own round where the sea washes it; the cut arrises stay crisp. Out: DIR/W.blend
with `W-high` (and with --bake 1 `W-game` and its page, baked as carve.py bakes) in the block's frame at its place.
"""

import json
import os
import sys

import bmesh
import bpy
import numpy as np

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
    return [b for b in bodies if b is not None]


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
    col = bpy.data.collections.new("cuts")
    for i, b in enumerate(cutters(W, crest, z_at, du, dv, n, toward, lo, hi, rng)):
        col.objects.link(bpy.data.objects.new(f"cut{i}", body_mesh(b, f"cut{i}")))
    m = high.modifiers.new("cuts", "BOOLEAN")
    m.operation, m.operand_type, m.collection, m.solver = "DIFFERENCE", "COLLECTION", col, W["solver"]
    carve.applied(high)
    for o in list(col.objects):
        bpy.data.objects.remove(o)
    bpy.data.collections.remove(col)
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
