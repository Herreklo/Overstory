"""The stair kind's stages (kinds/stair.json; schemas/stages.md): stone.py's lay() split into the seven stages the one
runner (tools/run_kind.py) runs, with the meshes they build hashing exactly what stone.py built before the split (the
gully port's step 2a: a refactor, proven by the FBX's mesh hash). stone.py stays the library: the set-out, the
course widths, the settling, the parts' fitting and make(); this file holds what each stage decides.

    facts     the record, validated (tools/stages/record.py), and its way's path from the town plan (a 2a exception)
    plan      what the mason set out: the flights, their rises and goings, the landings, each step's slabs, risers and
              kerbs as the slots they are, and the site's own facts (the walking line's lean, how wet each bed is)
    life      what the years did: on which flight each campaign fell, and each step's bed and each slab's fill now
              (upkeep.py), keyed by the fill's id, so step 3 can add each fill's layers' intervals
    geometry  the pieces, laid and fitted, worn where feet went: the vertices, faces and grain, and per vertex what
              the bake reads, per piece its put's facts; the landings' rows and the setts' rows are minted here
    bake      the history layers per vertex (polish, lichen, moss, water held, the bare years, the water, the sky)
    export    the meshes made in Blender, the FBX and its sidecar (stone_<token>.json), installed in Unity
    checks    ids by schemas/naming.md, the set-out by blender/tools/setout_check.py, one fill a slot, the counts

Every draw is keyed as stone.py keyed it, on the stages' legacySeed (1) and the same ids and purposes, each stream's
draws in the same order: the plan holds the "setout", "plan", "step", "wet", "rise", "moss" and "lean" draws, life
upkeep.py's and the campaigns', geometry the rest ("lay", "row", "marks", the crack's). Floats cross the stages as
they are (the plan in integer millimetres is step 2b's).

stone.lay() and stone.build() run the same four functions in one process (compose), each output passed through the
runner's plain() as the cache would, so the old command and the runner build the same mesh.
"""

import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
TOOLS = os.path.join(ROOT, "tools")
if HERE not in sys.path:
    sys.path.insert(0, HERE)
if TOOLS not in sys.path:
    sys.path.append(TOOLS)
import stone as ST  # noqa: E402  (the library; it puts the parts, the resolver and the blockouts on the path)
import hashing as HS  # noqa: E402
import hashes as HX  # noqa: E402
from hashes import Blob  # noqa: E402
import slab as SL  # noqa: E402
import cement as CE  # noqa: E402
import sett as SETT  # noqa: E402
import growth as GR  # noqa: E402
import upkeep as UP  # noqa: E402
import water as WT  # noqa: E402
import wear as WR  # noqa: E402
from wear import walking  # noqa: E402

STAGES_DIR = os.path.join(TOOLS, "stages")
CEMENT = 4      # a piece's kind: cement (pointing, a dab)
SOIL = 6        # a piece's kind: a joint's soil and moss


def _plain(v):
    """An output as the runner hands it on: numpy as Python values, tuples as lists, Blobs whole."""
    return HX.plain(v, "$", blobs=True)


def _arr(v):
    return v.values if isinstance(v, Blob) else np.asarray(v)


def _record_stages():
    if STAGES_DIR not in sys.path:
        sys.path.insert(0, STAGES_DIR)
    import record as RS
    return RS


# ------------------------------------------------------------------------------------------------------------ plan

def plan_stair(spec, lane, seed):
    """What the mason set out on the way's path (lane: name, width, pts in metres): each flight's rise, going and
    landings (stone.step_plan), each tread's slabs across it (stone.widths, every joint bridged), each step's top a
    little off the even line, its thickness and its risers' or kerbs' widths, and how much water each bed takes."""
    sid = ST.stair_id(spec)
    fl = ST.flights_of(lane)
    origin = fl[0]["a"].copy()
    lean = spec.get("lean", HS.uniform(HS.h(seed, sid, "lean"), ST.LEAN[0], ST.LEAN[1]))
    how = spec.get("built_as", "tread_on_riser")
    finish = spec.get("finish", "split")
    ws = ST.SLAB_WIDTHS[finish if finish in ("dressed", "rough") else "other"]
    e_ = ST.RISE_ERROR.get(finish if finish in ("dressed", "rough") else "other")
    flights, ids, steps, flags = {}, [], {}, []
    for fi, f in enumerate(fl):
        fid = ST.flight_id(spec, fi)
        ids.append(fid)
        a, b, W = f["a"], f["b"], f["width"]
        F = dict(index=fi, a=a, b=b, width=W, form=f["form"], n=f["n"], flag=f.get("flag"), setout=None, steps=[],
                 wet=[], err=[])
        flights[fid] = F
        if f.get("flag"):
            # (not built: a ladder of stone tells a false story; the plan is fixed instead)
            print("PLAN FLAG", spec["lane"], fi, f["flag"])
            flags.append(dict(flight=fi, flag=f["flag"]))
            continue
        sp = ST.step_plan(f, spec, fi, seed)
        if sp["fallback"]:
            # (the builder's patience could not be kept on this run: the limit of real practice set its landings)
            print("SETOUT FLAG", spec["lane"], fi, sp["fallback"])
            flags.append(dict(sp["fallback"]))
        n, h = sp["n"], sp["r"]
        SS, DD = sp["S"], sp["D"]
        # the treads' slabs as the mason laid them (every joint bridged)
        edges_t, below, below2 = [], [], []
        for i in range(n):
            prng = HS.Stream(seed, ST.tread_id(spec, fi, i), "plan")
            edges = ST.widths(prng, W, below, lo=ws["lo"], hi=ws["hi"], below2=below2, ks=ws["ks"])
            below2, below = below, edges[1:-1]
            edges_t.append(edges)
        # how much water each step's bed takes: more towards a flight's foot, and most where the lane's water is
        # led onto it (one or two places along it, the stair's own: always the foot, every campaign's run sat there)
        WET = ST.WET
        wrng = HS.Stream(seed, fid, "wet")
        sinks = [wrng.uniform(0.0, 1.0) for _ in range(wrng.randint(*ST.WET_SINKS))]
        wet = [WET["base"] + WET["foot"] * (1.0 - i / max(n - 1, 1)) +
               max(WET["sink"] * math.exp(-((i / max(n - 1, 1) - c) / WET["sinkSpread"]) ** 2) for c in sinks) +
               HS.uniform(HS.h(seed, ST.tread_id(spec, fi, i), "wet"), 0.0, WET["luck"]) for i in range(n)]
        # each step's top a little off the flight's even line (an old flight's rises are never all alike); its ends
        # on it (err[i] is the top of step i - 1, keyed on it)
        err = [0.0] + [HS.uniform(HS.h(seed, ST.tread_id(spec, fi, i - 1), "rise"), -e_, e_)
                       for i in range(1, n)] + [0.0]
        F.update(setout=sp, wet=wet, err=err)
        below_r = []
        for i in range(n):
            tid = ST.tread_id(spec, fi, i)
            F["steps"].append(tid)
            rng = HS.Stream(seed, tid, "step")          # the step's own: its thickness, overhang and risers' widths
            step_wet = float(np.clip(0.35 + 0.75 * wet[i] * HS.uniform(HS.h(seed, tid, "moss"), 0.3, 1.3), 0.15, 1.2))
            z_top = a[2] + (i + 1) * h + err[i + 1]
            zfoot = a[2] + i * h + err[i]
            T = dict(flight=fid, index=i, S=SS[i], D=DD[i], zTop=z_top, zFoot=zfoot, stepWet=step_wet,
                     edges=edges_t[i], slabs=[f"{tid}/sl-{k}" for k in range(len(edges_t[i]) - 1)])
            if f["form"] == "step_ramp":
                # a step-ramp (a trappegate): a long kerb stone for the riser, its top flush with the tread
                kd = rng.uniform(0.2, 0.26)
                kt = (z_top - zfoot) + rng.uniform(0.12, 0.16) + (0.15 if i == 0 else 0.0)
                edges_k = ST.widths(rng, W, below_r, lo=0.8, hi=2.0, ks=(1, 2, 2))
                below_r = edges_k[1:-1]
                T.update(kerbDepth=kd, kerbHeight=kt, kerbEdges=edges_k,
                         kerbs=[f"{tid}/kb-{k}" for k in range(len(edges_k) - 1)])
            elif how == "block":
                # one thick split slab a step, its front split face the riser, resting on the back of the one below;
                # the first set into the ground
                T.update(tread=h + ST.BUILT["block"]["bed"] + rng.uniform(-0.01, 0.02) + (0.2 if i == 0 else 0.0),
                         overhang=0.0)
            else:
                B = ST.BUILT["tread_on_riser"]
                t_tr = rng.uniform(*B["tread"])
                ovh = rng.uniform(*B["overhang"])
                edges_r = ST.widths(rng, W, below_r, lo=0.6, hi=2.2)
                below_r = edges_r[1:-1]
                T.update(tread=t_tr, overhang=ovh, riserEdges=edges_r,
                         risers=[f"{tid}/rs-{k}" for k in range(len(edges_r) - 1)])
            steps[tid] = T
    return dict(stair=sid, lane=spec["lane"], origin=origin, lean=lean, builtAs=how, finish=finish, flags=flags,
                flightIds=ids, flights=flights, steps=steps)


# ------------------------------------------------------------------------------------------------------------ life

def life_stair(spec, plan, seed, date):
    """What the years did to the stair, to the date: on which flight each campaign fell (one a stair, on the flight
    its cause chose: weighted by its steps), then each flight's life (upkeep.py): each step's bed now, and each slab's
    fill, keyed by its id (<slot>/<fill>)."""
    stone = ST.STONES[spec["stone"]]
    sid = plan["stair"]
    lean = plan["lean"]
    care_now = UP.keeper_in(spec["upkeep"], date - 1)["care"]
    flights = plan["flights"]
    built_fl = [flights[fid]["index"] for fid in plan["flightIds"] if not flights[fid]["flag"]]
    n_of = dict((flights[fid]["index"], flights[fid]["n"]) for fid in plan["flightIds"])
    camp, campaigns = {}, []
    for j, w in enumerate(spec["works"]):
        if w["kind"] == "campaign" and built_fl:
            camp[j] = HS.weighted(HS.h(seed, sid, "campaign", w["year"]), [(k, n_of[k]) for k in built_fl])
            campaigns.append(dict(event=w.get("event"), year=w["year"], flight=plan["flightIds"][camp[j]]))
    steps, fills = {}, {}
    for fid in plan["flightIds"]:
        F = flights[fid]
        if F["flag"]:
            continue
        fi, W = F["index"], F["width"]
        tids = F["steps"]
        edges = [plan["steps"][t]["edges"] for t in tids]
        works_here = [w for j, w in enumerate(spec["works"]) if w["kind"] != "campaign" or camp.get(j, 0) == fi]
        slots = dict(flight=fid, steps=list(tids), slabs=[list(plan["steps"][t]["slabs"]) for t in tids])
        life = UP.flight([list(zip(e[:-1], e[1:])) for e in edges], spec["built"], date, spec["upkeep"],
                         works_here, seed, slots, F["wet"], cracks=stone.get("cracks", 1.0),
                         busy=lambda x, W=W: float(walking(np.array([x / W]), W, lean)[0]))
        for tid, st in zip(tids, life):
            ids = []
            for sl in st["slabs"]:
                key = f"{sl['slot']}/{sl['fill']}"
                if key in fills:
                    raise ValueError(f"{key}: two slabs in one fill")
                fills[key] = dict(sl, step=tid)
                ids.append(key)
            steps[tid] = dict(reset=st["reset"], settled=st["settled"], mortar=st["mortar"], slabs=ids)
    return dict(date=int(date), care=care_now, campaigns=campaigns, steps=steps, fills=fills)


# ------------------------------------------------------------------------------------------------------------ geometry

class _Mesh(object):
    """One mesh being laid: what stone.py's put appended, and per vertex and per piece what the bake reads."""

    VERTEX = ("V", "UV0", "kind", "edge", "y", "across", "along", "foot", "worn", "zp")
    PIECE = ("start", "count", "footOn", "wornY", "bareY", "bedY", "liftedY", "hasLifted", "polish0", "var", "zFoot",
             "zTop", "stepWet")
    DTYPES = dict(start="int64", count="int64", footOn="bool", wornY="int64", bareY="int64", bedY="int64",
                  liftedY="int64", hasLifted="bool", polish0="float64", var="float64", zFoot="float64",
                  zTop="float64", stepWet="float64")

    def __init__(self, fid, setts):
        self.fid, self.setts = fid, setts
        self.v = dict((k, []) for k in self.VERTEX)
        self.p = dict((k, []) for k in self.PIECE)
        self.F, self.sizes, self.ids, self.nv = [], [], [], 0

    def output(self):
        out = dict(flight=self.fid, setts=self.setts, pieces=list(self.ids))
        for k in self.VERTEX:
            arr = np.concatenate(self.v[k])
            if k == "kind":
                assert arr.dtype == np.int8, arr.dtype
            else:
                assert arr.dtype == np.float64, (k, arr.dtype)
            out[k] = Blob(arr)
        out["corners"] = Blob(np.array([q for f in self.F for q in f], dtype=np.int32))
        out["sizes"] = Blob(np.array(self.sizes, dtype=np.int32))
        for k in self.PIECE:
            out[k] = Blob(np.array(self.p[k], dtype=self.DTYPES[k]))
        return out


def geometry_stair(spec, plan, life, seed):
    """The pieces of every flight, laid as stone.py's lay() laid them: the steps from the foot, each its risers or
    kerbs, its bed, its tread's slabs as the years left them (a crack's halves, a corner's dab), its joints, its
    landing, and the turn's landing last. Per piece the first half of stone.py's put(): where it sits along and across
    its step, the wear of feet and the nosing's rounding, its place in the street's frame and its grain; the rest of
    put() is the bake's."""
    YEAR = life["date"]
    care_now = life["care"]
    stone = ST.STONES[spec["stone"]]
    how = plan["builtAs"]
    origin = np.array(plan["origin"], float)
    lean = plan["lean"]
    LAP, JOINT = ST.LAP, ST.JOINT
    lane_key = plan["lane"].lower().replace(' ', '_')
    meshes, order, pieces, joints = {}, [], {}, []
    for fid in plan["flightIds"]:
        Fp = plan["flights"][fid]
        if Fp["flag"]:
            continue
        fi = Fp["index"]
        a, b, W = np.array(Fp["a"], float), np.array(Fp["b"], float), Fp["width"]
        d2 = (b - a)[:2]
        run = float(np.linalg.norm(d2))
        up = d2 / run                                    # uphill, in plan
        right = np.array([up[1], -up[0]])                # so right, up, z is right-handed
        sp = Fp["setout"]
        n, h, g = sp["n"], sp["r"], sp["g"]
        cur = dict(S=0.0, D=g)                           # the step being laid (put reads where along it a point lies)
        out_main = _Mesh(fid, False)
        out_setts = _Mesh(fid, True)
        name_main = f"stone_{lane_key}_{fi}"
        name_setts = f"stone_{lane_key}_{fi}_setts"
        # (put reads the step's top, foot and wetness as they stand when it is called, as stone.py's closure did: at
        # the turn's landing the flight's foot, and the last step's top and wetness)
        state = dict(z_top=None, zfoot=None, step_wet=None)

        def put(P, piece, rng, x0, s0, z0, foot_on, worn_y, bare_y, bed_y, polish0=0.0, lifted_y=None, dst=None,
                pc_id=None):
            """stone.py's put(), its first half: a piece's vertices P (slab space, x across, y up the flight, z up)
            set at x0 across, s0 along, z0 up, worn where feet go; returns it placed in the flight's frame."""
            kind = piece["kind"]
            assert kind.dtype == np.int8 and piece["edge"].dtype == np.float64 and P.dtype == np.float64
            assert isinstance(worn_y, int) and isinstance(bare_y, int) and isinstance(bed_y, int)
            across = np.clip((x0 + P[:, 0] + W / 2) / W, 0.0, 1.0)
            along = np.clip((s0 + P[:, 1] - cur["S"]) / max(cur["D"], 1e-3), 0.0, 1.5)
            top = (kind == 0) & foot_on
            # wear (wear.py): footfall times years over the stone's hardness, where feet go: across the walking line,
            # on the front half of a tread where the foot lands, and over the nosing, which rounds
            foot = walking(across, W, lean) * ((0.45 + 0.55 * np.exp(-((along * cur["D"] / g - 0.3) / 0.35) ** 2))
                                                if g < 0.5 else 1.0) * (1.0 if cur["D"] < 1.2 * g else
                                                                        np.clip(1.15 - along * 0.3, 0.6, 1.0))
            worn = WR.depth(stone["wear"], spec["footfall"], worn_y, foot, W)
            nose = foot_on & ((kind == 1) | ((kind == 0) & (piece["edge"] < 0.03) & (P[:, 1] < 0.05)))
            P = P.copy()
            # (the dish subtracts; the nosing's arris rounds faster than the tread hollows, never bowing the front out)
            P[:, 2] -= np.where(top, worn, 0.0) + np.where(nose, WR.nosing(worn, walking(across, W, lean)), 0.0)
            X = (a[0] - origin[0]) + right[0] * (x0 + P[:, 0]) + up[0] * (s0 + P[:, 1])
            Y = (a[1] - origin[1]) + right[1] * (x0 + P[:, 0]) + up[1] * (s0 + P[:, 1])
            Z = (z0 - origin[2]) + P[:, 2]
            out = dst if dst is not None else out_main
            base = out.nv
            out.v["V"].append(np.stack([X, Y, Z], -1))
            faces = [tuple(base + q for q in face) for face in piece["F"]]
            out.F.extend(faces)
            out.sizes.extend(len(f) for f in faces)
            ang = rng.uniform(0, 2 * math.pi)
            off = np.array([rng.uniform(0, 7), rng.uniform(0, 7)])
            uv = np.asarray(piece["UV"], dtype=np.float64)
            c_, s_ = math.cos(ang), math.sin(ang)
            ur = np.stack([uv[:, 0] * c_ - uv[:, 1] * s_, uv[:, 0] * s_ + uv[:, 1] * c_], -1)
            uv = np.where(((kind == 0) | (kind >= 4))[:, None], ur + off, uv + off)
            out.v["UV0"].append(uv)
            var = rng.random()
            m = len(P)
            for k_, v_ in (("kind", kind), ("edge", piece["edge"]), ("y", P[:, 1]), ("across", across),
                           ("along", along), ("foot", foot), ("worn", worn), ("zp", z0 + P[:, 2])):
                v_ = np.ascontiguousarray(v_)
                assert v_.shape == (m,), (k_, v_.shape)
                out.v[k_].append(v_)
            pp = out.p
            pp["start"].append(base)
            pp["count"].append(m)
            pp["footOn"].append(bool(foot_on))
            pp["wornY"].append(worn_y)
            pp["bareY"].append(bare_y)
            pp["bedY"].append(bed_y)
            pp["liftedY"].append(lifted_y if lifted_y is not None else 0)
            pp["hasLifted"].append(lifted_y is not None)
            pp["polish0"].append(float(polish0))
            pp["var"].append(var)
            pp["zFoot"].append(float(state["zfoot"]))
            pp["zTop"].append(float(state["z_top"]))
            pp["stepWet"].append(float(state["step_wet"]))
            if pc_id in pieces:
                raise ValueError(f"{pc_id}: two pieces with one id")
            out.ids.append(pc_id)
            pieces[pc_id] = dict(fill=pc_id.rsplit("#", 1)[0], mesh=name_setts if out is out_setts else name_main,
                                 chunk=HX.chunk_of(int(round(1000.0 * (origin[0] + float(X.mean())))),
                                                   int(round(1000.0 * (origin[1] + float(Y.mean()))))),
                                 vertices=m, triangles=sum(len(f) - 2 for f in faces), _rows=(base, base + m))
            out.nv += m
            return np.stack([x0 + P[:, 0], s0 + P[:, 1], z0 + P[:, 2]], -1)

        def joint(jid, kind, filled, line, made):
            joints.append(dict(id=jid, kind=kind, fill="cement" if filled and filled[0] == "cement" else "soil",
                               year=filled[1] if filled else None, mesh=name_main, line=line, pieces=made))

        def fill(pid, xc, half, s_a, s_b, z, bed_y):
            """The soil and moss a joint between two slabs fills with (pid, the joint's id): a strip a little below
            their tops, a little wider than the joint, so the joint reads as a damp green-dark line."""
            Vq = np.array([[-half, 0.0, 0.0], [half, 0.0, 0.0], [half, s_b - s_a, 0.0], [-half, s_b - s_a, 0.0]])
            piece = dict(V=Vq, F=[(0, 1, 2, 3)], kind=np.full(4, 6, dtype=np.int8), edge=np.zeros(4),
                         UV=Vq[:, :2] + xc)
            put(Vq, piece, HS.Stream(seed, pid, "marks"), xc, s_a, z, True, 0, YEAR - spec["built"], bed_y,
                pc_id=f"{pid}/0#0")
            return f"{pid}/0#0"

        def fill_bed(pid, x_a, s_f, length, width, zl, bed_y):
            """Soil and moss along a block's foot, in the bed joint where it stands on the step below."""
            pc = CE.pointing(HS.h(seed, pid), length, width)
            V = pc["V"].copy()
            t = np.clip(V[:, 0] / max(length, 1e-6), 0.0, 1.0)
            V[:, 2] = np.interp(t, np.linspace(0, 1, len(zl)), zl) + 0.001
            pc["kind"] = np.full(len(V), 6, dtype=np.int8)
            put(V, pc, HS.Stream(seed, pid, "marks"), x_a, s_f, 0.0, True, 0, YEAR - spec["built"], bed_y,
                pc_id=f"{pid}/0#0")
            return f"{pid}/0#0"

        def fill_front(pid, xc, half, s_f, z0, z1, bed_y, cast=None):
            """The same joint where it comes down a block's front: soil and moss a centimetre in, or the crew's
            cement pointing struck to the face."""
            Vq = np.array([[-half, 0.0, 0.0], [half, 0.0, 0.0], [half, 0.0, z1 - z0], [-half, 0.0, z1 - z0]])
            kind_ = 4 if cast is not None else 6
            piece = dict(V=Vq, F=[(0, 1, 2, 3)], kind=np.full(4, kind_, dtype=np.int8), edge=np.zeros(4),
                         UV=np.stack([Vq[:, 0] + xc, Vq[:, 2]], -1))
            yrs = cast if cast is not None else YEAR - spec["built"]
            put(Vq, piece, HS.Stream(seed, pid, "marks"), xc, s_f, z0, False, 0,
                yrs, bed_y if cast is None else cast, pc_id=f"{pid}/0#0")
            return f"{pid}/0#0"

        def point(pid, x_a, s_a, length, width, along_s, zl, cast_y):
            """Cement pointing struck along a joint, to the stone's top either side (zl, along it): along_s, a joint
            running up the flight at x_a; else one running across it at s_a."""
            pc = CE.pointing(HS.h(seed, pid), length, width)
            V = pc["V"].copy()
            t = np.clip(V[:, 0] / max(length, 1e-6), 0.0, 1.0)
            zz = np.interp(t, np.linspace(0, 1, len(zl)), zl) + 0.0012
            if along_s:
                V = np.stack([V[:, 1], V[:, 0], zz], -1)
                pc["F"] = [tuple(reversed(q)) for q in pc["F"]]
                put(V, pc, HS.Stream(seed, pid, "marks"), x_a, s_a, 0.0, True, cast_y, cast_y, cast_y,
                    pc_id=f"{pid}/0#0")
            else:
                V = np.stack([V[:, 0], V[:, 1], zz], -1)
                put(V, pc, HS.Stream(seed, pid, "marks"), x_a, s_a, 0.0, True, cast_y, cast_y, cast_y,
                    pc_id=f"{pid}/0#0")
            return f"{pid}/0#0"

        def pave(lid, s_from, s_to, z_top_, thick, bed_y, bare_y):
            """A landing (lid, its id) paved at z_top_ from s_from to s_to along the flight: rows of slabs, every
            joint bridged, the same stone and finish as the steps, as old as the flight; returns their placed tops.
            Its rows and their slabs are minted here (stair-row, stair-slab)."""
            placed, below_, pos, k_ = [], [], s_from, 0
            while pos < s_to - 0.05:
                rid = f"{lid}/rw-{k_}"
                rrng = HS.Stream(seed, rid, "row")
                row = min(rrng.uniform(0.45, 0.8), s_to - pos)
                edges_ = ST.widths(rrng, W, below_, lo=0.5, hi=1.6)
                below_ = edges_[1:-1]
                for k in range(len(edges_) - 1):
                    pid = f"{rid}/sl-{k}"
                    prng_ = HS.Stream(seed, pid, "lay")
                    w_ = edges_[k + 1] - edges_[k] - prng_.uniform(*JOINT)
                    pc = SL.slab(HS.h(seed, pid), w_, row + LAP * 0.5, thick, front_round=prng_.uniform(0.003, 0.006),
                                 side_round=0.004, flake=0.3, chip=prng_.uniform(0.006, 0.015), edge_jag=0.008)
                    P_ = ST.settler(prng_, w_, 0.004)(pc["V"])
                    placed.append(put(P_, pc, prng_, -W / 2 + edges_[k], pos, z_top_ - thick, True,
                                      bare_y, bare_y, bed_y, pc_id=f"{pid}/0#0"))
                    if k > 0:
                        made = fill(f"{rid}/jt-{k}", -W / 2 + edges_[k], 0.006, pos, pos + row, z_top_ - 0.004, bed_y)
                        joint(f"{rid}/jt-{k}", "joint", None,
                              [[-W / 2 + edges_[k], pos, z_top_ - 0.004], [-W / 2 + edges_[k], pos + row,
                                                                           z_top_ - 0.004]], [made])
                pos += row
                k_ += 1
            return placed

        prev_tops = []
        for i in range(n):
            tid = Fp["steps"][i]
            T = plan["steps"][tid]
            st = life["steps"][tid]
            slabs_now = [life["fills"][k] for k in st["slabs"]]
            bed_y = YEAR - st["reset"]
            step_wet = T["stepWet"]
            cemented = bool(st["mortar"]) and st["mortar"][0] == "cement"
            # (a stair let go is further off true: its stones rock and tilt, nobody resets them)
            off = (st["settled"] + 0.003) * (1.0 + 1.5 * (1.0 - care_now))
            z_top = T["zTop"]
            zfoot = T["zFoot"]
            state.update(z_top=z_top, zfoot=zfoot, step_wet=step_wet)
            Si, Di = T["S"], T["D"]
            cur["S"], cur["D"] = Si, Di
            if Fp["form"] == "step_ramp":
                # a step-ramp (a trappegate): a long kerb stone for the riser, dressed and set on edge, its top flush
                # with the tread, and the tread paved in setts behind it to the next kerb
                kd, kt, edges_k = T["kerbDepth"], T["kerbHeight"], T["kerbEdges"]
                for k in range(len(edges_k) - 1):
                    kid = f"{tid}/kb-{k}"
                    krng = HS.Stream(seed, kid, "lay")
                    w = edges_k[k + 1] - edges_k[k] - (krng.uniform(*JOINT) if k < len(edges_k) - 2 else 0.0)
                    pc = SL.slab(HS.h(seed, kid), w, kd, kt, front_round=krng.uniform(0.006, 0.012),
                                 side_round=0.004, flake=0.05, chip=krng.uniform(0.006, 0.014), edge_jag=0.004, layers=1)
                    P = ST.settler(krng, w, off * 0.6)(pc["V"])
                    put(P, pc, krng, -W / 2 + edges_k[k], Si, z_top - kt, True, YEAR - st["reset"], YEAR - spec["built"],
                        bed_y, pc_id=f"{kid}/0#0")
                # the setts: rows across, every joint off the row before, each its own size and set, crowned and worn
                # (the rows are minted here, stair-sett-row; a row's setts are the pieces of its fill)
                pos, below_s, r_ = Si + kd + 0.004, [], 0
                while pos < Si + Di - 0.04:
                    rid = f"{tid}/sets/rw-{r_}"
                    srng = HS.Stream(seed, rid, "row")
                    rw = min(srng.uniform(0.095, 0.13), Si + Di - pos)
                    xx, joints_s, c_ = -W / 2 + 0.01, [], 0
                    while xx < W / 2 - 0.05:
                        for _ in range(20):
                            Ls = srng.uniform(0.11, 0.22)
                            if all(abs(xx + Ls - j) > 0.04 for j in below_s):
                                break
                        ws = min(Ls, W / 2 - 0.01 - xx)
                        if ws < 0.05:
                            break
                        cid = f"{rid}/0#{c_}"
                        crng_ = HS.Stream(seed, cid, "lay")
                        pc = SETT.sett(HS.h(seed, cid), ws - crng_.uniform(0.005, 0.009),
                                       rw - crng_.uniform(0.005, 0.008), crown=crng_.uniform(0.002, 0.005))
                        P = pc["V"].copy()
                        P[:, 2] += crng_.uniform(-0.004, 0.004) - 0.01 * (pos - Si) / max(Di, 0.1)
                        put(P, pc, crng_, xx, pos, z_top, True, YEAR - st["reset"], YEAR - spec["built"], bed_y,
                            dst=out_setts, pc_id=cid)
                        joints_s.append(xx + Ls)
                        xx += Ls
                        c_ += 1
                    below_s = joints_s
                    pos += rw
                    r_ += 1
                # the sand bed between them: soil and moss in the joints
                made = fill(f"{tid}/sets/bed", 0.0, W / 2, Si + kd, Si + Di, z_top - 0.012, bed_y)
                joint(f"{tid}/sets/bed", "sand", None, None, [made])
                prev_tops = []
                continue
            t_tr, ovh = T["tread"], T["overhang"]
            if how != "block":
                B = ST.BUILT["tread_on_riser"]
                edges_r = T["riserEdges"]
                hr = (z_top - t_tr) - zfoot + 0.004     # (cut to meet its tread)
                # (the first step's riser is set into the ground, as a mason sets it)
                sunk = 0.2 if i == 0 else 0.0
                for k in range(len(edges_r) - 1):
                    rid = f"{tid}/rs-{k}"
                    rrng = HS.Stream(seed, rid, "lay")
                    jl = rrng.uniform(*JOINT) / 2 if k > 0 else 0.0
                    jr = rrng.uniform(*JOINT) / 2 if k < len(edges_r) - 2 else 0.0
                    w = edges_r[k + 1] - edges_r[k] - jl - jr
                    dep = rrng.uniform(*B["riser"])
                    piece = SL.slab(HS.h(seed, rid), w, dep, hr + sunk + 0.03, front_round=rrng.uniform(0.002, 0.006),
                                    side_round=0.003, flake=0.1, chip=rrng.uniform(0.006, 0.015), edge_jag=0.008, grid=0.16)
                    P = ST.settler(rrng, w, off * 0.5)(piece["V"])
                    put(P, piece, rrng, -W / 2 + edges_r[k] + jl, Si + ovh + rrng.uniform(-0.004, 0.004), zfoot - sunk - 0.03, False,
                        YEAR - spec["built"], YEAR - spec["built"], bed_y, pc_id=f"{rid}/0#0")
            # the bed line at a block's foot, where it stands on the step below: soil and moss where no crew pointed it
            if how == "block" and not cemented and prev_tops:
                s_f = Si + 0.004
                xs = np.linspace(-W / 2, W / 2, 24)
                zl = np.array([ST.top_line(prev_tops, x, [s_f - 0.01])[0] for x in xs])
                zl = np.where(zl < -1e8, zfoot, zl)
                made = fill_bed(f"{tid}/bed", -W / 2, s_f, W, 0.022, zl, bed_y)
                joint(f"{tid}/bed", "bed", None, [[-W / 2, s_f, float(zl[0])], [W / 2, s_f, float(zl[-1])]], [made])
            # a step reset in cement: its bed pointed where its front stands on the step below
            if cemented and prev_tops:
                s_f = Si + ovh - 0.006
                xs = np.linspace(-W / 2, W / 2, 24)
                zl = np.array([ST.top_line(prev_tops, x, [s_f - 0.01])[0] for x in xs])
                zl = np.where(zl < -1e8, zfoot, zl)
                made = point(f"{tid}/bed/pt", -W / 2, s_f, W, 0.026, False, zl, YEAR - st["mortar"][1])
                joint(f"{tid}/bed", "bed", st["mortar"], [[-W / 2, s_f, float(zl[0])], [W / 2, s_f, float(zl[-1])]],
                      [made])
            # the tread: its slabs as the years left them, each laid on the riser, its nosing over it
            edges = T["edges"]
            tops = []
            joints_t = []    # (x, half the gap, its filling: None (soil and moss) or (material, year), crack, id)
            jr = 0.0
            for k, sl in enumerate(slabs_now):
                x_a, x_b = edges[k], edges[k + 1]
                jr_left = jr
                # the stone in the slot now (a reclaimed slab is a new fill, so a new stone): its own draws
                key = f"{sl['slot']}/{sl['fill']}"
                srng = HS.Stream(seed, key, "lay")
                jl = srng.uniform(*JOINT) / 2 if k > 0 else 0.0
                jr = srng.uniform(*JOINT) / 2 if k < len(edges) - 2 else 0.0
                worn_y = YEAR - sl["placed"]
                bare_y = YEAR - sl["bare"]
                reclaimed = sl["origin"] == "reclaimed"
                c, corner = sl["cracked"], sl["corner"]
                parts = [(x_a + jl, x_b - jr, None)]
                if c:
                    xc = x_a + (x_b - x_a) * c["at"]
                    # (a crack in a solid block is a hairline, not a slot)
                    gap = HS.uniform(HS.h(seed, key, "crack", "gap"), 0.0005, 0.0012)
                    parts = [(x_a + jl, xc - gap, "a"), (xc + gap, x_b - jr, "b")]
                    joints_t.append((xc, gap, c["filled"], True, f"{key}/ck"))
                if k > 0:
                    joints_t.append((x_a, (jl + jr_left) / 2, ("cement", st["mortar"][1]) if cemented else None, False,
                                     f"{tid}/jt-{k}"))
                # (a landing's tread is laid in rows: its first row the step's own slab, the rest paved behind it)
                depth = min(Di, g * 1.6) + LAP + srng.uniform(-0.02, 0.03)
                tf = ST.settler(srng, x_b - x_a, off)
                s0 = Si + srng.uniform(-0.01, 0.01)
                fr, sr = srng.uniform(0.004, 0.008), srng.uniform(0.003, 0.006)
                fk, ch, jg = srng.uniform(0.3, 0.5), srng.uniform(0.008, 0.02), srng.uniform(0.008, 0.014)
                nl_ = None
                if how == "block":
                    # a thick block: how it was finished is a fact of the flight: a mason's dressed block square,
                    # flat-faced and true; a split block as it came; rough slabs from the site's own rock knocked about
                    finish = spec.get("finish", "split")
                    if finish == "dressed":
                        fr, sr, jg, nl_ = srng.uniform(0.003, 0.005), srng.uniform(0.002, 0.004), srng.uniform(0.002, 0.004), 1
                        ch, fk = srng.uniform(0.004, 0.008), 0.05
                    elif finish == "rough":
                        fr, sr, jg, nl_ = srng.uniform(0.008, 0.015), srng.uniform(0.006, 0.012), srng.uniform(0.016, 0.026), 2
                        ch = srng.uniform(0.02, 0.035)
                    else:
                        fr, sr, jg, nl_ = srng.uniform(0.006, 0.01), srng.uniform(0.004, 0.007), srng.uniform(0.008, 0.012), 2
                        ch = srng.uniform(0.012, 0.025)
                for pa, pb, half in parts:
                    w = pb - pa
                    broken = None
                    if corner and ((corner["side"] == "l" and half in (None, "a")) or (corner["side"] == "r" and half in (None, "b"))):
                        # (a nosing's corner spalls a few centimetres deep, down to a bedding plane)
                        broken = (corner["side"], corner["size"], min(t_tr, 0.04 + corner["size"] * 0.6))
                    # (its pieces: the whole slab, or a crack's left half, is #0; the right half #1)
                    pid = f"{key}#{1 if half == 'b' else 0}"
                    piece = SL.slab(HS.h(seed, pid), w, depth, t_tr, front_round=fr, side_round=sr,
                                    flake=fk, chip=ch, edge_jag=jg, broken=broken, layers=nl_)
                    dx = pa - x_a
                    P = tf(piece["V"], dx)
                    if half == "b":
                        # (the halves of a crack settled apart: a step, not a line; left open on a neglected stair they
                        # drop further)
                        P[:, 2] -= HS.uniform(HS.h(seed, key, "crack", "drop"), 0.002, 0.008) * \
                            (1.0 + (0.0 if c["filled"] else 2.0 * (1.0 - care_now)))
                    x0 = -W / 2 + pa
                    tops.append(put(P, piece, HS.Stream(seed, pid, "marks"), x0, s0, z_top - t_tr, True, worn_y, bare_y, bed_y,
                                    polish0=0.3 if reclaimed else 0.0, lifted_y=YEAR - sl["lifted"], pc_id=pid))
                    # a corner broken off and dabbed with cement: it fills the cut back to the stone's own front and
                    # end, struck flush with them and with the stone's top as it is now round the break
                    if broken and corner["filled"]:
                        cn = piece["corner"]
                        e0, f0 = cn["end"], cn["front"]
                        b1, a1 = max(cn["along"] - e0, 0.01), max(cn["back"] - f0, 0.01)
                        fr_ = lambda x, a1=a1, b1=b1: a1 * np.clip(1.0 - x / b1, 0.0, 1.0)  # noqa: E731
                        sd_ = lambda y, a1=a1, b1=b1: b1 * np.clip(1.0 - y / a1, 0.0, 1.0)  # noqa: E731
                        dab = CE.dab(HS.h(seed, f"{key}/dab"), fr_, sd_, (b1, a1), t_tr - 0.002, deep=cn["depth"])
                        Vd = dab["V"].copy()
                        Vd[:, 0] += e0
                        Vd[:, 1] += f0
                        if corner["side"] == "r":
                            Vd[:, 0] = w - Vd[:, 0]
                            dab["F"] = [tuple(reversed(q)) for q in dab["F"]]
                        Pd = ST.seat_dab(tf(Vd, dx), Vd[:, 2] - (t_tr - 0.002), tops[-1],
                                         ST.top_faces(piece["F"], piece["kind"]), x0, s0, z_top - t_tr)
                        cast_y = YEAR - corner["filled"][1]
                        put(Pd, dab, HS.Stream(seed, f"{key}/dab", "marks"), x0, s0, z_top - t_tr, True, cast_y, cast_y, cast_y,
                            pc_id=f"{key}/dab/0#0")
            # the joints between the tread's slabs and its cracks: pointed in cement where a crew or a quick fix
            # struck it, else soil and moss
            s_a, s_b = Si + 0.005, Si + min(Di, g * 1.6) + ovh
            for x, gap, filled, crack, jid in joints_t:
                xj = -W / 2 + x
                if filled and filled[0] == "cement":
                    ss = np.linspace(s_a, s_b, 10)
                    zl = ST.top_line(tops, xj, ss)
                    zl = np.where(zl < -1e8, z_top - 0.004, zl)
                    made = [point(f"{jid}/pt", xj, s_a, s_b - s_a, 2 * gap + 0.02, True, zl, YEAR - filled[1])]
                else:
                    made = [fill(jid, xj, gap + 0.004, s_a, s_b, z_top - 0.004, bed_y)]
                if how == "block":
                    # (a joint and a crack hold dirt and moss at the face, so neither opens on the void)
                    made.append(fill_front(f"{jid}/front", xj, gap + (0.0015 if crack else 0.003), Si + 0.002, zfoot,
                                           z_top - 0.006, bed_y, None))
                joint(jid, "crack" if crack else "joint", filled,
                      [[xj, s_a, z_top - 0.004], [xj, s_b, z_top - 0.004]], made)
            # a landing: the rest of the tread paved in rows of slabs at the step's level, behind its first row
            if Di > g * 1.6 + 0.05:
                tops += pave(f"{tid}/ld", Si + g * 1.6, Si + Di, z_top, t_tr, bed_y,
                             YEAR - spec["built"])
            prev_tops = tops
        # the landing at a turn, before the first step, at the flight's foot level
        if sp["start"] > 0.05:
            cur["S"], cur["D"] = 0.0, sp["start"]
            state["zfoot"] = a[2]
            pave(f"{fid}/turn", 0.0, sp["start"], a[2], h + 0.06, YEAR - spec["built"],
                 YEAR - spec["built"])
        for nm, ms in ((name_setts, out_setts), (name_main, out_main)):
            if ms.nv:
                meshes[nm] = ms
                order.append(nm)
    out = dict(meshOrder=order, meshes={}, joints=joints)
    for nm in order:
        out["meshes"][nm] = meshes[nm].output()
    # each piece's own rows hashed (its vertices in its mesh), and the fills and chunks summed from them
    for pid, p in pieces.items():
        r0, r1 = p.pop("_rows")
        p["hash"] = HX.hex64(out["meshes"][p["mesh"]]["V"].slice_hash(r0, r1))
    out["pieces"] = dict((k, pieces[k]) for k in sorted(pieces))
    out["summary"] = HX.summarise_pieces(out["pieces"])
    out["counts"] = dict(meshes=len(order), pieces=len(pieces),
                         vertices=sum(p["vertices"] for p in pieces.values()),
                         triangles=sum(p["triangles"] for p in pieces.values()))
    return out


# ------------------------------------------------------------------------------------------------------------ bake

def bake_stair(spec, plan, life, geo):
    """The history layers of every vertex, as the second half of stone.py's put() made them: polish where feet went;
    lichen where it is quiet for the years the stone has been bare (torn where hands lifted it); moss where it stays
    damp and sheltered, thinned by the keeper's care now; water held in the dish; the bare years and the piece's
    seed; which face and the water on it; what it sees of the sky and the ground within the flight."""
    care_now = life["care"]
    lean = plan["lean"]
    out = dict(meshes={}, pieces={})
    for nm in geo["meshOrder"]:
        M = geo["meshes"][nm]
        Fp = plan["flights"][M["flight"]]
        W, h = Fp["width"], Fp["setout"]["r"]
        trod = WR.busy(spec["footfall"], W)
        V = dict((k, _arr(M[k])) for k in ("kind", "edge", "y", "across", "along", "foot", "worn", "zp"))
        T = dict((k, _arr(M[k])) for k in _Mesh.PIECE)
        cols, uv1s, uv2s, uv3s = [], [], [], []
        for j, pid in enumerate(M["pieces"]):
            s, e = int(T["start"][j]), int(T["start"][j]) + int(T["count"][j])
            kind, edge, Py, across, along, foot, worn, zz = (V[k][s:e].copy() for k in
                                                             ("kind", "edge", "y", "across", "along", "foot", "worn",
                                                              "zp"))
            foot_on = bool(T["footOn"][j])
            worn_y, bare_y, bed_y = int(T["wornY"][j]), int(T["bareY"][j]), int(T["bedY"][j])
            lifted_y = int(T["liftedY"][j]) if bool(T["hasLifted"][j]) else None
            polish0, var = float(T["polish0"][j]), float(T["var"][j])
            zfoot, z_top, step_wet = float(T["zFoot"][j]), float(T["zTop"][j]), float(T["stepWet"][j])
            n = e - s
            cement = kind >= 4
            top = (kind == 0) & foot_on
            polish = np.where(foot_on & ((kind <= 1) | (kind == 5)), WR.polish(spec["footfall"], worn_y, foot), 0.0)
            polish = np.maximum(polish, np.where(foot_on & (kind <= 1), polish0, 0.0))
            # growth (nature's, docs/nature.md, Growth on surfaces): lichen where it is quiet for its years; on a
            # riser's face too, above where boots scuff its foot; moss where it stays damp
            traffic = (walking(across, W, lean) if foot_on else walking(across, W, lean) * (1.0 - np.clip((zz - zfoot) / 0.05, 0.0, 0.8))) * trod
            lich_y = bare_y
            if lifted_y is not None and lifted_y < bare_y:
                lich_y = np.where(((kind == 0) & (edge < 0.06)) | (kind == 1) | (kind == 2), lifted_y, bare_y)
            # (lichen wants light and to dry out: it hugs a tread's front and nosing and the riser's face, and thins
            # towards the damp back under the riser above, where moss takes over)
            if foot_on:
                exposed = np.where(kind == 0, np.clip(1.0 - (along - 0.2) / 0.6, 0.25, 1.0), 1.0)
            else:
                exposed = np.full(n, 0.8)
            lichen = GR.lichen_years(lich_y, np.where(foot_on, traffic, traffic * 0.75), exposed)
            lichen = np.where(kind == 6, 0.0, lichen)       # (a joint's soil takes moss, never lichen)
            back = (kind == 0) & foot_on & (along > 0.8)
            joint = (kind == 0) & (edge < 0.05) & (Py > 0.04)
            damp = np.where(back, np.clip((along - 0.8) / 0.15, 0.3, 1.0), 0.0) + np.where(joint & ~back, 1.0, 0.0) \
                + np.where(kind == 4, 1.0, 0.0) + np.where(kind == 5, 0.3, 0.0) + np.where(kind == 6, 1.0, 0.0)
            # (each step its own: how wet its bed is, and luck)
            damp = damp * step_wet
            if not foot_on:
                damp = damp + 0.7 * np.clip(1.0 - (zz - zfoot) / 0.04, 0.0, 1.0) * step_wet
            else:
                damp = damp + np.where(kind == 2, 0.7 * np.clip(1.0 - (zz - zfoot) / 0.04, 0.0, 1.0) * step_wet, 0.0)
            moss_y = np.where(back | joint | (kind == 4) | (kind == 6) | (not foot_on), min(bare_y, bed_y), bare_y)
            # (a tended stair is swept and its joints weeded: its keeper's care now thins the moss; neglect lets it in)
            damp = damp * (1.15 - 0.75 * care_now)
            moss = GR.moss(damp, trod * walking(across, W, lean) * np.where(foot_on & (kind != 6), np.maximum(np.exp(-((np.clip(along, 0, 1) - 0.3) / 0.35) ** 2), 0.7), 1.0), moss_y)
            # water stands only where the dish is deepest (on slate a few millimetres)
            held = np.clip((worn - 0.003) / 0.003, 0.0, 1.0) * top
            cols.append(np.stack([polish, lichen, moss, np.clip(held, 0, 1)], -1))
            uv1s.append(np.stack([np.full(n, bare_y / 200.0), np.full(n, var)], -1))
            # the water layer (water.py): on a tread water lingers in the dish, the joints and against the step
            # above, and the crown dries first; the nosing sheds it; a front takes what runs over the nosing above
            water_top = WT.on_top(back=np.where(back, (along - 0.8) / 0.2, 0.0), joint=np.where(joint, 0.8, 0.0),
                                  hollow=worn / 0.004)
            run_over = WT.over_edge(walking(across, W, lean) * 0.9, z_top - zz)
            water = np.where(kind == 0, water_top, np.where(kind == 1, 0.3, np.where(kind == 2, run_over,
                             np.where(kind >= 4, WT.HOLDS, 0.2))))
            if not foot_on:
                water = np.where(kind == 2, run_over, water)
            uv2s.append(np.stack([kind.astype(float), np.clip(water, 0.0, 1.0)], -1))
            # what each point sees of the sky within the flight (the town's own shade comes from its sky map)
            if foot_on:
                sky = np.where((kind == 0) | cement, 0.95 - 0.4 * np.clip((along - 0.75) / 0.25, 0.0, 1.0),
                               np.where(kind == 1, 0.75, np.where(kind == 2, 0.7, 0.35)))
            else:
                hh = np.clip((zz - zfoot) / max(h, 1e-3), 0.0, 1.0)
                sky = np.where(kind == 3, 0.35, np.where(kind == 6, 0.6, 0.8 - 0.2 * hh))
            ground = np.where(kind == 0, 0.12, np.where(kind == 3, 0.6, 0.3))
            uv3s.append(np.stack([sky, ground], -1))
        mo = dict(COL=np.concatenate(cols), UV1=np.concatenate(uv1s), UV2=np.concatenate(uv2s),
                  UV3=np.concatenate(uv3s))
        for k, v in mo.items():
            assert v.dtype == np.float64, (k, v.dtype)
        rows = Blob(np.concatenate([mo["COL"], mo["UV1"], mo["UV2"], mo["UV3"]], axis=1))
        for j, pid in enumerate(M["pieces"]):
            s, e = int(T["start"][j]), int(T["start"][j]) + int(T["count"][j])
            p = geo["pieces"][pid]
            out["pieces"][pid] = dict(fill=p["fill"], chunk=p["chunk"], mesh=nm, hash=HX.hex64(rows.slice_hash(s, e)),
                                      vertices=e - s)
        out["meshes"][nm] = dict((k, Blob(v)) for k, v in mo.items())
    out["pieces"] = dict((k, out["pieces"][k]) for k in sorted(out["pieces"]))
    out["summary"] = HX.summarise_pieces(out["pieces"])
    out["layers"] = dict(COL=["polish", "lichen", "moss", "held"], UV1=["bareYears/200", "seed"],
                         UV2=["face", "water"], UV3=["sky", "ground"])
    return out


# ------------------------------------------------------------------------------------------------------------ the meshes

def meshes_of(spec, plan, life, geo, bake):
    """The meshes as stone.py's lay() returned them: [(name, dict(V, F, COL, UV0..UV3, steps, rise, tread, life,
    landings, S, a, b, width[, setts]))], each flight's setts before its steps."""
    out = []
    for nm in geo["meshOrder"]:
        M, Bm = geo["meshes"][nm], bake["meshes"][nm]
        Fp = plan["flights"][M["flight"]]
        sp = Fp["setout"]
        h, g = sp["r"], sp["g"]
        corners, sizes = _arr(M["corners"]).tolist(), _arr(M["sizes"]).tolist()
        F, k = [], 0
        for s in sizes:
            F.append(tuple(corners[k:k + s]))
            k += s
        m = dict(V=_arr(M["V"]), F=F, COL=_arr(Bm["COL"]), UV0=_arr(M["UV0"]), UV1=_arr(Bm["UV1"]),
                 UV2=_arr(Bm["UV2"]), UV3=_arr(Bm["UV3"]))
        a, b, W = [float(v) for v in Fp["a"]], [float(v) for v in Fp["b"]], float(Fp["width"])
        if M["setts"]:
            m.update(steps=0, rise=h, tread=g, life=[], landings=0, S=[], a=a, b=b, width=W, setts=True)
        else:
            m.update(steps=sp["n"], rise=h, tread=g, life=life_record(plan, life, M["flight"]),
                     landings=sum(1 for d in sp["D"] if d > g * 1.6 + 0.05), S=[round(float(v), 3) for v in sp["S"]],
                     a=a, b=b, width=W)
        out.append((nm, m))
    return out


def life_record(plan, life, fid):
    """A flight's life as its sidecar holds it: each step's last bed and joints, and its slabs' repairs."""
    record = []
    for i, tid in enumerate(plan["flights"][fid]["steps"]):
        st = life["steps"][tid]
        r = dict(step=i, reset=st["reset"], off_mm=round(st["settled"] * 1000, 1),
                 mortar=list(st["mortar"]) if st["mortar"] else None, slabs=[])
        for key in st["slabs"]:
            sl = life["fills"][key]
            d = dict(origin=sl["origin"], placed=sl["placed"], bare=sl["bare"], lifted=sl["lifted"])
            for k in ("cracked", "corner"):
                if sl[k]:
                    d[k] = dict(year=sl[k]["year"], filled=list(sl[k]["filled"]) if sl[k]["filled"] else None)
            if sl["shim"]:
                d["shim"] = sl["shim"]
            r["slabs"].append(d)
        record.append(r)
    return record


def compose(spec, lane, seed, date):
    """plan, life, geometry and bake in one process, each output passed on as the runner passes it: what stone.lay()
    and stone.build() run."""
    P = _plain(plan_stair(spec, lane, seed))
    L = _plain(life_stair(spec, P, seed, date))
    G = _plain(geometry_stair(spec, P, L, seed))
    B = _plain(bake_stair(spec, P, L, G))
    return dict(plan=P, life=L, geometry=G, bake=B, meshes=meshes_of(spec, P, L, G, B),
                origin=np.array(P["origin"], float), flags=P["flags"])


# ------------------------------------------------------------------------------------------------------------ the sidecar

def _r3(v):
    return round(float(v), 3)


def sidecar(spec, plan, life, geo):
    """What the export's sidecar adds after stone.py's keys (which stay as they were: LT1Stone.cs reads name, origin
    and flights): the breaklines (each flight's walking line, each step's foot line), the joints (their lines and the
    pieces moss grows on), the affordances (treads, landings, turns and the walking line: dated sockets, walkable or
    not), the motion class and the collision roles. In the meshes' frame: metres from the origin."""
    origin = np.array(plan["origin"], float)
    lean = plan["lean"]
    built = spec["built"]
    frames, names = {}, {}
    for nm in geo["meshOrder"]:
        if not geo["meshes"][nm]["setts"]:
            names[geo["meshes"][nm]["flight"]] = nm
    for fid in plan["flightIds"]:
        Fp = plan["flights"][fid]
        a, b = np.array(Fp["a"], float), np.array(Fp["b"], float)
        d2 = (b - a)[:2]
        up = d2 / float(np.linalg.norm(d2))
        frames[fid] = (a, np.array([up[1], -up[0]]), up)

    def at(fid, x, s, z):
        a, right, up = frames[fid]
        return [_r3((a[0] - origin[0]) + right[0] * x + up[0] * s), _r3((a[1] - origin[1]) + right[1] * x + up[1] * s),
                _r3(z - origin[2])]

    def quad(fid, W, s0, s1, z):
        return [at(fid, -W / 2, s0, z), at(fid, W / 2, s0, z), at(fid, W / 2, s1, z), at(fid, -W / 2, s1, z)]

    walking_lines, feet, affordances = [], [], []
    for fid in plan["flightIds"]:
        Fp = plan["flights"][fid]
        if Fp["flag"]:
            continue
        W, sp = Fp["width"], Fp["setout"]
        g = sp["g"]
        xw = lean * min(0.25 * W, 0.5)      # (the walking line's middle, as wear.walking keeps to its side)
        pts = []
        if sp["start"] > 0.05:
            pts.append(at(fid, xw, sp["start"] / 2, Fp["a"][2]))
            affordances.append(dict(id=f"{fid}/turn", name="turn", walkable=True, mesh=names[fid], **{"from": built},
                                    to=None, quad=quad(fid, W, 0.0, sp["start"], Fp["a"][2])))
        for tid in Fp["steps"]:
            T = plan["steps"][tid]
            Si, Di, zt = T["S"], T["D"], T["zTop"]
            landing = Di > g * 1.6 + 0.05
            s1 = Si + (g * 1.6 if landing else Di)
            feet.append(dict(step=tid, pts=[at(fid, -W / 2, Si, T["zFoot"]), at(fid, W / 2, Si, T["zFoot"])]))
            pts.append(at(fid, xw, Si + 0.3 * min(Di, g), zt))
            affordances.append(dict(id=tid, name="tread", walkable=True, mesh=names[fid], **{"from": built}, to=None,
                                    quad=quad(fid, W, Si, s1, zt)))
            if landing:
                pts.append(at(fid, xw, Si + Di - 0.3 * g, zt))
                affordances.append(dict(id=f"{tid}/ld", name="landing", walkable=True, mesh=names[fid],
                                        **{"from": built}, to=None, quad=quad(fid, W, s1, Si + Di, zt)))
        walking_lines.append(dict(flight=fid, mesh=names[fid], pts=pts))
    affordances.append(dict(id=f"{plan['stair']}/walk", name="walk", walkable=True, **{"from": built}, to=None,
                            breaklines="walking"))
    joints = []
    for j in geo["joints"]:
        fid = geo["meshes"][j["mesh"]]["flight"]
        joints.append(dict(id=j["id"], kind=j["kind"], fill=j["fill"], year=j["year"], mesh=j["mesh"],
                           line=[at(fid, *p) for p in j["line"]] if j["line"] else None, growth=j["pieces"]))
    return dict(breaklines=dict(walking=walking_lines, feet=feet), joints=joints, affordances=affordances,
                motion="still",
                collision=dict(meshes=dict((nm, "none") for nm in geo["meshOrder"]), proxy="affordances",
                               walkable=[a["id"] for a in affordances if a["walkable"] and "quad" in a]))


# ------------------------------------------------------------------------------------------------------------ the stages

def _spec(ctx):
    """The library's spec of the record and its way, from the facts stage's output."""
    tp = ctx.record["townPlan"]
    lane = dict(name=tp["name"], width=tp["width"], pts=[tuple(p) for p in tp["pts"]])
    return ST.spec_of(ctx.record, tp["name"]), lane


def facts(ctx):
    """The record, validated (tools/stages/record.py), and its way's path from the town plan, in metres: the way the
    record is on, found in blender/blockouts/heart_layout.py by its id (a 2a exception: step 2b reads the plan's
    way from the town's own records, in integer millimetres)."""
    out = _record_stages().facts(ctx)
    lane = ST.lane_of(dict(way=next(l["id"] for l in out["links"] if l["rel"] == "on")))
    out["townPlan"] = dict(way=ST.way_id(lane["name"]), name=lane["name"], width=lane["width"],
                           pts=[[float(v) for v in p] for p in lane["pts"]], source="blender/blockouts/heart_layout.py")
    return out


def plan(ctx):
    ST.configure(plan=ctx.params, stairs=ctx.table("stairs"))
    spec, lane = _spec(ctx)
    return plan_stair(spec, lane, ctx.params["legacySeed"])


def life(ctx):
    ST.configure(materials=ctx.table("materials"))
    spec, _ = _spec(ctx)
    return life_stair(spec, ctx.outputs["plan"], ctx.params["legacySeed"], ctx.date)


def geometry(ctx):
    ST.configure(geometry=ctx.params, materials=ctx.table("materials"))
    spec, _ = _spec(ctx)
    return geometry_stair(spec, ctx.outputs["plan"], ctx.outputs["life"], ctx.params["legacySeed"])


def bake(ctx):
    spec, _ = _spec(ctx)
    return bake_stair(spec, ctx.outputs["plan"], ctx.outputs["life"], ctx.outputs["geometry"])


def export(ctx):
    """The meshes made in Blender and written as stone_<token>.fbx with its sidecar and its mesh hash, installed in
    the Unity project (installDir)."""
    spec, _ = _spec(ctx)
    P, L, G, B = (ctx.outputs[s] for s in ("plan", "life", "geometry", "bake"))
    meshes = meshes_of(spec, P, L, G, B)
    name = "stone_" + ctx.record["id"].split("-", 1)[1].replace("-", "_")
    info = ST.info_of(name, meshes, P["origin"], P["flags"])
    info.update(sidecar(spec, P, L, G))
    path = os.path.join(ctx.root, ctx.params["installDir"], name + ".fbx")
    entry = ST.write_export(path, meshes, info)
    for p in (path, path[:-4] + ".json"):
        ctx.wrote(p)
    rel = os.path.relpath(path, ctx.root).replace(os.sep, "/")
    return dict(name=name, fbx=rel, json=rel[:-4] + ".json", meshHash=entry["hash"], triangles=entry["triangles"],
                flights=[dict(name=f["name"], steps=f["steps"], tris=f["tris"]) for f in info["flights"]])


def checks(ctx):
    """The generic checks (ids, floats), then the stair's own: every built flight's set-out by
    blender/tools/setout_check.py, one current fill in every slab slot, the geometry's and the bake's pieces the same,
    and the export's triangles the geometry's."""
    out = _record_stages().checks(ctx)
    problems = list(out["problems"])
    spec, lane = _spec(ctx)
    P, L = ctx.outputs["plan"], ctx.outputs["life"]
    sys.path.insert(0, os.path.join(ROOT, "blender", "tools"))
    import setout_check as SC
    seed = ctx.kind["stages"]["plan"]["params"]["legacySeed"]
    for fid in P["flightIds"]:
        Fp = P["flights"][fid]
        if Fp["flag"]:
            problems.append(f"{fid}: not built: {Fp['flag']}")
            continue
        f = dict(a=np.array(Fp["a"], float), b=np.array(Fp["b"], float), width=Fp["width"], form=Fp["form"],
                 n=Fp["n"])
        _, bad, _ = SC.check_flight(f, spec, Fp["index"], seed)
        problems += [f"{fid}: {x}" for x in bad]
    seen = {}
    for tid, st in L["steps"].items():
        for key in st["slabs"]:
            slot = L["fills"][key]["slot"]
            if slot in seen:
                problems.append(f"{slot}: two fills now ({seen[slot]}, {key})")
            seen[slot] = key
    slots = [s for T in P["steps"].values() for s in T["slabs"]]
    problems += [f"{s}: no fill" for s in slots if s not in seen]
    G, B = ctx.outputs.get("geometry"), ctx.outputs.get("bake")
    if G is not None and B is not None and sorted(G["pieces"]) != sorted(B["pieces"]):
        problems.append("the geometry's pieces and the bake's differ")
    E = ctx.outputs.get("export")
    if E is not None and G is not None and E["triangles"] != G["counts"]["triangles"]:
        problems.append(f"the export holds {E['triangles']} triangles, the geometry {G['counts']['triangles']}")
    out.update(problems=problems[:50], problemCount=len(problems), **{"pass": not problems})
    out["stair"] = dict(flights=len(P["flightIds"]), steps=len(P["steps"]), fills=len(L["fills"]),
                        pieces=len(G["pieces"]) if G else None, triangles=G["counts"]["triangles"] if G else None)
    return out
