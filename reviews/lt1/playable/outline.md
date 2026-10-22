# The playable corner: the build outline

Phase 1 of LT1g, from `brief.md`, `pick.md` and LT1g's entry in `docs/experiments.md`. A fresh Opus session builds from it. The pre-mortem's fixes are in (section 7). Phase 2's build is replaced by a ladder of cheap tests (section 3).

Sizes are Opus-days. One Opus-day is about 8% of the weekly limit (6.5 to 9.5), from the usage log's 0.8 to 1.2% per build hour and the plan review's "two working days, 13 to 19%". Our estimates run long: the port was planned at 3 days and is 13.5 to 17.5.

## 1. What done looks like

**Phase 1a, the walk (Friday 23 October).**
- A Mac build in `unity/Builds/Playable/` opens on the corner at eye height in the clay town. WASD walks, V switches to the free camera, keys 1 to 5 jump to the judging views (`LT1Stone.Views`: eye-foot, eye-on, street, into12, high), and L cycles drizzle, low sun and blue hour.
- The gully is unchanged: stairs `bff7858b698f3efd`, walls `0a3d7db3100df20b`.
- The frame time is on screen. The harness's whole-scene run names the three biggest costs, and they enter the frame-rate gate in `docs/plan.md` as its baseline. The beams' A/B is measured.
- A one-minute capture and four stills at judged size are in `reviews/lt1/playable/walk/`, after the self-check and one strict Fable review.

**Phase 1b, the light and the grade (1c).** The four debts are closed by looking, not guessing. The rig is in layers with a hashed light record, the colour pipeline is in order, and exposure comes from illuminance. Every stage is shown in drizzle, low sun and blue hour, on clay and stone alike, beside target frames, and passes SEASON's check (below). The frame time is no worse than the walk's baseline beyond noise. Øystein walks it twice; one strict review comes at its end.

**Both, at the end:** keep and drop in `docs/experiments.md`, and `NOW.md` saying the port resumes inside this scene.

**Phase 2** is the ladder (section 3): five cheap tests, about one Opus-day, before any build is sized.

## 2. Phase 1, the walk

Rules for every stage:
- Unity and every Blender install into `unity/` run through `tools/unity_lock.py`.
- Nothing saves `LT1_Heart.unity`: the playable scene is a generated copy.
- Compose refuses to run if the gully's hashes differ.
- Each stage is one `LT1: …` commit, pushed.

### 1a, the walk (box 16, beams 3)

**W0. Preflight.** 0.1 d, 1%.
- *Checks:* the port's handover is in `NOW.md`; no Unity, perf-player or Blender process runs (by pid); the lock is free; `golden.sh` passes; both hashes go in the commit.
- *Risk:* the uncommitted change to `LT1_Heart.unity` belongs to another session. Its owner commits or drops it, never us, so this check comes first.

**W1. Compose the corner inside the town.** 0.7 to 1.1 d, 6 to 9%.
- *Builds:* `LT1Play.Compose` writes `Experiments/LT1/Playable/Generated/LT1_Playable.unity`: the heart's clay; `LT1Stone.Stage(grey: false)`'s stone, rigs and moods; the birch by `PlantBirch` at (44.5, 28.0); the five houses at 1989, placed from the `houses` offsets in `reviews/lt1/time/readers/diaries.json`.
- *The houses:* `export_time.py` gains `--years` and `--out`, and runs once with `--style stronger --years 1989 --out Assets/Art/Buildings/playable`. Øystein chose stronger; the time test's set is gentle. Other years wait until something asks for them.
- *Files:* `unity/Assets/Code/Editor/LT1Play.cs` (new); `blender/tools/export_time.py`; `unity/Assets/Art/Buildings/playable/manifest.json` (new); `.gitignore` (`Playable/Generated/`, `Buildings/playable/*.fbx`).
- *Reuses:* `LT1Stone.Stage`, `PlantBirch`, `LT1Time`'s placement, `StreetStage.Apply`. `LT1Perf`'s `Compose` and `BuildPlayer` are private and fixed to the perf scene (`Editor/Measuring/LT1Perf.cs:84, 164`), so they gain a scene path, with `perf.sh`'s summary unchanged on a rerun (0.1 to 0.25 d).
- *The facts first:* test 5's fixes (section 3) go into the diaries before the export runs: E's "empty when its last owner dies (1993)" and D's heirs in Oslo contradict the case and the export (0.1 d).
- *Ends in:* a batch check printing the gully's hashes, 5 houses, 1 birch and 3 rigs, and stills at the five views in drizzle.
- *Risk:* `Stage` opens HeartScene, so Compose saves only by explicit path into `Generated/`.

**W2. The number first: the overlay and the build.** 0.25 to 0.4 d, 2 to 3%.
- *Builds:* `unity/Assets/Code/Play/FrameTimeOverlay.cs` (new): CPU and GPU ms from `FrameTimingManager`, mean and worst 1% over 2 s, the light and view; F1 hides it. `LT1Play.Build` writes `unity/Builds/Playable/OverstoryPlayable.app` at 2560×1440 (the size `PlayerFrame` judges at; the class itself is editor-only), MSAA 4x, through `BuildPlayer` with W1's scene path.
- *Ends in:* the app opens and the overlay reads. Compose plus Build is timed once, into `docs/measuring.md`, as the plan review asked.

**W3. The harness's whole-scene run.** 0.55 to 0.65 d, 4 to 5%.
- *Builds:* `PerfRunner.cs` gains `-perf-scenes playable`, and `tools/perf.sh` a `playable` arm in timing mode. It measures the five judging views and LT1g's four views (A's window, the steps, the Row, the Anchor's door) in three lights. `tools/pass_budget.py` splits the passes.
- *The Anchor:* `heart_layout` has none, and `corner_blockout.py`'s 101 is an older layout. W3 casts the Anchor (`pl-bar`) and its door in `heart_layout`, labelled authored (0.1 d).
- *One more arm:* beams and shadows both off, to split the low-sun cost (0.05 d).
- *Ends in:* `reviews/perf/2026-10-23/playable/`, and the three biggest costs, each with its owner, in the plan's frame-rate gate.
- *Risk:* noise reaches 16.6% on the whole corner, so A/Bs under a millisecond run alone. The suspects: the beams, 64 ms in low sun (1c); the opaque shaders' 12.5 ms, owner unknown, since the haze is at most 1.5 ms (`reviews/lt1/history/r2.md:60`; 1c, L5); the birch, 10 to 16 ms (1e); MSAA, 5 to 6.5 ms (1c's pipeline). The port keeps its own order.

**W4. The walker.** 0.6 to 0.9 d, 5 to 7%.
- *Builds:* `Code/Play/Walker.cs` (new), a kinematic `CharacterController` (built-in physics, no package) at the eye views' height, step offset 0.25 m. From `play-craft.md`: 1.4 m/s, 2.2 brisk on Shift, 0.55 times up a flight and 0.6 down, no bob, a 0.12 s input spring; V toggles the free camera (`CameraShot`). `Code/Play/PlayKeys.cs` (new): 1 to 5 the judging views, 6 to 9 LT1g's four views, L the lights, M the moods.
- *Proxies,* item 4 of `collision-and-navigation.md`: houses and walls as boxes; flights as ramps from the stair generator's sidecar (`blender/generators/stone.py`, `stair_stages.py`); the clay ground as one mesh collider per 64 m; a camera layer; a record id on every proxy. `LT1Play.CheckProxies` runs the study's test 4.
- *Ends in:* `CheckProxies` passes; a scripted walk from A's door to E's and back neither falls nor sticks; physics stays under 0.5 ms.
- *Risk:* the clay's mesh colliders leak or cost too much. The fallback is boxes from `heart_layout`'s footprints.

**W5. The beams' A/B (1c's first item, L0, box 3).** 0.4 to 0.6 d, 3 to 5%.
- *Builds:* `SunBeams.shader` and its feature (`PC_Renderer.asset`, `StreetStage.cs`) at a quarter of the pixels: 12 to 16 steps, one hard tap, blue noise, a depth-aware upsample.
- *Ends in:* an A/B in low sun from eye-foot to high, with harness numbers. The target is about 0.5 ms, from 64.
- *Risk:* a quarter of the pixels can shimmer in motion, so a `tools/motion.sh` sheet at the gully decides, not a still. Golden frames change in low sun only; that diff goes to Øystein with the walk.

**W6. The clay audit and extension.** 0.25 to 0.5 d, 2 to 4%. Cut first.
- *Builds:* steps 1 and 2 of `town-plan.md`'s order in clay checked against what `heart_build.py` exports; step 3 (the villas, Tower Wood, the heath, the water tower) added where `heart_layout` already holds it. The walk stays inside the fine heart, with the painted far town beyond. No clay changes in sight of the gully's golden views this week.

**W7. Self-check, review, Friday.** 0.3 to 0.45 d, 2 to 4%, plus Fable's own cost.
- The self-check covers colour rules 1 to 10, the gate's numbers and the hashes. The lean packet is the capture, four stills at judged size with native crops, the harness summary and the beams' A/B. One strict Fable review, then fixes.
- *Capture:* the build plays a scripted one-minute walk to a PNG sequence through a runtime frame grab (`ScreenCapture`; `PlayerFrame` is editor-only). ffmpeg is already bundled in `.venv` by `imageio-ffmpeg` (`docs/measuring.md:330`), so it becomes a film.
- *Øystein judges* whether the corner holds at eye level as he walks, in three lights; whether the climb feels right; whether the beams are right.

**Total for 1a:** 3.15 to 4.7 d, 25 to 38%, against a box of 19.

### 1b, the light and the grade (1c), interleaved with the walk

Each light stage ends in the rebuilt walk, so Øystein's walk is where it is judged, and in a whole-scene harness run with no regression beyond noise. The lock passes to the port's 2b, or any other Unity user, only at stage boundaries. 1c owns the light code in `Code/Scenes/`, the sky, palette, beam and fog-light shaders, the light terms of `OS_ShadeP` in `StreetSurface.hlsl`, and the rigs in `Experiments/LT1/Heart/Light/`. Sheets go in `reviews/lt1/light/` (new).

**SEASON's check, at every stage** (`colour-and-shading.md`, the core rules):
1. **Shadow and ambient colour come from the light, never the object.** In the light-only view (every pigment one grey), a shaded clay face and a shaded stone face with the same facing and place differ by under 0.02 OKLab ΔE. A grep finds no material with its own shadow tint.
2. **The grade acts on the whole light.** `Grade.cs` and `Palette.shader` read only the frame, never a material or object. Style and target LUT are one table after the tonemap.
3. **Three lights at least:** drizzle, low sun and blue hour at the five views, clay and stone in the same frames, colour and light-only beside the target frames, at judged size.
4. **Value first, white stays white:** the value view's five bands, and a white chip in every sheet.

**LA. The light's range, on paper** (Øystein, 22 October: "we need to build for the future. do one thing right one time, instead of medium many many times"). 0.5 to 1 d, before L1 fixes the light record.
- **The craft of two regimes the corner doesn't show,** studied only far enough to shape the format and the shade's terms, and not built here:
  - light under a canopy: sun flecks, sky seen through leaves, light coming through them (the Firewatch reference);
  - many lamps at city scale on the reference machine.
- **Five written cases:** the Row at blue hour; a birch wood at a summer noon; open heath in drizzle; a dense street at night with many lamps in view; snow at low sun.
- **The check:** L1's light record and the shade's terms give each case a place, line by line, so later regimes add terms and keys instead of a rebuild.
- **Where findings go:** `docs/research/lighting-and-colour.md` and the coverage row in `docs/systems.md`.

**L1. Measuring the light.** 1.5 to 2 d. Debug views of the shade's terms (albedo, light alone, sky, ground and town bounce, sun, lamps, reflections) and a false-colour value view, keyed in the build. The light record (`schemas/light-record.schema.json`, `Code/Scenes/LightRecord.cs`, both new), saved and hashed with every sheet: the format first, since it is hardest to change. *Ends in* the four debts re-measured as numbers. *Risk:* shader variants multiply, so the debug keywords are stripped from the player.

**L2. Target frames.** 1 d. Drizzle and blue hour at eye-on and street, painted with `blender/tools/paintover.py` over L1's renders at judged size, beside `reviews/lt1/heart/target/3-street-gully-steps-target.png`. Fable judges them before Øystein sees them.

**L3. The colour pipeline in order.** 1.5 to 2.5 d. The style baked into Color Lookup. Dither at the last write, taking the still-camera shimmer from 0.47 levels to under 0.1 on `motion.sh`. Neutral against a hue-preserving table on the night frames (the tonemapper is ours to decide). MSAA's cost weighed here if W3 names it. Unity's `urp-postprocessing` skill is the reference for the Volume and lookup settings.

**L4. Exposure from illuminance.** 1 d. A grey and white chart in every sheet, so white staying white is measured.

**L5. The opaque shaders' 12.5 ms.** 0.25 d. Its owner is unknown: the haze is at most 1.5 ms (`reviews/lt1/history/r2.md:60`). A flat A/B per shader on the quad names it, and the gate carries it as "owner unknown" until then. Øystein walks the first light build here.

**L6. The sky as the source of the ambient (debt 1).** 3 to 5 d. CIE overcast with a sun indicatrix in drizzle, a Hillaire-style clear sky otherwise, the hemisphere terms derived whenever the light changes (`SkyMap.cs`, `Sky.shader`, `Daylight.cs`, `Code/Scenes/SkyModel.cs` new). *Ends in* an upright cylinder with a lit side under overcast. *Risk:* the largest, least-known item; its size is known only once it runs.

**L7. The rig in layers.** 3 to 4 d. World state, derived light, art keys (OKLCH pushes by hour, blended by weather, sparse overrides per place), then style, mood and lens; about 65 typed settings become a dozen pushes. *Ends in* today's five rigs re-expressed as keys and matched to today's judged frames before anything moves; then any hour from one record, a December day and its dusk included.

**L8. Bounce by looking (debts 2 and 4).** 1 to 2 d. The seen ground (the sun's shadow at the ground in front of a face; ground albedo by season and wet) and the seen town in `OS_TownSky`. Judged in low sun at the gully and on the Row. Any new render pass is checked with Unity's `validate-urp-render-graph-renderer-feature` skill before it is timed.

**L9. Occlusion done right (debt 3).** 0.5 to 1 d. GTAO, no occlusion on the sun (`DirectLightingStrength` 0.25 to 0), `GTAOMultiBounce`, specular occlusion from bake × town × AO.

**LR. Self-check, strict review, Øystein's second walk.** 0.5 d.

**Committed first:** LA, L1 and L2, 3 to 4 d. The rest is re-sized from the gap they show (the plan review's P3) before L3 starts.

**Total for 1b:** 13.75 to 20.25 d, 110 to 162%, with LA. Cut first: the seen-town half of L8; specular occlusion; the hue-preserving comparison; last, L6's clear sky (low sun keeps today's typed sky).

**Night is not in 1c.** Night in tiers (item 8, 5 to 8 d) stays with plan steps 3 and 6. Night after the blue hour is unmeasured; in Stavanger in December the sun sets about 15:35, so most of a winter day's play would fall in dusk or dark. Until night lands, it is the blue-hour rig carried on with the 1989 lamps from `TownLights`, labelled a stand-in. The case's November evenings and its Friday after 16:00 fall in the dark, so test 2 (section 3) checks this first, on stills. If it fails, the visits move into daylight (labelled), which costs nothing; night moves into 1c only if a case still needs it, with that failure as the evidence.

## 3. Phase 2: what to test first

Øystein ruled on 22 October that Phase 2's build, about 16 Opus-days in the pick, is too much to commit to before we know what to test. In its place is a ladder of five cheap tests of the pick's risks.
- Together they cost about one Opus-day, 8% of the weekly limit, plus an hour of Øystein's.
- None needs the command port, the solver, the bots, agent players or replays.
- The testing design and the case's build are sized only if the ladder passes, as their own decision with Øystein. The pick's 16 days is not a commitment.

This outline plans nothing for the case's build. No stage in Phase 1 serves only Phase 2: W3's and W4's four views are LT1g's judging views, and the house export takes 1989 only.

**The ladder's rules.**
- **The pre-mortem first.** Its open fixes (`premortem.md` §4) go into `case-spec.md` before it is frozen. Test 4 uses one of the run's deaths that Øystein has not read about.
- **Freeze, then test.** The spread rule, the score and the authored hours are written in `reviews/lt1/playable/case-spec.md` and hashed before test 1 runs. A change after any result is a new case. It reruns on seed B, which nothing is tuned on.
- Each test reports against the pass line written here before the next one starts.
- A kill stops the ladder. Its evidence goes to Øystein as a scope question, not as a fix.
- Scripts go in `tools/playable/`, and results in `reviews/lt1/playable/ladder/`.

### The risks, ranked by the work each could invalidate

| Rank | Risk | What it could invalidate | Test |
| --- | --- | --- | --- |
| 1 | The first telling is no decision | the spread, the score, the ledger and the Friday: the case's play, most of the 16 days | 1, the tie script |
| 2 | The clue is not in the pixels | the window phase, the screen's claim over the page (gate 3), and night pulled into 1c (5 to 8 days) | 2, sight and stills |
| 3 | The page does as well | the experiment's question | 3, two cold readers |
| 4 | It is not play | the case as a game | 4, Øystein's paper run |
| 5 | The case contradicts the export | W1's houses, the case's homes and roles; small to fix, but test 1 stands on it | 5, the facts check |

### 1. Is the first telling a decision? The tie script

**Rung:** a number, from the export alone. Plain Python, `tools/playable/ties.py`.
- **The tie table, for December 1989,** from the export only, each row with its source:
  - kin from parents, kids and dated partners;
  - coworkers from places, rebuilt to 1989 from hired, retired and left events (the export's staff lists are 1999's);
  - friendship and liking from the pair events up to that month: friends, confide, keep, cold, coolto, dislike, contempt.
  - The export has no liking field, so liking is read as the sign of those events, and the table says so.
- **What is already in view.** By December 1989, Hannah's ties are Agnes, Ben Reed (e-6400) and her son Sid. Olive has ties to seven people and three children, Peter Lane among them. The two women are joined only through Ben, so whichever is told second may hear it from him first. The events start only in January 1989, so the graph is thin.
- **Every line is tried:**
  - the 27 vantage plans (three evenings, three vantages);
  - every first telling;
  - every order of up to four tellings the clock allows, with walking minutes from `heart_layout`.
  - Each is scored by the pick's rule. The page's line (the Anchor's lead first), Peter first, and Hannah then Olive back to back are reported by name.
- **Seed B** (Andy Shaw, October 1998) is run the same way. His three visitors share the 80 points equally; the pick left his score undefined.
- **The sweep:** each spread parameter at half and at one and a half times its value.

**Pass,** on both seeds:
- the branches at the first telling (Hannah first against Olive first) differ by at least 16 of 80;
- the best line beats the page's and Peter-first by at least 16;
- telling the two back to back is not the best line;
- the page's line spreads to at least six people by 18:00, so the fail state exists;
- the ranking of the named lines holds across the sweep.

**Kill or change:**
- The first-telling branches within 8 of each other on both seeds means the order is free, so there is no decision. The case changes its cost once, by the clock or the rule, and is frozen and rerun on seed B. If it is still flat, the case goes back to the pick (B's attention grammar).
- A ranking that flips inside the sweep means the rule is tuned, not designed. It is rewritten from one stated principle.
- Fewer than six reached from the page's line means the spread is invisible. Either the spread runs along the town's Friday (authored hours, labelled), or seed B leads.

**Cost:** 0.3 d, 2.5%. The script is also test 4's referee.

### 2. Is the clue in the pixels? Sight, then stills

**2a, a number, Unity-free.** `tools/playable/sight.py` works over `heart_layout`'s footprints and the walk's camera (2560×1440, the eye views' field of view). For each vantage (the café window at A, the Row, the Anchor's door) it gives:
- the share of Hannah's climb, past her own door to E's, that is in line of sight;
- a figure's height in pixels along the climb;
- the sun's height at each authored hour, at the town's latitude.

The sun sets at about 16:05 in mid-November and 15:40 in mid-December, so November's evenings and Friday after 16:00 are dark. 0.05 d.

**2b, stills from the walk, under the lock, after W7.**
- A list of poses places plain capsules, unlabelled, at the authored visit hours. Each capsule's coat colour is seeded texture.
- The stills are taken in the light those hours really have, with blue hour as the night's labelled stand-in, and in drizzle.
- Each evening's vantage gets three stills: leaving the door, mid-flight, at E's door. Friday 16:30 on the Row gets one more.
- All are at judged size, with native crops. This is capsules and a camera, not the people movers. 0.2 d.

**Pass:**
- 2a: at least one vantage sees both doors and most of the climb;
- 2b: test 3's reader A says which door each figure left and which it entered, from the stills alone.

**Kill or change:**
- Wrong or "can't tell" at the real hours: the visits are authored into daylight, as a Saturday afternoon (labelled). This costs nothing to build, and Phase 1's night section stays as it is.
- Daylight fails too: the vantage moves, for example the window becomes the steps' foot.
- If no vantage works, the clue is not in the pixels, gate 3 fails, and the case goes back to the pick.

**Cost:** 0.25 d, 2%.

### 3. Does reading beat the page? Two cold readers

**Rung:** stills and text, read by a model.
- **The readers:** two fresh, blind readers on Sonnet, the other model from the designers. They are never told the answer.
- **Reader A** gets the page and 2b's stills. The page is what the player can read: the public and local records on Agnes and the corner, and the homes (authored).
- **Reader B** gets the same page only. With the homes in front of them, "tell the neighbours" is the page's best guess, and that is the guess to beat.
- **The questions,** the same for both:
  1. which door each figure left and entered (reader A only);
  2. who were Agnes's people in her last month, with a source for each;
  3. whom you tell first, and why;
  4. what you would say;
  5. what you are unsure of.
- **Scored:** names right and sourced; causal claims made without a source; the first telling.

**Pass:** A names Hannah from the steps and Olive, each with a source, and invents nothing. B does not name Hannah, or names her only as a guess marked unsure.

**Kill or change:**
- B names both from the page with confidence: the screen adds nothing. The homes or the page change, or gate 3 fails.
- A reads the climb as something false (an affair, a paid carer) or invents causes: the stills or the vantage change before test 4.
- A split verdict gets a second pair.

**Cost:** 0.1 d, 1%.

### 4. Is it play? Øystein's paper run

**Rung:** paper and a script, in one sitting under an hour, refereed by test 1's script in a play mode. Never refereed by a model.
- **The materials:**
  - the corner's map, with the homes and the walking minutes;
  - a card for each person, with the export's ties only;
  - three evenings, each with a vantage chosen in advance and sealed, then shown as 2b's stills from that vantage;
  - the Friday clock track;
  - the exposure ledger at the close.
- **The script** takes his tellings one at a time and prints only what he could see or be told.
- **Afterwards he answers four questions,** once, in his own words:
  1. Was the vantage a bet?
  2. Did the first telling cost something?
  3. Did failing feel fair?
  4. Would he play seed B?

**Pass:** he names the tell-order trade-off unprompted and wants seed B.

**Kill or change:** these are the pick's own "what would change our minds":
- he calls the evenings watching;
- the Friday has an answer he sees without a trade-off;
- failing feels random.

**Cost:** 0.25 d, 2%, plus his hour.

### 5. Do the facts agree? The facts check

**Rung:** a script and a read, `tools/playable/facts.py`, over the export, the five houses' diaries (`reviews/lt1/time/readers/diaries.json`) and the case's authored layer. Every fact the case states is checked:
- **The town has one café in 1989,** the Old Bank Café. Its owner is Peter Lane of C (e-6545; he retires from it in 1992, e-7137). A café at A run by the player would invent a business. The player is cast at A without one, or works at Peter's, and then "Peter first" changes meaning.
- **Olive is at the Anchor in 1989:** she retires in 1998 after ten years (e-8736). The Anchor's 1989 lead is rebuilt, since Evan Newman leads it in 1999.
- **E's diary,** "empty when its last owner dies (1993)", against Agnes's death in December 1989.
- **D's diary,** boarded in 1986 for heirs in Oslo, against Ken and Jonah Scott working in the town.
- **Seed B's houses in 1998** against Andy Shaw's case.

**Pass:** every contradiction has a fix that changes only our authored layer (a diary's wording, a home's casting), each with its cost.

**Change:** the fixes go into W1, before the house export.

**Kill:** a contradiction only the engine could settle, such as a home or job the export rules out. The case is re-cast before test 1 runs.

**Cost:** 0.1 d, 1%.

### The order and the total

1. **Now, beside the walk, Unity-free:** test 5, then test 1, with 2a alongside. 0.45 d.
2. **After W7, under the lock:** 2b, on the walk's build. 0.2 d.
3. **On 2b's stills:** test 3. 0.1 d.
4. **Last:** test 4, Øystein's sitting. 0.25 d.

**Total:** 1.0 Opus-day, about 8% of the weekly limit, plus Øystein's hour. The box is 8%, and the cut line 12%.

**What the ladder does not answer:**
- whether an agent can play it;
- how people other than Øystein misread it;
- whether it holds at length;
- the cost of the people movers.

Those wait for the sizing decision.

## 4. Order and dependencies

0. **The pre-mortem,** by a fresh reviewer on Opus, done 22 October (`premortem.md`). Its fixes are in (section 7).
1. **Thursday and Friday:** W0 to W7, all under the lock. Nothing else touches Unity.
2. **From the week of 26 October:** L1 to LR under the lock, alternating with the port's 2b at stage boundaries. Each Unity stage starts and ends with `golden.sh`, and a diff that is not the stage's own fails it.
3. **The ladder** (section 3): tests 5, 1 and 2a are Unity-free and run now, beside the walk; 2b runs under the lock after W7; then tests 3 and 4.
4. **Unity-free:** L2's painting (`paintover.py` is plain Python over the passes `LT1Heart.TargetPasses` renders under the lock), the light record's schema in L1, and the review packets. Everything else in Phase 1 needs the lock.
5. **Øystein's walks** use the built app, not the editor. Timed runs wait until he has closed it (the lock's timing mode does not see him).

**The fidelity ladder in Phase 1:** a number before a render (W2's overlay and W3's run before W4's walker); grey form before colour (every light stage's light-only view before its colour sheet); a still before motion, except the beams, where motion decides. Parallel work saves calendar time, not limit: at most three sessions at once (`NOW.md`), one weekly limit.

## 5. The honest total

The box is the plan's figure, else my low end; the cut line is 1.5 times it.

| Phase | Box | Honest estimate | Cut line (1.5× box) | Cut first, in order |
| --- | --- | --- | --- | --- |
| 1a, the walk | 19% (2.4 d) | 3.15 to 4.7 d, 25 to 38% | 28.5% | W6; the capture as a film; W5's motion sheet down to one view |
| 1b, the light | 13.75 d, 110% | 13.75 to 20.25 d, 110 to 162% | 20.6 d, 165% | the seen-town bounce; specular occlusion; the hue-preserving test; L6's clear sky |
| 2, the ladder | 8% (1 d) | 1 d, 8%, plus Øystein's hour | 12% | test 3's second pair; seed B in test 1 last |

1a's estimate is above its box by itself, so its cut line falls inside the estimate: W6 goes as soon as the running total passes 19%, and at 28.5% the walk stops for a re-plan in `NOW.md`. The same holds for 1b at 159%, and for the ladder at 12%.

**When the size will be known.** 1a by Friday. 1b after L6, the sky, its least-known item.

Together, Phase 1 is 16.4 to 24 days, about 1.3 to 1.9 weeks of the weekly limit, whatever runs beside it. The ladder adds one day.

## 6. Open questions

**Ours:**
1. Clay mesh colliders or footprint boxes? Known at W4.
2. Iteration time for Compose plus Build. Known at W2.
3. Whether the beams hold at a quarter of the pixels in motion. Known at W5.
4. Who owns the opaque shaders' 12.5 ms. Known at L5.

**Øystein's (scope and permissions only):**
1. **Golden frames:** may each light stage's frames serve as the working regression reference until you accept them at your first light walk (L5) and at LR? Recommended: yes. Only you accept a baseline.
2. **The player's place at A** (a play question, from test 5): the town's one café in 1989 is Peter Lane's, so the player cannot run a café of their own at A. Should the player work at Peter's café, which makes him the employer you would tell first, or live at A with no trade? Test 5 lays out both; you choose before test 1 freezes.

## 7. Changes after the pre-mortem

The pre-mortem (`premortem.md`, Opus, 22 October) checked the outline against the code. Its claims were checked again here before applying:
- **`LT1Perf` reuse:** `Compose` and `BuildPlayer` are private and fixed to the perf scene. They gain a scene path (W1). `PlayerFrame` is editor-only, so W2 takes only its size, and W7's capture uses a runtime grab.
- **The Anchor:** `heart_layout` has none, and `corner_blockout.py`'s 101 is an older layout. W3 casts it, labelled authored.
- **The haze:** it costs at most 1.5 ms, not the 12.5 ms of the opaque shaders. W3 names that cost "owner unknown", and L5 becomes a per-shader A/B (0.25 d, down from 0.5 to 1).
- **ffmpeg** is already bundled in `.venv`, so its question to Øystein is gone.
- **False history:** E's and D's diaries contradict the case and the export. Test 5 finds every such contradiction, and W1 applies the fixes before the house export.
- **W3** gains an arm with the beams and shadows both off.
- **The dark:** the case's evenings fall after sunset, so test 2 checks the clue on stills at the real hours before any night work.
- **Phase 2's must-fixes** (the perception rule, the decision audit, freeze then test, one seed before two) become the ladder's rules and tests 1 and 2. The rest wait for the sizing decision.

1a grows from 2.75 to 4 days to 3.15 to 4.7, and 1b falls by a quarter to three quarters of a day.
