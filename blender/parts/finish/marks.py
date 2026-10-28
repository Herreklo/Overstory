"""The corner's finishing marks on its page (UV1), read from 107's facts and the bakes (bake.py).

    Blender -b --factory-startup -P blender/parts/finish/marks.py -- --gen <corner.py's out> --cache cache/finish

Writes into <cache>/out, each 1,024 square, 8 bits, linear:
  geo.png       R occlusion within 0.6 m, G cavity (0.5 flat, darker where the surface is closed in, lighter on a
                worn arris), B the signed distance to the nearest butt (0.5 + d / 2 lapPageMm; 1 off the
                cladding), for the street level's laps, A the arris (a chamfer face at near, its place at street)
  hist-b.png    way B's (when scans.py has run): R the scan's own lost share, B its scanned decals' water
  hist-a.png    the history ways A and C read: R where paint is lost (a share, met by the tileable's breakup in the
                shader), G dirt, B water (streaks), A a value shift, 0.5 + dL*/80: each board's own value, the
                boarding's stains, the nails' heads and rust
  street-normal.png  the street level's laps and pillows (bake.py), 8 bits

Every mark is seeded from 107's id and a purpose and reads a fact: the neglect amount scales loss and grime; paint is
lost in groups only where water or wear acts on it (the boards' lower edges, their ends, the lowest courses, under the
sill, the corner board's foot); the sill, the nails and the eave's drip line (no gutter: each pan
drips) place the water and the foot's splash. No mark claims a dated event (UK4): a streak says water runs here,
never when.
"""

import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import finishlib as FL  # noqa: E402
from finishlib import HS  # noqa: E402

MATS = ["cladding", "trims", "sheet", "batten", "stone", "tiles", "zinc"]


def args():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    return {argv[i].lstrip("-"): argv[i + 1] for i in range(0, len(argv) - 1, 2)}


class Page:
    """The bakes as arrays, and the per-texel facts every mark reads."""

    def __init__(self, cache, meta):
        rd = lambda n: FL.read(os.path.join(cache, f"{n}.exr"))  # noqa: E731
        rest, nrm, ident = rd("rest"), rd("normal"), rd("ident")
        self.cov = rest[..., 3] > 0.5
        self.p = rest[..., :3] - 2.0
        self.n = nrm[..., :3] * 2.0 - 1.0
        self.piece = np.rint(ident[..., 0]).astype(np.int64)
        self.mat = np.where(self.cov, np.rint(ident[..., 1]).astype(np.int64), -1)
        self.arris = ident[..., 2]
        self.ao = rd("ao")[..., 0]
        self.cav = rd("cavity")[..., 0]
        self.sky = rd("sky")[..., 0]
        self.street_n = rd("street-normal")
        x, y, z = self.p[..., 0], self.p[..., 1], self.p[..., 2]
        self.x, self.y, self.z = x, y, z
        # along a wall: the street wall runs +x from the corner, the gable's own x runs -y
        self.street = x > y
        self.along = np.where(self.street, x, -y)
        self.up = self.n[..., 2] > 0.55
        self.vertical = np.abs(self.n[..., 2]) < 0.5
        self.m = {k: self.mat == i for i, k in enumerate(MATS)}
        self.meta = meta
        self.shape = self.cov.shape

    def per_piece(self, values, reduce):
        """Each piece's min or max of `values` over its texels, spread back over them."""
        n = self.piece.max() + 1
        out = np.full(n, np.inf if reduce == "min" else -np.inf)
        idx, val = self.piece[self.cov], values[self.cov]
        (np.minimum if reduce == "min" else np.maximum).at(out, idx, val)
        return out[self.piece]


def key(meta, *parts):
    return HS.h(meta["world"], f"h{meta['house']}", "finish", *parts)


def gauss(d, w):
    return np.exp(-(d / w) ** 2)


def board_values(pg, P, meta):
    """Each board, trim, sheet, batten, stone and tile its own value: a piece's seed, claiming no history."""
    dl = np.zeros(pg.shape)
    for i, mat in enumerate(MATS):
        spread = P["marks"]["boardValueL"][mat]
        u = FL.unit(key(meta, "value", mat), pg.piece)
        dl = np.where(pg.mat == i, (u - 0.5) * spread, dl)
    return dl


def soft_box(t, lo, hi, soft):
    """1 inside [lo, hi], falling to 0 over `soft` outside it."""
    return FL.smoothstep(lo - soft, lo, t) * (1.0 - FL.smoothstep(hi, hi + soft, t))


def groups_on(pg, k, mask, along, z, n, length, height, strength, soft=0.03, snap=None):
    """`n` groups of lost paint on `mask`, each `length` along and `height` up (ranges the seed draws in), placed in
    the ranges `along` and `z` (pairs, or one value for a group's start); their edges ragged by a little noise. With
    `snap` (the courses) a group starts at the butt of the board it falls on, where the paint lifts first."""
    out = np.zeros(pg.shape)
    for i in range(n):
        u = lambda *p: HS.unit(HS.h(k, i, *p))  # noqa: E731
        ln = length[0] + (length[1] - length[0]) * u("len")
        ht = height[0] + (height[1] - height[0]) * u("ht")
        a = along[0] + (along[1] - along[0] - ln) * u("at") if isinstance(along, (list, tuple)) else along
        zz = z[0] + (z[1] - z[0]) * u("z") if isinstance(z, (list, tuple)) else z
        if snap is not None:
            zz = max([c for c in snap if c <= zz] or [zz])
        st = strength[0] + (strength[1] - strength[0]) * u("st")
        g = soft_box(pg.along, a, a + ln, soft) * soft_box(pg.z, zz, zz + ht, min(soft * 0.4, ht * 0.5))
        out = np.maximum(out, st * g)
    rag = FL.fbm3(pg.p, HS.h(k, "rag"), 0.05, 3)
    return np.where(mask, out * FL.smoothstep(0.25, 0.6, rag + 0.25 * out), 0.0)


def paint_loss(pg, P, meta, dl):
    """Paint is lost in groups of 10 to 30 cm, only where water or wear acts on it, with calm whole paint between:
    along the boards' lower edges (most low on the wall), at their ends, on the lowest courses, under the sill, at the
    corner board's foot and on the trims' tops. Each group's share meets the tileable's breakup in the shader, so its
    flakes thin out to its ragged edge."""
    L = P["marks"]["loss"]
    h, f = meta["heights"], meta["features"]
    clad, trims = pg.m["cladding"] & pg.vertical, pg.m["trims"]
    courses = meta["courses"]
    gain = L["gain"] * meta["neglect"] / 600.0
    exposure = np.clip(pg.sky / 0.45, 0.35, 1.25)
    loss = np.zeros(pg.shape)

    def add(g):
        nonlocal loss
        loss = np.maximum(loss, g)
    foot_top = L["footTop"]
    # the boards' lower edges: each board's butt band, groups more often low on the wall where splash reaches
    E = L["edges"]
    for i, (wall, a, b, zb) in enumerate(meta["features"]["butts"]):
        on = clad & (pg.street == (wall == "street"))
        rate = E["perM"] * (1.0 + E["lowBoost"] * (zb < foot_top))
        n = int(rate * (b - a) + HS.unit(HS.h(key(meta, "edge-n", i))))
        if b - a > 0.12 and n:
            add(groups_on(pg, key(meta, "edge", i), on, (a, b), zb, n, E["length"], E["height"], E["strength"]))
    # board ends: end grain drinks water where a board meets a joint, the corner board or the casing
    En = L["ends"]
    cw = f["cornerBoard"][0]
    cx0, cx1, cz0, cz1 = f["casing"]
    ends = [("street", cw + 0.013, +1, None), ("gable", -cw, -1, None), ("street", cx0, -1, (cz0, cz1)),
            ("street", cx1, +1, (cz0, cz1))] + [(w, j, s_, (z0, z1)) for (w, j, z0, z1) in f["joints"] for s_ in (-1, 1)]
    for ci in range(len(courses) - 1):
        zb, zt = courses[ci], courses[ci + 1]
        for ei, (wall, e, side, band) in enumerate(ends):
            if band and not (zt > band[0] and zb < band[1]):
                continue
            k = key(meta, "end", ci, ei)
            if HS.unit(HS.h(k, "p")) > En["chance"] * (1.0 + En["lowBoost"] * (zb < foot_top)):
                continue
            ln = En["length"][0] + (En["length"][1] - En["length"][0]) * HS.unit(HS.h(k, "len"))
            span = (e, e + ln) if side > 0 else (e - ln, e)
            on = clad & (pg.street == (wall == "street"))
            add(groups_on(pg, k, on, span[0], zb, 1, (ln, ln), (0.3 * (zt - zb), zt - zb), En["strength"]))
    # the lowest courses, wetted by the splash under the eave's drip line
    F = L["foot"]
    for wall, lo_, hi_ in (("street", 0.0, meta["sample"][0]), ("gable", -meta["sample"][1], 0.0)):
        on = clad & (pg.street == (wall == "street"))
        n = int(F["perM"] * (hi_ - lo_))
        add(groups_on(pg, key(meta, "foot", wall), on, (lo_, hi_), (h["drip"][1], foot_top), n, F["length"],
                      F["height"], F["strength"], snap=courses))
    # under the sill: its drip wets the course below it
    sx0, sx1, z_sill, _ = f["sill"]
    U = L["underSill"]
    add(groups_on(pg, key(meta, "under-sill"), clad & pg.street, (sx0, sx1), (z_sill - U["reach"], z_sill - 0.04),
                  U["count"], U["length"], U["height"], U["strength"], snap=courses))
    # the corner board's foot, on both its faces
    C = L["cornerFoot"]
    corner = trims & pg.vertical & (np.abs(pg.along) < cw + 0.05) & (pg.z < h["top"] - 0.1)
    for wall in ("street", "gable"):
        on = corner & (pg.street == (wall == "street"))
        lo_ = -0.05 if wall == "street" else -cw - 0.05
        add(groups_on(pg, key(meta, "corner-foot", wall), on, lo_, h["drip"][1] - 0.02, 1, (cw + 0.1, cw + 0.1),
                      C["height"], C["strength"]))
    # the trims' tops: sun and standing water on the sill's and the cap's upper faces
    T = L["tops"]
    tops = trims & pg.up
    add(groups_on(pg, key(meta, "tops"), tops, (sx0, sx1 + 0.3), (h["open"][0] - 0.06, h["head"] + 0.12), T["count"],
                  T["length"], (0.3, 0.3), T["strength"]))
    # worn arrises, lifted in short runs along the edge
    arris = np.maximum(pg.arris, FL.blur(pg.arris, 1, pg.cov) * 1.5).clip(0, 1)
    runs = FL.smoothstep(0.55, 0.75, FL.fbm3(pg.p, key(meta, "arris-runs"), 0.07, 2))
    add(L["arris"] * arris * runs)
    painted = pg.m["cladding"] | trims
    return np.where(painted, np.clip(gain * loss * exposure, 0, 1), 0.0)


def lap_line(pg, P, meta):
    """For the street level, whose wall is a plane: each cladding texel's signed distance to the nearest butt,
    below the butt above positive, above its own butt negative, as 0.5 + d / (2 `lapPageMm`) (1 off the cladding),
    so the shader draws the lap's band and its sun shadow as the near boards do from their corners. Signed, the field
    runs straight through each butt, so the shader can box-filter the band over a pixel on either side of it."""
    sh = P["marks"]["shade"]
    page = sh["lapPageMm"] / 1000.0
    courses = np.asarray(meta["courses"])
    i = np.searchsorted(courses, pg.z, side="right")
    up = np.where(i < len(courses), courses[np.clip(i, 0, len(courses) - 1)], np.inf) - pg.z
    down = pg.z - np.where(i > 0, courses[np.clip(i - 1, 0, len(courses) - 1)], -np.inf)
    d = np.clip(0.5 + 0.5 * np.where(up <= down, up, -down) / page, 0.0, 0.98)
    return np.where(pg.m["cladding"] & pg.vertical, d, 1.0)


def drip_splash(pg, P, meta):
    """With no gutter, each pan's water falls from the eave onto the ground in front of the wall and splashes back at
    its foot: strongest under each drip, by how much its pan carries; uneven along the wall. 0..1 along the street wall,
    0.25 on the gable, which takes the verge's run-off."""
    S = P["marks"]["splash"]
    k = key(meta, "splash-drips")
    out = np.zeros(pg.shape)
    for i, (x, _, flow) in enumerate(meta["features"]["drips"]):
        w = S["width"][0] + (S["width"][1] - S["width"][0]) * HS.unit(HS.h(k, i, "w"))
        out = np.maximum(out, flow * gauss(pg.along - x, w))
    return np.where(pg.street, out, S["gable"])


def dirt(pg, P, meta, splash):
    D = P["marks"]["dirt"]
    h = meta["heights"]
    z = pg.z
    grain = 0.55 + 0.45 * FL.fbm3(pg.p, key(meta, "splash"), 0.05, 3)
    reach = D["footTop"] * (0.55 + 0.45 * splash)
    foot = D["foot"] * np.clip(1.0 - z / np.maximum(reach, 0.05), 0, 1) ** 1.3 * (0.3 + 0.7 * splash) * grain
    sheltered = np.clip(1.0 - pg.sky / 0.42, 0, 1)
    eave = D["eave"] * sheltered * FL.smoothstep(h["top"] - D["eaveReach"], h["top"] - 0.05, z)
    up = D["up"] * pg.up * (0.5 + 0.5 * FL.fbm3(pg.p, key(meta, "up-dirt"), 0.06, 2))
    cav = D["cavity"] * np.clip((1.0 - pg.cav) * 1.4, 0, 1)
    grime = D["grime"] * (meta["neglect"] / 1000.0) * FL.fbm3(pg.p, key(meta, "grime"), D["cell"], 3)
    # water running down each board leaves its dirt along the butt it drips from, fading up the face
    courses = np.asarray(meta["courses"])
    i = np.searchsorted(courses, z, side="right")
    above = z - np.where(i > 0, courses[np.clip(i - 1, 0, len(courses) - 1)], -np.inf)
    butts = np.where(pg.m["cladding"] & pg.vertical, D["butts"] * np.clip(1.0 - above / (D["buttsMm"] / 1000.0), 0, 1) ** 2, 0.0)
    return np.clip(foot + eave + up + cav + grime + butts, 0, 1)


def runnel(pg, k, along0, along1, z_top, n, width, length, strength, mask, ends=()):
    """Water leaving an edge at z_top between along0 and along1 runs down in `n` seeded runnels (plus one at each of
    `ends`), each fading with the distance it has run."""
    out = np.zeros(pg.shape)
    below = np.clip(z_top - pg.z, 0, None)
    starts = [(a, 1.0) for a in ends]
    for i in range(n):
        starts.append((along0 + (along1 - along0) * HS.unit(HS.h(k, i, "at")), 0.35 + 0.65 * HS.unit(HS.h(k, i, "a"))))
    for i, (a, amp) in enumerate(starts):
        w = width[0] + (width[1] - width[0]) * HS.unit(HS.h(k, i, "w"))
        ln = length[0] + (length[1] - length[0]) * HS.unit(HS.h(k, i, "len"))
        # a runnel wanders a little as it runs
        wander = (FL.noise2(below / 0.12, np.full(pg.shape, float(i)), HS.h(k, i, "wander")) - 0.5) * w * 1.5
        s = amp * strength * gauss(pg.along - a - wander, w) * np.exp(-below / ln)
        out = np.maximum(out, s)
    return np.where(mask & (pg.z <= z_top), out, 0.0)


def water(pg, P, meta, dl, splash):
    W = P["marks"]["water"]
    f = meta["features"]
    h = meta["heights"]
    out = np.zeros(pg.shape)
    wall = pg.street & pg.vertical & ~pg.m["tiles"]
    # under the sill: its front drips along its length, its horns most
    sx0, sx1, z_sill, proud = f["sill"]
    S = W["sill"]
    s = runnel(pg, key(meta, "sill"), sx0 + 0.03, sx1 - 0.03, z_sill, S["runnels"], S["width"], S["length"], 0.8,
               wall, ends=(sx0 + 0.012, sx1 - 0.012))
    wash = S["wash"] * ((pg.along > sx0) & (pg.along < sx1)) * np.exp(-np.clip(z_sill - pg.z, 0, None) / 0.22)
    out = np.maximum(out, np.where(wall & (pg.z <= z_sill), wash, 0) + s)
    # the eave's drip line: wind throws the most-laden pans' water back under the soffit, down the top courses
    E = W["eave"]
    k = key(meta, "eave")
    for i, (x, _, flow) in enumerate(f["drips"]):
        if flow < E["minFlow"] or not (0.05 < x < meta["sample"][0] - 0.05):
            continue
        r = runnel(pg, HS.h(k, i), x - 0.04, x + 0.04, h["top"], 1, E["width"], E["length"], E["strength"] * flow, wall)
        out = np.maximum(out, r)
    # the splash at the foot wets the plinth, the drip board and the lowest course
    sp = W["splash"]
    out = np.maximum(out, np.where(pg.vertical, sp["strength"] * splash * FL.smoothstep(sp["top"], 0.0, pg.z), 0.0))
    # the 1986 nails: an iron-black head, and rust run down the grain below it, on the batten and on what lies under
    N = W["nails"]
    k = key(meta, "nails")
    for i, (xn, zn) in enumerate(f["nails"]):
        ln = N["length"][0] + (N["length"][1] - N["length"][0]) * HS.unit(HS.h(k, i, "len"))
        below = np.clip(zn - pg.z, 0, None)
        near = pg.street & (pg.y < 0.0)
        head = gauss(np.hypot(pg.along - xn, pg.z - zn), N["headMm"] / 1000.0)
        w = N["widthMm"][0] / 1000.0 + (N["widthMm"][1] - N["widthMm"][0]) / 1000.0 * np.clip(below / ln, 0, 1)
        run = gauss(pg.along - xn, w / 2) * np.exp(-below / ln) * (pg.z <= zn)
        dl -= np.where(near, np.maximum(N["headL"] * head, N["rustL"] * run), 0.0)
    # the boarding's sheets: damp gathers low on the boarding and wicks in at each sheet's cut edges, leaving dark
    # blotched stains with a tide line at their edge; the middle, dry in the sun, bleaches lighter
    Sb = W["sheet"]
    sheet = pg.m["sheet"]
    z0, z1 = pg.per_piece(pg.z, "min"), pg.per_piece(pg.z, "max")
    a0, a1 = pg.per_piece(pg.along, "min"), pg.per_piece(pg.along, "max")
    edge = np.minimum(np.minimum(pg.z - z0, z1 - pg.z), np.minimum(pg.along - a0, a1 - pg.along))
    zb0, zb1 = pg.z[sheet].min(), pg.z[sheet].max()
    a_sheet = (pg.along[sheet].min(), pg.along[sheet].max())
    t = np.clip((pg.z - zb0) / max(zb1 - zb0, 1e-3), 0, 1)
    blot = FL.fbm3(pg.p, key(meta, "sheet-stain"), Sb["cell"], Sb["octaves"], Sb["gain"])
    reach = Sb["wickReach"] * (0.5 + blot)
    wet = Sb["blot"] * blot + Sb["bottom"] * (1 - t) ** 2 + Sb["wick"] * np.exp(-np.clip(edge, 0, None) / reach)
    # the head's drip falls behind the sheet's top edge and wicks down from it
    wet += Sb["head"] * np.exp(-np.clip(zb1 - pg.z, 0, None) / (Sb["headReach"] * (0.5 + blot)))
    # each batten holds water against the sheet on its top, which wicks up into it, most toward the batten's low
    # end where the water runs, and the more the lower it sits, since it holds what runs down the sheet above it;
    # and what spills runs down from its lower edge
    Bs = Sb["batten"]
    kb = key(meta, "sheet-batten")
    for bi, (bx0, bx1, zc, slope, w) in enumerate(f["battens"]):
        mid = (bx0 + bx1) / 2
        zt = zc + slope * (pg.along - mid) + w / 2
        low = np.clip(0.5 - np.sign(slope) * (pg.along - mid) / max(bx1 - bx0, 1e-3), 0, 1)
        catch = np.clip((zb1 - zc) / max(zb1 - zb0, 1e-3), 0, 1)
        held = Bs["above"] * catch * ((1 - Bs["low"]) + Bs["low"] * low) * np.exp(-(pg.z - zt) / (Bs["reach"] * (0.5 + blot)))
        wet += np.where(pg.z >= zt, held, 0.0)
        for ri in range(Bs["runs"]):
            a = a_sheet[0] + (a_sheet[1] - a_sheet[0]) * HS.unit(HS.h(kb, bi, ri, "at"))
            zr = zc + slope * (a - mid) - w / 2
            wet += runnel(pg, HS.h(kb, bi, ri), a, a, zr, 1, Bs["width"], Bs["length"], Bs["runWet"], sheet)
    # a stain is never one flat grey: darker and lighter within it, by the glue and the veneer's figure; and mould
    # speckles the sheet most where it stays damp
    mott = FL.smoothstep(0.3, 0.7, FL.fbm3(pg.p, key(meta, "sheet-mottle"), Sb["mottleCell"], 3))
    wetness = FL.smoothstep(Sb["wet"][0], Sb["wet"][1], wet) ** Sb["curve"]
    stain = Sb["stainL"] * wetness * (1.0 - Sb["mottle"] * mott)
    spk = FL.smoothstep(Sb["speckle"][0], Sb["speckle"][1], FL.fbm3(pg.p, key(meta, "sheet-speckle"), Sb["speckleCell"], 1))
    stain = stain + Sb["speckleL"] * spk * (0.3 + 0.7 * FL.smoothstep(Sb["dry"][0], Sb["wet"][1], wet))
    tide = Sb["tideL"] * np.exp(-((wet - Sb["wet"][0]) / Sb["tide"]) ** 2)
    bleach = Sb["bleachL"] * (1.0 - FL.smoothstep(Sb["dry"][0], Sb["dry"][1], wet))
    dl += np.where(sheet, bleach - stain - tide, 0.0)
    # the sheets' own nails, round each sheet's edges where 1986 fixed it to the casing: a dark head, a short rust run
    Nn = Sb["nails"]
    kn = key(meta, "sheet-nails")
    inset, every = Nn["inMm"] / 1000.0, Nn["everyMm"] / 1000.0
    for pid in np.unique(pg.piece[sheet]):
        m = sheet & (pg.piece == pid)
        sa0, sa1, sz0, sz1 = pg.along[m].min(), pg.along[m].max(), pg.z[m].min(), pg.z[m].max()
        spots = [(xa, zz) for xa in (sa0 + inset, sa1 - inset)
                 for zz in np.linspace(sz0 + inset, sz1 - inset, max(2, int(round((sz1 - sz0) / every)) + 1))]
        spots += [(xx, sz1 - inset) for xx in np.linspace(sa0 + inset, sa1 - inset, max(2, int(round((sa1 - sa0) / every)) + 1))[1:-1]]
        for ni, (xn, zn) in enumerate(spots):
            xn += (HS.unit(HS.h(kn, int(pid), ni, "x")) - 0.5) * 0.01
            zn += (HS.unit(HS.h(kn, int(pid), ni, "z")) - 0.5) * 0.02
            ln = Nn["length"][0] + (Nn["length"][1] - Nn["length"][0]) * HS.unit(HS.h(kn, int(pid), ni, "len"))
            below = np.clip(zn - pg.z, 0, None)
            head = gauss(np.hypot(pg.along - xn, pg.z - zn), Nn["headMm"] / 1000.0)
            wn = Nn["widthMm"][0] / 1000.0 + (Nn["widthMm"][1] - Nn["widthMm"][0]) / 1000.0 * np.clip(below / ln, 0, 1)
            run = gauss(pg.along - xn, wn / 2) * np.exp(-below / ln) * (pg.z <= zn)
            dl -= np.where(m, np.maximum(Nn["headL"] * head, Nn["rustL"] * run), 0.0)
    # the battens: raw sawn wood, darker where water hangs on their lower arris
    Bt = W["batten"]
    bat = pg.m["batten"]
    bz0 = pg.per_piece(pg.z, "min")
    dl -= np.where(bat, Bt["lowL"] * np.exp(-np.clip(pg.z - bz0, 0, None) / Bt["reach"]), 0.0)
    return np.clip(out, 0, 1)


def decal(img, u, v):
    """Bilinear sample of a decal's opacity at (u, v), v from its top edge down; nothing outside it."""
    h, w = img.shape
    x = u * (w - 1)
    y = (1.0 - v) * (h - 1)
    inside = (u >= 0) & (u <= 1) & (v >= 0) & (v <= 1)
    x0 = np.clip(np.floor(x).astype(np.int64), 0, w - 2)
    y0 = np.clip(np.floor(y).astype(np.int64), 0, h - 2)
    fx, fy = np.clip(x - x0, 0, 1), np.clip(y - y0, 0, 1)
    a = img[y0, x0] * (1 - fx) + img[y0, x0 + 1] * fx
    b = img[y0 + 1, x0] * (1 - fx) + img[y0 + 1, x0 + 1] * fx
    return np.where(inside, a * (1 - fy) + b * fy, 0.0)


def history_b(pg, P, meta, side):
    """Way B's page: the paint keeps the scan's own losses (its worst, down to a share, met by its own breakup),
    and water is scanned decals laid where A's runnels run: under the sill and below the nails.
    No foot dirt, grime or board values: no scan carries them."""
    D = P["scans"]["decals"]
    rd = lambda d: FL.read(os.path.join(FL.ROOT, "blender", "parts", "finish", "scans", d["dir"], d["file"]))[..., 0]  # noqa: E731
    water_img, rust_img = rd(D["water"]), rd(D["rust"])
    W = P["marks"]["water"]
    f, h = meta["features"], meta["heights"]
    wall = pg.street & pg.vertical & ~pg.m["tiles"]
    out = np.zeros(pg.shape)
    ww, wh = D["water"]["metres"]
    sx0, sx1, z_sill, _ = f["sill"]
    k = key(meta, "b", "sill")
    u0 = HS.unit(HS.h(k, "u")) * max(0.0, 1.0 - (sx1 - sx0) / ww)
    s = decal(water_img, u0 + (pg.along - sx0) / ww, (z_sill - pg.z) / wh)
    out = np.maximum(out, np.where(wall & (pg.along > sx0) & (pg.along < sx1), 0.8 * s, 0))
    rw, rh = D["rust"]["metres"]
    N = W["nails"]
    k = key(meta, "b", "nails")
    for i, (xn, zn) in enumerate(f["nails"]):
        sc = 0.6 + 0.8 * HS.unit(HS.h(k, i, "len"))
        near = pg.street & (pg.z <= zn + 0.004) & (pg.y < 0.0)
        r = decal(rust_img, 0.5 + (pg.along - xn) / (rw * sc), (zn - pg.z) / (rh * sc))
        out = np.maximum(out, np.where(near, N["strength"] * r, 0))
    # the scan's own losses, its worst first, down to the share photo 09's paint has lost
    S = P["scans"]
    loss = np.where(pg.m["cladding"], S["painted-board"]["lossShare"],
                    np.where(pg.m["trims"], S["trim-sheet"]["lossShare"], 0.0))
    return np.stack([loss, np.zeros(pg.shape), np.clip(out, 0, 1), np.full(pg.shape, 0.5)], axis=-1)


def main():
    a = args()
    gen, cache = os.path.abspath(a["gen"]), os.path.abspath(a["cache"])
    meta = json.load(open(os.path.join(gen, "corner.json")))
    P = json.load(open(os.path.join(FL.ROOT, "blender", "parts", "finish", "finish.json")))
    out = os.path.join(cache, "out")
    pg = Page(cache, meta)
    pad = meta["page"]["padPx"]

    dl = board_values(pg, P, meta)
    loss = paint_loss(pg, P, meta, dl)
    splash = drip_splash(pg, P, meta)
    dr = dirt(pg, P, meta, splash)
    wt = water(pg, P, meta, dl, splash)
    hist = np.stack([loss, dr, wt, 0.5 + np.clip(dl, -40, 40) / 80.0], axis=-1)
    hist = FL.dilate(np.where(pg.cov[..., None], hist, 0), pg.cov, pad + 2)
    FL.write(os.path.join(out, "hist-a.png"), hist)

    cav = np.clip((1.0 - pg.cav) * 1.3, 0, 1)
    geo = np.stack([pg.ao, 0.5 + 0.5 * (pg.arris * 0.6 - cav), lap_line(pg, P, meta), pg.arris], axis=-1)
    geo = FL.dilate(np.where(pg.cov[..., None], geo, 0), pg.cov, pad + 2)
    FL.write(os.path.join(out, "geo.png"), geo)

    side_path = os.path.join(out, "scans.json")
    if os.path.exists(side_path):
        hb = history_b(pg, P, meta, json.load(open(side_path)))
        FL.write(os.path.join(out, "hist-b.png"), FL.dilate(np.where(pg.cov[..., None], hb, 0), pg.cov, pad + 2))
        print(f"[marks] hist-b: water {hb[..., 2][pg.cov].mean():.3f}")

    sn = pg.street_n
    FL.write(os.path.join(out, "street-normal.png"), FL.dilate(sn[..., :3], sn[..., 3] > 0.5, pad + 2))
    share = lambda m: float((m & pg.cov).sum()) / max(1, int(pg.cov.sum()))  # noqa: E731
    painted = (pg.m["cladding"] | pg.m["trims"])
    print(f"[marks] loss {loss[painted].mean():.3f} mean, {share(painted & (loss > 0.5)):.3f} of the page over 0.5; "
          f"dirt {dr[pg.cov].mean():.3f}; water {wt[pg.cov].mean():.3f}; wrote {out}")


main()
