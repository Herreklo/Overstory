"""An outcrop as its jointing breaks it (pure numpy): the land's bedrock surface drawn as rigid blocks.

The landform gives the bedrock's surface (the envelope: a whaleback the ice left, smooth on its stoss side, plucked in
steps on its lee). The rock's steep joint families (the foliation and the cross joints) cut the ground into convex
columns, at seeded spacings; each column's top is one plane, fitted to the envelope at the column's middle. On the
stoss side the tops follow the envelope (the ice cut across the joints, which show as seams); on the lee the ice
plucked whole plates away, so a column's top drops by whole sheeting plates and the steps fall on joints. A cut is
dated and made by men: it splits the columns it crosses by its walls and lowers them to its floor. Every face is a
joint, the ice's plane, a cut or the sea's bed; nothing is bent (BB3).

Site metres: x east, y north, z up over mean sea level. Seeds from stable ids (blender/resolver/hashing.py).
"""

import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(HERE)), "resolver"))
import hashing as HS  # noqa: E402
import hull as H  # noqa: E402

# face labels (the face kind the shader reads)
ICE, JOINT, FOLIATION, CUT, BED, PLATE = "ice", "joint", "foliation", "cut", "bed", "plate"


def compass(b):
    r = math.radians(b)
    return np.array([math.sin(r), math.cos(r)])


class Whaleback:
    """One rock back the ice wore: its crest, radii to the stoss, the lee and either side, its profile's power."""

    def __init__(self, rec, ice, lee):
        self.c = np.array(rec["centre"], float)
        self.top = rec["top"]
        self.ice = ice
        r = rec["radii"]
        self.r_stoss, self.r_lee = r[0], r[1]
        self.r_left, self.r_right = (r[2], r[3]) if len(r) > 3 else (r[2], r[2])
        self.power = rec["power"]
        self.lee = dict(lee, **rec.get("lee", {}))

    def frame(self, x, y):
        dx, dy = x - self.c[0], y - self.c[1]
        s = dx * self.ice[0] + dy * self.ice[1]          # + toward the lee
        t = -dx * self.ice[1] + dy * self.ice[0]         # + to the ice's left
        return s, t

    def smooth(self, x, y):
        s, t = self.frame(x, y)
        rs = np.where(s < 0, self.r_stoss, self.r_lee)
        rt = np.where(t > 0, self.r_left, self.r_right)
        r = np.sqrt((s / rs) ** 2 + (t / rt) ** 2)
        return self.top * (1 - np.power(np.maximum(r, 0), self.power))


class Landform:
    """The bedrock's envelope: the main back and the smaller backs on its flanks, all worn by the one ice."""

    def __init__(self, rec):
        self.ice = compass(rec["iceToward"])
        self.lee = rec["lee"]
        self.backs = [Whaleback(rec, self.ice, self.lee)] + [Whaleback(k, self.ice, self.lee) for k in rec.get("knobs", [])]
        self.c = self.backs[0].c
        self.top = max(b.top for b in self.backs)

    def smooth(self, x, y):
        return np.max([b.smooth(x, y) for b in self.backs], axis=0)

    def back_at(self, x, y):
        return self.backs[int(np.argmax([b.smooth(x, y) for b in self.backs]))]

    def plucked(self, x, y, jitter=0.0):
        """How deep the lee was plucked under a block's middle: whole plates, stepping down from its back's crest."""
        b = self.back_at(x, y)
        s, _ = b.frame(x, y)
        L = b.lee
        if s <= L["from"]:
            return 0.0
        k = max(0, int(np.floor((s - L["from"]) / L["run"] + 1 + jitter)))
        return k * L["plate"]

    def grad(self, x, y, h=0.25):
        return np.array([(self.smooth(x + h, y) - self.smooth(x - h, y)) / (2 * h),
                         (self.smooth(x, y + h) - self.smooth(x, y - h)) / (2 * h)])


class Back:
    """A block's own back, as the ice wore it: over the block's plan (its ranges along the ice, s, and across it, t),
    its crest `crestShift` of the half-length toward the down-ice end, falling below the envelope by `roll` at the
    plan's ellipse (a seeded share of its half-width, within rollM) with the profile's `power`; down-ice of the crest
    it falls only `leeShare` of that by the plan's edge, so the back keeps a firm lip over its plucked lee. The fall
    is convex, so the envelope less the fall stays concave and its tangent planes bound the block."""

    def __init__(self, rec, ice, s_range, t_range, rng):
        self.ice = ice
        hs, ht = (s_range[1] - s_range[0]) / 2, (t_range[1] - t_range[0]) / 2
        self.cs = (s_range[0] + s_range[1]) / 2 + rec["crestShift"] * hs
        self.ct = (t_range[0] + t_range[1]) / 2
        self.rs_up = hs * (1 + rec["crestShift"]) + 1e-3
        self.rs_down = (hs * (1 - rec["crestShift"]) + 1e-3) / rec["leeShare"] ** (1 / rec["power"])
        self.rt = ht + 1e-3
        lo, hi = rec["rollM"]
        self.roll = float(np.clip(rng.uniform(*rec["rollShare"]) * min(hs, ht), lo, hi))
        self.power = rec["power"]

    def fall(self, x, y):
        """How far the back lies under the envelope at (x, y)."""
        s = x * self.ice[0] + y * self.ice[1] - self.cs
        t = -x * self.ice[1] + y * self.ice[0] - self.ct
        rs = np.where(s < 0, self.rs_up, self.rs_down)
        return self.roll * np.power(np.sqrt((s / rs) ** 2 + (t / self.rt) ** 2), self.power)

    def fall_grad(self, x, y, h=0.2):
        return np.array([(self.fall(x + h, y) - self.fall(x - h, y)) / (2 * h),
                         (self.fall(x, y + h) - self.fall(x, y - h)) / (2 * h)])

    def grad_under(self, land):
        """The block's top's gradient at (x, y): the envelope's less the fall's."""
        return lambda x, y: land.grad(x, y) - self.fall_grad(x, y)


def family_planes(key, fam, lo_hi):
    """A steep family's planes: (normal, offsets, gaps) at seeded spacings over the range of n.p. A joint's opening
    is seeded from the family's `open` record ([share, min, max] of open joints; the rest are tight seams)."""
    n = H.normal(fam["dip"], fam["dipToward"])
    lo, hi = lo_hi(n)
    rng = HS.Stream(key, "joints", fam["name"])
    a, b = fam["spacingM"]
    share, g0, g1 = fam.get("open", [0.0, 0.0, 0.0])
    tight = fam.get("tightM", 0.0)
    t = lo - rng.uniform(0.0, b)
    offs, gaps = [], []
    while t < hi:
        t += rng.uniform(a, b)
        offs.append(t)
        gaps.append(rng.uniform(g0, g1) if rng.uniform(0, 1) < share else tight)
    return n, np.array(offs), np.array(gaps)


def split(cells, n, offsets, gaps, label):
    """Every cell cut by each of a family's planes it straddles; both sides kept, parted by the joint's opening."""
    out = []
    for cell in cells:
        V = np.concatenate([f.V for f in cell])
        s = V @ n
        lo, hi = s.min(), s.max()
        parts = [cell]
        for d, g in zip(offsets, gaps):
            if not (lo + 1e-4 < d < hi - 1e-4):
                continue
            nxt = []
            lab = label + "-open" if g > 0.05 else label
            for p in parts:
                a = H.clip(p, n, d - g / 2, lab)
                b = H.clip(p, -n, -(d + g / 2), lab)
                nxt += [q for q in (a, b) if q is not None and H.volume(q) > 1e-3]
            parts = nxt
        out += parts
    return out


def tangent_points(land, key, region, step):
    """Where the ice's envelope is touched: a jittered grid over the region, shared by every block, so neighbouring
    blocks carry the same worn surface and it runs on across their tight joints."""
    x0, y0, x1, y1 = region
    rng = HS.Stream(key, "facets")
    pts = []
    for y in np.arange(y0, y1 + step, step):
        for x in np.arange(x0, x1 + step, step):
            pts.append((x + rng.uniform(-0.35, 0.35) * step, y + rng.uniform(-0.35, 0.35) * step))
    P = np.array(pts)
    Z = land.smooth(P[:, 0], P[:, 1])
    G = np.array([land.grad(x, y) for x, y in P])
    return P, Z, G


def centroid(cell):
    return np.concatenate([f.V for f in cell]).mean(0)


def traces(key, fam, n, offs, lo_hi):
    """Where each of a family's joints runs: [from, to] along its strike, a seeded length between the family's traceM
    (log-uniform, so a few run long and many short) about a seeded middle; through everything when it has none.
    Past a trace's ends the rock is whole, so the families meet in T's and the blocks they bound differ in size."""
    s = np.array([-n[1], n[0], 0.0])
    s /= max(float(np.linalg.norm(s)), 1e-9)
    lo, hi = lo_hi(s)
    if "traceM" not in fam:
        return s, np.array([[lo - 1.0, hi + 1.0]] * len(offs))
    rng = HS.Stream(key, "traces", fam["name"])
    a, b = fam["traceM"]
    out = []
    for _ in offs:
        L = math.exp(rng.uniform(math.log(a), math.log(b)))
        m = rng.uniform(lo, hi)
        out.append([m - L / 2, m + L / 2])
    return s, np.array(out)


def opening(rec, land, c):
    """How far the frost and the sea opened an open joint at c: 1 low on the back, 0 where the ice planed the crest."""
    o = rec["opening"]
    b = land.back_at(c[0], c[1])
    h = float(land.smooth(c[0], c[1])) / max(b.top, 1e-6)
    u = np.clip((o["shutAbove"] - h) / (o["shutAbove"] - o["fullBelow"]), 0.0, 1.0)
    return float(u * u * (3 - 2 * u))


def build(rec, key, sea):
    """The outcrop's blocks: a list of (faces, info) with each block's id and what made its top; `sea` is the site's
    sea record (its exposure by side).

    Every family's planes cut the ground into cells; a joint shows only along its trace, or where the sea and the frost
    broke the rock up all the way (opening 1, low on the shore). Cells joined across a joint that does not show are one
    block: one top, one plucking, one sheet stripped, and no bevel or riser between them, so the ice-planed back runs
    on across its seams and a few big backs stand among middle and small blocks."""
    land = Landform(rec["landform"])
    x0, y0, x1, y1 = rec["region"]
    bed = rec["bed"]
    corners = np.array([[x, y, z] for x in (x0, x1) for y in (y0, y1) for z in (bed, land.top + 2)])

    def lo_hi(n):
        s = corners @ n
        return s.min(), s.max()

    cells = [H.box((x0, y0, bed), (x1, y1, land.top + 2), BED)]
    planes = []                                   # (kind, normal, offset, gap, trace, strike)
    for fam in rec["families"]:
        n, offs, gaps = family_planes(key, fam, lo_hi)
        s, tr = traces(key, fam, n, offs, lo_hi)
        kind = FOLIATION if fam["name"] == "foliation" else JOINT
        for d, g, t in zip(offs, gaps, tr):
            cells = cut(cells, n, d, f"#{len(planes)}")
            planes.append((kind, n, d, g, t, s))
    cells = sorted(cells, key=lambda c: tuple(np.round(centroid(c), 3)))

    # which joint faces show, and the blocks the hidden ones join
    shows = {}
    up = list(range(len(cells)))

    def find(i):
        while up[i] != i:
            up[i] = up[up[i]]
            i = up[i]
        return i

    seen = {}
    for i, cell in enumerate(cells):
        c = centroid(cell)
        broken = opening(rec, land, c) >= 0.999
        for f in cell:
            if not f.label.startswith("#"):
                continue
            j = int(f.label[1:])
            fc = f.V.mean(0)
            t0, t1 = planes[j][4]
            u = float(fc @ planes[j][5])
            # along its trace a joint shows where it is open, or off the crest; the crest's tight seams the ice planed;
            # on the lee the ice plucked along every joint
            plucked = land.plucked(c[0], c[1]) > 0
            on = broken or plucked or (t0 <= u <= t1 and (planes[j][3] > 0.05 or opening(rec, land, c) >= 0.5))
            k = (j, tuple(np.round(fc, 2)))
            if k in seen:
                i2, on2 = seen[k]
                on = on or on2
                shows[(i, j)] = shows[(i2, j)] = on
                if not on:
                    up[find(i)] = find(i2)
            else:
                seen[k] = (i, on)
                shows[(i, j)] = on
    groups = {}
    for i in range(len(cells)):
        groups.setdefault(find(i), []).append(i)

    lf = rec["landform"]
    step = lf["facetM"]
    P, Z, G = tangent_points(land, key, rec["region"], step)
    coast = rec["coast"]
    sh = rec["sheets"]
    ice = land.ice
    blocks = []
    for g, members in sorted(groups.items()):
        GV = np.concatenate([f.V for i in members for f in cells[i]])
        gc = GV.mean(0)
        grng = HS.Stream(key, "block", f"{gc[0]:.2f}", f"{gc[1]:.2f}")
        z0 = float(land.smooth(gc[0], gc[1]))
        # plucked on the lee by whole sheeting plates, never below the lee's floor: the tread is the envelope's own
        # shell lowered by the plates (sheeting runs parallel to the surface), the riser the block's joint face
        drop = land.plucked(gc[0], gc[1], grng.uniform(-0.45, 0.45))
        drop = min(drop, max(0.0, z0 - land.lee["floor"])) if drop > 0 else 0.0
        lee = drop > 0
        # sheets stripped from the stoss before the last ice: whole sheeting shells gone over a block, where the slow
        # field says so; their edges fall on the blocks' joints and show as long ledges across the worn back
        # (none on the crest, which the ice planed across its seams: the fixture's top stands)
        phi = opening(rec, land, gc)
        n_sheets = int(np.floor(sheet_field(key, gc[0], gc[1], sh["cellM"]) * sh["most"] * phi + 0.3))
        drop += n_sheets * sh["thickM"] if drop == 0 else 0.0
        label = ICE if drop == 0 else PLATE
        # each block was worn as a whaleback of its own: a back over its plan, its crest toward its down-ice end,
        # rolling down at its edges by a share of its width, where its joints show (rec["backs"])
        sv = GV[:, 0] * ice[0] + GV[:, 1] * ice[1]
        tv = -GV[:, 0] * ice[1] + GV[:, 1] * ice[0]
        back = Back(rec["backs"], ice, (sv.min(), sv.max()), (tv.min(), tv.max()), grng)
        if lee:                                   # a plucked tread is a sheeting plane, its risers crisp: barely rounded
            back.roll *= rec["backs"]["leeRoll"]
        k = 0.0
        ext = GV[:, :2].max(0) - GV[:, :2].min(0)
        for i in members:
            cell = cells[i]
            c = centroid(cell)
            if float(land.smooth(c[0], c[1])) < rec["dropBelow"]:
                continue
            rng = HS.Stream(key, "block", f"{c[0]:.2f}", f"{c[1]:.2f}")
            # the sea takes whole blocks at the waterline, more where it is more exposed: the shore runs along joints
            if float(land.smooth(c[0], c[1])) < coast["belowM"] and rng.uniform(0, 1) < coast["share"] * exposure(sea, land, c):
                continue
            # the joints that show part the block from its neighbours by their opening; those that don't are seams
            f = []
            for q in cell:
                if q.label.startswith("#"):
                    j = int(q.label[1:])
                    kind, _, _, gap, _, _ = planes[j]
                    if shows[(i, j)]:
                        tight = gap <= 0.05
                        w = gap if tight else max(gap * opening(rec, land, c), 0.0)
                        lab = kind + ("-open" if w > 0.05 else "")
                    else:
                        w, lab = 0.0, kind + "-seam"
                    f.append((q, w, lab))
                else:
                    f.append((q, 0.0, q.label))
            faces = [H.Face(q.V, q.n, q.d, lab) for q, _, lab in f]
            for q, w, lab in f:
                if w > 0:
                    faces = H.clip(faces, q.n, q.d - w / 2, lab)
                    if faces is None:
                        break
            if faces is None:
                continue
            V = np.concatenate([q.V for q in faces])
            lo, hi = V[:, :2].min(0) - step, V[:, :2].max(0) + step
            near = np.where((P[:, 0] > lo[0]) & (P[:, 0] < hi[0]) & (P[:, 1] > lo[1]) & (P[:, 1] < hi[1]))[0]
            near = near[np.argsort(np.hypot(P[near, 0] - c[0], P[near, 1] - c[1]))]       # the middle's plane first
            top = None
            for j in near:
                (x, y) = P[j]
                z = float(Z[j]) - drop - float(back.fall(x, y))
                gr = G[j] - back.fall_grad(x, y)
                # z <= z_q + g.(p - q)
                nrm = np.array([-gr[0], -gr[1], 1.0])
                d = z - gr[0] * x - gr[1] * y
                ln = np.linalg.norm(nrm)
                faces = H.clip(faces, nrm / ln, d / ln, label)
                top = top or (nrm / ln, d / ln)
                if faces is None:
                    break
            if faces is None or H.volume(faces) < 1e-3:
                continue
            faces = chamfer(faces, top, rec["chamfers"], rng, cap=rec["chamfers"]["capShare"] * float(ext.min()),
                            worn=1.0 if drop > 0 else rec["chamfers"]["stossShare"])
            if faces is None or H.volume(faces) < 1e-3:
                continue
            blocks.append((faces, {"id": f"blk-{i}", "group": f"grp-{g}", "drop": drop, "top": z0 - drop, "saw": k,
                                   "grad": back.grad_under(land)}))
    for cut_ in rec.get("cuts", []):
        blocks = apply_cut(blocks, cut_)
    return blocks


def cut(cells, n, d, label):
    """Every cell the plane n.p = d crosses cut in two, both sides kept, the new faces labelled."""
    out = []
    for cell in cells:
        s = np.concatenate([f.V for f in cell]) @ n
        if not (s.min() + 1e-4 < d < s.max() - 1e-4):
            out.append(cell)
            continue
        out += [q for q in (H.clip(cell, n, d, label), H.clip(cell, -n, -d, label)) if q is not None and H.volume(q) > 1e-3]
    return out


def sheet_field(key, x, y, cell):
    """A slow seeded field in [0, 1] (value noise on a coarse grid, smoothly blended): where the stoss lost more of
    its sheets. Non-semantic: it claims no event, only the rock's own unevenness."""
    gx, gy = x / cell, y / cell
    ix, iy = int(np.floor(gx)), int(np.floor(gy))
    fx, fy = gx - ix, gy - iy
    v = lambda i, j: HS.Stream(key, "sheets", i, j).uniform(0, 1)
    sx, sy = fx * fx * (3 - 2 * fx), fy * fy * (3 - 2 * fy)
    a = v(ix, iy) + (v(ix + 1, iy) - v(ix, iy)) * sx
    b = v(ix, iy + 1) + (v(ix + 1, iy + 1) - v(ix, iy + 1)) * sx
    return a + (b - a) * sy


def exposure(sea, land, c):
    """The sea's exposure on the side of the outcrop a block stands on (the record's compass weights)."""
    dx, dy = c[0] - land.c[0], c[1] - land.c[1]
    e = sea["exposure"]
    b = math.degrees(math.atan2(dx, dy)) % 360
    ways = [(0, e["north"]), (90, e["east"]), (180, e["south"]), (270, e["west"]), (360, e["north"])]
    for (b0, w0), (b1, w1) in zip(ways, ways[1:]):
        if b0 <= b <= b1:
            return w0 + (w1 - w0) * (b - b0) / 90
    return 0.0


def chamfer(faces, top, rec, rng, cap, worn):
    """A block's top edges worn back where it meets its joints: a narrow bevel on a tight joint, a broad round-over
    into the gully an open joint became. Each is one plane through the top, leaning down to the joint (rigid)."""
    t, dT = top
    for f in list(faces):
        kind = f.label
        if kind not in rec or kind.endswith("Share"):
            continue
        n = f.n
        if abs(n[2]) > 0.6:                      # not a side
            continue
        w0, w1, slope = rec[kind]
        w = min(rng.uniform(w0, w1) * (worn if kind.endswith("-open") else 1.0), cap)
        # the line where the top meets the joint face drawn in by w; the bevel leans from it at `slope` to the top
        A = np.array([t, n, np.cross(t, n)])
        if abs(np.linalg.det(A)) < 1e-6:
            continue
        p0 = np.linalg.solve(A, np.array([dT, f.d - w, 0.0]))
        m = t + slope * n
        m /= np.linalg.norm(m)
        faces = H.clip(faces, m, float(m @ p0), kind + "-worn")
        if faces is None:
            return None
    return faces


def apply_cut(blocks, cut):
    """A dated cut along a line: the blocks it crosses split by its two walls, the part between lowered to its floor."""
    out = []
    pts = [np.array(p, float) for p in cut["line"]]
    w = cut["width"] / 2
    for faces, info in blocks:
        parts = [(faces, info)]
        for a, b, za, zb in zip(pts, pts[1:], cut["floor"], cut["floor"][1:]):
            d = (b - a) / np.linalg.norm(b - a)
            nrm = np.array([-d[1], d[0], 0.0])
            nxt = []
            for f, inf in parts:
                # beyond the segment's ends: untouched
                inside_end = H.clip(f, np.array([d[0], d[1], 0.0]), float(d @ b), CUT)
                if inside_end is None:
                    nxt.append((f, inf))
                    continue
                beyond = H.clip(f, -np.array([d[0], d[1], 0.0]), -float(d @ b), CUT)
                if beyond is not None:
                    nxt.append((beyond, inf))
                f2 = H.clip(inside_end, -np.array([d[0], d[1], 0.0]), -float(d @ a), CUT)
                before = H.clip(inside_end, np.array([d[0], d[1], 0.0]), float(d @ a), CUT)
                if before is not None:
                    nxt.append((before, inf))
                if f2 is None:
                    continue
                u0 = float(nrm[:2] @ a)                                      # across the corridor: u = n.p - u0
                left = H.clip(f2, -nrm, -(u0 + w), CUT)                      # u >= w
                right = H.clip(f2, nrm, u0 - w, CUT)                         # u <= -w
                mid = H.clip(f2, nrm, u0 + w, CUT)
                mid = H.clip(mid, -nrm, -(u0 - w), CUT) if mid is not None else None
                for q in (left, right):
                    if q is not None and H.volume(q) > 1e-3:
                        nxt.append((q, inf))
                if mid is not None:
                    # the floor: a plane through the line's two ends at their floor heights, level across
                    k = (zb - za) / float(np.linalg.norm(b - a))
                    fl = np.array([-k * d[0], -k * d[1], 1.0])
                    q = H.clip(mid, fl / np.linalg.norm(fl), (za - k * float(d @ a)) / np.linalg.norm(fl), CUT)
                    if q is not None and H.volume(q) > 1e-3:
                        nxt.append((q, dict(inf, cut=cut["id"])))
            parts = nxt
        out += parts
    return out
