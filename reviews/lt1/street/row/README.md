# The row: 107, 108 and 109 together, the overcast key (r08)

- Bad: the ground misses its rung. At the street stop it is 65.4 (pass 40–46; r07 54.7), so the white front stands only 17 above it. Ref 10 puts it 43 above.
  - Until the street has its own ground, the stage's ground is a stand-in: a URP Lit plane at L42, an albedo of 0.126. That is an aged dry asphalt (0.10–0.15), and I left it there.
  - On an open plane under this sky, 40–46 needs an albedo of 0.04–0.05, a fresh or wet asphalt. The road in ref 10 runs between houses that hide much of its sky, and it is likely damp.
  - A darker value here would be a material picked to meet the number, so the rung waits for the street's own ground.
  - The clay ground also has a faint blue tint (C 0.7–1.2, where every clay house is C 0), and it is 1.5 L lighter far off than near. It mirrors a little of Unity's default skybox, which Street.unity uses as its reflection source: a sky the stage does not draw. That stray light should go when the street gets its own ground.
- Bad: the sky's gradient misses its rung. Its sd over the open sky is 1.9 (pass ≥ 3; r07 0.7), running from 86.3 at the horizon to 91.6 at the top of the frame.
  - That is the CIE sky's own gradient over the band the frame sees, about 0 to 20° (1.7× in radiance), pressed by the tonemapper's shoulder.
  - More would need a cloud deck, or the bright cloud round the sun, and the sun is behind the camera at the stop.
  - The sun's quarter of the light (sun 0.3) is not drawn in the sky.
- Bad: the white gable now sits 6–8 L under the sky, as in the photographs, but its verge trim (about 88–90) is level with the sky. At the street stop and down the walk, only the shaded underside of the verge draws 108's outline against the sky (`r08-walk.jpg`, bottom row).
- Bad: the frame is lighter, not yet more alive. Everything moved up with the exposure, so faults 2 to 6 in r07's critic still stand. They are measured on the new key below.

The pass, on the street-stop clay still (p50 of clean patches):

| Rung | r07 | r08 | Pass |
|---|---|---|---|
| Sky | 71.5 | 89.9 | 87–93 ✓ |
| Sky sd | 0.7 | 1.9 | ≥ 3 ✗ |
| 108's front | 73.7 | 82.8 | 80–86 ✓ |
| Sky over the front | −2.2 | 7.1 | 6–12 ✓ |
| Ground | 54.7 | 65.4 | 40–46 ✗ |
| Frame p5 / p50 / p95 | 15.2 / 54.7 / 72.9 | 21.2 / 65.4 / 92.3 | p95 ≥ 90 ✓ |
| Eye-level panes: 108's near view at 4.4 m, lower sashes, against the wall | 13.2–14.7 against 72.9 | 15.2–17.1 against 82.4 | ≤ 20 ✓ |
| Low sun | | r07's to 0.00 L in every view, P and Pc, the row and 108 alone | unchanged ✓ |

Report only, for r09's material facts (clay, overcast):

| Rung | r07 | r08 | Target |
|---|---|---|---|
| 107's wall: clean boards between the openings, at the stop | 69.6–70.4 | 79.5–79.9 | within 8 of 108's (82.8) ✓ |
| 107's wall: the grime band under its windows | 43.6 | 54.0 | 29 under 108's ✗ |
| 109's wall: front, side | 16.6, 14.7 | 24.4, 21.2 | 30–38 ✗ |
| 109's wall over its roof | 1.4 | 2.7 | ≥ 12 ✗ |
| Roofs: 108, 107 | 23.5, 24.9 | 34.0, 34.9 | 28–40 ✓ |
| Roofs: 109 | 15.2 | 21.7 | 28–40 ✗ |
| Panes at the stop, 108's main floor (whole openings) | 17.5–19.9 | 21.2–24.9 | ≤ 30 ✓ |
| Panes at the stop, 108's upper floor | 19.9, 27.1 | 25.8, 36.1 | ≤ 30: one ✗ |
| Panes at 12 m, the row (whole openings, board included) | 27.5–34.9 | 38.2–45.2 | ≤ 30 ✗ |
| Panes from high | 39.1–41.1 | 49.2–51.6 | ✗ |

- 108's wall is 82.0 at 12 m and from high (r07 72.6), so the windows keep the gap to their wall that they had in r07 and gain none. That is r07's fault 4, unchanged.
- In colour at the stop, 109's red is 25.3 at chroma 24 (r07 17.9 at 17.4). The sky stays at chroma 0, the ground at 0.7.

Holds:
- The ladder's order is now the photographs': sky 90, the white front 83, which is 7 under it, the roofs at 34 and the panes at 15–25.
- At 4.4 m the lower sashes are 15–17 against a wall of 82. That gap of 65–67 (r07 58–60) is closer to Normanns gate 27's 73.
- Low sun is r07's to 0.00 L, so its ratio holds: 108's lit front 79.5, its shaded gable 40.7.
- No pop: on 108's walk from its eye view to its street stop, the largest frame step is 1.03× its neighbours'.
- No re-bake, and 107's cache is untouched.

How it is made:
- **The cause, measured first.** Both causes held: the sky was drawn too dark, and the key was low.
  - In r07 the drawn sky was the camera's flat background at linear 0.343. That is a third of the light the sky cast (level ground took 1.017 from the trilight), and darker than even that sky's CIE horizon (0.41 at the horizon to 1.31 at the zenith).
  - Before exposure, the white front was about 0.35, as bright as the sky behind it. The exposure of 0.72 put both at L64–74.
- **The sky.** `OS_StageSky` draws the CIE overcast sky on a sphere round the camera, behind everything.
  - At elevation e the sky is (1 + 2 sin e) / 3 of its zenith, and below the horizon it keeps the horizon's value.
  - `LT1Street.Sky` sets the zenith from the light the row casts, so the sky drawn is the sky that lights the street. Unity's trilight grades from the equator at the horizon to the sky overhead, so level ground takes equator + 2/3 (sky − equator). Under a CIE sky, that is 7/9 of the zenith's radiance.
  - A light row draws the sky when it says `drawn: "cie-overcast"`. Low sun draws none and keeps the flat background.
- **The glass.** Where the stage draws its sky, OS_Glass mirrors that sky (`_OS_StageSky`): its horizon is a third of the zenith, and the sky rises as (1 + 2 sin e) / 3. The flash's shore takes the same horizon. Where no sky is drawn, the glass keeps the trilight.
- **The key.** The exposure of `blender/parts/street/paint.json` light.overcast goes from 0.72 to 1.46. It is keyed to put the white front at about L83, 6–12 under the sky and below the tonemapper's steepest shoulder. It is data, not code.
- **Where the key lives.** The brief put any art push in keys.json's overcast rows. The stage does not read keys.json: that file is the light record's (LightDerive), so changing it would move the town's light record and leave the stage where it was. The stage's own light is the street's paint.json, so the key is there.
- **No re-bake.** A baked paint carries the light rows from when it was baked (its paint.json `lights`), and 107's cache cannot be rebuilt.
  - LT1Street now reads the rows from their sources at render time (`SourceLights`): finish.json painted.light, then the street's paint.json light. It falls back on the baked rows.
  - With r07's data, the new code renders r07 to 0.00 L (control `r08c`).

Sheets:
- `r08-overcast.jpg` and `r08-lowsun.jpg`: rows eye, street stop, 12 m and high; columns p3 P | r01 P | r07 P | r08 P | r07 Pc | r08 Pc.
- `r08-close-glass.jpg`: 108's near view at 4.4 m, r07 | r08, overcast above and low sun below, then refs 10 (Normanns gate 27) and 04 (Tidegeilen 9).
- `r08-board.jpg`: 108 alone at 12 m (r07 | r08) and from high (r07 | r08), overcast above and low sun below, then ref 04's window.
- `r08-walk.jpg`: 12 frames of 108's walk from its eye view to its street stop. Each r07 row sits above the r08 row with the same frames. The 5 s clip is `cache/street/renders/r08w/walk-108.mp4`.

These renders carry r03's toe (`packs/stavanger-1989/light/grade.json`). It is still uncommitted and waits for Øystein's yes.

    STREET_ROW="107:cache/street/gen/107h:cache/street/bake/107z4/out-r02 108:cache/street/gen/108g:cache/street/bake/108u/out-r02 109:cache/street/gen/109g:cache/street/bake/109u/out-r02" python3 tools/unity_lock.py run -- bash blender/parts/street/run/render.sh row r08 eye,street,raised,high P,Pc overcast,lowsun
    STREET_GEN=cache/street/gen/108g STREET_PAINT=cache/street/bake/108u/out-r02 python3 tools/unity_lock.py run -- bash blender/parts/street/run/render.sh 108 r08h eye,street,raised,high P,Pc overcast,lowsun
    STREET_WALK=120 STREET_GEN=cache/street/gen/108g STREET_PAINT=cache/street/bake/108u/out-r02 python3 tools/unity_lock.py run -- bash blender/parts/street/run/render.sh 108 r08w eye,street Pc overcast

Cost:
- Overcast adds one draw: the sky sphere, Unity's sphere of 768 triangles, with no shadows and no depth write. The glass adds one branch.
- The timing runs in low sun, which draws no sky, so it cannot see the sphere. I did not run a new timing, and t09 (street 4.6, raised 4.8, along 5.3, near3 5.7 ms) stands.
