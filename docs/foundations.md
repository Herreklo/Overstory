# Foundations

What every system shares, so each new one plugs in rather than starting again (`NOW.md`, the plan, step 0). The systems' own designs (`docs/trees.md`, `docs/stone.md`, `docs/nature.md`, `docs/building-system.md`) follow these; when a system finds that one of them is wrong, this page changes first.

## The judging views

Every part, and every assembly of parts, is judged from the same views, so no part is held to a lower bar than another. Every part must look good from every angle: the camera's behaviour is a later play decision, and a part that only looks good from one side is fixed in the part.

- **Eye level:** a person's height (1.6 to 1.7 m) with the part one to five metres away; at its foot, on it, looking down at it.
- **The street stop:** about 2.8 m up, the part a few to twenty-five metres away.
- **Into it:** about 12 m up, looking into a crown or along a lane.
- **The city camera:** pulled out and steep, near-isometric.
- From several headings, in three lights (grey drizzle, the 16:00 low sun after showers, the blue hour), in colour, greyscale and at one-eighth; with the form alone in grey light (every pigment one grey) when a look will not converge.
- Measured where it can be: the value spread of a form (`blender/tools/crown_value.py` for crowns), triangle and texture counts against the tier's budget, and frame time when a part joins the corner.

## Cold readers

Whether history reads (criterion 1 in `CLAUDE.md`) is judged by cold readers, never by the maker. The method is the engine's blind reading (`docs/method/reading.md` in Understory), and the tasks, controls and failures are those in `docs/research/history-in-things.md`, section 10. Øystein decided (22 October) that model readers stand in for strangers.

- **The readers.** Fresh agents with nothing but the frames and a brief, on a model other than the one that made the work. Each reads in a role: someone who has walked such a street all their life, a building historian, a player of exploration games. The historian is there because experts and the public read aged things most differently. Three readers for a round while building; six at a gate (two per role, across two models).
- **The material.** Frames from the judging views at the player's pixel size, cut into tiles so a reader sees every pixel a player would. A reader that sees less than a player makes the test stricter, never easier. The brief says only that these are views of a town.
- **The order.** The pack, the brief and the key (the histories on show, exported by the cause view) are committed before the reading. A coder agent codes the free text against the key without knowing which arm a frame came from: the real one, layers off or facts shuffled. A script scores everything before anyone looks at the frames again.
- **The bar at a gate.** At the street stop and 12 m:
  - at least four in five of the parts marked old, changed or neglected are right;
  - at least two in three of the histories in the budget are found;
  - pairs are ordered right at least four times in five where the record differs by twenty years or more;
  - at most one false history claim per frame on average, and none held with high confidence;
  - on the years strip, the direction is right between every pair of years.

  With the facts shuffled, parts marked right must fall by at least thirty points, or readers are reading conventions rather than our facts. With the history layers off, false claims set the baseline, and the real frames may not exceed it. A round while building reports the same numbers without a bar.
- **Where a model reader may differ from a person.** It shares the maker's associations, and it knows building history better than most of the public. The shuffled-facts control is the guard against both. People still read when the engine runs its human test: Overstory's ten-minute task rides on it (`docs/engine-requests.md`). Where people and the model panel disagree, people win, and the panel's brief or roles change.
- **Criterion 4** needs readers of its own, half shown the scene first and half the page, since a reader who has read the page already knows what happened.

Results go in `docs/experiments.md` against the frames.

## Detail by tier

One part, its facts and its seed, drawn at four tiers, the same thing at each, never a different claim:

| Tier | When | What it draws | Budget (provisional, to be measured) |
| --- | --- | --- | --- |
| Near | within about 20 m: eye level, scenes | the part in full: real chamfers, the worn hollow, a tree's real leaves near the camera, painted textures at about half a millimetre a texel | a stone piece up to 600 triangles; a tree up to 60,000; a house up to 40,000 |
| Street | 20 to 80 m | the part simplified, its texture's mips | a stone piece about 120; a tree about 10,000; a house about 8,000 |
| City | 80 to 400 m | runs of parts merged (a flight, a wall, a house), detail baked into their textures | a flight about 2,000; a tree about 1,500; a house about 1,500 |
| Far | beyond 400 m | impostors and the terrain's own baked colour | a few triangles |

**The reference machine is an ordinary computer** (Øystein, 22 October: playing should not need a gaming PC at all). Every budget is set on the Mac mini with an Apple M4 (10-core GPU). Benchmarks put it at about a third to a half of an RTX 3060, roughly the class of a recent laptop's built-in graphics. On it, at default settings, the game holds 60 frames a second on a 1440p screen in every judging view. Where the harness shows it pays, the game draws below the screen's size and upscales; that choice is made together with the antialiasing. Weaker machines get lower settings; nothing is designed for a gaming card. Its GPU draws in tiles, so the costs differ from a PC card's. Opaque overdraw and MSAA are cheap there. Alpha-tested cut-outs (leaf cards, grass) and dense small triangles are dear, so the trees and the ground cover are designed with that in mind (`docs/research/performance-at-scale.md`).

A frame's whole budget on that machine, provisional until the performance harness measures it: about 2 million visible triangles and under 3,000 draw calls, with shared parts instanced through the GPU Resident Drawer. That is half the earlier figure for a mid-range card, because the M4 is about half of one. Detail lives in painted textures, which cost little, before geometry; real geometry goes where it shows (a silhouette, a nosing, a hollow). Each part's done-list includes its tiers and their counts; the corner is frame-timed each time a part joins it.

## The shared surface layers

Every hard surface (stone, timber, brick, render, concrete, asphalt, roofs) is drawn by one stack of history layers, each from its cause and owned once, so a new material brings its pigment and rules rather than a new system (`docs/stone.md`, The history layers):

1. pigment and grain (the material's, painted at our scale, seeded per piece, never tiling);
2. tooling or finish (how it was made);
3. wear and polish (from footfall and every other contact of use, and years; `wear.py`);
4. stains (run-off, algae film, rust, soot, salt; run-off from the water layer, `Water.hlsl`);
5. growth: nature's (`docs/nature.md`, Growth on surfaces; `growth.py`, `Growth.hlsl`, the pack's `GrowthPack`);
6. damage and repair: the thing's upkeep (`docs/upkeep.md`: left alone, patched, worked in a campaign, renewed; each repair its own material and date, spread as its causes spread; `upkeep.py`, the parts in `blender/parts/repair/`);
7. weather (wet, frost, snow and ice, fallen leaves, litter).

**Water and gravity order the stains, the weather and the growth** (Øystein, 22 October: "think about how rain, moss etc works; gravity"). Each generator bakes, per point, how much water lies or runs there (the water layer, UV2.y on stone): rain lands on what faces up, runs to the low edges and joints, drips off copings and nosings and streaks down the faces below (most under joints and low points, strongest near the top), gathers in hollows, joints and at every wall's foot (the splash and the damp), and dries from the crowns and edges first. Wetness after rain, run-off streaks of algae and grime, moss and algae follow it; lichen takes the dry, lit, exposed places between. An even rule for every up-facing surface, or growth from a noise field, reads as the same pattern everywhere (camouflage).

**Wear follows every contact of use, not only feet:** footfall on what is walked on (polish, a hollow, rounded nosings), hands on what is held (a stair's parapet coping at hand height, a door's handle side, a railing), boots and bags at a wall's foot beside a flight, wheels at a corner, sitting on a step or a sill; each polishes, darkens and clears growth where it touches, from the uses (`docs/living-fabric.md`).

Lichen grows as rosettes: each colony from a point in its own year, spreading about a third of a millimetre a year, merging where colonies meet and stopping at a stone's edge (`Growth.hlsl`); from past the street stop, a film over each stone as much as its years and quiet give.

**Each system has one home, the same shape for every system** (Øystein, 22 October: separate the systems in a way that makes sense; water behaves differently on different materials). Where a cause acts is baked by the generators from facts and shape, how it is drawn is one shader include every surface's shader uses, what varies by place or material is the setting pack's or the material's own:

| System | Where (generator side) | How it is drawn | What the pack or the material brings |
| --- | --- | --- | --- |
| Water | `blender/generators/water.py`: where it lands, runs, drips, pools and lingers | `Water.hlsl`: wet now, the film, pools, run-off streaks | each material's water profile (how dark wet, how glossy its film, how long it holds water, how readily it stains); the shared materials' in `WaterPack` (cement, soil, growth) |
| Wear | `wear.py`: feet, hands, boots, wheels | the polish channel | the material's hardness and polish |
| Growth | `growth.py`: where and how long | `Growth.hlsl` | `GrowthPack`: the species, their pigments and rates |
| Damage and repair | `upkeep.py`; the repair parts in `blender/parts/repair/` | the repair materials' kinds | the era's materials (`docs/upkeep.md`) |
| Detail by distance | — | `Detail.hlsl` (`OS_Near`) | — |
| Light | the bakes (sky, ground) | `StreetLooks.hlsl` (`OS_ShadeP`) | the rigs |

Shade is the light's, never the object's (SEASON's lesson, `docs/research/colour-and-shading.md`, rule 1): every surface is lit by the town's one shade function (`OS_ShadeP`, `StreetLooks.hlsl`), and no layer carries a shadow tint. A layer's dark (a joint, a nosing's underside) is its occlusion, baked or the light's.

## The living fabric

Every made or planted thing carries one record (made, keepers and their care, uses, works, events) and runs through one runner to its life as it is now; changes flow between things through shared fields over the town (feet, water, sky, wind and salt, care, vacancy); and each view tells a measured number of histories, marks from one cause drawn as one shape (`docs/living-fabric.md`; repairs: `docs/upkeep.md`).

## Packs and facts

- What a thing is and when it changed are facts: from the engine, or authored in a fixture until the engine has them (`docs/engine-requests.md`). What claims nothing is seeded texture.
- What a place brings (its stones, species, building traditions, eras, growth, climate) is its setting pack; the systems know no country.
- Every system's done-list includes one part from a foreign pack (a London plane, a York stone flag, a brownstone stoop), to prove the system is not hard-coded to this town.

## The shared light's debts

Two faults in the town's light model change how every part is judged, and are fixed before the corner is judged complete. Under a uniform overcast an upright cylinder (a trunk, a post, a round tower) got no lit side and read as one soft value: fixed (22 October) by biasing the drizzle's sky term to its bright side, where the pale sun hides behind thin cloud, about a third brighter than the side away from it and near-neutral (research rule 2; light, never the object). In low sun the shade side of upright surfaces took warm ground bounce even where the ground beside it lay in blue shadow: fixed (22 October) in the town's one shade function, the ground's light following whether the ground a face looks onto is in sun (a face turned towards the sun and not in a cast shadow sees lit ground and its warm bounce; one turned away sees ground in shade, lit by the sky, and its cooler light), weighted by how strong the sun is beside the sky. With them, the drizzle and morning hours' retune (they fail the value test).
