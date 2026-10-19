"""House generator: west-coast timber houses with their long side to the street.

A house is clapboard walls on a stone plinth under a tiled gable roof, with framed
windows, a door with steps, sometimes a cross-gable (ark) over the front, a chimney,
and sometimes a shop on the ground floor.

build(params, seed) makes one house. Every missing parameter is drawn from the seed,
so the same seed and parameters always give the same house. The style preset
(straight, gentle, strong) sets how far proportions are pushed and how handmade the
house looks; it is the shape-language dial for look tests.

Units are metres, Z up. The pivot is the bottom centre of the footprint, on the ground.
The street side faces -Y.
"""

import math
import random

from kit import Builder, Frame, clip_x, subtract
import palette

STOREY = 3.0  # provisional until the art bible

# -- parameters and their ranges ---------------------------------------------

RANGES = {
    "width": (6, 11),  # street frontage, whole metres
    "depth": (6, 8),  # whole metres
    "storeys": [1, 1.5, 2, 2.5],  # .5 = a loft with a knee wall
    "pitch": (38, 48),  # roof pitch in degrees, before the style pushes it
    "plinth": (0.4, 0.9),
    "ark": 0.4,  # chance of a cross-gable when the house is wide enough
    "shop": 0.3,  # chance of a shop on the ground floor
    "chimneys": [0, 1, 1, 2],
}

STYLES = {
    #               board  lap    pitch  eave  gable  window bay   frame  lean  sag   jitter tilt  chamfer
    "straight": dict(band=0.2, lap=0.012, pitch_mul=1.00, eave=0.35, gable=0.25, win=1.00, bay=1.00, frame=0.10, lean=0.0, sag=0.00, jitter=0.00, tilt=0.0, chamfer=0.000),
    "gentle": dict(band=0.3, lap=0.022, pitch_mul=1.10, eave=0.50, gable=0.35, win=1.08, bay=1.10, frame=0.14, lean=0.7, sag=0.06, jitter=0.035, tilt=0.5, chamfer=0.012),
    "strong": dict(band=0.375, lap=0.034, pitch_mul=1.22, eave=0.65, gable=0.45, win=1.15, bay=1.22, frame=0.19, lean=1.8, sag=0.16, jitter=0.08, tilt=1.4, chamfer=0.025),
}

WALLS = [("wall_white", 46), ("wall_cream", 12), ("wall_yellow", 10), ("wall_grey", 9), ("wall_green", 7), ("wall_blue", 6), ("wall_ochre", 5), ("wall_oxred", 5)]
ROOFS = [("roof_red", 45), ("roof_red_dark", 15), ("roof_black", 25), ("roof_slate", 15)]
DOORS = ["door_green", "door_blue", "door_brown", "door_red", "door_grey", "trim_white"]


def _pick(rng, weighted):
    total = sum(w for _, w in weighted)
    x = rng.uniform(0, total)
    for name, w in weighted:
        x -= w
        if x <= 0:
            return name
    return weighted[-1][0]


def _snap(x, step):
    return max(step, round(x / step) * step)


def sample(seed, style="gentle", **fixed):
    """Draw a full parameter set from the seed. Fixed values win."""
    rng = random.Random(f"house:{seed}")
    s = STYLES[style]
    p = {}
    p["style"] = style
    p["width"] = rng.randint(*RANGES["width"])
    p["depth"] = rng.randint(*RANGES["depth"])
    p["storeys"] = rng.choice(RANGES["storeys"])
    p["pitch"] = min(60.0, rng.uniform(*RANGES["pitch"]) * s["pitch_mul"])
    p["plinth"] = rng.uniform(*RANGES["plinth"])
    p["ark"] = p["storeys"] >= 1.5 and p["width"] >= 7 and rng.random() < RANGES["ark"]
    p["shop"] = rng.random() < RANGES["shop"]
    p["chimneys"] = rng.choice(RANGES["chimneys"])
    p["wall"] = _pick(rng, WALLS)
    p["trim"] = "trim_white" if p["wall"] == "wall_white" or rng.random() < 0.7 else rng.choice(["trim_cream", "trim_dark"])
    p["roof"] = _pick(rng, ROOFS)
    p["door"] = rng.choice(DOORS)
    p["window"] = rng.choice(["T", "six", "T"])
    p["lean_x"] = rng.uniform(-1, 1)
    p["lean_y"] = rng.uniform(-1, 1)
    p["sag"] = rng.uniform(0.5, 1.0)
    p.update(fixed)
    return p


# -- the house ------------------------------------------------------------------


def build(params=None, seed=0, name=None, material=None):
    params = dict(params or {})
    p = sample(seed, params.pop("style", "gentle"), **params)
    s = STYLES[p["style"]]
    rng = random.Random(f"house-detail:{seed}")
    b = Builder()

    W, D, P = float(p["width"]), float(p["depth"]), p["plinth"]
    bh = s["band"]
    full = int(p["storeys"])
    knee = _snap(1.2, bh) if p["storeys"] % 1 else 0.0
    H = full * STOREY + knee  # wall height above the plinth, a whole number of bands
    pitch = math.radians(p["pitch"])
    tp = math.tan(pitch)
    e, g = s["eave"], s["gable"]
    t = 0.05  # board thickness
    lap = s["lap"]
    rt = 0.16  # roof course thickness
    ridge = P + H + (D / 2) * tp
    trim, wall, roof = p["trim"], p["wall"], p["roof"]
    fw = s["frame"]
    cham = s["chamfer"]

    # -- walls: frames and openings ------------------------------------------
    front = Frame((0, -D / 2, P), (1, 0, 0), (0, 0, 1), (0, -1, 0))
    back = Frame((0, D / 2, P), (-1, 0, 0), (0, 0, 1), (0, 1, 0))
    left = Frame((-W / 2, 0, P), (0, -1, 0), (0, 0, 1), (-1, 0, 0))
    right = Frame((W / 2, 0, P), (0, 1, 0), (0, 0, 1), (1, 0, 0))

    bay = 2.2 * s["bay"]
    nb = max(2, round(W / bay))
    centres = [-W / 2 + (i + 0.5) * W / nb for i in range(nb)]
    win_w = 0.9 * s["win"]
    win_h = _snap(1.4 * s["win"], bh)
    sill = _snap(0.9, bh)

    def jitter():
        return rng.uniform(-1, 1) * s["jitter"]

    # front: door, shop, windows, ark
    door_i = nb // 2 if nb % 2 else rng.choice([nb // 2 - 1, nb // 2])
    if nb >= 3 and rng.random() < 0.5:
        door_i = rng.choice([0, nb - 1])
    openings = {"front": [], "back": [], "left": [], "right": []}
    door_w, door_h = 1.0 * s["win"], _snap(2.2, bh)
    openings["front"].append(dict(a=centres[door_i] + jitter(), b0=0.0, b1=door_h, w=door_w, kind="door"))

    shop_bays = []
    if p["shop"] and nb >= 2:
        candidates = [i for i in range(nb - 1) if door_i not in (i, i + 1)] or [i for i in range(nb) if i != door_i]
        i = rng.choice(candidates)
        shop_bays = [i, i + 1] if i + 1 < nb and i + 1 != door_i else [i]
        a0 = centres[shop_bays[0]] - W / nb / 2 + 0.35
        a1 = centres[shop_bays[-1]] + W / nb / 2 - 0.35
        openings["front"].append(dict(a=(a0 + a1) / 2, b0=_snap(0.6, bh), b1=_snap(2.4, bh), w=a1 - a0, kind="shop"))

    for st in range(full):
        base = st * STOREY
        for i, c in enumerate(centres):
            if st == 0 and (i == door_i or i in shop_bays):
                continue
            openings["front"].append(dict(a=c + jitter(), b0=base + sill, b1=base + sill + win_h, w=win_w, kind="window"))
            if rng.random() < 0.75:
                openings["back"].append(dict(a=c + jitter(), b0=base + sill, b1=base + sill + win_h, w=win_w, kind="window"))
        ng = max(1, round(D / bay) - 1)
        for gname in ("left", "right"):
            for k in range(ng):
                if rng.random() < 0.8:
                    a = -D / 2 + (k + 0.5) * D / ng
                    openings[gname].append(dict(a=a + jitter(), b0=base + sill, b1=base + sill + win_h, w=win_w, kind="window"))

    # loft windows in the gables
    loft_h = _snap(1.1 * s["win"], bh)
    loft_b0 = H + _snap(0.45, bh)
    for gname in ("left", "right"):
        half_at_top = (D / 2) * (1 - (loft_b0 + loft_h + fw * 2 - H) / ((D / 2) * tp))
        if half_at_top > win_w / 2 + fw + 0.1:
            openings[gname].append(dict(a=jitter(), b0=loft_b0, b1=loft_b0 + loft_h, w=win_w * 0.9, kind="window"))

    profiles = {
        "front": dict(lo=-W / 2, hi=W / 2, H=H, tris=[]),
        "back": dict(lo=-W / 2, hi=W / 2, H=H, tris=[]),
        "left": dict(lo=-D / 2, hi=D / 2, H=H, tris=[(0.0, D / 2, H, H + (D / 2) * tp)]),
        "right": dict(lo=-D / 2, hi=D / 2, H=H, tris=[(0.0, D / 2, H, H + (D / 2) * tp)]),
    }

    ark = None
    if p["ark"]:
        ax = centres[nb // 2] if nb % 2 else 0.0
        aw = min(W * 0.45, max(2.6, W / nb * 1.3))
        pa = min(math.radians(60), pitch * 1.12)
        apex = H + (aw / 2) * math.tan(pa)
        if apex < H + (D / 2) * tp - 0.6:
            ark = dict(x=ax, w=aw, pitch=pa, apex=apex)
            profiles["front"]["tris"].append((ax, aw / 2, H, apex))
            openings["front"].append(dict(a=ax, b0=H + _snap(0.3, bh), b1=H + _snap(0.3, bh) + loft_h, w=win_w * 0.9, kind="window"))

    frames = dict(front=front, back=back, left=left, right=right)

    # -- clapboard ------------------------------------------------------------
    for wname, prof in profiles.items():
        fr = frames[wname]
        top = max([prof["H"]] + [tri[3] for tri in prof["tris"]])
        k = 0
        while k * bh < top - 1e-6:
            b0, b1 = k * bh, (k + 1) * bh
            polys = []
            if b1 <= prof["H"] + 1e-6:
                polys.append([(prof["lo"], b0), (prof["hi"], b0), (prof["hi"], b1), (prof["lo"], b1)])
            else:
                for ac, half, base, apex in prof["tris"]:
                    hw0 = half * (apex - b0) / (apex - base)
                    if hw0 <= 1e-3:
                        continue
                    if b1 < apex:
                        hw1 = half * (apex - b1) / (apex - base)
                        polys.append([(ac - hw0, b0), (ac + hw0, b0), (ac + hw1, b1), (ac - hw1, b1)])
                    else:
                        polys.append([(ac - hw0, b0), (ac + hw0, b0), (ac, apex)])
            for poly in polys:
                xs = [q[0] for q in poly]
                spans = [(min(xs), max(xs))]
                for o in openings[wname]:
                    if o["b0"] <= b0 + 1e-6 and o["b1"] >= b1 - 1e-6:
                        spans = subtract(spans, (o["a"] - o["w"] / 2, o["a"] + o["w"] / 2))
                for lo, hi in spans:
                    piece = clip_x(poly, lo, hi)
                    if piece:
                        b.strip(fr, piece, b0, b1, t, lap, wall)
            k += 1

    # corner boards
    cb = 0.12 + fw * 0.6
    out = t + lap + 0.012
    for sx in (-1, 1):
        for sy in (-1, 1):
            cx = sx * (W / 2 + out - cb / 2)
            cy = sy * (D / 2 + out - cb / 2)
            b.box(Frame((0, 0, 0), (1, 0, 0), (0, 0, 1), (0, -1, 0)), cx, P + H / 2, -cy, cb / 2, H / 2, cb / 2, trim, chamfer=cham * 0.5)

    # -- openings -------------------------------------------------------------
    rd = 0.14  # how far glass sits behind the board line
    fp = 0.03 + fw * 0.15  # how far frames stand out
    for wname, ops in openings.items():
        fr = frames[wname]
        for o in ops:
            a0, a1 = o["a"] - o["w"] / 2, o["a"] + o["w"] / 2
            b0, b1 = o["b0"], o["b1"]
            ac, bc, hw, hh = o["a"], (b0 + b1) / 2, o["w"] / 2, (b1 - b0) / 2
            # reveals line the hole so it never shows through
            b.box(fr, a0 - 0.02, bc, (t - rd) / 2, 0.02, hh, (t + rd) / 2, trim)
            b.box(fr, a1 + 0.02, bc, (t - rd) / 2, 0.02, hh, (t + rd) / 2, trim)
            b.box(fr, ac, b1 + 0.02, (t - rd) / 2, hw, 0.02, (t + rd) / 2, trim)
            if o["kind"] != "door":
                b.box(fr, ac, b0 - 0.02, (t - rd) / 2, hw, 0.02, (t + rd) / 2, trim)
            tilt = math.radians(rng.uniform(-1, 1) * s["tilt"])
            ct, st_ = math.cos(tilt), math.sin(tilt)
            tf = Frame(fr.point(ac, bc), fr.u * ct + fr.v * st_, fr.v * ct - fr.u * st_, fr.n)
            face = t + lap + fp
            if o["kind"] == "door":
                b.box(fr, ac, bc, -rd + 0.03, hw, hh, 0.03, p["door"], chamfer=cham * 0.5)
                for py in (0.28, 0.72):
                    b.box(fr, ac, b0 + (b1 - b0) * py, -rd + 0.07, hw * 0.62, hh * 0.3, 0.012, p["door"], chamfer=cham * 0.5)
                # casing and crown
                b.box(tf, -hw - fw / 2, 0, face / 2, fw / 2, hh, face / 2, trim, chamfer=cham)
                b.box(tf, hw + fw / 2, 0, face / 2, fw / 2, hh, face / 2, trim, chamfer=cham)
                b.box(tf, 0, hh + fw * 0.6, face / 2 + 0.01, hw + fw * 1.4, fw * 0.6, face / 2 + 0.01, trim, chamfer=cham)
                # steps up from the ground
                n_steps = max(1, math.ceil(P / 0.19))
                for k in range(n_steps):
                    top_b = -P + (k + 1) * P / n_steps
                    depth = (n_steps - k) * 0.32
                    b.box(fr, ac, (-P + top_b) / 2, depth / 2, hw + 0.25, (top_b + P) / 2, depth / 2, "stone", chamfer=cham)
                continue
            glass = "glass_shop" if o["kind"] == "shop" else "glass"
            b.box(fr, ac, bc, -rd + 0.01, hw, hh, 0.01, glass)
            # sash and bars
            sw = 0.04 + fw * 0.12
            z = -rd + 0.04
            b.box(fr, ac, b0 + sw / 2, z, hw, sw / 2, 0.02, trim)
            b.box(fr, ac, b1 - sw / 2, z, hw, sw / 2, 0.02, trim)
            b.box(fr, a0 + sw / 2, bc, z, sw / 2, hh, 0.02, trim)
            b.box(fr, a1 - sw / 2, bc, z, sw / 2, hh, 0.02, trim)
            if o["kind"] == "shop":
                n = max(1, round(o["w"] / 1.3))
                for k in range(1, n):
                    b.box(fr, a0 + k * o["w"] / n, bc, z, sw / 2, hh, 0.02, trim)
                # stall riser and sign band
                b.box(fr, ac, b0 / 2, t / 2 + 0.01, hw + 0.05, b0 / 2, t / 2 + 0.02, p["door"], chamfer=cham)
                b.box(tf, 0, hh + fw + 0.32, face / 2 + 0.02, hw + fw, 0.3, face / 2 + 0.02, {"default": trim, "n+": "sign"}, chamfer=cham)
            elif p["window"] == "T":
                tr = b0 + (b1 - b0) * 0.68
                b.box(fr, ac, tr, z, hw, sw / 2, 0.02, trim)
                b.box(fr, ac, (b0 + tr) / 2, z, sw / 2, (tr - b0) / 2, 0.02, trim)
            else:
                b.box(fr, ac, bc, z, sw / 2, hh, 0.02, trim)
                for f in (1 / 3, 2 / 3):
                    b.box(fr, ac, b0 + (b1 - b0) * f, z, hw, sw / 2, 0.02, trim)
            # casing, sill, crown
            b.box(tf, -hw - fw / 2, 0, face / 2, fw / 2, hh + fw, face / 2, trim, chamfer=cham)
            b.box(tf, hw + fw / 2, 0, face / 2, fw / 2, hh + fw, face / 2, trim, chamfer=cham)
            b.box(tf, 0, hh + fw / 2, face / 2, hw, fw / 2, face / 2, trim, chamfer=cham)
            b.box(tf, 0, -hh - 0.04, (face + 0.06) / 2, hw + fw + 0.05, 0.04, (face + 0.06) / 2, trim, chamfer=cham)
            if o["kind"] != "shop":
                crown = fw * (0.5 + 2.5 * s["frame"])
                b.box(tf, 0, hh + fw + crown / 2, (face + 0.04) / 2, hw + fw * 1.5, crown / 2, (face + 0.04) / 2, trim, chamfer=cham)

    # -- plinth ---------------------------------------------------------------
    pe = t + lap + 0.05
    b.box(Frame((0, 0, 0), (1, 0, 0), (0, 0, 1), (0, -1, 0)), 0, P / 2, 0, W / 2 + pe, P / 2, D / 2 + pe, "stone", chamfer=cham)

    # -- roof -----------------------------------------------------------------
    ch = 0.28 + bh * 0.4  # course height along the slope
    L = (D / 2 + e) / math.cos(pitch)
    v_wall = e / math.cos(pitch)
    for side in (-1, 1):
        rf = Frame((0, side * (D / 2 + e), P + H - e * tp), (1, 0, 0), (0, -side * math.cos(pitch), math.sin(pitch)), (0, side * math.sin(pitch), math.cos(pitch)))
        k = 0
        while k * ch < L - 1e-6:
            b0, b1 = k * ch, min(L, (k + 1) * ch)
            spans = [(-W / 2 - g, W / 2 + g)]
            if ark and side == -1 and b0 < v_wall + ch:
                spans = subtract(spans, (ark["x"] - ark["w"] / 2, ark["x"] + ark["w"] / 2))
            for lo, hi in spans:
                b.strip(rf, [(lo, b0), (hi, b0), (hi, b1), (lo, b1)], b0, b1, rt, lap * 2.5, roof, side_swatch=trim)
            k += 1
    # ridge
    rw = rt * math.sin(pitch) + 0.12
    b.box(Frame((0, 0, 0), (1, 0, 0), (0, 0, 1), (0, -1, 0)), 0, ridge + rt / math.cos(pitch) - 0.02, 0, W / 2 + g + 0.02, 0.09, rw, "roof_ridge", chamfer=cham)

    if ark:
        pa, aw, ax = ark["pitch"], ark["w"], ark["x"]
        tpa = math.tan(pa)
        y_front = -(D / 2 + g)
        y_back = -D / 2 + ((aw / 2) * tpa + 2.5 * rt) / tp
        La = (aw / 2 + e) / math.cos(pa)
        for side in (-1, 1):
            rf = Frame((ax + side * (aw / 2 + e), 0, P + H - e * tpa), (0, 1, 0), (-side * math.cos(pa), 0, math.sin(pa)), (side * math.sin(pa), 0, math.cos(pa)))
            k = 0
            while k * ch < La - 1e-6:
                b0, b1 = k * ch, min(La, (k + 1) * ch)
                b.strip(rf, [(y_front, b0), (y_back, b0), (y_back, b1), (y_front, b1)], b0, b1, rt, lap * 2.5, roof, side_swatch=trim)
                k += 1
        aridge = P + ark["apex"] + rt / math.cos(pa) - 0.02
        b.box(Frame((0, 0, 0), (0, 1, 0), (0, 0, 1), (1, 0, 0)), (y_front + y_back) / 2, aridge, ax, (y_back - y_front) / 2 + 0.02, 0.09, rt * math.sin(pa) + 0.12, "roof_ridge", chamfer=cham)
        # corner trims at the ark's edges above the eave
        for side in (-1, 1):
            b.box(front, ax + side * (aw / 2 - cb / 2 + 0.01), H + 0.4, out - cb / 2, cb / 2, 0.4, cb / 2, trim, chamfer=cham * 0.5)

    # -- chimneys ---------------------------------------------------------------
    cs = 0.55 + s["frame"] * 0.8
    ctop = ridge + 0.9
    chim = rng.choice(["brick", "render_white", "brick"])
    for i in range(p["chimneys"]):
        cx = rng.uniform(-W / 4, W / 4) if p["chimneys"] == 1 else (-1 if i == 0 else 1) * W * rng.uniform(0.18, 0.3)
        cy = rng.choice([0.0, 0.0, -0.7, 0.7])
        zb = P + H
        b.box(Frame((0, 0, 0), (1, 0, 0), (0, 0, 1), (0, -1, 0)), cx, (zb + ctop) / 2, -cy, cs / 2, (ctop - zb) / 2, cs / 2, chim, chamfer=cham)
        b.box(Frame((0, 0, 0), (1, 0, 0), (0, 0, 1), (0, -1, 0)), cx, ctop + 0.05, -cy, cs / 2 + 0.06, 0.05, cs / 2 + 0.06, "stone_dark", chamfer=cham)

    # -- the hand: lean and sag ---------------------------------------------------
    lean_x = math.tan(math.radians(s["lean"] * p["lean_x"]))
    lean_y = math.tan(math.radians(s["lean"] * 0.5 * p["lean_y"]))
    sag = s["sag"] * p["sag"]
    eave_z = P + H
    span = W / 2 + g + 0.1

    def hand(v):
        x, y, z = v
        f = 0.0
        if z > eave_z - 1.0:
            r = min(max((z - (eave_z - 1.0)) / (ridge - eave_z + 1.0), 0.0), 1.0)
            f = r * r * (3 - 2 * r)
        shape = max(0.0, 1.0 - (x / span) ** 2)
        z2 = z - sag * f * shape
        return type(v)((x + lean_x * z, y + lean_y * z, z2))

    b.deform(hand)

    name = name or f"kit_house_{p['style']}-{seed}_lod0"
    obj = b.build(name, material or palette.material())
    obj["params"] = repr(p)
    obj["seed"] = seed
    obj["triangles"] = b.triangles()
    return obj
