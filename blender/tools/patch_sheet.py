"""The face patches' check sheet (R2a in reviews/lt1/port/2b/design.md; the patches: blender/parts/stone/slate/patches.py).

Each patch is shown flat in grey, in neutral light raking from the upper left, from its stored maps: at 1 m (1 mm a
pixel), at 5 m and at 12 m (5 and 12 mm a pixel), and at one-eighth of the 1 m view. The far views are merged the way
the shader's footprint fade and the mips would merge them: the height and value low-passed by a Gaussian of one view
pixel, the normals taken from the low-passed height, then each view pixel the mean of its texels. Shading is Lambert
from the normal with a flat ambient, no cast shadows, since the shader has none from a patch either.

The checks (SN7's self-check), on L* of each view at its own size:
- one-pixel lines: a white top-hat (the image less its 3 x 3 opening) over a threshold, pieces 10 px or longer with a
  length at least four times their width; dark lines the same from a black top-hat;
- thin long lines (the "loose lines" a viewer names first): pieces of either top-hat over half the threshold, at most
  2 px wide and over 40 px long; at 5 m the aim is none;
- streaks: the same from 5 x 5 top-hats (marks up to 4 px wide) over 3 L*, over 40 px long and six times their width:
  how many steps still read as drawn strokes rather than ledges;
- floating lines (a line that starts or ends in the middle of the face, "disconnected from the shape", Øystein): the
  3 x 3 and 5 x 5 top-hats of each polarity over 1 L*, joined on the torus (so a line that crosses the wrap is one
  piece) across gaps of a pixel or two (the eye carries a line over them), kept where they reach 2 L* somewhere; a piece over 10 px long and four times its width is a line, and it
  floats unless it runs right across the patch (every column, or every row). At 1 m and 5 m the aim is none;
- spread: L*'s standard deviation and its 5th to 95th percentile range at each view (the face should hold within
  about 2 L* at 5 m in grey light: The Witness's final wall, by the coordinator's reading of its slides 30 and 31);
- specks: pieces of at most 2 x 2 px brighter (or darker) than their 5 x 5 median by 3 MADs and at least the threshold;
- calm: L*'s spread at each view, and the busyness measure of Done 5 (edge density and high-frequency share of L*);
- value: the value map's percentiles; relief: the height's histogram and percentiles; laminae steps a riser shows;
- tiling: the jump across the wrap against the mean step between neighbours inside, rows and columns;
- ledges (version 3), each found in the stored height map near the generator's boundary: in every column, the row
  of a broken edge's middle, where the face falls fastest down-dip. Its straightness: how far that trace strays from
  the best straight line (range and RMS, mm) and its local angle off the axis over 33 mm (p2, p98 and the most,
  degrees). The break falls almost evenly across its middle, so the trace is the centroid of the rows around the
  fastest fall that fall at least half as fast, not the fastest row alone (which jumps with the fine tooth). Its
  depth along its run: the fall from the highest point in the 35 mm up-dip to the lowest in the 35 mm down-dip (p5,
  p50, p95, and p95 over p5, its swell). The same for a bed face's scarp;
- spacing across the four split faces: each face's ledges and bands, the gaps between its ledges (mm, at their mean
  rows) and the widest over the narrowest; across the set, the gaps' coefficient of variation, and side by side (two
  faces at the same rows) the share of one face's ledges with a ledge of the other within 25 mm, at most over pairs;
- lattice repeat: how much a split face's facets repeat themselves, on their fold map (the magnitude of the facets'
  Laplacian, rebuilt by the generator once the stored maps' hashes match). Across the torus, the highest local peak
  of the autocorrelation outside its central lobe (an ellipse 30 mm along u and 20 across) and where; and locally,
  the same in each 256 mm window, as a mean and most over the sixteen windows: a lattice bent along the face loses
  its peaks across the torus but keeps short rows of like cells, which is what the eye catches. The same across the
  torus of the 1 m view's L* band-passed between 2 and 40 mm: high where the face looks alike shifted along u, as
  straight ruled ledges do.

The A/B on the spread limit (SN7): one split face built again in memory with only its facets' amplitude scaled
(AB_GAIN), beside the face as built and the two references at 1 m and 5 m, with both faces' spread and checks.

Beside the 1 m and 5 m views sit crops of two reference photographs (docs/references/stone/, in grey, cropped and
scaled with macOS sips): 05, the split fronts of the Aksla steps (Odd Roar Aalborg, CC BY-SA 4.0), at about 1 mm a
pixel, and 10, the dry-stone wall at Furulund (Frode H. Korneliussen, CC BY-SA 4.0), at about 4 to 5 mm a pixel. Both
scales are judged from the stones' sizes, not measured. The photographs carry lichen and colour the patches leave to
other layers: compare the form and the size of the marks, not the tone.

    python3.13 blender/tools/patch_sheet.py [out dir]      (default reviews/lt1/port/2b/r2a)
"""

import json
import math
import os
import shutil
import subprocess
import sys
import tempfile

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "blender", "parts", "stone", "slate"))
sys.path.insert(0, HERE)
import patches as PT  # noqa: E402
from golden_compare import write_png  # noqa: E402
from time_sheet import text  # noqa: E402

OUT = os.path.join(ROOT, "reviews", "lt1", "port", "2b", "r2a")
ELEV = math.radians(30.0)                      # the light's elevation above the face
AZ = math.radians(135.0)                       # from the upper left (u right, v up)
LIGHT = np.array([math.cos(ELEV) * math.cos(AZ), math.cos(ELEV) * math.sin(AZ), math.sin(ELEV)])
ALBEDO, AMBIENT, KEY = 0.30, 0.35, 1.6
VIEWS = (("1 m", 1), ("5 m", 5), ("12 m", 12))
THRESH = 4.0                                   # L* above (or below) its 3 x 3 opening (closing) that counts
THIN = (2.0, 2.0, 40)                          # thin long lines: L* over the opening, most width and least length, px
FLOAT = (1.0, 2.0, 10, 4)                      # floating lines: low and high L* (hysteresis), least length, length/width
STREAK = (3.0, 40, 6)                          # streaks: L* over the 5 x 5 opening, least length, length over width
REPEAT_LOBE = (30.0, 20.0)                     # the autocorrelation's central lobe left out, mm along u and across
REPEAT_WIN = 256                               # the local repeat's windows, mm
AB_PATCH, AB_GAIN = "split-2", 2.0             # the A/B on the spread limit: this face, its facets this many times
REFS = os.path.join(ROOT, "docs", "references", "stone")
# (file, crop x, y, w, h in the original's pixels, shown size, label): scales judged from the stones' sizes
REF_1M = ("05-aksla-old-split-stone-steps.jpg", 896, 1079, 1024, 1024, 1024,
          "REF 05 AKSLA STEP FRONTS, ABOUT 1 MM A PX (AALBORG, CC BY-SA 4.0)")
REF_5M = ("10-bergen-dry-stone-wall-and-bedrock.jpg", 1715, 830, 205, 205, 205,
          "REF 10 FURULUND WALL, ABOUT 4-5 MM A PX (KORNELIUSSEN, CC BY-SA 4.0)")


def srgb(lin):
    lin = np.clip(lin, 0, 1)
    return np.where(lin <= 0.0031308, 12.92 * lin, 1.055 * lin ** (1 / 2.4) - 0.055)


def lstar(lin):
    y = np.clip(lin, 0, None)
    f = np.where(y > (6 / 29) ** 3, np.cbrt(y), y / (3 * (6 / 29) ** 2) + 4 / 29)
    return 116 * f - 16


def gauss_lowpass(a, sigma):
    """A periodic Gaussian low-pass (sigma in texels), by FFT on the torus."""
    if sigma <= 0:
        return a
    f = np.fft.fftfreq(a.shape[0])
    g = np.exp(-2 * (math.pi * sigma) ** 2 * (f[:, None] ** 2 + f[None, :] ** 2))
    return np.real(np.fft.ifft2(np.fft.fft2(a) * g))


def box(a, k):
    h, w = a.shape[0] // k * k, a.shape[1] // k * k
    return a[:h, :w].reshape(h // k, k, w // k, k).mean(axis=(1, 3))


def shade(nrm, mult):
    ndl = np.clip(nrm @ LIGHT, 0, None)
    return ALBEDO * mult * (AMBIENT + KEY * ndl)


def view(h, n, v, mm):
    """The linear radiance of a patch seen at mm a pixel."""
    if mm == 1:
        return shade(n, v)
    hl = gauss_lowpass(h, mm)
    vl = gauss_lowpass(v, mm)
    lin = shade(PT.normals(hl), vl)
    return box(lin, mm)


# -- morphology and pieces, numpy only ---------------------------------------------------------------------------------

def _stack(a, r):
    p = np.pad(a, r, mode="edge")
    H, W = a.shape
    return [p[r + dy:r + dy + H, r + dx:r + dx + W] for dy in range(-r, r + 1) for dx in range(-r, r + 1)]


def erode(a, r=1):
    return np.minimum.reduce(_stack(a, r))


def dilate(a, r=1):
    return np.maximum.reduce(_stack(a, r))


def pieces(mask):
    """8-connected pieces of a boolean mask: a list of (ys, xs) arrays (union-find over the set pixels)."""
    ys, xs = np.nonzero(mask)
    if len(ys) == 0:
        return []
    idx = -np.ones(mask.shape, np.int64)
    idx[ys, xs] = np.arange(len(ys))
    parent = np.arange(len(ys))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i
    H, W = mask.shape
    for dy, dx in ((0, 1), (1, -1), (1, 0), (1, 1)):
        y2, x2 = ys + dy, xs + dx
        ok = (y2 >= 0) & (y2 < H) & (x2 >= 0) & (x2 < W)
        a = np.nonzero(ok)[0]
        b = idx[y2[a], x2[a]]
        keep = b >= 0
        for i, j in zip(a[keep], b[keep]):
            ri, rj = find(i), find(j)
            if ri != rj:
                parent[ri] = rj
    roots = np.array([find(i) for i in range(len(ys))])
    out = []
    for r in np.unique(roots):
        m = roots == r
        out.append((ys[m], xs[m]))
    return out


def shape_of(ys, xs):
    """Length and width of a piece from its second moments."""
    if len(ys) < 2:
        return 1.0, 1.0
    c = np.cov(np.stack([xs, ys]).astype(np.float64))
    ev = np.sort(np.linalg.eigvalsh(c))[::-1]
    length = max(np.ptp(xs), np.ptp(ys)) + 1.0
    width = len(ys) / length
    return length, max(width, math.sqrt(max(ev[1], 0)) * 2)


def lines_and_specks(L):
    """One-pixel lines and specks in an L* image."""
    res = {}
    for kind, top in (("bright", L - dilate(erode(L))), ("dark", erode(dilate(L)) - L)):
        n_lines, longest = 0, 0.0
        for ys, xs in pieces(top > THRESH):
            length, width = shape_of(ys, xs)
            if length >= 10 and length >= 4 * width:
                n_lines += 1
                longest = max(longest, length)
        res[f"{kind}_lines"] = n_lines
        res[f"{kind}_longest_px"] = longest
        n_thin = 0
        for ys, xs in pieces(top > THIN[0]):
            length, width = shape_of(ys, xs)
            if width <= THIN[1] and length > THIN[2]:
                n_thin += 1
        res[f"{kind}_thin_long"] = n_thin
    for kind, top in (("bright", L - dilate(erode(L, 2), 2)), ("dark", erode(dilate(L, 2), 2) - L)):
        n, longest = 0, 0.0
        for ys, xs in pieces(top > STREAK[0]):
            length, width = shape_of(ys, xs)
            if length > STREAK[1] and length >= STREAK[2] * width:
                n += 1
                longest = max(longest, length)
        res[f"{kind}_streaks"] = n
        res[f"{kind}_streak_longest_px"] = longest
    med = np.median(np.stack(_stack(L, 2)), axis=0)
    mad = np.median(np.abs(np.stack(_stack(L, 2)) - med), axis=0)
    for kind, diff in (("bright", L - med), ("dark", med - L)):
        cand = (diff > np.maximum(3 * 1.4826 * mad, THRESH))
        n = 0
        for ys, xs in pieces(cand):
            if np.ptp(ys) < 2 and np.ptp(xs) < 2:
                n += 1
        res[f"{kind}_specks"] = n
    return res


def torus_pieces(mask):
    """8-connected pieces of a boolean mask on the torus (it wraps at all four edges): a label per set pixel (the least
    flat index in its piece), by min-label passes with pointer jumping; -1 elsewhere."""
    H, W = mask.shape
    big = H * W
    lab = np.where(mask, np.arange(big).reshape(H, W), big)
    while True:
        m = lab.copy()
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                if dy or dx:
                    m = np.minimum(m, np.roll(lab, (dy, dx), axis=(0, 1)))
        m = np.where(mask, m, big)
        flat = m.ravel()
        sel = np.nonzero(flat < big)[0]
        for _ in range(4):
            flat[sel] = np.minimum(flat[sel], flat[flat[sel]])
        if np.array_equal(m, lab):
            break
        lab = m
    return np.where(mask, lab, -1)


def floating_lines(L):
    """Lines that start or end inside the patch, both polarities: see the module's note. Returns (floating, through)
    counts and the longest floating piece in px."""
    H, W = L.shape
    floating, through, longest = 0, 0, 0.0

    def erode_w(a, r):
        p = np.pad(a, r, mode="wrap")
        return np.minimum.reduce([p[r + dy:r + dy + H, r + dx:r + dx + W] for dy in range(-r, r + 1)
                                  for dx in range(-r, r + 1)])

    def opening(a, r):
        return -erode_w(-erode_w(a, r), r)

    def closing(a, r):
        return erode_w(-erode_w(-a, r), r)
    for top in (np.maximum(L - opening(L, 1), L - opening(L, 2)), np.maximum(closing(L, 1) - L, closing(L, 2) - L)):
        mask = top > FLOAT[0]
        if not mask.any():
            continue
        lab = torus_pieces(erode_w(-erode_w(-mask.astype(np.float64), 1), 1) > 0.5)    # gaps of a px or two bridged
        ys, xs = np.nonzero(mask)
        uniq, inv = np.unique(lab[mask], return_inverse=True)
        area = np.bincount(inv).astype(np.float64)
        peak = np.zeros(len(uniq))
        np.maximum.at(peak, inv, top[mask])
        ncols = np.bincount(np.unique(inv * W + xs) // W, minlength=len(uniq))
        nrows = np.bincount(np.unique(inv * H + ys) // H, minlength=len(uniq))
        length = np.maximum(ncols, nrows).astype(np.float64)
        width = area / length
        line = (peak > FLOAT[1]) & (length > FLOAT[2]) & (length >= FLOAT[3] * width)
        across = (ncols >= W) | (nrows >= H)
        floating += int((line & ~across).sum())
        through += int((line & across).sum())
        if (line & ~across).any():
            longest = max(longest, float(length[line & ~across].max()))
    return floating, through, longest


def busyness(L):
    """Done 5's measure on L*: edge density (Sobel over 10 L* a pixel) and the high-frequency share of the variance."""
    p = np.pad(L, 1, mode="wrap")
    gx = (p[:-2, 2:] + 2 * p[1:-1, 2:] + p[2:, 2:]) - (p[:-2, :-2] + 2 * p[1:-1, :-2] + p[2:, :-2])
    gy = (p[2:, :-2] + 2 * p[2:, 1:-1] + p[2:, 2:]) - (p[:-2, :-2] + 2 * p[:-2, 1:-1] + p[:-2, 2:])
    mag = np.hypot(gx, gy) / 8.0
    hf = L - gauss_lowpass(L, 2.0)
    return float((mag > 10.0).mean()), float(hf.var() / max(L.var(), 1e-9))


def ledge_traces(h, boundaries, ledge, down=1):
    """Each ledge's trace and depth as the stored height shows them (see the module's note): boundaries (n, N) and the
    ledge flags from the generator only say where to look, within 30 mm up-dip and 40 mm down-dip of the boundary.
    down: +1 where down-dip is down the image (every split face; a bed face by its drawn scarp), -1 where it is up."""
    N = PT.N
    cols = np.arange(N)
    g = (np.roll(h, -1, 0) - np.roll(h, 1, 0)) * 0.5 * down                     # rising down-dip
    g = sum(np.roll(g, k, 0) for k in range(-2, 3)) / 5.0                       # over 5 mm
    out = []
    for k, flag in enumerate(ledge):
        if not flag:
            continue
        r0 = np.round(boundaries[k]).astype(np.int64)
        offs = np.arange(-30, 41) * down
        G = g[(r0[None, :] + offs[:, None]) % N, cols[None, :]]
        # The break's slope is nearly even across its middle, so its steepest row alone wanders with the fine tooth;
        # its middle is the centroid of the run around the steepest row that falls at least half as fast.
        i = np.argmin(G, axis=0)
        half = 0.5 * G[i, cols]
        wgt = np.zeros_like(G)
        wgt[i, cols] = half - G[i, cols]
        for step in (1, -1):
            on = np.ones(N, dtype=bool)
            j = i.copy()
            while on.any():
                j = j + step
                on &= (j >= 0) & (j < len(offs))
                jj = np.clip(j, 0, len(offs) - 1)
                on &= G[jj, cols] < half
                wgt[jj[on], cols[on]] = (half - G[jj, cols])[on]
        y = r0 + down * (wgt * np.arange(-30, 41)[:, None]).sum(axis=0) / wgt.sum(axis=0)   # rows, unwrapped
        yi = np.round(y).astype(np.int64)
        up = h[(yi[None, :] - down * np.arange(0, 36)[:, None]) % N, cols[None, :]].max(axis=0)
        dn = h[(yi[None, :] + down * np.arange(0, 36)[:, None]) % N, cols[None, :]].min(axis=0)
        depth = up - dn
        fit = np.polyval(np.polyfit(cols, y, 1), cols)
        res = y - fit
        ys = PT.box1(PT.box1(y - y.mean(), 17), 17)                              # the trace over about 33 mm
        ang = np.degrees(np.arctan((np.roll(ys, -8) - np.roll(ys, 8)) / 16.0))
        out.append({"boundary": int(k), "mean_row_mm": round(float(y.mean() % N), 1),
                    "straight_dev_mm": {"range": round(float(res.max() - res.min()), 2),
                                        "rms": round(float(res.std()), 2)},
                    "angle_deg": {"p2": round(float(np.percentile(ang, 2)), 2),
                                  "p98": round(float(np.percentile(ang, 98)), 2),
                                  "most": round(float(np.abs(ang).max()), 2)},
                    "depth_mm": {"p5": round(float(np.percentile(depth, 5)), 2),
                                 "p50": round(float(np.percentile(depth, 50)), 2),
                                 "p95": round(float(np.percentile(depth, 95)), 2),
                                 "swell_p95_over_p5": round(float(np.percentile(depth, 95) / max(np.percentile(depth, 5),
                                                                                                  1e-6)), 2)}})
    return out


def spacing(faces):
    """The set's spacing: faces is {name: (bands, [ledge mean rows, mm])}. Per face its ledges, bands, gaps and the
    widest over the narrowest; across the set the gaps' coefficient of variation, and side by side the most, over
    pairs, of one face's ledges with a ledge of the other within 25 mm (in rows on the torus)."""
    N = PT.N
    per, gaps_all = {}, []
    for name, (bands, rows) in faces.items():
        r = sorted(rows)
        gaps = [round((r[(i + 1) % len(r)] - r[i]) % N if len(r) > 1 else N, 1) for i in range(len(r))]
        gaps_all += gaps
        per[name] = {"ledges": len(r), "bands": bands, "ledge_rows_mm": [round(x, 1) for x in r], "gaps_mm": gaps,
                     "widest_over_narrowest": round(max(gaps) / min(gaps), 2)}
    names = list(faces)
    aligned = []
    for a in names:
        for b in names:
            if a == b:
                continue
            ra, rb = np.array(faces[a][1]), np.array(faces[b][1])
            d = np.abs((ra[:, None] - rb[None, :] + N / 2) % N - N / 2).min(axis=1)
            aligned.append((float((d <= 25.0).mean()), a, b))
    worst = max(aligned)
    g = np.array(gaps_all)
    return {"faces": per, "gaps_cv": round(float(g.std() / g.mean()), 3),
            "gaps_mm_range": [round(float(g.min()), 1), round(float(g.max()), 1)],
            "side_by_side_aligned_most": {"share": round(worst[0], 2), "of": worst[1], "with": worst[2]}}


def _peaks(ac, d, reach):
    """The autocorrelation's highest local maximum (over a 9 x 9 neighbourhood) outside its central lobe and within
    reach (mm along u and across), and where; 0 where it has none."""
    out = ((d[None, :] / REPEAT_LOBE[0]) ** 2 + (d[:, None] / REPEAT_LOBE[1]) ** 2 >= 1.0) & \
        (np.abs(d[None, :]) <= reach[0]) & (np.abs(d[:, None]) <= reach[1])
    mx = ac.copy()
    for dy in range(-4, 5):
        for dx in range(-4, 5):
            if dx or dy:
                mx = np.maximum(mx, np.roll(np.roll(ac, dy, 0), dx, 1))
    m = np.where((ac >= mx) & out, ac, -np.inf)
    i = np.unravel_index(np.argmax(m), m.shape)
    if not np.isfinite(m[i]):
        return 0.0, 0, 0                                                         # no peak: it falls away throughout
    return float(m[i]), int(d[i[1]]), int(-d[i[0]])


def repeat_peak(a, win=REPEAT_WIN):
    """How much a map repeats itself. Across the whole torus: the highest local peak of its autocorrelation outside
    the central lobe (REPEAT_LOBE), and where; a strict lattice peaks at its cell. Locally: the same in each window
    of win mm (Hann-tapered, padded), its mean and most over the windows; a lattice bent along the face loses its
    peaks across the torus but keeps them in rows a cell or two long, which is what the eye catches."""
    N = a.shape[0]
    z = a - a.mean()
    F = np.fft.fft2(z)
    ac = np.real(np.fft.ifft2(F * np.conj(F)))
    ac /= ac[0, 0]
    d = (np.arange(N) + N // 2) % N - N // 2
    g, gu, gv = _peaks(ac, d, (N // 2, N // 2))
    taper = np.outer(np.hanning(win), np.hanning(win))
    dw = (np.arange(2 * win) + win) % (2 * win) - win
    loc = []
    for y0 in range(0, N, win):
        for x0 in range(0, N, win):
            w = a[y0:y0 + win, x0:x0 + win]
            w = (w - w.mean()) * taper
            Fw = np.fft.fft2(w, s=(2 * win, 2 * win))
            acw = np.real(np.fft.ifft2(np.abs(Fw) ** 2))
            acw /= acw[0, 0]
            loc.append(_peaks(acw, dw, (win // 2, win // 2))[0])
    return {"torus_peak": round(g, 3), "torus_at_du_dv_mm": [gu, gv],
            "local_peak_mean": round(float(np.mean(loc)), 3), "local_peak_most": round(float(np.max(loc)), 3)}


def fold_map(f):
    """The facets' folds: the magnitude of their Laplacian, on the torus."""
    return np.abs(np.roll(f, 1, 0) + np.roll(f, -1, 0) + np.roll(f, 1, 1) + np.roll(f, -1, 1) - 4.0 * f)


def bandpass(L, lo=2.0, hi=40.0):
    return gauss_lowpass(L, lo) - gauss_lowpass(L, hi)


# -- the sheet ----------------------------------------------------------------------------------------------------------

def grey(img):
    return np.repeat(img[..., None], 3, axis=2)


def enlarge(a, k):
    return np.repeat(np.repeat(a, k, axis=0), k, axis=1)


def place(canvas, img, x, y):
    canvas[y:y + img.shape[0], x:x + img.shape[1]] = grey(img) if img.ndim == 2 else img


def histogram_panel(h, v, w=900, hgt=260):
    """The relief's histogram (mm, 0.25 mm bins) and the value's (multiplier, 0.002 bins), as bars."""
    pan = np.full((2 * hgt + 60, w, 3), 0.12)
    for row, (data, lo, hi, step, label, ticks) in enumerate((
            (h, -14.0, 8.0, 0.25, "RELIEF MM", (-12, -8, -4, 0, 4, 8)),
            (v, 0.90, 1.10, 0.002, "VALUE X", (0.92, 0.96, 1.00, 1.04, 1.08)))):
        bins = np.arange(lo, hi + step, step)
        cnt, _ = np.histogram(np.clip(data, lo, hi - 1e-9), bins)
        frac = cnt / cnt.sum()
        top = 30 + row * (hgt + 30)
        bw = (w - 40) / len(cnt)
        peak = max(frac.max(), 1e-9)
        for i, f in enumerate(frac):
            bh = int(round((hgt - 50) * math.sqrt(f / peak)))   # square-root scale, so the tails show
            x0 = int(20 + i * bw)
            pan[top + hgt - 30 - bh:top + hgt - 30, x0:max(x0 + 1, int(20 + (i + 1) * bw) - 1)] = 0.75
        for tk in ticks:
            x = int(20 + (tk - lo) / (hi - lo) * (w - 40))
            pan[top + hgt - 30:top + hgt - 24, x] = 1.0
            text(pan, f"{tk:g}", x - 12, top + hgt - 22, scale=2, bg=(0.12, 0.12, 0.12))
        text(pan, label + " (SQRT SCALE)", 20, top - 22, scale=2, bg=(0.12, 0.12, 0.12))
    return pan


def read_bmp(path):
    """An uncompressed 24- or 32-bit BMP as (h, w, 3) floats in [0, 1], top row first."""
    b = open(path, "rb").read()
    off = int.from_bytes(b[10:14], "little")
    w = int.from_bytes(b[18:22], "little", signed=True)
    h = int.from_bytes(b[22:26], "little", signed=True)
    bpp = int.from_bytes(b[28:30], "little")
    stride = (w * bpp // 8 + 3) // 4 * 4
    a = np.frombuffer(b, np.uint8, count=stride * abs(h), offset=off).reshape(abs(h), stride)
    a = a[:, :w * bpp // 8].reshape(abs(h), w, bpp // 8)[..., 2::-1].astype(np.float64) / 255.0   # BGR(A) to RGB
    return a if h < 0 else a[::-1]


def reference(spec):
    """A reference photograph's crop in grey (sRGB in [0, 1]), cropped and scaled with macOS sips; None without it."""
    name, x, y, w, h, size, _label = spec
    if shutil.which("sips") is None or not os.path.exists(os.path.join(REFS, name)):
        return None
    tmp = tempfile.mkdtemp()
    try:
        crop, bmp = os.path.join(tmp, "c.jpg"), os.path.join(tmp, "c.bmp")
        subprocess.run(["sips", "-c", str(h), str(w), "--cropOffset", str(y), str(x), os.path.join(REFS, name),
                        "--out", crop], check=True, capture_output=True)
        subprocess.run(["sips", "-z", str(size), str(size), "-s", "format", "bmp", crop, "--out", bmp], check=True,
                       capture_output=True)
        rgb = read_bmp(bmp)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    lin = np.where(rgb <= 0.04045, rgb / 12.92, ((rgb + 0.055) / 1.055) ** 2.4)
    return srgb(lin @ np.array([0.2126, 0.7152, 0.0722]))


def riser_steps(h, window=170, step_mm=2.0):
    """How many laminae steps a 170 mm riser shows: along columns every 16 mm, windows every 85 mm down, count the
    boundaries where the height falls or rises by step_mm or more within 6 mm (a broken edge), less one per pair of
    a pluck's two edges counted separately (they are marks too, so they stay counted)."""
    counts = []
    for c in range(0, PT.N, 16):
        col = h[:, c]
        d = np.roll(col, -6) - col
        big = np.abs(d) >= step_mm
        edges = big & ~np.roll(big, 1)
        for r in range(0, PT.N, 85):
            counts.append(int(np.take(edges, range(r, r + window), mode="wrap").sum()))
    counts = np.array(counts)
    return {"mean": float(counts.mean()), "p10": float(np.percentile(counts, 10)), "p90": float(np.percentile(counts, 90)),
            "max": int(counts.max())}


def seam(a):
    """The jump across the wrap over the mean step between neighbours inside (1.0: no seam), columns and rows."""
    inner_c = np.abs(np.diff(a, axis=1)).mean()
    wrap_c = np.abs(a[:, 0] - a[:, -1]).mean()
    inner_r = np.abs(np.diff(a, axis=0)).mean()
    wrap_r = np.abs(a[0, :] - a[-1, :]).mean()
    return float(wrap_c / inner_c), float(wrap_r / inner_r)


def view_checks(h, n, v):
    """Each view's spread and line checks, for the A/B."""
    res = {}
    for label, mm in VIEWS:
        L = lstar(view(h, n, v, mm))
        fl, th, _ = floating_lines(L)
        ls = lines_and_specks(L)
        res[label] = {"Lstar_spread_p5_p95": round(float(np.percentile(L, 95) - np.percentile(L, 5)), 2),
                      "floating_lines": fl, "through_lines": th,
                      "thin_long": ls["bright_thin_long"] + ls["dark_thin_long"],
                      "specks": ls["bright_specks"] + ls["dark_specks"]}
    return res


def ab_sheet(out, seed, ref1, ref5):
    """The A/B on the spread limit: AB_PATCH as built (A) and with its facets' amplitude times AB_GAIN (B, built in
    memory only), at 1 m beside reference 05 and at 5 m (x4) beside reference 10."""
    faces = {}
    for tag, gain in (("A", 1.0), ("B", AB_GAIN)):
        maps, params = PT.make(AB_PATCH, seed, facet_gain=gain)
        h, n, v = PT.decode(maps)
        faces[tag] = (h, n, v, params["facet_amp_mm"] * gain, view_checks(h, n, v))
    bg = (0.12, 0.12, 0.12)
    W = 12 + 3 * (1024 + 12)
    y2 = 40 + 1024 + 40
    can = np.full((y2 + 820 + 60, W, 3), 0.12)
    text(can, f"A/B ON THE SPREAD LIMIT: {AB_PATCH.upper()} AS BUILT (A) AND ITS FACETS X{AB_GAIN:g} (B), ONLY THE "
              "AMPLITUDE CHANGED; FLAT, GREY, RAKING LIGHT FROM UPPER LEFT", 12, 8, scale=2, bg=bg)
    for i, tag in enumerate(("A", "B")):
        h, n, v, amp, chk = faces[tag]
        x = 12 + i * (1024 + 12)
        place(can, srgb(view(h, n, v, 1)), x, 40)
        text(can, f"{tag}: FACETS {amp:.1f} MM, 1 M (1 MM A PX), SPREAD {chk['1 m']['Lstar_spread_p5_p95']:.2f} L-STAR",
             x + 4, 44, scale=2)
        place(can, enlarge(srgb(view(h, n, v, 5)), 4), x, y2)
        text(can, f"{tag}: 5 M X4, SPREAD {chk['5 m']['Lstar_spread_p5_p95']:.2f} L-STAR (SN7: ABOUT 2)", x + 4, y2 + 4,
             scale=2)
    x = 12 + 2 * (1024 + 12)
    if ref1 is not None:
        place(can, ref1, x, 40)
        text(can, REF_1M[6], x + 4, 44, scale=2)
    if ref5 is not None:
        place(can, enlarge(ref5, 4), x, y2)
        text(can, "REF 10, ABOUT 4-5 MM A PX, X4", x + 4, y2 + 4, scale=2)
    text(can, "REFERENCES IN GREY, SCALES JUDGED; COMPARE FORM AND MARK SIZE, NOT TONE (LICHEN)", 12, y2 + 820 + 20,
         scale=2, bg=bg)
    write_png(os.path.join(out, "patches-ab.png"), can)
    return {"patch": AB_PATCH, "facet_gain": AB_GAIN,
            "A": {"facet_amp_mm": round(faces["A"][3], 2), "views": faces["A"][4]},
            "B": {"facet_amp_mm": round(faces["B"][3], 2), "views": faces["B"][4]}}


def main(out=OUT):
    os.makedirs(out, exist_ok=True)
    manifest = json.load(open(PT.MANIFEST))
    report = {"light": {"elevation_deg": 30, "from": "upper left", "albedo": ALBEDO, "ambient": AMBIENT, "key": KEY},
              "threshold_Lstar": THRESH, "patches": {}}
    over_cells, tile_cells, hists = [], [], []
    seed = manifest["worldSeed"]
    rows_for_spacing = {}
    ref1, ref5 = reference(REF_1M), reference(REF_5M)
    report["references"] = {"1 m": REF_1M[6] if ref1 is not None else None, "5 m": REF_5M[6] if ref5 is not None else None}
    for name in PT.PATCHES:
        maps = {k: PT.read16(os.path.join(ROOT, f["file"])) for k, f in manifest["patches"][name]["files"].items()}
        for k, f in manifest["patches"][name]["files"].items():
            assert PT.pixel_hash(maps[k]) == f["pixels"], f"{name} {k}: the stored map differs from the manifest"
        h, n, v = PT.decode(maps)
        r = {"relief_mm": {q: float(np.percentile(h, p)) for q, p in (("p1", 1), ("p5", 5), ("p50", 50), ("p95", 95), ("p99", 99))},
             "value": {q: float(np.percentile(v, p)) for q, p in (("p1", 1), ("p5", 5), ("p50", 50), ("p95", 95), ("p99", 99))},
             "slope_deg": {q: float(np.degrees(np.arccos(np.clip(np.percentile(n[..., 2], p), -1, 1)))) for q, p in (("p50", 50), ("p95", 5), ("p99", 1))},
             "views": {}}
        r["relief_mm"]["range_p1_p99"] = r["relief_mm"]["p99"] - r["relief_mm"]["p1"]
        r["value"]["band_p5_p95"] = r["value"]["p95"] - r["value"]["p5"]
        if name.startswith("split"):
            r["riser_steps"] = riser_steps(h)
        imgs = {}
        for label, mm in VIEWS:
            lin = view(h, n, v, mm)
            L = lstar(lin)
            imgs[label] = srgb(lin)
            ed, hf = busyness(L)
            fl, th, fll = floating_lines(L)
            r["views"][label] = {"px": list(lin.shape), "Lstar_mean": float(L.mean()), "Lstar_sd": float(L.std()),
                                 "Lstar_p5_p95": [float(np.percentile(L, 5)), float(np.percentile(L, 95))],
                                 "Lstar_spread_p5_p95": float(np.percentile(L, 95) - np.percentile(L, 5)),
                                 "edge_density": ed, "hf_share": hf, "floating_lines": fl, "through_lines": th,
                                 "floating_longest_px": fll, **lines_and_specks(L)}
        lin1 = view(h, n, v, 1)
        eighth = srgb(box(lin1, 8))
        L8 = lstar(box(lin1, 8))
        ed8, hf8 = busyness(L8)
        r["views"]["eighth"] = {"px": list(L8.shape), "Lstar_sd": float(L8.std()), "edge_density": ed8, "hf_share": hf8}
        sh = seam(h)
        sl = seam(lstar(lin1))
        r["seam"] = {"height_cols": sh[0], "height_rows": sh[1], "Lstar_cols": sl[0], "Lstar_rows": sl[1]}
        lay = {}
        PT.make(name, seed, layers=lay)                                          # where to look; the maps above match
        drawn = manifest["patches"][name]["drawn"]
        down = 1 if name.startswith("split") or drawn["scarp"]["down_dip"] == "down" else -1
        r["ledges"] = ledge_traces(h, lay["boundaries"], lay["ledge"], down)
        if name.startswith("split"):
            rows_for_spacing[name] = (drawn["bands"], [x["mean_row_mm"] for x in r["ledges"]])
            r["lattice_repeat"] = {"facet_folds": repeat_peak(fold_map(lay["facets"])),
                                   "Lstar_1m_bandpass": repeat_peak(bandpass(lstar(lin1)))}
        report["patches"][name] = r
        print(name, json.dumps({k: r["views"][k].get("bright_lines") for k in ("1 m", "5 m", "12 m")}), flush=True)

        # the patch's own sheet: 1 m at full size beside reference 05; 5 m four times (nearest) beside reference 10;
        # 5 m, 12 m and one-eighth at native size; 12 m four times
        one = imgs["1 m"]
        five, twelve = imgs["5 m"], imgs["12 m"]
        bg = (0.12, 0.12, 0.12)
        W = 12 + 1024 + 12 + 1024 + 12
        y2 = 40 + 1024 + 16
        y3 = y2 + 820 + 16
        canvas = np.full((y3 + 340 + 12, W, 3), 0.12)
        text(canvas, f"{name.upper()}  FLAT, GREY, RAKING LIGHT FROM UPPER LEFT", 12, 8, scale=3, bg=bg)
        place(canvas, one, 12, 40)
        text(canvas, "1 M  (1 MM A PX, 1024 MM)", 16, 44, scale=2)
        if ref1 is not None:
            place(canvas, ref1, 12 + 1024 + 12, 40)
            text(canvas, REF_1M[6], 12 + 1024 + 16, 44, scale=2)
        else:
            text(canvas, "REF 05 UNAVAILABLE (NEEDS MACOS SIPS)", 12 + 1024 + 16, 44, scale=2)
        place(canvas, enlarge(five, 4), 12, y2)
        text(canvas, "5 M  X4 NEAREST", 16, y2 + 4, scale=2)
        if ref5 is not None:
            place(canvas, enlarge(ref5, 4), 12 + 820 + 12, y2)
            text(canvas, "REF 10, ABOUT 4-5 MM A PX, X4", 12 + 820 + 16, y2 + 4, scale=2)
        xn = 12 + 820 + 12 + 820 + 16
        yn = y2
        for img, label in ((five, "5 M"), (twelve, "12 M"), (eighth, "1/8")):
            place(canvas, img, xn, yn)
            text(canvas, label, xn, yn + img.shape[0] + 2, scale=2, bg=bg)
            yn += img.shape[0] + 30
        place(canvas, enlarge(twelve, 4), 12, y3)
        text(canvas, "12 M  X4 NEAREST", 16, y3 + 4, scale=2)
        if ref5 is not None:
            text(canvas, "REF 10: " + REF_5M[6][7:], 12 + 340 + 16, y3 + 4, scale=2, bg=bg)
        if ref1 is not None:
            text(canvas, "REF 05: " + REF_1M[6][7:], 12 + 340 + 16, y3 + 30, scale=2, bg=bg)
        text(canvas, "REFERENCES IN GREY, SCALES JUDGED; COMPARE FORM AND MARK SIZE, NOT TONE (LICHEN)", 12 + 340 + 16,
             y3 + 56, scale=2, bg=bg)
        write_png(os.path.join(out, f"patch-{name}.png"), canvas)

        # the overview's cells: 5 m, 12 m and one-eighth, native
        over_cells.append((name, five, twelve, eighth))
        # the tiling check: 2 x 2 repeats at 4 mm a pixel, and the seams' crossing at 1 mm
        two = np.tile(lin1, (2, 2))
        tile_cells.append((name, srgb(box(two, 4)), srgb(two[1024 - 160:1024 + 160, 1024 - 160:1024 + 160])))
        hists.append((name, histogram_panel(h, v)))

    report["spacing"] = spacing(rows_for_spacing)
    report["ab"] = ab_sheet(out, seed, ref1, ref5)

    # overview
    cw = 204 + 12 + 85 + 12 + 128 + 24
    ov = np.full((40 + (len(over_cells) + 1) * (204 + 34), cw, 3), 0.12)
    text(ov, "5 M, 12 M, 1/8, NATIVE", 8, 8, scale=2, bg=(0.12, 0.12, 0.12))
    for i, (name, five, twelve, eighth) in enumerate(over_cells):
        y = 40 + i * (204 + 34)
        text(ov, name.upper(), 8, y, scale=2, bg=(0.12, 0.12, 0.12))
        place(ov, five, 8, y + 22)
        place(ov, twelve, 8 + 204 + 12, y + 22)
        place(ov, eighth, 8 + 204 + 12 + 85 + 12, y + 22)
    if ref5 is not None:
        y = 40 + len(over_cells) * (204 + 34)
        text(ov, "REF 10 AT ABOUT 5 M (GREY)", 8, y, scale=2, bg=(0.12, 0.12, 0.12))
        place(ov, ref5[:204, :204], 8, y + 22)
    write_png(os.path.join(out, "patches-distances.png"), ov)
    # one-eighth thumbnails alone
    th = np.full((40 + 128 + 30, 8 + len(over_cells) * 140, 3), 0.12)
    text(th, "ONE-EIGHTH OF THE 1 M VIEW", 8, 8, scale=2, bg=(0.12, 0.12, 0.12))
    for i, (name, _, _, eighth) in enumerate(over_cells):
        place(th, eighth, 8 + i * 140, 36)
        text(th, name.upper(), 8 + i * 140, 36 + 132, scale=2, bg=(0.12, 0.12, 0.12))
    write_png(os.path.join(out, "patches-eighth.png"), th)
    # tiling
    tw = 512 + 12 + 320 + 24
    tl = np.full((2 * (512 + 40) + 40, 3 * tw + 12, 3), 0.12)
    text(tl, "2 X 2 REPEATS AT 4 MM A PX, AND THE SEAMS' CROSSING AT 1 MM A PX (SEAMS AT THE MIDDLE)", 8, 8, scale=2,
         bg=(0.12, 0.12, 0.12))
    for i, (name, two, cross) in enumerate(tile_cells):
        x, y = 12 + (i % 3) * tw, 40 + (i // 3) * (512 + 40)
        text(tl, name.upper(), x, y, scale=2, bg=(0.12, 0.12, 0.12))
        place(tl, two, x, y + 22)
        place(tl, cross, x + 512 + 12, y + 22)
    write_png(os.path.join(out, "patches-tiling.png"), tl)
    # histograms
    hw = hists[0][1].shape[1]
    hh = hists[0][1].shape[0]
    hg = np.full((2 * (hh + 30) + 20, 3 * (hw + 12) + 12, 3), 0.12)
    for i, (name, pan) in enumerate(hists):
        x, y = 12 + (i % 3) * (hw + 12), 10 + (i // 3) * (hh + 30)
        text(hg, name.upper(), x, y, scale=2, bg=(0.12, 0.12, 0.12))
        place(hg, pan, x, y + 24)
    write_png(os.path.join(out, "patches-histograms.png"), hg)
    with open(os.path.join(out, "checks.json"), "w") as f:
        json.dump(report, f, indent=1)
        f.write("\n")
    return report


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else OUT)
