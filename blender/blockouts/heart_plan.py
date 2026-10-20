"""The heart's layout in plan over the relief: footprints, lanes, stairs, squares. reviews/lt1/centre/heart-plan.png.

    python blender/blockouts/heart_plan.py <out-dir>   (needs numpy and Pillow)
"""
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, __file__.rsplit("/", 1)[0])
import centre_land as L
import heart_layout as H

X0, Y0, X1, Y1 = H.HEART
step = 0.5   # 2 px per metre
xs = np.arange(X0, X1, 1.0); ys = np.arange(Y0, Y1, 1.0)
XX, YY = np.meshgrid(xs, ys, indexing="ij")
Z = H.carve(XX, YY, L.heights(XX, YY))
W = L.is_water(XX, YY)
gx = np.gradient(Z, 1.0, axis=0); gy = np.gradient(Z, 1.0, axis=1)
shade = np.clip((0.6 * gx + 0.4 * gy + 0.7) / np.sqrt(gx ** 2 + gy ** 2 + 1), 0, 1)
img = np.stack([226 + 0 * Z, 220 + 0 * Z, 204 + 0 * Z], -1) * (0.55 + 0.45 * shade)[..., None]
c2 = np.floor(Z / 2.0)
edge = (np.diff(c2, axis=0, append=c2[-1:]) != 0) | (np.diff(c2, axis=1, append=c2[:, -1:]) != 0)
img[edge & ~W] *= 0.82
img[W] = (150, 178, 200)
im = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).resize((int((Y1 - Y0) * 2), int((X1 - X0) * 2)), Image.NEAREST)
dr = ImageDraw.Draw(im)
def P(x, y): return ((y - Y0) * 2, (x - X0) * 2)
for lane in H.LANES:
    pts = [P(p[0], p[1]) for p in lane["pts"]]
    col = (190, 60, 40) if lane["kind"] == "steps" else (120, 110, 100)
    dr.line(pts, fill=col, width=max(2, int(lane["width"] * 2)) if lane["kind"] != "quay" else 3)
dr.polygon([P(*p) for p in H.MARKET_SQUARE], outline=(90, 60, 140), width=3)
dr.polygon([P(*p) for p in H.LANDING], outline=(190, 60, 40), width=3)
COL = {"corner": (214, 96, 64), "row": (60, 60, 60), "warehouse": (110, 80, 50), "landmark": (90, 60, 140)}
for b in H.BUILDINGS:
    dr.polygon([P(*p) for p in H.footprint(b)], fill=COL.get(b["role"], (60, 60, 60)), outline=(250, 250, 250))
f = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 22)
for x, y, t in [(60, -90, "the Basin"), (-120, -200, "the Holm"), (150, -330, "Watch Knoll"), (380, -100, "Market Square"),
                (440, 0, "cathedral"), (400, -350, "the Grid"), (60, 120, "Herring Hill"), (250, -470, "Broad Street")]:
    dr.text(P(x, y), t, fill=(20, 20, 20), font=f, anchor="mm", stroke_width=3, stroke_fill=(255, 255, 255))
im.save(f"{sys.argv[1]}/heart-plan.png")
im.resize((im.width // 2, im.height // 2)).save(f"{sys.argv[1]}/heart-plan-small.png")
print(im.size)
