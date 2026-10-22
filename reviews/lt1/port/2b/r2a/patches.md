# R2a, first half: the slate's face patches

**In short.** Six shared face patches for the town's phyllite (SN6, held to SN4, SN5 and SN7), made by rule and checked flat in grey. This is the second version ("patches 2"), reworked after the coordinator's read of the first at 5 m and Øystein's rule against floating lines.
- **The patches:** four split faces (wall fronts and risers) and two bed faces (tread and coping tops), each 1024² texels at 1 mm, seamless, with 16-bit height, normal and value maps.
- **Seeds:** every draw comes from `HS.Stream(1989, "stone/slate/patch/<name>", purpose)`. `check` rebuilds all six and every pixel hash matches.
- **The rules now:** no line that starts or ends inside the face (every split step and the one bed scarp, where there is one, run right across the patch); edges drawn by light (a lit arris over a shadowed break), never a dark groove; the face held near 2 L* in grey light; detail finer than a few mm faint.
- **What the checks found:** at 1 m and 5 m no floating lines, no lines under 2 px wide and over 40 px long, no specks, and every seam clean. The 5 m spread (p5 to p95) is 1.5 to 2.5 L* on the split faces and 0.8 to 1.3 on the bed faces; value bands are 0.014 to 0.026.
- **What remains:** in grey the split faces are calm planes crossed by straight ruled ledges, and the facet lattice repeats visibly in a 2 × 2. split-1 holds only 2.5 L* at 5 m. Nothing here has had a reviewer's eyes, and nothing has been seen in light or material.

| What | Where |
| --- | --- |
| Generator | `blender/parts/stone/slate/patches.py` (`build`, `check`) |
| Manifest (pixel hashes, each patch's drawn parameters) | `blender/parts/stone/slate/patches.manifest.json` |
| Maps (untracked, rebuilt) | `cache/stone/patches/slate-<name>-{height,normal,value}.png` |
| Sheet tool | `blender/tools/patch_sheet.py` |
| Sheet and numbers | this folder: `patch-<name>.png` (with references beside), `patches-distances.png`, `patches-eighth.png`, `patches-tiling.png`, `patches-histograms.png`, `checks.json` |

Run everything with Blender's Python (`/Applications/Blender.app/Contents/Resources/5.2/python/bin/python3.13`; it has numpy). Building all six takes about 7 s, the sheet about 13 s.

## The rules, and why

Phyllite is laminated. It parts along its foliation into leaves a centimetre to a hand thick, each a little different, and breaks across them. So the two workings show two different faces.

Three rules hold for both, and they shaped everything below:
- **No floating line** (Øystein: "floating lines, disconnected from the shape"). Every line on screen is an edge of the form that starts and ends at another edge. In a patch, a line must run right across it, so on a stone it meets the face's edges at both ends.
- **Edges by light, never a dark line** (The Witness's final wall, slides 30 and 31, as the coordinator read them). A step shows a lit edge over a shadowed one.
- **A face holds within about 2 L* in grey light, and detail is medium frequency** (the same source). Anything finer than a few mm is the first to fade or go.

### The split face (a section across the foliation)

1. **Bands.** A patch is 3 to 6 laminae bands across its 1024 mm height. Their relative weights are 60 to 140, so they come out 100 to 440 mm thick.
   - The boundaries share one wander of 2 to 5 mm, and each adds up to 1.5 mm of its own, so no two cross.
   - Each band is its own broken plane: up to 1 mm in or out of the face, leaning 1 to 3 degrees, and never more than 4 mm across its thickness.
   - The lean and offset come and go along u, from 20% to all of their value over 3 cycles.
   - Two bands' planes meet in a soft fold 50 mm wide.
2. **Facets.** The fracture across the bands is a triangulated lattice of corners about 200 mm apart along u and 120 mm across.
   - Each corner sits up to 1.6 to 2.8 mm in or out of the face (one amplitude drawn a patch), and each cell is split along a hashed diagonal. So every triangle is a plane with its own tilt of a degree or two, and the planes meet in folds with no step.
   - The lattice is bent by up to 0.4 of a cell, sheared by 1 or 2 cells over the patch's height, and its folds are rounded by a 7 mm Gaussian.
   - Why: soft-blended planes with independent heights read as pillows on a grid. An unbent lattice read as low-poly triangles, and an unsheared one as vertical columns. Above about 2.8 mm the face passes 2 L*.
3. **Steps.** Each band boundary has a step or not, even odds. A step is the upper band standing proud by 3 to 5 mm (weight 3) or 6 to 8 mm (weight 1), never deeper.
   - It runs right across the patch. Its depth varies along u over 4 cycles, but never falls below 55 to 70% of its most.
   - Its profile, from below, has three parts:
     - a broken edge, 3.5 to 4.5 times the depth and 16 to 32 mm wide: the shadowed face;
     - then a rounded arris 0.5 to 0.8 of that width, which rolls back by 60 to 80% of the step's height: the lit edge;
     - then the rest leans back into the face over 35 to 60% of the band above (at least 60 mm).
   - The edge wanders up to 4 mm above the boundary, and the break widens or narrows by 30% along u.
   - Why:
     - Steps that faded to nothing mid-face were floating lines.
     - Shallow steps that dipped to a third of their depth lost their lit edge for a few mm, and were then detected as two floating pieces.
     - Breaks narrower than 16 mm left a shallow step's shadow under 2 px wide at 5 m.
     - A lit slope gains fewer L* than a dark one loses, so only a narrow, steep arris balances the broad shadow. Without it a step is a dark groove.
4. **The tooth.** A fine planar tooth of soft-blended facets, 18 × 7 mm, with slopes of ±0.007 to ±0.011. Each band's gain is 0.6, 0.8 or 1.0, and the blend is 0.30.
   - Why: at the first version's gains (up to 1.5), its creases were short lines floating mid-face at 1 m (up to 69 a patch).
5. **Value.** Fine laminae 3 to 60 mm thick are each a shade lighter, darker or the same (±0.9%), meeting over 3 mm and following the foliation's wander. Each band is a shade its own (±0.8%), with a broad mottle of ±0.5%. Hue is left to the stone.
6. **Nothing plucked, nothing outlined.** The first version's plucks read as small squares at 5 m and as floating marks, so they are gone.

### The bed face (the foliation plane)

1. **The undulation is the read.** It is value noise on a lattice of 5 to 8 cells a patch, so a wavelength of about 250 to 400 mm, with a weaker octave at half that. It is 1 to 2 mm high.
2. **At most one scarp.** It is a coin toss: bed-0 has one, bed-1 has none.
   - The scarp is where the top lamina parted. It runs right across the patch, faces down-dip only, and is 1.5 to 3 mm deep, varying along u but never below 33 to 50% of its most.
   - Its break is 4 to 6 times its depth wide, between 10 and 20 mm, and it wanders 6 mm and 2 mm at about 128 and 43 mm.
   - Down-dip of it, the next lamina rises back over the rest of the patch's height (a sawtooth, so the face tiles).
   - The fresher parting is up to 3% darker and a little rougher (tooth slope 0.022 against 0.008), fading down-dip over 60 to 140 mm.
   - Why: the first version's flake scars were outlined all round like ink, overlapped, and had sides that feathered out mid-face (floating lines).

### Turns, and what is not here

A stone picks a patch, an offset and a turn by its seed:
- **Split patch:** only a half turn or a mirror in u, so the foliation stays along the bed.
- **Bed patch:** any turn.

Wear, polish, lichen, stains and every other mark that reads as history belong to the facts and the shader, never to a patch.

## What changed from the first version, and why

| Fault seen | Cause | Fix |
| --- | --- | --- |
| At 5 m the split faces read as flat grey card with loose horizontal grooves (coordinator) | 14 to 16 gated laminae with narrow 6 to 12 texel breaks in a flat field | 3 to 6 bands, each its own plane; a triangulated facet lattice across them; 16 to 32 mm breaks |
| Lines that start or end mid-face (Øystein) | ledges tapering to nothing along u; plucks; flake sides feathering out; tooth creases | full-width steps with a depth floor; no plucks; one full-width scarp or none; a faint tooth. Floating lines at 1 m went from 2 to 69 a patch (the round before) to 0 |
| A step reads as a dark groove | the shadowed break had no lit counterpart | a rounded arris rolling back 60 to 80% of the step's height |
| Bed scars outlined like ink, overlapping | flakes with scarps all round, nested and overlapping | no flakes; a broad undulation and at most one down-dip scarp |
| Spread above 2 L* at 5 m | facet corners up to 3.5 mm | 1.6 to 2.8 mm (spread 1.7 to 2.6 → 1.5 to 2.5) |
| Pillows on a grid; low-poly triangles; vertical columns (look-dev) | soft-min planes with independent heights; a straight lattice; an unsheared one | a continuous triangulated lattice, bent by 0.4 of a cell and sheared 1 or 2 cells |
| A row seam up to 4.6 after the shear | the lattice's corners did not shift with the shear at the wrap | the wrap shifts the corners by the shear; seam back to about 1 |
| split-3's double crease at the wrap | a seam's cap a few texels above a ledge's break | gone with the gated seams; no line at 1 m |

## The check sheet

The sheet's light rakes from the upper left at 30° elevation, with albedo 0.3, ambient 0.35, key 1.6, Lambert and no cast shadows.
- **Views:** 1 m (1 mm a pixel), 5 m and 12 m (5 and 12 mm a pixel). The far views low-pass the height and value with a Gaussian of one view pixel, take the normals from that height, then box down. This approximates the shader's footprint fade and mips; it is not a supersampled ground truth.
- **Floating lines:**
  - Detection: 3 × 3 and 5 × 5 top-hats of each polarity over 1 L*, joined on the torus across gaps of a pixel or two, and kept where they reach 2 L*.
  - A line is a piece over 10 px long and four times its width. It floats unless it spans every column or every row.
  - Through lines are the ones that do span.
- **Thin long lines:** top-hats over 2 L*, at most 2 px wide and over 40 px long (aim: none at 5 m).
- **Streaks:** 5 × 5 top-hats over 3 L*, over 40 px long and six times their width. They show which edges still read as strokes.
- **Lines and specks:** as in the first version (top-hats over 4 L*; specks up to 2 × 2 px).
- **Spread:** L*'s standard deviation and its 5th to 95th percentile range.
- **References beside the views, in grey:**
  - 05 (Aksla's old steps, Odd Roar Aalborg, CC BY-SA 4.0), cropped at about 1 mm a pixel beside the 1 m view;
  - 10 (the Furulund wall, Frode H. Korneliussen, CC BY-SA 4.0), at about 4 to 5 mm a pixel beside the 5 m view.

  Their scales are judged from the stones' sizes, not measured. Compare form and mark size, not tone: their tone is mostly lichen.

## Self-check numbers, from `checks.json`

| Patch | Drawn | Relief p1..p99 (mm) | Value band p5–p95 | Slope p50/p95/p99 (°) | L* sd / spread at 1 m | at 5 m | at 12 m | Floating at 1 / 5 / 12 m | Through at 5 m | Thin long at 5 m | Streaks at 5 m (longest) | Seam (h cols, h rows, L* cols, L* rows) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| split-0 | 3 bands, 1 step (6 mm), facets 1.8 mm | −2.2..3.1 | 0.019 | 0.8/2.6/12.6 | 0.95 / 1.74 | 0.73 / 1.51 | 0.48 / 1.36 | 0 / 0 / 1 (47 px) | 2 | 0 | 1 bright, 1 dark (85 px) | 0.94, 0.68, 1.17, 1.09 |
| split-1 | 6 bands, 3 steps (3, 3, 4 mm), facets 2.3 mm | −2.3..3.1 | 0.026 | 1.4/6.2/11.8 | 1.21 / 3.10 | 0.94 / 2.53 | 0.67 / 2.03 | 0 / 0 / 0 | 4 | 0 | 1 dark (171 px) | 0.93, 0.43, 1.02, 0.64 |
| split-2 | 3 bands, 1 step (4 mm), facets 2.3 mm | −2.3..3.0 | 0.023 | 1.1/3.6/11.4 | 1.00 / 2.49 | 0.79 / 2.23 | 0.59 / 1.94 | 0 / 0 / 0 | 2 | 0 | 1 dark (204 px) | 0.93, 0.69, 1.05, 0.89 |
| split-3 | 3 bands, 2 steps (6, 3 mm), facets 2.0 mm | −2.6..4.1 | 0.022 | 0.9/5.7/14.1 | 1.19 / 2.16 | 0.91 / 1.85 | 0.59 / 1.58 | 0 / 0 / 0 | 4 | 0 | 1 dark (163 px) | 1.01, 0.84, 1.28, 1.16 |
| bed-0 | one scarp (2.0 mm), undulation 1.6 mm | −1.6..1.6 | 0.023 | 0.7/1.6/3.7 | 0.57 / 1.33 | 0.48 / 1.25 | 0.41 / 1.19 | 0 / 0 / 0 | 1 | 0 | 0 | 0.46, 0.39, 1.25, 0.80 |
| bed-1 | no scarp, undulation 1.4 mm | −1.1..1.4 | 0.014 | 0.5/1.0/1.3 | 0.27 / 0.89 | 0.24 / 0.81 | 0.22 / 0.78 | 0 / 0 / 0 | 0 | 0 | 0 | 0.62, 0.60, 1.37, 1.26 |

Notes on the table:
- **Lines (over 4 L*) and specks** are 0 at every view on every patch. Edge density (Sobel over 10 L*) is 0 throughout.
- **Through lines and streaks are the same edges.** Each split patch's deepest step is a through line, and above 3 L* its shadow is a stroke 85 to 204 px long at 5 m. This is a ledge's edge running to the face's edges, as the rule asks. The streak count says it is still the strongest mark on a split face.
- **Where split-1's spread comes from.** I rebuilt split-1 with one component off at a time. At 5 m, facets alone give 1.6 L*, without steps it is 2.2, and without facets 2.1. The excess is six bands and three steps together, not fine detail.
- **Riser steps.** The first version's check (a break of 2 mm within 6 mm on a 170 mm riser) no longer finds the softer 16 to 32 mm breaks, and reads about 0. By construction there are 7 steps in 4096 mm of split face, so about one riser in three or four crosses a step.

## Known faults

1. **Straight ruled ledges.** A full-width step wanders only 2 to 5 mm over a metre and keeps much the same contrast along its length. In the 2 × 2 tiling and at one-eighth, the split faces read as ruled paper. On a stone it will be one or two ledges across a 300 to 600 mm face, which may hold, but in the patch it looks drawn by a ruler.
2. **The facet lattice repeats.** At 4 mm a pixel in `patches-tiling.png`, split-1 and split-2 show rows of similar crescent folds where the sheared lattice's cells line up.
3. **Calm in grey.** Within about 2 L* the split faces are gentle planes, and next to references 05 and 10 they read flat. The references' strong marks are mostly the stones' own form (corners, beds, joints) and lichen, which belong to the mesh and the shader, not to a patch. Whether the patch does enough under them is only judged once stones are laid.
4. **split-1 at 2.5 L* (p5 to p95) at 5 m,** above the 2 L* bar. Its sd is 0.94.
5. **The floating-line count sits near its threshold.** A full-width step whose lit edge dips under 1 L* for a few pixels is counted as floating. Moving the depth floor from 55 to 70% back to 40 to 55% brought one back on split-1 at 5 m. At 12 m, split-0's arris shows one 47 px floating piece.
6. **One bed patch has no scarp.** Two patches with a coin toss is thin. bed-1 is the undulation alone (0.8 L* at 5 m), which may read as plaster.
7. **Not seen in light or material.** The sheet is grey Lambert with no cast shadows and no hue, and there is no Blender render. Six patches is the plan's count; repetition across stones is untested until stones are laid.

## What a reviewer should judge

The reviewer should judge these from `patch-<name>.png` (each beside its references), `patches-tiling.png`, `patches-distances.png` and `patches-eighth.png`:
1. **Split face at 1 m beside 05.** Does it read as a cleavage section of phyllite (bands, broad facets, low ledges, lit over shadowed), or as a ruled board (faults 1 and 3)?
2. **5 m beside 10.** Is there any floating mark left to the eye, whatever the count says? Is a full-width ledge an acceptable strongest mark?
3. **Bed face.** Does the undulation with one scarp, or none, read as a cleavage plane, or as plaster (fault 6)?
4. **Repetition.** Would the facet rows in `patches-tiling.png` give a patch away on a wall (fault 2)?
5. **Next step.** Should the second half of R2a (a wall stone, a step and a coping at L0 and L1) start with these patches, so they are judged on stones? Or should one more round first make the ledges less ruled and break up the lattice?

## The coordinator's read, 22 October, 22:10

Not passed; paused here for the week's usage. On the tiling sheet the split faces read as ruled paper: each ledge is a straight, level line at one depth, and the four split patches put them at near-even spacing. Real lamination traces wander. The next round keeps every ledge running edge to edge, with nothing ending mid-face, and changes three things:
- each ledge follows a gently curving trace, a few degrees off the patch's axis;
- its depth swells and thins along its length, staying above the floor;
- the spacing differs between patches.

It also breaks the crescent rows (faults 2 and 4), and gives bed-1 its scarp or retires it. The per-patch sheets (`patch-*.png`, 2 MB each) are rebuilt by `blender/tools/patch_sheet.py` and kept out of git.

**Later, 22 October, 23:10.** The 2 L* limit is withdrawn (SN7). Øystein judged today's stones closer to what he wants than the street target. The next round may carry more value where it is relief lit by the light (lamina steps, worn hollows), never small-scale noise, and is judged beside today's stones at the same distance.
