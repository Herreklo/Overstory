"""Export a fixture street to Unity, as it stands in one year.

    blender -b --factory-startup --python export_street.py -- ../../fixtures/lt1-street.json ../../unity --year 1989

Writes, inside the Unity project:
- Assets/Art/Buildings/<street>/bld_<id>_<year>.fbx, one per building, at the default strength
  (or --style), with the lit floors of the fixture's `lit` block;
- Assets/Art/Kit/lamp/ and Assets/Art/Kit/bollard/, the street's kit pieces;
- Assets/Art/Palette/palette_albedo.png and palette_emit.png;
- Assets/Art/Buildings/<street>/street.json, the street resolved: where each building, lamp and
  bollard stands, and the bands of ground. Unity places and draws it; it decides nothing.

Every building is checked before export (validate.py), and the street is checked as a whole:
no two buildings within MIN_GAP of each other. A failure stops the export; nothing is written
for a street that fails.

Coordinates in street.json are street coordinates in metres: x along the street (as the plots),
y from the building line towards the back of the plots (negative towards the harbour), z up.
The FBX files are written so that Unity's (x, y, z) is the street's (x, z, y).
"""

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [os.path.join(HERE, "..", "generators"), os.path.join(HERE, "..", "resolver")]

import bpy  # noqa: E402
from mathutils import Vector  # noqa: E402

import palette  # noqa: E402
import building  # noqa: E402
import validate  # noqa: E402
import lamp  # noqa: E402
import bollard  # noqa: E402
from resolve import resolve  # noqa: E402
from eras import DEFAULT_STYLE  # noqa: E402

MIN_GAP = 1.0  # metres between neighbouring buildings, eaves included
GROUND_LINE = 1.0  # what stands below this height (steps, porches, bays) keeps behind the building line


def export_fbx(obj, path):
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    os.makedirs(os.path.dirname(path), exist_ok=True)
    bpy.ops.export_scene.fbx(
        filepath=path,
        use_selection=True,
        object_types={"MESH"},
        axis_forward="Z",
        axis_up="Y",
        bake_space_transform=True,
        apply_unit_scale=True,
        apply_scale_options="FBX_SCALE_ALL",
        mesh_smooth_type="OFF",
        use_mesh_modifiers=True,
        add_leaf_bones=False,
        bake_anim=False,
        path_mode="STRIP",
        embed_textures=False,
    )


def xyz(x, y, z):
    return dict(x=round(x, 4), y=round(y, 4), z=round(z, 4))


def lamp_variant(kind, installed):
    """The lamp of this kind from the latest era put up by the year it was installed."""
    best = None
    for v in lamp.VARIANTS:
        k, year = v.rsplit("-", 1)
        if k == kind and int(year) <= installed and (best is None or int(year) > int(best.rsplit("-", 1)[1])):
            best = v
    if best is None:
        raise ValueError(f"no {kind} lamp from {installed} or earlier")
    return best


def ground_bands(st):
    """The bands of ground from the building line out to the quay edge, in street y (metres)."""
    y = 0.0
    bands = []
    for key in ("pavement", "carriageway", "quay"):
        w = st[key]["width"] / 1000.0
        bands.append(dict(name=key, y0=round(y - w, 3), y1=round(y, 3), surface=st[key]["surface"]))
        y -= w
    return bands, round(y, 3)


def main(argv):
    fixture_path, unity = argv[0], argv[1]
    opts = dict(zip(argv[2::2], argv[3::2]))
    year = int(opts.get("--year", 1989))
    style = opts.get("--style", DEFAULT_STYLE)
    fx = json.load(open(fixture_path))
    st = fx["street"]
    sid = st["id"]
    ws = fx["worldSeed"]
    lit = {f["building"]: f["floors"] for f in fx.get("lit", {}).get("floors", [])}

    bpy.ops.wm.read_factory_settings(use_empty=True)
    mat = palette.material()
    assets = os.path.join(unity, "Assets")
    out_bld = os.path.join(assets, "Art", "Buildings", sid)

    # -- build and check every building, then the street as a whole -----------------------------------
    placed, problems = [], []
    for bd in fx["buildings"]:
        plan = resolve(bd, year, ws)
        if plan is None:
            continue  # not built yet, or gone
        floors = lit.get(bd["id"], [])
        ob = building.build(plan, style, name=f"bld_{bd['id']}_{year}", material=mat, lit=floors)
        probs = validate.check(ob)
        if probs:
            problems.append((bd["id"], probs))
        vs = [v.co for v in ob.data.vertices]
        front = min(v.y for v in vs if v.z < GROUND_LINE)
        cx = (bd["plot"]["x"] + bd["plot"]["w"] / 2) / 1000.0
        # street y grows towards the back of the plot, as Blender's y does
        pos = (cx, -front, 0.0)
        span = (cx + min(v.x for v in vs), cx + max(v.x for v in vs))
        tris = sum(len(p.vertices) - 2 for p in ob.data.polygons)
        placed.append(dict(id=bd["id"], obj=ob, pos=pos, span=span, tris=tris, lit=floors, type=bd["type"]))
    placed.sort(key=lambda p: p["span"][0])
    for a, b in zip(placed, placed[1:]):
        gap = b["span"][0] - a["span"][1]
        if gap < MIN_GAP:
            problems.append((f"{a['id']}/{b['id']}", [f"only {gap:.2f} m apart"]))
    if problems:
        for p in problems:
            print("FAIL", p)
        print("nothing exported")
        return 1

    # -- write ------------------------------------------------------------------------------------------
    palette.save_maps(os.path.join(assets, "Art", "Palette"))
    buildings = []
    for p in placed:
        fname = f"bld_{p['id']}_{year}.fbx"
        export_fbx(p["obj"], os.path.join(out_bld, fname))
        buildings.append(dict(id=p["id"], type=p["type"], file=f"Assets/Art/Buildings/{sid}/{fname}", position=xyz(*p["pos"]), lit=p["lit"], tris=p["tris"]))

    kit = []
    for v in lamp.VARIANTS:
        ob, light = lamp.build(v)
        rel = f"Assets/Art/Kit/lamp/{ob.name}.fbx"
        export_fbx(ob, os.path.join(unity, rel))
        kit.append(dict(name=v, file=rel, light=xyz(*light), glow=lamp.VARIANTS[v]["light"]))
    ob = bollard.build("cast-iron")
    rel = f"Assets/Art/Kit/bollard/{ob.name}.fbx"
    export_fbx(ob, os.path.join(unity, rel))
    kit.append(dict(name="bollard-cast-iron", file=rel, light=xyz(0, 0, 0), glow=""))

    lamps = []
    for L in st["lamps"]:
        if L["installed"] > year:
            continue
        lamps.append(dict(id=L["id"], variant=lamp_variant(L["kind"], L["installed"]), position=xyz(L["x"] / 1000.0, L["y"] / 1000.0, 0.0), light=L["light"]))

    bands, edge = ground_bands(st)
    x0, x1 = st["x0"] / 1000.0, st["x1"] / 1000.0
    bl = st["bollards"]
    bollards = []
    if bl["installed"] <= year:
        n = int((x1 - x0) // (bl["spacing"] / 1000.0))
        start = x0 + ((x1 - x0) - (n - 1) * bl["spacing"] / 1000.0) / 2
        bollards = [xyz(start + i * bl["spacing"] / 1000.0, edge + bl["inset"] / 1000.0, 0.0) for i in range(n)]

    street = dict(
        street=st["name"],
        year=year,
        style=style,
        worldSeed=ws,
        fixture=os.path.relpath(os.path.abspath(fixture_path), os.path.abspath(unity)),
        x0=x0,
        x1=x1,
        bands=bands,
        quay=dict(edge=edge, height=st["quay"]["height"] / 1000.0, coping=st["quay"]["coping"]),
        water=dict(level=st["water"]["level"] / 1000.0),
        backland=dict(depth=st["backland"]["depth"] / 1000.0, surface=st["backland"]["surface"],
                      profile=[dict(y=q["y"] / 1000.0, z=q["z"] / 1000.0) for q in st["backland"].get("profile", [])]),
        buildings=buildings,
        lamps=lamps,
        bollards=dict(variant="bollard-cast-iron", positions=bollards),
        kit=kit,
        emissive=[dict(swatch=k, off=v[0], group=v[1]) for k, v in palette.EMISSIVE.items()],
        palette=dict(grid=palette.GRID, names=palette.NAMES),
    )
    os.makedirs(out_bld, exist_ok=True)
    with open(os.path.join(out_bld, "street.json"), "w") as f:
        json.dump(street, f, indent=2)
        f.write("\n")
    total = sum(b["tris"] for b in buildings)
    print(f"exported {len(buildings)} buildings ({total} triangles), {len(lamps)} lamps, {len(bollards)} bollards at {style}, {year}")
    return 0


if __name__ == "__main__":
    argv = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else sys.argv[1:]
    sys.exit(main(argv))
