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
