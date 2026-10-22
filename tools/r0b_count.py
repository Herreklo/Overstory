"""R0b's counter (reviews/lt1/port/2b/design.md, The ladder, R0b; Done 4): one-pixel lines and specks in the gully's own
pixels, on frames at the player's size (Editor/LT1R0b.cs writes <root>/<moment>/<config>/<view>.png and the gully's
mask at <root>/<moment>/mask/<view>.png).

On L* (from the frame's sRGB, through linear luminance), inside the mask eroded by 2 px so the gully's outline against
what lies beyond it is never counted:
- lines: a white top-hat (L* less its 3 x 3 opening) and a black one (the 3 x 3 closing less L*), each over 4 L* (the
  threshold of blender/tools/patch_sheet.py's checks); 8-connected pieces longer than 10 px and under 2 px wide (length
  the larger of the piece's extents, width its pixels over its length or twice its minor axis' deviation). Reported as
  the total length in px, bright and dark;
- specks: 8-connected blobs of 1 to 4 px whose L* is more than 8 from the 5 x 5 median around them, bright and dark.

    python3.13 tools/r0b_count.py [root [moments]]  counts the frames, merged into <root>/counts.json
    python3.13 tools/r0b_count.py --table [root]    the result's tables in Markdown, from counts.json
    python3.13 tools/r0b_count.py --where [root [moments]]   where the marks sit: by surface kind and baked sky light
    python3.13 tools/r0b_count.py --same a.png b.png    pixel identity of two frames (the toggles' bit-identity proof)
    python3.13 tools/r0b_count.py --sheet [root]    <root>/sheet.png: baseline against all fixes, native crops

Needs numpy (Blender's own Python has it: /Applications/Blender.app/Contents/Resources/5.2/python/bin/python3.13).
PNGs are read through macOS sips as uncompressed BMP (checked exact on Unity's PNGs, which carry no colour chunk).
"""
import json
import os
import struct
import subprocess
import sys
import tempfile
import zlib

import numpy as np

LINE_T, SPECK_T = 4.0, 8.0
LINE_LEN, LINE_W = 10, 2.0
ERODE = 2
VIEWS = ["eye-foot", "eye-on", "eye-down", "street", "into12", "high"]
CONFIGS = ["A", "gnf", "jointfloor", "cutmarks", "bloom-off", "bloom-clamp", "bias02", "ssao-off", "all", "all-clamp",
           "all-flat", "all-onecolour", "all-norelief", "all-nogrowth", "all-onerock", "all-nolichen", "all-nomoss",
           "A2"]
MOMENTS = ["1600-low-sun", "1300-drizzle", "1750-blue-hour"]


def read_png(path):
    """An 8-bit PNG as (h, w, 3) uint8, top row first (through sips to BMP)."""
    with tempfile.TemporaryDirectory() as d:
        bmp = os.path.join(d, "f.bmp")
        subprocess.run(["sips", "-s", "format", "bmp", path, "--out", bmp], check=True, capture_output=True)
        b = open(bmp, "rb").read()
    off = int.from_bytes(b[10:14], "little")
    w = int.from_bytes(b[18:22], "little", signed=True)
    h = int.from_bytes(b[22:26], "little", signed=True)
    bpp = int.from_bytes(b[28:30], "little")
    stride = (w * bpp // 8 + 3) // 4 * 4
    a = np.frombuffer(b, np.uint8, count=stride * abs(h), offset=off).reshape(abs(h), stride)
    a = a[:, :w * bpp // 8].reshape(abs(h), w, bpp // 8)[..., 2::-1]
    return np.ascontiguousarray(a if h < 0 else a[::-1])


def write_png(path, rgb):
    rgb = np.ascontiguousarray(rgb.astype(np.uint8))
    h, w, _ = rgb.shape
    raw = np.zeros((h, 1 + w * 3), np.uint8)
    raw[:, 1:] = rgb.reshape(h, w * 3)

    def chunk(t, d):
        return struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t + d) & 0xFFFFFFFF)
    with open(path, "wb") as fh:
        fh.write(b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0))
                 + chunk(b"IDAT", zlib.compress(raw.tobytes(), 9)) + chunk(b"IEND", b""))


def lstar(rgb8):
    c = rgb8.astype(np.float32) / 255.0
    lin = np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)
    y = lin[..., 0] * 0.2126 + lin[..., 1] * 0.7152 + lin[..., 2] * 0.0722
    f = np.where(y > (6 / 29) ** 3, np.cbrt(y), y / (3 * (6 / 29) ** 2) + 4 / 29)
    return (116 * f - 16).astype(np.float32)


def _shift(a, dy, dx, fill):
    out = np.full_like(a, fill)
    H, W = a.shape
    ys, yd = (slice(dy, H), slice(0, H - dy)) if dy >= 0 else (slice(0, H + dy), slice(-dy, H))
    xs, xd = (slice(dx, W), slice(0, W - dx)) if dx >= 0 else (slice(0, W + dx), slice(-dx, W))
    out[yd, xd] = a[ys, xs]
    return out


def erode(a, r=1):
    fill = np.inf if a.dtype.kind == "f" else (True if a.dtype == bool else a.max())
    out = a.copy()
    for dy in range(-r, r + 1):
        for dx in range(-r, r + 1):
            out = np.minimum(out, _shift(a, dy, dx, fill))
    return out


def dilate(a, r=1):
    fill = -np.inf if a.dtype.kind == "f" else (False if a.dtype == bool else a.min())
    out = a.copy()
    for dy in range(-r, r + 1):
        for dx in range(-r, r + 1):
            out = np.maximum(out, _shift(a, dy, dx, fill))
    return out


def median5(a, rows=160):
    """The 5 x 5 median of each pixel (edges padded by their own values), in bands of rows."""
    p = np.pad(a, 2, mode="edge")
    H, W = a.shape
    out = np.empty_like(a)
    for y0 in range(0, H, rows):
        y1 = min(H, y0 + rows)
        st = np.stack([p[y0 + 2 + dy:y1 + 2 + dy, 2 + dx:2 + dx + W] for dy in range(-2, 3) for dx in range(-2, 3)])
        out[y0:y1] = np.partition(st, 12, axis=0)[12]
    return out


def pieces(mask):
    """8-connected pieces of a boolean mask as a label per set pixel (vectorised union-find with pointer jumping)."""
    ys, xs = np.nonzero(mask)
    n = len(ys)
    if n == 0:
        return ys, xs, np.zeros(0, np.int64)
    idx = -np.ones(mask.shape, np.int64)
    idx[ys, xs] = np.arange(n)
    H, W = mask.shape
    ea, eb = [], []
    for dy, dx in ((0, 1), (1, -1), (1, 0), (1, 1)):
        y2, x2 = ys + dy, xs + dx
        ok = (y2 >= 0) & (y2 < H) & (x2 >= 0) & (x2 < W)
        a = np.nonzero(ok)[0]
        b = idx[y2[a], x2[a]]
        k = b >= 0
        ea.append(a[k])
        eb.append(b[k])
    ea, eb = np.concatenate(ea), np.concatenate(eb)
    parent = np.arange(n)
    while True:
        ra, rb = parent[ea], parent[eb]
        diff = ra != rb
        if not diff.any():
            break
        lo, hi = np.minimum(ra[diff], rb[diff]), np.maximum(ra[diff], rb[diff])
        np.minimum.at(parent, hi, lo)
        while True:
            nxt = parent[parent]
            if np.array_equal(nxt, parent):
                break
            parent = nxt
    return ys, xs, parent


def groups(ys, xs, labels):
    order = np.argsort(labels, kind="stable")
    lab = labels[order]
    cuts = np.nonzero(np.diff(lab))[0] + 1
    return np.split(ys[order], cuts), np.split(xs[order], cuts)


def shape_of(ys, xs):
    length = max(np.ptp(xs), np.ptp(ys)) + 1.0
    if len(ys) < 3:
        return length, len(ys) / length
    c = np.cov(np.stack([xs, ys]).astype(np.float64))
    ev = np.sort(np.linalg.eigvalsh(c))
    return length, max(len(ys) / length, 2.0 * np.sqrt(max(ev[0], 0.0)))


def count(frame, mask, overlay=False):
    L = lstar(frame)
    m = erode(mask, ERODE)
    res = {"mask_px": int(m.sum())}
    marks = np.zeros(L.shape, np.uint8)
    for kind, top in (("bright", L - dilate(erode(L))), ("dark", erode(dilate(L)) - L)):
        ys, xs, lab = pieces((top > LINE_T) & m)
        total, n = 0.0, 0
        if len(ys):
            for gy, gx in zip(*groups(ys, xs, lab)):
                if len(gy) <= LINE_LEN:
                    continue
                length, width = shape_of(gy, gx)
                if length > LINE_LEN and width < LINE_W:
                    total += length
                    n += 1
                    if overlay:
                        marks[gy, gx] = 1 if kind == "bright" else 2
        res[f"{kind}_line_px"] = round(total)
        res[f"{kind}_lines"] = n
    med = median5(L)
    for kind, diff in (("bright", L - med), ("dark", med - L)):
        ys, xs, lab = pieces((diff > SPECK_T) & m)
        n = 0
        if len(ys):
            sizes = np.bincount(np.unique(lab, return_inverse=True)[1])
            n = int(((sizes >= 1) & (sizes <= 4)).sum())
            if overlay:
                u, inv = np.unique(lab, return_inverse=True)
                small = (sizes <= 4)[inv]
                marks[ys[small], xs[small]] = 3
        res[f"{kind}_specks"] = n
    res["line_px"] = res["bright_line_px"] + res["dark_line_px"]
    res["specks"] = res["bright_specks"] + res["dark_specks"]
    return (res, marks) if overlay else res


def load_mask(root, moment, view):
    return read_png(os.path.join(root, moment, "mask", view + ".png"))[..., 0] > 127


def _one(job):
    root, moment, view = job
    mask = load_mask(root, moment, view)
    res = {}
    for config in CONFIGS:
        f = os.path.join(root, moment, config, view + ".png")
        if os.path.exists(f):
            res[f"{moment}/{config}/{view}"] = count(read_png(f), mask)
    return res


def run(root, moments=None, workers=6):
    """Counts the frames of the moments asked (all by default), merged into <root>/counts.json, a view a process."""
    import multiprocessing
    cj = os.path.join(root, "counts.json")
    out = json.load(open(cj)) if os.path.exists(cj) else {}
    jobs = [(root, m, v) for m in MOMENTS for v in VIEWS
            if not (moments and m not in moments) and os.path.exists(os.path.join(root, m, "mask", v + ".png"))]
    with multiprocessing.get_context("spawn").Pool(workers) as pool:
        for res in pool.imap_unordered(_one, jobs):
            for k, r in sorted(res.items()):
                out[k] = r
                print(k, r["line_px"], r["specks"], flush=True)
    with open(cj, "w") as fh:
        json.dump(out, fh, indent=1, sort_keys=True)
    return out


def same(a, b):
    ba, bb = open(a, "rb").read(), open(b, "rb").read()
    pa, pb = read_png(a), read_png(b)
    d = np.abs(pa.astype(int) - pb.astype(int))
    print(f"bytes {'identical' if ba == bb else 'differ'}; pixels differing {int((d.max(axis=2) > 0).sum())}, "
          f"largest difference {int(d.max())}")


def sheet(root, size=300):
    """Baseline (A) against all fixes, native crops at eye-foot and street in low sun; then the mesh alone (all-flat);
    then A's marks and all-flat's: bright lines red, dark lines blue, specks yellow."""
    moment, rows = "1600-low-sun", []
    for view in ("eye-foot", "street"):
        mask = load_mask(root, moment, view)
        a = read_png(os.path.join(root, moment, "A", view + ".png"))
        z = read_png(os.path.join(root, moment, "all", view + ".png"))
        f = read_png(os.path.join(root, moment, "all-flat", view + ".png"))
        _, marks = count(a, mask, overlay=True)
        _, fmarks = count(f, mask, overlay=True)
        # the crop with most of the baseline's marks in it
        dens = (marks > 0).astype(np.float64)
        ii = np.pad(dens.cumsum(0).cumsum(1), ((1, 0), (1, 0)))
        H, W = dens.shape
        win = ii[size:, size:] - ii[:-size, size:] - ii[size:, :-size] + ii[:-size, :-size]
        y, x = np.unravel_index(np.argmax(win[::4, ::4]), win[::4, ::4].shape)
        y, x = y * 4, x * 4
        crop = lambda img: img[y:y + size, x:x + size]
        def ov(img, mk):
            o = (lstar(img)[..., None] / 100.0 * 255 * 0.6).repeat(3, 2).astype(np.uint8)
            for k, col in ((1, (255, 40, 40)), (2, (60, 120, 255)), (3, (255, 230, 0))):
                o[mk == k] = col
            return o
        gap = np.full((size, 4, 3), 255, np.uint8)
        rows.append(np.concatenate([crop(a), gap, crop(z), gap, crop(f), gap, crop(ov(a, marks)), gap,
                                    crop(ov(f, fmarks))], axis=1))
        print(view, "crop at", x, y)
    hgap = np.full((4, rows[0].shape[1], 3), 255, np.uint8)
    write_png(os.path.join(root, "sheet.png"), np.concatenate([rows[0], hgap, rows[1]], axis=0))


KIND_NAMES = ["top", "edge", "split", "bed", "pointing", "dab", "soil", "?"]


def kinds_of(root, moment, view):
    """Each pixel's kind (0 to 6, from the kinds map's red as kind / 8 in linear light; a strip between two kinds,
    interpolated, rounds to the nearer) and whether it lies on a stone's outline: within 2 px of another piece (the
    green channel is the piece's seed, one value over a stone) or of what is not stone."""
    raw = read_png(os.path.join(root, moment, "kinds", view + ".png"))
    k = raw.astype(np.float32) / 255.0
    lin = np.where(k <= 0.04045, k / 12.92, ((k + 0.055) / 1.055) ** 2.4)
    seed = raw[..., 1].astype(np.int16)
    outline = (dilate(seed, 2) - erode(seed, 2)) > 1
    return np.clip(np.round(lin[..., 0] * 8.0), 0, 7).astype(int), outline


WHERE_CONFIGS = ("A", "all", "all-flat", "all-onecolour", "all-nogrowth", "all-nolichen", "all-nomoss")


def _where_one(job):
    root, moment, config, view = job
    f = os.path.join(root, moment, config, view + ".png")
    acc = {}
    if os.path.exists(f):
        mask = load_mask(root, moment, view)
        kind, outline = kinds_of(root, moment, view)
        m = erode(mask, ERODE)
        _, marks = count(read_png(f), mask, overlay=True)
        for name, sel in (("mask", m), ("bright_line", marks == 1), ("dark_line", marks == 2), ("specks", marks == 3)):
            a = np.zeros(9)
            a[:8] += np.bincount(kind[sel], minlength=8)[:8]
            a[8] += (sel & m & outline).sum()
            acc[name] = a
    return moment, config, acc


def where(root, moments=None, configs=WHERE_CONFIGS, workers=6):
    """Where the marks sit: for each config, the share of bright and dark line px and of specks on each kind of
    surface, and on a stone's outline (its joints and the arrises against its neighbours); the mask's own shares
    beside them. Summed over the views of each light; merged into <root>/where.json, a frame a process."""
    import multiprocessing
    wj = os.path.join(root, "where.json")
    out = json.load(open(wj)) if os.path.exists(wj) else {}
    jobs = [(root, mo, c, v) for mo in MOMENTS for c in configs for v in VIEWS
            if not (moments and mo not in moments) and os.path.isdir(os.path.join(root, mo, "kinds"))]
    sums = {}
    with multiprocessing.get_context("spawn").Pool(workers) as pool:
        for moment, config, acc in pool.imap_unordered(_where_one, jobs):
            tot = sums.setdefault((moment, config), {})
            for name, a in acc.items():
                tot[name] = tot.get(name, np.zeros(9)) + a
    for (moment, config), acc in sorted(sums.items(), key=lambda kv: (MOMENTS.index(kv[0][0]), configs.index(kv[0][1]))):
        if not acc:
            continue
        out[f"{moment}/{config}"] = {k: v.tolist() for k, v in acc.items()}
        line = []
        for name in ("mask", "bright_line", "dark_line", "specks"):
            a = acc[name]
            tot = max(a[:8].sum(), 1)
            line.append(f"{name} " + " ".join(f"{KIND_NAMES[i]} {100 * a[i] / tot:.0f}%" for i in range(8) if a[i])
                        + f" | on an outline {100 * a[8] / tot:.0f}%")
        print(moment, config, "\n  " + "\n  ".join(line), flush=True)
    with open(wj, "w") as fh:
        json.dump(out, fh, indent=1, sort_keys=True)


def table(root):
    """Markdown from counts.json: per light and view, each config's lines (px) / specks; then each change's share of
    the baseline's, summed over the views (positive: removed)."""
    c = json.load(open(os.path.join(root, "counts.json")))
    cfgs = [k for k in CONFIGS if any(f"/{k}/" in key for key in c)]
    out = ["| light | view | " + " | ".join(cfgs) + " |", "|" + " --- |" * (len(cfgs) + 2)]
    for moment in MOMENTS:
        for view in VIEWS:
            cells = [f"{c[k]['line_px']}/{c[k]['specks']}" if (k := f"{moment}/{cfg}/{view}") in c else "-" for cfg in cfgs]
            if any(x != "-" for x in cells):
                out.append(f"| {moment} | {view} | " + " | ".join(cells) + " |")
    out += ["", "| light | metric | " + " | ".join(cfgs[1:]) + " |", "|" + " --- |" * (len(cfgs) + 1)]
    for moment in MOMENTS + ["all"]:
        for metric in ("line_px", "specks"):
            def tot(cfg):
                ks = [f"{m}/{cfg}/{v}" for m in (MOMENTS if moment == "all" else [moment]) for v in VIEWS]
                ks = [k for k in ks if k in c and f"{k.split('/')[0]}/A/{k.split('/')[2]}" in c]
                return sum(c[k][metric] for k in ks), len(ks)
            base, n = tot("A")
            if n == 0:
                continue
            cells = []
            for cfg in cfgs[1:]:
                t, m = tot(cfg)
                cells.append(f"{100 * (base - t) / base:+.0f}%" if base and m == n else "-")
            out.append(f"| {moment} | {metric} (A {base}) | " + " | ".join(cells) + " |")
    print("\n".join(out))


if __name__ == "__main__":
    args = sys.argv[1:]
    if args and args[0] == "--where":
        where(args[1] if len(args) > 1 else "reviews/lt1/port/2b/r0b", args[2].split(",") if len(args) > 2 else None)
    elif args and args[0] == "--table":
        table(args[1] if len(args) > 1 else "reviews/lt1/port/2b/r0b")
    elif args and args[0] == "--same":
        same(args[1], args[2])
    elif args and args[0] == "--sheet":
        sheet(args[1] if len(args) > 1 else "reviews/lt1/port/2b/r0b")
    else:
        run(args[0] if args else "reviews/lt1/port/2b/r0b", args[1].split(",") if len(args) > 1 else None)
