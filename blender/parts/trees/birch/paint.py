"""The downy birch's painted parts (Betula pubescens): its foliage and its bark, as mask textures the tree shader colours.

    python blender/parts/trees/birch/paint.py [unity project]      (numpy only; writes PNGs)

Leaves (birch_leaves.png, 1024 square, a 2 by 2 atlas of sprays, each cell one card about 0.42 m across). A spray is
what grows on a birch twig's end: a thin twig with short shoots along it, each bearing two or three leaves, and the
long shoot's leaves at its tip, smaller towards it. Downy birch leaves are ovate, rounded at the base, pointed, coarsely
toothed, 3 to 5 cm long on a stalk of about 1.5 cm. Channels (linear data, not colour):
- R: the leaf's own id, 0.06 to 1 (0 is the twig): each leaf turns and falls in its own seeded order, the same leaves
  first every year;
- G: light within the spray: leaves behind the others darker, a lighter midrib, darker edges;
- B: thickness, for the light through the leaves (a leaf's middle thick, its edge thin; the twig none);
- A: coverage, antialiased.

Clusters (birch_clusters.png, the atlas the tree's cards carry, four cells): the foliage as a downy birch carries it,
on sprays that go out and up (a twig rising out of the crown, side twigs climbing and spreading, every tip only
nodding), bold flat leaves along them, dense in a mass's core and sparse at its skin, long and short (CLUSTERS; the
assembler reads each cell's anchor from there). Channels as every tree's cluster atlas (blender/parts/trees/
painting.py); G is the spray's own light (lit along its upper edge, one mid value below, a soft shade underneath).
Its bare twigs (birch_twigs.png, the same cells): the spray's twigs and finer ones going out and up, the winter
crown's haze, shown as each card's leaves fall.

Marks (birch_marks.png, 4 by 4 cells, MARK_KINDS): the bark's dark marks, sixteen shapes (slashes, broken slashes,
rows of small dashes, hooks, old scars, chevrons), each a tear in the outer bark, some with the torn lip curled up
above; placed by the assembler (large ones where the tree shed a branch, chevrons over living ones, the rest the
bark's own lenticels, seeded); G lightness, B relief, A coverage.

Bark (birch_bark.png, 512 by 1024, tiling; u round the stem, v along it, one tile 0.3 m round and 0.6 m along):
- R: the bark's lightness, white with soft grey bands;
- G: lenticels (the short dark horizontal dashes) and the dark scars under branches;
- B: unused (lichen and an old trunk's dark foot are the shader's, from noise round the trunk, so they never repeat
  with the tile);
- A: the relief: thin horizontal rings of the outer bark, a faint grain along the stem, the lenticels sunk in; the
  shader bends the light by it.

Painted with numpy on a supersampled grid, deterministic from fixed seeds, so the same file comes out every time.
"""

import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from painting import CELL, atlas, curve, downsample, leaf_px, leaf_width, twig_cover, write_png  # noqa: E402

SEED = 1989


# -- leaves -------------------------------------------------------------------------------------------------------------

CARD = 0.42          # metres across a card
PX = CELL / CARD     # pixels per metre while painting


def _twig(rng, x0, y0, ang, length, curl, n=14):
    """A gently curving twig: points from (x0, y0) along ang (radians, image space), bending by curl."""
    pts = [(x0, y0)]
    a = ang
    step = length / n
    for _ in range(n):
        a += curl / n
        x0, y0 = x0 + math.cos(a) * step, y0 + math.sin(a) * step
        pts.append((x0, y0))
    return pts


def paint_spray(rng, kind):
    """One spray in one cell: a mother twig with side twiglets fanning wide, short shoots of two or three leaves
    along all of them, the long shoots' leaves at their tips, smaller towards them. Returns (id, light, thick, cover)
    supersampled."""
    n = CELL
    ys, xs = np.mgrid[0:n, 0:n].astype(np.float32)
    leaf_id = np.zeros((n, n), np.float32)
    light = np.zeros((n, n), np.float32)
    thick = np.zeros((n, n), np.float32)
    cover = np.zeros((n, n), np.float32)

    sides = {"spray": 5, "dense": 6, "open": 4, "tip": 3}[kind]
    spacing = {"spray": 0.024, "dense": 0.019, "open": 0.032, "tip": 0.026}[kind] * PX
    up = -math.pi / 2                                   # image y runs down: the twig grows up the card
    mother = _twig(rng, n * (0.5 + rng.uniform(-0.04, 0.04)), n * 0.97, up + rng.uniform(-0.12, 0.12),
                   n * 0.80, rng.uniform(-0.35, 0.35))
    twigs = [(mother, 1.0)]
    for k in range(sides):
        t = 0.2 + 0.6 * (k + rng.uniform(0.0, 0.6)) / sides
        i = int(t * (len(mother) - 1))
        (x0, y0), (x1, y1) = mother[i], mother[i + 1]
        along = math.atan2(y1 - y0, x1 - x0)
        side = 1 if k % 2 else -1
        a = along + side * math.radians(rng.uniform(44, 70))
        L = n * rng.uniform(0.26, 0.42) * (1.0 - 0.3 * t)
        twigs.append((_twig(rng, x0, y0, a, L, -side * rng.uniform(0.2, 0.5), 10), 0.7))

    # the leaves: along each twig a short shoot every few centimetres, alternately left and right
    leaves = []
    for pts, w in twigs:
        total = sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(pts, pts[1:]))
        d, k = spacing * rng.uniform(0.6, 1.2), 0
        while d < total:
            # the point and direction at distance d along the twig
            acc = 0.0
            for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
                seg = math.hypot(x1 - x0, y1 - y0)
                if acc + seg >= d:
                    f = (d - acc) / seg
                    bx, by, along = x0 + (x1 - x0) * f, y0 + (y1 - y0) * f, math.atan2(y1 - y0, x1 - x0)
                    break
                acc += seg
            frac = d / total
            side = 1 if k % 2 else -1
            size = 1.0 - 0.4 * frac ** 2                  # smaller towards the long shoot's tip
            m = [(side * rng.uniform(28, 50), size), (side * rng.uniform(62, 96), size * rng.uniform(0.75, 0.92))]
            if rng.random() < 0.45:
                m.append((-side * rng.uniform(8, 30), size * rng.uniform(0.7, 0.88)))
            for ang, sc in m:
                leaves.append((bx, by, along + math.radians(ang), sc, rng.uniform(0.5, 1.0), rng.random()))
            d += spacing * rng.uniform(0.8, 1.25)
            k += 1
        (x0, y0), (x1, y1) = pts[-2], pts[-1]
        leaves.append((x1, y1, math.atan2(y1 - y0, x1 - x0) + rng.uniform(-0.25, 0.25), 0.6, 0.9, rng.random()))

    # the twigs first, then the leaves from back to front (the order they are painted is their depth)
    for pts, w in twigs:
        tw = np.full((n, n), 1e9, np.float32)
        along = np.zeros((n, n), np.float32)
        acc = 0.0
        total = sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(pts, pts[1:]))
        for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
            dx, dy = x1 - x0, y1 - y0
            L2 = dx * dx + dy * dy
            tt = np.clip(((xs - x0) * dx + (ys - y0) * dy) / L2, 0, 1)
            dist = np.hypot(xs - (x0 + tt * dx), ys - (y0 + tt * dy))
            closer = dist < tw
            tw = np.where(closer, dist, tw)
            along = np.where(closer, (acc + tt * math.sqrt(L2)) / total, along)
            acc += math.sqrt(L2)
        radius = 0.0016 * PX * w * (1.0 - 0.6 * along)       # thinner towards the tip
        twig = tw < radius
        cover[twig] = 1.0
        light[twig] = 0.5
    order = sorted(range(len(leaves)), key=lambda j: leaves[j][5])
    for depth, j in enumerate(order):
        bx, by, ang, scale, foreshorten, _ = leaves[j]
        length = rng.uniform(0.034, 0.046) * scale * PX
        stalk = 0.3 * length
        ca, sa = math.cos(ang), math.sin(ang)
        r = int(stalk + length + 4)
        y0, y1 = max(int(by) - r, 0), min(int(by) + r, n)
        x0, x1 = max(int(bx) - r, 0), min(int(bx) + r, n)
        if y0 >= y1 or x0 >= x1:
            continue
        X, Y = xs[y0:y1, x0:x1], ys[y0:y1, x0:x1]
        # the stalk, then the blade beyond it, in leaf coordinates (u along, v across)
        u = (X - bx) * ca + (Y - by) * sa
        v = -(X - bx) * sa + (Y - by) * ca
        stalk_px = (u >= 0) & (u <= stalk) & (np.abs(v) <= 0.0008 * PX)
        t = (u - stalk) / length
        half = leaf_width(np.clip(t, 0, 1)) * length * foreshorten
        blade = (t >= 0) & (t <= 1) & (np.abs(v) <= half)
        here = blade | stalk_px
        lid = 0.06 + 0.94 * ((j * 0.6180339887 + rng.random() * 0.1) % 1.0)
        across = np.where(half > 0, np.abs(v) / np.maximum(half, 1e-3), 1.0)
        rib = np.exp(-(np.abs(v) / (0.012 * length)) ** 2) * (t > 0) * (t < 0.92)
        # calm inside: the spray's value comes from its mass, so its leaves differ only a little (the abstract
        # inner detail of Moss's and Oga's foliage); a faint darkening behind, a faint edge to each leaf
        g = 0.86 + 0.14 * (depth + 1) / len(order)
        g = g * (1.0 - 0.06 * across ** 3) + 0.02 * rib
        sl = (slice(y0, y1), slice(x0, x1))
        leaf_id[sl][here] = lid
        light[sl][here] = np.clip(g, 0, 1)[here]
        thick[sl][blade] = (0.55 + 0.45 * (1.0 - across ** 2))[blade]
        thick[sl][stalk_px] = 0.2
        cover[sl][here] = 1.0
    return leaf_id, light, thick, cover


def leaves(path):
    import random
    atlas = np.zeros((1024, 1024, 4), np.float32)
    for c, kind in enumerate(("spray", "dense", "open", "tip")):
        r = random.Random(f"birch-leaves-{SEED}-{c}")
        lid, light, thick, cover = paint_spray(r, kind)
        # downsample: average the masks under coverage, so edges keep their values; a leaf's id never blurs into
        # another's or the twig's: each texel takes the highest id under it
        cov = downsample(cover, 2)
        w = np.maximum(cov, 1e-4)
        ids = lid.reshape(512, 2, 512, 2).max(axis=(1, 3))
        cell = np.stack([ids, downsample(light * cover, 2) / w, downsample(thick * cover, 2) / w, cov], -1)
        y0, x0 = (c // 2) * 512, (c % 2) * 512
        atlas[y0:y0 + 512, x0:x0 + 512] = cell
    return write_png(path, (np.clip(atlas, 0, 1) * 255 + 0.5).astype(np.uint8))


# -- clumps: the leaves as a painter blocks them -------------------------------------------------------------------------

CLUMP = 1.0          # metres down a spray card (and across its cell; the card itself is half as wide)
CPX = CELL / CLUMP   # pixels per metre while painting


def _leaf(arrs, xs, ys, bx, by, ang, length, fore, lid, g):
    """One birch leaf on its stalk, painted into the masks."""
    leaf_id, light, thick, cover = arrs
    n = xs.shape[0]
    stalk = 0.28 * length
    ca, sa = math.cos(ang), math.sin(ang)
    r = int(stalk + length + 4)
    y0, y1 = max(int(by) - r, 0), min(int(by) + r, n)
    x0, x1 = max(int(bx) - r, 0), min(int(bx) + r, n)
    if y0 >= y1 or x0 >= x1:
        return
    X, Y = xs[y0:y1, x0:x1], ys[y0:y1, x0:x1]
    u = (X - bx) * ca + (Y - by) * sa
    v = -(X - bx) * sa + (Y - by) * ca
    stalk_px = (u >= 0) & (u <= stalk) & (np.abs(v) <= 0.0008 * CPX)
    t = (u - stalk) / length
    half = leaf_width(np.clip(t, 0, 1)) * length * fore
    blade = (t >= 0) & (t <= 1) & (np.abs(v) <= half)
    here = blade | stalk_px
    across = np.where(half > 0, np.abs(v) / np.maximum(half, 1e-3), 1.0)
    rib = np.exp(-(np.abs(v) / (0.012 * length)) ** 2) * (t > 0) * (t < 0.92)
    gg = g * (1.0 - 0.14 * across ** 3) + 0.05 * rib
    sl = (slice(y0, y1), slice(x0, x1))
    leaf_id[sl][here] = lid
    light[sl][here] = np.clip(gg, 0, 1)[here]
    thick[sl][blade] = (0.55 + 0.45 * (1.0 - across ** 2))[blade]
    thick[sl][stalk_px] = 0.2
    cover[sl][here] = 1.0


def paint_clump(rng, kind):
    """One hanging spray in one cell: the twig a birch's foliage hangs from, pendulous from the cell's top centre with
    a few side twigs hanging off it, and the leaves dense along all of them, so the spray is a long, narrow, soft mass
    whose edge is broken only by leaf tips. It keeps to the cell's middle half (the card is half as wide as it is long).
    Lit from above, a little darker beneath; the leaves at the skin painted last."""
    n = CELL
    ys, xs = np.mgrid[0:n, 0:n].astype(np.float32)
    arrs = [np.zeros((n, n), np.float32) for _ in range(4)]
    length = {"tassel": 0.8, "long": 0.86, "fan": 0.7, "short": 0.54}[kind]
    sides = {"tassel": 3, "long": 2, "fan": 5, "short": 2}[kind]
    # the main twig: down from the top centre, swaying a little
    main = _twig(rng, n * 0.5, n * 0.02, math.pi / 2 + rng.uniform(-0.12, 0.12), n * length, rng.uniform(-0.5, 0.5), 18)
    twigs = [(main, 1.0)]
    for k in range(sides):
        t = 0.18 + 0.6 * (k + rng.uniform(0, 0.7)) / sides
        i = int(t * (len(main) - 1))
        (x0, y0), (x1, y1) = main[i], main[i + 1]
        along = math.atan2(y1 - y0, x1 - x0)
        side = 1 if k % 2 else -1
        a = along + side * math.radians(rng.uniform(18, 40) if kind != "fan" else rng.uniform(30, 55))
        L = n * length * rng.uniform(0.3, 0.5) * (1.0 - 0.4 * t)
        twigs.append((_twig(rng, x0, y0, a, L, -side * rng.uniform(0.1, 0.4), 10), 0.7))
    # where the leaves are: a chain of masses along every twig, fattest a little below the top, thinning to the tip
    blobs = []
    for pts, w in twigs:
        for j, (x, y) in enumerate(pts[1:], 1):
            f = j / (len(pts) - 1)
            r = n * 0.085 * w * (0.55 + 0.45 * math.sin(math.pi * min(f * 1.15, 1.0))) * rng.uniform(0.85, 1.15)
            blobs.append((x, y, r))
    m = np.full((n, n), -1e9, np.float32)
    for cx, cy, r in blobs:
        m = np.maximum(m, 1.0 - np.hypot(xs - cx, ys - cy) / r)
    # keep to the middle half of the cell, clear of its foot
    m = np.where((np.abs(xs - n * 0.5) < n * 0.245) & (ys < n * 0.93), m, -1e9)
    inside = m > 0
    ymin, ymax = ys[inside].min(), ys[inside].max()

    def m_at(x, y):
        if abs(x - n * 0.5) >= n * 0.245 or y >= n * 0.93:
            return -1e9
        return max(1.0 - math.hypot(x - cx, y - cy) / r for cx, cy, r in blobs)

    count = {"tassel": 900, "long": 820, "fan": 980, "short": 520}[kind]
    leaves = []
    tries = 0
    while len(leaves) < count and tries < count * 60:
        tries += 1
        x, y = rng.uniform(n * 0.25, n * 0.75), rng.uniform(0, n)
        mm = m_at(x, y)
        if mm < -0.04:
            continue
        # birch leaves on a hanging spray point down and out, a little each way
        ang = math.pi / 2 + rng.gauss(0, 0.7)
        leaves.append((x, y, ang, mm, rng.random()))
    dist = np.full((n, n), 1e9, np.float32)
    for pts, w in twigs:
        for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
            dx, dy = x1 - x0, y1 - y0
            L2 = dx * dx + dy * dy
            tt = np.clip(((xs - x0) * dx + (ys - y0) * dy) / L2, 0, 1)
            dist = np.minimum(dist, np.hypot(xs - (x0 + tt * dx), ys - (y0 + tt * dy)))
    twig = dist < 0.0018 * CPX
    arrs[3][twig] = 1.0
    arrs[1][twig] = 0.45
    for x, y, ang, mm, rr in sorted(leaves, key=lambda l: -l[3] + 0.08 * l[4]):
        t = (y - ymin) / max(ymax - ymin, 1.0)
        g = (1.0 - 0.14 * t) * (0.86 + 0.14 * (1.0 - max(mm, 0.0))) * rng.uniform(0.88, 1.05)
        length_ = rng.uniform(0.038, 0.054) * CPX
        back = 0.64 * length_
        _leaf(arrs, xs, ys, x - math.cos(ang) * back, y - math.sin(ang) * back, ang, length_, rng.uniform(0.55, 1.0),
              0.06 + 0.94 * rng.random(), g)
    return arrs


def clumps(path):
    import random
    atlas = np.zeros((1024, 1024, 4), np.float32)
    for c, kind in enumerate(("tassel", "long", "fan", "short")):
        r = random.Random(f"birch-clumps-{SEED}-{c}")
        lid, light, thick, cover = paint_clump(r, kind)
        cov = downsample(cover, 2)
        w = np.maximum(cov, 1e-4)
        ids = lid.reshape(512, 2, 512, 2).max(axis=(1, 3))
        cell = np.stack([ids, downsample(light * cover, 2) / w, downsample(thick * cover, 2) / w, cov], -1)
        y0, x0 = (c // 2) * 512, (c % 2) * 512
        atlas[y0:y0 + 512, x0:x0 + 512] = cell
    return write_png(path, (np.clip(atlas, 0, 1) * 255 + 0.5).astype(np.uint8))


# -- clusters: a downy birch's sprays --------------------------------------------------------------------------------

CLUSTER = 0.8        # metres across a cluster card's cell (as painted; the card is sized by the assembler)
KPX = CELL / CLUSTER # pixels per metre while painting

# A downy birch's foliage is carried on sprays that go out and up: a twig comes in from inside the crown and rises
# outward, side twigs off it climb on its upper side and spread on its lower, and every tip only nods (a silver
# birch's hang in curtains; that is its own part). Bold flat leaves along them (Firewatch's rule). Each kind: where its
# twig comes in (the anchor, as shares of the cell from its top left; the assembler hangs the card so this point lies
# on the shoot's end and turns it so the painting's right is the way out of the crown), how far the spray reaches out
# and how far it rises (shares of the cell), how many side twigs, and how densely they are leaved (the leaves' spacing
# along a twig, m; and whether each node bears a pair). Dense in a mass's core, sparse at its skin, long and short.
CLUSTERS = {
    "core-long": dict(anchor=(0.12, 0.8), reach=0.8, rise=0.55, twigs=6, spacing=0.034, pairs=True, outward=True),
    "core": dict(anchor=(0.14, 0.78), reach=0.66, rise=0.5, twigs=5, spacing=0.034, pairs=True, outward=True),
    "skin-long": dict(anchor=(0.12, 0.76), reach=0.82, rise=0.45, twigs=4, spacing=0.05, pairs=False, outward=True),
    "skin": dict(anchor=(0.16, 0.74), reach=0.58, rise=0.42, twigs=3, spacing=0.05, pairs=False, outward=True),
}
KINDS = ("core-long", "core", "skin-long", "skin")    # the atlas's cells, in order (the assembler picks by place)


def _nod(pts, depth):
    """The last stretch of a twig turned down a little under its leaves: a nod, never a hang."""
    t = np.linspace(0.0, 1.0, len(pts))
    out = pts.copy()
    out[:, 1] += depth * np.clip((t - 0.7) / 0.3, 0, 1) ** 2
    return out


def _spray(rng, spec, n):
    """A downy birch's spray: the twig comes in at the anchor and rises outward, nodding at its tip; side twigs off it
    in turn, those on its upper side climbing, those on its lower spreading level, each nodding; a few finer ones off
    those. Returns (points in pixels, part) with part "main", "side" or "fine"."""
    A = np.array(spec["anchor"]) * n
    reach, rise = spec["reach"] * n, spec["rise"] * n
    E = A + np.array([reach * rng.uniform(0.9, 1.0), -rise * rng.uniform(0.85, 1.0)])
    main = _nod(curve(A, A + np.array([0.35 * (E[0] - A[0]), 0.75 * (E[1] - A[1])]), E, 24), 0.05 * n)
    out = [(main, "main")]
    k = spec["twigs"]
    for j in range(k):
        t = 0.2 + 0.7 * (j + rng.uniform(0.0, 0.7)) / k
        i = min(int(t * (len(main) - 1)), len(main) - 2)
        P = main[i]
        tan = math.atan2(main[i + 1][1] - P[1], main[i + 1][0] - P[0])
        upper = j % 2 == 0
        a = tan - math.radians(rng.uniform(30, 50)) if upper else tan + math.radians(rng.uniform(25, 45))
        L = reach * rng.uniform(0.3, 0.5) * (1.0 - 0.35 * t)
        Q = P + L * np.array([math.cos(a), math.sin(a)])
        side = _nod(curve(P, (P + Q) / 2 + np.array([0.0, -0.04 * L if upper else 0.02 * L]), Q, 12), 0.03 * n)
        out.append((side, "side"))
        for _ in range(rng.randint(0, 2)):
            u = rng.uniform(0.35, 0.75)
            m = int(u * (len(side) - 2))
            tan2 = math.atan2(side[m + 1][1] - side[m][1], side[m + 1][0] - side[m][0])
            a2 = tan2 + rng.choice((-1, 1)) * math.radians(rng.uniform(25, 45))
            R = side[m] + 0.45 * L * (1 - u) * np.array([math.cos(a2), math.sin(a2)])
            out.append((_nod(curve(side[m], (side[m] + R) / 2, R, 8), 0.015 * n), "fine"))
    return out


def paint_cluster(rng, kind):
    """One spray in one cell: the foliage of one shoot, as a downy birch carries it, rising out of the crown. Its twig
    comes in at the anchor, where the drawn twig ends, bare for a little so the spray is seen to grow from it; bold
    birch leaves (Firewatch's rule: a stylised leaf, larger than life at 8 to 10 cm, flat, crisp) hang from their
    stalks along every twig, densely in a core spray and sparsely in a skin spray, so it is an open spray of distinct
    leaves, never a closed shape and never a fine noise. Its own light is a small modulation of the crown's: lit along
    the spray's upper edge where the sky reaches, one mid value below, a soft shade at its underside, each leaf one
    value. Returns (id, light, thick, cover) supersampled, and the twigs."""
    n = CELL
    spec = CLUSTERS[kind]
    ys, xs = np.mgrid[0:n, 0:n].astype(np.float32)
    twigs = _spray(rng, spec, n)
    strokes = []                                       # (x, y, angle, length, fore)
    for pts, part in twigs:
        seg = np.linalg.norm(np.diff(pts, axis=0), axis=1)
        acc = np.concatenate([[0.0], np.cumsum(seg)])
        Lt = acc[-1]
        d = (0.07 * n if part == "main" else 0.01 * KPX) + rng.uniform(0, 0.01) * KPX
        side = 1
        sp = spec["spacing"] * (1.3 if part == "fine" else 1.0)
        while d < Lt:
            i = min(int(np.searchsorted(acc, d)) - 1, len(pts) - 2)
            f = (d - acc[i]) / max(seg[i], 1e-6)
            p = pts[i] + (pts[i + 1] - pts[i]) * f
            tan = math.atan2(pts[i + 1][1] - pts[i][1], pts[i + 1][0] - pts[i][0])
            for sd in ((side, -side) if spec["pairs"] and rng.random() < 0.6 else (side,)):
                a = tan + sd * math.radians(rng.uniform(30, 65))
                vx, vy = math.cos(a), math.sin(a) + 0.8               # leaves hang a little from their stalks
                strokes.append((p[0], p[1], math.atan2(vy, vx) + rng.gauss(0, 0.25),
                                rng.uniform(0.08, 0.105) * KPX * (1 - 0.2 * d / Lt), rng.uniform(0.7, 1.0)))
            side = -side
            d += sp * KPX * rng.uniform(0.75, 1.25)
    # each leaf's place in the spray, top to bottom, within its own column: the upper edge lit, the underside shaded
    xs_ = np.array([st[0] for st in strokes])
    ys_ = np.array([st[1] for st in strokes])
    bins = np.clip((xs_ / (0.08 * n)).astype(int), 0, 12)
    rel = np.zeros(len(strokes))
    for b_ in set(bins.tolist()):
        m = bins == b_
        top, bot = ys_[m].min(), ys_[m].max()
        rel[m] = (ys_[m] - top) / max(bot - top, 0.05 * n)

    def value(r):
        if r < 0.25 + rng.uniform(-0.06, 0.06):
            return 1.0
        return 0.82 * (1.0 - 0.16 * float(np.clip((r - 0.55) / 0.45, 0, 1)))

    leaf_id = np.zeros((n, n), np.float32)
    light = np.zeros((n, n), np.float32)
    thick = np.zeros((n, n), np.float32)
    cover = np.zeros((n, n), np.float32)
    tw = twig_cover(xs, ys, twigs, (0.0030, 0.0020, 0.0014), KPX)
    bare = tw > 0.5
    light[bare], thick[bare], cover[bare] = 0.45, 0.2, 1.0
    # painted from the bottom up, so the upper leaves overlap the lower like shingles
    for j in sorted(range(len(strokes)), key=lambda q: -strokes[q][1]):
        x, y, a, l, fo = strokes[j]
        px = leaf_px(xs, ys, x, y, a, l, fo)
        if not px:
            continue
        sl, m = px
        leaf_id[sl][m] = 0.06 + 0.94 * rng.random()
        light[sl][m] = value(rel[j]) + rng.uniform(-0.02, 0.02)
        thick[sl][m] = 0.75
        cover[sl][m] = 1.0
    return (leaf_id, light, thick, cover), twigs


def paint_bare(rng, twigs):
    """The spray's twigs bare, the winter crown's haze: the same twigs and finer ones off them, going out and up, so
    a bare downy birch is a soft tone with an ascending grain (Stalenhag's birches), each spray the drawn twig's own
    ends."""
    n = CELL
    ys, xs = np.mgrid[0:n, 0:n].astype(np.float32)
    fine = []
    for pts, part in twigs:
        for t in np.arange(0.25, 0.95, 0.14 if part == "main" else 0.22):
            i = int(t * (len(pts) - 2))
            tan = pts[i + 1] - pts[i]
            a = math.atan2(tan[1], tan[0]) - rng.uniform(0.0, 1.0) * math.radians(40)
            L = rng.uniform(0.03, 0.06) * KPX
            q = pts[i] + L * np.array([math.cos(a), math.sin(a)])
            fine.append((np.array([pts[i], (pts[i] + q) / 2, q]), "fine"))
    return twig_cover(xs, ys, twigs + fine, (0.0030, 0.0018, 0.0011), KPX)


def clusters(path, twig_path):
    """The downy birch's spray atlas (birch_clusters.png) and its bare twigs on the same cells (birch_twigs.png)."""
    return atlas(path, twig_path, KINDS, paint_cluster, paint_bare, "birch-sprays", SEED)


# -- the bark's marks --------------------------------------------------------------------------------------------------

MARK_KINDS = ("slash", "slash", "slash", "slash", "broken", "broken", "dashes", "dashes", "dashes", "hook", "hook",
              "scar", "scar", "chevron", "chevron", "tiny")      # the atlas's sixteen cells, 4 by 4, in order


def _slash(xs, yu, cx, cy, length, thick, curve, tilt, edge, n):
    """A pointed slash centred on (cx, cy), widest a third along, curving by curve, tilted: its signed distance (cell
    units, negative inside) and how far up it each point lies within it (0 at its lower edge, 1 at its upper)."""
    x0 = xs - cx
    y0 = yu - cy - tilt * x0
    t = np.clip(x0 / length + 0.5, 0, 1)
    inside = (x0 / length > -0.5) & (x0 / length < 0.5)
    half = thick * 0.5 * np.maximum(np.sin(np.pi * t ** 0.8), 0.0) ** 0.9
    mid = curve * np.sin(np.pi * t)
    y = y0 - mid
    d = np.abs(y) - half + 0.004 * edge
    d = np.where(inside, d, 1.0)
    up = np.clip(0.5 + y / np.maximum(2 * half, 1e-4), 0, 1)
    return d, up, half, mid, t


def _shape_cell(kind, rng):
    """One mark in one cell (u across the wood, up the image as up the wood): coverage, lightness (0 the mark's darkest,
    1 its lightest) and relief, supersampled. As a birch carries them and Firewatch draws them: a tear in the outer bark,
    many small, a few large, some broken, some with the torn lip curled up above them; each its own shape. The assembler
    places them (tree.py, mark_mesh): the large ones where the tree shed a branch, chevrons over living ones, the rest
    the bark's own lenticels, seeded."""
    n = CELL
    ys, xs = np.mgrid[0:n, 0:n].astype(np.float32) / n
    yu = 1.0 - ys
    edge = value_noise((n, n), (12, 12), np.random.default_rng(rng.randrange(1 << 30))) - 0.5
    cover = np.zeros((n, n), np.float32)
    light = np.zeros((n, n), np.float32)
    height = np.full((n, n), 0.5, np.float32)
    dark = rng.uniform(0.0, 0.18)                            # each mark its own depth of dark

    def paint_slash(cx, cy, length, thick, curve, tilt, lip):
        nonlocal cover, light, height
        d, up, half, mid, t = _slash(xs, yu, cx, cy, length, thick, curve, tilt, edge, n)
        tear = np.clip(0.5 - d * n / 2.0, 0, 1)
        cover = np.maximum(cover, tear)
        # the dark under the torn skin: darkest just under the lip, where it shades the opening
        light = np.where(tear > 0.5, dark + 0.2 * (1.0 - up), light)
        height = np.where(tear > 0.5, 0.12, height)
        if lip:
            # the outer bark torn and curled up along the upper edge: lighter, raised, catching the light
            lip_w = thick * 0.5 * np.maximum(np.sin(np.pi * t), 0.0) ** 0.6 * (1.0 + 0.6 * edge)
            y = yu - cy - tilt * (xs - cx) - mid
            dl = np.abs(y - (half + lip_w * 0.6)) - lip_w * 0.6
            lipm = np.clip(0.5 - dl * n / 2.0, 0, 1) * (np.abs((xs - cx) / length) < 0.5) * (1.0 - tear)
            cover = np.maximum(cover, lipm)
            light = np.where(lipm > 0.5, 1.0, light)
            height = np.where(lipm > 0.5, 0.9, height)

    tilt = rng.uniform(-0.12, 0.12)
    if kind == "slash":
        paint_slash(0.5, 0.5, rng.uniform(0.6, 0.94), rng.uniform(0.07, 0.15), rng.uniform(-0.04, 0.06), tilt,
                    rng.random() < 0.9)
    elif kind == "broken":
        # a slash broken where the bark bridged it: two or three pieces along one line
        k = rng.randint(2, 3)
        span = rng.uniform(0.7, 0.94)
        for j in range(k):
            ln = span / k * rng.uniform(0.6, 0.9)
            cx = 0.5 - span / 2 + span * (j + 0.5) / k
            paint_slash(cx, 0.5 + tilt * (cx - 0.5), ln, rng.uniform(0.05, 0.1), rng.uniform(-0.02, 0.03), tilt,
                        rng.random() < 0.4)
    elif kind == "dashes":
        # a row of small lenticels close together
        k = rng.randint(2, 4)
        for j in range(k):
            cx = rng.uniform(0.15, 0.85)
            paint_slash(cx, 0.5 + rng.uniform(-0.1, 0.1), rng.uniform(0.12, 0.3), rng.uniform(0.03, 0.06),
                        0.0, rng.uniform(-0.1, 0.1), False)
    elif kind == "hook":
        paint_slash(0.47, 0.5, rng.uniform(0.6, 0.82), rng.uniform(0.07, 0.12), 0.03, tilt, rng.random() < 0.6)
        sgn = rng.choice((-1, 1))
        hx = 0.47 + sgn * 0.33
        paint_slash(hx + sgn * 0.04, 0.5 - 0.06, 0.16, 0.06, 0.0, sgn * 0.9, False)
    elif kind == "scar":
        # an old scar, wide, its lower edge ragged where the bark broke, a crack or two across it
        d, up, half, mid, t = _slash(xs, yu, 0.5, 0.5, rng.uniform(0.75, 0.95), rng.uniform(0.16, 0.24), 0.02, tilt,
                                     edge * 3.0, n)
        tear = np.clip(0.5 - d * n / 3.0, 0, 1)
        cover = np.maximum(cover, tear)
        cracks = (np.abs(np.sin((yu + 0.05 * edge) * 60.0)) < 0.16)
        light = np.where(tear > 0.5, np.where(cracks, 0.3, dark), light)
        height = np.where(tear > 0.5, 0.15, height)
    elif kind == "chevron":
        # a living branch's chevron: two arms from a point over the branch, sloping down and out, tapering to points
        x = xs - 0.5
        arm = np.abs(x)
        slope = rng.uniform(0.4, 0.7)
        # a wedge: thick over the branch, its arms tapering to points down either side (the bark wrinkled over the
        # collar), never a thin V
        line = 0.66 - slope * arm + 0.02 * edge
        width = rng.uniform(0.16, 0.22) * np.clip(1.0 - arm / 0.46, 0, 1) ** 1.3 + 0.006
        d = np.maximum(yu - line, line - width - yu)
        cv = np.clip(0.5 - d * n / 2.0, 0, 1) * (arm < 0.46 * rng.uniform(0.8, 1.0))
        cover = np.maximum(cover, cv)
        light = np.where(cv > 0.5, dark + 0.08, light)
        height = np.where(cv > 0.5, 0.3, height)
    else:
        paint_slash(0.5, 0.5, rng.uniform(0.25, 0.4), rng.uniform(0.04, 0.07), 0.0, tilt, False)
    return cover.astype(np.float32), light.astype(np.float32), height.astype(np.float32)


def marks(path):
    """The bark marks atlas (birch_marks.png, 4 by 4 cells, MARK_KINDS): R one, G the mark's lightness (0 the dark
    under the bark, 1 the torn lip), B its relief (the lip raised, the tear sunk), A coverage."""
    import random
    out = np.zeros((1024, 1024, 4), np.float32)
    for c, kind in enumerate(MARK_KINDS):
        cover, light, height = _shape_cell(kind, random.Random(f"birch-marks-{SEED}-{c}"))
        cov = cover.reshape(256, 4, 256, 4).mean(axis=(1, 3))
        w = np.maximum(cov, 1e-4)
        cell = np.stack([np.ones_like(cov), (light * cover).reshape(256, 4, 256, 4).mean(axis=(1, 3)) / w,
                         (height * cover).reshape(256, 4, 256, 4).mean(axis=(1, 3)) / w, cov], -1)
        y0, x0 = (c // 4) * 256, (c % 4) * 256
        out[y0:y0 + 256, x0:x0 + 256] = cell
    return write_png(path, (np.clip(out, 0, 1) * 255 + 0.5).astype(np.uint8))


# -- bark -------------------------------------------------------------------------------------------------------------

def value_noise(shape, cells, rng):
    """Tiling value noise: a random grid of cells, smoothly interpolated, wrapping at the edges."""
    h, w = shape
    gy, gx = cells
    g = rng.random((gy, gx)).astype(np.float32)
    y = np.linspace(0, gy, h, endpoint=False)
    x = np.linspace(0, gx, w, endpoint=False)
    y0, x0 = np.floor(y).astype(int), np.floor(x).astype(int)
    fy, fx = y - y0, x - x0
    fy, fx = fy * fy * (3 - 2 * fy), fx * fx * (3 - 2 * fx)
    a = g[y0 % gy][:, x0 % gx]
    b = g[y0 % gy][:, (x0 + 1) % gx]
    c = g[(y0 + 1) % gy][:, x0 % gx]
    d = g[(y0 + 1) % gy][:, (x0 + 1) % gx]
    return (a * (1 - fx) + b * fx) * (1 - fy[:, None]) + (c * (1 - fx) + d * fx) * fy[:, None]


def bark(path, kind="downy"):
    """The bark tile. The downy birch's: a grey white mottled with lichen (B: where it grows), rougher, its rings
    faint. The silver birch's: a clean white with soft rings round the stem, no lichen to speak of."""
    downy = kind == "downy"
    rng = np.random.default_rng(SEED + 1)
    H, W = 1024, 512                       # v along (0.6 m), u round (0.3 m)
    # lightness: white with soft grey bands running round the stem, and a faint mottle
    bands = value_noise((H, W), (40, 3), rng) * 0.6 + value_noise((H, W), (90, 6), rng) * 0.4
    mottle = value_noise((H, W), (24, 12), rng)
    # calm (Firewatch's trunks): a pale ground with soft bands, the detail rationed to the lenticels
    light = 0.80 + (0.06 if downy else 0.14) * (bands - 0.5) + (0.12 if downy else 0.05) * (mottle - 0.5)
    # lenticels: short dark dashes across the stem, a few hundred per tile
    lent = np.zeros((H, W), np.float32)
    ys, xs = np.mgrid[0:H, 0:W].astype(np.float32)
    for _ in range(30):
        cy, cx = rng.uniform(0, H), rng.uniform(0, W)
        L, T = rng.uniform(22, 70), rng.uniform(1.4, 2.8)
        dy = (ys - cy + H / 2) % H - H / 2
        dx = (xs - cx + W / 2) % W - W / 2
        lent = np.maximum(lent, np.clip(1.0 - (np.abs(dx) / L) ** 2 - (dy / T) ** 2, 0, 1) ** 0.6)
    # the relief (nothing is flat): the outer bark in thin horizontal rings that catch the light, peeling a little at
    # their edges, a faint grain running along the stem, the lenticels sunk into it; the shader bends the light by it
    ring_v = value_noise((H, W), (70, 2), rng)
    rings = np.abs(np.sin((ys / H * 26.0 + 1.5 * ring_v) * np.pi)) ** 3      # ridges, irregularly spaced
    grain = value_noise((H, W), (6, 9), rng) - 0.5                         # faint, broad: never stripes that repeat
    # lichen: patches of several sizes, their edges broken (the downy birch's, on this damp coast)
    lich = (value_noise((H, W), (5, 3), rng) * 0.55 + value_noise((H, W), (14, 7), rng) * 0.3
            + value_noise((H, W), (40, 20), rng) * 0.15)
    lichen = np.zeros_like(light)          # lichen is the shader's, from noise round the trunk (a tile repeats it)
    height = (0.5 + (0.12 if downy else 0.22) * (rings - 0.3) + (0.1 if downy else 0.04) * grain - 0.35 * lent
              + 0.12 * lichen)
    img = np.stack([np.clip(light, 0, 1), np.clip(lent, 0, 1), lichen, np.clip(height, 0, 1)], -1)
    return write_png(path, (img * 255 + 0.5).astype(np.uint8))


if __name__ == "__main__":
    unity = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", "..", "..", "..", "unity")
    out = os.path.join(unity, "Assets", "Art", "Trees", "birch")
    print(leaves(os.path.join(out, "birch_leaves.png")))
    print(clumps(os.path.join(out, "birch_clumps.png")))
    print(clusters(os.path.join(out, "birch_clusters.png"), os.path.join(out, "birch_twigs.png")))
    print(marks(os.path.join(out, "birch_marks.png")))
    print(bark(os.path.join(out, "birch_bark.png")))
