"""The slaty rock's grain, painted at our scale (docs/stone.md, Texture and detail; the board, docs/references/stone/
02, 03, 06): one tile a metre across, seamless, read by the stone shader in each piece's own plane at its own offset
and turn, so no two stones repeat.

    slate_grain.png (2048 px, about half a millimetre a pixel):
    R  a bedding plane's lightness about 0.5: a smooth cleavage face in two or three soft values, a few long ridges
       along the bedding, the odd pale quartz vein
    G  its relief (0.5 the plane): the ridges raised, a soft mottle, the slightest tooth
    B  a split face's lightness: the rock broken across its bedding in plates a centimetre or three thick, each its
       own tone, a parting where one stands proud of the next
    A  the split face's relief: each plate standing in or out, the break rough across

The stone's pigment, its weathering and everything that reads as history are the shader's and the facts', never
painted here. Numpy only; deterministic from the seed.

    python blender/parts/stone/slate/paint.py [unity project dir]
"""

import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "trees"))
from painting import write_png  # noqa: E402

N = 2048
SEED = 1874


def band(rng, lo, hi, beta=1.0, aniso=(1.0, 1.0)):
    """Seamless noise with its power between lo and hi cycles a tile, falling as 1/f^beta; aniso stretches it (a
    larger x squeezes features across x, so they run along it). Unit spread."""
    fx = np.fft.fftfreq(N) * N
    FX, FY = np.meshgrid(fx, fx, indexing="xy")
    f = np.sqrt((FX * aniso[0]) ** 2 + (FY * aniso[1]) ** 2)
    win = np.exp(-((np.log(np.maximum(f, 1e-6)) - math.log(math.sqrt(lo * hi))) / (0.5 * math.log(hi / lo) + 0.4)) ** 2)
    amp = win / np.maximum(f, 1.0) ** beta
    amp[0, 0] = 0.0
    spec = (rng.standard_normal((N, N)) + 1j * rng.standard_normal((N, N))) * amp
    out = np.real(np.fft.ifft2(spec))
    return (out - out.mean()) / max(out.std(), 1e-9)


def soft_lines(rng, n, width_px, length=(0.15, 0.6), curve=0.08):
    """n thin wandering lines (quartz veins), seamless (drawn on the torus): a field 0 to 1."""
    yy, xx = np.mgrid[0:N, 0:N].astype(np.float32)
    out = np.zeros((N, N), np.float32)
    for _ in range(n):
        x0, y0 = rng.uniform(0, N), rng.uniform(0, N)
        ang = rng.uniform(0, math.pi)
        L = rng.uniform(*length) * N
        bend = rng.uniform(-curve, curve)
        w = width_px * rng.uniform(0.6, 1.6)
        # distance to a gently bent segment, on the torus
        for dx in (-N, 0, N):
            for dy in (-N, 0, N):
                px = xx - (x0 + dx)
                py = yy - (y0 + dy)
                u = px * math.cos(ang) + py * math.sin(ang)
                v = -px * math.sin(ang) + py * math.cos(ang) - bend * (u ** 2) / max(L, 1)
                inside = (u > 0) & (u < L)
                taper = np.clip(np.minimum(u, L - u) / (0.15 * L), 0, 1)
                d = np.abs(v) / (w * np.maximum(taper, 0.05))
                out = np.maximum(out, np.where(inside, np.clip(1.0 - d, 0, 1) * taper, 0.0))
    return out


def paint(path):
    rng = np.random.default_rng(SEED)
    # -- a bedding plane: a smooth cleavage face in two or three values, a few long ridges along the bedding, the
    # odd pale vein; no fine speckle (it read as granite) --
    broad = band(rng, 1.0, 4.0, 0.6)                     # values a quarter to a metre across
    mottle = band(rng, 4.0, 14.0, 0.8)                   # a soft mottle of a few centimetres
    # two or three values: the broad field stepped softly, so a slab carries planes of tone, not a cloud
    v = 0.7 * broad + 0.3 * mottle
    steps = np.tanh(2.2 * v) / np.tanh(2.2)
    ridge_f = band(rng, 6.0, 40.0, 0.5, aniso=(1.0, 0.08))        # long ridges along the bedding (x)
    ridges = np.clip((np.abs(ridge_f) - 1.6) / 0.5, 0, 1)
    fine = band(rng, 120.0, 400.0, 0.3)                  # the slightest tooth, for the light, barely in the tone
    L = 0.5 + 0.09 * steps + 0.03 * mottle - 0.04 * ridges + 0.012 * fine
    veins = soft_lines(np.random.default_rng(SEED + 1), 4, 2.5)
    L += 0.14 * veins
    R = 0.5 + 0.18 * ridges + 0.08 * mottle + 0.06 * fine
    # -- a split face: the rock broken across its bedding, stepping in plates a centimetre or three thick, each
    # standing in or out, a few thin partings between; never a fine even grain (it read as wood) --
    vv_ = np.arange(N)[:, None] / N
    warp = 0.0015 * band(rng, 2.0, 8.0, 0.8)
    vv = (vv_ + warp) % 1.0
    lrng = np.random.default_rng(SEED + 2)
    edges = [0.0]
    while edges[-1] < 1.0:
        edges.append(edges[-1] + lrng.uniform(0.008, 0.03))
    edges = np.array(edges) / edges[-1]
    tones = lrng.normal(0.0, 1.0, len(edges))
    stands = lrng.normal(0.0, 1.0, len(edges))
    idx = np.clip(np.searchsorted(edges, vv) - 1, 0, len(edges) - 2)
    within = (vv - edges[idx]) / np.maximum(edges[idx + 1] - edges[idx], 1e-6)
    # a parting only where a plate's edge stands proud of the next (not every boundary)
    proud = (stands[idx] - stands[np.clip(idx + 1, 0, len(stands) - 1)]) > 0.6
    seam = np.exp(-((1.0 - within) / 0.06) ** 2) * proud
    # the broken face itself: rough across, in plates (a hackly break), not smooth
    hack = band(rng, 30.0, 150.0, 0.5, aniso=(0.4, 1.0))
    E = 0.5 + 0.06 * tones[idx] + 0.04 * hack + 0.03 * mottle - 0.14 * seam
    A = 0.5 + 0.2 * stands[idx] - 0.25 * seam + 0.12 * hack
    rgba = np.stack([L, R, E, A], -1)
    return write_png(path, (np.clip(rgba, 0, 1) * 255 + 0.5).astype(np.uint8))


if __name__ == "__main__":
    unity = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", "..", "..", "..", "unity")
    print(paint(os.path.join(unity, "Assets", "Art", "Stone", "slate_grain.png")))
