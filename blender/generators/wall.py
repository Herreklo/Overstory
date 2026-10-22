"""Dry-stone walls, laid from their facts (docs/stone.md; docs/upkeep.md; the board: 09, 10, 11, 03): courses of thin
flat stones of the town's slaty rock along a wall's line, every joint bridged, the face battered back about one in
six, slab copings on top, and behind the stones the soil and moss a dry wall holds, so its joints read dark and green,
never as open voids. A wall retains the bank where the ground beside a lane stands well over the lane's grade, and
stands as a parapet where it does not; a parapet's coping runs at hand height over the stair's pitch line, raked over
each run and level over each landing, and its courses follow the stair under it. Its history is its own: built with
the lane, kept by the town, a bulged panel rebuilt by a crew in depot stone with cement pointing, and between
campaigns a face stone fallen here and there and left, its hearting showing in the hole, a hole patched.

The first: the gully steps' cheek walls, along both sides of each flight.

    blender -b --factory-startup --python blender/generators/wall.py -- gully_cheeks [unity project dir]

Writes unity/Assets/Art/Stone/<name>.fbx and <name>.json. The per-vertex channels are the stone's (stone.py): UV0
grain, UV1 (years bare / 200, seed), UV2 (kind, variation), UV3 bake (sky, ground), UV4 (polish, lichen years / 200),
UV5 (moss, water held).
"""

import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "parts", "stone", "slate"))
sys.path.insert(0, os.path.join(HERE, "..", "blockouts"))
sys.path.insert(0, os.path.join(HERE, "..", "resolver"))
import hashing as HS  # noqa: E402  (the one hash spec)
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
    "gully_cheeks": dict(id="wl-gully", lane="Gully Steps", stone="slate", built=1874, footfall=ST.FLIGHTS["gully"]["footfall"],
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
PARAPET = 0.9           # a parapet's top over the stair's pitch line, plumb: a handrail's height
FOOT = 0.18             # the wall's foot under the steps' line
RETAINS = 0.5           # a wall retains where the bank behind it stands this far over the lane's grade
STRETCH = 2.0           # a wall keeps one role for at least this length
BACKING = 0.035         # the soil and moss behind the joints, behind the face (cement pointing: 0.012)
HEARTING = (0.0, 0.02)  # where a face stone has fallen, the loose packing behind it has run out into its socket: how far
REPOSE = 0.75           # back from the face the lowest of it lies (at the lip it fell over), and how much further back
                        # for each metre up (it stands at about 53 degrees, as loose stone does), so the hole shows its
                        # rubble, never a void
SHEDS = 0.06            # a socket's floor raked steeper than this (the course's pitch) sheds water; only a level one
                        # holds it
SOCKET = 0.21           # the back of a fallen stone's socket, behind its hearting
HEAD_LEN = (0.32, 0.62) # a wall's head (its end) is built of its longest stones, laid through it or as far in as they go
EASE = 0.6              # a wall's courses ease from one pitch to the next over about this much either side of the change
LONG_SHORT = ((0.42, 0.58), (0.2, 0.27))   # a rebuilt panel's end stones, long and short in alternate courses


def recess(d):
    """The bake (sky, ground) of a point d metres into a hole in the face: of the sky, from the face's own at the lip
    to none at the socket's back, the floor stone.py gives a bed no sky reaches (0.35); of the ground and the hole's
    own lit beds, more the deeper it lies (stone.py's hidden bed, 0.6). A hole is shadowed, never a void."""
    f = np.clip(np.asarray(d, float) / SOCKET, 0.0, 1.0)
    return 0.7 - 0.35 * f, 0.3 + 0.3 * f


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


def pitch_line(sp, z0):
    """The stair's pitch line, the line of its nosings, as breaks (s, z) for np.interp: through each step's nosing (its
    front, at its tread's height), level across each landing from its step's nosing to a going short of the next, a
    going below the first nosing at the foot's height, and level beyond both ends. A cheek wall's coping and courses
    follow it, as a handrail does."""
    n, r, g, S = sp["n"], sp["r"], sp["g"], sp["S"]
    P = [(S[0] - g, z0)]
    for i in range(n):
        P.append((S[i], z0 + (i + 1) * r))
        if i < n - 1 and S[i + 1] - S[i] > g + 1e-6:
            P.append((S[i + 1] - g, z0 + (i + 1) * r))
    P = np.array(P, float)
    # (only its changes of pitch: a nosing in a straight run is no break)
    k = np.diff(P[:, 1]) / np.diff(P[:, 0])
    keep = np.concatenate([[True], np.abs(np.diff(k)) > 1e-6, [True]])
    return P[keep]


def eased(PL, lo, hi, ease=EASE):
    """The pitch line's breaks within [lo, hi] (a wall's length) eased, as a mason eases a wall's courses from the rake
    to the level and back over a few stones: each change of pitch rounded by a parabola over `ease` either side, less
    where the next change or the wall's end is nearer. A course never bends at a point, so no joint runs straight up
    the wall and its battered face turns smoothly there (bent at the breaks, the face creased and every course broke
    at the same place: the wall read as jogging out at a landing, and a landing's level courses as a stack). The
    coping, straight slabs, still turns at the breaks. Returns f(s), the eased line's height, for scalars and arrays."""
    q, z = PL[:, 0], PL[:, 1]
    k = np.concatenate([[0.0], np.diff(z) / np.diff(q), [0.0]])       # (level beyond both ends, as np.interp is)
    blends = []
    for i in range(len(q)):
        dk = k[i + 1] - k[i]
        if not lo < q[i] < hi or abs(dk) < 1e-9:
            continue
        w = min(ease, q[i] - lo, hi - q[i],
                (q[i] - q[i - 1]) / 2 if i > 0 else ease, (q[i + 1] - q[i]) / 2 if i < len(q) - 1 else ease)
        if w >= 0.05:
            blends.append((float(q[i]), float(dk), float(w)))

    def f(s):
        s = np.asarray(s, float)
        out = np.interp(s, q, z)
        for qb, dk, w in blends:
            out = out + dk * (np.clip(s - qb + w, 0.0, 2.0 * w) ** 2 / (4.0 * w) - np.clip(s - qb, 0.0, w))
        return out
    return f


def stretches(s, flags, least=STRETCH):
    """A wall keeps one role along a stretch of at least `least` metres: a shorter run of samples takes its
    neighbours' role, the shortest first. Each sample stands for the length halfway to its neighbours."""
    f = np.asarray(flags, bool).copy()
    s = np.asarray(s, float)
    edges = np.concatenate([[s[0]], (s[1:] + s[:-1]) / 2, [s[-1]]])
    while True:
        cuts = np.flatnonzero(f[1:] != f[:-1]) + 1
        starts, ends = np.concatenate([[0], cuts]), np.concatenate([cuts, [len(f)]])
        if len(starts) < 2:
            return f
        lens = edges[ends] - edges[starts]
        i = int(np.argmin(lens))
        if lens[i] >= least:
            return f
        f[starts[i]:ends[i]] = not f[starts[i]]


def minus(lo, hi, cut):
    """[lo, hi] less the intervals in cut."""
    out = [(lo, hi)]
    for c0, c1 in cut:
        out = [p for a_, b_ in out for p in ((a_, min(b_, c0)), (max(a_, c1), b_)) if p[1] - p[0] > 1e-6]
    return out


def facing(P, n):
    """A quad or triangle's corners (s, t, z) in the order whose face looks along n (s, t, z); (t, s, z) is the
    right-handed order of the flight's frame."""
    Q = P[:, [1, 0, 2]]
    return P if np.cross(Q[1] - Q[0], Q[2] - Q[0]) @ np.asarray(n, float)[[1, 0, 2]] > 0 else P[::-1].copy()


def lay(spec, seed=1):
    """Seeds (docs/building-blocks.md, Seeds and determinism): every draw is keyed on the world seed, the stable id of
    what it is for and its purpose (blender/resolver/hashing.py), never a position. The ids (schemas/naming.md, the
    wall's slots): the wall is its record (wl-<token>); a panel is the length beside one flight on one side,
    <wall>/fl-<n>/<l|r>; a course co-<k> from the foot; a stone's place sp-<j>, its span's ordinal along its course,
    <panel>/co-<k>/sp-<j>; the hearting seen where it has fallen, <stone>/ht-<m>; the backing's cells bk-<j>-<0|1>; the
    copings cp-<c>. (Renaming an id re-seeds what it names.)"""
    import heart_layout as H
    wid = spec.get("id") or "wl-" + ST.slug(spec["lane"]).replace("_", "-")
    lane = next(l for l in H.LANES if l["name"] == spec["lane"])
    fl = ST.flights_of(lane)
    origin = fl[0]["a"].copy()
    fell = spec["upkeep"][-1]["since"]     # stones fall and are left under the keeper whose care lets them
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
        slope = rise / run
        ground = ground_near(f)
        out = dict(V=[], F=[], COL=[], UV0=[], UV1=[], UV2=[], UV3=[])

        def put(P, kind, uv, rng, bare_y, bed_y, exposed, damp, sky, flip, water=None, touch=None, ground=None):
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
            # (bare_y and bed_y a number, or one a vertex where a piece spans old work and new: the backing)
            out["UV1"].append(np.stack([np.broadcast_to(np.asarray(bare_y, float) / 200.0, (len(P),)),
                                        np.full(len(P), var)], -1))
            # the water layer: how much water lies or runs here (see the copings and the courses below)
            out["UV2"].append(np.stack([kind.astype(float), np.clip(water if water is not None else np.full(len(P), 0.2), 0, 1)], -1))
            out["UV3"].append(np.stack([sky, np.full(len(P), 0.3) if ground is None else ground], -1))

        # the stair beside the walls, as the stair sets it out (stone.py's step_plan)
        sp = ST.step_plan(f, ST.FLIGHTS["gully"] if spec["lane"] == "Gully Steps" else spec, fi, seed)
        S_arr = np.array(sp["S"])

        def step_top(s):
            """The top of the step whose tread is at s along the flight (the same set-out as the stair)."""
            k = np.searchsorted(S_arr, np.asarray(s), side="right")
            return a[2] + np.clip(k, 0, sp["n"]) * sp["r"]

        PL = pitch_line(sp, float(a[2]))

        def pitch(s):
            return np.interp(s, PL[:, 0], PL[:, 1])

        courses_line = eased(PL, -0.3, run + 0.3)

        def base(s):
            """The wall's foot, under the steps' line: its courses run parallel to the pitch line, raked over each run
            of steps and level over each landing, eased from one pitch to the next (eased()); its face is battered
            from it."""
            return courses_line(s) - sp["r"] - FOOT

        bends = [float(q) for q in PL[:, 0] if -0.3 < q < run + 0.3]

        # (one panel was rebuilt, on the side whose bank stands highest: the water ran behind that wall)
        rise_of = {sd: np.mean([ground(*(a[:2] + up * s_ + right * sd * (W / 2 + 2.5))) - (a[2] + s_ * slope)
                                for s_ in np.linspace(0, run, 6)]) for sd in (1, -1)}
        bank_side = max(rise_of, key=rise_of.get)
        for side in (1, -1):
            pnl = f"{wid}/fl-{fi}/{'r' if side > 0 else 'l'}"
            # the line along the wall, its samples and the pitch line's breaks
            ss = np.unique(np.concatenate([np.linspace(-0.3, run + 0.3, max(8, int(run / 0.5))), bends]))
            # (the ground just behind the wall, where it stands: a retaining wall holds what is there; until the
            # corner's own ground is built the clay is that ground)
            bank = np.array([ground(*(a[:2] + up * s + right * side * (W / 2 + 0.7))) for s in ss])

            def bank_at(s):
                return np.interp(s, ss, bank)

            # its role is the ground's: it retains where the bank stands well over the lane's grade, along stretches
            # of a few metres, and stands as a parapet elsewhere
            grade = a[2] + np.clip(ss, 0.0, run) * slope
            retain = stretches(ss, bank > grade + RETAINS)
            # its height from the steps, never under the bank: a parapet at hand height over the pitch line
            top_line = np.maximum(np.where(retain, np.minimum(bank + 0.05, step_top(ss) + 3.0), pitch(ss) + PARAPET),
                                  bank + 0.05)
            # the rebuilt panel: where the lane's water ran behind the lower wall on the bank's side. The crew took
            # the bulged length down and built it again in cement, its ends stopped against the old dry work in a
            # straight joint (mortared work is not toothed into loose dry work), each end's stones long and short in
            # alternate courses, and its copings relaid
            panel = None
            for w in spec["works"]:
                if w["kind"] == "rebuilt" and side == bank_side and fi == 0:
                    prng = HS.Stream(seed, pnl, "rebuilt", w["year"])
                    L_ = prng.uniform(*w["length"])
                    s0 = prng.uniform(0.15, 0.35) * run
                    panel = dict(s=(s0, s0 + L_), year=w["year"], mortar=w["mortar"])
                    record.append(dict(flight=fi, side=side, rebuilt=[round(s0, 2), round(s0 + L_, 2)], year=w["year"]))
            ends_p = list(panel["s"]) if panel is not None else []
            # the copings' layout first: they are the top, and a change of pitch falls at a joint between two (the
            # coping before it is cut to it, or runs on to it), as does a rebuilt panel's end; their joints and low
            # ends are where the water off the top runs down the face
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
                """The wall's top: the copings' upper face, straight along each coping."""
                return np.interp(s, jts, top_j)

            ln = dict(flight=fi, side=side, a=[float(v) for v in a], up=[float(v) for v in up], width=float(W),
                      s=[round(float(v), 3) for v in ss], top=[round(float(v), 3) for v in top(ss)],
                      retain=[bool(v) for v in retain])
            lines.append(ln)
            # (water off the copings drips at their joints and at a few low points along their fronts)
            drip_list = WT.drips([e_c for _, e_c in copes[:-1]], [crng0.uniform(0.4, 1.0) for _ in copes[:-1]]) + \
                WT.drips([crng0.uniform(-0.3, run + 0.3) for _ in range(int(run / 1.5) + 1)],
                         [crng0.uniform(0.2, 0.6) for _ in range(int(run / 1.5) + 1)])
            # patchwork between: a face stone fallen here and there and left (care falling), one hole patched in
            # cement. Each fall is a place along the panel and a height up it, the upper courses likelier (the
            # stones there bear least weight)
            wrng = HS.Stream(seed, pnl, "patchwork")
            fallen = [wrng.uniform(0.0, run) for _ in range(wrng.randint(1, 3))]
            patched = wrng.uniform(0.0, run)
            fall_h = [1.0 - wrng.random() ** 2 for _ in fallen]

            def cemented(sm):
                return (panel is not None and panel["s"][0] <= sm <= panel["s"][1]) or abs(sm - patched) < 0.35

            # a fall point's height above the foot: from a little over the pitch line (the lowest courses, held by
            # the weight above, stay) to under the coping's bed
            falls = []
            for fs, fz in zip(fallen, fall_h):
                lo, hi = 0.3 + sp["r"], float(top(fs) - base(fs)) - 0.12
                if hi > lo:
                    falls.append((fs, lo + fz * (hi - lo)))

            # how much people lean on this wall: a parapet at hand height beside a steep flight is the stair's
            # handrail
            use = float(np.clip(slope * 1.6, 0.3, 1.0)) * (spec.get("footfall", 50000) / 50000.0) ** 0.5

            def face_water(sv, zv):
                """Water down a wall's face (water.py): streaks under the copings' drips, the splash at its foot."""
                return WT.down_face(sv, top(sv) - zv, zv - base(sv), drip_list)

            def h_over(s0_, s1_, ground_):
                """How far a band's top (its height over the foot, per s) stands over a ground along [s0_, s1_]."""
                q = np.linspace(s0_, s1_, 5)
                return q, base(q) - ground_(q)

            # the courses, from the foot: where a parapet's far side stands over a bank lower than the foot, the
            # wall goes down to it
            Hs = top(ss) - base(ss)
            free = ~retain
            z = min(0.0, float(np.min(bank[free] - base(ss)[free])) - 0.08) if free.any() else 0.0
            below, lost_below = [], []
            holes = []
            heads = {0: [], 1: []}       # the courses that reach each end of the panel (0 its foot, 1 its far end)
            k = 0
            while True:
                cid = f"{pnl}/co-{k}"
                krng = HS.Stream(seed, cid, "course")       # the course's height and its stones' lengths, in order
                ch = krng.uniform(*COURSE)
                # the joints this course must take, and the stone that starts at each: a rebuilt panel's straight
                # joints with the old work, its first and last stones long and short in alternate courses (the long at
                # one end over the short at the other, so each end's joints are bridged course by course)
                cuts = []
                if panel is not None:
                    long_, short_ = krng.uniform(*LONG_SHORT[0]), krng.uniform(*LONG_SHORT[1])
                    first, last = (long_, short_) if k % 2 == 0 else (short_, long_)
                    cuts = [(panel["s"][0], first), (panel["s"][1] - last, last), (panel["s"][1], None)]
                s_cur = -0.3
                joints, lost = [], []
                j = 0
                while s_cur < run + 0.3:
                    stid = f"{cid}/sp-{j}"
                    j += 1
                    for _ in range(20):
                        L_ = krng.uniform(*STONE_LEN)
                        e = s_cur + L_
                        if all(abs(e - jb) > BRIDGE for jb in below) or e > run + 0.3:
                            break
                    at = next((Lc for q, Lc in cuts if Lc is not None and abs(s_cur - q) < 1e-9), None)
                    if at is not None:
                        e = s_cur + at
                    # a joint the course must take: the stone before it is cut to it, or runs on to it (a change of
                    # pitch takes none: the courses ease through it)
                    nb = next((q for q, _ in cuts if s_cur + 0.15 <= q < e + 0.15), None)
                    if nb is not None:
                        e = nb
                    e = min(e, run + 0.3)
                    sm = (s_cur + e) / 2
                    b0, b1 = float(base(s_cur)), float(base(e))
                    bm, kb = (b0 + b1) / 2, (b1 - b0) / (e - s_cur)
                    hmin = min(float(top(q) - base(q)) for q in (s_cur, sm, e))
                    if z + ch * 0.5 > hmin - 0.08:        # (the coping takes over)
                        s_cur = e
                        continue
                    joints.append(e)
                    # what of it shows: its face over the treads beside it (below them the stair hides it), its back
                    # where it stands free over the bank behind it
                    _, foot_ = h_over(s_cur, e, step_top)
                    front = float(np.max(foot_ + z + ch)) > -0.2
                    _, back_ = h_over(s_cur, e, bank_at)
                    standing = not bool(np.interp(sm, ss, retain.astype(float)) > 0.5)
                    back = standing and float(np.max(back_ + z + ch)) > 0.02
                    # a face stone falls singly: the one a fall point lies in, and any left with its bed all but gone;
                    # a mortared stone holds
                    hit = any(s_cur <= fs < e and z <= hf < z + ch for fs, hf in falls)
                    bed_lost = sum(max(0.0, min(e, l1) - max(s_cur, l0)) for l0, l1 in lost_below)
                    gone = front and not cemented(sm) and (hit or bed_lost > 0.9 * (e - s_cur))
                    if gone:
                        lost.append((s_cur, e))
                        holes.append(dict(k=k, s0=s_cur, s1=e, h0=z, h1=z + ch, stid=stid))
                    # a course that stands at one of the panel's ends: the wall's head is closed there
                    if front or back:
                        for end_, at_end in ((0, s_cur <= -0.3 + 1e-9), (1, e >= run + 0.3 - 1e-9)):
                            if at_end:
                                heads[end_].append((k, z, ch, standing))
                    if (front and not gone) or back:
                        in_panel = panel is not None and panel["s"][0] <= sm <= panel["s"][1]
                        srng = HS.Stream(seed, stid, "lay")
                        stn = WS.face_stone(HS.h(seed, stid), e - s_cur - 0.006, ch - 0.004,
                                            depth=0.06, bulge=srng.uniform(0.003, 0.009),
                                            jag=srng.uniform(0.004, 0.01), chip=srng.uniform(0.006, 0.016))
                        V = stn["V"]
                        hrel = z + V[:, 1]                    # its height over the foot
                        setback = hrel * BATTER
                        sv = s_cur + 0.003 + V[:, 0]
                        tv = side * (W / 2 + 0.006 + setback - V[:, 2] + srng.uniform(-0.004, 0.006))
                        zv = bm + hrel + (sv - sm) * kb
                        bare = YEAR - (panel["year"] - srng.randint(15, 40) if in_panel else spec["built"])
                        Htop = max(float(top(sm)) - bm, 0.3)
                        exposed = np.clip(0.4 + 0.6 * hrel / Htop, 0.3, 1.0)
                        damp = np.clip(1.0 - hrel / 0.35, 0.0, 1.0) * 0.8
                        sky = np.full(len(V), 0.7)
                        if front and not gone:
                            P = np.stack([sv, tv, zv], -1)
                            # (boots scuff a wall's face just above each tread, most where the flight is steep)
                            scuff = WR.boots(zv - step_top(sv), use)
                            put(P, stn["kind"], dict(F=stn["F"], UV=np.stack([V[:, 0], V[:, 1] + z], -1)), srng,
                                bare, YEAR - (panel["year"] if in_panel else spec["built"]), exposed, damp, sky,
                                flip=(side == 1), water=face_water(sv, zv), touch=scuff)
                        # where it stands free (a parapet over the drop), its far side is a face too, battered back
                        # the other way: the wall is DEPTH thick under its coping, thicker at its foot
                        if back:
                            tb = side * (W / 2 + 0.006 + DEPTH + (2.0 * Htop - hrel) * BATTER + V[:, 2]
                                         + srng.uniform(-0.004, 0.006))
                            Pb = np.stack([sv, tb, zv], -1)
                            put(Pb, stn["kind"], dict(F=stn["F"], UV=np.stack([V[:, 0] + 3.1, V[:, 1] + z], -1)), srng,
                                bare, YEAR - spec["built"], exposed, damp, sky, flip=(side == -1),
                                water=face_water(sv, zv))
                    s_cur = e
                below, lost_below = joints, lost
                z += ch
                k += 1
                if z > float(Hs.max()) + 0.1 or k > 60:
                    break
            ln["fallen"] = [hl["stid"] for hl in holes]
            # where a face stone has fallen: its socket, the hearting behind it (the small packing stones a dry wall
            # is filled with), and the soil they hold, a little further in
            for hl in holes:
                s0, s1, h0, h1, stid = hl["s0"], hl["s1"], hl["h0"], hl["h1"], hl["stid"]

                def at(s, h, d):
                    return [s, side * (W / 2 + 0.006 + h * BATTER + d), float(base(s)) + h]

                # its lining: at its back the soil the hearting holds; round it the stones the fallen one lay among,
                # bared when it fell: the beds of the stones over and under it (bedding planes; the lower one holds
                # the grit and water that collect in the hole) and the split ends of its neighbours in the course
                quads = [(facing(np.array([at(s0, h0, SOCKET), at(s1, h0, SOCKET), at(s1, h1, SOCKET),
                                           at(s0, h1, SOCKET)]), (0, -side, 0)), "back", 6, WT.HOLDS)]
                # (the floor lies at the course's pitch: raked with the flight it sheds the rain to its low end and
                # stays damp in its grit; it holds standing water only where the course runs level, at a rest)
                rake = abs(float(base(s1) - base(s0))) / max(s1 - s0, 1e-6)
                floor_w = float(np.interp(rake, [SHEDS * 0.5, SHEDS], [WT.HOLDS, 0.45]))
                for hh, nz, other in ((h0, 1, hl["k"] - 1), (h1, -1, hl["k"] + 1)):
                    for x0, x1 in minus(s0, s1, [(o["s0"], o["s1"]) for o in holes if o["k"] == other]):
                        quads.append((facing(np.array([at(x0, hh, 0.01), at(x1, hh, 0.01), at(x1, hh, SOCKET),
                                                       at(x0, hh, SOCKET)]), (0, 0, nz)), "bed", 3,
                                      floor_w if nz > 0 else 0.2))
                for sx, ns in ((s0, 1), (s1, -1)):
                    if not any(o["k"] == hl["k"] and o is not hl and (o["s1"] == sx or o["s0"] == sx) for o in holes):
                        quads.append((facing(np.array([at(sx, h0, 0.01), at(sx, h1, 0.01), at(sx, h1, SOCKET),
                                                       at(sx, h0, SOCKET)]), (ns, 0, 0)), "end", 2, 0.2))
                Pq = np.concatenate([q_[0] for q_ in quads])
                d_of = np.abs(Pq[:, 1]) - W / 2 - 0.006
                uvq = np.concatenate([q_[:, [0, 2]] if how == "back" else
                                      (np.stack([q_[:, 0], d_of[4 * i:4 * i + 4]], -1) if how == "bed" else
                                       np.stack([d_of[4 * i:4 * i + 4], q_[:, 2]], -1))
                                      for i, (q_, how, _, _) in enumerate(quads)])
                hq = Pq[:, 2] - base(Pq[:, 0])
                kq = np.concatenate([np.full(4, kd, dtype=np.int8) for _, _, kd, _ in quads])
                wq = np.concatenate([np.full(4, wd) for _, _, _, wd in quads])
                # (each point's bake from how far into the hole it lies)
                sky_q, ground_q = recess(np.abs(Pq[:, 1]) - (W / 2 + 0.006 + hq * BATTER))
                put(Pq, kq, dict(F=[tuple(range(4 * i, 4 * i + 4)) for i in range(len(quads))], UV=uvq),
                    HS.Stream(seed, stid, "socket"), YEAR - fell, YEAR - fell, np.full(len(Pq), 0.3),
                    np.clip(1.0 - hq / 0.8, 0.35, 1.0), sky_q, flip=False, water=wq, ground=ground_q)
                # the hearting: rows of small stones, each its own size, run out into the socket since its face stone
                # went (loose packing has nothing left to hold it): the lowest near the lip, each row further back by
                # the slope loose stone stands at, each stone leaning back on it. Its faces turn up to the light, as a
                # gap in a dry wall shows its rubble core (set back 12 to 18 cm, the packing was hidden under the stone
                # above from every judging view and the hole read as its own floor, a flat void)
                hrng = HS.Stream(seed, stid, "hearting")
                rows, hz = [], h0
                while h1 - hz > 0.02:
                    rh = hrng.uniform(0.04, 0.07)
                    if h1 - (hz + rh) < 0.03:
                        rh = h1 - hz
                    rows.append((hz, rh))
                    hz += rh
                m = 0
                for hz, rh in rows:
                    x = s0
                    while s1 - x > 0.02:
                        L_ = hrng.uniform(0.05, 0.14)
                        if s1 - (x + L_) < 0.04:
                            L_ = s1 - x
                        htid = f"{stid}/ht-{m}"
                        m += 1
                        hr = HS.Stream(seed, htid, "lay")
                        sb_ = min(hr.uniform(*HEARTING) + (hz - h0) * REPOSE, SOCKET - 0.09)
                        stn = WS.face_stone(HS.h(seed, htid), L_ - 0.008, rh - 0.006, depth=0.05,
                                            bulge=hr.uniform(0.004, 0.012), jag=hr.uniform(0.004, 0.01),
                                            chip=hr.uniform(0.006, 0.014))
                        V = stn["V"].copy()
                        V[:, 2] -= V[:, 1] * REPOSE * hr.uniform(0.4, 1.0)      # (its top leant back on the slope)
                        sv = x + 0.004 + V[:, 0]
                        hrel = hz + 0.003 + V[:, 1]
                        P = np.stack([sv, side * (W / 2 + 0.006 + hrel * BATTER + sb_ - V[:, 2]), base(sv) + hrel], -1)
                        sky_h, ground_h = recess(sb_ - V[:, 2])
                        # (stones shed water: damp in the hole, never holding it as the soil behind and the grit on
                        # the floor do)
                        put(P, stn["kind"], dict(F=stn["F"], UV=np.stack([V[:, 0] + x, V[:, 1] + hz], -1)), hr,
                            YEAR - fell, YEAR - fell, np.full(len(V), 0.3), np.clip(1.0 - hrel / 0.8, 0.35, 1.0),
                            sky_h, flip=(side == 1), water=np.full(len(V), 0.3), ground=ground_h)
                        x += L_
            # the backing: soil and moss in the joints, a few centimetres behind the face, where the dry wall holds
            # them (in the rebuilt panel and the patched hole, cement pointing); open where a stone has fallen, and
            # following the foot and the top through each change of pitch
            nb = max(4, int(run / 0.25))
            sb = np.linspace(-0.3, run + 0.3, nb)
            for j in range(nb - 1):
                for half_, (zf0, zf1) in enumerate(((0.0, 0.5), (0.5, 1.0))):
                    s_a, s_b = sb[j], sb[j + 1]
                    # (cut at the panel's straight joints, so the pointing changes where the stones do)
                    xs = sorted({s_a, s_b} | {q for q in bends + ends_p if s_a < q < s_b} |
                                {q for hl in holes for q in (hl["s0"], hl["s1"]) if s_a < q < s_b})
                    pts, fcs, cem_v, yrs_v = [], [], [], []
                    for x0, x1 in zip(xs[:-1], xs[1:]):
                        sm = (x0 + x1) / 2
                        in_panel = panel is not None and panel["s"][0] <= sm <= panel["s"][1]
                        cem = cemented(sm)
                        d = 0.012 if cem else BACKING
                        yrs = YEAR - (panel["year"] if in_panel else (1979 if cem else spec["built"]))
                        H0, H1 = float(top(x0) - base(x0)), float(top(x1) - base(x1))
                        lo, hi = (H0 * zf0, H1 * zf0), (H0 * zf1, H1 * zf1)
                        bands = sorted((hl["h0"], hl["h1"]) for hl in holes if hl["s0"] <= x0 + 1e-9 and hl["s1"] >= x1 - 1e-9)
                        edges_ = [lo]
                        for h0, h1 in bands:
                            edges_ += [tuple(float(np.clip(h0, lo[i], hi[i])) for i in (0, 1)),
                                       tuple(float(np.clip(h1, lo[i], hi[i])) for i in (0, 1))]
                        edges_.append(hi)
                        for (p0, p1), (q0, q1) in zip(edges_[0::2], edges_[1::2]):
                            corner = [(x0, p0), (x1, p1), (x1, q1), (x0, q0)]
                            if q0 - p0 <= 1e-6 and q1 - p1 <= 1e-6:
                                continue
                            if q0 - p0 <= 1e-6:
                                corner = corner[:3]
                            elif q1 - p1 <= 1e-6:
                                corner = [corner[0], corner[1], corner[3]]
                            fcs.append(tuple(range(len(pts), len(pts) + len(corner))))
                            pts += [[sq, side * (W / 2 + 0.006 + hq * BATTER + d), float(base(sq)) + hq] for sq, hq in corner]
                            cem_v += [cem] * len(corner)
                            yrs_v += [yrs] * len(corner)
                    if not pts:
                        continue
                    P = np.array(pts)
                    kind = np.where(cem_v, 4, 6).astype(np.int8)
                    hgt = P[:, 2] - base(P[:, 0])
                    damp = np.clip(1.0 - hgt / 0.8, 0.35, 1.0)
                    yrs = np.array(yrs_v, float)
                    put(P, kind, dict(F=fcs, UV=P[:, [0, 2]]), HS.Stream(seed, f"{pnl}/bk-{j}-{half_}", "marks"),
                        yrs, yrs, np.full(len(P), 0.5), damp, np.full(len(P), 0.45), flip=(side == 1),
                        water=np.full(len(P), WT.HOLDS))
            # the copings: slabs laid along the top, each straight from joint to joint, their fronts a little proud of
            # the face (a parapet's a little proud of its far side too)
            for c, (s_cur, e) in enumerate(copes):
                sm = (s_cur + e) / 2
                cpid = f"{pnl}/cp-{c}"
                crng = HS.Stream(seed, cpid, "lay")
                thick = crng.uniform(0.07, 0.1)
                standing = not bool(np.interp(sm, ss, retain.astype(float)) > 0.5)
                depth_c = DEPTH + 0.05 if standing else DEPTH
                pc = SL.slab(HS.h(seed, cpid), e - s_cur - 0.008, depth_c, thick,
                             front_round=crng.uniform(0.004, 0.009), side_round=0.004, flake=0.3,
                             chip=crng.uniform(0.01, 0.025), edge_jag=crng.uniform(0.008, 0.014), layers=2)
                V = pc["V"]
                t0, t1 = float(top(s_cur)), float(top(e))
                face_t = W / 2 + 0.006 + float(top(sm) - base(sm)) * BATTER - crng.uniform(0.015, 0.035)
                sv = s_cur + 0.004 + V[:, 0]
                tv = side * (face_t + V[:, 1])
                zv = (t0 + t1) / 2 - thick + V[:, 2] + (sv - sm) * (t1 - t0) / (e - s_cur)
                P = np.stack([sv, tv, zv], -1)
                along = np.clip(V[:, 1] / depth_c, 0.0, 1.0)
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
                hand = WR.hands(float(top(sm)) - float(step_top(sm)), 1.0)
                edge_in = np.where(pc["kind"] == 0, np.clip(1.0 - V[:, 1] / 0.12, 0.0, 1.0), np.where(pc["kind"] == 1, 1.0, 0.0))
                put(P, pc["kind"], dict(F=pc["F"], UV=pc["UV"]), crng, bare, YEAR - spec["built"],
                    np.full(len(P), 1.0), damp, sky, flip=(side == 1), water=w_cope, touch=hand * edge_in * use)
            # the wall's heads: at each end of the panel the wall is closed, as a dry wall's end is built, with its
            # longest stones laid through it, or as far in as they go, each course bridging the joints of the one
            # under it; their faces make the end, plumb, from the face to the far face (or the depth a retaining wall
            # keeps behind its face), and behind their joints the soil a dry wall holds
            for end_, s_h in ((0, -0.3), (1, run + 0.3)):
                o_ = 1.0 if end_ else -1.0                     # out of the end, along the flight
                Hh = max(float(top(s_h) - base(s_h)), 0.3)
                b_h = float(base(s_h))

                def through(hh, standing_):
                    """The wall's thickness at a height over its foot, from its face to its far face (both battered)
                    or, where it retains, to the depth it keeps behind its face (the face alone battered)."""
                    return DEPTH + (Hh - hh) * BATTER * (2.0 if standing_ else 1.0)

                below_h = []
                for kk, zz, ch_, standing_ in heads[end_]:
                    cid = f"{pnl}/co-{kk}"
                    hrng = HS.Stream(seed, cid, "head", end_)
                    wd = through(zz + ch_ / 2, standing_)
                    laid, x_, joints_ = [], 0.0, []
                    while wd - x_ > 1e-6:
                        for _ in range(20):
                            L_ = hrng.uniform(*HEAD_LEN)
                            if x_ + L_ >= wd - STONE_LEN[0] or all(abs(x_ + L_ - jb) > BRIDGE for jb in below_h):
                                break
                        if wd - (x_ + L_) < STONE_LEN[0]:    # (no sliver at the back: the last runs to the far face)
                            L_ = wd - x_
                        laid.append((x_, L_))
                        x_ += L_
                        if wd - x_ > 1e-6:
                            joints_.append(x_)
                    below_h = joints_
                    for i, (x0, L_) in enumerate(laid):
                        stn = WS.face_stone(HS.h(seed, cid, "head", end_, i), L_ - 0.006, ch_ - 0.004, depth=0.06,
                                            bulge=hrng.uniform(0.003, 0.009), jag=hrng.uniform(0.004, 0.01),
                                            chip=hrng.uniform(0.006, 0.016))
                        V = stn["V"]
                        hrel = zz + V[:, 1]
                        # (across the end, each stone keeps its share of the thickness at every height, so the head
                        # meets both battered faces)
                        tf = W / 2 + 0.006 + hrel * BATTER
                        tv = side * (tf + (x0 + 0.003 + V[:, 0]) / wd * through(hrel, standing_))
                        sv = s_h - o_ * 0.003 + o_ * V[:, 2]
                        zv = b_h + hrel
                        P = np.stack([sv, tv, zv], -1)
                        bare = YEAR - spec["built"]
                        put(P, stn["kind"], dict(F=stn["F"], UV=np.stack([V[:, 0] + x0, V[:, 1] + zz], -1)), hrng,
                            bare, bare, np.clip(0.4 + 0.6 * hrel / Hh, 0.3, 1.0),
                            np.clip(1.0 - hrel / 0.35, 0.0, 1.0) * 0.8, np.full(len(V), 0.7), flip=(side * o_ > 0),
                            water=face_water(sv, zv))
                if heads[end_]:
                    h0_, h1_ = heads[end_][0][1], Hh          # (up to the coping's bed, as the face's backing)
                    st_ = heads[end_][0][3]
                    d_in = s_h - o_ * (0.003 + BACKING)
                    Pk = facing(np.array([[d_in, side * (W / 2 + 0.006 + hh * BATTER + dt), b_h + hh]
                                          for hh, dt in ((h0_, 0.0), (h0_, through(h0_, st_)),
                                                         (h1_, through(h1_, st_)), (h1_, 0.0))]), (o_, 0, 0))
                    put(Pk, np.full(4, 6, dtype=np.int8), dict(F=[(0, 1, 2, 3)], UV=Pk[:, [1, 2]]),
                        HS.Stream(seed, pnl, "head", end_), YEAR - spec["built"], YEAR - spec["built"],
                        np.full(4, 0.5), np.clip(1.0 - (Pk[:, 2] - b_h) / 0.8, 0.35, 1.0), np.full(4, 0.45),
                        flip=False, water=np.full(4, WT.HOLDS))
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
        sys.path.append(os.path.join(HERE, "..", "tools"))
        import mesh_hash  # noqa: E402
        with ST.install_lock(path):        # the install step, under the Unity lock (tools/unity_lock.py)
            bpy.ops.export_scene.fbx(filepath=path, use_selection=True, object_types={"MESH"}, axis_forward="Z",
                                     axis_up="Y", bake_space_transform=True, apply_unit_scale=True,
                                     apply_scale_options="FBX_SCALE_ALL", mesh_smooth_type="OFF", colors_type="LINEAR",
                                     use_mesh_modifiers=False, add_leaf_bones=False, bake_anim=False, path_mode="STRIP",
                                     embed_textures=False)
            with open(path[:-4] + ".json", "w") as fh:
                json.dump(info, fh, indent=1)
            print("FBX", path)
            mesh_hash.write_manifest(path)     # the mesh hashes beside the export (blender/tools/mesh_hash.py)
    return info


if __name__ == "__main__":
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    which = argv[0] if argv else "gully_cheeks"
    unity = argv[1] if len(argv) > 1 else os.path.join(HERE, "..", "..", "unity")
    build(which, unity)
