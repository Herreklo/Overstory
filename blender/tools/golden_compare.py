"""Golden comparison: every frame of a set against its baseline, by a perceptual difference after NVIDIA's FLIP
(docs/measuring.md, Golden views; docs/research/performance-at-scale.md, Visual regression and checks).

    blender -b --factory-startup --python blender/tools/golden_compare.py -- compare <baseline dir> <test dir> <out dir>
        [--ppd 52.4] [--mean 0.0005] [--worst 0.05] [--sheet-scale 4] [--present 1]
    blender -b --factory-startup --python blender/tools/golden_compare.py -- accept <test dir> <baseline dir>
    blender -b --factory-startup --python blender/tools/golden_compare.py -- selftest <out dir>

`compare` finds every PNG under the baseline, compares it with the same path under the test set, and writes:
- <out>/<path>.flip.png: the per-pixel difference as a heat map (magma, 0 black to 1 pale yellow, FLIP's own scale);
- <out>/<path>.flip10.png: the same amplified ten times, so a change far under the threshold can still be found;
- <out>/sheet-<folder>.png: per frame a strip (baseline, test, heat map, amplified), at a quarter size;
- <out>/report.json and <out>/report.md: per frame the mean, the 99th and 99.9th percentiles and the worst pixel,
  the share of pixels over 0.05, and pass or fail.
It exits 1 when any frame fails: its mean over --mean, its worst pixel over --worst, or the frame missing or resized
(--present 1 compares only the frames the test set has, for a partial render).

`accept` copies a set over the baseline. Only Øystein accepts a baseline (docs/measuring.md): the AI proposes, he
accepts on the sheet. `selftest` checks the metric on made-up images: identical images score zero everywhere, a small
patch of changed colour scores inside the patch and nowhere far from it, and a larger change scores higher.

The metric is an approximation of LDR-FLIP (Andersson et al., "FLIP: A Difference Evaluator for Alternating Images",
HPG 2020; the reference code is github.com/NVlabs/flip), written here in numpy because FLIP is not installed:
- colour: sRGB to linear to YCxCz (an opponent space), each channel filtered by FLIP's contrast sensitivity kernels
  (sums of Gaussians, applied as separable 1-D passes, which is exact for them), back to linear RGB clamped to [0, 1],
  to CIELAB with the Hunt adjustment, the HyAB distance raised to 0.7 and compressed as FLIP does (cmax from green to
  blue, pc 0.4, pt 0.95);
- features: edges and points of the linear luminance by FLIP's Gaussian first and second derivatives (std 0.082
  degrees, positive and negative weights each normalised), their difference scaled by 1/sqrt(2) and raised to 0.5;
- the frame's error per pixel: colour ** (1 - features).
Differences from the reference: edge padding is the same, but the kernels are evaluated separably (identical maths for
these kernels), floats are 64-bit, and nothing here has been checked pixel for pixel against NVIDIA's own tool; until it
is, treat the numbers as FLIP-like, not FLIP. Pixels per degree default to the reference player's screen: a 27-inch
2560 by 1440 monitor (0.597 m wide) seen from 0.7 m, 52.4 (FLIP's own default, 67, is a 4K screen of 0.7 m).
"""

import json
import math
import os
import shutil
import struct
import sys
import zlib

import numpy as np

# -- PNG in and out --------------------------------------------------------------------------------------------------


def read_png(path):
    """An 8-bit PNG as float sRGB values in [0, 1], top row first (h, w, 3). Read through Blender, untransformed."""
    import bpy
    img = bpy.data.images.load(path, check_existing=False)
    try:
        img.colorspace_settings.name = "Non-Color"
        w, h = img.size
        px = np.empty(w * h * 4, np.float32)
        img.pixels.foreach_get(px)
    finally:
        bpy.data.images.remove(img)
    rgb = px.reshape(h, w, 4)[::-1, :, :3].astype(np.float64)
    return np.round(rgb * 255.0) / 255.0


def write_png(path, rgb):
    """(h, w, 3) floats in [0, 1] or uint8, top row first, as an 8-bit RGB PNG."""
    if rgb.dtype != np.uint8:
        rgb = np.clip(np.round(rgb * 255.0), 0, 255).astype(np.uint8)
    h, w, _ = rgb.shape
    raw = np.zeros((h, 1 + w * 3), np.uint8)
    raw[:, 1:] = rgb.reshape(h, w * 3)

    def chunk(t, d):
        return struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t + d) & 0xFFFFFFFF)

    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "wb") as fh:
        fh.write(b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0))
                 + chunk(b"IDAT", zlib.compress(raw.tobytes(), 6)) + chunk(b"IEND", b""))


def shrink(rgb, k):
    """1/k size, each pixel the mean of a k by k block (for sheets only)."""
    h, w = rgb.shape[0] // k * k, rgb.shape[1] // k * k
    return rgb[:h, :w].reshape(h // k, k, w // k, k, -1).mean(axis=(1, 3))


# -- FLIP, approximated ----------------------------------------------------------------------------------------------

RGB2XYZ = np.array([[10135552 / 24577794, 8788810 / 24577794, 4435075 / 24577794],
                    [2613072 / 12288897, 8788810 / 12288897, 887015 / 12288897],
                    [1425312 / 73733382, 8788810 / 73733382, 70074185 / 73733382]])
XYZ2RGB = np.linalg.inv(RGB2XYZ)
WHITE = RGB2XYZ @ np.ones(3)          # D65, Y = 1
QC, QF, PC, PT = 0.7, 0.5, 0.4, 0.95
CSF = {"A": (1.0, 0.0047, 0.0, 1e-5), "RG": (1.0, 0.0053, 0.0, 1e-5), "BY": (34.1, 0.04, 13.5, 0.025)}


def srgb_to_linear(c):
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def _mul(m, img):
    return np.einsum("ij,hwj->hwi", m, img)


def linear_to_ycxcz(rgb):
    xyz = _mul(RGB2XYZ, rgb) / WHITE
    return np.stack((116.0 * xyz[..., 1] - 16.0, 500.0 * (xyz[..., 0] - xyz[..., 1]),
                     200.0 * (xyz[..., 1] - xyz[..., 2])), axis=-1)


def ycxcz_to_linear(o):
    y = (o[..., 0] + 16.0) / 116.0
    xyz = np.stack((o[..., 1] / 500.0 + y, y, y - o[..., 2] / 200.0), axis=-1) * WHITE
    return _mul(XYZ2RGB, xyz)


def linear_to_hunt_lab(rgb):
    t = _mul(RGB2XYZ, rgb) / WHITE
    d = 6.0 / 29.0
    f = np.where(t > d ** 3, np.cbrt(t), t / (3 * d * d) + 4.0 / 29.0)
    L = 116.0 * f[..., 1] - 16.0
    a = 500.0 * (f[..., 0] - f[..., 1])
    b = 200.0 * (f[..., 1] - f[..., 2])
    return np.stack((L, 0.01 * L * a, 0.01 * L * b), axis=-1)


def hyab(x, y):
    d = x - y
    return np.abs(d[..., 0]) + np.sqrt(d[..., 1] ** 2 + d[..., 2] ** 2)


def conv1d(img, k, axis):
    """img (h, w) convolved with an odd 1-D kernel along one axis, the edges padded with their own values."""
    r = len(k) // 2
    pad = [(0, 0), (0, 0)]
    pad[axis] = (r, r)
    p = np.pad(img, pad, mode="edge")
    out = np.zeros_like(img)
    n = img.shape[axis]
    for i, w in enumerate(k[::-1]):     # a true convolution (the kernels here are symmetric or used by magnitude)
        if w == 0.0:
            continue
        sl = [slice(None), slice(None)]
        sl[axis] = slice(i, i + n)
        out += w * p[tuple(sl)]
    return out


def csf_filter(channel, name, ppd):
    """FLIP's spatial filter for one opponent channel: a normalised sum of two Gaussians, applied separably."""
    a1, b1, a2, b2 = CSF[name]
    bmax = max(v for c in CSF.values() for v in (c[1], c[3]))
    r = int(math.ceil(3.0 * math.sqrt(bmax / (2.0 * math.pi ** 2)) * ppd))
    x = np.arange(-r, r + 1) / ppd
    terms = [(a * math.sqrt(math.pi / b), np.exp(-math.pi ** 2 * x * x / b)) for a, b in ((a1, b1), (a2, b2)) if a > 0]
    total = sum(c * e.sum() ** 2 for c, e in terms)
    out = np.zeros_like(channel)
    for c, e in terms:
        out += (c / total) * conv1d(conv1d(channel, e, 0), e, 1)
    return out


def feature_kernels(ppd):
    sd = 0.5 * 0.082 * ppd
    r = int(math.ceil(3.0 * sd))
    x = np.arange(-r, r + 1, dtype=np.float64)
    e = np.exp(-x * x / (2.0 * sd * sd))
    smooth = e / e.sum()
    edge = -x * e
    edge = np.where(edge < 0, edge / -edge[edge < 0].sum(), edge / edge[edge > 0].sum())
    point = (x * x / (sd * sd) - 1.0) * e
    point = np.where(point < 0, point / -point[point < 0].sum(), point / point[point > 0].sum())
    return smooth, edge, point


def features(y, ppd):
    smooth, edge, point = feature_kernels(ppd)
    ex, ey = conv1d(conv1d(y, edge, 1), smooth, 0), conv1d(conv1d(y, edge, 0), smooth, 1)
    px, py = conv1d(conv1d(y, point, 1), smooth, 0), conv1d(conv1d(y, point, 0), smooth, 1)
    return np.hypot(ex, ey), np.hypot(px, py)


def _cmax():
    g = linear_to_hunt_lab(np.array([[[0.0, 1.0, 0.0]]]))
    b = linear_to_hunt_lab(np.array([[[0.0, 0.0, 1.0]]]))
    return float(hyab(g, b)[0, 0] ** QC)


CMAX = _cmax()


def flip(ref_srgb, test_srgb, ppd):
    """The per-pixel FLIP-like error of a test frame against its reference, both (h, w, 3) sRGB in [0, 1]."""
    out = []
    for img in (ref_srgb, test_srgb):
        o = linear_to_ycxcz(srgb_to_linear(img))
        filt = np.stack([csf_filter(o[..., i], n, ppd) for i, n in enumerate(("A", "RG", "BY"))], axis=-1)
        lab = linear_to_hunt_lab(np.clip(ycxcz_to_linear(filt), 0.0, 1.0))
        y = (o[..., 0] + 16.0) / 116.0
        out.append((lab, *features(y, ppd)))
    (lab_r, e_r, p_r), (lab_t, e_t, p_t) = out
    de = hyab(lab_r, lab_t) ** QC
    pcc = PC * CMAX
    de_c = np.where(de < pcc, (PT / pcc) * de, PT + ((de - pcc) / (CMAX - pcc)) * (1.0 - PT))
    de_f = (np.maximum(np.abs(e_r - e_t), np.abs(p_r - p_t)) / math.sqrt(2.0)) ** QF
    return de_c ** (1.0 - de_f)


# magma, sampled (matplotlib's), for the heat map
MAGMA = np.array([
    (0.0, 0.001, 0.000, 0.014), (0.1, 0.064, 0.044, 0.180), (0.2, 0.172, 0.068, 0.384), (0.3, 0.300, 0.072, 0.484),
    (0.4, 0.425, 0.115, 0.506), (0.5, 0.550, 0.161, 0.506), (0.6, 0.683, 0.205, 0.484), (0.7, 0.810, 0.255, 0.441),
    (0.8, 0.916, 0.342, 0.389), (0.9, 0.983, 0.502, 0.375), (0.95, 0.994, 0.624, 0.427), (1.0, 0.987, 0.991, 0.750)])


def heat(err):
    e = np.clip(err, 0.0, 1.0)
    return np.stack([np.interp(e, MAGMA[:, 0], MAGMA[:, i]) for i in (1, 2, 3)], axis=-1)


# -- the tool --------------------------------------------------------------------------------------------------------


def pngs(root):
    out = []
    for dp, _, fs in os.walk(root):
        for f in fs:
            if f.endswith(".png") and ".flip" not in f:
                out.append(os.path.relpath(os.path.join(dp, f), root))
    return sorted(out)


def compare(base, test, out, ppd=52.4, max_mean=0.0005, max_worst=0.05, sheet_scale=4, present=False):
    rows, strips = [], {}
    for rel in pngs(base):
        row = dict(frame=rel)
        tp = os.path.join(test, rel)
        if present and not os.path.exists(tp):
            continue
        if not os.path.exists(tp):
            row.update(passed=False, why="missing from the test set")
            rows.append(row)
            print("MISSING", rel)
            continue
        a, b = read_png(os.path.join(base, rel)), read_png(tp)
        if a.shape != b.shape:
            row.update(passed=False, why=f"size {a.shape[1]}x{a.shape[0]} -> {b.shape[1]}x{b.shape[0]}")
            rows.append(row)
            print("RESIZED", rel)
            continue
        identical = bool(np.array_equal(a, b))
        err = np.zeros(a.shape[:2]) if identical else flip(a, b, ppd)
        q = np.percentile(err, [99.0, 99.9]) if not identical else (0.0, 0.0)
        row.update(identical=identical, mean=float(err.mean()), p99=float(q[0]), p999=float(q[1]),
                   worst=float(err.max()), over005=float((err > 0.05).mean()),
                   changed_pixels=int((np.abs(a - b).max(axis=-1) > 0).sum()))
        row["passed"] = row["mean"] <= max_mean and row["worst"] <= max_worst
        if not row["passed"]:
            row["why"] = "over the threshold"
        rows.append(row)
        stem = os.path.join(out, rel[:-4])
        write_png(stem + ".flip.png", heat(err))
        write_png(stem + ".flip10.png", heat(err * 10.0))
        k = sheet_scale
        strip = np.concatenate([shrink(a, k), shrink(b, k), shrink(heat(err), k), shrink(heat(err * 10.0), k)], axis=1)
        strips.setdefault(os.path.dirname(rel) or ".", []).append(strip)
        print(f"{'PASS' if row['passed'] else 'FAIL'} {rel}: mean {row['mean']:.6f}, p99.9 {row['p999']:.4f}, "
              f"worst {row['worst']:.4f}, {row['changed_pixels']} pixels changed{' (identical)' if identical else ''}")
    for folder, ss in strips.items():
        gap = np.ones((6, ss[0].shape[1], 3))
        sheet = np.concatenate([x for s in ss for x in (s, gap)][:-1], axis=0)
        write_png(os.path.join(out, "sheet-" + folder.replace(os.sep, "-").replace(".", "all") + ".png"), sheet)
    passed = all(r["passed"] for r in rows) and bool(rows)
    report = dict(baseline=os.path.abspath(base), test=os.path.abspath(test), ppd=ppd,
                  thresholds=dict(mean=max_mean, worst=max_worst), passed=passed, frames=rows,
                  metric="FLIP-like (golden_compare.py, an approximation of LDR-FLIP)")
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, "report.json"), "w") as fh:
        json.dump(report, fh, indent=1)
    with open(os.path.join(out, "report.md"), "w") as fh:
        fh.write(f"# Golden comparison\n\n{'All frames pass' if passed else 'FAILED'}: mean at most {max_mean}, worst "
                 f"pixel at most {max_worst} (FLIP-like, {ppd} pixels a degree).\n\n"
                 "| Frame | Mean | 99.9th | Worst | Over 0.05 | Pixels changed | |\n| --- | --- | --- | --- | --- | --- | --- |\n")
        for r in rows:
            if "mean" in r:
                fh.write(f"| {r['frame']} | {r['mean']:.6f} | {r['p999']:.4f} | {r['worst']:.4f} | "
                         f"{100 * r['over005']:.3f}% | {r['changed_pixels']} | {'pass' if r['passed'] else 'FAIL'} |\n")
            else:
                fh.write(f"| {r['frame']} | | | | | | FAIL: {r['why']} |\n")
    print("PASSED" if passed else "FAILED", os.path.join(out, "report.md"))
    return 0 if passed else 1


def accept(test, base):
    for rel in pngs(test):
        dst = os.path.join(base, rel)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copyfile(os.path.join(test, rel), dst)
        print("ACCEPTED", rel)
    for dp, _, fs in os.walk(test):
        for f in fs:
            if f == "frames.json":
                rel = os.path.relpath(os.path.join(dp, f), test)
                shutil.copyfile(os.path.join(test, rel), os.path.join(base, rel))
    return 0


def selftest(out, ppd=52.4):
    rng = np.random.default_rng(1)
    h, w = 360, 640
    yy, xx = np.mgrid[0:h, 0:w]
    base = np.stack([0.3 + 0.4 * xx / w, 0.35 + 0.1 * np.sin(yy / 9.0), 0.45 - 0.2 * yy / h], axis=-1)
    base += 0.08 * (rng.random((h, w, 1)) - 0.5)        # a painted grain
    base = np.round(np.clip(base, 0, 1) * 255) / 255
    small = base.copy()
    small[150:190, 300:360, 0] = np.clip(small[150:190, 300:360, 0] + 6 / 255, 0, 1)
    big = base.copy()
    big[150:190, 300:360] = np.clip(big[150:190, 300:360] * 1.25, 0, 1)
    same = flip(base, base, ppd)
    e_small, e_big = flip(base, small, ppd), flip(base, big, ppd)
    inside = (slice(150, 190), slice(300, 360))
    far = np.ones((h, w), bool)
    far[120:220, 270:390] = False
    checks = [
        ("identical images score zero everywhere", float(same.max()) == 0.0),
        ("a small change scores inside the patch", float(e_small[inside].mean()) > 0.005),
        ("and nothing far from it", float(e_small[far].max()) < 1e-9),
        ("a larger change scores higher", float(e_big[inside].mean()) > float(e_small[inside].mean())),
    ]
    write_png(os.path.join(out, "selftest-heat.png"),
              np.concatenate([base, small, heat(e_small), heat(10 * e_small), heat(e_big)], axis=1))
    for name, ok in checks:
        print("PASS" if ok else "FAIL", name)
    print(f"small patch mean {e_small[inside].mean():.4f}, worst {e_small.max():.4f}; "
          f"large patch mean {e_big[inside].mean():.4f}")
    return 0 if all(ok for _, ok in checks) else 1


if __name__ == "__main__":
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
    opts = {}
    pos = []
    i = 0
    while i < len(argv):
        if argv[i].startswith("--"):
            opts[argv[i][2:]] = float(argv[i + 1])
            i += 2
        else:
            pos.append(argv[i])
            i += 1
    cmd = pos[0] if pos else ""
    if cmd == "compare":
        code = compare(pos[1], pos[2], pos[3], ppd=opts.get("ppd", 52.4), max_mean=opts.get("mean", 0.0005),
                       max_worst=opts.get("worst", 0.05), sheet_scale=int(opts.get("sheet-scale", 4)),
                       present=bool(opts.get("present", 0)))
    elif cmd == "accept":
        code = accept(pos[1], pos[2])
    elif cmd == "selftest":
        code = selftest(pos[1], ppd=opts.get("ppd", 52.4))
    else:
        print(__doc__)
        code = 2
    sys.stdout.flush()
    os._exit(code)
