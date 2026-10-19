"""Kit parts: windows, doors and shopfronts by era, boarding, and the small things of life.

Each function adds geometry to a Builder in a wall frame (u along the wall, v up,
n out of the wall). Positions are metres in that frame; the opening is already cut
in the wall. Styles are named in eras.py; every part is chosen by the resolver.
"""

import math

from kit import Frame


def tilted(fr, a, b, angle):
    ct, st = math.cos(angle), math.sin(angle)
    return Frame(fr.point(a, b), fr.u * ct + fr.v * st, fr.v * ct - fr.u * st, fr.n)


class Ctx:
    """What every part needs to know: board depth, frame sizes, colours, chamfer."""

    def __init__(self, t, lap, fw, cham, trim, sash, wall, door, glass="glass"):
        self.t, self.lap, self.fw, self.cham = t, lap, fw, cham
        self.trim, self.sash, self.wall, self.door, self.glass = trim, sash, wall, door, glass
        self.face = t + lap + 0.03 + fw * 0.15  # how far frames stand proud of the wall line
        self.rd = 0.14  # how far glass sits behind the wall line


def reveal(b, fr, a0, a1, b0, b1, c, with_bottom=True):
    ac, bc, hw, hh = (a0 + a1) / 2, (b0 + b1) / 2, (a1 - a0) / 2, (b1 - b0) / 2
    depth = (c.t + c.rd) / 2
    z = (c.t - c.rd) / 2
    b.box(fr, a0 - 0.02, bc, z, 0.02, hh, depth, c.trim)
    b.box(fr, a1 + 0.02, bc, z, 0.02, hh, depth, c.trim)
    b.box(fr, ac, b1 + 0.02, z, hw + 0.04, 0.02, depth, c.trim)
    if with_bottom:
        b.box(fr, ac, b0 - 0.02, z, hw + 0.04, 0.02, depth, c.trim)


def glass_and_bars(b, fr, a0, a1, b0, b1, c, cols=1, rows=1, transom=None, glass=None, bar=None, top_grid=None):
    """Glass with sash frame and glazing bars. transom: fraction where a horizontal bar sits."""
    ac, bc, hw, hh = (a0 + a1) / 2, (b0 + b1) / 2, (a1 - a0) / 2, (b1 - b0) / 2
    b.box(fr, ac, bc, -c.rd + 0.01, hw, hh, 0.01, glass or c.glass)
    sw = bar or (0.035 + c.fw * 0.12)
    z = -c.rd + 0.04
    col = c.sash
    b.box(fr, ac, b0 + sw / 2, z, hw, sw / 2, 0.02, col)
    b.box(fr, ac, b1 - sw / 2, z, hw, sw / 2, 0.02, col)
    b.box(fr, a0 + sw / 2, bc, z, sw / 2, hh, 0.02, col)
    b.box(fr, a1 - sw / 2, bc, z, sw / 2, hh, 0.02, col)
    for k in range(1, cols):
        b.box(fr, a0 + k * (a1 - a0) / cols, bc, z, sw * 0.4, hh, 0.02, col)
    for k in range(1, rows):
        b.box(fr, ac, b0 + k * (b1 - b0) / rows, z, hw, sw * 0.4, 0.02, col)
    if transom is not None:
        tb = b0 + (b1 - b0) * transom
        b.box(fr, ac, tb, z, hw, sw * 0.6, 0.02, col)
        if top_grid:
            for k in range(1, top_grid):
                b.box(fr, a0 + k * (a1 - a0) / top_grid, (tb + b1) / 2, z, sw * 0.35, (b1 - tb) / 2, 0.02, col)


def curtains(b, fr, a0, a1, b0, b1, colour, kind):
    """Curtains just inside the glass: side panels, or a half curtain across the lower part."""
    z = -0.15
    w = (a1 - a0)
    if kind == "half":
        b.box(fr, (a0 + a1) / 2, b0 + (b1 - b0) * 0.25, z, w / 2 - 0.02, (b1 - b0) * 0.25, 0.005, colour)
    else:
        cw = w * 0.2
        b.box(fr, a0 + cw / 2 + 0.03, (b0 + b1) / 2, z, cw / 2, (b1 - b0) / 2 - 0.03, 0.005, colour)
        b.box(fr, a1 - cw / 2 - 0.03, (b0 + b1) / 2, z, cw / 2, (b1 - b0) / 2 - 0.03, 0.005, colour)


def casing(b, fr, a0, a1, b0, b1, c, width, angle=0.0, crown=None, sill=True):
    """The frame around an opening, its sill and its crown (none, flat, cornice, pediment, arch)."""
    ac, bc, hw, hh = (a0 + a1) / 2, (b0 + b1) / 2, (a1 - a0) / 2, (b1 - b0) / 2
    tf = tilted(fr, ac, bc, angle)
    face = c.face
    fw = width
    b.box(tf, -hw - fw / 2, 0, face / 2, fw / 2, hh + fw, face / 2, c.trim, chamfer=c.cham)
    b.box(tf, hw + fw / 2, 0, face / 2, fw / 2, hh + fw, face / 2, c.trim, chamfer=c.cham)
    b.box(tf, 0, hh + fw / 2, face / 2, hw, fw / 2, face / 2, c.trim, chamfer=c.cham)
    if sill:
        b.box(tf, 0, -hh - 0.04, (face + 0.06) / 2, hw + fw + 0.05, 0.04, (face + 0.06) / 2, c.trim, chamfer=c.cham)
    top = hh + fw
    if crown == "flat":
        ch = fw * 0.7
        b.box(tf, 0, top + ch / 2, (face + 0.03) / 2, hw + fw * 1.3, ch / 2, (face + 0.03) / 2, c.trim, chamfer=c.cham)
    elif crown == "cornice":
        ch = fw * 0.9
        b.box(tf, 0, top + ch / 2, (face + 0.02) / 2, hw + fw * 1.2, ch / 2, (face + 0.02) / 2, c.trim, chamfer=c.cham)
        b.box(tf, 0, top + ch + 0.035, (face + 0.08) / 2, hw + fw * 1.6, 0.035, (face + 0.08) / 2, c.trim, chamfer=c.cham)
    elif crown == "pediment":
        base = 0.06
        b.box(tf, 0, top + base / 2, (face + 0.03) / 2, hw + fw * 1.5, base / 2, (face + 0.03) / 2, c.trim, chamfer=c.cham)
        span = hw + fw * 1.5
        rise = span * 0.45
        poly = [(-span, top + base), (span, top + base), (0, top + base + rise)]
        b.strip(tf.sub(0, 0, 0), poly, top + base, top + base + rise, face + 0.02, 0.0, c.trim)
    elif crown == "arch":
        span = hw + fw
        rise = span * 0.35
        pts = [(-span, top)]
        for k in range(1, 8):
            x = -span + 2 * span * k / 8
            pts.append((x, top + rise * (1 - (x / span) ** 2)))
        pts.append((span, top))
        b.strip(tf, pts, top, top + rise, face + 0.01, 0.0, c.trim)


# -- windows ------------------------------------------------------------------------


def window(b, fr, a0, a1, b0, b1, c, style, angle=0.0, crown=None, boarded=False, reduced=False, curtain=None, lit=False):
    if reduced:
        # a smaller standard window set low in the old opening; the rest boarded in, in the wall colour
        na0, na1 = a0 + (a1 - a0) * 0.12, a1 - (a1 - a0) * 0.12
        nb1 = b0 + (b1 - b0) * 0.78
        b.box(fr, (a0 + a1) / 2, (nb1 + b1) / 2, -0.04, (a1 - a0) / 2, (b1 - nb1) / 2, 0.04, c.wall)
        b.box(fr, (a0 + na0) / 2, (b0 + nb1) / 2, -0.04, (na0 - a0) / 2, (nb1 - b0) / 2, 0.04, c.wall)
        b.box(fr, (na1 + a1) / 2, (b0 + nb1) / 2, -0.04, (a1 - na1) / 2, (nb1 - b0) / 2, 0.04, c.wall)
        reveal(b, fr, a0, a1, b0, b1, c)
        window(b, fr, na0, na1, b0, nb1, c, style, angle=0.0, crown=None, curtain=curtain, lit=lit)
        return
    reveal(b, fr, a0, a1, b0, b1, c)
    glass = "glass_lit" if lit else None
    if style == "small_panes":
        glass_and_bars(b, fr, a0, a1, b0, b1, c, cols=2, rows=3, glass=glass)
        fw = c.fw
    elif style == "cross_t":
        glass_and_bars(b, fr, a0, a1, b0, b1, c, transom=0.68, glass=glass)
        tb = b0 + (b1 - b0) * 0.68
        sw = 0.035 + c.fw * 0.12
        b.box(fr, (a0 + a1) / 2, (b0 + tb) / 2, -c.rd + 0.04, sw / 2, (tb - b0) / 2, 0.02, c.sash)
        fw = c.fw * 1.15
    elif style == "cross_arch":
        glass_and_bars(b, fr, a0, a1, b0, b1, c, transom=0.62, top_grid=3, glass=glass)
        tb = b0 + (b1 - b0) * 0.62
        sw = 0.035 + c.fw * 0.12
        b.box(fr, (a0 + a1) / 2, (b0 + tb) / 2, -c.rd + 0.04, sw / 2, (tb - b0) / 2, 0.02, c.sash)
        fw = c.fw
    elif style == "band":
        glass_and_bars(b, fr, a0, a1, b0, b1, c, cols=3, glass=glass, bar=0.05)
        fw = c.fw * 0.45
    elif style == "picture":
        glass_and_bars(b, fr, a0, a1, b0, b1, c, cols=1, glass=glass, bar=0.06)
        b.box(fr, a0 + (a1 - a0) * 0.76, (b0 + b1) / 2, -c.rd + 0.04, 0.03, (b1 - b0) / 2, 0.02, c.sash)
        fw = c.fw * 0.4
    elif style == "casement":
        glass_and_bars(b, fr, a0, a1, b0, b1, c, cols=2, glass=glass, bar=0.055)
        fw = c.fw * 0.4
    elif style == "stick_bars":
        glass_and_bars(b, fr, a0, a1, b0, b1, c, cols=2, glass=glass, bar=0.05)
        for k in (1, 3):
            b.box(fr, a0 + k * (a1 - a0) / 4, (b0 + b1) / 2, -c.rd + 0.035, 0.01, (b1 - b0) / 2, 0.006, c.sash)
        for k in (1, 2):
            b.box(fr, (a0 + a1) / 2, b0 + k * (b1 - b0) / 3, -c.rd + 0.035, (a1 - a0) / 2, 0.01, 0.006, c.sash)
        fw = c.fw * 0.5
    else:
        glass_and_bars(b, fr, a0, a1, b0, b1, c, glass=glass)
        fw = c.fw
    if curtain and not boarded:
        curtains(b, fr, a0, a1, b0, b1, curtain[0], curtain[1])
    casing(b, fr, a0, a1, b0, b1, c, fw, angle=angle, crown=crown)
    if boarded:
        boards(b, fr, a0, a1, b0, b1, c, angle)


def boards(b, fr, a0, a1, b0, b1, c, angle=0.0):
    """Planks nailed over an opening, a little crooked, with a brace."""
    n = max(2, int((b1 - b0) / 0.22))
    ph = (b1 - b0) / n
    for k in range(n):
        tf = tilted(fr, (a0 + a1) / 2, b0 + ph * (k + 0.5), angle * (1 if k % 2 else -1) * 2 + 0.02 * ((k * 7) % 3 - 1))
        b.box(tf, 0, 0, c.face + 0.02, (a1 - a0) / 2 + 0.08, ph * 0.42, 0.018, "wood", chamfer=0.005)
    diag = math.atan2(b1 - b0, a1 - a0)
    tf = tilted(fr, (a0 + a1) / 2, (b0 + b1) / 2, diag)
    b.box(tf, 0, 0, c.face + 0.05, math.hypot(a1 - a0, b1 - b0) / 2, 0.05, 0.018, "wood", chamfer=0.005)


# -- doors ----------------------------------------------------------------------------


def door(b, fr, a0, a1, b0, b1, c, style, angle=0.0, crown=None, boarded=False):
    ac, hw = (a0 + a1) / 2, (a1 - a0) / 2
    reveal(b, fr, a0, a1, b0, b1, c, with_bottom=False)
    leaf_b1 = b1
    if style == "panel_fanlight":
        leaf_b1 = b1 - 0.4
        glass_and_bars(b, fr, a0, a1, leaf_b1 + 0.04, b1, c, cols=3)
        b.box(fr, ac, leaf_b1 + 0.02, -c.rd + 0.05, hw, 0.02, 0.03, c.sash)
    lh = (leaf_b1 - b0) / 2
    b.box(fr, ac, b0 + lh, -c.rd + 0.03, hw, lh, 0.03, c.door, chamfer=c.cham * 0.5)
    if style in ("panel_fanlight", "eighties"):
        for py in (0.27, 0.73):
            for px in ((-0.5, 0.5) if style == "panel_fanlight" else (0,)):
                b.box(fr, ac + px * hw, b0 + (leaf_b1 - b0) * py, -c.rd + 0.07, hw * (0.38 if px else 0.7), lh * 0.36, 0.012, c.door, chamfer=c.cham * 0.5)
        if style == "eighties":
            b.box(fr, ac, b0 + (leaf_b1 - b0) * 0.73, -c.rd + 0.085, hw * 0.4, lh * 0.25, 0.01, "glass")
    elif style == "chalet_glass":
        gb0 = b0 + (leaf_b1 - b0) * 0.55
        b.box(fr, ac - hw * 0.45, (gb0 + leaf_b1 - 0.12) / 2, -c.rd + 0.07, hw * 0.38, (leaf_b1 - 0.12 - gb0) / 2, 0.01, "glass")
        b.box(fr, ac + hw * 0.45, (gb0 + leaf_b1 - 0.12) / 2, -c.rd + 0.07, hw * 0.38, (leaf_b1 - 0.12 - gb0) / 2, 0.01, "glass")
        b.box(fr, ac, b0 + (gb0 - b0) / 2, -c.rd + 0.07, hw * 0.75, (gb0 - b0) * 0.36, 0.012, c.door, chamfer=c.cham * 0.5)
    elif style == "funkis_canopy":
        b.box(fr, ac, b0 + (leaf_b1 - b0) * 0.7, -c.rd + 0.07, 0.11, 0.11, 0.01, "glass")
        b.box(fr, ac, b1 + 0.2, 0.55, hw + 0.5, 0.05, 0.6, c.trim, chamfer=c.cham)
    elif style == "teak_strip":
        for k in (-0.5, 0, 0.5):
            b.box(fr, ac + k * hw, b0 + lh, -c.rd + 0.065, 0.012, lh * 0.92, 0.008, "trim_dark")
        b.box(fr, a1 + 0.25, b0 + lh, -0.06, 0.1, lh * 0.9, 0.01, "glass")
    fw = c.fw * (0.5 if style in ("funkis_canopy", "teak_strip", "eighties") else 1.0)
    casing(b, fr, a0, a1, b0, b1, c, fw, angle=angle, crown=crown, sill=False)
    if boarded:
        boards(b, fr, a0, a1, b0, b1, c, angle)


def steps(b, fr, a, w, height, c):
    """Steps from the ground up to a door, with railings when they are high."""
    if height < 0.05:
        return
    n = max(1, math.ceil(height / 0.18))
    for k in range(n):
        top = -height + (k + 1) * height / n
        depth = (n - k) * 0.3
        b.box(fr, a, (-height + top) / 2, depth / 2, w / 2 + 0.25, (top + height) / 2, depth / 2, "stone", chamfer=c.cham)
    if height > 0.45:
        run = n * 0.3
        rf = Frame(fr.o, fr.n, fr.v, fr.u)  # u = out from the wall, n = along it
        for side in (-1, 1):
            x = a + side * (w / 2 + 0.2)
            for d in (0.05, run - 0.05):
                hgt = -height + height * (1 - d / run) + 0.9
                b.box(rf, d, (-height + hgt) / 2 + 0.0, x, 0.025, (hgt + height) / 2, 0.025, "metal_dark")
            ang = math.atan2(-height, run)
            tf = Frame(rf.point(run / 2, -height / 2 + 0.9, x), rf.u * math.cos(ang) + rf.v * math.sin(ang), rf.v * math.cos(ang) - rf.u * math.sin(ang), rf.n)
            b.box(tf, 0, 0, 0, math.hypot(run, height) / 2 + 0.05, 0.02, 0.025, "metal_dark")


# -- shopfronts ---------------------------------------------------------------------------


def shopfront(b, fr, a0, a1, b0, b1, c, style, sign=None, ghost=False, boarded=False, lit=False):
    """The shop window and its sign band. sign: the current business, or None."""
    ac, hw = (a0 + a1) / 2, (a1 - a0) / 2
    reveal(b, fr, a0, a1, b0, b1, c)
    glass = "glass_lit" if lit else "glass_shop"
    if style == "shop_1900":
        tb = b1 - (b1 - b0) * 0.2
        glass_and_bars(b, fr, a0, a1, b0, b1, c, cols=3, transom=(tb - b0) / (b1 - b0), top_grid=6, glass=glass)
        for x in (a0 - 0.12, a1 + 0.12):
            b.box(fr, x, (b0 + b1) / 2 - 0.15, c.face / 2 + 0.02, 0.12, (b1 - b0) / 2 + 0.45, c.face / 2 + 0.02, c.trim, chamfer=c.cham)
            b.box(fr, x, b1 + 0.62, c.face / 2 + 0.05, 0.15, 0.06, c.face / 2 + 0.05, c.trim, chamfer=c.cham)
        riser = c.door
        band = (b1 + 0.1, b1 + 0.6)
        band_col = "sign" if sign else ("stone" if ghost else c.trim)
        cornice = True
    elif style == "shop_1930":
        glass_and_bars(b, fr, a0, a1, b0, b1, c, cols=2, glass=glass, bar=0.04)
        riser = "trim_dark"
        band = (b1 + 0.05, b1 + 0.55)
        band_col = "trim_dark" if sign or ghost else c.trim
        cornice = False
    elif style == "shop_1960":
        glass_and_bars(b, fr, a0, a1, b0 - 0.35, b1, c, cols=3, glass=glass, bar=0.035)
        riser = "metal_gutter"
        band = (b1 + 0.05, b1 + 0.45)
        band_col = "sign" if sign else ("stone" if ghost else "metal_gutter")
        cornice = False
    else:  # shop_1980: the bar, small windows in a dark front
        riser = "wood"
        mid = ac
        b.box(fr, ac, (b0 + b1) / 2, -0.05, hw, (b1 - b0) / 2, 0.05, "wood")
        for x0, x1 in ((a0 + 0.15, mid - 0.25), (mid + 0.25, a1 - 0.15)):
            glass_and_bars(b, fr, x0, x1, b0 + 0.3, b1 - 0.2, c, cols=2, rows=2, glass="glass_lit" if lit else "glass", bar=0.04)
        band = (b1 + 0.05, b1 + 0.55)
        band_col = "trim_dark"
        cornice = False
    # stall riser below the glass
    if b0 > 0.05:
        b.box(fr, ac, b0 / 2, c.t / 2 + 0.01, hw + 0.02, b0 / 2, c.t / 2 + 0.03, riser, chamfer=c.cham)
    # sign band
    b.box(fr, ac, (band[0] + band[1]) / 2, c.face / 2 + 0.03, hw + 0.15, (band[1] - band[0]) / 2, c.face / 2 + 0.03, {"default": c.trim, "n+": band_col}, chamfer=c.cham)
    if cornice:
        b.box(fr, ac, band[1] + 0.05, c.face / 2 + 0.08, hw + 0.3, 0.05, c.face / 2 + 0.08, c.trim, chamfer=c.cham)
    if sign and style in ("shop_1960", "shop_1980"):
        # a projecting box sign
        sf = Frame(fr.point(a1 + 0.4, band[1] + 0.3, 0.0), fr.n, fr.v, fr.u)
        b.box(sf, 0.45, 0, 0, 0.4, 0.3, 0.06, {"default": "metal_dark", "n+": "glass_lit" if style == "shop_1980" else "sign", "n-": "glass_lit" if style == "shop_1980" else "sign"})
        b.box(sf, 0.05, 0, 0, 0.05, 0.03, 0.03, "metal_dark")
    if sign and style == "shop_1900":
        # a hanging bracket sign
        sf = Frame(fr.point(a0 - 0.3, band[1] + 0.2, 0.0), fr.n, fr.v, fr.u)
        b.box(sf, 0.45, 0.25, 0, 0.45, 0.02, 0.02, "metal_dark")
        b.box(sf, 0.6, -0.05, 0, 0.28, 0.22, 0.02, {"default": "metal_dark", "n+": "sign", "n-": "sign"})
    if boarded:
        boards(b, fr, a0, a1, b0, b1, c)


def loading_door(b, fr, a0, a1, b0, b1, c, boarded=False):
    """Two plank leaves, the kind on a quay warehouse."""
    ac, hw, hh = (a0 + a1) / 2, (a1 - a0) / 2, (b1 - b0) / 2
    reveal(b, fr, a0, a1, b0, b1, c, with_bottom=False)
    n = max(4, int((a1 - a0) / 0.16))
    for k in range(n):
        x = a0 + (k + 0.5) * (a1 - a0) / n
        b.box(fr, x, b0 + hh, -0.06, (a1 - a0) / n / 2 - 0.006, hh, 0.03, c.door)
    for y in (0.2, 0.8):
        b.box(fr, ac, b0 + (b1 - b0) * y, -0.02, hw - 0.02, 0.05, 0.015, c.door)
    b.box(fr, ac, b0 + hh, -0.01, 0.015, hh, 0.02, "metal_dark")
    casing(b, fr, a0, a1, b0, b1, c, c.fw * 0.8, sill=False)
    if boarded:
        boards(b, fr, a0, a1, b0, b1, c)


def flower_box(b, fr, a0, a1, sill_b, c, key):
    ac, hw = (a0 + a1) / 2, (a1 - a0) / 2 + 0.05
    b.box(fr, ac, sill_b - 0.2, c.face + 0.12, hw, 0.09, 0.1, c.trim, chamfer=c.cham)
    n = max(3, int(hw * 2 / 0.12))
    for k in range(n):
        x = ac - hw + (k + 0.5) * hw * 2 / n
        col = ("flowers_red", "leaf", "flowers_yellow", "leaf")[(key + k) % 4]
        b.box(fr, x, sill_b - 0.06 + 0.04 * ((key >> k) & 1), c.face + 0.12, 0.05, 0.06, 0.07, col, chamfer=0.01)
