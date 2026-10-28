"""House 107's street corner in 1989, the finishing test's sample: about 3 m of the street wall and 1.5 m of the gable
return, ground to eave, with the plinth, the lap cladding, the corner boards, one boarded window in its casing, the
eave with its fascia and the first two courses of pantiles. The first piece of 107's generator:
fitted parts whose inputs are facts (107's record, the working in classical.json, the pack's materials).

    Blender -b --factory-startup -P blender/parts/finish/corner.py -- --out cache/finish/gen   (all steps: run/build.sh)

Writes corner-near.fbx and corner-street.fbx (one object per material), corner.blend (both levels, for the bakes) and
corner.json (triangles per level and object, the page's charts, the features the marks read). Fails, writing nothing,
when a level is over its budget.

Two levels from one plan: near draws every board with its lap and every arris chamfered; street draws each wall as a
plane whose laps come from the page's normal (baked from near), its trims as boxes. Both share UV1, the page: each wall's
cladding is charted in the wall's plane, every other piece by its faces' groups, so a mark stays on the same board at
both levels. UV0 is the tileable's (metres along the grain) or the trim sheet's strip. Vertex colour: R the arris (a
chamfer face), G the piece's seed, B the under layer forced (mortar), A on a near board how far below the next course's
butt the corner sits (0..1 over `lapReach` metres; exact across the face, which is planar), 1 elsewhere.

Timber follows the frame (settle, sag, lean: classical.json bends); stones and the boarding of 1986 are rigid and
only moved and turned (BB3).
"""

import json
import math
import re
import os
import sys

import bmesh
import bpy
from mathutils import Matrix, Vector

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "blender", "resolver"))
import hashing as HS  # noqa: E402
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from finishlib import trim_strips  # noqa: E402

MM = 0.001
HERE = os.path.dirname(os.path.abspath(__file__))


def load(path):
    with open(os.path.join(ROOT, path)) as fh:
        return json.load(fh)


# ---------------------------------------------------------------- facts


class Facts:
    """107's record as the corner reads it."""

    def __init__(self, spec):
        street = load(spec["fixture"])
        self.world = street["worldSeed"]
        rec = next(b for b in street["buildings"] if b["id"] == spec["house"])
        ev = {e["kind"]: e for e in rec["events"]}
        self.id = rec["id"]
        self.year = spec["year"]
        self.built = ev["built"]["year"]
        self.era = ev["built"]["params"]["era"]
        self.wealth = ev["built"]["params"]["wealth"]
        self.windows = ev["windows_replaced"]["year"]
        self.boarded = ev["boarded"]["year"]
        self.neglect = ev["neglected"]["params"]["amount"]
        self.age = self.year - self.built

    def key(self, *parts):
        return HS.h(self.world, f"h{self.id}", *parts)

    def u(self, *parts):
        return HS.unit(self.key(*parts))

    def between(self, lo, hi, *parts):
        return lo + (hi - lo) * self.u(*parts)


# ---------------------------------------------------------------- the frame's bends


class Frame:
    """Old timber moves (classical.json bends): the seen corner settles, the wall plate sags between the gables, the
    roof's thrust leans the wall's head out. Positions are world metres, the street wall along +x from the corner,
    the gable along +y, z up; the street is at y < 0."""

    def __init__(self, W, F, z_sill, z_top):
        b = W["bends"]
        c = F.age / 100.0
        self.settle = min(b["settleMostMm"], b["settleMmPerCentury"] * c) * MM * W["push"]["settle"]
        self.sag = min(b["sagMostMm"], b["sagMmPerCentury"] * c) * MM
        self.lean = min(b["leanMostMm"], b["leanMmPerCentury"] * c) * MM
        self.L = b["frameLengthMm"] * MM
        self.reach = b["settleReachMm"] * MM
        self.bend, self.share = b["settleBendMm"] * MM, b["settleBendShare"]
        self.z_sill, self.z_top = z_sill, z_top

    def offset(self, p):
        x, y, z = p
        # the settled corner: the frame tilts down to it over `reach`, courses, sill and eave together, and its sill
        # beam bends a little more over the failing stones within `bend` of it
        tx, ty = max(0.0, 1.0 - x / self.reach), max(0.0, 1.0 - y / self.reach)
        bx, by = max(0.0, 1.0 - x / self.bend), max(0.0, 1.0 - y / self.bend)
        dz = -self.settle * ((1.0 - self.share) * tx * ty + self.share * (bx * by) ** 2)
        h = min(1.0, max(0.0, (z - self.z_sill) / (self.z_top - self.z_sill)))
        s = math.sin(math.pi * min(1.0, max(0.0, x / self.L)))
        dz -= self.sag * s * h
        dy = -self.lean * s * h * h
        return Vector((0.0, dy, dz))

    def __call__(self, p):
        return p + self.offset(p)

    def rigid(self, anchor, along=None):
        """A rigid piece's move: the frame's offset at its anchor, and a turn about the anchor that follows the
        frame's slope along `along` (a world direction), never a bend."""
        off = self.offset(anchor)
        if along is None:
            return Matrix.Translation(off)
        a = along.normalized() * 0.25
        d = (self.offset(anchor + a) - self.offset(anchor - a)).z / 0.5
        axis = Vector((0, 0, 1)).cross(along).normalized()
        if axis.length < 1e-9:
            return Matrix.Translation(off)
        ang = -math.atan(d) if axis.dot(Vector((0, 1, 0))) + axis.dot(Vector((-1, 0, 0))) > 0 else math.atan(d)
        rot = Matrix.Translation(anchor) @ Matrix.Rotation(ang, 4, axis) @ Matrix.Translation(-anchor)
        return Matrix.Translation(off) @ rot


# ---------------------------------------------------------------- pieces


class Face:
    __slots__ = ("p", "uv0", "chart", "cuv", "arris", "under")

    def __init__(self, p, uv0, chart, cuv, arris=False, under=False):
        self.p, self.uv0, self.chart, self.cuv, self.arris, self.under = p, uv0, chart, cuv, arris, under


class Piece:
    """One part in its own frame: built along local +x, outward local -y, up +z. `place` maps local to world rest;
    `mode` says how the frame moves it: 'frame' bends with the timber, 'rigid' is only moved and turned."""

    def __init__(self, pid, mat, levels, place=None, mode="frame", kind=None):
        self.id, self.mat, self.levels = pid, mat, levels
        self.place = place if place is not None else Matrix.Identity(4)
        self.mode = mode
        self.kind = kind or pid.split("/")[1]
        self.faces = {lv: [] for lv in levels}
        self.anchor = None
        self.along = None

    def add(self, level, face):
        self.faces[level].append(face)


CHARTS = {}  # key -> (w, h) metres, the same at every level


def chart(key, w, h):
    old = CHARTS.get(key)
    if old is None or old[0] < w or old[1] < h:
        CHARTS[key] = (max(w, old[0] if old else 0), max(h, old[1] if old else 0))
    return key


def extrude(piece, level, prof, o, L, P, Q, nseg=1, caps=(False, False), uvmode="strip", strip=None, tile_off=(0, 0),
            planar=None, cut=None):
    """Sweep a 2D profile along a straight line, in the piece's frame.

    prof: [(p, q, group, arris)] points in order (an open polyline); each edge (i, i+1) takes the group and arris of
    its first point. o: start; L: the sweep (a vector, its length the piece's length); P, Q: the profile's axes.
    UV0 'strip': u along the sweep, v the arc across its group (for the trim sheet and tileables; `strip` maps a
    group to (v0, width) in the sheet, metres of texture). Charts: each group's (length x nominal width) unless
    `planar` gives a function local point -> (chartkey, cu, cv, u0, v0) for wall-plane charting. `cut` (start, end)
    gives each end's offset along the sweep as a function of the profile point (p, q): an end sawn askew."""
    length = L.length
    d = L.normalized()
    prof = outward(prof, P, Q, d)
    # group arc lengths and the nominal width each group's chart takes
    groups = {}
    for i in range(len(prof) - 1):
        g = prof[i][2]
        a = math.dist(prof[i][:2], prof[i + 1][:2])
        groups.setdefault(g, [0.0, []])
        groups[g][1].append((i, groups[g][0], a))
        groups[g][0] += a
    for i in range(len(prof) - 1):
        g, arris = prof[i][2], prof[i][3]
        total = groups[g][0]
        start = next(s for (j, s, a) in groups[g][1] if j == i)
        a = math.dist(prof[i][:2], prof[i + 1][:2])
        nominal = piece_nominal(piece, g, total)
        for k in range(nseg):
            t0, t1 = k / nseg, (k + 1) / nseg
            pts, uv0, cuv = [], [], []
            for (t, j, s) in ((t0, i, start), (t1, i, start), (t1, i + 1, start + a), (t0, i + 1, start + a)):
                along = t * length + (cut[int(t)](*prof[j][:2]) if cut is not None and t in (0, 1) else 0.0)
                p = o + d * along + P * prof[j][0] + Q * prof[j][1]
                pts.append(p)
                frac = s / total if total > 0 else 0.0
                if planar is not None:
                    key, cu, cv, u0, v0 = planar(p)
                    uv0.append((u0 + tile_off[0], v0 + tile_off[1]))
                    cuv.append((cu, cv))
                else:
                    u = along
                    if strip is not None:
                        v0s, ws = strip(g, nominal)
                        uv0.append((u + tile_off[0], v0s + frac * ws))
                    else:
                        uv0.append((u + tile_off[0], frac * nominal + tile_off[1]))
                    cuv.append((u, frac * nominal))
            key = planar(pts[0])[0] if planar is not None else chart(f"{piece.id}#{g}", length, nominal)
            piece.add(level, Face(pts, uv0, key, cuv, arris))
    for end, on in ((0, caps[0]), (1, caps[1])):
        if not on:
            continue
        t = end * length
        bounds = cap_bounds(prof)
        ring = list(prof)
        pts = [o + d * (t + (cut[end](*p[:2]) if cut is not None else 0.0)) + P * p[0] + Q * p[1] for p in ring]
        # the start cap faces back along the sweep, the end cap forward
        if newell(pts).dot(d) * (1 if end else -1) < 0:
            pts, ring = pts[::-1], ring[::-1]
        key = chart(f"{piece.id}#cap{end}", *cap_size(prof))
        cuv = [((p[0] - bounds[0]), (p[1] - bounds[1])) for p in ring]
        uv0 = [(c[0] + tile_off[0], c[1] + tile_off[1]) for c in cuv]
        piece.add(level, Face(pts, uv0, key, cuv, False))


def newell(pts):
    n = Vector((0.0, 0.0, 0.0))
    for i, a in enumerate(pts):
        b = pts[(i + 1) % len(pts)]
        n += Vector(((a.y - b.y) * (a.z + b.z), (a.z - b.z) * (a.x + b.x), (a.x - b.x) * (a.y + b.y)))
    return n


def outward(prof, P, Q, d):
    """Walk the profile so every swept face looks away from the solid: with (P, Q, d) right-handed a face's normal
    is its edge turned left, so the closed section must run clockwise in (p, q). Each point carries the attributes
    of the edge leaving it, so a reversed walk shifts them by one."""
    area = sum(a[0] * b[1] - b[0] * a[1] for a, b in zip(prof, prof[1:] + prof[:1]))
    hand = P.cross(Q).dot(d)
    if area * hand <= 0:
        return prof
    n = len(prof)
    pts = prof[::-1]
    return [(pts[k][0], pts[k][1]) + tuple(prof[n - 2 - k][2:]) if k < n - 1 else pts[k] for k in range(n)]


NOMINAL = {}


def piece_nominal(piece, g, total):
    """A group's chart width: the street level's (unchamfered) width when the piece declared it, else its arc."""
    return NOMINAL.get((piece.id, g), total)


def cap_size(prof):
    b = cap_bounds(prof)
    return (max(b[2] - b[0], 0.005), max(b[3] - b[1], 0.005))


def cap_bounds(prof):
    ps = [p[0] for p in prof]
    qs = [p[1] for p in prof]
    return (min(ps), min(qs), max(ps), max(qs))


def rect_profile(w, h, c, groups=("bottom", "front", "top", "back"), chamfer_edges=(True, True), closed=False,
                 back=False):
    """A board's section, p across (0..w), q out of the wall (0..h): points walk bottom -> front -> top, each
    carrying the group and arris flag of the edge that leaves it. `c` chamfers the two front arrises when
    chamfer_edges says so; a chamfer belongs to the front's group and is flagged as an arris."""
    cb, ct = (c if chamfer_edges[0] else 0.0), (c if chamfer_edges[1] else 0.0)
    pts = [(0.0, 0.0, groups[0], False)]
    if cb > 0:
        pts += [(0.0, h - cb, groups[1], True), (cb, h, groups[1], False)]
    else:
        pts += [(0.0, h, groups[1], False)]
    if ct > 0:
        pts += [(w - ct, h, groups[1], True), (w, h - ct, groups[2], False)]
    else:
        pts += [(w, h, groups[2], False)]
    pts += [(w, 0.0, groups[3] if back else groups[2], False)]
    if back:
        pts += [(0.0, 0.0, groups[3], False)]
    return pts


# ---------------------------------------------------------------- the corner


class Corner:
    def __init__(self, spec, W, F, mats):
        self.S, self.W, self.F, self.M = spec, W, F, mats
        self.pieces = []
        self.features = {"butts": [], "nails": [], "sill": None, "eave": None, "foot": None, "casing": None,
                         "joints": [], "cornerBoard": None, "pipe": None, "drips": [], "battens": []}
        cl = W["cladding"]
        self.step = cl["stepMm"] * MM
        self.push = W["push"]
        self.ch = {k: v * MM for k, v in W["chamferMm"].items() if k != "describes"}
        self.lx = spec["sample"]["streetMm"] * MM
        self.ly = spec["sample"]["gableMm"] * MM
        # heights
        pl = W["plinth"]
        self.z_plinth = F.between(*[v * MM for v in pl["heightMm"]], "plinth", "height")
        self.z_floor = self.z_plinth + W["floorOverPlinthMm"] * MM
        dr = W["dripBoard"]
        self.z_drip0 = self.z_plinth - 0.03
        self.z_drip1 = self.z_drip0 + dr["heightMm"] * MM
        op = W["openings"]
        cs = W["casing"]
        self.sill_t = cs["sillMm"] * MM * self.push["sillThick"]
        self.z_open0 = self.z_floor + op["sillOverFloorMm"] * MM
        self.z_open1 = self.z_open0 + op["hMm"] * MM
        self.z_head1 = self.z_open1 + cs["headMm"] * MM
        self.cap_t = cs["capMm"] * MM * self.push["capThick"]
        self.z_top = self.z_floor + (W["storeyMm"] + W["floorMm"]) * MM
        self.x_open0 = op["edgeMm"] * MM
        self.x_open1 = self.x_open0 + op["wMm"] * MM
        self.cw = cs["widthMm"] * MM
        self.trim_proud = cs["proudMm"] * MM * self.push["trimProud"]
        self.frame = Frame(W, F, self.z_floor, self.z_top)
        self.pitch = math.radians(W["roofPitchDeg"])
        self.street_m = Matrix.Identity(4)
        self.gable_m = Matrix.Rotation(-math.pi / 2, 4, "Z")
        self.courses = self.course_table()

    # ---- the story pole: courses meet the drip board, the sill and the head's cap
    def course_table(self):
        lo, hi = [v * MM for v in self.W["cladding"]["exposureMm"]]
        bands = [(self.z_drip1, self.z_open0 - self.sill_t), (self.z_open0 - self.sill_t, self.z_head1 + self.cap_t),
                 (self.z_head1 + self.cap_t, self.z_top + 0.30)]
        zs = [bands[0][0]]
        n_all = 0
        for bi, (a, b) in enumerate(bands):
            mean = 0.5 * (lo + hi)
            n = max(1, round((b - a) / mean))
            draws = [self.F.between(lo, hi, "course", n_all + k, "exposure") for k in range(n)]
            k = (b - a) / sum(draws)
            z = a
            for e in draws:
                z += e * k
                zs.append(z)
            n_all += n
        return zs  # butt heights of each course, the last is above the sample

    # ---- planar charts for cladding: a wall's boards in the wall's plane
    def wall_planar(self, wall):
        tile = self.S["tileable"]["metres"]
        if wall == "street":
            x0, x1, z0, z1 = -0.06, self.lx, self.z_drip0 - 0.05, self.z_top + 0.32
            key = chart("wall/street", x1 - x0, z1 - z0)

            def f(p):
                return key, p.x - x0, p.z - z0, p.x, p.z
        else:
            x0, x1, z0, z1 = -self.ly, 0.06, self.z_drip0 - 0.05, self.z_top + 0.32
            key = chart("wall/gable", x1 - x0, z1 - z0)

            def f(p):
                return key, p.x - x0, p.z - z0, p.x, p.z
        return f

    def make(self, pid, mat, levels=("near", "street"), place=None, mode="frame"):
        pc = Piece(f"h{self.F.id}/{pid}", mat, levels, place, mode)
        self.pieces.append(pc)
        return pc

    def seed(self, *parts):
        return self.F.u(*parts)

    # ---- cladding
    def cladding(self):
        tile = self.S["tileable"]["metres"]
        c = self.W["cladding"]["butChamferMm"] * MM
        s = self.step
        for wall, place, x_lo, x_hi in (("street", self.street_m, 0.0, self.lx), ("gable", self.gable_m, -self.ly, 0.0)):
            planar = self.wall_planar(wall)
            zs = self.courses
            for ci in range(len(zs) - 1):
                zb, zt = zs[ci], zs[ci + 1]
                if zb >= self.z_top - 0.01 and wall == "street":
                    break
                if zb >= self.z_top + 0.27:
                    break
                zt = min(zt, self.z_top) if wall == "street" else zt
                spans = [(x_lo, x_hi)]
                in_window = wall == "street" and zt > self.z_open0 - self.sill_t + 0.005 and zb < self.z_head1 + self.cap_t - 0.005
                if in_window:
                    spans = [(x_lo, self.x_open0), (self.x_open1, x_hi)]
                if wall == "gable" and zb >= self.z_top - 0.01:
                    # the gable's triangle under the verge, as far as the sample's two courses reach
                    run = (zb - self.z_top) / math.tan(self.pitch)
                    spans = [(-0.42, -run)] if run < 0.42 else []
                # butt joints: boards are 2.6-5.2 m; a joint falls in the sample where the seed puts it
                cut = []
                for (a, b) in spans:
                    bl = self.F.between(2.6, 5.2, wall, "course", ci, "length")
                    j = a + bl * self.F.u(wall, "course", ci, "joint")
                    if a + 0.25 < j < b - 0.25 and b - a > 1.0:
                        cut += [(a, j - 0.001), (j + 0.001, b)]
                        self.features["joints"].append((wall, j, zb, zt))
                    else:
                        cut.append((a, b))
                for bi, (a, b) in enumerate(cut):
                    pc = self.make(f"clad/{wall}/c{ci:02d}b{bi}", "cladding", ("near",), place)
                    h = zt - zb
                    # section in (p = up the board, q = out): the butt's underside out to the step, its worn arris,
                    # then the face back to the top, which tucks under the course above
                    prof = [(0.0, 0.0, "front", False), (0.0, s - c, "front", True), (c, s, "front", False),
                            (h, 0.0, "front", False)]
                    nseg = max(1, round((b - a) / 0.5))
                    off = (self.seed(wall, ci, bi, "u") * 7.0, self.seed(wall, ci, bi, "v") * 7.0)
                    extrude(pc, "near", prof, Vector((a, 0.0, zb)), Vector((b - a, 0, 0)), Vector((0, 0, 1)),
                            Vector((0, -1, 0)), nseg=nseg, planar=planar, tile_off=off,
                            caps=(wall == "gable" and bi == 0 and a <= -self.ly + 1e-6,
                                  wall == "street" and b >= self.lx - 1e-6))
                    self.features["butts"].append((wall, a, b, zb))
            # street level: the wall as planes around the opening, its laps in the page's normal
            pc = self.make(f"clad/{wall}/plane", "cladding", ("street",), place)
            z0, z1 = zs[0], (self.z_top if wall == "street" else self.z_top)
            ymid = -0.5 * s
            if wall == "street":
                xs = [x_lo, self.x_open0, self.x_open1, x_hi]
                zc = [z0, self.z_open0 - self.sill_t, self.z_head1 + self.cap_t, z1]
                for i in range(3):
                    for j in range(3):
                        if i == 1 and j == 1:
                            continue
                        self.quad_planar(pc, "street", planar, xs[i], xs[i + 1], zc[j], zc[j + 1], ymid,
                                         nseg=max(1, round((xs[i + 1] - xs[i]) / 0.4)))
                self.end_cap_plane(pc, planar, x_hi, z0, z1, s, flip=True)
            else:
                self.quad_planar(pc, "street", planar, x_lo, x_hi, z0, z1, ymid, nseg=4)
                # the triangle under the verge's foot
                t = math.tan(self.pitch)
                tri = [Vector((-0.42, ymid, z1)), Vector((0.0, ymid, z1)), Vector((-0.42, ymid, z1 + 0.42 * t))]
                pts = tri
                uv0, cuv = [], []
                key = None
                for p in pts:
                    k, cu, cv, u0, v0 = planar(p)
                    key = k
                    uv0.append((u0, v0))
                    cuv.append((cu, cv))
                pc.add("street", Face(pts, uv0, key, cuv))
                self.end_cap_plane(pc, planar, x_lo, z0, z1, s)

    def quad_planar(self, pc, level, planar, x0, x1, z0, z1, y, nseg=1):
        for k in range(nseg):
            a = x0 + (x1 - x0) * k / nseg
            b = x0 + (x1 - x0) * (k + 1) / nseg
            pts = [Vector((a, y, z0)), Vector((b, y, z0)), Vector((b, y, z1)), Vector((a, y, z1))]
            uv0, cuv = [], []
            key = None
            for p in pts:
                key, cu, cv, u0, v0 = planar(p)
                uv0.append((u0, v0))
                cuv.append((cu, cv))
            pc.add(level, Face(pts, uv0, key, cuv))

    def end_cap_plane(self, pc, planar, x, z0, z1, s, flip=False):
        pts = [Vector((x, 0.0, z0)), Vector((x, -s, z0)), Vector((x, -s, z1)), Vector((x, 0.0, z1))]
        if flip:
            pts = pts[::-1]
        key = chart(f"{pc.id}#end", s, z1 - z0)
        cuv = [(abs(p.y), p.z - z0) for p in pts]
        pc.add("street", Face(pts, [(c[0], c[1]) for c in cuv], key, cuv))

    # ---- a trim: a board swept along its length, near with its arrises chamfered, street a box
    def trim(self, pid, place, o, L, P, Q, w, t, c, nseg=1, groups=("bottom", "front", "top"), caps=(True, True),
             chamfer_edges=(True, True), mode="frame", mat="trims", levels=("near", "street"), back=False):
        pc = self.make(pid, mat, levels, place, mode)
        for g, nominal in (((groups[1]), w), (groups[0], t), (groups[2], t)):
            NOMINAL[(pc.id, g)] = nominal
        for lv in levels:
            cc = c if lv == "near" else 0.0
            prof = rect_profile(w, t, cc, groups=groups + ("back",), chamfer_edges=chamfer_edges, back=back)
            # profile p across (along P), q outward (along Q)
            extrude(pc, lv, prof, o, L, P, Q, nseg=nseg, caps=caps, strip=self.strip(lv, c, mat), tile_off=(
                self.seed(pid, "u") * 7.0, 0.0))
        return pc

    def strip(self, level, chamfer, mat):
        """The trim sheet's strip a group maps to: its width's nearest strip, flat at near, bevelled at street."""
        if mat != "trims":
            return None
        ts = self.S["trimSheet"]
        widths = [w * MM for w in ts["stripsMm"]]
        n = len(widths)
        starts = trim_strips(ts)

        def f(group, nominal):
            i = min(range(n), key=lambda k: abs(widths[k] - nominal))
            return starts[level][i], widths[i]
        return f

    def corner_boards(self):
        cb = self.W["corner"]
        w = cb["widthMm"] * MM
        proud = cb["proudMm"] * MM * self.push["trimProud"]
        c = self.ch["corner"]
        z0, z1 = self.z_drip1 - 0.01, self.z_top
        H = z1 - z0
        # the street face's board covers the gable board's edge, so its outer arris is the house's corner; the gable
        # board runs back to meet it; both exposed arrises of each are worn
        s = self.step
        self.trim("corner/street", self.street_m, Vector((-(s + proud), -s, z0)), Vector((0, 0, H)),
                  Vector((1, 0, 0)), Vector((0, -1, 0)), w + s + proud, proud, c, nseg=3,
                  groups=("left", "front", "right"), chamfer_edges=(True, True), caps=(False, False))
        self.trim("corner/gable", self.gable_m, Vector((-w, -s, z0)), Vector((0, 0, H)),
                  Vector((1, 0, 0)), Vector((0, -1, 0)), w + s, proud, c, nseg=3,
                  groups=("left", "front", "right"), chamfer_edges=(True, False), caps=(False, False))
        self.features["cornerBoard"] = (w, proud, z0, z1)

    def drip_boards(self):
        dr = self.W["dripBoard"]
        h = dr["heightMm"] * MM
        proud = dr["proudMm"] * MM
        c = self.ch["drip"]
        for wall, place, a, b in (("street", self.street_m, -proud, self.lx), ("gable", self.gable_m, -self.ly, proud)):
            self.trim(f"drip/{wall}", place, Vector((a, -self.step + 0.0, self.z_drip0)), Vector((b - a, 0, 0)),
                      Vector((0, 0, 1)), Vector((0, -1, 0)), h, proud + self.step, c,
                      nseg=max(1, round((b - a) / 0.75)), groups=("bottom", "front", "top"),
                      caps=(wall == "gable", wall == "street"))
        self.features["foot"] = (self.z_drip0, self.z_drip1)

    def casing(self):
        cs = self.W["casing"]
        c = self.ch["casing"]
        p = self.trim_proud
        x0, x1 = self.x_open0, self.x_open1
        za, zb = self.z_open0, self.z_head1
        # the side boards, from the sill's top to the head's cap
        for side, x in (("l", x0 - self.cw), ("r", x1)):
            self.trim(f"casing/{side}", self.street_m, Vector((x, -self.step * 0.5, za)), Vector((0, 0, zb - za)),
                      Vector((1, 0, 0)), Vector((0, -1, 0)), self.cw, p, c, nseg=2,
                      groups=("left", "front", "right"), caps=(False, False))
        # the head's frieze board between them
        self.trim("casing/head", self.street_m, Vector((x0, -self.step * 0.5, self.z_open1)),
                  Vector((x1 - x0, 0, 0)), Vector((0, 0, 1)), Vector((0, -1, 0)), zb - self.z_open1, p * 0.8,
                  self.ch["small"] if "small" in self.ch else 0.006, nseg=1, caps=(False, False))
        # the head's cap: a water board over the whole casing, sloped to shed water, with a bed mould under it
        capw = (x1 + self.cw) - (x0 - self.cw) + 2 * 0.03
        cproud = cs["capProudMm"] * MM * self.push["capProud"]
        self.cap(x0 - self.cw - 0.03, capw, zb, cproud, self.cap_t, math.radians(cs["capSlopeDeg"]))
        bm = cs["bedMouldMm"]
        self.trim("casing/bed", self.street_m, Vector((x0 - self.cw - 0.01, -self.step * 0.5 - p, zb - bm[1] * MM)),
                  Vector((capw - 0.04, 0, 0)), Vector((0, 0, 1)), Vector((0, -1, 0)), bm[1] * MM, bm[0] * MM,
                  self.ch["bedMould"], caps=(True, True), chamfer_edges=(True, False))
        # the sill: a thick board with horns past the casing, its top falling outward
        horn = cs["hornMm"] * MM
        sp = cs["sillProudMm"] * MM * self.push["sillProud"]
        sx0, sx1 = x0 - self.cw - horn, x1 + self.cw + horn
        self.sill(sx0, sx1 - sx0, self.z_open0, sp, self.sill_t)
        self.features["sill"] = (sx0, sx1, self.z_open0 - self.sill_t, sp)
        self.features["casing"] = (x0 - self.cw, x1 + self.cw, za, zb + self.cap_t)

    def cap(self, x, length, z, proud, t, slope):
        """The head's drip cap: a flat board whose top falls outward by `slope`, the top's front arris chamfered, and
        a drip nose under its front edge so water leaves it clear of the casing."""
        c = self.ch["cap"]
        ct = self.ch["capTop"]
        dw, dh = [v * MM for v in self.W["casing"]["capDripMm"]]
        pc = self.make("casing/cap", "trims", ("near", "street"), self.street_m)
        d = proud
        rise = d * math.tan(slope)
        for lv in ("near", "street"):
            # section (p up, q out): under the board out to the drip nose, down its back and under it, the flat front,
            # the top's chamfered arris, then the top rising back to the wall
            if lv == "near":
                prof = [(0.0, 0.0, "bottom", False), (0.0, d - dw, "bottom", False), (-dh, d - dw, "bottom", False),
                        (-dh, d - c, "front", True), (-dh + c, d, "front", False),
                        (t - ct, d, "front", True), (t + rise * ct / d, d - ct, "top", False), (t + rise, 0.0, "top", False)]
            else:
                prof = [(0.0, 0.0, "bottom", False), (-dh, d, "front", False), (t, d, "top", False),
                        (t + rise, 0.0, "top", False)]
            NOMINAL[(pc.id, "bottom")] = d
            NOMINAL[(pc.id, "front")] = t
            NOMINAL[(pc.id, "top")] = math.hypot(d, rise)
            extrude(pc, lv, prof, Vector((x, -self.step * 0.5 - 0.0, z)), Vector((length, 0, 0)), Vector((0, 0, 1)),
                    Vector((0, -1, 0)), nseg=2, caps=(True, True), strip=self.strip(lv, c, "trims"),
                    tile_off=(self.seed("cap", "u") * 7.0, 0))

    def sill(self, x, length, ztop, proud, t):
        c = self.ch["sill"]
        pc = self.make("casing/sill", "trims", ("near", "street"), self.street_m)
        fall = 0.012
        for lv in ("near", "street"):
            cc = c if lv == "near" else 0.0
            # section (p up, q out): under the sill, its front with a worn top arris, the top falling outward
            if cc:
                prof = [(-t, 0.0, "bottom", False), (-t, proud - 0.004, "front", True), (-t + 0.004, proud, "front", False),
                        (-fall - cc, proud, "front", True), (-fall, proud - cc, "top", False), (0.0, 0.0, "top", False)]
            else:
                prof = [(-t, 0.0, "bottom", False), (-t, proud, "front", False), (-fall, proud, "top", False),
                        (0.0, 0.0, "top", False)]
            NOMINAL[(pc.id, "bottom")] = proud
            NOMINAL[(pc.id, "front")] = t
            NOMINAL[(pc.id, "top")] = proud
            extrude(pc, lv, prof, Vector((x, -self.step * 0.5, ztop)), Vector((length, 0, 0)), Vector((0, 0, 1)),
                    Vector((0, -1, 0)), nseg=2, caps=(True, True), strip=self.strip(lv, c, "trims"),
                    tile_off=(self.seed("sill", "u") * 7.0, 0))

    # ---- the eave: soffit, fascia, gutter on hooks, the verge's foot
    def eave(self):
        ev = self.W["eaves"]
        ov = ev["overhangMm"] * MM
        fh, ft = ev["fasciaMm"] * MM, ev["fasciaThickMm"] * MM
        st = ev["soffitThickMm"] * MM
        zt = self.z_top
        vg = self.W["verge"]
        vov = vg["overhangMm"] * MM
        xa = -vov - 0.015
        # soffit board under the eave, wall to fascia
        self.trim("eave/soffit", self.street_m, Vector((xa, -0.0, zt)), Vector((self.lx - xa, 0, 0)),
                  Vector((0, -1, 0)), Vector((0, 0, -1)), ov, st, self.ch["soffit"], nseg=4,
                  groups=("back", "under", "front"), chamfer_edges=(False, True), caps=(False, True))
        # fascia: a board standing on the soffit's edge
        self.trim("eave/fascia", self.street_m, Vector((xa, -ov, zt - st - 0.01)), Vector((self.lx - xa, 0, 0)),
                  Vector((0, 0, 1)), Vector((0, -1, 0)), fh, ft, self.ch["fascia"], nseg=4,
                  groups=("bottom", "front", "top"), caps=(True, True))
        self.features["eave"] = (zt, -ov - ft)
        # a gutter and downpipe only where the working has rainwater; the classical one has none, so the roof's
        # water leaves each pan at the eave's drip line (tiles())
        rw = self.W.get("rainwater")
        if rw:
            r = rw["gutterRadiusMm"] * MM
            gy = -ov - ft - r - 0.012
            gz = zt - st - 0.01 + fh - 0.035
            gx0 = xa + 0.01
            self.gutter(gx0, self.lx, gy, gz, r, rw)
            self.downpipe(gx0, gy, gz, r, rw)
        # the verge's barge board, its foot over the gable's corner
        bt = vg["thickMm"] * MM * self.push["bargeThick"]
        bw = vg["boardMm"] * MM
        run = 0.62
        place = self.gable_m
        t = math.tan(self.pitch)
        pc = self.make("verge/barge", "trims", ("near", "street"), place)
        L = Vector((-run, 0, run * t))
        o = Vector((ov + 0.01, -vov + bt * 0.0, zt - st - 0.01))
        for lv in ("near", "street"):
            cc = self.ch["barge"] if lv == "near" else 0.0
            prof = rect_profile(bw, bt, cc, groups=("bottom", "front", "top", "back"), chamfer_edges=(True, True))
            NOMINAL[(pc.id, "front")] = bw
            NOMINAL[(pc.id, "bottom")] = bt
            NOMINAL[(pc.id, "top")] = bt
            n = Vector((0, 0, 1)) - L.normalized() * L.normalized().z
            extrude(pc, lv, prof, o, L, n.normalized(), Vector((0, -1, 0)), nseg=1, caps=(True, False),
                    strip=self.strip(lv, self.ch["barge"], "trims"), tile_off=(self.seed("barge", "u") * 7, 0))

    def gutter(self, x0, x1, gy, gz, r, rw):
        n = 8
        pc = self.make("eave/gutter", "zinc", ("near", "street"), self.street_m)
        th = rw["gutterThickMm"] * MM
        for lv in ("near", "street"):
            k = n if lv == "near" else 4
            outer = [(r * math.cos(math.pi * i / k), -r * math.sin(math.pi * i / k)) for i in range(k + 1)]
            # sweep along x; profile p = local y (back to front), q = z; outside then inside
            prof = [(-p, q, "outside", False) for (p, q) in outer]
            inner = [(-p * (1 - th / r), q * (1 - th / r) + 0.0, "inside", False) for (p, q) in outer][::-1]
            bead = rw["beadMm"] * MM
            prof += [(r + bead * 0.3, bead * 0.6, "outside", False)] + inner
            prof = [(p, q, g, a) for (p, q, g, a) in prof]
            NOMINAL[(pc.id, "outside")] = math.pi * r
            NOMINAL[(pc.id, "inside")] = math.pi * r
            extrude(pc, lv, prof, Vector((x0, gy, gz)), Vector((x1 - x0, 0, 0)), Vector((0, -1, 0)), Vector((0, 0, 1)),
                    nseg=4 if lv == "near" else 3, caps=(True, False), tile_off=(self.seed("gutter", "u") * 7, 0))
        # hooks: flat irons from the fascia under the gutter
        hw, ht = [v * MM for v in rw["hookMm"]]
        every = rw["hookEveryMm"] * MM
        i = 0
        x = x0 + 0.12
        while x < x1 - 0.05:
            pc = self.make(f"eave/hook{i}", "zinc", ("near",), self.street_m)
            # a flat iron cradling the gutter from its lip round to its back, then up to the fascia
            ri, ro = r + th, r + th + ht
            pts = [(ri * math.cos(math.pi * j / 4), -ri * math.sin(math.pi * j / 4)) for j in range(4, -1, -1)]
            pts += [(ri, 0.03), (ro, 0.03)]
            pts += [(ro * math.cos(math.pi * j / 4), -ro * math.sin(math.pi * j / 4)) for j in range(5)]
            pts.append(pts[0])
            prof = [(-p, q, "iron", False) for (p, q) in pts]
            extrude(pc, "near", prof, Vector((x - hw / 2, gy, gz)), Vector((hw, 0, 0)), Vector((0, -1, 0)),
                    Vector((0, 0, 1)), nseg=1)
            x += every
            i += 1

    def downpipe(self, gx0, gy, gz, r, rw):
        """From the outlet near the gutter's end, a swan neck back to the wall, down to a shoe; rigid zinc."""
        pr = rw["pipeRadiusMm"] * MM
        x = gx0 + rw["outletFromEndMm"] * MM
        y_wall = -self.step - rw["offWallMm"] * MM - pr
        z_out = gz - r - 0.01
        dy = y_wall - gy
        neck = abs(dy)
        path = [Vector((x, gy, z_out)), Vector((x, gy, z_out - 0.07)), Vector((x, y_wall, z_out - 0.07 - neck)),
                Vector((x, y_wall, z_out - 0.07 - neck - 0.06))]
        z_shoe = rw["shoeMm"] * MM
        path += [Vector((x, y_wall, z_shoe + 0.06)), Vector((x, y_wall - 0.08, z_shoe - 0.02))]
        self.features["pipe"] = (x, y_wall, pr, z_shoe, z_out)
        for i in range(len(path) - 1):
            a, b = path[i], path[i + 1]
            pc = self.make(f"pipe/s{i}", "zinc", ("near", "street"), mode="rigid")
            d = (b - a)
            up = Vector((0, 0, 1)) if abs(d.normalized().z) < 0.9 else Vector((0, -1, 0))
            P = d.cross(up).normalized()
            Q = d.cross(P).normalized()
            ext = 0.012 if i < len(path) - 2 else 0.0
            a2 = a - d.normalized() * (0.012 if i > 0 else 0.0)
            b2 = b + d.normalized() * ext
            for lv in ("near", "street"):
                k = 8 if lv == "near" else 4
                prof = [(pr * math.cos(2 * math.pi * j / k), pr * math.sin(2 * math.pi * j / k), "round", False)
                        for j in range(k + 1)]
                NOMINAL[(pc.id, "round")] = 2 * math.pi * pr
                extrude(pc, lv, prof, a2, b2 - a2, P, Q, nseg=max(1, round((b2 - a2).length / 1.2)),
                        caps=(False, i == len(path) - 2), tile_off=(self.seed("pipe", i) * 7, 0))
            pc.anchor = Vector((x, y_wall, 1.5))
        # clips round the pipe to the wall
        every = rw["clipEveryMm"] * MM
        cw_, ct_ = [v * MM for v in rw["clipMm"]]
        z = z_shoe + 0.45
        i = 0
        while z < z_out - 0.07 - neck - 0.1:
            pc = self.make(f"pipe/clip{i}", "zinc", ("near",), mode="rigid")
            prof = [((pr + ct_) * math.cos(2 * math.pi * j / 8), (pr + ct_) * math.sin(2 * math.pi * j / 8), "iron", False)
                    for j in range(9)]
            extrude(pc, "near", prof, Vector((x, y_wall, z)), Vector((0, 0, cw_)), Vector((1, 0, 0)), Vector((0, 1, 0)),
                    caps=(True, True))
            pc.anchor = Vector((x, y_wall, z))
            z += every
            i += 1

    # ---- the boarding of 1986: sheets inside the casing, battens nailed across it; rough, rigid, proud
    def boarding(self):
        bd = self.W["boarding"]
        F = self.F
        x0, x1 = self.x_open0, self.x_open1
        za, zb = self.z_open0, self.z_open1
        t = bd["sheetThickMm"] * MM
        top_gap = F.between(*bd["topGapMm"], "board", "topgap") * MM
        y_set = -self.step * 0.5 - self.trim_proud
        n = bd["sheetsHigh"]
        hs = (zb - za - top_gap)
        split = 0.45 + 0.2 * F.u("board", "split")
        heights = [hs * split, hs * (1 - split)] if n == 2 else [hs]
        z = za + 0.002
        for i, h in enumerate(heights):
            g = F.between(*bd["sideGapMm"], "board", "sheet", i, "gap") * MM
            # each sheet set back by its own amount, so the join between two steps: a lip that throws a line of shadow
            y_face = y_set + F.between(*bd["setBackMm"], "board", "sheet", i, "setback") * MM
            pc = self.make(f"board/sheet{i}", "sheet", ("near", "street"), mode="rigid")
            sx0, sx1 = x0 + g * 0.5, x1 - g * 0.5
            for lv in ("near", "street"):
                cc = self.ch["sheet"] if lv == "near" else 0.0
                prof = rect_profile(h - 0.003, t, cc, groups=("bottom", "front", "top", "back"))
                NOMINAL[(pc.id, "front")] = h - 0.003
                NOMINAL[(pc.id, "bottom")] = t
                NOMINAL[(pc.id, "top")] = t
                extrude(pc, lv, prof, Vector((sx0, y_face + t, z)), Vector((sx1 - sx0, 0, 0)), Vector((0, 0, 1)),
                        Vector((0, -1, 0)), caps=(True, True), tile_off=(F.u("board", i, "u") * 7, F.u("board", i, "v") * 7))
            pc.anchor = Vector(((sx0 + sx1) / 2, y_face, z + h / 2))
            pc.along = Vector((1, 0, 0))
            pc.extent = (sx0, sx1, z, z + h)
            z += h
        self.features["sheets"] = (x0, x1, za, zb - top_gap, y_set + bd["setBackMm"][0] * MM)
        # battens across the casing, past it onto the cladding, out of level by the hand that nailed them
        bt = bd["battens"]
        th = bt["thickMm"] * MM
        y_b = -self.step * 0.5 - self.trim_proud
        span = zb - za
        for i in range(bt["count"]):
            w = F.between(*bt["widthMm"], "batten", i, "width") * MM
            zc = za + span * (0.28 + 0.46 * i) + (F.u("batten", i, "z") - 0.5) * 0.12
            pl = F.between(*bt["pastCasingMm"], "batten", i, "left") * MM
            pr = F.between(*bt["pastCasingMm"], "batten", i, "right") * MM
            bx0, bx1 = x0 - self.cw - pl, x1 + self.cw + pr
            tilt = math.radians(F.between(*bt["outOfLevelDeg"], "batten", i, "tilt")) * (1 if F.u("batten", i, "sign") < 0.5 else -1)
            pc = self.make(f"board/batten{i}", "batten", ("near", "street"), mode="rigid")
            L = Vector((math.cos(tilt), 0, math.sin(tilt))) * (bx1 - bx0)
            # centred on zc at its middle, where its nails are reckoned from
            o = Vector((bx0, y_b, zc - w / 2 - math.tan(tilt) * (bx1 - bx0) / 2))
            self.features["battens"].append((bx0, bx1, zc, math.tan(tilt), w))
            # each end sawn off by hand, askew across the face and through the board
            ec = bt["endCutDeg"]
            ends = [(math.tan(math.radians(F.between(-ec[0], ec[0], "batten", i, e, "face"))),
                     math.tan(math.radians(F.between(-ec[1], ec[1], "batten", i, e, "through")))) for e in ("start", "end")]
            cut = tuple((lambda p, q, a=a, b=b: a * (p - w / 2) + b * (q - th / 2)) for a, b in ends)
            for lv in ("near", "street"):
                cc = self.ch["batten"] if lv == "near" else 0.0
                prof = rect_profile(w, th, cc, groups=("bottom", "front", "top", "back"))
                NOMINAL[(pc.id, "front")] = w
                NOMINAL[(pc.id, "bottom")] = th
                NOMINAL[(pc.id, "top")] = th
                extrude(pc, lv, prof, o, L, Vector((-math.sin(tilt), 0, math.cos(tilt))), Vector((0, -1, 0)),
                        caps=(True, True), tile_off=(F.u("batten", i, "u") * 7, 0.0), cut=cut)
            pc.anchor = Vector(((bx0 + bx1) / 2, y_b, zc))
            pc.along = Vector((1, 0, 0))
            # nails: two at each casing it crosses
            for side, xc in (("l", x0 - self.cw / 2), ("r", x1 + self.cw / 2)):
                for k in range(bt["nailsPerEnd"]):
                    zz = zc + (math.tan(tilt) * (xc - (bx0 + bx1) / 2)) + (k - 0.5) * w * 0.5
                    self.features["nails"].append((xc + (F.u("nail", i, side, k) - 0.5) * 0.04, zz))

    # ---- the plinth: split fieldstone, rigid, each stone moved and turned to its bed
    def plinth(self):
        pl = self.W["plinth"]
        F = self.F
        zt = self.z_plinth
        depth = pl["depthMm"] * MM
        joint = lambda k: F.between(*pl["jointMm"], "plinth", k, "joint") * MM  # noqa: E731
        y_face = -self.step - 0.012
        for wall, place, length in (("street", self.street_m, self.lx), ("gable", self.gable_m, self.ly)):
            # stones along the wall; the corner stone shared, drawn on the street wall's list
            xs = []
            if wall == "street":
                x = F.between(*[v * MM for v in pl["cornerStoneMm"]], "plinth", "corner")
                xs.append((-0.0, x, True))
            else:
                x = 0.0 + F.between(0.35, 0.6, "plinth", "cornerdepth")
            k = 0
            while x < length - 0.05:
                L = F.between(*[v * MM for v in pl["stoneMm"]], "plinth", wall, k, "len")
                j = joint((wall, k))
                a = x + j
                b = min(a + L, length + 0.2)
                xs.append((a, b, False))
                x = b
                k += 1
            pc_m = self.make(f"plinth/{wall}/mortar", "stone", ("near", "street"), place)
            # the mortar's bed, set back behind the stones' faces
            for lv in ("near", "street"):
                a0 = -0.02 if wall == "street" else -length
                a1 = length if wall == "street" else 0.02
                yb = y_face + pl["jointBackMm"] * MM
                pts = [Vector((a0, yb, 0.0)), Vector((a1, yb, 0.0)), Vector((a1, yb, zt)), Vector((a0, yb, zt))]
                key = chart(f"plinth/{wall}", (length + 0.25), zt + 0.05)
                cuv = [(p.x - a0, p.z) for p in pts]
                pc_m.add(lv, Face(pts, [(p.x, p.z) for p in pts], key, cuv, under=True))
            for si, (a, b, corner) in enumerate(xs):
                sid = f"plinth/{wall}/s{si}"
                self.stone(sid, wall, place, a, b, zt, y_face, depth, corner, length)

    def stone(self, sid, wall, place, a, b, zt, y_face, depth, corner, wall_len):
        pl = self.W["plinth"]
        F = self.F
        bulge = F.between(*pl["faceBulgeMm"], sid, "bulge") * MM
        arr = F.between(*pl["arrisMm"], sid, "arris") * MM
        h = zt - 0.004
        # on the gable the stone runs along -x local; the street's corner stone returns onto the gable (its end)
        if wall == "gable":
            a, b = -b, -a
        pc = self.make(sid, "stone", ("near", "street"), place, mode="rigid")
        set_out = F.between(*pl["setOutMm"], sid, "out") * MM
        yf = y_face - set_out
        key = chart(f"plinth/{wall}", wall_len + 0.25, zt + 0.05)
        a0 = -0.02 if wall == "street" else -wall_len

        def cu(p):
            return (p.x - a0, p.z)
        for lv in ("near", "street"):
            ar = arr if lv == "near" else 0.0
            nx, nz = (3, 2) if lv == "near" else (1, 1)
            # the split face: a pillow, high in its middle, its border worn back by the arris
            grid = []
            for j in range(nz + 1):
                row = []
                for i in range(nx + 1):
                    u, v = i / nx, j / nz
                    x = a + ar + (b - a - 2 * ar) * u
                    z = ar + (h - 2 * ar) * v
                    edge = min(u, 1 - u, v, 1 - v)
                    lump = bulge * (math.sin(math.pi * u) * math.sin(math.pi * v)) ** 0.7
                    lump *= 0.75 + 0.5 * F.u(sid, "lump", i, j)
                    row.append(Vector((x, yf - lump, z)))
                grid.append(row)
            if lv == "street":
                c = Vector(((a + b) / 2, yf - bulge * 0.8, h / 2))
                ring = [Vector((a, yf, 0.004)), Vector((b, yf, 0.004)), Vector((b, yf, h)), Vector((a, yf, h))]
                for i in range(4):
                    pts = [ring[i], ring[(i + 1) % 4], c]
                    pc.add(lv, Face(pts, [cu(p) for p in pts], key, [cu(p) for p in pts]))
                continue
            for j in range(nz):
                for i in range(nx):
                    pts = [grid[j][i], grid[j][i + 1], grid[j + 1][i + 1], grid[j + 1][i]]
                    pc.add(lv, Face(pts, [cu(p) for p in pts], key, [cu(p) for p in pts]))
            # the worn arris ring, out to the stone's true edge, then its sides back into the joint
            border = [grid[0][i] for i in range(nx + 1)] + [grid[j][nx] for j in range(1, nz + 1)] + \
                     [grid[nz][i] for i in range(nx - 1, -1, -1)] + [grid[j][0] for j in range(nz - 1, 0, -1)]
            outer = []
            for p in border:
                q = Vector((min(max(p.x, a + 0.0), b), yf + ar * 0.6, p.z))
                if abs(p.x - (a + ar)) < 1e-6:
                    q.x = a
                if abs(p.x - (b - ar)) < 1e-6:
                    q.x = b
                if abs(p.z - ar) < 1e-6:
                    q.z = 0.004
                if abs(p.z - (h - ar)) < 1e-6:
                    q.z = h
                outer.append(q)
            m = len(border)
            for i in range(m):
                pts = [outer[i], outer[(i + 1) % m], border[(i + 1) % m], border[i]]
                pc.add(lv, Face(pts, [cu(p) for p in pts], key, [cu(p) for p in pts], arris=True))
            back = [Vector((p.x, yf + 0.03, p.z)) for p in outer]
            for i in range(m):
                pts = [back[i], back[(i + 1) % m], outer[(i + 1) % m], outer[i]]
                pc.add(lv, Face(pts, [cu(p) for p in pts], key, [cu(p) for p in pts]))
        pc.anchor = place @ Vector(((a + b) / 2, yf, 0.0))
        pc.along = (place.to_3x3() @ Vector((1, 0, 0)))

    # ---- pantiles: the first two courses over the eave, each tile laid and turned a little by hand
    def tiles(self):
        tl = {**self.M["clay-pantile"]["laid"], **{k: v for k, v in self.W["pantile"].items() if k != "describes"}}
        F = self.F
        cover, course, roll = tl["coverMm"] * MM, tl["courseMm"] * MM, tl["rollMm"] * MM
        thick, lift, lap = tl["thickMm"] * MM, tl["liftMm"] * MM, tl["lapMm"] * MM / (tl["coverMm"] * MM)
        pan, rnd = tl["panAt"], tl["roundness"]
        ev = self.W["eaves"]
        ov = ev["overhangMm"] * MM
        ft = ev["fasciaThickMm"] * MM
        fh = ev["fasciaMm"] * MM
        st = ev["soffitThickMm"] * MM
        vg = self.W["verge"]
        x0 = -vg["overhangMm"] * MM - tl["verge"]["pastMm"] * MM
        n = math.ceil((self.lx - x0) / cover)
        cs, sn = math.cos(self.pitch), math.sin(self.pitch)
        # the batten plane: the fascia's top at the eave, rising inward
        y_foot = -ov - ft - 0.05
        z_foot = self.z_top - st - 0.01 + fh + 0.004
        up = Vector((0, cs, sn))  # up the slope
        nrm = Vector((0, -sn, cs))  # out of the roof

        def wave(u):
            """One wave across a cover, 0 at the pan's floor (panAt) to 1 at the roll's crown half a cover on; raised
            to `roundness` the pan widens and flattens and the roll narrows, as the tile is made."""
            return (0.5 - 0.5 * math.cos(2.0 * math.pi * (u - pan))) ** rnd

        # a near tile runs from 0 to past its cover by the lap, where it lies on the next tile's pan edge; its
        # samples hold the pan's floor and the roll's crown
        k = self.S["levels"]["near"]["pantileSamples"]
        us = [i * (1.0 + lap) / (k - 1) for i in range(k)]
        for target in (pan, pan + 0.5):
            j = min(range(1, k - 1), key=lambda i: abs(us[i] - target))
            us[j] = target
        near_prof = [(u, wave(u) + (thick / roll) * min(1.0, max(0.0, (u - 0.9) / 0.1))) for u in sorted(us)]
        # the street level: one wave along each course, sampled at the floor, the flanks and the crown
        ks = self.S["levels"]["street"]["pantileSamples"]
        street_u = []
        u = pan - math.ceil(pan * ks) / ks
        while u < (self.lx - x0) / cover:
            street_u.append(max(0.0, u))
            u += 1.0 / ks
        street_u.append((self.lx - x0) / cover)
        street_prof = [(u, wave(u)) for u in street_u]
        length = course + 0.075
        for ci in range(self.S["sample"]["courses"]):
            key = chart(f"roof/c{ci}", self.lx - x0 + 0.1, length + 0.05)
            base = Vector((0, y_foot, z_foot)) + up * (course * ci)
            for lv in ("near", "street"):
                tiles_ = range(n) if lv == "near" else (None,)
                for ti in tiles_:
                    if lv == "near":
                        tid = f"roof/c{ci}/t{ti}"
                        pc = self.make(tid, "tiles", ("near",))
                        # each tile turned and seated a little by the hand that laid it (seeded: claims no history)
                        yaw = math.radians(1.6) * (2 * F.u(tid, "yaw") - 1)
                        dz = 0.004 * (2 * F.u(tid, "seat") - 1)
                        xa, prof = x0 + ti * cover, near_prof
                    else:
                        pc = self.make(f"roof/c{ci}/strip", "tiles", ("street",))
                        yaw, dz, xa, prof = 0.0, 0.0, x0, street_prof
                    foot = base + Vector((xa, 0, 0)) + nrm * (lift * 0.35 + dz)
                    head = base + Vector((xa, 0, 0)) + up * length - nrm * (lift * 0.15)
                    rot = Matrix.Rotation(yaw, 3, nrm)

                    def pt(u, hgt, at):
                        return at + rot @ (Vector((u * cover, 0, 0)) + nrm * (hgt * roll))
                    rows = (foot, head)
                    if ci == 0 and lv == "near":
                        # with no gutter, each pan's water leaves its foot at the eave: where it lands and how much
                        # runs in it (the seed's: how the tile lies, claiming no history)
                        drop = pt(pan, 0.0, foot)
                        self.features["drips"].append((drop.x, drop.y, 0.35 + 0.65 * F.u(tid, "flow")))
                    for j in range(len(prof) - 1):
                        (ua, ha), (ub, hb) = prof[j], prof[j + 1]
                        pts = [pt(ua, ha, rows[0]), pt(ub, hb, rows[0]), pt(ub, hb, rows[1]), pt(ua, ha, rows[1])]
                        cuv = [(p.x - x0, (p - base).dot(up)) for p in pts]
                        pc.add(lv, Face(pts, [(p.x, (p - base).dot(up)) for p in pts], key, cuv))
                        # the tile's foot: its thickness facing down the slope
                        f0, f1 = pts[0], pts[1]
                        dn = -nrm * thick
                        fp = [f0 + dn, f1 + dn, f1, f0]
                        cuv = [(p.x - x0, max(0.0, (p - base).dot(up))) for p in fp]
                        pc.add(lv, Face(fp, [(p.x, p.z) for p in fp], key, cuv))
                        if ci == 0 and lv == "near":
                            # under the first course, seen from the street below
                            ub_ = [f1 + dn, f0 + dn, pts[3] - nrm * thick, pts[2] - nrm * thick]
                            ub_ = [ub_[0], ub_[1], ub_[1] + up * 0.10, ub_[0] + up * 0.10]
                            cuv = [(p.x - x0, max(0.0, (p - base).dot(up))) for p in ub_]
                            pc.add(lv, Face(ub_, [(p.x, p.z) for p in ub_], key, cuv))
        self.features["roof"] = (x0, y_foot, z_foot, self.W["roofPitchDeg"])

    def build(self):
        self.cladding()
        self.corner_boards()
        self.drip_boards()
        self.casing()
        self.boarding()
        self.eave()
        self.plinth()
        self.tiles()


# ---------------------------------------------------------------- page packing


def pack(spec):
    pg = spec["page"]
    px = pg["pxPerM"]
    size = pg["size"]
    pad = pg["padPx"]
    items = sorted(CHARTS.items(), key=lambda kv: (-math.ceil(kv[1][1] * px), kv[0]))
    x = y = row_h = 0
    out = {}
    for key, (w, h) in items:
        wp, hp = math.ceil(w * px) + 2 * pad, math.ceil(h * px) + 2 * pad
        if x + wp > size:
            x, y, row_h = 0, y + row_h, 0
        out[key] = (x + pad, y + pad, wp - 2 * pad, hp - 2 * pad)
        x += wp
        row_h = max(row_h, hp)
    if y + row_h > size:
        raise SystemExit(f"[corner] the page is full: {y + row_h} px of {size}")
    return out, (y + row_h) / size


# ---------------------------------------------------------------- Blender objects


def to_object(name, faces, place_of, deform, rects, spec, colour_of):
    px = spec["page"]["pxPerM"]
    size = spec["page"]["size"]
    tile = spec["tileable"]["metres"]
    mesh = bpy.data.meshes.new(name)
    verts, polys, uv0, uv1, cols, rest, pieces = [], [], [], [], [], [], []
    for (pc, f) in faces:
        idx = []
        M = place_of(pc)
        for p in f.p:
            w = M @ p
            rest.append(tuple(w))
            verts.append(tuple(deform(pc, w)))
            idx.append(len(verts) - 1)
        polys.append(idx)
        rx, ry, rw, rh = rects[f.chart]
        for (u, v), (cu, cv) in zip(f.uv0, f.cuv):
            uv0.append((u / tile, v / tile))
            uv1.append(((rx + cu * px) / size, (ry + cv * px) / size))
        cols.append(colour_of(pc, f, [M @ p for p in f.p]))
        pieces.append(pc.index)
    mesh.from_pydata(verts, [], polys)
    mesh.update()
    l0 = mesh.uv_layers.new(name="uv0")
    l1 = mesh.uv_layers.new(name="page")
    l0.data.foreach_set("uv", [c for uv in uv0 for c in uv])
    l1.data.foreach_set("uv", [c for uv in uv1 for c in uv])
    ca = mesh.color_attributes.new("Col", "FLOAT_COLOR", "CORNER")
    flat = []
    for poly, c in zip(mesh.polygons, cols):
        for k in range(poly.loop_total):
            flat += c[k] if isinstance(c[0], list) else c
    ca.data.foreach_set("color", flat)
    ra = mesh.attributes.new("rest", "FLOAT_VECTOR", "POINT")
    ra.data.foreach_set("vector", [c for r in rest for c in r])
    pa = mesh.attributes.new("piece", "INT", "FACE")
    pa.data.foreach_set("value", pieces)
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    finish_normals(obj)
    return obj


def finish_normals(obj):
    """Face-weighted normals: big faces stay flat, chamfers roll the light between them; a turn over 50 degrees is
    a hard edge."""
    me = obj.data
    bm = bmesh.new()
    bm.from_mesh(me)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-6)
    for f in bm.faces:
        f.smooth = True
    for e in bm.edges:
        if len(e.link_faces) == 2:
            a = e.link_faces[0].normal.angle(e.link_faces[1].normal, 0.0)
            e.smooth = a < math.radians(50)
        else:
            e.smooth = True
    bm.to_mesh(me)
    bm.free()
    me.update()
    bpy.context.view_layer.objects.active = obj
    for o in bpy.context.selected_objects:
        o.select_set(False)
    obj.select_set(True)
    mod = obj.modifiers.new("weighted", "WEIGHTED_NORMAL")
    mod.mode = "FACE_AREA"
    mod.weight = 100
    mod.keep_sharp = True
    bpy.ops.object.modifier_apply(modifier=mod.name)


def tris_of(obj):
    return sum(len(p.vertices) - 2 for p in obj.data.polygons)


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    out = os.path.join(ROOT, "unity/Assets/Experiments/LT1/Finish/Generated")
    if "--out" in argv:
        out = os.path.abspath(argv[argv.index("--out") + 1])
    os.makedirs(out, exist_ok=True)
    spec = load("blender/parts/finish/corner.json")
    W = load(spec["working"])
    F = Facts(spec)
    mats = {m: load(f"packs/stavanger-1989/materials/{m}.json") for m in ("clay-pantile", "fieldstone", "pine")}
    corner = Corner(spec, W, F, mats)
    corner.build()
    rects, fill = pack(spec)
    for i, pc in enumerate(corner.pieces):
        pc.index = i

    bpy.ops.wm.read_factory_settings(use_empty=True)

    def place_of(pc):
        return pc.place

    def deform(pc, w):
        if pc.mode == "frame":
            return corner.frame(w)
        return w  # rigid pieces move as a whole below

    rigid = {}
    for pc in corner.pieces:
        if pc.mode == "rigid":
            anchor = pc.anchor if pc.anchor is not None else Vector((0, 0, 0))
            rigid[pc.id] = corner.frame.rigid(anchor, pc.along)

    def deform_r(pc, w):
        if pc.mode == "rigid":
            return rigid[pc.id] @ w
        return corner.frame(w)

    lap_reach = spec["lapReach"]

    def colour(pc, f, world):
        rgb = [1.0 if f.arris else 0.0, F.u(pc.id, "seed"), 1.0 if f.under else 0.0]
        board = re.search(r"/c(\d+)b\d+$", pc.id) if pc.kind == "clad" else None
        if board is None:
            return rgb + [1.0]
        z_next = corner.courses[int(board.group(1)) + 1]
        return [rgb + [min(1.0, max(0.0, z_next - w.z) / lap_reach)] for w in world]

    counts = {}
    objs = {}
    for lv in ("near", "street"):
        by_mat = {}
        for pc in corner.pieces:
            if lv not in pc.levels:
                continue
            for f in pc.faces[lv]:
                by_mat.setdefault(pc.mat, []).append((pc, f))
        for mat in sorted(by_mat):
            o = to_object(f"{lv}_{mat}", by_mat[mat], place_of, deform_r, rects, spec, colour)
            objs[(lv, mat)] = o
            counts.setdefault(lv, {})[mat] = tris_of(o)
    total = {lv: sum(c.values()) for lv, c in counts.items()}
    over = [lv for lv in total if total[lv] > spec["levels"][lv]["budgetTris"]]
    print(f"[corner] triangles: {json.dumps(counts)} totals {total}; page filled {fill:.2f}")
    if over:
        raise SystemExit(f"[corner] over budget: {', '.join(f'{lv} {total[lv]} > {spec['levels'][lv]['budgetTris']}' for lv in over)}")

    for lv in ("near", "street"):
        for o in bpy.context.scene.objects:
            o.select_set(o.name.startswith(lv + "_"))
        bpy.ops.export_scene.fbx(filepath=os.path.join(out, f"corner-{lv}.fbx"), use_selection=True,
                                 object_types={"MESH"}, mesh_smooth_type="OFF", use_mesh_modifiers=False,
                                 colors_type="LINEAR", axis_forward="-Z", axis_up="Y", apply_unit_scale=True,
                                 apply_scale_options="FBX_SCALE_ALL", bake_space_transform=True, add_leaf_bones=False)
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(out, "corner.blend"))
    pieces = [{"i": pc.index, "id": pc.id, "mat": pc.mat, "kind": pc.kind, "mode": pc.mode} for pc in corner.pieces]
    feats = {k: v for k, v in corner.features.items()}
    meta = {
        "house": F.id, "world": F.world, "year": F.year, "age": F.age, "neglectSince": F.boarded, "neglect": F.neglect, "wealth": F.wealth,
        "triangles": counts, "totals": total, "budgets": {lv: spec["levels"][lv]["budgetTris"] for lv in total},
        "page": spec["page"], "charts": {k: list(v) for k, v in rects.items()},
        "heights": {"plinth": corner.z_plinth, "floor": corner.z_floor, "drip": [corner.z_drip0, corner.z_drip1],
                    "open": [corner.z_open0, corner.z_open1], "head": corner.z_head1, "top": corner.z_top},
        "courses": corner.courses, "window": [corner.x_open0, corner.x_open1], "sample": [corner.lx, corner.ly],
        "bends": {"settle": corner.frame.settle, "sag": corner.frame.sag, "lean": corner.frame.lean},
        "features": feats, "pieces": pieces,
        "uv": {"uv0": "tileable (metres / tileable.metres) or trim-sheet strip", "page": "UV1: the page"},
        "colour": {"r": "arris (a chamfer face)", "g": "piece seed", "b": "under layer forced (mortar)"},
    }
    with open(os.path.join(out, "corner.json"), "w") as fh:
        json.dump(meta, fh, indent=1, default=lambda v: list(v) if hasattr(v, "__iter__") else str(v))
    print(f"[corner] wrote {out}")


main()
