"""The shimmer measure (docs/measuring.md, Motion sheets; docs/research/painted-marks-in-motion.md, Look tests that would
prove it, 2): how much fine detail changes from one frame of a sequence to the next.

    blender -b --factory-startup --python blender/tools/motion_measure.py -- measure <sequence dir> [<sequence dir> ...]
        [--out <dir>] [--sigma 1.5] [--level 3]
    blender -b --factory-startup --python blender/tools/motion_measure.py -- selftest <out dir>

For each pair of consecutive frames: the luma of each (Rec. 709 weights on the sRGB values, so the scale is roughly
perceptual, in 8-bit levels), their difference, and the fine part of that difference (the difference less its own
Gaussian blur of --sigma pixels): what changed at the scale of a pixel or two, where shimmer, crawl and popping live.
Per pair: the mean of its magnitude (the shimmer, in 8-bit levels), its 99th percentile, and the share of pixels whose
fine change is over --level levels (the flicker). Per sequence: their mean, median and worst over the pairs, a map of
where the fine change gathers (its mean magnitude per pixel over the sequence), and a sheet of the first frame beside
that map. A still camera on a still world must measure zero; anything above it is something moving that should not.

A moving camera moves every edge too, so its shimmer is never zero: the measure compares the same path before and after
a change (A/B), never two paths, and a mark that swims or crawls raises it. It is the first of the research's two
measures; the swim test, which warps each frame onto the next by its motion vectors and measures what is left, needs
the depth or motion vectors written beside each frame and is still to come. Thresholds are set against what Øystein sees.

Writes <out>/shimmer.json and shimmer.md (one row per sequence; a sequence measured again into the same folder replaces
its row) and a sheet per sequence; prints one line per sequence.
"""

import json
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import golden_compare as G  # noqa: E402  (PNG in and out, sheets)


def luma(rgb):
    return 255.0 * (0.2126 * rgb[..., 0] + 0.7152 * rgb[..., 1] + 0.0722 * rgb[..., 2])


def blur(img, sigma):
    r = int(math.ceil(3 * sigma))
    x = np.arange(-r, r + 1, dtype=np.float64)
    k = np.exp(-x * x / (2 * sigma * sigma))
    k /= k.sum()
    return G.conv1d(G.conv1d(img, k, 0), k, 1)


def fine_change(a, b, sigma):
    d = b - a
    return d - blur(d, sigma)


def measure_frames(frames, sigma=1.5, level=3.0):
    """frames: an iterable of (h, w) luma arrays in order. Returns (per-pair rows, mean fine-change map)."""
    rows, acc, prev, n = [], None, None, 0
    for i, y in enumerate(frames):
        if prev is not None:
            h = np.abs(fine_change(prev, y, sigma))
            rows.append(dict(pair=i - 1, shimmer=float(h.mean()), p99=float(np.percentile(h, 99.0)),
                             flicker=float((h > level).mean()), changed=float((y != prev).mean())))
            acc = h if acc is None else acc + h
            n += 1
        prev = y
    return rows, (acc / n if n else None)


def summary(rows):
    s = np.array([r["shimmer"] for r in rows]) if rows else np.zeros(1)
    f = np.array([r["flicker"] for r in rows]) if rows else np.zeros(1)
    return dict(pairs=len(rows), shimmer_mean=float(s.mean()), shimmer_median=float(np.median(s)),
                shimmer_worst=float(s.max()), flicker_mean=float(f.mean()), flicker_worst=float(f.max()))


def measure(dirs, out=None, sigma=1.5, level=3.0):
    results = []
    for d in dirs:
        files = sorted(f for f in os.listdir(d) if f.endswith(".png") and f[:4].isdigit())
        first = None

        def frames():
            nonlocal first
            for f in files:
                rgb = G.read_png(os.path.join(d, f))
                if first is None:
                    first = rgb
                yield luma(rgb)

        rows, mean_map = measure_frames(frames(), sigma, level)
        meta = {}
        if os.path.exists(os.path.join(d, "sequence.json")):
            with open(os.path.join(d, "sequence.json")) as fh:
                meta = json.load(fh)
        name = "-".join(p for p in (meta.get("moment"), os.path.basename(os.path.normpath(d))) if p)
        res = dict(sequence=name, dir=os.path.abspath(d), frames=len(files), sigma=sigma, level=level, **summary(rows),
                   per_pair=rows)
        results.append(res)
        print(f"{name}: {len(files)} frames, shimmer mean {res['shimmer_mean']:.4f} (worst {res['shimmer_worst']:.4f}) "
              f"levels, flicker {100 * res['flicker_mean']:.3f}% of pixels over {level} levels")
        if out and mean_map is not None:
            os.makedirs(out, exist_ok=True)
            # the map scaled so 2 levels of mean fine change is the top of the heat scale
            sheet = np.concatenate([G.shrink(first, 4), G.shrink(G.heat(mean_map / 2.0), 4)], axis=1)
            G.write_png(os.path.join(out, f"{name}-shimmer.png"), sheet)
    if out:
        os.makedirs(out, exist_ok=True)
        # (a day's report gathers every sequence measured into it; one measured again replaces its row)
        path = os.path.join(out, "shimmer.json")
        if os.path.exists(path):
            with open(path) as fh:
                kept = [r for r in json.load(fh) if r["sequence"] not in {x["sequence"] for x in results}]
            results = kept + results
        with open(path, "w") as fh:
            json.dump(results, fh, indent=1)
        with open(os.path.join(out, "shimmer.md"), "w") as fh:
            fh.write("# Shimmer\n\nThe fine change between consecutive frames (motion_measure.py), in 8-bit levels of luma: "
                     f"its mean per pair (median and worst over the pairs), and the share of pixels whose fine change is "
                     f"over {level} levels. Blur {sigma} px.\n\n"
                     "| Sequence | Frames | Shimmer, mean | Median | Worst pair | Flicker, mean | Worst pair |\n"
                     "| --- | --- | --- | --- | --- | --- | --- |\n")
            for r in results:
                fh.write(f"| {r['sequence']} | {r['frames']} | {r['shimmer_mean']:.4f} | {r['shimmer_median']:.4f} | "
                         f"{r['shimmer_worst']:.4f} | {100 * r['flicker_mean']:.3f}% | {100 * r['flicker_worst']:.3f}% |\n")
    return results


def selftest(out):
    """A still sequence measures zero; a pattern finer than a pixel, sampled without filtering, crawls as it moves and
    measures far more than the same pattern filtered to the pixel, and more than a coarse pattern moving the same."""
    h, w, n, speed = 120, 240, 30, 0.37      # a third of a pixel a frame

    def frames(freq, filtered, still=False):
        ys, xs = np.mgrid[0:h, 0:w].astype(np.float64)
        for t in range(n):
            off = 0.0 if still else speed * t
            if filtered:     # each pixel the mean of the pattern over its footprint (16 by 16 samples)
                acc = np.zeros((h, w))
                for j in range(16):
                    for i in range(16):
                        acc += np.sin(2 * math.pi * freq * (xs + (i + 0.5) / 16 - 0.5 + off + 0.6 * (ys + (j + 0.5) / 16 - 0.5)))
                v = acc / 256.0
            else:            # one sample a pixel, at its centre
                v = np.sin(2 * math.pi * freq * (xs + off + 0.6 * ys))
            yield 128.0 + 100.0 * v

    cases = {
        "still, fine pattern": measure_frames(frames(0.93, False, still=True))[0],
        "coarse pattern moving": measure_frames(frames(0.04, False))[0],
        "fine pattern filtered, moving": measure_frames(frames(0.93, True))[0],
        "fine pattern aliased, moving (crawls)": measure_frames(frames(0.93, False))[0],
    }
    s = {k: summary(v)["shimmer_mean"] for k, v in cases.items()}
    for k, v in s.items():
        print(f"  {k}: shimmer {v:.4f} levels")
    checks = [
        ("a still sequence measures zero", s["still, fine pattern"] == 0.0),
        ("an aliased pattern crawling scores more than the same pattern filtered",
         s["fine pattern aliased, moving (crawls)"] > 10 * max(s["fine pattern filtered, moving"], 1e-9)),
        ("and more than a coarse pattern moving as fast",
         s["fine pattern aliased, moving (crawls)"] > 10 * s["coarse pattern moving"]),
    ]
    for name, ok in checks:
        print("PASS" if ok else "FAIL", name)
    return 0 if all(ok for _, ok in checks) else 1


if __name__ == "__main__":
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
    opts, pos, i = {}, [], 0
    while i < len(argv):
        if argv[i].startswith("--"):
            opts[argv[i][2:]] = argv[i + 1]
            i += 2
        else:
            pos.append(argv[i])
            i += 1
    cmd = pos[0] if pos else ""
    if cmd == "measure":
        measure(pos[1:], opts.get("out"), float(opts.get("sigma", 1.5)), float(opts.get("level", 3.0)))
        code = 0
    elif cmd == "selftest":
        code = selftest(pos[1] if len(pos) > 1 else ".")
    else:
        print(__doc__)
        code = 2
    sys.stdout.flush()
    os._exit(code)
