#!/usr/bin/env python3
"""The checks a change runs by script before anyone looks at numbers (CLAUDE.md, How work runs). Minimal: only the
walked corner's houses so far.

    python3 tools/check.py [--houses cache/houses]

- Each house's triangles against its tier's budget (docs/foundations.md, the tiers: a house up to 40,000 near, about
  8,000 street, about 1,500 city), each level at most 60% of the one before it (the blender-generators skill, Levels).
  A tier not built (tools/houses.py --tiers) is reported as missing, not passed.
- Every material record houses.json names (its coats' paints, its roof's covering, the wood, stone, mortar, render and
  glass the shader reads) exists in the pack and holds the keys the shader is filled from.
- Every colour the paint rule names is in its colour list.

Exits 1 on a failure, 0 when everything built passes.
"""

import argparse
import json
import os
import struct
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
BUDGET = {"near": 40000, "street": 8000, "city": 1500}  # a house, docs/foundations.md (provisional)
SHARE = 0.6  # a level at most this share of the one before it
ALWAYS = ("pine", "fieldstone", "lime-mortar", "render", "glass")
KEYS = {
    "paint": ("chalk", "gloss", "peel", "water"),
    "cover": ("srgbNew", "srgbOld", "oldYears", "gloss", "water"),
    "pine": ("srgbNew", "srgbWeathered", "weatherHalfYears", "gloss", "water"),
    "fieldstone": ("srgb", "valueSpread", "warmSpread", "gloss", "water"),
    "lime-mortar": ("srgb", "gloss", "water", "jointView", "jointFar"),
    "render": ("srgb", "gloss", "water"),
    "glass": ("gloss", "daylight", "wave"),
}


def triangles(path):
    with open(path, "rb") as f:
        magic, count = struct.unpack("<4si", f.read(8))
    if magic != b"R2B2":
        raise ValueError(f"{path}: not an R2B2 soup")
    return count // 3


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--houses", default="cache/houses")
    a = ap.parse_args(argv)
    fails, missing = [], []
    rows = json.load(open(os.path.join(ROOT, a.houses, "houses.json")))
    pack = os.path.join(ROOT, rows["pack"])
    for h in rows["houses"]:
        before = None
        for tier in ("near", "street", "city"):
            path = os.path.join(ROOT, a.houses, f"{h['name']}.bin" if tier == "near" else f"{h['name']}.{tier}.bin")
            if not os.path.exists(path):
                missing.append(f"house {h['name']} {tier}")
                before = None
                continue
            t = triangles(path)
            ok = t <= BUDGET[tier] and (before is None or t <= SHARE * before)
            share = f", {t / before:.0%} of the level before" if before else ""
            print(f"{'pass' if ok else 'FAIL'}  house {h['name']} {tier} tier: {t:,} triangles (budget {BUDGET[tier]:,}{share})")
            if not ok:
                fails.append(f"house {h['name']} {tier}")
            before = t
    names = {c["paint"]: "paint" for h in rows["houses"] for c in h["coats"].values()}
    names.update({h["roof"]["material"]: "cover" for h in rows["houses"]})
    names.update({m: m for m in ALWAYS})
    for name, kind in sorted(names.items()):
        path = os.path.join(pack, "materials", f"{name}.json")
        if not os.path.exists(path):
            print(f"FAIL  material {name}: no record")
            fails.append(f"material {name}")
            continue
        rec = json.load(open(path))
        lost = [k for k in KEYS[kind] if k not in rec]
        if "water" in rec and len(rec["water"]) != 4:
            lost.append("water (four values)")
        print(f"{'pass' if not lost else 'FAIL'}  material {name}" + (f": lacks {', '.join(lost)}" if lost else ""))
        if lost:
            fails.append(f"material {name}")
    paint = json.load(open(os.path.join(pack, rows["paint"])))
    named = {c for p in paint["periods"] for part in ("body", "back", "trim", "window", "door") for c in (p[part] or [])}
    unknown = sorted(named - set(paint["colours"]))
    print(f"{'pass' if not unknown else 'FAIL'}  paint rule {rows['paint']}: every colour named is listed"
          + (f" (not: {', '.join(unknown)})" if unknown else ""))
    if unknown:
        fails.append("paint colours")
    if missing:
        print(f"missing  not built: {', '.join(missing)}")
    if fails:
        print(f"FAILED: {', '.join(fails)}")
        return 1
    print("passed (what is built)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
