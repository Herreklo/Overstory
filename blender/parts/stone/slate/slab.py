"""The slab: a piece of the town's own slaty rock, split along its bedding into a slab (docs/stone.md; the board,
docs/references/stone/: 02 and 03, Gamle Stavanger's flagstones and walls; 06, the split-slab stair at Dale). As a
mason leaves it: its outline wanders where it was split and its corners are knocked; its top is a bedding plane,
nearly flat but warped and here and there a layer lower where one flaked off; its front and sides are the split
edge, stacked thin layers each standing a little in or out; its edges rounded a little where it was dressed, the
front most. No wear and no growth: those are the piece's history, laid on by the generator from its facts.

    slab(seed, width, depth, thick, front_round=..., ...) -> dict of arrays

Lengths in metres; x across the slab (its width), y from its front edge (0) to its back (depth), z up from its bed
(0) to its top (thick). Numpy only; deterministic from the seed.
"""

import math
import random

import numpy as np

GRID = 0.08          # the top's grid across: enough for a worn hollow (half a metre wide) to be real shape
ROWS = (0.0, 0.012, 0.03, 0.06, 0.11)   # its rows from the front: fine over the nosing, where it rounds and wears
ROW = 0.12           # and on, back to the edge it lies under the step above


def _noise1(rng, n, freqs):
    """A smooth closed curve's offsets: sines at the given frequencies (cycles along the curve), each its own phase
    and weight; n samples."""
    t = np.arange(n) / n
    out = np.zeros(n)
    for f, a in freqs:
        out += a * np.sin(2 * math.pi * (f * t + rng.random()))
    return out


def _noise2(rng, x, y, scale, octaves=3, along=None):
    """Smooth value-like noise in [-1, 1] from summed rotated sines (no grid, so no squares); along (radians) keeps
    every octave's stripes near that heading, so its features run that way (a cleavage's ridges)."""
    out = np.zeros_like(x)
    amp, tot = 1.0, 0.0
    for o in range(octaves):
        a = rng.random() * math.pi if along is None else along + rng.uniform(-0.15, 0.15)
        k = (2 ** o) / scale
        u = x * math.cos(a) + y * math.sin(a)
        v = -x * math.sin(a) + y * math.cos(a)
        out += amp * np.sin(k * u * 6.283 + rng.random() * 6.283) * np.sin(k * v * 4.7 + rng.random() * 6.283)
        tot += amp
        amp *= 0.5
    return out / tot


def slab(seed, width, depth, thick, front_round=0.012, side_round=0.006, layers=None, warp=0.003, flake=0.35,
         chip=0.03, edge_jag=0.012, grid=GRID):
    """One slab. front_round, side_round: the radius its edges are rounded to (m); layers: how many split layers
    show in its edges (2 to 4 from its thickness if None); warp: how far its top departs from a plane (m); flake:
    the share of its top a layer lower where one flaked off; chip: how deep its corners are knocked (m); edge_jag:
    how far its split outline wanders (m).

    Returns V (n, 3), F (list of index tuples), and per vertex: kind (0 top, 1 rounded edge, 2 split face, 3 bed),
    edge (on the top: distance to its outline, m; elsewhere 0), s (on the faces: distance round the outline from the
    front left corner, m), and UV (n, 2): the top in metres (x, y), the faces round and up (s, z)."""
    rng = random.Random(f"slab-{seed}")
    nu = max(int(math.ceil(width / grid)), 3) + 1
    ys = [y for y in ROWS if y < depth - 0.05] + list(np.arange(ROWS[-1] + ROW, depth - 0.04, ROW)) + [depth]
    nv = len(ys)

    # the outline: each edge wanders inward by its own amount along it (never outward, so the slab keeps its size
    # as the generator fits it), its corners knocked
    def edge_offsets(n, length):
        # a split edge breaks in straight runs with angular turns (a smooth wobble read as a lobed tongue): a
        # piecewise-linear line through a few random breaks, then a little fine roughness
        t = np.linspace(0, 1, n)
        k = max(2, int(round(length / 0.25)) + rng.randint(0, 2))
        bt = np.sort(np.concatenate([[0.0, 1.0], [rng.random() for _ in range(k - 1)]]))
        bv = np.array([rng.random() for _ in bt])
        o = np.interp(t, bt, bv) + 0.15 * _noise1(rng, n, [(rng.uniform(9, 14), 1.0)])
        o = (o - o.min()) / max(np.ptp(o), 1e-9) * edge_jag
        for end in (0.0, 1.0):
            c = chip * rng.uniform(0.3, 1.2)
            w = rng.uniform(0.05, 0.12) / max(length, 0.1)
            o += c * np.clip(1.0 - np.abs(t - end) / max(w, 1e-3), 0.0, 1.0) ** 1.5
        return o

    o_front = edge_offsets(nu, width)        # inward from y = 0, along x
    o_back = edge_offsets(nu, width) * 0.5   # the back lies under the next step: plainer
    o_left = edge_offsets(nv, depth)
    o_right = edge_offsets(nv, depth)
    r_front = front_round * rng.uniform(0.7, 1.3)
    r_side = side_round * rng.uniform(0.6, 1.4)

    # the top grid, conforming to the outline, inset by each edge's rounding
    s = np.linspace(0.0, 1.0, nu)
    t = np.array(ys) / depth
    S, T = np.meshgrid(s, t, indexing="xy")                       # (nv, nu)
    left = o_left[:, None] + r_side
    right = width - o_right[:, None] - r_side
    front = o_front[None, :] + r_front
    back = depth - o_back[None, :] - 0.003
    X = left + (right - left) * S
    Y = front + (back - front) * T
    # the top: a bedding plane, warped, falling a little to the front to shed water, a layer lower where it flaked
    Z = thick + warp * _noise2(rng, X, Y, 0.9) - 0.004 * (1.0 - T)
    fl = _noise2(rng, X, Y, 0.35, octaves=4, along=0.0)
    step_ = rng.uniform(0.004, 0.009)
    if flake > 0:
        th = np.quantile(fl, 1.0 - flake)
        Z -= step_ * np.clip((fl - th) / 0.08, 0.0, 1.0)
    # distance to the outline, for the generator (moss in the joints, lichen on the quiet ends) and the rounding
    E = np.minimum.reduce([X - (left - r_side), (right + r_side) - X, Y - (front - r_front), (back + 0.003) - Y])

    V = [np.stack([X.ravel(), Y.ravel(), Z.ravel()], -1)]
    kind = [np.zeros(nu * nv, dtype=np.int8)]
    edge = [E.ravel()]
    F = []
    gid = lambda i, j: j * nu + i
    for j in range(nv - 1):
        for i in range(nu - 1):
            F.append((gid(i, j), gid(i + 1, j), gid(i + 1, j + 1), gid(i, j + 1)))
    # the top's border, counter-clockwise seen from above, starting at the front left corner
    ring = [gid(i, 0) for i in range(nu)] + [gid(nu - 1, j) for j in range(1, nv)] + \
           [gid(i, nv - 1) for i in range(nu - 2, -1, -1)] + [gid(0, j) for j in range(nv - 2, 0, -1)]
    top = V[0]
    P = top[ring][:, :2]
    nring = len(ring)
    # outward normals round the border (in plan)
    d = np.roll(P, -1, axis=0) - np.roll(P, 1, axis=0)
    nrm = np.stack([d[:, 1], -d[:, 0]], -1)
    nrm /= np.maximum(np.linalg.norm(nrm, axis=1, keepdims=True), 1e-9)
    # which edge each border point is on: the front rounds most, the back least
    side_of = np.array([0] * nu + [1] * (nv - 1) + [2] * (nu - 1) + [3] * (nv - 2))
    rad = np.where(side_of == 0, r_front, np.where(side_of == 2, 0.003, r_side))
    # the arris rounded unevenly, crisp in places and knocked in others (an even round caught the light as one line
    # along every nosing)
    def steps_along(n, k, lo, hi):
        bt = np.sort(np.concatenate([[0.0, 1.0], [rng.random() for _ in range(k)]]))
        bv = np.array([rng.uniform(lo, hi) for _ in bt])
        idx = np.clip(np.searchsorted(bt, np.linspace(0, 1, n), side="right") - 1, 0, len(bv) - 1)
        return bv[idx]
    rad = rad * steps_along(nring, max(3, nring // 6), 0.25, 1.7)
    per = np.concatenate([[0.0], np.cumsum(np.linalg.norm(np.diff(P, axis=0), axis=1))])

    rings = [np.array(ring)]
    base = len(top)
    zt = top[ring][:, 2]
    # the rounding: two rings stepping out and down over the edge's radius (a quarter round)
    for a in (0.45, 1.0):
        ang = a * math.pi / 2
        out = rad * math.sin(ang)
        dz = rad * (1.0 - math.cos(ang))
        R = np.concatenate([P + nrm * out[:, None], (zt - dz)[:, None]], -1)
        V.append(R)
        kind.append(np.full(nring, 1, dtype=np.int8))
        edge.append(np.zeros(nring))
        rings.append(np.arange(base, base + nring))
        base += nring
    # the split face: its layers, each standing a little in or out, down to the bed
    nl = layers or max(2, min(4, int(round(thick / 0.05))))
    heights = np.sort(np.array([rng.uniform(0.15, 0.85) for _ in range(nl - 1)]))[::-1]
    z_edge = zt - rad
    prev_out = rad.copy()
    for k, hk in enumerate(list(heights) + [0.0]):
        # each layer's standing in or out wanders along the edge; at the front more (it was split, then dressed only
        # on top), at the back least
        # each plate stands in or out by its own amount and breaks off abruptly along the edge (a smooth offset
        # along the whole edge read as planed striations)
        lay = steps_along(nring, max(2, nring // 10), -1.0, 1.0) + 0.2 * _noise1(rng, nring, [(rng.uniform(6, 10), 1.0)])
        amp = np.where(side_of == 0, 0.012, np.where(side_of == 2, 0.002, 0.008))
        outk = rad + amp * lay - 0.002 * k
        zk = z_edge * hk if hk > 0 else np.zeros(nring)
        # a ledge: the layer's top edge at the old setback, then its own face below it
        for zz, oo in ((zk + 0.002, prev_out), (zk, outk)) if hk > 0 else ((zk, outk),):
            R = np.concatenate([P + nrm * oo[:, None], np.maximum(zz, 0.0)[:, None]], -1)
            V.append(R)
            kind.append(np.full(nring, 2, dtype=np.int8))
            edge.append(np.zeros(nring))
            rings.append(np.arange(base, base + nring))
            base += nring
        prev_out = outk
    # the faces between consecutive rings (round the slab's border, whose points follow its grid)
    for ra, rb in zip(rings, rings[1:]):
        for k in range(nring):
            k1 = (k + 1) % nring
            F.append((ra[k], rb[k], rb[k1], ra[k1]))
    # the bed: a fan from its middle
    last = rings[-1]
    centre = np.array([[width / 2, depth / 2, 0.0]])
    V.append(centre)
    kind.append(np.array([3], dtype=np.int8))
    edge.append(np.zeros(1))
    c = base
    for k in range(nring):
        F.append((last[(k + 1) % nring], last[k], c))
    V = np.concatenate(V)
    kind = np.concatenate(kind)
    edge = np.concatenate(edge)
    # round the outline for each ring's points (faces' u), and the top in metres
    s_all = np.zeros(len(V))
    for r_ in rings[1:]:
        s_all[r_] = per
    UV = np.where((kind == 0)[:, None], V[:, :2], np.stack([s_all, V[:, 2]], -1))
    return dict(V=V, F=F, kind=kind, edge=edge, s=s_all, UV=UV, width=width, depth=depth, thick=thick,
                front_round=r_front)
