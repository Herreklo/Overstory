# W3: the walk's harness, and the lamps as the facts have them

LT1g, Phase 1a, stage W3 (`reviews/lt1/playable/outline.md` §2), 22 October 2026, Opus 5.5. Code commit `f19feaf`; results and docs in the commit that adds this report.

## In short

- The harness now measures what the walk's player draws. Run it with `tools/perf.sh playable`. It covers the five judging views and LT1g's four (A's window, the steps, the Row, the Anchor's door) in drizzle, low sun and blue hour.
- The fact fix: a house's shop lights burn only if its diary gives it a business in 1989. A has none in 1989, so its two shop lights are gone. They lit A's pavement in the blue hour. The fix reads the facts; nothing in it names A.
- The Anchor (`pl-bar`) is cast onto Harbour Row 24 in an authored sidecar, `fixtures/lt1-places-1989.json`. The heart is not rebuilt, and `heart_layout.py` is not edited.
- Baseline (offscreen, two runs):
  - drizzle: 24 to 44 ms;
  - low sun: 87 to 107 ms;
  - blue hour: 20 to 37 ms.

  The presented frame runs at 11 to 58 fps.
- The three biggest costs, with their owners:
  - low sun's beams: 64 to 66 ms (1c);
  - the materials' shaders: 9 to 14 ms (owner unknown until L5);
  - the birch: 11 to 17 ms where it is in view (1e).
- Golden passed before and after: all 15 frames are bit-identical.

## What was built

**The fact fix** (`LT1Play.ShopLights`, called from `ComposeOpen`):
- It reads `reviews/lt1/time/readers/diaries.json`: the houses' footprints, and the real arm's events.
- A house has a business in a year if the last of its `business_opened`, `business_closed` and `shop_removed` events up to that year opened one. Events are sorted by year, then by the diary's order.
- A shop lamp within 1 m of the footprint of a house with no business is dropped. The rest are written to `Assets/Experiments/LT1/Playable/Generated/lights-1989.json` (generated, not in git), and the stage's `TownLights` reads that file.
- The log names each lamp it dropped: `(39.79, 1.36) at A, (44.40, 1.31) at A`. That leaves 401 of 403 lamps.
- In 1989 none of A to E has a business: A's ironmonger closed in 1974 and its café opens in 2000, and B's bakery opens in 2000. So other years and other houses follow the facts with no further change.
- `Check` refuses the scene if:
  - its lamps come from anywhere else;
  - any shop light stands at a house with no business.

  It prints each house's business. HR 24's two shop lights stay lit, as fits the Anchor.

**The Anchor.** `fixtures/lt1-places-1989.json` gives `pl-bar`, the Anchor, on Harbour Row 24, with its footprint, its door at (23.29, 1.57, 1.9) facing the Row, `provenance: authored`, and a cause. The engine has the place but no building for it.
- I chose HR 24 because `docs/town-plan.md` puts the Anchor on Harbour Row. HR 24 is the merchant house on the Row nearest the corner (its east end is 5 m short of A).
- `heart_layout` already lights its ground floor and leaves its upper floors dark at 17:50 on a Friday. So the casting changes nothing on screen.
- I checked the values against `heart_layout.lay_out()` in Blender's Python.
- No heart entry was needed this week, and `heart_layout.py` is unchanged. The next heart rebuild should take the name from the sidecar (below). Test 2a's `sight.py` can read the same file for the Anchor's door.

**LT1g's four views** (`LT1Play.CaseViews`) are authored vantages at eye level, appended after the five judging views as indices 5 to 8. W4's keys 6 to 9 can call `SetView(5..8)`.

| View | Where | Looking at | Lens |
| --- | --- | --- | --- |
| `a-window` | the pavement at A's corner, beside its end window (from A's footprint) | up the lane and the steps | 35 mm |
| `steps` | on the Landing, (47.6, 45.0) | up the upper flight to E | 35 mm |
| `row` | across the Row from the lane's mouth, (52.4, −10.0) | up the lane | 28 mm |
| `anchor-door` | 2 m out from the Anchor's door (from the sidecar) | along the Row to the corner | 35 mm |

The stills are in `reviews/lt1/playable/walk/w3/`, in drizzle and at the blue hour. A's pavement is dark at the blue hour in `anchor-door` and `a-window`.

**The harness arm.**
- `LT1Perf.BuildPlayable` composes with `LT1Play.ComposeOpen`. It removes every `Overstory.Play` behaviour except `PlayCorner`; today that is the frame-time overlay, so the overlay is hidden in harness runs. It then places the runner with the player's nine views and saves `Perf/Generated/LT1_PerfPlayable.unity`. It builds `Builds/Perf/OverstoryPerfPlayable.app` and runs it into `reviews/perf/<date>/playable/`.
- The runner placement (`AddRunner`) and the build-and-run step are shared with the corner's arm, which behaves as before.
- This is how W3 places the runner, the item in the pre-mortem's §4. `-perf-scenes` only picks setups inside one built scene, so the walk's scene needs a build of its own.
- `PerfRunner`:
  - gains `composed` ("corner" or "playable"). `-perf-scenes playable` names that scene, and its segments keep plain names.
  - Asking a build for the other composed scene logs an error.
  - A pass configuration can turn several passes off (`-beams+shadows`).
- `tools/perf.sh playable` runs the arm.
- `tools/pass_budget.py` reads the playable scene and LT1g's views. It now has a beams and shadows split (each one alone, and only together) and flat rows.

## Files

- `unity/Assets/Code/Editor/LT1Play.cs`: shop lights from the diaries, `CaseViews`, the sidecar reader, a small JSON member scanner, `Check` for nine views and the lamps.
- `unity/Assets/Code/Editor/Measuring/LT1Perf.cs`: `BuildPlayable`, `ComposePlayable`, `AddRunner`, `BuildAndRun`, `BirchRoot`.
- `unity/Assets/Code/Perf/PerfRunner.cs`: `composed`, multi-pass configurations, `Run.scene`.
- `tools/perf.sh`, `tools/pass_budget.py`.
- `fixtures/lt1-places-1989.json`.
- `reviews/lt1/playable/walk/w3/*.png`.
- `reviews/perf/2026-10-22/playable/`: `run-1`, `run-2`, `runs.md`, `passes/run-1`, `passes/passes.md`.
- `docs/measuring.md`: "The walk's whole scene".
- `docs/plan.md`: "Frame time today" replaced by this baseline, and the three costs entered in the frame-rate gate.

## Numbers

Baseline: two runs, 36 segments, 150 frames × 2 rounds each. `runs.md`: within 3% on 22 of 36 segments, worst 10.2% (offscreen, steps in low sun). Figures are the means of the two runs' medians, in ms.

| View | Drizzle offscreen | Drizzle frame | Low sun offscreen | Low sun frame | Blue hour offscreen | Blue hour frame |
| --- | --- | --- | --- | --- | --- | --- |
| eye-foot | 36.1 | 30.1 | 102.9 | 87.0 | 29.9 | 26.1 |
| eye-on | 39.3 | 33.4 | 104.8 | 91.7 | 33.5 | 30.6 |
| street | 41.8 | 35.1 | 104.9 | 91.4 | 33.0 | 29.1 |
| into12 | 40.8 | 33.5 | 102.3 | 89.4 | 31.9 | 28.2 |
| high | 44.0 | 37.1 | 107.3 | 93.8 | 36.6 | 31.9 |
| a-window | 35.6 | 29.9 | 98.1 | 85.7 | 27.9 | 24.6 |
| steps | 31.0 | 25.7 | 99.3 | 83.4 | 25.4 | 22.5 |
| row | 33.6 | 28.8 | 99.2 | 87.2 | 26.2 | 23.1 |
| anchor-door | 24.2 | 20.9 | 86.7 | 74.8 | 19.7 | 17.3 |

Triangles: 11 to 17 million with the sun's shadows, 4 to 6 million at the blue hour. The main thread takes about 1 ms. The five judging views cost 1 to 5 ms (2 to 6%) more than the gully's corner on 21 October; that is the clay town and the houses, which count as scope.

The pass split: one run, at eye-foot, street, a-window and anchor-door, plus the empty frame (`passes/passes.md`). In low sun:

| | eye-foot | street | a-window | anchor-door |
| --- | --- | --- | --- | --- |
| all | 99.8 | 105.7 | 99.2 | 87.9 |
| beams | 64.1 | 65.6 | 65.1 | 64.2 |
| beams and shadows together | 71.5 | 73.9 | 72.7 | 69.2 |
| the beams, no shadow map | 40.2 | 39.8 | 39.6 | 39.6 |
| the shadow map, no beams | 7.4 | 8.4 | 7.6 | 4.9 |
| only together | 23.9 | 25.7 | 25.4 | 24.7 |
| the materials' shaders (bare less flat) | 11.8 | 12.9 | 9.1 | 5.9 |
| MSAA | 8.7 | 13.3 | 10.9 | 7.9 |

In drizzle and at the blue hour:
- the materials' shaders: 9.0 to 13.6 ms (5.8 to 6.2 at the Anchor's door);
- MSAA: 1.8 to 5.7 ms;
- the shadow map: 3.4 to 5.3 ms in drizzle.

No conclusion rests on a difference under a millisecond, so no sub-millisecond A/B was run alone. Differences on a 35 ms frame wander by about ±2 ms.

## The three biggest costs, with owners

1. **Low sun's beams, 64 to 66 ms. Owner: 1c.** The suspect's 64 ms is confirmed. 40 ms is the full-screen pass itself: 40 taps a pixel, the same in an empty frame. 24 to 26 ms is those taps reading a real 4096 shadow map. Without the beams and the shadow map, low sun would cost about what drizzle costs.
2. **The materials' shaders, 9 to 14 ms in every light** (6 ms at the Anchor's door). **Owner: unknown until L5** says which shader carries it; until then it sits with the plan's shader families, in the port's step 4. The bare scene is 7 to 16 ms, and the same geometry unlit is 1.3 to 2.1 ms.
3. **The birch, 11 to 17 ms where it is in view, in low sun. Owner: 1e.** By A/B the birch costs +12.6 at the street stop, +10.7 at 12 m and +17.4 at the city camera; the pass run gives +11.1 at the street stop. Where it is out of frame, the A/B is lost in noise: the steps view moved 5.5 ms with no change of triangles.

Close behind these are MSAA 4x, 2 to 6 ms (8 to 13 in low sun; owner 1c's pipeline), and the shadow map alone, 5 to 8 ms (1c). In low sun at the street stop, MSAA (13.3) is level with the birch, so the third place is narrow, and MSAA is in every frame.

## Golden

Before the first Unity run: PASS, all 15 frames "0 pixels changed (identical)".

After the last Unity run:

    PASS gully/1300-drizzle/eye-foot.png: mean 0.000000, p99.9 0.0000, worst 0.0000, 0 pixels changed (identical)
    PASS gully/1300-drizzle/eye-on.png: mean 0.000000, p99.9 0.0000, worst 0.0000, 0 pixels changed (identical)
    PASS gully/1300-drizzle/high.png: mean 0.000000, p99.9 0.0000, worst 0.0000, 0 pixels changed (identical)
    PASS gully/1300-drizzle/into12.png: mean 0.000000, p99.9 0.0000, worst 0.0000, 0 pixels changed (identical)
    PASS gully/1300-drizzle/street.png: mean 0.000000, p99.9 0.0000, worst 0.0000, 0 pixels changed (identical)
    PASS gully/1600-low-sun/eye-foot.png: mean 0.000000, p99.9 0.0000, worst 0.0000, 0 pixels changed (identical)
    PASS gully/1600-low-sun/eye-on.png: mean 0.000000, p99.9 0.0000, worst 0.0000, 0 pixels changed (identical)
    PASS gully/1600-low-sun/high.png: mean 0.000000, p99.9 0.0000, worst 0.0000, 0 pixels changed (identical)
    PASS gully/1600-low-sun/into12.png: mean 0.000000, p99.9 0.0000, worst 0.0000, 0 pixels changed (identical)
    PASS gully/1600-low-sun/street.png: mean 0.000000, p99.9 0.0000, worst 0.0000, 0 pixels changed (identical)
    PASS gully/1750-blue-hour/eye-foot.png: mean 0.000000, p99.9 0.0000, worst 0.0000, 0 pixels changed (identical)
    PASS gully/1750-blue-hour/eye-on.png: mean 0.000000, p99.9 0.0000, worst 0.0000, 0 pixels changed (identical)
    PASS gully/1750-blue-hour/high.png: mean 0.000000, p99.9 0.0000, worst 0.0000, 0 pixels changed (identical)
    PASS gully/1750-blue-hour/into12.png: mean 0.000000, p99.9 0.0000, worst 0.0000, 0 pixels changed (identical)
    PASS gully/1750-blue-hour/street.png: mean 0.000000, p99.9 0.0000, worst 0.0000, 0 pixels changed (identical)
    PASSED /Users/oystein/code/Overstory/reviews/golden/compare/report.md

## For W4 and W5

- **Running the harness on the walk's scene.** Run `UNITY_LOCK_OWNER="<who>" zsh tools/perf.sh playable -runs 2`; it takes about 16 minutes a run, and the player takes the screen. The pass split's command is in `docs/measuring.md`, "The walk's whole scene"; it takes about 21 minutes for four views. Add `-perf-views` to cut views, and `-norun` to only build.
- **The walker's components.** `ComposePlayable` removes every `Overstory.Play` behaviour except `PlayCorner`. A W4 walker or key handler in that namespace is therefore left out of harness runs automatically. A walker elsewhere must be removed there too, or it will move the camera under the runner.
- **The views' indices.** `PlayCorner.views` is the five judging views (0 to 4), then `a-window`, `steps`, `row`, `anchor-door` (5 to 8). `LT1Play.Check` refuses any other order.
- **The beams' cost now:** 64 to 66 ms in low sun, 0 to 1 ms in the other lights. Low sun cannot reach 60 fps before 1c, so W5's walk should be judged in drizzle and at the blue hour. In those lights the frame is 21 to 37 and 17 to 32 ms (the views of the steps and the Anchor's door come nearest 16.7).

## For W6: the proper heart fix

`blender/blockouts/heart_layout.py` still casts A as a café:
- line 465 names it "A (104, café 1988)";
- line 752 gives it `shop="open"` (and `upper=0.4`).

The proper fix:
- set A's evening to no shop, from its diary;
- take HR 24's name from `fixtures/lt1-places-1989.json`;
- rebuild the heart and `lights.json`.

Two things still show A's false shop lights until then:
- the golden blue-hour frames, and so a new golden baseline is needed after the rebuild;
- the corner's own harness arm (`LT1Perf.Build`, staged by `LT1Stone.Stage`).

The walk's scene is right already. With the heart rebuilt, `ShopLights` should drop nothing, and its log will show that.

## Open problems

- The baseline's spread reaches 10.2% (the steps in low sun) against the 21 October acceptance of about 3%. The birch's A/B out of view is inside that noise.
- The four LT1g views are authored vantages. W4 or the walk with Øystein may move them; `a-window` was moved once already, onto the pavement at A's corner, because 0.7 m from the front its east wall filled half the frame.
- The materials' shaders' owner waits on L5.
