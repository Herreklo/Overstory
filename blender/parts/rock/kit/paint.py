"""Way P's page for a rock part: the street's paint (blender/parts/street/paint.py) on a rock's page, p3's rules
(finish.json `painted`) unchanged.

    Blender -b --factory-startup -P blender/parts/rock/kit/paint.py -- --gen cache/rock/kit/gen/slab-block --cache cache/rock/kit/bake/slab-block

Reads house.json (part.py) and the bakes (bake.py), and writes into <cache>/out what way P reads, as the street's:
hist-p.png, hist-p2.png, paint-stroke.png, paint.json, geo.png, street-normal.png.

A rock is bare stone standing in the ground, so it takes what the house's stone plinth takes and nothing a paint
takes: darker toward the ground (`plinth`), its foot's wet margin with no splash (no eave sheds onto it; `wet`),
the contact shade (`contact`), and the ground's junction dark (`junction.ground`).
No peel, no washes, no lap. Its value is kit.json's material (p3's stone at the phyllite's L*), its hue kit.json's.
"""

import copy
import importlib.util
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
STREET = os.path.join(ROOT, "blender", "parts", "street")
FINISH = os.path.join(ROOT, "blender", "parts", "finish")
sys.path.insert(0, FINISH)
import finishlib as FL  # noqa: E402
from finishlib import HS  # noqa: E402


def module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


FP = module(os.path.join(FINISH, "paint.py"), "finish_paint")
MK = FP.MK
SM = module(os.path.join(STREET, "marks.py"), "street_marks")
SP = module(os.path.join(STREET, "paint.py"), "street_paint")  # its digest and junction, called as they are
key, field = MK.key, FP.field


def wave2(pg, k, cell):
    """The corner's seeded low wave, -1..1, of `cell` metres, over the ground plan: a rock has no wall to run along."""
    return 2.0 * FL.noise2(pg.x / cell, pg.y / cell, k) - 1.0


def main():
    a = MK.args()
    gen, cache = os.path.abspath(a["gen"]), os.path.abspath(a["cache"])
    meta = json.load(open(os.path.join(gen, "house.json")))
    meta.setdefault("walls", [])
    P = json.load(open(os.path.join(FINISH, "finish.json")))
    K = json.load(open(os.path.join(HERE, "kit.json")))
    Q = P["painted"]
    bake = json.load(open(os.path.join(cache, "bake.json")))
    out = os.path.join(cache, "out")
    os.makedirs(out, exist_ok=True)
    pg = SM.Page(cache, meta, bake["mats"])
    pad = meta["page"]["padPx"]
    T = Q["tongue"]

    mats = {k: dict(Q["materials"][v["like"]], **{f: x for f, x in v.items() if f not in ("like", "describes")})
            for k, v in K["materials"].items() if k != "describes"}
    rock = np.zeros(pg.shape, bool)
    for k in mats:
        rock |= pg.m[k]
    top = float(pg.z[pg.cov].max())

    # the stain: the foot's wet margin, its top a wavering found edge; no eave sheds onto a rock, so no splash swells it
    Wt = Q["wet"]
    wet_top = Wt["top"] + Wt["wobble"]["amp"] * wave2(pg, key(meta, "p-wet", 0), Wt["wobble"]["cell"])
    sn = np.where(rock, field(wet_top - pg.z, Wt["soft"]), 0.0)

    # the values: darker toward the ground, the contact shade, then the ground's junction dark from what is there
    dl = np.zeros(pg.shape)
    dl -= np.where(rock, Q["plinth"]["L"] * (1.0 - np.clip(pg.z / top, 0.0, 1.0)), 0.0)
    dl += np.where(rock & pg.up, Q["up"]["L"], 0.0)
    C = Q["contact"]
    own = np.ones(pg.shape)
    for name, m in mats.items():
        own = np.where(pg.m[name], m.get("contact", 1.0), own)
    dl -= own * (C["L"] * FL.smoothstep(C["ao"][0], C["ao"][1], 1.0 - pg.ao)
                 + C["cavL"] * FL.smoothstep(C["cav"][0], C["cav"][1], np.clip(1.0 - pg.cav, 0.0, 1.0)))
    base = np.zeros(pg.shape)
    for name, m in mats.items():
        base = np.where(pg.m[name], m["L"] - m.get("stainDL", 0.0) * (sn > 0.5), base)
    whole = SM.View(pg, pg.cov, {"origin": [0, 0], "dir": [1, 0], "out": [0, -1], "kind": "rock"})
    SP.down(whole, dl, base, whole.get(rock), whole.z, Q["junction"]["ground"])

    rng = Q["dlRange"]
    zero = np.zeros(pg.shape)
    hist = np.stack([zero, 0.5 + np.clip(dl, -rng, rng) / (2.0 * rng), sn, zero], axis=-1)
    FL.write(os.path.join(out, "hist-p.png"), FL.dilate(np.where(pg.cov[..., None], hist, 0), pg.cov, pad + 2))
    FL.write(os.path.join(out, "hist-p2.png"), FL.dilate(np.zeros(pg.shape + (3,)), pg.cov, pad + 2))
    FL.write(os.path.join(out, "paint-stroke.png"), FP.strokes(Q, meta))
    FL.write(os.path.join(out, "geo.png"), SM.geo(pg, P, meta))
    FL.write(os.path.join(out, "street-normal.png"), SM.street_normal(pg, meta))

    # the digest, as the street's; its colours kit.json's, laid on the clay's values
    Qc = copy.deepcopy(Q)
    cm = Qc["colour"]["mats"]
    for k, v in K["materials"].items():
        if k != "describes":
            cm[k] = dict(cm.get(v["like"], {}), **K["colour"].get(k, {}))
    E, L = Q["edge"], Q["lap"]
    sh = P["marks"]["shade"]
    digest = {
        "mats": [{"name": k, "painted": 0, "L": v["L"], "bareL": v.get("bareL", v["L"]),
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
    c = pg.cov & rock
    print(f"[paint] {meta['part']}: stained {float((sn[c] > 0.5).mean()):.3f}; "
          f"dL {np.percentile(dl[c], [1, 5, 50, 95]).round(1)}, beyond {rng}: {float((np.abs(dl[c]) > rng).mean()):.4f}; wrote {out}")


if __name__ == "__main__":
    main()
