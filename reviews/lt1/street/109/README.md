# 109: the sea house (1850), beside ref 01 and 107

- Bad: the ox-red runs hot orange in low sun, and the peel patches under the windows step too regularly. Both go to the light step.
- Holds: it reads as a Stavanger sea house, gable to the quay. The loading doors are stacked up the middle: board leaves, a hatch to each floor, one in the ark. The ark is a wedge: its front leans out to the plate, its gable is plumb, and its roof carries the main roof's upper courses forward. The cladding is lapped as in ref 01, the windows are few and small with white casings, the plinth is low dry stone, and the roof is pantile. It is built from a type file (`packs/stavanger-1989/house/seahouse.json`), and nothing is tuned for it. There is no hoist arm: the ark is the hoist's housing, and the loft has been a rehearsal room since 1987.
- Holds: its coat is the record's. A warehouse's keeper does not live there, so its turn is 1.5 times the pack's, and after the recorded 1960 ox-red the rule derives one coat, in 1979. At ten years old the red chalks darker and peels to grey wood, so it no longer reads as a new barn (`c08-care.jpg`, `c08-care-eye.jpg`).
- Fixed: the lighter band down the gable (Øystein, on c08). The wall's fade from top to foot took its top per column, and the cladding under the ark stops at 6.0 m. It now runs to the wall's hull, for every house; 107 and 108 change by 1/255 at most (`c09-band.jpg` beside 107, `c09-band-close.jpg`).
- The page is 4096 at 128 px/m. Pages sized in 256 px steps came out uncompressed (RGBA32, 225 MB a house), so the sizes are powers of two. Finer steps would need several pages and the shared Finish shader's stroke scale as a vector (`c10-page.jpg`).

Stills: `109-*.png`, from `render.sh 109 t3 street,eye P,Pc overcast,lowsun`.

Cost (`c10-timing.md`):
- Triangles: near 53,230 (68,664 by its 711 m², ceiling 80,000), street 9,452 (9,900: 1,100 a metre of frontage, 1.1 million a km of one side), city 748.
- A row of 50: 4.5, 4.6 and 5.2 ms (street, raised, along); near3, three houses near, 5.5 ms. On the 2048 page it was 3.7 and 4.6.
- Page: 85.3 MB at full, 0.33 MB from mip 4 down. A row of 50 streams 294 MB at the street stop. The near three or four houses hold most of that, at most 340 MB, and the far houses add about 37 MB a km.

Polish: the axle under the ark, and the leaves' strap hinges at eye level.

History: git log of this folder.
