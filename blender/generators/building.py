"""Builds a resolved plan into a mesh: walls, roofs, volumes, parts, ornament, life.

build(plan, style) reads a plan from blender/resolver/resolve.py and a stylisation
name (gentle, strong, wild) and returns one Blender object. Units are metres here;
the plan is in millimetres. The street side faces -Y; the pivot is the bottom
centre of the main footprint.
"""

import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "resolver"))

from kit import Builder, Frame, clip_x, clip_below, clip_above, subtract  # noqa: E402
import palette  # noqa: E402
import parts  # noqa: E402
from parts import Ctx  # noqa: E402
from hashing import h, unit  # noqa: E402
from eras import ERAS, STYLES  # noqa: E402

UP = (0, 0, 1)


def mm(x):
    return x / 1000.0


def snap(x, step):
    return max(step, round(x / step) * step)


# -- walls -------------------------------------------------------------------------------


def wall(b, fr, panels, openings, band, t, lap, swatch, vertical=False):
    """Clad a wall. panels: convex regions dict(lo, hi, b_lo, b_hi, below=[(m, c)], above=[(m, c)]).
    openings: list of (a0, a1, b0, b1) holes. Horizontal lapped boards, or vertical boards."""
    for p in panels:
        if vertical:
            _vertical(b, fr, p, openings, band, t, swatch)
            continue
        k = int(math.floor(p["b_lo"] / band + 1e-6))
        while k * band < p["b_hi"] - 1e-6:
            b0, b1 = max(k * band, p["b_lo"]), min((k + 1) * band, p["b_hi"])
            k += 1
            if b1 - b0 < 0.01:
                continue
            poly = [(p["lo"], b0), (p["hi"], b0), (p["hi"], b1), (p["lo"], b1)]
            for m, c in p.get("below", []):
                poly = clip_below(poly, m, c) if poly else poly
            for m, c in p.get("above", []):
                poly = clip_above(poly, m, c) if poly else poly
            if not poly:
                continue
            xs = [q[0] for q in poly]
            spans = [(min(xs), max(xs))]
            for a0, a1, ob0, ob1 in openings:
                if ob0 <= b0 + 1e-4 and ob1 >= b1 - 1e-4:
                    spans = subtract(spans, (a0, a1))
            for lo, hi in spans:
                piece = clip_x(poly, lo, hi)
                if piece:
                    b.strip(fr, piece, b0, b1, t, lap, swatch)


def _vertical(b, fr, p, openings, band, t, swatch):
    """Vertical boards with battens: the 1970s cladding."""
    bw = max(0.12, band * 0.45)
    k = int(math.floor(p["lo"] / bw))
    while k * bw < p["hi"] - 1e-6:
        a0, a1 = max(k * bw, p["lo"]), min((k + 1) * bw, p["hi"])
        k += 1
        ranges = [(p["b_lo"], p["b_hi"])]
        for oa0, oa1, ob0, ob1 in openings:
            if oa0 <= a0 + 1e-4 and oa1 >= a1 - 1e-4:
                ranges = subtract(ranges, (ob0, ob1))
            elif oa0 < a1 and oa1 > a0:
                ranges = subtract(ranges, (ob0, ob1))
        for r0, r1 in ranges:
            poly = [(a0, r0), (a1, r0), (a1, r1), (a0, r1)]
            for m, c in p.get("below", []):
                poly = clip_below(poly, m, c) if poly else poly
            for m, c in p.get("above", []):
                poly = clip_above(poly, m, c) if poly else poly
            if poly:
                b.strip(fr, poly, r0, r1, t, 0.0, swatch)
                ys = [q[1] for q in poly]
                b.box(fr, a0, (min(ys) + max(ys)) / 2, t + 0.012, 0.022, (max(ys) - min(ys)) / 2, 0.012, swatch)


# -- roofs -------------------------------------------------------------------------------


class Roof:
    """A pitched roof over a rectangle: ridge along U, sides across X, segments from the wall line inward."""

    def __init__(self, base, U, X, a0, a1, hw, z0, segs, e, kick, rt, ch, lap):
        self.base = (base[0], base[1])
        self.U, self.X = U, X
        self.a0, self.a1, self.hw, self.z0 = a0, a1, hw, z0
        self.rt, self.ch, self.lap = rt, ch, lap
        first = segs[0][0]
        pe = first * (1 - 0.45 * kick)
        self.profile = {}
        for s in (-1, 1):
            pts = [(s * (hw + e), z0 - e * math.tan(pe)), (s * hw, z0)]
            x, z = s * hw, z0
            for pitch, run in segs:
                x -= s * run
                z += run * math.tan(pitch)
                pts.append((x, z))
            self.profile[s] = pts
        self.ridge = self.profile[1][-1][1]
        self.segs = segs
        self.last_pitch = segs[-1][0]
        self.edge = None  # colour of course edges; the roof colour unless set

    def point(self, along, across, z):
        U, X = self.U, self.X
        return (self.base[0] + U[0] * along + X[0] * across, self.base[1] + U[1] * along + X[1] * across, z)

    def frame(self, along, across, z, u, v, n):
        return Frame(self.point(along, across, z), u, v, n)

    def vec(self, across, z):
        X = self.X
        return (X[0] * across, X[1] * across, z)

    def top(self, d):
        """Height of the roof's top surface at horizontal distance d from the ridge line."""
        pts = self.profile[1]
        for (x0, z0), (x1, z1) in zip(pts[::-1][:-1], pts[::-1][1:]):
            if abs(x0) <= d <= abs(x1) + 1e-9:
                t = (d - abs(x0)) / max(1e-9, abs(x1) - abs(x0))
                z = z0 + (z1 - z0) * t
                pitch = math.atan2(abs(z1 - z0), abs(x1 - x0))
                return z + self.rt / max(0.2, math.cos(pitch))
        return pts[0][1]

    def at_height(self, zt):
        """Distance from the ridge where the top surface reaches height zt (zt below the ridge)."""
        lo, hi = 0.0, self.hw
        for _ in range(40):
            mid = (lo + hi) / 2
            if self.top(mid) > zt:
                lo = mid
            else:
                hi = mid
        return (lo + hi) / 2

    def build(self, b, roof_col, trim, cuts=(), cham=0.0, ridge_col="roof_ridge"):
        for s in (-1, 1):
            pts = self.profile[s]
            run_from_eave = 0.0
            for i in range(len(pts) - 1):
                (x0, z0), (x1, z1) = pts[i], pts[i + 1]
                dx, dz = x1 - x0, z1 - z0
                length = math.hypot(dx, dz)
                vx, vz = dx / length, dz / length
                n1, n2 = (-vz, vx), (vz, -vx)
                nx, nz = n1 if n1[1] > 0 else n2
                fr = Frame(self.point(0, x0, z0), self.U, self.vec(vx, vz), self.vec(nx, nz))
                ext = 0.05 if i < len(pts) - 2 else 0.0
                L = length + ext
                k = 0
                while k * self.ch < L - 1e-6:
                    c0, c1 = k * self.ch, min(L, (k + 1) * self.ch)
                    k += 1
                    spans = [(self.a0, self.a1)]
                    start = run_from_eave + c0 * abs(vx)
                    for cs, cmax, lo, hi in cuts:
                        if cs == s and start < cmax:
                            spans = subtract(spans, (lo, hi))
                    for lo, hi in spans:
                        b.strip(fr, [(lo, c0), (hi, c0), (hi, c1), (lo, c1)], c0, c1, self.rt, self.lap, roof_col, side_swatch=self.edge or roof_col)
                run_from_eave += abs(dx)
        rw = self.rt * math.sin(self.last_pitch) + 0.12
        ridge_z = self.ridge + self.rt / max(0.2, math.cos(self.last_pitch)) - 0.02
        fr = Frame(self.point(0, 0, 0), self.U, UP, self.vec(1, 0))
        b.box(fr, (self.a0 + self.a1) / 2, ridge_z, 0, (self.a1 - self.a0) / 2 + 0.02, 0.09, rw, ridge_col, chamfer=cham)

    def gable_lines(self, zb):
        """Half-planes b <= m*a + c (a across, b height above zb) that a gable wall must stay under."""
        lines = []
        for s in (-1, 1):
            pts = self.profile[s][1:]
            for (x0, z0), (x1, z1) in zip(pts[:-1], pts[1:]):
                m = (z1 - z0) / (x1 - x0)
                lines.append((m, (z0 - zb) - m * x0))
        return lines

    def barges(self, b, at_along, outward, c, fret, crossing, finial, bb=0.24):
        """Barge boards along the gable edge, with fretwork teeth and crossed ends when the era has them."""
        n = (self.U[0] * outward, self.U[1] * outward, 0)
        fr = Frame(self.point(at_along, 0, 0), self.vec(1, 0), UP, n)
        for s in (-1, 1):
            pts = self.profile[s]
            for i in range(len(pts) - 1):
                (x0, z0), (x1, z1) = pts[i], pts[i + 1]
                if crossing and i == len(pts) - 2:
                    d = math.hypot(x1 - x0, z1 - z0)
                    x1, z1 = x1 + (x1 - x0) / d * 0.45, z1 + (z1 - z0) / d * 0.45
                top0, top1 = z0 - 0.02, z1 - 0.02
                poly = [(x0, top0 - bb), (x1, top1 - bb), (x1, top1), (x0, top0)]
                if x1 < x0:
                    poly = [(x1, top1 - bb), (x0, top0 - bb), (x0, top0), (x1, top1)]
                b.strip(fr, poly, min(top0, top1) - bb, max(top0, top1), 0.05, 0.0, c.trim)
                if fret:
                    seg = math.hypot(x1 - x0, z1 - z0)
                    nt = max(1, int(seg / 0.24))
                    for k in range(nt):
                        t0, t1 = k / nt, (k + 0.7) / nt
                        p0 = (x0 + (x1 - x0) * t0, top0 + (top1 - top0) * t0 - bb)
                        p1 = (x0 + (x1 - x0) * t1, top0 + (top1 - top0) * t1 - bb)
                        mid = ((p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2 - 0.14)
                        tri = [p0, p1, mid] if p1[0] > p0[0] else [p1, p0, mid]
                        b.strip(fr, tri, mid[1], max(p0[1], p1[1]), 0.04, 0.0, c.trim)
        if finial:
            b.box(fr, 0, self.ridge + 0.45, 0.03, 0.04, 0.55, 0.04, c.trim, chamfer=0.01)
            b.box(fr, 0, self.ridge + 1.0, 0.03, 0.08, 0.08, 0.08, c.trim, chamfer=0.02)


# -- the building ----------------------------------------------------------------------------


def build(plan, style="strong", name=None, material=None):
    s = STYLES[style]
    m = plan["main"]
    ws, bid = plan["seed"], plan["id"]
    key = lambda *parts_: h(ws, bid, "look", *parts_)
    coat = plan["coats"][-1]
    E = ERAS[m["era"]]
    orn = m["ornament"]
    b = Builder()

    band = s["band"] / 1000.0
    lap = s["lap"] / 1000.0
    t = 0.05
    fw = s["frame"] / 1000.0
    cham = s["chamfer"] / 1000.0
    win_scale = s["win"] / 1000.0
    jitter = s["jitter"] / 1000.0
    tilt = math.radians(s["tilt"] / 10.0)
    ctx = Ctx(t, lap, fw, cham, coat["trim"], coat["trim"], coat["wall"], coat["door"])
    occupied = plan.get("business") is not None or plan["condition"] > 450
    flowers = occupied and plan["condition"] > 650 and key("flowers") % 1000 < 450
    curtain_kind = "half" if key("curtain") % 3 == 0 else "sides"
    curtain_col = "curtain" if key("cc") % 2 else "curtain_warm"

    W, D, P = mm(m["W"]), mm(m["D"]), mm(m["plinth"])
    H = mm(m["H"])
    pitch_push = s["pitch"] / 1000.0
    r = m["roof"]
    if r["type"] == "mansard":
        segs = [(math.radians(min(78, r["lower_pitch"] / 10.0 * (1 + (pitch_push - 1) * 0.3))), mm(r["lower_run"])),
                (math.radians(r["pitch"] / 10.0 * pitch_push), D / 2 - mm(r["lower_run"]))]
    else:
        pitch = math.radians(min(62, r["pitch"] / 10.0 * (pitch_push if r["type"] != "flat" else 1.0)))
        segs = [(pitch, D / 2)]
    e = mm(r["eave"]) * s["eave"] / 1000.0
    g = mm(r["gable"]) * s["eave"] / 1000.0
    kick = (s["kick"] / 1000.0) if r.get("kick") else 0.0
    rt = 0.16
    ch = 0.26 + band * 0.4
    vertical = m.get("cladding") == "vertical"

    roof = Roof((0, 0), (1, 0, 0), (0, 1, 0), -W / 2 - g, W / 2 + g, D / 2, P + H, segs, e, kick, rt, ch, lap * 2.5)

    frames = {
        "front": Frame((0, -D / 2, P), (1, 0, 0), UP, (0, -1, 0)),
        "back": Frame((0, D / 2, P), (-1, 0, 0), UP, (0, 1, 0)),
        "left": Frame((-W / 2, 0, P), (0, 1, 0), UP, (-1, 0, 0)),
        "right": Frame((W / 2, 0, P), (0, 1, 0), UP, (1, 0, 0)),
    }
    orient_map = {"front": "front", "back": "back", "left": "left", "right": "right"}
    if m["orient"] == "gable":
        orient_map = {"front": "left", "back": "right", "left": "back", "right": "front"}

    # -- openings, snapped to the cladding bands ----------------------------------------
    openings = {k: [] for k in ("front", "back", "left", "right")}
    placed = []  # (facade_local, cell, a0, a1, b0, b1)
    for c in plan["cells"]:
        if c["facade"] not in openings:
            continue
        local = orient_map[c["facade"]]
        w = mm(c["w"]) * (win_scale if c["part"]["type"] == "window" else 1.0)
        a = mm(c["a"]) + (unit(key("jit", c["facade"], c["a"], c["b0"])) - 0.5) * 2 * jitter * (c["part"]["type"] == "window")
        b0 = snap(mm(c["b0"]), band) if c["b0"] > 0 else 0.0
        b1 = b0 + snap(mm(c["b1"] - c["b0"]) * (win_scale if c["part"]["type"] == "window" else 1.0), band)
        if c["part"]["type"] in ("door", "inner_door", "loading_door") and c["b0"] == 0:
            b1 = snap(mm(c["b1"]), band)
        a0, a1 = a - w / 2, a + w / 2
        openings[local].append((a0, a1, b0, b1))
        placed.append((local, c, a0, a1, b0, b1))

    # -- main walls --------------------------------------------------------------------------
    ark = next((x for x in plan["additions"] if x["kind"] == "ark"), None)
    long_panel = dict(lo=-W / 2, hi=W / 2, b_lo=0.0, b_hi=H)
    gable_panel = dict(lo=-D / 2, hi=D / 2, b_lo=0.0, b_hi=roof.ridge - P + 0.01, below=roof.gable_lines(P))
    ark_roof = None
    if ark:
        ax, aw = mm(ark["x"]), mm(ark["w"])
        pa = min(math.radians(64), segs[-1][0] * 1.12)
        apex = P + H + (aw / 2) * math.tan(pa)
        if apex + 2 * rt < roof.ridge - 0.4:
            y_back = -roof.at_height(apex + 2.5 * rt)
            ark_roof = Roof((ax, 0), (0, 1, 0), (1, 0, 0), -(D / 2 + g * 0.8), y_back, aw / 2, P + H, [(pa, aw / 2)], e * 0.8, kick, rt, ch, lap * 2.5)
    wall_panels = {"front": [long_panel], "back": [long_panel], "left": [gable_panel], "right": [gable_panel]}
    if ark_roof:
        lines = [(mm_, c_ - mm_ * ax) for mm_, c_ in ark_roof.gable_lines(P)]
        wall_panels["front"] = [long_panel, dict(lo=ax - aw / 2, hi=ax + aw / 2, b_lo=H, b_hi=ark_roof.ridge - P + 0.01, below=lines)]
    for name_, fr in frames.items():
        wall(b, fr, wall_panels[name_], openings[name_], band, t, lap, coat["wall"], vertical)

    # corner boards, or pilasters in classical houses
    out = t + lap + 0.012
    pil = orn.get("pilasters")
    cb = (0.3 if pil else 0.12 + fw * 0.6)
    world = Frame((0, 0, 0), (1, 0, 0), UP, (0, -1, 0))
    if not vertical:
        for sx in (-1, 1):
            for sy in (-1, 1):
                cx, cy = sx * (W / 2 + out - cb / 2), sy * (D / 2 + out - cb / 2)
                b.box(world, cx, P + H / 2, -cy, cb / 2, H / 2, cb / 2, coat["trim"], chamfer=cham * 0.5)
                if pil:
                    b.box(world, cx, P + H - 0.12, -cy, cb / 2 + 0.05, 0.12, cb / 2 + 0.05, coat["trim"], chamfer=cham)
                    b.box(world, cx, P + 0.15, -cy, cb / 2 + 0.04, 0.15, cb / 2 + 0.04, coat["trim"], chamfer=cham)
    # belt courses between storeys
    if orn.get("belt") and m["full"] >= 2:
        S = mm(m["storey_h"])
        for st in range(1, m["full"]):
            z = st * S - 0.05
            for name_, fr in frames.items():
                lo, hi = (-W / 2, W / 2) if name_ in ("front", "back") else (-D / 2, D / 2)
                b.box(fr, 0, z, out / 2 + 0.02, (hi - lo) / 2 + out, 0.07, out / 2 + 0.02, coat["trim"], chamfer=cham)
    # cornice under the eaves
    if orn.get("cornice"):
        for name_ in ("front", "back"):
            fr = frames[name_]
            b.box(fr, 0, H - 0.12, out / 2 + 0.06, W / 2 + out + 0.05, 0.12, out / 2 + 0.06, coat["trim"], chamfer=cham)

    # -- plinth -------------------------------------------------------------------------------
    pe = t + lap + 0.05
    b.box(world, 0, P / 2, 0, W / 2 + pe, P / 2, D / 2 + pe, "stone", chamfer=cham)

    # -- roof -----------------------------------------------------------------------------------
    cuts = []
    if ark_roof:
        cuts.append((-1, e + 0.35, ax - aw / 2, ax + aw / 2))
    roof.build(b, r["swatch"], coat["trim"], cuts=cuts, cham=cham)
    for along, outward in ((roof.a0 + 0.03, -1), (roof.a1 - 0.03, 1)):
        roof.barges(b, along, outward, ctx, fret=orn.get("fret"), crossing=orn.get("crossing"), finial=orn.get("finial"))
    if ark_roof:
        ark_roof.build(b, r["swatch"], coat["trim"], cham=cham)
        ark_roof.barges(b, ark_roof.a0 + 0.03, -1, ctx, fret=orn.get("fret"), crossing=orn.get("crossing"), finial=orn.get("finial"))
    # brackets under the eaves
    if orn.get("brackets"):
        n = max(3, int(W / 1.25))
        pe_ = segs[0][0] * (1 - 0.45 * kick)
        for side in (-1, 1):
            for k in range(n + 1):
                x = -W / 2 + k * W / n
                fr = Frame((x - 0.03, side * (D / 2 + t), P + H), (0, side, 0), UP, (1, 0, 0))
                om = e * 0.85
                tri = [(0, -0.02), (om, -om * math.tan(pe_) - 0.02), (0, -0.55)]
                b.strip(fr, tri, -0.55, -0.02, 0.06, 0.0, coat["trim"])
    # gutters and downpipes
    gutter = "metal_gutter" if plan["year"] >= 1950 else "metal_dark"
    pe_ = segs[0][0] * (1 - 0.45 * kick)
    for side in (-1, 1):
        y = side * (D / 2 + e + 0.04)
        z = P + H - e * math.tan(pe_) - 0.06
        b.box(world, 0, z, -y, W / 2 + g * 0.6, 0.06, 0.07, gutter)
    for sx in (-1, 1):
        x = sx * (W / 2 - 0.25)
        y = -(D / 2 + 0.12)
        z_top = P + H - e * math.tan(pe_) - 0.1
        b.box(world, x, z_top / 2, -y, 0.045, z_top / 2, 0.045, gutter)
        b.box(world, x, z_top - 0.05, -(y - (e - 0.1) / 2), 0.04, 0.04, (e - 0.1) / 2 + 0.04, gutter)

    # -- chimneys --------------------------------------------------------------------------------
    cs = (0.55 + fw * 0.8) * s["chimney"] / 1000.0
    for i, chm in enumerate(plan["chimneys"]):
        cx, cy = mm(chm["x"]), mm(chm["y"])
        top = roof.ridge + 0.9 * s["chimney"] / 1000.0
        col = "render_white" if chm["era"] in ("classical", "functionalist") else "brick"
        ang = math.radians((unit(key("chim", i)) - 0.5) * s["lean"] / 10.0 * 1.6)
        cf = parts.tilted(Frame((0, cy, 0), (1, 0, 0), UP, (0, -1, 0)), cx, (P + H + top) / 2, ang)
        b.box(cf, 0, 0, 0, cs / 2, (top - P - H) / 2, cs / 2, col, chamfer=cham)
        b.box(cf, 0, (top - P - H) / 2 + 0.05, 0, cs / 2 + 0.07, 0.05, cs / 2 + 0.07, "stone_dark", chamfer=cham)
        if chm["era"] in ("chalet", "jugend"):
            b.box(cf, 0, (top - P - H) / 2 - 0.18, 0, cs / 2 + 0.04, 0.05, cs / 2 + 0.04, col, chamfer=cham)

    # -- additions --------------------------------------------------------------------------------
    S = mm(m["storey_h"])
    for add in plan["additions"]:
        k = add["kind"]
        E_add = ERAS[add["era"]]
        if k == "bislag":
            _bislag(b, plan, add, ctx, coat, W, D, P, H, band, t, lap, rt, ch, cham, s, key, roof)
        elif k == "veranda":
            _veranda(b, plan, add, ctx, coat, W, D, P, S, cham)
        elif k == "bay":
            _bay(b, plan, add, ctx, coat, W, D, P, S, band, t, lap, cham, win_scale, vertical, key, curtain_col, curtain_kind)
        elif k == "dormers":
            for i, x in enumerate(add["xs"]):
                _dormer(b, plan, add, ctx, coat, mm(x), roof, band, t, lap, rt, ch, cham, s, kick, win_scale, orn, key, i)
        elif k == "lean_to":
            _lean_to(b, plan, add, ctx, coat, W, D, P, H, band, t, lap, rt, ch, cham, E_add, roof)
        elif k == "hoist":
            _hoist(b, plan, ctx, coat, W, D, P, H, roof, r, cham)

    # -- parts in the cells ------------------------------------------------------------------------
    business = plan.get("business")
    ghost = bool(plan.get("ghosts")) and not business
    for local, c, a0, a1, b0, b1 in placed:
        fr = frames[local]
        part = c["part"]
        ang = (unit(key("tilt", c["facade"], c["a"], c["b0"])) - 0.5) * 2 * tilt
        boarded = "boarded" in c
        crown = _crown(part, ERAS[part["era"]]["ornament"], orn, plan, part["era"])
        if part["type"] == "window":
            lit = False
            curt = (curtain_col, curtain_kind) if occupied else None
            parts.window(b, fr, a0, a1, b0, b1, ctx, part["style"], angle=ang, crown=crown, boarded=boarded, reduced=c.get("reduced", False), curtain=curt, lit=lit)
            if flowers and local == "front" and c.get("row", 0) in (0, 1) and not boarded:
                parts.flower_box(b, fr, a0, a1, b0, ctx, key("fb", c["a"], c["b0"]))
        elif part["type"] == "door":
            parts.door(b, fr, a0, a1, b0, b1, ctx, part["style"], angle=ang * 0.5, crown=crown, boarded=boarded)
            if local == "front" or (m["orient"] == "gable"):
                parts.steps(b, fr, (a0 + a1) / 2, a1 - a0, P, ctx)
        elif part["type"] == "inner_door":
            pass  # hidden inside the porch; the wall behind it stays open
        elif part["type"] == "shopfront":
            parts.shopfront(b, fr, a0, a1, b0, b1, ctx, part["style"], sign=business, ghost=ghost, boarded=boarded)
        elif part["type"] == "loading_door":
            parts.loading_door(b, fr, a0, a1, b0, b1, ctx, boarded=boarded)

    # -- the hand: lean, sag and bow ------------------------------------------------------------------
    # the lean always shows: at least half the style's amount, in a seeded direction
    lx = unit(key("lx"))
    lean_x = math.tan(math.radians(s["lean"] / 10.0 * (0.5 + 0.5 * abs(lx * 2 - 1)) * (1 if lx > 0.5 else -1)))
    lean_y = math.tan(math.radians(s["lean"] / 10.0 * 0.3 * (unit(key("ly")) * 2 - 1)))
    # old and neglected houses sag more
    age = max(0, plan["year"] - plan["built"])
    sag = s["sag"] / 1000.0 * (0.4 + 0.6 * unit(key("sag"))) * (0.6 + min(1.0, age / 120.0) + (1000 - plan["condition"]) / 1000.0)
    bow = s["bow"] / 1000.0 * (0.4 + 0.6 * unit(key("bow")))
    eave_z, ridge = P + H, roof.ridge
    span = W / 2 + g + 0.1

    def hand(v):
        x, y, z = v
        f = 0.0
        if z > eave_z - 1.0:
            q = min(max((z - (eave_z - 1.0)) / (ridge - eave_z + 1.0), 0.0), 1.0)
            f = q * q * (3 - 2 * q)
        shape = max(0.0, 1.0 - (x / span) ** 2)
        z2 = z - sag * f * shape
        if P < z < P + H:
            tt = (z - P) / H
            bulge = bow * math.sin(math.pi * tt)
            fx = max(-1.0, min(1.0, x / (W / 2)))
            fy = max(-1.0, min(1.0, y / (D / 2)))
            x += bulge * fx * (1 - 0.7 * fy * fy) * 0.5
            y += bulge * fy * (1 - 0.7 * fx * fx)
        return type(v)((x + lean_x * z, y + lean_y * z, z2))

    b.deform(hand)
    if m["orient"] == "gable":
        b.deform(lambda v: type(v)((-v[1], v[0], v[2])))

    name = name or f"bld_{bid}_{plan['year']}_{style}"
    obj = b.build(name, material or palette.material())
    obj["triangles"] = b.triangles()
    obj["plan_year"] = plan["year"]
    return obj


def _crown(part, part_orn, host_orn, plan, era):
    style = part["style"]
    if part["type"] not in ("window", "door"):
        return None
    if style in ("band", "picture", "casement", "stick_bars", "funkis_canopy", "teak_strip", "eighties"):
        return None
    if part.get("restored") or part["event"] == plan["main"]["event"]:
        # parts from the house's own building carry its ornament
        if host_orn.get("pediment"):
            return "pediment"
        if host_orn.get("cornice"):
            return "cornice"
        if style == "cross_arch":
            return "arch"
        return "flat"
    return "flat" if part_orn.get("pediment") or part_orn.get("cornice") else None


# -- additions ------------------------------------------------------------------------------------


def _bislag(b, plan, add, c, coat, W, D, P, H, band, t, lap, rt, ch, cham, s, key, main_roof):
    bx, bw, bd = mm(add["x"]), mm(add["w"]), mm(add["d"])
    Hb = snap(2.5, band)
    pb = math.radians(min(62, 50 * s["pitch"] / 1000.0))
    while P + Hb + (bw / 2) * math.tan(pb) + rt > P + H - 0.2 and pb > math.radians(25):
        pb -= math.radians(3)
    gb = 0.2 + band * 0.3
    roof = Roof((bx, 0), (0, 1, 0), (1, 0, 0), -(D / 2 + bd + gb), -D / 2 + 0.25, bw / 2, P + Hb, [(pb, bw / 2)], 0.22, 0.0, rt, ch, lap * 2.5)
    front = Frame((bx, -D / 2 - bd, P), (1, 0, 0), UP, (0, -1, 0))
    door = next(cc for cc in plan["cells"] if cc["facade"] == "bislag")
    dw = mm(door["w"])
    dh = snap(mm(door["b1"]), band)
    holes = [(-dw / 2, dw / 2, 0.0, dh)]
    lines = [(m_, c_ - m_ * 0.0) for m_, c_ in roof.gable_lines(P)]
    lines = [(m_, c_ + m_ * bx) for m_, c_ in lines]
    lines = [(m_, c_ - m_ * bx) for m_, c_ in lines]
    wall(b, front, [dict(lo=-bw / 2, hi=bw / 2, b_lo=0.0, b_hi=Hb), dict(lo=-bw / 2, hi=bw / 2, b_lo=Hb, b_hi=roof.ridge - P + 0.01, below=lines)], holes, band, t, lap, coat["wall"])
    side_win = key("bislag_win") % 2 == 0
    for sx in (-1, 1):
        fr = Frame((bx + sx * bw / 2, -D / 2 - bd / 2, P), (0, 1, 0), UP, (sx, 0, 0))
        hole = []
        if side_win:
            wb0 = snap(1.0, band)
            hole = [(-0.25, 0.25, wb0, wb0 + snap(0.8, band))]
        wall(b, fr, [dict(lo=-bd / 2, hi=bd / 2, b_lo=0.0, b_hi=Hb)], hole, band, t, lap, coat["wall"])
        if side_win:
            parts.window(b, fr, -0.25, 0.25, hole[0][2], hole[0][3], c, "small_panes" if plan["main"]["era"] == "classical" else "cross_t", crown="flat")
    world = Frame((0, 0, 0), (1, 0, 0), UP, (0, -1, 0))
    b.box(world, bx, P / 2, D / 2 + bd / 2, bw / 2 + 0.1, P / 2, bd / 2 + 0.1, "stone", chamfer=cham)
    roof.build(b, plan["main"]["roof"]["swatch"], coat["trim"], cham=cham)
    orn = plan["main"]["ornament"]
    roof.barges(b, roof.a0 + 0.03, -1, c, fret=orn.get("fret"), crossing=orn.get("crossing"), finial=orn.get("finial"), bb=0.18)
    E = ERAS[add["era"]]
    parts.door(b, front, -dw / 2, dw / 2, 0.0, dh, c, door["part"]["style"], crown="pediment" if orn.get("pediment") else "flat")
    parts.steps(b, front, 0.0, dw, P, c)


def _veranda(b, plan, add, c, coat, W, D, P, S, cham):
    sv = add["side"]
    vw, vd, vy = mm(add["w"]), mm(add["d"]), mm(add["y"])
    Hv = S - 0.15
    x_in, x_out = sv * W / 2, sv * (W / 2 + vd)
    xc = (x_in + x_out) / 2
    world = Frame((0, 0, 0), (1, 0, 0), UP, (0, -1, 0))
    b.box(world, xc, P / 2, -vy, vd / 2 + 0.05, P / 2, vw / 2 + 0.05, "stone", chamfer=cham)
    faces = [
        (Frame((x_out, vy, P), (0, 1, 0), UP, (sv, 0, 0)), -vw / 2, vw / 2),
        (Frame((xc, vy - vw / 2, P), (1, 0, 0), UP, (0, -1, 0)), -vd / 2, vd / 2),
        (Frame((xc, vy + vw / 2, P), (-1, 0, 0), UP, (0, 1, 0)), -vd / 2, vd / 2),
    ]
    for fr, lo, hi in faces:
        n = max(2, int(round((hi - lo) / 0.85)))
        b.box(fr, (lo + hi) / 2, 0.42, 0.04, (hi - lo) / 2, 0.42, 0.04, coat["wall"], chamfer=cham)
        b.box(fr, (lo + hi) / 2, 0.88, 0.06, (hi - lo) / 2 + 0.03, 0.04, 0.07, coat["trim"], chamfer=cham)
        b.box(fr, (lo + hi) / 2, (0.9 + Hv - 0.3) / 2, 0.0, (hi - lo) / 2, (Hv - 1.2) / 2, 0.01, "glass_shop")
        b.box(fr, (lo + hi) / 2, Hv - 0.62, 0.03, (hi - lo) / 2, 0.03, 0.04, coat["trim"])
        b.box(fr, (lo + hi) / 2, Hv - 0.15, 0.05, (hi - lo) / 2 + 0.05, 0.15, 0.08, coat["trim"], chamfer=cham)
        for k in range(n + 1):
            a = lo + k * (hi - lo) / n
            b.box(fr, a, Hv / 2, 0.05, 0.06, Hv / 2, 0.06, coat["trim"], chamfer=cham)
            if 0 < k < n:
                for row in range(1, 3):
                    b.box(fr, a + (hi - lo) / n / 2, 0.9 + (Hv - 1.2) * row / 3, 0.02, (hi - lo) / n / 2, 0.012, 0.02, coat["trim"])
    roof_z = P + Hv
    b.box(world, xc, roof_z + 0.11, -vy, vd / 2 + 0.18, 0.11, vw / 2 + 0.18, {"default": coat["trim"], "v+": "roof_black"}, chamfer=cham)
    if plan["main"]["full"] >= 2:
        rz = roof_z + 0.22
        for fr, lo, hi in faces:
            fr2 = Frame((fr.o[0], fr.o[1], rz), fr.u, fr.v, fr.n)
            b.box(fr2, (lo + hi) / 2, 0.9, 0.0, (hi - lo) / 2 + 0.05, 0.035, 0.05, coat["trim"], chamfer=cham)
            n = max(2, int((hi - lo) / 0.14))
            for k in range(n + 1):
                b.box(fr2, lo + k * (hi - lo) / n, 0.45, 0.0, 0.018 if k % 6 else 0.04, 0.45, 0.018 if k % 6 else 0.04, coat["trim"])


def _bay(b, plan, add, c, coat, W, D, P, S, band, t, lap, cham, win_scale, vertical, key, curtain_col, curtain_kind):
    bx, bw, bd = mm(add["x"]), mm(add["w"]), mm(add["d"])
    m = plan["main"]
    z0, z1 = S - 0.25, m["full"] * S
    front = Frame((bx, -D / 2 - bd, P), (1, 0, 0), UP, (0, -1, 0))
    sides = {sx: Frame((bx + sx * bw / 2, -D / 2 - bd / 2, P), (0, 1, 0), UP, (sx, 0, 0)) for sx in (-1, 1)}
    cells = [cc for cc in plan["cells"] if cc["facade"].startswith("bay_")]
    holes = {"bay_front": [], "bay_left": [], "bay_right": []}
    for cc in cells:
        w = mm(cc["w"]) * win_scale
        b0 = snap(mm(cc["b0"]), band)
        b1 = b0 + snap(mm(cc["b1"] - cc["b0"]) * win_scale, band)
        holes[cc["facade"]].append((-w / 2, w / 2, b0, b1, cc))
    wall(b, front, [dict(lo=-bw / 2, hi=bw / 2, b_lo=z0, b_hi=z1)], [hh[:4] for hh in holes["bay_front"]], band, t, lap, coat["wall"], vertical)
    for sx, name_ in ((-1, "bay_left"), (1, "bay_right")):
        wall(b, sides[sx], [dict(lo=-bd / 2, hi=bd / 2, b_lo=z0, b_hi=z1)], [hh[:4] for hh in holes[name_]], band, t, lap, coat["wall"], vertical)
    for name_, fr in (("bay_front", front), ("bay_left", sides[-1]), ("bay_right", sides[1])):
        for a0, a1, b0, b1, cc in holes[name_]:
            parts.window(b, fr, a0, a1, b0, b1, c, cc["part"]["style"], crown="flat" if name_ == "bay_front" else None, curtain=(curtain_col, curtain_kind))
    world = Frame((0, 0, 0), (1, 0, 0), UP, (0, -1, 0))
    b.box(world, bx, P + z0 - 0.08, D / 2 + bd / 2, bw / 2 + 0.06, 0.08, bd / 2 + 0.06, coat["trim"], chamfer=cham)
    for sx in (-1, 1):
        fr = Frame((bx + sx * (bw / 2 - 0.15) - 0.03, -D / 2, P + z0 - 0.16), (0, -1, 0), UP, (1, 0, 0))
        b.strip(fr, [(0, 0), (bd, 0), (0, -0.6)], -0.6, 0, 0.06, 0.0, coat["trim"])
    b.box(world, bx, P + z1 + 0.1, D / 2 + bd / 2 - 0.02, bw / 2 + 0.14, 0.1, bd / 2 + 0.14, {"default": coat["trim"], "v+": plan["main"]["roof"]["swatch"]}, chamfer=cham)


def _dormer(b, plan, add, c, coat, dx, roof, band, t, lap, rt, ch, cham, s, kick, win_scale, orn, key, i):
    m = plan["main"]
    dw = mm(add["w"]) * (0.9 + 0.2 * s["win"] / 1000.0)
    mansard = m["roof"]["type"] == "mansard"
    setback = 0.15 if mansard else 0.6
    d0 = roof.hw - setback
    z_base = roof.top(d0)
    hd = snap(1.4, band)
    pd = math.radians(min(60, 48 * s["pitch"] / 1000.0))
    apex = z_base + hd + (dw / 2) * math.tan(pd)
    if apex + 2 * rt > roof.ridge - 0.25:
        hd = max(band, hd - band)
        apex = z_base + hd + (dw / 2) * math.tan(pd)
        if apex + 2 * rt > roof.ridge - 0.25:
            return
    d_end = roof.at_height(apex + 2.5 * rt)
    droof = Roof((dx, 0), (0, 1, 0), (1, 0, 0), -(d0 + 0.25), -d_end, dw / 2, z_base + hd, [(pd, dw / 2)], 0.2, kick * 0.5, rt, ch, lap * 2.5)
    front = Frame((dx, -d0, z_base), (1, 0, 0), UP, (0, -1, 0))
    era_win = ERAS[add["era"]]["window"]
    ww = min(dw - 0.5, 0.85 * win_scale)
    wb0 = snap(0.25, band)
    wb1 = min(hd + 0.3, wb0 + snap(1.0, band))
    lines = [(m_, c_ - m_ * dx) for m_, c_ in droof.gable_lines(z_base)]
    lines = [(m_, c_ + m_ * dx) for m_, c_ in lines]
    wall(b, front, [dict(lo=-dw / 2, hi=dw / 2, b_lo=0.0, b_hi=hd), dict(lo=-dw / 2, hi=dw / 2, b_lo=hd, b_hi=droof.ridge - z_base + 0.01, below=lines)], [(-ww / 2, ww / 2, wb0, wb1)], band, t, lap, coat["wall"])
    slope = (roof.top(d0 - 1.0) - z_base) / 1.0
    run_e = hd / max(0.2, slope)
    for sx in (-1, 1):
        fr = Frame((dx + sx * dw / 2, -d0, z_base), (0, 1, 0), UP, (sx, 0, 0))
        wall(b, fr, [dict(lo=0.0, hi=run_e, b_lo=0.0, b_hi=hd, above=[(slope, -0.02)])], [], band, t, lap, coat["wall"])
    droof.build(b, m["roof"]["swatch"], coat["trim"], cham=cham)
    droof.barges(b, droof.a0 + 0.03, -1, c, fret=orn.get("fret"), crossing=False, finial=orn.get("finial"), bb=0.14)
    parts.window(b, front, -ww / 2, ww / 2, wb0, wb1, c, era_win, crown=None, curtain=None)


def _lean_to(b, plan, add, c, coat, W, D, P, H, band, t, lap, rt, ch, cham, E_add, main_roof):
    lw, ld = mm(add["w"]), mm(add["d"])
    Hl = snap(2.3, band)
    Hh = min(H - 0.35, Hl + ld * math.tan(math.radians(18)))
    vertical = E_add.get("cladding") == "vertical"
    wall_col = coat["wall"] if E_add["care"] >= 500 else ("wall_brown" if vertical else coat["wall"])
    back = Frame((0, D / 2 + ld, P), (-1, 0, 0), UP, (0, 1, 0))
    wall(b, back, [dict(lo=-lw / 2, hi=lw / 2, b_lo=0.0, b_hi=Hl)], [(-0.5, 0.5, snap(0.9, band), snap(0.9, band) + snap(1.0, band))], band, t, lap, wall_col, vertical)
    parts.window(b, back, -0.5, 0.5, snap(0.9, band), snap(0.9, band) + snap(1.0, band), c, E_add["window"])
    m_slope = -(Hh - Hl) / ld
    for sx in (-1, 1):
        fr = Frame((sx * lw / 2, D / 2 + ld / 2, P), (0, 1, 0), UP, (sx, 0, 0))
        wall(b, fr, [dict(lo=-ld / 2, hi=ld / 2, b_lo=0.0, b_hi=Hh + 0.01, below=[(m_slope, (Hh + Hl) / 2)])], [], band, t, lap, wall_col, vertical)
    pitch = math.atan2(Hh - Hl, ld)
    e = 0.3
    fr = Frame((0, D / 2 + ld + e, P + Hl - e * math.tan(pitch)), (1, 0, 0), (0, -math.cos(pitch), math.sin(pitch)), (0, math.sin(pitch), math.cos(pitch)))
    L = (ld + e + 0.2) / math.cos(pitch)
    k = 0
    while k * ch < L:
        c0, c1 = k * ch, min(L, (k + 1) * ch)
        k += 1
        b.strip(fr, [(-lw / 2 - 0.2, c0), (lw / 2 + 0.2, c0), (lw / 2 + 0.2, c1), (-lw / 2 - 0.2, c1)], c0, c1, rt * 0.8, lap * 2.0, "roof_black" if E_add["care"] < 500 else plan["main"]["roof"]["swatch"])
    world = Frame((0, 0, 0), (1, 0, 0), UP, (0, -1, 0))
    b.box(world, 0, P / 2, -(D / 2 + ld / 2), lw / 2 + 0.05, P / 2, ld / 2 + 0.05, "stone", chamfer=cham)


def _hoist(b, plan, c, coat, W, D, P, H, roof, r, cham):
    """The Stavanger-ark on a quay warehouse: a hoist housing over the loft door, with its beam."""
    # built before rotation: the quay gable is the local left gable (x = -W/2)
    hw, hd = 0.9, 1.0
    zb = P + H + 1.8
    x0 = -W / 2
    hb = Frame((x0 - hd / 2, 0, zb), (0, 1, 0), UP, (-1, 0, 0))
    b.box(hb, 0, 0.6, 0, hw, 0.6, hd / 2, coat["wall"], chamfer=cham)
    hr = Roof((x0 - hd / 2 + 0.2, 0), (1, 0, 0), (0, 1, 0), -hd / 2 - 0.25, hd / 2 + 0.6, hw, zb + 1.2, [(math.radians(45), hw)], 0.15, 0.0, 0.12, 0.25, 0.02)
    hr.build(b, r["swatch"], coat["trim"], cham=cham)
    beam = Frame((x0 - hd - 0.3, 0, zb + 1.0), (1, 0, 0), UP, (0, -1, 0))
    b.box(beam, 0.4, 0, 0, 0.7, 0.07, 0.07, "wood", chamfer=0.01)
    b.box(beam, -0.25, -0.5, 0, 0.012, 0.5, 0.012, "metal_dark")
