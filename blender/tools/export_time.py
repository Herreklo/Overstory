"""Export the corner's five houses at 1989, 2000, 2010 and 2020 to Unity (docs/experiments.md, LT1f).

    python3 blender/tools/time_key.py
    blender -b --factory-startup --python blender/tools/export_time.py -- unity [--style gentle] [--arms real,shuffled]

Reads reviews/lt1/time/readers/diaries.json (written by time_key.py: the record, and the shuffled control), resolves
each house in each year, builds it with the test-quality generator (building.py) at the corner's real proportions,
checks it (validate.py; a failure stops the export and nothing is written), and writes:
- Assets/Art/Buildings/time/<arm>/bld_<letter>_<year>.fbx, each house standing where the heart's grey mass for it
  stands (heart_layout's footprint): the middle of its main body's front on the middle of the heart's front, facing
  the same way, the top of its plinth at the heart's floor. A foundation block runs 8 m down under the body so the
  house meets the slope (the heart's masses do the same; it is buried wherever the ground is higher);
- Assets/Art/Buildings/time/time.json: for each arm, year and house, the file, its origin and turn in street metres
  (Unity's x, y, z is the street's x, z, y), and the house's middle for labels.

Nothing differs between two years of one house except what its plan says: the seeds are the diary's, so a part not
touched by an event is built the same.
"""

import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
sys.path[:0] = [HERE, os.path.join(HERE, "..", "generators"), os.path.join(HERE, "..", "resolver")]

import bpy  # noqa: E402
import bmesh  # noqa: E402

import palette  # noqa: E402
import building  # noqa: E402
import validate  # noqa: E402
import bake  # noqa: E402
from resolve import resolve  # noqa: E402
from export_street import export_fbx, xyz  # noqa: E402

FOUNDATION = 8.0  # metres of foundation under the body, buried where the ground stands higher


def foundation(ob, W, D):
    """A block under the main body from just above its foot down FOUNDATION metres, in the stone swatch."""
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    uv_layer = bm.loops.layers.uv.active
    u, v = palette.uv("stone")
    x0, x1, y0, y1 = -W / 2 + 0.06, W / 2 - 0.06, -D / 2 + 0.06, D / 2 - 0.06
    z0, z1 = -FOUNDATION, 0.02
    vs = [bm.verts.new(p) for p in ((x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0),
                                     (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1))]
    for f in ((0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7), (3, 2, 1, 0)):
        face = bm.faces.new([vs[i] for i in f])
        for loop in face.loops:
            loop[uv_layer].uv = (u, v)
    bm.normal_update()
    bm.to_mesh(ob.data)
    bm.free()


def placement(heart, W, D, P):
    """The origin and turn that put the main body's front middle (local 0, -D/2, P) on the heart's front middle at its
    floor, facing as the heart's footprint does (local x along the front, local y back from it)."""
    a = math.radians(heart["angle"])
    c, s = math.cos(a), math.sin(a)
    ax, ay = heart["ox"] + heart["w"] / 2 * c, heart["oy"] + heart["w"] / 2 * s
    lx, ly = 0.0, -D / 2
    ox, oy = ax - (lx * c - ly * s), ay - (lx * s + ly * c)
    return (ox, oy, heart["base"] - P), heart["angle"]


def main(argv):
    unity = argv[0]
    opts = dict(zip(argv[1::2], argv[2::2]))
    style = opts.get("--style", "gentle")
    arms = opts.get("--arms", "real,shuffled").split(",")
    src = json.load(open(os.path.join(ROOT, "reviews", "lt1", "time", "readers", "diaries.json")))
    ws = json.load(open(os.path.join(ROOT, "fixtures", "lt1-corner.json")))["worldSeed"]
    houses, years = src["houses"], src["years"]

    bpy.ops.wm.read_factory_settings(use_empty=True)
    mat = palette.material()
    built, problems = [], []
    for arm in arms:
        for year in years:
            for hs in houses:
                letter = hs["letter"]
                plan = resolve(src[arm][letter], year, ws)
                ob = building.build(plan, style, name=f"time_{arm}_{letter}_{year}", material=mat)
                probs = validate.check(ob)
                if probs:
                    problems.append((arm, letter, year, probs))
                m = plan["main"]
                W, D, P = m["W"] / 1000.0, m["D"] / 1000.0, m["plinth"] / 1000.0
                foundation(ob, W, D)
                (ox, oy, oz), yaw = placement(hs["heart"], W, D, P)
                a = math.radians(yaw)
                mid = (ox, oy, oz + P + m["H"] / 2000.0)  # the body's middle, for labels
                tris = sum(len(p.vertices) - 2 for p in ob.data.polygons)
                built.append(dict(arm=arm, year=year, letter=letter, id=hs["id"], obj=ob, origin=(ox, oy, oz), yaw=yaw,
                                  mid=mid, tris=tris))
    if problems:
        for p in problems:
            print("FAIL", p)
        print("nothing exported")
        return 1

    out = os.path.join(unity, "Assets", "Art", "Buildings", "time")
    rows = []
    for b in built:
        bake.bake(b["obj"])  # what each face sees: sky, ground, openness
        rel = f"Assets/Art/Buildings/time/{b['arm']}/bld_{b['letter']}_{b['year']}.fbx"
        export_fbx(b["obj"], os.path.join(unity, rel))
        rows.append(dict(arm=b["arm"], year=b["year"], letter=b["letter"], id=b["id"], file=rel,
                         position=xyz(*b["origin"]), yaw=round(b["yaw"], 4), middle=xyz(*b["mid"]), tris=b["tris"]))
    with open(os.path.join(out, "time.json"), "w") as f:
        json.dump(dict(style=style, worldSeed=ws, years=years, houses=[dict(letter=h["letter"], id=h["id"], heart=h["heart"]) for h in houses],
                       buildings=rows), f, indent=1)
        f.write("\n")
    print(f"exported {len(rows)} houses ({sum(r['tris'] for r in rows)} triangles) at {style}: {', '.join(arms)} x {years}")
    return 0


if __name__ == "__main__":
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
    sys.exit(main(argv))
