# The row: 107, 108 and 109 together, the sky's flash only at the head (r06)

- Bad: 108's own near view, 4.4 m off, changes on the main floor too. Up close the eye looks up into the sky, so the band takes the main floor just as it takes the upper floor from the street:
  - its lower sashes go from L34–37 to 13–18, and the top lights stay grey;
  - the room's furniture, which showed against the grey, is lost in the dark.

  The main floor is unchanged in every view of the row, in both lights, and at 108's own street stop.
- Bad: at the street stop the band reads as grey, not as a flash.
  - The top 30% of each upper opening has a median of 33–40, and a p90 of 62–68 taken with the head's wood. That is what the glass's Fresnel gives 42–53° off the face.
  - The cap binds only at a grazing angle, in the row's eye view, where the band is L58–63.
- Bad: at the sheet's scale, 108's upper floor at the street stop is 35–37 (r05 40–45), against the main floor's 25–31. At 10 px a window the casing still blurs in.
- Holds, at the street stop at 1:1 in overcast (`r06-close-glass.jpg`):
  - 108's upper floor measured whole is 24.2–29.5 (r05 36.5–40.7);
  - the lower 70% of each opening is 14.7–18, beside the main floor's 17–20; the top lights are 33–40;
  - so the upper windows read as dark eyes with the sky only in their top lights, not as blank paper;
  - the gable's top window is 32.8 (r05 38.2).
- Holds: the main floor, the casing, the sheers and the threshold are the same as r05 in every row view and both lights, every box to 0.1 L. The 12 m and high views do not change at all: their panes mirror the water and the far shore.
- Holds, elsewhere:
  - low sun at the street stop: the upper floor is 24.7–26.5 (r05 28.1–33.0);
  - the row's eye view, at a grazing angle: the upper floor is 47–48 (r05 60–65), its band capped at 58–63, and its lower sashes 40–42, like the main floor's 34–40 beside them;
  - 108 alone at its own street stop: the upper floor is 13–15 whole (r05 33–35).
- Holds: no pop. On 108's walk from its eye view to its street stop (`r06-walk.jpg`), the largest frame step is 1.03× its neighbours'.

How it is made:
- The values are in glass.json `flash`: depth 0.3, rise 0.08, soft 0.04, cap 0.45.
- Where a pane's reflection rises over the far shore's skyline (OS_Glass `Rise`, the same blocks as `Reflected`), the sky shows only in a band down from the opening's head.
  - The band deepens as the reflection climbs over the skyline, to 0.3 of the opening at 0.08 (sin) over it. So it steps with the shore's blocks, and it slides as the eye moves.
  - Its lower edge is soft above that line.
  - Its strength is the glass's own Fresnel, and never more than 0.45 of the light on the face.
- Below the band the pane mirrors the far shore.
- The mark from afar uses the opening's own frame, so it draws the same band.
- The room behind is still lit by the sky it sees, so a main floor that mirrors only the shore is untouched.

Sheets:
- `r06-overcast.jpg` and `r06-lowsun.jpg`: rows eye, street stop, 12 m, high; columns p3 P | r01 P | r05 P | r06 P | r05 Pc | r06 Pc.
- `r06-close-glass.jpg`: r05 | r06 at the street stop at 1:1, both floors, then refs 10 and 04.
- `r06-walk.jpg`: 12 frames of 108's walk; the 5 s clip is `cache/street/renders/r06h/walk-108.mp4`.

These renders carry r03's toe (`packs/stavanger-1989/light/grade.json`). It is still uncommitted and waits for Øystein's yes.

    STREET_ROW="107:cache/street/gen/107h:cache/street/bake/107z4/out-r02 108:cache/street/gen/108f:cache/street/bake/108u/out-r02 109:cache/street/gen/109f:cache/street/bake/109u/out-r02" python3 tools/unity_lock.py run -- bash blender/parts/street/run/render.sh row r06 eye,street,raised,high P,Pc overcast,lowsun
    STREET_WALK=120 STREET_GEN=cache/street/gen/108f STREET_PAINT=cache/street/bake/108u/out-r02 python3 tools/unity_lock.py run -- bash blender/parts/street/run/render.sh 108 r06h eye,street Pc,P overcast

Cost: no new geometry and no new draws, only a few instructions in the glass's fragment.
- Triangles and draws are r05's: 108 24,868/7,828/778, 109 53,248/9,470/748, 107 24,590/5,459/705.
- A row of 50 of 109 runs street 4.5, raised 4.6, along 5.3 and near3 5.5 ms (`cache/street/renders/t08/timing.md`). That is t06's frame, without the mark or the flash, to within 0.3 ms. The machine ran quieter than for t07 and t07c, so the change's cost is below what these runs can tell apart.
- Pages are unchanged.
