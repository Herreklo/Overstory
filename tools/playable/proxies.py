"""The walk's collision proxies (LT1g, the walk, W4; docs/research/collision-and-navigation.md, item 4), written as data
for the player's walker to build its colliders from.

    /Applications/Blender.app/Contents/MacOS/Blender -b --factory-startup --python tools/playable/proxies.py -- [OUT.json]

`heart_layout` needs numpy, which only Blender's Python has here, so this runs in Blender's Python (no bpy, no scene;
nothing is written but OUT.json, by default unity/Assets/Experiments/LT1/Playable/proxies.json).

The proxies follow the clay as it is drawn: the heart's layout is read at the commit that last exported the clay
(`unity/Assets/Art/Blockout/heart/ground_heart.fbx`), not the working tree, so a box never stands where the clay drew
nothing (a later layout is a new export, then a new run of this). The gully's stair is read from its sidecars.

What it writes, in street metres (x along the Row, y up the hill, z up), every proxy with an id that names its record:
- houses: a body box per building (plinth from the lowest ground to the eave), walkable by nothing; a roof box over
  it (the eave to the ridge, the chimney included), for the camera only. A to E carry their record ids (bld/104 ...).
- walls: the retaining walls the ground needs (`ground_walls`, on heart_build's own 1.5 m ground) and the yards' walls,
  except where the gully's stair replaced the clay's walls (LT1Stone.CutClayWalls); the gully's cheek walls from
  stone_gully_cheeks.json.
- blockers: sheds, bollards, lamps, wells, benches, stalls, the fountain and the crane; boats, lines, quay steps and
  pontoons stand in the water and are left out.
- stoops: walkable, as nested steps of at most 0.2 m.
- the gully's flights: one ramp per run through its nosings (a least-squares line, within 1.5 cm of every nosing),
  and flat tops for each run's last tread with its landing, the turn and the top tread (bridging the ground the
  stair's staging sank under them).
- doors (their stand point 0.4 m out from the front, as heart_layout's _door) and ways (every lane, stair and door
  path), for LT1Play.CheckProxies and the scripted walks.
The clay ground itself is not here: the player cuts the drawn ground into 64 m mesh colliders (WalkWorld).
"""

import hashlib
import importlib.util
import json
import math
import os
import re
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
BLOCKOUTS = os.path.join(ROOT, "blender", "blockouts")
CLAY = "unity/Assets/Art/Blockout/heart/ground_heart.fbx"
STAIR = "unity/Assets/Art/Stone/stone_gully.json"
CHEEKS = "unity/Assets/Art/Stone/stone_gully_cheeks.json"
MANIFEST = "unity/Assets/Art/Buildings/playable/manifest.json"
SINK_REACH = 0.3 + 1.6     # past a flight's top, how far the staging's sunk ground reaches (LT1Stone.SinkGround)
OUT = os.path.join(ROOT, "unity", "Assets", "Experiments", "LT1", "Playable", "proxies.json")
CORNER = (-60.0, -40.0, 140.0, 130.0)   # the corner's box (tools/playable/layout_dump.py), where CheckProxies is strict
STEP = 1.5                              # heart_build's ground grid in the heart
RAMP_THICK = 0.3
OVERHANG = 0.45                         # heart_build._massing's eaves
STOOP_STEP = 0.2

IN_WATER = {"boat", "tall ship", "line", "quay steps", "pontoon", "wheelhouse", "mast"}

sys.path.insert(0, BLOCKOUTS)


def git(*args):
    return subprocess.check_output(["git", "-C", ROOT, *args]).decode()


def blob_hash(data):
    return hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()


def load_layout(rev):
    """heart_layout as it was at rev, imported under its own name (centre_land is the working tree's: it has not
    changed since the clay's export, which main() checks)."""
    src = subprocess.check_output(["git", "-C", ROOT, "show", f"{rev}:blender/blockouts/heart_layout.py"])
    tmp = tempfile.mkdtemp(prefix="proxies-layout-")
    path = os.path.join(tmp, "heart_layout.py")
    with open(path, "wb") as f:
        f.write(src)
    spec = importlib.util.spec_from_file_location("heart_layout", path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["heart_layout"] = mod
    spec.loader.exec_module(mod)
    return mod, blob_hash(src)


def r(v, n=3):
    return round(float(v), n)


def box(id_, kind, layer, x, y, a, l, w, z0, z1, **extra):
    d = dict(id=id_, kind=kind, layer=layer, x=r(x), y=r(y), a=r(a, 4), l=r(l), w=r(w), z0=r(z0), z1=r(z1))
    d.update(extra)
    return d


def local(b, u, v):
    c, s = math.cos(math.radians(b["angle"])), math.sin(math.radians(b["angle"]))
    return b["ox"] + u * c - v * s, b["oy"] + u * s + v * c


def in_box(x, y, bx, pad=0.0):
    return bx[0] - pad <= x <= bx[2] + pad and bx[1] - pad <= y <= bx[3] + pad


def slug(name):
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def at(x, y):
    return f"{x:.2f}_{y:.2f}"


def main(out):
    import numpy as np
    import centre_land as L

    clay_rev = git("log", "-1", "--format=%H", "--", CLAY).strip()
    if git("diff", "--name-only", clay_rev, "HEAD", "--", "blender/blockouts/centre_land.py").strip():
        raise SystemExit("[proxies] centre_land changed since the clay's export: re-export the clay first")
    H, layout_blob = load_layout(clay_rev)
    HX0, HY0, HX1, HY1 = H.HEART

    # the ground as heart_build carves it (heart_build.build: grid, carve, _sample)
    xs = np.arange(HX0, HX1 + STEP / 2, STEP)
    ys = np.arange(HY0, HY1 + STEP / 2, STEP)
    X, Y = np.meshgrid(xs, ys, indexing="ij")
    Z = H.carve(X, Y, L.heights(X, Y))

    def sample(x, y):
        u = min(max((x - X[0, 0]) / STEP, 0), X.shape[0] - 1.001)
        v = min(max((y - Y[0, 0]) / STEP, 0), X.shape[1] - 1.001)
        i, j = int(u), int(v)
        fu, fv = u - i, v - j
        a = Z[i, j] + (Z[i + 1, j] - Z[i, j]) * fu
        b = Z[i, j + 1] + (Z[i + 1, j + 1] - Z[i, j + 1]) * fu
        return float(a + (b - a) * fv)

    def ground(x, y):
        if HX0 <= x <= HX1 and HY0 <= y <= HY1:
            return sample(x, y)
        return float(L.heights(np.array([x]), np.array([y]))[0])

    stair = json.load(open(os.path.join(ROOT, STAIR)))
    cheeks = json.load(open(os.path.join(ROOT, CHEEKS)))
    O = stair["origin"]
    flights = stair["flights"]

    def stair_region(x, y):
        """Where LT1Stone.CutClayWalls removed the clay's walls: along each flight, |t| < W/2 + 1.4."""
        for f in flights:
            a, b = f["a"], f["b"]
            dx, dy = b[0] - a[0], b[1] - a[1]
            run = math.hypot(dx, dy)
            ux, uy = dx / run, dy / run
            px, py = x - a[0], y - a[1]
            s, t = px * ux + py * uy, abs(px * uy - py * ux)
            if -0.5 < s < run + 0.5 and t < f["width"] / 2 + 1.4:
                return True
        return False

    proxies, doors = [], []
    seen = {}

    def unique(id_):
        k = seen.get(id_, 0)
        seen[id_] = k + 1
        return id_ if k == 0 else f"{id_}#{k + 1}"

    # -- houses
    for b in H.BUILDINGS:
        fp = H.footprint(b)
        if not any(in_box(x, y, H.HEART) for x, y in fp):
            continue
        W, D = b["w"], b["d"]
        m = re.match(r"^([A-E]) \((\d+)", b["name"])
        rec = f"bld/{m.group(2)}" if m and b["role"] == "corner" else unique(f"heart/bld/{slug(b['name'])}")
        low = min(ground(*local(b, u, v)) for u in (0, W / 2, W) for v in (0, D / 2, D))
        ze = b["base"] + b["eave"]
        cx, cy = local(b, W / 2, D / 2)
        proxies.append(box(rec, "house", "walk", cx, cy, b["angle"], W, D, min(low, b["base"]) - 0.4, ze,
                           name=b["name"]))
        roof = b["roof"]
        if roof == "flat":
            top, grow = ze + 0.5, 0.15
        elif roof == "tower":
            top, grow = ze + 0.6 + (b["eave"] * 1.1 if b["name"].startswith("the cathedral") else min(W, D) * 0.45), 0.3
        elif roof == "hip":
            top, grow = ze + math.tan(math.radians(b["pitch"])) * min(W, D) / 2, OVERHANG
        else:
            span = D if roof in ("eaves", "mansard") else W
            top, grow = ze + math.tan(math.radians(b["pitch"])) * (span / 2 + OVERHANG), OVERHANG
            if b["role"] in ("row", "corner", "warehouse") and b["name"] != "the Fish Hall":
                top += 1.1  # the chimney
        proxies.append(box(f"{rec}/roof", "roof", "camera", cx, cy, b["angle"], W + 2 * grow, D + 2 * grow, ze, top))
        dx, dy = H._door(b)
        doors.append(dict(id=f"{rec}/door", name=b["name"], x=r(dx), y=r(dy), z=r(b["base"]),
                          corner=in_box(dx, dy, CORNER), a=r(b["angle"], 4)))

    # -- walls the ground needs, and the yards'
    for w in H.ground_walls(ground):
        if not in_box(w["x"], w["y"], H.HEART) or stair_region(w["x"], w["y"]):
            continue
        proxies.append(box(unique(f"heart/wall/{at(w['x'], w['y'])}"), "wall", "walk", w["x"], w["y"], w["a"], w["l"], w["w"],
                           w["z0"], w["z1"]))

    # -- the small masses
    for d in H.DETAILS:
        k = d["kind"]
        if k in IN_WATER or not in_box(d["x"], d["y"], H.HEART):
            continue
        if k == "stoop":
            # nested steps up to the door: the house stands on the stoop's +v side (heart_layout: a stoop at local
            # (w/2, -0.8), 1.4 deep, its angle the house's)
            n = max(1, math.ceil(d["h"] / STOOP_STEP - 1e-6))
            nx, ny = -math.sin(math.radians(d["a"])), math.cos(math.radians(d["a"]))
            sid = f"heart/stoop/{at(d['x'], d['y'])}"
            for i in range(n):
                depth = d["w"] * (1 - i / n)
                off = (d["w"] - depth) / 2
                proxies.append(box(unique(f"{sid}/{i}"), "stoop", "walk", d["x"] + nx * off, d["y"] + ny * off, d["a"],
                                   d["l"], depth, d["z"] - 0.3, d["z"] + d["h"] * (i + 1) / n))
            continue
        if stair_region(d["x"], d["y"]) and k == "wall":
            continue
        kind = "wall" if k == "wall" else "blocker"
        proxies.append(box(unique(f"heart/{slug(k)}/{at(d['x'], d['y'])}"), kind, "walk", d["x"], d["y"], d["a"],
                           max(d["l"], 0.2), max(d["w"], 0.2), d["z"] - 0.2, d["z"] + d["h"], name=k))

    # -- the gully's flights: ramps over the nosings, flat tops for landings, the turn and the top
    aff = {a["id"]: a for a in stair["affordances"]}

    def absq(q):
        return [(p[0] + O[0], p[1] + O[1], p[2] + O[2]) for p in q]

    ramps_dev = []
    for fi, f in enumerate(flights):
        a, b = f["a"], f["b"]
        dx, dy = b[0] - a[0], b[1] - a[1]
        run = math.hypot(dx, dy)
        ux, uy = dx / run, dy / run
        ang = math.degrees(math.atan2(uy, ux))
        W = f["width"]
        fid = f"st-gully/fl-{fi}"
        s_of = lambda x, y: (x - a[0]) * ux + (y - a[1]) * uy
        pt = lambda s, z: (a[0] + ux * s, a[1] + uy * s, z)
        treads = sorted((t for t in stair["affordances"] if t["name"] == "tread" and t["id"].startswith(fid + "/")),
                        key=lambda t: int(t["id"].split("tr-")[1]))
        runs, cur = [], []
        for t in treads:
            cur.append(t)
            if t["id"] + "/ld" in aff:
                runs.append(cur)
                cur = []
        if cur:
            runs.append(cur)

        def flat(id_, s0, s1, z, tag):
            proxies.append(box(id_, "landing", "walk", *pt((s0 + s1) / 2, 0)[:2], ang, s1 - s0, W, z - RAMP_THICK, z,
                               flight=fid, tag=tag))

        turn = aff.get(f"{fid}/turn")
        base = a[2]
        if turn:
            q = absq(turn["quad"])
            ss = [s_of(p[0], p[1]) for p in q]
            flat(turn["id"], min(ss) - 0.3, max(ss), q[0][2], "turn")
        for k, rr in enumerate(runs):
            N = []
            for t in rr:
                q = absq(t["quad"])
                N.append((s_of((q[0][0] + q[1][0]) / 2, (q[0][1] + q[1][1]) / 2), q[0][2]))
            n = len(N)
            ms = sum(s for s, _ in N) / n
            mz = sum(z for _, z in N) / n
            m = sum((s - ms) * (z - mz) for s, z in N) / sum((s - ms) ** 2 for s, _ in N)
            z0 = mz - m * ms
            ramps_dev.append(max(abs(z0 + m * s - z) for s, z in N))
            s_lo, s_hi = (base - z0) / m, N[-1][0]
            p0, p1 = pt(s_lo, base), pt(s_hi, z0 + m * s_hi)
            proxies.append(dict(id=f"{fid}/run-{k}", kind="ramp", layer="walk", flight=fid,
                                p0=[r(v) for v in p0], p1=[r(v) for v in p1], w=r(W), t=RAMP_THICK, rise=r(f["rise"]),
                                steps=n))
            last = rr[-1]
            ld = aff.get(last["id"] + "/ld")
            top = absq(last["quad"])[0][2]
            if ld:
                q = absq(ld["quad"])
                flat(ld["id"], s_hi, max(s_of(p[0], p[1]) for p in q), top, "landing")
            else:
                # over the hollow the stair's staging sinks past the top (LT1Stone.SinkGround: vertices to run + 0.3 go
                # under the steps 1.6 m back, and the 1.5 m grid's triangles carry the dip about 1.6 m further), so the
                # walk meets the top tread level, not a 0.4 m riser
                flat(last["id"] + "/top", s_hi, run + SINK_REACH, top, "top")
            base = top

        # the cheek walls: a box per stretch between the sidecar's stations, from the flight's edge 0.5 m out
        for line in (ln for ln in cheeks["lines"] if ln["flight"] == fi):
            side = line["side"]
            lux, luy = line["up"]
            rx, ry = luy, -lux                 # right of the way up
            la = line["a"]
            S, T = line["s"], line["top"]
            tag = "r" if side > 0 else "l"
            for j in range(len(S) - 1):
                s0, s1 = S[j], S[j + 1]
                if s1 - s0 < 0.01:
                    continue
                sm = (s0 + s1) / 2
                t = side * (W / 2 + 0.25)
                cx = la[0] + lux * sm + rx * t
                cy = la[1] + luy * sm + ry * t
                zs = a[2] + (b[2] - a[2]) * max(0.0, min(1.0, s0 / run))
                proxies.append(box(f"wl-gully/fl-{fi}/{tag}/seg-{j}", "cheek", "walk", cx, cy,
                                   math.degrees(math.atan2(luy, lux)), s1 - s0 + 0.02, 0.5, zs - 1.5, max(T[j], T[j + 1])))

    proxies.sort(key=lambda p: p["id"])
    ids = [p["id"] for p in proxies]
    if len(set(ids)) != len(ids):
        raise SystemExit("[proxies] duplicate ids")

    ways = []
    for lane in H.LANES:
        pts = [(r(p[0]), r(p[1]), r(p[2])) for p in lane["pts"]]
        if not any(in_box(p[0], p[1], H.HEART) for p in pts):
            continue
        # (points flat, x y z x y z ..., as Unity's JsonUtility reads no nested arrays)
        ways.append(dict(name=lane["name"], kind=lane["kind"], width=r(lane["width"]), door=bool(lane.get("door", False)),
                         pts=[v for p in pts for v in p]))
    breaks = [dict(flight=b_["flight"], pts=[r(p[k] + O[k]) for p in b_["pts"] for k in range(3)])
              for b_ in stair["breaklines"]["walking"]]

    src = dict(clay=clay_rev, heart_layout=layout_blob,
               centre_land=blob_hash(open(os.path.join(BLOCKOUTS, "centre_land.py"), "rb").read()),
               stair=blob_hash(open(os.path.join(ROOT, STAIR), "rb").read()),
               cheeks=blob_hash(open(os.path.join(ROOT, CHEEKS), "rb").read()),
               seed=H.SEED)
    data = dict(source=src, heart=list(H.HEART), corner=list(CORNER), sea=H.SEA,
                proxies=proxies, doors=sorted(doors, key=lambda d: d["id"]), ways=ways, walking=breaks)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w") as f:
        json.dump(data, f, separators=(",", ":"), default=plain)
        f.write("\n")
    kinds = {}
    for p in proxies:
        kinds[p["kind"]] = kinds.get(p["kind"], 0) + 1
    print(f"[proxies] clay {clay_rev[:7]}, heart_layout blob {layout_blob[:8]}: {len(proxies)} proxies {kinds}, "
          f"{len(doors)} doors, {len(ways)} ways; ramps within {max(ramps_dev) * 100:.2f} cm of their nosings -> {out}")


def plain(o):
    """numpy's scalars (heart_layout computes with numpy) as JSON's own."""
    if hasattr(o, "item"):
        return o.item()
    raise TypeError(f"{type(o).__name__} is not JSON")


if __name__ == "__main__":
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []     # (Blender's own arguments come before --)
    main(os.path.abspath(argv[0]) if argv else OUT)
