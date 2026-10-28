"""What the finishing scripts share: the project's hash as numpy lattices, smooth seeded noise, and float image I/O
through Blender (numpy has no image codecs here). Arrays are (rows, cols) with row 0 at the image's bottom, as
Blender and Unity both sample them: axis 0 is v, axis 1 is u."""

import os
import sys

import bpy
import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "blender", "resolver"))
import hashing as HS  # noqa: E402

U64 = np.uint64


def _mix(z):
    with np.errstate(over="ignore"):
        z = z + U64(HS.GAMMA)
        z = (z ^ (z >> U64(30))) * U64(0xBF58476D1CE4E5B9)
        z = (z ^ (z >> U64(27))) * U64(0x94D049BB133111EB)
    return z ^ (z >> U64(31))


def unit(key, *idx):
    """HS.unit(HS.h(key, *idx)) over integer arrays: the same numbers the scalar spec gives."""
    shape = np.broadcast(*[np.asarray(a) for a in idx]).shape if idx else ()
    acc = np.full(shape, key, dtype=U64)
    for a in idx:
        acc = _mix(acc ^ np.asarray(a, dtype=np.int64).astype(U64))
    return (acc >> U64(11)).astype(np.float64) / float(1 << 53)


def _s(t):
    return t * t * (3.0 - 2.0 * t)


def noise2(u, v, key, period=None):
    """Smooth value noise in [0, 1] at lattice coordinates (u, v); `period` (pu, pv) wraps the lattice so a
    tileable repeats without a seam."""
    i0, j0 = np.floor(u).astype(np.int64), np.floor(v).astype(np.int64)
    fu, fv = _s(u - i0), _s(v - j0)

    def L(i, j):
        if period is not None:
            i, j = i % period[0], j % period[1]
        return unit(key, i, j)
    a, b = L(i0, j0), L(i0 + 1, j0)
    c, d = L(i0, j0 + 1), L(i0 + 1, j0 + 1)
    return (a + (b - a) * fu) + ((c + (d - c) * fu) - (a + (b - a) * fu)) * fv


def noise3(x, y, z, key):
    i0, j0, k0 = (np.floor(t).astype(np.int64) for t in (x, y, z))
    fx, fy, fz = _s(x - i0), _s(y - j0), _s(z - k0)
    out = 0.0
    for di in (0, 1):
        wx = fx if di else 1 - fx
        for dj in (0, 1):
            wy = fy if dj else 1 - fy
            for dk in (0, 1):
                wz = fz if dk else 1 - fz
                out = out + wx * wy * wz * unit(key, i0 + di, j0 + dj, k0 + dk)
    return out


def fbm2(u, v, key, cells, octaves=3, gain=0.5, period=True):
    """Fractal value noise over a tile of `cells` (cu, cv) lattice cells, each octave twice as fine; [0, 1]."""
    total, amp, norm = 0.0, 1.0, 0.0
    for o in range(octaves):
        cu, cv = cells[0] * 2 ** o, cells[1] * 2 ** o
        total = total + amp * noise2(u * cu, v * cv, HS.h(key, o), (cu, cv) if period else None)
        norm += amp
        amp *= gain
    return total / norm


def fbm3(p, key, cell, octaves=3, gain=0.5):
    total, amp, norm = 0.0, 1.0, 0.0
    for o in range(octaves):
        s = cell / 2 ** o
        total = total + amp * noise3(p[..., 0] / s, p[..., 1] / s, p[..., 2] / s, HS.h(key, o))
        norm += amp
        amp *= gain
    return total / norm


def smoothstep(a, b, x):
    t = np.clip((x - a) / (b - a), 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)


def equalise(a, mask=None):
    """Rank-map a field to a uniform [0, 1]: a threshold t then covers the share 1 - t of it."""
    flat = a[mask] if mask is not None else a.ravel()
    order = np.argsort(flat, kind="stable")
    ranks = np.empty_like(order)
    ranks[order] = np.arange(order.size)
    out = np.zeros_like(a, dtype=np.float64)
    vals = ranks / max(order.size - 1, 1)
    if mask is not None:
        out[mask] = vals
    else:
        out = vals.reshape(a.shape)
    return out


def blur(a, radius, mask=None, axis=None):
    """Box blur repeated three times (near Gaussian), periodic; with a mask, a normalised blur inside it."""
    def box(x, r, ax):
        if r < 1:
            return x
        c = np.cumsum(np.concatenate([x.take(range(-r - 1, 0), axis=ax), x, x.take(range(0, r), axis=ax)], axis=ax),
                      axis=ax)
        n = x.shape[ax]
        hi = c.take(range(2 * r + 1, 2 * r + 1 + n), axis=ax)
        lo = c.take(range(0, n), axis=ax)
        return (hi - lo) / (2 * r + 1)
    axes = (0, 1) if axis is None else (axis,)
    if mask is None:
        out = a.astype(np.float64)
        for _ in range(3):
            for ax in axes:
                out = box(out, radius, ax)
        return out
    m = mask.astype(np.float64)
    num, den = a * m, m
    for _ in range(3):
        for ax in axes:
            num, den = box(num, radius, ax), box(den, radius, ax)
    return np.where(den > 1e-6, num / np.maximum(den, 1e-6), a)


def dilate(a, mask, steps):
    """Spread the covered texels outward `steps` times into the charts' pads (mean of covered neighbours)."""
    a = a.copy()
    m = mask.copy()
    for _ in range(steps):
        acc = np.zeros_like(a)
        cnt = np.zeros(m.shape)
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)):
            sm = np.roll(np.roll(m, dy, 0), dx, 1)
            sa = np.roll(np.roll(a, dy, 0), dx, 1)
            acc += sa * (sm[..., None] if a.ndim == 3 else sm)
            cnt += sm
        grow = (~m) & (cnt > 0)
        fill = acc / np.maximum(cnt, 1)[..., None] if a.ndim == 3 else acc / np.maximum(cnt, 1)
        a[grow] = fill[grow]
        m = m | grow
    return a


def normal_from_height(h, metres_per_px, wrap=True):
    """Tangent-space normal (OpenGL, +v up) from a height field in metres; 0..1 encoded RGB."""
    if wrap:
        du = (np.roll(h, -1, 1) - np.roll(h, 1, 1)) / (2 * metres_per_px)
        dv = (np.roll(h, -1, 0) - np.roll(h, 1, 0)) / (2 * metres_per_px)
    else:
        du = np.gradient(h, metres_per_px, axis=1)
        dv = np.gradient(h, metres_per_px, axis=0)
    n = np.stack([-du, -dv, np.ones_like(h)], axis=-1)
    n /= np.linalg.norm(n, axis=-1, keepdims=True)
    return n * 0.5 + 0.5


def trim_strips(ts):
    """Where each strip starts across the trim sheet, metres: the flat strips (near) in the first half, the
    bevelled ones (street) in the second, each after a pad. The texture maker reads the same layout."""
    pad = ts["padMm"] * 0.001
    out = {}
    for level, base in (("near", 0.0), ("street", ts["metres"] / 2)):
        v, starts = base + pad, []
        for w in ts["stripsMm"]:
            starts.append(v)
            v += w * 0.001 + pad
        out[level] = starts
    return out

def trim_bevels(vm, ts):
    """The trim sheet's street half: across v (metres), each strip's edges fall at 45 degrees over its member's
    chamfer. Returns the bevel's height (metres, <= 0) and how far into the bevel each texel is (0..1, the arris 1).
    The pads hold the nearer strip's edge height, so no cliff sits beside a strip."""
    bevel = np.zeros_like(vm)
    wear = np.zeros_like(vm)
    starts = trim_strips(ts)["street"]
    edges = []
    for s, w in zip(starts, (w * 0.001 for w in ts["stripsMm"])):
        b = ts["bevelMm"][str(round(w / 0.001))] * 0.001
        d = np.minimum(vm - s, s + w - vm)
        inside = (vm >= s) & (vm <= s + w)
        bevel = np.where(inside, -np.maximum(0.0, b - d), bevel)
        wear = np.where(inside, np.clip(1.0 - d / b, 0.0, 1.0), wear)
        edges.append((s, s + w, -b))
    half = vm >= ts["metres"] / 2
    for i, (lo, hi, hb) in enumerate(edges):
        nxt = edges[i + 1][0] if i + 1 < len(edges) else ts["metres"]
        mid = (hi + nxt) / 2
        bevel = np.where(half & (vm > hi) & (vm <= mid), hb, bevel)
        if i + 1 < len(edges):
            bevel = np.where(half & (vm > mid) & (vm < nxt), edges[i + 1][2], bevel)
    bevel = np.where(half & (vm < edges[0][0]), edges[0][2], bevel)
    return bevel, wear


def pack_normal(n, gloss=None):
    """A tile's second map: R, G the tangent normal's x, y (OpenGL, z rebuilt in the shader), B a smoothness offset
    (0.5 none, +-0.5 the full range), A 1. `n` is a unit (h, w, 3) normal."""
    g = np.full(n.shape[:2], 0.5) if gloss is None else np.clip(0.5 + gloss, 0, 1)
    return np.stack([n[..., 0] * 0.5 + 0.5, n[..., 1] * 0.5 + 0.5, g, np.ones(n.shape[:2])], axis=-1)


def blend_normals(base, detail):
    """Whiteout blend of two unit normals (h, w, 3)."""
    n = np.stack([base[..., 0] + detail[..., 0], base[..., 1] + detail[..., 1], base[..., 2] * detail[..., 2]], -1)
    return n / np.linalg.norm(n, axis=-1, keepdims=True)


def read(path):
    im = bpy.data.images.load(path)
    w, h = im.size
    px = np.empty(w * h * 4, np.float32)
    im.pixels.foreach_get(px)
    bpy.data.images.remove(im)
    return px.reshape(h, w, 4).astype(np.float64)


def write(path, rgba, colour=False):
    """Write an (h, w, 3|4) array in [0, 1] as an 8-bit PNG; Non-Color unless `colour`."""
    h, w = rgba.shape[:2]
    out = np.ones((h, w, 4), np.float32)
    out[..., :rgba.shape[2]] = np.clip(rgba, 0.0, 1.0)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    im = bpy.data.images.new(os.path.basename(path), w, h, alpha=True)
    im.colorspace_settings.name = "sRGB" if colour else "Non-Color"
    im.pixels.foreach_set(out.ravel())
    im.filepath_raw = path
    im.file_format = "PNG"
    im.save()
    bpy.data.images.remove(im)
