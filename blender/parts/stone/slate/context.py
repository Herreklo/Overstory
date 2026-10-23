"""R2a's contexts: what R1's laying (the walls and their copings) and the stair's plan (the steps) put around each
judged specimen, built in the specimen's own frame, so Unity judges the stone as it sits and not beside the open bands
its hidden faces leave (port step 2b, rung R2a; the brief of 23 October; the note: reviews/lt1/port/2b/r2a/stones/
blender.md, the contexts).

A context holds, within about 0.6 m of the specimen's drawn faces:
- the neighbours a part makes, made by that part (stones.py: the step, the wall stone, the coping) from their own facts,
  seeds and patches at L0 and L1, and put through every check of their part;
- the joints' fills (SN5), single-level, face kind 6 (joint soil), slice 7, mask 0: a wall's one surface per panel and
  face, a plane behind the faces at the joint depth leaning at the batter, over the context's cells; a tread joint's,
  filled to the bed below, its top and front the joint's width inside its lips;
- every neighbour no part makes yet (the cheek wall a step's end tails into; a face stone with a side open to the air
  or on the ground; a head, a topstone) as a plain proxy block of its cell, single-level, flagged as a proxy.

Which neighbours, by specimen (the brief): the wall stone, the cells touching it on its face; the coping, the pieces at
either end (the copings of the runs either side and what lies against its ends) and the course under it, on both
faces; the step, the steps directly below and above in its flight (both stones of each), its partner across, and the
cheek wall its walled end tails into (the cells touching the end cells of the context's steps in that wall).

Where each piece sits comes from R1's laying (a cell in s along the wall line and z) and the part's own set-in; across
the wall, from the face planes. The face planes' datum is not in data yet (kinds/wall.json's geometry stage is
planned): a context puts each face through the specimen, one plane per face at the batter, constant along s (a wall
stone's face plane through its bed's front edge; a coping's stair face proud of its front and its bank face the wall's
top thickness behind; a step's cheek wall faceGap off the stair's edge where it meets the specimen's tread). That is
an unknown for R2b, and the sidecar names what it moves.

    PY=/Applications/Blender.app/Contents/Resources/5.2/python/bin/python3.13
    $PY blender/parts/stone/slate/context.py plan [parts]          the pieces each context holds, and why
    blender -b --factory-startup --python blender/parts/stone/slate/context.py -- leak [parts]     the ray test only
    blender -b --factory-startup --python blender/parts/stone/slate/context.py -- export [parts]   built, tested, installed

Lengths in metres inside, integer millimetres in R1's cells and the sidecar.
"""

import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import stones as S  # noqa: E402  (the parts, their checks and the FBX route)
import hashing as HS  # noqa: E402

ROOT = S.ROOT
TOOL = "context 1"
REACH_MM = 600                      # the brief: everything within about 0.6 m of the specimen's drawn faces
CODE = 7                            # the fills' and proxies' UV7.y: slice 7 (no patch), mask 0, chamfer 0
FILL_KIND, PROXY_KIND = 6, 2        # joint filling (Stone.shader's kind 6); a proxy's faces split stone, unpatched
LEAK_VIEWS = (("face-on 20", 1.0), ("face-on 20", 5.0), ("face-on 20", 12.0), ("eye 1.6 m", 5.0),
              ("eye 1.6 m", 12.0))  # the brief's judging views
FILL_GRID_MM = 10                   # a wall fill's grid lines nearer than this merge (no sliver triangles)
ERODE_MM = 2.0                      # the solid a ray may not reach: the stone's planes this far inside (the drawn
                                    # surface lies on them; within this a ray only grazes an edge)
WEAR_MARGIN_MM = 2.0                # the worn top: the level's own error and this inside the field (L1's grid lies
                                    # within its error of the field, either side)


def _m(v):
    return float(v) / 1000.0


def _box(s):
    return S._box(s)


def _touch(a, b):
    """Two closed cells meet: a side or a corner in common, or overlap."""
    return a[0] <= b[1] and b[0] <= a[1] and a[2] <= b[3] and b[2] <= a[3]


def _gap(a, b):
    """The distance (mm) between two cells in (s, z): 0 where they meet."""
    ds = max(0, a[0] - b[1], b[0] - a[1])
    dz = max(0, a[2] - b[3], b[2] - a[3])
    return math.hypot(ds, dz)


def _covers(intervals, lo, hi):
    """Do the intervals cover [lo, hi] (mm, integers)?"""
    at = lo
    for a, b in sorted(intervals):
        if a > at:
            return False
        at = max(at, b)
        if at >= hi:
            return True
    return at >= hi


def piece_data(data):
    """A Data of its own for one piece (its notes its own), sharing the pinned commit's laying."""
    d = S.Data(data.commit)
    d._laying = data.laying()
    d._r1 = data.r1_facts()
    return d


# -- the walls: cells, sides, the face planes ---------------------------------------------------------------------------

def wall_of(data, stone_id):
    for w in data.laying()["walls"]:
        if any(s["id"] == stone_id for s in w["stones"]) or any(c["id"] == stone_id for c in w["cells"]):
            return w
    raise S.Failed(f"no wall holds {stone_id}")


def face_cells(w, face):
    """Every cell on a face of a wall: its stones with that face (a coping, a through or a head on both), and on the
    stair face the steps' end cells. [(id, kind, box, stone or None)]"""
    out = [(s["id"], s["kind"], _box(s), s) for s in w["stones"] if face in s["faces"]]
    if face == "stair":
        out += [(c["id"], "step", _box(c), None) for c in w["cells"]]
    return out


def side_state(w, stone, face):
    """What each side of a face stone's cell lies against on its face: a joint where other cells cover the whole side,
    the ground where the bed lies on the footing, else open (to the air). {lo, hi, b, t}."""
    x0, x1, z0, z1 = _box(stone)
    cells = [c for c in face_cells(w, face) if c[0] != stone["id"]]
    lo = [(max(b[2], z0), min(b[3], z1)) for _i, _k, b, _s in cells if b[1] == x0 and min(b[3], z1) > max(b[2], z0)]
    hi = [(max(b[2], z0), min(b[3], z1)) for _i, _k, b, _s in cells if b[0] == x1 and min(b[3], z1) > max(b[2], z0)]
    bot = [(max(b[0], x0), min(b[1], x1)) for _i, _k, b, _s in cells if b[3] == z0 and min(b[1], x1) > max(b[0], x0)]
    top = [(max(b[0], x0), min(b[1], x1)) for _i, _k, b, _s in cells if b[2] == z1 and min(b[1], x1) > max(b[0], x0)]
    out = dict(lo="joint" if _covers(lo, z0, z1) else "open", hi="joint" if _covers(hi, z0, z1) else "open",
               b="joint" if _covers(bot, x0, x1) else "open", t="joint" if _covers(top, x0, x1) else "open")
    if out["b"] == "open":
        foot = [(max(a, x0), min(b, x1)) for a, b, z in w["footing"].get(face, []) if z == z0 and min(b, x1) > max(a, x0)]
        if _covers(foot + bot, x0, x1):
            out["b"] = "ground"
    return out


class Faces:
    """A context's two face planes in its wall's unrolled frame (s along the wall line, w across it from the stair face
    into the wall, z up; metres): the stair face w = b (z - zRef), the bank face w = tRef - b (z - zRef), each constant
    along s (the datum through the specimen: the module's docstring)."""

    def __init__(self, b, z_ref, t_ref, working):
        self.b, self.z_ref, self.t_ref, self.working = b, z_ref, t_ref, working

    def w(self, face, z):
        return self.b * (z - self.z_ref) if face == "stair" else self.t_ref - self.b * (z - self.z_ref)

    @staticmethod
    def into(face):
        """+1 where w runs into the wall behind a face (the stair's), -1 behind the bank's."""
        return 1.0 if face == "stair" else -1.0


def _turn(a, into):
    """The linear part of a stone's frame in the wall's: x along s by alongS, y across by into, z up."""
    return np.diag([float(a), float(into), 1.0])


def wall_map(part, facts, o, faces):
    """A wall piece's frame in its wall's (s, w, z): (M, c) with W = M p + c, from its cell, its set-in and its part."""
    half = o["setInMm"]
    a = facts["alongS"]
    s0, s1 = facts["cellS"]
    s_o = _m(s0 + half["l"]) if a > 0 else _m(s1 - half["l"])
    z_b = _m(facts["cellZ"][0] + half["b"])
    if part == "wallstone":
        face = facts["face"]
        return _turn(a, Faces.into(face)), np.array([s_o, faces.w(face, z_b), z_b])
    proud = _m(o["proudMm"][0])
    return _turn(a, 1.0), np.array([s_o, faces.w("stair", z_b) - proud, z_b])


# -- the pieces --------------------------------------------------------------------------------------------------------

def _built(part, facts, data, why, kind=None):
    d = piece_data(data)
    defn = S.definition(part)
    out = S.build(part, facts, defn, d)
    res = S.check(part, out, defn)
    return dict(id=facts["id"], kind=kind or part, part=part, proxy=False, why=why, facts=facts, out=out,
                fails=res["fails"], triangles=[len(out["L0"]["T"]), len(out["L1"]["T"])])


def wall_piece(data, w, stone, face, why):
    """A neighbour in a wall: made by its part where one makes it, else a proxy of its cell (the reason named)."""
    kind = stone["kind"]
    if kind == "coping":
        return _built("coping", S.coping_facts(data, w, stone), data, why)
    if kind in ("face", "through"):
        sides = side_state(w, stone, face)
        if all(v == "joint" for v in sides.values()):
            facts = S.wallstone_facts(data, w, stone, face, S.wall_sides(w, stone, face))
            p = _built("wallstone", facts, data, why, kind="through" if kind == "through" else None)
            if kind == "through":
                p["note"] = "a through stone, drawn as a face stone on this face (the wall stone part's)"
            return p
        bad = {k: v for k, v in sides.items() if v != "joint"}
        return dict(id=stone["id"], kind="proxy", of=kind, proxy=True, cell=_box(stone), face=face, why=why,
                    reason=f"a {kind} stone whose cell has a side {', '.join(f'{k} {v}' for k, v in sorted(bad.items()))}"
                           f": the wall stone part makes a joint on every side (R2b's)")
    return dict(id=stone["id"], kind="proxy", of=kind, proxy=True, cell=_box(stone), face=face, why=why,
                reason=f"a {kind}: no part makes it yet (R2b's)")


def wallstone_pieces(data, facts):
    w = wall_of(data, facts["id"])
    sp = next(s for s in w["stones"] if s["id"] == facts["id"])
    face = facts["face"]
    box = _box(sp)
    out = []
    for cid, kind, b, s in sorted(face_cells(w, face), key=lambda c: c[0]):
        if cid == sp["id"] or not _touch(box, b):
            continue
        if s is None:
            out.append(dict(id=cid, kind="proxy", of="step", proxy=True, cell=b, face=face, why="touches it",
                            reason="a step's end cell (R2b's)"))
            continue
        out.append(wall_piece(data, w, s, face, "touches it"))
    return w, out


def coping_pieces(data, facts):
    w = wall_of(data, facts["id"])
    sp = next(s for s in w["stones"] if s["id"] == facts["id"])
    box = _box(sp)
    chosen = {}
    for s in w["stones"]:
        if s is sp:
            continue
        b = _box(s)
        if s["kind"] == "coping" and (b[1] == box[0] or b[0] == box[1]):
            chosen[s["id"]] = (s, "a coping either side (the run below or above, at an end)")
        elif b[3] == box[2] and min(b[1], box[1]) > max(b[0], box[0]):
            chosen[s["id"]] = (s, "the course under it")
        elif _touch(box, b):
            chosen.setdefault(s["id"], (s, "lies against an end"))
    out = []
    for sid in sorted(chosen):
        s, why = chosen[sid]
        if s["kind"] == "coping":
            out.append(wall_piece(data, w, s, "stair", why))
        else:
            out.append(wall_piece(data, w, s, s["faces"][0], why))
    return w, out


def step_pieces(data, rule):
    """The step's: the steps below and above in its flight, its partner across, and the cheek wall its walled end
    tails into (proxies)."""
    plan = data.plan
    fid, sid = rule["flight"], rule["step"]
    idx = plan["steps"][sid]["index"]
    by_index = {s["index"]: k for k, s in plan["steps"].items() if s["flight"] == fid}
    ordinary = {k for _i, k in S.ordinary_steps(data, fid)}
    fl = next(f for f in data.laying()["steps"] if f["id"] == fid)
    out = []
    for k, why in ((by_index.get(idx - 1), "the step below"), (sid, "its partner across"),
                   (by_index.get(idx + 1), "the step above")):
        if k is None:
            raise S.Failed(f"{sid}: no {why} in {fid}")
        if k not in ordinary:
            raise S.Failed(f"{k} ({why}) is not an ordinary step: the step part does not make it")
        for st in sorted((s for s in fl["stones"] if s["step"] == k), key=lambda s: s["id"]):
            if st["id"] == rule["stone"]:
                continue
            facts, _laid = S.step_facts(data, fid, k, st)
            p = _built("step", facts, data, why)
            p["step"] = k
            out.append(p)
    return fl, out


# -- geometry in the specimen's frame ----------------------------------------------------------------------------------

def place(m, R, c):
    """A level's mesh moved into the specimen's frame by a turn R (about z) and a shift c (m): positions and the
    triangles' planes; the channels are the stone's own and stay."""
    out = dict(m)
    out["V"] = np.asarray(m["V"], float) @ R.T + c
    out["plane"] = [dict(p, n=R @ np.asarray(p["n"], float)) for p in m["plane"]]
    return out


def _rigid(R):
    if abs(np.linalg.det(R) - 1.0) > 1e-9 or np.abs(R @ R.T - np.eye(3)).max() > 1e-9:
        raise S.Failed(f"a piece's placing is no turn: {R.tolist()}")
    return R


def plain_mesh(name, V, tris, kind, seed_id, world, out_dir):
    """A single-level mesh (a fill or a proxy) with the contract's eight channels: UV0 metres in its own plane, UV1
    (0, seed), UV2 (kind, 0), UV3 (0.5 + 0.5 n_z, 1), UV4 and UV5 0, UV6 and UV7.x each corner's height over the
    opposite edge (L0's encoding), UV7.y the code (slice 7, mask 0, chamfer 0). Triangles wound so their normals point
    out_dir's way (a function of the triangle's centre)."""
    V = np.asarray(V, float)
    T = []
    planes = []
    for tri in tris:
        a, b, c = (V[i] for i in tri)
        n = np.cross(b - a, c - a)
        if np.linalg.norm(n) < 1e-12:
            raise S.Failed(f"{name}: a degenerate triangle")
        n = n / np.linalg.norm(n)
        if n @ out_dir((a + b + c) / 3.0) < 0:
            tri = (tri[0], tri[2], tri[1])
            n = -n
        T.append(tri)
        planes.append(dict(n=n, d=float(n @ a)))
    T = np.asarray(T, int)
    nt = len(T)
    UV = np.zeros((8, nt, 3, 2))
    seed = HS.unit(HS.h(world, seed_id, "seed"))
    z = np.array([0.0, 0.0, 1.0])
    for t in range(nt):
        n = planes[t]["n"]
        u = np.cross(z, n)
        u = u / np.linalg.norm(u) if np.linalg.norm(u) > 1e-9 else np.array([1.0, 0.0, 0.0])
        v = np.cross(n, u)
        P3 = V[T[t]]
        alt = S.altitudes(P3)
        for i in range(3):
            UV[0, t, i] = (P3[i] @ u, P3[i] @ v)
            UV[1, t, i] = (0.0, seed)
            UV[2, t, i] = (float(kind), 0.0)
            UV[3, t, i] = (0.5 + 0.5 * n[2], 1.0)
        for i in range(3):
            if i < 2:
                UV[6, t, i, i] = alt[i]
            else:
                UV[7, t, i, 0] = alt[i]
        UV[7, t, :, 1] = CODE
    return dict(V=V, T=T, UV=UV, plane=planes, face=[name] * nt, level=None, name=name)


def grid_quads(ss, zs, inside, point):
    """A conforming grid over a union of rectangles: every grid cell (ss x zs) whose middle is inside, two triangles
    each on the grid's own vertices, so no vertex lies on another triangle's edge (no T-junction)."""
    idx = {}
    V = []

    def vid(i, j):
        if (i, j) not in idx:
            idx[(i, j)] = len(V)
            V.append(point(ss[i], zs[j]))
        return idx[(i, j)]

    tris = []
    for i in range(len(ss) - 1):
        for j in range(len(zs) - 1):
            if inside(0.5 * (ss[i] + ss[i + 1]), 0.5 * (zs[j] + zs[j + 1])):
                a, b, c, d = vid(i, j), vid(i + 1, j), vid(i + 1, j + 1), vid(i, j + 1)
                tris += [(a, b, c), (a, c, d)]
    return np.array(V), tris


def _breaks(values, least):
    """Grid lines through every cell edge, those nearer than least (mm) to the one before merged into it (the last
    kept), so no grid cell is a sliver (a 1 mm column's triangles carry float32 normals past the FBX route's check)."""
    v = sorted(set(values))
    out = [v[0]]
    for x in v[1:]:
        if x - out[-1] >= least:
            out.append(x)
        elif x == v[-1]:
            out[-1] = x
    return out


def wall_fill(name, rects, face, faces, depth, to_spec, world, seed_id):
    """SN5's fill for one panel's face: one plane depth behind the face (measured level), leaning at the batter, over
    the union of rects (s0, s1, z0, z1 in mm), as a conforming grid on the cells' edges (merged within FILL_GRID_MM:
    a grid cell is filled where any rect overlaps it, so the fill grows past the union by less than that at its
    outline and never falls short of it)."""
    ss = _breaks([r[0] for r in rects] + [r[1] for r in rects], FILL_GRID_MM)
    zs = _breaks([r[2] for r in rects] + [r[3] for r in rects], FILL_GRID_MM)

    def inside(s, z):           # the middle of a grid cell: filled where any rect overlaps the cell
        i = max(k for k in range(len(ss) - 1) if ss[k] <= s)
        j = max(k for k in range(len(zs) - 1) if zs[k] <= z)
        a0, a1, b0, b1 = ss[i], ss[i + 1], zs[j], zs[j + 1]
        return any(min(r[1], a1) > max(r[0], a0) and min(r[3], b1) > max(r[2], b0) for r in rects)

    into = Faces.into(face)

    def point(s, z):
        zm = _m(z)
        return to_spec(np.array([_m(s), faces.w(face, zm) + into * depth, zm]))

    V, tris = grid_quads(ss, zs, inside, point)
    out_w = to_spec(np.array([0.0, -into, 0.0]), vector=True)
    return plain_mesh(name, V, tris, FILL_KIND, seed_id, world, lambda c: out_w)


def box_mesh(name, corners, centre, world, seed_id):
    """A proxy block from its eight corners (index bit 0: s or x high, bit 1: z high, bit 2: back), six quads, wound
    outwards from its centre."""
    quads = [(0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)]
    tris = []
    for a, b, c, d in quads:
        tris += [(a, b, c), (a, c, d)]
    return plain_mesh(name, corners, tris, PROXY_KIND, seed_id, world, lambda c: c - centre)


def wall_proxy(name, cell, face, faces, depth, to_spec, world, seed_id):
    """A plain block of a wall cell: its front on the face plane, its back depth behind the face at its bed (level),
    its top, bed and ends the cell's."""
    s0, s1, z0, z1 = (_m(v) for v in cell)
    into = Faces.into(face)
    back = faces.w(face, z0) + into * depth
    C = []
    for k in range(8):
        s = s1 if k & 1 else s0
        z = z1 if k & 2 else z0
        w = back if k & 4 else faces.w(face, z)
        C.append(to_spec(np.array([s, w, z])))
    C = np.array(C)
    return box_mesh(name, C, C.mean(axis=0), world, seed_id)


def riser_y(planes, z):
    """The riser's surface at height z (m) in the step's frame: the most set-back of its facets (the block is the
    intersection of n . p <= d, each riser plane facing -y)."""
    return max((p["d"] - p["n"][2] * z) / p["n"][1] for p in planes)


def tread_fill(name, A, B, d_fill, reach, world, seed_id, shift):
    """A tread joint's fill (SN5: filled to the bed below), between stones A (left) and B (right), in the step's frame
    shifted by shift (m) into the specimen's: its top d_fill below the tread, its front d_fill behind the more set-back
    of the two risers at each height (each a stone's facets), down past the bed into the step below; reaching into
    each stone past the joint by reach (inside the stone, past its chamfers), back to the stone's depth."""
    oa, ob = A["out"]["outline"], B["out"]["outline"]
    xa = _m(A["facts"]["wear"]["leftMm"]) + oa["L"]          # A's right end, in the flight's x
    xb = _m(B["facts"]["wear"]["leftMm"])                    # B's left end
    H, D = oa["H"], min(oa["D"], ob["D"])
    if abs(H - ob["H"]) > 1e-9:
        raise S.Failed(f"{name}: the two stones of a step are not one rise")
    ra = [p for p in oa["block"] if p.get("face", p["name"]) == "riser" or p["name"] == "riser"]
    rb = [p for p in ob["block"] if p.get("face", p["name"]) == "riser" or p["name"] == "riser"]
    zt = H - d_fill
    lines = [((p["d"]) / p["n"][1], -p["n"][2] / p["n"][1]) for p in ra + rb]       # y = a + k z
    cand = {-0.01, zt}
    for i in range(len(lines)):
        for j in range(i + 1, len(lines)):
            (a1, k1), (a2, k2) = lines[i], lines[j]
            if abs(k1 - k2) > 1e-12:
                z = (a2 - a1) / (k1 - k2)
                if -0.01 < z < zt:
                    cand.add(z)
    zs = sorted(cand)
    env = lambda z: max(riser_y(ra, z), riser_y(rb, z)) + d_fill  # noqa: E731
    keep = [zs[0]] + [z for i, z in enumerate(zs[1:-1], 1)
                      if abs((env(zs[i + 1]) - env(z)) / (zs[i + 1] - z) - (env(z) - env(zs[i - 1])) / (z - zs[i - 1]))
                      > 1e-9] + [zs[-1]]
    x0, x1 = xa - reach, xb + reach
    V = []
    for z in keep:
        y = env(z)
        V += [(x0, y, z), (x1, y, z)]
    n = len(keep)
    V += [(x0, D, zt), (x1, D, zt)]
    tris = []
    for i in range(n - 1):
        a, b, c, d = 2 * i, 2 * i + 1, 2 * i + 3, 2 * i + 2
        tris += [(a, b, c), (a, c, d)]
    top0, top1 = 2 * (n - 1), 2 * (n - 1) + 1
    tris += [(top0, top1, 2 * n + 1), (top0, 2 * n + 1, 2 * n)]
    V = np.array(V) + shift

    def out_dir(c):
        return np.array([0.0, 0.0, 1.0]) if c[2] > shift[2] + zt - 1e-6 else np.array([0.0, -1.0, 0.0])

    m = plain_mesh(name, V, tris, FILL_KIND, seed_id, world, out_dir)
    m["joint"] = dict(depthMm=round(d_fill * 1000, 3), topMm=round(zt * 1000, 3), frontBreaksMm=[round(z * 1000, 3) for z in keep],
                      reachMm=round(reach * 1000, 3), xMm=[round(x0 * 1000, 3), round(x1 * 1000, 3)])
    return m


# -- a context ---------------------------------------------------------------------------------------------------------

class Context:
    """One specimen's context: the specimen (facts, rule, its two levels), the pieces, and each piece's meshes in the
    specimen's frame (built: L0 and L1; fills and proxies: one)."""

    def __init__(self, part, data):
        self.part, self.data = part, data
        self.world = data.world_seed()
        self.defn = S.definition(part)
        self.facts, self.rule = S.SPECIMENS[part](data)
        self.spec = S.build(part, self.facts, self.defn, piece_data(data))
        self.o = self.spec["outline"]
        self.pieces = []
        self.notes = []
        getattr(self, f"_{part}")()
        fails = [f"{p['id']}: {f}" for p in self.pieces if not p["proxy"] for f in p.get("fails", [])]
        if fails:
            raise S.Failed(f"{part} context: a built piece fails its part's checks: " + "; ".join(fails[:8]))

    # the walls
    def _wall_faces(self, w, working, z_ref, t_ref):
        bk, bu = self.data.batter(working)
        return Faces(bk / bu, z_ref, t_ref, working)

    def _wall_to_spec(self, M, c):
        Mi = np.linalg.inv(M)

        def to_spec(W, vector=False):
            return Mi @ W if vector else Mi @ (W - c)
        return to_spec

    def _place_wall(self, faces, to_spec_M, to_spec_c, w):
        """The built pieces into the specimen's frame; proxies and fills built there."""
        Mi = np.linalg.inv(to_spec_M)
        for p in self.pieces:
            if p["proxy"]:
                continue
            o = p["out"]["outline"]
            bk, bu = self.data.batter(p["facts"]["working"])
            if bk / bu != faces.b:
                raise S.Failed(f"{p['id']}: its working's batter is not the context's (one plane per face)")
            M, c = wall_map(p["part"], p["facts"], o, faces)
            R = _rigid(Mi @ M)
            shift = Mi @ (c - to_spec_c)
            p["R"], p["c"] = R, shift
            p["meshes"] = {k: place(p["out"][k], R, shift) for k in ("L0", "L1")}

    def _proxies_and_fill(self, w, faces, to_spec):
        """Proxies of their cells, and one fill per panel and face over the context's cells on it."""
        n = 0
        cells_by = {}
        working = faces.working
        depth_proxy = _m(self.data.top_thick(working)) / 2.0         # a face stone's own depth (stones.py: back)
        jlo, jhi = self.data.wall_joint(working)
        for p in self.pieces:
            if p["proxy"]:
                p["name"] = f"proxy_{n}"
                n += 1
                p["mesh"] = wall_proxy(p["name"], p["cell"], p["face"], faces, depth_proxy, to_spec, self.world,
                                       p["id"])
                p["depthMm"] = round(depth_proxy * 1000)
        spec_stone = next(s for s in w["stones"] if s["id"] == self.facts["id"])
        entries = [(spec_stone, self.facts.get("face") or "stair")] if self.part == "wallstone" else []
        for p in self.pieces:
            st = next((s for s in w["stones"] if s["id"] == p["id"]), None)
            if st is not None:
                entries.append((st, p.get("face") or (p["facts"].get("face") if not p["proxy"] else None)))
        if self.part == "coping":
            entries.append((spec_stone, None))
        for st, face in entries:
            for f in (st["faces"] if st["kind"] == "coping" or face is None else [face]):
                b = _box(st)
                if st["kind"] == "coping":       # its bed joint: the course's top to the widest joint into it
                    if st["id"] != self.facts["id"]:
                        continue                 # a coping a run away has no course of the context under it
                    b = (b[0], b[1], b[2], b[2] + jhi)
                cells_by.setdefault((st["panel"], f), []).append(b)
        fills = []
        for k, ((panel, f), rects) in enumerate(sorted(cells_by.items())):
            name = f"fill_{k}"
            m = wall_fill(name, sorted(set(rects)), f, faces, _m(jlo), to_spec, self.world, f"{panel}/{f}/fill")
            fills.append(dict(id=f"{panel}/{f}/fill", kind="fill", proxy=False, single=True, name=name, mesh=m,
                              why="SN5: one surface per panel and face, at the joint depth behind the face, leaning "
                                  "at the batter, over the context's cells on it",
                              depthMm=jlo, panel=panel, face=f, cells=len(set(rects))))
        self.pieces += fills

    def _wallstone(self):
        w, self.pieces = wallstone_pieces(self.data, self.facts)
        face = self.facts["face"]
        working = self.facts["working"]
        o = self.o
        z_b = _m(self.facts["cellZ"][0] + o["setInMm"]["b"])
        faces = self._wall_faces(w, working, z_b, _m(self.data.top_thick(working)))
        if face == "bank":
            faces.t_ref = 0.0          # the bank face through the specimen's bed's front edge at zRef
        M, c = wall_map("wallstone", self.facts, o, faces)
        self.faces = faces
        self._place_wall(faces, M, c, w)
        self._proxies_and_fill(w, faces, self._wall_to_spec(M, c))
        self.datum = (f"{face} face: through the specimen's bed's front edge, leaning {self.data.batter(working)} "
                      f"(back, up), constant along s")

    def _coping(self):
        w, self.pieces = coping_pieces(self.data, self.facts)
        working = self.facts["working"]
        o = self.o
        z_b = _m(self.facts["cellZ"][0] + o["setInMm"]["b"])
        t_ref = _m(self.data.top_thick(working))
        faces = self._wall_faces(w, working, z_b, t_ref)
        M, c = wall_map("coping", self.facts, o, faces)
        self.faces = faces
        self._place_wall(faces, M, c, w)
        self._proxies_and_fill(w, faces, self._wall_to_spec(M, c))
        self.datum = (f"the stair face {o['proudMm'][0]} mm behind the specimen's front at its bed, the bank face the "
                      f"wall's top thickness ({round(t_ref * 1000)} mm) behind it there, each leaning "
                      f"{self.data.batter(working)} (back, up), constant along s; the copings of the runs either side "
                      f"are placed by their stair side, so their backs miss the bank plane by twice the batter's lean "
                      f"over the runs' rise (seen only from the bank)")
        for p in self.pieces:
            if p.get("part") == "coping":
                dz = p["facts"]["cellZ"][0] + p["out"]["outline"]["setInMm"]["b"] - \
                     (self.facts["cellZ"][0] + o["setInMm"]["b"])
                p["note"] = (f"placed by its stair side; its back is {round(2 * faces.b * dz, 1)} mm off the bank "
                             f"plane (its bed {dz} mm from the specimen's)")

    # the step
    def _step(self):
        data = self.data
        fl, self.pieces = step_pieces(data, self.rule)
        st = self.rule["laid"]["step"]
        spec_stone = self.rule["laid"]["stone"]
        x0 = min(p[0] for p in spec_stone["outline"])
        origin = np.array([_m(x0), _m(st["y"][0]), _m(st["z"][0])])
        for p in self.pieces:
            f = p["facts"]
            stp = next(s for s in fl["steps"] if s["id"] == p["step"])
            c = np.array([_m(f["wear"]["leftMm"]), _m(stp["y"][0]), _m(stp["z"][0])]) - origin
            p["R"], p["c"] = np.eye(3), c
            p["meshes"] = {k: place(p["out"][k], np.eye(3), c) for k in ("L0", "L1")}
        self.origin = origin
        # the cheek wall its walled end tails into
        half = fl["half"]
        walled = [k for k in ("l", "r") if self.facts["ends"][k]["kind"] == "walled"]
        proxies = []
        for side_key in walled:
            w = wall_of(data, spec_stone["id"])
            cells = {c["id"]: _box(c) for c in w["cells"]}
            sign = 1.0 if side_key == "r" else -1.0
            if data.wall_side(w["id"]) != sign:
                raise S.Failed(f"{spec_stone['id']}: its {side_key} end's wall {w['id']} is not on its {side_key}")
            own = cells[spec_stone["id"]]
            off = own[0] - st["y"][0]               # the wall's s against the plan's y, from the specimen's own cell
            if own[1] - own[0] != st["y"][1] - st["y"][0] or own[2] != st["z"][0] or own[3] != st["z"][1]:
                raise S.Failed(f"{spec_stone['id']}: its end cell {own} is not its step {st['y']}, {st['z']}")
            ends = [own] + [cells[p["id"]] for p in self.pieces if p["id"] in cells]
            for cid, kind, b, s in sorted(face_cells(w, "stair"), key=lambda c: c[0]):
                if s is None or not any(_touch(b, e) for e in ends):
                    continue
                panel = next(pp for pp in w["panels"] if pp["id"] == s["panel"])
                working, _laid = data.panel_working(w["id"], panel)
                proxies.append(dict(id=cid, kind="proxy", of=kind, proxy=True, cell=b, face="stair", wall=w["id"],
                                    working=working, why="the cheek wall its walled end tails into",
                                    reason="the cheek wall a step's end tails into: no part makes it yet (R2b's)"))
            steps_p = data.wall["stages"]["plan"]["params"]["steps"]
            gap = data.note("faceGapMm", steps_p["faceGapMm"], "kinds/wall.json: stages.plan.params.steps.faceGapMm "
                                                               f"(at {data.commit[:7]})")
            edge = _m(round(data.plan["flights"][self.rule["flight"]]["width"] * 1000) / 2)
            if abs(edge * 1000 + gap + data.wall["stages"]["plan"]["params"]["steps"]["tailMm"] - half) > 0.5:
                raise S.Failed(f"the stair's edge {edge}, faceGap {gap} and tail do not make R1's step end {half}")
            workings = {p["working"] for p in proxies}
            if len(workings) != 1:
                raise S.Failed(f"the cheek wall's cells are of {sorted(workings)}: one face plane each is not built")
            working = workings.pop()
            faces = self._wall_faces(w, working, _m(st["z"][1]), _m(data.top_thick(working)))
            depth = _m(data.top_thick(working)) / 2.0

            def to_spec(W, vector=False, sign=sign, off=off, edge=edge, gap=gap):
                s, wv, z = W
                if vector:
                    return np.array([sign * wv, s, z])
                return np.array([sign * (edge + _m(gap) + wv), s - _m(off), z]) - origin

            for n, p in enumerate(proxies):
                p["name"] = f"proxy_{n}"
                p["mesh"] = wall_proxy(p["name"], p["cell"], "stair", faces, depth, to_spec, self.world, p["id"])
                p["depthMm"] = round(depth * 1000)
            self.faces = faces
            self.datum = (f"the cheek wall's stair face {gap} mm off the stair's edge where it meets the specimen's "
                          f"tread (z {st['z'][1]}), leaning {data.batter(working)} (back, up), constant along s; a "
                          f"proxy block of each cell, {round(depth * 1000)} mm deep (half the wall's top thickness, a "
                          f"face stone's own)")
        self.pieces += proxies
        # the tread joints' fills: the specimen's own and those of the steps below and above
        stones = {p["id"]: p for p in self.pieces if not p["proxy"]}
        stones[spec_stone["id"]] = dict(id=spec_stone["id"], facts=self.facts, out=self.spec)
        fills = []
        for k in sorted({p["step"] for p in self.pieces if p.get("step")} | {self.rule["step"]}):
            stp = next(s for s in fl["steps"] if s["id"] == k)
            two = sorted((s for s in fl["stones"] if s["step"] == k), key=lambda s: min(q[0] for q in s["outline"]))
            if len(two) != 2:
                continue
            A, Bp = stones[two[0]["id"]], stones[two[1]["id"]]
            jw = _m(stp["joint"][1] - stp["joint"][0])
            reach = max(_m(A["out"]["outline"]["chamferMm"]), _m(Bp["out"]["outline"]["chamferMm"])) + 0.005
            shift = np.array([0.0, _m(stp["y"][0]), _m(stp["z"][0])]) - origin
            name = f"fill_{len(fills)}"
            m = tread_fill(name, A, Bp, jw, reach, self.world, stp["jointId"], shift)
            fills.append(dict(id=stp["jointId"], kind="fill", proxy=False, single=True, name=name, mesh=m,
                              why="SN5: a tread joint filled to the bed below, its top and front the joint's width "
                                  "inside its lips", jointMm=stp["joint"][1] - stp["joint"][0], **m["joint"]))
        self.pieces += fills

    # the objects
    def objects(self):
        """{object name: mesh}, in order: each built piece's L0 and L1, then fills and proxies."""
        out = {}
        for p in self.pieces:
            if p.get("meshes"):
                for k in ("L0", "L1"):
                    out[f"{p['id']}_{k}"] = p["meshes"][k]
        for p in self.pieces:
            if p.get("mesh") is not None:
                out[p["name"]] = p["mesh"]
        return out

    def level(self, k):
        """The context drawn with the specimen at level k: the built pieces' level k, every fill and proxy."""
        out = {}
        for p in self.pieces:
            if p.get("meshes"):
                out[f"{p['id']}_{k}"] = p["meshes"][k]
            elif p.get("mesh") is not None:
                out[p["name"]] = p["mesh"]
        return out


# -- the leak test (inside Blender: mathutils' BVH, on the CPU) --------------------------------------------------------

def solid_planes(o, level):
    """The specimen's solid as half-spaces n . p <= d (its block and chips, with L0's chamfers at L0; never a cover),
    and its worn top (the step's) apart: (planes, top or None)."""
    planes = list(o["block"]) + list(o["chips"])
    if level == 0:
        planes += [p for p, _s, _a in o["chamfers"]]
    top = None
    if o.get("wear") is not None:
        top = next(p for p in planes if p["name"] == "top")
    return [(np.asarray(p["n"], float), float(p["d"])) for p in planes], top


def rays(view):
    f = S.B.unit(view["target"] - view["cam"])
    r = S.B.unit(np.cross(f, np.array([0.0, 0.0, 1.0])))
    u = np.cross(r, f)
    fp = S.focal_px()
    W, H = S.RIG["width"], S.RIG["height"]
    i = (np.arange(W) + 0.5 - W / 2) / fp
    j = (H / 2 - (np.arange(H) + 0.5)) / fp
    I, J = np.meshgrid(i, j)
    D = f[None, None, :] + I[..., None] * r[None, None, :] + J[..., None] * u[None, None, :]
    D /= np.linalg.norm(D, axis=-1, keepdims=True)
    return D.reshape(-1, 3)


def chords(O, D, planes, erode, top_erode=None, top=None):
    """Each ray's chord [te, tx] through the eroded convex solid."""
    te = np.zeros(len(D))
    tx = np.full(len(D), np.inf)
    for n, d in planes:
        dd = d - (top_erode if (top is not None and d == float(top["d"]) and np.allclose(n, top["n"])) else erode)
        den = D @ n
        num = dd - O @ n
        with np.errstate(divide="ignore", invalid="ignore"):
            t = num / den
        enter = den < 0
        exit_ = den > 0
        te = np.where(enter, np.maximum(te, t), te)
        tx = np.where(exit_, np.minimum(tx, t), tx)
        par = den == 0
        tx = np.where(par & (num < 0), -np.inf, tx)
    return te, tx


def leak_test(ctx, with_context=True, step_mm=0.25):
    """The brief's check: from each judging view, every pixel's ray through the 28 mm lens at 2560 x 1440; a leak is a
    ray that sees an open band of the specimen: whose first hit among everything drawn (the specimen at a level and
    its context at the same level) is a specimen face seen from behind, or that reaches the specimen's solid (its
    planes ERODE_MM inside; the step's worn top its level's error and WEAR_MARGIN_MM inside the wear field) before its
    first hit. Context rays seen into a context piece from behind are counted apart (not the specimen's)."""
    from mathutils import Vector
    from mathutils.bvhtree import BVHTree
    o = ctx.o
    out = {}
    for level in (0, 1):
        k = f"L{level}"
        spec = ctx.spec[k]
        meshes = [("specimen", spec)] + (list(ctx.level(k).items()) if with_context else [])
        verts, polys, owner, normals = [], [], [], []
        for name, m in meshes:
            base = len(verts)
            V = np.asarray(m["V"], float)
            verts += [Vector(v) for v in V]
            for t, tri in enumerate(np.asarray(m["T"])):
                polys.append([base + int(i) for i in tri])
                owner.append(name)
                normals.append(np.asarray(m["plane"][t]["n"], float))
        bvh = BVHTree.FromPolygons(verts, polys, all_triangles=True)
        normals = np.array(normals)
        is_spec = np.array([n == "specimen" for n in owner])
        planes, top = solid_planes(o, level)
        tol = o["tol0"] if level == 0 else o["tol1"]
        erode = ERODE_MM / 1000.0
        top_erode = tol + WEAR_MARGIN_MM / 1000.0
        wear = o.get("wear")
        H = o["H"]
        for vname, dist in LEAK_VIEWS:
            view = S.views(o, dist)[vname]
            O = np.asarray(view["cam"], float)
            D = rays(view)
            # rays through the specimen's convex hull at all (uneroded), for the back-face test, and its eroded chords
            te0, tx0 = chords(O, D, planes, 0.0)
            near = np.nonzero((te0 < tx0) & (tx0 > 0))[0]
            te, tx = chords(O, D[near], planes, erode, top_erode if wear is not None else None, top)
            onspec = back = leak = ctx_back = 0
            leaks = []
            Ov = Vector(O)
            for q, ri in enumerate(near):
                d = D[ri]
                loc, nrm, idx, t_h = bvh.ray_cast(Ov, Vector(d))
                if idx is None:
                    t_h = np.inf
                else:
                    if is_spec[idx]:
                        if normals[idx] @ d > 0:
                            back += 1
                            leaks.append(int(ri))
                            continue
                        onspec += 1
                    elif normals[idx] @ d > 0:
                        ctx_back += 1
                a, b = max(te[q], 0.0), min(tx[q], t_h)
                if a >= b:
                    continue
                if wear is None:
                    leak += 1
                    leaks.append(int(ri))
                    continue
                ts = np.arange(a, b, step_mm / 1000.0)
                P = O + ts[:, None] * d
                inside = P[:, 2] <= H - wear.depth(P[:, 0], P[:, 1]) - top_erode
                if inside.any():
                    leak += 1
                    leaks.append(int(ri))
            px = [[int(r % S.RIG["width"]), int(r // S.RIG["width"])] for r in leaks[:5]]
            out.setdefault(k, {})[f"{vname} at {dist:g} m"] = dict(
                rays=int(len(D)), throughHull=int(len(near)), onSpecimen=int(onspec), seenFromBehind=int(back),
                throughSolid=int(leak), leaks=int(back + leak), contextFromBehind=int(ctx_back), firstLeakPx=px,
                el=view["el"])
    return out


def leak_summary(res):
    lines = []
    for k, vs in res.items():
        for v, r in vs.items():
            lines.append(f"  {k} {v}: {r['leaks']} leaks ({r['seenFromBehind']} from behind, {r['throughSolid']} "
                         f"through) of {r['throughHull']} rays on its hull, {r['onSpecimen']} on it; context from "
                         f"behind {r['contextFromBehind']}" + (f"; first at {r['firstLeakPx']}" if r["leaks"] else ""))
    return "\n".join(lines)


# -- the FBX route's check, at a context's distances ------------------------------------------------------------------

_OWN = """        own_err = float(np.abs(N3[:, 0] - own).max())
        if own_err > 1e-5:
"""
_OWN_SCALED = """        longest_o = np.max([np.linalg.norm(P[:, (i + 1) % 3] - P[:, i], axis=1) for i in range(3)], axis=0)
        own_dev = np.abs(N3[:, 0] - own).max(axis=1)
        own_allow = 1e-5 + 4.0 * float(np.abs(P).max()) * 2.0 ** -24 / (twice / longest_o)
        own_err = float(own_dev.max())
        if (own_dev > own_allow).any():
"""


def readback(path, objs):
    """stones.py's readback (every check of the FBX route: three control points a triangle, positions exact, normals
    flat and on their planes, all eight UVs bit for bit) with one change: a normal's bound against its own triangle's
    is scaled as the bound against its face's plane already is, by what float32 positions allow a triangle of its
    altitude at its distance from the frame's origin (4 R 2^-24 / altitude, over the fixed 1e-5). A context's pieces
    lie up to 1.3 m from the specimen's pivot, where a chamfer's corner triangle of a step a step away carries a
    float32 normal 2.4e-5 off its float64 one (stones.py's specimens, at their own pivots, keep within 1e-5)."""
    import inspect
    src = inspect.getsource(S.readback)
    if src.count(_OWN) != 1:
        raise S.Failed("stones.py's readback has changed: the context's bound no longer applies to it")
    ns = dict(S.__dict__)
    exec(compile(src.replace(_OWN, _OWN_SCALED), "stones.readback (context bound)", "exec"), ns)
    return ns["readback"](path, objs)


# -- the plan, the sidecar, the export ---------------------------------------------------------------------------------

def describe(ctx):
    rows = []
    for p in ctx.pieces:
        row = dict(id=p["id"], kind=p["kind"], proxy=p["proxy"], why=p["why"])
        if p.get("meshes"):
            row.update(part=p["part"], objects=dict(L0=f"{p['id']}_L0", L1=f"{p['id']}_L1"),
                       triangles=dict(L0=len(p["out"]["L0"]["T"]), L1=len(p["out"]["L1"]["T"])),
                       turnDeg=round(math.degrees(math.atan2(p["R"][1, 0], p["R"][0, 0])), 6),
                       offsetMm=[round(v * 1000, 3) for v in p["c"]], checks="pass")
            if p.get("note"):
                row["note"] = p["note"]
            if p["part"] == "wallstone":
                row["setInMm"] = p["out"]["outline"]["setInMm"]
        else:
            row.update(object=p["name"], triangles=len(p["mesh"]["T"]))
            for key in ("reason", "of", "cell", "face", "depthMm", "jointMm", "panel", "cells", "topMm", "frontBreaksMm",
                        "reachMm", "xMm", "wall", "working"):
                if key in p:
                    row[key] = list(p[key]) if isinstance(p[key], tuple) else p[key]
        rows.append(row)
    return rows


def plan_summary(ctx):
    lines = [f"== {ctx.part} context of {ctx.facts['id']}", f"  datum: {ctx.datum}"]
    for r in describe(ctx):
        tri = r["triangles"]
        lines.append(f"  {r['kind']:9s} {r['id']:44s} {('proxy' if r['proxy'] else ''):5s} {tri} {r['why']}"
                     + (f" -- {r['reason']}" if r.get("reason") else "") + (f" -- {r['note']}" if r.get("note") else ""))
    objs = ctx.objects()
    lines.append(f"  objects {len(objs)}, triangles {sum(len(m['T']) for m in objs.values())}")
    return "\n".join(lines)


def code_ids(part):
    ids = S.code_ids(part)
    ids["blender/parts/stone/slate/context.py"] = S.blob("blender/parts/stone/slate/context.py")
    for other in ("step", "wallstone", "coping"):
        ids[f"{S.PACK}/parts/stone/{other}.json"] = S.blob(f"{S.PACK}/parts/stone/{other}.json")
    return ids


def sidecar(ctx, leak, baseline):
    return S._jsonable(dict(
        part=f"{ctx.part}_context", specimen=ctx.facts["id"], tool=TOOL,
        frame=f"the specimen's frame ({S.GENERATED}/{ctx.part}.json: frame), so the context placed at the specimen's "
              f"transform sits as R1 laid it; " + S.FRAMES[ctx.part],
        rule=("the brief of 23 October: everything within about 0.6 m of the specimen's drawn faces that R1's laying "
              "(walls, copings) or the stair's plan (steps) puts there; " + {
                  "wallstone": "the wall stone: the cells touching it on its face, and the fill",
                  "coping": "the coping: the pieces at either end (the copings of the runs either side, and what lies "
                            "against its ends) and the course under it on both faces, and the fill",
                  "step": "the step: the steps directly below and above in its flight (both stones of each), its "
                          "partner across, the cheek wall its walled end tails into (proxies), and the tread joints' "
                          "fills"}[ctx.part]),
        datum=ctx.datum,
        datumNote="the face planes' datum is not in data yet (kinds/wall.json's geometry stage is planned); the context "
                  "puts each face through the specimen, one plane per face at the batter, constant along s: R2b's "
                  "unknown",
        objects="each built piece <id>_L0 and <id>_L1 (its part's own levels, its own seed and patches); fill_<n> and "
                "proxy_<n> single-level, drawn with either level. Ids hold '/': find objects by name among the "
                "model's children, not by Transform.Find's path",
        fillCode=dict(kind=FILL_KIND, slice=7, mask=0, chamfer=0, uv7y=CODE),
        proxyCode=dict(kind=PROXY_KIND, slice=7, mask=0, chamfer=0, uv7y=CODE,
                       note="a plain block of its cell, flagged: no part makes it yet"),
        channels=dict(zip([f"UV{c}" for c in range(8)], S.UV_LAYERS)),
        pieces=describe(ctx),
        leak=dict(rule=leak_test.__doc__.split("\n\n")[0].replace("\n    ", " "), erodeMm=ERODE_MM,
                  wearMarginMm=WEAR_MARGIN_MM,
                  margins=("a worn top is tested its level's error and the margin inside the wear field (L0 3 mm, "
                           "L1 7.5 mm at the step's 5.5 mm share), so a level's test cannot see an open band of the "
                           "top shallower than that; the L0 test, at 3 mm, bites alone (the step's uncovered top past "
                           "the cover) and passes with the context, whose pieces are the same at either level"
                           if ctx.part == "step" else "no worn top: every plane eroded by erodeMm"), views=[f"{v} at {d:g} m" for v, d in LEAK_VIEWS],
                  rig=S.RIG, withContext=leak, alone=baseline,
                  ok=all(r["leaks"] == 0 for vs in leak.values() for r in vs.values())),
        data=ctx.data.src, code=code_ids(ctx.part),
    ))


def export(ctx, leak, baseline):
    import shutil
    import tempfile
    import bpy
    sys.path.insert(0, os.path.join(ROOT, "blender", "generators"))
    import stone as ST      # its _export_fbx and install_lock, imported, never edited
    import mesh_hash
    if not all(r["leaks"] == 0 for vs in leak.values() for r in vs.values()):
        raise S.Failed(f"{ctx.part} context: the specimen's open bands are seen: nothing is exported")
    for ob in list(bpy.data.objects):
        bpy.data.objects.remove(ob, do_unlink=True)
    objs = ctx.objects()
    for name in objs:
        if len(name.encode()) > 63:
            raise S.Failed(f"{name}: longer than Blender's 63 bytes")
    obs = [S.make_object(name, m) for name, m in objs.items()]
    if [ob.name for ob in obs] != list(objs):
        raise S.Failed(f"{ctx.part} context: Blender renamed objects: {[ob.name for ob in obs][:5]}")
    side = sidecar(ctx, leak, baseline)
    path = os.path.join(ROOT, S.GENERATED, f"{ctx.part}_context.fbx")
    scratch = tempfile.mkdtemp(prefix="context-export-")
    try:
        trial = os.path.join(scratch, os.path.basename(path))
        ST._export_fbx(trial, obs)
        back = readback(trial, objs)
        new = mesh_hash.entry(trial)
        again = os.path.join(scratch, "again.fbx")
        ST._export_fbx(again, obs)
        if mesh_hash.entry(again) != new:
            raise S.Failed(f"{ctx.part} context: two exports of the same meshes hash differently")
        first = next(iter(objs))
        probe_name = f"{first}_shared"[:63]
        pm = dict(objs[first])
        probe = S.shared_object(probe_name, pm)
        probe_path = os.path.join(scratch, "shared.fbx")
        try:
            ST._export_fbx(probe_path, [probe])
        finally:
            bpy.data.objects.remove(probe, do_unlink=True)
        try:
            readback(probe_path, {probe_name: pm})
        except S.Failed as e:
            refused = str(e)
        else:
            raise S.Failed(f"{ctx.part} context: the FBX route's check passed {first} on shared control points")
    finally:
        shutil.rmtree(scratch, ignore_errors=True)
    back = dict(objects=len(back), triangles=sum(v["triangles"] for v in back.values()),
                each="three control points a triangle, its own; positions exact; normals flat, each its triangle's "
                     "own; all eight UVs bit for bit", sharedProbe=refused, perObject=back)
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
                raise S.Failed(f"{ctx.part} context: the installed FBX does not hash as the one read back")
            print("FBX", os.path.relpath(path, ROOT))
        ST._write_if_changed(path[:-4] + ".json", text)
    mesh_hash.write_manifest(path, manifest=os.path.join(ROOT, S.MANIFEST))
    mp = os.path.join(ROOT, S.MANIFEST)
    with open(mp) as fh:
        man = json.load(fh)
    key = os.path.basename(path)
    man[key]["context"] = dict(specimen=ctx.facts["id"], pieces=len(ctx.pieces),
                               proxies=sum(1 for p in ctx.pieces if p["proxy"]),
                               fills=sum(1 for p in ctx.pieces if p["kind"] == "fill"),
                               built=sum(1 for p in ctx.pieces if p.get("meshes")),
                               objects=len(objs), fbxVertices=3 * sum(len(m["T"]) for m in objs.values()),
                               note="the specimen's context in its frame (context.py); fills and proxies single-level")
    with open(mp, "w") as fh:
        json.dump(dict(sorted(man.items())), fh, indent=1)
        fh.write("\n")
    return side


def main(argv):
    """context.py <plan | leak | export> [part,part,...]"""
    cmd = argv[0] if argv else "plan"
    parts = argv[1].split(",") if len(argv) > 1 else list(S.PARTS)
    if cmd not in ("plan", "leak", "export"):
        raise SystemExit(f"unknown command {cmd}: plan, leak or export")
    data = S.Data()
    ok = True
    for part in parts:
        ctx = Context(part, S.Data(data.commit))
        print(plan_summary(ctx))
        if cmd == "plan":
            continue
        if S.timing_running():
            print("a timing run holds the machine: the ray test waits")
            S._wait_for_quiet()
        res = leak_test(ctx)
        base = leak_test(ctx, with_context=False)
        print(f"  the leak test, with its context:\n{leak_summary(res)}\n  alone:\n{leak_summary(base)}")
        good = all(r["leaks"] == 0 for vs in res.values() for r in vs.values())
        ok = ok and good
        if cmd == "export":
            side = export(ctx, res, base)
            print("  readback:", side["readback"]["objects"], "objects,", side["readback"]["triangles"],
                  "triangles; probe refused:", side["readback"]["sharedProbe"][:90])
    return 0 if ok else 1


if __name__ == "__main__":
    args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
    sys.exit(main(args))
