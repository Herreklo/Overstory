"""Way P's page and strokes for a whole house: finish/paint.py's corner grown to every wall and every opening.

    Blender -b --factory-startup -P blender/parts/street/paint.py -- --gen cache/street/gen/107 --cache cache/street/bake/107

Reads house.json (house.py) and the bakes (bake.py), and writes into <cache>/out what way P reads, each the page's size:
  hist-p.png, hist-p2.png, paint-stroke.png, paint.json   as finish/paint.py's: the same channels and digest keys
  geo.png, street-normal.png                              as finish/marks.py's (marks.py here)
and a look at hist-p's R and G and hist-p2's R side by side, into cache/street/paint-preview/<house>.png.

The corner's values (finish.json `painted`, p3) are used as they are; what changes is where they act and how much.
Each opening's shapes leave its own sill, head and battens on its own wall; the sill leaks at its lower end by the
frame's tilt, or, level, at the end toward the weather. Wear is graded by the facts (paint.json `wear`): the years since
the last coat and since the house was let go, the wall's exposure to the wet winds and the sill's fall, so the lee
walls keep their paint and the street front fails as p3 does. Gutter joints and the downpipe's shoe place their water;
the roof's tiles take their values tile by tile. No shape claims a dated event (UK4).
"""

import copy
import importlib.util
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
FINISH = os.path.join(HERE, "..", "finish")
sys.path.insert(0, FINISH)
import finishlib as FL  # noqa: E402
from finishlib import HS  # noqa: E402


def module(path, name):
    """A script as a module of its own name, its main left unrun (each guards its main)."""
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


FP = module(os.path.join(FINISH, "paint.py"), "finish_paint")  # the corner's shapes; it loads the corner's marks
MK = FP.MK
SM = module(os.path.join(HERE, "marks.py"), "street_marks")
key, field, wave, junction = MK.key, FP.field, FP.wave, FP.junction


# ---------------------------------------------------------------- the facts that grade the wear


def toward_weather(paints):
    """Toward where the wet winds come from (paints.json weather), in the pack's frame (x east, y north), which is the
    house's: its street front, -y, faces south."""
    a = math.radians(paints["weather"]["fromDeg"])
    return np.array([math.sin(a), math.cos(a)])


def exposure(wall, paints):
    """How squarely a wall faces the wet winds: 1 facing them, `least` on the lee."""
    W = paints["weather"]
    return W["least"] + (1.0 - W["least"]) * max(0.0, float(np.dot(wall["out"], toward_weather(paints))))


def coats(meta, paints, since):
    """The paint's age (paints.json upkeep): painted in `since` (the house's building, or the lean-to's), then every
    cycle (by the house's wealth) until a neglect or a boarding stops it, its last coat the cycle's last turn before
    that year, or a 'repainted' event's. Returns the years since that coat, the years let go, and the cycle."""
    lo, hi = paints["upkeep"]["cycleYears"]
    cyc = lo + (hi - lo) * min(max(meta["wealth"] / 1000.0, 0.0), 1.0)
    stops = [e["year"] for e in meta["events"] if e["kind"] in ("neglected", "boarded") and e["year"] <= meta["year"]]
    stop = min(stops) if stops else meta["year"]
    last = since + max(0, math.floor((stop - since) / cyc - 1e-9)) * cyc
    last = max([last] + [e["year"] for e in meta["events"] if e["kind"] == "repainted" and e["year"] <= meta["year"]])
    return meta["year"] - last, (meta["year"] - stop) if stops else 0, cyc


def severity(meta, paints, A, wall, tilt=0.0):
    """How far the paint has failed on a wall (and at an opening, by its sill's fall): 1 is p3."""
    since = meta["leanTo"]["year"] if wall["kind"] == "lean" else meta["built"]
    age, neglected, cyc = coats(meta, paints, since)
    tf = 1.0 + A["tiltGain"] * min(1.0, abs(tilt) / A["tiltFull"])
    return A["scale"] * (age + neglected) / cyc * exposure(wall, paints) * tf


def leak_side(o, wall, paints, A):
    """Which end of an opening leaks (-1 its start, +1 its end): the sill's lower end, z rising by `tilt` a metre along
    the wall (house.py); a level sill, or a door, at the end toward the weather."""
    t = o.get("tilt", 0.0)
    if "sill" in o and abs(t) >= A["level"]:
        return 1.0 if t < 0 else -1.0
    return 1.0 if float(np.dot(wall["dir"], toward_weather(paints))) > 0 else -1.0


def floor_of(meta, o, wall):
    """Where the water off an opening stops running down its wall: the drip board (`heights.drip`) on the house, the
    lean-to's lowest butt, or the top of an opening below it, whose cap takes it."""
    sx0, sx1 = (o.get("sill") or o["casing"])[:2]
    below = [p["casing"][3] for p in meta["openings"] if p is not o and p["wall"] == o["wall"]
             and p["casing"][3] <= o["casing"][2] and p["casing"][0] < sx1 + 0.3 and p["casing"][1] > sx0 - 0.3]
    if below:
        return [max(below)] * 2
    if wall["kind"] == "lean":
        return [meta["courses"][str(wall["group"])][0]] * 2
    return meta["heights"]["drip"]


def opening_meta(meta, o, k, wall, cap_t):
    """The corner's meta for one opening, so the corner's shapes read it: its own features (a door's sill stands at
    its casing), its wall's courses and butt joints, the floor its water runs to (as `heights.drip`) and its head;
    seeds of its own (`house` names the opening)."""
    cx0, cx1, cz0, cz1 = o["casing"]
    f = {"sill": o.get("sill") or [cx0, cx1, cz0, 0.0], "casing": o["casing"], "sheets": o.get("sheets"),
         "battens": o.get("battens", []), "nails": o.get("nails", []), "opening": [o["a0"], o["a1"]],
         "joints": [("street", a, zb, zt) for w, a, zb, zt in meta["features"]["joints"] if w == wall["i"]]}
    return {"world": meta["world"], "house": f"{meta['house']}/open{k}", "courses": meta["courses"][str(wall["group"])],
            "features": f, "heights": {"drip": floor_of(meta, o, wall), "head": cz1 - cap_t}}


def graded(Q, s, A, om, door):
    """The corner's failed paint at severity `s`: its washes and runs' strengths, its peel's heights and the casing's
    peel reach times s (at most `most`); below 1 the tongue's runs end sooner and the runs cross fewer laps. A door has
    no sill: only the head's run."""
    q = copy.deepcopy(Q)
    T = q["tongue"]
    g = min(s, A["most"])
    f, h = om["features"], om["heights"]
    spans = {"leak": f["sill"][2] - h["drip"][0], "dry": f["sill"][2] - h["drip"][0], "cap": h["head"] - f["casing"][2]}
    if door:
        T["runs"] = {"cap": T["runs"]["cap"]}
    for name, R in T["runs"].items():
        R["L"] *= g
        R["peel"] = [[w, min(0.95, ht * g)] for w, ht in R["peel"]]
        if g < 1.0:
            R["length"] = (R["length"] or spans[name]) * g
    for kind in ("leak", "dry", "batten"):
        S = T["runoff"][kind]
        S["strength"] *= g
        S["boards"] = max(1, int(round(S["boards"] * min(g, 1.0))))
        S["flake"] = [S["flake"][0], min(0.95, S["flake"][1] * g)]
    q["peel"]["casing"]["reach"] *= g
    return q


# ---------------------------------------------------------------- the failed paint


def runoff(pg, T, meta, srcs):
    """finish/paint.py's runoff, its sources given: each (its settings, along, z), one narrow streak down its laps,
    a soft wash from a neck under the lap above to the drip edge, a hard tick there, and at its last drip edge a flake
    of bare wood; from the street stop one soft mark of its own (`far`). Returns the peel's field, the wash near and
    far (L*) and the stain's field."""
    R = T["runoff"]
    c = meta["courses"]
    clad = pg.m["cladding"] & pg.vertical & pg.street
    joints = [(x, b) for face, x, b, _ in meta["features"]["joints"] if face == "street"]
    peel_, wash, far, stain = np.zeros(pg.shape), np.zeros(pg.shape), np.zeros(pg.shape), np.zeros(pg.shape)
    drip = R["dripMm"] / 1000.0
    Fr = R["far"]
    for si, (S, x0, z0) in enumerate(srcs):
        k = key(meta, "p-runoff", si)
        u = lambda *p: 2.0 * HS.unit(HS.h(k, *p)) - 1.0  # noqa: E731
        faces = [(c[i], min(c[i + 1], z0)) for i in range(len(c) - 2, -1, -1) if c[i] < z0 - 1e-6][:S["boards"]]
        cx = x0
        for j, (b, t) in enumerate(faces):
            cx += R["wander"] * u("c", j)
            wj = (R["width"][0] + (R["width"][1] - R["width"][0]) * j / max(len(faces) - 1, 1)) * S["scale"] * (1.0 + 0.15 * u("w", j))
            face = clad & (pg.z >= b) & (pg.z < t)
            Wb = R["wobble"]
            off = np.abs(pg.along - cx) + Wb["amp"] * wave(pg, HS.h(k, "e", j), Wb["cell"], pg.z)
            s = np.clip((t - pg.z) / max(t - b, 1e-3), 0.0, 1.0)
            half = 0.5 * wj * (R["neck"] + (1.0 - R["neck"]) * s ** R["spread"])
            core = 1.0 - FL.smoothstep(R["core"] * half, half, off)
            left = 1.0 - R["fade"] * j / max(len(faces) - 1, 1)
            wash = np.maximum(wash, np.where(face, S["strength"] * left * (R["L"][0] + (R["L"][1] - R["L"][0]) * s) * core, 0.0))
            hw = 0.5 * wj * Fr["width"]
            far = np.maximum(far, np.where(face, S["strength"] * left * Fr["L"] * (1.0 - FL.smoothstep(Fr["core"] * hw, hw, off)), 0.0))
            tick = np.minimum(0.5 * wj * R["tick"] - off, drip * (1.0 + 0.3 * u("t", j)) - (pg.z - b))
            stain = np.maximum(stain, np.where(face, field(tick, R["soft"]), 0.0))
            if j == len(faces) - 1:
                fw, share = S["flake"]
                hf = 0.5 * fw * (1.0 + 0.2 * u("fw"))
                pc = cx + 0.3 * hf * u("fc")
                js = [x for x, jb in joints if abs(jb - b) < 1e-3 and abs(x - pc) < hf + T["joint"]["reach"]]
                peel_ = np.maximum(peel_, np.where(face, FP.strip(pg, T, k, pc, hf, b, t, share, js), 0.0))
    return peel_, wash, far, stain


def sources(R, meta, side, door):
    """Where the water leaves an opening, as the corner's: the sill's horns (the leaking one most), and each batten's
    lower end, where its tilt sends the water."""
    f = meta["features"]
    srcs = []
    if not door:
        (leak, lo), (dry, do) = FP.horns(meta, side)
        z_sill = f["sill"][2]
        srcs += [(R["leak"], leak - lo * R["inset"], z_sill), (R["dry"], dry - do * R["inset"], z_sill)]
    for bx0, bx1, zc, slope, w in f["battens"]:
        x = bx0 if slope > 0 else bx1
        srcs.append((R["batten"], x + (R["inset"] if slope > 0 else -R["inset"]), zc + slope * (x - (bx0 + bx1) / 2.0) - w / 2.0))
    return srcs


def peel_casing(pg, Q, meta, side):
    """The corner's peel at the casing's leaking leg, at its foot (on the sill, or a door's threshold)."""
    R = Q["peel"]
    f = meta["features"]
    W = R["wobble"]
    cx0, cx1, cz0, _ = f["casing"]
    ax0, ax1 = f["opening"]
    leg = (cx0 - 0.01, ax0) if side < 0 else (ax1, cx1 + 0.01)
    on = pg.m["trims"] & pg.vertical & (pg.along > leg[0]) & (pg.along < leg[1]) & (pg.z >= cz0 - 0.005)
    edge = cz0 + R["casing"]["reach"] * (1.0 - W["share"] * 0.5 * (1.0 + wave(pg, key(meta, "p-casing"), W["cell"], pg.z)))
    return np.where(on, field(edge - pg.z, R["soft"]), 0.0)


def peel_tops(pg, Q, k):
    """The corner's ledges' tops, standing wet: bare but at their ends, where what they meet keeps them."""
    R = Q["peel"]
    a0p, a1p = pg.per_piece(pg.along, "min"), pg.per_piece(pg.along, "max")
    ins = R["tops"]["inset"] * (1.0 + 0.5 * wave(pg, k, R["wobble"]["cell"]))
    d = np.minimum(np.minimum(pg.along - a0p - ins, a1p - pg.along - ins), 1.0)
    return np.where(pg.m["trims"] & pg.up, field(d, R["soft"]), 0.0)


def opening_stains(pg, Q, meta, side):
    """The corner's stains an opening's facts place: rust under some of its battens' nails, down the batten and the
    casing below; the boarding's damp strip down its leaking side."""
    f = meta["features"]
    out = np.zeros(pg.shape)
    Ru = Q["rust"]
    k = key(meta, "p-rust")
    iron = (pg.m["trims"] | pg.m["batten"]) & (pg.y < 0.0)
    for i, (xn, zn) in enumerate(f["nails"]):
        if HS.unit(HS.h(k, i)) >= Ru["share"]:
            continue
        ln = Ru["length"][0] + (Ru["length"][1] - Ru["length"][0]) * HS.unit(HS.h(k, i, "len"))
        out = np.maximum(out, FP.run(pg, HS.h(k, i, "w"), xn, zn, ln, Ru["width"], 0.002, iron))
    B = Q["sheet"]
    if f["sheets"] and B["leakWidth"] > 0.0:
        ab0, ab1 = f["sheets"][:2]
        from_leak = np.where(side < 0, pg.along - ab0, ab1 - pg.along)
        sd = B["leakWidth"] + B["wobble"]["amp"] * wave(pg, key(meta, "p-sheet", "leak"), B["wobble"]["cell"], pg.z) - from_leak
        out = np.maximum(out, np.where(pg.m["sheet"], field(sd, 0.04), 0.0))
    return out


def splash(pg, Q, P, S, wall, meta):
    """The foot's wetting along a wall, as the corner's broad splash: one broad swell under each of its drips by how
    much it carries (a gutter's leaking joint, the downpipe's shoe); with none, a gable's verge run-off, even, and the
    lean-to's gutterless low eave its whole length."""
    ds = [d for d in meta["features"]["drips"] if d[0] == wall["i"]]
    if ds:
        broad = np.zeros(pg.shape)
        for _, x, flow, _ in ds:
            broad = np.maximum(broad, flow * MK.gauss(pg.along - x, Q["wet"]["splashWidth"]))
        return broad
    eave = wall["kind"] == "lean" and abs(wall["dir"][0]) > 0.9
    return np.full(pg.shape, S["splash"]["leanEave"] if eave else P["marks"]["splash"]["gable"])


def wet_margin(pg, Q, meta, broad, plinth):
    """The plinth's wet margin (the corner's): splash keeps its foot wet, higher where the splash is, its top a
    wavering found edge."""
    Wt = Q["wet"]
    if "L" in Wt:
        return np.zeros(pg.shape)
    top = Wt["top"] + Wt["splash"] * broad + Wt["wobble"]["amp"] * wave(pg, key(meta, "p-wet", meta["wall"]), Wt["wobble"]["cell"])
    return np.where(plinth, field(top - pg.z, Wt["soft"]), 0.0)


# ---------------------------------------------------------------- the values


def wall_low(pg, Q, clad, zf):
    """How low on its wall each point is, 0 under the eave (or the verge) to 1 at the boards' foot, eased by the
    gradient's power; and the wall's top above each point."""
    top = FP.edges(pg, clad)
    t = np.clip((pg.z - zf) / np.maximum(top - zf, 0.1), 0.0, 1.0)
    return (1.0 - t) ** Q["wall"]["power"], top


def wall_values(pg, Q, zf, z_plinth, broad):
    """The corner's broad washes on one wall: its one gradient, light at its top and darkening steadily to its foot;
    under the eave a soft contact band; the plinth darker toward the ground, its top under the drip board dark."""
    dl = np.zeros(pg.shape)
    clad = pg.m["cladding"] & pg.vertical
    wall = (pg.m["cladding"] | pg.m["trims"]) & pg.vertical
    plinth = (pg.m["stone"] | pg.m["concrete"]) & pg.vertical
    low, top = wall_low(pg, Q, clad, zf)
    Wl = Q["wall"]
    dl += np.where(wall, Wl["topL"] + (Wl["footL"] - Wl["topL"]) * low, 0.0)
    E = Q["eave"]
    d = top - pg.z
    dl -= np.where(wall & (d >= -0.002), E["L"] * (1.0 - FL.smoothstep(0.0, E["reach"], d)) ** E["power"], 0.0)
    Pl = Q["plinth"]
    dl -= np.where(plinth, Pl["L"] * (1.0 - np.clip(pg.z / z_plinth, 0.0, 1.0)), 0.0)
    dl -= np.where((pg.m["stone"] | pg.m["concrete"]) & pg.up, Pl.get("capL", 0.0), 0.0)
    Wt = Q["wet"]
    if "L" in Wt:
        wet = 1.0 - FL.smoothstep(-Wt["soft"], Wt["soft"], pg.z - Wt["top"] - Wt["splash"] * broad)
        dl -= np.where(plinth, Wt["L"] * wet, 0.0)
    return dl, top, low


def opening_values(pg, Q, meta, side, board):
    """The corner's broad washes an opening places: a soft wash widening under its sill; its boarding holding water,
    darkest at its head, down its leaking side and at the sill, in one soft wash, with a band of its own above the lower
    batten."""
    f = meta["features"]
    dl = np.zeros(pg.shape)
    sx0, sx1, z_sill, _ = f["sill"]
    Sw = Q["sillWash"]
    if Sw["L"]:
        below = np.clip(z_sill - pg.z, 0.0, None)
        hw = (sx1 - sx0) / 2.0 + Sw["spread"] * below
        across = MK.soft_box(pg.along - (sx0 + sx1) / 2.0, -hw, hw, Sw["soft"])
        fall = (1.0 - np.clip(below / Sw["reach"], 0.0, 1.0)) ** 1.5
        dl -= np.where(pg.m["cladding"] & pg.vertical & (pg.z < z_sill), Sw["L"] * across * fall, 0.0)
    if not f["sheets"]:
        return dl
    Bw = board["wash"]
    sheet = pg.m["sheet"]
    ab0, ab1, zb0, zb1 = f["sheets"][:4]
    from_leak = np.where(side < 0, pg.along - ab0, ab1 - pg.along)
    head = (1.0 - FL.smoothstep(0.0, Bw["head"], zb1 - pg.z)) * (1.0 - 0.5 * np.clip(from_leak / (ab1 - ab0), 0, 1))
    lk = 1.0 - FL.smoothstep(0.0, Bw["leak"], from_leak)
    bx0, bx1, zc, slope, bw = f["battens"][0]
    zl = zc + slope * (pg.along - (bx0 + bx1) / 2.0) + bw / 2.0
    lowness = np.clip(0.5 - np.sign(slope) * (pg.along - (bx0 + bx1) / 2.0) / max(bx1 - bx0, 1e-3), 0.0, 1.0)
    bat = np.where(pg.z > zl - 0.01, 1.0 - FL.smoothstep(0.0, Bw["batten"] * (1.0 + Bw["lowEnd"] * lowness), pg.z - zl), 0.0)
    sill = 1.0 - FL.smoothstep(0.0, Bw["sill"], pg.z - zb0)
    wash = 1.0 - (1.0 - head) * (1.0 - lk) * (1.0 - 0.6 * sill)
    dl -= np.where(sheet, np.maximum(Bw["L"] * wash, Bw["batL"] * bat), 0.0)
    Pb = board.get("blotch")
    if Pb:
        k = key(meta, "p-blotch")
        n = sum(a * FL.noise2(pg.along / c, pg.z / c, HS.h(k, j)) for j, (c, a) in enumerate(Pb["octaves"])) / sum(a for _, a in Pb["octaves"])
        lowS = np.clip((zb1 - pg.z) / max(zb1 - zb0, 1e-3), 0.0, 1.0)
        dl -= np.where(sheet, Pb["L"] * FL.smoothstep(Pb["cut"] - Pb["soft"], Pb["cut"] + Pb["soft"], n + Pb["low"] * (lowS - 0.5)), 0.0)
    return dl


def down(v, dl, base, mask, d, J, to="to"):
    """A junction's dark (the corner's) on a view: the value drawn down to J[to] at the junction, easing back over
    J's reach, from what the paint is there now."""
    v.put(dl, -np.where(mask, junction(d, v.get(base) + v.get(dl), J[to], J["reach"]), 0.0), "add")


def opening_junctions(v, Q, meta, dl, base, battens):
    """The darks an opening's facts place: under its sill, under each of its battens (onto the trims and the sheet),
    under its head on the sheet."""
    J = Q["junction"]
    f = meta["features"]
    clad = v.m["cladding"] & v.vertical
    if f["sill"][3] > 0.0:
        sx0, sx1, z_sill, _ = f["sill"]
        down(v, dl, base, clad & (MK.soft_box(v.along, sx0, sx1, 0.015) > 0.5), z_sill - v.z, J["sill"])
    wall = (v.m["cladding"] | v.m["trims"]) & v.vertical
    for i in battens:
        b = (v.piece == i) & v.vertical
        if not b.any():
            continue
        foot_b = FP.edges(v, b, top=False)
        a0, a1 = v.along[b].min(), v.along[b].max()
        under = (v.along > a0) & (v.along < a1)
        dB = foot_b - v.z
        onto = wall if J["batten"].get("clad", True) else v.m["trims"] & v.vertical
        down(v, dl, base, onto & ~b & under, dB, J["batten"])
        down(v, dl, base, v.m["sheet"] & under, dB, J["batten"], "sheetTo")
    if f["sheets"]:
        down(v, dl, base, v.m["sheet"], f["sheets"][3] - v.z, J["head"])


def opening_small(pg, Q, meta):
    """The small an opening places: its battens' end grain and the nails' heads, its sheets' join, a dark seam."""
    f = meta["features"]
    dl = np.zeros(pg.shape)
    Bt = Q["batten"]
    bat = pg.m["batten"]
    for bx0, bx1, zc, slope, w in f["battens"]:
        zl = pg.z - (zc + slope * (pg.along - (bx0 + bx1) / 2.0))
        on = bat & (np.abs(zl) <= w / 2.0 + 0.03) & (pg.along > bx0 - 0.05) & (pg.along < bx1 + 0.05)
        ends = np.minimum(np.abs(pg.along - bx0), np.abs(bx1 - pg.along))
        dl -= np.where(on, Bt["endL"] * FL.smoothstep(Bt["endMm"] / 1000.0, 0.0, ends), 0.0)
    Ru = Q["rust"]
    r_head = Ru["headMm"] / 1000.0
    for xn, zn in f["nails"]:
        r = np.hypot(pg.along - xn, pg.z - zn)
        dl -= np.where(bat, Ru["headL"] * FL.smoothstep(r_head, 0.6 * r_head, r), 0.0)
    sheet = pg.m["sheet"]
    if sheet.any():
        B = Q["sheet"]
        z0, z1 = pg.per_piece(pg.z, "min"), pg.per_piece(pg.z, "max")
        zs0, zs1 = pg.z[sheet].min(), pg.z[sheet].max()
        dj = np.minimum(np.where(z1 >= zs1 - 0.01, np.inf, z1 - pg.z), np.where(z0 <= zs0 + 0.01, np.inf, pg.z - z0))
        dl -= np.where(sheet, B["joinL"] * FL.smoothstep(B["joinMm"] / 1000.0, 0.0, dj), 0.0)
    return dl


def tile_values(pg, Q, meta, roof):
    """The roof one dark mass, a few of its tiles catching more light, tile by tile: each cell of `cover` along its
    eave by `course` up its slope from the foot (features.roof), so a plane that stands for many tiles lights its own
    few. Off any slope (the ridge), by piece, as the corner's."""
    T = Q["tiles"]
    tiles = pg.m["tiles"] | pg.m["roof"]
    if roof is None:
        cell = (pg.piece, 0, 0)
    else:
        a = math.radians(roof["pitch"])
        # up the slope from its foot, in the eave wall's own frame (y back from its face), as the foot is given
        s = (pg.y - roof["foot"][0]) * math.cos(a) + (pg.z - roof["foot"][1]) * math.sin(a)
        cell = (np.floor(s / roof["course"]).astype(np.int64), np.floor((pg.along - roof["x0"]) / roof["cover"]).astype(np.int64),
                np.full(pg.shape, roof["wall"]))
    u = FL.unit(key(meta, "p-tile"), *cell)
    v = FL.unit(key(meta, "p-tile-v"), *cell)
    return np.where(tiles & (u < T["share"]), T["L"] * (0.5 + 0.5 * v), 0.0)


def joint_lines(pg, S, meta, wall):
    """A thin dark at each butt joint of a wall's boards (features.joints), as the junctions are drawn."""
    J = S["joint"]
    w = J["mm"] / 1000.0
    clad = pg.m["cladding"] & pg.vertical
    dl = np.zeros(pg.shape)
    for wi, a, zb, zt in meta["features"]["joints"]:
        if wi != wall["i"]:
            continue
        on = clad & (pg.z >= zb) & (pg.z < zt) & (np.abs(pg.along - a) < w)
        dl -= np.where(on, J["L"] * (1.0 - FL.smoothstep(0.0, w, np.abs(pg.along - a))), 0.0)
    return dl


def grime(pg, Q, low, sills):
    """The lap grime's strength on a wall's boards: everywhere some, more down its gradient and on the courses each
    sill drips on."""
    L = Q["lap"]
    sill = np.zeros(pg.shape)
    for sx0, sx1, z_sill, _ in sills:
        sill = np.maximum(sill, MK.soft_box(pg.along, sx0 - 0.1, sx1 + 0.1, L["sillSoft"]) * MK.soft_box(pg.z, z_sill - 0.35, z_sill, L["sillSoft"]))
    a = L["base"] + L["foot"] * low + L["sill"] * sill
    return np.where(pg.m["cladding"] & pg.vertical, np.clip(a, 0.0, 1.0), 0.0)


# ---------------------------------------------------------------- the digest's colours


def house_paint(meta, paints):
    """The paint the house wears (paints.json): a 'repainted' event's, else its era's default; its trims' with it."""
    D = paints["defaults"]
    ev = [e for e in meta["events"] if e["kind"] == "repainted" and e["year"] <= meta["year"] and e["params"].get("paint")]
    if ev:
        wall = ev[-1]["params"]["paint"]
        return paints["paints"][wall], paints["paints"][D["repaint"].get(wall, D[meta["era"]]["trim"])]
    d = D["warehouse"] if meta["type"] == "warehouse" else D[meta["era"]]
    return paints["paints"][d["wall"]], paints["paints"][d["trim"]]


def preview(path, pl, dl, wash, rng, washL):
    """hist-p's R and G and hist-p2's R side by side, each at half the page, to look at."""
    half = lambda a: a.reshape(a.shape[0] // 2, 2, a.shape[1] // 2, 2).mean(axis=(1, 3))  # noqa: E731
    panels = [half(pl), half(0.5 + np.clip(dl, -rng, rng) / (2.0 * rng)), half(np.clip(wash / washL, 0.0, 1.0))]
    img = np.concatenate(panels, axis=1)
    FL.write(path, np.repeat(img[..., None], 3, axis=-1))


# ---------------------------------------------------------------- the house


def main():
    a = MK.args()
    gen, cache = os.path.abspath(a["gen"]), os.path.abspath(a["cache"])
    meta = json.load(open(os.path.join(gen, "house.json")))
    P = json.load(open(os.path.join(FL.ROOT, "blender", "parts", "finish", "finish.json")))
    S = json.load(open(os.path.join(HERE, "paint.json")))
    St = json.load(open(os.path.join(HERE, "street.json")))
    paints = json.load(open(os.path.join(FL.ROOT, St["paints"])))
    W = json.load(open(os.path.join(FL.ROOT, St["eras"][meta["era"]])))
    Q = P["painted"]
    A = S["wear"]
    bake = json.load(open(os.path.join(cache, "bake.json")))
    out = os.path.join(cache, "out")
    pg = SM.Page(cache, meta, bake["mats"])
    pad = meta["page"]["padPx"]
    board = FP.boarding(Q, a.get("boarding"))
    cap_t = W["casing"]["capMm"] / 1000.0 * W["push"]["capThick"]
    T = Q["tongue"]

    # every material's paint value: the corner's, the boarding's kept variant, and paint.json's for the rest
    extra = {k: v for k, v in S["materials"].items() if k != "describes"}
    mats = dict(Q["materials"], sheet=board["sheet"], batten=board["batten"])
    mats.update({k: (dict(mats[v]) if isinstance(v, str) else v) for k, v in extra.items()})

    pl, sn, dl, gr = (np.zeros(pg.shape) for _ in range(4))
    wash, far = np.zeros(pg.shape), np.zeros(pg.shape)
    walls = {w["i"]: w for w in meta["walls"]}
    views = {i: SM.View(pg, pg.wall == i, w) for i, w in walls.items()}
    wsev = {i: severity(meta, paints, A, w) for i, w in walls.items()}
    roofs = {r["wall"]: r for r in meta["features"]["roof"]}
    log = []

    # each opening on its own wall, the other openings' pieces left out of its view
    ops = []
    for k, o in enumerate(meta["openings"]):
        wall = walls[o["wall"]]
        mine = [pc["i"] for pc in meta["pieces"] if pc["kind"] == f"open{k}"]
        others = [pc["i"] for pc in meta["pieces"] if pc["kind"].startswith("open") and pc["kind"] != f"open{k}"]
        v = SM.View(pg, (pg.wall == wall["i"]) & ~np.isin(pg.piece, others), wall)
        om = opening_meta(meta, o, k, wall, cap_t)
        side = leak_side(o, wall, paints, A)
        s = severity(meta, paints, A, wall, o.get("tilt", 0.0))
        door = "sill" not in o
        ops.append((k, o, wall, v, om, side, s, door, mine))
        log.append(f"open{k} w{wall['i']} {o['kind']} {s:.2f}{'+' if side > 0 else '-'}")

    # the failed paint: each opening's runs, its tongue and its casing's peel by its severity; each wall's tops,
    # its gutter's leaks and its plinth's wet margin
    for k, o, wall, v, om, side, s, door, mine in ops:
        q = graded(Q, s, A, om, door)
        if s >= A["from"]["runoff"]:
            pt, ws, fr, st = runoff(v, q["tongue"], om, sources(q["tongue"]["runoff"], om, side, door))
            if s >= A["from"]["tongue"]:
                tp, tw = FP.tongue(v, q, om, side)
                pt = np.maximum(pt, tp)
                ws = np.maximum(ws, tw)
            v.put(pl, pt)
            v.put(wash, ws)
            v.put(far, fr)
            v.put(sn, st)
        if s >= A["from"]["peel"]:
            v.put(pl, peel_casing(v, q, om, side))
        v.put(sn, opening_stains(v, Q, om, side))
    broads = {}
    for i, v in views.items():
        wall = walls[i]
        vm = {"world": meta["world"], "house": meta["house"], "wall": i, "courses": meta["courses"][str(wall["group"])],
              "features": {"joints": [("street", a_, zb, zt) for w_, a_, zb, zt in meta["features"]["joints"] if w_ == i]}}
        if wsev[i] >= A["from"]["peel"]:
            v.put(pl, peel_tops(v, Q, key(meta, "p-tops", i)))
        broads[i] = splash(v, Q, P, S, wall, meta)
        plinth = (v.m["stone"] | v.m["concrete"]) & v.vertical
        v.put(sn, wet_margin(v, Q, vm, broads[i], plinth))
        for di, (_, x, flow, kind) in enumerate(d for d in meta["features"]["drips"] if d[0] == i):
            if kind == "gutter":
                G = dict(S["gutter"], strength=S["gutter"]["strength"] * flow)
                vm_d = dict(vm, house=f"{meta['house']}/w{i}/drip{di}")
                pt, ws, fr, st = runoff(v, T, vm_d, [(G, x, meta["heights"]["top"])])
                v.put(pl, pt)
                v.put(wash, ws)
                v.put(far, fr)
                v.put(sn, st)
            else:
                Sh = S["shoe"]
                zf = meta["heights"]["drip"][0]
                on = (v.m["cladding"] | v.m["trims"]) & v.vertical
                ws = Sh["L"] * flow * MK.gauss(v.along - x, Sh["width"]) * (1.0 - FL.smoothstep(zf, zf + Sh["top"], v.z))
                v.put(wash, np.where(on, ws, 0.0))
    painted = pg.m["cladding"] | pg.m["trims"]
    pl = np.where(painted, pl, 0.0)

    # the values: broad washes first, each wall's and each opening's; then the contact shade; then the darks at
    # every junction, from what the paint is there; then the small
    lows = {}
    for i, v in views.items():
        wall = walls[i]
        lean = wall["kind"] == "lean"
        zf = meta["courses"]["1"][0] if lean else meta["heights"]["drip"][1]
        z_pl = zf if lean else meta["heights"]["plinth"]
        d, top, low = wall_values(v, Q, zf, z_pl, broads[i])
        v.put(dl, d, "add")
        lows[i] = (zf, top, low)
    for k, o, wall, v, om, side, s, door, mine in ops:
        v.put(dl, opening_values(v, Q, om, side, board), "add")
    dl += np.where((pg.m["trims"] | pg.m["stone"] | pg.m["batten"]) & pg.up, Q["up"]["L"], 0.0)
    C = Q["contact"]
    own = np.ones(pg.shape)
    for name, m in mats.items():
        if name in pg.m:
            own = np.where(pg.m[name], m.get("contact", 1.0), own)
    dl -= own * (C["L"] * FL.smoothstep(C["ao"][0], C["ao"][1], 1.0 - pg.ao)
                 + C["cavL"] * FL.smoothstep(C["cav"][0], C["cav"][1], np.clip(1.0 - pg.cav, 0.0, 1.0)))
    base = np.zeros(pg.shape)
    for name, m in mats.items():
        if name in pg.m:
            base = np.where(pg.m[name], m["L"] - m.get("stainDL", 0.0) * (sn > 0.5), base)
    J = Q["junction"]
    for i, v in views.items():
        wall = (v.m["cladding"] | v.m["trims"]) & v.vertical
        down(v, dl, base, wall, lows[i][1] - v.z, J["eave"])
    for k, o, wall, v, om, side, s, door, mine in ops:
        opening_junctions(v, Q, om, dl, base, [i for i in mine if meta["pieces"][i]["mat"] == "batten"])
    for i, v in views.items():
        lean = walls[i]["kind"] == "lean"
        zf = lows[i][0]
        clad = v.m["cladding"] & v.vertical
        plinth = (v.m["stone"] | v.m["concrete"]) & v.vertical
        down(v, dl, base, clad, v.z - zf, J["drip"])
        down(v, dl, base, plinth, (zf if lean else meta["heights"]["drip"][0]) - v.z, J["plinth"])
        down(v, dl, base, plinth, v.z, J["ground"])
    for k, o, wall, v, om, side, s, door, mine in ops:
        v.put(dl, opening_small(v, Q, om), "add")
    for i, v in views.items():
        v.put(dl, joint_lines(v, S, meta, walls[i]) + tile_values(v, Q, meta, roofs.get(i)), "add")
    loose = SM.View(pg, pg.wall == -1, walls[0])
    loose.put(dl, tile_values(loose, Q, meta, None), "add")
    for i, v in views.items():
        sills = [om["features"]["sill"] for k, o, wall, ov, om, side, s, door, mine in ops if wall["i"] == i and not door]
        v.put(gr, grime(v, Q, lows[i][2], sills))

    rng = Q["dlRange"]
    hist = np.stack([pl, 0.5 + np.clip(dl, -rng, rng) / (2.0 * rng), sn, gr], axis=-1)
    FL.write(os.path.join(out, "hist-p.png"), FL.dilate(np.where(pg.cov[..., None], hist, 0), pg.cov, pad + 2))
    h2 = np.stack([np.clip(wash / T["washL"], 0.0, 1.0), np.clip(far / T["washL"], 0.0, 1.0), np.zeros(pg.shape)], axis=-1)
    FL.write(os.path.join(out, "hist-p2.png"), FL.dilate(np.where(pg.cov[..., None], h2, 0), pg.cov, pad + 2))
    FL.write(os.path.join(out, "paint-stroke.png"), FP.strokes(Q, meta))
    FL.write(os.path.join(out, "geo.png"), SM.geo(pg, P, meta))
    FL.write(os.path.join(out, "street-normal.png"), SM.street_normal(pg, meta))

    # the digest, as the corner's; way Pc's paint is the house's own (paints.json), laid on the clay's values
    wp, tp_ = house_paint(meta, paints)
    Qc = copy.deepcopy(Q)
    cm = Qc["colour"]["mats"]
    cm["cladding"]["paint"] = [wp["C"], wp["h"]]
    cm["trims"]["paint"] = [tp_["C"], tp_["h"]]
    for k, v in extra.items():
        cm[k] = dict(cm[v]) if isinstance(v, str) else S["colour"].get(k, {})
    E, L = Q["edge"], Q["lap"]
    sh = P["marks"]["shade"]
    M = P["materials"]
    digest = {
        "mats": [{"name": k, "painted": 1 if M.get(k, {}).get("painted") else 0, "L": v["L"], "bareL": v.get("bareL", v["L"]),
                  "underL": v.get("underL", v["L"]), "stainDL": v.get("stainDL", 0.0), "smooth": v["smooth"],
                  "stainSmooth": v.get("stainSmooth", v["smooth"]), "brushL": v.get("brushL", 0.0), "flatUp": v.get("flatUp", 0.0),
                  "stainEdge": v.get("stainEdge", 1.0), "ao": v.get("ao", Q["aoStrength"]), "shadowLift": v.get("shadowLift", 0.0)}
                 for k, v in mats.items()],
        "lights": [dict(v, light=k) for k, v in Q["light"].items()],
        "strokeScale": meta["page"]["size"] / meta["page"]["pxPerM"] / Q["stroke"]["metres"],
        "edgeAmp": E["amp"], "strokeFade": E["fadeLod"], "brushFade": Q["brush"]["fadeLod"], "brushFar": Q["brush"]["far"],
        "dragL": Q["drag"]["L"], "dragScale": Q["drag"]["scale"], "dlRange": Q["dlRange"], "rimL": E["rimL"],
        "rimW": E["rimW"], "rimFar": E["rimFar"], "rimBreak": E["rimBreak"], "bareShift": E["bareShift"],
        "washL": T["washL"], "bareWash": T["bareWash"], "washFade": T["runoff"]["far"]["lod"] if T.get("runoff", {}).get("use") else [0, 0],
        "aoStrength": Q["aoStrength"], "lapDark": L["occlusion"], "lapCore": L["occCoreMm"] / 1000.0,
        "lapReach": L["occReachMm"] / 1000.0, "lapGrimeL": L["grimeL"], "lapGrimeReach": L["reach"],
        "lapGrimeBreak": L["break"], "lapPage": sh["lapPageMm"] / 1000.0,
        "colour": FP.colours(P, Qc, mats),
    }
    json.dump(digest, open(os.path.join(out, "paint.json"), "w"), indent=1)
    preview(os.path.join(FL.ROOT, "cache", "street", "paint-preview", f"{meta['house']}.png"), pl, dl, wash, rng, T["washL"])
    share = lambda m: float((m & pg.cov).sum()) / max(1, int((painted & pg.cov).sum()))  # noqa: E731
    print(f"[paint] severity by wall {', '.join(f'w{i} {s:.2f}' for i, s in wsev.items())}; {'; '.join(log)}")
    print(f"[paint] boarding {a.get('boarding') or Q['boarding']['use']}; peeled {share(painted & (pl > 0.5)):.3f} of the paint; "
          f"stained {share(sn > 0.5):.3f}; dL {np.percentile(dl[pg.cov], [1, 5, 50, 95]).round(1)}, "
          f"beyond {rng}: {float((np.abs(dl[pg.cov]) > rng).mean()):.4f}; wrote {out}")


if __name__ == "__main__":
    main()
