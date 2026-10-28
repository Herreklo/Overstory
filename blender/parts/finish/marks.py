"""The corner's finishing marks on its page (UV1), read from 107's facts and the bakes (bake.py).

    Blender -b --factory-startup -P blender/parts/finish/marks.py -- --gen <corner.py's out> --cache cache/finish

Writes into <cache>/out, each 1,024 square, 8 bits, linear:
  geo.png       R occlusion within 0.6 m, G cavity (0.5 flat, darker where the surface is closed in, lighter on a
                worn arris), B the sky's light, A the arris (a chamfer face at near, its place at street)
  hist-b.png    way B's (when scans.py has run): R the scan's own lost share, B its scanned decals' water
  hist-a.png    the history ways A and C read: R where paint is lost (a share, met by the tileable's breakup in the
                shader), G dirt, B water (streaks and stains), A each board's value, 0.5 + dL*/20
  street-normal.png  the street level's laps and pillows (bake.py), 8 bits

Every mark is seeded from 107's id and a purpose and reads a fact: the neglect amount scales loss and grime, the
house's sill, nails, gutter and shoe place the water, the wall's foot and eave place the dirt. No mark claims a
dated event (UK4): a streak says water runs here, never when.
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


def paint_loss(pg, P, meta, dl):
    L = P["marks"]["loss"]
    h = meta["heights"]
    f = meta["features"]
    painted = pg.m["cladding"] | pg.m["trims"]
    clad = pg.m["cladding"]
    z = pg.z
    # how far above its butt a texel sits on its board: paint fails first at the butt, where water leaves
    zb = pg.per_piece(z, "min")
    lap = clad * np.exp(-np.clip(z - zb, 0, None) / L["lapHeight"])
    # the wall's foot, wetted by splash
    foot = FL.smoothstep(L["footTop"], h["drip"][0] - 0.05, z)
    # board ends: end grain drinks water where a board meets a joint, the corner board or the casing
    cw, _, _, _ = f["cornerBoard"]
    step = 0.013
    ends_st = [cw + step, f["casing"][0], f["casing"][1]]
    ends_gb = [-cw]
    d_end = np.full(pg.shape, 9.0)
    in_window = (z > f["casing"][2] - 0.08) & (z < f["casing"][3])
    for e in ends_st:
        near_win = in_window if e in f["casing"][:2] else np.ones(pg.shape, bool)
        d_end = np.where(pg.street & near_win, np.minimum(d_end, np.abs(pg.along - e)), d_end)
    for e in ends_gb:
        d_end = np.where(~pg.street, np.minimum(d_end, np.abs(pg.along - e)), d_end)
    for wall, j, z0, z1 in f["joints"]:
        on = (pg.street == (wall == "street")) & (z >= z0) & (z < z1)
        d_end = np.where(on, np.minimum(d_end, np.abs(pg.along - j)), d_end)
    ends = clad * np.exp(-d_end / L["endReach"])
    # worn arrises, lifted toward the wood in runs along the edge
    arris = np.maximum(pg.arris, FL.blur(pg.arris, 1, pg.cov) * 1.5).clip(0, 1)
    wear_runs = FL.smoothstep(0.35, 0.65, FL.fbm3(pg.p, key(meta, "arris-runs"), 0.07, 2))
    up = pg.up.astype(float)
    pot = L["base"] + L["lap"] * lap + L["foot"] * foot + L["ends"] * ends + L["up"] * up
    pot = pot + L["arris"] * arris * (0.35 + 0.65 * wear_runs)
    # sheltered faces weather less: the sky they see scales the loss
    exposure = np.clip(pg.sky / 0.45, 0.35, 1.25)
    groups = FL.smoothstep(L["groups"][0], L["groups"][1], FL.fbm3(pg.p, key(meta, "loss-groups"), L["groupCell"], 3))
    neglect = meta["neglect"] / 1000.0
    loss = L["gain"] * neglect * pot * exposure * (L["groupFloor"] + (2 - L["groupFloor"]) * groups)
    return np.where(painted, np.clip(loss, 0, 1), 0.0)


def lap_line(pg, P, meta):
    """The dark line under each lap for the street level, whose wall is a plane: a cladding texel's occlusion from how
    far below the next course's butt it sits, averaged over the texel so the line survives at one texel wide."""
    sh = P["marks"]["shade"]
    r = sh["lapReachMm"] / 1000.0
    tau = 1.0 / meta["page"]["pxPerM"]
    courses = np.asarray(meta["courses"])
    z_next = courses[np.clip(np.searchsorted(courses, pg.z, side="right"), 0, len(courses) - 1)]
    d0 = np.clip(z_next - pg.z - tau / 2, 0, None)
    mean = r / tau * (np.exp(-d0 / r) - np.exp(-(d0 + tau) / r))
    return np.where(pg.m["cladding"] & pg.vertical, 1.0 - sh["lapDarkStreet"] * mean, 1.0)


def dirt(pg, P, meta):
    D = P["marks"]["dirt"]
    h = meta["heights"]
    z = pg.z
    splash = 0.55 + 0.45 * FL.fbm3(pg.p, key(meta, "splash"), 0.09, 3)
    foot = D["foot"] * FL.smoothstep(D["footTop"], 0.0, z) ** 1.3 * splash
    sheltered = np.clip(1.0 - pg.sky / 0.42, 0, 1)
    eave = D["eave"] * sheltered * FL.smoothstep(h["top"] - D["eaveReach"], h["top"] - 0.05, z)
    up = D["up"] * pg.up * (0.5 + 0.5 * FL.fbm3(pg.p, key(meta, "up-dirt"), 0.06, 2))
    cav = D["cavity"] * np.clip((1.0 - pg.cav) * 1.4, 0, 1)
    grime = D["grime"] * (meta["neglect"] / 1000.0) * FL.fbm3(pg.p, key(meta, "grime"), D["cell"], 3)
    return np.clip(foot + eave + up + cav + grime, 0, 1)


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


def water(pg, P, meta, dl):
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
    # the 1986 nails rust: a short streak below each, on the batten and down what lies under it
    N = W["nails"]
    k = key(meta, "nails")
    for i, (xn, zn) in enumerate(f["nails"]):
        ln = N["length"][0] + (N["length"][1] - N["length"][0]) * HS.unit(HS.h(k, i, "len"))
        below = np.clip(zn - pg.z, 0, None)
        near = pg.street & (pg.z <= zn + 0.004) & (pg.y < 0.0)
        r = N["strength"] * gauss(pg.along - xn, N["width"] * (1 + below / 0.1)) * np.exp(-below / ln)
        out = np.maximum(out, np.where(near, r, 0))
    # a neglected gutter fills and overflows: runs down the fascia and, fainter, down the wall under the soffit
    O = W["overflow"]
    fascia = pg.m["trims"] & (pg.z > h["top"] - 0.05) & (pg.n[..., 1] < -0.5)
    under = wall & (pg.z < h["top"])
    neglect = meta["neglect"] / 1000.0
    o = runnel(pg, key(meta, "overflow"), 0.3, meta["sample"][0] - 0.15, h["top"] + 0.16, O["count"], O["width"],
               O["length"], O["strength"] * neglect / 0.6, fascia | under)
    out = np.maximum(out, np.where(fascia, o, 0.55 * o))
    # the downpipe's shoe throws water back at the plinth and the wall's foot
    px, _, _, z_shoe, _ = f["pipe"]
    Sh = W["shoe"]
    d = np.hypot(pg.along - px, (pg.z - 0.05) * 0.8)
    out = np.maximum(out, np.where(pg.street & pg.vertical & (pg.z < 0.8), Sh["strength"] * gauss(d, Sh["radius"]), 0))
    # the boarding's sheets: water wicks up from their foot and in at their head, leaving blotches and tide lines
    Sb = W["sheet"]
    sheet = pg.m["sheet"]
    # damp gathers low on the boarding as a whole, and each sheet wicks it in at its cut edges
    z0, z1 = pg.per_piece(pg.z, "min"), pg.per_piece(pg.z, "max")
    a0, a1 = pg.per_piece(pg.along, "min"), pg.per_piece(pg.along, "max")
    edge = np.minimum(np.minimum(pg.z - z0, z1 - pg.z), np.minimum(pg.along - a0, a1 - pg.along))
    zb0, zb1 = pg.z[sheet].min(), pg.z[sheet].max()
    t = np.clip((pg.z - zb0) / max(zb1 - zb0, 1e-3), 0, 1)
    blot = FL.fbm3(pg.p, key(meta, "sheet-stain"), Sb["cell"], Sb["octaves"], Sb["gain"])
    wet = blot * 0.75 + Sb["bottom"] * (1 - t) ** 2 + Sb["wick"] * np.exp(-np.clip(edge, 0, None) / Sb["wickReach"])
    # a stain is one soft wet area with a single tide line at its edge, never contours all through it
    stain = FL.smoothstep(0.5, 0.5 + Sb["edge"], wet) * Sb["stain"]
    tide = np.exp(-((wet - 0.5) / Sb["tide"]) ** 2) * Sb["tideStrength"]
    out = np.where(sheet, np.maximum(out, np.maximum(stain, tide)), out)
    bleach = Sb["bleachL"] * FL.smoothstep(0.42, 0.25, FL.fbm3(pg.p, key(meta, "sheet-bleach"), 0.2, 3))
    dl += np.where(sheet, bleach, 0.0)
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
    and water is scanned decals laid where A's runnels run: under the sill, below the nails, down from the gutter.
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
    O = W["overflow"]
    fascia = pg.m["trims"] & (pg.z > h["top"] - 0.05) & (pg.n[..., 1] < -0.5)
    under = wall & (pg.z < h["top"])
    k = key(meta, "b", "overflow")
    z_lip = h["top"] + 0.16
    o = decal(water_img, HS.unit(HS.h(k, "u")) * 0.4 + pg.along / ww, (z_lip - pg.z) / (wh * 1.5))
    o = o * O["strength"] * (meta["neglect"] / 1000.0) / 0.6
    out = np.maximum(out, np.where(fascia, o, np.where(under, 0.55 * o, 0)))
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
    dr = dirt(pg, P, meta)
    wt = water(pg, P, meta, dl)
    hist = np.stack([loss, dr, wt, 0.5 + dl / 20.0], axis=-1)
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
