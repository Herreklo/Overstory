"""Way P's page for a rock part: the street's paint (blender/parts/street/paint.py) on a rock's page, p3's rules
(finish.json `painted`) unchanged.

    Blender -b --factory-startup -P blender/parts/rock/kit/paint.py -- --gen cache/rock/kit/gen/slab-block --cache cache/rock/kit/bake/slab-block

Reads house.json (part.py) and the bakes (bake.py), and writes into <cache>/out what way P reads, as the street's:
hist-p.png, hist-p2.png, paint-stroke.png, paint.json, geo.png, street-normal.png, and for a sculpted part (bake.py's
high-poly bake) near-normal.png.

A rock is bare stone standing in the turf, its page its own (kit.json `skin`), not the house plinth's: the turf's damp
a little darker over its foot, with no wet band (no eave splashes a rock); the contact shade (finish.json `contact`); its
cracks dark by the cavity bake; its rounds lighter by their arris; the lichen as its material's stain, patches on its
old faces, more on a top than a side, none under its girth nor on a fresh break; and the ground's junction dark
(`junction.ground`). No peel, no washes, no lap. Its value and hue are its material's (the part's own, kit.json
`materials` and `colour`).
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

    mats = {k: dict(Q["materials"][K["materials"][k]["like"]],
                    **{f: x for f, x in K["materials"][k].items() if f not in ("like", "describes", "_")})
            for k in bake["mats"]}
    rock = np.zeros(pg.shape, bool)
    for k in mats:
        rock |= pg.m[k]
    Sk = K["skin"]

    # the face each texel lies on: the designed plane its normal is nearest; a fresh break has had no time for lichen
    faces = [(np.array(f["n"]), f["wear"]) for f in meta.get("faces", {}).values() if "n" in f]
    fresh = np.zeros(pg.shape, bool)
    if faces:
        near = np.argmax(np.stack([pg.n @ n for n, _ in faces], -1), -1)
        fresh = rock & np.isin(near, [i for i, (_, w) in enumerate(faces) if w in K["sculpt"]["fresh"]])

    # the stain: the lichen, seeded patches covering a share of each face by how far up it looks
    Li = Sk["lichen"]
    up = pg.n[..., 2]
    share = Li["share"][0] + (Li["share"][1] - Li["share"][0]) * FL.smoothstep(Li["up"][0], Li["up"][1], up)
    share = np.where((up < Li["under"]) | fresh, 0.0, share)
    big = FL.fbm3(pg.p, key(meta, "p-lichen", 0), Li["cellM"][0], Li["octaves"])
    spots = FL.fbm3(pg.p, key(meta, "p-lichen", 1), Li["cellM"][1], Li["octaves"])
    pat = FL.equalise((1.0 - Li["mix"]) * big + Li["mix"] * spots, rock)
    sn = np.where(rock, field(pat - (1.0 - share), Li["soft"]), 0.0)

    # the values: the turf's damp over the foot, the contact shade, the cracks dark, the rounds light, then the
    # ground's junction dark from what is there
    dl = np.zeros(pg.shape)
    Fo, Cr, Ar = Sk["foot"], Sk["crack"], Sk["arris"]
    dl -= np.where(rock, Fo["L"] * (1.0 - FL.smoothstep(0.0, Fo["m"], pg.z)), 0.0)
    C = Q["contact"]
    own = np.ones(pg.shape)
    for name, m in mats.items():
        own = np.where(pg.m[name], m.get("contact", 1.0), own)
    dl -= own * C["L"] * FL.smoothstep(C["ao"][0], C["ao"][1], 1.0 - pg.ao)
    dl -= np.where(rock, Cr["L"] * FL.smoothstep(Cr["cav"][0], Cr["cav"][1], np.clip(1.0 - pg.cav, 0.0, 1.0)), 0.0)
    dl += np.where(rock, Ar["L"] * FL.smoothstep(Ar["at"][0], Ar["at"][1], pg.arris), 0.0)
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
    if bake.get("high"):  # a sculpted part: the near level's own normal from the high-poly, beside the street level's
        nn = FL.read(os.path.join(cache, "near-normal.exr"))
        FL.write(os.path.join(out, "near-normal.png"), FL.dilate(nn[..., :3], nn[..., 3] > 0.5, pad + 2))

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
    print(f"[paint] {meta['part']}: lichen {float((sn[c] > 0.5).mean()):.3f} (fresh {float(fresh[c].mean()):.3f}); "
          f"dL {np.percentile(dl[c], [1, 5, 50, 95]).round(1)}, beyond {rng}: {float((np.abs(dl[c]) > rng).mean()):.4f}; wrote {out}")


if __name__ == "__main__":
    main()
