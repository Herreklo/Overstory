"""Way P's page: 107's corner painted as a painter would (finish.json `painted`).

    Blender -b --factory-startup -P blender/parts/finish/paint.py -- --gen <corner.py's out> --cache cache/finish

Writes into <cache>/out:
  hist-p.png        1,024 square, 8 bits, linear: R the peel's field and B the stain's, each shape's edge at 0.5 and
                    ramped over its `soft` either side, the shader's edge anti-aliased to the pixel; G a value shift,
                    0.5 + dL*/(2 dlRange) (the wall's tone course by course, the darks at every junction, the ply's
                    figure and runs, the battens' grain, the nails' heads, the plinth's blocks); A the lap grime's
                    strength
  hist-p2.png       1,024 square: R the tongue's wash, 0 to 1 of `tongue.washL` (the paint takes it whole, the dry
                    bare fibre only `bareWash` of it); G the laps kept far, where the rest collapse into the wall's
                    plane; B where a torn edge keeps its lip of paint film
  paint.json        the Unity scene's digest of way P (LT1Finish.cs), with its own overcast, and the colour still's
                    tints (way Pc: the same values, hue laid on them)

Three unequal planes carry the light (the wall's one gradient in G, the window dark, the sun's shadow); one failed-paint
shape carries the water, board by board: its wash soft and darker than the paint, its peel bare silvered fibre darker
still, a few slivers creeping up from the drip edges where the water lingers longest. Every shape is placed by a fact:
the surround's leaking side, the sill and its horns, the head, the courses and their butt joints, the battens and their
nails; its strength by the house's neglect and the years since its upkeep stopped (`wear`). No shape claims a dated
event (UK4): a wash says water runs here, never when.
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


def tint(L, C, h):
    """A colour, chroma C at hue h (CIE LCh, degrees) read at L*, as linear sRGB of luminance 1: a hue laid on a value
    without moving it."""
    a, b = C * math.cos(math.radians(h)), C * math.sin(math.radians(h))
    fy = (L + 16.0) / 116.0
    inv = lambda t: t ** 3 if t ** 3 > 216.0 / 24389.0 else (116.0 * t - 16.0) / 903.3  # noqa: E731
    X, Y, Z = 0.95047 * inv(fy + a / 500.0), inv(fy), 1.08883 * inv(fy - b / 200.0)
    rgb = [max(0.0, 3.2404542 * X - 1.5371385 * Y - 0.4985314 * Z),
           max(0.0, -0.9692660 * X + 1.8760108 * Y + 0.0415560 * Z),
           max(0.0, 0.0556434 * X - 0.2040259 * Y + 1.0572252 * Z)]
    y = 0.2126 * rgb[0] + 0.7152 * rgb[1] + 0.0722 * rgb[2]
    return [round(c / y, 5) for c in rgb]


def colours(P, Q, mats):
    """The colour still's tints (`painted.colour`): each material's paint, bare fibre, under layer and stain at their
    clay values, the wash at the paint's less the darkest wash, and each light's sun, sky, horizon and ground, the
    plain sky behind and the ground's albedo. A colour a material does not name is its paint's at that value; with no
    paint named, white."""
    C = Q["colour"]
    out = {"mats": [], "lights": []}
    for k, v in mats.items():
        c = C["mats"].get(k, {})
        L = v["L"]
        t = lambda part, at: tint(at, *c.get(part, c["paint"])) if "paint" in c or part in c else [1.0, 1.0, 1.0]  # noqa: E731
        out["mats"].append({"name": k, "tint": t("paint", L), "bareTint": t("bare", v.get("bareL", L)),
                            "underTint": t("under", v.get("underL", L)), "stainTint": t("stain", L - v.get("stainDL", 0.0))})
    out["washTint"] = tint(Q["materials"]["cladding"]["L"] - Q["tongue"]["washL"], *C["wash"])
    for name, c in C["light"].items():
        out["lights"].append({"light": name, **{k: tint(c["atL"], *c[k]) for k in ("sun", "sky", "equator", "ground")},
                              "background": tint(c["background"][2], *c["background"][:2]),
                              "floor": tint(P["ground"]["L"], *c["floor"])})
    return out


def wave(pg, k, cell, t=None):
    """A seeded low wave, -1..1, of `cell` metres along the wall (or along `t`): an edge drawn freehand."""
    t = pg.along if t is None else t
    return 2.0 * FL.noise2(t / cell, np.zeros(pg.shape), k) - 1.0


def rag(pg, k, cell, t=None):
    """Smooth seeded noise, about -1..1, of two octaves `cell` metres and finer along the wall (or along `t`): a torn
    edge with no steps."""
    return (wave(pg, k, cell, t) + 0.5 * wave(pg, HS.h(k, 2), cell / 2.3, t)) / 1.5


def wear(meta, F):
    """How far the house has gone without upkeep, 1 at the house the values were judged on (`F`): its neglect (per
    mille, the engine's) and the years since its upkeep stopped, `lead` years before it was boarded, eased by `power`."""
    years = max(meta["year"] - meta["neglectSince"], 0) + F["lead"]
    return (meta["neglect"] / F["neglect"] * years / (F["years"] + F["lead"])) ** F["power"]


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
        broad = np.maximum(broad, flow * MK.gauss(pg.along - x, Q["wet"]["splashWidth"]))
    return np.where(pg.street, broad, splash)


def junction(d, base, to, reach):
    """A junction's dark, as a shift: the value `base` drawn down to `to` at the junction, easing back over `reach`;
    nothing on its far side, and nothing where the value is darker already."""
    w = np.where(d >= -0.002, 1.0 - FL.smoothstep(0.0, reach, d), 0.0)
    return w * np.maximum(base - to, 0.0)


def peel(pg, Q, meta, side):
    """The paint lost outside the tongue: the casing's leaking leg at its foot on the sill, where the surround's joint
    feeds the tongue, and the ledges' tops, where water stands. The bare wood shows, dry."""
    R = Q["peel"]
    f = meta["features"]
    trims = pg.m["trims"]
    out = np.zeros(pg.shape)
    W = R["wobble"]
    # the casing's leg on the leaking side, at its foot on the sill
    cx0, cx1, cz0_, _ = f["casing"]
    ax0, ax1 = f["sheets"][0], f["sheets"][1]
    leg = (cx0 - 0.01, ax0) if side < 0 else (ax1, cx1 + 0.01)
    on = trims & pg.vertical & pg.street & (pg.along > leg[0]) & (pg.along < leg[1]) & (pg.z >= cz0_ - 0.005)
    edge = cz0_ + R["casing"]["reach"] * (1.0 - W["share"] * 0.5 * (1.0 + wave(pg, key(meta, "p-casing"), W["cell"], pg.z)))
    out = np.maximum(out, np.where(on, field(edge - pg.z, R["soft"]), 0.0))
    # the ledges' tops stand wet: bare but at their ends, where the casing and the corner keep them; a top cut by the
    # sample's edge runs on
    tops = trims & pg.up
    a0p, a1p = pg.per_piece(pg.along, "min"), pg.per_piece(pg.along, "max")
    lo_cut = np.where(pg.street, 0.0, -meta["sample"][1])
    hi_cut = np.where(pg.street, meta["sample"][0], 0.0)
    ins = R["tops"]["inset"] * (1.0 + 0.5 * wave(pg, key(meta, "p-tops"), W["cell"]))
    d0 = np.where(a0p <= lo_cut + 0.01, np.inf, pg.along - a0p - ins)
    d1 = np.where(a1p >= hi_cut - 0.01, np.inf, a1p - pg.along - ins)
    out = np.maximum(out, np.where(tops, field(np.minimum(np.minimum(d0, d1), 1.0), R["soft"]), 0.0))
    return np.where(pg.m["cladding"] | trims, out, 0.0)


def sliver(pg, S, k, xp, out, hl, h, b, t, joints):
    """One peel: a long thin sliver of bare fibre along the grain, from the board's drip edge (the butt, b) creeping up,
    tallest at xp and tapering out either side to ragged ends, longer on the side the water spreads to (`out`), its edge
    broken along the grain; where a
    butt joint lies under it the end grain drinks, so there it climbs the face, widest at the drip edge."""
    J = S["joint"]
    H = t - b
    rise = np.clip(pg.z - b, 0.0, None)
    d = pg.along - xp
    side = hl * np.where(out * d > 0.0, 1.0 + S["asym"], 1.0 - S["asym"])
    side = side * (1.0 + S["ends"]["amp"] * rag(pg, HS.h(k, "e"), S["ends"]["cell"], pg.z))
    u = np.clip(np.abs(d) / side, 0.0, 1.0)
    top = (min(h, H * S["maxShare"]) * (1.0 - u ** S["power"])
           + S["rag"]["amp"] * rag(pg, HS.h(k, "t"), S["rag"]["cell"]) * (1.0 - u))
    G = S["grain"]
    sd = np.where(u < 1.0, top - rise, -np.abs(d) + side)
    sd = sd + G["amp"] * (2.0 * FL.noise2(pg.along / G["cell"][0], pg.z / G["cell"][1], HS.h(k, "g")) - 1.0)
    for xj in joints:
        jw = J["width"] * (1.0 + J["foot"] * (1.0 - rise / H)) + S["ends"]["amp"] * 0.1 * rag(pg, HS.h(k, "j", xj), S["ends"]["cell"], pg.z)
        sd = np.maximum(sd, np.minimum(jw - np.abs(pg.along - xj), H * J["height"] - rise))
    return field(sd, S["soft"])


def tongue(pg, Q, meta, side, wr):
    """The one failed-paint shape, following the water: off each of the sill's ends to the plinth (the leaking end's the
    whole way, the dry end's fading) and down beside the casing from the head's leaking end to the sill. On each board
    its wash spreads toward the drip edge, where the water lingers, and the board below takes it narrower again; each
    board's share is its own, so no mark crosses a lap. Its peel is a few slivers, one large and some small, on the
    boards where the water stays longest: the wettest, worse at a butt joint and low down, where splash keeps it wet.
    Its strength and size follow the house's wear `wr`. Returns the peel's field and the wash's strength, L*."""
    T = Q["tongue"]
    S = T["slivers"]
    f, h = meta["features"], meta["heights"]
    clad = pg.m["cladding"] & pg.vertical & pg.street
    drip = pg.m["trims"] & pg.vertical & pg.street & (pg.z < h["drip"][1] + 0.003)
    (leak, lo), (dry, do) = horns(meta, side)
    z_sill = f["sill"][2]
    cx = f["casing"][0] if side < 0 else f["casing"][1]
    c = meta["courses"]
    starts = {"leak": (leak, lo, z_sill, h["drip"][0]), "dry": (dry, do, z_sill, h["drip"][0]),
              "cap": (cx, lo, h["head"], f["casing"][2])}
    joints = [(x, b) for face, x, b, _ in f["joints"] if face == "street"]
    wash = np.zeros(pg.shape)
    cands = []
    for name, R in T["runs"].items():
        x0, out, z0, z1 = starts[name]
        length = R["length"] * wr
        faces = [(max(c[i], z1), min(c[i + 1], z0), clad) for i in range(len(c) - 2, -1, -1)
                 if c[i] < z0 - 1e-6 and c[i + 1] > z1 + 1e-6]
        if z1 < h["drip"][1]:
            faces.append((h["drip"][0], h["drip"][1], drip))
        wb_up = None
        for j, (b, t, on) in enumerate(faces):
            if length and z0 - t >= length:
                break
            k = key(meta, "p-tongue", name, j)
            u = lambda *p: 2.0 * HS.unit(HS.h(k, *p)) - 1.0  # noqa: E731
            D = z0 - b
            wb = min(R["w0"] + R["spread"] * D ** R["spreadPower"], R["wMax"]) * wr * (1.0 + R["jitter"] * u("w"))
            wt = R["w0"] * wr if wb_up is None else R["take"] * wb_up
            cc = x0 + out * (R["inset"] + R["lean"] * D) + R["wander"] * wb * u("c")
            face = on & (pg.z >= b) & (pg.z < t)
            s = np.clip((t - pg.z) / (t - b), 0.0, 1.0)
            w = wt + (wb - wt) * s ** R["shape"]
            side_w = w * (1.0 + R["asym"] * np.sign(out * (pg.along - cc)))
            across = 1.0 - FL.smoothstep(R["core"], 1.0, np.abs(pg.along - cc) / side_w)
            fade = np.clip(1.0 - (z0 - pg.z) / length, 0.0, 1.0) if length else 1.0
            a = R["L"] * wr * fade * (1.0 + R["jitter"] * u("a")) * (R["edge"] + (1.0 - R["edge"]) * s)
            wash = np.maximum(wash, np.where(face, a * across, 0.0))
            # how long the water stays on this board's drip edge: the run's strength there, more at a butt joint
            # under the run and low down
            js = [x for x, jb in joints if abs(jb - b) < 1e-3 and abs(x - cc) < wb + S["joint"]["reach"]]
            stay = R["L"] * (1.0 - (z0 - b) / length if length else 1.0) * (1.0 + S["jitter"] * u("stay"))
            stay *= (1.0 + S["joint"]["bonus"] * bool(js)) * (1.0 + S["low"] * (1.0 - (b - h["drip"][0]) / (z_sill - h["drip"][0])))
            cands.append((stay, name, j, b, t, face, cc, out, wb, js, k))
            wb_up = wb
    # the slivers, largest on the wettest board, one to a course
    peel_ = np.zeros(pg.shape)
    used = set()
    cands.sort(key=lambda e: -e[0])
    n = 0
    for stay, name, j, b, t, face, cc, out, wb, js, k in cands:
        if n >= len(S["sizes"]) or round(b, 4) in used:
            continue
        used.add(round(b, 4))
        length, height = S["sizes"][n]
        u = lambda *p: 2.0 * HS.unit(HS.h(k, *p)) - 1.0  # noqa: E731
        xp = cc + S["offset"] * wb * u("x")
        peel_ = np.maximum(peel_, np.where(face, sliver(pg, S, k, xp, out, 0.5 * length * wr, height * wr, b, t, js), 0.0))
        print(f"[paint] sliver {n}: {name} board {j} at {b:.3f}, x {xp:.3f}, {length * wr:.2f} by {height * wr:.3f} m"
              f"{', over a butt joint' if js else ''}")
        n += 1
    return peel_, wash


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


def stains(pg, Q, meta, side):
    """The stain field, shapes with a found edge: rust under some of the battens' nails. The ply's damp and the
    plinth's are soft, in values()."""
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


def wall_low(pg, Q, meta, clad, z=None):
    """How low on the wall each point (or height `z` above it) is, 0 under the eave to 1 at the drip board, eased by
    the gradient's power; and the wall's top above each point."""
    top = edges(pg, clad)
    zf = meta["heights"]["drip"][1]
    t = np.clip(((pg.z if z is None else z) - zf) / np.maximum(top - zf, 0.1), 0.0, 1.0)
    return (1.0 - t) ** Q["wall"]["power"], top


def open_up(a, pg, r):
    """A page opened up the wall (its least then its most over r pixels either side): lines thinner than 2r go, broad
    shapes stay."""
    ax = 0 if np.nanmean(np.abs(np.diff(pg.z, axis=0))) > np.nanmean(np.abs(np.diff(pg.z, axis=1))) else 1
    lo = a.copy()
    for k in range(1, r + 1):
        lo = np.minimum(lo, np.minimum(np.roll(a, k, ax), np.roll(a, -k, ax)))
    hi = lo.copy()
    for k in range(1, r + 1):
        hi = np.maximum(hi, np.maximum(np.roll(lo, k, ax), np.roll(lo, -k, ax)))
    return hi


def course(pg, meta):
    """Each point's course: its index up the wall and its middle's height (the drip board's below the first)."""
    c = np.array(meta["courses"])
    i = np.clip(np.searchsorted(c, pg.z, side="right") - 1, 0, len(c) - 2)
    return i, 0.5 * (c[i] + c[i + 1])


def values(pg, Q, meta, side, board, sn, wr, broad):
    """The value shifts, dL*: broad washes first (the wall's one gradient, light under the eave's soft band and
    darkening steadily to its foot, the same round the corner, so nothing runs at one height, each course taking its
    own tone of it; a soft wash widening under the sill; the boarding's damp, run down the ply from its head), then the
    darks at every junction (under the eave, the sill and each batten, the boards onto the drip board, the plinth
    under it and onto the ground), then the small: contact shade, the ply's figure and its nails, the battens' grain
    and their nails' heads, the sheets' join, the plinth's blocks each its own, a few tiles lit."""
    f, h = meta["features"], meta["heights"]
    dl = np.zeros(pg.shape)
    clad = pg.m["cladding"] & pg.vertical
    wall = (pg.m["cladding"] | pg.m["trims"]) & pg.vertical
    stone = pg.m["stone"] & pg.vertical
    J = Q["junction"]
    # the wall's one gradient, light at its top and darkening steadily down to its foot; under the eave a soft
    # contact band, dark at the eave and fading down into the light
    low, top = wall_low(pg, Q, meta, clad)
    zf = h["drip"][1]
    Wl = Q["wall"]
    ci, zm = course(pg, meta)
    low_c, _ = wall_low(pg, Q, meta, clad, zm)
    jit = Wl["courseJitter"] * (2.0 * FL.unit(key(meta, "p-course"), ci + 100 * pg.street) - 1.0)
    dl += np.where(wall, Wl["topL"] + (Wl["footL"] * wr - Wl["topL"]) * low, 0.0)
    tone = np.where(clad, (Wl["footL"] * wr - Wl["topL"]) * Wl["course"] * (low_c - low) + jit, 0.0)
    dl += tone
    E = Q["eave"]
    d = top - pg.z
    dl -= np.where(wall & (d >= -0.002), E["L"] * (1.0 - FL.smoothstep(0.0, E["reach"], d)) ** E["power"], 0.0)
    Pl = Q["plinth"]
    dl -= np.where(stone, Pl["L"] * (1.0 - np.clip(pg.z / h["plinth"], 0.0, 1.0)), 0.0)
    dl += np.where(stone, Pl["blockL"] * (2.0 * FL.unit(key(meta, "p-block"), pg.piece) - 1.0), 0.0)
    dl -= np.where(stone & pg.up, Pl["capL"], 0.0)
    # the splash keeps the plinth's foot damp, higher under the drips that carry most: a soft dark, no found edge
    Wt = Q["wet"]
    wet = 1.0 - FL.smoothstep(-Wt["soft"], Wt["soft"], pg.z - Wt["top"] - Wt["splash"] * broad)
    dl -= np.where(stone, Wt["L"] * wet, 0.0)
    # under the sill, the water it sheds: a soft wash widening down
    sx0, sx1, z_sill, _ = f["sill"]
    Sw = Q["sillWash"]
    below = np.clip(z_sill - pg.z, 0.0, None)
    hw = (sx1 - sx0) / 2.0 + Sw["spread"] * below
    across = MK.soft_box(pg.along - (sx0 + sx1) / 2.0, -hw, hw, Sw["soft"])
    fall = (1.0 - np.clip(below / Sw["reach"], 0.0, 1.0)) ** 1.5
    dl -= np.where(clad & pg.street & (pg.z < z_sill), Sw["L"] * across * fall, 0.0)
    # the boarding holds water: darkest at its head and down its leaking side and at the sill, in one soft wash; a
    # band of its own above the lower batten
    Bw = board["wash"]
    sheet = pg.m["sheet"]
    ab0, ab1, zb0, zb1 = f["sheets"][:4]
    from_leak = np.where(side < 0, pg.along - ab0, ab1 - pg.along)
    # the head sheds its rain onto the ply: a soft damp band down from it, its lower edge a slow tide line
    Td = Bw["tide"]
    reach = Bw["head"] * (1.0 + Td["amp"] * wave(pg, key(meta, "p-ply-tide"), Td["cell"]))
    head = (1.0 - FL.smoothstep(0.0, reach, zb1 - pg.z)) * (1.0 - 0.5 * np.clip(from_leak / (ab1 - ab0), 0, 1))
    lk = 1.0 - FL.smoothstep(0.0, Bw["leak"], from_leak)
    bx0, bx1, zc, slope, bw = f["battens"][0]
    zl = zc + slope * (pg.along - (bx0 + bx1) / 2.0) + bw / 2.0
    lowness = np.clip(0.5 - np.sign(slope) * (pg.along - (bx0 + bx1) / 2.0) / max(bx1 - bx0, 1e-3), 0.0, 1.0)
    bat = np.where(pg.z > zl - 0.01, 1.0 - FL.smoothstep(0.0, Bw["batten"] * (1.0 + Bw["lowEnd"] * lowness), pg.z - zl), 0.0)
    sill = 1.0 - FL.smoothstep(0.0, Bw["sill"], pg.z - zb0)
    wash = 1.0 - (1.0 - head) * (1.0 - lk) * (1.0 - 0.6 * sill)
    dl -= np.where(sheet, np.maximum(Bw["L"] * wash, Bw["batL"] * bat), 0.0)
    # each sheet's cut edges drink: a narrow dark round it, deepest along its foot
    Pe = Q["ply"]["edge"]
    a0e, a1e = pg.per_piece(pg.along, "min"), pg.per_piece(pg.along, "max")
    z0e, z1e = pg.per_piece(pg.z, "min"), pg.per_piece(pg.z, "max")
    de = np.minimum(np.minimum(pg.along - a0e, a1e - pg.along), z1e - pg.z)
    dl -= np.where(sheet, Pe["L"] * np.maximum(1.0 - FL.smoothstep(0.0, Pe["reach"], de),
                                                Pe["foot"] * (1.0 - FL.smoothstep(0.0, Pe["footReach"], pg.z - z0e))), 0.0)
    # the small
    dl += np.where((pg.m["trims"] | pg.m["stone"] | pg.m["batten"]) & pg.up, Q["up"]["L"], 0.0)
    C = Q["contact"]
    occ = 1.0 - pg.ao
    shut = np.clip(1.0 - pg.cav, 0.0, 1.0)
    own = np.ones(pg.shape)
    for name, v in dict(Q["materials"], sheet=board["sheet"], batten=board["batten"]).items():
        own = np.where(pg.m[name], v.get("contact", 1.0), own)
    contact = lambda o, c: C["L"] * FL.smoothstep(C["ao"][0], C["ao"][1], o) + C["cavL"] * FL.smoothstep(C["cav"][0], C["cav"][1], c)  # noqa: E731
    dl -= own * contact(occ, shut)
    # each butt's own thin line of it goes with the course's tone, so far off it goes with the laps
    thin = contact(occ, shut) - contact(open_up(occ, pg, C["lapPx"]), open_up(shut, pg, C["lapPx"]))
    tone -= np.where(clad, np.clip(thin, 0.0, None), 0.0)
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
        # a batten bears on the casing alone: the boards behind its ends are clear of it and take no dark
        down(pg.m["trims"] & pg.vertical & ~b & under, dB, J["batten"]["to"], J["batten"]["reach"])
        down(sheet & under, dB, J["batten"]["sheetTo"], J["batten"]["reach"])
    down(sheet, zb1 - pg.z, J["head"]["to"], J["head"]["reach"])
    down(clad, pg.z - zf, J["drip"]["to"], J["drip"]["reach"])
    down(stone, h["drip"][0] - pg.z, J["plinth"]["to"], J["plinth"]["reach"])
    down(stone, pg.z, J["ground"]["to"], J["ground"]["reach"])
    # the battens, raw-sawn and weathered: long streaks along their grain, each its own; their sawn ends lifted to
    # their own grey, so no end reads as a dark peg
    Bt = Q["batten"]
    bat = pg.m["batten"]
    n_along = np.abs(np.where(pg.street, pg.n[..., 0], pg.n[..., 1]))
    dl += np.where(bat & pg.vertical & (n_along > 0.7), Bt["endL"], 0.0)
    for n, (bx0, bx1, zc, slope, w) in enumerate(f["battens"]):
        zl = pg.z - (zc + slope * (pg.along - (bx0 + bx1) / 2.0))
        on = bat & (np.abs(zl) <= w / 2.0 + 0.03) & (pg.along > bx0 - 0.05) & (pg.along < bx1 + 0.05)
        g = 2.0 * FL.noise2(pg.along / Bt["grain"][0], zl / Bt["grain"][1], key(meta, "p-batten-grain", n)) - 1.0
        dl += np.where(on, Bt["grainL"] * g, 0.0)
    # the ply: its face veneer's figure, long and wavy along each sheet's long side as the veneer runs, its oval
    # patches where the mill cut out knots, and the nails round each sheet's edge
    Pf = Q["ply"]
    kf = key(meta, "p-ply")
    wide = (pg.per_piece(pg.along, "max") - pg.per_piece(pg.along, "min")) >= (pg.per_piece(pg.z, "max") - pg.per_piece(pg.z, "min"))
    g_along, g_across = np.where(wide, pg.along, pg.z), np.where(wide, pg.z, pg.along)
    Fg = Pf["figure"]
    wav = Fg["wave"] * np.sin(g_along / Fg["cell"][1] * 2.0 * np.pi + 6.0 * FL.noise2(g_along / Fg["cell"][1], g_across / Fg["cell"][0], HS.h(kf, "w")))
    fig = 2.0 * FL.noise2((g_across + wav) / Fg["cell"][0], g_along / Fg["cell"][1], kf) - 1.0
    dl += np.where(sheet, Fg["L"] * fig, 0.0)
    Pp = Pf["patches"]
    for v in meta["pieces"]:
        if v["mat"] != "sheet":
            continue
        on = (pg.piece == v["i"]) & pg.cov
        if not on.any():
            continue
        pa0, pa1, pz0, pz1 = pg.along[on].min(), pg.along[on].max(), pg.z[on].min(), pg.z[on].max()
        horiz = (pa1 - pa0) >= (pz1 - pz0)
        for n in range(Pp["each"]):
            kp = HS.h(kf, "patch", v["i"], n)
            cxp = pa0 + Pp["inset"] + (pa1 - pa0 - 2 * Pp["inset"]) * HS.unit(HS.h(kp, "x"))
            czp = pz0 + Pp["inset"] + (pz1 - pz0 - 2 * Pp["inset"]) * HS.unit(HS.h(kp, "z"))
            pu, pv = (pg.along - cxp, pg.z - czp) if horiz else (pg.z - czp, pg.along - cxp)
            ln, wd = Pp["size"]
            sdp = wd / 2.0 * (1.0 - (np.clip(pu / (ln / 2.0), -1.0, 1.0)) ** 2) - np.abs(pv) - np.where(np.abs(pu) > ln / 2.0, 1.0, 0.0)
            dl += np.where(on, Pp["L"] * FL.smoothstep(-0.0015, 0.0015, sdp), 0.0)
    a0p, a1p = pg.per_piece(pg.along, "min"), pg.per_piece(pg.along, "max")
    z0p, z1p = pg.per_piece(pg.z, "min"), pg.per_piece(pg.z, "max")
    Nl = Pf["nails"]
    ins, gap = Nl["insetMm"] / 1000.0, Nl["spacing"]
    near_x = np.minimum(pg.along - a0p, a1p - pg.along)
    near_z = np.minimum(pg.z - z0p, z1p - pg.z)
    # on the line `ins` in from each edge, every `gap` along it
    dx = np.abs(near_x - ins)
    dz = np.abs(near_z - ins)
    ox = np.abs(((pg.z - z0p - ins) / gap + 0.5) % 1.0 - 0.5) * gap
    oz = np.abs(((pg.along - a0p - ins) / gap + 0.5) % 1.0 - 0.5) * gap
    r = np.minimum(np.hypot(dx, ox), np.hypot(dz, oz))
    dl += np.where(sheet, Nl["L"] * FL.smoothstep(Nl["headMm"] / 1000.0, 0.4 * Nl["headMm"] / 1000.0, r), 0.0)
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
    return dl, tone


def grime(pg, Q, meta, side):
    """The lap grime's strength on the boards: everywhere some, more down the wall's gradient and on the courses the
    sill drips on."""
    L = Q["lap"]
    f = meta["features"]
    sx0, sx1, z_sill, _ = f["sill"]
    foot, _ = wall_low(pg, Q, meta, pg.m["cladding"] & pg.vertical)
    sill = MK.soft_box(pg.along, sx0 - 0.1, sx1 + 0.1, L["sillSoft"]) * MK.soft_box(pg.z, z_sill - 0.35, z_sill, L["sillSoft"]) * pg.street
    a = L["base"] + L["foot"] * foot + L["sill"] * sill
    return np.where(pg.m["cladding"] & pg.vertical, np.clip(a, 0.0, 1.0), 0.0)


def lap_keep(pg, Q, meta):
    """The laps kept far, where the rest collapse into the wall's plane, so a wall reads as two or three broad strokes
    from the street: on each wall the butt nearest the drip board's top, and on the wall with the opening those
    nearest its sill and its head; on a wall with none, those nearest each `plain` share of its height. 1 down a kept
    butt's reach, else 0."""
    K = Q["lap"]["far"]
    h, f = meta["heights"], meta["features"]
    c = np.array(meta["courses"])
    clad = pg.m["cladding"] & pg.vertical
    zf = h["drip"][1]
    out = np.zeros(pg.shape)
    for face, opening in ((pg.street, True), (~pg.street, False)):
        levels = [zf] + ([f["sill"][2], h["head"]] if opening else [zf + s * (h["top"] - zf) for s in K["plain"]])
        for z in levels:
            b = c[np.argmin(np.abs(c - z))]
            out = np.where(clad & face & (pg.z <= b + 0.01) & (pg.z > b - K["reach"] - 0.02), 1.0, out)
    return out


def lip_pieces(pg, Q, meta):
    """Where a torn edge keeps its lip of lifted paint film: in pieces along it, about `cell` long, `share` of it."""
    Lp = Q["lip"]
    n = FL.noise2(pg.along / Lp["cell"], pg.z / Lp["cell"], key(meta, "p-lip"))
    return FL.smoothstep(1.0 - Lp["share"] - 0.1, 1.0 - Lp["share"] + 0.1, n)


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

    wr = wear(meta, Q["wear"])
    Wl = Q["wall"]
    broad = broad_splash(pg, Q, meta, MK.drip_splash(pg, P, meta))
    pt, wash = tongue(pg, Q, meta, side, wr)
    pl = np.maximum(peel(pg, Q, meta, side), pt)
    sn = stains(pg, Q, meta, side)
    dl, tone = values(pg, Q, meta, side, board, sn, wr, broad)
    gr = grime(pg, Q, meta, side)
    rng = Q["dlRange"]
    hist = np.stack([pl, 0.5 + np.clip(dl - tone, -rng, rng) / (2.0 * rng), sn, gr], axis=-1)
    hist = FL.dilate(np.where(pg.cov[..., None], hist, 0), pg.cov, pad + 2)
    FL.write(os.path.join(out, "hist-p.png"), hist)
    h2 = np.stack([np.clip(wash / Q["tongue"]["washL"], 0.0, 1.0), lap_keep(pg, Q, meta), lip_pieces(pg, Q, meta),
                   0.5 + np.clip(tone, -Wl["toneRange"], Wl["toneRange"]) / (2.0 * Wl["toneRange"])], axis=-1)
    FL.write(os.path.join(out, "hist-p2.png"), FL.dilate(np.where(pg.cov[..., None], h2, 0), pg.cov, pad + 2))

    L, Lp = Q["lap"], Q["lip"]
    sh = P["marks"]["shade"]
    M = P["materials"]
    mats = dict(Q["materials"], sheet=board["sheet"], batten=board["batten"])
    digest = {
        "mats": [{"name": k, "painted": 1 if M[k]["painted"] else 0, "L": v["L"], "bareL": v.get("bareL", v["L"]),
                  "underL": v.get("underL", v["L"]), "stainDL": v.get("stainDL", 0.0), "smooth": v["smooth"],
                  "stainSmooth": v.get("stainSmooth", v["smooth"]), "flatUp": v.get("flatUp", 0.0),
                  "ao": v.get("ao", Q["aoStrength"]), "shadowLift": v.get("shadowLift", 0.0)}
                 for k, v in mats.items()],
        "lights": [dict(v, light=k) for k, v in Q["light"].items()],
        "dlRange": Q["dlRange"], "toneRange": Wl["toneRange"], "bareShift": Q["bareShift"],
        "washL": Q["tongue"]["washL"], "bareWash": Q["tongue"]["bareWash"],
        # the lip's width in the peel's field, whose `soft` metres are half of it
        "lipL": Lp["L"], "lipW": 0.5 * Lp["widthMm"] / 1000.0 / Q["tongue"]["slivers"]["soft"], "lipFace": Lp["face"],
        "aoStrength": Q["aoStrength"], "lapDark": L["occlusion"], "lapCore": L["occCoreMm"] / 1000.0,
        "lapReach": L["occReachMm"] / 1000.0, "lapGrimeL": L["grimeL"], "lapGrimeReach": L["reach"],
        "lapPage": sh["lapPageMm"] / 1000.0, "lapFar": L["far"]["mmPerPx"], "lapFarReach": L["far"]["reach"],
        "colour": colours(P, Q, mats),
    }
    json.dump(digest, open(os.path.join(out, "paint.json"), "w"), indent=1)
    painted = pg.m["cladding"] | pg.m["trims"]
    share = lambda m: float((m & pg.cov).sum()) / max(1, int((painted & pg.cov).sum()))  # noqa: E731
    print(f"[paint] side {side:+.0f}; wear {wr:.2f}; boarding {which}; peeled {share(painted & (pl > 0.5)):.3f} of the paint; "
          f"stained {share(sn > 0.5):.3f}; dL {np.percentile(dl[pg.cov], [1, 5, 50, 95]).round(1)}, "
          f"beyond {rng}: {float((np.abs(dl[pg.cov]) > rng).mean()):.4f}; wrote {out}")


if __name__ == "__main__":
    main()
