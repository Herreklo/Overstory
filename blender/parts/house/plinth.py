"""The plinth a timber house stands on, fitted to its ground: grey fieldstone in lime mortar from below the ground up to
the sill beam. The stones are laid as the town's masons lay a wall (tools/r2b_wall.lay: always on the lowest place,
courses forming and breaking, no joint over a joint), each a fieldstone in its place: a rounded, irregular face, a
little domed, its arrises worn round, set a little in or out and turned. Rigid stones, only placed and turned: none is
bent to the ground; the lowest course runs into it. The working's plinth gives the sizes (timber.json)."""

import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "tools"))
import r2b_wall  # noqa: E402  (the mason's laying, shared with the town's walls)
from soup import add, mul, norm  # noqa: E402

MM = 0.001


def _fieldstone(soup, f, cell, wb, wf, pl, rng):
    """One fieldstone filling its cell (s0, z0, s1, z1) less its joints: an outline whose four corners are arcs of
    their own rounding (roundSegments each: at eye level a corner cut once read as an octagon), the face domed out from
    that outline and its arris rounded back to it."""
    s0, z0, s1, z1 = cell
    w, h = s1 - s0, z1 - z0
    r = [min(rng.uniform(*pl["roundMm"]) * MM, 0.4 * w, 0.4 * h) for _ in range(4)]
    k_arc = pl["roundSegments"]
    o = []
    for (cs_, cz_, a0), rr in zip(((s0 + r[0], z0 + r[0], 180), (s1 - r[1], z0 + r[1], 270),
                                   (s1 - r[2], z1 - r[2], 0), (s0 + r[3], z1 - r[3], 90)), r):
        for i in range(k_arc + 1):
            t = math.radians(a0 + 90.0 * i / k_arc)
            o.append((cs_ + rr * math.cos(t), cz_ + rr * math.sin(t)))
    turn = math.radians(rng.uniform(*pl["turnDeg"]))
    sc, zc = 0.5 * (s0 + s1), 0.5 * (z0 + z1)
    cs, sn = math.cos(turn), math.sin(turn)
    o = [(sc + (a - sc) * cs - (z - zc) * sn, zc + (a - sc) * sn + (z - zc) * cs) for a, z in o]
    dome = rng.uniform(*pl["domeMm"]) * MM
    arr = min(0.35 * min(w, h), rng.uniform(*pl["roundMm"]) * MM * 0.6)
    # the face's ring, drawn in from the outline by the arris, and its crown
    k = 1.0 - 2.0 * arr / max(1e-3, min(w, h))
    ring = [(sc + (a - sc) * k, zc + (z - zc) * k) for a, z in o]
    crown = f.at(sc, zc, wf + dome)
    pr = [f.at(a, z, wf) for a, z in ring]
    po = [f.at(a, z, wf - arr) for a, z in o]
    pb = [f.at(a, z, wb) for a, z in o]
    # the face's normals as a rounded stone's: the crown square on, the ring leaning out by the dome's fall, the
    # arris's foot further (drawn soft over the few triangles)
    hw, hh = 0.5 * w, 0.5 * h

    def lean(a, z, k):
        da, dz = (a - sc) / hw, (z - zc) / hh
        return norm(add(f.n, add(mul(f.u, da * k), mul(f.v, dz * k))))
    k_ring = 2.2 * dome / max(0.05, min(hw, hh))
    nr = [lean(a, z, k_ring) for a, z in ring]
    no = [lean(a, z, 1.4) for a, z in o]
    n = len(o)
    for i in range(n):
        j = (i + 1) % n
        soup.tri(pr[i], pr[j], crown, ta=ring[i], tb=ring[j], tc=(sc, zc), ns=(nr[i], nr[j], f.n))
        soup.quad(po[i], po[j], pr[j], pr[i], ta=[o[i], o[j], ring[j], ring[i]], ns=(no[i], no[j], nr[j], nr[i]))
        soup.quad(pb[i], pb[j], po[j], po[i], ta=[o[i], o[j], o[j], o[i]])


def plinth(soup, f, s0, s1, z_ground, z_top, pl, face_w, seed):
    """The plinth on wall frame f from s0 to s1, from z_ground (below the lowest ground along the wall) to z_top: the
    mortar's bed, then each stone of the mason's laying. seed: the wall's (hashing.h)."""
    import hashing as HS
    back = face_w - pl["bedMm"] * MM
    soup.use(kind="mortar", scheme="none", seed=0.0, lap=0.0, shelter=0.0)
    soup.quad(f.at(s0, z_ground, back), f.at(s1, z_ground, back), f.at(s1, z_top, back), f.at(s0, z_top, back),
              ta=[(s0, z_ground), (s1, z_ground), (s1, z_top), (s0, z_top)])
    cells = r2b_wall.lay(seed, pl, s1 - s0, z_top - z_ground)
    for i, c in enumerate(cells):
        rng = HS.Stream(seed, "fieldstone", i)
        (a, b), (e, _), _, (_, t) = c
        j = 0.5 * rng.uniform(*pl["jointMm"]) * MM
        cell = (s0 + a + (j if a > 1e-6 else 0.0), z_ground + b + (j if b > 1e-6 else 0.0),
                s0 + e - (j if e < s1 - s0 - 1e-6 else 0.0), z_ground + t - j)
        if cell[2] - cell[0] < 0.04 or cell[3] - cell[1] < 0.04:
            continue
        soup.use(kind="stone", seed=rng.random(), lap=1.0 if b < 1e-6 else 0.5)
        _fieldstone(soup, f, cell, back - 0.02, face_w + rng.uniform(*pl["setOutMm"]) * MM, pl, rng)
    return len(cells)
