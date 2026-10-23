"""Masonry: a stair's cheek walls and its steps laid as 2D elevations in integer millimetres, by a mason's rules, before
any mesh (port step 2b, rung R1: reviews/lt1/port/2b/design.md, SN2, SN3, SN9, SN10). Pure Python, no bpy and no
numpy: the wall kind's stages and the stair's geometry stage call these functions later, from facts in integer mm.

A wall line (wl-<token>/fl-<n>/<l|r>, the wall beside one flight on one side) is unrolled as an elevation: s along
the flight from its foot point (mm), z up (mm, absolute). It has two faces, the stair's and the bank's, built to the
same level course lines and through the same features. It is laid in this order, features first:
- the course lines: one on every step top and none between (a rise is one course, up to RISE_ONE), free courses over
  the last step, each no larger than the one below, and foundation courses under the foot, larger than any rise (the
  largest courses low);
- the top, by SN2's parapet: level slab copings stepped square, a whole number of courses a step (one going or two
  each level run, `goings`), every bed on a course line, so below the last step every step falls on a step top's
  line; over a rest the coping runs level and drops square at the next flight. Where a stretch climbs other than a
  whole number of steps, its one short step stays at the stretch's top unless the runs then cannot be laid whole,
  and goes to the nearest place down the stretch where they can. Nothing is cut to a slope: no rake cuts, kneelers
  or knee stones. A wall end's run ends in a square topstone through its top course;
- the heads at the wall's ends: ties and runners alternating, each two courses high, under the topstone;
- the footings: on the stair's face the steps themselves (their ends occupied cells, 150 mm into the wall), on the
  bank's face steps with the ground, each step a whole course;
- the panels between the features (and the 1961 panel's edges), each on its own id and seed; every course takes a
  tooth at a panel's boundary and a straight joint at a 1961 edge, chosen from the line's features alone, so that a
  panel re-lays alone;
- the fallen stones the facts give, the through stones;
- then each course's free lengths, filled by choosing each stone's length (never stretched), every joint kept a lap
  from the joints below and above, the copings' joints included; a face the facts' visibility says is seen from
  nowhere is hidden work: its fill is not laid (its heads and throughs are).

The steps (SN3) are laid in plan: one or two stones a step, both ends 150 mm into the walls, the joint outside the
middle third, alternating, lapped 40 to 60 mm on the step below; a rest two to four slabs.

Seeds: blender/resolver/hashing.py, keyed on the world seed, the stable id of what a draw is for and its purpose,
never a float. Choices are integers and the four operations; outlines are integer mm, and no float enters a choice.
Ids (schemas/naming.md; the slots 2b proposes): a panel <line>/pn-<p>; a face stone <panel>/<stair|bank>/co-<k>/sp-<j>;
a through <panel>/co-<k>/th-<j>; a coping <panel>/cp-<c>; a head's stone <line>/hd-<e>/st-<m> (a tie, through the
wall), its runners .../st-<m>/stair and .../st-<m>/bank, its topstone <line>/hd-<e>/top. A step's stones are the
plan's <step>/sl-<k>; a rest's slabs <step>/sl-<k> counted row by row from its front (the plan names two; a rest
deeper than the longest slab has four); a turn landing's <flight>/turn/sl-<k>.

`clock`, when given, is a dict the laying adds its seconds to, by part (time.perf_counter); it never enters the
output, so the layout's hash is the same with or without it.
"""
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "resolver"))
import hashing as HS  # noqa: E402  (the one hash spec)

# The rules of any wall, in code (design.md 7b: what holds whatever the stone, its working, its era or the style):
# level beds, no rake, SN10's bond and SN2's sliver and acute limits. Every number that depends on the stone, its
# working, its era or the style is data, read into a Rules (below): the wall kind's structure from kinds/wall.json's
# plan params, the working's stone sizes from the pack's walling table (packs/<pack>/walling.json), by the working the
# facts name.
SLIVER = 50                 # no stone under 50 mm high, no face narrower (SN2)
ACUTE = 25                  # nor more acute than 25 degrees (tested, never a choice)
RATIO = (9, 2)              # no stone longer than 4.5 times its height (SN10)
LAP_MIN = 40                # a joint is kept 0.4 of the course's height, at least 40 mm, from the joints below (SN10)
FALLS_WHEN = (9, 10)        # a stone whose bed has lost more than nine tenths of its support falls with it
SHIFT_STEP = 5              # the through stones' search steps along the course, mm (a search's resolution only)
OVER_TOP = 300              # the free courses are laid this far over the top, past any coping's thickness, so the
                            # top always finds its bed (a search's reach only)

FACES = ("stair", "bank")
OPEN = ("end", "riser-open")      # a course's ends that are no joint: the wall's end, a stepped section's open end


class Refused(ValueError):
    """A rule the facts make impossible: raised loudly, never fixed silently."""


def _pair(v):
    return (v[0], v[1])


class Rules:
    """The numbers one wall line and its flight's steps are laid by, all from data, under the names the laying uses.

    `kind` is the wall kind's plan params (kinds/wall.json), the wall's structure: its parapet, its stepped top, its
    heads, its panels' teeth, its footings, the steps' ends in the walls. `walling` is the pack's walling table
    (packs/<pack>/walling.json); `working` names the working the wall was built in, `rebuilt` the working of the panel
    its facts say was rebuilt (or None), `stair` the working the stair's steps were laid in. A working's numbers are
    its stone's and its builders': the course heights the stone was split to, the stones' lengths, the copings', heads'
    and through stones' sizes, the steps' laps and joints. A missing number raises (KeyError): nothing defaults.
    """

    def __init__(self, kind, walling, working, rebuilt=None, stair=None):
        W = walling["workings"]
        if working not in W:
            raise Refused(f"the walling table has no working {working!r}")
        w = W[working]
        self.working, self.material = working, w["material"]
        # the working's: the stone and how it was laid
        self.COURSE = _pair(w["courseMm"])            # a course's height
        self.RISE_ONE = w["riseOneMm"]                # a rise up to this is one course; over it, one line between
        self.FOUND = _pair(w["foundationMm"])         # the foundation courses under the foot: larger than any rise
        self.STONE = _pair(w["stoneMm"])              # a face stone's length
        self.DRAW = tuple(_pair(p) for p in w["drawnPerHeight"])  # its drawn length, as fractions of its height
        self.SHORT = w["shortMm"]                     # where geometry leaves a run no whole stones fill, the least
        self.COPE_T = _pair(w["copeThickMm"])         # a coping's thickness
        self.COPE_NOM = w["copeNominalMm"]            # its nominal: the ideal bed is the pitch line + parapet - this
        self.COPE_L = _pair(w["copeLengthMm"])        # a coping slab's length
        self.COPE_MIN = w["copeLeastMm"]              # the least, where a run or a panel leaves less than a slab
        self.TOPSTONE = _pair(w["topstoneMm"])        # a topstone's length
        self.HEAD_TIE = _pair(w["headTieMm"])         # a head's tie, through the wall, as its face shows
        self.HEAD_RUN = _pair(w["headRunnerMm"])      # a head's runner along one face
        self.THROUGH = _pair(w["throughMm"])          # a through stone's face
        self.THROUGH_FIRST = _pair(w["throughFirstMm"])   # the first through from a panel's start
        self.THROUGH_EVERY = _pair(w["throughEveryMm"])   # and then one about this often
        # the rebuilt panel's working: its end stones, long and short in alternate courses
        self.rebuilt = rebuilt
        if rebuilt is not None:
            if rebuilt not in W:
                raise Refused(f"the walling table has no working {rebuilt!r}")
            self.LONG_SHORT = tuple(_pair(p) for p in W[rebuilt]["edgeStonesMm"])
        else:
            self.LONG_SHORT = None
        # the stair's working: its steps' laps and joints (SN3)
        if stair is not None:
            if stair not in W:
                raise Refused(f"the walling table has no working {stair!r}")
            s = W[stair]["steps"]
            self.STEP_LAP = _pair(s["lapMm"])             # a step's front bears this far on the back of the one below
            self.TREAD_JOINT = _pair(s["jointMm"])        # a tread's joint (SN5)
            self.STEP_JOINT_CLEAR = s["jointClearMm"]     # no joint within this of the joint on the step below
        # the kind's: the wall's structure
        self.PARAPET = kind["parapetMm"]              # the coping's top over the pitch line
        self.GOINGS = tuple(kind["copingGoings"])     # a level run of coping spans this many goings
        self.GOINGS_LAID = kind["copingGoingsLaid"]   # the one laid unless a caller asks for another
        self.HEAD_COURSES = kind["headCourses"]       # a head's stone is this many courses high
        self.SQUARE = tuple(_pair(p) for p in kind["topstoneSquare"])   # a topstone's length over its height
        self.RISER_FIRST = kind["riserFirstPerHeight"]    # a stepped section's stone at a riser: this times its height
        self.FREE_STEP = kind["freeCourseStepMm"]     # a free course over the last step: at least this less than below
        self.FOOT_TREAD = kind["footingTreadMm"]      # a bank footing's step is at least this long
        self.TOOTH = _pair(kind["toothMm"])           # a panel's boundary joint, course by course, this far either side
        self.TOOTH_WIDE = _pair(kind["toothWideMm"])  # where no tooth in TOOTH fits
        self.THROUGH_CLEAR = kind["throughClearMm"]   # no through stone this near a panel's boundary
        self.THROUGH_SHIFT = kind["throughShiftMm"]   # a through moves at most this far from where it is due
        st = kind["steps"]
        self.STEP_TAIL = st["tailMm"]                 # a step's both ends this far into the walls
        self.FACE_GAP = st["faceGapMm"]               # a wall's face stands this far off the stair's edge
        self.FIRST_STEP_BED = st["firstBedMm"]        # the first step's block goes this far under the lane
        self.REST_CUT = st["restCutMm"]               # a rest's two rows meet within this of its middle
        # derived
        self.FALL_CLEAR = self.TOOTH_WIDE[1] + self.STONE[0]   # a fallen stone keeps this far from a boundary
        # what the rules in code need of the numbers, checked here so a data edit cannot break them silently
        for name, (lo, hi) in (("courseMm", self.COURSE), ("stoneMm", self.STONE), ("copeLengthMm", self.COPE_L),
                               ("topstoneMm", self.TOPSTONE), ("toothMm", self.TOOTH)):
            if lo > hi:
                raise Refused(f"{working}: {name} {lo} > {hi}")
        if self.COURSE[0] < SLIVER or self.COPE_T[0] < SLIVER:
            raise Refused(f"{working}: a course or a coping under SN2's {SLIVER} mm")
        if self.GOINGS_LAID not in self.GOINGS:
            raise Refused(f"the wall kind lays {self.GOINGS_LAID} goings a level run, not one of {self.GOINGS}")
        # two panels' free joints decouple when their teeth leave them a course's lap apart (SN10): the widest teeth
        # either side of a boundary and the shortest stone beyond them
        if 2 * self.STONE[0] - 2 * self.TOOTH_WIDE[1] < lap_of(self.COURSE[1]):
            raise Refused(f"{working}: teeth to {self.TOOTH_WIDE[1]} mm and stones from {self.STONE[0]} mm leave two "
                          f"panels' joints under the lap of a {self.COURSE[1]} mm course apart")

    def longest(self, h):
        """The longest stone a course of height h takes (SN10's 4.5, and the working's longest)."""
        return min(self.STONE[1], RATIO[0] * h // RATIO[1])

    def drawn(self, h):
        """The range a course stone's length is drawn from (the working's fractions of its height), within its stones
        and SN10."""
        lo = max(self.STONE[0], self.DRAW[0][0] * h // self.DRAW[0][1])
        return lo, max(lo, min(self.longest(h), self.DRAW[1][0] * h // self.DRAW[1][1]))

    def corner(self, h):
        """A stepped section's corner stone at a riser, in a course h high: at least RISER_FIRST times h (SN2), to the
        course's longest."""
        lm = self.longest(h)
        return min(max(self.STONE[0], self.RISER_FIRST * h), lm), lm

    def edge_stone(self, m, h, side):
        """A rebuilt panel's end stone at its edge in course m (side 0 its first, 1 its last): long and short in
        alternate courses, the two edges a course apart, to the course's longest."""
        ls = self.LONG_SHORT[(m + side) % 2]
        lm = self.longest(h)
        return min(ls[0], lm), min(ls[1], lm)

    def run_layable(self, n, h, first=None, last=None):
        """Whether a run n long in a course h high can be laid in whole stones SN10 allows with its end stones' rules
        (`first`, `last`: their ranges, or None): the fill's own search, asked only whether a laying exists."""
        if n == 0:
            return True
        return fill_run(0, n, self.STONE[0], self.longest(h), [], lambda i: self.STONE[0], first, last) is not None

    def square(self, h):
        """A topstone h high is square when its length is within these (ceiling and floor), and the working's."""
        (a, b), (c, d) = self.SQUARE
        return max(self.TOPSTONE[0], -(-a * h // b)), min(self.TOPSTONE[1], c * h // d)


def rules_for(facts, data, line=None):
    """The Rules a line (or, with no line, the stair's steps) is laid by: data is {"kind": the wall kind's plan params,
    "walling": the pack's walling table}; the workings are the facts' (walls.working, the line's rebuilt.working,
    stair.working)."""
    reb = line.get("rebuilt") if line else None
    return Rules(data["kind"], data["walling"], facts["walls"]["working"],
                 reb["working"] if reb else None, facts["stair"]["working"])


def load_data(root, pack="stavanger-1989"):
    """The data a wall is laid from: the wall kind's plan params and the pack's walling table, as files."""
    import json
    kind = json.load(open(os.path.join(root, "kinds", "wall.json")))
    walling = json.load(open(os.path.join(root, "packs", pack, "walling.json")))
    return dict(kind=kind["stages"]["plan"]["params"], walling=walling)


class _Tick:
    """Adds the seconds of a `with` block to clock[part] (nothing when the clock is None)."""

    def __init__(self, clock, part):
        self.clock, self.part = clock, part

    def __enter__(self):
        self.t0 = time.perf_counter()

    def __exit__(self, *exc):
        if self.clock is not None:
            self.clock[self.part] = self.clock.get(self.part, 0.0) + time.perf_counter() - self.t0


def div_round(n, d):
    """n / d to the nearest integer, halves up (d nonzero)."""
    if d < 0:
        n, d = -n, -d
    return (2 * n + d) // (2 * d)


def lap_of(h):
    """SN10: a joint's lap from the joints below a course of height h."""
    return max(LAP_MIN, (2 * h + 4) // 5)


def is_joint(end):
    """Whether a course's end is a joint against something laid (a stone, a feature, a step's end, the ground's step,
    a tooth or edge, the coping a stepped section rises from), not an open end."""
    return end["type"] not in OPEN


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
    R = iv_union(_intersect([iv for iv in R if iv[1] >= iv[0]], allowed))
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
# The steps, in plan

def lay_steps(flight, seed, slab, width, D):
    """A flight's steps (SN3): the stones of each step across, both ends D.STEP_TAIL into the walls, never pieced in
    depth; a rest's slabs in rows; a turn landing's under the flight's foot. x across the stair (mm, right of the
    uphill direction positive), y along it (s). Raises Refused when the longest stone the record's finish allows makes a
    two-stone step impossible with its joint outside the middle third."""
    fid = flight["id"]
    half = width // 2 + D.FACE_GAP + D.STEP_TAIL
    clear = width + 2 * D.FACE_GAP
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

    widest = edge_window(-1, D.TREAD_JOINT[1])
    if widest[0] > widest[1]:
        raise Refused(f"{fid}: a two-stone step is impossible: the stones would be {2 * half} mm across between the "
                      f"walls' tails, the longest the finish allows is {hi} mm, and the joint must lie outside the "
                      f"middle third ({third} mm either side of the walking line)")
    out["jointWindow"] = dict(left=list(edge_window(-1, D.TREAD_JOINT[0])), right=list(edge_window(1, D.TREAD_JOINT[0])),
                              widthMm=edge_window(-1, D.TREAD_JOINT[0])[1] - edge_window(-1, D.TREAD_JOINT[0])[0] + 1)
    steps = flight["steps"]
    n = len(steps)
    side = 1 if HS.h(seed, fid, "joint", "side") % 2 else -1
    below = None                       # the joint (xl, jw) on the step or row below
    T = [flight["zFoot"]] + [st["zTop"] for st in steps]

    def row_joint(key_id, below_x, ahead_side):
        """A rest's or landing's row: two slabs, the joint anywhere both stay within the finish's sizes, clear of the
        joint below and, on the row the next step bears on, of where that step's joint can fall."""
        rng = HS.Stream(seed, key_id, "row")
        jw = rng.randint(*D.TREAD_JOINT)
        lo_x, hi_x = half - hi - jw, hi - half          # both slabs <= hi
        lo_x, hi_x = max(lo_x, -half + lo), min(hi_x, half - lo - jw)
        allowed = [(lo_x, hi_x)]
        keep = []
        if below_x is not None:
            keep.append((below_x - D.STEP_JOINT_CLEAR, below_x + D.STEP_JOINT_CLEAR))
        if ahead_side is not None:
            w0, w1 = edge_window(ahead_side, D.TREAD_JOINT[1])[0], edge_window(ahead_side, D.TREAD_JOINT[0])[1]
            keep.append((w0 - D.STEP_JOINT_CLEAR, w1 + D.STEP_JOINT_CLEAR))
        allowed = iv_minus_open(allowed, keep)
        if not allowed:
            raise Refused(f"{key_id}: no joint for a rest's row clear of the joints below and above")
        x = iv_nearest(allowed, rng.randint(lo_x, hi_x))
        return x, jw

    if flight["start"] > 0:
        # the turn landing under the flight's foot, at the lane's level: the first step bears on its back
        rid = f"{fid}/turn"
        lap = HS.Stream(seed, f"{fid}/turn", "lap").randint(*D.STEP_LAP)
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
        lap = rng.randint(*D.STEP_LAP) if i < n - 1 else 0
        y0 = st["S"]
        y1 = steps[i + 1]["S"] + lap if i < n - 1 else y0 + st["D"]     # (S and D were rounded apart: S rules)
        rise = T[i + 1] - T[i]
        z0 = T[i + 1] - rise - (D.FIRST_STEP_BED if i == 0 and flight["start"] == 0 else 0)
        rest = st["D"] > g + 1
        if not rest:
            jw = rng.randint(*D.TREAD_JOINT)
            wl, wh = edge_window(side, jw)
            x = rng.randint(wl, wh)
            if below is not None and abs(x - below) < D.STEP_JOINT_CLEAR:
                out["flags"].append(f"{sid}: joint within {D.STEP_JOINT_CLEAR} mm of the one below")
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
                d0 = min(max(rng.randint(depth // 2 - D.REST_CUT, depth // 2 + D.REST_CUT), lo_d), hi_d)
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

    def __init__(self, line, flight, steps_out, seed, D, reseed=None):
        self.f = line
        self.D = D
        self.fl = flight
        self.steps_out = steps_out
        self.seed = seed
        self.reseed = reseed or {}
        self.id = line["id"]
        self.side = line["side"]
        self.s0, self.s1 = line["s0"], line["s1"]
        self.flags = []
        self.T = [flight["zFoot"]] + [st["zTop"] for st in flight["steps"]]
        self.S = [st["S"] for st in flight["steps"]]

    # ---- keys
    def key(self, owner, *purpose):
        """A draw's key: the world seed, the id it is for, its purpose; a panel re-laid by an event takes its event."""
        extra = self.reseed.get(owner)
        return (self.seed, owner) + purpose + ((extra,) if extra else ())

    def stream(self, owner, *purpose):
        return HS.Stream(*self.key(owner, *purpose))

    # ---- course lines
    def course_lines(self):
        """One line on every step top, none between (a rise over RISE_ONE takes one, the lower course the larger);
        the free courses over the last step, the first no larger than the last rise and each no larger than the one
        below; the foundation courses under the foot, each at least any rise and at least the course over it."""
        D = self.D
        lid, T = self.id, self.T
        L = [(T[0], "step", -1)]
        for i in range(len(T) - 1):
            lo, hi = T[i], T[i + 1]
            rise = hi - lo
            if rise < D.COURSE[0]:
                raise Refused(f"{self.fl['steps'][i]['id']}: a rise of {rise} mm is under a course's least")
            if rise > D.RISE_ONE:
                a, b = lo + (rise + 1) // 2, hi - D.COURSE[0]
                m = HS.between(HS.h(self.seed, lid, "course", i), a, b) if b >= a else lo + rise // 2
                L.append((m, "mid", i))
            L.append((hi, "step", i))
        rng = HS.Stream(self.seed, lid, "courses", "free")
        hp = T[-1] - T[-2] if len(T) > 1 else D.COURSE[1]
        z = T[-1]
        while z < T[-1] + D.PARAPET + OVER_TOP:
            h = rng.randint(max(D.COURSE[0], hp - D.FREE_STEP), max(D.COURSE[0], hp))
            z += h
            L.append((z, "free", None))
            hp = h
        # downwards from the foot, each course at least the one over it: the largest lowest
        rng = HS.Stream(self.seed, lid, "courses", "found")
        zlow = min(min(gz for _, gz in self.f["ground"]), T[0]) - D.FOUND[1]
        z, h = T[0], D.FOUND[0]
        while z > zlow:
            h = rng.randint(h, D.FOUND[1])
            z -= h
            L.append((z, "found", None))
        L.sort()
        self.Lz = [z for z, _, _ in L]
        self.Lkind = [k for _, k, _ in L]
        self.Lsrc = [s for _, _, s in L]

    def nearest(self, y):
        """The index of the course line nearest y (the lower one on a tie)."""
        return min(range(len(self.Lz)), key=lambda i: (abs(self.Lz[i] - y), i))

    # ---- the pitch line's runs and the panels
    def runs(self):
        P = self.fl["pitch"]
        segs = []
        if P[0][0] > self.s0 + SLIVER:
            segs.append(dict(kind="level", s=[self.s0, P[0][0]], z=P[0][1]))
        for p, q in zip(P, P[1:]):
            segs.append(dict(kind="rake" if q[1] > p[1] else "level", s=[p[0], q[0]], z=[p[1], q[1]]))
        if P[-1][0] < self.s1 - SLIVER:
            segs.append(dict(kind="level", s=[P[-1][0], self.s1], z=P[-1][1]))
        return segs

    def panels_make(self, segs, xs):
        """The panels, between the line's features (design.md, Panels: heads, rests, the rebuilt panel's edges). A
        rest's feature in the wall (a level stretch of the pitch between two rising ones) is the coping's level run
        over it, so its panel's boundaries are that run's risers, where every course under the run's ends must end or
        take a tooth anyway. The wall's ends are its heads, laid as features: the panel beside a head runs to the
        wall's end, its fill meeting the head's stones. The rebuilt panel's edges are the facts'. Every boundary that
        is no edge takes a tooth in the courses that run across it."""
        b = set()
        for q, sg in enumerate(segs):
            if sg["kind"] != "level" or q == 0 or q == len(segs) - 1:
                continue
            mid = (sg["s"][0] + sg["s"][1]) // 2
            i = next(i for i in range(len(xs) - 1) if xs[i] <= mid < xs[i + 1] or i == len(xs) - 2)
            b |= {x for x in (xs[i], xs[i + 1]) if self.s0 < x < self.s1}
        reb = self.f.get("rebuilt")
        edges = list(reb["s"]) if reb else []
        bounds = sorted(b | set(edges) | {self.s0, self.s1})
        self.edges = edges
        self.panels = []
        for p, (lo, hi) in enumerate(zip(bounds, bounds[1:])):
            work = str(reb["year"]) if reb and reb["s"][0] <= (lo + hi) // 2 <= reb["s"][1] else "built"
            self.panels.append(dict(id=f"{self.id}/pn-{p}", s=[lo, hi], work=work))
        self.boundaries = sorted(b - set(edges))     # the boundaries every course across them is toothed at

    def panel_at(self, s):
        for pn in self.panels:
            if pn["s"][0] <= s < pn["s"][1]:
                return pn
        return self.panels[-1]

    def panel_starting(self, s):
        return next(pn for pn in self.panels if pn["s"][0] == s)

    def panel_ending(self, s):
        return next(pn for pn in self.panels if pn["s"][1] == s)

    # ---- the top: level slab copings stepped square (SN2's parapet)
    def ideal_bed(self):
        """The coping's ideal bed along the wall: the pitch line + PARAPET - COPE_NOM, level beyond its ends, as
        integer breaks (s, y) from s0 to s1."""
        D = self.D
        P = self.fl["pitch"]

        def at(s):
            if s <= P[0][0]:
                return P[0][1]
            if s >= P[-1][0]:
                return P[-1][1]
            for (sa, za), (sb, zb) in zip(P, P[1:]):
                if sa <= s <= sb:
                    return za + div_round((s - sa) * (zb - za), sb - sa)
        pts = [(self.s0, at(self.s0))] + [(s, z) for s, z in P if self.s0 < s < self.s1] + [(self.s1, at(self.s1))]
        Y = [(s, z + D.PARAPET - D.COPE_NOM) for s, z in pts]
        if any(q[1] < p[1] for p, q in zip(Y, Y[1:])):
            raise Refused(f"{self.id}: a pitch line that falls along s has no stepped-coping rule here")
        return Y

    def place_risers(self, risers, goings, tops):
        """Each riser from where the ideal bed puts it, moved only within its window (half a going either side of
        that point, on the stretch the bed rises over), by two rules of the bond, in this order:
        1. a riser near a straight joint (a rebuilt panel's edge, which runs through every course under it) leaves
           its courses room to be laid to it: on the edge's lower side, the run from the riser to the edge takes its
           corner stone (at least RISER_FIRST times the course's height) and, where the run is the rebuilt panel's,
           the edge's long or short stone, in every course the riser steps over; else the riser moves to the nearest
           place in its window where they fit, or onto the edge. On the edge's higher side within a lap (SN10) of
           it, where the riser's joint would sit over the edge's, it lies on the edge;
        2. where a level run of `goings` goings holds a whole coping slab (COPE_L's least), every level run between
           two risers is one: a short run's risers move out, the higher first, each by what its window and its other
           run allow (kept a whole slab, by pushing the risers beyond it in turn; never shrunk at the wall's ends,
           where the topstones are laid), over as many passes as move anything. With one going a run (under a slab
           by nature) the risers stay where the bed puts them;
        3. each end run (the wall's first and last, `tops`: the square topstone's range in each) holds its topstone
           and a whole slab, or is the topstone alone: else its riser moves to the nearest place in its window where
           it does, keeping the run beyond it a whole slab where rule 2 holds (a slab's least where it does not).
        What cannot be met is flagged, never forced."""
        D, Lz, lid = self.D, self.Lz, self.id
        half = self.fl["g"] // 2
        reb = self.f.get("rebuilt")
        edges = list(reb["s"]) if reb else []
        H = [Lz[i + 1] - Lz[i] for i in range(len(Lz) - 1)]
        for r in risers:
            r["window"] = (max(r["stretch"][0], r["ideal"] - half), min(r["stretch"][1], r["ideal"] + half))
            r["moved"], r["fixed"] = None, False
        def room_ok(r, x, e):
            """Whether every course riser r steps over can be laid from x to the edge e above it."""
            return x == e or (x < e and all(
                D.run_layable(e - x, H[m], D.corner(H[m]),
                              D.edge_stone(m, H[m], 1) if e == reb["s"][1] and x > reb["s"][0] else None)
                for m in range(r["lo"], r["hi"])))

        for k, r in enumerate(risers):
            lap = lap_of(H[r["lo"]])
            lo_w = max(r["window"][0], risers[k - 1]["at"] + D.COPE_MIN if k else r["window"][0])
            hi_w = min(r["window"][1], risers[k + 1]["at"] - D.COPE_MIN if k + 1 < len(risers) else r["window"][1])
            below = [e for e in edges if 0 < r["at"] - e < lap]
            above = [e for e in edges if e > r["at"]][:1]
            for e in below:
                if lo_w <= e <= hi_w:
                    r["at"], r["fixed"] = e, True
                    r["moved"] = f"onto the straight joint at {e}"
                else:
                    self.flags.append(f"{lid}: the riser at {r['at']} is {r['at'] - e} mm past the straight joint at "
                                      f"{e}, which is outside its window {[lo_w, hi_w]}")
            for e in above:
                if room_ok(r, r["at"], e):
                    continue
                ok = [x for x in range(lo_w, hi_w + 1) if room_ok(r, x, e)]
                if not ok:
                    self.flags.append(f"{lid}: the riser at {r['at']} leaves its courses no laying to the straight "
                                      f"joint at {e} anywhere in its window {[lo_w, hi_w]}")
                    continue
                x = min(ok, key=lambda v: (abs(v - r["at"]), v))
                r["moved"] = (f"onto the straight joint at {e}" if x == e else
                              f"{x - r['ideal']:+d} mm, so its corner stones and the edge's fit before the straight "
                              f"joint at {e}")
                r["at"], r["fixed"] = x, True
        n = len(risers)
        if n < 2:
            return

        def length(i):              # the interior run between risers i - 1 and i (1 <= i < n)
            return risers[i]["at"] - risers[i - 1]["at"]

        def push(k, want, sgn, least=D.COPE_L[0]):
            """Moves riser k by up to `want` mm (up the wall for sgn 1, down for -1) within its window, keeping the
            run beyond it `least` long (a whole slab), and pushing the risers beyond as that run needs. Returns the mm
            moved."""
            r = risers[k]
            other = k + 1 if sgn > 0 else k          # the run on the riser's far side
            if r["fixed"] or want <= 0 or not 1 <= other < n:
                return 0                             # an end run is never shrunk: its topstone is laid in it
            want = min(want, r["window"][1] - r["at"] if sgn > 0 else r["at"] - r["window"][0])
            if length(other) - least < want:
                push(k + sgn, want - max(0, length(other) - least), sgn, least)
            mv = max(0, min(want, length(other) - least))
            if mv:
                r["at"] += sgn * mv
                r["moved"] = f"{r['at'] - r['ideal']:+d} mm, so the runs either side are whole slabs"
            return mv

        if goings * self.fl["g"] >= D.COPE_L[0]:     # a run of `goings` goings holds a whole slab: the odd ones can
            for _ in range(2 * n):
                moved = 0
                for i in range(1, n):
                    short = D.COPE_L[0] - length(i)
                    if short > 0:
                        got = push(i, short, 1)
                        moved += got + push(i - 1, short - got, -1)
                if not moved:
                    break
        whole = goings * self.fl["g"] >= D.COPE_L[0]
        beyond = D.COPE_L[0] if whole else D.COPE_MIN     # what rule 3 keeps the runs beyond an end riser
        for e, (lo_t, hi_t) in enumerate(tops):
            if not risers or lo_t > hi_t:
                continue
            k = 0 if e == 0 else n - 1
            r = risers[k]
            out = 1 if e == 0 else -1               # the move that lengthens the end run

            def end_len(x, e=e):
                return x - self.s0 if e == 0 else self.s1 - x
            L0_ = end_len(r["at"])
            if L0_ >= lo_t + D.COPE_L[0] or lo_t <= L0_ <= hi_t:
                continue
            if r["fixed"]:
                self.flags.append(f"{lid}: the end run at the riser {r['at']} is {L0_} mm, neither a topstone ({lo_t} "
                                  f"to {hi_t}) nor one and a whole slab; the riser lies on a straight joint")
                continue
            saved = [(q["at"], q["moved"]) for q in risers]
            opts = []
            # a topstone and a whole slab: the riser moves away from the end, the runs beyond kept `beyond` long
            want = lo_t + D.COPE_L[0] - L0_
            if n > 1 and push(k, want, out, beyond) == want:
                opts.append((want, "and a whole slab", [(q["at"], q["moved"]) for q in risers]))
            for q, (at_, mv_) in zip(risers, saved):
                q["at"], q["moved"] = at_, mv_
            # the topstone alone: the riser moves toward the end, within its window and a least run from the next
            if L0_ > hi_t:
                x = r["at"] - out * (L0_ - hi_t)
                lo_w, hi_w = r["window"]
                if k > 0:
                    lo_w = max(lo_w, risers[k - 1]["at"] + beyond)
                if k + 1 < n:
                    hi_w = min(hi_w, risers[k + 1]["at"] - beyond)
                if lo_w <= x <= hi_w:
                    opts.append((L0_ - hi_t, "alone", [(q["at"], q["moved"]) if q is not r else (x, None)
                                                       for q in risers]))
            if not opts:
                self.flags.append(f"{lid}: the end run at the riser {r['at']} is {L0_} mm, neither a topstone ({lo_t} "
                                  f"to {hi_t}) nor one and a whole slab; its window and the runs beyond allow neither")
                continue
            _, how, state = min(opts, key=lambda o: (o[0], o[1]))
            for q, (at_, mv_) in zip(risers, state):
                q["at"], q["moved"] = at_, mv_
            r["moved"] = f"{r['at'] - r['ideal']:+d} mm, so the end run is its topstone {how}"
            r["fixed"] = True
        for i in range(1, n):
            if length(i) < D.COPE_L[0]:
                self.flags.append(f"{lid}: the level run from {risers[i - 1]['at']} to {risers[i]['at']} is "
                                  f"{length(i)} mm, under a whole coping slab ({D.COPE_L[0]}): its windows allow no more")
            if length(i) <= 0:
                raise Refused(f"{lid}: two risers cross at {risers[i]['at']}")

    def coping(self, goings):
        """Features first: the coping's level runs and their risers, the topstones at the wall's ends, the slabs.
        A riser goes where the ideal bed crosses the middle of the step, between the two beds; a step is `goings`
        courses up to the nearest line under the next level run's ideal bed (fewer to meet it exactly), so it falls
        on a course line and every coping lies on whole courses. Sets the ceiling the courses are laid under."""
        D = self.D
        if goings not in D.GOINGS:
            raise Refused(f"{self.id}: a level run spans {' or '.join(map(str, D.GOINGS))} goings, not {goings}")
        if self.f.get("retains"):
            raise Refused(f"{self.id}: a retaining wall's top (SN2: the bank over a level top course) is not laid "
                          "at R1; no line in these facts retains")
        segs = self.runs()
        lid, Lz = self.id, self.Lz
        Y = self.ideal_bed()
        self.idealBed = Y
        k0 = self.nearest(Y[0][1])

        def setout(shorts):
            """The risers, as a mason sets out a stepped coping: each rising stretch of the ideal bed ends at a level
            run (a rest, a landing, the wall's end), and the bed steps up to the line nearest that run's ideal bed,
            `goings` courses a step. Where a stretch's courses are not a whole number of such steps, one step is
            short: `shorts` maps the stretch (its index) to the short step's place among its steps, counted from the
            stretch's foot; by default it is the last, beside the level run above. Returns the risers, the flags,
            the beds, the coping runs' thicknesses, each end's square topstone range, and the default places."""
            k, x, j, si = k0, self.s0, 0, 0
            out, fl, places = [], [], []
            while j < len(Y) - 1:
                if Y[j + 1][1] == Y[j][1]:
                    j += 1
                    continue
                ja = j
                while j < len(Y) - 1 and Y[j + 1][1] > Y[j][1]:
                    j += 1
                stretch = (Y[ja][0], Y[j][0])
                kE = self.nearest(Y[j][1])
                whole, short = divmod(max(0, kE - k), goings)
                sizes = [goings] * whole
                if short:
                    sizes.insert(shorts.get(si, whole), short)
                places.append(whole if short else None)
                for step in sizes:
                    v2 = Lz[k] + Lz[k + step]
                    xr = None
                    for (sa, ya), (sb, yb) in zip(Y[ja:j], Y[ja + 1:j + 1]):
                        if 2 * yb >= v2:
                            xr = sa if 2 * ya >= v2 else sa + div_round((v2 - 2 * ya) * (sb - sa), 2 * (yb - ya))
                            break
                    if xr is None:
                        xr = Y[j][0]
                        fl.append(f"{lid}: a riser from {Lz[k]} to {Lz[k + step]} put at the stretch's end {xr}")
                    xr = max(xr, x)
                    out.append(dict(at=xr, lo=k, hi=k + step, ideal=xr, stretch=stretch, stretchIndex=si,
                                    short=step < goings))
                    x = xr
                    k += step
                si += 1
            merged = []
            for r in out:
                if merged and merged[-1]["at"] == r["at"]:
                    merged[-1]["hi"] = r["hi"]
                    fl.append(f"{lid}: two risers meet at {r['at']}: one step of "
                              f"{merged[-1]['hi'] - merged[-1]['lo']} courses")
                else:
                    merged.append(dict(r))
            beds = [k0] + [r["hi"] for r in merged]
            if beds[0] == 0 or beds[-1] == 0:
                raise Refused(f"{lid}: the end run's bed is the lowest line; no course under it for a topstone")
            t = [HS.Stream(self.seed, lid, "cope", "run", i).randint(*D.COPE_T) for i in range(len(beds))]
            # the square topstone's range at each end: through the end run's top course, to the coping's top
            tops_sq = [D.square(Lz[beds[i]] + t[i] - Lz[beds[i] - 1]) for i in (0, len(beds) - 1)]
            return merged, fl, beds, t, tops_sq, places

        def unmet(shorts):
            """What a set-out leaves unmet once its risers are placed: the flags (an end run neither its topstone
            nor its topstone and a whole slab, a level run under a whole slab, a straight joint with no room), a
            refusal counting above any number of them."""
            rs, fl, _, _, tq, _ = setout(shorts)
            n0 = len(self.flags)
            try:
                self.place_risers(rs, goings, tq)
                got = (0, len(fl) + len(self.flags) - n0)
            except Refused:
                got = (1, len(fl))
            del self.flags[n0:]
            return got

        # the short step goes at its stretch's top unless the runs cannot then be laid; then, one stretch at a time,
        # at the nearest place down the stretch that leaves less unmet (a mason sets out the steps from the heads,
        # so the ends' topstones and every run's whole slabs fit), the stretches in order at each distance
        shorts = {}
        best = unmet(shorts)
        places = setout(shorts)[5]
        while best != (0, 0):
            found = None
            for d in range(1, max([p for p in places if p is not None], default=0) + 1):
                for si, p in enumerate(places):
                    if p is None or si in shorts or p - d < 0:
                        continue
                    got = unmet({**shorts, si: p - d})
                    if got < best:
                        found = (si, p - d, got)
                        break
                if found:
                    break
            if not found:
                break
            shorts[found[0]] = found[1]
            best = found[2]
        risers, fl, beds, t, tops_sq, places = setout(shorts)
        self.flags += fl
        self.place_risers(risers, goings, tops_sq)
        for r in risers:
            si = r["stretchIndex"]
            if r["short"] and si in shorts:
                n_ = places[si] - shorts[si]
                r["short"] = (f"the stretch's short step, set {n_} step{'s' if n_ != 1 else ''} down from its top so "
                              f"its runs can be laid whole")
                r["moved"] = f"{r['moved']}; {r['short']}" if r["moved"] else r["short"]
        xs = [self.s0] + [r["at"] for r in risers] + [self.s1]
        # the topstones at the wall's ends: square, bedded through the end run's top course; a run too short for a
        # topstone and a slab is the topstone alone (its riser moved to make it square, flagged)
        tops = {}
        for e in (0, 1):
            i = 0 if e == 0 else len(beds) - 1
            bed = beds[i]
            if bed == 0:
                raise Refused(f"{lid}: the end run's bed is the lowest line; no course under it for a topstone")
            zt = Lz[bed - 1]
            C = Lz[bed] + t[i]
            h = C - zt
            lo_t, hi_t = D.square(h)
            if lo_t > hi_t:
                raise Refused(f"{lid}/hd-{e}/top: no square topstone {h} mm high within {D.TOPSTONE}")
            tid = f"{lid}/hd-{e}/top"
            run_len = xs[i + 1] - xs[i]
            if len(beds) == 1:
                run_len //= 2
            Lt0 = self.stream(tid, "lay").randint(lo_t, hi_t)
            if len(beds) > 1 and run_len < lo_t:
                Lt, cap = lo_t, True
                self.flags.append(f"{tid}: its run was {run_len} mm, under a square topstone; the riser moved out "
                                  f"to {lo_t}")
            elif len(beds) > 1 and run_len <= hi_t:
                Lt, cap = run_len, True
            elif run_len - lo_t >= D.COPE_L[0]:          # a topstone and a whole slab
                Lt, cap = min(max(Lt0, lo_t), min(hi_t, run_len - D.COPE_L[0])), False
            elif run_len - lo_t >= D.COPE_MIN:            # a topstone and a short slab, flagged with the slab
                Lt, cap = min(max(Lt0, lo_t), min(hi_t, run_len - D.COPE_MIN)), False
            elif len(beds) > 1:
                Lt, cap = hi_t, True
                self.flags.append(f"{tid}: its run was {run_len} mm, a topstone and less than a slab; the riser "
                                  f"moved in to {hi_t}")
            else:
                raise Refused(f"{lid}: a wall of one run too short for two topstones and a slab")
            if cap:
                if e == 0:
                    xs[1] = self.s0 + Lt
                    risers[0]["at"] = xs[1]
                else:
                    xs[-2] = self.s1 - Lt
                    risers[-1]["at"] = xs[-2]
            tops[e] = dict(id=tid, Lt=Lt, bed=zt, top=C, cap=cap)
        for i in range(len(beds)):
            if xs[i + 1] - xs[i] < D.COPE_MIN and not ((i == 0 and tops[0]["cap"]) or
                                                     (i == len(beds) - 1 and tops[1]["cap"])):
                self.flags.append(f"{lid}: a level run of {xs[i + 1] - xs[i]} mm at {xs[i]}, under {D.COPE_MIN}")
            if xs[i + 1] <= xs[i]:
                raise Refused(f"{lid}: the coping's runs overlap at {xs[i]}")
        self.risers = [dict(at=r["at"], lo=r["lo"], hi=r["hi"], courses=r["hi"] - r["lo"], ideal=r["ideal"],
                            moved=r["moved"]) for r in risers]
        self.panels_make(segs, xs)
        self.cruns = [dict(s=[xs[i], xs[i + 1]], bed=Lz[beds[i]], bedIndex=beds[i], t=t[i], top=Lz[beds[i]] + t[i])
                      for i in range(len(beds))]
        # the ceiling the courses are laid under, and the features and slabs on it
        ceil, feats, slabs = [], [], []
        self.head_top = {}
        for i in range(len(beds)):
            a, b = xs[i], xs[i + 1]
            z, C = Lz[beds[i]], Lz[beds[i]] + t[i]
            pieces = []
            if i == 0:
                tp = tops[0]
                pieces.append(dict(s=[a, a + tp["Lt"]], z=tp["bed"], top=tp["top"], owner=tp["id"], kind="topstone"))
                a += tp["Lt"]
            tail = None
            if i == len(beds) - 1:
                tp = tops[1]
                tail = dict(s=[b - tp["Lt"], b], z=tp["bed"], top=tp["top"], owner=tp["id"], kind="topstone")
                b -= tp["Lt"]
            if b > a:
                pieces.append(dict(s=[a, b], z=z, top=C, owner="coping", kind="coping", run=i))
            if tail:
                pieces.append(tail)
            ceil += pieces
        for e in (0, 1):
            tp = tops[e]
            a, b = (self.s0, self.s0 + tp["Lt"]) if e == 0 else (self.s1 - tp["Lt"], self.s1)
            feats.append(dict(id=tp["id"], kind="topstone", outline=[[a, tp["bed"]], [b, tp["bed"]], [b, tp["top"]],
                                                                     [a, tp["top"]]], bed=tp["bed"], head=e,
                              at=a if e == 1 else b, cap=tp["cap"]))
            self.head_top[e] = (tp["bed"], tp["id"])
        # the slabs: each coping piece cut near every panel boundary and 1961 edge inside it, then into slabs of
        # COPE_L. A piece no longer than a slab is one slab, across the boundary; a longer one is cut at the boundary,
        # or as near it as keeps both sides a whole slab long (the cut is the line's features' alone, so either
        # panel re-lays alone: the slab over the boundary is the panel's that holds its middle, and its own joints
        # stay a slab from its ends, on that panel's side)
        bounds = sorted(set(pn["s"][0] for pn in self.panels[1:]))
        self.cope_j = {}
        self.cope_cuts = []
        for c in ceil:
            if c["kind"] != "coping":
                continue
            a, b = c["s"]
            cuts = [a]
            if b - a > D.COPE_L[1]:
                inner = [q for q in bounds if a < q < b]
                for bi, q in enumerate(inner):
                    lo_c = cuts[-1] + D.COPE_L[0]
                    hi_c = b - D.COPE_L[0] * (len(inner) - bi)
                    if lo_c > hi_c:
                        self.cope_cuts.append(dict(at=q, cut=None, run=c["run"]))
                        continue
                    x_ = min(max(q, lo_c), hi_c)
                    cuts.append(x_)
                    self.cope_cuts.append(dict(at=q, cut=x_, run=c["run"]))
            cuts.append(b)
            for jj, (p, q) in enumerate(zip(cuts, cuts[1:])):
                pn = self.panel_at((p + q) // 2)
                if q - p <= D.COPE_L[1]:
                    J = [p, q]
                else:
                    rng = self.stream(pn["id"], "cope", c["run"], jj)
                    J = fill_run(p, q, D.COPE_L[0], D.COPE_L[1], [], lambda i_, rng=rng: rng.randint(*D.COPE_L))
                if q - p < D.COPE_MIN:
                    self.flags.append(f"{pn['id']}: a coping {q - p} mm long between {p} and {q}, under {D.COPE_MIN}")
                for u, v in zip(J, J[1:]):
                    slabs.append(dict(panel=pn["id"], kind="coping", run=c["run"], bedIndex=beds[c["run"]],
                                      outline=[[u, c["z"]], [v, c["z"]], [v, c["top"]], [u, c["top"]]]))
        # the copings' joints, over the course under each run: every slab end that meets a stone (another slab, a
        # topstone, or a stepped section's corner stone at a riser the run is the lower side of)
        for sl in slabs:
            i = sl["run"]
            u, v = sl["outline"][0][0], sl["outline"][1][0]
            for x_, left in ((u, True), (v, False)):
                if x_ in (self.s0, self.s1):
                    continue
                if left and x_ == xs[i] and i > 0 and beds[i - 1] < beds[i]:
                    continue        # the higher run's open end over its riser
                if not left and x_ == xs[i + 1] and i < len(beds) - 1 and beds[i + 1] < beds[i]:
                    continue
                self.cope_j.setdefault(sl["bedIndex"] - 1, []).append((x_, lap_of(self.cruns[i]["t"])))
        self.slabs = slabs
        self.features = feats
        self.ceiling = ceil
        for p, q in zip(ceil, ceil[1:]):
            if p["s"][1] != q["s"][0]:
                raise Refused(f"{lid}: the coping's pieces do not meet at {p['s'][1]} / {q['s'][0]}")

    def ceiling_at(self, s):
        for c in self.ceiling:
            if c["s"][0] <= s < c["s"][1]:
                return c["z"]
        return self.ceiling[-1]["z"]

    # ---- footings
    def footings(self):
        D = self.D
        S, T = self.S, self.T
        ff = [(self.s0, S[0], T[0], "lane" if self.fl["start"] == 0 else "turn")]
        for i in range(len(S)):
            ff.append((S[i], S[i + 1] if i + 1 < len(S) else self.s1, T[i + 1], self.fl["steps"][i]["id"]))
        self.foot = {"stair": [(a, b, z, ref) for a, b, z, ref in ff if b > a]}
        g = self.f["ground"]
        steps_ = {sb - sa for (sa, _), (sb, _) in zip(g, g[1:-1])}     # the last sample is the line's end
        if len(steps_) != 1 or g[-1][0] - g[-2][0] > min(steps_):
            raise Refused(f"{self.id}: the ground is sampled at uneven spacings {sorted(steps_)}")
        grid = steps_.pop()                         # the ground's sample spacing, from the facts
        cells = []
        for (sa, za), (sb, zb) in zip(g, g[1:]):
            m = min(za, zb)
            idx = max([i for i, z in enumerate(self.Lz) if z <= m], default=0)
            cells.append((sa, sb, idx))
        n = len(cells)
        per = D.FOOT_TREAD // grid
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
        """Course m's lengths on a face: where it stands over the footing and under the coping and its topstones.
        Each run [a, b] carries its ends' causes: the wall's end, a topstone (a feature it abuts), a riser (the end
        of a stepped section, against the lower run's coping or topstone for part of its height, or open over it),
        a step's end or the ground's step."""
        L, L2 = self.Lz[m], self.Lz[m + 1]
        runs = []
        for i, c in enumerate(self.ceiling):
            if c["z"] >= L2:
                if runs and runs[-1]["b"] == c["s"][0] and runs[-1]["ri"] == i - 1:
                    runs[-1]["b"], runs[-1]["ri"] = c["s"][1], i
                else:
                    runs.append(dict(a=c["s"][0], b=c["s"][1], li=i, ri=i))
            elif c["z"] > L:
                self.flags.append(f"{self.id}: course {m} meets {c['owner']}'s bed {c['z']} inside it")
        out = []
        for r in runs:
            lend = self._nb_end(r["li"] - 1, L, L2) if r["a"] > self.s0 else dict(type="end")
            rend = self._nb_end(r["ri"] + 1, L, L2) if r["b"] < self.s1 else dict(type="end")
            out.append(dict(a=r["a"], b=r["b"], l=lend, r=rend))
        stand = iv_union([(a, b - 1) for a, b, z, _ in self.foot[face] if z <= L])
        res = []
        for lo0, hi0 in stand:
            lo1, hi1 = lo0, hi0 + 1
            for run in out:
                lo, hi = max(lo1, run["a"]), min(hi1, run["b"])
                if lo >= hi:
                    continue
                lend = run["l"] if lo == run["a"] else self._foot_end(face, lo)
                rend = run["r"] if hi == run["b"] else self._foot_end(face, hi)
                res.append(dict(a=lo, b=hi, l=lend, r=rend))
        res.sort(key=lambda d: d["a"])
        return res

    def _nb_end(self, i, L, L2):
        """A course's end against the ceiling piece i beside it, lower than the course's top: a topstone standing
        through it (a feature), the lower run's coping or topstone over part of its height (a riser's joint), or
        nothing (an open end at a riser)."""
        c = self.ceiling[i]
        if c["top"] >= L2:
            return dict(type="feature", ref=c["owner"])
        if c["top"] > L:
            return dict(type="riser", ref=c["owner"])
        return dict(type="riser-open", ref=c["owner"])

    def _foot_end(self, face, s):
        if face == "bank":
            return dict(type="ground", ref="ground")
        for i, Si in enumerate(self.S):
            if Si == s:
                return dict(type="step", ref=step_end_id(self.steps_out, self.fl["steps"][i]["id"], self.side, s))
        return dict(type="step", ref="step")


# ---------------------------------------------------------------------------------------------------------------
# Laying a line's courses

def lay_line(line, flight, steps_out, seed, D, reseed=None, goings=None, laid=None, clock=None):
    """One wall line, features first, then each course's free lengths. `laid` maps (panel id, face) to whether that
    face is laid stone by stone (the facts' visibility); a face missing from it is laid."""
    laid = laid or {}
    goings = D.GOINGS_LAID if goings is None else goings
    W = Line(line, flight, steps_out, seed, D, reseed)
    with _Tick(clock, "features: course lines"):
        W.course_lines()
    with _Tick(clock, "features: coping"):
        W.coping(goings)
    with _Tick(clock, "features: footings"):
        W.footings()
    nb = len(W.Lz) - 1
    H = [W.Lz[m + 1] - W.Lz[m] for m in range(nb)]
    lid = W.id
    with _Tick(clock, "features: regions"):
        regions = {f: [W.band_region(m, f) for m in range(nb)] for f in FACES}
    carved = {f: [[] for _ in range(nb)] for f in FACES}     # stones laid first in each course: (x0, x1, id)
    placed = []                                               # the stones laid first
    cope_j = {m: W.cope_j.get(m, []) for m in range(nb)}      # the copings' joints over course m: (x, lap)

    def carve(face, m, x0, x1, sid):
        carved[face][m].append((x0, x1, sid))

    reb = line.get("rebuilt")
    STONE_END = dict(type="stone", ref=None)      # a run's end against a stone laid first

    def owner_of(p):
        """The panel a run belongs to: the one a tooth or an edge at its end opens or closes, else the one holding
        its middle."""
        if p["l"]["type"] in ("tooth", "edge"):
            return W.panel_starting(p["l"]["at"])
        if p["r"]["type"] in ("tooth", "edge"):
            return W.panel_ending(p["r"]["at"])
        return W.panel_at((p["a"] + p["b"]) // 2)

    def ends_rule(m, p):
        """A run's first and last stones' lengths from its ends (None where free): at a riser, the stepped section's
        corner stone; at a rebuilt panel's edge, on the panel's side, its long or short stone."""
        h = H[m]
        first = D.corner(h) if p["l"]["type"] in ("riser", "riser-open") else None
        last = D.corner(h) if p["r"]["type"] in ("riser", "riser-open") else None
        if reb and owner_of(p)["work"] != "built":
            if p["l"]["type"] == "edge":
                first = D.edge_stone(m, h, 0)
            if p["r"]["type"] == "edge":
                last = D.edge_stone(m, h, 1)
        return first, last

    def layable(m, a, b, l, r):
        """Whether a run of course m from a to b, with these ends, can be laid in whole stones under its end
        stones' rules: every stone laid first (a head, a tooth, a fallen stone, a through) leaves its runs so."""
        return b >= a and D.run_layable(b - a, H[m], *ends_rule(m, dict(a=a, b=b, l=l, r=r)))

    # ---- the heads: ties and runners alternating, two courses each, under the end's topstone
    t_heads = time.perf_counter()

    def rooms(face, spans, e):
        """The run each spanned course has at the wall's end on a face, with its course."""
        out = []
        for m in spans:
            for run in regions[face][m]:
                if (e == 0 and run["a"] == W.s0) or (e == 1 and run["b"] == W.s1):
                    out.append((run, m))
        return out

    def room_left(run, m, e, x):
        """Whether a head stone x long at end e leaves its course's run nothing, or a run its stones can lay."""
        if x > run["b"] - run["a"]:
            return False
        if e == 0:
            return layable(m, run["a"] + x, run["b"], STONE_END, run["r"])
        return layable(m, run["a"], run["b"] - x, run["l"], STONE_END)

    def head_len(drawn_len, nominal, wide, room_list, sid, avoid=()):
        """A head stone's length: the drawn one if it leaves every spanned course either nothing or a whole stone
        beside it, and its inner end a lap from the joints under and over it (`avoid`: (length, lap)), else the
        nearest that does, first in its own range, then in any a course takes; flagged if so."""
        def fits(x):
            return all(room_left(run, m, e, x) for run, m in room_list) and \
                all(abs(x - y) >= lp for y, lp in avoid)
        for lo_, hi_ in (nominal, wide):
            ok = [x for x in range(lo_, hi_ + 1) if fits(x)]
            if ok:
                x = min(ok, key=lambda v: (abs(v - drawn_len), v))
                if (lo_, hi_) != nominal:
                    W.flags.append(f"{sid}: {x} mm, outside its range {nominal}, to leave whole stones beside it")
                return x
        lens = [run["b"] - run["a"] for run, _ in room_list]
        x = min([drawn_len] + lens)
        W.flags.append(f"{sid}: no length leaves whole stones beside it (rooms {lens}); {x} mm")
        return x

    def end_joints(face, m, e, s_end, lap):
        """The joints fixed before the heads in course m on a face, as lengths from the wall's end e, each with the
        lap a head stone's inner end keeps from it: the course's ends against a feature, a riser or a step."""
        if not 0 <= m < nb:
            return []
        ys = [r_[k] for r_ in regions[face][m] for k, side in (("a", "l"), ("b", "r")) if is_joint(r_[side])]
        return [(abs(y - s_end), lap) for y in ys]

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
            pairs.append((max(j - D.HEAD_COURSES, i0), j))
            j -= D.HEAD_COURSES
        for k, (i, j) in enumerate(reversed(pairs)):
            h = W.Lz[j] - W.Lz[i]
            rng = HS.Stream(seed, f"{hid}/st-{k}", "lay")
            tie = (k % 2 == 0) == tie_first
            spans = list(range(i, j))
            hi_ = D.longest(h)
            avoid = [(top_len, lap_of(H[j]) if j < nb else LAP_MIN)] if j == i1 else []
            # the inner end a lap from the stone under it (the head's last, or the course's fixed joints) and from the
            # joints fixed over it (a riser's course end, a coping's joint)
            avoid_f = {f: avoid + ([(prev_len[f], lap_of(H[i]))] if prev_len[f] is not None else
                                   end_joints(f, i - 1, e, s_end, lap_of(H[i]))) +
                       end_joints(f, j, e, s_end, lap_of(H[j]) if j < nb else LAP_MIN) +
                       [(abs(y - s_end), lp) for y, lp in cope_j[j - 1]] for f in FACES}
            # each face's head stands on that face's own footing: a face takes the pair's courses that stand over
            # its footing at the end (a face never stands under its footing, where the steps' ends or the ground
            # are). A tie runs through both faces only where both stand in all its courses; elsewhere each face
            # that stands lays its own stone, a header or a runner by the head's order, in its standing courses.
            stand = {f: [m for run, m in rooms(f, spans, e)] for f in FACES}
            if tie and all(stand[f] == spans for f in FACES):
                sid = f"{hid}/st-{k}"
                Lh = head_len(rng.randint(*D.HEAD_TIE), D.HEAD_TIE, (D.STONE[0], hi_),
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
                    sp = stand[f]
                    if not sp:
                        continue
                    if sp != list(range(sp[0], sp[-1] + 1)) or sp[-1] != j - 1:
                        raise Refused(f"{hid}/st-{k}: {f} stands in courses {sp} of {spans}, not the pair's top")
                    ia = sp[0]
                    sid = f"{hid}/st-{k}/{f}"
                    hf = W.Lz[j] - W.Lz[ia]
                    hi_f = D.longest(hf)
                    if tie:
                        nominal = (min(D.HEAD_TIE[0], hi_f), min(D.HEAD_TIE[1], hi_f))
                    else:
                        nominal = (min(D.HEAD_RUN[0], hi_f), min(D.HEAD_RUN[1], hi_f))
                    av = avoid_f[f] if ia == i else (avoid + end_joints(f, ia - 1, e, s_end, lap_of(H[ia])) +
                                                     end_joints(f, j, e, s_end, lap_of(H[j]) if j < nb else LAP_MIN) +
                                                     [(abs(y - s_end), lp) for y, lp in cope_j[j - 1]])
                    Lh = head_len(rng.randint(*nominal), nominal, (D.STONE[0], hi_f), rooms(f, sp, e), sid, av)
                    prev_len[f] = Lh
                    if not tie and Lh < D.HEAD_RUN[0]:
                        W.flags.append(f"{sid}: a runner {Lh} mm, under the {D.HEAD_RUN[0]} a runner should be")
                    x0, x1 = (s_end, s_end + Lh) if e == 0 else (s_end - Lh, s_end)
                    placed.append(dict(id=sid, kind="head", role="tie" if tie else "runner", faces=[f], bands=sp,
                                       outline=[[x0, W.Lz[ia]], [x1, W.Lz[ia]], [x1, W.Lz[j]], [x0, W.Lz[j]]]))
                    for m in sp:
                        carve(f, m, x0, x1, sid)
    if clock is not None:
        clock["features: heads"] = clock.get("features: heads", 0.0) + time.perf_counter() - t_heads

    def split(pieces, x0, x1, sid):
        """The pieces less a stone laid first over [x0, x1]."""
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
                q["a"], q["l"] = x1, dict(type="stone", ref=sid)
                nxt.append(q)
        return nxt

    # ---- each course's lengths less the heads: the pieces every later step lays into
    segs = {f: [] for f in FACES}
    for f in FACES:
        for m in range(nb):
            pieces = [dict(r) for r in regions[f][m]]
            for x0, x1, sid in sorted(carved[f][m]):
                pieces = split(pieces, x0, x1, sid)
            segs[f].append(sorted([p for p in pieces if p["b"] > p["a"]], key=lambda d: d["a"]))

    def fixed_of(f, m):
        """Course m's joints fixed before the fill: its pieces' ends that are joints, and the ends of the stones laid
        first in it that are not the wall's or a riser's open end."""
        out = set()
        outer = set()
        for r_ in regions[f][m]:
            if not is_joint(r_["l"]):
                outer.add(r_["a"])
            if not is_joint(r_["r"]):
                outer.add(r_["b"])
        for p in segs[f][m]:
            if is_joint(p["l"]):
                out.add(p["a"])
            if is_joint(p["r"]):
                out.add(p["b"])
        for x0, x1, _ in carved[f][m]:
            out |= {x for x in (x0, x1) if x not in outer}
        return sorted(out)

    # ---- the teeth: every course takes a tooth at each panel boundary and a straight joint at each 1961 edge,
    # chosen from the line's features alone (before any panel's own stones), bottom up
    t_teeth = time.perf_counter()
    fixed = {f: [fixed_of(f, m) for m in range(nb)] for f in FACES}
    cut_report = []
    bl = sorted([(e_, "edge") for e_ in W.edges] + [(sb, "tooth") for sb in W.boundaries])

    def tooth_cands(f, m, sb, kind, bi, p, below_extra=()):
        """Course m's places for the tooth (or the edge's straight joint) at sb in its piece p, in the order they are
        tried, each with whether it keeps its laps from the joints fixed above and below it (`below_extra`: joints
        to be fixed below it, for the look ahead): the kind's teeth, on the course's side first, then the other's;
        then wider, to TOOTH_WIDE; then nearer the boundary than a tooth, since SN10's laps outrank the kind's
        tooth; and only then the same places without the laps."""
        more = any(p["a"] < sb2 < p["b"] for sb2, _ in bl[bi + 1:])
        if kind == "edge":
            cands = [(sb, False)]
        else:
            ti = W.boundaries.index(sb)
            par = HS.h(seed, lid, "tooth", ti) % 2
            d0 = HS.between(HS.h(seed, lid, "tooth", ti, f, m), *D.TOOTH)
            sg = 1 if (m + par) % 2 == 0 else -1
            ds = [sg * d0] + [sg * d for d in range(D.TOOTH[0], D.TOOTH[1] + 1) if d != d0] + \
                 [-sg * d for d in range(D.TOOTH[0], D.TOOTH[1] + 1)] + \
                 [s_ * d for d in range(D.TOOTH[1] + 1, D.TOOTH_WIDE[1] + 1) for s_ in (sg, -sg)] + \
                 [s_ * d for d in range(D.TOOTH[0] - 1, 0, -1) for s_ in (sg, -sg)]
            cands = [(sb + d, True) for d in ds] + [(sb + d, False) for d in ds]
        below_ = list(fixed[f][m - 1]) + list(below_extra) if m > 0 else []
        for x, with_laps in cands:
            if with_laps:
                if any(abs(x - y) < lap_of(H[m]) for y in below_):
                    continue
                if m + 1 < nb and any(abs(x - y) < lap_of(H[m + 1]) for y in fixed[f][m + 1]):
                    continue
                if any(abs(x - y) < lp for y, lp in cope_j[m]):
                    continue
            cut = dict(type=kind, at=sb)
            if x - p["a"] < D.STONE[0] or not layable(m, p["a"], x, p["l"], cut):
                continue
            if p["b"] - x < D.STONE[0] or (not more and not layable(m, x, p["b"], cut, p["r"])):
                continue
            yield x, with_laps

    def next_ok(f, m, sb, bi, x, least):
        """Whether the course over m still has a tooth at sb that keeps its laps, at least `least` off it, once m's
        is at x (a course's tooth is chosen looking one course ahead, so it never leaves the next one boxed in
        between its joints)."""
        if m + 1 >= nb:
            return True
        q = next((q for q in segs[f][m + 1] if q["a"] < sb < q["b"]), None)
        if q is None:
            return True
        return any(wl and abs(x2 - sb) >= least for x2, wl in tooth_cands(f, m + 1, sb, "tooth", bi, q, below_extra=[x]))

    for f in FACES:
        for m in range(nb):
            pieces = segs[f][m]
            for bi, (sb, kind) in enumerate(bl):
                k_ = next((k for k, q in enumerate(pieces) if q["a"] < sb < q["b"]), None)
                if k_ is None:
                    continue
                p = pieces[k_]
                got = None
                if kind == "tooth":     # the first tooth that keeps its laps and leaves the next course a whole
                    for least in (D.TOOTH[0], 1):     # tooth, else one nearer the boundary
                        got = next(((x, wl) for x, wl in tooth_cands(f, m, sb, kind, bi, p)
                                    if wl and next_ok(f, m, sb, bi, x, least)), None)
                        if got is not None:
                            break
                if got is None:
                    got = next(tooth_cands(f, m, sb, kind, bi, p), None)
                if got is None:
                    what = f"the {reb['year']} edge" if kind == "edge" else "the boundary"
                    ends = [(abs(y - sb), y, q_["type"]) for y, q_ in ((p["a"], p["l"]), (p["b"], p["r"]))
                            if is_joint(q_) and abs(y - sb) < D.STONE[0]]
                    if ends:
                        d_, y, t_ = min(ends)
                        cut_report.append(f"{lid} {f} course {m}: {what} at {sb} is the course's end against the "
                                          f"{t_} at {y}, {d_} mm off it (no stone fits between them); the stone at "
                                          f"that end is the panel's that holds its middle")
                    else:
                        cut_report.append(f"{lid} {f} course {m}: {what} at {sb} takes no "
                                          f"{'joint' if kind == 'edge' else 'tooth'} (no place the fill can lay both "
                                          "sides of); the stone across it is the panel's that holds its middle")
                    continue
                x, with_laps = got
                if kind == "tooth" and not with_laps:
                    cut_report.append(f"{lid} {f} course {m}: the tooth at {sb} is at {x}, within a lap of a fixed "
                                      f"joint above or below (no tooth to {D.TOOTH_WIDE[1]} mm clears them)")
                elif kind == "tooth" and abs(x - sb) > D.TOOTH[1]:
                    W.flags.append(f"{lid} {f} course {m}: the tooth at {sb} is {abs(x - sb)} mm off it, over {D.TOOTH[1]}")
                elif kind == "tooth" and abs(x - sb) < D.TOOTH[0]:
                    W.flags.append(f"{lid} {f} course {m}: the tooth at {sb} is {abs(x - sb)} mm off it, under "
                                   f"{D.TOOTH[0]}, to keep its laps")
                left, right = dict(p), dict(p)
                left["b"], left["r"] = x, dict(type=kind, at=sb)
                right["a"], right["l"] = x, dict(type=kind, at=sb)
                pieces[k_:k_ + 1] = [left, right]
                fixed[f][m] = sorted(set(fixed[f][m] + [x]))
            segs[f][m] = pieces
    if clock is not None:
        clock["fill: teeth"] = clock.get("fill: teeth", 0.0) + time.perf_counter() - t_teeth

    def where(face, m, s):
        for p in segs[face][m]:
            if p["a"] <= s < p["b"]:
                return p
        return None

    def carve_in(face, m, x0, x1, sid):
        carve(face, m, x0, x1, sid)
        segs[face][m] = sorted([p for p in split(segs[face][m], x0, x1, sid) if p["b"] > p["a"]],
                               key=lambda d: d["a"])

    def lap_blocks(m, faces):
        """The joints a stone laid first in course m keeps its free ends a lap from, with each one's lap: those fixed
        in the courses above and below it, and the copings' joints over it (the fill keeps its own joints clear of
        all)."""
        out = []
        for f in faces:
            for mm, lap in ((m - 1, lap_of(H[m])), (m + 1, lap_of(H[m + 1]) if m + 1 < nb else 0)):
                if not 0 <= mm < nb:
                    continue
                for p in segs[f][mm]:
                    for side, y in (("l", p["a"]), ("r", p["b"])):
                        if is_joint(p[side]):
                            out.append((y, lap))
                for x0, x1, _ in carved[f][mm]:
                    out += [(x0, lap), (x1, lap)]
        return out + list(cope_j[m])

    def clear_of(x, blocks):
        return all(abs(x - y) >= lp for y, lp in blocks)

    def laps_clear(m, ends, faces):
        blocks = lap_blocks(m, faces)
        return all(clear_of(x, blocks) for x in ends)

    def near_boundary(x0, x1):
        """Whether a stone over [x0, x1] comes within FALL_CLEAR of a panel's boundary or a rebuilt panel's edge."""
        return any(x0 - D.FALL_CLEAR < sb < x1 + D.FALL_CLEAR for sb, _ in bl)

    # ---- the fallen stones the facts give (the stair's face; a mortared stone holds)
    t_falls = time.perf_counter()
    fall_report = []
    for fp in line.get("falls", []):
        s, z = fp["s"], fp["z"]
        if fp["held"]:
            fall_report.append(dict(s=s, z=z, result="held (the facts: bedded in mortar, in the rebuilt panel or a "
                                                     "patched hole)"))
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
        rng = W.stream(pn["id"], "fallen", s)  # (the fall point is a fact, an integer: it keys only its own draw)
        h = H[m]
        L0 = rng.randint(*D.drawn(h))
        o0 = rng.randint(0, L0 - 1)
        best = None
        # the stone over the fall point nearest its drawn length and offset, kept from the boundaries where it can be:
        # the least cost over every length and place, the shortest length and then the lowest place on a tie. Each
        # end's own conditions are found once per place; for each length the places are searched outward from the
        # drawn offset, so the first clear place found is that length's least
        blocks = lap_blocks(m, ["stair"])
        okL = {x0: layable(m, p["a"], x0, p["l"], STONE_END) and (x0 == p["a"] or clear_of(x0, blocks))
               for x0 in range(max(s - D.longest(h) + 1, p["a"]), min(s, p["b"] - D.STONE[0]) + 1)}
        okR = {x1: layable(m, x1, p["b"], STONE_END, p["r"]) and (x1 == p["b"] or clear_of(x1, blocks))
               for x1 in range(max(s + 1, p["a"] + D.STONE[0]), min(s + D.longest(h), p["b"]) + 1)}
        t_x = s - o0
        for Lf in range(D.STONE[0], D.longest(h) + 1):
            if best is not None and abs(Lf - L0) > best[0]:
                if Lf > L0:
                    break
                continue
            lo_x, hi_x = max(s - Lf + 1, p["a"]), min(s, p["b"] - Lf)
            if lo_x > hi_x:
                continue
            got = None
            for d in range(0, max(abs(t_x - lo_x), abs(hi_x - t_x)) + 1):
                if got is not None and got[0] < 100000:
                    break
                for x0 in ((t_x - d, t_x + d) if d else (t_x,)):
                    if not lo_x <= x0 <= hi_x or not okL.get(x0) or not okR.get(x0 + Lf):
                        continue
                    c_ = 100000 * near_boundary(x0, x0 + Lf) + abs(Lf - L0) + d
                    if got is None or c_ < got[0]:
                        got = (c_, x0)
            if got is not None and (best is None or got[0] < best[0]):
                best = (got[0], got[1], got[1] + Lf)
        if best is None:
            fall_report.append(dict(s=s, z=z, result=f"no room for a fallen stone in course {m}: not placed"))
            continue
        cost, x0, x1 = best
        if cost >= 100000:
            W.flags.append(f"{lid}: the fallen stone at {s} lies within {D.FALL_CLEAR} mm of a panel's boundary")
        sid_tmp = f"{pn['id']}/stair/co-{m}/fallen-{len(fall_report)}"
        placed.append(dict(id=sid_tmp, kind="face", faces=["stair"], bands=[m], fallen=True, panel=pn["id"],
                           outline=[[x0, W.Lz[m]], [x1, W.Lz[m]], [x1, W.Lz[m + 1]], [x0, W.Lz[m + 1]]],
                           fact=dict(s=s, z=z)))
        carve_in("stair", m, x0, x1, sid_tmp)
        fall_report.append(dict(s=s, z=z, result=f"fell: course {m}, {x0} to {x1}", id=sid_tmp))
    if clock is not None:
        clock["features: falls"] = clock.get("features: falls", 0.0) + time.perf_counter() - t_falls

    # ---- the through stones: about one a metre in each panel, in the course nearest the face's middle height
    t_thr = time.perf_counter()
    through_report = []
    for pn in W.panels:
        lo, hi = pn["s"]
        rng = W.stream(pn["id"], "throughs")
        xc = lo + rng.randint(*D.THROUGH_FIRST)
        j = 0
        while xc < hi - D.THROUGH_CLEAR:
            Lt = rng.randint(*D.THROUGH)
            done = False
            ff, cc = W.foot_at("stair", xc), W.ceiling_at(xc)
            if xc - Lt // 2 >= lo + D.THROUGH_CLEAR and xc - Lt // 2 + Lt <= hi - D.THROUGH_CLEAR and cc > ff:
                zmid = (ff + cc) // 2
                order = sorted(range(nb), key=lambda m: (abs((W.Lz[m] + W.Lz[m + 1]) // 2 - zmid), m))[:4]
                for m in order:
                    Lm = min(Lt, D.longest(H[m]))
                    if Lm < D.THROUGH[0]:
                        continue
                    x0, x1 = xc - Lm // 2, xc - Lm // 2 + Lm
                    ok = False
                    for dx in sorted(range(-D.THROUGH_SHIFT, D.THROUGH_SHIFT + 1, SHIFT_STEP), key=lambda v: (abs(v), v)):
                        if x0 + dx < lo + D.THROUGH_CLEAR or x1 + dx > hi - D.THROUGH_CLEAR:
                            continue
                        ok = True
                        for f in FACES:
                            p = where(f, m, xc + dx)
                            if p is None or not (p["a"] <= x0 + dx and x1 + dx <= p["b"]) or \
                                    not layable(m, p["a"], x0 + dx, p["l"], STONE_END) or \
                                    not layable(m, x1 + dx, p["b"], STONE_END, p["r"]):
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
                            carve_in(f, m, x0, x1, sid)
                        j += 1
                        done = True
                        break
            if not done:
                through_report.append(dict(panel=pn["id"], at=xc, result="no course with room on both faces"))
            xc += rng.randint(*D.THROUGH_EVERY)
    if clock is not None:
        clock["features: throughs"] = clock.get("features: throughs", 0.0) + time.perf_counter() - t_thr

    # ---- the fill: each course from the foot, each free length by choosing its stones' lengths
    t_fill = time.perf_counter()
    fixed = {f: [fixed_of(f, m) for m in range(nb)] for f in FACES}
    stones = list(placed)
    joints = {f: [[] for _ in range(nb)] for f in FACES}
    fill_report = []
    hidden_runs = []
    pfill = clock.setdefault("panel fill", {}) if clock is not None else None

    for f in FACES:
        for m in range(nb):
            h = H[m]
            lapm = lap_of(h)
            # every joint in the course below: its fill's, and the ends of the stones laid first in it that meet
            # another such stone (a fallen stone against a head)
            below = [(y - lapm, y + lapm) for y in sorted(set(joints[f][m - 1]) | set(fixed[f][m - 1]))] if m > 0 else []
            above = []
            if m + 1 < nb:
                lu = lap_of(H[m + 1])
                above = [(y - lu, y + lu) for y in fixed[f][m + 1]]
            above += [(y - lp, y + lp) for y, lp in cope_j[m]]
            win = below + above
            ordinal = {}
            for p in segs[f][m]:
                a, b = p["a"], p["b"]
                pn = owner_of(p)
                if not laid.get((pn["id"], f), True):
                    hidden_runs.append(dict(face=f, course=m, a=a, b=b, panel=pn["id"]))
                    continue
                t0 = time.perf_counter()
                o = ordinal.get(pn["id"], 0)
                ordinal[pn["id"]] = o + 1
                rng = W.stream(pn["id"], f, "co", m, "lay", o)
                lmax = D.longest(h)
                dlo, dhi = D.drawn(h)
                first, last = ends_rule(m, p)
                tgt = lambda i, rng=rng: rng.randint(dlo, dhi)  # noqa: E731
                J, how = None, None
                for how_, lmin_, win_, first_, last_ in (
                        ("bond", D.STONE[0], win, first, last),
                        ("bond, the end stones' rule dropped", D.STONE[0], win, None, None),
                        ("bond below only", D.STONE[0], below, None, None),
                        ("no bond", D.STONE[0], [], None, None),
                        (f"stones under {D.STONE[0]} mm, bonded", D.SHORT, win, None, None),
                        (f"stones under {D.STONE[0]} mm", D.SHORT, [], None, None)):
                    if how_ == "bond, the end stones' rule dropped" and first is None and last is None:
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
                                            r=p["r"]["type"], panel=pn["id"]))
                for x0, x1 in zip(J, J[1:]):
                    st = dict(id=None, kind="face", faces=[f], bands=[m], panel=pn["id"],
                              outline=[[x0, W.Lz[m]], [x1, W.Lz[m]], [x1, W.Lz[m + 1]], [x0, W.Lz[m + 1]]])
                    if how != "bond":
                        st["relaxed"] = how
                    stones.append(st)
                joints[f][m] += [x for x in J[1:-1]] + ([a] if is_joint(p["l"]) else []) + \
                    ([b] if is_joint(p["r"]) else [])
                if pfill is not None:
                    pfill[pn["id"]] = pfill.get(pn["id"], 0.0) + time.perf_counter() - t0
            joints[f][m] = sorted(set(joints[f][m]) | set(fixed[f][m]))
    if clock is not None:
        clock["fill: courses"] = clock.get("fill: courses", 0.0) + time.perf_counter() - t_fill

    # ---- the fall goes on: a stone whose bed lay all but wholly over a fallen one falls too
    t_ids = time.perf_counter()
    changed = True
    while changed:
        changed = False
        gone = [st for st in stones if st.get("fallen")]
        for st in stones:
            if st.get("fallen") or st["kind"] != "face" or "stair" not in st["faces"] or st.get("panel") is None:
                continue
            if W.panel_at(_xs(st)[0])["work"] != "built":
                continue
            m = st["bands"][0]
            x0, x1 = _xs(st)
            lost = sum(max(0, min(x1, _xs(g)[1]) - max(x0, _xs(g)[0])) for g in gone if g["bands"][-1] == m - 1)
            if lost * FALLS_WHEN[1] > FALLS_WHEN[0] * (x1 - x0):
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
    for sl in sorted(W.slabs, key=lambda d: d["outline"][0][0]):
        c = cop.get(sl["panel"], 0)
        cop[sl["panel"]] = c + 1
        stones.append(dict(id=f"{sl['panel']}/cp-{c}", kind="coping", faces=list(FACES), bands=[sl["bedIndex"]],
                           panel=sl["panel"], outline=sl["outline"], run=sl["run"]))
    for ft in W.features:
        stones.append(dict(id=ft["id"], kind=ft["kind"], faces=list(FACES), bands=_bands_of(W, ft["outline"]),
                           outline=ft["outline"], cap=ft.get("cap", False)))
    # the step ends, as the wall's stair face sees them
    cells = []
    for st in steps_out["steps"]:
        rows = st["rows"] if st.get("rest") else [dict(y=st["y"])]
        for r_ in rows:
            y0, y1 = r_["y"]
            cells.append(dict(id=step_end_id(steps_out, st["id"], W.side, y0), outline=[[y0, st["z"][0]], [y1, st["z"][0]],
                                                                                      [y1, st["z"][1]],
                                                                                      [y0, st["z"][1]]]))
    hidden = sorted(set((pid, f) for (pid, f), v in laid.items() if not v and pid.startswith(lid + "/")))
    out = dict(
        id=lid, flight=flight["id"], side=W.side, s=[W.s0, W.s1], goings=goings,
        regions={f: [[dict(a=p["a"], b=p["b"], l=p["l"]["type"], r=p["r"]["type"]) for p in regions[f][m]]
                     for m in range(nb)] for f in FACES},
        features=[dict(id=ft["id"], kind=ft["kind"], at=ft.get("at"), bed=ft["bed"], head=ft.get("head"),
                       cap=ft.get("cap", False)) for ft in W.features],
        risers=W.risers,
        copingRuns=W.cruns,
        idealBed=[list(p) for p in W.idealBed],
        pitch=flight["pitch"],
        lines=[dict(z=z, kind=k_, src=s_) for z, k_, s_ in zip(W.Lz, W.Lkind, W.Lsrc)],
        panels=W.panels, edges=W.edges, boundaries=W.boundaries,
        footing={f: [[a, b, z] for a, b, z, _ in W.foot[f]] for f in FACES},
        ground=line["ground"],
        ceiling=[dict(s=c["s"], z=c["z"], top=c["top"], owner=c["owner"], kind=c["kind"]) for c in W.ceiling],
        stones=sorted(stones, key=lambda s: s["id"]),
        cells=cells,
        hidden=[list(x) for x in hidden],
        hiddenRuns=hidden_runs,
        joints={f: [list(js) for js in joints[f]] for f in FACES},
        copingJoints={str(m): [list(v) for v in cope_j[m]] for m in range(nb) if cope_j[m]},
        segments={f: [[dict(a=p["a"], b=p["b"], l=p["l"], r=p["r"]) for p in segs[f][m]] for m in range(nb)]
                  for f in FACES},
        report=dict(falls=fall_report, throughs=through_report, cuts=cut_report, fills=fill_report, flags=W.flags),
    )
    if clock is not None:
        clock["fill: falls on, ids, output"] = clock.get("fill: falls on, ids, output", 0.0) + time.perf_counter() - t_ids
    return out


def _xs(st):
    xs = [p[0] for p in st["outline"]]
    return min(xs), max(xs)


def _bands_of(W, poly):
    zs = [p[1] for p in poly]
    lo, hi = min(zs), max(zs)
    return [m for m in range(len(W.Lz) - 1) if W.Lz[m] < hi and W.Lz[m + 1] > lo]


# ---------------------------------------------------------------------------------------------------------------
# The whole: the stair's steps and its walls

def laid_table(facts):
    """(panel id, face) -> laid, from the facts' visibility (walls.visibility.panels); None when the facts have none,
    so every face is laid."""
    vis = facts["walls"].get("visibility")
    if not vis:
        return None
    return {(pid, f): bool(v[f]["laid"]) for pid, v in vis["panels"].items() for f in FACES}


def lay(facts, data, reseed=None, goings=None, clock=None):
    """The stair's steps and its walls from the facts and the data (load_data: the wall kind's params and the pack's
    walling table), by the workings the facts name. `goings` overrides the kind's laid goings (the variant's)."""
    seed = facts["worldSeed"]
    slab = facts["sources"]["stepStone"]
    Ds = rules_for(facts, data)
    goings = Ds.GOINGS_LAID if goings is None else goings
    width = None
    steps = []
    with _Tick(clock, "steps"):
        for fl in facts["stair"]["flights"]:
            width = fl["width"]
            steps.append(lay_steps(fl, seed, slab, fl["width"], Ds))
    laid = laid_table(facts)
    walls = []
    for ln in facts["walls"]["lines"]:
        fl = facts["stair"]["flights"][ln["flight"]]
        D = rules_for(facts, data, ln)
        w = lay_line(ln, fl, steps[ln["flight"]], seed, D, reseed, goings, laid, clock)
        if laid is not None:
            missing = [pn["id"] for pn in w["panels"] if (pn["id"], "stair") not in laid]
            if missing:
                raise Refused(f"the facts' visibility has no entry for {', '.join(missing)}")
        walls.append(w)
    return dict(what="R1's layout (port step 2b): the gully's cheek walls as elevations and its steps in plan, integer "
                     "mm, laid by blender/generators/masonry.py from reviews/lt1/port/2b/r1/facts.json",
                worldSeed=seed, width=width, goings=goings, steps=steps, walls=walls)
