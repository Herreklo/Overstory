# The building blocks

How every material, kind of thing and system is built, for the first town, a bigger city and the three example games. Reasons are in `docs/research/building-blocks-decisions.md`, by section. The order of work is in `docs/plan.md`, whose step names (1c, House A) are used here. The names 3.0 to 3.4 are the gully port's steps under their old names: 3.0 is the port's step 0b (seeds), 3.1 its steps 1 and 2 (schemas and stages), 3.2 its step 3 (history), 3.3 its step 4 (materials) and 3.4 its step 5 (levels) (`docs/research/building-blocks-decisions.md` §13).

The stack: Blender 4.x Python offline; Unity 6000.6, URP 17.6, C# with Burst. The reference machine is the base M4 Mac mini, 16 GB unified memory, 60 fps at 1440p, so 16.7 ms a frame.

*Provisional* marks what a named measurement settles; Open until measured lists each with the default built on meanwhile. Everything else is firm.

## In short

- **BB1** Blender makes parts; C# in the player assembles the town (Øystein accepted); a kind's Python freezes, deleted after C# parity and one strict review. Evidence: decisions §1. Reopens: none named.
- **D1.6, D14.2** Schemas parity-tested per stage before meshes; generated binaries untracked; git history not rewritten. Evidence: decisions §2, §14. Reopens: LT1's merge (Øystein).
- **D5.1** History is a function of record and date; only shells cache a bake. Evidence: decisions §5. Reopens: none named.
- **S2** Every pass has a line before geometry moves: M4, 1440p, 16.7 ms, 2.0 reserve, opaque 5.0 (history 0.5); 2 million triangles; 6 GB. Evidence: `measuring.md`. Reopens: each fix's harness A/B.
- **S1** (disputed) No temporal accumulation or alpha-to-coverage; SMAA at native with depth priming; STP once every mover writes motion vectors. MSAA 4× until port step 5 (3.4) keeps step 3's A/B clean; then shimmer and golden views choose, on levelled geometry. Evidence: Light. Reopens: step 5.
- **D6.4** (disputed) Only the mass-produced repeats; hand-split wall stones stay unique. Evidence: `research/scale-test.md`. Reopens: House A's final chunks breaking the pool (Øystein decides).
- **BB2** Painted far town test: after the gully port, before House A's far level. Evidence: decisions §14. Reopens: Øystein.
- **BB3** A stone is rigid. A rigid piece (stone, slab, brick, a timber that does not flex) is placed only by moving and turning it, never bent, sheared or stretched. It fits by choosing the piece or by a judged cut. A course through a change of pitch steps or tapers as a mason lays it. Only parts that really flex (plants, cloth, people) deform, from their rest position (UV5). The export's rigidity check enforces it. Evidence: Øystein, 22 October ("you can not bend rocks"). The gully's cheek walls shear their face stones and copings along the rake, and bend the hearting stones through each change of pitch. Reopens: none.

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

**One source of truth per stage and kind** (BB1), since two live sources drift. Python (`resolve.py`, `upkeep.py`, `blender/parts/*.py`) is the source until a kind's port. Then it is frozen as the parity reference, and deleted once the C# passes parity on the golden fixtures and one strict review. Look sheets then run the C# through Unity in batch mode. Plan and life flip the week after the gully port; the house resolver before House A; geometry per family, stone first.

Reasons: decisions §0, §1.

## Contracts and where files live

**Schemas** (D1.6) are hand-written JSON Schema (draft 2020-12). Python validates with `jsonschema` (MIT). C# types are hand-written twins, held to the schemas by parity tests over `fixtures/golden/<kind>/<stage>.json`.

| File in `schemas/` | Describes |
| --- | --- |
| `record.schema.json` | any record: id, kind, provenance, precision, lifespan, events, links, keeper and care, pins |
| `kind.schema.json` | a kind: stage parameters, slots, families, levels and budgets (with each shader family's shading over flat, in ms at the street stop), motion, affordances, fields read and written |
| `part.schema.json` | a family: `made_as`, era, sizes, fit modes, pivot, sockets, removal mark, variants, error and budget per level, shadow, collision and motion roles, intrinsic channels, each procedural mark's smallest feature (which, with the face class, sets its texel), shader family, lifecycle |
| `plan.schema.json` | an instance: part path, variant, seed, placement in mm, fit, placing event, chunk id |
| `slot.schema.json`, `interval.schema.json` | slots and fills, a surface region carrying its face class; life intervals (from, to, reset year, rate, age offset, an optional reach, cause) |
| `channels.json`, `maps.json`, `layers.json` | the vertex and texel channels with byte widths; the map and layer registries |
| `chunk-format.md`, `chunk.schema.json` | the binary file as a container (a header with the ruleset version, and an index of units by id, level, hash key, offset and length) and each unit as a versioned byte table, one reader per language tested on one golden file |
| `world-state.schema.json`, `change-query.schema.json` | the world state; `changes(scope, t0, t1)` |
| `naming.md` | one page of naming grammar for ids, part paths, kinds, materials, chunks, page groups, blocks, maps and fields, written before the first kind file |
| `CHANGELOG.md` | every schema change with its migration |

**Folders.** `schemas/`. `kinds/<kind>.json` at the repo root (stair, wall, house, birch, lamp, bollard, natural-stone, ground-act), because both languages and the player read it. `packs/<city-year>/`. `blender/parts/<family>/` for part code, with C# twins later in `unity/Assets/Code/Parts/`. `fixtures/` for records, golden fixtures and the engine run. `migrations/`. `cache/`, untracked, for chunks, tree timelines and exported library meshes. `tools/` for checks and builds.

**Versioning.** Every record file carries `schemaVersion`. `tools/migrate.py` runs `migrations/NNN_<name>.py` on every fixture, and a check fails if any is behind. C# reads only the current version. The curated 1989 town and its pins migrate by the same scripts, so a rule change never kills it.

**The hash chain** (`tools/hashes.py`, later `Hashes.cs`): `schemaVersion`, `rulesetVersion` (kind file and part function versions) and `worldSeed`, then the record, plan, life and mesh hashes, then `bakeVersion` (the `OS_History` include, the layer curves, the bake and shell-bake code, the shaders) and the bake hash. Each is a cache key, and a stage with unchanged inputs is skipped.

**Generated files are rebuilt, not tracked** (D14.2). FBX, chunks, library meshes and tree timelines leave git; hash manifests and part sources stay. Golden baselines keep one current baseline per kind, view and light in git, at the size judged; a superseded one leaves the tree and stays as its hash in the manifest. Plain git until LFS is reachable. The tree drops its 385 MB of FBX at 3.1. History is not rewritten now; it is revisited at LT1's merge (Øystein, 21 October).

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

**History is a function of the record and the date** (D5.1). Pages store inputs: one drive per texel per layer, and the layer's form says what it scales. Polish and moss take an amplitude times their material's curve; lichen takes a rate into it. Each layer runs from one of its piece's clocks, chosen per texel by a reach. The thing's speed (its footfall) and its care are per thing, and the date is a shader global (`_OS_Date`, a float, never half). So a jump costs a uniform, and a watched town draws as a jumped one. On the gully the law is exact in float at 1989 and at every earlier build, and within 0.5/255 in 8 bits (`reviews/lt1/history/fit.md`).
- **The law** (`layers.json`), with t the date in years. The constants are slate's until the material records hold them (step 4):
  - polish = max(H1.R × (1 − e^(−k·min(t − placed, 40))), the piece's inherited polish), k the thing's footfall / 400,000 a year;
  - lichen = clip(H1.G × max(t − c − 12, 0) / 200), c the bare year, or the disturbed year within the hands' reach (face kind and edge distance) of a piece lifted by hands;
  - moss = clip(H1.B × 2.04 × (1.15 − 0.75·care), 0, 1) × (1 − 0.85·clip(trod × P0.R)) × min((t − c) / 60, 1), c the bare year, or the later of bare and disturbed where H1.A says the bed reaches. The clip comes before the trodden thinning. Care is the thing's in year t − 1, and trod is the thing's;
  - a cleaning restarts lichen and moss: neither runs from before the cleaned year;
  - the hollow is derived, not stored. Its depth on a walked tread is the thing's wear rate × H1.R × (t − placed); the water it holds, clip((depth − 3 mm) / 3 mm), and the tread's water, max(P0.G, min(depth / 4 mm, 1)), follow from it. The dish tied to polish is a slate rule: a material that dishes without polishing takes UV4.y or a channel of its own.
- **Clocks per piece, drives per texel.** The chunk's piece table holds each piece's four resets (placed, disturbed, cleaned, reserved), as year × 16 + month from the pack's first year, and the age it brought in whole years: bare is placed less that age. Lifted by hands is a flag. No texel holds an offset. An entry is 32 bytes on disk and 16 on the GPU, read in the vertex stage by UV3's piece index (`schemas/chunk-format.md`).
- **Care is a uniform.** A change of care costs a uniform, never a rebake, so a keeper's decline falls out of the function. H1 rebakes only for geometry, a rate or a reach.
- **Baked as laid.** H1 and the fields that make it are baked on each piece as laid, in its own frame, not on the settled stone: the page holds between events, and polish and lichen stay on a sinking stone. P0 is the place's, at the settled position, and is rebuilt on geometry; a front's foot band is a place effect there, where the target frame wants it. This lands at step 2b, since it changes the FBX, and is judged against the target frame.
- Maps serve every level, from the atlas UV. Per vertex sit only piece constants and what moves geometry (a hollow's rate), so no hand-over between carriers must match. *Provisional.*
- Pages are kept per 16 m page group of 4 m chunks, addressed by UV1 and rebaked by region; the mesh still draws and rebuilds by the 4 m chunk. Pages are resident only within the reach of the levels that read them (L0 to L2, about 80 m), and stream whole, not by mip; shells read their atlas.
- A surface's texel is the coarser of its marks' smallest feature and its face class. The plan sets the face class by one function, and the record check validates it:
  - *street*, a face to a walked street, lane, square or quay, takes its material's texel on every floor: 2 cm walked stone, 4 cm walls and trims;
  - *yard*, a face to a yard, a garden or another building, takes its material's texel to 2 m above the ground it meets, where splash, damp and contact sit, and 8 cm above;
  - *roof* 8 cm, since roofs carry neglect in the raised views; the ground 8 cm.
- Pages hold drives, which vary slowly, and no grain: the fine marks come from noise in UV2. **Charts** are cut per run of one face kind (a wall's face, a flight unrolled along its walking line), joints inside, on a 16-texel grid with 2 texels of padding and three mips, sampled trilinear without anisotropy, so a BC block at mip 2 stays inside its chart. A group that mixes texels packs each rectangle at its own texel into one set of pages. Per run, packing and padding waste about 10 to 15 % (*provisional:* measured at step 3's R3).
- **Formats.** Pages are RGBA8 until a real page's BC7 error is measured, at the end of step 3's R3: per channel, mips 0 to 2, the 99th percentile at most 2/255 (H1.B about 1/255, since moss doubles its error). A pair that fails goes to a BC5 page and costs a sample.
- **What a family reads.** A shader family reads only its own pages (`layers.json`'s readers): the stone reads P0 and H1. A sample is budgeted at 0.17 ms a 1440p screen, inside history's 0.5 ms at overdraw 1 (Budgets); story pages count against the history budget per view too. Minified, a sample measured about 0.02 ms. What costs is how busy the output is, paid in the passes after the draw (`reviews/lt1/history/r2.md`), so history's line is measured on the real stone, never on a quad.
- **One baker.** One bake function serves the editor and the player, held to golden page hashes. Step 3 bakes the gully's pages offline in Blender: a named exception to baking in the player, which ends at step 5.
- The reason: a house's envelope (walls and roof) is 444 m², not its 56 m² street front. With every face at 4 cm, a house is 1.7 MB of pages and the 850 houses in the 300 m radius 1.45 GB, against a 0.8 GB pool. By face class a house is about 0.75 MB, and the houses within 80 m about 50 MB.
- A rate change (a gutter, a fallen neighbour) rebakes the map region on the GPU, not the unchanged mesh. The chunk's invalidation table says per act which pages, instances and whether the mesh it dirties. Rebakes run behind the dated card, 2 ms GPU per 1024×512 page with its compression. Drawing a page takes 0.7 ms and reading it back 0.7 ms (a blit standing in for the bake's shader, so a floor). Compressing it on the CPU takes 5.3 to 8.7 ms (DXT5, since Unity's CPU path offers no BC7): three to six frames' streaming budget. So pages are compressed on the GPU, by an encoder the project does not have yet (*provisional:* the bake's own shader and that encoder, timed on the M4).
- Intrinsic channels (face kind, edge distance, own occlusion) are in the mesh. Extrinsic ones are per instance, field tile or map, so a library sett carries its own lane's years: reset years in the chunk's piece table (by UV3's piece index) or the facts buffer, care in the facts buffer, feet and static water in P0. Damp is the shade's, from water and the weather.
- The light's inputs (sky seen, ground seen, openness, weather exposure) live in the place pages P0 and P1, with a two-channel bent normal at L0 to L2. Shells drop the bent normal; impostors have their own atlas.
- Every shell gets its atlas (albedo and normal at the date, the light's inputs, the index), painted or plain, baked on demand on the player's GPU within L3's reach. Until it lands, a shell draws plain from its material class and reset year: the layers' quiet mean. A block (L4) reads the atlas's small mips where one is cached and draws plain elsewhere. City-wide, no atlas ships: at 444 m² a house and 5 cm, atlases are about 340 MB a km of street, and a block's mips would need 10 cm at 200 m. The atlas is the one exception to inputs-only maps: the shell caches an output bake of pigment with slow history, invalidated per thing by the change query; drift stays live from the index's reset year. A cached evaluation is still the function. Format reserved at 3.1; the bake comes with the gully's shell.

**The map registry** (`maps.json`) names each map's channels, owner, unit, texel, format and GPU encoder, readers and rebuild trigger. *Fields* are coarse and owned by the land. *Place maps* are fine and owned by the chunk, sampled from the fields and the chunk's geometry.

| Map | Channels | Owner, unit | Texel | Format | Read by | Rebuilt when |
| --- | --- | --- | --- | --- | --- | --- |
| Height and sky | height; sky seen, horizon angle | land, 64 m | 0.5 m heart, 2 m beyond | R16 + RG8 | far shadows, horizon, light | a ground act |
| Ground | R soil, G seasonal albedo (an index into the material's range), B wet, A reserved | land, 64 m | 0.25 to 0.5 m | RGBA8 | feet of rock, walls, plinths; blade roots; seen ground | a ground act, the season |
| Fields | a slice each: soil, flow, wetness, wind and salt, sun dose, made ground, feet | land, 64 m | 0.5 to 1 m heart, 2 to 4 m beyond | `Texture2DArray`, R8 or R16 | place-map bakes, placer, deposits | an act, the feet plan, the decade |
| Place P0 | R feet (the walking line's share), G static water, B sky seen, A ground seen | 16 m page group | by face class: 2, 4, 8 cm | RGBA8 → BC7 | the families that list it, via `OS_History` | geometry, a neighbour's rain shadow |
| Place P1 | R openness, G weather exposure, B and A reserved | 16 m page group | same | RGBA8 → BC7 | same | geometry, a neighbour |
| History H1 | R polish amplitude, G lichen rate, B moss's damp (unclipped, over 2.04), A bed reach | 16 m page group | same | RGBA8 → BC7 | same | geometry, a rate change, a reach |
| History H2, story groups | R wash, G deposit, B splash, A contact | 16 m page group | same | RGBA8 → BC7 | same | the history budget; a rate change |
| History H3, story groups, reserved | R carrier (from the water bake), G soot, B salt, A reserved | 16 m page group | same | RGBA8 → BC7 | same | when the layer lands |
| Bent normal | RG direction | 16 m page group | same | RG8 → BC5 | the shade | geometry |
| Deposits | leaves and litter | 16 m page group | 8 cm | R8 → BC4 | ground, plants | the day's wind, feet, keepers |
| Shell atlas | albedo at the date; normal; sky seen, ground seen, openness, weather exposure; index (R thing in the cell, G reset year from the pack's first year) | 32 m cell | 3 to 5 cm | BC3, BC5, BC3, R8G8 uncompressed | shells, blocks | the change query names the thing |
| Impostor atlas | the impostor baker's | species, library | fixed | BC7 | far trees | the species' timeline |

**The layer registry** (`layers.json`) names each layer's page and channel, inputs, curve owner (the material record), reset rule and, once fitted, its law; the layers derived from others (the hollow); and the pages each shader family reads. Every shader reads layers through one `OS_History(address, layer)` in one include. A new layer (soot, salt, rust runs, carried stains, splash bands, failing coats) takes a reserved channel or a new page and touches that include, never a kind.

**History where the stories are.** P0, P1, H1 and the bent normal are the shared weathering bake on every page group: true and quiet. H2 and H3 are allocated per page group by the history budget per view: the change query's weight, summed over the judged views that see a group, ranks the groups, and the highest get the story pages up to a cap. A group without them reads each of their layers as its material's quiet mean through `OS_History`. Adding a layer to a kind later is a registry entry and a rebake, never a rebuild. *Provisional:* the cap, at most a fifth of resident groups and 0.2 GB, settled by the years sheet and cold readers.

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

**Units,** powers of two in metres, each with an id in the plan: 4 m draw-and-rebuild chunks at L0 and L1, cut at piece boundaries; 16 m page groups of those chunks, which hold the place and history pages; 32 m cells at L2 and L3; 64 m land and streaming chunks (two cells); 128 m blocks (four cells). A change rebuilds the chunk, not the thing; at L2 it regenerates its run and re-merges the cell. GPU occlusion culls by bounding sphere, so a 33 m flight drawn whole is never culled. The sizes hold at scale: a stair's 4 m holds 100,000 triangles at final quality and is placed in about 0.7 ms. A house's 4 m holds only about 560 triangles at test quality, but the near count is bounded by reach, not by the city, and draws are cheap, so it still draws as its own chunk. A larger draw unit would draw a stair's 400,000 triangles at L0 out to 24 m, past stone's eye-level line, and quadruple a watched repair's upload.

**Precision.** Records and plans hold positions as integers in mm. Meshes are Float32 relative to their own unit's corner, so a 128 m block holds 0.02 mm. Units are placed from the plan relative to a world origin, rebased to the camera's 64 m chunk when the camera passes 2 km from it; within 2 km a float holds 0.25 mm. Shaders that read absolute position (wind, fields) get the origin as a split global; marks read UV2 and ids, so a rebase moves none. *Provisional:* the rebase's hitch. The scale test drew to 2 km in Unity's float coordinates (0.24 mm steps) without a rebase.

**Repetition** (D6.4). Only what really was mass-produced repeats. Bricks, roof tiles, factory windows and doors, catalogue houses, and setts (hand-split but to standard sizes) come from libraries, each instance varied by placement, wear and history. Everything made by hand for one place is its own: a unique fitted piece, made in the player per chunk from its record and seed, costing build time and memory, never disk. One stair with its walls is 816,000 triangles and 36 MB at full detail today; the levels and the 4 m chunk keep unique pieces at full detail only near the camera. A repeat-finding check on golden views proves no library piece is found. Hand-split wall stones not made to standard sizes stay their own too, since the geometry fits its pool with levels: at test quality, L0 for every house in the 300 m streaming radius would be 600 MB, and L0 reaches only 20 m (the scale test). Only if House A's final-quality chunks break the pool does Øystein decide whether those stones may come from a large library where no repeat can be found.

**Hand-over.** A dithered cross-fade, never animated, since that breaks the Resident Drawer. Both sides share marks, seed and history address, and switch where values match. At L2 to L3 it fades per cell with hysteresis. *Provisional.*

**Instancing.** The Resident Drawer with the user value draws kit parts and street things; our own BatchRendererGroup draws swarms; no Entities. One 32-bit value indexes both the facts buffer and the pick table. Shaders use `#pragma target 4.5`, `DOTS_INSTANCING_ON`, `LOD_FADE_CROSSFADE` and `unity_RendererUserValue`. Burst, Collections and Mathematics are in `manifest.json`. *Provisional:* the Drawer can be slower when GPU-bound, and MSAA turns depth priming off.

**Shadows from proxies.** L0 and L1 never cast. L2 casts in the first cascades, L3 and L4 beyond. Small parts, tufts and litter never cast. Each chunk has a caster proxy. Trees cast from their opaque cores and lobes, never from leaf cards. People, boats, lamps, flags and laundry cast from a coarse level of their own in the first cascades only; a lamp's light casts by its tier. Today the cascades draw the town twice more (15 million triangles against 5.5).

**Rows by hash.** Slate courses and sett rows come from a per-row hash evaluated alike in C# and HLSL, so far levels draw the same slates without a bake.

**The painted far town** (BB2). Shells and blocks are built either way; unpainted, they are the district level from the same data. A look test decides only whether the atlas is painted (anisotropic Kuwahara on albedo and normal, one direction map) or plain. Reserved at 3.1: aligned cells; a per-thing atlas rectangle in the chunk format; per-triangle ids on shells; the shell's channels; `_OS_BAKE` in every shader (unlit albedo at the date, normal, history, ids), shared with the light's debug views; the cached bake; per-cell cross-fade. The shell level costs 18 to 20 days once, painted or plain, against 35 to 40 for far levels per kind (the study's estimate). Painting is about 3 of those days, so the test decides the look and those days only. *Provisional:* the test, 5 to 7 days (four arms, three lights, motion sheets, M4 timing, cold readers, six drop rules), timed by Øystein: after the gully port and before House A's far level (21 October).

Reasons: decisions §6.

## Budgets

All provisional until each fix is A/B'd on the harness. The measurements are the harness's pass run (`docs/measuring.md`, The pass budget) and the scale test (`docs/research/scale-test.md`). The baseline: the blue hour 25 to 35 ms with 5.5 million triangles, 76 draws and no casters; drizzle 28 to 42; low sun 84 to 96; the birch 10 to 16; memory 1.4 GB by the system's footprint; the main thread about 1 ms, so the frame is GPU-bound. Scale adds no new failure to the frame: a 2 km district, with L0 to 200 m and shells beyond and the beams off, draws the street stop, 12 m and city camera in 21 to 25 ms in the blue hour and 27 to 31 in drizzle and low sun, the same per-pixel floor as the corner.

**Frame by pass** (S2; GPU ms at 1440p; 14.7 used, 2.0 reserve). Today is the street stop in its dearest light (`docs/measuring.md`, The pass budget).

| Pass | ms | Today | Note |
| --- | --- | --- | --- |
| Opaque geometry, L0 to L4 | 5.0 | 14.5 (1.9 flat) | a raster floor of 2.0 (drawn flat) and shading over flat of 3.0: `OS_History` 0.5 at overdraw 1 with depth priming (0.17 ms a page sampled), surface shading 2.5 split by shader family from the first flat A/B at the street stop, measured with history off |
| Shadow cascades from proxies | 2.0 | 7.1 | fewer cascades, proxies as casters, the far cascades cached |
| Sky, atmosphere, air | 1.5 | 2.4, beams 64.3 | the haze leaves every fragment for a low-resolution volume, counted here; the beams at a quarter of the pixels, about 0.5 |
| Lights and spill | 1.0 | | 8 to 16 shadowed spots |
| GTAO | 1.0 | 4.3 | indirect light only, at half resolution |
| SSR and water | 1.0 | 3.9 | URP's own SSR, temporal filtering off, at half resolution where wet |
| Trees and alpha-tested layers | 1.0 | the birch 12.6 | the birch's own fix |
| Full-screen passes | 0.4 | 2.6 to 3.8 | fog lights, key block and palette in one pass, folded into post's, skipped when idle |
| Post (grading, dither, focus stencil) | 0.8 | 3.6 | |
| Anti-aliasing | 0.8 | MSAA 4× 6.5 | see Light, time and world state |
| Id readback, UI | 0.2 | | |
| Reserve | 2.0 | | holds people's share until the grey walker is measured |
| **Sum** | **16.7** | | 14.7 in passes and 2.0 reserve |

Every measured pass but the sky is over twice its line, so each gets a fix. The fixes that need no levels (the beams, the haze, the shader families, the birch) are their own track and land before the port's proof sheet. The levels, proxies and groups are the tools the other fixes are measured with, so they are not held back as triangle work.

**Triangles per judging view** (millions visible after culling; ceilings 2 million and 3,000 draws). The ceilings hold shadows, edges, memory and L0's reach; they do not set the opaque pass's cost, which is its shaders'. Drawn flat, the corner's 2.74 million triangles cost 1.9 ms; in their shaders, 14.5.

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
| Fields, ground, height | 0.2 | Render targets | 0.3 |
| | | Engine, code, audio, UI | 0.7 |

Place and history maps hold the four base pages on every page group within L2's reach and the story pages within their cap.

Geometry fits its pool with levels: at test quality, L0 for every house within the 300 m radius would be 600 MB, and L0 reaches only 20 m; a house is about 1 KB as a shell. Final-quality houses are heavier, so House A checks the pool again.

**Disk per kilometre** (both sides, about 250 houses; a house's envelope of walls and roof is 444 m²):
- *Shipped city-wide:* the records (315 bytes a house), the libraries, and the coarse geometry: shells (1.6 MB a km²), L4 and the ground's rings. A few MB a km².
- *Built on demand and cached on disk:* near levels (L0 is 708 KB a house at test quality, 93 MB a km); instance records about 30 MB; place and history pages by face class, about 190 MB at four base pages a byte a texel with mips, plus about 4 MB a flight of walked stone at 2 cm and story pages on a fifth of groups; shell atlases, about 340 MB at 5 cm. The cache stores every page compressed, so a revisit skips the bake, and evicts by distance under its byte cap.
- *The heart's start date ships whole:* about 0.55 GB of L0 at test quality, plus its pages and atlases.

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

- **Nothing relies on temporal accumulation** (S1), so marks stay stable and golden views repeat. The port builds for SMAA at native 1440p with depth priming on; MSAA 2× and 4× stay harness arms, FSR 1 the fallback for fewer pixels, STP only once every mover writes motion vectors. Shaders do not rely on alpha-to-coverage. The reason: MSAA 4× costs 3.4 to 6.5 ms at the corner against a 0.8 ms line, and turns depth priming off while the opaque pass is mostly shading.
- The scenes keep MSAA 4× until 3.4, so step 3's history A/B changes one thing. At 3.4 the filter is chosen on levelled geometry (a median triangle of ten pixels or more, since MSAA pays at edges), by the motion sheets' shimmer measure and the golden views, with the cross-fade and the leaf cards' clip judged under each arm; the baselines are re-accepted once (*provisional*).
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
- A flight's landings keep the landing rule: the shortest is one stride and one going, so it is crossed in step, and no run between them goes over 18 risers or 3.3 m of rise, the limit of real practice (`stone.py`'s `step_plan`; `blender/tools/setout_check.py`).
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
| Export checks | budget per level, the 60 % rule, median triangle, fits never silent, the kit validator, plan validity, licences, the id test, the rigidity check (each rigid piece against its part mesh by its best rigid fit; over 0.1 mm fails, BB3) |
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

**Scale.** The world shipped is the records, the libraries and the coarse geometry (shells, L4, the ground's rings): a few MB a km². Chunks are binary, keyed by the hash chain, evicted least-recently-used by distance under the byte caps. A file holds many units: one file a 128 m block holds its records, shells, L4 and ground, so the 0.28 ms a file is paid once a block, and near levels are cached a file per 64 m chunk. People are generated at runtime from identity numbers, cached by a hash of record, age step and outfit. The heart's start-date cache ships, and near levels elsewhere build on demand from the record, with the same code for both. Shipping near levels does not scale: at test quality L0 is 708 KB a house, 2.1 GB a km² of town like the core, 2,300 times the house's record of 315 bytes, so a metropolis would need hundreds of gigabytes. Building keeps up: walking asks for about 4 near chunks of 4 m a second and driving 40, and placing costs 0.68 ms of Burst per 100,000 triangles.

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
| History carrier | maps at every level | the gully's A/B in grey light at eye level, FLIP within threshold, shown beside the target frame | step 3's R5, on 2b's as-laid build |
| Map density | by face class; pages by 16 m group | the years sheet at 12 m and the high view | step 3's R6 |
| Page format | RGBA8; then BC7 per page, a failing channel pair to BC5 | a real page's BC7 error per channel, mips 0 to 2, 99th percentile at most 2/255 (H1.B about 1/255) | step 3, at R3's end, before R4 |
| History's cost on a busy screen | 0.5 ms a screen at overdraw 1, 0.17 ms a sample; a minified sample measured at about 0.02 ms on a quad | the gully's four arms (all minus history off, projected per stone pixel to the street stop): history's change to an already textured output, paid in the passes after the draw | step 3's R7 |
| Chart borders in motion | charts per run, 16-texel grid, 2 texels of padding, three mips, trilinear | a motion sheet across chart borders at mips 1 and 2 | step 3's R6 |
| Page binding under the Resident Drawer | global page arrays and piece table; the pick index in the user value, its unit slot giving the table's base | the user value's DOTS-instanced variant under the Drawer | 3.4, with the Drawer's pragmas |
| Map rebake cost; the player's GPU encoder | 2 ms GPU a 1024×512 page with its compression, on the GPU | the bake's own shader and a GPU encoder (BC7, BC5, BC4), timed on the M4 | step 5, when pages first bake in the player (step 3 bakes offline) |
| Place bake in the player | P0 and P1 baked on the GPU per page group | a spike: cost per house against driving's 40 near chunks a second | before step 5 |
| Shell atlas bake | on demand within L3's reach; plain until it lands | its input (the shell and the function, or L2) and whether cells cache atlases; then its cost per cell against the city pan's 90 cells a second | the input at step 1; the cost before step 5 |
| Mixed texels in a chunk | each part's rectangle at its own texel, charts per run | packing waste measured on the gully's pages (10 to 15 % per run estimated) | step 3's R3 |
| Story pages | a fifth of resident groups, 0.2 GB | the years sheet, cold readers | step 4 |
| The brush | anchored to UV2 | a motion sheet | after the port |
| Level boundaries, hand-over | error under a pixel; dithered cross-fade | motion sheets at one sample a pixel | 3.4 |
| Levels for library parts | generator levels, meshoptimizer | the Mesh LOD test on the gully's FBX | 3.4 |
| Resident Drawer | on | the harness A/B | 3.4 |
| Painted far town | shells built, atlas plain | the look test | Øystein's call |
| Frame by pass, disk, build time in C# | the tables above; family shares from the first flat A/B | each pass's fix A/B'd on the harness; the C# core timed | the port |
| Anti-aliasing | SMAA at native with depth priming; the scenes on MSAA 4× until then | shimmer and golden views on levelled geometry, the cross-fade and leaf cards under each arm | 3.4 |
| The shade's lookups | in `OS_ShadeP` | look test | 1c |
| Light counts | 8 to 16 shadowed spots | the harness | steps 3 and 6 |
| Memory for a second date or record | 0.5 GB | a second date resident in the district player, by footprint | step 4 |
| Water-borne carriers | in the water bake | the gully's handrail post | after the corner's wash |
| Board atlas; hex-tiling | as stated | look tests | House A; step 3 |
| Ground edges | slow as mesh, fast as shader | the corner's years sheet | 1d |
| Birch cost; regrowth in play | opaque first; growth offline | the harness; a measurement | now; step 7 |
| People's far mesh, archetypes | identity numbers in the contract | the recognition test, crowds of 500 and 2,000 | step 5 |
| Collision and navigation | proxy per chunk, navmesh per 64 m cell | a short craft study | before the grey walker |
| Streaming a frame | 1.5 ms main thread, 8 MB, 64 renderers; reads on workers | the renderer count under the Drawer; a cold read (`purge`, then the district loaded on workers; the scale test's 960 MB/s was a warm cache) | 3.4 |
| Origin rebase | at 2 km, to the camera's 64 m chunk | a camera driven past 2 km in the district player | before a town passes 2 km |
| Flags and laundry | stepped on twos | a motion sheet | before the wind |
| Water reflection | URP's SSR, no temporal filtering | the harness, a motion sheet | step 6 |
| A house at final quality; the geometry pool | unknown; the pool fits at test quality | House A | House A |
| Scripting backend | Mono, every hot loop in Burst | IL2CPP against Mono on the C# core's main thread (installing IL2CPP is Øystein's permission) | the week after the port |
| Pins across a rules change | on slot and fill ids | the first `rulesetVersion` bump | the first bump |
