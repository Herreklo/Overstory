# The world's systems

A map of everything the world is made of and how it fits together, with the state of each and where it is designed. Three levels, each built once and reused (SY1): **shared systems** act on everything (water runs down any face); **materials** give each thing its identity (slate, granite, timber, paint); **kinds of things** are built from materials by generators from facts (a stair, a wall, a house), and every instance in the world is generated, never made by hand. A kind is made once with care (its parts, its rules, a variety sheet, a review); a material once (its pigment, grain, working, water, wear and ageing); a system once for all. The plan's steps are in `NOW.md`; the rule that reuse stops at systems is in `CLAUDE.md`.

State: **built** (in use, reviewed), **in progress**, **designed** (a design page, not built), **planned** (in the plan or the research, no design yet).

## In short

- **SY1** Systems act on everything, materials give identity, kinds are generated from facts; each built once, no instance by hand. Evidence: the opening. Reopens: none named.
- **SY2** Engine: people, money, ventures, plans, works, homes, feet. Pack: land, eras, rules, species, climate. Ours: how a fact looks; derived facts until the engine has them. Evidence: Who decides. Reopens: none named.
- **SY3** A kind joins with research, parts on a quick sheet, its material, the shared systems, facts, tiers, one foreign-pack part, a variety sheet, a strict review, Øystein; done per the plan (disputed: "birch done"). Evidence: How a new thing joins. Reopens: none named.
- **SY4** Subject and craft first; a gap blocks building. Gaps, due before: weather, step 9; sound, scenes. Management screens: once the first game is chosen or the greybox needs them. Evidence: Research coverage. Reopens: none named.
- **D2.1, D2.2** Non-fact choices come from world seed, stable id and purpose; each debt moves at its own step, paint at port step 4; the Variety stairs stale until rebuilt. Evidence: Seeds. Reopens: none named.

## Who decides (SY2)

| Who | Decides | Where |
| --- | --- | --- |
| The engine (Understory) | people, their lives, money, ventures, the council's plans, works as decisions, homes, feet | `docs/engine-requests.md` |
| The setting pack | the land, its history script, materials and parts by era, building rules, species, climate, city types | `docs/town-system.md`, `docs/foundations.md` |
| Overstory's rules | how a fact looks: wear, growth, repairs drawn, light, the history budget; derived facts until the engine has them | this page |

## Shared systems

| System | What it does | State | Where |
| --- | --- | --- | --- |
| Light | the town's one shade function, the sky map, the rigs (drizzle, low sun, blue hour, morning, sea fog), the style | built | `StreetLooks.hlsl`, `docs/visual-direction.md` |
| Water | where rain lands, runs, drips, pools and lingers; each material's answer to it | built | `water.py`, `Water.hlsl`, `WaterPack` |
| Wear | every contact of use: feet, hands, boots; polish, hollows, rounded nosings | built (wheels, sitting: planned) | `wear.py` |
| Growth on surfaces | lichen and moss by years, quiet, damp and light | built | `growth.py`, `Growth.hlsl`, `GrowthPack`, `docs/nature.md` |
| Upkeep and repairs | keepers and care, patchwork, campaigns, renewals, by era | built (stone); every material next | `upkeep.py`, `docs/upkeep.md` |
| History as a function | each layer drawn from the record and the date: a drive per texel in the history pages, clocks per piece, speed and care per thing, the date a global; every shader reads it through one include | designed (decisions D5.1, D5.4, D5.10); the law fitted on the gully, the date, the include and the cost measured (step 3's R1 to R2c); the pages, the stone on them, the A/B, the years sheet and the gully's cost next (R3 to R7) | `docs/building-blocks.md`, `schemas/layers.json`, `schemas/maps.json`, `Shaders/History.hlsl`, `reviews/lt1/history/` |
| Detail by distance | true up close, painted from afar | built | `Detail.hlsl` |
| Distance tiers | near, street, city, far: simpler geometry and merged meshes by distance; budgets | designed; next after the corner's stone | `docs/foundations.md` |
| The living fabric | one record and runner for every made or planted thing; changes flow through shared fields (feet, water, sky, wind and salt, care, vacancy); the history budget per view | designed | `docs/living-fabric.md` |
| The town system | dated plan units, plots with cycles, plans and building rules, the underground, the past grown to the start year | designed | `docs/town-system.md`, `docs/research/urban-design.md`, `city-forces.md`, `city-types.md` |
| Coatings | paint and limewash in coats by owner and decade, fading, peeling, ghost signs | planned (with the houses) | |
| Weather and seasons | rain, snow, frost, fog, wind; the year's turn; fallen leaves | partly (wetness, the trees' seasons); planned | `docs/trees.md` |
| Records | signs, posters, notices, papers: perceived information, which may be wrong | designed (engine request 9) | `docs/engine-requests.md` |
| People and crowds | figures, posture from state, crowds | planned (plan step 5) | `docs/research/people-deep-dive.md`, `docs/living-world.md` |
| Seeds | the one hash spec: every visible choice that is not a fact is drawn from the world seed, a stable id (`schemas/naming.md`) and its purpose | built for the gully (stone, walls, upkeep) and in Unity (`Hash.cs`, the air motes); debts below | `blender/resolver/hashing.py`, `Core/Hash.cs`, `fixtures/golden/hash-vectors.json` |


**Seed debts** (22 October; D2.1, D2.2). These still draw from the old randomness, and each moves onto the hash spec at its own step:
- `blender/parts/stone/*/paint.py` and `parts/trees/birch/paint.py` use numpy's `default_rng` (with the material record, step 4);
- `parts/trees/painting.py`, `tree_growth.py`, `house.py`, `stair_facts.py`, and the clay's `blockouts/heart_layout.py` and `heart_build.py` use `random.Random`. Moving the clay moves every golden frame.

There are two other debts:
- `upkeep.py` still uses `exp`: a lognormal settling rate and a Poisson count of quick fixes. These break D2.2's rule that choices are made from integers, the four operations and square roots only (step 2).
- The Variety stairs' FBX and their manifest (`unity/Assets/Art/Stone/Variety/`) predate the hash spec and the landing rule. They are stale until they are rebuilt.

## Materials

Each with its own identity from facts (where it came from, how it was worked, how it is exposed), and its own answer to water, wear, cracking and age.

| Material | Variants | State |
| --- | --- | --- |
| Stone | slate (split blocks and slabs), granite (dressed, setts), rubble (the gully's own rock); bedrock and boulders as nature's | built: slate, granite, rubble; bedrock planned |
| Mortar and cement | lime, cement pointing, dabs, screeds | built (cement, joint soil) |
| Soil and sand | joints, beds, yards, paths | built (joints); ground planned |
| Timber | cladding, windows, doors, fences, quays' timber | planned (houses) |
| Paint | coats on timber, iron and render | planned (coatings) |
| Render and brick | masonry houses, warehouses | planned |
| Concrete | casts, steps, quay toes, 1960s blocks | planned |
| Asphalt | patches from the 1920s, everywhere after 1960 | planned |
| Metal | iron (rails, lamps, covers), zinc, steel | planned |
| Roofing | slate, red tile, Eternit, felt, tin | planned (houses) |
| Glass | windows by era, light behind them | planned (houses) |
| Bark and leaves | the trees' own | built (birches) |
| Water bodies | the sea, the Basin, streams, puddles | planned (plan step 6) |

## Kinds of things

| Group | Kinds | State |
| --- | --- | --- |
| Stone, made | stairs (block, tread on riser, step-ramp); dry-stone walls and copings; setts and flag gutters; kerbs; plinths; quay walls and steps | stairs in review; walls first pass; setts and the lane in progress; kerbs, plinths, quays planned (plan steps 1 and 6) |
| Stone, natural | bedrock and knolls, cliffs, boulders, the shore's rock | planned (plan steps 3 and 6) |
| Buildings | wooden town houses, merchants' houses, shopfronts, sea houses and warehouses, the cannery, church and school, 1960s blocks | the house generator and building diaries exist at test quality; the corner's five houses are plan step 2 |
| Building parts | walls and cladding, windows, doors, roofs, chimneys, gutters and downpipes, stoops, signs | planned (plan step 2) |
| Street things | lamps, posts, railings and handrails, fences, benches, bins, kiosks, wires and poles, covers, bollards | clay only; planned (plan steps 3 and 6) |
| The underground | mains, cables, cellars, shelters, tunnels, parking, passages; their surface traces | designed (town system); traces first |
| Land | the terrain and hillsides, made ground, the shore and beach, streams, lakes | clay only; planned (plan step 6) |
| Nature, living | trees (birch done; spruce, beech, rowan, sycamore next), grass and ground cover, heath, ferns and weeds in joints, bushes and hedges, gardens and lawns, farmland, forest, wetland | birches built; the rest designed in `docs/nature.md`, plan step 7 (grass in the corner at step 3) |
| Moving and alive | people, crowds, boats, vehicles, animals, smoke, washing on the line | planned (steps 5 and later) |
| Interiors | rooms as space and stuff by era and household | planned (plan step 8) |
| The region | other towns, farms, roads, the sea routes | planned (plan step 10) |

## Research coverage

Every system, material and kind is studied twice before it is built (SY4; `CLAUDE.md`: research the subject and the craft): its **subject** (what it is, its facts, history and look) and its **craft** (how the best studios and masters build it at quality and scale, for our stack). A gap here blocks building. "Running" means the study is being written.

| Area | Subject | Craft |
| --- | --- | --- |
| Light and colour | `colour-and-shading.md`, `masters-of-colour.md` (masters across a whole scene: palettes per light, where chroma sits measured on our references, the greys, the accent, one grade holding it in URP) | `lighting-and-colour.md`; light under a canopy and many lamps at city scale studied in LA as far as the light record and the shade's terms need (§10 to §12; `reviews/lt1/light/la-report.md`); their builds' craft (the canopy map, the night tiers) is finished at 1e and the night step, with the unknowns listed in the report |
| Water, wear, growth, repairs | `repairs.md`, `stone.md`, `nature.md` | `materials-at-scale.md`, `history-in-things.md` |
| History in things | `world-that-remembers.md`, `house-changes.md`, `repairs.md` | `history-in-things.md` |
| History pages: binding, block compression, time inputs per texel, charts | `history-in-things.md` (Gu's factorisation), `wear.py` and `growth.py` (the laws) | `history-pages.md` (step 3's R0; the binding and its cost measured at R2 to R2c: a sample is cheap, a busy output is not; a real page's BC7 error and the chart waste at R3, border shimmer at R6, the binding under the Resident Drawer at 3.4) |
| Tiers, instancing, quality control | `tools-and-performance.md` (thin) | `performance-at-scale.md` |
| Per-pixel cost on the M4: passes, tile memory, shading rates | `docs/measuring.md` (the pass budget), `reviews/lt1/playable/walk/w3-report.md` | `performance-craft.md` (beams at a quarter of the pixels with one hard tap; each term shaded at its rate; trees depth first; the frame kept on tile; per-line profiling in Xcode; resolution as the reserve dial; each to be A/B'd on the harness in the frame-rate gate) |
| Kits and generators | `generating-the-past.md` (thin) | `kits-and-generation.md`, `where-generation-runs.md` |
| Towns and cities | `urban-design.md`, `city-forces.md`, `city-types.md`, `town-change.md`, `stavanger-centre.md` | `kits-and-generation.md`, `urban-design.md` |
| Stone, made | `stone.md` (laying a stair and its walls: level beds, heads at a change of pitch, steps built in; 22 October), `repairs.md` | `stone.md` (How stone is built and laid: rigid blocks cut by planes, shared sculpted faces, budgets, the faults' causes, seven checks; 22 October, notes in `reviews/lt1/port/2b/`), `materials-at-scale.md`, `performance-at-scale.md`, `kits-and-generation.md`; a cut-to-fit rigid generator has no public precedent, so its rules come from masons, engineers and packing papers |
| Land, rock, water, coast | `nature.md`, `stone.md` | `land-rock-and-water.md` |
| Buildings and their parts | `house-changes.md` (to 1989), `house-changes-1989-2020.md` (what owners and the town did from 1989 to 2020, new buildings among the old, the marks that date each, and the evidence for LT1f's authored rules after 1988), `wooden-town-architecture.md`, `house-fronts.md` (repaint practice and cycle, course layout, profiles, factory joinery; failure rates on this coast and the weather wall still open) | `kits-and-generation.md`, `materials-at-scale.md`, `house-fronts.md` (what the fronts need from the port's steps 4 and 5: coats as clocks, painted marks as masked coats, thin repeating features drawn from their facts, lap shadows from the shader, casters, library parts; the front family's cost is unmeasured, learned at step 5) |
| Trees and nature | `trees.md`, `vegetation.md`, `park-trees.md`, `nature.md` | `performance-at-scale.md`, `animation-and-motion.md` (wind); `ground-cover-and-plants.md` (ground cover, plants, and the trees re-checked against the reference machine; three large decks unopened: its Gaps) |
| People as models | `people.md`, `people-deep-dive.md` | `characters.md` |
| Behaviour on screen | `people.md` (thin) | `behaviour-on-screen.md` (29 October: schedule data, The Sims 4's emotions, Gehl, Whyte, Statistics Norway's 1980s day and the pace of towns closed from sources, much of it secondary; Rockstar's own account, Life Between Buildings and Norway's distances still open: its Gaps) |
| Animation and motion | `what-moves.md` (thin) | `animation-and-motion.md` |
| Street things, vehicles, boats, animals | `between-buildings.md`, `what-moves.md` (thin); street things: `street-things.md`; boats and vehicles: `boats-and-vehicles.md` | boats and vehicles: `boats-and-vehicles.md` (the harbour and streets 1870 to 2020, the berth moved by wind, tide and wakes, parked and timetabled movers without physics, their cost on the M4 and three first tests; 29 October; the town archive's gaps listed); animals: `animals.md` (subject and craft: harbour and coast birds, dogs and cats, Jæren's sheep and cattle by era; flocks, herds, formats and sizes on screen; 29 October; wingbeats and a measured flock cost on the M4 still open); street things: `street-things.md` (Stavanger's lamps, handrails, quays, fences and dating marks 1866 to 2020 with their keepers; kits, lamps without a light each, painted iron by one upkeep value, their cost on the M4 and three first tests; 29 October; the 1960 jubilee book, span lighting's years, bollard makers and Unity's timings on Apple GPUs still open) |
| Windows, glass, signs, lettering, records | `interface.md` (thin), `wooden-town-architecture.md` | `fronts-windows-and-signs.md` (what is seen through windows, lit windows, signs by era, street records; search budget ran out for some games: its Gaps) |
| Interiors | `rooms-and-interiors.md` (subject and craft, 29 October); `scenes-and-sound.md` | the view through windows in `fronts-windows-and-signs.md`; homes 1870 to 2020 with 1989 in numbers, furnishing from facts, room light on the M4, three first tests; open: workplace interiors in 1989, villas after 1945, kitchens after 1980, several game talks, and APV's cost on the M4 (its Gaps) |
| Weather, seasons and effects | `trees.md` (seasons), `lighting-and-colour.md` (partly) | **gap**, before plan step 9 (with smoke, steam, spray and fire) |
| The painted look in motion | `colour-and-shading.md`, `visual-direction.md` | `painted-marks-in-motion.md` |
| Time on screen: one place across years | `history-in-things.md`, `town-change.md`, `living-fabric.md` | `time-on-screen.md` |
| Collision and navigation (where people and the camera can go, footing on treads and slopes) | `reach_check.py` (ways only) | `collision-and-navigation.md` |
| Camera and composition | `visual-direction.md` | `camera-and-composition.md` (gaps reached 29 October, some only through others' reports; section 7, spectacle from a free camera, with three grey tests for the Holm tip; still unread: the Uncharted 3 camera talk, Sucker Punch's landscape and wind talks, the CEDEC 2017 slides) |
| Management and data interfaces: tables, boards, calendars, inboxes, ledgers (a manager game's desk) | `interface-and-inspection.md` (reading the world only) | **gap**, studied once the first game is chosen or the greybox needs it |
| Playtesting: the programme, tools and what is worth trying | `docs/foundations.md` (Cold readers) | `playtesting.md` (Fable review after the reset; Blizzard, Insomniac, Riot and Sawyer's reactivity testing unread: the search budget ran out) |
| Play craft: feel, focus, guidance, transitions, narrow streets | `living-world.md` | `play-craft.md` (Øystein: "extremely clever... master craftsmanship, finesse"; GDC Vault was down: the slides to read after the reset) |
| Sound and music | `scenes-and-sound.md` (thin) | **gap**, before scenes |
| Interface and reading the world | `interface.md` (thin) | `interface-and-inspection.md` (hover, inspect, the why-probe, the journal; what every part carries for picking) |

## How a new thing joins

This lists what a kind brings (SY3); when it is done is the plan's definition (`docs/plan.md`, The order, Done: across its range, walked in the playable corner, at the bar against its target frame, accepted by Øystein; until then its state is the rung it has reached). A kind joins by a checklist (`docs/living-fabric.md`, Making it nice to work with): its subject and craft researched (above); its parts made once and shaped on a quick sheet; its material, or a new one with its identity; which shared systems act on it and how (water, wear, growth, repairs); its facts, by rule until the engine has them; its tiers and counts; one foreign-pack part; a variety sheet in the game's light; a strict review; Øystein's judgement. A material joins with its pigment, grain, working, water profile, wear and crack rates, and how it ages. A shared system is built once and every kind and material takes it.
