# Stone

How the town's stone is made, laid, aged and drawn: steps, walls, quays, kerbs, paving and bedrock first, and through the same history layers every hard surface later (brick, render, concrete, asphalt). A piece of stone is a part of the world with a history, like a building or a tree: what reads as history (a worn hollow, a relaid step, lichen the size of eighty years) is a fact with a date; what claims nothing (the grain, the exact chip of an edge) is seeded texture. This is the design; how it was found is in `docs/experiments.md` (LT1, stone), and the research behind it in `docs/research/stone.md`.

## What we want

- **Each piece reads its stone, its age and its use**, at the street stop and from the city camera: a viewer can say which steps are busy and which quiet, which flight is old and which run of it was reset, which corners were patched and when, which wall was rebuilt, and is right.
- **Our style, not the generic one.** Big shapes first and few values (two or three a stone); detail only where the story is (the lit edge, the worn middle, the damp foot); joints as broken accents, never a grid; grey stone as a coloured grey that takes the light's colour.
- **Time is real.** A flight is built in its year and wears with the feet that climb it; lichen grows from the year the stone was bare and is cleaned away when someone cleans it; a repair is a dated event. The flight in 1989 contains the flight it was in 1988.
- **Every city brings its stone.** The system knows nothing about Norway: a setting pack brings its stones, how they are dressed and laid, its eras of paving, and its parts (phyllite, slate and granite here; York stone flags and Portland stone in London; brownstone and bluestone in New York). The harbour town stands on Stavanger's own phyllite (Øystein, 22 October; `docs/research/land-rock-and-water.md`). The knolls, the Bluff and the bare rock in the lanes are phyllite: laminated, banded grey-green to graphite-black, rusty in places, plucked into thin stepped ledges along its foliation. The slaty local stone of the old town's steps and walls is the same rock, quarried. Pale gneiss and granite appear only as erratic boulders the ice carried in, and as granite brought in as dressed stone from about 1870.
- **It grows as a system.** One flight in the beauty corner first; then every hard surface in the town by the same pieces, rules and history layers, from a lane's steps to a city's quays; and brick, render, concrete and asphalt join through the same layers with their own pigments and rules.

## The facts a piece carries

From the engine, or authored in a fixture until the engine has them (`docs/engine-requests.md`):

- *Kind and finish*: the stone, from the pack's list (the local phyllite and its slate, Iddefjord granite, larvikite, concrete) and how it was dressed (split, hewn, sawn).
- *Built*: the year, and how, by the era's practice: block steps each resting on the one below, or slabs set into the terrain; dry-stone or mortared; setts in arcs or rows.
- *Place*, computed rather than authored: shade (the town's sky map), wet (slope, run-off from what stands above, the tide band on a quay), exposure to the sea wind, which way it faces.
- *Use*: footfall a year (the engine's trips), and how it is used: which line people take, up or down, in pairs or single file.
- *Tending*: the years it was cleaned or weeded, gritted or salted.
- *Upkeep and events* (`docs/upkeep.md`): who kept it and how well, decade by decade; and the works, each dated: a run of steps reset (its own stones bedded level again, fresh joints), a step swapped (an unworn side step moved to the middle, a sharper nosing among worn ones), a hollow filled with a cement screed, a stone indent, a concrete recast, a handrail set in lead and its post rusting, a wall section rebuilt in new stone, a strip dug up for a pipe and patched, a surface asphalted over.

## How time works

As for trees: a piece's diary is read at the year, deterministically. Its state accumulates from its facts and resets with its events:

- **Wear** is footfall times years over the stone's hardness (Archard's law): a hollow down the walking line, deepest at the middle of a wide step, the nosing rounded; polish comes in the first years, depth over centuries.
- **Growth** is a rate times the years since the stone was bare or cleaned, after a delay: map lichen discs growing about 0.7 mm a year on the quiet ends and faces, moss in the joints and at the wall's feet where it is shaded and wet, Grimmia cushions on wall tops; never on the walking line.
- **Stains** follow water: black run-off streaks under what drips, green film on shaded wet faces, rust under iron.
- **Damage** follows causes: a frost crack at a rusting rail post, a bulge in an undrained wall.
- **Repair** resets what it touches, and only that (`docs/upkeep.md`): a reset step keeps its stone, hollow and lichen but gets a level bed and fresh joints, its joint moss restarting and its lichen torn where hands gripped it; depot stone brings its own weathering; a new stone starts from its year (no hollow, no lichen); cement, a screed or concrete is another material with its own date. Repairs come in runs and scattered patches, never one new step in an old flight without a cause that touched one step.

The weather and the season are a second clock on top: wet (darker and glossier, water standing in the worn hollows, the gloss drying first), frost and snow, ice in the hollows, and fallen leaves gathering in the corners of steps and against walls (`docs/trees.md`).

## A setting pack's stone

A pack brings, for each stone: its pigment and range, its grain, how it splits and dresses (the shapes of its blocks), its hardness (how fast it wears), its porosity (how much it darkens wet), what grows on it and how it stains; for each way of building, its rules and sizes by era (steps, walls, coursing and bonds, paving patterns, kerbs); and its parts. The first pack is the Norwegian west coast in 1989: the town's own slaty rock, dark blue-grey and laminated, split into slabs (flagstones, slab steps, dry-stone walls; Gamle Stavanger's, `docs/references/stone/` 02, 03, 06); Iddefjord granite, light grey, brought in (kerbs, setts, quay stone, dressed steps); a darker banded gneiss (walls, rough steps); larvikite as an accent; concrete from about 1890; dry-stone and mortared walls; field stone, then setts from about 1850, small setts in arcs from 1910 to 1950, asphalt after; kerbs 5, 8 and 12 inches wide by their year; granite quays with a narrow tide band.

## How stone is made

Five steps, each with one owner.

1. **Facts** (the engine, or a fixture): kind, built, use, tending, events; place computed from the town.
2. **Layout** (the plan; `blender/blockouts/heart_layout.py`): where the stone goes, as paths and edges: a flight along its lane with its width and levels, a wall where a lane is cut into the slope or stands over it, a quay's edge, a kerb, a square's field.
3. **Hand-made parts** (Blender, each judged alone; `blender/parts/stone/<kind>/`): per stone, a few pieces in a few sizes (step blocks, landing slabs, wall stones, copings, setts, kerbs, quay blocks, bedrock knuckles), each with real chamfers of its own size and no wear (wear comes from facts); a painted grain set per stone at our scale, with relief; and a few painted detail atlases (lichen discs, moss cushions, stains, cracks, tooling), rationed like the birch's bark marks.
4. **Assembly** (`blender/generators/stone.py`): lays the pieces by the era's rules, each seeded (its piece, its turn, its offset in the grain): a flight fitted to its path (rises and treads, each block on the one below, landings, cheek walls), walls bridging every joint, the biggest stones low, leaning back, setts in arcs; then applies the diary: each tread deformed by its wear, growth and stains placed by masks (shade and occlusion, run-off traced down the geometry, the footfall across a tread), repairs marked; and bakes per vertex what the shader reads (wear, polish, growth, stains, age, how much water a hollow holds).
5. **Unity:** one stone shader on the town's shading (one shade rule, `StreetLooks.hlsl`), drawing the history layers below; shared pieces instanced (the GPU Resident Drawer), a run of steps or a wall merged into one mesh with a proxy far off.

## The history layers

Every hard surface is drawn by the same stack, each layer from its cause, so a new material joins by bringing its own pigment and rules rather than a new system:

1. **Pigment and grain**: the material's own colour and painted grain, seeded per piece, never tiling (an offset and turn per piece, world-anchored noise across large surfaces).
2. **Tooling**: how it was dressed (split, hewn, sawn), on its faces.
3. **Wear and polish**: from the footfall map and the years; real geometry for the hollow and the rounded nosing, polish in the shading.
4. **Stains**: run-off streaks, green film, rust, soot, salt bloom.
5. **Growth**: nature's, not stone's (`docs/nature.md`, Growth on surfaces): the stone's facts give where and how long (lichen on what is quiet for its years, moss in the joints and at the feet, grass and ferns in cracks, ferns only in lime mortar), the pack's species what grows there, one shared layer draws it.
6. **Damage and repair**: cracks, spalls, bulges, lost corners; patches, campaigns and renewals, each its own material and date, from the thing's upkeep (`docs/upkeep.md`; `upkeep.py`; the repair parts in `blender/parts/repair/`).
7. **Weather**: wet (darker, glossier, water in the hollows), frost, snow and ice, fallen leaves, litter where people pass.

## Texture and detail

Texture is painted at our scale, as the bark is: the grain and its value painted into the pigment, relief in the alpha to bend the light, never a photo scan with light baked in. Detail follows the view, and the story:

- **In a scene** (close): tooling marks, the stone's crystals, fine lichen and the moss's texture.
- **At the street stop** (about 3 m up): the chamfers, the worn hollow and the polish on the walking line, lichen patches on the quiet ends, moss in the joints, stains under drips, a reset run's straighter line and cement joints, a cement dab in a broken corner.
- **From 12 m and the city camera**: the flight as a few value shapes (the polished middle, the darker quiet edges and the wall's damp foot), walls as banded courses with a lit coping; nothing that is only noise.
- **Far off**: merged proxies in flat value, carried by light and air.

## Our style

What makes stone in games look cheap, and what we do instead (`docs/research/stone.md`): tiling (a seeded offset and turn per piece, world-anchored noise); every edge chipped the same (wear only where contact and use put it); bevels only in the normal map (real chamfers, each its own size); grout as a regular grid (pieces laid by real rules, joints as broken accents); uniform noise (two or three values a stone, detail rationed to the story); light baked into the texture (pigment only, shade from the light by the town's one rule).

## How it is judged

Each piece on its own sheet, and each assembly in the corner's light (drizzle, low sun, and the gully steps' night), at the street stop, from 12 m and from the city camera, in colour, greyscale and at one-eighth: a flight built in 1850, 1920 and 1960 seen in 1989; busy and quiet; dry and wet; with a relaid step and a screed. A history test (a viewer says blind which flight is busy, which old, which step relaid, and is right), a variety test (twelve flights from fresh seeds: no two alike, every difference saying something true), a determinism test (the same seed the same after a reload), and a performance test (a town's steps and walls). Then the strict review (a fresh reviewer on Fable 5.1, checking the core rules) and Øystein's judgement, beside the reference board (`docs/references/stone/`) and the gully steps' target frame.
