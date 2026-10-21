# Pre-mortem: the building blocks, seen from April 2027

Written on Fable 5.1 on 21 October 2026, before the architecture, from the plan, the register and the harness baseline; it builds on `pre-mortem.md`. It is April 2027 and the architecture failed in one of these ways, ranked.

## 1. The frame was bound by pixels; the architecture optimised triangles

**What failed.** The port cut the gully's triangles by 80% and the frame fell by a sixth. D6 spent weeks on levels, chunks and proxies while the cost sat in the shaders: sky, fog lights, SSR, occlusion, MSAA.

**Earliest sign.** In the baseline already: the blue hour draws 5.5 million triangles, 76 draws, no shadow casters, and still takes 25 to 35 ms, a floor of 25 ms before any geometry, against 16.7.

**The decision.** D6.5 budgets triangles and draws; no pass has a millisecond cost.

**Cheapest test today.** A harness run on an empty scene with sky, lights and post alone, then each pass toggled; a millisecond budget per pass beside D6.5. Over 8 ms, the shaders get a port stage.

## 2. The contract lived in prose; Python and C# read it differently

**What failed.** Records, stages and ids were described in sentences. The Python port read them one way, the C# core another. Mesh parity (D2.3) failed and nobody could say which was right.

**Earliest sign.** The first C# chunk places the right pieces with the wrong seeds: a sort order, a float formatted differently.

**The decision.** D1.6 left "unknown"; D1.2's single source a week after the port.

**Cheapest rule today.** Schemas as files: kind, part, plan, slot, interval, chunk, hash chain. Each stage writes a golden fixture on the gully; parity is tested at every stage boundary, in data, before any mesh. Decide D1.6 Monday.

## 3. The gully proved the framework; the house did not fit it

**What failed.** The gully has no plan stage, slots, fills, coats, library parts or fitting to a footprint. It exercised maps and levels, not the record. House A found a runner that assumed geometry first and a kind file that was stone's renamed.

**Earliest sign.** The stone kind file holds fields no other kind uses, or the runner branches on the kind's name.

**The decision.** D1.4 and D1.5 settled on one kind; D3.1, D1.9 and D1.11 waited.

**Cheapest test today.** Monday, write the house's kind definition and one window's slot record against the same schemas, validated, not built: two kinds on paper before one in code.

## 4. Memory was never budgeted; the 16 GB floor was found by crashing

**What failed.** The corner used 231 MB, so memory never had a line. Then unique close chunks (D6.4 c), maps at 4 to 280 MB a kilometre (D5.3), two resident versions for a comparison (D12.3) and a cache without eviction (D15.2) met a base M4 whose 16 GB the GPU shares.

**Earliest sign.** The scale test reports frame time and disk, not peak memory.

**The decision.** D15.3 gives disk per kilometre and no memory ceiling.

**Cheapest rule today.** A memory sheet: MB per kilometre for geometry, maps, fields and cache, under about 6 GB on 16 GB unified memory; the harness reports peak memory, the scale test fails over it.

## 5. History as a function made jumps free and works a stall

**What failed.** With inputs in the maps and the date a global (D5.1 b), a jump cost a uniform. But every act that changes a rate or reset (a repair, a gutter, a coat) rebuilt a chunk's maps in the player, which took longer than a frame; the family game hitched on every works year.

**Earliest sign.** A jump across a works year on the gully takes over 100 ms in the player.

**The decision.** D1.1 (b) moves bakes into the player; D5.4 makes rate changes rebuilds; the scale test never times a map bake.

**Cheapest test today.** One 1024 by 512 chunk map baked and compressed in the scale test's player, timed; an invalidation table in the chunk format: which maps each act dirties.

## 6. Ids survived merging and not regeneration

**What failed.** Semantic part paths (D3.2) carried a piece index. A fitting rule changed, a run split into more pieces, and every id below the slot shifted while the geometry hash barely moved. Pins (D1.10), the journal and the pick table (D13.1) pointed at the wrong stones.

**Earliest sign.** After plan 3.1 the piece ids change while the geometry hash does not.

**The decision.** D3.2 promises stability for every id; D1.10 learns about pins "at the first bump".

**Cheapest rule today.** Promise stability down to slot and fill; pieces in a fill are derived indices. An id test: bump the rules version, regenerate, count ids lost and born, fail above zero.

## What a lead technical artist would say is missing

- **Record versioning and migration.** Every record file, the 1989 town made once, pins and the engine's run need a `schema_version`, and the pack needs migrations as code run on every fixture (D3.1 mentions one), or the curated town dies at the first rule change.
- **The source-of-truth split, per stage.** A table: stage, source language, reference, the date it flips; Python frozen per kind at its port.
- **Determinism tooling.** Stage hashes only say "differs": add a diff by stable id, a two-machine run, and Blender and Unity versions pinned in the pack.
- **The authoring loop time.** Today a sheet is one 67 s Blender run; after stages, bakes, levels, checks, import and golden views it could be twenty minutes. Budget it (a look change seen in under three minutes), let the hash chain (D2.4) skip unchanged stages, time it Wednesday.
- **A test matrix.** Kinds by levels, lights, views, dates and machines, a subset run on a daily player build; today, 24 segments.
- **Content validation at the record level.** A validator that fails plans: a fill outside its slot, dates out of order, a missing actor, a family outside its era. D14.5 and D14.6 check only meshes.
- **A naming grammar before the first kind file.** Ids, part paths, kind, material, chunk, map and field names on one page; stone sets the pattern.
- **Retiring a part.** A family's lifecycle (draft, judged, in library, deprecated, removed) and what a record referencing a removed part draws: a tombstone or a kept last mesh, or replacement breaks the town.
- **The build pipeline.** One script that makes a player from pack, libraries, cache and code and fails on D14.5's checks. `tools/perf.sh` builds a player in passing; nothing builds a game.
