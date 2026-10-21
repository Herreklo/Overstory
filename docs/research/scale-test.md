# The scale test

What does the town cost at city scale on the reference machine, and what does that say about where generation runs and how the town streams? A district 2 km across was built from the test-quality house generator on the clay ground. It was drawn in a built player with the corner's real shaders and measured on the M4 Mac mini at 1440p (21 and 22 October). The plan asked for it (`docs/plan.md`, Tuesday), and it settles or sharpens what `docs/building-blocks.md` leaves open until measured. Raw numbers: `reviews/perf/2026-10-22/district/` (`scale-report.md`, `run-1/summary.md`) and `district-memory/`.

## In short

- **Scale adds no new failure to the frame.**
  - With L0 within 200 m of the eye and shells beyond, the district draws in 21 to 25 ms in the blue hour at the street stop, 12 m and the city camera. Drizzle and low sun (beams off) take 27 to 31 ms.
  - That is the same per-pixel floor the pass budget found in the corner (`docs/measuring.md`, The pass budget), and its fixes carry the city.
  - The levels matter: L0 everywhere in the core doubles the city camera, to 46 to 55 ms with 15 million triangles.
- **Sun beams cost the city what they cost the corner:** about 59 ms in low sun, whatever is drawn.
- **Near levels are built on demand; only records, coarse levels and the heart ship.**
  - At test quality, L0 is 708 KB a house: 2.1 GB a km² of town like the core. That is 2,300 times the record of 315 bytes a house.
  - Shipping L0 would cost a metropolis hundreds of gigabytes. Shells (1.6 MB a km²) and the ground can ship.
  - Demand allows building near levels: walking asks for 4 4-metre chunks a second, driving 40.
  - Placing a chunk's parts costs 0.7 ms per 100,000 triangles in a Burst job.
- **Burst is required.** The same placement takes 13 times longer in plain C# under Mono (9.1 ms per 100,000 triangles). IL2CPP is not installed, so the player is Mono.
- **Streaming must leave the main thread and batch its files.**
  - Each file costs 0.28 ms plus 0.63 ms a MB on the main thread. A core chunk (64 m, 8.8 MB) takes 5.6 ms, nearly four frames' streaming budget.
  - The city camera panning at 300 m/s asks for about 190 units a second: 84 ms of main thread a second, 93% of the budget.
- **History maps are about eight times the architecture's disk line if every outer face carries them.**
  - A house's envelope is 444 m² (walls and roof, from the shells). The disk estimate assumed about 56 m², its street front.
  - At 4 cm, every face mapped is 1.7 MB a house, 425 MB a km of street and 1.45 GB resident in the 300 m radius, against a 0.8 GB pool.
- **History pages must be compressed on the GPU.** Compressing a 1024 by 512 page on the CPU takes 5 to 9 ms (DXT5, as `Texture2D.Compress` offers no BC7). That is three to six frames' streaming budget.
- **Memory is the system's count, not Unity's.**
  - Unity's own counter says 246 MB. The system counts 1.4 GB for the corner's player, plus 0.9 GB for the district's 0.74 GB of meshes: 2.6 GB at the end. That is inside the 6 GB budget, with no maps, people, library parts or textures for the district yet.
- **Generation offline is cheap.** In Blender's Python on 8 processes, the district took 222 s: 68 km² an hour, 38 houses a second. The bake is the dear stage: 0.6 to 0.9 s a house, ten times the build.

## What was built

`blender/tools/scale_district.py`:
- A 2,048 m square (4.2 km²) of streets on the clay ground's slopes: 34 rows 52 m apart in the dense middle and 76 m apart outside, and cross streets every 160 m. That is 94 km of street.
- 8,960 plots, 6 to 12 m wide, 1 to 3 m apart in the dense middle and 5 to 12 m outside. Warehouses are 7 to 10 m wide.
- Each plot's diary is resolved at 1989 by the test-quality house generator (`building.py`). 8,519 houses stand and 441 plots are empty.
- The core, 512 m square in the middle (789 houses), is kept at full detail (L0) with every house baked. Every house also has a shell: a box to the eave and a gable, 14 triangles.
- The ground is a 2 m grid with setts on the streets.
- Everything is cut into 1,024 chunks of 64 m in a little binary format (OSCK v1: 24-byte vertices of position, snorm8 normal, unorm8 colour and half UV), with each chunk's records beside it.

A house at test quality has a median of 10,800 triangles (95th percentile 21,400). Density is 2,000 houses a km² over the district and 3,000 in the core.

The player (`DistrictLoader`, `DistrictBench`, `PerfRunner`) loads every chunk at start, one after another, timing each. It draws the district in the corner's street shader (`M_Street.mat`), with every pass of the corner's pipeline, in three arrangements:
- *near*: L0 within 200 m of the eye, shells beyond: what the game would draw;
- *l0*: the whole core at L0: the worst case for triangles;
- *shells*: no L0 at all.

The views are:
- the street stop on the central street;
- 12 m up;
- the corner's near-isometric high view;
- the city camera, 150 m up looking 35 degrees down;
- *over*, the whole district from low over its edge, with everything in the frame.

Each view was drawn in the three lights, with every pass on and with the beams off.

## Frame time

Offscreen ms, the median (95th percentiles within 4%); the beams off, as their rewrite will leave them at about 0.5 ms.

| View | Near, blue hour | Near, drizzle | Near, low sun | L0 everywhere, blue hour | Shells only, blue hour |
| --- | --- | --- | --- | --- | --- |
| Street stop | 20.8 | 26.5 | 28.8 | 26.1 | 15.0 |
| 12 m | 23.0 | 28.8 | 30.4 | 28.6 | 16.2 |
| High | 14.5 | 18.1 | 18.0 | 14.4 | 12.6 |
| City camera | 25.0 | 30.5 | 29.9 | 45.5 | 19.3 |
| Over (everything) | 28.9 | 29.7 | 29.5 | 46.0 | 29.3 |

- *Triangles a frame*, every pass included: 3.9 to 9.1 million near, 8 to 21.5 million with L0 everywhere, and 1 to 3.2 million as shells.
- *Draws*: about 1,000 at the street stop and city camera, and 2,900 over everything.
- *The main thread*: 0.4 to 0.7 ms, and 1.1 to 1.4 ms at 2,900 draws. Draw calls are not the limit; the 3,000-draw ceiling holds without the Resident Drawer.
- *With the beams on in low sun*: 70 to 119 ms. The beams cost about 59 ms in every view.

What it says:
- **The per-pixel floor is the frame.** With shells only, the street stop costs 15 ms with a million triangles, against 9 ms for the corner's empty frame in the same light. At the over view the ground and the shells alone cost 29 ms.
- **L0 is the triangle risk.** L0 for the whole core adds 20 ms at the city camera (15 million triangles against 3.7). Levels by distance are needed as designed. The near arrangement's 3.9 million in the blue hour is about 2 million drawn twice (the depth prepass), the building blocks' ceiling.
- **The ground needs levels too.** A flat 2 m grid is 2.1 million triangles and 37 MB a km², the largest cache item after L0.

## Memory

The system's physical footprint (`footprint`, which counts the GPU's buffers on Apple's unified memory):
- the corner's player, before the district: 1.4 GB;
- after loading the district's 742 MB of vertices and indices: 2.3 GB (+0.87 GB, about 1.18 times the mesh bytes);
- at the end of the run, after every view has drawn: 2.6 GB.

The process's resident size grew only 0.29 GB, and Unity's "total used" counter stayed at 246 MB. Neither sees GPU memory, so the harness's memory column (`docs/measuring.md`) undercounts by a factor of about ten. Memory budgets must be checked by footprint.

At test quality, the core's L0 is 546 MB for 0.26 km². Within the 300 m streaming radius at core density (about 850 houses), L0 for every house would be 600 MB. L0 only reaches 20 m, and a house is about 1 KB as a shell, so geometry fits its 1 GB pool with levels. Final-quality houses are heavier and unknown until House A.

Blender's peak was 0.6 to 0.7 GB a process.

## Disk and the cache

| What | Total | Per km² | Per km of street |
| --- | --- | --- | --- |
| L0 meshes (the core) | 546 MB | 2.1 GB | 93 MB |
| Shells (every house) | 7 MB | 1.6 MB | 0.07 MB |
| Ground, 2 m grid | 156 MB | 37 MB | 1.7 MB |
| Records (the diaries) | 2.6 MB | 0.6 MB | 0.03 MB |

L0 is 708 KB a house. Its vertices are not shared, because the faces are flat (24 bytes each). That is 2,300 times the house's record.

**Maps.** The architecture's disk line (`docs/building-blocks.md`, Disk per kilometre: 13 to 51 MB of pages a km at 8 to 4 cm) works out to about 56 m² of mapped surface a house, its street front. The envelope measured from the shells is 444 m² a house. The surface of every triangle is 1,563 m², which counts every board's back and edges.

Four base pages at a byte a texel with mips and 15% packing waste, over the whole envelope, come to this:

| Texel | A house | Per km of street (250 houses) | Per km² (core density) | Resident, the 300 m radius (850 houses) |
| --- | --- | --- | --- | --- |
| 2 cm | 6.8 MB | 1.7 GB | 20.5 GB | 5.8 GB |
| 4 cm | 1.7 MB | 425 MB | 5.1 GB | 1.45 GB |
| 8 cm | 0.43 MB | 106 MB | 1.3 GB | 0.36 GB |

So, against the 0.8 GB pool, every outer face cannot carry pages at street-front density. Either fronts are mapped finely and sides, backs and roofs coarsely (16 cm, or the vertex colour alone), or pages stream by distance. The disk line grows about eight times if not.

## Generation

In Blender's Python on the M4 (`scale-report.md`):

| Stage | A house, alone | A house, 8 processes at once |
| --- | --- | --- |
| Resolve the diary at 1989 | 0.2 ms | 0.2 ms |
| Build (`building.py`) | 64 ms | 95 ms |
| Bake (`bake.py`, ray fans) | 0.6 s | 0.93 s |
| Extract, shell, write | 7 ms | 7 ms |

The whole district took 222 s of wall time in 8 processes (1,611 s of process time). A core chunk took 12 s, and a chunk outside it 0.7 s. Run in parallel, a house costs half as much again: the M4 has 4 performance and 6 efficiency cores.

## Loading and rebuilding a chunk in the player

On the main thread of the built player (Mono):
- A chunk file is read and uploaded through `MeshData` in 0.28 ms plus 0.63 ms a MB. The whole district loads in 0.7 s, 960 MB/s, from a warm file cache (the files were written minutes before).
- A core chunk (64 m, about 11 houses, 8.8 MB) takes 5.6 ms (95th percentile 9.1 ms).
- An outer chunk (shells and ground, 165 KB) takes 0.3 ms.

Rebuilding the largest chunk (265,000 triangles, cut into 1,384 parts of 400 vertices, each placed through its transform; the generator places judged parts and invents no geometry):
- placing in plain C# (Mono): 24.2 ms, which is 9.1 ms per 100,000 triangles;
- placing as a Burst job: 1.8 ms, which is 0.68 ms per 100,000 triangles (13 times faster);
- uploading through `MeshData`: 1.6 ms (p95 2.2).

A history page of 1024 by 512 (a blit stands in for the bake's shader):
- drawn: 0.7 ms;
- read back: 0.7 ms;
- compressed on the CPU to DXT5: 8.7 ms, or 5.3 ms in the fast mode.

The architecture's 2 ms of GPU a page needs the compression on the GPU, which nothing in the project does yet.

## What the camera's movement asks for

Units coming into each level's reach each second, moving steadily (`tools/scale_report.py`; reaches from `docs/building-blocks.md`). The last column is the units within reach at once, which a jump asks for in one go.

| Unit | Walk 1.4 m/s | Drive 14 m/s | City camera, 300 m/s pan at 150 m | At once |
| --- | --- | --- | --- | --- |
| L0 and L1, 4 m chunks, to 20 m | 4.3 | 40 | 0 | 88 |
| L3 shells, 32 m cells, to 200 m | 0.6 | 6 | 90 | 148 |
| Streaming chunks, 64 m, to 300 m | 0.2 | 2.3 | 45 | 88 |
| L4 blocks, 128 m, to 1.5 km | 0 | 2.6 | 58 | 484 |

At the measured load rate, at core density:
- walking costs 1.7 ms of main thread a second;
- driving costs 17 ms a second;
- the city camera's pan costs 84 ms a second.

The building blocks allow 1.5 ms a frame, 90 ms a second. A jump's first view (88 near chunks, 148 cells, 88 streaming chunks, 484 blocks) is about 0.4 s of main thread, behind the dated card.

## What it means

**Where generation runs.**
- `docs/research/where-generation-runs.md` holds: parts are made offline, and the town is assembled in the player, in C# with Burst.
- Placement is cheap enough to rebuild a chunk in a frame's worth of worker time (a final-quality stair chunk of 100,000 triangles in about 0.7 ms).
- What is not yet known is the bake, today 0.6 s a house in Python. It is ten times the build, and the stage to port and measure first: on the GPU, or as a Burst job, behind the change.

**The shipped cache.**
- The heart's start date can ship (0.55 GB of L0 at test quality, plus its pages).
- City-wide, the shipped world is the records, the libraries and the coarse levels (shells, ground and L4: a few MB a km²).
- Near levels are built on demand from the record as the camera comes. The demand rates allow it at walking and driving speed.

**How the town streams.**
- Files are read on worker threads (`AsyncReadManager` into native arrays), so the main thread keeps only `ApplyAndDisposeWritableMeshData` and renderer changes.
- A 64 m chunk's upload is split across frames when it is over budget.
- Small units are packed together: one file a 128 m block holding its shells and L4, so the per-file 0.28 ms is paid once a block, not once a cell.
- The city camera's pan then fits its budget.

**Unit sizes.**
- 4 m stays the unit a change rebuilds: a stair's 4 m holds 100,000 triangles at final quality.
- A test-quality house's 4 m holds about 560 triangles (34 KB), too little to be its own file or renderer. Houses are loaded and drawn by the 64 m chunk, or by a 16 m group, and rebuilt by 4 m.

**Maps.**
- The texel follows what the camera sees: the street front and the ground floor fine; sides, backs and roofs coarse.
- Pages are compressed on the GPU.

## What changes in the architecture

For the main session to weigh; `docs/building-blocks.md` is not this study's to change.

1. *Disk per kilometre and map density*: the page estimate assumes about 56 m² a house; the envelope is 444. Set a texel per face kind (front, side and back, roof), or the disk line and the 0.8 GB pool grow about eight times.
2. *Shipped cache against on demand*: settled as records, libraries and coarse levels shipped city-wide; near levels on demand; the heart's start date shipped as the exception. Shipping L0 does not scale (2.1 GB a km² at test quality).
3. *Streaming a frame*: reads on workers, uploads split, small units packed into block files. As measured, a core chunk's load is 5.6 ms on the main thread, and the city camera's pan uses 93% of the streaming budget.
4. *Map rebake cost*: GPU compression is required, not preferred. A GPU BC7 (or BC1/BC4) encoder is a missing piece.
5. *Burst* is required for rebuilds in play (13 times plain C#). IL2CPP is not installed; whether it is wanted is open.
6. *Memory* is measured by the system's footprint. The harness's Unity counter misses GPU memory, about nine tenths of it.
7. *The ground* gets levels: a heightfield far off, not a flat 2 m grid everywhere.

## Limits

- **Houses at test quality.** They are flat-shaded and unshared, with no library parts, maps, textures, people, trees or lamps. Final quality is unknown until House A.
- **Warm file cache.** The district was loaded straight after it was written, so 960 MB/s is a warm-cache rate. A cold SSD read is slower but runs on workers.
- **The bench's page is a blit,** not the bake's shader; its draw time is a floor.
- **Mono, not IL2CPP**, in the player.
- **No Resident Drawer or GPU occlusion:** plain renderers, a chunk's three meshes each.
- **The origin was not rebased:** positions run to 2 km in Unity's float coordinates (0.24 mm steps). The rebase at 2 km is untested.
- **One machine, one run.** The harness's spread is within 3% (`docs/measuring.md`).

## How to run it

    blender -b --factory-startup --python blender/tools/scale_district.py -- blender/cache/scale-district --part <i>/8 --bake 1   # eight at once, about 4 minutes
    tools/perf.sh -runs 1 -out reviews/perf/<date>/district -district <absolute path to blender/cache/scale-district> \
        -perf-scenes district-near,district-l0,district-shells -perf-passes all,-beams -perf-frames 40 -perf-warmup 15 -perf-rounds 2 -perf-shots some
    python3 tools/scale_report.py blender/cache/scale-district --summary reviews/perf/<date>/district/run-1/summary.json --wall <s> --processes 8

The player run takes about 11 minutes; the district's chunks (708 MB) stay in `blender/cache/`, out of git. `-perf-district-views street,city` keeps some views. `--box i0,j0,i1,j1` builds a few chunks for a quick sample.
