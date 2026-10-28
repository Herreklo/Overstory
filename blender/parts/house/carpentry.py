"""A timber wall's carpentry, fitted to its facts: the cladding's courses, the boards in them, and the trims that close
them (corner boards, the drip board over the plinth, the casings round the openings). Fitted parts: functions whose
inputs are the wall (its frame, length, height, gable) and its openings, and the working's sizes from the pack
(packs/<pack>/timber.json, a working's cladding, corner, dripBoard and casing). No defaults: a missing key is an error.

A wall's frame (soup.Frame): s along the wall from its left end seen from outside, z up from the ground floor's level
(the house's base), w out from the sheathing. Every size from the pack is in millimetres.
"""

import math

from soup import add, mul

MM = 0.001


def story_pole(z0, keys, top, exposure):
    """The courses' lines from z0 up to top, as a carpenter sets them out on a story pole: between each pair of key
    heights (a sill's underside, a head's top) the exposure is evened out so that a course line falls on each key,
    within the working's range; a key that cannot be met is passed. Returns the lines, z0 first, top last."""
    lo, hi = exposure[0] * MM, exposure[1] * MM
    nominal = 0.5 * (lo + hi)
    lines = [z0]
    for k in sorted(k for k in keys if z0 + lo * 0.9 <= k <= top - lo * 0.9):
        span = k - lines[-1]
        if span < lo * 0.9:
            continue    # too near the last line: the key falls inside a board
        n = max(1, round(span / nominal))
        if lo * 0.85 <= span / n <= hi * 1.15:
            lines += [lines[-1] + span * i / n for i in range(1, n)] + [k]
        else:
            n = int(span / nominal)
            lines += [lines[-1] + nominal * i for i in range(1, n + 1)]
    # on to the top at the nominal; the last, part course runs up under the eave or the rake
    while top - lines[-1] > nominal * 1.05:
        lines.append(lines[-1] + nominal)
    if top - lines[-1] > 0.02:
        lines.append(top)
    return lines


def gable_half(z, eave, ridge, half):
    """The gable's half-width at height z (half the wall at the eave, nothing at the ridge)."""
    if z <= eave:
        return half
    return max(0.0, half * (ridge - z) / (ridge - eave))


def _intervals(s0, s1, blocks):
    """[s0, s1] less the blocked intervals."""
    out = [(s0, s1)]
    for b0, b1 in sorted(blocks):
        nxt = []
        for a0, a1 in out:
            if b1 <= a0 or b0 >= a1:
                nxt.append((a0, a1))
                continue
            if b0 > a0:
                nxt.append((a0, b0))
            if b1 < a1:
                nxt.append((b1, a1))
        out = nxt
    return [(a, b) for a, b in out if b - a > 0.03]


def _marks(sv, z, s, end, sills, mk):
    """Where water works into a board at (sv, z): how much of a sill's run-off reaches it (1 under the sill's foot,
    fading over dripReachM below and dripSideM to its sides) and how near it is to its own end grain (1 at its end,
    0 past endReachM)."""
    drip = 0.0
    for a, b, zs in sills:
        if z < zs - 1e-4:
            side = max(0.0, 1.0 - max(a - sv, sv - b, 0.0) / mk["dripSideM"])
            drip = max(drip, side * max(0.0, 1.0 - (zs - z) / mk["dripReachM"]))
    near = max(0.0, 1.0 - min(sv - s, end - sv) / mk["endReachM"])
    return (drip, near)


def _face(soup, f, edges, zf, zt, dep, lz, s, end, sills, mk):
    """A board's face from zf to zt between its edges (sa0, sa1 at its foot, sb0, sb1 at its top: a gable's rake
    cuts its ends), cut across where its marks change (near its ends and at the sides of a sill's run-off over it), so
    each corner carries its own (uv7)."""
    sa0, sa1, sb0, sb1 = edges
    lo, hi = min(sa0, sb0), max(sa1, sb1)
    cuts = {lo, hi}
    if soup.level == 0:
        r = mk["endReachM"]
        cuts |= {c for c in (s + r, end - r) if lo < c < hi}
    if soup.level < 2:
        for a, b, zs in sills:
            if zt < zs and zs - zf < mk["dripReachM"]:
                cuts |= {c for c in (a - mk["dripSideM"], a, b, b + mk["dripSideM"]) if lo < c < hi}
    cuts = sorted(cuts)

    def mark(sv, z):
        # from the street a board's end grain is a few pixels, and the face is not cut for it: none drawn
        if soup.level >= 2:
            return (0.0, 0.0)
        m = _marks(sv, z, s, end, sills, mk)
        return m if soup.level == 0 else (m[0], 0.0)
    for c0, c1 in zip(cuts, cuts[1:]):
        a0, a1 = min(max(c0, sa0), sa1), min(max(c1, sa0), sa1)
        b0, b1 = min(max(c0, sb0), sb1), min(max(c1, sb0), sb1)
        if a1 - a0 < 1e-4 and b1 - b0 < 1e-4:
            continue
        soup.quad(f.at(a0, zf, dep(zf)), f.at(a1, zf, dep(zf)), f.at(b1, zt, dep(zt)), f.at(b0, zt, dep(zt)),
                  ta=[(a0, zf), (a1, zf), (b1, zt), (b0, zt)], laps=(lz(zf), lz(zf), lz(zt), lz(zt)),
                  marks=(mark(a0, zf), mark(a1, zf), mark(b1, zt), mark(b0, zt)))


def clad(soup, f, wall, openings, lines, cl, rng, shelter, patches=(), sills=None, butts=()):
    """Rebated boards over the wall, course by course. A single-rebated board's face leans back by its step, so each
    course stands proud of the one above it; a double-rebated board's faces lie in one plane, a groove at each joint.

    wall: dict(length, eave, ridge or None (no gable), left, right: the corner boards' widths at each end).
    openings: casing outlines (s0, s1, z0, z1) the boards butt against.
    lines: the story pole's course lines. cl: the working's cladding. rng: the wall's stream (hashing.Stream).
    shelter(z): how sheltered a height is (0 open, 1 under the eave's overhang).
    patches: (s0, s1, z0, z1, year): where a later change boarded in part of an old opening; the boards there are
    that year's, cut at the old opening's sides.
    sills: (s0, s1, z) the sills whose run-off reaches the boards (their outline's foot), else each opening's foot.
    butts: outlines (s0, s1, z0, z1) the boards stop at with no trim over their ends (a later infill, its own boards
    thinner): each board ending there shows its end grain."""
    but = cl["butMm"] * MM
    top = but - cl["stepMm"] * MM
    groove = cl["grooveMm"] * MM
    blen = (cl["boardLengthMm"][0] * MM, cl["boardLengthMm"][1] * MM)
    gap = cl["jointGapMm"] * MM
    jit = cl["tiltJitterMm"] * MM
    L, eave, ridge = wall["length"], wall["eave"], wall.get("ridge")
    half = L / 2
    if soup.level >= 2:
        # the wall as planes: up to the eave, and the gable over it, the openings cut out of them
        top_ = ridge - 0.08 if ridge is not None else lines[-1]
        if ridge is not None and top_ > eave + 0.1:
            # a gable that starts at its eave (an ark's, over its tie) is one plane
            lines = [lines[0], eave, top_] if eave > lines[0] + 0.01 else [lines[0], top_]
        else:
            lines = [lines[0], lines[-1]]
    # the sills water runs off: each casing's foot, over its width
    if sills is None:
        sills = [(o[0], o[1], o[2]) for o in openings]
    openings = list(openings) + list(butts)

    def butted(sv, side, za, zb):
        # whether a run's end at sv meets an infill's side (side 0: its left side, s0; 1: its right, s1)
        return any(abs(sv - b[side]) < 1e-4 and b[2] < zb - 0.004 and b[3] > za + 0.004 for b in butts)
    prev_joints = []
    boards = 0
    for i in range(len(lines) - 1):
        za, zb = lines[i], lines[i + 1]
        e = zb - za
        lap = min(0.03, e * 0.2)
        w_hi = top + (but - top) * lap / (e + lap)   # the face's depth where the next course covers it
        if ridge is not None and zb > eave:
            ha, hb = gable_half(za, eave, ridge, half), gable_half(zb, eave, ridge, half)
            if hb < 0.05:
                break
            run = (half - ha, half + ha, half - hb, half + hb)
        else:
            run = (wall["left"], L - wall["right"], wall["left"], L - wall["right"])
        over = [o for o in openings if o[2] < zb - 0.004 and o[3] > za + 0.004]
        s_lo = min(run[0], run[2])
        s_hi = max(run[1], run[3])

        def year_of(c0, c1):
            return next((p[4] for p in patches if p[0] <= c0 + 1e-4 and c1 <= p[1] + 1e-4
                         and p[2] < zb - 0.004 and p[3] > za + 0.004), None)

        # the course's runs between the openings, cut where a patch starts and ends; and over an opening whose
        # casing ends inside the course, the board notched round it (above its head, below its sill)
        runs = []
        for a0, a1 in _intervals(s_lo, s_hi, [(o[0], o[1]) for o in over]):
            cuts = sorted({a0, a1} | {c for p in patches if p[2] < zb - 0.004 and p[3] > za + 0.004
                                      for c in (p[0], p[1]) if a0 < c < a1})
            runs += [(c0, c1, year_of(c0, c1), za, zb) for c0, c1 in zip(cuts, cuts[1:])]
        for o in over:
            if o[3] < zb - 0.01:
                runs.append((o[0], o[1], year_of(o[0], o[1]), o[3], zb))
            if o[2] > za + 0.01:
                runs.append((o[0], o[1], year_of(o[0], o[1]), za, o[2]))
        joints = []
        for a0, a1, yr, z_lo, z_hi in runs:
            # boards along the run, their joints kept off the course below's
            soup.use(year=float(yr if yr is not None else wall["year"]))
            notch = z_lo > za + 1e-4
            s = a0
            while s < a1 - 0.03:
                ln = rng.uniform(*blen)
                end = min(a1, s + ln)
                if a1 - end < 0.6 and yr is None:
                    end = a1
                for _ in range(6):
                    if end >= a1 or all(abs(end - j) > 0.35 for j in prev_joints):
                        break
                    end = min(a1, end + 0.4)
                piece = rng.random()
                tilt = rng.uniform(-jit, jit)
                b_but, b_hi = but + tilt * 0.5, w_hi + tilt

                def dep(z):
                    return b_but + (b_hi - b_but) * (z - za) / max(1e-6, zb - za)
                soup.use(kind="board", seed=piece, lap=0.0, shelter=shelter(0.5 * (za + zb)), scheme=wall["scheme"])
                # the face: its corners on the course's run (the gable's rake cuts its ends)
                def clip(z, s):
                    if ridge is None or z <= eave:
                        return s
                    h = gable_half(z, eave, ridge, half)
                    return min(max(s, half - h), half + h)
                zf = z_lo if notch else za + groove
                zt = z_hi
                sa0, sa1 = clip(zf, s), clip(zf, end)
                sb0, sb1 = clip(zt, s), clip(zt, end)
                if sa1 - sa0 > 0.02 or sb1 - sb0 > 0.02:
                    lz = lambda z: (z - za) / max(1e-6, zb - za)
                    _face(soup, f, (sa0, sa1, sb0, sb1), zf, zt, dep, lz, s, end, sills, cl["marks"])
                    soup.use(kind="underside")
                    if notch or soup.level >= 2:
                        pass    # (its foot sits on the casing's head)
                    elif groove > 0 and soup.level > 0:
                        # the groove as one face sloping from the slot's foot out to the board's: its shadow line
                        soup.quad(f.at(sa0, za, but - groove), f.at(sa1, za, but - groove), f.at(sa1, zf, b_but),
                                  f.at(sa0, zf, b_but), ta=[(sa0, 0.0), (sa1, 0.0), (sa1, groove), (sa0, groove)])
                    elif groove > 0:
                        # the joint's groove: the board's rebated underside and the slot's back
                        soup.quad(f.at(sa0, zf, but - groove), f.at(sa1, zf, but - groove), f.at(sa1, zf, b_but),
                                  f.at(sa0, zf, b_but), ta=[(sa0, 0.0), (sa1, 0.0), (sa1, 0.02), (sa0, 0.02)])
                        soup.quad(f.at(sa0, za, but - groove), f.at(sa1, za, but - groove),
                                  f.at(sa1, zf, but - groove), f.at(sa0, zf, but - groove),
                                  ta=[(sa0, 0.0), (sa1, 0.0), (sa1, groove), (sa0, groove)])
                    else:
                        # its lap edge: the underside that throws the course's shadow line
                        soup.quad(f.at(sa0, za, w_hi), f.at(sa1, za, w_hi), f.at(sa1, za, b_but),
                                  f.at(sa0, za, b_but), ta=[(sa0, 0.0), (sa1, 0.0), (sa1, 0.02), (sa0, 0.02)])
                    # its ends where it meets the next board (end grain, a hair's gap)
                    soup.use(kind="endgrain")
                    if soup.level > 0:
                        pass
                    elif end < a1 - 0.01:
                        soup.quad(f.at(sa1 - gap, zf, dep(zf)), f.at(sa1 - gap, zf, 0.0), f.at(sb1 - gap, zt, 0.0),
                                  f.at(sb1 - gap, zt, dep(zt)))
                    if s > a0 + 0.01:
                        soup.quad(f.at(sa0, zf, 0.0), f.at(sa0, zf, dep(zf)), f.at(sb0, zt, dep(zt)), f.at(sb0, zt, 0.0))
                    if soup.level == 0:
                        # where the board stops at an infill with no trim over its end: its end grain, standing
                        # proud of the thinner boards beside it
                        if end >= a1 - 0.01 and butted(a1, 0, za, zb):
                            soup.quad(f.at(sa1, zf, dep(zf)), f.at(sa1, zf, 0.0), f.at(sb1, zt, 0.0), f.at(sb1, zt, dep(zt)))
                        if s <= a0 + 0.01 and butted(a0, 1, za, zb):
                            soup.quad(f.at(sa0, zf, 0.0), f.at(sa0, zf, dep(zf)), f.at(sb0, zt, dep(zt)), f.at(sb0, zt, 0.0))
                    boards += 1
                if end < a1 and not notch and z_hi >= zb - 1e-4:
                    joints.append(end)
                s = end + gap
        prev_joints = joints
    return boards


def corner_boards(soup, f, wall, z0, z1, cb, out_w, extend_left, extend_right, rng):
    """The corner boards at the wall's ends, standing proud of the cladding (out_w: the cladding's face). A wall whose
    board laps its neighbour's runs past the corner by that board's thickness."""
    pu = soup.push
    w = cb["widthMm"] * MM
    # proud as the casings are, by the style's push: the edge the wall turns on, found against the next wall's light
    t = out_w + cb["proudMm"] * MM * pu["trimProud"]
    w0 = out_w if soup.level >= 2 else 0.0     # at the city level only its part proud of the cladding (casing)
    L = wall["length"]
    ch = pu["chamferMm"]["trim"] * MM
    soup.use(kind="trim", lap=0.5, scheme="trim")
    for side, ext in ((0, extend_left), (1, extend_right)):
        soup.use(seed=rng.random())
        # its arrises chamfered (near); its foot on the drip board and its head under the eave hidden
        if side == 0:
            soup.bbox(f, -ext, w, z0, z1, w0, t, ch, skip=("back", "bottom", "top"), grain="z")
        else:
            soup.bbox(f, L - w, L + ext, z0, z1, w0, t, ch, skip=("back", "bottom", "top"), grain="z")


def drip_board(soup, f, s0, s1, z0, db, out_w, rng):
    """The drip board along the cladding's foot, over the plinth: a thick board whose top slopes out to shed water,
    proud by the style's push, its nose's arrises chamfered (near), so its lit top and its dark underside read as one
    heavy line over the plinth."""
    pu = soup.push
    h, p, sl = db["heightMm"] * MM, db["proudMm"] * MM * pu["trimProud"], db["slopeMm"] * MM
    soup.use(kind="trim", seed=rng.random(), lap=0.5, scheme="trim", shelter=0.0)
    w1 = out_w + p
    wb = out_w * 0.5
    c = min(pu["chamferMm"]["trim"] * MM, 0.25 * h) if soup.level == 0 else 0.0
    # its section (w, z): the underside, the nose, the top weathering back up into the cladding
    k = sl / max(w1 - wb, 1e-6)
    pts = [(0.0, z0), (w1 - c, z0), (w1, z0 + c), (w1, z0 + h - c), (w1 - c, z0 + h + c * k), (wb, z0 + h + sl),
           (0.0, z0 + h + sl)] if c > 0 else [(0.0, z0), (w1, z0), (w1, z0 + h), (wb, z0 + h + sl), (0.0, z0 + h + sl)]
    section(soup, f, s0, s1, pts)
    return z0 + h


def section(soup, f, s0, s1, pts, ta_along=True, ends=(True, True)):
    """A piece drawn as a section swept along s from s0 to s1: pts its outline in (w, z), any order round it, its
    end caps drawn where ends says (each cap the outline's convex hull, as a sawn end is flat)."""
    area = sum(pts[i][0] * pts[(i + 1) % len(pts)][1] - pts[(i + 1) % len(pts)][0] * pts[i][1] for i in range(len(pts)))
    if area < 0:
        pts = pts[::-1]
    run = 0.0
    for i in range(len(pts)):
        (wa, za), (wb, zb) = pts[i], pts[(i + 1) % len(pts)]
        d = math.hypot(wb - wa, zb - za)
        if d < 1e-6:
            continue
        nw, nz = (zb - za) / d, -(wb - wa) / d
        out = add(mul(f.n, nw), mul(f.v, nz))
        soup.poly([f.at(s0, za, wa), f.at(s1, za, wa), f.at(s1, zb, wb), f.at(s0, zb, wb)], out,
                  ta=[(s0, run), (s1, run), (s1, run + d), (s0, run + d)])
        run += d
    hull = _hull(pts)
    for s, sgn, on in ((s0, -1.0, ends[0]), (s1, 1.0, ends[1])):
        if not on:
            continue
        for k in range(1, len(hull) - 1):
            soup.poly([f.at(s, hull[0][1], hull[0][0]), f.at(s, hull[k][1], hull[k][0]),
                       f.at(s, hull[k + 1][1], hull[k + 1][0])], mul(f.u, sgn),
                      ta=[(hull[0][0], hull[0][1]), (hull[k][0], hull[k][1]), (hull[k + 1][0], hull[k + 1][1])])


def _hull(pts):
    """The convex hull of 2-D points, counter-clockwise (monotone chain)."""
    p = sorted(set(pts))
    if len(p) < 3:
        return p

    def turn(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    lo, hi = [], []
    for q in p:
        while len(lo) >= 2 and turn(lo[-2], lo[-1], q) <= 0:
            lo.pop()
        lo.append(q)
    for q in reversed(p):
        while len(hi) >= 2 and turn(hi[-2], hi[-1], q) <= 0:
            hi.pop()
        hi.append(q)
    return lo[:-1] + hi[:-1]


def sill_section(w_back, w_wall, w_nose, z_top, slope, thick, ch, groove, level):
    """A window sill's section in (w, z): flat under the frame, then its weathered top falling to the nose, the nose
    with its arrises eased, and under the nose the drip groove that stops water running back to the wall.
    groove: (width, depth, its distance back from the nose), in metres."""
    zt_n = z_top - slope
    zb = z_top - thick
    if level > 0:
        return [(w_back, z_top), (w_wall, z_top), (w_nose, zt_n), (w_nose, zb), (w_back, zb)]
    gw, gd, go = groove
    c = min(ch, 0.3 * (zt_n - zb))
    return [(w_back, z_top), (w_wall, z_top), (w_nose - c, zt_n + c * slope / max(w_nose - w_wall, 1e-6)),
            (w_nose, zt_n - c), (w_nose, zb + c), (w_nose - c, zb),
            (w_nose - go, zb), (w_nose - go, zb + gd), (w_nose - go - gw, zb + gd), (w_nose - go - gw, zb),
            (w_back, zb)]


def casing(soup, f, s0, s1, z0, z1, cs, out_w, rng, with_sill=True):
    """A casing round an opening whose hole is (s0, s1, z0, z1): side casings, a head with its bed mould and cap (the
    drip that sheds water off the head), and a thick sill whose top weathers out to a nose with a drip groove under
    it, its horns past the sides. Proportions are the working's, pushed by the style (timber.json, push); arrises
    are chamfered where the near level draws them. Returns the casing's outline, the line the cladding butts
    against."""
    pu = soup.push
    ch = pu["chamferMm"]
    cw, cp = cs["widthMm"] * MM, cs["proudMm"] * MM * pu["trimProud"]
    hd = cs["headMm"] * MM
    cap = cs["capMm"] * MM * pu["capThick"]
    capp = cs["capProudMm"] * MM * pu["capProud"]
    sh, sp = cs["sillMm"] * MM * pu["sillThick"], cs["sillProudMm"] * MM * pu["sillProud"]
    horn = cs["hornMm"] * MM
    w = out_w + cp
    w0 = out_w if soup.level >= 2 else 0.0
    wf = out_w - pu["frameSetBackMm"] * MM
    soup.use(kind="trim", lap=0.5, scheme="trim")
    zs = z0 - (sh if with_sill else 0.0)
    slope = 0.18 * sp if with_sill else 0.0
    # the side casings stand on the sill's weathered top (their feet under it)
    z_foot = z0 - slope * max(0.0, w - wf) / max(sp + out_w - wf, 1e-6) - 0.004 if with_sill else z0
    soup.use(seed=rng.random())
    soup.bbox(f, s0 - cw, s0, z_foot, z1, w0, w, ch["trim"] * MM, skip=("back", "top", "bottom"), grain="z")
    soup.use(seed=rng.random())
    soup.bbox(f, s1, s1 + cw, z_foot, z1, w0, w, ch["trim"] * MM, skip=("back", "top", "bottom"), grain="z")
    soup.use(seed=rng.random())
    soup.bbox(f, s0 - cw, s1 + cw, z1, z1 + hd, w0, w, ch["trim"] * MM, skip=("back", "top"))
    zc = z1 + hd
    if cap > 0:
        bh, bp = (v * MM for v in pu["bedMouldMm"])
        # the bed mould under the cap's nose: the step that makes the head read as a cornice in small
        soup.use(seed=rng.random())
        soup.bbox(f, s0 - cw - bp * 0.6, s1 + cw + bp * 0.6, zc - bh, zc, w0, w + bp, ch["frame"] * MM,
                  skip=("back", "top"))
        soup.use(seed=rng.random())
        reach = max(capp, cp + bp + 0.02)
        soup.bbox(f, s0 - cw - (reach - cp), s1 + cw + (reach - cp), zc, zc + cap, w0, out_w + reach,
                  ch["trim"] * MM)
    if cs.get("brackets"):
        # a bracket on each side casing under the cap's ends, tapering down from the cap's depth
        bh, bp, bt = (v * MM for v in cs["brackets"])
        bp *= pu["capProud"]
        for sc in (s0 - cw / 2, s1 + cw / 2):
            soup.use(seed=rng.random())
            a, b, zt_, zb_ = sc - bt / 2, sc + bt / 2, zc, zc - bh
            wt, wb = w + bp, w + bp * 0.25
            soup.poly([f.at(a, zb_, wb), f.at(b, zb_, wb), f.at(b, zt_, wt), f.at(a, zt_, wt)],
                      add(f.n, mul(f.v, -bp / bh)))
            soup.poly([f.at(a, zb_, w), f.at(a, zb_, wb), f.at(a, zt_, wt), f.at(a, zt_, w)], mul(f.u, -1.0))
            soup.poly([f.at(b, zb_, wb), f.at(b, zb_, w), f.at(b, zt_, w), f.at(b, zt_, wt)], f.u)
            soup.poly([f.at(a, zb_, w), f.at(b, zb_, w), f.at(b, zb_, wb), f.at(a, zb_, wb)], mul(f.v, -1.0))
    if with_sill:
        soup.use(seed=rng.random())
        gw, gd, go = (v * MM for v in pu["dripGrooveMm"])
        pts = sill_section(wf - 0.11, wf, out_w + sp, z0, slope, sh, ch["sill"] * MM, (gw, gd, go), soup.level)
        section(soup, f, s0 - cw - horn, s1 + cw + horn, pts)
    return (s0 - cw, s1 + cw, zs, zc + cap)


def reveal(soup, f, s0, s1, z0, z1, w_front, w_back):
    """The opening's lining from the frame's face (w_back) out to w_front, where the casing's own inner faces take
    over: four faces looking into the hole."""
    if soup.level >= 2 or w_front <= w_back + 1e-4:
        return
    soup.use(kind="trim", lap=0.5, scheme="trim")
    soup.quad(f.at(s0, z0, w_back), f.at(s0, z0, w_front), f.at(s0, z1, w_front), f.at(s0, z1, w_back))
    soup.quad(f.at(s1, z0, w_front), f.at(s1, z0, w_back), f.at(s1, z1, w_back), f.at(s1, z1, w_front))
    soup.quad(f.at(s0, z1, w_back), f.at(s0, z1, w_front), f.at(s1, z1, w_front), f.at(s1, z1, w_back))
