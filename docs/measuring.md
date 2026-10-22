# Measuring

The tools every later change to the world is judged with: mesh hashes, the golden views, the frame-time harness and the motion sheets. They come before the building blocks (`docs/plan.md`, Monday), so the gully can be rebuilt on them and shown to be the same up close and cheaper at distance. They are built to be correct and repeatable first. Each was tested against the acceptance written for it (the harness meets its 3% on GPU time everywhere and on the frame in 22 of 24 segments), and the numbers below are today's baseline.

Numbers do the first pass, eyes the second (`CLAUDE.md`, Using tokens well). A change that alters a hash, a golden frame, a frame time or a shimmer score is found by the tools; a reviewer then looks where they point.

Everything runs on the reference machine (`docs/foundations.md`): the Mac mini with the M4, Unity 6000.6.6f1 in batch mode on `unity/`, one job at a time through the Unity lock (`tools/unity_lock.py`; the unity-conventions skill, Using Unity), which waits while the editor or another job has it open, Blender 5.2.2 in the background. Nothing here needs anything installed; what would make the tools better is at the end.

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

**Baseline** (22 October). The manifests for the committed stone are in `unity/Assets/Art/Stone/mesh-hashes.json` and `Variety/mesh-hashes.json` (13 files). The gully's, exported from today's generators: stairs `babe291de7a32bb1` (361,282 triangles in two meshes), cheek walls `55e3f8fc8958493e` (451,594). Until 21 October the committed gully hashed stairs `91e31a9c9d6f7786` and walls `73020f2dc2ab1b3f` (454,924), which no generator made (below).

**What the hashes found** (21 October). The committed gully was not what its generators build.
- The stairs: built from the generators at their own commit (`200d596`) or at today's, they hash `babe291de7a32bb1`, not the committed `91e31a9c9d6f7786`. Most vertices sit up to 4.9 cm elsewhere (mean about 1 cm), and the face kinds (UV2), the bake (UV3), polish and lichen (UV4) and moss and water (UV5) differ; the grain and the years (UV0, UV1) are the same. The FBX on disk was written ten minutes before its commit; why it differs is not known (the code changed after the export, or something outside the commit did, such as Blender's version or a part's file), and two builds today agree with each other bit for bit.
- The cheek walls: at their own commit they rebuild exactly; since the door paths of `800085a` (a way to D now climbs to a point on the ways) one wall has 3,330 fewer triangles.

So on 22 October the gully was exported again from today's generators (two builds bit for bit the same), its golden views rendered and looked at, and both accepted as the baseline (Golden views, Baseline). The port's first rule, that the gully's geometry hash must not change, is measured against these hashes.

**Accepted by Øystein (22 October),** as the regression reference only: it shows the port changes nothing, not that the look is right. The look is judged against the target frame (`reviews/lt1/heart/target/3-street-gully-steps-target.png`) and the bar, beside the render (Øystein: "not sure if the before version is the right thing to compare it against"). Step 0b: seeds on the hash spec. The gully re-draws because of three changes:
- since `dbd455c`, the generators draw every seed from stable ids (`schemas/naming.md`) through `blender/resolver/hashing.py`;
- since `13e1b3b`, the set-out keeps its rests;
- since `7c5086c` and `21ec5df`, the cheek walls are built from the ground's facts.

The builds:
- Three builds hash the same: two in scratch folders and one in the project. Every array Unity reads is bit for bit identical, and so are the side files. The FBX bytes differ only in the header's creation time and in the object ids Blender's exporter makes from Python's salted `hash()`. The mesh hash leaves both out by design.
- The new hashes:
  - stairs `bff7858b698f3efd` (354,126 triangles; the lower flight has 30 steps and one rest of 1.30 m);
  - cheek walls `0a3d7db3100df20b` (607,872 triangles, 35 % more than 451,594).
- A wall's role is now the ground's alone, with no seed in it. A wall retains where the bank behind it stands more than 0.5 m over the lane's grade, along stretches of at least 2 m. In today's clay no stretch qualifies, so all four walls stand as parapets at hand height, with a back face built above the bank. The upper left wall's change from retaining to parapet is a valid draw from the facts, not a seeding artefact.
- The added triangles are those backs, the closed ends (about 15,000) and the hearting behind fallen stones.
- The tracked FBX and `mesh-hashes.json` hold this build, so the committed generators reproduce them. Until it is accepted, `zsh tools/golden.sh` fails against the 22 October frames.

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

renders into `reviews/golden/current/` (about 15 s for all fifteen frames) and compares into `reviews/golden/compare/` (about 10 s), both kept out of git, and exits 1 if a frame fails. It runs under the Unity lock in timing mode, as the harness does (below), and writes `reviews/golden/compare/machine.json`. A partial render compares only the frames it made. To accept a new baseline (only Øystein accepts one; the AI proposes it with its sheet):

    blender -b --factory-startup --python blender/tools/golden_compare.py -- accept reviews/golden/current reviews/golden/baseline

**Accepted (21 October).**
- Rendered twice, all fifteen frames are bit-identical: no pixel differs.
- A test-only change, the slate's weathered colour a shade warmer on the stair (`LT1Golden.Views -tweak`, in memory, never saved), fails every frame: mean 0.001 (the street stop, where the stair is small) to 0.014 (on the steps), worst pixel 0.08 to 0.15. The heat maps show it on the stair's stones and nowhere else, not on the cheek walls or the clay.
- The metric's own test (`golden_compare.py -- selftest`): identical images score zero everywhere, a small patch of changed colour scores inside the patch and nowhere far from it, and a larger change scores higher.

**Baseline** (accepted 22 October). `reviews/golden/baseline/gully/<light>/<view>.png`, fifteen frames, 45 MB, with `frames.json` (size, MSAA, warm-up, Unity version, GPU). They are in plain git: Git LFS is not installed on this machine, and `.gitattributes` keeps renders out of it because LFS uploads cannot be reached from the cloud workspace.

Why it changed: the gully is now the one today's generators build (Mesh hashes, What the hashes found).
- Against the first baseline (21 October, the old FBX) every frame differs: mean 0.002 to 0.005 at the street stop, 12 m and the city camera; 0.015 to 0.019 at the foot of the steps; 0.044 to 0.046 on them. Worst pixels 0.31 to 0.98, where stones moved by a pixel or two.
- The old FBX put back renders the first baseline bit for bit, so the geometry is the whole difference.
- The new frames render bit-identically twice.
- A fresh Fable agent judged seven blind pairs of native-size crops where the frames differ most (`reviews/golden/rebaseline-2026-10-22.md`). It found every pair equal: the differences are the generator's own noise (stone positions, which face kind lands where, where moss falls), each as plausible as the other, so both builds are fit to be the reference.
- It proposed the new one on the main session's brief, and Øystein accepted it (22 October).

**Known defects, frozen into the baseline** (shared by both builds; fixing one is a deliberate change to the reference, not a regression):
- the left cheek wall's low end reads as see-through thin slabs at the street stop, and as a black band between the wall and the tread ends from 12 m (the wall's skins seem to have no end cap);
- where a stone's end stands proud of its neighbour, the joint is a flat black bar with no end face; it stripes the flight with dark ticks at the street stop;
- the lichen reads as decals in grey light: a uniform bright rim, and young rosettes all coin-round and one size;
- one-pixel bedding lines on the big riser catch the wet gloss: likely to shimmer.

**Accepted by Øystein (22 October)** as the regression reference; the look is judged against the target frame. Step 0b: the gully from the generators on the hash spec. Every frame fails against the 22 October baseline, as a re-drawn gully must:

| Views | Mean |
| --- | --- |
| On the steps | 0.15 to 0.16 |
| At the foot | 0.077 to 0.089 |
| Street stop, 12 m and the city camera | 0.013 to 0.031 |

Part of the low-sun change is the air motes, which now draw from `Core/Hash.cs` (`4fc4948`).

Blind strict reviews: fresh Fable agents judged eight pairs of native-size crops, taken where the frames differ most. The records are in `reviews/golden/rebaseline-2026-10-22-seeds.md` and `-seeds-2.md`, with their keys. Against the 22 October build, the last review found this build better in 8 of 8 pairs.

Faults found on the way and fixed in the function where each belonged:
- the set-out silently dropped rests the facts require (option A, `13e1b3b`);
- cement dabs stood up to 38 mm proud of a riser;
- fallen-stone holes drew as black voids. The lining was baked as unlit soil; the holes now show lit rubble at its angle of repose;
- the wall ends were hollow; they are now closed by heads laid through the thickness;
- the left wall jogged at the rest, because of forced course joints;
- the 1961 stretch met the old work in a ragged stack; it now meets it at a straight joint with long-and-short ends.

Still open, so the build is not yet at the bar. In the reviewer's order:
1. The courses bend through the change of pitch, where a mason would step or taper them. This came from the jog's fix.
2. A small notch where the coping steps at the rest (12 m, about 15 px).
3. Wall stones read as pillows on undercut shadow, without beds.
4. A loose fan of stones at the right wall's top end, at eye level.

Shared with the 22 October build:
- tread mottling across the walking line, near white in drizzle;
- black slots at tread joints;
- one-pixel nosing lines, orange rims on courses in low sun and single specks, all risks to shimmer.

The lower flight's 16 risers before its rest is a draw within the town's patience (11 to 16), so it stays.

To accept:
1. Export both kinds (`stone.py -- gully`, `wall.py -- gully_cheeks`).
2. Check the hashes above.
3. Run `zsh tools/golden.sh`.
4. Copy `reviews/golden/current/gully` over `reviews/golden/baseline/gully`.

Until then, the 22 October baseline stays the reference.

## The frame-time harness

**What it measures.** What the corner costs to draw on the reference machine, in a built player (never the editor, which draws at a different speed), at the player's size, for every judging view in every light. `Overstory.Perf.PerfRunner` (runtime code) holds each view and records:
- *offscreen:* the view drawn into a 2560 by 1440 target with the game's MSAA, six at a time back to back with the GPU kept busy, the wall time a frame. It is the cost of drawing the view, free of the display's cadence, and the steadiest number: the one to compare in an A/B;
- *frame:* the presented frame's period (FrameTimingManager's CPU frame time, which includes waiting for the GPU and the screen): what the player gets. macOS presents on the display's refresh even with vsync off, so it comes in whole ticks (6.9 ms on the 144 Hz screen here);
- *GPU:* the GPU's own time a presented frame. On Apple's tile GPU the passes of successive frames overlap, so it can exceed the frame's period; compare it with itself, not with the frame;
- the main and render threads' time, the triangles, draw calls, SetPass calls and shadow casters of the median frame, every pass included (a release player keeps no batch count), and the memory in use.

`LT1Perf.Build` composes the corner as the gully's frames stage it (`LT1Stone.Stage`: the heart in clay, the stair and its cheek walls in stone) and plants the corner's birch where `docs/experiments.md` has it, in C's yard by the lower flight. It is the judged downy birch at 60 (seed 1, 16.7 m), older and taller than the fact's birch of about 40 years and 14 m, so its cost is an upper bound. The scene is saved as a generated scene (out of git) with the runner, and built as a macOS player with frame timing stats on; the player settings changed for the build are put back after it. The segments: the five golden views and the birch's own view (`birch12`, its crown filling the frame from 12 m), in each light, and the six again in low sun without the birch (the A/B), 24 in all. Each is measured twice, in two rounds one after the other (150 presented frames after 30 to warm up, and six batches of six offscreen frames), after 600 frames to let the machine settle; a screenshot of each is taken after all the measuring.

**How to run it.**

    tools/perf.sh [-runs 2] [-perf-only street,high] [-perf-frames 150] [-perf-rounds 2]

composes, builds (about 6 minutes the first time, seconds after) and runs the player full screen at 2560 by 1440, about 11 minutes a run. Each run writes `reviews/perf/<date>/run-<n>/summary.json` and `summary.md`, with every frame in `frames.csv`, the screenshots and the player's log beside them (out of git); `runs.md` says how far the day's complete runs agree. The player takes the screen: leave the machine alone while it runs. A run never waits for a quiet machine, which never comes (Spotlight's `mds_stores` takes 30 to 40% of a core all the time, `mediaanalysisd` 50 to 86% since 19 October): `tools/perf.sh` runs under the Unity lock in timing mode, which waits only until no other Unity, Blender batch process or player of ours is running, and writes the machine's background load into each run's folder as `machine.json` (the busiest processes before the run and every 30 s during it, Spotlight's among them, and the load average). The first attempt stopped part way (why is not known: a key, or another app taking the screen); a run that stops writes no summary and is left out of the comparison. A build rewrites some settings as housekeeping (URP's stripping prefilters, the default volume profile's list of overrides, the graphics settings' warm-up fields); `tools/perf.sh` puts back those that were clean before, so a run leaves git as it found it, and the golden views render bit-identical after it.

Two arms leave every pass on and set a shader keyword everywhere (step 3; `reviews/lt1/history/r2.md`): `-perf-passes history-off` (`OS_HISTORY_OFF`: every history layer at its material's quiet mean, no page or piece read) and `haze-off` (`OS_HAZE_OFF`: `OS_Atmosphere` skipped in the stone, street, tree and motes shaders); `LT1Golden.Views -history-off` or `-haze-off` renders the same arm. `-perf-scenes quad-rgba8,quad-bc7` adds the history quad (`LT1History`: 4,096 pieces reading three synthetic pages through `Shaders/History.hlsl`), measured in `all` and `history-off` from the empty scene's views; `summary.json` gives each segment's per-round offscreen medians (`round_offscreen_ms`).

A quad scene takes options after its format (`half`, `two`, `tile<k>` and R2c's sampling arms; `reviews/lt1/history/r2.md`). What they found: a busy output costs in the passes after the draw, not in the draw. The quad sampling its pages minified and writing a flat colour costs +0.05 ms; writing texel-rate noise with no sample, +2.2 ms. So the pass budget below, measured on quiet frames, understates a busy screen by about 2.2 ms, and a shader's cost is measured on its own real output, never on a stand-in.

**Accepted (21 October).** Two runs (`reviews/perf/2026-10-21/runs.md`):
- the GPU time agrees within 3.1% in all 24 segments;
- the frame agrees within 3% in 22 of 24; the other two (on the steps and 12 m up, in drizzle) differ by 5.0 and 5.2%, their medians sitting between two refresh ticks;
- offscreen agrees within 3% in 22 of 24; the other two (at the foot of the steps in drizzle and the blue hour) by 4.0 and 6.9%;
- in low sun, the heaviest load, all three agree within 1.5% in every segment. The lighter the load, the more the M4's clocks wander, so the light views vary most.

Earlier runs, measuring each segment once and then in rounds without the offscreen batches, disagreed by up to 8 to 10% on the frame and 7.5% on GPU time. With the offscreen batches in every segment, which keep the GPU busy, they agree as above; how much of that is the method and how much a quieter machine is not yet known, and more runs will tell. Other apps open on the machine (the Unity editor on another project, Blender, the Claude app) are part of the noise; each run's `machine.json` names them. The player draws what the golden views show: its street stop in low sun without the birch is within three 8-bit levels of the golden still in 92% of pixels (about a level darker on average), the rest at edges.

**Baseline** (21 October, run 1; run 2 within the spreads above):

| Light | Offscreen (ms) | Frame (ms) | Frames a second | Triangles a frame | Draw calls | Shadow casters |
| --- | --- | --- | --- | --- | --- | --- |
| Drizzle | 33.5 to 50.4 | 28.0 to 42.3 | 24 to 36 | 13.8 to 15.5 million | 130 to 143 | 54 to 67 |
| Low sun | 97.8 to 113.4 | 84.0 to 96.3 | 10 to 12 | 13.8 to 15.9 million | 131 to 147 | 54 to 70 |
| Blue hour | 27.2 to 40.1 | 25.3 to 34.8 | 29 to 40 | 5.5 million | 76 | 0 |

Memory in use: 231 to 234 MB by Unity's count, which leaves out the GPU's memory; the system counts 1.4 GB for the same player (The scale test, below). The main thread takes about a millisecond: the corner is bound by the GPU.

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
- Low sun costs about two and a half times drizzle on the same triangles, so something drawn only in low sun costs about 55 to 65 ms. It is the sun's beams (The pass budget, below).
- The birch, one tree, costs 10 to 16 ms wherever it is in view (an eighth to a sixth of the frame) and 25 ms where its crown fills the frame (a fifth): the dearest thing on screen, as the ground cover study estimated.

## The pass budget

**What it measures.** What each pass of the pipeline costs on the M4 at 1440p, so the architecture's frame budget by pass (`docs/building-blocks.md`, Budgets) rests on numbers. The harness draws each segment with every pass on, then with each pass alone turned off, then with every pass off (`bare`: the opaque geometry lit by the sun alone, no shadows, no MSAA). A pass's cost is the difference in offscreen time. The passes are the sky, the sun's shadow map, SSAO, SSR, the four full-screen passes (sun beams, fog lights, the key block, the palette), post-processing, MSAA 4×, the air's motes, and the opaque and depth textures the pipeline copies. It does this for the corner and for an empty frame (the corner with every renderer hidden: the sky, the lights and post alone, where a fixed cost shows without the geometry's noise). Three A/Bs follow from the first answers: every frame drawn offscreen at half the width and height (a quarter of the pixels, every vertex; `-perf-offscreen-scale 0.5`), so the pixels' share of a cost shows; the street shader without its leaf cards' `clip()`; and the bare corner drawn in a flat unlit material (`flat`), so the street shader's own cost shows.

**How to run it.**

    tools/perf.sh -runs 1 -out reviews/perf/<date>/passes -perf-frames 60 -perf-warmup 20 -perf-rounds 2 \
        -perf-passes all,-sky,-shadows,-ssao,-ssr,-beams,-foglights,-keyblock,-palette,-post,-msaa,-motes,-opaquetex,-depthtex,-fullscreen,bare \
        -perf-scenes empty,corner -perf-views eye-foot,street,into12,high -perf-empty-views street,high -perf-shots some
    python3 tools/pass_budget.py reviews/perf/<date>/passes/run-1 > reviews/perf/<date>/passes/passes.md

It measures for about 42 minutes (280 segments, two rounds each). `-perf-shots some` keeps a screenshot of every configuration at the first view, which shows each switch does what it says (checked: without the sky the top is flat, bare changes everything, without post the grade moves, without the beams the empty low-sun frame changes and the street stop barely does).

**Accuracy.** Within a segment the offscreen time holds within about 2.4% (median 95th percentile over median). Between segments the M4's clocks wander, so a pass's cost in the corner is known to about ±1.5 ms (some show as small negatives) and to about ±0.1 ms on the empty frame. A pass under about 1.5 ms in the corner is read from the empty frame.

**The answers** (21 October; `reviews/perf/2026-10-21/passes/passes.md`, with `passes-half/`, `passes-noclip/` and `passes-flat/` beside it):

| Offscreen ms, the street stop | Drizzle | Low sun | Blue hour |
| --- | --- | --- | --- |
| Every pass on | 37.3 | 102.1 | 30.0 |
| The empty frame, every pass on (sky, lights, post, nothing drawn) | 8.5 | 49.0 | 9.2 |
| Bare: the opaque geometry alone, 2.74 million triangles, 20 draws | 14.6 | 14.3 | 14.5 |
| Bare in a flat unlit material | 2.0 | 1.9 | 1.9 |
| Sun's shadows | 7.1 | 32.4 | (none) |
| Sun beams | (idle) | 64.3 (40.2 empty) | 1.0 |
| MSAA 4× | 4.9 | 6.5 | 5.4 (1.8 empty) |
| SSAO | 2.8 | 4.3 | 2.4 (0.7 empty) |
| SSR | 2.0 | 3.9 | 3.2 (2.3 empty) |
| Fog lights, key block, palette (no lamp lit, look D off: their colour copies) | 0.5 to 0.7 each (empty) | 1.1 to 1.4 each | 0.8 to 0.9 each |
| Post | 0.3 | 3.6 | 1.2 |
| The birch (low sun, with and without) | | 12.6 | |

The sky, the opaque and depth textures and the motes are each under the noise (the sky 1.5 to 2.4 ms on the empty frame, behind the town hidden by it). The other views agree: `passes.md` holds every view.

**What owns the floor** (the blue hour, 30 ms at the street stop, no shadows):
- *The opaque pass is about half of it, and it is the shaders, not the triangles.* Bare, the geometry costs 14.5 ms. Drawn in a flat unlit material, the same 2.74 million triangles in the same 20 draws cost 1.9 ms in every view and light. So about 12.5 ms of the bare frame (85 to 90 %) is the street, stone and tree shaders' own work, and rasterising the triangles and their overdraw is under 2 ms. At half the width and height the bare frame costs 6.8 ms, so about 10.3 ms of it scales with pixels and 4.2 ms does not: the shading is mostly per pixel. Every opaque fragment runs the atmosphere's haze march (`OS_Atmosphere`, `StreetSurface.hlsl:267`: twelve steps along the view ray, each with two noise lookups) besides its surface and light; it is the first suspect, not yet measured on its own.
- *The leaf cards' `clip()` is not it.* With `OS_CardClip` removed from the street shader the bare frame is 13.2 to 13.9 ms against 14.3 to 14.6, and the whole frame within the noise: at most about a millisecond.
- *The rest is the screen-space passes and MSAA:* MSAA 5.4, SSR 3.2, SSAO 2.4, the four full-screen passes about 2.6 (each pays about 0.5 ms for its colour copy even when it does nothing), post 1.2. Two thirds of the whole frame scales with pixels: at half the width and height it costs 14.9 ms, so 20.1 ms is per pixel and 9.9 ms is not.
- *An empty frame already costs 7 to 9 ms* (49 in low sun): over half the 16.7 before anything is drawn. SSR alone is 2.3 ms with nothing to reflect, and MSAA 1.8.
- *MSAA's cost barely shrinks with the pixels* (5.4 ms at full size, 3.3 at half the width and height): it is paid at the triangles' edges, and today's triangles are small enough that most pixels hold an edge. The foundations' rule of a median visible triangle of ten pixels or more would cut it.

**What costs low sun its extra 55 to 65 ms: the sun beams.** Turned off, the frame drops 64 ms in the corner and 40 ms on the empty frame (`SunBeams.shader`: a 40-step march along every pixel's ray, each step a soft shadow-map tap). The shadows' 31 to 32 ms in low sun, against 5 to 7 in drizzle where the beams are idle, are most likely the beams' taps too (with the shadows off the beams have no map to sample); an A/B with both off would split them. Post in low sun (2.8 to 4.7 ms against about 1 in the other lights) is the second, smaller unknown.

**Proposed budget by pass on the M4** (GPU ms at 1440p, against the provisional one in `docs/building-blocks.md`, Budgets; today's cost is the street stop's in the light where it is dearest):

| Pass | Provisional | Today | Proposed | What it takes |
| --- | --- | --- | --- | --- |
| Opaque geometry | 5.0 | 14.5 (1.9 flat) | 5.0 | the shaders' per-pixel work from about 10 ms to about 3: the haze out of every fragment (a low-resolution volume or the vertex), then each shader A/B'd flat |
| Sun's shadows | 2.0 | 7.1 | 2.0 | fewer cascades, proxies as casters, the far cascades cached |
| Sky, atmosphere, air | 1.5 | 2.4 + beams 64.3 | 1.5 | the beams at a quarter of the pixels, 12 to 16 steps, one hard tap with a blue-noise offset, upsampled by depth: about 0.5 |
| Lights and spill | 1.0 | not lit here | 1.0 | unmeasured |
| GTAO | 1.0 | 4.3 | 1.0 | at half resolution |
| SSR and water | 1.0 | 3.9 (2.3 empty) | 1.0 | at half resolution, only where the surface is wet or water |
| Trees and alpha-tested layers | 1.0 | the birch 12.6 | 1.0 | unchanged: the birch's own fix |
| Full-screen passes | (none) | 2.6 to 3.8 | 0.4 | fog lights, key block and palette in one pass, folded into post's, skipped when idle |
| Post | 0.8 | 3.6 | 0.8 | low sun's extra 2 to 3 ms found |
| Anti-aliasing | 0.5 | MSAA 4× 6.5 | 0.8 | MSAA 4× cannot reach it: see below |
| Id readback, UI | 0.2 | | 0.2 | |
| Reserve | 2.7 | | 2.0 | |
| **Sum** | **16.7** | **102.1 (low sun)** | **16.7** | |

Every measured pass but the sky is over twice its budget in at least one light, so by the foundations' own rule each gets a fix before any triangle work. In order of what they save: the beams (about 60 ms in low sun), the birch (about 11), the opaque shaders (about 9), MSAA (about 6), shadows (about 5), SSAO and SSR (about 3 each), post in low sun (about 3), the full-screen passes (about 2).

**Two findings change architecture decisions** (for the main session; `docs/building-blocks.md` is not this page's to change):
- *Anti-aliasing.* "MSAA 4× native" (Rendering, and the decisions table) costs 3.4 to 6.5 ms at the corner against its 0.5 ms line, and 1.4 to 1.8 on an empty frame. The candidates, each without temporal accumulation: SMAA or another spatial filter at native resolution, MSAA 2×, or fewer pixels with FSR 1. Judged by the motion sheets' shimmer measure and the golden views, not by cost alone.
- *The triangle budget is not the frame's floor.* Today's 2.74 million triangles draw in under 2 ms flat; the shaders and the screen-space passes are the floor. The per-view triangle ceilings still matter for shadows, MSAA's edges and memory, but the port's first frame budget is the shaders'. A per-shader flat A/B (street, stone, tree) is the next switch.

The proposed numbers are provisional until each fix is A/B'd on the harness.

## The scale test

**What it measures.** What the town costs at city scale on the M4: a district 2 km across (8,519 test-quality houses on the clay ground, the 512 m core at L0, shells everywhere), loaded into the built player and drawn with the corner's shaders and passes. It gives build time, disk, memory, the frame at the judging views, a chunk's load and rebuild time, and the chunks a second the camera's movement asks for. What the numbers mean for the architecture is in `docs/research/scale-test.md`, with how to run it.

**Baseline** (22 October; `reviews/perf/2026-10-22/district/`, `scale-report.md` and `run-1/summary.md`):

| | |
| --- | --- |
| Generation (Blender's Python, 8 processes) | 222 s for 4.2 km²; a house built in 64 ms alone (95 ms with 8 at once), baked in 0.6 s (0.93 s) |
| Disk | 708 MB of chunks: L0 708 KB a house (2.1 GB a km² of core), shells 1.6 MB a km², the 2 m ground 37 MB a km², records 315 bytes a house |
| A house's envelope (from its shell) | 444 m² |
| Frame, near (L0 to 200 m, shells beyond), beams off | street stop 20.8 / 26.5 / 28.8 ms (blue hour / drizzle / low sun), 12 m 23.0 / 28.8 / 30.4, city camera 25.0 / 30.5 / 29.9 |
| Frame, L0 for the whole core | city camera 45.5 ms in the blue hour (15 million triangles) |
| The beams in low sun | about 59 ms in every view |
| Main thread | 0.4 to 0.7 ms; 1.1 to 1.4 ms at 2,900 draws |
| Memory (footprint, GPU included) | the corner's player 1.4 GB; with the district loaded 2.3 GB; 2.6 GB after every view has drawn |
| Loading a chunk (main thread) | 0.28 ms + 0.63 ms a MB; a core chunk (8.8 MB) 5.6 ms, 95th 9.1 |
| Rebuilding a chunk (265,000 triangles in 1,384 parts) | placing 24.2 ms in C# (Mono), 1.8 ms in Burst; uploading 1.6 ms |
| A 1024 by 512 history page | drawn 0.7 ms, read back 0.7 ms, compressed on the CPU to DXT5 8.7 ms (fast 5.3) |
| The camera's demand, main thread a second | walk 1.7 ms, drive 17 ms, the city camera's 300 m/s pan 84 ms |

**The harness's memory column undercounts.** It reads Unity's "total used" (231 to 248 MB), which leaves out the GPU's buffers and textures; the system's footprint for the same player is 1.4 GB before the district. `DistrictLoader.Footprint` reads it from `footprint(1)`; the harness should report it for every run.

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
- **The harness's other switches** (`docs/research/performance-at-scale.md`, The performance harness, 5): the Resident Drawer and GPU occlusion, the shadows' reach and cascades, a forced level per kind, each shader drawn flat in turn (street, stone, tree), and each anti-aliasing candidate against MSAA 4×. Each is an A/B on the same segments, as the passes and the birch already are.
- **The footprint in every run:** the system's count of the player's memory beside Unity's, for every segment, so memory budgets are judged on what the machine holds.
- **Hashes from every generator.** `stone.py` and `wall.py` write them; the trees, the houses and the clay should too as they are ported onto the building blocks.
- **Golden views of more than the gully**, as each kind joins: the birch, the corner's houses, the clay heart from its stops.

## Local tools (installed 21 October, with Øystein's OK)

These live in a project virtual environment, `.venv/` (not in git), with `jsonschema` for the record checks (`tools/validate_record.py`). To recreate it: `python3 -m venv .venv && .venv/bin/pip install -r requirements.txt` (the pins, Python 3.9.6).
- **NVIDIA FLIP** (`flip-evaluator`, from github.com/NVlabs/flip): the reference image comparison, used to check `golden_compare.py`'s approximation. Run it as `.venv/bin/flip`, or import `flip_evaluator` from `.venv/bin/python`.
- **ffmpeg**, bundled by `imageio-ffmpeg`, so no Homebrew is needed. It turns motion sheets into videos. The path is printed by `.venv/bin/python -c "import imageio_ffmpeg; print(imageio_ffmpeg.get_ffmpeg_exe())"`.
- **Git LFS is not installed,** on purpose: `.gitattributes` keeps renders in plain git because LFS isn't reachable from the cloud workspace. The repository's size is handled by the architecture's decision to keep generated meshes out of git.
