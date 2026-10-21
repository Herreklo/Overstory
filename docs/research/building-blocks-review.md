<!-- Strict review of docs/building-blocks.md by a fresh Fable 5.1 agent, 21 October 2026. Fixes applied in the commit that follows. -->
# Strict review: docs/building-blocks.md

Reviewer: lead technical artist / technical director, cold read. Read: the document, the register, CLAUDE.md, NOW.md Decided, plan.md 1 to 125. Code checked: `blender/resolver/hashing.py` (the hash spec as stated is correct: SplitMix64 finaliser, FNV-1a, start value `0x2545F4914F6CDD1D`, `unit = (h>>11)/2^53`), FBX total (385 MB, correct). The decisions doc was opened only after the draft, to sort drafting slips from real gaps; each finding says which.

**Verdict: ready after fixes.** The shape is right: stages, contracts as files, inputs not outputs in the maps, ids down to fill, a provisional line for every number. Nothing locks out the three games. The must-fixes are a budget that does not add as written, map channels that do not fit their pages, one decided item read against its wording, and the shell path stated two ways. A team can build on it tomorrow once those four are fixed; the should-fixes are what a Wednesday builder will otherwise decide on their own.

## Must fix

**1. The frame budget does not add up as written.** Budgets, "Frame by pass". "GTAO, SSR and water | 1.0 each" reads as 3.0 ms. The column then sums to 15.0 used, 17.7 with the reserve, over 16.7. The decisions doc has two rows (GTAO 1.0; SSR and water 1.0), which sum to 14.0. Drafting slip. Fix: restore the two rows and print the column's sum under the table.

**2. The map pages do not hold the channels the text puts in them.** What a part carries, the registry. P0 is RGBA8 with feet, water held, sky seen, ground seen; the same section says the light's openness and weather exposure "live in the place map", and there is no channel for them (D7.1 names four light inputs plus the bent normal). H2 names five layers (wash, deposit, splash, carrier, contact) for four channels. "Own occlusion" is called an intrinsic channel in the mesh, and the vertex table has no slot for it. Same in the decisions doc, so a real gap. Fix: add a channel column to the registry (P0 four named; a P1 for openness, weather exposure and two reserved; H2 as two pages or four layers), and put own occlusion in UV4.w, which is "spare".

**3. Repetition is read against a decided item.** Levels, "Repetition"; Open until measured. NOW.md Decided: "Repetition only where things really were mass-produced ... bricks, roof tiles, factory windows and doors, catalogue houses, and setts ... Everything made by hand for one place is its own." The document says "hand-made ones from large [libraries]" and lets pieces repeat where no viewer can find them, then asks Øystein for a reading NOW.md already gives at the grain of pieces. The decisions doc took "nothing repeats unless factory-made" as the only decided wording and missed the second item; a real gap. Fix: make the default the decided wording (libraries for NOW.md's list; hand-made for one place is a unique fitted piece, costing build time and memory, not disk, per D6.4), and narrow the question to Øystein to the one case the wording leaves open: hand-split wall stones not shaped for their spot, with the scale test's memory number beside it.

**4. The shell's source of history is stated two ways.** In short 3 says the far shell alone caches an output bake. Levels says shells and blocks are built either way and the test decides only whether the atlas is painted. Budgets then says disk is "under 0.1 GB without" painted shells and memory lists "Shell atlases (if painted)", which both assume no atlas when unpainted. But a 32 m shell has nothing else to read: chunk maps are per 4 m chunk and the shell's only UV is "atlas UV". The decisions doc is clear that the atlas exists in both arms (painted or plain). Drafting slip. Fix: say every shell carries its atlas (index, light inputs, albedo and normal at the date), painted or plain; the look test decides the painting only; disk and memory carry the atlas in both arms.

## Should fix

**5. No tangent frame.** Vertex layout. The normal is SNorm16×4 with its fourth component unnamed; BC5 bent normal, L2 "relief in the maps' normal" and the shell's normal atlas all need a basis, and none is stated. Real gap. Fix: name it: the tangent derived in the shader from UV1's derivatives (fine for soft relief), or the normal's w as a sign with a per-piece tangent in the facts table; say which, and which levels use which.

**6. The piece index and the pick index disagree, and the split is unmarked.** Records (pick index 12 bits chunk or cell, 20 bits piece) against UV3 (piece index UNorm16, 65,536). Also UNorm16 is a normalised format used as an integer; use `UInt16`/`UInt32`. The 12-bit field (4,096 resident units) is stated firm while 4 m chunks, 32 m cells and 128 m blocks all compete for it. Fix: a small per-level table (bits for unit, bits for piece or instance, format), marked provisional, settled by the picking spike.

**7. The shell layout is ambiguous.** "Shells carry 28: position, normal, atlas UV, and per triangle the thing index, part slot and material class in UV1 and UV3." UV1 is the atlas address in the main table, and three ids go into two UNorm16 channels. Same wording in the decisions doc. Fix: its own four-row table (Position 12, Normal 8, UV1 atlas 4, UV3 thing index and packed slot or class 4) with formats.

**8. CLAUDE.md's "does not invent their geometry" is changed but not listed as superseded.** D1.3 says the rule's wording changes for fitted parts (the judged thing is the function and its sheet). The superseded table lists only CLAUDE.md's LFS line and the docs table. Neither doc lists it; real omission. Fix: add the row with the new wording: "a fixed part is a judged mesh; a fitted part is a judged function; the generator places only judged parts and never invents one".

**9. The decided "concentrate history" item has no mechanism.** NOW.md and plan.md item 4: a shared weathering bake on every surface, the full layers where a view's stories are, any layer addable later. The document has the registry and reserved H2, but says nothing on which chunks get the full layers or how. Fix: one paragraph: P0 and H1 are the shared base on every chunk; H2 pages are allocated per chunk by the history budget per view (the change query's weight), and a chunk without stories carries none.

**10. Texel size when a chunk mixes materials.** What a part carries: 2 cm walked stone, 4 cm walls. The gully's 4 m chunk holds both, and Wednesday's builder must choose. Not stated anywhere. Fix: a rule: a chunk's pages are at the finest texel any part in it needs, or one page per material class; say which and its cost.

**11. Disk per kilometre counts two pages; the registry has four or five.** Budgets. "Maps 4 to 18 MB at 4 to 8 cm" was derived for about 2 bytes a texel; P0, H1, H2, bent normal and deposits at BC7/BC5 (1 byte a texel each) roughly double it. Fix: recompute from the registry by page, and say which pages ship in the cache and which are rebuilt on load.

**12. No per-frame streaming budget.** Budgets give worker ms per chunk and nothing for the main thread or GPU uploads: mesh and map uploads, BC compression, and GameObject and MeshRenderer churn (the Resident Drawer needs one renderer per 4 m chunk). This is a lead TA's first hitch question and the exploration game's fast camera rise lives here. Real gap. Fix: three provisional lines: main-thread ms a frame for swaps, chunks and MB uploaded a frame, renderers resident per streaming radius, settled by the scale test.

**13. The hash chain misses the code that bakes.** Contracts. `rulesetVersion` names kind files and part functions; a change to `OS_History`, a layer curve or the shell bake would leave cached bakes and atlases valid. Fix: add `bakeVersion` (the history include and bake code) above the bake hash.

**14. Float precision for a bigger city.** Positions are Float32; past about 16 km from origin the unit of precision passes 1 mm, and marks and shadows jitter. The document promises to hold for a metropolis and never says where the origin is. Fix: state vertices are chunk-local, chunks placed from the integer plan, and the camera origin rebased per 64 m chunk; or state the world stays under 8 km and the rule that reopens it.

**15. Seeds rule 2 reads two ways.** "Choices use only integers, the four operations and square root." A builder may ban sin and cos from geometry. The register's clause was lost: a transcendental may place a vertex, never choose. Fix: restore the clause.

**16. The L2 merge unit reads two ways.** Levels table: "runs of 3 to 5 m in the 32 m cell"; Units: "32 m cells at L2 and L3". Fix: say which is the mesh and which is the rebuild unit at L2.

**17. Conflict 28 is dropped.** Stepped or smooth motion for flags and laundry (register §4, 28) appears nowhere. Fix: a row in Open until measured, default stepped per `visual-direction.md`, settled by a motion sheet.

**18. Two contract fields from the register are missing.** Section 3: every record carries keeper and care; the part definition carries each procedural mark's smallest feature (which sizes the texel). `record.schema.json` and `part.schema.json` list neither. Fix: add both.

**19. The painted-town's cost comparison hides the unpainted arm's cost.** "18 to 20 days against 35 to 40 for conventional far levels." Since shells and blocks are built either way, the real comparison is painting (the Kuwahara bake and direction map) against plain, a few days. Fix: state the painted arm's own cost, or drop the study's comparison.

## Could fix

**20. Shadows are silent on trees and movers.** D6.8 says hulls and cores cast; the document says only L2 and proxies cast, nothing on trees, people, laundry or boats. Fix: one line each.

**21. `eras.json` "shared with the engine".** The engine assumes no country and is never changed from here. Fix: "the same era ids the engine's export uses", or an entry in `engine-requests.md`.

**22. Rejected alternatives with reasons remain** ("'Years since' would rebake on every jump"; "A dozen types do not justify code generation"; Unity Terrain's faults). Doc rule: current design only. Fix: cut the reasons; they live in the decisions doc.

**23. Golden baselines in plain git.** Fifteen frames are 44 MB (`measuring.md`); per kind, light, view and accepted baseline this grows a 2.2 GB repository fast. Fix: keep one current baseline per kind in git, older ones as hashes, or a cap.

**24. SSR is budgeted and water says "SSR first"; URP has no stock SSR as far as this reviewer knows.** Fix: confirm, and if ours, name it as a renderer feature to write and cost it.

**25. Picking and casting for "moving and lit things"** (lamps, boats, laundry) are not stated. Fix: fold into 6 and 20.

Counts: must fix 4, should fix 15, could fix 6.
