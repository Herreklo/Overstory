"""The walked corner's site as the heart's clay has it, gathered once for the rock and ground's generators.

Imports blender/blockouts/heart_layout (over two minutes) and writes cache/ground/site.json (and site.npz):
- the clay ground exactly as heart_build makes it (the 1.5 m grid, carved), over the corner, so the new ground meets
  the clay it replaces at the border with no step;
- the same carving on a fine grid, and the land before the knuckle stood up out of it (the rock's base);
- the knuckle's outline and top (centre_land.ROCKS), the clay's retaining walls near the corner (ground_walls), the
  corner's buildings (A to E: footprint, base), the Landing, the cooper's yard and the ways (Gully Steps, the
  terraces) as they pass the corner.

Street metres (x towards the Basin's head, y up Herring Hill, z up). Run with Blender's python (numpy):

    $PY tools/corner_site.py [--out cache/ground]
"""

import argparse
import json
import math
import os
import sys

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "blender", "blockouts"))

# the corner's box: wide enough for the street camera's whole frame of near ground and rock
BOX = (26.0, -4.0, 74.0, 58.0)
FINE = 0.25


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="cache/ground")
    a = ap.parse_args()
    out = os.path.join(ROOT, a.out)
    os.makedirs(out, exist_ok=True)

    import centre_land as L  # noqa: E402
    import heart_layout as H  # noqa: E402  (lays the town out on import)

    hx0, hy0, _, _ = H.HEART
    # the clay grid's own lines (heart_build: grid(HX0, HY0, ..., 1.5)), over the corner
    i0, i1 = int(math.floor((BOX[0] - hx0) / 1.5)), int(math.ceil((BOX[2] - hx0) / 1.5))
    j0, j1 = int(math.floor((BOX[1] - hy0) / 1.5)), int(math.ceil((BOX[3] - hy0) / 1.5))
    cx = hx0 + 1.5 * np.arange(i0, i1 + 1)
    cy = hy0 + 1.5 * np.arange(j0, j1 + 1)
    CX, CY = np.meshgrid(cx, cy, indexing="ij")
    CZ = H.carve(CX, CY, L.heights(CX, CY))

    fx = np.arange(BOX[0], BOX[2] + FINE / 2, FINE)
    fy = np.arange(BOX[1], BOX[3] + FINE / 2, FINE)
    FX, FY = np.meshgrid(fx, fy, indexing="ij")
    natural = L.heights(FX, FY)
    FZ = H.carve(FX, FY, natural.copy())
    knuckle = [r for r in L.ROCKS if r["name"] == "the corner's knuckle"][0]
    rocks = list(L.ROCKS)
    L.ROCKS[:] = [r for r in rocks if r is not knuckle]
    bare = L.heights(FX, FY)                    # the land before the knuckle stood up out of it
    carved_bare = H.carve(FX, FY, bare.copy())  # and the ways cut into that land
    L.ROCKS[:] = rocks

    def ground(x, y):
        # heart_build's own sample of the clay grid (bilinear), as ground_walls is given it there
        X, Y = CX, CY
        step = 1.5
        u = min(max((x - X[0, 0]) / step, 0), X.shape[0] - 1.001)
        v = min(max((y - Y[0, 0]) / step, 0), X.shape[1] - 1.001)
        i, j = int(u), int(v)
        fu, fv = u - i, v - j
        p = CZ[i, j] + (CZ[i + 1, j] - CZ[i, j]) * fu
        q = CZ[i, j + 1] + (CZ[i + 1, j + 1] - CZ[i, j + 1]) * fu
        return float(p + (q - p) * fv)

    def near(x, y, pad=0.0):
        return BOX[0] - pad <= x <= BOX[2] + pad and BOX[1] - pad <= y <= BOX[3] + pad

    walls = [w for w in H.ground_walls(ground) if near(w["x"], w["y"])]
    corner = []
    for b in H.BUILDINGS:
        fp = H.footprint(b)
        if any(near(x, y, 4.0) for x, y in fp):
            corner.append(dict(name=b["name"], role=b["role"], fp=[list(p) for p in fp], base=b["base"],
                               eave=b["eave"], angle=b["angle"], w=b["w"], d=b["d"]))
    details = [d for d in H.DETAILS if near(d["x"], d["y"], 2.0)]
    lanes = []
    for lane in H.LANES:
        pts = [p for p in lane["pts"] if near(p[0], p[1], 30.0)]
        if pts and lane["kind"] != "road":
            lanes.append(dict(name=lane["name"], kind=lane["kind"], width=lane["width"],
                              pts=[list(map(float, p)) for p in lane["pts"]]))
    site = dict(
        note="The walked corner as the heart's clay has it (tools/corner_site.py); street metres.",
        box=BOX, clay=dict(x0=float(cx[0]), y0=float(cy[0]), step=1.5, nx=len(cx), ny=len(cy)),
        fine=dict(x0=float(fx[0]), y0=float(fy[0]), step=FINE, nx=len(fx), ny=len(fy)),
        knuckle=dict(name=knuckle["name"], top=knuckle["top"], face=knuckle["face"], steps=knuckle["steps"],
                     outline=[list(p) for p in knuckle["outline"]]),
        landing=dict(z=H.LANDING_Z, poly=[list(p) for p in H.LANDING]),
        yards=[dict(poly=[list(p) for p in poly], z=z) for poly, z in H.YARDS if any(near(x, y) for x, y in poly)],
        walls=walls, buildings=corner, details=details, lanes=lanes,
    )
    json.dump(site, open(os.path.join(out, "site.json"), "w"), indent=1)
    np.savez_compressed(os.path.join(out, "site.npz"), clay=CZ, fine=FZ, natural=natural, bare=bare,
                        carved_bare=carved_bare)
    print(f"site: {len(walls)} walls, {len(corner)} buildings, {len(details)} details, {len(lanes)} lanes -> {out}")


if __name__ == "__main__":
    main()
