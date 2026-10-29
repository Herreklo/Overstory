"""The Bluff's target frame (look-in 3): Herring Hill's point, a 20 m face over the Roads, in its town and its light.

Look-in 2's form language (target_whaleback.py: ice-rounded masses, the face along the steep foliation, turf over
the lip, the shore's zones), set where the town plan puts it and broken the way rock breaks:

- The site. The face follows the plan's bluff line round Herring Hill's point, its foot on the 3 m contour. Its west
  end rises from Harbour Row's end, where the Hundred Steps climb its shoulder (the clay's route and benches); its east
  end falls to Cannery Bight, where the cannery stands on made ground. The Heights' villas on the spine; in the Roads
  the Pip and its beacon, the Teeth, the wreck, Bridge Island and the High Bridge, Gull Island; the breakwater.
- The rock. The ice rounded the tops and their up-ice (east-north-east) sides. The sea and the frost plucked the face
  block by block along its joints: the foliation, steep, dipping west-south-west, and sheet joints dipping gently to
  the sea. So the face is flat planes meeting at crisp edges, and its open joints are dark lines; the swell has worn
  round only what it reaches. A fresh scar where a slab came down, paler and sharp, its blocks at the foot. Sea caves
  along the foliation at the foot, on the low-tide shelf.
- The light. The face looks north, so only the summer evening sun reaches it: 21 June at 21:40, the sun 6 degrees up
  in the north-west (bearing 307). It is full on the west face and the point, rakes the north face, and leaves the east
  face in the northern sky's shade.

Site frame: X west (150 - the town's street y), Y south (street x + 345), z over mean sea level. It is right-handed,
so no render is mirrored. A compass bearing c lies at azimuth c + 180 in target.py's convention. The town's facts
round the Bluff are read from cache/rock/site/: the clay's ground, houses, steps, benches and landmarks, snapshot once
from blender/blockouts and only read (`--site 1` remakes it, about 3 minutes).

    Blender -b --factory-startup -P blender/parts/rock/target_site.py -- --out DIR [--grey 1] [--rebuild 1]
        [--cam NAME | x,y,lookx,looky,lookz,lens[,height]] [--vox 0.3] [--samples 96] [--w 1600 --h 900]
"""

import json
import math
import os
import sys
import time

import bpy
import mathutils
import numpy as np
import openvdb as vdb

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bluff as BL  # noqa: E402
import target as T  # noqa: E402
import target_whaleback as W  # noqa: E402
from target_whaleback import box, fbm2, smax, smin, ss, vnoise2  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
SITE = os.path.join(ROOT, "cache", "rock", "site")
NORTH = 10.0  # the true bearing of the site's -Y (the town's +x is compass 190)
T.SUN = {"azimuth": (307.0 - NORTH + 180.0) % 360.0, "elevation": 6.0, "color": (1.0, 0.68, 0.42), "energy": 7.0}
SEA = -0.3  # a falling tide: the shelf and the caves' mouths dry

CAMS = {  # x, y, look x, y, z, lens, eye over the ground or sea (or, flagged, over the datum)
    "ne16": (-110.0, -70.0, 40.0, 40.0, 12.0, 28.0, 16.0, 1),
    "ne24": (-130.0, -100.0, 40.0, 40.0, 10.0, 28.0, 24.0, 1),
    "bight": (-215.0, 10.0, 40.0, -20.0, 10.0, 24.0, 22.0, 1),
    "teeth": (-30.0, -120.0, 50.0, 40.0, 10.0, 26.0, 14.0, 1),
    # the frames: from a boat by the Teeth, the sun from the right along the face; from the cannery's quay into it
    "main": (-40.0, -125.0, 45.0, 35.0, 9.0, 28.0, 16.0, 1),
    "quay": (-250.0, 37.0, 150.0, -75.0, 6.0, 28.0, 6.5, 1),
    "shelf": (30.0, -4.0, 115.0, 60.0, 9.0, 24.0, 2.6, 1),
    "boat": (40.0, -45.0, 110.0, 55.0, 9.0, 28.0, 4.0, 1),
    "pointsea": (-5.0, -20.0, 100.0, 50.0, 10.0, 24.0, 3.0, 1),
    "teethnear": (-20.0, -70.0, 70.0, 40.0, 10.0, 28.0, 8.0, 1),
}


def compass(c):
    """A true compass bearing as a horizontal unit vector in this frame (X west, Y south)."""
    a = math.radians(c - NORTH)
    return np.array([-math.sin(a), -math.cos(a)])


def plane_normal(dip, toward):
    h = compass(toward) * math.sin(math.radians(dip))
    return np.array([h[0], h[1], math.cos(math.radians(dip))])


NFOL = plane_normal(68.0, 250.0)   # the phyllite's foliation: steep, dipping west-south-west
NSHEET = plane_normal(12.0, 0.0)   # sheet joints, dipping gently to the sea
ICE = math.degrees(math.atan2(compass(67.0)[1], compass(67.0)[0]))  # the up-ice side faces east-north-east


def joints(lo, hi, mean, spread, seed):
    """Joint planes of one set, as their offsets along its normal: irregularly spaced, as rock is."""
    rng = np.random.default_rng(seed)
    q, out = lo, []
    while q < hi:
        out.append(q)
        q += mean * rng.uniform(1 - spread, 1 + spread)
    return np.array(out, np.float64)


# -- the site, from the town plan ---------------------------------------------------------------------------------------

FOOT = ([-300, -260, -220, -180, -112, -45, 0, 25, 55, 80, 120, 150, 168],   # the face's foot (3 m contour), Y by X
        [108.0, 96.0, 82.0, 63.0, 41.0, 13.0, 8.0, 7.0, 15.0, 31.0, 69.0, 92.0, 104.0])
RIM = ([-300, -240, -180, -120, -60, 0, 40, 70, 95, 120, 150, 168],          # the height of its top
       [10.0, 14.0, 19.0, 22.0, 23.5, 24.5, 24.0, 22.0, 18.0, 12.5, 6.0, 3.0])
SHELF_W = ([-260, -200, -150, -60, 0, 60, 100, 130, 150], [0.0, 2.0, 5.0, 7.0, 9.0, 13.0, 12.0, 6.0, 0.0])


def foot_q(x):
    """The foliation's offset (q1) where it meets the face's foot at x."""
    x = np.asarray(x, float)
    return NFOL[0] * x + NFOL[1] * np.interp(x, *FOOT)


def slab_joints(lo, hi, median, sigma, least, seed):
    """Joint planes whose spacings are lognormal: many slabs near the median, a few thin ones and a few broad."""
    rng = np.random.default_rng(seed)
    q, out = lo, []
    while q < hi:
        out.append(q)
        q += min(max(least, median * math.exp(rng.normal(0.0, sigma))), 2.4 * median)
    return np.array(out, np.float64)


def build_joints():
    """The foliation's joints: the crush zones, and between them the slabs, mostly a few metres wide, some thin, some
    broad; each joint's slab knows its mass. The sheet joints, a few metres apart."""
    qm = foot_q(CRUSH)
    q1, mass = [], []
    for m, (a, b) in enumerate(zip(qm, qm[1:])):
        for q in slab_joints(a, b - 1.2, 3.8, 0.65, 1.2, 100 + m):
            q1.append(q)
            mass.append(m)
    q1.append(qm[-1])
    return np.array(q1), np.array(mass), qm, slab_joints(-60.0, 60.0, 4.5, 0.4, 1.5, 8)


MASSES = [  # ice-worn knuckles at the rim: x, y, height, stoss slope, lee slope, seed
    (24.0, 26.0, 30.0, 0.30, 1.0, 1), (-48.0, 30.0, 27.5, 0.32, 0.95, 2), (76.0, 48.0, 24.5, 0.30, 0.9, 4),
    (-122.0, 54.0, 26.0, 0.34, 0.9, 3), (-20.0, 92.0, 31.0, 0.26, 0.8, 5),
]
# The crush zones: where the foliation's weak seams meet the face's foot (x). The sea has dug them into geos and the
# frost into gullies, so they split the Bluff into masses. Each mass between two of them: its face's set-back (m), its
# rim's rise or fall (m), its turn (set-back per m along x), its lean (per m up), how round the ice left its shoulder
# (m), how much of its face was plucked (0 to 1), and how high its back domes over the gullies (m). The ice came from
# the east-north-east: the east masses are its stoss, rolled round to the sea; the point and the west masses are
# sea-cut and plucked, flat joint faces at sharp edges, and they face the evening sun.
CRUSH = [-300.0, -262.0, -220.0, -180.0, -140.0, -105.0, -70.0, -20.0, 12.0, 38.0, 62.0, 88.0, 112.0, 132.0, 200.0]
SLABS = [  # set-back, rise, turn, lean, round, plucked, dome; the sea's notch (m) and the whaleback's slope above it
    (1.0, -4.0, 0.00, 0.20, 6.0, 0.0, 2.0, 4.0, 1.10), (1.0, -4.0, 0.02, 0.22, 8.0, 0.0, 3.0, 5.0, 1.00),
    (0.0, -2.0, -0.04, 0.18, 10.0, 0.2, 4.0, 6.0, 0.90), (2.0, -1.0, 0.05, 0.20, 9.0, 0.0, 3.5, 4.5, 1.20),
    (0.0, 1.0, -0.06, 0.15, 10.0, 0.2, 4.5, 5.5, 0.95), (5.0, -3.5, 0.0, 0.20, 6.0, 0.3, 2.5, 3.5, 1.00),
    (0.0, 0.0, 0.05, 0.15, 7.0, 0.3, 4.0, 6.5, 0.85), (1.5, 1.0, -0.05, 0.14, 3.0, 0.7, 3.0, 10.0, 0.50),
    (-1.0, 2.5, 0.07, 0.06, 1.2, 1.0, 3.5, 40.0, 0.06), (2.5, 0.0, -0.03, 0.12, 0.5, 1.0, 2.0, 40.0, 0.12),
    (0.0, 1.5, 0.08, 0.07, 1.0, 1.0, 3.0, 40.0, 0.07), (4.0, -2.0, 0.0, 0.16, 1.5, 0.8, 1.5, 40.0, 0.16),
    (0.0, 1.0, -0.06, 0.10, 2.0, 0.8, 2.5, 40.0, 0.10), (0.5, 0.0, 0.0, 0.12, 3.0, 0.5, 1.5, 40.0, 0.12)]
BULGE = [5.0, 6.0, 7.0, 6.0, 7.0, 4.0, 6.0, 3.0, 1.6, 0.8, 1.2, 1.0, 1.0, 1.5]  # each mass bows out between its gullies (m)
CURVE = [0.035, 0.03, 0.03, 0.035, 0.03, 0.03, 0.025, 0.015, 0, 0, 0, 0, 0, 0]  # its back flattening as it rises (per m)
GULLY = {5: 4.5, 6: 5.5, 10: 3.0, 11: 5.0, 12: 3.5, 7: 2.0}  # crush zone index: how deep its gully cuts the rim
CAVES = [(11, 3.2, 7.5, 16.0), (10, 1.7, 3.8, 8.0), (8, 1.2, 2.6, 5.0)]  # crush zone, width, height, depth
SCAR = (50.0, 13.0, 10.0, 8.0)  # where a slab came down not long ago: x, z, half width, half height
Q1, MASS, QM, Q2 = build_joints()
QS = slab_joints(float(Q1[0]) - 5.0, float(Q1[-1]) + 5.0, 1.9, 0.45, 0.8, 33)  # the shelf's ribs: the foliation's beds
MADE_Z = 2.2
MADE = [(-172.0, 34.0), (-336.0, 34.0), (-336.0, 236.0), (-262.0, 236.0), (-238.0, 120.0), (-172.0, 66.0)]  # the cannery's ground
TEETH = [(-30.0, -96.0, 2.2, 7.0), (-48.0, -104.0, 1.4, 4.0), (-8.0, -112.0, 1.6, 5.0), (18.0, -100.0, 1.0, 3.5),
         (-70.0, -122.0, 1.8, 6.0), (-58.0, -140.0, 0.9, 3.0)]  # x, y, height, radius
PIP = (212.0, -27.0, 6.0, 14.0)


def site_snapshot():
    """The town's facts round the Bluff, read once from the clay (blender/blockouts), into cache/rock/site."""
    sys.path.insert(0, os.path.join(ROOT, "blender", "blockouts"))
    import centre_land as L
    import heart_layout as HL
    HL.lay_out()

    def site(xs, ys):
        return 150.0 - ys, xs + 345.0
    out = dict(buildings=[], steps=[], details=[], far=[])
    for b in HL.BUILDINGS:
        if -470 < b["ox"] < -40 and -160 < b["oy"] < 600:
            X, Y = site(b["ox"], b["oy"])
            out["buildings"].append(dict(name=b["name"], X=X, Y=Y, angle=b["angle"], w=b["w"], d=b["d"], base=b["base"],
                                         eave=b["eave"], pitch=b["pitch"], roof=b["roof"], role=b["role"]))
    out["steps"] = [[*site(x, y), z] for x, y, z in HL.HUNDRED_STEPS]
    for d in HL.DETAILS:
        if -470 < d["x"] < -40 and -160 < d["y"] < 600:
            dd = dict(d)
            dd["X"], dd["Y"] = site(d["x"], d["y"])
            out["details"].append(dd)
    for f in HL.FAR:
        ff = dict(f)
        ff["X"], ff["Y"] = site(f["x"], f["y"])
        if "x2" in f:
            ff["X2"], ff["Y2"] = site(f["x2"], f["y2"])
        out["far"].append(ff)
    out["breakwater"] = [list(site(x, y)) for x, y in L.BREAKWATER]
    out["far_range"] = [list(r) for r in L.FAR_RANGE]
    Xs, Ys = np.arange(-1000.0, 801.0, 4.0), np.arange(-720.0, 401.0, 4.0)
    XX, YY = np.meshgrid(Xs, Ys)
    sx, sy = YY - 345.0, 150.0 - XX
    np.savez_compressed(os.path.join(SITE, "ground.npz"), X=Xs, Y=Ys, Z=L.heights(sx, sy).astype(np.float32),
                        water=L.is_water(sx, sy))
    json.dump(out, open(os.path.join(SITE, "bluff-site.json"), "w"), indent=1, default=float)


GROUND = None


def town(x, y):
    """The town's drawn ground, bilinear (4 m)."""
    global GROUND
    if GROUND is None:
        g = np.load(os.path.join(SITE, "ground.npz"))
        GROUND = (g["X"], g["Y"], g["Z"].astype(np.float32))
    gx, gy, gz = GROUND
    fx = np.clip((x - gx[0]) / 4.0, 0, len(gx) - 1.001)
    fy = np.clip((y - gy[0]) / 4.0, 0, len(gy) - 1.001)
    ix, iy = np.floor(fx).astype(np.int64), np.floor(fy).astype(np.int64)
    tx, ty = fx - ix, fy - iy
    return ((gz[iy, ix] * (1 - tx) + gz[iy, ix + 1] * tx) * (1 - ty)
            + (gz[iy + 1, ix] * (1 - tx) + gz[iy + 1, ix + 1] * tx) * ty)


def face_line(x):
    return np.interp(x, *FOOT).astype(np.float32)


def hull(x, y, cx, cy, hm, stoss, lee, seed, k):
    """target_whaleback's ice-worn mass, its stoss turned to face up-ice (east-north-east)."""
    rng = np.random.default_rng(seed)
    roof = (hm + 0 * x + 0 * y).astype(np.float32)
    for az, sl in ((0, stoss), (35, stoss * 1.3), (-35, stoss * 1.3), (75, 0.6 * lee), (-75, 0.6 * lee),
                   (115, 0.85 * lee), (-115, 0.85 * lee), (155, lee), (-155, lee), (180, lee * 1.1)):
        a = math.radians(az + ICE + rng.uniform(-12, 12))
        s = sl * rng.uniform(0.8, 1.25)
        c = rng.uniform(1.5, 4.5) if abs(az) < 60 else rng.uniform(0.5, 2.5)
        z = hm + c - s * ((x - cx) * math.cos(a) + (y - cy) * math.sin(a))
        roof = smin(roof, z.astype(np.float32), k)
    return roof


def slab_table(values, soften):
    """A value per mass as a function of q1, its steps softened over `soften` metres."""
    q = np.linspace(QM[0] - 40.0, QM[-1] + 40.0, 2400)
    m = np.clip(np.searchsorted(QM, q) - 1, 0, len(SLABS) - 1)
    v = np.asarray(values, float)[m]
    n = max(1, int(soften / (q[1] - q[0])))
    v = np.convolve(np.pad(v, n, mode="edge"), np.ones(2 * n + 1) / (2 * n + 1), mode="same")[n:-n]
    return q, v


RISE = slab_table([s_[1] for s_ in SLABS], 7.0)
ROUND = slab_table([s_[4] for s_ in SLABS], 10.0)


def top(x, y):
    """The ground over the face: the rim's height along it, each mass its own rise, the crush zones' gullies cut down
    into it; the town's hill from 60 m in (the drawn ground is not trusted nearer, where its cliff band digs a trench);
    ice-worn knuckles at the rim, stepped on their lee."""
    fl = face_line(x)
    d = y - fl
    rim = np.interp(x, *RIM).astype(np.float32)
    q1 = NFOL[0] * x + NFOL[1] * y + NFOL[2] * rim
    near = 1 - ss(8.0, 45.0, d)
    rim = rim + np.interp(q1, *RISE) * near
    m = np.clip(np.searchsorted(QM, q1) - 1, 0, len(SLABS) - 1)
    u = (q1 - 0.5 * (QM[m] + QM[m + 1])) / (0.5 * (QM[m + 1] - QM[m]))
    rim = rim + np.array([s_[6] for s_ in SLABS], np.float32)[m] * (1 - np.clip(u, -1, 1) ** 2) * (1 - ss(15.0, 55.0, d))
    for i, depth in GULLY.items():
        rim = rim - depth * np.exp(-((q1 - QM[i]) / 4.0) ** 2) * (1 - ss(10.0, 40.0, d))
    far = town(x, np.maximum(y, fl + 60.0))
    w = ss(12.0, 60.0, d)
    h = rim * (1 - w) + far * w + 1.2 * fbm2(x / 40.0, y / 40.0, 7) * (1 - w)
    for cx, cy, hm, stoss, lee, seed in MASSES:
        dome = hull(x, y, cx, cy, hm, stoss, lee, seed, 3.0)
        down = -((x - cx) * math.cos(math.radians(ICE)) + (y - cy) * math.sin(math.radians(ICE)))  # down-ice
        lee_side = ss(3.0, 10.0, down) * ss(0.0, 2.0, dome - h)
        f = dome / 2.6
        stair = 2.6 * (np.floor(f) + ss(0.82, 1.0, f - np.floor(f)))  # the blocks the ice pulled out: treads, sharp risers
        dome = dome * (1 - lee_side) + stair * lee_side
        h = smax(h, dome + 0.4 * fbm2(x / 9.0, y / 9.0, 11), 3.0)
    e = ss(-262.0, -232.0, x)  # the hill's east flank falls to the cannery's made ground
    return (MADE_Z + (h - MADE_Z) * e).astype(np.float32)


def mass_sides():
    """Each mass's face, and the slabs it stands in. The mass gives the plane (set back, turned, leaning, bowed between
    its gullies, notched where the swell reaches). Each slab stands a little in or out from the one beside it, as the
    blocks behind came out: most flush with their neighbour, so the joint between them is only a line in the stone,
    some a step whose edge catches the light, more where the sea and the frost plucked the mass. Where a sheet joint
    let the upper part of a run of slabs go, the face steps back above it in a ledge that runs a few slabs and ends;
    a face only recedes upward, as blocks come out from the lip down."""
    sl = np.array(SLABS, np.float32)
    xt = np.linspace(-320.0, 220.0, 5000)
    qc, hw = 0.5 * (QM[:-1] + QM[1:]), 0.5 * (QM[1:] - QM[:-1])
    xc = np.interp(qc, foot_q(xt), xt)  # where each mass's middle meets the foot
    n1, n2 = len(MASS), len(Q2)  # slabs (one fewer than the joints) and sheet joints
    rng = np.random.default_rng(1989)
    pl = sl[MASS, 5]
    col = np.zeros(n1, np.float32)
    for j in range(1, n1):
        if MASS[j] != MASS[j - 1]:
            continue  # each mass's slabs start flush with its plane
        if rng.random() < 0.35 + 0.35 * pl[j]:
            col[j] = col[j - 1] + rng.choice([-1.0, 1.0]) * rng.uniform(0.35, 1.5) * (0.4 + 0.6 * pl[j])
        else:
            col[j] = col[j - 1]
    col -= np.array([col[MASS == m].mean() if (MASS == m).any() else 0.0 for m in range(len(SLABS))])[MASS]
    twist = rng.normal(0.0, 0.02 + 0.03 * pl).astype(np.float32)  # each slab's face turned a little on its own
    step = np.zeros((n1, n2), np.float32)
    for k in range(n2):
        j = 0
        while j < n1:
            if rng.random() < 0.10 + 0.25 * pl[j]:
                run = int(rng.integers(2, 7))
                step[j:j + run, k] = rng.uniform(0.4, 1.4) * (0.4 + 0.6 * pl[j])
                j += run + int(rng.integers(1, 6))
            else:
                j += 1
    # the fresh scar: the slabs where it stands lost their upper parts above one sheet joint not long ago
    sx, sz, shw, shh = SCAR
    xs_ = np.interp(0.5 * (Q1[:-1] + Q1[1:]), foot_q(xt), xt)  # each slab's middle at the foot
    base = np.array([sx, face_line(np.array([sx]))[0], sz - shh]) @ NSHEET
    step[np.abs(xs_ - sx) < shw, int(np.argmin(np.abs(Q2 - base)))] += 1.6
    cum = np.concatenate([np.zeros((n1, 1), np.float32), np.cumsum(step, 1)], 1)  # set-back above each sheet joint
    return dict(back=sl[:, 0], turn=sl[:, 2], lean=sl[:, 3], notch=sl[:, 7], slope=sl[:, 8], qc=qc, hw=hw,
                bulge=np.array(BULGE, np.float32), curve=np.array(CURVE, np.float32), xc=xc.astype(np.float32),
                col=col, twist=twist, cum=cum)


B = None


def face_sdf(X, Y, Z, yp, k):
    """The face as the slabs between the foliation's joints, each its mass's plane set in or out and stepped back
    above its ledges: the union of a point's slab and the two beside it, their edges rounded over k."""
    q1 = NFOL[0] * X + NFOL[1] * Y + NFOL[2] * Z
    q2 = NSHEET[0] * X + NSHEET[1] * Y + NSHEET[2] * Z
    i1 = np.clip(np.searchsorted(Q1, q1) - 1, 1, len(Q1) - 3)
    i2 = np.clip(np.searchsorted(Q2, q2), 0, len(Q2))
    best = np.full(np.broadcast(X, Y, Z).shape, np.inf, np.float32)
    swell = 0.6 * ss(5.0, 1.0, Z) * (Z > -2)  # the swell's reach undercut, then worn round
    for a in (-1, 0, 1):
        j = i1 + a
        m = MASS[j]
        lo, hi = Q1[j], Q1[j + 1]
        up = 1.5 * np.logaddexp(0.0, (Z - B["notch"][m]) / 1.5)
        u = np.clip((q1 - B["qc"][m]) / B["hw"][m], -1.3, 1.3)
        lean = B["lean"][m] * Z + (B["slope"][m] - B["lean"][m]) * up + B["curve"][m] * up * up + B["bulge"][m] * u * u
        plane = (B["back"][m] + B["col"][j] + swell + lean + B["turn"][m] * (X - B["xc"][m])
                 + B["twist"][j] * (q1 - 0.5 * (lo + hi)))
        # each ledge a clean tread: the slab between two sheet joints is the plane at its own set-back, cut off at
        # the joint above it; the union of a point's band and the two beside it
        face = np.full_like(best, np.inf)
        for b in (-1, 0, 1):
            i = np.clip(i2 + b, 0, len(Q2))
            roof = np.where(i < len(Q2), Q2[np.minimum(i, len(Q2) - 1)], 1e9)
            face = np.minimum(face, smax((plane + B["cum"][j, i] - yp) * 0.9, q2 - roof, k))
        d = smax(smax(lo - q1, q1 - hi, k), face, k)
        best = np.minimum(best, d)
    return best


def land_sdf(X, Y, Z):
    """Rock and turf < 0 at the points (X, Y, Z), arrays that broadcast."""
    fl = face_line(X)
    yp = Y - fl
    tp = top(X[..., 0] if X.ndim == 3 else X, Y[..., 0] if Y.ndim == 3 else Y)
    tp = tp[..., None] if X.ndim == 3 else tp
    bare = ss(0.22, 0.4, fbm2(X / 7.0, Y / 7.0, 51))
    dome = (Z - tp - 0.6 * bare) * 0.8
    k = (0.10 + 0.9 * ss(3.5, 0.5, Z)).astype(np.float32)  # crisp, but round where the swell reaches
    face = face_sdf(X, Y, Z, yp, k)
    sx, sz, hw, hh = SCAR
    q1 = NFOL[0] * X + NFOL[1] * Y + NFOL[2] * Z
    rnd = np.interp(q1, *ROUND).astype(np.float32)
    lip = rnd * (1 - 0.6 * ss(1.0, 0.6, np.hypot((X - sx) / hw, (Z - sz) / (hh + 6))))  # the scar's lip is sharp
    rock = smax(dome, face, lip)
    for i, w0, h0, depth in CAVES:  # in the crush zones, at the foot
        across = q1 - QM[i]
        w = w0 * np.maximum(1 - (Z / h0) ** 2, 0) ** 0.55
        slot = np.maximum(np.maximum(np.abs(across) - w / 2, yp - depth), -1.2 - Z)
        rock = smax(rock, -slot, 0.25)
    # the low-tide shelf the sea cut at the foot: the foliation's beds left standing as ribs that run out into the
    # water, each rising across its width to a crest the sea has worn round and dropping at the next joint into the
    # swell's gully, its crest falling seaward and ending at its own length
    sw = np.interp(X, *SHELF_W).astype(np.float32)
    q1 = NFOL[0] * X + NFOL[1] * Y
    i_s = np.clip(np.searchsorted(QS, q1) - 1, 0, len(QS) - 2)
    rng = np.random.default_rng(31)
    crest0, fall, depth, reach = (rng.uniform(lo, hi, len(QS))[i_s] for lo, hi in
                                  ((0.5, 1.3), (0.04, 0.12), (0.4, 1.0), (0.35, 1.25)))
    t = (q1 - QS[i_s]) / (QS[i_s + 1] - QS[i_s])
    out = np.maximum(-yp, 0.0)  # metres out from the foot
    crest = crest0 - fall * out + 0.06 * fbm2(X / 4.0, Y / 4.0, 31)
    bed = crest - depth * (1 - ss(0.0, 0.8, t) * ss(1.0, 0.86, t))
    end = ss(reach * sw + 1.0, reach * sw - 1.0, out) * ss(-sw - 2.5, -sw + 0.8, yp)
    bed = bed * end - 3.6 * (1 - end)
    bed = np.where(sw > 0.5, bed, -3.6)
    rock = smin(rock, (Z - bed) * 0.9, 0.12)
    for i, (tx, ty, th, tr) in enumerate(TEETH + [PIP]):  # the skerries, if they reach the grid
        hk = hull(X, Y, tx, ty, th, 0.25, 0.7, 40 + i, 0.6)
        rock = smin(rock, (Z - hk) * 0.85, 0.6)
    rock = np.maximum(rock, -4.0 - Z)
    # turf on the backs, over the lip and a little down it, torn; bare on the windswept knolls
    turf = smax((Z - tp - 0.16) * 0.8, face - 0.12, np.maximum(1.4, 0.55 * rnd))
    turf = np.maximum(turf, (tp - 1.0 - 0.9 * (0.5 + 0.5 * fbm2(X / 2.5, Y / 2.5, 61))) - Z)
    turf = np.maximum(turf, 4.0 - Z)
    return rock.astype(np.float32), turf.astype(np.float32)


# -- the band round the face: a grid sheared to follow it ----------------------------------------------------------------

def band(vox, rebuild, cache):
    """The rock and turf within the band from 26 m out to 44 m in, on a grid sheared along the face line, as meshes."""
    if os.path.exists(cache) and not rebuild:
        return np.load(cache)
    t0 = time.time()
    xs = np.arange(-262.0, 166.0 + 1e-6, vox, dtype=np.float32)
    ys = np.arange(-26.0, 44.0 + 1e-6, vox, dtype=np.float32)
    zs = np.arange(-5.0, 34.0 + 1e-6, vox, dtype=np.float32)
    rock = np.empty((len(xs), len(ys), len(zs)), np.float32)
    turf = np.empty_like(rock)
    step = 48
    for i in range(0, len(xs), step):
        X = xs[i:i + step, None, None]
        Y = face_line(X) + ys[None, :, None]
        Z = zs[None, None, :]
        X, Y, Z = np.broadcast_arrays(X, Y, Z)
        r, t = land_sdf(X, Y, Z)
        rock[i:i + step], turf[i:i + step] = r, t
    print(f"band sdf {rock.shape}: {time.time() - t0:.0f}s")

    def surface(D):
        g = vdb.FloatGrid(1.0)
        g.copyFromArray(np.ascontiguousarray(np.clip(D / vox, -1.0, 1.0)))
        p, t, q = g.convertToPolygons(0.0, 0.0)
        p = np.asarray(p, np.float32)
        x = xs[0] + p[:, 0] * vox
        p = np.stack([x, face_line(x) + ys[0] + p[:, 1] * vox, zs[0] + p[:, 2] * vox], -1)
        t, q = np.asarray(t, np.int32).reshape(-1, 3), np.asarray(q, np.int32).reshape(-1, 4)
        c = p[q].mean(1)
        i = int(np.argmax(c[:, 2]))
        n = np.cross(p[q[i, 2]] - p[q[i, 0]], p[q[i, 3]] - p[q[i, 1]])
        if n[2] < 0:
            q, t = q[:, ::-1].copy(), t[:, ::-1].copy()
        return p, t, q
    rp, rt, rq = surface(rock)
    tp, tt, tq = surface(turf)
    np.savez(cache, rp=rp, rt=rt, rq=rq, tp=tp, tt=tt, tq=tq)
    print(f"band surfaces: {time.time() - t0:.0f}s")
    return np.load(cache)


def snap(ob, vox):
    """The mesher chamfers every edge by a voxel. Put each vertex back on the rock's own planes (cliff.py's way): off
    the edges onto its plane, at an edge onto the crease where the planes round it meet (dual contouring's point), so
    the planes are flat and their edges crisp, and only what the field itself rounds (the ice, the sea) stays round."""
    me = ob.data
    V0 = np.zeros(len(me.vertices) * 3, np.float32)
    me.vertices.foreach_get("co", V0)
    V0 = V0.reshape(-1, 3).astype(np.float64)
    E = np.zeros(len(me.edges) * 2, np.int32)
    me.edges.foreach_get("vertices", E)
    E = E.reshape(-1, 2)
    me.calc_loop_triangles()
    F = np.zeros(len(me.loop_triangles) * 3, np.int32)
    me.loop_triangles.foreach_get("vertices", F)
    F = F.reshape(-1, 3)

    def sd(P):
        out = np.empty(len(P))
        for i in range(0, len(P), 150_000):
            q = P[i:i + 150_000].astype(np.float32)
            out[i:i + 150_000] = land_sdf(q[:, 0], q[:, 1], q[:, 2])[0]
        return out
    h = 0.03
    tet = np.array([[1, 1, 1], [1, -1, -1], [-1, 1, -1], [-1, -1, 1]], float)
    dv = [sd(V0 + h * t_) for t_ in tet]
    g = sum(d_[:, None] * t_ for d_, t_ in zip(dv, tet))
    g /= np.maximum(np.linalg.norm(g, axis=1), 1e-9)[:, None]
    D = np.einsum("ij,ij->i", g, V0) - sum(dv) / 4  # each vertex's tangent plane: g . x = D
    A = np.einsum("ni,nj->nij", g, g)
    b = g * (D - np.einsum("ij,ij->i", g, V0))[:, None]
    for i_, j_ in ((E[:, 0], E[:, 1]), (E[:, 1], E[:, 0])):  # and its neighbours' planes
        res = D[j_] - np.einsum("ij,ij->i", g[j_], V0[i_])
        for r_ in range(3):
            np.add.at(b[:, r_], i_, g[j_, r_] * res)
            for c_ in range(3):
                np.add.at(A[:, r_, c_], i_, g[j_, r_] * g[j_, c_])
    w, Q = np.linalg.eigh(A)
    inv = np.where(w > 0.05 * w[:, -1:], 1 / np.maximum(w, 1e-12), 0.0)  # planes under ~25 degrees apart: one
    mv = np.einsum("nij,nj,nkj,nk->ni", Q, inv, Q, b)
    ln = np.linalg.norm(mv, axis=1)
    V = V0 + mv * np.minimum(1.0, vox / np.maximum(ln, 1e-9))[:, None]

    def normals(P):
        return np.cross(P[F[:, 1]] - P[F[:, 0]], P[F[:, 2]] - P[F[:, 0]])
    n0 = normals(V0)
    for it in range(12):  # a face that turned over goes back toward where it was
        n1 = normals(V)
        l0, l1 = np.linalg.norm(n0, axis=1), np.linalg.norm(n1, axis=1)
        bad = (np.einsum("ij,ij->i", n0, n1) < 0.3 * l0 * l1) & (l1 > 0.2 * l0)
        if not bad.any():
            break
        back = np.unique(F[bad])
        V[back] = V0[back] if it == 11 else 0.5 * (V[back] + V0[back])
    moved = np.linalg.norm(V - V0, axis=1)
    print(f"snap: {(moved > 0.005).mean():.0%} of vertices moved, mean {moved[moved > 0.005].mean() * 100:.1f} cm")
    me.vertices.foreach_set("co", V.astype(np.float32).ravel())
    me.update()


def flat(ob, tris):
    """Down to `tris` triangles by collapse, and shaded as planes: normals weighted by face area, edges over 34
    degrees sharp."""
    me = ob.data
    me.calc_loop_triangles()
    if len(me.loop_triangles) > tris:
        m = ob.modifiers.new("lod", "DECIMATE")
        m.decimate_type, m.ratio, m.use_collapse_triangulate = "COLLAPSE", tris / len(me.loop_triangles), True
        dg = bpy.context.evaluated_depsgraph_get()
        new = bpy.data.meshes.new_from_object(ob.evaluated_get(dg))
        ob.modifiers.clear()
        ob.data = new
    ob.data.shade_smooth()
    ob.data.set_sharp_from_angle(angle=math.radians(34))
    wn = ob.modifiers.new("planes", "WEIGHTED_NORMAL")
    wn.mode, wn.keep_sharp = "FACE_AREA", True


# -- the rest of the place ---------------------------------------------------------------------------------------------

def inside(poly, x, y):
    """Points in a polygon (even-odd)."""
    res = np.zeros(np.broadcast(x, y).shape, bool)
    n = len(poly)
    for i in range(n):
        x1, y1 = poly[i]
        x2, y2 = poly[(i + 1) % n]
        c = ((y1 > y) != (y2 > y)) & (x < (x2 - x1) * (y - y1) / (y2 - y1 + 1e-9) + x1)
        res ^= c
    return res


def hill(x, y):
    """The ground inland of the band, and the shore beyond its ends: top() on land, the town's ground at sea."""
    d = y - face_line(x)
    h = np.where(d > 0, top(x, y), town(x, y))
    in_band = (x > -262.0) & (x < 166.0) & (d < 40.0)
    return np.where(in_band | inside(MADE, x, y), -20.0, h)


def town_ground(x, y):
    """The town's own ground beyond the hill: the Basin, the Holm, the islands, the far shores."""
    mine = (x > -330.0) & (x < 166.0) & (y > -30.0) & (y < 330.0)
    return np.where(mine, -20.0, town(x, y))


def footprint(b):
    """A clay building's corners in this frame: (ox, oy) is a corner, w runs along its angle, d across it."""
    c, s_ = math.cos(math.radians(b["angle"])), math.sin(math.radians(b["angle"]))
    return [(b["X"] - (x * s_ + y * c), b["Y"] + (x * c - y * s_)) for x, y in ((0, 0), (b["w"], 0), (b["w"], b["d"]), (0, b["d"]))]


def centred(cx, cy, ang, length, width):
    """Corners of a box centred at (cx, cy), its length along ang (degrees, in this frame)."""
    u = np.array([math.cos(math.radians(ang)), math.sin(math.radians(ang))]) * length / 2
    v = np.array([-math.sin(math.radians(ang)), math.cos(math.radians(ang))]) * width / 2
    c = np.array([cx, cy])
    return [tuple(c - u - v), tuple(c + u - v), tuple(c + u + v), tuple(c - u + v)]


def box_mesh(name, corners, base, eave, pitch=0.0, roof="flat", below=3.0):
    """A grey house from below the ground to its eave, under a roof: "eaves" (ridge along the first edge), "gable"
    (ridge across it), "hip", or flat."""
    p = [np.array(c, float) for c in corners]
    if roof == "gable":
        p = p[1:] + p[:1]
    rise = 0.0 if roof in ("flat", "tower", "mansard") else 0.5 * np.linalg.norm(p[3] - p[0]) * math.tan(math.radians(pitch))
    z0, z1, z2 = base - below, base + eave, base + eave + rise
    verts = [(*q, z0) for q in p] + [(*q, z1) for q in p]
    faces = [(3, 2, 1, 0), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
    if rise > 0:
        m0, m1 = (p[0] + p[3]) / 2, (p[1] + p[2]) / 2
        if roof == "hip":
            u = (m1 - m0) / np.linalg.norm(m1 - m0) * min(0.45 * np.linalg.norm(p[3] - p[0]), 0.45 * np.linalg.norm(m1 - m0))
            m0, m1 = m0 + u, m1 - u
        verts += [(*m0, z2), (*m1, z2)]
        faces += [(4, 5, 9, 8), (6, 7, 8, 9), (5, 6, 9), (7, 4, 8)]
    else:
        faces += [(4, 5, 6, 7)]
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], faces)
    me.update()
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    return ob


def cylinder(name, x, y, z0, z1, r, n=16):
    me = bpy.data.meshes.new(name)
    a = np.linspace(0, 2 * np.pi, n, endpoint=False)
    v = [(x + r * math.cos(t), y + r * math.sin(t), z) for z in (z0, z1) for t in a]
    f = [tuple(range(n))[::-1], tuple(range(n, 2 * n))] + [(i, (i + 1) % n, n + (i + 1) % n, n + i) for i in range(n)]
    me.from_pydata(v, [], f)
    me.update()
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    return ob


ROUTE = [(153.0, 2.2), (146.0, 2.2), (128.0, 7.0), (122.0, 7.0), (104.0, 12.0), (97.0, 12.0), (79.0, 17.0),
         (72.0, 17.0), (64.0, 21.5), (59.0, 21.5)]  # the Hundred Steps up the shoulder's face: (x, height), flights between landings
LANDINGS = [3, 5, 7]  # the landings with a bench


def face_at(x, z):
    """Where the face stands at x and height z: a ray from the sea."""
    dg = bpy.context.evaluated_depsgraph_get()
    y0 = float(face_line(np.array([x]))[0]) - 30.0
    hit = bpy.context.scene.ray_cast(dg, mathutils.Vector((x, y0, z)), mathutils.Vector((0, 1, 0)), distance=80.0)
    return hit[1].y if hit[0] else y0 + 30.0


def face_stair(name, width=2.2):
    """The Hundred Steps as built against the face: flights of 17 cm risers and landings on a stone wall corbelled
    out from the rock, a rail on the sea side. Returns the stair and its landings (x, y, z, along)."""
    verts, faces = [], []

    def quad(a, b, c, d):
        n = len(verts)
        verts.extend([a, b, c, d])
        faces.append((n, n + 1, n + 2, n + 3))
    pts = []
    for (x0, z0), (x1, z1) in zip(ROUTE, ROUTE[1:]):
        n = max(2, int(abs(x1 - x0) / 0.5))
        for i in range(n):
            t = i / n
            x, z = x0 + (x1 - x0) * t, z0 + (z1 - z0) * t
            pts.append((x, z))
    pts.append(ROUTE[-1])
    inner = [face_at(x, z + 0.6) - 0.05 for x, z in pts]
    inner = np.array(inner)
    inner = np.minimum(inner, np.convolve(np.pad(inner, 4, mode="edge"), np.ones(9) / 9, mode="same")[4:-4])
    landings = []
    for k in range(len(pts) - 1):
        (x0, z0), (x1, z1) = pts[k], pts[k + 1]
        y0, y1 = inner[k], inner[k + 1]
        o0, o1 = y0 - width, y1 - width
        rise = z1 - z0
        if abs(rise) < 1e-3:
            quad((x0, y0, z0), (x1, y1, z1), (x1, o1, z1), (x0, o0, z0))
        else:  # treads and risers along this sample
            m = max(1, int(round(abs(rise) / 0.17)))
            for i in range(m):
                xa, xb = x0 + (x1 - x0) * i / m, x0 + (x1 - x0) * (i + 1) / m
                ya, yb = y0 + (y1 - y0) * i / m, y0 + (y1 - y0) * (i + 1) / m
                z = z0 + rise * i / m
                zn = z0 + rise * (i + 1) / m
                quad((xa, ya, zn), (xb, yb, zn), (xb, yb - width, zn), (xa, ya - width, zn))
                quad((xa, ya, z), (xa, ya, zn), (xa, ya - width, zn), (xa, ya - width, z))
        bot0, bot1 = max(z0 - 2.6, -0.5), max(z1 - 2.6, -0.5)
        quad((x0, o0, bot0), (x1, o1, bot1), (x1, o1, z1), (x0, o0, z0))       # the wall's face
        quad((x0, o0, bot0), (x0, y0, bot0 + 1.5), (x1, y1, bot1 + 1.5), (x1, o1, bot1))  # its corbel, back to the rock
        quad((x0, o0 + 0.05, z0 + 0.95), (x1, o1 + 0.05, z1 + 0.95), (x1, o1 + 0.05, z1 + 1.0), (x0, o0 + 0.05, z0 + 1.0))
        if k % 6 == 0:
            quad((x0 - 0.03, o0 + 0.05, z0), (x0 + 0.03, o0 + 0.05, z0), (x0 + 0.03, o0 + 0.05, z0 + 1.0),
                 (x0 - 0.03, o0 + 0.05, z0 + 1.0))
    for li in LANDINGS:
        (xa, za), (xb, _) = ROUTE[li], ROUTE[li + 1]
        xm = 0.5 * (xa + xb)
        k = int(np.argmin([abs(p[0] - xm) + abs(p[1] - za) for p in pts]))
        landings.append((xm, inner[k], za))
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], faces)
    me.update()
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    return ob, landings


def person(name, x, y, z, facing=0.0):
    """A grown person for scale: 1.75 m, a coat, standing."""
    obs = [cylinder(name + "-legs", x, y, z, z + 0.85, 0.15, 10), cylinder(name + "-coat", x, y, z + 0.8, z + 1.5, 0.22, 10)]
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.12, location=(x, y, z + 1.63), segments=12, ring_count=8)
    obs.append(bpy.context.active_object)
    return obs


def far_range():
    """The far range's bearings, heights and distances, read from the clay's source without running it."""
    import ast
    src = open(os.path.join(ROOT, "blender", "blockouts", "centre_land.py")).read()
    for node in ast.parse(src).body:
        if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == "FAR_RANGE":
            return ast.literal_eval(node.value)


def mountains(far_range):
    """The far range in the east and south-east, 20 to 35 km off, as one silhouette ring."""
    bear = np.array([r[0] for r in far_range], float)
    hgt = np.array([r[1] for r in far_range], float)
    dist = np.array([r[2] for r in far_range], float)
    b = np.linspace(bear[0] - 15, bear[-1] + 15, 360)
    hh = np.interp(b, bear, hgt) * (0.75 + 0.35 * (0.5 + 0.5 * vnoise2(b / 3.0, b * 0 + 0.5, 3))) * ss(bear[0] - 15, bear[0], b) * ss(bear[-1] + 15, bear[-1], b)
    dd = np.interp(b, bear, dist)
    verts, faces = [], []
    for i, (bb, h, d) in enumerate(zip(b, hh, dd)):
        p = compass(bb) * d
        verts += [(p[0], p[1], -200.0), (p[0], p[1], max(h, 0.0) - d * d / (2 * 6.371e6))]
        if i:
            faces.append((2 * i - 2, 2 * i, 2 * i + 1, 2 * i - 1))
    me = bpy.data.meshes.new("mountains")
    me.from_pydata(verts, [], faces)
    me.update()
    ob = bpy.data.objects.new("mountains", me)
    bpy.context.scene.collection.objects.link(ob)
    return ob


def swell_height(x, y):
    """The swell from the Roads' mouth (bearing 340), long-crested, steepening and breaking where the shelf rises."""
    k = compass(340.0 + 180.0)  # the way it runs
    s = (x * k[0] + y * k[1]) / 38.0 * 2 * np.pi + 0.7 * fbm2(x / 70.0, y / 70.0, 101)
    d = y - face_line(x)
    shoal = ss(-60.0, -12.0, d)
    crest = (0.5 + 0.5 * np.cos(s)) ** (3.0 + 4.0 * shoal)
    h = (0.55 + 0.35 * shoal) * crest - 0.18 + 0.06 * fbm2(x / 3.0, y / 3.0, 103)
    edge = ss(-280.0, -200.0, x) * ss(200.0, 160.0, x) * ss(-200.0, -150.0, y)
    return SEA + h * edge


def build(out, grey, vox):
    S = json.load(open(os.path.join(SITE, "bluff-site.json")))
    global B
    B = mass_sides()
    L = band(vox, BL.arg("--rebuild"), os.path.join(out, "band.npz"))
    rock, turf = W.mesh("rock", L["rp"], L["rt"], L["rq"]), W.mesh("turf", L["tp"], L["tt"], L["tq"])
    snap(rock, vox)
    flat(rock, int(BL.arg("--tris", 900_000)))
    rock.data.calc_loop_triangles()
    print(f"rock {len(rock.data.loop_triangles)} triangles, turf {len(turf.data.polygons)} faces")
    land = [W.heightfield("hill", -330.0, 166.0, -30.0, 330.0, 1.5, hill),
            W.heightfield("town", -1000.0, 800.0, -720.0, 400.0, 4.0, town_ground)]
    # the cannery's made ground and the quay walls round it
    xs = np.array([p[0] for p in MADE])
    ys = np.array([p[1] for p in MADE])
    made = W.heightfield("made", float(xs.min()), float(xs.max()), float(ys.min()), float(ys.max()), 1.0,
                         lambda x, y: np.where(inside(MADE, x, y), MADE_Z + 0.05, -20.0))
    skerries = []
    for i, (tx, ty, th, tr) in enumerate(TEETH + [PIP]):
        skerries.append(W.heightfield(f"skerry{i}", tx - tr * 2.5, tx + tr * 2.5, ty - tr * 2.5, ty + tr * 2.5, 0.4,
                                      lambda x, y, a=(tx, ty, th, i): hull(x, y, a[0], a[1], a[2], 0.25, 0.7, 40 + a[3], 0.6)
                                      + 0.1 * fbm2(x / 2.0, y / 2.0, 41)))
    sea = W.heightfield("sea", -6000.0, 6000.0, -9000.0, 2000.0, 100.0, lambda x, y: x * 0 + SEA)
    swell = W.heightfield("swell", -280.0, 200.0, -200.0, 110.0, 0.6, swell_height)
    built = [box_mesh(b["name"], footprint(b), b["base"], b["eave"], b["pitch"], b["roof"]) for b in S["buildings"]]
    # the cannery (the clay has only its chimney): long halls on the made ground along the bight's quay, the packing
    # hall at the face's foot, the smoke house between, the boiler house under the chimney
    for name, cx, cy, ang, l, w, e, p in (("the cannery's long hall", -300.0, 150.0, 90.0, 74.0, 18.0, 8.5, 28.0),
                                         ("the cannery's packing hall", -226.0, 62.0, 22.0, 46.0, 15.0, 7.0, 26.0),
                                         ("the smoke house", -270.0, 98.0, 90.0, 22.0, 10.0, 6.0, 40.0),
                                         ("the boiler house", -312.0, 206.0, 0.0, 14.0, 12.0, 7.0, 30.0)):
        built.append(box_mesh(name, centred(cx, cy, ang, l, w), MADE_Z, e, p, "eaves"))
    for f in S["far"]:
        X, Y = f["X"], f["Y"]
        g = float(town(np.array([X]), np.array([Y]))[0])
        if f["kind"] == "chimney":
            built.append(cylinder(f["name"], X, Y, 0.0, MADE_Z + f["h"], f["w"] / 2))
        elif f["kind"] == "mast":
            built.append(cylinder(f["name"], X, Y, -2.0, f["h"] - 2.0, f["w"] / 2, 8))
        elif f["kind"] == "bow":
            built.append(box_mesh(f["name"], centred(X, Y, 30.0, 9.0, f["w"]), -1.0, f["h"]))
        elif f["kind"] == "ruin":
            for k, (dx, dy, l, w) in enumerate(((0, -5, 30, 0.9), (0, 5, 30, 0.9), (-15, 0, 0.9, 10), (15, 0, 0.9, 10))):
                built.append(box_mesh(f"{f['name']} {k}", centred(X + dx, Y + dy, 0.0, l, w), g, 7.0 - 2.5 * (k % 2)))
        elif f["kind"] in ("tower", "block"):
            built.append(box_mesh(f["name"], centred(X, Y, 0.0, f["w"], f["w"] * (0.6 if f["kind"] == "block" else 1)),
                                  g, f["h"]))
        elif f["kind"] == "cranes":
            for k in range(3):
                built.append(box_mesh(f"{f['name']} {k}", centred(X + 22 * k - 22, Y, 0.0, 2.0, 2.0), g, f["h"]))
                built.append(box_mesh(f"{f['name']} jib {k}", centred(X + 22 * k - 22, Y - 12, 90.0, 34.0, 1.2),
                                      g + f["h"] - 3.0, 1.5, below=0.0))
        elif f["kind"] == "condeep":
            built.append(cylinder(f["name"] + " cells", X, Y, -10.0, 40.0, 55.0, 24))
            for k in range(3):
                a = k * 2 * math.pi / 3
                built.append(cylinder(f"{f['name']} shaft {k}", X + 22 * math.cos(a), Y + 22 * math.sin(a),
                                      40.0, 40.0 + f["h"] - 18.0 * k, 7.0, 16))
        elif f["kind"] == "bridge":
            x0, y0, x1, y1 = X, Y, f["X2"], f["Y2"]
            n = 24
            ang = math.degrees(math.atan2(y1 - y0, x1 - x0))
            span = math.hypot(x1 - x0, y1 - y0) / n
            for k in range(n):
                t = (k + 0.5) / n
                zd = 8.0 + (f["h"] - 8.0) * math.sin(math.pi * t)
                cx, cy = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
                built.append(box_mesh(f"{f['name']} deck {k}", centred(cx, cy, ang, span + 0.3, f["w"]), zd - 1.2, 1.2,
                                      below=0.0))
                if k % 4 == 2:
                    built.append(cylinder(f"{f['name']} pier {k}", cx, cy, -5.0, zd - 1.2, 1.6, 8))
    bw = S["breakwater"]
    for i, ((x0, y0), (x1, y1)) in enumerate(zip(bw, bw[1:])):
        built.append(box_mesh(f"the breakwater {i}", centred((x0 + x1) / 2, (y0 + y1) / 2,
                              math.degrees(math.atan2(y1 - y0, x1 - x0)), math.hypot(x1 - x0, y1 - y0) + 4, 6.0), 0.5, 2.0))
    built.append(cylinder("the breakwater's light", bw[-1][0] + 2.0, bw[-1][1] - 1.0, 2.5, 9.0, 1.1, 12))
    details = []
    for d in S["details"]:
        if d["kind"] in ("boat", "shed", "wall", "wheelhouse", "quay steps", "stoop"):
            details.append(box_mesh(d["kind"], centred(d["X"], d["Y"], d["a"] + 90.0, d["l"], d["w"] + 0.1), d["z"],
                                    d["h"], below=0.4))
    steps, landings = face_stair("the Hundred Steps")
    for x, y, z in landings:
        details.append(box_mesh("bench", centred(x, y - 0.5, 0.0, 1.8, 0.5), z, 0.48, below=0.0))
    x, y, z = landings[1]
    people = person("on the landing", x + 1.6, y - 1.1, z)
    people += person("on the shelf", 84.0, 25.0, W.ground_at(84.0, 25.0))
    # the slab that came down, in blocks at the foot: rigid, angular, unworn
    rng = np.random.default_rng(5)
    falls = []
    sx, sz, hw, hh = SCAR
    for i in range(9):
        x = sx + rng.uniform(-hw, hw) * 0.9
        y = float(face_line(np.array([x]))[0]) - rng.uniform(1.0, 7.0)
        falls.append(block_rock(f"fallen{i}", x, y, W.ground_at(x, y), rng.uniform(0.8, 2.4), 100 + i))
    # what the sea and the frost lift off the beds and leave on the shelf: small slabs, lying flat
    loose = []
    for i in range(70):
        x = rng.uniform(-60.0, 150.0)
        sw = float(np.interp(x, *SHELF_W))
        if sw < 3.0:
            continue
        y = float(face_line(np.array([x]))[0]) - rng.uniform(0.8, sw - 0.5)
        loose.append(block_rock(f"loose{i}", x, y, W.ground_at(x, y), rng.uniform(0.25, 0.8), 200 + i))
    return dict(rock=rock, turf=turf, land=land, made=made, skerries=skerries, sea=sea, swell=swell, built=built,
                details=details, steps=steps, people=people, falls=falls, loose=loose,
                mountains=mountains(far_range()))


def block_rock(name, x, y, z, r, seed):
    """A block off the face: its joint faces flat and its edges sharp (a hull of the corners of a skewed box)."""
    import bmesh
    rng = np.random.default_rng(seed)
    a, b, c = r, r * rng.uniform(0.5, 0.9), r * rng.uniform(0.35, 0.6)
    pts = []
    for sx in (-1, 1):
        for sy in (-1, 1):
            for sz in (-1, 1):
                pts.append((sx * a * rng.uniform(0.7, 1.0), sy * b * rng.uniform(0.7, 1.0), sz * c * rng.uniform(0.7, 1.0)))
    bm = bmesh.new()
    vs = [bm.verts.new(p) for p in pts]
    bmesh.ops.convex_hull(bm, input=vs)
    bmesh.ops.bevel(bm, geom=list(bm.edges), offset=0.04, segments=1, affect="EDGES")
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    ob.location = (x, y, z + c * 0.6)
    ob.rotation_euler = tuple(rng.uniform(-0.5, 0.5, 2)) + (rng.uniform(0, 6.28),)
    return ob


def camera(cam):
    x, y, lx, ly, lz, lens = cam[:6]
    h = cam[6] if len(cam) > 6 else 1.6
    p = mathutils.Vector((x, y, h if len(cam) > 7 and cam[7] else max(W.ground_at(x, y), SEA) + h))
    cd = bpy.data.cameras.new("cam")
    cd.lens, cd.sensor_width = lens, 36.0
    cd.clip_end = 60000.0
    ob = bpy.data.objects.new("cam", cd)
    bpy.context.scene.collection.objects.link(ob)
    ob.location = p
    ob.rotation_euler = (mathutils.Vector((lx, ly, lz)) - p).to_track_quat("-Z", "Y").to_euler()
    bpy.context.scene.camera = ob
    print(f"camera at {tuple(round(v, 2) for v in p)}")


# -- colour: materials, the passes and the painter's finish ----------------------------------------------------------

CLASS = {"rock": 1, "sea": 2, "turf": 3, "built": 4, "made": 5, "far": 6, "mountains": 7, "steps": 8, "people": 9}
FOAM = (-280.0, 200.0, -200.0, 110.0, 0.5)  # the foam image's extent (x0, x1, y0, y1) and step (m)


def relink(m):
    """A material's node writer and its base colour's input, cut from what fed it (returned), to add to it."""
    nt = m.node_tree
    sock = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED").inputs["Base Color"]
    c = sock.links[0].from_socket
    nt.links.remove(sock.links[0])
    return T.G(nt), sock, c


def site_rock():
    """The floor's phyllite, with what this site adds: the scar fresh, paler and clean of lichen, and the open joints,
    the caves and the notch dark (Hertervig's cracks), by occlusion."""
    W.NFOL = NFOL
    m = W.rock_material()
    g, sock, c = relink(m)
    P, N, x, y, z, nz = T.geometry(g)
    sx, sz, hw, hh = SCAR
    scar = g.math("MULTIPLY", g.ss(g.math("ABSOLUTE", g.math("SUBTRACT", x, sx)), hw * 1.05, hw * 0.75),
                  g.ss(g.math("ABSOLUTE", g.math("SUBTRACT", z, sz)), hh * 1.05, hh * 0.75))
    c = g.mix(g.math("MULTIPLY", scar, g.ss(nz, 0.6, 0.3)), c, (0.15, 0.155, 0.14))
    # the stone's own grey: the floor's grey-green read khaki under this warm sun
    c = g.out(g.node("ShaderNodeHueSaturation", {"Color": c, "Saturation": 0.45}), "Color")
    # crustose lichen, pale, in patches with hard edges, on what faces the sky above the spray
    lich = g.math("MULTIPLY", g.ss(g.noise(P, 0.9, 3.0, 0.65), 0.6, 0.62),
                  g.math("MULTIPLY", g.ss(z, 4.0, 6.0), g.ss(nz, 0.45, 0.75)))
    c = g.mix(g.math("MULTIPLY", lich, 0.85), c, (0.30, 0.30, 0.29))
    # the shelf the tide covers twice a day: wet, dark, barnacled in a fine even speckle, not in patches
    tide = g.mix(g.ss(g.noise(P, 25.0, 2.0), 0.45, 0.6), (0.035, 0.035, 0.032), (0.085, 0.08, 0.07))
    c = g.mix(g.math("MULTIPLY", g.ss(z, 0.95, 0.6), g.ss(nz, 0.2, 0.5)), c, tide)
    # rain's dark run-off, in streaks down the steep faces from the ledges and joints
    run = g.noise(g.vec(g.math("MULTIPLY", x, 1.2), g.math("MULTIPLY", y, 1.2), g.math("MULTIPLY", z, 0.08)), 1.0, 3.0, 0.6)
    c = g.mix(g.math("MULTIPLY", g.ss(run, 0.56, 0.7), g.math("MULTIPLY", g.ss(nz, 0.5, 0.2), 0.55)), c, g.scale(c, 0.55))
    ao = g.node("ShaderNodeAmbientOcclusion", {"Distance": 0.9}, samples=12, only_local=True)
    c = g.mix(g.ss(g.out(ao, "AO"), 0.8, 0.4), c, (0.005, 0.005, 0.005))
    g.put(sock, c)
    return m


def house_material():
    """The clay's houses painted as the town paints them: most white, some ochre, a few red or grey-green; the roofs'
    tiles dark glazed or red."""
    m, g, bsdf = T.material("houses")
    P, N, x, y, z, nz = T.geometry(g)
    r = g.out(g.node("ShaderNodeObjectInfo"), "Random")
    c = g.mix(g.ss(r, 0.66, 0.67), (0.62, 0.60, 0.55), (0.46, 0.33, 0.14))
    c = g.mix(g.ss(r, 0.82, 0.83), c, (0.25, 0.06, 0.035))
    c = g.mix(g.ss(r, 0.93, 0.94), c, (0.24, 0.28, 0.24))
    tile = g.mix(g.ss(g.math("FRACT", g.math("MULTIPLY", r, 7.0)), 0.6, 0.62), (0.05, 0.05, 0.055), (0.17, 0.055, 0.03))
    g.put(bsdf.inputs["Base Color"], g.mix(g.ss(nz, 0.3, 0.45), c, tile))
    g.put(bsdf.inputs["Roughness"], 0.7)
    return m


def foam_image():
    """Foam where the swell meets rock at this tide: thick at the rock, a second band a few metres out."""
    x0, x1, y0, y1, h = FOAM
    X, Y = np.meshgrid(np.arange(x0, x1, h, dtype=np.float32), np.arange(y0, y1, h, dtype=np.float32), indexing="ij")
    rock, _ = land_sdf(X, Y, np.full_like(X, SEA + 0.15))
    W.H = h
    return W.foam_image(rock < 0)


def sea_material(foam):
    """The floor's sea, and the swell's break: white water on the crests the shelf steepens, torn along them."""
    W.LO, W.HI = (FOAM[0], FOAM[2]), (FOAM[1], FOAM[3])
    m = W.sea_material(foam)
    g, sock, c = relink(m)
    P, N, x, y, z, nz = T.geometry(g)
    torn = g.ss(g.noise(g.vec(g.math("MULTIPLY", x, 0.3), y, 0.0), 0.8, 3.0, 0.6), 0.35, 0.55)
    crest = g.math("MULTIPLY", g.ss(z, SEA + 0.42, SEA + 0.72), torn)
    g.put(sock, g.mix(crest, c, (0.62, 0.64, 0.62)))
    # a sea, not a lake: the evening breeze's chop over the swell, metres long, so far water breaks the reflections
    bsdf = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    nrm, rough = (bsdf.inputs[k].links[0].from_socket for k in ("Normal", "Roughness"))
    chop = g.noise(g.vec(g.math("MULTIPLY", x, 0.5), y, 0.0), 0.35, 4.0, 0.65)
    b2 = g.node("ShaderNodeBump", {"Strength": 0.6, "Distance": 0.25, "Height": chop, "Normal": nrm})
    g.put(bsdf.inputs["Normal"], g.out(b2, "Normal"))
    g.put(bsdf.inputs["Roughness"], g.math("ADD", rough, 0.08))
    return m


def colour(parts):
    """Each part its material and its class (the object index the finish reads)."""
    sm = sea_material(foam_image())
    rock, turf = site_rock(), W.turf_material()
    houses = house_material()
    mats = {"rock": rock, "skerries": rock, "turf": turf, "sea": sm, "swell": sm, "built": houses,
            "made": W.plain("made", (0.10, 0.095, 0.085), 0.85, 0.3, 0.4, (0.13, 0.12, 0.11)),
            "steps": W.plain("steps", (0.20, 0.19, 0.17), 0.8, 0.2, 2.0, (0.15, 0.145, 0.13)),
            "falls": W.plain("fresh", (0.15, 0.155, 0.14), 0.5, 0.3, 1.0, (0.12, 0.125, 0.115)),
            "mountains": W.plain("mountains", (0.07, 0.08, 0.09), 0.9)}
    mats["loose"] = rock
    cls = {"skerries": "rock", "falls": "rock", "loose": "rock", "swell": "sea", "details": "built"}
    wood = W.plain("wood", (0.07, 0.045, 0.025), 0.7)
    coats = [W.plain("coat", (0.30, 0.025, 0.02), 0.8), W.plain("coat2", (0.03, 0.04, 0.07), 0.8)]
    for k, v in parts.items():
        for o in (v if isinstance(v, list) else [v]):
            if o.type != "MESH":
                continue
            if k == "land":
                m, c = (turf, "turf") if o.name == "hill" else (W.fields_material(), "far")
            elif k == "people":
                m, c = coats[0 if o.name.startswith("on the landing") else 1], "people"
            elif k == "details":
                m, c = (wood if o.name.startswith("bench") else houses), "built"
            else:
                m, c = mats.get(k, houses), cls.get(k, k)
            o.data.materials.clear()
            o.data.materials.append(m)
            o.pass_index = CLASS.get(c, 4)


def sky():
    """A clear midsummer evening: the zenith and the sky away from the sun a deep clear blue (the shade's light, so the
    shade is cool), the horizon pale, warming toward the sun low in the north-west."""
    w = bpy.data.worlds.new("site-sky")
    bpy.context.scene.world = w
    w.use_nodes = True
    nt = w.node_tree
    nt.nodes.clear()
    g = T.G(nt)
    d = g.node("ShaderNodeVectorMath", operation="NORMALIZE")
    g.put(d.inputs[0], g.out(g.node("ShaderNodeTexCoord"), "Generated"))
    dv = d.outputs[0]
    az, el = math.radians(T.SUN["azimuth"]), math.radians(T.SUN["elevation"])
    dot = g.node("ShaderNodeVectorMath", operation="DOT_PRODUCT")
    g.put(dot.inputs[0], dv)
    dot.inputs[1].default_value = (math.sin(az) * math.cos(el), math.cos(az) * math.cos(el), math.sin(el))
    sz = g.out(g.node("ShaderNodeSeparateXYZ", {"Vector": dv}), "Z")
    toward = g.out(dot, "Value")
    hor = g.mix(g.ss(toward, -0.2, 0.95), (0.36, 0.45, 0.58), (0.98, 0.78, 0.55))
    c = g.mix(g.ss(sz, 0.0, 0.45), hor, (0.10, 0.20, 0.42))
    glow = g.math("POWER", g.math("MAXIMUM", toward, 0.0), 24.0)
    c = g.mix(g.math("MULTIPLY", glow, 0.6), c, (1.6, 1.15, 0.7))
    bg = g.node("ShaderNodeBackground", {"Color": c, "Strength": 1.0})
    g.L.new(bg.outputs[0], g.node("ShaderNodeOutputWorld").inputs["Surface"])


def overriding(path, m, world_strength, samples):
    """Render the frame with every surface one material, in a black world (or the sky's), raw, 16 bits."""
    sc = bpy.context.scene
    vl = sc.view_layers[0]
    keep = (sc.world, sc.cycles.samples, sc.cycles.use_denoising, sc.render.filter_size,
            sc.view_settings.view_transform, sc.view_settings.look, sc.render.image_settings.color_depth)
    vl.material_override = m
    if world_strength == 0.0:
        black = bpy.data.worlds.get("black") or bpy.data.worlds.new("black")
        black.use_nodes = True
        black.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.0
        sc.world = black
    sc.cycles.samples, sc.cycles.use_denoising = samples, False
    sc.render.filter_size = 0.01 if samples == 1 else 1.0
    sc.view_settings.view_transform, sc.view_settings.look = "Raw", "None"
    sc.render.image_settings.color_depth = "16"
    sc.render.filepath = path
    bpy.ops.render.render(write_still=True)
    vl.material_override = None
    (sc.world, sc.cycles.samples, sc.cycles.use_denoising, sc.render.filter_size,
     sc.view_settings.view_transform, sc.view_settings.look, sc.render.image_settings.color_depth) = keep


def passes(out, tag):
    """The finish's facts: the sun alone on white clay (which planes it lights, and the shadows), and per pixel the
    distance (/4 km) and the class."""
    m, g, bsdf = T.material("sun-pass")
    nt = m.node_tree
    nt.nodes.remove(bsdf)
    d = g.node("ShaderNodeBsdfDiffuse", {"Color": (1.0, 1.0, 1.0)})
    g.L.new(d.outputs[0], next(n for n in nt.nodes if n.type == "OUTPUT_MATERIAL").inputs["Surface"])
    lamp = bpy.data.lights["sun"]
    e = lamp.energy, tuple(lamp.color)
    lamp.energy, lamp.color = math.pi, (1.0, 1.0, 1.0)  # a plane square to the sun reads 1
    overriding(os.path.join(out, f"{tag}-sun.png"), m, 0.0, 16)
    lamp.energy, lamp.color = e
    m, g, bsdf = T.material("geo-pass")
    nt = m.node_tree
    nt.nodes.remove(bsdf)
    cam = g.node("ShaderNodeCameraData")
    oi = g.node("ShaderNodeObjectInfo")
    col = g.node("ShaderNodeCombineColor", {"Red": g.math("DIVIDE", g.out(cam, "View Distance"), 4000.0),
                                             "Green": 0.0, "Blue": g.math("DIVIDE", g.out(oi, "Object Index"), 16.0)})
    em = g.node("ShaderNodeEmission", {"Color": g.out(col, "Color"), "Strength": 1.0})
    g.L.new(em.outputs[0], next(n for n in nt.nodes if n.type == "OUTPUT_MATERIAL").inputs["Surface"])
    overriding(os.path.join(out, f"{tag}-geo.png"), m, 0.0, 1)


KEEP = {0: 0.7, 1: 0.6, 2: 0.6, 3: 0.55, 4: 0.8, 5: 0.6, 6: 0.6, 7: 0.6, 8: 0.7, 9: 1.0}  # class: how much of the
# render's variation inside each of its value shapes (lit, shade) the finish keeps; the shapes' own values are the
# material's under the light, never set by the finish


def lic(a, tx, ty, n, same):
    """Each pixel the mean along its stroke's direction over +-n pixels, stopping where `same` says the shape ends."""
    h, w = same.shape
    yy, xx = np.mgrid[0:h, 0:w]
    acc = a.copy()
    cnt = np.ones((h, w), np.float32)
    for s in range(1, n + 1):
        for sg in (-1, 1):
            py = np.clip(np.rint(yy + sg * s * ty).astype(np.int32), 0, h - 1)
            px = np.clip(np.rint(xx + sg * s * tx).astype(np.int32), 0, w - 1)
            ok = (same[py, px] == same).astype(np.float32)
            acc += a[py, px] * (ok[..., None] if a.ndim == 3 else ok)
            cnt += ok
    return acc / (cnt[..., None] if a.ndim == 3 else cnt)


def paint(out, tag):
    """The painter's finish by value shapes: each class's lit planes and its shade each drawn toward their own value
    (the material's, under this light), only part of the render's variation left inside each, the darks held dark; the air by distance toward the
    horizon's own colour; then, from a hundred metres out, flat strokes drawn along the forms (level on sky and sea),
    never across a class's or the sun's edge; near, the planes as they are; the cracks drawn back in on top."""
    img = W.pixels(os.path.join(out, f"{tag}-render.png"))
    geo = W.pixels(os.path.join(out, f"{tag}-geo.png"))
    sun = W.pixels(os.path.join(out, f"{tag}-sun.png"))[..., 0]
    h, w = sun.shape
    d = geo[..., 0] * 4000.0
    sky = d <= 0.0
    cls = np.where(sky, 0, np.rint(geo[..., 2] * 16.0)).astype(np.int32)
    lit = ss(0.05, 0.18, sun)
    lum = img @ np.array([0.2126, 0.7152, 0.0722], np.float32)
    v = lum.copy()
    for c, k in KEEP.items():
        sel = cls == c
        if sel.sum() < 50:
            continue
        Y, L = lum[sel], lit[sel]
        ml = np.median(Y[L > 0.5]) if (L > 0.5).sum() > 50 else np.median(Y)
        ms = np.median(Y[L <= 0.5]) if (L <= 0.5).sum() > 50 else np.median(Y)
        a, b = ml + k * (Y - ml), ms + k * (Y - ms)
        v[sel] = b + (a - b) * L
        if c == 2:  # the break: white water stays white
            v[sel] = v[sel] + (0.86 - v[sel]) * ss(ms + 0.15, ms + 0.35, Y)
    ground = (cls == 1) | (cls == 3) | (cls == 5)
    near = box(lum, max(2, w // 400))
    crack = ground * np.maximum(ss(0.55, 0.3, lum / np.maximum(near, 1e-3)), ss(0.05, 0.015, lum))
    v = v + (0.05 - v) * crack
    ratio = np.clip(v / np.maximum(lum, 0.015), 0.0, 6.0)
    col = img * ratio[..., None]
    col = col + (v[..., None] - col) * ss(0.03, 0.0, lum)[..., None]  # what was black has no hue to keep
    warm = (lit * ~sky * (cls != 2))[..., None]
    col = col * (1 + warm * np.array([0.05, 0.0, -0.07], np.float32)) * (
        1 + (1 - warm) * (~sky)[..., None] * np.array([-0.04, 0.0, 0.05], np.float32))
    # the air: toward the horizon's colour in each column, from a few hundred metres out
    hz = np.zeros((w, 3), np.float32)
    has = np.zeros(w, bool)
    for x in range(w):
        rows = np.nonzero(sky[:, x])[0]
        if len(rows):
            hz[x] = img[max(rows.max() - 6, 0):rows.max() + 1, x].mean(0)
            has[x] = True
    if has.any():
        for ch in range(3):
            hz[:, ch] = np.interp(np.arange(w), np.nonzero(has)[0], hz[has, ch])
        hz = box(hz[None], max(4, w // 80))[0]
    air = (1 - np.exp(-np.maximum(d - 220.0, 0) / 1400.0)) * ~sky * 0.85
    col = col + (hz[None, :, :] - col) * air[..., None]
    col = np.clip(col, 0, 1)
    # strokes: flat, along the forms, finer near than far
    s = w / 1600.0
    k1, k2, k3 = (W.kuwahara(col, max(1, int(r * s))) for r in (1, 2, 4))
    t1, t2 = ss(50.0, 140.0, d)[..., None], ss(350.0, 1500.0, d + sky * 4000.0)[..., None]
    pt = k1 * (1 - t1) + k2 * t1
    pt = pt * (1 - t2) + k3 * t2
    L = pt @ np.array([0.2126, 0.7152, 0.0722], np.float32)
    gy, gx = np.gradient(box(L, 1))
    jxx, jyy, jxy = (box(a, max(3, int(4 * s))) for a in (gx * gx, gy * gy, gx * gy))
    th = 0.5 * np.arctan2(2 * jxy, jxx - jyy) + np.pi / 2  # along the edge, not across it
    level = (cls == 0) | (cls == 2)
    tx, ty = np.where(level, 1.0, np.cos(th)), np.where(level, 0.0, np.sin(th))
    same = cls * 2 + (lit > 0.5)
    n = max(2, int(4 * s))
    pt = lic(pt, tx, ty, n, same)
    grain = lic(np.random.default_rng(1989).standard_normal((h, w)).astype(np.float32), tx, ty, 2 * n, same)
    grain = grain / max(float(grain.std()), 1e-3)
    pt = pt + (grain * np.where(sky, 0.008, 0.016))[..., None]
    true = ((1 - ss(100.0, 300.0, d)) * ~sky)[..., None]  # true up close: the strokes only where the eye can't read the planes
    pt = pt + (col - pt) * true
    pt = pt * (1 - 0.8 * crack * (d < 400.0))[..., None] + 0.05 * 0.8 * (crack * (d < 400.0))[..., None]
    yy, xx = np.mgrid[0:h, 0:w]
    r = np.hypot((xx - w * 0.5) / w, (yy - h * 0.45) / h)
    pt = pt * (1 - 0.18 * ss(0.4, 0.8, r))[..., None]
    canvas = box(np.random.default_rng(7).random((h, w)).astype(np.float32), 1)
    pt = np.clip(pt + (canvas[..., None] - 0.5) * 0.03, 0, 1)
    o = bpy.data.images.new(f"{tag}-painted", w, h, alpha=False)
    o.colorspace_settings.name = "Non-Color"
    px = np.ones((h, w, 4), np.float32)
    px[..., :3] = pt[::-1]
    o.pixels = px.ravel()
    o.filepath_raw = os.path.join(out, f"{tag}-target.png")
    o.file_format = "PNG"
    o.save()
    print("wrote", o.filepath_raw)


def main():
    if BL.arg("--site"):
        site_snapshot()
        return
    out = BL.arg("--out")
    os.makedirs(out, exist_ok=True)
    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o)
    t0 = time.time()
    grey = bool(BL.arg("--grey"))
    vox = float(BL.arg("--vox", 0.3))
    parts = build(out, grey, vox)
    if grey:
        clay = BL.material("clay", (0.20, 0.20, 0.20), 0.8)
        house = BL.material("house", (0.30, 0.30, 0.30), 0.8)
        water = BL.material("sea", (0.02, 0.025, 0.03), 0.12)
        for k, v in parts.items():
            for o in (v if isinstance(v, list) else [v]):
                if o.type != "MESH":
                    continue
                m = water if k in ("sea", "swell") else house if k in ("built", "details", "steps", "people") else clay
                o.data.materials.clear()
                o.data.materials.append(m)
    else:
        colour(parts)
    W.rig()
    sky()
    names = BL.arg("--cam").split("+") if BL.arg("--cam") else ["main"]
    if names[0] == "all":
        names = list(CAMS)
    T.cycles(int(BL.arg("--w", 1600)), int(BL.arg("--h", 900)), int(BL.arg("--samples", 96)))
    for name in names:
        cam = CAMS[name] if name in CAMS else tuple(float(v) for v in name.split(","))
        for o in [o for o in bpy.data.objects if o.type == "CAMERA"]:
            bpy.data.objects.remove(o)
        camera(cam)
        tag = name if name in CAMS else "cam"
        sc = bpy.context.scene
        sc.render.filepath = os.path.join(out, f"grey-{tag}.png" if grey else f"{tag}-render.png")
        bpy.ops.render.render(write_still=True)
        print("wrote", sc.render.filepath, f"{time.time() - t0:.0f}s")
        if not grey:
            passes(out, tag)
            paint(out, tag)
            print(f"painted {tag} {time.time() - t0:.0f}s")
    print(f"done {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
