#!/usr/bin/env python3
"""The pass budget (docs/measuring.md, The pass budget): what each pass of the pipeline costs, from a frame-time run
with the passes toggled (tools/perf.sh -perf-passes ... -perf-scenes empty,corner; the walk's whole scene:
tools/perf.sh playable ... -perf-scenes empty,playable).

    python3 tools/pass_budget.py reviews/perf/<date>/passes/run-1 [more runs ...] > passes.md

A pass's cost is the frame with every pass on less the frame with that pass alone off (offscreen, the view drawn back
to back with the GPU kept busy: the A/B number), per scene, view and light. 'bare' is every pass off: what the scene's
geometry costs on its own, drawn with the main light only; 'flat' is bare with every material one unlit colour, so
bare less flat is what the materials' shaders cost. '-beams+shadows' turns both off at once (W3): with the two alone,
it splits low sun's cost into the beams with no shadow map to read, the shadow map with no beams, and what they cost
only together. With several runs, each segment's median of the runs' medians.
"""

import json
import statistics
import sys

PASSES = ["sky", "shadows", "ssao", "ssr", "beams", "foglights", "keyblock", "palette", "post", "msaa", "motes",
          "opaquetex", "depthtex"]
WHAT = {
    "sky": "the sky (Sky.shader), drawn behind everything",
    "shadows": "the sun's shadow map, four cascades of one 4096 map",
    "ssao": "screen-space ambient occlusion (full resolution)",
    "ssr": "screen-space reflections",
    "beams": "the sun's beams (SunBeams.shader: 40 shadow-map taps a pixel)",
    "foglights": "the lamps in the fog (FogLights.shader; the colour copy only, no lamp is lit in these lights)",
    "keyblock": "the woodblock print's key block (look D only; the colour copy and an early out here)",
    "palette": "the style's colour pass (Palette.shader)",
    "post": "post-processing: grade, bloom, grain, vignette, dither",
    "msaa": "MSAA 4x",
    "motes": "the air's motes (low sun only)",
    "opaquetex": "the opaque texture the pipeline copies after the opaques (no shader reads it)",
    "depthtex": "the depth texture (the screen-space passes still ask for it when they are on)",
}


def load(paths):
    runs = [json.load(open(p.rstrip("/") + "/summary.json")) for p in paths]
    seg = {}
    for r in runs:
        for s in r["segments"]:
            seg.setdefault(s["name"], []).append(s)
    out = {}
    for name, ss in seg.items():
        s = ss[0]
        out[name] = dict(scene=s.get("scene") or "corner", passes=s.get("passes") or "all", view=s["view"], light=s["light"],
                         birches=s["birches"], off=statistics.median(x["offscreen_ms"]["median"] for x in ss),
                         gpu=statistics.median(x["gpu_ms"]["median"] for x in ss),
                         frame=statistics.median(x["cpu_ms"]["median"] for x in ss),
                         tris=s["counters"] and next((c["median"] for c in s["counters"] if c["name"] == "triangles"), -1),
                         spread=(max(x["offscreen_ms"]["median"] for x in ss) - min(x["offscreen_ms"]["median"] for x in ss)))
    return runs, out


VIEWS = ["eye-foot", "eye-on", "street", "into12", "high", "birch12", "a-window", "steps", "row", "anchor-door"]
TITLE = {"empty": "The empty scene", "corner": "The corner", "playable": "The walk's corner in the town"}


def main(paths):
    runs, seg = load(paths)
    by = {}
    for s in seg.values():
        if s["birches"]:
            by.setdefault((s["scene"], s["view"], s["light"]), {})[s["passes"]] = s
    lights = sorted({k[2] for k in by})
    scenes = [sc for sc in ("empty", "corner", "playable") if any(k[0] == sc for k in by)]
    r0 = runs[0]
    print("# The pass budget: what each pass costs on the M4\n")
    print(f"{len(runs)} run(s), {r0['started']}, {r0['gpu']} ({r0['api']}), {r0['screen']}, MSAA {r0['msaa']}x; "
          f"{r0['rounds']} rounds of {r0['framesPerSegment']} frames a segment and six batches of six offscreen frames.\n")
    print("Milliseconds offscreen (the view drawn into a 2560 by 1440 target back to back, the GPU kept busy; the A/B "
          "number). A pass's cost is every pass on less every pass on but that one. 'All' and 'bare' (every pass off) "
          "are whole frames. The empty scene is the corner with every renderer hidden but the air's motes: the sky, "
          "the lights and post alone.\n")
    for sc in scenes:
        views = sorted({k[1] for k in by if k[0] == sc}, key=lambda v: VIEWS.index(v) if v in VIEWS else len(VIEWS))
        print(f"## {TITLE[sc]}\n")
        head = "| Pass | " + " | ".join(f"{l} {v}" for l in lights for v in views) + " |"
        print(head)
        print("| --- |" + " --- |" * (len(lights) * len(views)))

        def row(label, f):
            cells = []
            for l in lights:
                for v in views:
                    d = by.get((sc, v, l), {})
                    x = f(d)
                    cells.append("" if x is None else f"{x:.1f}")
            print(f"| {label} | " + " | ".join(cells) + " |")

        row("**all**", lambda d: d["all"]["off"] if "all" in d else None)
        for p in PASSES + ["fullscreen"]:
            row(p, lambda d, p=p: d["all"]["off"] - d["-" + p]["off"] if "all" in d and "-" + p in d else None)
        row("sum of the passes", lambda d: sum(d["all"]["off"] - d["-" + p]["off"] for p in PASSES if "-" + p in d) if "all" in d else None)
        bs = "-beams+shadows"
        if any(bs in d for (s_, _, _), d in by.items() if s_ == sc):
            row("beams and shadows together", lambda d: d["all"]["off"] - d[bs]["off"] if "all" in d and bs in d else None)
            row("  the beams, no shadow map", lambda d: d["-shadows"]["off"] - d[bs]["off"] if "-shadows" in d and bs in d else None)
            row("  the shadow map, no beams", lambda d: d["-beams"]["off"] - d[bs]["off"] if "-beams" in d and bs in d else None)
            row("  only together", lambda d: d["all"]["off"] - d["-beams"]["off"] - d["-shadows"]["off"] + d[bs]["off"]
                if all(k in d for k in ("all", "-beams", "-shadows", bs)) else None)
        row("**bare**", lambda d: d["bare"]["off"] if "bare" in d else None)
        row("all less bare", lambda d: d["all"]["off"] - d["bare"]["off"] if "all" in d and "bare" in d else None)
        if any("flat" in d for (s_, _, _), d in by.items() if s_ == sc):
            row("**flat**", lambda d: d["flat"]["off"] if "flat" in d else None)
            row("bare less flat (the materials' shaders)", lambda d: d["bare"]["off"] - d["flat"]["off"] if "bare" in d and "flat" in d else None)
        print()
    nob = [s for s in seg.values() if not s["birches"]]
    if nob:
        print("## The birch (low sun, every pass on)\n")
        print("| View | With (ms) | Without (ms) | The birch |\n| --- | --- | --- | --- |")
        for s in nob:
            w = by.get((s["scene"], s["view"], s["light"]), {}).get("all")
            if w:
                print(f"| {s['view']} | {w['off']:.1f} | {s['off']:.1f} | {w['off'] - s['off']:+.1f} |")
        print()
    if len(runs) > 1:
        worst = max(seg.values(), key=lambda s: s["spread"] / max(s["off"], 1e-3))
        print(f"Worst spread between runs: {worst['spread']:.2f} ms on {worst['view']}@{worst['light']}/{worst['passes']} "
              f"({100 * worst['spread'] / worst['off']:.1f}%).\n")
    print("## What each pass is\n")
    for p in PASSES:
        print(f"- *{p}*: {WHAT[p]};")
    print("- *fullscreen*: the four full-screen passes together (beams, fog lights, key block, palette).")


if __name__ == "__main__":
    main(sys.argv[1:])
