# R2a, first half: the slate's face patches

**In short.** Six shared face patches for the town's phyllite (SN6, held to SN4, SN5 and SN7), made by rule and checked flat in grey. This is the third version ("patches 3"). It was reworked after the coordinator's read of the second version (22 October, 22:10), where the split faces read as ruled paper.
- **The patches:** four split faces (wall fronts and risers) and two bed faces (tread and coping tops). Each is 1024² texels at 1 mm, seamless, with 16-bit height, normal and value maps.
- **Seeds:** every draw comes from `HS.Stream(1989, "stone/slate/patch/<name>", purpose)`. `check` rebuilds all six and every pixel hash matches.
- **What changed:**
  - Every ledge follows its own gently curving trace.
  - Its depth swells and thins above a floor. Each face has one major ledge that stays a line at 12 m; the rest are minor and fade whole.
  - The number and spacing of ledges is set per face, so no two faces share a rhythm.
  - Bands meet in folds instead of steps.
  - The facets come from scattered corners joined by a Delaunay triangulation, not a lattice.
  - Both bed faces have a scarp.
- **What the checks found:**
  - At 1, 5 and 12 m: no floating lines, no thin long lines, no specks and no seams.
  - The 5 m spread (p5 to p95) is 1.47 to 2.06 L* on the split faces and 1.13 to 1.29 on the bed faces.
  - Ledges stray 11 to 25 mm from a straight line (the second version: 5 to 10).
  - Ledges swell 1.3 to 2.2 times along their run.
  - No face puts a ledge within 25 mm of another face's.
- **The A/B on the spread limit:** split-2 with its facets doubled holds 2.86 L* at 5 m and still passes every line check, but it is no nearer references 05 and 10. My recommendation is in [the A/B](#the-ab-on-the-spread-limit).
- **What still fails:**
  - In grey the faces are still calm and flat beside 05 and 10.
  - The traces read as smooth drawn waves, and a ledge reads as a narrow rope.
  - split-1 holds 2.06 L* at 5 m.
  - The fix for the crescent rows rests on the eye more than the numbers.
  - Nothing has been seen in light or material, or by a reviewer.

| What | Where |
| --- | --- |
| Generator | `blender/parts/stone/slate/patches.py` (`build`, `check`) |
| Manifest (pixel hashes, each patch's drawn parameters) | `blender/parts/stone/slate/patches.manifest.json` |
| Maps (untracked, rebuilt) | `cache/stone/patches/slate-<name>-{height,normal,value}.png` |
| Sheet tool | `blender/tools/patch_sheet.py` |
| Sheets and numbers | this folder: `patch-<name>.png` (with references beside; untracked), `patches-distances.png`, `patches-eighth.png`, `patches-tiling.png`, `patches-histograms.png`, `patches-ab.png`, `checks.json` |

Run everything with Blender's Python (`/Applications/Blender.app/Contents/Resources/5.2/python/bin/python3.13`; it has numpy). `check` takes about 3 s for all six, and the sheet about 23 s.

## The rules, and why

Phyllite is laminated. It parts along its foliation into leaves a centimetre to a hand thick, each a little different, and breaks across them. So the two workings show two different faces.

Three rules hold for both, and they shaped everything below:
- **No floating line** (Øystein: "floating lines, disconnected from the shape"). Every line on screen is an edge of the form that starts and ends at another edge. In a patch, a line must run right across it, so on a stone it meets the face's edges at both ends. This must hold at every distance where the line shows. A ledge whose thin stretch fades while its thick stretch still shows has broken in two.
- **Edges by light, never a dark line** (The Witness's final wall, slides 30 and 31, as the coordinator read them). A step shows a lit edge over a shadowed one.
- **A face holds within about 2 L* in grey light, and detail is medium frequency** (the same source; SN7). Anything finer than a few mm is the first to fade or go.

### The split face (a section across the foliation)

1. **Ledges, set per face.** The set's design, not a draw, is how many ledges each face has and how many of them are major: split-0 has 2 (one major), split-1 has 3 (one major), split-2 has 1 (major) and split-3 has 2 (none major).
   - The gaps between ledges are drawn from three classes: 70 to 110 (weight 2), 130 to 260 (weight 3) and 300 to 560 (weight 2). They are then scaled to the patch, and drawn again until the widest is at least twice the narrowest. So a close pair sits beside a broad plain face.
   - Inside each gap there are soft band boundaries (no step). Their number is drawn from 0 up to one for each 150 mm of the gap past the first 150, and is never more than 2. The bands' relative thicknesses are 60 to 140.
   - Why: in the second version every boundary had even odds of a step. The four faces put their ledges at similar spacing, and two faces put theirs at the same rows.
2. **Traces.** Every boundary follows its own trace: a sum of whole cycles a patch (wavelengths of 1024, 512 and 341 mm), so it closes across the u seam. A ledge's trace is at most 4 to 7.5° off the patch's axis, and a soft boundary's 1.5 to 3.5°. A common foliation wander of 1 to 3 mm is added on top.
   - No two boundaries come closer than 45 mm at any u. Where they would, the traces are scaled down. So ledges never cross or touch.
   - Why: a straight line at a few degrees cannot close across the seam, and a level one reads as ruled.
3. **Bands meet in folds.** Each boundary has a height in or out of the face, up to 1.5 mm. It comes and goes along u, from 20% to all of its value over 3 cycles. A band is the plane between its two boundaries' heights, so it leans by their difference: under 0.6° on these faces. Neighbouring bands meet in a soft fold 50 mm wide: a ridge or a valley, never a step.
   - Why: in the second version each band leaned its own way. Where two neighbours leaned the same way they made soft steps of up to 4 mm. These added spread (split-2's bands alone held 1.68 L* at 5 m, now about 1.1), and in places they cancelled a ledge along its run.
4. **Facets from scattered corners.**
   - **Corners:** thrown at random, 3000 tries in whole millimetres. Each corner has a reach of 80, 110 or 150 mm (weights 2, 3, 1). A corner is kept only where no kept corner is within the mean of the two reaches across the foliation, or 5/3 of it along.
   - **Triangles:** the corners are joined by a Delaunay triangulation on the torus. That gives 43 to 48 corners and 86 to 96 triangles a patch.
   - **Height:** each corner sits up to 1.6 to 2.8 mm in or out of the face (one amplitude drawn a patch). It is 70% of that on a face with three ledges, so split-1's facets are 1.6 mm. Each triangle is a plane, and the folds between them are rounded by a 7 mm Gaussian.
   - Why: the second version's bent, sheared lattice left rows of similar crescent folds (its fault 2). Every row of cells had the same size and the same bend.
5. **Steps.**
   - **Depth:** a major ledge is 5.5 to 6.8 mm where it swells most and never under 4 mm. A minor ledge is 2.6 to 3.0 mm at most and never under 1.5 mm. Either thins to 58 to 66% of its most. The depth swells 2 to 4 times a patch, the swells a little narrower than the thin runs between.
   - **Profile:** as in the second version.
     - A broken edge 3.5 to 4.5 times the depth, between 16 and 26 mm wide (the shadowed face).
     - A rounded arris 0.5 to 0.8 of that width and never over 14 mm, rolling back 60 to 80% of the depth (the lit edge).
     - The rest leans back over 35 to 60% of the band above.
   - **Edge:** it sits up to 3 mm above its boundary and wanders there at fine wavelengths. The break widens or narrows by 30% along u.
   - **Why the depths:**
     - A fixed floor of 2.2 to 3 mm broke at 12 m under swells of 6 to 8 mm. Its thick stretch was a line there and its thin stretch was not, so it floated.
     - A ledge in between (4 to 5 mm) was a line at 12 m in some stretches and not in others.
     - So the major ledge keeps a 4 mm floor, which is a line at 12 m along its whole run. A minor ledge stays under 3 mm, so it is a line at 1 and 5 m and fades whole by 12 m (the finest marks fade first).
   - **Why the width:** breaks wider than 26 mm made a swelling ledge's shadow a band at 5 m, no longer a line.
6. **The tooth and value** are unchanged:
   - a faint planar tooth (18 × 7 mm, gains 0.6 to 1.0);
   - fine laminae ±0.9% in value, following the bands;
   - each band ±0.8%, with a broad mottle of ±0.5%;
   - hue left to the stone;
   - nothing plucked, nothing outlined.

### The bed face (the foliation plane)

1. **The undulation is the read.** It is value noise on a lattice of 3 to 8 cells a patch, a wavelength of about 130 to 340 mm, longer one way than the other on some. It is 1 to 2 mm high.
2. **One scarp on each.** The scarp is where the top lamina parted.
   - **Run and depth:** it runs right across the patch on a gently curving trace (5 to 6° at most), faces down-dip, and is 2.4 to 3.0 mm deep at most, never under 70 to 80% of that.
   - **Break:** 4 to 6 times its depth wide, between 10 and 20 mm. It wanders 3 mm and 1 mm at about 128 and 43 mm.
   - **Behind it:** down-dip, the next lamina rises back over the rest of the patch (a sawtooth, so the face tiles). The fresher parting is up to 3% darker and a little rougher, fading down-dip over 60 to 140 mm.
   - **The two faces differ:** bed-0's scarp faces down the image, away from the light, so it is a shadowed edge. bed-1's faces up the image, towards the light, so it is a lit edge.
   - Why: the second version's bed-1 had no scarp (its fault 6) and was only the undulation, 0.8 L* at 5 m. A lit scarp gains fewer L* than a shadowed one loses, and its light turns with its trace. At the second version's wander (6 and 2 mm) its edge turned up to 18° and its light came and went, and at a floor of 1 to 1.6 mm it broke at 5 m.

### Turns, and what is not here

A stone picks a patch, an offset and a turn by its seed:
- **Split patch:** only a half turn or a mirror in u, so the foliation stays along the bed.
- **Bed patch:** any turn.

Wear, polish, lichen, stains and every other mark that reads as history belong to the facts and the shader, never to a patch.

## What changed from the second version, and why

| Fault seen | Cause | Fix |
| --- | --- | --- |
| Straight, level ledges: ruled paper in the 2 × 2 (coordinator, 22:10; fault 1) | all boundaries shared one wander of 2 to 5 mm | each boundary its own periodic trace, 4 to 7.5° at its steepest, 45 mm apart at least; deviation from a straight line 5–10 → 11–25 mm |
| A ledge at one depth (22:10) | depth varied over 4 cycles within 55 to 70% of its most, at similar depths on every ledge | one major ledge a face (5.5 to 6.8 mm, floor 4 mm) and minor ones (2.6 to 3.0, floor 1.5); swelling 2 to 4 times a patch |
| Floating at 12 m once ledges swelled (found on the way) | a thin stretch faded at 12 m while the thick stretch was still a line | the major and minor classes above: a major ledge is a line along its whole run at 12 m, and a minor one fades whole |
| Near-even spacing, the same across faces (22:10) | even odds of a step at every band boundary | ledge counts set per face (2, 3, 1, 2); gaps from three classes, the widest at least twice the narrowest; no two faces' ledges within 25 mm |
| Soft steps between bands added spread and cancelled ledges (found on the way) | each band leaned its own way, and neighbours leaning the same way made steps of up to 4 mm | bands as planes between their boundaries' heights, meeting in folds |
| Rows of crescent folds in the 2 × 2 (fault 2) | a bent, sheared lattice: every row of cells alike | scattered corners and a Delaunay triangulation on the torus; no lattice, no bend |
| split-1 at 2.53 L* at 5 m (fault 4) | 6 bands, 3 steps and facets of 2.3 mm together | 5 bands, 3 ledges of which one is major, facets at 70% (1.6 mm): 2.06 |
| bed-1 with no scarp: plaster (fault 6) | the scarp was a coin toss | a scarp on both faces, bed-1's lit; a finer wander (3 and 1 mm) and a 70 to 80% floor so a lit scarp holds at 5 m |

## The check sheet

The sheet's light rakes from the upper left at 30° elevation, with albedo 0.3, ambient 0.35, key 1.6, Lambert and no cast shadows.
- **Views:** 1 m (1 mm a pixel), 5 m and 12 m (5 and 12 mm a pixel). The far views low-pass the height and value with a Gaussian of one view pixel, take the normals from that height, then box down. This approximates the shader's footprint fade and mips; it is not a supersampled ground truth.
- **Floating lines, through lines, thin long lines, streaks, lines and specks, spread:** as in the second version.
  - A line is a piece of 3 × 3 and 5 × 5 top-hats over 1 L*, reaching 2 L*, over 10 px long and four times its width. It floats unless it spans every column or row.
  - Thin long lines are at most 2 px wide and over 40 px long (top-hats over 2 L*).
  - Streaks are over 3 L*.
  - Lines and specks are over 4 L*.
  - The spread is L*'s 5th to 95th percentile range.
- **New in this version:**
  - **Ledges.** Each ledge's trace is found in the stored height near the generator's boundary. In every column the trace is the middle of its broken edge: the centroid of the rows around the steepest fall that fall at least half as fast. The steepest row alone jumps with the tooth, because a break falls almost evenly across its middle.
    - Straightness: the trace's deviation from its best straight line (range and RMS), and its local angle over 33 mm (p2, p98, most).
    - Depth along the run: the highest point within 35 mm up-dip minus the lowest within 35 mm down-dip (p5, p50, p95, and p95 over p5). This includes the facets and folds nearby, so it reads a little under the drawn depths.
  - **Spacing across the four split faces.** Each face's ledges, bands, gaps and widest over narrowest. Across the set, the gaps' coefficient of variation. Side by side, the most of one face's ledges that have a ledge of another face within 25 mm at the same rows.
  - **Repeat.** The autocorrelation of the facets' fold map (the magnitude of their Laplacian), outside a central ellipse 30 by 20 mm:
    - across the torus, its highest local peak and where it is;
    - in each 256 mm window, the same peak, as a mean and a most over the sixteen windows (a bent lattice loses its peaks across the torus but keeps short rows of like cells);
    - and across the torus for the 1 m view's L* band-passed between 2 and 40 mm, which is high where the face looks alike shifted along u, as ruled ledges do.
  - **A local seam.** The jump across the wrap over the steps of the three rows (columns) either side of it. The old seam measure is kept, but it divides by the whole face's mean step, so a ledge's break that crosses the wrap reads there as a seam.
  - **The A/B sheet** (`patches-ab.png`). It shows split-2 as built (A) and with its facets doubled (B, built in memory), with nothing else changed. Both are at 1 m beside 05 and at 5 m (×4) beside 10, with their spreads and line checks in `checks.json` under `ab`.
- **References in grey:**
  - 05 (Aksla's old steps, Odd Roar Aalborg, CC BY-SA 4.0), at about 1 mm a pixel;
  - 10 (the Furulund wall, Frode H. Korneliussen, CC BY-SA 4.0), at about 4 to 5 mm a pixel.

  Their scales are judged from the stones' sizes, not measured. Compare form and mark size, not tone: their tone is mostly lichen.

The second version's numbers below were measured with the same functions on its maps, rebuilt from its generator at `9d26333`. Its ledges were located from the drawn step list.

## Self-check numbers, from `checks.json`

| Patch | Drawn | Relief p1..p99 (mm) | Value band p5–p95 | Slope p50/p95/p99 (°) | L* sd / spread at 1 m | at 5 m | at 12 m | Floating at 1 / 5 / 12 m | Through at 5 / 12 m | Thin long at 5 m | Streaks at 5 m (longest) | Seam, local (h cols, h rows, L* cols, L* rows) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| split-0 | 3 bands; ledges: major 6.8 (floor 4.0), minor 2.6 (1.6); facets 1.8 mm, 48 corners | −1.9..3.6 | 0.020 | 0.8/4.7/14.1 | 1.14 / 1.74 | 0.87 / 1.49 | 0.54 / 1.25 | 0 / 0 / 0 | 3 / 1 | 0 | 2 dark (86 px) | 1.02, 1.07, 1.04, 1.10 |
| split-1 | 5 bands; ledges: minor 3.0, minor 2.9, major 5.9 (4.0); facets 1.6 mm, 46 corners | −1.6..2.8 | 0.022 | 0.9/6.8/13.4 | 1.19 / 2.37 | 0.88 / 2.06 | 0.52 / 1.58 | 0 / 0 / 0 | 4 / 1 | 0 | 1 dark (204 px) | 1.02, 1.02, 1.04, 0.88 |
| split-2 | 3 bands; ledge: major 5.9 (4.0); facets 2.3 mm, 45 corners | −2.1..2.6 | 0.026 | 1.0/2.5/12.7 | 1.00 / 1.92 | 0.78 / 1.69 | 0.52 / 1.55 | 0 / 0 / 0 | 2 / 1 | 0 | 1 dark (164 px) | 1.02, 1.15, 1.04, 0.97 |
| split-3 | 4 bands; ledges: minor 2.7, minor 2.9; facets 2.0 mm, 43 corners | −1.9..2.1 | 0.022 | 0.8/3.1/7.9 | 0.75 / 1.71 | 0.54 / 1.47 | 0.38 / 1.31 | 0 / 0 / 0 | 2 / 0 | 0 | 0 | 1.01, 1.06, 1.08, 1.16 |
| bed-0 | scarp 2.8 (floor 2.1), facing down; undulation 1.6 mm | −2.1..2.2 | 0.023 | 0.6/1.6/7.5 | 0.68 / 1.33 | 0.59 / 1.29 | 0.49 / 1.34 | 0 / 0 / 0 | 1 / 1 | 0 | 0 | 1.08, 1.08, 1.10, 1.06 |
| bed-1 | scarp 2.9 (floor 2.1), facing up (lit); undulation 1.4 mm | −1.9..1.7 | 0.029 | 0.6/1.3/7.0 | 0.46 / 1.18 | 0.39 / 1.13 | 0.33 / 1.07 | 0 / 0 / 0 | 1 / 0 | 0 | 0 | 1.00, 1.03, 1.06, 1.06 |

Notes on the table:
- **Lines (over 4 L*) and specks** are 0 at every view on every patch. Edge density (Sobel over 10 L*) is 0 throughout.
- **Through lines are the ledges.**
  - At 5 m every ledge is a through line. Some count twice: the lit arris and the shadow separately.
  - At 12 m only the major ledges and bed-0's shadowed scarp remain, one a face. split-3 (two minor ledges) and bed-1 (a lit scarp) show no line at 12 m.
- **The old seam measure** reads 4.0 on split-0's rows. Its minor ledge lies at row 1023, so the break crosses the wrap. The step across the wrap (0.087 mm) lies between its neighbours' (0.093 and 0.074), the local measure reads 1.07, and the seams' crossing in `patches-tiling.png` shows the ledge running on. Every other patch reads 0.4 to 1.3 on the old measure.

### Ledges: straightness and depth along the run

| Patch | Ledge (row, mm) | Deviation from straight, range / RMS (mm) | Angle over 33 mm, p2..p98 / most (°) | Depth p5 / p50 / p95 (mm) | Swell p95/p5 |
| --- | --- | --- | --- | --- | --- |
| split-0 | major (278) | 20.3 / 6.3 | −7.9..8.1 / 9.0 | 3.9 / 4.7 / 6.6 | 1.69 |
| split-0 | minor (1024) | 20.3 / 5.2 | −5.7..6.9 / 7.6 | 1.2 / 1.5 / 2.2 | 1.83 |
| split-1 | minor (77) | 23.4 / 5.5 | −6.7..7.0 / 8.7 | 1.5 / 1.8 / 2.6 | 1.70 |
| split-1 | minor (554) | 20.1 / 4.7 | −5.8..6.5 / 7.3 | 1.3 / 2.0 / 2.4 | 1.93 |
| split-1 | major (978) | 11.3 / 3.1 | −4.6..6.0 / 7.0 | 3.3 / 3.9 / 4.7 | 1.44 |
| split-2 | major (671) | 24.2 / 5.8 | −5.8..8.7 / 9.5 | 3.6 / 4.0 / 4.6 | 1.30 |
| split-3 | minor (367) | 24.9 / 5.7 | −7.1..9.5 / 10.9 | 1.5 / 1.7 / 2.1 | 1.36 |
| split-3 | minor (616) | 17.5 / 4.3 | −6.4..6.5 / 6.8 | 1.3 / 2.1 / 2.9 | 2.18 |
| bed-0 | scarp (21) | 15.0 / 3.2 | −6.8..8.1 / 11.6 | 2.1 / 2.7 / 2.9 | 1.35 |
| bed-1 | scarp (936) | 19.4 / 5.4 | −8.5..9.0 / 10.5 | 2.0 / 2.2 / 3.4 | 1.69 |

The second version, measured the same way:
- **Straightness:** its seven split ledges strayed 4.7 to 9.9 mm from straight (RMS 1.2 to 2.6). Their angle at most was 3.0 to 7.8°, and that came from the short-wavelength wander of the edge, not a curve.
- **Depth:** they swelled 1.28 to 3.16 times, but its minor ledges thinned to 0.7 to 1.1 mm (p5).
- **What is new:** this version's ledges do not vary more in depth than the second version's. What is new is the floor (minor ledges never under 1.2 mm measured, major ones never under 3.3) and that the faces differ: one deep ledge and the rest shallow.

### Spacing across the four split faces

| | split-0 | split-1 | split-2 | split-3 | Across the set |
| --- | --- | --- | --- | --- | --- |
| Ledges (major), bands | 2 (1), 3 | 3 (1), 5 | 1 (1), 3 | 2 (0), 4 | |
| Gaps between ledges (mm) | 746, 278 | 477, 425, 123 | 1024 | 249, 775 | CV 0.57 (second version 0.58) |
| Widest over narrowest | 2.68 | 3.89 | — | 3.11 | |
| Side by side: ledges within 25 mm of another face's | | | | | 0 (second version: split-2's only ledge 4 mm from one of split-1's) |

### Repeat

| Face | Facet folds, across the torus: second → third version | Facet folds, mean in 256 mm windows | most in a window | L* at 1 m, across the torus (ruled ledges) |
| --- | --- | --- | --- | --- |
| split-0 | 0.10 → 0.18 | 0.127 → 0.147 | 0.37 → 0.42 | 0.72 → 0.23 |
| split-1 | 0.15 → 0.13 | 0.153 → 0.088 | 0.30 → 0.24 | 0.80 → 0.46 |
| split-2 | 0.09 → 0.13 | 0.162 → 0.098 | 0.41 → 0.36 | 0.63 → 0.49 |
| split-3 | 0.12 → 0.14 | 0.178 → 0.090 | 0.35 → 0.25 | 0.28 → 0.33 |

Across the torus no measure separates the two versions. The second version's bend had already broken the lattice's long-range order, so its rows were local.
- **In 256 mm windows,** the repeat falls by 40 to 50% on split-1, split-2 and split-3, and these are the faces where the crescent rows were seen. It rises on split-0, which has the fewest corners (48), so each window holds only a few facets.
- **The L* repeat along u** falls on the three faces with the ruled ledges. On split-3 it rises a little: its two minor ledges are close (249 mm apart), so a shift along u keeps the pair.

## The A/B on the spread limit

This is one face and one change. split-2 is shown as built (A) and with its facets' amplitude doubled (B). Nothing else changes. The sheet is `patches-ab.png`, with 05 and 10 beside the faces.

| | Facets | Spread at 1 / 5 / 12 m (L*) | Floating at 1 / 5 / 12 m | Through at 5 / 12 m | Thin long, specks |
| --- | --- | --- | --- | --- | --- |
| A, as built | 2.3 mm | 1.92 / 1.69 / 1.55 | 0 / 0 / 0 | 2 / 1 | 0, 0 |
| B, facets × 2 | 4.6 mm | 3.08 / 2.86 / 2.62 | 0 / 0 / 0 | 2 / 1 | 0, 0 |

A scan in memory with the same checks found where the line rules start to bind:
- **split-2:** × 1.5 gives 2.26 L* at 5 m. × 2.5 gives 3.49, with 2 floating lines at 12 m. × 3 gives 4.13, with 3 floating at 12 m.
- **split-0:** × 1.5 gives 2.03. × 2 gives 2.57, with one thin long line at 5 m. × 2.5 gives 3.05, with 1 floating line at 5 m and 2 at 12 m.

What the sheet shows:
- **B at 1 m:** its broad facets read as soft fracture planes a few hundred mm across, where A's are barely seen. B looks more like broken stone and adds no line.
- **At 5 m:** B is a shade more modelled.
- **Beside the references:** neither A nor B is anywhere near 05 or 10. Their marks are the stones' own form at block scale (corners, beds, joints in deep shadow, breaks of 10 to 50 mm) and lichen. A patch of 2 to 5 mm relief cannot carry those at any spread.

**Evidence, in short:**
- Doubling the facets takes a face to about 2.9 L* at 5 m without breaking any line rule.
- Going further breaks the floating rule at 12 m (split-2 from × 2.5, split-0 already at × 2 with a thin line).
- Neither level closes the gap to the references.

**Recommendation (for the coordinator, who decides SN7):**
- **Split faces:** let a split face reach about 3 L* at 5 m in grey, where the extra comes from broad planes (marks over about 50 mm) and every line check stays at zero. On these faces the line rules, not 2 L*, are what binds first.
- **Bed faces:** keep them at about 2.
- **Do not raise it for these patches yet.** Judge A beside B on the first wall stone at L0 in the town's light (the second half of R2a), together with the other marks (wear, the joints' fill and moss, weather). SN7's evidence is Øystein's "a bit much" beside the clay, so the limit is best judged as he judged it: on stones, with the other marks.
- **Do not expect the limit to fix the flatness.** That belongs to the stone's mesh and to growth.

## Known faults

1. **Calm and flat beside 05 and 10** (the second version's fault 3, unchanged). At 1 m, split-1 reads as a smooth board crossed by soft waves, and the facets (1.6 to 2.3 mm) are barely seen. The A/B above says the spread limit is not the main cause.
2. **The traces read as drawn waves.** Each trace is a sum of one to three whole cycles a patch, so it is smooth and regular. In the 2 × 2 the ledges look like gentle sine curves, not broken lamination: there is no kink, no step and no change of pace along a run.
3. **A ledge reads as a narrow rope at 2 to 4 mm a pixel.** The arris rolls back 60 to 80% of the depth, so the lit roll sits right over the shadow band. It is beaded where the break widens and narrows along its run (8 cycles a patch).
4. **The spacing is uneven within a face, not across the set.** The gaps' coefficient of variation is 0.57, as in the second version (0.58). split-1 (gaps 477, 425, 123) and split-3 (249, 775) both read as a close pair beside a broad face, and in a 2 × 2 that is a rhythm of its own.
5. **The fix for the crescent rows rests on the eye.** There are no crescents (the folds are straight now) and no rows that I can see in `patches-tiling.png`, and the local repeat falls on three faces. But split-0's local repeat is higher than the second version's, and nothing separates them across the torus. At 4 mm a pixel the largest triangles in split-0 and split-1 show as straight-edged wedges, which risks the low-poly read that the second version's notes named.
6. **split-1 holds 2.06 L* at 5 m,** just over "about 2". With three ledges, the ledges set the spread: without facets it is still 1.79.
7. **Minor ledges fade whole by 12 m by design.** split-3 and bed-1 show no line at 12 m. It is open whether a face with no line at that distance reads as stone or as plaster beside its neighbours.
8. **The bed faces are nearly uniform at 1 m** (1.2 to 1.3 L*). bed-1's lit scarp is a thin light line.
9. **Not seen in light or material.** The sheet is grey Lambert with no cast shadows and no hue, and there is no Blender render. Six patches is the plan's count, and repetition across stones is untested until stones are laid.
10. **Sheet size.** `patches-ab.png` is 2.3 MB in plain git: the A/B needs its 1 m views at full size beside 05.

## What a reviewer should judge

The reviewer should judge these from `patches-ab.png`, `patches-tiling.png`, `patch-<name>.png` (rebuild with `blender/tools/patch_sheet.py`), `patches-distances.png` and `patches-eighth.png`:
1. **Traces.** In the tiling, do the ledges read as lamination that wanders, or as drawn waves and ropes (faults 2 and 3)?
2. **Spacing.** Does any common rhythm show across the four split faces, or within one in a 2 × 2 (fault 4)?
3. **Facets.** Are the crescent rows gone, and do the larger triangles read as low-poly (fault 5)?
4. **Distances.** At 5 m beside 10, is any mark floating to the eye, whatever the count says? At 12 m, is a split face with one line or none acceptable (fault 7)?
5. **The spread limit.** A or B beside 05 and 10: is the recommendation above right, and should B wait for a stone?
6. **Bed faces.** Do bed-0 (shadowed scarp) and bed-1 (lit scarp) read as cleavage planes, or as plaster (fault 8)?
7. **Next step.** Should the second half of R2a start on stones with these patches, or should one more round first make the traces less regular?

## The coordinator's read, 22 October, 22:10

Not passed; paused here for the week's usage. On the tiling sheet the split faces read as ruled paper: each ledge is a straight, level line at one depth, and the four split patches put them at near-even spacing. Real lamination traces wander. The next round keeps every ledge running edge to edge, with nothing ending mid-face, and changes three things:
- each ledge follows a gently curving trace, a few degrees off the patch's axis;
- its depth swells and thins along its length, staying above the floor;
- the spacing differs between patches.

It also breaks the crescent rows (faults 2 and 4), and gives bed-1 its scarp or retires it. The per-patch sheets (`patch-*.png`, 2 MB each) are rebuilt by `blender/tools/patch_sheet.py` and kept out of git.

### Answers, version 3

1. **A gently curving trace, a few degrees off axis, never crossing, edge to edge.**
   - Done by the numbers. Each boundary has its own trace (one to three whole cycles a patch, with its own phases), 4 to 7.5° at its steepest. Measured, the traces stray 11 to 25 mm from straight (the second version: 5 to 10). Their angle over 33 mm stays within ±9.5° (p2 to p98), and is 10.9° at most.
   - Boundaries are never closer than 45 mm, and ledges are 123 to 775 mm apart. Every ledge is a through line where it is a line, and none floats.
   - What still fails: the curves are too smooth and regular, and read as drawn (faults 2 and 3).
2. **Depth swells and thins above a floor, with no floating pieces at 1, 5 and 12 m.**
   - Done: 0 floating on all six at all three distances. Ledges swell 1.3 to 2.2 times along their run. Major ledges never fall under 3.3 mm measured (4.0 drawn) and minor ones never under 1.2 (1.5 drawn).
   - The swell ratio is no larger than the second version's. The change is the floor, and one deep ledge a face beside shallow ones.
3. **Spacing differs between patches.**
   - Partly done. The faces have 2, 3, 1 and 2 ledges and 3 to 5 bands, and the gaps within a face differ at least 2.7 times. No face puts a ledge within 25 mm of another face's (the second version had one pair 4 mm apart).
   - Across the set the gaps vary no more than before (CV 0.57 against 0.58), and two faces read as close pairs (fault 4).
4. **Break the crescent rows; answer split-1's spread.**
   - The lattice is gone: there are scattered corners and a Delaunay triangulation, with no bend, so no crescents and no rows that I can see. The local repeat falls 40 to 50% on the three faces where rows were seen, but rises on split-0, and no measure across the torus separates the versions (fault 5).
   - split-1 is 2.53 → 2.06 L* at 5 m: 5 bands, one major ledge of three, and facets at 70%. That is still just over 2.
   - The A/B on the limit is above.
5. **bed-1: a scarp, or retire it.**
   - Given a scarp, facing the light, so the two bed faces differ: bed-0 has a shadowed edge and bed-1 a lit one. bed-1's scarp is a through line at 5 m, where the face holds 1.13 L*, and fades by 12 m.
   - Six patches kept. Nothing in the numbers argues for fewer, and repetition across stones is judged only once stones are laid.

## The coordinator's read, 23 October, 00:20

**Not passed as a finished face, and a fourth round on the flat sheet would not finish it. The patches go to R2a's stones as they are.**

What the eye sees, on `patches-tiling.png` and `patches-ab.png`:
- The ledges no longer read as ruled lines.
- But each ledge reads as a soft cord: a lit line over a dark one, of even width, on a smooth wave.
- Between the ledges the split faces read as grey plaster.
- Beside 05 and 10, A (2 L*) and B (facets ×2, about 3 L*) are both far from the stone, and B is hardly different from A.

**Why the sheet cannot settle it:**
- **R0b** (`../r0b/result.md`): today's rock colour and grain relief make none of the gully's lines and specks (+1% and −2%). The faults SN7's face limit guards against come from moss and the mesh's outlines.
- **This A/B:** the references' marks are the block's own form (planes stepped at centimetres, cracks across a whole stone, chipped corners) and lichen. A patch of 2 to 5 mm cannot carry them, so in SN4 they belong to the stone's mesh (at most three planar facets, stepped at least 15 mm), and in 2b's facts to the stone's value.
- The patch is judged on a stone or nowhere.

**What R2a's stones test, one change at a time against the patches as built,** on the wall stone at L0, in grey and then in the target's light, at 1 and 5 m with the footprint fade on:
1. **facets ×2** on the split faces, about 3 L* at 5 m, with every line check at zero (this round's B);
2. **minor ledges off,** leaving the lamina steps to the mesh: does the cord go, and does the face hold?

The bed faces stay at about 2 L* (the walking surface is the calmest part).
SN7's number for the split face is then set from that A/B, with its evidence, and recorded in the design.

**Open, carried to the stones:**
- the cord-like ledges and their smooth traces;
- split-1 at 2.06 L*;
- the crescent rows' fix resting on the eye;
- repetition across stones.
