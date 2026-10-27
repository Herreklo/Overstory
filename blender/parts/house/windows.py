"""Windows, fitted to their hole: the frame, the sashes, the glazing bars (modelled, never cut out), and the glass,
which carries the pane's place in the window and the room's seed so the shader can draw a room behind it. A boarded
window is covered by rough boards nailed across its casing. The window's kind is the pack's (timber.json, windows),
chosen by the house's era or by the year its windows were replaced.
"""

MM = 0.001


def _frame_box(soup, f, s0, s1, z0, z1, w0, w1, grain="s"):
    soup.box(f, s0, s1, z0, z1, w0, w1, skip=("back",), grain=grain)


def _sash(soup, f, s0, s1, z0, z1, wf, sa, bar, rows, cols, rng, lit, scheme, glass_w):
    """One sash: its four rails and stiles, its bars, and its panes of glass."""
    d = 0.045
    soup.use(kind="sash", scheme=scheme, seed=rng.random(), lap=0.5)
    _frame_box(soup, f, s0, s1, z0, z0 + sa * 1.25, wf - d, wf)          # the bottom rail, deeper than the rest
    _frame_box(soup, f, s0, s1, z1 - sa, z1, wf - d, wf)
    _frame_box(soup, f, s0, s0 + sa, z0 + sa * 1.25, z1 - sa, wf - d, wf, grain="z")
    _frame_box(soup, f, s1 - sa, s1, z0 + sa * 1.25, z1 - sa, wf - d, wf, grain="z")
    gs0, gs1, gz0, gz1 = s0 + sa, s1 - sa, z0 + sa * 1.25, z1 - sa
    bw = bar
    if bw > 0:
        for i in range(1, cols):
            s = gs0 + (gs1 - gs0) * i / cols
            _frame_box(soup, f, s - bw / 2, s + bw / 2, gz0, gz1, wf - d * 0.7, wf - 0.006, grain="z")
        for j in range(1, rows):
            z = gz0 + (gz1 - gz0) * j / rows
            _frame_box(soup, f, gs0, gs1, z - bw / 2, z + bw / 2, wf - d * 0.7, wf - 0.006)
    return (gs0, gs1, gz0, gz1)


def glass(soup, f, hole, pane, wg, lit, centre):
    """The glass over a sash's opening, its surface coordinates the window's own (metres from its foot, centred)."""
    s0, s1, z0, z1 = pane
    soup.use(kind="glass", scheme="none", lit=lit, lap=0.5)
    c, base = centre, hole[2]
    soup.quad(f.at(s0, z0, wg), f.at(s1, z0, wg), f.at(s1, z1, wg), f.at(s0, z1, wg),
              ta=[(s0 - c, z0 - base), (s1 - c, z0 - base), (s1 - c, z1 - base), (s0 - c, z1 - base)])


def window(soup, f, hole, spec, out_w, rng, lit, scheme):
    """A window in its hole (s0, s1, z0, z1): the frame flush with the cladding's face, the sashes just inside it."""
    s0, s1, z0, z1 = hole
    fr, sa, bar = spec["frameMm"] * MM, spec["sashMm"] * MM, spec["barMm"] * MM
    top = spec["top"] * MM
    cols, rows = spec["cols"], spec["rows"]
    wf = out_w - 0.004
    depth = 0.11
    centre = 0.5 * (s0 + s1)
    soup.use(kind="sash", scheme=scheme, seed=rng.random(), lap=0.5)
    _frame_box(soup, f, s0, s1, z0, z0 + fr, wf - depth, wf)
    _frame_box(soup, f, s0, s1, z1 - fr, z1, wf - depth, wf)
    _frame_box(soup, f, s0, s0 + fr, z0 + fr, z1 - fr, wf - depth, wf, grain="z")
    _frame_box(soup, f, s1 - fr, s1, z0 + fr, z1 - fr, wf - depth, wf, grain="z")
    i0, i1, j0, j1 = s0 + fr, s1 - fr, z0 + fr, z1 - fr
    ws = wf - 0.014
    wg = ws - 0.03
    if top > 0:
        # the T-post: a transom under the top light and a post between the casements below it
        zt = j1 - top
        soup.use(kind="sash", scheme=scheme, seed=rng.random())
        _frame_box(soup, f, i0, i1, zt - fr * 0.5, zt + fr * 0.5, wf - depth, wf)
        p = _sash(soup, f, i0, i1, zt + fr * 0.5, j1, ws, sa * 0.85, bar, 1, 2 if bar > 0 else 1, rng, lit, scheme, wg)
        glass(soup, f, hole, p, wg, lit, centre)
        j1 = zt - fr * 0.5
        if cols == 2:
            sm = 0.5 * (i0 + i1)
            soup.use(kind="sash", scheme=scheme, seed=rng.random())
            _frame_box(soup, f, sm - fr * 0.5, sm + fr * 0.5, j0, j1, wf - depth, wf, grain="z")
            for a, b in ((i0, sm - fr * 0.5), (sm + fr * 0.5, i1)):
                p = _sash(soup, f, a, b, j0, j1, ws, sa, bar, rows, 1, rng, lit, scheme, wg)
                glass(soup, f, hole, p, wg, lit, centre)
            return
    if cols == 2 and spec["post"]:
        # two casements either side of a fixed post
        sm = 0.5 * (i0 + i1)
        soup.use(kind="sash", scheme=scheme, seed=rng.random())
        _frame_box(soup, f, sm - fr * 0.5, sm + fr * 0.5, j0, j1, wf - depth, wf, grain="z")
        for a, b in ((i0, sm - fr * 0.5), (sm + fr * 0.5, i1)):
            p = _sash(soup, f, a, b, j0, j1, ws, sa, bar, rows, 1, rng, lit, scheme, wg)
            glass(soup, f, hole, p, wg, lit, centre)
        return
    # casements meeting in the middle, or one sash
    for k in range(cols):
        a = i0 + (i1 - i0) * k / cols
        b = i0 + (i1 - i0) * (k + 1) / cols
        p = _sash(soup, f, a, b, j0, j1, ws, sa, bar, rows, 1, rng, lit, scheme, wg)
        glass(soup, f, hole, p, wg, lit, centre)


def boarded(soup, f, outline, out_w, proud, bd, rng, year):
    """Rough boards nailed across a casing's outline, a little apart, each its own: unpainted, put up that year."""
    s0, s1, z0, z1 = outline
    t = bd["thickMm"] * MM
    w0 = out_w + proud + 0.002
    h = z1 - z0
    n = max(2, round(h / 0.19))
    over = bd["overlapMm"] * MM
    soup.use(kind="boarding", scheme="none", year=year, lap=0.5)
    for i in range(n):
        za = z0 + h * i / n + 0.008
        zb = z0 + h * (i + 1) / n - 0.008
        soup.use(seed=rng.random())
        dz = rng.uniform(-0.012, 0.012)
        soup.box(f, s0 - over * rng.uniform(0.3, 1.0), s1 + over * rng.uniform(0.3, 1.0), za + dz, zb + dz, w0,
                 w0 + t)
