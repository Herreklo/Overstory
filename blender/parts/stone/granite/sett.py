"""A hewn sett as it lies in a lane (the board, docs/references/stone/02, 13, 14): a block of hard rock a hand or two
long, its top crowned and its arrises worn round by wheels and feet, its outline a little out of square as the
mason's hammer left it, its sides running down into the sand bed (all a joint shows of them). Light: a sett is one of
thousands, so it is about forty triangles; its worn crystals and its hewn sides are painted (granite_grain.png).

    sett(seed, length, width, crown=0.004, round_=0.006, skew=0.006, depth=0.05) -> dict(V, F, kind, edge, UV)

Lengths in metres; x along the sett (0 to length), y across (0 to width), z up to its crown at 0, its sides down to
-depth. kind 0 top, 1 the worn arris, 2 a hewn side. Numpy only; deterministic from the seed.
The seed is the piece's key, an int or a string (its stable id hashed with the world seed: h(worldSeed, id)); its
draws come from the hash spec's stream (blender/resolver/hashing.py), never the random module.
"""

import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "resolver"))
import hashing as HS  # noqa: E402  (the one hash spec)


def sett(seed, length, width, crown=0.004, round_=0.006, skew=0.006, depth=0.05):
    rng = HS.Stream(seed, "sett")
    # the outline: four corners a little out of square, each edge with one kink where the hammer took a flake
    c = [(0.0, 0.0), (length, 0.0), (length, width), (0.0, width)]
    c = [(x + rng.uniform(-skew, skew), y + rng.uniform(-skew, skew)) for x, y in c]
    ring = []
    for k in range(4):
        (x0, y0), (x1, y1) = c[k], c[(k + 1) % 4]
        t = rng.uniform(0.3, 0.7)
        nx, ny = (y1 - y0), -(x1 - x0)
        nl = max(np.hypot(nx, ny), 1e-6)
        inset = rng.uniform(0.0, skew)
        ring.append((x0, y0))
        ring.append((x0 + (x1 - x0) * t - nx / nl * inset, y0 + (y1 - y0) * t - ny / nl * inset))
    P = np.array(ring)                                  # 8 points round the outline, counter-clockwise
    ctr = P.mean(0)
    n = len(P)
    r = round_ * rng.uniform(0.6, 1.4)
    # rings: the crown's middle, the top's edge inset by the rounding, the arris, the side's top and its foot
    inner = ctr + (P - ctr) * 0.45
    top_edge = ctr + (P - ctr) * (1.0 - r / max(min(length, width) / 2, r * 2))
    z_mid = 0.0
    z_top = -crown
    z_arris = z_top - r * 0.7
    V = [np.array([[ctr[0], ctr[1], z_mid + rng.uniform(-0.001, 0.001)]]),
         np.column_stack([inner, np.full(n, z_mid - crown * 0.35)]),
         np.column_stack([top_edge, np.full(n, z_top)]),
         np.column_stack([P, np.full(n, z_arris)]),
         np.column_stack([P, np.full(n, z_arris - r)]),
         np.column_stack([P + (P - ctr) * 0.02, np.full(n, -depth)])]
    kind = [np.zeros(1), np.zeros(n), np.zeros(n), np.ones(n), np.full(n, 2), np.full(n, 2)]
    V = np.vstack(V)
    kind = np.concatenate(kind).astype(np.int8)
    F = []
    for k in range(n):
        F.append((0, 1 + k, 1 + (k + 1) % n))
    for ring_a in range(1, 5):
        a0, b0 = 1 + (ring_a - 1) * n, 1 + ring_a * n
        for k in range(n):
            k1 = (k + 1) % n
            F.append((a0 + k, b0 + k, b0 + k1, a0 + k1))
    # distance to the outline on the top, for the joints' moss and the wear
    d_edge = np.zeros(len(V))
    d_edge[0] = min(length, width) / 2
    d_edge[1:1 + n] = min(length, width) / 4
    UV = np.where((kind == 0)[:, None], V[:, :2], np.column_stack([np.arange(len(V)) * 0.0 + V[:, 0] + V[:, 1], V[:, 2]]))
    return dict(V=V, F=F, kind=kind, edge=d_edge, UV=UV)
