"""The slaty rock's face patches (SN6 in reviews/lt1/port/2b/design.md; docs/research/stone.md, How stone is built and
laid, In short 6): the shared sculpted faces a stone's working picks from by its seed, made once by the rules of how
the town's phyllite breaks, never as generic noise. What each rule answers is in reviews/lt1/port/2b/r2a/patches.md
(version 3: the second version's split faces read as ruled paper, so the ledges now wander, swell and space unevenly).

Phyllite is laminated: it parts along its foliation into leaves (laminae) a centimetre to a hand thick, each a little
different in make and tone, and breaks across them. So the two workings show two different faces:

- **The split face** (a wall stone's front, a step's riser): a section across the foliation, the stone lying on its
  natural bed, so the laminae run along u. A patch has one to three ledges, where a lamina broke back and the one
  above stands proud: a rounded lit arris over one broken shadowed edge, never two creases close together. Most
  faces have one major ledge, a line at every distance, and the rest minor, which fade whole by 12 m (the finest
  marks fade first). Their spacing is uneven (a close pair, then a broad plain face), and differs from patch to
  patch. Between them the face is a few bands, each its own broken plane leaning a degree or so, meeting its
  neighbours in a fold (a ridge or a valley, never a step). Every boundary follows its own gently curving trace, a
  few degrees off the patch's axis at most and closing across the seam, so the bands pinch and swell and no two
  lines run parallel; they never cross or touch. A ledge runs right across the patch (on a stone it meets the
  face's edges at both ends; a line that starts or ends mid-face floats, Øystein), and its depth swells and thins
  along its run, never below a floor that keeps its edges whole wherever its deepest is a line. Across the bands
  the fracture runs in broad planar facets: corners scattered over the patch, each a millimetre or two in or out,
  joined into triangles, so the folds between them fall in no rows or columns. Within each band a fine planar
  tooth, faint (the finest marks fade first). Value: fine laminae a shade lighter or darker, following the bands as
  they pinch and swell; each band a shade its own; a soft mottle; nothing plucked, nothing outlined.
- **The bed face** (a tread's or coping's top): the foliation plane itself, broad and nearly flat. Its read is a broad
  gentle undulation (a wavelength of about 130 to 340 mm, 1 to 2 mm high, longer one way than the other on some) and
  its value, and one scarp, where the top lamina parted: it runs right across the patch on a gently curving trace,
  faces down-dip only, its depth swelling and thinning above a floor, and the next lamina rises back from it over the
  rest of the patch so the face tiles; its fresher parting is a little rougher and a shade darker, fading down-dip.

Restraint (SN4, SN5, SN7): no line on screen that is not an edge of the form running to another edge; edges drawn by
light, never by a dark line; in grey light a face holds within about 2 L* (The Witness's final wall); no broken edge
narrower than 16 mm on a split face or 10 mm on a bed face (narrower, a step's shadow is a drawn stroke at 5 m); no
specks; value in one narrow band, hue left to the stone. Everything that reads as history (wear, polish, lichen,
stains) is the facts' and the shader's, never painted here. blender/tools/patch_sheet.py measures all of it.

Each patch is N x N texels at 1 mm, seamless on the torus, and has three maps (cache/stone/patches/, not tracked):
- `slate-<name>-height.png`: 16-bit grey, millimetres = v / 65535 * 32 - 16, the patch's mean at 0, + out of the face;
- `slate-<name>-normal.png`: 16-bit RGB, tangent space, u right, v up the image (green up, as Unity and OpenGL),
  (n + 1) / 2;
- `slate-<name>-value.png`: 16-bit grey, the face value's multiplier = 0.75 + 0.5 * v / 65535 (1.0 at 32767.5).
Their pixel hashes are in patches.manifest.json beside this file. A stone picks a patch, an offset and a turn by its
seed: a split patch only by a half turn or a mirror in u (its foliation stays along the bed), a bed patch by any turn.

Seeds: every draw comes from the hash spec (blender/resolver/hashing.py), keyed (worldSeed, "stone/slate/patch/<name>",
purpose); lattices and corners hash (..., i, j, n) the same way, vectorised here and checked against the scalar spec.
Integers choose (how many, which class, where); floats from the hash only shape texels. The number of ledges in each
split patch, and how many of them are major, is the set's design (LEDGES), not a draw: four patches are too few to
leave their spread to chance.

    python patches.py build [--out DIR]      write the maps and the manifest
    python patches.py check [--out DIR]      rebuild in memory and compare the pixel hashes with the manifest (exit 1)

R2a's A/B arms (ARMS) are built and checked beside the patches, on the four split faces only: `slate-split-N-facets2-*`
(facet_gain 2.0) and `slate-split-N-nominor-*` (minor=False, the major ledge alone), under "arms" in the manifest.

Run with Blender's Python (numpy): /Applications/Blender.app/Contents/Resources/5.2/python/bin/python3.13
"""

import hashlib
import json
import math
import os
import struct
import sys
import zlib

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "blender", "resolver"))
import hashing as HS  # noqa: E402  (the one hash spec)

TOOL = "patches 3"
PACK = "stavanger-1989"
N = 1024                      # texels a side, 1 mm each
H_LO, H_HI = -16.0, 16.0      # the height map's range, mm
V_LO, V_HI = 0.75, 1.25       # the value map's range, as a multiplier on the face's one value
OUT = os.path.join(ROOT, "cache", "stone", "patches")
MANIFEST = os.path.join(HERE, "patches.manifest.json")
PATCHES = ("split-0", "split-1", "split-2", "split-3", "bed-0", "bed-1")
# R2a's A/B arms on the split faces (reviews/lt1/port/2b/r2a/stones/plan.md, The patch array): slices 6 to 9 are facets
# x2 on split-0..3, slices 10 to 13 the minor ledges off, as (suffix, make's keyword arguments).
ARMS = (("facets2", {"facet_gain": 2.0}), ("nominor", {"minor": False}))

# -- the rules' constants (mm unless said) -----------------------------------------------------------------------------

# Split face: the ledges and their spacing. The second version's ledges were straight, level, of one depth and nearly
# evenly spaced, and in a 2 x 2 tiling the faces read as ruled paper (the coordinator, 22 October, 22:10).
LEDGES = {"split-0": (2, 1), "split-1": (3, 1), "split-2": (1, 1), "split-3": (2, 0)}   # the set: (ledges, of
                              # them major), so no two patches share a rhythm; which is major, where each lies, its
                              # trace and its depths are drawn
LEDGE_GAP = ((70, 110, 2), (130, 260, 3), (300, 560, 2))   # the gaps between ledges: classes (lo, hi, weight) of
                              # relative weights, then scaled to the patch, so a close pair sits beside a broad face
LEDGE_GAP_MIN = 70            # no two ledges closer at rest (with their traces, never under TRACE_GAP_MIN)
LEDGE_UNEVEN = 2.0            # the widest gap at least this times the narrowest, or the gaps are drawn again: never even
SOFT_PER_GAP = (0, 2)         # band boundaries with no step (soft folds) inside each gap between ledges ...
SOFT_BAND = 150               # ... one for each this much of the gap past the first, at most SOFT_PER_GAP[1]
BAND_WEIGHT = (60, 140)       # the bands' relative thicknesses within a gap
WANDER_MM = (1, 3)            # the foliation's common wander along u (3 cycles a patch)
TRACE_CYCLES = (1, 2, 3)      # a boundary's trace: whole cycles a patch (wavelengths N, N/2, N/3), so it closes
                              # across the u seam (a straight line at a few degrees cannot)
TRACE_SLOPE = (40, 75)        # tenths of a degree: a ledge's trace at its steepest, off the patch's axis
SOFT_SLOPE = (15, 35)         # tenths of a degree: a soft boundary's trace at its steepest
TRACE_GAP_MIN = 45            # no two boundaries ever come closer than this (traces scaled down if they would)
BAND_NODE = 15                # tenths of a mm: a boundary's height in or out of the face, so a band leans by the
                              # difference of its two boundaries' (at most 3 mm across it: a degree or two on most)
BAND_COME = (0.2, 3)          # a boundary's height comes and goes along u: from this share to all, over 3 cycles
BAND_BLEND = 50               # mm: two bands' planes meet in a soft fold this wide, never a crease

# Split face: the facets. The second version's bent, sheared lattice of corners left rows of similar crescent folds
# (fault 2): every row of cells had the same size and the same bend. Rows of corners zipped into triangles left
# slivers in diagonal rows. Now the corners are thrown at random and kept where no other is near (each its own reach,
# so the facets come in several sizes), and joined by the Delaunay triangulation on the torus: no rows, no columns,
# no slivers, and nothing repeats inside the patch.
FACET_SITE = ((80, 2), (110, 3), (150, 1))   # a corner's reach across the foliation (mm) by class (weights); two
                              # corners keep apart by the mean of their reaches ...
FACET_ASPECT = (5, 3)         # ... and along the foliation by 5/3 of it, so the facets lie longer along u
FACET_TRIES = 3000            # corners thrown (whole millimetres), each kept or not by its distance to those kept
FACET_AMP = (16, 28)          # tenths of a mm: each corner in or out of the face by up to this (drawn a patch), so
                              # each triangle between is a plane tilted a degree or two, meeting the next in a fold
                              # with no step; more and the face passes about 2 L* in grey light (The Witness)
FACET_SOFT = 7.0              # mm: the folds rounded over this (a Gaussian), never a knife line
FACET_SHARE = {1: 100, 2: 100, 3: 70}   # percent of the facets' drawn amplitude by the face's number of ledges: a
                              # face's light is shared, so a face of three ledges has calmer facets between them (at
                              # full amplitude it held about 2.3 L* at 5 m; SN7)

# Split face: a ledge's profile and its depth along its run.
STEP_MAJOR = (55, 68)         # tenths of a mm: a major ledge's depth where it swells most, never past 8 mm (deeper
                              # facets are the mesh's, SN4); a line at 1, 5 and 12 m ...
STEP_MINOR = (26, 30)         # ... and a minor ledge's, a line at 1 and 5 m that fades whole by 12 m (the finest marks
                              # fade first): a face's ledges are one or none major and the rest minor, never all alike
STEP_FLOOR = (58, 66)         # percent of its most: its depth where it thins most, never less ...
STEP_FLOOR_MAJOR = 40         # ... and never under this on a major ledge (tenths of a mm), nor under STEP_FLOOR_MIN on a
STEP_FLOOR_MIN = 15           # minor: a ledge's thinnest stretch keeps its edge whole at every distance where its
                              # deepest is a line (a fixed floor of 2.2 to 3 mm broke at 12 m under swells of 6 to 8 mm;
                              # a ledge between, 4 to 5 mm, was a line at 12 m in some stretches and not in others)
SWELL_CYCLES = (2, 4)         # its depth swells this many times a patch ...
SWELL_POW = 1.4               # ... the swells a little narrower than the thin runs between
STEP_ARRIS = (5, 8)           # tenths of the break's width: the step's top edge rolls back over this, a rounded arris
STEP_ARRIS_DROP = (60, 80)    # percent of the step's height it rolls back by, so steeply that the narrow lit edge
                              # weighs as much as the broad shadow (a lit slope gains fewer L* than a dark one loses):
                              # the step reads as a ledge, lit over shadowed, never as a dark groove
STEP_LEAN = (35, 60)          # percent of the band above (at least 60 mm, at most 70% of its narrowest): the rest of
                              # the step's height leans back into the face over this
STEP_BEVEL = (35, 45)         # tenths: a step's broken edge, its width over its height ...
STEP_W = (16.0, 26.0)         # ... never narrower than 16 mm (narrower, a shallow step's shadow was a line under 2 px
                              # wide at 5 m) nor wider than 26 (wider, where a ledge swells its shadow was a band past
                              # 5 px at 5 m, no longer a line, and the ledge read as ending there)
STEP_ARRIS_MAX = 14.0         # mm: the lit arris never wider, so where a ledge swells it grows brighter, not broader
STEP_IN = 3.0                 # a step's edge wanders up to this far above its boundary, at fine wavelengths
BEVEL_VARY = 0.3              # and breaks this much wider or narrower along its run
ROUND = (2.0, 0.3)            # a broken edge's corners rounded over 2 texels or 0.3 of its width, the larger, so no
                              # crease is a line (at 1.5 texels, the foot of a steep edge was a dark line 1 to 2 px)

# Split face: tooth and value.
TOOTH_CELL = (18, 7)          # the tooth's facets, along u and across: longer along the foliation
TOOTH_TILT = (0.007, 0.011)   # their tilts' half-ranges along u and across (slopes)
TOOTH_LIFT = 0.10             # their offsets' half-range
TOOTH_BLEND = 0.30            # the facets' soft border (a soft-min temperature in cell units squared)
TOOTH_GAIN = ((0.6, 1), (0.8, 2), (1.0, 1))   # a band's tooth: finer, usual, coarser (gain, weight)
FOLIA = ((3, 8, 3), (9, 24, 4), (25, 60, 2))  # the fine laminae, for value only: thickness classes (lo, hi, weight)
FOLIA_TONE = 0.009            # a fine lamina a shade lighter or darker: "laminated" where the relief is calm
FOLIA_SOFT = 3                # mm: their tones meet over this, so no lamina is a drawn line
BAND_TONE = 0.008             # a band a shade lighter or darker
MOTTLE = 0.005                # a very soft broad mottle

# Bed face. The main read is a broad gentle undulation and the value, and one scarp facing down-dip and running right
# across (the first version's flake scars were outlined all round, like ink, and a scar's feathered sides were lines
# ending mid-face; the second version's bed-1 had no scarp and read as plaster).
UNDULATION = ((3, 8), (5, 8), (10, 20))   # its lattice along u and across (cells a patch: wavelengths of about 130
                                          # to 340 mm, longer one way on some) and its amplitude in tenths of a mm
SCARP_DEPTH = (24, 30)        # tenths of a mm: the top lamina's edge, where it parted, where it swells most ...
SCARP_FLOOR = (70, 80)        # ... and where it thins most, in percent of that, never under STEP_FLOOR_MIN: a scarp
                              # facing the light gains fewer L* than one facing away loses, and its light turns with its
                              # trace, so its thinnest must stay a line at 5 m (at 1 to 1.6 mm it broke there)
SCARP_FRESH = (60, 140)       # mm: the lower lamina's fresher parting, a shade darker, fading down-dip over this
BED_BEVEL = (40, 60, 10.0, 20.0)  # a scarp's break: factor on its depth (tenths), least and most width (at 6
                                 # to 12 mm the scarps read as thin strokes at 5 m)
EDGE_WANDER = (3.0, 1.0)      # a scarp's fine wander, mm, at about 128 and 43 mm, on top of its trace (at 6
                              # and 2 its edge turned up to 18 degrees and its light came and went)
SCAR_TONE = 0.03              # a scarp's fresher parting, a shade darker
TOOTH_BED = (0.008, 0.022)    # the tooth's slopes on the old cleavage face and on the fresher parting


# -- the hash spec, vectorised --------------------------------------------------------------------------------------

_G = np.uint64(HS.GAMMA)
_C1 = np.uint64(0xBF58476D1CE4E5B9)
_C2 = np.uint64(0x94D049BB133111EB)


def _vmix(z):
    with np.errstate(over="ignore"):
        z = z + _G
        z = (z ^ (z >> np.uint64(30))) * _C1
        z = (z ^ (z >> np.uint64(27))) * _C2
    return z ^ (z >> np.uint64(31))


def vkey(prefix, *ints):
    """HS.h(*key, *ints) for arrays of non-negative ints, where prefix = HS.h(*key)."""
    shape = np.broadcast(*[np.asarray(a) for a in ints]).shape if ints else ()
    acc = np.full(shape, prefix, dtype=np.uint64)
    for a in ints:
        acc = _vmix(acc ^ np.asarray(a, dtype=np.int64).astype(np.uint64))
    return acc


def vunit(key):
    return (key >> np.uint64(11)).astype(np.float64) / float(1 << 53)


def selftest_hash():
    """The vectorised lattice hash equals the scalar spec."""
    pre = HS.h(1989, "stone/slate/patch/selftest", "lattice")
    for i, j, n in ((0, 0, 0), (3, 7, 2), (63, 127, 4), (1023, 5, 1)):
        a = int(vkey(pre, np.array(i), np.array(j), np.array(n)))
        b = HS.h(1989, "stone/slate/patch/selftest", "lattice", i, j, n)
        assert a == b, (i, j, n, a, b)


# -- seamless fields ----------------------------------------------------------------------------------------------------

def value_noise(prefix, px, py):
    """A seamless field in [-1, 1] on N x N: hashed values on a px by py lattice (wrapped), quintic between."""
    I, J = np.meshgrid(np.arange(px), np.arange(py), indexing="xy")
    lat = vunit(vkey(prefix, I, J)) * 2.0 - 1.0                      # (py, px)
    x = np.arange(N) * (px / N)
    y = np.arange(N) * (py / N)
    i0, j0 = np.floor(x).astype(int), np.floor(y).astype(int)
    fx, fy = x - i0, y - j0
    fx = fx * fx * fx * (fx * (fx * 6 - 15) + 10)
    fy = fy * fy * fy * (fy * (fy * 6 - 15) + 10)
    i1, j1 = (i0 + 1) % px, (j0 + 1) % py
    i0, j0 = i0 % px, j0 % py
    a = lat[np.ix_(j0, i0)] * (1 - fx) + lat[np.ix_(j0, i1)] * fx
    b = lat[np.ix_(j1, i0)] * (1 - fx) + lat[np.ix_(j1, i1)] * fx
    return a * (1 - fy)[:, None] + b * fy[:, None]


def wander(st, cycles, beta=1.0):
    """A seamless 1-D wander along u, peak 1: a few cosines of whole cycles a patch, falling as 1 / cycles^beta."""
    u = np.arange(N, dtype=np.float64)
    out = np.zeros(N)
    for m in range(1, cycles + 1):
        a = st.uniform(0.4, 1.0) / m ** beta
        ph = 2.0 * math.pi * st.randrange(N) / N
        out += a * np.cos(2.0 * math.pi * m * u / N + ph)
    return out / max(np.abs(out).max(), 1e-9)


def trace(st, slope_deg):
    """A boundary's trace along u: v as a smooth function, periodic in u (whole cycles a patch, so it closes across the
    seam), its shape its own (each cycle's weight and phase drawn), scaled so that its steepest local slope is
    slope_deg off the patch's axis. A straight line at an angle cannot close at a few degrees; this can."""
    u = np.arange(N, dtype=np.float64)
    v = np.zeros(N)
    dv = np.zeros(N)
    for m in TRACE_CYCLES:
        a = st.uniform(0.2, 1.0) / m ** 1.2     # the longer cycles carry a little more of the slope, so it shows
        ph = 2.0 * math.pi * st.randrange(N) / N
        k = 2.0 * math.pi * m / N
        v += a * np.cos(k * u + ph)
        dv -= a * k * np.sin(k * u + ph)
    return v * math.tan(math.radians(slope_deg)) / max(np.abs(dv).max(), 1e-12)


def rnd(w):
    """A break's corner rounding, in units of its width w: ROUND[0] texels or ROUND[1] of the width, the larger."""
    return np.maximum(ROUND[0] / w, ROUND[1])


def ramp(t, r):
    """0 at t = 0, rising along a straight break to 1 by t = 1, its two corners rounded over r (all in units of the
    break's width) by a soft-plus, whose slope is one broad bump across the break, never a narrow core; continuous in
    value at t = 0, so a break meets the flat beside it in a soft crease, never a jump. (A C1 ramp with quadratic
    corners concentrated the slope in a straight core and its shaded side read as a dark line; so did any power on
    the profile.)"""
    def sp(z):
        return 0.5 * (z + np.sqrt(z * z + r * r))
    c0 = sp(0.0) - sp(-1.0)
    return (sp(t) - sp(t - 1.0) - c0) / (1.0 - c0)


def _lattice(prefix, cell):
    """A jittered (anisotropic) grid with a whole number of cells a patch, so what is built on it wraps: its size, its
    cells' width and height, and five hashed units per cell."""
    px, py = max(1, round(N / cell[0])), max(1, round(N / cell[1]))
    I, J = np.meshgrid(np.arange(px), np.arange(py), indexing="xy")
    k = [vunit(vkey(prefix, I, J, np.full_like(I, n))) for n in range(5)]
    return px, py, N / px, N / py, k


def _blend_planes(px, py, cw, ch, k, gx, gy, c0, blend, reach=1):
    """A plane per cell, through its jittered site, blended softly into its neighbours (a soft-min on distance), so the
    planes meet in soft folds. Cells up to `reach` away take part: a broad blend needs 2, or the lattice's cell
    boundaries show as hairlines where the set of neighbours changes."""
    jx, jy = 0.15 + 0.7 * k[0], 0.15 + 0.7 * k[1]
    out = np.zeros((N, N))
    xs = np.arange(N, dtype=np.float64)
    for r0 in range(0, N, 128):
        ys = np.arange(r0, r0 + 128, dtype=np.float64)
        X, Y = np.meshgrid(xs, ys, indexing="xy")
        ci, cj = np.floor(X / cw).astype(int), np.floor(Y / ch).astype(int)
        num = np.zeros_like(X)
        den = np.zeros_like(X)
        d2s, ps = [], []
        for dj in range(-reach, reach + 1):
            for di in range(-reach, reach + 1):
                ii, jj = ci + di, cj + dj
                wi, wj = ii % px, jj % py
                sx = (ii + jx[wj, wi]) * cw
                sy = (jj + jy[wj, wi]) * ch
                dx, dy = X - sx, Y - sy
                d2s.append((dx / cw) ** 2 + (dy / ch) ** 2)
                ps.append(c0[wj, wi] + gx[wj, wi] * dx + gy[wj, wi] * dy)
        dmin = np.minimum.reduce(d2s)
        for d2, p in zip(d2s, ps):
            w = np.exp(-(d2 - dmin) / blend)
            num += w * p
            den += w
        out[r0:r0 + 128] = num / den
    return out


def tooth(prefix, cell, tilt, lift, blend):
    """The fine planar tooth: small facets, their slopes up to tilt (along u, across) either way."""
    px, py, cw, ch, k = _lattice(prefix, cell)
    gx, gy = (2 * k[2] - 1) * tilt[0], (2 * k[3] - 1) * tilt[1]
    return _blend_planes(px, py, cw, ch, k, gx, gy, (2 * k[4] - 1) * lift, blend)


def soften(a, sigma):
    """A periodic Gaussian blur (sigma in texels), by FFT on the torus."""
    fr = np.fft.fftfreq(N)
    g = np.exp(-2.0 * (math.pi * sigma) ** 2 * (fr[:, None] ** 2 + fr[None, :] ** 2))
    return np.real(np.fft.ifft2(np.fft.fft2(a) * g))


def _raster(tris):
    """Linear interpolation over triangles on the torus: each (3, 3) array of (u, v, h) corners, unrolled; every texel
    centre (u = column, v = row) lies in one or two (on a shared edge, where both agree)."""
    out = np.full((N, N), np.nan)
    for t in tris:
        u, v, h = t[:, 0], t[:, 1], t[:, 2]
        x0, x1 = int(math.floor(u.min())), int(math.ceil(u.max()))
        y0, y1 = int(math.floor(v.min())), int(math.ceil(v.max()))
        X, Y = np.meshgrid(np.arange(x0, x1 + 1, dtype=np.float64), np.arange(y0, y1 + 1, dtype=np.float64),
                           indexing="xy")
        d = (v[1] - v[2]) * (u[0] - u[2]) + (u[2] - u[1]) * (v[0] - v[2])
        l0 = ((v[1] - v[2]) * (X - u[2]) + (u[2] - u[1]) * (Y - v[2])) / d
        l1 = ((v[2] - v[0]) * (X - u[2]) + (u[0] - u[2]) * (Y - v[2])) / d
        l2 = 1.0 - l0 - l1
        inside = (l0 >= -1e-9) & (l1 >= -1e-9) & (l2 >= -1e-9)
        if not inside.any():
            continue
        ys = Y[inside].astype(int) % N
        xs = X[inside].astype(int) % N
        out[ys, xs] = (l0 * h[0] + l1 * h[1] + l2 * h[2])[inside]
    assert not np.isnan(out).any(), "a texel no triangle covers"
    return out


def _circles(P, T):
    """The circumcircles (centre x, y and radius squared) of triangles T (m, 3) over points P (n, 2)."""
    a, b, c = P[T[:, 0]], P[T[:, 1]], P[T[:, 2]]
    sa, sb, sc = (a * a).sum(1), (b * b).sum(1), (c * c).sum(1)
    d = 2.0 * (a[:, 0] * (b[:, 1] - c[:, 1]) + b[:, 0] * (c[:, 1] - a[:, 1]) + c[:, 0] * (a[:, 1] - b[:, 1]))
    ux = (sa * (b[:, 1] - c[:, 1]) + sb * (c[:, 1] - a[:, 1]) + sc * (a[:, 1] - b[:, 1])) / d
    uy = (sa * (c[:, 0] - b[:, 0]) + sb * (a[:, 0] - c[:, 0]) + sc * (b[:, 0] - a[:, 0])) / d
    return np.stack([ux, uy, (a[:, 0] - ux) ** 2 + (a[:, 1] - uy) ** 2], axis=1)


def delaunay(P):
    """The Delaunay triangles of points P (n, 2), as (m, 3) indices: Bowyer and Watson's insertion, in the points'
    order, inside a super-triangle that is dropped at the end."""
    n = len(P)
    lo, hi = P.min(0), P.max(0)
    c, s = (lo + hi) / 2.0, float((hi - lo).max()) * 20.0
    Q = np.vstack([P, [[c[0] - s, c[1] - s], [c[0] + s, c[1] - s], [c[0], c[1] + s]]])
    T = np.array([[n, n + 1, n + 2]], dtype=np.int64)
    C = _circles(Q, T)
    for i in range(n):
        x, y = Q[i]
        bad = (C[:, 0] - x) ** 2 + (C[:, 1] - y) ** 2 < C[:, 2]
        E = np.sort(T[bad][:, [0, 1, 1, 2, 2, 0]].reshape(-1, 2), axis=1)
        key, cnt = np.unique(E[:, 0] * (n + 3) + E[:, 1], return_counts=True)
        rim = key[cnt == 1]                                             # the hole's boundary: edges of one bad triangle
        new = np.stack([rim // (n + 3), rim % (n + 3), np.full(len(rim), i)], axis=1)
        T = np.vstack([T[~bad], new])
        C = np.vstack([C[~bad], _circles(Q, new)])
    return T[(T < n).all(axis=1)]


def facet_sites(seed, pid):
    """The facets' corners: thrown at whole millimetres from the patch's stream, each with a reach drawn by class,
    kept where every corner already kept lies at least the mean of their two reaches away (across the foliation;
    along it, FACET_ASPECT times that), on the torus. Integers throughout, so the set is exact."""
    st = HS.Stream(seed, pid, "facet sites")
    au, av = FACET_ASPECT[1], FACET_ASPECT[0]                          # u counts 3/5 as much as v
    U, V, R = (np.zeros(0, dtype=np.int64) for _ in range(3))
    for _ in range(FACET_TRIES):
        u, v = st.randrange(N), st.randrange(N)
        r = FACET_SITE[st.weighted([(i, w) for i, (_, w) in enumerate(FACET_SITE)])][0]
        du = np.abs(U - u)
        dv = np.abs(V - v)
        du, dv = np.minimum(du, N - du), np.minimum(dv, N - dv)
        if np.all(4 * ((au * du) ** 2 + (av * dv) ** 2) >= av * av * (R + r) ** 2):
            U, V, R = np.append(U, u), np.append(V, v), np.append(R, r)
    return U, V, R


def facets(seed, pid, amp, info=None):
    """The fracture's broad facets: corners scattered over the patch, each a little in or out of the face, joined into
    triangles, so every triangle is a plane with its own tilt and the planes meet in folds with no step. The corners
    are thrown at random and kept apart by their own reaches (facet_sites), and joined by the Delaunay triangulation of
    the torus (the patch and its eight neighbours' copies, measured with u shortened by FACET_ASPECT so the facets lie
    along the foliation; each triangle kept once, in the tile its centroid falls in): no rows, no columns, no slivers,
    no repeat inside the patch (the second version's lattice left rows of similar crescent folds). The folds are
    rounded."""
    U, V, R = facet_sites(seed, pid)
    hv = (2.0 * vunit(vkey(HS.h(seed, pid, "facet heights"), U, V)) - 1.0) * amp
    k = len(U)
    du = np.repeat(np.array([-1, 0, 1, -1, 0, 1, -1, 0, 1]) * N, k)
    dv = np.repeat(np.array([-1, -1, -1, 0, 0, 0, 1, 1, 1]) * N, k)
    Pu, Pv = np.tile(U, 9) + du, np.tile(V, 9) + dv
    P = np.stack([Pu * FACET_ASPECT[1] / FACET_ASPECT[0], Pv], axis=1).astype(np.float64)
    T = delaunay(P)
    cu, cv = Pu[T].mean(axis=1), Pv[T].mean(axis=1)
    T = T[(cu >= 0) & (cu < N) & (cv >= 0) & (cv < N)]
    tris = [np.stack([Pu[t], Pv[t], np.tile(hv, 9)[t]], axis=1).astype(np.float64) for t in T]
    if info is not None:
        reach = {str(r): int((R == r).sum()) for r, _w in FACET_SITE}
        info.update(corners=int(k), corners_by_reach_mm=reach, triangles=len(tris))
    return soften(_raster(tris), FACET_SOFT)


def smoothstep(z):
    z = np.clip(z, 0.0, 1.0)
    return z * z * (3 - 2 * z)


def wrapd(d):
    """A distance along the torus, into [-N/2, N/2)."""
    return (d + N / 2) % N - N / 2


def box1(a, w):
    """A periodic box mean of width w (odd, texels) along a 1-D array."""
    c = np.cumsum(np.concatenate([a[-(w // 2):], a, a[:w // 2]]))
    c = np.concatenate([[0.0], c])
    return (c[w:] - c[:-w]) / w


# -- the split face ------------------------------------------------------------------------------------------------------

def _ledge_gaps(sp, L):
    """The gaps between L ledges round the patch, whole millimetres summing to N: each from a class of weights, scaled
    to the patch; drawn again (the stream goes on) until no gap is under LEDGE_GAP_MIN and the widest is at least
    LEDGE_UNEVEN times the narrowest, so the ledges never fall evenly."""
    if L == 1:
        return [N]
    for _ in range(64):
        w = []
        for _k in range(L):
            lo, hi, _w = LEDGE_GAP[sp.weighted([(i, wt) for i, (_, _, wt) in enumerate(LEDGE_GAP)])]
            w.append(sp.randint(lo, hi))
        g = [N * x // sum(w) for x in w]
        g[-1] += N - sum(g)
        if min(g) >= LEDGE_GAP_MIN and max(g) >= LEDGE_UNEVEN * min(g):
            return g
    raise AssertionError("no uneven spacing drawn in 64 tries")


def split_patch(seed, name, layers=None, facet_gain=1.0, minor=True):
    """A split face's height (mm) and value multiplier, N x N, and its drawn parameters. With layers (a dict), also its
    facets alone and each boundary's trace and depth along u, for the sheet's measures. facet_gain scales the facets'
    amplitude only (the sheet's A/B on the spread limit; 1 for the patches themselves). minor=False builds only the
    major ledge (R2a's arm, minor ledges off): every draw is made as before, so the rest of the face is the same."""
    pid = f"stone/slate/patch/{name}"
    params = {}
    rows = np.arange(N, dtype=np.float64)[:, None]
    cols = np.arange(N)[None, :]

    # 1. Where the ledges lie: their number is the set's; the gaps between them are drawn uneven, so a close pair
    # sits beside a broad plain face, and no two patches share a rhythm. Inside each gap, a soft band boundary or two
    # (a fold, no step), for each SOFT_BAND of the gap past the first.
    sp = HS.Stream(seed, pid, "spacing")
    L, majors = LEDGES[name]
    gaps = _ledge_gaps(sp, L)
    first = sp.randrange(N)
    Y, ledge = [], []
    y = first
    for g in gaps:
        k = sp.randint(SOFT_PER_GAP[0], max(SOFT_PER_GAP[0], min(SOFT_PER_GAP[1], g // SOFT_BAND - 1)))
        ws = [sp.randint(*BAND_WEIGHT) for _ in range(k + 1)]
        parts = [g * x // sum(ws) for x in ws]
        parts[-1] += g - sum(parts)
        for i, p in enumerate(parts):
            Y.append(y % N)
            ledge.append(i == 0)
            y += p
    n = len(Y)
    order = np.argsort(Y)                                              # boundaries down the image from the first
    Y = np.array(Y, dtype=np.int64)[order]
    ledge = [ledge[i] for i in order]
    t = [int((Y[(k + 1) % n] - Y[k]) % N) for k in range(n)]          # band k: from boundary k down to k + 1, at rest
    params.update(ledges=L, ledge_gaps_mm=[int(g) for g in gaps], bands=n, thickness_mm=t)

    # 2. Where each boundary runs: the foliation's small common wander, and a trace of its own, gently curving and a
    # few degrees off the axis at its steepest (a ledge more than a soft fold), each its own shape; scaled down
    # together if any two neighbours would come closer than TRACE_GAP_MIN.
    sc = HS.Stream(seed, pid, "character")
    shared_amp = sc.randint(*WANDER_MM)
    sb = HS.Stream(seed, pid, "boundaries")
    W = shared_amp * wander(sb, 3)
    slopes = [sb.randint(*(TRACE_SLOPE if ledge[k] else SOFT_SLOPE)) / 10.0 for k in range(n)]
    T = np.stack([trace(sb, s) for s in slopes])
    scale = 1.0
    for k in range(n):
        d = T[(k + 1) % n] - T[k]
        if t[k] + d.min() < TRACE_GAP_MIN:
            scale = min(scale, (t[k] - TRACE_GAP_MIN) / -d.min())
    T *= scale
    B = Y[:, None] + W[None, :] + T                                     # (n, N): each boundary's row along u
    gap_min = min(float(((B[(k + 1) % n] - B[k]) % N).min()) for k in range(n))
    params.update(wander_mm=shared_amp, trace_slope_deg=slopes, trace_scale=round(scale, 3),
                  boundary_gap_min_mm=round(gap_min, 1))

    # 3. Each texel's band and its distances to the band's top and bottom boundaries.
    best = np.full((N, N), np.inf)
    lam = np.zeros((N, N), dtype=np.int64)
    for k in range(n):
        d = (rows - B[k][None, :]) % N
        m = d < best
        best = np.where(m, d, best)
        lam = np.where(m, k, lam)
    nxt = (lam + 1) % n
    prv = (lam - 1) % n
    d_top = best
    d_bot = (B[nxt, cols] - rows) % N
    a_up = 0.5 * smoothstep(1.0 - d_top / (BAND_BLEND / 2.0))      # the neighbour's share: half at the boundary,
    a_dn = 0.5 * smoothstep(1.0 - d_bot / (BAND_BLEND / 2.0))      # none half the fold's width in

    # 4. Each band its own broken plane, leaning a degree or so across its thickness; two bands' planes meet in a
    # fold, never a step. Each boundary has a height of its own, a little in or out of the face, coming and going along
    # u; a band runs straight from its top boundary's height to its bottom's, so the planes are continuous, close round
    # the patch, and meet in ridges and valleys, rounded over BAND_BLEND. (The second version gave each band its own
    # lean and offset; leaning one way, neighbours met in soft steps of up to 4 mm, and at a ledge the bands' jump
    # cancelled or doubled the ledge along its run.)
    sl = HS.Stream(seed, pid, "levels")
    z = np.empty((n, N))
    for k in range(n):
        come = BAND_COME[0] + (1.0 - BAND_COME[0]) * (0.5 + 0.5 * wander(sl, BAND_COME[1]))   # along u, never constant
        z[k] = sl.randint(-BAND_NODE, BAND_NODE) / 10.0 * come
    thick = d_top + d_bot
    s_ = d_top / np.maximum(thick, 1.0)
    height = soften(z[lam, cols] * (1.0 - s_) + z[nxt, cols] * s_, BAND_BLEND / 4.0)
    th = np.stack([(B[(k + 1) % n] - B[k]) % N for k in range(n)])
    params["band_lean_deg"] = [round(float(np.degrees(np.arctan(np.abs(z[(k + 1) % n] - z[k]) / th[k]).max())), 2)
                               for k in range(n)]

    # 5. The fracture across the bands: broad planar facets, each tilted a degree or two its own way, meeting in soft
    # folds that fall in no rows; the face's light comes from these.
    fa = sc.randint(*FACET_AMP) * FACET_SHARE[L] // 100 / 10.0
    finfo = {}
    fac = facets(seed, pid, fa * facet_gain, finfo)
    params.update(facet_amp_mm=fa, facets=finfo)
    height = height + fac

    # 6. The ledges. At each ledge boundary the band above stands proud: its top edge rolls back in a rounded arris
    # (lit) and its face leans back the rest of the way over part of the band; at the boundary it breaks down in one
    # broken edge (shadowed), never two creases close together. A ledge runs right across the patch on its boundary's
    # trace; its depth swells and thins along u between its most and a floor that keeps its lit edge whole, and its
    # break widens with it; its edge wanders a little above the boundary.
    sf = HS.Stream(seed, pid, "steps")
    raise_ = np.zeros((N, N))
    slist, depths, drawn = [], {}, []
    major = sf.randrange(L) if majors else -1                           # which ledge, in order down the patch
    for kb in range(n):
        if not ledge[kb]:
            continue
        ka = (kb - 1) % n                                               # the band above, which stands proud
        big = len(drawn) == major
        most = sf.randint(*(STEP_MAJOR if big else STEP_MINOR))         # tenths of a mm
        share = sf.randint(*STEP_FLOOR)
        narrow = float(((B[kb] - B[ka]) % N).min())
        lean = min(max(60, t[ka] * sf.randint(*STEP_LEAN) // 100), int(0.7 * narrow))
        bev = sf.randint(*STEP_BEVEL) / 10.0
        ark = sf.randint(*STEP_ARRIS) / 10.0
        f = sf.randint(*STEP_ARRIS_DROP) / 100.0
        swells = sf.randint(*SWELL_CYCLES)
        e = STEP_IN * (0.5 + 0.5 * wander(sf, 12, 0.5))
        widen = 1.0 + BEVEL_VARY * wander(sf, 8, 0.6)
        sw = (0.5 + 0.5 * wander(sf, swells, 0.5)) ** SWELL_POW
        drawn.append((kb, ka, big, most, share, lean, bev, ark, f, swells, e, widen, sw))
    for kb, ka, big, most, share, lean, bev, ark, f, swells, e, widen, sw in drawn:
        if not (big or minor):
            continue                                                    # the arm with the minor ledges off
        d_hi = most / 10.0
        d_lo = max(STEP_FLOOR_MAJOR if big else STEP_FLOOR_MIN, most * share // 100) / 10.0
        D1 = d_lo + (d_hi - d_lo) * sw                                  # its depth along u
        slist.append(dict(boundary=int(kb), major=bool(big), most=d_hi, floor=d_lo, swells=int(swells), lean=int(lean),
                          arris=ark, arris_drop=f))
        depths[kb] = D1
        D = D1[None, :]
        w = np.clip(bev * D * widen[None, :], STEP_W[0], STEP_W[1])
        a = np.minimum(ark * w, STEP_ARRIS_MAX)                        # the arris's width
        b = B[kb][None, :] - e[None, :]                                 # the step's edge, a little above the boundary
        p = wrapd(b - rows)                                             # how far above the edge
        tb = (p + w) / w
        brk = np.where(tb > 0, ramp(np.maximum(tb, 0.0), rnd(w)), 0.0)          # the shadowed face, rising
        ta = p / a
        arr = np.where(ta > 0, ramp(np.maximum(ta, 0.0), rnd(a)), 0.0)          # the lit arris, rolling back
        tl = (p - a) / (lean - a)
        back = np.where(tl > 0, ramp(np.maximum(tl, 0.0), 0.3), 0.0)            # the face leaning back the rest
        lip = np.clip(1.0 - f * arr - (1.0 - f) * back, 0.0, 1.0)
        raise_ = raise_ + D * brk * lip
    height = height + raise_
    params["step_list"] = slist
    if not minor:
        params["minor"] = False

    # 7. The fine planar tooth, coarser or finer by band, blended across the boundaries; faint, since detail finer than
    # a few mm fades first (its creases were short lines floating mid-face at 1 m).
    st2 = HS.Stream(seed, pid, "tooth gain")
    gain = np.array([TOOTH_GAIN[st2.weighted([(i, w) for i, (_, w) in enumerate(TOOTH_GAIN)])][0] for _ in range(n)])
    params["tooth_gain"] = [float(x) for x in gain]
    gl = gain[lam] * (1 - a_up - a_dn) + gain[prv] * a_up + gain[nxt] * a_dn
    height = height + gl * tooth(HS.h(seed, pid, "tooth"), TOOTH_CELL, TOOTH_TILT, TOOTH_LIFT, TOOTH_BLEND)

    # 8. Value: the fine laminae within the bands, each a shade lighter, darker or the same, meeting softly; they follow
    # the bands as they pinch and swell (each texel's place across its band, carried back to the band at rest). Each
    # band a shade its own; a very soft broad mottle. All in one narrow band.
    sv = HS.Stream(seed, pid, "folia")
    prof = np.zeros(N)
    y = 0
    while y < N:
        lo, hi, _w = FOLIA[sv.weighted([(i, w) for i, (_, _, w) in enumerate(FOLIA)])]
        ti = min(sv.randint(lo, hi), N - y)
        prof[y:y + ti] = (0, -1, 1)[sv.weighted([(0, 2), (1, 1), (2, 1)])]
        y += ti
    prof = box1(box1(prof, FOLIA_SOFT), FOLIA_SOFT)
    tarr = np.array(t, dtype=np.float64)
    yy = (Y[lam] - first) + d_top * tarr[lam] / np.maximum(thick, 1.0)
    i0 = np.floor(yy).astype(int)
    fr = yy - i0
    folia = prof[i0 % N] * (1 - fr) + prof[(i0 + 1) % N] * fr
    stn = HS.Stream(seed, pid, "tone")
    tone = np.array([(0, -1, 1)[stn.weighted([(0, 2), (1, 1), (2, 1)])] for _ in range(n)], dtype=np.float64)
    params["band_tone"] = [int(x) for x in tone]
    tb_ = tone[lam] * (1 - a_up - a_dn) + tone[prv] * a_up + tone[nxt] * a_dn
    mult = 1.0 + FOLIA_TONE * folia + BAND_TONE * tb_ + MOTTLE * value_noise(HS.h(seed, pid, "mottle"), 4, 8)
    if layers is not None:
        layers.update(facets=fac, boundaries=B, ledge=list(ledge), depths=depths)
    return height, mult, params


# -- the bed face --------------------------------------------------------------------------------------------------------

def bed_patch(seed, name, layers=None):
    pid = f"stone/slate/patch/{name}"
    params = {}
    rows = np.arange(N, dtype=np.float64)[:, None]
    sc = HS.Stream(seed, pid, "character")
    lu = sc.randint(*UNDULATION[0])
    lv = sc.randint(*UNDULATION[1])
    amp = sc.randint(*UNDULATION[2]) / 10.0
    kb = sc.randint(BED_BEVEL[0], BED_BEVEL[1]) / 10.0
    params.update(undulation_cells=[lu, lv], undulation_mm=amp, bevel=kb)

    # 1. The plane: a broad gentle undulation, its wavelengths about 130 to 340 mm (longer one way than the other where
    # the cells differ) and its amplitude 1 to 2 mm. This and the value are the face's read.
    und = (value_noise(HS.h(seed, pid, "broad"), lu, lv)
           + 0.3 * value_noise(HS.h(seed, pid, "broad2"), 2 * lu, 2 * lv))
    height = amp * und / np.abs(und).max()

    # 2. One scarp, running right across the patch along u: the edge where the top lamina parted, facing down-dip, on a
    # gently curving trace with a finer wander, breaking wider or narrower; its depth swells and thins along its length
    # above a floor. Down-dip of it lies the next lamina, which rises back over the rest of the patch's height (a
    # millimetre or two over a metre), so the face tiles. Its fresher parting is a shade darker, fading down-dip;
    # nothing else is drawn.
    ss = HS.Stream(seed, pid, "scarp")
    most = ss.randint(*SCARP_DEPTH)
    d = most / 10.0
    d_lo = max(STEP_FLOOR_MIN, most * ss.randint(*SCARP_FLOOR) // 100) / 10.0
    fl = ss.randint(*SCARP_FRESH)
    y0 = ss.randrange(N)
    down = 1 if ss.randrange(2) else -1                                 # down-dip is down the image, or up
    slope = ss.randint(*TRACE_SLOPE) / 10.0
    swells = ss.randint(*SWELL_CYCLES)
    sw = (0.5 + 0.5 * wander(ss, swells, 0.5)) ** SWELL_POW
    edge = trace(ss, slope) + EDGE_WANDER[0] * wander(ss, 8, 0.8) + EDGE_WANDER[1] * wander(ss, 24, 0.5)
    widen = 1.0 + BEVEL_VARY * wander(ss, 12, 0.6)
    D1 = d_lo + (d - d_lo) * sw
    D = D1[None, :]
    w = np.clip(kb * D * widen[None, :], BED_BEVEL[2], BED_BEVEL[3])
    p = wrapd(down * (rows - (y0 + edge)[None, :]))                    # how far down-dip of the scarp
    brk = np.where(p > 0, ramp(np.maximum(p, 0.0) / w, rnd(w)), 0.0)
    height = height + D * ((p + N / 2.0) / N - brk)                    # down at the scarp, back up over the patch
    fresh = np.where(p > 0, smoothstep(1.0 - p / fl), 0.0)
    params["scarp"] = dict(most=d, floor=d_lo, swells=int(swells), row=int(y0), trace_slope_deg=slope,
                           down_dip="down" if down > 0 else "up", fresh_mm=fl)

    # 3. The tooth: the old cleavage face nearly smooth, the fresher parting a little rougher.
    fine = tooth(HS.h(seed, pid, "tooth"), (14, 14), (1.0, 1.0), 0.05, 0.25)
    height = height + fine * (TOOTH_BED[0] + (TOOTH_BED[1] - TOOTH_BED[0]) * fresh)

    # 4. Value: one tone, the fresher parting a shade darker, a soft broad mottle.
    mult = 1.0 - SCAR_TONE * fresh + 0.012 * value_noise(HS.h(seed, pid, "mottle"), 3, 5)
    if layers is not None:
        layers.update(boundaries=(y0 + edge)[None, :], ledge=[True], depths={0: D1})
    return height, mult, params


# -- maps ------------------------------------------------------------------------------------------------------------------

def normals(height):
    """Tangent-space normals from the height (mm on a 1 mm grid), periodic: u right, v up the image."""
    dhdu = (np.roll(height, -1, axis=1) - np.roll(height, 1, axis=1)) * 0.5
    dhdr = (np.roll(height, -1, axis=0) - np.roll(height, 1, axis=0)) * 0.5   # down the image
    n = np.stack([-dhdu, dhdr, np.ones_like(height)], -1)          # -dh/dv = +dh/drow
    return n / np.linalg.norm(n, axis=-1, keepdims=True)


def encode(height, mult):
    h = height - height.mean()
    assert h.min() > H_LO and h.max() < H_HI, (h.min(), h.max())
    assert mult.min() > V_LO and mult.max() < V_HI, (mult.min(), mult.max())
    h16 = np.round((h - H_LO) / (H_HI - H_LO) * 65535).astype(np.uint16)
    v16 = np.round((mult - V_LO) / (V_HI - V_LO) * 65535).astype(np.uint16)
    nrm = normals(h)
    n16 = np.round((nrm + 1.0) * 0.5 * 65535).astype(np.uint16)
    return {"height": h16, "normal": n16, "value": v16}


def png16(path, a):
    """A 16-bit PNG, grey (h, w) or RGB (h, w, 3), every row filter 0."""
    h, w = a.shape[:2]
    ch = 1 if a.ndim == 2 else a.shape[2]
    raw = np.zeros((h, 1 + w * ch * 2), np.uint8)
    raw[:, 1:] = np.frombuffer(a.astype(">u2").tobytes(), np.uint8).reshape(h, w * ch * 2)

    def chunk(t, d):
        return struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t + d) & 0xFFFFFFFF)

    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        f.write(b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 16, 0 if ch == 1 else 2, 0, 0, 0))
                + chunk(b"IDAT", zlib.compress(raw.tobytes(), 6)) + chunk(b"IEND", b""))


def read16(path):
    """Reads back a PNG written by png16 (16-bit, filter 0 on every row)."""
    data = open(path, "rb").read()
    pos, idat, w, h, ch = 8, b"", 0, 0, 1
    while pos < len(data):
        ln, = struct.unpack(">I", data[pos:pos + 4])
        tag = data[pos + 4:pos + 8]
        body = data[pos + 8:pos + 8 + ln]
        if tag == b"IHDR":
            w, h, depth, ctype = struct.unpack(">IIBB", body[:10])
            assert depth == 16 and ctype in (0, 2)
            ch = 1 if ctype == 0 else 3
        elif tag == b"IDAT":
            idat += body
        pos += 12 + ln
    raw = np.frombuffer(zlib.decompress(idat), np.uint8).reshape(h, 1 + w * ch * 2)
    assert not raw[:, 0].any(), "only filter 0 rows"
    a = np.frombuffer(raw[:, 1:].tobytes(), ">u2").reshape((h, w) if ch == 1 else (h, w, ch))
    return a.astype(np.uint16)


def pixel_hash(a):
    return hashlib.sha256(f"{a.shape}".encode() + a.astype(">u2").tobytes()).hexdigest()


def decode(maps):
    """The stored maps as numbers: height in mm, normal as unit vectors, the value's multiplier."""
    h = maps["height"].astype(np.float64) / 65535 * (H_HI - H_LO) + H_LO
    n = maps["normal"].astype(np.float64) / 65535 * 2.0 - 1.0
    n /= np.linalg.norm(n, axis=-1, keepdims=True)
    v = maps["value"].astype(np.float64) / 65535 * (V_HI - V_LO) + V_LO
    return h, n, v


def world_seed():
    return json.load(open(os.path.join(ROOT, "packs", PACK, "pack.json")))["worldSeed"]


def make(name, seed, layers=None, facet_gain=1.0, minor=True):
    """A patch's maps and drawn parameters. facet_gain and minor (split faces only) are the A/B arms: the facets'
    amplitude scaled, and the minor ledges off."""
    if name.startswith("split"):
        height, mult, params = split_patch(seed, name, layers, facet_gain, minor)
    else:
        height, mult, params = bed_patch(seed, name, layers)
    return encode(height, mult), params


def build(out=OUT, check=False):
    selftest_hash()
    seed = world_seed()
    doc = {
        "tool": TOOL,
        "describes": "The slaty rock's face patches (blender/parts/stone/slate/patches.py; SN6): four split faces and "
                     "two bed faces, 1024 by 1024 texels at 1 mm, seamless. Hashes are of the pixels (16-bit, "
                     "big-endian, row-major), so they hold whatever the PNG's compression.",
        "pack": PACK,
        "worldSeed": seed,
        "texels": N,
        "mmPerTexel": 1,
        "encoding": {
            "height": f"16-bit grey: mm = v / 65535 * {H_HI - H_LO:g} - {-H_LO:g}; the patch's mean at 0; + out of the face",
            "normal": "16-bit RGB: tangent space, u right, v up the image (green up), n = 2 v / 65535 - 1",
            "value": f"16-bit grey: the face value's multiplier = {V_LO:g} + {V_HI - V_LO:g} * v / 65535",
        },
        "patches": {},
    }
    old = json.load(open(MANIFEST)) if check and os.path.exists(MANIFEST) else None
    bad = []
    for name in PATCHES:
        maps, params = make(name, seed)
        entry = {"id": f"stone/slate/patch/{name}", "working": name.split("-")[0], "files": {}, "drawn": params}
        for kind, a in maps.items():
            fn = f"slate-{name}-{kind}.png"
            entry["files"][kind] = {"file": os.path.relpath(os.path.join(out, fn), ROOT), "pixels": pixel_hash(a)}
            if not check:
                png16(os.path.join(out, fn), a)
                assert pixel_hash(read16(os.path.join(out, fn))) == entry["files"][kind]["pixels"]
        doc["patches"][name] = entry
        if old is not None:
            for kind in maps:
                if old["patches"].get(name, {}).get("files", {}).get(kind, {}).get("pixels") != entry["files"][kind]["pixels"]:
                    bad.append(f"{name} {kind}")
        print(name, "done", flush=True)
    doc["arms"] = {}
    for suffix, kw in ARMS:
        for name in PATCHES:
            if not name.startswith("split"):
                continue
            arm = f"{name}-{suffix}"
            maps, params = make(name, seed, **kw)
            entry = {"id": f"stone/slate/patch/{name}", "arm": suffix, "working": "split",
                     "made": {k: v for k, v in kw.items()}, "files": {}, "drawn": params}
            for kind, a in maps.items():
                fn = f"slate-{arm}-{kind}.png"
                entry["files"][kind] = {"file": os.path.relpath(os.path.join(out, fn), ROOT), "pixels": pixel_hash(a)}
                if not check:
                    png16(os.path.join(out, fn), a)
                    assert pixel_hash(read16(os.path.join(out, fn))) == entry["files"][kind]["pixels"]
            doc["arms"][arm] = entry
            if old is not None:
                for kind in maps:
                    if old.get("arms", {}).get(arm, {}).get("files", {}).get(kind, {}).get("pixels") != \
                            entry["files"][kind]["pixels"]:
                        bad.append(f"{arm} {kind}")
            print(arm, "done", flush=True)
    if check:
        if old is None:
            print("no manifest to check against")
            return 1
        if old.get("tool") != TOOL:
            bad.append(f"tool {old.get('tool')} against {TOOL}")
        print("differs: " + ", ".join(bad) if bad else "every pixel hash matches the manifest")
        return 1 if bad else 0
    with open(MANIFEST, "w") as f:
        json.dump(doc, f, indent=1)
        f.write("\n")
    return 0


if __name__ == "__main__":
    args = sys.argv[1:]
    cmd = args[0] if args else "build"
    out = args[args.index("--out") + 1] if "--out" in args else OUT
    sys.exit(build(out, check=(cmd == "check")))
