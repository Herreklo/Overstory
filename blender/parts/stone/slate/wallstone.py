"""The wall stone: a thin flat piece of the town's slaty rock as a dry-stone wall shows it (docs/stone.md; the board,
docs/references/stone/: 03 Gamle Stavanger's garden wall, 09 and 10 Bergen's retaining walls, 11 a mossy wall): laid on
its bed, only its split end shows in the wall's face, a little bulged, its outline broken in straight runs with knocked
corners, and its sides running back into the wall a few centimetres (all a joint shows of it). Its back and bed are
never seen.

    face_stone(seed, length, height, depth=0.07, ...) -> dict of arrays

Lengths in metres; u along the wall (0 at the stone's left end), v up from its bed (0) to its top (height), w out of
the wall's face (0 the face plane, positive out). Numpy only; deterministic from the seed.
"""

import math
import random

import numpy as np


def _outline(rng, length, height, jag, chip, step=0.05):
    """The face's outline, counter-clockwise from the bottom left: straight runs between angular breaks along each
    side, inward only, the corners knocked."""
    pts = []

    def side(a, b, n_in):
        L = float(np.linalg.norm(np.subtract(b, a)))
        n = max(2, int(math.ceil(L / step)))
        t = np.linspace(0.0, 1.0, n, endpoint=False)
        k = max(1, int(round(L / 0.12)))
        bt = np.sort(np.concatenate([[0.0, 1.0], [rng.random() for _ in range(k)]]))
        bv = np.array([rng.random() for _ in bt]) * jag
        off = np.interp(t, bt, bv)
        for tt, o in zip(t, off):
            pts.append((a[0] + (b[0] - a[0]) * tt + n_in[0] * o, a[1] + (b[1] - a[1]) * tt + n_in[1] * o))

    c = [(0.0, 0.0), (length, 0.0), (length, height), (0.0, height)]
    ins = [(0.0, 1.0), (-1.0, 0.0), (0.0, -1.0), (1.0, 0.0)]
    for i in range(4):
        side(c[i], c[(i + 1) % 4], ins[i])
    P = np.array(pts)
    # the corners knocked: points near each corner pulled in along the diagonal
    for cx, cy in c:
        d = np.hypot(P[:, 0] - cx, P[:, 1] - cy)
        k = chip * rng.uniform(0.3, 1.2)
        pull = np.clip(1.0 - d / max(k * 2.5, 1e-3), 0.0, 1.0) * k
        dirx = np.sign(length / 2 - cx)
        diry = np.sign(height / 2 - cy)
        P[:, 0] += pull * dirx * 0.7
        P[:, 1] += pull * diry * 0.7
    return P


def face_stone(seed, length, height, depth=0.07, bulge=0.006, jag=0.008, chip=0.012):
    """One stone's face in a wall. Returns V (n, 3), F, kind (all 2: a split face), UV (n, 2: u and v in metres, so the
    laminae run along the wall), and w0 (the face plane's offset of each vertex, for the generator's lean)."""
    rng = random.Random(f"wallstone-{seed}")
    P = _outline(rng, length, height, min(jag, height * 0.2), min(chip, height * 0.35))
    n = len(P)
    centre = np.array([length / 2, height / 2])
    inner = centre + (P - centre) * 0.82
    # the face: the outline at the face plane rounded back a little, an inner ring bulged out, the centre most
    rim_back = -min(0.006, height * 0.08)
    b_inner = bulge * rng.uniform(0.5, 1.2)
    b_centre = bulge * rng.uniform(0.9, 1.6)
    V = [np.column_stack([P, np.full(n, rim_back)]),
         np.column_stack([inner, np.full(n, b_inner)]),
         np.array([[centre[0], centre[1], b_centre]])]
    # the sides running back into the wall
    V.append(np.column_stack([P, np.full(n, -depth)]))
    V = np.vstack(V)
    F = []
    o_rim, o_in, o_c, o_back = 0, n, 2 * n, 2 * n + 1
    for i in range(n):
        j = (i + 1) % n
        F.append((o_rim + i, o_rim + j, o_in + j, o_in + i))
        F.append((o_in + i, o_in + j, o_c))
        F.append((o_back + i, o_back + j, o_rim + j, o_rim + i))
    kind = np.full(len(V), 2, dtype=np.int8)
    UV = V[:, :2].copy()
    return dict(V=V, F=F, kind=kind, UV=UV, edge=np.zeros(len(V)))
