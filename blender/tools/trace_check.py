"""Trace check: everything a plan shows names the diary event that put it there.

    python3 trace_check.py                      # the fixtures, every year each building stands
    python3 trace_check.py --random 500         # plus the stress test's random diaries

Runs on plans, so it needs plain Python, not Blender. For every building and year it walks
the resolved plan and checks that each visible element (anything with a kind, type, era,
style or swatch) carries an `event`, and that the event is in the building's diary up to
that year. A plan that fails shows something the diary cannot explain.

Plan values that read as history but carry no event trail are reported as gaps, not
failures (today: `condition`, which wear is drawn from).

Exits non-zero if any element is untraced or names an event the diary does not hold.
"""

import argparse
import glob
import json
import os
import sys
import types
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [os.path.join(HERE, "..", "generators"), os.path.join(HERE, "..", "resolver")]

from resolve import resolve  # noqa: E402

VISIBLE = ("kind", "type", "era", "style", "swatch")
GAPS = ("condition",)
YEARS = range(1800, 2031)


def walk(node, path, ids, report):
    if isinstance(node, dict):
        if path != "plan" and any(k in node for k in VISIBLE):
            report["elements"] += 1
            if "event" not in node:
                report["untraced"][path] += 1
            elif node["event"] not in ids:
                report["unknown"][path] += 1
        for k, v in node.items():
            walk(v, f"{path}.{k}", ids, report)
    elif isinstance(node, list):
        for v in node:
            walk(v, f"{path}[]", ids, report)


def check(buildings, world_seed, label, report):
    for b in buildings:
        for year in YEARS:
            plan = resolve(b, year, world_seed)
            if plan is None:
                continue
            report["plans"] += 1
            ids = {e["id"] for e in b["events"] if e["year"] <= year}
            walk(plan, "plan", ids, report)
            for g in GAPS:
                if g in plan and any(e["year"] <= year and e["kind"] in ("neglected", "restored") for e in b["events"]):
                    report["gaps"][g] += 1
    report["sources"].append(label)


def random_buildings(n):
    """The stress test's random diaries, without Blender: stress.py imports bpy at the top."""
    sys.modules.setdefault("bpy", types.ModuleType("bpy"))
    for name in ("building", "validate"):
        sys.modules.setdefault(name, types.ModuleType(name))
    import stress  # noqa: E402
    return [stress.random_diary(i) for i in range(n)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--random", type=int, default=0, help="also check this many random diaries")
    args = ap.parse_args()

    report = dict(plans=0, elements=0, untraced=Counter(), unknown=Counter(), gaps=Counter(), sources=[])
    for path in sorted(glob.glob(os.path.join(HERE, "..", "..", "fixtures", "*.json"))):
        data = json.load(open(path))
        if "buildings" in data and data["buildings"] and "events" in data["buildings"][0]:
            check(data["buildings"], data.get("worldSeed", 0), os.path.basename(path), report)
    if args.random:
        check(random_buildings(args.random), 1, f"{args.random} random diaries", report)

    print(f"checked {report['plans']} plans, {report['elements']} visible elements ({', '.join(report['sources'])})")
    for kind in ("untraced", "unknown"):
        for path, n in report[kind].most_common():
            print(f"  {kind}: {path} x{n}")
    for g, n in report["gaps"].items():
        print(f"  gap: `{g}` reads as history in {n} plans but names no event")
    failed = bool(report["untraced"] or report["unknown"])
    print("FAIL" if failed else "pass: every visible element names a diary event")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
