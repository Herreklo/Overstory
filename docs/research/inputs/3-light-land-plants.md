# Inputs 3: light, land and plants

A digest of three craft studies for the building-blocks architecture (`docs/plan.md`, What the architecture decides). It decides nothing; it sets out the evidence so Monday's Fable session can decide from it.

The studies, and the short names used below:
- *Light*: `docs/research/lighting-and-colour.md`;
- *Land*: `docs/research/land-rock-and-water.md`;
- *Plants*: `docs/research/ground-cover-and-plants.md`.

Code claims were checked at commit `60f61bd` (`StreetLooks.hlsl`, `Tree.shader`, the URP assets, `tree.py`, `bake.py`, `growth.py`, `blender/blockouts/`). Every one checked held.

## 1. Lighting and colour

### In short

- Physics underneath, art on top, acting on the whole light; light painted into colour breaks when the light changes (§1).
- The four light debts share one cause: the shade function guesses what a face sees. Three lookups end them: the sky's radiance, the ground a face looks onto, the town it faces (§7).
- Our sky map is runtime sky occlusion that follows a rebuilt town; Unity's probe volumes bake in the editor (§2).
- The rig is about 65 typed settings an hour. It should become six layers (world state, derived light, art keys, style, mood, lens), the first three a hashable record (§7, §8).
- Night is thinnest: 403 lights against Forward+'s 256, no lamp shadows, lamp reflections about twenty times too dim, the style pass after the dither (§3, §4, §7).

### Against the bar

| Test | Finding |
| --- | --- |
| Primary sources | Strong: Patry on Ghost (SIGGRAPH 2021), Hillaire, Jimenez's GTAO, Lagarde, Gjøl, Sea of Thieves, Imageworks, Yang, Unity's docs and our URP 17.6 source. Not opened: Ng's Firewatch talk, Bauer's RDR2 slides, INSIDE, Disco Elysium's and The Last of Us's talks (Gaps). |
| Marking | Good. One load-bearing claim is (unverified): that thin cloud brightens round the hidden sun (§2), on which the drizzle's bright side rests. |
| Concrete | Strong. Checked: `OS_TownSky` makes 64 sky-map reads; the lamp highlight is un-normalised Blinn-Phong (exponent about 1,700 at smoothness 0.97); `DirectLightingStrength: 0.25`; the light cap is 256. |
| Thin | §6 (how lighting artists work) is mostly secondary. It predates the M4 (committed 21 October): no cost is set against a tile-based GPU. |
| Stale | Its Gaps say `foundations.md` lists two debts; it lists four. Its five questions for Øystein are now ours (`NOW.md`: night sky, lamp glass and tonemapper are look questions; the architecture is delegated). |

**Verdict: meets the bar, with gaps that change no decision.** The M4 gap sets numbers (how many shadowed lamps, whether GTAO earns its pass) that the harness measures. The structure does not hang on them.

### Decisions it proposes

| Decision | Why | Cost | Depends on | Alternatives weighed | Status |
| --- | --- | --- | --- | --- | --- |
| Parts carry visibility, never light: sky, ground, openness, weather exposure per face, at every tier, impostors included | an impostor baked lit freezes an hour (§7, §9) | exists as vertex rgba; maps and impostors new | where bakes live per tier | lightmaps, APV (§2) | consistent with `foundations.md` |
| A bent normal (two channels) from the same ray fan | directional ambient without guessing; Ghost's 25% boost (§1, §9) | small | the same carrier | today's typed horizon colour | new |
| Three lookups in `OS_ShadeP`: sky radiance from a model; the seen ground (sun shadow at the ground point in front, its albedo by season and wet); the seen town (is the wall `OS_TownSky` hits lit?) | the four debts (§7 table) | 1–2 days bounce; 3–5 sky model | a ground albedo map; the sky map | more guesses; Surface Cache GI (preview) | `foundations.md` names it the lasting fix |
| Occlusion on indirect light only: GTAO, none on the sun, multi-bounce with albedo, specular occlusion from bake × town × AO | Jimenez 2016, Frostbite 2014, in our SRP core (§2, §7) | 0.5–1 day | GTAO feeding `OS_ShadeP` (untested) | today's eased SSAO | new |
| The light in six layers, one owner each; layers 1–3 one record, hashed and replayed | Ghost, RDR2, Imageworks' key rigs (§1, §6, §8) | 3–4 days | a world-state record | hand-typed rigs (§7) | delegated, ours |
| Lights in tiers from sockets: shadowed spots near (perhaps 8–16), unshadowed in the street tier, emission and glow map beyond; `FogLights` binned by tile | 403 lights against 256 (§3, §7) | 5–8 days, steps 3 and 6 | light sockets; M4 counts | raise the cap | numbers unmeasured |
| No baked probes; reflection probes placed by the town generator, relit a few a frame; far shadows and horizon angles precomputed from the height map | Ghost's 235 probes; a 30 m knoll at 8° shades 210 m (§2, §7, §9) | 3–4 days | the sky map's rebuild | APV; Ghost's far shadow atlas | new |
| Lamp kinds drain colour (sodium, mercury); normalised specular; style pass baked into the Color Lookup table; dither at the last write; exposure from illuminance; a chart and debug views of the shade's terms | CRI facts (§3); Gjøl; Patry's exposure-albedo loop (§4, §7, §8) | about 4 days | light records | an orange multiply; typed exposure | tonemapper ours, on frames |

## 2. Land, rock and water

### In short

- A height field is the soft ground only. Steep and crisp ground is meshes over it, and the ground stops along breaklines at every wall, kerb, quay and rock (The bottom line 1, 5; §1).
- This coast is ice-scoured phyllite. Every rock follows one ice direction, one foliation strike and dip, and the pack's joint sets (§1, §2).
- The land has a dated history: natural ground, then made-ground acts (cut, fill, terrace, quay apron, blast), each with a year and an edge (§5, §6).
- Fields per chunk (soil depth, flow, depressions, wetness, wind and salt, sun dose, made ground, feet) do what painted masks do elsewhere (§6).
- The harbour is ripples: a Gerstner sum sized by wind and fetch, opaque water coloured by baked depth, lamp columns from the lights list (§3).

### Against the bar

| Test | Finding |
| --- | --- |
| Primary sources | Good: Galin's review, Priority-Flood, Esri, CityEngine, Frostbite 2007, Ng's slides, van Muijden's Horizon deck (its map names quoted, the PDF in its sources), Tessendorf, Finch, Vlachos, Boat Attack, NGU 2024/034. Not opened: Ghost's landscapes, The Witcher 3's terrain, Breath of the Wild's CEDEC talk, Battlefront, Brucks (Gaps). |
| Marking | Good, with (ours) on arithmetic. Far Cry 5's cliffs rest on third-party notes, marked secondary. |
| Concrete | Strong. Checked: the clay ground is a 1.5 m grid in the heart, 6 m and 60 m beyond; `carve()` and `ground_walls()` are undated. The ring arithmetic holds. |
| Thin | Written before the M4: it sets the land against "a whole frame's 4 million" triangles (§1); the frame is now 2 million, so 370,000 before culling is about a fifth (ours). No craft source for towns on slopes beyond CityEngine (Gaps). Water reflection costs unmeasured. |
| Stale | Its question on bedrock is decided (phyllite). Its water reference board waits on Øystein's download OK. |

**Verdict: meets the bar, with gaps that change no decision.** Each main choice stands on two or more primary sources: mesh terrain with breaklines (Galin, Esri, Firewatch), layers with dated acts (Galin, CityEngine), fields (Horizon, Frostbite), rock as generated parts (Firewatch, the joint-control studies). The unopened talks would add detail, not reverse a choice. The unsettled facts (ice direction, dip, tide) are pack values; the architecture needs their slots.

### Decisions it proposes

| Decision | Why | Cost | Depends on | Alternatives weighed | Status |
| --- | --- | --- | --- | --- | --- |
| Natural ground as layers: bedrock, regolith (thickness and kind), landforms (outline, rock kind, ice vector, foliation, joints), water (sea level, tide, streams, seabed) | layered fields (§1, §6) | ½ day pack facts, 2 days split | the pack | one `heights()`; erosion simulation, the wrong process here | in scope (`plan.md`) |
| Made ground as dated acts (outline, kind, target surface, edge treatment, year, plan unit), applied in date order | CityEngine stores deltas over the original (§5) | in the 2 days | plan units; the living fabric's record | undated `carve()` | in scope |
| Mesh terrain: 64 m chunks, constrained triangulation with breaklines, holes under paving and houses, rings 0.5/2/8/64 m, skirts, a coarse caster per chunk | Unity Terrain stretches on cliffs, holds no breaklines, misses the Resident Drawer (§1 table) | 3 days | every part's foot line | Unity Terrain; a uniform grid (6 M triangles) | in scope; agrees with performance |
| Fields per chunk at 0.5–1 m in the heart, 2–4 m beyond | Horizon, Frostbite, Wildlands (§1, §6) | 2–3 days | layers, acts, feet | painted masks; per-part bakes | new |
| Natural stone as a kind: a volume cut by joints, leaned by foliation, smoothed and plucked by the ice, chamfered by kind; cut faces dated with drill marks by era | Firewatch's planes, Gurney; geo365 (§2) | 4–5 days, the knuckle | pack vectors; history maps | sculpted; scanned (light in the surface); Far Cry 5's slope cliffs | in scope |
| Parts meet the ground by data: foot lines as breaklines; a top-down ground map read at every foot; a strata tint under unloaded rock | Far Cry 5 (secondary); no RVT in URP (§2) | in items 4, 10 | the ground map | Unreal's RVT | new |
| A ground shader on `OS_ShadeP`: few materials chosen from the fields, crisp thresholded edges, hex-tiling, a far colour bake | Frostbite, The Witcher 3 (§1) | 3 days | the fields | Unity's four-layer splat | conflict 1 below |
| Water: opaque meshes with baked depth, seabed and shore distance; 8–12 Gerstner waves from wind and fetch; SSR; boats' heights on the CPU; lamp columns from the lights list; tide and shore bands as derived facts | fetch arithmetic (ours), Finch, Minnaert, MarLIN (§3, §4) | 4 days + 1–2 for columns | world state; the coast polygon | FFT; HDRP water; Crest URP (paid); refraction; planar (only if SSR fails) | new |

## 3. Ground cover and plants

### In short

- On the M4, opaque against alpha-tested decides everything: hidden-surface removal skips what opaque fragments hide, but every alpha-tested layer is shaded (Apple, WWDC 2020; §6).
- Near ground cover is opaque strokes grown on the GPU from the fields, thinning into the ground's colour, which is measured from the near tier (§1).
- The birches are probably the dearest pixels: up to 4,200 eye-facing cards, of the order of fifty layers a pixel. Measure, then cut cards to outlines, add opaque cores, test a depth pass, real leaves within 8 m (§7).
- Five kinds (films, mats, tufts, plants, litter) and one placer: present = potential(fields, facts, date) > rank(seed) (§8).
- Restraint is a fact: kept streets carried about 1.4% weed cover a year after herbicide stopped (Melander 2009; §2).

### Against the bar

| Test | Finding |
| --- | --- |
| Primary sources | Good where it matters: Apple's WWDC 2020 sessions, Frostbite 2007, Outerra, AMD, Ng's slides, Tiny Glade's posts, Humus, Castaño, Zotz, RHS, SNL. Not opened: Ghost's grass deck, Horizon's placement and vegetation decks, Uncharted 4's technical art; search ran out before Genshin, Sable, The Witcher 3 and others (Gaps). |
| Marking | Good. Ghost's blade figures (unverified), Breath of the Wild (secondary), the fifty layers (ours). |
| Concrete | The only one of the three written for the M4. Checked: `max_cards=4200`; `Tree.shader` at target 3.5 in the AlphaTest queue with alpha-to-coverage; MSAA 4×, Resident Drawer off; `growth.py` per vertex. |
| Thin | Hedges, climbers and gardens have no game craft source (§3). The far colour by view elevation is untested (Gaps). |

**Verdict: meets the bar, with gaps that change no decision.** The unopened decks would refine tuning, not the shape: compute placement from fields, opaque near, a hand-over to the ground's colour and no cast shadows each rest on primary sources. The land study appears to have read the Horizon deck this one could not. What could change the trees' re-fit is measurement: the birch's overdraw, whether alpha-to-coverage defeats hidden-surface removal, and a leaf depth pass's cost. Ghost's grass deck is worth reading just before the placer (with Øystein's download OK), not on Monday.

### Decisions it proposes

| Decision | Why | Cost | Depends on | Alternatives weighed | Status |
| --- | --- | --- | --- | --- | --- |
| Opaque first: no cards or shells near; cards only where few overlap, cut to their outline; opaque cores in every mass | Apple (§6); Humus's trimming keeps 52–60% of the quad | a rule | the harness | blades, cards, shells, ground only (§1) | new |
| Near ground cover as opaque strokes: tufts of 5–12 blades 1–2 cm wide, 30–80 triangles, thinning with widened survivors, gone by 20–40 m | AMD, Outerra; the pixel table (§1, §6) | look test 1, 2–3 days | the placer | fine blades (alias past 8 m); cards; shells | ours, on frames |
| One GPU placer: compute per tile, seeds hashed from tile, cell and layer, rank against potential, levels by pixel size, indirect draws; plants with records through the Resident Drawer | Frostbite's roulette; Horizon's "locally stable" (§6, §8) | about a week | the land's fields | Unity's details; GameObjects; geometry shaders (none on Metal) | new |
| Mats (lawn, moss, heath) as a surface 2–40 cm high with its edge as geometry, in the land's chunk mesh | "clusters with edges" is geometric (§8) | a week, with the ground shader | land chunks | the edge in the shader only (Land §1) | conflict 1 below |
| The far colour measured from each community's near tier by view elevation and season | none published how (§1) | 2 days | ground shader | an artist's guess; Tiny Glade's "astroturf" | new |
| Plants on hard surfaces along the generators' joint lines and faces; species by stress; wall ferns by mortar chemistry | γ-ton; Melander; BSBI (§2) | 3–4 days | joint-line data | by hand; curvature masks | new |
| Bushes, hedges, climbers and gardens as things with records, built like small trees; a hedge is hull plus shoots since its last cut | the trees' method; SNL, RHS (§3) | a week each | keepers' calendars | none found | new |
| Leaves and litter as a deposit field per chunk for the date, moved by the day's wind, cleared by feet and keepers | RHS, Network Rail (§4) | 3–4 days | weather as a hash of seed and day | decals; particles | new |
| No cast shadows from tufts or litter; hulls and cores cast | Ghost, Book of the Dead (§6) | none | proxies | none | consistent with performance |
| Near ground cover up to about 300,000 triangles; the tree overhead 100,000–150,000 with real leaves | the tiler's buffer (§6, §7) | none | the harness | `foundations.md`'s 60,000 a near tree | conflicts with foundations (provisional) |

## 4. What every part or thing must carry

**For the light** (Light §9): the bake per face (sky, ground, openness, weather exposure) at every tier, impostors included; a bent normal; albedo in a validated range; porosity, smoothness and water profile; translucency (leaves, curtains, paper, sailcloth, glass); an emission group tied to the fact that turns it on; light sockets (a lamp's position, cone, kind, era, shadow flag; a window's spill and cookie); room data behind windows (index, lit state, curtain, interior map); a record for every light.

**For the land** (Land §2, §6):
- every part on the ground: its foot line as a breakline, hard or soft, and its footprint, so the ground is cut away under it;
- what it writes into the fields: rain shadow, drip line, damp foot, shelter;
- natural stone: rock kind, the three vectors, years bare per face, a cut's drill era, how far the soil has climbed;
- each made-ground act: outline, kind, target surface, edge treatment, year, founder;
- each chunk: field tiles, ground map, ring level, skirts, a coarse caster; each water body its depth, seabed, shore distance and exposure; each quay its tide band.

**For the plants** (Plants §8):
- every hard part: joint lines and growth faces as data (width, depth, soil, water, feet, years since laid or swept, lime or acid); copings for cushions; gutters as litter traps;
- every wall face: its climbable region, keep-clear zones (windows, gutters, eaves, downpipes), trellis sockets;
- every plant: a record, parts by tier, wind data (element, pivot, stiffness, phase), season ranks, an opaque core;
- every GPU instance: transform, part and species, seed and rank, wind phase, field tile, and nothing else;
- each chunk: community and years since disturbance, keeper and care, the date's leaf deposit, the mat's height;
- clear zones as facts: the walking line, each keeper's swept ground, the keep-clear bands.

## 5. Conflicts and overlaps

### Between the three

| # | Topic | What they say | To settle |
| --- | --- | --- | --- |
| 1 | A mat's edge: mesh or shader | Land §1: "a crisp edge where two communities meet, thresholded against noise". Plants §8: the mat keeps "that edge as a silhouette at every tier" in the chunk mesh. | As mesh, every change of care re-triangulates a chunk. Perhaps slow edges (heath over rock) are mesh and fast ones (lawn against long grass) shader. |
| 2 | One ground map, three readers | Land: rocks and walls read it at their foot (§2). Plants: blades root in its colour (§1). Light: the seen ground needs "the ground's albedo for the season and the wet" (§7); `_OS_SunBounce` assumes a third in every weather (§5). | One map, owned once. |
| 3 | One world state | Light's layer 1 (§8); Land's tide from the date and waves from wind (§3); Plants' weather as "a hash of the world's seed and the day" (§4). | One record every system reads. |
| 4 | Two winds | Land's wind and salt is a climate field from fetch (§4); the one wind moves blades and leaves (Plants §5). The fetch also sizes the waves (Land §3). | Own them separately; share the fetch. |
| 5 | Lamp loops | Light bins `FogLights` by tile (§7); Land loops over near lamps for water columns (§3). | One tiled light list. |
| 6 | Shadows | Light: far shadows from the height map (§7); Land: a caster per chunk (§6); Plants: hulls and cores (§6). | The height map may carry far land shadow. |
| 7 | Tier boundaries | `foundations.md`: 20, 80, 400 m. `performance-at-scale.md`: 8, 20, 80, 200. Plants: 8 and 40 (§8). Land: rings at 64, 256, 1,024 m; stone at 5 and 20 (§6). Light: no numbers. | `plan.md` says levels by measured error; the named tiers may become judging bands. |
| 8 | The 2 million triangles | Land about 370,000 before culling (against 4 million); Plants 300,000 plus 150,000; water under 100,000 (Land §6). | Near 0.8 million before stone and houses: a split is needed. |

### With other studies

- **The trees' cards against the M4.** Plants §7: "of the order of fifty card layers a pixel, every one a feedback fragment". `performance-at-scale.md` §3 still budgets the near birch at 60,000 triangles of cards.
- **The cards against wind and marks in motion.** `painted-marks-in-motion.md` §7, fault 6: "Leaf cards flip"; its rule is that what changes with the view fades. The re-fit adds cut hulls, opaque cores and real leaves within 8 m. All must move with one wind: a core that sways with its mass but not the flutter, or cards drift off it. Real leaves multiply what the wind and motion vectors move. The leaves-to-cards switch is a fade, and URP's cross-fade dither "reads as a screen door" without TAA (`painted-marks-in-motion.md` §5, unverified as seen).
- **MSAA or temporal antialiasing.** Plants §6: hashed alpha's noise "is meant to be smoothed by temporal antialiasing, which we do not use". `painted-marks-in-motion.md` §7: "MSAA 4× stays ... nothing may need TAA to look right". `performance-at-scale.md` (Decisions 4): TAA or STP "may suit the painted look ... Decide on measured frames." Light relies on GTAO and SSR; none says whether URP's need temporal accumulation (my question). MSAA "stops depth priming" (performance), which bears on the leaf depth pass.
- **Bakes on vertices or maps.** `performance-at-scale.md` §5 slims the street vertex to position, normal and two UVs, history in maps. Light wants four bake channels and a bent normal at every tier (§9). The light bake belongs in the same channel spec.
- **Repetition.** "Nothing repeats unless it was factory-made" (`NOW.md`); `plan.md` allows hand-made things from large libraries. Library size per species for strokes and sprays is unset.
- **Pickability** (`plan.md`). A GPU tuft stores only tile and seed, so it picks back to its community through the field tile.
- **No Houdini, no paid assets.** Houdini, Gaea, Crest's URP version and Megascans are cited as craft only; no proposal depends on them.
- **Costed per kilometre.** Horizon's fields cost about 4 MB a square kilometre (Land §1); ours are more, and no study gives our figure.

### With decisions already made

- Beyond the Status columns: Plants' grass parting round people is play, for Øystein; its "how green" follows the rule that anything reading as history must be a fact. Land's boards and Plants' three decks wait on Øystein's download OK.

## 6. Unknowns

### What the frame-time harness must measure first

On the M4 at 1440p, in the judging views:
1. The birches on and off, with an overdraw capture of one crown in Xcode (Plants §7; already in Tuesday's run).
2. Alpha-to-coverage against a plain clip: does it defeat hidden-surface removal (Plants Gaps)?
3. `OS_TownSky`'s 64 reads a pixel, and `FogLights` over 403 lamps (Light Gaps).
4. GTAO and SSR: cost, whether GTAO feeds `OS_ShadeP`, whether each is clean without temporal accumulation.
5. How many lights Forward+ sees from each stop (Light Gaps).
6. Chunked ground's triangles in view after culling (Land Gaps).
7. A depth-only leaf pass under MSAA (Plants §6).
8. Banding in the fog nocturne, in the motion-sheet renderer (Light Gaps).

### Learned on the way

| Unknown | From | Where learned |
| --- | --- | --- |
| Does thin cloud brighten round the hidden sun? | Light §2 | drizzle frames, the light step |
| Surface Cache GI and froxel fog on Metal | Light item 12 | Unity 6.7 LTS; a day each |
| Ice direction, the phyllite's dip, the knoll's reading | Land §1, §2 | pack facts (item 1), checked at Watch Knoll |
| How far ledges can be height field | Land Gaps | Watch Knoll (item 9) |
| SSR on the Basin against a planar reflection | Land item 13 | plan step 6 |
| Tide constants; quays by era | Land Gaps | before the quay walls |
| Strokes against cards; shimmer at the street stop | Plants look test 1 | before the placer is tuned |
| A hand-over under ΔE 2 | Plants look test 2 | with the mats |
| Leaves' real budget under the birch | Plants look test 5 | the trees' re-fit |
| How fast mat edges move, and the re-triangulation | conflict 1 (mine) | the corner's years sheet |
| Moss rates, leaf colour by week, hedge decay | Plants Gaps | before plan steps 7 and 9 |
| Our fields' disk and memory per km² | none | the scale test |

## Across the three

### What the light, the land and the plants require of every part

1. **Visibility, not light:** the bake and a bent normal at every tier, impostors included.
2. **Its edges as data:** foot lines as breaklines, joint lines and growth faces with their facts, traps, climbable regions, keep-clear zones.
3. **Its material's carriers:** albedo in range, porosity, smoothness, water profile, translucency, chemistry.
4. **What it writes into the shared fields and what it reads:** rain shadow, drip and damp out; the ground map, sky map, field tiles and wind in.
5. **Sockets and records** for whatever lights, sways or grows.
6. **Opaque first:** no cut-out where layers stack; cores behind cards; shadows from hulls and proxies.

### The order, relative to the foundations

By "hardest to change first, biggest risk first" (`CLAUDE.md`):
1. **With the harness, Monday:** measure the birches, alpha-to-coverage, `OS_TownSky`, GTAO and SSR. They are the largest risks to how plants and light are built, and cheap to measure.
2. **Data formats, in the architecture:** the world-state record; ground as layers and dated acts (2½ days, clay frames unchanged); the part channel spec. The gully's port should carry its breaklines, joint lines and bake per tier from day one, so it proves them.
3. **With the scale test, Tuesday:** the chunk (Land's 64 m against the town's streaming chunk) and the maps each holds.
4. **Before further look judging:** the two cheap lookups and occlusion (1.5 to 3 days), since the debts change how every part is judged (`foundations.md`).
5. **Before new hours and weathers:** the sky model and the rig as layers (6 to 9 days).
6. **Then the plan's steps:** the birches' cut cards and cores; at step 3 the knuckle, fields, ground shader with mats, the placer, joint plants on the gully; water at step 6; night lights over steps 3 and 6.

### Three questions for Fable

1. **The part contract per tier.** What exactly does every part carry for the light, the land and the plants, and where does each channel live at each tier (vertex, part maps, chunk maps, impostor), so that history, the light bake and growth potentials share one spec?
2. **One tier table and one triangle budget on the M4, opaque first.** Reconcile five sets of tier boundaries, split the 2 million triangles among land, water, ground cover, trees, stone and houses, and write two rules: opaque first, and nothing relying on temporal accumulation. The harness's first numbers set the figures, not the shape.
3. **Shared state, owned once.** One world-state record and one set of maps per chunk (sky and height, a ground map with seasonal albedo, fields, deposits): who owns each, at what resolution and chunk, and when each is rebuilt, including whether a mat's edge is a moving breakline or shader.
