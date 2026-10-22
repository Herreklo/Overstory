"""Masonry: a stair's cheek walls and its steps laid as 2D elevations in integer millimetres, by a mason's rules, before
any mesh (port step 2b, rung R1: reviews/lt1/port/2b/design.md, SN2, SN3, SN4, SN10). Pure Python, no bpy and no
numpy: the wall kind's stages and the stair's geometry stage call these functions later, from facts in integer mm.

A wall line (wl-<token>/fl-<n>/<l|r>, the wall beside one flight on one side) is unrolled as an elevation: s along
the flight from its foot point (mm), z up (mm, absolute). It has two faces, the stair's and the bank's, built to the
same level course lines and through the same features. It is laid in this order, features first:
- the course lines: every step top, at most one line between two step tops (the lower course the larger), free lines
  over the last step and foundation lines under the foot, each course 60 to 140 mm (wall.py's COURSE);
- the coping, raked over each flight and level over each rest, with its features: a kneeler at the foot of every
  raked run (at the lane and at every rest-to-flight break) and every 2.4 to 3.6 m along it (Rivington 1904, p. 54;
  Mitchell 1902), a knee at every flight-to-rest break, carrying both tops, and a square topstone where a wall ends on
  a level; every bed under them on a course line;
- the heads at the wall's ends: ties and runners alternating, each two courses high;
- the footings: on the stair's face the steps themselves (their ends occupied cells, 150 mm into the wall), on the
  bank's face steps with the ground, each step a whole course;
- the panels between the features (and the 1961 panel's edges), each on its own id and seed;
- the fallen stones the facts give, the through stones, the panels' toothed boundaries, the 1961 edges' straight joints;
- then each course's free lengths, filled by choosing each stone's length (never stretched), every joint kept a lap
  from the joints below and above, the last stone under the rake long enough for the cut to leave a trapezoid.

The steps (SN3) are laid in plan: one or two stones a step, both ends 150 mm into the walls, the joint outside the
middle third, alternating, lapped 40 to 60 mm on the step below; a rest two to four slabs.

Seeds: blender/resolver/hashing.py, keyed on the world seed, the stable id of what a draw is for and its purpose,
never a position. Choices are integers and the four operations (and a square root for a rake's length); outlines are
integer mm, and no float enters a choice. Ids (schemas/naming.md; the slots 2b proposes): a panel <line>/pn-<p>; a
face stone <panel>/<stair|bank>/co-<k>/sp-<j>; a through <panel>/co-<k>/th-<j>; a coping <panel>/cp-<c>; a head's
stone <line>/hd-<e>/st-<m> (a tie, through the wall), its runners .../st-<m>/stair and .../st-<m>/bank, its topstone
<line>/hd-<e>/top; <line>/kneeler-<i>, <line>/knee-<i>. A step's stones are the plan's <step>/sl-<k>; a rest's slabs
<step>/sl-<k> counted row by row from its front (the plan names two; a rest deeper than the longest slab has four);
a turn landing's <flight>/turn/sl-<k>.
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "resolver"))
import hashing as HS  # noqa: E402  (the one hash spec)

# The wall's numbers (wall.py's, in mm), and SN2's and SN10's
COURSE = (60, 140)          # a course's height
SLIVER = 50                 # no stone under 50 mm high, no face narrower (SN2)
ACUTE = 25                  # nor more acute than 25 degrees (tested, never a choice)
STONE = (180, 620)          # a face stone's length (wall.py STONE_LEN)
SHORT = 120                 # where geometry leaves a run no whole stones fill, the least a stone may be (flagged)
RATIO = (9, 2)              # no stone longer than 4.5 times its height (SN10)
LAP_MIN = 40                # a joint is kept 0.4 of the course's height, at least 40 mm, from the joints below (SN10)
PARAPET = 900               # the coping's top over the pitch line (wall.py PARAPET)
COPE_T = (70, 100)          # a coping's thickness, square to its top (wall.py)
COPE_T_LEVEL = (70, 84)     # a level run's: the raked run above it is this times the rake's secant, within COPE_T
COPE_L = (450, 1000)        # a coping slab's length along its bed (wall.py)
COPE_DELTA = 40             # how far a coping's top may stand off the pitch line + PARAPET, to put its bed on a line
KNEELER_W = (250, 450)      # a kneeler's level top
KNEELER_EVERY = (2400, 3600)  # an intermediate kneeler along a raked run, this far (8 to 12 goings) from the stop below
KNEELER_MID_W = (250, 450)  # its bed's length: wider than it is high
KNEELER_BACK = 2            # a kneeler's plumb back rises through at most two courses (SN10), where the lines allow
KNEE_LEVEL = (150, 350)     # a knee's level top
KNEE_RAKE = (150, 450)      # a knee's raked top, along s
TOPSTONE = (220, 450)       # a topstone's length (its height near it: square)
HEAD_TIE = (180, 260)       # a head's tie, through the wall, as its face shows
HEAD_RUN = (400, 620)       # a head's runner along one face (wall.py HEAD_LEN, from its longest stones)
LONG_SHORT = ((420, 580), (200, 270))   # a rebuilt panel's end stones, long and short in alternate courses (wall.py)
THROUGH = (200, 300)        # a through stone's face
THROUGH_FIRST = (400, 700)  # the first through from a panel's start
THROUGH_EVERY = (800, 1000) # and then one about every metre
THROUGH_CLEAR = 300         # never this near a panel's boundary (its teeth and their laps stay clear)
TOOTH = (50, 90)            # a panel's boundary joint, course by course, this far either side of it, alternating
FREE_FIRST = (100, 140)     # the free courses over the last step: the first, then each one up to 25 mm smaller
FREE_STEP = 25
FOUND = (110, 140)          # the foundation courses under the foot (the bank's face shows them where it is low)
FOOT_TREAD = 300            # a bank footing's step is at least this long
GRID = 100                  # the ground's sample spacing

# The steps' (SN3), in mm
STEP_TAIL = 150             # both ends this far into the walls
FACE_GAP = 6                # a wall's face stands this far off the stair's edge (wall.py, W/2 + 0.006)
STEP_LAP = (40, 60)         # a step's front bears this far on the back of the one below
TREAD_JOINT = (4, 10)       # a tread's joint (SN5)
STEP_JOINT_CLEAR = 150      # no joint within this of the joint on the step below
FIRST_STEP_BED = 200        # the first step's block goes this far under the lane

FACES = ("stair", "bank")


class Refused(ValueError):
    """A rule the facts make impossible: raised loudly, never fixed silently."""


def div_round(n, d):
    """n / d to the nearest integer, halves up (d nonzero)."""
    if d < 0:
        n, d = -n, -d
    return (2 * n + d) // (2 * d)


def lap_of(h):
    """SN10: a joint's lap from the joints below a course of height h."""
    return max(LAP_MIN, (2 * h + 4) // 5)


def longest(h):
    """The longest stone a course of height h takes (SN10's 4.5, and wall.py's longest)."""
    return min(STONE[1], RATIO[0] * h // RATIO[1])


def fillable(n, h):
    """Whether a free length n in a course of height h can be laid in whole stones of wall.py's lengths that SN10
    allows: some count k of stones with k x 180 <= n <= k x longest(h). (A thin course has gaps: at 62 mm high no
    run between 279 and 360 mm can be filled.)"""
    if n == 0:
        return True
    lm = longest(h)
    if n < STONE[0] or lm < STONE[0]:
        return False
    k = -(-n // lm)
    return k * STONE[0] <= n


# ---------------------------------------------------------------------------------------------------------------
# Interval sets of integers: sorted, disjoint [lo, hi] pairs

def iv_clip(ivs, lo, hi):
    return [(max(a, lo), min(b, hi)) for a, b in ivs if min(b, hi) >= max(a, lo)]


def iv_union(ivs):
    out = []
    for a, b in sorted(ivs):
        if out and a <= out[-1][1] + 1:
            out[-1] = (out[-1][0], max(out[-1][1], b))
        else:
            out.append((a, b))
    return out


def iv_minus_open(ivs, windows):
    """ivs less every integer strictly inside a window (lo, hi)."""
    out = list(ivs)
    for lo, hi in windows:
        a0, b0 = lo + 1, hi - 1
        if a0 > b0:
            continue
        nxt = []
        for a, b in out:
            if b < a0 or a > b0:
                nxt.append((a, b))
                continue
            if a < a0:
                nxt.append((a, a0 - 1))
            if b > b0:
                nxt.append((b0 + 1, b))
        out = nxt
    return out


def iv_contains(ivs, x):
    return any(a <= x <= b for a, b in ivs)


def iv_nearest(ivs, x):
    best = None
    for a, b in ivs:
        c = min(max(x, a), b)
        if best is None or abs(c - x) < abs(best - x):
            best = c
    return best


def fill_run(a, b, lmin, lmax, windows, target, first=None, last=None):
    """Joints along [a, b]: each stone's length in [lmin, lmax] (the first in `first`, the last in `last`, when given),
    no joint strictly inside a window, each stone as near its drawn length as the run allows: target(i) is the i-th
    stone's drawn length. Exact: the positions from which b can still be reached are found first, so a stone is never
    stretched to close the run. Returns the joints [a, x1, ..., b], or None when no laying exists."""
    if b <= a:
        return None
    allowed = iv_minus_open([(a, b)], windows)
    llo, lhi = last if last else (lmin, lmax)
    # the positions from which b is one last stone away, then from which those are one stone away, and so on
    R = iv_clip(iv_minus_open([(b - lhi, b - llo)], windows), a, b - 1)
    R = [iv for iv in R if iv[1] >= iv[0]]
    R = iv_union([(x, y) for x, y in R if iv_contains(allowed, x) or True])
    R = iv_union(_intersect(R, allowed))
    while True:
        P = iv_union(R + _intersect(iv_clip([(u - lmax, v - lmin) for u, v in R], a, b - 1), allowed))
        if P == R:
            break
        R = P
    joints, x, i = [a], a, 0
    while True:
        lo, hi = first if (i == 0 and first) else (lmin, lmax)
        cand = _intersect(R, [(x + lo, x + hi)])
        end_ok = llo <= b - x <= lhi and lo <= b - x <= hi
        t = x + target(i)
        if end_ok and (not cand or abs(b - t) <= abs(iv_nearest(cand, t) - t)):
            joints.append(b)
            return joints
        if not cand:
            return None
        x = iv_nearest(cand, t)
        joints.append(x)
        i += 1


def _intersect(A, B):
    out = []
    for a, b in A:
        for c, d in B:
            lo, hi = max(a, c), min(b, d)
            if lo <= hi:
                out.append((lo, hi))
    return iv_union(out)


# ---------------------------------------------------------------------------------------------------------------
# The rake: a raked coping's top and bed between two breaks, in integer mm

class Rake:
    """A raked coping run from (sA, CA) to (sB, CB), its top's ends: its bed is the top less tv (the thickness, plumb),
    and a joint square to the rake rises dx back from its bed point to its top."""

    def __init__(self, sA, CA, sB, CB, tv, dx, t):
        self.sA, self.CA, self.sB, self.CB, self.tv, self.dx, self.t = sA, CA, sB, CB, tv, dx, t

    @classmethod
    def square(cls, sA, CA, sB, CB, t):
        """Its thickness t square to the top (the rake's length by an integer square root, in thousandths of a mm)."""
        ds, dz = sB - sA, CB - CA
        ln = math.isqrt((ds * ds + dz * dz) * 1000000)
        return cls(sA, CA, sB, CB, div_round(t * ln, ds * 1000), div_round(t * dz * 1000, ln), t)

    @classmethod
    def meeting(cls, sA, CA, sB, CB, t_level):
        """Its thickness chosen so a joint square to the rake from its foot (sA, CA) meets its bed at the level run's
        bed, t_level under CA: plumb thickness t_level(1 + k^2), the joint's run t_level k."""
        ds, dz = sB - sA, CB - CA
        ln = math.isqrt((ds * ds + dz * dz) * 1000000)
        return cls(sA, CA, sB, CB, div_round(t_level * (ds * ds + dz * dz), ds * ds), div_round(t_level * dz, ds),
                   div_round(t_level * ln, ds * 1000))

    def C(self, s):
        return self.CA + div_round((s - self.sA) * (self.CB - self.CA), self.sB - self.sA)

    def B(self, s):
        return self.C(s) - self.tv

    def inv_B(self, z):
        return self.sA + div_round((z + self.tv - self.CA) * (self.sB - self.sA), self.CB - self.CA)

    def slope(self):
        return (self.CB - self.CA, self.sB - self.sA)


# ---------------------------------------------------------------------------------------------------------------
# The steps, in plan

def lay_steps(flight, seed, slab, width):
    """A flight's steps (SN3): the stones of each step across, both ends STEP_TAIL into the walls, never pieced in
    depth; a rest's slabs in rows; a turn landing's under the flight's foot. x across the stair (mm, right of the
    uphill direction positive), y along it (s). Raises Refused when the longest stone the record's finish allows makes a
    two-stone step impossible with its joint outside the middle third."""
    fid = flight["id"]
    half = width // 2 + FACE_GAP + STEP_TAIL
    clear = width + 2 * FACE_GAP
    third = -(-clear // 6)                  # the middle third's half-width, rounded out: a joint lies at |x| >= this
    hi, lo = slab["hi"], slab["lo"]
    out = dict(id=fid, half=half, third=third, stones=[], steps=[], flags=[])
    def edge_window(side, jw):
        """Where a step's joint [xl, xl + jw] may start. On the left (side -1) the right stone [xl + jw, half] is at
        most hi long and the joint's edge lies outside the middle third (xl + jw <= -third); on the right the left
        stone [-half, xl] is at most hi long and xl >= third."""
        if side < 0:
            return (half - hi - jw, -third - jw)
        return (third, hi - half)

    widest = edge_window(-1, TREAD_JOINT[1])
    if widest[0] > widest[1]:
        raise Refused(f"{fid}: a two-stone step is impossible: the stones would be {2 * half} mm across between the "
                      f"walls' tails, the longest the finish allows is {hi} mm, and the joint must lie outside the "
                      f"middle third ({third} mm either side of the walking line)")
    out["jointWindow"] = dict(left=list(edge_window(-1, TREAD_JOINT[0])), right=list(edge_window(1, TREAD_JOINT[0])),
                              widthMm=edge_window(-1, TREAD_JOINT[0])[1] - edge_window(-1, TREAD_JOINT[0])[0] + 1)
    steps = flight["steps"]
    n = len(steps)
    side = 1 if HS.h(seed, fid, "joint", "side") % 2 else -1
    below = None                       # the joint (xl, jw) on the step or row below
    T = [flight["zFoot"]] + [st["zTop"] for st in steps]

    def row_joint(key_id, below_x, ahead_side):
        """A rest's or landing's row: two slabs, the joint anywhere both stay within the finish's sizes, clear of the
        joint below and, on the row the next step bears on, of where that step's joint can fall."""
        rng = HS.Stream(seed, key_id, "row")
        jw = rng.randint(*TREAD_JOINT)
        lo_x, hi_x = half - hi - jw, hi - half          # both slabs <= hi
        lo_x, hi_x = max(lo_x, -half + lo), min(hi_x, half - lo - jw)
        allowed = [(lo_x, hi_x)]
        keep = []
        if below_x is not None:
            keep.append((below_x - STEP_JOINT_CLEAR, below_x + STEP_JOINT_CLEAR))
        if ahead_side is not None:
            w0, w1 = edge_window(ahead_side, TREAD_JOINT[1])[0], edge_window(ahead_side, TREAD_JOINT[0])[1]
            keep.append((w0 - STEP_JOINT_CLEAR, w1 + STEP_JOINT_CLEAR))
        allowed = iv_minus_open(allowed, keep)
        if not allowed:
            raise Refused(f"{key_id}: no joint for a rest's row clear of the joints below and above")
        x = iv_nearest(allowed, rng.randint(lo_x, hi_x))
        return x, jw

    if flight["start"] > 0:
        # the turn landing under the flight's foot, at the lane's level: the first step bears on its back
        rid = f"{fid}/turn"
        lap = HS.Stream(seed, f"{fid}/turn", "lap").randint(*STEP_LAP)
        y0, y1 = 0, steps[0]["S"] + lap
        if y1 - y0 > hi:
            out["flags"].append(f"{fid}/turn: {y1 - y0} mm deep, over the longest slab {hi}: laid as one row anyway")
        x, jw = row_joint(f"{rid}/row-0", None, side)
        out["stones"] += [dict(id=f"{rid}/sl-0", kind="landing", step=f"{fid}/turn", row=0,
                               outline=[[-half, y0], [x, y0], [x, y1], [-half, y1]]),
                          dict(id=f"{rid}/sl-1", kind="landing", step=f"{fid}/turn", row=0,
                               outline=[[x + jw, y0], [half, y0], [half, y1], [x + jw, y1]])]
        out["steps"].append(dict(id=f"{fid}/turn", rest=True, rows=[dict(y=[y0, y1], joint=[x, x + jw])],
                                 lap=lap, z=[T[0] - (T[1] - T[0]), T[0]], turn=True))
        below = x
    g = flight["g"]
    for i, st in enumerate(steps):
        sid = st["id"]
        rng = HS.Stream(seed, sid, "lay")
        lap = rng.randint(*STEP_LAP) if i < n - 1 else 0
        y0 = st["S"]
        y1 = steps[i + 1]["S"] + lap if i < n - 1 else y0 + st["D"]     # (S and D were rounded apart: S rules)
        rise = T[i + 1] - T[i]
        z0 = T[i + 1] - rise - (FIRST_STEP_BED if i == 0 and flight["start"] == 0 else 0)
        rest = st["D"] > g + 1
        if not rest:
            jw = rng.randint(*TREAD_JOINT)
            wl, wh = edge_window(side, jw)
            x = rng.randint(wl, wh)
            if below is not None and abs(x - below) < STEP_JOINT_CLEAR:
                out["flags"].append(f"{sid}: joint within {STEP_JOINT_CLEAR} mm of the one below")
            out["stones"] += [dict(id=f"{sid}/sl-0", kind="step", step=sid, outline=[[-half, y0], [x, y0], [x, y1],
                                                                                     [-half, y1]]),
                              dict(id=f"{sid}/sl-1", kind="step", step=sid, outline=[[x + jw, y0], [half, y0],
                                                                                     [half, y1], [x + jw, y1]])]
            out["steps"].append(dict(id=sid, rest=False, side=side, joint=[x, x + jw], jointId=f"{sid}/jt-0",
                                     y=[y0, y1], lap=lap, z=[z0, T[i + 1]]))
            below = x
            side = -side
        else:
            depth = y1 - y0
            nrows = -(-depth // hi)
            if nrows == 1:
                cuts = [y0, y1]
            else:
                # two rows (the rests here are under 2 x hi deep), the cut near the middle, both rows within hi
                lo_d, hi_d = max(depth - hi, lo), min(hi, depth - lo)
                if nrows > 2 or lo_d > hi_d:
                    raise Refused(f"{sid}: a rest {depth} mm deep cannot be laid in two rows of slabs up to {hi} mm")
                d0 = min(max(rng.randint(depth // 2 - 300, depth // 2 + 300), lo_d), hi_d)
                cuts = [y0, y0 + d0, y1]
            rows = []
            for r_ in range(len(cuts) - 1):
                x, jw = row_joint(f"{sid}/row-{r_}", below, side if r_ == len(cuts) - 2 and i < n - 1 else None)
                ya, yb = cuts[r_], cuts[r_ + 1]
                out["stones"] += [dict(id=f"{sid}/sl-{2 * r_}", kind="rest", step=sid, row=r_,
                                       outline=[[-half, ya], [x, ya], [x, yb], [-half, yb]]),
                                  dict(id=f"{sid}/sl-{2 * r_ + 1}", kind="rest", step=sid, row=r_,
                                       outline=[[x + jw, ya], [half, ya], [half, yb], [x + jw, yb]])]
                rows.append(dict(y=[ya, yb], joint=[x, x + jw]))
                below = x
            out["steps"].append(dict(id=sid, rest=True, rows=rows, y=[y0, y1], lap=lap, z=[z0, T[i + 1]]))
    return out


def step_end_id(steps_out, step_id, side, y):
    """The id of the stone whose end shows in the wall on `side` at y along the step (for a rest, its row)."""
    k = 1 if side > 0 else 0
    for st in steps_out["stones"]:
        if st["step"] == step_id and st["outline"][0][1] <= y < st["outline"][2][1] and \
                ((k == 1 and st["outline"][1][0] == steps_out["half"]) or (k == 0 and st["outline"][0][0] == -steps_out["half"])):
            return st["id"]
    return step_id


# ---------------------------------------------------------------------------------------------------------------
# A wall line

class Line:
    """One wall line's laying: its facts, its course lines, its coping and features, its panels, its faces' courses."""

    def __init__(self, line, flight, steps_out, seed, reseed=None):
        self.f = line
        self.fl = flight
        self.steps_out = steps_out
        self.seed = seed
        self.reseed = reseed or {}
        self.id = line["id"]
        self.side = line["side"]
        self.s0, self.s1 = line["s0"], line["s1"]
        self.flags = []
        self.stones = []           # every stone: face stones, throughs, copings, heads, features
        self.cells = []            # the step ends, as the wall sees them (occupied, not the wall's)
        self.T = [flight["zFoot"]] + [st["zTop"] for st in flight["steps"]]
        self.S = [st["S"] for st in flight["steps"]]

    # ---- keys
    def key(self, owner, *purpose):
        """A draw's key: the world seed, the id it is for, its purpose; a panel re-laid by an event takes its event."""
        extra = self.reseed.get(owner)
        return (self.seed, owner) + purpose + ((extra,) if extra else ())

    def stream(self, owner, *purpose):
        return HS.Stream(*self.key(owner, *purpose))

    def between(self, lo, hi, owner, *purpose):
        return HS.between(HS.h(*self.key(owner, *purpose)), lo, hi)

    # ---- course lines
    def course_lines(self, forced):
        lid, T = self.id, self.T
        L = [(T[0], "step", -1)]
        self.mid_of = {}
        for i in range(len(T) - 1):
            lo, hi = T[i], T[i + 1]
            rise = hi - lo
            if rise < COURSE[0]:
                raise Refused(f"{self.fl['steps'][i]['id']}: a rise of {rise} mm is under a course's least")
            if rise > COURSE[1]:
                if i in forced:
                    m = forced[i]
                else:
                    a, b = lo + (rise + 1) // 2, hi - COURSE[0]
                    m = HS.between(HS.h(self.seed, lid, "course", i), a, b) if b >= a else lo + rise // 2
                L.append((m, "mid", i))
                self.mid_of[i] = m
            L.append((hi, "step", i))
        rng = HS.Stream(self.seed, lid, "courses", "free")
        z, hp = T[-1], None
        while z < T[-1] + PARAPET + 300:
            h = rng.randint(*FREE_FIRST) if hp is None else rng.randint(max(COURSE[0], hp - FREE_STEP), hp)
            z += h
            L.append((z, "free", None))
            hp = h
        rng = HS.Stream(self.seed, lid, "courses", "found")
        zlow = min(min(gz for _, gz in self.f["ground"]), T[0]) - 2 * COURSE[1]
        z = T[0]
        while z > zlow:
            z -= rng.randint(*FOUND)
            L.append((z, "found", None))
        L.sort()
        self.Lz = [z for z, _, _ in L]
        self.Lkind = [k for _, k, _ in L]
        self.Lsrc = [s for _, _, s in L]

    def line_index(self, z):
        return self.Lz.index(z)

    def lines_in(self, lo, hi):
        return [z for z in self.Lz if lo <= z <= hi]

    # ---- the pitch line's runs and the panels
    def runs(self):
        P = self.fl["pitch"]
        segs = []
        if P[0][0] > self.s0 + SLIVER:
            segs.append(dict(kind="level", s=[self.s0, P[0][0]], z=P[0][1]))
        for p, q in zip(P, P[1:]):
            if q[1] > p[1]:
                segs.append(dict(kind="rake", s=[p[0], q[0]], z=[p[1], q[1]]))
            else:
                segs.append(dict(kind="level", s=[p[0], q[0]], z=p[1]))
        if P[-1][0] < self.s1 - SLIVER:
            segs.append(dict(kind="level", s=[P[-1][0], self.s1], z=P[-1][1]))
        if segs[-1]["kind"] != "level":
            raise Refused(f"{self.id}: a wall ending on a rake has no head rule yet")
        return segs

    def panels_make(self, segs):
        b = [self.s0]
        for sg in segs[1:]:
            b.append(sg["s"][0])
        edges = []
        reb = self.f.get("rebuilt")
        if reb:
            edges = list(reb["s"])
        bounds = sorted(set(b + edges + [self.s1]))
        self.edges = edges
        self.panels = []
        for p, (lo, hi) in enumerate(zip(bounds, bounds[1:])):
            work = "1961" if reb and reb["s"][0] <= (lo + hi) // 2 <= reb["s"][1] else "built"
            self.panels.append(dict(id=f"{self.id}/pn-{p}", s=[lo, hi], work=work))
        self.boundaries = []      # the feature boundaries the courses under a feature are toothed at
        for sg in segs[1:]:
            self.boundaries.append(sg["s"][0])

    def panel_at(self, s):
        for pn in self.panels:
            if pn["s"][0] <= s < pn["s"][1]:
                return pn
        return self.panels[-1]

    # ---- the coping and its features
    def coping(self):
        """Features first: the coping's runs, its kneelers, knees and topstones, the beds under them on course lines.
        Returns the ceiling the courses are laid under: pieces along s, level (a bed) or raked (a Rake)."""
        forced = {}
        for _ in range(4):
            self.course_lines(forced)
            need = self._coping(forced)
            if need is None:
                return
            forced.update(need)
        raise Refused(f"{self.id}: the coping's beds could not be put on course lines")

    def _snap_level(self, zp, owner):
        """A level run's top and bed: the bed on a course line, its top PARAPET + delta over the pitch, its thickness
        in COPE_T_LEVEL; the drawn delta and thickness kept as near as a line allows."""
        rng = HS.Stream(self.seed, owner, "cope", "level")     # (the wall's coping, not its panel's: no event re-lays it)
        d0, t0 = rng.randint(-COPE_DELTA, COPE_DELTA), rng.randint(*COPE_T_LEVEL)
        best = None
        for z in self.Lz:
            c = z - zp - PARAPET
            dlo, dhi = max(-COPE_DELTA, COPE_T_LEVEL[0] + c), min(COPE_DELTA, COPE_T_LEVEL[1] + c)
            if dlo > dhi:
                continue
            d = min(max(d0, dlo), dhi)
            t = d - c
            cost = abs(d - d0) + abs(t - t0)
            if best is None or cost < best[0]:
                best = (cost, z, d, t)
        if best is None:
            # no line in reach: the rise under the bed takes its middle line there
            want = zp + PARAPET + d0 - t0
            for i in range(len(self.T) - 1):
                lo, hi = self.T[i] + COURSE[0], self.T[i + 1] - COURSE[0]
                wlo, whi = zp + PARAPET - COPE_DELTA - COPE_T_LEVEL[1], zp + PARAPET + COPE_DELTA - COPE_T_LEVEL[0]
                a, b = max(lo, wlo), min(hi, whi)
                if a <= b:
                    self.flags.append(f"{owner}: the level coping's bed forced the middle line of rise {i} to "
                                      f"{min(max(want, a), b)}")
                    return dict(force={i: min(max(want, a), b)})
            raise Refused(f"{owner}: no course line or rise can take the level coping's bed near {want}")
        _, z, d, t = best
        return dict(C=zp + PARAPET + d, B=z, t=t, delta=d)

    def _coping(self, forced):
        segs = self.runs()
        self.panels_make(segs)
        lid = self.id
        feats, slabs, ceil = [], [], []
        self.features = feats
        # the level runs' tops and beds
        for k, sg in enumerate(segs):
            if sg["kind"] == "level":
                owner = f"{lid}/run-{k}"
                if k == len(segs) - 1:
                    rng = self.stream(f"{lid}/hd-1/top", "cope")
                    sg["C"] = sg["z"] + PARAPET + rng.randint(-COPE_DELTA, COPE_DELTA)
                    sg["B"] = None
                else:
                    r = self._snap_level(sg["z"], owner)
                    if "force" in r:
                        return r["force"]
                    sg.update(r)
        # the raked runs' tops, from the level runs either side (the lane's foot draws its own)
        n_kneel = n_knee = 0
        for k, sg in enumerate(segs):
            if sg["kind"] != "rake":
                continue
            (sa, sb), (za, zb) = sg["s"], sg["z"]
            if k == 0:
                kid = f"{lid}/kneeler-{n_kneel}"
                rng = self.stream(kid, "rake")
                CA = za + PARAPET + rng.randint(-COPE_DELTA, COPE_DELTA)
                t = rng.randint(80, COPE_T[1])
                CB = segs[k + 1]["C"]
                sg["R"] = Rake.square(sa, CA, sb, CB, t)
            else:
                prev = segs[k - 1]
                sg["R"] = Rake.meeting(sa, prev["C"], sb, segs[k + 1]["C"], prev["t"])
                if not COPE_T[0] <= sg["R"].t <= COPE_T[1]:
                    self.flags.append(f"{lid}: a raked run's thickness {sg['R'].t} is outside {COPE_T}")
        # walk the runs: the features at their junctions, the slabs between, the ceiling under them
        x = self.s0
        for k, sg in enumerate(segs):
            if sg["kind"] == "rake":
                R = sg["R"]
                if k == 0:
                    # the lane's kneeler, the wall's end: a level top from the end to where its square face meets
                    # the run's bed on a course line
                    kid = f"{lid}/kneeler-{n_kneel}"
                    n_kneel += 1
                    rng = self.stream(kid, "lay")
                    w0 = rng.randint(*KNEELER_W)
                    best = None
                    for z in self.Lz:
                        sq = R.inv_B(z)
                        sk = sq - R.dx
                        w = sk - self.s0
                        if KNEELER_W[0] - 50 <= w <= KNEELER_W[1] + 70:
                            if best is None or abs(w - w0) < abs(best[1] - w0):
                                best = (z, w, sq, sk)
                    if best is None:
                        raise Refused(f"{kid}: no course line puts the lane kneeler's face on the run's bed")
                    zL, w, sq, sk = best
                    CK = R.C(sk)
                    zb = self._kneeler_bed(CK, zL, sq - self.s0, kid)
                    poly = [[self.s0, zb], [sq, zb], [sq, zL], [sk, CK], [self.s0, CK]]
                    feats.append(dict(id=kid, kind="kneeler", outline=poly, bed=zb, at=sg["s"][0], lane=True,
                                      head=0))
                    ceil.append(dict(kind="level", s=[self.s0, sq], z=zb, owner=kid))
                    start = sq
                    self.head_top = {0: (zb, kid)}
                else:
                    start = sg["start_q"]
                # the knee at the run's top
                nxt = segs[k + 1]
                knid = f"{lid}/knee-{n_knee}"
                n_knee += 1
                rng = self.stream(knid, "lay")
                r0 = rng.randint(*KNEE_RAKE)
                a0 = sg_level_a = nxt.get("knee_a")
                sn = sg["s"][1]
                Bn = R.B(sn)
                cap = Bn - 56
                if nxt.get("B") is not None:
                    cap = min(cap, nxt["B"] - SLIVER)
                back_top = nxt["B"] if nxt.get("B") is not None else nxt["C"]
                best = None
                for z in self.Lz:
                    if z > cap:
                        continue
                    sp1 = R.inv_B(z)
                    st_ = sp1 - R.dx
                    rl = sn - st_
                    if rl < 100 or sp1 - start < COPE_L[0]:
                        continue
                    back = sum(1 for L in self.Lz if z <= L < back_top)
                    cost = 10000 * max(0, back - KNEELER_BACK) + abs(rl - r0)
                    if best is None or cost < best[0]:
                        best = (cost, z, rl, sp1, st_)
                if best is None:
                    raise Refused(f"{knid}: no course line gives the knee a bed under the run")
                if best[0] >= 10000:
                    self.flags.append(f"{knid}: its plumb side rises through {best[0] // 10000 + KNEELER_BACK} courses")
                _, zx, rl, sp1, st_ = best
                # the run's intermediate kneelers (Rivington 1904, p. 54; Mitchell 1902), every 2.4 to 3.6 m of going
                # from the stop below, each its own stone: a level bed on a course line where the rake's bed meets
                # it, a plumb back rising to the next line the rake's bed meets, the coping's section on its top, its
                # faces square to the rake; the run's slabs between, bed point to bed point
                prev = start
                while True:
                    kid = f"{lid}/kneeler-{n_kneel}"
                    rng = self.stream(kid, "lay")
                    d0 = rng.randint(*KNEELER_EVERY)
                    w0 = rng.randint(*KNEELER_MID_W)
                    best = None
                    for i1, z1 in enumerate(self.Lz):
                        sL = R.inv_B(z1)
                        d = sL - prev
                        if not KNEELER_EVERY[0] <= d <= KNEELER_EVERY[1]:
                            continue
                        for i2 in range(i1 + 1, len(self.Lz)):
                            z2 = self.Lz[i2]
                            sR = R.inv_B(z2)
                            w = sR - sL
                            if not KNEELER_MID_W[0] <= w <= KNEELER_MID_W[1] + 100 or sp1 - sR < COPE_L[0]:
                                continue
                            if R.C(sR - R.dx) - z1 >= w:
                                continue                    # wider than it is high
                            cost = abs(d - d0) + abs(w - w0) + 10000 * max(0, i2 - i1 - KNEELER_BACK)
                            if best is None or cost < best[0]:
                                best = (cost, z1, z2, sL, sR, d)
                    if best is None:
                        if sp1 - prev > KNEELER_EVERY[1]:
                            self.flags.append(f"{kid}: a raked stretch of {sp1 - prev} mm from {prev} to the knee takes "
                                              f"no intermediate kneeler (no course lines in reach)")
                        break
                    n_kneel += 1
                    _, z1, z2, sL, sR, d = best
                    poly = [[sL, z1], [sR, z1], [sR, z2], [sR - R.dx, R.C(sR - R.dx)], [sL - R.dx, R.C(sL - R.dx)]]
                    feats.append(dict(id=kid, kind="kneeler", outline=poly, bed=z1, at=sL, mid=True, fromStop=d))
                    self._rake_slabs(R, prev, sL, slabs)
                    ceil.append(dict(kind="rake", s=[prev, sL], R=R, owner=f"{lid}/rake-{k}"))
                    ceil.append(dict(kind="level", s=[sL, sR], z=z1, owner=kid))
                    prev = sR
                # the raked run's slabs, bed point to bed point, from its last stop's face to the knee's
                self._rake_slabs(R, prev, sp1, slabs)
                ceil.append(dict(kind="rake", s=[prev, sp1], R=R, owner=f"{lid}/rake-{k}"))
                # the knee's level top: on a rest the rest's solver gives it; at the wall's end what the topstone leaves
                C = nxt["C"]
                if k + 1 == len(segs) - 1:
                    a = rng.randint(*KNEE_LEVEL)
                    room = self.s1 - sn
                    a = min(max(a, room - TOPSTONE[1]), room - TOPSTONE[0])
                    # the topstone square on the knee's bed where the knee's level top allows it
                    h = C - zx
                    lo_t, hi_t = max(TOPSTONE[0], -(-3 * h // 4), room - KNEE_LEVEL[1]), \
                        min(TOPSTONE[1], 4 * h // 3, room - KNEE_LEVEL[0])
                    if lo_t <= hi_t:
                        a = room - min(max(room - a, lo_t), hi_t)
                    if not KNEE_LEVEL[0] <= a <= KNEE_LEVEL[1]:
                        self.flags.append(f"{knid}: its level top {a} mm is outside {KNEE_LEVEL}")
                    snR = sn + a
                    poly = [[sp1, zx], [snR, zx], [snR, C], [sn, C], [st_, R.C(st_)]]
                    feats.append(dict(id=knid, kind="knee", outline=poly, bed=zx, at=sn))
                    ceil.append(dict(kind="level", s=[sp1, snR], z=zx, owner=knid))
                    # the topstone at the end, square: its bed the line giving it a height nearest its length
                    tid = f"{lid}/hd-1/top"
                    Lt = self.s1 - snR
                    zt = zx if 3 * (C - zx) <= 4 * Lt <= 16 * (C - zx) // 3 else self._bed_for(C, zx, Lt, COPE_T[1], tid)
                    feats.append(dict(id=tid, kind="topstone", outline=[[snR, zt], [self.s1, zt], [self.s1, C],
                                                                        [snR, C]], bed=zt, head=1))
                    ceil.append(dict(kind="level", s=[snR, self.s1], z=zt, owner=tid))
                    self.head_top[1] = (zt, tid)
                else:
                    nxt["knee"] = dict(id=knid, sp1=sp1, st=st_, zx=zx, sn=sn, rng=rng)
            else:
                if k == len(segs) - 1:
                    continue           # (the last level run: laid with the knee before it)
                # a level run before a raked one: its kneeler at the break; on a rest a knee before it, at the wall's
                # foot a topstone
                kid = f"{lid}/kneeler-{n_kneel}"
                n_kneel += 1
                rng = self.stream(kid, "lay")
                b0 = rng.randint(*KNEELER_W)
                sk = sg["s"][1]
                R = segs[k + 1]["R"]
                sq = R.inv_B(sg["B"])
                C, Bl = sg["C"], sg["B"]
                if k == 0:
                    tid = f"{lid}/hd-0/top"
                    trng = self.stream(tid, "lay")
                    Lt0 = trng.randint(250, 400)
                    left_kind, left_len0, left_rng = "topstone", Lt0, (TOPSTONE[0], 400)
                    ib = self.Lz.index(Bl)
                    if ib >= KNEELER_BACK:
                        h1, h2 = C - self.Lz[ib - 1], C - self.Lz[ib - KNEELER_BACK]
                        lo_t, hi_t = max(TOPSTONE[0], -(-3 * h1 // 4)), min(400, 4 * h2 // 3)
                        if lo_t <= hi_t:
                            left_rng = (lo_t, hi_t)
                            left_len0 = min(max(Lt0, lo_t), hi_t)
                    x0 = self.s0
                else:
                    kn = sg["knee"]
                    a0 = kn["rng"].randint(*KNEE_LEVEL)
                    left_kind, left_len0, left_rng = "knee", a0, KNEE_LEVEL
                    x0 = kn["sn"]
                total = sk - x0
                a, bb = self._rest_split(total, left_len0, left_rng, b0, KNEELER_W, sg)
                xl, xr = x0 + a, sk - bb
                if left_kind == "topstone":
                    zt = self._square_bed(C, Bl, a, tid)
                    feats.append(dict(id=tid, kind="topstone", outline=[[self.s0, zt], [xl, zt], [xl, C], [self.s0, C]],
                                      bed=zt, head=0))
                    ceil.append(dict(kind="level", s=[self.s0, xl], z=zt, owner=tid))
                    self.head_top = {0: (zt, tid)}
                else:
                    kn = sg["knee"]
                    poly = [[kn["sp1"], kn["zx"]], [xl, kn["zx"]], [xl, C], [kn["sn"], C],
                            [kn["st"], segs[k - 1]["R"].C(kn["st"])]]
                    feats.append(dict(id=kn["id"], kind="knee", outline=poly, bed=kn["zx"], at=kn["sn"]))
                    ceil.append(dict(kind="level", s=[kn["sp1"], xl], z=kn["zx"], owner=kn["id"]))
                # the level slabs between
                if xr > xl:
                    self._level_slabs(xl, xr, Bl, C, slabs)
                    ceil.append(dict(kind="level", s=[xl, xr], z=Bl, owner="coping"))
                # the kneeler: level bed on a line, its top level to the break, its face square to the rake
                zb = self._kneeler_bed(C, Bl, sq - xr, kid)
                poly = [[xr, zb], [sq, zb], [sq, Bl], [sk, C], [xr, C]]
                feats.append(dict(id=kid, kind="kneeler", outline=poly, bed=zb, at=sk))
                ceil.append(dict(kind="level", s=[xr, sq], z=zb, owner=kid))
                segs[k + 1]["start_q"] = sq
        self.slabs = slabs
        self.ceiling = ceil
        self.segs = segs
        # the ceiling is contiguous from end to end
        for p, q in zip(ceil, ceil[1:]):
            if p["s"][1] != q["s"][0]:
                raise Refused(f"{lid}: the coping's pieces do not meet at {p['s'][1]} / {q['s'][0]}")
        return None

    def _square_bed(self, top, under, length, owner):
        """A topstone's bed: a course line under `under`, the stone square (its length 0.75 to 1.33 its height),
        nearest its length, its plumb side through at most KNEELER_BACK courses under `under` where the lines allow."""
        i = self.Lz.index(under)
        best = None
        for j in range(i - 1, -1, -1):
            h = top - self.Lz[j]
            if not 3 * h <= 4 * length <= 16 * h // 3:
                continue
            cost = 10000 * max(0, i - j - KNEELER_BACK) + abs(h - length)
            if best is None or cost < best[0]:
                best = (cost, self.Lz[j])
        if best is None:
            return self._bed_for(top, under - COURSE[0], length, top - under + COURSE[0], owner)
        if best[0] >= 10000:
            self.flags.append(f"{owner}: its plumb side rises through {best[0] // 10000 + KNEELER_BACK} courses")
        return best[1]

    def _kneeler_bed(self, top, under, width, owner):
        """A kneeler's bed: a course line under `under` (the course line its plumb side rises to), the stone wider than
        high, its height nearest three quarters of its width, its plumb side through at most KNEELER_BACK courses
        where the lines allow (SN2's kneeler, SN10's two courses)."""
        i = self.Lz.index(under)
        best = None
        for j in range(i - 1, -1, -1):
            z = self.Lz[j]
            if top - z >= width:
                break
            cost = 10000 * max(0, i - j - KNEELER_BACK) + abs(4 * (top - z) - 3 * width)
            if best is None or cost < best[0]:
                best = (cost, z)
        if best is None:
            self.flags.append(f"{owner}: no course line under {under} leaves it wider than high; one course under it")
            return self.Lz[i - 1]
        if best[0] >= 10000:
            self.flags.append(f"{owner}: its plumb side rises through {best[0] // 10000 + KNEELER_BACK} courses")
        return best[1]

    def _bed_for(self, top, cap, length, least, owner):
        """A feature's bed: the course line at most `cap`, giving a height of at least `least`, nearest to `length`
        (a square stone)."""
        best = None
        for z in self.Lz:
            if z > cap or top - z < least or top - z > 2 * KNEELER_W[1]:
                continue
            if best is None or abs((top - z) - length) < abs((top - best) - length):
                best = z
        if best is None:
            raise Refused(f"{owner}: no course line gives it a bed")
        return best

    def _rest_split(self, total, a0, arange, b0, brange, sg):
        """A level run's length between its left feature (a knee's level top or a topstone) and its kneeler: either both
        meet, or the slabs between are at least a slab long."""
        best = None
        for a in range(arange[0], arange[1] + 1, 1):
            for b in (brange[0], brange[1], min(max(b0, brange[0]), brange[1]), total - a - COPE_L[0], total - a):
                if not brange[0] <= b <= brange[1]:
                    continue
                r = total - a - b
                if r != 0 and r < COPE_L[0]:
                    continue
                cost = abs(a - a0) + abs(b - b0)
                if best is None or cost < best[0]:
                    best = (cost, a, b)
        if best is None:
            raise Refused(f"{self.id}: a level run of {total} mm takes no knee or topstone, kneeler and slabs")
        return best[1], best[2]

    def _rake_slabs(self, R, start, end, slabs):
        """Raked copings from bed point `start` to `end`: joints square to the rake; a 1961 edge takes a joint."""
        cuts = [start] + [e for e in self.edges if start + 1 < e < end - 1] + [end]
        for a, b in zip(cuts, cuts[1:]):
            pn = self.panel_at((a + b) // 2)
            rng = self.stream(pn["id"], "cope", "rake", "first" if a == start else "after", a)
            lo = COPE_L[0] if b - a >= COPE_L[0] else max(SLIVER * 4, b - a)
            J = fill_run(a, b, lo, COPE_L[1], [], lambda i: rng.randint(*COPE_L))
            if J is None:
                J = [a, b]
                self.flags.append(f"{pn['id']}: a raked coping {b - a} mm long, outside {COPE_L}")
            for p, q in zip(J, J[1:]):
                slabs.append(dict(panel=pn["id"], kind="coping", rake=True,
                                  outline=[[p, R.B(p)], [q, R.B(q)], [q - R.dx, R.C(q - R.dx)],
                                           [p - R.dx, R.C(p - R.dx)]]))

    def _level_slabs(self, a, b, Bl, C, slabs):
        pn = self.panel_at((a + b) // 2)
        rng = self.stream(pn["id"], "cope", "level", a)
        J = fill_run(a, b, COPE_L[0], COPE_L[1], [], lambda i: rng.randint(*COPE_L))
        if J is None:
            J = [a, b]
            self.flags.append(f"{pn['id']}: a level coping {b - a} mm long, outside {COPE_L}")
        for p, q in zip(J, J[1:]):
            slabs.append(dict(panel=pn["id"], kind="coping", rake=False, outline=[[p, Bl], [q, Bl], [q, C], [p, C]]))

    def ceiling_at(self, s):
        for c in self.ceiling:
            if c["s"][0] <= s <= c["s"][1]:
                return c["R"].B(s) if c["kind"] == "rake" else c["z"]
        return None

    # ---- footings
    def footings(self):
        S, T = self.S, self.T
        ff = [(self.s0, S[0], T[0], "lane" if self.fl["start"] == 0 else "turn")]
        for i in range(len(S)):
            ff.append((S[i], S[i + 1] if i + 1 < len(S) else self.s1, T[i + 1], self.fl["steps"][i]["id"]))
        self.foot = {"stair": [(a, b, z, ref) for a, b, z, ref in ff if b > a]}
        g = self.f["ground"]
        cells = []
        for (sa, za), (sb, zb) in zip(g, g[1:]):
            m = min(za, zb)
            idx = max([i for i, z in enumerate(self.Lz) if z <= m], default=0)
            cells.append((sa, sb, idx))
        n = len(cells)
        per = FOOT_TREAD // GRID
        f = [min(cells[j][2] + abs(i - j) // per for j in range(n)) for i in range(n)]
        fb = []
        for (sa, sb, _), fi in zip(cells, f):
            if fb and fb[-1][2] == self.Lz[fi]:
                fb[-1] = (fb[-1][0], sb, fb[-1][2], "ground")
            else:
                fb.append((sa, sb, self.Lz[fi], "ground"))
        fb[0] = (self.s0, fb[0][1], fb[0][2], "ground")
        fb[-1] = (fb[-1][0], self.s1, fb[-1][2], "ground")
        self.foot["bank"] = fb

    def foot_at(self, face, s):
        for a, b, z, _ in self.foot[face]:
            if a <= s < b:
                return z
        return self.foot[face][-1][2]

    # ---- a course's free lengths on a face, before anything is laid in it
    def band_region(self, m, face):
        """Course m's lengths on a face: where it stands over the footing and under the coping and its features.
        Each run [a, b] carries its ends' causes and, when it starts under the rake, the rake's cut (sTop)."""
        L, L2 = self.Lz[m], self.Lz[m + 1]
        pieces = []
        for c in self.ceiling:
            p0, p1 = c["s"]
            if c["kind"] == "level":
                if c["z"] >= L2:
                    pieces.append([p0, p1, None, c["owner"], c["owner"]])
                elif c["z"] > L:
                    self.flags.append(f"{self.id}: course {m} meets {c['owner']}'s bed {c['z']} inside it")
            else:
                R = c["R"]
                if R.B(p1) <= L:
                    continue
                if R.B(p0) > L:
                    a, top = p0, (None if R.B(p0) >= L2 else R.inv_B(L2))
                    if top is not None:
                        self.flags.append(f"{self.id}: course {m} starts under the rake at {p0} part-high")
                else:
                    a = R.inv_B(L)
                    if a >= p1:
                        continue
                    top = R.inv_B(L2)
                    if top > p1:
                        self.flags.append(f"{self.id}: course {m} is cut by the rake to its run's end at {p1} (a wedge)")
                        top = p1
                pieces.append([a, p1, top, "rake" if a > p0 or R.B(p0) == L else c["owner"], c["owner"]])
        runs = []
        for pc in pieces:
            if runs and runs[-1][1] == pc[0] and pc[2] is None:
                runs[-1][1] = pc[1]
                runs[-1][4] = pc[4]
            else:
                runs.append(list(pc))
        # the left end's cause: the piece before (the feature it abuts), the right end's: the piece after
        out = []
        for a, b, top, lt, rt in runs:
            lend = dict(type="rake") if lt == "rake" else self._end_at(a, "left")
            rend = self._end_at(b, "right")
            out.append(dict(a=a, b=b, sTop=top, l=lend, r=rend))
        # the footing: where the course stands on it (the footing at or under its bed), as whole stretches
        stand = iv_union([(a, b - 1) for a, b, z, _ in self.foot[face] if z <= L])
        res = []
        for lo0, hi0 in stand:
            lo1, hi1 = lo0, hi0 + 1
            for run in out:
                lo, hi = max(lo1, run["a"]), min(hi1, run["b"])
                if lo >= hi:
                    continue
                l = run["l"] if lo == run["a"] else self._foot_end(face, lo, "left")
                r = run["r"] if hi == run["b"] else self._foot_end(face, hi, "right")
                top = run["sTop"] if lo == run["a"] else None
                if lo != run["a"] and run["sTop"] is not None and lo < run["sTop"]:
                    top = run["sTop"]
                    l = dict(type="ground-under-rake", ref="ground", plumb=self.ceiling_at(lo) - L)
                    self.flags.append(f"{self.id} {face}: course {m} rises out of its footing under the rake at {lo}")
                res.append(dict(a=lo, b=hi, sTop=top, l=l, r=r))
        res.sort(key=lambda d: d["a"])
        return res

    def _end_at(self, s, which):
        if s <= self.s0 or s >= self.s1:
            return dict(type="end")
        for c in self.ceiling:
            if (which == "left" and c["s"][1] == s) or (which == "right" and c["s"][0] == s):
                if c["owner"] != "coping" and not c["owner"].startswith(self.id + "/rake"):
                    return dict(type="feature", ref=c["owner"])
        for c in self.ceiling:
            if c["s"][0] <= s <= c["s"][1] and c["owner"] != "coping" and not c["owner"].startswith(self.id + "/rake"):
                return dict(type="feature", ref=c["owner"])
        return dict(type="feature", ref="coping")

    def _foot_end(self, face, s, which):
        if face == "bank":
            return dict(type="ground", ref="ground")
        # the stair's face: the step whose end rises over the course at s
        for i, Si in enumerate(self.S):
            if Si == s:
                y = s if which == "right" else s - 1
                return dict(type="step", ref=step_end_id(self.steps_out, self.fl["steps"][i]["id"], self.side, s))
        return dict(type="step", ref="step")


# ---------------------------------------------------------------------------------------------------------------
# Laying a line's courses

def lay_line(line, flight, steps_out, seed, reseed=None):
    W = Line(line, flight, steps_out, seed, reseed)
    W.coping()
    W.footings()
    # (panels need no clear zone: a tooth reaches at most 90 mm past its boundary and a stone is at least 180 mm long,
    # so the free joints of two panels toothed together stand at least 180 mm apart, beyond any lap; only where a
    # boundary takes no tooth does one panel's stone cross it, and the independence test counts what that couples)
    clear = []
    nb = len(W.Lz) - 1
    H = [W.Lz[m + 1] - W.Lz[m] for m in range(nb)]
    lid = W.id
    regions = {f: [W.band_region(m, f) for m in range(nb)] for f in FACES}
    carved = {f: [[] for _ in range(nb)] for f in FACES}     # stones laid first in each course: (x0, x1, id)
    placed = []                                               # the stones laid first

    def carve(face, m, x0, x1, sid):
        carved[face][m].append((x0, x1, sid))

    # ---- the heads: ties and runners alternating, two courses each, under the end's topstone or kneeler
    def rooms(face, spans, e):
        """The length each spanned course has at the wall's end on a face, with its height (none where hidden)."""
        out = []
        for m in spans:
            for run in regions[face][m]:
                if (e == 0 and run["a"] == W.s0) or (e == 1 and run["b"] == W.s1):
                    out.append((run["b"] - run["a"], H[m]))
        return out

    def head_len(drawn, nominal, wide, room_list, sid, avoid=()):
        """A head stone's length: the drawn one if it leaves every spanned course either nothing or a whole stone
        beside it, and its inner end a lap from those of the stones under and over it (`avoid`: (length, lap)), else
        the nearest that does, first in its own range, then in any a course takes; flagged if so."""
        def fits(x):
            return all(x <= r_ and fillable(r_ - x, h_) for r_, h_ in room_list) and \
                all(abs(x - y) >= lp for y, lp in avoid)
        for lo_, hi_ in (nominal, wide):
            ok = [x for x in range(lo_, hi_ + 1) if fits(x)]
            if ok:
                x = min(ok, key=lambda v: (abs(v - drawn), v))
                if (lo_, hi_) != nominal:
                    W.flags.append(f"{sid}: {x} mm, outside its range {nominal}, to leave whole stones beside it")
                return x
        x = min([drawn] + [r_ for r_, _ in room_list])
        W.flags.append(f"{sid}: no length leaves whole stones beside it (rooms {room_list}); {x} mm")
        return x

    for e, s_end in ((0, W.s0), (1, W.s1)):
        top_z, top_id = W.head_top[e]
        top_ft = next(ft for ft in W.features if ft["id"] == top_id)
        top_len = max(abs(p_[0] - s_end) for p_ in top_ft["outline"] if p_[1] == top_z)   # its bed's length
        prev_len = {f: None for f in FACES}
        base = min(W.foot_at("stair", s_end if e == 0 else s_end - 1), W.foot_at("bank", s_end if e == 0 else s_end - 1))
        i0, i1 = W.Lz.index(base), W.Lz.index(top_z)
        hid = f"{lid}/hd-{e}"
        tie_first = HS.h(seed, hid, "order") % 2 == 0
        # two courses a stone, counted from the top down, so a single course left over is the deepest, at the foot
        pairs, j = [], i1
        while j > i0:
            pairs.append((max(j - 2, i0), j))
            j -= 2
        for k, (i, j) in enumerate(reversed(pairs)):
            h = W.Lz[j] - W.Lz[i]
            rng = HS.Stream(seed, f"{hid}/st-{k}", "lay")
            tie = (k % 2 == 0) == tie_first
            spans = list(range(i, j))
            hi_ = longest(h)
            avoid = [(top_len, lap_of(H[j]) if j < nb else LAP_MIN)] if j == i1 else []
            avoid_f = {f: avoid + ([(prev_len[f], lap_of(H[i]))] if prev_len[f] is not None else []) for f in FACES}
            if tie:
                sid = f"{hid}/st-{k}"
                Lh = head_len(rng.randint(*HEAD_TIE), HEAD_TIE, (STONE[0], hi_),
                              rooms("stair", spans, e) + rooms("bank", spans, e), sid,
                              avoid_f["stair"] + avoid_f["bank"])
                prev_len = {f: Lh for f in FACES}
                x0, x1 = (s_end, s_end + Lh) if e == 0 else (s_end - Lh, s_end)
                placed.append(dict(id=sid, kind="head", role="tie", faces=list(FACES), bands=spans,
                                   outline=[[x0, W.Lz[i]], [x1, W.Lz[i]], [x1, W.Lz[j]], [x0, W.Lz[j]]]))
                for f in FACES:
                    for m in spans:
                        carve(f, m, x0, x1, sid)
            else:
                for f in FACES:
                    sid = f"{hid}/st-{k}/{f}"
                    nominal = (min(HEAD_RUN[0], hi_), hi_)
                    Lh = head_len(rng.randint(*nominal), nominal, (STONE[0], hi_), rooms(f, spans, e), sid, avoid_f[f])
                    prev_len[f] = Lh
                    if Lh < HEAD_RUN[0]:
                        W.flags.append(f"{sid}: a runner {Lh} mm, under the {HEAD_RUN[0]} a runner should be")
                    x0, x1 = (s_end, s_end + Lh) if e == 0 else (s_end - Lh, s_end)
                    placed.append(dict(id=sid, kind="head", role="runner", faces=[f], bands=spans,
                                       outline=[[x0, W.Lz[i]], [x1, W.Lz[i]], [x1, W.Lz[j]], [x0, W.Lz[j]]]))
                    for m in spans:
                        carve(f, m, x0, x1, sid)

    def free_runs(face, m):
        """Course m's runs on a face less what is laid first in it."""
        out = []
        for run in regions[face][m]:
            pieces = [dict(run)]
            for x0, x1, sid in sorted(carved[face][m]):
                nxt = []
                for p in pieces:
                    if x1 <= p["a"] or x0 >= p["b"]:
                        nxt.append(p)
                        continue
                    if x0 > p["a"]:
                        q = dict(p)
                        q["b"], q["r"] = x0, dict(type="stone", ref=sid)
                        nxt.append(q)
                    if x1 < p["b"]:
                        q = dict(p)
                        q["a"], q["l"], q["sTop"] = x1, dict(type="stone", ref=sid), None
                        if p["sTop"] is not None and x1 < p["sTop"] + SLIVER:
                            W.flags.append(f"{sid}: laid inside the rake's cut of course {m}")
                        nxt.append(q)
                pieces = nxt
            out += pieces
        return [p for p in out if p["b"] > p["a"]]

    def where(face, m, s):
        for p in free_runs(face, m):
            if p["a"] <= s < p["b"]:
                return p
        return None

    def laps_clear(m, ends, faces):
        """Whether a stone laid first in course m keeps its free ends (those not against a run's end) a lap from the
        ends of the stones and features laid first in the courses above and below it (the fill keeps its own joints
        clear of both)."""
        for f in faces:
            for mm, lap in ((m - 1, lap_of(H[m])), (m + 1, lap_of(H[m + 1]) if m + 1 < nb else 0)):
                if not 0 <= mm < nb:
                    continue
                for p in free_runs(f, mm):
                    for side, y in (("l", p["a"]), ("r", p["b"])):
                        if p[side]["type"] in ("stone", "feature") and any(abs(x - y) < lap for x in ends):
                            return False
        return True

    # ---- the fallen stones the facts give (the stair's face; a mortared stone holds)
    reb = line.get("rebuilt")
    fall_report = []
    for fp in line.get("falls", []):
        s, z = fp["s"], fp["z"]
        if fp["held"]:
            fall_report.append(dict(s=s, z=z, result="held (cement: the 1961 panel or the patched hole)"))
            continue
        m = max([i for i in range(nb) if W.Lz[i] <= z], default=None)
        if m is None or m >= nb:
            fall_report.append(dict(s=s, z=z, result="outside the courses"))
            continue
        p = where("stair", m, s)
        if p is None:
            fall_report.append(dict(s=s, z=z, result=f"in course {m} where a feature or head stands: not placed"))
            continue
        pn = W.panel_at(s)
        rng = W.stream(pn["id"], "fallen", s // 1)  # (the fall point is a fact; its place keys only its own draw)
        h = H[m]
        L0 = rng.randint(STONE[0], longest(h))
        o0 = rng.randint(0, L0 - 1)
        lo = p["a"]
        if p["sTop"] is not None:
            lo = max(p["a"] + STONE[0], p["sTop"] + SLIVER)
        best = None
        for Lf in range(STONE[0], longest(h) + 1):
            for x0 in range(max(s - Lf + 1, p["a"]), min(s, p["b"] - Lf) + 1):
                x1 = x0 + Lf
                if x0 == p["a"]:
                    left_ok = p["sTop"] is None or x1 >= p["sTop"] + SLIVER     # (the cut stone itself may fall)
                else:
                    left_ok = x0 >= lo and fillable(x0 - p["a"], h)
                if not left_ok or not fillable(p["b"] - x1, h):
                    continue
                if not laps_clear(m, [x for x, e in ((x0, p["a"]), (x1, p["b"])) if x != e], ["stair"]):
                    continue
                cost = abs(Lf - L0) + abs((s - x0) - o0)
                if best is None or cost < best[0]:
                    best = (cost, x0, x1)
        if best is None:
            fall_report.append(dict(s=s, z=z, result=f"no room for a fallen stone in course {m}: not placed"))
            continue
        _, x0, x1 = best
        sid_tmp = f"{pn['id']}/stair/co-{m}/fallen-{len(fall_report)}"
        placed.append(dict(id=sid_tmp, kind="face", faces=["stair"], bands=[m], fallen=True, panel=pn["id"],
                           outline=_band_outline(W, m, x0, x1, p), fact=dict(s=s, z=z)))
        carve("stair", m, x0, x1, sid_tmp)
        fall_report.append(dict(s=s, z=z, result=f"fell: course {m}, {x0} to {x1}", id=sid_tmp))

    # ---- the through stones: about one a metre in each panel, in the course nearest the face's middle height
    through_report = []
    for pn in W.panels:
        lo, hi = pn["s"]
        rng = W.stream(pn["id"], "throughs")
        xc = lo + rng.randint(*THROUGH_FIRST)
        j = 0
        while xc < hi - THROUGH_CLEAR:
            Lt = rng.randint(*THROUGH)
            x0 = xc - Lt // 2
            x1 = x0 + Lt
            done = False
            if x0 >= lo + THROUGH_CLEAR and x1 <= hi - THROUGH_CLEAR:
                ff, cc = W.foot_at("stair", xc), W.ceiling_at(xc)
                if cc is not None:
                    zmid = (ff + cc) // 2
                    order = sorted(range(nb), key=lambda m: (abs((W.Lz[m] + W.Lz[m + 1]) // 2 - zmid), m))[:4]
                    for m in order:
                        ok = False
                        Lm = min(Lt, longest(H[m]))
                        if Lm < THROUGH[0]:
                            continue
                        x0, x1 = xc - Lm // 2, xc - Lm // 2 + Lm
                        for dx in sorted(range(-150, 151, 5), key=lambda v: (abs(v), v)):
                            ok = True
                            for f in FACES:
                                p = where(f, m, xc)
                                if p is None or not (p["a"] <= x0 + dx and x1 + dx <= p["b"]) or \
                                        not fillable(x0 + dx - p["a"], H[m]) or not fillable(p["b"] - x1 - dx, H[m]) or \
                                        (p["sTop"] is not None and x0 + dx < p["sTop"] + SLIVER):
                                    ok = False
                                    break
                            if ok and not laps_clear(m, [x0 + dx, x1 + dx], FACES):
                                ok = False
                            if ok:
                                x0, x1 = x0 + dx, x1 + dx
                                break
                        if ok:
                            sid = f"{pn['id']}/co-{m}/th-{j}"
                            placed.append(dict(id=sid, kind="through", faces=list(FACES), bands=[m], panel=pn["id"],
                                               outline=[[x0, W.Lz[m]], [x1, W.Lz[m]], [x1, W.Lz[m + 1]],
                                                        [x0, W.Lz[m + 1]]]))
                            for f in FACES:
                                carve(f, m, x0, x1, sid)
                            j += 1
                            done = True
                            break
            if not done:
                through_report.append(dict(panel=pn["id"], at=xc, result="no course with room on both faces"))
            xc += rng.randint(*THROUGH_EVERY)

    # ---- the free runs, and the joints every course must take: the panels' teeth and the 1961 edges
    runs = {f: [free_runs(f, m) for m in range(nb)] for f in FACES}
    fixed = {f: [[] for _ in range(nb)] for f in FACES}      # vertical joints fixed before the fill, per course

    def is_joint(end):
        return end["type"] not in ("end", "rake")

    for f in FACES:
        for m in range(nb):
            for p in runs[f][m]:
                if is_joint(p["l"]):
                    fixed[f][m].append(p["a"])
                if is_joint(p["r"]):
                    fixed[f][m].append(p["b"])
            # (a stone laid first against a feature leaves no run between them, but their joint is fixed all the same)
            outer = set()
            for r_ in regions[f][m]:
                if r_["l"]["type"] in ("end", "rake"):
                    outer.add(r_["a"])
                if r_["r"]["type"] in ("end", "rake"):
                    outer.add(r_["b"])
            for x0, x1, _ in carved[f][m]:
                fixed[f][m] += [x for x in (x0, x1) if x not in outer]
            fixed[f][m] = sorted(set(fixed[f][m]))
    cut_report = []

    def feasible(a, b, m, sTop):
        """Whether the fill can lay [a, b] in course m in whole stones, its free joints clear of the boundaries."""
        first = (max(STONE[0], sTop + SLIVER - a), longest(H[m])) if sTop is not None else None
        return fill_run(a, b, STONE[0], longest(H[m]), clear, lambda i: STONE[0], first) is not None

    # each course, left to right: a 1961 edge takes a straight joint where it can, a feature's boundary a tooth, each
    # only where the fill can lay both sides
    cuts = {f: [[] for _ in range(nb)] for f in FACES}
    segs = {f: [[] for _ in range(nb)] for f in FACES}
    bl = sorted([(e_, "edge") for e_ in W.edges] + [(sb, "tooth") for sb in W.boundaries])
    for f in FACES:
        for m in range(nb):
            pieces = sorted([dict(p) for p in runs[f][m]], key=lambda d: d["a"])
            for bi, (sb, kind) in enumerate(bl):
                k_ = next((k for k, q in enumerate(pieces) if q["a"] < sb < q["b"]), None)
                if k_ is None:
                    continue
                p = pieces[k_]
                more = any(p["a"] < sb2 < p["b"] for sb2, _ in bl[bi + 1:])
                if kind == "edge":
                    cands = [sb]
                else:
                    ti = W.boundaries.index(sb)
                    par = HS.h(seed, lid, "tooth", ti) % 2
                    d0 = HS.between(HS.h(seed, lid, "tooth", ti, f, m), *TOOTH)
                    sg = 1 if (m + par) % 2 == 0 else -1
                    cands = [sg * d0] + [sg * d for d in range(TOOTH[0], TOOTH[1] + 1) if d != d0] + \
                            [-sg * d for d in range(TOOTH[0], TOOTH[1] + 1)]
                    cands = [sb + d for d in cands]
                got = None
                for x in cands:
                    if kind == "tooth":
                        if m > 0 and any(abs(x - y) < lap_of(H[m]) for y in fixed[f][m - 1] + cuts[f][m - 1]):
                            continue
                        if m + 1 < nb and any(abs(x - y) < lap_of(H[m + 1]) for y in fixed[f][m + 1]):
                            continue
                    if not feasible(p["a"], x, m, p["sTop"]):
                        continue
                    if (more and p["b"] - x < STONE[0]) or (not more and not feasible(x, p["b"], m, None)):
                        continue
                    got = x
                    break
                if got is None:
                    what = "the 1961 edge" if kind == "edge" else "the boundary"
                    cut_report.append(f"{lid} {f} course {m}: {what} at {sb} takes no {'joint' if kind == 'edge' else 'tooth'}"
                                      f" (no place the fill can lay both sides of, clear of the joints above and below); "
                                      f"the stone across it is the panel's that holds its middle")
                    continue
                left, right = dict(p), dict(p)
                left["b"], left["r"] = got, dict(type=kind, ref=None)
                right["a"], right["l"], right["sTop"] = got, dict(type=kind, ref=None), None
                pieces[k_:k_ + 1] = [left, right]
                cuts[f][m].append(got)
                fixed[f][m].append(got)
            segs[f][m] = pieces

    # ---- the fill: each course from the foot, each free length by choosing its stones' lengths
    stones = list(placed)
    joints = {f: [[] for _ in range(nb)] for f in FACES}
    fill_report = []
    for f in FACES:
        for m in range(nb):
            h = H[m]
            lapm = lap_of(h)
            win = []
            if m > 0:
                win += [(y - lapm, y + lapm) for y in joints[f][m - 1]]
            if m + 1 < nb:
                lu = lap_of(H[m + 1])
                win += [(y - lu, y + lu) for y in fixed[f][m + 1]]
            ordinal = {}
            for p in sorted(segs[f][m], key=lambda d: d["a"]):
                a, b = p["a"], p["b"]
                pn = W.panel_at((a + b) // 2)
                o = ordinal.get(pn["id"], 0)
                ordinal[pn["id"]] = o + 1
                rng = W.stream(pn["id"], f, "co", m, "lay", o)
                lmax = longest(h)
                first = None
                if p["sTop"] is not None:
                    first = (max(STONE[0], p["sTop"] + SLIVER - a), lmax)
                if p["l"]["type"] == "ground-under-rake":
                    pass
                last = None
                if pn["work"] == "1961" and reb:
                    ls = LONG_SHORT[m % 2]
                    if p["l"]["type"] == "edge" and first is None:
                        first = (ls[0], min(ls[1], lmax)) if ls[0] <= lmax else (min(ls[0], lmax), lmax)
                    if p["r"]["type"] == "edge":
                        ls2 = LONG_SHORT[(m + 1) % 2]
                        last = (ls2[0], min(ls2[1], lmax)) if ls2[0] <= lmax else (min(ls2[0], lmax), lmax)
                tgt = lambda i, rng=rng, lmax=lmax: rng.randint(STONE[0], lmax)  # noqa: E731
                cut = (max(STONE[0], p["sTop"] + SLIVER - a), lmax) if p["sTop"] is not None else None
                below = [(y - lapm, y + lapm) for y in joints[f][m - 1]] if m > 0 else []
                J, how = None, None
                for how_, lmin_, win_, first_, last_ in (
                        ("bond", STONE[0], win + clear, first, last),
                        ("bond, the 1961 long-and-short end dropped", STONE[0], win + clear, cut, None),
                        ("bond below only", STONE[0], below + clear, cut, None),
                        ("no bond", STONE[0], clear, cut, None),
                        ("stones under 180 mm, bonded", SHORT, win + clear, cut, None),
                        ("stones under 180 mm", SHORT, clear, cut, None)):
                    if how_ == "bond, the 1961 long-and-short end dropped" and first == cut and last is None:
                        continue
                    J = fill_run(a, b, lmin_, lmax, win_, tgt, first_, last_)
                    if J is not None:
                        how = how_
                        break
                if J is None:
                    J = fill_run(a, b, SLIVER, max(lmax, b - a), [], tgt, None, None)
                    how = "lengths relaxed"
                if J is None:
                    J = [a, b]
                    how = "one piece"
                if how != "bond":
                    fill_report.append(dict(line=lid, face=f, course=m, a=a, b=b, h=h, how=how, l=p["l"]["type"],
                                            r=p["r"]["type"], sTop=p["sTop"]))
                for k, (x0, x1) in enumerate(zip(J, J[1:])):
                    q = dict(p)
                    q["a"], q["b"] = x0, x1
                    q["sTop"] = p["sTop"] if k == 0 else None
                    st = dict(id=None, kind="face", faces=[f], bands=[m], panel=pn["id"], outline=_band_outline(W, m, x0, x1, q),
                              seg=(p["a"], p["b"]))
                    if how != "bond":
                        st["relaxed"] = how
                    stones.append(st)
                joints[f][m] += [x for x in J[1:-1]] + ([a] if is_joint(p["l"]) else []) + ([b] if is_joint(p["r"]) else [])
            joints[f][m] = sorted(set(joints[f][m]))

    # ---- the fall goes on: a stone whose bed lay all but wholly over a fallen one falls too
    changed = True
    while changed:
        changed = False
        gone = [st for st in stones if st.get("fallen")]
        for st in stones:
            if st.get("fallen") or st["kind"] != "face" or "stair" not in st["faces"] or st.get("panel") is None:
                continue
            if W.panel_at(_xs(st)[0])["work"] == "1961":
                continue
            m = st["bands"][0]
            x0, x1 = _xs(st)
            lost = sum(max(0, min(x1, _xs(g)[1]) - max(x0, _xs(g)[0])) for g in gone if g["bands"][-1] == m - 1)
            if lost * 10 > 9 * (x1 - x0):
                st["fallen"] = True
                st["fallenBy"] = "its bed lost"
                changed = True

    # ---- ids: a stone's place counts along its course in its panel and face
    order = {}
    for st in sorted([s for s in stones if s["kind"] == "face"], key=lambda s: (s["panel"], s["faces"][0], s["bands"][0],
                                                                               _xs(s)[0])):
        k = (st["panel"], st["faces"][0], st["bands"][0])
        j = order.get(k, 0)
        order[k] = j + 1
        old = st.get("id")
        st["id"] = f"{st['panel']}/{st['faces'][0]}/co-{st['bands'][0]}/sp-{j}"
        for fr in fall_report:
            if fr.get("id") == old and old is not None:
                fr["id"] = st["id"]
    cop = {}
    for sl in W.slabs:
        c = cop.get(sl["panel"], 0)
        cop[sl["panel"]] = c + 1
        stones.append(dict(id=f"{sl['panel']}/cp-{c}", kind="coping", faces=list(FACES), bands=[], panel=sl["panel"],
                           outline=sl["outline"], rake=sl["rake"]))
    for ft in W.features:
        stones.append(dict(id=ft["id"], kind=ft["kind"], faces=list(FACES), bands=_bands_of(W, ft["outline"]),
                           outline=ft["outline"], lane=ft.get("lane", False)))
    # the step ends, as the wall's stair face sees them
    cells = []
    for st in steps_out["steps"]:
        rows = st["rows"] if st.get("rest") else [dict(y=st["y"])]
        for r_ in rows:
            y0, y1 = r_["y"]
            cells.append(dict(id=step_end_id(steps_out, st["id"], W.side, y0), outline=[[y0, st["z"][0]], [y1, st["z"][0]],
                                                                                      [y1, st["z"][1]],
                                                                                      [y0, st["z"][1]]]))
    for st in stones:
        st.pop("seg", None)
        if "panel" in st and st["panel"] is None:
            st.pop("panel")
    out = dict(
        id=lid, flight=flight["id"], side=W.side, s=[W.s0, W.s1],
        regions={f: [[dict(a=p["a"], b=p["b"], l=p["l"]["type"], r=p["r"]["type"], sTop=p["sTop"]) for p in regions[f][m]]
                     for m in range(nb)] for f in FACES},
        features=[dict(id=ft["id"], kind=ft["kind"], at=ft.get("at"), mid=ft.get("mid", False), lane=ft.get("lane", False),
                       fromStop=ft.get("fromStop"), bed=ft["bed"]) for ft in W.features],
        pitch=flight["pitch"],
        lines=[dict(z=z, kind=k_, src=s_) for z, k_, s_ in zip(W.Lz, W.Lkind, W.Lsrc)],
        panels=W.panels, edges=W.edges, boundaries=W.boundaries,
        footing={f: [[a, b, z] for a, b, z, _ in W.foot[f]] for f in FACES},
        ground=line["ground"],
        ceiling=[dict(kind=c["kind"], s=c["s"], owner=c["owner"],
                      **({"z": c["z"]} if c["kind"] == "level" else
                         {"rake": [c["R"].sA, c["R"].CA, c["R"].sB, c["R"].CB, c["R"].tv, c["R"].dx, c["R"].t]}))
                 for c in W.ceiling],
        stones=sorted(stones, key=lambda s: s["id"]),
        cells=cells,
        joints={f: [list(js) for js in joints[f]] for f in FACES},
        segments={f: [[dict(a=p["a"], b=p["b"], l=p["l"], r=p["r"], sTop=p["sTop"]) for p in sorted(segs[f][m], key=lambda d: d["a"])]
                      for m in range(nb)] for f in FACES},
        report=dict(falls=fall_report, throughs=through_report, cuts=cut_report, fills=fill_report, flags=W.flags),
    )
    return out


def _xs(st):
    xs = [p[0] for p in st["outline"]]
    return min(xs), max(xs)


def _bands_of(W, poly):
    zs = [p[1] for p in poly]
    lo, hi = min(zs), max(zs)
    return [m for m in range(len(W.Lz) - 1) if W.Lz[m] < hi and W.Lz[m + 1] > lo]


def _band_outline(W, m, x0, x1, p):
    """A course stone's face: a rectangle, or under the rake (its run's first stone) the trapezoid the cut leaves."""
    L, L2 = W.Lz[m], W.Lz[m + 1]
    if p.get("sTop") is not None and x0 == p["a"] and p["l"]["type"] == "rake":
        return [[x0, L], [x1, L], [x1, L2], [p["sTop"], L2]]
    if p.get("sTop") is not None and x0 == p["a"]:
        # (a run that starts part-high under the rake: a plumb left side, then the rake)
        zl = W.ceiling_at(x0)
        return [[x0, L], [x1, L], [x1, L2], [p["sTop"], L2], [x0, zl]]
    return [[x0, L], [x1, L], [x1, L2], [x0, L2]]


# ---------------------------------------------------------------------------------------------------------------
# The whole: the stair's steps and its walls

def lay(facts, reseed=None):
    seed = facts["worldSeed"]
    slab = facts["sources"]["stepStone"]
    width = None
    steps = []
    for fl in facts["stair"]["flights"]:
        width = fl["width"]
        steps.append(lay_steps(fl, seed, slab, fl["width"]))
    walls = []
    for ln in facts["walls"]["lines"]:
        fl = facts["stair"]["flights"][ln["flight"]]
        walls.append(lay_line(ln, fl, steps[ln["flight"]], seed, reseed))
    return dict(what="R1's layout (port step 2b): the gully's cheek walls as elevations and its steps in plan, integer "
                     "mm, laid by blender/generators/masonry.py from reviews/lt1/port/2b/r1/facts.json",
                worldSeed=seed, width=width, steps=steps, walls=walls)
