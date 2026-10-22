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

Since the gully port's step 2a this is the stair kind's library (kinds/stair.json): what it decides is split into the
seven stages in stair_stages.py, which the one runner runs on a record (tools/run_kind.py fixtures/records/st-gully.json)
and lay() and build() run in one process, so both build the same mesh. Its rules come from the kind's params and the
pack's tables (configure()); the gully's facts from its record (spec_of()).
"""

import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "resolver"))
import hashing as HS  # noqa: E402  (the one hash spec)
sys.path.insert(0, os.path.join(HERE, "..", "parts", "stone", "slate"))
sys.path.insert(0, os.path.join(HERE, "..", "blockouts"))
sys.path.insert(0, os.path.join(HERE, "..", "parts", "repair"))
import slab as SL  # noqa: E402
import cement as CE  # noqa: E402
sys.path.insert(0, os.path.join(HERE, "..", "parts", "stone", "granite"))
import sett as SETT  # noqa: E402
import growth as GR  # noqa: E402
import upkeep as UP  # noqa: E402
import water as WT  # noqa: E402
import wear as WR  # noqa: E402
from wear import walking  # noqa: E402

ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
PACK = "stavanger-1989"
GULLY = os.path.join(ROOT, "fixtures", "records", "st-gully.json")


def _read(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


# The rules, as data (docs/building-blocks.md): the stair kind's params (kinds/stair.json: the plan stage's and the
# geometry stage's), the pack's builders' habits and codes (packs/<pack>/stairs.json) and its stones
# (packs/<pack>/materials/: how fast each wears under feet, mm a century at 100,000 footfalls a year, granite about 1.5
# to 3, soft stone about 15, the slaty rock between, unverified; how readily it cracks, slate parting along its beds,
# granite seldom). They are held there in integer millimetres and per mille, and set here in metres and fractions by
# configure(), which each stage calls with what it reads: each divided by 1000.0 is the literal it replaced, bit for
# bit (a correctly rounded quotient of two integers). YEAR is the fabric's date (the pack's showYear by default).
#
#   STRIDE      two rises and a going: a person's stride on a stair (Blondel's rule)
#   GOING_MIN   a going a foot fits on; GOING_RANGE what a rise's going is held within
#   RISE_MAX    the most a person climbs in one step; STRIDE_MAX two rises and a going at most, where spare run
#               lengthens the goings (the stride's range setout_check.py holds every flight to: 0.59 to 0.70)
#   RAMP_MIN    below this slope a way is paved, not stepped; STEP_RAMP below this a stair is a step-ramp
#   LAP         how far a tread reaches under the riser of the step above; JOINT a joint's width (wide joints showed
#               the void under the treads as black slots)
#   BUILT       how a step is built (a fact of the flight, by its era and its stone): a tread slab on a riser set on
#               edge, its nosing proud (a slab-on-riser step is mostly riser: thick treads over recessed risers read
#               as shelves over black slots); or one thick block a step on its bed, its front the riser
#   PATIENCE    risers a builder lets run unbroken (owners as they please: OWN_PATIENCE); RUN_RISERS_MAX and
#               RUN_RISE_MAX the limits of real practice (DIN 18065; TEK section 12-14)
BUILT = {"tread_on_riser": {}, "block": {}}


def _m(v):
    return v / 1000.0


def _pair(v):
    return (_m(v[0]), _m(v[1]))


def configure(plan=None, geometry=None, stairs=None, materials=None, year=None):
    """Set the library's rules from the kind's params, the pack's tables and the date (what each is, above)."""
    global YEAR, STONES, LAP, JOINT, STRIDE, GOING_MIN, GOING_RANGE, RISE_MAX, STRIDE_MAX, RAMP_MIN, STEP_RAMP
    global STONE_RISES, RISE_ERROR, SLAB_WIDTHS, LEAN, WET, WET_SINKS, PATIENCE, OWN_PATIENCE, RUN_RISERS_MAX
    global RUN_RISE_MAX
    if year is not None:
        YEAR = int(year)
    if plan is not None:
        STRIDE = _m(plan["strideMm"])
        GOING_MIN = _m(plan["goingMinMm"])
        GOING_RANGE = _pair(plan["goingRangeMm"])
        RISE_MAX = _m(plan["riseMaxMm"])
        STRIDE_MAX = _m(plan["strideMaxMm"])
        RAMP_MIN = _m(plan["rampMinPerMille"])
        STEP_RAMP = _m(plan["stepRampPerMille"])
        STONE_RISES = dict((k, _pair(v)) for k, v in plan["stoneRisesMm"].items())
        b = plan["builtMm"]
        BUILT["tread_on_riser"].update(tread=_pair(b["treadOnRiser"]["tread"]),
                                       overhang=_pair(b["treadOnRiser"]["overhang"]))
        BUILT["block"].update(bed=_m(b["block"]["bed"]))
        RISE_ERROR = dict((k, _m(v)) for k, v in plan["riseErrorMm"].items())
        SLAB_WIDTHS = dict((k, dict(lo=_m(v["lo"]), hi=_m(v["hi"]), ks=tuple(v["ks"]) if v["ks"] else None))
                           for k, v in plan["slabWidthsMm"].items())
        LEAN = _pair(plan["leanPerMille"])
        WET = dict((k, _m(v)) for k, v in plan["wetPerMille"].items())
        WET_SINKS = tuple(plan["wetSinks"])
    if geometry is not None:
        LAP = _m(geometry["lapMm"])
        JOINT = _pair(geometry["jointMm"])
        BUILT["tread_on_riser"]["riser"] = _pair(geometry["riserDepthMm"])
    if stairs is not None:
        PATIENCE = dict((k, tuple(v)) for k, v in stairs["patience"].items())
        OWN_PATIENCE = tuple(stairs["ownPatience"])
        RUN_RISERS_MAX = int(stairs["runRisersMax"])
        RUN_RISE_MAX = _m(stairs["runRiseMaxMm"])
    if materials is not None:
        STONES = dict((d["material"], dict(wear=_m(d["wearUmPerCentury"]), cracks=_m(d["cracksPerMille"])))
                      for _, d in sorted(materials.items()))


def defaults():
    """What configure() is called with when the library is imported: the kind's params, the pack's tables, its
    showYear."""
    kind = _read(os.path.join(ROOT, "kinds", "stair.json"))
    pack = os.path.join(ROOT, "packs", PACK)
    mats = dict((f[:-5], _read(os.path.join(pack, "materials", f)))
                for f in sorted(os.listdir(os.path.join(pack, "materials"))) if f.endswith(".json"))
    return dict(plan=kind["stages"]["plan"]["params"], geometry=kind["stages"]["geometry"]["params"],
                stairs=_read(os.path.join(pack, "stairs.json")), materials=mats,
                year=_read(os.path.join(pack, "pack.json"))["showYear"])


configure(**defaults())


# A stair's facts from its record (schemas/record.schema.json): the flights authored for the beauty corner until the
# engine's fabric pass has them (docs/engine-requests.md, 6), as the library's spec: the stone, the year laid and how,
# the footfall a year, who kept it and how well, decade by decade, and the works its records hold (upkeep.py;
# docs/upkeep.md). The way it is on is the town plan's (lane_of).
BUILT_AS = {"block": "block", "treadOnRiser": "tread_on_riser"}


def spec_of(record, lane=None):
    """The library's spec of a stair record: dict(id, [lane], stone, built, built_as, finish, footfall, upkeep (each
    care period as dict(by (the keeper's role then: upkeep.py's word), since, care (a fraction))), works (each
    campaign or renewal event as dict(kind, year, share, mortar, stock, steps, material, event)), way (the way it is
    on)). lane: the way's name in the town plan, where it is known."""
    built = next(e for e in record["events"] if e["kind"] == "built")
    p = built.get("params", {})
    use = record.get("use", [])
    if len(use) != 1:
        raise ValueError(f"{record['id']}: the library reads one period of use, not {len(use)} (step 2b)")

    def keeper(year):
        k = None
        for kp in sorted(record.get("keepers", []), key=lambda kp: kp["from"]["year"]):
            if kp["from"]["year"] <= year:
                k = kp["keeper"]
        return (k or {}).get("role") or "owner"
    upkeep = [dict(by=keeper(c["from"]["year"]), since=c["from"]["year"], care=c["care"] / 1000.0)
              for c in sorted(record.get("care", []), key=lambda c: c["from"]["year"])]
    works = []
    for e in record["events"]:
        if e["kind"] not in ("campaign", "renewed"):
            continue
        q = e.get("params", {})
        w = dict(kind=e["kind"], year=e["at"]["year"])
        if "sharePerMille" in q:
            w["share"] = q["sharePerMille"] / 1000.0
        for k in ("mortar", "stock", "material"):
            if k in q:
                w[k] = q[k]
        if "steps" in q:
            w["steps"] = tuple(q["steps"])
        w["event"] = e["id"]
        works.append(w)
    spec = dict(id=record["id"])
    if lane:
        spec["lane"] = lane
    spec.update(stone=p["stone"], built=built["at"]["year"], built_as=BUILT_AS[p.get("builtAs", "treadOnRiser")],
                finish=p.get("finish", "split"), footfall=use[0]["footfall"], upkeep=upkeep, works=works,
                way=next((l["id"] for l in record.get("links", []) if l["rel"] == "on"), None))
    return spec


FLIGHTS = {"gully": spec_of(_read(GULLY))}


def way_id(name):
    """A way's record id in the town plan, from its name (the plan's ways are not records yet: step 2b)."""
    return "way-" + slug(name).replace("_", "-")


def lane_of(spec):
    """The town plan's way a stair is laid on (blender/blockouts/heart_layout.py; a minute to import, so only here):
    by its name, or by the way its record is on."""
    import heart_layout as H
    if spec.get("lane"):
        return next(l for l in H.LANES if l["name"] == spec["lane"])
    return next(l for l in H.LANES if way_id(l["name"]) == spec["way"])


# Seeds (docs/building-blocks.md, Seeds and determinism): every draw is keyed on the world seed, the stable id of the
# part it is for and what it decides (the hash spec, blender/resolver/hashing.py), never on a position, so a piece
# that moves or changes never re-draws its neighbours. The ids follow the record grammar (Records and ids): the stair
# is its record (st-<token>); a flight is fl-<n> of it (its plan unit, from the foot); a step is the tread slot tr-<i>
# of its flight; a tread slab sl-<k>, a riser rs-<k>, a kerb kb-<k> and the joint left of slab k jt-<k> are slots of
# their step, a landing behind it ld, its rows rw-<r>; a slab's fill counts the stones that have stood in its slot
# (upkeep.py), so a slab replaced is a new stone with its own seed; a fill's pieces (a cracked slab's halves) are #0
# and #1, and a step-ramp's setts are the pieces of their row's fill, <step>/sets/rw-<r>/0#<c>. (schemas/naming.md's
# stair rule: renaming an id re-seeds what it names.)
def stair_id(spec):
    """The stair's record id: its own, or st- and its lane's name."""
    return spec.get("id") or "st-" + slug(spec["lane"]).replace("_", "-")


def flight_id(spec, fi):
    return f"{stair_id(spec)}/fl-{fi}"


def tread_id(spec, fi, i):
    return f"{flight_id(spec, fi)}/tr-{i}"


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


# The landing rule: a run of steps longer than its builder would climb without a rest gets a landing, and a landing is
# long enough to cross in step. Sources: Approved Document M 1.33; DIN 18065 (a landing every 18 steps at most);
# Norway's TEK §12-14 (no unbroken run over 3.3 m of rise); DGUV (a landing is whole strides plus one going: the
# shortest, one stride and one going, about 0.9 to 1 m). The builders' patience and the limits are the pack's
# (stairs.json: PATIENCE, OWN_PATIENCE, RUN_RISERS_MAX, RUN_RISE_MAX), the stride the kind's (STRIDE, STRIDE_MAX).


def stone_rises(spec):
    """The rise the stone gives, as a range (m): a split block's own thickness, rough stones as they come, a thin
    tread on its riser; a dressed flight's era standard, one value (the kind's stoneRisesMm)."""
    if spec.get("built_as", "tread_on_riser") == "block":
        return STONE_RISES["blockDressed"] if spec.get("finish", "split") == "dressed" else STONE_RISES["block"]
    return STONE_RISES["treadOnRiser"]


def going_of(r):
    """The going a rise asks for: two rises and a going a stride (Blondel), within what a foot fits and a leg spans."""
    return float(np.clip(STRIDE - 2.0 * r, GOING_RANGE[0], GOING_RANGE[1]))


def landing_min(g):
    """The shortest landing on a flight of going g: one stride and one going, so it is crossed in step (DGUV)."""
    return STRIDE + g


def practice_limit(r):
    """The most risers real practice lets run unbroken at rise r: 18, and no more than 3.3 m of rise."""
    return max(1, min(RUN_RISERS_MAX, int(math.floor(RUN_RISE_MAX / r + 1e-9))))


def rests_needed(n, max_run):
    """The landings n risers need so no run between them is longer than max_run."""
    return max(0, int(math.ceil(n / max_run)) - 1)


def fits(n, H, run, max_run=None):
    """Whether n risers over a rise H fit a run of the given length (m) with the rests they need: n goings and k of
    the shortest landings within it, n.g + k.L_min <= run. max_run: the builder's patience in risers, or None for the
    limit of real practice at this rise. Pure: the narrowing and the set-out's own check both ask it."""
    r = H / n
    g = going_of(r)
    k = rests_needed(n, practice_limit(r) if max_run is None else max_run)
    return n * g + k * landing_min(g) <= run + 1e-9


def _narrow(f, spec, fi, seed):
    """The set-out's draws and its narrowing, pure. The rise's unit draw u and the builder's patience are drawn first,
    in that order, from the flight's own stream; the riser counts the stone's range can give are then narrowed to the
    contiguous run of them that fits (fits()), and u is mapped onto the rises of that run, so a flight whose whole
    range fits draws exactly the rise it drew before the rule. If none fits the patience, the limit of real practice
    stands in for it (flagged); if none fits that either, the flight cannot be built (ok False, its reason given).
    Returns (dict, the stream, at its place after the two draws)."""
    a, b = f["a"], f["b"]
    run = float(np.linalg.norm((b - a)[:2]))
    H = float(b[2] - a[2])
    rng = HS.Stream(seed, flight_id(spec, fi), "setout")
    lo, hi = stone_rises(spec)
    u = rng.random() if hi > lo else None
    patience = rng.randint(*PATIENCE.get(spec["upkeep"][0]["by"], OWN_PATIENCE))
    out = dict(run=run, H=H, lo=lo, hi=hi, u=u, patience=patience, fallback=None, ok=True, reason=None)
    if f.get("flag"):
        return dict(out, ok=False, reason=f["flag"]), rng
    ns = list(range(max(1, int(round(H / hi))), max(1, int(round(H / lo))) + 1))
    n_today = max(1, int(round(H / (lo + (hi - lo) * u if u is not None else lo))))
    limit = patience
    ok = [n for n in ns if fits(n, H, run, patience)]
    if not ok:
        limit = None
        ok = [n for n in ns if fits(n, H, run, None)]
    if not ok:
        n = ns[0]
        g = going_of(H / n)
        k = rests_needed(n, practice_limit(H / n))
        reason = (f"no rise in the stone's range ({lo:.2f} to {hi:.2f} m) fits: {H:.2f} m of "
                  f"rise over {run:.2f} m of run needs at least {n} risers of {H / n:.3f} m, going {g:.3f} m, and "
                  f"{k} landings of {landing_min(g):.2f} m at the limit of real practice ({RUN_RISERS_MAX} risers, "
                  f"{RUN_RISE_MAX} m), {n * g + k * landing_min(g):.2f} m in all; turn the stair: the plan's fault")
        return dict(out, ok=False, reason=reason, n_range=(ns[0], ns[-1])), rng
    # (fits() grows with n, so the risers that fit run from the fewest; still, take the run of them nearest the
    # stone's own draw)
    blocks, cur = [], [ok[0]]
    for n in ok[1:]:
        if n == cur[-1] + 1:
            cur.append(n)
        else:
            blocks.append(cur)
            cur = [n]
    blocks.append(cur)
    na, nb = min(((b_[0], b_[-1]) for b_ in blocks), key=lambda ab: max(ab[0] - n_today, n_today - ab[1], 0))
    # the rises that round to that run, within the stone's range
    lo_n, hi_n = max(lo, H / (nb + 0.5)), (min(hi, H / (na - 0.5)) if na > 1 else hi)
    r_t = lo_n + (hi_n - lo_n) * u if u is not None else lo
    n = min(max(max(1, int(round(H / r_t))), na), nb)
    out.update(n=n, n_range=(na, nb), stone_range=(ns[0], ns[-1]))
    if limit is None:
        r = H / n
        g = going_of(r)
        k_p = rests_needed(n, patience)
        out["fallback"] = dict(
            rule="landing", flight=fi, flag="the builder's patience overridden by the limit of real practice",
            reason=f"no rise in the stone's range fits {patience} risers a run: {n} risers need {k_p} landings "
                   f"of {landing_min(g):.2f} m, {n * g + k_p * landing_min(g):.2f} m of run where there is "
                   f"{run:.2f} m", patience=patience, limit=practice_limit(r), n=n, r=round(r, 4),
            g=round(g, 4), rests=rests_needed(n, practice_limit(r)), run=round(run, 3), H=round(H, 3),
            landing_min=round(landing_min(g), 3))
    return out, rng


def setout_feasible(f, spec, fi, seed=1):
    """Whether a flight of the plan can be set out by the landing rule, for a town-plan checker at plan time, without
    building: dict(ok, fallback (True when only the limit of real practice fits), reason (why not, when not), n_range
    (the riser counts that fit), patience)."""
    if f.get("form") == "step_ramp":
        return dict(ok=True, fallback=False, reason=None, n_range=(f["n"], f["n"]), patience=None)
    nar, _ = _narrow(f, spec, fi, seed)
    return dict(ok=nar["ok"], fallback=nar["fallback"] is not None, reason=nar["reason"],
                n_range=nar.get("n_range"), patience=nar["patience"])


def step_plan(f, spec, fi, seed=1):
    """How a mason sets a flight out (the landing rule): the rise from the stone, the going from the stride, the run
    left over as landings. The stone gives a range of rises (a split block's own thickness, a dressed flight's era
    standard, rough stones as they come); the going is what two rises and a going of a stride (0.63 m) leave; the
    builder's patience (the town a dozen or so risers, a society a few less, owners as they please) says how many
    risers may run unbroken. The rise is drawn from the stone's range narrowed to the riser counts n whose n goings
    and the rests they need, each at least one stride and one going (landing_min), fit the run (fits()); a flight
    whose whole range fits draws what it drew before the rule. If no count fits the builder's patience, the limit of
    real practice stands in for it (18 risers, 3.3 m of rise), written as the flight's flag; if none fits that either,
    the stair cannot be built as planned and this raises (turn the stair: the plan's fault), as it does if the
    landings laid are fewer than the rests needed. A landing at a turn (the start of every flight after the first)
    gives way to the steps and their rests. Returns dict(n, r, g, S (each step's front along the flight), D (its
    tread's depth to the next front, a landing's included), start (the landing before the first step), rests (the
    landings needed), limit (the risers a run may hold), landing_min, cuts (the steps a landing follows), landings
    (their lengths), fallback (None, or the flag))."""
    a, b = f["a"], f["b"]
    run = float(np.linalg.norm((b - a)[:2]))
    H = float(b[2] - a[2])
    if f.get("form") == "step_ramp":
        n = f["n"]
        g = run / n
        return dict(n=n, r=H / n, g=g, S=[i * g for i in range(n)], D=[g] * n, start=0.0, rests=0, limit=None,
                    landing_min=None, cuts=[], landings=[], fallback=None)
    where = f"{spec.get('lane', stair_id(spec))} ({flight_id(spec, fi)})"
    nar, rng = _narrow(f, spec, fi, seed)
    if not nar["ok"]:
        raise ValueError(f"{where}: {nar['reason']}")
    n = nar["n"]
    r = H / n
    g = going_of(r)
    L = landing_min(g)
    limit = nar["patience"] if nar["fallback"] is None else practice_limit(r)
    k = rests_needed(n, limit)
    # the set-out's own check (the same rule as the narrowing)
    if not fits(n, H, run, nar["patience"] if nar["fallback"] is None else None):
        raise ValueError(f"{where}: {n} risers and {k} landings do not fit "
                         f"{run:.2f} m of run; turn the stair: the plan's fault")
    # (the landing at a turn gives way to the steps and the rests they need, never they to it)
    start = min(max(f["width"], 1.0), 1.6) if fi > 0 else 0.0
    start = max(0.0, min(start, run - n * g - k * L))
    left = run - start - n * g
    count = k
    if left > 0.0 and count == 0 and left > 0.9:
        count = 1
    if count and left / count > 3.0:
        count = int(math.ceil(left / 3.0))
    if count and left / count < L:
        count = max(k, int(left / L + 1e-9))
    if count == 0:
        # no landing: the run left over spread over the goings, as far as a stride allows (two rises and a going
        # at most STRIDE_MAX); what is left lengthens the top step
        g = min((run - start) / n, max(g, STRIDE_MAX - 2.0 * r))
        land = 0.0
    else:
        land = left / count
    # the runs between landings, as even as the builder made them
    cuts = sorted(set(int(round(n * (j + 1) / (count + 1) + rng.uniform(-1.5, 1.5))) for j in range(count)))
    cuts = [c for c in cuts if 1 <= c < n]
    if len(cuts) < k:
        raise ValueError(f"{where}: {len(cuts)} landings laid where {n} "
                         f"risers need {k} (no run over {limit}); the set-out lost one")
    if max(np.diff([0] + cuts + [n])) > limit:
        # (the builder's unevenness gives way where it would leave a run longer than the limit: each landing moved
        # no further than it must, in order up the flight)
        prev, m = 0, len(cuts)
        for j, c in enumerate(cuts):
            c = max(c, n - (m - j) * limit, prev + 1)
            cuts[j] = prev = min(c, prev + limit, n - (m - j))
    # (each landing its own length, as the ground and the builder gave it: all alike read as drawn; none shorter than
    # landing_min, what a short one lacks taken from the longer ones)
    lens = [rng.uniform(0.6, 1.4) for _ in cuts]
    lens = [land * len(cuts) * x / max(sum(lens), 1e-6) for x in lens]
    short = sum(max(0.0, L - x) for x in lens)
    over = [max(0.0, x - L) for x in lens]
    if short > 1e-9 and sum(over) > 0.0:
        lens = [max(L, x) - short * o / sum(over) for x, o in zip(lens, over)]
    land_at = dict(zip(cuts, lens))
    S, D, pos = [], [], start
    for i in range(n):
        d = g + land_at.get(i + 1, 0.0)
        S.append(pos)
        D.append(d)
        pos += d
    D[-1] = max(g, run - S[-1])
    return dict(n=n, r=r, g=g, S=S, D=D, start=start, rests=k, limit=limit, landing_min=L, cuts=cuts, landings=lens,
                fallback=nar["fallback"])


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


def top_faces(F, kind):
    """A piece's top faces (every corner of kind 0), as triangles."""
    return np.array([(f[0], f[t], f[t + 1]) for f in F if all(kind[q] == 0 for q in f)
                     for t in range(1, len(f) - 1)], dtype=np.int64).reshape(-1, 3)


def top_at(x, s, placed, tris):
    """The height of a placed piece's top under each point (x, s) in plan: read off the top face it lies over; past
    the top's edge (over a break), the nearest face's slope carried on, kept within the heights of its corners.
    placed: the piece's vertices as put placed them (x, s, z); tris: its top faces (top_faces)."""
    A, B, C = placed[tris[:, 0]], placed[tris[:, 1]], placed[tris[:, 2]]
    e0, e1 = B[:, :2] - A[:, :2], C[:, :2] - A[:, :2]
    den = e0[:, 0] * e1[:, 1] - e1[:, 0] * e0[:, 1]
    ok = np.abs(den) > 1e-12                     # (faces squashed onto a break's cut have no plan area)
    den = np.where(ok, den, 1.0)
    px, ps = x[:, None] - A[None, :, 0], s[:, None] - A[None, :, 1]
    u = (px * e1[None, :, 1] - e1[None, :, 0] * ps) / den
    v = (e0[None, :, 0] * ps - px * e0[None, :, 1]) / den
    w = 1.0 - u - v
    z = w * A[None, :, 2] + u * B[None, :, 2] + v * C[None, :, 2]
    # how far outside each face a point lies, in metres (its barycentric overshoot times the face's size)
    size = np.sqrt(np.abs(den))
    out = np.where(ok[None, :], np.maximum(np.maximum(-u, -v), np.maximum(-w, 0.0)) * size[None, :], np.inf)
    k = out.argmin(axis=1)
    rows = np.arange(len(x))
    lo = np.minimum(np.minimum(A[k, 2], B[k, 2]), C[k, 2])
    hi = np.maximum(np.maximum(A[k, 2], B[k, 2]), C[k, 2])
    return np.clip(z[rows, k], lo, hi)


def seat_dab(Pd, rel, placed, tris, x0, s0, z0, below=0.001):
    """A cement dab struck flush with the stone it is bonded to, as the stone stands now round the break (dropped with
    its half, worn, its nosing rounded): its top on the stone's top under each of its points (top_at), its highest
    point a millimetre below it (cement wears faster than slate, so it is never proud of it). Pd: the dab's vertices
    in its slab's frame, placed at x0 across, s0 along and z0 up; rel: each one's height below the dab's struck top as
    it was made (the trowel's marks, the skin feathered under the stone, the skirt down the break's face); placed and
    tris: the stone as put placed it and its top faces. Returns Pd at its new heights."""
    Pd = Pd.copy()
    Pd[:, 2] = top_at(x0 + Pd[:, 0], s0 + Pd[:, 1], placed, tris) - below + (rel - rel.max()) - z0
    return Pd


def lay(spec, seed=1, date=None):
    """The flights of one stair, laid and aged (stair_stages.py: plan, life, geometry and bake, as the runner runs
    them): each step from its life (upkeep.py), so its bed, its joints and its slabs carry their own years, and its
    repairs are spread over the flight as the years left them. date: the fabric's (YEAR, read when called). Returns
    a list of (name, mesh dict), the street origin and the plan's flags."""
    out = compose(spec, seed, date)
    return out["meshes"], out["origin"], out["flags"]


def compose(spec, seed=1, date=None):
    """The stages' outputs for a spec, its way found in the town plan (stair_stages.compose)."""
    import stair_stages as SS
    lane = lane_of(spec)
    return SS.compose(dict(spec, lane=lane["name"]), lane, seed, YEAR if date is None else date)


# the named stairs the variety sheet builds and blender/tools/setout_check.py sets out
VARIETY = ["Gully Steps", "Tanner's Steps", "Bishop's Steps", "the Hundred Steps", "the path to Lookout Park",
           "passage at -172", "passage at 92", "passage at 110", "stair-lane 2", "stair-lane 6",
           "the way to D (1107, empty since 1986)", "the Crack"]


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


# (a flag's keys in the order stone.py wrote them: the runner's cache hands dicts back in sorted order)
FLAG_KEYS = ("rule", "flight", "flag", "reason", "patience", "limit", "n", "r", "g", "rests", "run", "H", "landing_min")


def info_of(name, meshes, origin, flags):
    """The export's sidecar as LT1Stone.cs reads it (name, origin, flights) with the plan's flags: each flight's
    steps, rise, going, ends, width, step fronts, triangles and life. The stages' additions follow it (sidecar())."""
    flags = [dict(sorted(f.items(), key=lambda kv: FLAG_KEYS.index(kv[0]) if kv[0] in FLAG_KEYS else len(FLAG_KEYS)))
             for f in flags]
    return dict(name=name, origin=[float(v) for v in origin], flags=flags,
                flights=[dict(name=nm, steps=m["steps"], rise=round(m["rise"], 3), tread=round(m["tread"], 3),
                              a=m["a"], b=m["b"], width=m["width"], S=m["S"],
                              tris=sum(len(f) - 2 for f in m["F"]), life=m["life"]) for nm, m in meshes])


def make_all(meshes):
    """The scene emptied and the meshes made in it."""
    import bpy
    for ob in list(bpy.data.objects):
        bpy.data.objects.remove(ob, do_unlink=True)
    return [make(name, m) for name, m in meshes]


def _export_fbx(path, obs):
    import bpy
    bpy.ops.object.select_all(action="DESELECT")
    for ob in obs:
        ob.select_set(True)
    bpy.context.view_layer.objects.active = obs[0]
    bpy.ops.export_scene.fbx(filepath=path, use_selection=True, object_types={"MESH"}, axis_forward="Z",
                             axis_up="Y", bake_space_transform=True, apply_unit_scale=True,
                             apply_scale_options="FBX_SCALE_ALL", mesh_smooth_type="OFF", colors_type="LINEAR",
                             use_mesh_modifiers=False, add_leaf_bones=False, bake_anim=False, path_mode="STRIP",
                             embed_textures=False)


def _write_if_changed(path, text):
    if os.path.exists(path):
        with open(path) as fh:
            if fh.read() == text:
                return False
    with open(path, "w") as fh:
        fh.write(text)
    return True


def install_lock(path):
    """The Unity lock (tools/unity_lock.py) for an install step into unity/Assets only: it waits while a Unity run, a
    timing run or the editor has the project, so none of them sees an installed file rewritten under it."""
    tools = os.path.normpath(os.path.join(HERE, "..", "..", "tools"))
    if tools not in sys.path:
        sys.path.append(tools)
    import unity_lock  # noqa: E402
    return unity_lock.installing(path)


def write_export(path, meshes, info, obs=None):
    """The meshes (made now unless obs are given) written to path as FBX, the sidecar beside it as <name>.json, and
    the mesh hashes into the manifest beside them (blender/tools/mesh_hash.py). Returns the file's manifest entry.

    An installed file is rewritten only when it changes: the FBX is exported to a scratch folder and hashed first, and
    when the installed one hashes the same, mesh for mesh and channel for channel, it is left as it is (an FBX's bytes
    differ at every export by its header's time, and Unity imports a rewritten file again); the sidecar and the
    manifest are written only when their text differs."""
    import shutil
    import tempfile
    obs = obs or make_all(meshes)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tools = os.path.normpath(os.path.join(HERE, "..", "tools"))
    if tools not in sys.path:
        sys.path.append(tools)
    import mesh_hash  # noqa: E402
    scratch = tempfile.mkdtemp(prefix="stone-export-")
    try:
        trial = os.path.join(scratch, os.path.basename(path))
        _export_fbx(trial, obs)
        new = mesh_hash.entry(trial)
    finally:
        shutil.rmtree(scratch, ignore_errors=True)
    with install_lock(path):                  # the install step, under the Unity lock
        old = mesh_hash.entry(path) if os.path.exists(path) else None
        if old == new:
            print("FBX", path, "unchanged: left as it is")
        else:
            _export_fbx(path, obs)
            print("FBX", path)
        _write_if_changed(path[:-4] + ".json", json.dumps(info, indent=1))
        manifest = mesh_hash.manifest_path(path)
        held = {}
        if os.path.exists(manifest):
            with open(manifest) as fh:
                held = json.load(fh)
        if old == new and held.get(os.path.basename(path)) == new:
            print("HASH", os.path.basename(path), new["hash"], f"{new['triangles']} triangles", "(unchanged) ->",
                  manifest)
            return new
        return mesh_hash.write_manifest(path)     # the mesh hashes beside the export


def build(which, unity=None, seed=1, spec=None, folder=""):
    """One stair: the beauty corner's own by its key in FLIGHTS, or any flight in the plan from its spec (stair_facts),
    written to Assets/Art/Stone/<folder>/stone_<which>.fbx and .json (the stages' sidecar keys after stone.py's)."""
    import stair_stages as SS
    spec = spec or FLIGHTS[which]
    lane = lane_of(spec)
    spec = dict(spec, lane=lane["name"])
    out = SS.compose(spec, lane, seed, YEAR)
    meshes, origin, flags = out["meshes"], out["origin"], out["flags"]
    if not meshes:
        print("STONE", which, "nothing built:", flags)
        return dict(name=f"stone_{which}", flags=flags)
    obs = make_all(meshes)
    info = info_of(f"stone_{which}", meshes, origin, flags)
    info.update(SS.sidecar(spec, out["plan"], out["life"], out["geometry"]))
    print("STONE", {k: v for k, v in info.items() if k in ("name", "origin", "flags")},
          [(f["name"], f["steps"], f["tris"]) for f in info["flights"]])
    if unity:
        write_export(os.path.join(unity, "Assets", "Art", "Stone", folder, f"stone_{which}.fbx"), meshes, info, obs)
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
        names = argv[2:] or VARIETY
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
            facts_path = os.path.join(unity, "Assets", "Art", "Stone", "Variety", f"stone_{slug(nm)}.facts.json")
            with install_lock(facts_path), open(facts_path, "w") as fh:
                json.dump(facts, fh, indent=1)
    else:
        build(which, unity)
