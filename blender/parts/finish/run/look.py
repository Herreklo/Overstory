"""A look sheet in grey: renders beside references, each scaled to one row height (references turned to their
luminance, so values compare). Blender -b --factory-startup -P look.py -- out height spec [spec ...]
spec = path@x,y,w,h@label[@colour] (x, y from the top-left, '-' for the whole image; `colour` keeps its colour);
rows split on a lone '/'."""
import sys

import numpy as np
import bpy

sys.path.insert(0, "/Users/oystein/code/Overstory/blender/parts/finish/run")
from montage import label, read, resize  # noqa: E402


def grey(a):
    lin = np.where(a <= 0.04045, a / 12.92, ((a + 0.055) / 1.055) ** 2.4)
    Y = lin @ np.array([0.2126, 0.7152, 0.0722])
    g = np.where(Y <= 0.0031308, 12.92 * Y, 1.055 * np.power(Y, 1 / 2.4) - 0.055)
    return np.repeat(g[..., None], 3, -1)


argv = sys.argv[sys.argv.index("--") + 1:]
out, height, specs = argv[0], int(argv[1]), argv[2:]
rows, row = [], []
for sp in specs:
    if sp == "/":
        rows.append(row)
        row = []
        continue
    path, crop, *lab = sp.split("@")
    a = read(path)
    if crop != "-":
        x, y, w, h = [int(v) for v in crop.split(",")]
        a = a[y:y + h, x:x + w]
    a = resize(a if "colour" in lab[1:] else grey(a), height / a.shape[0])
    row.append(label(a.copy(), lab[0]) if lab and lab[0] else a)
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
im.file_format = "JPEG" if out.endswith(".jpg") else "PNG"
im.save(quality=92) if out.endswith(".jpg") else im.save()
print(f"[look] {out} {W}x{H}")
