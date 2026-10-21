"""Sheets, reader packs and the ways of showing time for the corner through the years (docs/experiments.md, LT1f).

    blender -b --factory-startup --python blender/tools/time_sheet.py -- <command> [options]

Commands (frames from LT1Time.Frames and LT1Time.Masks under reviews/lt1/time/frames):
- strips:  each view's four years side by side, dated, at a third of the size (reviews/lt1/time/sheets/).
- pack <arm> <out>: the cold readers' material: every frame as four tiles at the player's pixel size plus the whole
  frame at half size, under codes that hide the year; codes.json says which is which (kept for the scorer, never
  given to readers); and a locator, the city view with the five houses lettered.
- toggle:  the toggle in place, as an animated PNG per view and pair of years (the years flip, nothing between).
- strokes: repainted stroke by stroke in the order things happened: per view, from 1989 to 2020, each recorded change
  brushed in over its house, in date order, dated; an animated PNG and a strip of its steps.
- window:  a window into another year: the present with a pane, or a photograph held at its spot, showing the earlier
  year exactly where it was, over a house the record changed.

Images are read and written as 8-bit PNG through numpy (golden_compare.read_png and write_png); animated PNGs are
written by hand (APNG), since no other image tool is installed. Text is a small bitmap font, drawn here.
"""

import json
import os
import struct
import sys
import zlib

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)

from golden_compare import read_png, write_png, shrink  # noqa: E402

TIME = os.path.join(ROOT, "reviews", "lt1", "time")
FRAMES = os.path.join(TIME, "frames")
YEARS = (1989, 2000, 2010, 2020)
VIEWS = ("eye", "street", "12m", "city")
LETTERS = "ABCDE"

# -- a small bitmap font --------------------------------------------------------------------------------------------

GLYPHS = {
    "0": "01110 10001 10011 10101 11001 10001 01110", "1": "00100 01100 00100 00100 00100 00100 01110",
    "2": "01110 10001 00001 00010 00100 01000 11111", "3": "11110 00001 00001 01110 00001 00001 11110",
    "4": "00010 00110 01010 10010 11111 00010 00010", "5": "11111 10000 11110 00001 00001 10001 01110",
    "6": "00110 01000 10000 11110 10001 10001 01110", "7": "11111 00001 00010 00100 01000 01000 01000",
    "8": "01110 10001 10001 01110 10001 10001 01110", "9": "01110 10001 10001 01111 00001 00010 01100",
    "A": "01110 10001 10001 11111 10001 10001 10001", "B": "11110 10001 10001 11110 10001 10001 11110",
    "C": "01110 10001 10000 10000 10000 10001 01110", "D": "11100 10010 10001 10001 10001 10010 11100",
    "E": "11111 10000 10000 11110 10000 10000 11111", "F": "11111 10000 10000 11110 10000 10000 10000",
    "G": "01110 10001 10000 10111 10001 10001 01111", "H": "10001 10001 10001 11111 10001 10001 10001",
    "I": "01110 00100 00100 00100 00100 00100 01110", "J": "00111 00010 00010 00010 00010 10010 01100",
    "K": "10001 10010 10100 11000 10100 10010 10001", "L": "10000 10000 10000 10000 10000 10000 11111",
    "M": "10001 11011 10101 10101 10001 10001 10001", "N": "10001 10001 11001 10101 10011 10001 10001",
    "O": "01110 10001 10001 10001 10001 10001 01110", "P": "11110 10001 10001 11110 10000 10000 10000",
    "Q": "01110 10001 10001 10001 10101 10010 01101", "R": "11110 10001 10001 11110 10100 10010 10001",
    "S": "01111 10000 10000 01110 00001 00001 11110", "T": "11111 00100 00100 00100 00100 00100 00100",
    "U": "10001 10001 10001 10001 10001 10001 01110", "V": "10001 10001 10001 10001 10001 01010 00100",
    "W": "10001 10001 10001 10101 10101 10101 01010", "X": "10001 10001 01010 00100 01010 10001 10001",
    "Y": "10001 10001 01010 00100 00100 00100 00100", "Z": "11111 00001 00010 00100 01000 10000 11111",
    " ": "00000 00000 00000 00000 00000 00000 00000", "-": "00000 00000 00000 11111 00000 00000 00000",
    ":": "00000 01100 01100 00000 01100 01100 00000", ".": "00000 00000 00000 00000 00000 01100 01100",
    "/": "00001 00010 00010 00100 01000 01000 10000", ">": "01000 00100 00010 00001 00010 00100 01000",
    ",": "00000 00000 00000 00000 01100 00100 01000", "'": "00100 00100 01000 00000 00000 00000 00000",
    "(": "00010 00100 01000 01000 01000 00100 00010", ")": "01000 00100 00010 00010 00010 00100 01000",
}


def text(img, s, x, y, scale=4, fg=(1.0, 1.0, 1.0), bg=(0.08, 0.08, 0.1), pad=None):
    """Writes s at (x, y) (top left) on a plate of bg, in place. Returns the plate's width and height."""
    s = s.upper()
    pad = scale * 2 if pad is None else pad
    w = len(s) * 6 * scale - scale + 2 * pad
    h = 7 * scale + 2 * pad
    H, W = img.shape[:2]
    x0, y0 = max(0, min(W - w, x)), max(0, min(H - h, y))
    img[y0:y0 + h, x0:x0 + w] = bg
    for i, ch in enumerate(s):
        rows = GLYPHS.get(ch, GLYPHS[" "]).split()
        for r, row in enumerate(rows):
            for c, bit in enumerate(row):
                if bit == "1":
                    yy, xx = y0 + pad + r * scale, x0 + pad + (i * 6 + c) * scale
                    img[yy:yy + scale, xx:xx + scale] = fg
    return w, h


# -- reading the frames ---------------------------------------------------------------------------------------------


def frame(arm, view, year):
    return read_png(os.path.join(FRAMES, arm, f"{view}-{year}.png"))


def mask(arm, view, year, letter):
    """A house's own pixels in a view (LT1Time.Masks: the house white, everything else black, occlusion kept)."""
    m = read_png(os.path.join(FRAMES, "masks", arm, f"{view}-{year}-{letter}.png")).mean(axis=2)
    lo, hi = float(m.min()), float(m.max())
    return m > (lo + hi) / 2 if hi - lo > 0.05 else np.zeros(m.shape, bool)


def labels():
    return json.load(open(os.path.join(FRAMES, "frames.json")))["frames"]


def apng(path, frames, delays_ms):
    """An animated PNG (every frame full size, 8-bit RGB). Plays in browsers and in macOS Quick Look."""
    def chunk(t, d):
        return struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t + d) & 0xFFFFFFFF)

    h, w, _ = frames[0].shape
    out = [b"\x89PNG\r\n\x1a\n", chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)),
           chunk(b"acTL", struct.pack(">II", len(frames), 0))]
    seq = 0
    for i, (f, d) in enumerate(zip(frames, delays_ms)):
        rgb = np.clip(np.round(f * 255.0), 0, 255).astype(np.uint8) if f.dtype != np.uint8 else f
        raw = np.zeros((h, 1 + w * 3), np.uint8)
        raw[:, 1:] = rgb.reshape(h, w * 3)
        data = zlib.compress(raw.tobytes(), 6)
        out.append(chunk(b"fcTL", struct.pack(">IIIIIHHBB", seq, w, h, 0, 0, int(d), 1000, 0, 0)))
        seq += 1
        if i == 0:
            out.append(chunk(b"IDAT", data))
        else:
            out.append(chunk(b"fdAT", struct.pack(">I", seq) + data))
            seq += 1
    out.append(chunk(b"IEND", b""))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as fh:
        fh.write(b"".join(out))


def half(img):
    return shrink(img, 2)


# -- the years strip ------------------------------------------------------------------------------------------------


def strips(arm="real"):
    out = os.path.join(TIME, "sheets")
    rows = []
    for view in VIEWS:
        cells = []
        for year in YEARS:
            f = shrink(frame(arm, view, year), 3)
            text(f, str(year), 12, 12, scale=4)
            cells.append(f)
        gap = np.full((cells[0].shape[0], 8, 3), 0.12)
        row = np.concatenate(sum([[c, gap] for c in cells], [])[:-1], axis=1)
        text(row, view, 12, row.shape[0] - 60, scale=4, bg=(0.3, 0.12, 0.1))
        rows.append(row)
        write_png(os.path.join(out, f"strip-{arm}-{view}.png"), row)
    gap = np.full((8, rows[0].shape[1], 3), 0.12)
    sheet = np.concatenate(sum([[r, gap] for r in rows], [])[:-1], axis=0)
    write_png(os.path.join(out, f"strips-{arm}.png"), shrink(sheet, 2))
    print("strips", arm)


# -- the readers' pack ----------------------------------------------------------------------------------------------


def pack(arm, out):
    """Every frame as an overview (half size) and four tiles at full size, under codes that hide the year."""
    rng = np.random.default_rng(1989 if arm == "real" else 2020)
    codes = {}
    for view in VIEWS:
        letters = list("WXYZ")
        order = rng.permutation(len(YEARS))
        for code_i, yi in enumerate(order):
            year = YEARS[yi]
            code = f"{view}-{letters[code_i]}"
            codes[code] = dict(view=view, year=year)
            f = frame(arm, view, year)
            d = os.path.join(out, "frames")
            write_png(os.path.join(d, f"{code}-whole.png"), half(f))
            H, W = f.shape[:2]
            for ti, (y0, x0) in enumerate(((0, 0), (0, W // 2), (H // 2, 0), (H // 2, W // 2))):
                write_png(os.path.join(d, f"{code}-tile{ti + 1}.png"), f[y0:y0 + H // 2, x0:x0 + W // 2])
    with open(os.path.join(out, "codes.json"), "w") as fh:
        json.dump(codes, fh, indent=1, sort_keys=True)
    # the locators: each view with the houses lettered where they are seen (their own pixels, from the masks), the
    # letter just above the visible part of each house; a house hidden in a view gets no letter there
    for view, year in (("city", 2020), ("eye", 1989), ("street", 1989), ("12m", 1989)):
        img = frame(arm, view, year).copy()
        for letter in LETTERS:
            m = mask(arm, view, year, letter)
            if m.sum() < 3000:
                continue
            ys, xs = np.nonzero(m)
            x = int(np.median(xs))
            top = int(np.percentile(ys[np.abs(xs - x) < 40], 2)) if (np.abs(xs - x) < 40).any() else int(ys.min())
            text(img, letter, x - 28, max(0, top - 110), scale=8, bg=(0.65, 0.1, 0.08))
        write_png(os.path.join(out, f"locator-{view}.png"), half(img))
    print("pack", arm, out, len(codes), "frames")


# -- the toggle in place --------------------------------------------------------------------------------------------


def toggle():
    out = os.path.join(TIME, "ways", "toggle")
    for view in VIEWS:
        for t0, t1 in zip(YEARS, YEARS[1:]):
            a, b = half(frame("real", view, t0)), half(frame("real", view, t1))
            for img, y in ((a, t0), (b, t1)):
                text(img, str(y), 16, 16, scale=5)
            apng(os.path.join(out, f"toggle-{view}-{t0}-{t1}.png"), [a, b], [900, 900])
    print("toggle")


# -- repainted, stroke by stroke ------------------------------------------------------------------------------------


def _stroke_field(shape, seed, angle):
    """A painter's stroke order over the frame: low values are painted first. Long strokes along one direction, each
    with its own start, so a region fills in overlapping bands, not a straight wipe."""
    H, W = shape
    rng = np.random.default_rng(seed)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    ca, sa = np.cos(angle), np.sin(angle)
    along = (xx * ca + yy * sa) / max(H, W)
    across = (-xx * sa + yy * ca)
    band = np.floor(across / 26.0)  # strokes about 26 px wide at the player's size
    offs = rng.random(int(band.max() - band.min()) + 2).astype(np.float32)
    jitter = offs[(band - band.min()).astype(int)]
    wobble = 0.03 * np.sin(across / 9.0 + jitter * 6.28)
    return np.clip(0.55 * along + 0.45 * jitter + wobble, 0, None)


def _dilate(m, r):
    out = m.copy()
    for _ in range(r):
        o = out.copy()
        o[1:] |= out[:-1]
        o[:-1] |= out[1:]
        o[:, 1:] |= out[:, :-1]
        o[:, :-1] |= out[:, 1:]
        out = o
    return out


def strokes(scale=4, steps=6, frames_dir=None, out=None):
    """From 1989 to 2020 in one view: each change the record draws, in date order, brushed in over its house."""
    key = json.load(open(os.path.join(TIME, "readers", "key.json")))["real"]
    out = out or os.path.join(TIME, "ways", "strokes")
    for view in VIEWS:
        canvas = shrink(frame("real", view, YEARS[0]), scale)
        text(canvas, str(YEARS[0]), 16, 16, scale=5)
        seq, delays, keyframes = [canvas.copy()], [1400], [canvas.copy()]
        canvas = shrink(frame("real", view, YEARS[0]), scale)
        for t0, t1 in zip(YEARS, YEARS[1:]):
            target = shrink(frame("real", view, t1), scale)
            pair = f"{t0}-{t1}"
            events = []
            for letter in LETTERS:
                drawn = [c for c in key["houses"][letter]["changes"][pair] if c["drawn"]]
                if drawn:
                    events.append((drawn[0]["year"], letter))
            events.sort()
            done = np.zeros(canvas.shape[:2], bool)
            for n, (year, letter) in enumerate(events):
                m = mask("real", view, t0, letter) | mask("real", view, t1, letter)
                m = shrink(m[..., None].astype(np.float32), scale)[..., 0] > 0.2
                if not m.any():
                    continue  # the house is not in this view
                m = _dilate(m, 6)
                field = _stroke_field(m.shape, zlib.crc32(f"{view}-{letter}-{year}".encode()) % 1000, 0.5 + 0.7 * (n % 2))
                lo, hi = np.percentile(field[m], [0, 100])
                ys, xs = np.nonzero(m)
                for k in range(1, steps + 1):
                    cut = lo + (hi - lo) * k / steps
                    paint = m & (field <= cut)
                    canvas[paint] = target[paint]
                    shown = canvas.copy()
                    text(shown, f"{year}  {letter}", int(xs.mean()) - 60, max(0, int(ys.min()) - 50), scale=4, bg=(0.65, 0.1, 0.08))
                    text(shown, str(year), 16, 16, scale=5)
                    seq.append(shown)
                    delays.append(70 if k < steps else 900)
                    if k == steps // 2:
                        keyframes.append(shown)  # the stroke half laid, for the sheet
                done |= m
                keyframes.append(seq[-1])
            # what the changes did beyond their houses (their shadows on the ground and on neighbours) settles last
            rest = ~done
            for k in (1, 2, 3):
                canvas[rest] = canvas[rest] + (target[rest] - canvas[rest]) * (k / 3)
                shown = canvas.copy()
                text(shown, str(t1), 16, 16, scale=5)
                seq.append(shown)
                delays.append(120 if k < 3 else 1600)
            keyframes.append(seq[-1])
        if frames_dir:  # each step on its own, for a reader
            for i, k in enumerate(keyframes):
                write_png(os.path.join(frames_dir, f"strokes-{view}-step{i + 1:02d}.png"), k)
            continue
        apng(os.path.join(out, f"strokes-{view}.png"), seq, delays)
        ks = [k for k in keyframes]
        cols = 4
        rows_ = []
        for r in range(0, len(ks), cols):
            row = ks[r:r + cols] + [np.zeros_like(ks[0])] * (cols - len(ks[r:r + cols]))
            rows_.append(np.concatenate(row, axis=1))
        write_png(os.path.join(out, f"strokes-{view}-steps.png"), np.concatenate(rows_, axis=0))
        print("strokes", view, len(seq), "frames")


# -- a window into another year ---------------------------------------------------------------------------------------


def window(view, now, then, letter, kind="pane", out_name=None):
    """The present, with the earlier year inside a pane (a soft-edged round window) or a photograph (a print with a
    white border, a little turned) held over one house, aligned to the pixel."""
    a, b = frame("real", view, now).copy(), frame("real", view, then)
    m = mask("real", view, now, letter) | mask("real", view, then, letter)
    # where on the house the two years differ: the record names the house; until each drawn pixel can name its part
    # (the building blocks' ids), the pixels of that house that changed stand in for the changed part
    region = _dilate(m, 4) & (np.abs(a - b).max(axis=2) > 3 / 255)
    if region.sum() < 200:
        region = m
    ys, xs = np.nonzero(region)
    cy, cx = int((ys.min() + ys.max()) / 2), int((xs.min() + xs.max()) / 2)
    H, W = a.shape[:2]
    yy, xx = np.mgrid[0:H, 0:W]
    if kind == "pane":
        r = min(int(max(ys.max() - ys.min(), xs.max() - xs.min()) * 0.6) + 60, int(0.24 * W))
        d = np.sqrt((yy - cy) ** 2 + (xx - cx) ** 2)
        inside = d < r
        a[inside] = b[inside]
        ring = (d >= r) & (d < r + 6)
        a[ring] = (0.95, 0.93, 0.88)
        text(a, str(then), cx - 60, cy - r - 70, scale=6)
    else:
        hw = min(int((xs.max() - xs.min()) * 0.6) + 60, int(0.22 * W))
        hh = min(int((ys.max() - ys.min()) * 0.6) + 50, int(0.3 * H))
        ang = np.radians(-4.0)
        u = (xx - cx) * np.cos(ang) + (yy - cy) * np.sin(ang)
        v = -(xx - cx) * np.sin(ang) + (yy - cy) * np.cos(ang)
        inner = (np.abs(u) < hw) & (np.abs(v) < hh)
        border = (np.abs(u) < hw + 28) & (np.abs(v) < hh + 28 + 40 * (v > 0)) & ~inner
        shadow = (np.abs(u - 14) < hw + 28) & (np.abs(v - 18) < hh + 68) & ~inner & ~border
        a[shadow] *= 0.6
        a[inner] = b[inner]
        a[border] = (0.94, 0.92, 0.86)
        text(a, str(then), cx - 60, cy + hh + 34, scale=5, fg=(0.15, 0.15, 0.15), bg=(0.94, 0.92, 0.86), pad=2)
    text(a, str(now), 16, 16, scale=5)
    name = out_name or f"window-{kind}-{view}-{letter}-{then}-in-{now}.png"
    write_png(os.path.join(TIME, "ways", "window", name), half(a))
    print("window", name)


def windows():
    key = json.load(open(os.path.join(TIME, "readers", "key.json")))["real"]
    for view in VIEWS:
        for t0, t1 in zip(YEARS, YEARS[1:]):
            for letter in LETTERS:
                if not any(c["drawn"] for c in key["houses"][letter]["changes"][f"{t0}-{t1}"]):
                    continue
                if not (mask("real", view, t0, letter).sum() > 4000):
                    continue
                window(view, t1, t0, letter, "pane")
                window(view, t1, t0, letter, "photo")


def main(argv):
    cmd = argv[0]
    if cmd == "strips":
        strips(argv[1] if len(argv) > 1 else "real")
    elif cmd == "pack":
        pack(argv[1], argv[2])
    elif cmd == "toggle":
        toggle()
    elif cmd == "strokes":
        strokes()
    elif cmd == "strokes-frames":
        strokes(scale=2, steps=6, frames_dir=argv[1])
    elif cmd == "window":
        windows()
    else:
        raise SystemExit(f"unknown command {cmd}")
    return 0


if __name__ == "__main__":
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
    sys.exit(main(argv))
