# Finish test, round 4

House 107's corner in 1989, A (procedural, our own) only, beside photos 09 and 01, in clay: value grey at each material's lightness, real gloss and no hue. This is the last round of this way of building.

**Sheet layout:**
- Top row: overcast. Bottom row: low sun, raking the street wall from its east end at 18° elevation.
- Columns: A at 1:1 from the 2560×1440 renders, then photo 09 (and photo 01 below it), scaled to about the same metres per pixel.

**Views:**
- `eye.jpg`: 1.6 m high, about 3 m away.
- `street.png`: the street stop, 20 m.
- `raised.png`: 12 m up.
- `high.png`: high.

All four views were rendered with the final code.

**Build:** run/build.sh (corner.py, bake.py, tiles.py, scans.py, marks.py), then run/render.sh r04 eye,street,raised,high A under the Unity lock, then run/sheets.sh r04 A.

**Budget:** every new mark is in a texture or a normal map; no triangle was added.
- **Triangles:** 2,731 near (budget 3,000) and 793 street (budget 800). corner.py still fails over budget.
- **Textures A reads,** all 1,024²:
  - the ply sheet's authored scan tile over 0.5 m (0.49 mm a texel), from Poly Haven's CC0 `plywood`;
  - the batten's scan tile over 2 m, from Poly Haven's CC0 `raw_wooden_floor_01` (both logged in `docs/research/downloads.md`);
  - the flake atlas over 0.5 m (R plates, G halo, B run cores);
  - the tileables (painted board, trim sheet, stone, tile, zinc) over 2 m, each with its normal;
  - the pages (history, geometry, the street level's lap normal) at 128 px/m.

**Verdict, bad first:**
1. **It does not hold yet.**
   - **The sheet's stains have the wrong edge.** 09's lower panels carry broad, soft, mottled grey clouds. A's stain is a flat band behind a crisp, scalloped front, like torn paper.
     - The depth is closer than in round 3 but still short: lower p5 136 against 09's 68.
     - The dry islands deep in a stain are now only 4 L\* lighter, with no rim, as asked. That raised the lower p5 from round 3's 119.
     - What is missing is still how 09's stain grades and speckles from inside, not how deep it goes.
   - **Two thin dark dashes remain on the upper sheet's middle panel at the street stop,** in both lights. Each is 1 px tall and about 13 cm long, at render rows 699 and 702.
     - The grain fade is in and works: at 20 m the face grain is gone and only the mottle and stains remain. Forcing the fade to full left these dashes pixel-identical, so they are not the grain.
     - All four history channels and the geometry page are smooth at that spot. Their source (the street mesh or SSAO) is unfound.
   - **The sill runs are on the page but faint at eye level,** about 4–5 L\*. They are narrow, restart at each lap and start at the sill ends, but they do not read as runs beside 09's.
   - **The battens are lighter than 09's.** 09's are mid-grey and weathered with light chips; A's are near-white with grey sides.
   - **In low sun the plinth's broad planes hang a little like vertical folds.** Round 4's first plinth read as crazy paving there: small facets, each stepping off its neighbour. The facets are now about a block's size and the steps between them are worn to soft ramps, so the net is gone, but the planes are soft and run vertically.
   - **In low sun at the street stop, the lap shadows on the wall break into short dashes.**
2. **What works:**
   - **The wall at eye level:**
     - flakes vary in scale, only at drip edges, board ends, sill ends and the lowest courses;
     - each flake shows bare wood in its own value, with a chalky halo and no dark rim;
     - their shapes share nothing with the sheet's fronts;
     - each board darkens to its underside, with a soft lap shadow;
     - each course has its own value, so no board reads as replaced.
   - **The head wicking is back,** under the head on the leaking side only.
   - **The laps at the street stop match 09:** 5.8 mm integrated, the same as 09.
   - **The trims are worn,** and the battens' broken arrises are drawn only where the curvature mask says an edge is.
   - **The plinth no longer reads as stage concrete:**
     - in overcast, split blocks with grain, mottle and broad planes;
     - the mortar sandy.
   - **The fan stays,** with both bends kept true.
   - **The exposure is unchanged** and matches 09.

**Measured:**
- **Board-to-board value at eye level,** mean neighbour |dL\*| in two column bands: 1.81 and 1.62, at most 4.95. Round 3 was 1.99 and 1.86, at most 5.5. For comparison, 09 is 0.37–1.7 and 01 is 1.35–3.34.
- **Lap at the street stop, integrated across the line** (`lapint`, at 10 mm/px): 5.8 mm median (round 3: 5.7; 09: 5.8).
- **Sheet, p5/p50 at the street stop:**
  - middle 157/201 (round 3: 156/216; 09: 103/204);
  - lower 136/201 (round 3: 119/186; 09: 68/190).

  09's values include the casing's gap and shadow.
- **Paint at its brightest, p50–p95:**
  - eye level 223–232 against 09's 226–233;
  - street stop 226–229 against 09's 223–231.

  So nothing was stopped down.

**What changed, all as data in `finish.json`:**
- **The flake atlas** is `tiles.flake`.
- **Board tone:**
  - `marks.shade` darkens each board to its underside and softens the lap shadow (`lapDark`, `lapCoreMm`, `lapReachMm`);
  - `marks.boardValueL` gives one value per course.
- **The trims' wear** is `marks.loss.tops` and `marks.loss.arris`.
- **The runs** are `marks.water.sill`: they restart at each lap.
- **The head wicking** is `edges.head` with `headSide`, on the leaking side only.
- **The sheet:**
  - `materials.sheet.stain` sets the islands (`islandW`, `islandL`);
  - `materials.sheet.grainFar` fades the grain to mip 6 once far.
- **The batten's chips** are `marks.water.batten`, through the curvature mask.
- **The plinth's stone** is `tiles.stone`: block-sized facets, their steps worn by `facetSoftMm`, grain and mottle.
