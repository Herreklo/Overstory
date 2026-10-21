"""The slaty rock's grain, painted at our scale (docs/stone.md, Texture and detail; the board, docs/references/stone/
02, 03, 06): one tile a metre across, seamless, read by the stone shader in each piece's own plane at its own offset
and turn, so no two stones repeat.

    slate_grain.png (2048 px, about half a millimetre a pixel):
    R  a bedding plane's lightness about 0.5: broad blotches, a mottle, faint streaks along the bedding, the rock's
       flecks (pale mica, dark grains), a few quartz veins, pits
    G  its relief (0.5 the plane): the flecks and pits sunk or raised, the streaks as faint ridges
    B  a split face's lightness: its laminae, thin layers each its own tone, wavering, with the same flecks
    A  the split face's relief: each layer standing a little in or out

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
    # -- a bedding plane --
    broad = band(rng, 1.0, 4.0, 0.6)                     # blotches a quarter to a metre across
    mottle = band(rng, 6.0, 30.0, 0.6)                   # a mottle of a few centimetres
    streak = band(rng, 15.0, 120.0, 0.4, aniso=(1.0, 0.12))    # faint streaks along the bedding (x)
    grain = band(rng, 150.0, 700.0, 0.2)                 # the rock's own grain, a millimetre or two
    L = 0.5 + 0.055 * broad + 0.06 * mottle + 0.035 * streak + 0.05 * grain
    # flecks: pale mica and dark grains, a few in a hundred, a pixel or two across
    fl = band(rng, 400.0, 1000.0, 0.0)
    pale = np.clip((fl - 2.2) / 0.6, 0, 1)
    dark = np.clip((-fl - 2.3) / 0.6, 0, 1)
    L += 0.16 * pale - 0.18 * dark
    # a few quartz veins, pale and thin
    veins = soft_lines(np.random.default_rng(SEED + 1), 5, 3.0)
    L += 0.2 * veins
    # pits: small dark hollows where a grain fell out
    pit_f = band(rng, 120.0, 300.0, 0.0)
    pits = np.clip((pit_f - 2.6) / 0.4, 0, 1)
    L -= 0.15 * pits
    R = 0.5 + 0.18 * grain + 0.12 * mottle + 0.12 * streak + 0.1 * pale - 0.25 * pits - 0.05 * dark
    R = 0.5 + (R - 0.5) * 0.9
    # -- a split face: laminae along x, layers each its own tone, wavering --
    v = np.arange(N)[:, None] / N                        # up the face (rows)
    warp = 0.0022 * band(rng, 2.0, 10.0, 0.8) + 0.0008 * band(rng, 20.0, 60.0, 0.5)
    vv = (v + warp) % 1.0
    # the layers: random thicknesses 1.5 to 7 mm, each a tone and a standing in or out
    lrng = np.random.default_rng(SEED + 2)
    edges = [0.0]
    while edges[-1] < 1.0:
        edges.append(edges[-1] + lrng.uniform(0.0015, 0.007))
    edges = np.array(edges) / edges[-1]
    tones = lrng.normal(0.0, 1.0, len(edges))
    stands = lrng.normal(0.0, 1.0, len(edges))
    idx = np.clip(np.searchsorted(edges, vv) - 1, 0, len(edges) - 2)
    within = (vv - edges[idx]) / np.maximum(edges[idx + 1] - edges[idx], 1e-6)
    seam = np.exp(-((np.minimum(within, 1.0 - within)) / 0.12) ** 2)        # a dark fine line between layers
    E = 0.5 + 0.07 * tones[idx] + 0.035 * mottle + 0.04 * grain - 0.12 * seam + 0.1 * pale - 0.12 * dark
    A = 0.5 + 0.16 * stands[idx] - 0.2 * seam + 0.1 * grain
    rgba = np.stack([L, R, E, A], -1)
    return write_png(path, (np.clip(rgba, 0, 1) * 255 + 0.5).astype(np.uint8))


if __name__ == "__main__":
    unity = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", "..", "..", "..", "unity")
    print(paint(os.path.join(unity, "Assets", "Art", "Stone", "slate_grain.png")))
