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

Stills in `../second-round/`, from the same cameras in the same moments. 27 stills were rendered in 21 Unity runs.
- **Blue hour (1):** the style's ramp no longer holds a lamp colour typed in code. Its keys come from the light: the sky's colour in shade, and above the sky's own value the colour of the lamps that are on. The sky reads blue (82 92 129; the target's is 81 92 126) and the roofs silhouette. Bands are 8 43 23 24 1 against the target's 2 29 19 26 20 2 1; the target's upper bands are its lamp pools.
- **Fog (2):** the bank thickens away from the eye over 20 m (the pack's `air.bankClearM`) and stands 80 m high, so the far gully lifts 2 to 3 L* and the houses part by distance. It takes the sky's colour.
- **Low sun (3):** clouds are lit as the walls are, by the sun with little sky above them, so they take its amber. The streaks gather in fields, with octaves turned off the wind, and no longer blow.
- **Drizzle (4):** by day a cloud deck mixes towards daylight white by its cover (light-derive-2), so the pink cast is gone. Drizzle thins the air by its visibility (the pack's `air.precipitation`, by Koschmieder), so the far houses soften.
- **Follow-ups done:** the fallback lamp colour is out of code. A record's overrides for a place are pushed after the keys when that place's rig is written.
- **Strict review on Fable:** pending at this commit.

For other elements:
- Lamps: the gully lanterns are still dropped (`heart_layout.py`), so the stair and wall get no pools; that is most of the blue-hour bands' gap.
- Stone: wet treads only darken (by 4 L*). The film's gloss is capped at 0.62 by the stone board, so from the street the sheen is faint.
- The window spill's colour is still typed in `StreetStage` (it is off: `spillCd` 0).

The cost is one more exp per haze tap and one noise per sky pixel. Frame time is not measured: the full-screen run needs Øystein's Mac free. The golden baselines change with the light and need re-blessing.
