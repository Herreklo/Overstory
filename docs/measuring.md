# Measuring

The tools every later change to the world is judged with: mesh hashes, the golden views, the frame-time harness and the motion sheets. They come before the building blocks (`docs/plan.md`, Monday), so the gully can be rebuilt on them and shown to be the same up close and cheaper at distance. They are built to be correct and repeatable first. Each was tested against the acceptance written for it (the harness meets its 3% on GPU time everywhere and on the frame in 22 of 24 segments), and the numbers below are today's baseline.

Numbers do the first pass, eyes the second (`CLAUDE.md`, Using tokens well). A change that alters a hash, a golden frame, a frame time or a shimmer score is found by the tools; a reviewer then looks where they point.

Everything runs on the reference machine (`docs/foundations.md`): the Mac mini with the M4, Unity 6000.6.6f1 in batch mode on `unity/` (the editor must not be open on it), Blender 5.2.2 in the background. Nothing here needs anything installed; what would make the tools better is at the end.

## Mesh hashes

**What it measures.** Whether an exported mesh is the same as before, and if not, which mesh and which channel changed. `blender/tools/mesh_hash.py` reads each FBX with Blender's own parser (never re-imported, so it hashes exactly what Unity reads) and hashes, per mesh: positions, corner indices with the polygon ends, edges, normals, every UV channel by its index and name, colours, smoothing, materials, any other layer, and the model's transform. Floats are hashed bit for bit (only minus zero is made plus zero); the file's header (its creation time) is left out, so two builds of the same thing hash the same. The hashes go into `mesh-hashes.json` beside the exports, one per folder, keyed by file name.

**How to run it.** `stone.py` and `wall.py` write the manifest after every export. By hand:

    blender -b --factory-startup --python blender/tools/mesh_hash.py -- write   <fbx> ...
    blender -b --factory-startup --python blender/tools/mesh_hash.py -- check   <fbx> ... [--manifest <json>]
    blender -b --factory-startup --python blender/tools/mesh_hash.py -- compare <fbx a> <fbx b>
    blender -b --factory-startup --python blender/tools/mesh_hash.py -- selftest <fbx> <scratch dir>

`check` exits 1 on any difference and names the mesh and the channels, with the vertex and triangle counts when they moved. Hashing the gully's two files takes about 1.5 s.

**Accepted (21 October).**
- The gully (stairs and cheek walls) built twice into scratch folders hashes the same: stairs `babe291de7a32bb1`, cheek walls `55e3f8fc8958493e`. Each build takes 72 s for the stairs and 71 s for the walls.
- A vertex moved by a tenth of a millimetre, exported through the generators' own FBX settings, changes that mesh's positions and normals and nothing else; the same file exported twice unchanged hashes the same (`selftest`).

**Baseline.** The manifests for the committed stone are in `unity/Assets/Art/Stone/mesh-hashes.json` and `Variety/mesh-hashes.json` (13 files). The gully's: stairs `91e31a9c9d6f7786` (361,282 triangles in two meshes), cheek walls `73020f2dc2ab1b3f` (454,924).

**What the hashes found.** The committed gully is not what its generators build.
- The stairs: built from the generators at their own commit (`200d596`) or at today's, they hash `babe291de7a32bb1`, not the committed `91e31a9c9d6f7786`. Most vertices sit up to 4.9 cm elsewhere (mean about 1 cm), and the face kinds (UV2), the bake (UV3), polish and lichen (UV4) and moss and water (UV5) differ; the grain and the years (UV0, UV1) are the same. The FBX on disk was written ten minutes before its commit; why it differs is not known (the code changed after the export, or something outside the commit did, such as Blender's version or a part's file), and two builds today agree with each other bit for bit.
- The cheek walls: at their own commit they rebuild exactly; since the door paths of `800085a` (a way to D now climbs to a point on the ways) one wall has 3,330 fewer triangles.

So the golden views below show the committed FBX, which no generator now makes. Before the gully is ported onto the building blocks (whose first rule is that the gully's geometry hash must not change), the gully should be exported again from today's generators, looked at, and its golden views accepted again.

## Golden views and player-size stills

**What it measures.** Whether a change altered what the player sees of the gully, where, and by how much. `LT1Golden.Views` stages the gully exactly as `LT1Stone.Frames` does (the same staging, views and aim, now shared, with frames byte-identical before and after the sharing) and renders it at the judging views:
- eye level at the foot of the steps (`eye-foot`) and on them (`eye-on`);
- the street stop at about 2.8 m (`street`);
- 12 m up beside the flight, looking along the lane (`into12`);
- the city camera, pulled out and steep (`high`);

in the three lights (`1300-drizzle`, `1600-low-sun`, `1750-blue-hour`). Every frame is rendered as the player sees it (`PlayerFrame`): 2560 by 1440, one sample a pixel with the game's own antialiasing (the pipeline's MSAA 4x), after the stills' eight warm-up renders, read back exactly. Never larger and averaged down: that hid shimmer and put footprint fades at one and a half times the distance the player sees them (`docs/research/painted-marks-in-motion.md`).

`blender/tools/golden_compare.py` compares each frame with its baseline by a perceptual difference after NVIDIA's FLIP, written in numpy because FLIP is not installed: the frames in an opponent colour space filtered by FLIP's contrast-sensitivity kernels, the Hunt-adjusted HyAB colour distance, and FLIP's edge and point features on luminance, combined as FLIP combines them, at the pixels a degree of the reference player's screen (a 27-inch 1440p monitor at 70 cm: 52.4). It is an approximation, not checked pixel for pixel against NVIDIA's tool, so its numbers are FLIP-like. Per frame it writes a heat map on FLIP's scale (magma, black to pale yellow), the same amplified ten times, and a strip of baseline, test and both maps; per folder a sheet; and a report with the mean, the 99.9th percentile, the worst pixel and how many pixels changed at all.

**The threshold.** A frame passes when its mean is at most 0.0005 and its worst pixel at most 0.05. The noise floor is zero (below), so the threshold is set by what a real change scores, not by noise; it can be tightened.

**How to run it.**

    tools/golden.sh [-moments 1600 -views street,high]

renders into `reviews/golden/current/` (about 15 s for all fifteen frames) and compares into `reviews/golden/compare/` (about 10 s), both kept out of git, and exits 1 if a frame fails. A partial render compares only the frames it made. To accept a new baseline (only Øystein accepts one; the AI proposes it with its sheet):

    blender -b --factory-startup --python blender/tools/golden_compare.py -- accept reviews/golden/current reviews/golden/baseline

**Accepted (21 October).**
- Rendered twice, all fifteen frames are bit-identical: no pixel differs.
- A test-only change, the slate's weathered colour a shade warmer on the stair (`LT1Golden.Views -tweak`, in memory, never saved), fails every frame: mean 0.001 (the street stop, where the stair is small) to 0.014 (on the steps), worst pixel 0.08 to 0.15. The heat maps show it on the stair's stones and nowhere else, not on the cheek walls or the clay.
- The metric's own test (`golden_compare.py -- selftest`): identical images score zero everywhere, a small patch of changed colour scores inside the patch and nowhere far from it, and a larger change scores higher.

**Baseline.** `reviews/golden/baseline/gully/<light>/<view>.png`, fifteen frames, 44 MB, with `frames.json` (size, MSAA, warm-up, Unity version, GPU). They are in plain git: Git LFS is not installed on this machine, and `.gitattributes` keeps renders out of it because LFS uploads cannot be reached from the cloud workspace.

## The frame-time harness

**What it measures.** What the corner costs to draw on the reference machine, in a built player (never the editor, which draws at a different speed), at the player's size, for every judging view in every light. `Overstory.Perf.PerfRunner` (runtime code) holds each view and records:
- *offscreen:* the view drawn into a 2560 by 1440 target with the game's MSAA, six at a time back to back with the GPU kept busy, the wall time a frame. It is the cost of drawing the view, free of the display's cadence, and the steadiest number: the one to compare in an A/B;
- *frame:* the presented frame's period (FrameTimingManager's CPU frame time, which includes waiting for the GPU and the screen): what the player gets. macOS presents on the display's refresh even with vsync off, so it comes in whole ticks (6.9 ms on the 144 Hz screen here);
- *GPU:* the GPU's own time a presented frame. On Apple's tile GPU the passes of successive frames overlap, so it can exceed the frame's period; compare it with itself, not with the frame;
- the main and render threads' time, the triangles, draw calls, SetPass calls and shadow casters of the median frame, every pass included (a release player keeps no batch count), and the memory in use.

`LT1Perf.Build` composes the corner as the gully's frames stage it (`LT1Stone.Stage`: the heart in clay, the stair and its cheek walls in stone) and plants the corner's birch where `docs/experiments.md` has it, in C's yard by the lower flight. It is the judged downy birch at 60 (seed 1, 16.7 m), older and taller than the fact's birch of about 40 years and 14 m, so its cost is an upper bound. The scene is saved as a generated scene (out of git) with the runner, and built as a macOS player with frame timing stats on; the player settings changed for the build are put back after it. The segments: the five golden views and the birch's own view (`birch12`, its crown filling the frame from 12 m), in each light, and the six again in low sun without the birch (the A/B), 24 in all. Each is measured twice, in two rounds one after the other (150 presented frames after 30 to warm up, and six batches of six offscreen frames), after 600 frames to let the machine settle; a screenshot of each is taken after all the measuring.

**How to run it.**

    tools/perf.sh [-runs 2] [-perf-only street,high] [-perf-frames 150] [-perf-rounds 2]

composes, builds (about 6 minutes the first time, seconds after) and runs the player full screen at 2560 by 1440, about 11 minutes a run. Each run writes `reviews/perf/<date>/run-<n>/summary.json` and `summary.md`, with every frame in `frames.csv`, the screenshots and the player's log beside them (out of git); `runs.md` says how far the day's complete runs agree. The player takes the screen: leave the machine alone while it runs. The first attempt stopped part way (why is not known: a key, or another app taking the screen); a run that stops writes no summary and is left out of the comparison. A build rewrites some settings as housekeeping (URP's stripping prefilters, the default volume profile's list of overrides, the graphics settings' warm-up fields); `tools/perf.sh` puts back those that were clean before, so a run leaves git as it found it, and the golden views render bit-identical after it.

**Accepted (21 October).** Two runs (`reviews/perf/2026-10-21/runs.md`):
- the GPU time agrees within 3.1% in all 24 segments;
- the frame agrees within 3% in 22 of 24; the other two (on the steps and 12 m up, in drizzle) differ by 5.0 and 5.2%, their medians sitting between two refresh ticks;
- offscreen agrees within 3% in 22 of 24; the other two (at the foot of the steps in drizzle and the blue hour) by 4.0 and 6.9%;
- in low sun, the heaviest load, all three agree within 1.5% in every segment. The lighter the load, the more the M4's clocks wander, so the light views vary most.

Earlier runs, measuring each segment once and then in rounds without the offscreen batches, disagreed by up to 8 to 10% on the frame and 7.5% on GPU time. With the offscreen batches in every segment, which keep the GPU busy, they agree as above; how much of that is the method and how much a quieter machine is not yet known, and more runs will tell. Other apps open on the machine (the Unity editor on another project, Blender, the Claude app) are part of the noise. The player draws what the golden views show: its street stop in low sun without the birch is within three 8-bit levels of the golden still in 92% of pixels (about a level darker on average), the rest at edges.

**Baseline** (21 October, run 1; run 2 within the spreads above):

| Light | Offscreen (ms) | Frame (ms) | Frames a second | Triangles a frame | Draw calls | Shadow casters |
| --- | --- | --- | --- | --- | --- | --- |
| Drizzle | 33.5 to 50.4 | 28.0 to 42.3 | 24 to 36 | 13.8 to 15.5 million | 130 to 143 | 54 to 67 |
| Low sun | 97.8 to 113.4 | 84.0 to 96.3 | 10 to 12 | 13.8 to 15.9 million | 131 to 147 | 54 to 70 |
| Blue hour | 27.2 to 40.1 | 25.3 to 34.8 | 29 to 40 | 5.5 million | 76 | 0 |

Memory in use: 231 to 234 MB. The main thread takes about a millisecond: the corner is bound by the GPU.

The birch, in low sun (offscreen, with and without it):

| View | With (ms) | Without (ms) | The birch |
| --- | --- | --- | --- |
| eye level, at the foot | 97.8 | 95.7 | +2.1 (out of view; its shadow) |
| eye level, on the steps | 102.1 | 101.7 | +0.4 (out of view) |
| the street stop | 102.0 | 89.3 | +12.7 |
| 12 m along the lane | 101.2 | 91.4 | +9.8 |
| the city camera | 105.3 | 89.5 | +15.9 |
| its crown filling the frame | 113.4 | 88.8 | +24.6 |

It adds about 507,000 triangles a frame over every pass, 14 draw calls and 8 shadow casters.

What the baseline says, for the building blocks:
- Against 60 frames a second at 1440p (16.7 ms), today's corner is one and a half to two and a half times over in drizzle and the blue hour, and five to six times over in low sun.
- A frame holds about 15 million triangles with the sun's shadows and 5.5 million without them: the four shadow cascades draw the town about twice more. The foundations' budget is 2 million visible.
- Low sun costs about two and a half times drizzle on the same triangles, so something drawn only in low sun costs about 55 to 65 ms. The sun's beams and light shafts are the suspects; it is the first A/B switch to add.
- The birch, one tree, costs 10 to 16 ms wherever it is in view (an eighth to a sixth of the frame) and 25 ms where its crown fills the frame (a fifth): the dearest thing on screen, as the ground cover study estimated.

## Motion sheets and the shimmer measure

**What it measures.** How the gully looks moving, as the player sees it, and how much its fine detail shimmers. `LT1Motion.Sheets` stages the gully as the golden views do and renders it along four camera paths at 60 frames a second, every frame a `PlayerFrame` (2560 by 1440, one sample a pixel, the game's MSAA 4x), one render a frame as the game draws, written as a PNG sequence:
- *still:* the street stop held for a second, to catch anything that moves when nothing should;
- *walk:* a person walking past the foot of the steps at 1.4 m/s for 2.5 s, eye at 1.7 m, head turned to the steps;
- *pan:* the street stop turning at 5 degrees a second for 3 s;
- *crane:* rising from the street stop (2.8 m) to 12 m over the lane in 3 s, eased in and out.

The world's clock is the light's own, so the world holds still and only the camera moves. Low sun by default (`-moments` for the others); `-birch` plants the corner's birch; `-nodither` turns the camera's dithering off, in memory; `-test crawl|smooth` stands the measure's known case on the first steps (below).

`blender/tools/motion_measure.py` measures each sequence. For each pair of consecutive frames it takes the luma (Rec. 709 weights on the sRGB values, in 8-bit levels), their difference, and the fine part of that difference (less its own Gaussian blur of 1.5 px): what changed at the scale of a pixel or two, where shimmer, crawl and popping live. The *shimmer* is that fine change's mean magnitude in levels; the *flicker* is the share of pixels whose fine change is over 3 levels. Per sequence: their mean, median and worst pair, and a sheet of the first frame beside a map of where the fine change gathers (2 levels at the top of the scale). A moving camera moves every edge, so a moving path never measures zero: compare the same path before and after a change, never two paths. The swim test, which tells a sliding mark from an aliasing one, is still to come.

**How to run it.**

    tools/motion.sh [-paths still,walk] [-moments 1300-drizzle] [-nodither] [-birch] [-test crawl]

renders into `reviews/motion/current/<light>/<path>/` (out of git; about 4 MB a frame, 1.6 GB for the four paths, about 2.5 minutes) and measures into `reviews/motion/<date>/` (`shimmer.md`, `shimmer.json` and a sheet per sequence; a sequence measured again replaces its row). Measuring takes about 20 s a hundred frames.

**Accepted (21 October).**
- *The still camera.* With the camera's dithering off, every frame of the still is bit-identical: shimmer 0.0000, flicker 0. With the game's dithering on, as the player sees it, it measures 0.47 levels and 0.15% of pixels flicker by more than 3 levels in every frame: URP draws its dither as a fresh noise each frame, the only thing on screen that moves when nothing should. Whether the camera keeps its dithering is a look question (it hides banding in the sky, and it boils the whole frame by about a level; the research's advice is that nothing that stands boils).
- *A known crawl.* A board of 1 mm squares on the first steps, about half a pixel each from the walk: sampled without mips it aliases into a moire that crawls, and the walk measures 3.97 levels and 10.7% flicker; the same board with trilinear mips measures 1.17 and 7.1%, the same as the walk without any board. Held still, both measure as the still camera does. The measure's own test (`motion_measure.py -- selftest`): a still sequence measures zero; a pattern finer than a pixel, unfiltered and moving a third of a pixel a frame, measures 112 levels, the same pattern filtered to the pixel 4.7, a coarse pattern moving as fast 0.55.

**Baseline** (the gully in low sun, `reviews/motion/2026-10-21/shimmer.md`):

| Path | Shimmer (levels) | Flicker | Without dithering: shimmer | Flicker |
| --- | --- | --- | --- | --- |
| still | 0.47 | 0.15% | 0.00 | 0.00% |
| walk | 1.17 | 7.2% | 0.86 | 6.7% |
| pan | 1.02 | 4.4% | 0.68 | 4.1% |
| crane | 1.05 | 4.7% | 0.71 | 4.4% |

## What would make the tools better

Nothing was installed for these tools. These would make them better, each with its source:
- **NVIDIA FLIP** (`pip install flip-evaluator`, from github.com/NVlabs/flip, BSD-3-Clause): the reference metric, first to check `golden_compare.py`'s approximation against it pixel for pixel, then to replace it.
- **ffmpeg** (`brew install ffmpeg`, from ffmpeg.org): to turn the motion sheets' PNG sequences into 60 fps video Øystein can watch, and to keep a sequence in a fraction of the space (ProRes or lossless H.264 for judging).
- **Git LFS** (`brew install git-lfs`, from git-lfs.com): `CLAUDE.md` asks for large binaries in LFS, but `.gitattributes` keeps renders out of it because the cloud workspace cannot reach LFS uploads. Whether the golden baselines (44 MB a set) move to LFS is Øystein's call.

## Still to come

- **The swim test** (`docs/research/painted-marks-in-motion.md`, Look tests, 2): each frame warped onto the next by its motion vectors and what is left measured, so a mark that slides on its surface is told from one that only aliases. It needs depth or motion vectors written beside each frame of a motion sheet.
- **The harness's switches** (`docs/research/performance-at-scale.md`, The performance harness, 5): the Resident Drawer and GPU occlusion, MSAA against none, the shadows' reach and cascades, the sun's beams, a forced level per kind. Each is an A/B on the same segments, as the birch already is.
- **Hashes from every generator.** `stone.py` and `wall.py` write them; the trees, the houses and the clay should too as they are ported onto the building blocks.
- **Golden views of more than the gully**, as each kind joins: the birch, the corner's houses, the clay heart from its stops.
