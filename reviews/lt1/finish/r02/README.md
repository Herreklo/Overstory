# Finish test, round 2

House 107's corner in 1989, now with C taken forward and A and B kept as references. It covers about 3 m of street wall and 1.5 m of gable return, in clay: value grey at each material's lightness, real gloss and no hue.

**Sheet layout:**
- Top row: overcast. Bottom row: low sun, which now rakes the street wall from its east end at 18° elevation, so the gable is in shade.
- Columns: A procedural, B scanned, C both, at 1:1 from the 2560×1440 renders.
- Last column: photo 09 and photo 01, scaled to about the same metres per pixel.

**Views:**
- `eye.jpg`: 1.6 m high, about 3 m away.
- `street.png`: the street stop, 20 m.
- `raised.png`: 12 m up.
- `high.png`: high.

`raised.png` and `high.png` were rendered before the last fix, the street level's lap filtering, so their laps are weaker than the code now draws.

**Build:** run/build.sh (corner.py, then bake.py, which was missing from round 1's script and left the AO stale), marks.py, then run/render.sh under the Unity lock, then run/sheets.sh.

**Triangles:** 2,521 near (budget 3,000) and 665 street (budget 800).

**Verdict, bad first:**
1. **C does not hold yet.**
   - At the street stop the laps are still lighter than 09's: about 0.75 of the face against 09's 0.6–0.7.
   - The settle, pushed ×2 to show at the street stop, bows the lower courses at eye level almost like a lens.
   - The roof reads as a toy sawtooth. It is not under test, but it is in every frame.
   - A and C are now nearly the same, so the scans add little. B's sheet is still wallpaper.
2. **The boarding is close but not there.**
   - Sheet behind raw battens, with rusted nails and mottled wicking stains.
   - Its lower panel matches 09's dark tail. The middle panel lacks some of 09's stains.
   - The plinth reads as dressed blocks, but keeps some scan speckle.
3. **What works:**
   - The wall is crisp white, with paint loss only in short strips at the butts, the foot and under the sill, and calm stretches between them.
   - The lap band at eye level matches 09.
   - The low sun throws crisp batten, sill, cap and lap shadows.
   - The drip cap is plain.
   - The trim arrises catch light.
   - The bend shows at the street stop.

**Measured:**
- **Lap under overcast at eye level:** 0.56–0.6 of the face, 11 mm at half depth. 09: 0.54–0.67, about 13 mm.
- **Lap at the street stop, integrated across the line:** about 4 mm of full darkness against 09's 4.5–7 mm. Before the fix it was 2.8 mm. The fix: the street page holds a signed distance to the nearest butt, read at full size and box-filtered over the pixel, so a mip no longer averages the lap away.
- **Sheet, p5/p50 at the street stop:** middle 179/214 (09: 103/204); lower 128/174 (09: 68/190).
- **Bend:** the top lap line falls 2.9 px from its chord at the street stop.

**Where the brief met the data:**
- The boarding is sheet behind battens, cited to photo 09 in `classical.json`. The pack's timber data was removed in the clean-up.
- There is no gutter or downpipe, because the classical working has none. The eave's drip line falls on the wall and the foot.
- The settle is pushed ×2 by the style dial (`push.settle`), from 40 to 80 mm. The true 40 mm bends a 3 m wall by under 2 px at the street stop.
- The course width stays the pack's 15 cm. Photo 09 is a later house with 10–11 cm courses.
- Zinc stays in the material lists, but nothing uses it.
- C's sheet takes the scan wallpaper as its tileable, under the page's marks.

**Stand-ins in B:** a wallpaper scan for the sheet.
