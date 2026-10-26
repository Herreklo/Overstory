# The walked corner's light, first pass (26 October)

Commits `08cbf5f` (the light record) and `15ebaef` (cheaper light). Stills: `street-*` from the target's camera (target: `../../heart/target/3-street-gully-steps-target.png`), `foot-*` from a person's eye at the foot of the steps, in blue hour with sea fog, drizzle at 13:00 and low sun at 16:00. Frames rendered r00 to r17.

**Strict review on Fable: FAIL** for the light's share. The faults, worst first:
1. Blue hour has no sky. It shows no zenith-to-horizon gradient and no glow, and sky and fog share one value, so the roofs don't silhouette. Our value bands (per cent by L* band 0 to 9) bear it out: the render is 1 20 53 24 1 0 0, the target 2 28 20 26 21 2 1. Region means matched the target within 2 L*, but they hide this.
2. The fog doesn't layer with depth: near and far houses sit at one value, and the fog is neutral grey, not sky-lit blue.
3. In low sun, the high streak layer blows to white in repeating streaks, and the clouds never take the amber that the walls take.
4. Drizzle has a pink-beige cast (a hue that the numbers put at chroma 0.01, but the eye sees), with no softening in the distance. The treads read dry.
5. No pools under the lamps and no spill from the windows. This is partly lamp placement: all the gully lanterns are dropped by `heart_layout.py`'s "never on another way" check, which is the lamps element's to fix.

The reviewer's lift: a real blue-hour sky gradient, with the fog taking its colour and thinning toward the camera.

**What holds:**
- Every light value is data in the light record (`tools/light_record.py check`: 4 of 4 hold).
- Drizzle clouds sit at the deck's derived light, with the CIE gradient.
- The windows and halo match the target.

**Cost:**
- One 512² cloud map now serves both the cloud shadows and the beams. It is drawn before the opaques and redrawn only when the drift strays.
- The town sky now reads a horizon map worked out once per town: 12 taps a pixel instead of 64. The map is 1 m texels at 6 heights, about 50 MB for the 1 km square. Against the old term it agrees within 1 L* per region and 5 L* at p99.9.
- Frame time is not measured yet: the full-screen run needs Øystein's Mac free.
- The golden baselines change with the light and need re-blessing.

**Follow-ups:**
- The fallback lamp colour is still in code (`StreetStage.SetStyle`).
- Record overrides are not yet applied in the derivation.
- The blue-hour fog was set to 200 m for the look.
- For a city, the sky map and its horizon move to a window round the camera.
- Drizzle's wet ground reads pale with dark puddles; that is the ground element's.

## Second round (26 October)

Stills in `../second-round/`, from the same cameras in the same moments. 36 stills were rendered in 24 Unity runs.
- **Blue hour (1):** the style's ramp no longer holds a lamp colour typed in code. Its keys come from the light: the sky's colour in shade, and above the sky's own value the colour of the lamps that are on. The sky reads blue (82 92 129; the target's is 81 92 126) and the roofs silhouette. Bands are 8 43 23 24 1 against the target's 2 29 19 26 20 2 1; the target's upper bands are its lamp pools.
- **Fog (2):** the bank thickens away from the eye over 20 m (the pack's `air.bankClearM`) and stands 80 m high, so the far gully lifts 2 to 3 L* and the houses part by distance. It takes the sky's colour.
- **Low sun (3):** clouds are lit as the walls are, by the sun with little sky above them, so they take its amber. The streaks gather in fields, with octaves turned off the wind, and no longer blow.
- **Drizzle (4):** by day a cloud deck mixes towards daylight white by its cover (light-derive-2), so the pink cast is gone. Drizzle thins the air by its visibility (the pack's `air.precipitation`, by Koschmieder), so the far houses soften.
- **Follow-ups done:** the fallback lamp colour is out of code. A record's overrides for a place are pushed after the keys when that place's rig is written.
- **Strict review on Fable: FAIL** (narrow). Drizzle is near its intent. Still open: the blue-hour dome is flat and darkens toward the horizon from the foot, with no glow; the low-sun sky is a warm grey with no blue, and its streaks repeat; the far fog is thin in blue hour and drizzle; the blue-hour near field is a band dark. The glow over the gully and the lifts at the stair and right wall are lamplight in the target (the lamps element's).
- **After the review:** a slow wander bends the streaks in long waves, so their rhythm loosens. Drizzle now fills the air up to the cloud: the air thins with height only by the haze's share of it, which lifts the far house 2 L*. A faster dome curve (0.35) moved the low-sun sky by under 1 L*, so it was put back.
- **Still open, for the next round:** the low-sun sky lacks blue because the derived clear zenith is pale (single scattering with a haze of 0.3 leaves out the blue that multiple scattering adds), so the fix is in the model or a `sky.zenith` key push. Drizzle's far air needs a look push on `air` for overcast, beyond what the drizzle's visibility gives. Under a 0.9 deck the blue-hour sky follows the CIE overcast law, darker low, and its glow over the gully is the missing lanterns'. After those, the fog lights' cure, then the strict review again.

For other elements:
- Lamps: the gully lanterns are still dropped (`heart_layout.py`), so the stair and wall get no pools; that is most of the blue-hour bands' gap.
- Stone: wet treads only darken (by 4 L*). The film's gloss is capped at 0.62 by the stone board, so from the street the sheen is faint.
- The window spill's colour is still typed in `StreetStage` (it is off: `spillCd` 0).

**Frame time** (26 October, 23:05 to 23:16, on a quiet machine with Understory paused: load 1.5 to 5.5; one run of the walk's nine views in three lights, `reviews/perf/2026-10-26/playable/light-r2/run-2`, and a pass split at the foot and the street stop, `light-r2-passes/passes.md`). Numbers taken earlier under load 20 were rough and are replaced.

| Light | Frame (ms) | Frames a second | Against W7 |
| --- | --- | --- | --- |
| Drizzle | 14.9 to 27.3 | 37 to 67 | 4 to 6 ms cheaper |
| Low sun | 16.3 to 27.2 | 37 to 61 | 5 to 9 ms cheaper |
| Blue hour | 41.8 to 51.1 | 20 to 24 | 23 to 28 ms dearer |

What the terms cost (offscreen, at the foot and the street stop):
- Blue hour's lamps in the fog (FogLights): 21.5 to 21.9 ms. The pass loops over all 403 of the town's lamps at every pixel, and since the first pass put blue hour in sea fog, the halos are on. That is the whole regression. The cure is to cull the lamps to the view each frame and draw the halos at a quarter of the pixels, as the beams are.
- The fog bank on surfaces and sky (the 12-tap march; the `haze-off` arm): 9 to 11 ms at blue hour, about 1 ms by day.
- The sky: 1 to 2 ms. The four full-screen passes by day: 3 to 5 ms.

The golden baselines change with the light and need re-blessing.

## Third round (27 October)

Stills in `../third-round/`, from the same cameras in the same moments. 26 views (52 stills with their grey) were rendered in 9 Unity runs, plus one timing run.
- **Low sun (1):** the clear zenith the model gives was blue enough; the style's pass greyed it. The colour ramp and the chroma drain now act only on what the light falls on, weighed by how much of it the air hides, so the sky and the air's light over far walls keep the light's colour. Clear low sun takes a small `sky.zenith` push (dC 0.05, dh −6). The cirrus gathers in uneven fields, with the streaks' width varying over the sky. In light-derive-3, each march step integrates its own extinction.
- **Far air (2):** `air` is pushed +0.9 stops under overcast and `fog` +0.7 in the fog rows (`keys.json`), so drizzle's houses part by distance and the bank lifts the far gully 6 L* at blue hour.
- **Blue-hour dome (3):** the cloud base is lit from below by the lamps' light to the sky: the share sent up, and of the rest what the wet ground gives back through the street's open share. It is spread over the base as from a face turned up, at the cloud kind's albedo (new in the pack), on a coarse map from `TownLights`, and replaces a typed ×3. At 17:50 under the fog it adds a few per cent. Away from the gully the target's sky is flat (L* 39 to 40); its lift over the gully is the lanterns' glow.
- **Fog lights (4):** the lamps are culled to each camera's view, and the halos are drawn at a quarter of the pixels with a composite that minds the rays' lengths (`FogLightsFeature`). They are within 5/255 of the old pass on every pixel. Offscreen in the editor, with no window (`reviews/perf/2026-10-26/light-r3-foglights.md`), the pass went from 19.0–19.5 ms to 1.6–1.7 ms, and a blue-hour frame from 44–47 ms to 26–30 ms. The old pass stays as the A/B arm `foglights-full`.
- **Shade in low sun:** the bright sky round the sun is hidden by whatever hides the sun (`OS_SkyFor`), so a wall in cast shadow takes the horizon's own lilac, not the sun side's amber. After sunset the sun side's glow is a wide arch that no shadow hides, so this applies only while the sun is up (as the sky's own `sunUp`).
- **Still over 16.7 ms:** blue hour is now about 2 ms dearer than with no halos at all. What is left is the fog bank's march (9 to 11 ms in round 2) and the scene itself, since drizzle is 23 to 28 ms offscreen too. The full-screen walk is still owed.
- **Strict review (Fable):** blue hour and drizzle pass. Low sun failed on warm shade under a lilac sky and passed after the fix. To watch: the shade sits a touch heavy against the pale ground. Minor, for the ensemble: the cirrus's colour should vary with its bearing to the sun; the clear zenith should deepen away from the sun; drizzle's overcast reads as horizontal smears; blue hour's sky and fog are cleaner and bluer than the target's dusty violet.
