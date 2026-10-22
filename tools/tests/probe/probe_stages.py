"""The probe kind's stages (tools/tests/probe/kinds/probe.json): a tiny stand-in for a real kind, so the runner, the
chain, the cache and diff_stage are proved through all seven stages without Blender.

Each stage does what its real counterpart does, at toy size: facts validates the record; plan places each fill in
integer millimetres, jittered from its id and the world seed; life ages and wears the fills standing at the date, in
years and per mille; geometry makes a box per piece (a worn slab splits in two) and summarises pieces, fills and
chunks; bake writes a per-vertex channel; export writes an OBJ into the stage's work folder. Geometry and bake use
numpy where it is (Blender's Python) and lists where it is not (the venv): their hashes must agree.
"""
import copy
import glob
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
for p in (os.path.join(ROOT, "tools"), os.path.join(ROOT, "blender", "resolver")):
    if p not in sys.path:
        sys.path.insert(0, p)
import hashes as HX  # noqa: E402
import hashing as HS  # noqa: E402
from hashes import Blob  # noqa: E402

try:
    import numpy as np
except ImportError:
    np = None

BOX_TRIANGLES = [(0, 2, 1), (1, 2, 3), (4, 5, 6), (5, 7, 6), (0, 1, 4), (1, 5, 4),
                 (2, 6, 3), (3, 6, 7), (0, 4, 2), (2, 4, 6), (1, 3, 5), (3, 7, 5)]


def facts(ctx):
    """The record; validated in full where jsonschema is, by validate_record's checks with the probe's own kind, pack
    and parts standing in for the town's."""
    try:
        import validate_record as VR
    except ImportError:
        ctx.log("not validated: this Python has no jsonschema")
        return copy.deepcopy(ctx.source)
    c = VR.Contracts()
    c._kinds[ctx.kind["kind"]] = ctx.kind
    c._packs[ctx.source["pack"]] = ctx.pack
    parts = os.path.join(ctx.pack_dir, "parts")
    for f in glob.glob(os.path.join(parts, "**", "*.json"), recursive=True):
        c._parts[(ctx.source["pack"], os.path.relpath(f, parts)[:-5].replace(os.sep, "/"))] = VR.read_json(f)
        ctx.depends(f)
    counts = VR.check_record(c, ctx.source, label=ctx.source["id"])
    if c.problems:
        raise ValueError("the record does not validate:\n  " + "\n  ".join(c.problems))
    ctx.log("valid: %d events, %d slots, %d fills" % (counts["events"], counts["slots"], counts["fills"]))
    return copy.deepcopy(ctx.source)


def plan(ctx):
    """Every fill of every socket, placed in integer millimetres: its slot's place (a flaw's on its slab's), less the
    joint, jittered from its id."""
    joint = ctx.table("metrics")["jointMm"]
    j = ctx.params["jitterMm"]
    slots = dict((s["id"], s) for s in ctx.record["slots"])
    fills = []
    for sid in sorted(slots):
        s = slots[sid]
        if s["type"] != "socket":
            continue
        at = list(s["at"])
        parent = sid.rsplit("/", 2)[0]
        if parent in slots and slots[parent]["type"] == "socket":
            at = [a + b for a, b in zip(slots[parent]["at"], at)]
        for f in s["fills"]:
            jit = [HS.h(ctx.world_seed, f["id"], "plan", axis) % (2 * j + 1) - j for axis in ("x", "y")]
            size = list(f["fit"]["size"])
            body = f["role"] == "body"
            fills.append({"fill": f["id"], "slot": sid, "part": f["part"],
                          "at": [at[0] + jit[0] + (joint // 2 if body else 0), at[1] + jit[1] + (joint // 2 if body else 0),
                                 at[2]],
                          "size": [size[0] - joint, size[1] - joint, size[2]] if body else size,
                          "from": f["from"]["year"], "to": f["to"]["year"] if f["to"] else None})
    return {"fills": fills}


def life(ctx):
    """The fills standing at the date: their years and their wear in per mille."""
    date = ctx.date
    rate = ctx.params["wearPerMillePerYear"]
    out = {}
    for f in ctx.outputs["plan"]["fills"]:
        if f["from"] > date or (f["to"] is not None and f["to"] <= date):
            continue
        years = date - f["from"]
        out[f["fill"]] = {"years": years, "wear": min(1000, years * rate + HS.h(ctx.world_seed, f["fill"], "life") % 40)}
    return {"date": date, "fills": out}


def _box(xa, xb, y0, sy, z0, sz):
    """A box's eight corners in Python floats: corner k takes x from bit 0, y from bit 1, z from bit 2."""
    return [[xa + ((k >> 0) & 1) * (xb - xa), y0 + ((k >> 1) & 1) * sy, z0 + ((k >> 2) & 1) * sz] for k in range(8)]


def geometry(ctx):
    """A box per piece, its top hollowed by its wear; a slab worn past splitAtWear is two pieces. Positions in metres."""
    hollow, split = ctx.params["hollowM"], ctx.params["splitAtWear"]
    plan = dict((f["fill"], f) for f in ctx.outputs["plan"]["fills"])
    worn = ctx.outputs["life"]["fills"]
    boxes, pieces = [], {}
    for fid in sorted(worn):
        p, w = plan[fid], worn[fid]["wear"]
        n = 2 if w >= split else 1
        for i in range(n):
            x0 = p["at"][0] + p["size"][0] * i // n
            x1 = p["at"][0] + p["size"][0] * (i + 1) // n
            boxes.append((x0 / 1000.0, x1 / 1000.0, p["at"][1] / 1000.0, p["size"][1] / 1000.0, p["at"][2] / 1000.0,
                          p["size"][2] / 1000.0 - hollow * (w / 1000.0)))
            pieces["%s#%d" % (fid, i)] = {"fill": fid, "chunk": HX.chunk_of(x0, p["at"][1]), "vertices": 8,
                                          "triangles": 12}
    if np is not None:
        b = np.array(boxes, dtype=np.float64)
        bits = np.array([[(k >> 0) & 1, (k >> 1) & 1, (k >> 2) & 1] for k in range(8)], dtype=np.float64)
        pos = np.empty((len(boxes), 8, 3))
        pos[:, :, 0] = b[:, None, 0] + bits[None, :, 0] * (b[:, 1] - b[:, 0])[:, None]
        pos[:, :, 1] = b[:, None, 2] + bits[None, :, 1] * b[:, None, 3]
        pos[:, :, 2] = b[:, None, 4] + bits[None, :, 2] * b[:, None, 5]
        positions = Blob(pos.reshape(-1, 3))
        tris = Blob((np.array(BOX_TRIANGLES, dtype=np.int32)[None, :, :]
                     + 8 * np.arange(len(boxes), dtype=np.int32)[:, None, None]).reshape(-1, 3))
        piece = Blob(np.repeat(np.arange(len(boxes), dtype=np.int32), 8))
    else:
        positions = Blob([v for bx in boxes for v in _box(*bx)], "float64")
        tris = Blob([[a + 8 * i, b + 8 * i, c + 8 * i] for i in range(len(boxes)) for a, b, c in BOX_TRIANGLES], "int32")
        piece = Blob([i for i in range(len(boxes)) for _ in range(8)], "int32")
    for i, pid in enumerate(sorted(pieces, key=lambda k: (k.split("#")[0], int(k.split("#")[1])))):
        pieces[pid]["hash"] = HX.hex64(positions.slice_hash(8 * i, 8 * i + 8))
    out = {"mesh": {"positions": positions, "triangles": tris, "piece": piece}, "pieces": pieces}
    out.update(HX.summarise_pieces(pieces))
    return out


def bake(ctx):
    """Each vertex's wear, as the shader would read it (float32), and each piece's share of it hashed."""
    geo = ctx.outputs["geometry"]
    worn = ctx.outputs["life"]["fills"]
    order = sorted(geo["pieces"], key=lambda k: (k.split("#")[0], int(k.split("#")[1])))
    per_piece = [worn[geo["pieces"][pid]["fill"]]["wear"] for pid in order]
    if np is not None:
        idx = geo["mesh"]["piece"].values
        wear = Blob((np.array(per_piece, dtype=np.float64)[idx] / 1000.0).astype(np.float32))
    else:
        wear = Blob([per_piece[i] / 1000.0 for i in geo["mesh"]["piece"].tolist()], "float32")
    pieces = {}
    for i, pid in enumerate(order):
        p = geo["pieces"][pid]
        pieces[pid] = {"fill": p["fill"], "chunk": p["chunk"], "hash": HX.hex64(wear.slice_hash(8 * i, 8 * i + 8))}
    out = {"channels": {"wear": wear}, "pieces": pieces}
    out.update(HX.summarise_pieces(pieces))
    return out


def export(ctx):
    """The mesh as an OBJ in the stage's work folder; its text hash and counts in the output."""
    geo = ctx.outputs["geometry"]["mesh"]
    verts, tris = geo["positions"].tolist(), geo["triangles"].tolist()
    lines = ["o %s" % ctx.record["id"]]
    lines += ["v %r %r %r" % tuple(v) for v in verts]
    lines += ["f %d %d %d" % (a + 1, b + 1, c + 1) for a, b, c in tris]
    text = "\n".join(lines) + "\n"
    path = os.path.join(ctx.work, ctx.record["id"] + ".obj")
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    ctx.wrote(path)
    return {"files": {ctx.record["id"] + ".obj": {"text": HX.text_hash(text), "vertices": len(verts),
                                                  "triangles": len(tris)}}}


def failing(ctx):
    """A checks entry that never passes: the runner must stop and fail on it (tools/tests/test_stages.py)."""
    return {"pass": False, "problems": ["the probe's failing check"]}
