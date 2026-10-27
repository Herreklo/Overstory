"""The mass card: a piece of a crown's mass as a painter blocks it, solid within and broken only at its edge
(reviews/lt1/art-direction/README.md, the trees: masses, never leaves). Four cells, 2 by 2: a round clump, a wide one
for a mass's underside, a notched one, and a thin one for a crown losing itself upward. The edge is a birch's: a fine
fringe of small leaves (a few centimetres on a card of 1.6 m, never legible one by one past a few metres) and fine
sprays standing out of it, so the outline has promontories and bays of sky; inside, one solid value, no speckle.

Channels: r how far in from the clump's edge (0 at a leaf's tip, 1 in the solid core), g each leaf's own seed (0 the
core), b 0, a coverage. Numpy only; deterministic (seeded from the part's name through blender/resolver/hashing.py).

    python3.13 blender/parts/trees/mass_card.py unity/Assets/Art/Trees/Corner/mass_card_clusters.png

(the _clusters name is how ArtImport.cs imports a tree's spray: linear, clamped, its coverage kept in every mip)
"""

import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", ".."))
from painting import write_png, downsample, leaf_width        # noqa: E402
from resolver import hashing as HS                            # noqa: E402

CELL = 1024     # painted per cell, written at half


def cell_shape(kind, seed):
    """The clump's solid core: its outline radius by angle (shares of the cell's half-width), and its stretch."""
    s = HS.Stream("mass-card", kind, seed)
    ang = np.linspace(0.0, 2 * math.pi, 720, endpoint=False)
    r = np.full_like(ang, 0.50 if kind != "thin" else 0.30)
    # broad lobes, never a ruled circle
    for k, amp in ((2, 0.05), (3, 0.07), (4, 0.04), (6, 0.035), (9, 0.02)):
        r += amp * np.cos(k * ang + s.uniform(0, 2 * math.pi))
    sx, sy = (1.2, 0.74) if kind == "wide" else (1.0, 1.0)
    if kind == "notched":
        # a deep notch of sky into one side, a seam between two lobes
        a0 = s.uniform(0, 2 * math.pi)
        d = np.angle(np.exp(1j * (ang - a0)))
        r -= 0.36 * np.exp(-(d / 0.28) ** 2)
    return ang, np.maximum(r, 0.08), sx, sy


def leaf(cover, ids, depth, xs, ys, bx, by, heading, length, idv):
    """One bold leaf from its stalk's end (bx, by) along heading, length in pixels, into the coverage."""
    n = cover.shape[0]
    r = int(length * 1.3 + 4)
    y0, y1 = max(int(by) - r, 0), min(int(by) + r, n)
    x0, x1 = max(int(bx) - r, 0), min(int(bx) + r, n)
    if y0 >= y1 or x0 >= x1:
        return
    X, Y = xs[y0:y1, x0:x1], ys[y0:y1, x0:x1]
    ca, sa = math.cos(heading), math.sin(heading)
    u = (X - bx) * ca + (Y - by) * sa
    v = -(X - bx) * sa + (Y - by) * ca
    t = u / length
    half = leaf_width(np.clip(t, 0, 1)) * length * 1.3
    blade = np.clip((half - np.abs(v)) / 1.5 + 0.5, 0.0, 1.0) * ((t >= 0) & (t <= 1))
    win = cover[y0:y1, x0:x1]
    ids[y0:y1, x0:x1] = np.where((blade > win) & (blade > 0.5), idv, ids[y0:y1, x0:x1])
    cover[y0:y1, x0:x1] = np.maximum(win, blade)
    depth[y0:y1, x0:x1] = np.maximum(depth[y0:y1, x0:x1], blade * np.clip(0.5 - 0.5 * t, 0.0, 1.0))


def paint_cell(kind, seed):
    n = CELL
    ys, xs = np.mgrid[0:n, 0:n].astype(np.float32)
    cx = cy = n / 2.0
    ang, rr, sx, sy = cell_shape(kind, seed)
    hw = n / 2.0
    dx, dy = (xs - cx) / (sx * hw), (ys - cy) / (sy * hw)
    rho = np.hypot(dx, dy)
    th = np.mod(np.arctan2(dy, dx), 2 * math.pi)
    edge = np.interp(th, ang, rr, period=2 * math.pi)
    cover = np.clip((edge - rho) * hw / 2.0 + 0.5, 0.0, 1.0).astype(np.float32)
    depth = np.clip((edge - rho) / 0.3, 0.0, 1.0).astype(np.float32)
    ids = np.zeros_like(cover)
    s = HS.Stream("mass-card-leaves", kind, seed)
    L = 0.035 * n                      # a leaf: about 5 cm on a near card of 1.6 m
    count = 0

    def at(a, reach):
        e = float(np.interp(a % (2 * math.pi), ang, rr, period=2 * math.pi))
        return cx + math.cos(a) * e * reach * sx * hw, cy + math.sin(a) * e * reach * sy * hw

    # the core's outline broken by leaves lying over it, each its own way (never a ring of teeth)
    ring = 150 if kind != "thin" else 60
    for k in range(ring):
        a = 2 * math.pi * (k + s.uniform(-0.45, 0.45)) / ring
        bx, by = at(a, s.uniform(0.86, 1.0))
        count += 1
        leaf(cover, ids, depth, xs, ys, bx, by, a + s.uniform(-1.2, 1.2), L * s.uniform(0.7, 1.15), count / 2000.0)
    # clumps: small sprays of leaves gathered round a twig's end, set on and just out of the outline, uneven round
    # it, so the outline breaks at three scales (the core's broad lobes, the clumps, the leaves) with bays of sky
    # between them (the broken edge of a painted mass)
    clumps = {"round": 34, "wide": 36, "notched": 30, "thin": 30}[kind]
    for k in range(clumps):
        a = 2 * math.pi * (k + s.uniform(-0.5, 0.5)) / clumps
        cxk, cyk = at(a, s.uniform(0.92, 1.5 if kind == "thin" else 1.25))
        rad = L * s.uniform(1.2, 3.2) * (1.2 if kind == "thin" else 1.0)
        for _ in range(int(4 + 3 * rad / L)):
            # each leaf from a point inside the clump, heading out of it: the clump's own edge is leaf tips
            q, d = s.uniform(0, 2 * math.pi), rad * math.sqrt(s.uniform(0.0, 1.0)) * 0.55
            px, py = cxk + math.cos(q) * d, cyk + math.sin(q) * d
            count += 1
            leaf(cover, ids, depth, xs, ys, px, py, q + s.uniform(-0.7, 0.7), L * s.uniform(0.7, 1.1), count / 2000.0)
    return depth, ids, cover


KINDS = ("round", "wide", "notched", "thin")


def atlas(path, seed=1):
    half = CELL // 2
    out = np.zeros((2 * half, 2 * half, 4), np.uint8)
    for c, kind in enumerate(KINDS):
        depth, ids, cover = paint_cell(kind, seed)
        d, i, a = (downsample(x, 2) for x in (depth, ids, cover))
        cell = np.stack([d, i, np.zeros_like(d), a], axis=-1)
        # straight colour under a coverage edge: the core's values bleed out so mips never pull in black
        r0, c0 = (c // 2) * half, (c % 2) * half
        out[r0:r0 + half, c0:c0 + half] = np.clip(cell * 255.0 + 0.5, 0, 255).astype(np.uint8)
    # rows top-down in the PNG: cell 0 top left
    return write_png(path, out)


if __name__ == "__main__":
    print(atlas(sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "mass_card_clusters.png")))
