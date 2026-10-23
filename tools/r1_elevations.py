"""Port step 2b, rung R1: the gully's cheek walls and steps laid as 2D elevations in integer millimetres, by a mason's
rules, before any mesh (reviews/lt1/port/2b/design.md, The ladder; SN2, SN3, SN8, SN9, SN10). The laying is
blender/generators/masonry.py; this tool gathers its facts, measures which wall faces are seen, runs the laying, checks
it, times it and draws the sheet.

    PY=/Applications/Blender.app/Contents/Resources/5.2/python/bin/python3.13
    $PY tools/r1_elevations.py facts         the facts, once: the stair's plan from its stages (tools/run_kind.py), the
                                             ground behind each wall and wall.py's own fact draws (Blender, about 2 min)
                                             -> reviews/lt1/port/2b/r1/facts.json, in integer mm, without a visibility
    $PY tools/r1_elevations.py visibility    which panel faces are seen, from the six judging views and the walkable
                                             ground at 1.6 m, with the terrain and the walls as occluders (numpy, about
                                             5 min, most of it importing the clay's layout) -> facts.json's
                                             walls.visibility, and visibility.png
    $PY tools/r1_elevations.py hash [G]      the layout's hash with G goings to a level run of coping, in this process
                                             alone (the determinism check runs it as a second process)
    $PY tools/r1_elevations.py               the layout from facts.json, both variants (two goings and one), each laid
                                             twice and once in a second process; the tests, the counts against SN8, the
                                             timing; layout.json, report.md and the sheet

The facts are rounded to integer mm here, at the boundary, and nowhere else (the rounding is recorded in facts.json).
The visibility is a measurement in floats (metres), like the ground's: what enters the facts is only whether each
panel face is laid stone by stone, and its areas rounded to cm2.
"""
import json
import math
import os
import statistics
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "blender", "generators"))
sys.path.insert(0, os.path.join(ROOT, "blender", "resolver"))
BLOCKOUTS = os.path.join(ROOT, "blender", "blockouts")

OUT = os.path.join(ROOT, "reviews", "lt1", "port", "2b", "r1")
FACTS = os.path.join(OUT, "facts.json")
BLENDER = "/Applications/Blender.app/Contents/MacOS/Blender"
BPY = "/Applications/Blender.app/Contents/Resources/5.2/python/bin/python3.13"
RECORD = os.path.join(ROOT, "fixtures", "records", "st-gully.json")
GOLDEN_PLAN = "a99de7262eee1c2b"     # fixtures/golden/stair/plan.json's output hash
FACES = ("stair", "bank")
# The workings the gully's facts name (packs/stavanger-1989/walling.json): wall.py's gully_cheeks is slate, built in
# 1874, dry; its works list the 1961 rebuild (cement, reclaimed stock); the stair is block steps of split slate. They
# are authored here, like wall.py's other facts, until a wl-gully record holds them
WORKINGS = dict(walls="dry-split-1874", rebuilt="cement-relaid-1961", stair="dry-split-1874")

# The judging views (unity/Assets/Code/Editor/LT1Stone.cs, Views; read, never edited): name, eye, target (street
# metres, z up), vertical field of view in degrees; frames 2560 x 1440
VIEWS = [
    ("eye-foot", (49.8, 21.4, 4.7), (48.6, 30.7, 5.9), 37.8),
    ("eye-on", (49.6, 28.4, 5.95), (48.7, 33.5, 6.4), 37.8),
    ("eye-down", (50.2, 27.0, 5.5), (49.1, 29.2, 4.4), 37.8),
    ("street", (49.3, 12.0, 5.6), (47.5, 44.0, 10.5), 46.4),
    ("into12", (56.0, 18.0, 15.0), (48.6, 30.7, 5.5), 46.4),
    ("high", (80.0, 2.0, 60.0), (48.5, 36.0, 7.0), 15.0),
]
ASPECT = 2560 / 1440
EYE = 1.6           # m, a standing eye over the walkable ground
RANGE = 80.0        # m, the farthest eye counted
RANGE_WIDE = 120.0  # m, the sensitivity's
NEAR = 8.0          # m, L0's range: a face seen only from farther is seen only at L1
SAMPLE = 220        # mm, the samples' spacing along each course, at its mid-height
WALL_TOP = (0.15, 0.57)  # m, an occluding wall's top as a slab outside the stair's clear half-width (its batter at a
                         # 900 mm parapet, and the 0.42 m top)

# SN8's table and estimate (design.md)
TRI = dict(face=(40, 16), coping=(120, 48), head=(120, 48), through=(120, 48), topstone=(120, 48))
STEP_TRI = (300, 120)
FILL_TRI = (8, 8)
SN8 = dict(walls=(110000, 45000), stairs=(40000, 16000), gully=(150000, 65000), faceM2=140, wallStones=2700,
           copings=150, steps=78, stonesAStep=1.6, triAStone=250, rests=8000)

READ = """**The coordinator's read (22 October, 22:20).** Not passed. The next round starts from three decisions.
- **One course a rise.** The 140 mm maximum course came from `wall.py`. The town's own walls (`docs/references/stone/` 31 and 36) are thick split slabs, so the course range rises to cover a rise (up to about 190 mm), with one course on each step top as SN2 already allows. That roughly halves the stone count.
- **The back faces.** All four walls are parapets (`retains: false` in the clay's ground), so both faces are seen from somewhere. Measure which back faces the five judging views and the walkable ground can see before deciding how they are laid.
- **The budget.** SN8's 110k for the walls assumed 140 m² of face, and the walls have 212.5 m². Re-derive it from the faces that are seen, then hold to it."""

ROUND1 = dict(wallStones=8620, faceStones=8301, copings=106, kneelers=22, knees=18, throughs=71, heads=96,
              topstones=6, faceM2=212.5, stepStones=170, l0Walls=370320, l0Stairs=51000, l0Gully=421320,
              hash="aec969068f3406f1", checks=37, passing=34, laps=18, crosses=5, chains=13, chainsTops=8, independent=32,
              panels=40)


def mm(x):
    """Metres to integer mm, half away from zero: the one rounding, at the facts' boundary."""
    v = float(x) * 1000.0
    return int(math.floor(v + 0.5)) if v >= 0 else -int(math.floor(-v + 0.5))


# ---------------------------------------------------------------------------------------------------------------
# Inside Blender: the ground behind each wall line, and wall.py's own fact draws (read, never its laying)

def blender_ground(out_path):
    import numpy as np
    import hashing as HS
    import wall as WL          # (first: it puts blender/blockouts on the path)
    import heart_layout as H
    import stone as ST
    spec = WL.WALLS["gully_cheeks"]
    seed = 1                                   # wall.py's seed today (its build's default): these are today's facts
    wid = spec["id"]
    lane = next(l for l in H.LANES if l["name"] == spec["lane"])
    fl = ST.flights_of(lane)
    res = dict(flights=[], lines=[])
    for fi, f in enumerate(fl):
        a, b, W = f["a"], f["b"], f["width"]
        d2 = (b - a)[:2]
        run = float(np.linalg.norm(d2))
        up = d2 / run
        right = np.array([up[1], -up[0]])
        slope = float(b[2] - a[2]) / run
        ground = WL.ground_near(f)
        sp = ST.step_plan(f, ST.FLIGHTS["gully"], fi, seed)
        S_arr = np.array(sp["S"])

        def step_top(s):
            k = np.searchsorted(S_arr, np.asarray(s), side="right")
            return a[2] + np.clip(k, 0, sp["n"]) * sp["r"]

        PL = WL.pitch_line(sp, float(a[2]))

        def pitch(s):
            return np.interp(s, PL[:, 0], PL[:, 1])

        courses_line = WL.eased(PL, -0.3, run + 0.3)

        def base(s):
            return courses_line(s) - sp["r"] - WL.FOOT

        bends = [float(q) for q in PL[:, 0] if -0.3 < q < run + 0.3]
        rise_of = {sd: np.mean([ground(*(a[:2] + up * s_ + right * sd * (W / 2 + 2.5))) - (a[2] + s_ * slope)
                                for s_ in np.linspace(0, run, 6)]) for sd in (1, -1)}
        bank_side = max(rise_of, key=rise_of.get)
        res["flights"].append(dict(index=fi, run=run, a=[float(v) for v in a], b=[float(v) for v in b], width=float(W),
                                   S=[float(v) for v in sp["S"]], n=int(sp["n"]), r=float(sp["r"]), g=float(sp["g"]),
                                   pitch=[[float(p), float(q)] for p, q in PL], bankSide=int(bank_side)))
        for side in (1, -1):
            pnl = f"{wid}/fl-{fi}/{'r' if side > 0 else 'l'}"
            ss = np.unique(np.concatenate([np.linspace(-0.3, run + 0.3, max(8, int(run / 0.5))), bends]))
            bank = np.array([ground(*(a[:2] + up * s + right * side * (W / 2 + 0.7))) for s in ss])
            grade = a[2] + np.clip(ss, 0.0, run) * slope
            retain = WL.stretches(ss, bank > grade + WL.RETAINS)
            top_line = np.maximum(np.where(retain, np.minimum(bank + 0.05, step_top(ss) + 3.0), pitch(ss) + WL.PARAPET),
                                  bank + 0.05)
            panel = None
            for w in spec["works"]:
                if w["kind"] == "rebuilt" and side == bank_side and fi == 0:
                    prng = HS.Stream(seed, pnl, "rebuilt", w["year"])
                    L_ = prng.uniform(*w["length"])
                    s0 = prng.uniform(0.15, 0.35) * run
                    panel = dict(s=[s0, s0 + L_], year=w["year"], mortar=w["mortar"], stock=w["stock"], cause=w["cause"])
            ends_p = list(panel["s"]) if panel is not None else []
            crng0 = HS.Stream(seed, pnl, "copes")
            copes, s_c = [], -0.3
            while s_c < run + 0.3:
                e_c = min(s_c + crng0.uniform(0.45, 1.0), run + 0.3)
                nb = next((q for q in sorted(bends + ends_p) if s_c + 0.25 <= q < e_c + 0.25), None)
                if nb is not None:
                    e_c = nb
                copes.append((s_c, e_c))
                s_c = e_c
            jts = np.array([copes[0][0]] + [e_c for _, e_c in copes])
            top_j = np.interp(jts, ss, top_line)

            def top(s):
                return np.interp(s, jts, top_j)

            wrng = HS.Stream(seed, pnl, "patchwork")
            fallen = [wrng.uniform(0.0, run) for _ in range(wrng.randint(1, 3))]
            patched = wrng.uniform(0.0, run)
            fall_h = [1.0 - wrng.random() ** 2 for _ in fallen]

            def cemented(sm):
                return (panel is not None and panel["s"][0] <= sm <= panel["s"][1]) or abs(sm - patched) < 0.35

            falls = []
            for fs, fz in zip(fallen, fall_h):
                lo, hi = 0.3 + sp["r"], float(top(fs) - base(fs)) - 0.12
                if hi > lo:
                    hf = lo + fz * (hi - lo)
                    falls.append(dict(s=float(fs), z=float(base(fs) + hf), held=bool(cemented(fs))))
            gs = np.arange(-0.3, run + 0.3 + 1e-9, 0.1)
            if gs[-1] < run + 0.3 - 1e-6:
                gs = np.append(gs, run + 0.3)
            gz = [float(ground(*(a[:2] + up * s + right * side * (W / 2 + 0.7)))) for s in gs]
            res["lines"].append(dict(id=pnl, flight=fi, side=side, run=run, retain=bool(np.any(retain)),
                                     ground=[[float(s), z] for s, z in zip(gs, gz)], rebuilt=panel, falls=falls,
                                     patched=float(patched)))
    with open(out_path, "w") as fh:
        json.dump(res, fh)
    print("ground written", out_path)


# ---------------------------------------------------------------------------------------------------------------
# The facts, in integer mm

def gather_facts():
    import hashes as HX
    tmp = tempfile.mkdtemp(prefix="r1-facts-")
    plan_dir = os.path.join(tmp, "plan")
    r = subprocess.run([BPY, os.path.join(ROOT, "tools", "run_kind.py"), RECORD, "--until", "plan", "--no-cache",
                        "--out", plan_dir], cwd=ROOT, capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit("run_kind failed:\n" + r.stdout + r.stderr)
    plan = json.load(open(os.path.join(plan_dir, "plan.json")))
    run = json.load(open(os.path.join(plan_dir, "run.json")))
    plan_hash = next(s["output"] for s in run["stages"] if s["stage"] == "plan")
    gpath = os.path.join(tmp, "ground.json")
    r = subprocess.run([BLENDER, "-b", "--factory-startup", "--python", os.path.abspath(__file__), "--", "ground", gpath],
                       cwd=ROOT, capture_output=True, text=True)
    if r.returncode != 0 or not os.path.exists(gpath):
        sys.exit("Blender ground failed:\n" + r.stdout[-4000:] + r.stderr[-4000:])
    gr = json.load(open(gpath))
    kind = json.load(open(os.path.join(ROOT, "kinds", "stair.json")))
    pack = json.load(open(os.path.join(ROOT, "packs", "stavanger-1989", "pack.json")))
    o = plan["output"]
    flights = []
    for fid in o["flightIds"]:
        F = o["flights"][fid]
        sp = F["setout"]
        gf = gr["flights"][F["index"]]
        a, b = F["a"], F["b"]
        run_m = math.hypot(b[0] - a[0], b[1] - a[1])
        steps = []
        for i, tid in enumerate(F["steps"]):
            st = o["steps"][tid]
            steps.append(dict(id=tid, index=i, S=mm(st["S"]), D=mm(st["D"]), zTop=mm(st["zTop"]), zFoot=mm(st["zFoot"])))
        # the pitch line (wall.py's pitch_line: through each nosing at its nominal height, level across each landing
        # to a going short of the next, a going below the first nosing), from the plan's set-out
        n, rr, g, S = sp["n"], sp["r"], sp["g"], sp["S"]
        z0 = a[2]
        P = [(S[0] - g, z0)]
        for i in range(n):
            P.append((S[i], z0 + (i + 1) * rr))
            if i < n - 1 and S[i + 1] - S[i] > g + 1e-6:
                P.append((S[i + 1] - g, z0 + (i + 1) * rr))
        keep = [P[0]]
        for i in range(1, len(P) - 1):
            k0 = (P[i][1] - P[i - 1][1]) / (P[i][0] - P[i - 1][0])
            k1 = (P[i + 1][1] - P[i][1]) / (P[i + 1][0] - P[i][0])
            if abs(k1 - k0) > 1e-6:
                keep.append(P[i])
        keep.append(P[-1])
        pitch = [[mm(p), mm(q)] for p, q in keep]
        wl_pitch = [[mm(p), mm(q)] for p, q in gf["pitch"]]
        flights.append(dict(id=fid, index=F["index"], a=[mm(v) for v in a], b=[mm(v) for v in b], run=mm(run_m),
                            width=mm(F["width"]), n=n, g=mm(g), r=mm(rr), start=mm(sp["start"]), zFoot=mm(a[2]),
                            steps=steps, pitch=pitch, pitchMatchesWallPy=(pitch == wl_pitch),
                            setoutMatchesWallPy=([mm(v) for v in S] == [mm(v) for v in gf["S"]])))
    lines = []
    for ln in gr["lines"]:
        f = flights[ln["flight"]]
        reb = ln["rebuilt"]
        lines.append(dict(id=ln["id"], flight=ln["flight"], side=ln["side"], s0=-300, s1=f["run"] + 300,
                          retains=ln["retain"],
                          ground=[[mm(s), mm(z)] for s, z in ln["ground"]],
                          rebuilt=None if reb is None else dict(s=[mm(reb["s"][0]), mm(reb["s"][1])], year=reb["year"],
                                                                mortar=reb["mortar"], stock=reb["stock"],
                                                                cause=reb["cause"], working=WORKINGS["rebuilt"]),
                          falls=[dict(s=mm(fp["s"]), z=mm(fp["z"]), held=fp["held"]) for fp in ln["falls"]],
                          patched=mm(ln["patched"])))
    slab = kind["stages"]["plan"]["params"]["slabWidthsMm"]["other"]
    facts = dict(
        what="R1's facts (port step 2b): the gully stair's plan and its walls' facts in integer mm, gathered by "
             "tools/r1_elevations.py facts; the laying (blender/generators/masonry.py) reads only this",
        worldSeed=pack["worldSeed"],
        rounding="every length and height is rounded here, once, from the stages' metres to integer mm, half away "
                 "from zero; nothing downstream rounds a fact again",
        sources=dict(
            plan=dict(tool="tools/run_kind.py fixtures/records/st-gully.json --until plan --no-cache", hash=plan_hash,
                      golden=GOLDEN_PLAN, matchesGolden=(plan_hash == GOLDEN_PLAN),
                      seed="the stair kind's legacySeed (1): today's set-out, which R1 must be re-run on when 2b "
                           "retires legacySeed"),
            ground="the clay's carved ground (wall.py's ground_near: blender/blockouts/heart_build.py's 1.5 m grid), "
                   "sampled every 100 mm at 0.7 m behind each wall's face line, where wall.py reads its bank",
            wallFacts="wall.py's own fact draws at its seed today (1): the 1961 panel's place and length and the fall "
                      "points (and which are held by cement). They are authored in code, not yet in a wl-gully record",
            stepStone=dict(source="kinds/stair.json, plan params slabWidthsMm.other (split slate)", lo=slab["lo"],
                           hi=slab["hi"])),
        stair=dict(id="st-gully", builtAs=o["builtAs"], finish=o["finish"], working=WORKINGS["stair"],
                   flights=flights),
        walls=dict(id="wl-gully", built=1874, working=WORKINGS["walls"], lines=lines),
    )
    os.makedirs(OUT, exist_ok=True)
    with open(FACTS, "w") as fh:
        json.dump(facts, fh, indent=1, sort_keys=True)
    print("facts written", FACTS, "hash", HX.hash_hex(facts), "plan", plan_hash,
          "matches golden" if plan_hash == GOLDEN_PLAN else "DIFFERS FROM GOLDEN")
    print("the facts have no visibility now: run `r1_elevations.py visibility` next")


_DATA = {}


def data():
    """The data the walls are laid from (masonry.load_data: kinds/wall.json's plan params and the pack's walling
    table), read once a process."""
    import masonry as M
    if not _DATA:
        _DATA.update(M.load_data(ROOT))
    return _DATA


def rules(M, facts, wall_id=None, dat=None):
    """The masonry.Rules a wall line (by its id), or with none the stair's steps, is laid and tested by (from the
    pack's data, or `dat`)."""
    ln = next(l_ for l_ in facts["walls"]["lines"] if l_["id"] == wall_id) if wall_id else None
    return M.rules_for(facts, dat or data(), ln)


VARIANT = os.path.join(OUT, "granite-1930.json")


def variant_inputs(facts):
    """design.md 7b's check: the test record's workings merged into a copy of the pack's walling table, and a copy of
    the facts naming them (the walls' working and the rebuilt panel's); nothing else changes."""
    rec = json.load(open(VARIANT))
    dat = json.loads(json.dumps(data()))
    clash = sorted(set(rec["workings"]) & set(dat["walling"]["workings"]))
    if clash:
        sys.exit(f"the test record's workings {clash} are the pack's own")
    dat["walling"]["workings"].update(rec["workings"])
    f2 = json.loads(json.dumps(facts))
    f2["walls"]["working"] = rec["applies"]["walls"]
    for ln in f2["walls"]["lines"]:
        if ln.get("rebuilt"):
            ln["rebuilt"]["working"] = rec["applies"]["rebuilt"]
    return rec, dat, f2


def variant(facts, M, g):
    """The granite wall from data alone: laid twice (the hashes must match), tested by the same checks, counted."""
    import hashes as HX
    rec, dat, f2 = variant_inputs(facts)
    out = {}
    for G in (2, 1):
        try:
            lay = M.lay(f2, dat, goings=G)
        except M.Refused as e:
            out[G] = dict(refused=str(e))
            continue
        h1, h2 = HX.hash_hex(lay), HX.hash_hex(M.lay(f2, dat, goings=G))
        T = run_tests(lay, f2, M, g, dat)
        C = counts(lay)
        flags = [x for w in lay["walls"] for x in w["report"]["flags"]]
        cuts = [x for w in lay["walls"] for x in w["report"]["cuts"]]
        fills = [x for w in lay["walls"] for x in w["report"]["fills"]]
        out[G] = dict(layout=lay, hashes=(h1, h2), T=T, C=C, flags=flags, cuts=cuts, fills=fills)
    return rec, out


def without_visibility(facts):
    f2 = json.loads(json.dumps(facts))
    f2["walls"].pop("visibility", None)
    return f2


# ---------------------------------------------------------------------------------------------------------------
# Which wall faces are seen (numpy, floats: a measurement, like the ground's)

class Terrain:
    """The clay's carved ground (heart_layout.carve over centre_land.heights) on its own 1.5 m grid, sampled
    bilinearly as heart_build._sample does, and inside each flight's clear width the steps' own treads."""

    def __init__(self, np, H, L, facts, bbox, reach):
        self.np = np
        hx0, hy0 = H.HEART[0], H.HEART[1]
        x0 = hx0 + math.floor((bbox[0] - reach - 3 - hx0) / 1.5) * 1.5
        y0 = hy0 + math.floor((bbox[1] - reach - 3 - hy0) / 1.5) * 1.5
        self.xs = np.arange(x0, bbox[2] + reach + 3 + 0.75, 1.5)
        self.ys = np.arange(y0, bbox[3] + reach + 3 + 0.75, 1.5)
        X, Y = np.meshgrid(self.xs, self.ys, indexing="ij")
        self.Z = H.carve(X, Y, L.heights(X, Y))
        self.flights = []
        for fl in facts["stair"]["flights"]:
            a = np.array(fl["a"], float) / 1000
            b = np.array(fl["b"], float) / 1000
            d = b[:2] - a[:2]
            run = float(np.hypot(*d))
            up = d / run
            self.flights.append(dict(a=a, up=up, right=np.array([up[1], -up[0]]), run=run,
                                     hw=fl["width"] / 2000 + 0.006, S=np.array([st["S"] for st in fl["steps"]]) / 1000,
                                     tops=np.array([fl["zFoot"]] + [st["zTop"] for st in fl["steps"]]) / 1000))

    def __call__(self, px, py):
        np = self.np
        u = np.clip((px - self.xs[0]) / 1.5, 0, len(self.xs) - 1.001)
        v = np.clip((py - self.ys[0]) / 1.5, 0, len(self.ys) - 1.001)
        i, j = u.astype(np.int64), v.astype(np.int64)
        fu, fv = u - i, v - j
        Z = self.Z
        a = Z[i, j] + (Z[i + 1, j] - Z[i, j]) * fu
        b = Z[i, j + 1] + (Z[i + 1, j + 1] - Z[i, j + 1]) * fu
        z = a + (b - a) * fv
        for f in self.flights:
            rx, ry = px - f["a"][0], py - f["a"][1]
            s = rx * f["up"][0] + ry * f["up"][1]
            t = rx * f["right"][0] + ry * f["right"][1]
            on = (np.abs(t) <= f["hw"]) & (s >= 0) & (s <= f["run"])
            if on.any():
                z[on] = f["tops"][np.searchsorted(f["S"], s[on], side="right")]
        return z


def line_geometry(np, facts, layout):
    """Each wall line in plan (metres): its flight's foot, uphill and right unit vectors, its side, the stair's clear
    half-width at the face, its ends, its coping's top and its stair footing along s."""
    geo = []
    for ln, w in zip(facts["walls"]["lines"], layout["walls"]):
        fl = facts["stair"]["flights"][ln["flight"]]
        a = np.array(fl["a"], float) / 1000
        b = np.array(fl["b"], float) / 1000
        d = b[:2] - a[:2]
        up = d / float(np.hypot(*d))
        geo.append(dict(id=w["id"], a=a, up=up, right=np.array([up[1], -up[0]]), sd=ln["side"],
                        hw=fl["width"] / 2000 + 0.006, s0=w["s"][0] / 1000, s1=w["s"][1] / 1000,
                        cs=np.array([c["s"][0] for c in w["ceiling"]], float) / 1000,
                        ct=np.array([c["top"] for c in w["ceiling"]], float) / 1000,
                        fs=np.array([a_ for a_, b_, z_ in w["footing"]["stair"]], float) / 1000,
                        fz=np.array([z_ for a_, b_, z_ in w["footing"]["stair"]], float) / 1000))
    return geo


def step_at(np, starts, vals, s):
    return vals[np.clip(np.searchsorted(starts, s, side="right") - 1, 0, len(vals) - 1)]


def wall_samples(np, layout, geo, T):
    """A sample every SAMPLE mm along each course of each panel face, at the course's mid-height, 20 mm off the face
    along its normal (the faces battered 1 in 6, as wall.py's), each with the face area it stands for."""
    rows = []
    for li, w in enumerate(layout["walls"]):
        Lz = [l_["z"] for l_ in w["lines"]]
        for fi, f in enumerate(FACES):
            for m, runs in enumerate(w["regions"][f]):
                h = Lz[m + 1] - Lz[m]
                zc = (Lz[m] + Lz[m + 1]) / 2
                for r in runs:
                    for pi, pn in enumerate(w["panels"]):
                        lo, hi = max(r["a"], pn["s"][0]), min(r["b"], pn["s"][1])
                        if hi <= lo:
                            continue
                        n = max(1, -(-(hi - lo) // SAMPLE))
                        for i in range(n):
                            rows.append((li, fi, pi, m, lo + (hi - lo) * (2 * i + 1) / (2 * n), zc, (hi - lo) * h / n,
                                         (hi - lo) / n, h))
    A = np.array(rows, float)
    li, fi = A[:, 0].astype(int), A[:, 1].astype(int)
    s, z = A[:, 4] / 1000, A[:, 5] / 1000
    P = np.zeros((len(A), 3))
    N = np.zeros((len(A), 3))
    buried = np.zeros(len(A), bool)
    for k, g in enumerate(geo):
        sel = li == k
        ss, zz = s[sel], z[sel]
        zf = step_at(np, g["fs"], g["fz"], ss)
        top = step_at(np, g["cs"], g["ct"], ss)
        ts = g["hw"] + (zz - zf) / 6
        tb = g["hw"] + (top - zf) / 6 + 0.42 + (top - zz) / 6
        face_bank = fi[sel] == 1
        t = np.where(face_bank, tb, ts)
        out_sign = np.where(face_bank, 1.0, -1.0) * g["sd"]       # the face's outward side, in units of right
        xy = g["a"][:2] + ss[:, None] * g["up"] + (g["sd"] * t)[:, None] * g["right"]
        nrm = np.concatenate([out_sign[:, None] * g["right"], np.full((sel.sum(), 1), 1 / 6)], axis=1)
        nrm /= np.linalg.norm(nrm, axis=1)[:, None]
        P[sel] = np.concatenate([xy, zz[:, None]], axis=1) + 0.02 * nrm
        N[sel] = nrm
        q = xy + (0.1 * out_sign)[:, None] * g["right"]
        buried[sel] = T(q[:, 0], q[:, 1]) > zz
    return dict(A=A, P=P, N=N, buried=buried, line=li, face=fi, panel=A[:, 2].astype(int), course=A[:, 3].astype(int),
                s=A[:, 4], z=A[:, 5], area=A[:, 6], ds=A[:, 7], h=A[:, 8])


def eye_points(np, H, L, T, bbox, reach, yards=True):
    """Standing eyes over the walkable ground within `reach` of the walls: every lane, stair and quay of the clay
    (heart_layout.LANES) every 1.75 m along and about 1.5 m across, 0.3 m in from its edges; the Landing, the small
    places and the market square, and the yards, on a 1.5 m grid; none inside a house's footprint. z: the ground (the
    treads on a stair) + 1.6 m."""
    pts, kinds, names = [], [], []
    seen = set()

    def near(x, y):
        dx = max(bbox[0] - x, 0, x - bbox[2])
        dy = max(bbox[1] - y, 0, y - bbox[3])
        return math.hypot(dx, dy) <= reach

    def add(x, y, kind, name):
        k = (round(x, 3), round(y, 3))
        if k in seen or not near(x, y):
            return
        seen.add(k)
        pts.append((x, y))
        kinds.append(kind)
        names.append(name)
    for lane in H.LANES:
        P = lane["pts"]
        hw = max(0.0, lane["width"] / 2 - 0.3)
        nac = int(2 * hw // 1.5) + 1
        if nac % 2 == 0:
            nac += 1
        offs = [0.0] if nac == 1 else [-hw + 2 * hw * i / (nac - 1) for i in range(nac)]
        for p, q in zip(P, P[1:]):
            x1, y1, x2, y2 = float(p[0]), float(p[1]), float(q[0]), float(q[1])
            Lg = math.hypot(x2 - x1, y2 - y1)
            if Lg < 1e-6:
                continue
            n = max(1, math.ceil(Lg / 1.75))
            px, py = -(y2 - y1) / Lg, (x2 - x1) / Lg
            for i in range(n + 1):
                cx, cy = x1 + (x2 - x1) * i / n, y1 + (y2 - y1) * i / n
                for o in offs:
                    add(cx + px * o, cy + py * o, "lane", lane["name"])
    places = [("the Landing", H.LANDING, "place")] + [(n_, poly, "place") for n_, poly, _ in H.SMALL_PLACES] + \
        [("the market square", H.MARKET_SQUARE, "place")] + \
        ([(f"yard {i}", poly, "yard") for i, (poly, _) in enumerate(H.YARDS)] if yards else [])
    for name, poly, kind in places:
        poly = [(float(x), float(y)) for x, y in poly]
        xs_, ys_ = [p[0] for p in poly], [p[1] for p in poly]
        gx, gy = np.meshgrid(np.arange(min(xs_) + 0.75, max(xs_), 1.5), np.arange(min(ys_) + 0.75, max(ys_), 1.5),
                             indexing="ij")
        ins = L._inside(poly, gx, gy)
        for x, y in zip(gx[ins].tolist(), gy[ins].tolist()):
            add(x, y, kind, name)
    E = np.array(pts, float)
    drop = np.zeros(len(E), bool)
    for b in H.BUILDINGS:
        fp = [(float(x), float(y)) for x, y in H.footprint(b)]
        if not near(*fp[0]) and not near(*fp[2]):
            continue
        drop |= L._inside(fp, E[:, 0], E[:, 1])
    keep = ~drop
    E = E[keep]
    kinds = [k for k, kp in zip(kinds, keep) if kp]
    names = [n_ for n_, kp in zip(names, keep) if kp]
    z = T(E[:, 0], E[:, 1]) + EYE
    return np.concatenate([E, z[:, None]], axis=1), kinds, names, int(drop.sum())


def house_boxes(np, H, bbox, reach):
    """The sensitivity's occluders: each house of the clay within reach as a box over its footprint up to its eaves
    (heart_build: base + eave; below the base its plinth or the ground), its roof left out, so it blocks no more than
    the house would."""
    out = []
    for b in H.BUILDINGS:
        fp = np.array(H.footprint(b), float)
        x0, y0 = fp.min(axis=0)
        x1, y1 = fp.max(axis=0)
        if x1 < bbox[0] - reach or x0 > bbox[2] + reach or y1 < bbox[1] - reach or y0 > bbox[3] + reach:
            continue
        out.append((fp, (x0, y0, x1, y1), float(b["base"]) + float(b["eave"])))
    return out


def houses_block(np, P, E, houses):
    """For each ray P -> E: whether it passes through a house's box (its footprint, under its eaves): the segment
    clipped to the footprint's four half-planes, then its height over that stretch against the eaves."""
    blk = np.zeros(len(P), bool)
    if not len(P):
        return blk
    D = E - P
    lo_xy, hi_xy = np.minimum(P[:, :2], E[:, :2]), np.maximum(P[:, :2], E[:, :2])
    for fp, (x0, y0, x1, y1), ztop in houses:
        idx = np.nonzero(~blk & (hi_xy[:, 0] >= x0) & (lo_xy[:, 0] <= x1) & (hi_xy[:, 1] >= y0) &
                         (lo_xy[:, 1] <= y1))[0]
        if not len(idx):
            continue
        t0 = np.zeros(len(idx))
        t1 = np.ones(len(idx))
        ok = np.ones(len(idx), bool)
        cx, cy = fp[:, 0].mean(), fp[:, 1].mean()
        for k in range(4):
            ax, ay = fp[k]
            bx, by = fp[(k + 1) % 4]
            nx, ny = by - ay, ax - bx                      # an edge normal; flipped to point outwards
            if nx * (cx - ax) + ny * (cy - ay) > 0:
                nx, ny = -nx, -ny
            num = -((P[idx, 0] - ax) * nx + (P[idx, 1] - ay) * ny)    # inside where n.(p - a) <= 0
            den = D[idx, 0] * nx + D[idx, 1] * ny
            par = np.abs(den) < 1e-12
            ok &= ~(par & (num < 0))
            t = np.where(par, 0.0, num / np.where(par, 1.0, den))
            ent = ~par & (den < 0)
            ext = ~par & (den > 0)
            t0 = np.where(ent, np.maximum(t0, t), t0)
            t1 = np.where(ext, np.minimum(t1, t), t1)
        ok &= t0 < t1
        zlow = np.minimum(P[idx, 2] + t0 * D[idx, 2], P[idx, 2] + t1 * D[idx, 2])
        blk[idx[ok & (zlow < ztop)]] = True
    return blk


def ray_blocked(np, P, E, own, geo, T, houses=None):
    """For each ray from a sample P to an eye E: blocked by another wall line (its top as a slab, under its coping's
    top at three points across it) or by the ground (marched every 0.5 m from 0.3 m off the face to 0.3 m short of
    the eye, blocked 20 mm under the ground); with `houses`, by the houses too (the sensitivity's)."""
    D = E - P
    dist = np.linalg.norm(D, axis=1)
    blk = np.zeros(len(P), bool) if houses is None else houses_block(np, P, E, houses)
    for li, g in enumerate(geo):
        relP, relE = P[:, :2] - g["a"][:2], E[:, :2] - g["a"][:2]
        tP, tE = g["sd"] * (relP @ g["right"]), g["sd"] * (relE @ g["right"])
        t0, t1 = g["hw"] + WALL_TOP[0], g["hw"] + WALL_TOP[1]
        cand = (own != li) & ~((tP < t0) & (tE < t0)) & ~((tP > t1) & (tE > t1)) & ~blk
        idx = np.nonzero(cand)[0]
        if not len(idx):
            continue
        sP, sE = relP[idx] @ g["up"], relE[idx] @ g["up"]
        dt = tE[idx] - tP[idx]
        par = np.abs(dt) < 1e-9
        dts = np.where(par, 1.0, dt)
        l0, l1 = (t0 - tP[idx]) / dts, (t1 - tP[idx]) / dts
        la = np.where(par, 0.0, np.clip(np.minimum(l0, l1), 0, 1))
        lb = np.where(par, 1.0, np.clip(np.maximum(l0, l1), 0, 1))
        hit = np.zeros(len(idx), bool)
        for lam in (la, (la + lb) / 2, lb):
            s = sP + lam * (sE - sP)
            z = P[idx, 2] + lam * (E[idx, 2] - P[idx, 2])
            k = np.searchsorted(g["cs"], s, side="right") - 1
            inside = (s >= g["s0"]) & (s <= g["s1"]) & (k >= 0)
            hit |= inside & (z < g["ct"][np.clip(k, 0, len(g["ct"]) - 1)])
        blk[idx[hit]] = True
    idx = np.nonzero(~blk)[0]
    d = 0.3
    while len(idx):
        idx = idx[d < dist[idx] - 0.3]
        if not len(idx):
            break
        Q = P[idx] + (d / dist[idx])[:, None] * D[idx]
        hit = Q[:, 2] < T(Q[:, 0], Q[:, 1]) - 0.02
        blk[idx[hit]] = True
        idx = idx[~hit]
        d += 0.5
    return blk


def candidate_pairs(np, SM, E, eye_ok, rmin, rmax, view_frusta=None, samples=None):
    """(sample, eye, distance) for every eye the face looks towards (in front of its battered plane), between rmin
    and rmax, and for a judging view within its frame."""
    out_s, out_e, out_d = [], [], []
    S_idx = np.arange(len(SM["P"])) if samples is None else samples
    E_idx = np.nonzero(eye_ok)[0]
    if not len(E_idx) or not len(S_idx):
        return np.zeros(0, int), np.zeros(0, int), np.zeros(0)
    Ee = E[E_idx]
    for c0 in range(0, len(S_idx), 300):
        si = S_idx[c0:c0 + 300]
        d = Ee[None, :, :] - SM["P"][si][:, None, :]
        dist = np.linalg.norm(d, axis=2)
        ok = (np.einsum("ijk,ik->ij", d, SM["N"][si]) > 0) & (dist > rmin) & (dist <= rmax)
        if view_frusta is not None:
            for k_, (e_i, fwd, rgt, upv, tv, th) in view_frusta.items():
                col = np.nonzero(E_idx == e_i)[0]
                if not len(col):
                    continue
                c = col[0]
                rel = -d[:, c, :]          # the sample from the eye
                zc = rel @ fwd
                ok[:, c] &= (zc > 0.1) & (np.abs(rel @ upv) <= zc * tv) & (np.abs(rel @ rgt) <= zc * th)
        a_, b_ = np.nonzero(ok)
        out_s.append(si[a_])
        out_e.append(E_idx[b_])
        out_d.append(dist[a_, b_])
    return np.concatenate(out_s), np.concatenate(out_e), np.concatenate(out_d)


def sweep(np, si, ei, key, SM, E, geo, T, nS, batch=120000, houses=None):
    """Each sample's rays in its own order (key ascending), the r-th ray of every sample together; a sample stops at
    its first clear ray. Returns per sample the eye of that ray (-1 for none) and the rays tested."""
    first_eye = np.full(nS, -1)
    if not len(si):
        return first_eye, 0
    order = np.lexsort((key, si))
    s_o, e_o = si[order], ei[order]
    starts = np.r_[0, np.nonzero(np.diff(s_o))[0] + 1]
    rank = np.arange(len(s_o)) - np.repeat(starts, np.diff(np.r_[starts, len(s_o)]))
    o2 = np.lexsort((s_o, rank))
    s_o, e_o = s_o[o2], e_o[o2]
    tested = 0
    for p0 in range(0, len(s_o), batch):
        bs, be = s_o[p0:p0 + batch], e_o[p0:p0 + batch]
        live = first_eye[bs] < 0
        if not live.any():
            continue
        bs, be = bs[live], be[live]
        tested += len(bs)
        clear = ~ray_blocked(np, SM["P"][bs], E[be], SM["line"][bs], geo, T, houses)
        u, fi = np.unique(bs[clear], return_index=True)
        first_eye[u] = be[clear][fi]
    return first_eye, tested


def measure_visibility(facts):
    import numpy as np
    sys.path.insert(0, BLOCKOUTS)
    import masonry as M
    t_start = time.perf_counter()
    import centre_land as L
    import heart_layout as H
    t_import = time.perf_counter() - t_start
    f0 = without_visibility(facts)
    layout = M.lay(f0, data(), goings=2)
    geo = line_geometry(np, f0, layout)
    allxy = np.concatenate([np.array([g["a"][:2] + g["s0"] * g["up"], g["a"][:2] + g["s1"] * g["up"]])
                            for g in geo])
    bbox = (allxy[:, 0].min() - 3, allxy[:, 1].min() - 3, allxy[:, 0].max() + 3, allxy[:, 1].max() + 3)
    t0 = time.perf_counter()
    T = Terrain(np, H, L, f0, bbox, RANGE_WIDE)
    SM = wall_samples(np, layout, geo, T)
    nS = len(SM["P"])
    E, ekind, ename, in_houses = eye_points(np, H, L, T, bbox, RANGE_WIDE, yards=True)
    nv = len(VIEWS)
    E = np.concatenate([np.array([v[1] for v in VIEWS], float), E])
    ekind = ["view"] * nv + ekind
    ename = [v[0] for v in VIEWS] + ename
    is_view = np.array([k == "view" for k in ekind])
    is_yard = np.array([k == "yard" for k in ekind])
    frusta = {}
    for k, (name, e, c, vfov) in enumerate(VIEWS):
        e, c = np.array(e), np.array(c)
        fwd = (c - e) / np.linalg.norm(c - e)
        rgt = np.cross(fwd, [0, 0, 1.0])
        rgt /= np.linalg.norm(rgt)
        upv = np.cross(rgt, fwd)
        tv = math.tan(math.radians(vfov / 2))
        frusta[k] = (k, fwd, rgt, upv, tv, tv * ASPECT)
    live = ~SM["buried"]
    # A: the judging views, every ray
    a_s, a_e, a_d = candidate_pairs(np, SM, E, is_view, 0.0, 1e9, frusta, np.nonzero(live)[0])
    a_clear = ~ray_blocked(np, SM["P"][a_s], E[a_e], SM["line"][a_s], geo, T) if len(a_s) else np.zeros(0, bool)
    views_of = [set() for _ in range(nS)]
    view_near = np.zeros(nS, bool)
    for s_, e_, d_, c_ in zip(a_s.tolist(), a_e.tolist(), a_d.tolist(), a_clear.tolist()):
        if c_:
            views_of[s_].add(ename[e_])
            if d_ <= NEAR:
                view_near[s_] = True
    view_any = np.array([bool(v) for v in views_of])
    # B: the walkable ground, near rays first (yards last within each), then far, each sample to its first clear ray
    walk = ~is_view
    b_s, b_e, b_d = candidate_pairs(np, SM, E, walk, 0.0, RANGE, None, np.nonzero(live)[0])
    key = (b_d > NEAR) * 2000.0 + is_yard[b_e] * 1000.0 + b_d
    first_b, tested_b = sweep(np, b_s, b_e, key, SM, E, geo, T, nS)
    seen_b = first_b >= 0
    dist_b = np.full(nS, np.inf)
    dist_b[seen_b] = np.linalg.norm(E[first_b[seen_b]] - SM["P"][seen_b], axis=1)
    near_b = seen_b & (dist_b <= NEAR)
    # C: without the yards: a sample first seen from a yard near by was not seen from any other near eye; its far
    # rays from the lanes and places are tested now (one first seen from a yard far off was seen from nothing else)
    yard_first = seen_b & np.array([ekind[e_] == "yard" if e_ >= 0 else False for e_ in first_b.tolist()])
    c_samples = np.nonzero(yard_first & near_b)[0]
    c_s, c_e, c_d = candidate_pairs(np, SM, E, walk & ~is_yard, NEAR, RANGE, None, c_samples)
    first_c, tested_c = sweep(np, c_s, c_e, c_d, SM, E, geo, T, nS)
    # D: farther eyes, to RANGE_WIDE, for every sample seen from nothing within RANGE
    unseen = live & ~seen_b & ~view_any
    d_s, d_e, d_d = candidate_pairs(np, SM, E, walk, RANGE, RANGE_WIDE, None, np.nonzero(unseen)[0])
    first_d, tested_d = sweep(np, d_s, d_e, d_d, SM, E, geo, T, nS)
    # E: the houses as occluders too, boxes to their eaves (a sensitivity: the brief names the terrain and the walls)
    HB = house_boxes(np, H, bbox, RANGE)
    a_clear_h = a_clear.copy()
    if a_clear.any():
        a_clear_h[a_clear] = ~houses_block(np, SM["P"][a_s[a_clear]], E[a_e[a_clear]], HB)
    view_any_h, view_near_h = np.zeros(nS, bool), np.zeros(nS, bool)
    for s_, d_, c_ in zip(a_s.tolist(), a_d.tolist(), a_clear_h.tolist()):
        if c_:
            view_any_h[s_] = True
            view_near_h[s_] |= d_ <= NEAR
    first_h, tested_h = sweep(np, b_s, b_e, key, SM, E, geo, T, nS, houses=HB)
    seen_bh = first_h >= 0
    dist_h = np.full(nS, np.inf)
    dist_h[seen_bh] = np.linalg.norm(E[first_h[seen_bh]] - SM["P"][seen_bh], axis=1)
    seen_h = view_any_h | seen_bh
    near_h = view_near_h | (seen_bh & (dist_h <= NEAR))
    t_meas = time.perf_counter() - t0
    near = view_near | near_b
    seen = view_any | seen_b
    cls = np.where(SM["buried"], 3, np.where(near, 0, np.where(seen, 1, 2)))     # 0 near, 1 far only, 2 unseen, 3 buried
    cls_h = np.where(SM["buried"], 3, np.where(near_h, 0, np.where(seen_h, 1, 2)))
    # the far-only samples: how far their nearest clear eye on the walkable ground is, and where it stands
    fo = (cls == 1) & seen_b
    far_from = {}
    for s_ in np.nonzero(fo)[0].tolist():
        far_from[ename[first_b[s_]]] = far_from.get(ename[first_b[s_]], 0.0) + float(SM["area"][s_]) / 1e6
    far_only = dict(
        nearestEyeM=[round(float(x), 1) for x in np.percentile(dist_b[fo], [0, 25, 50, 75, 100])] if fo.any() else [],
        seenFrom={k: round(v, 2) for k, v in sorted(far_from.items(), key=lambda kv: -kv[1])[:8]},
        what="the walkable ground's nearest clear eye of each sample seen only from beyond 8 m (min, quartiles, max), "
             "and the m2 by the lane or place of that eye")
    # without the yards
    seen_ny = view_any | (seen_b & ~yard_first) | (first_c >= 0)
    near_ny = view_near | (near_b & ~yard_first)
    seen_wide = seen | (first_d >= 0)
    # by panel face
    panels = {}
    names = ("near", "farOnly", "unseen", "buried")
    for k, w in enumerate(layout["walls"]):
        for pi, pn in enumerate(w["panels"]):
            rec = {}
            for fi, f in enumerate(FACES):
                sel = (SM["line"] == k) & (SM["panel"] == pi) & (SM["face"] == fi)
                ar = {names[c]: round(float(SM["area"][sel & (cls == c)].sum()) / 1e6, 4) for c in range(4)}
                firsts = sorted(set(ekind[e_] for e_ in first_b[sel & seen_b].tolist()))
                rec[f] = dict(laid=bool(seen[sel].any()), m2=ar, samples=int(sel.sum()),
                              views=sorted(set().union(*[views_of[i] for i in np.nonzero(sel)[0]])) if sel.any() else [],
                              seenFrom=firsts, laidWithoutYards=bool(seen_ny[sel].any()),
                              laidAt120m=bool(seen_wide[sel].any()),
                              nearWithoutYards=round(float(SM["area"][sel & near_ny & ~SM["buried"]].sum()) / 1e6, 4),
                              laidWithHouses=bool(seen_h[sel].any()),
                              m2WithHouses={names[c]: round(float(SM["area"][sel & (cls_h == c)].sum()) / 1e6, 4)
                                            for c in range(4)})
            panels[pn["id"]] = rec
    tot = {}
    for fi, f in enumerate(FACES):
        sel = SM["face"] == fi
        tot[f] = {names[c]: round(float(SM["area"][sel & (cls == c)].sum()) / 1e6, 2) for c in range(4)}
        tot[f]["laidM2"] = round(sum(sum(v[f]["m2"].values()) for v in panels.values() if v[f]["laid"]), 2)
        tot[f]["hiddenM2"] = round(sum(sum(v[f]["m2"].values()) for v in panels.values() if not v[f]["laid"]), 2)
        tot[f]["facesLaid"] = sum(1 for v in panels.values() if v[f]["laid"])
        tot[f]["faces"] = len(panels)
    sens = dict(
        withoutYards=dict(facesChanged=sorted(f"{p} {f}" for p, v in panels.items() for f in FACES
                                              if v[f]["laid"] != v[f]["laidWithoutYards"])),
        at120m=dict(facesChanged=sorted(f"{p} {f}" for p, v in panels.items() for f in FACES
                                        if v[f]["laid"] != v[f]["laidAt120m"])),
        withHouses=dict(
            what="the houses of the clay as occluders too, each a box over its footprint to its eaves (no roof)",
            houses=len(HB),
            facesChanged=sorted(f"{p} {f}" for p, v in panels.items() for f in FACES
                                if v[f]["laid"] != v[f]["laidWithHouses"]),
            m2={f: {names[c]: round(float(SM["area"][(SM["face"] == fi) & (cls_h == c)].sum()) / 1e6, 2)
                    for c in range(4)} for fi, f in enumerate(FACES)}))
    eyes = {k: sum(1 for x in ekind if x == k) for k in ("view", "lane", "place", "yard")}
    within = np.array([True] * nv + [bool(np.min(np.linalg.norm(SM["P"][::50, :2] - e[:2], axis=1)) <= RANGE)
                                     for e in E[nv:]])
    vis = dict(
        what="which panel faces are seen (tools/r1_elevations.py visibility): a face seen from any judging view or "
             "walkable point is laid stone by stone; a face seen from nowhere is hidden work, its fill not laid",
        method=dict(
            ground="the clay's carved ground on its 1.5 m grid (heart_layout.carve over centre_land.heights, as "
                   "wall.py's ground_near), bilinear; inside each flight's clear width the steps' treads",
            faces=f"a sample every {SAMPLE} mm along each course at its mid-height, on the face battered 1 in 6 "
                  "(wall.py), 20 mm off it; a sample is buried where the ground 0.1 m outside the face stands over it",
            eyes=f"the six judging views (LT1Stone.cs, in frame at 2560 x 1440) and standing eyes {EYE} m over the "
                 "walkable ground: every lane, stair and quay of heart_layout.LANES every 1.75 m along and about "
                 "1.5 m across (0.3 m in from the edges), the Landing, the small places, the market square and the "
                 "yards on a 1.5 m grid, none inside a house",
            rays="from the sample to the eye, if the eye is in front of the face; blocked by another wall line (its "
                 f"top as a slab {WALL_TOP[0]} to {WALL_TOP[1]} m outside the stair's clear half-width, under its "
                 "coping's top) or by the ground (marched every 0.5 m, 20 mm under it); houses do not block "
                 "(sensitivity.withHouses adds them)",
            classes=f"near: seen from an eye within {NEAR:g} m (L0's range); farOnly: seen only from farther, up to "
                    f"{RANGE:g} m; unseen: from nowhere within {RANGE:g} m; buried: under the ground",
            measuredOn="the two-going layout's courses and copings, before any fill"),
        eyeHeightMm=int(EYE * 1000), rangeM=RANGE, nearMm=int(NEAR * 1000), sampleMm=SAMPLE,
        eyes=dict(eyes, withinRange=int(within.sum()), droppedInHouses=in_houses), samples=int(nS),
        rays=dict(views=int(len(a_s)), walkable=int(tested_b), withoutYards=int(tested_c), wide=int(tested_d),
                  withHouses=int(tested_h)),
        panels=panels, totals=tot, sensitivity=sens, farOnly=far_only)
    timing = dict(importS=round(t_import, 1), measureS=round(t_meas, 1))
    return vis, dict(SM=SM, cls=cls, E=E, ekind=ekind, geo=geo, layout=layout, views_of=views_of), timing


def visibility_main():
    import numpy as np
    facts = json.load(open(FACTS))
    vis, raw, tm = measure_visibility(facts)
    facts["walls"]["visibility"] = vis
    with open(FACTS, "w") as fh:
        json.dump(facts, fh, indent=1, sort_keys=True)
    draw_visibility(np, vis, raw, os.path.join(OUT, "visibility.png"))
    with open(os.path.join(tempfile.gettempdir(), "r1-visibility-timing.json"), "w") as fh:
        json.dump(tm, fh)
    print("visibility written to", FACTS, "timing", tm)
    for f in FACES:
        print(f, vis["totals"][f])
    print("eyes", vis["eyes"], "rays", vis["rays"])
    print("sensitivity", vis["sensitivity"])


# ---------------------------------------------------------------------------------------------------------------
# Shapes (the checks may use floats: they decide nothing in the layout)

def area2(poly):
    """Twice the signed area of an outline, in mm^2 (integer)."""
    return sum(p[0] * q[1] - q[0] * p[1] for p, q in zip(poly, poly[1:] + poly[:1]))


def simplified(poly):
    """The outline less repeated points and points on a straight run (an edge counts once)."""
    pts = []
    for p in poly:
        if not pts or p != pts[-1]:
            pts.append(list(p))
    if len(pts) > 1 and pts[0] == pts[-1]:
        pts.pop()
    changed = True
    while changed and len(pts) > 3:
        changed = False
        for i in range(len(pts)):
            a, b, c = pts[i - 1], pts[i], pts[(i + 1) % len(pts)]
            if (b[0] - a[0]) * (c[1] - b[1]) - (b[1] - a[1]) * (c[0] - b[0]) == 0:
                pts.pop(i)
                changed = True
                break
    return pts


def convex(pts):
    sg = 0
    for i in range(len(pts)):
        a, b, c = pts[i - 1], pts[i], pts[(i + 1) % len(pts)]
        cr = (b[0] - a[0]) * (c[1] - b[1]) - (b[1] - a[1]) * (c[0] - b[0])
        if cr != 0:
            if sg and (cr > 0) != (sg > 0):
                return False
            sg = cr
    return True


def edge_lengths(pts):
    return [math.hypot(q[0] - p[0], q[1] - p[1]) for p, q in zip(pts, pts[1:] + pts[:1])]


def angles(pts):
    out = []
    for i in range(len(pts)):
        a, b, c = pts[i - 1], pts[i], pts[(i + 1) % len(pts)]
        u, v = (a[0] - b[0], a[1] - b[1]), (c[0] - b[0], c[1] - b[1])
        out.append(math.degrees(math.atan2(abs(u[0] * v[1] - u[1] * v[0]), u[0] * v[0] + u[1] * v[1])))
    return out


def span(poly, k):
    vs = [p[k] for p in poly]
    return min(vs), max(vs)


# ---------------------------------------------------------------------------------------------------------------
# The checks

class Tests:
    """Each test: what it checks, how many it checked, its failures (each with where and what), and marks for the
    sheet."""

    def __init__(self):
        self.t = {}
        self.marks = {}
        self.tally = {}

    def add(self, sn, name, rule):
        self.t.setdefault((sn, name), dict(sn=sn, name=name, rule=rule, checked=0, fails=[], notes=[]))
        if rule and not self.t[(sn, name)]["rule"]:
            self.t[(sn, name)]["rule"] = rule
        return self.t[(sn, name)]

    def check(self, sn, name, rule, ok, where, what, mark=None):
        t = self.add(sn, name, rule)
        t["checked"] += 1
        if not ok:
            t["fails"].append(dict(where=where, what=what))
            if mark:
                self.marks.setdefault(mark[0], []).append(mark[1:])
        return ok

    def note(self, sn, name, rule, text):
        self.add(sn, name, rule)["notes"].append(text)

    def failing(self):
        return {k: t for k, t in self.t.items() if t["fails"]}


def hidden_of(w):
    """The wall's hidden panel faces: (panel id, face) -> its s range."""
    rng = {pn["id"]: pn["s"] for pn in w["panels"]}
    return {(p, f): rng[p] for p, f in w["hidden"]}


def wall_tests(T, w, fl, M, D, clock=None):
    lid = w["id"]
    Lz = [l_["z"] for l_ in w["lines"]]
    Lk = [l_["kind"] for l_ in w["lines"]]
    nb = len(Lz) - 1
    Hc = [Lz[m + 1] - Lz[m] for m in range(nb)]
    tops = [fl["zFoot"]] + [st["zTop"] for st in fl["steps"]]
    G = w["goings"]
    s0, s1 = w["s"]
    course_kinds = ("face", "through", "head")
    hid = hidden_of(w)
    t_other = time.perf_counter()
    # ---- SN1, SN4, SN2's slivers, SN9's no rake: every stone's outline
    for st in w["stones"]:
        poly = st["outline"]
        pts = simplified(poly)
        mk = (lid, st["faces"][0], "stone", st["id"])
        T.check("SN1", "integer outlines", "every outline is integer mm",
                all(isinstance(v, int) for p in poly for v in p), st["id"], "a coordinate is not an integer")
        T.check("SN1", "convex", "every stone is a convex block (its face outline convex)", convex(pts), st["id"],
                f"not convex: {pts}", mk)
        T.check("SN4", "4 to 7 edges", "a face outline has four to seven straight edges", 4 <= len(pts) <= 7,
                st["id"], f"{len(pts)} edges: {pts}", mk)
        el, an = edge_lengths(pts), angles(pts)
        T.check("SN2", "no face under 50 mm", "no edge of a face shorter than 50 mm (no slivers)", min(el) >= M.SLIVER,
                st["id"], f"an edge of {min(el):.0f} mm", mk)
        T.check("SN2", "no angle under 25 degrees", "no corner more acute than 25 degrees", min(an) >= M.ACUTE,
                st["id"], f"a corner of {min(an):.1f} degrees", mk)
        T.check("SN9", "no rake", "no stone or coping cut to a slope: every edge of every wall stone level or plumb",
                all(p[0] == q[0] or p[1] == q[1] for p, q in zip(poly, poly[1:] + poly[:1])), st["id"],
                f"a sloping edge in {poly}", mk)
        z0, z1 = span(poly, 1)
        x0, x1 = span(poly, 0)
        if st["kind"] in course_kinds:
            T.check("SN2", "no stone under 50 mm high", "no stone under 50 mm high", z1 - z0 >= M.SLIVER, st["id"],
                    f"{z1 - z0} mm high", mk)
            zs = sorted(set(p[1] for p in poly))
            T.check("SN2", "level beds on course lines", "a course stone's bed and top are level, on course lines; a "
                    "coping's and a topstone's bed on a course line", all(z in Lz for z in zs), st["id"],
                    f"heights {zs} not all course lines", mk)
            T.check("SN10", "no stone over 4.5 x its height", "no stone longer than 4.5 times its height",
                    2 * (x1 - x0) <= 9 * (z1 - z0), st["id"], f"{x1 - x0} x {z1 - z0} mm ({(x1 - x0) / (z1 - z0):.2f})",
                    mk)
        elif st["kind"] in ("coping", "topstone"):
            T.check("SN2", "level beds on course lines", "", z0 in Lz, st["id"], f"its bed {z0} is not a course line",
                    mk)
    # ---- SN2: the courses
    for m in range(nb):
        T.check("SN2", f"course heights {D.COURSE[0]} to {D.COURSE[1]}", f"every course {D.COURSE[0]} to "
                f"{D.COURSE[1]} mm high (a rise up to {D.RISE_ONE} is one course)", D.COURSE[0] <= Hc[m] <= D.COURSE[1],
                f"{lid} course {m}", f"{Hc[m]} mm")
    for i, z in enumerate(tops):
        T.check("SN2", "a line on each step top", "one course line on each step top", z in Lz, f"{lid} step top {i}",
                f"{z} is not a course line")
    for i in range(len(tops) - 1):
        between = [z for z in Lz if tops[i] < z < tops[i + 1]]
        want = 0 if tops[i + 1] - tops[i] <= D.RISE_ONE else 1
        T.check("SN2", "one course a rise", f"one course on each step top and none between (a rise over {D.RISE_ONE} "
                "takes one line between)", len(between) == want, f"{lid} rise {i}",
                f"{len(between)} lines between {tops[i]} and {tops[i + 1]} ({tops[i + 1] - tops[i]} mm)")
    for a, b, z in w["footing"]["bank"]:
        T.check("SN2", "bank footing in whole courses", "on the bank side the footing steps with the ground, each step "
                "a whole course", z in Lz, f"{lid} bank footing {a} to {b}", f"{z} is not a course line")
    treads = [b - a for a, b, z in w["footing"]["bank"][1:-1]]
    if treads:
        T.note("SN2", "bank footing in whole courses", "", f"{lid}: {len(w['footing']['bank'])} footing steps, the "
               f"shortest inner tread {min(treads)} mm")
    ends = {}
    for f in FACES:
        for m in range(nb):
            for r in w["regions"][f][m]:
                for side in ("l", "r"):
                    ends[r[side]] = ends.get(r[side], 0) + 1
                    T.check("SN2", "every course ends at a feature", "each course ends at the wall's end, a step's end "
                            "or the ground's step, a topstone, or a stepped section's end (the riser)",
                            r[side] in ("riser", "riser-open", "feature", "end", "step", "ground"),
                            f"{lid} {f} course {m} at {r['a'] if side == 'l' else r['b']}", f"ends at {r[side]}")
    T.note("SN2", "every course ends at a feature", "", f"{lid}: course ends by kind {dict(sorted(ends.items()))}")
    # ---- SN9's overlap and contact, in the elevation: each face's courses tiled exactly, nothing in a step's end.
    # Every stone is a rectangle on course lines (no rake, level beds above), so a course on a face is intervals.
    cells = [(span(c["outline"], 0), span(c["outline"], 1), c["id"]) for c in w["cells"]]
    for f in FACES:
        hidden_x = [rng for (p, ff), rng in hid.items() if ff == f]
        foot = w["footing"][f]
        for m in range(nb):
            L, L2 = Lz[m], Lz[m + 1]
            ss = sorted((span(st["outline"], 0) + (st,) for st in w["stones"] if f in st["faces"] and m in st["bands"]),
                        key=lambda t_: (t_[0], t_[1], t_[2]["id"]))
            runs = [(r_["a"], r_["b"]) for r_ in w["regions"][f][m]]
            if not ss and not runs:
                continue
            where = f"{lid} {f} course {m}"
            over = [(p[2]["id"], q[2]["id"], p[1] - q[0]) for p, q in zip(ss, ss[1:]) if q[0] < p[1]]
            T.check("SN9", "the faces tiled: no overlap", "no two stones on a face share any of a course's length",
                    not over, where, "; ".join(f"{a_} and {b_} overlap {d_} mm" for a_, b_, d_ in over),
                    (lid, f, "lap", ss[0][0], ss[-1][1], L, L2) if over else None)
            for a, b in runs:
                gaps, x = [], a
                for x0, x1, _ in ss:
                    if x1 <= x:
                        continue
                    if x0 >= b:
                        break
                    if x0 > x:
                        gaps.append((x, x0))
                    x = max(x, x1)
                if x < b:
                    gaps.append((x, b))
                gaps = [g for g in gaps if not any(h0 <= g[0] and g[1] <= h1 for h0, h1 in hidden_x)]
                T.check("SN9", "the faces tiled: no gap", "every course's length on a face, over the footing and under "
                        "the coping, is filled by stones meeting end to end (a hidden panel face's fill apart)",
                        not gaps, f"{where} [{a}, {b}]", "open " + ", ".join(f"{g0} to {g1}" for g0, g1 in gaps),
                        (lid, f, "lap", gaps[0][0], gaps[-1][1], L, L2) if gaps else None)
            for x0, x1, st in ss:
                inside = [(max(x0, a), min(x1, b)) for a, b in runs if x0 < b and a < x1]
                if st["kind"] in ("coping", "topstone"):
                    ok, why = not inside, f"over the course's length at {inside}"
                else:
                    outside, x = [], x0
                    for a, b in sorted(inside):
                        if a > x:
                            outside.append((x, a))
                        x = max(x, b)
                    if x < x1:
                        outside.append((x, x1))
                    # outside the course's length a stone is only a two-faced one (a tie, a through) laid for the
                    # other face, under this face's footing: buried here, never in the coping's place
                    ok = all(len(st["faces"]) == 2 and all(z >= L2 for a, b, z in foot if a < o1 and o0 < b)
                             for o0, o1 in outside)
                    why = f"outside the course's length at {outside}, not under this face's footing"
                T.check("SN9", "the faces tiled: every stone in its place", "a course stone lies in the course's "
                        "length, or, if it is two-faced, under this face's footing; a coping or topstone lies over it",
                        ok, f"{where}: {st['id']}", why, (lid, f, "stone", st["id"]) if not ok else None)
    for st in w["stones"]:
        if "stair" not in st["faces"]:
            continue
        (x0, x1), (z0, z1) = span(st["outline"], 0), span(st["outline"], 1)
        hit = [c[2] for c in cells if x0 < c[0][1] and c[0][0] < x1 and z0 < c[1][1] and c[1][0] < z1]
        T.check("SN9", "nothing in a step's end", "no stone on the stair face stands in a step's end, where it tails "
                "into the wall (the occupied cells)", not hit, st["id"], f"in {', '.join(hit)}",
                (lid, "stair", "stone", st["id"]) if hit else None)
    # ---- SN2's parapet: level slab copings stepped square, a whole number of courses a step
    risers = w["risers"]
    runs = w["copingRuns"]
    P = w["pitch"]
    Pe = [[s0, P[0][1]]] + [p for p in P if s0 < p[0] < s1] + [[s1, P[-1][1]]]
    rising = [(p[0], q[0]) for p, q in zip(Pe, Pe[1:]) if q[1] > p[1]]
    level = [(p[0], q[0]) for p, q in zip(Pe, Pe[1:]) if q[1] == p[1]]
    rests = [(a, b) for a, b in level if a > s0 and b < s1]
    for r in risers:
        T.check("SN2", "copings on whole courses", "every coping lies on a course line and steps a whole number of "
                f"courses, one to {G} (the goings a level run spans)", 1 <= r["courses"] <= G and
                0 <= r["lo"] < r["hi"] < len(Lz), f"{lid} riser at {r['at']}", f"a step of {r['courses']} courses")
        if Lz[r["hi"]] <= tops[-1]:
            T.check("SN2", "a step falls only on a step top's line", "below the last step top, a coping steps from one "
                    "step top's course line to another's", Lk[r["lo"]] == "step" and Lk[r["hi"]] == "step",
                    f"{lid} riser at {r['at']}", f"from a {Lk[r['lo']]} line to a {Lk[r['hi']]} line")
        T.check("SN2", "risers only where the pitch rises", "a coping steps only where the stair rises, never over a "
                "rest", any(a <= r["at"] <= b for a, b in rising), f"{lid} riser at {r['at']}",
                f"outside the rising stretches {rising}")
    for a, b in rests:
        inside = [r["at"] for r in risers if a < r["at"] < b]
        T.check("SN2", "over a rest the coping runs level", "over a rest the coping runs level and drops square at "
                "the next flight", not inside, f"{lid} rest {a} to {b}", f"risers at {inside}")
    for st in w["stones"]:
        if st["kind"] == "coping":
            x0, x1 = span(st["outline"], 0)
            T.check("SN2", f"coping slabs {D.COPE_L[0]} to {D.COPE_L[1]} mm", f"a coping slab {D.COPE_L[0]} to "
                    f"{D.COPE_L[1]} mm long (wall.py)", D.COPE_L[0] <= x1 - x0 <= D.COPE_L[1], st["id"],
                    f"{x1 - x0} mm", (lid, "stair", "stone", st["id"]))
        if st["kind"] == "topstone":
            x0, x1 = span(st["outline"], 0)
            z0, z1 = span(st["outline"], 1)
            (qa, qb), (qc, qd) = D.SQUARE
            T.check("SN2", "square topstones", f"a head's topstone is square (length {qa}/{qb} to {qc}/{qd} its "
                    "height)", qb * (x1 - x0) >= qa * (z1 - z0) and qd * (x1 - x0) <= qc * (z1 - z0), st["id"],
                    f"{x1 - x0} x {z1 - z0} mm", (lid, "stair", "stone", st["id"]))
    # ---- SN9's open ends: every wall end a head under a square topstone; every coping run ends at one or a square step
    for e, s_end in ((0, s0), (1, s1)):
        hs = [st for st in w["stones"] if st["id"].startswith(f"{lid}/hd-{e}/")]
        top = next((st for st in hs if st["kind"] == "topstone"), None)
        T.check("SN9", "open ends", "every wall end is a head under a square topstone; every run of coping ends at a "
                "topstone or a square step onto the run below", top is not None and
                any(st["kind"] == "head" for st in hs) and s_end in span(top["outline"], 0), f"{lid}/hd-{e}",
                "no head and topstone at the wall's end")
    at_r = {r["at"] for r in risers}
    for i, c in enumerate(runs):
        a, b = c["s"]
        ok_l = (i == 0 and a == s0) or a in at_r
        ok_r = (i == len(runs) - 1 and b == s1) or b in at_r
        T.check("SN9", "open ends", "", ok_l and ok_r, f"{lid} coping run {a} to {b}", "an end at neither a topstone nor "
                "a step")
    for r in risers:
        x = r["at"]
        for f in FACES:
            if any(p_ == f and lo < x < hi for (pid, p_), (lo, hi) in hid.items()):
                continue
            missing = [m for m in range(r["lo"], r["hi"]) if
                       any(a <= x < b and z <= Lz[m] for a, b, z in w["footing"][f]) and
                       not any(run_["a"] == x for run_ in w["regions"][f][m])]
            T.check("SN9", "open ends", "", not missing, f"{lid} {f} riser at {x}",
                    f"courses {missing} do not stop square at the step")
    # ---- a stepped section's corner stone (Assumed: at least twice its height)
    by_course = {}
    for st in w["stones"]:
        if st["kind"] in course_kinds:
            for m in st["bands"]:
                for f in st["faces"]:
                    by_course.setdefault((f, m), []).append(st)
    for f in FACES:
        for m in range(nb):
            for r in w["regions"][f][m]:
                for side, x in (("l", r["a"]), ("r", r["b"])):
                    if r[side] not in ("riser", "riser-open"):
                        continue
                    if any(p_ == f and lo <= x <= hi for (pid, p_), (lo, hi) in hid.items()):
                        continue
                    st = next((s_ for s_ in by_course.get((f, m), []) if span(s_["outline"], 0)[0 if side == "l" else 1]
                               == x), None)
                    if st is None or st["kind"] != "face" or st.get("fallen"):
                        continue
                    L_ = span(st["outline"], 0)[1] - span(st["outline"], 0)[0]
                    need = min(max(D.STONE[0], D.RISER_FIRST * Hc[m]), D.longest(Hc[m]))
                    T.check("SN2", "a stepped section's corner stone at least 2 x its height", "(assumed) the stone a "
                            "stepped section starts or ends with at a riser is at least twice its course's height",
                            L_ >= need, st["id"], f"{L_} mm in a {Hc[m]} mm course (at least {need})",
                            (lid, f, "stone", st["id"]))
    # ---- SN2: the heads alternate
    for e in (0, 1):
        for f in FACES:
            hs = sorted([st for st in w["stones"] if st["kind"] == "head" and st["id"].startswith(f"{lid}/hd-{e}/")
                         and f in st["faces"]], key=lambda st: span(st["outline"], 1)[0])
            roles = [st["role"] for st in hs]
            T.check("SN2", "heads: ties and runners alternate", "a wall's end is a head, ties and runners "
                    "alternating up each face", all(a != b for a, b in zip(roles, roles[1:])), f"{lid}/hd-{e} {f}",
                    f"roles {roles}")
    # ---- hidden work
    for pn in w["panels"]:
        for f in FACES:
            n_face = sum(1 for st in w["stones"] if st["kind"] == "face" and st.get("panel") == pn["id"] and
                         st["faces"] == [f])
            if (pn["id"], f) in hid:
                T.check("SN8", "hidden faces are hidden work", "a panel face seen from nowhere has no face stones laid "
                        "(its heads and throughs are; its fill shows on the sheet veiled)", n_face == 0,
                        f"{pn['id']} {f}", f"{n_face} face stones laid")
            else:
                has_room = any(max(r["a"], pn["s"][0]) < min(r["b"], pn["s"][1]) for m in range(nb)
                               for r in w["regions"][f][m])
                T.check("SN8", "seen faces are laid", "a panel face seen from somewhere is laid stone by stone",
                        n_face > 0 or not has_room, f"{pn['id']} {f}", "no face stones")
    if clock is not None:
        clock["other tests"] = clock.get("other tests", 0.0) + time.perf_counter() - t_other
    t_bond = time.perf_counter()
    sn10(T, w, M, Lz, Hc, nb, hid)
    if clock is not None:
        clock["bond tests (SN10)"] = clock.get("bond tests (SN10)", 0.0) + time.perf_counter() - t_bond
    # ---- SN10: the largest courses low
    for m in range(nb):
        if Lz[m + 1] <= tops[0]:
            above = max(Hc[m + 1:])
            T.check("SN10", "the largest courses low", "the foundation courses no smaller than any course above them; "
                    "in a rise with a line between, the lower course the larger; over the last step each course no "
                    "larger than the one below, the first no larger than the last rise", Hc[m] >= above,
                    f"{lid} foundation course {m}", f"{Hc[m]} under a {above} mm course")
    for i in range(len(tops) - 1):
        mids = [z for z in Lz if tops[i] < z < tops[i + 1]]
        if mids:
            lower, upper = mids[0] - tops[i], tops[i + 1] - mids[0]
            T.check("SN10", "the largest courses low", "", lower >= upper, f"{lid} rise {i}", f"{lower} under {upper}")
    free = [Hc[m] for m in range(nb) if Lz[m] >= tops[-1]]
    last_rise = tops[-1] - max(z for z in Lz if z < tops[-1])
    if free:
        T.check("SN10", "the largest courses low", "", free[0] <= last_rise, f"{lid} free course 0",
                f"{free[0]} over the last rise's {last_rise}")
    for k in range(1, len(free)):
        T.check("SN10", "the largest courses low", "", free[k] <= free[k - 1], f"{lid} free course {k}",
                f"{free[k]} over {free[k - 1]}")


def sn10(T, w, M, Lz, Hc, nb, hid):
    """SN10's bond per face: laps, four-stone crosses, joints through more than two courses, the line of minimum
    trace; a coping's joints count over the course under it, kept lap_of(its thickness) from the joints there.
    Hidden panel faces are skipped."""
    lid = w["id"]
    edges = set(w["edges"])
    rx = {st["id"]: st["relaxed"] for st in w["stones"] if st.get("relaxed")}
    kind = {st["id"]: st["kind"] for st in w["stones"]}
    height = {st["id"]: span(st["outline"], 1)[1] - span(st["outline"], 1)[0] for st in w["stones"]}
    top_kinds = ("coping", "topstone")
    for f in FACES:
        hidden_rng = [rng for (p, f_), rng in hid.items() if f_ == f]

        def skip(x):
            return any(lo < x < hi for lo, hi in hidden_rng)
        occ = [[] for _ in range(nb)]
        for st in w["stones"]:
            if f not in st["faces"]:
                continue
            x0, x1 = span(st["outline"], 0)
            for m in st["bands"]:
                if m < nb:
                    occ[m].append((x0, x1, st["id"]))
        J = [[] for _ in range(nb)]
        pair = {}
        for m in range(nb):
            iv = sorted(occ[m])
            starts = {}
            for x0, x1, sid in iv:
                starts.setdefault(x0, []).append(sid)
            for x0, x1, sid in iv:
                for sid2 in starts.get(x1, []):
                    if sid2 != sid and not skip(x1):
                        J[m].append((x1, sid, sid2))
                        pair[(m, x1)] = {sid, sid2}
        link = {}
        for m in range(1, nb):
            for x, a, b in J[m]:
                if kind[a] in top_kinds and kind[b] in top_kinds:
                    lap = M.lap_of(min(height[a], height[b]))
                else:
                    lap = M.lap_of(Hc[m])
                for y, c, d in J[m - 1]:
                    if abs(x - y) >= lap:
                        continue
                    same = a in (c, d) or b in (c, d)
                    link.setdefault((m, x), set()).add((m - 1, y))
                    link.setdefault((m - 1, y), set()).add((m, x))
                    if same:
                        continue
                    if x == y and x in edges:
                        T.note("SN10", "laps", "", f"{lid} {f} course {m}: the rebuilt panel's edge, a straight "
                               f"joint at {x} (a fact, exempt)")
                        continue
                    why = sorted(set(f"{i_} {rx[i_]}" for i_ in (a, b, c, d) if rx.get(i_)))
                    T.check("SN10", "laps", "no vertical joint within 0.4 of the course height (at least 40 mm) of "
                            "one in the course below; a coping's, 0.4 of its thickness", False,
                            f"{lid} {f} course {m} at {x}", f"{abs(x - y)} mm from the joint below at {y} (lap {lap})" +
                            (f"; where the fill was relaxed: {'; '.join(why)}" if why else f"; {a}, {b} over {c}, {d}"),
                            (lid, f, "lap", x, y, Lz[m - 1], Lz[m + 1]))
                    if abs(x - y) <= 12 and len({a, b, c, d}) == 4:
                        T.check("SN10", "no four-stone cross", "no four stones meeting at a point", False,
                                f"{lid} {f} course {m} at {x}", f"{a}, {b} over {c}, {d}", (lid, f, "cross", x, Lz[m]))
            T.add("SN10", "laps", "")["checked"] += len(J[m])
            T.add("SN10", "no four-stone cross", "no four stones meeting at a point")["checked"] += len(J[m])
        seen = set()
        longest_chain = longest_edge = 0
        for node in sorted(link):
            if node in seen:
                continue
            comp, stack = set(), [node]
            while stack:
                q = stack.pop()
                if q in comp:
                    continue
                comp.add(q)
                stack += list(link.get(q, ()))
            seen |= comp
            courses = sorted(set(m for m, _ in comp))
            xs = set(x for _, x in comp)
            exempt = len(xs) == 1 and xs <= edges
            if len(courses) > 2 and not exempt:
                common = set.intersection(*[pair.get(n_, set()) for n_ in comp])
                tally = {}
                for n_ in comp:
                    for i_ in pair.get(n_, ()):
                        tally[i_] = tally.get(i_, 0) + 1
                top = max(sorted(tally), key=lambda i_: tally[i_]) if tally else None
                if common:
                    i_ = sorted(common)[0]
                    cause = f"the plumb side of {i_} ({kind[i_]}, {len(courses)} courses high)"
                    cat = "a tall stone's side"
                elif top and tally[top] >= 3:
                    cause = f"the side of {top} ({kind[top]}, {tally[top]} courses) with joints in line beyond it"
                    cat = "a tall stone's side"
                else:
                    cause = "joints of course stones in line"
                    cat = "course joints"
                T.check("SN10", "no joint through more than two courses", "no vertical joint through more than two "
                        "courses", False, f"{lid} {f} courses {courses[0]} to {courses[-1]} at {min(xs)}",
                        f"a joint through {len(courses)} courses: {cause}" +
                        (f"; relaxed: {'; '.join(sorted(set(rx[i_] for i_ in tally if rx.get(i_))))}"
                         if any(rx.get(i_) for i_ in tally) else ""),
                        (lid, f, "chain", min(xs), max(xs), Lz[courses[0]], Lz[courses[-1] + 1]))
                key_ = (cat, kind[top] if cat != "course joints" and top else "")
                T.tally[key_] = T.tally.get(key_, 0) + 1
            if exempt:
                longest_edge = max(longest_edge, len(courses))
            else:
                longest_chain = max(longest_chain, len(courses))
        T.add("SN10", "no joint through more than two courses", "no vertical joint through more than two courses")[
            "checked"] += sum(len(j) for j in J)
        T.note("SN10", "no joint through more than two courses", "", f"{lid} {f}: the longest run of joints within a "
               f"lap of each other spans {longest_chain} courses (a two-course head's side counts as two)" +
               (f"; the rebuilt panel's edge, a straight joint by the facts, runs {longest_edge}" if longest_edge else
                ""))
        for pn in w["panels"]:
            if (pn["id"], f) in hid:
                continue
            lo, hi = pn["s"]
            Jp = [sorted(x for x, _, _ in J[m] if lo <= x <= hi) for m in range(nb)]
            best = None
            m = 0
            while m < nb:
                if not Jp[m]:
                    m += 1
                    continue
                m0 = m
                while m < nb and Jp[m]:
                    m += 1
                top, bot = m - 1, m0
                if top - bot + 1 < 3:
                    continue
                cost = {x: Hc[top] for x in Jp[top]}
                for k in range(top - 1, bot - 1, -1):
                    cost = {y: Hc[k] + min(c + abs(x - y) for x, c in cost.items()) for y in Jp[k]}
                hgt = Lz[top + 1] - Lz[bot]
                ratio = min(cost.values()) / hgt
                if best is None or top - bot > best[1]:
                    best = (ratio, top - bot, hgt, bot, top)
            if best:
                T.note("SN10", "line of minimum trace", "reported per laid panel face", f"{pn['id']} {f}: "
                       f"{best[0]:.2f} times the height over courses {best[3]} to {best[4]} ({best[2]} mm; 1.00 is a "
                       "straight joint)")
            else:
                T.note("SN10", "line of minimum trace", "reported per laid panel face", f"{pn['id']} {f}: no stack of "
                       "three courses with joints")


def step_tests(T, so, fl, slab, width, D):
    """SN3 and SN5 on one flight's steps, by the stair's working and the wall kind's numbers (masonry.Rules)."""
    fid = so["id"]
    tail, gap = D.STEP_TAIL, D.FACE_GAP
    (la, lb), (ja, jb), jc = D.STEP_LAP, D.TREAD_JOINT, D.STEP_JOINT_CLEAR
    half, third = so["half"], so["third"]
    T.check("SN3", f"ends {tail} mm into the walls", f"both ends go {tail} mm into the walls",
            half - (width // 2 + gap) == tail, fid, f"tail {half - (width // 2 + gap)} mm")
    jw = so["jointWindow"]
    T.note("SN3", "joint outside the middle third", "", f"{fid}: a step's joint can start only in {jw['left']} or "
           f"{jw['right']} mm ({jw['widthMm']} mm of play a side): two stones of at most {slab['hi']} mm across "
           f"{2 * half} mm, the joint outside the middle third ({third} mm either side of the walking line)")
    by_step = {}
    for st in so["stones"]:
        by_step.setdefault(st["step"], []).append(st)
    below = None
    side_prev = None
    for k, sd in enumerate(so["steps"]):
        sts = by_step.get(sd["id"], [])
        for st in sts:
            x0, x1 = span(st["outline"], 0)
            y0, y1 = span(st["outline"], 1)
            T.check("SN3", "within the finish's sizes", f"each stone {slab['lo']} to {slab['hi']} mm across and at "
                    f"most {slab['hi']} deep", slab["lo"] <= x1 - x0 <= slab["hi"] and y1 - y0 <= slab["hi"], st["id"],
                    f"{x1 - x0} x {y1 - y0} mm", (fid, "stone", st["id"]))
        xs = sorted(span(st["outline"], 0) for st in sts)
        T.check("SN3", f"ends {tail} mm into the walls", "", xs[0][0] == -half and xs[-1][1] == half, sd["id"],
                f"ends {xs[0][0]}, {xs[-1][1]}")
        if not sd["rest"]:
            T.check("SN3", "one or two stones a step", "one or two stones a step, never three", 1 <= len(sts) <= 2,
                    sd["id"], f"{len(sts)} stones")
            whole = all(span(st["outline"], 1) == tuple(sd["y"]) for st in sts)
            T.check("SN3", "never pieced in depth", "each step stone runs its step's whole depth", whole, sd["id"],
                    "pieced in depth")
            x, xr = sd["joint"]
            T.check("SN3", "joint outside the middle third", f"the joint falls outside the walking line's middle "
                    f"third (|x| >= {third} mm)", xr <= -third or x >= third, sd["id"], f"joint {x} to {xr}",
                    (fid, "joint", sd["id"]))
            T.check("SN5", f"tread joints {ja} to {jb} mm", f"joints between tread stones are {ja} to {jb} mm",
                    ja <= xr - x <= jb, sd["id"], f"{xr - x} mm")
            if side_prev is not None:
                T.check("SN3", "joints alternate", "the joints alternate sides", sd["side"] != side_prev, sd["id"],
                        "same side as the step below")
            side_prev = sd["side"]
            if below is not None:
                T.check("SN3", f"no joint within {jc} mm of the one below", f"no joint within {jc} mm of the joint on the "
                        "step below", abs(x - below) >= jc, sd["id"], f"{abs(x - below)} mm", (fid, "joint", sd["id"]))
            below = x
        else:
            n = len(sts)
            T.check("SN3", "rests: two to four slabs", "a rest keeps the plan's form: two to four large slabs",
                    2 <= n <= 4, sd["id"], f"{n} slabs")
            if n > 2:
                T.note("SN3", "rests: two to four slabs", "", f"{sd['id']}: {sd['y'][1] - sd['y'][0] if 'y' in sd else '?'}"
                       f" mm deep, over the longest slab ({slab['hi']}): four slabs in two rows where the plan names two")
            for r in sd["rows"]:
                x, xr = r["joint"]
                if below is not None:
                    T.check("SN3", f"no joint within {jc} mm of the one below", "", abs(x - below) >= jc,
                            f"{sd['id']} row {r['y']}", f"{abs(x - below)} mm", (fid, "joint", sd["id"]))
                T.check("SN5", f"tread joints {ja} to {jb} mm", "", ja <= xr - x <= jb, f"{sd['id']} row {r['y']}",
                        f"{xr - x} mm")
                if -third < x and xr < third:
                    T.note("SN3", "joint outside the middle third", "", f"{sd['id']} row {r['y']}: a rest's joint at "
                           f"{x} lies inside the middle third (two slabs of at most {slab['hi']} across {2 * half} mm "
                           f"must meet within {slab['hi'] - half} mm of the centre; SN3 puts the rule on steps)")
                below = x
        if not sd.get("turn"):
            i = next(j for j, s_ in enumerate(fl["steps"]) if s_["id"] == sd["id"])
            if i < len(fl["steps"]) - 1:
                T.check("SN3", f"laps {la} to {lb} mm", f"each step's front bears on the back of the one below, lapping {la} "
                        f"to {lb} mm", la <= sd["lap"] <= lb and sd["y"][1] == fl["steps"][i + 1]["S"] + sd["lap"]
                        if "y" in sd else la <= sd["lap"] <= lb, sd["id"], f"lap {sd['lap']}")
        else:
            T.check("SN3", f"laps {la} to {lb} mm", "", la <= sd["lap"] <= lb, sd["id"], f"lap {sd['lap']}")


# ---------------------------------------------------------------------------------------------------------------
# Counts (SN8) and the budget re-derived from the faces that are seen

def face_areas(w):
    """mm2 of each panel face: its courses' lengths over the footing and under the coping, and the copings' and
    topstones' faces over them (the whole face, bank and buried parts included)."""
    Lz = [l_["z"] for l_ in w["lines"]]
    out = {}
    for pn in w["panels"]:
        lo, hi = pn["s"]
        for f in FACES:
            a = 0
            for m, runs in enumerate(w["regions"][f]):
                for r in runs:
                    a += max(0, min(r["b"], hi) - max(r["a"], lo)) * (Lz[m + 1] - Lz[m])
            for c in w["ceiling"]:
                a += max(0, min(c["s"][1], hi) - max(c["s"][0], lo)) * (c["top"] - c["z"])
            out[(pn["id"], f)] = a
    return out


def counts(layout):
    out = dict(walls={}, steps={})
    tot = dict(wallStones=0, faceStones=0, faceStair=0, faceBank=0, copings=0, copingsUnder450=0, copingsUnder200=0,
               throughs=0, heads=0, topstones=0, fallen=0, l0Walls=0, l1Walls=0, panelFaces=0, panelFacesLaid=0,
               faceM2=0.0, seenM2=0.0, hiddenM2=0.0, seenStairM2=0.0, seenBankM2=0.0, hiddenBankM2=0.0,
               hiddenStairM2=0.0, risers=0, risersOne=0, copingRuns=0)
    for w in layout["walls"]:
        k = {}
        l0 = l1 = 0
        hid = set(tuple(x) for x in w["hidden"])
        for st in w["stones"]:
            kk = st["kind"] if st["kind"] != "head" else f"head {st['role']}"
            if st["kind"] == "face":
                kk = f"face ({st['faces'][0]})"
                tot["faceStair" if st["faces"][0] == "stair" else "faceBank"] += 1
            k[kk] = k.get(kk, 0) + 1
            l0 += TRI[st["kind"]][0]
            l1 += TRI[st["kind"]][1]
            if st["kind"] == "coping":
                ln = span(st["outline"], 0)[1] - span(st["outline"], 0)[0]
                tot["copingsUnder450"] += ln < 450
                tot["copingsUnder200"] += ln < 200
        fa = face_areas(w)
        laid = [key for key in fa if key not in hid]
        l0 += FILL_TRI[0] * len(laid)
        l1 += FILL_TRI[1] * len(laid)
        seen = sum(v for key, v in fa.items() if key not in hid) / 1e6
        hidden = sum(v for key, v in fa.items() if key in hid) / 1e6
        out["walls"][w["id"]] = dict(kinds=dict(sorted(k.items())), total=len(w["stones"]), l0=l0, l1=l1,
                                     faceM2=round((seen + hidden), 2), seenM2=round(seen, 2), hiddenM2=round(hidden, 2),
                                     panelFaces=len(fa), panelFacesLaid=len(laid))
        tot["wallStones"] += len(w["stones"])
        tot["faceStones"] += sum(1 for st in w["stones"] if st["kind"] == "face")
        for kk, name in (("coping", "copings"), ("through", "throughs"), ("head", "heads"), ("topstone", "topstones")):
            tot[name] += sum(1 for st in w["stones"] if st["kind"] == kk)
        tot["fallen"] += sum(1 for st in w["stones"] if st.get("fallen"))
        tot["l0Walls"] += l0
        tot["l1Walls"] += l1
        tot["panelFaces"] += len(fa)
        tot["panelFacesLaid"] += len(laid)
        tot["faceM2"] += seen + hidden
        tot["seenM2"] += seen
        tot["hiddenM2"] += hidden
        for f in FACES:
            sv = sum(v for key, v in fa.items() if key[1] == f and key not in hid) / 1e6
            hv = sum(v for key, v in fa.items() if key[1] == f and key in hid) / 1e6
            tot["seenStairM2" if f == "stair" else "seenBankM2"] += sv
            tot["hiddenStairM2" if f == "stair" else "hiddenBankM2"] += hv
        tot["risers"] += len(w["risers"])
        tot["risersOne"] += sum(1 for r in w["risers"] if r["courses"] == 1)
        tot["copingRuns"] += len(w["copingRuns"])
    ts = 0
    for so in layout["steps"]:
        kk = {}
        for st in so["stones"]:
            kk[st["kind"]] = kk.get(st["kind"], 0) + 1
        out["steps"][so["id"]] = dict(kinds=kk, total=len(so["stones"]))
        ts += len(so["stones"])
    for key in ("faceM2", "seenM2", "hiddenM2", "seenStairM2", "seenBankM2", "hiddenBankM2", "hiddenStairM2"):
        tot[key] = round(tot[key], 2)
    tot["stepStones"] = ts
    tot["l0Stairs"], tot["l1Stairs"] = ts * STEP_TRI[0], ts * STEP_TRI[1]
    tot["l0Gully"], tot["l1Gully"] = tot["l0Walls"] + tot["l0Stairs"], tot["l1Walls"] + tot["l1Stairs"]
    # SN8's own density, rounded to whole triangles a m2 of course face; the budget over the seen course face needs
    # the visibility, so the report derives it (write_report), and the counts hold no second budget to disagree with it
    tot["density"] = (round(SN8["walls"][0] / SN8["faceM2"]), round(SN8["walls"][1] / SN8["faceM2"]))
    out["totals"] = tot
    return out


def independence(layout, facts, M, goings, laid):
    """Re-lay one panel at a time with a record event's seed and count the stones that change outside it."""
    res = []
    seed = facts["worldSeed"]
    for ln, w in zip(facts["walls"]["lines"], layout["walls"]):
        fl = facts["stair"]["flights"][ln["flight"]]
        so = layout["steps"][ln["flight"]]
        base = {st["id"]: st["outline"] for st in w["stones"]}
        owner = {st["id"]: st.get("panel") for st in w["stones"]}
        for pn in w["panels"]:
            w2 = M.lay_line(ln, fl, so, seed, rules(M, facts, ln["id"]), {pn["id"]: "relaid"}, goings, laid)
            new = {st["id"]: st["outline"] for st in w2["stones"]}
            inside = sum(1 for i in set(base) | set(new) if base.get(i) != new.get(i) and
                         (owner.get(i) == pn["id"] or i.startswith(pn["id"] + "/")))
            outside = sorted(i for i in set(base) | set(new) if base.get(i) != new.get(i) and
                             not (owner.get(i) == pn["id"] or i.startswith(pn["id"] + "/")))
            res.append(dict(panel=pn["id"], changedInside=inside, changedOutside=len(outside), outside=outside[:6]))
    return res


# ---------------------------------------------------------------------------------------------------------------
# Timing: one process, the CPU, Python

def timing(facts, M, goings, C, runs=5):
    """The laying's time by part, the median of `runs` runs, and the bond tests' (SN10, in this tool); per m2 of laid
    face and per stone, for the gully and its largest panel."""
    parts, totals, pf = {}, [], {}
    layout = None
    for _ in range(runs):
        clock = {}
        t0 = time.perf_counter()
        layout = M.lay(facts, data(), goings=goings, clock=clock)
        totals.append(time.perf_counter() - t0)
        for k, v in clock.items():
            if k == "panel fill":
                for p, x in v.items():
                    pf.setdefault(p, []).append(x)
            else:
                parts.setdefault(k, []).append(v)
    tests = {}
    for _ in range(runs):
        T_ = Tests()
        ck = {}
        for w in layout["walls"]:
            fl = next(f for f in facts["stair"]["flights"] if f["id"] == w["flight"])
            wall_tests(T_, w, fl, M, rules(M, facts, w["id"]), ck)
        for k, v in ck.items():
            tests.setdefault(k, []).append(v)
    med = {k: statistics.median(v) * 1000 for k, v in parts.items()}
    total = statistics.median(totals) * 1000
    tmed = {k: statistics.median(v) * 1000 for k, v in tests.items()}
    # the largest panel by laid face area
    best = None
    for w in layout["walls"]:
        fa = face_areas(w)
        hid = set(tuple(x) for x in w["hidden"])
        for pn in w["panels"]:
            a = sum(v for (p, f), v in fa.items() if p == pn["id"] and (p, f) not in hid)
            if best is None or a > best[0]:
                best = (a, pn["id"], w["id"])
    area, pid, lid = best
    n_p = sum(1 for w in layout["walls"] for st in w["stones"] if st.get("panel") == pid)
    ln = next(l_ for l_ in facts["walls"]["lines"] if l_["id"] == lid)
    fl = facts["stair"]["flights"][ln["flight"]]
    so = layout["steps"][ln["flight"]]
    laid = M.laid_table(facts)
    relays = []
    for _ in range(runs):
        t0 = time.perf_counter()
        M.lay_line(ln, fl, so, facts["worldSeed"], rules(M, facts, lid), {pid: "relaid"}, goings, laid)
        relays.append(time.perf_counter() - t0)
    tot = C["totals"]
    n_st = tot["wallStones"]
    return dict(
        runs=runs, totalMs=round(total, 1), parts={k: round(v, 2) for k, v in sorted(med.items())},
        tests={k: round(v, 1) for k, v in sorted(tmed.items())},
        perM2=round(total / tot["seenM2"], 2), perStone=round(total / (n_st + tot["stepStones"]), 4),
        perM2Walls=round((total - med.get("steps", 0)) / tot["seenM2"], 2),
        perStoneWalls=round((total - med.get("steps", 0)) / n_st, 4),
        bondPerM2=round(tmed.get("bond tests (SN10)", 0) / tot["seenM2"], 2),
        bondPerStone=round(tmed.get("bond tests (SN10)", 0) / n_st, 4),
        largest=dict(panel=pid, m2=round(area / 1e6, 2), stones=n_p, fillMs=round(statistics.median(pf[pid]) * 1000, 2),
                     lineRelayMs=round(statistics.median(relays) * 1000, 1),
                     fillPerM2=round(statistics.median(pf[pid]) * 1000 / (area / 1e6), 2),
                     fillPerStone=round(statistics.median(pf[pid]) * 1000 / max(1, n_p), 4)),
        machine=machine())


def machine():
    try:
        cpu = subprocess.run(["sysctl", "-n", "machdep.cpu.brand_string"], capture_output=True, text=True).stdout.strip()
        model = subprocess.run(["sysctl", "-n", "hw.model"], capture_output=True, text=True).stdout.strip()
    except OSError:
        cpu, model = "?", "?"
    return f"{cpu} ({model}), Python {sys.version.split()[0]}, one process, one thread"


# ---------------------------------------------------------------------------------------------------------------
# The sheet: PNGs written by hand (zlib), drawn with numpy

FONT = {
    "0": (14, 17, 19, 21, 25, 17, 14), "1": (4, 12, 4, 4, 4, 4, 14), "2": (14, 17, 1, 2, 4, 8, 31),
    "3": (31, 2, 4, 2, 1, 17, 14), "4": (2, 6, 10, 18, 31, 2, 2), "5": (31, 16, 30, 1, 1, 17, 14),
    "6": (6, 8, 16, 30, 17, 17, 14), "7": (31, 1, 2, 4, 8, 8, 8), "8": (14, 17, 17, 14, 17, 17, 14),
    "9": (14, 17, 17, 15, 1, 2, 12), "A": (14, 17, 17, 17, 31, 17, 17), "B": (30, 17, 17, 30, 17, 17, 30),
    "C": (14, 17, 16, 16, 16, 17, 14), "D": (28, 18, 17, 17, 17, 18, 28), "E": (31, 16, 16, 30, 16, 16, 31),
    "F": (31, 16, 16, 30, 16, 16, 16), "G": (14, 17, 16, 23, 17, 17, 15), "H": (17, 17, 17, 31, 17, 17, 17),
    "I": (14, 4, 4, 4, 4, 4, 14), "J": (7, 2, 2, 2, 2, 18, 12), "K": (17, 18, 20, 24, 20, 18, 17),
    "L": (16, 16, 16, 16, 16, 16, 31), "M": (17, 27, 21, 21, 17, 17, 17), "N": (17, 17, 25, 21, 19, 17, 17),
    "O": (14, 17, 17, 17, 17, 17, 14), "P": (30, 17, 17, 30, 16, 16, 16), "Q": (14, 17, 17, 17, 21, 18, 13),
    "R": (30, 17, 17, 30, 20, 18, 17), "S": (15, 16, 16, 14, 1, 1, 30), "T": (31, 4, 4, 4, 4, 4, 4),
    "U": (17, 17, 17, 17, 17, 17, 14), "V": (17, 17, 17, 17, 17, 10, 4), "W": (17, 17, 17, 21, 21, 21, 10),
    "X": (17, 17, 10, 4, 10, 17, 17), "Y": (17, 17, 17, 10, 4, 4, 4), "Z": (31, 1, 2, 4, 8, 16, 31),
    " ": (0,) * 7, "-": (0, 0, 0, 31, 0, 0, 0), "/": (0, 1, 2, 4, 8, 16, 0), ".": (0, 0, 0, 0, 0, 12, 12),
    ":": (0, 12, 12, 0, 12, 12, 0), "(": (2, 4, 8, 8, 8, 4, 2), ")": (8, 4, 2, 2, 2, 4, 8),
    ",": (0, 0, 0, 0, 12, 4, 8), "=": (0, 0, 31, 0, 31, 0, 0), "+": (0, 4, 4, 31, 4, 4, 0),
    "%": (24, 25, 2, 4, 8, 19, 3), "<": (2, 4, 8, 16, 8, 4, 2), ">": (8, 4, 2, 1, 2, 4, 8),
}

COL = dict(
    bg=(255, 255, 255), ink=(40, 40, 40), outline=(70, 70, 70), face=(214, 210, 200), face1961=(184, 204, 228),
    through=(126, 186, 116), tie=(52, 128, 150), runner=(122, 182, 204), topstone=(226, 196, 58),
    coping=(150, 150, 160), fallen=(25, 25, 25), cell=(150, 108, 76), ground=(214, 232, 202),
    groundline=(70, 120, 60), pitch=(60, 90, 220), fail=(225, 20, 20), relaxed=(220, 0, 200), held=(20, 20, 20), fell=(235, 130, 20), notplaced=(130, 130, 130),
    rest=(222, 206, 176), step=(200, 200, 196), step2=(180, 180, 176), landing=(190, 214, 230), third=(225, 20, 20),
    wallface=(90, 90, 90), tail=(236, 226, 214), hidden=(236, 230, 222), hiddenwork=(250, 236, 200),
    near=(60, 160, 80), far=(240, 160, 40), unseen=(150, 150, 150), buried=(150, 108, 76),
    eyelane=(60, 90, 220), eyeplace=(150, 60, 200), eyeyard=(225, 20, 20), eyeview=(20, 20, 20),
    terrain=(244, 244, 238))


class Canvas:
    def __init__(self, w, h, np):
        self.np = np
        self.w, self.h = w, h
        self.img = np.full((h, w, 3), 255, dtype=np.uint8)

    def poly(self, pts, col):
        np = self.np
        xs, ys = [p[0] for p in pts], [p[1] for p in pts]
        x0, x1 = max(0, int(math.floor(min(xs)))), min(self.w - 1, int(math.ceil(max(xs))))
        y0, y1 = max(0, int(math.floor(min(ys)))), min(self.h - 1, int(math.ceil(max(ys))))
        if x1 < x0 or y1 < y0:
            return
        gx, gy = np.meshgrid(np.arange(x0, x1 + 1) + 0.5, np.arange(y0, y1 + 1) + 0.5)
        a = sum(p[0] * q[1] - q[0] * p[1] for p, q in zip(pts, pts[1:] + pts[:1]))
        sg = 1.0 if a > 0 else -1.0
        inside = np.ones(gx.shape, dtype=bool)
        for p, q in zip(pts, pts[1:] + pts[:1]):
            inside &= sg * ((q[0] - p[0]) * (gy - p[1]) - (q[1] - p[1]) * (gx - p[0])) >= 0
        sub = self.img[y0:y1 + 1, x0:x1 + 1]
        sub[inside] = col

    def rect(self, x0, y0, x1, y1, col):
        x0, x1 = sorted((int(round(x0)), int(round(x1))))
        y0, y1 = sorted((int(round(y0)), int(round(y1))))
        x0, y0 = max(0, x0), max(0, y0)
        x1, y1 = min(self.w, max(x1, x0 + 1)), min(self.h, max(y1, y0 + 1))
        if x1 > x0 and y1 > y0:
            self.img[y0:y1, x0:x1] = col

    def veil(self, x0, y0, x1, y1, col, k=3):
        np = self.np
        x0, x1 = sorted((max(0, int(round(x0))), min(self.w, int(round(x1)))))
        y0, y1 = sorted((max(0, int(round(y0))), min(self.h, int(round(y1)))))
        if x1 > x0 and y1 > y0:
            sub = self.img[y0:y1, x0:x1].astype("int32")
            self.img[y0:y1, x0:x1] = ((sub * (5 - k) + np.array(col) * k) // 5).astype("uint8")

    def line(self, x0, y0, x1, y1, col, width=1, dash=0):
        n = int(max(abs(x1 - x0), abs(y1 - y0))) + 1
        for i in range(n + 1):
            if dash and (i // dash) % 2:
                continue
            t = i / max(n, 1)
            x, y = int(round(x0 + (x1 - x0) * t)), int(round(y0 + (y1 - y0) * t))
            for dx in range(-(width // 2), width - width // 2):
                for dy in range(-(width // 2), width - width // 2):
                    if 0 <= x + dx < self.w and 0 <= y + dy < self.h:
                        self.img[y + dy, x + dx] = col

    def outline(self, pts, col, width=1):
        for p, q in zip(pts, pts[1:] + pts[:1]):
            self.line(p[0], p[1], q[0], q[1], col, width)

    def text(self, x, y, s, col, scale=2):
        for ch in s.upper():
            g = FONT.get(ch, FONT[" "])
            for r, bits in enumerate(g):
                for c in range(5):
                    if bits & (1 << (4 - c)):
                        y0, x0 = int(y + r * scale), int(x + c * scale)
                        self.img[max(0, y0):max(0, y0 + scale), max(0, x0):max(0, x0 + scale)] = col
            x += 6 * scale

    def png(self, path):
        import struct
        import zlib

        def chunk(t, d):
            return struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t + d) & 0xFFFFFFFF)
        raw = b"".join(b"\x00" + self.img[y].tobytes() for y in range(self.h))
        with open(path, "wb") as fh:
            fh.write(b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", self.w, self.h, 8, 2, 0, 0, 0)) +
                     chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b""))


def stone_colour(st, w):
    k = st["kind"]
    if st.get("fallen"):
        return COL["fallen"]
    if k == "face":
        pn = next(p for p in w["panels"] if p["id"] == st["panel"])
        base = COL["face1961"] if pn["work"] != "built" else COL["face"]
        v = (int(st["id"].encode().hex()[-6:], 16) % 21) - 10
        return tuple(max(0, min(255, c + v)) for c in base)
    if k == "head":
        return COL["tie"] if st["role"] == "tie" else COL["runner"]
    if k == "coping":
        v = (int(st["id"].encode().hex()[-6:], 16) % 21) - 10
        return tuple(max(0, min(255, c + v)) for c in COL["coping"])
    return COL[k]


LEGEND = [("face", "face stone"), ("face1961", "1961 panel"), ("through", "through"), ("tie", "head tie"),
          ("runner", "head runner"), ("topstone", "topstone"), ("coping", "coping"), ("fallen", "fallen (hole)"),
          ("cell", "step end (occupied)"), ("ground", "ground (bank)"), ("hidden", "under the stair (hidden)"),
          ("hiddenwork", "hidden work (unseen)"), ("pitch", "pitch line"),
          ("relaxed", "laid without full bond"), ("fail", "test failure"), ("fell", "ring: a fall, fell"),
          ("held", "ring: a fall, held"), ("notplaced", "ring: a fall, not placed")]


def draw_legend(cv, x, y, items=LEGEND):
    for i, (k, label) in enumerate(items):
        xx = x + (i % 4) * 330
        yy = y + (i // 4) * 26
        if label.startswith("ring: "):
            ring(cv, xx + 15, yy + 8, COL[k])
            label = label[6:]
        else:
            cv.poly([(xx, yy), (xx + 30, yy), (xx + 30, yy + 16), (xx, yy + 16)], COL[k])
            cv.outline([(xx, yy), (xx + 30, yy), (xx + 30, yy + 16), (xx, yy + 16)], COL["outline"])
        cv.text(xx + 38, yy + 1, label, COL["ink"])


def ring(cv, cx, cy, col):
    """A fall point's ring, 9 to 10 px across its radius."""
    for r in (9, 10):
        for t in range(0, 360, 6):
            xx, yy = int(cx + r * math.cos(math.radians(t))), int(cy + r * math.sin(math.radians(t)))
            if 0 <= xx < cv.w and 0 <= yy < cv.h:
                cv.img[yy, xx] = col


def draw_elevation(np, w, face, marks, falls, path, title="", scale=0.2, strip=6000):
    """One face of one wall line, unrolled: s left to right (the bank face as seen through the wall from the stair),
    z up, in strips of `strip` mm, at `scale` px a mm."""
    s0, s1 = w["s"]
    starts = list(range(s0, s1, strip))
    vis = [st for st in w["stones"] if face in st["faces"]]
    relaxed = {st["id"] for st in w["stones"] if st.get("relaxed")}
    hid = [(lo, hi) for (p, f), (lo, hi) in hidden_of(w).items() if f == face]
    blocks = []
    for a in starts:
        b = min(a + strip, s1)
        zs = [p[1] for st in vis for p in st["outline"] if a - 200 <= p[0] <= b + 200]
        zs += [c["top"] for c in w["ceiling"] if c["s"][0] <= b and c["s"][1] >= a]
        zs += [z for s, z in w["ground"] if a <= s <= b] if face == "bank" else []
        zs += [c["outline"][0][1] for c in w["cells"] if a <= c["outline"][0][0] <= b] if face == "stair" else []
        zs += [z for a_, b_, z in w["footing"][face] if a_ <= b and b_ >= a]
        zlo, zhi = min(zs) - 150, max(zs) + 120
        blocks.append((a, b, zlo, zhi))
    M_ = 40
    W_ = int(strip * scale) + 2 * M_ + 60
    hs = [int((zhi - zlo) * scale) + 70 for a, b, zlo, zhi in blocks]
    head = 252
    cv = Canvas(W_, head + sum(hs) + 20, np)
    cv.text(M_, 14, f"{w['id']}  {face} face  {'(seen through the wall from the stair)' if face == 'bank' else ''}"
            f"  {title}", COL["ink"], 3)
    cv.text(M_, 46, f"R1 round 2 elevation, integer mm, {scale} px a mm (60 mm = {int(60 * scale)} px), strips of "
            f"{strip} mm", COL["ink"])
    cv.text(M_, 68, f"s from the foot of the flight; copings stepped {w['goings']} going(s) a level run", COL["ink"])
    draw_legend(cv, M_, 96)
    y = head
    for (a, b, zlo, zhi), hgt in zip(blocks, hs):
        ox = M_ + 50

        def P(s, z):
            return (ox + (s - a) * scale, y + 40 + (zhi - z) * scale)
        cv.text(M_, y + 6, f"s {a} to {b}", COL["ink"])
        if face == "bank":
            g = [(s, z) for s, z in w["ground"] if a - 100 <= s <= b + 100]
            for (sa, za), (sb, zb) in zip(g, g[1:]):
                cv.poly([P(sa, za), P(sb, zb), P(sb, zlo), P(sa, zlo)], COL["ground"])
        for st in vis:
            xs = [p[0] for p in st["outline"]]
            if max(xs) < a - 50 or min(xs) > b + 50:
                continue
            cv.poly([P(p[0], p[1]) for p in st["outline"]], stone_colour(st, w))
        for st in vis:
            xs = [p[0] for p in st["outline"]]
            if max(xs) < a - 50 or min(xs) > b + 50:
                continue
            cv.outline([P(p[0], p[1]) for p in st["outline"]], COL["relaxed"] if st["id"] in relaxed else COL["outline"])
        # hidden work: a panel face seen from nowhere, its fill not laid (its heads and throughs are), veiled
        for lo, hi in hid:
            if hi >= a and lo <= b:
                ztop = max(c["top"] for c in w["ceiling"] if c["s"][0] < hi and c["s"][1] > lo)
                x0_, y0_ = P(max(lo, a - 50), ztop)
                x1_, y1_ = P(min(hi, b + 50), zlo)
                cv.veil(x0_, y0_, x1_, y1_, COL["hiddenwork"], 4)
                cv.text(x0_ + 8, y0_ + 8, "hidden work: seen from nowhere", COL["ink"])
        if face == "bank":
            g = [(s, z) for s, z in w["ground"] if a - 100 <= s <= b + 100]
            for (sa, za), (sb, zb) in zip(g, g[1:]):
                cv.line(*P(sa, za), *P(sb, zb), COL["groundline"], 2)
        else:
            # under the stair's surface the wall is hidden: what is laid there (the heads' feet) is shown veiled
            for fa, fb, fz in w["footing"]["stair"]:
                if fb >= a and fa <= b:
                    x0_, y0_ = P(max(fa, a - 50), fz)
                    x1_, y1_ = P(min(fb, b + 50), zlo)
                    cv.veil(x0_, y0_, x1_, y1_, COL["hidden"], 3)
            for c in w["cells"]:
                xs = [p[0] for p in c["outline"]]
                if max(xs) >= a and min(xs) <= b:
                    pts = [P(max(a - 50, min(b + 50, p[0])), p[1]) for p in c["outline"]]
                    cv.poly(pts, COL["cell"])
                    cv.outline(pts, COL["outline"])
        pl = w["pitch"]
        for (pa, za), (pb, zb) in zip(pl, pl[1:]):
            cv.line(*P(pa, za), *P(pb, zb), COL["pitch"], 1, dash=6)
        for pn in w["panels"]:
            for x in pn["s"]:
                if a <= x <= b:
                    xx, _ = P(x, zhi)
                    cv.line(xx, y + 34, xx, y + 40, COL["ink"], 2)
            mid = (pn["s"][0] + pn["s"][1]) // 2
            if a <= mid <= b:
                cv.text(P(mid, zhi)[0] - 24, y + 22, pn["id"].rsplit("/", 1)[1], COL["ink"])
        for mk in marks:
            if mk[0] == "stone":
                st = next((s_ for s_ in vis if s_["id"] == mk[1]), None)
                if st and min(p[0] for p in st["outline"]) <= b and max(p[0] for p in st["outline"]) >= a:
                    cv.outline([P(p[0], p[1]) for p in st["outline"]], COL["fail"], 3)
            elif mk[0] == "lap" and a <= mk[1] <= b:
                x0, x1 = min(mk[1], mk[2]) - 20, max(mk[1], mk[2]) + 20
                cv.outline([P(x0, mk[3]), P(x1, mk[3]), P(x1, mk[4]), P(x0, mk[4])], COL["fail"], 2)
            elif mk[0] == "cross" and a <= mk[1] <= b:
                cx, cy = P(mk[1], mk[2])
                cv.line(cx - 8, cy - 8, cx + 8, cy + 8, COL["fail"], 3)
                cv.line(cx - 8, cy + 8, cx + 8, cy - 8, COL["fail"], 3)
            elif mk[0] == "chain" and a <= mk[1] <= b:
                cv.line(*P(mk[1], mk[3]), *P(mk[1], mk[4]), COL["fail"], 4)
        if face == "stair":
            for fp in falls:
                if a <= fp["s"] <= b:
                    cx, cy = P(fp["s"], fp["z"])
                    col = COL["held"] if "held" in fp["result"] else (COL["notplaced"] if "not placed" in fp["result"]
                                                                      else COL["fell"])
                    ring(cv, cx, cy, col)
        yb = y + 40 + (zhi - zlo) * scale
        for s in range((a // 1000) * 1000, b + 1, 1000):
            if s < a:
                continue
            x, _ = P(s, zlo)
            cv.line(x, yb, x, yb + 10, COL["ink"], 2)
            cv.text(x + 4, yb + 2, str(s), COL["ink"])
        for z in range((zlo // 500 + 1) * 500, zhi, 500):
            _, yy = P(a, z)
            cv.line(ox - 12, yy, ox - 2, yy, COL["ink"], 2)
            cv.text(M_ - 30, yy - 7, str(z), COL["ink"])
        y += hgt
    cv.png(path)


def draw_steps(np, layout, facts, marks, path, scale=0.1):
    flights = layout["steps"]
    cols = []
    for so in flights:
        fl = next(f for f in facts["stair"]["flights"] if f["id"] == so["id"])
        ymax = max(p[1] for st in so["stones"] for p in st["outline"])
        cols.append((so, fl, ymax))
    colw = int((2 * 1756 + 800) * scale)
    M_ = 40
    head = 200
    H_ = head + int(max(y for _, _, y in cols) * scale) + 80
    cv = Canvas(max(1560, M_ * 2 + colw * len(cols) + 200), H_, np)
    cv.text(M_, 14, "R1 steps in plan  st-gully", COL["ink"], 3)
    cv.text(M_, 46, f"integer mm, {scale} px a mm; x across (right of uphill +), y up the flight;", COL["ink"])
    cv.text(M_, 66, "the walking line's middle third red (dashed), the walls' faces grey, joints black", COL["ink"])
    for i, (k, label) in enumerate([("step", "step stone"), ("rest", "rest slab"), ("landing", "turn landing"),
                                    ("tail", "tail inside the wall"), ("fail", "test failure")]):
        xx, yy = M_ + i * 300, 96
        cv.poly([(xx, yy), (xx + 30, yy), (xx + 30, yy + 16), (xx, yy + 16)], COL[k])
        cv.text(xx + 38, yy + 1, label, COL["ink"])
    for ci, (so, fl, ymax) in enumerate(cols):
        ox = M_ + 80 + ci * (colw + 60) + int(400 * scale)
        oy = head + int(ymax * scale)
        half = so["half"]
        face = fl["width"] // 2 + 6

        def P(x, y):
            return (ox + (x + half) * scale, oy - y * scale)
        cv.text(ox, head - 40, so["id"], COL["ink"], 2)
        for x0, x1 in ((-half, -face), (face, half)):
            cv.poly([P(x0, 0), P(x1, 0), P(x1, ymax), P(x0, ymax)], COL["tail"])
        stones = sorted(so["stones"], key=lambda st: span(st["outline"], 1)[0])
        for k, st in enumerate(stones):
            pts = [P(p[0], p[1]) for p in st["outline"]]
            col = COL["landing"] if st["kind"] == "landing" else COL["rest"] if st["kind"] == "rest" else (
                COL["step"] if (k // 2) % 2 == 0 else COL["step2"])
            cv.poly(pts, col)
            cv.outline(pts, COL["outline"])
        for x in (-face, face):
            cv.line(*P(x, 0), *P(x, ymax), COL["wallface"], 2)
        for x in (-so["third"], so["third"]):
            cv.line(*P(x, 0), *P(x, ymax), COL["third"], 1, dash=5)
        for sd in so["steps"]:
            if not sd["rest"]:
                x, xr = sd["joint"]
                cv.line(*P((x + xr) / 2, sd["y"][0]), *P((x + xr) / 2, sd["y"][1] - sd["lap"]), COL["ink"], 2)
        for mk in marks:
            if mk[0] == "stone":
                st = next((s_ for s_ in so["stones"] if s_["id"] == mk[1]), None)
                if st:
                    cv.outline([P(p[0], p[1]) for p in st["outline"]], COL["fail"], 3)
            elif mk[0] == "joint":
                sd = next((s_ for s_ in so["steps"] if s_["id"] == mk[1]), None)
                if sd and not sd["rest"]:
                    x, xr = sd["joint"]
                    cv.line(*P(x, sd["y"][0]), *P(x, sd["y"][1]), COL["fail"], 4)
        for i, st in enumerate(fl["steps"]):
            if i % 5 == 0 or st["D"] > fl["g"] + 1:
                cv.text(ox - int(400 * scale) - 70, P(0, st["S"])[1] - 14, f"{i}" + (" rest" if st["D"] > fl["g"] + 1
                                                                                    else ""), COL["ink"])
        for y in range(0, ymax + 1, 5000):
            cv.line(ox - 30, P(0, y)[1], ox - 14, P(0, y)[1], COL["ink"], 2)
            cv.text(ox - int(400 * scale) - 70, P(0, y)[1] + 2, f"y {y}", COL["groundline"])
    cv.png(path)


def draw_visibility(np, vis, raw, path):
    """Each wall line's two faces unrolled, every sample coloured by what sees it, each panel labelled laid or hidden
    with its areas; and a plan of the eyes."""
    SM, cls, E, ekind, geo, layout = raw["SM"], raw["cls"], raw["E"], raw["ekind"], raw["geo"], raw["layout"]
    sc = 0.035
    walls = layout["walls"]
    strips = []
    for li, w in enumerate(walls):
        for fi, f in enumerate(FACES):
            sel = (SM["line"] == li) & (SM["face"] == fi)
            zlo = float((SM["z"][sel] - SM["h"][sel] / 2).min()) - 200
            zhi = max(c["top"] for c in w["ceiling"]) + 200
            strips.append((li, fi, w, f, zlo, zhi, int((w["s"][1] - w["s"][0]) * sc), int((zhi - zlo) * sc)))
    M_ = 40
    plan_w = 700
    width = M_ * 2 + max(s[6] for s in strips) + 80 + plan_w
    head = 170
    height = max(head + sum(s[7] + 70 for s in strips) + 20, head + 1000)
    cv = Canvas(width, height, np)
    cv.text(M_, 14, "R1 round 2: which wall faces are seen", COL["ink"], 3)
    t = vis["totals"]
    cv.text(M_, 46, f"samples every {vis['sampleMm']} mm at each course's mid-height; eyes: the six judging views and "
            f"standing eyes {vis['eyeHeightMm'] / 1000:g} m over the walkable ground within {vis['rangeM']:g} m; the "
            "ground and the walls occlude, houses do not", COL["ink"])
    cv.text(M_, 66, f"stair faces: {t['stair']['facesLaid']} of {t['stair']['faces']} laid; bank faces: "
            f"{t['bank']['facesLaid']} of {t['bank']['faces']} laid; seen only beyond {vis['nearMm'] / 1000:g} m: "
            f"stair {t['stair']['farOnly']} m2, bank {t['bank']['farOnly']} m2", COL["ink"])
    draw_legend(cv, M_, 92, [("near", f"seen within {vis['nearMm'] / 1000:g} m"),
                             ("far", f"seen only beyond {vis['nearMm'] / 1000:g} m"), ("unseen", "seen from nowhere"),
                             ("buried", "under the ground"), ("eyelane", "eye on a lane or stair"),
                             ("eyeplace", "eye on a place"), ("eyeyard", "eye in a yard"),
                             ("eyeview", "judging view")])
    y = head
    ccol = [COL["near"], COL["far"], COL["unseen"], COL["buried"]]
    for li, fi, w, f, zlo, zhi, sw, shh in strips:
        ox = M_ + 40
        s0 = w["s"][0]
        cv.text(M_, y + 4, f"{w['id']} {f} face", COL["ink"])

        def P(s, z):
            return (ox + (s - s0) * sc, y + 30 + (zhi - z) * sc)
        sel = np.nonzero((SM["line"] == li) & (SM["face"] == fi))[0]
        for i in sel:
            x0, y0 = P(SM["s"][i] - SM["ds"][i] / 2, SM["z"][i] + SM["h"][i] / 2)
            x1, y1 = P(SM["s"][i] + SM["ds"][i] / 2, SM["z"][i] - SM["h"][i] / 2)
            cv.rect(x0, y0, x1, y1, ccol[int(cls[i])])
        for c in w["ceiling"]:
            cv.rect(*P(c["s"][0], c["top"]), *P(c["s"][1], c["z"]), COL["coping"])
        for pn in w["panels"]:
            xa, _ = P(pn["s"][0], zhi)
            cv.line(xa, y + 26, xa, y + 30 + shh, COL["ink"], 1)
            rec = vis["panels"][pn["id"]][f]
            mid, _ = P((pn["s"][0] + pn["s"][1]) / 2, zhi)
            lab = pn["id"].rsplit("/", 1)[1] + (" laid" if rec["laid"] else " hidden")
            cv.text(mid - len(lab) * 3, y + 32 + shh + 2, lab, COL["ink"] if rec["laid"] else COL["fail"], 1)
        y += shh + 70
    # the plan
    px0 = M_ * 2 + max(s[6] for s in strips) + 80
    xs_all, ys_all = E[:, 0], E[:, 1]
    cx, cy = 48.0, 50.0
    half = 90.0
    k = (plan_w - 20) / (2 * half)

    def Q(x, y_):
        return (px0 + (y_ - (cy - half)) * k, head + 20 + (x - (cx - half)) * k)    # +y right, +x down (the map's)
    cv.rect(*Q(cx - half, cy - half), *Q(cx + half, cy + half), COL["terrain"])
    cols = dict(lane=COL["eyelane"], place=COL["eyeplace"], yard=COL["eyeyard"], view=COL["eyeview"])
    for i in range(len(E)):
        if abs(E[i, 0] - cx) <= half and abs(E[i, 1] - cy) <= half:
            qx, qy = Q(E[i, 0], E[i, 1])
            r = 3 if ekind[i] == "view" else 1
            cv.rect(qx - r, qy - r, qx + r + 1, qy + r + 1, cols[ekind[i]])
    for g in geo:
        for f_off in (g["hw"], g["hw"] + 0.42):
            a = g["a"][:2] + g["s0"] * g["up"] + g["sd"] * f_off * g["right"]
            b = g["a"][:2] + g["s1"] * g["up"] + g["sd"] * f_off * g["right"]
            cv.line(*Q(*a), *Q(*b), COL["ink"], 2)
    cv.text(px0, head, f"plan: {2 * half:g} m square about the gully, +y right, +x down; north up is +y right", COL["ink"],
            1)
    cv.png(path)


# ---------------------------------------------------------------------------------------------------------------
# The run

def lay_hash(facts, goings):
    import hashes as HX
    import masonry as M
    return HX.hash_hex(M.lay(facts, data(), goings=goings))


def run_tests(layout, facts, M, g, dat=None):
    T = Tests()
    ids = [st["id"] for w in layout["walls"] for st in w["stones"]] + [st["id"] for so in layout["steps"]
                                                                        for st in so["stones"]]
    for i in ids:
        T.check("ids", "ids follow the grammar", "every id is a slot by schemas/naming.md", g.match("slot", i), i,
                "not a slot")
    T.check("ids", "ids are unique", "no two stones share an id", len(ids) == len(set(ids)), "all",
            f"{len(ids) - len(set(ids))} repeated")
    slab = facts["sources"]["stepStone"]
    for so, fl in zip(layout["steps"], facts["stair"]["flights"]):
        step_tests(T, so, fl, slab, fl["width"], rules(M, facts, dat=dat))
    for w in layout["walls"]:
        fl = next(f for f in facts["stair"]["flights"] if f["id"] == w["flight"])
        wall_tests(T, w, fl, M, rules(M, facts, w["id"], dat))
    return T


def main(argv):
    import numpy as np
    import hashes as HX
    import masonry as M
    from naming import Grammar
    facts = json.load(open(FACTS))
    if not facts["walls"].get("visibility"):
        sys.exit("facts.json has no visibility: run `r1_elevations.py visibility` first")
    g = Grammar.load()
    laid = M.laid_table(facts)
    res = {}
    for G in (2, 1):
        first = M.lay(facts, data(), goings=G)
        again = M.lay(facts, data(), goings=G)
        h1, h2 = HX.hash_hex(first), HX.hash_hex(again)
        r = subprocess.run([sys.executable, os.path.abspath(__file__), "hash", str(G)], cwd=ROOT, capture_output=True,
                           text=True)
        h3 = r.stdout.strip().split()[-1] if r.returncode == 0 and r.stdout.strip() else "FAILED " + r.stderr[-300:]
        T = run_tests(first, facts, M, g)
        C = counts(first)
        res[G] = dict(layout=first, hashes=(h1, h2, h3), T=T, C=C)
        print(f"goings {G}: hash {h1}, again {h2}, second process {h3}",
              "stable" if h1 == h2 == h3 else "UNSTABLE")
    L2 = res[2]
    ind = independence(L2["layout"], facts, M, 2, laid)
    ind1 = independence(res[1]["layout"], facts, M, 1, laid)
    tm = timing(facts, M, 2, L2["C"])
    tm1 = timing(facts, M, 1, res[1]["C"], runs=3)
    vt = None
    p_vt = os.path.join(tempfile.gettempdir(), "r1-visibility-timing.json")
    if os.path.exists(p_vt):
        vt = json.load(open(p_vt))
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "layout.json"), "w") as fh:
        json.dump(dict(primary=L2["layout"], oneGoing=res[1]["layout"]), fh, sort_keys=True, separators=(",", ":"))
    # the sheet
    sheet = []
    for G in (2, 1):
        T, layout = res[G]["T"], res[G]["layout"]
        for w in layout["walls"]:
            for f in (FACES if G == 2 else ("stair",)):
                mk = [m_[1:] for m_ in T.marks.get(w["id"], []) if m_[0] == f]
                name = f"{w['id'].split('/', 1)[1].replace('/', '-')}-{f}{'' if G == 2 else '-1going'}.png"
                draw_elevation(np, w, f, mk, w["report"]["falls"], os.path.join(OUT, name),
                               "" if G == 2 else "(the one-going variant)")
                sheet.append(name)
    smk = []
    for so in L2["layout"]["steps"]:
        smk += [m_ for m_ in L2["T"].marks.get(so["id"], [])]
    draw_steps(np, L2["layout"], facts, smk, os.path.join(OUT, "steps-plan.png"))
    sheet.append("steps-plan.png")
    sheet.append("visibility.png")
    var = variant(facts, M, g)
    for G, v in sorted(var[1].items()):
        if "T" in v:
            print(f"granite record, goings {G}: hash {v['hashes'][0]}, again {v['hashes'][1]}",
                  "stable" if v["hashes"][0] == v["hashes"][1] else "UNSTABLE", f"tests {len(v['T'].t)}, failing",
                  {k: len(t["fails"]) for k, t in v["T"].failing().items()})
        else:
            print(f"granite record, goings {G}: refused: {v['refused']}")
    write_report(facts, res, ind, ind1, tm, tm1, vt, sheet, var)
    for G in (2, 1):
        T = res[G]["T"]
        print(f"goings {G}: tests {len(T.t)}, failing {len(T.failing())}, failures "
              f"{sum(len(t['fails']) for t in T.t.values())}")
        for (sn, name), t in sorted(T.t.items()):
            print(f"  {sn:5s} {name:56s} checked {t['checked']:6d}  failed {len(t['fails']):5d}")
        c = res[G]["C"]["totals"]
        print("  counts", {k: c[k] for k in ("wallStones", "faceStones", "copings", "throughs", "heads", "topstones",
                                             "l0Walls", "l1Walls", "density", "seenM2", "hiddenM2", "faceM2")})
    print("independence", sum(1 for r in ind if r["changedOutside"] == 0), "of", len(ind),
          "one-going", sum(1 for r in ind1 if r["changedOutside"] == 0), "of", len(ind1))
    print("timing", tm)
    print("sheet", ", ".join(sheet))


# ---------------------------------------------------------------------------------------------------------------
# The report

def _n(x):
    return f"{x:,}" if isinstance(x, int) else f"{x:,.2f}"


def _m2(x):
    """An area for the prose: none when it rounds to nothing, else two decimals."""
    return "none" if round(x, 2) == 0 else f"{x:,.2f} m²"


def _pct(new, old):
    return f"{round(100 * (new - old) / old):+d}%"


def write_report(facts, res, ind, ind1, tm, tm1, vt, sheet, var):
    """report.md: In short, the coordinator's read answered, the brief's five points, then the tests, the counts and
    the timing, the visibility, the budget, the laying's own reports, the panels re-laid, data and code, the granite
    record, the sheet, what fails and why, and what was assumed. Every number is this run's."""
    import masonry as M
    L = []
    a = L.append
    T2, C2, lay2 = res[2]["T"], res[2]["C"], res[2]["layout"]
    T1, C1, lay1 = res[1]["T"], res[1]["C"], res[1]["layout"]
    t2, t1 = C2["totals"], C1["totals"]
    o = ROUND1
    D = rules(M, facts, facts["walls"]["lines"][0]["id"])
    flights = {f["id"]: f for f in facts["stair"]["flights"]}
    # ---- the visibility
    vis = facts["walls"]["visibility"]
    vtot = vis["totals"]

    def vsum(k):
        return round(vtot["stair"][k] + vtot["bank"][k], 2)
    near, far, unseen, buried = vsum("near"), vsum("farOnly"), vsum("unseen"), vsum("buried")
    seen_c = round(near + far, 2)
    regions_m2 = round(near + far + unseen + buried, 2)
    tops_m2 = round(t2["faceM2"] - regions_m2, 2)
    n_faces = vtot["stair"]["faces"] + vtot["bank"]["faces"]
    n_laid = vtot["stair"]["facesLaid"] + vtot["bank"]["facesLaid"]
    far_whole = sorted((p, f) for p, d in vis["panels"].items() for f, x in d.items()
                       if x["m2"]["near"] == 0 and x["m2"]["farOnly"] > 0)
    far_whole_m2 = round(sum(vis["panels"][p][f]["m2"]["farOnly"] for p, f in far_whole), 2)
    far_part = sorted((p, f) for p, d in vis["panels"].items() for f, x in d.items()
                      if x["m2"]["near"] > 0 and x["m2"]["farOnly"] > 0)
    in_views = sum(1 for d in vis["panels"].values() for x in d.values() if x["views"])
    # ---- the budgets
    # SN8's density rounded to whole triangles a m2 (786 and 321), the numbers the brief names and the report prints
    d0, d1 = t2["density"]
    A0, A1 = int(round(d0 * seen_c, -2)), int(round(d1 * seen_c, -2))
    B0 = int(round(d0 * (seen_c - far_whole_m2), -2))
    fw = set(far_whole)
    n_fw = sum(1 for w in lay2["walls"] for st in w["stones"] if st["kind"] == "face" and
               (st.get("panel"), st["faces"][0]) in fw)
    l0B = t2["l0Walls"] - n_fw * TRI["face"][0] - len(fw) * FILL_TRI[0]
    S0, S1 = t2["l0Stairs"], t2["l1Stairs"]
    G0, G1 = A0 + S0, A1 + S1
    # ---- the courses
    rises = []
    for fl in facts["stair"]["flights"]:
        tp = [fl["zFoot"]] + [s_["zTop"] for s_ in fl["steps"]]
        rises += [b - a_ for a_, b in zip(tp, tp[1:])]
    under, free, n_mid = [], [], 0
    for w in lay2["walls"]:
        fl = flights[w["flight"]]
        Lz = [l_["z"] for l_ in w["lines"]]
        n_mid += sum(1 for l_ in w["lines"] if l_["kind"] == "mid")
        for m, (z0, z1) in enumerate(zip(Lz, Lz[1:])):
            if not any(w["regions"][f][m] for f in FACES):
                continue
            (free if z0 >= fl["steps"][-1]["zTop"] else under).append(z1 - z0)
    med = lambda v: sorted(v)[len(v) // 2]  # noqa: E731
    rest_ids = {s_["id"] for so in lay2["steps"] for s_ in so["steps"] if s_["rest"]}
    goings = [b["S"] - a_["S"] for fl in facts["stair"]["flights"] for a_, b in zip(fl["steps"], fl["steps"][1:])
              if a_["id"] not in rest_ids and b["id"] not in rest_ids]
    # ---- the steps
    st_steps = [s_ for so in lay2["steps"] for s_ in so["steps"] if not s_["rest"]]
    st_rests = [s_ for so in lay2["steps"] for s_ in so["steps"] if s_["rest"]]
    by_step = {}
    for so in lay2["steps"]:
        for st in so["stones"]:
            by_step[st["step"]] = by_step.get(st["step"], 0) + 1
    n_step_stones = sum(by_step.get(s_["id"], 0) for s_ in st_steps)
    n_rest_slabs = sum(by_step.get(s_["id"], 0) for s_ in st_rests)
    slab = facts["sources"]["stepStone"]
    so0 = lay2["steps"][0]
    jw = so0["jointWindow"]
    deep = [(s_["id"], s_["y"][1] - s_["y"][0], by_step.get(s_["id"], 0)) for s_ in st_rests
            if "y" in s_ and by_step.get(s_["id"], 0) > 2]
    # ---- the tests
    f2, f1 = T2.failing(), T1.failing()
    n_fail2 = sum(len(t["fails"]) for t in f2.values())

    def tget(T, sn, name):
        return T.t.get((sn, name), dict(checked=0, fails=[], notes=[]))
    laps2, cross2 = tget(T2, "SN10", "laps"), tget(T2, "SN10", "no four-stone cross")
    chain2 = tget(T2, "SN10", "no joint through more than two courses")
    alone2 = sum(1 for r in ind if r["changedOutside"] == 0)
    alone1 = sum(1 for r in ind1 if r["changedOutside"] == 0)
    flags2 = [x for w in lay2["walls"] for x in w["report"]["flags"]]
    cuts2 = [x for w in lay2["walls"] for x in w["report"]["cuts"]]
    fills2 = [x for w in lay2["walls"] for x in w["report"]["fills"]]
    falls2 = [x for w in lay2["walls"] for x in w["report"]["falls"]]
    thr2 = [x for w in lay2["walls"] for x in w["report"]["throughs"]]
    copes = [span(st["outline"], 0)[1] - span(st["outline"], 0)[0] for w in lay2["walls"] for st in w["stones"]
             if st["kind"] == "coping"]
    wall_len = sum(w["s"][1] - w["s"][0] for w in lay2["walls"]) / 1000

    def drops(lay):
        """The coping's square steps: each drop between two coping runs, in mm and in courses."""
        mm_, nc_ = [], {}
        for w in lay["walls"]:
            Lz_ = [l_["z"] for l_ in w["lines"]]
            for p_, q_ in zip(w["ceiling"], w["ceiling"][1:]):
                if p_["kind"] == q_["kind"] == "coping" and p_["z"] != q_["z"]:
                    mm_.append(abs(q_["z"] - p_["z"]))
                    k_ = abs(Lz_.index(q_["z"]) - Lz_.index(p_["z"]))
                    nc_[k_] = nc_.get(k_, 0) + 1
        return sorted(mm_), dict(sorted(nc_.items()))
    dr2, dr1 = drops(lay2), drops(lay1)
    rec, VO = var
    V2 = VO.get(2, {})
    V1 = VO.get(1, {})
    vfail = V2["T"].failing() if "T" in V2 else {}

    def by_rule(fails, want=("SN1", "SN2", "SN9", "SN10")):
        """design.md 7b's rules: which pass and which fail, from the failing checks."""
        bad = {sn for sn, _ in fails}
        ok_, no_ = [r_ for r_ in want if r_ not in bad], [r_ for r_ in want if r_ in bad]
        return (", ".join(ok_[:-1]) + " and " + ok_[-1] if len(ok_) > 1 else "".join(ok_)) + \
            (" pass" if len(ok_) > 1 else " passes") if ok_ else "", no_

    a("# R1 round 2: the gully's walls and steps as elevations")
    a("")
    a("Port step 2b, rung R1, round 2 (`reviews/lt1/port/2b/design.md`, The ladder). The cheek walls and the steps are "
      "laid in integer millimetres by `blender/generators/masonry.py`, from `r1/facts.json` and the data "
      "(`kinds/wall.json`, `packs/stavanger-1989/walling.json`), then checked, timed and drawn by "
      "`tools/r1_elevations.py`. This report gives numbers and faults only. It judges no look, and no reviewer has "
      "passed anything in it.")
    a("")
    # ------------------------------------------------------------------------------------------------ In short
    a("## In short")
    a("")
    a(f"- **Counts against the budgets (SN8), two goings a level run (the variant laid):** {_n(t2['wallStones'])} wall "
      f"stones (round 1: {_n(o['wallStones'])}, {_pct(t2['wallStones'], o['wallStones'])}; the design's estimate "
      f"about {_n(SN8['wallStones'])}). Walls L0 {_n(t2['l0Walls'])} triangles: the old budget is "
      f"{_n(SN8['walls'][0])} and the re-derived one {_n(A0)}. Walls L1 {_n(t2['l1Walls'])}: old {_n(SN8['walls'][1])}, "
      f"re-derived {_n(A1)}. Steps L0 {_n(S0)} ({t2['stepStones']} stones at {STEP_TRI[0]}) against "
      f"{_n(SN8['stairs'][0])}. The gully L0 {_n(t2['l0Gully'])}: old {_n(SN8['gully'][0])}, re-derived {_n(G0)} "
      f"(round 1: {_n(o['l0Gully'])}).")
    rep2 = sorted(name for (sn, name), t in T2.t.items() if not t["checked"])
    rep1 = sorted(name for (sn, name), t in T1.t.items() if not t["checked"])
    a(f"- **Tests:** {len(T2.t) - len(rep2)} checks and {len(rep2)} report only ({', '.join(rep2) or 'none'}, as "
      f"the design asks). With two goings, {len(T2.t) - len(rep2) - len(f2)} checks pass and {len(f2)} fail. With one "
      f"going, {len(T1.t) - len(rep1) - len(f1)} pass and {len(f1)} fails: "
      + ("; ".join(f"{sn} {name}, {len(t['fails'])} of {t['checked']}" for (sn, name), t in sorted(f1.items()))
         or "none") + ". Laid twice in one run and once in a second process, the hashes are "
      + "; ".join(f"{'two goings' if G == 2 else 'one going'} `{res[G]['hashes'][0]}` "
                  + ("the same three times" if len(set(res[G]['hashes'])) == 1 else
                     "NOT the same: " + ", ".join(res[G]['hashes'])) for G in (2, 1)) + ".")
    a(f"- **Visibility:** all {n_faces} panel faces are seen from somewhere, so all are laid stone by stone and none is "
      f"hidden work. Of the course faces, {_n(near)} m² are seen from within 8 m, {_n(far)} m² only from beyond 8 m "
      f"(all bank faces, on fl-1), {_m2(unseen)} from nowhere, and {_n(buried)} m² lie under the ground. Adding "
      f"the houses as occluders changes "
      f"{len(vis['sensitivity'].get('withHouses', {}).get('facesChanged', [])) or 'no'} faces.")
    a(f"- **Round 1's faults:** laps {o['laps']} to {len(laps2['fails'])}, four-stone crosses {o['crosses']} to "
      f"{len(cross2['fails'])}, joints through more than two courses {o['chains']} to {len(chain2['fails'])}. "
      f"Panels that re-lay alone: {o['independent']} of {o['panels']} before, {alone2} of {len(ind)} now (one going: "
      f"{alone1} of {len(ind1)}).")
    a(f"- **Data, not code:** every number that depends on the stone, its working or its era now lives in data. A "
      f"mortared granite wall of the 1930s (`r1/granite-1930.json`) is laid by the same functions with no code edit. "
      + (f"It fails {len(vfail)} check{'' if len(vfail) == 1 else 's'}: "
         + "; ".join(f"{sn} {name}, {len(t['fails'])} of {t['checked']}" for (sn, name), t in sorted(vfail.items()))
         + f". {by_rule(vfail)[0]}." if vfail else "It passes every check.") if "T" in V2 else
      f"It was refused: {V2.get('refused')}.")
    a(f"- **Timing (Python, one process, the CPU):** the whole gully takes {tm['totalMs']:,.0f} ms to lay: "
      f"{tm['perM2Walls']} ms a m² of laid wall face and {tm['perStoneWalls']} ms a wall stone. The bond tests take "
      f"{tm['bondPerM2']} ms a m² more. The C# port will differ.")
    still = []
    if f2:
        still.append("with two goings: " + "; ".join(f"{sn} {name}" for sn, name in sorted(f2)))
    if f1:
        still.append("with one going: " + "; ".join(f"{sn} {name} ({len(t['fails'])})" for (sn, name), t in
                                                   sorted(f1.items())))
    if vfail:
        still.append("the granite record: " + "; ".join(f"{sn} {name} ({len(t['fails'])})" for (sn, name), t in
                                                        sorted(vfail.items())))
    still.append(f"the walls' L0 is over the old budget ({_n(t2['l0Walls'])} against {_n(SN8['walls'][0])}) and "
                 f"under the re-derived one by {_n(A0 - t2['l0Walls'])}; the steps' L0 is over theirs "
                 f"({_n(S0)} against {_n(SN8['stairs'][0])})")
    still.append(f"{len(flags2)} flags and {len(cuts2)} boundary cuts in the laying's own reports")
    a("- **What still fails:** " + "; ".join(still) + ". All of it is under What fails, and why.")
    a("")
    # ------------------------------------------------------------------------------------------------ the read
    a(READ)
    a("")
    a("**Answers.**")
    a("")
    a(f"- **One course a rise: done.** The course range is now {D.COURSE[0]} to {D.COURSE[1]} mm, and a rise up to "
      f"{D.RISE_ONE} mm is one course. The rises are {min(rises)} to {max(rises)} mm, so every rise is one course: one "
      f"line on each step top and none between ({n_mid} lines between in all four walls). The courses under the last "
      f"step are the rises themselves ({min(under)} to {max(under)} mm, median {med(under)}). The free courses over it "
      f"run from {max(free)} down to {min(free)} mm, and the foundation courses are {D.FOUND[0]} to {D.FOUND[1]} mm. "
      f"The count fell from {_n(o['wallStones'])} to {_n(t2['wallStones'])} wall stones, more than the read's "
      "\"roughly halves\", because the longer stones ride on the higher courses: a stone runs "
      f"{D.STONE[0]} to {D.STONE[1]} mm, drawn {D.DRAW[0][0]}/{D.DRAW[0][1]} to {D.DRAW[1][0]}/{D.DRAW[1][1]} of its "
      "height, within SN10's 4.5.")
    fo_ = vis.get("farOnly", {})
    a(f"- **The back faces: measured.** Both faces of every panel are seen from somewhere: the bank faces from the "
      f"lanes and places around the gully. {len(far_whole)} whole bank faces on fl-1 ({far_whole_m2} m²) are seen "
      "only from beyond 8 m" + (f": their nearest eyes are {fo_['nearestEyeM'][0]} to {fo_['nearestEyeM'][-1]} m "
                               "off, on " + ", ".join(k for k, _ in sorted(fo_["seenFrom"].items(),
                                                                         key=lambda kv: -kv[1]))
                               if fo_.get("nearestEyeM") else "") +
      ". So no face is hidden work, and the bank faces are laid stone by stone like the stair faces. The method and "
      "the numbers are under The visibility measurement.")
    a(f"- **The budget: re-derived from the seen faces.** At SN8's own density ({round(d0)} L0 and {round(d1)} L1 "
      f"triangles a m² of course face), the {seen_c} m² of seen course face give the walls {_n(A0)} at L0 and "
      f"{_n(A1)} at L1. The walls lay {_n(t2['l0Walls'])} and {_n(t2['l1Walls'])}, inside both. This is a proposal: "
      "design.md is not edited. The derivation and a second option are under The budget, re-derived.")
    a("")
    # ------------------------------------------------------------------------------------------------ the brief
    a("## The brief's five points")
    a("")
    a(f"1. **One course a rise: answered.** As above. The ranges and their reasons are in the walling table's notes "
      "(`packs/stavanger-1989/walling.json`). The town's own walls (`docs/references/stone/` 31 and 36) are thick "
      "split slabs in level beds with the biggest stones low, so a course covers a rise. The free courses diminish "
      f"upwards by up to {D.FREE_STEP} mm a course, from no more than the last rise down to {D.COURSE[0]}. The "
      f"foundation courses are larger than any rise, and each is at least the course over it (fixed this round, see "
      f"Assumed). SN2's \"a line on each step top\" checks {tget(T2, 'SN2', 'a line on each step top')['checked']} "
      f"step tops and \"one course a rise\" {tget(T2, 'SN2', 'one course a rise')['checked']} rises, with no failure. "
      f"SN10's \"the largest courses low\" checks {tget(T2, 'SN10', 'the largest courses low')['checked']} courses, "
      "with no failure.")
    a(f"2. **The back faces: answered.** I measured them from the six judging views and from standing eyes 1.6 m over "
      "all the walkable ground, by panel and face, with the terrain and the walls as occluders. All "
      f"{n_faces} faces are seen; {in_views} of them appear in at least one judging view. {_n(far)} m² of course "
      f"face is seen only from beyond 8 m. No face is veiled, because none is hidden.")
    a(f"3. **The budget: answered, as a proposal.** Walls: L0 {_n(A0)} and L1 {_n(A1)} (option A), or L0 {_n(B0)} if "
      f"the faces seen only from beyond 8 m are built at L1 alone (option B). Steps: L0 {_n(S0)} and L1 {_n(S1)}, "
      f"the table's {STEP_TRI[0]} and {STEP_TRI[1]} a stone times the {t2['stepStones']} stones the facts make. The "
      f"gully: L0 {_n(G0)} and L1 {_n(G1)}.")
    a(f"4. **Stepped tops by SN2: answered.** There are no kneelers, knees or raked stones: SN9's \"no rake\" checks "
      f"{_n(tget(T2, 'SN9', 'no rake')['checked'])} stones, none sloped. Every coping lies on whole courses, and below "
      f"the last step every coping steps from one step top's line to another's. Over each rest the coping runs level "
      f"({tget(T2, 'SN2', 'over a rest the coping runs level')['checked']} rest runs, each rest on both walls, no "
      f"riser on any) and drops square "
      "at the next flight. Every coping run ends at a head's topstone or at a square step "
      f"({tget(T2, 'SN9', 'open ends')['checked']} ends checked, none open). Both variants are laid. I pick **two "
      f"goings** a level run: a going is {min(goings)} to {max(goings)} mm here (median {med(goings)}), so a run "
      f"over one going leaves a slab of about 300 mm, under a whole slab's {D.COPE_L[0]} mm. With one going, "
      f"{len(tget(T1, 'SN2', f'coping slabs {D.COPE_L[0]} to {D.COPE_L[1]} mm')['fails'])} of "
      f"{tget(T1, 'SN2', f'coping slabs {D.COPE_L[0]} to {D.COPE_L[1]} mm')['checked']} slabs are short. With two "
      f"goings, all {len(copes)} slabs are {min(copes)} to {max(copes)} mm (median {med(copes)}). The coping then "
      f"steps {', '.join(f'{v} times by {k} course' + ('s' if k > 1 else '') for k, v in dr2[1].items())}, "
      f"{dr2[0][0]} to {dr2[0][-1]} mm (median {med(dr2[0])}); with one going it steps "
      f"{', '.join(f'{v} times by {k} course' + ('s' if k > 1 else '') for k, v in dr1[1].items())}, "
      f"{dr1[0][0]} to {dr1[0][-1]} mm. The design leaves the final choice to R2b's grey form, by how the stepped top "
      "reads; this is R1's evidence for it. The one-going variant's stair faces are on the sheet for comparison.")
    a(f"5. **Round 1's other faults: answered.** Laps: {o['laps']} failures to {len(laps2['fails'])}. Crosses: "
      f"{o['crosses']} to {len(cross2['fails'])}. Joints through more than two courses: {o['chains']} to "
      f"{len(chain2['fails'])} (round 1's {o['chains']} included {o['chainsTops']} at the topstones; now "
      f"{sum(1 for x in chain2['fails'] if 'topstone' in x['what'])}). Panels changing stones outside themselves: "
      f"{o['panels'] - o['independent']} of {o['panels']} to {len(ind) - alone2} of {len(ind)}. The steps' 9 mm play "
      f"and fl-1's rests are by the facts, and I propose no rule change for them, since nothing here is evidence "
      "against the rules. Each is under What fails, and why.")
    a("")
    # ------------------------------------------------------------------------------------------------ tests
    a("## Tests")
    a("")
    a("Each check counts what it looked at and lists what failed. The one-going variant is checked by the same "
      "tests. New this round, from the self-check: SN9's overlap and contact in the elevation (each face's courses "
      "tiled with no overlap and no gap, every stone in its course's length or, if two-faced, under the other "
      "face's footing, and nothing in a step's end), and the heads' alternation counted up each face.")
    a("")
    a("| Rule | Check | Two goings: checked | failed | One going: checked | failed |")
    a("| --- | --- | --- | --- | --- | --- |")
    for key in sorted(set(T2.t) | set(T1.t)):
        x2, x1 = T2.t.get(key), T1.t.get(key)
        def cell(x):
            if not x:
                return "- | -"
            return "reported | -" if not x["checked"] else f"{x['checked']} | {len(x['fails'])}"
        a(f"| {key[0]} | {key[1]} | {cell(x2)} | {cell(x1)} |")
    a("")
    a("Failures and notes, two goings unless marked:")
    a("")
    for (sn, name), t in sorted(T2.t.items()):
        t1_ = T1.t.get((sn, name), dict(fails=[]))
        if not t["fails"] and not t["notes"] and not t1_["fails"]:
            continue
        a(f"**{sn}, {name}.** {t['rule']}")
        a("")
        for x in t["fails"][:20]:
            a(f"- FAIL {x['where']}: {x['what']}")
        if len(t["fails"]) > 20:
            a(f"- ... and {len(t['fails']) - 20} more")
        if t1_["fails"]:
            a(f"- one going: {len(t1_['fails'])} failures, e.g. " +
              "; ".join(f"{x['where']} {x['what']}" for x in t1_["fails"][:4]))
        notes = t["notes"]
        if name == "laps":
            edges = {}
            for n_ in notes:
                key_ = n_.split(": ", 1)[0].rsplit(" course", 1)[0] + " at " + n_.rsplit("at ", 1)[1].split(" ")[0]
                edges[key_] = edges.get(key_, 0) + 1
            for k_, v in sorted(edges.items()):
                a(f"- {k_}: the rebuilt panel's edge, a straight joint by the facts (exempt), in {v} courses")
            notes = []
        if name == "line of minimum trace":
            vals = []
            for n_ in notes:
                try:
                    vals.append((float(n_.split(": ", 1)[1].split(" times")[0]), n_))
                except (IndexError, ValueError):
                    pass
            if vals:
                vs = sorted(v for v, _ in vals)
                a(f"- {len(vals)} laid panel faces with a stack of three or more jointed courses: the least trace is "
                  f"{vs[0]:.2f} times the height, the median {vs[len(vs) // 2]:.2f}, the most {vs[-1]:.2f} (1.00 is a "
                  "straight joint). The five lowest:")
                for _, n_ in sorted(vals)[:5]:
                    a(f"  - {n_}")
            notes = [n_ for n_ in notes if "no stack" in n_][:3]
        for n_ in notes[:16]:
            a(f"- {n_}")
        if len(notes) > 16:
            a(f"- ... and {len(notes) - 16} more notes")
        a("")
    # ------------------------------------------------------------------------------------------------ counts
    a("## Counts (SN8)")
    a("")
    a("| Wall line | Stones | By kind | Laid face m² | L0 | L1 |")
    a("| --- | --- | --- | --- | --- | --- |")
    for wid, c in C2["walls"].items():
        kinds = ", ".join(f"{k} {v}" for k, v in c["kinds"].items())
        a(f"| {wid} | {c['total']} | {kinds} | {c['seenM2']} | {_n(c['l0'])} | {_n(c['l1'])} |")
    for sid, c in C2["steps"].items():
        a(f"| {sid} (steps) | {c['total']} | {', '.join(f'{k} {v}' for k, v in c['kinds'].items())} | | "
          f"{_n(c['total'] * STEP_TRI[0])} | {_n(c['total'] * STEP_TRI[1])} |")
    a("")
    a("| | Round 1 | Two goings | One going | Design (SN8) |")
    a("| --- | --- | --- | --- | --- |")
    rows = [("wall stones", o["wallStones"], t2["wallStones"], t1["wallStones"], f"about {SN8['wallStones']:,}"),
            ("face stones", o["faceStones"], t2["faceStones"], t1["faceStones"], ""),
            ("copings", o["copings"], t2["copings"], t1["copings"], f"about {SN8['copings']}"),
            ("kneelers and knees", o["kneelers"] + o["knees"], 0, 0, ""),
            ("throughs", o["throughs"], t2["throughs"], t1["throughs"], ""),
            ("head stones", o["heads"], t2["heads"], t1["heads"], ""),
            ("topstones", o["topstones"], t2["topstones"], t1["topstones"], ""),
            ("laid face m² (courses, copings and topstones)", o["faceM2"], t2["faceM2"], t1["faceM2"],
             f"about {SN8['faceM2']}"),
            ("step stones and slabs", o["stepStones"], t2["stepStones"], t1["stepStones"],
             f"about {SN8['steps']} steps of {SN8['stonesAStep']}"),
            ("walls L0", o["l0Walls"], t2["l0Walls"], t1["l0Walls"], f"{SN8['walls'][0]:,}"),
            ("walls L1", "", t2["l1Walls"], t1["l1Walls"], f"{SN8['walls'][1]:,}"),
            ("stairs L0", o["l0Stairs"], t2["l0Stairs"], t1["l0Stairs"], f"{SN8['stairs'][0]:,}"),
            ("the gully L0", o["l0Gully"], t2["l0Gully"], t1["l0Gully"], f"{SN8['gully'][0]:,}"),
            ("the gully L1", "", t2["l1Gully"], t1["l1Gully"], f"{SN8['gully'][1]:,}")]
    for r in rows:
        a("| " + " | ".join(str(_n(v)) if isinstance(v, (int, float)) else str(v) for v in r) + " |")
    a("")
    a(f"The triangles are SN8's table: a face stone {TRI['face'][0]} at L0 and {TRI['face'][1]} at L1; a coping, "
      f"head, through or topstone {TRI['coping'][0]} and {TRI['coping'][1]}; a step stone or slab {STEP_TRI[0]} and "
      f"{STEP_TRI[1]}; a laid panel face's fill {FILL_TRI[0]}. The laid face is "
      f"{t2['seenStairM2']} m² on the stair side and {t2['seenBankM2']} m² on the bank side, coping faces and the "
      f"ground's buried strip included. That is {round(t2['faceStones'] / seen_c, 1)} face stones a m² of seen course "
      f"face, and {round(t2['l0Walls'] / seen_c)} L0 triangles a m², against SN8's {round(d0)}.")
    a("")
    a("**How long the laying takes.** This is CPython, in one process on one thread, on "
      f"{tm['machine'].split(', Python')[0]}. Each time is the median of {tm['runs']} runs, measured with "
      "`time.perf_counter` around each part. The C# port will differ: it will have other data structures, no "
      "interpreter, and possibly other searches, so these numbers size the work but are not the C# cost.")
    a("")
    a("| | ms | ms a m² of laid face | ms a stone |")
    a("| --- | --- | --- | --- |")
    a(f"| the whole gully, walls and steps (two goings) | {tm['totalMs']:,.1f} | {tm['perM2']} | {tm['perStone']} |")
    a(f"| the walls alone | {tm['totalMs'] - tm['parts'].get('steps', 0):,.1f} | {tm['perM2Walls']} | "
      f"{tm['perStoneWalls']} |")
    a(f"| the largest panel's fill ({tm['largest']['panel']}, {tm['largest']['m2']} m², "
      f"{tm['largest']['stones']} stones) | {tm['largest']['fillMs']} | {tm['largest']['fillPerM2']} | "
      f"{tm['largest']['fillPerStone']} |")
    a(f"| that panel's line re-laid for an event in it, every feature included | {tm['largest']['lineRelayMs']} | | |")
    a(f"| the bond tests (SN10, in this tool, not the laying) | {tm['tests'].get('bond tests (SN10)', 0)} | "
      f"{tm['bondPerM2']} | {tm['bondPerStone']} |")
    a(f"| the one-going variant, the whole gully ({tm1['runs']} runs) | {tm1['totalMs']:,.1f} | {tm1['perM2']} | "
      f"{tm1['perStone']} |")
    a("")
    tot_parts = sum(tm["parts"].values())
    a("| Part of the laying | ms | share |")
    a("| --- | --- | --- |")
    for k, v in sorted(tm["parts"].items(), key=lambda kv: -kv[1]):
        a(f"| {k} | {v} | {round(100 * v / tot_parts)}% |")
    feat = sum(v for k, v in tm["parts"].items() if k.startswith("features"))
    fill = sum(v for k, v in tm["parts"].items() if k.startswith("fill"))
    a("")
    a(f"Features take {round(feat, 1)} ms ({round(100 * feat / tot_parts)}%), the fill {round(fill, 1)} ms "
      f"({round(100 * fill / tot_parts)}%) and the steps {tm['parts'].get('steps', 0)} ms. The fill keeps the bond "
      "itself: each stone's length is chosen clear of the joints below and above, so the laying has no separate "
      "bond pass, and the bond tests above are only this tool's check. The other tests take "
      f"{tm['tests'].get('other tests', 0)} ms. For a city: {wall_len:.1f} m of wall line, with "
      f"{round(t2['faceM2'] / wall_len, 2)} m² of laid face a metre of line (both faces, copings and the buried "
      f"strip included), take {round((tm['totalMs'] - tm['parts'].get('steps', 0)) / wall_len, 1)} ms a metre of line to lay, "
      f"so about {round((tm['totalMs'] - tm['parts'].get('steps', 0)) / wall_len):,} s a kilometre of such wall, "
      "in this Python. Nothing was changed for speed.")
    a("")
    # ------------------------------------------------------------------------------------------------ visibility
    a("## The visibility measurement")
    a("")
    a("`tools/r1_elevations.py visibility` measures which panel faces are seen. Its method, as written into "
      "`facts.json`:")
    a("")
    for k in ("faces", "eyes", "ground", "rays", "classes", "measuredOn"):
        a(f"- **{k}:** {vis['method'][k]}.")
    e = vis["eyes"]
    a(f"- **counts:** {vis['samples']:,} samples; {e['view']} judging views, {e['lane']:,} eyes on lanes, stairs and "
      f"quays, {e['place']} on the places, {e['yard']} in the yards ({e['droppedInHouses']} dropped inside houses). "
      f"{vis['rays']['views']:,} rays from the views, {vis['rays']['walkable']:,} from the walkable ground (each "
      "sample stops at its first clear ray, nearest eyes first).")
    if vt:
        a(f"- **time:** {vt['measureS']} s to measure, after {vt['importS']} s to import the clay's layout.")
    a("")
    a("| Face | Seen within 8 m | Seen only beyond 8 m | Seen from nowhere | Buried | Faces laid |")
    a("| --- | --- | --- | --- | --- | --- |")
    for f in FACES:
        x = vtot[f]
        a(f"| {f} | {x['near']} | {x['farOnly']} | {x['unseen']} | {x['buried']} | {x['facesLaid']} of "
          f"{x['faces']} |")
    a(f"| both | {near} | {far} | {unseen} | {buried} | {n_laid} of {n_faces} |")
    a("")
    a(f"The area is in m² of course face (copings and topstones are not sampled: they are {tops_m2} m² more, and "
      f"seen from every side). **{far} m² is seen only from beyond 8 m.** {far_whole_m2} m² of it is in "
      f"{len(far_whole)} whole faces, every one a bank face on fl-1: "
      + ", ".join(f"{p.split('/', 1)[1]} {f}" for p, f in far_whole) + ". The rest is in "
      + ", ".join(f"{p.split('/', 1)[1]} {f}" for p, f in far_part) + ", which are also seen from near.")
    a("")
    fo = vis.get("farOnly", {})
    if fo.get("nearestEyeM"):
        q = fo["nearestEyeM"]
        a(f"The far-only area is not seen from far off. Its nearest clear eye on the walkable ground is {q[0]} to "
          f"{q[-1]} m away (median {q[2]}), standing on "
          + "; ".join(f"{k}, {v} m²" for k, v in sorted(fo["seenFrom"].items(), key=lambda kv: -kv[1]))
          + ". So those faces sit in L1's range, never in L0's.")
        a("")
    sens = vis["sensitivity"]
    wh = sens.get("withHouses")
    a("**Sensitivity.** Without the yards (they may not be walkable in play), "
      f"{len(sens['withoutYards']['facesChanged']) or 'no'} faces change. With eyes out to {RANGE_WIDE:g} m, "
      f"{len(sens['at120m']['facesChanged']) or 'no'} faces change." +
      (f" With the clay's {wh['houses']} houses as occluders too (boxes over their footprints to their eaves, roofs "
       f"left out), {len(wh['facesChanged']) or 'no'} faces change; on the bank side the area seen within 8 m falls "
       f"from {vtot['bank']['near']} to {wh['m2']['bank']['near']} m², the far-only area rises to "
       f"{wh['m2']['bank']['farOnly']} m², and {_m2(wh['m2']['bank']['unseen'] + wh['m2']['stair']['unseen'])} "
       "is seen from nowhere. The result does not rest on leaving the houses out." if wh else ""))
    a("")
    a("The sheet `visibility.png` shows each sample by its class: near, far only, unseen, or buried.")
    a("")
    # ------------------------------------------------------------------------------------------------ budget
    a("## The budget, re-derived (a proposal)")
    a("")
    a(f"SN8 sets the walls at {_n(SN8['walls'][0])} L0 and {_n(SN8['walls'][1])} L1 for about {SN8['faceM2']} m² of "
      f"face. Its estimate counts {SN8['faceM2']} m² of course face for the face stones and adds the copings, so its "
      f"density is {round(d0)} L0 and {round(d1)} L1 triangles a m² of course face, copings included.")
    a("")
    a(f"- **A (proposed): every seen face at L0.** {seen_c} m² of seen course face ({near} within 8 m plus {far} only "
      f"beyond) gives L0 {round(d0)} × {seen_c} = {_n(A0)} and L1 {round(d1)} × {seen_c} = {_n(A1)}. The buried "
      f"{buried} m² is left out: it is laid because its faces are seen, but nobody sees it. The walls lay "
      f"{_n(t2['l0Walls'])} L0 ({_n(A0 - t2['l0Walls'])} under) and {_n(t2['l1Walls'])} L1 "
      f"({_n(A1 - t2['l1Walls'])} under).")
    a(f"- **B: the faces seen only from beyond 8 m built at L1 alone.** L0 {round(d0)} × "
      f"({seen_c} − {far_whole_m2}) = {_n(B0)}; L1 as A. Those faces hold {n_fw} face stones, which would have no "
      f"L0, so the walls' L0 count becomes {_n(l0B)}. B saves only memory and export time: L0 is drawn within 8 m "
      "anyway, so frame time does not change. It also ties the mesh to today's eyes, so B belongs to step 5's "
      "chunks, if anywhere.")
    a(f"- **Steps.** SN8's {_n(SN8['stairs'][0])} assumed {SN8['steps']} steps of about {SN8['stonesAStep']} stones "
      f"at {SN8['triAStone']} triangles, and {_n(SN8['rests'])} for the rests. The facts give {len(st_steps)} steps "
      f"of two stones each and {len(st_rests)} rests and landings of {n_rest_slabs} slabs, so {t2['stepStones']} "
      f"stones. One stone cannot span a step: the stair is {2 * so0['half']} mm between the walls' faces with the "
      f"ends in them, and the longest slab is {slab['hi']}. Proposed: L0 {_n(S0)} and L1 {_n(S1)}, the table's "
      f"{STEP_TRI[0]} and {STEP_TRI[1]} a stone. The other way is to hold {_n(SN8['stairs'][0])} at "
      f"{SN8['stairs'][0] // t2['stepStones']} triangles a stone, which R2b's step part would have to meet.")
    a(f"- **The gully,** A plus the steps: L0 {_n(G0)} and L1 {_n(G1)}, against SN8's {_n(SN8['gully'][0])} and "
      f"{_n(SN8['gully'][1])}. It lays {_n(t2['l0Gully'])} and {_n(t2['l1Gully'])}.")
    a("")
    a("design.md is not edited; the reviewer decides. `kinds/wall.json`'s levels keep SN8's numbers, marked "
      "provisional.")
    a("")
    # ------------------------------------------------------------------------------------------------ reports
    a("## The laying's own reports")
    a("")
    a(f"Two goings. {len(flags2)} flags, {len(cuts2)} boundary cuts, {len(fills2)} free lengths laid with less than "
      f"the full rule, {len(falls2)} fall points not placed, {len(thr2)} through stones not placed.")
    a("")
    for w in lay2["walls"]:
        r = w["report"]
        a(f"**{w['id']}.**")
        a("")
        for fp in r["falls"]:
            a(f"- fall at s {fp['s']}, z {fp['z']}: {fp['result']}")
        hows = {}
        for fr in r["fills"]:
            hows[fr["how"]] = hows.get(fr["how"], 0) + 1
        if hows:
            a(f"- free lengths laid without the full rule: {', '.join(f'{v} {k}' for k, v in sorted(hows.items()))}")
        for x in r["throughs"]:
            a(f"- through stone not placed in {x['panel']} at {x['at']}: {x['result']}")
        for x in r["cuts"]:
            a(f"- cut: {x}")
        for x in r["flags"]:
            a(f"- flag: {x}")
        if not any(r.values()):
            a("- nothing to report")
        a("")
    a("**The rules that place the features, and why** (each found by a failure in this round's runs, fixed at its "
      "cause):")
    a("")
    moved = [(w["id"], r_) for w in lay2["walls"] for r_ in w["risers"] if r_.get("moved")]
    a(f"- **Risers move within their window** (half a going either side of where the ideal bed puts them), by three "
      f"rules in order. {len(moved)} of {t2['risers']} risers moved:")
    for wid, r_ in moved:
        a(f"  - {wid} riser at {r_['at']} (ideal {r_['ideal']}): {r_['moved']}")
    a("  1. *A straight joint:* a riser within a lap of a rebuilt panel's edge snaps onto it. If it is just above the "
      "edge, it moves until its stepped section's corner stone (at least twice the course's height) and the edge's "
      "stone both fit before the joint. Before this rule, fl-0/r's riser at 5769 left 457 mm to the 6226 edge, and "
      "the corner and the edge stone could not both be laid.")
    a(f"  2. *Whole slabs:* between two risers the run takes whole slabs ({D.COPE_L[0]} to {D.COPE_L[1]} mm), "
      "pushing the next riser along within its window where it must.")
    a(f"  3. *The end runs:* a wall's end run is either its topstone alone or a topstone and a whole slab.")
    a("- **Panels are bounded at the rests' coping run ends** and at the rebuilt panel's edges. A wall's ends are its "
      f"heads, not panel boundaries. This gives {sum(len(w['panels']) for w in lay2['walls'])} panels where round 1 "
      f"had {o['panels']}.")
    a("- **Teeth look one course ahead:** a boundary's tooth in a course is chosen so the course above still has a "
      f"lapped tooth of at least {D.TOOTH[0]} mm. Where none fits in {D.TOOTH[0]} to {D.TOOTH[1]}, it goes up to "
      f"{D.TOOTH_WIDE[1]} (flagged), and below {D.TOOTH[0]} only to keep its laps (flagged).")
    a("- **The end stones' rules hold for every stone laid first** (heads, teeth, falls and throughs): a stepped "
      f"section's corner stone at least {D.RISER_FIRST} times its height, and the rebuilt panel's edge stones long and "
      "short in alternate courses.")
    a("- **The heads keep clear of the joints fixed above and below them**: the risers' corner joints, the stones "
      "laid first, and the coping joints over the top course.")
    a("- **Each face's head stands on that face's own footing.** A tie runs through both faces only in courses where "
      "both faces stand at the wall's end; below the higher footing the lower face goes on alone, a header or a "
      "runner by the head's order, in its own courses. Before this rule the head started both faces at the lower "
      "footing, so at the top ends of fl-0/l and fl-1/r a stair-face stone stood under the top step's level, in the "
      "last steps' ends (st-gully/fl-0/tr-28 and tr-29, st-gully/fl-1/tr-47), and the granite record's fl-0/r tie "
      "did the same. SN9's new tiling checks found it in the self-check; no other check had looked.")
    a("")
    # ------------------------------------------------------------------------------------------------ panels
    a("## Panels re-laid one at a time")
    a("")
    a("Each panel is re-laid with an event's seed on its own id, and every stone that changes is counted.")
    a("")
    for lbl, rr in (("Two goings", ind), ("One going", ind1)):
        bad = [r for r in rr if r["changedOutside"]]
        a(f"- **{lbl}:** {len(rr) - len(bad)} of {len(rr)} panels change only their own stones (from "
          f"{min(r['changedInside'] for r in rr)} to {max(r['changedInside'] for r in rr)} of them).")
        for r in bad:
            a(f"  - {r['panel']}: {r['changedInside']} inside and {r['changedOutside']} outside, e.g. "
              f"{', '.join(r['outside'][:3])}")
    a(f"- Round 1: {o['independent']} of {o['panels']}. The leaks were at boundaries where a course took no tooth, so "
      "one stone crossed the boundary. Now such a course ends against the ground or a step, and the report names it "
      "as a cut (above).")
    a("")
    # ------------------------------------------------------------------------------------------------ data
    a("## What lives in data, and what stays in code")
    a("")
    a("Changing style, era or world must be a data edit (the coordinator, for Øystein; design.md 7b). `masonry.py` "
      "reads every number that depends on the stone, its working, its era or the style into a `Rules`, from two "
      "files:")
    a("")
    a("- **The pack's walling table, `packs/stavanger-1989/walling.json`**, by the working a wall's facts name "
      "(`dry-split-1874`, its 1961 rebuild `cement-relaid-1961`). It holds the stone's and the builders' numbers: "
      "the course heights (`courseMm`, `riseOneMm`, `foundationMm`); the stones (`stoneMm`, `drawnPerHeight`, "
      "`shortMm`); the copings (`copeThickMm`, `copeNominalMm`, `copeLengthMm`, `copeLeastMm`); the topstones, head "
      "ties and runners (`topstoneMm`, `headTieMm`, `headRunnerMm`); the through stones (`throughMm`, "
      "`throughFirstMm`, `throughEveryMm`); a rebuilt panel's edge stones (`edgeStonesMm`); and the steps' laps and "
      "joints (`steps`). Each value has a note with its reason and source. Round 1 had all of these as module "
      "constants.")
    a("- **The wall kind, `kinds/wall.json`**, beside `kinds/stair.json`, in `schemas/kind.schema.json`'s shape. Its "
      "plan params hold the wall's structure: the parapet's height, one or two goings a level run, a head's courses, "
      "the topstone's squareness, a stepped section's corner stone, the free courses' step, the bank footing's "
      "tread, the panels' teeth, the throughs' clearance and shift, and where the steps' ends sit in the walls.")
    a("- **In code, the rules of any wall:** level beds and no rake; SN2's sliver (50 mm) and acute (25°) limits; "
      "SN10's bond (no stone over 4.5 times its height, a lap of 0.4 of the course and at least 40 mm, the "
      "four-stone cross, joints through more than two courses); a stone falls when nine tenths of its bed is gone. "
      "Two more numbers stay in code because they are only the search's resolution and reach (5 mm steps for a "
      "through stone, 300 mm of free courses over the top), not facts about any wall. `Rules` also checks the data "
      "against the code's rules, so a bad edit raises an error and is never laid quietly.")
    a("- **Gone with the stepped tops:** round 1's kneelers, knees, raked copings and their numbers.")
    a("- **What the schemas cannot hold.** `schemas/material.schema.json` refuses a walling section "
      "(`additionalProperties: false`), so I did not put one into `materials/slate.json`. The walling table is a pack "
      "table in `stairs.json`'s format instead, keyed by working, with each working naming its material. No schema "
      "validates either table. A walling schema, or a `walling` section in the material schema, is for the reviewer "
      "to decide. `tools/validate_record.py` passes with `kinds/wall.json` in the registry.")
    a("- **Joint widths** between wall stones are not modelled at R1: the stones meet at their outlines. When R2's "
      "geometry needs them, they belong in the working (a dry slate's few mm against a mortared granite's 10 to "
      "15 mm). The steps' tread joints (4 to 10 mm, SN5) are in the walling table already.")
    a("")
    a("### The granite record (design.md 7b)")
    a("")
    a(f"`r1/granite-1930.json` is a test record, not researched, in the walling table's shape. It holds two workings "
      f"no gully wall has: `{rec['applies']['walls']}` (squared granite in level mortared courses, 140 to 340 mm "
      f"high, stones 300 to 1200 mm, slab copes 500 to 1200 mm) and `{rec['applies']['rebuilt']}`. The tool merges "
      "them into a copy of the pack's table, points the facts' walls and their rebuilt panel at them, and lays and "
      "tests the same walls with the same functions. No code changes.")
    a("")
    if "T" in V2:
        Vt = V2["C"]["totals"]
        a(f"- **Laid:** hash `{V2['hashes'][0]}`, again `{V2['hashes'][1]}` "
          f"({'the same' if V2['hashes'][0] == V2['hashes'][1] else 'DIFFERENT'}). {_n(Vt['wallStones'])} wall "
          f"stones, {Vt['copings']} copings, {Vt['throughs']} throughs; walls L0 {_n(Vt['l0Walls'])} and L1 "
          f"{_n(Vt['l1Walls'])}.")
        vrep = sum(1 for t in V2['T'].t.values() if not t["checked"])
        a(f"- **Tests:** {len(V2['T'].t) - vrep} checks, {len(V2['T'].t) - vrep - len(vfail)} pass, "
          f"{len(vfail)} fail{'s' if len(vfail) == 1 else ''}. {by_rule(vfail)[0]}" +
          (f"; {' and '.join(by_rule(vfail)[1])} fail{'s' if len(by_rule(vfail)[1]) == 1 else ''}:"
           if by_rule(vfail)[1] else "."))
        for (sn, name), t in sorted(vfail.items()):
            for x in t["fails"][:6]:
                a(f"  - FAIL {sn} {name}: {x['where']}, {x['what']}")
        a(f"- **The laying's reports:** {len(V2['flags'])} flags, {len(V2['cuts'])} cuts, {len(V2['fills'])} free "
          "lengths laid with less of the rule" + (": " + "; ".join(sorted(set(x["how"] for x in V2["fills"])))
                                                  if V2["fills"] else "") + ".")
        if "T" in V1:
            v1f = V1["T"].failing()
            a(f"- **One going:** hash `{V1['hashes'][0]}` ({'stable' if V1['hashes'][0] == V1['hashes'][1] else 'UNSTABLE'}); "
              + ("; ".join(f"{sn} {name} fails {len(t['fails'])}" for (sn, name), t in sorted(v1f.items())) or
                 "every check passes") + ".")
        if vfail:
            a("- **Why the slabs fail:** at fl-0's top ends, the run from the last riser to the wall's end is about "
              "670 mm. Neither a square topstone alone (at most about 400 mm in the granite's courses) nor a "
              "topstone and a whole slab (at least 800 mm) fits, and the risers cannot move further inside their "
              "windows. The laying lays a slab of what is left (never under the working's least, `copeLeastMm`, 300) "
              "and flags it, and SN2's test fails it. "
              "This is the granite's numbers meeting the gully's goings, not the code: the slate passes with the "
              "same functions.")
    else:
        a(f"- **Refused:** {V2.get('refused')}")
    a("")
    # ------------------------------------------------------------------------------------------------ the sheet
    a("## The sheet")
    a("")
    a("Look first at `fl-0-r-stair.png` (the 1961 panel, its edges and the moved risers), `fl-1-r-bank.png` (a "
      "bank face seen only from beyond 8 m, its footing stepping with the ground) and `steps-plan.png`.")
    a("")
    for s in sheet:
        a(f"- `{s}`")
    a("")
    a("Each elevation is drawn at 1:50 in strips of 6 m. Face stones are grey, the 1961 panel's are a warmer grey; "
      "throughs, head ties, runners, topstones and copings each have their own tone. A failing check is drawn in "
      "red, and a stone the fill laid with less of the rule in magenta. On the stair faces each fall point the "
      "facts give is ringed: orange where its stone fell (the hole is black), black where the facts hold it, grey "
      "where no stone could be chosen for it. The legend is on each sheet.")
    a("")
    # ------------------------------------------------------------------------------------------------ fails
    a("## What fails, and why")
    a("")
    k_one = f"coping slabs {D.COPE_L[0]} to {D.COPE_L[1]} mm"
    a(f"1. **One going a level run: {len(tget(T1, 'SN2', k_one)['fails'])} coping slabs under {D.COPE_L[0]} mm.** "
      f"A going here is {min(goings)} to {max(goings)} mm, so a level run of one going is about 300 mm long and holds "
      f"no whole slab. The laying lays each such run as one slab of its own length (never under the working's least, "
      f"{D.COPE_MIN} mm) and flags it: {sum(1 for w in lay1['walls'] for x in w['report']['flags'] if 'under a whole coping slab' in x)} "
      f"of the one-going variant's {sum(len(w['report']['flags']) for w in lay1['walls'])} flags. SN2's test fails "
      "them. This is the nature of one going with this coping, not a fault to fix; it is why two goings are laid.")
    if vfail:
        a("2. **The granite record: two coping slabs under 500 mm at fl-0's top ends.** See The granite record: its "
          "numbers, not the code.")
    a(f"3. **The budgets.** The walls' L0 ({_n(t2['l0Walls'])}) is over SN8's {_n(SN8['walls'][0])} and inside the "
      f"re-derived {_n(A0)} by {round(100 * (A0 - t2['l0Walls']) / A0, 1)}%. The steps' L0 ({_n(S0)}) is over SN8's "
      f"{_n(SN8['stairs'][0])}, because the facts make {t2['stepStones']} stones where SN8 assumed about "
      f"{round(SN8['steps'] * SN8['stonesAStep'])} plus the rests. Both are proposals for the reviewer.")
    a(f"4. **The flags and cuts.** {len(flags2)} flags: "
      + "; ".join(x.replace("wl-gully/", "") for x in flags2)
      + f". {len(cuts2)} cuts: at each, a panel's boundary or the 1961 edge lies within one least stone "
        f"({D.STONE[0]} mm) of the course's end against the ground or a step, so no tooth fits. The course's "
        "end serves as the boundary's joint, and the stone there belongs to the panel that holds its middle. None "
        "breaks a check; each is listed under The laying's own reports.")
    a(f"5. **The steps' 9 mm of play (SN3).** The longest slab is {slab['hi']} mm and the stair "
      f"{2 * so0['half']} mm across, ends in the walls. Its joint must then start in {jw['left']} or {jw['right']} "
      f"mm, outside the middle third ({so0['third']} mm either side of the walking line): {jw['widthMm']} mm of play "
      "a side. So every step's joint lies on one of two lines about a metre apart, alternating up the stair. Every "
      "SN3 check passes. Whether the two lines read as mechanical is a look question for R2b's grey sheet, not a "
      "rule's, and I propose no change without that evidence. A longer slab is the finish's fact, from "
      "`kinds/stair.json`.")
    a(f"6. **fl-1's rests.** {len(deep)} rests are {min(d for _, d, _ in deep)} to {max(d for _, d, _ in deep)} mm "
      f"deep, more than the longest slab ({slab['hi']}), so each takes four slabs in two rows where the plan names "
      "two. SN3's \"two to four slabs\" passes. A rest's two slabs must also meet within "
      f"{slab['hi'] - so0['half']} mm of the centre, inside the middle third. SN3 puts that rule on steps, so the "
      "rest joints are notes, not failures. No rule change: both follow from the plan's depths and the finish's "
      "sizes.")
    a("")
    # ------------------------------------------------------------------------------------------------ assumed
    a("## Assumed")
    a("")
    a("- **Houses are not occluders in the measurement,** since the brief names the terrain and the walls, and the "
      "clay's houses are blockouts that will move. A sensitivity adds them as boxes to their eaves: "
      + (f"{len(vis['sensitivity']['withHouses']['facesChanged']) or 'no'} faces change (The visibility "
         "measurement)." if vis["sensitivity"].get("withHouses") else "not run."))
    a(f"- **The eyes:** a standing eye at {EYE} m over every walkable lane, stair, quay, place and yard within "
      f"{RANGE:g} m, and the six judging views in their frames. A wall's occluding top is a slab {WALL_TOP[0]} to "
      f"{WALL_TOP[1]} m outside the stair's clear half-width, up to its coping's top. L0's range is 8 m (SN8).")
    a("- **A sample is buried** where the ground 0.1 m outside the face stands over its mid-height. Buried stones are "
      "laid, because their face is seen.")
    a("- **Two goings** a level run is the variant laid and counted; one going is laid and tested beside it.")
    a(f"- **\"A whole course a step\"** (SN2) is read as a whole number of courses: with two goings and one course "
      f"a rise, the coping steps by two courses (up to {dr2[0][-1]} mm). Read as exactly one course, SN2's own "
      "two-going option could not exist once a course is a rise. SN2's \"an extra course goes in where a step would grow too big\" gives no number, "
      "and no step here is more than two rises, so none goes in; R2b's grey form judges the steps' size.")
    a(f"- **A stepped section's corner stone** is at least {D.RISER_FIRST} times its course's height (SN2 does not "
      "give a number).")
    a("- **The 1961 panel's edges** are straight joints through every course by the facts, exempt from SN10's laps "
      "and chains; its edge stones are long and short in alternate courses.")
    a("- **The foundation courses** under the foot hold no stones at R1, since no face reaches below the foot. Their "
      "lines are drawn from the largest down: each is at least the course over it (fixed this round, after the "
      f"self-check found fl-0/r's at 194 under 252). SN10's test now checks every course above, as its rule says.")
    a("- **Seeds and rounding** as round 1: every draw keys on the pack's world seed through `HS.Stream`, `HS.h` and "
      "`HS.between`. The facts were rounded once to integer mm at the boundary. wall.py's own fact draws (the 1961 "
      "panel, the fall points, which falls cement holds) are at its seed 1, so R1 is re-run when they move into a "
      "wl-gully record.")
    a("- **`tools/check.py`** does not exist yet: it is built after the reset on 26 October. This run's own tests and "
      "`tools/validate_record.py` stand in for it.")
    a("- **Not laid at R1:** the coping's rebates and the batter (3D, R2); the patched holes; the 1952 campaign's "
      "reset run; the hidden work under the step ends and the stair's surface.")
    a("")
    with open(os.path.join(OUT, "report.md"), "w") as fh:
        fh.write("\n".join(L) + "\n")


if __name__ == "__main__":
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
    if argv and argv[0] == "ground":
        blender_ground(argv[1])
    elif argv and argv[0] == "facts":
        gather_facts()
    elif argv and argv[0] == "visibility":
        visibility_main()
    elif argv and argv[0] == "hash":
        print(lay_hash(json.load(open(FACTS)), int(argv[1]) if len(argv) > 1 else 2))
    else:
        main(argv)
