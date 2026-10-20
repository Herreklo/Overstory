"""The silver birch's painted parts (Betula pendula: the planted garden and park birch, its twigs hanging in long
curtains as it ages): its foliage as drapes, and its bark.

    python blender/parts/trees/silver_birch/paint.py [unity project]      (numpy only; writes PNGs)

Clusters (silver_birch_clusters.png, the atlas the tree's cards carry, four cells): the downy birch's rising spray for
the upper crown, and strand bundles in three lengths (a short bare twig arc, long fine twigs hanging from it, bold
flat leaves along them; Firewatch's rule: larger than life, crisp) for the arching limbs below (CLUSTERS; the
assembler reads each cell's anchor from there). Channels as every
tree's cluster atlas (blender/parts/trees/painting.py): R each leaf's id, G the drape's own light (lit along the arch,
one mid value below, shading softly to the tips), B thickness, A coverage. Its bare twigs (silver_birch_twigs.png, the
same cells): the drape's twigs and finer hanging ones, the winter crown's haze. The bark is the downy birch's for now
(the silver birch's own, whiter, breaking into black diamonds and a fissured foot, is still to be painted).
"""

import importlib.util
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from painting import CELL, atlas, curve, leaf_px, twig_cover  # noqa: E402

SEED = 1989
CLUSTER = 0.8        # metres across a cluster card's cell (as painted; the card is sized by the assembler)
KPX = CELL / CLUSTER # pixels per metre while painting

# A silver birch's foliage: its leader and upper limbs rise and carry sprays (the downy birch's, borrowed); its outer
# and lower limbs arch over and let their twigs hang in strands. A strand bundle: a short twig arc at the top, bare,
# and from it a few long fine twigs hanging, leaves along them, so the bundle is two or three times longer than wide,
# a veil open between its strands, with no cap; the volume comes from many bundles overlapping along an arching limb.
# Three lengths. Each kind: where its twig comes in (the anchor, as shares of the cell from its top left; the
# assembler hangs the card so this point lies on the shoot's end), the arc's width and the strands' length (shares of
# the cell), how many strands, and how densely they are leaved (the leaves' spacing along a strand, m; and whether a
# node may bear a pair). outward: the painting's right is the way out of the crown (the assembler turns the card so).
CLUSTERS = {
    "spray": None,                                  # the downy birch's core spray (set below)
    "strands-long": dict(anchor=(0.26, 0.14), width=0.5, length=0.86, twigs=4, spacing=0.04, pairs=False, outward=True),
    "strands": dict(anchor=(0.26, 0.15), width=0.48, length=0.68, twigs=4, spacing=0.04, pairs=False, outward=True),
    "strands-short": dict(anchor=(0.26, 0.16), width=0.44, length=0.5, twigs=3, spacing=0.044, pairs=False,
                          outward=True),
}
KINDS = ("spray", "strands-long", "strands", "strands-short")   # the atlas's cells, in order


def _downy():
    """The downy birch's parts module (its sprays and its bark, which the silver birch borrows for now)."""
    spec = importlib.util.spec_from_file_location("paint_birch", os.path.join(HERE, "..", "birch", "paint.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


DOWNY = _downy()
CLUSTERS["spray"] = dict(DOWNY.CLUSTERS["core"])


def _strands(rng, spec, n):
    """A strand bundle's twigs: a short arc from the anchor, rising a little and turning over, and from points along
    it fine twigs hanging, each its own length, swaying a little, a few finer ones off them. Returns (points in pixels,
    part) with part "main", "hang" or "fine"."""
    A = np.array(spec["anchor"]) * n
    W, L = spec["width"] * n, spec["length"] * n
    # the twig rises from the anchor and arches over, so the bundle's top is a curve, never a rod
    E = np.array([A[0] + W * rng.uniform(0.85, 1.0), A[1] + rng.uniform(0.06, 0.12) * n])
    main = curve(A, np.array([A[0] + 0.4 * (E[0] - A[0]), A[1] - rng.uniform(0.12, 0.16) * n]), E, 18)
    out = [(main, "main")]
    k = spec["twigs"]
    for j in range(k):
        t = 0.3 + 0.7 * (j + rng.uniform(0.0, 0.8)) / k
        P = main[min(int(t * (len(main) - 1)), len(main) - 1)]
        # strands of very different lengths, swaying, splaying a little apart
        length = (A[1] + L - P[1]) * rng.uniform(0.35, 1.0)
        Q = np.array([P[0] + rng.uniform(-0.08, 0.12) * W, P[1] + length])
        pts = curve(P, np.array([P[0] + rng.uniform(-0.1, 0.14) * W, P[1] + 0.45 * length]), Q, 18)
        out.append((pts, "hang"))
        for _ in range(rng.randint(0, 2)):
            u = rng.uniform(0.25, 0.7)
            q = pts[int(u * (len(pts) - 1))]
            sd = rng.choice((-1, 1))
            R = q + np.array([sd * rng.uniform(0.03, 0.06) * n, rng.uniform(0.07, 0.14) * n])
            out.append((curve(q, np.array([(q[0] + R[0]) / 2 + sd * 0.012 * n, q[1] + 0.01 * n]), R, 8), "fine"))
    return out


def paint_cluster(rng, kind):
    """One cluster in one cell: on the upper crown the downy birch's rising spray; below, a strand bundle as a silver
    birch carries its foliage: the twig comes in at the anchor, where the drawn twig ends, and arcs over, bare; bold
    birch leaves (Firewatch's rule: larger than life, flat, crisp) hang along the strands falling from it, so it is a
    veil of distinct leaves, longer than wide, never a capped shape and never a fine noise. Its own light is a small
    modulation of the crown's: lit at the top where the sky reaches, one mid value down the strands, a soft shade
    towards their tips, each leaf one value. Returns (id, light, thick, cover) supersampled, and the twigs."""
    if kind == "spray":
        return DOWNY.paint_cluster(rng, "core")
    n = CELL
    spec = CLUSTERS[kind]
    ys, xs = np.mgrid[0:n, 0:n].astype(np.float32)
    twigs = _strands(rng, spec, n)
    A = np.array(spec["anchor"]) * n
    L = spec["length"] * n
    strokes = []                                       # (x, y, angle, length, fore)
    for pts, part in twigs:
        seg = np.linalg.norm(np.diff(pts, axis=0), axis=1)
        acc = np.concatenate([[0.0], np.cumsum(seg)])
        Lt = acc[-1]
        # the arc stays bare (no cap): the leaves are on the strands, the bundle seen to hang from its twig
        if part == "main":
            continue
        # each strand's leaves begin a little way down it, at its own height: a ragged top, never a straight edge
        d = rng.uniform(0.02, 0.12) * Lt + rng.uniform(0, 0.01) * KPX
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
    tw = twig_cover(xs, ys, twigs, (0.0030, 0.0020, 0.0014), KPX)
    bare = tw > 0.5
    light[bare], thick[bare], cover[bare] = 0.45, 0.2, 1.0
    for x, y, a, l, fo in sorted(strokes, key=lambda st: -st[1]):
        px = leaf_px(xs, ys, x, y, a, l, fo)
        if not px:
            continue
        sl, m = px
        leaf_id[sl][m] = 0.06 + 0.94 * rng.random()
        light[sl][m] = value(y) + rng.uniform(-0.02, 0.02)
        thick[sl][m] = 0.75
        cover[sl][m] = 1.0
    return (leaf_id, light, thick, cover), twigs


def paint_bare(rng, twigs):
    """A spray's twigs bare as the downy birch's are; a strand bundle's: the same twigs and finer ones hanging off
    them. The cluster's twigs bare, as the winter crown's haze: the same fan from the anchor, and finer twigs off every
    twig, so a bare crown is a soft tone with an ascending grain (Stalenhag's birches), each fan visibly the drawn
    twig's own ends."""
    if any(part == "side" for _, part in twigs):
        return DOWNY.paint_bare(rng, twigs)
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
    return twig_cover(xs, ys, twigs + fine, (0.0032, 0.0020, 0.0012), KPX)


def clusters(path, twig_path):
    return atlas(path, twig_path, KINDS, paint_cluster, paint_bare, "silver-birch-clusters", SEED)


def bark(path):
    """The downy birch's bark, until the silver birch's own is painted."""
    return DOWNY.bark(path)


if __name__ == "__main__":
    unity = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", "..", "..", "..", "unity")
    out = os.path.join(unity, "Assets", "Art", "Trees", "silver_birch")
    print(clusters(os.path.join(out, "silver_birch_clusters.png"), os.path.join(out, "silver_birch_twigs.png")))
    print(bark(os.path.join(out, "silver_birch_bark.png")))
