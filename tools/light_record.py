#!/usr/bin/env python3
"""The light records (schemas/light-record.schema.json; reviews/lt1/light/la-report.md, What L1 must hold).

A record's inputs are its world state, its sources and its overrides; its id is their hash (schemas/hashing.md). This
tool writes the sources and the id from the files they name, and checks a record against the schema and the files.
The derived block is Unity's to write (Overstory.EditorTools.LT1Light.Derive, light-derive-1), never this tool's.

    .venv/bin/python tools/light_record.py write [records...]   the sources and id of each (fixtures/light/*.json)
    .venv/bin/python tools/light_record.py check [records...]   schema, id and sources; exit 1 on any problem

Sources:
- fabric: the heart's lamps (lights.json, shops apart) and its built meshes, by content;
- people: who is in (the lit shopfronts in lights.json, the lit windows in the buildings' meshes, authored by
  heart_layout.py's evening());
- pack: the pack's light tables but the keys (light/sky.json, light/lamp-kinds.json);
- keys: light/keys.json.
"""

import glob
import hashlib
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import hashes as HS  # noqa: E402

FUNCTION = "light-derive-1"
HEART = os.path.join(ROOT, "unity", "Assets", "Art", "Blockout", "heart")
LIGHT = os.path.join(ROOT, "packs", "{pack}", "light")
RECORDS = os.path.join(ROOT, "fixtures", "light")


def read(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def sha(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def sources(world):
    lamps = read(os.path.join(HEART, "lights.json"))["lamps"]
    meshes = sorted(n for n in os.listdir(HEART) if n.endswith(".fbx"))
    fabric = {"lamps": [l for l in lamps if l["kind"] != "shop"],
              "meshes": {n: sha(os.path.join(HEART, n)) for n in meshes}}
    people = {"shops": [l for l in lamps if l["kind"] == "shop"],
              "windows": {n: sha(os.path.join(HEART, n)) for n in meshes if n.startswith("buildings")},
              "authored": "blender/blockouts/heart_layout.py:evening"}
    light = LIGHT.format(pack=world["pack"])
    return {
        "fabric": HS.hash_hex(fabric),
        "people": HS.hash_hex(people),
        "pack": HS.hash_hex({"sky": read(os.path.join(light, "sky.json")),
                             "lampKinds": read(os.path.join(light, "lamp-kinds.json"))}),
        "keys": HS.hash_hex(read(os.path.join(light, "keys.json"))),
        "function": FUNCTION,
    }


def identity(record):
    return HS.hash_hex({"world": record["world"], "sources": record["sources"], "overrides": record["overrides"]})


def files(args):
    return args or sorted(glob.glob(os.path.join(RECORDS, "*.json")))


def write(paths):
    for path in paths:
        r = read(path)
        out = {"schemaVersion": 2, "id": "", "world": r["world"], "sources": sources(r["world"]),
               "overrides": r.get("overrides", []), "derived": r.get("derived", {})}
        out["id"] = identity(out)
        stale = r.get("id") != out["id"]
        with open(path, "w", encoding="utf-8") as f:
            json.dump(out, f, indent=2, ensure_ascii=False)
            f.write("\n")
        print(f"{os.path.relpath(path, ROOT)}: {out['id']}" + (" (new inputs: derive again)" if stale else ""))


def check(paths):
    from jsonschema import Draft202012Validator
    from referencing import Registry, Resource
    from referencing.jsonschema import DRAFT202012
    schemas = {n: read(os.path.join(ROOT, "schemas", n)) for n in os.listdir(os.path.join(ROOT, "schemas"))
               if n.endswith(".schema.json")}
    registry = Registry().with_resources(
        [(s["$id"], Resource.from_contents(s, default_specification=DRAFT202012)) for s in schemas.values()])
    validator = Draft202012Validator(schemas["light-record.schema.json"], registry=registry)
    terms = {t["id"] for t in read(os.path.join(ROOT, "schemas", "light-terms.json"))["terms"]}
    bad = 0
    for path in paths:
        r = read(path)
        problems = [f"{'/'.join(map(str, e.absolute_path))}: {e.message}" for e in validator.iter_errors(r)]
        if r.get("id") != identity(r):
            problems.append("id is not the hash of its inputs")
        if r.get("sources") != sources(r["world"]):
            problems.append("sources differ from the files now: write, then derive again")
        pushes = [p for o in r.get("overrides", []) for p in o["pushes"]] + r.get("derived", {}).get("keys", {}).get("pushes", [])
        problems += [f"push on an unknown term {p['target']}" for p in pushes if p["target"] not in terms]
        for p in problems:
            print(f"{os.path.relpath(path, ROOT)}: {p}")
        bad += bool(problems)
    print(f"{len(paths) - bad} of {len(paths)} records hold")
    return bad == 0


if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in ("write", "check"):
        sys.exit(__doc__)
    if sys.argv[1] == "write":
        write(files(sys.argv[2:]))
    else:
        sys.exit(0 if check(files(sys.argv[2:])) else 1)
