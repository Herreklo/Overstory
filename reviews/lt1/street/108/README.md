# 108: the chalet (c02), from its record, beside ref 10 and 107

- Holds: it reads as ref 10's house, a sveitser chalet of 1901 with its gable to the street. The plinth is high and rendered, and the belt carries dentils. The loft row is four windows with one more in the peak. The verge is deep, with a moulded barge and purlin ends. The surrounds are bracketed, the side door has steps, and the roof is slate. It is built from a chalet era file and the shared versions; no part is tuned for this house. The windows are 1901's, from the 1985 restoration, and the paint is the 1985 white, so the wear is slight. That is what the facts say.
- Bad: overcast is flat grey. The deep verge throws a hard-edged band down the gable, because the overcast light is a 65° key light with shadow 0.7 (`LT1Street.cs`, Lighting overcast). The barge's diagonal shadow edge shows a sawtooth: the soft-shadow filter is on Low. The geometry is clean (grey `rake` view). Both go to the street's light step.
- Bad: the plinth is plain render with a wet foot. Ref 10 has three cellar windows in it. Near has 168 triangles left, so the cellar windows are on the polish list with the beaded cladding.
- Fixed on the way, for every house:
  - The verge's barge was sheared. A sign error left it about 15 cm deep vertically; it now has its true width, and an end board closes the eave box under its foot.
  - The house's shadows now cast two-sided. One-sided, the sun's normal bias opened the joints between faces turned different ways, and lit lines crossed the shadow on the ground. 107 showed them too.
  - Each roof slope gets its sarking, the boards seen from under the verge.
  - The bake no longer assumes pantiles.
  - Slate has its own paint values, at L* 33 with a cool hue. A rendered plinth takes the plinth's wet margin and junctions, without brush strokes.

`c02-sheet.jpg`, top row: ref 10, then grey at ref 10's stand, then the street stop overcast in clay and in colour. Bottom row: 107 (the floor) at the street stop overcast, then 108 at the street stop in low sun, from 12 m in low sun, and at eye level overcast. Rendered with `render.sh 108 c02 eye,gable,street,raised P,Pc overcast,lowsun`; the raised still is from c02t.

Cost (`c03-timing.md`, `STREET_TIMING=50 render.sh 108 c03 street Pc overcast`):
- Triangles: near 24,832 (25k), street 7,792 (8k), city 778 (800).
- A row of 50: 3.8, 4.0 and 4.7 ms (street, raised, along), against 107's 3.6, 4.1 and 4.8 ms.
- The page: 21.3 MB on the GPU at full, BC7.
- 107 after the shared changes: near 24,590, street 6,287, city 705.
