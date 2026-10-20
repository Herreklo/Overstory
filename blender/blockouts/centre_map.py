"""The centre plan as a shaded relief map with contours, paths and labels: reviews/lt1/centre/centre-land-draft.png.

    python blender/blockouts/centre_map.py <out-dir>   (needs numpy and Pillow)
"""
import sys, math, time
sys.path.insert(0, "/Users/oystein/code/Overstory/blender/blockouts")
import numpy as np
import centre_land as L
from PIL import Image, ImageDraw, ImageFont
t0 = time.time()
X0, X1, Y0, Y1, step = -820, 900, -900, 1160, 2.0   # x down (south), y right (east)
xs = np.arange(X0, X1, step); ys = np.arange(Y0, Y1, step)
XX, YY = np.meshgrid(xs, ys, indexing="ij")
Z = L.heights(XX, YY)
W = L.is_water(XX, YY)
print("heights", round(time.time() - t0, 1), "s", Z.min(), Z.max())
gx = np.gradient(Z, step, axis=0); gy = np.gradient(Z, step, axis=1)
lx, ly, lz = -0.6, -0.4, 0.7   # light from the north-west
n = np.sqrt(gx ** 2 + gy ** 2 + 1)
shade = np.clip((-gx * lx - gy * ly + lz) / n / math.sqrt(lx * lx + ly * ly + lz * lz), 0, 1)
t = np.clip(Z / 70.0, 0, 1)
r = 228 - 50 * t; g = 222 - 30 * t; b = 196 - 40 * t
img = np.stack([r, g, b], -1) * (0.5 + 0.62 * shade)[..., None]
c2 = np.floor(Z / 2.0); c10 = np.floor(Z / 10.0)
edge2 = (np.diff(c2, axis=0, append=c2[-1:]) != 0) | (np.diff(c2, axis=1, append=c2[:, -1:]) != 0)
edge10 = (np.diff(c10, axis=0, append=c10[-1:]) != 0) | (np.diff(c10, axis=1, append=c10[:, -1:]) != 0)
img[edge2 & ~W] *= 0.8
img[edge10 & ~W] = (120, 96, 72)
img[W] = (148, 176, 198)
img = np.clip(img, 0, 255).astype(np.uint8)
im = Image.fromarray(img, "RGB")   # rows = x (south down), columns = y (east right): north up
dr = ImageDraw.Draw(im)
def P(x, y): return ((y - Y0) / step, (x - X0) / step)
def line(pts, col, w, dash=False):
    Q = [P(x, y) for x, y in pts]
    if not dash:
        dr.line(Q, fill=col, width=w); return
    for a, b in zip(Q, Q[1:]):
        k = max(2, int(math.hypot(b[0] - a[0], b[1] - a[1]) / 5))
        for i in range(0, k, 2):
            dr.line([(a[0] + (b[0] - a[0]) * i / k, a[1] + (b[1] - a[1]) * i / k), (a[0] + (b[0] - a[0]) * (i + 1) / k, a[1] + (b[1] - a[1]) * (i + 1) / k)], fill=col, width=w)
ROAD, LANE, STEP, WATERWAY = (80, 70, 60), (120, 100, 80), (190, 60, 40), (40, 70, 120)
line([(-250, -6), (150, -6), (220, -14), (270, -30), (300, -50)], ROAD, 4)              # Harbour Row
line([(-150, -176), (0, -166), (150, -150), (250, -134), (300, -124)], ROAD, 4)          # the pub quay
line([(-230, -232), (0, -226), (34, -224)], LANE, 3)                                      # Holmegate on Holmen
line([(60, -192), (150, -182), (300, -150)], LANE, 3)                                     # its upper street, south of the sund
line([(47, -170), (47, -300)], (60, 60, 60), 6)                                           # the sund's bridge
line([(60, -10), (60, -150)], WATERWAY, 2, dash=True)                                     # the harbour ferry
line(L.BRIDGE, (50, 50, 50), 5)                                                           # the 1978 bridge
line(L.BREAKWATER, (100, 100, 100), 5)
line([(-236, 120), (-230, 140), (-224, 150)], STEP, 3)                                    # the hundred steps
line([(-246, 412), (-150, 422), (-20, 452)], ROAD, 3)                                       # the east harbour's quay, the cannery
for off in (18, 34, 54):
    line([(-200, off + 4), (60, off), (200, off - 6), (280, off - 30)], LANE, 2)          # contour lanes
line([(49, -6), (49, 20), (47, 38), (46, 64), (60, 120), (60, 205)], STEP, 3)            # Bakkesmauet to the top
line([(-110, -6), (-112, 40), (-108, 100), (-100, 190)], STEP, 3)                        # the other gully's lane
line([(120, -420), (200, -300), (290, -160)], ROAD, 8)                                    # the fire-break street
for k in range(7):
    line([(110 + k * 60, -250), (130 + k * 60, -620)], LANE, 2)
for k in range(5):
    line([(100, -300 - k * 70), (640, -270 - k * 70)], LANE, 2)
sq = [(305, -120), (350, -130), (352, -60), (306, -64)]
dr.polygon([P(x, y) for x, y in sq], fill=(214, 194, 166), outline=(80, 70, 60))
font = ImageFont.load_default(size=20)
FONT = "/System/Library/Fonts/Supplemental/Arial.ttf"
def label(x, y, t, big=False):
    f = ImageFont.truetype(FONT, 26 if big else 17)
    sx, sy = P(x, y)
    dr.text((sx, sy), t, fill=(255, 255, 255), font=f, anchor="mm", stroke_width=3, stroke_fill=(255, 255, 255))
    dr.text((sx, sy), t, fill=(30, 30, 30), font=f, anchor="mm")
for x, y, t, big in [(-620, 0, "THE BAY", True), (60, -86, "VÅGEN", True), (-90, 590, "EAST HARBOUR", True),
                     (-180, -560, "WEST COVE", True), (60, -650, "beach", False), (300, 690, "stream valley", False), (20, 236, "summit park", False), (-150, -262, "Holmen (pubs)", False), (150, -360, "knoll, tower", False),
                     (360, -470, "FIRE GRID", True), (330, -95, "Torget", False), (395, 30, "cathedral", False),
                     (520, -50, "lake", False), (100, 140, "OLD TOWN", True), (90, 300, "villas", False),
                     (-300, 180, "bluff", False), (-200, 440, "cannery", False), (-160, 940, "STORHAUG", True),
                     (470, 980, "FOREST HILL", True), (-740, 390, "island suburb", False), (-620, -380, "island", False),
                     (-470, 640, "bridge 1978", False), (-395, -110, "light", False), (-250, -760, "ferry quay, oil base", False),
                     (760, -320, "NEWER TOWN", True), (90, 36, "corner", False), (-370, -60, "beacon", False)]:
    label(x, y, t, big)
im.save(f"{sys.argv[1]}/centre-land-draft.png")
print("done", round(time.time() - t0, 1), "s", im.size)
