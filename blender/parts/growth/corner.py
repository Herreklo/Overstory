"""The walked corner's growth as the painted corner draws it (Code/Editor/Corner/LT1CornerGrowth.cs): the tufts' meshes
(tufts.py), where they stand (growth.place_tufts, from the record and fixtures/lt1-corner-growth.json), the painted
layer's values as globals (packs/<pack>/growth.json, painted) and the knuckle's stand-in rules (rock), in one file the
element reads: cache/growth/corner/growth.json, rebuilt, not tracked (its hashes in blender/parts/growth/corner.manifest.json).

It prints the budgets (tufts a square metre by habitat, triangles a tuft by level, the corner's tufts and triangles at
their nearest and as the street camera draws them) and fails over any of them.

    $PY blender/parts/growth/corner.py           make and check
    $PY blender/parts/growth/corner.py --check   check what is made
"""

import argparse
import hashlib
import json
import math
import os
import sys

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, os.path.join(ROOT, "blender", "resolver"))
sys.path.insert(0, os.path.join(ROOT, "blender", "generators"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import growth  # noqa: E402
import tufts as TU  # noqa: E402

OUT = os.path.join(ROOT, "cache", "growth", "corner")
MESHES = os.path.join(ROOT, "cache", "growth", "tufts")
STREET = os.path.join(ROOT, "unity", "Assets", "Art", "Buildings", "corner-strong", "street.json")
HOUSES = os.path.join(ROOT, "cache", "houses", "houses.json")
FIXTURE = os.path.join(ROOT, "fixtures", "lt1-corner.json")
WHERE = os.path.join(ROOT, "fixtures", "lt1-corner-growth.json")
MANIFEST = os.path.join(os.path.dirname(os.path.abspath(__file__)), "corner.manifest.json")
# the street camera (Paint.json's view "street", street metres): where the drawn budget is measured from
STREET_EYE = (49.3, 12.0, 5.6)


def srgb_to_linear(h):
    c = np.array([int(h.lstrip("#")[i:i + 2], 16) / 255.0 for i in (0, 2, 4)])
    return [round(float(x), 5) for x in np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)]


def ground_of(street):
    f = street["town"]["fine"]
    z = np.array(f["z"], float).reshape(f["ny"], f["nx"])

    def at(x, y):
        gx, gy = (x - f["x0"]) / f["step"], (y - f["y0"]) / f["step"]
        ix, iy = int(np.clip(math.floor(gx), 0, f["nx"] - 2)), int(np.clip(math.floor(gy), 0, f["ny"] - 2))
        fx, fy = float(np.clip(gx - ix, 0, 1)), float(np.clip(gy - iy, 0, 1))
        return (z[iy, ix] * (1 - fx) + z[iy, ix + 1] * fx) * (1 - fy) + (z[iy + 1, ix] * (1 - fx) + z[iy + 1, ix + 1] * fx) * fy
    return at


def fact(fixture, what, where_has):
    for g in fixture["ground_history"]:
        if g["what"] == what and where_has in g["where"]:
            return g
    raise KeyError(f"ground_history has no {what} at {where_has}")


def globals_of(painted):
    L, M = painted["lichen"], painted["moss"]
    return [
        {"name": "_GP_Lichen", "v": L["ratio"] + [L["shareMax"]]},
        {"name": "_GP_LichenShape", "v": [L["spacing"][0], L["spacing"][1], L["lobe"][0], L["lobe"][1]]},
        {"name": "_GP_LichenSoft", "v": [L["soft"], L["cluster"][0], L["fullYears"] / 200.0, L["cluster"][1]]},
        {"name": "_GP_Moss", "v": M["ratio"] + [M["patch"]]},
        {"name": "_GP_MossSoft", "v": [M["soft"], L["smallShare"], 0.0, 0.0]},
        {"name": "_GP_LichenFar", "v": [L["softFar"], L["outline"][0], L["outline"][1], L["cluster"][2]]},
    ]


def make(variants=4):
    P = growth.pack()
    T = P["tufts"]
    fixture = json.load(open(FIXTURE))
    street = json.load(open(STREET))
    houses = json.load(open(HOUSES))
    where = json.load(open(WHERE))
    date = float(houses["date"])
    seed = fixture["worldSeed"]
    ground = ground_of(street)

    # the meshes: every species' variants at every level
    os.makedirs(MESHES, exist_ok=True)
    meshes = {}
    for name, spec in T["species"].items():
        for v in range(variants):
            tuft = TU.blades(spec, name, v, seed)
            files = []
            for level in range(len(T["levels"])):
                fn = f"{name}-{v}-L{level}.bin"
                tris = TU.mesh(tuft, spec, level)
                TU.write_r2b(os.path.join(MESHES, fn), tris)
                files.append({"file": fn, "tris": len(tris)})
            meshes[(name, v)] = {"H": tuft["H"], "R": tuft["R"], "levels": files}

    # where they stand
    footprints = [[(h["fp"][i], h["fp"][i + 1]) for i in range(0, len(h["fp"]), 2)] for h in houses["houses"]]
    footprints += [[(c["x"], c["y"]) for c in f["corners"]] for f in street["town"]["foundations"]]
    steps = [[(p["x"], p["y"]) for p in s["points"]] for s in street["town"]["steps"]]
    rows, area = growth.place_tufts(where, ground, footprints, steps, fixture["heath_above"] / 1000.0, seed,
                                    variants=variants)

    habitats = list(T["habitats"])
    kinds = {}
    for sp, v, hab, x, y, z, turn, scale, lx, ly, rank, hue in rows:
        k = kinds.setdefault((sp, v), [])
        k += [x, y, z, turn, scale, lx, ly, rank, hue, habitats.index(hab)]
    look = T["look"]
    out_kinds = []
    for (sp, v), inst in sorted(kinds.items()):
        spec, m = T["species"][sp], meshes[(sp, v)]
        out_kinds.append({
            "species": sp, "variant": v,
            "levels": [os.path.relpath(os.path.join(MESHES, f["file"]), ROOT) for f in m["levels"]],
            "tris": [f["tris"] for f in m["levels"]],
            "height": round(m["H"], 3), "radius": round(max(m["H"], m["R"] * 1.6), 3),
            "base": srgb_to_linear(spec["base"]), "tip": srgb_to_linear(spec["tip"]),
            "seed": srgb_to_linear(spec.get("seed", spec["tip"])),
            "hue": spec["clumpHue"],
            "instances": inst,
        })
    lichen = fact(fixture, "lichen", "knuckle")
    R = P["rock"]
    out = {
        "_": "The corner's growth for the painted corner (blender/parts/growth/corner.py): rebuilt, not tracked.",
        "pack": houses["pack"], "date": date, "seed": seed,
        "globals": globals_of(P["painted"]),
        "standIn": {
            "fact": f"ground_history: lichen, {lichen['where']}, {lichen['year']}",
            "years": round(max(date - lichen["year"] - growth.LICHEN_DELAY, 0.0) / 200.0, 4),
            "rule": [R["overhang"], R["fullRain"], R["skyPower"]],
            "foot": [R["footLichen"][0], R["footLichen"][1], R["footMoss"][1]],
            "mossMax": R["footMossMax"], "mossOverLichen": R["mossOverLichen"],
        },
        "tufts": {
            "to": [l["to"] for l in T["levels"]], "fade": T["fade"],
            "thinFrom": T["thin"]["from"], "keepAt120": T["thin"]["keepAt120"], "widen": T["thin"]["widen"],
            "look": look, "habitats": habitats,
            "kinds": out_kinds,
        },
        "area": area,
    }
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, "growth.json")
    with open(path, "w") as f:
        json.dump(out, f, separators=(",", ":"))
    return out


def check(out):
    """The budgets, printed; returns the ones over."""
    T = growth.pack()["tufts"]
    B = T["budget"]
    over = []
    kinds = out["tufts"]["kinds"]
    to = out["tufts"]["to"]
    print("tris a tuft by level (budget " + " / ".join(map(str, B["trisPerTuft"])) + "):")
    by_species = {}
    for k in kinds:
        by_species.setdefault(k["species"], []).append(k["tris"])
    for sp, ts in sorted(by_species.items()):
        worst = [max(t[l] for t in ts) for l in range(len(to))]
        print(f"  {sp:11s} " + " / ".join(f"{w:3d}" for w in worst))
        for l, w in enumerate(worst):
            if w > B["trisPerTuft"][l]:
                over.append(f"{sp} L{l}: {w} tris > {B['trisPerTuft'][l]}")
    n_hab = {}
    total, tris0 = 0, 0
    drawn, tris_drawn = 0, 0
    eye = np.array(STREET_EYE)
    thin_from, keep_min = out["tufts"]["thinFrom"], out["tufts"]["keepAt120"]
    for k in kinds:
        I = np.array(k["instances"], float).reshape(-1, 10)
        total += len(I)
        tris0 += len(I) * k["tris"][0]
        for h in I[:, 9].astype(int):
            n_hab[h] = n_hab.get(h, 0) + 1
        d = np.linalg.norm(I[:, :3] - eye, axis=1)
        keep = np.where(d > thin_from, np.maximum(keep_min, thin_from / np.maximum(d, 1e-3)), 1.0)
        ok = (I[:, 7] < keep) & (d <= to[-1])
        level = np.searchsorted(np.array(to), d[ok])
        drawn += int(ok.sum())
        tris_drawn += int(sum(k["tris"][min(l, len(to) - 1)] for l in level))
    print("tufts a square metre (budget %.1f):" % B["tuftsPerSqm"])
    for h, name in enumerate(out["tufts"]["habitats"]):
        a = out["area"].get(name, 0.0)
        dens = n_hab.get(h, 0) / a if a > 0 else 0.0
        print(f"  {name:6s} {n_hab.get(h, 0):5d} tufts over {a:7.1f} m2: {dens:4.2f}")
        if dens > B["tuftsPerSqm"]:
            over.append(f"{name}: {dens:.2f} tufts a m2 > {B['tuftsPerSqm']}")
    print(f"the corner: {total} tufts, {tris0} tris at their nearest")
    print(f"from the street camera: {drawn} tufts drawn (budget {B['cornerTuftsDrawn']}), {tris_drawn} tris "
          f"(budget {B['cornerTris']})")
    if drawn > B["cornerTuftsDrawn"]:
        over.append(f"drawn {drawn} > {B['cornerTuftsDrawn']}")
    if tris_drawn > B["cornerTris"]:
        over.append(f"tris drawn {tris_drawn} > {B['cornerTris']}")
    return over


def manifest(out):
    path = os.path.join(OUT, "growth.json")
    files = {"cache/growth/corner/growth.json": hashlib.sha256(open(path, "rb").read()).hexdigest()[:16]}
    for k in out["tufts"]["kinds"]:
        for f in k["levels"]:
            files[f] = hashlib.sha256(open(os.path.join(ROOT, f), "rb").read()).hexdigest()[:16]
    with open(MANIFEST, "w") as f:
        json.dump({"_": "The hashes of what blender/parts/growth/corner.py makes (cache/growth/, not tracked).",
                   "files": dict(sorted(files.items()))}, f, indent=1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    if a.check:
        out = json.load(open(os.path.join(OUT, "growth.json")))
    else:
        out = make()
        manifest(out)
    over = check(out)
    if over:
        print("OVER BUDGET:", *over, sep="\n  ")
        sys.exit(1)
    print("within budget")


if __name__ == "__main__":
    main()
