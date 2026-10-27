"""The walked corner's timber houses, built from their facts and baked, for Unity (LT1Houses).

Each house is assembled by blender/parts/house/house.py from its plan (blender/blockouts/heart_layout.py's building:
footprint, base, eave, roof, pitch), its record (fixtures/lt1-corner.json: era, built, dated events), the pack's
timber workings (packs/stavanger-1989/timber.json) and the date. Writes cache/houses/<name>.bin (R2B2 soups, Unity's
frame) and cache/houses/houses.json (one row a house, for the houses buffer: its index, id, era, built, wealth, dated
events, its coats on the date (blender/parts/house/coats.py, by the pack's paint.json) and its roof's covering).

    /Applications/Blender.app/Contents/MacOS/Blender -b --factory-startup --python tools/houses.py -- \\
        [--houses C,D,E] [--out cache/houses] [--date 1989.8] [--pack packs/stavanger-1989] [--no-bake]
        [--tiers near,street,city]

Blender only for its ray tree (mathutils): nothing is made in a scene.
"""

import argparse
import json
import math
import os
import re
import sys
import time

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
for p in ("blender/resolver", "blender/blockouts", "blender/parts/house"):
    sys.path.insert(0, os.path.join(ROOT, p))

import numpy as np  # noqa: E402

import centre_land as L  # noqa: E402
import hashing as HS  # noqa: E402
import heart_layout as H  # noqa: E402
import coats as CO  # noqa: E402
import house as HO  # noqa: E402  (blender/parts/house, not the old generator)


def facts_of(record):
    """A fixture building's record as the house assembler reads it: its era, the year it was built, its wealth and
    its dated events, oldest first."""
    events = sorted(record["events"], key=lambda e: (e["year"], e["id"]))
    built = next(e for e in events if e["kind"] == "built")
    return dict(id=record["id"], era=built["params"]["era"], built=built["year"],
                wealth=built["params"].get("wealth", 0), storeys=built["params"].get("storeys", 1000),
                with_=built["params"].get("with", []), events=[e for e in events if e["kind"] != "built"])


def local_ground(b, pad=12.0, step=0.5):
    """The carved ground round a house, sampled as heart_build samples it."""
    xs = [b["ox"] + dx for dx in (-b["w"] - pad, b["w"] + pad, 0.0)]
    ys = [b["oy"] + dy for dy in (-b["d"] - pad, b["d"] + pad, 0.0)]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    X, Y = np.meshgrid(np.arange(x0, x1 + step / 2, step), np.arange(y0, y1 + step / 2, step), indexing="ij")
    Z = H.carve(X, Y, L.heights(X, Y))

    def ground(x, y):
        u = min(max((x - x0) / step, 0), X.shape[0] - 1.001)
        v = min(max((y - y0) / step, 0), X.shape[1] - 1.001)
        i, j = int(u), int(v)
        fu, fv = u - i, v - j
        a = Z[i, j] + (Z[i + 1, j] - Z[i, j]) * fu
        c = Z[i, j + 1] + (Z[i + 1, j + 1] - Z[i, j + 1]) * fu
        return float(a + (c - a) * fv)
    return ground


BOUNCE = 0.45  # the light a painted house's own faces send on: the mean albedo of its paint and wood in grey light


def bake_soup(soup, ground):
    """What each triangle sees (bake.py's rays and reach): its share of open sky, of open ground, and its openness
    close by. The house only knows itself; the ground is the carved ground's height under each sample. A ray that
    meets the house itself brings back one bounce: what the face it meets sees of sky and ground, times BOUNCE, so a
    rafter's side under a deep eave is lit by the boards round it, not black. A joint (the slot between stones drawn as
    one face, from the street tier) and the mortar behind the stones see past them: their shade is in the joint's share
    (lime-mortar.json, jointView and jointFar). A stone's facet sees one light, the mean of its triangles'."""
    import importlib.util
    from mathutils import Vector
    from mathutils.bvhtree import BVHTree
    spec = importlib.util.spec_from_file_location("bake", os.path.join(ROOT, "blender/generators/bake.py"))
    BK = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(BK)
    verts = [Vector(p) for p in soup.p]
    polys = [(i, i + 1, i + 2) for i in range(0, len(verts), 3)]
    tree = BVHTree.FromPolygons(verts, polys, epsilon=0.0)
    from soup import KINDS
    kinds = [int(soup.ch[3 * t][2]) for t in range(len(polys))]
    through = (KINDS["joint"], KINDS["mortar"])
    first, hits = [], []
    for t in range(len(polys)):
        a, b, c = verts[3 * t], verts[3 * t + 1], verts[3 * t + 2]
        n = (b - a).cross(c - a).normalized()
        u, w = BK._basis(n)
        centre = (a + b + c) / 3.0
        dirs = [u * x + w * y + n * z for x, y, z in BK._FAN]
        samples = [centre] + [q.lerp(centre, 0.5) for q in (a, b, c)]
        sky = gnd = near = 0
        met = []
        for s in samples:
            o = s + n * BK.LIFT
            h = o.z - ground(o.x, o.y)
            for d in dirs:
                hit, hn, face, dist = tree.ray_cast(o, d, BK.REACH)
                while hit is not None and kinds[t] in through and kinds[face] == KINDS["stone"]:
                    hit, hn, face, dist = tree.ray_cast(hit + d * 1e-4, d, BK.REACH)
                if hit is not None:
                    near += dist < BK.NEAR
                    if hn.dot(d) < 0.0:
                        met.append(face)
                    continue
                if d.z < -1e-4 and h > 0.0 and -h / d.z < BK.REACH:
                    gnd += 1
                else:
                    sky += 1
        k = float(len(samples) * len(dirs))
        first.append((sky / k, gnd / k, 1.0 - near / k))
        hits.append((met, k))
    seen = []
    for (sky, gnd, op), (met, k) in zip(first, hits):
        sky += BOUNCE * sum(first[f][0] for f in met) / k
        gnd += BOUNCE * sum(first[f][1] for f in met) / k
        seen.append((sky, gnd, op))
    # a stone's facet is one plane a hand wide: it sees one light, whatever triangles it is cut into (else each
    # triangle of its fan shows as a shard)
    facets = {}
    for t in range(len(polys)):
        if kinds[t] != KINDS["stone"]:
            continue
        a, b, c = verts[3 * t], verts[3 * t + 1], verts[3 * t + 2]
        n = (b - a).cross(c - a)
        area = n.length
        if area < 1e-12:
            continue
        n = n / area
        key = (round(soup.ch[3 * t][4], 6), round(n.x * 50), round(n.y * 50), round(n.z * 50))
        facets.setdefault(key, []).append((t, area))
    for tris in facets.values():
        total = sum(w for _, w in tris)
        mean = tuple(sum(seen[t][i] * w for t, w in tris) / total for i in range(3))
        for t, _ in tris:
            seen[t] = mean
    out = []
    for s in seen:
        out += [s] * 3
    return out


def roof_of(facts, timber, date):
    """The roof's covering material and the year it was laid: the era's, unless a 'roof_retiled' event since."""
    year = facts["built"]
    for e in facts["events"]:
        if e["kind"] == "roof_retiled" and e["year"] <= date:
            year = e["year"]
    return dict(material=timber["workings"][facts["era"]]["roof"]["material"], year=year)


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--houses", default="C")
    ap.add_argument("--out", default="cache/houses")
    ap.add_argument("--date", type=float, default=1989.8)
    ap.add_argument("--pack", default="packs/stavanger-1989")
    ap.add_argument("--timber", default="timber.json")
    ap.add_argument("--paint", default="paint.json")
    ap.add_argument("--no-bake", action="store_true")
    ap.add_argument("--tiers", default="near", help="the levels to write (timber.json, levels): near as L.bin, others as L.<tier>.bin")
    a = ap.parse_args(argv)
    out = os.path.join(ROOT, a.out)
    os.makedirs(out, exist_ok=True)
    timber = json.load(open(os.path.join(ROOT, a.pack, a.timber)))
    paint = json.load(open(os.path.join(ROOT, a.pack, a.paint)))
    fixture = json.load(open(os.path.join(ROOT, "fixtures/lt1-corner.json")))
    records = {r["id"]: r for r in fixture["buildings"]}
    seed = fixture["worldSeed"]
    rows = []
    for index, letter in enumerate(a.houses.split(",")):
        b = next(x for x in H.BUILDINGS if x["name"].startswith(letter + " ("))
        hid = int(re.match(r".*?\((\d+)", b["name"]).group(1))
        facts = facts_of(records[hid])
        ground = local_ground(b)
        for tier in a.tiers.split(","):
            t0 = time.time()
            soup, report = HO.build(b, facts, timber, ground, a.date, index, seed, lit_share=0.5, tier=tier)
            t1 = time.time()
            baked = None if a.no_bake else bake_soup(soup, ground)
            soup.write(os.path.join(out, f"{letter}.bin" if tier == "near" else f"{letter}.{tier}.bin"), baked)
            print(f"[houses] {letter} {tier}: {report['triangles']} triangles, built {t1 - t0:.1f} s, baked {time.time() - t1:.1f} s")
        rows.append(dict(index=index, name=letter, id=hid, era=facts["era"], built=facts["built"],
                         wealth=facts["wealth"], events=facts["events"],
                         coats=CO.coats(facts, paint, seed, a.date), roof=roof_of(facts, timber, a.date),
                         fp=[round(c, 3) for xy in H.footprint(b, 0.0) for c in xy]))
        print(f"[houses] {letter} ({hid}, {facts['era']} {facts['built']}): {report['windows']} windows, roof {report['roof']}")
        for w, r in report["walls"].items():
            print(f"[houses]   {w}: {r}")
    json.dump(dict(date=a.date, pack=a.pack, paint=a.paint, houses=rows), open(os.path.join(out, "houses.json"), "w"), indent=1)


if __name__ == "__main__":
    main(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else [])
