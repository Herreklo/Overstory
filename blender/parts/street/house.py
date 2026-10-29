"""A whole house of Harbour Row from its record, the street test's generator: the corner's fitted parts (the finishing
test, blender/parts/finish/corner.py at de6e1c0) grown to every wall, opening, trim, plinth stone, eave, verge, roof
course, ridge and chimney a house has, and its extensions. Nothing here belongs to one house: a house is its record
(the fixture), its era's working (packs/<pack>/house/<era>.json, whose `versions` give each part's family), the pack's
materials and the street's levels (street.json).

    Blender -b --factory-startup -P blender/parts/street/house.py -- --house 107 --out cache/street/gen/107
        [--fixture fixtures/lt1-street.json] [--year 1989]

Writes house-near.fbx, house-street.fbx and house-city.fbx (one object per material), house.blend (the levels and the bake level's
tiles, for the bakes) and house.json (triangles per level and object, the page's charts, the walls, courses, openings
and features the paint reads). Fails, writing nothing, when a level is over its budget's top.

The house's own frame: x along the street front from its left corner, y back from the building line, z up, metres.
Walls run counter-clockwise seen from above: 0 the front (+x, outward -y), 1 the right gable or end, 2 the back, 3 the
left; an extension's walls follow. Every wall piece is built in its wall's frame (x along, outward -y, up z).

Two levels from one plan, as the corner's: near draws every board with its lap, every arris chamfered and the lowest
roof courses tile by tile; street draws each wall as planes whose laps come from the page's normal, its trims as boxes,
its roof as course planes (their tiles' relief baked from the bake level). Both share UV1, the page. Vertex colour: R
the arris, G the piece's seed, B the under layer forced (mortar), A on a near board how far below the next course's
butt the corner sits (0..1 over lapReach), 1 elsewhere.
"""

import json
import math
import os
import re
import sys

import bpy
from mathutils import Matrix, Vector

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "blender", "resolver"))
import hashing as HS  # noqa: E402
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from geom import MM, Charts, Face, Piece, data_profile, extrude, newell, rect_profile, to_object, tris_of  # noqa: E402

Z = Vector((0.0, 0.0, 1.0))
OUT = Vector((0.0, -1.0, 0.0))
ALONG = Vector((1.0, 0.0, 0.0))


def load(path):
    with open(path if os.path.isabs(path) else os.path.join(ROOT, path)) as fh:
        return json.load(fh)


def rng(r):
    return [v * MM for v in r]


# ---------------------------------------------------------------- facts


class Facts:
    """A house's record as the generator reads it, in the year it is seen."""

    def __init__(self, fixture, hid, year):
        street = load(fixture)
        self.world = street["worldSeed"]
        rec = next(b for b in street["buildings"] if b["id"] == hid)
        self.id, self.type, self.plot = rec["id"], rec["type"], rec["plot"]
        self.year = year
        self.events = sorted((e for e in rec["events"] if e["year"] <= year), key=lambda e: (e["year"], e["id"]))
        built = self.first("built")
        self.built = built["year"]
        self.era = built["params"]["era"]
        self.storeys = built["params"]["storeys"] / 1000.0
        self.wealth = built["params"]["wealth"]
        self.age = year - self.built

    def all(self, kind):
        return [e for e in self.events if e["kind"] == kind]

    def first(self, kind):
        ev = self.all(kind)
        return ev[0] if ev else None

    def last(self, kind):
        ev = self.all(kind)
        return ev[-1] if ev else None

    def windows_made(self, wall_kind):
        """The year a wall's windows were made: the house's building, or the last event that replaced or restored
        them there ('street' scope: the front only; 'all': every wall). A restoration to 'original' windows makes them
        again in the house's own era."""
        made, era_of = self.built, self.built
        for e in self.events:
            p = e["params"]
            if e["kind"] == "windows_replaced" and (p.get("scope") == "all" or (p.get("scope") == "street" and wall_kind == "front")):
                made, era_of = e["year"], e["year"]
            if e["kind"] == "restored" and p.get("windows") == "original":
                made, era_of = e["year"], self.built
        return made, era_of

    def boarded(self):
        """The boarding's event, unless a later one opened the house again."""
        b = self.last("boarded")
        if b is None:
            return None
        if any(e["year"] > b["year"] and e["kind"] in ("restored", "unboarded", "repainted", "business_opened") for e in self.events):
            return None
        return b

    def key(self, *parts):
        return HS.h(self.world, f"h{self.id}", *parts)

    def u(self, *parts):
        return HS.unit(self.key(*parts))

    def between(self, lo, hi, *parts):
        return lo + (hi - lo) * self.u(*parts)

    def pick(self, options, *parts):
        """One of `options` (each with a `weight`) by the seed."""
        total = sum(o.get("weight", 1) for o in options)
        t = self.u(*parts) * total
        for o in options:
            t -= o.get("weight", 1)
            if t <= 0:
                return o
        return options[-1]


# ---------------------------------------------------------------- the frame's bends


class Frame:
    """Old timber moves (the working's bends), each by its cause, growing with the frame's age: one corner settles on
    its stones (which one is the seed's), the wall plates sag between the gables and the ridge with them, and the
    roof's thrust pushes the eave walls' heads out. Points are the house's rest positions."""

    def __init__(self, W, F, w, d, z_sill, z_top, z_ridge):
        b = W["bends"]
        c = F.age / 100.0
        self.settle = min(b["settleMostMm"], b["settleMmPerCentury"] * c) * MM * W["push"]["settle"]
        self.sag = min(b["sagMostMm"], b["sagMmPerCentury"] * c) * MM
        self.lean = min(b["leanMostMm"], b["leanMmPerCentury"] * c) * MM
        self.ridge_share = b.get("ridgeSagShare", 1.0)
        self.reach = b["settleReachMm"] * MM
        self.bend, self.share = b["settleBendMm"] * MM, b["settleBendShare"]
        k = int(F.u("frame", "settle-corner") * 4) % 4
        self.corner = ((0.0, 0.0), (w, 0.0), (w, d), (0.0, d))[k]
        self.w, self.d = w, d
        self.z_sill, self.z_top, self.z_ridge = z_sill, z_top, z_ridge

    def offset(self, p):
        x, y, z = p
        cx, cy = self.corner
        dx, dy_ = abs(x - cx), abs(y - cy)
        tx, ty = max(0.0, 1.0 - dx / self.reach), max(0.0, 1.0 - dy_ / self.reach)
        bx, by = max(0.0, 1.0 - dx / self.bend), max(0.0, 1.0 - dy_ / self.bend)
        dz = -self.settle * ((1.0 - self.share) * tx * ty + self.share * (bx * by) ** 2)
        s = math.sin(math.pi * min(1.0, max(0.0, x / self.w)))
        if z <= self.z_top:
            h = min(1.0, max(0.0, (z - self.z_sill) / (self.z_top - self.z_sill)))
            hs, hl = h, h * h
        else:
            r = min(1.0, (z - self.z_top) / max(self.z_ridge - self.z_top, 1e-3))
            hs, hl = 1.0 + (self.ridge_share - 1.0) * r, 1.0 - r
        dz -= self.sag * s * hs
        side = -1.0 if y < self.d / 2.0 else 1.0
        inside = 1.0 if -0.5 < y < self.d + 0.5 else 0.0
        dy = self.lean * s * hl * side * inside
        return Vector((0.0, dy, dz))

    def __call__(self, p):
        return p + self.offset(p)

    def rigid(self, anchor, along=None):
        """A rigid piece's move: the frame's offset at its anchor, and a turn about the anchor that follows the
        frame's slope along `along`, never a bend."""
        off = self.offset(anchor)
        if along is None or along.length < 1e-9:
            return Matrix.Translation(off)
        a = along.normalized()
        slope = (self.offset(anchor + a * 0.25) - self.offset(anchor - a * 0.25)).z / 0.5
        axis = Z.cross(a)
        if axis.length < 1e-9:
            return Matrix.Translation(off)
        rot = Matrix.Translation(anchor) @ Matrix.Rotation(-math.atan(slope), 4, axis.normalized()) @ Matrix.Translation(-anchor)
        return Matrix.Translation(off) @ rot


# ---------------------------------------------------------------- walls


class Wall:
    """A wall's frame: x along it from `origin`, outward local -y, up z. `kind` 'eave' (its top under the eave) or
    'gable' (its top the verge's rake); `group` the course table its boards follow."""

    def __init__(self, i, origin, angle, length, kind, group=0, base=0.0):
        self.i, self.L, self.kind, self.group = i, length, kind, group
        self.M = Matrix.Translation(Vector((origin[0], origin[1], base))) @ Matrix.Rotation(angle, 4, "Z")
        self.origin = Vector((origin[0], origin[1], 0.0))
        self.dir = (self.M.to_3x3() @ ALONG).normalized()
        self.out = (self.M.to_3x3() @ OUT).normalized()

    def along(self, world):
        return (world - self.origin).dot(self.dir)

    def info(self):
        return {"i": self.i, "origin": list(self.origin[:2]), "dir": list(self.dir[:2]), "out": list(self.out[:2]),
                "length": self.L, "kind": self.kind, "group": self.group}


# ---------------------------------------------------------------- the house


class House:
    def __init__(self, S, W, V, F, mats, paints):
        self.S, self.W, self.V, self.F, self.M, self.P = S, W, V, F, mats, paints
        self.pieces, self.charts = [], Charts()
        self.features = {"openings": [], "joints": [], "butts": [], "drips": [], "pipes": [], "roof": [], "tiles": []}
        self.push = W["push"]
        self.ch = {k: v * MM for k, v in W["chamferMm"].items() if k != "describes"}
        cl = W["cladding"]
        self.step = cl["stepMm"] * MM
        # the body
        self.w = F.plot["w"] * MM
        self.d = F.between(*rng(W["depthMm"]), "body", "depth")
        self.pitch = math.radians(F.between(*W["roofPitchDeg"], "body", "pitch"))
        self.t = math.tan(self.pitch)
        pl = W["plinth"]
        self.z_plinth = F.between(*rng(pl["heightMm"]), "plinth", "height")
        self.z_floor = self.z_plinth + W["floorOverPlinthMm"] * MM
        dr = W["dripBoard"]
        self.z_drip0 = self.z_plinth - 0.03
        self.z_drip1 = self.z_drip0 + dr["heightMm"] * MM
        self.full = int(math.floor(F.storeys + 1e-6))
        self.loft = F.storeys - self.full >= 0.5
        lift = (W["storeyMm"] + W["floorMm"]) * MM
        self.floors = [self.z_floor + k * lift for k in range(self.full)]
        self.z_loft = self.z_floor + self.full * lift
        self.knee = F.between(*rng(W["kneeMm"]), "body", "knee") if self.loft else 0.0
        self.z_top = self.z_loft + self.knee
        cs = W["casing"]
        self.cw = cs["widthMm"] * MM
        self.trim_proud = cs["proudMm"] * MM * self.push["trimProud"]
        self.sill_t = cs["sillMm"] * MM * self.push["sillThick"]
        self.cap_t = cs["capMm"] * MM * self.push["capThick"]
        self.head_h = cs["headMm"] * MM
        # the eave and the roof's planes (each eave wall's own frame: y out, the tiles' foot and the ridge)
        ev, vg = W["eaves"], W["verge"]
        self.ov = ev["overhangMm"] * MM
        self.fh, self.ft, self.st = ev["fasciaMm"] * MM, ev["fasciaThickMm"] * MM, ev["soffitThickMm"] * MM
        self.vov = vg["overhangMm"] * MM
        self.bt = vg["thickMm"] * MM * self.push["bargeThick"]
        self.bw = vg["boardMm"] * MM
        self.y_foot = -self.ov - self.ft - 0.05
        self.z_foot = self.z_top - self.st - 0.01 + self.fh + 0.004
        self.z_ridge = self.zp(self.d / 2.0)
        self.frame = Frame(W, F, self.w, self.d, self.z_floor, self.z_top, self.z_ridge)
        self.walls = [Wall(0, (0.0, 0.0), 0.0, self.w, "eave"), Wall(1, (self.w, 0.0), math.pi / 2, self.d, "gable"),
                      Wall(2, (self.w, self.d), math.pi, self.w, "eave"), Wall(3, (0.0, self.d), 3 * math.pi / 2, self.d, "gable")]
        self.version_of = {}
        self.courses = {}
        self.lean_to = None

    # ---- heights of the roof
    def zp(self, y):
        """The tiles' plane over a point `y` back from the front wall (symmetric about the ridge)."""
        yy = min(y, self.d - y)
        return self.z_foot + (yy - self.y_foot) * self.t

    def z_rake(self, a):
        """A gable's cladding top at `a` along it: under the verge's soffit."""
        return self.zp(a) - 0.085

    # ---- versions
    def version(self, family, made, era_of=None):
        """The part's version made in `made` (its looks those of `era_of`, a restoration's), by those who could pay;
        every opening of one making shares it. The versions are the pack's, shared by every era (house/versions.json):
        one naming `eras` is made only for a house of those."""
        era_of = era_of or made
        vs = [v for v in self.V[family] if self.F.era in v.get("eras", [self.F.era])]
        ok = [v for v in vs if v["years"][0] <= era_of <= v["years"][1] and v.get("wealth", [0, 1e9])[0] <= self.F.wealth <= v.get("wealth", [0, 1e9])[1]]
        if not ok:
            ok = [min(vs, key=lambda v: min(abs(era_of - v["years"][0]), abs(era_of - v["years"][1])))]
        v = self.F.pick(ok, "version", family, made)
        self.version_of[f"{family}@{made}"] = v["id"]
        return v

    # ---- pieces
    def make(self, pid, mat, levels=("near", "street"), wall=None, mode="frame", place=None, group=0):
        pl = place if place is not None else (wall.M if wall is not None else Matrix.Identity(4))
        pc = Piece(f"h{self.F.id}/{pid}", mat, levels, pl, mode, wall=wall.i if wall is not None else -1, group=group)
        self.pieces.append(pc)
        return pc

    def trim(self, pid, wall, o, L, P, Q, w, t, c, nseg=1, groups=("bottom", "front", "top"), caps=(True, True),
             chamfer_edges=(True, True), mode="frame", mat="trims", levels=("near", "street"), back=False, place=None, cut=None):
        pc = self.make(pid, mat, levels, wall, mode, place)
        nominal = {groups[1]: w, groups[0]: t, groups[2]: t}
        for lv in levels:
            cc = c if lv == "near" else 0.0
            prof = rect_profile(w, t, cc, groups=groups + ("back",), chamfer_edges=chamfer_edges, back=back)
            extrude(pc, lv, prof, o, L, P, Q, self.charts, nseg=nseg, caps=caps, nominal=nominal, cut=cut)
        return pc

    # ---- the story pole: one course table for the house's walls, its courses meeting every window's sill and head
    def course_table(self, group, z0, z1, fixed, cl, tag):
        lo, hi = rng(cl["exposureMm"])
        mean = 0.5 * (lo + hi)
        marks = sorted({z for z in fixed if z0 + 0.6 * lo < z < z1 - 0.6 * lo})
        edges = [z0] + marks + [z1]
        zs, n_all = [z0], 0
        for a, b in zip(edges, edges[1:]):
            n = max(1, round((b - a) / mean))
            draws = [self.F.between(lo, hi, tag, "course", n_all + k, "exposure") for k in range(n)]
            k = (b - a) / sum(draws)
            z = a
            for e in draws:
                z += e * k
                zs.append(z)
            n_all += n
        self.courses[group] = zs
        return zs

    # ---- openings
    def plan_openings(self):
        """Where the openings fall, from the record and the working: the front in bays with its door in an inner bay,
        each gable one window on each floor that has one and its loft's, the back two; a part the extension covers
        has none. Each opening's parts are versions of its making."""
        W, F = self.W, self.F
        op = W["openings"]
        bd = F.boarded()
        out = []
        win, loft, door = op["window"], op["loft"], op["door"]

        def add(wall, kind, a0, z0, ww, hh):
            made, era_of = F.windows_made("front" if wall.i == 0 else "other")
            o = {"wall": wall.i, "kind": kind, "a0": a0, "a1": a0 + ww, "z0": z0, "z1": z0 + hh,
                 "made": made if kind != "door" else F.built, "eraOf": era_of if kind != "door" else F.built,
                 "boarded": bd is not None and (bd["params"].get("scope") == "all" or wall.i == 0)}
            out.append(o)
        # the front: bays across it
        wall = self.walls[0]
        edge = F.between(*rng(op["front"]["edgeMm"]), "open", "front", "edge")
        ww = win["wMm"] * MM
        span = wall.L - 2 * edge - ww
        n = 1 + max(0, round(span / (op["front"]["bayMm"] * MM)))
        xs = [edge + (span * k / (n - 1) if n > 1 else span / 2.0) for k in range(n)]
        door_at = None
        if op["front"].get("door") and n >= 3:
            door_at = 1 + int(F.u("open", "front", "door") * (n - 2)) % (n - 2)
        for k, x in enumerate(xs):
            for z in self.floors:
                if k == door_at and z == self.floors[0]:
                    dw = door["wMm"] * MM
                    dz = door["overFloorMm"] * MM
                    dh = (win["sillOverFloorMm"] + win["hMm"]) * MM - dz if door.get("headWithWindows") else door["hMm"] * MM
                    add(wall, "door", x + (ww - dw) / 2.0, z + dz, dw, dh)
                else:
                    add(wall, "window", x, z + win["sillOverFloorMm"] * MM, ww, win["hMm"] * MM)
        # the gables: one window on each floor that has one, and the loft's
        for wall in (self.walls[1], self.walls[3]):
            c = wall.L / 2.0
            for fi, z in enumerate(self.floors):
                lo, hi = op["gable"]["ground"]
                if lo + round(F.u("open", wall.i, "floor", fi) * (hi - lo)) >= 1:
                    add(wall, "window", c - ww / 2.0, z + win["sillOverFloorMm"] * MM, ww, win["hMm"] * MM)
            if self.loft:
                lo, hi = op["gable"]["loft"]
                m = lo + round(F.u("open", wall.i, "loft") * (hi - lo))
                lw = loft["wMm"] * MM
                gap = 1.8 if m == 2 else 0.0
                for j in range(m):
                    cx = c + (j - (m - 1) / 2.0) * gap
                    add(wall, "loft", cx - lw / 2.0, self.z_loft + loft["sillOverFloorMm"] * MM, lw, loft["hMm"] * MM)
        # the back
        wall = self.walls[2]
        bk = op["back"]
        e = F.between(*rng(bk["edgeMm"]), "open", "back", "edge")
        nb = bk["windows"]
        for k in range(nb):
            x = e + (wall.L - 2 * e - ww) * (k / (nb - 1) if nb > 1 else 0.5)
            add(wall, "window", x, self.floors[0] + win["sillOverFloorMm"] * MM, ww, win["hMm"] * MM)
        self.openings = out

    def covered_by_lean_to(self, o):
        lt = self.lean_to
        if lt is None or o["wall"] != 2:
            return False
        # clear of its roof's overhang by the opening's casing and horns
        m = self.cw + 0.05 + 0.15 + 0.1
        return o["a1"] > lt["a0"] - m and o["a0"] < lt["a1"] + m and o["z0"] < lt["z_hi"] + 0.1

    # ---- cladding
    def wall_planar(self, wall, z0, z1, a0=-0.3, a1=None):
        a1 = wall.L + 0.3 if a1 is None else a1
        key = self.charts(f"wall/w{wall.i}", a1 - a0, z1 - z0)

        def f(p):
            return key, p.x - a0, p.z - z0
        return f

    def wall_top(self, wall, a):
        return self.z_top if wall.kind == "eave" else self.z_rake(a)

    def cladding(self, walls, group, z_start, cl, gaps, rake=None, z_end=None, mode="frame", place_of=None):
        """Every wall's boards course by course (near) and its planes (street). `gaps(wall, zb, zt)` gives the
        stretches along the wall a course must leave open (the openings, what an extension covers); `rake(wall)` its
        top's function along it, or None for a level top at z_end."""
        zs = self.courses[group]
        s = cl["stepMm"] * MM
        c = cl["butChamferMm"] * MM
        jc = 0.003
        blo, bhi = rng(cl["boardLengthMm"])
        for wall in walls:
            top = rake(wall) if rake else (lambda a, zz=z_end: zz)
            apex = max(top(a) for a in [wall.L * k / 20.0 for k in range(21)])
            planar = self.wall_planar(wall, self.z_drip0 - 0.05 if group == 0 else z_start - 0.05, apex + 0.35)
            place = place_of(wall) if place_of else wall.M
            for ci in range(len(zs) - 1):
                zb, zt = zs[ci], zs[ci + 1]
                if zb >= apex - 0.02:
                    break
                if not rake:
                    zt = min(zt, z_end)
                    if zb >= z_end - 0.01:
                        break
                # the course's reach along the wall at its foot and top: a gable's narrows to the rake
                ext = lambda z: self.reach(wall, top, z)  # noqa: E731
                lo_b, hi_b = ext(zb)
                if hi_b - lo_b < 0.06:
                    break
                spans = self.subtract([(lo_b, hi_b)], gaps(wall, zb, zt))
                # butt joints: boards 2.6 to 5.2 m, staggered by the seed
                for (a, b) in spans:
                    if b - a < 0.02:
                        continue
                    cuts, x = [], a - self.F.u(wall.i, group, "course", ci, "first") * bhi
                    k = 0
                    while True:
                        x += self.F.between(blo, bhi, wall.i, group, "course", ci, "len", k)
                        k += 1
                        if x >= b - 0.25:
                            break
                        if x > a + 0.25:
                            cuts.append(x)
                    pts = [a] + cuts + [b]
                    for j in cuts:
                        self.features["joints"].append((wall.i, j, zb, zt))
                    for bi in range(len(pts) - 1):
                        ba, bb = pts[bi], pts[bi + 1]
                        h = zt - zb
                        pc = self.make(f"clad/w{wall.i}/c{ci:02d}b{len(self.features['butts'])}", "cladding", ("near",),
                                       wall, mode, place, group)
                        prof = [(0.0, 0.0, "front", False), (0.0, s - c, "front", True), (c, s, "front", False),
                                (h, 0.0, "front", False)]
                        r0, r1 = (bi == 0 and abs(ba - lo_b) < 1e-6), (bi == len(pts) - 2 and abs(bb - hi_b) < 1e-6)
                        j0, j1 = bi > 0, bi < len(pts) - 2
                        ea, eb = ext(zb)

                        def cut0(p, q, ea=ea, r0=r0, j0=j0):
                            return (ext(zb + p)[0] - ea if r0 else 0.0) + (jc * q / s if j0 else 0.0)

                        def cut1(p, q, eb=eb, r1=r1, j1=j1):
                            return (ext(zb + p)[1] - eb if r1 else 0.0) - (jc * q / s if j1 else 0.0)
                        nseg = max(1, round((bb - ba) / 0.5))
                        extrude(pc, "near", prof, Vector((ba, 0.0, zb)), Vector((bb - ba, 0, 0)), Z, OUT, self.charts,
                                nseg=nseg, planar=planar, cut=(cut0, cut1), caps=(j0, j1))
                        if pc.mode == "rigid":
                            pc.anchor, pc.along = self.lean_to["anchor"], self.lean_to["along"]
                        self.features["butts"].append((wall.i, ba, bb, zb))
            # street level: the wall as planes in a grid round its openings, clipped to its top
            pc = self.make(f"clad/w{wall.i}/plane", "cladding", ("street",), wall, mode, place, group)
            if pc.mode == "rigid":
                pc.anchor, pc.along = self.lean_to["anchor"], self.lean_to["along"]
            z0 = zs[0]
            xs = {0.0, wall.L}
            zc = {z0, apex}
            gl = gaps(wall, None, None)
            for (a, b, za, zb_) in gl:
                xs |= {a, b}
                zc |= {za, zb_}
            if not rake:
                zc.add(z_end)
            xs = sorted(x for x in xs if 0.0 <= x <= wall.L)
            zc = sorted(z for z in zc if z0 <= z <= apex)
            ymid = -0.5 * s
            for i in range(len(xs) - 1):
                for j in range(len(zc) - 1):
                    xa, xb, za, zb_ = xs[i], xs[i + 1], zc[j], zc[j + 1]
                    mx, mz = (xa + xb) / 2.0, (za + zb_) / 2.0
                    if any(a <= mx <= b and z_a <= mz <= z_b for (a, b, z_a, z_b) in gl):
                        continue
                    if not rake and za >= z_end - 1e-6:
                        continue
                    nseg = max(1, round((xb - xa) / 0.5))
                    for k in range(nseg):
                        a = xa + (xb - xa) * k / nseg
                        b = xa + (xb - xa) * (k + 1) / nseg
                        poly = [Vector((a, ymid, za)), Vector((b, ymid, za)), Vector((b, ymid, zb_)), Vector((a, ymid, zb_))]
                        if rake:
                            poly = clip_top(poly, top)
                        if len(poly) >= 3:
                            cuv = [planar(p)[1:] for p in poly]
                            pc.add("street", Face(poly, cuv, planar(poly[0])[0], cuv))

    def reach(self, wall, top, z):
        """How far along a wall a course at height z runs: between where its top (a gable's rake, a lean-to's
        slope, or level) falls to z on either side of its highest point."""
        L = wall.L
        am = max((L * k / 40.0 for k in range(41)), key=top)

        def cross(lo, hi, rising):
            for _ in range(40):
                m = 0.5 * (lo + hi)
                if (top(m) < z) == rising:
                    lo = m
                else:
                    hi = m
            return 0.5 * (lo + hi)
        a0 = 0.0 if top(0.0) >= z else cross(0.0, am, True)
        a1 = L if top(L) >= z else cross(am, L, False)
        return (a0, a1)

    @staticmethod
    def subtract(spans, gaps):
        out = spans
        for (g0, g1) in gaps:
            nxt = []
            for (a, b) in out:
                if g1 <= a or g0 >= b:
                    nxt.append((a, b))
                    continue
                if g0 > a:
                    nxt.append((a, g0))
                if g1 < b:
                    nxt.append((g1, b))
            out = nxt
        return out

    def opening_gaps(self, wall, zb, zt):
        """The stretches a course leaves open on `wall` (zb, zt the course; None for all of them as boxes)."""
        boxes = []
        for o in self.openings:
            if o["wall"] != wall.i or o.get("covered"):
                continue
            z_lo = o["z0"] - (0.0 if o["kind"] == "door" else self.sill_t)
            z_hi = o["z1"] + self.head_h + self.cap_t
            if zb is None:
                boxes.append((o["a0"], o["a1"], max(z_lo, self.courses[0][0]), o["z1"]))
            elif zt > z_lo + 0.005 and zb < z_hi - 0.005:
                boxes.append((o["a0"], o["a1"]))
        lt = self.lean_to
        if lt is not None and wall.i == 2:
            if zb is None:
                boxes.append((lt["a0"], lt["a1"], self.courses[0][0], lt["z_hi"] - 0.02))
            elif zt < lt["z_hi"] - 0.02:
                boxes.append((lt["a0"], lt["a1"]))
        return boxes

    # ---- corner boards and drip boards
    def corner_boards(self):
        cb = self.W["corner"]
        w = cb["widthMm"] * MM
        proud = cb["proudMm"] * MM * self.push["trimProud"]
        c = self.ch["corner"]
        s = self.step
        z0, z1 = self.z_drip1 - 0.01, self.z_top
        H = z1 - z0
        for wall in self.walls:
            for end in (0, 1):
                if wall.kind == "eave":
                    # the eave wall's board covers the gable board's edge, so its outer arris is the house's corner
                    x = -(s + proud) if end == 0 else wall.L - w
                    width = w + s + proud
                    ce = (True, True)
                else:
                    x = -s if end == 0 else wall.L - w
                    width = w + s
                    ce = (end == 1, end == 0)
                self.trim(f"corner/w{wall.i}e{end}", wall, Vector((x, -s, z0)), Vector((0, 0, H)), ALONG, OUT, width,
                          proud, c, nseg=4, groups=("left", "front", "right"), chamfer_edges=ce, caps=(False, False))
        self.cb = (w, proud)

    def drip_boards(self):
        dr = self.W["dripBoard"]
        h = dr["heightMm"] * MM
        proud = dr["proudMm"] * MM
        c = self.ch["drip"]
        for wall in self.walls:
            a, b = (-(proud + self.step), wall.L + proud + self.step) if wall.kind == "eave" else (0.0, wall.L)
            spans = [(a, b)]
            for o in self.openings:
                if o["wall"] == wall.i and o["kind"] == "door":
                    spans = self.subtract(spans, [(o["a0"] - self.cw, o["a1"] + self.cw)])
            for k, (sa, sb) in enumerate(spans):
                self.trim(f"drip/w{wall.i}s{k}", wall, Vector((sa, -self.step, self.z_drip0)), Vector((sb - sa, 0, 0)),
                          Z, OUT, h, proud + self.step, c, nseg=max(1, round((sb - sa) / 0.75)),
                          groups=("bottom", "front", "top"), caps=(wall.kind == "eave" or k > 0, wall.kind == "eave" or k < len(spans) - 1))

    # ---- an opening's surround: moulded casing legs, the head's frieze, cap and bed mould, the horned sill
    def surround(self, o, k):
        W = self.W
        cs = W["casing"]
        wall = self.walls[o["wall"]] if o["wall"] < len(self.walls) else self.lt_walls[o["wall"] - len(self.walls)]
        mode = "rigid" if o.get("leanTo") else "frame"
        place = self.lt_place(wall) if o.get("leanTo") else wall.M
        made = self.F.built if not o.get("leanTo") else self.lean_to["year"]
        cv = self.version("casing", made)
        hv = self.version("head", made)
        sv = self.version("sill", made)
        x0, x1, za, zo1 = o["a0"], o["a1"], o["z0"], o["z1"]
        zb = zo1 + self.head_h
        p = self.trim_proud
        y0 = -self.step * 0.5
        tag = f"open{k}"
        cw = max(pt[0] for pt in cv["profileMm"]) * MM
        o["cw"] = cw
        # the legs: the version's moulding swept up each side, its opening edge toward the opening
        prof = data_profile(cv["profileMm"], self.push["trimProud"])
        flat = [(0.0, 0.0, "left", False), (0.0, p, "front", False), (cw, p, "right", False), (cw, 0.0, "right", False)]
        for side, xo, P in (("l", x0 - cw, ALONG), ("r", x1 + cw, -ALONG)):
            pc = self.make(f"{tag}/casing/{side}", "trims", ("near", "street"), wall, mode, place)
            for lv in ("near", "street"):
                extrude(pc, lv, prof if lv == "near" else flat, Vector((xo, y0, za)), Vector((0, 0, zb - za)), P, OUT,
                        self.charts, nseg=2, nominal={"front": cw, "left": p, "right": p})
            self.rigid_lt(pc, o)
        # the head's frieze between them
        pc = self.trim(f"{tag}/casing/head", wall, Vector((x0, y0, zo1)), Vector((x1 - x0, 0, 0)), Z, OUT,
                       zb - zo1, p * 0.8, 0.006, caps=(False, False), mode=mode, place=place)
        self.rigid_lt(pc, o)
        # the cap: a water board over the whole surround, sloped to shed water, with a bed mould under it if its
        # version has one
        capw = (x1 + cw) - (x0 - cw) + 2 * 0.03
        cproud = hv["capProudMm"] * MM * self.push["capProud"]
        self.cap(tag, wall, place, mode, x0 - cw - 0.03, capw, zb, cproud, self.cap_t, math.radians(cs["capSlopeDeg"]), o)
        if hv.get("bedMould"):
            bm = cs["bedMouldMm"]
            pc = self.trim(f"{tag}/casing/bed", wall, Vector((x0 - cw - 0.01, y0 - p, zb - bm[1] * MM)),
                           Vector((capw - 0.04, 0, 0)), Z, OUT, bm[1] * MM, bm[0] * MM, self.ch["bedMould"],
                           caps=(True, True), chamfer_edges=(True, False), mode=mode, place=place)
            self.rigid_lt(pc, o)
        feat = {"casing": [x0 - cw, x1 + cw, za, zb + self.cap_t], "versions": {"casing": cv["id"], "head": hv["id"], "sill": sv["id"]}}
        if o["kind"] != "door":
            horn = sv["hornMm"] * MM
            sp = cs["sillProudMm"] * MM * self.push["sillProud"]
            sx0, sx1 = x0 - cw - horn, x1 + cw + horn
            self.sill(tag, wall, place, mode, sx0, sx1 - sx0, za, sp, self.sill_t, o)
            feat["sill"] = [sx0, sx1, za - self.sill_t, sp]
            # the sill's fall along its length, from the frame: water leaves it at its lower end
            if not o.get("leanTo"):
                a = wall.M @ Vector((sx0, 0, za))
                b = wall.M @ Vector((sx1, 0, za))
                feat["tilt"] = (self.frame.offset(b).z - self.frame.offset(a).z) / (sx1 - sx0)
            else:
                feat["tilt"] = 0.0
        else:
            # the door's threshold: a hardwood board across the opening from the stones to the floor
            z_st = self.z_plinth if not o.get("leanTo") else za - 0.05
            pc = self.trim(f"{tag}/threshold", wall, Vector((x0 - cw, y0 + 0.02, z_st)), Vector((x1 - x0 + 2 * cw, 0, 0)),
                           Z, OUT, za - z_st, 0.05, 0.006, caps=(True, True), mode=mode, place=place)
            self.rigid_lt(pc, o)
            feat["tilt"] = 0.0
            if not o.get("leanTo") and za > 0.3:
                self.steps(tag, wall, x0 - cw, x1 + cw, za - 0.012)
        self.reveal(tag, wall, place, mode, o, y0 - p)
        o.update(feat)

    def reveal(self, tag, wall, place, mode, o, y_face):
        """What stands behind an opening's casing: its frame, set back by the working's reveal, and the reveal's four
        sides; a gap in a boarding shows the frame, never a hole."""
        x0, x1, za, zb = o["a0"], o["a1"], o["z0"], o["z1"]
        yb = y_face + self.W["casing"]["revealMm"] * MM
        pc = self.make(f"{tag}/reveal", "trims", ("near", "street"), wall, mode, place)
        key = self.charts(f"h{self.F.id}/{tag}/reveal", (x1 - x0) + 2 * (yb - y_face) + 0.02, (zb - za) + 2 * (yb - y_face) + 0.02)
        r = yb - y_face

        def cu(p):
            return (p.x - x0 + r + 0.01, p.z - za + r + 0.01)
        quads = [[Vector((x0, yb, za)), Vector((x1, yb, za)), Vector((x1, yb, zb)), Vector((x0, yb, zb))],
                 [Vector((x0, y_face, za)), Vector((x0, yb, za)), Vector((x0, yb, zb)), Vector((x0, y_face, zb))],
                 [Vector((x1, yb, za)), Vector((x1, y_face, za)), Vector((x1, y_face, zb)), Vector((x1, yb, zb))],
                 [Vector((x0, y_face, zb)), Vector((x0, yb, zb)), Vector((x1, yb, zb)), Vector((x1, y_face, zb))],
                 [Vector((x0, yb, za)), Vector((x0, y_face, za)), Vector((x1, y_face, za)), Vector((x1, yb, za))]]
        # a window open to the street shows its window in the frame's place; a door and a boarded window the plane
        glazed = not o["boarded"] and o["kind"] != "door"
        for lv in ("near", "street"):
            for q in quads[1:] if glazed else quads:
                pc.add(lv, Face(q, [cu(p) for p in q], key, [cu(p) for p in q]))
        # from afar the reveal's sides too shallow to see: the frame where it stands behind a boarding (the sheets close
        # the reveal), else flush with the casing's back, so no side opens a crack
        q = quads[0] if o["boarded"] else [Vector((p.x, y_face, p.z)) for p in quads[0]]
        pc.city = [Face(q, [cu(p) for p in quads[0]], key, [cu(p) for p in quads[0]])]
        self.rigid_lt(pc, o)
        if glazed:
            self.window(tag, wall, place, o, yb, key, cu)

    # ---- the window: its version's frame, sashes, bars, putty or beads and panes, in the frame's place
    def window(self, tag, wall, place, o, yb, key, cu):
        """The window of the opening's making (versions.window), set in the reveal at its back. Its frame's outer edge
        runs on behind the reveal's sides and the casing, so no crack opens between them; a post and a transom split
        it; each sash fills its frame's opening, set back from the frame's face by the rebate's shoulder, so the joint
        between them is that step's line of shade, never an open slot (a slot finer than a pixel at the near level's
        farthest flickers as dashes); a fixed light is glazed in the frame itself. Each light's glass lies
        in its rebate, the putty sloping down to it from the wood's face (a bead's square edge instead, set in the
        rebate). The street level keeps the frame, sashes and bars, the sashes tight in their openings and the glass
        flush with their faces; the city level keeps the reveal's flush plane. Every wooden face is a trim on the
        reveal's chart, so the page paints it as the opening's; the window is one rigid thing, moved and turned with
        its wall but never bent. Its panes are glass: uv0 metres from the window's centre and foot, and their vertex
        colour R its glass's kind (glass.json kinds, by the year it was made: the integer part of R x 4) with the
        window's own seed (the room behind it, the fraction), G the pane's seed (its waves), B the window's width / 4 m
        and A its height / 3 m."""
        F = self.F
        v = self.version("window", o["made"], o["eraOf"])
        x0, x1, za, zb = o["a0"], o["a1"], o["z0"], o["z1"]
        # what shows of the joinery: the casing laps the frame's outer edge and each sash laps its rebate in the frame
        # and the post, so the frame shows a strip and the post little or none; a sash's sightline (stile, rail, bar)
        # holds its putty or bead, so its wood shows that much narrower at near level
        lap = v["lapMm"] * MM
        fw = (v["frameMm"][0] - v["coverMm"] - v["lapMm"]) * MM
        sw, bw = v["sashMm"][0] * MM, v["barMm"][0] * MM
        brail = sw * v["bottomRail"]
        back, reb, gl = v["setBackMm"] * MM, v["rebateMm"] * MM, v["glazing"]
        pm = gl["mm"][0] * MM
        ext = 0.012
        kinds = self.M["glass"]["kinds"]
        names = [k for k in kinds if k != "describes"]
        gk = next((k for k in names if kinds[k]["years"][0] <= o["made"] <= kinds[k]["years"][1]), names[-1])
        o["window"], o["glass"] = v["id"], gk
        cx = (x0 + x1) / 2.0
        r_room = (names.index(gk) + 0.05 + 0.9 * F.u(tag, "room")) / 4.0
        size = [(x1 - x0) / 4.0, (zb - za) / 3.0]
        anchor, along = place @ Vector((cx, yb, (za + zb) / 2.0)), place.to_3x3() @ ALONG
        near, street, both = ("near",), ("street",), ("near", "street")

        def piece(name, mat):
            pc = self.make(f"{tag}/window/{name}", mat, both, wall, "rigid", place)
            pc.no_city = True
            if o.get("leanTo"):
                self.rigid_lt(pc, o)
            else:
                pc.anchor, pc.along = anchor, along
            return pc

        def front(pc, lvs, r, y):
            """A member's face: its grain along its length."""
            q = [Vector((r[0], y, r[1])), Vector((r[2], y, r[1])), Vector((r[2], y, r[3])), Vector((r[0], y, r[3]))]
            up = r[3] - r[1] > r[2] - r[0]
            for lv in lvs:
                pc.add(lv, Face(q, [(p.z, p.x) if up else (p.x, p.z) for p in q], key, [cu(p) for p in q]))

        def ring(pc, lvs, a, ya, b, yb_, out=False):
            """Four faces from rectangle `a` at depth `ya` to `b` at `yb_`, each turned to the front and in toward the
            rectangles' middle (out from it if `out`)."""
            ca = [(a[0], a[1]), (a[2], a[1]), (a[2], a[3]), (a[0], a[3])]
            cb = [(b[0], b[1]), (b[2], b[1]), (b[2], b[3]), (b[0], b[3])]
            inward = (Vector((0, 0, 1)), Vector((-1, 0, 0)), Vector((0, 0, -1)), Vector((1, 0, 0)))
            for k in range(4):
                j = (k + 1) % 4
                q = [Vector((ca[k][0], ya, ca[k][1])), Vector((ca[j][0], ya, ca[j][1])),
                     Vector((cb[j][0], yb_, cb[j][1])), Vector((cb[k][0], yb_, cb[k][1]))]
                if newell(q).length < 1e-10:
                    continue
                if newell(q).dot(inward[k] * (-1.0 if out else 1.0) + Vector((0, -0.3, 0))) < 0:
                    q = q[::-1]
                along_x = k % 2 == 0
                for lv in lvs:
                    pc.add(lv, Face(q, [((p.x if along_x else p.z), p.y) for p in q], key, [cu(p) for p in q]))

        panes = []

        def glaze(wood, pkey, jobs):
            """Each light's putty or bead and its glass. `jobs`: a level, its lights, the wood's face and whether the
            glass lies in its rebate (else flush with the face, filling the light)."""
            g = piece(f"glass/{pkey}", "glass")
            for lv, lights, y, full in jobs:
                for li, L in enumerate(lights):
                    R, yg = L, y
                    if full and gl["kind"] == "putty":
                        R, yg = inset(L, gl["mm"][0] * MM), y + reb
                        ring(wood, (lv,), L, y + 0.0005, R, yg)
                    elif full:
                        bwid, bh = gl["mm"][0] * MM, gl["mm"][1] * MM
                        R, yg = inset(L, bwid), y + reb
                        ring(wood, (lv,), L, y, L, yg - bh)
                        ring(wood, (lv,), L, yg - bh, R, yg - bh)
                        ring(wood, (lv,), R, yg - bh, R, yg)
                    if lv == "near":
                        panes.append(R)
                    q = [Vector((R[0], yg, R[1])), Vector((R[2], yg, R[1])), Vector((R[2], yg, R[3])), Vector((R[0], yg, R[3]))]
                    g.add(lv, Face(q, [(p.x - cx, p.z - za) for p in q], key, [cu(p) for p in q],
                                   col=[r_room, F.u(tag, "pane", pkey, li)] + size))

        # the frame: its sides the full height, the head and foot between them, the post between those, the transom
        # either side of the post
        fr = piece("frame", "trims")
        I = (x0 + fw, za + fw, x1 - fw, zb - fw)
        for r in ((x0 - ext, za - ext, I[0], zb + ext), (I[2], za - ext, x1 + ext, zb + ext),
                  (I[0], za - ext, I[2], I[1]), (I[0], I[3], I[2], zb + ext)):
            front(fr, both, r, yb)
        sashes, tops = v["sashes"], v.get("topLights") or []
        mw = max(0.0, v["postMm"] * MM - 2.0 * lap) if v.get("mullion") else 0.0
        n = len(sashes)
        span = I[2] - I[0] - (n - 1) * mw
        cols, x = [], I[0]
        for s in sashes:
            cols.append((x, x + span * s["w"]))
            x += span * s["w"] + mw
        zt, tf = I[3], 0.0
        if v.get("transom"):
            tf = max(0.0, v["transom"]["faceMm"] * MM - 2.0 * lap)
            zt = I[3] - v["transom"]["share"] * (I[3] - I[1] - tf) - tf
            for a, b in cols:
                front(fr, both, (a, zt, b, zt + tf), yb)
        if mw > 0:
            for k in range(1, n):
                front(fr, both, (cols[k - 1][1], I[1], cols[k][0], I[3]), yb)
        # the frame's openings: each a sash's (or a fixed light's), and the top lights' over the transom
        cells = [((a, I[1], b, zt), s) for (a, b), s in zip(cols, sashes)]
        if v.get("transom"):
            cells += [((a, zt + tf, b, I[3]), s) for (a, b), s in zip(cols, tops)]
        if not mw and n > 1:
            # casements meeting without a post: one opening in the frame, the sashes a gap apart in it
            low = [c for c in cells if c[0][3] <= zt + 1e-6]
            holes = [((cols[0][0], I[1], cols[-1][1], zt), low)] + [(c[0], [c]) for c in cells if c not in low]
        else:
            holes = [(c[0], [c]) for c in cells]
        y_s = yb + back
        for hi, (hole, inside) in enumerate(holes):
            if all(s.get("fixed") for _, s in inside):
                for k, (cell, s) in enumerate(inside):
                    lights, _ = sash_grid(cell, s, bw, v, cell[3] - cell[1])
                    glaze(fr, f"{hi}.{k}", [("near", lights, yb, True), ("street", lights, yb, False)])
                continue
            ring(fr, both, hole, yb, hole, y_s)
            for k, (cell, s) in enumerate(inside):
                sp = piece(f"sash{hi}.{k}", "trims")
                jobs = []
                for lv, R, c in (("near", cell, pm), ("street", cell, 0.0)):
                    a, ar = sw - c, brail - c
                    for r in ((R[0], R[1], R[0] + a, R[3]), (R[2] - a, R[1], R[2], R[3]),
                              (R[0] + a, R[1], R[2] - a, R[1] + ar), (R[0] + a, R[3] - a, R[2] - a, R[3])):
                        front(sp, (lv,), r, y_s)
                    inner = (R[0] + a, R[1] + ar, R[2] - a, R[3] - a)
                    lights, bars = sash_grid(inner, s, bw - 2.0 * c, v, cell[3] - cell[1] - sw - brail)
                    for r in bars:
                        front(sp, (lv,), r, y_s)
                    jobs.append((lv, lights, y_s, lv == "near"))
                glaze(sp, f"{hi}.{k}", jobs)
        # the glass's share of the opening (inside the casing), across its widest row of panes and by area: the
        # sightlines checked against the references'
        o["glassAcross"] = round(max(sum(Q[2] - Q[0] for Q in panes if Q[1] <= (R[1] + R[3]) / 2.0 <= Q[3])
                                     for R in panes) / (x1 - x0), 3)
        o["glassArea"] = round(sum((R[2] - R[0]) * (R[3] - R[1]) for R in panes) / ((x1 - x0) * (zb - za)), 3)

    def steps(self, tag, wall, x0, x1, z_top):
        """Split stone steps up to a door: as many risers as its height needs, each slab one going deeper than the
        one above it; rigid, set on the ground."""
        st = self.W["steps"]
        F = self.F
        n = max(1, round(z_top / (0.5 * (st["riserMm"][0] + st["riserMm"][1]) * MM)))
        go = st["goingMm"] * MM
        past = F.between(*rng(st["pastDoorMm"]), tag, "steps", "past")
        y_wall = -self.step - 0.012
        for k in range(n):
            ztk = z_top * (k + 1) / n
            depth = go * (n - k)
            jog = (F.u(tag, "steps", k, "jog") - 0.5) * 0.04
            sa, sb = x0 - past + jog, x1 + past + jog
            pc = self.make(f"{tag}/step{k}", "stone", ("near", "street"), wall, "rigid")
            for lv in ("near", "street"):
                prof = rect_profile(ztk, depth, 0.012 if lv == "near" else 0.0, groups=("back", "front", "top", "under"),
                                    chamfer_edges=(False, True))
                extrude(pc, lv, prof, Vector((sa, y_wall, 0.0)), Vector((sb - sa, 0, 0)), Z, OUT, self.charts,
                        caps=(True, True), nominal={"front": ztk, "top": depth})
            pc.anchor = wall.M @ Vector(((sa + sb) / 2, y_wall, 0.0))
            pc.along = wall.M.to_3x3() @ ALONG

    def rigid_lt(self, pc, o):
        if o.get("leanTo"):
            pc.anchor, pc.along = self.lean_to["anchor"], self.lean_to["along"]

    def cap(self, tag, wall, place, mode, x, length, z, proud, t, slope, o):
        c = self.ch["cap"]
        ct = self.ch["capTop"]
        dw, dh = rng(self.W["casing"]["capDripMm"])
        pc = self.make(f"{tag}/casing/cap", "trims", ("near", "street"), wall, mode, place)
        d = proud
        rise = d * math.tan(slope)
        for lv in ("near", "street"):
            if lv == "near":
                prof = [(0.0, 0.0, "bottom", False), (0.0, d - dw, "bottom", False), (-dh, d - dw, "bottom", False),
                        (-dh, d - c, "front", True), (-dh + c, d, "front", False),
                        (t - ct, d, "front", True), (t + rise * ct / d, d - ct, "top", False), (t + rise, 0.0, "top", False)]
            else:
                prof = [(0.0, 0.0, "bottom", False), (-dh, d, "front", False), (t, d, "top", False), (t + rise, 0.0, "top", False)]
            extrude(pc, lv, prof, Vector((x, -self.step * 0.5, z)), Vector((length, 0, 0)), Z, OUT, self.charts, nseg=2,
                    caps=(True, True), nominal={"bottom": d, "front": t, "top": math.hypot(d, rise)})
        self.rigid_lt(pc, o)

    def sill(self, tag, wall, place, mode, x, length, ztop, proud, t, o):
        c = self.ch["sill"]
        pc = self.make(f"{tag}/casing/sill", "trims", ("near", "street"), wall, mode, place)
        fall = 0.012
        for lv in ("near", "street"):
            if lv == "near":
                prof = [(-t, 0.0, "bottom", False), (-t, proud - 0.004, "front", True), (-t + 0.004, proud, "front", False),
                        (-fall - c, proud, "front", True), (-fall, proud - c, "top", False), (0.0, 0.0, "top", False)]
            else:
                prof = [(-t, 0.0, "bottom", False), (-t, proud, "front", False), (-fall, proud, "top", False), (0.0, 0.0, "top", False)]
            extrude(pc, lv, prof, Vector((x, -self.step * 0.5, ztop)), Vector((length, 0, 0)), Z, OUT, self.charts, nseg=2,
                    caps=(True, True), nominal={"bottom": proud, "front": t, "top": proud})
        self.rigid_lt(pc, o)

    # ---- the boarding: sheets inside the casing, battens nailed across it; rough, rigid, proud
    def boarding(self, o, k):
        bd = self.W["boarding"]
        F = self.F
        wall = self.walls[o["wall"]] if o["wall"] < len(self.walls) else self.lt_walls[o["wall"] - len(self.walls)]
        place = self.lt_place(wall) if o.get("leanTo") else wall.M
        x0, x1, za, zb = o["a0"], o["a1"], o["z0"], o["z1"]
        t = bd["sheetThickMm"] * MM
        tag = f"open{k}"
        top_gap = F.between(*bd["topGapMm"], tag, "topgap") * MM
        y_set = -self.step * 0.5 - self.trim_proud
        door = o["kind"] == "door"
        n = bd["sheetsHigh"] if (zb - za) > 1.0 else 1
        hs = zb - za - top_gap
        split = 0.45 + 0.2 * F.u(tag, "split")
        heights = [hs * split, hs * (1 - split)] if n == 2 else [hs]
        z = za + 0.002
        sheets = []
        for i, h in enumerate(heights):
            g = F.between(*bd["sideGapMm"], tag, "sheet", i, "gap") * MM
            y_face = y_set + F.between(*bd["setBackMm"], tag, "sheet", i, "setback") * MM
            pc = self.make(f"{tag}/board/sheet{i}", "sheet", ("near", "street"), wall, "rigid", place)
            sx0, sx1 = x0 + g * 0.5, x1 - g * 0.5
            for lv in ("near", "street"):
                cc = self.ch["sheet"] if lv == "near" else 0.0
                prof = rect_profile(h - 0.003, t, cc, groups=("bottom", "front", "top", "back"))
                extrude(pc, lv, prof, Vector((sx0, y_face + t, z)), Vector((sx1 - sx0, 0, 0)), Z, OUT, self.charts,
                        caps=(True, True), nominal={"front": h - 0.003, "bottom": t, "top": t})
            pc.anchor = place @ Vector(((sx0 + sx1) / 2, y_face, z + h / 2))
            pc.along = place.to_3x3() @ ALONG
            sheets.append([sx0, sx1, z, z + h])
            z += h
        o["sheets"] = [x0, x1, za, zb - top_gap, y_set + bd["setBackMm"][0] * MM]
        # battens across the casing, past it onto the cladding, out of level by the hand that nailed them; a door's
        # middle one on the diagonal
        bt = bd["battens"]
        th = bt["thickMm"] * MM
        y_b = -self.step * 0.5 - self.trim_proud
        span = zb - za
        count = bd["door"]["battens"] if door else bt["count"]
        # a batten reaches past the casing only as far as the cladding is free: it stops short of the next opening's
        # casing (half the gap, so two neighbours' ends never meet) and of the corner board
        lo, hi = (self.cb[0], wall.L - self.cb[0]) if not o.get("leanTo") else (0.0, wall.L)
        for q in self.openings:
            if q is o or q["wall"] != o["wall"] or bool(q.get("leanTo")) != bool(o.get("leanTo")):
                continue
            if q["a1"] <= x0:
                lo = max(lo, (q["a1"] + q.get("cw", self.cw) + x0 - o["cw"]) / 2)
            elif q["a0"] >= x1:
                hi = min(hi, (x1 + o["cw"] + q["a0"] - q.get("cw", self.cw)) / 2)
        room = (max(0.0, x0 - o["cw"] - lo - 0.03), max(0.0, hi - x1 - o["cw"] - 0.03))
        o["battens"], o["nails"] = [], []
        for i in range(count):
            w = F.between(*bt["widthMm"], tag, "batten", i, "width") * MM
            diag = door and bd["door"].get("diagonal") and i == 1
            if door:
                zc = za + span * (0.18 + 0.32 * i) + (F.u(tag, "batten", i, "z") - 0.5) * 0.1
            else:
                zc = za + span * (0.28 + 0.46 * i) + (F.u(tag, "batten", i, "z") - 0.5) * 0.12
            if diag:
                bx0, bx1 = x0 + 0.02, x1 - 0.02
                rise = span * 0.42
                tilt = math.atan2(rise, bx1 - bx0) * (1 if F.u(tag, "diag") < 0.5 else -1)
                zc = za + span * 0.5
            else:
                pl = min(room[0], F.between(*bt["pastCasingMm"], tag, "batten", i, "left") * MM)
                pr = min(room[1], F.between(*bt["pastCasingMm"], tag, "batten", i, "right") * MM)
                bx0, bx1 = x0 - o["cw"] - pl, x1 + o["cw"] + pr
                tilt = math.radians(F.between(*bt["outOfLevelDeg"], tag, "batten", i, "tilt")) * (1 if F.u(tag, "batten", i, "sign") < 0.5 else -1)
            length = (bx1 - bx0) / math.cos(tilt)
            pc = self.make(f"{tag}/board/batten{i}", "batten", ("near", "street"), wall, "rigid", place)
            L = Vector((math.cos(tilt), 0, math.sin(tilt))) * length
            o_ = Vector((bx0, y_b - (th if diag else 0.0), zc - w / 2 - math.tan(tilt) * (bx1 - bx0) / 2))
            o["battens"].append([bx0, bx1, zc, math.tan(tilt), w])
            ec = bt["endCutDeg"]
            ends = [(math.tan(math.radians(F.between(-ec[0], ec[0], tag, "batten", i, e, "face"))),
                     math.tan(math.radians(F.between(-ec[1], ec[1], tag, "batten", i, e, "through")))) for e in ("start", "end")]
            cut = tuple((lambda p, q, a=a, b=b, w=w: a * (p - w / 2) + b * (q - th / 2)) for a, b in ends)
            for lv in ("near", "street"):
                cc = self.ch["batten"] if lv == "near" else 0.0
                prof = rect_profile(w, th, cc, groups=("bottom", "front", "top", "back"))
                extrude(pc, lv, prof, o_, L, Vector((-math.sin(tilt), 0, math.cos(tilt))), OUT, self.charts,
                        caps=(True, True), cut=cut, nominal={"front": w, "bottom": th, "top": th})
            pc.anchor = place @ Vector(((bx0 + bx1) / 2, y_b, zc))
            pc.along = place.to_3x3() @ ALONG
            # nails: two at each casing it crosses (on a diagonal, at its ends on the sheet)
            xs = ((x0 + 0.06, x1 - 0.06) if diag else (x0 - o["cw"] / 2, x1 + o["cw"] / 2))
            for side, xc in zip(("l", "r"), xs):
                for kk in range(bt["nailsPerEnd"]):
                    zz = zc + (math.tan(tilt) * (xc - (bx0 + bx1) / 2)) + (kk - 0.5) * w * 0.5
                    o["nails"].append([xc + (F.u(tag, "nail", i, side, kk) - 0.5) * 0.04, zz])

    # ---- the plinth: split fieldstone, rigid, a long corner stone bonding each corner, the runs between
    def plinth(self):
        pl = self.W["plinth"]
        F = self.F
        zt = self.z_plinth
        y_face = -self.step - 0.012
        e = -y_face
        n = len(self.walls)
        # each corner's stone runs along one of its two walls (the seed's), its end the other's face
        corner = []
        for i in range(n):
            j = (i + 1) % n
            along_i = F.u("plinth", "corner", i, "which") < 0.5
            Lc = F.between(*rng(pl["cornerStoneMm"]), "plinth", "corner", i, "len")
            Dc = F.between(*rng(pl["cornerReturnMm"]), "plinth", "corner", i, "ret")
            corner.append((i, j, along_i, Lc, Dc))
        runs = {i: [0.0, self.walls[i].L] for i in range(n)}
        jm = lambda *k: F.between(*rng(pl["jointMm"]), "plinth", *k, "joint")  # noqa: E731
        for (i, j, along_i, Lc, Dc) in corner:
            wi, wj = self.walls[i], self.walls[j]
            if along_i:
                # along wall i's end, its end face on wall j's start
                self.stone(f"plinth/k{i}", wi, wi.L - Lc, wi.L + e, zt, y_face, end=(1, wj, Dc))
                runs[i][1] = wi.L - Lc - jm("ci", i)
                runs[j][0] = Dc - e + jm("cj", i)
            else:
                # along wall j's start, its start face on wall i's end
                self.stone(f"plinth/k{i}", wj, -e, Lc, zt, y_face, end=(0, wi, Dc))
                runs[j][0] = Lc + jm("cj", i)
                runs[i][1] = wi.L - (Dc - e) - jm("ci", i)
        for wall in self.walls:
            a, b = runs[wall.i]
            # stones between, their lengths drawn and then fitted so the last meets the corner stone
            ls, x = [], a
            while x < b:
                ls.append(F.between(*rng(pl["stoneMm"]), "plinth", wall.i, len(ls), "len"))
                x += ls[-1] + 0.014
            joints = [jm(wall.i, k) for k in range(len(ls))]
            k = (b - a - sum(joints[:-1])) / sum(ls) if ls else 1.0
            x = a
            for si, L in enumerate(ls):
                L *= k
                self.stone(f"plinth/w{wall.i}/s{si}", wall, x, x + L, zt, y_face)
                x += L + joints[si]
            # the mortar's bed, set back behind the stones' faces
            pc = self.make(f"plinth/w{wall.i}/mortar", "stone", ("near", "street"), wall)
            yb = y_face + pl["jointBackMm"] * MM
            key = self.charts(f"plinth/w{wall.i}", wall.L + 0.6, zt + 0.05)
            self.city_plinth.append((wall, y_face, e, zt, key))
            for lv in ("near", "street"):
                pts = [Vector((0.0, yb, 0.0)), Vector((wall.L, yb, 0.0)), Vector((wall.L, yb, zt)), Vector((0.0, yb, zt))]
                cuv = [(p.x + 0.3, p.z) for p in pts]
                pc.add(lv, Face(pts, cuv, key, cuv, under=True))

    def stone(self, sid, wall, a, b, zt, y_face, end=None):
        """A split stone between a and b along its wall: a pillowed face worn back at its arris, its sides into the
        joint. A corner stone (`end`: which end, the other wall, its return) shows its end on the other wall as a
        second face."""
        pl = self.W["plinth"]
        F = self.F
        bulge = F.between(*rng(pl["faceBulgeMm"]), sid, "bulge")
        arr = F.between(*rng(pl["arrisMm"]), sid, "arris")
        h = zt - 0.004
        pc = self.make(sid, "stone", ("near", "street"), wall, "rigid")
        set_out = F.between(*rng(pl["setOutMm"]), sid, "out")
        yf = y_face - set_out
        key = self.charts(f"plinth/w{wall.i}", wall.L + 0.6, zt + 0.05)

        def cu(p):
            return (p.x + 0.3, p.z)
        self.pillow(pc, sid, a, b, yf, h, bulge, arr, key, cu, lambda u, v, a=a, b=b: Vector((a + (b - a) * u, yf, v)),
                    Vector((0, -1, 0)))
        if end is not None:
            which, other, D = end
            x = b if which == 1 else a
            ko = self.charts(f"plinth/w{other.i}", other.L + 0.6, zt + 0.05)
            M = wall.M

            def cu2(p, other=other, M=M):
                return (other.along(M @ p) + 0.3, p.z)
            # the end face runs from the stone's face back into the wall by D, facing along +x (or -x)
            sgn = 1.0 if which == 1 else -1.0
            if which == 1:
                f = lambda u, v: Vector((x, yf + D * u, v))  # noqa: E731
            else:
                f = lambda u, v: Vector((x, yf + D * (1.0 - u), v))  # noqa: E731
            self.pillow(pc, sid + "e", 0.0, D, yf, h, bulge, arr, ko, cu2, f, Vector((sgn, 0, 0)))
        pc.anchor = wall.M @ Vector(((a + b) / 2, yf, 0.0))
        pc.along = wall.M.to_3x3() @ ALONG

    def pillow(self, pc, sid, a, b, yf, h, bulge, arr, key, cu, at, nrm):
        """A split face over the unit square `at(u, v)` (v in metres up): high in its middle, its border worn back
        by the arris, then its sides 30 mm back into the joint."""
        F = self.F
        for lv in ("near", "street"):
            ar = arr if lv == "near" else 0.0
            nx, nz = (3, 2) if lv == "near" else (1, 1)
            L = b - a
            uu = lambda i: (ar + (L - 2 * ar) * i / nx) / L  # noqa: E731
            grid = []
            for j in range(nz + 1):
                row = []
                for i in range(nx + 1):
                    u, v = i / nx, j / nz
                    lump = bulge * (math.sin(math.pi * u) * math.sin(math.pi * v)) ** 0.7 * (0.75 + 0.5 * F.u(sid, "lump", i, j))
                    row.append(at(uu(i), ar + (h - 2 * ar) * v) + nrm * lump)
                grid.append(row)
            if lv == "street":
                c = at(0.5, h / 2) + nrm * bulge * 0.8
                ring = [at(0.0, 0.004), at(1.0, 0.004), at(1.0, h), at(0.0, h)]
                for i in range(4):
                    pts = [ring[i], ring[(i + 1) % 4], c]
                    if newell_dot(pts, nrm) < 0:
                        pts = pts[::-1]
                    pc.add(lv, Face(pts, [cu(p) for p in pts], key, [cu(p) for p in pts]))
                continue
            flip = None
            for j in range(nz):
                for i in range(nx):
                    pts = [grid[j][i], grid[j][i + 1], grid[j + 1][i + 1], grid[j + 1][i]]
                    if flip is None:
                        flip = newell_dot(pts, nrm) < 0
                    if flip:
                        pts = pts[::-1]
                    pc.add(lv, Face(pts, [cu(p) for p in pts], key, [cu(p) for p in pts]))
            border = [grid[0][i] for i in range(nx + 1)] + [grid[j][nx] for j in range(1, nz + 1)] + \
                     [grid[nz][i] for i in range(nx - 1, -1, -1)] + [grid[j][0] for j in range(nz - 1, 0, -1)]
            uvs = [(i / nx, 0) for i in range(nx + 1)] + [(1, j / nz) for j in range(1, nz + 1)] + \
                  [(i / nx, 1) for i in range(nx - 1, -1, -1)] + [(0, j / nz) for j in range(nz - 1, 0, -1)]
            outer = []
            for (u, v), p in zip(uvs, border):
                ue = 0.0 if u == 0 else (1.0 if u == 1 else uu(round(u * nx)))
                ve = 0.004 if v == 0 else (h if v == 1 else ar + (h - 2 * ar) * v)
                outer.append(at(ue, ve) - nrm * ar * 0.6)
            m = len(border)
            back = [p - nrm * 0.03 for p in outer]
            for i in range(m):
                for ring_a, ring_b, arris in ((outer, border, True), (back, outer, False)):
                    pts = [ring_a[i], ring_a[(i + 1) % m], ring_b[(i + 1) % m], ring_b[i]]
                    if flip:
                        pts = pts[::-1]
                    pc.add(lv, Face(pts, [cu(p) for p in pts], key, [cu(p) for p in pts], arris=arris))

    # ---- the eave: soffit, fascia, gutter on hooks and its downpipe
    def eaves(self):
        F = self.F
        rw = self.W.get("rainwater")
        has_gutter = rw is not None and rw["fittedYear"] <= F.year
        for wall in self.walls:
            if wall.kind != "eave":
                continue
            xa, xb = -self.vov - self.bt - 0.01, wall.L + self.vov + self.bt + 0.01
            zt = self.z_top
            self.trim(f"eave/w{wall.i}/soffit", wall, Vector((xa, 0.0, zt)), Vector((xb - xa, 0, 0)), OUT, Vector((0, 0, -1)),
                      self.ov, self.st, self.ch["soffit"], nseg=max(2, round((xb - xa) / 1.0)),
                      groups=("back", "under", "front"), chamfer_edges=(False, True), caps=(True, True))
            self.trim(f"eave/w{wall.i}/fascia", wall, Vector((xa, -self.ov, zt - self.st - 0.01)), Vector((xb - xa, 0, 0)),
                      Z, OUT, self.fh, self.ft, self.ch["fascia"], nseg=max(2, round((xb - xa) / 1.0)), caps=(True, True))
            if has_gutter:
                r = rw["gutterRadiusMm"] * MM
                gy = -self.ov - self.ft - r - 0.012
                gz = zt - self.st - 0.01 + self.fh - 0.035
                # the outlet at one end (the seed's), its pipe clear of the corner board
                end = 0 if F.u("pipe", wall.i, "end") < 0.5 else 1
                self.gutter(wall, xa + 0.01, xb - 0.01, gy, gz, r, rw)
                x = rw["outletFromEndMm"] * MM
                x = x if end == 0 else wall.L - x
                self.downpipe(wall, x, gy, gz, r, rw)
                # neglected, the gutter's joints open: each drips by how long it has been let go
                ng = F.last("neglected")
                if ng:
                    years = F.year - ng["year"]
                    for k in range(1 + (years > 5)):
                        at = xa + (xb - xa) * (0.2 + 0.6 * F.u("gutter", wall.i, "leak", k))
                        flow = min(1.0, ng["params"]["amount"] / 1000.0 * (0.4 + 0.2 * years))
                        self.features["drips"].append([wall.i, at, flow, "gutter"])
                self.features["drips"].append([wall.i, x, 1.0 if F.last("neglected") else 0.5, "shoe"])

    def gutter(self, wall, x0, x1, gy, gz, r, rw):
        th = rw["gutterThickMm"] * MM
        pc = self.make(f"eave/w{wall.i}/gutter", "zinc", ("near", "street"), wall)
        for lv in ("near", "street"):
            k = 8 if lv == "near" else 4
            outer = [(r * math.cos(math.pi * i / k), -r * math.sin(math.pi * i / k)) for i in range(k + 1)]
            prof = [(-p, q, "outside", False) for (p, q) in outer]
            inner = [(-p * (1 - th / r), q * (1 - th / r), "inside", False) for (p, q) in outer][::-1]
            bead = rw["beadMm"] * MM
            prof += [(r + bead * 0.3, bead * 0.6, "outside", False)] + inner
            extrude(pc, lv, prof, Vector((x0, gy, gz)), Vector((x1 - x0, 0, 0)), OUT, Z, self.charts,
                    nseg=max(3, round((x1 - x0) / 1.5)), caps=(True, True), nominal={"outside": math.pi * r, "inside": math.pi * r})
        hw, ht = rng(rw["hookMm"])
        every = rw["hookEveryMm"] * MM
        x, i = x0 + 0.12, 0
        while x < x1 - 0.05:
            pc = self.make(f"eave/w{wall.i}/hook{i}", "zinc", ("near",), wall)
            ri, ro = r + th, r + th + ht
            pts = [(ri * math.cos(math.pi * j / 4), -ri * math.sin(math.pi * j / 4)) for j in range(4, -1, -1)]
            pts += [(ri, 0.03), (ro, 0.03)]
            pts += [(ro * math.cos(math.pi * j / 4), -ro * math.sin(math.pi * j / 4)) for j in range(5)]
            pts.append(pts[0])
            extrude(pc, "near", [(-p, q, "iron", False) for (p, q) in pts], Vector((x - hw / 2, gy, gz)), Vector((hw, 0, 0)),
                    OUT, Z, self.charts)
            x += every
            i += 1

    def downpipe(self, wall, x, gy, gz, r, rw):
        """From the outlet a swan neck back to the wall, down to a shoe; rigid zinc, clear of the drip board."""
        pr = rw["pipeRadiusMm"] * MM
        dr = self.W["dripBoard"]["proudMm"] * MM
        y_wall = -self.step - max(rw["offWallMm"] * MM, dr + 0.012) - pr
        z_out = gz - r - 0.01
        neck = abs(y_wall - gy)
        path = [Vector((x, gy, z_out)), Vector((x, gy, z_out - 0.07)), Vector((x, y_wall, z_out - 0.07 - neck)),
                Vector((x, y_wall, z_out - 0.07 - neck - 0.06))]
        z_shoe = rw["shoeMm"] * MM
        path += [Vector((x, y_wall, z_shoe + 0.06)), Vector((x, y_wall - 0.08, z_shoe - 0.02))]
        self.features["pipes"].append([wall.i, x, y_wall, pr, z_shoe, z_out])
        anchor = wall.M @ Vector((x, y_wall, 1.5))
        for i in range(len(path) - 1):
            a, b = path[i], path[i + 1]
            pc = self.make(f"pipe/w{wall.i}/s{i}", "zinc", ("near", "street"), wall, "rigid")
            d = b - a
            up = Z if abs(d.normalized().z) < 0.9 else OUT
            P = d.cross(up).normalized()
            Q = d.cross(P).normalized()
            a2 = a - d.normalized() * (0.012 if i > 0 else 0.0)
            b2 = b + d.normalized() * (0.012 if i < len(path) - 2 else 0.0)
            for lv in ("near", "street"):
                k = 8 if lv == "near" else 4
                prof = [(pr * math.cos(2 * math.pi * j / k), pr * math.sin(2 * math.pi * j / k), "round", False) for j in range(k + 1)]
                extrude(pc, lv, prof, a2, b2 - a2, P, Q, self.charts, nseg=max(1, round((b2 - a2).length / 1.2)),
                        caps=(False, i == len(path) - 2), nominal={"round": 2 * math.pi * pr})
            pc.anchor, pc.along = anchor, None
        cw_, ct_ = rng(rw["clipMm"])
        z, i = z_shoe + 0.45, 0
        while z < z_out - 0.07 - neck - 0.1:
            pc = self.make(f"pipe/w{wall.i}/clip{i}", "zinc", ("near",), wall, "rigid")
            prof = [((pr + ct_) * math.cos(2 * math.pi * j / 8), (pr + ct_) * math.sin(2 * math.pi * j / 8), "iron", False) for j in range(9)]
            extrude(pc, "near", prof, Vector((x, y_wall, z)), Vector((0, 0, cw_)), ALONG, Vector((0, 1, 0)), self.charts, caps=(True, True))
            pc.anchor, pc.along = anchor, None
            z += rw["clipEveryMm"] * MM
            i += 1

    # ---- the verges: barge boards up each rake and a soffit under the tiles' overhang
    def verges(self):
        t = self.t
        for wall in self.walls:
            if wall.kind != "gable":
                continue
            L = wall.L
            a_foot = self.y_foot + 0.05
            for half in (0, 1):
                # the rake from its foot (over the eave's fascia) to the apex, in the gable's frame
                if half == 0:
                    a0, a1 = -self.ov - self.ft, L / 2.0
                else:
                    a0, a1 = L / 2.0, L + self.ov + self.ft
                p0 = Vector((a0, -self.vov, self.zp_wall(a0) - 0.006))
                p1 = Vector((a1, -self.vov, self.zp_wall(a1) - 0.006))
                r = (p1 - p0)
                rd = r.normalized()
                P = (Vector((0, 0, -1)) - rd * rd.z).normalized()
                # plumb cuts at the foot and the apex
                plumb = lambda p, q, P=P, rd=rd: -P.x * p / rd.x  # noqa: E731
                self.trim(f"verge/w{wall.i}h{half}/barge", wall, p0, r, P, OUT, self.bw, self.bt, self.ch["barge"],
                          nseg=max(2, round(r.length / 0.8)), groups=("top", "front", "bottom"),
                          caps=(True, True), cut=(plumb, plumb))
                # the soffit under the tiles from the gable's face out to the barge board
                q0 = Vector((a0, 0.0, self.zp_wall(a0) - 0.07))
                q1 = Vector((a1, 0.0, self.zp_wall(a1) - 0.07))
                self.trim(f"verge/w{wall.i}h{half}/soffit", wall, q0, q1 - q0, OUT, Vector((0, 0, -1)), self.vov, 0.02, 0.0,
                          nseg=max(2, round((q1 - q0).length / 0.8)), groups=("back", "under", "front"), caps=(False, False),
                          chamfer_edges=(False, False))
            del a_foot

    def zp_wall(self, a):
        """The tiles' plane over a gable's point `a` along it (beyond its ends, the eave's overhang)."""
        return self.z_foot + (min(a, self.d - a) - self.y_foot) * self.t

    # ---- the roof: pantiles course by course on each slope, the ridge, the chimney
    def roof(self):
        tl = {**self.M["clay-pantile"]["laid"], **{k: v for k, v in self.W["pantile"].items() if k != "describes"}}
        F = self.F
        cover, course, roll = tl["coverMm"] * MM, tl["courseMm"] * MM, tl["rollMm"] * MM
        thick, lift, lap = tl["thickMm"] * MM, tl["liftMm"] * MM, tl["lapMm"] * MM / (tl["coverMm"] * MM)
        pan, rnd = tl["panAt"], tl["roundness"]
        x0 = -self.vov - self.bt - tl["verge"]["pastMm"] * MM
        x1 = self.w - x0
        span = x1 - x0
        n_cov = math.ceil(span / cover)
        cs, sn = math.cos(self.pitch), math.sin(self.pitch)
        up, nrm = Vector((0, cs, sn)), Vector((0, -sn, cs))
        Ls = (self.d / 2.0 - self.y_foot) / cs
        n_courses = max(1, math.ceil((Ls - 0.06) / course))
        near_c = self.S["levels"]["near"]["tileCourses"]

        def wave(u):
            return (0.5 - 0.5 * math.cos(2.0 * math.pi * (u - pan))) ** rnd

        k = self.S["levels"]["near"]["pantileSamples"]
        us = [i * (1.0 + lap) / (k - 1) for i in range(k)]
        for target in (pan, pan + 0.5):
            j = min(range(1, k - 1), key=lambda i: abs(us[i] - target))
            us[j] = target
        near_prof = [(u, wave(u) + (thick / roll) * min(1.0, max(0.0, (u - 0.9) / 0.1))) for u in sorted(us)]
        ks = self.S["levels"]["street"]["pantileSamples"]
        street_u, u = [], pan - math.ceil(pan * ks) / ks
        while u < span / cover:
            street_u.append(max(0.0, u))
            u += 1.0 / ks
        street_u.append(span / cover)
        street_prof = [(u, wave(u)) for u in street_u]
        verge_prof = [(u, wave(u)) for u in (0.0, pan, pan + 0.5, 1.0 + lap)]
        for wall in self.walls:
            if wall.kind != "eave":
                continue
            base0 = Vector((0, self.y_foot, self.z_foot))
            for ci in range(n_courses):
                length = min(course + 0.075, Ls - course * ci + 0.02)
                key = self.charts(f"roof/w{wall.i}/c{ci:02d}", span + 0.1, length + 0.06)
                base = base0 + up * (course * ci)
                plane = []
                if ci < near_c:
                    plane.append(("near", "tiles", True))
                    # never drawn: the near tiles' bake target, so their charts are baked as the planes' are, from
                    # the tiles' top surface (the tiles' own charts overlap where they lap)
                    plane.append(("bake", "target", False))
                else:
                    plane.append(("near", "roof", False))
                    plane.append(("bake", "tiles", True))
                plane.append(("street", "tiles" if ci == 0 else "roof", ci == 0))
                self.city_roof.append((wall, ci, base, x0, x1, roll, thick, lift, length, up, nrm, key))
                for lv, mat, waves in plane:
                    if mat == "target":
                        pc = self.make(f"roof/w{wall.i}/c{ci:02d}/target", mat, (lv,), wall)
                        self.course_plane(pc, lv, base, x0, x0, x1, roll, thick, lift, length, up, nrm, key)
                    elif waves and lv != "street":
                        for ti in range(n_cov):
                            tid = f"roof/w{wall.i}/c{ci:02d}/t{ti}"
                            pc = self.make(tid, mat, (lv,), wall)
                            yaw = math.radians(1.6) * (2 * F.u(tid, "yaw") - 1)
                            dz = 0.004 * (2 * F.u(tid, "seat") - 1)
                            self.tile_strip(pc, lv, near_prof, base, x0 + ti * cover, cover, roll, thick, lift, length,
                                            up, nrm, yaw, dz, key, x0, under=ci == 0)
                            if ci == 0 and lv == "near":
                                self.features["tiles"].append([wall.i, x0 + ti * cover + pan * cover])
                    elif waves:
                        pc = self.make(f"roof/w{wall.i}/c{ci:02d}/strip", mat, (lv,), wall)
                        self.tile_strip(pc, lv, street_prof, base, x0, cover, roll, thick, lift, length, up, nrm, 0.0, 0.0,
                                        key, x0, under=True)
                    else:
                        # the verges' tiles real, so the rake draws their rolls against the sky; the plane between
                        # them from the first tile's roll to the last's, where the tiles stand at its height
                        prof = near_prof if lv == "near" else verge_prof
                        for ti in (0, n_cov - 1):
                            tid = f"roof/w{wall.i}/c{ci:02d}/t{ti}"
                            vt = self.make(tid if lv == "near" else tid + "/street", "tiles", (lv,), wall)
                            yaw = math.radians(1.6) * (2 * F.u(tid, "yaw") - 1) if lv == "near" else 0.0
                            dz = 0.004 * (2 * F.u(tid, "seat") - 1) if lv == "near" else 0.0
                            self.tile_strip(vt, lv, prof, base, x0 + ti * cover, cover, roll, thick, lift, length,
                                            up, nrm, yaw, dz, key, x0)
                        xa, xb = x0 + cover * (pan + 0.5), min(x1, x0 + cover * (n_cov - 0.5 + pan))
                        pc = self.make(f"roof/w{wall.i}/c{ci:02d}/plane", mat, (lv,), wall)
                        self.course_plane(pc, lv, base, x0, xa, xb, roll, thick, lift, length, up, nrm, key)
            self.features["roof"].append({"wall": wall.i, "x0": x0, "foot": [self.y_foot, self.z_foot], "pitch": math.degrees(self.pitch),
                                          "courses": n_courses, "course": course, "cover": cover, "pan": pan})
        self.ridge(x0, x1)

    def tile_strip(self, pc, lv, prof, base, xa, cover, roll, thick, lift, length, up, nrm, yaw, dz, key, x0, under=False):
        foot = base + Vector((xa, 0, 0)) + nrm * (lift * 0.35 + dz)
        head = base + Vector((xa, 0, 0)) + up * length - nrm * (lift * 0.15)
        rot = Matrix.Rotation(yaw, 3, nrm)

        def pt(u, hgt, at):
            return at + rot @ (Vector((u * cover, 0, 0)) + nrm * (hgt * roll))

        def cuv(p):
            return (p.x - x0 + 0.05, max(0.0, (p - base).dot(up)) + 0.03)
        for j in range(len(prof) - 1):
            (ua, ha), (ub, hb) = prof[j], prof[j + 1]
            pts = [pt(ua, ha, foot), pt(ub, hb, foot), pt(ub, hb, head), pt(ua, ha, head)]
            pc.add(lv, Face(pts, [cuv(p) for p in pts], key, [cuv(p) for p in pts]))
            dn = -nrm * thick
            f0, f1 = pts[0], pts[1]
            fp = [f0 + dn, f1 + dn, f1, f0]
            pc.add(lv, Face(fp, [cuv(p) for p in fp], key, [cuv(p) for p in fp]))
            if under:
                ub_ = [f1 + dn, f0 + dn, f0 + dn + up * 0.10, f1 + dn + up * 0.10]
                pc.add(lv, Face(ub_, [cuv(p) for p in ub_], key, [cuv(p) for p in ub_]))

    def course_plane(self, pc, lv, base, x0, xa, xb, roll, thick, lift, length, up, nrm, key):
        """A course drawn as one plane over its tiles' crests (as the tiles stand at its foot and head), the pans
        below it in the page's normal and occlusion; its foot a step down to the pans, its two ends closed."""
        foot = base + nrm * (lift * 0.35 + roll)
        head = base + up * length + nrm * (roll - lift * 0.15)
        dn = -nrm * (thick + roll)
        n = max(2, round((xb - xa) / 1.0))

        def cuv(p):
            return (p.x - x0 + 0.05, max(0.0, (p - base).dot(up)) + 0.03)
        for k in range(n):
            a = xa + (xb - xa) * k / n
            b = xa + (xb - xa) * (k + 1) / n
            pts = [foot + Vector((a, 0, 0)), foot + Vector((b, 0, 0)), head + Vector((b, 0, 0)), head + Vector((a, 0, 0))]
            pc.add(lv, Face(pts, [cuv(p) for p in pts], key, [cuv(p) for p in pts]))
            fp = [pts[0] + dn, pts[1] + dn, pts[1], pts[0]]
            pc.add(lv, Face(fp, [cuv(p) for p in fp], key, [cuv(p) for p in fp]))
        for x, flip in ((xa, True), (xb, False)):
            e = [foot + Vector((x, 0, 0)) + dn, head + Vector((x, 0, 0)) + dn, head + Vector((x, 0, 0)), foot + Vector((x, 0, 0))]
            if flip:
                e = e[::-1]
            pc.add(lv, Face(e, [cuv(p) for p in e], key, [cuv(p) for p in e]))

    def ridge(self, x0, x1):
        """Half-round ridge tiles along the ridge, each lapping the next; one strip at the street level."""
        rd = self.M["clay-pantile"]["laid"]["ridge"]
        r, tl, lp = rd["radiusMm"] * MM, rd["lengthMm"] * MM, rd["lapMm"] * MM
        zr = self.z_ridge + self.W["ridge"]["seatMm"] * MM - r * 0.35
        yr = self.d / 2.0
        span = x1 - x0
        key = self.charts("ridge/strip", span + 0.1, 2 * math.pi * r * 1.03 + 0.1)
        place = Matrix.Identity(4)

        def planar(p):
            # one chart for both levels: along the ridge, and round the roll (its inside below its outside)
            th = math.atan2(p.z - zr, yr - p.y)
            inside = math.hypot(p.z - zr, yr - p.y) < r * 0.99 - 0.004
            return key, p.x - x0 + 0.05, max(0.0, th) * r * 1.02 + 0.03 + (math.pi * r * 1.03 + 0.03 if inside else 0.0)

        def ring(k, rr):
            return [(rr * math.cos(math.pi * i / k), rr * math.sin(math.pi * i / k)) for i in range(k + 1)]
        # street: one half-round along the whole ridge
        pc = self.make("ridge/strip", "tiles", ("street",), None, "frame", place)
        prof = [(p, q, "round", False) for p, q in ring(6, r)]
        extrude(pc, "street", prof, Vector((x0, yr, zr)), Vector((span, 0, 0)), Vector((0, -1, 0)), Z, self.charts,
                nseg=max(2, round(span / 1.0)), caps=(True, True), planar=planar)
        n = math.ceil(span / (tl - lp))
        for i in range(n):
            xa = x0 + i * (tl - lp)
            L = min(tl, x1 - xa)
            pc = self.make(f"ridge/t{i}", "tiles", ("near",), None, "frame", place)
            rr = r * (1.0 + 0.02 * (i % 2))
            prof = [(p, q, "round", False) for p, q in ring(8, rr)] + [(-rr + 0.016, 0.0, "round", False)] + \
                   [(p * (1 - 0.016 / rr), q * (1 - 0.016 / rr), "round", False) for p, q in ring(8, rr)][::-1][1:]
            extrude(pc, "near", [(p, q, g, a) for (p, q, g, a) in ring_prof(prof)], Vector((xa, yr, zr)), Vector((L, 0, 0)),
                    Vector((0, -1, 0)), Z, self.charts, caps=(True, False), planar=planar)
        self.chimney(zr + r)

    def chimney(self, z_crest):
        ch = self.W["chimney"]
        F = self.F
        v = self.version("chimney", F.built)
        a = F.between(*rng(ch["sizeMm"]), "chimney", "size")
        x = self.w * F.between(*ch["alongShare"], "chimney", "along")
        y = self.d / 2.0
        top = self.z_ridge + F.between(*rng(ch["aboveRidgeMm"]), "chimney", "above")
        bottom = self.zp(y - a / 2.0 - 0.02) - 0.08
        c = self.ch["chimney"]
        pc = self.make("chimney/stack", "render", ("near", "street"), None, "rigid", Matrix.Identity(4))
        band, down = rng(v["bandMm"]), v["bandDownMm"] * MM
        for lv in ("near", "street"):
            cc = c if lv == "near" else 0.0
            # the stack swept up as a square section with its four arrises worn
            sq = square(a, cc)
            extrude(pc, lv, sq, Vector((x, y, bottom)), Vector((0, 0, top - bottom)), ALONG, Vector((0, 1, 0)), self.charts,
                    nseg=2, nominal={"face": 4 * a})
            if band[0] > 0:
                bb = a + 2 * band[0]
                extrude(pc, lv, square(bb, cc * 0.5), Vector((x, y, top - down - band[1])), Vector((0, 0, band[1])), ALONG,
                        Vector((0, 1, 0)), self.charts, caps=(True, True), nominal={"face": 4 * bb})
            # its top: a rim round the flue, the flue a dark hole
            fl = a * 0.45
            key = self.charts("chimney/top", a + 0.02, a + 0.02)
            h = a / 2.0
            o = [Vector((x - h, y - h, top)), Vector((x + h, y - h, top)), Vector((x + h, y + h, top)), Vector((x - h, y + h, top))]
            i_ = [Vector((x - fl / 2, y - fl / 2, top)), Vector((x + fl / 2, y - fl / 2, top)), Vector((x + fl / 2, y + fl / 2, top)),
                  Vector((x - fl / 2, y + fl / 2, top))]
            cu = lambda p: (p.x - x + h + 0.01, p.y - y + h + 0.01)  # noqa: E731
            for k in range(4):
                pts = [o[k], o[(k + 1) % 4], i_[(k + 1) % 4], i_[k]]
                pc.add(lv, Face(pts, [cu(p) for p in pts], key, [cu(p) for p in pts]))
            dn = Vector((0, 0, -0.2))
            for k in range(4):
                pts = [i_[k], i_[(k + 1) % 4], i_[(k + 1) % 4] + dn, i_[k] + dn]
                pc.add(lv, Face(pts, [cu(p) for p in pts], key, [cu(p) for p in pts], under=True))
        pc.anchor, pc.along = Vector((x, y, self.z_ridge)), ALONG
        self.features["chimney"] = [x, y, a, top]
        # where the stack meets the tiles a zinc apron dressed round it, its upper edge a hand over the tiles' crests
        # on every side (rising with the roof to the ridge on the gable sides) and turned in onto the stack
        fl = self.W["pantile"]
        up = fl["rollMm"] * MM + 0.12
        g = 0.015
        e = a / 2.0 + g
        pz = self.make("chimney/apron", "zinc", ("near", "street"), None, "rigid", Matrix.Identity(4))
        crest = lambda yy: min(self.zp(yy) + up, z_crest + 0.06)  # noqa: E731
        ring_ = [(x - e, y - e), (x + e, y - e), (x + e, y + e), (x - e, y + e)]
        for lv in ("near", "street"):
            for k in range(4):
                (ax, ay), (bx, by) = ring_[k], ring_[(k + 1) % 4]
                # a side across the ridge (k odd) breaks at the ridge so its edge follows both slopes
                cut = [(ax, ay)] + ([(ax, y)] if ay != by and (ay - y) * (by - y) < 0 else []) + [(bx, by)]
                key = self.charts(f"chimney/apron{k}", 2 * e, up + 0.4)
                for (px, py), (qx, qy) in zip(cut, cut[1:]):
                    s0, s1 = abs(px - ax) + abs(py - ay), abs(qx - ax) + abs(qy - ay)
                    pts = [Vector((px, py, bottom)), Vector((qx, qy, bottom)), Vector((qx, qy, crest(qy))), Vector((px, py, crest(py)))]
                    uv = [(s0, 0.0), (s1, 0.0), (s1, crest(qy) - bottom), (s0, crest(py) - bottom)]
                    pz.add(lv, Face(pts, uv, key, uv))
                # the turn-in: a lip from the apron's edge onto the stack
                key = self.charts(f"chimney/lip{k}", 2 * e, g + 0.01)
                pts = []
                for (px, py) in cut:
                    pts.append(Vector((px, py, crest(py))))
                inner = [Vector((x + (px - x) * (a / 2) / e, y + (py - y) * (a / 2) / e, crest(py))) for (px, py) in cut]
                for i in range(len(cut) - 1):
                    q = [pts[i], pts[i + 1], inner[i + 1], inner[i]]
                    s0 = abs(cut[i][0] - ax) + abs(cut[i][1] - ay)
                    s1 = abs(cut[i + 1][0] - ax) + abs(cut[i + 1][1] - ay)
                    uv = [(s0, 0.0), (s1, 0.0), (s1, g), (s0, g)]
                    pz.add(lv, Face(q, uv, key, uv))
        pz.anchor, pz.along = Vector((x, y, self.z_ridge)), ALONG

    # ---- the extension: a lean-to on the back, rigid as a whole, out of plumb by the hand that built it
    def lean_to_plan(self):
        ev = next((e for e in self.F.all("extended") if e["params"].get("kind") == "lean_to"), None)
        if ev is None:
            return
        F, W = self.F, self.W
        lt = W["leanTo"]
        depth = F.between(*rng(lt["depthMm"]), "leanto", "depth")
        width = self.w * F.between(*lt["widthShare"], "leanto", "width")
        xl = (self.w - width) * F.u("leanto", "at")
        xr = xl + width
        eave = lt["eaveMm"] * MM
        pitch = math.radians(F.between(*lt["pitchDeg"], "leanto", "pitch"))
        z_hi = min(eave + depth * math.tan(pitch), self.z_top - 0.3)
        plumb = math.radians(F.between(*lt["plumbDeg"], "leanto", "plumb"))
        back = self.walls[2]
        self.lean_to = {"year": ev["year"], "x": [xl, xr], "depth": depth, "eave": eave, "z_hi": z_hi, "plumb": plumb,
                        "a0": back.along(Vector((xr, self.d, 0))), "a1": back.along(Vector((xl, self.d, 0))),
                        "anchor": Vector(((xl + xr) / 2, self.d, 0.0)), "along": ALONG}
        y1 = self.d + depth
        n = len(self.walls)
        self.lt_walls = [Wall(n, (xr, self.d), math.pi / 2, depth, "lean", 1),
                         Wall(n + 1, (xr, y1), math.pi, width, "lean", 1),
                         Wall(n + 2, (xl, y1), 3 * math.pi / 2, depth, "lean", 1)]
        # its door in one of its sides, toward the house
        side = self.lt_walls[0] if F.u("leanto", "door") < 0.5 else self.lt_walls[2]
        door = W["openings"]["door"]
        dw, dh = door["wMm"] * MM * 0.9, min(door["hMm"] * MM, eave - 0.25)
        a0 = 0.25 if side is self.lt_walls[0] else side.L - 0.25 - dw
        bd = F.boarded()
        self.openings.append({"wall": side.i, "kind": "door", "a0": a0, "a1": a0 + dw, "z0": lt["plinthMm"] * MM + 0.02,
                              "z1": lt["plinthMm"] * MM + 0.02 + dh, "made": ev["year"], "eraOf": ev["year"], "leanTo": True,
                              "boarded": bd is not None and bd["params"].get("scope") == "all"})

    def lt_place(self, wall):
        """A lean-to piece's frame: its wall's, turned out of plumb about the foot of the house's back wall."""
        lt = self.lean_to
        pivot = Vector((0, self.d, 0))
        R = Matrix.Translation(pivot) @ Matrix.Rotation(-lt["plumb"], 4, "X") @ Matrix.Translation(-pivot)
        return R @ wall.M

    def lean_to_build(self):
        lt = self.lean_to
        if lt is None:
            return
        W = self.W
        L = W["leanTo"]
        cl = {**W["cladding"], **L["cladding"]}
        zp = L["plinthMm"] * MM
        y1 = self.d + lt["depth"]
        tp = (lt["z_hi"] - lt["eave"]) / lt["depth"]

        def top(wall):
            if wall.i == self.lt_walls[1].i:
                return lambda a: lt["eave"]
            if wall.i == self.lt_walls[0].i:
                return lambda a: lt["z_hi"] - tp * a
            return lambda a: lt["eave"] + tp * a
        fixed = []
        for o in self.openings:
            if o.get("leanTo"):
                fixed.append(o["z1"] + self.head_h + self.cap_t)
        self.course_table(1, zp, lt["z_hi"] + 0.05, fixed, cl, "leanto")
        self.cladding(self.lt_walls, 1, zp, cl, self.opening_gaps_lt, rake=top, mode="rigid", place_of=self.lt_place)
        # its plinth: a cast band under every wall
        for wall in self.lt_walls:
            pc = self.make(f"leanto/plinth/w{wall.i}", "concrete", ("near", "street"), wall, "rigid", self.lt_place(wall))
            prof = [(0.0, 0.0, "front", False), (0.0, 0.03, "front", False), (zp, 0.03, "top", False), (zp, 0.0, "top", False)]
            extrude(pc, "near", prof, Vector((-0.03, 0.0, 0.0)), Vector((wall.L + 0.06, 0, 0)), Z, OUT, self.charts, caps=(True, True))
            extrude(pc, "street", prof, Vector((-0.03, 0.0, 0.0)), Vector((wall.L + 0.06, 0, 0)), Z, OUT, self.charts, caps=(True, True))
            pc.anchor, pc.along = lt["anchor"], lt["along"]
        # corner boards at its two outer corners
        cb = W["corner"]
        w = cb["widthMm"] * MM * 0.8
        proud = cb["proudMm"] * MM
        s = cl["stepMm"] * MM
        for wall, x in ((self.lt_walls[1], -(s + proud)), (self.lt_walls[1], self.lt_walls[1].L - w)):
            H = lt["eave"] - zp
            pc = self.trim(f"leanto/corner/{x:.2f}", wall, Vector((x, -s, zp)), Vector((0, 0, H)), ALONG, OUT, w + s + proud,
                           proud, self.ch["corner"], nseg=2, groups=("left", "front", "right"), caps=(False, False),
                           mode="rigid", place=self.lt_place(wall))
            pc.anchor, pc.along = lt["anchor"], lt["along"]
        # its roof: boards under felt, a slab from the house's wall out over the eave
        xl, xr = lt["x"]
        ov = 0.15
        o0 = Vector((xl - ov, self.d - 0.02, lt["z_hi"] + 0.03))
        o1 = Vector((xl - ov, y1 + ov, lt["eave"] + 0.03 - tp * ov))
        pc = self.make("leanto/roof", "felt", ("near", "street"), None, "rigid",
                       Matrix.Translation(Vector((0, self.d, 0))) @ Matrix.Rotation(-lt["plumb"], 4, "X") @ Matrix.Translation(Vector((0, -self.d, 0))))
        L_ = o1 - o0
        for lv in ("near", "street"):
            prof = rect_profile(xr - xl + 2 * ov, 0.07, 0.01 if lv == "near" else 0.0, groups=("end", "top", "edge", "under"), back=True)
            extrude(pc, lv, [(p, -q, g, a) for (p, q, g, a) in prof], o0, L_, ALONG, Vector((0, 0, 1)) + Vector((0, 1, 0)) * 0.0,
                    self.charts, nseg=2, caps=(True, True), nominal={"top": xr - xl + 2 * ov, "end": 0.07, "edge": 0.07, "under": xr - xl})
        pc.anchor, pc.along = lt["anchor"], lt["along"]
        # the felt dressed over boards nailed round the slab's edges (a fascia at the eave, a barge board each side),
        # and its turn-up at the house hidden under a cover board on the wall
        plumb = Matrix.Translation(Vector((0, self.d, 0))) @ Matrix.Rotation(-lt["plumb"], 4, "X") @ Matrix.Translation(Vector((0, -self.d, 0)))
        bt_, fh_ = 0.022, 0.17
        pb = self.make("leanto/edges", "trims", ("near", "street"), None, "rigid", plumb)
        down, outy = Vector((0, 0, -1)), Vector((0, 1, 0))
        for lv in ("near", "street"):
            cc = self.ch["fascia"] if lv == "near" else 0.0
            extrude(pb, lv, rect_profile(fh_, bt_, cc, groups=("bottom", "front", "top", "back")),
                    Vector((xl - ov - bt_, o1.y, o1.z + 0.012)), Vector((xr - xl + 2 * ov + 2 * bt_, 0, 0)), down, outy,
                    self.charts, nseg=2, caps=(True, True), nominal={"front": fh_, "bottom": bt_, "top": bt_})
            for xb, sgn in ((xl - ov - bt_, 1), (xr + ov, 1)):
                extrude(pb, lv, rect_profile(fh_ - 0.02, bt_, cc, groups=("bottom", "front", "top", "back")),
                        Vector((xb, o0.y + 0.02, o0.z + 0.012)), Vector((0, L_.y - 0.02, L_.z + tp * 0.02)), down,
                        Vector((sgn, 0, 0)), self.charts, nseg=2, caps=(True, False),
                        nominal={"front": fh_ - 0.02, "bottom": bt_, "top": bt_})
            extrude(pb, lv, rect_profile(0.10, bt_, cc, groups=("bottom", "front", "top", "back")),
                    Vector((xl - ov, self.d + 0.004, o0.z - 0.015)), Vector((xr - xl + 2 * ov, 0, 0)), Z, outy,
                    self.charts, nseg=2, caps=(True, True), nominal={"front": 0.10, "bottom": bt_, "top": bt_})
        pb.anchor, pb.along = lt["anchor"], lt["along"]

    def opening_gaps_lt(self, wall, zb, zt):
        boxes = []
        for o in self.openings:
            if o["wall"] != wall.i:
                continue
            z_hi = o["z1"] + self.head_h + self.cap_t
            if zb is None:
                boxes.append((o["a0"], o["a1"], self.courses[1][0], o["z1"]))
            elif zt > o["z0"] + 0.005 and zb < z_hi - 0.005:
                boxes.append((o["a0"], o["a1"]))
        return boxes

    # ---- the whole
    def build(self):
        W = self.W
        self.city_roof, self.city_plinth = [], []
        self.plan_openings()
        self.lean_to_plan()
        for o in self.openings:
            o["covered"] = self.covered_by_lean_to(o)
        self.openings = [o for o in self.openings if not o["covered"]]
        fixed = []
        for o in self.openings:
            if o["kind"] in ("window", "loft") and not o.get("leanTo"):
                fixed += [o["z0"] - self.sill_t, o["z1"] + self.head_h + self.cap_t]
        self.course_table(0, self.z_drip1, self.z_ridge + 0.1, fixed, W["cladding"], "house")
        self.cladding([w for w in self.walls if w.kind == "eave"], 0, self.z_drip1, W["cladding"], self.opening_gaps,
                      z_end=self.z_top)
        self.cladding([w for w in self.walls if w.kind == "gable"], 0, self.z_drip1, W["cladding"], self.opening_gaps,
                      rake=lambda wall: self.z_rake)
        self.corner_boards()
        self.drip_boards()
        for k, o in enumerate(self.openings):
            self.surround(o, k)
            if o["boarded"]:
                self.boarding(o, k)
        self.plinth()
        self.eaves()
        self.verges()
        self.roof()
        self.lean_to_build()

    def city(self):
        """The city level, after the rest so every other piece keeps its index: what the street level draws that a
        house seen from afar still shows. Each street piece keeps its faces but those whose group the level drops
        (street.json levels.city) and that are narrower than its width (the sides and tops a few centimetres
        across) or that only the ground could see (undersides, backs), each run of segments along a straight sweep
        merged to one face, and none turned to the wall it stands on; each roof course one plane from verge to verge
        with its foot's step, each wall's plinth one face, a piece's own city faces where it has them (an opening's
        frame flush). Where a merged face's edge meets another's corner, the
        corner is welded into the edge, so the frame's bend opens no crack. Every face on its street face's chart, so the page and its bake are the street level's."""
        C = self.S["levels"]["city"]
        drop, narrow, never = set(C["dropGroups"]), C["dropNarrowerM"], set(C["neverGroups"])
        own = {"roof", "plinth"}
        for pc in list(self.pieces):
            if "street" not in pc.levels or pc.kind in own or getattr(pc, "no_city", False):
                continue
            fs = getattr(pc, "city", None) or [f for f in merge_runs(pc.faces["street"]) if group_of(f.chart) not in never
                  and (group_of(f.chart) not in drop or width_of(f) >= narrow)
                  and not (pc.wall >= 0 and newell(f.p).normalized().y > C["dropFacingWall"])]
            if fs:
                pc.levels = tuple(pc.levels) + ("city",)
                pc.faces["city"] = weld(fs)
        for (wall, ci, base, x0, x1, roll, thick, lift, length, up, nrm, key) in self.city_roof:
            pc = self.make(f"roof/w{wall.i}/c{ci:02d}/city", "roof", ("city",), wall)
            foot = base + nrm * (lift * 0.35 + roll)
            head = base + up * length + nrm * (roll - lift * 0.15)
            pts = [foot + Vector((x0, 0, 0)), foot + Vector((x1, 0, 0)), head + Vector((x1, 0, 0)), head + Vector((x0, 0, 0))]
            # and its foot's step down to the course below, which draws the course's line
            dn = -nrm * (thick + roll)
            for q in (pts, [pts[0] + dn, pts[1] + dn, pts[1], pts[0]]):
                cuv = [(p.x - x0 + 0.05, max(0.0, (p - base).dot(up)) + 0.03) for p in q]
                pc.add("city", Face(q, cuv, key, cuv))
        for (wall, y_face, e, zt, key) in self.city_plinth:
            pc = self.make(f"plinth/w{wall.i}/city", "stone", ("city",), wall)
            pts = [Vector((-e, y_face, 0.0)), Vector((wall.L + e, y_face, 0.0)), Vector((wall.L + e, y_face, zt)), Vector((-e, y_face, zt))]
            cuv = [(p.x + 0.3, p.z) for p in pts]
            pc.add("city", Face(pts, cuv, key, cuv))


def inset(r, d):
    """A rectangle (x0, z0, x1, z1) shrunk by `d` all round."""
    return (r[0] + d, r[1] + d, r[2] - d, r[3] - d)


def sash_grid(inner, s, bw, v, h_nominal):
    """A sash's lights and bars inside its stiles and rails: `cols` by `rows`, the rows fitted to the version's pane
    height where it has one (paneHMm: a smaller opening, a loft's, takes fewer panes of the same glass), from the
    sash's nominal height so every level counts the same. The upright bars run the full height, the cross bars
    between them."""
    nc = s.get("cols", 1)
    nr = s.get("rows", 1)
    if v.get("paneHMm"):
        b = v["barMm"][0] * MM
        nr = max(1, round((h_nominal + b) / (v["paneHMm"] * MM + b)))
    w, h = inner[2] - inner[0], inner[3] - inner[1]
    lw, lh = (w - (nc - 1) * bw) / nc, (h - (nr - 1) * bw) / nr
    lights = [(inner[0] + i * (lw + bw), inner[1] + j * (lh + bw), inner[0] + i * (lw + bw) + lw, inner[1] + j * (lh + bw) + lh)
              for i in range(nc) for j in range(nr)]
    bars = [(inner[0] + i * (lw + bw) - bw, inner[1], inner[0] + i * (lw + bw), inner[3]) for i in range(1, nc)]
    bars += [(inner[0] + i * (lw + bw), inner[1] + j * (lh + bw) - bw, inner[0] + i * (lw + bw) + lw, inner[1] + j * (lh + bw))
             for i in range(nc) for j in range(1, nr)]
    return lights, bars


def square(a, c):
    """A square section `a` across centred on the sweep, its four arrises chamfered by `c`: one group, 'face'."""
    h = a / 2.0
    pts = []
    for (sx, sy) in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
        if c > 0:
            # each corner as two points either side of its chamfer, walking round
            pts.append((sx * h + (c if sx < 0 and sy < 0 else 0), sy * h))
        pts.append((sx * h, sy * h))
    if c > 0:
        pts = []
        for (sx, sy), (nx, ny) in (((-1, -1), (1, -1)), ((1, -1), (1, 1)), ((1, 1), (-1, 1)), ((-1, 1), (-1, -1))):
            ax, ay = sx * h, sy * h
            bx, by = nx * h, ny * h
            d = ((bx - ax) / (2 * h), (by - ay) / (2 * h))
            pts.append((ax + d[0] * c, ay + d[1] * c, "face", False))
            pts.append((bx - d[0] * c, by - d[1] * c, "face", True))
        pts.append(pts[0])
        return pts
    pts = [(-h, -h, "face", False), (h, -h, "face", False), (h, h, "face", False), (-h, h, "face", False), (-h, -h, "face", False)]
    return pts


def group_of(chart):
    """A face's group from its chart key ('h107/open0/casing/l#front' -> 'front', a cap's 'cap'), '-' for a planar chart."""
    return chart.split("#")[1].rstrip("0123456789") if "#" in chart else "-"


def width_of(f):
    """A face's narrower extent: a quad's lesser mean of its two pairs of opposite sides, any other face's least side."""
    e = [(f.p[(k + 1) % len(f.p)] - f.p[k]).length for k in range(len(f.p))]
    return min((e[0] + e[2]) / 2, (e[1] + e[3]) / 2) if len(e) == 4 else min(e)


def weld(faces):
    """Every corner of a piece's faces that lies inside another face's edge put into that edge (its UVs between the
    edge's ends), so a bend moves both alike: no T-junction to crack."""
    pts = [(p, f.uv0[k], f.cuv[k]) for f in faces for k, p in enumerate(f.p)]
    out = []
    for f in faces:
        P, U0, CU = [], [], []
        n = len(f.p)
        for k in range(n):
            a, b = f.p[k], f.p[(k + 1) % n]
            P.append(a), U0.append(f.uv0[k]), CU.append(f.cuv[k])
            ab = b - a
            L2 = ab.length_squared
            if L2 < 1e-12:
                continue
            on = {}
            for (q, _, _) in pts:
                t = (q - a).dot(ab) / L2
                if 1e-4 < t < 1 - 1e-4 and (a + ab * t - q).length < 1e-5:
                    on[round(t, 6)] = t
            for t in sorted(on.values()):
                lerp = lambda x, y: (x[0] + (y[0] - x[0]) * t, x[1] + (y[1] - x[1]) * t)  # noqa: E731
                P.append(a + ab * t), U0.append(lerp(f.uv0[k], f.uv0[(k + 1) % n])), CU.append(lerp(f.cuv[k], f.cuv[(k + 1) % n]))
        out.append(Face(P, U0, f.chart, CU, f.arris, f.under) if len(P) > n else f)
    return out


def merge_runs(faces):
    """Quads on one chart that share a whole edge, their sides running on in line, as one quad, until none do: a
    sweep's segments, a wall's grid of planes. In the piece's own frame, before any bend, so a run is straight."""
    def line(a, b, c):
        u, v = b - a, c - b
        return u.length > 1e-9 and v.length > 1e-9 and u.normalized().dot(v.normalized()) > 0.9999

    def join(g, f):
        if len(g.p) != 4 or len(f.p) != 4 or f.chart != g.chart or f.arris != g.arris or f.under != g.under:
            return None
        for i in range(4):
            for j in range(4):
                if (f.p[j] - g.p[(i + 1) % 4]).length < 1e-6 and (f.p[(j + 1) % 4] - g.p[i]).length < 1e-6:
                    ga = [(i + 1 + k) % 4 for k in range(4)]  # g from the shared edge's end round to its start
                    fb = [(j + 2) % 4, (j + 3) % 4]
                    P = [g.p[k] for k in ga] + [f.p[k] for k in fb]
                    if not (line(P[5], P[0], P[1]) and line(P[2], P[3], P[4])):
                        return None
                    keep = [1, 2, 4, 5]
                    pick = lambda gl, fl: ([gl[k] for k in ga] + [fl[k] for k in fb])  # noqa: E731
                    return Face([P[k] for k in keep], [pick(g.uv0, f.uv0)[k] for k in keep], f.chart,
                                [pick(g.cuv, f.cuv)[k] for k in keep], f.arris, f.under)
        return None
    out = list(faces)
    merged = True
    while merged:
        merged = False
        for a in range(len(out)):
            for b in range(len(out)):
                if a != b:
                    m = join(out[a], out[b])
                    if m is not None:
                        out[a] = m
                        del out[b]
                        merged = True
                        break
            if merged:
                break
    return out


def ring_prof(prof):
    return prof


def newell_dot(pts, n):
    from geom import newell
    return newell(pts).dot(n)


def clip_top(poly, top):
    """A wall plane's polygon (x along, z up) cut to the part below its top's function, sampled as a polyline."""
    out = []
    n = len(poly)
    f = lambda p: top(p.x) - p.z  # noqa: E731
    for i in range(n):
        a, b = poly[i], poly[(i + 1) % n]
        fa, fb = f(a), f(b)
        if fa >= 0:
            out.append(a)
        if (fa >= 0) != (fb >= 0):
            lo, hi = (a, b) if fa >= 0 else (b, a)
            for _ in range(30):
                m = (lo + hi) / 2
                if f(m) >= 0:
                    lo = m
                else:
                    hi = m
            out.append(lo)
    # the top's own kink (the apex) inside the cut edge
    res = []
    for i, p in enumerate(out):
        res.append(p)
        q = out[(i + 1) % len(out)] if out else p
        if abs(f(p)) < 1e-4 and abs(f(q)) < 1e-4 and abs(p.x - q.x) > 1e-4:
            xs = sorted((p.x, q.x))
            # the gable's apex lies between them: add it
            for xm in [xs[0] + (xs[1] - xs[0]) * k / 8 for k in range(1, 8)]:
                pass
            mid = None
            for k in range(1, 40):
                xm = p.x + (q.x - p.x) * k / 40
                zl = p.z + (q.z - p.z) * k / 40
                if top(xm) - zl > 1e-3:
                    mid = xm
                    break
            if mid is not None:
                # find the top's highest point between p and q
                best = max((p.x + (q.x - p.x) * k / 200 for k in range(201)), key=lambda xm: top(xm))
                res.append(Vector((best, p.y, top(best))))
    return res


# ---------------------------------------------------------------- export


def glass_digest(G):
    """glass.json as the glass shader reads it: colours linear, the kinds in order (a pane's vertex colour R names
    one by its index)."""
    def lin(h):
        return [((int(h[i:i + 2], 16) / 255.0 + 0.055) / 1.055) ** 2.4 if int(h[i:i + 2], 16) > 10 else int(h[i:i + 2], 16) / 255.0 / 12.92
                for i in (0, 2, 4)]
    r, c, d = G["room"], G["room"]["curtains"], G["daylight"]
    kinds = [dict(k, name=n) for n, k in G["kinds"].items() if n != "describes"]
    return {"gloss": G["gloss"], "lamp": lin(r["srgbLamp"]), "walls": lin(r["srgbWalls"]), "ceiling": lin(r["srgbCeiling"]),
            "floor": lin(r["srgbFloor"]), "furniture": lin(r["srgbFurniture"]), "shade": lin(r["srgbShade"]),
            "curtain": lin(c["srgb"]), "room": [r["lampPower"], r["lampSoftM2"], r["depthM"], r["halfWidthM"], r["sillM"],
            r["heightM"], r["ambient"], r["lampDropM"], r["lampSwingM"], r["furnitureHeightM"], r["furnitureHalfLengthM"],
            r["cornerReachM"], r["cornerLight"], r["shadeRadiusM"], r["shadeGlow"]],
            "curtains": [c["share"], c["opacity"], c["depthM"], c["valanceShare"], c["foldsPerM"]],
            "daylight": [d["window"], d["backWall"], d["ceiling"], d["curtains"]],
            "kinds": [{"name": k["name"], "tiltDeg": k["tiltDeg"], "perM": k["perM"], "shape": k["shape"]} for k in kinds]}


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    a = {argv[i].lstrip("-"): argv[i + 1] for i in range(0, len(argv) - 1, 2)}
    S = load("blender/parts/street/street.json")
    hid = int(a.get("house", 107))
    year = int(a.get("year", S["year"]))
    out = os.path.abspath(a.get("out", os.path.join(ROOT, "cache", "street", "gen", str(hid))))
    os.makedirs(out, exist_ok=True)
    F = Facts(a.get("fixture", S["fixture"]), hid, year)
    W = load(S["eras"][F.era])
    V = load(S["versions"])
    mats = {m: load(f"{S['materials']}/{m}.json") for m in ("clay-pantile", "fieldstone", "pine", "glass")}
    paints = load(S["paints"])
    house = House(S, W, V, F, mats, paints)
    house.build()
    house.city()
    for i, pc in enumerate(house.pieces):
        pc.index = i
    # densities by part
    dens = S["page"]["density"]
    # the walls that face the street take the page's full density, every other face `elsewhere` of it
    front = {w.i for w in house.walls if w.kind != "lean" and w.out.y < -0.7}
    on_front = {f"open{k}" for k, o in enumerate(house.openings) if o["wall"] in front}
    for key in list(house.charts.size):
        kind = key.split("#")[0].split("/")[1] if key.startswith("h") else key.split("/")[0]
        parts = key.split("#")[0].split("/")
        faces = (parts[0] in ("wall", "plinth") and parts[1] in {f"w{i}" for i in front}) or \
                (key.startswith("h") and parts[1] in on_front)
        sc = 1.0 if faces else dens.get("elsewhere", 1.0)
        if kind in dens:
            sc *= dens[kind]
        if key.endswith("#under"):
            sc = dens["under"] * dens.get("elsewhere", 1.0)
        house.charts.scale[key] = sc
    rects, fill, px = house.charts.fit(S["page"])

    bpy.ops.wm.read_factory_settings(use_empty=True)
    rigid = {}
    for pc in house.pieces:
        if pc.mode == "rigid":
            anchor = pc.anchor if pc.anchor is not None else Vector((0, 0, 0))
            rigid[pc.id] = house.frame.rigid(anchor, pc.along)

    def place_of(pc):
        return pc.place

    def deform(pc, w):
        if pc.mode == "rigid":
            return rigid[pc.id] @ w
        return house.frame(w)

    lap_reach = S["lapReach"]

    def colour(pc, f, world):
        if f.col is not None:
            return list(f.col)
        rgb = [1.0 if f.arris else 0.0, F.u(pc.id, "seed"), 1.0 if f.under else 0.0]
        board = re.search(r"/c(\d+)b\d+$", pc.id) if pc.kind == "clad" else None
        if board is None:
            return rgb + [1.0]
        zs = house.courses[pc.group]
        z_next = zs[min(int(board.group(1)) + 1, len(zs) - 1)]
        # the lap's distance in the wall's own frame: its rest height before any turn
        M = pc.place
        loc = [M.inverted() @ w for w in world]
        return [rgb + [min(1.0, max(0.0, z_next - p.z) / lap_reach)] for p in loc]

    counts, objs = {}, {}
    for lv in ("near", "street", "city", "bake"):
        by_mat = {}
        for pc in house.pieces:
            if lv not in pc.levels:
                continue
            for f in pc.faces[lv]:
                by_mat.setdefault(pc.mat, []).append((pc, f))
        for mat in sorted(by_mat):
            o = to_object(f"{lv}_{mat}", by_mat[mat], place_of, deform, rects, S["page"]["size"], colour)
            objs[(lv, mat)] = o
            counts.setdefault(lv, {})[mat] = tris_of(o)
    total = {lv: sum(c.values()) for lv, c in counts.items()}
    budgets = {lv: S["levels"][lv]["budgetTris"] for lv in ("near", "street", "city")}
    over = [lv for lv in budgets if total.get(lv, 0) > budgets[lv][1]]
    print(f"[house] {hid}: triangles {json.dumps(counts)} totals {total}; page {px} px/m, filled {fill:.2f}; "
          f"versions {json.dumps(house.version_of)}")
    if over:
        raise SystemExit(f"[house] over budget: {', '.join(f'{lv} {total[lv]} > {budgets[lv][1]}' for lv in over)}")

    for lv in ("near", "street", "city"):
        for o in bpy.context.scene.objects:
            o.select_set(o.name.startswith(lv + "_"))
        bpy.ops.export_scene.fbx(filepath=os.path.join(out, f"house-{lv}.fbx"), use_selection=True,
                                 object_types={"MESH"}, mesh_smooth_type="OFF", use_mesh_modifiers=False,
                                 colors_type="LINEAR", axis_forward="-Z", axis_up="Y", apply_unit_scale=True,
                                 apply_scale_options="FBX_SCALE_ALL", bake_space_transform=True, add_leaf_bones=False)
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(out, "house.blend"))
    walls = house.walls + (house.lt_walls if house.lean_to else [])
    meta = {
        "house": F.id, "world": F.world, "year": F.year, "built": F.built, "age": F.age, "era": F.era, "type": F.type,
        "wealth": F.wealth, "plot": F.plot, "events": F.events,
        "size": [house.w, house.d], "pitch": math.degrees(house.pitch),
        "triangles": counts, "totals": total, "budgets": budgets,
        "page": dict(S["page"], pxPerM=px), "fill": fill, "charts": {k: list(v) for k, v in rects.items()},
        "heights": {"plinth": house.z_plinth, "floor": house.z_floor, "floors": house.floors, "loft": house.z_loft,
                    "drip": [house.z_drip0, house.z_drip1], "top": house.z_top, "ridge": house.z_ridge,
                    "foot": [house.y_foot, house.z_foot]},
        "walls": [w.info() for w in walls], "courses": {str(k): v for k, v in house.courses.items()},
        "openings": house.openings, "leanTo": house.lean_to and {k: (list(v) if hasattr(v, "__iter__") else v) for k, v in house.lean_to.items()},
        "bends": {"settle": house.frame.settle, "sag": house.frame.sag, "lean": house.frame.lean, "corner": house.frame.corner},
        "versions": house.version_of, "features": house.features,
        "lap": {"reach": S["lapReach"], "step": W["cladding"]["stepMm"] * MM},
        "planeShadow": S["planeShadow"], "seenWithinM": S["levels"]["near"]["seenWithinM"],
        "cityFromM": S["levels"]["city"]["seenFromM"],
        "pieces": [{"i": pc.index, "id": pc.id, "mat": pc.mat, "kind": pc.kind, "mode": pc.mode, "wall": pc.wall, "group": pc.group}
                   for pc in house.pieces],
        "uv": {"uv0": "metres along the grain", "page": "UV1: the page"},
        "glass": glass_digest(mats["glass"]),
        "colour": {"r": "arris (a chamfer face)", "g": "piece seed", "b": "under layer forced (mortar, a flue)",
                   "a": "near boards: distance below the next butt / lapReach"},
    }
    with open(os.path.join(out, "house.json"), "w") as fh:
        json.dump(meta, fh, indent=1, default=lambda v: list(v) if hasattr(v, "__iter__") else str(v))
    print(f"[house] wrote {out}")


main()
