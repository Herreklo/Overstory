# R2a's stones in Blender: the step, the machinery, the export

Port step 2b, rung R2a, the Blender half (`plan.md` in this folder is the contract). Written 23 October by the Blender agent (Opus). It covers the step and the shared machinery, built, checked, exported and installed. The wall stone and the coping follow in a later section. No reviewer has passed anything here.

## In short

- **Built.** `blender/parts/stone/slate/block.py` is the machinery: rigid convex blocks cut by planes, facets, chips, chamfers at L0, a wear field subtracted, hidden faces not drawn, skirts and covers, and a triangulation sized for the screen. `blender/parts/stone/slate/stones.py` holds the step as a part function whose inputs are facts, with its checks, export, quick sheet and CLI. The definition is `packs/stavanger-1989/parts/stone/step.json` (draft; `tools/validate_record.py` passes).
- **The specimen** is `st-gully/fl-0/tr-9/sl-1`, chosen by a rule (below). It has L0 144 of 300 triangles and L1 69 of 120. In the gate view (face-on, 20° of top), 7.3% of its L0 triangles are under 2 px at 8 m (median 103.7 px²) and 5.0% of L1's at 20 m. L1 lies within 8.51 mm of L0 (limit 11). Every check passes, and two builds are identical.
- **Every step stone the gully lays** (134, the ordinary steps of both flights as R1 laid them) is built and passes every check of its own. The steps alone fail SN8's thin-triangle share at L0: 13.7% (1,689 of 12,298 front-facing triangles) under 2 px at 8 m. L1 passes at 4.9%. Chamfers make 10.8 points of the 13.7: SN4's 10 to 12 mm chamfer is 2.5 to 3.6 px at 8 m by design, so any chamfer seen more than about 45° off its normal falls under 2 px. SN8's share belongs to the level (the whole gully, fills included), so the export reports it and does not hold on it. R2b lays the level and R3 measures it.
- **Risk, with numbers.** For the gully to pass at 10%, the walls (W front-facing L0 triangles at share x) need x ≤ (0.10 (12,298 + W) − 1,689) / W: about 9.4% at W = 80,000. The wall stones have four chamfered arrises each, a bottom one seen 55° to 65° off from 20° above, so they will be harder than the steps, not easier. The wall stone's own number comes with its section.
- **Exported** as `unity/Assets/Experiments/LT1/R2a/Generated/step.fbx` with its sidecar `step.json` (git-ignored, installed under `install_lock`). The mesh hash is `df9d7a1ae9f8d7ab`, in `blender/parts/stone/slate/stones.manifest.json`. Read back with Blender's FBX parser: positions exact, normals flat (each its triangle's own), all eight UV layers bit for bit.
- **One conflict for the Unity side.** `LT1R2a.cs`'s `Pivot()` expects L1's bounds to start at (0, 0, 0). They start at (0, −30, 0) mm, because the riser runs 30 mm below the bed (its skirt). The pivot is the bed's front left corner, as the definition says. The sidecar's `bounds.L1.minMm` gives the expected minimum.
- **Data and code.** Every fact comes from data. Each value is read through one function that records its source in the sidecar. The part's own numbers sit in a `PARAMS` table in `stones.py` as the defaults of a proposed `params` object, because `part.schema.json` is closed. `slate.json` needs a `cornerBreak` field. `kinds/stair.json` disagrees with R1's walling table on the lap and the tread joint.
- **Checks.** `tools/check.py` does not exist yet; it is built after the 26 October reset. I ran this note's own tests (`stones.py check` and `flight`, the export's readback) and `tools/validate_record.py`, which passes.

## The step

### The specimen, by rule

`specimen_step` takes the first flight. Of its ordinary steps (not the first, whose block runs under the lane; not a rest; not the last, which nothing laps), it takes the one whose rise lies nearest the set-out rise, with the lowest index on a tie. That gives `tr-9`, rise 166 against the set-out's 167. The stone is the one of R1's laying (`masonry.lay` at the pinned commit) that carries the walking line, the flight's centre. Its wear is all on it. Its history comes from the stair's life stage: placed 1874, reset in cement in 1952, and a corner broken in 1897 (56 mm, left), filled with cement in 1986. Its left end is a joint (8 mm) and its right end goes into the wall. The rule and every candidate's rise are printed into the sidecar (`rule`).

### How a stone is made (block.py)

- **The block.** A stone is the intersection of half-spaces `n · p ≤ d` in its own frame (x along from its left end as the street sees it, y back from the riser, z up from the bed). Faces have roles: exposed (drawn), hidden (bed, back, walled ends: not drawn), and cover (a neighbour over the faces: here the next step, lapped on).
- **Skirts.** A drawn face that ends at a hidden face or a cover runs 30 mm past it, so a neighbour's joint, fill or wear never opens a gap. The checks measure what each skirt must reach. The top must run under the next step past its riser's foot (a facet's set-back of up to 25 mm, plus SN9's 3 mm contact: 28 mm). The riser must reach below its bed past the worn top of the step below (2.2 mm worn plus 3 mm: 5.2 mm).
- **Facets (SN4).** Each stone draws its laminae by seed from the top down, whole mm, at least 50 mm apart. A split face breaks back only at a lamina: a convex fold, stepped 15 to 25 mm, so the block stays convex. Two faces that meet at an arris never break at the same lamina, so every corner is three-faced and the chamfer between them is never cut into slivers. Risers have one facet (weight 3) or two (weight 1); open ends have one to three.
- **Chips (SN4).** A chip is a planar cut at a corner of the mass. One goes only where a fact puts it (the life stage's broken corner), or at an open end's top front corner by seed (250 per mille). A broken corner of slate breaks down to a bedding plane, so the stone's nearest lamina sets its depth. Where the record's size would make a chip face under SN9's 50 mm, the bite grows by the least whole per mille that clears it (`chip_least`). The fact is drawn a little larger, never smaller or missing, and the sidecar gives `sizeMm` and `grownPerMille`. The specimen's 56 mm corner needed no growth; in the pool, two corners grew by 37 and 99 per mille. A chip the record says was filled is cut after the chamfers: under its fill its edges are joints, not arrises.
- **Chamfers (SN4), at L0 only.** Every exposed arris gets a 45° chamfer, its leg (along each face, as a mason gives it) 10 to 12 mm by seed per stone. An arris is any turn of 20° or more between two faces; a face's own facets never make one. L1 is the same planes without the chamfers. Its lit line is kept in the shading by the edge distances (UV6 and UV7).
- **The wear (SN4).** `wear.py`'s laws (footfall times years over the stone's hardness, where feet land) are subtracted as a height field. Rows fall within each level's error (L0 1 mm; L1 half its 11 mm), never narrower than 2 px at the level's far edge. Columns sit at most 120 mm apart across the walking line. The field is flat wherever the wear is under a tenth of L0's error, so unworn stone merges into few faces. The block is cut by the field's triangles column by column, and nothing else moves a vertex. Where the nosing's run-out falls within 2 px of a column node or a chip's crossing, it snaps to it. Columns are inset by the chamfer at a chamfered end, so no column lands a fraction of a mm from the chamfer's foot.
- **Seen regions.** A joint end is drawn only where it is seen (SN5: a fill no deeper than the joint is wide). That is a band behind the riser, facet by facet, below the top, and behind a chip that breaks the end's corner. The band is the widest joint, plus the wear on the end's top, plus SN9's contact, and never less than the chamfer plus 2 px. A chamfer on such an end's arris is clipped to the same band.
- **The surface.** It is merged face by face and made conforming (no T-junctions). Edges under 2 px collapse where the faces about them lie flat within half SN9's planarity (0.05 mm). Corners that only lie straight along an edge are thinned out. Each face is triangulated exactly, for the fewest triangles whose altitude is at least the 2 px size; of those cuts, it takes the least thin (`tri_cost` = under-size count + 0.01 (size / altitude)²).

### What the checks hold (every stone, both levels)

| Check | Rule | Specimen |
| --- | --- | --- |
| budgets | SN8: 300 / 120, L1 at most 60% of L0 | 144 / 69 (0.479) |
| planarity | SN9: every face on its plane within 0.1 mm | 0.0 mm |
| convexity | every vertex inside the block and its skirts | 0.0 mm |
| welds | no two vertices within 0.1 mm that are not one | none |
| T-junctions, manifold | none; open edges only on a hidden face, a cover or a seen region's edge | 0; 32 and 19 open edges, all on those |
| slivers | SN9: no block face under 50 mm or 25° | riser 66 mm (42.2°), chip 64.5 mm (50.1°) |
| no rake | top and bed level | level |
| hidden faces | none drawn | none |
| contract | UV0 metric to 1e-6; UV1 one value; UV2 kinds; UV7 code whole, L0 mask 0, its chamfer the stone's; L0's edge distances exact | passes |
| wear | the drawn top within each level's share of wear.py's field, sampled every 2 mm | L0 0.835 mm of 1; L1 5.44 of 5.5 |
| L1 against L0 | two-sided, sampled every 2 mm; no L1 face on a chamfer's plane | 8.51 / 6.03 mm of 11 |
| chamfer width | every chamfer seen within 45° of its normal is at least 2 px at 8 m | 3.56 px square on, 2.52 px for its leg face-on |
| skirts | reach as above | 30 mm against 28.0 and 5.18 |
| facts | lap within walling's [40, 60]; joints within [4, 10] | lap 49, joint 8 |
| determinism | a second build identical, bit for bit | yes |
| thin triangles | SN8 in the gate view, per piece for the specimen; pooled for the steps (below) | 7.3% L0, 5.0% L1 |

Other views are measured and reported, not gated. From eye height (1.6 m), a tread at 20 m is seen at 4°, where any cut of it is under 2 px; there 63% of L1's front-facing triangles are thin. Four variants exercise inputs the specimen lacks: an open end with facets and a seeded chip, both ends walled, a 700 mm stone off the walking line, and the specimen without its corner. All pass every check.

### The pool: every step stone the gully lays

`stones.py flight` builds all 134 stones of the ordinary steps of both flights, as R1 laid them, at the pinned commit (6 processes, about 172 s). It writes `flight-check.json`, and the export refuses to run unless that file is current (the same code and data ids) and every stone passes.

| | L0 at 8 m | L1 at 20 m |
| --- | --- | --- |
| triangles per stone | 61 to 152, median 103 | 23 to 69, median 44 |
| under 2 px, pooled | 13.7% (1,689 of 12,298) | 4.9% (240 of 4,916) |
| per stone | 6.6% to 30.1%, median 16.6%, 81 over 10% | 0% to 18.2%, median 6.9%, 29 over 10% |
| median visible triangle | 63.1 px² | 55.9 px² |
| smallest altitude | 0.264 mm | 2.46 mm |

The specimen, at 7.3%, is better than the median stone. It is long and carries the walking line, so its big tread triangles dilute its chamfers. The worst stones are short ones with a chipped corner (up to 30%).

Where the L0 thin triangles come from (each classed by its 3D altitude and the angle it is seen at):

| Source | Share of all L0 front-facing triangles |
| --- | --- |
| chamfer pieces narrower than 2 px square on (corner caps where three chamfers meet, the worn nosing's remnant of the chamfer) | 5.7% |
| chamfers seen more than 45° off their normal (an end's chamfers face-on; the riser|end chamfer 50° to 56° off) | 5.1% |
| face pieces narrower than 2 px square on | 1.4% |
| slivers under 2 mm in 3D | 0.9% |
| faces seen more than 45° off | 0.5% |
| other | 0.1% |

Chamfers make 10.8 of the 13.7 points. That is SN4 against SN8 in its plainest form: a 10 to 12 mm chamfer is thin by nature at 8 m, as the design's table of the pre-mortem says ("the gate is by pixels, not aspect, since a chamfer is thin by nature"). Without them the steps would be near 3%. The machinery already does what it can: chamfers stop at three-faced corners, columns stay off a chamfer's foot, and edges under 2 px collapse.

### The gate's policy, and why

SN8 says thin triangles are counted over "the level's front-facing triangles, the fills included". So the steps alone cannot pass or fail it; the gully does, at R2b's laying and R3's measure. The flight reports the steps' pooled share (`shareOk`, `shareFails`, `shareRule` in `flight-check.json` and the sidecar). It holds every other check on every stone (`ok`), and the export holds on `ok`. The specimen alone is also held to the share in the gate view, as Unity's harness measures one piece.

## The export

- **Route.** FBX plus a sidecar per part, L0 and L1 as two objects (`step_L0`, `step_L1`), through `stone.py`'s `_export_fbx` and `install_lock` (imported, never edited). The export is flat-shaded, forward +Z and up +Y with the space transform baked, so Unity's mesh holds x along, y up, z back with no turn on its object.
- **Readback.** Before the install, the export is written to a scratch file and read back with Blender's own FBX parser, as `mesh_hash` does, never re-imported. It checks the triangles in order, the positions exact against the map, and the normals flat: a triangle's three corners carry one normal, it is the normal of the triangle's own corners in the file (to 1e-5, float32's arithmetic), and it lies on the face's plane within what rounding the positions to float32 allows a triangle of its altitude. All eight UV layers must match bit for bit by name. The same meshes exported twice must hash the same. The installed file must hash as the one read back.
- **Sidecar** (`Generated/step.json`): objects, pivot, frame, bounds per level, triangles, the chamfer and its form (`chamferMeasure` "leg", 45°), the channels by name, the facts and the specimen's rule, the outline's numbers (facets, chips, laminae, wear rows and columns, each face's kind, patch slice, mode and offset), every check's result, the pool's summary, the readback's notes, the mesh hash, and every input with its source (`data`) and content id (`code`).
- **The pivot and the skirts.** Bounds: L0 and L1 from (0, −30, 0) to (2295, 166, 327) mm in Unity's frame. The −30 is the riser's skirt below the bed; the 327 is the top drawn under the next step to its skirt (the going 297 plus 30). The block itself is 346 deep (the going plus the 49 mm lap).

## The quick sheet

`blender-sheet.png` (Workbench, lock-aware: it waits while a timing run holds the Unity lock). It shows the specimen at both levels in the gate's view, magnified, with its thin triangles red; each level raised 45° and from 40° left; the four variants; the skirts from behind and below; and the wear from above, blue the deepest. It checks that the machinery works and judges nothing. Each triangle is coloured by its kind: grey the top, orange a chamfer, blue-grey a split face.

## Data and code

Read from data, each through one function in `stones.py` that records the value and its source in the sidecar's `data`:

| Value | From |
| --- | --- |
| world seed, show year | `packs/stavanger-1989/pack.json` |
| built year, footfall by period | `fixtures/records/st-gully.json` |
| flights, steps, set-out, width, lean | `fixtures/golden/stair/plan.json` (the plan stage's output) |
| a stone's placed year, its broken corner and fill, the step's reset | `fixtures/golden/stair/life.json` |
| the wear rate | `packs/stavanger-1989/materials/slate.json`: `wearUmPerCentury` |
| the steps' lap [40, 60] and tread joint [4, 10] | `packs/stavanger-1989/walling.json`: `workings.dry-split-1874.steps` (R1's), with `kinds/stair.json` as the fallback |
| each stone's outline, joints and the next step's front | R1's laying, `masonry.lay` run in memory at the pinned commit on R1's facts, `kinds/wall.json`'s plan params and the walling table (never the git-ignored `layout.json`) |
| the patch slices | `blender/parts/stone/slate/patches.manifest.json` |
| the levels' errors and budgets, the pivot | `packs/stavanger-1989/parts/stone/step.json` |

Proposed, with a documented default in code until the file takes the field:

- **The part's own numbers → a `params` object in the part definition.** `part.schema.json` is closed (`additionalProperties: false`), so I did not add it. `PARAMS["step"]` in `stones.py` holds the defaults, read only through `param()`, which prefers the definition's `params` the day the schema takes them: `chamferMm` [10, 12], `chamferMeasure` "leg", `arrisMaxDeg` 160, `riserFacets` [[1, 3], [2, 1]], `endFacets` [[1, 2], [2, 1], [3, 1]], `facetStepMm` [15, 25], `facetLeastMm` 50, `chipPerMille` 250, `chipLegMm` [50, 80], `skirtMm` 30, `nosingReachMm` 50, `wearGridMm` 120, `wearFlatShare` 100, `l1WearShare` 500, and `patches` (the slice sets per face). The proposal: `params`, an object of named numbers, ranges and weighted choices, free per part and documented by the part's function.
- **`slate.json`: `cornerBreak`** = {`alongPerMille` 1300, `backPerMille` 750, `depthMm` 40, `depthPerMille` 600}: how a corner of slate breaks off a nosing, the bite along and back per its size and how deep. Read through `Data.corner_break()`. The default is `slab.py`'s and `stair_stages.py`'s numbers, the gully's broken corners as they were judged.

What stays in code is the rule of any stone (convex, planar, level beds, no rake, square arrises), SN8's and SN9's limits as the design states them, the wear's laws (`wear.py`), and the judging rig (the 28 mm lens at 2560 × 1440). The design's numbers are rules of any part, not style.

## Conflicts for others to settle

- **`kinds/stair.json` against R1's walling table.** The stair kind's geometry stage says `lapMm` 100 and `jointMm` [4, 12]. The walling table's `dry-split-1874` steps say [40, 60] and [4, 10]; so does SN3 for the lap, and SN5 says 4 to 10 mm between tread stones. The table is what R1 laid, so it wins in `Data.tread_lap()` and `Data.tread_joint()`, and the kind is the fallback. One of the two files should change. I wrote neither.
- **The Unity pivot check** (above). `LT1R2a.cs` is the Unity agent's file; I did not change it.
- **L1's error is 11 mm**, not the design's "about 6 mm". L1 is L0 without its chamfers, so its distance from L0 is the chamfer's sagitta on an arris (8.5 mm at a 12 mm leg) and 10.4 mm where three chamfers meet (half the leg times √3). The definition says 11 and explains it. R2a's A/B at 8, 10 and 12 m is where the number gets judged.

## Faults, honestly

- The steps alone are at 13.7% thin at L0 (above). This is the largest open question for R2b and R3, and the wall stones will make it harder.
- Four L0 triangles in the pool have altitudes of 0.26 to 0.33 mm, at an open (unfilled) chip's chamfers (`fl-1/tr-15/sl-0`, `fl-0/tr-28/sl-1`, `fl-0/tr-12/sl-0`, `fl-1/tr-15/sl-1`). They pass the weld check (0.1 mm) and are not degenerate, but they are slivers. `collapse` refuses to merge them because it would bend a face by more than 0.05 mm, or move a column vertex it keeps. Five stones have an L0 altitude under 1 mm; 73 have one under 2 mm.
- The tread's wear is held mostly by one row 50 mm behind the nosing (rows at 0, 50 and 327 mm on the specimen): the law's nosing falls off linearly to nothing 50 mm back, and the hollow behind it stays within 1 mm of flat. That is true to `wear.py` as written. Whether the hollow reads at 1 m is for Unity's frames.
- Every step stone in the pool is walled at one end and jointed at the other. No laid stone has an open end, so the open-end facets and seeded chips are exercised only by the variants.
- `stones.py` is one file of about 2,600 lines. Its wall stone and coping will reuse the machinery, but its checks, face frames and channels are still written for the step; they are generalised with the wall stone.
