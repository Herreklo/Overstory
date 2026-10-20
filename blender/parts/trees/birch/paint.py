"""The downy birch's painted parts: its leaf sprays and its bark, as mask textures the tree shader colours.

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

Clusters (birch_clusters.png, the atlas the tree's cards carry, four cells): the foliage as the birch carries it, in
drapes (a twig arching over, fine twigs falling from it, bold flat leaves along them), dense in a mass's core and
sparse at its skin, long and short (CLUSTERS; the assembler reads each cell's anchor from there). The same channels as
the leaves; G is the drape's own light (lit along the arch, one mid value below, shading softly to the tips). Its bare
twigs (birch_twigs.png, the same cells; A coverage): the drape's twigs and finer ones off them, the winter crown's
haze, shown as each card's leaves fall.

Bark (birch_bark.png, 512 by 1024, tiling; u round the stem, v along it, one tile 0.3 m round and 0.6 m along):
- R: the bark's lightness, white with soft grey bands;
- G: lenticels (the short dark horizontal dashes) and the dark scars under branches;
- B: the fissured foot (black cracked plates), which the shader shows on old trunks near the ground;
- A: one.

Painted with numpy on a supersampled grid, deterministic from fixed seeds, so the same file comes out every time.
"""

import math
import os
import struct
import sys
import zlib

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
SEED = 1989


def write_png(path, rgba):
    """rgba: uint8 array (h, w, 4)."""
    h, w, _ = rgba.shape
    raw = b"".join(b"\x00" + rgba[y].tobytes() for y in range(h))

    def chunk(tag, data):
        c = struct.pack(">I", len(data)) + tag + data
        return c + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    png = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 6, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b"")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        f.write(png)
    return path


def downsample(a, k):
    h, w = a.shape[:2]
    return a.reshape(h // k, k, w // k, k, *a.shape[2:]).mean(axis=(1, 3))


# -- leaves -------------------------------------------------------------------------------------------------------------

CELL = 1024          # supersampled cell (written at 512)
CARD = 0.42          # metres across a card
PX = CELL / CARD     # pixels per metre while painting


def leaf_width(t):
    """Half-width of a downy birch leaf along its length (t 0 at the stalk, 1 at the tip), as a share of its length:
    rounded at the base, widest about a third along, tapering to a point, with coarse double teeth."""
    t = np.clip(t, 0, 1)
    base = np.maximum(np.sin(np.pi * t ** 0.72), 0.0) ** 0.85 * (1.0 - 0.32 * t)
    teeth = 0.045 * np.abs(np.sin(t * np.pi * 9.0)) + 0.02 * np.abs(np.sin(t * np.pi * 18.0 + 0.7))
    return 0.37 * base * (1.0 - teeth * (t > 0.08))


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


# -- clusters: a twig's foliage as a drape ----------------------------------------------------------------------------

CLUSTER = 0.8        # metres across a cluster card's cell (as painted; the card is sized by the assembler)
KPX = CELL / CLUSTER # pixels per metre while painting

# A birch's foliage hangs in drapes: a twig arcs in and droops, and from it a few fine twigs hang, small leaves
# scattered along them, so the drape is a soft veil, open between its strands, with no cap and no closed outline (a
# closed shape repeated round a crown reads as one big leaf, or a jellyfish). Each kind: where its twig comes in (the
# anchor, as shares of the cell from its top left; the assembler hangs the card so this point lies on the shoot's
# end and turns it so the drape falls out from the crown), its width and length (shares of the cell), how many twigs
# hang from it, and how densely they are leaved (the leaves' spacing along a twig, m; and whether each node bears a
# pair). The core of a mass is dense drapes; its skin sparse ones, long and short.
CLUSTERS = {
    "core-long": dict(anchor=(0.2, 0.22), width=0.72, length=0.95, twigs=6, spacing=0.034, pairs=True, hang=True),
    "core": dict(anchor=(0.2, 0.24), width=0.74, length=0.78, twigs=6, spacing=0.034, pairs=True, hang=True),
    "skin-long": dict(anchor=(0.24, 0.22), width=0.6, length=0.92, twigs=4, spacing=0.05, pairs=False, hang=True),
    "skin": dict(anchor=(0.24, 0.24), width=0.62, length=0.68, twigs=3, spacing=0.05, pairs=False, hang=True),
}
KINDS = ("core-long", "core", "skin-long", "skin")    # the atlas's cells, in order (the assembler picks by place)


def _curve(p0, p1, p2, n):
    t = np.linspace(0.0, 1.0, n)[:, None]
    return (1 - t) ** 2 * p0 + 2 * (1 - t) * t * p1 + t ** 2 * p2


def _drape(rng, spec, n):
    """A drape's twigs: the twig comes in at the anchor, rises and arches over and down, as a birch's branchlet does;
    fine twigs fall from points along the arch (and from its end), so the drape's top is the arch's curve, never a
    straight rod; each falls its own length, swaying and splaying a little, with a few finer ones off it. Returns
    (points in pixels, part) with part "main", "hang" or "fine"."""
    A = np.array(spec["anchor"]) * n
    W, L = spec["width"] * n, spec["length"] * n
    top = A[1] - rng.uniform(0.13, 0.17) * n                         # the arch's crown, above the anchor
    E = np.array([A[0] + W * rng.uniform(0.8, 0.95), A[1] + rng.uniform(0.15, 0.3) * L])
    main = _curve(A, np.array([A[0] + 0.35 * (E[0] - A[0]), 2 * top - (A[1] + E[1]) / 2]), E, 24)
    out = [(main, "main")]
    k = spec["twigs"]
    for j in range(k):
        t = 0.2 + 0.8 * (j + rng.uniform(0.0, 0.8)) / k
        P = main[min(int(t * (len(main) - 1)), len(main) - 1)]
        bottom = A[1] + L - 0.2 * n
        length = max(bottom - P[1], 0.1 * n) * rng.uniform(0.4, 1.0)
        sway = rng.uniform(-0.1, 0.16) * W
        Q = np.array([P[0] + sway, P[1] + length])
        # leaving the arch outward a little before it falls
        pts = _curve(P, np.array([P[0] + rng.uniform(0.02, 0.08) * W, P[1] + 0.25 * length]), Q, 16)
        out.append((pts, "hang"))
        for _ in range(rng.randint(1, 3)):
            u = rng.uniform(0.2, 0.7)
            q = pts[int(u * (len(pts) - 1))]
            sd = rng.choice((-1, 1))
            R = q + np.array([sd * rng.uniform(0.04, 0.09) * n, rng.uniform(0.05, 0.13) * n])
            out.append((_curve(q, np.array([(q[0] + R[0]) / 2 + sd * 0.015 * n, q[1] + 0.005 * n]), R, 8), "fine"))
    return out


def _leaf_px(xs, ys, bx, by, ang, length, fore):
    """The pixels of one bold birch leaf on its stalk (its blade and stalk masks, and its bounds)."""
    n = xs.shape[0]
    stalk = 0.22 * length
    r = int(stalk + length + 4)
    y0, y1 = max(int(by) - r, 0), min(int(by) + r, n)
    x0, x1 = max(int(bx) - r, 0), min(int(bx) + r, n)
    if y0 >= y1 or x0 >= x1:
        return None
    X, Y = xs[y0:y1, x0:x1], ys[y0:y1, x0:x1]
    ca, sa = math.cos(ang), math.sin(ang)
    u = (X - bx) * ca + (Y - by) * sa
    v = -(X - bx) * sa + (Y - by) * ca
    t = (u - stalk) / length
    half = leaf_width(np.clip(t, 0, 1)) * length * fore * 1.15
    blade = (t >= 0) & (t <= 1) & (np.abs(v) <= half)
    return (slice(y0, y1), slice(x0, x1)), blade


def paint_cluster(rng, kind):
    """One drape in one cell: the foliage of one twig, as a birch carries it. Its twig arcs in at the top from the
    anchor, where the drawn twig ends; bold birch leaves (Firewatch's rule: a stylised leaf, larger than life at 8 to
    10 cm, flat, crisp) hang along every fine twig, densely in a core drape and sparsely in a skin drape, so it is a
    veil of distinct leaves, never a closed shape and never a fine noise. Its own light is
    a small modulation of the crown's: lit along the top where the sky reaches, one mid value down the strands, and a
    soft shade towards their tips, each leaf one value. Returns (id, light, thick, cover) supersampled, and the twigs."""
    n = CELL
    spec = CLUSTERS[kind]
    ys, xs = np.mgrid[0:n, 0:n].astype(np.float32)
    twigs = _drape(rng, spec, n)
    A = np.array(spec["anchor"]) * n
    L = spec["length"] * n
    strokes = []                                       # (x, y, angle, length, fore)
    for pts, part in twigs:
        seg = np.linalg.norm(np.diff(pts, axis=0), axis=1)
        acc = np.concatenate([[0.0], np.cumsum(seg)])
        Lt = acc[-1]
        # the arc where the twig comes in stays bare for a little: the drape is seen to hang from it
        d = (0.08 * n if part == "main" else 0.01 * KPX) + rng.uniform(0, 0.01) * KPX
        side = 1
        sp = spec["spacing"] * (1.3 if part == "fine" else 1.0)
        while d < Lt:
            i = min(int(np.searchsorted(acc, d)) - 1, len(pts) - 2)
            f = (d - acc[i]) / max(seg[i], 1e-6)
            p = pts[i] + (pts[i + 1] - pts[i]) * f
            tan = math.atan2(pts[i + 1][1] - pts[i][1], pts[i + 1][0] - pts[i][0])
            for sd in ((side, -side) if spec["pairs"] and rng.random() < 0.6 else (side,)):
                a = tan + sd * math.radians(rng.uniform(30, 65))
                vx, vy = math.cos(a), math.sin(a) + 1.2               # leaves hang from their stalks
                strokes.append((p[0], p[1], math.atan2(vy, vx) + rng.gauss(0, 0.25),
                                rng.uniform(0.08, 0.105) * KPX * (1 - 0.2 * d / Lt), rng.uniform(0.7, 1.0)))
            side = -side
            d += sp * KPX * rng.uniform(0.75, 1.25)

    arch = min(p[1] for pts, part in twigs if part == "main" for p in pts)

    def value(y):
        r = (y - arch) / L
        if r < 0.18 + rng.uniform(-0.05, 0.05):
            return 1.0                                  # lit along the arch, where the sky reaches
        return 0.82 * (1.0 - 0.16 * float(np.clip((r - 0.45) / 0.5, 0, 1)))  # mid, shading softly to the tips

    # painted from the bottom up, so the upper leaves overlap the lower like shingles
    leaf_id = np.zeros((n, n), np.float32)
    light = np.zeros((n, n), np.float32)
    thick = np.zeros((n, n), np.float32)
    cover = np.zeros((n, n), np.float32)
    tw = _twig_cover(xs, ys, twigs, (0.0030, 0.0020, 0.0014))
    bare = tw > 0.5
    light[bare], thick[bare], cover[bare] = 0.45, 0.2, 1.0
    for x, y, a, l, fo in sorted(strokes, key=lambda st: -st[1]):
        px = _leaf_px(xs, ys, x, y, a, l, fo)
        if not px:
            continue
        sl, m = px
        leaf_id[sl][m] = 0.06 + 0.94 * rng.random()
        light[sl][m] = value(y) + rng.uniform(-0.02, 0.02)
        thick[sl][m] = 0.75
        cover[sl][m] = 1.0
    return (leaf_id, light, thick, cover), twigs


def _twig_cover(xs, ys, twigs, widths):
    """The spray's twigs as coverage, each order at its width (m) at its foot, thinning to its tip."""
    cover = np.zeros(xs.shape, np.float32)
    for pts, part in twigs:
        order = 0 if part == "main" else 2 if part == "fine" else 1     # the twig, its side twigs and tips, fine
        w0 = widths[min(order, len(widths) - 1)] * KPX
        m = len(pts)
        for i, (p0, p1) in enumerate(zip(pts, pts[1:])):
            _line(cover, xs, ys, [tuple(p0), tuple(p1)], max(w0 * (1.0 - 0.55 * i / m), 1.4))
    return cover


def paint_fan(rng, twigs):
    """The cluster's twigs bare, as the winter crown's haze: the same fan from the anchor, and finer twigs off every
    twig, so a bare crown is a soft tone with an ascending grain (Stalenhag's birches), each fan visibly the drawn
    twig's own ends."""
    n = CELL
    ys, xs = np.mgrid[0:n, 0:n].astype(np.float32)
    fine = []
    for pts, part in twigs:
        for t in np.arange(0.25, 0.95, 0.12 if part == "main" else 0.2):
            i = int(t * (len(pts) - 2))
            tan = pts[i + 1] - pts[i]
            a = math.atan2(tan[1], tan[0]) + rng.choice((-1, 1)) * math.radians(rng.uniform(25, 45))
            L = rng.uniform(0.03, 0.06) * KPX
            q = pts[i] + L * np.array([math.cos(a), math.sin(a) + 0.6])            # hanging twigs
            fine.append((np.array([pts[i], (pts[i] + q) / 2 + np.array([0, 0.15 * L]), q]), "fine"))
    return _twig_cover(xs, ys, twigs + fine, (0.0032, 0.0020, 0.0012))


def clusters(path, twig_path):
    """The cluster atlas (birch_clusters.png) and its bare twigs on the same cells (birch_twigs.png)."""
    import random
    atlas = np.zeros((1024, 1024, 4), np.float32)
    bare = np.zeros((1024, 1024, 4), np.float32)
    for c, kind in enumerate(KINDS):
        r = random.Random(f"birch-clusters-{SEED}-{c}")
        (lid, light, thick, cover), twigs_ = paint_cluster(r, kind)
        cov = downsample(cover, 2)
        w = np.maximum(cov, 1e-4)
        ids = lid.reshape(512, 2, 512, 2).max(axis=(1, 3))
        cell = np.stack([ids, downsample(light * cover, 2) / w, downsample(thick * cover, 2) / w, cov], -1)
        y0, x0 = (c // 2) * 512, (c % 2) * 512
        atlas[y0:y0 + 512, x0:x0 + 512] = cell
        tc = downsample(paint_fan(r, twigs_), 2)
        bare[y0:y0 + 512, x0:x0 + 512] = np.stack([np.zeros_like(tc), np.full_like(tc, 0.8), np.zeros_like(tc), tc], -1)
    write_png(twig_path, (np.clip(bare, 0, 1) * 255 + 0.5).astype(np.uint8))
    return write_png(path, (np.clip(atlas, 0, 1) * 255 + 0.5).astype(np.uint8))


def _line(cover, xs, ys, pts, width):
    """Paint a polyline of the given width (pixels) into the coverage, antialiased by distance."""
    n = cover.shape[0]
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        r = int(width + 3)
        ya, yb = max(int(min(y0, y1)) - r, 0), min(int(max(y0, y1)) + r, n)
        xa, xb = max(int(min(x0, x1)) - r, 0), min(int(max(x0, x1)) + r, n)
        if ya >= yb or xa >= xb:
            continue
        X, Y = xs[ya:yb, xa:xb], ys[ya:yb, xa:xb]
        dx, dy = x1 - x0, y1 - y0
        L2 = dx * dx + dy * dy + 1e-6
        t = np.clip(((X - x0) * dx + (Y - y0) * dy) / L2, 0, 1)
        d = np.hypot(X - (x0 + t * dx), Y - (y0 + t * dy))
        cov = np.clip(width / 2 + 0.5 - d, 0, 1)
        cover[ya:yb, xa:xb] = np.maximum(cover[ya:yb, xa:xb], cov)


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


def bark(path):
    rng = np.random.default_rng(SEED + 1)
    H, W = 1024, 512                       # v along (0.6 m), u round (0.3 m)
    # lightness: white with soft grey bands running round the stem, and a faint mottle
    bands = value_noise((H, W), (40, 3), rng) * 0.6 + value_noise((H, W), (90, 6), rng) * 0.4
    mottle = value_noise((H, W), (24, 12), rng)
    light = 0.78 + 0.16 * (bands - 0.5) * 2 * 0.5 + 0.08 * (mottle - 0.5)
    # lenticels: short dark dashes across the stem, a few hundred per tile
    lent = np.zeros((H, W), np.float32)
    ys, xs = np.mgrid[0:H, 0:W].astype(np.float32)
    for _ in range(120):
        cy, cx = rng.uniform(0, H), rng.uniform(0, W)
        L, T = rng.uniform(16, 60), rng.uniform(1.0, 2.2)
        dy = (ys - cy + H / 2) % H - H / 2
        dx = (xs - cx + W / 2) % W - W / 2
        lent = np.maximum(lent, np.clip(1.0 - (np.abs(dx) / L) ** 2 - (dy / T) ** 2, 0, 1) ** 0.6)
    # the foot: deep fissures running along the stem, wandering, between cracked plates
    wander = (value_noise((H, W), (5, 4), rng) - 0.5) * 70.0
    xw = (xs + wander) % W
    cells = 7
    ridge = np.abs(((xw / W) * cells) % 1.0 - 0.5) * 2.0                  # 1 at a fissure, 0 mid-plate
    width = 0.75 + 0.2 * value_noise((H, W), (16, 7), rng)
    fiss = np.clip((ridge - width) / (1.0 - width), 0, 1) ** 0.7
    breaks = value_noise((H, W), (26, 7), rng)
    across = np.clip(1.0 - np.abs(breaks - 0.5) * 14.0, 0, 1) * (ridge < width)   # plates cracked across now and then
    rough = value_noise((H, W), (60, 40), rng)
    foot = np.clip(np.maximum(fiss, across * 0.8) + 0.25 * (rough - 0.5), 0, 1)
    img = np.stack([np.clip(light, 0, 1), np.clip(lent, 0, 1), foot, np.ones_like(light)], -1)
    return write_png(path, (img * 255 + 0.5).astype(np.uint8))


if __name__ == "__main__":
    unity = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", "..", "..", "..", "unity")
    out = os.path.join(unity, "Assets", "Art", "Trees", "birch")
    print(leaves(os.path.join(out, "birch_leaves.png")))
    print(clumps(os.path.join(out, "birch_clumps.png")))
    print(clusters(os.path.join(out, "birch_clusters.png"), os.path.join(out, "birch_twigs.png")))
    print(bark(os.path.join(out, "birch_bark.png")))
