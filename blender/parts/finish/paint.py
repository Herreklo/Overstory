"""Way P's page and strokes: 107's corner painted as a painter would (finish.json `painted`).

    Blender -b --factory-startup -P blender/parts/finish/paint.py -- --gen <corner.py's out> --cache cache/finish

Writes into <cache>/out:
  hist-p.png        1,024 square, 8 bits, linear: R the peel's field and B the stain's (the foot's dirt among them),
                    each shape's edge at 0.5 and ramped over its `soft` either side, so a stroke can move the edge; G
                    a value shift, 0.5 + dL*/(2 dlRange) (the wall's gradient, the washes, the darks at every
                    junction, lighter tops, the battens' end grain, the nails' heads, a few tiles); A the lap grime's
                    strength
  hist-p2.png       1,024 square: R the long washes, 0 to 1 of the darkest's L* (on the paint and the bare wood
                    alike: water darkens both), where the brush drags down them near
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
    itself, its top edge drawn freehand, its ends torn along the grain and drawing in as they rise, ramped so the
    strokes break them."""
    W, En = Q["peel"]["wobble"], Q["peel"]["ends"]
    h = (top - butt) * share
    edge = butt + h * (1.0 - W["share"] * 0.5 * (1.0 + wave(pg, k, W["cell"])))
    rise = np.clip(pg.z - butt, 0.0, None)
    e0 = a0 + En["lean"] * rise + En["amp"] * wave(pg, HS.h(k, "e0"), En["cell"], pg.z)
    e1 = a1 - En["lean"] * rise + En["amp"] * wave(pg, HS.h(k, "e1"), En["cell"], pg.z)
    sd = np.minimum(np.minimum(pg.along - e0, e1 - pg.along), edge - pg.z)
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


def foot_top(pg, Q, meta, broad):
    """The foot's dirt: its top edge, painted freehand, higher under the drips that carry most."""
    Fo = Q["foot"]
    k = key(meta, "p-foot")
    top = meta["heights"]["drip"][1] + Fo["height"] * (1.0 - Fo["splash"] + Fo["splash"] * broad)
    for i, (amp, cell) in enumerate(Fo["rag"]):
        top = top + amp * wave(pg, HS.h(k, i), cell)
    return top


def junction(d, base, to, reach):
    """A junction's dark, as a shift: the value `base` drawn down to `to` at the junction, easing back over `reach`;
    nothing on its far side, and nothing where the value is darker already."""
    w = np.where(d >= -0.002, 1.0 - FL.smoothstep(0.0, reach, d), 0.0)
    return w * np.maximum(base - to, 0.0)


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


def stains(pg, Q, meta, side, broad, foot):
    """The stain field, shapes with a found edge: the foot's dirt on the boards, its top ragged; rust under some of
    the battens' nails; the boarding's damp strip down its leaking side (its one edge on the sheet; its others the
    sheet's own, under the casing); and the plinth's wet margin."""
    f = meta["features"]
    out = np.zeros(pg.shape)

    def add(g):
        nonlocal out
        out = np.maximum(out, g)
    zf = meta["heights"]["drip"][1]
    add(np.where(pg.m["cladding"] & pg.vertical & (pg.z >= zf - 0.005), field(foot - pg.z, Q["foot"]["soft"]), 0.0))
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


def edges(pg, mask, top=True, cell=0.02):
    """The top (or the foot) of what `mask` covers above every point along each wall: the street wall's eave, the
    gable's rising verge, a batten's lower edge."""
    out = np.zeros(pg.shape)
    for face in (pg.street, ~pg.street):
        m = mask & face & pg.cov
        if not m.any():
            continue
        lo = pg.along[m].min()
        bins = np.clip(((pg.along - lo) / cell).astype(np.int64), 0, None)
        e = np.full(bins[m].max() + 1, -np.inf if top else np.inf)
        (np.maximum if top else np.minimum).at(e, bins[m], pg.z[m])
        idx = np.arange(len(e))
        ok = np.isfinite(e)
        e = np.interp(idx, idx[ok], e[ok])
        out = np.where(face, e[np.clip(bins, 0, len(e) - 1)], out)
    return out


def values(pg, Q, meta, side, broad, board, foot, sn):
    """The value shifts, dL*, and the washes' strength: broad washes first (the wall's big gradient, its contact band
    under the eave down to the body and the foot's dirt below it, a soft wash widening under the sill, one long wash
    from each horn and one from the head's leaking end, the boarding's damp), then the darks at every junction
    (under the eave, the sill and each batten, the boards onto the drip board, the plinth under it and onto the
    ground), then the small: tops lighter, contact shade, the battens' end grain and the nails' heads, the sheets'
    join, a few tiles lit."""
    f, h = meta["features"], meta["heights"]
    dl = np.zeros(pg.shape)
    streak = np.zeros(pg.shape)
    clad = pg.m["cladding"] & pg.vertical
    wall = (pg.m["cladding"] | pg.m["trims"]) & pg.vertical
    stone = pg.m["stone"] & pg.vertical
    J = Q["junction"]
    # the wall's body a little lighter toward its top; under the eave a contact band, dark at the eave and fading
    # down to the body
    top = edges(pg, clad)
    zf = h["drip"][1]
    t = np.clip((pg.z - zf) / np.maximum(top - zf, 0.1), 0.0, 1.0)
    Wl = Q["wall"]
    dl += np.where(wall, Wl["footL"] + (Wl["topL"] - Wl["footL"]) * FL.smoothstep(0.0, 1.0, t), 0.0)
    E = Q["eave"]
    d = top - pg.z
    dl -= np.where(wall & (d >= -0.002), E["L"] * (1.0 - FL.smoothstep(0.0, E["reach"], d)) ** E["power"], 0.0)
    # the foot's dirt (the boards' share is the stain field's): darker still toward the drip board; on the trims, the
    # same zone as a value
    Fo = Q["foot"]
    t = np.clip((pg.z - zf) / np.maximum(foot - zf, 0.05), 0.0, 1.0)
    dl -= np.where(clad & (pg.z < foot), Fo["L"] * (1.0 - t) ** Fo["power"], 0.0)
    dl -= np.where(pg.m["trims"] & pg.vertical, Fo["trimL"] * field(foot - pg.z, Fo["soft"]), 0.0)
    dl -= np.where(stone, Fo["plinthL"] * (1.0 - np.clip(pg.z / h["plinth"], 0.0, 1.0)), 0.0)
    # under the sill, the water it sheds: a soft wash widening down
    sx0, sx1, z_sill, _ = f["sill"]
    Sw = Q["sillWash"]
    below = np.clip(z_sill - pg.z, 0.0, None)
    hw = (sx1 - sx0) / 2.0 + Sw["spread"] * below
    across = MK.soft_box(pg.along - (sx0 + sx1) / 2.0, -hw, hw, Sw["soft"])
    fall = (1.0 - np.clip(below / Sw["reach"], 0.0, 1.0)) ** 1.5
    dl -= np.where(clad & pg.street & (pg.z < z_sill), Sw["L"] * across * fall, 0.0)
    # three long washes, each one continuous: from each horn down the boards and over the drip board's face, and from
    # the head's leaking end down beside the casing to its horn. Widest and darkest at the head, tapering as each
    # fades; its outer side a found edge, its inner side lost
    Wa = Q["wash"]
    (leak, lo), (dry, do) = horns(meta, side)
    below_sill = (clad | (pg.m["trims"] & pg.vertical & (pg.z < zf + 0.003))) & pg.street & (pg.z < z_sill)
    beside = clad & pg.street & (pg.z < h["head"]) & (pg.z > f["casing"][2])
    for name, horn, out_dir, z0, on in (("leak", leak, lo, z_sill, below_sill), ("dry", dry, do, z_sill, below_sill),
                                        ("cap", leak, lo, h["head"], beside)):
        S = Wa[name]
        k = key(meta, "p-wash", name)
        d = np.clip(z0 - pg.z, 0.0, None)
        tt = np.clip(d / S["length"], 0.0, 1.0)
        x = horn - out_dir * Wa["inset"] + Wa["wanderMm"] / 1000.0 * wave(pg, k, 0.15, d)
        w = S["width"] * (1.0 - S["taper"] * tt)
        s = out_dir * (pg.along - x) / w
        across = np.where(s > 0, 1.0 - FL.smoothstep(1.0 - S["found"], 1.0, s), np.exp(-s * s))
        g = np.where(on, across * (1.0 - tt) ** S["power"], 0.0)
        streak = np.maximum(streak, S["L"] * g)
    # the boarding holds water: darkest at its head and down its leaking side and at the sill, in one soft wash; a
    # band of its own above the lower batten
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
    wash = 1.0 - (1.0 - head) * (1.0 - lk) * (1.0 - 0.6 * sill)
    dl -= np.where(sheet, np.maximum(Bw["L"] * wash, Bw["batL"] * bat), 0.0)
    # the small
    dl += np.where((pg.m["trims"] | pg.m["stone"] | pg.m["batten"]) & pg.up, Q["up"]["L"], 0.0)
    C = Q["contact"]
    occ = 1.0 - pg.ao
    shut = np.clip(1.0 - pg.cav, 0.0, 1.0)
    dl -= C["L"] * FL.smoothstep(C["ao"][0], C["ao"][1], occ) + C["cavL"] * FL.smoothstep(C["cav"][0], C["cav"][1], shut)
    # the darks at every junction, each drawn down to its own value from what the paint is there
    mats = dict(Q["materials"], sheet=board["sheet"], batten=board["batten"])
    base = np.zeros(pg.shape)
    for name, v in mats.items():
        base = np.where(pg.m[name], v["L"] - v.get("stainDL", 0.0) * (sn > 0.5), base)

    def down(mask, d, to, reach):
        nonlocal dl
        dl -= np.where(mask, junction(d, base + dl, to, reach), 0.0)
    down(wall, top - pg.z, J["eave"]["to"], J["eave"]["reach"])
    down(clad & pg.street & (MK.soft_box(pg.along, sx0, sx1, 0.015) > 0.5), z_sill - pg.z, J["sill"]["to"], J["sill"]["reach"])
    for v in meta["pieces"]:
        if v["mat"] != "batten":
            continue
        b = (pg.piece == v["i"]) & pg.vertical
        if not (b & pg.cov).any():
            continue
        foot_b = edges(pg, b, top=False)
        a0, a1 = pg.along[b & pg.cov].min(), pg.along[b & pg.cov].max()
        under = pg.street & (pg.along > a0) & (pg.along < a1)
        dB = foot_b - pg.z
        down(wall & ~b & under, dB, J["batten"]["to"], J["batten"]["reach"])
        down(sheet & under, dB, J["batten"]["sheetTo"], J["batten"]["reach"])
    down(sheet, zb1 - pg.z, J["head"]["to"], J["head"]["reach"])
    down(clad, pg.z - zf, J["drip"]["to"], J["drip"]["reach"])
    down(stone, h["drip"][0] - pg.z, J["plinth"]["to"], J["plinth"]["reach"])
    down(stone, pg.z, J["ground"]["to"], J["ground"]["reach"])
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
    return dl, streak / max(Wa[n]["L"] for n in ("leak", "dry", "cap"))


def grime(pg, Q, meta, side):
    """The lap grime's strength on the boards: everywhere some, more toward the foot and on the courses the sill
    drips on."""
    L = Q["lap"]
    f, h = meta["features"], meta["heights"]
    sx0, sx1, z_sill, _ = f["sill"]
    foot = 1.0 - np.clip((pg.z - h["drip"][1]) / Q["foot"]["height"], 0.0, 1.0)
    sill = MK.soft_box(pg.along, sx0 - 0.1, sx1 + 0.1, L["sillSoft"]) * MK.soft_box(pg.z, z_sill - 0.35, z_sill, L["sillSoft"]) * pg.street
    a = L["base"] + L["foot"] * foot + L["sill"] * sill
    return np.where(pg.m["cladding"] & pg.vertical, np.clip(a, 0.0, 1.0), 0.0)


def lay(n, px, k, cover, length, width, angle, taper, soft, dry=0.0):
    """Strokes laid in a painter's order on a tiling square of `n` pixels, `px` metres each, until they cover it
    `cover` times: along u, up to `angle` off it, `length` and `width` ranges in metres, each stroke flat at its own
    value, the brush loaded at its start and running dry to a narrower end (losing `dry` of its cover by then), its
    edge `soft` pixels."""
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
        a = np.clip(0.5 - d / (soft * px), 0.0, 1.0) * (1.0 - dry * np.clip((s + ln / 2.0) / ln, 0.0, 1.0))
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
                         Bh["angleDeg"], Bh["taper"], Bh["softPx"], Bh["dry"])
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
    foot = foot_top(pg, Q, meta, broad)
    pl = peel(pg, Q, meta, side)
    sn = stains(pg, Q, meta, side, broad, foot)
    dl, streak = values(pg, Q, meta, side, broad, board, foot, sn)
    gr = grime(pg, Q, meta, side)
    rng = Q["dlRange"]
    hist = np.stack([pl, 0.5 + np.clip(dl, -rng, rng) / (2.0 * rng), sn, gr], axis=-1)
    hist = FL.dilate(np.where(pg.cov[..., None], hist, 0), pg.cov, pad + 2)
    FL.write(os.path.join(out, "hist-p.png"), hist)
    h2 = np.stack([streak, np.zeros(pg.shape), np.zeros(pg.shape)], axis=-1)
    FL.write(os.path.join(out, "hist-p2.png"), FL.dilate(np.where(pg.cov[..., None], h2, 0), pg.cov, pad + 2))
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
        "edgeAmp": E["amp"], "strokeFade": E["fadeLod"], "brushFade": Q["brush"]["fadeLod"], "brushFar": Q["brush"]["far"],
        "dragL": Q["drag"]["L"], "dragScale": Q["drag"]["scale"], "dlRange": Q["dlRange"], "rimL": E["rimL"],
        "rimW": E["rimW"], "rimFar": E["rimFar"], "rimBreak": E["rimBreak"], "bareShift": E["bareShift"],
        "washL": max(Q["wash"][n]["L"] for n in ("leak", "dry", "cap")),
        "aoStrength": Q["aoStrength"], "lapDark": L["occlusion"], "lapCore": L["occCoreMm"] / 1000.0,
        "lapReach": L["occReachMm"] / 1000.0, "lapGrimeL": L["grimeL"], "lapGrimeReach": L["reach"],
        "lapGrimeBreak": L["break"], "lapPage": sh["lapPageMm"] / 1000.0,
    }
    json.dump(digest, open(os.path.join(out, "paint.json"), "w"), indent=1)
    painted = pg.m["cladding"] | pg.m["trims"]
    share = lambda m: float((m & pg.cov).sum()) / max(1, int((painted & pg.cov).sum()))  # noqa: E731
    print(f"[paint] side {side:+.0f}; boarding {which}; peeled {share(painted & (pl > 0.5)):.3f} of the paint; "
          f"stained {share(sn > 0.5):.3f}; dL {np.percentile(dl[pg.cov], [1, 5, 50, 95]).round(1)}, "
          f"beyond {rng}: {float((np.abs(dl[pg.cov]) > rng).mean()):.4f}; wrote {out}")


if __name__ == "__main__":
    main()
