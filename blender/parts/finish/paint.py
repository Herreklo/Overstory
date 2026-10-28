"""Way P's page and strokes: 107's corner painted as a painter would (finish.json `painted`).

    Blender -b --factory-startup -P blender/parts/finish/paint.py -- --gen <corner.py's out> --cache cache/finish

Writes into <cache>/out:
  hist-p.png        1,024 square, 8 bits, linear: R the peel's field and B the stain's, each shape's edge at 0.5 and
                    ramped over its `soft` either side, so a stroke can move the edge; G a value shift, 0.5 + dL*/80
                    (the foot's gradient, lighter tops, contact shade, the battens' end grain, the nails' heads, a
                    few tiles); A the lap grime's strength
  paint-stroke.png  the authored strokes, 1 m square, tiling: R, G and B three sets of short flat brush strokes along
                    u, each its own value, which break the peel's, the stain's and the lap grime's edges near; A long
                    soft strokes along the boards, which let a plane breathe near and are gone by the street stop
  paint.json        the Unity scene's digest of way P (LT1Finish.cs), with its own overcast

Broad washes carry the light and the water (G); a few shapes with a hierarchy carry the damage (R, B), their
character at their edges. Every shape is placed by a fact: the surround's leaking side, the sill and its horns, the
eave's drips and what each carries, the battens and their nails, the courses. No shape claims a dated event (UK4): a
wash says water runs here, never when.
"""

import json
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import finishlib as FL  # noqa: E402
from finishlib import HS  # noqa: E402
import marks as MK  # noqa: E402

key = MK.key


def field(sd, soft):
    """A shape's field from its signed distance (inside positive): its edge at 0.5, ramped over `soft` either side."""
    return 0.5 + 0.5 * np.clip(sd / soft, -1.0, 1.0)


def wave(pg, k, cell, t=None):
    """A seeded low wave, -1..1, of `cell` metres along the wall (or along `t`): an edge drawn freehand."""
    t = pg.along if t is None else t
    return 2.0 * FL.noise2(t / cell, np.zeros(pg.shape), k) - 1.0


def board_patch(pg, Q, k, on, a0, a1, butt, top, share):
    """Paint lost on one board from its butt up `share` of its face, between a0 and a1 along: its foot the butt
    itself, its top edge drawn freehand, its ends ramped so the strokes break them."""
    W = Q["peel"]["wobble"]
    h = (top - butt) * share
    edge = butt + h * (1.0 - W["share"] * 0.5 * (1.0 + wave(pg, k, W["cell"])))
    sd = np.minimum(np.minimum(pg.along - a0, a1 - pg.along), edge - pg.z)
    return np.where(on & (pg.z >= butt) & (pg.z < top), field(sd, Q["peel"]["soft"]), 0.0)


def course_of(meta, z):
    """The course whose board shows at z: its butt and the butt above."""
    c = meta["courses"]
    i = max(j for j in range(len(c)) if c[j] <= z + 1e-6)
    return c[i], c[i + 1]


def horns(meta, side):
    """The sill's horns: the leaking one and the dry one, each with the way out from the window."""
    sx0, sx1 = meta["features"]["sill"][:2]
    leak = sx0 if side < 0 else sx1
    dry = sx1 if side < 0 else sx0
    return (leak, -1.0 if leak == sx0 else 1.0), (dry, -1.0 if dry == sx0 else 1.0)


def broad_splash(pg, Q, meta, splash):
    """The foot's wetting along the street wall in one broad swell under each drip, by how much its pan carries (not a
    bump per drip); the gable's even."""
    broad = np.zeros(pg.shape)
    for x, _, flow in meta["features"]["drips"]:
        broad = np.maximum(broad, flow * MK.gauss(pg.along - x, Q["foot"]["splashWidth"]))
    return np.where(pg.street, broad, splash)


def peel(pg, Q, meta, side):
    """Paint lost where water sits, with a hierarchy: one big zone at the foot on the leaking side, where the horn's
    run meets the splash; one medium under the sill's leaking end; a few small (under the dry horn, under the drips
    that carry most, at the gable's foot), the corner board's foot, the casing's leaking leg and the ledges' tops.
    Each board's patch stops at its lap; the bare wood shows, silvered."""
    R = Q["peel"]
    f, h = meta["features"], meta["heights"]
    clad = pg.m["cladding"] & pg.vertical
    trims = pg.m["trims"]
    out = np.zeros(pg.shape)
    (leak, lo), (dry, do) = horns(meta, side)
    z_sill = f["sill"][2]

    def add(g):
        nonlocal out
        out = np.maximum(out, g)

    def jit(k, v, spread=0.15):
        return v * (1.0 + spread * (2.0 * HS.unit(k) - 1.0))

    def courses_up(z):
        c = course_of(meta, z)
        while True:
            yield c
            c = course_of(meta, c[1] + 0.01)

    def courses_down(z):
        c = course_of(meta, z)
        while True:
            yield c
            c = course_of(meta, c[0] - 0.01)
    # the big zone: from the lowest board up, narrowing, leaning toward the run that feeds it
    B = R["big"]
    centre = leak + lo * B["offset"]
    for ci, ((hw, share), (butt, top)) in enumerate(zip(B["courses"], courses_up(h["drip"][1] + 0.01))):
        k = key(meta, "p-big", ci)
        c = centre - lo * B["lean"] * ci
        add(board_patch(pg, Q, k, clad & pg.street, c - jit(HS.h(k, 0), hw), c + jit(HS.h(k, 1), hw), butt, top, share))
    # the medium: the boards under the sill's leaking end
    for ci, ((o, i, share), (butt, top)) in enumerate(zip(R["medium"]["courses"], courses_down(z_sill - 0.01))):
        k = key(meta, "p-medium", ci)
        a = (leak + lo * jit(HS.h(k, "o"), o), leak - lo * jit(HS.h(k, "i"), i))
        add(board_patch(pg, Q, k, clad & pg.street, min(a), max(a), butt, top, share))
    # the small ones
    low = course_of(meta, h["drip"][1] + 0.01)
    ranked = sorted([d for d in f["drips"] if 0.05 < d[0] < meta["sample"][0] - 0.05], key=lambda d: -d[2])
    for si, S in enumerate(R["small"]):
        k = key(meta, "p-small", si)
        if S["under"] == "dryHorn":
            butt, top = course_of(meta, z_sill - 0.01)
            a = (dry + do * jit(HS.h(k, "o"), S["outside"]), dry - do * jit(HS.h(k, "i"), S["inside"]))
            add(board_patch(pg, Q, k, clad & pg.street, min(a), max(a), butt, top, S["share"]))
        elif S["under"] == "drip":
            x = ranked[S["rank"]][0] + 0.05 * (2.0 * HS.unit(HS.h(k, "at")) - 1.0)
            ln = jit(HS.h(k, "len"), S["length"])
            add(board_patch(pg, Q, k, clad & pg.street, x - ln / 2, x + ln / 2, low[0], low[1], S["share"]))
        else:
            add(board_patch(pg, Q, k, clad & ~pg.street, S["at"][0], S["at"][1], low[0], low[1], S["share"]))
    # the corner board's foot, both its faces, from the drip board up
    cw, _, cz0, _ = f["cornerBoard"]
    W = R["wobble"]
    corner = trims & pg.vertical & (np.abs(pg.along) < cw + 0.05) & (pg.z >= cz0 - 0.005)
    edge = R["corner"]["top"] - W["share"] * 0.15 * (1.0 + wave(pg, key(meta, "p-corner"), W["cell"], pg.p[..., 0] + pg.p[..., 1]))
    add(np.where(corner, field(edge - pg.z, R["soft"]), 0.0))
    # the casing's leg on the leaking side, at its foot on the sill, where the surround's joint feeds it
    cx0, cx1, cz0_, _ = f["casing"]
    ax0, ax1 = f["sheets"][0], f["sheets"][1]
    leg = (cx0 - 0.01, ax0) if side < 0 else (ax1, cx1 + 0.01)
    on = trims & pg.vertical & pg.street & (pg.along > leg[0]) & (pg.along < leg[1]) & (pg.z >= cz0_ - 0.005)
    edge = cz0_ + R["casing"]["reach"] * (1.0 - W["share"] * 0.5 * (1.0 + wave(pg, key(meta, "p-casing"), W["cell"], pg.z)))
    add(np.where(on, field(edge - pg.z, R["soft"]), 0.0))
    # the ledges' tops stand wet: bare but at their ends, where the casing and the corner keep them; a top cut by the
    # sample's edge runs on
    tops = trims & pg.up
    a0p, a1p = pg.per_piece(pg.along, "min"), pg.per_piece(pg.along, "max")
    lo_cut = np.where(pg.street, 0.0, -meta["sample"][1])
    hi_cut = np.where(pg.street, meta["sample"][0], 0.0)
    ins = R["tops"]["inset"] * (1.0 + 0.5 * wave(pg, key(meta, "p-tops"), W["cell"]))
    d0 = np.where(a0p <= lo_cut + 0.01, np.inf, pg.along - a0p - ins)
    d1 = np.where(a1p >= hi_cut - 0.01, np.inf, a1p - pg.along - ins)
    add(np.where(tops, field(np.minimum(np.minimum(d0, d1), 1.0), R["soft"]), 0.0))
    return np.where(pg.m["cladding"] | trims, out, 0.0)


def run(pg, k, x0, z0, length, width, wander, mask):
    """A run from (x0, z0) down: its field 1 at its head, its strength easing to the edge (0.5) at `length`, so its
    contour tapers to a point; it wanders a little as it runs."""
    d = z0 - pg.z
    a = np.clip(1.0 - 0.5 * d / length, 0.0, 1.0)
    x = x0 + wander * (2.0 * FL.noise2(np.clip(d, 0, None) / 0.1, np.zeros(pg.shape), k) - 1.0)
    return np.where(mask & (d >= 0), a * np.exp(-((pg.along - x) / width) ** 2), 0.0)


def boarding(Q, which=None):
    """The boarding's variant: `which` or the one kept."""
    Bd = Q["boarding"]
    return Bd[which or Bd["use"]]


def stains(pg, Q, meta, side, broad):
    """The stain field, shapes with a found edge: rust under some of the battens' nails, the boarding's damp strip
    down its leaking side (its one edge on the sheet; its others the sheet's own, under the casing), and the plinth's
    wet margin."""
    f = meta["features"]
    out = np.zeros(pg.shape)

    def add(g):
        nonlocal out
        out = np.maximum(out, g)
    # rust under some of the battens' nails, down the batten and the casing below it
    Ru = Q["rust"]
    k = key(meta, "p-rust")
    iron = (pg.m["trims"] | pg.m["batten"]) & pg.street & (pg.y < 0.0)
    for i, (xn, zn) in enumerate(f["nails"]):
        if HS.unit(HS.h(k, i)) >= Ru["share"]:
            continue
        ln = Ru["length"][0] + (Ru["length"][1] - Ru["length"][0]) * HS.unit(HS.h(k, i, "len"))
        add(run(pg, HS.h(k, i, "w"), xn, zn, ln, Ru["width"], 0.002, iron))
    # the boarding's damp strip
    B = Q["sheet"]
    ab0, ab1 = f["sheets"][:2]
    from_leak = np.where(side < 0, pg.along - ab0, ab1 - pg.along)
    sd = B["leakWidth"] + B["wobble"]["amp"] * wave(pg, key(meta, "p-sheet", "leak"), B["wobble"]["cell"], pg.z) - from_leak
    add(np.where(pg.m["sheet"], field(sd, 0.04), 0.0))
    # the plinth's wet margin: splash from the drips keeps its foot wet, higher under the drips that carry most
    Wt = Q["wet"]
    top = Wt["top"] + Wt["splash"] * broad + Wt["wobble"]["amp"] * wave(pg, key(meta, "p-wet"), Wt["wobble"]["cell"])
    add(np.where(pg.m["stone"] & pg.vertical, field(top - pg.z, Wt["soft"]), 0.0))
    return out


def wall_tops(pg, mask, cell=0.02):
    """Each wall's top above every point along it (the street wall's eave, the gable's rising verge)."""
    tops = np.zeros(pg.shape)
    for face in (pg.street, ~pg.street):
        m = mask & face & pg.cov
        if not m.any():
            continue
        lo = pg.along[m].min()
        bins = np.clip(((pg.along - lo) / cell).astype(np.int64), 0, None)
        top = np.full(bins[m].max() + 1, -np.inf)
        np.maximum.at(top, bins[m], pg.z[m])
        idx = np.arange(len(top))
        ok = np.isfinite(top)
        top = np.interp(idx, idx[ok], top[ok])
        tops = np.where(face, top[np.clip(bins, 0, len(top) - 1)], tops)
    return tops


def values(pg, Q, meta, side, broad, board):
    """The value shifts, dL*: broad washes first (the whole wall lighter under the eave's contact band and falling to
    its foot, the foot's dirt, a soft wash widening under the sill, one broad tapering wash from each horn, the
    boarding's damp), then the small: tops lighter, contact shade, the battens' end grain and the nails' heads, the
    sheets' join, a few tiles lit."""
    f, h = meta["features"], meta["heights"]
    dl = np.zeros(pg.shape)
    wall = (pg.m["cladding"] | pg.m["trims"]) & pg.vertical
    # the wall carries the light: lighter under the eave's band, falling to the foot
    top = wall_tops(pg, pg.m["cladding"] & pg.vertical)
    zf = h["drip"][1]
    t = np.clip((pg.z - zf) / np.maximum(top - zf, 0.1), 0.0, 1.0)
    Wl = Q["wall"]
    dl += np.where(wall, Wl["footL"] + (Wl["topL"] - Wl["footL"]) * FL.smoothstep(0.0, 1.0, t), 0.0)
    E = Q["eave"]
    dl -= np.where(wall, E["L"] * (1.0 - FL.smoothstep(0.0, E["reach"], top - pg.z)) ** 1.5, 0.0)
    # the foot's dirt rises higher under the drips that carry most, in one broad swell each
    Fo = Q["foot"]
    reach = Fo["reach"] * (1.0 - Fo["splash"] + Fo["splash"] * broad)
    t = np.clip((pg.z - zf) / reach, 0.0, 1.0)
    dl -= np.where(wall, Fo["L"] * (1.0 - t) ** Fo["power"], 0.0)
    dl -= np.where(pg.m["stone"] & pg.vertical, Fo["plinthL"] * (1.0 - np.clip(pg.z / h["plinth"], 0.0, 1.0)), 0.0)
    # under the sill, the water it sheds: a soft wash widening down
    sx0, sx1, z_sill, _ = f["sill"]
    Sw = Q["sillWash"]
    below = np.clip(z_sill - pg.z, 0.0, None)
    hw = (sx1 - sx0) / 2.0 + Sw["spread"] * below
    across = MK.soft_box(pg.along - (sx0 + sx1) / 2.0, -hw, hw, Sw["soft"])
    fall = (1.0 - np.clip(below / Sw["reach"], 0.0, 1.0)) ** 1.5
    dl -= np.where(pg.m["cladding"] & pg.vertical & pg.street & (pg.z < z_sill), Sw["L"] * across * fall, 0.0)
    # from each horn, one broad wash down the boards: widest and darkest at its head, tapering as it fades; its
    # outer side a found edge, its inner side lost
    Wa = Q["wash"]
    for name, (horn, out_dir) in zip(("leak", "dry"), horns(meta, side)):
        S = Wa[name]
        k = key(meta, "p-wash", name)
        d = np.clip(z_sill - pg.z, 0.0, None)
        tt = np.clip(d / S["length"], 0.0, 1.0)
        x = horn - out_dir * Wa["inset"] + Wa["wanderMm"] / 1000.0 * wave(pg, k, 0.15, d)
        w = S["width"] * (1.0 - S["taper"] * tt)
        s = out_dir * (pg.along - x) / w
        across = np.where(s > 0, 1.0 - FL.smoothstep(1.0 - S["found"], 1.0, s), np.exp(-s * s))
        on = pg.m["cladding"] & pg.vertical & pg.street & (pg.z < z_sill)
        dl -= np.where(on, S["L"] * across * (1.0 - tt) ** S["power"], 0.0)
    # the boarding holds water: darkest at its head and down its leaking side, above the lower batten and at the sill;
    # one soft wash
    Bw = board["wash"]
    sheet = pg.m["sheet"]
    ab0, ab1, zb0, zb1 = f["sheets"][:4]
    from_leak = np.where(side < 0, pg.along - ab0, ab1 - pg.along)
    head = (1.0 - FL.smoothstep(0.0, Bw["head"], zb1 - pg.z)) * (1.0 - 0.5 * np.clip(from_leak / (ab1 - ab0), 0, 1))
    lk = 1.0 - FL.smoothstep(0.0, Bw["leak"], from_leak)
    bx0, bx1, zc, slope, bw = f["battens"][0]
    zl = zc + slope * (pg.along - (bx0 + bx1) / 2.0) + bw / 2.0
    lowness = np.clip(0.5 - np.sign(slope) * (pg.along - (bx0 + bx1) / 2.0) / max(bx1 - bx0, 1e-3), 0.0, 1.0)
    bat = np.where(pg.z > zl - 0.01, 1.0 - FL.smoothstep(0.0, Bw["batten"] * (1.0 + Bw["lowEnd"] * lowness), pg.z - zl), 0.0)
    sill = 1.0 - FL.smoothstep(0.0, Bw["sill"], pg.z - zb0)
    wash = 1.0 - (1.0 - head) * (1.0 - lk) * (1.0 - 0.7 * bat) * (1.0 - 0.6 * sill)
    dl -= np.where(sheet, Bw["L"] * wash, 0.0)
    dl += np.where((pg.m["trims"] | pg.m["stone"] | pg.m["batten"]) & pg.up, Q["up"]["L"], 0.0)
    C = Q["contact"]
    occ = 1.0 - pg.ao
    shut = np.clip(1.0 - pg.cav, 0.0, 1.0)
    dl -= C["L"] * FL.smoothstep(C["ao"][0], C["ao"][1], occ) + C["cavL"] * FL.smoothstep(C["cav"][0], C["cav"][1], shut)
    # the battens: end grain drinks and darkens; the nails' heads
    Bt = Q["batten"]
    bat = pg.m["batten"]
    for bx0, bx1, zc, slope, w in f["battens"]:
        zl = pg.z - (zc + slope * (pg.along - (bx0 + bx1) / 2.0))
        on = bat & (np.abs(zl) <= w / 2.0 + 0.03) & (pg.along > bx0 - 0.05) & (pg.along < bx1 + 0.05)
        ends = np.minimum(np.abs(pg.along - bx0), np.abs(bx1 - pg.along))
        dl -= np.where(on, Bt["endL"] * FL.smoothstep(Bt["endMm"] / 1000.0, 0.0, ends), 0.0)
    Ru = Q["rust"]
    r_head = Ru["headMm"] / 1000.0
    for xn, zn in f["nails"]:
        r = np.hypot(pg.along - xn, pg.z - zn)
        dl -= np.where(bat & pg.street, Ru["headL"] * FL.smoothstep(r_head, 0.6 * r_head, r), 0.0)
    # the sheets' join, a dark seam
    B = Q["sheet"]
    z0, z1 = pg.per_piece(pg.z, "min"), pg.per_piece(pg.z, "max")
    zs0, zs1 = pg.z[sheet].min(), pg.z[sheet].max()
    dj = np.minimum(np.where(z1 >= zs1 - 0.01, np.inf, z1 - pg.z), np.where(z0 <= zs0 + 0.01, np.inf, pg.z - z0))
    dl -= np.where(sheet, B["joinL"] * FL.smoothstep(B["joinMm"] / 1000.0, 0.0, dj), 0.0)
    # the roof one dark mass, a few of its tiles catching more light
    T = Q["tiles"]
    u = FL.unit(key(meta, "p-tile"), pg.piece)
    v = FL.unit(key(meta, "p-tile-v"), pg.piece)
    dl += np.where(pg.m["tiles"] & (u < T["share"]), T["L"] * (0.5 + 0.5 * v), 0.0)
    return dl


def grime(pg, Q, meta, side):
    """The lap grime's strength on the boards: everywhere some, more toward the foot and on the courses the sill
    drips on."""
    L = Q["lap"]
    f, h = meta["features"], meta["heights"]
    sx0, sx1, z_sill, _ = f["sill"]
    foot = 1.0 - np.clip((pg.z - h["drip"][1]) / Q["foot"]["reach"], 0.0, 1.0)
    sill = MK.soft_box(pg.along, sx0 - 0.1, sx1 + 0.1, L["sillSoft"]) * MK.soft_box(pg.z, z_sill - 0.35, z_sill, L["sillSoft"]) * pg.street
    a = L["base"] + L["foot"] * foot + L["sill"] * sill
    return np.where(pg.m["cladding"] & pg.vertical, np.clip(a, 0.0, 1.0), 0.0)


def lay(n, px, k, cover, length, width, angle, taper, soft):
    """Strokes laid in a painter's order on a tiling square of `n` pixels, `px` metres each, until they cover it
    `cover` times: along u, up to `angle` off it, `length` and `width` ranges in metres, each stroke flat at its own
    value, the brush loaded at its start and running dry to a narrower end, its edge `soft` pixels."""
    cv = np.full((n, n), 0.5)
    area, i = 0.0, 0
    (l0, l1), (w0, w1) = length, width
    m = n * px
    while area < cover * m * m:
        u = lambda *p: HS.unit(HS.h(k, i, *p))  # noqa: E731
        ln = math.exp(math.log(l0) + (math.log(l1) - math.log(l0)) * u("len"))
        wd = w0 + (w1 - w0) * u("w")
        ang = math.radians(angle) * (2.0 * u("a") - 1.0)
        way = 1.0 if u("dir") < 0.5 else -1.0
        cx, cy = u("x") * n, u("y") * n
        hx = (ln / 2.0 + wd) / px + soft
        hy = (abs(math.sin(ang)) * ln / 2.0 + wd) / px + soft
        X, Y = np.meshgrid(np.arange(int(cx - hx), int(cx + hx) + 2), np.arange(int(cy - hy), int(cy + hy) + 2))
        dx, dy = (X + 0.5 - cx) * px, (Y + 0.5 - cy) * px
        s = way * (dx * math.cos(ang) + dy * math.sin(ang))
        t = -dx * math.sin(ang) + dy * math.cos(ang)
        hw = wd / 2.0 * (1.0 - taper * np.clip((s + ln / 2.0) / ln, 0.0, 1.0))
        d = np.hypot(np.maximum(np.abs(s) - ln / 2.0, 0.0), t) - hw
        a = np.clip(0.5 - d / (soft * px), 0.0, 1.0)
        ri, ci = Y % n, X % n
        cv[ri, ci] = cv[ri, ci] * (1.0 - a) + u("v") * a
        area += ln * wd
        i += 1
    return cv, i


def strokes(Q, meta):
    """The authored strokes on a tiling metre: R, G and B three sets of short flat ones that break the peel's, the
    stain's and the lap grime's edges near (5 to 30 cm long, 1 to 3 cm wide, a few degrees off the boards); A long
    soft ones along the boards (30 to 80 cm), the value a plane breathes by near."""
    S, Bh = Q["stroke"], Q["brush"]
    n = S["size"]
    px = S["metres"] / n
    mm = lambda r: [v / 1000.0 for v in r]  # noqa: E731
    out = np.full((n, n, 4), 0.5)
    for ch in range(3):
        out[..., ch], i = lay(n, px, key(meta, "p-stroke", ch), S["cover"], mm(S["lengthMm"]), mm(S["widthMm"]),
                              S["angleDeg"], S["taper"], S["softPx"])
        print(f"[paint] strokes {'RGB'[ch]}: {i}")
    out[..., 3], i = lay(n, px, key(meta, "p-brush"), Bh["cover"], mm(Bh["lengthMm"]), mm(Bh["widthMm"]),
                         Bh["angleDeg"], Bh["taper"], Bh["softPx"])
    print(f"[paint] brush A: {i}")
    return out


def main():
    a = MK.args()
    gen, cache = os.path.abspath(a["gen"]), os.path.abspath(a["cache"])
    meta = json.load(open(os.path.join(gen, "corner.json")))
    P = json.load(open(os.path.join(FL.ROOT, "blender", "parts", "finish", "finish.json")))
    Q = P["painted"]
    out = os.path.join(cache, "out")
    pg = MK.Page(cache, meta)
    pad = meta["page"]["padPx"]
    # the surround's joint leaks on one side (the seed marks.py's boarding reads)
    side = 1.0 if HS.unit(key(meta, "surround-leak")) < 0.5 else -1.0
    # the boarding's variant: --boarding a|b for the A/B, else the one kept
    which = a.get("boarding") or Q["boarding"]["use"]
    board = boarding(Q, which)

    broad = broad_splash(pg, Q, meta, MK.drip_splash(pg, P, meta))
    pl = peel(pg, Q, meta, side)
    sn = stains(pg, Q, meta, side, broad)
    dl = values(pg, Q, meta, side, broad, board)
    gr = grime(pg, Q, meta, side)
    hist = np.stack([pl, 0.5 + np.clip(dl, -40, 40) / 80.0, sn, gr], axis=-1)
    hist = FL.dilate(np.where(pg.cov[..., None], hist, 0), pg.cov, pad + 2)
    FL.write(os.path.join(out, "hist-p.png"), hist)
    FL.write(os.path.join(out, "paint-stroke.png"), strokes(Q, meta))

    E, L = Q["edge"], Q["lap"]
    sh = P["marks"]["shade"]
    M = P["materials"]
    mats = dict(Q["materials"], sheet=board["sheet"], batten=board["batten"])
    digest = {
        "mats": [{"name": k, "painted": 1 if M[k]["painted"] else 0, "L": v["L"], "bareL": v.get("bareL", v["L"]),
                  "underL": v.get("underL", v["L"]), "stainDL": v.get("stainDL", 0.0), "smooth": v["smooth"],
                  "stainSmooth": v.get("stainSmooth", v["smooth"]), "brushL": v.get("brushL", 0.0), "flatUp": v.get("flatUp", 0.0),
                  "stainEdge": v.get("stainEdge", 1.0)}
                 for k, v in mats.items()],
        "lights": [dict(v, light=k) for k, v in Q["light"].items()],
        "strokeScale": meta["page"]["size"] / meta["page"]["pxPerM"] / Q["stroke"]["metres"],
        "edgeAmp": E["amp"], "strokeFade": E["fadeLod"], "brushFade": Q["brush"]["fadeLod"], "rimL": E["rimL"],
        "rimW": E["rimW"], "bareShift": E["bareShift"],
        "aoStrength": Q["aoStrength"], "lapDark": L["occlusion"], "lapCore": L["occCoreMm"] / 1000.0,
        "lapReach": L["occReachMm"] / 1000.0, "lapGrimeL": L["grimeL"], "lapGrimeReach": L["reach"],
        "lapGrimeBreak": L["break"], "lapPage": sh["lapPageMm"] / 1000.0,
    }
    json.dump(digest, open(os.path.join(out, "paint.json"), "w"), indent=1)
    painted = pg.m["cladding"] | pg.m["trims"]
    share = lambda m: float((m & pg.cov).sum()) / max(1, int((painted & pg.cov).sum()))  # noqa: E731
    print(f"[paint] side {side:+.0f}; boarding {which}; peeled {share(painted & (pl > 0.5)):.3f} of the paint; "
          f"stained {share(sn > 0.5):.3f}; dL {np.percentile(dl[pg.cov], [5, 50, 95]).round(1)}; wrote {out}")


if __name__ == "__main__":
    main()
