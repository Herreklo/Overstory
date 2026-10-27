"""A pitched roof fitted to its house: the covering in courses, the ridge, the soffits under the overhangs, the fascia
and gutter along the eaves, the downpipes, the bargeboards up the rakes, and the chimney through the ridge. A fitted
part: its inputs are the house's span, length, eave, pitch and age (facts), the working's overhangs, boards and
chimney, the covering's record (how its tiles or slates are laid) and the rainwater goods (the pack's).

The roof's own coordinates: a across the span (0 under the ridge), r along the ridge (0 to its length), z up from the
house's base. place(a, r, z) gives the street's frame. At the near level the covering is modelled tile by tile (a
pantile's rolls, each slate); further off it is the courses' strips, the eave's course still modelled.
"""

import math

from soup import add, cross, dot, mul, norm, sub

MM = 0.001


def oquad(soup, a, b, c, d, out, ta=None):
    """A quad wound to face out (a direction it should face along)."""
    n = cross(sub(b, a), sub(c, a))
    if dot(n, out) < 0:
        a, b, c, d = b, a, d, c
        if ta:
            ta = [ta[1], ta[0], ta[3], ta[2]]
    soup.quad(a, b, c, d, ta=ta)


def nquad(soup, p, ns, out, ta=None):
    """A quad wound to face out, its corners' own normals ns (a rounded surface), or the face's when ns is None."""
    n = cross(sub(p[1], p[0]), sub(p[2], p[0]))
    if dot(n, n) < 1e-18:
        n = cross(sub(p[2], p[0]), sub(p[3], p[0]))
    if dot(n, out) < 0:
        p = [p[1], p[0], p[3], p[2]]
        ns = None if ns is None else [ns[1], ns[0], ns[3], ns[2]]
        if ta:
            ta = [ta[1], ta[0], ta[3], ta[2]]
    soup.quad(*p, ta=ta, ns=ns)


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


def sweep(soup, place, rd, ad, zd, r0, r1, prof, closed=False):
    """A section swept straight along the ridge: prof the (a, z) points of its outline about (0, 0), each with its own
    outward normal ((a, z) too), placed at a section origin; rd, ad, zd the street directions of r, a and z."""
    for i in range(len(prof) - (0 if closed else 1)):
        (pa, pn), (qa, qn) = prof[i], prof[(i + 1) % len(prof)]
        na = norm(add(mul(ad, pn[0]), mul(zd, pn[1])))
        nb = norm(add(mul(ad, qn[0]), mul(zd, qn[1])))
        p = [place(pa[0], r0, pa[1]), place(qa[0], r0, qa[1]), place(qa[0], r1, qa[1]), place(pa[0], r1, pa[1])]
        nquad(soup, p, [na, nb, nb, na], add(na, nb), ta=[(r0, 0.0), (r0, 1.0), (r1, 1.0), (r1, 0.0)])


def tube(soup, place, path, radius, sides, e1):
    """A round pipe along a polyline of (a, r, z) points, mitred at its bends; e1 the street direction square to every
    run (the pipe bends in one plane). Smooth normals; its ends are left open."""
    P = [place(*q) for q in path]
    ds = [norm(sub(P[i + 1], P[i])) for i in range(len(P) - 1)]
    rings = []
    for i, c in enumerate(P):
        d_in = ds[i - 1] if i > 0 else ds[0]
        d_out = ds[i] if i < len(ds) else ds[-1]
        m = norm(add(d_in, d_out))
        e2 = norm(cross(d_in, e1))
        ring = []
        for k in range(sides):
            ph = 2.0 * math.pi * k / sides
            p0 = add(c, mul(add(mul(e1, math.cos(ph)), mul(e2, math.sin(ph))), radius))
            t = -dot(sub(p0, c), m) / dot(d_in, m)
            ring.append(add(p0, mul(d_in, t)))
        rings.append(ring)
    for i, d in enumerate(ds):
        e2 = norm(cross(d, e1))
        rad = [add(mul(e1, math.cos(2.0 * math.pi * k / sides)), mul(e2, math.sin(2.0 * math.pi * k / sides)))
               for k in range(sides)]
        for k in range(sides):
            k1 = (k + 1) % sides
            nquad(soup, [rings[i][k], rings[i][k1], rings[i + 1][k1], rings[i + 1][k]],
                  [rad[k], rad[k1], rad[k1], rad[k]], add(rad[k], rad[k1]))
    return P


class Slope:
    """One side of the roof: points on its boarding's top from the eave's edge up (d, metres up the slope), along the
    ridge (r) and out from it (h, along its normal)."""

    def __init__(self, place, flat, sgn, ae, z_e, pitch):
        self.place, self.sgn, self.ae, self.z_e = place, sgn, ae, z_e
        self.sp, self.cp = math.sin(math.radians(pitch)), math.cos(math.radians(pitch))
        o = flat(0.0, 0.0, 0.0)
        self.A = norm(sub(flat(1.0, 0.0, 0.0), o))
        self.R = norm(sub(flat(0.0, 1.0, 0.0), o))
        self.Z = norm(sub(flat(0.0, 0.0, 1.0), o))
        self.N = norm(add(mul(self.A, sgn * self.sp), mul(self.Z, self.cp)))
        self.down = norm(add(mul(self.A, sgn * self.cp), mul(self.Z, -self.sp)))

    def at(self, d, r, h):
        return self.place(self.sgn * (self.ae - d * self.cp + self.sp * h), r, self.z_e + d * self.sp + self.cp * h)


def pantiles(soup, s, r0, r1, slope_len, laid, rng, waved):
    """Pantiles in courses up one slope: each course its tiles across, each tile an S (a broad flat pan and a narrower
    round roll, its own normals), its roll's edge lying over the next tile's pan (a step of the tile's thickness, the
    tile tilted across by it as laid tiles are), its foot a lip standing proud of the course below and dropped a little
    by the seed (mass-made tiles hung by hand: texture, no history), its ends closed at the verges. The rolls' phase is
    the street's (the painted mark's: along the slope's run, from the street's origin), so the mark and the form
    agree. waved: how many courses from the eave are modelled (all at near; the eave's alone further off, the rest a
    strip at the rolls' mean)."""
    cover, course = laid["coverMm"] * MM, laid["courseMm"] * MM
    amp, lift = laid["rollMm"] * MM / 2.0, laid["liftMm"] * MM
    thick, pan = laid["thickMm"] * MM, laid.get("panShape", 0.22)
    drop = laid.get("dropMm", 0.0) * MM
    base = amp * (1.0 + pan) + thick + 0.004
    # along the run, as the painted mark measures it: across the slope's own facing, in the street's plan
    D = norm((-s.N[1], s.N[0], 0.0))
    o = s.at(0.0, 0.0, 0.0)
    a0, ak = o[0] * D[0] + o[1] * D[1], dot(s.R, D)
    k = 2.0 * math.pi / cover
    tb = laid.get("lapAt", 0.58)          # where in the tile's wave (a share of it) the roll's edge lies on the next pan
    ph = lambda r: (a0 + ak * r) / cover  # the wave's phase in tiles
    # the profile: a sine with its trough flattened and its crest sharpened (the pan and the roll), the same crest as
    # the painted mark's; and the step where one tile's roll edge laps the next
    f = lambda t: amp * (math.sin(2.0 * math.pi * t) - pan * math.cos(4.0 * math.pi * t))
    df = lambda t: amp * 2.0 * math.pi * (math.cos(2.0 * math.pi * t) + 2.0 * pan * math.sin(4.0 * math.pi * t))
    lo, hi = sorted((ph(r0), ph(r1)))
    # samples: six to a tile and the lap twice (the step), each with its tile
    pts = []
    for j in range(math.floor(lo - tb) - 1, math.ceil(hi - tb) + 1):
        for q in range(7):
            t = j + tb + q / 6.0
            pts.append((t, j, q))
    rs = []
    for t, j, q in pts:
        r = (t * cover - a0) / ak
        rs.append((r, t, j, q))
    rs.sort(key=lambda x: x[0])
    out_ = []
    for r, t, j, q in rs:
        if r0 - 1e-6 <= r <= r1 + 1e-6:
            out_.append((r, t, j, q))
    # the ends at the verges, in their tiles
    for rr in (r0, r1):
        t = ph(rr)
        j = math.floor(t - tb)
        out_.append((rr, t, j, (t - tb - j) * 6.0))
    out_.sort(key=lambda x: (x[0], x[2] if ak > 0 else -x[2]))
    # height of a tile j at phase t: its S, tilted across by the lap; normals from the S
    tilt = lambda t, j: thick * ((t - tb - j) - 0.5)
    n_c = max(1, math.ceil(slope_len / course - 1e-6))
    for i in range(n_c):
        d0, d1 = i * course, min((i + 1) * course, slope_len)
        wav = i < waved
        foot, head = base + lift, base
        soup.use(kind="tile", scheme="none", seed=rng.random(), lap=0.0, shelter=0.0)
        if not wav:
            p = [s.at(d0, r0, foot), s.at(d0, r1, foot), s.at(d1, r1, head), s.at(d1, r0, head)]
            nquad(soup, p, None, s.N, ta=[(r0, d0), (r1, d0), (r1, d1), (r0, d1)])
            soup.use(lap=1.0)
            under = head if i else -0.03
            p = [s.at(d0, r0, under), s.at(d0, r1, under), s.at(d0, r1, foot), s.at(d0, r0, foot)]
            nquad(soup, p, None, s.down, ta=[(r0, d0 - 0.04), (r1, d0 - 0.04), (r1, d0), (r0, d0)])
            continue
        # each tile's seeded drop at its foot
        drops = {}
        for r, t, j, q in out_:
            if j not in drops:
                drops[j] = rng.uniform(0.0, drop)
        hgt = lambda r, t, j: f(t) + tilt(t, j)
        nrm = lambda t: norm(sub(s.N, mul(s.R, (df(t) + thick) * ak / cover)))
        tiles = {}
        for r, t, j, q in out_:
            tiles.setdefault(j, []).append((r, t, q))
        below = (i > 0 and (i - 1) < waved)
        for j, row in tiles.items():
            row.sort()
            dz = drops[j]
            for (ra, ta_, _), (rb, tb_, _) in zip(row, row[1:]):
                if rb - ra < 1e-5:
                    continue
                ha, hb = hgt(ra, ta_, j), hgt(rb, tb_, j)
                na, nb = nrm(ta_), nrm(tb_)
                p = [s.at(d0, ra, foot - dz + ha), s.at(d0, rb, foot - dz + hb), s.at(d1, rb, head + hb),
                     s.at(d1, ra, head + ha)]
                soup.use(lap=0.0)
                nquad(soup, p, [na, nb, nb, na], s.N, ta=[(ra, d0), (rb, d0), (rb, d1), (ra, d1)])
                # the tile's nose at the course's foot, down to the course below
                soup.use(lap=1.0)
                ua = head + (hgt(ra, ta_, j) if below else 0.0) if i else -0.03
                ub = head + (hgt(rb, tb_, j) if below else 0.0) if i else -0.03
                p = [s.at(d0, ra, ua - thick * 0.3), s.at(d0, rb, ub - thick * 0.3), s.at(d0, rb, foot - dz + hb),
                     s.at(d0, ra, foot - dz + ha)]
                nquad(soup, p, None, s.down, ta=[(ra, d0 - 0.04), (rb, d0 - 0.04), (rb, d0), (ra, d0)])
            # the roll's edge over the next tile's pan: the step, the tile's thickness (the next tile's foot its own
            # drop)
            for r_e, t_e, q in row:
                if q != 6 or not (r0 + 1e-4 < r_e < r1 - 1e-4) or (j + 1) not in drops:
                    continue
                h_hi, h_lo = hgt(r_e, t_e, j), hgt(r_e, t_e, j + 1)
                side = mul(s.R, 1.0 if ak > 0 else -1.0)
                soup.use(lap=0.5)
                p = [s.at(d0, r_e, foot - drops[j + 1] + h_lo), s.at(d1, r_e, head + h_lo), s.at(d1, r_e, head + h_hi),
                     s.at(d0, r_e, foot - dz + h_hi)]
                nquad(soup, p, None, side)
        # the verges: each course's end closed down to the boarding
        for rr, sd in ((r0, -1.0), (r1, 1.0)):
            t = ph(rr)
            j = math.floor(t - tb)
            hh = hgt(rr, t, j)
            soup.use(lap=0.5)
            p = [s.at(d0, rr, 0.0), s.at(d1, rr, 0.0), s.at(d1, rr, head + hh), s.at(d0, rr, foot + hh)]
            nquad(soup, p, None, mul(s.R, sd), ta=[(d0, 0.0), (d1, 0.0), (d1, 0.05), (d0, 0.05)])
    return n_c, base + amp * (1.0 + pan), base + lift + amp * (1.0 + pan) + thick * 0.5


def slates(soup, s, r0, r1, slope_len, laid, rng, modelled):
    """Slates in courses up one slope, each course breaking joint by half a slate. Modelled (near): each slate its own
    plane, its butt standing proud of the course below, its own seeded roll about the slope and drop at its butt
    (mass-made slates hung by hand: texture, no history), the joints between them open on the dark felt. Else the
    courses' strips."""
    W, course = laid["widthMm"] * MM, laid["courseMm"] * MM
    lift, gap = laid["liftMm"] * MM, laid["jointMm"] * MM
    roll, drop = math.radians(laid["rollDeg"]), laid["dropMm"] * MM
    base = 0.5 * W * math.tan(roll) + 0.001
    n_c = max(1, math.ceil(slope_len / course - 1e-6))
    if modelled:
        soup.use(kind="joint", scheme="none", seed=rng.random(), lap=0.0, shelter=0.0)
        nquad(soup, [s.at(0.0, r0, 0.0005), s.at(0.0, r1, 0.0005), s.at(slope_len, r1, 0.0005),
                     s.at(slope_len, r0, 0.0005)], None, s.N, ta=[(r0, 0.0), (r1, 0.0), (r1, slope_len), (r0, slope_len)])
    for i in range(n_c):
        d0, d1 = i * course, min((i + 1) * course, slope_len)
        under = base - 0.001 if i else -0.02
        if not modelled:
            soup.use(kind="tile", scheme="none", seed=rng.random(), lap=0.0, shelter=0.0)
            p = [s.at(d0, r0, base + lift), s.at(d0, r1, base + lift), s.at(d1, r1, base), s.at(d1, r0, base)]
            nquad(soup, p, None, s.N, ta=[(r0, d0), (r1, d0), (r1, d1), (r0, d1)])
            soup.use(lap=1.0)
            p = [s.at(d0, r0, under), s.at(d0, r1, under), s.at(d0, r1, base + lift), s.at(d0, r0, base + lift)]
            nquad(soup, p, None, s.down, ta=[(r0, d0 - 0.04), (r1, d0 - 0.04), (r1, d0), (r0, d0)])
            continue
        r = r0 - (0.5 * W if i % 2 else 0.0)
        while r < r1 - 1e-6:
            ra, rb = max(r, r0), min(r + W, r1)
            r += W
            if rb - ra < 0.03:
                continue
            ra += 0.5 * gap if ra > r0 + 1e-6 else 0.0
            rb -= 0.5 * gap if rb < r1 - 1e-6 else 0.0
            t, dz = math.tan(rng.uniform(-roll, roll)), rng.uniform(0.0, drop)
            rc = 0.5 * (ra + rb)
            L = lambda d, rr: base + (lift - dz) * (d1 - d) / max(d1 - d0, 1e-6) + (rr - rc) * t
            soup.use(kind="tile", scheme="none", seed=rng.random(), lap=0.0, shelter=0.0)
            top = [s.at(d0, ra, L(d0, ra)), s.at(d0, rb, L(d0, rb)), s.at(d1, rb, L(d1, rb)), s.at(d1, ra, L(d1, ra))]
            nquad(soup, top, None, s.N, ta=[(ra, d0), (rb, d0), (rb, d1), (ra, d1)])
            soup.use(lap=1.0)
            nquad(soup, [s.at(d0, ra, under), s.at(d0, rb, under), top[1], top[0]], None, s.down,
                  ta=[(ra, d0 - 0.04), (rb, d0 - 0.04), (rb, d0), (ra, d0)])
            nquad(soup, [s.at(d0, ra, 0.0005), s.at(d1, ra, 0.0005), top[3], top[0]], None, mul(s.R, -1.0))
            nquad(soup, [s.at(d0, rb, 0.0005), s.at(d1, rb, 0.0005), top[2], top[1]], None, s.R)
    return n_c, base + lift, base + lift + 0.003


def ridge_tiles(soup, place, z0, r0, r1, rd, rng, sides=12):
    """Half-round ridge tiles along the apex, each a little wider at its foot where it laps over the next: a step at
    each lap. Smooth normals."""
    R, Lt, lap = rd["radiusMm"] * MM, rd["lengthMm"] * MM, rd["lapMm"] * MM
    n = max(1, round((r1 - r0) / Lt))
    o = place(0.0, r0, z0)
    A = norm(sub(place(1.0, r0, z0), o))
    Rr = norm(sub(place(0.0, r0 + 1.0, z0), o))
    Z = norm(sub(place(0.0, r0, z0 + 1.0), o))
    half = sides // 2
    for j in range(n):
        ra, rb = r0 + (r1 - r0) * j / n, r0 + (r1 - r0) * (j + 1) / n + (lap if j < n - 1 else 0.0)
        Ra, Rb = R, R + lap * 0.6
        soup.use(kind="tile", scheme="none", seed=rng.random(), lap=0.5, shelter=0.0)
        for i in range(half):
            t0, t1 = math.pi * i / half, math.pi * (i + 1) / half
            n0 = norm(add(mul(A, math.cos(t0)), mul(Z, math.sin(t0))))
            n1 = norm(add(mul(A, math.cos(t1)), mul(Z, math.sin(t1))))
            p = [place(Ra * math.cos(t0), ra, z0 + Ra * math.sin(t0)), place(Ra * math.cos(t1), ra, z0 + Ra * math.sin(t1)),
                 place(Rb * math.cos(t1), rb, z0 + Rb * math.sin(t1)), place(Rb * math.cos(t0), rb, z0 + Rb * math.sin(t0))]
            nquad(soup, p, [n0, n1, n1, n0], add(n0, n1), ta=[(ra, t0 * R), (ra, t1 * R), (rb, t1 * R), (rb, t0 * R)])
            # the lap's step: the wide foot's end, a ring facing along the ridge
            p = [place(Ra * math.cos(t0), rb, z0 + Ra * math.sin(t0)), place(Ra * math.cos(t1), rb, z0 + Ra * math.sin(t1)),
                 place(Rb * math.cos(t1), rb, z0 + Rb * math.sin(t1)), place(Rb * math.cos(t0), rb, z0 + Rb * math.sin(t0))]
            nquad(soup, p, None, Rr)
        for side, rr_, RR in ((-1.0, ra, Ra), (1.0, rb, Rb)):
            if (side < 0 and j > 0) or (side > 0 and j < n - 1):
                continue
            soup.use(kind="mortar")
            for i in range(half):
                t0, t1 = math.pi * i / half, math.pi * (i + 1) / half
                p = [place(0.0, rr_, z0), place(RR * math.cos(t0), rr_, z0 + RR * math.sin(t0)),
                     place(RR * math.cos(t1), rr_, z0 + RR * math.sin(t1)), place(0.0, rr_, z0)]
                soup.tri(*[p[0], p[1], p[2]]) if dot(cross(sub(p[1], p[0]), sub(p[2], p[0])), mul(Rr, side)) > 0 else \
                    soup.tri(p[0], p[2], p[1])


def gutter(soup, place, a_c, z_c, r0, r1, sgn, rw, hooks):
    """A half-round gutter along the eave about (a_c, z_c): its outside, its rolled bead on the outer lip, its inside
    and its ends; hooks the r's of the straps that hold it."""
    R, bead = rw["gutterRadiusMm"] * MM, rw["beadMm"] * MM
    o = place(a_c, r0, z_c)
    A = norm(sub(place(a_c + 1.0, r0, z_c), o))
    Z = norm(sub(place(a_c, r0, z_c + 1.0), o))
    Rr = norm(sub(place(a_c, r0 + 1.0, z_c), o))
    at = lambda a, z: (lambda pa, r, pz: place(a_c + sgn * pa, r, z_c + pz))
    pl = at(0, 0)
    out_ = [((R * math.cos(math.pi * i / 6), -R * math.sin(math.pi * i / 6)),
             (math.cos(math.pi * i / 6), -math.sin(math.pi * i / 6))) for i in range(7)]
    soup.use(kind="metal", scheme="trim", lap=0.0, shelter=0.0)
    sweep(soup, pl, Rr, mul(A, sgn), Z, r0, r1, out_[::-1])
    inner = [((p[0] * 0.97, p[1] * 0.97), (-n[0], -n[1])) for p, n in out_]
    sweep(soup, pl, Rr, mul(A, sgn), Z, r0, r1, inner)
    rb_ = 0.5 * bead
    ring = [((R + rb_ + rb_ * math.cos(math.pi * i / 3), rb_ * math.sin(math.pi * i / 3)),
             (math.cos(math.pi * i / 3), math.sin(math.pi * i / 3))) for i in range(7)]
    sweep(soup, pl, Rr, mul(A, sgn), Z, r0, r1, ring)
    for rr_, side in ((r0, -1.0), (r1, 1.0)):
        for i in range(6):
            p0, p1 = out_[i][0], out_[i + 1][0]
            tri = [pl(0.0, rr_, 0.0), pl(p0[0], rr_, p0[1]), pl(p1[0], rr_, p1[1])]
            if dot(cross(sub(tri[1], tri[0]), sub(tri[2], tri[0])), mul(Rr, side)) < 0:
                tri = [tri[0], tri[2], tri[1]]
            soup.tri(*tri)
    hw, ht = rw["hookMm"][0] * MM, rw["hookMm"][1] * MM
    for rh in hooks:
        strap = [((p[0] * (R + ht) / R, p[1] * (R + ht) / R), n) for p, n in out_]
        sweep(soup, pl, Rr, mul(A, sgn), Z, rh - hw / 2, rh + hw / 2, strap[::-1])
        for rr_, side in ((rh - hw / 2, -1.0), (rh + hw / 2, 1.0)):
            for i in range(6):
                p0, p1 = out_[i][0], out_[i + 1][0]
                q0, q1 = strap[i][0], strap[i + 1][0]
                nquad(soup, [pl(p0[0], rr_, p0[1]), pl(p1[0], rr_, p1[1]), pl(q1[0], rr_, q1[1]),
                             pl(q0[0], rr_, q0[1])], None, mul(Rr, side))
    return R


def roof(soup, place, span, length, eave, pitch, wk, rng, verge_dir, side_dir, laid=None, push=None, rain=None,
         sag=0.0, wall_out=0.0, ground_at=None):
    """The roof over a span (wall to wall across) and a length (gable to gable). verge_dir(r_sign) and side_dir(a_sign)
    give the street-frame outward directions of the gable ends and the slopes, for winding. laid: the covering's
    record (how it is laid); push: the style's push (timber.json); rain: the rainwater goods; sag: how far the ridge
    has settled between the gables (m); wall_out: the cladding's face out from the wall's plane; ground_at(x, y): the
    ground's height under a street point, in the roof's z (where a downpipe ends)."""
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
    near = soup.level == 0
    open_eave = wk["eaves"]["rafterTails"]
    zb = lambda a: zt(a) - wk["eaves"].get("boardingMm", 25) * MM / cp   # the boarding's underside on open rafters
    push = push or {}
    pu_ch = push.get("chamferMm", {})
    es = push.get("ridgeSag", {}).get("eaveShare", 0.3)

    # the frame settles between the gables: most at the ridge's middle, a share of it at the eaves
    flat = place
    def place(a, r, z):
        t = min(1.0, max(0.0, r / length))
        return flat(a, r, z - sag * 4.0 * t * (1.0 - t) * (es + (1.0 - es) * max(0.0, 1.0 - abs(a) / ae)))

    # the covering: courses up each slope from the eave
    rf = wk["roof"]
    vt = wk["verge"]["thickMm"] * MM * push.get("bargeThick", 1.0)
    vg = (laid or {}).get("verge", {"over": False, "bargeAboveMm": 50})
    past = vt + vg.get("pastMm", 0) * MM if vg["over"] else -0.002
    slope_len = ae / cp
    tiles = 0
    top_h = peak = 0.0
    slopes = {}
    for sgn in (-1.0, 1.0):
        s = Slope(place, flat, sgn, ae, zt(ae), pitch)
        slopes[sgn] = s
        if rf["cover"] == "pantile" and laid:
            n_c, top_h, peak = pantiles(soup, s, r0 - past, r1 + past, slope_len, laid, rng,
                                  waved=10 ** 6 if near else 1)
        elif laid:
            n_c, top_h, peak = slates(soup, s, r0 - past, r1 + past, slope_len, laid, rng, modelled=near)
        else:
            raise ValueError("a roof needs its covering's record (laid)")
        tiles += n_c
        # the boarding's underside under the overhangs (one face from the eave's edge to the ridge, the house hides
        # the rest), painted with the trim. Under an open eave the overhang is the boarding alone on the rafters' tails,
        # thin, and a frieze board closes the wall's top between the tails
        ev = wk["eaves"]
        fh, ft = ev["fasciaMm"] * MM, ev["fasciaThickMm"] * MM
        ztop = zt(ae)
        out = side_dir(sgn)
        a_wall = half + wall_out
        soup.use(kind="trim", scheme="trim", seed=rng.random(), lap=0.5, shelter=1.0)
        if open_eave:
            q = [place(sgn * ae, r0, zb(ae)), place(sgn * ae, r1, zb(ae)), place(sgn * a_wall, r1, zb(a_wall)),
                 place(sgn * a_wall, r0, zb(a_wall))]
            oquad(soup, *q, down)
            q = [place(sgn * a_wall, r0, zu(a_wall)), place(sgn * a_wall, r1, zu(a_wall)), place(0.0, r1, ridge_u),
                 place(0.0, r0, ridge_u)]
            oquad(soup, *q, down)
            soup.use(kind="trim", scheme="trim", seed=rng.random(), lap=1.0, shelter=1.0)
            q = [place(sgn * (a_wall + 0.002), -wall_out, eave - 0.06), place(sgn * (a_wall + 0.002), length + wall_out, eave - 0.06),
                 place(sgn * (a_wall + 0.002), length + wall_out, zb(a_wall)), place(sgn * (a_wall + 0.002), -wall_out, zb(a_wall))]
            oquad(soup, *q, out)
        else:
            q = [place(sgn * ae, r0, zu(ae)), place(sgn * ae, r1, zu(ae)), place(0.0, r1, ridge_u), place(0.0, r0, ridge_u)]
            oquad(soup, *q, down)
        if fh > 0:
            soup.use(kind="trim", scheme="trim", seed=rng.random(), shelter=0.0)
            c = pu_ch.get("fascia", 0) * MM if near else 0.0
            # its face, a chamfer along its foot, and its foot
            q = [place(sgn * (ae + ft), r0, ztop - fh + c), place(sgn * (ae + ft), r1, ztop - fh + c),
                 place(sgn * (ae + ft), r1, ztop + 0.01), place(sgn * (ae + ft), r0, ztop + 0.01)]
            oquad(soup, *q, out, ta=[(r0, c), (r1, c), (r1, fh), (r0, fh)])
            if c > 0:
                q = [place(sgn * (ae + ft - c), r0, ztop - fh), place(sgn * (ae + ft - c), r1, ztop - fh),
                     place(sgn * (ae + ft), r1, ztop - fh + c), place(sgn * (ae + ft), r0, ztop - fh + c)]
                oquad(soup, *q, add(out, down))
            q = [place(sgn * ae, r0, ztop - fh), place(sgn * ae, r1, ztop - fh), place(sgn * (ae + ft - c), r1, ztop - fh),
                 place(sgn * (ae + ft - c), r0, ztop - fh)]
            oquad(soup, *q, down)
            for rr_, side in ((r0, -1.0), (r1, 1.0)):
                q = [place(sgn * ae, rr_, ztop - fh), place(sgn * (ae + ft - c), rr_, ztop - fh),
                     place(sgn * (ae + ft), rr_, ztop - fh + c), place(sgn * (ae + ft), rr_, ztop + 0.01)]
                oquad(soup, *q, verge_dir(side))
        else:
            # the boarding's edge, plumb at the eave
            soup.use(kind="trim", scheme="trim", seed=rng.random(), shelter=0.0)
            zl = zb(ae) if open_eave else zu(ae)
            q = [place(sgn * ae, r0, zl), place(sgn * ae, r1, zl), place(sgn * ae, r1, ztop + 0.01),
                 place(sgn * ae, r0, ztop + 0.01)]
            oquad(soup, *q, out)
        if ev["rafterTails"]:
            rw, rd = ev["rafterMm"][0] * MM, ev["rafterMm"][1] * MM
            n_r = max(2, round(length / (ev["rafterSpacingMm"] * MM)) + 1)
            for k in range(n_r):
                rc = 0.04 + (length - 0.08) * k / (n_r - 1)
                soup.use(kind="trim", scheme="trim", seed=rng.random(), shelter=1.0)
                ra, rb = rc - rw / 2, rc + rw / 2
                a_in, a_out = sgn * a_wall, sgn * (ae - 0.03)
                zd = rd / cp
                zr = lambda a: zb(abs(a))
                # sides, underside, and the end cut plumb
                for rr_, s_ in ((ra, -1.0), (rb, 1.0)):
                    oquad(soup, place(a_in, rr_, zr(a_in) - zd), place(a_out, rr_, zr(a_out) - zd),
                          place(a_out, rr_, zr(a_out)), place(a_in, rr_, zr(a_in)), verge_dir(s_))
                oquad(soup, place(a_in, ra, zr(a_in) - zd), place(a_out, ra, zr(a_out) - zd),
                      place(a_out, rb, zr(a_out) - zd), place(a_in, rb, zr(a_in) - zd), down)
                oquad(soup, place(a_out, ra, zr(a_out) - zd), place(a_out, rb, zr(a_out) - zd),
                      place(a_out, rb, zr(a_out)), place(a_out, ra, zr(a_out)), out)
        if ev["gutter"] and rain:
            R = rain["gutterRadiusMm"] * MM
            a_c, z_c = ae + ft + R, ztop - 0.03
            run = (r0 + 0.02, r1 - 0.02)
            every = rain["hookEveryMm"] * MM
            nh = max(2, round((run[1] - run[0]) / every) + 1)
            hooks = [run[0] + 0.12 + (run[1] - run[0] - 0.24) * i / (nh - 1) for i in range(nh)] if near else []
            gutter(soup, place, sgn * a_c, z_c, run[0], run[1], sgn, rain, hooks)
            if soup.level <= 1:
                # the downpipe: from an outlet by one end of the wall (the seed's), a swan neck back under the eave to
                # the wall, down it on clips, a shoe above the plinth
                Rp = rain["pipeRadiusMm"] * MM
                end = 0 if rng.random() < 0.5 else 1
                r_p = rain["outletFromEndMm"] * MM if end == 0 else length - rain["outletFromEndMm"] * MM
                a_w = half + wall_out + rain["offWallMm"] * MM + Rp
                z1 = z_c - R - 0.10
                z2 = z1 - (a_c - a_w)
                foot = place(sgn * a_w, r_p, 0.0)
                zf = (ground_at(foot[0], foot[1]) if ground_at else 0.0) + rain["footMm"] * MM
                sh = rain["shoeMm"] * MM
                path = [(sgn * a_c, r_p, z_c - R * 0.6), (sgn * a_c, r_p, z1), (sgn * a_w, r_p, z2),
                        (sgn * a_w, r_p, zf + sh * 0.7), (sgn * (a_w + sh * 0.7), r_p, zf)]
                e1 = norm(sub(place(0.0, 1.0, 0.0), place(0.0, 0.0, 0.0)))
                soup.use(kind="metal", scheme="trim", seed=rng.random(), lap=0.0, shelter=0.0)
                sides = 10 if near else 6
                tube(soup, place, path, Rp, sides, e1)
                # its open mouth at the shoe, dark
                soup.use(kind="joint")
                tube(soup, place, [path[-2], path[-1]], Rp * 0.9, sides, e1)
                cw, ct = rain["clipMm"][0] * MM, rain["clipMm"][1] * MM
                n_cl = max(2, int((z2 - zf) / (rain["clipEveryMm"] * MM)) + 1)
                soup.use(kind="metal")
                for i in range(n_cl):
                    zc_ = zf + sh + (z2 - zf - sh - 0.2) * (i + 0.5) / n_cl
                    tube(soup, place, [(sgn * a_w, r_p, zc_ - cw / 2), (sgn * a_w, r_p, zc_ + cw / 2)],
                         Rp + ct * 0.5, sides, e1)
                    tube(soup, place, [(sgn * (half + wall_out), r_p, zc_), (sgn * (a_w - Rp), r_p, zc_)],
                         ct, 4, norm(sub(place(0.0, 0.0, 1.0), place(0.0, 0.0, 0.0))))

    # the ridge: half-round ridge tiles over a pantiled apex, a low capping over slates
    soup.use(kind="tile", scheme="none", seed=rng.random(), lap=0.5)
    rd_ = (laid or {}).get("ridge", {})
    if rf["cover"] == "pantile":
        Rr_ = rd_.get("radiusMm", 120) * MM
        z_r = zt(0.0) + top_h - Rr_ * tp * 0.55
        if near:
            ridge_tiles(soup, place, z_r, r0 - past, r1 + past, rd_, rng)
        else:
            prism(soup, place, ((0.0, z_r), r0 - past, r1 + past), Rr_, 8, half=True)
    else:
        prism(soup, place, ((0.0, zt(0.0) + top_h * 0.5), r0 - past - 0.02, r1 + past + 0.02),
              rd_.get("radiusMm", 60) * MM, 8, half=True)

    # the bargeboards up each rake, standing off the gable wall by the verge's overhang; chamfered on their faces'
    # edges near
    vb = wk["verge"]["boardMm"] * MM
    cb = pu_ch.get("barge", 0) * MM if near else 0.0
    above = vg.get("bargeAboveMm", 50) * MM
    soup.use(kind="trim", scheme="trim", lap=0.5, shelter=0.0)
    for rs, r in ((-1.0, r0), (1.0, r1)):
        out = verge_dir(rs)
        for sgn in (-1.0, 1.0):
            soup.use(seed=rng.random())
            k = 12
            for j in range(k):
                aa, ab = sgn * ae * (1 - j / k), sgn * ae * (1 - (j + 1) / k)
                ta_, tb_ = zt(aa) + above, zt(ab) + above
                ba, bb = ta_ - vb / cp, tb_ - vb / cp
                ro = r + rs * vt
                ri = ro - rs * cb
                c_ = cb / cp
                oquad(soup, place(aa, ro, ba + c_), place(ab, ro, bb + c_), place(ab, ro, tb_ - c_),
                      place(aa, ro, ta_ - c_), out, ta=[(abs(aa), 0.0), (abs(ab), 0.0), (abs(ab), vb), (abs(aa), vb)])
                oquad(soup, place(aa, r, ba), place(ab, r, bb), place(ab, ri, bb), place(aa, ri, ba), down)
                oquad(soup, place(aa, r, ta_), place(ab, r, tb_), place(ab, ri, tb_), place(aa, ri, ta_), up)
                if cb > 0:
                    oquad(soup, place(aa, ri, ta_), place(ab, ri, tb_), place(ab, ro, tb_ - c_), place(aa, ro, ta_ - c_),
                          add(out, up))
                    oquad(soup, place(aa, ri, ba), place(ab, ri, bb), place(ab, ro, bb + c_), place(aa, ro, ba + c_),
                          add(out, down))
            # the board's foot, cut plumb at the eave
            a_ = sgn * ae
            oquad(soup, place(a_, r, zt(a_) + above - vb / cp), place(a_, ro, zt(a_) + above - vb / cp),
                  place(a_, ro, zt(a_) + above), place(a_, r, zt(a_) + above), side_dir(sgn))
        # the verge's underside between the board and the wall; under an open eave the boarding alone, and the gable
        # wall's top closed up to it
        soup.use(kind="trim", scheme="trim", seed=rng.random(), shelter=1.0)
        zv = zb if open_eave else zu
        for sgn in (-1.0, 1.0):
            rin = -wall_out if rs < 0 else length + wall_out
            q = [place(sgn * ae, r, zv(ae)), place(sgn * ae, rin, zv(ae)), place(0.0, rin, zv(0.0)), place(0.0, r, zv(0.0))]
            oquad(soup, *q, down)
            if open_eave:
                rw_ = rin + rs * 0.002
                q = [place(sgn * (half + wall_out), rw_, zu(half + wall_out)), place(0.0, rw_, ridge_u),
                     place(0.0, rw_, zb(0.0)), place(sgn * (half + wall_out), rw_, zb(half + wall_out))]
                oquad(soup, *q, out)
    return dict(ridge_u=ridge_u, ridge_top=zt(0.0), courses=tiles, zt=zt, half=half, place=place, cover_h=top_h,
                cover=lambda a: zt(a) + peak / cp)   # the covering's highest point above a, plumb


def chimney(soup, place, r_at, a_at, zt_ridge, ch, rng, inside_z, cover=None, flash=None):
    """A rendered stack through the roof by the ridge: its body, a cap that sheds the rain, the flue's dark mouth, and
    where it meets the covering (cover(a): the covering's top across the span) a metal apron dressed up its faces
    (flash: its upstand's height, how far it stands off the stack, how far its skirt lies out over the covering, m)."""
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
    if cover and flash:
        fh, fo, skirt = flash
        soup.use(kind="metal", scheme="none", seed=rng.random(), lap=1.0, shelter=0.0)
        for (pa, pr), (qa, qr) in faces:
            ks = [0.0, 1.0]
            if (pa - a_at) * (qa - a_at) < 0 and abs(pa - qa) > 1e-6:
                ks = [0.0, (0.0 - pa) / (qa - pa), 1.0]
            pts = [(pa + (qa - pa) * k_, pr + (qr - pr) * k_) for k_ in ks]
            c = place(cx, cr, z0)
            for (ua, ur), (va, vr) in zip(pts, pts[1:]):
                oa = lambda x_: x_ + (fo if x_ > cx + 1e-6 else (-fo if x_ < cx - 1e-6 else 0.0))
                orr = lambda x_: x_ + (fo if x_ > cr + 1e-6 else (-fo if x_ < cr - 1e-6 else 0.0))
                za, zb = cover(ua) + 0.004, cover(va) + 0.004
                out = sub(place(0.5 * (oa(ua) + oa(va)), 0.5 * (orr(ur) + orr(vr)), za), place(cx, cr, za))
                # the upstand against the stack
                oquad(soup, place(oa(ua), orr(ur), za), place(oa(va), orr(vr), zb), place(oa(va), orr(vr), zb + fh),
                      place(oa(ua), orr(ur), za + fh), out)
                # its top edge, dressed back into the stack
                oquad(soup, place(ua, ur, za + fh), place(va, vr, zb + fh), place(oa(va), orr(vr), zb + fh),
                      place(oa(ua), orr(ur), za + fh), (0.0, 0.0, 1.0))
                # the skirt dressed out over the covering's rolls, and its turned-down edge
                sk = lambda x_, c_: x_ + (skirt if x_ > c_ + 1e-6 else (-skirt if x_ < c_ - 1e-6 else 0.0))
                pa_, pb_ = (sk(oa(ua), cx), sk(orr(ur), cr)), (sk(oa(va), cx), sk(orr(vr), cr))
                ya, yb = cover(pa_[0]) + 0.004, cover(pb_[0]) + 0.004
                oquad(soup, place(oa(ua), orr(ur), za), place(oa(va), orr(vr), zb), place(pb_[0], pb_[1], yb),
                      place(pa_[0], pa_[1], ya), (0.0, 0.0, 1.0))
                oquad(soup, place(pa_[0], pa_[1], ya), place(pb_[0], pb_[1], yb), place(pb_[0], pb_[1], yb - 0.012),
                      place(pa_[0], pa_[1], ya - 0.012), out)
    soup.use(kind="room", scheme="none", lit=0.0)
    f = 0.11
    q = [place(cx - f, cr - f, top + h + 0.002), place(cx + f, cr - f, top + h + 0.002),
         place(cx + f, cr + f, top + h + 0.002), place(cx - f, cr + f, top + h + 0.002)]
    oquad(soup, *q, (0.0, 0.0, 1.0))
