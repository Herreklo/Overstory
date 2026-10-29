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

## c03: streaming on; the city level (29 October)

- Holds: mip streaming is on at the PC quality level, which Øystein approved. The budget is 2048 MB with at most 4 mips dropped. A batch capture now forces full mips (`unity/Assets/Code/Editor/BatchFullMips.cs` sets `Texture.streamingTextureForceLoadAll` in batch mode). Before and after, with streaming off and on, p3 (eye, street, raised, high) and 107 (eye, street, raised, high, back, gable) are pixel-identical in both lights and both ways: `stilldiff.py` reads a max of 0.0 L* on every still. Nothing in the current scenes drops a mip.
- Holds: the city level (`house.py` `city()`, `street.json` `levels.city`). It has no geometry of its own:
  - every street piece keeps its faces, but drops the sides and tops narrower than 13 cm, every underside, back and inner face, and every face turned toward its wall;
  - each run of segments is merged into one face, and corners are welded into the merged edges so the frame's bend opens no crack;
  - each roof course is one plane with its foot's step, which draws the course lines;
  - each plinth is one face;
  - a boarded opening's frame stays at its depth behind the sheets; an unboarded one comes flush with the casing.

  Every face sits on its street face's chart, so the page, its bake and its paint are unchanged and nothing new is baked. House 107 is 729 triangles (budget 500–800), and the level is drawn from 60 m. In `c03-city.jpg`, street level and city level side by side:
  - top: 60 m in colour under low sun, and the same in clay overcast;
  - bottom: 120 m in colour under low sun, and 80 m from a roof in clay overcast.

  The boarding, casings, wear, roof course lines and lichen all read the same. Only the eave course's rolled tile edge goes, under a pixel there.
- Learned: the row of 50 costs the same time with the city level as without it. Looking down the row, 42 houses are city and triangles in view drop from 312k to 80.5k, but the frame is 10.4 ms against 10.3. The time isn't in triangles: it is in about 550 draws (11 materials a house), the shading and the shadow pass. The next lever is draws (one material a far house), not geometry.

Cost of one house (`c03-timing.md`, `STREET_TIMING=50 render.sh 107 c03t street P overcast`):
- Triangles: near 24,474 (budget 25k), street 6,251 (8k), city 729 (800).
- Draws and materials: 11 a level. The city level draws with the street level's materials.
- Textures on the GPU in BC7: 21.3 MB a house at full, 0.08 MB at mip 4 and down; one 1.3 MB stroke texture shared. Meshes, all three levels: 5.1 MB, as the editor counts them.
- A street of 50: 1.07 GB all at full; streamed (counted, at most 4 mips dropped) 80–97 MB, with 3–4 houses at full.
- A kilometre, both sides at 7 m plots (286 houses): 6.1 GB at full. Streamed, about 0.1 GB of far houses at mip 4 (0.08 MB each) plus the near ones.
- Frame time, offscreen in the editor, batch mode (Apple M4, 2560×1440, MSAA 4x, one 4096 cascade, SSAO; not the player's frame): street stop 3.7 ms, 12 m 4.2 ms, down the row of 50 10.4 ms.

## k01: the crisp chips back (29 October)

- Holds: bare wood takes 0.67 of the page's value shift, not the corner's 0.3 (`paint.json` `edge.bareShift`, over finish.json's `edge`). The neglect tongues, the foot's dirt and the junctions' darks are a film of water and grime over paint and fibre alike, so the chip darkens as a multiply would: (52 + 16) / (85.3 + 16) of the paint's shift. The long washes keep `bareWash` 0.12, so in a run the fibre stays lighter. Nothing else changed: the pages are byte-identical, and p3 is untouched.
- Why: the peel shapes never changed. From s06 the neglect, and from s08 the chalk, darkened the paint around them while bare wood took only 0.3 of it, so the two met. On the page, the paint just outside a chip and the bare just inside it now differ by a median of 27 L* (5th percentile 5), against 16 (5th percentile −18, the chip lighter); edges within 10 L* drop from 26% to 8%.
- In `k01-chips.jpg` the columns are s03, k00 (HEAD) and k01. The top two rows are p3's camera: clay overcast, then colour under low sun. The bottom two are the street stop. `k01-chips-eye.jpg` is the eye view, k00 against k01. At eye level the chips are hard-edged again on the sill tongues and the foot, grey wet fibre under a grey film. From the street stop they hold as a few clean marks: 0.4% of 8 px blocks move by more than 1 L*, against 2.3–3.5% at eye level. The lower wall stays greyer than s03's, as s06 and s08 made it; only the chips are back.

## c04: one draw a far house (29 October)

- Holds: a city-level house is one mesh and one material. `LT1Street.OneMesh` merges its 11 pieces in Unity, and each vertex names its material's row in `uv2.x`. The one material is the street level's, with the `_OS_ONE` keyword in OS_Finish: each face reads its own material's 24 values (L*, bare, under, stain, smoothness, occlusion, shadow lift, brush, flatten, stain edge, the four tints, the plane's shadow) from a 7 × 11 table of the house's own (`mattab-P/Pc`). With the keyword off the shader is unchanged: p3 renders pixel-identical (eye and street stop, both lights, max 0.0). Against a material a piece (d00 against d01: the street stop, 60 m and the roof view at city level, both lights, both ways), no 8 px block moves by 0.6 L* or more, and the only changes are single pixels along edges. `STREET_CITYONE=0` keeps a material a piece for an A/B.
- Holds: far shadows. A city house already casts only from its city level, which is now one draw. A house too far for its shadow (a ridge's 9 m over the sun's rise) to reach the shadowed distance now casts nothing; in the row's three views that is the same pixels as casting (max 0.0). `STREET_FARSHADOW=cast` keeps them casting.
- Learned: the SRP Batcher is on in the pipeline but was off for OS_Finish, because `_Geo_TexelSize` sat outside `UnityPerMaterial`. Moved in, the batcher takes the shader, and the row falls a further 1.2 ms (along 5.4 to 4.2, street stop 4.0 to 3.3). But both 107 and p3 change: the whole painted surface shifts by 1 to 3 L*, up to 15 L* over 8 px blocks (10–20% of blocks at eye level, 4–6% at the street stop). The URP/Lit ground doesn't change, and a single capture shows it as much as a sequence does, so it isn't stale state. Until that is traced the batcher stays off, so the accepted look holds.
- Learned: the renderer's draw counters read nothing in batch mode, so draws are counted from the renderers in view (forward pass only).

Cost (`c04-timing.md`, `STREET_TIMING=50 render.sh 107 d15 street P overcast`; editor, batch mode, offscreen: the editor's own work is in every number, so these over-count the player's frame; a player-build timing waits until Øystein says the Mac is free):

| Row of 50, along | Draws in view | ms a frame |
| --- | --- | --- |
| c03, a material a piece | 547 | 10.3–10.6 |
| one material a far house | 127 | 4.8–5.4 |
| and far shadows dropped (default) | 127 | 4.8–5.3 |
| one house alone (the scene's own cost) | 8 | 2.75 |
| (the batcher on, look not yet held) | 127 | 4.2 |

- Per far house: 1 draw, 729 triangles, plus 1 shadow draw while its shadow can reach the shadowed distance. Over the scene's own 2.75 ms, the 49 more houses down the row (42 far, 7 at the street level) cost 2.1–2.6 ms, against 7.8 before. That leaves about 0.03–0.04 ms a far house, near the editor's run-to-run spread of ±0.3 ms.

## c05: the SRP Batcher traced, still off (29 October)

- Ruled out, in about an hour:
  - Globals and property blocks: none. No `Shader.SetGlobal…` or MaterialPropertyBlock anywhere in the project sets a name in OS_Finish's `UnityPerMaterial`.
  - Stale per-renderer data: toggling every renderer after each light change leaves the stills unchanged (e03).
  - The value of `_Geo_TexelSize` inside the cbuffer: with it inside and the pipeline's batcher off for the run (`STREET_SRPB=0`, e04), 107 matches k01 (no 8 px block moves 0.12 L*).
- So the shift comes from the batcher's own draw path, in the per-draw data it fills. The likeliest is the ambient SH (`SampleSH`): the overcast and ambient-lit faces move most, and the URP/Lit ground, batched in both runs, doesn't move. The next step is to write `SampleSH(n)` out in both paths and compare. Until then the batcher stays off; the prize is 1.2 ms down the row of 50.
- g01, the sag halved in the pack (`classical.json` bends: 31 mm a century, at most 55): 107's wall plate now sags 50 mm at mid-span, the ridge 60. In `g01-sag.jpg` (left k01, right g01: the street stop in clay overcast, then eye level in colour under low sun) the eave and the top laps run nearly straight, with a gentle dip, as the references show at that age. Triangles unchanged (near 24,474, street 6,251, city 729).

## m01: the marks are keyed to the house, not the page (29 October)

- Holds: no mark is seeded from the page, its charts or UV position. Every seed is the house, the opening, the run, the board counted down from its source, and the wall's own metres (along, up); the 3D breakup reads the rest position. The bake's charts did not move with the sag.
- What moved between k01 and g01 is a fact. Window 3's sill was dead level (−0.00002 a metre): the old sag lifted its right end as much as the corner's settlement lowered it. At half the sag the settlement wins, and the sill falls 5 mm a metre toward the corner. Water leaves a sill at its lower end, so window 3's leak flipped from its left horn to its right, and its tongue, its casing's peel and its runs moved with it. Window 2's sill only steepened (−0.003 to −0.005), with the same leak.
- The control: today's build painted with k01's sill tilts (`out-m01`, nothing else changed) matches k01's peel on the page exactly (0 texels differ). Against g01 it differs only at window 3. In `m01-marks.jpg`, eye level under low sun, the top row is k01, g01 and the control. The bottom row is the differences (k01 against g01, k01 against the control, g01 against the control). The first two show only edges, every line moved a few pixels by the sag. The third shows only window 3's casing and the water below it.

## Polish, later

- Flakes along the grain: at eye level the chips are blobby rectangles of a size. Failing paint flakes along the grain: long flakes at each board's lower edge and at the butts, the lifted edge catching the light, a hairline shadow under it (coordinator, after k01).
- The leak side is a switch at 1 mm a metre (`paint.json` `level`): a sill near level flips its whole wear on a small change. A near-level sill should pool and leak at both ends, its share easing from one end to the other as it tilts.

## w04: the window family (29 October)

- Holds: windows are built from the facts by one function (`house.py` `window`). It builds a frame in the reveal, casements or fixed lights by the pack's version, bars from the pane height, putty or beads, and the glass. Each version is data in `classical.json` `versions.window`: six-pane (1828), cross (krysspost, 1901) and one-light (1965, the husmor window: one sealed pane held by beads, no post). Glass takes its kind from the year it was glazed (`glass.json` `kinds`: crown, cylinder, drawn, float), and each kind bends its reflection its own way. Behind the glass a room is drawn by interior mapping (`OS_Glass.shader`), lit by day as a share of the light on the window's face, with sheer side curtains. The pieces are rigid, so the sag moves a window whole and never bends it. The city level keeps the reveal's flush plane.
- In 1985, 107 has one-light windows on the front (replaced 1965) and six-pane windows on the gables. The cross is 107 with its replacement moved to 1901, as a check of the version only (a fixture in the scratchpad, not the town's).
- Stills, each beside its reference at eye level (columns: reference, colour overcast, colour low sun, clay overcast):
  - `w04-cross.jpg`: ref 05.
  - `w04-six.jpg`: refs 07 and 02.
  - `w04-one.jpg`: refs 10 and 04.
- Holds: the structure matches each reference. The cross has its post, transom, two top lights and two casements with one bar each. The six-pane has two casements of three panes. The one-light has one plain sash with a wide bottom rail. The glass sits darker than the wall by the references' margin: L* 54–56 against a wall of 77 in clay overcast, against ref 05's 72 and 91. The sheers read as cloth.
- Bad: the glass reflects almost nothing, so the panes read as openings into a dark room. Refs 04 and 10 show the glass's reflection doing most of the work: the opposite street, a bright sky in one pane and dark in the next. The shader reflects the scene's trilight. Its sky is about 1.3 times the wall's light, where a real overcast sky is about 3 times, and there is no street opposite to reflect. This is for the street's light: a sky and the far side of the street for the glass to reflect. A brighter mirror here would be a painted glow.
- Bad, small: at eye level the gap between sash and frame (3 mm, 15 mm deep) reads as a hard black line. In the references it is a hairline.
- Age sheet (`w04-age.jpg`, as `age-sheet.jpg`: 107 in 1985 with its paint 2, 8 and 20 years old, then 1989; the rows are the street stop in colour under low sun, the same in clay overcast, and 12 m in colour overcast): the blank panels are gone. Each window reads as a window from the street stop and 12 m, and its paint ages with the wall's. 1989 is unchanged (every opening boarded).

Cost (`w04tw`, `STREET_TIMING=50 render.sh 107 w04tw street P overcast`, with 107 as of 1985 glazed; editor, batch mode, offscreen):
- Triangles, one house: near 24,540 one-light, 24,744 six-pane, 24,888 cross (budget 25k); street 6,229 / 6,337 / 6,433 (8k); city 643 (800).
- Glass adds one material and one draw at near and street level, and no texture: it reads the page's occlusion. The city level is still one draw.
- Row of 50: street stop 3.6 ms, raised 4.0, along 4.7 (1989's boarded row: 3.7, 4.1, 4.8). Textures unchanged: 21.3 MB a house at full; 80–97 MB streamed.
