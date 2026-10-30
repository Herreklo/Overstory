"""Way P's page for a rock part: the street's paint (blender/parts/street/paint.py) on a rock's page, p3's rules
(finish.json `painted`) unchanged.

    Blender -b --factory-startup -P blender/parts/rock/kit/paint.py -- --gen cache/rock/kit/gen/slab-block --cache cache/rock/kit/bake/slab-block

Reads house.json (part.py) and the bakes (bake.py), and writes into <cache>/out what way P reads, as the street's:
hist-p.png, hist-p2.png, paint-stroke.png, paint.json, geo.png, street-normal.png, and for a sculpted part (bake.py's
high-poly bake) near-normal.png.

A rock is bare stone standing in the turf, its page its own (kit.json `skin`), not the house plinth's: a calm base of
its material's value under one broad, soft variation; the turf's damp a little darker over its foot, with no wet band
(no eave splashes a rock); the contact shade (finish.json `contact`); its cavities dark by the cavity bake; a crack or
two drawn as a painter draws them, a dark line with a lighter lip along a joint's trace across a whole face, never
ending inside one; the lichen as its material's stain, a few colonies set on its biggest up- and sea-facing old faces,
clear of their edges; and the ground's junction dark (`junction.ground`). Values per plane are the light's, never the
page's. No peel, no washes, no lap. Its value and hue are its material's (the part's own, kit.json `materials` and
`colour`).
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
    MS_skewed = lambda st_, lo, hi, k: lo + (hi - lo) * st_.random() ** int(k)  # noqa: E731  (mass.py's skewed)
    MS_unit = lambda toward, slope=90.0: np.array([np.sin(np.radians(toward)) * np.sin(np.radians(slope)),  # noqa: E731
                                                   np.cos(np.radians(toward)) * np.sin(np.radians(slope)), np.cos(np.radians(slope))])

    # the designed faces: each texel's the plane its normal is nearest; each plane's offset where it lies flat; a
    # texel's distance in its plane to the face's edge, the nearest line another plane (or the turf) cuts it along
    X = next(x for x in K["mass"]["masses"] if x["id"] == meta["part"])
    keys = [k for k, f in meta.get("faces", {}).items() if "n" in f]
    N = np.array([meta["faces"][k]["n"] for k in keys]); wear = [meta["faces"][k]["wear"] for k in keys]
    face = np.where(rock, np.argmax(pg.n @ N.T, -1), -1)
    D = np.array([np.median((pg.p[(face == i) & (pg.n @ N[i] > 0.999)] @ N[i])) if ((face == i) & (pg.n @ N[i] > 0.999)).any()
                  else np.max(pg.p[face == i] @ N[i], initial=0.0) for i in range(len(N))])

    def edge(i, Pf):
        out = Pf[:, 2] / max(np.sqrt(1.0 - N[i][2] ** 2), 1e-3)
        for j in range(len(N)):
            s2 = 1.0 - float(N[i] @ N[j]) ** 2
            if j != i and s2 > 1e-3:
                out = np.minimum(out, (D[j] - Pf @ N[j]) / np.sqrt(s2))
        return out

    st = lambda *k: HS.Stream(meta["world"], "rock", meta["part"], "paint", *k)  # noqa: E731
    count = lambda i: int((face == i).sum())  # noqa: E731

    # the lichen: colonies on the biggest old faces that look up or out to sea, each a cluster of round spots (a few
    # big, many small) thickest at its middle, which is clear of the face's edges; none on a face looking down
    Li = Sk["lichen"]; up = pg.n[..., 2]; sea = MS_unit(Li["seaToward"])
    old = [i for i in range(len(N)) if wear[i] not in K["sculpt"]["fresh"] and (N[i][2] >= Li["up"] or N[i] @ sea >= Li["sea"])]
    chosen = sorted(old, key=lambda i: -count(i) * max(N[i][2], N[i] @ sea))[:Li["faces"]]
    sn = np.zeros(pg.shape); rs = st("lichen"); col = 0
    for i in chosen:
        Pf = pg.p[face == i]; dist = edge(i, Pf)
        a = np.cross(N[i], [0.0, 0.0, 1.0] if abs(N[i][2]) < 0.9 else [1.0, 0.0, 0.0]); a /= np.linalg.norm(a); b = np.cross(N[i], a)
        for _ in range(rs.randint(*Li["colonies"])):
            R = rs.uniform(*Li["rM"]); ok = np.nonzero(dist >= Li["clearM"] + R)[0]
            if not len(ok):
                continue
            c = Pf[ok[rs.randint(0, len(ok) - 1)]]; col += 1; sd = np.full(pg.shape, -1.0)
            for _ in range(rs.randint(*Li["spots"])):
                t = rs.uniform(0, 2 * np.pi); q = c + R * rs.random() ** Li["fall"] * (np.cos(t) * a + np.sin(t) * b)
                sd = np.maximum(sd, MS_skewed(rs, *Li["spotRM"], Li["skew"]) - np.linalg.norm(pg.p - q, axis=-1))
            sn = np.maximum(sn, field(sd, Li["soft"]))
    sn = np.where(rock & (up > Li["under"]), sn, 0.0)

    # the values: the broad variation, the turf's damp over the foot, the contact shade, the cavities dark, the drawn
    # crack, then the ground's junction dark from what is there
    dl = np.zeros(pg.shape)
    Br, Fo, Cv = Sk["broad"], Sk["foot"], Sk["cavity"]
    dl += np.where(rock, Br["L"] * (2.0 * FL.fbm3(pg.p, key(meta, "p-broad"), Br["cellM"], Br["octaves"]) - 1.0), 0.0)
    dl -= np.where(rock, Fo["L"] * (1.0 - FL.smoothstep(0.0, Fo["m"], pg.z)), 0.0)
    C = Q["contact"]
    own = np.ones(pg.shape)
    for name, m in mats.items():
        own = np.where(pg.m[name], m.get("contact", 1.0), own)
    dl -= own * C["L"] * FL.smoothstep(C["ao"][0], C["ao"][1], 1.0 - pg.ao)
    dl -= np.where(rock, Cv["L"] * FL.smoothstep(Cv["cav"][0], Cv["cav"][1], np.clip(1.0 - pg.cav, 0.0, 1.0)), 0.0)

    # the crack: the joint's trace across the biggest side facing the mass's front, at a seeded offset from its middle,
    # carried over onto the face its upper end runs into (`faces`); drawn on those faces' texels only, so it ends
    # where the planes change
    Cr = Sk["crack"]
    jn = next(j for j in X["structure"]["joints"] if j["name"] == Cr["set"]); nj = MS_unit(jn["dipToward"], jn["dip"])
    front = MS_unit(X["front"])
    sides = [i for i in range(len(N)) if N[i] @ front >= Cr["front"] and abs(N[i][2]) <= 0.6]
    if sides and Cr["faces"]:
        A = max(sides, key=count); PA = pg.p[face == A]; t = PA @ nj; rc = st("crack")
        x = float(np.median(t)) + Cr["offset"] * float(np.ptp(t)) * rc.uniform(-1.0, 1.0); side = 1.0 if rc.random() < 0.5 else -1.0
        L_, amp = Cr["wander"]
        sj = pg.p @ nj - x + amp * (2.0 * FL.fbm3(pg.p, key(meta, "p-crack"), L_, 2) - 1.0)
        on = face == A; w = Cr["widthM"] / 2
        for _ in range(Cr["faces"] - 1):
            tr = rock & (np.abs(sj) < w) & ~on; ta = pg.p[on & (np.abs(sj) < w)]
            best, bz = -1, -1e9
            for j in np.unique(face[tr]):
                pj = pg.p[tr & (face == j)]
                near = np.min(np.linalg.norm(pj[::max(1, len(pj) // 400), None] - ta[None, ::max(1, len(ta) // 400)], axis=-1))
                if near < Cr["near"] and pj[:, 2].mean() > bz and N[j][2] > N[A][2]:
                    best, bz = j, pj[:, 2].mean()
            if best < 0:
                break
            on |= face == best
        lip = Cr["lipM"] / 2
        dl += np.where(on, -Cr["L"] * field(w - np.abs(sj), Cr["soft"]) + Cr["lipL"] * field(lip - np.abs(side * sj - w - lip), Cr["soft"]), 0.0)

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
    print(f"[paint] {meta['part']}: lichen {float((sn[c] > 0.5).mean()):.3f} in {col} colonies on {[keys[i] for i in chosen]}; "
          f"dL {np.percentile(dl[c], [1, 5, 50, 95]).round(1)}, beyond {rng}: {float((np.abs(dl[c]) > rng).mean()):.4f}; wrote {out}")


if __name__ == "__main__":
    main()
