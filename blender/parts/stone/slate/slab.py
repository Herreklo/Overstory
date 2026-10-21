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


# A corner broken off slate leaves flat faces, not a scoop: the rock parts along straight planes (a curved bite read as
# a bent plank).
def bite_front(x, size):
    """How far a broken corner's bite reaches back from the nosing, at x from the broken end (m): a straight cut."""
    return size * 0.75 * np.clip(1.0 - np.abs(x) / (size * 1.3), 0.0, 1.0)


def bite_side(y, size):
    """How far a broken corner's bite reaches in from the slab's end, at y back from the nosing (m): a straight cut."""
    return size * 0.8 * np.clip(1.0 - np.asarray(y) / (size * 1.1), 0.0, 1.0)


def slab(seed, width, depth, thick, front_round=0.012, side_round=0.006, layers=None, warp=0.003, flake=0.35,
         chip=0.03, edge_jag=0.012, grid=GRID, broken=None, dome=0.0):
    """One slab. front_round, side_round: the radius its edges are rounded to (m); layers: how many split layers
    show in its edges (2 to 4 from its thickness if None); warp: how far its top departs from a plane (m); flake:
    the share of its top a layer lower where one flaked off; chip: how deep its corners are knocked (m); edge_jag:
    how far its split outline wanders (m); broken: (side "l" or "r", size, depth or None): a corner broken off its
    nosing, down to the bedding plane nearest depth (through the whole slab if None); dome: how far its top is crowned
    above its edges (m: a sett worn round by wheels and feet).

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
    # a corner broken off its nosing (upkeep.py: a dropped load, a frost): an angular bite out of the front and the
    # side at one end, its faces fresh split, down to a bedding plane (the slab whole below it)
    o_whole = (o_front.copy(), o_left.copy(), o_right.copy())
    bite_depth = None
    if broken:
        side, size = broken[0], broken[1]
        bite_depth = broken[2] if len(broken) > 2 else None
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
    # the outline as it was before the break, for the faces below it
    X0 = (o_whole[1][:, None] + r_side) + ((width - o_whole[2][:, None] - r_side) - (o_whole[1][:, None] + r_side)) * S
    Y0 = (o_whole[0][None, :] + r_front) + (back - (o_whole[0][None, :] + r_front)) * T
    # the top: a bedding plane, warped, falling a little to the front to shed water, a layer lower where it flaked
    Z = thick + warp * _noise2(rng, X, Y, 0.9) - 0.004 * (1.0 - T)
    if dome > 0:
        # (crowned: highest in the middle, falling to every edge)
        Z += dome * (1.0 - (2.0 * S - 1.0) ** 2) * (1.0 - (2.0 * T - 1.0) ** 2)
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
    P0 = np.stack([X0.ravel(), Y0.ravel()], -1)[ring]
    nring = len(ring)

    def normals_of(Q):
        """Outward normals round a border (in plan)."""
        d = np.roll(Q, -1, axis=0) - np.roll(Q, 1, axis=0)
        n_ = np.stack([d[:, 1], -d[:, 0]], -1)
        return n_ / np.maximum(np.linalg.norm(n_, axis=1, keepdims=True), 1e-9)
    nrm, nrm0 = normals_of(P), normals_of(P0)
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
    # and knocked hard in a few places along the front, where a load or a frost took a piece of the arris
    knock = np.zeros(nring)
    for _ in range(rng.randint(0, 2 + int(width))):
        c_ = rng.randrange(nring)
        L_ = rng.randint(2, 4)
        idx = (np.arange(c_ - L_, c_ + L_ + 1)) % nring
        knock[idx] = np.maximum(knock[idx], rng.uniform(0.008, 0.02) * np.clip(1.0 - np.abs(np.arange(-L_, L_ + 1)) / (L_ + 0.5), 0, 1))
    rad = rad + np.where(side_of == 0, knock, knock * 0.4)
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
    # a break tapers down through the layers: the top one loses the most, each below it less, until at its depth
    # the slab is whole, so it dies out in a few small steps along the bedding planes (one full-size ledge at the
    # break's floor read as the ghost of the unbroken step)
    floor_frac = 1.0 - bite_depth / thick if bite_depth is not None else -1.0

    def bitten(frac):
        """How much of the break a layer at this height (a fraction of the slab's) has lost: 1 at the top, 0 at
        the break's depth and below."""
        if floor_frac < 0.0:
            return 1.0
        return float(np.clip((frac - floor_frac) / max(1.0 - floor_frac, 1e-3), 0.0, 1.0)) ** 0.8

    def kinks(n, k, amp):
        """A line wandering in straight runs with angular kinks (a smooth wander read as wood grain)."""
        bt = np.sort(np.concatenate([[0.0, 1.0], [rng.random() for _ in range(k)]]))
        bv = np.array([rng.uniform(-1.0, 1.0) for _ in bt]) * amp
        return np.interp(np.linspace(0, 1, n), bt, bv)
    z_edge = zt - rad
    prev_out = rad.copy()
    last_ring = (z_edge, rad.copy())
    for k, hk in enumerate(list(heights) + [0.0]):
        # each layer's standing in or out wanders along the edge; at the front more (it was split, then dressed only
        # on top), at the back least
        # each plate stands in or out by its own amount and breaks off abruptly along the edge (a smooth offset
        # along the whole edge read as planed striations)
        # each plate's face in flat facets: straight runs between kinks along the edge (a stepped or smooth offset
        # read as boards or soap), standing in or out by up to a couple of centimetres on a thick block
        amp_f = float(np.clip(thick * 0.08, 0.012, 0.022))
        lay = kinks(nring, max(3, nring // 5), 1.0)
        amp = np.where(side_of == 0, amp_f, np.where(side_of == 2, 0.002, amp_f * 0.65))
        outk = rad + amp * lay - 0.002 * k
        # a parting shows only where a plate has broken away; elsewhere the face runs on from the plate above (each
        # parting along the whole edge at one height read as ruled boards), and the bedding wanders a little
        if hk > 0:
            closed = steps_along(nring, max(3, nring // 8), 0.0, 1.0) < 0.5
            outk = np.where(closed, prev_out, outk)
        zk = z_edge * np.clip(hk + kinks(nring, max(3, nring // 12), 0.03), 0.05, 0.95) if hk > 0 else np.zeros(nring)
        # a ledge: the layer's top edge at the old setback, then its own face below it
        pairs = ((zk + 0.002, prev_out), (zk, outk)) if hk > 0 else ((zk, outk),)
        for zz, oo in pairs:
            # a tall band of a plate is lumpy down its height too: a facet ring every five centimetres, each
            # standing in or out of the straight lean between the band's top and bottom (one flat band a plate read
            # as stacked pancakes)
            za, oa = last_ring
            n_mid = int(np.clip(np.mean(za - np.maximum(zz, 0.0)) / 0.05, 0, 6))
            for m_ in range(1, n_mid + 1):
                f_ = m_ / (n_mid + 1)
                zm = za + (np.maximum(zz, 0.0) - za) * f_
                om = oa + (oo - oa) * f_ + amp * 0.55 * kinks(nring, max(3, nring // 2), 1.0)
                Rm = np.concatenate([P + nrm * om[:, None], zm[:, None]], -1)
                V.append(Rm)
                kind.append(np.full(nring, 2, dtype=np.int8))
                edge.append(np.zeros(nring))
                rings.append(np.arange(base, base + nring))
                base += nring
            R = np.concatenate([P + nrm * oo[:, None], np.maximum(zz, 0.0)[:, None]], -1)
            V.append(R)
            kind.append(np.full(nring, 2, dtype=np.int8))
            edge.append(np.zeros(nring))
            rings.append(np.arange(base, base + nring))
            base += nring
            last_ring = (np.maximum(zz, 0.0), oo)
        # and each plate leans in or out from its top to its bottom, so the next parting starts where it ends
        prev_out = outk + amp * 0.7 * kinks(nring, max(2, nring // 7), 1.0)
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
    # the break: a plane cut across the corner (slate parts along planes), the top layer losing the most and each
    # below it less, down to the break's depth, every point inside a layer's corner triangle moved onto its cut
    corner = None
    if broken:
        cx = 0.0 if side == "l" else width
        sgn = 1.0 if side == "l" else -1.0
        b_, a_ = size * 1.3, size * 0.75                # along the step from the end, back from the nosing
        ff = np.array([bitten(z / max(thick, 1e-6)) for z in V[:, 2]])
        B, A = b_ * ff, a_ * ff
        u, v = np.abs(V[:, 0] - cx), V[:, 1]
        ok = (B > 1e-4) & (A > 1e-4)
        q = np.where(ok, u / np.maximum(B, 1e-6) + v / np.maximum(A, 1e-6), 9.0)
        inside = q < 1.0
        nx, ny = 1.0 / np.maximum(B, 1e-6), 1.0 / np.maximum(A, 1e-6)
        nn = np.hypot(nx, ny)
        d = (1.0 - q) / nn
        V[inside, 0] = cx + sgn * (u + d * nx / nn)[inside]
        V[inside, 1] = (v + d * ny / nn)[inside]
        # where the stone's own front and end stand at the corner, and the cut, for a dab fitted to it
        corner = dict(side=side, along=b_, back=a_, depth=bite_depth if bite_depth is not None else thick,
                      front=float((o_front[0] if side == "l" else o_front[-1]) + r_front),
                      end=float((o_left[0] if side == "l" else o_right[0]) + r_side))
    # round the outline for each ring's points (faces' u), and the top in metres
    s_all = np.zeros(len(V))
    for r_ in rings[1:]:
        s_all[r_] = per
    UV = np.where((kind == 0)[:, None], V[:, :2], np.stack([s_all, V[:, 2]], -1))
    # its outline as cut, for what is fitted to it (a dab in a broken corner): how far each edge lies inward
    outline = dict(x=np.linspace(0.0, width, nu), front=o_front + r_front, y=np.array(ys, float),
                   left=o_left + r_side, right=o_right + r_side)
    return dict(V=V, F=F, kind=kind, edge=edge, s=s_all, UV=UV, width=width, depth=depth, thick=thick,
                front_round=r_front, outline=outline, corner=corner)
