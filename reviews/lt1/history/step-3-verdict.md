# Step 3: pre-mortem and decisions

Fable 5.1, 22 October, on the packet.

## Pre-mortem: why it was dropped

1. **The sample tax.** The quad costs 0.17 ms a screen per page sampled (0.52/3, BC7). Every family read P0, P1, H1, story pages and the bent normal: five or six samples an opaque pixel, 1 ms a screen against S2's 0.5. The bound was per screen; the quad was the sampler's easiest case (magnified, one slice, coherent). *Sign:* R2's quad fails by two to three times.

2. **Two bakers.** Step 3 bakes pages in Blender; `maps.json` says the player bakes them. The step-5 HLSL baker disagreed at chart borders; step 3's A/B proved nothing about what ships. *Sign:* the encoder line reads "offline: none" while R3 writes one, with no golden page hash to match.

3. **Rebakes crept back until the function was a rebake with extra steps.** Care in H1.B meant every care change rebaked; 1946's decline needed "a decline or a jump". *Sign:* R1's "a care change triggers a rebake", accepted without asking whether the shader could apply care (decision 4).

4. **Blocks and mips at distance.** BC7 erred four times R0's bound; mip-2 blocks straddled 4-texel charts; borders shimmered in motion; the A/B passed only in RGBA8, so RGBA8 shipped and texels coarsened. *Sign:* R2's mip-2 error, the page's error deferred past the packer.

**A lead technical artist would say we lack:** a read budget per family (samples a pixel, not ms a screen); one bake function for editor and player, with golden page hashes; a page debug view and a date scrub before the port; chart borders judged in motion; a measurement that resolves 0.5 ms, which the corner (16 % spread) cannot. The order is right; the cost rung had the wrong bound.

## Decisions

1. **Decided:** one drive per texel per layer, the layer's form saying what it scales: amplitude × curve (polish, moss), rate × curve (lichen); the clock chosen per texel by a reach; speed and care per thing. Rate-only misses by 70 to 111/255 across dates; this is exact to 0.5/255. Changed by: a layer varying in two quantities per texel, which takes an H2 channel, not a second law.

2. **Decided:** age offsets per piece, whole years in the piece table; none per texel; H1.A freed. R1 found none needed. Changed by: an onset varying within a piece, a drive of its own.

3. **Decided:** H1 = R polish amplitude (also the dish's share), G lichen rate, B moss amplitude *without care* (see 4), A bed reach, binary, read at 0.5 (a threshold tolerates BC error); P0.G static water; held water from H1.R, the wear rate and the placed year. The dish tied to polish is a slate rule, named in `layers.json`. Changed by: a material that dishes without polishing.

4. **Measure first (an hour, no 2a):** R1 scaled the *clipped* amplitude by care: 39/255 on the ~3,000 clipped vertices, the rest exact. Store the unclipped drive, damp × (1 − 0.85·traffic); apply (1.15 − 0.75·care) in the shader; clip after. Expected ≤0.6/255 at every build at its own care. Then care is a per-thing uniform (D5.5), a care change costs a uniform, 1946's decline falls out, and H1 rebakes only for geometry, a rate or a reach. Changed by: the rerun failing; then R1's rebake stands.

5. **Decided:** H1 baked on each piece as laid: the page must hold between events, and polish and lichen stay on a sinking stone. The feet band is a place effect: if the target frame wants it, it comes from P0's water at the settled position, rebaked on geometry. 2a makes the change; Øystein judges it against the target frame, not the old build; R5's A is that build. Changed by: R5 showing the feet dead; then the band moves to P0.G.

6. **Decided:** 32 bytes on disk, 16 on the GPU, resets as year × 16 + month from the pack's first year. Name the GPU's four u16 reset slots now: placed, disturbed, cleaned, reserved; bare = placed − age brought; lifted a flag. Cleaning resets lichen and moss (`layers.json`). Changed by: a kind needing a fifth clock.

7. **Measure first (one harness run):** the quad at half scale; with two pages, not three; with UV tiled ×4 to sample minified and trilinear, as the street stop will. Decided now: the 0.25 bound assumed overdraw 2; the port builds for depth priming (S1), so S2's line is 0.5 ms a screen at overdraw 1, budgeted at 0.17 ms a sample. A family reads only its pages: the stone reads P0 and H1, not P1, about 0.35 ms; story pages count against D5.9. Per-pixel history does not fail S2; RGBA8 does. Not reopened: vertex history at distance (D5.2) or half precision; the cost is sampling. Changed by: the minified run over 0.25 ms a sample; then texels coarsen (S3) before the design does.

8. **Decided:** a 16-texel chart grid, charts per run, from R3: the packer is hardest to change; runs make it cheap. Format per page from the real page's BC7 error at R3's end, before R4 (none exists earlier): per channel, mips 0 to 2, 99th ≤2/255; a failing pair goes BC5 and costs a sample. No grain in pages. Changed by: every channel over the line; then H1 is two BC5 pages.

9. **Decided:** R3 goes ahead after 4's rerun; the cost run gates R4, not R3.

## The brief's changes

- **R1b**: the care rerun, before R3. **R2b**: the three quad arms, BC7 and RGBA8.
- **R3:** 16-texel grid; H1.B without care; accept adds the real page's BC7 error per channel and mip, a page debug view, a golden page hash.
- **R4:** care a per-thing value (a global now); the stone samples P0 and H1 only. **R5:** A is 2a's as-laid build; RGBA8, then R3's format.
- **R6:** the moss jump at a care change equals the old code's within 1/255 (not continuity); a motion sheet across chart borders at mips 1 and 2.
- **R7:** 0.5 ms a screen at overdraw 1, from the quad with real pages and law, scaled by the stone's pixel share. A stripping rule before any new `multi_compile` arm.
- **Cut line for Friday:** R1b, R2b and the decisions in docs and schemas need no 2a. With 2a by Thursday morning: R3, R4, R5 at eye-foot and eye-on in RGBA8. R6, R7 and BC7 next week.

## For an Opus agent: docs and schemas

- Decisions: D5.1 (drive × curve; clocks per piece; care and speed per thing); D5.4 (a care change is a uniform, pending R1b); new D5.10 (the per-sample budget); S2 (0.5 at overdraw 1; the 0.25 bound withdrawn).
- `maps.json`: h1 and p0 as fit.md (e) minus "a care change"; a `charts` block (per run, 16-texel grid, 2-texel padding, 3 mips); the encoder line.
- `layers.json`: `describes`; per layer `law` {form, clock, curve, delay}; moss `careFactor`; the hollow a derived layer; h1.a the bed reach; `readers` per family.
- `interval.schema.json`: the description; optional `reach`. `chunk-format.md` §4: the 32-byte table; the 16-byte GPU entry, four named reset slots. `channels.json`: uv4.y; uv5.
- `measuring.md`, `systems.md`, `building-blocks.md` ("Open until measured").
