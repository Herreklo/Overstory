"""A skyline check: the land seen from one point, near, middle and far hills in separate tones, to show the
backdrop reads in layers. reviews/lt1/centre/skyline-from-bay.png.

    python blender/blockouts/centre_skyline.py <out.png> <x> <y>   (needs numpy and Pillow)
"""
import sys, math
sys.path.insert(0, "/Users/oystein/code/Overstory/blender/blockouts")
import numpy as np
import centre_land as L
from PIL import Image, ImageDraw, ImageFont
# from the bay, north of the old town's point, eye 4 m over the water, looking south (towards +x), 100 degrees wide
ex, ey, ez = float(sys.argv[2]), float(sys.argv[3]), 4.0
W, H = 1400, 420
fov = math.radians(100)
az = np.linspace(-fov / 2, fov / 2, W)          # 0 = towards +x (south); + = towards +y (east)
dist = np.concatenate([np.arange(20, 600, 4), np.arange(600, 1600, 8), np.arange(1600, 3400, 16)])
A, D = np.meshgrid(az, dist, indexing="ij")
X = ex + D * np.cos(A); Y = ey - D * np.sin(A)   # screen right is west? keep: + angle -> -y (west) so the image is not mirrored
Z = L.heights(X, Y)
Z = np.maximum(Z, 0.0)
ang = np.degrees(np.arctan2(Z - ez, D))          # elevation angle of every sample
img = Image.new("RGB", (W, H), (226, 232, 238)); dr = ImageDraw.Draw(img)
def ypix(a): return H - 60 - a * 26                  # 26 px per degree
# the far range, as the backdrop: bearing in street axes (compass = 190 - street bearing in degrees)
import math as _m
far = np.full(W, -5.0)
for i in range(W):
    street_b = _m.degrees(-az[i])  # 0 = +x, positive = towards -y... matches X, Y above
    comp = (190.0 - (_m.degrees(_m.atan2(-_m.sin(az[i]), _m.cos(az[i]))) * -1.0 + 0.0)) % 360
best = None
pts = sorted(L.FAR_RANGE)
for i in range(W):
    # compass bearing of this column: the column looks along street direction (cos a, -sin a)
    sx, sy = _m.cos(az[i]), -_m.sin(az[i])
    sb = _m.degrees(_m.atan2(sy, sx))           # street bearing: 0 along +x, 90 along +y
    comp = (190.0 - sb) % 360                   # +x is compass 190, +y compass 100
    for (b0, h0, d0), (b1, h1, d1) in zip(pts, pts[1:]):
        if b0 <= comp <= b1:
            t = (comp - b0) / (b1 - b0)
            h = h0 + (h1 - h0) * t; d = d0 + (d1 - d0) * t
            far[i] = _m.degrees(_m.atan2(h - ez - d * d / 12740000.0, d))  # earth's curve
img0 = img
for i in range(W):
    if far[i] > -4:
        dr.line([(W - 1 - i, ypix(far[i])), (W - 1 - i, H)], fill=(184, 192, 204))
bands = [(1600, 3200, (150, 160, 175)), (600, 1600, (110, 120, 130)), (0, 600, (60, 66, 72))]
for d0, d1, col in bands:
    mask = (D >= d0) & (D < d1)
    top = np.where(mask, ang, -5).max(axis=1)
    for i in range(W):
        dr.line([(W - 1 - i, ypix(top[i])), (W - 1 - i, H)], fill=col)
dr.line([(0, ypix(0)), (W, ypix(0))], fill=(120, 150, 175), width=2)
f = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 16)
dr.text((10, 10), f"From the bay at ({ex:.0f}, {ey:.0f}) looking south, eye 4 m over the water. Dark: within 600 m. Mid: 600-1600 m. Light: 1600-3400 m. Palest: mountains 22-34 km. 26 px per degree.", fill=(30, 30, 30), font=f)
for deg, name in [(-50, "east (Ropewalk, forest hill)"), (0, "south (the town, the Basin's head)"), (50, "west (fire grid, ridge)")]:
    xpix = W / 2 - deg / 100 * W
    dr.text((xpix, H - 30), name, fill=(30, 30, 30), font=f, anchor="mm")
img.save(sys.argv[1])
print("ok")
