#!/usr/bin/env python3
"""L5's split of the materials' shaders (1c; reviews/lt1/light/l5-report.md): who owns bare less flat, from a frame-time
run with L5's arms (tools/perf.sh playable -perf-passes all,all-shadow,bare,flat,flat-<family>...,bare-<term>...).

    python3 tools/shader_split.py reviews/perf/<date>/l5/run-1 [more runs ...] > reviews/perf/<date>/l5/split.md

Offscreen ms (the A/B number), per view and light. A family's cost is bare less 'flat-<family>' (bare with only that
family's materials unlit); a term's is bare less 'bare-<term>' (bare with that term skipped); the shadow sample's is all
less 'all-shadow'. With several runs, each segment's median of the runs' medians, and a second table of each
difference's spread between runs (the largest less the smallest), so a number can be read against its own noise.
"""

import json
import statistics
import sys

VIEWS = ["eye-foot", "eye-on", "street", "into12", "high", "a-window", "steps", "row", "anchor-door"]
TERMS = {
    "townsky": "the town's sky (OS_TownSky: 8 directions x 8 reaches, 64 map reads and 8 atan)",
    "clouds": "the clouds' shadow (OS_CloudLight: the seven-noise cloud field)",
    "haze": "the air (OS_Atmosphere, the existing OS_HAZE_OFF)",
    "lamps": "the lamps' light loop (Forward+ additional lights, look P)",
    "refl": "the reflection probes' sample (GlossyEnvironmentReflection, look P)",
    "brush": "the brushwork (OS_Brush, look P)",
    "growth": "stone's growth layer whole (Growth.hlsl: lichen fields, young rosettes, moss cushions)",
    "rosettes": "stone's young lichen rosettes alone (the 3x3 loop lerped away past about 1 cm a pixel)",
    "near": "every near mark (OS_Near forced to 0: grain relief, sand, crazing, areoles, crumbs)",
}


def load(paths):
    seg = {}
    for p in paths:
        for s in json.load(open(p.rstrip("/") + "/summary.json"))["segments"]:
            seg.setdefault((s["view"], s["light"], s.get("passes") or "all"), []).append(s["offscreen_ms"]["median"])
    return seg


def main(paths):
    seg = load(paths)
    cols = sorted({(v, l) for v, l, _ in seg}, key=lambda c: (c[1], VIEWS.index(c[0]) if c[0] in VIEWS else 99))
    configs = sorted({c for _, _, c in seg})
    fams = [c[5:] for c in configs if c.startswith("flat-")]
    terms = [t for t in TERMS if f"bare-{t}" in configs]

    def med(v, l, c):
        x = seg.get((v, l, c))
        return statistics.median(x) if x else None

    def diff(v, l, a, b):
        xa, xb = seg.get((v, l, a)), seg.get((v, l, b))
        if not xa or not xb:
            return None, None
        per_run = [p - q for p, q in zip(xa, xb)]
        return statistics.median(xa) - statistics.median(xb), (max(per_run) - min(per_run) if len(per_run) > 1 else None)

    rows = [("**all**", lambda v, l: (med(v, l, "all"), None)),
            ("**bare**", lambda v, l: (med(v, l, "bare"), None)),
            ("**flat**", lambda v, l: (med(v, l, "flat"), None)),
            ("**bare less flat** (the materials' shaders)", lambda v, l: diff(v, l, "bare", "flat"))]
    rows += [(f"family *{f}*: bare less flat-{f}", (lambda f: lambda v, l: diff(v, l, "bare", f"flat-{f}"))(f)) for f in fams]
    rows += [("sum of the families", lambda v, l: (sum(d for d in (diff(v, l, "bare", f"flat-{f}")[0] for f in fams) if d is not None)
                                                   if fams else None, None))]
    rows += [(f"term *{t}*: bare less bare-{t}", (lambda t: lambda v, l: diff(v, l, "bare", f"bare-{t}"))(t)) for t in terms]
    if "all-shadow" in configs:
        rows += [("term *shadow* (the shadow map's sample in the shaders): all less all-shadow", lambda v, l: diff(v, l, "all", "all-shadow"))]

    runs = max(len(x) for x in seg.values())
    print("# L5: who owns the materials' shaders\n")
    print(f"{len(paths)} run(s) ({runs} reading(s) a segment); offscreen ms at 2560 by 1440, the median of the runs' medians. "
          "A family's cost is bare less flat-<family>; a term's is bare less bare-<term> (all less all-shadow for the shadow "
          "sample). Bare is every pass off: no shadow map, SSAO, SSR, MSAA or post.\n")
    head = "| | " + " | ".join(f"{l} {v}" for v, l in cols) + " |"
    for title, spread in (("Milliseconds", False), ("Spread between runs (largest less smallest run's difference)", True)):
        if spread and runs < 2:
            break
        print(f"## {title}\n")
        print(head)
        print("| --- " * (len(cols) + 1) + "|")
        for name, f in rows:
            cells = []
            for v, l in cols:
                d, s = f(v, l)
                x = s if spread else d
                cells.append("" if x is None else f"{x:.1f}")
            if spread and all(c == "" for c in cells):
                continue
            print(f"| {name} | " + " | ".join(cells) + " |")
        print()
    print("## The terms\n")
    for t in terms:
        print(f"- *{t}*: {TERMS[t]};")
    if "all-shadow" in configs:
        print("- *shadow*: the main light's shadow-map sample and URP's soft filter in the street and stone shaders (the map still drawn).")


if __name__ == "__main__":
    main(sys.argv[1:])
