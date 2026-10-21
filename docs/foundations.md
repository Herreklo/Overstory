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

## Detail by tier

One part, its facts and its seed, drawn at four tiers, the same thing at each, never a different claim:

| Tier | When | What it draws | Budget (provisional, to be measured) |
| --- | --- | --- | --- |
| Near | within about 20 m: eye level, scenes | the part in full: real chamfers, the worn hollow, a tree's real leaves near the camera, painted textures at about half a millimetre a texel | a stone piece up to 600 triangles; a tree up to 60,000; a house up to 40,000 |
| Street | 20 to 80 m | the part simplified, its texture's mips | a stone piece about 120; a tree about 10,000; a house about 8,000 |
| City | 80 to 400 m | runs of parts merged (a flight, a wall, a house), detail baked into their textures | a flight about 2,000; a tree about 1,500; a house about 1,500 |
| Far | beyond 400 m | impostors and the terrain's own baked colour | a few triangles |

A frame's whole budget, to be confirmed by the performance harness (`docs/research/tools-and-performance.md`): about 4 million visible triangles and under 3,000 draw calls at 1440p and 60 frames a second on a mid-range PC graphics card, with shared parts instanced through the GPU Resident Drawer. Detail lives in painted textures, which cost little, before geometry; real geometry goes where it shows (a silhouette, a nosing, a hollow). Each part's done-list includes its tiers and their counts; the corner is frame-timed each time a part joins it.

## The shared surface layers

Every hard surface (stone, timber, brick, render, concrete, asphalt, roofs) is drawn by one stack of history layers, each from its cause and owned once, so a new material brings its pigment and rules rather than a new system (`docs/stone.md`, The history layers):

1. pigment and grain (the material's, painted at our scale, seeded per piece, never tiling);
2. tooling or finish (how it was made);
3. wear and polish (from footfall and use, and years);
4. stains (run-off, algae film, rust, soot, salt);
5. growth: nature's (`docs/nature.md`, Growth on surfaces; `growth.py`, `Growth.hlsl`, the pack's `GrowthPack`);
6. damage and repair (each its own material and date);
7. weather (wet, frost, snow and ice, fallen leaves, litter).

Shade is the light's, never the object's (SEASON's lesson, `docs/research/colour-and-shading.md`, rule 1): every surface is lit by the town's one shade function (`OS_ShadeP`, `StreetLooks.hlsl`), and no layer carries a shadow tint. A layer's dark (a joint, a nosing's underside) is its occlusion, baked or the light's.

## Packs and facts

- What a thing is and when it changed are facts: from the engine, or authored in a fixture until the engine has them (`docs/engine-requests.md`). What claims nothing is seeded texture.
- What a place brings (its stones, species, building traditions, eras, growth, climate) is its setting pack; the systems know no country.
- Every system's done-list includes one part from a foreign pack (a London plane, a York stone flag, a brownstone stoop), to prove the system is not hard-coded to this town.

## The shared light's debts

Two faults in the town's light model change how every part is judged, and are fixed before the corner is judged complete: under a uniform overcast an upright cylinder (a trunk, a post, a round tower) gets no lit side and reads as one soft value; and in low sun the shade side of upright surfaces takes warm ground bounce even where the ground beside it lies in blue shadow. With them, the drizzle and morning hours' retune (they fail the value test).
