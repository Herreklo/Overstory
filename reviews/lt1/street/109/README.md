# 109: the sea house (c04), from its record, beside ref 01 and 107

- Holds: it reads as a Stavanger sea house, built 1850 by a herring salter, 2.5 storeys, its gable to the quay. The doors are stacked up the middle: a pair of board leaves at the ground, a hatch on the floor above, and one in the ark. The ark is a wedge: its front leans out from a foot to the plate, its gable is plumb, and its roof is the main roof's upper courses carried forward. The cladding is lapped, as in ref 01. The windows are few and small, set out at the sides, with white casings. The plinth is low dry stone, and the roof is pantile. It is built from a type file (`packs/stavanger-1989/house/seahouse.json`) over the classical era and the shared versions. Nothing is tuned for this house.
- The paint is the record's 1960 ox-red with white linseed trims, the pack's rule for a sea house. Two fixes made that true (below). The clay twin carries the paint's dark value, so the house is judged in grey as it is in colour.
- The coat is the record's (`c08-care.jpg`: before at left, after at right of each pair, overcast then low sun; `c08-care-eye.jpg`: eye level before, after overcast, after low sun). Before, the pack's cycle ran to 1989 and gave a 1988 coat. Now paint.py reads only the record. Its coats after 1959 are derived by `care.py` from the keeper and written into the fixture as `repainted` events with provenance `derived`. 109 is not lived in (a warehouse), so its turn is the pack's 11.5 years by its wealth (500) times 1.5, ±20% seeded: one derived coat, in 1979, after the recorded 1960 ox-red. At ten years old the red chalks darker and browner, and the paint peels to grey wood under the windows. It no longer reads as a new barn. The peel patches step a little regularly; that goes to the light and colour step.
- Bad: the page is 76 px/m, against 107's 126 and 108's 90. One 2048 page covers 714 m² of charts. A bigger house's page is a format question for the city.
- Bad: ox-red at C* 34 runs hot orange on the front in low sun. That goes to the street's light step.
- Polish list: a hoist beam or axle under the ark. The leaves' strap hinges are near-only, which is right at the street stop, but they are small at eye level.
- Fixed on the way, for every house:
  - The city plinth named its material `fieldstone`, which has no row in the paint, so 107's city level stopped Unity. It is now `stone`, as at near and street.
  - A `repainted` event's colour is read from `params.wall`, as the records write it. Before, paint.py read `params.paint`, which no record has.
  - A wall's value is now its paint's: the clay's cladding value scaled by the paint's L* against the white it was set for (`paint.json` `clayPaint`). White houses are unchanged.
  - The near and street budgets scale with the house's surface (its charts on the page) against 107's 260 m² (`street.json` `budgetSurfaceM2`), so it is the same triangles a square metre. The city budget stays as it is.
- 108 builds as committed. 107 differs only in its city plinth row (705 triangles, unchanged) and the street cuts below.

`c04-sheet.jpg` (built before the street cuts, which do not show), top row: ref 01, the ark in grey, then the street stop overcast in clay and in colour. Bottom row: 107 (the floor) at the street stop overcast, then 109 at the street stop in low sun, at eye level in low sun, and from 12 m in low sun. Rendered with `render.sh 109 c04 eye,gable,street,raised P,Pc overcast,lowsun`.

Street level (`s01-eave-ab.jpg`, the street stop's eave at 2.2x, low sun above and overcast below):
- At left is 109 as built at e396d6c, 11,784 triangles. In the middle the course planes run on 2 m frame segments and the eave course has no under faces (`street.json` `frameSegmentM`, `eaveUnder`), 9,452: it cannot be told from the left. At right the eave's wave is 3 samples a cover and the frame 3 m, 8,588: the pantile rolls are lost from the eave's line against the sky, and the scallops coarsen. So the middle is kept.
- 107 with the middle's cuts goes from 6,287 to 5,459 triangles and cannot be told apart at its eave in either light.
- On one side of a street, the street level per metre of frontage and per m² of surface is 780 and 21.1 for 107, 974 and 15.3 for 108, and 1,050 and 13.2 for 109. A flat 8k would be 889 a metre for 109, and it reads coarser.

Cost (`c07-timing.md`, `STREET_TIMING=50 render.sh 109 c07 street Pc overcast`):
- Triangles: near 53,230 (budget 68,664 at 714 m², with a ceiling of 80,000 for any house), street 9,452 (budget 9,900: 1,100 a metre of its 9 m frontage, never below 8,000, `street.json` `perFrontageM`), city 748 (800).
- The street level by frontage is 1.1 million triangles a km of one side of a street, if every plot were at the rule's rate. Built, 107 is at 780 a metre, 108 at 974 and 109 at 1,050.
- A row of 50: 3.7, 3.9 and 4.4 ms (street, raised, along).
- The worst near view, `near3`, has three houses drawn near at once, at eye level 5 m off the middle one, at a 75° field of view: 4.6 ms with 169,142 triangles in view. 107's is 4.2 ms with 78,973.
- The page: 21.3 MB on the GPU at full, BC7.
