# What port steps 4 and 5 must leave room for

Read this before step 4 opens. It comes from the plan review of 22 October: its inventory (`docs/research/plan-review-2026-10-22.md`, The inventory) and the house-front research (`docs/research/house-fronts.md`, cited as HF n).

## The rule (Fable, the plan review)

Steps 4 and 5 leave room for the needs below, but build nothing for houses, trees or land. Each step is done only when three written records validate against its formats. They are written and checked, not built, as step 1 did for one window's slot record:
1. a House A front: a coat stack, a glazed window, a painted sign;
2. a birch chunk;
3. a 64 m land chunk with water faces.

A format changes only where a written record fails to fit it. No field is added for a client that has no record.

## The needs stone alone would not reveal

Tags: **M4** is step 4 (materials as pack records), **L5** is step 5 (levels, chunks, the shell, casters, pick ids), and **HP** is the history pages.

1. **Coatings as a kind of material (M4).** A material is either a substrate or a coating. A coating carries its binder, film, failure modes and adhesion by pair. Raised by houses, sea houses' tar, render and limewash, iron and signs. Source: HF 1.
2. **The visible coat's year as a clock per texel (HP).** This is the fifth clock D5.4 names. There is no coat layer in `layers.json` and none in `kinds/house.json:57`. Source: HF 5 and 6.
3. **The coat record and its way to the GPU (M4, L5).** It holds scope, preparation, film and mask, and collapses past eight coats. A replaced board needs its own coat list, but D4.3 keys coats by wall id. The 16-byte GPU piece entry is full (`chunk-format.md:112–126`). Source: HF 3 and 7.
4. **Record fields beyond wear (M4):**
   - pigment drift with the years (cement, paint);
   - seasonal albedo and translucency (leaves, ground);
   - emission and spectrum (lamps, lit rooms);
   - glass by era;
   - the tiling mode;
   - timber by source and working.
5. **Atlases hold shape, not stuff (M4).** The trim atlas holds relief only, keyed by profile. Grain and pigment come from the record. Source: HF 2.
6. **Thin and repeating features (L5).**
   - They need a second level-switch rule, and band-limited patterns drawn from their facts (board courses, pane grids; HF 11 and 12).
   - Long runs (handrails, gutters, wires) have no rule for crossing a chunk cut, and they break the ten-pixel triangle rule (`building-blocks.md:267`).
7. **Charts in the wall's plane for clad walls (L5, HP).** Houses may need unwrapping. Sources: HF 10; `history-pages.md:77`.
8. **Fine shadows from the shader, and casters that must stay (L5).** The casters that stay are eaves, water boards, porches and chimneys, and the trees' cores and lobes. Sources: HF 13 and 14.
9. **Chunk sections the stone lacks (L5):** kit instances, decals, light sockets and room boxes (`chunk-format.md:92`; `building-blocks.md:310, 329, 356`).
10. **Library parts with history (L5).** Each instance needs a page address and a stretch, or its copies are merged into L0 and L1. Source: HF 16.
11. **Swarms carry dates (L5).**
    - Setts, tufts and litter need a reset year and a page address (`channels.json:54`, against `building-blocks.md:167`).
    - Tufts are drawn by compute and indirect draws (`ground-cover-and-plants.md:249`).
12. **Pick codes (L5, the id test).** Swarms, people, decals and coats have none, and the 2-bit path is full (`channels.json:46`; HF 18). The blockout people of 1g meet this first.
13. **Land and water units (L5, HP):**
    - there is no merge unit for the 64 m land chunk (`kind.schema.json:127`);
    - faces of ground alone have no page group (`maps.json:6`);
    - water and soffits are not face classes (`maps.json:14–21`);
    - the tide follows the hour.
14. **The shell (L5).**
    - It needs a top-coat mask, or each repaint rebakes a street (`painted-far-town.md:113`; HF 17).
    - Inset openings carry their slot in uv3 (HF 15).
    - Lettering must survive the shell's texel.
15. **Readers and laws for each family (HP).**
    - Only stone reads (`layers.json:21`), and fronts need four to five samples (HF 9).
    - Polish runs on footfall (`:5`), but handrails and handles are polished by hands.
    - The hollow is a slate rule (`:17`).
16. **The alpha-tested foliage pass and one far form for trees (L5).** The far form is disputed (see below).
17. **The cost of rebuilding a house that changes (L5).** It is first met in the player: the place bake and the encoder (`chunk-format.md:134–139`). The stone bakes offline, so it never meets this cost.
18. **Clocks per tile on roofs laid by hash** (`materials-at-scale.md`; D6.10).
19. **One list of lights across the town:** sockets, tile-binned spill, and light on water (`building-blocks.md:310`).

## Already decided in the stone's shape

Check each of these when its step opens:
- `schemas/material.schema.json:16–24`: wear in µm a century, and cracks counted against slate.
- `schemas/layers.json`:
  - slate's constants (line 3);
  - polish from footfall (line 5);
  - the hollow as a slate rule (line 17);
  - stone as the only reader (line 21);
  - no coat layer.
- `schemas/chunk-format.md:88, 112–126`: the piece flags, and the full 16-byte entry with no room for a coat offset or a room.
- `schemas/maps.json:14–21`: four facings only.
- `schemas/kind.schema.json:127`: no land merge unit.
- `docs/upkeep.md:57`: cement drawn as face kinds 4 and 5 in `Stone.shader`.
- `packs/stavanger-1989/parts/window/cross-arch.json` names crown glass, which ended about 1840 (HF 3 and 4).
- `parts/coat/paint.json` fixes oil paint as its binder (HF 3 and 4).

## Docs that disagree

Settle each of these, and correct both docs in place:
- Tufts: the BatchRendererGroup (`building-blocks.md:133, 220`) or compute (`ground-cover-and-plants.md:249`)?
- Tree edges: alpha-to-coverage (`trees.md:43`) or S1, under which shaders don't rely on it (`building-blocks-decisions.md:403`)?
- The shell's albedo and index: `maps.json:80, 83`, `painted-far-town.md:86, 89, 113` and HF 17 give three readings.
- The trees' far form: `maps.json:84`, `trees.md:42` and `building-blocks.md:208` disagree.

`building-blocks.md:3`, `building-blocks-decisions.md:298` and `chunk-format.md:139` use step names 3.0 to 3.4, from a numbering the plan no longer uses. Map each one to the port's steps before relying on it.
