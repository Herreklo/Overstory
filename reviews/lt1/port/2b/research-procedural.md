# Procedural masonry: how others generate walls, steps and packing

For the stone redraw, 22 October 2026, Opus 5.5, online only. (primary): the makers' own page or paper, read. (secondary): a search summary, forum or abstract snippet. (unverified): unconfirmed, or our arithmetic. Three PDFs (Legakis, Peytavie, Wang 2025) would not open.

## In short

- **Lay out in 2D, features before fill.** Place ends, quoins, the rake, the 1961 panel's edges and the coping first, then fill courses between, tracking what is taken (Legakis's order and occupancy maps). Every stone is settled on the unrolled elevation, in integer mm, before any mesh exists.
- **Fill a course by choosing, never stretching.** Unreal's grammar can scale a module into leftover length; Burger rounds the wall to whole bricks. One breaks our rule, the other our facts. Redraw the last few lengths within range, then close with one cut stone above a minimum length (PCG's `<A,B,C>` fallback).
- **Bond is a number, and every sheet is measured.** Reject a perpendicular joint within a minimum lap of one below, forbid four-stone crosses, cap the longest straight joint (Derouet-Jourdan). Measure with the engineers' line of minimum trace and the longest joint.
- **A stone is a judged convex slab trimmed by planes.** Split slaty rock breaks along planes, so a few planar faces are true to the material and cheap. A plane cut keeps a convex block convex, so its collision hull stays valid (Embark's reasoning).
- **Choose the stone that fits, as robots do.** Dry-stone robots and packing papers pick from an inventory of rigid stones by a fit score; none deform one. Score a few dozen candidates (forms × flips) per slot by least cut and best bed.
- **Budget by what is seen.** Peytavie's piles cost about 132 triangles a stone. Ours can cost 20 to 40 with buried faces dropped, under 1,000 a square metre (unverified). Far levels merge stones into course strips, then a slab baked from L0 (Unreal's HLOD).
- **No public studio talk shows a rigid, cut-to-fit masonry generator.** There are breakdowns, product docs and engineering papers; the papers' metrics are the best thing to borrow.

## 1. Tools and talks

- **Fabien Burger, wall generator for Unreal in Houdini** (primary). Points along a line, each replaced by one of three same-size bricks with different bevel seeds and one shared UV unwrap. Length is rounded to whole bricks (5.5 m becomes 5.4 m). Alternate rows offset half a brick. Damage by selection: bricks inside a cutter deleted, edge bricks turned 0 to 40 degrees about a corner pivot, about 10 % of plain bricks kept as relief over a base wall. Collision is separate named pieces. Borrow the shared UV and damage by selection; avoid the rounding and fixed offset.
- **Unreal PCG shape grammar** (primary). Modules along a spline: `A*`, `A+`, weighted `{…}`, fallback `<A,B,C>`. Each module has a size and a `scalable` flag that stretches it into leftover space (Python API, secondary). Both ends of a module sit on the spline, so rigid modules lie on chords; Epic warns tight corners come out wrong. At a bend or change of pitch, chords leave wedge gaps, which a mason fills with a tapered, cut stone. **Self Pruning** drops overlapping points by extent (secondary): rank, then drop, never squash.
- **Embark, Building Creator for THE FINALS** (primary). Feature nodes share global parameters (wall thickness, floor height). A window module is a visual mesh, a boolean cutter and sockets. Each feature keeps a simplified planar outline, split in 2D into convex pieces and extruded into collision hulls, fully automated. No masonry: trims are authored meshes.
- **Houdini forum, Roman wall** (secondary). Grid rows plus jitter with a bevelled box per point fails on varied sizes, overlaps and gaps; the reply is to split a wall volume into cells. A Lego-wall asset picks bricks from a fixed set by weight.
- **Blender.** A geometry-nodes stone fence fills an extruded curve with stones between a minimum and maximum width (secondary). A packing add-on warns that stones large for their space leave holes, and one style lines up on long runs (primary docs).
- **Substance Designer** (Tuur Sangers, Yager; primary). A per-stone id drives variety: flood fill to gradient at varied angles gives each stone its own tilt; flood fill to random grey drives warp and colour. Users find tile-generator stones too alike and tile random's order unreal (Polycount, secondary). Borrow: per-stone ids drive tilt, tint and wear in the shader.
- **Tiny Glade, Townscaper.** Tiny Glade's stone method is not public. Opara: structure first, randomness after (primary). Townscaper deforms modules into cells: the opposite of our rule.

## 2. Academic work

- **Legakis, Dorsey, Gortler, SIGGRAPH 2001** (secondary). Bricks turning corners, stones framing openings. Features are done in a fixed order; occupancy maps record what neighbours already filled. The order our generator needs.
- **Derouet-Jourdan, Salvati, Jonchier, CGF 2019** (OLM Digital; primary). A Wang tile is a four-stone corner. Tiles making a cross are removed, leaving vertical-joint and horizontal-joint tiles. A hash (FNV seeding xorshift) sets edge colours, a 2×2 solver fills between, and fixed checkerboards on diagonals cap every straight line at n tiles. Any cell is evaluated alone. Stones are rectangles. Crosses and long lines are named faults with a deterministic cure.
- **Peytavie, Galin, Grosjean, Mérillou, CGF 2009** (secondary). Aperiodic tiles; rocks from Voronoi cells under an anisotropic distance; walls and huts of thousands of rocks, no simulation. A cover model: 17,504 stones, 2,315,840 triangles.
- **Engineering packers.** Shaqfa and Beyer (2022) pack stones as a constrained optimisation mimicking a mason, Python under LGPL (secondary). Wang et al. (2024) stack non-uniform stones in 2D walls by image convolution, with wedging, judged by a rigid-block model (primary abstract). Wang and Beyer (2025) compare generated and real walls on size, aspect, sphericity, vertical interlocking and course horizontality (primary abstract). Robots (Wermelinger; Liu, Napp; Johns, ETH) choose each next stone and pose from a scanned inventory by support and stability (secondary). All keep stones rigid.
- **Masonry quality index** (Borri, Corradi, Castori 2015; secondary via a thesis). Engineers grade walls by rules of art, among them staggered joints, measured by the line of minimum trace: the shortest top-to-bottom path through joints across a panel. Longer is better bonded; one quoted threshold is over 160 cm for stones over 40 cm (unverified).

## 3. Steps and stairs

No public generator lays several stones per tread with laps (searched Houdini, PCG, Blender).
- **Flights from a path** (McNeel forum, secondary): a new flight starts when the run exceeds steps × going plus a minimum landing (about 1.85 m there); rise and going fixed within a flight.
- **Fitting** (Superhive Procedural Stairs, primary docs): step height is a maximum rise, adjusted so the flight meets its ends; depth is a target going; a level edge is a landing.
- **Collision**: a ramp under visible steps (Unity, Panda3D forums, secondary), as our walker already does.
- **For us** (proposal, unverified): a tread is a course on its own bed. Run the wall's fill rule with the bond test against the tread below, so joints break. The nosing laps the riser by a fact. At a rest the cheek wall's courses step; the coping takes one raking cut per flight.

## 4. Making it cheap

- **Flat faces are the material.** A slab of 6 to 10 planar faces plus two or three chip planes carries the form; split-face roughness lives in normal and height maps. About 20 to 40 triangles a stone with backs and buried beds removed (unverified).
- **Arithmetic** (unverified). Mean course 10 cm, mean stone 40 cm: about 25 stones a square metre, so about 750 triangles at 30 a stone, against 3,300 at Peytavie's density. At 1440p with a 60° vertical view, a 40 × 10 cm face is about 100 × 25 px at 5 m, 42 × 10 at 12 m, 16 × 4 at 30 m. So: chips to about 10 m; plain stones merged per course chunk to about 25 m; course strips with joints in texture beyond; a slab baked from L0 far off. Unreal's HLOD merges and simplifies meshes under a baked material (primary).
- **Small library, no repetition.** About 8 judged forms per class × 4 flips (end for end, face for back) = 32 candidates. Every cut changes a silhouette. A hashed per-stone texture offset (`stone.md`) and per-stone tint and wear do the rest.
- **Merge per chunk** (Kronenberger in `kits-and-generation.md`); collision from the wall's planar outline as a few convex hulls (Embark).

## 5. Pitfalls and fixes

| Fault | Named by | Fix |
| --- | --- | --- |
| Half-stone offset, running bond look | Burger's method | drawn lengths; minimum lap, not a fixed offset |
| Crosses, long straight joints | Derouet-Jourdan | forbid crosses; cap and measure the longest joint |
| Alignment on long runs | Superhive | measure; course heights seeded per course |
| Shapes alike, no real order | Polycount | choose by fit; largest low |
| Holes where stones are big for the space | Superhive | closer with a minimum; refuse fits loudly |
| Uniform joints | Blender Artists | joint width from each stone's fit |
| Stones "cut and glued" on, no mass | Polycount | real depth, through-stones, ends showing beds |
| Stretched or deformed modules | PCG `scalable`, Townscaper | forbidden: cut, taper, step |
| Every edge chipped, one rounding | (unverified, ours) | chips from causes: exposure, feet, 1961's fresh cuts |
| Floating or sunk stones | (unverified, ours) | drop to the bed line; check contact and gaps per stone |

## Sources

Tools: Fabien Burger, [procedural wall generator for Unreal in Houdini](https://80.lv/articles/creating-a-procedural-wall-generator-for-unreal-in-houdini/) (80.lv) · Epic, [shape grammar with PCG](https://dev.epicgames.com/documentation/en-us/unreal-engine/using-shape-grammar-with-pcg-in-unreal-engine) · Epic, [PCGSubdivisionSubmodule](https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/class/PCGSubdivisionSubmodule) · Epic, [PCG node reference](https://dev.epicgames.com/documentation/en-us/unreal-engine/procedural-content-generation-framework-node-reference-in-unreal-engine) · Epic, [World Partition HLOD](https://dev.epicgames.com/documentation/en-us/unreal-engine/world-partition---hierarchical-level-of-detail-in-unreal-engine) · Adrian Björkerud (Embark), [procedural buildings of THE FINALS](https://www.sidefx.com/community/making-the-procedural-buildings-of-the-finals-using-houdini/) · SideFX forum, [procedural Roman wall](https://www.sidefx.com/forum/topic/80477) · Giuseppe Flora, [procedural Lego wall](https://www.sidefx.com/tutorials/create-a-procedural-lego-wall/) · Superhive, [Procedural Stone Wall docs](https://superhivemarket.com/products/procedural-stone-wall/docs) · ne3dward, [stone fence](https://ne3dward.gumroad.com/l/stonefence) · Tuur Sangers, [varied rock walls in Substance Designer](https://80.lv/articles/001agt-creating-varied-rock-walls-in-substance-designer) · Polycount, [tile bricks](https://polycount.com/discussion/comment/2577268), [stone hut](https://polycount.com/discussion/comment/1210122) · Blender Artists, [procedural stonewall](https://blenderartists.org/t/realistic-procedural-stonewall-for-2-8/1282351) · Anastasia Opara, [procedural architecture](https://80.lv/articles/realistic-procedural-architecture-for-games/) (80.lv).

Papers: Legakis, Dorsey, Gortler, [Feature-based cellular texturing](https://graphics.cs.yale.edu/node/159) · Derouet-Jourdan, Salvati, Jonchier, [Wang tiles for wall patterns](https://ar5iv.labs.arxiv.org/html/1706.03950) ([CGF](https://diglib.eg.org/handle/10.1111/cgf13635)) · Peytavie, Galin, Grosjean, Mérillou, [rock piles](https://diglib.eg.org/handle/10.2312/CGF.v28i7pp1801-1809) and [cover model](https://vcg.isti.cnr.it/cgf/winner.php?year=2010) · Shaqfa, Beyer, [virtual microstructure generator](https://infoscience.epfl.ch/record/294854) · Wang et al., [image-convolution stone packing](https://experts.umn.edu/en/publications/an-image-convolution-based-method-for-the-irregular-stone-packing/) · Wang, Beyer, [rubble walls from 2D images](https://www.canadamasonrydesigncentre.com/research/3d-microstructure-generation-of-rubble-stone-masonry-walls-from-2d-images/) · Wermelinger et al., [greedy stone towers](https://ijcai.org/proceedings/2018/760) · Liu, Choi, Napp, [robotic dry stacking](https://impact.ornl.gov/en/publications/planning-for-robotic-dry-stacking-with-irregular-stones/) · Johns et al. (ETH), [excavator dry-stone wall](https://techxplore.com/news/2023-11-autonomous-excavator-meter-high-dry-stone-wall.html) · Borri, Corradi, Castori, [masonry quality index](https://link.springer.com/10.1007/s10518-015-9731-4), via [a Politecnico di Milano thesis](https://www.politesi.polimi.it/retrieve/a81cb05b-34f5-616b-e053-1605fe0a889a/11.pdf).

Stairs: McNeel forum, [staircases on terrain](https://discourse.mcneel.com/t/generative-staircases-on-terrain/127400) · Superhive, [Procedural Stairs docs](https://superhivemarket.com/products/procedural-stairs/docs) · [Unity](https://discussions.unity.com/t/what-is-a-good-size-for-stairs/16686) and [Panda3D](https://discourse.panda3d.org/t/raycast-character-controller-handling-stairs/14050) forums on ramps.
