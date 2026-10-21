# Where generation runs

Which stages of generation run offline, and which inside the shipped game? This study closes the gap the generation digest found (`inputs/2-generation-performance.md`, The shared shortfall). Play changes the record, and the 3D world must show it. A built game can't run Blender, import FBX or ship GPL code. So every stage that must answer to play has to exist in the player.

Claims are marked as in the other studies: (primary), (secondary), (unverified); our own arithmetic (ours). Costs are Opus working days.

## The answer in short

- **Parts are made offline; the town is assembled in the game.** Every shipped game that changes at runtime does this: parts authored offline, then chosen, fitted, deformed, instanced and merged in play. Only voxel worlds and Tiny Glade generate raw geometry at runtime.
- **In the player, in C#:** plan, life at a date, placement of library parts, fitted parts per chunk and level, the extrinsic bakes and the cheap checks. Facts come from the engine's own process.
- **Offline, in Blender:** the part library with each part's levels and intrinsic channels, tree growth timelines, impostors, and the expensive checks.
- **One source of truth:** each stage that runs in the player is written once, in C#, and offline runs call the same code. The Python generators are the reference the port is checked against, and retire stage by stage.
- **The world on disk is the record plus the libraries.** Chunk meshes and maps are a cache keyed by the hash chain. Disk grows with the record, not with the meshes, which keeps bigger cities possible.
- **Most of time costs nothing.** The date is a global (`time-on-screen.md`), and wear, polish and lichen are closed forms in years. Drift across thirty years is a uniform; only discrete changes rebuild, chunk by chunk.
- **Fix the seeds first.** The stone side seeds Python's `random.Random` from strings, some built from float positions. Python does not keep those sequences across versions, and a moved piece re-draws its neighbours. Seeds come from SplitMix64 on stable part ids, as the resolver's do.
- **Port after the stage split.** Next week's gully work stays in Python, as planned; the split is the specification the port copies. The house generator is ported before House A.

## Where we stand

Checked on branch `lt/1-harbour-street`:

- **The generators are nearly free of Blender.** `stone.py`, `wall.py`, `wear.py`, `growth.py`, `upkeep.py`, `water.py`, the resolver and `building.py` are plain Python and numpy. Blender appears only in `make()` and `build()`, which create objects and export FBX. The other seams are small: `kit.py` uses `mathutils.Vector`, `bake.py` uses `mathutils.bvhtree` for its ray fans, and `tree.py` uses `bmesh` for one convex hull.
- **Two kinds of randomness.** The resolver seeds from `hashing.h`, SplitMix64 written so "the C# port must produce the same numbers". The stone side uses `random.Random`, with some keys from formatted floats (`f"fill-{xc:.3f}-{s_a:.3f}"`, `stone.py` 418).
- **The stone has no plan stage** (K §6); the house's plan is in integers.
- **Drift is a closed form.** The hollow is `rate × use × years` (`wear.depth`), linear in years. Polish saturates within forty years; lichen and moss are clipped ramps (`growth.py`).
- **The engine is TypeScript, in its own process beside Unity.** A save holds its version, checkpoints and the player's commands (`living-world.md`), never meshes.
- **Unity 6000.6.6f1, URP 17.6.** Burst, Collections and Mathematics are not yet installed.
- **Baselines on the M4:** the test house generator, under 80 ms a house in Blender (ours, from 129 in 10.2 s); the gully's flight, 67 s and a 16 MB FBX; a stair with its walls, about 816,000 triangles.

"Life is computed offline per thing" (`living-fabric.md`), "only the chunk a change touches is rebuilt offline" (`town-system.md`) and "Unity runs no generation" (K §6) are overturned in their *where*. The rest holds: cached by hash, rebuilt per chunk, never per town.

## 1. How games that change at runtime make geometry

| Game | Offline | At runtime, from what |
| --- | --- | --- |
| Townscaper | corner modules, each labelled with the neighbour case it fits (secondary) | a solver picks a module per irregular cell and deforms it into the cell; structure first, decoration second; windows cut by a stencil. Delay grows with the connected structure's size (secondary, Thompson's interview) |
| Bad North | over 300 tiles from Maya; adjacency read from their edges (secondary) | each island solved by wave function collapse, restarted from a saved state on failure, merged into one mesh. Some islands miss their time budget (secondary). From a seed |
| Tiny Glade | a hand-written generator per element (primary quotes) | walls, stairs, roofs and doors rebuilt as the player draws, on the GPU in compute shaders, which is why the makers wrote their own renderer (primary quotes). Only what an edit touches is recomputed (K §3). From strokes and terrain |
| Cities: Skylines 1 and 2 | every asset modelled, with required levels (CS2: one under half the triangles, one at most 500); tree impostors made at import (primary wiki); colour variety from mask textures (primary) | growables placed by zone and drawn as instances through Unity's BatchRendererGroup, about 50 floats each (secondary). Level-ups swap assets (unverified). From instance records |
| The Sims | objects modelled | walls, floors and roofs built from the lot's rooms (unverified; player reports point that way, secondary) |
| Minecraft, Sodium | block models; village templates | 16³ sections re-meshed on workers when a block changes (unverified). Greedy meshing cuts a solid 8³ block from 3,072 faces to 6, noisy terrain only from 2,198 to 1,670 (primary article). Sodium 0.5 meshes 40 to 60 per cent faster (primary) |
| Valheim; Enshrouded | Valheim's pieces as prefabs | Valheim places instances and passes support along them, no mesh generation (secondary). Enshrouded sculpts voxels at runtime (secondary) |
| No Man's Sky | the generators | voxels, polygons, textures and population generated continuously (primary abstract), from a seed (secondary) plus stored edits (unverified) |
| RimWorld, Dwarf Fortress, SimCity (2013), Manor Lords | sprites, buildings and modules | the asset chosen from simulation state; RimWorld's walls by their neighbours; Manor Lords' houses fitted to drawn plots (all unverified or player wikis) |
| Assassin's Creed Unity, Far Cry 5, Wildlands | modular, partly automated cities; Houdini inside the editor, regenerated nightly because the same inputs give the same world (primary and secondary, K §2, P §1) | nothing generated; instances drawn by GPU pipelines |
| Firewatch; Red Dead Redemption 2 | everything modelled | Firewatch swaps sectors, burned or green, by story day (primary). RDR2 draws footprints into a mud map (secondary). History in play as states and textures |

What they share:

- **The careful work is offline:** parts, materials, levels or the rules that make them. Even Tiny Glade's generators are hand-written per element.
- **At runtime they choose, fit, deform, instance and merge,** reading small data: cell cases, voxels, seeds plus edits, instance lists, state. No changing world ships as meshes.
- **History in play lives in textures and instance data.** Geometry changes by local rebuilds or swaps, and levels come with the parts or from merging, never from simplifying in play.
- **Determinism is by seeds and inputs.** No maker publishes how floats match across machines, and none publishes a rebuild time.

No shipped game builds its parts from dated facts. Ours is Townscaper's pattern with a record behind it: approved parts, chosen and fitted from facts, rebuilt locally when the record changes.

## 2. Hybrids: libraries offline, assembly in the game

A part comes in one of two forms (K §6, `made_as`):

- **A fixed part is a mesh:** a sett, a slate, a window of an era and maker, a lamp, a wall stone in its size class. It is made and judged in Blender and ships with its levels, intrinsic channels (face kind, edge distance, its own occlusion from `bake.py`), sockets and sidecar. The game places it and gives it the place's history through instance data (P §2).
- **A fitted part is an approved function whose inputs are facts:** a tread fitted to its step and worn by its feet, a coping cut to its wall, cladding round its openings, a roof over its footprint. The function and its parameters are judged on the sheet; its geometry is made per instance, wherever the instance is made. When play can change the fact, that is the player.

This settles the digest's conflict 6: the generator invents no geometry.

| | Baked offline | Computed in the game |
| --- | --- | --- |
| Drift (wear, polish, lichen, moss, fading) | nothing | rates and reset years per dated interval, written on change; the state at the date in the shader |
| A tread's hollow | nothing | depth per year per vertex and its gradient, written on change; the vertex shader moves the surface by the date (ours: depth is linear in years) |
| Discrete changes (made, replaced, removed; a coat, a sign) | nothing | the plan diff, then the chunks it touches |
| Fixed parts, their levels and intrinsic channels | once, into the library | placement only |
| Extrinsic history at the street and city levels | nothing | per-chunk maps and field tiles, on change |
| Trees | the growth timeline per tree (`trees.md`, step 2); impostors per species, age band, season and state | the tree at the date; tint and scale per impostor |
| The district level | nothing | a block's atlas, rendered again when the block changes |
| Natural ground and rock | the base with its breaklines | dated acts, if a game needs them (unknown) |

The rule: **precompute what has few states and costs much; compute what follows from the record.** Firewatch's two states can be baked. A town with a record has too many.

**What a date span lets us precompute.** The past before the game's start is fixed: it is grown from the pack's script to the hand-off year (`town-system.md`, section 3), so it can be built offline and shipped as a cache, or built on first launch. Works already decided have dated phases (hoarding, pit, scaffold), so a worker can build the next phase before its date. Drift needs nothing. What the engine has not yet decided can't be precomputed: a thirty-year jump waits for the engine's own run.

## 3. Unity 6 at runtime

| Tool | What it gives the player | Limits |
| --- | --- | --- |
| `Mesh.AllocateWritableMeshData` | meshes written from jobs; the data can be used "from any thread" (primary) | allocation has overhead, so allocate many at once; the sample applies on the main thread |
| Jobs and Burst | Unity's examples (primary): on a 2019 MacBook Pro, a 300,000-triangle noise ball in 2,723 ms in plain C#, 187 ms in Burst, 22 ms in multi-threaded Burst, 14 ms in a compute shader. On a 2018 one, combining 4.6 million vertices: 760 ms and 640 MB of garbage on the plain API, 60 ms with Jobs and Burst | old Intel hardware; rendering included |
| Compute shaders | maps and field tiles written on the GPU, Tiny Glade's route | a readback costs a frame |
| GPU Resident Drawer, user value, BRG | instanced library parts; one 32-bit value per renderer indexing a buffer of facts; BRG for setts, slates and grass (primary, P §1) | nothing gained for a unique merged chunk |
| Mesh LOD | levels chosen in the player | generated only in the editor (`MeshLodUtility` is in `UnityEditor`; primary docs via search), so a mesh made in play gets no automatic levels |
| `Texture2D.Compress` | at runtime, R8 to BC4 and RG16 to BC5 on desktop (primary) | the better encoder is editor-only |
| Burst `FloatMode.Deterministic` | "consistent across all supported platforms" (primary) | 64-bit and Burst code only; subnormals flushed; NaN bits may differ; slower; promises nothing about managed C# or Python |
| Python for Unity | nothing: "designed to work only in the Unity Editor", support ending with 6.1 (primary docs via search) | |

So building meshes in play is cheap enough: Burst on workers writes hundreds of thousands of triangles in tens of milliseconds, and a chunk is a fraction of that. Levels for runtime meshes come from our generators, from the same seed and outline (P4), with meshoptimizer through P/Invoke as the fallback for natural stone and land. History reaches instances through user values and BRG buffers, and chunks through maps written on the GPU.

## 4. Porting, and one source of truth

| Way | For | Against |
| --- | --- | --- |
| A. Two sources: Python kept, a C# copy checked by hashes | no change to how we work | every rule written twice, for ever; drift is certain |
| B. C# is the source: each stage ported once, Python the reference until the stage matches, then retired; offline runs call the same C# | one source; offline equals the player by construction; Burst, jobs and the harness apply directly | a port of about 6,500 lines (ours); agents iterate in C# rather than in a Blender script |
| C. A shared Rust or C++ core called from both | one source; floats could match everywhere | a third language, a native build per platform, debugging across the boundary |
| D. Python in the player | no port | Unity's Python is editor-only; CPython and numpy per platform is heavy, and closed on consoles (unverified) |

**B.** The town library is already meant to reach the engine the same way: "a port, not a rewrite" (`town-system.md`). The core (plan, life, fitted-part functions) is plain C# with no `UnityEngine` types. It runs in the player, in Unity's batch mode offline, and in a `dotnet` host if iteration needs one. A thin Unity layer writes `MeshData`, buffers and maps; Burst goes on hot loops when the harness shows the need. A core free of `bpy` also avoids any question of Blender's GPL reaching our scripts (unverified).

### Determinism across languages

Python and C# agree stage by stage if five rules hold:

1. **Seeds from SplitMix64 on stable ids.** Python promises only that `random()` repeats: "Most of the random module's algorithms and seeding functions are subject to change across Python versions" (primary). `randrange`, behind `randint`, changed in 3.2 and 3.12, and our stone uses `uniform`, `randint` and `choices`, so a Blender upgrade could already re-draw the gully. Keys from formatted floats break carry 7 of `time-on-screen.md` (a seed stable for a part's whole life).
2. **Decisions only from integers, or from `+ − × ÷` and square root,** which IEEE 754 rounds exactly in both languages. `exp`, `sin` and `pow` come from different maths libraries, numpy's vector loops may differ again, and ARM compilers may fuse a multiply and an add (all unverified for our functions). A transcendental result may place a vertex, never choose a branch, a count or a part.
3. **Plans and life in integers:** millimetres, years, ids, rates in fixed point. Their hashes then match bit for bit, as `plan_signature` already allows.
4. **Geometry by tolerance across languages, by hash within one.** The same index buffers; positions within 0.05 mm; channels within one 8-bit step. `mesh_hash.py` hashes floats bit for bit: right for a refactor in Python, too strict across languages.
5. **Sort by stable id before any loop that shapes output.**

Within C#, each platform's maths library may move a vertex by a nanometre between a Mac and a PC. Under rule 2 nothing else changes, and since saves hold the record, a game loaded elsewhere rebuilds the same town within tolerance. Burst's deterministic mode is for anything that must hash identically across machines, such as a shipped cache checked on load.

**The parity check, per stage ported:** plan hashes equal on the 129 stress buildings and the gully's flights at every fixture year, once shuffled; life tables equal; geometry within tolerance per chunk and level; the golden views within FLIP threshold as the final word. The Python is deleted when its kind's last stage passes. Two live sources would be option A by the back door.

### The cost

| Port | Lines (ours) | Estimate |
| --- | --- | --- |
| Hashing, eras and the resolver, with plan-hash parity | about 650 | 1.5 to 2 d |
| Seeds by SplitMix64 on part ids, in Python first | | about 1 d, plus a new baseline |
| The runtime assembler: instances, user values, BRG buffers, pick ids | new | 4 to 6 d (already P8, P9) |
| The chunk format, cache and streaming | new | 3 to 5 d |
| The stone and wall stages, fitted treads, levels per chunk | about 2,300 | 6 to 9 d |
| The house builder (`kit`, `building`, `parts`, palette, roof, `validate`) | about 1,900 | 5 to 8 d |
| The tree assembler at a date (growth stays offline) | about 1,800 | 5 to 7 d, at step 7 |

About 26 to 38 days in all. The assembler, chunks and levels are needed anyway; the new cost is porting code we have, about 15 to 22 days (ours).

## 5. What a change in play costs

Estimates (ours), none yet measured in a player. A stair with its walls is about 25,000 triangles a metre today, so a 4 m chunk holds about 100,000. Unity's noise ball wrote 300,000 in 22 ms on old hardware; ours do more per vertex, so we allow 10 to 50 ms of worker time a chunk.

| Change | What runs | Estimated cost | Seen as |
| --- | --- | --- | --- |
| **One stair repaired** (two slabs replaced, repointed) | plan diff (two new part ids, two removal years); two life intervals; one chunk's fitted pieces at the close and near levels; its street-level maps (about 128,000 texels at 1 cm) | microseconds for plan and life; 10 to 50 ms on workers; under 1 ms of GPU | the chunk swapped whole a frame or two later |
| **One house extended** | the resolver; the house's fitted parts and instances and its levels; two fronts' maps (about 88,000 texels at 4 cm); its block's atlas | test quality is under 80 ms in Python with Blender's overhead, so a few to 20 ms in C# (ours). Final quality is unknown until House A | swapped within a few frames |
| **Thirty years across a district** (1,000 buildings) | the engine's run first; then the date global moves, so drift is free. The change query lists the discrete changes: coats and windows as instance records, structural changes as rebuilds | if one building in ten is rebuilt, 100 at 5 to 50 ms is 0.5 to 5 s of worker time, about 0.1 to 1 s across the M4's cores (ours) | the first view's 20 to 50 things built behind the dated card, the rest as streaming reaches them |

Three things keep it small: **the chunk, not the thing** (P3's 3 to 5 m chunks, with a piece cache so only changed pieces are made); **the date as a global** (without it, a jump rebuilds every surface); and **library parts changing by record**, not by mesh (a coat, a window or a sign costs microseconds).

**First load and streaming use the same code.** Chunks are made from the record near the camera and cached on disk by hash. A kilometre of street holds about 250 houses: about 20 s in Python at test quality, perhaps 1 to 5 s of worker time in C# (ours). If that can't keep up with the camera, the game ships the start date's cache (tens of megabytes a kilometre; P §4) and rebuilds only what play changes.

**One heavy case: a tree beside a change.** A tree regrows from the year its site changed (`trees.md`), which in play would mean running the growth simulation in the player. Until that is measured, a change beside a tree is applied as events the timeline already handles (limbs cut back where the new wall stands). Full regrowth stays offline for the shipped past; step 7 learns whether play needs more.

## 6. Licences

GPL-3.0 code linked into a closed game would put the game's source under the GPL, so it can't ship. MIT, BSD, Apache-2.0, ISC and Boost ask for a notice. Offline tools may be GPL, since a program's output is generally not covered (GNU's FAQ; unverified here), unless the same tool must also run in play.

| Need | GPL (offline only) | Permissive (can ship) | Choice |
| --- | --- | --- | --- |
| Hipped roofs over irregular footprints | `bpypolyskel`, GPL-3.0 (primary, digest); CGAL's straight skeleton, GPL or commercial (unverified) | a C# port of Kendzi's straight skeleton in `reinterpretcat/csharp-libs`, Apache-2.0 (primary; robustness untested); Polyskel's Swift port, MIT (secondary) | our own `Roof` in `building.py` first; the Apache-2.0 port when the first irregular hipped roof appears, tested on the stress footprints |
| Simplifying natural stone and land | Blender's Decimate | meshoptimizer, MIT (primary): border locking, attribute weights, a C API | meshoptimizer, natively in the player, through its MIT Python wrapper offline |
| Offsets, clipping, triangulation | | Clipper2 (Boost), earcut (ISC), LibTessDotNet (SGI Free B) (all unverified) | only when the house port needs them |

Every shipped library goes on a list with its licence and notice, checked at build.

## What we should do

### Where each stage runs

| Stage | Offline | In the player |
| --- | --- | --- |
| 1. Facts | the pack, fixtures and the grown past, shipped as record | the engine's own process |
| 2. Plan | the same C# core, for golden views, tests and any shipped cache | the C# core, in integers, when a thing's facts change |
| 3. Life | | intervals written on change (by the engine once request 19 lands); the state at the date in HLSL, and in C# for the change query and the why-probe |
| 4. Geometry | fixed parts, made in Blender | placement of library parts; fitted parts per chunk and level, Burst where measured |
| 5. Bake | intrinsic channels into library parts; impostors per species and state | extrinsic maps and field tiles; block atlases |
| 6. Export | the library as Unity assets with sidecars (FBX is fine in the editor) | none: chunks go to a disk cache keyed by hash |
| 7. Checks | stress tests, parity, mesh hashes, golden views with FLIP, cold readers | budgets per level, fits refused never silent, plan validity |

**Decided here:** this map, because a built player can run neither Blender, FBX import nor GPL code, and play changes the record; C# as the one source for what runs in the player; fixed parts as meshes and fitted parts as functions; the date as a global; seeds on stable part ids; the licence rules.

**Left to measurement:** chunks on demand or a shipped start-date cache; whether a rebuild hitches a frame; plain C# or Burst; final-quality time per house (House A); tree regrowth in play (step 7).

**Authored offline as libraries:** fixed parts with their levels, intrinsic channels, sockets and removal marks; fitted-part functions and their parameters, judged on sheets that run the C# once ported, so what is judged is what ships; materials; the pack and the grown past; trees' timelines, parts and impostors; the land's natural base.

**Computed by the game:** everything in the player column, plus record ids for picking at every level and the chunk cache.

### What is ported, and when

1. **Monday, the architecture:** adopt this map. Write the contracts as language-neutral schemas both languages implement: kind, part definition, plan, life intervals, channel spec, chunk format, hash chain. Mark the three "offline" sentences quoted in Where we stand as superseded.
2. **Tuesday, the scale test,** with the measurements below. No port needed: the runtime floor is measured on synthetic chunks.
3. **Wednesday to Friday, the gully, in Python as planned:**
   - split the stages with the hash unchanged;
   - then, as its own commit, seeds by SplitMix64 on part ids: the hash changes once by design, and the new baseline is accepted on the golden views and a quick strict review;
   - history as rates and reset years with the date a global, which is the runtime model built first in Python;
   - no C# this week: the split is the specification the port copies.
4. **The week after:** hashing and the resolver in C# with plan-hash parity, the cheapest proof that integer stages match (1.5 to 2 d); the chunk format and runtime assembler on the gully's library parts (4 to 6 d); then the stone stages, until the gully is built in the player and passes the parity check (6 to 9 d).
5. **Before House A (step 2):** port the house builder, so final-quality house code is written once, in C#.
6. **Step 7:** the tree assembler; growth stays offline.

### The scale test's extra measurements

Added to the digest's five (`inputs/2-generation-performance.md`, section 4):

1. **The runtime floor in a built player** (macOS, IL2CPP, 1440p): load a chunk from a binary file and upload it; write a 100,000-triangle chunk through `MeshData` in plain C# and in a Burst job; write and compress one chunk's history tiles. Report p50 and p95 on the main thread and the workers, and any frame over 16.7 ms. *Settles:* whether change in play is affordable without a hitch, and whether Burst is needed.
2. **The demand rate:** chunks entering the streaming radius each second along the judging paths, at walking pace and the city camera's pan, times measurement 1 and the build time per chunk, as a share of the M4's cores. *Settles:* on demand near the camera, or a shipped cache.
3. **The cache per kilometre:** disk and resident memory of meshes, instance records and maps at each level, against the record alone. *Settles:* what a big city ships, and the cache's limit.

The resolver's parity probe also gives the Python-to-C# speed ratio that measurement 2 needs; until it lands, measurement 2 uses a range.

## For Øystein to decide

- **Scope:** porting the code we have adds about 15 to 22 Opus-days around House A. *Recommendation:* accept it now. Every kind written in Python before the port is written twice, and without it play can't change the town.

## Gaps

- No primary source for how The Sims, Manor Lords, SimCity (2013) or Assassin's Creed Unity build at runtime. GDC Vault was down and the Paradox forum would not open.
- No game publishes rebuild times. Our costs extrapolate Unity's examples on 2019 Intel laptops, not the M4.
- The Python-to-C# speed ratio is unmeasured; final-quality time per house waits for House A.
- That numpy, .NET and ARM compilers differ in the last bit for our functions is unverified; section 4's rules make it harmless either way.
- Licences not opened: Clipper2, earcut, LibTessDotNet, CGAL, the Unity Companion Licence. The Apache-2.0 skeleton's robustness is untested, and meshoptimizer's simplifier speed was not read.
- The cost of regrowing a tree in play is unknown (step 7). How the engine's process ships per platform is the engine's question.

## Sources

Unity: [Mesh API examples, with timings](https://github.com/Unity-Technologies/MeshApiExamples) · [Mesh.AllocateWritableMeshData](https://docs.unity3d.com/ScriptReference/Mesh.AllocateWritableMeshData.html) · [Burst float precision and determinism (6.6)](https://docs.unity3d.com/Manual/burst/float-precision-determinism.html) · [MeshLodUtility](https://docs.unity3d.com/ScriptReference/MeshLodUtility.html) (search results) · [Texture2D.Compress](https://docs.unity3d.com/ScriptReference/Texture2D.Compress.html) · [Python Scripting, known issues](https://docs.unity3d.com/Packages/com.unity.scripting.python@7.0/manual/known-issues.html) and [the 6.0 manual page](https://docs.unity3d.com/ja/6000.0/Manual/com.unity.scripting.python.html) (search results)

Determinism and licences: [Python's random, Notes on Reproducibility](https://docs.python.org/3/library/random.html) · [meshoptimizer](https://github.com/zeux/meshoptimizer) · [bpypolyskel](https://github.com/prochitecture/bpypolyskel) · [csharp-libs straight skeleton](https://github.com/reinterpretcat/csharp-libs) · [Polyskel for Swift](https://github.com/andygeers/Polyskel-Swift) (snippet)

Games: [Thompson, How Townscaper works](https://www.gamedeveloper.com/game-platforms/how-townscaper-works-a-story-four-games-in-the-making) · [Boris the Brave on Townscaper's grid](https://boristhebrave.com/docs/sylves/1/articles/tutorials/townscaper.html) · [80.lv, Tiny Glade interview](https://80.lv/articles/exclusive-tiny-glade-developers-discuss-bevy-proceduralism-publishers-cozy-games/) · [80.lv, Tiny Glade's windows](https://80.lv/articles/procedural-windows-in-pounce-light-s-tiny-glade-get-an-upgrade) · [CS2 asset pipeline: buildings](https://cs2.paradoxwikis.com/Asset_Pipeline:_Buildings) · [CS2, adding custom assets](https://www.paradoxinteractive.com/games/cities-skylines-ii/news/adding-custom-assets) · [Huhtala, CS2 performance](https://blog.paavo.me/cities-skylines-2-performance/) · [Sims roof reports](https://forums.ea.com/discussions/the-sims-4-feedback-en/halved-curvedmultidiagonal-roofs-/13547085) · [0fps, Meshing in a Minecraft game](https://0fps.net/2012/06/30/meshing-in-a-minecraft-game/) · [Sodium 0.5 notes](https://modrinth.com/mod/sodium/version/mc1.20.1-0.5.0) · [Enshrouded, Wccftech](https://wccftech.com/enshrouded-is-a-zelda-ft-valheim-type-of-game-from-keen/amp/) · [Valheim modding notes](https://thunderstore.io/c/valheim/p/Hardwire99/DvergrCraftsmanship/v/1.0.0/) · [McKendrick, No Man's Sky, GDC 2017](https://www.gdcvault.com/play/1024265/Continuous-World-Generation-in-No) · [MCV on Murray's talk](https://www.mcvuk.com/sean-murray-discusses-no-mans-sky-development-at-gdc/) · [Manor Lords wiki, burgage plots](https://wiki.hoodedhorse.com/Manor_Lords/Burgage_plot/es) · [GDC 2012, GlassBox](https://gamedeveloper.com/design/gdc-2012-breaking-down-em-simcity-em-s-glassbox-engine) · [Willmott, Inside GlassBox](https://www.andrewwillmott.com/talks/inside-glassbox) · Assassin's Creed Unity, Firewatch, Cities: Skylines 1, RDR2, Horizon, Far Cry 5 and Wildlands: the sources in `performance-at-scale.md` and `kits-and-generation.md`

Ours: `docs/plan.md`, `inputs/2-generation-performance.md`, `kits-and-generation.md`, `performance-at-scale.md`, `tools-and-performance.md`, `time-on-screen.md`, `docs/living-fabric.md`, `town-system.md`, `living-world.md`, `trees.md`; `blender/generators/` and `blender/resolver/` as checked on 21 October
