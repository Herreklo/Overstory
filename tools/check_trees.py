#!/usr/bin/env python3
"""The walked corner's trees against their budgets (blender/parts/trees/corner.json, budget), read from the meshes
themselves (cache/trees/corner, written by blender/parts/trees/corner.py):

- the near birch's drawn triangles at its near level, a tree's street and far levels, a heath birch (far only);
- each level at most share of the one before it (the blender-generators skill, Levels);
- shadow proxies are counted apart (drawn into the shadow map only).

    python3 tools/check_trees.py        (tools/check.py runs it too)

Exits 1 on a failure, 0 when everything built passes. A tree or level not built is reported as missing, not passed.
"""

import json
import os
import struct
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CACHE = "cache/trees/corner"
DATA = "blender/parts/trees/corner.json"


def submeshes(path):
    """Triangles per submesh of a TRE1 mesh."""
    with open(path, "rb") as f:
        magic, n, s = struct.unpack("<4sii", f.read(12))
        if magic != b"TRE1":
            raise ValueError(f"{path}: not a TRE1 mesh")
        f.seek(n * 16 * 4, 1)
        out = {}
        for _ in range(s):
            name = f.read(16).rstrip(b"\0").decode("ascii")
            (c,) = struct.unpack("<i", f.read(4))
            f.seek(c * 4, 1)
            out[name] = c // 3
    return out


def check():
    """Prints a line per tree and level; returns the failures."""
    budget = json.load(open(os.path.join(ROOT, DATA)))["budget"]
    index_path = os.path.join(ROOT, CACHE, "trees.json")
    if not os.path.exists(index_path):
        print(f"missing  trees: {CACHE}/trees.json not built (blender/parts/trees/corner.py)")
        return []
    fails = []
    for t in json.load(open(index_path))["trees"]:
        names = [lv["level"] for lv in t["levels"]]
        heath = names == ["far"] and t["habit"] == "birch"
        before = None
        for lv in t["levels"]:
            path = os.path.join(ROOT, lv["file"])
            if not os.path.exists(path):
                print(f"missing  tree {t['id']} {lv['level']}: {lv['file']}")
                before = None
                continue
            tris = submeshes(path)
            drawn = sum(v for k, v in tris.items() if k != "shadow")
            cap = budget["far_heath"] if heath else budget[lv["level"]]
            ok = drawn <= cap and (before is None or drawn <= budget["share"] * before)
            share = f", {drawn / before:.0%} of the level before" if before else ""
            shadow = f", shadow proxies {tris['shadow']:,}" if "shadow" in tris else ""
            print(f"{'pass' if ok else 'FAIL'}  tree {t['id']} {lv['level']}: {drawn:,} triangles (budget {cap:,}{share}{shadow})")
            if not ok:
                fails.append(f"tree {t['id']} {lv['level']}")
            before = drawn
    return fails


if __name__ == "__main__":
    failed = check()
    print(f"FAILED: {', '.join(failed)}" if failed else "passed (what is built)")
    sys.exit(1 if failed else 0)
