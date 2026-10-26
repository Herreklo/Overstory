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
