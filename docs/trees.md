# Trees

How the town's trees are made, grown, aged and drawn. A tree is a part of the world with a history, like a building: what reads as history (its age, its pruning, the storm that took a limb) is a fact with a date; what claims nothing (the exact twist of a twig) is seeded texture. This is the design; how it was found is in `docs/experiments.md` (LT1, trees), and the research behind it in `docs/research/trees.md`.

## What we want

- **Each tree reads as its species and its age**, at the street stop and from the roofs: a viewer can tell a birch from a rowan, a young one from an old one, a planted avenue from a self-seeded yard tree, a pollarded tree from a free one.
- **Our style, not the generic one.** Painterly realism: true silhouettes, the crown built of structured masses with sky between them, branches seen through a thin autumn crown, colour in the shade; never a soft ball standing in for a crown (`docs/visual-direction.md`, no round blobs).
- **Time is real.** A tree grows from its planting or seeding year, and the same tree at age 31 contains the tree it was at 30. Seasons follow the date and the species. It can be pruned, pollarded, broken by a storm, felled, die standing and fall.
- **Every city brings its own trees.** The system knows nothing about Norway: a setting pack brings species, how they are planted and tended there, and the parts that draw them (`docs/visual-direction.md`, the setting is a pack).
- **It holds at city scale**, from one tree filling the frame to thousands across the map, at frame rate.

## The facts a tree carries

From the engine, or authored in a fixture until the engine has them (`docs/engine-requests.md`):

- *Species* (from the setting pack's list) and *origin*: planted (by whom, as what: an avenue, a garden tree, a park), self-seeded, or a remnant of what was there before the town.
- *Born*: the year it was planted or seeded; for a planted tree also the nursery age it was planted at.
- *Site*: where it stands, and what that does to it: open or crowded, sheltered or in the sea wind, rock or deep soil. The build follows from it: an open-grown tree gets light from every side and grows a massive trunk and a wide, tall crown; a crowded one (in a grove, a hedge, against a house) races up for light and grows long and skinny with a small crown high up; each tree's own inherited build varies it further (Øystein: some trees massive, wide and tall, others long and skinny). The site's quality scales the species' height curve, so a tree is as tall as its place lets it be: a birch on a knoll in the sea wind stays a few metres high, a spruce in a deep garden grows big; the species' top height is the setting's (here the west coast's), never a forest record.
- *How stout it grows* follows from the facts, never from chance alone: a trunk thickens with the leaves it feeds and the load it carries. Open-grown trees (a park, a field, alone on a knoll), old trees, the big species (beech, oak, lime, sycamore, horse chestnut), trees on deep soil and old cut or pollarded town trees grow big trunks; crowded trees (a grove, a plantation, a hedge) grow tall and slim with a small crown high up; young trees, the slim species (birch, rowan, alder, aspen, willow), thin soil and rock keep slim trunks; a tree of several stems has slimmer stems. Each tree's own build varies it within that (seeded), and the wind makes it stouter for its height.
- *Events*, each dated: pruned (crown raised, thinned, reduced), pollarded (and how often), storm damage (a limb lost), disease, lopped for a cable or a view, felled (leaving a stump), died (standing dead wood, then fallen). In town the big old trees with fat trunks are the ones cut (Øystein): heavy limbs taken off at the trunk to keep them from growing wild, leaving a flat stub with a callus ring, a trunk still as thick below the cut as the limb once needed, and thin water shoots round the wound in the years after.

The season comes from the date and the place's climate; the weather's wind from the day.

## How time works

A tree's whole life is grown once, deterministically from its seed and its facts, year by year: every branch knows the year it grew, how thick it was each year after, and the year it was shed or cut. To draw the tree at a date, the timeline is read at that year: branches not yet born are absent, shed ones gone, each at its thickness then. So the tree is the same from one visit to the next, and older trees contain their younger selves; an event changes the timeline from its year on, and nothing before it.

Seasons are a second clock on top: leaf-out, full leaf, autumn colour, leaf fall, bare, and snow on the branches, each species at its own dates for the latitude, shifted a little by the year's weather (a cold autumn colours earlier and redder: `docs/research/nature.md`).

## A setting pack's trees

A pack brings, for each species: its habit (how it grows: the rules and numbers the timeline follows), its parts (bark, twigs, leaf and needle clusters, flowers and fruit, each season's version, made by hand and approved one at a time), its phenology, and how the place tends it (pollarding for London's planes, the Norwegian garden birch left to itself). The first pack is the Norwegian west coast in 1989: downy and silver birch, Norway spruce, rowan, Scots pine on the rock, sycamore as the big town tree; later aspen, lime, horse chestnut, elm, willow, juniper.

## How a tree is made

Five steps, each with one owner (after the research: `docs/research/trees.md`).

1. **Facts** (the engine, or a fixture): species, origin, born, site, events.
2. **The growth timeline** (offline, once per tree, cached; `blender/generators/tree_growth.py`). A self-organising tree after Palubicki et al. 2009: each year its buds grow or wait by the light they get, the share of an overcast sky each sees through a grid of the tree's own foliage and of its neighbours (houses, walls, other trees, from the site facts), and grow towards where it comes from; apical control set by the species and loosened with age, so a young tree is tall and an old one broad; shaded branches shed; trunk and branch widths by the pipe model, which remembers shed and cut branches, so an old cut still shows in the trunk. The species' crown masses (step 3) steer it as an envelope. Events apply between years: pruning, pollarding with its regrowth, a storm's lost limb. Every node keeps its birth year, its death or cut year and its width by year; drawing the tree at a date reads the timeline there. Seeded from the tree's id and stable node ids. The habit and the simulator are versioned: changing them would rewrite every tree's history, so a change is a new version, never a silent edit. When a site fact changes (a house built beside it in 1975), the tree regrows from that year only.
3. **Hand-made parts** (Blender, each judged alone; `blender/parts/trees/<species>/`): per species, a few bark sets by age; five to eight clump and twig modules (sprays of leaves or needles, flowers and fruit), each with painted masks for colour, the order its leaves fall and how much light shines through; and the crown masses: three to five faceted volumes per species and age, the way a painter blocks a tree, with sky between them. The masses are both the growth's envelope and the shape the crown shades by. Few variants, made well (Firewatch built 23 trees for a whole game).
4. **Assembly** (`blender/generators/tree.py`): read the timeline at the year; sweep branches as tubes with collars where they join, faired by their thickness (thick wood bends in curves, a twig keeps its zigzag); place clumps on the living shoot tips and, on a birch, on the short shoots along its long shoots (so a limb is clothed along its length, never bare to a tuft), each tied to its node so a branch keeps its clump for life; bake into the mesh the branch hierarchy, pivots and phase for wind, the crown's own occlusion, and normals from the masses; build the distance levels: branches thinned, fewer and larger clumps with density shells in the crown's core, then an impostor that knows the tree's state (in leaf or bare, pollarded, dead), so the far view never contradicts a fact.
5. **Unity:** clump meshes shared and instanced (the GPU Resident Drawer), per tree its season, hue and wind phase as instance data; trunks unique and cheap; alpha with coverage-preserving mips, edges smooth by alpha-to-coverage or hashed alpha; light through the leaves as a wrapped back term, strongest against a low sun; wind from one deterministic gust field over the town, seeded by the day's weather, in two levels of motion and a ripple, fading with distance; levels cross-faded by dither.

## Detail by view

The town view and the scenes share one style and one set of rules, at different levels of detail (Øystein): in a scene the camera is close, so a tree draws its finer twigs, more of its leaf parts and its bark close to; from the street stop the twigs finer than a pixel are carried by the painted twig fans; far off, impostors. The same tree, its facts and its timeline, at each.

## Seasons in the shader

Each clump has a seeded rank. The species' phenology at the date (leaf-out, full leaf, autumn colour, leaf fall, bare) sets the leaves' colour and how many have fallen: clumps colour and fall in rank order, so the same leaves always turn first, and the tree on 20 October is the same tree on 21 October with a few more leaves gone. Snow lies on the branches' upper sides by the snow's depth. Oak and beech keep their dead leaves into winter (marcescence), a species' fact.

## Our style

What makes a game tree look cheap, and what we do instead: regular, recursive branching and bonsai proportions (self-organised growth, branches that run long before they split); flat sheets of cards without air (clumps with gaps, sky through the crown); noisy, snapping shading (normals from the masses, so a crown shades as three to five planes of light and shade, not as a thousand cards); alpha thinning and shimmer at distance (coverage-preserving mips); level-of-detail waves and popping shadows (dithered cross-fades, shadows chosen per cascade); synchronised, over-bent sway (a gust field, renormalised bending); too many variants (a few, made well); and above all the soft sphere for a crown, which our direction rules out. In October, when the birches are thin, the branch structure is the drawing.

## How it is judged

Each species on its own sheet in the corner's light (16:00 and 17:50 in sea fog): five ages (5, 15, 30, 60 and 100 years), four seasons (May, July, 20 October, January), at the street stop, from the city camera just over the ridges looking into the crown (about 12 m up), from the roofs and from higher, steeper stops, in colour, greyscale and at one-eighth. A silhouette test (the species named blind at one-eighth), a growth test (each age contains the one before), a variety test (twelve seeds of one species and age: each different, all the same species), and a performance test (a street of two hundred trees, a town of five thousand). The strict review (a fresh reviewer on Fable 5.1), then Øystein.
