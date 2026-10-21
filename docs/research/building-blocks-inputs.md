# Building-blocks inputs

The page Monday's Fable session starts from when it writes `docs/building-blocks.md`. It gathers every decision the architecture must take, with the evidence, costs, dependencies and conflicts from the fourteen craft studies (through the five digests in `docs/research/inputs/`) and from the two studies without a digest, `where-generation-runs.md` and `interface-and-inspection.md`. It decides nothing. Written on Opus, 22 October 2026.

## 1. How to use this

- Read this section, then the register group by group. Contested or weighty decisions get a full entry; the rest a row. Where the evidence clearly favours one option, a **lean** says so: a reading of evidence, not a decision.
- Pointers. A study by its file name in `docs/research/` and section (`where-generation-runs` §4); a digest as "inputs 2" with its item or conflict; K is `kits-and-generation` and P is `performance-at-scale`, as in the digests. "(ours)" marks this page's own arithmetic or reading. "Plan 3.2" is a step of the gully's port in `docs/plan.md`: 3.0 seeds, 3.1 stages, 3.2 history, 3.3 materials, 3.4 levels and chunks, 3.5 measure, 3.6 review.
- Settled by: evidence (enough already), judgement (Fable), the harness, the scale test, a look test, a motion sheet, or Øystein.
- Urgency: before the gully port (with its step), before House A (plan step 2), or later (with its step).
- In each group the full entries come first, then the rows; numbers follow the topic, not the order on the page.

### Decided already: do not reopen

`NOW.md`, Decided (22 October), unless Øystein reopens them:
- the architecture's decisions are delegated; only taste, scope and play go to Øystein;
- the reference machine is the M4 Mac mini, 60 fps at 1440p at default settings;
- cold readers are model readers;
- how years pass depends on the game; the screen follows the record, and play changes the record;
- show from 1989, remember from 1870: the past is the starting record, generated once by rule, never rendered; era content only for what survives into 1989;
- the player's acts change the 3D world, through the record;
- signs and street text in English, in each era's lettering;
- scenes written, not voiced; no motion capture; motion from free libraries edited against video;
- the town stands on Stavanger's phyllite;
- nothing repeats unless it was factory-made (Øystein, on stairs); no Houdini, no commissions, free and open bases only;
- build for bigger cities: every choice costed per building and per kilometre of street.

`CLAUDE.md`: the engine decides, Unity draws, Blender builds the parts; Understory is never changed from here; parts made with care, assembled by generators that do not invent their geometry; seeded and deterministic; the five kinds of thing on screen, and anything that reads as history is a fact; evidence, not verdicts; the setting is a pack; Rule 8; the order of work (hardest to change first, biggest risk first, a ladder of fidelity, one kind end to end, decisions written once).

Look and craft are ours (`NOW.md`): the night sky's colour, lamp glass, the tonemapper, the brush's octaves and any boil, near ground cover as strokes or blades.

**Planned, not decided.** `docs/plan.md` assumes history maps instead of per-vertex channels, levels by measured error, SplitMix64 seeds (plan 3.0) and generated meshes out of git. The architecture may revise them with reasons. `where-generation-runs` writes "Decided here" over its map; a study cannot decide, so it is the strongest proposal on the table.

### Who decides what

| Øystein: scope, play, permissions | The architecture |
| --- | --- |
| *Scope:* the C# port, about 15 to 22 Opus-days of porting around House A (`where-generation-runs`, For Øystein); the town system's scope and the eras after 1989 (`town-system.md`) | every item in the register, look and craft included |
| *Play:* which game first; how time passing is shown, to be explored creatively and prototyped on the corner (`NOW.md`); the interface's four defaults (the photograph, seeing the record, confirmation, naming strangers; `interface-and-inspection`, For Øystein); whether the player's mark is noticeable; the camera as a witness (`behaviour-on-screen`); grass parting round people (`ground-cover-and-plants`) | |
| *Permissions:* reference downloads, each with source and size first (archive photographs, the unopened GDC decks, Ghost's grass deck) | |
| *The reach of his own rules:* whether "English" covers proper names (the fixtures' "Vik Jernvare", street names with ø; inputs 5, conflict 7); whether reading "nothing repeats" at the grain of things is what he meant (D6.4) | |

They go to him in one message, each with a recommendation, after Tuesday's review (`docs/plan.md`).

### Bar checks for the two studies without a digest

**`where-generation-runs.md`.**
- *Sources:* primary where they opened: Unity's manuals and Mesh API examples with timings, Burst's determinism page, `Texture2D.Compress`, Python's notes on `random`, meshoptimizer, `bpypolyskel`, the Apache-2.0 skeleton, the CS2 asset wiki, 0fps, Sodium, Tiny Glade's makers via 80.lv. Townscaper, Bad North, Valheim and the Sims are secondary or unverified, and marked. That `MeshLodUtility` and Python for Unity are editor-only rests on search results.
- *Concrete:* the strongest study on the player side; costs and timings marked (ours). Checked here: `stone.py` seeds `random.Random(f"fill-{xc:.3f}-{s_a:.3f}")` (line 418); `resolve.py` has `plan_signature` (line 443); Unity is 6000.6.6f1. Two slips change nothing: SplitMix64 lives in `blender/resolver/hashing.py`, not `hashing.h`; and Burst 2.0.0 and Collections 6.6.0 are already present as built-in dependencies of `render-pipelines.core` in `packages-lock.json` (Mathematics is absent), not "not yet installed". The port should name them in `manifest.json`.
- *Thin:* no game publishes a rebuild time, so in-play costs extrapolate Unity's examples on 2019 Intel laptops (§5); the Python-to-C# speed ratio is unmeasured; streaming and cache eviction get one line; people, also generated at runtime (`characters` §7.1.10), are not costed; five licences unopened (Clipper2, earcut, LibTessDotNet, CGAL, the Unity Companion Licence).
- *Overreach:* "Decided here" and "This settles the digest's conflict 6" (§2) are proposals.
- **Verdict: meets the bar.** Its map rests on hard limits (no Blender, FBX import or GPL code in a player) and on a survey in which games that change at runtime assemble parts made offline, voxel worlds and Tiny Glade aside. Its numbers wait on the scale test.

**`interface-and-inspection.md`.**
- *Sources:* primary: Unity's manuals, Apple's WWDC20 and HIG, Microsoft's XAG, NN/g, the bubble-cursor paper, Paradox's dev diary 74, Grinblat and Bucklew, Mobius, Blizzard, Naughty Dog. Most game mechanics and all the theory are secondary or abstracts, and marked; Shneiderman and Fagerholt would not open.
- *Concrete:* section 6 is the clearest statement of what picking needs: ids at every tier, a scissored 64-by-64 id render read back two or three frames late, the highlight as one compare in the lit shader, the focus as a stencil in the post pass. Costs in days; (our estimate) throughout.
- *Stale within the project:* §3 says only transform, layer and rendering-layer mask vary under the GPU Resident Drawer, so "Ids for instanced parts must come from instance data we control or from position". P §1 reads in Unity's manual that the Renderer Shader User Value (6.3 on) gives each renderer a 32-bit value that "avoids breaking GRD instancing draw calls" (D13.1).
- *Thin:* no measured highlight cost on Apple silicon; `SV_PrimitiveID` on Metal unconfirmed; hover, the pad and the toggle need people, since model readers see stills.
- **Verdict: meets the bar for the architecture.** Its section 6 is what the building blocks take; its play choices are defaults for Øystein; "hover names things" clashes with behaviour's rule 10 (D13.6).

## 2. The decision register

Decisions are numbered D*group*.*n*. Section 3 assembles what they make every part carry; section 4 lists the conflicts once more with how to settle each.

### D1. The generator framework and where each stage runs

**D1.1 Which stages run offline, and which in the shipped player?**
- *Options:* (a) all offline in Blender; Unity reads plans and meshes (K §6; P, Our approach 8; `living-fabric.md`, Tiers). (b) Parts offline; plan, life at a date, placement, fitted parts per chunk and level, extrinsic bakes and cheap checks in the player, in C# (`where-generation-runs`, What we should do). (c) Library parts only, history in instance data and maps, no fitted geometry made in play (inputs 2, The shared shortfall).
- *Evidence:* a built player cannot run Blender, import FBX or ship GPL code. Shipped games that change at runtime author parts offline and choose, fit, deform, instance and merge them in play; only voxel worlds and Tiny Glade generate raw geometry (`where-generation-runs` §1). Burst wrote 300,000 triangles in 22 ms on a 2019 laptop (§3, primary); a 4 m chunk is estimated at 10 to 50 ms of worker time (§5, ours).
- *Cost:* (b) 26 to 38 days, 15 to 22 of them porting code we have (§4, ours); (c) the assembler and chunk format, 4 to 6 and 3 to 5 days.
- *Conflict:* K §6, Unity "places parts from the library at the plan's transforms and runs no generation"; `where-generation-runs`: "In the player, in C#: plan, life at a date, placement of library parts, fitted parts per chunk and level, the extrinsic bakes and the cheap checks."
- *Depends on:* Øystein's answer on the port; the scale test's runtime floor and demand rate.
- *Settled by* judgement; the scale test sets only on-demand against a shipped cache (D15.1). *Urgency:* the map before plan 3.1 (the split is the port's specification); the port the week after; the house builder before House A. *Lean:* (b). (a) breaks two decided items (play changes the record; the player's acts change the 3D world). (c) shows a coat, a sign or a swapped window, but no repaired tread, extended house or rebuilt wall, since those are fitted. Either answer from Øystein starts the same way: language-neutral contracts and plans in integers.

**D1.3 Fixed and fitted parts, and "the generator does not invent geometry".**
- *Options:* (i) each part is fixed (a judged mesh) or fitted (a judged function whose inputs are facts), and the rule says so (K §6, `made_as`; `where-generation-runs` §2); (ii) every part a hand-modelled `.blend` (the `blender-generators` skill); (iii) generators make geometry freely.
- *Conflict:* `CLAUDE.md`, the generator "does not invent their geometry"; K §6, "fitted: a part function called per instance because its shape is a fact" (inputs 2, conflict 6).
- *Evidence:* every stone piece today is fitted; walls, roofs and cladding must fit their footprints.
- *Settled by* judgement. *Urgency:* plan 3.1. *Lean:* (i); for a fitted part, the function and its parameters are what is judged, on a sheet. `CLAUDE.md` and the skill change wording.

| # | Question | Evidence and lean | Cost | Settled by | Urgency |
| --- | --- | --- | --- | --- | --- |
| D1.2 | One source for what runs in the player? | Two sources (drift certain), C# as source with Python the reference until each stage matches, a Rust or C++ core (a third language), or Python in the player (editor-only) (`where-generation-runs` §4). Lean: C# as source. Agents then iterate in C#, and look sheets run the C#. | inside D1.1 | evidence | the week after the port |
| D1.4 | Seven stages for every kind? | Facts, plan, life, geometry, bake, export, checks, each output hashed data (K §2, §6). In the player, export becomes the chunk cache. Stone has no plan stage today. Lean: yes. | about 4 d | evidence | plan 3.1 |
| D1.5 | Kinds as data, one runner? | `blender/kinds/`, one `generate(kind, thing, year, level)`, one export, one channel file; the monolith is copied into `wall.py` and channel headers drift (K §6, checked). Lean: yes. | about 2 d | evidence | plan 3.1 |
| D1.6 | The contracts' language, for Python and C# both? | Not studied (gap 1). JSON Schema with generated types, hand-written twins held by parity tests, or a binary schema for chunks. | unknown | judgement | plan 3.1 |
| D1.7 | A part definition? | K4's fields (section 3) and a kit validator; per level its error, budget and shadow role (P). | with D1.8 | evidence | schema plan 3.1; families House A |
| D1.8 | Standards per pack? | A metrics table by era: storeys, openings, rises, kerbs, thicknesses, grid (K3); the body range by cohort (inputs 4, our reading). Stavanger's values are unverified (`wooden-town-architecture`, Thin). | about 2 d | evidence; values from archives | schema now; values before the first window |
| D1.9 | Fitting? | Exact, stretch, adaptor, change the opening, refuse; never silent (K5). | in D3.1 | evidence | House A |
| D1.10 | Locks? | Pins as facts on semantic anchors; reseeds recorded (K9; Lipp). Whether pins survive a rules change is learned at the first bump. | about 2 d | evidence | House A |
| D1.11 | Things laid along a line? | One one-dimensional grammar (start, fill, end, corner, fallback, fit) for kerbs, copings, cladding runs, rails (K8). | 1 to 2 d | evidence | the walls (1e) |
| D1.12 | Licences? | Only permissive code ships, listed and checked at build; `bpypolyskel` (GPL-3.0) offline only; meshoptimizer (MIT) may ship; the Apache-2.0 skeleton for irregular hips, tested first (`where-generation-runs` §6). | about 1 d each | evidence | the first irregular roof |

### D2. Seeds and determinism

| # | Question | Evidence and lean | Cost | Settled by | Urgency |
| --- | --- | --- | --- | --- | --- |
| D2.1 | Seeds from what? | SplitMix64 on stable part ids, off `random.Random`: "Most of the random module's algorithms and seeding functions are subject to change across Python versions" (primary); keys from formatted floats re-draw neighbours when a piece moves and break "a seed stable for a part's whole life" (`time-on-screen` item 7). A replaced part takes a new id. Lean: yes. | about 1 d, own commit, new baseline | evidence | plan 3.0 |
| D2.2 | Matching across languages? | Five rules: seeds on stable ids; decisions only from integers or `+ − × ÷` and square root (a transcendental may place a vertex, never choose); plans and life in integers; geometry by tolerance across languages; sort by stable id (`where-generation-runs` §4). HLSL joins where layouts are evaluated at a point (D6.10). Lean: adopt. | in the split | evidence | plan 3.1 |
| D2.3 | Mesh hashes? | Conflict: P §6, "positions at 0.1 mm, channels quantised"; `where-generation-runs`, `mesh_hash.py` "hashes floats bit for bit: right for a refactor in Python, too strict across languages", tolerance 0.05 mm. A quantised hash is no tolerance test: a value near a boundary flips it (ours). Lean: a bit hash within one language; a tolerance compare per chunk and level across languages; FLIP on golden views last. | 2 d with checks | evidence | plan 3.1 |
| D2.4 | One hash chain? | Facts and rules version, then plan, life, mesh per chunk and level, bake, each a cache key; K's plan hasher, P's mesh hashes and the fabric's life hasher as one tool (inputs 2, overlap 12). | in D1.4 | evidence | plan 3.1 |
| D2.5 | Burst's deterministic floats? | Only for what must hash alike across machines, such as a shipped cache checked on load (`where-generation-runs` §4). | none | evidence | with D15.1 |

### D3. Records and the data contract

**D3.1 One dated record, and at what grain?**
- *Options:* (a) one structure: a slot (opening, socket, surface region, pane) never deleted, holding dated fills, each with its part, event, years, fit and the mark its removal leaves; (b) a record per kind (window, sign, cladding, socket).
- *Evidence:* K's dated cells, the fronts study's window records and the time study's lifespans are "one structure seen three ways" (inputs 5, conflict 1); the architecture study's dated wall surfaces are a fourth view (conflict 3). The code deletes cells (`_shop_fitted`, `resolve.py` 427), keeps one `original` per cell (387, 388), has no sign record (`ghosts`, line 82) and one `cladding` per volume (136). The window surround has no home (inputs 5, conflict 2).
- *Cost:* 2 to 3 days and a fixture hash migration (fronts, What we should do 1; K rec 4). *Depends on:* D3.2, D12.3, D13.1.
- *Settled by* judgement. *Urgency:* the structure before plan 3.1 (a stone repair is a fill); the house migration before House A, and before 1f if it is to show a window replaced twice. *Lean:* (a), down to pane and surface region, the surround its own fill: one change query, one pick path, one superposition check.

**D3.2 Ids: their form, and who mints them.**
- *Evidence:* the draft contract says "Ids are strings, typed by prefix, never reused and never changed" (`docs/engine-contract.md`). A part keeps its id for life; a replacement takes a new one (time item 7). Locks keep ids through regeneration, so a journal entry still points at the right step (`interface-and-inspection` §6, 2). The engine models no buildings yet, so fabric ids come from the pack and fixtures.
- *Options:* part ids as a semantic path from the thing through slot and fill (ours, after K9's anchors) or as counters; the 32-bit pixel id (chunk or record index plus part index; interface §6) as the stored id, or only as a draw-time index.
- *Settled by* judgement; no study designs ids end to end (gap 2). *Urgency:* plan 3.1. *Lean:* string ids in the record, semantic part paths, 32-bit indices only at draw time.

| # | Question | Evidence and lean | Cost | Settled by | Urgency |
| --- | --- | --- | --- | --- | --- |
| D3.3 | What travels with each fact and event? | Its kind among the five on screen, provenance (`authored`, `derived`, engine), precision (year or decade), actor, weight (time item 9; interface §6, 8 and 9). | hours, an engine request | evidence | fields plan 3.1 |
| D3.4 | What does the record admit? | One fabric record, kinds as data: parts, garments and carried things (`characters` §7.5), social traces (behaviour §7), plants (plants §3), signs, rooms, lights (fronts §8; light §9). | schema | evidence | schema now |
| D3.5 | A hierarchy? | Part, thing, group (flight, house, block), place; hover picks the level that suits the distance; far levels resolve to the thing (interface §6, 3). | schema | evidence | plan 3.1 |
| D3.6 | Readable text? | Only from records, the words layer feeding world, card and speech alike (fronts §6, §8; interface §6, 9). | none | evidence | House A |

### D4. Materials as data

**D4.1 A mark with its own cause: decal or bake?**
- *Options:* (a) dated mesh decals from one atlas per family, drawn by the host's stack, baked into the map far off; URP's Decal Projector only for transient scene state (`materials-at-scale` §4, M5); (b) carriers in the water bake, from each source down the flow path across parts, fading from a removed fixing's year (`history-in-things`, H4); (c) split by the shape of the cause.
- *Conflict:* materials, "rust runs below a fixing … each is a mesh decal"; history, carriers run "down the flow path across part boundaries" (inputs 1).
- *Evidence:* decals for marks with their own cause (The Division; materials §1); stain-bleeding by flow (history §2); DBuffer decals need a depth-normal prepass (materials §4). *Cost:* M5 3 days; H4 uncosted, its bake across parts undesigned.
- *Settled by* judgement, then H4's first case (the gully's handrail post) as a look test. *Urgency:* House A for signs and posters; carriers after the corner's wash. *Lean:* (c): records and outlines (signs, posters, a removed shopfront's line) as decals, since each stacks and picks; water-borne stains as carriers, since they cross parts.

| # | Question | Evidence and lean | Cost | Settled by | Urgency |
| --- | --- | --- | --- | --- | --- |
| D4.2 | The material record? | One shared library; a thing's identity is its masks and parameters, from facts and shape (materials §1). Each record: identity, pigment, grain script and seed, tooling, water profile, wear, growth affinity, paint failure, city bake (M4); albedo range, porosity, smoothness, translucency (light §9); scatter (`characters` §7.1.7); a curve per process (H1); texel targets 0.5 mm walked stone, 1 mm walls and trims, 2 mm roofs. Families in a `Texture2DArray`; an editor step writes the asset from the record, which takes over the role `LT1Trees.Materials` plays for the trees (ours). | 2 d | evidence | plan 3.3 |
| D4.3 | Coats? | Up to eight a wall in a data texture by wall id, survival a height blend by paint kind (M3), each coat with its year. Conflict: `building-system.md`, "The shader reads one number per coat: years since it was applied" (inputs 5, conflict 4). Lean: the year, read against the date. | 5 to 6 d with D4.4 | evidence | House A |
| D4.4 | Boards? | A board-and-trim atlas, 4 by 1 m at 1 mm; boards stay geometry for the low sun (materials §4). The profile is factory-made, the grain is not, so grain follows D6.4. | with D4.3 | look test | House A |
| D4.5 | Surfaces without joints? | Hex-tiling for render, concrete, asphalt, ground (M8; land agrees); a Kuwahara city bake only as an experiment. | 1 + 2 d | look test | step 3 |

### D5. History storage and drawing

**D5.1 What does a history map store?**
- *Options:* (a) states at a date: polish, lichen years / 200, moss, water held; water layer, sky, ground, years bare / 200 (`materials-at-scale` §4, worked example, copied from today's UV1 to UV5); (b) inputs: rates or the fields that make them, and reset years; the date a shader global; each layer its material's curve at rate × (t − reset) (`history-in-things` §8; `time-on-screen` item 2; P, "Bake inputs, not outputs").
- *Evidence:* the layer law rests on Gu 2006 and Lu 2007 (primary). Our drift is closed form already: the hollow is rate × use × years; polish saturates within forty years; lichen and moss are clipped ramps (`where-generation-runs`, Where we stand). With (a) every date is a rebake; with (b) "a jump costs a uniform", which the decided rule needs: the town draws the same watched or jumped, "so a jump is cheap" (`town-system.md`, For Øystein 2).
- *Conflict:* materials, "lichen years / 200 … years bare / 200"; time item 2, "Bake the reset year and the per-point rate instead, and pass the fabric date as a global."
- *Cost:* 1 to 2 days (time); the channel budget grows with each new layer (D5.6).
- *Settled by* evidence, checked on the gully's years sheet (jumps only at works) and by FLIP. *Urgency:* plan 3.2. *Lean:* (b).

**D5.2 One history path, or two?**
- *Options:* (a) maps at every level, addressed from the pieces' metric UV0 (`materials-at-scale` §3, §4); (b) per vertex at close and near, resampled from `history(piece, point)`, chunk maps from the street level (P §5); (c) maps at every level, per-vertex data only for piece constants and for what moves geometry, such as the hollow's rate and gradient (`where-generation-runs` §2).
- *Evidence:* decimated to a third, flight 0 keeps 95 % of its surface within 2 mm (materials §4, measured); houses cannot carry history per vertex; P's own argument frees the carrier ("nothing is kept, everything is sampled again"); today's vertex grid is about 8 cm, a 2 cm map is finer.
- *Conflict:* materials, history "in a texture with a parameterisation every tier shares"; P §5, close "per vertex, as now"; `living-fabric.md`, "the city tier bakes the life into the merged mesh's vertex data" (inputs 2, conflict 2).
- *Cost:* M1 3 days; overlaps P5 (2 to 3) and P6 (5 to 8). *Depends on:* D5.3, D6.2, D6.6.
- *Settled by* a look test: the gully A/B in grey light at eye level, FLIP within threshold; the harness for cost. *Urgency:* plan 3.2. *Lean:* (c): no hand-over between carriers where values must match (`painted-marks-in-motion` §5), and houses need maps anyway.

**D5.3 The map's unit and texel size.**
- *Options:* per merged run (flight, wall run, facade, roof slope; materials §4) or per draw chunk of 3 to 5 m (P §5); 1 cm a texel (P §4) or 2 cm underfoot and 4 to 8 cm on walls and roofs (materials §4).
- *Evidence:* at 1 cm both fronts of a kilometre of two-storey street take about 280 MB; at 4 to 8 cm, 4 to 18 MB (inputs 2, ours). The gully's map at 2 cm is 1024 by 512, about 1 MB compressed. Fields are smooth; crisp edges come from noise thresholded on them (materials §1).
- *Depends on:* D6.3, D8.1. *Settled by* the scale test with synthetic maps at both densities (inputs 2, section 4, item 2, not in the plan as written) and the gully's A/B. *Urgency:* density plan 3.2; unit plan 3.4.
- *Lean:* each field sized by its smallest feature (materials' figures for surface history); the draw chunk as unit, since chunks cut at piece boundaries split a run's atlas without seams and are what a change rebuilds.

**D5.4 Where resets live, and rates that change mid-life.**
- *Evidence:* "a repair is its own surface with its own stack from its year" (history §8); piece values survive simplification as vertex constants (materials §4).
- *Gap found here (ours):* the layer law holds one rate per point within an interval. When a rate changes (a gutter fitted, a neighbour pulled down, care falling), the layer must carry on from where it was. An age offset per texel for each interval, beside its rate, does that; a rate change is a discrete change that rebuilds its chunk anyway. No study addresses it.
- *Options:* resets per piece and repair surface, rates and offsets per texel; or resets per texel too. *Settled by* judgement, checked on the years sheet. *Urgency:* plan 3.2. *Lean:* the first.

| # | Question | Evidence and lean | Cost | Settled by | Urgency |
| --- | --- | --- | --- | --- | --- |
| D5.5 | Split history by cause? | Intrinsic channels (face kind, edge distance, own occlusion) in the mesh; extrinsic ones (years, feet, water, damp, care) per instance, field tile or map, so a library sett carries its lane's years (P5; P §2). Lean: yes. | 2 to 3 d | evidence | plan 3.2 |
| D5.6 | Slots for the missing layers? | Wash and deposit with flow rate, end of flow and rain shelter (H2); a deposit field by source and era (H3); the splash band (H5); contact wear beyond feet and sun dose (H8); carriers (H4). Slots now, values later; the study costs none (inputs 1). | not given | judgement | slots plan 3.2 |
| D5.7 | Newer over older? | A superposition validator (H6) and a diff across two dates that fails any pixel outside the change list (time item 7). | about 1 d | evidence | House A |
| D5.8 | Fine marks and the brush? | Thresholded on fields with noise in the part's mark coordinate, faded to the mean by footprint; Toksvig on faded relief; fields as two or three painted plates at the street stop (M7; painted §5). The brush re-anchored to the part's coordinate, borders blended, its fine octave faded by footprint (P3); today it reads world position on a 71 cm grid and will slide on anything that moves (painted §7). Octave stepping is ours, on motion sheets (P5). | 2 d; 3 d brush; 1 to 2 d octaves | motion sheet | the mark contract at plan 3.1; the brush after the port |
| D5.9 | Budgets per view? | One mechanism, three counts: histories (`living-fabric.md`, Rationing), acts (behaviour §7), motion (animation §2), chosen by the change query's weight (inputs 4, C7). Numbers wait on the corner's years sheet. | small | look test, cold readers | weight now; step 4 |

### D6. Distance levels, chunks, instancing and repetition

**D6.2 How are levels made?**
- *Options:* (a) Blender's Decimate by measured error (M2); (b) the generator makes each level from the same seed and outline (P4: a 1,100-triangle tread, then 100 to 150, then a box of 12 to 24); (c) Unity's Mesh LOD at import; (d) meshoptimizer with attribute weights and locked borders.
- *Evidence:* Decimate "weighs no attributes"; with Mesh LOD "joints are likely to melt", it says nothing on UVs and builds only in the editor (P §1; `where-generation-runs` §3). Decimate keeps 95 % within 2 mm at a third, with 13 mm outliers at chips (materials §4). If fitted parts are made in the player, only (b) and (d) exist there.
- *Conflict:* materials, levels "by Decimate and measured error"; P, "Levels made by the generator from the same seed" (inputs 1).
- *Settled by* the Mesh LOD afternoon test on the gully's FBX (P rec 2) and A/B at each switch. *Urgency:* plan 3.4. *Lean:* (b) for fitted parts, since it runs in the player and keeps outlines and joints; (d) for natural stone and land; (a) or (c) only for offline library parts that pass the A/B.

**D6.3 The merge unit.**
- *Options:* per thing; runs of 3 to 5 m cut at piece boundaries (P3); the land's 64 m chunks; a streaming cell; or nested.
- *Evidence:* GPU occlusion culls by bounding sphere, so a 33 m flight is never culled (P §1); AC Unity's clusters (primary); a change rebuilds the chunk, not the thing (`where-generation-runs` §5).
- *Conflict:* K §6, "Unique geometry, merged per thing"; P, "A flight is written as runs of three to five metres"; land, "Chunks of 64 m"; `foundations.md`, "runs of parts merged (a flight, a wall, a house)" (inputs 2, conflict 1).
- *Settled by* the scale test (load and rebuild per chunk, demand rate, cache per kilometre). *Urgency:* the chunk id in the plan at plan 3.1; sizes at plan 3.4. *Lean:* nested: 3 to 5 m draw-and-rebuild chunks for close to street levels, merged runs and blocks beyond, 64 m land chunks, streaming cells an aligned multiple, each unit with an id for picking.

**D6.4 Repetition and libraries.**
- *Options:* (a) every hand-made piece unique ("Every piece its own seeded instance, so nothing repeats", `research/stone.md`); (b) large libraries fitted by stretch, face stones repeating "beyond a few metres apart, turned and mirrored" (K §7), "a few hundred wall stones in size classes" (P); (c) things never repeat; pieces repeat only where no viewer can find the repeat; only what wear shaped is unique (K, For Øystein 1; `docs/plan.md`).
- *Evidence:* a stair with its walls is 816,000 triangles and 36 MB of FBX; a kilometre of wall about 5 million triangles and 200 MB today, against about 50,000 instance records and 30 MB of maps from libraries (P, estimate). Øystein's words were "no two stairs alike unless manufactured like that" (K, For Øystein 1): about things. Under D1.1 (b), a unique fitted piece costs build time and memory, not disk.
- *Conflict:* `NOW.md`, "Nothing repeats unless it was factory-made", against K §7 and P (inputs 2, conflict 5). The question returns for "one of 8 to 12 archetype silhouettes" (animation §2), rooms as "a few rooms per kind, era and class" (fronts), board grain, and plant strokes.
- *Settled by* judgement on the reading; a look test (a stretched library stone at eye level; P, Gaps); a repeat-finding check on the golden views; the scale test for the memory of unique close chunks. *Urgency:* before plan 3.4 for stone; House A for boards and rooms. *Lean:* (c), measured by whether a repeat can be found. It reads a decided item at the grain Øystein spoke, so the reading goes to him with the numbers.

**D6.5 Splitting the frame's budget.**
- *Question:* how do 2 million visible triangles and 3,000 draws divide among land, water, ground cover, trees, stone, houses and people in each judging view?
- *Evidence:* land about 370,000 before culling; near ground cover up to 300,000; the tree overhead 100,000 to 150,000 with real leaves; water under 100,000 (inputs 3, conflict 8); twenty near people 0.3 to 0.8 million (inputs 4, C4, ours); P built its tiers on 4 million (inputs 2, conflict 8). On the M4, opaque overdraw and MSAA are cheap, alpha-tested layers and small triangles dear (`foundations.md`). P1: the median visible triangle at ten pixels or more.
- *Settled by* the harness for figures, judgement for shape; the scale test has no people, so their share is held back. *Urgency:* provisional before plan 3.4. *Lean:* every kind declares counts per level as an export check; a split per view; opaque first (D9.1); nothing relying on temporal accumulation (D7.2).

| # | Question | Evidence and lean | Cost | Settled by | Urgency |
| --- | --- | --- | --- | --- | --- |
| D6.1 | The tier table? | Five sets of boundaries: `foundations.md` 20, 80, 400 m; P 8, 20, 80, 200; plants 8, 40; land rings out to 64, 256 and 1,024 m; stone 5, 20 (inputs 3, conflict 7). A pixel spans 0.48 mm per metre, so a level is safe beyond about 2,000 times its error (P); supersampled stills set fades 1.5 times too far (painted §5). Lean: levels by error in pixels; named tiers as judging bands; `foundations.md` rewritten. | none | evidence; motion sheet for switches | plan 3.4 |
| D6.6 | Hand-overs? | Conflict: painted §5, the dither "reads as a screen door while the fade runs" without TAA (unverified); P §5, "A dither suits a painted look better than a pop." Dithered cross-fade works with the Resident Drawer, animated does not (UUM-91634, P §1). Lean: the same marks, seed and history address both sides, the switch where values match (painted P6). | a day a kind | motion sheet | plan 3.4 |
| D6.7 | Instancing route? | The Resident Drawer with the Renderer Shader User Value for kit parts and street things; BRG for setts, slates, tufts; no Entities (P8). Shaders to `#pragma target 4.5` with `DOTS_INSTANCING_ON`, `LOD_FADE_CROSSFADE`, `unity_RendererUserValue` (P9). The Drawer "can get slower" when GPU-bound, and MSAA forces depth priming off (P §1). | 1 to 2 d shaders; 4 to 6 d libraries | harness | shaders plan 3.4; libraries before House A |
| D6.8 | Shadows? | From proxies: close and near never cast, street in the first cascades, city beyond; small parts, tufts, litter never; hulls and cores cast (P7; plants §6). | about 1 d | evidence | plan 3.4 (cut line) |
| D6.9 | District and far? | Merged per block with a block atlas; impostors far; needed now only if the scale test's thousand clay houses miss the frame at the city camera (inputs 2, section 4, item 3). | about a week | scale test | later |
| D6.10 | Layouts evaluated at a point? | Slate courses and sett rows by a hash per row, alike in C# and HLSL, so far levels draw the same slates without a bake (P10). | not costed | evidence | the first roof |

### D7. The light

**D7.2 Antialiasing, and whether anything may rely on temporal accumulation.**
- *Options:* MSAA 4× at native 1440p, FSR 1 the first fallback, STP only once every mover writes motion vectors (painted P7); TAA or STP by default (P, Decisions 4).
- *Conflict:* painted §7, "nothing may need TAA to look right"; P, TAA or STP "is softer, may suit the painted look". Plants §6: hashed alpha's noise "is meant to be smoothed by temporal antialiasing, which we do not use". In Unity 6, TAA excludes MSAA and MSAA forces depth priming off (painted §5; P §1). Whether GTAO and SSR are clean without temporal accumulation is unmeasured (inputs 3).
- *Settled by* the harness and motion sheets. *Urgency:* the rule before shaders change (plan 3.4); the choice later. *Lean:* the rule "nothing relies on temporal accumulation", MSAA 4× by default: every mark stays stable without history, and golden views and hashes stay repeatable.

| # | Question | Evidence and lean | Cost | Settled by | Urgency |
| --- | --- | --- | --- | --- | --- |
| D7.1 | Where do the light's inputs live per level? | Parts carry visibility, never light: sky, ground, openness and weather exposure per face, and a two-channel bent normal, at every level and on impostors (light §7, §9). Conflict: P §5 slims the street vertex to "position, normal and two UVs"; light wants four bake channels and a bent normal everywhere (inputs 3). The materials "place" map already holds sky and ground seen. Lean: in the same maps as history (D5.2); impostors in their own atlas. | small | judgement | plan 3.2 |
| D7.3 | One world state? | One record, owned once, read by every system: fabric date, day of year, sun, weather, wind, tide. Light's layers 1 to 3 hashed and replayed (light §8); plants' weather "a hash of the world's seed and the day"; land's tide from the date; four separate clocks (time item 6) (inputs 3, conflict 3). `LT1Years` does not exist yet. | 1 d clocks; 3 to 4 d rig as layers | evidence | the date at plan 3.2; the rig at 1c |
| D7.4 | The shade's lasting fix? | Three lookups in `OS_ShadeP`: sky radiance from a model, the seen ground, the seen town; the four debts share one cause (light §7). Reads D8.1's ground map. | 1 to 2 d bounce; 3 to 5 d sky | look test | 1c; the cheap lookups before more look judging |
| D7.5 | Lights, spill and sockets? | Lights from sockets in tiers: shadowed spots near (perhaps 8 to 16), unshadowed at the street level, glow beyond. No window or shop is a real light; spill from a tile-binned buffer; one socket definition for lamps and windows (light §3, §7; fronts §3). Conflict: `TownLights.cs` makes every lit shop a spot light (lines 75 to 81; inputs 5, conflict 6). The heart holds 403 lights against Forward+'s 256 per camera; how many each camera sees is unmeasured. | 5 to 8 d; 2 d spill | harness | socket schema before House A; steps 3 and 6 |
| D7.6 | Probes? | None baked: probe volumes bake in the editor and cannot follow a rebuilt town. Reflection probes placed by the generator, a few relit a frame; far shadows and horizon angles from the height map (light §2, §7). Follows D1.1. | 3 to 4 d | evidence | 1c, step 6 |
| D7.7 | Occlusion? | On indirect light only: GTAO, none on the sun, multi-bounce with albedo, specular occlusion (light §2, §7). | 0.5 to 1 d | harness | 1c |
| D7.8 | Screen and grading rules? | No runtime painterly filter (Kuwahara about 25 ms on the M4, our scaling); no boil on what stands (painted P8). The style pass in the colour lookup, dither at the last write, lamp kinds by spectrum, normalised specular, exposure from illuminance, a chart and debug views of the shade's terms (light §3, §4, §7, §8). HDR buffers, dithered grading and no lifted blacks, since dark skin breaks first (`characters` §6; a Rule 8 safeguard). | about 4 d | evidence; frames | now, as rules |

### D8. The land and water

**D8.1 Shared maps, owned once.**
- *Question:* who owns each shared map (height and sky, the ground map, fields, deposits, history maps), at what resolution and unit, and when is each rebuilt?
- *Evidence:* the ground map has three readers: rock, wall and plinth feet (land §2), blade roots (plants §1), the light's seen ground with seasonal albedo and wet (light §5, §7) (inputs 3, conflict 2). Two studies size fields differently, which the digests did not list (ours): P §4 tiles feet, water, sky and care at 64 by 64 for a 4 m chunk, "6 cm a texel"; land §6 bakes soil, flow, wetness, wind and salt, sun dose, made ground and feet "at 0.5 to 1 m in the heart and 2 to 4 m beyond". `living-fabric.md` redraws fields "by decade"; D1.1 (b) makes that "on change". Horizon's fields take about 4 MB a square kilometre (land §1); ours are unmeasured.
- *Settled by* judgement for owners, the scale test for disk. *Urgency:* the registry before plan 3.2 (the gully reads water and feet); land fields at 1d. *Lean:* one registry naming each map's owner, resolution, unit, readers and rebuild trigger; one ground map; land fields coarse, surface history fine, each sized by its smallest feature.

| # | Question | Evidence and lean | Cost | Settled by | Urgency |
| --- | --- | --- | --- | --- | --- |
| D8.2 | Natural and made ground? | Natural ground as layers (bedrock, regolith, landforms with rock kind, ice vector, foliation and joints, water); made ground as dated acts (outline, kind, target surface, edge, year, plan unit) applied in date order, as CityEngine stores deltas (land §1, §5). Acts in play only "if a game needs them (unknown)" (`where-generation-runs` §2); a family game does (section 5). | ½ + 2 d | evidence | 1d |
| D8.3 | Terrain? | Mesh terrain: 64 m chunks, constrained triangulation with breaklines, holes under paving and houses, rings of 0.5 m triangles to 64 m, 2 m to 256 m, 8 m to 1 km and 64 m beyond (about 370,000 triangles before culling), skirts, a coarse caster; not Unity Terrain, which stretches on cliffs, holds no breaklines and misses the Resident Drawer (land §1). Its chunks line up with D6.3's streaming cells. | 3 d | evidence | 1d |
| D8.4 | Parts meeting the ground? | Foot lines as hard or soft breaklines, footprints cut from the ground, a ground map read at every foot, a strata tint under unloaded rock (land §2). The gully exports breaklines from the start (inputs 3). | in D8.3 | evidence | export plan 3.1 |
| D8.5 | Natural stone? | A kind: a volume cut by joints, leaned by foliation, smoothed and plucked by the ice; cut faces dated with drill marks; the pack's vectors as slots, checked at Watch Knoll (land §1, §2). | 4 to 5 d | look test | 1d |
| D8.6 | The ground's shader, and a mat's edge? | On `OS_ShadeP`: few materials chosen from fields, thresholded edges, hex-tiling, a far colour bake (land §1). Edge as mesh (plants §8) or shader (land §1) (inputs 3, conflict 1): perhaps slow edges mesh, fast ones shader. | 3 d; mats a week | the corner's years sheet | step 3 |
| D8.7 | Water? | Opaque meshes with baked depth; 8 to 12 Gerstner waves from wind and fetch; SSR, planar only if SSR fails; lamp columns from the one tiled light list; tide and shore bands derived (land §3). Two winds, climate and moving, share the fetch (inputs 3, conflict 4). | 4 + 1 to 2 d | look test | step 6 |

### D9. Plants

| # | Question | Evidence and lean | Cost | Settled by | Urgency |
| --- | --- | --- | --- | --- | --- |
| D9.1 | Opaque first? | A rule: no cards or shells near; cards only where few overlap, cut to their outline; opaque cores. Apple's GPUs skip what opaque fragments hide but shade every alpha-tested layer (WWDC 2020; plants §6). | a rule | harness (overdraw, alpha-to-coverage, a depth pass under MSAA) | now; birches at 1e |
| D9.2 | One placer, one presence law? | present = potential(fields, facts, date) > rank(seed), per tile on the GPU, indirect draws (plants §6, §8). It overlaps the layer law (inputs 1): one presence law for discrete things (plants, colonies, litter) beside the layer law for continuous ones (ours). | about a week | judgement | step 3 |
| D9.3 | What hard parts carry for plants? | Joint lines and growth faces as data, copings, traps, climbable regions, keep-clear zones, trellis sockets (plants §8; section 3). | in the export | evidence | plan 3.1 (the gully's joints) |
| D9.4 | Plants as records? | Bushes, hedges, climbers and gardens built like small trees, with keepers' calendars; a hedge is a hull plus the shoots since its last cut (plants §3). | a week each | evidence | schema now; steps 3, 7 |
| D9.5 | Trees on the M4? | Conflict: P §3, the near birch at 60,000 triangles "is fine within 20 m"; plants, "Our birches are probably the dearest pixels" (about fifty card layers a pixel). `foundations.md` budgets 60,000 a near tree; plants 100,000 to 150,000 overhead with real leaves. | the re-fit | harness, Tuesday | 1e |
| D9.6 | Trees ready for wind? | Bark marks from the undisplaced position, dithers from the card's UV, no mirror flip, a motion-vector pass (painted P4). | 1 to 2 d | motion sheet | before the wind |
| D9.7 | A tree beside a change in play? | Growth stays offline; a change applies as events the timeline handles; regrowth in play is learned at step 7 (`where-generation-runs` §5). | unknown | measurement at step 7 | step 7 |
| D9.8 | Leaves and litter? | A deposit field per chunk for the date, moved by the day's wind, cleared by feet and keepers (plants §4). | 3 to 4 d | look test | step 3 or 9 |

### D10. Motion and people's affordances

**D10.2 People inside the levels and the repetition rule.**
- *Options:* each person's own shape at every level, near "about 25,000 to 40,000 triangles", far "a `proxy741`-class shell" (`characters` §7.1.9); "one of 8 to 12 archetype silhouettes" at the city level, near "about 15,000 to 25,000" (`animation-and-motion` §2).
- *Agreement:* the same height, build, hair mass, outer colour and gait seed at every level. Skinned levels are separate meshes (Mesh LOD deforms level 0 regardless); the Resident Drawer takes only mesh renderers; people need their own pick path (inputs 4, C13).
- *Conflict:* archetypes against "nothing repeats" (inputs 4, C4); twenty near figures take 0.3 to 0.8 million triangles (ours).
- *Settled by* the people step's recognition test and crowd tier at 500 and 2,000 on the harness. *Urgency:* step 5, with a budget share held now (D6.5). *Lean:* identity numbers in the contract now; the far mesh by measurement.

| # | Question | Evidence and lean | Cost | Settled by | Urgency |
| --- | --- | --- | --- | --- | --- |
| D10.1 | Motion class and anchor class: one field or two? | Painted: "static, rigid, skinned, flexible, card or fluid"; animation: "still, hinged, swinging, flexible, floating, emitting" (inputs 1, 4). Lean (ours): one field per element, the anchor derived (still to static; hinged, swinging, floating to rigid; flexible to flexible; emitting to fluid), plus a card or skinned flag. Animation: "the cheapest item here and the one that cannot wait". | 1 to 2 d | judgement | plan 3.1 |
| D10.3 | How does motion data reach Unity? | Element index and depth in one UV channel; a sidecar element table; the importer writes a float texture or Vector4 UVs; people get their own import rule (animation, What every mesh must carry). Under D1.1 (b) meshes made in the player write any layout through `MeshData`; only library parts pass through FBX (ours). | with D10.1 | evidence | plan 3.1 |
| D10.4 | Affordances? | Dated sockets like any other (D3.1), with the fields in section 3 (animation; behaviour §4). A worn tread's height is read at the date, since the hollow moves the surface (ours). The grey walker on the gully's treads (1 to 2 d, inputs 4) tests the contract before a thousand stairs exist. | half a day each for stairs and doors | the grey walker | export plan 3.1 |
| D10.5 | Feet? | Every walked surface registers a walking line to the feet field, the sum of the year's day plans over the paths (behaviour §7; engine request 16; `authored` until then). | none now | evidence | plan 3.1 |
| D10.6 | Wind? | One field, a pure function of position and absolute time, sampled by each element through its own oscillator; levels wake by Beaufort force (animation §3); owned with the world state (D7.3). | 4 to 6 d on the birches | motion sheet | contract now |
| D10.7 | Motion and time? | Every motion a function of the record and absolute time; cloth the one warm-started exception; a time-jump test (animation, WWSD 9). | 1 d | evidence | the rule now |
| D10.8 | The gait seed? | In identity, set at birth (`characters` §7.2; animation §1), not in the per-year `person_behaviour`, which invites a re-roll (behaviour §7; inputs 4, C5). | none | judgement | schema now |
| D10.9 | Faces? | Swapped painted textures (`living-world.md`) or shape keys (animation; `characters` §7.1.8) (inputs 4, C2). People's import keeps blend shapes on, so both stay open. | none now | look test | step 5 |
| D10.10 | Clips and rules? | Engine-neutral data, since Unity's animation system is changing (animation §1). | none | evidence | step 5 |

### D11. Buildings, fronts and signs

| # | Question | Evidence and lean | Cost | Settled by | Urgency |
| --- | --- | --- | --- | --- | --- |
| D11.1 | The window? | Inside D3.1: the opening never deleted, fills as a list, the dressing, the room by reference (fronts §8; section 3). The surround is its own dated fill (architecture rule 4; inputs 5, conflict 2). | 2 to 3 d | judgement | House A |
| D11.2 | Wall surfaces? | Dated by region: cladding with profile, year, scope and corner type; fronts reclad first, gables and yards keep the first skin (architecture rule 2). Today one `cladding` per volume. | in D3.1 | evidence | House A |
| D11.3 | The room? | A record with a box in mm, kind, household or business, year fitted and lamps, `derived` by era until homes (engine #59); its box as instance data that survives merging (fronts §8). Which of the room box, each pane's glass and the lit state are instance data and which texture, at each level, is open (inputs 5, question 3); the lit state must stay live by the hour, never baked. The room atlas meets D6.4. | in D11.1 | judgement | schema House A; shader step 2 |
| D11.4 | The sign? | A record with its own events, apart from the business (fields in section 3); street records as a coat stack (fronts §5, §8). The reach of "English" goes to Øystein. | in D11.1; 2 d street records | evidence | House A |
| D11.5 | The ground floor? | Its own grammar, under a control layer of a few correlated decisions per building (K7). | about 2 d | evidence | House A |
| D11.6 | `eras.py`? | Classical houses roll a mansard 30 % of the time (line 16), but "no source shows mansards on Stavanger's classical houses"; on D or E it claims a roof raise the record lacks (inputs 5, conflict 10). Also chalet pitch 38° to 45°, classical eaves near 100 mm, storeys 2,500 to 2,600 mm, new shelves. `stronger` multiplies pitch by 1.3 and eaves by 1.7 (`building.py` 286 to 292), amplifying a wrong base. | data and a fixture migration | evidence; archive values | the mansard before 1f; values before step 2 |
| D11.7 | Glass and interiors? | Glass by era with one normal per pane (crown, cylinder to 1928, drawn to the late 1960s, then float); one opaque window shader reading the room box (fronts §1, §2; M6). | 4 to 6 d | look test, harness | step 2 |
| D11.8 | Lit rooms? | The household's day as rules, lit per room and hour, `derived` until engine #22 (fronts §3). | 1 to 2 d | evidence | step 2 |
| D11.9 | Roofs? | Courses as geometry; odd tiles by index from upkeep (M6); a straight skeleton when a footprint needs it (D1.12). | 3 d a family | look test | House A |

### D12. Time

| # | Question | Evidence and lean | Cost | Settled by | Urgency |
| --- | --- | --- | --- | --- | --- |
| D12.1 | Where are lives written? | Conflict: time item 3, "The yearly runner writes the intervals offline"; `where-generation-runs`, "intervals written on change (by the engine once request 19 lands)"; `living-fabric.md`, "Life is computed offline per thing". Follows D1.1: lean in the player, in C#, on change; the past to 1989 may ship as a cache. | about 2 d | D1.1 | plan 3.2, in Python |
| D12.2 | The date? | A shader global, with four clocks: fabric year, day of year, the hour as the sun's position, weather (time items 2, 6). Inside D7.3. | 1 d | evidence | plan 3.2 |
| D12.3 | Lifespans and comparisons? | A part exists from making to removal; a comparison draws the shared instances plus the few parts alive at one date; an earlier chunk stays resident while a comparison needs it (time item 4). Its memory is unmeasured. | in D3.1 | scale test, then step 4 | lifespans House A; comparisons step 4 |
| D12.4 | The change query? | `changes(scope, t0, t1)`: cause, actor, provenance, precision, weight, parts and region per view, plus drift magnitudes (time item 5). It feeds the budgets, highlights, the why-probe, the journal and the readers' key; for 1f a plan diff at two years stands in (inputs 5). | about 2 d | evidence | schema now; step 4 |
| D12.5 | The drawing as a function? | Of (record, fabric date, light moment, weather, view, tier), hashed; the watched-or-jumped test and the diff check (time items 1, 7). | about 1 d each | evidence | the rule now |
| D12.6 | Scene state? | By hour and year from habits and the record, with a fabric-only switch for judging (time item 8); committed to the engine only when it matters (`CLAUDE.md`). Perhaps instance overrides on their own clock, never in maps (ours). | not costed | judgement | LT2 |
| D12.7 | Works in progress? | Large works keep dated phases (hoarding, pit, scaffold), so a jump inside a work shows the site (time item 4). | not costed | evidence | a slot in lifespans now |
| D12.8 | The player's mark? | The guard stays: the fabric's condition never depends on whether anyone watched. Whether the mark is noticeable is Øystein's exploration; an actor on every event (D3.3) keeps it possible. | none | Øystein | none |

### D13. The interface

**D13.1 The pick path for every drawn kind.**
- *Paths:* merged chunks: a chunk-local index per vertex and a table per chunk. Instanced kit parts: (a) the Renderer Shader User Value, (b) our own BRG buffer, (c) depth and position through a spatial index. GPU swarms: tile and seed resolve to the community through the field tile (inputs 3). Skinned people, alpha-tested leaves, terrain and decals each need a path (a poster stack picks the top sheet and exposes those beneath). Street and city levels: P's piece map doubles as a pick map; district: a building id in the block atlas (inputs 2, ours) (`interface-and-inspection` §6, 1).
- *Conflict:* interface §3, "Ids for instanced parts must come from instance data we control or from position"; P §1, the user value "avoids breaking GRD instancing draw calls".
- *Cost:* the picking spike, 1 to 1.5 days (interface, What we should do 2), with test 6: the id at random screen points names the same record as a raycast against full meshes.
- *Settled by* the spike. *Urgency:* ids in the contract at plan 3.1; the spike during the port. *Lean:* (a) for kit parts, since one 32-bit value can index both the facts buffer and the pick table; (b) for swarms.

| # | Question | Evidence and lean | Cost | Settled by | Urgency |
| --- | --- | --- | --- | --- | --- |
| D13.2 | Highlight and focus? | One shared function in every shader of the shared surface layers compares the hover and selected global ids with the part's id: an even lift, no hue, direction or shadow. The focus is a stencil in the existing post pass. Nothing samples neighbours, which breaks the M4's tile memory (interface §3). | in the shaders; 1 d look test | look test, cold readers | shaders at plan 3.4 |
| D13.3 | Reading ids back? | A scissored 64-by-64 id render round the cursor, read back two or three frames late; not a full 1440p id target (14.7 MB a frame, about 0.9 GB/s) (interface §6, our estimate). | in the spike | harness | with the spike |
| D13.4 | Anchors and bounds? | A label anchor and screen bound per record, a head anchor for people, following the lifespan; people, signs, posters and doors also in a CPU list for the bubble snap (interface §6, 6 and 7). | small | evidence | House A; people later |
| D13.5 | The knowledge store? | Between record and screen: what the role has seen, heard, been told and read, with the marks (seen, heard, told, written, inferred, the record, unknown); engine requests for `knownBy` and who told whom (interface §6, 10). The three dials differ here. | 1 d | evidence | the first game; provenance now (D3.3) |
| D13.6 | Labels? | Behaviour rule 10: "No labels, anywhere in the world view or the scenes"; interface: "hover names things"; characters: "a name on approach" (inputs 4, C8). Lean: narrow rule 10 to readings of character; a name is a fact. | none | judgement | before a game |

### D14. Quality tools and checks

| # | Question | Evidence and lean | Cost | Settled by | Urgency |
| --- | --- | --- | --- | --- | --- |
| D14.1 | Who accepts a new golden baseline? | Conflict: P §6, "Only Øystein accepts a baseline. The AI proposes; he accepts on the sheet"; `where-generation-runs`, the new baseline "is accepted on the golden views and a quick strict review". `NOW.md`: look and craft are ours, Øystein judges milestones. `docs/measuring.md` (being written for Monday) keeps P's rule ("only Øystein accepts one; the AI proposes it with its sheet") and renders baselines at 2560 by 1440, one sample a pixel, which settles their size. This week needs at least three new baselines (a fresh export of the gully, the seeds, history in maps), so the rule sets how often he is asked. Lean: a strict review accepts while building; Øystein accepts milestone sheets. | none | judgement | plan 3.0 |
| D14.2 | Generated meshes and git? | Conflict: `CLAUDE.md`, "Large binary files (renders, FBX) go through Git LFS"; `.gitattributes`, "Git LFS uploads are not reachable from the cloud workspace"; P12, generated meshes out of git with a manifest of hashes. Git history is 2.2 GB; 373 MB of FBX in Unity, 272 MB of it stone (plan, Baselines). Lean: rebuild generated meshes, keep a hash manifest and the library parts' sources in git; change `CLAUDE.md`'s Practical line. | about 1 d | judgement | before plan 3.1 regenerates the gully |
| D14.3 | The harness? | Four paths, three lights, A/B switches (Resident Drawer, GPU occlusion, MSAA, the history path, forced levels), gates both ways (P §6). | 3 d | planned | Monday |
| D14.4 | Golden views and motion sheets? | FLIP against baselines from the motion-sheet renderer (60 fps, 1440p, one sample a pixel) and stills at the player's footprint; a swim test and shimmer index (P13; painted P1). | 4 d; 2 to 3 d | planned | Monday |
| D14.5 | Export checks? | Budget per level; each level at most 60 % of the one before; median triangle of ten pixels or more (P1, P13); fits never silent (K5); the kit validator (K4); plan validity; the licence list. | 2 d with hashes | evidence | from plan 3.1 |
| D14.6 | Fact checks? | One framework for `trace_check.py`, `act_check` and the cut check (behaviour), the label check (interface rule 1), the superposition validator (H6), the diff across dates, watched-or-jumped and the time-jump test (ours). | each with its first user | evidence | from plan 3.2 |
| D14.7 | Variety? | One expressive-range tool (K §4, P §6; inputs 2, overlap 14); counts per level. | 1 d | evidence | the first library |
| D14.8 | Cold readers? | Model readers (decided). Noted, not reopened: face recognition and viewer bias are human perception (inputs 4, C10); hover, pad and toggle need people. People read in the engine's human test (`foundations.md`). | none | decided | none |

### D15. Scale

| # | Question | Evidence and lean | Cost | Settled by | Urgency |
| --- | --- | --- | --- | --- | --- |
| D15.1 | On demand, or a shipped cache? | The same code for first load and streaming; chunks made near the camera and cached by hash; if demand outruns build, ship the start date's cache (tens of MB a kilometre) and rebuild only what play changes (`where-generation-runs` §5). | in D15.2 | scale test (its measurements 1 to 3) | before House A |
| D15.2 | Chunk format and cache? | Binary, not FBX; keyed by the hash chain; the world on disk is the record plus the libraries. Eviction and the cache's limit are unstudied. | 3 to 5 d | judgement | the week after the port |
| D15.3 | Disk and memory per kilometre? | History maps 4 to 18 MB or about 280 MB for a kilometre of fronts, by density (inputs 2, ours); 70 to 140 KB of maps a house (inputs 1); about 50,000 instance records and 30 MB of maps a kilometre of wall (P); fields per km² unknown. The scale test needs synthetic buffers and maps (inputs 2, section 4, item 2). | in the test | scale test | Tuesday |
| D15.4 | Build time? | About 13 houses a second at test quality, about 20 s a kilometre of street, about 2 h for 100,000 on one process; final quality unknown until House A; a flight 67 s (inputs 2). | in the test | scale test; House A | Tuesday |
| D15.5 | What does a new city's pack bring? | Not studied as a list (gap 8). From the studies (ours): metrics table and era shelves, material records, part libraries and era content, geology and climate vectors (ice, foliation, joints, tide, fetch, splash height), lamp kinds, letter styles, the field guide, population and dress tables. Carried over: kinds, stages, runner, shaders, systems, checks. | not costed | judgement | the boundary now |
| D15.6 | People at runtime? | Generated from identity numbers and cached by a hash of record, age step and outfit (`characters` §7.1.10); uncosted in the player. | not costed | harness at step 5 | step 5 |

### D16. Process

| # | Question | Evidence and lean | Urgency |
| --- | --- | --- | --- |
| D16.1 | The port against the week? | The studies' estimates for the gully's port add to 16 to 22 Opus-days; the plan gives three (inputs 2). Keep the cut line: by Friday, expect the stages split, the hashes unchanged and history as a function. One step comes first: the committed stairs FBX is not what today's generators make (hash `babe291de7a32bb1` against `91e31a9c9d6f7786`, vertices up to 4.9 cm apart), so the gully is exported again and its golden views accepted before plan 3.0 (`docs/measuring.md`, Mesh hashes). | now |
| D16.2 | Python or C# this week? | Python; the split is the port's specification (`where-generation-runs`, What is ported 3). | now |
| D16.3 | What does the architecture supersede? | "Life is computed offline per thing", "the city tier bakes the life into the merged mesh's vertex data" and fields "redrawn by decade" (`living-fabric.md`); "only the chunk a change touches is rebuilt offline" (`town-system.md`); "runs no generation" (K §6); "years since it was applied" (`building-system.md`); the tier table (`foundations.md`); the brush's one world size (`visual-direction.md`; painted P5); "nothing repeats" per piece (`research/stone.md`), if D6.4 (c); the LFS line (`CLAUDE.md`); the skills `blender-generators` (hand-modelled `.blend`, a 1 m grid) and `unity-conventions`. | with the architecture |
| D16.4 | Which gap passes, and when? | Each just before its step, none changing an architecture decision: 1989 dress and hair, editing motion against video (before people); routines, time use, proxemics; opening sizes, pitches and eaves from Stavanger byarkiv, Willmott's slides, City Sample's interiors, SSB table 14320 (before step 2, downloads with Øystein's OK); Ghost's grass deck (before the placer) (inputs 3 to 5). | per step |
| D16.5 | The pre-mortem? | Before the gully port, on Tuesday (`CLAUDE.md`; plan). | Tuesday |
| D16.6 | What changes in existing work? | The gully and walls are ported, keeping their facts, rules, style and review findings (plan 1e); the stairs' five open faults wait for the new foundations (ours, from the order of work). The birches get cut cards, cores, real leaves near and wind-ready marks (D9.5, D9.6). The houses start with House A made by the generator with pins (K11), then twelve from the same parts; the window and its surround are the first final part (`wooden-town-architecture`, parts ranked). | with each step |

## 3. The one data contract, assembled

The union of what every study asks a part or thing to carry, de-duplicated. **[C*n*]** marks a conflict, listed after the tables. Sources: inputs 1 to 5, "What every part must carry"; `interface-and-inspection` §6; `where-generation-runs`, What we should do; `time-on-screen`, What the building blocks must carry.

| Holder | Carries |
| --- | --- |
| **Every record** (thing, part, person, plant, sign, room, light, garment, trace) | A string id typed by prefix, never reused (`engine-contract.md`); kind; its place among the five kinds on screen; provenance (`authored`, `derived`, engine) and precision; a lifespan (made, removed, each with its event); events with cause, actor, precision and weight; links up the hierarchy (part, thing, group, place); a label anchor, screen bound and region per named view; keeper and care; pins (semantic anchor, provenance) and recorded reseeds. **[C3]** |
| **Part definition** (per family) | `made_as` (fixed or fitted), era range, size ranges, fit modes and stretch limits, a named pivot at its true base or hinge, sockets and the families they accept, its removal mark, variant count; per level its error, triangle budget and shadow role; a motion class per element **[C6]**; intrinsic channels (library parts); each procedural mark's smallest feature; an anchor class derived from the motion class; a motion-vector pass in every shader that moves vertices (painted §7). |
| **Plan instance** | Part id (a semantic path), variant, seed (SplitMix64 of the id), placement in integer millimetres, the fit used, the placing event, its chunk id, its levels; life intervals (construction, material, origin, reset years, rates, age offsets **[C2]**). |
| **Slot** (opening, socket, surface region, pane) | Position, size, year and cause; fills over time (part, event, years, fit); each removal's mark; accepted families; edge reference. Windows: surround, sash era, inner window, each pane's glass kind and year, a dressing stack (year hung, state by hour), a room reference. Signs: method, maker, English text, letter style, light and hours, coats, state, claims. Coats per facade (colour, year, paint kind, primer) **[C7]**. Cladding: profile, year, scope, corner type. Roofs: form, pitch, eaves and verges, covering. Plinths: height on each side of the slope. |
| **Per vertex** | Position, normal; a per-piece metric grain UV; an atlas address for the maps; a piece index into the chunk's table (seed, ids, reset years, material, pick); face kind; edge distance on dense trims; a mark coordinate, run-continuous where the paint should flow **[C4]**; for flexible parts, element index, depth and flutter weight; for deforming parts, rest position and normal; for wind-moved parts, the undisplaced position; for worn fitted treads, the hollow's rate and gradient; the chunk-local pick index. Light bake per vertex only if D7.1 says so **[C5]**. **[C1]** |
| **Per texel** (history and place maps) | Per process, rates or the fields that make them: water (lands, runs, drips, pools), flow rate, end of flow, rain shelter, height above ground and ledges, splash, sky and ground seen, openness, weather exposure, sun dose, wind and salt facing, deposit per source, feet, hand zones; carriers (source, amount, removal year); age offsets per interval; a bent normal; at the street level and beyond, piece id, joints, height and roughness with the relief folded in. **[C2] [C5] [C9]** |
| **Per GPU instance** | Transform; a 32-bit user value or BRG offset into a facts buffer (years, care, season, hue, wind phase, coat table) **[C8]**. Swarms carry only transform, part and species, seed and rank, wind phase and field tile (plants §8). |
| **Per chunk and level** | Id and bounds, cut at piece boundaries; levels with their error and counts; a caster proxy; field-tile indices and maps; a pick table (index to record id and part path); the lifespans a comparison needs; its hash; a material with a texture-array index. Every level keeps the close level's pivots, element ids, phase seeds, mark coordinate, seed and history address. |
| **Edges and sockets** | Foot lines as hard or soft breaklines, and footprints; joint lines and growth faces with their facts (width, depth, soil, water, feet, years since laid or swept, lime or acid), copings and gutters as traps; climbable regions, keep-clear zones, trellis sockets; drip edges and splash lines; light sockets (position, cone, kind, era, shadow flag; a window's spill and cookie) and an emission group tied to its fact; emitters (position, direction, feeding fact); hinges (axis, limits, side, closed rest, the fact that opens it); hull points, waterline, draught, berths, cleats and bollards; affordances (treads, walking line, landings, handrails, sit, lean, stand and serve points, sills, shelter, a lamp's cone, grips); what it writes into fields (rain shadow, drip line, damp foot, shelter) and what it reads (ground map, sky map, field tiles, wind). |
| **Natural stone and made ground** | Rock kind, the three vectors, years bare per face, a cut's drill era, how far soil has climbed; each made-ground act's outline, kind, target surface, edge, year, founder and plan unit; each water body's depth, seabed, shore distance and exposure; each quay's tide band. |
| **People** | Identity numbers set at birth (appearance seed, parents, features, pigments, grown height, build, gait seed) **[C10]**; the `game_engine` skeleton through Humanoid, about 20 bones far, up to four weights a vertex; measurements (leg, hip, eye, shoulder, sitting height); sockets (hands, head, back, hips, soles, eyes); flex weights on hems and hair ends; a face near only; the same height, build, hair mass and outer colour at every level; a head anchor; their own pick path. Garments carry the fabric record with owners, and history maps. |
| **Plants** | A record, parts by level, wind data per element (pivot, stiffness, phase), season ranks, an opaque core. |
| **World state** | Fabric date, day of year, sun, weather, wind, tide: one record, hashed. |
| **Material record** | As D4.2. |

**Conflicts in the contract:**
- [C1] The vertex layout. FBX from Blender "carries 2D UV sets and one usable vertex colour" (animation); Unity has eight UV channels of up to four floats, plus colour. Nobody allocates them (inputs 4, C9). Our tally: no family needs more than about twelve floats beyond position and normal (a worn tread: grain, atlas, piece, face kind, mark, hollow; a branch: mark, element, flutter, undisplaced position; a garment: grain, atlas, rest position and normal, mark). So the choice is one fixed layout or a semantic channel spec mapped to slots per family. Under D1.1 (b), meshes made in the player write any layout through `MeshData`; only library parts cross FBX, through the importer and a sidecar (D10.3).
- [C2] The map's contents: states or inputs (D5.1); resets per piece or per texel; offsets when a rate changes (D5.4).
- [C3] The record id through merging and instancing: a vertex index and chunk table when merged, the user value or a BRG buffer when instanced, the piece map at the street and city levels, the block atlas at the district level, tile and seed for swarms, a separate path for people (D13.1). Ids must also survive regeneration (D1.10, D3.2).
- [C4] One mark coordinate or two: run-continuous for the brush (painted §7) against UV0 per piece at "its own offset and turn" (materials §4) (inputs 1). Perhaps both: grain per piece, marks per run.
- [C5] The light's bake: per vertex at every level (light §9) or in the maps (P §5) (D7.1).
- [C6] Motion and anchor classes: two vocabularies, one field (D10.1).
- [C7] Coats: a year, or "years since it was applied" (D4.3).
- [C8] Per-instance data under the Resident Drawer: the user value, or our own BRG (D13.1).
- [C9] Field resolution: about 6 cm tiles (P) against 0.5 to 1 m (land) (D8.1).
- [C10] The gait seed: in identity at birth, or in a per-year record (D10.8).

## 4. Conflicts across studies

| # | Conflict | Where | Settle by |
| --- | --- | --- | --- |
| 1 | Generation in the player: K §6, P and `living-fabric.md` against `where-generation-runs` | D1.1, D12.1 | judgement on evidence; Øystein's scope for the port |
| 2 | Generators making geometry: `CLAUDE.md` and the skill against K §6 | D1.3 | judgement (the rule's wording) |
| 3 | History maps hold states (materials) or inputs (history, time, P) | D5.1 | evidence; the gully's years sheet |
| 4 | One history path (materials, plan) or two (P); vertex data at the city level (`living-fabric.md`) | D5.2 | look test (A/B, FLIP) |
| 5 | Texel size: 1 cm (P) against 2 to 8 cm (materials); field tiles 6 cm (P) against 0.5 to 1 m (land) | D5.3, D8.1 | scale test with synthetic maps; A/B |
| 6 | City level as "albedo with history baked in" (materials) against "Bake inputs" (P) | D5.1 | evidence |
| 7 | Rust runs as decals (materials) or carriers across parts (history) | D4.1 | judgement; the handrail post |
| 8 | Levels by Decimate (materials), by the generator (P), by Mesh LOD (K); Mesh LOD editor-only (tools) | D6.2 | the afternoon test; A/B at switches |
| 9 | The merge unit: thing (K), 3 to 5 m (P), 64 m (land), runs (foundations) | D6.3 | scale test |
| 10 | Repetition: `NOW.md` against K §7, P and the plan; archetypes, rooms, grain, strokes | D6.4, D10.2, D11.3 | judgement, shown to Øystein; look test; repeat check |
| 11 | Five sets of tier boundaries; where fades sit (P against painted §5) | D6.1 | evidence; motion sheet |
| 12 | The frame budget: 4 million (P) against 2 million (`foundations.md`); the split | D6.5 | harness |
| 13 | Trees on the M4: P §3 against plants §7 | D9.5 | harness |
| 14 | The cross-fade dither: painted against P | D6.6 | motion sheet |
| 15 | Temporal antialiasing: painted against P; plants' hashed alpha; GTAO and SSR | D7.2 | harness, motion sheet; the rule by judgement |
| 16 | The light's bake per vertex (light) against a slim vertex (P) | D7.1 | judgement |
| 17 | Ids under the Resident Drawer: interface §3 against P §1 | D13.1 | the picking spike |
| 18 | Mesh hashes quantised (P) or bit-exact with tolerance across languages (`where-generation-runs`) | D2.3 | evidence |
| 19 | Coats as "years since" (`building-system.md`) against the date as a global (time) | D4.3 | evidence |
| 20 | Baselines accepted only by Øystein (P, `docs/measuring.md`) or by strict review (`where-generation-runs`, `NOW.md`) | D14.1 | judgement |
| 21 | Git LFS (`CLAUDE.md`) against no LFS from the cloud (`.gitattributes`) and generated meshes out of git (P) | D14.2 | judgement |
| 22 | Two class vocabularies (painted, animation); channels nobody allocates (animation, painted, characters, materials) | D10.1, section 3 [C1] | judgement |
| 23 | One mark coordinate per run (painted) against per piece (materials) | section 3 [C4] | judgement; motion sheet |
| 24 | People's levels: own shape (characters) or archetypes (animation); walking speed with age (characters §4 against animation §1) | D10.2 | people step: measurement and the recognition test |
| 25 | The gait seed's owner (characters, animation against behaviour) | D10.8 | judgement |
| 26 | Faces: swapped textures (`living-world.md`) against shape keys (animation) | D10.9 | look test at step 5 |
| 27 | Labels: behaviour rule 10 against "hover names things" | D13.6 | judgement |
| 28 | Smooth or stepped for flags and laundry: animation against `what-moves.md` and `visual-direction.md` (inputs 4, C1) | ours, on frames | motion sheet |
| 29 | A mat's edge as mesh (plants) or shader (land) | D8.6 | the corner's years sheet |
| 30 | Shops as spot lights (`TownLights.cs`) against spill from a buffer (fronts, light) | D7.5 | evidence; the harness's light counts |
| 31 | The resolver deletes cells; three studies say never delete | D3.1 | evidence |
| 32 | A seeded mansard against the fact rule | D11.6 | evidence |
| 33 | One world state, two winds, one lamp list, one ground map (light, land, plants overlaps) | D7.3, D8.1, D8.7 | judgement: owned once |
| 34 | Three budgets per view (living fabric, behaviour, animation) | D5.9 | judgement: one mechanism |
| 35 | English signs against Norwegian names in fixtures and streets | D11.4 | Øystein (the reach of his rule) |
| 36 | Model readers against human perception for faces (inputs 4, C10) | D14.8 | decided; people beside in the engine's human test |

## 5. The three example games

`docs/plan.md` asks that no decision lock out a manager (a football club or a band, with a world around it), an exploration game, or a family across generations. The three dials (control, influence, knowledge; `living-world.md`) and `town-plan.md`'s scenario table say what each needs.

**A manager.** Needs its own people deeply and the town thinly; crowds at matches and gigs; rooms (the rehearsal loft, the clubhouse, a pub's back room); weekly posters; seasons to years; the club's or band's places changing (a new stand, a converted loft); commands the engine accepts or refuses.
- D1.1 (a) or (c) locks it out of a new stand or a rebuilt loft; (b) keeps it.
- D6.4 or D10.2 read strictly at the grain of people would make a match crowd of thousands unaffordable; far figures with their own identity numbers on shared meshes keep it open, if measured.
- D4.1 with posters only in baked maps would rebake a wall every week; posters as records and decals keep it cheap.
- D11.3 as a window-only box would block walkable rooms at step 8; the room record must be able to grow into geometry.
- D13.5: the knowledge store as data per role, not hard-wired to the observer.
- D1.5 and D1.8: kinds and metrics as data, so a stadium or a clubhouse is a new kind, not timber houses stretched.

**An exploration game.** Needs roaming at eye level in any lane, from any angle; streaming at walking pace and on fast camera rises; traces that read (criterion 1) and secrets with dates; the why-probe and the journal; night.
- D6.5 and D15.1: budgets and streaming must hold at eye level everywhere, not only at the judging stops; how fast the camera may rise before streaming shows is unmeasured (inputs 2, Unknowns).
- Collision and navigation are unstudied (gap 6). An avatar needs colliders and a walkable mesh per chunk, rebuilt with the chunk; a worn tread that moves by the date in the vertex shader (D5.2 c) needs its collider to read the same date.
- D3.2 and D13.1: journal entries must still point at the right step after rebuilds and across years.
- D7.5: night exploration sees more lamps per camera than Forward+ allows, unless spill and tiers hold.
- D5.9: the history budget rations what shows unasked; what it hides must stay findable through the card and the probe.

**A family across generations.** Needs play over decades; houses built, extended, pulled down and rebuilt; new roads and fills; gardens planted and grown; people born with their parents' looks, ageing and dying; comparisons across decades; homes (engine #59); eras after 1989.
- D1.1 (a) or (c) locks it out: extensions and rebuilds are fitted geometry made in play.
- D5.1 (a) rebakes every surface on every jump; (b) makes thirty years a uniform for drift.
- D8.2 with ground acts offline only locks out a new road or a filled garden; acts must run in the player.
- D9.7: a tree planted in play cannot grow if growth is offline only; step 7 must measure growth in the player or a precomputed timeline per plausible site.
- D2.1, D3.2: seeds and ids stable for a part's whole life, across sixty years.
- D10.2 and D15.6: people generated at runtime from identity numbers, with parents in the record (D3.4) and age keys to 80 (`characters` §4).
- The eras after 1989 are content and scope (Øystein), not architecture; nothing in the register assumes a final year.

## 6. Gaps that would change a decision

| # | Gap | Decisions | What closes it |
| --- | --- | --- | --- |
| 1 | The language of contracts both Python and C# implement | D1.6 | a half-day craft scan (schema code generation, binary schemas) against the parity test's needs |
| 2 | Ids end to end: minting, part paths, draw-time indices, survival through regeneration | D3.2, D13.1 | a design note in the architecture, tested by the picking spike |
| 3 | Per-instance data and picking under the Resident Drawer; `SV_PrimitiveID` on Metal | D13.1, D6.7 | the picking spike (1 to 1.5 d) |
| 4 | The runtime floor in a built player (chunk load, `MeshData` writes, map compression), the demand rate, the Python-to-C# ratio | D1.1, D15.1 | the scale test's extra measurements 1 to 3; the resolver's parity probe |
| 5 | Disk and memory of maps and fields per kilometre at each density | D5.3, D8.1, D15.3 | synthetic maps in the scale test (not yet in the plan) |
| 6 | Collision, navigation and physics data per part and chunk | the contract; the exploration game | no study; a short craft study before the grey walker or the people step |
| 7 | Rates that change mid-life | D5.4 | designed in the architecture; the gully's years sheet |
| 8 | What a new city's pack must bring | D15.5 | a list in the architecture, tested by the first foreign-pack part (`systems.md`, How a new thing joins) |
| 9 | Whether a 2 cm map draws as crisp as the 8 cm vertex grid; BC7 blocks in a smooth field | D5.2, D5.3 | plan 3.2's A/B |
| 10 | How Mesh LOD treats UVs; decimation's 13 mm outliers at a switch | D6.2 | the afternoon test; A/B at plan 3.4 |
| 11 | The cross-fade dither without TAA | D6.6 | a motion sheet at the first switch |
| 12 | The birch's overdraw, alpha-to-coverage, lights per camera, GTAO and SSR without temporal accumulation | D9.5, D7.5, D7.2 | the harness |
| 13 | The memory of two chunk versions in a comparison | D12.3 | the scale test, then step 4 |
| 14 | A carrier's bake across parts | D4.1 | H4's first case, the handrail post |
| 15 | Final-quality build time per house | D1.1, D15.4 | House A |
| 16 | People's share of the frame; skinning and crowds on the M4 | D6.5, D10.2 | the grey walker's frame cost; the crowd tier at step 5 |
| 17 | Cache eviction and the streaming radius | D15.2 | with the chunk format; the scale test's demand rate |
| 18 | What parts carry for sound (an acoustic class for footsteps, reverb) | D4.2 | the sound study before scenes (`systems.md`); a slot in the material record now |

Coverage gaps that add record kinds but no architecture (street things, vehicles, boats, animals; rooms; weather and effects; the camera) are studied before their steps (`systems.md`, Research coverage); D3.4 admits their kinds.

## 7. The order of building it implies

Hardest to change first: contracts and data formats, then measurement, then scale, then one kind end to end, then parts (`CLAUDE.md`, Working in the right order). Set against `docs/plan.md`:

| When (plan) | What | Decisions it fixes | Study estimate (Opus-days) |
| --- | --- | --- | --- |
| Monday, tools | Harness, golden views, mesh hashes, export checks, motion sheets | D14.3 to D14.5, D2.3 | 3 + 4 + 2 + 2 to 3 (P13; painted P1) |
| Monday, architecture | The stage map; contracts as schemas (kind, part, plan, slot, intervals, channel spec, chunk, hash chain); ids; map contents; the maps registry; world state; motion contract; affordances; pick ids; what is superseded | D1.1 to D1.8, D2.x, D3.1 to D3.5, D5.1, D5.4, D7.3, D8.1, D10.1, D10.3 to D10.5, D13.1, D16.3 | half a day for the interface's needs (interface, What we should do 1); otherwise judgement |
| Tuesday | The scale test with its additions: the runtime floor, demand rate and cache (`where-generation-runs`); synthetic maps at both densities; a chunk loaded and rebuilt in a built player; the birches; lights per stop. Then the pre-mortem and review | D1.1 (cache), D5.3, D6.3, D6.5, D8.1, D15.1 to D15.4 | not costed |
| Wed to Fri, plan 3.0 to 3.4 | The gully in Python: first a fresh export and accepted baseline (D16.1); then seeds; stages, kind, channels, motion contract, hasher; history into maps against the date; material records; levels, chunks, proxies. The picking spike and the grey walker ride on it | D2.1, D1.4, D1.5, D5.2, D5.3, D4.2, D6.1 to D6.3, D6.5, D6.6, D6.7 (shaders), D6.8, D13.1 | 16 to 22 in all (inputs 2), plus 1 to 1.5 and 1 to 2 |
| The week after | The C# core, if Øystein accepts: resolver parity, chunk format and assembler, the stone stages | D1.2, D15.2 | 1.5 to 2 + 7 to 11 + 6 to 9 |
| 1c | The light's lookups and occlusion; then the sky model and rig as layers | D7.4, D7.7, D7.3 | 1.5 to 3; 6 to 9 |
| 1d | Land layers and acts, mesh terrain, fields, the knuckle | D8.2 to D8.5 | 11.5 to 13.5 |
| 1e | Walls and birches re-fitted; the brush re-anchored and octave-stepped; trees ready for wind | D1.11, D9.1, D9.5, D9.6, D5.8 | 3 + 1 to 2 + 1 to 2, plus the re-fits (uncosted) |
| 1f, in parallel | Clay houses at four years, once the fixtures gain House B and its fire, events after 1988, a reversal, and no seeded mansard | D11.6, D12.4 (a plan diff stands in) | 1 to 2 weeks (plan) |
| Before House A | The record migration, metrics and part definitions, the ground floor, the linear grammar, pins, libraries and BRG, coats and boards, decals, the house builder in C#, the archive sizes (downloads with Øystein's OK) | D3.1, D1.7 to D1.11, D11.1 to D11.5, D6.7, D4.1, D4.3, D4.4 | about 26 to 36 |

**Reliability of these estimates.**
- Most are guesses. Inputs 2 finds of K that "Every cost is a guess"; `history-in-things` and `behaviour-on-screen` give none; `where-generation-runs` marks its own as (ours), extrapolated from 2019 laptops. P's are the best grounded.
- They read like a human team's days. Summed to House A they come to roughly 95 to 130 Opus-days (ours, overlaps not removed), against 7 to 11 weeks of the usage limit for steps 1 and 2 in the plan's rough sizes. The plan records the stairs going from nothing to "close", with upkeep, wear, water and growth, in about a day and a half (`docs/plan.md`, Rough sizes). Building compresses a great deal at our pace.
- What does not compress: convergence loops (the stairs took eight rounds, the gully six strict reviews), measurement runs (a flight's 67 s, the clay heart's six minutes, the harness's paths), Fable's share of the weekly limit, and Øystein's judging.
- No ratio can be computed yet: the usage log has two lines. Logging each step's actual use next week (step, model, tokens, review rounds) against the figures above gives the first real ratio, which the plan already asks for.

