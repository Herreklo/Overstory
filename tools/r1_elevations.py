"""Port step 2b, rung R1: the gully's cheek walls and steps laid as 2D elevations in integer millimetres, by a mason's
rules, before any mesh (reviews/lt1/port/2b/design.md, The ladder; SN2, SN3, SN10). The laying is
blender/generators/masonry.py; this tool gathers its facts, runs it twice, checks it and draws the sheet.

    PY=/Applications/Blender.app/Contents/Resources/5.2/python/bin/python3.13
    $PY tools/r1_elevations.py facts      the facts, once: the stair's plan from its stages (tools/run_kind.py), the
                                          ground behind each wall and wall.py's own fact draws (Blender, about 2 min)
                                          -> reviews/lt1/port/2b/r1/facts.json, in integer mm
    $PY tools/r1_elevations.py            the layout from facts.json, twice, its hash; layout.json, report.md and
                                          the sheet (one PNG per wall elevation, the steps in plan)

The facts are rounded to integer mm here, at the boundary, and nowhere else (the rounding is recorded in facts.json).
"""
import json
import math
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "blender", "generators"))
sys.path.insert(0, os.path.join(ROOT, "blender", "resolver"))

OUT = os.path.join(ROOT, "reviews", "lt1", "port", "2b", "r1")
FACTS = os.path.join(OUT, "facts.json")
BLENDER = "/Applications/Blender.app/Contents/MacOS/Blender"
BPY = "/Applications/Blender.app/Contents/Resources/5.2/python/bin/python3.13"
RECORD = os.path.join(ROOT, "fixtures", "records", "st-gully.json")
GOLDEN_PLAN = "a99de7262eee1c2b"     # fixtures/golden/stair/plan.json's output hash


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
                                                                cause=reb["cause"]),
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
        stair=dict(id="st-gully", builtAs=o["builtAs"], finish=o["finish"], flights=flights),
        walls=dict(id="wl-gully", built=1874, lines=lines),
    )
    os.makedirs(OUT, exist_ok=True)
    with open(FACTS, "w") as fh:
        json.dump(facts, fh, indent=1, sort_keys=True)
    print("facts written", FACTS, "hash", HX.hash_hex(facts), "plan", plan_hash,
          "matches golden" if plan_hash == GOLDEN_PLAN else "DIFFERS FROM GOLDEN")


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


def x_at(poly, z):
    """The outline's extent along s at height z (a convex outline)."""
    xs = []
    for p, q in zip(poly, poly[1:] + poly[:1]):
        if (p[1] - z) * (q[1] - z) <= 0 and p[1] != q[1]:
            xs.append(p[0] + (z - p[1]) * (q[0] - p[0]) / (q[1] - p[1]))
        elif p[1] == q[1] == z:
            xs += [p[0], q[0]]
    return (min(xs), max(xs)) if xs else None


# ---------------------------------------------------------------------------------------------------------------
# The checks

class Tests:
    """Each test: what it checks, how many it checked, its failures (each with where and what), and marks for the
    sheet."""

    def __init__(self):
        self.t = {}
        self.marks = {}

    def add(self, sn, name, rule):
        self.t.setdefault((sn, name), dict(sn=sn, name=name, rule=rule, checked=0, fails=[], notes=[]))
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


def faces_of(st):
    return st["faces"]


def wall_tests(T, w, fl, M):
    lid = w["id"]
    Lz = [l["z"] for l in w["lines"]]
    nb = len(Lz) - 1
    Hc = [Lz[m + 1] - Lz[m] for m in range(nb)]
    tops = [fl["zFoot"]] + [st["zTop"] for st in fl["steps"]]
    course_kinds = ("face", "through", "head")
    # ---- SN1, SN4, SN2's slivers: every stone's outline
    for st in w["stones"]:
        poly = st["outline"]
        pts = simplified(poly)
        mk = [(lid, f, "stone", st["id"]) for f in faces_of(st)]
        allint = all(isinstance(v, int) for p in poly for v in p)
        T.check("SN1", "integer outlines", "every outline is integer mm", allint, st["id"], "a coordinate is not an "
                "integer")
        T.check("SN1", "convex", "every stone is a convex block (its face outline convex)", convex(pts), st["id"],
                f"not convex: {pts}", mk[0] if mk else None)
        T.check("SN4", "4 to 7 edges", "a face outline has four to seven straight edges", 4 <= len(pts) <= 7,
                st["id"], f"{len(pts)} edges: {pts}", mk[0] if mk else None)
        el, an = edge_lengths(pts), angles(pts)
        T.check("SN2", "no face under 50 mm", "no edge of a face shorter than 50 mm (no slivers)", min(el) >= M.SLIVER,
                st["id"], f"an edge of {min(el):.0f} mm", mk[0] if mk else None)
        T.check("SN2", "no angle under 25 degrees", "no corner more acute than 25 degrees", min(an) >= M.ACUTE,
                st["id"], f"a corner of {min(an):.1f} degrees", mk[0] if mk else None)
        z0, z1 = span(poly, 1)
        if st["kind"] in course_kinds:
            T.check("SN2", "no stone under 50 mm high", "no stone under 50 mm high", z1 - z0 >= M.SLIVER, st["id"],
                    f"{z1 - z0} mm high", mk[0] if mk else None)
            zs = sorted(set(p[1] for p in poly))
            lvl = [z for z in zs if z in Lz]
            ok = z0 in Lz and z1 in Lz and all(z in Lz for z in zs) or (st["kind"] == "face" and len(pts) == 5)
            T.check("SN2", "level beds on course lines", "a course stone's bed and top are level, on course lines",
                    ok, st["id"], f"heights {zs} not all course lines", mk[0] if mk else None)
            x0, x1 = span(poly, 0)
            T.check("SN10", "no stone over 4.5 x its height", "no stone longer than 4.5 times its height",
                    2 * (x1 - x0) <= 9 * (z1 - z0), st["id"], f"{x1 - x0} x {z1 - z0} mm ({(x1 - x0) / (z1 - z0):.2f})",
                    mk[0] if mk else None)
        elif st["kind"] in ("kneeler", "knee", "topstone"):
            bed = [p for p in poly if p[1] == z0]
            T.check("SN2", "level beds on course lines", "a course stone's bed and top are level, on course lines",
                    len(bed) >= 2 and z0 in Lz, st["id"], f"its bed {z0} is not a level course line",
                    (lid, "stair", "stone", st["id"]))
    # ---- SN2: the courses
    for m in range(nb):
        T.check("SN2", "course heights 60 to 140", "every course 60 to 140 mm high (wall.py's COURSE); none under 50",
                M.COURSE[0] <= Hc[m] <= M.COURSE[1], f"{lid} course {m}", f"{Hc[m]} mm")
    for i, z in enumerate(tops):
        T.check("SN2", "a line on each step top", "one course line on each step top", z in Lz, f"{lid} step top {i}",
                f"{z} is not a course line")
    for i in range(len(tops) - 1):
        between = [z for z in Lz if tops[i] < z < tops[i + 1]]
        T.check("SN2", "at most one line between step tops", "at most one line between two step tops",
                len(between) <= 1, f"{lid} rise {i}", f"{len(between)} lines between {tops[i]} and {tops[i + 1]}")
    for a, b, z in w["footing"]["bank"]:
        T.check("SN2", "bank footing in whole courses", "on the bank side the footing steps with the ground, each step "
                "a whole course", z in Lz, f"{lid} bank footing {a} to {b}", f"{z} is not a course line")
    treads = [b - a for a, b, z in w["footing"]["bank"][1:-1]]
    if treads:
        T.note("SN2", "bank footing in whole courses", "", f"{lid}: {len(w['footing']['bank'])} footing steps, the "
               f"shortest inner tread {min(treads)} mm")
    ends = {}
    for f in M.FACES:
        for m in range(nb):
            for r in w["regions"][f][m]:
                for side in ("l", "r"):
                    ends[r[side]] = ends.get(r[side], 0) + 1
                    T.check("SN2", "every course ends at a footing or the coping", "each course starts on the "
                            "footing uphill and ends under the coping downhill (or at the wall's head)",
                            r[side] in ("rake", "feature", "end", "step", "ground"), f"{lid} {f} course {m} at "
                            f"{r['a'] if side == 'l' else r['b']}", f"ends at {r[side]}")
    T.note("SN2", "every course ends at a footing or the coping", "", f"{lid}: course ends by kind {dict(sorted(ends.items()))}")
    # ---- SN2: kneelers and knees at the breaks
    P = w["pitch"]
    ups, downs = [], []
    if P[0][0] <= w["s"][0] + M.SLIVER:
        ups.append(P[0][0])
    for p, q, r_ in zip(P, P[1:], P[2:]):
        if q[1] == p[1] and r_[1] > q[1]:
            ups.append(q[0])
        if q[1] > p[1] and r_[1] == q[1]:
            downs.append(q[0])
    if P[-1][1] > P[-2][1]:
        downs.append(P[-1][0])
    if P[0][0] > w["s"][0] + M.SLIVER:
        ups.append(P[0][0])
    feats = w["features"]
    for s in ups:
        lane = abs(s - w["s"][0]) <= M.SLIVER
        T.check("SN2", "a kneeler at every upward break", "a kneeler at the foot of every raked run, at the lane and "
                "every rest-to-flight break", any(f_["kind"] == "kneeler" and not f_["mid"] and
                                                  (f_["at"] == s or (lane and f_["lane"])) for f_ in feats),
                f"{lid} at {s}", "no kneeler")
    for s in downs:
        T.check("SN2", "a knee at every downward break", "a knee stone at every flight-to-rest break",
                any(f_["kind"] == "knee" and f_["at"] == s for f_ in feats), f"{lid} at {s}", "no knee")
    for f_ in feats:
        if f_["mid"]:
            T.check("SN2", "intermediate kneelers every 2.4 to 3.6 m", "an intermediate kneeler 8 to 12 goings (2.4 "
                    "to 3.6 m) from the stop below", M.KNEELER_EVERY[0] <= f_["fromStop"] <= M.KNEELER_EVERY[1],
                    f_["id"], f"{f_['fromStop']} mm from the stop below")
    for c in w["ceiling"]:
        if c["kind"] == "rake":
            T.check("SN2", "intermediate kneelers every 2.4 to 3.6 m", "no raked stretch longer than 3.6 m between "
                    "its stops", c["s"][1] - c["s"][0] <= M.KNEELER_EVERY[1], f"{lid} rake {c['s']}",
                    f"{c['s'][1] - c['s'][0]} mm between stops")
    for st in w["stones"]:
        if st["kind"] == "kneeler":
            x0, x1 = span(st["outline"], 0)
            z0, z1 = span(st["outline"], 1)
            T.check("SN2", "kneelers wider than high", "a kneeler is wider than it is high", x1 - x0 > z1 - z0,
                    st["id"], f"{x1 - x0} wide, {z1 - z0} high", (lid, "stair", "stone", st["id"]))
        if st["kind"] == "topstone":
            x0, x1 = span(st["outline"], 0)
            z0, z1 = span(st["outline"], 1)
            T.check("SN2", "square topstones", "a head's topstone is square (length 0.75 to 1.33 its height)",
                    3 * (z1 - z0) <= 4 * (x1 - x0) <= 16 * (z1 - z0) // 3, st["id"], f"{x1 - x0} x {z1 - z0} mm",
                    (lid, "stair", "stone", st["id"]))
    # ---- SN2: the heads alternate
    for e in (0, 1):
        hs = sorted([st for st in w["stones"] if st["kind"] == "head" and st["id"].startswith(f"{lid}/hd-{e}/")],
                    key=lambda st: span(st["outline"], 1)[0])
        roles = []
        for st in hs:
            z0 = span(st["outline"], 1)[0]
            if not roles or roles[-1][0] != z0:
                roles.append((z0, st["role"]))
        alt = all(a[1] != b[1] for a, b in zip(roles, roles[1:]))
        T.check("SN2", "heads: ties and runners alternate", "a wall's end is a head, ties and runners alternating",
                alt, f"{lid}/hd-{e}", f"roles {[r for _, r in roles]}")
    # ---- SN2: the rake cuts
    cut = [st for st in w["stones"] if st["kind"] == "face" and any(
        p[0] != q[0] and p[1] != q[1] for p, q in zip(st["outline"], st["outline"][1:] + st["outline"][:1]))]
    if cut:
        el = min(min(edge_lengths(simplified(st["outline"]))) for st in cut)
        an = min(min(angles(simplified(st["outline"]))) for st in cut)
        T.note("SN2", "rake cuts leave trapezoids", "", f"{lid}: {len(cut)} stones cut by the rake, "
               f"{sum(1 for st in cut if len(simplified(st['outline'])) == 4)} trapezoids and "
               f"{sum(1 for st in cut if len(simplified(st['outline'])) == 5)} pentagons; their shortest edge "
               f"{el:.0f} mm, their most acute corner {an:.1f} degrees")
    for st in cut:
        pts = simplified(st["outline"])
        T.check("SN2", "rake cuts leave trapezoids", "the rake cut leaves a trapezoid: no face narrower than 50 mm, "
                "none more acute than 25 degrees", min(edge_lengths(pts)) >= M.SLIVER and min(angles(pts)) >= M.ACUTE,
                st["id"], f"edges {[round(v) for v in edge_lengths(pts)]}, corners {[round(v, 1) for v in angles(pts)]}",
                (lid, st["faces"][0], "stone", st["id"]))
    # ---- SN10 per face
    edges = set(w["edges"])
    rx = {st["id"]: st["relaxed"] for st in w["stones"] if st.get("relaxed")}
    kind = {st["id"]: st["kind"] for st in w["stones"]}
    for f in M.FACES:
        occ = [[] for _ in range(nb)]
        for st in w["stones"]:
            if f not in st["faces"]:
                continue
            if st["kind"] in course_kinds:
                x0, x1 = span(st["outline"], 0)
                for m in st["bands"]:
                    occ[m].append((x0, x1, st["id"]))
            elif st["kind"] in ("kneeler", "knee", "topstone"):
                for m in st["bands"]:
                    xa = x_at(st["outline"], (Lz[m] + Lz[m + 1]) / 2)
                    if xa:
                        occ[m].append((int(round(xa[0])), int(round(xa[1])), st["id"]))
        J = [[] for _ in range(nb)]
        pair = {}
        for m in range(nb):
            iv = sorted(occ[m])
            starts = {}
            for x0, x1, sid in iv:
                starts.setdefault(x0, []).append(sid)
            for x0, x1, sid in iv:
                for sid2 in starts.get(x1, []):
                    if sid2 != sid:
                        J[m].append((x1, sid, sid2))
                        pair[(m, x1)] = {sid, sid2}
        stones_in = [set(sid for _, _, sid in occ[m]) for m in range(nb)]
        link = {}
        for m in range(1, nb):
            lap = M.lap_of(Hc[m])
            for x, a, b in J[m]:
                for y, c, d in J[m - 1]:
                    if abs(x - y) >= lap:
                        continue
                    same = a in (c, d) or b in (c, d)
                    link.setdefault((m, x), set()).add((m - 1, y))
                    link.setdefault((m - 1, y), set()).add((m, x))
                    if same:
                        continue
                    if x == y and x in edges:
                        T.note("SN10", "laps", "", f"{lid} {f} course {m}: the 1961 edge's straight joint at {x} "
                               "(a fact, exempt)")
                        continue
                    why = sorted(set(f"{i_} {rx[i_]}" for i_ in (a, b, c, d) if rx.get(i_)))
                    T.check("SN10", "laps", "no vertical joint within 0.4 of the course height (at least 40 mm) of "
                            "one in the course below", False, f"{lid} {f} course {m} at {x}",
                            f"{abs(x - y)} mm from the joint below at {y} (lap {lap})" +
                            (f"; where the fill was relaxed: {'; '.join(why)}" if why else
                             f"; {a}, {b} over {c}, {d}"),
                            (lid, f, "lap", x, y, Lz[m - 1], Lz[m + 1]))
                    if abs(x - y) <= 12 and len({a, b, c, d}) == 4:
                        T.check("SN10", "no four-stone cross", "no four stones meeting at a point", False,
                                f"{lid} {f} course {m} at {x}", f"{a}, {b} over {c}, {d}", (lid, f, "cross", x, Lz[m]))
            T.add("SN10", "laps", "")["checked"] += len(J[m])
            T.add("SN10", "no four-stone cross", "no four stones meeting at a point")["checked"] += len(J[m])
        seen = set()
        longest_chain = 0
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
            if len(courses) > 2 and not (len(xs) == 1 and xs <= edges):
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
                T.tally = getattr(T, "tally", {})
                key_ = (cat, kind[top] if cat != "course joints" and top else "")
                T.tally[key_] = T.tally.get(key_, 0) + 1
            longest_chain = max(longest_chain, len(courses))
        T.add("SN10", "no joint through more than two courses", "no vertical joint through more than two courses")[
            "checked"] += sum(len(j) for j in J)
        T.note("SN10", "no joint through more than two courses", "", f"{lid} {f}: the longest run of joints within a "
               f"lap of each other spans {longest_chain} courses (a two-course head's side counts as two)")
        # the line of minimum trace, per panel: a crack's shortest path down the face through its vertical joints
        # and along its beds, over the panel's longest unbroken stack of courses with joints, as a ratio to its height
        for pn in w["panels"]:
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
                height = Lz[top + 1] - Lz[bot]
                ratio = min(cost.values()) / height
                if best is None or top - bot > best[1]:
                    best = (ratio, top - bot, height, bot, top)
            if best:
                T.note("SN10", "line of minimum trace", "reported per wall panel", f"{pn['id']} {f}: {best[0]:.2f} times "
                       f"the height over courses {best[3]} to {best[4]} ({best[2]} mm; 1.00 is a straight joint)")
            else:
                T.note("SN10", "line of minimum trace", "reported per wall panel", f"{pn['id']} {f}: no stack of three "
                       "courses with joints")
    # ---- SN10: the largest courses low
    for i in range(len(tops) - 1):
        mids = [z for z in Lz if tops[i] < z < tops[i + 1]]
        if mids:
            lower, upper = mids[0] - tops[i], tops[i + 1] - mids[0]
            T.check("SN10", "the largest courses low", "in each rise the lower course is the larger; over the last "
                    "step each course no larger than the one below", lower >= upper, f"{lid} rise {i}",
                    f"{lower} under {upper}")
    free = [Hc[m] for m in range(nb) if Lz[m] >= tops[-1]]
    for k in range(1, len(free)):
        T.check("SN10", "the largest courses low", "", free[k] <= free[k - 1], f"{lid} free course {k}",
                f"{free[k]} over {free[k - 1]}")


def step_tests(T, so, fl, slab, width):
    fid = so["id"]
    half, third = so["half"], so["third"]
    T.check("SN3", "ends 150 mm into the walls", "both ends go 150 mm into the walls",
            half - (width // 2 + 6) == 150, fid, f"tail {half - (width // 2 + 6)} mm")
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
        T.check("SN3", "ends 150 mm into the walls", "", xs[0][0] == -half and xs[-1][1] == half, sd["id"],
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
            T.check("SN5", "tread joints 4 to 10 mm", "joints between tread stones are 4 to 10 mm",
                    4 <= xr - x <= 10, sd["id"], f"{xr - x} mm")
            if side_prev is not None:
                T.check("SN3", "joints alternate", "the joints alternate sides", sd["side"] != side_prev, sd["id"],
                        "same side as the step below")
            side_prev = sd["side"]
            if below is not None:
                T.check("SN3", "no joint within 150 mm of the one below", "no joint within 150 mm of the joint on the "
                        "step below", abs(x - below) >= 150, sd["id"], f"{abs(x - below)} mm", (fid, "joint", sd["id"]))
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
                    T.check("SN3", "no joint within 150 mm of the one below", "", abs(x - below) >= 150,
                            f"{sd['id']} row {r['y']}", f"{abs(x - below)} mm", (fid, "joint", sd["id"]))
                T.check("SN5", "tread joints 4 to 10 mm", "", 4 <= xr - x <= 10, f"{sd['id']} row {r['y']}",
                        f"{xr - x} mm")
                if -third < x and xr < third:
                    T.note("SN3", "joint outside the middle third", "", f"{sd['id']} row {r['y']}: a rest's joint at "
                           f"{x} lies inside the middle third (two slabs of at most {slab['hi']} across {2 * half} mm "
                           "must meet within 544 mm of the centre; SN3 puts the rule on steps)")
                below = x
        if not sd.get("turn"):
            i = next(j for j, s_ in enumerate(fl["steps"]) if s_["id"] == sd["id"])
            if i < len(fl["steps"]) - 1:
                T.check("SN3", "laps 40 to 60 mm", "each step's front bears on the back of the one below, lapping 40 "
                        "to 60 mm", 40 <= sd["lap"] <= 60 and sd["y"][1] == fl["steps"][i + 1]["S"] + sd["lap"]
                        if "y" in sd else 40 <= sd["lap"] <= 60, sd["id"], f"lap {sd['lap']}")
        else:
            T.check("SN3", "laps 40 to 60 mm", "", 40 <= sd["lap"] <= 60, sd["id"], f"lap {sd['lap']}")


def counts(layout):
    """SN8's counts: stones per wall and kind, face area, and the L0 triangles at the design's per-kind rates."""
    TRI = dict(face=40, coping=120, head=120, kneeler=120, knee=120, through=120, topstone=120)
    out = dict(walls={}, steps={}, design=dict(wallStones=2700, faceM2=140, copings=150,
                                               budgets=dict(walls=110000, stairs=40000, gully=150000)))
    tw = 0
    for w in layout["walls"]:
        k = {}
        area = {f: 0 for f in ("stair", "bank")}
        tris = 0
        for st in w["stones"]:
            kk = st["kind"] if st["kind"] != "head" else f"head {st['role']}"
            k[kk] = k.get(kk, 0) + 1
            if st["kind"] == "face":
                k[f"face ({st['faces'][0]})"] = k.get(f"face ({st['faces'][0]})", 0) + 1
            for f in st["faces"]:
                area[f] += abs(area2(st["outline"]))
            tris += TRI[st["kind"]]
        out["walls"][w["id"]] = dict(kinds=dict(sorted(k.items())), total=len(w["stones"]),
                                     faceM2={f: round(a / 2e6, 2) for f, a in area.items()}, l0Tris=tris)
        tw += tris
    ts = 0
    for so in layout["steps"]:
        k = {}
        for st in so["stones"]:
            k[st["kind"]] = k.get(st["kind"], 0) + 1
        out["steps"][so["id"]] = dict(kinds=k, total=len(so["stones"]), l0Tris=300 * len(so["stones"]))
        ts += 300 * len(so["stones"])
    allw = [st for w in layout["walls"] for st in w["stones"]]
    out["totals"] = dict(wallStones=len(allw), faceStones=sum(1 for st in allw if st["kind"] == "face"),
                         copings=sum(1 for st in allw if st["kind"] == "coping"),
                         kneelers=sum(1 for st in allw if st["kind"] == "kneeler"),
                         intermediateKneelers=sum(1 for w in layout["walls"] for f_ in w["features"] if f_["mid"]),
                         knees=sum(1 for st in allw if st["kind"] == "knee"),
                         throughs=sum(1 for st in allw if st["kind"] == "through"),
                         heads=sum(1 for st in allw if st["kind"] == "head"),
                         topstones=sum(1 for st in allw if st["kind"] == "topstone"),
                         fallen=sum(1 for st in allw if st.get("fallen")),
                         faceM2=round(sum(abs(area2(st["outline"])) * len(st["faces"]) for st in allw) / 2e6, 1),
                         stepStones=sum(len(so["stones"]) for so in layout["steps"]),
                         l0TrisWalls=tw, l0TrisStairs=ts, l0TrisGully=tw + ts)
    return out


def independence(layout, facts, M):
    """Re-lay one panel at a time with a record event's seed and count the stones that change outside it."""
    res = []
    seed = facts["worldSeed"]
    for ln, w in zip(facts["walls"]["lines"], layout["walls"]):
        fl = facts["stair"]["flights"][ln["flight"]]
        so = layout["steps"][ln["flight"]]
        base = {st["id"]: st["outline"] for st in w["stones"]}
        owner = {st["id"]: st.get("panel") for st in w["stones"]}
        for pn in w["panels"]:
            w2 = M.lay_line(ln, fl, so, seed, {pn["id"]: "relaid"})
            new = {st["id"]: st["outline"] for st in w2["stones"]}
            inside = sum(1 for i in set(base) | set(new) if base.get(i) != new.get(i) and
                         (owner.get(i) == pn["id"] or i.startswith(pn["id"] + "/")))
            outside = sorted(i for i in set(base) | set(new) if base.get(i) != new.get(i) and
                             not (owner.get(i) == pn["id"] or i.startswith(pn["id"] + "/")))
            res.append(dict(panel=pn["id"], changedInside=inside, changedOutside=len(outside), outside=outside[:6]))
    return res


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
    through=(126, 186, 116), tie=(52, 128, 150), runner=(122, 182, 204), kneeler=(238, 146, 46),
    kneelermid=(250, 196, 120), knee=(168, 104, 200), topstone=(226, 196, 58), coping=(150, 150, 160),
    fallen=(25, 25, 25), cell=(150, 108, 76), ground=(214, 232, 202), groundline=(70, 120, 60), pitch=(60, 90, 220),
    fail=(225, 20, 20), relaxed=(220, 0, 200), held=(40, 90, 230), rest=(222, 206, 176), step=(200, 200, 196),
    step2=(180, 180, 176), landing=(190, 214, 230), third=(225, 20, 20), wallface=(90, 90, 90), tail=(236, 226, 214),
    hidden=(236, 230, 222))


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
        base = COL["face1961"] if pn["work"] == "1961" else COL["face"]
        v = (int(st["id"].encode().hex()[-6:], 16) % 21) - 10
        return tuple(max(0, min(255, c + v)) for c in base)
    if k == "head":
        return COL["tie"] if st["role"] == "tie" else COL["runner"]
    if k == "kneeler":
        return COL["kneelermid"] if any(f_["id"] == st["id"] and f_["mid"] for f_ in w["features"]) else COL["kneeler"]
    return COL[k]


LEGEND = [("face", "face stone"), ("face1961", "1961 panel"), ("through", "through"), ("tie", "head tie"),
          ("runner", "head runner"), ("kneeler", "kneeler"), ("kneelermid", "intermediate kneeler"), ("knee", "knee"),
          ("topstone", "topstone"), ("coping", "coping"), ("fallen", "fallen (hole)"), ("cell", "step end (occupied)"),
          ("ground", "ground (bank)"), ("hidden", "hidden below"), ("pitch", "pitch line"),
          ("relaxed", "laid without full bond"), ("fail", "test failure")]


def draw_legend(cv, x, y):
    for i, (k, label) in enumerate(LEGEND):
        xx = x + (i % 4) * 300
        yy = y + (i // 4) * 26
        cv.poly([(xx, yy), (xx + 30, yy), (xx + 30, yy + 16), (xx, yy + 16)], COL[k])
        cv.outline([(xx, yy), (xx + 30, yy), (xx + 30, yy + 16), (xx, yy + 16)], COL["outline"])
        cv.text(xx + 38, yy + 1, label, COL["ink"])


def draw_elevation(np, w, face, marks, relaxed, falls, path, scale=0.2, strip=6000):
    """One face of one wall line, unrolled: s left to right (the bank face as seen through the wall from the stair),
    z up, in strips of `strip` mm, at `scale` px a mm."""
    s0, s1 = w["s"]
    starts = list(range(s0, s1, strip))
    vis = [st for st in w["stones"] if face in st["faces"]]
    blocks = []
    for a in starts:
        b = min(a + strip, s1)
        zs = [p[1] for st in vis for p in st["outline"] if a - 200 <= p[0] <= b + 200]
        zs += [z for s, z in w["ground"] if a <= s <= b] if face == "bank" else []
        zs += [c["outline"][0][1] for c in w["cells"] if a <= c["outline"][0][0] <= b] if face == "stair" else []
        zlo, zhi = min(zs) - 150, max(zs) + 120
        blocks.append((a, b, zlo, zhi))
    M = 40
    W_ = int(strip * scale) + 2 * M + 60
    hs = [int((zhi - zlo) * scale) + 70 for a, b, zlo, zhi in blocks]
    head = 200
    cv = Canvas(W_, head + sum(hs) + 20, np)
    cv.text(M, 14, f"{w['id']}  {face} face  {'(seen through the wall from the stair)' if face == 'bank' else ''}",
            COL["ink"], 3)
    cv.text(M, 46, f"R1 elevation, integer mm, {scale} px a mm (60 mm = {int(60 * scale)} px), strips of {strip} mm; "
            "s from the flight's foot", COL["ink"])
    draw_legend(cv, M, 70)
    y = head
    for (a, b, zlo, zhi), hgt in zip(blocks, hs):
        ox = M + 50

        def P(s, z):
            return (ox + (s - a) * scale, y + 40 + (zhi - z) * scale)
        cv.text(M, y + 6, f"s {a} to {b}", COL["ink"])
        if face == "bank":
            g = [(s, z) for s, z in w["ground"] if a - 100 <= s <= b + 100]
            for (sa, za), (sb, zb) in zip(g, g[1:]):
                cv.poly([P(sa, za), P(sb, zb), P(sb, zlo), P(sa, zlo)], COL["ground"])
        for st in vis:
            xs = [p[0] for p in st["outline"]]
            if max(xs) < a - 50 or min(xs) > b + 50:
                continue
            pts = [P(p[0], p[1]) for p in st["outline"]]
            cv.poly(pts, stone_colour(st, w))
        for st in vis:
            xs = [p[0] for p in st["outline"]]
            if max(xs) < a - 50 or min(xs) > b + 50:
                continue
            pts = [P(p[0], p[1]) for p in st["outline"]]
            cv.outline(pts, COL["relaxed"] if st["id"] in relaxed else COL["outline"])
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
                    x0_, x1_ = max(0, int(round(x0_))), min(cv.w, int(round(x1_)))
                    y0_, y1_ = max(0, int(round(y0_))), min(cv.h, int(round(y1_)))
                    if x1_ > x0_ and y1_ > y0_:
                        sub = cv.img[y0_:y1_, x0_:x1_].astype("int32")
                        cv.img[y0_:y1_, x0_:x1_] = ((sub * 2 + np.array(COL["hidden"]) * 3) // 5).astype("uint8")
            for c in w["cells"]:
                xs = [p[0] for p in c["outline"]]
                if max(xs) >= a and min(xs) <= b:
                    pts = [P(max(a - 50, min(b + 50, p[0])), p[1]) for p in c["outline"]]
                    cv.poly(pts, COL["cell"])
                    cv.outline(pts, COL["outline"])
        pl = w["pitch"]
        for (pa, za), (pb, zb) in zip(pl, pl[1:]):
            cv.line(*P(pa, za), *P(pb, zb), COL["pitch"], 1, dash=6)
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
                    col = COL["held"] if "held" in fp["result"] else (COL["fail"] if "not placed" in fp["result"]
                                                                      else COL["relaxed"])
                    for r in (9, 10):
                        for t in range(0, 360, 6):
                            xx, yy = int(cx + r * math.cos(math.radians(t))), int(cy + r * math.sin(math.radians(t)))
                            if 0 <= xx < cv.w and 0 <= yy < cv.h:
                                cv.img[yy, xx] = col
        # metre ticks
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
            cv.text(M - 30, yy - 7, str(z), COL["ink"])
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
    M = 40
    head = 200
    H_ = head + int(max(y for _, _, y in cols) * scale) + 80
    cv = Canvas(max(1560, M * 2 + colw * len(cols) + 200), H_, np)
    cv.text(M, 14, "R1 steps in plan  st-gully", COL["ink"], 3)
    cv.text(M, 46, f"integer mm, {scale} px a mm; x across (right of uphill +), y up the flight;", COL["ink"])
    cv.text(M, 66, "the walking line's middle third red (dashed), the walls' faces grey, joints black", COL["ink"])
    for i, (k, label) in enumerate([("step", "step stone"), ("rest", "rest slab"), ("landing", "turn landing"),
                                    ("tail", "tail inside the wall"), ("fail", "test failure")]):
        xx, yy = M + i * 300, 96
        cv.poly([(xx, yy), (xx + 30, yy), (xx + 30, yy + 16), (xx, yy + 16)], COL[k])
        cv.text(xx + 38, yy + 1, label, COL["ink"])
    for ci, (so, fl, ymax) in enumerate(cols):
        ox = M + 80 + ci * (colw + 60) + int(400 * scale)
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


# ---------------------------------------------------------------------------------------------------------------
# The run

def main(argv):
    import numpy as np
    import hashes as HX
    import masonry as M
    from naming import Grammar
    facts = json.load(open(FACTS))
    first = M.lay(facts)
    again = M.lay(facts)
    h1, h2 = HX.hash_hex(first), HX.hash_hex(again)
    layout = first
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "layout.json"), "w") as fh:
        json.dump(layout, fh, sort_keys=True, separators=(",", ":"))
    T = Tests()
    g = Grammar.load()
    ids = [st["id"] for w in layout["walls"] for st in w["stones"]] + [st["id"] for so in layout["steps"]
                                                                        for st in so["stones"]]
    for i in ids:
        T.check("ids", "ids follow the grammar", "every id is a slot by schemas/naming.md", g.match("slot", i), i,
                "not a slot")
    T.check("ids", "ids are unique", "no two stones share an id", len(ids) == len(set(ids)), "all",
            f"{len(ids) - len(set(ids))} repeated")
    slab = facts["sources"]["stepStone"]
    for so, fl in zip(layout["steps"], facts["stair"]["flights"]):
        step_tests(T, so, fl, slab, fl["width"])
    for w in layout["walls"]:
        fl = next(f for f in facts["stair"]["flights"] if f["id"] == w["flight"])
        wall_tests(T, w, fl, M)
    C = counts(layout)
    ind = independence(layout, facts, M)
    # the sheet
    sheet = []
    for w in layout["walls"]:
        relaxed = set()
        for fr in w["report"]["fills"]:
            for st in w["stones"]:
                if st["kind"] == "face" and st["faces"][0] == fr["face"] and fr["course"] in st["bands"] and \
                        fr["a"] <= span(st["outline"], 0)[0] < fr["b"]:
                    relaxed.add(st["id"])
        for f in M.FACES:
            mk = [m_[2:] for m_ in T.marks.get(w["id"], [])] if False else []
            for key, lst in T.marks.items():
                if key == w["id"]:
                    for m_ in lst:
                        if m_[0] == f:
                            mk.append(m_[1:])
            name = f"{w['id'].split('/', 1)[1].replace('/', '-')}-{f}.png"
            draw_elevation(np, w, f, mk, relaxed, w["report"]["falls"], os.path.join(OUT, name))
            sheet.append(name)
    smk = []
    for so in layout["steps"]:
        smk += [m_ for m_ in T.marks.get(so["id"], [])]
    draw_steps(np, layout, facts, smk, os.path.join(OUT, "steps-plan.png"))
    sheet.append("steps-plan.png")
    write_report(layout, facts, T, C, ind, h1, h2, sheet)
    fails = sum(len(t["fails"]) for t in T.t.values())
    print("layout hash", h1, "again", h2, "stable" if h1 == h2 else "UNSTABLE")
    print("tests", len(T.t), "failures", fails)
    for (sn, name), t in sorted(T.t.items()):
        print(f"  {sn:5s} {name:48s} checked {t['checked']:6d}  failed {len(t['fails']):5d}")
    print("sheet", ", ".join(sheet))


def write_report(layout, facts, T, C, ind, h1, h2, sheet):
    L = []
    a = L.append
    a("# R1: the gully's walls and steps as elevations")
    a("")
    a("Port step 2b, rung R1 (`reviews/lt1/port/2b/design.md`, The ladder). The cheek walls and the steps laid in "
      "integer millimetres by `blender/generators/masonry.py`, from `r1/facts.json`, checked and drawn by "
      "`tools/r1_elevations.py`. Numbers and faults only; no judgement of the look.")
    a("")
    t0 = C["totals"]
    a("## Not done; next round")
    a("")
    a("Stopped here for usage (the coordinator, 22 October). The design changed at e84862e after this run was built: "
      "dry lane walls carry no raked coping, so SN2 now has a retaining wall with no coping (the bank over a level top "
      "course) and a parapet with level slab copings stepped square, a whole course a step, nothing cut to a rake.")
    a("")
    a("- **Stepped tops** replace this run's kneelers, knees, intermediate kneelers and raked copings (and the rake "
      "cuts under them); `masonry.py`'s `_coping` and the SN2 rake tests are to be redone, not finished.")
    a(f"- **The stone count:** {t0['wallStones']:,} wall stones ({t0['faceStones']:,} face) against the design's "
      f"about 2,700; L0 {t0['l0TrisGully']:,} triangles against 150,000 (walls {t0['l0TrisWalls']:,} against 110,000). "
      "Why: every rise (146 to 188 mm) is over the 140 mm course, so two courses a rise, median 83 mm; stones of 180 mm "
      "to 4.5 times that height are short; and both faces are laid stone by stone (the bank face alone is about 60% "
      "of the face stones, the walls' faces 212 m2 against 140).")
    a(f"- **Lap failures:** {len(T.t.get(('SN10', 'laps'), dict(fails=[]))['fails'])} laps and "
      f"{len(T.t.get(('SN10', 'no four-stone cross'), dict(fails=[]))['fails'])} four-stone crosses, all at the free "
      "lengths the fill relaxed (short runs in thin courses; What fails, 2).")
    a("")
    a("## In short")
    a("")
    fails = {k: t for k, t in T.t.items() if t["fails"]}
    a(f"- **Hash:** `{h1}` (laid twice in one run: {'the same' if h1 == h2 else 'DIFFERENT: ' + h2}); the run is "
      "repeated in a second process to show it holds.")
    a(f"- **Tests:** {len(T.t)} checks; {len(T.t) - len(fails)} pass, {len(fails)} fail "
      f"({sum(len(t['fails']) for t in fails.values())} failures in all). The failures, each with its cause, are "
      "under Tests.")
    t_ = C["totals"]
    a(f"- **Counts (SN8):** {t_['wallStones']} wall stones ({t_['faceStones']} face stones, {t_['copings']} copings, "
      f"{t_['kneelers']} kneelers of which {t_['intermediateKneelers']} intermediate, {t_['knees']} knees, "
      f"{t_['throughs']} throughs, {t_['heads']} head stones, {t_['topstones']} topstones), {t_['faceM2']} m2 of face "
      f"on both faces, {t_['stepStones']} step stones and slabs. L0 at the design's rates: walls {t_['l0TrisWalls']:,} "
      f"triangles against 110,000, stairs {t_['l0TrisStairs']:,} against 40,000, the gully {t_['l0TrisGully']:,} "
      "against 150,000.")
    worst = max(ind, key=lambda r: r["changedOutside"])
    tl = getattr(T, "tally", {})
    if tl:
        a("- **Joints through more than two courses, by cause:** " + "; ".join(
            f"{v} {c}{' (' + k + ')' if k else ''}" for (c, k), v in sorted(tl.items(), key=lambda kv: -kv[1])) + ".")
    a(f"- **Panels re-lay alone:** {sum(1 for r in ind if r['changedOutside'] == 0)} of {len(ind)} panels re-laid with "
      f"an event's seed change no stone outside themselves; the worst changes {worst['changedOutside']} "
      f"({worst['panel']}).")
    a("")
    a("## Tests")
    a("")
    a("| Rule | Check | Checked | Failed |")
    a("| --- | --- | --- | --- |")
    for (sn, name), t in sorted(T.t.items()):
        a(f"| {sn} | {name} | {t['checked']} | {len(t['fails'])} |")
    a("")
    for (sn, name), t in sorted(T.t.items()):
        if not t["fails"] and not t["notes"]:
            continue
        a(f"**{sn}, {name}.** {t['rule']}")
        a("")
        for fl_ in t["fails"][:25]:
            a(f"- FAIL {fl_['where']}: {fl_['what']}")
        if len(t["fails"]) > 25:
            a(f"- ... and {len(t['fails']) - 25} more (all in `layout.json`'s checks)")
        notes = t["notes"]
        for n in notes[:40]:
            a(f"- {n}")
        if len(notes) > 40:
            a(f"- ... and {len(notes) - 40} more notes")
        a("")
    a("## Counts (SN8)")
    a("")
    a("| Wall line | Stones | By kind | Face m2 (stair, bank) | L0 triangles |")
    a("| --- | --- | --- | --- | --- |")
    for wid, c in C["walls"].items():
        kinds = ", ".join(f"{k} {v}" for k, v in c["kinds"].items())
        a(f"| {wid} | {c['total']} | {kinds} | {c['faceM2']['stair']}, {c['faceM2']['bank']} | {c['l0Tris']:,} |")
    for sid, c in C["steps"].items():
        a(f"| {sid} (steps) | {c['total']} | {', '.join(f'{k} {v}' for k, v in c['kinds'].items())} | | "
          f"{c['l0Tris']:,} |")
    a("")
    a(f"The design's estimate was about {C['design']['wallStones']:,} wall stones, {C['design']['faceM2']} m2 of face "
      f"and {C['design']['copings']} copings.")
    a("")
    a("## The laying's own reports")
    a("")
    for w in layout["walls"]:
        r = w["report"]
        a(f"**{w['id']}.**")
        for fp in r["falls"]:
            a(f"- fall at s {fp['s']}, z {fp['z']}: {fp['result']}")
        hows = {}
        for fr in r["fills"]:
            hows[fr["how"]] = hows.get(fr["how"], 0) + 1
        if hows:
            a(f"- free lengths laid without the full rule: {', '.join(f'{v} {k}' for k, v in sorted(hows.items()))}")
        if r["throughs"]:
            a(f"- through stones not placed: {len(r['throughs'])} ({', '.join(str(x['at']) for x in r['throughs'])})")
        if r["cuts"]:
            a(f"- boundaries that took no tooth or straight joint in a course: {len(r['cuts'])}")
        for fl_ in r["flags"]:
            a(f"- {fl_}")
        a("")
    a("## Panels re-laid one at a time")
    a("")
    for r in ind:
        if r["changedOutside"]:
            a(f"- {r['panel']}: {r['changedInside']} of its stones change and {r['changedOutside']} outside it "
              f"(e.g. {', '.join(r['outside'][:3])})")
    a(f"- the others ({sum(1 for r in ind if r['changedOutside'] == 0)}) change only their own stones")
    a("")
    a("## The sheet")
    a("")
    for s in sheet:
        a(f"- `{s}`")
    a("")
    findings(a, layout, facts, T, C, ind)
    with open(os.path.join(OUT, "report.md"), "w") as fh:
        fh.write("\n".join(L) + "\n")


def findings(a, layout, facts, T, C, ind):
    """What fails and why, what is undecided and why, and what was assumed: the numbers from this run."""
    walls, steps = layout["walls"], layout["steps"]
    fills = [dict(fr, line=w["id"]) for w in walls for fr in w["report"]["fills"] if "long-and-short" not in fr["how"]]
    lens = [fr["b"] - fr["a"] for fr in fills]
    hs = [fr["h"] for fr in fills]
    rises = [b - a for fl in facts["stair"]["flights"]
             for a, b in zip([fl["zFoot"]] + [s_["zTop"] for s_ in fl["steps"]], [s_["zTop"] for s_ in fl["steps"]])]
    under, free = [], []
    for w in walls:
        fl = next(f for f in facts["stair"]["flights"] if f["id"] == w["flight"])
        Lz = [l_["z"] for l_ in w["lines"]]
        for z0, z1 in zip(Lz, Lz[1:]):
            (under if z0 < fl["steps"][-1]["zTop"] else free).append(z1 - z0)
    slab = facts["sources"]["stepStone"]
    half, third = steps[0]["half"], steps[0]["third"]
    win = slab["hi"] - half - third
    tops = [st for w in walls for st in w["stones"] if st["kind"] == "topstone"]
    tl = getattr(T, "tally", {})
    n_top = sum(v for (c, k), v in tl.items() if k == "topstone")
    laps = T.t.get(("SN10", "laps"), dict(fails=[]))["fails"]
    crosses = T.t.get(("SN10", "no four-stone cross"), dict(fails=[]))["fails"]
    leaks = [r for r in ind if r["changedOutside"]]
    t_ = C["totals"]
    a("## What fails, and why")
    a("")
    a(f"1. **Thin courses, the root of most of what follows.** Every rise is {min(rises)} to {max(rises)} mm, over "
      f"wall.py's 140 mm course, so SN2's lines (one on each step top, at most one between) give two courses a rise: "
      f"courses under the last step are {min(under)} to {max(under)} mm (median {sorted(under)[len(under) // 2]}), "
      f"the free courses above it {min(free)} to {max(free)} mm, falling upwards (the largest courses low). A stone "
      f"is 180 mm to 4.5 times its height, so most are short: {t_['faceStones']:,} face stones against the design's "
      f"about {C['design']['wallStones']:,}, and the walls' L0 is {t_['l0TrisWalls']:,} triangles against SN8's "
      f"110,000 (the gully {t_['l0TrisGully']:,} against 150,000). Undecided, not mine to decide: a course up to "
      "the largest rise (one course a rise, about a third of the stones), or the count kept and SN8's rates or "
      "budget changed.")
    a(f"2. **SN10 laps ({len(laps)}) and four-stone crosses ({len(crosses)}), and {sum(v for (c, k), v in tl.items() if c == 'course joints')} "
      f"joints through three courses**, all at the {len(fills)} free lengths the fill could not lay in whole stones "
      "clear of the joints below and above, so laid with less of the rule (marked magenta on the sheet; each is "
      "listed under The laying's own reports). They are runs of "
      f"{min(lens)} to {max(lens)} mm in courses {min(hs)} to {max(hs)} mm high, between a panel's tooth, a step "
      "end, a stone laid first or the rake: one or two joints fit at all, and the course below has a joint there. "
      "The teeth are chosen before the fill, from the boundary alone, so that a panel re-lays alone; choosing them "
      "from the fill below would couple panels. Larger courses (1) would remove most of these.")
    a(f"3. **SN10 joints through more than two courses at the wall ends' topstones ({n_top}).** SN2's square topstone "
      f"(220 to 450 mm, length 0.75 to 1.33 its height) at a flight's top end stands in the free courses of 60 to "
      f"about 80 mm, so its plumb side passes through three courses or more ({', '.join(sorted(set(str(span(st['outline'], 1)[1] - span(st['outline'], 1)[0]) for st in tops)))} mm high). "
      "At wl-gully/fl-1/l the knee's level top (at most 350 mm, my own range) leaves the topstone too long to be "
      "square on the knee's bed, so its bed drops a further three courses. Undecided: a smaller topstone, larger "
      "free courses, or a topstone's side read as one stone's side rather than a joint through courses.")
    a(f"4. **Panels re-laid alone: {len(ind) - len(leaks)} of {len(ind)}.** The other {len(leaks)} change "
      f"{min(r['changedOutside'] for r in leaks)} to {max(r['changedOutside'] for r in leaks)} stones beyond "
      "themselves, nearly all in courses where a boundary took no tooth (the reports' 'boundaries that took no tooth': "
      f"{sum(len(w['report']['cuts']) for w in walls)} course crossings in all), so one stone crosses it and is laid by "
      "the panel holding its middle; one or two follow a fallen stone redrawn near a boundary.")
    a(f"5. **Steps: L0 {t_['l0TrisStairs']:,} triangles against 40,000** ({t_['stepStones']} stones and slabs at 300). "
      "Every step test passes, but SN3's middle third leaves almost no room: with the finish's longest slab "
      f"({slab['hi']} mm) across {2 * half} mm, a step's joint can only fall {third} to {third + win} mm from the "
      f"centre ({win + 1} mm of play). A rest's two slabs must meet within {slab['hi'] - half} mm of the "
      "centre, so every rest joint is inside the middle third (SN3 puts the rule on steps; reported as notes). "
      "The plan names two slabs a rest; fl-1's rests are deeper than the longest slab and take four in two rows.")
    a("")
    a("## Assumed, and not laid at R1")
    a("")
    a("- **Seeds:** every new draw keys on the pack's world seed (1989) through `HS.Stream`/`HS.h`. The stair's plan is "
      "today's set-out from the record's kind at its legacySeed (1) and wall.py's own fact draws (the 1961 panel, "
      "the fall points and which are held by cement) are at its seed 1: R1 must be re-run when 2b retires "
      "legacySeed and when those facts move into a wl-gully record.")
    a("- **Rounding:** the stages' metres were rounded once to integer mm in `facts.json` (half away from zero) and "
      "nowhere after. The plan's S and D were rounded apart and differ by 1 mm in places; a step's depth is taken "
      "from the nosings (S), so each lap is exactly its drawn lap.")
    a(f"- **Steps:** laps 40 to 60 mm by SN3 (the kind's own lap is 100 mm); the middle third on the clear width "
      f"between the walls' faces with their 6 mm joints ({2 * (half - 150)} mm, so |x| at least {third}); ends "
      f"{half} mm from the centre (150 mm into each wall); the turn landing at fl-1's foot one rise thick, from the "
      "landing's front to the first step's nosing plus its lap.")
    a("- **Kneelers:** 'wider than high' is taken on the whole stone, bed to top; a kneeler's height is drawn near "
      "three quarters of its width, its plumb back through at most two courses where the lines allow; intermediate "
      "kneelers every 2.4 to 3.6 m of going (fl-1's raked runs are all under 2.4 m, so only fl-0 has them).")
    a("- **Not laid at R1:** the coping's rebates (a 3D matter, R2); the patched holes; the 1952 campaign's reset "
      "run (the plan's output does not say which steps it moved, so it is untested); the wall's hidden work under "
      "the step ends and under the stair's surface (veiled on the sheet); the batter (in the face alone, a 3D "
      "matter).")
    flags = [f_ for w in walls for f_ in w["report"]["flags"]] + [f_ for so in steps for f_ in so["flags"]]
    if flags:
        a("- **The laying's flags:** " + "; ".join(flags) + ".")


if __name__ == "__main__":
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
    if argv and argv[0] == "ground":
        blender_ground(argv[1])
    elif argv and argv[0] == "facts":
        gather_facts()
    else:
        main(argv)
