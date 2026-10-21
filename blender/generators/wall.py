"""Dry-stone walls, laid from their facts (docs/stone.md; docs/upkeep.md; the board: 09, 10, 11, 03): courses of thin
flat stones of the town's slaty rock along a wall's line, every joint bridged, the face battered back about one in
six, slab copings on top, and behind the stones the soil and moss a dry wall holds, so its joints read dark and green,
never as open voids. A wall retains the bank where the ground beside a lane rises, and stands as a parapet where it
falls away. Its history is its own: built with the lane, kept by the town, a bulged panel rebuilt by a crew in depot
stone with cement pointing, and between campaigns stones fallen and left, a hole patched.

The first: the gully steps' cheek walls, along both sides of each flight.

    blender -b --factory-startup --python blender/generators/wall.py -- gully_cheeks [unity project dir]

Writes unity/Assets/Art/Stone/<name>.fbx and <name>.json. The per-vertex channels are the stone's (stone.py): UV0
grain, UV1 (years bare / 200, seed), UV2 (kind, variation), UV3 bake (sky, ground), UV4 (polish, lichen years / 200),
UV5 (moss, water held).
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
import growth as GR  # noqa: E402
import water as WT  # noqa: E402
import wear as WR  # noqa: E402
import slab as SL  # noqa: E402
import wallstone as WS  # noqa: E402
import stone as ST  # noqa: E402

YEAR = ST.YEAR

# The walls authored for the beauty corner until the engine's fabric pass has them (docs/engine-requests.md, 6, 13,
# 14): the lane they line, the stone, when they were built, who kept them and how well, and the works their records
# hold.
WALLS = {
    "gully_cheeks": dict(lane="Gully Steps", stone="slate", built=1874, footfall=ST.FLIGHTS["gully"]["footfall"],
                         upkeep=[dict(by="town", since=1874, care=0.4), dict(by="town", since=1946, care=0.3),
                                 dict(by="town", since=1965, care=0.2)],
                         # (the lane's water ran behind the lower wall on the bank's side until it bulged)
                         works=[dict(kind="rebuilt", year=1961, length=(3.0, 4.5), mortar="cement", stock="reclaimed",
                                     cause="bulged where the lane's water ran behind it")]),
}

BATTER = 1.0 / 6.0      # how far the face leans back for each metre up
COURSE = (0.06, 0.14)   # a course's height: thin flat stones split along their beds
STONE_LEN = (0.18, 0.62)
BRIDGE = 0.08           # a joint is kept at least this far from the joints in the course below
DEPTH = 0.42            # the wall's thickness at its top, under the coping


def ground_near(f, reach=8.0):
    """The heart's carved ground round a flight, on the clay's own 1.5 m grid (blender/blockouts/heart_build.py),
    so the walls meet the bank the clay shows."""
    import centre_land as L
    import heart_build as HB
    import heart_layout as H
    xs = [f["a"][0], f["b"][0]]
    ys = [f["a"][1], f["b"][1]]
    x0 = HB.HX0 + math.floor((min(xs) - reach - HB.HX0) / 1.5) * 1.5
    y0 = HB.HY0 + math.floor((min(ys) - reach - HB.HY0) / 1.5) * 1.5
    X, Y = HB.grid(x0, y0, max(xs) + reach, max(ys) + reach, 1.5)
    Z = H.carve(X, Y, L.heights(X, Y))
    return lambda x, y: float(HB._sample(X, Y, Z, x, y))


def lay(spec, seed=1):
    import heart_layout as H
    lane = next(l for l in H.LANES if l["name"] == spec["lane"])
    fl = ST.flights_of(lane)
    origin = fl[0]["a"].copy()
    meshes = []
    record = []
    lines = []
    for fi, f in enumerate(fl):
        a, b, W = f["a"], f["b"], f["width"]
        d2 = (b - a)[:2]
        run = float(np.linalg.norm(d2))
        up = d2 / run
        right = np.array([up[1], -up[0]])
        rise = float(b[2] - a[2])
        n = max(1, int(round(rise / ST.RISE)))
        h, g = rise / n, run / n
        slope = rise / run
        ground = ground_near(f)
        out = dict(V=[], F=[], COL=[], UV0=[], UV1=[], UV2=[], UV3=[])

        def put(P, kind, uv, rng, bare_y, bed_y, exposed, damp, sky, flip, water=None, touch=None):
            """A piece already placed in the flight's frame (s along, t across, z up), its history from its facts."""
            X = (a[0] - origin[0]) + right[0] * P[:, 1] + up[0] * P[:, 0]
            Y = (a[1] - origin[1]) + right[1] * P[:, 1] + up[1] * P[:, 0]
            Z = P[:, 2] - origin[2]
            base = sum(len(v) for v in out["V"])
            out["V"].append(np.stack([X, Y, Z], -1))
            out["F"].extend(tuple(base + q for q in (reversed(face) if flip else face)) for face in uv["F"])
            # touch: hands on a coping at hand height, boots at a wall's foot (the uses' other contacts): polish
            # where it is touched, and no lichen
            touch = np.zeros(len(P)) if touch is None else np.clip(touch, 0.0, 1.0)
            lichen = GR.lichen_years(bare_y, touch, exposed)
            lichen = np.where(kind == 6, 0.0, lichen)
            moss = GR.moss(damp, np.zeros(len(P)), np.where((kind == 6) | (kind == 4), bed_y, bare_y))
            out["COL"].append(np.stack([touch * 0.85, lichen, moss, np.zeros(len(P))], -1))
            off = np.array([rng.uniform(0, 7), rng.uniform(0, 7)])
            out["UV0"].append(uv["UV"] + off)
            var = rng.random()
            out["UV1"].append(np.stack([np.full(len(P), bare_y / 200.0), np.full(len(P), var)], -1))
            # the water layer: how much water lies or runs here (see the copings and the courses below)
            out["UV2"].append(np.stack([kind.astype(float), np.clip(water if water is not None else np.full(len(P), 0.2), 0, 1)], -1))
            out["UV3"].append(np.stack([sky, np.full(len(P), 0.3)], -1))

        # (one panel was rebuilt, on the side whose bank stands highest: the water ran behind that wall)
        rise_of = {sd: np.mean([ground(*(a[:2] + up * s_ + right * sd * (W / 2 + 2.5))) - (a[2] + s_ * slope)
                                for s_ in np.linspace(0, run, 6)]) for sd in (1, -1)}
        bank_side = max(rise_of, key=rise_of.get)
        for side in (1, -1):
            # the bank beside the flight: retained where it rises, a parapet where it falls away
            ss = np.linspace(-0.3, run + 0.3, max(8, int(run / 0.5)))

            def step_top(s):
                return a[2] + np.clip(np.floor(np.asarray(s) / g) + 1, 0, n) * h

            # (the ground just behind the wall, where it stands: a retaining wall holds what is there; until the
            # corner's own ground is built the clay is that ground)
            bank = np.array([ground(*(a[:2] + up * s + right * side * (W / 2 + 0.7))) for s in ss])
            st_ = step_top(ss)
            retain = bank > st_ + 0.5
            top_line = np.where(retain, np.minimum(bank + 0.05, st_ + 3.0), st_ + 0.9)
            # a wall's top runs in straight rakes between a few breaks, never following every wobble of the ground
            kb = np.linspace(0, len(ss) - 1, max(3, int(run / 3.0))).astype(int)
            top_line = np.interp(np.arange(len(ss)), kb, top_line[kb])
            top = lambda s: float(np.interp(s, ss, top_line))
            # (its line, for the frames: the clay bank behind a retaining stretch is raised to meet its top)
            lines.append(dict(flight=fi, side=side, a=[float(v) for v in a], up=[float(v) for v in up],
                              width=float(W), s=[round(float(v), 3) for v in ss], top=[round(float(v), 3) for v in top_line],
                              retain=[bool(v) for v in retain]))
            # its foot below the steps' line (the courses run parallel to the flight, from a raked base)
            base = lambda s: a[2] + s * slope - 0.18
            wrng = random.Random(f"{spec['lane']}-wall-{seed}-{fi}-{side}")
            # the rebuilt panel: where the lane's water ran behind the lower wall on the bank's side
            panel = None
            for w in spec["works"]:
                if w["kind"] == "rebuilt" and side == bank_side and fi == 0:
                    L_ = wrng.uniform(*w["length"])
                    s0 = wrng.uniform(0.15, 0.35) * run
                    panel = dict(s=(s0, s0 + L_), year=w["year"], mortar=w["mortar"])
                    record.append(dict(flight=fi, side=side, rebuilt=[round(s0, 2), round(s0 + L_, 2)], year=w["year"]))
            # patchwork between: a few stones fallen and left (care falling), one hole patched in cement
            fallen = [wrng.uniform(0.0, run) for _ in range(wrng.randint(1, 3))]
            patched = wrng.uniform(0.0, run)
            # the copings' layout first: their joints and low ends are where the water off the top runs down the face
            crng0 = random.Random(f"{spec['lane']}-copelay-{seed}-{fi}-{side}")
            copes, s_c = [], -0.3
            while s_c < run + 0.3:
                e_c = min(s_c + crng0.uniform(0.45, 1.0), run + 0.3)
                copes.append((s_c, e_c))
                s_c = e_c
            # (water off the copings drips at their joints and at a few low points along their fronts)
            drip_list = WT.drips([e_c for _, e_c in copes[:-1]], [crng0.uniform(0.4, 1.0) for _ in copes[:-1]]) + \
                WT.drips([crng0.uniform(-0.3, run + 0.3) for _ in range(int(run / 1.5) + 1)],
                         [crng0.uniform(0.2, 0.6) for _ in range(int(run / 1.5) + 1)])

            # how much people lean on this wall: a parapet at hand height beside a steep flight is the stair's
            # handrail
            use = float(np.clip(slope * 1.6, 0.3, 1.0)) * (spec.get("footfall", 50000) / 50000.0) ** 0.5

            def face_water(sv, zv):
                """Water down a wall's face (water.py): streaks under the copings' drips, the splash at its foot."""
                tops = np.array([top(q) for q in sv])
                bases = np.array([base(q) for q in sv])
                return WT.down_face(sv, tops - zv, zv - bases, drip_list)
            # the courses
            z = 0.0
            below = []
            k = 0
            while True:
                ch = wrng.uniform(*COURSE)
                s_cur = -0.3
                joints = []
                while s_cur < run + 0.3:
                    for _ in range(20):
                        L_ = wrng.uniform(*STONE_LEN)
                        e = s_cur + L_
                        if all(abs(e - j) > BRIDGE for j in below) or e > run + 0.3:
                            break
                    e = min(e, run + 0.3)
                    sm = (s_cur + e) / 2
                    zb = base(sm) + z
                    if zb + ch * 0.5 > top(sm) - 0.08:        # (the coping takes over)
                        s_cur = e
                        continue
                    in_panel = panel is not None and panel["s"][0] <= sm <= panel["s"][1]
                    gone = any(abs(sm - fs) < 0.25 for fs in fallen) and z > 0.3 and wrng.random() < 0.35
                    srng = random.Random(f"{spec['lane']}-ws-{seed}-{fi}-{side}-{k}-{s_cur:.3f}")
                    if not gone:
                        stn = WS.face_stone(f"{fi}{side}{k}{s_cur:.3f}", e - s_cur - 0.006, ch - 0.004,
                                            depth=0.06, bulge=srng.uniform(0.003, 0.009),
                                            jag=srng.uniform(0.004, 0.01), chip=srng.uniform(0.006, 0.016))
                        V = stn["V"]
                        hgt = zb + V[:, 1]
                        setback = (hgt - base(sm)) * BATTER
                        sv = s_cur + 0.003 + V[:, 0]
                        tv = side * (W / 2 + 0.006 + setback - V[:, 2] + srng.uniform(-0.004, 0.006))
                        zv = hgt + (sv - sm) * slope
                        P = np.stack([sv, tv, zv], -1)
                        bare = YEAR - (panel["year"] - srng.randint(15, 40) if in_panel else spec["built"])
                        exposed = np.clip(0.4 + 0.6 * (hgt - base(sm)) / max(top(sm) - base(sm), 0.3), 0.3, 1.0)
                        damp = np.clip(1.0 - (hgt - base(sm)) / 0.35, 0.0, 1.0) * 0.8
                        sky = np.full(len(P), 0.7)
                        # (boots scuff a wall's face just above each tread, most where the flight is steep)
                        above = zv - step_top(sv)
                        scuff = WR.boots(above, use)
                        put(P, stn["kind"], dict(F=stn["F"], UV=np.stack([V[:, 0], V[:, 1] + z], -1)), srng,
                            bare, YEAR - (panel["year"] if in_panel else spec["built"]), exposed, damp, sky,
                            flip=(side == 1), water=face_water(sv, zv), touch=scuff)
                        # where it stands free (a parapet over the drop), its back is a face too
                        if not bool(np.interp(sm, ss, retain.astype(float)) > 0.5):
                            tb = side * (W / 2 + 0.006 + DEPTH - setback + V[:, 2] + srng.uniform(-0.004, 0.006))
                            Pb = np.stack([sv, tb, zv], -1)
                            put(Pb, stn["kind"], dict(F=stn["F"], UV=np.stack([V[:, 0] + 3.1, V[:, 1] + z], -1)), srng,
                                bare, YEAR - spec["built"], exposed, damp, sky, flip=(side == -1),
                                water=face_water(sv, zv))
                    joints.append(e)
                    s_cur = e
                below = joints
                z += ch
                k += 1
                if base(run / 2) + z > max(top_line) + 0.1 or k > 60:
                    break
            # the backing: soil and moss in the joints, a few centimetres behind the face, where the dry wall holds
            # them (in the rebuilt panel and the patched hole, cement pointing)
            nb = max(4, int(run / 0.25))
            sb = np.linspace(-0.3, run + 0.3, nb)
            for j in range(nb - 1):
                for zf0, zf1 in ((0.0, 0.5), (0.5, 1.0)):
                    s_a, s_b = sb[j], sb[j + 1]
                    sm = (s_a + s_b) / 2
                    in_panel = panel is not None and panel["s"][0] <= sm <= panel["s"][1]
                    cem = in_panel or abs(sm - patched) < 0.35
                    zz = [base(s_a) + (top(s_a) - base(s_a)) * zf0, base(s_b) + (top(s_b) - base(s_b)) * zf0,
                          base(s_b) + (top(s_b) - base(s_b)) * zf1, base(s_a) + (top(s_a) - base(s_a)) * zf1]
                    ssq = [s_a, s_b, s_b, s_a]
                    tt = [side * (W / 2 + 0.006 + (zq - base(sq)) * BATTER + (0.012 if cem else 0.035))
                          for zq, sq in zip(zz, ssq)]
                    P = np.array([[ssq[q], tt[q], zz[q]] for q in range(4)])
                    kind = np.full(4, 4 if cem else 6, dtype=np.int8)
                    hgt = P[:, 2] - np.array([base(q) for q in ssq])
                    damp = np.clip(1.0 - hgt / 0.8, 0.35, 1.0)
                    yrs = YEAR - (panel["year"] if in_panel else (1979 if cem else spec["built"]))
                    put(P, kind, dict(F=[(0, 1, 2, 3)], UV=P[:, [0, 2]]), random.Random(f"back-{fi}-{side}-{j}-{zf0}"),
                        yrs, yrs, np.full(4, 0.5), damp, np.full(4, 0.45), flip=(side == 1), water=np.full(4, WT.HOLDS))
            # the copings: slabs laid flat along the top, their fronts a little proud of the face
            for c, (s_cur, e) in enumerate(copes):
                sm = (s_cur + e) / 2
                thick = wrng.uniform(0.07, 0.1)
                crng = random.Random(f"{spec['lane']}-cope-{seed}-{fi}-{side}-{c}")
                pc = SL.slab(f"{spec['lane']}-cope-{fi}-{side}-{c}", e - s_cur - 0.008, DEPTH, thick,
                             front_round=crng.uniform(0.004, 0.009), side_round=0.004, flake=0.3,
                             chip=crng.uniform(0.01, 0.025), edge_jag=crng.uniform(0.008, 0.014), layers=2)
                V = pc["V"]
                zt = top(sm) - thick
                face_t = W / 2 + 0.006 + (top(sm) - base(sm)) * BATTER - crng.uniform(0.015, 0.035)
                sv = s_cur + 0.004 + V[:, 0]
                tv = side * (face_t + V[:, 1])
                zv = zt + V[:, 2] + (sv - sm) * slope
                P = np.stack([sv, tv, zv], -1)
                along = np.clip(V[:, 1] / DEPTH, 0.0, 1.0)
                damp = np.where(pc["kind"] == 0, np.clip((along - 0.75) / 0.25, 0.0, 1.0) * 0.6, 0.0)
                sky = np.where(pc["kind"] == 0, 0.95, np.where(pc["kind"] == 3, 0.35, 0.75))
                in_panel = panel is not None and panel["s"][0] <= sm <= panel["s"][1]
                bare = YEAR - (panel["year"] - crng.randint(15, 40) if in_panel else spec["built"])
                # (a coping is laid with a fall to the bank: water lingers at its back and in its joints, its crown
                # dries first; its front face takes the drip)
                xin = np.minimum(V[:, 0], (e - s_cur) - V[:, 0])
                w_cope = np.where(pc["kind"] == 0, np.clip(np.maximum(np.clip((along - 0.6) / 0.4, 0, 1),
                                                                      np.clip(1.0 - xin / 0.05, 0, 1) * 0.8), 0.12, 1.0),
                                  np.where(pc["kind"] == 2, 0.5, 0.3))
                # hands on the coping's inner edge where it is at hand height above the steps (about 0.95 m)
                hand = WR.hands(top(sm) - float(step_top(sm)), 1.0)
                edge_in = np.where(pc["kind"] == 0, np.clip(1.0 - V[:, 1] / 0.12, 0.0, 1.0), np.where(pc["kind"] == 1, 1.0, 0.0))
                put(P, pc["kind"], dict(F=pc["F"], UV=pc["UV"]), crng, bare, YEAR - spec["built"],
                    np.full(len(P), 1.0), damp, sky, flip=(side == 1), water=w_cope, touch=hand * edge_in * use)
        meshes.append((f"stone_{spec['lane'].lower().replace(' ', '_')}_walls_{fi}",
                       dict(V=np.concatenate(out["V"]), F=out["F"], COL=np.concatenate(out["COL"]),
                            UV0=np.concatenate(out["UV0"]), UV1=np.concatenate(out["UV1"]),
                            UV2=np.concatenate(out["UV2"]), UV3=np.concatenate(out["UV3"]))))
    return meshes, origin, record, lines


def build(which, unity=None, seed=1):
    import bpy
    for ob in list(bpy.data.objects):
        bpy.data.objects.remove(ob, do_unlink=True)
    spec = WALLS[which]
    meshes, origin, record, lines = lay(spec, seed)
    obs = [ST.make(name, m) for name, m in meshes]
    info = dict(name=f"stone_{which}", origin=[float(v) for v in origin], works=record, lines=lines,
                walls=[dict(name=nm, tris=sum(len(f) - 2 for f in m["F"])) for nm, m in meshes])
    print("WALLS", info)
    if unity:
        path = os.path.join(unity, "Assets", "Art", "Stone", f"stone_{which}.fbx")
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
    which = argv[0] if argv else "gully_cheeks"
    unity = argv[1] if len(argv) > 1 else os.path.join(HERE, "..", "..", "unity")
    build(which, unity)
