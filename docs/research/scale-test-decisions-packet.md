# The scale test's changes: the decision packet

For the decision-maker (Fable 5.1), 22 October. Sources: `docs/research/scale-test.md` (in full) and `docs/measuring.md`, The pass budget. Commit `7962e2e` already wrote into `docs/building-blocks.md` what only settles open items: rebake numbers (GPU compression was already the rule), memory by footprint (2.6 GB), Burst for every loop in play, streaming reads on workers, the heart shipped and near levels on demand, hand-split stones kept their own, ground rings. Four changes below alter decided rules. Arithmetic marked *mine* is derived from the study's figures.

## A. Anti-aliasing

**Numbers.** MSAA 4× costs 4.9, 6.5 and 5.4 ms at the street stop (drizzle, low sun, blue hour), 3.4 to 6.5 across views, 1.4 to 1.8 on an empty frame. At a quarter of the pixels it still costs 3.3: it is paid at triangle edges. In Unity 6, MSAA forces depth priming off, and 85 to 90 % of the opaque pass is the shaders' own work.

**Current rule** (Light; D7.2): "Nothing relies on temporal accumulation … MSAA 4× at native 1440p, FSR 1 as fallback, STP only once every mover writes motion vectors (*provisional*)." Budget "MSAA 4× resolve 0.5"; memory "Render targets, MSAA 4× 0.3".

**Recommendation.** Keep the rule. The default built on becomes SMAA at native 1440p with depth priming on; MSAA 2× and 4× stay harness arms. The line becomes "Anti-aliasing 0.8". The choice is made by the motion sheets' shimmer measure and the golden views at 3.4, with the dithered cross-fade judged under the same filter. Shaders do not rely on alpha-to-coverage.

**Port.** Step 3's A/B renders both arms under one filter. Golden baselines are re-accepted once if the filter changes. Step 5 judges the cross-fade under it.

## B. The opaque budget belongs to the shaders

**Numbers.** The corner's 2.74 M triangles in 20 draws: 14.5 ms in their shaders, 1.9 ms flat unlit. About 12.5 ms is the shaders' work, and 10.3 ms scales with pixels. Every fragment runs a 12-step haze march, the first suspect, not yet measured alone. In the district, shells alone cost 15 ms at the street stop with 1 M triangles. Triangles still matter at scale: L0 for the whole core adds 20 ms at the city camera.

**Current rule** (Budgets; §7): "Opaque geometry, L0 to L4 | 5.0 | the triangle budget below". In short 5: "shaders are budgeted and A/B'd before triangles are ported". Rule: "a pass over twice its budget … gets a fix stage before any triangle work".

**Recommendation.** The 5.0 ms opaque line is the shaders' per-pixel cost, split by shader family. Each family's share is its cost over flat on the harness. The haze leaves the per-fragment path (a low-resolution volume or the vertex), A/B'd. `OS_History` gets its own line, measured in step 3. The triangle ceilings stay, for shadows, edges, memory and L0's reach. Take the pass budget's proposed table (full-screen passes 0.4, reserve 2.0).

**Port.** Step 1: `kind.schema.json`'s budgets gain a per-pixel shader line. Step 3: the A/B also times history on against off, flat, at the street stop; pages are sampled once a fragment each. Every measured pass but the sky is over twice its line, so by the standing rule the pass fixes precede step 5's triangle work.

## C. History map texel by face

**Numbers.** A house's envelope is 444 m², not the 56 m² street front the disk line assumed. With every face at 4 cm: 1.7 MB a house, 425 MB a km of street, and 1.45 GB resident in the 300 m radius (850 houses), against the 0.8 GB pool. At 8 cm: 0.43 MB and 0.36 GB.

**Current rule** (What a part carries; D5.3, PROV on the scale test): "A part's texel comes from its material's target and its marks' smallest feature: 2 cm walked stone, 4 cm walls and trims, 8 cm roofs and ground." Disk: "13 to 51 MB at 8 to 4 cm" over 14,000 m² a km. Pool: "the four base pages on every resident chunk".

**Recommendation.**
- A surface's texel is the coarser of two things: its marks' smallest feature, and its face class from the plan. The street front and the ground floor take the material's texel; sides and backs 8 cm; roofs 16 cm. Maps hold rates, which vary slowly; fine marks come from noise in UV2.
- Pages are resident only within the reach of the levels that read them (L0 to L2, about 80 m); shells read their atlas.
- *Mine:* 0.3 to 0.6 MB a house, 77 to 147 MB a km, 0.26 to 0.50 GB over 850 houses; within 80 m, about 60 houses.
- Judged on the years sheet at 12 m and the high view, where roofs show.

**Port.** Step 1: `maps.json`'s texel column becomes per face class; surface-region slots (`bld-101/sf-n`) carry the face class; `part.schema.json` keeps the smallest feature. Step 3: the gully's walked stone stays at 2 cm; the packer already takes a texel per rectangle.

## D. Units, files and what ships

**Numbers.** A stair's 4 m holds 100,000 triangles at final quality; a test-quality house's 4 m holds about 560 (34 KB). Each file costs 0.28 ms on the main thread. A jump needs 148 L3 cells and 484 L4 blocks; the city pan asks for 90 cells and 58 blocks a second. Coarse geometry is small: shells 1.6 MB a km², records 0.6 MB a km². The 2 m ground is 37 MB a km² before its rings.

**Current rules.** "4 m draw-and-rebuild chunks at L0 and L1" (D6.3, sizes PROV on the scale test); maps' "unit is the draw chunk"; the Drawer "holds one per 4 m chunk and level"; D15.2 FIRM "the world on disk is the record plus the libraries".

**Recommendation.**
- The rebuild unit and the hash key stay the 4 m chunk. The draw unit and its map pages become a 16 m group of 4 m chunks, re-merged on rebuild as L2 re-merges its cell.
- Files hold many units: one file per 128 m block for its records, shells, L4 and ground; near levels are cached per 64 m chunk.
- City-wide, the records, the libraries and the coarse geometry ship.
- Shell atlases do not ship city-wide. *Mine:* at 444 m² a house and 5 cm, an atlas is about 340 MB a km of street, not the line's 115. They bake on demand on the GPU, and L4's smallest mips may ship.

**Port.** Step 1: `chunk-format.md` becomes a container: a header and an index of units by id, level, hash key, offset and length. `naming.md` names groups and blocks. The pick index's unit slot is the draw group. Step 5 merges 4 m chunks into groups.

## What I ask

For each of A to D: accept, amend, or reject, with a reason in one or two sentences. Then name what a lead technical artist would say is still missing before step 1, the schema files. Candidates I see: the shell atlases' bake cost at the camera's demand; a cold-read rate; final-quality cost (House A); page streaming by mip. Then name anything that needs Øystein: scope, play or permissions only. Answer in under 600 words.
