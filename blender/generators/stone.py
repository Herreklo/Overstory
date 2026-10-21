"""Stone, laid from its facts (docs/stone.md, How stone is made, step 4): the pieces (blender/parts/stone/) fitted
by the era's rules to the plan's paths, each seeded, then the piece's diary applied: the hollow and the polish its
footfall wore, lichen on what is quiet for as many years as the stone has been bare, moss where it is damp and
sheltered, water held where it is hollow, and the repairs, each from its year.

The first: the gully steps (docs/experiments.md, LT1, the second part), split slabs of the town's slaty rock, each
step resting on the one below.

    blender -b --factory-startup --python blender/generators/stone.py -- gully [unity project dir]

Writes unity/Assets/Art/Stone/<name>.fbx and, beside it, <name>.json (the street origin the mesh is laid from).

Per vertex the shader reads (docs/stone.md, The history layers): UV4 x polish (0 to 1), y lichen (its years over 200),
UV5 x moss (how damp and sheltered, 0 to 1), y water held (0 to 1); UV0 the stone's grain (the top in metres, the
split faces round and up); UV1 x the stone's years since it was laid or relaid (over 200), y a seed for the piece;
UV2 x which face (0 top, 1 rounded edge, 2 split face, 3 bed), y the slab's own variation (0 to 1); UV3 the bake (x what
it sees of the sky within the flight, y of the ground).
"""

import json
import math
import os
import random
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "parts", "stone", "slate"))
sys.path.insert(0, os.path.join(HERE, "..", "blockouts"))
import slab as SL  # noqa: E402
import growth as GR  # noqa: E402

YEAR = 1989

# The stones a pack brings (docs/stone.md, A setting pack's stone): how fast each wears under feet (mm a century at
# 100,000 footfalls a year: granite about 1.5 to 3, soft stone about 15; the slaty rock between, unverified). What
# grows on it is nature's (growth.py; the pack's species, GrowthPack).
STONES = {
    "slate": dict(wear=8.0),
}

# The flights authored for the beauty corner until the engine's fabric pass has them (docs/engine-requests.md, 6):
# the plan's path, the stone, the year laid, the footfall a year, and dated events.
FLIGHTS = {
    "gully": dict(lane="Gully Steps", stone="slate", built=1874, built_as="tread_on_riser", footfall=50000,
                  events=[dict(kind="relaid", flight=0, step=9, year=1952)]),
}

RISE = 0.17          # the steps' rise, about (outdoor steps 12 to 16 cm, steeper in a gully)
LAP = 0.10           # how far a tread reaches under the riser of the step above
JOINT = (0.004, 0.012)    # (wide joints showed the void under the treads as black slots)
# how a step is built (a fact of the flight, by its era and its stone): a tread slab laid on a riser set on edge,
# the tread's nosing standing out over the riser (a dark line under every step, from close by and from the city
# camera alike); or one thick block a step, its front the riser
BUILT = {
    "tread_on_riser": dict(tread=(0.10, 0.14), overhang=(0.02, 0.04), riser=(0.07, 0.09)),
    "block": dict(bed=0.06),
}


def h01(*k):
    return random.Random("-".join(str(x) for x in k)).random()


def flights_of(lane):
    """The plan's path as flights: each segment steep enough for steps (a rise over its run of 6% or more)."""
    out = []
    for (ax, ay, az), (bx, by, bz) in zip(lane["pts"], lane["pts"][1:]):
        run = math.hypot(bx - ax, by - ay)
        if run < 0.1 or abs(bz - az) / run < 0.06:
            continue
        out.append(dict(a=np.array([ax, ay, az], float), b=np.array([bx, by, bz], float), width=lane["width"]))
    return out


def widths(rng, total, below, lo=0.7, hi=2.3):
    """A course of slabs across the flight: one or two, now and then three, each its own width and its joint wherever
    the slab broke, kept away from the joints below (a joint is bridged, as a mason lays them; three or four to a
    tread in a regular bond read as brickwork)."""
    for _ in range(40):
        k = rng.choice((1, 2, 2, 2, 3)) if total > 2.2 else rng.choice((1, 1, 2))
        cuts = sorted(rng.uniform(0.18, 0.82) * total for _ in range(k - 1))
        edges = [0.0] + cuts + [total]
        ws = np.diff(edges)
        if ws.min() < lo or ws.max() > hi:
            continue
        if all(min((abs(c - b) for b in below), default=9.0) > 0.3 for c in cuts):
            return edges
    return edges


def walking(a):
    """Where people walk across a flight (0 one side, 1 the other): mostly the middle, in two lanes, up and down,
    never the very edges; 1 at the busiest."""
    # (on a flight 3.2 m wide people keep to the middle metre and a half to two; its edges stay quiet)
    p = 0.55 * np.exp(-((a - 0.4) / 0.12) ** 2) + 0.55 * np.exp(-((a - 0.6) / 0.12) ** 2) + 0.15 * np.exp(-((a - 0.5) / 0.22) ** 2)
    return np.clip(p / 0.71, 0.0, 1.0)


def settle(rng, P, w):
    """A piece settled a little since it was laid: turned, tilted, sunk, each its own way."""
    P = P.copy()
    yaw = math.radians(rng.uniform(-1.0, 1.0))
    cy, sy = math.cos(yaw), math.sin(yaw)
    px, py = P[:, 0] - w / 2, P[:, 1].copy()
    P[:, 0] = px * cy - py * sy + w / 2
    P[:, 1] = px * sy + py * cy
    P[:, 2] += (P[:, 0] - w / 2) * math.radians(rng.uniform(-1.0, 1.0)) - rng.uniform(0.0, 0.01)
    return P


def lay(spec, seed=1):
    """The flights of one stair, laid and aged. Returns a list of (name, mesh dict), and the street origin."""
    import heart_layout as H
    lane = next(l for l in H.LANES if l["name"] == spec["lane"])
    stone = STONES[spec["stone"]]
    how = spec.get("built_as", "tread_on_riser")
    fl = flights_of(lane)
    origin = fl[0]["a"].copy()
    meshes = []
    for fi, f in enumerate(fl):
        a, b, W = f["a"], f["b"], f["width"]
        d2 = (b - a)[:2]
        run = float(np.linalg.norm(d2))
        up = d2 / run                                    # uphill, in plan
        right = np.array([up[1], -up[0]])                # so right, up, z is right-handed
        rise = float(b[2] - a[2])
        n = max(1, int(round(rise / RISE)))
        h, g = rise / n, run / n
        out = dict(V=[], F=[], COL=[], UV0=[], UV1=[], UV2=[], UV3=[])
        below_t, below_r = [], []

        def put(P, piece, rng, x0, s0, z0, laid, foot_on, years):
            """A piece's vertices P (slab space, already turned to the flight: x across, y up the flight, z up),
            set at x0 across, s0 along, z0 up; its history from its facts."""
            kind = piece["kind"]
            across = np.clip((x0 + P[:, 0] + W / 2) / W, 0.0, 1.0)
            along = np.clip((s0 + P[:, 1]) / g - np.floor((s0 + 0.02) / g), 0.0, 1.5)
            top = (kind == 0) & foot_on
            # wear: footfall times years over the stone's hardness, where feet go: across the walking line, on the
            # front half of a tread where the foot lands, and over the nosing, which rounds
            foot = walking(across) * (0.45 + 0.55 * np.exp(-((along - 0.3) / 0.35) ** 2))
            depth_mm = stone["wear"] * (spec["footfall"] / 1e5) * (years / 100.0)
            worn = depth_mm / 1000.0 * foot
            nose = foot_on & ((kind == 1) | ((kind == 0) & (piece["edge"] < 0.03) & (P[:, 1] < 0.05)))
            P = P.copy()
            # (the dish subtracts; the nosing's arris rounds a little more, never bowing the front out)
            P[:, 2] -= np.where(top, worn, 0.0) + np.where(nose, worn * 0.8 * walking(across), 0.0)
            polish = np.where(foot_on & (kind <= 1), np.clip(1.0 - np.exp(-spec["footfall"] * min(years, 40) / 4e5), 0.0, 1.0) * foot, 0.0)
            # growth (nature's, docs/nature.md, Growth on surfaces): lichen where it is quiet for its years; on a
            # riser's face too, above where boots scuff its foot; moss where it stays damp: the strip in front of the
            # riser above (from four fifths of the tread to where the riser stands), the joints between slabs, a
            # riser's foot
            traffic = walking(across) if foot_on else walking(across) * (1.0 - np.clip((z0 + P[:, 2] - zfoot) / 0.05, 0.0, 0.8))
            lichen = GR.lichen_years(years, np.where(foot_on, traffic, traffic * 0.75))
            # the back strip: solid in the last few centimetres before the riser above, fading forward
            back = (kind == 0) & foot_on & (along > 0.72)
            joint = (kind == 0) & (piece["edge"] < 0.05) & (P[:, 1] > 0.04)
            damp = np.where(back, np.clip((along - 0.72) / 0.18, 0.35, 1.0), 0.0) + np.where(joint & ~back, 0.8, 0.0)
            if not foot_on:
                damp = damp + 0.7 * np.clip(1.0 - (z0 + P[:, 2] - zfoot) / 0.04, 0.0, 1.0)
            # (feet land on a tread's front half: its back corner is untrodden even in the middle of a busy flight)
            moss = GR.moss(damp, walking(across) * np.where(foot_on, np.exp(-((np.clip(along, 0, 1) - 0.3) / 0.35) ** 2), 1.0), years)
            # water stands only where the dish is deepest (on slate a few millimetres; half the walking line under water
            # read as white paint from every view)
            held = np.clip((worn - 0.003) / 0.003, 0.0, 1.0) * top
            X = (a[0] - origin[0]) + right[0] * (x0 + P[:, 0]) + up[0] * (s0 + P[:, 1])
            Y = (a[1] - origin[1]) + right[1] * (x0 + P[:, 0]) + up[1] * (s0 + P[:, 1])
            Z = (z0 - origin[2]) + P[:, 2]
            base = sum(len(v) for v in out["V"])
            out["V"].append(np.stack([X, Y, Z], -1))
            out["F"].extend(tuple(base + q for q in face) for face in piece["F"])
            out["COL"].append(np.stack([polish, lichen, moss, np.clip(held, 0, 1)], -1))
            ang = rng.uniform(0, 2 * math.pi)
            off = np.array([rng.uniform(0, 7), rng.uniform(0, 7)])
            uv = np.asarray(piece["UV"], dtype=np.float64)
            c_, s_ = math.cos(ang), math.sin(ang)
            ur = np.stack([uv[:, 0] * c_ - uv[:, 1] * s_, uv[:, 0] * s_ + uv[:, 1] * c_], -1)
            uv = np.where((kind == 0)[:, None], ur + off, uv + off)
            out["UV0"].append(uv)
            var = rng.random()
            out["UV1"].append(np.stack([np.full(len(P), (YEAR - laid) / 200.0), np.full(len(P), var)], -1))
            out["UV2"].append(np.stack([kind.astype(float), np.full(len(P), var)], -1))
            # what each point sees of the sky within the flight (the town's own shade comes from its sky map): a
            # tread open but for its back corner under the riser above; a riser in the shadow of the nosing over it,
            # less towards its top; a bed none
            if foot_on:
                sky = np.where(kind == 0, 0.95 - 0.4 * np.clip((along - 0.75) / 0.25, 0.0, 1.0),
                               np.where(kind == 1, 0.85, np.where(kind == 2, 0.6, 0.1)))
            else:
                hh = np.clip((z0 + P[:, 2] - zfoot) / max(h, 1e-3), 0.0, 1.0)
                sky = np.where(kind == 3, 0.1, 0.78 - 0.25 * hh)
            ground = np.where(kind == 0, 0.12, np.where(kind == 3, 0.6, 0.3))
            out["UV3"].append(np.stack([sky, ground], -1))

        def fill(xc, half, s_a, s_b, z, years, laid):
            """The soil and moss a joint between two slabs fills with: a strip a little below their tops, a little
            wider than the joint, so the joint reads as a damp green-dark line (open, it showed the void under the
            treads as a black slot)."""
            Vq = np.array([[-half, 0.0, 0.0], [half, 0.0, 0.0], [half, s_b - s_a, 0.0], [-half, s_b - s_a, 0.0]])
            piece = dict(V=Vq, F=[(0, 1, 2, 3)], kind=np.zeros(4, dtype=np.int8), edge=np.zeros(4),
                         UV=Vq[:, :2] + xc)
            put(Vq, piece, random.Random(f"fill-{xc:.3f}-{s_a:.3f}"), xc, s_a, z, laid, True, years)

        # each step's top a little off the flight's even line (an old flight's rises are never all alike); its ends on it
        erng = random.Random(f"{spec['lane']}-{seed}-{fi}-rises")
        err = [0.0] + [erng.uniform(-0.012, 0.012) for _ in range(n - 1)] + [0.0]
        for i in range(n):
            rng = random.Random(f"{spec['lane']}-{seed}-{fi}-{i}")
            relaid = next((e for e in spec["events"] if e["kind"] == "relaid" and e["flight"] == fi and e["step"] == i), None)
            laid = relaid["year"] if relaid else spec["built"]
            years = YEAR - laid
            z_top = a[2] + (i + 1) * h + err[i + 1]
            zfoot = a[2] + i * h + err[i]
            if how == "tread_on_riser":
                B = BUILT[how]
                t_tr = rng.uniform(*B["tread"])
                ovh = rng.uniform(*B["overhang"])
                # the riser: a slab on edge, its face the bedding plane, standing on the tread below (or the ground),
                # set back under the nosing
                edges = widths(rng, W, below_r, lo=0.6, hi=2.2)
                below_r = edges[1:-1]
                hr = h - t_tr + 0.03
                for k in range(len(edges) - 1):
                    jl = rng.uniform(*JOINT) / 2 if k > 0 else 0.0
                    jr = rng.uniform(*JOINT) / 2 if k < len(edges) - 2 else 0.0
                    w = edges[k + 1] - edges[k] - jl - jr
                    th = rng.uniform(*B["riser"])
                    piece = SL.slab(f"{spec['lane']}-{seed}-{fi}-{i}-r{k}", w, hr, th, front_round=0.004, side_round=0.004,
                                    flake=0.2, grid=0.16)
                    Q = piece["V"]
                    # slab space (x across, y its height, z its thickness) to the flight: y up, z towards the foot
                    P = np.stack([Q[:, 0], -Q[:, 2] + th, Q[:, 1]], -1)
                    P = np.stack([P[:, 0], P[:, 1], P[:, 2]], -1)
                    P = settle(rng, P, w)
                    s0 = i * g + ovh + rng.uniform(-0.005, 0.005) - th
                    put(P, piece, rng, -W / 2 + edges[k] + jl, s0 + th, zfoot - 0.03 + (t_tr * 0 if i == 0 else 0.0),
                        laid, False, years)
                # the tread: a slab laid on it, its nosing over the riser
                edges = widths(rng, W, below_t)
                below_t = edges[1:-1]
                # an old tread cracked across in places: a fine joint where it broke, its two halves settling apart
                gaps = [rng.uniform(*JOINT) / 2 for _ in edges]
                if not relaid and years > 40:
                    for k in range(len(edges) - 1):
                        if edges[k + 1] - edges[k] > 0.85 and rng.random() < 0.3:
                            c = edges[k] + (edges[k + 1] - edges[k]) * rng.uniform(0.35, 0.65)
                            edges = sorted(edges + [c])
                            gaps = gaps[:k + 1] + [rng.uniform(0.002, 0.004)] + gaps[k + 1:]
                            break
                for k in range(len(edges) - 1):
                    jl = gaps[k] if k > 0 else 0.0
                    jr = gaps[k + 1] if k < len(edges) - 2 else 0.0
                    w = edges[k + 1] - edges[k] - jl - jr
                    depth = g + LAP + rng.uniform(-0.02, 0.03)
                    # split slate: crisp edges, its corners knocked, a layer flaked off here and there (rounded, every
                    # tread read as a bar of soap); its wear rounds the walking line's nosing on its own
                    piece = SL.slab(f"{spec['lane']}-{seed}-{fi}-{i}-{k}", w, depth, t_tr,
                                    front_round=0.002 if relaid else rng.uniform(0.004, 0.008),
                                    side_round=0.002 if relaid else rng.uniform(0.003, 0.006),
                                    flake=0.05 if relaid else rng.uniform(0.3, 0.5),
                                    chip=0.004 if relaid else rng.uniform(0.008, 0.02),
                                    edge_jag=0.004 if relaid else rng.uniform(0.008, 0.014))
                    P = settle(rng, piece["V"], w)
                    put(P, piece, rng, -W / 2 + edges[k] + jl, i * g + rng.uniform(-0.01, 0.01), z_top - t_tr, laid, True, years)
                # the joints between the tread's slabs, filled
                for k in range(1, len(edges) - 1):
                    fill(-W / 2 + edges[k], gaps[k] + 0.008, i * g + 0.005, (i + 1) * g + ovh, z_top - 0.016, years, laid)
            else:
                edges = widths(rng, W, below_t)
                below_t = edges[1:-1]
                for k in range(len(edges) - 1):
                    jl = rng.uniform(*JOINT) / 2 if k > 0 else 0.0
                    jr = rng.uniform(*JOINT) / 2 if k < len(edges) - 2 else 0.0
                    w = edges[k + 1] - edges[k] - jl - jr
                    thick = h + BUILT["block"]["bed"] + rng.uniform(-0.01, 0.02)
                    depth = g + LAP + rng.uniform(-0.02, 0.03)
                    piece = SL.slab(f"{spec['lane']}-{seed}-{fi}-{i}-{k}", w, depth, thick,
                                    front_round=0.004 if relaid else rng.uniform(0.008, 0.02),
                                    side_round=0.003 if relaid else rng.uniform(0.004, 0.01),
                                    flake=0.15 if relaid else rng.uniform(0.25, 0.45))
                    P = settle(rng, piece["V"], w)
                    put(P, piece, rng, -W / 2 + edges[k] + jl, i * g + rng.uniform(-0.012, 0.012), z_top - thick, laid, True, years)
        meshes.append((f"stone_{spec['lane'].lower().replace(' ', '_')}_{fi}",
                       dict(V=np.concatenate(out["V"]), F=out["F"], COL=np.concatenate(out["COL"]),
                            UV0=np.concatenate(out["UV0"]), UV1=np.concatenate(out["UV1"]), UV2=np.concatenate(out["UV2"]),
                            UV3=np.concatenate(out["UV3"]),
                            steps=n, rise=h, tread=g)))
    return meshes, origin


def make(name, m):
    import bpy
    me = bpy.data.meshes.new(name)
    me.from_pydata([tuple(v) for v in m["V"]], [], m["F"])
    me.validate()
    me.update()
    loops = np.zeros(len(me.loops), dtype=np.int64)
    me.loops.foreach_get("vertex_index", loops)
    # the history in UV4 (polish, lichen) and UV5 (moss, water held): floats that arrive as they are (a vertex
    # colour came through Unity's import converted, the baked years shrunk to about half)
    col = np.asarray(m["COL"], np.float64)
    for nm, arr in (("uv0", m["UV0"]), ("uv1", m["UV1"]), ("uv2", m["UV2"]), ("uv3", m["UV3"]), ("uv4", col[:, :2]), ("uv5", col[:, 2:])):
        layer = me.uv_layers.new(name=nm)
        layer.data.foreach_set("uv", np.asarray(arr, np.float32)[loops].ravel())
    me.polygons.foreach_set("use_smooth", [True] * len(me.polygons))
    # split stone has crisp edges: smooth only across gentle turns (a bedding plane's warp, a rounded nosing's steps),
    # sharp across a split (smooth everywhere, every slab read as a cushion)
    me.set_sharp_from_angle(angle=math.radians(32))
    me.update()
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    return ob


def build(which, unity=None, seed=1):
    import bpy
    for ob in list(bpy.data.objects):
        bpy.data.objects.remove(ob, do_unlink=True)
    spec = FLIGHTS[which]
    meshes, origin = lay(spec, seed)
    obs = [make(name, m) for name, m in meshes]
    info = dict(name=f"stone_{which}", origin=[float(v) for v in origin],
                flights=[dict(name=nm, steps=m["steps"], rise=round(m["rise"], 3), tread=round(m["tread"], 3),
                              tris=sum(len(f) - 2 for f in m["F"])) for nm, m in meshes])
    print("STONE", info)
    if unity:
        path = os.path.join(unity, "Assets", "Art", "Stone", f"stone_{which}.fbx")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        bpy.ops.object.select_all(action="DESELECT")
        for ob in obs:
            ob.select_set(True)
        bpy.context.view_layer.objects.active = obs[0]
        bpy.ops.export_scene.fbx(filepath=path, use_selection=True, object_types={"MESH"}, axis_forward="Z",
                                 axis_up="Y", bake_space_transform=True, apply_unit_scale=True,
                                 apply_scale_options="FBX_SCALE_ALL", mesh_smooth_type="OFF", colors_type="LINEAR",
                                 use_mesh_modifiers=False, add_leaf_bones=False, bake_anim=False, path_mode="STRIP",
                                 embed_textures=False)
        with open(path[:-4] + ".json", "w") as fh:
            json.dump(info, fh, indent=1)
        print("FBX", path)
    return info


if __name__ == "__main__":
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    which = argv[0] if argv else "gully"
    unity = argv[1] if len(argv) > 1 else os.path.join(HERE, "..", "..", "unity")
    build(which, unity)
