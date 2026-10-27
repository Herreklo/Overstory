"""The house's door, fitted to its hole: a pair of panelled leaves under an overlight, in a frame set back in the
casing's reveal, on a threshold, with stone steps down to the ground where the ground lies below it. The door's kind
is the era's (timber.json, doors): its size, its panels (square fields, raised; the glazed rows of a later door), its
overlight. Boarded with the house's windows while the house is boarded.
"""

import math

import windows as WN

MM = 0.001


def _panel(soup, f, a, b, za, zb, wl, field, raise_, rng):
    """A raised panel between its stiles and rails: the flat ground sunk by field, the raised field in its middle and
    the bevels from one to the other."""
    soup.use(seed=rng.random())
    wg, wr = wl - field, wl - field * 0.35
    soup.quad(f.at(a, za, wg), f.at(b, za, wg), f.at(b, zb, wg), f.at(a, zb, wg), ta=[(a, za), (b, za), (b, zb), (a, zb)])
    if soup.level > 0:
        return
    r = min(raise_, 0.3 * (b - a), 0.3 * (zb - za))
    a1, b1, za1, zb1 = a + r, b - r, za + r, zb - r
    soup.quad(f.at(a1, za1, wr), f.at(b1, za1, wr), f.at(b1, zb1, wr), f.at(a1, zb1, wr),
              ta=[(a1, za1), (b1, za1), (b1, zb1), (a1, zb1)])
    g = wg + 0.002
    soup.quad(f.at(a, za, g), f.at(b, za, g), f.at(b1, za1, wr), f.at(a1, za1, wr))
    soup.quad(f.at(b, za, g), f.at(b, zb, g), f.at(b1, zb1, wr), f.at(b1, za1, wr))
    soup.quad(f.at(b, zb, g), f.at(a, zb, g), f.at(a1, zb1, wr), f.at(b1, zb1, wr))
    soup.quad(f.at(a, zb, g), f.at(a, za, g), f.at(a1, za1, wr), f.at(a1, zb1, wr))


def _leaf(soup, f, a, b, za, zb, wl, sp, rng, handle):
    """One leaf: its stiles and rails standing the leaf's thickness, a raised panel (or a pane) in each field."""
    t = sp["leafMm"] * MM
    st, rl, br, lk = (sp[k] * MM for k in ("stileMm", "railMm", "bottomRailMm", "lockRailMm"))
    rows, glazed = sp["panelRows"], sp["glazedRows"]
    soup.use(kind="door", scheme="door", seed=rng.random(), lap=0.5)
    soup.box(f, a, a + st, za, zb, wl - t, wl, grain="z")
    soup.box(f, b - st, b, za, zb, wl - t, wl, grain="z")
    # the rails: the bottom, the lock rail under the top row's fields, the rest between equal fields
    fa, fb = za + br, zb - rl
    inner = fb - fa - lk - (rows - 2) * rl if rows > 1 else fb - fa
    fh = inner / rows
    zs = [fa]
    for i in range(rows):
        z0 = zs[-1]
        z1 = z0 + fh
        zs.append(z1)
        if i < rows - 1:
            zs.append(z1 + (lk if i == 0 else rl))
    soup.use(kind="door", scheme="door", seed=rng.random())
    soup.box(f, a + st, b - st, za, fa, wl - t, wl)
    soup.box(f, a + st, b - st, fb, zb, wl - t, wl)
    for i in range(rows - 1):
        soup.box(f, a + st, b - st, zs[2 * i + 1], zs[2 * i + 2], wl - t, wl)
    for i in range(rows):
        z0, z1 = zs[2 * i], zs[2 * i + 1]
        if i >= rows - glazed:
            soup.use(kind="glass", scheme="none", lit=0.0)
            soup.quad(f.at(a + st, z0, wl - t * 0.6), f.at(b - st, z0, wl - t * 0.6), f.at(b - st, z1, wl - t * 0.6),
                      f.at(a + st, z1, wl - t * 0.6))
            soup.use(kind="door", scheme="door")
        else:
            soup.use(kind="door", scheme="door")
            _panel(soup, f, a + st, b - st, z0, z1, wl, sp["fieldMm"] * MM, sp["raiseMm"] * MM, rng)
    if handle is not None:
        hw, hh, hp = (v * MM for v in sp["handleMm"])
        zh = za + sp["handleAtMm"] * MM
        soup.use(kind="metal", scheme="none", seed=rng.random())
        soup.box(f, handle - hw / 2, handle + hw / 2, zh - hh / 2, zh + hh / 2, wl, wl + hp * 0.4)
        soup.box(f, handle - hw * 0.35, handle + hw * 0.35, zh + hh * 0.15, zh + hh * 0.35, wl, wl + hp)


def door(soup, f, hole, sp, out_w, rng, lit):
    """A door in its hole (s0, s1, z0, z1), z0 its threshold: the frame, the overlight under the head, the leaves."""
    s0, s1, z0, z1 = hole
    fr = sp["frameMm"] * MM
    wf = out_w - 0.004
    if soup.level >= 2:
        soup.use(kind="door", scheme="door", seed=rng.random(), lap=0.5)
        soup.quad(f.at(s0, z0, wf - 0.05), f.at(s1, z0, wf - 0.05), f.at(s1, z1, wf - 0.05), f.at(s0, z1, wf - 0.05),
                  ta=[(s0, z0), (s1, z0), (s1, z1), (s0, z1)])
        return
    depth = 0.12
    soup.use(kind="sash", scheme="door", seed=rng.random(), lap=0.5)
    soup.box(f, s0, s1, z1 - fr, z1, wf - depth, wf)
    soup.box(f, s0, s0 + fr, z0, z1 - fr, wf - depth, wf, grain="z")
    soup.box(f, s1 - fr, s1, z0, z1 - fr, wf - depth, wf, grain="z")
    i0, i1, j1 = s0 + fr, s1 - fr, z1 - fr
    wl = wf - sp["setBackMm"] * MM
    light = sp["lightMm"] * MM
    if light > 0:
        zt = j1 - light
        soup.use(kind="sash", scheme="door", seed=rng.random())
        soup.box(f, i0, i1, zt - fr * 0.5, zt + fr * 0.5, wf - depth, wf)
        wg = wl - 0.03
        p = WN._sash(soup, f, i0, i1, zt + fr * 0.5, j1, wl, sp["barMm"] * MM * 1.6, sp["barMm"] * MM, 1,
                     sp["lightCols"], rng, lit, "door", wg)
        WN.glass(soup, f, (s0, s1, zt + fr * 0.5, z1), p, wg, lit, 0.5 * (s0 + s1))
        j1 = zt - fr * 0.5
    leaves = sp["leaves"]
    for k in range(leaves):
        a = i0 + (i1 - i0) * k / leaves
        b = i0 + (i1 - i0) * (k + 1) / leaves
        handle = (a + sp["stileMm"] * MM * 0.5) if (leaves == 1 or k == 1) else None
        _leaf(soup, f, a + 0.002, b - 0.002, z0, j1, wl, sp, rng, handle)


def threshold(soup, f, s0, s1, za, zb, out_w, rng):
    """The threshold board under the door, from the drip board's line to the door's foot."""
    soup.use(kind="trim", scheme="trim", seed=rng.random(), lap=0.5)
    soup.box(f, s0, s1, za, zb, 0.0, out_w + 0.03)


def steps(soup, f, s0, s1, ztop, zground, st, rng):
    """Stone steps down from the threshold to the ground: each a rigid slab, set on the one below it, the lowest on
    the ground; none where the ground is within a step of the threshold."""
    drop = ztop - zground
    lo, hi = st["riserMm"][0] * MM, st["riserMm"][1] * MM
    if drop < lo * 0.5:
        return 0
    n = max(1, math.ceil(drop / hi - 1e-6))
    riser = drop / n
    tread = st["treadMm"] * MM
    over = st["overhangMm"] * MM
    soup.use(kind="stone", scheme="none", lap=0.5)
    for k in range(n):
        zt = ztop - riser * k
        soup.use(seed=rng.random())
        widen = over * (1 + 0.5 * k)
        soup.box(f, s0 - widen, s1 + widen, zground - 0.12, zt, 0.0, tread * (k + 1), skip=("back", "bottom"))
    return n
