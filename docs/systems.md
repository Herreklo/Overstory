# The world's systems

A map of everything the world is made of and how it fits together, with the state of each and where it is designed. Three levels, each built once and reused: **shared systems** act on everything (water runs down any face); **materials** give each thing its identity (slate, granite, timber, paint); **kinds of things** are built from materials by generators from facts (a stair, a wall, a house), and every instance in the world is generated, never made by hand. A kind is made once with care (its parts, its rules, a variety sheet, a review); a material once (its pigment, grain, working, water, wear and ageing); a system once for all. The plan's steps are in `NOW.md`; the rule that reuse stops at systems is in `CLAUDE.md`.

State: **built** (in use, reviewed), **in progress**, **designed** (a design page, not built), **planned** (in the plan or the research, no design yet).

## Who decides

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
| Detail by distance | true up close, painted from afar | built | `Detail.hlsl` |
| Distance tiers | near, street, city, far: simpler geometry and merged meshes by distance; budgets | designed; next after the corner's stone | `docs/foundations.md` |
| The living fabric | one record and runner for every made or planted thing; changes flow through shared fields (feet, water, sky, wind and salt, care, vacancy); the history budget per view | designed | `docs/living-fabric.md` |
| The town system | dated plan units, plots with cycles, plans and building rules, the underground, the past grown to the start year | designed | `docs/town-system.md`, `docs/research/urban-design.md`, `city-forces.md`, `city-types.md` |
| Coatings | paint and limewash in coats by owner and decade, fading, peeling, ghost signs | planned (with the houses) | |
| Weather and seasons | rain, snow, frost, fog, wind; the year's turn; fallen leaves | partly (wetness, the trees' seasons); planned | `docs/trees.md` |
| Records | signs, posters, notices, papers: perceived information, which may be wrong | designed (engine request 9) | `docs/engine-requests.md` |
| People and crowds | figures, posture from state, crowds | planned (plan step 5) | `docs/research/people-deep-dive.md`, `docs/living-world.md` |

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

Every system, material and kind is studied twice before it is built (`CLAUDE.md`: research the subject and the craft): its **subject** (what it is, its facts, history and look) and its **craft** (how the best studios and masters build it at quality and scale, for our stack). A gap here blocks building. "Running" means the study is being written.

| Area | Subject | Craft |
| --- | --- | --- |
| Light and colour | `colour-and-shading.md`, `masters-of-colour.md` (thin) | `lighting-and-colour.md` |
| Water, wear, growth, repairs | `repairs.md`, `stone.md`, `nature.md` | `materials-at-scale.md`, `history-in-things.md` |
| History in things | `world-that-remembers.md`, `house-changes.md`, `repairs.md` | `history-in-things.md` |
| Tiers, instancing, quality control | `tools-and-performance.md` (thin) | `performance-at-scale.md` |
| Kits and generators | `generating-the-past.md` (thin) | `kits-and-generation.md` (running) |
| Towns and cities | `urban-design.md`, `city-forces.md`, `city-types.md`, `town-change.md`, `stavanger-centre.md` | `kits-and-generation.md`, `urban-design.md` |
| Stone, made | `stone.md`, `repairs.md` | `materials-at-scale.md`, `performance-at-scale.md`, `kits-and-generation.md` (running) |
| Land, rock, water, coast | `nature.md`, `stone.md` | `land-rock-and-water.md` (running) |
| Buildings and their parts | `house-changes.md`, `wooden-town-architecture.md` | `kits-and-generation.md` (running), `materials-at-scale.md` |
| Trees and nature | `trees.md`, `vegetation.md`, `park-trees.md`, `nature.md` | `performance-at-scale.md`, `animation-and-motion.md` (wind; running); ground cover craft: **gap**, before plan step 3 |
| People as models | `people.md`, `people-deep-dive.md` | `characters.md` |
| Behaviour on screen | `people.md` (thin) | `behaviour-on-screen.md` (search budget ran out: its Gaps list sources to close) |
| Animation and motion | `what-moves.md` (thin) | `animation-and-motion.md` (running) |
| Street things, vehicles, boats | `between-buildings.md`, `what-moves.md` (thin) | **gap**, before plan step 6 |
| Signs, lettering, records | `interface.md` (thin) | **gap**, with the houses' shopfronts (partly in `wooden-town-architecture.md`) |
| Interiors | `scenes-and-sound.md` (thin) | **gap**, before plan step 8 |
| Weather and seasons | `trees.md` (seasons), `lighting-and-colour.md` (partly) | **gap**, before plan step 9 |
| Camera and composition | `visual-direction.md` | **gap**, before the play camera |
| Sound and music | `scenes-and-sound.md` (thin) | **gap**, before scenes |
| Interface and reading the world | `interface.md` (thin) | **gap**, before play |

## How a new thing joins

A kind joins by a checklist (`docs/living-fabric.md`, Making it nice to work with): its subject and craft researched (above); its parts made once and shaped on a quick sheet; its material, or a new one with its identity; which shared systems act on it and how (water, wear, growth, repairs); its facts, by rule until the engine has them; its tiers and counts; one foreign-pack part; a variety sheet in the game's light; a strict review; Øystein's judgement. A material joins with its pigment, grain, working, water profile, wear and crack rates, and how it ages. A shared system is built once and every kind and material takes it.
