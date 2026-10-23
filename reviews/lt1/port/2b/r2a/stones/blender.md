# R2a's stones in Blender: the step, the wall stone, the coping

Port step 2b, rung R2a, the Blender half (`plan.md` in this folder is the contract). Written 23 October by the Blender agent (Opus). It covers the shared machinery and the three parts, each built, checked, exported and installed. No reviewer has passed anything here.

## In short

- **Built.** `blender/parts/stone/slate/block.py` is the machinery: rigid convex blocks cut by planes, facets, chips, chamfers at L0, a wear field subtracted, hidden faces not drawn, seen regions, skirts and covers, and a triangulation sized for the screen. `blender/parts/stone/slate/stones.py` holds three part functions whose inputs are facts (`step`, `wallstone`, `coping`), with their checks, pools, export, quick sheets and CLI. The definitions are `packs/stavanger-1989/parts/stone/step.json`, `wallstone.json` and `coping.json` (draft; each passes `tools/validate_record.py`'s part check, `Contracts.part`).
- **Three specimens, each chosen by a stated rule.**

  | Part | Specimen | L0 (budget) | L1 (budget) | Thin at L0, 8 m | Thin at L1, 20 m | L1 from L0 |
  | --- | --- | --- | --- | --- | --- | --- |
  | step | `st-gully/fl-0/tr-9/sl-1` | 144 (300) | 69 (120) | 10 of 137 (7.3%) | 3 of 60 (5.0%) | 8.51 mm (11) |
  | wall stone | `wl-gully/fl-1/r/pn-4/bank/co-21/sp-1` | 18 (40) | 10 (16) | 0 of 10 | 0 of 4 | 9.21 mm (11) |
  | coping | `wl-gully/fl-0/r/pn-4/cp-3` | 36 (120) | 26 (48) | 2 of 11 (18.2%) | 0 of 5 | 8.98 mm (11) |

- **Every stone of the three pools passes every check of its own:** the 134 step stones, the 1,220 ordinary wall face stones and the 136 copings of the panels as built, as R1 laid them (round 2) at the pinned commit.
- **The level gate passes, and the export holds on it.** SN8's thin share is the level's ("the level's front-facing triangles, the fills included"), and building-blocks' 60% rule is each kind's. The export now holds both over the three pools: L0 at 8 m has 2,028 of 27,794 front-facing triangles under 2 px (7.3%: steps 13.7%, wall stones 0.0%, copings 23.4%). L1 at 20 m has 243 of 11,016 (2.2%). The medians are 63 to 207 px². The stair kind's L1 is 0.454 of its L0, the walls kind's 0.580 (limit 0.6).
- **A change of policy, named.** Before this, the step's specimen was also held alone to the 10% share. Now no single piece is held to the share or to the 60% ratio. Both are reported per piece, and the level and the kind are held. One triangle moves a coping's share by about nine points, and the coping's L1 is 0.72 of its L0 by nature (it loses only its chamfers).
- **The chamfer rules, each from evidence.**
  - SN7 keeps the bed's arrises square on both new parts: a chamfer there faces down, the dark line beneath an edge.
  - The coping chamfers only its top's perimeter. With every arris chamfered it was 19 of 31 thin (61%), from three chamfers meeting in points whose tips are under 2 px at any triangulation. As built it is 2 of 11.
  - The wall stone's leg is SN4's top, 12 mm. At 10 mm its end chamfers, seen about 50° off in the judging view, are 1.9 px. Every sixth pool stone gave 19.9%, 1.2% and 0% thin at legs of 10, 11 and 12 mm, and the whole pool was 7.5% at [10, 12].
- **Exported and installed** under `install_lock` into `unity/Assets/Experiments/LT1/R2a/Generated/` (git-ignored), with hashes in `blender/parts/stone/slate/stones.manifest.json`:
  - `step.fbx` is unchanged at `04615df7f74b3455`; only its sidecar was rewritten.
  - `wallstone.fbx` is `c980b31eeaae3fd7`.
  - `coping.fbx` is `ebcb6e640f9ba4ff`.

  Every triangle sits on three control points of its own. Each file was read back exact, and each export proved that the FBX route's check refuses shared control points.
- **Vertices beside triangles** (the part's own, an exact indexed mesh's, the FBX's):

  | Part | L0 | L1 |
  | --- | --- | --- |
  | wall stone | 12, 54, 54 | 8, 29, 30 |
  | coping | 23, 108, 108 | 18, 75, 78 |

  Across the pools: wall stones L0 15,872, 73,272, 73,272 and L1 10,376, 39,608, 40,296; copings L0 3,052, 13,487, 13,524 and L1 2,476, 9,563, 10,068. The step's finding holds for every part: under the contract's per-triangle edge distances, an exact indexed mesh shares almost nothing more than the FBX does.
- **For the Unity side.**
  - `LT1R2a.cs`'s `Pivot()` will fail both new parts with "the top does not face up". It sums kind-0 triangles, and their tops are bed faces (kind 3).
  - A wall stone judged alone shows its open band: it is drawn only 77 mm behind the wall's plane. Its context (below) hides it.
- **Contexts.** Each specimen has a context in its own frame (`context.py`): its neighbours built by their parts, SN5's fills, and proxies where no part exists yet. With the context in place, a ray at every pixel of the five judging views sees none of the specimen's open bands at either level. Details and faults are in "The contexts".
- **Data and code.** Every fact is read from data through one function that records its source. The proposed fields have documented defaults:
  - five for `walling.json` (`jointMm`, `batterPerHeight`, `topThickMm`, `copeOverMm`, `copeProudMm`);
  - `slate.json`'s `cornerBreak`;
  - a `params` object for the part definitions, since `part.schema.json` is closed.

  I wrote none of `walling.json`, `kinds/wall.json`, `slate.json` or the schema.
- **Checks.** `tools/check.py` does not exist yet; it is built after the 26 October reset. I ran this note's own tests (`stones.py check`, `flight` for each part, the level gate, the export's readback and probe) and `tools/validate_record.py`, which passes. It checks a part only where a record uses one, so I also ran its own part check (`Contracts.part`) on the three definitions: no problems.

## The step

### The specimen, by rule

`specimen_step` takes the first flight. Of its ordinary steps (not the first, whose block runs under the lane; not a rest; not the last, which nothing laps), it takes the one whose rise lies nearest the set-out rise, with the lowest index on a tie. That gives `tr-9`, rise 166 against the set-out's 167. The stone is the one of R1's laying (`masonry.lay` at the pinned commit) that carries the walking line, the flight's centre. Its wear is all on it. Its history comes from the stair's life stage: placed 1874, reset in cement in 1952, and a corner broken in 1897 (56 mm, left), filled with cement in 1986. Its left end is a joint (8 mm) and its right end goes into the wall. The rule and every candidate's rise are printed into the sidecar (`rule`).

### How a stone is made (block.py)

- **The block.** A stone is the intersection of half-spaces `n · p ≤ d` in its own frame (x along from its left end as the street sees it, y back from the riser, z up from the bed). Faces have roles: exposed (drawn), hidden (bed, back, walled ends: not drawn), and cover (a neighbour over the faces: here the next step, lapped on).
- **Skirts.** A drawn face that ends at a hidden face or a cover runs 30 mm past it, so a neighbour's joint, fill or wear never opens a gap. The checks measure what each skirt must reach. The top must run under the next step past its riser's foot (a facet's set-back of up to 25 mm, plus SN9's 3 mm contact: 28 mm). The riser must reach below its bed past the worn top of the step below (2.2 mm worn plus 3 mm: 5.2 mm).
- **Facets (SN4).** Each stone draws its laminae by seed from the top down, whole mm, at least 50 mm apart. A split face breaks back only at a lamina: a convex fold, stepped 15 to 25 mm, so the block stays convex. Two faces that meet at an arris never break at the same lamina, so every corner is three-faced and the chamfer between them is never cut into slivers. Risers have one facet (weight 3) or two (weight 1); open ends have one to three.
- **Chips (SN4).** A chip is a planar cut at a corner of the mass. One goes only where a fact puts it (the life stage's broken corner), or at an open end's top front corner by seed (250 per mille). A broken corner of slate breaks down to a bedding plane, so the stone's nearest lamina sets its depth. Where the record's size would make a chip face under SN9's 50 mm, the bite grows by the least whole per mille that clears it (`chip_least`). The fact is drawn a little larger, never smaller or missing, and the sidecar gives `sizeMm` and `grownPerMille`. The specimen's 56 mm corner needed no growth; in the pool, two corners grew by 37 and 99 per mille. A chip the record says was filled is cut after the chamfers: under its fill its edges are joints, not arrises.
- **Chamfers (SN4), at L0 only.** `block.chamfers` chamfers the arrises it is given (every exposed one by default, a part's list where it names them), each at 45°, its leg (along each face, as a mason gives it) 10 to 12 mm by seed per stone. An arris is any turn of 20° or more between two faces; a face's own facets never make one. L1 is the same planes without the chamfers. Its lit line is kept in the shading by the edge distances (UV6 and UV7).
- **The wear (SN4).** `wear.py`'s laws (footfall times years over the stone's hardness, where feet land) are subtracted as a height field. Rows fall within each level's error (L0 1 mm; L1 half its 11 mm), never narrower than 2 px at the level's far edge. Columns sit at most 120 mm apart across the walking line. The field is flat wherever the wear is under a tenth of L0's error, so unworn stone merges into few faces. The block is cut by the field's triangles column by column, and nothing else moves a vertex. Where the nosing's run-out falls within 2 px of a column node or a chip's crossing, it snaps to it. Columns are inset by the chamfer at a chamfered end, so no column lands a fraction of a mm from the chamfer's foot.
- **Seen regions.** A face that runs into a neighbour is drawn only where it is seen (SN5: a fill no deeper than the joint is wide). For the step that is a joint end: a band behind the riser, facet by facet, below the top, and behind a chip that breaks the end's corner. The band is the widest joint, plus the wear on the end's top, plus SN9's contact, and never less than the chamfer plus 2 px. A chamfer on such an end's arris is clipped to the same band.
- **The surface.** It is merged face by face and made conforming (no T-junctions). Edges under 2 px collapse where the faces about them lie flat within half SN9's planarity (0.05 mm). Corners that only lie straight along an edge are thinned out. Each face is triangulated exactly, for the fewest triangles whose altitude is at least the 2 px size; of those cuts, it takes the least thin (`tri_cost` = under-size count + 0.01 (size / altitude)²).

### What the checks hold (every stone, both levels)

| Check | Rule | Specimen |
| --- | --- | --- |
| budgets | SN8: 300 / 120 per piece (held); L1 / L0 reported, the kind's held (below) | 144 / 69 (0.479); vertices 89 / 45 of its own, 428 / 204 indexed exactly, 432 / 207 in the FBX |
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
| thin triangles | SN8 in the judging view (face-on, 20° of top): reported per piece, held over the level (below) | 7.3% L0, 5.0% L1 |

Other views are measured and reported, not gated. From eye height (1.6 m), a tread at 20 m is seen at 4°, where any cut of it is under 2 px; there 63% of L1's front-facing triangles are thin. Four variants exercise inputs the specimen lacks: an open end with facets and a seeded chip, both ends walled, a 700 mm stone off the walking line, and the specimen without its corner. All pass every check.

### The pool: every step stone the gully lays

`stones.py flight step` builds all 134 stones of the ordinary steps of both flights, as R1 laid them, at the pinned commit (6 processes, about 3 minutes). It writes `flight-check.json`. The export refuses to run unless every pool is current (the same code and data ids) and every stone passes.

| | L0 at 8 m | L1 at 20 m |
| --- | --- | --- |
| triangles per stone | 61 to 152, median 103 (12,947 in all) | 23 to 69, median 44 (5,882 in all) |
| vertices per stone, its own mesh | 40 to 93, median 65.5 (8,298 in all) | 18 to 45, median 31 (4,103 in all) |
| vertices for an exact indexed mesh (identical in every channel) | 38,534 in all | 17,474 in all |
| vertices in the FBX, three a triangle | 38,841 in all | 17,646 in all |
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

Chamfers make 10.8 of the 13.7 points. That is SN4 against SN8 in its plainest form: a 10 to 12 mm chamfer is thin by nature at 8 m, as the design's table of the pre-mortem says ("the gate is by pixels, not aspect, since a chamfer is thin by nature"). The coping's corner rule (below) would take most of the 5.7 points of corner caps out of the steps too. I did not apply it to the step: the step is exported, read back and judged in Unity (`95dc472`). It is a follow-up (Faults).

## The wall stone

### The specimen, by rule

The pool (`face_pool`) is every face stone of a panel as built whose cell has a face or through stone against all four of its sides on its face. These are the walls' ordinary stones; one at a panel's edge, a head, a step's end, the ground or a coping is R2b's. There are 1,220 of them. `specimen_wallstone` takes the one whose cell lies nearest the pool's median length and height, each difference over its interquartile range (exact fractions), with the lowest id on a tie. The medians are 405 and 166 mm, the interquartile ranges 217 and 16 mm. `wl-gully/fl-1/r/pn-4/bank/co-21/sp-1` has exactly that cell, 405 by 166, on the bank face of the right wall of the second flight. Faces or throughs lie on every side (one each end, two above, two below). It was laid in 1874 in `dry-split-1874`.

### How it is made

- **The block.** A rigid convex block on its natural bed. Its top and bed are the laminae's planes (bed faces, UV2 kind 3, level by SN2). Its face is split across them at the wall's batter (1/6, `batterPerHeight`), in one plane or two (`faceFacets` [[1, 3], [2, 1]]). Two planes form a convex bulge whose two edges lie on the wall's plane, so the joints above and below are the wall's and a fill pressed in no deeper than the joint meets it (SN5). The ridge is set back 15 to 25 mm at one of the stone's laminae. Its ends are split, square to the wall. Its back is half the wall's top (210 mm), hidden.
- **Set in.** Each side is set in from R1's cell by a seeded half joint, 2 to 6 mm (half of SN5's 4 to 12). Where those draws would make the stone longer than SN10's 4.5 times its height, they are drawn at the least above and below and the most at the ends. That binds on two pool stones: cells 664 by 156 and 670 by 154 drew 659 by 146 and 662 by 146 (4.51 each) and are now 652 by 152 (4.29) and 658 by 150 (4.39). The sidecar's `setInRule` says when it applied.
- **Only what is seen is drawn.** The face, and of the top, the bed and the ends only a band behind the wall's plane, measured level. The band is as deep as a joint is seen: the widest joint (12 mm) plus SN9's contact (3 mm), and never less than 2 px at a level's far edge seen at the judging view's 20° past the chamfer, with a 10% margin (`bandMarginPerMille`). L1's 20 m sets it: ceil(23.8 mm × 1.1 / sin 20°) = 77 mm. Behind the band the stone is in the wall and never seen, so its back changes nothing drawn.
- **Chamfers at L0.** The face's arrises with the top and with each end: three chamfers, 12 mm legs. Each end's chamfer starts at the point where the top's chamfer meets the top and the end, so each top corner is one point (two chamfers in a mitre; without it a cap of c (√(1 + b²) − 1), 0.15 mm, would sit between them). The end chamfers' legs come out 0.16 mm short of 12 for it (`legDriftMm`). The arrises that run back into the wall lie in its joints and stay square. The bed's arris stays square (SN7); `bedChamfer` is the arm.
- **Patches.** Split faces take `split-0` to `split-3` and bed faces `bed-0` and `bed-1` by seed, as the step's (`patches` in `PARAMS`).

### What the checks hold

| Check | Rule | Specimen |
| --- | --- | --- |
| budgets | SN8: 40 / 16 per piece (held); L1 / L0 reported, the walls kind's held | 18 / 10 (0.556); vertices 12 / 8 of its own, 54 / 29 indexed, 54 / 30 in the FBX |
| planarity, convexity, welds, T-junctions, hidden faces, contract, determinism | as the step's | pass; 4 open edges a level, all on the band's back edge |
| form | the face's edges on the wall's plane; ridges proud only as the bulge puts them | 0.0 mm off the plane; one facet |
| slivers | SN9: no block face under 50 mm or 25° | the ends 157 mm at 80.5° (the batter) |
| L1 against L0 | two-sided, every 2 mm | 9.21 / 5.92 mm of 11 (the top corners, where two chamfers meet) |
| chamfer width | as the step's | 3.56 px square on, 2.52 px for its leg face-on |
| facts | the course within `courseMm` [120, 260]; the cell within `shortMm` 120 and the lesser of `stoneMm`'s 850 and SN10's 4.5 × its height; the half joints within [2, 6]; the stone drawn within SN10 | 166 in range; 405 within [120, 747]; 5, 2, 6, 3; 398 by 157 (2.54) |
| thin triangles | SN8 in the judging view: reported per piece, held over the level | L0 0 of 10 (median 134.9 px²); L1 0 of 4 (128.0 px²) |

The variants are R1's own stones at the pool's extremes (least length 180 by 178; greatest length and greatest height, one stone, 798 by 188; least height 195 by 140), the specimen broken once (two facets), and the specimen with its bed chamfered (the arm). All pass every check. The two-facet stones take 26 and 14 triangles. The arm takes the bed's chamfer to 2 of 12 thin (16.7%, the bed chamfer seen from above) and L1 to 10.29 mm from L0.

### The pool

`stones.py flight wallstone` builds all 1,220 (about 2 minutes) into `walls-check.json`.

| | L0 at 8 m | L1 at 20 m |
| --- | --- | --- |
| triangles per stone | 18 to 26, median 18 (24,424 in all) | 10 to 14, median 10 (13,432 in all) |
| vertices: its own; indexed; the FBX's | 15,872; 73,272; 73,272 | 10,376; 39,608; 40,296 |
| under 2 px, pooled | 0 of 14,048 | 0 of 5,496 |
| median visible triangle | 106.0 px² | 79.7 px² |
| smallest altitude | 10.6 mm | 36.4 mm |

912 stones have one facet and 308 two. They are drawn 168 to 787 mm long and 131 to 183 mm high; 768 are on bank faces and 452 on stair faces. 139 of the 1,220 cells lie outside the working's `drawnPerHeight` (1.5 to 4 times as long as high). That is R1's laying, reported in each row (`withinDrawn`), not a fault of the part.

### Two decisions, with their evidence

- **The bed's arris square (SN7 over SN4).** SN4 chamfers every exposed arris; SN7 draws edges "by light on the lit arris, never by a dark line beneath it". The bed's chamfer faces down, so it is that dark line. It is also thin from above: 2 of 12 L0 triangles on the specimen (16.7%). The arm (`bedChamfer: true`) is kept for R2a's A/B in Unity.
- **The leg at 12 mm (SN4's top).** SN4 asks for 10 to 12 mm "at least 2 px at 8 m". The end chamfers of a face are seen about 50° off their normal in the judging view, where a 10 mm leg is 1.9 px. With the step's [10, 12] by seed, the pool was 7.5% thin at L0 (1,054 of 14,048; 201 stones over 10%), all of it the end chamfers. On every sixth pool stone (204), legs of 10, 11 and 12 mm gave 19.9%, 1.2% (only a two-facet face's lower piece) and 0%. The wall stone takes 12 for every stone; the step and the coping keep [10, 12].

## The coping

### The specimen, by rule

The pool is every coping of a panel as built: 136 of R1's 144 (the other eight lie on the 1961 panel's rebuild). `specimen_coping` uses the wall stone's rule on length and thickness. The medians are 592.5 and 86 mm, the interquartile ranges 98.5 and 18 mm. `wl-gully/fl-0/r/pn-4/cp-3` has a cell of 590 by 87 on the first flight's right wall. Its left end is a joint, and its right end is open, its run's end over a riser. It was laid in 1874.

### How it is made

- **The block.** A slab of split slate on its bed across the wall's top: six planes, its top and bed the laminae's (kind 3), its long sides and ends split (kind 2), one plane each. A face of 64 to 98 mm has no room for a second facet of 50 (SN9). Its width is the wall's top and its overhangs, 420 + 50 = 470 mm (`topThickMm`, `copeOverMm`). Its front stands a seeded 15 to 35 mm proud of the stair's face (`copeProudMm`; 32 on the specimen), and its back the rest of the overhang (18), the bank's face of a standing wall. Its thickness is its run's less its bed's half joint (85), and its length is its cell's less a half joint at each joint end (586).
- **Ends.** An open end is square and drawn whole, and its top corners are knocked by seed (250 per mille each, legs 50 to 80 mm, down at most half the slab; SN4's chips at a coping's ends). The specimen has one, `chip:r-back`, a 62 mm face at 45.6°. A joint end is drawn where the joint is seen: within the band below the top (21 mm: the chamfer plus 2 px at 8 m) and behind each face, the wall's plane leaning back at the batter above the bed. The bed is drawn under each overhang and 15 mm past the face under it.
- **Chamfers at L0: the top's perimeter, and only that.** front|top, back|top where the back is seen, and end|top at each end, 10 to 12 mm by seed (11 on the specimen). Square:
  - the bed's arrises (SN7, as the wall stone's);
  - each end's upright arrises (below);
  - a knock's arrises: a break after the dressing is sharp, and it cuts through the top's chamfers;
  - a joint end's arris with the bed, which lies inside the joint.

  `bedChamfer`, `uprightChamfer` and `chipChamfer` are the arms.

### What the checks hold

| Check | Rule | Specimen |
| --- | --- | --- |
| budgets | SN8: 120 / 48 per piece (held); L1 / L0 reported, the walls kind's held | 36 / 26 (0.722); vertices 23 / 18 of its own, 108 / 75 indexed, 108 / 78 in the FBX |
| planarity, convexity, welds, T-junctions, hidden faces, contract, determinism | as the step's | pass; 8 open edges a level, where the bed's seen bands stop (`bed seen`, `bed fill`) and on the joint end's (`end-l seen`) |
| slivers | SN9 | faces 85 mm at 90°; the knock 62 mm at 45.6° |
| L1 against L0 | two-sided, every 2 mm | 8.98 / 5.5 mm of 11 |
| chamfer width | as the step's | 3.27 px square on, 2.31 px for its leg face-on |
| facts | the run's thickness within `copeThickMm` [70, 100]; the length within `copeLeastMm` 200 and `copeLengthMm`'s 1000; the half joints within [2, 6] | 87; 590; 4 and 2 |
| thin triangles | SN8 in the judging view (face-on to its stair side, 20° of top): reported, held over the level | L0 2 of 11 (18.2%: the end|top chamfers, 76° off their normal); L1 0 of 5 |

The variants are R1's copings at the pool's extremes (least length 450 by 90, greatest length 994 by 87, least thickness 609 by 70, greatest thickness 583 by 100), the specimen with both ends open and every corner knocked, the specimen with both ends joints, and the specimen with every arris chamfered (the arm). All pass every check. Both open is the largest at 50 and 34 triangles.

### The pool

`stones.py flight coping` builds all 136 into `copings-check.json`.

| | L0 at 8 m | L1 at 20 m |
| --- | --- | --- |
| triangles per stone | 30 to 42, median 34 (4,508 in all) | 22 to 30, median 26 (3,356 in all) |
| vertices: its own; indexed; the FBX's | 3,052; 13,487; 13,524 | 2,476; 9,563; 10,068 |
| under 2 px, pooled | 23.4% (339 of 1,448) | 0.5% (3 of 604) |
| per stone | 0% to 40%, median 30%, 104 over 10% | 0% to 12.5%, median 0%, 3 over 10% |
| median visible triangle | 176.8 px² | 206.8 px² |
| smallest altitude | 8.4 mm | 15.1 mm |

59 copings have two joint ends and 77 one open end. 32 corners are knocked. They are drawn 438 to 987 mm long and 65 to 98 mm thick.

### The corners, with their evidence

With every arris chamfered (SN4 read literally; the arm), the specimen's L0 is 78 triangles, 19 of 31 under 2 px in the judging view (61.3%, median 13.8 px²), and L0 lies 11.0 mm from L1, at the limit (L1 to L0 9.53 mm). The causes:
- Three chamfers meet in a point at every corner of an end: the top's, the front's or back's, and the end's upright one. Its three tips are about c/2 tall, under 2 px at 8 m whatever the triangulation.
- The bed's chamfers face down (SN7).
- The knocks' chamfers are slivers on a 50 to 80 mm break.

Squaring the upright arrises leaves only two chamfers at each top corner, meeting in a mitre that has no tip: with vertical faces and equal legs the mitre meets exactly. As built, the specimen is 36 triangles, 2 of 11 thin. What is left is the end|top chamfers, seen 76° off their normal from the stair. No chamfer of 10 to 12 mm is 2 px there, so that is the price of SN4's chamfer on the top's perimeter. It is 23.4% of the copings' L0 and 1.2 points of the level. The arm that would remove it, end|top square on a joint end, is one line in `outline_coping`'s classification. It was not taken: the level passes with them, and from up or down the stair they are the lit line of the run's steps.

## The level gate, and why

SN8 counts thin triangles over "the level's front-facing triangles, the fills included", at each level's far edge, and asks a median visible triangle of 10 px or more. Building-blocks says "each kind's export check: each level at most 60 % of the one before". Neither is a rule of one piece.
- **Reported per piece:** each specimen's and each pool stone's thin share in every view (the sidecar's `checks.thin`, with `view` "the level's view (pooled)" or "reported"), and its L1 / L0 (`checks.triangles.ratioWithin`).
- **Held by the export** (`level_gate`, the sidecar's `checks.level`): the three pools pooled, at most 10% under 2 px at L0 (8 m) and L1 (20 m), each pool's median visible triangle at least 10 px², and each kind's L1 at most 0.6 of its L0. The stair kind is the steps; the walls kind is the wall stones and copings. Every stone's own checks are held too, and every pool must be current.
- **Why the policy changed.** The step's specimen was held to the share alone before. A coping's L0 has about eleven front-facing triangles, so one triangle moves its share by about nine points, and its L1 is 0.72 of its L0 because L1 loses only its chamfers. Per piece, both numbers judge noise, not cost.

| | L0 at 8 m | L1 at 20 m |
| --- | --- | --- |
| steps (134) | 1,689 of 12,298 (13.7%) | 240 of 4,916 (4.9%) |
| wall stones (1,220) | 0 of 14,048 | 0 of 5,496 |
| copings (136) | 339 of 1,448 (23.4%) | 3 of 604 (0.5%) |
| **pooled** | **2,028 of 27,794 (7.3%)** | **243 of 11,016 (2.2%)** |
| median visible triangle | 63.1, 106.0, 176.8 px² | 55.9, 79.7, 206.8 px² |

| Kind | L0 | L1 | L1 / L0 |
| --- | --- | --- | --- |
| stair (steps) | 12,947 | 5,882 | 0.454 |
| walls (wall stones, copings) | 28,932 | 16,788 | 0.580 |

What the pools leave out: the fills (eight large triangles a panel, never thin, so they would only lower the share), and every wall stone R2b lays (heads, throughs, topstones, stones at a panel's edge, the ground, a step's end or under a coping), the rests and the first and last steps. The real level's share and ratio are R2b's laying and R3's measure. The walls' 0.580 is close to the limit, and R2b's pieces will move it.

## The export

- **Route.** FBX plus a sidecar per part, L0 and L1 as two objects (`<part>_L0`, `<part>_L1`), through `stone.py`'s `_export_fbx` and `install_lock` (imported, never edited). The export is flat-shaded, forward +Z and up +Y with the space transform baked, so Unity's mesh holds x along, y up, z back with no turn on its object. Each triangle is written on three control points of its own (below). `stones.py export` runs only when every part's check passes, every pool is current and passes, and the level gate passes.
- **Readback.** Before the install, the export is written to a scratch file and read back with Blender's own FBX parser, as `mesh_hash` does, never re-imported. It checks:
  - the triangles in order;
  - three control points a triangle, each corner on its own (the FBX route's check, below);
  - the positions, exact against the map;
  - the normals flat: a triangle's three corners carry one normal, which is the normal of the triangle's own corners in the file (to 1e-5, float32's arithmetic) and lies on the face's plane within what rounding the positions to float32 allows a triangle of its altitude;
  - all eight UV layers bit for bit by name.

  The same meshes exported twice must hash the same, and the installed file must hash as the one read back.
- **Installed, 23 October** (`logs/fbx-route-shared-refused.txt`):

  | File | Mesh hash | L0 mesh | L1 mesh | Triangles | Corners (= control points) |
  | --- | --- | --- | --- | --- | --- |
  | `step.fbx` (unchanged, left as it was) | `04615df7f74b3455` | `399d5b8aa879fd3c` | `bd0de39fd98d6a7b` | 144 / 69 | 432 / 207 |
  | `wallstone.fbx` | `c980b31eeaae3fd7` | `7c88626f8e5703f2` | `ea39a0df8b3fa0d4` | 18 / 10 | 54 / 30 |
  | `coping.fbx` | `ebcb6e640f9ba4ff` | `0c2d88ea6846d6f5` | `ad51a7b958987e15` | 36 / 26 | 108 / 78 |

- **Sidecar** (`Generated/<part>.json`). It holds:
  - objects, pivot and frame;
  - bounds per level;
  - triangles and vertices per level (`vertices` the part's own, `indexedVertices` an exact indexed mesh's, `fbxVertices` the FBX's);
  - the chamfer and its form (`chamferMeasure` "leg", 45°);
  - the channels by name;
  - the facts and the specimen's rule;
  - the outline's numbers (the step's facets, chips, laminae, wear rows and columns; the walls' set-in, facets, bands, proud, chips and square arrises with why; each face's kind, patch slice, mode and offset);
  - every check's result, the pool's summary and the level gate's;
  - the readback's notes and the mesh hash;
  - every input with its source (`data`) and content id (`code`).
- **Bounds.** In Unity's frame (x along, y up, z back, mm):
  - The step runs from (0, −30, 0) to (2295, 166, 327). The −30 is the riser's skirt below the bed, and the 327 is the top drawn under the next step to its skirt.
  - The wall stone runs from (0, 0, 0) to (398, 157, 103.2): the band's 77 mm plus the batter's 26.2 at the top.
  - The coping runs from (0, 0, 0) to (586, 85, 470).

### The FBX route's control points

- **The fault.** Unity's FBX import merges the corners that share one FBX control point when their UVs lie within about 1e-3 and their normals within about 1.3°. No weld or optimise setting stops it. The first step.fbx (`df9d7a1ae9f8d7ab`) shared control points where the part's corners are one, and came in with 411 vertices for L0's 432 corners and 193 for L1's 207. On L0, three triangles took a neighbour's edge distances (off by up to 0.665 mm) and one normal was 0.54° off. On L1, two normals were up to 1.29° off and six triangles had a slot that was neither their own edge's distance nor an arris's. The Unity builder found and proved it: `logs/readback-step.txt` for the file as installed, `logs/readback-step-test.txt` for a trial with every triangle on its own control points, which read back exact.
- **The fix, on the FBX route only.** `make_object` (the FBX export step) writes each triangle on three control points of its own, in order. Nothing else changes: the triangles, their order, the positions, the normals and all eight UV layers are bit for bit what the part made. The part functions keep their shared positions, so that the FBX's limits do not spread into the parts or into step 5's chunks (`schemas/chunk-format.md`), which carry vertices exactly.
- **The check is the FBX route's.** The readback fails the export if the file has any count of control points other than three a triangle, or if any two corners share one, naming how many corners sit on how many shared points. Every export proves it bites: it writes the specimen's L0 a second time on the part's own vertices to a scratch file and fails unless the check refuses it. The refusals were "89 control points for 432 corners, 430 corners on 87 shared ones" for the step, 12 for 54 (all shared) for the wall stone and 23 for 108 (106 on 21 shared) for the coping. They are in the sidecar's `readback.sharedProbe` and `logs/fbx-route-shared-refused.txt`.
- **What it costs.** The sidecar, the manifest's `levels` notes and the sheets count all three: the part's own vertices, an exact indexed mesh's and the FBX's. `mesh_hash`'s `vertices` are the file's control points, so they now equal its corners.
- **What sharing the contract allows.** Counted on the step's specimen with `indexed_vertices` (every channel as float32, bit for bit) and a scratch count by channel group:
  - positions alone: 89 and 45;
  - positions and flat normals: 300 and 143;
  - all but the edge distances: also 300 and 143;
  - every channel: 428 and 204.

  Only the edge distances keep corners apart beyond the hard edges, and they keep almost all of them apart: an exact indexed chunk needs 99.2% and 99.0% of the FBX's vertices across the steps (L0, L1), 100% and 98.3% across the wall stones, and 99.7% and 95.0% across the copings. Fewer vertices would need edge distances shared within a face, a change to the contract that is the Unity side's to weigh. The rule stands as given: the unsharing lives in the FBX step only.

## The contexts

`blender/parts/stone/slate/context.py` (23 October) builds, for each specimen, what R1's laying or the stair's plan puts within about 0.6 m of it, in the specimen's frame. Unity places it at the specimen's transform.

- **What each holds.**
  - The step: the five other stones of tr-8, tr-9 and tr-10 (step part), three tread-joint fills, and six proxies of the right cheek wall's stair-face cells. It has 19 objects and 735 triangles.
  - The wall stone: the six cells touching it on the bank face (wall stone part) and one bank fill. It has 13 objects and 232 triangles.
  - The coping: cp-2 and cp-4 (coping part); co-31/sp-1 on both faces (wall stone part); proxies for co-31/sp-0 and co-32/sp-0 on both faces, whose lo side is open to the air; and a fill on each face. It has 14 objects and 256 triangles.
- **How pieces are made.** Every built piece passes its part's own checks. Fills use kind 6 and code 7. Proxies use kind 2 and code 7, are their cell exactly and are 210 mm deep, and the sidecar names each one's reason.
- **Files.** `<part>_context.fbx` and `.json`, installed under `install_lock`:
  - `step_context.fbx` `9a0e1e98a4a1067c`;
  - `wallstone_context.fbx` `3d43f6a804d263d0`;
  - `coping_context.fbx` `79212bc945de9c5a`.

  The hashes are in the manifest. Every object was read back exact, and the probe was refused. The specimens' own hashes are unchanged.
- **The ray test.** It runs in Blender's CPU BVH, one ray per pixel at 2560 × 1440 through the 28 mm lens. The views are face-on 20° at 1, 5 and 12 m and eye height at 5 and 12 m. A leak is a first hit on a specimen face from behind, or a ray reaching the specimen's solid (its planes 2 mm inside) before its first hit.
  - With the context: 0 leaks in all 30 view-and-level cases.
  - Alone, the wall stone: 20,886, 1,294, 216, 1,164 and 108 leaks at both levels.
  - Alone, the step: at L0, 2,893, 745, 154, 275 and 0, through the top beyond the cover and the joint slot.
  - Alone, the coping: 0, because its open faces (the joint end and the bed) face away from every judging view.
- **Faults, named.**
  - The face planes' datum is not in data (the geometry stage is planned). Each context runs one plane per face through the specimen, constant along s:
    - The step's cheek-wall face is battered through the specimen's tread, so it stands 22 to 48 mm inside the walking width at tr-8.
    - cp-2 and cp-4 are placed by their stair side, so their backs miss the bank plane by -110 and +112 mm. This is seen only from the bank.
  - **The L1 test has a 7.5 mm margin on the worn top.** The test holds L1 7.5 mm inside the wear field, its 5.5 mm share plus 2 mm. So the L1 test cannot see a top band shallower than that, and the alone step shows 0 at L1. L0's 3 mm margin bites, and the context's pieces are the same at either level.
  - **The readback's own-normal bound is scaled.** At a context's distances it uses 4R·2⁻²⁴/altitude over the fixed 1e-5, like the plane bound. A chamfer-corner triangle of tr-8/sl-0 is 2.4e-5 off at 1.2 m from the pivot. stones.py itself is unchanged.
  - **A wall fill's grid merges lines closer than 10 mm.** A 1 mm column failed the normals check. The fill can grow past the union of its cells by less than that, but never falls short.

## The quick sheets

`blender-sheet.png` (the step), `blender-sheet-wallstone.png` and `blender-sheet-coping.png` (Workbench, lock-aware: they wait while a timing run holds the Unity lock). They check that the machinery works and judge nothing. Each triangle is coloured by its kind: grey the top, orange a chamfer, blue-grey a split face, brown a bed face. Labels give each level's triangles and vertices three ways. Each sheet shows:
- the specimen at both levels in the judging view, magnified, its thin triangles red;
- each level raised 45° and from 40° left;
- the variants.

The step's sheet adds the skirts from behind and below and the wear from above, blue the deepest. The walls' sheets add each level from behind and above, the seen bands lighter, and the right end square on: the batter on the wall stone, the proud front and back and the knock on the coping.

## Data and code

Read from data, each through one function in `stones.py` (class `Data`) that records the value and its source in the sidecar's `data`:

| Value | From |
| --- | --- |
| world seed, show year | `packs/stavanger-1989/pack.json` |
| built year, footfall by period | `fixtures/records/st-gully.json` |
| flights, steps, set-out, width, lean | `fixtures/golden/stair/plan.json` (the plan stage's output) |
| a stone's placed year, its broken corner and fill, the step's reset | `fixtures/golden/stair/life.json` |
| the wear rate | `packs/stavanger-1989/materials/slate.json`: `wearUmPerCentury` |
| the steps' lap [40, 60] and tread joint [4, 10] | `walling.json`: `workings.dry-split-1874.steps` (R1's), with `kinds/stair.json` as the fallback |
| every stone's cell, faces, neighbours, panel and run; the copings' runs and joints | R1's laying, `masonry.lay` run in memory at the pinned commit on R1's facts, `kinds/wall.json`'s plan params and the walling table (never the git-ignored `layout.json`) |
| a panel's working and laid year; a wall's side | R1's facts (`reviews/lt1/port/2b/r1/facts.json` at the pinned commit): `walls.working`, `walls.built`, a line's `rebuilt` and `side` |
| course, stone and short lengths, `drawnPerHeight`, the coping's thickness, length and least length (the facts checks) | `walling.json`: `workings.dry-split-1874` (`courseMm`, `stoneMm`, `shortMm`, `drawnPerHeight`, `copeThickMm`, `copeLengthMm`, `copeLeastMm`) |
| the patch slices | `blender/parts/stone/slate/patches.manifest.json` |
| the levels' errors and budgets, the pivot | each part's definition in `packs/stavanger-1989/parts/stone/` |

Proposed, with a documented default in code until the file takes the field (each read through one function; the sidecar's `data` names it as a default and where the default came from):
- **`walling.json`, per working** (`Data.walling_value`):
  - `jointMm` [4, 12], a wall's joints, from SN5; the table holds only the steps' [4, 10]. Read by `wall_joint()`.
  - `batterPerHeight` [1, 6], the face's lean as whole numbers, from `wall.py`'s BATTER and SN2's "about one in six". Read by `batter()`.
  - `topThickMm` 420, the wall's thickness under the coping, from `wall.py`'s DEPTH. Read by `top_thick()`.
  - `copeOverMm` 50, a standing wall's coping overhangs together, from `wall.py`. Read by `cope_over()`.
  - `copeProudMm` [15, 35], how far the coping's front stands proud of the face below, from `wall.py`. Read by `cope_proud()`.
- **`slate.json`: `cornerBreak`** = {`alongPerMille` 1300, `backPerMille` 750, `depthMm` 40, `depthPerMille` 600}: how a corner of slate breaks off a nosing. It is read through `Data.corner_break()`. The default is `slab.py`'s and `stair_stages.py`'s numbers, the gully's broken corners as they were judged.
- **The part's own numbers → a `params` object in the part definition.** `part.schema.json` is closed (`additionalProperties: false`), so I did not add it. `PARAMS` in `stones.py` holds the defaults, read only through `param()`, which prefers the definition's `params` the day the schema takes them. The proposal: `params`, an object of named numbers, ranges and weighted choices, free per part and documented by the part's function.

  | Part | Params (defaults) |
  | --- | --- |
  | step | `chamferMm` [10, 12], `chamferMeasure` "leg", `arrisMaxDeg` 160, `riserFacets` [[1, 3], [2, 1]], `endFacets` [[1, 2], [2, 1], [3, 1]], `facetStepMm` [15, 25], `facetLeastMm` 50, `chipPerMille` 250, `chipLegMm` [50, 80], `skirtMm` 30, `nosingReachMm` 50, `wearGridMm` 120, `wearFlatShare` 100, `l1WearShare` 500, `patches` |
  | wallstone | `chamferMm` [12, 12], `chamferMeasure` "leg", `arrisMaxDeg` 160, `faceFacets` [[1, 3], [2, 1]], `facetStepMm` [15, 25], `facetLeastMm` 50, `bedChamfer` false, `bandMarginPerMille` 100, `patches` |
  | coping | `chamferMm` [10, 12], `chamferMeasure` "leg", `arrisMaxDeg` 160, `bedChamfer` false, `uprightChamfer` false, `chipChamfer` false, `chipPerMille` 250, `chipLegMm` [50, 80], `patches` |

What stays in code:
- the rules of any stone: convex, planar, level beds, no rake, rigid, only what is seen drawn;
- SN8's, SN9's and SN10's limits as the design states them;
- the wear's laws (`wear.py`);
- the judging rig (the 28 mm lens at 2560 × 1440, the judging view face-on with 20° of top, 8 m and 20 m);
- the level gate's rule and the kinds each part's stones are of (`KINDS`).

The design's numbers are rules of any part, not style. No style look value is set here: the look parameters are the shader's and the patches'.

## Conflicts for others to settle

- **`kinds/stair.json` against R1's walling table.** The stair kind's geometry stage says `lapMm` 100 and `jointMm` [4, 12]. The walling table's `dry-split-1874` steps say [40, 60] and [4, 10]; so does SN3 for the lap, and SN5 says 4 to 10 mm between tread stones. The table is what R1 laid, so it wins in `Data.tread_lap()` and `Data.tread_joint()`, and the kind is the fallback. One of the two files should change. I wrote neither.
- **L1's error is 11 mm in all three definitions.** The design says "about 6 mm", and `kinds/wall.json` and `kinds/stair.json` say 4. L1 is L0 without its chamfers, so its distance from L0 is the chamfer's sagitta on an arris (8.5 mm at a 12 mm leg), 9.2 to 9.8 mm where two meet, and 10.4 where three meet (the step's corners). R2a's A/B at 8, 10 and 12 m is where the number gets judged.
- **L2 to L4's errors.** The three definitions say 25, 100 and 250 mm (step.json's, carried over); both kinds say 10, 25 and 100. The chunks (step 5) make those levels, and one side should change.
- **SN10 binds the stone; R1 checks the cell.** R1 keeps each cell within 4.5 times its height. The stone is the cell less its joints, so a cell at R1's limit cannot be drawn within SN10 by any joint in SN5's range: even at the least above and below and the most at the ends, (4.5 H − 12) / (H − 4) > 4.5. The part's set-in rule fixes the two pool stones that broke it. R1's check should measure the cell less the least joint, or the walling table should say which SN10 means.
- **`copeThickMm` is the course's, not the slab's.** R1's coping cells are 70 to 100 mm thick, the run's, and the slab is that less its bed's half joint (64 to 98 mm by the rule, 65 to 98 as laid). If the table means the slab, R1's runs are 2 to 6 mm too thin. A question for R1.
- **Unity's `Pivot()` and the new parts** (`LT1R2a.cs`, the Unity agent's file; I did not change it).
  - It sums the kind-0 triangles' normals and fails with "orientation: the top does not face up (+y)" when their mean is not up. The wall stone and the coping have no kind-0 triangles: their tops are bed faces (kind 3) by SN4, since a coping's top and a wall stone's top are the laminae's planes, not a walked tread.
  - The coping's split faces, front and back both drawn on a standing wall, have a mean normal near zero, so that log line says nothing for it either.
  - The bounds check reads the sidecar's `bounds` and passes as it stands.
- **Directive 2's premise.** Keeping shared corners in the parts was for step 5's chunks. Under the per-triangle edge distances, almost no corners are identical in every channel (The FBX route's control points).

## Faults, honestly

- **The steps alone are at 13.7% thin at L0.** The level passes at 7.3% because the wall stones dilute them. Of those points, 5.7 are corner caps where three chamfers meet, the same fault the coping's rule removed. Applying the coping's rule to the step (its upright riser|end arrises square, a knock's arrises sharp) would change step.fbx after the Unity side read it back and judged it, so it is a follow-up for the coordinator. The step also keeps chamfered chips.
- **The copings are at 23.4% thin at L0** (median 30% a piece), from the end|top chamfers seen 76° off from the stair. No leg in SN4's range is 2 px there. The level carries it; the arm is one line (The corners).
- **The walls kind is at 0.580 of 0.6.** Only the ordinary face stones and the copings are counted. R2b's heads, throughs and edge stones will move it either way.
- **A wall stone judged alone shows its open band.** It is drawn only 77 mm behind the wall's plane, and the top, ends and bed stop there. From the judging view at 20° above, the top band's back edge is open and the shell's inside faces are back faces. In the wall the stone above covers it. For R2a's frames it needs neighbours, the panel's fill plane, or a dark backing set at the band's depth. The coping has the same at its joint ends and its bed. The step's open faces were checked by the Unity side (`95dc472`, "the open faces leak nothing seen").
- **The wall stone's chamfer no longer varies** (12 mm on every stone). The step's and the coping's vary 10 to 12 by seed. SN4's range allowed it; the variation was ±1 mm, about 0.3 px at 8 m.
- **SN5's light rim against the chamfers.** SN5 forbids "a light rim [that] rings a stone"; SN4 chamfers every seen arris, and the wall stone's end and top chamfers sit at its joints. Whether the lit chamfers at a joint read as a ring is for Unity's grey frames. The arms are the params above.
- **Four L0 triangles in the step pool have altitudes of 0.26 to 0.33 mm**, at an open (unfilled) chip's chamfers (`fl-1/tr-15/sl-0`, `fl-0/tr-28/sl-1`, `fl-0/tr-12/sl-0`, `fl-1/tr-15/sl-1`). They pass the weld check (0.1 mm) and are not degenerate, but they are slivers. `collapse` refuses to merge them because it would bend a face by more than 0.05 mm, or move a column vertex it keeps. The wall stones' and copings' smallest altitudes are 10.6 and 8.4 mm.
- **The tread's wear is held mostly by one row 50 mm behind the nosing** (rows at 0, 50 and 327 mm on the specimen). The law's nosing falls off linearly to nothing 50 mm back, and the hollow behind it stays within 1 mm of flat. That is true to `wear.py` as written. Whether the hollow reads at 1 m is for Unity's frames.
- **No laid step stone has an open end,** so the step's open-end facets and seeded chips are exercised only by the variants.
- **`stones.py` is one file of about 3,600 lines.** The parts share the machinery, the checks and the export, but the step's outline and the walls' outlines are still separate functions with some repeated setup.
