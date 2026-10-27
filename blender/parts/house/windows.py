"""Windows, fitted to their hole: the frame, the sashes, the glazing bars (modelled, never cut out), and the glass,
which carries the pane's place in the window and the room's seed so the shader can draw a room behind it. A boarded
window is covered by rough boards nailed upright over its casing. The window's kind is the pack's (timber.json, windows),
chosen by the house's era or by the year its windows were replaced.
"""

MM = 0.001


# the faces of a framing piece that lie against its neighbours: a rail's ends against the stiles or jambs, a stile's
# or post's ends against the rails, an outer stile's or jamb's side against the frame or the reveal
RAIL, POST = ("back", "left", "right"), ("back", "top", "bottom")


def _frame_box(soup, f, s0, s1, z0, z1, w0, w1, c, grain="s", skip=("back",)):
    soup.bbox(f, s0, s1, z0, z1, w0, w1, c, skip=skip, grain=grain)


def _sash(soup, f, s0, s1, z0, z1, wf, sa, bar, rows, cols, rng, lit, scheme, glass_w):
    """One sash: its four rails and stiles (the bottom rail deeper), its glazing bars (moulded: their outer arrises
    chamfered wide, so each bar catches the light as a ridge), and its panes' opening."""
    ch = soup.push["chamferMm"]
    d = 0.045
    soup.use(kind="sash", scheme=scheme, seed=rng.random(), lap=0.5)
    cs, cb = ch["sash"] * MM, ch["bar"] * MM
    _frame_box(soup, f, s0, s1, z0, z0 + sa * 1.25, wf - d, wf, cs, skip=RAIL)    # the bottom rail, deeper than the rest
    _frame_box(soup, f, s0, s1, z1 - sa, z1, wf - d, wf, cs, skip=RAIL)
    _frame_box(soup, f, s0, s0 + sa, z0 + sa * 1.25, z1 - sa, wf - d, wf, cs, grain="z", skip=POST + ("left",))
    _frame_box(soup, f, s1 - sa, s1, z0 + sa * 1.25, z1 - sa, wf - d, wf, cs, grain="z", skip=POST + ("right",))
    gs0, gs1, gz0, gz1 = s0 + sa, s1 - sa, z0 + sa * 1.25, z1 - sa
    bw = bar
    if bw > 0:
        for i in range(1, cols):
            s = gs0 + (gs1 - gs0) * i / cols
            _frame_box(soup, f, s - bw / 2, s + bw / 2, gz0, gz1, wf - d * 0.7, wf - 0.006, cb, grain="z", skip=POST)
        for j in range(1, rows):
            z = gz0 + (gz1 - gz0) * j / rows
            _frame_box(soup, f, gs0, gs1, z - bw / 2, z + bw / 2, wf - d * 0.7, wf - 0.006, cb, skip=RAIL)
    return (gs0, gs1, gz0, gz1)


def glass(soup, f, hole, pane, wg, lit, centre):
    """The glass over a sash's opening, its surface coordinates the window's own (metres from its foot, centred),
    and the window's half width and height on its place channels (lap, shelter), for the room the shader draws."""
    s0, s1, z0, z1 = pane
    kept = dict(lap=soup.a["lap"], shelter=soup.a["shelter"])
    soup.use(kind="glass", scheme="none", lit=lit, lap=0.5 * (hole[1] - hole[0]), shelter=hole[3] - hole[2])
    c, base = centre, hole[2]
    soup.quad(f.at(s0, z0, wg), f.at(s1, z0, wg), f.at(s1, z1, wg), f.at(s0, z1, wg),
              ta=[(s0 - c, z0 - base), (s1 - c, z0 - base), (s1 - c, z1 - base), (s0 - c, z1 - base)])
    soup.use(**kept)


def window(soup, f, hole, spec, out_w, rng, lit, scheme):
    """A window in its hole (s0, s1, z0, z1): the frame set back into the opening behind the casing (the style's
    push: a deep reveal), the sashes set back in the frame, the glass back in the sashes' rebates."""
    s0, s1, z0, z1 = hole
    pu = soup.push
    fr, sa, bar = spec["frameMm"] * MM, spec["sashMm"] * MM, spec["barMm"] * MM
    top = spec["top"] * MM
    cols, rows = spec["cols"], spec["rows"]
    wf = out_w - pu["frameSetBackMm"] * MM
    depth = 0.11
    cf = pu["chamferMm"]["frame"] * MM
    centre = 0.5 * (s0 + s1)
    if soup.level >= 2:
        glass(soup, f, hole, (s0, s1, z0, z1), wf - 0.03, lit, centre)
        return
    soup.use(kind="sash", scheme=scheme, seed=rng.random(), lap=0.5)
    _frame_box(soup, f, s0, s1, z0, z0 + fr, wf - depth, wf, cf, skip=RAIL)
    _frame_box(soup, f, s0, s1, z1 - fr, z1, wf - depth, wf, cf, skip=RAIL)
    _frame_box(soup, f, s0, s0 + fr, z0 + fr, z1 - fr, wf - depth, wf, cf, grain="z", skip=POST + ("left",))
    _frame_box(soup, f, s1 - fr, s1, z0 + fr, z1 - fr, wf - depth, wf, cf, grain="z", skip=POST + ("right",))
    i0, i1, j0, j1 = s0 + fr, s1 - fr, z0 + fr, z1 - fr
    ws = wf - pu["sashSetBackMm"] * MM
    wg = ws - pu["glassSetBackMm"] * MM
    if top > 0:
        # the T-post: a transom under the top light and a post between the casements below it
        zt = j1 - top
        soup.use(kind="sash", scheme=scheme, seed=rng.random())
        _frame_box(soup, f, i0, i1, zt - fr * 0.5, zt + fr * 0.5, wf - depth, wf, cf, skip=RAIL)
        p = _sash(soup, f, i0, i1, zt + fr * 0.5, j1, ws, sa * 0.85, bar, 1, 2 if bar > 0 else 1, rng, lit, scheme, wg)
        glass(soup, f, hole, p, wg, lit, centre)
        j1 = zt - fr * 0.5
        if cols == 2:
            sm = 0.5 * (i0 + i1)
            soup.use(kind="sash", scheme=scheme, seed=rng.random())
            _frame_box(soup, f, sm - fr * 0.5, sm + fr * 0.5, j0, j1, wf - depth, wf, cf, grain="z", skip=POST)
            for a, b in ((i0, sm - fr * 0.5), (sm + fr * 0.5, i1)):
                p = _sash(soup, f, a, b, j0, j1, ws, sa, bar, rows, 1, rng, lit, scheme, wg)
                glass(soup, f, hole, p, wg, lit, centre)
            return
    if cols == 2 and spec["post"]:
        # two casements either side of a fixed post
        sm = 0.5 * (i0 + i1)
        soup.use(kind="sash", scheme=scheme, seed=rng.random())
        _frame_box(soup, f, sm - fr * 0.5, sm + fr * 0.5, j0, j1, wf - depth, wf, cf, grain="z", skip=POST)
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


def _plank(soup, f, sc, zc, w, h, w0, t, turn, across=False):
    """One rough board standing in an opening from w0 out by t, its centre (sc, zc), w wide and h long, turned in the
    wall's plane by turn (radians): its face and its four edges. Rigid: only turned. Its marks (uv7) are its half width
    and its length, so the wood (House.shader) knows its edges and both its ends; a batten across the boards (across)
    gives its half width negative, so the wood runs no rust along it (rust runs down, not along a level batten)."""
    import math
    c, s_ = math.cos(turn), math.sin(turn)

    def at(a, z, d):
        return f.at(sc + a * c - z * s_, zc + a * s_ + z * c, d)
    q = ((-w / 2, -h / 2), (w / 2, -h / 2), (w / 2, h / 2), (-w / 2, h / 2))
    mk = (-w / 2 if across else w / 2, h)
    front = [at(a, z, w0 + t) for a, z in q]
    # the grain runs up the board: its surface coordinates along (s) its length; its lap, how far below its top
    soup.quad(*front, ta=[(z + zc, a) for a, z in q], laps=[h / 2 - z for a, z in q], marks=[mk] * 4)
    if soup.level > 0 and t < soup.err:
        return
    back = [at(a, z, w0) for a, z in q]
    for i in range(4):
        j = (i + 1) % 4
        soup.quad(back[i], back[j], front[j], front[i], ta=[(q[i][1] + zc, 0.0), (q[j][1] + zc, 0.0), (q[j][1] + zc, t), (q[i][1] + zc, t)],
                  laps=[h / 2 - q[i][1], h / 2 - q[j][1], h / 2 - q[j][1], h / 2 - q[i][1]], marks=[mk] * 4)


def boarded(soup, f, hole, out_w, proud, bd, rng, year, sill=None):
    """An empty house's opening boarded up: rough sawn boards, reused and of mixed widths, stood upright in the
    opening between its jambs, on its sill and cut to fit under its head, a little behind the casing's face, butted
    with uneven gaps, a board now and then cut short or a little out of true; left unpainted, put up that year
    (timber.json, boarding). hole is the opening (s0, s1, z0, z1); sill its sill's (height, proud) (m), whose top
    slopes out and down from the opening's foot, or None (a door's threshold). The boards draw from their own stream
    (one draw of the wall's), so the wall's other parts keep their seeds."""
    import hashing as HS
    import math
    brng = HS.Stream("boarding", rng.randint(0, 2 ** 31 - 1))
    s0, s1, z0, z1 = hole
    t = bd["thickMm"] * MM
    face = out_w + proud
    soup.use(kind="boarding", scheme="none", year=year, lap=0.5)
    if soup.level >= 2:
        # (from the city the boarding is one face in the opening)
        soup.use(seed=brng.random())
        w = face - bd["setBackMm"][0] * MM
        soup.quad(f.at(s0, z0, w), f.at(s1, z0, w), f.at(s1, z1, w), f.at(s0, z1, w),
                  ta=[(z0, s0), (z0, s1), (z1, s1), (z1, s0)], marks=[((s1 - s0) / 2, z1 - z0)] * 4)
        return
    planks = []
    a = s0 + 0.002
    end = s1 - 0.002
    while a < end - 0.04:
        w = min(brng.uniform(*bd["widthMm"]) * MM, end - a)
        if end - a - w < bd["widthMm"][0] * MM * 0.6:
            w = end - a
        planks.append((a, w))
        a += w + brng.uniform(*bd["gapMm"]) * MM
    inner = [i for i in range(1, len(planks) - 1)]
    skew = inner[brng.randint(0, len(inner) - 1)] if inner and brng.random() < bd["outOfTrueShare"] else -1
    for i, (a, w) in enumerate(planks):
        # (never into the window's frame behind it)
        w0 = max(face - brng.uniform(*bd["setBackMm"]) * MM - t, out_w - 0.002)
        # it stands on the sill where the sill's slope meets the board's back, and is cut to fit under the head
        lo = z0 if sill is None else z0 - sill[0] * 0.35 * max(0.0, w0) / (out_w + sill[1])
        hi = z1 - brng.uniform(*bd["topGapMm"]) * MM
        turn = math.radians(brng.uniform(*bd["outOfTrueDeg"]) * (1 if brng.random() < 0.5 else -1)) if i == skew else 0.0
        # a board out of true was nailed on last, over its neighbours' faces, and cut to clear the head and sill
        if turn:
            w0 = face - bd["setBackMm"][0] * MM
            hi -= abs(math.sin(turn)) * w
            lo = max(lo, z0 if sill is None else z0 - sill[0] * 0.35 * max(0.0, w0) / (out_w + sill[1])) + abs(math.sin(turn)) * w
        soup.use(seed=brng.random())
        _plank(soup, f, a + w / 2, 0.5 * (lo + hi), w, hi - lo, w0, t, turn)
    # battens across hold the boards together, nailed over their faces (the byarkiv's Pedersgata 81, 1989): one for
    # about every spacingM of the opening's height, each a little out of level
    bt = bd["battens"]
    n = max(1, round((z1 - z0) / bt["spacingM"]))
    for k in range(n):
        bw = brng.uniform(*bt["widthMm"]) * MM
        zc = z0 + (z1 - z0) * (k + 0.5) / n + brng.uniform(-0.25, 0.25) * (z1 - z0) / n
        zc = min(max(zc, z0 + bw), z1 - bw)
        turn = math.radians(90.0 + brng.uniform(-1.0, 1.0) * bt["outOfLevelDeg"])
        length = (s1 - s0) - 0.004 - abs(math.cos(turn)) * bw
        soup.use(seed=brng.random())
        _plank(soup, f, 0.5 * (s0 + s1), zc, bw, length, face - bd["setBackMm"][0] * MM, bt["thickMm"] * MM, turn, across=True)
