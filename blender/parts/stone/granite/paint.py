"""The setts' rock, painted at our scale (docs/stone.md; the board, docs/references/stone/02, 13, 14): a hard, dark,
crystalline rock (the lanes' setts: gneiss and granite brought in, docs/research/stone.md), its own identity beside
the slate (Øystein: elements share systems, never looks): a fine even speckle of mineral grains a millimetre or two
across, dark and pale in salt and pepper, here and there a faint gneissic banding; its worn top smoothed so the grains
read as a soft speckle, its sides rough. One tile a metre across, seamless, read by the stone shader in each sett's
own plane at its own offset and turn.

    granite_grain.png (2048 px, about half a millimetre a pixel):
    R  a worn top's lightness about 0.5: the speckle softened by wear, a faint banding
    G  its relief: almost none, the worn crystals flush
    B  a hewn side's lightness: the speckle sharp, the pick's marks in short strokes
    A  the side's relief: the grains standing, the strokes

The rock's pigment, weathering and everything that reads as history are the shader's and the facts', never painted
here. Numpy only; deterministic from the seed.

    python blender/parts/stone/granite/paint.py [unity project dir]
"""

import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "slate"))
sys.path.insert(0, os.path.join(HERE, "..", "..", "trees"))
from paint import N, band  # noqa: E402
from painting import write_png  # noqa: E402

SEED = 1910


def grains(rng, size_px, share):
    """A field of mineral grains a few pixels across: 1 on the dark (or pale) grains, 0 between."""
    g = band(rng, N / (size_px * 4.0), N / (size_px * 1.2), beta=0.0)
    th = np.quantile(g, 1.0 - share)
    return np.clip((g - th) / 0.35, 0.0, 1.0)


def build(unity):
    rng = np.random.default_rng(SEED)
    dark = grains(rng, 3.0, 0.32)          # hornblende and biotite: dark, a millimetre or two
    pale = grains(rng, 4.0, 0.22)          # feldspar: paler, a little larger
    banding = band(rng, 2.0, 6.0, beta=1.0, aniso=(1.0, 6.0))     # a faint gneissic banding, along x
    mottle = band(rng, 3.0, 14.0, beta=1.2)
    # the worn top: the crystals flush and softened, a soft speckle and a faint banding
    soft_dark = band(rng, N / 16.0, N / 5.0, beta=0.0)
    top = 0.5 + 0.10 * (pale - dark) * 0.7 + 0.03 * banding + 0.03 * mottle + 0.02 * soft_dark
    top_rel = 0.5 + 0.02 * band(rng, 8.0, 60.0, beta=1.0)
    # the hewn side: the speckle sharp, the pick's strokes short and slanting
    strokes = band(rng, 30.0, 120.0, beta=0.5, aniso=(4.0, 1.0))
    side = 0.5 + 0.16 * (pale - dark) + 0.04 * strokes + 0.03 * mottle
    side_rel = 0.5 + 0.12 * strokes + 0.08 * (pale - dark)
    rgba = np.stack([np.clip(c, 0, 1) for c in (top, top_rel, side, side_rel)], -1)
    path = os.path.join(unity, "Assets", "Art", "Stone", "granite_grain.png")
    write_png(path, (rgba * 255).astype(np.uint8))
    print("GRAIN", path, [round(float(rgba[..., k].std()), 3) for k in range(4)])


if __name__ == "__main__":
    unity = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", "..", "..", "..", "unity")
    build(unity)
