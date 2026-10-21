"""Mesh hashes: a deterministic hash of every mesh in an exported FBX, channel by channel, read from the file itself
(docs/measuring.md, Mesh hashes; docs/research/performance-at-scale.md, Visual regression and checks, 5).

The FBX's own arrays are read with Blender's bundled parser (io_scene_fbx.parse_fbx), never re-imported, so the hash is
of exactly what Unity reads: per mesh its positions, its corner indices (with the polygon ends) and edges, its normals,
every UV channel by its index and name, colours, smoothing, materials, any other layer, and the model's own transform.
Floats are hashed bit for bit (minus zero made plus zero), so any change at all names the mesh and the channel. The
FBX's header (its creation time, the exporter's version) is left out, so two builds of the same thing hash the same.

The hashes go beside the export, one manifest per folder (`mesh-hashes.json`, keyed by file name; never `<name>.json`,
which the stair's info and the variety sheet already use).

    blender -b --factory-startup --python blender/tools/mesh_hash.py -- write  <fbx> [<fbx> ...]
    blender -b --factory-startup --python blender/tools/mesh_hash.py -- check  <fbx> [<fbx> ...] [--manifest <json>]
    blender -b --factory-startup --python blender/tools/mesh_hash.py -- compare <fbx a> <fbx b>
    blender -b --factory-startup --python blender/tools/mesh_hash.py -- selftest <fbx> <scratch dir>

`check` recomputes each file's hashes and compares them with the manifest beside it (or the one named), and exits 1 on
any difference, naming the mesh and channel. `compare` does the same between two files. `selftest` proves the hash
sees a one-vertex change end to end: it imports the file, exports it twice with the generators' settings, once as it
is and once with one vertex moved by a tenth of a millimetre, and checks that the two plain exports hash the same and
that only that mesh's positions (and the normals of the faces it turns) changed.

Generators call `write_manifest(path)` right after their export (stone.py, wall.py).
"""

import hashlib
import json
import os
import sys

import numpy as np

TOOL = "mesh_hash 1"
MANIFEST = "mesh-hashes.json"


def _parser():
    try:
        from io_scene_fbx import parse_fbx
    except ImportError:
        import bpy  # noqa: F401  (inside Blender the core add-ons sit beside its scripts)
        import addon_utils
        for p in addon_utils.paths():
            if os.path.isdir(os.path.join(p, "io_scene_fbx")) and p not in sys.path:
                sys.path.append(p)
        from io_scene_fbx import parse_fbx
    return parse_fbx


ARRAYS = {"d": np.float64, "f": np.float32, "i": np.int32, "l": np.int64, "b": np.uint8}
SCALARS = {"D": np.float64, "F": np.float32}
PLURAL = {"normal": "normals", "binormal": "binormals", "tangent": "tangents", "color": "colours",
          "smoothing": "smoothing", "material": "materials", "edgecrease": "creases", "visibility": "visibility"}


def _h(*parts):
    h = hashlib.sha256()
    for p in parts:
        h.update(p if isinstance(p, bytes) else str(p).encode())
        h.update(b"\x1f")
    return h.hexdigest()[:16]


def _feed(h, e):
    """An element and everything under it into the hash, depth first, in file order: every property typed, float
    arrays bit for bit with minus zero made plus zero (so the sign of a zero never counts)."""
    h.update(e.id or b"")
    h.update(b"(")
    for p, t in zip(e.props, e.props_type):
        t = chr(t) if isinstance(t, int) else t.decode()
        h.update(t.encode())
        if t in ARRAYS:
            a = np.frombuffer(p, dtype=ARRAYS[t]) if not isinstance(p, np.ndarray) else p.astype(ARRAYS[t])
            if t in "df":
                a = a + 0.0
            h.update(np.ascontiguousarray(a).tobytes())
        elif t in SCALARS:
            h.update((np.asarray([p], dtype=SCALARS[t]) + 0.0).tobytes())
        elif isinstance(p, (bytes, bytearray)):
            h.update(bytes(p))
        else:
            h.update(repr(p).encode())
        h.update(b",")
    h.update(b")[")
    for c in e.elems:
        _feed(h, c)
    h.update(b"]")


def _hash_elems(elems):
    h = hashlib.sha256()
    for e in elems:
        _feed(h, e)
    return h.hexdigest()[:16]


def _name(prop):
    return prop.split(b"\x00\x01")[0].decode("utf-8", "replace")


def _channel(e):
    """The channel a geometry's child element belongs to."""
    i = e.id.decode()
    if i == "Vertices":
        return "positions"
    if i == "PolygonVertexIndex":
        return "indices"
    if i == "Edges":
        return "edges"
    if i.startswith("LayerElement"):
        kind = i[len("LayerElement"):].lower()
        index = e.props[0] if e.props else 0
        if kind == "uv":
            return f"uv{index}"
        return PLURAL.get(kind, kind) + (f"{index}" if index else "")
    return "other"


def hash_fbx(path):
    """{mesh name: {hash, vertices, corners, triangles, channels: {channel: hash}}} for every mesh in the file."""
    parse_fbx = _parser()
    root, version = parse_fbx.parse(path)
    objects = next((e for e in root.elems if e.id == b"Objects"), None)
    conns = next((e for e in root.elems if e.id == b"Connections"), None)
    if objects is None:
        raise ValueError(f"{path}: no Objects in the FBX")
    geoms = {e.props[0]: e for e in objects.elems if e.id == b"Geometry" and e.props[2] == b"Mesh"}
    models = {e.props[0]: e for e in objects.elems if e.id == b"Model"}
    owner = {}
    for c in (conns.elems if conns else []):
        if c.props[0] == b"OO" and c.props[1] in geoms and c.props[2] in models:
            owner[c.props[1]] = models[c.props[2]]
    meshes = {}
    for gid, g in geoms.items():
        model = owner.get(gid)
        name = _name(model.props[1]) if model is not None else _name(g.props[1])
        chans = {}
        for c in g.elems:
            chans.setdefault(_channel(c), []).append(c)
        channels = {ch: _hash_elems(els) for ch, els in sorted(chans.items())}
        if model is not None:
            # where the mesh stands: the model's own transform (its Lcl translation, rotation, scale and pivots)
            p70 = next((e for e in model.elems if e.id == b"Properties70"), None)
            if p70 is not None:
                channels["transform"] = _hash_elems([p for p in p70.elems if p.props and p.props[0].startswith(
                    (b"Lcl", b"Geometric", b"Rotation", b"Scaling", b"PreRotation", b"PostRotation"))])
        pvi = next((np.frombuffer(c.props[0], np.int32) for c in g.elems if c.id == b"PolygonVertexIndex"),
                   np.zeros(0, np.int32))
        verts = next((len(c.props[0]) // 3 for c in g.elems if c.id == b"Vertices"), 0)
        polys = int((pvi < 0).sum())
        key = name
        n = 1
        while key in meshes:
            n += 1
            key = f"{name}#{n}"
        meshes[key] = dict(hash=_h(*[f"{k}={v}" for k, v in sorted(channels.items())]), vertices=int(verts),
                           corners=int(len(pvi)), triangles=int(len(pvi) - 2 * polys), channels=channels)
    return dict(sorted(meshes.items()))


def entry(path):
    meshes = hash_fbx(path)
    return dict(tool=TOOL, hash=_h(*[f"{k}={v['hash']}" for k, v in meshes.items()]),
                triangles=sum(m["triangles"] for m in meshes.values()), meshes=meshes)


def manifest_path(fbx):
    return os.path.join(os.path.dirname(os.path.abspath(fbx)), MANIFEST)


def write_manifest(fbx, manifest=None):
    """Hash one exported file into the manifest beside it (other files' entries kept). Returns its entry."""
    manifest = manifest or manifest_path(fbx)
    data = {}
    if os.path.exists(manifest):
        with open(manifest) as fh:
            data = json.load(fh)
    e = entry(fbx)
    data[os.path.basename(fbx)] = e
    with open(manifest, "w") as fh:
        json.dump(dict(sorted(data.items())), fh, indent=1)
        fh.write("\n")
    print("HASH", os.path.basename(fbx), e["hash"], f"{e['triangles']} triangles", "->", manifest)
    return e


def diff(a, b, label_a="expected", label_b="found"):
    """The differences between two entries, as lines naming the mesh and channel."""
    out = []
    for name in sorted(set(a["meshes"]) | set(b["meshes"])):
        ma, mb = a["meshes"].get(name), b["meshes"].get(name)
        if ma is None or mb is None:
            out.append(f"  {name}: only in {label_b if ma is None else label_a}")
            continue
        if ma["hash"] == mb["hash"]:
            continue
        chans = sorted(set(ma["channels"]) | set(mb["channels"]))
        changed = [c for c in chans if ma["channels"].get(c) != mb["channels"].get(c)]
        counts = "" if (ma["vertices"], ma["triangles"]) == (mb["vertices"], mb["triangles"]) else \
            f" (vertices {ma['vertices']} -> {mb['vertices']}, triangles {ma['triangles']} -> {mb['triangles']})"
        out.append(f"  {name}: {', '.join(changed)} changed{counts}")
    return out


def check(fbxs, manifest=None):
    bad = 0
    for f in fbxs:
        m = manifest or manifest_path(f)
        if not os.path.exists(m):
            print("NO MANIFEST", f, m)
            bad += 1
            continue
        with open(m) as fh:
            want = json.load(fh).get(os.path.basename(f))
        if want is None:
            print("NOT IN MANIFEST", f, m)
            bad += 1
            continue
        got = entry(f)
        if got["hash"] == want["hash"]:
            print("SAME", os.path.basename(f), got["hash"])
        else:
            bad += 1
            print("CHANGED", os.path.basename(f), want["hash"], "->", got["hash"])
            print("\n".join(diff(want, got)))
    return bad


def compare(a, b):
    ea, eb = entry(a), entry(b)
    if ea["hash"] == eb["hash"]:
        print("SAME", ea["hash"], f"{ea['triangles']} triangles in {len(ea['meshes'])} meshes")
        return 0
    print("DIFFERENT", ea["hash"], eb["hash"])
    print("\n".join(diff(ea, eb, a, b)))
    return 1


EXPORT = dict(use_selection=True, object_types={"MESH"}, axis_forward="Z", axis_up="Y", bake_space_transform=True,
              apply_unit_scale=True, apply_scale_options="FBX_SCALE_ALL", mesh_smooth_type="OFF",
              colors_type="LINEAR", use_mesh_modifiers=False, add_leaf_bones=False, bake_anim=False,
              path_mode="STRIP", embed_textures=False)


def selftest(fbx, scratch):
    """A one-vertex change, end to end through Blender's FBX export: only that mesh's positions may change."""
    import bpy
    os.makedirs(scratch, exist_ok=True)
    for ob in list(bpy.data.objects):
        bpy.data.objects.remove(ob, do_unlink=True)
    bpy.ops.import_scene.fbx(filepath=fbx)
    obs = sorted((o for o in bpy.context.scene.objects if o.type == "MESH"), key=lambda o: o.name)
    for o in obs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = obs[0]
    same_a = os.path.join(scratch, "selftest_a.fbx")
    same_b = os.path.join(scratch, "selftest_b.fbx")
    moved = os.path.join(scratch, "selftest_moved.fbx")
    bpy.ops.export_scene.fbx(filepath=same_a, **EXPORT)
    bpy.ops.export_scene.fbx(filepath=same_b, **EXPORT)
    v = obs[0].data.vertices[len(obs[0].data.vertices) // 2]
    v.co.z += 0.0001
    obs[0].data.update()
    bpy.ops.export_scene.fbx(filepath=moved, **EXPORT)
    ea, eb, em = entry(same_a), entry(same_b), entry(moved)
    ok = ea["hash"] == eb["hash"]
    print("SELFTEST exported twice:", "same" if ok else "DIFFERENT", ea["hash"], eb["hash"])
    lines = diff(ea, em)
    print(f"SELFTEST one vertex of {obs[0].name} moved 0.1 mm:", "changed" if lines else "NOT SEEN")
    print("\n".join(lines))
    # (moving a vertex also turns its faces, so the exported corner normals beside it change with it)
    want = [f"  {obs[0].name}: normals, positions changed"]
    passed = ok and lines == want
    print("SELFTEST", "PASS" if passed else "FAIL")
    return 0 if passed else 1


if __name__ == "__main__":
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
    if not argv:
        print(__doc__)
        sys.exit(2)
    cmd, rest = argv[0], argv[1:]
    manifest = None
    if "--manifest" in rest:
        i = rest.index("--manifest")
        manifest = rest[i + 1]
        rest = rest[:i] + rest[i + 2:]
    if cmd == "write":
        for f in rest:
            write_manifest(f, manifest)
        code = 0
    elif cmd == "check":
        code = 1 if check(rest, manifest) else 0
    elif cmd == "compare":
        code = compare(rest[0], rest[1])
    elif cmd == "selftest":
        code = selftest(rest[0], rest[1])
    else:
        print(__doc__)
        code = 2
    sys.stdout.flush()
    os._exit(code)
