"""Way A's tileables: each material's surface made here from seeded fields, never from a photograph.

    Blender -b --factory-startup -P blender/parts/finish/tiles.py -- --cache cache/finish

Writes into <cache>/out, each 1,024 square over 2 m (corner.json's tileable and trim sheet), 8 bits, linear:
  tile-<name>.png     R the under layer's L*/100 (bare wood, the plinth's mortar), G the surface's L*/100 (the paint,
                      the stone, the clay), B breakup (uniform 0..1: paint is lost where the page's loss share + B > 1;
                      elsewhere it breaks dirt and water up), A height, 0.5 + 0.5 * mm / heightMm
  tile-<name>-n.png   the normal from that height, tangent space, OpenGL (+v up), packed with a smoothness offset
                      (finishlib.pack_normal; none here: way A's gloss is the material's)
u runs along the grain (a board's length, a trim's sweep), v across. Fields are made at twice the size and boxed
down, so nothing finer than about two texels survives to shimmer. Each tileable's mean lightness is its material's
(finish.json); the fields only move texels about it. Nothing here claims history: the page carries that.
"""

import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import finishlib as FL  # noqa: E402
from finishlib import HS  # noqa: E402

MM = 0.001
SS = 2  # made at twice the size, boxed down


def args():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    return {argv[i].lstrip("-"): argv[i + 1] for i in range(0, len(argv) - 1, 2)}


class Tile:
    """One tileable's lattice: u along the grain, v across, both 0..1 over `metres`, wrapping."""

    def __init__(self, name, size, metres):
        self.name, self.size, self.m = name, size, metres
        self.n = size * SS
        t = (np.arange(self.n) + 0.5) / self.n
        self.u, self.v = np.meshgrid(t, t)
        self.key = HS.h("finish", "tile", name)

    def cells(self, along, across):
        return max(1, round(self.m / along)), max(1, round(self.m / across))

    def fbm(self, purpose, along, across, octaves=3, gain=0.5):
        return FL.fbm2(self.u, self.v, HS.h(self.key, purpose), self.cells(along, across), octaves, gain)

    def signed(self, purpose, along, across, octaves=3, gain=0.5):
        """A field about 0 with unit spread, so an amplitude reads as the L* or mm it moves."""
        f = self.fbm(purpose, along, across, octaves, gain)
        return (f - f.mean()) / max(f.std(), 1e-9)

    def figure(self, purpose, period, wander, extra=None):
        """Flat-sawn figure: growth rings met by the face at a wandering angle, so bands `period` metres apart
        swell into arches. Returns the latewood's share 0..1, the narrow band of each ring."""
        n = max(1, round(self.m / period))
        w = self.fbm(purpose, 0.5, period * 10, octaves=2)
        phase = self.v * n + wander * (w - 0.5)
        if extra is not None:
            phase = phase + extra
        f = phase - np.floor(phase)
        return FL.smoothstep(0.62, 0.8, f) * (1.0 - FL.smoothstep(0.86, 1.0, f))

    def scatter(self, purpose, per_m2):
        """Seeded sites over the tile (u, v in 0..1), as many as the area holds at `per_m2`."""
        count = max(1, round(per_m2 * self.m * self.m))
        k = HS.h(self.key, purpose)
        return [(HS.unit(HS.h(k, i, "u")), HS.unit(HS.h(k, i, "v")), k, i) for i in range(count)]

    def near(self, cu, cv):
        """Wrapped offsets in metres from a site to every texel: (along, across)."""
        du = (self.u - cu + 0.5) % 1.0 - 0.5
        dv = (self.v - cv + 0.5) % 1.0 - 0.5
        return du * self.m, dv * self.m

    def voronoi(self, purpose, size, across=None):
        """Jittered cells about `size` metres along (and `across` metres across, if given), wrapping: each texel's cell
        id, its offset from the cell's site in metres, and how far it is from the cell's edge (second nearest site
        less the nearest, in metres of `size`)."""
        k = max(1, round(self.m / size))
        kv = k if across is None else max(1, round(self.m / across))
        x, y = self.u * k, self.v * kv
        ix, iy = np.floor(x).astype(np.int64), np.floor(y).astype(np.int64)
        key = HS.h(self.key, purpose)
        best = np.full(x.shape, 9.0)
        second = np.full(x.shape, 9.0)
        bid = np.zeros(x.shape, np.int64)
        ox = np.zeros(x.shape)
        oy = np.zeros(x.shape)
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                cx, cy = ix + dx, iy + dy
                wx, wy = cx % k, cy % kv
                px = cx + 0.15 + 0.7 * FL.unit(key, wx, wy, 0)
                py = cy + 0.15 + 0.7 * FL.unit(key, wx, wy, 1)
                d = np.hypot(x - px, y - py)
                closer = d < best
                second = np.where(closer, best, np.minimum(second, d))
                bid = np.where(closer, wy * k + wx, bid)
                ox = np.where(closer, x - px, ox)
                oy = np.where(closer, y - py, oy)
                best = np.where(closer, d, best)
        s = self.m / k
        return bid, ox * s, oy * s, (second - best) * s, key

    def down(self, a):
        n = self.size
        return a.reshape(n, SS, n, SS).mean(axis=(1, 3))

    def save(self, out, under, surface, breakup, height_mm, range_mm, extra_height_m=None):
        """Box down, keep the means where finish.json put them, and write the tile and its normal."""
        under, surface, h = self.down(under), self.down(surface), self.down(height_mm)
        b = FL.equalise(self.down(breakup))
        rgba = np.stack([under / 100.0, surface / 100.0, b, 0.5 + 0.5 * np.clip(h / range_mm, -1, 1)], axis=-1)
        FL.write(os.path.join(out, f"tile-{self.name}.png"), rgba)
        hm = h * MM if extra_height_m is None else h * MM + extra_height_m
        nrm = FL.normal_from_height(hm, self.m / self.size, wrap=True) * 2.0 - 1.0
        FL.write(os.path.join(out, f"tile-{self.name}-n.png"), FL.pack_normal(nrm))
        print(f"[tiles] {self.name}: under {under.mean():.1f}±{under.std():.1f} surface {surface.mean():.1f}"
              f"±{surface.std():.1f} height ±{h.std():.3f} mm")
        return b


def painted(t, spec, Lp, Lu):
    """Old paint on pine: the figure telegraphs through as relief; bare, the weathered wood shows it in value."""
    fig = t.figure("figure", spec["figureMm"] * MM, spec["wander"])
    streak = t.signed("streak", 0.25, 0.008, octaves=2)
    cloud = t.signed("cloud", 0.6, 0.2, octaves=2)
    under = Lu - spec["underFigureL"] * (fig - fig.mean()) + spec["underStreakL"] * 0.5 * streak + cloud
    brush = t.signed("brush", 0.3, 0.012, octaves=2)
    paint = Lp + spec["paintBrushL"] * 0.5 * brush + spec["paintCloudL"] * cloud
    height = spec["figureReliefMm"] * fig + spec["brushReliefMm"] * brush * 0.5
    # old oil paint cracks along the grain and across it into plates, and a plate comes off whole: each plate its
    # own seeded share, met by a ragged edge and grouped by the patch it sits in
    fa, fc = (v * MM for v in spec["flakeMm"])
    pa, pc = (v * MM for v in spec["patchMm"])
    la, lc = (v * MM for v in spec["plateMm"])
    bid, _, _, _, key = t.voronoi("plates", la, lc)
    plate = FL.unit(key, bid, 7)
    pw, fw = spec["plateWeight"], spec["flakeWeight"]
    breakup = (pw * plate + fw * t.fbm("flake", fa, fc) + (1.0 - pw - fw) * t.fbm("patch", pa, pc)
               + spec["figureInBreakup"] * fig)
    return under, paint, breakup, height - height.mean()


def painted_board(t, spec, mat, out):
    under, paint, breakup, height = painted(t, spec, mat["paint"]["L"], mat["under"]["L"])
    t.save(out, under, paint, breakup, height, spec["heightMm"])


def trim_sheet(t, spec, mat, ts, out):
    """The trim sheet: the painted board's surface in strips across v, flat in the near half; in the street half
    each strip's edges fall at 45 degrees over its member's chamfer, and its paint wears a little more there."""
    under, paint, breakup, height = painted(t, spec, mat["paint"]["L"], mat["under"]["L"])
    bevel, wear = FL.trim_bevels(t.v * t.m, ts)
    breakup = breakup + spec["bevelBreakup"] * wear
    t.save(out, under, paint, breakup, height, spec["heightMm"], extra_height_m=t.down(bevel))


def sheet(t, spec, mat, out):
    """The 1986 boarding: rotary-cut veneer, its wild wide figure, and checks opened along the grain by weather."""
    L = mat["paint"]["L"]
    fig = t.figure("figure", spec["figureMm"] * MM, spec["wander"])
    cloud = t.signed("cloud", 0.4, 0.15, octaves=2)
    value = L - spec["figureL"] * (fig - fig.mean()) + spec["cloudL"] * cloud
    height = spec["figureReliefMm"] * fig
    ck = spec["checks"]
    lo, hi = (v * MM for v in ck["lengthMm"])
    for cu, cv, k, i in t.scatter("checks", ck["perM2"]):
        length = lo + (hi - lo) * HS.unit(HS.h(k, i, "len"))
        width = ck["widthMm"] * MM * (0.6 + 0.8 * HS.unit(HS.h(k, i, "w")))
        da, dc = t.near(cu, cv)
        along = np.clip(1.0 - (2.0 * da / length) ** 2, 0.0, 1.0)
        line = np.exp(-(dc / width) ** 2) * along
        value = value - ck["L"] * line
        height = height - ck["depthMm"] * line
    # how water soaks into it: unevenly, in a mottle of fibres and glue as well as in broad patches
    mo = spec["mottle"]
    breakup = (1.0 - mo["weight"]) * t.fbm("breakup", 0.12, 0.05) + mo["weight"] * t.fbm("mottle", mo["mm"][0] * MM,
                                                                                        mo["mm"][1] * MM)
    t.save(out, value, value, breakup, height - height.mean(), spec["heightMm"])


def batten(t, spec, mat, out):
    """Rough-sawn battens: the saw's marks across the face, the figure, and knots the rings bend around."""
    L = mat["paint"]["L"]
    kn = spec["knots"]
    lo, hi = (v * MM for v in kn["sizeMm"])
    bend = np.zeros_like(t.u)
    knot = np.zeros_like(t.u)
    for cu, cv, k, i in t.scatter("knots", kn["perM2"]):
        r = lo + (hi - lo) * HS.unit(HS.h(k, i, "size"))
        da, dc = t.near(cu, cv)
        q = (da / (0.75 * r)) ** 2 + (dc / (0.5 * r)) ** 2
        knot = np.maximum(knot, FL.smoothstep(1.2, 0.6, q))
        bend = bend + 1.6 * np.exp(-q / 5.0)
    fig = t.figure("figure", spec["figureMm"] * MM, spec["wander"], extra=bend)
    streak = t.signed("streak", 0.2, 0.008, octaves=2)
    cloud = t.signed("cloud", 0.5, 0.12, octaves=2)
    wobble = t.fbm("saw-wobble", 0.05, 0.4, octaves=2)
    n = max(1, round(t.m / (spec["sawMm"] * MM)))
    ph = (t.u + spec["sawSlant"] * t.v) * n + 1.5 * (wobble - 0.5)
    saw = 1.0 - 2.0 * np.abs(ph - np.floor(ph) - 0.5)
    sawamp = t.fbm("saw-amp", 0.3, 0.05, octaves=2)
    value = (L - spec["figureL"] * (fig - fig.mean()) + spec["streakL"] * 0.5 * streak + cloud
             - kn["L"] * knot)
    height = (spec["figureReliefMm"] * fig + spec["sawReliefMm"] * saw * sawamp + kn["reliefMm"] * knot)
    breakup = t.fbm("breakup", 0.1, 0.03) + 0.2 * fig
    t.save(out, value, value, breakup, height - height.mean(), spec["heightMm"])


def stone(t, spec, mat, out):
    """The plinth's fieldstone: a split face that undulates and breaks in soft cleavage steps, mottled by its
    minerals at a few centimetres; the mortar sandy."""
    m = spec["undulationMm"] * MM
    base = t.signed("face", m, m, octaves=4, gain=0.55)
    k = 1.0 / spec["stepEvery"]
    ph = base * k
    terr = (np.floor(ph) + FL.smoothstep(0.75, 1.0, ph - np.floor(ph))) / k
    form = (1.0 - spec["terrace"]) * base + spec["terrace"] * terr
    height = spec["reliefMm"] * form
    mo = spec["mottleMm"] * MM
    mottle = t.signed("mottle", mo, mo, octaves=3)
    value = mat["paint"]["L"] + spec["mottleL"] * 0.5 * mottle + spec["formL"] * 0.5 * base
    mortar = mat["under"]["L"] + spec["mortarL"] * t.signed("mortar", spec["mortarMm"] * MM, spec["mortarMm"] * MM)
    breakup = t.fbm("breakup", 0.08, 0.08) + 0.15 * (base - base.min()) / np.ptp(base)
    t.save(out, mortar, value, breakup, height - height.mean(), spec["heightMm"])


def clay_tile(t, spec, mat, out):
    """Old pantiles: fired clay mottled by the kiln, sand-faced, gently uneven."""
    m = spec["mottleMm"] * MM
    value = mat["paint"]["L"] + spec["mottleL"] * 0.5 * t.signed("mottle", m, m)
    r = spec["reliefScaleMm"] * MM
    height = spec["reliefMm"] * t.signed("relief", r, r, octaves=2)
    breakup = t.fbm("breakup", 0.06, 0.06)
    t.save(out, value, value, breakup, height, spec["heightMm"])


def zinc(t, spec, mat, out):
    """Weathered zinc: a dull patina mottled in clouds, faint streaks along the rolled sheet, soft dents."""
    m = spec["mottleMm"] * MM
    value = (mat["paint"]["L"] + spec["mottleL"] * 0.5 * t.signed("mottle", m, m)
             + spec["streakL"] * 0.5 * t.signed("streak", 0.6, 0.025, octaves=2))
    d = spec["dentMm"] * MM
    height = spec["reliefMm"] * t.signed("dents", d, d, octaves=2)
    breakup = t.fbm("breakup", 0.08, 0.04)
    t.save(out, value, value, breakup, height, spec["heightMm"])


def main():
    a = args()
    here = os.path.dirname(os.path.abspath(__file__))
    out = os.path.join(os.path.abspath(a["cache"]), "out")
    spec = json.load(open(os.path.join(here, "finish.json")))
    corner = json.load(open(os.path.join(here, "corner.json")))
    size, metres = corner["tileable"]["size"], corner["tileable"]["metres"]
    ts = corner["trimSheet"]
    M, T = spec["materials"], spec["tiles"]
    only = set(a["only"].split(",")) if "only" in a else None
    jobs = [
        ("painted-board", lambda t: painted_board(t, T["painted-board"], M["cladding"], out)),
        ("trim-sheet", lambda t: trim_sheet(t, T["trim-sheet"], M["trims"], ts, out)),
        ("sheet", lambda t: sheet(t, T["sheet"], M["sheet"], out)),
        ("batten", lambda t: batten(t, T["batten"], M["batten"], out)),
        ("stone", lambda t: stone(t, T["stone"], M["stone"], out)),
        ("tile", lambda t: clay_tile(t, T["tile"], M["tiles"], out)),
        ("zinc", lambda t: zinc(t, T["zinc"], M["zinc"], out)),
    ]
    for name, job in jobs:
        if only and name not in only:
            continue
        job(Tile(name, ts["size"] if name == "trim-sheet" else size, ts["metres"] if name == "trim-sheet" else metres))
    print(f"[tiles] wrote {out}")


main()
