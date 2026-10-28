# Finish test, round 1

House 107's corner in 1989: about 3 m of street wall and 1.5 m of gable return. It is finished three ways in clay, with value grey at each material's lightness, real gloss and no hue.

**Sheet layout:**
- Top row: overcast. Bottom row: low sun.
- Columns: A procedural, B scanned, C both, at 1:1 from the 2560×1440 renders.
- Last column: photo 09 as it is, and photo 01 (already black and white), scaled to about the same metres per pixel.

**Views:**
- `eye.jpg`: 1.6 m high, about 3 m away.
- `street.png`: the street stop, 20 m.
- `raised.png`: 12 m up.
- `high.png`: high.

**Build:** Blender `blender/parts/finish/` (run/build.sh, then run/render.sh under the Unity lock, then run/sheets.sh). Shader `Overstory/Finish` and the scene builder in `unity/Assets/Experiments/LT1/Finish/`.

**Triangles:** 2,684 near (budget 3,000), 764 street (budget 800). Checked by corner.py, which writes nothing when a level is over budget.

**Verdict, bad first:**
1. **None holds.**
   - At eye level the laps read as thin pencil lines, not photo 09's shadowed overlap, so the wall reads as flat panels.
   - A's paint loss is sprinkled evenly in small flat-grey spots, which reads as noise.
   - B's scan loss smears in horizontal rows that repeat every metre, which reads as pasted.
   - The under-sill streaks fall like a regular curtain.
2. **The boarding is uneven.**
   - Its blotched water stains read in A and C, but too pale and even.
   - B's sheet is flat wallpaper.
   - In low sun the gable is flat white (the sun is head-on), and the downpipe's shadow is soft.
3. **What works:**
   - Values match photo 09: paint 226 against 232, sheet 201 against 201.
   - Trim and sill arrises catch light.
   - The dirty foot and the darker eave read at the street stop.
   - Both levels are within budget.
   - C is closest.

**Differences that are form, not finish:**
- Photo 09's courses are about 10–11 cm; ours are the pack's 15 cm.
- Photo 09's surround is moulded; 107's 1965 husmor surround is plain.

**Where the brief met the data:**
- The classical working has no gutter.
- The husmor trims are marked "lost".
- The pack's boarding is formwork planks, but the sheet follows photo 09.

**B's stand-ins:** a wallpaper scan for the sheet, and tinted rust for the zinc.
