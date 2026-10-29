"""Tile renders into one contact sheet (numpy through Blender's images; no PIL).

    Blender -b --factory-startup -P blender/parts/rock/sheet.py -- OUT.png COLS IMG1 IMG2 ...
"""
import sys

import bpy
import numpy as np

a = sys.argv[sys.argv.index("--") + 1:]
out, cols, paths = a[0], int(a[1]), a[2:]
ims = []
for p in paths:  # each at the first's height, so references of any size sit beside the renders
    im = bpy.data.images.load(p)
    if ims and im.size[1] != ims[0].shape[0]:
        im.scale(max(1, round(im.size[0] * ims[0].shape[0] / im.size[1])), ims[0].shape[0])
    w, h = im.size
    ims.append(np.array(im.pixels[:]).reshape(h, w, 4))
h, w = ims[0].shape[0], max(im.shape[1] for im in ims)
rows = (len(ims) + cols - 1) // cols
pad = 6
S = np.ones(((h + pad) * rows - pad, (w + pad) * cols - pad, 4))
for i, im in enumerate(ims):
    r, c = divmod(i, cols)
    y = (rows - 1 - r) * (h + pad)
    S[y:y + h, c * (w + pad):c * (w + pad) + im.shape[1]] = im[:h]
o = bpy.data.images.new("sheet", S.shape[1], S.shape[0], alpha=False)
o.pixels = S.ravel()
o.filepath_raw = out
o.file_format = "PNG"
o.save()
