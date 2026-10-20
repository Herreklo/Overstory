"""The map of uses: every piece of land with its use, over the relief, and a check that no land is left without
one. reviews/lt1/centre/centre-land-use.png.

    python blender/blockouts/centre_uses.py <out-dir>   (needs numpy and Pillow)
"""
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, __file__.rsplit("/", 1)[0])
import centre_land as L

X0, X1, Y0, Y1, step = -900, 1450, -1000, 1350, 2.5
xs = np.arange(X0, X1, step); ys = np.arange(Y0, Y1, step)
XX, YY = np.meshgrid(xs, ys, indexing="ij")
Z = L.heights(XX, YY)
W = L.is_water(XX, YY)
gx = np.gradient(Z, step, axis=0); gy = np.gradient(Z, step, axis=1)
shade = np.clip((0.6 * gx + 0.4 * gy + 0.7) / np.sqrt(gx ** 2 + gy ** 2 + 1) / 1.01, 0, 1)
COL = {"home": (226, 176, 90), "night": (214, 96, 64), "civic": (140, 120, 200), "work": (140, 140, 140),
       "nature": (110, 170, 110), "farm": (190, 190, 110), "edge": (170, 130, 100)}
img = np.zeros(XX.shape + (3,))
covered = np.zeros(XX.shape, dtype=bool)
for name, kind, poly in L.USES:
    m = L._inside(poly, XX, YY) & ~covered & ~W
    img[m] = COL[kind]
    covered |= m
land = ~W
dead = land & ~covered
img[dead] = (255, 0, 255)
img = img * (0.55 + 0.45 * shade)[..., None]
img[W] = (150, 178, 200)
im = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8))
dr = ImageDraw.Draw(im)
f = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 13)
for name, kind, poly in L.USES:
    cx = sum(p[0] for p in poly) / len(poly); cy = sum(p[1] for p in poly) / len(poly)
    pos = ((cy - Y0) / step, (cx - X0) / step)
    short = name.split(":")[0].split(",")[0]
    dr.text(pos, short, fill=(255, 255, 255), font=f, anchor="mm", stroke_width=3, stroke_fill=(255, 255, 255))
    dr.text(pos, short, fill=(25, 25, 25), font=f, anchor="mm")
lx = 10
for kind, col in COL.items():
    dr.rectangle([lx, im.height - 24, lx + 14, im.height - 10], fill=col)
    dr.text((lx + 18, im.height - 17), kind, fill=(20, 20, 20), font=f, anchor="lm")
    lx += 90
im.save(f"{sys.argv[1]}/centre-land-use.png")
print(f"land without a use: {dead.sum() / land.sum():.2%} of the land on the map")
