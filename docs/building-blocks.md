# The building blocks

How every material, kind of thing and system is built, for the first town, a bigger city and the three example games. Reasons are in `docs/research/building-blocks-decisions.md`, by section. The order of work is in `docs/plan.md`, whose step names (3.0 to 3.4, 1c, House A) are used here.

The stack: Blender 4.x Python offline; Unity 6000.6, URP 17.6, C# with Burst. The reference machine is the base M4 Mac mini, 16 GB unified memory, 60 fps at 1440p, so 16.7 ms a frame.

*Provisional* marks what a named measurement settles; Open until measured lists each with the default built on meanwhile. Everything else is firm.

## In short

1. **Parts are made offline; the town is assembled in the player.** Fixed parts are judged meshes from Blender. Fitted parts are judged functions. Plan, life, placement, fitted geometry, extrinsic bakes and cheap checks run in C# in the player.
2. **Contracts are files, not prose.** JSON Schema in `schemas/`, golden fixtures per stage, parity tested in data at every stage boundary before any mesh.
3. **History is a function of the record and the date.** Maps hold inputs (rates, reset years, age offsets). The date is a shader global, so a jump costs one uniform. Every far shell carries its own atlas, painted or plain, and alone caches an output bake, invalidated by the change query.
4. **Ids are stable down to slot and fill; pieces are derived.** Record ids are typed strings, never reused. Piece and pick indices exist only at draw time.
5. **Budgets are in milliseconds, megabytes and triangles, per pass and per kilometre, on 16 GB.** All provisional, but a line exists for each before geometry moves. The frame is pixel-bound today, so shaders are budgeted and A/B'd before triangles are ported.

## The stage map

Every kind runs through seven stages, each with a hashed output.

| Stage | Runs where | Output |
| --- | --- | --- |
| 1 Facts | offline: the pack, fixtures, the curated 1989 record; the engine's own process in play. Data, never code | record hash |
| 2 Plan | C# core in the player, also for golden views and the shipped cache | plan in integers (mm); plan hash |
| 3 Life | C# on change in the player; the state at the date in HLSL | life intervals per piece, texel inputs; life hash |
| 4 Geometry | fixed parts in Blender only; fitted parts and placement in C# with Burst | mesh per chunk and level; mesh hash |
| 5 Bake | intrinsic channels into library parts in Blender; extrinsic maps, field tiles and shell atlases on the player's GPU | map pages; bake hash |
| 6 Export and cache | library parts as FBX with a JSON sidecar through the editor importer; chunks never as FBX, but as a binary cache in `cache/chunks/` and `StreamingAssets` | the chunk file |
| 7 Checks | offline in Python (record, kit, parity, mesh hashes, golden views, motion sheets, cold readers); in the player in C# (budgets per level, refused fits, plan validity, the cache verified on load) | pass or fail, logged |

**One source of truth per stage and kind,** since two live sources drift. Python (`resolve.py`, `upkeep.py`, `blender/parts/*.py`) is the source until a kind's port. Then it is frozen as the parity reference, and deleted once the C# passes parity on the golden fixtures and one strict review. Look sheets then run the C# through Unity in batch mode. Plan and life flip the week after the gully port; the house resolver before House A; geometry per family, stone first.

Reasons: decisions §0, §1.

## Contracts and where files live

**Schemas** are hand-written JSON Schema (draft 2020-12). Python validates with `jsonschema` (MIT). C# types are hand-written twins, held to the schemas by parity tests over `fixtures/golden/<kind>/<stage>.json`.

| File in `schemas/` | Describes |
| --- | --- |
| `record.schema.json` | any record: id, kind, provenance, precision, lifespan, events, links, keeper and care, pins |
| `kind.schema.json` | a kind: stage parameters, slots, families, levels and budgets, motion, affordances, fields read and written |
| `part.schema.json` | a family: `made_as`, era, sizes, fit modes, pivot, sockets, removal mark, variants, error and budget per level, shadow, collision and motion roles, intrinsic channels, each procedural mark's smallest feature (which sets its texel), lifecycle |
| `plan.schema.json` | an instance: part path, variant, seed, placement in mm, fit, placing event, chunk id |
| `slot.schema.json`, `interval.schema.json` | slots and fills; life intervals (from, to, reset year, rate, age offset, cause) |
| `channels.json`, `maps.json`, `layers.json` | the vertex and texel channels with byte widths; the map and layer registries |
| `chunk-format.md`, `chunk.schema.json` | the binary chunk as a versioned byte table, one reader per language tested on one golden chunk |
| `world-state.schema.json`, `change-query.schema.json` | the world state; `changes(scope, t0, t1)` |
| `naming.md` | one page of naming grammar for ids, part paths, kinds, materials, chunks, maps and fields, written before the first kind file |
| `CHANGELOG.md` | every schema change with its migration |

**Folders.** `schemas/`. `kinds/<kind>.json` at the repo root (stair, wall, house, birch, lamp, bollard, natural-stone, ground-act), because both languages and the player read it. `packs/<city-year>/`. `blender/parts/<family>/` for part code, with C# twins later in `unity/Assets/Code/Parts/`. `fixtures/` for records, golden fixtures and the engine run. `migrations/`. `cache/`, untracked, for chunks, tree timelines and exported library meshes. `tools/` for checks and builds.

**Versioning.** Every record file carries `schemaVersion`. `tools/migrate.py` runs `migrations/NNN_<name>.py` on every fixture, and a check fails if any is behind. C# reads only the current version. The curated 1989 town and its pins migrate by the same scripts, so a rule change never kills it.

**The hash chain** (`tools/hashes.py`, later `Hashes.cs`): `schemaVersion`, `rulesetVersion` (kind file and part function versions) and `worldSeed`, then the record, plan, life and mesh hashes, then `bakeVersion` (the `OS_History` include, the layer curves, the bake and shell-bake code, the shaders) and the bake hash. Each is a cache key, and a stage with unchanged inputs is skipped.

**Generated files are rebuilt, not tracked.** FBX, chunks, library meshes and tree timelines leave git; hash manifests and part sources stay. Golden baselines keep one current baseline per kind, view and light in git, at the size judged; a superseded one leaves the tree and stays as its hash in the manifest. Plain git until LFS is reachable. The tree drops its 385 MB of FBX at 3.1. History is not rewritten.

Reasons: decisions §2, §10.

## Seeds and determinism

The same building looks the same until its history changes it. Five rules hold in Python and C#, and in HLSL where a layout is evaluated at a point:
1. Seeds come from stable ids (part path and purpose) through SplitMix64. Never `random.Random`, which may change between Python versions, and never keys from formatted floats, which re-draw neighbours when a piece moves. A replaced part takes a new id and so a new seed.
2. Choices use only integers, the four operations and square root. A transcendental may place a vertex, never choose.
3. Plans and life are integers: mm, per mille, years and months.
4. Geometry is compared by tolerance.
5. Everything sorts by stable id.

**One hash spec.** Python's `hashing.py` is it, since every plan hash and fixture already rests on it: FNV-1a over UTF-8, SplitMix64 from `0x2545F4914F6CDD1D`, `unit = (h>>11)/2^53`. `Core/Hash.cs` matches it. Both reproduce the 200 pairs in `fixtures/golden/hash-vectors.json`.

**Comparing meshes.** Bit-exact within a language. Across languages by tolerance per chunk and level (positions 0.05 mm, each channel its quantum), since a quantised hash flips at a boundary. FLIP on golden views last. Burst's deterministic float mode only for the shipped cache verified on load.

**Debugging.** `tools/diff_stage.py` diffs by stable id at every stage. A two-machine run comes in the scale test week. `packs/<pack>/tooling.json` pins Blender and Unity.

Reasons: decisions §3.

## Records and ids

**One structure,** so there is one change query, one pick path and one superposition check. A thing holds slots (openings, sockets, surface regions, panes, affordances), never deleted. A slot holds fills in date order, each with its part, placing event, from and to, fit, and the mark its removal leaves. A window's surround, a coat and a stone repair are fills. Nothing deletes the cells it covers, and no cell holds a single `original`.

The record admits every kind as data: parts, plants, signs, rooms, lights, garments, carried things, social traces, works phases, photographs. Things nest as part, thing, group and place, and far levels resolve to the thing. Readable text comes only from records.

| Level | Form | Minted by | Survives |
| --- | --- | --- | --- |
| Record | `<prefix>-<token>`: `bld-101`, `st-gully`, `p-812` | its owner: the engine; the pack script for `generated-past` (a counter from world seed and plan unit); by hand for `authored` | everything; never reused |
| Event | `bld-101/13` | the owner, appended | everything |
| Slot | `bld-101/op-n1-2`, `st-gully/tr-17`, `bld-101/sf-n` | the plan stage by the kind's rule in `naming.md`; semantic, never a positional counter | regeneration; a renaming rule change ships a migration |
| Fill | `<slot>/<n>` in date order | appended, never renumbered | regeneration; an out-of-order insertion is a migration |
| Piece | `<fill>#<i>` | the geometry stage | its fill's rules version only |
| Pick index | 32 bits, split by path (under the vertex layout) | the assembler at draw time | one build of its unit; never stored |

`tools/id_check.py` bumps `rulesetVersion`, regenerates, and fails if any record, slot or fill id is lost or born. Pins attach to slot and fill ids. A second pack's ids take its pack id as a prefix at load. A pick resolves through the chunk's table to a record and part path, then to the hierarchy level that suits the distance.

**Every record and event carries** its place among the five kinds of thing on screen; provenance as `simulated`, `generated-past`, `derived` or `authored`; precision (year, decade, month); actor; weight; where. Every record also names its keeper and its care.

**Checks and lifecycle.** `tools/validate_record.py` checks fills against their slot's dates and size, date order, actor, era, provenance, well-formed unique ids, that nothing is deleted, and the facts contract's hand-off rules. A family is `draft`, `judged`, `library`, `deprecated` or `removed`; a removed one keeps its last judged mesh and function as a tombstone, so old records still draw.

**The facts contract** (`docs/facts-contract.md`) uses the four labels. Each game's domain model (a match, an edition, works and prices) gets a row before that game is built: owned by the game's module, `simulated` when the engine runs it, `derived` when the game's rules do. Care comes from money, presence, age and events, never character (Rule 8).

Reasons: decisions §4.

## What a part carries

**The vertex layout.** Meshes at L0 to L2 are written through `MeshData` in the player, so the layout is ours; library parts cross FBX with a sidecar naming each UV set's channel. *Provisional:* byte widths.

| Slot | Content | Format | Bytes |
| --- | --- | --- | --- |
| Position | | Float32×3 | 12 |
| Normal | w is padding | SNorm16×4 | 8 |
| UV0 | grain, metric per piece | Float16×2 | 4 |
| UV1 | atlas address into the chunk's maps | UNorm16×2 | 4 |
| UV2 | mark coordinate, continuous along a run (the brush) | Float32×2 | 8 |
| UV3 | piece index; edge distance in tenths of a mm | UInt16×2 | 4 |
| UV4 | face kind, hollow rate, flutter weight or element depth, own occlusion | UNorm8×4 | 4 |
| UV5, optional | rest position, for deforming and wind-moved parts | Float16×4 | 8 |
| UV6, optional | element index and depth (trees, people, flexible parts) | UInt16×2 | 4 |

That is 44 bytes, 56 with both options. The light's inputs sit in the place pages, not the vertex.

**Shells** (L3, L4) carry 28 bytes. Their ids are constant over each triangle: vertices split where an id changes, and the shader reads them without interpolation.

| Slot | Content | Format | Bytes |
| --- | --- | --- | --- |
| Position | | Float32×3 | 12 |
| Normal | w is padding | SNorm16×4 | 8 |
| UV1 | address in the shell atlas | UNorm16×2 | 4 |
| UV3 | thing index in the cell; part slot (10 bits) and material class (6 bits) | UInt16×2 | 4 |

**The tangent frame.** No tangent is stored. Each shader derives the frame per pixel from the screen derivatives of the UV set its normal detail lives in: UV1 for the bent normal, the maps' relief and the shell's normal atlas; UV0 for a material's grain normal. The same holds at every level. *Provisional:* the gully's A/B at L2 and on shells, where coarse triangles may facet; if they do, a MikkTSpace tangent in SNorm8×4 (4 bytes) joins the layout.

**Per instance.** A kit instance under the GPU Resident Drawer carries its transform and the 32-bit Renderer Shader User Value: the pick index, which also indexes a per-cell `StructuredBuffer` of facts (record and part, seed, reset year, care, season and hue, wind phase, coat-table offset). Swarms (setts, slates, tufts, litter) use our own BatchRendererGroup: transform, part and species, seed and rank, wind phase, field tile. People are skinned, on their own path. *Provisional.*

**The pick index** is a `UInt32` (*provisional:* the picking spike).

| Bits | Field |
| --- | --- |
| 31 to 30 | path: chunk (L0, L1), cell (L2, L3), block (L4), kit instance |
| 29 to 16 | resident unit slot, 16,384 |
| 15 to 0 | piece, thing or instance in the unit, 65,536: UV3's piece index, a shell's thing index, or the cell's facts buffer |

A unit with more than 65,536 takes a second slot. Swarms pick through tile and seed, people by their own path. Lamps, boats, flags and laundry are kit instances and pick through the user value.

**History maps store inputs:** rates (or the fields that make them) and age offsets per texel, reset years per piece and repair surface. Each layer is its material's curve at rate × (date − reset + offset). So a jump costs a uniform, and a watched town draws as a jumped one.
- Maps serve every level, from the atlas UV. Per vertex sit only piece constants and what moves geometry (a hollow's rate), so no hand-over between carriers must match. *Provisional.*
- The unit is the draw chunk. A part's texel comes from its material's target and its marks' smallest feature: 2 cm walked stone, 4 cm walls and trims, 8 cm roofs and ground. A chunk that mixes them packs each part's rectangle at its own texel into one set of pages, addressed by UV1; packing and mip gutters waste about 15 %. *Provisional.*
- A rate change (a gutter, a fallen neighbour, falling care) rebakes the map region on the GPU, not the unchanged mesh. The chunk's invalidation table says per act which pages, instances and whether the mesh it dirties. Rebakes run behind the dated card, 2 ms GPU per 1024×512 page with its compression. Drawing a page takes 0.7 ms and reading it back 0.7 ms (a blit standing in for the bake's shader, so a floor). Compressing it on the CPU takes 5.3 to 8.7 ms (DXT5, since Unity's CPU path offers no BC7): three to six frames' streaming budget. So pages are compressed on the GPU, by an encoder the project does not have yet (*provisional:* the bake's own shader and that encoder, timed on the M4).
- Intrinsic channels (face kind, edge distance, own occlusion) are in the mesh. Extrinsic ones are per instance, field tile or map, so a library sett carries its own lane's years: reset years in the chunk's piece table (by UV3's piece index) or the facts buffer, care in the facts buffer, feet and water held in P0. Damp is the shade's, from water held and the weather.
- The light's inputs (sky seen, ground seen, openness, weather exposure) live in the place pages P0 and P1, with a two-channel bent normal at L0 to L2. Shells drop the bent normal; impostors have their own atlas.
- Every shell carries its atlas (albedo and normal at the date, the light's inputs, the index), painted or plain. It is the one exception to inputs-only maps: the shell caches an output bake of pigment with slow history, invalidated per thing by the change query; drift stays live from the index's reset year. A cached evaluation is still the function. Format reserved at 3.1; the bake comes with the gully's shell.

**The map registry** (`maps.json`) names each map's channels, owner, unit, texel, format, readers and rebuild trigger. *Fields* are coarse and owned by the land. *Place maps* are fine and owned by the chunk, sampled from the fields and the chunk's geometry.

| Map | Channels | Owner, unit | Texel | Format | Read by | Rebuilt when |
| --- | --- | --- | --- | --- | --- | --- |
| Height and sky | height; sky seen, horizon angle | land, 64 m | 0.5 m heart, 2 m beyond | R16 + RG8 | far shadows, horizon, light | a ground act |
| Ground | R soil, G seasonal albedo (an index into the material's range), B wet, A reserved | land, 64 m | 0.25 to 0.5 m | RGBA8 | feet of rock, walls, plinths; blade roots; seen ground | a ground act, the season |
| Fields | a slice each: soil, flow, wetness, wind and salt, sun dose, made ground, feet | land, 64 m | 0.5 to 1 m heart, 2 to 4 m beyond | `Texture2DArray`, R8 or R16 | place-map bakes, placer, deposits | an act, the feet plan, the decade |
| Place P0 | R feet, G water held, B sky seen, A ground seen | chunk | 2, 4, 8 cm | RGBA8 → BC7 | every shader, via `OS_History` | geometry, a neighbour's rain shadow |
| Place P1 | R openness, G weather exposure, B and A reserved | chunk | same | RGBA8 → BC7 | same | geometry, a neighbour |
| History H1 | R polish rate, G lichen rate, B moss rate, A age offset | chunk | same | RGBA8 → BC7 | same | a reset, a rate change |
| History H2, story chunks | R wash, G deposit, B splash, A contact | chunk | same | RGBA8 → BC7 | same | the history budget; a rate change |
| History H3, story chunks, reserved | R carrier (from the water bake), G soot, B salt, A reserved | chunk | same | RGBA8 → BC7 | same | when the layer lands |
| Bent normal | RG direction | chunk | same | RG8 → BC5 | the shade | geometry |
| Deposits | leaves and litter | chunk | 8 cm | R8 → BC4 | ground, plants | the day's wind, feet, keepers |
| Shell atlas | albedo at the date; normal; sky seen, ground seen, openness, weather exposure; index (R thing in the cell, G reset year from the pack's first year) | 32 m cell | 3 to 5 cm | BC3, BC5, BC3, R8G8 uncompressed | shells, blocks | the change query names the thing |
| Impostor atlas | the impostor baker's | species, library | fixed | BC7 | far trees | the species' timeline |

**The layer registry** (`layers.json`) names each layer's page and channel, inputs, curve owner (the material record) and reset rule. Every shader reads layers through one `OS_History(address, layer)` in one include. A new layer (soot, salt, rust runs, carried stains, splash bands, failing coats) takes a reserved channel or a new page and touches that include, never a kind.

**History where the stories are.** P0, P1, H1 and the bent normal are the shared weathering bake on every chunk: true and quiet. H2 and H3 are allocated per chunk by the history budget per view: the change query's weight, summed over the judged views that see a chunk, ranks the chunks, and the highest get the story pages up to a cap. A chunk without them reads each of their layers as its material's quiet mean through `OS_History`. Adding a layer to a kind later is a registry entry and a rebake, never a rebuild. *Provisional:* the cap, at most a fifth of resident chunks and 0.2 GB, settled by the years sheet and cold readers.

**Keeping history honest.** A superposition validator (newer over older) and a two-date diff that fails any pixel outside the change list. Fine marks threshold fields with noise in the mark coordinate, fading to the mean by footprint. The brush anchors to UV2, since in world space it slides on what moves (*provisional*). One budget counts histories, acts and motion, by the change query's weight.

Reasons: decisions §5.

## Levels, chunks, instancing and the far field

**Five levels per kind,** each with its error in mm and its budget in the part and kind files. A level switches where its error is under about a pixel at 1440p. A pixel spans 0.48 mm per metre, so a level is safe beyond about 2,000 times its error. *Provisional:* the boundaries.

| Level | Judging band | What it is | Merge unit |
| --- | --- | --- | --- |
| L0 close | eye level, under about 8 m | full fitted geometry, maps at full texel | 4 m chunk |
| L1 near | street stop, to about 20 m | the generator's second level from the same seed and outline (a tread from 1,100 to 100 to 150 triangles) | 4 m chunk |
| L2 street | 12 m view, to 50 to 80 m | coarse pieces, relief in the maps' normal; the piece map is also the pick map | one mesh per 32 m cell, merged from runs of 3 to 5 m cached by hash |
| L3 shell | about 50 to 200 m | the thing's coarse mesh from its plan (a house 500 to 1,500 triangles, a flight a stepped ribbon), the shell atlas | 32 m cell, one mesh, one atlas page |
| L4 block | city camera, beyond about 200 m | about 100 triangles a house, the atlas's small mips | 128 m block |

The tiers in `docs/foundations.md` are judging bands, not switch distances. Trees keep their own levels to 200 m, then opaque lobes. Moving and lit things (lamps, boats, people, laundry) keep instanced levels, culled by screen size.

**Making levels.** Fitted parts make their own in the generator, so they exist in the player. Natural stone and land use meshoptimizer (MIT) with attribute weights and locked borders. Decimate (weighs no attributes) and Mesh LOD (editor-only, melts joints) serve only offline library parts that pass the A/B. *Provisional.*

**Units,** powers of two in metres, each with an id in the plan: 4 m draw-and-rebuild chunks at L0 and L1, cut at piece boundaries; 32 m cells at L2 and L3; 64 m land and streaming chunks (two cells); 128 m blocks (four cells). A change rebuilds the chunk, not the thing; at L2 it regenerates its run and re-merges the cell. GPU occlusion culls by bounding sphere, so a 33 m flight drawn whole is never culled. *Provisional:* the sizes.

**Precision.** Records and plans hold positions as integers in mm. Meshes are Float32 relative to their own unit's corner, so a 128 m block holds 0.02 mm. Units are placed from the plan relative to a world origin, rebased to the camera's 64 m chunk when the camera passes 2 km from it; within 2 km a float holds 0.25 mm. Shaders that read absolute position (wind, fields) get the origin as a split global; marks read UV2 and ids, so a rebase moves none. *Provisional:* the rebase's hitch. The scale test drew to 2 km in Unity's float coordinates (0.24 mm steps) without a rebase.

**Repetition.** Only what really was mass-produced repeats. Bricks, roof tiles, factory windows and doors, catalogue houses, and setts (hand-split but to standard sizes) come from libraries, each instance varied by placement, wear and history. Everything made by hand for one place is its own: a unique fitted piece, made in the player per chunk from its record and seed, costing build time and memory, never disk. One stair with its walls is 816,000 triangles and 36 MB at full detail today; the levels and the 4 m chunk keep unique pieces at full detail only near the camera. A repeat-finding check on golden views proves no library piece is found. Hand-split wall stones not made to standard sizes stay their own too, since the geometry fits its pool with levels: at test quality, L0 for every house in the 300 m streaming radius would be 600 MB, and L0 reaches only 20 m (the scale test). Only if House A's final-quality chunks break the pool does Øystein decide whether those stones may come from a large library where no repeat can be found.

**Hand-over.** A dithered cross-fade, never animated, since that breaks the Resident Drawer. Both sides share marks, seed and history address, and switch where values match. At L2 to L3 it fades per cell with hysteresis. *Provisional.*

**Instancing.** The Resident Drawer with the user value draws kit parts and street things; our own BatchRendererGroup draws swarms; no Entities. One 32-bit value indexes both the facts buffer and the pick table. Shaders use `#pragma target 4.5`, `DOTS_INSTANCING_ON`, `LOD_FADE_CROSSFADE` and `unity_RendererUserValue`. Burst, Collections and Mathematics are in `manifest.json`. *Provisional:* the Drawer can be slower when GPU-bound, and MSAA turns depth priming off.

**Shadows from proxies.** L0 and L1 never cast. L2 casts in the first cascades, L3 and L4 beyond. Small parts, tufts and litter never cast. Each chunk has a caster proxy. Trees cast from their opaque cores and lobes, never from leaf cards. People, boats, lamps, flags and laundry cast from a coarse level of their own in the first cascades only; a lamp's light casts by its tier. Today the cascades draw the town twice more (15 million triangles against 5.5).

**Rows by hash.** Slate courses and sett rows come from a per-row hash evaluated alike in C# and HLSL, so far levels draw the same slates without a bake.

**The painted far town.** Shells and blocks are built either way; unpainted, they are the district level from the same data. A look test decides only whether the atlas is painted (anisotropic Kuwahara on albedo and normal, one direction map) or plain. Reserved at 3.1: aligned cells; a per-thing atlas rectangle in the chunk format; per-triangle ids on shells; the shell's channels; `_OS_BAKE` in every shader (unlit albedo at the date, normal, history, ids), shared with the light's debug views; the cached bake; per-cell cross-fade. The shell level costs 18 to 20 days once, painted or plain, against 35 to 40 for far levels per kind (the study's estimate). Painting is about 3 of those days, so the test decides the look and those days only. *Provisional:* the test, 5 to 7 days (four arms, three lights, motion sheets, M4 timing, cold readers, six drop rules), timed by Øystein.

Reasons: decisions §6.

## Budgets

All provisional until each fix is A/B'd on the harness. The measurements are the harness's pass run (`docs/measuring.md`, The pass budget) and the scale test (`docs/research/scale-test.md`). The baseline: the blue hour 25 to 35 ms with 5.5 million triangles, 76 draws and no casters; drizzle 28 to 42; low sun 84 to 96; the birch 10 to 16; memory 1.4 GB by the system's footprint; the main thread about 1 ms, so the frame is GPU-bound. Scale adds no new failure to the frame: a 2 km district, with L0 to 200 m and shells beyond and the beams off, draws the street stop, 12 m and city camera in 21 to 25 ms in the blue hour and 27 to 31 in drizzle and low sun, the same per-pixel floor as the corner.

**Frame by pass** (GPU ms at 1440p; 14.0 used, 2.7 reserve). A pass over twice its budget at the harness's first run gets a fix before any triangle work.

| Pass | ms | Note |
| --- | --- | --- |
| Opaque geometry, L0 to L4 | 5.0 | the triangle budget below |
| Shadow cascades from proxies | 2.0 | |
| Sky, atmosphere, air | 1.5 | low sun's extra 55 to 65 ms is a bug, found first |
| Lights and spill | 1.0 | 8 to 16 shadowed spots |
| GTAO | 1.0 | indirect light only |
| SSR and water | 1.0 | URP's own SSR, temporal filtering off |
| Trees and alpha-tested layers | 1.0 | one birch costs 10 to 16 today: the first target |
| Post (grading, dither, focus stencil) | 0.8 | |
| MSAA 4× resolve | 0.5 | |
| Id readback, UI | 0.2 | |
| Reserve | 2.7 | holds people's share until the grey walker is measured |
| **Sum** | **16.7** | 14.0 in passes and 2.7 reserve |

**Triangles per judging view** (millions visible after culling; ceilings 2 million and 3,000 draws).

| Kind | Eye level | Street stop | 12 m | City camera |
| --- | --- | --- | --- | --- |
| Land | 0.25 | 0.3 | 0.35 | 0.35 |
| Ground cover and plants | 0.3 | 0.25 | 0.1 | 0.05 |
| Trees | 0.3 | 0.3 | 0.25 | 0.15 |
| Stone | 0.3 | 0.2 | 0.15 | 0.05 |
| Houses and fronts | 0.35 | 0.45 | 0.5 | 0.4 (shells and blocks 0.1 to 0.3) |
| People (20 near) | 0.3 | 0.3 | 0.2 | 0.1 |
| Water | 0.05 | 0.05 | 0.1 | 0.1 |
| Street things, decals, signs | 0.1 | 0.1 | 0.05 | 0.05 |

Each kind's export check: each level at most 60 % of the one before, and a median visible triangle of ten pixels or more.

At city scale the ceilings hold with levels. With L0 to 200 m and shells beyond, the district draws 3.9 to 9.1 million triangles a frame with every pass; the blue hour's 3.9 million are about 2 million drawn twice by the depth prepass. L0 for the whole core takes the city camera to 45.5 ms with 15 million. Draws are not the limit: 2,900 cost 1.1 to 1.4 ms of main thread without the Resident Drawer.

**Memory** (resident under 6 GB by the system's footprint, which counts the GPU's buffers in unified memory; Unity's own counter misses about nine tenths, so no budget is checked by it). The corner's player is 1.4 GB. With the scale test's district loaded (742 MB of meshes) it reached 2.6 GB, with no maps, people, library parts or textures for the district yet.

| Pool | GB | Pool | GB |
| --- | --- | --- | --- |
| Geometry in the streaming radius | 1.0 | Library parts, material arrays | 1.0 |
| Place and history maps | 0.8 | Chunk cache; a second date or record | 0.5 |
| Shell atlases, painted or plain | 1.0 | People | 0.5 |
| Fields, ground, height | 0.2 | Render targets, MSAA 4× | 0.3 |
| | | Engine, code, audio, UI | 0.7 |

Place and history maps hold the four base pages on every resident chunk and the story pages within their cap.

Geometry fits its pool with levels: at test quality, L0 for every house within the 300 m radius would be 600 MB, and L0 reaches only 20 m; a house is about 1 KB as a shell. Final-quality houses are heavier, so House A checks the pool again.

**Disk per kilometre** (both sides, about 250 houses, about 14,000 m² of surface): place and history pages 13 to 51 MB at 8 to 4 cm (four base pages at a byte a texel, story pages on a fifth of chunks, mips included), plus about 4 MB a flight of walked stone at 2 cm; instance records about 30 MB; shell atlases 115 MB at 5 cm or 320 MB at 3 cm; chunks 20 to 40 MB. So 0.2 to 0.45 GB, painted or plain. The disk cache stores every page compressed, so a revisit skips the bake; the shipped heart cache carries them all, and elsewhere pages bake on the GPU at first build. The 1989 centre's shipped cache is about 1 GB.

**Build time** (C# worker time): a 4 m chunk 10 to 50 ms; a house under 20 ms at test quality; a kilometre of street 1 to 5 s; a thirty-year jump across a district under 1 s, the first view's 20 to 50 things built behind the dated card. A house at final quality is unknown until House A.
- Every loop over parts or vertices in play is a Burst job. Placing a chunk's parts costs 0.68 ms per 100,000 triangles in Burst, against 9.1 ms in plain C# under Mono, which the player runs (IL2CPP is not installed). So a final-quality stair's 4 m (100,000 triangles) is placed in about 0.7 ms, and uploading 265,000 triangles through `MeshData` takes 1.6 ms.
- The bake is the dear stage: 0.6 to 0.9 s a house in Blender's Python, ten times the build. It is the first stage timed when it moves to the player.
- Offline, Blender's Python on 8 processes builds 68 km² of test-quality town an hour.

**Streaming a frame:** at most 1.5 ms of main thread for swaps and renderer changes (90 ms a second); at most 8 MB uploaded (meshes and pages), so a larger upload is split across frames; at most 64 renderers added or removed under the Resident Drawer, which holds one per 4 m chunk and level, about 10,000 resident (*provisional*); page compression on the GPU, at most one page a frame, from the reserve. Past a limit the coarser level stays a frame longer; nothing hitches.
- Files are read on worker threads (`AsyncReadManager` into native arrays). The main thread keeps only `ApplyAndDisposeWritableMeshData` and renderer changes.
- The reason: read and uploaded on the main thread, a file costs 0.28 ms plus 0.63 ms a MB. A core chunk of 64 m (8.8 MB) takes 5.6 ms, and the city camera's 300 m/s pan asks for 84 ms a second, 93 % of the line. Walking asks for 1.7 ms a second and driving 17.
- A jump's first view (88 near chunks, 148 cells, 88 streaming chunks, 484 blocks) is about 0.4 s of main thread, behind the dated card.

**The authoring loop.** A look change on one kind is seen in under 3 minutes (one chunk regenerated, imported, one golden view compared). The gully's full sheet takes under 10 minutes. A loop over budget is fixed before the port goes on.

Reasons: decisions §7.

## Light, time and world state

- **Nothing relies on temporal accumulation,** so marks stay stable and golden views repeat. MSAA 4× at native 1440p, FSR 1 as fallback, STP only once every mover writes motion vectors (*provisional*).
- **One world state,** owned once and hashed: fabric date (year, month), day of year, the hour as the sun's position, weather, wind (climate and moving, one fetch), tide, latitude, longitude, time zone. The light's layers replay from it.
- **The shade's three lookups** (sky radiance from a model, the seen ground, the seen town) sit in `OS_ShadeP`, since the light's four debts share one cause. *Provisional.*
- **Lights come from sockets in tiers,** since the heart has 403 against Forward+'s 256 a camera: 8 to 16 shadowed spots near, unshadowed at street, glow beyond (*provisional*). No shop or window is a real light; spill comes from a tile-binned buffer. One socket serves lamps and windows.
- **No baked probes,** since they cannot follow a rebuilt town. The generator places reflection probes, a few relit a frame. Far shadows and horizon angles come from the height map.
- **Occlusion on indirect light only:** GTAO, multi-bounce with albedo, specular occlusion; none on the sun.
- **No runtime painterly filter and no boil on what stands.** The style is in the colour lookup; dither at the last write; lamps by spectrum; normalised specular; exposure from illuminance; HDR buffers with no lifted blacks, which break dark skin first (Rule 8). A chart and debug views of the shade's terms share `_OS_BAKE`.

**Time.**
- Lives are written on change in C# in the player; the past to 1989 may ship as a cache.
- A part exists from making to removal. The cache key holds the record and life hashes, so a second date, or a counterfactual twin's record, is a second key resident for the frustum only (*provisional:* memory). Two-date frames draw both keys under one camera and light through a movable mask in the post pass, one change at a time in date order.
- `changes(scope, t0, t1)` returns cause, actor, provenance, precision, weight, parts, region per view and drift. It feeds budgets, highlights, the why-probe, the journal, the readers' key and the shell rebake.
- The drawing is a hashed function of record, fabric date, light moment, weather, view and level.
- Scene state is instance overrides on their own clock, never in maps or the record, committed to the engine only when it matters.
- Works keep dated phases (hoarding, pit, scaffold) as fills of a works slot.
- Condition never depends on whether anyone watched. The actor on every event keeps the player's mark possible.

Reasons: decisions §8.

## Materials, plants, land and motion

**Materials.**
- Causes split by shape. Records and outlines (signs, posters, a removed shopfront's line, rust below a fixing) are dated mesh decals from one atlas per family, drawn by the host's stack and baked into the shell far off; decals stack and pick. Water-borne stains are carriers in the water bake, running down the flow path across parts and fading from the removal year (*provisional*). URP's Decal Projector is only for transient scene state.
- One material record per material in `packs/<pack>/materials/`: identity, pigment, grain script and seed, tooling, water profile, wear, growth affinity, paint failure, city bake, albedo range, porosity, smoothness, translucency, scatter, a curve per process, texel targets, an acoustic class (reserved). Families sit in a `Texture2DArray`. An editor step writes the Unity asset from the record.
- Coats are fills with their year, read against the date, up to eight a wall in a data texture by wall id.
- A board-and-trim atlas, 4 by 1 m at 1 mm; boards stay geometry at L0 and L1 for the low sun (*provisional*). Hex-tiling for concrete, asphalt and ground (*provisional*).

**Plants.** Opaque first: no cards or shells near, cards only where few overlap, cut to outline. One placer, one presence law: present when potential(fields, facts, date) > rank(seed). The gully exports joint lines, growth faces, traps, climbable regions and keep-clear zones. Plants are records with keepers' calendars. Wind-ready marks: bark from UV5's rest position, a motion-vector pass. Growth stays offline; a change beside a tree applies as events (*provisional*). A deposit field per chunk.

**Land and water.** Natural ground is layers. Made ground is dated acts applied in date order, run in the player, since a game may build a road. Terrain is mesh in 64 m chunks with breaklines and rings that coarsen by distance, since a flat 2 m grid everywhere is 2.1 million triangles and 37 MB a km², the largest cache item after L0 (the scale test). Foot lines are breaklines and footprints. Natural stone is its own kind. The ground shades through `OS_ShadeP` with few materials drawn from fields; slow edges are mesh, fast ones shader (*provisional*). Water is opaque meshes with baked depth and Gerstner waves from wind and fetch. It reflects through URP 17.6's own Screen Space Reflection renderer feature (on in `PC_Renderer`, behind the `URP_SCREEN_SPACE_REFLECTION` define), with temporal filtering off; planar reflection only if that fails (*provisional:* the harness and a motion sheet).

**Motion and affordances.**
- One motion class per element: still, hinged, swinging, flexible, floating, emitting. The anchor class is derived; a flag says card or skinned.
- People's identity numbers are in the contract; their far mesh and archetypes are *provisional*. The gait seed is in identity from birth. Faces keep both routes open, with blend shapes kept on import.
- Affordances are dated sockets read at the date: treads, walking line, landings, handrails, sit, lean, stand, sills, shelter, grips. Every walked surface registers a walking line to the feet field.
- Flags, laundry, smoke and splashes step on twos from a shared clock; people and the camera stay smooth (`docs/research/what-moves.md`). *Provisional:* a motion sheet.
- Wind is one field, a pure function of position and absolute time. Every motion is a function of the record and absolute time; cloth is the one warm-started exception.
- Clips and rules are engine-neutral data.

**Collision and navigation.** Each part level declares a `collision_role` (none, proxy, full). The chunk carries one merged proxy at L1 detail. A tread's hollow is below a walker's foot tolerance, so the collider reads the date only when the chunk rebuilds. Walkable surfaces come from affordances and the ground chunk. A navigation mesh is built at runtime per 64 m cell and rebuilt with the chunk. *Provisional.*

Reasons: decisions §9.

## Buildings, fronts, signs and the interface

**Buildings.**
- The window is a slot: the opening never deleted, its fills a list, the surround its own fill, then the dressing stack and the room by reference.
- Wall surfaces are dated by region: profile, year, scope, corner type.
- A room is a record (box in mm, kind, household, year fitted, lamps). Its box is instance data; its lit state is live by the hour, never baked. It can grow into geometry.
- A sign is a record with its own events; street records are a coat stack. The ground floor has its own grammar under a control layer.
- Nothing is rolled that the record lacks: the seeded mansard is gone, since it claimed a roof raise. Era values live in `packs/<pack>/eras.json`; the `stronger` multipliers are gone.
- Glass by era with one normal per pane; one opaque window shader reads the room box. Lit rooms follow the household's day by rules, `derived` until the engine provides it (its #22).
- Roof courses are geometry, odd tiles by index, with a permissive straight skeleton for irregular hips.

**The interface.**
- Picking: chunks through UV3's piece index and the chunk's table; kit instances through the user value; swarms through tile and seed; shells per triangle; people by their own path (*provisional*).
- Ids come from a scissored 64×64 id render round the cursor, read back two or three frames late.
- One highlight function compares the hover and selected global ids: an even lift, no hue, no neighbour sampling. The focus is a stencil in the post pass.
- Each record has a label anchor and a screen bound; people have a head anchor; a CPU list serves the bubble snap.
- The knowledge store is data per role: seen, heard, told, written, inferred, the record, unknown. Built with the first game.
- A name is a fact and may be shown. A reading of character is never labelled.

Reasons: decisions §9.

## Quality tools and checks

| Tool | What it does |
| --- | --- |
| Baselines | a strict review accepts one while building; Øystein accepts milestone sheets |
| The harness | A/B switches (Resident Drawer, GPU occlusion, MSAA, history path, forced levels, sun beams, shadow reach); peak memory |
| Golden views, motion sheets | one sample a pixel; the swim test and shimmer index |
| Export checks | budget per level, the 60 % rule, median triangle, fits never silent, the kit validator, plan validity, licences, the id test |
| Fact checks | one framework: `trace_check`, act, cut and label checks, superposition, diff across dates, watched-or-jumped, time-jump |
| Expressive range | counts per level, the repeat-finding check |
| Test matrix | kinds × levels × lights × views × dates × machines in `tools/matrix.json`; a subset on the daily build |
| Build pipeline | `tools/build_player.sh` builds pack, libraries, cache and code into a macOS player and fails on the checks; a daily build on the Mac mini. `tools/perf.sh` stands until a C# core exists |
| Licences | only permissive code ships, listed in `LICENSES-shipped.md` and checked at build; `bpypolyskel` (GPL) offline only; meshoptimizer (MIT) and an Apache-2.0 skeleton ship |

Research gaps are studied just before their steps.

Reasons: decisions §10.

## A new city's pack

A pack (`packs/<city-year>/`) brings: `metrics.json` (storeys, openings, rises, kerbs, thicknesses, grid, by era); `eras.json` (Overstory's own pack data, offered to the engine through `docs/engine-requests.md`, never written into Understory); `materials/`; part families with their era content; `geology.json` and `climate.json` (rock, ice vector, foliation, joints, tide, fetch, splash, wind, latitude, longitude); `lamps.json`; `lettering/`; the record catalogue; the field guide; population and dress tables; `names.json`, every placeholder name; `tooling.json`; the curated start record and its pins.

Everything else carries over: schemas, kinds, stages, shaders, the shared systems, checks, the chunk format and the interface. A foreign-pack part is a data check only until step 10.

**Scale.** The world on disk is the record plus the libraries. Chunks are binary, keyed by the hash chain, evicted least-recently-used by distance under the byte caps. People are generated at runtime from identity numbers, cached by a hash of record, age step and outfit. The heart's start-date cache ships, and near levels elsewhere build on demand from the record, with the same code for both. Shipping near levels does not scale: at test quality L0 is 708 KB a house, 2.1 GB a km² of town like the core, 2,300 times the house's record of 315 bytes, so a metropolis would need hundreds of gigabytes. Building keeps up: walking asks for about 4 near chunks of 4 m a second and driving 40, and placing costs 0.68 ms of Burst per 100,000 triangles.

Reasons: decisions §11.

## The three example games

**A manager (a club or a band).** A new stand is fitted geometry made in the player. Crowds are far figures with their own identity numbers on shared meshes. Posters are decal records on a coat stack. A room can grow into a clubhouse; a stadium is a new kind file. What keeps it open: kinds and metrics as data, one record for every kind, the assembler in the player.

**An exploration game.** Levels switch by error in pixels anywhere, so eye level holds in any lane. Small chunks and a shipped cache cover walking pace. Collision and navigation are reserved per part level. Journal entries point at slot and fill ids that survive rebuilds. What the history budget hides stays findable through the card and the probe.

**A family across generations.** Extensions and rebuilds are fitted geometry in the player. Thirty years of drift costs a uniform; discrete changes are chunk rebuilds behind the dated card. Ground acts run in the player. A planted tree grows from a timeline or events. Seeds and ids hold for a part's life; people come from identity numbers with parents in the record. Eras after 1989 are content, and nothing assumes a final year.

Reasons: decisions §12.

## What this changes in existing work

- **Stone.** Facts move from `FLIGHTS` and `stair_facts.py` into a fixture; `YEAR` is no longer hard-coded. Seeds move to SplitMix64. The monolith splits into the seven stages under `kinds/stair.json` and `kinds/wall.json`. Its six UV channels become the map pages and the vertex layout. Levels, chunks, a shell ribbon and caster proxies follow. The five open faults wait for the new foundations. Findings, style and facts are kept, proven by the golden views.
- **Birches.** Cut cards, opaque cores, real leaves near, wind-ready marks, levels to 200 m, then lobes. The timeline cache is keyed into the hash chain. `h01` and the simulator's `random.Random` move to the one hash, so the timelines change once, with a new baseline.
- **Houses.** The record migrates to slots and fills; the mansard goes; `eras.py` becomes pack data. The house builder is ported to C# before House A, which the generator builds with pins, then twelve more from the same parts. The window and its surround are the first final part.
- **Kit props** (lamp, bollard) become library families with definitions, levels and sockets; the unused seed goes.
- **Unity.** `StreetGround.cs`'s kerbs and flags become a kind. Placement in `LT1Stone`, `LT1Trees` and `LT1Heart` becomes the assembler reading records, and their material values come from pack records. `TownLights.cs` reads sockets; its spot per shop goes. Shaders gain `_OS_BAKE`, the highlight compare, `OS_History` and the Drawer's pragmas.

**Statements superseded,** each file to be updated:

| File | Statement |
| --- | --- |
| `docs/living-fabric.md` | "Life is computed offline per thing"; "the city tier bakes the life into the merged mesh's vertex data"; fields "redrawn by decade" |
| `docs/town-system.md` | "Only the chunk a change touches is rebuilt offline" |
| `docs/research/kits-and-generation.md` §6 | Unity "runs no generation" |
| `docs/building-system.md` | "The shader reads one number per coat: years since it was applied" |
| `docs/foundations.md` | the tier table's switch distances; merged "runs of parts (a flight, a wall, a house)" as the merge unit |
| `docs/visual-direction.md` | the brush's one world size |
| `docs/research/stone.md` | "Every piece its own seeded instance, so nothing repeats", which becomes: setts and other mass-produced pieces from libraries, everything hand-made for one place its own |
| `CLAUDE.md` | Practical: "Large binary files (renders, FBX) go through Git LFS", which becomes "generated binaries are rebuilt, not tracked; baselines in plain git until LFS is reachable"; Standing rules: the generator "does not invent their geometry", which becomes "a fixed part is a judged mesh; a fitted part is a judged function; the generator places only judged parts and never invents one"; the Docs table gains this file |
| `blender-generators` skill | parts as `.blend` through LFS; `random.Random(seed)`; the 1 m grid; `kit_<family>_<variant>_<lod>`; "wear, dirt and age set by Unity, not baked"; `blender/validate.py`; export to `Assets/Art/Kit/`; 2,000 triangles for LOD0 |
| `unity-conventions` skill | `PlaceGrammar.cs`, `Code/Characters/`; "GPU instancing, static batching"; "one shared hash" (true again after 3.0); "Unity never decides" (Unity assembles and fits, and still never invents a fact) |
| `docs/measuring.md` | "only Øystein accepts a baseline" |
| `docs/plan.md` | `blender/kinds/` |
| `docs/engine-contract.md`, `docs/notes/` | `engine` as a provenance value |

Reasons: decisions §10.

## Open until measured

| Item | Default built on | Settled by | When |
| --- | --- | --- | --- |
| Vertex byte widths | the layout table | the gully's A/B | 3.2 |
| Tangent frame | derived from UV derivatives | the gully's A/B at L2 and on shells | 3.2 |
| Pick index split | 2, 14 and 16 bits | the picking spike | during the port |
| Per-instance data; picking and readback | user value plus a facts buffer per cell; id render round the cursor | the picking spike, tested against raycasts on full meshes | during the port |
| History carrier | maps at every level | the gully's A/B in grey light at eye level, FLIP within threshold | 3.2 |
| Map density and unit | 2, 4, 8 cm; the draw chunk | the scale test with synthetic maps at both densities; BC7 in a smooth field | 3.2; unit 3.4 |
| Map rebake cost | 2 ms GPU a 1024×512 page with its compression, on the GPU | the bake's own shader and a GPU encoder (BC7, BC5, BC4), timed on the M4 | before pages bake in the player |
| Mixed texels in a chunk | each part's rectangle at its own texel | packing waste measured on the gully's pages (the scale test assumed 15 %) | 3.2 |
| Story pages | a fifth of resident chunks, 0.2 GB | the years sheet, cold readers | step 4 |
| The brush | anchored to UV2 | a motion sheet | after the port |
| Level boundaries, hand-over | error under a pixel; dithered cross-fade | motion sheets at one sample a pixel | 3.4 |
| Levels for library parts | generator levels, meshoptimizer | the Mesh LOD test on the gully's FBX | 3.4 |
| Unit sizes | 4, 32, 64, 128 m | the scale test: rebuild per chunk, demand rate, cache per km | 3.4 |
| Resident Drawer | on | the harness A/B | 3.4 |
| Painted far town | shells built, atlas plain | the look test | Øystein's call |
| Frame by pass, disk, build time in C# | the tables above | each pass's fix A/B'd on the harness; the C# core timed | the port |
| Anti-aliasing | MSAA 4× native, FSR 1 fallback | the harness, motion sheets | 3.4 |
| The shade's lookups | in `OS_ShadeP` | look test | 1c |
| Light counts | 8 to 16 shadowed spots | the harness | steps 3 and 6 |
| Memory for a second date or record | 0.5 GB | a second date resident in the district player, by footprint | step 4 |
| Water-borne carriers | in the water bake | the gully's handrail post | after the corner's wash |
| Board atlas; hex-tiling | as stated | look tests | House A; step 3 |
| Ground edges | slow as mesh, fast as shader | the corner's years sheet | 1d |
| Birch cost; regrowth in play | opaque first; growth offline | the harness; a measurement | now; step 7 |
| People's far mesh, archetypes | identity numbers in the contract | the recognition test, crowds of 500 and 2,000 | step 5 |
| Collision and navigation | proxy per chunk, navmesh per 64 m cell | a short craft study | before the grey walker |
| Streaming a frame | 1.5 ms main thread, 8 MB, 64 renderers; reads on workers | the renderer count under the Drawer; a cold read (the scale test's 960 MB/s was a warm cache) | 3.4 |
| Origin rebase | at 2 km, to the camera's 64 m chunk | a camera driven past 2 km in the district player | before a town passes 2 km |
| Flags and laundry | stepped on twos | a motion sheet | before the wind |
| Water reflection | URP's SSR, no temporal filtering | the harness, a motion sheet | step 6 |
| A house at final quality; the geometry pool | unknown; the pool fits at test quality | House A | House A |
| Scripting backend | Mono, every hot loop in Burst | IL2CPP against Mono on the C# core's main thread | the week after the port |
| Pins across a rules change | on slot and fill ids | the first `rulesetVersion` bump | the first bump |
