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
sys.path.insert(0, os.path.join(HERE, "..", "parts", "repair"))
import slab as SL  # noqa: E402
import cement as CE  # noqa: E402
import growth as GR  # noqa: E402
import upkeep as UP  # noqa: E402
import water as WT  # noqa: E402
import wear as WR  # noqa: E402
from wear import walking  # noqa: E402

YEAR = 1989

# The stones a pack brings (docs/stone.md, A setting pack's stone): how fast each wears under feet (mm a century at
# 100,000 footfalls a year: granite about 1.5 to 3, soft stone about 15; the slaty rock between, unverified). What
# grows on it is nature's (growth.py; the pack's species, GrowthPack).
STONES = {
    "slate": dict(wear=8.0),
    # dressed granite, brought in for money from about 1870 (docs/research/stone.md): hard, it scarcely hollows
    "granite": dict(wear=2.0),
}

# The flights authored for the beauty corner until the engine's fabric pass has them (docs/engine-requests.md, 6):
# the plan's path, the stone, the year laid, the footfall a year, who kept it and how well, decade by decade, and the
# works its records hold (upkeep.py; docs/upkeep.md).
FLIGHTS = {
    "gully": dict(lane="Gully Steps", stone="slate", built=1874, built_as="block", footfall=50000,
                  upkeep=[dict(by="town", since=1874, care=0.5), dict(by="town", since=1930, care=0.3),
                          dict(by="town", since=1946, care=0.45), dict(by="town", since=1965, care=0.25)],
                  works=[dict(kind="campaign", year=1911, share=0.25),
                         dict(kind="campaign", year=1952, share=0.4, mortar="cement", stock="reclaimed")]),
}

RISE = 0.17          # the steps' rise, about (outdoor steps 12 to 16 cm, steeper in a gully)
LAP = 0.10           # how far a tread reaches under the riser of the step above
JOINT = (0.004, 0.012)    # (wide joints showed the void under the treads as black slots)
# how a step is built (a fact of the flight, by its era and its stone): a tread slab laid on a riser set on edge,
# the tread's nosing standing out over the riser (a dark line under every step, from close by and from the city
# camera alike); or one thick block a step, its front the riser
BUILT = {
    # (a slab-on-riser step is mostly riser: its rough split face 10 to 12 cm tall under a tread 6 to 8 cm thick, the
    # nosing 2 to 3 cm proud; thick treads over recessed risers read as shelves over black slots)
    "tread_on_riser": dict(tread=(0.06, 0.08), overhang=(0.02, 0.03), riser=(0.16, 0.24)),
    "block": dict(bed=0.06),
}


def h01(*k):
    return random.Random("-".join(str(x) for x in k)).random()


STRIDE = 0.63        # two rises and a going: a person's stride on a stair (Blondel's rule)
GOING_MIN = 0.26     # a going a foot fits on
RISE_MAX = 0.20      # the most a person climbs in one step
RAMP_MIN = 0.10      # below this slope a way is paved, not stepped
STEP_RAMP = 0.18     # below this slope a stair is a step-ramp (a trappegate): a going of one or two strides, low risers


def flights_of(lane):
    """The plan's path as flights: each segment steep enough for steps, always laid uphill (a segment the plan draws
    downhill is reversed: built as it was drawn, one went down as a single long slab), with its rise and going chosen
    together by the stride; a gentle segment a step-ramp; one steeper than a person can climb flagged as the plan's
    fault, never built as a ladder."""
    out = []
    for (ax, ay, az), (bx, by, bz) in zip(lane["pts"], lane["pts"][1:]):
        run = math.hypot(bx - ax, by - ay)
        if run < 0.1:
            continue
        if bz < az:
            (ax, ay, az), (bx, by, bz) = (bx, by, bz), (ax, ay, az)
        slope = (bz - az) / run
        if slope < RAMP_MIN:
            continue
        f = dict(a=np.array([ax, ay, az], float), b=np.array([bx, by, bz], float), width=lane["width"])
        if slope < STEP_RAMP:
            # a step-ramp: a going of one stride or two (so no one breaks step), its riser what the slope gives
            k = 1 if slope * 0.65 >= 0.09 else 2
            n = max(1, int(round(run / (0.65 * k))))
            f["form"] = "step_ramp"
        else:
            going = STRIDE / (1.0 + 2.0 * slope)
            if going < GOING_MIN or slope * GOING_MIN > RISE_MAX:
                f["flag"] = f"too steep for steps: {slope:.2f} over {run:.1f} m (the plan's fault)"
                going = GOING_MIN
            n = max(1, int(round(run / going)))
            f["form"] = "stair"
        f["n"] = n
        out.append(f)
    return out


def widths(rng, total, below, lo=0.7, hi=2.3, below2=(), ks=None):
    """A course of slabs across the flight: one or two, now and then three, each its own width and its joint wherever
    the slab broke, kept away from the joints below (a joint is bridged, as a mason lays them; three or four to a
    tread in a regular bond read as brickwork)."""
    for _ in range(40):
        k = rng.choice(ks) if ks else (rng.choice((1, 2, 2, 2, 3)) if total > 2.2 else rng.choice((1, 1, 2)))
        cuts = sorted(rng.uniform(0.18, 0.82) * total for _ in range(k - 1))
        edges = [0.0] + cuts + [total]
        ws = np.diff(edges)
        if ws.min() < lo or ws.max() > hi:
            continue
        # (and off the line the two rows below make: joints drifting the same way step after step lined up into a
        # diagonal seam that read as a fissure)
        drift = [2 * b - b2 for b in below for b2 in below2 if abs(b - b2) < 0.6]
        if all(min((abs(c - b) for b in below), default=9.0) > 0.3 for c in cuts) and \
                all(min((abs(c - d) for d in drift), default=9.0) > 0.2 for c in cuts):
            return edges
    return edges


def settler(rng, w, off):
    """How a piece has settled since its bed was laid: turned, tilted, sunk, each its own way, by as much as its bed
    has gone off true (upkeep.py) and a mason's own few millimetres. Returns the transform for the piece's vertices
    (dx: where they sit in the frame of the slab they belong to, for the halves of one that cracked)."""
    k = min(off / 0.012, 1.6)
    # (a step sinks and tilts on its bed; it scarcely turns in plan: turned, the bottom step read as a tapering tongue)
    yaw = math.radians(rng.uniform(-1.0, 1.0) * 0.25 * k)
    tilt = math.radians(rng.uniform(-1.0, 1.0) * 0.9 * k)
    sink = rng.uniform(0.3, 1.0) * off
    cy, sy = math.cos(yaw), math.sin(yaw)

    def tf(V, dx=0.0):
        P = np.array(V, dtype=np.float64, copy=True)
        px, py = P[:, 0] + dx - w / 2, P[:, 1].copy()
        P[:, 0] = px * cy - py * sy + w / 2 - dx
        P[:, 1] = px * sy + py * cy
        P[:, 2] += px * tilt - sink
        return P
    return tf


def top_line(placed, x, s_vals, reach=0.04):
    """The height of the stone's top along a joint at x across, at each s along the flight: the highest of the placed
    tops within reach of it (pointing is struck to the stone either side)."""
    z = np.full(len(s_vals), -1e9)
    for P in placed:
        near = np.abs(P[:, 0] - x) < reach
        if not near.any():
            continue
        Q = P[near]
        for j, s in enumerate(s_vals):
            m = np.abs(Q[:, 1] - s) < 0.05
            if m.any():
                z[j] = max(z[j], float(Q[m, 2].max()))
    return z


def lay(spec, seed=1):
    """The flights of one stair, laid and aged: each step from its life (upkeep.py), so its bed, its joints and its
    slabs carry their own years, and its repairs are spread over the flight as the years left them. Returns a list of
    (name, mesh dict), and the street origin."""
    import heart_layout as H
    lane = next(l for l in H.LANES if l["name"] == spec["lane"])
    stone = STONES[spec["stone"]]
    how = spec.get("built_as", "tread_on_riser")
    fl = flights_of(lane)
    origin = fl[0]["a"].copy()
    meshes = []
    flags = []
    # the stair's facts the whole of it shares: the side its walking line keeps to, how well it is kept now, and on
    # which flight each campaign fell (one campaign a stair, on the flight its cause chose: the wettest and longest)
    lean = spec.get("lean", random.Random(f"{spec['lane']}-lean").uniform(-0.8, 0.8))
    care_now = UP.keeper_in(spec["upkeep"], YEAR - 1)["care"]
    crng = random.Random(f"{spec['lane']}-{seed}-campaigns")
    built_fl = [k for k, f in enumerate(fl) if not f.get("flag")]
    campaign_flight = {}
    for w in spec["works"]:
        if w["kind"] == "campaign" and built_fl:
            campaign_flight[id(w)] = crng.choices(built_fl, weights=[fl[k]["n"] for k in built_fl])[0]
    for fi, f in enumerate(fl):
        a, b, W = f["a"], f["b"], f["width"]
        d2 = (b - a)[:2]
        run = float(np.linalg.norm(d2))
        up = d2 / run                                    # uphill, in plan
        right = np.array([up[1], -up[0]])                # so right, up, z is right-handed
        rise = float(b[2] - a[2])
        n = f["n"]
        h, g = rise / n, run / n
        if f.get("flag"):
            # (not built: a ladder of stone tells a false story; the plan is fixed instead)
            print("PLAN FLAG", spec["lane"], fi, f["flag"])
            flags.append(dict(flight=fi, flag=f["flag"]))
            continue
        out = dict(V=[], F=[], COL=[], UV0=[], UV1=[], UV2=[], UV3=[])
        below_r = []
        trod = WR.busy(spec["footfall"], W)

        # the treads' slabs as the mason laid them (every joint bridged), then the flight's life over them: the
        # bottom steps take the most water into their beds, and loads are dropped where people go
        plan, below, below2 = [], [], []
        dressed = spec.get("finish") == "dressed"
        rough = spec.get("finish") == "rough"
        for i in range(n):
            prng = random.Random(f"{spec['lane']}-{seed}-{fi}-{i}-plan")
            edges = widths(prng, W, below, below2=below2, hi=3.4, ks=(1, 1, 2)) if dressed else \
                (widths(prng, W, below, below2=below2, lo=0.35, hi=1.1, ks=(2, 3, 3, 4)) if rough else
                 widths(prng, W, below, below2=below2))
            below2, below = below, edges[1:-1]
            plan.append(edges)
        # how much water each step's bed takes: more towards a flight's foot, and most where the lane's water is
        # led onto it (one or two places along it, the stair's own: always the foot, every campaign's run sat there)
        wrng = random.Random(f"{spec['lane']}-{seed}-{fi}-wet")
        sinks = [wrng.uniform(0.0, 1.0) for _ in range(wrng.randint(1, 2))]
        wet = [0.25 + 0.3 * (1.0 - i / max(n - 1, 1)) + max(0.55 * math.exp(-((i / max(n - 1, 1) - c) / 0.15) ** 2)
               for c in sinks) + wrng.uniform(0.0, 0.2) for i in range(n)]
        works_here = [w for w in spec["works"] if w["kind"] != "campaign" or campaign_flight.get(id(w), 0) == fi]
        life = UP.flight([list(zip(e[:-1], e[1:])) for e in plan], spec["built"], YEAR, spec["upkeep"],
                         works_here, f"{spec['lane']}-{seed}-{fi}", wet,
                         busy=lambda x: float(walking(np.array([x / W]), W, lean)[0]))

        def put(P, piece, rng, x0, s0, z0, foot_on, worn_y, bare_y, bed_y, polish0=0.0, lifted_y=None):
            """A piece's vertices P (slab space, already turned to the flight: x across, y up the flight, z up),
            set at x0 across, s0 along, z0 up; its history from its facts: worn_y the years feet have worn it here,
            bare_y the years since its top was bare (lichen, weathering), bed_y the years since its bed and joints
            were last disturbed (moss in them), lifted_y the years since hands last lifted it (its lichen torn where
            they gripped: its edges and faces). Returns it placed in the flight's frame (x, s, z)."""
            kind = piece["kind"]
            cement = kind >= 4
            across = np.clip((x0 + P[:, 0] + W / 2) / W, 0.0, 1.0)
            along = np.clip((s0 + P[:, 1]) / g - np.floor((s0 + 0.02) / g), 0.0, 1.5)
            top = (kind == 0) & foot_on
            # wear (wear.py): footfall times years over the stone's hardness, where feet go: across the walking line,
            # on the front half of a tread where the foot lands, and over the nosing, which rounds
            foot = walking(across, W, lean) * ((0.45 + 0.55 * np.exp(-((along - 0.3) / 0.35) ** 2)) if g < 0.5 else 1.0)
            worn = WR.depth(stone["wear"], spec["footfall"], worn_y, foot, W)
            nose = foot_on & ((kind == 1) | ((kind == 0) & (piece["edge"] < 0.03) & (P[:, 1] < 0.05)))
            P = P.copy()
            # (the dish subtracts; the nosing's arris rounds faster than the tread hollows, never bowing the front out)
            P[:, 2] -= np.where(top, worn, 0.0) + np.where(nose, WR.nosing(worn, walking(across, W, lean)), 0.0)
            polish = np.where(foot_on & ((kind <= 1) | (kind == 5)), WR.polish(spec["footfall"], worn_y, foot), 0.0)
            polish = np.maximum(polish, np.where(foot_on & (kind <= 1), polish0, 0.0))
            # growth (nature's, docs/nature.md, Growth on surfaces): lichen where it is quiet for its years; on a
            # riser's face too, above where boots scuff its foot; moss where it stays damp: the strip in front of the
            # riser above (from four fifths of the tread to where the riser stands), the joints between slabs and
            # their pointing, a riser's foot, for the years since the bed was last disturbed
            traffic = (walking(across, W, lean) if foot_on else walking(across, W, lean) * (1.0 - np.clip((z0 + P[:, 2] - zfoot) / 0.05, 0.0, 0.8))) * trod
            lich_y = bare_y
            if lifted_y is not None and lifted_y < bare_y:
                lich_y = np.where(((kind == 0) & (piece["edge"] < 0.06)) | (kind == 1) | (kind == 2), lifted_y, bare_y)
            # (lichen wants light and to dry out: it hugs a tread's front and nosing and the riser's face, and thins
            # towards the damp back under the riser above, where moss takes over: a pale front and a dark back to
            # every step, as at Dale, the board's 06)
            if foot_on:
                exposed = np.where(kind == 0, np.clip(1.0 - (along - 0.2) / 0.6, 0.25, 1.0), 1.0)
            else:
                exposed = np.full(len(P), 0.8)
            lichen = GR.lichen_years(lich_y, np.where(foot_on, traffic, traffic * 0.75), exposed)
            lichen = np.where(kind == 6, 0.0, lichen)       # (a joint's soil takes moss, never lichen)
            back = (kind == 0) & foot_on & (along > 0.8)
            joint = (kind == 0) & (piece["edge"] < 0.05) & (P[:, 1] > 0.04)
            damp = np.where(back, np.clip((along - 0.8) / 0.15, 0.3, 1.0), 0.0) + np.where(joint & ~back, 1.0, 0.0) \
                + np.where(kind == 4, 1.0, 0.0) + np.where(kind == 5, 0.3, 0.0) + np.where(kind == 6, 1.0, 0.0)
            # (each step its own: how wet its bed is, and luck; the same dash on every step read as a ladder from above)
            damp = damp * step_wet
            if not foot_on:
                damp = damp + 0.7 * np.clip(1.0 - (z0 + P[:, 2] - zfoot) / 0.04, 0.0, 1.0) * step_wet
            else:
                damp = damp + np.where(kind == 2, 0.7 * np.clip(1.0 - (z0 + P[:, 2] - zfoot) / 0.04, 0.0, 1.0) * step_wet, 0.0)
            moss_y = np.where(back | joint | (kind == 4) | (kind == 6) | (not foot_on), min(bare_y, bed_y), bare_y)
            # (feet land on a tread's front half: its back corner is untrodden even in the middle of a busy flight)
            # (moss thins where people walk even at a tread's back and a step's foot: brooms, boots and grit; the green
            # bands at the quiet ends, not a rung across every step)
            # (a tended stair is swept and its joints weeded: its keeper's care now thins the moss; neglect lets it in)
            damp = damp * (1.15 - 0.75 * care_now)
            moss = GR.moss(damp, trod * walking(across, W, lean) * np.where(foot_on & (kind != 6), np.maximum(np.exp(-((np.clip(along, 0, 1) - 0.3) / 0.35) ** 2), 0.7), 1.0), moss_y)
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
            uv = np.where(((kind == 0) | cement)[:, None], ur + off, uv + off)
            out["UV0"].append(uv)
            var = rng.random()
            out["UV1"].append(np.stack([np.full(len(P), bare_y / 200.0), np.full(len(P), var)], -1))
            # the water layer (water.py): on a tread water lingers in the dish, the joints and against the step above,
            # and the crown dries first; the nosing sheds it; a front takes what runs over the nosing above it, most
            # down the worn middle where the dish drains, strongest just under the nosing; a joint's soil holds it
            zz = z0 + P[:, 2]
            water_top = WT.on_top(back=np.where(back, (along - 0.8) / 0.2, 0.0), joint=np.where(joint, 0.8, 0.0),
                                  hollow=worn / 0.004)
            run_over = WT.over_edge(walking(across, W, lean) * 0.9, z_top - zz)
            water = np.where(kind == 0, water_top, np.where(kind == 1, 0.3, np.where(kind == 2, run_over,
                             np.where(kind >= 4, WT.HOLDS, 0.2))))
            if not foot_on:
                water = np.where(kind == 2, run_over, water)
            out["UV2"].append(np.stack([kind.astype(float), np.clip(water, 0.0, 1.0)], -1))
            # what each point sees of the sky within the flight (the town's own shade comes from its sky map): a
            # tread open but for its back corner under the riser above; a riser in the shadow of the nosing over it,
            # less towards its top; a bed none
            if foot_on:
                sky = np.where((kind == 0) | cement, 0.95 - 0.4 * np.clip((along - 0.75) / 0.25, 0.0, 1.0),
                               np.where(kind == 1, 0.75, np.where(kind == 2, 0.7, 0.35)))
            else:
                hh = np.clip((z0 + P[:, 2] - zfoot) / max(h, 1e-3), 0.0, 1.0)
                sky = np.where(kind == 3, 0.35, np.where(kind == 6, 0.6, 0.8 - 0.2 * hh))
            ground = np.where(kind == 0, 0.12, np.where(kind == 3, 0.6, 0.3))
            out["UV3"].append(np.stack([sky, ground], -1))
            return np.stack([x0 + P[:, 0], s0 + P[:, 1], z0 + P[:, 2]], -1)

        def fill(xc, half, s_a, s_b, z, bed_y):
            """The soil and moss a joint between two slabs fills with: a strip a little below their tops, a little
            wider than the joint, so the joint reads as a damp green-dark line (open, it showed the void under the
            treads as a black slot)."""
            Vq = np.array([[-half, 0.0, 0.0], [half, 0.0, 0.0], [half, s_b - s_a, 0.0], [-half, s_b - s_a, 0.0]])
            piece = dict(V=Vq, F=[(0, 1, 2, 3)], kind=np.full(4, 6, dtype=np.int8), edge=np.zeros(4),
                         UV=Vq[:, :2] + xc)
            put(Vq, piece, random.Random(f"fill-{xc:.3f}-{s_a:.3f}"), xc, s_a, z, True, 0, YEAR - spec["built"], bed_y)

        def fill_bed(key, x_a, s_f, length, width, zl, bed_y):
            """Soil and moss along a block's foot, in the bed joint where it stands on the step below."""
            pc = CE.pointing(key, length, width)
            V = pc["V"].copy()
            t = np.clip(V[:, 0] / max(length, 1e-6), 0.0, 1.0)
            V[:, 2] = np.interp(t, np.linspace(0, 1, len(zl)), zl) + 0.001
            pc["kind"] = np.full(len(V), 6, dtype=np.int8)
            put(V, pc, random.Random(key), x_a, s_f, 0.0, True, 0, YEAR - spec["built"], bed_y)

        def fill_front(xc, half, s_f, z0, z1, bed_y, cast=None):
            """The same joint where it comes down a block's front: soil and moss a centimetre in (an open joint read
            as a black slit), or the crew's cement pointing struck to the face."""
            Vq = np.array([[-half, 0.0, 0.0], [half, 0.0, 0.0], [half, 0.0, z1 - z0], [-half, 0.0, z1 - z0]])
            kind_ = 4 if cast is not None else 6
            piece = dict(V=Vq, F=[(0, 1, 2, 3)], kind=np.full(4, kind_, dtype=np.int8), edge=np.zeros(4),
                         UV=np.stack([Vq[:, 0] + xc, Vq[:, 2]], -1))
            yrs = cast if cast is not None else YEAR - spec["built"]
            put(Vq, piece, random.Random(f"front-{xc:.3f}-{s_f:.3f}"), xc, s_f, z0, False, 0,
                yrs, bed_y if cast is None else cast)

        def point(key, x_a, s_a, length, width, along_s, zl, cast_y):
            """Cement pointing struck along a joint, to the stone's top either side (zl, along it): along_s, a joint
            running up the flight at x_a; else one running across it at s_a."""
            pc = CE.pointing(key, length, width)
            V = pc["V"].copy()
            t = np.clip(V[:, 0] / max(length, 1e-6), 0.0, 1.0)
            zz = np.interp(t, np.linspace(0, 1, len(zl)), zl) + 0.0012
            if along_s:
                V = np.stack([V[:, 1], V[:, 0], zz], -1)
                pc["F"] = [tuple(reversed(q)) for q in pc["F"]]
                put(V, pc, random.Random(key), x_a, s_a, 0.0, True, cast_y, cast_y, cast_y)
            else:
                V = np.stack([V[:, 0], V[:, 1], zz], -1)
                put(V, pc, random.Random(key), x_a, s_a, 0.0, True, cast_y, cast_y, cast_y)

        # each step's top a little off the flight's even line (an old flight's rises are never all alike); its ends on it
        erng = random.Random(f"{spec['lane']}-{seed}-{fi}-rises")
        e_ = {"dressed": 0.004, "rough": 0.02}.get(spec.get("finish", "split"), 0.012)
        err = [0.0] + [erng.uniform(-e_, e_) for _ in range(n - 1)] + [0.0]
        prev_tops = []
        for i in range(n):
            rng = random.Random(f"{spec['lane']}-{seed}-{fi}-{i}")
            st = life[i]
            bed_y = YEAR - st["reset"]
            step_wet = float(np.clip(0.35 + 0.75 * wet[i] * random.Random(f"{spec['lane']}-{fi}-{i}-moss").uniform(0.3, 1.3), 0.15, 1.2))
            cemented = bool(st["mortar"]) and st["mortar"][0] == "cement"
            off = st["settled"] + 0.003
            z_top = a[2] + (i + 1) * h + err[i + 1]
            zfoot = a[2] + i * h + err[i]
            if how == "block":
                # one thick split slab a step, its front split face the riser, resting on the back of the one below
                # (the board's 05 and 06; block steps, docs/research/stone.md); the first set into the ground
                t_tr = h + BUILT["block"]["bed"] + rng.uniform(-0.01, 0.02) + (0.2 if i == 0 else 0.0)
                ovh = 0.0
            else:
                B = BUILT["tread_on_riser"]
                t_tr = rng.uniform(*B["tread"])
                ovh = rng.uniform(*B["overhang"])
                # the riser: a block of the rock laid on its bed on the tread below (or the ground), its rough split
                # face to the lane, nearly flush under the nosing
                edges_r = widths(rng, W, below_r, lo=0.6, hi=2.2)
                below_r = edges_r[1:-1]
                hr = (z_top - t_tr) - zfoot + 0.004     # (cut to meet its tread: set to a standard height, sky showed between)
                # (the first step's riser is set into the ground, as a mason sets it, so the lane meets a block and
                # not its bed)
                sunk = 0.2 if i == 0 else 0.0
                for k in range(len(edges_r) - 1):
                    jl = rng.uniform(*JOINT) / 2 if k > 0 else 0.0
                    jr = rng.uniform(*JOINT) / 2 if k < len(edges_r) - 2 else 0.0
                    w = edges_r[k + 1] - edges_r[k] - jl - jr
                    dep = rng.uniform(*B["riser"])
                    # (bedded a little into the step below: the slab below settles further than the riser on it, and
                    # sky showed under the riser's foot)
                    piece = SL.slab(f"{spec['lane']}-{seed}-{fi}-{i}-r{k}", w, dep, hr + sunk + 0.03, front_round=rng.uniform(0.002, 0.006),
                                    side_round=0.003, flake=0.1, chip=rng.uniform(0.006, 0.015), edge_jag=0.008, grid=0.16)
                    P = settler(rng, w, off * 0.5)(piece["V"])
                    put(P, piece, rng, -W / 2 + edges_r[k] + jl, i * g + ovh + rng.uniform(-0.004, 0.004), zfoot - sunk - 0.03, False,
                        YEAR - spec["built"], YEAR - spec["built"], bed_y)
            # the bed line at a block's foot, where it stands on the step below: soil and moss where no crew pointed
            # it (lime pointing washes out in a few decades; the board, 06)
            if how == "block" and not cemented and prev_tops:
                s_f = i * g + 0.004
                xs = np.linspace(-W / 2, W / 2, 24)
                zl = np.array([top_line(prev_tops, x, [s_f - 0.01])[0] for x in xs])
                zl = np.where(zl < -1e8, zfoot, zl)
                fill_bed(f"{spec['lane']}-{fi}-{i}-bed", -W / 2, s_f, W, 0.022, zl, bed_y)
            # a step reset in cement: its bed pointed where its front stands on the step below
            if cemented and prev_tops:
                s_f = i * g + ovh - 0.006
                xs = np.linspace(-W / 2, W / 2, 24)
                zl = np.array([top_line(prev_tops, x, [s_f - 0.01])[0] for x in xs])
                zl = np.where(zl < -1e8, zfoot, zl)
                point(f"{spec['lane']}-{fi}-{i}-bed", -W / 2, s_f, W, 0.026, False, zl, YEAR - st["mortar"][1])
            # the tread: its slabs as the years left them, each laid on the riser, its nosing over it
            edges = plan[i]
            tops = []
            joints = []      # (x, half the gap, its filling: None (soil and moss) or (material, year))
            jr = 0.0
            for k, sl in enumerate(st["slabs"]):
                x_a, x_b = edges[k], edges[k + 1]
                jr_left = jr
                jl = rng.uniform(*JOINT) / 2 if k > 0 else 0.0
                jr = rng.uniform(*JOINT) / 2 if k < len(edges) - 2 else 0.0
                worn_y = YEAR - sl["placed"]
                bare_y = YEAR - sl["bare"]
                reclaimed = sl["origin"] == "reclaimed"
                key = f"{spec['lane']}-{seed}-{fi}-{i}-{k}" + ("-rc" if reclaimed else "")
                c, corner = sl["cracked"], sl["corner"]
                parts = [(x_a + jl, x_b - jr, None)]
                if c:
                    xc = x_a + (x_b - x_a) * c["at"]
                    gap = rng.uniform(0.0005, 0.0012)        # (a crack in a solid block is a hairline, not a slot)
                    parts = [(x_a + jl, xc - gap, "a"), (xc + gap, x_b - jr, "b")]
                    joints.append((xc, gap, c["filled"], True))
                if k > 0:
                    joints.append((x_a, (jl + jr_left) / 2, ("cement", st["mortar"][1]) if cemented else None, False))
                depth = g + LAP + rng.uniform(-0.02, 0.03)
                tf = settler(rng, x_b - x_a, off)
                s0 = i * g + rng.uniform(-0.01, 0.01)
                fr, sr = rng.uniform(0.004, 0.008), rng.uniform(0.003, 0.006)
                fk, ch, jg = rng.uniform(0.3, 0.5), rng.uniform(0.008, 0.02), rng.uniform(0.008, 0.014)
                nl_ = None
                if how == "block":
                    # a thick block: its front one rough lumpy plate or two (the board, 06: no stacked laminae on a
                    # step's front), its arris crisp and knocked (rounded all along, every block read as dough); the
                    # walking line's wear rounds its own nosings. How it was finished is a fact of the flight: a
                    # mason's dressed block square, flat-faced and true; a split block as it came; rough slabs from
                    # the site's own rock knocked about
                    finish = spec.get("finish", "split")
                    if finish == "dressed":
                        fr, sr, jg, nl_ = rng.uniform(0.003, 0.005), rng.uniform(0.002, 0.004), rng.uniform(0.002, 0.004), 1
                        ch, fk = rng.uniform(0.004, 0.008), 0.05
                    elif finish == "rough":
                        fr, sr, jg, nl_ = rng.uniform(0.008, 0.015), rng.uniform(0.006, 0.012), rng.uniform(0.016, 0.026), 2
                        ch = rng.uniform(0.02, 0.035)
                    else:
                        fr, sr, jg, nl_ = rng.uniform(0.006, 0.01), rng.uniform(0.004, 0.007), rng.uniform(0.008, 0.012), 2
                        ch = rng.uniform(0.012, 0.025)
                for pa, pb, half in parts:
                    w = pb - pa
                    broken = None
                    if corner and ((corner["side"] == "l" and half in (None, "a")) or (corner["side"] == "r" and half in (None, "b"))):
                        # (a nosing's corner spalls a few centimetres deep, down to a bedding plane)
                        broken = (corner["side"], corner["size"], min(t_tr, 0.04 + corner["size"] * 0.6))
                    # split slate: crisp edges, its corners knocked, a layer flaked off here and there (rounded, every
                    # tread read as a bar of soap); its wear rounds the walking line's nosing on its own
                    piece = SL.slab(key + (f"-{half}" if half else ""), w, depth, t_tr, front_round=fr, side_round=sr,
                                    flake=fk, chip=ch, edge_jag=jg, broken=broken, layers=nl_)
                    dx = pa - x_a
                    P = tf(piece["V"], dx)
                    if half == "b":
                        P[:, 2] -= rng.uniform(0.002, 0.008)    # (the halves of a crack settled apart: a step, not a line)
                    x0 = -W / 2 + pa
                    tops.append(put(P, piece, rng, x0, s0, z_top - t_tr, True, worn_y, bare_y, bed_y,
                                    polish0=0.3 if reclaimed else 0.0, lifted_y=YEAR - sl["lifted"]))
                    # a corner broken off and dabbed with cement: it fills the cut back to the stone's own front and
                    # end, struck flush with them and with the top, as deep as the break went
                    if broken and corner["filled"]:
                        cn = piece["corner"]
                        e0, f0 = cn["end"], cn["front"]
                        b1, a1 = max(cn["along"] - e0, 0.01), max(cn["back"] - f0, 0.01)
                        fr_ = lambda x, a1=a1, b1=b1: a1 * np.clip(1.0 - x / b1, 0.0, 1.0)
                        sd_ = lambda y, a1=a1, b1=b1: b1 * np.clip(1.0 - y / a1, 0.0, 1.0)
                        dab = CE.dab(f"{key}-dab", fr_, sd_, (b1, a1), t_tr - 0.002, deep=cn["depth"])
                        Vd = dab["V"].copy()
                        Vd[:, 0] += e0
                        Vd[:, 1] += f0
                        if corner["side"] == "r":
                            Vd[:, 0] = w - Vd[:, 0]
                            dab["F"] = [tuple(reversed(q)) for q in dab["F"]]
                        Pd = tf(Vd, dx)
                        cast_y = YEAR - corner["filled"][1]
                        put(Pd, dab, random.Random(f"{key}-dab"), x0, s0, z_top - t_tr, True, cast_y, cast_y, cast_y)
            # the joints between the tread's slabs and its cracks: pointed in cement where a crew or a quick fix
            # struck it, else soil and moss
            s_a, s_b = i * g + 0.005, (i + 1) * g + ovh
            for x, gap, filled, crack in joints:
                xj = -W / 2 + x
                if filled and filled[0] == "cement":
                    ss = np.linspace(s_a, s_b, 10)
                    zl = top_line(tops, xj, ss)
                    zl = np.where(zl < -1e8, z_top - 0.004, zl)
                    point(f"{spec['lane']}-{fi}-{i}-{x:.3f}", xj, s_a, s_b - s_a, 2 * gap + 0.02, True, zl,
                          YEAR - filled[1])
                else:
                    fill(xj, gap + 0.004, s_a, s_b, z_top - 0.004, bed_y)
                if how == "block":
                    # (a joint and a crack hold dirt and moss at the face, so neither opens on the void; the crew's
                    # pointing shows on the tread, its front joint filled as the others: a pale upright strip read as
                    # a plank)
                    fill_front(xj, gap + (0.0015 if crack else 0.003), i * g + 0.002, zfoot, z_top - 0.006, bed_y, None)
            prev_tops = tops
        # the life as the flight's record: each step's last bed and joints, and its slabs' repairs
        record = []
        for i, st in enumerate(life):
            r = dict(step=i, reset=st["reset"], off_mm=round(st["settled"] * 1000, 1),
                     mortar=list(st["mortar"]) if st["mortar"] else None, slabs=[])
            for sl in st["slabs"]:
                d = dict(origin=sl["origin"], placed=sl["placed"], bare=sl["bare"], lifted=sl["lifted"])
                for key in ("cracked", "corner"):
                    if sl[key]:
                        d[key] = dict(year=sl[key]["year"], filled=list(sl[key]["filled"]) if sl[key]["filled"] else None)
                if sl["shim"]:
                    d["shim"] = sl["shim"]
                r["slabs"].append(d)
            record.append(r)
        meshes.append((f"stone_{spec['lane'].lower().replace(' ', '_')}_{fi}",
                       dict(V=np.concatenate(out["V"]), F=out["F"], COL=np.concatenate(out["COL"]),
                            UV0=np.concatenate(out["UV0"]), UV1=np.concatenate(out["UV1"]), UV2=np.concatenate(out["UV2"]),
                            UV3=np.concatenate(out["UV3"]),
                            steps=n, rise=h, tread=g, life=record,
                            a=[float(v) for v in a], b=[float(v) for v in b], width=float(W))))
    return meshes, origin, flags


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


def slug(name):
    return "".join(c if c.isalnum() else "_" for c in name.lower()).strip("_")


def build(which, unity=None, seed=1, spec=None, folder=""):
    """One stair: the beauty corner's own by its key in FLIGHTS, or any flight in the plan from its spec (stair_facts),
    written to Assets/Art/Stone/<folder>/stone_<which>.fbx and .json."""
    import bpy
    for ob in list(bpy.data.objects):
        bpy.data.objects.remove(ob, do_unlink=True)
    spec = spec or FLIGHTS[which]
    meshes, origin, flags = lay(spec, seed)
    if not meshes:
        print("STONE", which, "nothing built:", flags)
        return dict(name=f"stone_{which}", flags=flags)
    obs = [make(name, m) for name, m in meshes]
    info = dict(name=f"stone_{which}", origin=[float(v) for v in origin], flags=flags,
                flights=[dict(name=nm, steps=m["steps"], rise=round(m["rise"], 3), tread=round(m["tread"], 3),
                              a=m["a"], b=m["b"], width=m["width"],
                              tris=sum(len(f) - 2 for f in m["F"]), life=m["life"]) for nm, m in meshes])
    print("STONE", {k: v for k, v in info.items() if k != "flights"},
          [(f["name"], f["steps"], f["tris"]) for f in info["flights"]])
    if unity:
        path = os.path.join(unity, "Assets", "Art", "Stone", folder, f"stone_{which}.fbx")
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
    if which == "variety":
        # every named flight in the plan (or the default twelve), each from its own facts, into Art/Stone/Variety
        import heart_layout as H
        import stair_facts as SF
        sys.path.insert(0, os.path.join(HERE, "..", "tools"))
        names = argv[2:] or ["Gully Steps", "Tanner's Steps", "Bishop's Steps", "the Hundred Steps",
                             "the path to Lookout Park", "passage at -172", "passage at 92", "passage at 110",
                             "stair-lane 2", "stair-lane 6", "the way to D (1107, empty since 1986)", "the Crack"]
        for nm in names:
            lane = next((l for l in H.LANES if l["name"] == nm), None)
            sp = SF.facts_for(lane) if lane else None
            if sp is None:
                continue
            info = build(slug(nm), unity, spec=dict(sp), folder="Variety")
            if not info.get("flights"):
                continue
            facts = dict(name=nm, stone=sp.get("stone", "slate"), built=sp["built"], built_as=sp.get("built_as"),
                         finish=sp.get("finish", "split"),
                         footfall=sp["footfall"], keepers=[[u["by"], u["since"], u["care"]] for u in sp["upkeep"]],
                         works=[[w["kind"], w["year"]] for w in sp["works"]])
            with open(os.path.join(unity, "Assets", "Art", "Stone", "Variety", f"stone_{slug(nm)}.facts.json"), "w") as fh:
                json.dump(facts, fh, indent=1)
    else:
        build(which, unity)
