"""The heart's layout, dumped for the ladder's Unity-free tests (test 2a's sight, test 1's walking minutes).

    /Applications/Blender.app/Contents/MacOS/Blender -b --factory-startup --python tools/playable/layout_dump.py -- OUT.json

`blender/blockouts/heart_layout.py` needs numpy, which only Blender's Python has here, so this runs in Blender's
Python once (no bpy, no scene, nothing written but OUT.json) and the tests read the dump in plain Python.

The dump holds, in street metres (x towards the Basin's head, y up Herring Hill, z up):
- every lane, stair, quay and door path (`LANES`), with its width and kind: the town's walking network;
- in the corner's box (CORNER, below): every building with its footprint, base, eave, pitch and roof; the small masses
  (`DETAILS`: yard walls, sheds, stoops, lamps); the retaining walls the ground needs (`ground_walls`, the gully's
  cheek walls among them), the Landing, the yards; and the carved ground on heart_build's own 1.5 m grid;
- the source's git blob hash, so a later layout is a new dump.

It reads the layout; it changes nothing in it.
"""

import hashlib
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
BLOCKOUTS = os.path.join(ROOT, "blender", "blockouts")
sys.path.insert(0, BLOCKOUTS)

import numpy as np  # noqa: E402

import centre_land as L  # noqa: E402
import heart_layout as H  # noqa: E402

CORNER = (-60.0, -40.0, 140.0, 130.0)  # x0, y0, x1, y1: the corner, the Row from the Anchor's stretch to B, up to E
STEP = 1.5                               # heart_build's ground grid


def blob_hash(path):
    data = open(path, "rb").read()
    return hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()


def r(v, n=3):
    return round(float(v), n)


def inside_box(x, y, pad=0.0):
    x0, y0, x1, y1 = CORNER
    return x0 - pad <= x <= x1 + pad and y0 - pad <= y <= y1 + pad


def main(out):
    hx0, hy0 = H.HEART[0], H.HEART[1]
    # the grid aligned with heart_build's (origin HEART's corner, 1.5 m), cut to the corner's box
    i0 = int(math.floor((CORNER[0] - hx0) / STEP))
    i1 = int(math.ceil((CORNER[2] - hx0) / STEP))
    j0 = int(math.floor((CORNER[1] - hy0) / STEP))
    j1 = int(math.ceil((CORNER[3] - hy0) / STEP))
    xs = hx0 + STEP * np.arange(i0, i1 + 1)
    ys = hy0 + STEP * np.arange(j0, j1 + 1)
    X, Y = np.meshgrid(xs, ys, indexing="ij")
    Z = H.carve(X, Y, L.heights(X, Y))

    def ground(x, y):
        if not (xs[0] <= x <= xs[-1] and ys[0] <= y <= ys[-1]):
            return float(L.heights(np.array([x]), np.array([y]))[0])
        u = min(max((x - xs[0]) / STEP, 0), len(xs) - 1.001)
        v = min(max((y - ys[0]) / STEP, 0), len(ys) - 1.001)
        i, j = int(u), int(v)
        fu, fv = u - i, v - j
        a = Z[i, j] + (Z[i + 1, j] - Z[i, j]) * fu
        b = Z[i, j + 1] + (Z[i + 1, j + 1] - Z[i, j + 1]) * fu
        return float(a + (b - a) * fv)

    walls = [w for w in H.ground_walls(ground) if inside_box(w["x"], w["y"])]
    buildings = []
    for b in H.BUILDINGS:
        fp = H.footprint(b)
        if not any(inside_box(x, y, 2.0) for x, y in fp):
            continue
        door = H._door(b)
        buildings.append(dict(name=b["name"], role=b["role"], ox=r(b["ox"]), oy=r(b["oy"]), angle=r(b["angle"], 4),
                              w=r(b["w"]), d=r(b["d"]), base=r(b["base"]), eave=r(b["eave"]), pitch=r(b["pitch"]),
                              roof=b["roof"], low=b.get("low"), door=[r(door[0]), r(door[1])]))
    lanes = [dict(name=l["name"], width=r(l["width"]), kind=l.get("kind", "lane"), door=bool(l.get("door")),
                  pts=[[r(p[0], 2), r(p[1], 2), r(p[2], 2)] for p in l["pts"]]) for l in H.LANES]
    details = [dict(kind=d["kind"], x=r(d["x"]), y=r(d["y"]), z=r(d["z"]), l=r(d["l"]), w=r(d["w"]), h=r(d["h"]),
                    a=r(d.get("a", 0.0), 4)) for d in H.DETAILS if inside_box(d["x"], d["y"])]
    places = [dict(name=n, poly=[[r(x), r(y)] for x, y in poly], z=r(z)) for n, poly, z in
              [("the Landing", H.LANDING, H.LANDING_Z), ("Market Square", H.MARKET_SQUARE, H.MARKET_Z)] + list(H.SMALL_PLACES)]
    yards = [dict(poly=[[r(x), r(y)] for x, y in poly], z=r(z)) for poly, z in H.YARDS
             if any(inside_box(x, y) for x, y in poly)]
    dump = dict(
        source=dict(heart_layout=blob_hash(os.path.join(BLOCKOUTS, "heart_layout.py")),
                    centre_land=blob_hash(os.path.join(BLOCKOUTS, "centre_land.py")), seed=H.SEED),
        corner=list(CORNER), sea=H.SEA,
        ground=dict(x0=r(xs[0]), y0=r(ys[0]), step=STEP, nx=len(xs), ny=len(ys),
                    z=[[r(v, 2) for v in row] for row in Z.tolist()]),
        buildings=buildings, lanes=lanes, details=details, walls=[{k: r(v) for k, v in w.items()} for w in walls],
        places=places, yards=yards)
    with open(out, "w") as f:
        json.dump(dump, f, separators=(",", ":"))
    print("[layout_dump] {}: {} buildings, {} lanes, {} details, {} walls, ground {}x{}".format(
        out, len(buildings), len(lanes), len(details), len(walls), len(xs), len(ys)))


if __name__ == "__main__":
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
    main(argv[0])
