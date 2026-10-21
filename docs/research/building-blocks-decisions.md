# Building blocks: the decisions

Fable 5.1, 21 October 2026 (evening session). Input: the register (`docs/research/building-blocks-inputs.md`), the architecture pre-mortem, the packet of surrounding docs, the code inventory, the facts contract. Everything in `NOW.md` "Decided" is taken as fixed and not reopened.

Status words: **FIRM** (decided on evidence or judgement; build on it). **PROV** (provisional: a named measurement settles it; the default is what to build on meanwhile). "Needed by" names the step: 3.0 seeds, 3.1 stages, 3.2 history, 3.3 materials, 3.4 levels, House A, or later.

Stack assumed throughout: Blender 4.x Python offline; Unity 6000.6 URP 17.6 C# with Burst; the base M4 Mac mini, 16 GB unified memory, 60 fps at 1440p, so 16.7 ms a frame.

## 0. The five decisions everything else hangs on

1. **Parts offline, the town assembled in the player.** Fixed parts are judged meshes made in Blender; fitted parts are judged functions. Plan, life, placement, fitted geometry per chunk and level, the extrinsic bakes and the cheap checks run in C# in the player. Python builds the gully this week as the specification; C# becomes the single source stage by stage from the week after.
2. **Contracts are files, not prose.** JSON Schema files in `schemas/`, golden fixtures per stage on the gully, parity tested at every stage boundary in data before any mesh.
3. **History is a function of the record and the date.** Maps hold inputs (rates, reset years, age offsets); the date is a shader global; a jump costs a uniform. One exception, reserved now: the far level (the shell) caches an output bake, invalidated by the change query.
4. **Ids are stable down to slot and fill; pieces are derived.** Record ids are strings typed by prefix and never reused; slots and fills live in the record and survive regeneration by construction; piece indices and 32-bit pick indices exist only at draw time, through a table per chunk.
5. **Budgets are in milliseconds, megabytes and triangles, per pass and per kilometre, on 16 GB.** All provisional until the harness and the scale test, but a line exists for each before any geometry moves. The frame today is pixel-bound (25 ms with 5.5 million triangles and no shadows), so the shaders get a budget and an A/B before the triangles get a port.

## 1. The stage map

| Stage | Runs where | Source of truth now | Flips to C# when | Output (hashed) |
| --- | --- | --- | --- | --- |
| 1 Facts | offline: pack, fixtures, the curated 1989 record; the engine's own process in play | the record files (JSON) | never: data, not code | record hash (schemaVersion, rulesetVersion, worldSeed, content) |
| 2 Plan | both: Python this week; C# core in the player and for golden views and the shipped cache | Python `resolve.py`, `step_plan` | the week after the port: plan-hash parity on the gully, then the house resolver before House A | plan (integers, mm) and plan hash |
| 3 Life | both: Python at 3.2; C# on change in the player; the state at the date in HLSL | Python `upkeep.py` and the layer curves | with the chunk assembler, the week after the port | life intervals per piece and texel inputs; life hash |
| 4 Geometry | fixed parts: Blender only. Fitted parts and placement: Python now, C# with Burst in the player | Python `blender/parts/*.py` | per family at its port (stone first, then the house kit) | mesh per chunk and level; mesh hash per chunk and level |
| 5 Bake | intrinsic channels into library parts: Blender. Extrinsic maps, field tiles, shell atlases: the player (GPU) | Python this week | with the chunk assembler | map pages; bake hash |
| 6 Export / chunk cache | library parts as FBX plus JSON sidecar through the editor importer; chunks never as FBX: a binary cache keyed by the hash chain, on disk in `cache/chunks/` (untracked) and `StreamingAssets` for a shipped start-date cache | Python exporter | with the chunk format | the chunk file |
| 7 Checks | offline: validate record, validate kit, parity, mesh hashes, golden views (FLIP), motion sheets, cold readers. Player: budgets per level, fits refused never silent, plan validity, cache verified on load | `tools/` Python | checks that run in the player are written in C# once; offline checks stay Python | pass or fail, logged |

Rule for the flip (pre-mortem, "the source-of-truth split"): a stage's Python is frozen at its port date for a kind, kept as the reference for parity, and deleted for that kind when the C# passes parity on the kind's golden fixtures and one strict review. Agents then iterate in C#, and look sheets run the C# through Unity batch mode. FIRM. Reason: two live sources drift (`where-generation-runs` §4); Øystein accepted the port.

## 2. The contracts

**D1.6, FIRM, needed before 3.1.** JSON Schema (draft 2020-12) files, hand-written, in `schemas/`:

| File | Describes |
| --- | --- |
| `record.schema.json` | any record: id, kind, provenance, precision, lifespan, events, links, pins |
| `kind.schema.json` | a kind file: its stages' parameters, slots it admits, families it accepts, levels and budgets, motion contract, affordances, what it writes to and reads from fields |
| `part.schema.json` | a part family: `made_as`, era range, size ranges, fit modes, pivot, sockets, removal mark, variants, per-level error, budget, shadow role, collision role, motion class per element, intrinsic channels, lifecycle state |
| `plan.schema.json` | a plan instance: part path, variant, seed, placement in mm, fit used, placing event, chunk id |
| `slot.schema.json` | slots and fills (section 4) |
| `interval.schema.json` | life intervals: from, to, reset year, rate, age offset, cause |
| `channels.json` | the vertex and texel channel spec (section 5), with byte widths |
| `chunk-format.md` + `chunk.schema.json` | the binary chunk's byte layout, versioned; its header fields as JSON |
| `maps.json` | the map registry (section 5) |
| `layers.json` | the history layer registry (section 5) |
| `world-state.schema.json` | the one world state (D7.3) |
| `change-query.schema.json` | `changes(scope, t0, t1)` (D12.4) |
| `naming.md` | the naming grammar: ids, part paths, kinds, materials, chunks, maps, fields, on one page, written before the first kind file |
| `CHANGELOG.md` | every schema change with its migration |

Reason: pre-mortem story 2 and the register's gap 1. Code generation is not worth a tool chain for about a dozen types; what the parity test needs is fixtures, not generated classes. Python validates with `jsonschema` (MIT) in `tools/`; C# types are hand-written twins, held to the schema by parity tests over the golden fixtures (`fixtures/golden/<kind>/<stage>.json`, written by Python this week). The binary chunk is specified as a byte table with a version word and read by one reader per language, tested on the same golden chunk.

**Record versioning and migration (pre-mortem), FIRM, from 3.1.** Every record file carries `schemaVersion`; `migrations/NNN_<name>.py` run on every fixture by `tools/migrate.py` in a check that fails if a fixture is behind. C# reads only the current version; migration is offline. The curated 1989 town and its pins migrate by the same scripts, so a rule change never kills it.

**Repository layout, FIRM.** `schemas/` (above); `kinds/<kind>.json` (stair, wall, house, birch, lamp, bollard, natural-stone, ground-act); `packs/stavanger-1989/` (section 11); `blender/parts/<family>/` (part code, Python now; C# twins later in `unity/Assets/Code/Parts/`); `fixtures/` (records, golden fixtures, the engine run); `migrations/`; `cache/` (untracked: chunks, tree timelines, exported library meshes); `tools/` (checks and builds). I overrule the plan's `blender/kinds/`: a kind file is read by both languages and the player, so it does not live under `blender/`.

**Hash chain (D2.4), FIRM, 3.1.** One tool, `tools/hashes.py` now and `Hashes.cs` later: `schemaVersion` + `rulesetVersion` (a hash of the kind file and the part functions' versions) + `worldSeed` → record hash → plan hash → life hash → mesh hash per chunk and level → bake hash. Each is a cache key; a stage whose inputs' hashes are unchanged is skipped (this is also the authoring-loop budget's lever).

## 3. Seeds and determinism (D2)

| # | Decision | Reason | Status | Needed by |
| --- | --- | --- | --- | --- |
| D2.1 | SplitMix64 on stable ids (part path, purpose) everywhere; `random.Random` and float-formatted keys removed; a replaced part takes a new id and so a new seed | Python documents that `random` changes across versions; `stone.py:418` keys on formatted floats and re-draws neighbours when a piece moves | FIRM | 3.0, own commit, new baseline |
| D2.1b | One hash spec for both languages: Python's `hashing.py` (`h()`: FNV-1a over UTF-8, SplitMix64 start `0x2545F4914F6CDD1D`, `unit = (h>>11)/2^53`) becomes the spec; `Core/Hash.cs` is changed to match; `fixtures/golden/hash-vectors.json` holds 200 key-value pairs both must reproduce | the resolver's plan hashes and every fixture signature already rest on Python's version; C# is cheaper to change | FIRM | 3.0 |
| D2.2 | The five cross-language rules: seeds on stable ids; choices only from integers or + − × ÷ and sqrt; plans and life in integers (mm, per mille, years and months); geometry compared by tolerance; sort by stable id. HLSL joins where layouts are evaluated at a point (D6.10) | `where-generation-runs` §4 | FIRM | 3.1 |
| D2.3 | Bit-exact mesh hash within one language; across languages a tolerance compare per chunk and level (positions 0.05 mm, each channel by its spec's quantum); FLIP on golden views last | a quantised hash flips at a boundary and is no tolerance test | FIRM | 3.1 |
| D2.5 | Burst deterministic float mode only for the shipped cache verified on load; everywhere else plain | nothing else needs cross-machine bit equality | FIRM | with D15.1 |
| Det. debugging | `tools/diff_stage.py`: a diff by stable id at every stage (plan, life, pieces), not only "differs"; a two-machine run in the scale test week; Blender and Unity versions pinned in `packs/<pack>/tooling.json` and checked by the runner | pre-mortem, "determinism tooling" | FIRM | 3.1; the two-machine run Tuesday |

## 4. Records and ids (D3, D13.1, C3)

**D3.1, FIRM, structure before 3.1, house migration before House A.** One dated record, one structure: a thing holds slots; a slot (opening, socket, surface region, pane, affordance) is never deleted and holds fills in date order; a fill has its part, placing event, from and to, the fit used and the mark its removal leaves. The window's surround is its own fill in the opening slot; coats are fills of a facade's surface region; a stone repair is a fill. The resolver's `_shop_fitted` deletion and the single `original` per cell go. Reason: three studies converge on one structure (inputs 5, conflict 1); one change query, one pick path, one superposition check.

**Ids end to end, FIRM, 3.1.**

| Level | Form | Minted by | Survives |
| --- | --- | --- | --- |
| Record (thing, person, place, plant, sign, room, light) | `<prefix>-<token>`: `bld-101`, `st-gully`, `wl-gully-e`, `p-812`, `pl-mill` | its owner: the engine for its records; the pack script for `generated-past` ids (deterministic counter from the world seed and plan unit); by hand for `authored` | everything: it is in the record and never reused |
| Event | `<record>/<n>`: `bld-101/13` | the owner, appended | everything |
| Slot | `<record>/<slot>`: `bld-101/op-n1-2` (an opening), `st-gully/tr-17` (a tread), `bld-101/sf-n` (north surface) | the plan stage, from the kind's slot naming rule in `naming.md`; semantic, never positional counters | regeneration under the same rules; a rules change that renames slots ships a migration |
| Fill | `<slot>/<n>`, ordinal in date order | appended on each event; never renumbered | regeneration; an out-of-order insertion is a migration, not a renumbering |
| Piece | `<fill>#<i>` | derived by the geometry stage | the fill's rules version only; pieces may be reborn |
| Pick index | 32-bit: 12 bits chunk or cell slot, 20 bits piece or instance index | the assembler at draw time | one build of the chunk; never stored in the record |

Stability is promised down to fill. The id test (`tools/id_check.py`): bump `rulesetVersion`, regenerate, count record, slot and fill ids lost and born, fail above zero; piece changes are reported with counts. Pins (D1.10) attach to slot and fill ids, so they survive regeneration; whether a pin survives a rules change is the first bump's lesson, with the test in place. Packs side by side (the world-map idea): one world is one pack; a second pack's ids are prefixed by its pack id at load, so nothing collides. Picking resolves the pick index through the chunk's table to a record id and part path, and then to the level of the hierarchy that suits the distance (D3.5: part, thing, group, place).

| # | Decision | Reason | Status | Needed by |
| --- | --- | --- | --- | --- |
| D3.3 | Every record and event carries: its place among the five kinds on screen; provenance in four values `simulated`, `generated-past`, `derived`, `authored` (the word `engine` is retired); precision (year, decade, month); actor; weight; `where` | the facts contract needs four; the engine's requests 28 and 32 match | FIRM | 3.1 |
| D3.4 | One record admits every kind as data: parts, plants, signs, rooms, lights, garments, carried things, social traces, works phases, photographs | one change query and one pick path | FIRM | schema now |
| D3.5 | Hierarchy part, thing, group, place; far levels resolve to the thing | interface §6 | FIRM | 3.1 |
| D3.6 | Readable text only from records (the words layer) | fronts §6 | FIRM | House A |
| Record validation | `tools/validate_record.py`: fill inside its slot's dates and size, dates in order, actor present, family within era, provenance valid, ids unique and well formed, nothing deleted, the facts contract's hand-off checks | pre-mortem, "content validation at the record level" | FIRM | 3.1 |
| Part lifecycle | A family is `draft`, `judged`, `library`, `deprecated` or `removed`; a removed family keeps its last judged mesh and function as a tombstone so old records still draw | pre-mortem, "retiring a part" | FIRM | the first library |

**The facts contract: confirmed with three changes.** (1) Four labels, as above. (2) A row for each game's domain model (the match, the edition, works and prices): owned by the game's own module, `simulated` when the engine runs it and `derived` when the game's rules do; written before that game is built. (3) The hand-off checks become rules of the record validator. The S seam (1959) stays; care from money, presence, age and events, never character, stays as a Rule 8 safeguard.

## 5. Channels, maps and the layer registry (C1, C8, D5, D7.1, D8.1)

**Vertex layout (`channels.json`), FIRM as a spec, byte widths PROV until the gully's A/B at 3.2.** Fitted and merged meshes at L0 to L2 are written through `MeshData` in the player, so the layout is ours; library parts cross FBX with a JSON sidecar that names which UV set carries which channel (D10.3).

| Slot | Content | Format | Bytes |
| --- | --- | --- | --- |
| Position | | Float32×3 | 12 |
| Normal | | SNorm16×4 | 8 |
| UV0 | grain, metric per piece | Float16×2 | 4 |
| UV1 | atlas address into the chunk's maps | UNorm16×2 | 4 |
| UV2 | mark coordinate, run-continuous (the brush) | Float32×2 | 8 |
| UV3 | piece index, edge distance | UNorm16×2 | 4 |
| UV4 | face kind, hollow rate, flutter weight or element depth, spare | UNorm8×4 | 4 |
| UV5 (optional) | rest or undisplaced position for deforming and wind-moved parts | Float16×4 | 8 |
| UV6 (optional) | element index and depth (trees, people, flexible parts) | UNorm16×2 | 4 |

Base 44 bytes, 56 with both options. Shells (L3, L4): position, normal, atlas UV, and per-triangle thing index, part slot and material class in UV1 and UV3: 28 bytes. C4 is settled as both: grain per piece in UV0, marks per run in UV2. The light's inputs are not per vertex (C5): they sit in the place map.

**Per-instance (C8), PROV, the picking spike during the port; default below.** Under the GPU Resident Drawer each kit instance carries only its transform and the 32-bit Renderer Shader User Value, which is the pick index above and also indexes a per-cell `StructuredBuffer` of instance facts: record and part indices, seed, reset year, care, season and hue, wind phase, coat-table offset. Swarms (setts, slates, tufts, litter) go through our own BRG buffer with transform, part and species, seed and rank, wind phase and field tile. People have their own path (skinned, not the Drawer).

**History maps (D5.1, D5.2, D5.3, D5.4).**

| # | Decision | Reason | Status | Needed by |
| --- | --- | --- | --- | --- |
| D5.1 | Maps store inputs: per-texel rates (or the fields that make them) and age offsets; reset years per piece and repair surface; the fabric date a global; each layer is its material's curve at rate × (date − reset + offset) | the layer law is closed form already; a jump costs a uniform, which the decided rule (watched or jumped draw the same) needs | FIRM; checked on the gully's years sheet and FLIP | 3.2 |
| D5.1b | Exception reserved: at L3 and beyond a shell caches an output bake of pigment with slow history, invalidated per thing by the change query; drift stays live from the reset year in the index map | the painted far town needs it, and a cached evaluation of a function is still the function | FIRM as a reservation | the format at 3.1; the bake with the look test |
| D5.2 | (c) maps at every level, addressed from the atlas UV; per-vertex only piece constants and what moves geometry (the hollow's rate and gradient) | no hand-over between carriers where values must match; houses need maps anyway; decimated to a third, the flight keeps 95 % within 2 mm | PROV: the gully A/B in grey light at eye level, FLIP within threshold; default (c) | 3.2 |
| D5.3 | Unit: the draw chunk (section 6). Texel: 2 cm walked stone, 4 cm walls and trims, 8 cm roofs and ground; each field sized by its smallest feature | at 1 cm a kilometre of fronts is about 280 MB; at 4 to 8 cm 4 to 18 MB; the gully at 2 cm is about 1 MB | PROV: the scale test with synthetic maps at both densities, and the A/B (gap 9, BC7 in a smooth field); default as stated | density 3.2; unit 3.4 |
| D5.4 | Resets per piece and repair surface; rates and age offsets per texel. A rate change (a gutter, a fallen neighbour, care falling) rebakes the affected map region on the GPU and does not rebuild the mesh | overruling the register's "rebuilds its chunk anyway": the mesh did not change, and a mesh rebuild on every care change is pre-mortem story 5 | FIRM; years sheet | 3.2 |
| D5.4b | An invalidation table in the chunk format: for each act kind, which map pages, which instances and whether the mesh is dirtied; map rebakes run on the GPU behind the dated card, budget 2 ms GPU per 1024×512 page | pre-mortem story 5 | PROV: one page baked and compressed in the scale test's player, timed | the table at 3.1; the number Tuesday |
| D5.5 | Intrinsic channels (face kind, edge distance, own occlusion) in the mesh or library part; extrinsic (years, feet, water, damp, care) per instance, field tile or map | a library sett carries its lane's years | FIRM | 3.2 |
| D7.1 | The light's inputs live in the place map (sky seen, ground seen, openness, weather exposure) with a two-channel bent normal at L0 to L2; shells drop the bent normal; impostors their own atlas | one carrier, no hand-over; P's slim vertex and the light's four channels both satisfied | FIRM | 3.2 |

**The map registry (`maps.json`, D8.1), FIRM, before 3.2.** One entry per map: owner, resolution, unit, format, readers, rebuild trigger. C9 (6 cm against 0.5 to 1 m) is two different things with two names: *fields* are coarse and land-owned; *place maps* are fine and chunk-owned, sampled from the fields plus the chunk's own geometry.

| Map | Owner | Unit | Texel | Format | Readers | Rebuilt when |
| --- | --- | --- | --- | --- | --- | --- |
| Height and sky | land | 64 m chunk | 0.5 m heart, 2 m beyond | R16 + RG8 | far shadows, horizon, light | a ground act |
| Ground map (soil, seasonal albedo, wet) | land | 64 m | 0.25 to 0.5 m | RGBA8 | rock, wall and plinth feet, blade roots, the light's seen ground | a ground act or the season |
| Fields (soil, flow, wetness, wind and salt, sun dose, made ground, feet) | land | 64 m | 0.5 to 1 m heart, 2 to 4 m beyond | one `Texture2DArray` | place-map bakes, the placer, deposits | an act, the feet plan, the decade |
| Place map, page P0 (feet, water held, sky seen, ground seen) | the kind's chunk | draw chunk | 2 / 4 / 8 cm | RGBA8 → BC7 | every shader through `OS_History` | geometry or a neighbour's rain shadow changes |
| History page H1 (rate: polish, lichen, moss; age offset) | chunk | draw chunk | same | RGBA8 → BC7 | same | a reset, a rate change |
| History page H2 (reserved: wash and deposit, splash, carrier, contact) | chunk | draw chunk | same | RGBA8 | same | when the layer lands |
| Bent normal | chunk | draw chunk | same | RG8 (BC5) | the shade | geometry |
| Deposits (leaves, litter) | chunk | draw chunk | 8 cm | R8 | ground and plants | the day's wind, feet, keepers |
| Shell atlas (albedo, normal, light and weather, index) | the 32 m cell | cell | 3 to 5 cm | BC3, BC5, BC3, R8G8 | shells and blocks | the change query names the thing |
| Impostor atlas | species | library | fixed | BC7 | far trees | the species' timeline |

**The layer registry (`layers.json`, D5.6), FIRM, 3.2.** Each layer names its page and channel, its inputs, its curve's owner (the material record) and its reset rule. Every shader reads layers through one `OS_History(address, layer)` function in one include, so a new layer (soot, salt, rust runs, carried stains, splash bands, failing coats) takes a reserved channel or a new page and touches one include, never a kind. Slots now, values later.

| # | Decision | Reason | Status | Needed by |
| --- | --- | --- | --- | --- |
| D5.7 | A superposition validator (newer over older) and a diff across two dates that fails any pixel outside the change list | time item 7 | FIRM | House A |
| D5.8 | Fine marks thresholded on fields with noise in the part's mark coordinate, faded to the mean by footprint; the brush re-anchored to the run's mark coordinate (UV2), borders blended, its fine octave faded by footprint; octave stepping judged on motion sheets | today's brush reads world position on a 71 cm grid and slides on anything that moves | mark contract FIRM at 3.1; the brush PROV: motion sheet after the port | 3.1; after the port |
| D5.9 | One budget mechanism, three counts (histories, acts, motion), chosen by the change query's weight | three studies ask for the same thing | FIRM; numbers from the years sheet and cold readers | weight at 3.1; step 4 |

## 6. Levels, chunks, instancing, repetition and the far field (D6)

**The levels, FIRM as a scheme; boundaries PROV by error in pixels, fades on motion sheets at 3.4.** Five levels per kind, each with its error in millimetres and budget in the part and kind definitions; the switch happens where the level's error is under about one pixel at 1440p (a pixel spans 0.48 mm per metre of distance, so a level is safe beyond about 2,000 times its error; the fade distance measured on one-sample-a-pixel sheets, not supersampled stills).

| Level | Name | Judging band | What it is | Merge unit |
| --- | --- | --- | --- | --- |
| L0 | close | eye level, under about 8 m | full fitted geometry, maps at full texel | 4 m draw chunk |
| L1 | near | the street stop, to about 20 m | the generator's second level from the same seed and outline (a tread from 1,100 to 100 to 150 triangles) | 4 m draw chunk |
| L2 | street | 12 m view, to about 50 to 80 m | coarse pieces, relief into the maps' normal; the piece map doubles as the pick map | runs of 3 to 5 m merged into the 32 m cell |
| L3 | shell | far, about 50 to 200 m | the thing's coarse mesh from its plan (a house 500 to 1,500 triangles, a flight a stepped ribbon), the shell atlas | 32 m cell, one mesh and one atlas page |
| L4 | block | city camera, beyond about 200 m | about 100 triangles a house, the shell atlas's small mips, no second bake | 128 m block |

Named tiers in `foundations.md` become judging bands, not switch distances. Trees keep their own levels to about 200 m, then opaque lobes. Moving and lit things (lamps, boats, people, laundry) keep their own instanced levels, culled by screen size.

**The painted far town.** The shell (L3) and the block (L4) are built either way: unpainted, they are the plan's district level made from the same data. What the look test decides is only whether the atlas is painted (anisotropic Kuwahara on albedo and normal with a shared direction map) or plain. The architecture reserves now, at 3.1 (hours): 32 m cells aligned so that two make a 64 m land chunk and four a block; a per-thing atlas rectangle in the chunk format; per-triangle thing index, part slot and material class on shells; the shell's channel set (section 5); an unlit bake mode in every shader (`_OS_BAKE`: albedo at the date, normal, history channels, ids), which the light's debug views need anyway; the D5.1b exception; per-cell dithered cross-fade with hysteresis as the default hand-over. The test itself (5 to 7 days, four arms, three lights, motion sheets, M4 timing, cold readers, six drop rules) is PROV, and its timing is a scope question for Øystein (section 13). Reason: the register never weighed this study; it replaces D6.9 and most of the far part of D6.1, D6.3 and D6.6, and costs less to build than conventional far levels per kind (18 to 20 days against 35 to 40, the study's estimate) if it passes.

| # | Decision | Reason | Status | Needed by |
| --- | --- | --- | --- | --- |
| D6.2 | Fitted parts make their own levels from the same seed and outline (b), in the generator, so they exist in the player; natural stone and land through meshoptimizer (MIT, ships) with attribute weights and locked borders (d); Decimate or Mesh LOD only for offline library parts that pass the A/B at each switch | Decimate weighs no attributes and Mesh LOD is editor-only and melts joints; only (b) and (d) run in the player | PROV: the Mesh LOD afternoon test on the gully's FBX for library parts; default (b) and (d) | 3.4 |
| D6.3 | Nested units, all powers of two in metres: 4 m draw-and-rebuild chunks at L0 and L1, cut at piece boundaries; 32 m cells at L2 and L3; 64 m land and streaming chunks; 128 m blocks. Every unit has an id in the plan. A change rebuilds the chunk, not the thing | GPU occlusion culls by bounding sphere, so a 33 m flight is never culled; a change must rebuild something small; the painted far town's cells and the land's chunks must align | chunk ids FIRM at 3.1; sizes PROV: the scale test (load and rebuild per chunk, demand rate, cache per kilometre) | 3.1; 3.4 |
| D6.4 | (c) Things never repeat. Pieces may repeat where no viewer can find the repeat: beyond a few metres apart, turned or mirrored, re-weathered by their own place. Unique is only what wear or a hand shaped for one spot (worn treads, carved stones, bespoke joinery). Factory-made pieces come from small libraries, hand-made from large ones. Measured by a repeat-finding check on golden views | 816,000 triangles and 36 MB a stair cannot scale to a town; Øystein's words were about things ("no two stairs alike unless manufactured like that") | PROV: Øystein's reading (section 13), a look test of a stretched library stone at eye level, the repeat check; default (c) | before 3.4 for stone; House A for boards and rooms |
| D6.6 | Dithered cross-fade (never animated: it breaks the Resident Drawer); both sides share marks, seed and history address; the switch where values match; per-cell with hysteresis at L2 to L3 | painted P6; UUM-91634 | PROV: a motion sheet at the first switch (the screen-door risk without TAA) | 3.4 |
| D6.7 | The GPU Resident Drawer on, with the Renderer Shader User Value, for kit parts and street things; our own BRG for swarms; no Entities. Shaders to `#pragma target 4.5`, `DOTS_INSTANCING_ON`, `LOD_FADE_CROSSFADE`, `unity_RendererUserValue`; Burst, Collections and Mathematics named in `manifest.json` | one 32-bit value indexes both the facts buffer and the pick table | PROV: the harness A/B (the Drawer "can get slower" GPU-bound, and we are GPU-bound; MSAA turns depth priming off) | shaders at 3.4; libraries before House A |
| D6.8 | Shadows from proxies: L0 and L1 never cast; L2 casts in the first cascades; L3 and L4 beyond; small parts, tufts and litter never; a caster proxy per chunk | the cascades draw the town twice more today (15 million against 5.5) | FIRM | 3.4, the cut line |
| D6.9 | Replaced by the shell and block levels above | | FIRM | 3.4 for the gully's shell |
| D6.10 | Slate courses and sett rows by a per-row hash evaluated alike in C# and HLSL | far levels draw the same slates without a bake | FIRM | the first roof |

## 7. Budgets

All PROV: the harness's empty-scene run with passes toggled (Monday's tools session) and the scale test (Tuesday) replace these numbers; the lines exist now so nothing is built without one. The baseline that sets them: blue hour 25 to 35 ms with 5.5 million triangles, 76 draws, no casters; drizzle 28 to 42; low sun 84 to 96; the birch 10 to 16 ms; memory 231 MB; the main thread about 1 ms, so the frame is GPU-bound.

**Frame time by pass (ms of GPU at 1440p, 60 fps; 14.0 used, 2.7 reserve).**

| Pass | Budget | Note |
| --- | --- | --- |
| Opaque geometry, L0 to L4, Resident Drawer | 5.0 | the triangle budget below |
| Shadow cascades from proxies | 2.0 | after D6.8 |
| Sky, atmosphere, air (beams, motes) | 1.5 | low sun's 55 to 65 ms is a bug, A/B'd first; nothing is ported before it is found |
| Lights and spill (tiled, 8 to 16 shadowed spots) | 1.0 | D7.5 |
| GTAO (indirect only) | 1.0 | D7.7 |
| SSR and water | 1.0 | D8.7 |
| Trees and alpha-tested layers | 1.0 | D9.1; one birch today costs 10 to 16, so this is the first target |
| Post: grading, dither, focus stencil | 0.8 | D7.8 |
| MSAA 4× resolve | 0.5 | D7.2 |
| Id readback, UI | 0.2 | D13.3 |
| Reserve | 2.7 | people's share is held here until the grey walker is measured |

Rule: a pass over twice its budget after the harness's first run gets a fix stage before any triangle work; the triangles follow.

**Triangles and draws per judging view (visible, after culling; 2 million and 3,000 draws as ceilings).**

| Kind | Eye level | Street stop | 12 m | City camera |
| --- | --- | --- | --- | --- |
| Land | 0.25 M | 0.3 M | 0.35 M | 0.35 M |
| Ground cover and plants | 0.3 M | 0.25 M | 0.1 M | 0.05 M |
| Trees | 0.3 M | 0.3 M | 0.25 M | 0.15 M |
| Stone (stairs, walls, setts) | 0.3 M | 0.2 M | 0.15 M | 0.05 M |
| Houses and fronts | 0.35 M | 0.45 M | 0.5 M | 0.4 M (shells and blocks 0.1 to 0.3 M) |
| People (20 near, crowds held) | 0.3 M | 0.3 M | 0.2 M | 0.1 M |
| Water | 0.05 M | 0.05 M | 0.1 M | 0.1 M |
| Street things, decals, signs | 0.1 M | 0.1 M | 0.05 M | 0.05 M |

Each kind declares its counts per level as an export check (D14.5): each level at most 60 % of the one before; the median visible triangle ten pixels or more.

**Memory (the player's resident total under 6 GB on 16 GB unified; the harness reports peak, the scale test fails above).**

| Pool | Budget |
| --- | --- |
| Geometry resident (chunks in the streaming radius) | 1.0 GB |
| Place and history maps | 0.8 GB |
| Shell atlases (if painted; mips by distance) | 1.0 GB |
| Fields, ground, height | 0.2 GB |
| Library parts and material arrays | 1.0 GB |
| Chunk cache in RAM, second record or date resident for a comparison | 0.5 GB |
| People | 0.5 GB |
| Render targets at 1440p MSAA 4× | 0.3 GB |
| Engine, code, audio, UI | 0.7 GB |

**Disk per kilometre of street (both sides, about 250 houses):** history and place maps 4 to 18 MB at 4 to 8 cm (walked stone at 2 cm adds about 1 MB a flight); instance records about 30 MB; shell atlases 115 MB at 5 cm or 320 MB at 3 cm; chunks about 20 to 40 MB. So 0.2 to 0.4 GB a kilometre with painted shells, under 0.1 GB without; the 1989 centre's shipped cache about 1 GB. The scale test measures these with synthetic maps at both densities.

**Build time (worker time, C# in the player):** a 4 m chunk 10 to 50 ms; a house under 20 ms at test quality (Python is under 80 ms with Blender's overhead); a kilometre of street 1 to 5 s; a thirty-year jump across a district under 1 s of worker time, the first view's 20 to 50 things built behind the dated card. Final quality per house is unknown until House A.

**The authoring loop (pre-mortem):** a look change on one kind seen in under 3 minutes (one chunk regenerated, imported, one golden view compared); the gully's full sheet in under 10 minutes; a kind's full stage run skips every stage whose input hashes are unchanged. Timed on Wednesday; a loop over budget is fixed before the port goes on.

## 8. The light, time and world state (D7, D12)

| # | Decision | Reason | Status | Needed by |
| --- | --- | --- | --- | --- |
| D7.2 | The rule: nothing relies on temporal accumulation; MSAA 4× at native 1440p by default; FSR 1 the first fallback; STP only once every mover writes motion vectors | every mark must stay stable without history; golden views and hashes must repeat; hashed alpha and GTAO without TAA are measured | rule FIRM; the AA choice PROV: harness and motion sheets | the rule at 3.4 |
| D7.3 | One world state, owned once, hashed: fabric date (year, month), day of year, hour as the sun's position, weather, wind (climate and moving, one fetch), tide, latitude, longitude, time zone. The light's layers replay from it | four clocks in four studies; one record | FIRM | the date at 3.2; the rig at 1c |
| D7.4 | The shade's three lookups (sky radiance from a model, seen ground, seen town) in `OS_ShadeP` | the four debts share one cause | PROV: look test at 1c | the cheap lookups before more look judging |
| D7.5 | Lights from sockets in tiers (8 to 16 shadowed spots near, unshadowed at street, glow beyond); no shop or window a real light; spill from a tile-binned buffer; one socket definition for lamps and windows. `TownLights.cs`'s spot per shop goes | 403 lights in the heart against Forward+'s 256 a camera | rule FIRM; counts PROV: harness | socket schema before House A; steps 3 and 6 |
| D7.6 | No baked probes; reflection probes placed by the generator, a few relit a frame; far shadows and horizon angles from the height map | probes cannot follow a rebuilt town | FIRM | 1c |
| D7.7 | Occlusion on indirect light only: GTAO, multi-bounce with albedo, specular occlusion; none on the sun | light §2 | FIRM; cost on the harness | 1c |
| D7.8 | No runtime painterly filter; no boil on what stands; the style pass in the colour lookup; dither at the last write; lamps by spectrum; normalised specular; exposure from illuminance; HDR buffers, no lifted blacks (dark skin breaks first: Rule 8); a chart and debug views of the shade's terms, which share the `_OS_BAKE` mode | light §3 to §8; painted P8 | FIRM as rules | now |
| D12.1 | Lives written on change, in C# in the player; the past to 1989 may ship as a cache; Python writes them at 3.2 as the specification | follows the stage map | FIRM | 3.2 |
| D12.2 | The date as a shader global with the four clocks of D7.3 | time item 2 | FIRM | 3.2 |
| D12.3 | A part exists from making to removal; a comparison draws the shared instances plus the parts alive at each date; the chunk cache key includes the record hash and the life hash, so a second date is a second key resident for the frustum only | time item 4 | lifespans FIRM; memory PROV: the scale test (gap 13) | House A; step 4 |
| Counterfactual twin | A second record is a second record hash in the same world; the same key path gives two towns resident for the frustum. Nothing more is reserved | the paper playtests' ask; a cache keyed on the record already allows it | FIRM as a reservation; memory with D12.3 | later |
| Two-date frames | Two keys, one camera, one light: the chunks of both dates drawn with a movable mask in the post pass; one change at a time in date order from the change query's regions | the showing-time ideas | FIRM as a reservation | step 4 |
| D12.4 | `changes(scope, t0, t1)` as a schema now: cause, actor, provenance, precision, weight, parts and region per view, drift magnitudes; a plan diff at two years stands in for 1f | it feeds budgets, highlights, the why-probe, the journal, the readers' key and the shell rebake | FIRM | schema now; step 4 |
| D12.5 | The drawing is a function of (record, fabric date, light moment, weather, view, level), hashed; the watched-or-jumped test and the diff check | time items 1 and 7 | FIRM | the rule now |
| D12.6 | Scene state as instance overrides on their own clock, never in maps or the record; committed to the engine only when it matters; a fabric-only switch for judging | `CLAUDE.md`'s five kinds | FIRM as a default | LT2 |
| D12.7 | Works keep dated phases (hoarding, pit, scaffold) as fills of a works slot | time item 4 | FIRM, a slot now | lifespans at House A |
| D12.8 | The guard stays: condition never depends on whether anyone watched; the actor on every event keeps the player's mark possible; whether it is noticeable is Øystein's exploration | decided | none | none |

## 9. Materials, plants, land, motion, buildings, interface

**Materials (D4).**

| # | Decision | Reason | Status | Needed by |
| --- | --- | --- | --- | --- |
| D4.1 | Split by the shape of the cause: records and outlines (signs, posters, a removed shopfront's line, rust below a fixing) are dated mesh decals from one atlas per family, drawn by the host's stack and baked into the shell far off; water-borne stains are carriers in the water bake, down the flow path across parts, fading from the removal year; URP's Decal Projector only for transient scene state | decals stack and pick; carriers cross parts | decals FIRM; carriers PROV: the gully's handrail post as the first case | decals House A; carriers after the corner's wash |
| D4.2 | One material record in `packs/<pack>/materials/`: identity, pigment, grain script and seed, tooling, water profile, wear, growth affinity, paint failure, city bake, albedo range, porosity, smoothness, translucency, scatter, a curve per process, texel targets, an acoustic class (reserved). Families in a `Texture2DArray`; an editor step writes the Unity asset from the record and replaces `LT1Trees.Materials` and `LT1Stone`'s values | materials §1; gap 18 | FIRM | 3.3 |
| D4.3 | Coats as fills with their year; the shader reads the year against the date; up to eight a wall in a data texture by wall id | "years since" rebakes on every jump | FIRM | House A |
| D4.4 | A board-and-trim atlas, 4 by 1 m at 1 mm; boards stay geometry at L0 and L1; grain follows D6.4 | the low sun needs the relief | PROV: look test | House A |
| D4.5 | Hex-tiling for concrete, asphalt and ground; the Kuwahara city bake is the painted far town's test | M8 | PROV: look test at step 3 | step 3 |

**Plants (D9).** D9.1 opaque first, a rule now (no cards or shells near; cards only where few overlap, cut to their outline; opaque cores), FIRM, the birches re-fitted at 1e. D9.2 one placer with one presence law (present = potential(fields, facts, date) > rank(seed)) beside the layer law for continuous things, FIRM, step 3. D9.3 joint lines, growth faces, traps, climbable regions and keep-clear zones exported from the gully at 3.1, FIRM. D9.4 plants as records with keepers' calendars, schema now. D9.5 the birch's cost measured on the harness Tuesday, PROV. D9.6 wind-ready marks (bark from the undisplaced position in UV5, dithers from the card's UV, a motion-vector pass), FIRM before the wind. D9.7 growth stays offline; a change beside a tree applies as events; regrowth in play measured at step 7, PROV. D9.8 a deposit field per chunk, look test at step 3.

**Land (D8).** D8.2 natural ground as layers; made ground as dated acts applied in date order, and acts run in the player (the family game needs a new road), FIRM, 1d. D8.3 mesh terrain in 64 m chunks with breaklines and rings, not Unity Terrain, FIRM, 1d. D8.4 foot lines as breaklines and footprints exported from the gully at 3.1, FIRM. D8.5 natural stone as a kind, look test at 1d. D8.6 the ground on `OS_ShadeP` with few materials from fields; slow edges as mesh, fast as shader, PROV on the corner's years sheet. D8.7 water as opaque meshes with baked depth, Gerstner waves from wind and fetch, SSR first, look test at step 6.

**Motion and affordances (D10).** D10.1 one motion class per element (still, hinged, swinging, flexible, floating, emitting) with the anchor class derived and a card-or-skinned flag, FIRM, 3.1. D10.2 identity numbers in the contract now; the far mesh and archetypes by measurement at step 5 (the recognition test, crowds at 500 and 2,000), PROV. D10.3 as in section 5, FIRM. D10.4 affordances as dated sockets (treads, walking line, landings, handrails, sit, lean, stand, sills, shelter, grips) read at the date; the grey walker on the gully tests the contract, FIRM, export at 3.1. D10.5 every walked surface registers a walking line to the feet field, FIRM. D10.6 wind as one field, a pure function of position and absolute time, in the world state, FIRM, contract now. D10.7 every motion a function of the record and absolute time, cloth the one warm-started exception; a time-jump test, FIRM. D10.8 the gait seed in identity at birth, FIRM. D10.9 faces: both routes stay open (blend shapes kept on import), look test at step 5. D10.10 clips and rules as engine-neutral data, FIRM.

**Collision and navigation (gap 6), PROV: a short craft study before the grey walker; defaults now.** Each part level declares a `collision_role` (none, proxy, full); the chunk carries one merged collision proxy built from its parts' proxies at L1 detail (a tread's hollow of a few centimetres is below a walker's foot tolerance, so the collider reads the date only when the chunk rebuilds, never per frame). Walkable surfaces come from the affordance records (treads, landings, walking lines) and the ground chunk; a navigation mesh is built at runtime per 64 m cell from the collision proxies and rebuilt with the chunk. Reserved in the schemas now: `collision_role` on part levels, `walkable` on affordances, a collision section in the chunk format.

**Buildings, fronts and signs (D11).** D11.1 the window inside D3.1: opening never deleted, fills as a list, the surround its own fill, the dressing stack, the room by reference, FIRM, House A. D11.2 wall surfaces dated by region (profile, year, scope, corner type), FIRM, House A. D11.3 the room as a record with a box in mm, kind, household, year fitted, lamps; its box as instance data; the lit state live by the hour, never baked; it must be able to grow into geometry (the manager's clubhouse), FIRM, schema House A. D11.4 the sign as a record with its own events; street records as a coat stack, FIRM, House A; the reach of "English" to Øystein. D11.5 the ground floor's own grammar under a control layer, FIRM, House A. D11.6 the seeded mansard goes before 1f: a roll that claims a roof raise the record lacks breaks the facts rule; `eras.py`'s values move to `packs/<pack>/eras.json`, `stronger`'s multipliers go, archive values before step 2, FIRM. D11.7 glass by era with one normal per pane, one opaque window shader reading the room box, look test at step 2. D11.8 lit rooms from the household's day as rules, `derived` until engine #22, FIRM, step 2. D11.9 roof courses as geometry, odd tiles by index, a permissive straight skeleton for irregular hips, look test at House A.

**The interface (D13).** D13.1 as in sections 4 and 5: merged chunks pick through UV3's piece index and the chunk's table; kit instances through the user value; swarms through tile and seed; shells per triangle; people their own path; the spike (1 to 1.5 days) during the port with test 6 (the id at random screen points names the same record as a raycast against full meshes), PROV. D13.2 one shared highlight function comparing the hover and selected global ids: an even lift, no hue, no neighbour sampling; the focus a stencil in the post pass, FIRM, shaders at 3.4. D13.3 a scissored 64×64 id render round the cursor, read back two or three frames late, FIRM default, measured with the spike. D13.4 a label anchor and screen bound per record, a head anchor for people, a CPU list for the bubble snap, FIRM, House A. D13.5 the knowledge store as data per role (seen, heard, told, written, inferred, the record, unknown), built with the first game; provenance now, FIRM. D13.6 rule 10 narrowed: a name is a fact and may be shown; a reading of character is never labelled, FIRM.

## 10. Quality tools, process and what changes (D14, D16)

| # | Decision | Reason | Status | Needed by |
| --- | --- | --- | --- | --- |
| D14.1 | A strict review accepts a baseline while building; Øystein accepts milestone sheets | three baselines this week; `NOW.md` makes look and craft ours. Overrules P §6 and `measuring.md`'s rule | FIRM | 3.0 |
| D14.2 | Nothing generated is tracked: FBX, chunks, exported library meshes, tree timelines leave git and are rebuilt; hash manifests, part sources and the golden baselines stay. The working tree drops its 385 MB of FBX when the gully regenerates at 3.1; the 2.5 GB history is not rewritten now (section 13). `CLAUDE.md`'s LFS line changes to "generated binaries are rebuilt, not tracked; baselines in plain git until LFS is reachable" | LFS is unreachable from the cloud workspace; P12 | FIRM | before 3.1 |
| D14.3, D14.4 | The harness with its A/B switches (Resident Drawer, GPU occlusion, MSAA, the history path, forced levels, the sun's beams, shadow reach), peak memory reported; golden views and motion sheets at one sample a pixel; the swim test and shimmer index | planned; pre-mortem story 4 adds memory | FIRM | Monday |
| D14.5 | Export checks: budget per level, 60 % rule, median triangle ten pixels, fits never silent, the kit validator, plan validity, the licence list, the id test | P1, P13, K4, K5 | FIRM | from 3.1 |
| D14.6 | One fact-check framework: `trace_check`, act check, cut check, label check, superposition, the diff across dates, watched-or-jumped, time-jump | each with its first user | FIRM | from 3.2 |
| D14.7 | One expressive-range tool with counts per level and the repeat-finding check | K §4 | FIRM | the first library |
| Test matrix | kinds × levels × lights × views × dates × machines in `tools/matrix.json`; a subset runs on the daily player build; today 24 segments | pre-mortem | FIRM; grows per kind | Monday |
| Build pipeline | `tools/build_player.sh`: pack, libraries, cache and code to a macOS player; runs the checks and fails on them; a daily build on the Mac mini at a quiet hour | nothing builds a game today | FIRM; built the week after the port when a C# core exists; `tools/perf.sh` stands meanwhile | the week after the port |
| D1.12 | Only permissive code ships, listed in `LICENSES-shipped.md` and checked at build; `bpypolyskel` (GPL) offline only; meshoptimizer (MIT) ships; the Apache-2.0 skeleton for irregular hips | `where-generation-runs` §6 | FIRM | the first irregular roof; the list now |
| D16.1, D16.2 | Python this week; a fresh export of the gully and accepted golden views before 3.0 | the committed FBX is not what the generators build | FIRM | now |
| D16.4, D16.5 | Research gaps pass just before their steps; the pre-mortem on Tuesday reviews this document | | FIRM | Tuesday |

**Superseded statements (D16.3 plus the inventory):**
- `living-fabric.md`: "Life is computed offline per thing"; "the city tier bakes the life into the merged mesh's vertex data"; fields "redrawn by decade".
- `town-system.md`: "only the chunk a change touches is rebuilt offline".
- `kits-and-generation.md` §6: Unity "runs no generation".
- `building-system.md`: "The shader reads one number per coat: years since it was applied".
- `foundations.md`: the tier table with switch distances; "runs of parts merged (a flight, a wall, a house)" as the merge unit.
- `visual-direction.md`: the brush's one world size.
- `research/stone.md`: "Every piece its own seeded instance, so nothing repeats" (pending Øystein's reading).
- `CLAUDE.md`, Practical: "Large binary files (renders, FBX) go through Git LFS".
- `blender-generators` skill: parts as `.blend` files through LFS; `random.Random(seed)`; the 1 m grid; `kit_<family>_<variant>_<lod>` names; "wear, dirt and age set by Unity, not baked"; `blender/validate.py`; export to `Assets/Art/Kit/`; 2,000 triangles for LOD0.
- `unity-conventions` skill: `PlaceGrammar.cs` and `Code/Characters/`; "GPU instancing, static batching"; "one shared hash" (true again after 3.0); "Unity never decides" (Unity assembles and fits; it still never invents a fact).
- `docs/measuring.md`: "only Øystein accepts a baseline".
- `docs/plan.md`: `blender/kinds/`.
- `docs/engine-contract.md` and the notes: the word `engine` as a provenance value.

**What changes in existing work (D16.6):**
- *Stone (stairs, steps, walls):* facts move from `FLIGHTS` and `stair_facts.py` into a fixture record; `YEAR` stops being hard-coded; seeds to SplitMix64 on part ids; the monolith splits into the seven stages under `kinds/stair.json` and `kinds/wall.json` with one runner; the six UV channels become the place and history pages plus the layout of section 5; levels, 4 m chunks, a shell ribbon and caster proxies; materials as pack records. The five open faults of the stairs wait for the new foundations. Review findings, style and facts are kept, proven by the golden views.
- *Birches:* cut cards, opaque cores, real leaves near, wind-ready marks, their own levels to 200 m, then lobes; growth stays offline with the timeline cache keyed into the hash chain; `h01` and the simulator's `random.Random` move to the one hash (the timelines change once, by design, with a new baseline).
- *Houses:* the record migrates to slots and fills; the mansard goes; `eras.py` becomes pack data; House A is built by the generator with pins, then twelve from the same parts; the window and its surround are the first final part; the house builder is ported to C# before House A.
- *Kit props (lamp, bollard):* become library families with part definitions, levels and sockets; the unused seed goes.
- *Unity:* `StreetGround.cs`'s kerbs and flags move under the linear grammar as a kind; `LT1Stone`, `LT1Trees` and `LT1Heart`'s placement becomes the assembler reading records; `TownLights.cs` reads sockets; the shaders gain `_OS_BAKE`, the highlight compare, `OS_History`, and the Drawer's pragmas; the Resident Drawer is switched on and measured.
- *Skills and docs:* `blender-generators`, `unity-conventions`, `CLAUDE.md`'s docs table and Practical line, `foundations.md`'s tiers, `living-fabric.md`, `building-system.md`, `town-system.md`, `measuring.md`, and this architecture as `docs/building-blocks.md`.

## 11. A new city's pack (D15.5), FIRM

**A pack brings** (`packs/<city-year>/`): `metrics.json` (storeys, openings, rises, kerbs, thicknesses, grid, by era); `eras.json` (era shelves and dates; the shared timeline with the engine); `materials/` (records); part family definitions and their era content (the kits: each house type and era its own); `geology.json` and `climate.json` (rock kind, ice vector, foliation, joints, tide, fetch, splash height, wind climate, latitude and longitude); `lamps.json`; `lettering/` (letter styles by era); the record catalogue (posters, the paper); the field guide (plants by habitat); population and dress tables; `names.json` (every placeholder name in one file); `tooling.json` (pinned Blender and Unity versions); the curated start record and its pins.

**Carries over** (not in the pack): the schemas, the kinds, the stages and runner, the shaders and the shade, the shared systems (water, wear, growth, upkeep, light, detail by distance, the placer), the checks, the chunk format and cache, the interface. The first foreign-pack part is a data check only until step 10 (the producer's note in the pre-mortem).

**Scale (D15).** D15.1 PROV: the scale test's demand rate against build rate; default: ship the start date's cache for the heart, build on demand beyond it, the same code for both. D15.2 FIRM structure: a binary chunk keyed by the hash chain; the world on disk is the record plus the libraries; eviction LRU by distance under a byte cap from section 7; built the week after the port. D15.3 and D15.4 as section 7, PROV Tuesday. D15.6 people generated at runtime from identity numbers and cached by a hash of record, age step and outfit; costed at step 5.

## 12. The three example games

**A manager (a club or a band).** Nothing locks it out. A new stand or a converted loft is fitted geometry made in the player (section 1); crowds of thousands are far figures with their own identity numbers on shared meshes, which D6.4's reading permits and step 5 measures; weekly posters are decal records on a coat stack, not rebakes; the room record may grow into geometry (D11.3); the knowledge store is data per role; a stadium is a new kind file with its own metrics, not a stretched house. What keeps it open: kinds and metrics as data, the record admitting every kind, and the player-side assembler.

**An exploration game.** Nothing locks it out. Budgets and streaming are set per judging view but the levels switch by error in pixels anywhere, so eye level holds in any lane; 4 m chunks and 64 m streaming cells with a shipped cache fallback cover walking pace, and the scale test measures how fast the camera may rise; collision and navigation have a reserved role per part level and a chunk section, settled before the grey walker; journal entries point at slot and fill ids that survive rebuilds and years; night sees lamps in tiers with spill from a buffer; what the history budget hides stays findable through the card and the probe.

**A family across generations.** Nothing locks it out. Extensions, demolitions and rebuilds are fitted geometry in the player; thirty years of drift costs a uniform, and the discrete changes come from the change query as chunk rebuilds behind the dated card (under 1 s of worker time for a district, provisional); ground acts run in the player, so a new road or a filled garden is possible; a tree planted in play grows from a precomputed timeline or events until step 7 measures growth in play; seeds and ids are stable for a part's whole life; people are generated from identity numbers with parents in the record; the eras after 1989 are content, and nothing assumes a final year.

## 13. The gully port this week, in order, with the cut line

Re-estimated against these decisions. The register's studies put the full port at 16 to 22 Opus-days; the plan gives three. Each step ends in a commit and a pushed state.

| Step | What | Honest estimate | Status by Friday |
| --- | --- | --- | --- |
| 0a | Fresh export of today's gully and walls; golden views re-accepted by a strict review; the baseline | half a day | done |
| 0b | Seeds: one hash spec, `Hash.cs` matched to `hashing.py`, the vector file; `stone.py`, `wall.py`, `upkeep.py` on SplitMix64 over part ids; new baseline | 1 day | done |
| 1 | The schema files, the naming grammar, the layer and map registries, the change query, the world state; the house kind and one window's slot record written against the same schemas and validated, not built (pre-mortem story 3); `validate_record.py`; `migrate.py` with migration 001 | 1 to 1.5 days | done |
| 2 | Stone split into the seven stages as `kinds/stair.json` and one runner; facts from a fixture; the plan hasher and the hash chain; golden fixtures per stage; `diff_stage.py`; the geometry hash unchanged; the export carrying breaklines, joints, affordances and the motion class | 2 days | done or nearly |
| 3 | History as a function: rates, reset years and age offsets into the place and history pages at 2 cm, the date a global, `OS_History` in the shaders; the gully's A/B in grey light at eye level, FLIP within threshold; the years sheet shows jumps only at works | 2 to 3 days | **the cut line**: started, perhaps not accepted |
| 4 | Materials as pack records; the editor step that writes the Unity assets | 1 day | next week |
| 5 | Levels from the generator, 4 m chunks, the shell ribbon, caster proxies, the Drawer's pragmas and the highlight compare; the id test | 3 to 4 days | next week |
| 6 | The picking spike (1 to 1.5 days) and the grey walker (1 to 2 days) | | next week, with the C# core |
| 7 | Measure before and after at every judging view; the strict review; the proof sheet | 1 day | Friday, on whatever is honestly complete |

The steps add to 13.5 to 17.5 Opus-days for the whole port, and 6.5 to 8 through step 3 (corrected by the session from the table; the first draft said 7.5 to 10). The week has three. Friday's milestone is steps 0 to 2 reviewed, with step 3 as far as it has got and its A/B shown as is. The architecture, the tools and the scale test do not move. No stage is ported to C# this week; the only C# change is matching `Hash.cs` to the hash spec (step 0b).

## 14. Questions for Øystein

Only scope, play and permissions; each with a recommendation.

1. **The reach of "English" over proper names.** Signs and street text are English (decided). The fixtures still hold "Vik Jernvare" and streets with ø. *Recommendation:* English placeholders for every proper name too, until you name things yourself; every name lives in `packs/stavanger-1989/names.json` and nothing else refers to it; the lettering supports æ, ø and å from the start, so your names can be Norwegian later without a change anywhere else.
2. **"Nothing repeats" read at the grain of things.** Your words were about stairs. The architecture reads them as: things never repeat; a hand-made piece may repeat where no viewer can find it (a few metres apart, turned, re-weathered by its own place); only what wear or a hand shaped for one spot is unique. The numbers: one stair with its walls today is 816,000 triangles and 36 MB; a kilometre of wall is about 5 million triangles and 200 MB, against about 50,000 instance records and 30 MB of maps from libraries. *Recommendation:* that reading, checked by a repeat-finding test on the golden views and a look test of a stretched library stone at eye level, both of which you see.
3. **The painted far town's look test: when.** The shell level is built either way; the test (5 to 7 days) decides only whether it is painted. *Recommendation:* run it after the gully port and before House A's far level, so the house kit's far level is built once, not twice; defer it if the port runs over.
4. **The repository's history.** The working tree drops its generated FBX now (385 MB), but the 2.5 GB of history holds the old ones. Rewriting history is a one-way change that breaks every clone, including the cloud workspace's. *Recommendation:* not now; revisit when LT1 merges to main, with LFS installed first if you want it.
