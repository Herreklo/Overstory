"""R2a's stones: the step as a part function whose inputs are facts, made at L0 and L1 from one seed and outline on the
block machinery (block.py); its checks, its export and its quick sheet (port step 2b, rung R2a; the design:
reviews/lt1/port/2b/design.md, SN1, SN3, SN4, SN8, SN9; the contract: reviews/lt1/port/2b/r2a/stones/plan.md; the
note: reviews/lt1/port/2b/r2a/stones/blender.md).

A step stone is a rigid convex block, the stair's rise high, laid on its natural bed (the laminae level): its top is
the bedding plane (a bed face, the tread's top), its front and a joint end are split across the laminae (split faces),
its bed, its back under the next step and its ends in the walls are never seen and are not drawn. Every exposed arris
is chamfered at L0 (SN4); L1 is the same planes without the chamfers, its lit line kept in the shading by the edge
distances (UV6, UV7). The wear (wear.py's laws: footfall times years over the stone's hardness, where feet go) is
subtracted as a height field, a grid only where it varies; nothing else moves a vertex. A corner the record says was
broken is a planar cut (SN4: chips where a fact puts them).

Every value comes from data, never a constant in code (Øystein, 23 October; the design's Done, 7b):
- the stair's facts (rise, going, the flight's width and lean) from the plan stage's output (fixtures/golden/stair);
  the stone's history (its years, its broken corner) from the life stage's; the footfall and the dates from the record
  (fixtures/records/st-gully.json); the world seed and the show year from the pack;
- the working's numbers from R1's walling table (packs/<pack>/walling.json), by the working R1's facts name: the steps'
  lap and joint, a wall's joint, batter and top thickness, a coping's overhang and how proud it stands; and each
  stone's outline from R1's laying (masonry.lay on R1's facts, kinds/wall.json's plan params and the walling table, all
  at one pinned commit);
- the wear rate and how a corner breaks from the material the steps' working names (packs/<pack>/materials/);
- the levels' errors from the kind's table (kinds/stair.json, kinds/wall.json: levels), the one source;
- the part's own numbers (chamfer, facets, chips, skirt, wear grid, patch sets) from its definition
  (packs/<pack>/parts/<part>.json: params), through `param`.
Each is read through one function that notes its source, and none has a default here: a missing key is an error.
What stays in code is the rule of any stone (convex, planar, level beds, no rake, square arrises, SN9's limits), the
wear's laws (wear.py, and where feet land on a tread), the judging rig (the 28 mm lens at 2560 x 1440), the contract's
encodings and the hashing (reviews/lt1/port/2b/r2a/stones/blender.md, Data and code).

    PY=/Applications/Blender.app/Contents/Resources/5.2/python/bin/python3.13
    $PY blender/parts/stone/slate/stones.py flight               every stone of the gully's flights: SN8's pooled share
    $PY blender/parts/stone/slate/stones.py check                build the step and the machinery's variants, check
    blender -b --factory-startup --python blender/parts/stone/slate/stones.py -- export      and export, read back
    blender -b --factory-startup --python blender/parts/stone/slate/stones.py -- sheet       the quick sheet

Lengths in metres inside, integer millimetres in facts and definitions. The stone's frame: x along it from its left
end (looking up the stair), y back from its front (the riser), z up from its bed.
"""

import json
import math
import os
import subprocess
import sys
from fractions import Fraction

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
for _p in (HERE, os.path.join(ROOT, "blender", "resolver"), os.path.join(ROOT, "blender", "generators"),
           os.path.join(ROOT, "blender", "tools")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import block as B  # noqa: E402
import hashing as HS  # noqa: E402  (the one hash spec)
import wear as WR  # noqa: E402  (the shared laws of wear)

PACK = "packs/stavanger-1989"
GENERATED = "unity/Assets/Experiments/LT1/R2a/Generated"
MANIFEST = "blender/parts/stone/slate/stones.manifest.json"
SHEET = "reviews/lt1/port/2b/r2a/stones/blender-sheet.png"
R1_FACTS = "reviews/lt1/port/2b/r1/facts.json"
TOOL = "stones 1"

# The judging rig (plan.md, The judging set; SN4 and SN8 are written against it): the 28 mm lens on a 24 mm high
# frame (46.4 degrees vertical), 2560 x 1440, one sample a pixel. A measuring tool's, not the town's.
RIG = dict(focalMm=28.0, sensorMm=24.0, width=2560, height=1440)

# SN8's thin-triangle gate and SN9's limits: the rules of any part, as the design states them.
GATE = dict(thinPx=2.0, thinShare=0.10, medianAreaPx=10.0, l0Distance=8.0, l1Distance=20.0)
# The gate's view: SN8's measure as the judging set takes it (plan.md, The measures), face-on with 20 degrees of top
# seen at each level's far edge, as LT1R2a's Triangles does (piece.View("8"), ("20")). The other views are measured
# and reported, not gated: from eye height at 8 and 20 m a tread's top is seen at 11 and 4 degrees, where any cut of
# it is under 2 px (at 20 m the whole tread is), and 40 degrees off a chamfer on the far end is seen along its length.
GATED_VIEWS = ("face-on 20",)
SN9 = dict(planarMm=0.1, sliverMm=50.0, sliverDeg=25.0, chamferPx=2.0, contactMm=3.0)
COLLAPSE_MM = SN9["planarMm"] / 2      # how far a short edge's collapse may bend a face (block.collapse)


def _f(px_mm):
    return px_mm / 1000.0


def focal_px():
    return RIG["height"] * RIG["focalMm"] / RIG["sensorMm"]


# -- data -------------------------------------------------------------------------------------------------------------

def _load(rel):
    with open(os.path.join(ROOT, rel)) as fh:
        return json.load(fh)


def committed(rel, commit="HEAD"):
    """The file as the commit holds it (git show), so a build reads another session's data at a commit and never its
    work in progress in this shared checkout."""
    return subprocess.run(["git", "-C", ROOT, "show", f"{commit}:{rel}"], capture_output=True, check=True).stdout


_TRACKED = None


def tracked(rel):
    """Whether git holds the file: another session's data is read only once it is committed, so a build at a commit
    never depends on work in progress beside it."""
    global _TRACKED
    if _TRACKED is None:
        try:
            out = subprocess.run(["git", "-C", ROOT, "ls-files"], capture_output=True, text=True, check=True).stdout
            _TRACKED = set(out.splitlines())
        except (OSError, subprocess.CalledProcessError):
            _TRACKED = set()
    return rel in _TRACKED


def clean(rel):
    """Tracked and with no uncommitted change."""
    if not tracked(rel):
        return False
    r = subprocess.run(["git", "-C", ROOT, "diff", "--quiet", "HEAD", "--", rel], capture_output=True)
    return r.returncode == 0


def head():
    try:
        return subprocess.run(["git", "-C", ROOT, "rev-parse", "--short", "HEAD"], capture_output=True, text=True,
                              check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


class Data:
    """Every input a stone reads, each through one function that notes where it came from (the sidecar prints the
    list), so moving a value to another file is a one-line change here."""

    def __init__(self, commit=None):
        self.src = {}
        # one commit for every file another session owns, pinned once, so a commit landing mid-run cannot mix two (a
        # run's workers are handed their parent's)
        self.commit = commit or subprocess.run(["git", "-C", ROOT, "rev-parse", "HEAD"], capture_output=True,
                                               text=True, check=True).stdout.strip()
        self.pack = _load(f"{PACK}/pack.json")
        self.materials = {}
        self.stair = _load("kinds/stair.json")
        self.wall = self.at_commit("kinds/wall.json") if tracked("kinds/wall.json") else None
        self.walling = self.at_commit(f"{PACK}/walling.json") if tracked(f"{PACK}/walling.json") else None
        self.record = _load("fixtures/records/st-gully.json")
        self.plan = _load("fixtures/golden/stair/plan.json")["output"]
        self.life = _load("fixtures/golden/stair/life.json")["output"]
        self.patches = _load("blender/parts/stone/slate/patches.manifest.json")

    def at_commit(self, rel):
        """A JSON file another session owns, as the pinned commit holds it."""
        return json.loads(committed(rel, self.commit))

    def laying(self):
        """R1's laying (blender/generators/masonry.py, lay) made in memory from its facts and its data, every one of
        the three as the pinned commit holds it: never its git-ignored layout.json, which a run beside this one may
        rewrite, and never masonry.py's work in progress in this checkout. Only hashing.py, which masonry imports,
        is read from the checkout, so it must be unchanged."""
        if getattr(self, "_laying", None) is None:
            if not clean("blender/resolver/hashing.py"):
                raise ValueError("blender/resolver/hashing.py has uncommitted changes: R1's laying would not be the "
                                 "commit's")
            import types
            rel = "blender/generators/masonry.py"
            M = types.ModuleType("masonry_at_commit")
            M.__file__ = os.path.join(ROOT, rel)
            exec(compile(committed(rel, self.commit), f"{rel}@{self.commit[:7]}", "exec"), M.__dict__)
            data = dict(kind=self.at_commit("kinds/wall.json")["stages"]["plan"]["params"],
                        walling=self.at_commit(f"{PACK}/walling.json"))
            self._laying = M.lay(self.at_commit(R1_FACTS), data)
            self.note("laying", "R1 round 2", f"{rel}: lay({R1_FACTS}, kinds/wall.json plan params, "
                                              f"{PACK}/walling.json), all at {self.commit[:7]}")
        return self._laying

    def note(self, name, value, source):
        self.src[name] = dict(value=value, source=source)
        return value

    # the pack
    def world_seed(self):
        return self.note("worldSeed", self.pack["worldSeed"], f"{PACK}/pack.json: worldSeed")

    def show_year(self):
        return self.note("showYear", self.pack["showYear"], f"{PACK}/pack.json: showYear")

    # the record
    def built(self):
        ev = next(e for e in self.record["events"] if e["kind"] == "built")
        return self.note("built", ev["at"]["year"], f"fixtures/records/st-gully.json: {ev['id']} (built)")

    def footfall(self, year):
        use = [u for u in self.record["use"] if u["from"]["year"] <= year]
        u = max(use, key=lambda u: u["from"]["year"])
        return self.note("footfall", u["footfall"], f"fixtures/records/st-gully.json: use from {u['from']['year']}")

    # the material: the steps' working's (a stone's wear and how its corners break are its material's)
    def material(self):
        """The material the stair's steps are of, by their working (R1's facts: stair.working; the walling table's
        working names its material): packs/<pack>/materials/<material>.json, read from the checkout."""
        name, w = self.steps_working()
        mat = w["material"]
        if mat not in self.materials:
            rel = f"{PACK}/materials/{mat}.json"
            if not os.path.exists(os.path.join(ROOT, rel)):
                raise ValueError(f"{PACK}/walling.json: workings.{name} names material {mat!r}, and {rel} does not exist")
            self.materials[mat] = (_load(rel), rel)
        return self.materials[mat]

    def material_value(self, key):
        m, rel = self.material()
        if key not in m:
            raise ValueError(f"{rel} has no {key}: the step's material must give it (schemas/material.schema.json)")
        return m[key], rel

    def wear_rate_mm(self):
        """mm a century at 100,000 footfalls a year on a flight 3.2 m wide (wear.py, depth)."""
        v, rel = self.material_value("wearUmPerCentury")
        return self.note("wearMmPerCentury", v / 1000.0, f"{rel}: wearUmPerCentury")

    def corner_break(self):
        """How a corner breaks off a step's nosing (the chip rule's material half): the bite along the step and back
        from the nosing per mille of its size, how deep, and whether it goes down to a bedding plane."""
        v, rel = self.material_value("cornerBreak")
        return self.note("cornerBreak", v, f"{rel}: cornerBreak")

    # the stair's working in R1's walling table
    def steps_working(self):
        """The working the stair's steps were laid in (R1's facts: stair.working, dry-split-1874 for the gully) and
        its entry in the walling table, both as the pinned commit holds them."""
        name = self.r1_facts()["stair"].get("working")
        if not name:
            raise ValueError(f"{R1_FACTS} names no stair.working at {self.commit[:7]}")
        w = self.working(name)
        if "steps" not in w:
            raise ValueError(f"{PACK}/walling.json: workings.{name} has no steps, and the stair is laid in it")
        self.note("stairWorking", name, f"{R1_FACTS}: stair.working")
        return name, w

    def steps_value(self, key):
        name, w = self.steps_working()
        if key not in w["steps"]:
            raise ValueError(f"{PACK}/walling.json: workings.{name}.steps has no {key}")
        return name, w["steps"][key]

    def tread_joint(self):
        """[least, most] mm between two stones of a step: the working's (R1's walling table, which R1 laid by; the
        stair kind's own [4, 12] builds 2a's baseline and is not read here)."""
        name, v = self.steps_value("jointMm")
        return self.note("treadJointMm", list(v), f"{PACK}/walling.json: workings.{name}.steps.jointMm")

    def tread_lap(self):
        """[least, most] mm a step lies on the one below: the working's (R1's walling table; the stair kind's own
        lap of 100 builds 2a's baseline and is not read here)."""
        name, v = self.steps_value("lapMm")
        return self.note("treadLapMm", list(v), f"{PACK}/walling.json: workings.{name}.steps.lapMm")

    # the levels: one source, the kind's table (design.md SN8)
    def level_error(self, part, level):
        """A level's geometric error (mm) for a part's stones: its kind's (kinds/<kind>.json: levels), the one source;
        the stair kind's from the checkout, the wall kind's at the pinned commit (the commit R1 laid by)."""
        rel = KIND_FILES[part]
        k = self.stair if rel == "kinds/stair.json" else self.wall
        if k is None:
            raise ValueError(f"{rel} is not tracked, so no level's error can be read for {part}")
        lv = k.get("levels", {}).get(level, {})
        if "errorMm" not in lv:
            raise ValueError(f"{rel}: levels.{level} has no errorMm")
        at = "" if rel == "kinds/stair.json" else f" (at {self.commit[:7]})"
        return self.note(f"{part}.{level}.errorMm", lv["errorMm"], f"{rel}: levels.{level}.errorMm{at}")

    # the face patches
    def slice_of(self, name):
        names = list(self.patches["patches"])
        return names.index(name)

    def patch_mm(self):
        """A face patch's side in whole mm (patches.manifest.json: texels x mmPerTexel): a face's offset into its patch
        is drawn within it."""
        return self.note("patchMm", int(self.patches["texels"] * self.patches["mmPerTexel"]),
                         "blender/parts/stone/slate/patches.manifest.json: texels x mmPerTexel")

    # R1's walling: a wall stone's working, and the fields the table has no key for yet
    def r1_facts(self):
        if getattr(self, "_r1", None) is None:
            self._r1 = self.at_commit(R1_FACTS)
        return self._r1

    def panel_working(self, wall_id, panel):
        """The working a panel of a wall was laid in, and the year: R1's facts' (the wall's working where the panel is
        as built; the line's rebuilt working and year where the panel is its rebuild), as the pinned commit holds
        them."""
        W = self.r1_facts()["walls"]
        line = next(ln for ln in W["lines"] if ln["id"] == wall_id)
        if panel["work"] == "built":
            return (self.note("wallWorking", W["working"], f"{R1_FACTS}: walls.working ({panel['id']} as built)"),
                    self.note("wallLaid", W["built"], f"{R1_FACTS}: walls.built"))
        rb = line["rebuilt"]
        return (self.note("wallWorking", rb["working"], f"{R1_FACTS}: {wall_id} rebuilt.working ({panel['id']})"),
                self.note("wallLaid", rb["year"], f"{R1_FACTS}: {wall_id} rebuilt.year"))

    def wall_side(self, wall_id):
        """+1 for a wall on the stair's right looking up it, -1 on its left (R1's facts: the line's side)."""
        line = next(ln for ln in self.r1_facts()["walls"]["lines"] if ln["id"] == wall_id)
        return line["side"]

    def working(self, name):
        if not self.walling or name not in self.walling["workings"]:
            raise ValueError(f"no working {name!r} in {PACK}/walling.json at {self.commit[:7]}")
        return self.walling["workings"][name]

    def walling_value(self, name, key):
        """One value of a working of R1's walling table, as the pinned commit holds it, noted with where it came from.
        There is no default: a working without the key is an error (schemas/walling.schema.json requires it)."""
        w = self.working(name)
        if key not in w:
            raise ValueError(f"{PACK}/walling.json: workings.{name} has no {key} (at {self.commit[:7]})")
        return self.note(f"{name}.{key}", w[key], f"{PACK}/walling.json: workings.{name}.{key}")

    def wall_joint(self, name):
        """[least, most] mm of a joint between two stones of a wall (the faces' and the copings')."""
        return list(self.walling_value(name, "jointMm"))

    def batter(self, name):
        """How far the face leans back for its height, as whole numbers [back, up]."""
        return list(self.walling_value(name, "batterPerHeight"))

    def top_thick(self, name):
        """The wall's thickness at its top, under the coping (mm)."""
        return self.walling_value(name, "topThickMm")

    def cope_over(self, name):
        """How much wider a standing wall's coping is than the wall's top (mm), its overhangs on both faces together."""
        return self.walling_value(name, "copeOverMm")

    def cope_proud(self, name):
        """[least, most] mm a coping's front stands proud of the face under it (the rest of copeOver at its back)."""
        return list(self.walling_value(name, "copeProudMm"))


# The part's own numbers are its definition's params (packs/<pack>/parts/stone/<part>.json: params, each a value with
# the note that gives its reason; schemas/part.schema.json). stones.py keeps no default: each is read only through
# param(), and a missing key is an error.
def param(part, defn, key, data=None):
    """A part's number: its definition's params.<key>.value."""
    held = (defn or {}).get("params", {})
    if key not in held:
        raise ValueError(f"{PACK}/parts/stone/{part}.json has no params.{key}")
    v = held[key]["value"]
    if data is not None:
        data.note(f"{part}.{key}", v, f"{PACK}/parts/stone/{part}.json: params.{key}")
    return v


def definition(part):
    return _load(f"{PACK}/parts/stone/{part}.json")


# -- the specimen -----------------------------------------------------------------------------------------------------

def ordinary_steps(data, fid):
    """A flight's ordinary steps (SN3): not the first, whose block runs under the lane; not a rest; not the last,
    which nothing laps. [(index, step id)], by index."""
    plan = data.plan
    F = plan["flights"][fid]
    steps = sorted((s for s in plan["steps"].values() if s["flight"] == fid), key=lambda s: s["index"])
    ids = {s["index"]: k for k, s in plan["steps"].items() if s["flight"] == fid}
    n = len(steps)
    return [(s["index"], ids[s["index"]]) for s in steps
            if 0 < s["index"] < n - 1 and s["D"] <= F["setout"]["g"] + 0.001]


def step_facts(data, fid, sid, stone):
    """One laid stone's facts, from R1's laying (its outline, the step's joint and the next step's front) and the
    stair's life stage (placed, its broken corner and fill): what the part function takes."""
    world = data.world_seed()
    plan = data.plan
    F = plan["flights"][fid]
    lay = data.laying()
    fl = next(f for f in lay["steps"] if f["id"] == fid)
    laid = {s["id"]: s for s in fl["steps"]}
    idx = plan["steps"][sid]["index"]
    nid = next(k for k, s in plan["steps"].items() if s["flight"] == fid and s["index"] == idx + 1)
    st, nxt = laid[sid], laid[nid]
    xs = [p[0] for p in stone["outline"]]
    ys = [p[1] for p in stone["outline"]]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    half = fl["half"]
    jw = st["joint"][1] - st["joint"][0]

    def end(x):
        return dict(kind="walled") if abs(x) == half else dict(kind="joint", jointMm=jw)

    stone_id = stone["id"]
    fill = data.life["fills"].get(f"{stone_id}/0")
    year = data.show_year()
    placed = fill["placed"] if fill else data.built()
    corner = None
    if fill and fill.get("corner") and fill["corner"]["year"] <= year:
        c = fill["corner"]
        corner = dict(side=c["side"], sizeMm=round(c["size"] * 1000), year=c["year"],
                      filled=c["filled"] if c.get("filled") and c["filled"][1] <= year else None)
    going = nxt["y"][0] - st["y"][0]
    return dict(
        id=stone_id, worldSeed=world, part="step",
        lengthMm=x1 - x0, riseMm=st["z"][1] - st["z"][0], goingMm=going, lapMm=(y1 - y0) - going,
        ends=dict(l=end(x0), r=end(x1)), back="lapped",
        wear=dict(leftMm=x0, widthMm=round(F["width"] * 1000), lean=plan["lean"], footfall=data.footfall(year),
                  years=year - placed, rateMmPerCentury=data.wear_rate_mm()),
        corner=corner, years=year - (fill["bare"] if fill else placed),
    ), dict(step=st, stone=stone, placed=placed, fill=fill)


def flight_stones(data):
    """Every stone of every flight's ordinary steps, as R1 laid them: [(flight, step, index, stone)], by flight,
    index and stone id."""
    lay = data.laying()
    out = []
    for fid in data.plan["flightIds"]:
        fl = next(f for f in lay["steps"] if f["id"] == fid)
        for idx, sid in ordinary_steps(data, fid):
            for stone in sorted((s for s in fl["stones"] if s["step"] == sid), key=lambda s: s["id"]):
                out.append((fid, sid, idx, stone))
    return out


def specimen_step(data):
    """The step judged alone, chosen by a rule from the stair's facts (SN3): on the first flight, of its ordinary steps
    (not the first, whose block runs under the lane; not a rest; not the last, which nothing laps), the one whose rise
    lies nearest the set-out rise, the lowest index on a tie. Its stones are R1's laying's (masonry.lay at its commit:
    two across, both ends 150 mm into the walls, the joint outside the middle third and clear of the joints below,
    lapped on the step below); the specimen is the stone that carries the walking line (the flight's centre), so all
    its wear is on it. Its history (placed, reset, a broken corner) is the stair's life stage's."""
    plan = data.plan
    fid = plan["flightIds"][0]
    F = plan["flights"][fid]
    r_set = round(F["setout"]["r"] * 1000)

    def rise(sid):
        s = plan["steps"][sid]
        return round((s["zTop"] - s["zFoot"]) * 1000)

    ordinary = ordinary_steps(data, fid)
    best_idx, sid = min(ordinary, key=lambda t: (abs(rise(t[1]) - r_set), t[0]))
    lay = data.laying()
    fl = next(f for f in lay["steps"] if f["id"] == fid)
    stone = next(s for s in fl["stones"] if s["step"] == sid and min(p[0] for p in s["outline"]) <= 0 <=
                 max(p[0] for p in s["outline"]))
    facts, laid = step_facts(data, fid, sid, stone)
    life = data.life["steps"][sid]
    fill = laid["fill"]
    rule = dict(
        flight=fid, step=sid, index=best_idx, riseMm=rise(sid), setoutRiseMm=r_set,
        candidates={k: rise(k) for _i, k in ordinary},
        laid=dict(source=data.src["laying"]["source"], step=laid["step"], stone=stone),
        stone=stone["id"], history=dict(placed=laid["placed"], reset=life.get("reset"), mortar=life.get("mortar"),
                                        lifted=fill.get("lifted") if fill else None, corner=facts["corner"]),
    )
    data.note("specimen", stone["id"], "stones.py specimen_step: the rule in its docstring")
    return facts, rule


# -- the wear ---------------------------------------------------------------------------------------------------------

class Wear:
    """The tread's wear in the stone's frame (wear.py's laws, as stair_stages.put applies them): the depth at (x, y),
    m, and the polish. Feet land on the front of a tread (the along profile, stair_stages.put's), the nosing rounds
    several times faster than the hollow (wear.nosing), falling linearly to nothing nosingReach back, so one grid row
    there holds it exactly."""

    def __init__(self, facts, reach):
        w = facts["wear"]
        self.W = w["widthMm"] / 1000.0
        self.lean = w["lean"]
        self.x0 = w["leftMm"] / 1000.0
        self.g = facts["goingMm"] / 1000.0
        self.footfall, self.years, self.rate = w["footfall"], w["years"], w["rateMmPerCentury"]
        self.reach = reach

    def walk(self, x):
        across = np.clip((self.x0 + np.asarray(x, float) + self.W / 2) / self.W, 0.0, 1.0)
        return WR.walking(across, self.W, self.lean)

    def along(self, y):
        """Where on the tread the foot lands (stair_stages.put): most a third of the going back from the nosing."""
        y = np.clip(np.asarray(y, float), 0.0, 1.5 * self.g)
        if self.g >= 0.5:
            return np.ones_like(y)
        return 0.45 + 0.55 * np.exp(-((y / self.g - 0.3) / 0.35) ** 2)

    def foot(self, x, y):
        return self.walk(x) * self.along(y)

    def worn(self, x, y):
        return WR.depth(self.rate, self.footfall, self.years, self.foot(x, y), self.W)

    def nose(self, x):
        return WR.nosing(self.worn(x, 0.0), self.walk(x))

    def depth(self, x, y):
        y = np.asarray(y, float)
        return self.worn(x, y) + self.nose(x) * np.clip(1.0 - np.maximum(y, 0.0) / self.reach, 0.0, 1.0)

    def polish(self, x, y):
        return WR.polish(self.footfall, self.years, self.foot(x, y))


def wear_rows(wear, y_end, tol, least=0.0, fixed=()):
    """The grid's rows, whole millimetres, from the front (0) to the drawn top's end (y_end): each as far back as the
    wear's profile at the walking line stays within tol of the straight line between rows, and at least `least` past
    the one before (a row narrower than that is under SN8's 2 px in its level's far view); `fixed` rows are kept."""
    xs = np.linspace(-wear.x0 - wear.W / 2, -wear.x0 + wear.W / 2, 641)
    xp = xs[np.argmax(wear.depth(xs, 0.3 * wear.g))]
    end = int(round(y_end * 1000))
    lmm = int(math.ceil(least * 1000 - 1e-9))
    stops = sorted({int(round(f * 1000)) for f in fixed if 0 < f < y_end} | {end})
    rows, cur = [0], 0
    for stop in stops:
        while cur < stop:
            first = min(cur + max(lmm, 1), stop)
            best = first
            for e in range(stop, first - 1, -1):
                ys = np.arange(cur, e + 1) / 1000.0
                d = wear.depth(xp, ys)
                lin = d[0] + (d[-1] - d[0]) * (ys - ys[0]) / max(ys[-1] - ys[0], 1e-9)
                if np.abs(d - lin).max() <= tol:
                    best = e
                    break
            if stop - best < lmm and best != stop:      # never leave a row narrower than least before the stop
                best = stop if stop - cur <= 2 * lmm else stop - lmm
            rows.append(best)
            cur = best
    return [r / 1000.0 for r in rows]


def _lattice(Wmm, n):
    """The flight's lattice: its width (mm) cut into n even parts, each column in whole mm from the centre line, halves
    up (integers only)."""
    return lambda k: (2 * k * Wmm - n * Wmm + n) // (2 * n)


def field_error(wear, X, rows, flat, step=0.002, worst=False):
    """The largest difference (m) between wear.py's depth and the field a lattice X (flight frame, m) and rows make,
    over the flight's width and the rows' depth, sampled step apart (wear_checks' spacing), each cell split as
    grid_triangles fits it, or (worst) along whichever diagonal fits it worse there."""
    xs = np.asarray(X, float) - wear.x0
    ys = np.asarray(rows, float)
    nd = np.array([[node_depth(wear, rows, flat, x, y) for x in xs] for y in ys])
    px = np.arange(xs[0], xs[-1] + 1e-9, step)
    py = np.arange(ys[0], ys[-1] + 1e-9, step)
    PX, PY = np.meshgrid(px, py)
    i = np.clip(np.searchsorted(xs, PX, side="right") - 1, 0, len(xs) - 2)
    j = np.clip(np.searchsorted(ys, PY, side="right") - 1, 0, len(ys) - 2)
    u = (PX - xs[i]) / (xs[i + 1] - xs[i])
    v = (PY - ys[j]) / (ys[j + 1] - ys[j])
    d00, d10, d01, d11 = nd[j, i], nd[j, i + 1], nd[j + 1, i], nd[j + 1, i + 1]
    cx, cy = 0.5 * (xs[:-1] + xs[1:]), 0.5 * (ys[:-1] + ys[1:])
    want = np.array([[node_depth(wear, rows, flat, x, y) for x in cx] for y in cy])
    main = np.abs(0.5 * (nd[:-1, :-1] + nd[1:, 1:]) - want) <= np.abs(0.5 * (nd[1:, :-1] + nd[:-1, 1:]) - want) + 1e-15
    m = main[j, i]
    f_main = np.where(v <= u, d00 + u * (d10 - d00) + v * (d11 - d10), d00 + u * (d11 - d01) + v * (d01 - d00))
    f_anti = np.where(u + v <= 1, d00 + u * (d10 - d00) + v * (d01 - d00),
                      d11 + (1 - u) * (d01 - d11) + (1 - v) * (d10 - d11))
    true = wear.depth(PX, PY)
    if worst:
        return float(max(np.max(np.abs(f_main - true)), np.max(np.abs(f_anti - true))))
    return float(np.max(np.abs(np.where(m, f_main, f_anti) - true)))


def lattice_parts(wear, rows, spacing, tol, flat, least):
    """How many even parts the flight's width is cut into for its wear grid: the fewest at most spacing (mm) wide whose
    field (with L0's rows) stays within tol (m, L0's error) of wear.py's across the whole flight whichever diagonal
    splits each cell, so every stone of the flight takes the same lattice and each cell's diagonal is free to follow
    the stone's own edges (grid_triangles' choose). (The nosing's twist, its depth falling back while it changes
    across, costs a quarter of its change over a part at a cell's middle, which spacing alone does not bound.) A
    stone's end cell is up to least (m) wider than a part, where wear_columns moves a column onto the end, and the
    twist grows with the width, so the error is held to tol less that share."""
    Wmm = int(round(wear.W * 1000))
    n = -(-Wmm // int(spacing))
    while True:
        X = _lattice(Wmm, n)
        err = field_error(wear, [X(k) / 1000.0 for k in range(n + 1)], rows, flat, worst=True)
        part = wear.W / n
        if err * (part + least) / part <= tol or n >= 4 * Wmm // int(spacing):
            return n, err
        n += 1


def wear_columns(wear, L, y_end, n, flat, least, every=1, inset=(0.0, 0.0)):
    """The grid's columns: the flight's, not the stone's, since the wear is the flight's (its walking line runs across
    both stones of a step) and each stone is cut from it, so the two sides of a joint carry one field. The flight's
    lattice is its width cut into n even parts (lattice_parts), in whole mm from its centre line (integers); a level
    takes every `every`-th of them. The stone takes the lattice's columns over the run where the
    wear is deeper than flat (m), from the last at or before its left end to the first at or past its right, so its
    ends are not grid lines (a field edge along an arris would only fold its chamfer); a column inside the stone
    within least (m) of an end, or of an end's chamfer (inset, m: the chamfer's leg at a chamfered end, left and
    right, since edge_nodes takes the end's column onto its chamfer), goes onto the end, as no cell is cut narrower.
    Returns [(k, x)] in the stone's frame (m), or [] when nothing is worn."""
    Wmm = int(round(wear.W * 1000))
    x0 = int(round(wear.x0 * 1000))
    Lmm = int(round(L * 1000))
    X = _lattice(Wmm, n)                         # the lattice in the flight's frame, mm

    k_lo = 0
    while X(k_lo) > x0:
        k_lo -= 1
    while X(k_lo + 1) <= x0:
        k_lo += 1
    k_hi = k_lo
    while X(k_hi) < x0 + Lmm:
        k_hi += 1
    ys = np.linspace(0.0, y_end, 41)
    on = []
    for k in range(k_lo, k_hi):                 # a cell is worn where the law tops flat anywhere in it (5 mm apart)
        xs = np.arange(X(k), X(k + 1) + 1, 5) / 1000.0 - wear.x0
        on.append(bool(np.max(wear.depth(xs[:, None], ys[None, :])) > flat))
    if not any(on):
        return []
    a = k_lo + on.index(True)
    b = k_lo + len(on) - on[::-1].index(True)
    if every > 1:                               # the coarser level's lattice, still covering the run
        a -= (a % every)
        b += (-b) % every
    lm = [int(math.ceil((least + e) * 1000 - 1e-9)) for e in inset]
    out = []
    for k in range(a, b + 1, every):
        x = X(k) - x0
        if 0 < x < lm[0]:
            x = 0
        elif Lmm - lm[1] < x < Lmm:
            x = Lmm
        if not out or x != round(out[-1][1] * 1000):
            out.append((k, x / 1000.0))
    return out


def field(wear, cols, rows, L, D, flat, margin=0.1):
    """The wear's grid over the stone: the columns (padded with a flat one a margin past each end where the run stops
    inside the stone), the rows (held constant a margin in front of the stone and behind the drawn top's end), and the
    nodes' depths (m): (xs, ys, depth[j, i])."""
    xs = list(cols)
    if xs[0] > -1e-9:
        xs = [-margin] + xs
    if xs[-1] < L + 1e-9:
        xs = xs + [L + margin]
    ys = [rows[0] - margin] + list(rows) + [D + margin]
    depth = np.zeros((len(ys), len(xs)))
    for j, y in enumerate(ys):
        for i, x in enumerate(xs):
            depth[j, i] = node_depth(wear, rows, flat, x, y) if cols[0] - 1e-9 <= x <= cols[-1] + 1e-9 else 0.0
    return xs, ys, depth


def edge_nodes(o, xs, ys, depth, cols, rows, flat, least, rounds=12):
    """L0's field nodes on its chamfers' planes: the front row's on the nosing's (the riser's chamfer with the top),
    and a column moved onto an end (wear_columns) on that end's where the end is chamfered; the node at their corner
    on both. A node on a chamfer's plane makes the field's line between two of them lie in it, so the worn top meets
    the chamfer along the field's own lines: a row, a column and a cell's diagonal leave the chamfer's edge at one
    point, not just apart (each such pair a sliver of top and a fan of thin chamfer on screen). Where the wear has
    eaten the chamfer through, the node stays on the arris, so the field meets the riser along its own row; between
    such a node and one on the chamfer, a node goes where the chamfer runs out (the law's depth there reaching the
    chamfer's foot on the riser), so the row runs along the riser to it and up the chamfer's plane from it, and no
    sliver of field is left between them. Each node moves only along its own row or column (the corner along both),
    inward only, onto the plane at the law's depth there (a fixed point, a few rounds of Newton's steps). The margin
    rows in front and behind take their neighbours' depths, so the field is level in y outside the stone and stands
    above the chamfer there. Changes depth in place; returns ((X, Y), between, moved [(j, i, dx mm, dy mm)])."""
    X, Y = np.meshgrid(np.asarray(xs, float), np.asarray(ys, float))
    ch = {p["name"]: p for p, _s, _a in o["chamfers"]}
    H, L, wear = o["H"], o["L"], o["wear"]
    moved = []

    def solve(j, i, planes, axes):
        """Move node (j, i) inward along axes (0 x, 1 y) onto planes, the law's depth held at each step; a node the
        planes would take outward (the chamfer worn through there) stays. Whether a node is flat stone is decided where
        the grid puts it, and it keeps that as it moves: a flat node stays at the top's plane, a worn one follows the
        law itself, so its depth is never cut at flat on the way (a node whose depth crossed flat between two steps
        would jump by flat and never meet the plane). Either is within flat of node_depth's. Returns whether it
        moved."""
        q = np.array([X[j, i], Y[j, i], 0.0])
        q0 = q.copy()
        worn = node_depth(wear, rows, flat, q[0], q[1]) > 0.0

        def law(x, y):
            return float(wear.depth(x, min(max(y, rows[0]), rows[-1]))) if worn else 0.0

        for _ in range(rounds):
            q[2] = H - law(q[0], q[1])
            g = np.array([float(p["n"] @ q - p["d"]) for p in planes])
            if np.abs(g).max() < 1e-12:
                break
            J = np.array([[p["n"][a] for a in axes] for p in planes])
            step = np.linalg.solve(J, -g)
            for a, dv in zip(axes, step):
                q[a] += dv
        q[2] = H - law(q[0], q[1])
        if max(abs(float(p["n"] @ q - p["d"])) for p in planes) > 1e-9:
            raise Failed(f"a field node does not reach its chamfer ({[p['name'] for p in planes]})")
        inward = [(q[a] - q0[a]) * (1.0 if q0[a] < 0.5 * (L if a == 0 else o["D"]) else -1.0) for a in axes]
        if min(inward) <= 1e-12:
            return False
        X[j, i], Y[j, i] = q[0], q[1]
        depth[j, i] = H - q[2]
        moved.append((j, i, round((q[0] - q0[0]) * 1000, 3), round((q[1] - q0[1]) * 1000, 3)))
        return True

    jf = list(ys).index(rows[0])                        # the front row (ys starts a margin in front of it)
    jb = list(ys).index(rows[-1])
    run = [i for i in range(len(xs)) if cols[0] - 1e-9 <= xs[i] <= cols[-1] + 1e-9]
    nose = ch.get("ch:riser|top")
    end_cols = {}
    for side, xe in (("l", 0.0), ("r", L)):
        i = next((k for k in run if abs(xs[k] - xe) < 1e-9), None)
        if i is not None and o["ends"][side] != "walled" and f"ch:end-{side}|top" in ch:
            end_cols[i] = ch[f"ch:end-{side}|top"]
    on = {}
    for i in run:
        if nose is None:
            break
        if i in end_cols:
            on[i] = solve(jf, i, [nose, end_cols[i]], (0, 1)) or solve(jf, i, [nose], (1,))
        else:
            on[i] = solve(jf, i, [nose], (1,))
    for i, p in sorted(end_cols.items()):
        for j in range(jf + (1 if nose is not None else 0), jb + 1):
            solve(j, i, [p], (0,))
    # where the nosing's chamfer runs out between two of the front row's nodes: on the riser, at the chamfer's foot
    between = {}
    if nose is not None:
        def foot(x):                                    # the law's top less the chamfer's foot on the riser at x
            z = H - node_depth(wear, rows, flat, x, rows[0])
            zc = (nose["d"] - nose["n"][0] * x - nose["n"][1] * rows[0]) / nose["n"][2]
            return z - zc
        for a, b in zip(run, run[1:]):
            if on.get(a) == on.get(b):
                continue
            lo, hi = xs[a], xs[b]
            flo = foot(lo)
            for _ in range(60):
                mid = 0.5 * (lo + hi)
                if (foot(mid) > 0) == (flo > 0):
                    lo, flo = mid, foot(mid)
                else:
                    hi = mid
            x = 0.5 * (lo + hi)
            zc = (nose["d"] - nose["n"][1] * rows[0]) / nose["n"][2]
            # a run-out is no nearer than two pixels at 8 m to another corner on the nosing's foot (each such pair a
            # sliver of chamfer, and of top, a fraction of a mm wide): within that of one of its two nodes, the node
            # goes to it along its row (an end's corner node, on two chamfers, stays); within that of where a chip's
            # plane crosses the foot, it goes there, so the chamfer runs out where the chip begins
            stops = [(abs(X[jf, i] - x), "node", i) for i in (a, b) if i not in end_cols]
            for c in o["chips"]:
                if abs(c["n"][0]) > 1e-9:
                    xc = (c["d"] - c["n"][1] * rows[0] - c["n"][2] * zc) / c["n"][0]
                    if xs[a] < xc < xs[b]:
                        stops.append((abs(xc - x), "chip", xc))
            near = min(stops, key=lambda t: t[0], default=None)
            if near is not None and near[0] < least:
                if near[1] == "node":
                    i = near[2]
                    moved.append((jf, i, round((x - X[jf, i]) * 1000, 3), round((rows[0] - Y[jf, i]) * 1000, 3)))
                    X[jf, i], Y[jf, i], depth[jf, i] = x, rows[0], H - zc
                    continue
                x = near[2]
            between[(jf, a)] = (x, rows[0], H - zc)
    for i in range(len(xs)):                            # the margins level with their neighbours
        depth[0, i] = depth[jf, i]
        depth[-1, i] = depth[jb, i]
    return (X, Y), between, moved


def node_depth(wear, rows, flat, x, y):
    """The field's depth at a point: wear.py's at (x, y), the rows' ends holding it in y; none where that is no
    deeper than flat (m, the flat share of L0's error), so unworn stone is exactly flat and merges into few faces."""
    d = float(wear.depth(x, min(max(y, rows[0]), rows[-1])))
    return d if d > flat else 0.0


# -- the step -------------------------------------------------------------------------------------------------------

def laminae(rng, H, least, most):
    """The stone's laminae where a split face can break back (SN4: facets stepped where laminae broke): up to `most`
    level planes, whole mm, from the top down, each at least `least` (m) from the next, the top and the bed. Every
    faceted face of the stone breaks only at these, and two faces that meet at an arris never at the same one (folds'
    `taken`): their ridges are a lamina apart at least, so the arris's corners are three-faced and the chamfer between
    them is never cut into slivers (one plane on both would make a four-faced corner, which the chamfer cuts into a
    piece a fraction of a mm high)."""
    lmm, hmm = int(round(least * 1000)), int(round(H * 1000))
    k = min(most, hmm // lmm - 1)
    out, hi = [], hmm - lmm
    for i in range(k):
        z = rng.randint((k - i) * lmm, hi)
        out.append(z)
        hi = z - lmm
    return out


def folds(name, m, p0, count, rng, planes_mm, steps, taken=()):
    """A vertical face's facets (SN4: at most three), as convex folds about level ridges so the block stays convex:
    below each ridge the face leans back, each facet's foot set back a seeded whole mm in steps past the line of the
    facet above. Its count - 1 ridges are chosen by seed from the stone's laminae (planes_mm, whole mm from the top
    down) not `taken` by a face it meets at an arris, so every facet is a lamina high at least; where too few are
    left, the face has as many facets as they allow. m the face's outward normal, p0 a point on it. Returns (planes,
    the face's set-back at its foot)."""
    m = np.asarray(m, float)
    pool = [z for z in planes_mm if z not in set(taken)]
    count = min(count, len(pool) + 1)
    if count < 2:
        return [], 0.0
    chosen = []
    for _ in range(count - 1):
        chosen.append(pool.pop(rng.randint(0, len(pool) - 1)))
    ridges = [z / 1000.0 for z in sorted(chosen, reverse=True)]
    out, y, K = [], 0.0, 0.0
    for i, z in enumerate(ridges):
        z_next = ridges[i + 1] if i + 1 < len(ridges) else 0.0
        s = rng.randint(*steps) / 1000.0
        K2 = K + s / (z - z_next)
        pp = np.asarray(p0, float) - y * m
        n = m - K2 * np.array([0.0, 0.0, 1.0])
        d = float(m @ pp) - K2 * z
        nn = float(np.linalg.norm(n))
        out.append(B.plane(f"{name}/facet-{i + 2}", n / nn, d=d / nn, face=name, kind=2, ridge=z,
                           setbackMm=round(s * 1000), slope=K2))
        y += K2 * (z - z_next)
        K = K2
    return out, y


def outline(facts, defn=None, data=None):
    """Everything both levels share, from the facts and the seed: the block's planes and facets, the chips, the
    chamfers' planes and leg, the faces' kinds, patches and frames, the wear and its grid, the seen regions."""
    data = data or Data()
    part = facts["part"]
    world, sid = facts["worldSeed"], facts["id"]
    P = lambda key: param(part, defn, key, data)  # noqa: E731
    L, H, g = _f(facts["lengthMm"]), _f(facts["riseMm"]), _f(facts["goingMm"])
    D = g + _f(facts["lapMm"])
    s = _f(P("skirtMm"))
    planes = [B.plane("top", (0, 0, 1), d=H, kind=0),
              B.plane("bed", (0, 0, -1), d=0.0, role="hidden", skirt=s),
              B.plane("riser", (0, -1, 0), d=0.0, kind=2),
              B.plane("back", (0, 1, 0), d=D, role="hidden")]
    ends = {}
    for side, sign, xe in (("l", -1.0, 0.0), ("r", 1.0, L)):
        ends[side] = facts["ends"][side]["kind"]
        role = "hidden" if ends[side] == "walled" else "exposed"
        planes.append(B.plane(f"end-{side}", (sign, 0, 0), d=sign * xe, role=role, kind=2))
    covers = [B.plane("cover:next", (0, 1, 0), d=g, role="cover", skirt=s)] if facts["back"] == "lapped" else []
    # the split faces' facets: a riser one plane mostly, sometimes broken back below a lamina; an open end the same
    least = _f(P("facetLeastMm"))
    fsteps = P("facetStepMm")
    most = max(int(a) for a, _w in P("riserFacets") + P("endFacets")) - 1
    planes_mm = laminae(HS.Stream(world, sid, "laminae"), H, least, most)
    rng = HS.Stream(world, sid, "riser")
    nf = rng.weighted([(int(a), int(w)) for a, w in P("riserFacets")])
    facets, riser_foot = folds("riser", (0, -1, 0), (0, 0, 0), nf, rng, planes_mm, fsteps)
    end_facets = {}
    for side, sign, xe in (("l", -1.0, 0.0), ("r", 1.0, L)):
        if ends[side] == "open":
            r2 = HS.Stream(world, sid, f"end-{side}")
            ne = r2.weighted([(int(a), int(w)) for a, w in P("endFacets")])
            fs, _foot = folds(f"end-{side}", (sign, 0, 0), (xe, 0, 0), ne, r2, planes_mm, fsteps,
                              taken=[round(p["ridge"] * 1000) for p in facets if p["face"] == "riser"])
            facets += fs
            end_facets[side] = 1 + len(fs)
    block = planes + facets
    # chips (SN4): where a fact puts one (a corner broken off the nosing), and an open end's top front corner by seed
    chips = []
    centre = np.array([L / 2, D / 2, H / 2])
    cn = facts.get("corner")
    if cn:
        cb = data.corner_break()
        size = _f(cn["sizeMm"])
        b, a = size * cb["alongPerMille"] / 1000.0, size * cb["backPerMille"] / 1000.0
        dz = min(H, _f(cb["depthMm"]) + size * cb["depthPerMille"] / 1000.0)
        if cb["toBed"] and planes_mm:   # a stone that parts along its beds breaks down to one: its nearest lamina
            dz = min((H - _f(z) for z in planes_mm), key=lambda d: (abs(d - dz), d))
        b, a, grown = chip_least(b, a, dz)
        chips.append(corner_chip(f"chip:{cn['side']}", cn["side"], L, H, (b, a, dz), centre,
                                 fact=f"broken {cn['year']}", filled=cn.get("filled"), sizeMm=int(cn["sizeMm"]),
                                 grownPerMille=grown))
    for side in ("l", "r"):
        if ends[side] == "open" and not (cn and cn["side"] == side):
            r3 = HS.Stream(world, sid, f"chip-{side}")
            if r3.randint(0, 999) < P("chipPerMille"):
                legs = tuple(_f(r3.randint(*P("chipLegMm"))) for _ in range(3))
                chips.append(corner_chip(f"chip:{side}", side, L, H, legs, centre, fact="knocked (seed)"))
    # the chamfers (SN4) on every exposed arris of the block and its open chips, a leg seeded per stone. A chip the
    # record says was filled (the 1986 dab) is cut after them: under its fill its edges are joints, not arrises (SN4: a
    # line is an arris, a joint or the boundary of a mark)
    clo, chi = P("chamferMm")
    c_mm = HS.Stream(world, sid, "chamfer").randint(clo, chi)
    measure = P("chamferMeasure")
    if measure != "leg":
        raise ValueError(f"chamferMeasure {measure!r}: only 'leg' is built (blender.md)")
    open_chips = [c for c in chips if not c.get("filled")]
    ch = B.chamfers(block + open_chips, _f(c_mm), P("arrisMaxDeg"))
    # the wear (wear.py) and its grid: L0's rows within L0's error, L1's within its share of L1's, each no narrower
    # than SN8's 2 px in its far view (face-on, 20 degrees of top)
    tol0 = _f(data.level_error(part, "l0"))
    tol1 = _f(data.level_error(part, "l1")) * P("l1WearShare") / 1000.0
    wear = Wear(facts, _f(P("nosingReachMm")))
    y_end = g + s if covers else D
    rows0 = wear_rows(wear, y_end, tol0, least=least_row(GATE["l0Distance"]), fixed=(wear.reach,))
    rows1 = wear_rows(wear, y_end, tol1, least=least_row(GATE["l1Distance"]))
    flat = tol0 * P("wearFlatShare") / 1000.0
    flat1 = tol1 * P("wearFlatShare") / 1000.0      # L1's flat stone: the same share of its own error
    parts, lattice_err = lattice_parts(wear, rows0, P("wearGridMm"), tol0, flat, two_px(0))
    inset = tuple(_f(c_mm) if ends[side] != "walled" else 0.0 for side in ("l", "r"))
    cols0 = wear_columns(wear, L, y_end, parts, flat, two_px(0), inset=inset)
    cols1 = wear_columns(wear, L, y_end, parts, flat1, two_px(1), every=2)
    # a joint end is seen above its fill and in front of it (SN5: a fill no deeper than the joint is wide): the band
    # is the widest joint, the wear on the end's top and SN9's contact tolerance deep, and never less than the
    # chamfer and two pixels at 8 m past it, so what is drawn of the end past its chamfer is no sliver (more of it
    # drawn behind the fill costs nothing seen)
    regions = {}
    jmax = data.tread_joint()[1]
    risers = [next(p for p in planes if p["name"] == "riser")] + [p for p in facets if p["face"] == "riser"]
    for side, xe in (("l", 0.0), ("r", L)):
        if ends[side] == "joint":
            ys = np.linspace(0.0, y_end, 64)
            wmax = float(np.max(wear.depth(np.full_like(ys, xe), ys)))
            c_band = _f(max(math.ceil(jmax + wmax * 1000 + SN9["contactMm"]),
                            c_mm + math.ceil(two_px(0) * 1000)))
            regions[f"end-{side}"] = joint_regions(risers, H, c_band,
                                                   [c for c in chips if c["name"] == f"chip:{side}"])
    # a chamfer on an arris of a joint end is seen where the end is (a chip's arris with the end runs on into the joint
    # behind its fill; the riser's and the top's lie inside the band, which is the chamfer and two pixels at least)
    for p, _sag, _ang in ch:
        held = [f for f in p["chamfer"] if f in regions]
        if held:
            regions[p["face"]] = regions[held[0]]
    o = dict(facts=facts, L=L, H=H, g=g, D=D, skirt=s, block=block, covers=covers, chamfers=ch, chamferMm=c_mm,
             chips=chips, wear=wear, rows0=rows0, rows1=rows1, cols0=cols0, cols1=cols1, flat=flat, flat1=flat1,
             regions=regions, laminaeMm=planes_mm,
             lattice=dict(parts=parts, widthMm=round(wear.W * 1000), errorMm=round(lattice_err * 1000, 3)),
             ends=ends,
             riserFacets=1 + sum(1 for p in facets if p["face"] == "riser"), riserFootMm=round(riser_foot * 1000, 2),
             endFacets=end_facets, y_end=y_end, tol0=tol0, tol1=tol1, jointMaxMm=jmax)
    o["faces"] = face_frames(o, defn, data)
    _unfold(o)
    return o


def joint_regions(risers, H, band, chips=()):
    """Where a joint end is seen (SN5: its fill no deeper than the joint is wide, pressed in from the joint's lips):
    within band of the top, within band behind the riser, facet by facet (each facet's slab between its ridges, so the
    regions are disjoint and follow the riser where a lamina broke back), and within band behind a chip that breaks
    the end's corner (its edge with the end is a lip of the joint too: the fill stands below it). The band behind a
    facet is measured level, back from it as a fill is pressed in, so the region's edge folds at each ridge as the
    riser does and meets itself there (along the facet's normal it would step by band (1 / cos(lean) - 1) at each
    ridge, a sliver that thin); behind a chip, along the chip's normal, outside the facets' bands, slab by slab, so
    every piece is convex and none overlaps another. Each region a list of half-spaces n . p <= d."""
    up = np.array([0.0, 0.0, 1.0])
    out = [[dict(n=-up, d=-(H - band))]]
    ridges = [H - band] + [min(p["ridge"], H - band) for p in risers[1:]] + [-1.0]
    for i, p in enumerate(risers):
        top, bottom = ridges[i], ridges[i + 1]
        if top <= bottom:
            continue
        slab = [dict(n=up, d=top)] + ([dict(n=-up, d=-bottom)] if bottom > -1.0 else [])
        out.append([dict(n=-p["n"], d=-(p["d"] + band * p["n"][1]))] + slab)
        for c in chips:
            out.append([dict(n=-c["n"], d=-(c["d"] - band)), dict(n=p["n"], d=p["d"] + band * p["n"][1])] + slab)
    return out


def least_row(distance):
    """The narrowest row of the tread's grid that stays at 2 px at a level's far edge, seen face-on with 20 degrees of
    top (the judging set's view), through the rig's lens."""
    return GATE["thinPx"] * distance / focal_px() / math.sin(math.radians(20.0))


def chip_least(b, a, dz):
    """A broken corner drawn no narrower than a face may be (SN9: a face under 50 mm is a sliver): where the record's
    size gives a chip face under it (the gully's least, 40 mm, bites 52 along and 30 back), its bite along and back
    grows together by the least whole per mille that clears it; its depth stays the bedding plane it broke to. Returns
    the legs (m) and the growth (per mille over the record's size, 0 where none was needed): the fact drawn a little
    larger, never smaller or missing, and the sidecar says by how much."""
    def width(k):
        tri = np.array([[b * k, 0.0, 0.0], [0.0, a * k, 0.0], [0.0, 0.0, -dz]])
        n = B.unit(np.cross(tri[1] - tri[0], tri[2] - tri[0]))
        return min_width(tri, n)
    least = SN9["sliverMm"] / 1000.0
    if width(1.0) >= least:
        return b, a, 0
    lo, hi = 1000, 2000
    while width(hi / 1000.0) < least:
        hi *= 2
    while hi - lo > 1:
        mid = (lo + hi) // 2
        lo, hi = (mid, hi) if width(mid / 1000.0) < least else (lo, mid)
    return b * hi / 1000.0, a * hi / 1000.0, hi - 1000


def corner_chip(name, side, L, H, legs, centre, back=None, **info):
    """A chip off a top front corner (SN4: a planar cut at a corner of the mass): the plane through the points legs
    (m) along the top's front edge, back along the end's top and down the front's end. With back (m), the top back
    corner instead, the back face at y = back: legs along its top edge, forward along the end's top, down its end."""
    b, a, dz = legs
    xe, sx = (0.0, 1.0) if side == "l" else (L, -1.0)
    y0, sy = (0.0, 1.0) if back is None else (back, -1.0)
    pts = [np.array([xe + sx * b, y0, H]), np.array([xe, y0 + sy * a, H]), np.array([xe, y0, H - dz])]
    return through(name, pts, centre, kind=2, legsMm=[round(v * 1000) for v in legs], **info)


def through(name, pts, centre, **info):
    """The plane through three points, its outside away from the block's centre."""
    a, b, c = pts
    n = B.unit(np.cross(b - a, c - a))
    if (centre - a) @ n > 0:
        n = -n
    return B.plane(name, n, point=a, role="exposed", face=name, **info)


def face_frames(o, defn, data):
    """Each drawn face's kind, patch slice and UV0 frame (the contract's UV0): a split face u along the cleavage
    (level: the stone lies on its bed), v up its plane, a facet unfolded about its ridge, then only a half turn or a
    mirror in u; the top (a bed face) in plan, any turn; a chamfer u along its arris, no patch. Offsets in whole mm."""
    facts = o["facts"]
    part, world, sid = facts["part"], facts["worldSeed"], facts["id"]
    sets = param(part, defn, "patches", data)
    tile = data.patch_mm()
    out = {}
    z = np.array([0.0, 0.0, 1.0])

    def pick(face, names):
        r = HS.Stream(world, sid, face, "patch")
        name = names[r.randint(0, len(names) - 1)]
        return name, data.slice_of(name), r

    # a face's role: the step's top is its tread (kind 0); a level face a part names a bed (a wall stone's top and bed,
    # a coping's top and bed: the laminae's own planes) is kind 3, in plan, as the tread; every other face is split
    roles = o.get("faceRoles", {})
    for p in o["block"] + o["chips"]:
        if p["role"] != "exposed" or p["face"] in out:
            continue
        face = p["face"]
        role = roles.get(face, "tread" if face == "top" else "split")
        if role in ("tread", "bed"):
            name, sl, r = pick(face, sets["top" if role == "tread" else "bed"])
            turn = r.randint(0, 359)
            th = math.radians(turn)
            u = np.array([math.cos(th), math.sin(th), 0.0])
            v = np.array([-math.sin(th), math.cos(th), 0.0])
            out[face] = dict(kind=0 if role == "tread" else 3, patch=name, slice=sl, o=np.zeros(3), u=u, v=v, mode=0,
                             plan=True, offset=(r.randint(0, tile - 1), r.randint(0, tile - 1)), turnDeg=turn)
        else:
            name, sl, r = pick(face, sets["split"])
            base = next(q for q in o["block"] + o["chips"] if q["name"] == face)
            n = base["n"]
            u = B.unit(np.cross(z, n))
            out[face] = dict(kind=2, patch=name, slice=sl, o=np.zeros(3), u=u, v=np.cross(n, u), mode=r.randint(0, 2),
                             plan=False, offset=(r.randint(0, tile - 1), r.randint(0, tile - 1)))
    for p, _sag, _ang in o["chamfers"]:
        q0, q1 = p["arris"]
        u = B.unit(q1 - q0)
        out[p["face"]] = dict(kind=1, patch=None, slice=7, o=q0.copy(), u=u, v=np.cross(p["n"], u), mode=0,
                              plan=False, offset=(0, 0))
    return out


def two_px(level):
    """Two pixels in metres at the level's far edge (L0 8 m, L1 20 m), square on through the rig's lens."""
    return GATE["thinPx"] * (GATE["l0Distance"] if level == 0 else GATE["l1Distance"]) / focal_px()


def level_mesh(o, level):
    """One level's mesh: the block (with L0's chamfers, never L1's) and its chips, cut by its wear field, drawn where it
    is seen; then its channels."""
    planes = list(o["block"]) + list(o["chips"])
    if level == 0:
        planes += [p for p, _s, _a in o["chamfers"]]
    planes += o["covers"]
    cols = [x for _k, x in (o["cols0"] if level == 0 else o["cols1"])]
    rows = o["rows0"] if level == 0 else o["rows1"]
    fgrid, fld = None, None
    if cols:
        flat = o["flat"] if level == 0 else o["flat1"]
        xs, ys, depth = field(o["wear"], cols, rows, o["L"], o["D"], flat)
        wear = o["wear"]
        tol = o["tol0"] if level == 0 else o["tol1"]
        size = two_px(level)
        nodes, between, moved = None, None, []
        if level == 0:
            nodes, between, moved = edge_nodes(o, xs, ys, depth, cols, rows, flat, size)
        fld = B.grid_triangles(xs, ys, depth, o["H"],
                               centre_depth=lambda x, y: node_depth(wear, rows, flat, x, y)
                               if cols[0] <= x <= cols[-1] else 0.0,
                               fit=tol,
                               choose=lambda splits: int(np.argmin([B.piece_cost(planes, sp, size)
                                                                    for sp in splits])),
                               nodes=nodes, between=between)
        fgrid = dict(xs=xs, ys=ys, depth=depth, rows=rows, cols=cols, onChamfer=moved,
                     runsOut=sorted(round(v[0] * 1000, 1) for v in (between or {}).values()))
    lines = np.array([x for x in cols if 1e-9 < x < o["L"] - 1e-9])     # the ends are no structure lines
    # the grid's columns where they cross the field, so the worn top keeps its quads; a column's vertex only on
    # planar faces (a chamfer's foot on the riser, say) is no corner and goes
    keep = (lambda q, faces: bool(len(lines)) and float(np.abs(lines - q[0]).min()) < 1e-9)
    surf = B.cut(planes, field=fld, regions=o["regions"], keep=keep)
    # an edge under two pixels where the faces about it lie flat (a row and a diagonal meeting a chamfer's edge just
    # apart) made one point, within half SN9's planarity
    surf, moves = B.collapse(surf, two_px(level), COLLAPSE_MM / 1000.0, keep=keep, bounds=bounds(o))
    m = B.triangulate(B.thin_out(surf, two_px(level)), size=two_px(level))
    m["collapsed"] = [dict(lengthMm=round(ln * 1000, 3), bendMm=round(bd * 1000, 4)) for _u, _v, ln, bd in moves]
    m["grid"] = fgrid
    m["level"] = level
    m["planes"] = planes
    channels(o, m)
    return m


# -- the channels (the contract's vertex layout) ----------------------------------------------------------------------

def _uv0(fr, p, pl):
    q = p - fr["o"]
    u = q @ fr["u"]
    if fr["plan"]:
        v = q @ fr["v"]
    elif "ridge" in pl and "vfold" in fr:
        r0, v0 = fr["vfold"][pl["name"]]
        vk = np.cross(pl["n"], fr["u"])
        v = v0 + (p - r0) @ vk
    else:
        v = q @ fr["v"]
    mode = fr["mode"]
    if mode == 1:
        u, v = -u, -v
    elif mode == 2:
        u = -u
    return u + fr["offset"][0] / 1000.0, v + fr["offset"][1] / 1000.0


def _unfold(o):
    """A faceted face's v unfolded about each ridge: the facet below a ridge carries on from the face above it."""
    by_face = {}
    for p in o["block"]:
        if "ridge" in p:
            by_face.setdefault(p["face"], []).append(p)
    for face, fs in by_face.items():
        fr = o["faces"][face]
        fr["vfold"] = {}
        base = next(p for p in o["block"] if p["name"] == face)
        above = base
        v_above = None
        for p in sorted(fs, key=lambda p: -p["ridge"]):
            # a point on the ridge: where this facet meets the one above it, at x = 0 in the frame's u
            n1, d1, n2, d2 = above["n"], above["d"], p["n"], p["d"]
            # solve for the point with z = ridge on both planes, along u = 0
            zr = p["ridge"]
            A = np.array([n1, n2, fr["u"]])
            rhs = np.array([d1, d2, 0.0])
            r0 = np.linalg.solve(A, rhs)
            assert abs(r0[2] - zr) < 1e-6, f"{p['name']}: its ridge is not where it was cut"
            if above is base:
                v_at = (r0 - fr["o"]) @ fr["v"]
            else:
                ra, va = v_above
                v_at = va + (r0 - ra) @ np.cross(above["n"], fr["u"])
            fr["vfold"][p["name"]] = (r0, v_at)
            v_above = (r0, v_at)
            above = p


def channels(o, m):
    """The eight UV channels at every corner (the contract, plan.md's table): UV0 metres in the face with its patch's
    offset and turn; UV1 (years / 200, seed); UV2 (kind, water 0); UV3 (0.5 + 0.5 n_z, 1); UV4 (polish, 0); UV5 (0, 0);
    UV6 and UV7 the edge distances and the code."""
    facts = o["facts"]
    V, T = m["V"], m["T"]
    nt = len(T)
    UV = np.zeros((8, nt, 3, 2))
    seed = HS.unit(HS.h(facts["worldSeed"], facts["id"], "seed"))
    years = facts["years"]
    wear = o["wear"]
    polished = set() if wear is None else \
        {"top"} | {p["face"] for p, _s, _a in o["chamfers"] if set(p["chamfer"]) == {"top", "riser"}}
    for t in range(nt):
        pl = m["plane"][t]
        face = m["face"][t]
        fr = o["faces"][face]
        n = pl["n"]
        P3 = V[T[t]]
        for i in range(3):
            UV[0, t, i] = _uv0(fr, P3[i], pl)
            UV[1, t, i] = (years / 200.0, seed)
            UV[2, t, i] = (fr["kind"], 0.0)
            UV[3, t, i] = (0.5 + 0.5 * n[2], 1.0)
            if face in polished:
                UV[4, t, i] = (float(wear.polish(P3[i][0], P3[i][1])), 0.0)
    edge, code = edge_channels(o, m)
    UV[6] = edge[:, :, :2]
    UV[7, :, :, 0] = edge[:, :, 2]
    UV[7, :, :, 1] = code[:, None]
    m["UV"] = UV
    m["edge"] = edge
    m["code"] = code


def altitudes(P3):
    """Corner i's height over the opposite edge (the contract's solid-wireframe distances)."""
    out = np.zeros(3)
    for i in range(3):
        a, b, c = P3[i], P3[(i + 1) % 3], P3[(i + 2) % 3]
        e = c - b
        out[i] = np.linalg.norm(np.cross(a - b, e)) / np.linalg.norm(e)
    return out


def edge_channels(o, m):
    """UV6 and UV7. L0: corner i carries its height over the opposite edge in slot i, 0 in the others; the code is the
    face's slice + 64 x the stone's chamfer (mask 0). L1 (a compatible widening of the contract): a slot may hold the
    distance to any arris line L0 chamfers that comes within a leg of the triangle, in the triangle's plane (for the
    triangle's own edge the same numbers as L0's encoding, in the slot of the corner opposite it); its mask bit is set
    where L0's chamfer stands there; the code's chamfer is what L0's chamfer keeps of its leg where the wear has eaten
    into it (whole mm, the mean over the triangle's masked slots), else the stone's."""
    V, T = m["V"], m["T"]
    nt = len(T)
    c_mm = o["chamferMm"]
    edge = np.zeros((nt, 3, 3))
    code = np.zeros(nt)
    for t in range(nt):
        alt = altitudes(V[T[t]])
        for i in range(3):
            edge[t, i, i] = alt[i]
        code[t] = o["faces"][m["face"][t]]["slice"] + 64 * c_mm
    m["arrisLines"] = []
    if m["level"] == 0:
        return edge, code
    # L1's arrises: its mesh edges between two faces L0 chamfers between, each with what L0's chamfer keeps there
    chs = {tuple(sorted(p["chamfer"])): p for p, _s, _a in o["chamfers"]}
    owners = {}
    for t, tri in enumerate(T):
        for k in range(3):
            a, b = int(tri[k]), int(tri[(k + 1) % 3])
            owners.setdefault((min(a, b), max(a, b)), []).append(t)
    segs = []
    for (a, b), ts in sorted(owners.items()):
        if len(ts) != 2:
            continue
        fa, fb = m["face"][ts[0]], m["face"][ts[1]]
        pair = tuple(sorted((fa, fb)))
        if fa == fb or pair not in chs:
            continue
        keep = kept_leg(o, chs[pair], 0.5 * (V[a] + V[b]))
        segs.append(dict(a=a, b=b, faces=pair, keep=keep))
    m["arrisLines"] = segs
    leg = c_mm / 1000.0
    for t in range(nt):
        face = m["face"][t]
        tri = [int(i) for i in T[t]]
        P3 = V[tri]
        n = m["plane"][t]["n"]
        cand = []
        for sg in segs:
            if face not in sg["faces"]:
                continue
            A, Bp = V[sg["a"]], V[sg["b"]]
            own = sg["a"] in tri and sg["b"] in tri
            dist = min(float(B.point_tri_distance(np.array([A, Bp]), *P3).min()),
                       min(_seg_dist(p, A, Bp) for p in P3))
            if own or dist < leg - 1e-9:
                cand.append((0 if own else 1, dist, sg["a"], sg["b"], sg))
        cand.sort(key=lambda c: c[:4])
        slots, rest = [None, None, None], []
        for own, _d, _a, _b, sg in cand:
            A, Bp = V[sg["a"]], V[sg["b"]]
            A2 = A - ((A - P3[0]) @ n) * n
            B2 = Bp - ((Bp - P3[0]) @ n) * n
            mvec = np.cross(n, B.unit(B2 - A2))
            if (P3.mean(axis=0) - A2) @ mvec < 0:
                mvec = -mvec
            d = (P3 - A2) @ mvec
            item = (d, sg)
            same = [x for x in slots + rest if x is not None and np.abs(x[0] - d).max() < 1e-4]
            if same:                                   # a neighbouring piece of an arris already held: one line
                continue
            if own == 0:
                slots[3 - tri.index(sg["a"]) - tri.index(sg["b"])] = item
            else:
                rest.append(item)
        for item in rest:
            k = next((k for k in range(3) if slots[k] is None), None)
            if k is None:
                break
            slots[k] = item
        mask, keeps = 0, []
        for k in range(3):
            if slots[k] is None:
                continue
            d, sg = slots[k]
            edge[t, :, k] = np.maximum(d, 0.0)
            kf = sg["keep"][face]
            if int(round(kf)) >= 1:
                mask |= 1 << k
                keeps.append(kf)
        ch = int(round(sum(keeps) / len(keeps))) if keeps else c_mm
        code[t] = o["faces"][face]["slice"] + 8 * mask + 64 * ch
    return edge, code


def kept_leg(o, chp, q):
    """What L0's chamfer keeps of its leg (mm) at a point q on the arris L1 draws, on each of its two faces: where the
    top is worn, L1's arris lies the depth there below L0's, so on the other face the leg is the leg less that depth,
    and on the top the chamfer's edge falls back to where the worn surface meets the chamfer's plane (the leg less the
    depth there, found by a few fixed-point steps, the wear changing slowly across a leg); elsewhere the whole leg."""
    c = chp["leg"]
    fa, fb = chp["chamfer"]
    if "top" not in chp["chamfer"] or not o["cols0"]:
        return {fa: c * 1000.0, fb: c * 1000.0}
    ua, ub = chp["inward"]
    u_top = ua if chp["between"][0] == "top" else ub
    wear, rows, flat = o["wear"], o["rows0"], o["flat"]
    other = fb if fa == "top" else fa
    d0 = node_depth(wear, rows, flat, q[0], q[1])
    t = c
    for _ in range(12):
        p = q + t * u_top
        t = c - node_depth(wear, rows, flat, p[0], p[1])
        if t <= 0:
            t = 0.0
            break
    return {"top": float(np.clip(t, 0.0, c)) * 1000.0, other: float(np.clip(c - d0, 0.0, c)) * 1000.0}


def _seg_dist(p, a, b):
    d = b - a
    t = float(np.clip((p - a) @ d / max(float(d @ d), 1e-30), 0.0, 1.0))
    return float(np.linalg.norm(p - (a + t * d)))


# -- the part function ----------------------------------------------------------------------------------------------

def step(facts, defn=None, data=None):
    """The step stone (SN3, SN4): facts in, its two levels out. facts: id, worldSeed, part ('step'), lengthMm, riseMm,
    goingMm, lapMm, ends {l, r: {kind: joint | walled | open, jointMm}}, back ('lapped' when the next step lies on
    it), wear {leftMm (the stone's left end from the flight's centre line), widthMm, lean, footfall, years,
    rateMmPerCentury}, corner (a broken corner the record holds, or None), years (bare, for UV1)."""
    data = data or Data()
    defn = defn if defn is not None else definition("step")
    o = outline(facts, defn, data)
    L0 = level_mesh(o, 0)
    L1 = level_mesh(o, 1)
    return dict(outline=o, L0=L0, L1=L1, commit=data.commit)


# -- the wall stone and the coping: their facts from R1's laying ------------------------------------------------------
#
# R1 lays a wall's stones as cells in the wall's elevation (s along the wall line, up the stair; z up), each from joint
# centre to joint centre: walling.json has no wall joint, so every stone is set in from its cell on each side it shares
# with a laid neighbour by a seeded half joint of its own (half of SN5's 4 to 12 mm, whole mm), and a joint is the sum
# of its two stones' halves, within SN5 whatever either draws. A stone's frame is right-handed and its own: x along its
# face from its left end as one looking at that face sees it, y back from the face, z up from its bed; so x runs up the
# wall line (+s) on a right-hand wall's bank face and a left-hand wall's stair face, and down it (-s) on the others
# (alongS in the facts: the placement is a turn, never a mirror).

def _box(s):
    xs = [p[0] for p in s["outline"]]
    zs = [p[1] for p in s["outline"]]
    return min(xs), max(xs), min(zs), max(zs)


def _cell(s):
    """A cell's length along the wall and its height (mm)."""
    x0, x1, z0, z1 = _box(s)
    return x1 - x0, z1 - z0


def _median(v):
    v = sorted(v)
    n = len(v)
    return Fraction(v[n // 2]) if n % 2 else Fraction(v[n // 2 - 1] + v[n // 2], 2)


def _iqr(v):
    v = sorted(v)
    n = len(v)
    return _median(v[(n + 1) // 2:]) - _median(v[:n // 2])


def along_s(side, face):
    """+1 where a stone's x runs up the wall line (s), -1 where down it: x = y cross z, y back from the face."""
    into = side if face == "stair" else -side        # y, across the stair in the stair's x: +1 to its right
    return -into


def wall_sides(wall, stone, face):
    """The kinds of the stones whose cells share a stretch of each side of a face stone's cell on its face, by the
    cell's sides in s and z: {lo, hi, b, t}."""
    x0, x1, z0, z1 = _box(stone)
    out = {"lo": [], "hi": [], "b": [], "t": []}
    for o in wall["stones"]:
        if o is stone or face not in o["faces"]:
            continue
        a0, a1, b0, b1 = _box(o)
        if a1 == x0 and min(z1, b1) > max(z0, b0):
            out["lo"].append(o["kind"])
        if a0 == x1 and min(z1, b1) > max(z0, b0):
            out["hi"].append(o["kind"])
        if b1 == z0 and min(x1, a1) > max(x0, a0):
            out["b"].append(o["kind"])
        if b0 == z1 and min(x1, a1) > max(x0, a0):
            out["t"].append(o["kind"])
    return out


def face_pool(data):
    """The face stones the wall stone part makes: every face stone of a panel as built whose cell has a face or
    through stone against all four of its sides on its face (the walls' ordinary stones; one at a panel's edge, a
    head, a step's end, the ground or a coping is R2b's). [(wall, stone, face, sides)], by stone id."""
    out = []
    for w in data.laying()["walls"]:
        built = {p["id"] for p in w["panels"] if p["work"] == "built"}
        for s in w["stones"]:
            if s["kind"] != "face" or s.get("panel") not in built:
                continue
            face = s["faces"][0]
            sides = wall_sides(w, s, face)
            if all(v and all(k in ("face", "through") for k in v) for v in sides.values()):
                out.append((w, s, face, sides))
    return sorted(out, key=lambda t: t[1]["id"])


def wallstone_facts(data, wall, stone, face, sides):
    """A face stone's facts from R1's laying: its cell, what lies against each side (a joint: the part sets itself in
    by half of one), its working and when it was laid (its panel's), and the frame's way along the wall."""
    x0, x1, z0, z1 = _box(stone)
    if len(stone["outline"]) != 4:
        raise Failed(f"{stone['id']}: a cell of {len(stone['outline'])} corners; the part makes rectangles")
    panel = next(p for p in wall["panels"] if p["id"] == stone["panel"])
    working, laid = data.panel_working(wall["id"], panel)
    a = along_s(data.wall_side(wall["id"]), face)
    lo, hi = ("l", "r") if a > 0 else ("r", "l")
    kinds = {lo: sides["lo"], hi: sides["hi"], "b": sides["b"], "t": sides["t"]}
    return dict(id=stone["id"], worldSeed=data.world_seed(), part="wallstone", working=working, face=face,
                cellMm=[x1 - x0, z1 - z0], cellS=[x0, x1], cellZ=[z0, z1], alongS=a,
                sides={k: "joint" for k in ("l", "r", "b", "t")}, against={k: sorted(v) for k, v in kinds.items()},
                laid=laid, years=data.show_year() - laid)


def specimen_wallstone(data):
    """The wall stone judged alone, chosen by a rule from R1's laying: of the face stones the part makes (face_pool:
    in a panel as built, a face or through stone against all four sides), the one whose cell lies nearest the pool's
    median length and height, each difference over its interquartile range (exact fractions), the lowest id on a
    tie."""
    pool = face_pool(data)
    Ls = [_box(s)[1] - _box(s)[0] for _w, s, _f, _sd in pool]
    Hs = [_box(s)[3] - _box(s)[2] for _w, s, _f, _sd in pool]
    mL, mH, qL, qH = _median(Ls), _median(Hs), _iqr(Ls), _iqr(Hs)
    best = min(range(len(pool)), key=lambda i: (abs(Ls[i] - mL) / qL + abs(Hs[i] - mH) / qH, pool[i][1]["id"]))
    w, s, face, sides = pool[best]
    facts = wallstone_facts(data, w, s, face, sides)
    rule = dict(pool=len(pool), poolRule=face_pool.__doc__.split(": ", 1)[1].split(" [(")[0],
                medianMm=[float(mL), float(mH)], iqrMm=[float(qL), float(qH)], cellMm=facts["cellMm"],
                stone=s["id"], wall=w["id"], face=face, against=facts["against"],
                laid=dict(source=data.src["laying"]["source"], stone=s))
    data.note("specimen", s["id"], "stones.py specimen_wallstone: the rule in its docstring")
    return facts, rule


def coping_pool(data):
    """Every coping R1 lays: [(wall, stone)], by stone id."""
    return sorted(((w, s) for w in data.laying()["walls"] for s in w["stones"] if s["kind"] == "coping"),
                  key=lambda t: t[1]["id"])


def coping_facts(data, wall, stone):
    """A coping's facts from R1's laying: its cell (its run's thickness), its ends (a joint where R1 lays a stone
    against it, its run's copingJoints over the course under it; else open, a run's end over its riser, SN9's square
    step onto the run below), its faces (both long sides seen on a standing wall), its working and when it was laid."""
    x0, x1, z0, z1 = _box(stone)
    run = wall["copingRuns"][stone["run"]]
    joints = {j[0] for j in wall["copingJoints"].get(str(run["bedIndex"] - 1), [])}
    panel = next(p for p in wall["panels"] if p["id"] == stone["panel"])
    working, laid = data.panel_working(wall["id"], panel)
    a = along_s(data.wall_side(wall["id"]), "stair")       # its front is its stair side
    at = {"lo": x0, "hi": x1}
    lo, hi = ("l", "r") if a > 0 else ("r", "l")
    ends = {lo: "joint" if at["lo"] in joints else "open", hi: "joint" if at["hi"] in joints else "open"}
    return dict(id=stone["id"], worldSeed=data.world_seed(), part="coping", working=working,
                cellMm=[x1 - x0, z1 - z0], cellS=[x0, x1], cellZ=[z0, z1], alongS=a, run=stone["run"],
                runMm=dict(s=run["s"], bed=run["bed"], t=run["t"], top=run["top"]), ends=dict(l=ends["l"], r=ends["r"]),
                back="exposed" if "bank" in stone["faces"] else "hidden", faces=list(stone["faces"]),
                laid=laid, years=data.show_year() - laid)


def specimen_coping(data):
    """The coping judged alone, by the same rule as the wall stone's: of the copings of the panels as built, the one
    whose length and thickness lie nearest the medians, each difference over its interquartile range, the lowest id
    on a tie."""
    pool = []
    for w, s in coping_pool(data):
        built = {p["id"] for p in w["panels"] if p["work"] == "built"}
        if s.get("panel") in built:
            pool.append((w, s))
    Ls = [_box(s)[1] - _box(s)[0] for _w, s in pool]
    Ts = [_box(s)[3] - _box(s)[2] for _w, s in pool]
    mL, mT, qL, qT = _median(Ls), _median(Ts), _iqr(Ls), _iqr(Ts)
    best = min(range(len(pool)), key=lambda i: (abs(Ls[i] - mL) / qL + abs(Ts[i] - mT) / qT, pool[i][1]["id"]))
    w, s = pool[best]
    facts = coping_facts(data, w, s)
    rule = dict(pool=len(pool), medianMm=[float(mL), float(mT)], iqrMm=[float(qL), float(qT)],
                cellMm=facts["cellMm"], stone=s["id"], wall=w["id"], ends=facts["ends"], run=facts["runMm"],
                laid=dict(source=data.src["laying"]["source"], stone=s))
    data.note("specimen", s["id"], "stones.py specimen_coping: the rule in its docstring")
    return facts, rule


# -- the wall stone ----------------------------------------------------------------------------------------------------

def set_in(facts, data, sides):
    """Each side's half joint (whole mm, half of SN5's range each way), drawn for every side in a fixed order so a
    side's draw never depends on another's kind; 0 where the side is not a joint."""
    jlo, jhi = data.wall_joint(facts["working"])
    rs = HS.Stream(facts["worldSeed"], facts["id"], "joints")
    drawn = {k: rs.randint(-(-jlo // 2), jhi // 2) for k in sides}
    return {k: (drawn[k] if facts_side(facts, k) == "joint" else 0) for k in sides}


def facts_side(facts, k):
    if k in ("l", "r") and "ends" in facts:
        return facts["ends"][k]
    if k == "b" and facts["part"] == "coping":
        return "joint"
    return facts["sides"][k]


def bulge(H, b, ridges, steps):
    """A split face's facets as a convex bulge on the wall's plane (SN2's batter b, SN4's facets): the face's profile
    y(z) = max of its facets' lines, each facet below a ridge set back by its step past the line of the facet above
    (SN4: stepped where laminae broke), both its edges on the wall's plane y = b z (so the joints above and below it
    are the wall's, and a fill pressed in no deeper than the joint is wide meets it: SN5). ridges (m) from the top
    down, steps (m) each ridge's. Returns [(slope, intercept)] from the top facet down, and how far proud of the
    wall's plane each ridge stands (m)."""
    zs = [H] + list(ridges) + [0.0]
    delta = [s / (zs[i + 1] - zs[i + 2]) for i, s in enumerate(steps)]
    k_bot = b - sum(d * (H - r) / H for d, r in zip(delta, ridges))
    lines = []
    for j in range(len(ridges) + 1):
        lines.append((k_bot + sum(delta[j:]), -sum(d * r for d, r in zip(delta[j:], ridges[j:]))))
    proud = [b * r - max(k * r + e for k, e in lines) for r in ridges]
    return lines, proud


def outline_wallstone(facts, defn=None, data=None):
    """A wall face stone (SN2, SN4, SN5): a rigid convex block on its natural bed, its top and bed the laminae's planes
    (bed faces, level), its face split across them at the batter, of one facet or two in a convex bulge whose edges lie
    on the wall's plane; its ends split. Set into its cell by its half joints, seeded within SN5's range unless they
    would draw it longer than SN10's 4.5 times its height (then the least above and below, the most at the ends;
    a cell at R1's limit cannot be drawn within SN10 by any joint: blender.md, the conflicts). What is drawn: the face, and of its
    top, bed and ends only a band behind the wall's plane, measured level, as deep as a joint is seen (the widest, its
    fill no deeper than it is wide, and SN9's contact) and never less than two pixels at a level's far edge seen at the
    gate's 20 degrees past the chamfer, with a margin (L1's sets it: 77 mm); behind the band the stone is in the wall,
    never seen, and its back (half the wall's top, hidden) changes nothing drawn. L0 chamfers the face's arrises with
    the top and the ends (SN4's seen arrises; the arrises running back into the wall lie in its joints), each end's
    meeting the top's at one point; the bed's stays square (SN7: its chamfer would face down, the dark line beneath an
    edge; bedChamfer is the arm, each end's then meeting the bed's at one point)."""
    data = data or Data()
    part = facts["part"]
    world, sid = facts["worldSeed"], facts["id"]
    P = lambda key: param(part, defn, key, data)  # noqa: E731
    working = facts["working"]
    half = set_in(facts, data, ("l", "r", "b", "t"))
    Lc, Hc = facts["cellMm"]
    sn10 = None
    if Fraction(Lc - half["l"] - half["r"], Hc - half["b"] - half["t"]) > Fraction(*SN10_RATIO):
        # SN10 binds the stone, not its cell: where the seeded half joints (texture within SN5's range) would draw it
        # longer than 4.5 times its height, they are drawn the least above and below and the most at the ends
        jlo, jhi = data.wall_joint(working)
        half = dict(l=jhi // 2, r=jhi // 2, b=-(-jlo // 2), t=-(-jlo // 2))
        sn10 = "SN10: the half joints the least above and below and the most at the ends"
    Lmm = Lc - half["l"] - half["r"]
    Hmm = Hc - half["b"] - half["t"]
    L, H = _f(Lmm), _f(Hmm)
    bk, bu = data.batter(working)
    b = bk / bu
    # the face's facets: ridges from the stone's laminae, each stepped a seeded whole mm
    least = _f(P("facetLeastMm"))
    counts = [(int(a), int(w)) for a, w in P("faceFacets")]
    lam = laminae(HS.Stream(world, sid, "laminae"), H, least, max(a for a, _w in counts) - 1)
    rng = HS.Stream(world, sid, "face")
    nf = min(rng.weighted(counts), len(lam) + 1)
    pool, chosen = list(lam), []
    for _ in range(nf - 1):
        chosen.append(pool.pop(rng.randint(0, len(pool) - 1)))
    chosen.sort(reverse=True)
    steps_mm = [rng.randint(*P("facetStepMm")) for _ in chosen]
    lines, proud = bulge(H, b, [_f(z) for z in chosen], [_f(s) for s in steps_mm])
    facets = []
    for j, (k, e) in enumerate(lines):
        nn = math.sqrt(1.0 + k * k)
        info = dict(kind=2, slope=k)
        if j:
            info.update(ridge=_f(chosen[j - 1]), setbackMm=steps_mm[j - 1])
        facets.append(B.plane("front" if j == 0 else f"front/facet-{j + 1}", (0.0, -1.0, k), d=-e / nn, face="front",
                              **info))
    back = _f(data.top_thick(working)) / 2.0
    block = [B.plane("top", (0, 0, 1), d=H, kind=3), B.plane("bed", (0, 0, -1), d=0.0, kind=3),
             B.plane("end-l", (-1, 0, 0), d=0.0, kind=2), B.plane("end-r", (1, 0, 0), d=L, kind=2),
             B.plane("back", (0, 1, 0), d=back, role="hidden")] + facets
    clo, chi = P("chamferMm")
    c_mm = HS.Stream(world, sid, "chamfer").randint(clo, chi)
    if P("chamferMeasure") != "leg":
        raise ValueError(f"chamferMeasure {P('chamferMeasure')!r}: only 'leg' is built (blender.md)")
    by = {p["name"]: p for p in block}
    pairs = [("front", "top"), ("end-l", "front"), ("end-r", "front")] + ([("bed", "front")] if P("bedChamfer")
                                                                          else [])

    def start(pair, made):
        # an end's chamfer through the point where the top's chamfer meets the top and the end, and the bed's through
        # where the end's lowest piece meets the bed and the end: the arrises running back into the wall are square,
        # so each corner is one point (else a cap c (sqrt(1 + b^2) - 1) across, 0.15 mm, between two chamfers)
        if pair in (("end-l", "front"), ("end-r", "front")):
            c1 = next(p for p, _s, _a in made if p["chamfer"] == ("front", "top"))
            return B._meet([by["top"], by[pair[0]], c1])
        if pair == ("bed", "front"):
            low = min((p for p, _s, _a in made if p["chamfer"] == ("end-l", "front")),
                      key=lambda p: min(p["arris"][0][2], p["arris"][1][2]))
            return B._meet([by["bed"], by["end-l"], low])
        return None

    ch = B.chamfers(block, _f(c_mm), P("arrisMaxDeg"), pairs=pairs, start=start)
    jmax = data.wall_joint(working)[1]
    sin20 = math.sin(math.radians(20.0))
    margin = 1.0 + P("bandMarginPerMille") / 1000.0
    band_mm = max(jmax + SN9["contactMm"], c_mm + math.ceil(two_px(0) * 1000.0 * margin / sin20),
                  math.ceil(two_px(1) * 1000.0 * margin / sin20))
    nb = math.sqrt(1.0 + b * b)
    seen = [dict(n=np.array([0.0, 1.0, -b]) / nb, d=_f(band_mm) / nb)]
    regions = {f: [seen] for f in ("top", "bed", "end-l", "end-r")}
    o = dict(facts=facts, part=part, L=L, H=H, g=0.0, D=back, skirt=0.0, block=block, covers=[], chamfers=ch,
             chamferMm=c_mm, chips=[], wear=None, rows0=[], rows1=[], cols0=[], cols1=[], flat=0.0, flat1=0.0,
             regions=regions, laminaeMm=lam, tol0=_f(data.level_error(part, "l0")),
             tol1=_f(data.level_error(part, "l1")), y_end=back, ends=dict(l="joint", r="joint"),
             faceRoles={"top": "bed", "bed": "bed"}, target=np.array([L / 2, b * H / 2, H / 2]), batter=b,
             bandMm=band_mm, setInMm=half, setInRule=sn10, faceFacets=len(lines), ridgesMm=sorted(chosen, reverse=True),
             setbacksMm=steps_mm, proudMm=[round(p * 1000, 2) for p in proud], bedChamfer=bool(P("bedChamfer")))
    o["faces"] = face_frames(o, defn, data)
    _unfold(o)
    o["summary"] = dict(cellMm=facts["cellMm"], setInMm=half, setInRule=sn10, lengthMm=Lmm, heightMm=Hmm,
                        batter=[bk, bu], faceFacets=len(lines), laminaeMm=lam, ridgesMm=o["ridgesMm"],
                        setbacksMm=steps_mm, slopes=[round(k, 6) for k, _e in lines], ridgeProudMm=o["proudMm"],
                        bandMm=band_mm, backMm=round(back * 1000), bedChamfer=o["bedChamfer"], chamfers=len(ch),
                        legDriftMm=[round(p["legDrift"] * 1000, 4) for p, _s, _a in ch],
                        faces=_faces_summary(o))
    o["boundsNote"] = (f"the pivot is the bed's front left corner; the face's edges lie on the wall's plane (y = "
                       f"{bk}/{bu} z back), its bulge up to {max(o['proudMm'] or [0.0]):g} mm proud of it; the top, the "
                       f"bed and the ends are drawn only {band_mm} mm behind that plane, measured level")
    return o


def _faces_summary(o):
    return {f: dict(kind=fr["kind"], patch=fr["patch"], slice=fr["slice"], mode=fr["mode"], offsetMm=list(fr["offset"]),
                    turnDeg=fr.get("turnDeg")) for f, fr in sorted(o["faces"].items())}


def wallstone(facts, defn=None, data=None):
    """The wall face stone: facts in (wallstone_facts), its two levels out."""
    data = data or Data()
    defn = defn if defn is not None else definition("wallstone")
    o = outline_wallstone(facts, defn, data)
    return dict(outline=o, L0=level_mesh(o, 0), L1=level_mesh(o, 1), commit=data.commit)


# -- the coping --------------------------------------------------------------------------------------------------------

def outline_coping(facts, defn=None, data=None):
    """A coping slab (SN2, SN4, SN9): a rigid block of split slate on its bed across the wall's top, the wall's top
    and its overhangs wide (walling: topThick and copeOver), its run's thickness less its bed's half joint: its top and
    bed the laminae's planes (bed faces), its long sides and ends split, one plane each (a face of 70 to 100 mm has no
    room for a second facet of 50: SN9). Its front stands a seeded whole mm proud of the stair's face (copeProud), its
    back the rest of the overhang (a standing wall's bank face); its bed is drawn under the overhangs and a joint's
    band past the faces under them. An open end (a run's end over its riser) is square and drawn whole, its top
    corners knocked by seed (SN4: chips at a coping's ends); a joint end is set in by its half joint and drawn where
    the joint is seen: within the band below the top and behind each face, the wall's plane leaning back above the
    bed. L0 chamfers the top's arrises, its perimeter, and those only: the bed's would face down (SN7, bedChamfer);
    the ends' upright arrises each meet two of the top's at a corner, where three chamfers meet in a point whose tips
    are under 2 px at 8 m whatever the triangulation (SN8), and two in a mitre that has none (uprightChamfer); a knock
    is a break after the dressing, its arrises sharp, cutting through the top's chamfers (chipChamfer); a joint end's
    arris with the bed is inside the joint."""
    data = data or Data()
    part = facts["part"]
    world, sid = facts["worldSeed"], facts["id"]
    P = lambda key: param(part, defn, key, data)  # noqa: E731
    working = facts["working"]
    half = set_in(facts, data, ("l", "r", "b"))
    Lmm = facts["cellMm"][0] - half["l"] - half["r"]
    Tmm = facts["cellMm"][1] - half["b"]
    over = data.cope_over(working)
    Wmm = data.top_thick(working) + over
    proud = HS.Stream(world, sid, "proud").randint(*data.cope_proud(working))
    proud_back = over - proud
    L, T, W = _f(Lmm), _f(Tmm), _f(Wmm)
    bk, bu = data.batter(working)
    b = bk / bu
    back_seen = facts["back"] == "exposed"
    block = [B.plane("top", (0, 0, 1), d=T, kind=3), B.plane("bed", (0, 0, -1), d=0.0, kind=3),
             B.plane("front", (0, -1, 0), d=0.0, kind=2),
             B.plane("back", (0, 1, 0), d=W, kind=2, role="exposed" if back_seen else "hidden"),
             B.plane("end-l", (-1, 0, 0), d=0.0, kind=2), B.plane("end-r", (1, 0, 0), d=L, kind=2)]
    centre = np.array([L / 2, W / 2, T / 2])
    chips = []
    for side in ("l", "r"):
        if facts["ends"][side] != "open":
            continue
        for corner in ("front", "back") if back_seen else ("front",):
            r3 = HS.Stream(world, sid, f"chip-{side}-{corner}")
            if r3.randint(0, 999) < P("chipPerMille"):
                lo, hi = P("chipLegMm")
                bb, aa = _f(r3.randint(lo, hi)), _f(r3.randint(lo, hi))
                dz = _f(min(r3.randint(lo, hi), Tmm * P("chipDepthPerMille") // 1000))
                bb, aa, grown = chip_least(bb, aa, dz)
                chips.append(corner_chip(f"chip:{side}-{corner}", side, L, T, (bb, aa, dz), centre,
                                         back=W if corner == "back" else None, fact="knocked (seed)",
                                         grownPerMille=grown))
    clo, chi = P("chamferMm")
    c_mm = HS.Stream(world, sid, "chamfer").randint(clo, chi)
    if P("chamferMeasure") != "leg":
        raise ValueError(f"chamferMeasure {P('chamferMeasure')!r}: only 'leg' is built (blender.md)")
    faces = B.polyhedron([p for p in block + chips if p["role"] in ("exposed", "hidden")])
    every = sorted({tuple(sorted((faces[i][0]["face"], faces[j][0]["face"])))
                    for i, j, _e, _a in B.arrises(faces, P("arrisMaxDeg"))})
    inside = {tuple(sorted(("bed", f"end-{s}"))) for s in ("l", "r") if facts["ends"][s] == "joint"}
    square = {}
    for k in every:
        if k in inside:
            square[k] = "in the joint"
        elif "bed" in k and not P("bedChamfer"):
            square[k] = "the bed's (SN7)"
        elif any(f.startswith("chip:") for f in k) and not P("chipChamfer"):
            square[k] = "a knock's"
        elif "top" not in k and not any(f.startswith("chip:") for f in k) and "bed" not in k \
                and not P("uprightChamfer"):
            square[k] = "upright (SN8: a corner of three)"
    ch = B.chamfers(block + chips, _f(c_mm), P("arrisMaxDeg"), pairs=[k for k in every if k not in square])
    # where it is seen: the bed under each overhang and a joint's band past the face under it; a joint end within the
    # band below the top (seen from above into the joint) and behind each face (the wall's plane above the bed leans
    # back b per its height: the band reaches past it at the top)
    jmax = data.wall_joint(working)[1]
    bed_band = jmax + SN9["contactMm"]
    cb = max(jmax + SN9["contactMm"], c_mm + math.ceil(two_px(0) * 1000))
    up = np.array([0.0, 0.0, 1.0])
    ey = np.array([0.0, 1.0, 0.0])
    regions = {"bed": [[dict(n=ey, d=_f(proud + bed_band))]] +
                      ([[dict(n=-ey, d=-(W - _f(proud_back + bed_band)))]] if back_seen else [])}
    lean = math.ceil(b * Tmm)
    for side in ("l", "r"):
        if facts["ends"][side] != "joint":
            continue
        below = dict(n=up, d=T - _f(cb))
        reg = [[dict(n=-up, d=-(T - _f(cb)))], [dict(n=ey, d=_f(proud + lean + cb)), below]]
        if back_seen:
            reg.append([dict(n=-ey, d=-(W - _f(proud_back + lean + cb))), below])
        regions[f"end-{side}"] = reg
    o = dict(facts=facts, part=part, L=L, H=T, g=0.0, D=W, skirt=0.0, block=block, covers=[], chamfers=ch,
             chamferMm=c_mm, chips=chips, wear=None, rows0=[], rows1=[], cols0=[], cols1=[], flat=0.0, flat1=0.0,
             regions=regions, laminaeMm=[], tol0=_f(data.level_error(part, "l0")),
             tol1=_f(data.level_error(part, "l1")), y_end=W, ends=dict(facts["ends"]),
             faceRoles={"top": "bed", "bed": "bed"}, target=np.array([L / 2, 0.0, T / 2]), batter=b,
             setInMm=half, proudMm=[proud, proud_back])
    o["faces"] = face_frames(o, defn, data)
    _unfold(o)
    o["summary"] = dict(cellMm=facts["cellMm"], setInMm=half, lengthMm=Lmm, thicknessMm=Tmm, widthMm=Wmm,
                        proudMm=dict(front=proud, back=proud_back if back_seen else None), ends=facts["ends"],
                        back=facts["back"], bedBandMm=bed_band, jointBandMm=cb, batterLeanMm=lean,
                        chips=[dict(name=c["name"], legsMm=c.get("legsMm"), fact=c.get("fact"),
                                    grownPerMille=c.get("grownPerMille")) for c in chips],
                        chamfers=len(ch), squareArrises={"|".join(k): why for k, why in sorted(square.items())},
                        faces=_faces_summary(o))
    o["boundsNote"] = (f"the pivot is the bed's front left corner; the front stands {proud} mm proud of the stair's "
                       f"face, the back {proud_back} mm of the bank's; the bed is drawn under each overhang and "
                       f"{bed_band} mm past the face under it")
    return o


def coping(facts, defn=None, data=None):
    """The coping: facts in (coping_facts), its two levels out."""
    data = data or Data()
    defn = defn if defn is not None else definition("coping")
    o = outline_coping(facts, defn, data)
    return dict(outline=o, L0=level_mesh(o, 0), L1=level_mesh(o, 1), commit=data.commit)


def build(part, facts, defn=None, data=None):
    return {"step": step, "wallstone": wallstone, "coping": coping}[part](facts, defn, data)


# -- checks (SN8, SN9; the export runs them and stops on any failure) -------------------------------------------------

class Failed(Exception):
    pass


def views(o, distance):
    """The stated views (plan.md, the judging set; the memory's raised views): face-on with 20 degrees of top seen,
    from eye height (1.6 m over the street the stone lies on), 40 degrees to either side at 20 up, and raised at 45;
    each at distance (m) from the middle of the stone's drawn front (a part's own target where it gives one), the 28 mm
    lens."""
    target = o["target"] if "target" in o else np.array([o["L"] / 2, o["g"] / 2, o["H"] / 2])
    out = {}
    eye = math.degrees(math.asin(min(1.0, (1.6 - target[2]) / distance)))
    for name, az, el in (("face-on 20", 0, 20), ("eye 1.6 m", 0, eye), ("left 40", -40, 20), ("right 40", 40, 20),
                         ("raised 45", 0, 45)):
        a, e = math.radians(az), math.radians(el)
        d = np.array([math.sin(a) * math.cos(e), -math.cos(a) * math.cos(e), math.sin(e)])
        out[name] = dict(cam=target + distance * d, target=target, az=az, el=round(el, 2))
    return out


def project(view, P):
    f = B.unit(view["target"] - view["cam"])
    r = B.unit(np.cross(f, np.array([0.0, 0.0, 1.0])))
    u = np.cross(r, f)
    q = P - view["cam"]
    zc = q @ f
    fp = focal_px()
    return np.stack([RIG["width"] / 2 + fp * (q @ r) / zc, RIG["height"] / 2 - fp * (q @ u) / zc], -1), zc


def thin_gate(m, view, keep=False):
    """SN8's gate in one view: the front-facing triangles (a convex block hides none of its own front faces but the
    wear's few hundredths of a degree), each one's smallest altitude in px and its area in px. With keep, the
    altitudes and areas too (a pool's)."""
    V, T = m["V"], m["T"]
    out = []
    for t, tri in enumerate(T):
        P3 = V[tri]
        c = P3.mean(axis=0)
        if m["plane"][t]["n"] @ (view["cam"] - c) <= 0:
            continue
        p2, _ = project(view, P3)
        a, b, cc = p2
        A2 = abs((b[0] - a[0]) * (cc[1] - a[1]) - (b[1] - a[1]) * (cc[0] - a[0]))
        Lmax = max(np.linalg.norm(b - a), np.linalg.norm(cc - a), np.linalg.norm(cc - b))
        out.append((A2 / Lmax if Lmax > 0 else 0.0, 0.5 * A2, m["face"][t]))
    alt = np.array([x[0] for x in out])
    area = np.array([x[1] for x in out])
    thin = alt < GATE["thinPx"]
    r = dict(front=len(out), thin=int(thin.sum()), thinShare=round(float(thin.mean()) if len(out) else 0.0, 4),
             thinFaces=sorted({out[i][2] for i in np.nonzero(thin)[0]}),
             medianAreaPx=round(float(np.median(area)), 1) if len(out) else 0.0,
             medianAltitudePx=round(float(np.median(alt)), 2) if len(out) else 0.0,
             ok=bool(len(out) and thin.mean() <= GATE["thinShare"] and np.median(area) >= GATE["medianAreaPx"]))
    if keep:
        r["altitudesPx"], r["areasPx"] = alt.tolist(), area.tolist()
    return r


def chamfer_px(o, view):
    """Each chamfer's width on screen at its arris's middle, exactly through the lens: the distance in px between its
    two edges (the setback lines on its faces), across the arris's own direction on screen; with the angle the
    chamfer is seen at from its normal."""
    out = []
    for p, _s, _a in o["chamfers"]:
        q0, q1 = p["arris"]
        mid = 0.5 * (q0 + q1)
        ua, ub = p["inward"]
        leg = p["leg"]
        pts = np.array([mid + leg * ua, mid + leg * ub, mid + leg * ua + 0.01 * B.unit(q1 - q0)])
        p2, _ = project(view, pts)
        e = B.unit(p2[2] - p2[0]) if np.linalg.norm(p2[2] - p2[0]) > 0 else np.array([1.0, 0.0])
        w = abs((p2[1] - p2[0])[0] * e[1] - (p2[1] - p2[0])[1] * e[0])
        to_cam = B.unit(view["cam"] - mid)
        ang = math.degrees(math.acos(float(np.clip(p["n"] @ to_cam, -1.0, 1.0))))
        out.append(dict(face=p["face"], px=round(w, 2), seenDeg=round(ang, 1)))
    return out


def indexed_vertices(m):
    """The vertices an exact indexed mesh needs for one level: its corners identical in every channel (position, the
    face's normal and all eight UV layers, as the float32 values the export writes) counted once. Step 5's chunks
    carry vertices exactly and may share such corners; but the edge distances (UV6, UV7) are each triangle's own, so
    under the contract nearly every corner is its triangle's alone, and this is close to three a triangle."""
    T = np.asarray(m["T"])
    nt = len(T)
    P = np.asarray(m["V"], np.float64).astype(np.float32)[T.ravel()]
    N = np.repeat(np.asarray([p["n"] for p in m["plane"]], np.float64).astype(np.float32), 3, axis=0)
    UV = np.asarray(m["UV"], np.float32).reshape(8, 3 * nt, 2)
    rows = np.ascontiguousarray(np.concatenate([P, N] + list(UV), axis=1)) + np.float32(0.0)   # -0.0 as 0.0
    return int(len(np.unique(rows.view(np.dtype((np.void, rows.dtype.itemsize * rows.shape[1]))))))


def check(part, out, defn):
    """Every check SN8 and SN9 give a part, run on both levels: a dict of results, and the list of failures. Two are
    a level's, not a piece's, and are reported here and held over the pools (level_gate): SN8's share of thin
    triangles (a level's front-facing triangles at its far edge, the fills included) and building-blocks.md's 60%
    (each kind's export check: L1 at most 60% of L0)."""
    o, L0, L1 = out["outline"], out["L0"], out["L1"]
    fails = []
    res = {}
    lv = defn["levels"]
    data = Data(out["commit"])
    # the facts against the working: the lap on the step below and each joint to the next stone (R1's laying's)
    res["facts"] = facts_checks(o["facts"], data, o)
    fails += res["facts"]["fails"]
    res["form"] = form_checks(o)
    fails += res["form"]["fails"]
    # budgets
    res["triangles"] = dict(L0=len(L0["T"]), L1=len(L1["T"]), budget=[lv["l0"]["triangles"], lv["l1"]["triangles"]],
                            ratio=round(len(L1["T"]) / max(len(L0["T"]), 1), 3),
                            vertices=dict(L0=len(L0["V"]), L1=len(L1["V"])),
                            indexedVertices=dict(L0=indexed_vertices(L0), L1=indexed_vertices(L1)),
                            fbxVertices=dict(L0=3 * len(L0["T"]), L1=3 * len(L1["T"])))
    if len(L0["T"]) > lv["l0"]["triangles"]:
        fails.append(f"budget: L0 {len(L0['T'])} > {lv['l0']['triangles']}")
    if len(L1["T"]) > lv["l1"]["triangles"]:
        fails.append(f"budget: L1 {len(L1['T'])} > {lv['l1']['triangles']}")
    res["triangles"]["ratioWithin"] = bool(len(L1["T"]) <= LEVEL_RATIO * len(L0["T"]))
    for name, m in (("L0", L0), ("L1", L1)):
        r = mesh_checks(o, m)
        res[name] = r
        fails += [f"{name} {f}" for f in r["fails"]]
    # the block's own faces: convex, slivers, no rake
    res["block"] = block_checks(o)
    fails += res["block"]["fails"]
    # the wear field against its law
    res["wear"] = dict(L0=wear_checks(o, L0, o["tol0"]), L1=wear_checks(o, L1, o["tol1"]))
    fails += res["wear"]["L0"]["fails"] + [f"L1 {f}" for f in res["wear"]["L1"]["fails"]]
    # L1 against L0
    res["l1VsL0"] = l1_vs_l0(o, L0, L1, data.level_error(part, "l1"))
    fails += res["l1VsL0"]["fails"]
    # thin triangles at each level's far edge
    th = {}
    for name, m, dist in (("L0", L0, GATE["l0Distance"]), ("L1", L1, GATE["l1Distance"])):
        th[name] = {vn: thin_gate(m, v) for vn, v in views(o, dist).items()}
        for vn, r in th[name].items():
            r["view"] = "the level's view (pooled)" if vn in GATED_VIEWS else "reported"
    res["thin"] = th
    # the skirts: the top drawn under the next step reaches past that step's foot (its riser set back by up to the
    # facets' largest step) and SN9's contact; the bed's skirt reaches below the worn top of the step below where this
    # riser's foot stands on it (this stone's own wear at its back, the same law) and the contact
    if part == "step":
        res["skirts"] = skirt_checks(o, defn)
        fails += res["skirts"]["fails"]
    # the chamfer's width at 8 m
    cw = {vn: chamfer_px(o, v) for vn, v in views(o, GATE["l0Distance"]).items()}
    low = [(vn, c) for vn, cs in cw.items() for c in cs if c["seenDeg"] <= 45.0 and c["px"] < SN9["chamferPx"]]
    res["chamferPx"] = dict(views=cw, rule="every chamfer seen within 45 degrees of its normal (as square as a face "
                            "seen face-on shows its leg) is at least 2 px wide at 8 m", ok=not low,
                            squareOnPx=round(math.sqrt(2) * o["chamferMm"] / 1000.0 / GATE["l0Distance"] *
                                             focal_px(), 2),
                            legFaceOnPx=round(o["chamferMm"] / 1000.0 / GATE["l0Distance"] * focal_px(), 2))
    for vn, c in low:
        fails.append(f"chamfer: {c['face']} {c['px']} px at 8 m in {vn} (seen {c['seenDeg']} degrees off its normal)")
    # determinism
    again = build(part, o["facts"], defn, Data(out["commit"]))
    same = all(np.array_equal(out[k]["V"], again[k]["V"]) and np.array_equal(out[k]["T"], again[k]["T"]) and
               np.array_equal(out[k]["UV"], again[k]["UV"]) for k in ("L0", "L1"))
    res["deterministic"] = same
    if not same:
        fails.append("determinism: a second build differs")
    res["fails"] = fails
    return res


def facts_checks(facts, data, o=None):
    """A stone's facts within its working, through Data's accessors (R1's laying's own rules, so a cell outside them
    is R1's to answer, named here): a step's lap and joints; a wall stone's course and length (SN10: no longer than
    4.5 times its height, nor than the working's longest; a short one only where a run leaves no whole stone) and its
    half joints; a coping's thickness and length."""
    if facts["part"] == "wallstone":
        return wall_facts_checks(facts, data, o)
    if facts["part"] == "coping":
        return coping_facts_checks(facts, data, o)
    lap, joint = data.tread_lap(), data.tread_joint()
    fails = []
    if facts.get("back") == "lapped" and not lap[0] <= facts["lapMm"] <= lap[1]:
        fails.append(f"facts: lap {facts['lapMm']} mm outside {lap}")
    widths = [e["jointMm"] for e in facts["ends"].values() if e["kind"] == "joint"]
    for w in widths:
        if not joint[0] <= w <= joint[1]:
            fails.append(f"facts: joint {w} mm outside {joint}")
    return dict(lapMm=facts["lapMm"], lapRangeMm=lap, jointsMm=widths, jointRangeMm=joint, fails=fails)


SN10_RATIO = (9, 2)     # SN10: no stone longer than 4.5 times its height (masonry.py's RATIO, the rule of any wall)


def _half_checks(o, data, working, fails):
    jlo, jhi = data.wall_joint(working)
    lo, hi = -(-jlo // 2), jhi // 2
    half = o["setInMm"]
    for k, v in sorted(half.items()):
        if facts_side(o["facts"], k) == "joint" and not lo <= v <= hi:
            fails.append(f"facts: the {k} half joint {v} mm outside [{lo}, {hi}]")
    return dict(halfJointMm=half, halfRangeMm=[lo, hi], jointRangeMm=[jlo, jhi])


def wall_facts_checks(facts, data, o):
    name = facts["working"]
    course = data.walling_value(name, "courseMm")
    stone = data.walling_value(name, "stoneMm")
    short = data.walling_value(name, "shortMm")
    draw = data.walling_value(name, "drawnPerHeight")
    L, H = facts["cellMm"]
    fails = []
    if not course[0] <= H <= course[1]:
        fails.append(f"facts: a course {H} mm outside {course}")
    longest = min(stone[1], SN10_RATIO[0] * H // SN10_RATIO[1])
    if not short <= L <= longest:
        fails.append(f"facts: a cell {L} mm long outside [{short}, {longest}] (shortMm; SN10 and stoneMm)")
    r = dict(cellMm=[L, H], courseRangeMm=course, lengthRangeMm=[short, longest], stoneMm=stone,
             short=L < stone[0], drawnPerHeight=draw,
             withinDrawn=bool(Fraction(*draw[0]) <= Fraction(L, H) <= Fraction(*draw[1])))
    if o is not None:
        r.update(_half_checks(o, data, name, fails))
        Ls, Hs = o["summary"]["lengthMm"], o["summary"]["heightMm"]
        r["stoneMm"] = [Ls, Hs]
        if Fraction(Ls, Hs) > Fraction(*SN10_RATIO):
            fails.append(f"facts: the stone {Ls} by {Hs} mm, longer than 4.5 times its height (SN10)")
    r["fails"] = fails
    return r


def coping_facts_checks(facts, data, o):
    name = facts["working"]
    thick = data.walling_value(name, "copeThickMm")
    length = data.walling_value(name, "copeLengthMm")
    least = data.walling_value(name, "copeLeastMm")
    L, T = facts["cellMm"]
    fails = []
    if not thick[0] <= T <= thick[1]:
        fails.append(f"facts: a coping {T} mm thick outside {thick}")
    if not least <= L <= length[1]:
        fails.append(f"facts: a coping {L} mm long outside [{least}, {length[1]}] (copeLeastMm, copeLengthMm)")
    r = dict(cellMm=[L, T], thickRangeMm=thick, lengthRangeMm=[least, length[1]], short=L < length[0],
             ends=facts["ends"])
    if o is not None:
        r.update(_half_checks(o, data, name, fails))
        r["drawnMm"] = [o["summary"]["lengthMm"], o["summary"]["thicknessMm"]]
    r["fails"] = fails
    return r


def form_checks(o):
    """A wall stone's face against the wall it stands in (SN2, SN4, SN5): both its edges on the wall's plane (the
    joints above and below it are the wall's), each facet a lamina high at least (folds: SN9), each ridge stepped
    within facetStepMm, the bulge convex; and every face but the face drawn only within the band. A coping: its
    proud fronts within copeProud and copeOver."""
    fails = []
    if o.get("part") != "wallstone":
        return dict(fails=fails)
    b, H = o["batter"], o["H"]
    facets = [p for p in o["block"] if p.get("face") == "front"]
    top_f = next(p for p in facets if p["name"] == "front")         # the top facet; the block lists them down
    bot_f = facets[-1]
    y_top = (top_f["d"] - top_f["n"][2] * H) / top_f["n"][1]       # n . (x, y, z) = d with n_x = 0, solved for y
    y_bed = bot_f["d"] / bot_f["n"][1]
    off = max(abs(y_top - b * H), abs(y_bed))
    if off > 1e-9:
        fails.append(f"form: the face's edges {off * 1000:.4f} mm off the wall's plane")
    proud = o["proudMm"]
    if any(p < 0 for p in proud):
        fails.append("form: a ridge behind the wall's plane (the bulge not convex)")
    return dict(edgesOffPlaneMm=round(off * 1000, 6), ridgeProudMm=proud, facets=len(facets), fails=fails)


def skirt_checks(o, defn):
    """The skirts reach far enough: the top drawn under the next step past that step's riser foot, set back by its
    facets' steps at most, and SN9's contact; the riser drawn below its bed past the worn top of the step below where
    its foot stands (this stone's own wear at its back, the same law), and the contact."""
    fails = []
    s_mm = o["skirt"] * 1000.0
    part = o["facts"]["part"]
    most = max(int(a) for a, _w in param(part, defn, "riserFacets", None))
    setback = float((most - 1) * param(part, defn, "facetStepMm", None)[1])
    contact = SN9["contactMm"]
    r = dict(skirtMm=s_mm, footSetbackMaxMm=setback, contactMm=contact)
    if o["covers"]:
        need = setback + contact
        r["coverNeedMm"] = need
        if s_mm < need:
            fails.append(f"skirt: the top under the next step reaches {s_mm:g} mm past its riser, under {need:g} mm")
    xs = np.linspace(0.0, o["L"], 241)
    ys = np.linspace(max(o["g"] - setback / 1000.0, 0.0), o["g"], 11)
    worn = float(np.max(o["wear"].depth(xs[:, None], ys[None, :]))) * 1000.0
    r["wornUnderFootMm"] = round(worn, 2)
    r["bedNeedMm"] = round(worn + contact, 2)
    if s_mm < worn + contact:
        fails.append(f"skirt: the bed's {s_mm:g} mm does not reach below the worn top under the foot "
                     f"({worn + contact:.1f} mm)")
    r["fails"] = fails
    return r


def mesh_checks(o, m):
    """One level's mesh: planar faces, inside the block, welded, no T-junctions, closed but where it should be open,
    hidden faces gone, the channel contract."""
    V, T = m["V"], m["T"]
    fails = []
    r = {}
    # planarity: every face's loop on its plane
    worst = 0.0
    for face, p, loop in m["groups"]:
        worst = max(worst, float(np.abs(V[loop] @ p["n"] - p["d"]).max()))
    r["planarMm"] = round(worst * 1000, 6)
    if worst * 1000 > SN9["planarMm"]:
        fails.append(f"planarity: {worst * 1000:.4f} mm")
    # inside the block (with its skirts), and the block convex by construction (half-spaces)
    out_worst = 0.0
    for p in o["block"] + o["chips"] + o["covers"]:
        lim = p["d"] + (p.get("skirt", 0.0) if p["role"] in ("hidden", "cover") else 0.0)
        out_worst = max(out_worst, float((V @ p["n"] - lim).max()))
    r["outsideBlockMm"] = round(max(out_worst, 0.0) * 1000, 6)
    if out_worst > 1e-7:
        fails.append(f"convexity: a vertex {out_worst * 1000:.4f} mm outside the block")
    # welds: no two vertices within 0.1 mm that are not one
    close = 0
    for i in range(len(V)):
        dd = np.linalg.norm(V[i + 1:] - V[i], axis=1)
        close += int(((dd > 0) & (dd < 1e-4)).sum())
    r["nearVertices"] = close
    if close:
        fails.append(f"welds: {close} pairs of vertices closer than 0.1 mm")
    # T-junctions: no vertex inside an edge
    edges = {}
    for t, tri in enumerate(T):
        for k in range(3):
            a, b = int(tri[k]), int(tri[(k + 1) % 3])
            edges.setdefault((a, b), []).append(t)
    tj = 0
    allv = np.arange(len(V))
    for (a, b) in edges:
        if a < b or (b, a) not in edges:
            tj += len(B._on_segment(V, a, b, allv))
    r["tJunctions"] = tj
    if tj:
        fails.append(f"T-junctions: {tj}")
    # manifold: every inner edge twice, once each way; open edges only where a drawn face ends at a hidden one
    open_e = [(a, b) for (a, b) in edges if (b, a) not in edges]
    dup = [(a, b) for (a, b), ts in edges.items() if len(ts) > 1]
    r["openEdges"] = len(open_e)
    r["openEdgesOn"] = sorted(_open_on(o, V, open_e))
    if dup:
        fails.append(f"manifold: {len(dup)} edges used twice the same way")
    bad_open = [e for e in open_e if not _on_hidden(o, V, e)]
    r["openNotOnHidden"] = len(bad_open)
    if bad_open:
        fails.append(f"open edges: {len(bad_open)} not on a hidden face, a cover or a seen region's edge")
    # hidden faces gone
    hidden = {p["face"] for p in o["block"] if p["role"] == "hidden"}
    drawn_hidden = sorted({f for f in m["face"] if f in hidden})
    r["hiddenDrawn"] = drawn_hidden
    if drawn_hidden:
        fails.append(f"hidden faces drawn: {drawn_hidden}")
    # degenerate triangles
    alt, area = B.tri_altitudes(V, T)
    r["smallestAltitudeMm"] = round(float(alt.min()) * 1000, 4)
    if alt.min() <= 1e-6:
        fails.append(f"degenerate triangle: altitude {alt.min() * 1000:.6f} mm")
    # the channel contract
    r["contract"] = contract_checks(o, m)
    fails += r["contract"]["fails"]
    r["fails"] = fails
    return r


def _open_on(o, V, open_e):
    names = set()
    for a, b in open_e:
        names.add(_which(o, V[a], V[b]))
    return names


def bounds(o):
    """Where the drawn surface may end open, as (n, d): the hidden planes and covers moved out by their skirts, each
    seen region's half-spaces, a joint end's plane (where its fill meets it). _which names them; collapse keeps every
    vertex on those it lies on."""
    return [(n, d) for _name, n, d in _limits(o)]


def _limits(o):
    lims = []
    for p in o["block"] + o["covers"]:
        if p["role"] in ("hidden", "cover"):
            lims.append((p["name"], p["n"], p["d"] + p.get("skirt", 0.0)))
    for face, regs in o["regions"].items():
        for k, reg in enumerate(regs):
            for h in reg:
                lims.append((f"{face} seen", h["n"], h["d"]))
    for p in o["block"]:            # an edge on a joint end's plane meets the joint's fill there (SN5)
        if p["name"] in o["regions"]:
            lims.append((f"{p['name']} fill", p["n"], p["d"]))
    return lims


def _which(o, A, Bp):
    for name, n, d in _limits(o):
        if abs(A @ n - d) < 1e-7 and abs(Bp @ n - d) < 1e-7:
            return name
    return "?"


def _on_hidden(o, V, e):
    return _which(o, V[e[0]], V[e[1]]) != "?"


def contract_checks(o, m):
    UV = m["UV"]
    fails = []
    kinds = UV[2, :, :, 0]
    if not np.isin(kinds, [0, 1, 2, 3]).all() or (UV[2, :, :, 1] != 0).any():
        fails.append("contract: UV2 kind or water out of range")
    code = UV[7, :, :, 1]
    if (code != np.round(code)).any() or (code != code[:, :1]).any():
        fails.append("contract: UV7's code not one whole number a triangle")
    c = code[:, 0].astype(int)
    sl, mask, ch = c % 8, (c // 8) % 8, c // 64
    for t in range(len(c)):
        k = int(kinds[t, 0])
        ok = (k == 1 and sl[t] == 7) or (k == 2 and 0 <= sl[t] <= 3) or (k in (0, 3) and 4 <= sl[t] <= 5)
        if not ok:
            fails.append(f"contract: triangle {t} kind {k} slice {sl[t]}")
            break
    if m["level"] == 0 and (mask != 0).any():
        fails.append("contract: L0 with a mask")
    if m["level"] == 0 and (ch != o["chamferMm"]).any():
        fails.append("contract: L0's chamfer not the stone's")
    if (ch < 0).any() or (ch > o["chamferMm"]).any():
        fails.append("contract: a chamfer out of range")
    if (np.abs(UV[1] - UV[1][0, 0]) > 0).any():
        fails.append("contract: UV1 not one value a stone")
    if (np.abs(UV[3, :, :, 1] - 1.0) > 0).any() or (UV[5] != 0).any():
        fails.append("contract: UV3's ground or UV5 not as the contract")
    # UV0 metric: metres in the face's own plane, so an edge's UV0 length is its length in the plane (the triangle's
    # corners projected onto it: collapse may have moved a corner off it by up to COLLAPSE_MM, which moves nothing in
    # the plane); the top's, metres in plan, its length in plan
    worst = 0.0
    V, T = m["V"], m["T"]
    for t in range(len(T)):
        pl = m["plane"][t]
        plan = o["faces"][m["face"][t]]["plan"]
        P3 = V[T[t]] if plan else V[T[t]] - np.outer(V[T[t]] @ pl["n"] - pl["d"], pl["n"])
        U = UV[0, t]
        for i in range(3):
            j = (i + 1) % 3
            e = P3[j] - P3[i]
            L3 = float(np.linalg.norm(e[:2] if plan else e))
            L2 = float(np.linalg.norm(U[j] - U[i]))
            if L3 > 1e-6:
                worst = max(worst, abs(L2 - L3) / L3)
    if worst > 1e-6:
        fails.append(f"contract: UV0 not metric ({worst:.2e})")
    # L0's edge distances: corner i's own slot its height over the opposite edge, the others 0
    if m["level"] == 0:
        e = m["edge"]
        for t in range(len(T)):
            alt = altitudes(V[T[t]])
            if not np.allclose(np.diag(e[t]), alt, atol=1e-9) or np.abs(e[t] - np.diag(np.diag(e[t]))).max() > 0:
                fails.append(f"contract: L0 edge distances wrong on triangle {t}")
                break
    return dict(masked=int(((code[:, 0].astype(int) // 8) % 8 > 0).sum()), fails=fails)


def block_checks(o):
    """The unworn block's own faces (before chamfers, chips trimmed in): convex, no sliver (SN9: a face under 50 mm or
    25 degrees; chamfers are thin by design and the wear's facets are governed by the thin-triangle gate, so neither
    is a sliver here), no rake (the top and the bed level, SN9)."""
    fails = []
    planes = [p for p in o["block"] + o["chips"] if p["role"] in ("exposed", "hidden")]
    faces = B.polyhedron(planes)
    out = []
    for p, poly in faces:
        if p["role"] != "exposed":
            continue
        w, ang = min_width(poly, p["n"]), min_angle(poly, p["n"])
        out.append(dict(face=p["name"], widthMm=round(w * 1000, 1), angleDeg=round(ang, 1)))
        if w * 1000 < SN9["sliverMm"] - 1e-6 or ang < SN9["sliverDeg"] - 1e-6:
            fails.append(f"sliver: {p['name']} {w * 1000:.1f} mm, {ang:.1f} degrees")
    top = next(p for p in o["block"] if p["name"] == "top")
    bed = next(p for p in o["block"] if p["name"] == "bed")
    rake = not (np.array_equal(top["n"], [0.0, 0.0, 1.0]) and np.array_equal(bed["n"], [0.0, 0.0, -1.0]))
    if rake:
        fails.append("rake: the top or the bed is not level")
    # convex: every vertex of the block inside every half-space
    allv = np.concatenate([poly for _p, poly in faces])
    worst = max(float((allv @ p["n"] - p["d"]).max()) for p in planes)
    if worst > 1e-9:
        fails.append(f"convexity: the block's vertex {worst:.2e} m outside a face")
    return dict(faces=out, rake=rake, fails=fails)


def min_width(poly, n):
    """A convex polygon's least width (its narrowest caliper)."""
    e1, e2 = B.basis(n)
    P2 = np.stack([poly @ e1, poly @ e2], -1)
    best = np.inf
    for i in range(len(P2)):
        a, b = P2[i], P2[(i + 1) % len(P2)]
        d = b - a
        if np.linalg.norm(d) < 1e-12:
            continue
        nn = np.array([-d[1], d[0]]) / np.linalg.norm(d)
        best = min(best, float(np.max(np.abs((P2 - a) @ nn))))
    return best


def min_angle(poly, n):
    out = 180.0
    k = len(poly)
    for i in range(k):
        a, b, c = poly[i - 1], poly[i], poly[(i + 1) % k]
        u, v = B.unit(a - b), B.unit(c - b)
        out = min(out, math.degrees(math.acos(float(np.clip(u @ v, -1.0, 1.0)))))
    return out


def wear_checks(o, m, tol):
    """The drawn top against wear.py's field: at points 2 mm apart over the top as the level draws it, the height of
    its triangles against the block's top less the law's depth; the largest difference against the level's share."""
    fails = []
    if m["grid"] is None:
        return dict(maxErrorMm=0.0, fails=fails)
    V, T = m["V"], m["T"]
    tops = [t for t in range(len(T)) if m["face"][t] == "top"]
    X, Y = np.meshgrid(np.arange(0.0, o["L"] + 1e-9, 0.002), np.arange(0.0, o["y_end"] + 1e-9, 0.002))
    X, Y = X.ravel(), Y.ravel()
    Z = np.full(len(X), np.nan)
    for t in tops:
        a, b, c = V[T[t]]
        det = (b[0] - a[0]) * (c[1] - a[1]) - (c[0] - a[0]) * (b[1] - a[1])
        if abs(det) < 1e-18:
            continue
        l1 = ((X - a[0]) * (c[1] - a[1]) - (c[0] - a[0]) * (Y - a[1])) / det
        l2 = ((b[0] - a[0]) * (Y - a[1]) - (X - a[0]) * (b[1] - a[1])) / det
        inside = (l1 >= -1e-9) & (l2 >= -1e-9) & (l1 + l2 <= 1 + 1e-9)
        Z[inside] = a[2] + l1[inside] * (b[2] - a[2]) + l2[inside] * (c[2] - a[2])
    on = ~np.isnan(Z)
    rows = m["grid"]["rows"]
    true = np.asarray(o["wear"].depth(X[on], Y[on]), float)
    err = np.abs((o["H"] - Z[on]) - true)
    worst = float(err.max()) if len(err) else 0.0
    if worst > tol * 1.0001:
        fails.append(f"wear: the drawn top misses wear.py's field by {worst * 1000:.3f} mm (its share "
                     f"{tol * 1000:g} mm)")
    return dict(maxErrorMm=round(worst * 1000, 3), toleranceMm=round(tol * 1000, 3), samples=int(on.sum()),
                rows=[round(y * 1000) for y in rows], columns=[round(x * 1000) for x in m["grid"]["cols"]],
                fails=fails)


def l1_vs_l0(o, L0, L1, limit_mm):
    """L1 against L0: every L1 face on one of L0's planes or the wear's (none of the chamfers'), and the two-sided
    distance between the surfaces, sampled every 2 mm, against L1's error."""
    fails = []
    ch_names = {p["name"] for p, _s, _a in o["chamfers"]}
    on_chamfer = sorted({L1["plane"][t]["name"] for t in range(len(L1["T"])) if L1["plane"][t]["name"] in ch_names})
    if on_chamfer:
        fails.append(f"L1 on a chamfer's plane: {on_chamfer}")
    P1, _ = B.sample_tris(L1["V"], L1["T"], 0.002)
    P0, _ = B.sample_tris(L0["V"], L0["T"], 0.002)
    reach = 2 * limit_mm / 1000.0                      # exact to twice the limit; farther is a fail anyway
    d10 = B.surface_distance(P1, L0["V"], L0["T"], reach)
    d01 = B.surface_distance(P0, L1["V"], L1["T"], reach)
    a, b = float(d10.max()) * 1000, float(d01.max()) * 1000
    sag = max(s for _p, s, _a in o["chamfers"]) * 1000 if o["chamfers"] else 0.0
    if max(a, b) > limit_mm + 1e-6:
        fails.append(f"L1 against L0: {max(a, b):.2f} mm over L1's {limit_mm} mm")
    return dict(l1ToL0Mm=round(a, 2), l0ToL1Mm=round(b, 2), chamferSagittaMm=round(sag, 2), limitMm=limit_mm,
                fails=fails)


# -- the machinery's variants (shown on the sheet, checked, not exported) -------------------------------------------

def variants(facts):
    """The machinery on inputs the specimen does not exercise: an open end (facets and a seeded chip), a stone walled
    at both ends, a short stone off the walking line, and the specimen without its broken corner."""
    out = {}
    v = json.loads(json.dumps(facts))
    v["id"] = facts["id"] + "~open"
    v["ends"] = dict(l=dict(kind="open"), r=dict(kind="walled"))
    v["corner"] = None
    out["open end"] = v
    v = json.loads(json.dumps(facts))
    v["id"] = facts["id"] + "~walled"
    v["ends"] = dict(l=dict(kind="walled"), r=dict(kind="walled"))
    v["corner"] = None
    out["walled both"] = v
    v = json.loads(json.dumps(facts))
    v["id"] = facts["id"] + "~short"
    v["lengthMm"] = 700
    v["wear"]["leftMm"] = facts["wear"]["widthMm"] // 2 - 700 + 156
    v["ends"] = dict(l=dict(kind="joint", jointMm=8), r=dict(kind="walled"))
    v["corner"] = None
    out["short"] = v
    v = json.loads(json.dumps(facts))
    v["id"] = facts["id"]
    v["corner"] = None
    out["no corner"] = v
    return out


def _extremes(items, size):
    """The items at the least and the greatest of each of a cell's two sizes, the lowest id on a tie."""
    out = {}
    for k, name in ((0, "length"), (1, "height")):
        out[f"least {name}"] = min(items, key=lambda t: (size(t)[k], t[1]["id"]))
        out[f"greatest {name}"] = min(items, key=lambda t: (-size(t)[k], t[1]["id"]))
    return out


def wall_variants(part, data):
    """The machinery on inputs the specimen does not exercise, each (facts, the definition's params it is built with):
    R1's own stones at the pool's extremes (the least and the greatest cell length and height); for the wall stone,
    the specimen broken once (two facets) and with its bed's arris chamfered (the arm of R2a's A/B: SN4 against SN7
    and SN8); for the coping, the specimen with both its ends open (its corners knocked, every one), with both
    joints, and with every arris chamfered (the arm: the bed's, the ends' upright ones and the knocks')."""
    out = {}
    if part == "wallstone":
        facts, _rule = specimen_wallstone(data)
        pool = face_pool(data)
        for name, (w, s, face, sides) in _extremes(pool, lambda t: _cell(t[1])).items():
            out[name] = (wallstone_facts(data, w, s, face, sides), {})
        out["two facets"] = (dict(facts), {"faceFacets": [[2, 1]]})
        out["bed chamfered (the arm)"] = (dict(facts), {"bedChamfer": True})
        return out
    facts, _rule = specimen_coping(data)
    pool = [(w, s) for w, s in coping_pool(data)
            if s.get("panel") in {p["id"] for p in w["panels"] if p["work"] == "built"}]
    for name, (w, s) in _extremes(pool, lambda t: _cell(t[1])).items():
        out[name] = (coping_facts(data, w, s), {})
    v = json.loads(json.dumps(facts))
    v["id"] = facts["id"] + "~open"
    v["ends"] = dict(l="open", r="open")
    out["both open"] = (v, {"chipPerMille": 1000})
    v = json.loads(json.dumps(facts))
    v["id"] = facts["id"] + "~joints"
    v["ends"] = dict(l="joint", r="joint")
    out["both joints"] = (v, {})
    out["every arris chamfered (the arm)"] = (dict(facts), {"bedChamfer": True, "uprightChamfer": True,
                                                            "chipChamfer": True})
    return out


def with_params(defn, params):
    """The definition with some params' values set (a variant's: the machinery on inputs the specimen does not take)."""
    if not params:
        return defn
    d = json.loads(json.dumps(defn))
    for k, v in params.items():
        d.setdefault("params", {})[k] = dict(value=v, note="a variant's (stones.py: wall_variants)")
    return d


def summary(res):
    th = res["thin"]
    lines = [f"triangles L0 {res['triangles']['L0']} / {res['triangles']['budget'][0]}, "
             f"L1 {res['triangles']['L1']} / {res['triangles']['budget'][1]} (L1/L0 {res['triangles']['ratio']}, "
             f"{'within' if res['triangles']['ratioWithin'] else 'over'} 60%: the kind's, held over the pools); "
             f"vertices L0 {res['triangles']['vertices']['L0']}, L1 {res['triangles']['vertices']['L1']} of its own "
             f"(identical in every channel {res['triangles']['indexedVertices']['L0']} and "
             f"{res['triangles']['indexedVertices']['L1']}; the FBX's {res['triangles']['fbxVertices']['L0']} and "
             f"{res['triangles']['fbxVertices']['L1']})"]
    for lvl in ("L0", "L1"):
        for vn, r in th[lvl].items():
            verdict = ("(the level's view) " if vn in GATED_VIEWS else "(reported) ") + ("within" if r["ok"] else
                                                                                      "over")
            lines.append(f"  {lvl} {vn}: front {r['front']}, under 2 px {r['thin']} ({100 * r['thinShare']:.1f}%), "
                         f"median {r['medianAreaPx']} px, altitude {r['medianAltitudePx']} px {verdict}"
                         f" {r['thinFaces'] if r['thin'] else ''}")
    sk = res.get("skirts")
    if sk:
        lines.append(f"skirts: {sk['skirtMm']:g} mm; under the next step needs {sk.get('coverNeedMm')}, the bed needs "
                     f"{sk['bedNeedMm']} (worn {sk['wornUnderFootMm']} under the foot)")
    lines.append(f"L1 vs L0: L1->L0 {res['l1VsL0']['l1ToL0Mm']} mm, L0->L1 {res['l1VsL0']['l0ToL1Mm']} mm, "
                 f"sagitta {res['l1VsL0']['chamferSagittaMm']} mm, limit {res['l1VsL0']['limitMm']}")
    for lvl in ("L0", "L1"):
        w = res["wear"][lvl]
        if "rows" in w:
            lines.append(f"wear {lvl}: error {w['maxErrorMm']} mm (share {w.get('toleranceMm')}), rows "
                         f"{w.get('rows')}, {len(w.get('columns', []))} columns")
    lines.append(f"chamfer: square on {res['chamferPx']['squareOnPx']} px, its leg face-on "
                 f"{res['chamferPx']['legFaceOnPx']} px at 8 m; ok {res['chamferPx']['ok']}")
    for lvl in ("L0", "L1"):
        r = res[lvl]
        lines.append(f"{lvl}: planar {r['planarMm']} mm, outside {r['outsideBlockMm']} mm, T {r['tJunctions']}, open "
                     f"{r['openEdges']} on {r['openEdgesOn']}, smallest altitude {r['smallestAltitudeMm']} mm, "
                     f"masked {r['contract']['masked']}")
    lines.append("block faces: " + ", ".join(f"{f['face']} {f['widthMm']} mm {f['angleDeg']} deg"
                                             for f in res["block"]["faces"]))
    fc = res["facts"]
    if "lapMm" in fc:
        lines.append(f"facts: lap {fc['lapMm']} mm in {fc['lapRangeMm']}, joints {fc['jointsMm']} mm in "
                     f"{fc['jointRangeMm']}")
    else:
        lines.append("facts: " + ", ".join(f"{k} {v}" for k, v in fc.items() if k != "fails"))
    fm = res.get("form", {})
    if len(fm) > 1:
        lines.append("form: " + ", ".join(f"{k} {v}" for k, v in fm.items() if k != "fails"))
    lines.append(f"deterministic {res['deterministic']}")
    lines.append("FAILS: " + ("; ".join(res["fails"]) if res["fails"] else "none"))
    return "\n".join(lines)


# -- the pools: every stone a part makes in the gully, SN8's share over them -----------------------------------------

FLIGHT = "reviews/lt1/port/2b/r2a/stones/flight-check.json"
POOLS = {"step": FLIGHT, "wallstone": "reviews/lt1/port/2b/r2a/stones/walls-check.json",
         "coping": "reviews/lt1/port/2b/r2a/stones/copings-check.json"}
POOL_RULES = {
    "step": "SN8's share over a level: every stone of every flight's ordinary steps, as R1 laid them (masonry.lay at "
            "the pinned commit), each at its level's far edge (L0 8 m, L1 20 m) in the judging view (face-on, 20 "
            "degrees of top), its front-facing triangles pooled; every other check on each stone",
    "wallstone": "SN8's share over a level: every face stone the part makes (face_pool: in a panel as built, a face or "
                 "through stone against all four sides of its cell on its face), as R1 laid them (masonry.lay at the "
                 "pinned commit), each at its level's far edge (L0 8 m, L1 20 m) in the judging view (face-on to its "
                 "face, 20 degrees of top), its front-facing triangles pooled; every other check on each stone",
    "coping": "SN8's share over a level: every coping of a panel as built, as R1 laid them (masonry.lay at the pinned "
              "commit), each at its level's far edge (L0 8 m, L1 20 m) in the judging view (face-on to its stair "
              "side, 20 degrees of top), its front-facing triangles pooled; every other check on each stone",
}
SHARE_RULE = ("SN8 sets its 10% over a level's front-facing triangles at its far edge, the fills included: the gully's "
              "whole level (walls, copings, fills and steps), which R2b lays and R3 measures. This part's stones alone "
              "are reported here against it; the export holds the gully's pieces pooled over every part's pool "
              "(level_gate), and every stone's other checks (ok)")
LEVEL_RATIO = 0.6       # building-blocks.md: each kind's export check, each level at most 60% of the one before
KINDS = {"step": "stair", "wallstone": "walls", "coping": "walls"}     # the kind (kinds/) each part's stones are of
KIND_FILES = {"step": "kinds/stair.json", "wallstone": "kinds/wall.json", "coping": "kinds/wall.json"}  # and its file
LEVEL_RULE = ("SN8's share over the gully's pieces as R1 laid them: every part's pool (the steps, the wall face stones, "
              "the copings), each stone at each level's far edge in the judging view, its front-facing triangles "
              "pooled: at most 10% under 2 px, and each pool's median visible triangle at least 10 px (the fills, eight "
              "large triangles a panel, are not built here and would only lower the share). Each kind's L1 at most 60% "
              "of its L0 over its pools (building-blocks.md: the stair kind the steps, the walls kind the wall stones "
              "and copings). A piece's own share and ratio are reported, never held: a coping's L0 has about a dozen "
              "front-facing triangles, so one triangle moves its share by about nine points")
_WORKER = {}


def _worker_data(commit):
    """One Data a process for a commit, so a pool's worker lays R1's walls once, not once a stone (its notes are the
    pool's, never a sidecar's)."""
    if commit not in _WORKER:
        _WORKER.clear()
        _WORKER[commit] = Data(commit)
    return _WORKER[commit]


def pool_jobs(part, data):
    if part == "step":
        return [(data.commit, part, (fid, sid, st["id"])) for fid, sid, _idx, st in flight_stones(data)]
    if part == "wallstone":
        return [(data.commit, part, (w["id"], s["id"])) for w, s, _f, _sd in face_pool(data)]
    return [(data.commit, part, (w["id"], s["id"])) for w, s in coping_pool(data)
            if s.get("panel") in {p["id"] for p in w["panels"] if p["work"] == "built"}]


def _pool_facts(part, data, key):
    if part == "step":
        fid, sid, stone_id = key
        fl = next(f for f in data.laying()["steps"] if f["id"] == fid)
        stone = next(s for s in fl["stones"] if s["id"] == stone_id)
        facts, _laid = step_facts(data, fid, sid, stone)
        return facts, dict(id=stone_id, flight=fid, step=sid, lengthMm=facts["lengthMm"], riseMm=facts["riseMm"])
    wid, stone_id = key
    w = next(w for w in data.laying()["walls"] if w["id"] == wid)
    s = next(s for s in w["stones"] if s["id"] == stone_id)
    if part == "wallstone":
        face = s["faces"][0]
        facts = wallstone_facts(data, w, s, face, wall_sides(w, s, face))
    else:
        facts = coping_facts(data, w, s)
    return facts, dict(id=stone_id, wall=wid, cellMm=facts["cellMm"])


def _flight_one(job):
    """One stone of a pool (a worker's): its facts from R1's laying, built and checked (every check but SN8's share,
    which is the pool's), and its front-facing triangles' sizes in the judging view at each level's edge."""
    commit, part, key = job
    data = _worker_data(commit)
    defn = definition(part)
    facts, head_row = _pool_facts(part, data, key)
    try:
        out = build(part, facts, defn, data)
    except Failed as e:                 # a stone the part cannot make is the pool's failure, named, not its end
        return dict(head_row, fails=[f"build: {e}"]), None
    res = check(part, out, defn)
    o = out["outline"]
    if part == "step":
        fid, sid, _sid = key
        row = dict(head_row, index=data.plan["steps"][sid]["index"], lapMm=facts["lapMm"],
                   jointsMm=res["facts"]["jointsMm"], leftMm=facts["wear"]["leftMm"],
                   ends=[facts["ends"]["l"]["kind"], facts["ends"]["r"]["kind"]],
                   corner=facts["corner"] is not None, riserFacets=o["riserFacets"])
        row = {k: row[k] for k in ("id", "flight", "step", "index", "lengthMm", "riseMm", "lapMm", "jointsMm",
                                   "leftMm", "ends", "corner", "riserFacets")}
    elif part == "wallstone":
        sm = o["summary"]
        row = dict(head_row, face=facts["face"], drawnMm=[sm["lengthMm"], sm["heightMm"]], setInMm=sm["setInMm"],
                   faceFacets=sm["faceFacets"], ridgeProudMm=sm["ridgeProudMm"], short=res["facts"]["short"],
                   withinDrawn=res["facts"]["withinDrawn"])
    else:
        sm = o["summary"]
        row = dict(head_row, drawnMm=[sm["lengthMm"], sm["thicknessMm"]], ends=[facts["ends"]["l"], facts["ends"]["r"]],
                   proudMm=sm["proudMm"]["front"], chips=[c["name"] for c in sm["chips"]], short=res["facts"]["short"])
    row.update(triangles=[len(out["L0"]["T"]), len(out["L1"]["T"])],
               vertices=[len(out["L0"]["V"]), len(out["L1"]["V"])],
               indexedVertices=[res["triangles"]["indexedVertices"]["L0"], res["triangles"]["indexedVertices"]["L1"]],
               smallestAltitudeMm=[res["L0"]["smallestAltitudeMm"], res["L1"]["smallestAltitudeMm"]],
               l1VsL0Mm=max(res["l1VsL0"]["l1ToL0Mm"], res["l1VsL0"]["l0ToL1Mm"]))
    if part == "step":
        row["wearErrorMm"] = [res["wear"]["L0"]["maxErrorMm"], res["wear"]["L1"]["maxErrorMm"]]
    row["fails"] = res["fails"]
    sizes = {}
    for name, m, dist in (("L0", out["L0"], GATE["l0Distance"]), ("L1", out["L1"], GATE["l1Distance"])):
        r = thin_gate(m, views(o, dist)[GATED_VIEWS[0]], keep=True)
        row[name] = {k: r[k] for k in ("front", "thin", "thinShare", "medianAreaPx", "thinFaces")}
        sizes[name] = (r["altitudesPx"], r["areasPx"])
    return row, sizes


def flight_check(data, workers=None, part="step"):
    """Every stone a part makes in the gully (the step: every flight's ordinary steps, both stones of each; the wall
    stone: face_pool's; the coping: every coping of a panel as built; all as R1 laid them), each built and put
    through every check; and SN8's share over their front-facing triangles, each at its level's far edge in the
    judging set's view (face-on, 20 degrees of top), pooled. A worker per core the timing run leaves (one while L5
    times). Writes the part's POOLS file; returns its dict: ok when no stone fails a check; shareOk when the pool's
    share and median pass at both levels (SN8 sets the share over the gully's whole level, which the part's stones
    are a part of, so it is reported, not held: shareRule)."""
    import multiprocessing as mp
    code = code_ids(part)      # the code the stones are built by, read before they are (an edit during the run shows)
    jobs = pool_jobs(part, data)
    if workers is None:
        workers = 1 if timing_running() else max(1, min(6, (os.cpu_count() or 2) - 2))
    if workers > 1:
        with mp.get_context("spawn").Pool(workers) as pool:
            results = pool.map(_flight_one, jobs, chunksize=max(1, len(jobs) // (8 * workers)))
    else:
        results = [_flight_one(j) for j in jobs]
    rows = [r for r, sz in results if sz is not None]
    unbuilt = [r for r, sz in results if sz is None]
    pooled, fails, share_fails = {}, [f"{r['id']}: {f}" for r in unbuilt for f in r["fails"]], []
    for lvl in ("L0", "L1"):
        alt = np.concatenate([np.asarray(sz[lvl][0], float) for _r, sz in results if sz is not None])
        area = np.concatenate([np.asarray(sz[lvl][1], float) for _r, sz in results if sz is not None])
        thin = alt < GATE["thinPx"]
        shares = np.array([r[lvl]["thinShare"] for r in rows])
        pooled[lvl] = dict(stones=len(rows), front=int(len(alt)), thin=int(thin.sum()),
                           thinShare=round(float(thin.mean()), 4), medianAreaPx=round(float(np.median(area)), 1),
                           medianAltitudePx=round(float(np.median(alt)), 2),
                           perStone=dict(min=round(float(shares.min()), 4), median=round(float(np.median(shares)), 4),
                                         max=round(float(shares.max()), 4),
                                         over=int((shares > GATE["thinShare"]).sum())),
                           worst=[dict(id=r["id"], share=r[lvl]["thinShare"], thin=r[lvl]["thin"],
                                       front=r[lvl]["front"], faces=r[lvl]["thinFaces"])
                                  for r in sorted(rows, key=lambda r: (-r[lvl]["thinShare"], r["id"]))[:5]])
        pooled[lvl]["ok"] = bool(thin.mean() <= GATE["thinShare"] and np.median(area) >= GATE["medianAreaPx"])
        if not pooled[lvl]["ok"]:
            share_fails.append(f"pool {lvl}: {pooled[lvl]['thin']} of {pooled[lvl]['front']} under 2 px "
                               f"({100 * pooled[lvl]['thinShare']:.1f}%), median {pooled[lvl]['medianAreaPx']} px")
    for r in rows:
        fails += [f"{r['id']}: {f}" for f in r["fails"]]
    tri = np.array([r["triangles"] for r in rows])
    ver = np.array([r["vertices"] for r in rows])
    ind = np.array([r["indexedVertices"] for r in rows])
    head = dict(part=part) if part != "step" else {}
    res = _jsonable(dict(
        **head,
        rule=POOL_RULES[part],
        commit=data.commit, pinned=pinned_ids(data.commit), code=code, view=GATED_VIEWS[0], gate=GATE, pooled=pooled,
        triangles=dict(L0=dict(min=int(tri[:, 0].min()), median=float(np.median(tri[:, 0])), max=int(tri[:, 0].max())),
                       L1=dict(min=int(tri[:, 1].min()), median=float(np.median(tri[:, 1])), max=int(tri[:, 1].max())),
                       total=[int(tri[:, 0].sum()), int(tri[:, 1].sum())]),
        vertices=dict(L0=dict(min=int(ver[:, 0].min()), median=float(np.median(ver[:, 0])), max=int(ver[:, 0].max())),
                      L1=dict(min=int(ver[:, 1].min()), median=float(np.median(ver[:, 1])), max=int(ver[:, 1].max())),
                      total=[int(ver[:, 0].sum()), int(ver[:, 1].sum())],
                      indexedTotal=[int(ind[:, 0].sum()), int(ind[:, 1].sum())],
                      fbxTotal=[3 * int(tri[:, 0].sum()), 3 * int(tri[:, 1].sum())],
                      note="total: the part's own vertices (positions, shared where one); indexedTotal: corners "
                           "identical in every channel counted once (what an exact indexed mesh needs under the "
                           "contract); fbxTotal: the FBX route's, three a triangle"),
        smallestAltitudeMm=[min(r["smallestAltitudeMm"][0] for r in rows), min(r["smallestAltitudeMm"][1] for r in rows)],
        fails=fails, ok=not fails, shareFails=share_fails, shareOk=not share_fails,
        shareRule=SHARE_RULE.replace("This part's stones", "The steps") if part == "step" else SHARE_RULE,
        unbuilt=unbuilt, stones=rows))
    with open(os.path.join(ROOT, POOLS[part]), "w") as f:
        json.dump(res, f, indent=1, sort_keys=False)
        f.write("\n")
    return res


def flight_current(part="step"):
    """The pool's result on disk, if its code is the checkout's: (result or None, why not)."""
    rel = POOLS[part]
    path = os.path.join(ROOT, rel)
    if not os.path.exists(path):
        return None, f"no {rel}: run `stones.py flight {part}`"
    with open(path) as f:
        res = json.load(f)
    if res.get("code") != code_ids(part):
        return None, f"{rel} was run with other code or data: run `stones.py flight {part}` again"
    if res.get("pinned") != pinned_ids(Data().commit):
        return None, f"{rel} read R1's files as {res.get('commit', '?')[:7]} held them, and HEAD's differ: run " \
                     f"`stones.py flight {part}` again"
    return res, None


def flight_summary(res):
    lines = []
    what = res.get("part", "step")
    for lvl in ("L0", "L1"):
        p = res["pooled"][lvl]
        lines.append(f"pool {what} {lvl}: {p['stones']} stones, {p['thin']} of {p['front']} under 2 px "
                     f"({100 * p['thinShare']:.1f}%), median {p['medianAreaPx']} px, altitude {p['medianAltitudePx']} "
                     f"px, {'within' if p['ok'] else 'over'} SN8's share; per stone {100 * p['perStone']['min']:.1f} to "
                     f"{100 * p['perStone']['max']:.1f}% (median {100 * p['perStone']['median']:.1f}%, "
                     f"{p['perStone']['over']} over 10%)")
    lines.append(f"pool triangles: L0 {res['triangles']['L0']}, L1 {res['triangles']['L1']}; smallest altitude "
                 f"{res['smallestAltitudeMm']} mm")
    if "vertices" in res:
        lines.append(f"pool vertices: L0 {res['vertices']['L0']}, L1 {res['vertices']['L1']}; in all "
                     f"{res['vertices']['total']} of their own (identical in every channel "
                     f"{res['vertices'].get('indexedTotal')}; the FBX route's {res['vertices']['fbxTotal']})")
    lines.append(f"pool, the {what} stones alone against SN8's share (the level's, R2b and R3): " +
                 ("; ".join(res["shareFails"]) if res["shareFails"] else "within"))
    lines.append("pool FAILS (every stone's checks): " + ("; ".join(res["fails"][:40]) if res["fails"] else "none") +
                 (f" ... ({len(res['fails'])} in all)" if len(res["fails"]) > 40 else ""))
    return "\n".join(lines)


def level_gate():
    """The checks that are a level's or a kind's, not a piece's (LEVEL_RULE), over every part's pool as it stands on
    disk. Returns (result, None), or (None, why) when a pool is missing or was run with other code or data."""
    pools = {}
    for part in PARTS:
        fr, why = flight_current(part)
        if fr is None:
            return None, why
        pools[part] = fr
    fails, share, kinds = [], {}, {}
    for lvl in ("L0", "L1"):
        front = sum(p["pooled"][lvl]["front"] for p in pools.values())
        thin = sum(p["pooled"][lvl]["thin"] for p in pools.values())
        med = {part: p["pooled"][lvl]["medianAreaPx"] for part, p in pools.items()}
        ok = thin <= GATE["thinShare"] * front and all(m >= GATE["medianAreaPx"] for m in med.values())
        share[lvl] = dict(front=front, thin=thin, thinShare=round(thin / front, 4), medianAreaPx=med,
                          byPart={part: dict(thin=p["pooled"][lvl]["thin"], front=p["pooled"][lvl]["front"],
                                             thinShare=p["pooled"][lvl]["thinShare"]) for part, p in pools.items()},
                          ok=bool(ok))
        if not ok:
            fails.append(f"SN8 over the gully's pieces, {lvl}: {thin} of {front} under 2 px "
                         f"({100 * thin / front:.1f}%), medians {med} px")
    for part, p in pools.items():
        k = kinds.setdefault(KINDS[part], dict(parts=[], stones=0, triangles=[0, 0]))
        k["parts"].append(part)
        k["stones"] += len(p["stones"])
        k["triangles"] = [k["triangles"][0] + p["triangles"]["total"][0], k["triangles"][1] + p["triangles"]["total"][1]]
    for name, k in sorted(kinds.items()):
        k["ratio"] = round(k["triangles"][1] / k["triangles"][0], 4)
        k["ok"] = bool(k["triangles"][1] <= LEVEL_RATIO * k["triangles"][0])
        if not k["ok"]:
            fails.append(f"levels: the {name} kind's L1 {k['triangles'][1]} over 60% of its L0 {k['triangles'][0]}")
    return _jsonable(dict(rule=LEVEL_RULE, share=share, kinds=kinds,
                          pools={part: dict(file=POOLS[part], stones=len(p["stones"]), commit=p["commit"])
                                 for part, p in pools.items()}, fails=fails, ok=not fails)), None


def level_summary(lv):
    lines = []
    for lvl in ("L0", "L1"):
        sh = lv["share"][lvl]
        by = ", ".join(f"{part} {b['thin']} of {b['front']} ({100 * b['thinShare']:.1f}%)" for part, b in sh["byPart"].items())
        lines.append(f"level {lvl}, the gully's pieces pooled: {sh['thin']} of {sh['front']} under 2 px "
                     f"({100 * sh['thinShare']:.1f}%; {by}), medians {sh['medianAreaPx']} px: "
                     f"{'within' if sh['ok'] else 'OVER'}")
    for name, k in sorted(lv["kinds"].items()):
        lines.append(f"kind {name} ({', '.join(k['parts'])}; {k['stones']} stones): L1/L0 {k['triangles'][1]} / "
                     f"{k['triangles'][0]} = {k['ratio']}: {'within' if k['ok'] else 'OVER'} 60%")
    return "\n".join(lines)


# -- the export (inside Blender) -------------------------------------------------------------------------------------

# The eight UV layers by name (the contract's table, plan.md): the FBX carries them in this order, Unity reads them as
# TexCoord0 to 7.
UV_LAYERS = ("uv0 face metres", "uv1 years seed", "uv2 kind water", "uv3 sky ground", "uv4 polish lichen",
             "uv5 moss water", "uv6 d0 d1", "uv7 d2 code")
FRAME = ("the stone's frame: x along it from its left end as the street sees it, y back from its front, z up from its "
         "bed (Blender); exported forward +Z, up +Y with the space transform baked (stone.py's _export_fbx), so Unity's "
         "mesh holds x along, y up, z back with no turn on its object")
FRAMES = {
    "step": FRAME,
    "wallstone": ("the stone's frame: x along its face from its left end as one looking at that face sees it, y back "
                  "from its face (the bed's front edge on the wall's plane), z up from its bed (Blender); placed by a "
                  "turn about z, never a mirror (its facts' alongS: +1 where x runs up the wall line); exported forward "
                  "+Z, up +Y with the space transform baked (stone.py's _export_fbx), so Unity's mesh holds x along, y "
                  "up, z back with no turn on its object"),
    "coping": ("the stone's frame: x along it from its left end as the stair sees it, y back from its stair side "
               "(its front) across the wall, z up from its bed (Blender); placed by a turn about z, never a mirror "
               "(its facts' alongS); exported forward +Z, up +Y with the space transform baked (stone.py's "
               "_export_fbx), so Unity's mesh holds x along, y up, z back with no turn on its object"),
}


def _jsonable(v):
    if isinstance(v, dict):
        return {str(k): _jsonable(x) for k, x in v.items()}
    if isinstance(v, (list, tuple)):
        return [_jsonable(x) for x in v]
    if isinstance(v, np.ndarray):
        return _jsonable(v.tolist())
    if isinstance(v, (np.integer,)):
        return int(v)
    if isinstance(v, (np.floating,)):
        return float(v)
    if isinstance(v, (np.bool_,)):
        return bool(v)
    return v


def blob(rel, commit=None):
    """A file's content id (git's blob hash): the same for the same bytes at any commit, so a sidecar names its inputs
    without changing when nothing it read did. With a commit, the file as that commit holds it; without, the checkout's."""
    if commit:
        cmd = ["git", "-C", ROOT, "rev-parse", f"{commit}:{rel}"]
    else:
        cmd = ["git", "-C", ROOT, "hash-object", os.path.join(ROOT, rel)]
    return subprocess.run(cmd, capture_output=True, text=True, check=True).stdout.strip()[:12]


PINNED = ("blender/generators/masonry.py", "kinds/wall.json", f"{PACK}/walling.json", R1_FACTS)


def pinned_ids(commit):
    """The content ids of the files Data reads at its pinned commit (R1's), as that commit holds them."""
    return {rel: blob(rel, commit) for rel in PINNED}


def code_ids(part="step"):
    """The content ids of the code a part's stones are built by and of the data Data reads from the checkout for it
    (its definition among them; what it reads at the pinned commit is named by the commit), so a result on disk is
    current only while none of them has changed."""
    common = ("blender/parts/stone/slate/stones.py", "blender/parts/stone/slate/block.py", "blender/generators/wear.py",
              "blender/resolver/hashing.py", f"{PACK}/parts/stone/{part}.json", f"{PACK}/pack.json")
    # the step reads the material its working names (the pinned commit's facts and table name it): every one the pack
    # has is named, so a change to any shows
    mats = tuple(sorted(f"{PACK}/materials/{f}" for f in os.listdir(os.path.join(ROOT, PACK, "materials"))
                        if f.endswith(".json")))
    own = {"step": mats + ("kinds/stair.json", "fixtures/records/st-gully.json", "fixtures/golden/stair/plan.json",
                           "fixtures/golden/stair/life.json")}.get(part, ())
    return {rel: blob(rel) for rel in common + own + ("blender/parts/stone/slate/patches.manifest.json",)}


def sidecar(part, out, res, rule, data, defn, flight=None, level=None):
    """The sidecar beside the FBX (Unity's readback, LT1R2a.Stone, reads it): the objects, the pivot and frame, each
    level's triangles and bounds, the chamfer and its form, the channels, the facts and the specimen's rule, the
    outline's numbers, the checks (the specimen's, and the pool's SN8 share over every stone the part makes in the
    gully), and where every input came from."""
    o = out["outline"]

    def bounds(m):
        U = np.stack([m["V"][:, 0], m["V"][:, 2], m["V"][:, 1]], -1)   # Unity's x, y, z
        return dict(minMm=[round(float(v) * 1000, 3) for v in U.min(axis=0)],
                    maxMm=[round(float(v) * 1000, 3) for v in U.max(axis=0)])

    th = res["thin"]
    if part == "step":
        note = (f"the pivot is the bed's front left corner; the drawn faces run {o['skirt'] * 1000:g} mm past a hidden "
                "face or a cover (the skirts), so the riser reaches below the bed (Unity's y) where the step below is "
                "worn, and the top runs back under the next step")
        shape = dict(lengthMm=o["facts"]["lengthMm"], riseMm=o["facts"].get("riseMm"), ends=o["ends"],
                     riserFacets=o["riserFacets"], riserFootMm=o["riserFootMm"], endFacets=o["endFacets"],
                     chips=[dict(name=c["name"], legsMm=c.get("legsMm"), fact=c.get("fact"), filled=c.get("filled"),
                                 sizeMm=c.get("sizeMm"), grownPerMille=c.get("grownPerMille"))
                            for c in o["chips"]],
                     chamfers=len(o["chamfers"]), skirtMm=o["skirt"] * 1000, lattice=o["lattice"],
                     rows0Mm=[round(y * 1000) for y in o["rows0"]], rows1Mm=[round(y * 1000) for y in o["rows1"]],
                     cols0=[[k, round(x * 1000)] for k, x in o["cols0"]],
                     cols1=[[k, round(x * 1000)] for k, x in o["cols1"]],
                     faces={f: dict(kind=fr["kind"], patch=fr["patch"], slice=fr["slice"], mode=fr["mode"],
                                    offsetMm=list(fr["offset"]), turnDeg=fr.get("turnDeg"))
                            for f, fr in sorted(o["faces"].items())})
    else:
        note, shape = o["boundsNote"], o["summary"]
    extra = {}
    if part == "step":
        extra = dict(wear={k: {kk: vv for kk, vv in w.items() if kk != "fails"} for k, w in res["wear"].items()})
    late = dict(skirts={k: v for k, v in res["skirts"].items() if k != "fails"}) if part == "step" else \
        dict(form={k: v for k, v in res["form"].items() if k != "fails"})
    return _jsonable(dict(
        part=part, id=o["facts"]["id"], tool=TOOL, definition=f"{PACK}/parts/stone/{part}.json",
        objects=dict(L0=f"{part}_L0", L1=f"{part}_L1"),
        pivot=defn["pivot"], frame=FRAMES[part],
        bounds=dict(L0=bounds(out["L0"]), L1=bounds(out["L1"]), note=note),
        levels={k: dict(triangles=len(out[k]["T"]), vertices=len(out[k]["V"]),
                        indexedVertices=res["triangles"]["indexedVertices"][k], fbxVertices=3 * len(out[k]["T"]),
                        errorMm=data.level_error(part, k.lower())) for k in ("L0", "L1")},
        vertices="vertices: the part's own mesh, its positions shared where corners are one; indexedVertices: its "
                 "corners identical in every channel (position, normal, all eight UVs) counted once, what an exact "
                 "indexed mesh such as step 5's chunks needs under the contract (the edge distances, UV6 and UV7, are "
                 "each triangle's own, so few corners are shared); fbxVertices: the FBX's, three a triangle, none "
                 "shared, since Unity's FBX import merges near-equal corners that share a control point (the FBX "
                 "route's alone)",
        chamferMm=o["chamferMm"], chamferMeasure=param(part, defn, "chamferMeasure"),
        chamferForm=dict(legPerMm=1, angleDeg=45, note="the code's mm is the leg kept along each face; an equal-legged "
                                                       "chamfer on a square arris"),
        channels=dict(zip([f"UV{c}" for c in range(8)], UV_LAYERS)),
        facts=o["facts"], rule=rule,
        outline=shape,
        checks=dict(fails=res["fails"], triangles=res["triangles"], l1VsL0=res["l1VsL0"],
                    **extra,
                    thin={lvl: {vn: {k: r[k] for k in ("front", "thin", "thinShare", "medianAreaPx",
                                                       "medianAltitudePx", "view", "ok")}
                                for vn, r in th[lvl].items()} for lvl in th},
                    gate=dict(views=list(GATED_VIEWS), **GATE),
                    chamferPx=dict(squareOnPx=res["chamferPx"]["squareOnPx"],
                                   legFaceOnPx=res["chamferPx"]["legFaceOnPx"], ok=res["chamferPx"]["ok"]),
                    **late,
                    mesh={lvl: {k: res[lvl][k] for k in ("planarMm", "outsideBlockMm", "tJunctions", "openEdges",
                                                          "smallestAltitudeMm")} for lvl in ("L0", "L1")},
                    deterministic=res["deterministic"],
                    facts={k: v for k, v in res["facts"].items() if k != "fails"},
                    flight=None if flight is None else dict(
                        file=POOLS[part], rule=flight["rule"], commit=flight["commit"], view=flight["view"],
                        pooled={lvl: {k: v for k, v in p.items() if k != "worst"}
                                for lvl, p in flight["pooled"].items()},
                        triangles=flight["triangles"], vertices=flight.get("vertices"),
                        smallestAltitudeMm=flight["smallestAltitudeMm"],
                        stones=len(flight["stones"]), ok=flight["ok"], shareOk=flight["shareOk"],
                        shareFails=flight["shareFails"], shareRule=flight["shareRule"]),
                    level=level),
        data=data.src, code=code_ids(part),
    ))


def make_object(name, m):
    """One level as a Blender mesh for the FBX route: its triangles in order, flat (each corner its face's normal), the
    eight channels as float32 UV layers set per corner (each triangle's own edge distances), and each triangle with
    its own three vertices (FBX control points). The unsharing is the FBX route's alone: Unity's FBX import merges the
    corners that share a control point when their UVs lie within about 1e-3 and their normals within about 1.3
    degrees, whatever its weld setting (the Unity builder's proof: reviews/lt1/port/2b/r2a/stones/logs/
    readback-step.txt: a triangle took a neighbour's edge distances or normal), and with no control point shared
    nothing can merge. The part's own mesh (m) keeps its positions shared where corners are one; step 5's chunks
    carry vertices exactly and may share the corners identical in every channel (few under the contract, as the edge
    distances are each triangle's own: indexed_vertices); the sidecar, the manifest and the sheet count all three."""
    import bpy
    me = bpy.data.meshes.new(name)
    nt = len(m["T"])
    corners = np.asarray(m["V"], float)[np.asarray(m["T"]).ravel()]
    me.from_pydata([tuple(float(c) for c in v) for v in corners], [],
                   [(3 * t, 3 * t + 1, 3 * t + 2) for t in range(nt)])
    if me.validate(verbose=False):
        raise Failed(f"{name}: Blender's validate changed the mesh")
    loops = np.zeros(len(me.loops), dtype=np.int64)
    me.loops.foreach_get("vertex_index", loops)
    if len(me.polygons) != nt or len(me.vertices) != 3 * nt or not np.array_equal(loops, np.arange(3 * nt)):
        raise Failed(f"{name}: the mesh is not its triangles in order, each with its own three vertices")
    for c, layer_name in enumerate(UV_LAYERS):
        layer = me.uv_layers.new(name=layer_name)
        if layer is None:
            raise Failed(f"{name}: no room for UV layer {c}")
        layer.data.foreach_set("uv", np.asarray(m["UV"][c], np.float32).ravel())
    me.polygons.foreach_set("use_smooth", [False] * len(me.polygons))
    me.update()
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    return ob


def shared_object(name, m):
    """The probe for the FBX route's check: one level as a Blender mesh on the part's own vertices, its corners
    sharing control points where their positions are one (the first export's way, which Unity's import merges).
    Written only to a scratch file, so that readback is seen to refuse it; never installed."""
    import bpy
    me = bpy.data.meshes.new(name)
    me.from_pydata([tuple(float(c) for c in v) for v in m["V"]], [], [tuple(int(i) for i in t) for t in m["T"]])
    for c, layer_name in enumerate(UV_LAYERS):
        me.uv_layers.new(name=layer_name).data.foreach_set("uv", np.asarray(m["UV"][c], np.float32).ravel())
    me.polygons.foreach_set("use_smooth", [False] * len(me.polygons))
    me.update()
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    return ob


def readback(path, levels):
    """The exported FBX read back with Blender's own parser (as mesh_hash does, never re-imported): per level, its
    triangles in order, its positions as the export's map gives them (x, y, z to -x, z, y in the file, times its
    unit scale; Unity's import turns x back), its normals its faces', and all eight UV layers bit for bit as the
    float32 values set. Returns {level: notes}, raising Failed on any difference."""
    import mesh_hash
    parse_fbx = mesh_hash._parser()
    root, _version = parse_fbx.parse(path)
    objects = next(e for e in root.elems if e.id == b"Objects")
    conns = next(e for e in root.elems if e.id == b"Connections")
    geoms = {e.props[0]: e for e in objects.elems if e.id == b"Geometry"}
    models = {e.props[0]: e for e in objects.elems if e.id == b"Model"}
    by_name = {}
    for c in conns.elems:
        if c.props[0] == b"OO" and c.props[1] in geoms and c.props[2] in models:
            by_name[mesh_hash._name(models[c.props[2]].props[1])] = geoms[c.props[1]]
    notes = {}
    for name, m in levels.items():
        if name not in by_name:
            raise Failed(f"readback: no mesh {name} in {path} ({sorted(by_name)})")
        g = by_name[name]
        el = {}
        for c in g.elems:
            el.setdefault(c.id, []).append(c)
        Vf = np.frombuffer(el[b"Vertices"][0].props[0], np.float64).reshape(-1, 3)
        pvi = np.frombuffer(el[b"PolygonVertexIndex"][0].props[0], np.int32)
        ends = pvi < 0
        corners = np.where(ends, -pvi - 1, pvi)
        nt = len(m["T"])
        if ends.sum() != nt or len(pvi) != 3 * nt or not ends[2::3].all():
            raise Failed(f"readback {name}: {int(ends.sum())} polygons of {len(pvi)} corners, not {nt} triangles")
        # the FBX route's check: no two corners share a control point (make_object), since Unity's import merges
        # near-equal corners that do; the file has 3 a triangle, each corner its own, in order
        if len(Vf) != 3 * nt or not np.array_equal(corners, np.arange(3 * nt)):
            _u, uses = np.unique(corners, return_counts=True)
            raise Failed(f"readback {name}: {len(Vf)} control points for {3 * nt} corners, {int(uses[uses > 1].sum())} "
                         f"corners on {int((uses > 1).sum())} shared ones: Unity's import would merge them")
        want = np.asarray(m["V"], np.float32).astype(np.float64)[m["T"].ravel()]
        want = np.stack([-want[:, 0], want[:, 2], want[:, 1]], -1)
        got = Vf[corners]
        big = np.abs(want).max()
        scale = float(np.abs(got).max() / big)
        if not any(abs(scale - s) < 1e-9 * s for s in (1.0, 100.0)):
            raise Failed(f"readback {name}: positions scaled {scale}")
        scale = 1.0 if abs(scale - 1.0) < 1e-9 else 100.0
        pos_err = float(np.abs(got - scale * want).max()) / scale
        if pos_err > 0.0:
            raise Failed(f"readback {name}: positions off the map by {pos_err:.3e} m")
        # normals: per corner, each its face's (flat). Blender computes them in float32 from the float32 positions, so
        # (a) a triangle's three corners carry one normal exactly; (b) it is the normal of the triangle's own corners
        # as the file holds them, to float32's arithmetic (1e-5); (c) it lies on the face's plane to what rounding the
        # positions to float32 allows a triangle of its altitude (4 R 2^-24 / altitude, R the largest coordinate)
        ln = el[b"LayerElementNormal"][0]
        sub = {c.id: c for c in ln.elems}
        N = np.frombuffer(sub[b"Normals"].props[0], np.float64).reshape(-1, 3)
        if sub.get(b"NormalsIndex") is not None:
            N = N[np.frombuffer(sub[b"NormalsIndex"].props[0], np.int32)]
        if len(N) != 3 * nt:
            raise Failed(f"readback {name}: {len(N)} normals for {3 * nt} corners")
        N3 = N.reshape(nt, 3, 3)
        if not (np.array_equal(N3[:, 0], N3[:, 1]) and np.array_equal(N3[:, 0], N3[:, 2])):
            raise Failed(f"readback {name}: a triangle's corners carry different normals (not flat)")
        P = got.reshape(nt, 3, 3) / scale
        own = np.cross(P[:, 1] - P[:, 0], P[:, 2] - P[:, 0])
        twice = np.linalg.norm(own, axis=1)
        own = own / twice[:, None]
        own_err = float(np.abs(N3[:, 0] - own).max())
        if own_err > 1e-5:
            raise Failed(f"readback {name}: normals off their triangles' own by {own_err:.2e}")
        fn = np.array([p["n"] for p in m["plane"]])
        fn = np.stack([-fn[:, 0], fn[:, 2], fn[:, 1]], -1)
        longest = np.max([np.linalg.norm(P[:, (i + 1) % 3] - P[:, i], axis=1) for i in range(3)], axis=0)
        allow = 4.0 * float(np.abs(P).max()) * 2.0 ** -24 / (twice / longest) + 1e-6
        dev = np.linalg.norm(N3[:, 0] - fn, axis=1)
        if (dev > allow).any():
            t = int(np.argmax(dev / allow))
            raise Failed(f"readback {name}: triangle {t}'s normal {dev[t]:.2e} off its face's plane, over float32's "
                         f"{allow[t]:.2e}")
        n_err = float(dev.max())
        # the eight UV layers
        uvs = {}
        for lay in el.get(b"LayerElementUV", []):
            sub = {c.id: c for c in lay.elems}
            idx = lay.props[0]
            vals = np.frombuffer(sub[b"UV"].props[0], np.float64).reshape(-1, 2)
            ref = sub[b"ReferenceInformationType"].props[0]
            mapping = sub[b"MappingInformationType"].props[0]
            if mapping != b"ByPolygonVertex":
                raise Failed(f"readback {name}: UV{idx} mapped {mapping!r}")
            if ref == b"IndexToDirect":
                vals = vals[np.frombuffer(sub[b"UVIndex"].props[0], np.int32)]
            uvs[idx] = (sub[b"Name"].props[0].decode(), vals)
        if sorted(uvs) != list(range(8)):
            raise Failed(f"readback {name}: UV layers {sorted(uvs)}")
        for c in range(8):
            lname, vals = uvs[c]
            if lname != UV_LAYERS[c]:
                raise Failed(f"readback {name}: UV{c} named {lname!r}, not {UV_LAYERS[c]!r}")
            exp = np.asarray(m["UV"][c], np.float32).reshape(-1, 2).astype(np.float64)
            if vals.shape != exp.shape or not np.array_equal(vals, exp):
                diff = np.abs(vals - exp).max() if vals.shape == exp.shape else float("nan")
                raise Failed(f"readback {name}: UV{c} differs by {diff:.3e}")
        notes[name] = dict(triangles=nt, corners=len(pvi), fileVertices=len(Vf),
                           controlPoints="three a triangle, its own, none shared", unitScale=scale,
                           positions="exact", normals="flat, each its triangle's own", normalsOwnMaxErr=own_err,
                           normalsOffPlaneMax=n_err, uv="all eight bit for bit")
    return notes


def export(part, out, res, rule, data, defn, flight=None, level=None):
    """Export one stone: its checks must pass; its two levels made in an empty scene, exported to a scratch file and
    read back, then installed under the Unity lock (only when its meshes changed: an FBX's bytes change at every
    export by its header's time), its sidecar beside it, its hashes into the part code's manifest."""
    import shutil
    import tempfile
    import bpy
    sys.path.insert(0, os.path.join(ROOT, "blender", "generators"))
    import stone as ST      # its _export_fbx and install_lock, imported, never edited
    import mesh_hash
    if res["fails"]:
        raise Failed(f"{part}: the checks fail, nothing is exported: " + "; ".join(res["fails"]))
    for ob in list(bpy.data.objects):
        bpy.data.objects.remove(ob, do_unlink=True)
    names = dict(L0=f"{part}_L0", L1=f"{part}_L1")
    obs = [make_object(names[k], out[k]) for k in ("L0", "L1")]
    side = sidecar(part, out, res, rule, data, defn, flight, level)
    path = os.path.join(ROOT, GENERATED, f"{part}.fbx")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    scratch = tempfile.mkdtemp(prefix="stones-export-")
    try:
        trial = os.path.join(scratch, f"{part}.fbx")
        ST._export_fbx(trial, obs)
        back = readback(trial, {names[k]: out[k] for k in ("L0", "L1")})
        new = mesh_hash.entry(trial)
        again = os.path.join(scratch, f"{part}-again.fbx")
        ST._export_fbx(again, obs)
        if mesh_hash.entry(again) != new:
            raise Failed(f"{part}: two exports of the same meshes hash differently")
        # the FBX route's check seen to bite: L0 on shared control points (the first export's way) must be refused
        probe_name = f"{names['L0']}_shared"
        probe = shared_object(probe_name, out["L0"])
        probe_path = os.path.join(scratch, f"{part}-shared.fbx")
        try:
            ST._export_fbx(probe_path, [probe])
        finally:
            bpy.data.objects.remove(probe, do_unlink=True)
        try:
            readback(probe_path, {probe_name: out["L0"]})
        except Failed as e:
            refused = str(e)
        else:
            raise Failed(f"{part}: the FBX route's check passed L0 written on shared control points")
    finally:
        shutil.rmtree(scratch, ignore_errors=True)
    back["sharedProbe"] = dict(refused=refused, note="L0 written on the part's own vertices (shared control points) "
                                                     "to a scratch file, so the FBX route's check is seen to refuse it")
    side["readback"] = back
    side["meshHash"] = new["hash"]
    text = json.dumps(side, indent=1) + "\n"
    with ST.install_lock(path):
        old = mesh_hash.entry(path) if os.path.exists(path) else None
        if old == new:
            print("FBX", os.path.relpath(path, ROOT), "unchanged: left as it is")
        else:
            ST._export_fbx(path, obs)
            if mesh_hash.entry(path) != new:
                raise Failed(f"{part}: the installed FBX does not hash as the one read back")
            print("FBX", os.path.relpath(path, ROOT))
        ST._write_if_changed(path[:-4] + ".json", text)
    mesh_hash.write_manifest(path, manifest=os.path.join(ROOT, MANIFEST))
    manifest_notes(part, out, names)
    return side


def manifest_notes(part, out, names):
    """Beside mesh_hash's entry (whose vertices are the FBX's control points, three a triangle), each level's own
    count: the part's mesh with its corners shared where they are one, so the cost of the FBX route's unsharing shows
    beside the triangles (mesh_hash's check reads only the hash, so the note changes nothing it compares)."""
    mp = os.path.join(ROOT, MANIFEST)
    with open(mp) as fh:
        man = json.load(fh)
    man[f"{part}.fbx"]["levels"] = {names[k]: dict(triangles=len(out[k]["T"]), partVertices=len(out[k]["V"]),
                                                   indexedVertices=indexed_vertices(out[k]),
                                                   fbxVertices=3 * len(out[k]["T"])) for k in ("L0", "L1")}
    man[f"{part}.fbx"]["levelsNote"] = ("partVertices: the part's own mesh, positions shared where corners are one; "
                                        "indexedVertices: corners identical in every channel counted once (an exact "
                                        "indexed mesh, as step 5's chunks; the edge distances are each triangle's "
                                        "own); fbxVertices: the FBX's, three a triangle, none shared (Unity's FBX "
                                        "import merges near-equal corners that share one)")
    with open(mp, "w") as fh:
        json.dump(dict(sorted(man.items())), fh, indent=1)
        fh.write("\n")


# -- the quick sheet (inside Blender, Workbench; it checks the machinery works and judges nothing) --------------------

KIND_RGB = {0: (0.60, 0.58, 0.54), 1: (0.88, 0.52, 0.20), 2: (0.40, 0.46, 0.52), 3: (0.56, 0.46, 0.36)}   # tread/top, chamfer, split, bed
THIN_RGB, WIRE_RGB, INK_RGB, DEEP_RGB = (0.86, 0.10, 0.08), (0.06, 0.06, 0.06), (0.02, 0.02, 0.02), (0.10, 0.22, 0.55)
CELL = (1280, 720)
LABEL_CHARS = 110       # a label's longest line; fewer where its drawn width would leave the cell (_label)


def timing_running():
    """A timing run holds the Unity lock (L5 has priority): no render starts while it does."""
    tools = os.path.join(ROOT, "tools")
    if tools not in sys.path:
        sys.path.append(tools)
    import unity_lock
    h = unity_lock.read_holder()
    return bool(h and h.get("timing") and unity_lock.alive(h.get("pid"), h.get("pid_start")))


def _wait_for_quiet():
    import time
    while timing_running():
        print("a timing run holds the Unity lock: the sheet waits (30 s)")
        time.sleep(30)


def _coloured_mesh(name, V, tris, rgb):
    """A mesh of triangles (V, tris) with one colour per triangle, as a corner colour attribute Workbench shows."""
    import bpy
    me = bpy.data.meshes.new(name)
    me.from_pydata([tuple(float(c) for c in v) for v in V], [], [tuple(int(i) for i in t) for t in tris])
    me.validate(verbose=False)
    attr = me.color_attributes.new(name="col", type="FLOAT_COLOR", domain="CORNER")
    cols = np.repeat(np.asarray(rgb, np.float32).reshape(-1, 3), [len(p.vertices) for p in me.polygons], axis=0)
    rgba = np.concatenate([cols, np.ones((len(cols), 1), np.float32)], -1)
    attr.data.foreach_set("color", rgba.ravel())
    me.color_attributes.active_color = attr
    me.color_attributes.render_color_index = me.color_attributes.active_color_index
    me.polygons.foreach_set("use_smooth", [False] * len(me.polygons))
    me.update()
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    return ob


def _wire(m, half):
    """Every triangle edge as a thin square prism, half (m) across: the triangulation drawn over the stone."""
    edges = sorted({(min(int(a), int(b)), max(int(a), int(b))) for t in m["T"] for a, b in
                    ((t[0], t[1]), (t[1], t[2]), (t[2], t[0]))})
    V, F = [], []
    for a, b in edges:
        A, Bp = m["V"][a], m["V"][b]
        e = B.unit(Bp - A)
        u = B.unit(np.cross(e, [0.0, 0.0, 1.0]) if abs(e[2]) < 0.9 else np.cross(e, [1.0, 0.0, 0.0]))
        w = np.cross(e, u)
        k = len(V)
        for P in (A, Bp):
            for su, sw in ((1, 1), (-1, 1), (-1, -1), (1, -1)):
                V.append(P + half * (su * u + sw * w))
        for i in range(4):
            j = (i + 1) % 4
            F += [(k + i, k + j, k + 4 + j), (k + i, k + 4 + j, k + 4 + i)]
    return np.array(V), np.array(F)


def _camera(scene, cam_pos, target, zoom=1.0, ortho=None):
    import bpy
    from mathutils import Vector
    cd = bpy.data.cameras.new("cam")
    cd.sensor_fit = "VERTICAL"
    cd.sensor_height = RIG["sensorMm"] / zoom
    cd.lens = RIG["focalMm"]
    cd.clip_start, cd.clip_end = 0.01, 200.0
    if ortho:
        cd.type = "ORTHO"
        cd.sensor_fit = "HORIZONTAL"     # ortho_scale is then the frame's width, as _label and the wire's px take it
        cd.ortho_scale = ortho
    ob = bpy.data.objects.new("cam", cd)
    scene.collection.objects.link(ob)
    ob.location = Vector(cam_pos)
    ob.rotation_euler = (Vector(target) - Vector(cam_pos)).to_track_quat("-Z", "Y").to_euler()
    scene.camera = ob
    return ob


def _fit(V, az, el, aspect=CELL[0] / CELL[1], fill=0.82):
    """A camera at azimuth az and elevation el (degrees) that frames the points V, through the rig's lens: the
    distance found by bisection so the projected box fills `fill` of the frame."""
    target = 0.5 * (V.min(axis=0) + V.max(axis=0))
    a, e = math.radians(az), math.radians(el)
    d = np.array([math.sin(a) * math.cos(e), -math.cos(a) * math.cos(e), math.sin(e)])
    t = RIG["sensorMm"] / 2 / RIG["focalMm"]
    lo, hi = 0.2, 50.0
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        view = dict(cam=target + mid * d, target=target)
        f = B.unit(view["target"] - view["cam"])
        r = B.unit(np.cross(f, [0.0, 0.0, 1.0]))
        u = np.cross(r, f)
        q = V - view["cam"]
        zc = q @ f
        x, y = (q @ r) / zc, (q @ u) / zc
        ok = np.abs(x).max() <= fill * t * aspect and np.abs(y).max() <= fill * t
        lo, hi = (lo, mid) if ok else (mid, hi)
    return target + hi * d, target


def _label(scene, cam, text, zoom=1.0):
    """The text at the frame's top left, in front of the camera, wrapped to the cell's width."""
    import bpy
    from mathutils import Vector
    import textwrap

    def text_mesh(body):
        cu = bpy.data.curves.new("label", "FONT")
        cu.body = body
        cu.size = 1.0
        tob = bpy.data.objects.new("label", cu)
        scene.collection.objects.link(tob)
        dg = bpy.context.evaluated_depsgraph_get()
        me = bpy.data.meshes.new_from_object(tob.evaluated_get(dg))
        bpy.data.objects.remove(tob, do_unlink=True)
        bpy.data.curves.remove(cu)
        V = np.array([v.co[:] for v in me.vertices])
        F = [tuple(p.vertices) for p in me.polygons]
        bpy.data.meshes.remove(me)
        return V, F

    # a unit of the text is h below, 0.09 of the frame's half height: a line fits while it spans under 0.94 of the
    # frame's width, 2 half_w
    room = 0.94 * 2.0 * (CELL[0] / CELL[1]) / 0.09
    chars = LABEL_CHARS
    while True:
        V, F = text_mesh("\n".join(textwrap.wrap(text, chars)))
        if V[:, 0].max() <= room or chars <= 40:
            break
        chars -= 4
    tris = []
    for f in F:
        tris += [(f[0], f[i], f[i + 1]) for i in range(1, len(f) - 1)]
    if cam.data.type == "ORTHO":
        half_h = cam.data.ortho_scale / 2 / (CELL[0] / CELL[1])
        z = 1.0
    else:
        z = 0.5
        half_h = z * (cam.data.sensor_height / 2) / cam.data.lens
    half_w = half_h * CELL[0] / CELL[1]
    h = 0.045 * 2 * half_h
    P = np.stack([-half_w + 0.03 * half_w + V[:, 0] * h, half_h - 0.06 * 2 * half_h + V[:, 1] * h,
                  np.full(len(V), -z)], -1)
    M = np.array(cam.matrix_world)
    W = (M[:3, :3] @ P.T).T + M[:3, 3]
    _coloured_mesh("label", W, tris, [INK_RGB] * len(tris))


def _render_cell(path, stone, view, text, colours=None, wire_px=1.4, zoom=1.0, ortho=None):
    """One cell: the stone (each triangle its colour), its triangulation as a wire about wire_px wide at the stone's
    middle, the label; rendered by Workbench to path."""
    import bpy
    scene = bpy.context.scene
    for ob in list(scene.collection.objects):
        bpy.data.objects.remove(ob, do_unlink=True)
    cam_pos, target = view
    cam = _camera(scene, cam_pos, target, zoom, ortho)
    dist = float(np.linalg.norm(np.asarray(target) - np.asarray(cam_pos)))
    if ortho:
        px = ortho / CELL[0]
    else:
        px = dist * (RIG["sensorMm"] / zoom) / RIG["focalMm"] / CELL[1]
    rgb = colours if colours is not None else [KIND_RGB[int(stone["UV"][2, t, 0, 0])] for t in range(len(stone["T"]))]
    _coloured_mesh("stone", stone["V"], stone["T"], rgb)
    WV, WF = _wire(stone, 0.5 * wire_px * px)
    _coloured_mesh("wire", WV, WF, [WIRE_RGB] * len(WF))
    _label(scene, cam, text, zoom)
    scene.render.filepath = path
    _wait_for_quiet()
    bpy.ops.render.render(write_still=True)


def _scene():
    import bpy
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_WORKBENCH"
    scene.render.resolution_x, scene.render.resolution_y = CELL
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGB"
    scene.render.image_settings.compression = 90
    scene.render.dither_intensity = 0.0      # no noise in the flat ground, so the sheet stays small in git
    scene.view_settings.view_transform = "Standard"
    scene.display.render_aa = "8"
    sh = scene.display.shading
    sh.light = "STUDIO"
    sh.color_type = "VERTEX"
    sh.show_cavity = False           # its screen-space sampling speckles every face: noise to git, nothing to see
    sh.show_shadows = True
    scene.display.light_direction = (-0.45, -0.65, 0.62)
    scene.display.shadow_focus = 0.6
    world = bpy.data.worlds.new("sheet")
    world.color = (0.93, 0.93, 0.92)
    scene.world = world
    return scene


def _gate_colours(m, view):
    """Each triangle's kind colour, red where it is under 2 px in the gate's view (thin_gate's measure)."""
    out = []
    for t, tri in enumerate(m["T"]):
        P3 = m["V"][tri]
        rgb = KIND_RGB[int(m["UV"][2, t, 0, 0])]
        if m["plane"][t]["n"] @ (view["cam"] - P3.mean(axis=0)) > 0:
            p2, _ = project(view, P3)
            a, b, c = p2
            A2 = abs((b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0]))
            Lm = max(np.linalg.norm(b - a), np.linalg.norm(c - a), np.linalg.norm(c - b))
            if Lm > 0 and A2 / Lm < GATE["thinPx"]:
                rgb = THIN_RGB
        out.append(rgb)
    return out


def _depth_colours(o, m):
    """The top by its worn depth (blue the deepest), every other face its kind."""
    tops = [t for t in range(len(m["T"])) if m["face"][t] == "top"]
    dep = {t: o["H"] - float(m["V"][m["T"][t]][:, 2].mean()) for t in tops}
    most = max(dep.values()) if dep else 1.0
    out = []
    for t in range(len(m["T"])):
        k = KIND_RGB[int(m["UV"][2, t, 0, 0])]
        if t in dep and most > 0:
            s = dep[t] / most
            k = tuple((1 - s) * a + s * b for a, b in zip(KIND_RGB[0], DEEP_RGB))
        out.append(k)
    return out


def write_png(path, rgb):
    """An 8-bit RGB PNG, each row filtered by whichever of PNG's five filters leaves the least (the usual heuristic:
    the smallest sum of the residuals as signed bytes), deflated at level 9, with no time or software chunk: the same
    pixels always make the same bytes, and a sheet stays small in git."""
    import struct
    import zlib
    h, w, _c = rgb.shape
    a = rgb.reshape(h, w * 3).astype(np.int16)
    zero = np.zeros(w * 3, np.int16)
    raw = bytearray()
    prev = zero
    for y in range(h):
        cur = a[y]
        left = np.concatenate([zero[:3], cur[:-3]])
        ul = np.concatenate([zero[:3], prev[:-3]])
        p = left + prev - ul
        pa, pb, pc = np.abs(p - left), np.abs(p - prev), np.abs(p - ul)
        paeth = np.where((pa <= pb) & (pa <= pc), left, np.where(pb <= pc, prev, ul))
        cands = [cur, cur - left, cur - prev, cur - (left + prev) // 2, cur - paeth]
        res = [(c & 0xFF).astype(np.uint8) for c in cands]
        cost = [int(np.abs(r.astype(np.int8).astype(np.int32)).sum()) for r in res]
        f = int(np.argmin(cost))
        raw.append(f)
        raw += res[f].tobytes()
        prev = cur

    def chunk(tag, body):
        return struct.pack(">I", len(body)) + tag + body + struct.pack(">I", zlib.crc32(tag + body) & 0xFFFFFFFF)

    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as fh:
        fh.write(b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)) +
                 chunk(b"IDAT", zlib.compress(bytes(raw), 9)) + chunk(b"IEND", b""))


def sheet_path(part):
    return SHEET if part == "step" else f"reviews/lt1/port/2b/r2a/stones/blender-sheet-{part}.png"


def _compose(cells, rel):
    """The cells, three across, into one PNG at rel."""
    import bpy
    cols, gap = 3, 6
    rows = -(-len(cells) // cols)
    Wd, Ht = cols * CELL[0] + (cols - 1) * gap, rows * CELL[1] + (rows - 1) * gap
    canvas = np.ones((Ht, Wd, 4), np.float32)
    for i, path in enumerate(cells):
        img = bpy.data.images.load(path)
        px = np.array(img.pixels[:], np.float32).reshape(CELL[1], CELL[0], img.channels)
        bpy.data.images.remove(img)
        r, c = divmod(i, cols)
        y0 = Ht - (r + 1) * CELL[1] - r * gap         # Blender's pixels run bottom up
        x0 = c * (CELL[0] + gap)
        canvas[y0:y0 + CELL[1], x0:x0 + CELL[0], :3] = px[:, :, :3]
    rgb = np.clip(np.round(canvas[::-1, :, :3] * 255.0), 0, 255).astype(np.uint8)    # top down, the cells' bytes
    write_png(os.path.join(ROOT, rel), rgb)
    print("SHEET", rel, f"{len(cells)} cells, {Wd} x {Ht}")


def _band_colours(o, m):
    """A wall stone's or a coping's faces by kind, and where a face is drawn only within its seen band (top, bed and
    ends), a lighter shade of its kind, so the band's edge shows."""
    out = []
    for t in range(len(m["T"])):
        k = KIND_RGB.get(int(m["UV"][2, t, 0, 0]), KIND_RGB[0])
        if m["face"][t] in o["regions"]:
            k = tuple(0.5 * a + 0.5 for a in k)
        out.append(k)
    return out


def sheet(part, out, variant_outs, res):
    """The quick sheet: the specimen at both levels in the gate's view (magnified, its thin triangles red) and two
    more, the machinery's variants; the step's skirts and wear, a wall stone's or a coping's seen bands from behind
    and its end square on; cells composed into sheet_path(part)."""
    import shutil
    import tempfile
    _scene()
    o, L0, L1 = out["outline"], out["L0"], out["L1"]
    tmp = tempfile.mkdtemp(prefix="stones-sheet-")
    cells = []
    try:
        def cell(stone, view, text, **kw):
            path = os.path.join(tmp, f"cell-{len(cells):02d}.png")
            _render_cell(path, stone, view, text, **kw)
            cells.append(path)

        th = res["thin"]
        for name, m, dist in (("L0", L0, GATE["l0Distance"]), ("L1", L1, GATE["l1Distance"])):
            zoom = (4.0 if name == "L0" else 10.0) if part == "step" else float(max(1, round(0.9 * dist / o["L"])))
            v = views(o, dist)["face-on 20"]
            r = th[name]["face-on 20"]
            cell(m, (v["cam"], v["target"]),
                 f"{part} {name}, face-on 20 deg at {dist:g} m (the level's view; x{zoom:g}): {r['thin']} of "
                 f"{r['front']} under 2 px, red", colours=_gate_colours(m, v), zoom=zoom, wire_px=1.2)
            for vn, az, el in (("raised 45", 0, 45), ("left 40", -40, 20)):
                cell(m, _fit(m["V"], az, el), f"{part} {name}, {vn}: {len(m['T'])} triangles; vertices "
                                              f"{len(m['V'])} its own, {indexed_vertices(m)} indexed, "
                                              f"{3 * len(m['T'])} the FBX's")
        for vname, vo in variant_outs.items():
            cell(vo["L0"], _fit(vo["L0"]["V"], 30, 35),
                 f"variant: {vname}, L0 {len(vo['L0']['T'])} triangles ({len(vo['L0']['V'])} vertices, the FBX's "
                 f"{3 * len(vo['L0']['T'])}), L1 {len(vo['L1']['T'])} ({len(vo['L1']['V'])}, "
                 f"{3 * len(vo['L1']['T'])})")
        if part == "step":
            cell(L0, _fit(L0["V"], 150, -15), f"{part} L0 from behind, below: the skirts ({o['skirt'] * 1000:g} mm)")
            span = max(o["L"], o["D"]) * 1.15
            top = (np.array([o["L"] / 2, o["D"] / 2, 10.0]), np.array([o["L"] / 2, o["D"] / 2, 0.0]))
            cell(L0, top, f"{part} L0 from above: the wear, blue the deepest ({o['lattice']['parts']} parts of the "
                          f"flight)", colours=_depth_colours(o, L0), ortho=span, wire_px=1.0)
        else:
            band = (f"the band {o['bandMm']} mm behind the wall's plane" if part == "wallstone" else
                    f"the bed {o['summary']['bedBandMm']:g} mm past each face, a joint end within "
                    f"{o['summary']['jointBandMm']} mm")
            for name, m in (("L0", L0), ("L1", L1)):
                cell(m, _fit(m["V"], 160, 30), f"{part} {name} from behind, above: drawn only where seen ({band}; "
                                               f"lighter)", colours=_band_colours(o, m))
            V = L0["V"]
            span = 1.25 * max(float(np.ptp(V[:, 1])), float(np.ptp(V[:, 2])) * CELL[0] / CELL[1])   # the width
            mid = 0.5 * (V.min(axis=0) + V.max(axis=0))
            end = (np.array([o["L"] + 5.0, mid[1], mid[2]]), np.array([o["L"], mid[1], mid[2]]))
            what = ((f"its face {o['faceFacets']} planes, the ridges proud {o['proudMm']} mm" if o['faceFacets'] > 1
                     else "its face one plane") +
                    f", the batter {o['summary']['batter'][0]}/{o['summary']['batter'][1]}"
                    if part == "wallstone" else
                    f"proud {o['summary']['proudMm']['front']} mm at the front, {o['summary']['proudMm']['back']} at "
                    f"the back")
            cell(L0, end, f"{part} L0, its right end square on (ortho): {what}", colours=_band_colours(o, L0),
                 ortho=span, wire_px=1.0)
        _compose(cells, sheet_path(part))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


SPECIMENS = {"step": specimen_step, "wallstone": specimen_wallstone, "coping": specimen_coping}
PARTS = ("step", "wallstone", "coping")


def main(argv):
    """stones.py <check | flight | export | sheet> [part,part,...] (every part when none is named)."""
    cmd = argv[0] if argv else "check"
    parts = argv[1].split(",") if len(argv) > 1 else list(PARTS)
    if cmd not in ("check", "flight", "export", "sheet"):
        raise SystemExit(f"unknown command {cmd}: check, flight, export or sheet")
    bad = [p for p in parts if p not in PARTS]
    if bad:
        raise SystemExit(f"unknown parts {bad}: {', '.join(PARTS)}")
    data = Data()
    if cmd == "flight":
        ok = True
        for part in parts:
            fr = flight_check(data, part=part)
            print(flight_summary(fr))
            ok = ok and fr["ok"]
        return 0 if ok else 1
    failed = []
    for part in parts:
        print(f"\n==== {part}")
        pdata = Data(data.commit)
        defn = definition(part)
        facts, rule = SPECIMENS[part](pdata)
        print(json.dumps({k: v for k, v in rule.items() if k != "laid"}, indent=1))
        out = build(part, facts, defn, pdata)
        res = check(part, out, defn)
        print(summary(res))
        fr, why = flight_current(part)
        print(flight_summary(fr) if fr else f"pool: {why}")
        lv, lwhy = level_gate()
        print(level_summary(lv) if lv else f"level: {lwhy}")
        if cmd == "export":
            if fr is None or not fr["ok"]:
                raise Failed(f"{part}: the pool's stones do not all pass: {why or fr['fails'][:10]}")
            if lv is None or not lv["ok"]:
                raise Failed(f"{part}: the level's checks do not pass: {lwhy or lv['fails']}")
            side = export(part, out, res, rule, pdata, defn, flight=fr, level=lv)
            print("readback:", json.dumps(side["readback"]))
            continue
        failed += [f"{part}: {f}" for f in res["fails"]] + ([f"{part}: {why}"] if fr is None else
                                                           [f"{part}: {f}" for f in fr["fails"]])
        failed += [f"{part}: level: {lwhy}"] if lv is None else [f"{part}: {f}" for f in lv["fails"]]
        vouts = {}
        if part == "step":
            vs = {name: (v, {}) for name, v in variants(facts).items()}
        else:
            vs = wall_variants(part, Data(data.commit))
        for name, (v, params) in vs.items():
            vd = with_params(defn, params)
            ov = build(part, v, vd, Data(data.commit))
            rv = check(part, ov, vd)
            print(f"\n== {part} variant {name}" + (f" (params {params})" if params else ""))
            print(summary(rv))
            failed += [f"{part} {name}: {f}" for f in rv["fails"]]
            vouts[name] = ov
        if cmd == "sheet":
            sheet(part, out, vouts, res)
    if cmd == "export":
        return 0
    print("\nALL FAILS: " + ("; ".join(failed) if failed else "none"))
    return 0 if not failed else 1


if __name__ == "__main__":
    args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
    sys.exit(main(args))
