# The building system

How buildings are generated, change over time and show their history. The research behind it is in the Project docs ("A world that remembers" and the topic docs).

## In short

A building is a diary of dated events. The engine writes the diary. A resolver turns the diary, read up to a given year, into a plan. Unity builds the plan from plain walls and roofs it generates itself and from detailed kit parts made in Blender. The same diary always gives the same building. Anything that reads as history (a later window, a ghost sign, a porch added in another era) is a fact from the diary; small seeded variation (a lean, a board width) is texture that claims no history.

## The diary

Each building has an id, a plot and a list of events. An event has:

- `year` (and month when it matters);
- `kind`: built, extended, repainted, reclad, windows replaced, converted, business opened, business closed, boarded up, neglected, restored, demolished;
- `layer`: the part of the building it changes (structure, skin, services, use, stuff);
- `params`: what the event did (an extension's side and size, a paint colour, a business's kind and name);
- `cause`: who decided it and why, as the engine logged it.

Layers follow Stewart Brand: structure changes rarely, skin every few decades, use every few years, stuff often. Showing year Y means reading every event up to Y.

The building also carries a character: **low road** (warehouses, sheds, factories: changed often and cheaply, uses come and go) or **high road** (villas, churches, banks: mostly repainted and repaired). It sets which events its diary may hold.

## Resolution

The resolver runs five passes, in this order.

1. Massing. Volumes from the diary: the main body and every extension, porch, veranda, bay window, dormer and lean-to, each with its own era, material and storey height.
2. Facade grid. Each facade is split into columns and storeys. Floor lines snap across volumes of the same era; a volume from another era keeps its own lines, so the seam shows its date. Every cell is tested against the building's own volumes and its neighbours: a window never sits where a wing or a neighbour meets the wall, and a window blocked by a later neighbour becomes a boarded cell dated to that neighbour.
3. Parts. Each cell gets a part: a window, door, shopfront section, plain wall or boarding. The part comes from the shelf of the era it was installed (see below).
4. Decoration and sockets. After the structure, a separate pass fills sockets: sign bands take signs, eaves take gutters, corners take downpipes, sills take flower boxes, shopfronts take awnings. A socket names the part types it accepts and sits relative to a facade edge, so it survives later changes.
5. Surfaces. Every surface is a stack of coats. A repaint adds a coat, neglect wears the top coat, a restoration strips back. Where wear goes through, the coat below shows: an older colour, an earlier shop's lettering, the line of a removed shopfront. Wear masks follow exposure, drips below sills and cornices, and the ground line. The shader reads one number per coat: years since it was applied.

## Parts come from the decade they were installed

Each part on a shelf carries a year range. A part is chosen in two steps: first filter by the installing event's year, then pick with a seed from `hash(worldSeed, buildingId, eventId, cell)`. A 1968 window replacement therefore gets a 1960s window, and a new event re-picks only the cells it touches. Additions are scored on whether they follow the host's lines (eave height, window rhythm); careful eras follow them, careless eras break them, so a street shows which decades looked after it.

## Materials

Material is chosen per volume from era, purpose, wealth and local rules (a masonry rule after a fire, brick for canneries, stone for banks). Each material has its own parts (stone lintels and brick arches for brick) and its own ageing: wood peels and is repainted, brick takes soot and salt bloom, concrete streaks and spalls, render cracks and is patched.

## Rules

- Hard rules keep everything buildable: a storey stands on a storey, an overhang has support, a window has a room behind it, every gutter has a downpipe, every door a path to a street. A plan that breaks one is rejected and reported.
- Soft rules shape taste: no two neighbouring fronts identical from the same era, detail at junctions and calm on walls. A soft rule that can't be met is quietly given up.
- Roofs are built over the combined footprint where possible, and fall back to one roof per volume when that fails validation.
- Stylisation is a set of parameters (proportion push, lean, sag, irregularity, trim size, bevels) shared by every generator, in named strengths: gentle, strong and stronger. Proportions (pitch, eave depth, board width, window size, trim) carry the boldness; deformation (lean, sag, bow) stays small, because it is what reads as caricature and what breaks construction. The wobble lives inside each piece; edges stay on the grid so pieces fit.

## Fitting

Every part fits where it is placed, or it changes until it does. A part never cuts into a roof, a wall or another part.

- A window, door or shopfront fits inside its own storey, with its crown or sign: under the belt course, and on the top storey under the roof's underside where the part stands out from the wall.
- A steep roof's overhang flares out at the eave (at most 50°), as a mansard's does, so the eave never swallows the top storey.
- Beside a cross-gable, parts stay under its side eaves; the eave falls away from the cross-gable, so a part's far edge is the one that counts. Gutters, brackets and cornices stop where the cross-gable's roof begins.
- A window in a gable stays under the gable's roof lines.
- A porch is solved before any wall is built. It narrows, lowers its pitch (down to nearly flat) and changes height until its roof stays under the sills above it, under the main eave and cornice, and clear of the windows beside it. The windows beside it then fit under its eave. Belt courses stop at a porch.
- When something still does not fit, it gives way in this order: it shrinks to two boards, its crown becomes simpler, it moves down within its storey, and last it is left out, which leaves plain wall. A diary fact (the porch) wins over a part the resolver chose (a window over it).

## Checks

Every built building is checked before it is rendered or exported (`blender/generators/validate.py`). Faces carry a role (wall, roof, facade part) and the part they belong to, so the checks read what a face is, not its colour.

- Uncovered wall: a ray goes up from the top of every wall face; it must hit something.
- Part through roof: no facade part (window, door, shopfront, crown, belt, cornice) may intersect a roof.
- Degenerate faces, and the triangle budget.

`blender/tools/stress.py` builds hundreds of random diaries at several years and strengths and runs the checks on each. No sheet leaves the lab unless the stress test passes at the strengths on it, the street fixtures pass, and the renders have been inspected at full resolution.

## Who decides

The engine decides every fact in the diary, including why. The resolver decides how a fact looks, from the diary and the seed. Unity builds and draws. Nothing in Unity invents a fact.

## Determinism

- Seeds come from explicit integer hashes (SplitMix64), never from language hash functions or `UnityEngine.Random`.
- The resolver works in integers: grid cells, millimetres, enum ids. Floats appear only when meshes are built.
- Anything iterated in a way that affects the result is sorted by a stable id first.
- A plan hasher resolves fixture diaries across many years and compares the hashes with committed ones, twice, the second time in shuffled order.

## Where it lives

The resolver is prototyped in Python (`blender/resolver/`) so it can run in Blender, headless or interactive. Once its rules settle it is ported to C# for Unity, and the plan hasher proves both give the same plans.
