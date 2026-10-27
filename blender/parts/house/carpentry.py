"""A timber wall's carpentry, fitted to its facts: the cladding's courses, the boards in them, and the trims that close
them (corner boards, the drip board over the plinth, the casings round the openings). Fitted parts: functions whose
inputs are the wall (its frame, length, height, gable) and its openings, and the working's sizes from the pack
(packs/<pack>/timber.json, a working's cladding, corner, dripBoard and casing). No defaults: a missing key is an error.

A wall's frame (soup.Frame): s along the wall from its left end seen from outside, z up from the ground floor's level
(the house's base), w out from the sheathing. Every size from the pack is in millimetres.
"""

import math

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


def clad(soup, f, wall, openings, lines, cl, rng, shelter, patches=()):
    """Rebated boards over the wall, course by course. A single-rebated board's face leans back by its step, so each
    course stands proud of the one above it; a double-rebated board's faces lie in one plane, a groove at each joint.

    wall: dict(length, eave, ridge or None (no gable), left, right: the corner boards' widths at each end).
    openings: casing outlines (s0, s1, z0, z1) the boards butt against.
    lines: the story pole's course lines. cl: the working's cladding. rng: the wall's stream (hashing.Stream).
    shelter(z): how sheltered a height is (0 open, 1 under the eave's overhang).
    patches: (s0, s1, z0, z1, year): where a later change boarded in part of an old opening; the boards there are
    that year's, cut at the old opening's sides."""
    but = cl["butMm"] * MM
    top = but - cl["stepMm"] * MM
    groove = cl["grooveMm"] * MM
    blen = (cl["boardLengthMm"][0] * MM, cl["boardLengthMm"][1] * MM)
    gap = cl["jointGapMm"] * MM
    jit = cl["tiltJitterMm"] * MM
    L, eave, ridge = wall["length"], wall["eave"], wall.get("ridge")
    half = L / 2
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
                    p = [f.at(sa0, zf, dep(zf)), f.at(sa1, zf, dep(zf)), f.at(sb1, zt, dep(zt)), f.at(sb0, zt, dep(zt))]
                    t = [(sa0, zf), (sa1, zf), (sb1, zt), (sb0, zt)]
                    lz = lambda z: (z - za) / max(1e-6, zb - za)
                    soup.quad(*p, ta=t, laps=(lz(zf), lz(zf), lz(zt), lz(zt)))
                    soup.use(kind="underside")
                    if notch:
                        pass    # (its foot sits on the casing's head)
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
                    if end < a1 - 0.01:
                        soup.quad(f.at(sa1 - gap, zf, dep(zf)), f.at(sa1 - gap, zf, 0.0), f.at(sb1 - gap, zt, 0.0),
                                  f.at(sb1 - gap, zt, dep(zt)))
                    if s > a0 + 0.01:
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
    w = cb["widthMm"] * MM
    t = out_w + cb["proudMm"] * MM
    L = wall["length"]
    soup.use(kind="trim", lap=0.5, scheme="trim")
    for side, ext in ((0, extend_left), (1, extend_right)):
        soup.use(seed=rng.random())
        if side == 0:
            soup.box(f, -ext, w, z0, z1, 0.0, t, grain="z")
        else:
            soup.box(f, L - w, L + ext, z0, z1, 0.0, t, grain="z")


def drip_board(soup, f, s0, s1, z0, db, out_w, rng):
    """The drip board along the cladding's foot, over the plinth: a thick board whose top slopes out to shed water."""
    h, p, sl = db["heightMm"] * MM, db["proudMm"] * MM, db["slopeMm"] * MM
    soup.use(kind="trim", seed=rng.random(), lap=0.5, scheme="trim", shelter=0.0)
    w1 = out_w + p
    # front, its top sloping back up to the cladding, its underside
    soup.quad(f.at(s0, z0, w1), f.at(s1, z0, w1), f.at(s1, z0 + h, w1), f.at(s0, z0 + h, w1),
              ta=[(s0, z0), (s1, z0), (s1, z0 + h), (s0, z0 + h)])
    soup.quad(f.at(s0, z0 + h, w1), f.at(s1, z0 + h, w1), f.at(s1, z0 + h + sl, out_w * 0.5),
              f.at(s0, z0 + h + sl, out_w * 0.5), ta=[(s0, 0), (s1, 0), (s1, 0.04), (s0, 0.04)])
    soup.quad(f.at(s0, z0, 0.0), f.at(s1, z0, 0.0), f.at(s1, z0, w1), f.at(s0, z0, w1),
              ta=[(s0, 0), (s1, 0), (s1, 0.04), (s0, 0.04)])
    for s, sgn in ((s0, -1), (s1, 1)):
        a, b = (f.at(s, z0, 0.0), f.at(s, z0, w1)) if sgn > 0 else (f.at(s, z0, w1), f.at(s, z0, 0.0))
        c, d = (f.at(s, z0 + h + sl, out_w * 0.5), f.at(s, z0 + h, w1)) if sgn < 0 else \
               (f.at(s, z0 + h, w1), f.at(s, z0 + h + sl, out_w * 0.5))
        soup.quad(a, b, c if sgn > 0 else d, d if sgn > 0 else c)
    return z0 + h


def casing(soup, f, s0, s1, z0, z1, cs, out_w, rng, with_sill=True):
    """A casing round an opening whose hole is (s0, s1, z0, z1): side casings, a head with its cap (the drip that
    sheds water off the head) and a sloped sill with horns past the sides. Returns the casing's outline, the line
    the cladding butts against."""
    cw, cp = cs["widthMm"] * MM, cs["proudMm"] * MM
    hd, cap, capp = cs["headMm"] * MM, cs["capMm"] * MM, cs["capProudMm"] * MM
    sh, sp, horn = cs["sillMm"] * MM, cs["sillProudMm"] * MM, cs["hornMm"] * MM
    w = out_w + cp
    soup.use(kind="trim", lap=0.5, scheme="trim")
    zs = z0 - (sh if with_sill else 0.0)
    soup.use(seed=rng.random())
    soup.box(f, s0 - cw, s0, z0, z1, 0.0, w, grain="z")
    soup.use(seed=rng.random())
    soup.box(f, s1, s1 + cw, z0, z1, 0.0, w, grain="z")
    soup.use(seed=rng.random())
    soup.box(f, s0 - cw, s1 + cw, z1, z1 + hd, 0.0, w)
    if cap > 0:
        soup.use(seed=rng.random())
        soup.box(f, s0 - cw - (capp - cp), s1 + cw + (capp - cp), z1 + hd, z1 + hd + cap, 0.0, out_w + capp)
    if cs.get("brackets"):
        # a bracket on each side casing under the cap's ends, tapering down from the cap's depth
        bh, bp, bt = (v * MM for v in cs["brackets"])
        for sc in (s0 - cw / 2, s1 + cw / 2):
            soup.use(seed=rng.random())
            a, b, zt_, zb_ = sc - bt / 2, sc + bt / 2, z1 + hd, z1 + hd - bh
            wt, wb = w + bp, w + bp * 0.25
            soup.quad(f.at(a, zb_, wb), f.at(b, zb_, wb), f.at(b, zt_, wt), f.at(a, zt_, wt))
            soup.quad(f.at(a, zb_, w), f.at(a, zb_, wb), f.at(a, zt_, wt), f.at(a, zt_, w))
            soup.quad(f.at(b, zb_, wb), f.at(b, zb_, w), f.at(b, zt_, w), f.at(b, zt_, wt))
            soup.quad(f.at(a, zb_, w), f.at(b, zb_, w), f.at(b, zb_, wb), f.at(a, zb_, wb))
    if with_sill:
        soup.use(seed=rng.random())
        a, b = s0 - cw - horn, s1 + cw + horn
        wf = out_w + sp
        # the sill: front, sloping top back to the frame, underside, ends
        soup.quad(f.at(a, zs, wf), f.at(b, zs, wf), f.at(b, z0 - sh * 0.35, wf), f.at(a, z0 - sh * 0.35, wf),
                  ta=[(a, zs), (b, zs), (b, z0), (a, z0)])
        soup.quad(f.at(a, z0 - sh * 0.35, wf), f.at(b, z0 - sh * 0.35, wf), f.at(b, z0, 0.0), f.at(a, z0, 0.0),
                  ta=[(a, 0.0), (b, 0.0), (b, 0.06), (a, 0.06)])
        soup.quad(f.at(a, zs, 0.0), f.at(b, zs, 0.0), f.at(b, zs, wf), f.at(a, zs, wf))
        soup.quad(f.at(a, zs, 0.0), f.at(a, zs, wf), f.at(a, z0 - sh * 0.35, wf), f.at(a, z0, 0.0))
        soup.quad(f.at(b, zs, wf), f.at(b, zs, 0.0), f.at(b, z0, 0.0), f.at(b, z0 - sh * 0.35, wf))
    return (s0 - cw, s1 + cw, zs, z1 + hd + cap)


def reveal(soup, f, s0, s1, z0, z1, w_front, w_back):
    """The opening's lining from the casing's face back to the frame: four faces looking into the hole."""
    soup.use(kind="trim", lap=0.5, scheme="trim")
    soup.quad(f.at(s0, z0, w_back), f.at(s0, z0, w_front), f.at(s0, z1, w_front), f.at(s0, z1, w_back))
    soup.quad(f.at(s1, z0, w_front), f.at(s1, z0, w_back), f.at(s1, z1, w_back), f.at(s1, z1, w_front))
    soup.quad(f.at(s0, z1, w_back), f.at(s0, z1, w_front), f.at(s1, z1, w_front), f.at(s1, z1, w_back))
    soup.quad(f.at(s0, z0, w_front), f.at(s0, z0, w_back), f.at(s1, z0, w_back), f.at(s1, z0, w_front))
