"""The painting tools every tree's parts share, so all of them are painted by one hand: a PNG writer, the
supersampled grid, curves, a birch leaf's outline and its rasteriser, antialiased lines, a cluster's twigs as
coverage, and the cluster atlas with its bare twigs. Numpy only; deterministic.
"""

import math
import os
import struct
import zlib

import numpy as np

CELL = 1024          # a supersampled atlas cell (written at 512)


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


# -- shapes ------------------------------------------------------------------------------------------------------------

def curve(p0, p1, p2, n):
    """A quadratic Bezier from p0 through the pull of p1 to p2, n points."""
    t = np.linspace(0.0, 1.0, n)[:, None]
    return (1 - t) ** 2 * p0 + 2 * (1 - t) * t * p1 + t ** 2 * p2


def leaf_width(t):
    """Half-width of a downy birch leaf along its length (t 0 at the stalk, 1 at the tip), as a share of its length:
    rounded at the base, widest about a third along, tapering to a point, with coarse double teeth."""
    t = np.clip(t, 0, 1)
    base = np.maximum(np.sin(np.pi * t ** 0.72), 0.0) ** 0.85 * (1.0 - 0.32 * t)
    teeth = 0.045 * np.abs(np.sin(t * np.pi * 9.0)) + 0.02 * np.abs(np.sin(t * np.pi * 18.0 + 0.7))
    return 0.37 * base * (1.0 - teeth * (t > 0.08))


def leaf_px(xs, ys, bx, by, ang, length, fore):
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


def line(cover, xs, ys, pts, width):
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



def twig_cover(xs, ys, twigs, widths, px_per_m):
    """A cluster's twigs as coverage, each order at its width (m) at its foot, thinning to its tip."""
    cover = np.zeros(xs.shape, np.float32)
    for pts, part in twigs:
        order = 0 if part == "main" else 2 if part == "fine" else 1     # the twig, its side twigs and tips, fine
        w0 = widths[min(order, len(widths) - 1)] * px_per_m
        m = len(pts)
        for i, (p0, p1) in enumerate(zip(pts, pts[1:])):
            line(cover, xs, ys, [tuple(p0), tuple(p1)], max(w0 * (1.0 - 0.55 * i / m), 1.4))
    return cover


def atlas(path, twig_path, kinds, paint_one, paint_bare, tag, seed):
    """A cluster atlas (2 by 2 cells, each painted at CELL and written at half) and its bare twigs on the same cells.
    paint_one(rng, kind) returns ((id, light, thick, cover), twigs); paint_bare(rng, twigs) the bare twigs' coverage.
    Channels: R each leaf's id (0 the twig), G light within the cluster, B thickness, A coverage; the twigs' A only.
    Coverage is averaged on the way down and a leaf's id never blurs into another's (each texel takes the highest)."""
    import random
    out = np.zeros((1024, 1024, 4), np.float32)
    bare = np.zeros((1024, 1024, 4), np.float32)
    for c, kind in enumerate(kinds):
        r = random.Random(f"{tag}-{seed}-{c}")
        (lid, light, thick, cover), twigs = paint_one(r, kind)
        cov = downsample(cover, 2)
        w = np.maximum(cov, 1e-4)
        ids = lid.reshape(512, 2, 512, 2).max(axis=(1, 3))
        cell = np.stack([ids, downsample(light * cover, 2) / w, downsample(thick * cover, 2) / w, cov], -1)
        y0, x0 = (c // 2) * 512, (c % 2) * 512
        out[y0:y0 + 512, x0:x0 + 512] = cell
        tc = downsample(paint_bare(r, twigs), 2)
        bare[y0:y0 + 512, x0:x0 + 512] = np.stack([np.zeros_like(tc), np.full_like(tc, 0.8), np.zeros_like(tc), tc], -1)
    write_png(twig_path, (np.clip(bare, 0, 1) * 255 + 0.5).astype(np.uint8))
    return write_png(path, (np.clip(out, 0, 1) * 255 + 0.5).astype(np.uint8))
