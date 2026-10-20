"""The centre plan as a shaded relief map with contours, paths and labels: reviews/lt1/centre/centre-land-draft.png.

    python blender/blockouts/centre_map.py <out-dir>   (needs numpy and Pillow)
"""
import sys, math, time
sys.path.insert(0, "/Users/oystein/code/Overstory/blender/blockouts")
import numpy as np
import centre_land as L
from PIL import Image, ImageDraw, ImageFont
t0 = time.time()
X0, X1, Y0, Y1, step = -900, 1450, -1000, 1350, 2.5   # x down (south), y right (east)
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
# only what the land fixes: quays, the main roads, the bridges, the railway, the hundred steps, the ferry.
# Streets and lanes are laid in clay.
line([(-250, -6), (150, -6), (250, -14), (300, -24), (334, -42)], ROAD, 4)              # Harbour Row
line([(-186, -176), (0, -166), (150, -150), (240, -140), (300, -134)], ROAD, 4)          # the pub quay
line([(-210, 422), (-120, 444), (-30, 462)], ROAD, 4)                                    # the cannery's quay
line([(28, -226), (66, -226)], (40, 40, 40), 6)                                         # the sund's bridge, across it
line([(60, -10), (60, -158)], WATERWAY, 2, dash=True)                                   # the harbour ferry
line(L.BRIDGE, (50, 50, 50), 5)                                                          # the 1978 bridge
line(L.BREAKWATER, (100, 100, 100), 5)
line(L.RAILWAY, (40, 40, 40), 3, dash=True)
line([(-240, 60), (-262, 80), (-276, 96)], STEP, 3)                                     # the hundred steps up the bluff
sq = [(350, -120), (410, -128), (414, -40), (352, -36)]
dr.polygon([P(x, y) for x, y in sq], fill=(214, 194, 166), outline=(80, 70, 60))
font = ImageFont.load_default(size=20)
FONT = "/System/Library/Fonts/Supplemental/Arial.ttf"
def label(x, y, t, big=False):
    f = ImageFont.truetype(FONT, 26 if big else 17)
    sx, sy = P(x, y)
    dr.text((sx, sy), t, fill=(255, 255, 255), font=f, anchor="mm", stroke_width=3, stroke_fill=(255, 255, 255))
    dr.text((sx, sy), t, fill=(30, 30, 30), font=f, anchor="mm")
for x, y, t, big in [(-620, 0, "THE BAY", True), (210, -84, "VÅGEN", True), (-160, 680, "EAST HARBOUR", True),
                     (-160, -520, "WEST COVE", True), (-100, -230, "Holmen", False), (190, -370, "knoll, tower", False),
                     (360, -470, "FIRE GRID", True), (440, -84, "Torget", False), (470, 40, "cathedral", False),
                     (640, -50, "lake", False), (60, 170, "OLD TOWN", True), (-20, 270, "villas, summit park", False),
                     (-300, 230, "bluff", False), (-110, 380, "cannery streets", False), (-250, 520, "cannery", False),
                     (-260, 1200, "STORHAUG", True), (520, 1000, "FOREST HILL", True), (-740, 390, "island suburb", False),
                     (-620, -380, "island", False), (-580, 900, "bridge 1978", False), (-312, -150, "light", False),
                     (-250, -780, "ferry quay, oil base", False), (800, -420, "NEWER TOWN", True), (80, 30, "corner", False),
                     (-400, -60, "beacon", False), (40, -620, "beach", False), (250, 640, "stream valley", False),
                     (980, 150, "railway", False), (800, -780, "ridge", False), (1350, 300, "upland", True), (30, -250, "sund", False)]:
    label(x, y, t, big)
im.save(f"{sys.argv[1]}/centre-land-draft.png")
print("done", round(time.time() - t0, 1), "s", im.size)
