#!/usr/bin/env python3
"""The scale test's numbers (docs/research/scale-test.md): the district's generation, its cache per square kilometre and
per kilometre of street, the maps it would carry, and how many chunks a second the camera's movement asks for at each
unit size, against what loading and building one costs.

    python3 tools/scale_report.py <district dir> [--summary reviews/perf/<date>/district/run-1/summary.json]
        [--wall <seconds the generation took>] [--processes <n>] > report.md

Reads <district>/district.json and <district>/parts/part_*.json (blender/tools/scale_district.py), and the player's
summary (the loader's and the benchmarks' numbers) when given. Standard library only.
"""

import glob
import json
import math
import os
import statistics
import sys

# the levels' units and reach (docs/building-blocks.md, Levels, chunks, instancing and the far field)
UNITS = [
    ("L0 and L1, 4 m chunks", 4.0, 20.0),
    ("L2, 32 m cells", 32.0, 80.0),
    ("L3 shells, 32 m cells", 32.0, 200.0),
    ("streaming, 64 m chunks", 64.0, 300.0),
    ("L4 blocks, 128 m", 128.0, 1500.0),
]
MOVES = [  # (name, metres a second, height of the eye above the street)
    ("walk", 1.4, 1.7),
    ("run", 4.0, 1.7),
    ("drive (50 km/h)", 14.0, 1.5),
    ("city camera pan, 150 m up", 300.0, 150.0),
]


def q(v, p):
    s = sorted(v)
    return s[min(len(s) - 1, max(0, math.ceil(p * len(s)) - 1))] if s else float("nan")


def cells_in(x, y, r, s):
    """The cells of side s whose squares come within r of (x, y)."""
    out = set()
    for i in range(int(math.floor((x - r) / s)), int(math.floor((x + r) / s)) + 1):
        for j in range(int(math.floor((y - r) / s)), int(math.floor((y + r) / s)) + 1):
            dx = max(i * s - x, 0, x - (i + 1) * s)
            dy = max(j * s - y, 0, y - (j + 1) * s)
            if dx * dx + dy * dy <= r * r:
                out.add((i, j))
    return out


def demand(speed, reach, s, height, seconds=20.0, hz=30.0):
    """Cells a second that come into reach as the eye moves at speed along a line at 30 degrees to the grid; reach is
    measured in 3D from an eye at height, so a high camera needs no near units at all."""
    r2 = reach * reach - height * height
    if r2 <= 0:
        return 0.0, 0
    r = math.sqrt(r2)
    dx, dy = math.cos(math.radians(30)), math.sin(math.radians(30))
    have = cells_in(0.0, 0.0, r, s)
    first = len(have)
    new = 0
    for k in range(1, int(seconds * hz) + 1):
        t = k / hz * speed
        now = cells_in(t * dx, t * dy, r, s)
        new += len(now - have)
        have = now
    return new / seconds, first


def main(argv):
    d = argv[0]
    opts = dict(zip(argv[1::2], argv[2::2]))
    plan = json.load(open(os.path.join(d, "district.json")))
    parts = [json.load(open(f)) for f in sorted(glob.glob(os.path.join(d, "parts", "part_*.json")))]
    chunks = [c for p in parts for c in p["chunks"]]
    sec = {}
    for p in parts:
        for k, v in p["seconds"].items():
            sec[k] = sec.get(k, 0.0) + v
    houses = sum(c["houses"] for c in chunks)
    l0_houses = sum(c["l0_houses"] for c in chunks)
    baked = sum(c.get("baked", 0) for c in chunks)
    empty = sum(c["empty"] for c in chunks)
    tris = [t for c in chunks for t in c["tris_each"]]
    size, core, unit = plan["size"], plan["core"], plan["chunk"]
    km2, core_km2 = (size / 1000) ** 2, (core / 1000) ** 2
    # streets: the rows, each across the district, and the cross streets every 160 m (scale_district.py)
    street_km = (len(plan["rows"]) * size + math.floor(size / 160.0) * size) / 1000.0
    total = sum(c["bytes"] for c in chunks)
    l0b = sum(c["l0_bytes"] for c in chunks)
    shb = sum(c["shell_bytes"] for c in chunks)
    grb = sum(c["ground_bytes"] for c in chunks)
    recb = sum(c["record_bytes"] for c in chunks)
    area = sum(c["area"] for c in chunks)
    l0_area = sum(c["l0_area"] for c in chunks)
    l0_tris = sum(c["l0_tris"] for c in chunks)
    core_chunks = [c for c in chunks if c["l0_houses"] > 0]
    MB = 1048576.0

    print("# The scale test: the district's numbers\n")
    print(f"From `{d}`: {size:.0f} m square ({km2:.2f} km²), {plan['plots']:,} plots in {len(chunks)} chunks of {unit:.0f} m; "
          f"{houses:,} houses built, {empty} plots empty in 1989; the core {core:.0f} m square ({core_km2:.2f} km²) at full detail "
          f"({l0_houses:,} houses), every house as a shell. About {len(plan['rows'])} streets across it and cross streets every "
          f"160 m: {street_km:.0f} km of street, so {houses / street_km:.0f} houses a kilometre (both sides).\n")

    print("## A house\n")
    print(f"Triangles a house at full detail (test quality): median {statistics.median(tris):,.0f}, 95th percentile {q(tris, .95):,.0f}, "
          f"worst {max(tris):,}; surface {area / houses:.0f} m² a house. The core holds {l0_tris:,} triangles at L0, "
          f"{l0_tris / core_km2 / 1e6:.1f} million a km² and {l0_tris / (core * core) * 16:,.0f} in a 4 m chunk on average.\n")

    print("## Generation (Blender's Python, one process)\n")
    per = lambda k, n: 1000 * sec.get(k, 0) / max(n, 1)
    print("| Stage | Seconds (all processes) | Milliseconds a house |\n| --- | --- | --- |")
    for k, n in (("resolve", houses + empty), ("build", houses), ("bake", baked), ("extract", houses), ("shell", houses)):
        print(f"| {k}{' (' + str(baked) + ' houses baked)' if k == 'bake' else ''} | {sec.get(k, 0):.0f} | {per(k, n):.1f} |")
    print(f"| ground (a chunk) | {sec.get('ground', 0):.0f} | {1000 * sec.get('ground', 0) / len(chunks):.1f} a chunk |")
    print(f"| write (a chunk) | {sec.get('write', 0):.0f} | {1000 * sec.get('write', 0) / len(chunks):.1f} a chunk |")
    print(f"| **all** | {sec.get('total', 0):.0f} | {1000 * sec.get('total', 0) / houses:.1f} |")
    cs = [c["seconds"] for c in core_chunks]
    os_ = [c["seconds"] for c in chunks if c["l0_houses"] == 0 and c["houses"] > 0]
    if cs:
        print(f"\nA core chunk ({unit:.0f} m, built, baked, at L0 and as shells) took {statistics.median(cs):.1f} s (95th {q(cs, .95):.1f} s); "
              f"one outside it (shells only, but every house still built) {statistics.median(os_):.1f} s.")
    if "--wall" in opts:
        w = float(opts["--wall"])
        n = int(opts.get("--processes", len(parts)))
        print(f"The whole district took {w:.0f} s of wall time in {n} processes: {houses / w:.1f} houses a second, "
              f"{km2 / (w / 3600):.1f} km² an hour.")
    print()

    print("## The cache\n")
    print("| What | Total (MB) | Per km² of its area (MB) | Per km of street (MB) |\n| --- | --- | --- | --- |")
    print(f"| L0 meshes (core only) | {l0b / MB:.0f} | {l0b / MB / core_km2:.0f} | {l0b / MB / (street_km * core_km2 / km2):.0f} |")
    print(f"| shells (every house) | {shb / MB:.0f} | {shb / MB / km2:.1f} | {shb / MB / street_km:.2f} |")
    print(f"| ground (2 m grid) | {grb / MB:.0f} | {grb / MB / km2:.1f} | {grb / MB / street_km:.2f} |")
    print(f"| records (the diaries, JSON) | {recb / MB:.1f} | {recb / MB / km2:.2f} | {recb / MB / street_km:.3f} |")
    print(f"| **chunk files** | {total / MB:.0f} | | |")
    print(f"\nL0 mesh is {l0b / max(sum(c['record_bytes'] for c in core_chunks), 1):,.0f} times its records' bytes: "
          f"{l0b / max(l0_houses, 1) / 1024:.0f} KB a house against {recb / max(houses, 1):.0f} bytes of diary.\n")
    print("Maps the core's surface would carry (four base pages at a byte a texel, BC7, mips a third more; packing waste 15 %):\n")
    print("| Texel | Per house (MB) | Per km² of town like the core (MB) | Per km of street (MB) |\n| --- | --- | --- | --- |")
    for cm in (2, 4, 8):
        b = l0_area / (cm / 100) ** 2 * 4 * 4 / 3 * 1.15
        print(f"| {cm} cm | {b / MB / max(l0_houses, 1):.1f} | {b / MB / core_km2:,.0f} | {b / MB / (street_km * core_km2 / km2):,.0f} |")
    print()

    s = None
    if "--summary" in opts:
        run = json.load(open(opts["--summary"]))
        s = run.get("district")
        b = run.get("bench")
    print("## Loading and building a chunk on the M4\n")
    fit = None
    if s and s.get("chunks"):
        ms, by, co = s["msEach"], s["bytesEach"], s["coreEach"]
        print(f"The player loaded {s['chunks']} chunk files ({s['fileBytes'] / MB:.0f} MB) in {s['loadSeconds']:.1f} s, "
              f"{s['mbPerSecond']:.0f} MB/s on the main thread: a chunk {s['chunkMs']['median']:.2f} ms (95th {s['chunkMs']['p95']:.2f}, "
              f"worst {s['chunkMs']['max']:.1f}), a core chunk {s['coreChunkMs']['median']:.1f} ms (95th {s['coreChunkMs']['p95']:.1f}); "
              f"reading the file {s['readMs']['median']:.2f} ms of it. Resident memory {s['rssBefore'] / MB:.0f} MB before, "
              f"{s['rssAfter'] / MB:.0f} MB after ({(s['vertexBytes'] + s['indexBytes']) / MB:.0f} MB of vertices and indices).")
        # time against bytes: a line through the chunks (least squares), the fixed cost and the rate
        n = len(ms)
        mx, my = sum(by) / n, sum(ms) / n
        sxx = sum((x - mx) ** 2 for x in by)
        k = sum((x - mx) * (y - my) for x, y in zip(by, ms)) / sxx if sxx else 0.0
        c0 = my - k * mx
        fit = (c0, k)
        print(f"A chunk's load time fits {c0:.2f} ms + {k * MB:.2f} ms a MB.\n")
    if s and b and b.get("vertices"):
        per100k = lambda v: v / b["triangles"] * 1e5
        print(f"Rebuilding {b['chunk']} ({b['triangles']:,} triangles in {b['parts']} parts): placing its parts took "
              f"{b['placeManagedMs']['median']:.1f} ms in plain C# and {b['placeBurstMs']['median']:.2f} ms as a Burst job "
              f"({per100k(b['placeManagedMs']['median']):.1f} and {per100k(b['placeBurstMs']['median']):.2f} ms a 100,000 triangles), "
              f"uploading it {b['uploadMs']['median']:.1f} ms. A {b['pageWidth']} by {b['pageHeight']} history page: drawn and waited "
              f"for {b['pageDrawMs']['median']:.2f} ms, read back {b['pageReadbackMs']['median']:.2f} ms, compressed on the CPU to "
              f"{b['pageFormat']} {b['pageCompressMs']['median']:.0f} ms ({b['pageCompressFastMs']['median']:.0f} ms fast).\n")

    print("## What the camera's movement asks for\n")
    print("Units a second coming into each level's reach (in 3D, from the eye), moving steadily across the grid; and the "
          "units within reach at once, which a jump (a map click, a cut) asks for in one go. Building blocks' reaches: L0 "
          "and L1 to 20 m, L2 to 80 m, L3 to 200 m, the streaming radius 300 m, L4 to 1.5 km.\n")
    head = "| Unit | Reach | " + " | ".join(m[0] for m in MOVES) + " | At once |"
    print(head)
    print("| --- | --- |" + " --- |" * (len(MOVES) + 1))
    rows = {}
    for name, s_, reach in UNITS:
        cells = []
        once = 0
        for mname, v, hgt in MOVES:
            rate, first = demand(v, reach, s_, hgt)
            rows[(name, mname)] = rate
            cells.append(f"{rate:.1f}")
            once = max(once, first) if hgt < 10 else once
        print(f"| {name} | {reach:.0f} m | " + " | ".join(cells) + f" | {once} |")
    print()
    if fit:
        c0, k = fit
        l0_per_m2 = l0b / (core * core)
        sh_per_m2 = (shb + grb) / (size * size)
        print("Main-thread time a second those rates cost, if each unit loads from the cache at the measured rate "
              f"({c0:.2f} ms + {k * MB:.2f} ms a MB), its bytes from the core's density ({l0_per_m2 * 16 / 1024:.0f} KB a 4 m chunk at L0, "
              f"{sh_per_m2 * 1024 / 1024:.0f} KB a 32 m cell of shells and ground):\n")
        print("| Unit | " + " | ".join(m[0] for m in MOVES) + " |\n| --- |" + " --- |" * len(MOVES))
        for name, s_, reach in UNITS:
            dens = l0_per_m2 if s_ == 4 else sh_per_m2
            ms_unit = c0 + k * dens * s_ * s_
            print(f"| {name} ({ms_unit:.2f} ms each) | " + " | ".join(f"{rows[(name, m[0])] * ms_unit:.1f}" for m in MOVES) + " |")
        print("\nAt 60 fps a frame has 1.5 ms for streaming (building blocks), 90 ms a second.")


if __name__ == "__main__":
    main(sys.argv[1:])
