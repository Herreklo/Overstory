"""t09's outline over a grey still: its mask's edge (mask-<view>.png from scan.py --subject t09) drawn in red.

    Blender -b --factory-startup -P outline.py -- DIR SUBJECT VIEW,VIEW... LIGHT,LIGHT...
writes DIR/<subject>-<view>-<light>-t09.png
"""
import os, sys

import bpy
import numpy as np

a = sys.argv[sys.argv.index("--") + 1:]
d, subject, views, lights = a[0], a[1], a[2].split(","), a[3].split(",")


def load(p):
    im = bpy.data.images.load(p); w, h = im.size
    return np.array(im.pixels[:], np.float32).reshape(h, w, 4)


for v in views:
    m = load(os.path.join(d, f"mask-{v}.png"))[..., 0] > 0.5
    er = m.copy()
    for _ in range(2):  # 2 px line
        er = er & np.roll(er, 1, 0) & np.roll(er, -1, 0) & np.roll(er, 1, 1) & np.roll(er, -1, 1)
    edge = m & ~er
    for li in lights:
        p = load(os.path.join(d, f"{subject}-{v}-{li}.png"))
        p[edge] = (0.85, 0.05, 0.03, 1)
        h, w = p.shape[:2]
        o = bpy.data.images.new("o", w, h); o.pixels[:] = p.reshape(-1)
        o.filepath_raw = os.path.join(d, f"{subject}-{v}-{li}-t09.png"); o.file_format = "PNG"; o.save()
