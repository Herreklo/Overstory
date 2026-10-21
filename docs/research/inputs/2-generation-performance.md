# Inputs 2: generation and performance

A digest of two craft studies for the building-blocks architecture (`docs/plan.md`, What the architecture decides). It decides nothing. It sets out the evidence so Monday's Fable session can decide from it.

The studies, and the short names used below:
- **K**: `docs/research/kits-and-generation.md`;
- **P**: `docs/research/performance-at-scale.md`.

"rec n" is item n of a study's "What we should do". Claims about our code were checked on branch `lt/1-harbour-street` in `stone.py`, `wall.py`, `blender/resolver/`, `Stone.shader`, `PC_RPAsset.asset`, `ArtImport.cs` and `.gitattributes`. Our own arithmetic is marked (ours). Sections 3 and 4 are joint, because most conflicts sit between the two studies.

## The baselines in the studies' terms

| Baseline (22 October, M4) | What it means |
| --- | --- |
| One stair with its walls: about 816,000 triangles | Two-fifths of the 2 million triangle frame budget in `foundations.md`. P says "a fifth", against the old 4 million. About 130 times the city tier's 2,000 a flight, because no level exists (P, Where we stand). |
| The gully's flight: 67 s, 16 MB FBX | A thousand flights take 19 h and 16 GB, or 36 GB with their walls. A kilometre of wall is about 5 million triangles and 200 MB of FBX today. With libraries and bakes it is about 50,000 instance records and 30 MB of maps (P, Our approach, estimate). |
| The house generator: about 13 buildings a second at test quality | (ours) A kilometre of street with 8 m frontages on both sides holds about 250 houses: about 20 s. 100,000 buildings take about 2 h on one process. Final-quality time per house is unknown. At a flight's 67 s, a kilometre of street would take about 4.6 h. |
| Git 2.2 GB; Unity 407 MB of art, 272 MB of it stone | Every FBX sits in plain git with no LFS (`.gitattributes`). P rec 9 takes generated meshes out of git. |

## 1. kits-and-generation.md

### In short

- Standards come before parts: grid, footprints, pivots, opening sizes and storeys (K §1, Bethesda).
- Shipped cities are a chain of stages run in a fixed order and deterministically. Heroes and filler share one footprint and one set of metrics (K §2).
- Change rides on parts, never on whole-building swaps. Cells and sockets become dated records with fills, and a removal leaves a mark (K §5).
- Hand curation survives regeneration only behind pins anchored to semantic ids (K §4; Lipp 2008 and 2011).
- What our framework lacks: stages, kinds as data, one channel spec, one export, a pack metrics table, part definitions (K §6).

### Against the bar

- **Primary sources read** where they opened: Bethesda's decks (slides 1 to 100 of each), the masters' articles, the CityEngine and PCG docs, Lipp, Compton, Rome Reborn, City Sample, the Wildlands interviews. Not opened: Müller 2006, Wonka 2003, Fallout 4's slides 101 to 274, the video-only talks (K, Gaps).
- **Marking** is consistent. The unverified claims prop up illustrations, not proposals (City Sample's counts, CGA snap lines, Spider-Man's interiors, Houdini's price).
- **Checked here,** hardest because K's searches ran out:
  - `bpypolyskel` is **GPL-3.0**. Its README states the 99.99 per cent on 320,000 OpenStreetMap roofs, so that claim is now primary. It runs outside Blender with `mathutils`. GPL is fine in an offline tool, but it cannot ship inside a closed game.
  - A meshoptimizer Python wrapper exists: `meshoptimizer` on PyPI, MIT, a 0.2.30a0 pre-release from February 2026 with one maintainer. Its `simplify_with_attributes` takes attribute weights and a vertex lock. Border locking is undocumented.
  - The claims about our code hold. `stone.lay` is 483 lines with a nested `put()`. The headers of `stone.py` (line 16) and `wall.py` (line 13) say UV2.y holds variation, while the code writes water there. `_shop_fitted` filters the covered window cells out of the plan (`resolve.py` 427). A cell keeps one `original`.
- **Concrete** on the Blender side: stages, a kind's fields, a part sidecar, fit modes. Thin on what Unity does with a plan, which it hands to P. Roofs (K §5) is one paragraph. Every cost is a guess (K, Gaps).
- **Verdict: meets the bar with gaps that change no decision** about the framework. The exception is shared with P (The shared shortfall, below). K asserts that Unity "places parts from the library at the plan's transforms and runs no generation" (K §6) without studying it.

### Decisions it proposes

*Scope* means the decision is listed in `plan.md`, What the architecture decides. *Open* means delegated to the architecture and not yet taken.

| # | What | Why | Cost | Depends on | Alternatives weighed | Status |
| --- | --- | --- | --- | --- | --- | --- |
| K1 | Seven stages for every kind (facts, plan, life, geometry, bake, export, checks), each output hashed data | Shipped cities run stages in order and regenerate from inputs (K §2). Stone has no plan stage (K §6, not right 2). | about 4 d (rec 1) | K2 | Houdini (out); Geometry Nodes, worse for diffs and hashes (K §3) | scope; open |
| K2 | A kind as data in `blender/kinds/`; one runner `generate(kind, thing, year, tier)`; one export; one `channels.py` | Monolith copied into `wall.py`; channel headers drift; three exporters (K §6, not right 1, 7 and 9; checked) | about 2 d (rec 2) | K1 | copy and edit per kind (today) | scope; open |
| K3 | A metrics table per pack, by era (storeys, openings, rises, kerbs, thicknesses, the grid) | Standards before pieces (K §1). Storeys of 3 m in the skill and 2,850 to 3,000 mm in `eras.py` (K §6, not right 4). | about 2 d with K4 (rec 3) | the pack format | the skill's 1 m module | scope; open |
| K4 | A definition per part family (`made_as` fixed or fitted, sizes, fit modes, stretch, pivot, sockets, removal marks, tiers, variants), and a kit validator | Kronenberger, Klevestav, Bethesda (K §1, §6) | in K3, then minutes a part | K3 | hand-modelled `.blend` parts (the skill) | open; tension with `CLAUDE.md` (conflict 6) |
| K5 | Fit in order: exact, stretch, adaptor, change the opening, refuse | K §5, Fitting | inside K6 | K4 | `reduced` only (today) | open |
| K6 | Cells and sockets as dated records; fills as a list; nothing deleted; each removal leaves its part's mark | K §5. `_shop_fitted` deletes cells (checked). | about 2 d, plus a fixture hash migration (rec 4) | K4 | world states, whole swaps (K §5, Alterations) | scope; open |
| K7 | The ground floor as its own grammar; a control layer of a few discrete, correlated decisions per building | City Sample's base and upper styles; Instant Architecture (abstract only); Boris the Brave (secondary) (K §5, §4) | about 2 d (rec 5) | K6 | one grammar per façade | open |
| K8 | A one-dimensional grammar: start, fill, end, corner, fallback, a fit rule | Unreal PCG shape grammar (K §3) | 1 to 2 d (rec 7) | K4 | code per kind | scope; open |
| K9 | Pins as facts on semantic anchors; recorded reseeds; a stress test per kind; expressive range; counts per tier | Wildlands' lock; Lipp; Compton; Smith and Whitehead (K §4) | about 2 d (rec 8) | stable ids from K1 | Wildlands' coarse lock | scope ("locks"); open |
| K10 | Things never repeat. Manufactured pieces come from small libraries, hand-made from large libraries fitted by stretch. Only what wear shaped is unique. | K §6, §7; For Øystein 1 | about 1 d per family (rec 6) | P8 | every piece unique (today) | **conflicts** with the decided "Nothing repeats unless it was factory-made" (conflict 5) |
| K11 | The hero made by the generator with pins: House A, then twelve | K §4, Hero | part of plan step 2 (rec 9) | K9 | a hand-made hero | scope; open |
| K12 | The room behind each window in the plan (floor, kind, lit, household) | K §5, Interiors | half a day (rec 10) | K6 | migrating at step 8 | open; overlap 13 |
| K13 | `bpypolyskel` and meshoptimizer, when needed | K §3; licences checked here | about 1 d each (rec 11) | none | Houdini (out) | open; GPL keeps `bpypolyskel` offline |
| K14 | The plan is the contract: Unity places parts and runs no generation | K §6; the `street.json` precedent | none | none | not weighed | **asserted, not studied** (The shared shortfall) |

Already decided: no Houdini (`NOW.md`). Left out as low stakes: wave function collapse only for local fit at junctions, never failing silently (K §3).

### What every part or thing must carry (K)

- **Part definition:** id, family, era range, `made_as`, size ranges, fit modes and stretch limits, a named pivot, sockets with the families they accept, removal marks, budget per tier, variant count (K §6).
- **Plan instance:** part id, variant, seed, placement in integer millimetres, the fit used, the fact or event that placed it, its sockets (K §6, stage 2).
- **Dated cell:** the opening (position, size, year, cause) and its fills over time (part, event, years, fit). **Dated socket:** its occupants over time and each removal's mark (K §5).
- **Per building:** the control layer's decisions. **Per window:** the room behind it (K §5).
- **Pins:** a semantic anchor and provenance, checked again on every rebuild. Reseeds are recorded (K §4).
- **Hashes and counts:** the plan hash, plus part counts, unique meshes and triangles per tier (K §4).

## 2. performance-at-scale.md

### In short

- The style's distance rule is the budget's rule: real geometry where a pixel can hold it, painted detail beyond. Levels are chosen by error in pixels (P, What a pixel holds).
- Our stone draws its eye-level detail at every distance: 816,206 triangles a stair, no levels, one mesh 33 m long (P, Where we stand).
- Cut chunks at piece boundaries, make levels in the generator, cast shadows from proxies, and bake history channels rather than final colour into per-chunk maps (P §5; Our approach 1 to 5).
- Repeated small pieces come from libraries as instances. Unity 6.6 has the Resident Drawer, BRG and a 32-bit user value per renderer, but URP has no HLOD and no virtual texturing (P §1, §2).
- Measure first: a frame-time harness, golden views with FLIP, mesh hashes and export checks, about two weeks in all (P §6).

### Against the bar

- **Primary sources read:** Unity 6 manuals throughout, AC Unity and RedLynx (SIGGRAPH 2015), Firewatch, The Order, Frostbite, URP's test settings, FLIP, meshoptimizer. Not opened: Ghost of Tsushima's grass, Horizon's slides, Spider-Man, Brucks' impostors (P, Gaps).
- **Marking** is mostly right. Five third-party frame studies are unmarked (GTA V, Cities: Skylines 2, RDR2, Cyberpunk, Mafia). They are captures, not the makers' words: read them as (secondary). Each decision leaning on them also rests on a primary source or on P's pixel arithmetic, which I re-checked: 0.48 mm a pixel per metre, so a level is safe beyond about 2,000 times its error.
- **Concrete:** the most concrete study we have. Its readings of our project hold (`PC_RPAsset`: MSAA 4×, shadows to 200 m, Resident Drawer off; `Stone.shader` at `#pragma target 3.5`; Unity 6000.6.6f1).
- **Stale or thin:** its frame budget is the old 4 million triangles, not 2 million. It offers 30 fps, but 60 is decided. Its trees ignore the M4's alpha-test cost (`ground-cover-and-plants.md`). Streaming gets one line. Texture memory is estimated for a 1.5 m wall only (P §4), not for houses. (ours) At P's 1 cm a texel and 2 bytes, both fronts of a kilometre of two-storey street (2,000 by 7 m) come to about 280 MB. At the 4 to 8 cm of `materials-at-scale.md`'s history maps they come to 4 to 18 MB.
- **Verdict: meets the bar with gaps that change no decision** about levels, chunks, bakes, shadows and the quality tools. On scale it falls short, together with K.

### The shared shortfall

Both studies assume generation runs offline in Blender and that Unity only reads plans and meshes (K §6; P, Our approach 8). So does `living-fabric.md`: "Life is computed offline per thing". Two settled points press on that:
- the player's acts change the 3D world through the record, and years pass in play (`NOW.md`, Decided);
- `plan.md` asks for generation "cached, deterministic, on demand near the camera".

A built player cannot import FBX (glTFast loads glTF at run time; `tools-and-performance.md`), cannot run Blender, and cannot ship GPL code. Mesh LOD runs at import only. So change made in play, or generation on demand, needs those stages in C# inside the player, or assembly from library parts only with history written into instance data and maps at run time. Neither study weighs this. It decides which stages exist twice, determinism across languages, the chunk format, and whether worn geometry (a tread's hollow) can change in play.

**A gap-closing pass should look for:** Unity 6's run-time mesh paths (`Mesh.MeshData`, `AllocateWritableMeshData`, `AsyncReadManager`, Addressables) and their cost on the M4; how games that rebuild in play do it (Tiny Glade, Townscaper, voxel chunk rebuilds); determinism across languages (our SplitMix64; Burst's float rules). The scale test gives the numbers (section 4).

### Decisions it proposes

| # | What | Why | Cost | Depends on | Alternatives weighed | Status |
| --- | --- | --- | --- | --- | --- | --- |
| P1 | Choose levels by error in pixels; keep the median visible triangle at ten pixels or more | 2×2 quad shading; the pixel arithmetic, checked (P, What a pixel holds) | inside the checks | the harness | metres per tier (`foundations.md`) | scope; open |
| P2 | Six levels: close (to 8 m), near (8 to 20), street (20 to 80), city (80 to 200), district (200 on), far | One tier spans four to five times in distance (P §5 table) | none | P1 | four tiers (`foundations.md`) | refines `foundations.md`; open |
| P3 | Chunks cut at piece boundaries (flights 3 to 5 m, walls about 4 m, paving 4 by 4 m), each with its own bounds, levels and caster | AC Unity's clusters (primary). GPU occlusion culls by bounding sphere, so a 33 m flight is never culled (P §1). | within 4 to 6 d (rec 3) | K1's plan | merging per thing (K) | scope; **conflicts** (conflict 1) |
| P4 | Each part generator makes its own levels from the same seed and outline | Mesh LOD "might produce undesired results" and says nothing on UVs; Decimate weighs no attributes (P §1) | in rec 3 | K4's tiers | Mesh LOD (rec 2's afternoon test); meshoptimizer for natural stone and land | open |
| P5 | History as a pure function `history(piece, point)`, split into intrinsic channels (shape) and extrinsic ones (place) | `put()` already computes channels from facts and a point (checked); the split lets a library piece carry a lane's years (P §2, §5) | 2 to 3 d (rec 4) | K1's life stage | carrying attributes through simplification | `plan.md` adopts the function; its carrier is open (conflict 2) |
| P6 | Bake inputs, not outputs: per-chunk maps (piece, joints, height, history channels, relief folded into roughness), and a texture path in `Stone.shader` | HLOD and Simplygon freeze the light; The Order's offline layers and roughness (P §5) | 5 to 8 d (rec 5) | P3, P5 | baking final colour; a generic tiling texture, which claims joints that are not the lane's (P §2) | scope; overlaps materials (conflict 2) |
| P7 | Shadows from proxies: close and near never cast, street in the first cascades, city beyond, small parts never | Firewatch's proxies (primary); Cities: Skylines 2's shadows took 40 of 87.8 ms (P §1) | about 1 d (rec 6) | P3 | none | scope; open |
| P8 | Kit parts through the Resident Drawer with the Renderer Shader User Value; swarms (setts, slates, grass) through BRG | Unity docs; RedLynx drew 250,000 objects (P §1) | 1 to 2 d for shaders (rec 10); 4 to 6 d for libraries (rec 11) | P9, K10 | Entities Graphics, not needed | open; measure, since the Resident Drawer "can get slower" when GPU-bound |
| P9 | Shaders made ready: `#pragma target 4.5`, `DOTS_INSTANCING_ON`, `LOD_FADE_CROSSFADE`, `unity_RendererUserValue` | The Resident Drawer's requirements (P, Our approach 7) | in rec 10 | none | none | open; cheap |
| P10 | Layouts evaluated at a point where the craft allows (slate courses, sett rows by a hash per row) | Then distant levels draw the same slates with no bake (P §2) | not costed | the layout written identically in Python and HLSL | baking | open; a duty of determinism across languages |
| P11 | Field tiles per chunk (64 by 64 texels a 4 m chunk) in texture arrays | A town-wide map at 5 cm is impossible (P §4) | in rec 5 | the fields (`living-fabric.md`) | none | open |
| P12 | Generated meshes out of git, with a manifest of hashes; a binary chunk format later | 36 MB a stair; `.git` at 2.2 GB (P, Our approach 8) | about 1 d (rec 9) | P13's hashes | LFS (`CLAUDE.md`) | scope; **conflicts** (conflict 10) |
| P13 | The quality tools: the frame-time harness (four paths, three lights, A/B switches, gates both ways); golden views with FLIP, accepted only by Øystein; mesh hashes; export checks (budget per level, each level at most 60 per cent of the one before, median triangle); variety plots | Frostbite; URP's own tests on Metal Mac minis (P §6) | 3 d harness, 4 d golden, 2 d hashes and checks, 1 d variety | none | eyes only | Monday's tools session |
| P14 | Tree levels and impostors; GPU grass from the fields; a district level merged per block | Firewatch; Ghost of Tsushima and Horizon (secondary); GTA V; Cities: Skylines 1 (P §3; recs 12 to 14) | about a week each | P1 to P6 | Unity's terrain details, which know no fields | later steps; trees conflict 7 |

Already decided or ours: the target is 60 fps at 1440p on the M4 (`NOW.md`), which closes P's 30 fps option. Antialiasing (MSAA against TAA or STP) is a craft choice, made on measured frames.

### What every part or thing must carry (P)

- **Per level:** its geometric error in metres, its triangle count against the level's budget, its shadow role (P1; P, Our approach 5).
- **Per chunk:** id and bounds, cut at a piece boundary, and the index of its field tile (P, Our approach 1; §4).
- **History, split by cause:** intrinsic channels in the mesh (face kind, distance to an edge, the piece's own occlusion). Extrinsic ones per instance or field tile: years, footfall, water, damp, care (P §2).
- **Per instance:** transform, extrinsic facts, and a 32-bit user value or BRG offset into a buffer of the thing's facts (P §1, §4).
- **Per chunk bake:** piece id, joints, height, history channels, roughness with the relief folded in (P §5).
- **Material:** one per chunk, with a texture-array index for the family (P §4).
- **Hashes:** a mesh hash (positions at 0.1 mm, channels quantised) in a manifest, and a cache key from the facts and the rules' version (P §5, §6).
- **For picking,** which `plan.md` requires and neither study names: a record id for every drawn piece at every level. That is per vertex at the close level, the user value for instanced parts, and P's piece map, which can double as the pick map, at the street and city levels. (ours) At the district level, a building id in the block atlas.

## 3. Conflicts and overlaps

| # | Between | The claims | What it touches |
| --- | --- | --- | --- |
| 1 | K, P, `land-rock-and-water.md`, `foundations.md` | **The unit of merging.** K §6: fitted parts are "Unique geometry, merged per thing". P: "A flight is written as runs of three to five metres". Land: "Chunks of 64 m". Foundations' city tier: "runs of parts merged (a flight, a wall, a house)". | chunk ids, streaming cells, culling (question 3) |
| 2 | K, P, `materials-at-scale.md`, `living-fabric.md`, `plan.md` | **The history carrier.** K §6: results "baked per vertex for one shader stack". P §5: close "per vertex, as now"; street "the chunk's baked maps". Materials: "Houses cannot carry history per vertex at all"; history maps at "about 2 cm a texel under the feet and 4 to 8 cm on walls". Living fabric: "the city tier bakes the life into the merged mesh's vertex data". `plan.md` has adopted "history maps instead of per-vertex channels". | the channel spec; port step 2 (question 2) |
| 3 | K, P, `tools-and-performance.md`, `NOW.md` | **Generation in Unity.** K §6: Unity "runs no generation". P §2: slates "computed in a shader"; P §3: grass from "a compute pass". Tools: "Building meshes at runtime … Merge each neighbourhood's walls and roofs". `NOW.md`: "The player's acts change the 3D world". | The shared shortfall (question 1) |
| 4 | K, P, `tools-and-performance.md` | **The simplifier.** K §3: "Blender's Decimate; Unity 6's Mesh LOD at import; meshoptimizer". P §1: Decimate "weighs no attributes"; with Mesh LOD "joints are likely to melt". Tools: Mesh LOD works "only in the editor". | P4; rec 2's test settles it |
| 5 | K, P, `plan.md`, `NOW.md` | **Repetition.** `NOW.md`, Decided: "Nothing repeats unless it was factory-made". K §7: wall "face stones may repeat beyond a few metres apart, turned and mirrored". P: "a few hundred wall stones in size classes". `plan.md`: "hand-made ones from large libraries". | K10, P8 (question 3) |
| 6 | K, `CLAUDE.md`, the skill | **Do generators make geometry?** `CLAUDE.md`: the generator "does not invent their geometry". K §6: "fitted: a part function called per instance because its shape is a fact". The `blender-generators` skill says parts are hand-modelled `.blend` files. | the rule's wording; the skill update in `plan.md` |
| 7 | P, `ground-cover-and-plants.md` | **Trees on the M4.** P §3: the near birch at 60,000 triangles "is fine within 20 m"; far crowns with "lower alpha cutoff, broader cards". Ground cover: "every layer of cards … costs a shading pass"; "Our birches are probably the dearest pixels". | the trees' levels; the harness measures it |
| 8 | P, `foundations.md`, `NOW.md` | **The frame budget.** P: "4 million visible triangles … on a mid-range card", and an offer of "1440p at 30 frames". Foundations: "about 2 million visible triangles"; `NOW.md`: 60 fps on the M4. | Recheck P's tier plan against 2 million. |
| 9 | P, `painted-marks-in-motion.md` | **Where fades sit.** P ties the close level to `OS_Near`, "between 2.5 and 8 m". Painted marks: our stills fade "between about 3.7 and 12.5 m … against 2.5 and 8.3 m in play". | Judge level switches at the game's pixel, with the motion-sheet renderer. |
| 10 | P, `CLAUDE.md`, `.gitattributes` | **Git.** `CLAUDE.md`: "Large binary files (renders, FBX) go through Git LFS". `.gitattributes`: "Git LFS uploads are not reachable from the cloud workspace". P: "Generated meshes out of git". | P12; the Practical line in `CLAUDE.md` |
| 11 | P, `interface-and-inspection.md` (being written) | **Ids under the Resident Drawer.** Interface: ids for instanced parts "must come from instance data we control or from position". P §1: the Renderer Shader User Value is one 32-bit value per renderer that "avoids breaking GRD instancing". | the picking path for kit parts: the cheap path may already exist |
| 12 | K, P, `living-fabric.md` | **Overlap: hashes.** K's plan hasher, P's mesh hashes and the living fabric's life hasher, each cached by "a hash of its facts and the rules' version". | one tool with stages |
| 13 | K, `fronts-windows-and-signs.md` | **Overlap: interiors.** K §5: a room per window by "its floor, its kind, lit or not, whose household". Fronts: "the room's box … as instance data". | The seam needs both. |
| 14 | K §4, P §6 | **Overlap: expressive range.** Both propose two-metric plots with a sheet per cell. | one tool |

## 4. Unknowns

### Learned on the way

| Unknown | Study | Where it is learned |
| --- | --- | --- |
| Whether a library stone stretched to fit reads true at eye level | P, Gaps; K §6 | a look test on the slab sheet, before libraries become a rule |
| How Mesh LOD treats six UV channels and sharp edges | P rec 2 | an afternoon on the gully's FBX, before port step 4 |
| `Stone.shader`'s cost a pixel; what the Resident Drawer and GPU occlusion gain | P, Gaps | the harness, Monday and Tuesday |
| Disk and memory of bakes per kilometre | P §4 | the first chunk bake (port step 4) |
| Final-quality time to generate a house | K, Gaps | House A |
| Whether a new kind really takes days | K | the second kind after the gully (kerb or landing setts) |
| Whether a layout evaluated at a point matches the near pieces | P §2 | the first roof |
| Whether pins survive a change of rules | K §3 (Lipp) | the first rule version bump with pins in place |
| How fast the camera may rise before streaming shows | P, Gaps | when streaming exists |
| Which variety metrics predict readability | K §4, P §6 | the first variety sheet read by cold readers |

### What the scale test must answer before the architecture settles

`plan.md` leaves where generation runs and how the town streams provisional until the scale test. As planned, the test measures a district in clay. To settle the architecture it must answer:

1. **Build time** per building and per kilometre, on one process and on several, at test quality, with the gully's 67 s as the final-quality point. *Settles:* generating everything offline against generating on demand.
2. **Disk and resident memory per kilometre, at each view,** with synthetic instance buffers and per-chunk maps at the studies' densities (1 cm, and 4 to 8 cm). Clay meshes alone under-count both. *Settles:* the chunk format and the streaming radius.
3. **Frame time** at the street stop, 12 m and the city camera, with about a thousand houses in clay and with a 1,500-triangle stand-in. *Settles:* whether the district level is needed now.
4. **Time in a built player** to load one chunk from a run-time format (not FBX), and to regenerate one changed thing and its chunk. *Settles:* whether change in play is affordable, and where it runs.
5. **Draws and GPU time** with the Resident Drawer and GPU occlusion on and off. *Settles:* the instancing route.

Items 2 and 4 are not in the plan as written.

## Across both studies

### The generator framework they imply

- **Stages** (K §6, with P's additions):
  1. facts;
  2. plan: part instances in integers, each with its chunk, its levels and the fact that placed it;
  3. life: `history(piece, point)` from the record and the date;
  4. geometry per level and chunk: fitted parts as unique meshes, fixed parts as instance lists;
  5. bake: intrinsic channels into library meshes; extrinsic ones into instance buffers, field tiles and chunk maps;
  6. export: a manifest, meshes or binary chunks, instance records, maps;
  7. checks: validation, budgets per level, hashes, golden views.
- **Kinds as data:** K's eight fields. For each level, P adds the error, the budget and the shadow role.
- **Runner:** one entry, `generate(kind, thing, year, level)`. Batches run on `multiprocessing`, with seeds by SplitMix64 from stable ids.
- **Hashes:** one chain, each link a cache key: facts and the rules' version, then plan, life, mesh per chunk and level, and bake.

### Distance levels and instancing

| Level | Distance | Shape | History carried by | Drawn as | Casts |
| --- | --- | --- | --- | --- | --- |
| Close | to about 8 m | every piece in full | per vertex (P) or history maps (materials): open | merged chunks; library parts through the Resident Drawer or BRG | no |
| Near | 8 to 20 m | pieces simplified from their own seed | sampled again from `history()` | as close | no |
| Street | 20 to 80 m | bevelled boxes; ribbons with true top lines | the chunk's maps | chunks; kit parts at lower levels | first cascades |
| City | 80 to 200 m | merged per run | the maps' mips | chunks | beyond |
| District | 200 m on | merged per block | a block atlas | one draw a block | coarse |
| Far | horizon | terrain, impostors | baked colour | impostors | no |

Levels switch by error in pixels, hidden by a dithered cross-fade (P §5).

### The order to build them

Hardest to change first, measured before changed (`CLAUDE.md`, Working in the right order):
1. **Measure** (Monday): the harness, golden views through the motion-sheet renderer, mesh hashes (P13).
2. **The scale test** (Tuesday), with items 2 and 4 added. It settles question 1.
3. **The contracts:** the channel spec, kind and part schemas, the metrics schema, the hash chain, chunk and record ids (K2 to K4; P5's split).
4. **The gully's port:**
   - stages with an unchanged geometry hash (K1);
   - history into its carrier (P5, P6);
   - chunks and generator levels (P3, P4), then proxies (P7);
   - shaders ready for the Resident Drawer (P9).
5. **Bakes and git:** the texture path (P6); meshes out of git (P12).
6. **Before the houses:** metrics and part definitions (K3, K4), dated cells and sockets (K6), the ground floor and control layer (K7), the one-dimensional grammar (K8), pins (K9), libraries with BRG (K10, P8), then House A (K11).
7. **Later:** the trees' levels, the district level, GPU grass (P14).

**A cost mismatch to settle:** the studies' estimates for the port (K rec 1; P recs 3 to 6) add up to 16 to 22 Opus-days. The plan gives it three days. The cut line moves levels and proxies to the next week, but the stage split and history alone are 6 to 7 study-days.

### The three questions Fable most needs to settle

1. **Where does each stage run, and does any of it run in the player?** Play changes the record and years pass in play, but both studies assume offline Blender. The answer decides:
   - which stages need C# twins;
   - the chunk format;
   - determinism across languages;
   - whether worn geometry can change in play.

   The scale test's items 1 and 4 inform it.
2. **What carries history at each level, and at what texel size?** The options: per vertex at the close level (P), maps at every level (materials, `plan.md`), or vertex data at the city level (living fabric). With it: what is baked, and what is evaluated at a point. The answer decides the channel spec, port step 2, and disk per kilometre: about 280 MB against 4 to 18 MB for a kilometre of house fronts (ours).
3. **What is drawn unique, what comes from libraries, and in what unit?** Two parts:
   - square the decided "nothing repeats unless it was factory-made" with large libraries of hand-made stones;
   - choose the merge unit: per thing, chunks of 3 to 5 m, the land's 64 m, or a streaming cell.

   The answer decides the libraries, BRG, the plan's chunk ids and picking.
