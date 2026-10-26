"""The split wall stone (port step 2b, R2b): a face stone of a dry wall of split slate, as reference 10 shows one
(docs/references/stone/10-bergen-dry-stone-wall-and-bedrock.jpg): laid on its natural bed, only its split end in the
wall's face; its outline the cell the mason fitted it to, its ends split on a slant and broken once, its top a lamina's
plane, sometimes with a lamina lost from part of it, its corners knocked; its face split across the laminae in two or
three facets meeting on a ridge; its arrises weathered round; its sides running back into the wall, a little narrower
behind. Rigid: the laying moves and turns it, never bends it.

    wallstone(seed, cell, p) -> dict(P (3 t, 3) the triangles' corners, kind (t,), slit (3 t,), the stone's centre)

It has no cheaper level seen as itself: from an eye along the wall its ends' sides show where it stands proud of its
neighbour, a few pixels wide at any distance, so L1 is L0 and it hands over to the chunk's level
(reviews/lt1/port/2b/r2b/wallstone/switch).

The wall's frame: u along the wall, v up, w out of the face (0 the wall's plane), in metres. The cell is its four
corners (bed left, bed right, top right, top left), each end a straight slant; p is the definition's params (values in
mm and degrees). Numpy only; deterministic from the seed (blender/resolver/hashing.py's streams).
"""

import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "resolver"))
import hashing as HS  # noqa: E402  (the one hash spec)

MM = 0.001


def _between(rng, lo_hi):
    return rng.uniform(lo_hi[0], lo_hi[1])


def outline(rng, cell, p):
    """The face's outline, counter-clockwise from the bed's left end, and each point's chamfer (m)."""
    bl, br, tr, tl = (np.array(c, float) for c in cell)
    H = min(tl[1] - bl[1], tr[1] - br[1])
    # the half joints: the stone smaller than its cell by a joint's half at each side, the ends along the wall
    jb, jt = (_between(rng, p["jointHalfMm"]) * MM for _ in range(2))
    jl, jr = (_between(rng, p["jointHalfMm"]) * MM for _ in range(2))
    bl = bl + (jl, jb)
    br = br + (-jr, jb)
    tr = tr + (-jr, -jt)
    tl = tl + (jl, -jt)
    H = H - jb - jt
    # the stone's own shape inside its cell: its top sloping down to one end (a slab thins along its length), each
    # end split on a slant, the top's corner or the bed's set in (dry joints open into wedges between such stones)
    drop = rng.uniform(*p["topSlope"]) * H
    if rng.random() < 0.5:
        tl = tl + (0.0, -drop)
    else:
        tr = tr + (0.0, -drop)
    for end, sgn in (("l", 1.0), ("r", -1.0)):
        k = rng.uniform(*p["endSlant"]) * H * sgn
        if rng.random() < 0.5:
            if end == "l":
                tl = tl + (k, 0.0)
            else:
                tr = tr + (k, 0.0)
        elif end == "l":
            bl = bl + (k, 0.0)
        else:
            br = br + (k, 0.0)
    pts = [bl, br]
    # the right end, broken once: the split ran in a little from the slant
    jag = min(_between(rng, p["endJagMm"]) * MM, 0.25 * H)
    t = rng.uniform(0.3, 0.7)
    pts.append(br + (tr - br) * t + (-jag, 0.0))
    pts.append(tr)
    # the top, a lamina's plane; sometimes a lamina lost from one end of it, the top stepped down there
    if rng.random() < p["topStepChance"]:
        s = min(_between(rng, p["topStepMm"]) * MM, 0.22 * H)
        us = rng.uniform(0.25, 0.75)
        a = tl + (tr - tl) * us
        run = s * rng.uniform(0.6, 1.6)
        if rng.random() < 0.5:     # the right part lowered
            pts[-1] = tr + (0.0, -s)
            pts += [a + (run, -s), a]
        else:                      # the left part lowered
            pts += [a, a + (-run, -s)]
            tl = tl + (0.0, -s)
    pts.append(tl)
    jag = min(_between(rng, p["endJagMm"]) * MM, 0.25 * H)
    t = rng.uniform(0.3, 0.7)
    pts.append(bl + (tl - bl) * t + (jag, 0.0))
    P = [np.asarray(q, float) for q in pts]
    # the corners knocked: each of the four replaced by two points along its edges, the top's more than the bed's
    # (weather and handling take the upper arrises; the bed's lie protected)
    # (a bed knock smaller than the bed's chamfer is never seen: none unless the definition gives one)
    corners = {0: "bed", 1: "bed"} if p["knockMm"].get("bed") else {}
    out, chamf = [], []
    n = len(P)
    tops = [i for i in range(n) if P[i][1] > bl[1] + 0.5 * H]
    top_corners = {min(tops, key=lambda i: P[i][0] + P[i][1] * 0.01), max(tops, key=lambda i: P[i][0] - P[i][1] * 0.01)}
    c_face = min(_between(rng, p["arrisMm"]) * MM, 0.2 * H)
    for i in range(n):
        a, c, b = P[i - 1], P[i], P[(i + 1) % n]
        kind = corners.get(i, "top" if i in top_corners else None)
        bed_pt = abs(c[1] - bl[1]) < 1e-6
        cc = c_face * (p["bedChamferShare"] if bed_pt else 1.0)
        if kind is None:
            out.append(c)
            chamf.append(cc)
            continue
        knock = _between(rng, p["knockMm"][kind]) * MM * min(1.0, H / 0.15)
        for q, f in ((a, rng.uniform(0.5, 1.0)), (b, rng.uniform(0.5, 1.0))):
            d = q - c
            L = float(np.linalg.norm(d))
            out.append(c + d / L * min(knock * f, 0.35 * L))
            chamf.append(cc)
        if i in corners:   # the bed corner's second point sits on the end, off the bed: its chamfer is the face's
            chamf[-2 if i == 0 else -1] = c_face
    Q = np.array(out)
    # counter-clockwise, from the bed's left end
    if _area(Q) < 0:
        Q, chamf = Q[::-1].copy(), chamf[::-1]
    return Q, np.array(chamf), H


def _area(Q):
    x, y = Q[:, 0], Q[:, 1]
    return 0.5 * float(np.sum(x * np.roll(y, -1) - np.roll(x, -1) * y))


def inset(Q, c):
    """Q offset inward by c (per vertex: the mean of its two edges'), the miters held to three times c."""
    n = len(Q)
    out = np.zeros_like(Q)
    for i in range(n):
        a, b, d = Q[i - 1], Q[i], Q[(i + 1) % n]
        e1 = (b - a) / np.linalg.norm(b - a)
        e2 = (d - b) / np.linalg.norm(d - b)
        n1 = np.array([-e1[1], e1[0]])
        n2 = np.array([-e2[1], e2[0]])
        m = n1 + n2
        ml = np.linalg.norm(m)
        if ml < 1e-6:
            out[i] = b + n1 * c[i]
            continue
        m /= ml
        cosh = max(float(np.dot(m, n1)), 1.0 / 3.0)
        out[i] = b + m * c[i] / cosh
    return out


def wallstone(seed, cell, p):
    rng = HS.Stream(seed, "wallstone-r2b")
    Q, ch, H = outline(rng, cell, p)
    n = len(Q)
    I = inset(Q, ch)
    cen = Q.mean(axis=0)
    L = float(Q[:, 0].max() - Q[:, 0].min())
    # the face: the inner ring on the wall's plane, the split's ridge out from it
    size = min(1.0, H / 0.16)
    bulge = _between(rng, p["bulgeMm"]) * MM * size
    # the fracture: one or two points off the middle where the split stood proudest, each at its own height, and
    # the face's edge not quite on one plane either, so no two facets mirror each other
    u0, u1 = Q[:, 0].min(), Q[:, 0].max()
    v0 = Q[:, 1].min()
    k = 1 if rng.random() < p["faceModes"]["one"] else 2
    if k == 1:
        R = [(u0 + L * rng.uniform(0.3, 0.7), v0 + H * rng.uniform(0.35, 0.7))]
    else:
        a = rng.uniform(0.15, 0.4)
        b = rng.uniform(0.6, 0.85)
        R = [(u0 + L * a, v0 + H * rng.uniform(0.3, 0.75)), (u0 + L * b, v0 + H * rng.uniform(0.3, 0.75))]
    R = np.array(R)
    Rw = np.array([bulge * rng.uniform(0.45, 1.0) for _ in R])
    rim = p["rimMm"] * MM * size
    tris = []
    kinds = []
    slits = []

    def tri(a, b, c, k, slit=(0.0, 0.0, 0.0)):
        tris.append((a, b, c))
        kinds.append(k)
        slits.append(slit)
    # (the face and its arris shade as one rounded surface; the sides, in the joint, keep their edges)

    I3 = [np.array([q[0], q[1], rng.uniform(-rim, rim)]) for q in I]
    R3 = [np.array([q[0], q[1], w]) for q, w in zip(R, Rw)]
    Qf = [np.array([q[0], q[1], -1.0 * c]) for q, c in zip(Q, ch)]
    ring = I3
    if len(R) == 1:
        for i in range(n):
            tri(ring[i], ring[(i + 1) % n], R3[0], 2)
    else:
        d = R[1] - R[0]
        mid = 0.5 * (R[0] + R[1])
        side = [0 if np.dot(q - mid, d) < 0 else 1 for q in I]
        for i in range(n):
            j = (i + 1) % n
            if side[i] == side[j]:
                tri(ring[i], ring[j], R3[side[i]], 2)
            else:
                tri(ring[i], ring[j], R3[side[j]], 2)
                tri(ring[i], R3[side[j]], R3[side[i]], 2)
    # the weathered arris: the outline pushed back by its chamfer, the band between it and the face
    for i in range(n):
        j = (i + 1) % n
        tri(Qf[i], Qf[j], I3[j], 1)
        tri(Qf[i], I3[j], I3[i], 1)
    # the sides, back into the wall as deep as a joint is seen, a little narrower behind
    seen = p["seenMm"] * MM
    taper = p["taperMm"] * MM
    Qb = inset(Q, np.full(n, taper))
    Qb = [np.array([q[0], q[1], -seen]) for q in Qb]
    for i in range(n):
        j = (i + 1) % n
        tri(Qb[i], Qb[j], Qf[j], None, (seen - ch[i], seen - ch[j], 0.0))
        tri(Qb[i], Qf[j], Qf[i], None, (seen - ch[i], 0.0, 0.0))
    # every triangle facing out of the stone (a point inside it, behind the face), each side's face by its normal:
    # 0 its top (a bedding plane), 3 its bed, 2 a split end
    inside = np.array([cen[0], cen[1], -0.6 * seen])
    P, K, S, D = [], [], [], []
    for (a, b, c), k, (da, db, dc) in zip(tris, kinds, slits):
        nrm = np.cross(b - a, c - a)
        ln = np.linalg.norm(nrm)
        if ln < 1e-12:
            continue
        if np.dot(nrm, (a + b + c) / 3.0 - inside) < 0:
            b, c = c, b
            db, dc = dc, db
            nrm = -nrm
        S.append(k is not None)
        if k is None:
            nv = nrm[1] / ln
            k = 0 if nv > 0.6 else (3 if nv < -0.6 else 2)
        P += [a, b, c]
        D += [da, db, dc]
        K.append(k)
    # (slit: each corner's depth into its joint, from the back of the stone's arris, where the joint's slit begins)
    out = dict(P=np.array(P), kind=np.array(K, dtype=np.int8), soft=np.array(S), slit=np.array(D),
               centre=np.array([cen[0], cen[1], 0.0]), bed=float(v0), H=H, L=L)
    return out
