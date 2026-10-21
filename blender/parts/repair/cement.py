"""Cement as a quick fix leaves it (docs/research/repairs.md; upkeep.py): worked in place with a trowel, so its shape is
the hand's, never a mason's. A dab pressed into a corner broken off a step, its top struck roughly level with the
stone, its front rounded where the trowel turned and a little proud or a little short of the old line; and pointing
run along a joint, wider than the joint, smeared onto the stone either side, its edges wandering.

    dab(seed, front, side, reach, height) -> dict of arrays: a lump filling a broken corner up to the stone's
                                         broken edge, the corner at (0, 0), x along the step, y back from the
                                         nosing, z up to the stone's top
    pointing(seed, length, width)     -> a strip along x, centred on y = 0, flat at z = 0

kind 5 (cast cement) and 4 (pointing) for the stone shader (Stone.shader). Lengths in metres; numpy only;
deterministic from the seed.
"""

import random

import numpy as np


def dab(seed, front, side, reach, height, skin=0.012, rays=14, rings=(0.0, 0.06, 0.15, 0.3, 0.55, 0.75, 0.9, 1.0), deep=None):
    """A lump of cement pressed into a corner broken off a step: it fills the break up to the stone's broken edge
    (front(x): how far the edge lies back from the nosing's line at x along the step; side(y): how far in from the
    slab's end at y back from the nosing; both the slab part's own outline, the break only, 0 where it is whole), its
    top struck roughly level with the stone and domed where the trowel lifted, a thin skin feathered onto the stone
    round it that sinks under the stone's top at an uneven line, its front and outer side carried down below the
    break's floor (deep, or most of the slab) with a 2 to 4 mm shoulder. reach: (x, y) how far the break reaches. Meshed in a fan from the corner, so
    its edge follows the break. The broken corner at (0, 0); x along the step, y back from the nosing, z up to the
    stone's top at height."""
    rng = random.Random(f"dab-{seed}")
    c = np.array([-0.001, -0.001])      # (struck flush with the old faces, never a lip)
    w_amp, w_f, w_ph = rng.uniform(0.5, 0.9), rng.uniform(5, 9), rng.uniform(0, 6)

    def inside(P):
        return np.maximum(np.where(P[..., 0] < reach[0], front(P[..., 0]) - P[..., 1], -1.0),
                          np.where(P[..., 1] < reach[1], side(P[..., 1]) - P[..., 0], -1.0))

    th = np.linspace(0.0, np.pi / 2, rays)
    R = np.linspace(0.0, max(reach) + skin * 3, 200)
    Vt, T = [], []
    for k, a in enumerate(th):
        d = np.array([np.cos(a), np.sin(a)])
        P = c + R[:, None] * d
        ins = inside(P)
        sk = skin * (1.0 + w_amp * np.sin(a * w_f + w_ph)) / 2.0 + skin * 0.5
        out = np.nonzero(ins < -sk)[0]
        rb = R[out[0]] if len(out) else R[-1]
        for f in rings:
            p = c + rb * f * d
            Vt.append(p)
            T.append(np.clip(inside(p[None])[0] / sk + 1.0, 0.0, 1.0))      # 0 at the skin's edge, 1 in the break
    Vt, T = np.array(Vt), np.array(T)
    nr = len(rings)
    # struck flush with the stone's top, the trowel's strokes a fraction of a millimetre (a lumpy top read as putty)
    proud = rng.uniform(0.0, 0.0005)
    Z = height - 0.004 + (0.004 + proud) * T ** 0.7 + 0.0003 * np.sin(Vt[:, 0] * rng.uniform(150, 260) + Vt[:, 1] * rng.uniform(80, 160))
    # its front and outer side rounded where the trowel turned
    sh = rng.uniform(0.002, 0.004)
    Z -= sh * np.maximum(np.clip(1.0 - (Vt[:, 1] - c[1]) / 0.006, 0, 1), np.clip(1.0 - (Vt[:, 0] - c[0]) / 0.006, 0, 1)) ** 1.5 * (T > 0.99)
    top = np.column_stack([Vt, Z])
    gid = lambda k, j: k * nr + j
    F = []
    for k in range(rays - 1):
        for j in range(nr - 1):
            if j == 0:
                F.append((gid(k, 0), gid(k, 1), gid(k + 1, 1)))
            else:
                F.append((gid(k, j), gid(k, j + 1), gid(k + 1, j + 1), gid(k + 1, j)))
    # the skirt: the front ray and the side ray carried down below the break's floor, as far as the break goes,
    # rounded over at its shoulder, a little bellied where the cement slumped before it set, its face uneven
    floor = height - (deep if deep is not None else max(height * 0.9, 0.03)) - 0.003
    rows = [(0.35, 0.0006), (0.65, 0.0004), (1.0, 0.0)]      # (how far down, how far out: flush, a hair's belly)
    V = [top]
    base = len(top)
    for ray, facing in ((0, "y"), (rays - 1, "x")):
        ring = [gid(ray, j) for j in range(nr) if T[gid(ray, j)] > 0.5]
        out_ = np.array([0.0, -1.0]) if facing == "y" else np.array([-1.0, 0.0])
        prev = ring
        for depth_, belly in rows:
            P = top[ring].copy()
            z_top = P[:, 2].copy()
            P[:, 2] = z_top + (floor - z_top) * depth_
            jig = np.array([rng.uniform(-0.0004, 0.0004) for _ in ring]) * (depth_ < 1.0)
            P[:, :2] += out_ * (belly + jig)[:, None]
            V.append(P)
            cur = list(range(base, base + len(ring)))
            for k in range(len(ring) - 1):
                if facing == "y":
                    F.append((cur[k], cur[k + 1], prev[k + 1], prev[k]))        # facing -y
                else:
                    F.append((cur[k + 1], cur[k], prev[k], prev[k + 1]))        # facing -x
            prev = cur
            base += len(ring)
    V = np.vstack(V)
    kind = np.full(len(V), 5, dtype=np.int8)
    UV = np.stack([V[:, 0] + V[:, 2] * 0.3, V[:, 1] + V[:, 2] * 0.7], -1)
    return dict(V=V, F=F, kind=kind, edge=np.zeros(len(V)), UV=UV)


def pointing(seed, length, width, n=None):
    """Pointing run along a joint: a flat strip a little wider than the joint, its two edges wandering where the
    trowel smeared it onto the stone."""
    rng = random.Random(f"pointing-{seed}")
    n = n or max(3, int(np.ceil(length / 0.06)) + 1)
    xs = np.linspace(0.0, length, n)
    wob = lambda: np.interp(xs, np.sort(np.concatenate([[0, length], [rng.uniform(0, length) for _ in range(3)]])),
                            [rng.uniform(0.3, 1.0) for _ in range(5)])
    lo = -width / 2 * wob()
    hi = width / 2 * wob()
    V = np.vstack([np.stack([xs, lo, np.zeros(n)], -1), np.stack([xs, hi, np.zeros(n)], -1)])
    F = [(k, k + 1, n + k + 1, n + k) for k in range(n - 1)]
    kind = np.full(len(V), 4, dtype=np.int8)
    return dict(V=V, F=F, kind=kind, edge=np.zeros(len(V)), UV=V[:, :2].copy())
