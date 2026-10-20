"""The silver birch's painted parts (Betula pendula: the planted garden and park birch, its twigs hanging in long
curtains as it ages): its foliage as drapes, and its bark.

    python blender/parts/trees/silver_birch/paint.py [unity project]      (numpy only; writes PNGs)

Clusters (silver_birch_clusters.png, the atlas the tree's cards carry, four cells): a twig arching over, fine twigs
falling from it, bold flat leaves along them (Firewatch's rule: larger than life, crisp), dense in a mass's core and
sparse at its skin, long and short (CLUSTERS; the assembler reads each cell's anchor from there). Channels as every
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

# A birch's foliage hangs in drapes: a twig arcs in and droops, and from it a few fine twigs hang, small leaves
# scattered along them, so the drape is a soft veil, open between its strands, with no cap and no closed outline (a
# closed shape repeated round a crown reads as one big leaf, or a jellyfish). Each kind: where its twig comes in (the
# anchor, as shares of the cell from its top left; the assembler hangs the card so this point lies on the shoot's
# end and turns it so the drape falls out from the crown), its width and length (shares of the cell), how many twigs
# hang from it, and how densely they are leaved (the leaves' spacing along a twig, m; and whether each node bears a
# pair). The core of a mass is dense drapes; its skin sparse ones, long and short. outward: the painting's right is
# the way out of the crown (the assembler turns the card so).
CLUSTERS = {
    "core-long": dict(anchor=(0.2, 0.22), width=0.72, length=0.95, twigs=6, spacing=0.034, pairs=True, outward=True),
    "core": dict(anchor=(0.2, 0.24), width=0.74, length=0.78, twigs=6, spacing=0.034, pairs=True, outward=True),
    "skin-long": dict(anchor=(0.24, 0.22), width=0.6, length=0.92, twigs=4, spacing=0.05, pairs=False, outward=True),
    "skin": dict(anchor=(0.24, 0.24), width=0.62, length=0.68, twigs=3, spacing=0.05, pairs=False, outward=True),
}
KINDS = ("core-long", "core", "skin-long", "skin")    # the atlas's cells, in order (the assembler picks by place)


def _drape(rng, spec, n):
    """A drape's twigs: the twig comes in at the anchor, rises and arches over and down, as a birch's branchlet does;
    fine twigs fall from points along the arch (and from its end), so the drape's top is the arch's curve, never a
    straight rod; each falls its own length, swaying and splaying a little, with a few finer ones off it. Returns
    (points in pixels, part) with part "main", "hang" or "fine"."""
    A = np.array(spec["anchor"]) * n
    W, L = spec["width"] * n, spec["length"] * n
    top = A[1] - rng.uniform(0.13, 0.17) * n                         # the arch's crown, above the anchor
    E = np.array([A[0] + W * rng.uniform(0.8, 0.95), A[1] + rng.uniform(0.15, 0.3) * L])
    main = curve(A, np.array([A[0] + 0.35 * (E[0] - A[0]), 2 * top - (A[1] + E[1]) / 2]), E, 24)
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
        pts = curve(P, np.array([P[0] + rng.uniform(0.02, 0.08) * W, P[1] + 0.25 * length]), Q, 16)
        out.append((pts, "hang"))
        for _ in range(rng.randint(1, 3)):
            u = rng.uniform(0.2, 0.7)
            q = pts[int(u * (len(pts) - 1))]
            sd = rng.choice((-1, 1))
            R = q + np.array([sd * rng.uniform(0.04, 0.09) * n, rng.uniform(0.05, 0.13) * n])
            out.append((curve(q, np.array([(q[0] + R[0]) / 2 + sd * 0.015 * n, q[1] + 0.005 * n]), R, 8), "fine"))
    return out


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
    return twig_cover(xs, ys, twigs + fine, (0.0032, 0.0020, 0.0012), KPX)


def clusters(path, twig_path):
    # painted with the seeds the birch's drapes were first painted with, so the atlas is the one judged on 21 October
    return atlas(path, twig_path, KINDS, paint_cluster, paint_bare, "birch-clusters", SEED)


def _downy():
    """The downy birch's parts module (its bark and its marks, which the silver birch borrows for now)."""
    spec = importlib.util.spec_from_file_location("paint_birch", os.path.join(HERE, "..", "birch", "paint.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def bark(path):
    """The downy birch's bark, until the silver birch's own is painted (its colour is set apart in its material)."""
    return _downy().bark(path)


def marks(path):
    """The downy birch's marks: a birch's chevrons and scars."""
    return _downy().marks(path)


if __name__ == "__main__":
    unity = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", "..", "..", "..", "unity")
    out = os.path.join(unity, "Assets", "Art", "Trees", "silver_birch")
    print(clusters(os.path.join(out, "silver_birch_clusters.png"), os.path.join(out, "silver_birch_twigs.png")))
    print(marks(os.path.join(out, "silver_birch_marks.png")))
    print(bark(os.path.join(out, "silver_birch_bark.png")))
