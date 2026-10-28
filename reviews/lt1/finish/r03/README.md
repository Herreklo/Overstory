# Finish test, round 3

House 107's corner in 1989, A (procedural, our own) only, beside photos 09 and 01. B and C are dropped: they had come to look the same as A, and the scans brought only wallpaper and repeats. The piece covers about 3 m of street wall and 1.5 m of gable return, in clay: value grey at each material's lightness, real gloss and no hue.

**Sheet layout:**
- Top row: overcast. Bottom row: low sun, raking the street wall from its east end at 18° elevation.
- Columns: A at 1:1 from the 2560×1440 renders, then photo 09 (and photo 01 below it), scaled to about the same metres per pixel.

**Views:**
- `eye.jpg`: 1.6 m high, about 3 m away.
- `street.png`: the street stop, 20 m.
- `raised.png`: 12 m up.
- `high.png`: high.

All four views were rendered with the final code.

**Build:** run/build.sh, then run/render.sh r03 eye,street,raised,high A under the Unity lock, then run/sheets.sh r03 A.

**Triangles:** 2,731 near (budget 3,000) and 793 street (budget 800).

**Verdict, bad first:**
1. **It does not hold yet.**
   - **The sheet's stains are too light.** They now have 09's structure: pale upper panels, a band held above the lower batten, a damp low panel, and wicking under the head. But the band is lighter than 09's: middle p5 156 against 103, lower p5 119 against 68.
     - Darker stains (stainL 55) were tried. They gave flat grey cut-outs with crisp edges, which looked worse, so the change was reverted. What is missing is how a stain grades and mottles within the band, not how deep it goes.
   - **The runs under the lower batten are too even:** three or four equal vertical stripes in the bottom panel.
   - **The board value now sits at about 2 L\*, as asked.** But a few short boards between butts read as lighter patches at eye level and at 12 m, which looks like replaced boards: a history claim with no fact behind it. A value per course would be calmer.
   - **The settle and the eave sag fan out.** The settle drops the corner 40 mm, true at push 1: a 28 mm tilt over 3 m plus a 12 mm bend within 0.8 m of the corner. The courses near the foot and the sill tilt toward the corner.
     - The eave also carries the recipe's sag between the gables (80–120 mm, `house-asset-craft.md`; 99.8 mm at 1989 over the 7 m frame). Three metres from the corner the eave is 97 mm down against the corner's 40 mm, so it falls 57 mm *away* from the corner.
     - Mid-height is about flat. At the street stop that is about 6 px away at the eave and 4 px toward the corner at the foot.
     - It does not bow, but it adds to the perspective's convergence. Both bends are kept true, so the eave does not tilt toward the corner as asked.
   - **Raised and high show the test piece's cut:** the gable rises bare above the two tile courses.
2. **What works:**
   - **The laps at the street stop match 09:** 5.7 mm integrated against 09's 5.8 mm, by the same tool.
   - The wall at eye level holds as in round 2, with crisp white paint, loss in short strips and calm stretches.
   - **The roof has its true form:**
     - 220 mm cover;
     - a 50 mm roll in a shallow S-wave;
     - laid course by course, and matte when dry.

     It reads as pantiles at the street stop and at 12 m, with no sawtooth.
   - The plinth has lost its speckle.
   - Low sun throws crisp batten, sill, cap and lap shadows, and the trim arrises catch light.
   - **A works without outside assets:** the finishing needs no scans.

**Measured:**
- **Lap at the street stop, integrated across the line** (`lapint`, at 10 mm/px): 5.7 mm median. Round 2 measured 4.8 mm by the same tool; 09 measures 5.8 mm. 09's target was 4.5–7 mm.
- **Board-to-board value at eye level,** mean neighbour |dL\*| in two column bands: 1.99 and 1.86, at most 5.5. Round 2 was 0.59; 09 is 0.37–1.7 and 01 is 1.35–3.34.
- **Sheet, p5/p50 at the street stop:**
  - middle 156/216 (round 2: 179/214; 09: 103/204);
  - lower 119/186 (round 2: 128/174; 09: 68/190).

**Where the brief met the data:**
- **The pantile** is cited in `classical.json` (`pantile`): Højslev normalformat, cover 220 mm; Wienerberger and Sandtoft give 45–69 mm for the roll. The pack's `clay-pantile.json` still says 240/58, so whoever owns the pack should check it.
- The settle is the bend's own shape in `classical.json` (`settleReachMm`, `settleBendMm`, `settleBendShare`). `push.settle` is back to 1.
- The eave sag is kept from the recipe, which makes the fan described above.
- Board value is `boardValueL.cladding` 13.5, up from 4.
- The lap core and reach are now 6 and 26 mm, up from 5 and 20.
- A faint grime line sits on each lap's top edge, where dust settles (`dirt.butts`).
- **The sheet's stains each have a cause:**
  - wicking under the head;
  - water held above each batten, scaled by the sheet that drains to it, so the lower batten holds most;
  - runs from the batten edges;
  - nails round each sheet's edges, with a rust run.
- Each batten is now centred on its line at mid-span. This fixed nails sitting up to 24 mm off it.
