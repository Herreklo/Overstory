# Inputs 1: materials, history and marks

Digests of three craft studies for the building-blocks architecture (`docs/plan.md`, "What the architecture decides"), October 2026, by an Opus agent. It decides nothing. Claims about our code that a decision rests on were checked in the source ("checked").

Status in the tables: **open** (nothing decides it); **planned** (the plan's days or scope assume it, but `NOW.md`'s "Decided" does not hold it); **decided** (`NOW.md` "Decided" or `CLAUDE.md`); **conflicts** (with a decision or another study).

## 1. `materials-at-scale.md`

### In short

1. Big worlds keep a small shared library of surfaces; a thing's identity is its masks and parameters. Ours come from facts and shape (§1).
2. Detail splits by frequency: smooth "where" fields in maps or vertices, identity in tiling painted textures, crisp edges from noise thresholded on the field (§1, Tiny Glade).
3. History rides on our vertices, so the stone cannot shed triangles. Decimated to a third, flight 0 keeps 95 % of its surface within 2 mm (§4, measured).
4. History moves into history maps per merged run, addressed from piece-local metric UVs, so every tier shares it and houses become possible (§4, "What should change now").
5. Houses get a board-and-trim atlas and a coat stack from a per-wall coat table; every material becomes a record in the pack (§4, §5).

### Against the bar

- **Sources.** Primary where they opened (Unity, Epic, Lagarde, Quilez, Mikkelsen, Toksvig, Paquette 2002, meshoptimizer). Many talks gave abstracts only; Cyberpunk's shader is known from modders. All marked (Gaps). `history-in-things.md` did open the Uncharted 4 slides (its §1), closing part of this study's first gap.
- **Concrete for our stack.** The strongest of the three: a triangle census by face kind and a decimation error table, run headless (§4); map sizes and memory for flight 0 (§4, "Worked through"); costs in days.
- **Checked.** UV1 to UV5 hold what §4 says (`Stone.shader`, lines 8 to 11); `STONES` in `stone.py`; boards from `_clad` with a 16-by-16 swatch palette (`building.py`, `palette.py`); `OS_Near` full at a 1.2 mm footprint, gone at 4 mm (`Detail.hlsl`).
- **Slips that change nothing.** A pixel at 1440p with the 38° lens spans 0.48 mm a metre, not 0.46 (§3; `painted-marks-in-motion.md` §5 has 0.48). Today's vertex is 72 bytes, not about 80.
- **One design fault.** The worked map layout (§4, "the gully's history map") stores states at a date ("lichen years / 200", "years bare / 200"), copied from today's channels. Two other studies want inputs with the date as a global (Conflicts). A reconciliation for Fable, not missing evidence.
- **Thin.** §2 restates `docs/visual-direction.md`; nothing rests on it. Its glass dates (Gaps) are now covered by `fronts-windows-and-signs.md`, finding 1.

**Verdict: meets the bar, with gaps that change no decision.** What is open is measurement (Unknowns).

### Decisions it proposes

| # | What | Why | Cost | Depends on | Alternatives weighed | Status |
| --- | --- | --- | --- | --- | --- | --- |
| M1 | History maps per merged run, 2 cm a texel underfoot, 4 to 8 cm on walls and roofs; piece rectangles addressed from UV0; 4-texel dilation; identity stays per vertex | per-vertex history blocks decimation and cannot hold a drip on a board (§4, "What breaks"); HLOD's gutter (§3) | 3 days | metric piece UVs (exist); a channel spec | an attribute-aware simplifier (meshoptimizer); Unity Mesh LOD, UV handling undocumented (§3) | planned (plan 3.2); conflicts with `performance-at-scale.md` |
| M2 | Stone tiers by measured error: full part within 5 m, Decimate to a third to 20 m, a quarter to 80 m, merged run beyond; each switch A/B in grey light | a third keeps 95 % within 2 mm, under half a pixel at 10 m (§4) | 1 to 2 days | M1 | limited dissolve (removed nothing); regenerated levels not weighed | planned in outline; method conflicts with `performance-at-scale.md` |
| M3 | Board atlas (4 × 1 m at 1 mm, strips by profile) and coat stack: up to 8 coats a wall in a data texture by wall id; survival a height blend by paint kind | boards stay geometry for the low-sun comb (§4); the GPU Resident Drawer refuses `MaterialPropertyBlock` | 5 to 6 days | M1, M4, facade exposure | per-vertex palette (today); Paquette's simulation, kept as rules | planned |
| M4 | Each material a record in the pack (identity, pigment, grain script and seed, tooling, water profile, wear, growth affinity, paint failure, city bake); family textures in one `Texture2DArray`; an editor step writes the asset | identity is spread over a dict, saved shader values and packs (§1, §5) | 2 days | the pack format | hand-tuned assets (today) | planned |
| M5 | Discrete facts (ghost signs, posters, rust runs, patches) as dated mesh decals from a family atlas, drawn by the host's stack, baked into the map far off; URP's Decal Projector only for transient scene state | a mark with its own cause needs more than a field (The Division, §1); DBuffer needs a depth-normal prepass | 3 days | M1, M4, diaries | projectors everywhere; clustered decals | open; conflicts with H4 |
| M6 | Glass by era with seeded waves; interior mapping by era and household. Roofs: courses as geometry, odd tiles by index from upkeep | van Dongen; the city camera sees roofs most (§4) | 4 days; 3 a roof family | room records; M4 | modelled rooms; tiles as geometry | open; glass refined by `fronts-windows-and-signs.md` |
| M7 | Distance rules: Toksvig on faded relief; fields drawn as two or three painted plates at the street stop; cross-fades where values match | §3, four rules | 2 days | M1, M2 | the mean alone ("grey mush") | open |
| M8 | Hex-tiling for render, concrete, asphalt, ground; an offline Kuwahara city bake as an experiment | no joints hide seams (§1); §3 rule 3 | 1 + 2 days | M1 | Quilez's two-fetch index | open; `land-rock-and-water.md` §1 agrees |

Texel targets: 0.5 mm for walked stone, 1 mm for walls, trims and paint, 2 mm for roofs. Its questions for Øystein now fall to the architecture (`NOW.md`: "The architecture's decisions are delegated").

### What every part must carry

- Per vertex, constant over a piece: face kind, piece seed, wall or board id. They survive decimation and index the rest.
- A per-piece metric grain UV, and an atlas address into its run's map, the same at every tier.
- Map channels (contested): polish, lichen, moss, water held; water layer, sky seen, ground seen, years bare.
- Per thing, in a data texture by id: the coat table (colour, year, paint kind, primer), care, years.
- Edge distance per vertex on dense trims; a material record id; for decals, atlas cell, year and host id.

### Conflicts and overlaps

| With | This study | The other | Kind |
| --- | --- | --- | --- |
| `performance-at-scale.md` §5 | "history in a texture with a parameterisation every tier shares" (§3) | close and near levels keep history "per vertex, as now"; maps from 20 m | conflict: one path or two |
| `performance-at-scale.md`, "Stairs" 2 | levels by Decimate and measured error | "Levels made by the generator from the same seed" | conflict: method |
| `performance-at-scale.md` §4 | 2 cm underfoot, 4 to 8 cm on walls | "1 cm at 20 m" | conflict: density |
| `performance-at-scale.md`, In short | city tier: "or the albedo with history baked in (no light)" | "Bake inputs, not outputs" | small conflict |
| `history-in-things.md` §8; `time-on-screen.md`, building blocks 2 | "lichen years / 200 … years bare / 200" | "Bake the reset year and the per-point rate instead, and pass the fabric date as a global" | conflict: map content |
| `history-in-things.md`, What we should do 4 | "rust runs below a fixing … each is a mesh decal" | carriers run "down the flow path across part boundaries" in the water bake | conflict: decal or bake |
| `painted-marks-in-motion.md` §5 | "Every tier switch should cross-fade (URP's LOD cross-fade dithers)" | the dither "reads as a screen door" without TAA (unverified) | tension |
| `painted-marks-in-motion.md` §7 | "a brush mark has a size in the world and never tiles visibly" (§1) | our brush "draws a world grid"; one world size "cannot serve our camera" | the rule is broken in code |
| `NOW.md`, Decided | a few metres of board grain on every board at seeded offsets (§4) | "Nothing repeats unless it was factory-made" | check: the profile is factory-made, the grain is not |

### Unknowns

- Blocks from BC7 in a smooth field; whether a 2 cm map draws as crisp as today's 8 cm vertex grid: the gully's map, FLIP and grey-light A/B (plan 3.2).
- Whether decimation's 13 mm outliers at chips show at the switch: A/B at the switch (plan 3.4).
- Map memory and mip streaming past a few thousand houses (about 70 to 140 KB a house): Tuesday's scale test is clay without maps, so this comes with house A.
- The per-pixel cost of `Growth.hlsl` and `OS_Noise` at 1440p: the harness. Whether Kuwahara reads painted or muddy: M8's experiment.

## 2. `history-in-things.md`

### In short

1. Every mark has a source, a path and an age. Games keep only the place, so their weathering says nothing (bottom line; §2).
2. Water washes and stains; a washed face beside a sheltered one is the strongest read of exposure (§2, Dorsey 1996; §6).
3. One curve per process per material, a rate per point: the state at year t is the curve at rate(x) × (t − reset(x)) (§2, Gu 2006; §8, the layer law).
4. Newer over older, and a work cuts what was there; a validator enforces it (§6, Harris; §8).
5. Parts date, surfaces age; readers infer causes from anything systematic, so seeded texture must be unsystematic at every cause's scale (§1, §7, §10).

### Against the bar

- **Sources.** Read in full: Dorsey 1996 and 1999, Chen 2005, Gu 2006, Lu 2007, the Uncharted 4 slides, Ruskin, Morris. Games, film, models, painters and most building practice are secondary, and marked.
- **Concrete for our stack.** It names the files and the shader change. Checked: the water bake is one scalar per vertex that folds splash into run-off (`water.py`, `down_face`, splash 0.35 m), with no wash, deposit or shelter term; shaders read years per piece and no rate (`OS_Streak`). Its list of what is missing (§9) is right.
- **Weak for our stack.** No costs (days, channels, milliseconds) for any of its twelve proposals, against `NOW.md`'s "every choice is costed". Carried stains across part boundaries (§9) need a bake over an assembly, which it does not design.
- **Thin.** §3 (film) and §4 (models) rest on articles and forums; they give principles, not decisions.
- **Superseded.** §10's readers are people; `NOW.md` decided model readers, and `docs/foundations.md` already uses §10's tasks with them.
- **Unverified local facts** (splash height, heating eras, the weather wall, repaint intervals) are pack data, not architecture.

**Verdict: meets the bar, with gaps that change no decision.** Its evidence is strongest where the architecture leans on it (the layer law, wash and deposit, superposition). Costs and the cross-part bake are design work for Fable.

### Decisions it proposes

| # | What | Why | Cost | Depends on | Alternatives weighed | Status |
| --- | --- | --- | --- | --- | --- | --- |
| H1 | The layer law: each layer is its material's curve at rate × (t − reset); rate baked from fields, reset from the record; a layer reads only the layers it depends on | Gu 2006; Lu 2007's cascades (§2, §8) | not given ("a small lookup") | per-point fields; curves in M4 | years since reset alone (today) | planned ("history as a function of the record and the date") |
| H2 | Wash and deposit in the water bake: flow rate, end of flow, rain shelter | Dorsey 1996, partial flow; black crusts (§2, §6) | not given | rain exposure | context generators (Substance); full particle simulation (§2) | planned |
| H3 | A deposit field (smoke, dust, salt) with sources by era | §6, Air | not given | the living fabric's fields | none | planned |
| H4 | Carried stains: a carrier from each source down the flow path across parts; a removed fixing's stain fades from its removal year | differential flow; γ-ton stain-bleeding (§2) | not given | H2; a bake that sees neighbours | none | planned; conflicts with M5 |
| H5 | The splash band as its own term (about 30 cm, above ledges), suppressed by moss and by paving that does not splash | Dorsey; γ-ton multi-weathering (§2, §6) | not given | H2 | folded into water (today) | planned |
| H6 | A superposition check: each mark's year in the cause view; a validator fails a mark older than a work it crosses | Harris; Morris; Venice Charter, article 12 (§6, §8) | not given | dated marks; works with scope | none | planned |
| H7 | Coatings with the houses: failure at board ends, bottom boards, sills, the weather wall; chalking by sun dose; ghost signs | NIKU; Purdue; Lu 2007 (§6) | not given | M3; H8 | none | planned (as M3) |
| H8 | Contact wear beyond feet (hands, shoulders, leaning, scraping) per material; a sun-dose bake beside the sky map | statues; Hsu and Wong; Purdue, FPL, Lund (§6) | not given | uses; the sky map | feet only (today) | wear planned; sun dose open |
| H9 | Dating from parts: each kind carries a part per era that dates it; typology and years sheets; "can you see the technique?" in every history review | 36 % right on decades from surfaces (§10); Riegl (§7); the Bechers (§6) | none | kits' part families | dating from surfaces | open; `time-on-screen.md` agrees |

### What every part must carry

- A reset year per point, or per piece and per repair surface, from the record. A repair is its own surface with its own stack from its year (§8, rule 1).
- Per-point rates, or the fields that make them: water (land, run, drip, pool), flow rate, end of flow, rain shelter, height above ground and ledges, sky, sun dose, wind and salt facing, deposit exposure per source, feet, hand zones.
- Carriers: which source upstream, how much, and the source's removal year.
- Each mark's year and the work that cut it (H6); the part's era and the fact that put it there (H9).
- The material's curve per process, in its record.

### Conflicts and overlaps

| With | This study | The other | Kind |
| --- | --- | --- | --- |
| `materials-at-scale.md` §4 | rate and reset (§8) | states at a date; rust runs as decals | conflicts (above) |
| `time-on-screen.md`, building blocks 2 and 3 | "they need a per-point rate and a curve per material and process" (§8) | "The date is an input, not a bake"; lives "stored as dated intervals" | agreement; it adds intervals |
| `kits-and-generation.md`, the stages | rate and reset | stage 3, Life, outputs "years since each layer was reset" | small conflict |
| `ground-cover-and-plants.md`, In short 6 | one curve, a rate per point | "Every plant has a stable rank, and time moves a threshold" | overlap: one mechanism |
| `land-rock-and-water.md` §2 | the splash band carries soil (§6) | a ground map "that rock, wall and plinth shaders read at their foot" | overlap: the band's colour |
| `NOW.md`, Decided | readers "from the public" (§10) | "Cold readers are model readers" | superseded |

### Unknowns

- Whether per-point rates give a smooth years sheet with jumps only at works: the gully's years sheet.
- Splash height and the weather wall here: a look test at the corner's wall foot, and the pack's climate data.
- Heating eras, the cannery stack, Norwegian repaint intervals: subject research before the deposit field and coatings are tuned.
- Whether shuffled facts drop the readers' score by thirty points: the first cold-reader round.
- How a carrier crosses parts, and at what bake cost: H4's first case, the gully's handrail post.

## 3. `painted-marks-in-motion.md`

### In short

1. A mark fixed to the thing moves right; one fixed to the screen slides (the "shower door"). Motion coherence tracks pleasantness (Kendall τ = 0.58) (§1).
2. Every production that kept strokes stable stored them in the thing's own space (§3).
3. Our brush reads world position, picks a world plane by the normal, draws a 71 cm grid with seams and never fades by footprint. It will slide on anything that moves, wind first (§7).
4. One world-sized stroke spans 1,450 pixels at 1 m and 4 at 400 m; octaves cycled by log2 of the footprint hold it within a factor of two (§5).
5. Supersampled stills hide shimmer and set fades 1.5 times too far; no mark has been judged moving. MSAA 4× stays, nothing may need TAA, no painterly filter over the screen (§5 to §7).

### Against the bar

- **Sources.** Primary: the INRIA papers, Praun 2001, Lu 2010, Vlachos 2010, the Deep Canvas and Patcher patents, Unity's manual and SRP source, Apple's WWDC talks. Secondary and "our arithmetic" marked throughout.
- **Concrete for our stack.** Strongest on cost (a technique table for the M4, §6) and on Unity 6's limits: TAA excludes MSAA; transparent materials write no motion vectors; STP needs compute (§5).
- **Checked.** `OS_Brush` reads world position, picks a plane by the normal, uses 1/1.4 m cells, has no footprint fade, and runs at 0.5 (`StreetLooks.hlsl` 319 to 332; `StreetStage.cs` 81). `OS_CardWS` flips cards by a side test against the camera's right vector (`Tree.shader` 159 to 172); leaf dithers read `positionCS.xy`; moss cover is unfaded (`Growth.hlsl`); `LT1Render` renders 1920 × 1080 at Super 2.
- **Gaps.** The search budget ran out, so many games have no technique found. Unverified: GPU skinning leaving spare UVs, STP's cost on the M4, the cross-fade dither's visibility without TAA. None changes an architecture decision; the dither is measured by the motion sheet.

**Verdict: meets the bar, with gaps that change no decision.**

### Decisions it proposes

| # | What | Why | Cost | Depends on | Alternatives weighed | Status |
| --- | --- | --- | --- | --- | --- | --- |
| P1 | Judge in motion at the game's pixel: a motion-sheet renderer (60 fps, 1440p, MSAA 4×, one sample a pixel), a footprint scale for stills, a swim test and a shimmer index | supersampled stills hide every fault in §7 (item 10) | 2 to 3 days | the harness | stills (today) | planned (Monday's tools) |
| P2 | The mark contract: mark coordinate, anchor class, seed by identity, rest pose, undisplaced position, motion vectors, the same marks at every tier, the smallest feature per mark | film's rule 1 (§3); the table by kind (§4) | 1 day | none | world-fixed marks | planned ("the painted look in motion") |
| P3 | The brush re-anchored to the part's coordinate, borders blended, fine octave faded by footprint; every other mark band-limited (moss cover, `OS_CardClip`) | §7, faults 1 to 4 and 8; Quilez (§5) | 3 days | P2 | the families in §1: screen-fixed, advected, per-object 2D, Gabor noise, filters | open |
| P4 | Trees ready for wind: bark marks from the undisplaced position; dithers from the card's UV; no mirror flip; a motion-vector pass with wind | §7, faults 5 to 7 | 1 to 2 days | P2 | none | open; before the wind |
| P5 | The octave-stepped brush: two octaves a factor of two apart, cross-faded by log2 of the footprint, contrast renormalised | dynamic solid textures (§1); a painter sizes strokes to the canvas (§5) | 1 to 2 days | P3; P1's pull-out | one world size; nested levels; marks by screen area | open; changes a line of `docs/visual-direction.md`; ours (`NOW.md`: "the brush's size by octaves and any boil") |
| P6 | Tier hand-overs: the same marks both sides, the switch where values match, short fades | §5 | a day a kind | M1, M2 | none | planned with tiers |
| P7 | Anti-aliasing: MSAA 4× at native 1440p; FSR 1 first fallback; STP only once every mover writes motion vectors | §5, §6 | none now | the harness | TAA or STP by default | open; conflicts with `performance-at-scale.md`'s leaning |
| P8 | No runtime painterly filter (Kuwahara about 25 ms at four sectors on the M4, our scaling); no boil on what stands; fluids by flow maps and held flipbooks; beams without a screen grain | §6; film's rule 5 (§3); Vlachos (§4) | 1 to 2 days (beams) | none | half-resolution Kuwahara far off; low or full boil | open; ours (`NOW.md`) |

### What every part must carry (§7)

- A 2D mark coordinate in metres, continuous where the paint should flow (a stone's face, a board's length, a wall run, the bark round its stem), anchored where the part does not change.
- An anchor class (static, rigid, skinned, flexible, card, fluid), joined to the motion class.
- A seed from the thing's and the part's identity, never vertex or build order.
- Rest position and normal (three floats each) on what deforms; the undisplaced position on what the wind moves; a motion-vector pass in every shader that moves vertices.
- The same mark coordinate, seed and history address at every tier; each procedural mark's smallest feature, declared.

### Conflicts and overlaps

| With | This study | The other | Kind |
| --- | --- | --- | --- |
| `performance-at-scale.md` §5 | the cross-fade dither "reads as a screen door while the fade runs" (unverified) | "A dither suits a painted look better than a pop" | conflict, settled by measurement |
| `performance-at-scale.md`, Decisions 4 | "Every mark must be stable without temporal accumulation" | TAA or STP "is softer, may suit the painted look" | conflict: stance |
| `animation-and-motion.md`, what every mesh carries | anchor class: "static, rigid, skinned, flexible, card or fluid" | motion class: "still, hinged, swinging, flexible, floating, emitting" | overlap: two vocabularies, one field |
| `animation-and-motion.md`, same | rest position in three-float UVs (`Mesh.SetUVs`) | "FBX from Blender carries 2D UV sets and one usable vertex colour" | dependency: an import step |
| `characters.md` §1 | octaves hold screen size; people carry "fewer, steadier marks" | strokes "scaled to the body … a decision for the look test" | overlap: one look test |
| `materials-at-scale.md` §4 | continuous across "a wall run" | UV0 per piece at "its own offset and turn" | tension: perhaps two coordinates |
| `time-on-screen.md`, item 7; `lighting-and-colour.md` §9 | seeds from identity; marks the same at every tier | "a replaced part gets a new id"; the bake kept "every part, every tier" | agreement |

### Unknowns

- Whether the brush shows in motion from the street stop at 0.5; if not, "it is doing no work" (§7): the motion sheet.
- Whether two octaves breathe in the pull-out (if so, nested levels): the motion sheet.
- How visible URP's cross-fade dither is without TAA: the first tier switch (plan 3.4).
- GPU skinning and spare UVs: the people step. STP's cost: only if the frame does not fit. The cost of `OS_Brush` and a second octave: the harness.

## 4. Across the three

### How history is stored and drawn

Read with `performance-at-scale.md` §5 and `time-on-screen.md`, the studies agree on a chain:

1. The record holds each part's life as dated intervals; a part exists from making to removal (`time-on-screen.md`, items 3 and 4).
2. History is a pure function, `history(piece, point)` (`performance-at-scale.md` §5), of the place's fields: water with wash, end of flow and shelter; splash; sky and sun dose; deposit; feet and hands; carriers (`history-in-things.md` §8, §9).
3. The generator rasterises it into history maps addressed from piece-local metric UVs, the same at every tier (`materials-at-scale.md` §4).
4. The maps hold inputs; the fabric date is a shader global; each layer is its material's curve at rate × (t − reset) (`history-in-things.md` §8; `time-on-screen.md` item 2).
5. Facts per thing (coat tables, care, signs) sit in a data texture indexed by an id on the vertices or the renderer's 32-bit user value (`materials-at-scale.md` §4; `performance-at-scale.md` §4). The same id serves picking back to the record (plan).
6. Discrete facts with a place are dated mesh decals drawn by the host's stack (`materials-at-scale.md` §4).
7. Fine marks are thresholded on the fields with noise in the part's mark coordinate and faded to their mean by footprint (`materials-at-scale.md` §1; `painted-marks-in-motion.md` §5).
8. A validator keeps newer over older; a diff across two dates fails any pixel outside the change list (`history-in-things.md` §8; `time-on-screen.md` item 7).

Three links are not agreed: what the map stores; whether close range keeps per-vertex history; whether carried stains are decals or a bake.

### The order to build them

1. Measure first, with the motion-sheet renderer among the tools (P1); golden views made with it avoid the stills' blind spots.
2. The contracts: one channel spec, the mark contract, the material record, the map's content under the layer law (P2, M4, H1).
3. The gully's history into maps, date as input, look unchanged by FLIP (M1, H1; plan 3.2).
4. The gully's tiers, chunks, proxies and hand-overs (M2, P6; plan 3.4).
5. The brush re-anchored and band-limited, as its own A/B after the port (P3, P5).
6. Wash, deposit, end of flow and splash on the corner's walls (H2, H5); then deposit sources and carriers (H3, H4).
7. Material records, then the board atlas and coat stack with house A (M3, H7, H8).
8. Trees ready for wind before the wind (P4); decals, glass and roofs with the houses (M5, M6); cold readers on the gully's years sheet (H9).

### The three questions Fable most needs to settle

1. **What does a history map store, and in how many channels?** Inputs with the date as a global (fields or rates, and reset years: `history-in-things.md` §8, `time-on-screen.md` item 2, `performance-at-scale.md` §5), or states at a date (`materials-at-scale.md` §4 and today's channels)? It sets the channel budget once wash, deposit, end of flow, splash, sun dose, carriers and hand zones arrive, whether a reset is per piece or per texel, and whether a jump in years costs a uniform or a rebake.
2. **One history path or two?** Maps at every tier with the mesh decimated by measured error (`materials-at-scale.md` §3, §4), or per-vertex history at close and near levels regenerated from the seed, with chunk maps from 20 m (`performance-at-scale.md` §5, "Stairs")? It fixes texel density (1 cm, 2 cm or 4 to 8 cm), the unit (run or chunk), the switch distances and the hand-over (`painted-marks-in-motion.md` §5).
3. **What is the one contract every part carries?** Identity (thing, part, seed, face kind) for lookup, seeds and picking; the map address; a run-continuous mark coordinate for the brush (`painted-marks-in-motion.md` §7) beside the per-piece grain coordinate (`materials-at-scale.md` §4); one class merging the anchor and motion vocabularies (`animation-and-motion.md`); rest pose and element index where needed. All within FBX's 2D UV sets plus an import step, and Unity's eight channels.
