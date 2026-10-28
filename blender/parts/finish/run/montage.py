"""Lay crops side by side: Blender -b --factory-startup -P montage.py -- out spec [spec ...]
spec = path@x,y,w,h@scale (x, y from the top-left; scale resizes the crop, area-averaged down, bilinear up).
Rows split on a lone '/' spec."""
import sys
import numpy as np
import bpy

sys.path.insert(0, "/Users/oystein/code/Overstory/blender/parts/finish")


def read(path):
    im = bpy.data.images.load(path)
    w, h = im.size
    px = np.empty(w * h * 4, np.float32)
    im.pixels.foreach_get(px)
    bpy.data.images.remove(im)
    return px.reshape(h, w, 4)[::-1, :, :3].astype(np.float64)  # row 0 = top


def resize(a, s):
    if abs(s - 1) < 1e-6:
        return a
    h, w = a.shape[:2]
    nh, nw = max(1, int(round(h * s))), max(1, int(round(w * s)))
    if s < 1:
        ys = (np.arange(nh + 1) * h / nh).astype(int)
        xs = (np.arange(nw + 1) * w / nw).astype(int)
        c = np.cumsum(np.cumsum(np.pad(a, ((1, 0), (1, 0), (0, 0))), 0), 1)
        tot = c[ys[1:]][:, xs[1:]] - c[ys[:-1]][:, xs[1:]] - c[ys[1:]][:, xs[:-1]] + c[ys[:-1]][:, xs[:-1]]
        area = (ys[1:] - ys[:-1])[:, None, None] * (xs[1:] - xs[:-1])[None, :, None]
        return tot / area
    y = (np.arange(nh) + 0.5) / s - 0.5
    x = (np.arange(nw) + 0.5) / s - 0.5
    y0 = np.clip(np.floor(y).astype(int), 0, h - 2)
    x0 = np.clip(np.floor(x).astype(int), 0, w - 2)
    fy = np.clip(y - y0, 0, 1)[:, None, None]
    fx = np.clip(x - x0, 0, 1)[None, :, None]
    a00, a01 = a[y0][:, x0], a[y0][:, x0 + 1]
    a10, a11 = a[y0 + 1][:, x0], a[y0 + 1][:, x0 + 1]
    return (a00 * (1 - fx) + a01 * fx) * (1 - fy) + (a10 * (1 - fx) + a11 * fx) * fy


GLYPHS = {
    "A": ["01110", "10001", "10001", "11111", "10001", "10001", "10001"],
    "B": ["11110", "10001", "10001", "11110", "10001", "10001", "11110"],
    "C": ["01111", "10000", "10000", "10000", "10000", "10000", "01111"],
    "P": ["11110", "10001", "10001", "11110", "10000", "10000", "10000"],
    "0": ["01110", "10011", "10101", "10101", "11001", "10001", "01110"],
    "1": ["00100", "01100", "00100", "00100", "00100", "00100", "01110"],
    "9": ["01110", "10001", "10001", "01111", "00001", "00010", "01100"],
}


def label(a, text, k=3):
    x = 6
    for ch in text:
        g = GLYPHS.get(ch)
        if g is None:
            x += 3 * k
            continue
        a[4:4 + 9 * k, x - 2:x + 6 * k] = 0.08
        for r, row in enumerate(g):
            for c, on in enumerate(row):
                if on == "1":
                    a[8 + r * k:8 + (r + 1) * k, x + c * k:x + (c + 1) * k] = 0.95
        x += 6 * k + 2
    return a


def main():
    argv = sys.argv[sys.argv.index("--") + 1:]
    out, specs = argv[0], argv[1:]
    rows, row = [], []
    for sp in specs:
        if sp == "/":
            rows.append(row)
            row = []
            continue
        path, crop, scale, *lab = sp.split("@")
        a = read(path)
        if crop != "-":
            x, y, w, h = [int(v) for v in crop.split(",")]
            a = a[y:y + h, x:x + w]
        a = resize(a, float(scale))
        row.append(label(a.copy(), lab[0]) if lab else a)
    rows.append(row)
    gap = 8
    H = sum(max(t.shape[0] for t in r) for r in rows) + gap * (len(rows) + 1)
    W = max(sum(t.shape[1] for t in r) + gap * (len(r) + 1) for r in rows)
    img = np.full((H, W, 3), 0.12)
    y = gap
    for r in rows:
        x = gap
        for t in r:
            img[y:y + t.shape[0], x:x + t.shape[1]] = t
            x += t.shape[1] + gap
        y += max(t.shape[0] for t in r) + gap
    o = np.ones((H, W, 4), np.float32)
    o[..., :3] = img[::-1]
    im = bpy.data.images.new("m", W, H, alpha=True)
    im.colorspace_settings.name = "Non-Color"
    im.pixels.foreach_set(o.ravel())
    im.filepath_raw = out
    if out.endswith(".jpg"):
        im.file_format = "JPEG"
        im.save(quality=95)
    else:
        im.file_format = "PNG"
        im.save()
    print(f"[montage] {out} {W}x{H}")


if __name__ == "__main__":
    main()
