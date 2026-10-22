# W7: the self-check, the gate's baseline, the app

LT1g, Phase 1a, stage W7 (`reviews/lt1/playable/outline.md` §2), 22 October 2026, Opus 5.5. The last stage of the walk. W6 was cut. W7a (the walker's feel) was stopped before it compiled; its finding is recorded below. Everything here is in the commit that adds this report.

## In short

- **No strict review was run, on Fable or on Opus.** Øystein watched the walk's stills and a capture on 22 October and gave his own verdict, which stands as the review of the look:
  - the frame rate: "laggy and jumpy";
  - the climb: "a bit boaty";
  - the eye: "too close to the stairs at times";
  - the scale: "nice";
  - the tempo: to be taken from references;
  - the tree: "looks not good in game" (out of the walk until 1e, Q16);
  - the stairs: "very buggy and not nice", redrawn in the port's 2b (Q15).
- **The capture and the four stills were cut,** since Øystein had already judged the walk. The five views were rendered in three lights only to look for bugs and for the self-check (`w7/selfcheck-five-views-three-lights.jpg`).
- **The self-check** (table below). The gully's hashes hold (stairs `bff7858b698f3efd`, walls `0a3d7db3100df20b`). `CheckProxies` passes its six tests. The scripted walk A to E and back reaches 70 of 70 points with 0 falls and 0 sticks. Of the nineteen colour rules, five pass, four pass in part, seven fail and three cannot be judged yet. Every failure is known debt that 1c owns; none is new to this stage.
- **One bug found:** the underside of an eave on the drawn house at the left at the foot of the steps renders black in drizzle and at the blue hour, with a one-pixel light line across it in drizzle (`w7/crop-eye-foot-eave.jpg`). In low sun it is lit, so the faces are there; what is missing is light on down-facing faces. Shadows must go cool, not black. Owner: 1c (the sky and ground terms, L6 and L8).
- **The frame-rate gate's baseline** (no tree, the beams at a quarter of the pixels; `reviews/perf/2026-10-22/playable/w7/`). The frame is presented in:
  - 21 to 33 ms in drizzle (30 to 48 fps);
  - 22 to 36 ms in low sun (27 to 46 fps);
  - 17 to 29 ms at the blue hour (35 to 60 fps).

  At W3 this was 11 to 58 fps; now it is 27 to 60. Low sun went from the dearest light to drizzle's cost.
- **The three biggest costs now,** with owners (`w7/passes/passes.md`):
  1. the materials' shaders, 6 to 12 ms in every light (owner unknown until L5; the port's shader families, and 2b's stone for its share);
  2. the sun's shadow map, 4 to 7 ms in drizzle and low sun (1c);
  3. MSAA 4x, 2 to 5 ms (1c's pipeline, L3).

  W3's three were the beams (64 to 66 ms), the materials' shaders (9 to 14) and the card birch (11 to 17). The beams now cost about 1 ms, and the birch is out of the walk.
- **The baseline is noisy:** the two runs agree within 3% on only 10 of 27 segments, worst 14.3%. Other sessions' Blender, node and Claude processes ran beside it. A change under about 3 ms is not visible in this baseline.
- **The app is rebuilt** at `unity/Builds/Playable/OverstoryPlayable.app`. It opens, and its own shot shows the overlay reading frame 21.6 ms, worst 1% 28.6 (46 fps), at the foot of the steps in drizzle (`w7/overlay.jpg`).
- **Golden** at the start and at the end gives the same result. The 10 frames in drizzle and at the blue hour are identical. The 5 low-sun frames differ by W5's beams, mean 0.0002 to 0.0065, worst pixel 0.055 to 0.079. The baseline is not re-blessed; that is Øystein's call.
- **Open:** the walker's feel (below), which waits for the game; the black eave; the baseline's noise; the 0.5 ms beams target, still below what the harness can resolve; W5's faint seam on near depth creases.

## The self-check

The five views (eye-foot, eye-on, street, into12, high) in drizzle, low sun and blue hour, from `tools/playable.sh -method Compose -stills`, judged at native size and on the sheet. "Known debt, 1c" names the outline's light stage that owns it.

| Check | Result | Note |
| --- | --- | --- |
| 1. Light is the identity: the coast's lights and the night's | in part | Drizzle, low sun and blue hour are in. Summer and night are not; night is plan steps 3 and 6. |
| 2. Light is dramatic: deep shadow, little fill, rays | pass in low sun | Deep cool shadow, warm light, beams where the sun streams past the houses. Night is not built. |
| 3. A colour script keyed to facts | not yet | Today's three rigs are typed. Any hour from one record is L7. Known debt, 1c. |
| 4. One dominant colour of air, one warm accent | fail | Low sun is warm everywhere it is lit; drizzle has no accent. Known debt, 1c (L7's art keys). |
| 5. Every light in the town is a fact | pass | Lamps come from `lights-1989.json`. A's two shop lights are dropped, since A has no business in 1989 (`Check`). |
| 6. The sky designed from the hour and the weather | in part | Low sun and the blue hour have cloud bands flattened to the horizon. Drizzle's sky is one flat grey. Known debt, 1c (L6). |
| 7. Windows and lamps light the world round them | fail | No lit window or lamp spill shows in the five views at the blue hour. Known debt, 1c and night. |
| 8. Fog is a bank, not a filter | not yet | The five views show no water. The haze is a uniform fade with distance. Known debt, 1c. |
| 9. Shade sees the town | in part | The lanes' floors go cool in low sun, but the feet of walls do not darken more than open ground. Known debt, 1c (L6, L8). |
| 10. Drizzle is the default and the hardest test | fail | Drizzle is flat mid-grey clay and does not yet stand on its own. Known debt, 1c; the clay is greybox. |
| 11. Shadow and ambient colour from the light, never the object; shadows cool, not black | fail | Shadows go cool in low sun and at the blue hour, but the eave above is black in two lights. SEASON's light-only check needs L1's debug views. Known debt, 1c. |
| 12. Value first: four or five values, reads at one-eighth size | fail | Drizzle and the blue hour are mostly middle values with no white; low sun has its dark and its light. Known debt, 1c (L1's value view). |
| 13. Chroma placed, not spread | fail | The light's colour is spread evenly: orange wherever the sun falls, blue everywhere at the blue hour. Known debt, 1c (L7). |
| 14. A muted base with small saturated accents | fail | The base is muted, but there are no accents yet: no lit windows, signs or boats in view. Known debt, 1c and the kinds. |
| 15. White stays white | not yet | No white chip in the frames. L4 puts a grey and white chart in every sheet. |
| 16. Atmosphere does distance in layers | pass | The far houses step back in paler layers in every light. |
| 17. Weather wets what it wets | pass | Wet patches lie on the ground in drizzle only. |
| 18. Neutral tonemapping with our own grade | pass | The grade and moods are ours (`Style_game`); the tonemapper choice is L3's. |
| 19. Every colour difference also shows in value | pass | Nothing on screen yet carries meaning by colour alone. |
| The gully's hashes | pass | Stairs `bff7858b698f3efd`, walls `0a3d7db3100df20b`, recomputed from the FBX on every Compose and Build. |
| `CheckProxies` | pass | All six tests: 3,994 proxies, nosings within 1.49 cm, every door and way in the corner, the camera sphere, the clay under every box. |
| The scripted walk (`a-e-a.walk`) | pass | 70 of 70 points in 140.7 s; 0 falls, 0 sticks, 0 under the surface. Walker physics 53 µs mean, p99 299 µs, worst frame 2.4 ms. |
| The gate's numbers | recorded | Below, and in `docs/plan.md` ("Frame time today" and the frame-rate gate). |

**Looking for bugs.** I looked for holes, missing parts, black slots and lights where the facts have none, in the five views and LT1g's four, in three lights.
- No holes. No missing parts: the tree's absence is intended (`-tree none`).
- One black slot: the eave above. It is one house's down-facing faces with no sky or ground term, not a hole.
- No light where the facts have none. The specks in low sun are the air's motes, which belong to that light.
- At the Anchor's door at the blue hour, the Anchor's ground floor does not read as lit, though `heart_layout` lights it. Whether the frame should show it is a question for 1c's windows (rule 7), not a fault in the facts.

## The baseline

`UNITY_LOCK_OWNER="W7b" zsh tools/perf.sh playable -runs 2 -out reviews/perf/2026-10-22/playable/w7` builds the current walk scene: no tree, and the beams at a quarter of the pixels. Its own `-out` keeps W3's baseline in `reviews/perf/2026-10-22/playable/` from being written over. Each run took about 6 minutes.

Means of the two runs' medians, in ms:

| View | Drizzle offscreen | Drizzle frame | Low sun offscreen | Low sun frame | Blue hour offscreen | Blue hour frame |
| --- | --- | --- | --- | --- | --- | --- |
| eye-foot | 33.4 | 27.9 | 37.4 | 30.2 | 27.4 | 23.9 |
| eye-on | 38.8 | 33.0 | 41.6 | 36.4 | 32.6 | 28.6 |
| street | 29.5 | 23.9 | 30.8 | 25.8 | 22.3 | 19.5 |
| into12 | 30.0 | 25.1 | 31.2 | 26.4 | 23.1 | 20.2 |
| high | 29.3 | 24.4 | 30.4 | 26.1 | 22.3 | 19.7 |
| a-window | 31.3 | 25.7 | 34.1 | 28.4 | 23.9 | 21.1 |
| steps | 31.3 | 26.2 | 32.9 | 26.5 | 23.8 | 21.2 |
| row | 30.2 | 24.4 | 29.8 | 25.6 | 21.6 | 18.7 |
| anchor-door | 24.2 | 20.6 | 24.9 | 21.6 | 18.7 | 16.5 |

| Light | Offscreen (ms) | Frame (ms) | fps | Triangles | Draws | W3's offscreen (ms) |
| --- | --- | --- | --- | --- | --- | --- |
| Drizzle | 24.2 to 38.8 | 20.6 to 33.0 | 30 to 48 | 11.1 to 15.9 million | 117 to 142 | 24.2 to 44.0 |
| Low sun | 24.9 to 41.6 | 21.6 to 36.4 | 27 to 46 | 11.2 to 16.3 million | 121 to 149 | 86.7 to 107.3 |
| Blue hour | 18.7 to 32.6 | 16.5 to 28.6 | 35 to 60 | 3.7 to 5.7 million | 64 to 76 | 19.7 to 36.6 |

- **Where W3's numbers went.**
  - Low sun is 62 to 77 ms cheaper offscreen: that is W5's beams, which were 64 to 66 ms.
  - The street stop, 12 m and the city camera are 9 to 15 ms cheaper in drizzle and at the blue hour: that is the card birch, which was 11 to 17 ms where it was in view.
  - The views that never had the birch in frame moved by −4.6 to +0.4 ms, about the noise.
- **The dearest views** are eye level on the steps and at their foot, in every light. The gully's stone fills those frames, and its shaders are the dearest on screen (12 ms at the foot against 6 to 8 elsewhere).
- **The main thread** takes about 1 ms, so the frame is the GPU's.
- **Noise.** The runs agree within 3% on only 10 of 27 segments; W3 managed 22 of 36. The worst spreads are 14.3% (A's window, low sun) and 12.2% (12 m, low sun). `machine.json` shows other sessions' work through both runs: an interactive Blender, several node processes peaking above one core, Claude's renderer, and XprotectService at a full core before the run. A difference under about 3 ms is not visible in this baseline, so the next milestone's comparison should run on a quiet machine, or with three runs.

**The pass split** (one run, four views, `w7/passes/passes.md`; offscreen ms; a pass's cost is all on less all but that one):

| Pass | Drizzle | Low sun | Blue hour |
| --- | --- | --- | --- |
| The materials' shaders (bare less flat) | 6.2 to 12.2 | 5.9 to 11.2 | 5.9 to 11.0 |
| The shadow map | 4.4 to 5.9 | 4.0 to 7.2 | none |
| MSAA 4x | 2.3 to 4.8 | 2.2 to 4.8 | 2.4 to 4.1 |
| SSAO | 1.4 to 3.3 | 0.7 to 4.4 | 0.9 to 4.1 |
| SSR | 0.8 to 2.4 | 2.4 to 3.6 | 1.4 to 2.9 |
| Post | 1.1 to 1.8 | 1.2 to 3.8 | 1.1 to 1.8 |
| The beams | −0.2 to 0.5 | −0.0 to 3.0 | −0.3 to 0 |
| The four full-screen passes together | 1.1 to 2.7 | 3.7 to 6.0 | 2.0 to 2.7 |

## The three biggest costs, with owners

1. **The materials' shaders, 6 to 12 ms in every light.** Owner: unknown until L5 names the shader. Until then the cost sits with the shader families in the port's step 4. The gully's stone accounts for the 4 to 5 ms extra at the foot of the steps, so 2b's redraw meets that share (SN8's frame-time A/B per view). Bare is 7 to 14 ms; the same geometry unlit is 1.3 to 2.4.
2. **The sun's shadow map, 4 to 7 ms in drizzle and low sun,** and none at the blue hour, which casts no shadows. Owner: 1c. Without the old beams it no longer multiplies (W3: 31 to 34 ms with them).
3. **MSAA 4x, 2 to 5 ms in every light.** Owner: 1c's pipeline (L3). In low sun it was 8 to 13 ms beside the old full-size beams, and is now what it costs in the other lights.

SSAO and SSR (1 to 4 ms each, 1c) follow close behind. Third place is narrow: MSAA and SSAO overlap within the noise at A's window.

## The app

- `UNITY_LOCK_OWNER="W7b" zsh tools/playable.sh` composes, checks and builds in 15 s: compose and check 4 s, build 6 s. The log is `unity/Builds/Playable/build.log`.
- `OverstoryPlayable.app/Contents/MacOS/Overstory -shot <png> -shot-after 20` opened the build and wrote its frame with the overlay (`w7/overlay.jpg`). The overlay reads:
  - frame 21.6 ms, worst 1% 28.6 (46 fps);
  - CPU 0.7 ms;
  - GPU 33.5 ms;
  - 93 frames in 2 s, 2560×1440, MSAA 4x;
  - 1300-drizzle, walk.
- The scripted walk ran in the same build: `-walk tools/playable/walks/a-e-a.walk` gave `w7/a-e-a.csv` and `w7/walk-player.log`. Its `shot` stills were deleted after the check, since the stills were cut, so the CSV names PNGs that are not kept.

**The keys, as they stand in the build:**

| Key | What it does |
| --- | --- |
| W A S D, or the arrows | Walk at 1.4 m/s, or fly in the free camera. |
| Shift | Brisk, 2.2 m/s; 2.5 times as fast in the free camera. |
| Ctrl | 0.3 times as fast in the free camera. |
| Click | Hold the mouse to look (raw, unsmoothed). |
| Esc | Let the mouse go. |
| Q, E | Turn. |
| R, F | Tilt. |
| V | Free camera; V again lands on open ground. |
| Page Up, Page Down, wheel | Up and down in the free camera. |
| 1 to 5 (and the number pad) | The judging views: eye-foot, eye-on, street, into12, high. |
| 6 to 9 (and the number pad) | LT1g's views: A's window, the steps, the Row, the Anchor's door. |
| L | The next light: drizzle, low sun, blue hour. |
| M | The next mood (none after the last). |
| F1 | Hide or show the overlay. |

A view key holds the camera at that view. Any movement or turning key, the wheel or a click takes it back.

## The walker's boatiness, found but not fixed (W7a, stopped)

W7a was stopped before it compiled. The walker's feel waits until the game is chosen, since whether there is a walker at all is open. Its finding is recorded so it is not lost. It was measured on a motion capture and agrees with Øystein's "a bit boaty" and "too close to the stairs at times":
- **Pace reads the slope only once the feet are on a flight,** so the eye heaves up at each run's foot: a 4.4 m/s² jolt overshooting to 0.6 m/s, then sagging.
- **Two chained springs on eye height** float about 0.13 m past each run's top and dip at each foot.
- **The lean swings 6° to 15°** at every landing.
- **The eye drifts about 4 cm** after stopping.

The drafted fix: read the ground and slope a little ahead, on a smoothed ground line, and follow eye height with one stiff spring. W7a also saw golden differ at into12 in drizzle and at the blue hour while W5 was uncommitted. That was another session's transient: it was gone in W5's final golden and is not in this stage's two runs.

## Golden

At the start and at the end, the same result:

    PASS gully/1300-drizzle/* (5): 0 pixels changed (identical)
    FAIL gully/1600-low-sun/eye-foot.png: mean 0.000869, p99.9 0.0355, worst 0.0584, 69736 pixels changed
    FAIL gully/1600-low-sun/eye-on.png: mean 0.000233, p99.9 0.0204, worst 0.0624, 20534 pixels changed
    FAIL gully/1600-low-sun/high.png: mean 0.006536, p99.9 0.0377, worst 0.0552, 651815 pixels changed
    FAIL gully/1600-low-sun/into12.png: mean 0.002698, p99.9 0.0520, worst 0.0790, 281070 pixels changed
    FAIL gully/1600-low-sun/street.png: mean 0.002836, p99.9 0.0513, worst 0.0709, 201323 pixels changed
    PASS gully/1750-blue-hour/* (5): 0 pixels changed (identical)

The five low-sun frames are W5's beams, inside the range W5's own golden reported. Re-blessing the baseline is Øystein's decision (W5's sheet: `w5/golden-sheet-gully-1600-low-sun.png`). `LT1_Heart.unity`'s uncommitted change belongs to another session; its hash was the same before and after every run here.

## Files

- `reviews/lt1/playable/walk/w7-report.md` (this report).
- `reviews/lt1/playable/walk/w7/`:
  - `selfcheck-five-views-three-lights.jpg`;
  - `crop-eye-foot-eave.jpg`;
  - `overlay.jpg`;
  - `a-e-a.csv`, `walk-player.log`, `shot-player.log`.
- `reviews/perf/2026-10-22/playable/w7/`: `runs.md`; `run-1`, `run-2` (summary and machine); `passes/run-1` and `passes/passes.md`.
- `docs/plan.md`: "Frame time today" and the frame-rate gate's baseline, replaced.
- `docs/measuring.md`: the walk's baseline and pass costs, replaced.
- `docs/experiments.md`: LT1g's Phase 1a, keep and drop.
- `reviews/lt1/playable/premortem.md` §4: the note on W7's review.

## Open

- **The walker's feel** (above) waits for the game.
- **The black eave** goes to 1c, as rule 11's check in L1, with L6 and L8's terms.
- **The baseline's noise.** Run the next gate comparison on a quiet machine, or with three runs.
- **`tools/pass_budget.py`'s legend** still describes the beams as "40 shadow-map taps a pixel", which is the old pass. It is a one-line fix for whoever next touches the tool.
- **From W5:** the 0.5 ms beams target is below the harness's resolution, and there is a faint seam on near depth creases.
- **Golden's low-sun baseline** waits for Øystein.
