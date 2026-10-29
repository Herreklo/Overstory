# The row: 107, 108 and 109 together, each paint and roof at its measured lightness (r09)

- Bad: as a whole, r09 is worse than r08 under overcast (`r09-overcast.jpg`, column 4 against 3).
  - The roofs have washed out to 49–56: 108's slate is 27 under its white wall (r08: 49), and 109's pantile is lighter than its own wall.
  - The row has lost the dark anchors r08's roofs gave it, and the frame has gone flat.
  - In colour, 108's slate reads as a powder blue and the pantiles as a chalky pink.
  - By "beside the best so far", this does not go to Øystein.
- Bad: 109 fails its pass. In clay its wall is 4.8 under its roof (44.0 against 48.8; pass: 8 or more over it). r08 had it 2.7 over.
  - Physically the measured values can't reach that pass.
    - The ox-red measures Y 0.107 (L* 39) and a weathered pantile Y 0.116 (L* 40.6).
    - A roof at its pitch sees more sky than a wall, so under a faithfully drawn sky the wall sits under its roof.
    - Only a roof darkened by soot, moss or wet would put it 8 over, and no measured soiled tile roof was found.
    - The roof's own marks (moss, lichen, eave grime) keep the L* steps they were judged with on the clay's old 22, and on a roof of 40–48 those steps are small.
  - In colour 109 is now red with blood in it, not tarred: 42.5 at chroma 34.5 at the stop (r08 25.3 at 24).
- Bad: the display chain lifts the mids. Under r08's key (exposure 1.46, Neutral, then the toe), an L* 42 albedo (the ground) reads 67 and the ox-red's 39 reads 44.
  - The key puts the white at 83 high on the tonemapper's shoulder, so everything below it is pressed up.
  - Inverted through the chain (the toe, then Neutral) from the measured patches, a curve linear in scene luminance below the white, with the white kept at 82, gives:
    - the ground 60;
    - 108's roof 46 and 109's 39;
    - 109's wall 34;
    - the panes 14.
  - The sky (scene 1.89 against the white's 0.92) would clip, so it needs a shoulder above the white.
  - I first estimated the ground at about 41 from the albedos alone. That was wrong. On an open plane the ground takes about twice the white wall's light per unit of albedo: the scene ratio is 2.2, against an albedo ratio of 5.3–6.4. So the curve cannot bring the ground into 40–46, as r08 found.
  - The curve is r10's one change, in the grade (`grade.json`, `LT1Street.Grade`), beside the toe.
- Fixed, not a design change: 108's bake was stale.
  - Its maps (`108u`, 16:31) were older than its gens (108f 19:43, 108g 20:12), so a page baked against them lost the slate's marks.
  - r08's page (out-r02, 17:58) was baked before 108f existed, against the gen the maps were made from.
  - 108's maps are re-baked against 108g into a new folder, `cache/street/bake/108v` (108u is left as it was).
  - The control (`r08v`: HEAD's code and data on the fresh maps, with r08's pages for 107 and 109) reproduces r08 to 0.0 L on every patch, 108's roof included. The one exception is the ground (+2.0, the reflection fix).
- Bad: the ground is 2.0 L lighter (65.4 to 67.4), further from its rung. That is the reflection fix: the ground now mirrors the stage's own sky, which is lighter than Unity's default skybox. Its blue tint is gone (C 0.7 to 0.0).
- Bad: the slate's measured old value (48.5) is above r07's 28–40 rung for roofs. A weathered slate measures lighter and greyer than a fresh one.

The pass, on the street-stop clay still (p50 of clean patches; the control is r08v):

| Rung | r08 | Control | r09 | Pass |
|---|---|---|---|---|
| 109's wall over its roof, at the stop | +2.7 (24.4, 21.7) | +2.7 | −4.8 (44.0, 48.8) | ≥ 8 ✗ |
| The same from 12 m | +3.6 (23.5, 19.9) | +3.6 | −4.0 (43.2, 47.2) | ≥ 8 ✗ |
| 109 in colour, at the stop | 25.3, C 24.0 | 25.3, C 24.0 | 42.5, C 34.5 | red, not tarred ✓ |
| 108's front, side | 82.8, 85.3 | 82.8, 85.3 | 82.1, 84.9 | within 1 L ✓ |
| 108's wall from 12 m, from high | 82.0, 82.0 | 82.0, 82.0 | 81.3, 81.3 | within 1 L ✓ |
| 107's clean boards | 79.9 | 79.9 | 79.9 | within 1 L ✓ |
| The p3 corner, 16 stills | | | byte-identical before and after | within 1 L ✓ |
| Low sun: 108's lit front, its shaded side | 86.3, 52.4 | 86.3, 52.4 | 85.6, 52.0 | within 1 L ✓ |
| Low sun, colour: 108's lit front, its shaded side | 86.2, 52.5 | 86.2, 52.5 | 85.7, 51.8 | within 1 L ✓ |
| Every value traced to a source | | | 7 of 9 measured; the alkyd whites are an estimate from Jotun's hex colours, and the grey-green has no source | ✗ on two |

Moved by their albedo (clay, overcast, at the stop):

| Patch | r08 | Control | r09 |
|---|---|---|---|
| 109's side | 21.2 | 21.2 | 38.2 |
| 109's roof (pantile, 88 years) | 21.7 | 21.7 | 48.8 |
| 108's roof (slate, 88 years), at the stop and from 12 m | 34.0, 35.7 | 34.0, 35.7 | 54.8, 56.3 |
| 107's grime band | 54.0 | 54.0 | 54.0 |
| Ground | 65.4 | 67.4 | 67.4 |
| Sky | 92.7 | 92.7 | 92.7 |
| Low sun: 109's lit front, its shaded side, its roof | 37.9, 7.2, 5.9 | the same | 51.6, 11.8, 14.7 |
| Low sun: 108's roof | 8.8 | 8.8 | 17.5 |

Low sun is in the same sheet (`r09-lowsun.jpg`), in the same views as overcast, and is measured on the same patches above. There, 109's lit front stands 37 over its roof, which faces away from the sun.

The values and their sources (each also written beside its value in the data):

| Value | Was | Now | Source |
|---|---|---|---|
| Linseed white, wall and trim | 89, 90 | 92 | Measured: TiO2 in linseed on spruce, L* 92.0 (Baar et al., WCTE 2025, Table 4). Its measured b* +9.6 is not applied: this round is lightness. |
| Alkyd white, wall and trim | 92, 93 | 94 | Estimate: Jotun 9918 and 1001 hex colours, L* 94.4 and 93.7. No measured titanium alkyd white was found. |
| Ox-red (109) | 34, C 34, h 33 | 39, C 35, h 37 | Measured: iron-oxide red earth in linseed, L* 39.0 fresh, 39.9 after 5 years outdoors (Baar et al.). Cross-checks: Taubmans LRV 9.34 (L* 36.6), Jotun 0154 (37.9). |
| Ochre | 66, C 38, h 78 | 54, C 46, h 67 | Measured: ferric oxide yellow in linseed (Baar et al.). |
| Grey-green | 62 | 62 | None found; authored, unverified. |
| Pantile, new and old | finish's 22 | 45, 40.6 | New: clay tile VIS 0.15 (Kültür & Türkeri 2012), brick ECOSTRESS 0097 L* 45.5. Old: weathered terracotta tile ECOSTRESS 0484, L* 40.6, C* 9.1. |
| Slate, new and old | finish's 22 | 42.2, 48.5 | New: grey phyllite ECOSTRESS Ward85 (Norway's roof slates are phyllites, snl.no). Old: weathered slate shingle ECOSTRESS 0680, L* 48.5. |
| Deposits | | `packs/stavanger-1989/materials/deposits.json` | Runoff dust 44.7 (median of nine ECOSTRESS soils), grime 12.9 (USGS carbon black), rust 47.7 (USGS goethite film), lichen 53.5 (USGS Xanthoparmelia), moss 21.6 (Lovelock & Robinson R550, an estimate); shade and wet are not deposits (L 0). |

The pantile is at its measured 40.6, not the 32.5 in the brief: no measured source gives 32.5.

How it is made:
- **A mark is a deposit, not a fixed step.** Each mark lays its dirt over the surface, lerp(surface, dirt, share), in luminance.
  - The share is the one that takes the value the mark was judged on down by the mark's judged step. On the walls that value is the clay white (85.3), so 109's red takes the same share of the same dirt as a white wall. On a roof it is the roof's own value.
  - Before, a mark subtracted the same L* from every paint, so on the dark red 109 the marks went near black.
  - The page's cover is now T·Y + D (hist-p2 B and A, `coverScale`). The shader's stain, wash and lap grime use the same Cover(L, step, dirt) (`OS_Finish`, `_Deposit`).
  - A page with no `deposit` field gives `_Deposit` 0, which is the old arithmetic. Old pages render bit-identical under the new shader (r09a against r09o: 0 pixels differ).
- **What each mark is made of** is data: `deposits.json` for the dirts, and `paint.json` deposit.parts for which mark lays which.
  - The runs off the openings and the long washes, chalk included, take grime, not dust. They were judged as dark as L* 17 on the clay, and dust (44.7) cannot reach that.
  - With dust, 4.1% of 107's page could not make its step, and its band went 7.3 lighter and warm (C 3 to 22). With grime the band is back at 54.0.
  - What still cannot make its step is moss on 107 (0.24% of the page) and on 109 (0.17%), held at the moss's own value.
- **A roof's value** is its material's own, from new to old over `oldYears` (`clay-pantile.json`, `roof-slate.json`, `value`). The cladding's clay value is the clay white times the paint's L* over the white's, so a dark paint is a dark clay.
- **The reflection source** is the stage's own sky: a 32 px cube of the drawn sky and the ground (`LT1Street.Reflection`), set as the custom reflection. The glass already mirrors the drawn sky (`_OS_StageSky`, r08), and the wet takes the same cube, so nothing mirrors Unity's default skybox now.
- **New folders.** Every bake is a new `out-r09` page, and 108's maps are new (`108v`). 107h's gen and `107z4/out-hull` are untouched.
- **The rock's 107.** Its page (`out-hull`) has no `deposit` field, so under the new shader it renders as before: a difference of 0, by construction and by the bit-identical old-page proof. I did not open HolmTip, which is the rock lane's uncommitted scene.

Cost: no new texture fetch, since hist-p2 was already RGBA at the same size (4096; 2048 for 107). The shader adds one branch per material and a few ALU, and the reflection cube is 32 px, made once at build. I ran no timing, so t09 (street 4.6, raised 4.8, along 5.3, near3 5.7 ms) stands.

Sheets:
- `r09-overcast.jpg` and `r09-lowsun.jpg`: rows eye, street stop, 12 m and high; columns p3 P | r01 P | r08 P | r09 P | r08 Pc | r09 Pc.
- `r09-close-glass.jpg`: 108's near view at 4.4 m, r08 | r09, overcast above and low sun below, then refs 10 and 04. The panes and the whites are unchanged.
- `r09-board.jpg`: 108 alone at 12 m and from high, r08 | r09, both lights, then ref 04's window.
- `r09-walk.jpg`: 12 frames of 108's walk, each r08 row above the r09 row with the same frames. It has no pop.
- `r09-p3-corner.jpg`: the p3 corner in every view and both lights, before | after the shader change. The stills are byte-identical.

These renders carry r03's toe (`packs/stavanger-1989/light/grade.json`). It is still uncommitted and waits for Øystein's yes.

    B=/Applications/Blender.app/Contents/MacOS/Blender
    $B -b --factory-startup -P blender/parts/street/bake.py -- --gen cache/street/gen/108g --cache cache/street/bake/108v   # 108's maps, against its current gen
    $B -b --factory-startup -P blender/parts/street/paint.py -- --gen cache/street/gen/108g --cache cache/street/bake/108v --out cache/street/bake/108v/out-r09   # and 107h 107z4, 109g 109u
    STREET_ROW="107:cache/street/gen/107h:cache/street/bake/107z4/out-r09 108:cache/street/gen/108g:cache/street/bake/108v/out-r09 109:cache/street/gen/109g:cache/street/bake/109u/out-r09" python3 tools/unity_lock.py run -- bash blender/parts/street/run/render.sh row r09 eye,street,raised,high P,Pc overcast,lowsun
    STREET_GEN=cache/street/gen/108g STREET_PAINT=cache/street/bake/108v/out-r09 python3 tools/unity_lock.py run -- bash blender/parts/street/run/render.sh 108 r09h eye,street,raised,high P,Pc overcast,lowsun
    STREET_WALK=120 STREET_GEN=cache/street/gen/108g STREET_PAINT=cache/street/bake/108v/out-r09 python3 tools/unity_lock.py run -- bash blender/parts/street/run/render.sh 108 r09w eye,street Pc overcast
