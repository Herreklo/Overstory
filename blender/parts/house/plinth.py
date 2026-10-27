"""The plinth a timber house stands on, fitted to its ground: grey granite and gneiss split to blocks and laid in lime
mortar, from below the ground up to the sill beam, as Gamle Stavanger's plinths were built (research-subject.md, 4).
The stones are laid as the town's masons lay a wall (tools/r2b_wall.lay: always on the lowest place, courses forming
and breaking, no joint over a joint), the top course brought level for the sill. Each stone shows its split face: one
plane, or two meeting on a low ridge where the split ran across the grain; its corners knocked and an edge broken
once; a narrow arris chamfered back to the mortar. The joints are pointed nearly flush with the faces, so the plinth
reads as a few large grey blocks, quieter than the boards above it. Rigid stones, only placed and turned: none is bent
to the ground; the lowest course runs into it. The working's plinth gives the sizes (timber.json)."""

import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "tools"))
import r2b_wall  # noqa: E402  (the mason's laying, shared with the town's walls)

MM = 0.001


def _outline(cell, pl, arr, rng):
    """The face's outline in the wall's plane (s, z), counter-clockwise from the bed's left: each corner knocked off
    by two cuts of their own lengths, each edge broken once a little inward."""
    s0, z0, s1, z1 = cell
    cs = ((s0, z0), (s1, z0), (s1, z1), (s0, z1))
    sc, zc = 0.5 * (s0 + s1), 0.5 * (z0 + z1)
    least = 0.22 * min(s1 - s0, z1 - z0)
    o = []
    for i, c in enumerate(cs):
        prev, nxt = cs[i - 1], cs[(i + 1) % 4]
        chip = min(rng.uniform(*pl["chipMm"]) * MM, least)
        for q, k in ((prev, rng.uniform(0.6, 1.4)), (nxt, rng.uniform(0.6, 1.4))):
            d = math.hypot(q[0] - c[0], q[1] - c[1])
            t = max(chip * k, 1.4 * arr) / d
            o.append((c[0] + (q[0] - c[0]) * t, c[1] + (q[1] - c[1]) * t))
        t = rng.uniform(0.3, 0.7)
        m = (c[0] + (nxt[0] - c[0]) * t, c[1] + (nxt[1] - c[1]) * t)
        b = rng.uniform(*pl["breakMm"]) * MM
        dx, dz = sc - m[0], zc - m[1]
        d = math.hypot(dx, dz)
        o.append((m[0] + dx / d * b, m[1] + dz / d * b))
    return o


def _inset(o, d):
    """The convex outline o drawn in by d at every edge (each corner where its two edges' offset lines meet)."""
    n = len(o)
    lines = []
    for i in range(n):
        a, b = o[i], o[(i + 1) % n]
        ex, ez = b[0] - a[0], b[1] - a[1]
        L = math.hypot(ex, ez)
        nx, nz = -ez / L, ex / L  # inward for a counter-clockwise outline
        lines.append(((a[0] + nx * d, a[1] + nz * d), (ex / L, ez / L)))
    out = []
    for i in range(n):
        (p, u), (q, v) = lines[i - 1], lines[i]
        den = u[0] * v[1] - u[1] * v[0]
        if abs(den) < 1e-9:
            out.append(q)
            continue
        t = ((q[0] - p[0]) * v[1] - (q[1] - p[1]) * v[0]) / den
        out.append((p[0] + u[0] * t, p[1] + u[1] * t))
    return out


def _halves(ring, side):
    """The ring cut by the ridge into its two sides (each convex), the cut's points in both."""
    out = []
    for keep in (-1.0, 1.0):
        h = []
        n = len(ring)
        for i in range(n):
            a, b = ring[i], ring[(i + 1) % n]
            da, db = side(a) * keep, side(b) * keep
            if da >= 0.0:
                h.append(a)
            if (da > 0.0 > db) or (db > 0.0 > da):
                t = da / (da - db)
                h.append((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t))
        if len(h) >= 3:
            out.append(h)
    return out


def _splitstone(soup, f, cell, wb, wf, pl, rng):
    """One split stone in its cell (s0, z0, s1, z1, already less its joints): its outline, its face of one or two
    planes standing proud of the outline by the arris, its arris, and its sides back into the bed. The stone is moved
    and turned as one (set out, pitched, yawed, turned in the wall's plane), never bent. From the street level its face
    is drawn from the outline, with no arris or sides."""
    s0, z0, s1, z1 = cell
    sc, zc = 0.5 * (s0 + s1), 0.5 * (z0 + z1)
    arr = min(rng.uniform(*pl["arrisMm"]) * MM, 0.15 * min(s1 - s0, z1 - z0))
    o = _outline(cell, pl, arr, rng)
    if soup.level > 0:
        # (from the street a knock or a break is under two pixels: the cell's corners, the seed's draws kept)
        o = [(s0, z0), (s1, z0), (s1, z1), (s0, z1)]
    # the split: across the grain, one ridge a little slanted, standing out of the face's plane; or one plane
    ridge = rng.uniform(*pl["ridgeMm"]) * MM if rng.random() < pl["ridgeShare"] else 0.0
    sr = s0 + (s1 - s0) * rng.uniform(0.3, 0.7)
    a = math.radians(rng.uniform(*pl["ridgeSlantDeg"]))
    ca, sa = math.cos(a), math.sin(a)

    def side(p):
        return (p[0] - sr) * ca - (p[1] - zc) * sa
    near = soup.level == 0
    ring = _inset(o, arr) if near else o
    dl = max([-side(p) for p in ring] + [1e-3])
    dr = max([side(p) for p in ring] + [1e-3])

    def proud(p):
        d = side(p)
        return ridge * (1.0 - (d / dr if d >= 0.0 else -d / dl))
    # rigid: turned in the wall's plane, pitched about the along axis, yawed about the up axis, round its centre
    turn, pitch, yaw = (math.radians(rng.uniform(*pl[k])) for k in ("turnDeg", "pitchDeg", "yawDeg"))
    ct, st, cp, sp, cy, sy = math.cos(turn), math.sin(turn), math.cos(pitch), math.sin(pitch), math.cos(yaw), math.sin(yaw)
    wc = wf

    def at(s, z, w):
        ds, dz, dw = s - sc, z - zc, w - wc
        ds, dz = ds * ct - dz * st, ds * st + dz * ct
        dz, dw = dz * cp - dw * sp, dz * sp + dw * cp
        ds, dw = ds * cy + dw * sy, -ds * sy + dw * cy
        return f.at(sc + ds, zc + dz, wc + dw)
    for h in _halves(ring, side) if ridge > 0.0 else [ring]:
        ph = [at(p[0], p[1], wf + proud(p)) for p in h]
        for i in range(1, len(h) - 1):
            soup.tri(ph[0], ph[i], ph[i + 1], ta=h[0], tb=h[i], tc=h[i + 1])
    if not near:
        return
    n = len(o)
    pr = [at(p[0], p[1], wf + proud(p)) for p in ring]
    po = [at(p[0], p[1], wf + proud(q) - arr) for p, q in zip(o, ring)]
    pb = [at(p[0], p[1], wb) for p in o]
    for i in range(n):
        j = (i + 1) % n
        soup.quad(po[i], po[j], pr[j], pr[i], ta=[o[i], o[j], ring[j], ring[i]])
        soup.quad(pb[i], pb[j], po[j], po[i], ta=[o[i], o[j], o[j], o[i]])


def plinth(soup, f, s0, s1, z_ground, z_top, pl, face_w, seed):
    """The plinth on wall frame f from s0 to s1, from z_ground (below the lowest ground along the wall) to z_top: the
    mortar's pointing a little behind the faces, then each stone of the mason's laying. seed: the wall's
    (hashing.h)."""
    import hashing as HS
    point = face_w - pl["pointMm"] * MM
    soup.use(kind="mortar" if soup.level == 0 else "joint", scheme="none", seed=0.0, lap=0.0, shelter=0.0)
    soup.quad(f.at(s0, z_ground, point), f.at(s1, z_ground, point), f.at(s1, z_top, point), f.at(s0, z_top, point),
              ta=[(s0, z_ground), (s1, z_ground), (s1, z_top), (s0, z_top)])
    if soup.level >= 2:
        soup.use(kind="stone", seed=0.5, lap=0.5)
        soup.quad(f.at(s0, z_ground, face_w), f.at(s1, z_ground, face_w), f.at(s1, z_top, face_w), f.at(s0, z_top, face_w),
                  ta=[(s0, z_ground), (s1, z_ground), (s1, z_top), (s0, z_top)])
        return 0
    cells = r2b_wall.lay(seed, pl, s1 - s0, z_top - z_ground, level=True)
    for i, c in enumerate(cells):
        rng = HS.Stream(seed, "fieldstone", i)
        (a, b), (e, _), _, (_, t) = c
        j = 0.5 * rng.uniform(*pl["jointMm"]) * MM
        cell = (s0 + a + (j if a > 1e-6 else 0.0), z_ground + b + (j if b > 1e-6 else 0.0),
                s0 + e - (j if e < s1 - s0 - 1e-6 else 0.0), z_ground + t - j)
        if cell[2] - cell[0] < 0.06 or cell[3] - cell[1] < 0.06:
            continue
        soup.use(kind="stone", seed=rng.random(), lap=1.0 if b < 1e-6 else 0.5)
        _splitstone(soup, f, cell, point - 0.03, face_w + rng.uniform(*pl["setOutMm"]) * MM, pl, rng)
    return len(cells)
