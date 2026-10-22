"""The slaty rock's face patches (SN6 in reviews/lt1/port/2b/design.md; docs/research/stone.md, How stone is built and
laid, In short 6): the shared sculpted faces a stone's working picks from by its seed, made once by the rules of how
the town's phyllite breaks, never as generic noise. What each rule answers is in reviews/lt1/port/2b/r2a/patches.md.

Phyllite is laminated: it parts along its foliation into leaves (laminae) a centimetre to a hand thick, each a little
different in make and tone, and breaks across them. So the two workings show two different faces:

- **The split face** (a wall stone's front, a step's riser): a section across the foliation, the stone lying on its
  natural bed, so the laminae run along u. A patch is three to six bands (laminae a hand to a forearm thick), each its
  own broken plane a little in or out of the face and leaning a degree or two, meeting its neighbours in a soft fold.
  Across the bands the fracture runs in broad planar facets (a bent, sheared triangulated lattice of corners each a
  millimetre or two in or out), meeting in rounded folds with no step; these give the face its light. Where two bands
  meet, the upper may stand proud by one low step (3 to 8 mm): a rounded lit arris over one broken shadowed edge,
  never two creases close together. A step runs right across the patch (on a stone it meets the face's edges at both
  ends; a line that starts or ends mid-face floats, Øystein); its depth varies along u but never below about half its
  most. Within each band a fine planar tooth, faint (the finest marks fade first). Value: fine laminae a shade lighter
  or darker, each band a shade its own, a soft mottle; nothing plucked, nothing outlined.
- **The bed face** (a tread's or coping's top): the foliation plane itself, broad and nearly flat. Its read is a broad
  gentle undulation (a wavelength of about 250 to 400 mm, 1 to 2 mm high) and its value. At most one scarp, where the
  top lamina parted: it runs right across the patch, faces down-dip only, its depth varying but never below a third
  or so of its most, and the next lamina rises back from it over the rest of the patch so the face tiles; its fresher
  parting is a little rougher and a shade darker, fading down-dip. Half the bed patches have no scarp.

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
purpose); lattices hash (..., i, j, n) the same way, vectorised here and checked against the scalar spec. Integers
choose (how many, which class, which lamina); floats from the hash only shape texels.

    python patches.py build [--out DIR]      write the maps and the manifest
    python patches.py check [--out DIR]      rebuild in memory and compare the pixel hashes with the manifest (exit 1)

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

TOOL = "patches 2"
PACK = "stavanger-1989"
N = 1024                      # texels a side, 1 mm each
H_LO, H_HI = -16.0, 16.0      # the height map's range, mm
V_LO, V_HI = 0.75, 1.25       # the value map's range, as a multiplier on the face's one value
OUT = os.path.join(ROOT, "cache", "stone", "patches")
MANIFEST = os.path.join(HERE, "patches.manifest.json")
PATCHES = ("split-0", "split-1", "split-2", "split-3", "bed-0", "bed-1")

# -- the rules' constants (mm unless said) -----------------------------------------------------------------------------

# Split face. A patch is a few laminae bands across its height, each its own broken plane; the fracture across them is
# a few broad planar facets; where two bands meet, the upper may stand proud by one low step running right across. The
# read at 5 m is facets of slightly different light and a few ledges, never loose lines (the first version's narrow
# steps that faded out mid-face read as floating grooves).
BANDS = (3, 6)                # laminae bands across a patch's height (1024 mm)
BAND_WEIGHT = (60, 140)       # their thicknesses' relative weights
WANDER_MM = (2, 5)            # the foliation's common wander along u
OWN_WANDER = 15               # tenths of a mm: each boundary's own wander besides
BAND_OFFSET = 10              # tenths of a mm: a band's plane in or out of the face
BAND_LEAN = (10, 30)          # tenths of a degree: a band's lean across its thickness ...
BAND_LEAN_RANGE = 4.0         # ... never more than this across the band
BAND_COME = (0.2, 3)          # a band's lean and offset come and go along u: from this share to all, over 3 cycles
BAND_BLEND = 50               # mm: two bands' planes meet in a soft fold this wide, never a crease
FACET_CELL = (200, 120)       # the fracture's facets: a lattice of corners this far apart (along u, across) ...
FACET_AMP = (16, 28)          # ... each corner in or out of the face by up to this (tenths of a mm, drawn a patch),
                              # so the facets between are planes tilted a degree or two, meeting in folds with no step
                              # (planes blended across a step read as pillows on a grid); more and the face passes
                              # about 2 L* in grey light (The Witness)
FACET_WARP = 0.40             # the lattice bent by up to this share of a cell, so no fold runs straight or on a grid
FACET_SOFT = 7.0              # mm: the folds rounded over this (a Gaussian), never a knife line
STEP_ON = ((0, 1), (1, 1))    # a boundary has a step or not (weights); a step runs right across the patch, so on a
                              # stone it meets the face's edges at both ends (a line that ends mid-face floats, Øystein)
STEP_DEPTH = ((3, 5, 3), (6, 8, 1))     # (lo, hi, weight): never deeper than 8; deeper facets are the mesh's (SN4)
STEP_FLOOR = (55, 70)         # percent: along u its depth varies, never below this share of its most (at a third,
                              # the lit arris fell under 1 L* for a few mm and the step read as two floating lines)
STEP_VARY = 4                 # the variation's cycles a patch
STEP_ARRIS = (5, 8)           # tenths of the break's width: the step's top edge rolls back over this, a rounded arris
STEP_ARRIS_DROP = (60, 80)    # percent of the step's height it rolls back by, so steeply that the narrow lit edge
                              # weighs as much as the broad shadow (a lit slope gains fewer L* than a dark one loses):
                              # the step reads as a ledge, lit over shadowed, never as a dark groove
STEP_LEAN = (35, 60)          # percent of the band above (at least 60 mm): the rest of the step's height leans back
                              # into the face over this
STEP_BEVEL = (35, 45)         # tenths: a step's broken edge, its width over its height ...
STEP_W = (16.0, 32.0)         # ... never narrower than 16 mm (narrower, a shallow step's shadow was a line under 2 px
                              # wide at 5 m)
STEP_IN = 4.0                 # a step's edge wanders up to this far above its boundary
BEVEL_VARY = 0.3              # and breaks this much wider or narrower along its run
ROUND = (2.0, 0.3)            # a broken edge's corners rounded over 2 texels or 0.3 of its width, the larger, so no
                              # crease is a line (at 1.5 texels, the foot of a steep edge was a dark line 1 to 2 px)
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

# Bed face. The main read is a broad gentle undulation and the value; at most one scarp, facing down-dip and running
# right across (the first version's flake scars were outlined all round, like ink, and a scar's feathered sides were
# lines ending mid-face).
UNDULATION = ((5, 8), (10, 20))   # its lattice (cells a patch: a wavelength of about 250 to 400 mm) and its
                                  # amplitude in tenths of a mm (1 to 2 mm)
SCARPS = ((0, 1), (1, 1))     # a bed patch has one scarp, running right across it, or none (weights): a scarp that
                              # ends inside the patch floats (Øystein)
SCARP_DEPTH = (15, 30)        # tenths of a mm: the top lamina's edge, where it parted
SCARP_FLOOR = (33, 50)        # percent: along its length its depth varies, never below this share of its most
SCARP_FRESH = (60, 140)       # mm: the lower lamina's fresher parting, a shade darker, fading down-dip over this
BED_BEVEL = (40, 60, 10.0, 20.0)  # a scarp's break: factor on its depth (tenths), least and most width (at 6
                                 # to 12 mm the scarps read as thin strokes at 5 m)
EDGE_WANDER = (6.0, 2.0)      # a scarp's wander, mm, at about 128 and 43 mm
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


def facets(seed, pid, amp, shear):
    """The fracture's broad facets: a triangulated lattice of corners, each a little in or out of the face, so every
    triangle between is a plane with its own tilt and the planes meet in folds with no step; the lattice is bent so no
    fold runs straight, sheared by a whole number of cells over the patch's height so its cross folds run slant and
    never line up down the face (upright, they read as a grid), each cell split along a hashed diagonal, and the folds
    rounded."""
    pre = HS.h(seed, pid, "facets")
    px, py = max(1, round(N / FACET_CELL[0])), max(1, round(N / FACET_CELL[1]))
    I, J = np.meshgrid(np.arange(px), np.arange(py), indexing="xy")
    hv = (2.0 * vunit(vkey(pre, I, J, np.zeros_like(I))) - 1.0) * amp       # (py, px): the corners' heights
    diag = vunit(vkey(pre, I, J, np.ones_like(I))) < 0.5                     # which diagonal splits the cell
    X, Y = np.meshgrid(np.arange(N, dtype=np.float64), np.arange(N, dtype=np.float64), indexing="xy")
    cw, ch = N / px, N / py
    xw = X / cw + shear * Y / N + FACET_WARP * value_noise(HS.h(seed, pid, "facet bend u"), 8, 8)
    yw = Y / ch + FACET_WARP * value_noise(HS.h(seed, pid, "facet bend v"), 8, 10)
    i0, j0 = np.floor(xw).astype(int), np.floor(yw).astype(int)
    fx, fy = xw - i0, yw - j0

    def corner(i, j):
        """The lattice corner (i, j), unwrapped: each wrap down the patch shifts it back by the shear, so it tiles."""
        return j % py, (i - shear * (j // py)) % px
    h00, h10, h01, h11 = (hv[corner(i0 + a, j0 + b)] for a, b in ((0, 0), (1, 0), (0, 1), (1, 1)))
    d = diag[corner(i0, j0)]
    a = np.where(fx >= fy, h00 + fx * (h10 - h00) + fy * (h11 - h10), h00 + fy * (h01 - h00) + fx * (h11 - h01))
    b = np.where(fx + fy <= 1.0, h00 + fx * (h10 - h00) + fy * (h01 - h00),
                 h11 + (1.0 - fx) * (h01 - h11) + (1.0 - fy) * (h10 - h11))
    return soften(np.where(d, a, b), FACET_SOFT)


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

def split_patch(seed, name):
    pid = f"stone/slate/patch/{name}"
    params = {}

    # 1. The bands: three to six laminae bands across the patch's height, their thicknesses whole millimetres.
    st = HS.Stream(seed, pid, "laminae")
    n = st.randint(*BANDS)
    wts = [st.randint(*BAND_WEIGHT) for _ in range(n)]
    t = [N * w // sum(wts) for w in wts]
    t[-1] += N - sum(t)
    first = st.randrange(N)
    Y = (first + np.concatenate([[0], np.cumsum(t)[:-1]])) % N        # each band's top boundary, at rest
    params.update(bands=n, thickness_mm=[int(x) for x in t])

    # 2. Where each boundary runs: the foliation's common wander plus a little of its own, so no two cross.
    sc = HS.Stream(seed, pid, "character")
    shared_amp = sc.randint(*WANDER_MM)
    params["wander_mm"] = shared_amp
    sb = HS.Stream(seed, pid, "boundaries")
    W = shared_amp * wander(sb, 3)
    B = np.empty((n, N))
    for k in range(n):
        B[k] = Y[k] + W + (sb.randint(0, OWN_WANDER) / 10.0) * wander(sb, 5, 0.7)

    # 3. Each texel's band and its distances to the band's top and bottom boundaries.
    rows = np.arange(N, dtype=np.float64)[:, None]
    cols = np.arange(N)[None, :]
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

    # 4. Each band its own broken plane: a little in or out of the face, leaning a degree or so across its thickness
    # (never more than a few mm across it); two bands' planes meet in a soft fold, never a crease.
    sl = HS.Stream(seed, pid, "levels")
    off = np.empty((n, N))
    g = np.empty((n, N))
    lean_deg = []
    for k in range(n):
        lean = math.tan(math.radians(sl.randint(*BAND_LEAN) / 10.0))
        gk = (1 if sl.randrange(2) else -1) * min(lean, BAND_LEAN_RANGE / t[k])
        lean_deg.append(round(math.degrees(math.atan(gk)), 2))
        come = BAND_COME[0] + (1.0 - BAND_COME[0]) * (0.5 + 0.5 * wander(sl, BAND_COME[1]))   # along u, never constant
        off[k] = (sl.randint(-BAND_OFFSET, BAND_OFFSET) / 10.0) * come
        g[k] = gk * come
    params["lean_deg"] = lean_deg
    thick = d_top + d_bot
    th_prv = (B[lam, cols] - B[prv, cols]) % N
    th_nxt = (B[(nxt + 1) % n, cols] - B[nxt, cols]) % N
    own = off[lam, cols] + g[lam, cols] * (d_top - thick / 2.0)
    up = off[prv, cols] + g[prv, cols] * (th_prv + d_top - th_prv / 2.0)     # the band above, carried past its bottom
    dn = off[nxt, cols] + g[nxt, cols] * (-d_bot - th_nxt / 2.0)             # the band below, carried above its top
    height = (1.0 - a_up - a_dn) * own + a_up * up + a_dn * dn

    # 5. The fracture across the bands: broad planar facets, each tilted a degree or two its own way, meeting in soft
    # folds; the face's light comes from these.
    fa = sc.randint(*FACET_AMP) / 10.0
    shear = (-2, -1, 1, 2)[sc.randrange(4)]
    params.update(facet_amp_mm=fa, facet_shear_cells=shear)
    height = height + facets(seed, pid, fa, shear)

    # 6. The steps. Where two bands meet, the upper may stand proud: its top edge rolls back in a rounded arris (lit)
    # and its face leans back the rest of the way over part of the band; at the boundary it breaks down in one broken
    # edge (shadowed), never two creases close together. A step runs right across the patch: its depth varies along u
    # but never falls below a third or so of its most, and never passes 8 mm; its edge wanders a little above the
    # boundary and breaks wider or narrower along u. A boundary without a step is only the bands' soft fold.
    sf = HS.Stream(seed, pid, "steps")
    raise_ = np.zeros((N, N))
    slist = []
    for k in range(n):
        if not sf.weighted([(c, w) for c, w in STEP_ON]):
            continue
        lo, hi, _w = STEP_DEPTH[sf.weighted([(i, w) for i, (_, _, w) in enumerate(STEP_DEPTH)])]
        d = sf.randint(lo, hi)
        floor = sf.randint(*STEP_FLOOR) / 100.0
        lean = max(60, t[k] * sf.randint(*STEP_LEAN) // 100)
        bev = sf.randint(*STEP_BEVEL) / 10.0
        ark = sf.randint(*STEP_ARRIS) / 10.0
        f = sf.randint(*STEP_ARRIS_DROP) / 100.0
        e = STEP_IN * (0.5 + 0.5 * wander(sf, 12, 0.5))
        widen = 1.0 + BEVEL_VARY * wander(sf, 8, 0.6)
        vary = 0.5 + 0.5 * wander(sf, STEP_VARY, 0.7)
        slist.append(dict(boundary=k, height=int(d), floor=floor, lean=int(lean), arris=ark, arris_drop=f))
        D = (d * (floor + (1.0 - floor) * vary))[None, :]                # (1, N): its depth along u
        w = np.clip(bev * D * widen[None, :], STEP_W[0], STEP_W[1])
        a = ark * w                                                     # the arris's width
        b = B[(k + 1) % n][None, :] - e[None, :]                       # the step's edge, a little above the boundary
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

    # 7. The fine planar tooth, coarser or finer by band, blended across the boundaries; faint, since detail finer than
    # a few mm fades first (its creases were short lines floating mid-face at 1 m).
    st2 = HS.Stream(seed, pid, "tooth gain")
    gain = np.array([TOOTH_GAIN[st2.weighted([(i, w) for i, (_, w) in enumerate(TOOTH_GAIN)])][0] for _ in range(n)])
    params["tooth_gain"] = [float(x) for x in gain]
    gl = gain[lam] * (1 - a_up - a_dn) + gain[prv] * a_up + gain[nxt] * a_dn
    height = height + gl * tooth(HS.h(seed, pid, "tooth"), TOOTH_CELL, TOOTH_TILT, TOOTH_LIFT, TOOTH_BLEND)

    # 8. Value: the fine laminae within the bands, each a shade lighter, darker or the same, meeting softly and running
    # with the foliation's wander; each band a shade its own; a very soft broad mottle. All in one narrow band.
    sv = HS.Stream(seed, pid, "folia")
    prof = np.zeros(N)
    y = 0
    while y < N:
        lo, hi, _w = FOLIA[sv.weighted([(i, w) for i, (_, _, w) in enumerate(FOLIA)])]
        ti = min(sv.randint(lo, hi), N - y)
        prof[y:y + ti] = (0, -1, 1)[sv.weighted([(0, 2), (1, 1), (2, 1)])]
        y += ti
    prof = box1(box1(prof, FOLIA_SOFT), FOLIA_SOFT)
    yy = (rows - W[None, :] - first) % N
    i0 = np.floor(yy).astype(int)
    fr = yy - i0
    folia = prof[i0 % N] * (1 - fr) + prof[(i0 + 1) % N] * fr
    stn = HS.Stream(seed, pid, "tone")
    tone = np.array([(0, -1, 1)[stn.weighted([(0, 2), (1, 1), (2, 1)])] for _ in range(n)], dtype=np.float64)
    params["band_tone"] = [int(x) for x in tone]
    tb_ = tone[lam] * (1 - a_up - a_dn) + tone[prv] * a_up + tone[nxt] * a_dn
    mult = 1.0 + FOLIA_TONE * folia + BAND_TONE * tb_ + MOTTLE * value_noise(HS.h(seed, pid, "mottle"), 4, 8)
    return height, mult, params


# -- the bed face --------------------------------------------------------------------------------------------------------

def bed_patch(seed, name):
    pid = f"stone/slate/patch/{name}"
    params = {}
    rows = np.arange(N, dtype=np.float64)[:, None]
    sc = HS.Stream(seed, pid, "character")
    n_scarps = sc.weighted([(c, w) for c, w in SCARPS])
    lat = sc.randint(*UNDULATION[0])
    amp = sc.randint(*UNDULATION[1]) / 10.0
    kb = sc.randint(BED_BEVEL[0], BED_BEVEL[1]) / 10.0
    params.update(scarps=n_scarps, undulation_cells=lat, undulation_mm=amp, bevel=kb)

    # 1. The plane: a broad gentle undulation, its wavelength about 250 to 400 mm and its amplitude 1 to 2 mm. This and
    # the value are the face's read.
    und = value_noise(HS.h(seed, pid, "broad"), lat, lat) + 0.3 * value_noise(HS.h(seed, pid, "broad2"), 2 * lat, 2 * lat)
    height = amp * und / np.abs(und).max()

    # 2. At most one scarp, running right across the patch along u: the edge where the top lamina parted, facing
    # down-dip, a broken edge that wanders and breaks wider or narrower; its depth varies along its length but never
    # below a third or so of its most. Down-dip of it lies the next lamina, which rises back over the rest of the patch's
    # height (a millimetre or two over a metre), so the face tiles. Its fresher parting is a shade darker, fading
    # down-dip; nothing else is drawn.
    fresh = np.zeros((N, N))
    if n_scarps:
        ss = HS.Stream(seed, pid, "scarp")
        d = ss.randint(*SCARP_DEPTH) / 10.0
        floor = ss.randint(*SCARP_FLOOR) / 100.0
        fl = ss.randint(*SCARP_FRESH)
        y0 = ss.randrange(N)
        down = 1 if ss.randrange(2) else -1                             # down-dip is down the image, or up
        vary = 0.5 + 0.5 * wander(ss, STEP_VARY, 0.7)
        edge = EDGE_WANDER[0] * wander(ss, 8, 0.8) + EDGE_WANDER[1] * wander(ss, 24, 0.5)
        widen = 1.0 + BEVEL_VARY * wander(ss, 12, 0.6)
        D = (d * (floor + (1.0 - floor) * vary))[None, :]
        w = np.clip(kb * D * widen[None, :], BED_BEVEL[2], BED_BEVEL[3])
        p = wrapd(down * (rows - (y0 + edge)[None, :]))                # how far down-dip of the scarp
        brk = np.where(p > 0, ramp(np.maximum(p, 0.0) / w, rnd(w)), 0.0)
        height = height + D * ((p + N / 2.0) / N - brk)                # down at the scarp, back up over the patch
        fresh = np.where(p > 0, smoothstep(1.0 - p / fl), 0.0)
        params["scarp"] = dict(depth=d, floor=floor, row=int(y0), down_dip="down" if down > 0 else "up", fresh_mm=fl)

    # 3. The tooth: the old cleavage face nearly smooth, the fresher parting a little rougher.
    fine = tooth(HS.h(seed, pid, "tooth"), (14, 14), (1.0, 1.0), 0.05, 0.25)
    height = height + fine * (TOOTH_BED[0] + (TOOTH_BED[1] - TOOTH_BED[0]) * fresh)

    # 4. Value: one tone, the fresher parting a shade darker, a soft broad mottle.
    mult = 1.0 - SCAR_TONE * fresh + 0.012 * value_noise(HS.h(seed, pid, "mottle"), 3, 5)
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


def make(name, seed):
    fn = split_patch if name.startswith("split") else bed_patch
    height, mult, params = fn(seed, name)
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
    if check:
        if old is None:
            print("no manifest to check against")
            return 1
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
