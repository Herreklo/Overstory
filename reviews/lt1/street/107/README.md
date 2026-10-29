# 107 alone (s01): the whole house from its record, beside the p3 corner

- Bad: at the street stop it is a plain white box on empty ground, not yet stunning. The wear doesn't carry: p3's runs read under every window, while 107's are faint and its peel sits at the foot. The roof's patches mottle, and the chimney is a pale stub.
- Bad: the boarded openings are flat planes behind blue-grey battens that read as painted, with no sash, glass or leaf behind them (leaves are step 3). The low sun grazes the front, so the street stop in that light is flat.
- Holds: it reads as a 1½-storey house of 1828 with a 1950 lean-to, not a kiosk. Trims, steps, plinth corner, verges and roof are all whole, nothing is tuned per house, and the counts are near 24,318 / 25k and street 6,155 / 8k triangles.

`sheet.jpg`: top row is the p3 floor, then the street stop (20 m) in clay and colour, overcast. Bottom row is p3 in colour, then eye level in clay overcast and in colour under low sun. The stills come from Unity, from `blender/parts/street/run/render.sh 107 s01` at 9496a88.

## s03: p3's rules ported, roof seam A/B (29 October)

- Bad: the roof seam still shows at the street stop and from 12 m. It is not geometry. The baked page differs between courses 1–2 (baked from the near tiles) and 3 up (carried onto the planes from the bake level): occlusion 0.62 against 0.80, cavity 0.34 against 0.43, with identical normals. The planes' microshadow (`_OS_PLANE`, in `s03-seam.jpg`: 0 left, 1 right) adds dark dashes, not rolls, so it stays at 0.
- Bad: at p3's own cameras (`s03-floor.jpg`: p3 left, 107 right) the marks under 107's first window have p3's character (the tongue, runs, peel at the foot) but read weaker. The page is 90 px/m against p3's 128, and the camera frames the corner wider than p3's, so the corner's origin differs from p3's.
- Holds: p3 is unchanged by the shader change. All 16 of p3-final3's stills re-rendered pixel-identical (maximum difference 0). The paint is now p3's own runoff, tongue and peel, with no recalibration: the front is p3's and the other walls only lower.

## s06: roof bake unified, wear from severity, boarding from ref 09, 128 px/m on the street walls (29 October)

- Holds: the roof seam is gone. Every course's occlusion and cavity are now carried from the tiles' top surface, so the near tiles' overlapping charts no longer darken them. The eave course's median occlusion was 0.45 and is now 0.88, and courses 1–2 match 3 and up (bake.py, a `bake_target` plane per near course).
- Holds: `_FlatUp` 0 on the course planes (`s06-roof-ab.jpg`: s03, then 3, 1 and 0). In low sun the rolls read as columns down the slope and the dashes go; at 3 and 1 the slope reads as flat courses with dashes. Overcast, the courses still lead. The square checker is gone. The roof ages in broad shapes from its facts: the eave course darkest, moss down the pans from the ridge, the north slope darker. There are no replaced tiles, because 107 has no roof repair.
- Holds: 90 against 128 px/m at the street stop (`s06-density.jpg`) look the same, so the read there comes from broad shapes, not resolution. The street walls take 128 px/m and every other face 79, all on the same 2048 page.
- Better, not there yet: neglect now comes from severity. It is the wall's wear plus half the neglect's amount (front 0.92, west gable 0.72, lee walls 0.14). Broad grey tongues hang under each sill, the foot is grey and the upper wall under the eave greys. At the street stop the tongues and the foot read, but the band under the eave is still subtle, and it is a white house before a neglected one.
- Better, not there yet: the boarding follows ref 09. The ply is pale (L* 63), with water stains hanging from the head; the battens are raw, pale wood (L* 75). At the street stop the sheets sit close to the wall's value, so the openings read less than s03's dark sheets did.

`s06-sheet.jpg`: on the left is s03, on the right s06. The rows are the street stop overcast in clay, the street stop in low sun in colour, 12 m overcast in clay, and 12 m in low sun in colour. Rendered with `render.sh 107 s06 eye,street,raised P,Pc overcast,lowsun`; the 90 px/m build is s04f0.

Cost of one house, from `cache/street/renders/s05/timing.md` (`STREET_TIMING=50 render.sh 107 s05 ...`):
- Triangles: near 24,474 (budget 25k), street 6,251 (budget 8k). The city level is not built yet (budget 500–800).
- Draw calls and materials: 11 materials per level, so 11 draws a level plus its shadow casters. That makes 22 materials a house per way, since each house has its own page.
- Texture memory: four 2048 maps and one 1024 stroke map, uncompressed with mips: about 91 MB on the GPU (the editor counts 171 MB with the CPU copy). Meshes for both levels: 4.9 MB (editor count).
- A street of 50 (one side at 7 m plots): textures 4.5 GB uncompressed, which breaks the budget. BC7 would bring it to about 1.2 GB, and mip streaming to about 0.2 GB with five houses near; that A/B is not run yet. Triangles at street level are 313k if all 50 are in view.
- A kilometre of such houses: 143 a side at 7 m plots, 286 for both sides. Textures 26 GB uncompressed, which is impossible; about 6.8 GB with BC7 and no streaming. With streaming and a city level, what is resident follows what is near.
- Frame time, offscreen in the editor, batch mode (Apple M4, 2560×1440, MSAA 4x, Pc, low sun, one 4096 cascade, SSAO; not the player's frame, and no sky or post): street stop 3.7 ms, 12 m 4.4 ms, and 10.0 ms looking down a row of 50 (all at street level, 312k triangles, 547 draws).

## s07–s08: BC7 and streaming, ply and roof age, the paint's age; the age sheet (29 October)

- Holds: the page is block-compressed (BC7), now the default. `stilldiff.py` measures the change in L* between s06 and the same build in BC7, pixel by pixel and over 8 px blocks. At the street stop, 12 m, high, back and gable, no block changes by more than 1.4 L*. At eye level 0.05% of blocks change by up to 2.4 L*, at casing corners. In `s07-bc7.jpg` (uncompressed left, BC7 right, eye level at 1.6×) the two can't be told apart. Frame time is the same, back to back: 3.8 ms against 3.9 at the street stop.
- Better, not there yet: the ply is L* 50, with blotches 14 darker and the head's wash 7. In clay overcast at the street stop the sheets are 55 with blotches 42, against a wall of 80 (s06: 66 against 80; s03: 38). In colour under low sun they are 58–72 against 89, and the openings still read lighter than s03's.
- Better: the roof ages in colour as well as value (`roof_marks`). The lower third is greyer and darker, a streak runs down under the chimney, and lichen grows in small pale grey-green rosettes on the top courses and the ridge, thinning toward the eave. At the street stop it reads as an old roof, not new terracotta. The first try's lichen, 0.35 m patches, read as big square blobs and was redrawn.
- Better: the paint's own age. p3 is now 107's front in 1989, at wear 0.93 (`wear.floor`). A wall fails by its wear against that, so a younger coat fails less. Chalk greys every painted wall from wear 0.2 to full at 1.3. 107's front is less crisp cream; in low sun the lit wall is near white, so the chalk shows mostly overcast.
- Age sheet (`age-sheet.jpg`): 107 as of 1985, unboarded (`house.py --year 1985`), its paint 2, 8 and 20 years after a coat (`paint.py --since`), then 107 in 1989. The rows are the street stop in colour under low sun, the same in clay overcast, and 12 m in colour overcast. Two years is crisp. Eight shows the first runs under the sills and a slight grey. Twenty is greyed all over, with tongues and a grey foot, and reads older than 1989's front, which is boarded with its own marks. Wear grows with time from the facts alone.
- Bad: an unboarded window is a blank painted panel, with no sash or glass; those parts are in step 3. The age sheet's windows show it.

`s08-sheet.jpg`: s03, s06 and s08 at the street stop in colour under low sun, the same in clay overcast, and 12 m in colour under low sun.

Cost of one house (`s07-timing.md`, `STREET_TIMING=50 render.sh 107 s07t-c street Pc lowsun`):
- Triangles: near 24,474 (25k), street 6,251 (8k). The city level is not built yet (500–800).
- Draws and materials: 11 a level, so 22 materials a house per way (each house has its own page).
- Textures on the GPU in BC7: 21.3 MB a house at full (uncompressed 74.7 MB), 1.33 MB at mip 2 and down. One stroke texture of 1.3 MB is shared by every house. Meshes: 4.9 MB for both levels, as the editor counts them.
- A street of 50: 1.07 GB all at full. With mip streaming, counted rather than measured, each house holds the mip its nearest point needs at 128 px/m at 2560×1440, at most 2 mips dropped: 140–148 MB, with 3–4 houses at full and the rest at mip 2. Streaming is off in the project's quality settings (`streamingMipmapsActive: 0`); the import now marks the page as streamable.
- A kilometre, both sides at 7 m plots (286 houses): 6.1 GB at full, about 0.44 GB streamed, of which 0.38 GB is the floor of mip 2. Allowing 4 mips dropped would bring the floor to about 0.03 GB.
- Frame time, offscreen in the editor, batch mode (not the player's frame): street stop 3.8 ms, 12 m 4.4, and down a row of 50 houses at street level 10.3 (312k triangles, 547 draws). The row needs the city level.

## s09: the ply at 43 (29 October)

- Holds: the ply is L* 43, with blotches 11 darker (to 32). In `s09-ply-ab.jpg` the columns are s03, the ply at 50 and at 43, at the street stop in colour under low sun (top) and overcast (bottom). At 43 each opening reads as a mid-grey board framed by the white casings in both lights, with its blotches and battens, and not as dark glass. In clay overcast the sheets are 49, with blotches 38, against a wall of 75. In colour under low sun they are 66 against 88.
- Not done: mip streaming in the project's quality settings and full mips in batch captures. Changing the shared Unity settings was refused by the session's permission check, so the page is marked streamable but streaming is still off.
