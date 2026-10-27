"""A pitched roof fitted to its house: the covering in courses, the ridge, the soffits under the overhangs, the fascia
and gutter along the eaves, the bargeboards up the rakes, and the chimney through the ridge. A fitted part: its inputs
are the house's span, length, eave and pitch (facts) and the working's overhangs, boards and chimney (the pack's).

The roof's own coordinates: a across the span (0 under the ridge), r along the ridge (0 to its length), z up from the
house's base. place(a, r, z) gives the street's frame.
"""

import math

from soup import cross, dot, norm, sub

MM = 0.001


def oquad(soup, a, b, c, d, out, ta=None):
    """A quad wound to face out (a direction it should face along)."""
    n = cross(sub(b, a), sub(c, a))
    if dot(n, out) < 0:
        a, b, c, d = b, a, d, c
        if ta:
            ta = [ta[1], ta[0], ta[3], ta[2]]
    soup.quad(a, b, c, d, ta=ta)


def prism(soup, place, path, radius, sides, out_up=True, half=False):
    """A round section swept straight along the ridge (r) at (a, z): a ridge tile, a gutter or a pipe's run."""
    (a, z), r0, r1 = path
    n = sides
    rng = range(n) if not half else range(n // 2)
    for i in rng:
        t0 = math.pi * (i / n * 2.0) if not half else math.pi * i / (n // 2)
        t1 = math.pi * ((i + 1) / n * 2.0) if not half else math.pi * (i + 1) / (n // 2)
        p = lambda t, r: place(a + radius * math.cos(t), r, z + radius * math.sin(t) * (1 if out_up else -1))
        mid = 0.5 * (t0 + t1)
        c0 = place(a, r0, z)
        q = [p(t0, r0), p(t1, r0), p(t1, r1), p(t0, r1)]
        out = sub(p(mid, r0), c0)
        oquad(soup, *q, out, ta=[(r0, t0 * radius), (r0, t1 * radius), (r1, t1 * radius), (r1, t0 * radius)])


def roof(soup, place, span, length, eave, pitch, wk, rng, verge_dir, side_dir):
    """The roof over a span (wall to wall across) and a length (gable to gable). verge_dir(r_sign) and side_dir(a_sign)
    give the street-frame outward directions of the gable ends and the slopes, for winding."""
    tp = math.tan(math.radians(pitch))
    cp = math.cos(math.radians(pitch))
    half = span / 2
    oe = wk["eaves"]["overhangMm"] * MM
    ov = wk["verge"]["overhangMm"] * MM
    T = 0.20
    ridge_u = eave + half * tp                       # the underside's apex, the gable walls' peak
    zu = lambda a: eave + (half - abs(a)) * tp       # the underside
    zt = lambda a: zu(a) + T / cp                    # the top of the boarding, under the tiles
    ae = half + oe
    r0, r1 = -ov, length + ov
    up = (0.0, 0.0, 1.0)
    down = (0.0, 0.0, -1.0)

    # the covering: courses up each slope from the eave, each standing a little proud at its foot
    rf = wk["roof"]
    gauge, butt = rf["gaugeMm"] * MM, rf["buttMm"] * MM
    slope_len = ae / cp
    n = max(2, math.ceil(slope_len / gauge))
    tiles = 0
    for sgn in (-1.0, 1.0):
        out = side_dir(sgn)
        for i in range(n):
            d0, d1 = slope_len * i / n, slope_len * (i + 1) / n
            a0, a1 = sgn * (ae - d0 * cp), sgn * (ae - d1 * cp)
            soup.use(kind="tile", scheme="none", seed=rng.random(), lap=0.0, shelter=0.0)
            lift0 = butt
            p = [place(a0, r0 - 0.04, zt(a0) + lift0), place(a0, r1 + 0.04, zt(a0) + lift0),
                 place(a1, r1 + 0.04, zt(a1) + 0.004), place(a1, r0 - 0.04, zt(a1) + 0.004)]
            nrm = norm((out[0] * tp, out[1] * tp, 1.0))
            oquad(soup, *p, nrm, ta=[(r0, d0), (r1, d0), (r1, d1), (r0, d1)])
            # the course's foot: its butts in a line
            soup.use(kind="tile", lap=1.0)
            q = [place(a0, r0 - 0.04, zt(a0) + 0.004 - (0.0 if i else 0.03)), place(a0, r1 + 0.04, zt(a0) + 0.004 - (0.0 if i else 0.03)),
                 place(a0, r1 + 0.04, zt(a0) + lift0), place(a0, r0 - 0.04, zt(a0) + lift0)]
            oquad(soup, *q, out, ta=[(r0, d0 - 0.04), (r1, d0 - 0.04), (r1, d0), (r0, d0)])
            tiles += 1
        # the boarding's underside under the overhangs (one face from the eave's edge to the ridge, the house hides
        # the rest), painted with the trim
        soup.use(kind="trim", scheme="trim", seed=rng.random(), lap=0.5, shelter=1.0)
        q = [place(sgn * ae, r0, zu(ae)), place(sgn * ae, r1, zu(ae)), place(0.0, r1, ridge_u), place(0.0, r0, ridge_u)]
        oquad(soup, *q, down)
        # the fascia along the eave, or the rafters' ends under an open eave; the gutter where the era had one
        ev = wk["eaves"]
        fh, ft = ev["fasciaMm"] * MM, ev["fasciaThickMm"] * MM
        ztop = zt(ae)
        if fh > 0:
            soup.use(kind="trim", scheme="trim", seed=rng.random(), shelter=0.0)
            q = [place(sgn * (ae + ft), r0, ztop - fh), place(sgn * (ae + ft), r1, ztop - fh),
                 place(sgn * (ae + ft), r1, ztop + 0.01), place(sgn * (ae + ft), r0, ztop + 0.01)]
            oquad(soup, *q, out, ta=[(r0, 0), (r1, 0), (r1, fh), (r0, fh)])
            q = [place(sgn * ae, r0, ztop - fh), place(sgn * ae, r1, ztop - fh), place(sgn * (ae + ft), r1, ztop - fh),
                 place(sgn * (ae + ft), r0, ztop - fh)]
            oquad(soup, *q, down)
        else:
            # the boarding's edge, plumb at the eave
            soup.use(kind="trim", scheme="trim", seed=rng.random(), shelter=0.0)
            q = [place(sgn * ae, r0, zu(ae)), place(sgn * ae, r1, zu(ae)), place(sgn * ae, r1, ztop + 0.01),
                 place(sgn * ae, r0, ztop + 0.01)]
            oquad(soup, *q, out)
        if ev["rafterTails"]:
            rw, rd = ev["rafterMm"][0] * MM, ev["rafterMm"][1] * MM
            n_r = max(2, round(length / (ev["rafterSpacingMm"] * MM)) + 1)
            for k in range(n_r):
                rc = 0.04 + (length - 0.08) * k / (n_r - 1)
                soup.use(kind="trim", scheme="trim", seed=rng.random(), shelter=1.0)
                ra, rb = rc - rw / 2, rc + rw / 2
                a_in, a_out = sgn * (half - 0.05), sgn * (ae - 0.03)
                zd = rd / cp
                # sides, underside, and the end cut plumb
                for rr_, s_ in ((ra, -1.0), (rb, 1.0)):
                    oquad(soup, place(a_in, rr_, zu(abs(a_in)) - zd), place(a_out, rr_, zu(abs(a_out)) - zd),
                          place(a_out, rr_, zu(abs(a_out))), place(a_in, rr_, zu(abs(a_in))), verge_dir(s_))
                oquad(soup, place(a_in, ra, zu(abs(a_in)) - zd), place(a_out, ra, zu(abs(a_out)) - zd),
                      place(a_out, rb, zu(abs(a_out)) - zd), place(a_in, rb, zu(abs(a_in)) - zd), down)
                oquad(soup, place(a_out, ra, zu(abs(a_out)) - zd), place(a_out, rb, zu(abs(a_out)) - zd),
                      place(a_out, rb, zu(abs(a_out))), place(a_out, ra, zu(abs(a_out))), out)
        if ev["gutter"]:
            soup.use(kind="metal", scheme="trim", seed=rng.random())
            prism(soup, place, ((sgn * (ae + ft + 0.065), ztop - 0.03), r0 + 0.02, r1 - 0.02), 0.065, 8,
                  out_up=False, half=True)

    # the ridge: half-round ridge tiles over a pantiled apex, a low capping over slates
    soup.use(kind="tile", scheme="none", seed=rng.random(), lap=0.5)
    prism(soup, place, ((0.0, zt(0.0) + 0.02), r0 - 0.05, r1 + 0.05), 0.12 if rf["cover"] == "pantile" else 0.06, 8,
          half=True)

    # the bargeboards up each rake, standing off the gable wall by the verge's overhang
    vb, vt = wk["verge"]["boardMm"] * MM, wk["verge"]["thickMm"] * MM
    soup.use(kind="trim", scheme="trim", lap=0.5, shelter=0.0)
    for rs, r in ((-1.0, r0), (1.0, r1)):
        out = verge_dir(rs)
        for sgn in (-1.0, 1.0):
            soup.use(seed=rng.random())
            k = 12
            for j in range(k):
                aa, ab = sgn * ae * (1 - j / k), sgn * ae * (1 - (j + 1) / k)
                ta_, tb_ = zt(aa) + 0.05, zt(ab) + 0.05
                ba, bb = ta_ - vb / cp, tb_ - vb / cp
                ro = r + rs * vt
                oquad(soup, place(aa, ro, ba), place(ab, ro, bb), place(ab, ro, tb_), place(aa, ro, ta_), out,
                      ta=[(abs(aa), 0.0), (abs(ab), 0.0), (abs(ab), vb), (abs(aa), vb)])
                oquad(soup, place(aa, r, ba), place(ab, r, bb), place(ab, ro, bb), place(aa, ro, ba), down)
                oquad(soup, place(aa, r, ta_), place(ab, r, tb_), place(ab, ro, tb_), place(aa, ro, ta_), up)
            # the board's foot, cut plumb at the eave
            a_ = sgn * ae
            oquad(soup, place(a_, r, zt(a_) + 0.05 - vb / cp), place(a_, ro, zt(a_) + 0.05 - vb / cp),
                  place(a_, ro, zt(a_) + 0.05), place(a_, r, zt(a_) + 0.05), side_dir(sgn))
        # the verge's underside between the board and the wall
        soup.use(kind="trim", scheme="trim", seed=rng.random(), shelter=1.0)
        for sgn in (-1.0, 1.0):
            rin = 0.0 if rs < 0 else length
            q = [place(sgn * ae, r, zu(ae)), place(sgn * ae, rin, zu(ae)), place(0.0, rin, ridge_u), place(0.0, r, ridge_u)]
            oquad(soup, *q, down)
    return dict(ridge_u=ridge_u, ridge_top=zt(0.0), courses=tiles, zt=zt, half=half)


def chimney(soup, place, r_at, a_at, zt_ridge, ch, rng, inside_z):
    """A rendered stack through the roof by the ridge: its body, a cap that sheds the rain, the flue's dark mouth."""
    w, d = ch["sizeMm"][0] * MM, ch["sizeMm"][1] * MM
    top = zt_ridge + ch["aboveRidgeMm"] * MM
    if ch["crown"] == "corbelled":
        top -= 0.16
    soup.use(kind="render", scheme="none", seed=rng.random(), lap=0.5, shelter=0.0)
    a0, a1, r0, r1 = a_at - w / 2, a_at + w / 2, r_at - d / 2, r_at + d / 2
    z0 = inside_z
    faces = [((a0, r0), (a1, r0)), ((a1, r0), (a1, r1)), ((a1, r1), (a0, r1)), ((a0, r1), (a0, r0))]
    cx, cr = a_at, r_at
    for (pa, pr), (qa, qr) in faces:
        mid = place(0.5 * (pa + qa), 0.5 * (pr + qr), z0)
        c = place(cx, cr, z0)
        out = sub(mid, c)
        oquad(soup, place(pa, pr, z0), place(qa, qr, z0), place(qa, qr, top), place(pa, pr, top), out,
              ta=[(0, z0), (1, z0), (1, top), (0, top)])
    if ch["crown"] == "corbelled":
        # two courses oversailing the stack, each a little further out
        for i, e_ in enumerate((0.03, 0.06)):
            soup.use(kind="render", seed=rng.random())
            za_, zb_ = top + 0.08 * i, top + 0.08 * (i + 1)
            for (pa, pr), (qa, qr) in faces:
                k_ = lambda v, e_=e_: v + (e_ if v > 0 else -e_)
                sa, sr, ta_, tr_ = pa - cx, pr - cr, qa - cx, qr - cr
                mid = place(cx + 0.5 * (k_(sa) + k_(ta_)), cr + 0.5 * (k_(sr) + k_(tr_)), za_)
                out = sub(mid, place(cx, cr, za_))
                oquad(soup, place(cx + k_(sa), cr + k_(sr), za_), place(cx + k_(ta_), cr + k_(tr_), za_),
                      place(cx + k_(ta_), cr + k_(tr_), zb_), place(cx + k_(sa), cr + k_(sr), zb_), out)
            q = [place(a0 - e_, r0 - e_, za_), place(a1 + e_, r0 - e_, za_), place(a1 + e_, r1 + e_, za_),
                 place(a0 - e_, r1 + e_, za_)]
            oquad(soup, *q, (0.0, 0.0, -1.0))
        top += 0.16
    # the cap, a slab a little wider, and the flue
    e, h = (0.09, 0.06) if ch["crown"] == "corbelled" else (0.05, 0.08)
    soup.use(kind="render", seed=rng.random())
    for (pa, pr), (qa, qr) in faces:
        sa, sr = (pa - cx), (pr - cr)
        ta_, tr_ = (qa - cx), (qr - cr)
        k = lambda v: v + (e if v > 0 else -e)
        mid = place(cx + 0.5 * (k(sa) + k(ta_)), cr + 0.5 * (k(sr) + k(tr_)), top)
        out = sub(mid, place(cx, cr, top))
        oquad(soup, place(cx + k(sa), cr + k(sr), top), place(cx + k(ta_), cr + k(tr_), top),
              place(cx + k(ta_), cr + k(tr_), top + h), place(cx + k(sa), cr + k(sr), top + h), out)
    q = [place(a0 - e, r0 - e, top + h), place(a1 + e, r0 - e, top + h), place(a1 + e, r1 + e, top + h),
         place(a0 - e, r1 + e, top + h)]
    oquad(soup, *q, (0.0, 0.0, 1.0))
    soup.use(kind="room", scheme="none", lit=0.0)
    f = 0.11
    q = [place(cx - f, cr - f, top + h + 0.002), place(cx + f, cr - f, top + h + 0.002),
         place(cx + f, cr + f, top + h + 0.002), place(cx - f, cr + f, top + h + 0.002)]
    oquad(soup, *q, (0.0, 0.0, 1.0))
