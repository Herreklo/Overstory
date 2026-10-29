"""Two rounds' stills compared by machine, in L* (CIE, 0 to 100) as a viewer sees value.

    Blender -b --factory-startup -P blender/parts/street/run/stilldiff.py -- <round A dir> <round B dir> [block px] [diff dir]

For every still in A with a namesake in B: the mean, 99th percentile and largest L* difference pixel by pixel, and
the same over blocks of `block` px (default 8) a side, which is what a read of broad shapes sees: a change under
1 L* over a block is below what an eye tells apart. Prints a table; exit 0. With a diff dir, each still's difference
as an image there (grey 0.5 the same, 10 L* lighter or darker in B to white or black).
"""
import glob
import os
import sys

import bpy
import numpy as np

argv = sys.argv[sys.argv.index("--") + 1:]
A, B = (os.path.abspath(p) for p in argv[:2])
k = int(argv[2]) if len(argv) > 2 else 8
out = os.path.abspath(argv[3]) if len(argv) > 3 else None


def L(path):
    img = bpy.data.images.load(path)
    img.colorspace_settings.name = "Non-Color"
    w, h = img.size
    a = np.array(img.pixels[:], dtype=np.float32).reshape(h, w, 4)[..., :3]
    bpy.data.images.remove(img)
    lin = np.where(a <= 0.04045, a / 12.92, ((a + 0.055) / 1.055) ** 2.4)
    Y = lin @ np.array([0.2126, 0.7152, 0.0722], dtype=np.float32)
    return 116 * np.where(Y > 0.008856, np.cbrt(Y), 7.787 * Y + 16 / 116) - 16


print(f"{'still':34s} {'mean':>5s} {'p99':>5s} {'max':>5s} | {k}px blocks: {'max':>5s} {'>1 L*':>7s}")
for pa in sorted(glob.glob(os.path.join(A, "*.png"))):
    pb = os.path.join(B, os.path.basename(pa))
    if not os.path.exists(pb):
        continue
    d = L(pa) - L(pb)
    h, w = (s // k * k for s in d.shape)
    D = d[:h, :w].reshape(h // k, k, w // k, k).mean((1, 3))
    if out:
        os.makedirs(out, exist_ok=True)
        im = bpy.data.images.new("d", d.shape[1], d.shape[0])
        g = np.clip(0.5 - d / 20.0, 0, 1)
        im.pixels[:] = np.dstack([g, g, g, np.ones_like(g)]).ravel()
        im.filepath_raw = os.path.join(out, os.path.basename(pa))
        im.file_format = "PNG"
        im.save()
        bpy.data.images.remove(im)
    ad = np.abs(d)
    print(f"{os.path.basename(pa):34s} {ad.mean():5.2f} {np.percentile(ad, 99):5.2f} {ad.max():5.1f} | "
          f"{np.abs(D).max():5.2f} {(np.abs(D) > 1).mean() * 100:6.2f}%")
