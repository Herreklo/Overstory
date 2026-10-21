"""The scale test's district (docs/research/scale-test.md; docs/plan.md, the building blocks, the scale test): a
district several square kilometres across, a grid of streets lined with houses from the test-quality house generator
(random diaries as the stress test draws them, resolved in 1989), on a clay ground, written as the chunk cache a player
streams: one binary file per 64 m chunk holding its houses merged at full detail (L0), each house's shell (its box and
roof, from its own mesh: the stand-in for the far levels the architecture will make) and the ground.

    blender -b --factory-startup --python blender/tools/scale_district.py -- <out dir> [--size 2048] [--core 512]
        [--part 0/1] [--bake 0|1|<every n-th>] [--limit <houses>] [--box i0,j0,i1,j1]

The layout is drawn first, in plain Python and the same in every process: streets every 52 m in the dense middle of
the district and every 76 m round it, cross streets every 160 m, houses along both sides of each street with their
long side to it, each plot as wide as its diary says. Only houses whose plots lie in the core (a square of --core
metres at the district's centre) are written at L0; every house is built and gets a shell. --part i/n builds every
n-th chunk from i, so n Blender processes can share the work. --bake 1 bakes what each face sees (bake.py) for every
L0 house, --bake n for every n-th (the rest take an even bake: the bake changes the light, not the cost). --box builds
only the chunks with indices in that box (a sample).

Writes <out>/chunks/c_<i>_<j>.bin, <out>/records/c_<i>_<j>.json (the houses' diaries: the record the cache is made
from) and <out>/parts/part_<i>.json (per chunk its houses, triangles and bytes, and the seconds each stage took).

The chunk file (little-endian): 'OSCK', version 1, the chunk's origin (x, y, z in Unity metres), the number of
meshes, and per mesh: its vertex and index counts, the index size (2 or 4 bytes), its bounds (min and max, chunk-local
Unity metres), the vertices and the indices. A vertex is 24 bytes, in Unity's attribute order: position (float32 x3),
normal (snorm8 x4), colour (unorm8 x4: the bake's sky, ground, openness), UV0 (float16 x2: the palette).
The meshes are, in order: L0 (the core's houses merged), the shells, the ground.
"""

import json
import math
import os
import struct
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [HERE, os.path.join(HERE, "..", "generators"), os.path.join(HERE, "..", "resolver")]

import bpy  # noqa: E402
import numpy as np  # noqa: E402

import bake  # noqa: E402
import building  # noqa: E402
import palette  # noqa: E402
from eras import DEFAULT_STYLE  # noqa: E402
from hashing import h, between  # noqa: E402
from resolve import resolve  # noqa: E402
from stress import random_diary  # noqa: E402

CHUNK = 64.0           # metres: the streaming chunk (docs/building-blocks.md, Units)
STREET = 8.0           # street width, kerb to kerb
SETBACK = 1.5          # from the kerb to the front of the house
CROSS_EVERY = 160.0    # metres between cross streets
DENSE = 600.0          # half the side of the dense middle
SPACING = (52.0, 76.0) # metres between streets: dense, open
GAPS = ((1.0, 3.0), (5.0, 12.0))  # metres between neighbouring houses: dense, open
GROUND_STEP = 2.0      # the ground's grid
GROUND_LINE = 1.0      # what stands below this height keeps behind the building line (export_street.py)
SEED = 1989
VERTEX = np.dtype([("p", "<f4", 3), ("n", "i1", 4), ("c", "u1", 4), ("uv", "<f2", 2)])
assert VERTEX.itemsize == 24


def ground_z(x, y):
    """The clay ground's height (street metres): rising gently from the harbour at y = 0, with long swells."""
    return 0.018 * y + 3.5 * math.sin(x / 310.0) * math.sin(y / 270.0) + 1.5 * math.sin((x + 2 * y) / 140.0)


def layout(size):
    """Every plot in the district: (index, x of the frontage's middle, y of the kerb, side, frontage, zone).
    The same for every process. Side +1 lies north of its street and faces south onto it; -1 lies south."""
    plots, n = [], 0
    c = size / 2.0
    y, row = 30.0, 0
    while y < size - 30.0:
        dense = abs(y - c) < DENSE
        for side in (+1, -1):
            x = 6.0
            k = 0
            while x < size - 18.0:
                i = n
                d = random_diary(i)
                w = d["plot"]["w"] / 1000.0
                z = 0 if abs(y - c) < DENSE and abs(x - c) < DENSE else 1
                gap = GAPS[z][0] + (GAPS[z][1] - GAPS[z][0]) * (h(SEED, "gap", row, side, k) % 1000) / 1000.0
                # a cross street every CROSS_EVERY metres: plots stop short of it and start beyond it
                cx = round((x + w / 2) / CROSS_EVERY) * CROSS_EVERY
                if cx > 0 and x < cx + STREET / 2 + SETBACK and x + w > cx - STREET / 2 - SETBACK:
                    x = cx + STREET / 2 + SETBACK
                    continue
                plots.append(dict(i=i, x=x + w / 2, kerb=y + side * STREET / 2, side=side, w=w, zone=z, row=row))
                n += 1
                k += 1
                x += w + gap
        y += SPACING[0] if dense else SPACING[1]
        row += 1
    return plots


def chunk_of(p, size):
    front = p["kerb"] + p["side"] * SETBACK
    return int(p["x"] // CHUNK), int(front // CHUNK)


def to_unity(a):
    """Street axes (x along, y back, z up) to Unity's (x, y up, z): a swap, so a mirror (windings turn over)."""
    return a[..., [0, 2, 1]]


def house_arrays(ob):
    """The house's mesh as loops: positions, normals (flat, the face's), palette UV, bake colour, and triangles."""
    me = ob.data
    me.calc_loop_triangles()
    nv, nl, npoly, nt = len(me.vertices), len(me.loops), len(me.polygons), len(me.loop_triangles)
    co = np.empty(nv * 3, np.float32)
    me.vertices.foreach_get("co", co)
    co = co.reshape(-1, 3)
    vi = np.empty(nl, np.int32)
    me.loops.foreach_get("vertex_index", vi)
    lt = np.empty(npoly, np.int32)
    me.polygons.foreach_get("loop_total", lt)
    pn = np.empty(npoly * 3, np.float32)
    me.polygons.foreach_get("normal", pn)
    pn = pn.reshape(-1, 3)
    uv = np.empty(nl * 2, np.float32)
    me.uv_layers[0].data.foreach_get("uv", uv)
    uv = uv.reshape(-1, 2)
    attr = me.color_attributes.get("bake")
    if attr is not None:
        col = np.empty(nv * 4, np.float32)
        attr.data.foreach_get("color", col)
        col = col.reshape(-1, 4)[vi]
    else:
        col = np.tile(np.array([0.6, 0.2, 1.0, 1.0], np.float32), (nl, 1))
    tri = np.empty(nt * 3, np.int32)
    me.loop_triangles.foreach_get("loops", tri)
    return dict(p=co[vi], n=np.repeat(pn, lt, axis=0), uv=uv, c=col, t=tri.reshape(-1, 3))


def place(a, yaw_deg, t):
    """The house's arrays turned about z and moved to t (street metres)."""
    c, s = math.cos(math.radians(yaw_deg)), math.sin(math.radians(yaw_deg))
    R = np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]], np.float32)
    return dict(a, p=a["p"] @ R.T + np.asarray(t, np.float32), n=a["n"] @ R.T)


def mode_uv(uv, mask):
    if not mask.any():
        return palette.uv("ground")
    q = np.round(uv[mask] * 16 - 0.5).astype(np.int32)
    keys, counts = np.unique(q[:, 0] * 16 + q[:, 1], return_counts=True)
    k = keys[np.argmax(counts)]
    return ((k // 16 + 0.5) / 16, (k % 16 + 0.5) / 16)


def shell(a):
    """The house as its box and a gable roof along its length (local street metres): the far level's stand-in."""
    p, n = a["p"], a["n"]
    low = p[:, 2] < GROUND_LINE
    x0, x1 = p[low, 0].min(), p[low, 0].max()
    y0, y1 = p[low, 1].min(), p[low, 1].max()
    walls = np.abs(n[:, 2]) < 0.2
    eave = float(np.percentile(p[walls, 2], 90)) if walls.any() else float(p[:, 2].max()) * 0.6
    ridge = max(float(np.percentile(p[:, 2], 99)), eave + 0.3)
    wall_uv = mode_uv(a["uv"], walls & (p[:, 2] > GROUND_LINE))
    roof_uv = mode_uv(a["uv"], n[:, 2] > 0.3)
    ym = (y0 + y1) / 2
    quads = [  # (corners, uv), each wound to face out
        ([(x0, y0, 0), (x1, y0, 0), (x1, y0, eave), (x0, y0, eave)], wall_uv),
        ([(x1, y1, 0), (x0, y1, 0), (x0, y1, eave), (x1, y1, eave)], wall_uv),
        ([(x0, y1, 0), (x0, y0, 0), (x0, y0, eave), (x0, y1, eave)], wall_uv),
        ([(x1, y0, 0), (x1, y1, 0), (x1, y1, eave), (x1, y0, eave)], wall_uv),
        ([(x0, y0, eave), (x1, y0, eave), (x1, ym, ridge), (x0, ym, ridge)], roof_uv),
        ([(x1, y1, eave), (x0, y1, eave), (x0, ym, ridge), (x1, ym, ridge)], roof_uv),
    ]
    tris = [([(x0, y1, eave), (x0, y0, eave), (x0, ym, ridge)], wall_uv), ([(x1, y0, eave), (x1, y1, eave), (x1, ym, ridge)], wall_uv)]
    P, N, U, T = [], [], [], []
    for poly, uv in quads + tris:
        q = np.array(poly, np.float32)
        nn = np.cross(q[1] - q[0], q[2] - q[0])
        nn /= max(np.linalg.norm(nn), 1e-6)
        b = len(P)
        P.extend(q)
        N.extend([nn] * len(q))
        U.extend([uv] * len(q))
        T.extend([(b, b + 1, b + 2)] + ([(b, b + 2, b + 3)] if len(q) == 4 else []))
    k = len(P)
    return dict(p=np.array(P, np.float32), n=np.array(N, np.float32), uv=np.array(U, np.float32),
                c=np.tile(np.array([0.6, 0.2, 1.0, 1.0], np.float32), (k, 1)), t=np.array(T, np.int32))


def ground(ci, cj, rows):
    """The chunk's ground: a 2 m grid, each triangle its own (flat, so the palette never smears), setts on the streets."""
    m = int(CHUNK / GROUND_STEP)
    xs = ci * CHUNK + np.arange(m + 1) * GROUND_STEP
    ys = cj * CHUNK + np.arange(m + 1) * GROUND_STEP
    X, Y = np.meshgrid(xs, ys)
    Z = np.vectorize(ground_z)(X, Y)
    G = np.stack([X, Y, Z], -1).astype(np.float32)                     # (m+1, m+1, 3), [j, i]
    a, b, c, d = G[:-1, :-1], G[:-1, 1:], G[1:, 1:], G[1:, :-1]
    P = np.stack([np.stack([a, b, c], 2), np.stack([a, c, d], 2)], 2).reshape(-1, 3, 3)
    mid = P.mean(1)
    rows = np.asarray(rows, np.float32)
    along = np.abs(mid[:, 1:2] - rows[None, :]).min(1) < STREET / 2
    k = np.mod(mid[:, 0], CROSS_EVERY)
    street = along | (k < STREET / 2) | (k > CROSS_EVERY - STREET / 2)
    U = np.where(street[:, None, None], np.array(palette.uv("setts_mean"), np.float32), np.array(palette.uv("ground"), np.float32))
    U = np.broadcast_to(U, (len(P), 3, 2))
    nn = np.cross(P[:, 1] - P[:, 0], P[:, 2] - P[:, 0])
    nn /= np.maximum(np.linalg.norm(nn, axis=1, keepdims=True), 1e-6)
    n = len(P)
    return dict(p=P.reshape(-1, 3), n=np.repeat(nn, 3, axis=0), uv=U.reshape(-1, 2).astype(np.float32),
                c=np.tile(np.array([1.0, 0.0, 1.0, 1.0], np.float32), (3 * n, 1)), t=np.arange(3 * n, dtype=np.int32).reshape(-1, 3))


def views(size, rows):
    """The district's judging views (street metres), on the street nearest its centre: the street stop (a person's eye
    looking along the street), 12 m up, the corner's high near-isometric view, the city camera (150 m up, 35 degrees
    down) and the whole district from low over its edge (everything in the frame: the worst case)."""
    c = size / 2.0
    row = min(rows, key=lambda r: abs(r - c))
    on = lambda x, y, up: (x, y, ground_z(x, y) + up)     # a point up metres above the ground under it
    lens28 = 46.4
    v = [
        ("street", on(c - 40, row - 1.5, 1.8), on(c + 60, row + 1.5, 4.0), lens28),
        ("into12", on(c - 30, row - 3.0, 12.0), on(c + 20, row + 4.0, 0.0), lens28),
        ("high", on(c + 31.5, row + 12 - 34, 53.0), on(c, row + 12, 0.0), 15.0),
        ("city", on(c - 120, row - 175, 150.0), on(c, row + 40, 0.0), lens28),
        ("over", on(c - 500, 60, 160.0), on(c + 200, size - 300, 0.0), lens28),
    ]
    return [dict(name=n, pos=[round(float(x), 2) for x in p], target=[round(float(x), 2) for x in t], fov=f) for n, p, t, f in v]


def merge(parts):
    if not parts:
        return None
    off = np.cumsum([0] + [len(a["p"]) for a in parts[:-1]])
    return dict(p=np.concatenate([a["p"] for a in parts]), n=np.concatenate([a["n"] for a in parts]),
                uv=np.concatenate([a["uv"] for a in parts]), c=np.concatenate([a["c"] for a in parts]),
                t=np.concatenate([a["t"] + o for a, o in zip(parts, off)]))


def pack(a, origin):
    """A mesh's bytes: its header and its vertices and indices in Unity's axes, relative to the chunk's origin."""
    if a is None or len(a["t"]) == 0:
        return struct.pack("<3I6f", 0, 0, 2, *([0.0] * 6)), 0
    p = to_unity(a["p"]) - np.asarray(origin, np.float32)
    v = np.zeros(len(p), VERTEX)
    v["p"] = p
    nn = to_unity(a["n"])
    v["n"][:, :3] = np.clip(np.round(nn * 127), -127, 127)
    v["c"] = np.clip(np.round(a["c"] * 255), 0, 255)
    v["uv"] = a["uv"]
    t = a["t"][:, [0, 2, 1]]                       # (the axis swap is a mirror: wind each triangle the other way)
    isz = 2 if len(p) <= 65535 else 4
    idx = t.astype("<u2" if isz == 2 else "<u4").tobytes()
    lo, hi = p.min(0), p.max(0)
    head = struct.pack("<3I6f", len(p), t.size, isz, *lo.tolist(), *hi.tolist())
    return head + v.tobytes() + idx, len(t)


def main(out, size, core, part, parts, bake_every, limit, box=None):
    t_start = time.time()
    bpy.ops.wm.read_factory_settings(use_empty=True)
    mat = palette.material()
    plots = layout(size)
    rows = sorted({p["kerb"] - p["side"] * STREET / 2 for p in plots})
    by_chunk = {}
    for p in plots:
        by_chunk.setdefault(chunk_of(p, size), []).append(p)
    n_chunks = int(math.ceil(size / CHUNK))
    keys = [(i, j) for j in range(n_chunks) for i in range(n_chunks)]
    mine = [k for n, k in enumerate(keys) if n % parts == part]
    if box:
        mine = [(i, j) for (i, j) in mine if box[0] <= i <= box[2] and box[1] <= j <= box[3]]
    c0, c1 = size / 2 - core / 2, size / 2 + core / 2
    for d in ("chunks", "records", "parts"):
        os.makedirs(os.path.join(out, d), exist_ok=True)
    if part == 0:
        with open(os.path.join(out, "district.json"), "w") as fh:
            json.dump(dict(size=size, core=core, chunk=CHUNK, plots=len(plots), rows=rows, views=views(size, rows)), fh, indent=1)
    stats = dict(part=part, parts=parts, size=size, core=core, plots=len(plots), chunks=[], seconds={})
    sec = dict(resolve=0.0, build=0.0, bake=0.0, extract=0.0, shell=0.0, ground=0.0, write=0.0)
    built = 0
    for (ci, cj) in mine:
        L0, shells, records, info = [], [], [], dict(i=ci, j=cj, houses=0, l0_houses=0, empty=0, l0_tris=0, tris_each=[], area=0.0, l0_area=0.0, baked=0)
        t_chunk = time.time()
        for p in by_chunk.get((ci, cj), []):
            if limit and built >= limit:
                break
            t0 = time.time()
            d = random_diary(p["i"])
            plan = resolve(d, 1989, SEED)
            t1 = time.time()
            sec["resolve"] += t1 - t0
            if plan is None:
                info["empty"] += 1
                continue
            ob = building.build(plan, DEFAULT_STYLE, material=mat)
            t2 = time.time()
            sec["build"] += t2 - t1
            front = p["kerb"] + p["side"] * SETBACK
            in_core = c0 <= p["x"] < c1 and c0 <= front < c1
            if in_core and bake_every and (built % bake_every == 0):
                bake.bake(ob)
                info["baked"] += 1
            t3 = time.time()
            sec["bake"] += t3 - t2
            a = house_arrays(ob)
            me = ob.data
            bpy.data.objects.remove(ob, do_unlink=True)
            bpy.data.meshes.remove(me)
            t4 = time.time()
            sec["extract"] += t4 - t3
            low = a["p"][:, 2] < GROUND_LINE
            f_local = float(a["p"][low, 1].min()) if low.any() else float(a["p"][:, 1].min())
            yaw = 0.0 if p["side"] > 0 else 180.0
            ty = front - f_local if p["side"] > 0 else front + f_local
            z = ground_z(p["x"], front)
            sh = shell(a)
            T = (p["x"], ty, z)
            shells.append(place(sh, yaw, T))
            if in_core:
                L0.append(place(a, yaw, T))
                info["l0_houses"] += 1
                info["l0_tris"] += len(a["t"])
            P = a["p"][a["t"]]
            area = 0.5 * float(np.linalg.norm(np.cross(P[:, 1] - P[:, 0], P[:, 2] - P[:, 0]), axis=1).sum())
            info["area"] += area
            if in_core:
                info["l0_area"] += area
            info["tris_each"].append(len(a["t"]))
            info["houses"] += 1
            records.append(d)
            built += 1
            sec["shell"] += time.time() - t4
        t5 = time.time()
        g = ground(ci, cj, rows)
        sec["ground"] += time.time() - t5
        t6 = time.time()
        origin = to_unity(np.array([ci * CHUNK, cj * CHUNK, 0.0], np.float32))
        blobs = [pack(merge(L0), origin), pack(merge(shells), origin), pack(g, origin)]
        data = b"OSCK" + struct.pack("<I3fI", 1, *origin.tolist(), len(blobs)) + b"".join(b for b, _ in blobs)
        name = f"c_{ci}_{cj}"
        with open(os.path.join(out, "chunks", name + ".bin"), "wb") as fh:
            fh.write(data)
        rec = json.dumps(records, separators=(",", ":"))
        with open(os.path.join(out, "records", name + ".json"), "w") as fh:
            fh.write(rec)
        sec["write"] += time.time() - t6
        info.update(seconds=time.time() - t_chunk, bytes=len(data), record_bytes=len(rec), l0_bytes=len(blobs[0][0]), shell_bytes=len(blobs[1][0]),
                    ground_bytes=len(blobs[2][0]), shell_tris=blobs[1][1], ground_tris=blobs[2][1])
        stats["chunks"].append(info)
        if limit and built >= limit:
            break
    stats["seconds"] = dict(sec, total=time.time() - t_start)
    stats["houses"] = built
    with open(os.path.join(out, "parts", f"part_{part}.json"), "w") as fh:
        json.dump(stats, fh)
    print(f"DISTRICT part {part}/{parts}: {len(stats['chunks'])} chunks, {built} houses, "
          + ", ".join(f"{k} {v:.1f} s" for k, v in stats["seconds"].items()))


if __name__ == "__main__":
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    out = argv[0]
    opts = dict(zip(argv[1::2], argv[2::2]))
    part, parts = (int(v) for v in opts.get("--part", "0/1").split("/"))
    main(out, float(opts.get("--size", 2048)), float(opts.get("--core", 512)), part, parts,
         int(opts.get("--bake", 1)), int(opts.get("--limit", 0)),
         [int(v) for v in opts["--box"].split(",")] if "--box" in opts else None)
