# 109: the sea house (c04), from its record, beside ref 01 and 107

- Holds: it reads as a Stavanger sea house, built 1850 by a herring salter, 2.5 storeys, its gable to the quay. The doors are stacked up the middle: a pair of board leaves at the ground, a hatch on the floor above, and one in the ark. The ark is a wedge: its front leans out from a foot to the plate, its gable is plumb, and its roof is the main roof's upper courses carried forward. The cladding is lapped, as in ref 01. The windows are few and small, set out at the sides, with white casings. The plinth is low dry stone, and the roof is pantile. It is built from a type file (`packs/stavanger-1989/house/seahouse.json`) over the classical era and the shared versions. Nothing is tuned for this house.
- The paint is the record's 1960 ox-red with white linseed trims, the pack's rule for a sea house. Two fixes made that true (below). The clay twin carries the paint's dark value, so the house is judged in grey as it is in colour.
- Bad: the coat looks fresh. The pack's repaint cycle runs to 1989 (a kept house, wealth 500, every 11.5 years), so its last coat is 1988. The pack says the engine decides care from 1959 (`peopleStart`), and the record holds no repaint after 1960. Capping the cycle at 1959 would also move 107's last coat from 1977 to 1950, so it is left as it was and goes to the coordinator as a facts question.
- Bad: the page is 76 px/m, against 107's 126 and 108's 90. One 2048 page covers 714 m² of charts. A bigger house's page is a format question for the city.
- Bad: ox-red at C* 34 runs hot orange on the front in low sun. That goes to the street's light step.
- Polish list: a hoist beam or axle under the ark. The leaves' strap hinges are near-only, which is right at the street stop, but they are small at eye level.
- Fixed on the way, for every house:
  - The city plinth named its material `fieldstone`, which has no row in the paint, so 107's city level stopped Unity. It is now `stone`, as at near and street.
  - A `repainted` event's colour is read from `params.wall`, as the records write it. Before, paint.py read `params.paint`, which no record has.
  - A wall's value is now its paint's: the clay's cladding value scaled by the paint's L* against the white it was set for (`paint.json` `clayPaint`). White houses are unchanged.
  - The near and street budgets scale with the house's surface (its charts on the page) against 107's 260 m² (`street.json` `budgetSurfaceM2`), so it is the same triangles a square metre. The city budget stays as it is.
- 107 and 108 build as committed. The one exception is 107's city plinth row (705 triangles, unchanged).

`c04-sheet.jpg`, top row: ref 01, the ark in grey, then the street stop overcast in clay and in colour. Bottom row: 107 (the floor) at the street stop overcast, then 109 at the street stop in low sun, at eye level in low sun, and from 12 m in low sun. Rendered with `render.sh 109 c04 eye,gable,street,raised P,Pc overcast,lowsun`.

Cost (`c06-timing.md`, `STREET_TIMING=50 render.sh 109 c06 street Pc overcast`):
- Triangles: near 53,230 (budget 68,664 at 714 m²), street 11,784 (21,972), city 748 (800).
- A row of 50: 3.9, 4.1 and 4.7 ms (street, raised, along), against 108's 3.8, 4.2 and 4.8 ms timed in the same minute.
- The page: 21.3 MB on the GPU at full, BC7.
