# The plan

The order of the work and the current week's plan in detail. `NOW.md` holds the state and links here; update this page when a step starts or ends.

## In short

- **PL1** Steps 1–10: stone, buildings, ground, years, people, city, nature, interiors, weather, region. Evidence: The order. Reopens: a proposal.
- **P2** Done: holds its range (variety, levels, three lights, 1-spp motion, town count, budget), walked in 1g, at the bar, Øystein accepts. Else its rung: number, grey form, sheet, levels, motion, count, three lights, accepted; never "close". Evidence: plan review. Reopens: unnameable ranges.
- **P1, P9, P3, P7** Milestones: walked in 1g, timed whole. The first walk is the baseline, clay counting as scope; an unscoped rise stops the step; hold or fall until under 16.7 ms at every judging view in three lights. 1.5× a box forces a re-plan; no dates past the next milestone, re-estimated at the stone or 13 November. Evidence: the same. Reopens: walk over 1.5×, 16.6% noise, re-plans from boxes.
- **P8** Port steps 4 and 5: done when a House A front, a birch chunk and a 64 m land chunk with water validate unbuilt; formats change only where a record fails, no field without one. Evidence: `foundation-needs.md`. Reopens: none named.
- **PL2–4** 1g's time: stroke by stroke, the toggle as baseline, the photograph close only. Evidence: 1g. Reopens: more readers.

## This week (22 to 26 October)

Written by the plan review of 22 October (`docs/research/plan-review-2026-10-22.md`). From Monday 26 October, the Monday session rewrites this block from `NOW.md`'s order.

**Friday 23 October's milestone** is a Mac build Øystein walks, on whatever is honestly complete:
- the clay town, with the corner inside it at today's quality;
- whole-scene frame times at the judging views in three lights, taken under the Unity lock's `--timing` (or by hand on a quiet machine, and said so);
- the first case and the testing design, picked (`reviews/lt1/playable/brief.md`, phases 0 and 1).

**The boxes** are in per cent of the weekly limit, from `docs/usage-log.md`'s unit costs. 48% was left at 07:45 UTC on 22 October, and the limit resets on Monday 26 October at 12:00 UTC.
- the playable corner's phase 0, the design: 5 (no Unity, run in parallel);
- its phase 1, the walk: 16;
- 1c's A/B on the beams, on the walk's first whole-scene run: 3;
- the In shorts, with `CLAUDE.md` halved into its skills and `NOW.md` brought under its budget: 2;
- the rest is reserve.

A step that reaches 1.5 times its box stops for a re-plan (P3), a few lines written beside it in `NOW.md`. Øystein is told only when a re-plan moves a milestone or the scope.

**Then, on the stone's path:**
1. 1c in the walked corner, beams first, with the port's 2b beside it on the Blender side;
2. the strict review of the port's steps 0 to 2, against the target frame;
3. R3 to R7;
4. `reviews/lt1/port/foundation-needs.md`, read before the port's step 4 opens.

The play, the brief's phase 2, is the milestone after the walk. It is boxed and runs beside 2b.

**Every week** (P7):
- Monday, after the reset: one session writes this block from `NOW.md`'s order, with each step's box. It also checks the warning signs in the pre-mortems (`docs/research/pre-mortem.md`, `pre-mortem-architecture.md`, `plan-review-2026-10-22.md`).
- Friday: Øystein walks the corner and plays whatever case exists.
- One strict review per milestone, never per round (Fable, or Opus if Fable is out, noted).
- The top of `NOW.md`, kept under its budget, is the one status source.

## Standing notes

**Baselines (measured 22 October on the M4):**
- The house generator at test quality built and checked 129 buildings in 10.2 s (50 random diaries at four years, Blender's start included), about 13 a second.
- The gully's flight at final quality takes 67 s and makes one 16 MB FBX, without its walls.
- One stair with its walls is about 816,000 triangles.
- The repository is 2.2 GB of git history. Unity holds 407 MB of art, 373 MB of it in 222 FBX files, 272 MB of that stone.

**Frame time today** (the harness, 21 October; `docs/measuring.md`): the corner runs at 28 to 42 ms in drizzle, 84 to 96 ms in low sun, and 25 to 35 ms at the blue hour. That's 10 to 40 fps against the 60 fps target.
- About 15 million triangles a frame with sun shadows, and 5.5 million without.
- Something drawn only in low sun costs about 55 to 65 ms; the sun beams are the suspect.
- The birch costs 10 to 16 ms in view, and 25 ms when it fills the frame.
- URP's dither is redrawn every frame, so a still camera shimmers by about half a level. That is decided with the light (1c).

The walk's first whole-scene run replaces these as the baseline (The order, the frame-rate gate).

At today's rate a thousand stairs would take about 19 hours to generate and 16 GB of FBX. The architecture must change how they are made, not tune them.

**The gully's port:** its steps and estimates are in `docs/research/building-blocks-decisions.md` §13, and what is done and what is left in `reviews/lt1/port-handover.md`.

**What the architecture decides** is written once, in `docs/building-blocks.md`: the stages, the contracts, ids, what every part carries, levels, budgets and what changes in existing work.
Its reasons are in `docs/research/building-blocks-decisions.md`, and its open numbers in its table "Open until measured".
The questions left for Øystein are in `NOW.md`.

**Leaner without losing brilliance** (PL3; Øystein, 22 October: "we need to make the game leaner, I fear; is it possible without losing visual brilliance?"). The proposals and where each stands:
1. *Paint the far town:* past about 50 m, a painted backdrop baked from the near models for each date, instead of distance versions for every kind. Øystein: "I would have to see this, but sounds promising." It becomes a look test in the foundations, designed in `docs/research/painted-far-town.md`. A single painted picture can't survive a free camera, so the design is painted shells: each thing a coarse mesh from its plan, in 32 m cells, carrying painted albedo, normals, history channels and ids, lit live by the town's one shade function. Four versions are compared (a reference, conventional distance levels, unpainted shells and painted shells) in the corner's views and three lights, with motion sheets, M4 timing and cold readers. Six named results would make us drop it.
2. *Make the 1989 town once,* curated, with records by rule, instead of growing two centuries plot by plot. Decided (Øystein: "as long as we can change this later"). The 1989 town is stored as records that can be regenerated, edited, or replaced later by a growth simulation or by the engine's own past. It also removes the pre-mortem's risk that Overstory becomes the engine.
3. *Libraries only where things were factory-made:* each house type and era gets its own kit (decided; see `NOW.md`).
4. *Concentrate the history:* the full set of history layers goes where a view's stories are; elsewhere one shared weathering bake (rain, sun, years, care) keeps every surface true but quiet. Decided (Øystein: "as long as we can build this out later"). The architecture designs the layer stack so specialised layers (soot, salt, rust runs, carried stains, splash bands, failing coats) can be added to any kind later without rebuilding it: a registry of layers, reserved channels in the history maps, and the shared bake as the base every layer sits on.
5. *A dense town, not a metropolis, for now:* decided.
6. *Moods:* withdrawn. The lighting study's way is already the leaner one: the light derived from a sky model for any hour and weather, with a few art keys on top, replaces about sixty-five hand-typed settings an hour. Every hour and weather then comes nearly free, and a mood is a set of art keys.
7. *People:* their own research project with great care (Øystein). No shortcut.
8. *Eye level for every part:* open. The cost of eye level is measured per kind during the gully port and the first house, then decided with numbers.

Also: build more, write less. Docs only where a decision needs recording; the building blocks proven in code and frames.

**From the pre-mortem** (`docs/research/pre-mortem.md`, ranked failure stories; on Opus, to be checked by Fable; the architecture's own pre-mortem is `docs/research/pre-mortem-architecture.md`):
- a half-page contract saying which facts are Overstory's and which are the engine's, before the architecture builds on either;
- one real engine run exported as a fixture, asked of the engine project in `docs/engine-requests.md`, so a frame is drawn from the engine at least once before step 2;
- the usage log by kind of work (build, measure, review, research, docs) and what each produced, which the re-estimate in Rough sizes uses;
- the grey walker on the gully steps before step 2, the cheapest test of people.

**Budget:**
- The weekly limit resets on Monday at 12:00 UTC (13:00 Oslo time in winter).
- Usage is checked at the start of each day. When it runs low, work stops at a milestone boundary with everything pushed (`CLAUDE.md`, Using tokens well).
- Fable's own limit goes to decisions and to one strict review per milestone.
- Two things are tested blind before we rely on them (`docs/research/working-with-claude.md`):
  - the lean review packet: one past strict review is re-run with it, and its findings are compared;
  - Haiku for search, by spot audits.

## The order (agreed 22 October, reviewed by Fable; amended by the plan review of 22 October)

Every system is treated the same way:
- research of the subject and the craft;
- a reference board, a design doc and a target;
- parts made one at a time, judged in grey light from eye level to the raised views, from several headings and in three lights;
- rules and generators, never hand placement, with the shared layers on top;
- frames measured and checked against the core rules;
- one strict review at its milestone (Fable, or Opus if Fable is out, noted), then Øystein's judgement.

**Done** (the plan review, P2). A kind is done when it holds across its range in LT1's 1989 town, walked in the playable corner, at the bar against its target frame, and accepted by Øystein. Its range covers:
- its variety;
- every distance level;
- three lights;
- motion at one sample a pixel;
- its count at town scale;
- staying inside its frame budget.

Until then, its state is written as the rung it has reached, with what still waits. The rungs are: a number, grey form, a sheet, levels, motion, the count, three lights, accepted. "Close" is never a state.

For example, the gully is done only with the Variety stairs rebuilt, and the birches only over their ages and sites, with levels and wind at town scale. `docs/systems.md`'s "How a new thing joins" lists what a kind brings; this says when it is done.

**The standing frame and the frame-rate gate** (the plan review, P1 and P9). Every milestone ends in the playable corner (1g), walked. The harness runs the whole scene at the judging views in three lights, under the Unity lock's `--timing`, and the milestone's strict review judges the result.
- The walk's first run is the baseline. The clay town counts as scope, not as a regression.
- A rise without a change of scope stops the step, just as overrunning its box does.
- The number must hold or fall at each milestone until the corner is under 16.7 ms at every judging view in three lights.
- The fixes that need no levels each have a place: the beams and the haze with 1c, the shader families with the port's step 4, and the birch's cost with 1e. The Monday session puts any fix first.
- A question under a millisecond is measured on its own, but always on the real output (`reviews/lt1/history/r2.md`, R2c).

The work is built round the beauty corner: each system's first slice is the corner's own. It is a world, not a town: the same systems serve a fishing village, the countryside and a metropolis through setting packs.

The steps keep their numbers, since other docs cite them (PL1). Step 1 is reopened on the building blocks (Øystein: "think about the order we do things"):
0. *The foundations page and the light's debts:* done. The lasting light fix is step 1c.
1. *The corner's stone, rebuilt on the building blocks.* The order now (the plan review):
   - first, 1g's design and walk;
   - then 1c in the walked corner, with the port's 2b beside it;
   - the strict review of the port's steps 0 to 2;
   - the port's R3 to R7;
   - the port's steps 4 to 7;
   - then the rest of step 1, as listed below.

   The sub-steps:
   - 1a, the architecture;
   - 1b, the foundations (the framework, materials as data, history storage, distance levels and instancing, the harness, golden views, the scale test). The port's steps 4 and 5 (the plan review, P8) leave room for houses, trees and land, but build nothing for them. Each step is done only when three written records validate against its formats, without being built:
     - a House A front: a coat stack, a glazed window, a painted sign;
     - a birch chunk;
     - a 64 m land chunk with water faces.

     A format changes only where a written record fails to fit it, and no field is added without a record (`reviews/lt1/port/foundation-needs.md`).
   - 1c, the light's lasting fix and the colour grade (the lookups, the sky model, rigs as layers). It comes first after the walk, in the walked corner. Øystein, 22 October: "yes lighting and color grading very important. (also remember Seasons shading philosophy)".
     - It holds to the core rules, SEASON's lesson first: shadow and ambient colour come from the light, never from the object (`docs/research/colour-and-shading.md`).
     - The art and the grade act on the whole light, never on one material (`docs/research/lighting-and-colour.md`).
     - Each change is tested in at least drizzle, low sun and the blue hour, and judged against the target frames.
     - It starts with the low sun's extra 55 to 65 ms (the beams) and settles the dither's shimmer.
   - 1d, the corner's land (natural ground plus dated acts, breaklines, the rock knuckle);
   - 1e, the gully and walls re-fitted, then the birches. This is mostly porting, keeping their facts, rules, style and review findings.

   - 1f, the game's question tested early, in clay (`CLAUDE.md`, Working in the right order: biggest risk first). The corner's houses are built from their diaries at 1989, 2000, 2010 and 2020 by the test-quality generator. Their events after 1988 were authored by named rules of real practice and labelled `authored` (`docs/experiments.md`, 1f); 1f found that the research on what owners and the town did from 1989 to 2020 is a gap, studied before step 4. Two or three of the most promising ways of showing time are prototyped, from a wide creative exploration. Cold readers read them (criteria 1 and 4) before any final house part is made. It needs none of the architecture, so it can start as soon as there is room, and its findings shape the houses and the history budget.

   - 1f+, paper playtests with agent players (Øystein: "can you playtest as well... really analyse the concepts, what feels fun, what feels engaging"). The round's purpose (Øystein): "We will not land on a game after this, but we will definitely know what's missing, and what we HAVE to improve." Its main output is a must-improve register for the engine, Overstory's systems, the interface and content, each item marked must, should or could with its evidence. The concepts' ranking comes second. The register becomes the bundle of engine requests and Overstory's next priorities. Stopped on 22 October after 11 of 24 runs, to put the week into building (Øystein). Its interim note (`docs/playtests/paper-1/analysis/interim.md`) stands in for the register. The concepts are redesigned from the needs it found and tested next with people in the greybox (1g).
     - a game-master agent runs each first-game concept in text, from real simulated lives where possible (Understory's published records, read-only);
     - five player agents of different kinds, on two models, play 20 to 30 turns each and think aloud, marking curiosity, engagement, boredom, confusion and the wish to quit;
     - first, a design panel (a systems designer, a narrative and RPG designer, an experience designer) takes each concept apart: the core loop; hours 1, 10 and 100; the player's motivations; where it turns into a chore; which game does each part best;
     - an analyst compares the concepts by engagement over time, repetition, fulfilment (whether choices showed consequences the player cared about), and whether the lives and the town's history actually change what the player decides;
     - the panel redesigns, or merges the strongest parts of two concepts into a hybrid, and the game master replays; a sceptic argues to kill the weakest;
     - the output is ranked concepts with their sessions, and what the greybox should test first (Øystein: "put yourself in the mind of a game developer in this sandbox, and really push it");
     - Fable reviews it after the reset.

     Agent players find confusion, dead stretches and broken loops; they can't feel fun, so Øystein and his testers have the final word. Later, agent players play the greybox first.
   - 1g, a playable greybox of the corner (Øystein: "testing gameplay and ideas before everything looks finished"):
     - the free camera;
     - blockout people, driven by the real engine run when it arrives (`docs/engine-requests.md`, request 36), else by authored fixtures;
     - hover and inspect as placeholders;
     - showing time from 1f as a switch (PL2): repainted stroke by stroke (leading) against the toggle in place (the baseline it must beat), with more readers than 1f's one each. In 1f, stroke by stroke found 7 of 8 changes with no false claim, the toggle 6 and the window 3, one reader each (Øystein, 21 October, on 1f's sheet). The photograph held at its spot stays, for close views only. The exploration stays wide (Øystein: "there are many cool ways to show time progressing, we should try to be very creative here"), within the constraints in `docs/research/time-on-screen.md`.

     Its play questions are settled by testing variants side by side, never by opinion (Øystein, on the camera: "we have to test this"):
     - a walker or a drone in the lanes;
     - what counts as "you saw it" from a raised view;
     - good viewpoints discovered or marked;
     - how far eye level reaches;
     - a walk mode at eye level;
     - whether people react to the camera;
     - from `docs/research/play-craft.md`: whether the walker has a body; whether the clock runs while the player reads; whether it slows when someone followed acts; whether notices say only that something exists.

     Each variant is a switch in the greybox. The playtest programme compares them with agent players first, then Øystein and his testers.

     It is judged by playing it, and it feeds the choice of the first game. Its play is researched at the same depth as the building blocks (Øystein: "we need to be extremely clever and do deep research how other games do things; master craftsmanship, finesse").

     It starts now (the plan review, 22 October), on the play studies that exist, read from their In shorts. The talks and masters they couldn't open stay held. It is the standing frame (above):
     - the port resumes inside it at 2b;
     - its three biggest costs go to the frame-rate gate, and the port keeps its own order;
     - its first case is built from facts the engine records today, and what the case lacks goes into the next request bundle (`docs/engine-requests.md`);
     - its play (the brief's phase 2) is the milestone after the walk, beside 2b. The studies are `camera-and-composition.md`, `collision-and-navigation.md`, `play-craft.md` (feel, focus, guidance, transitions, narrow streets) and `interface-and-inspection.md`, with the options in `docs/ideas/first-game-options.md`. The playtest itself is designed in `docs/research/playtesting.md` (Øystein: "the playtest will be extremely important"): the programme, the tools the greybox needs (a note key, exact replays from determinism, telemetry), what to measure, and what is worth trying. Opus writes it first; Fable reviews and extends it after the usage reset.

   Then the landing's setts, the kerb and the plinths.
2. *Buildings, built right the first time:* House A by the generator, twelve more from the same parts, then the corner's five houses; coats, windows and signs; a first cold reader.
3. *The corner's ground and things:* heath, D's yard, moss and grass, the lamp, the handrail; the corner complete in four lights.
4. *The corner through the years, forward from 1989* (1989, 2000, 2010, 2020; show from 1989, remember from 1870). Cold readers read the 1989 frame against its record and the changes between years, and it is checked against the engine's front door (`rH28`). The content after 1989 is researched just before this step.
5. *People, in-house on free bases;* the first scene outdoors, on the gully steps at night (criterion 3); a playable camera test.
6. *The heart at the city view:* land and water, paving, the town's things, generated streets; frame time measured each time a part joins (criterion 5).
7. *Nature's living parts,* and the trees' open list.
8. *Interiors and LT2 indoors;* the two clocks settled with the engine.
9. *Weather and seasons finished;* moods judged blind.
10. *Districts, the region, other towns;* one foreign setting pack as the proof.

Each area is researched, subject and craft, before its step starts (`docs/systems.md`). The living fabric's build folds into the steps (`docs/living-fabric.md`):
- step 1: the runner and the record, and the gully's years sheet;
- step 2: House A's coats and shopfront from its keepers and uses;
- step 3: the feet and water fields;
- step 4: the history budget, measured;
- step 6: the cannery street.

## Rough sizes (22 October; step 1 re-estimated on 21 October from the architecture)

**These are guesses made before the evidence** (the plan review, 22 October, P3). They rest on the stairs' pace before the craft research, and the one re-estimate since grew a step four- to sixfold: the port was planned at three days and is 13.5 to 17.5 Opus-days. So no date past the next milestone holds. When the stone is complete, or on 13 November if that comes first, the whole plan is re-estimated in per cent of the weekly limit per finished kind, from `docs/usage-log.md`.

These are weeks of the weekly usage limit, which sets our pace more than the hours do. The studies' own day counts read like a human team's and overestimate our pace. In the week to 22 October, the stairs went from nothing to "close", with their upkeep, wear, water and growth systems, in about a day and a half of work. So these sizes come from the kinds left to make, the foundations, and what the stairs and birches took.

| Steps | What | Weeks |
| --- | --- | --- |
| 1f | **The core idea tested in clay:** the corner's houses at four years, ways of showing time, cold readers | 1 to 2, early |
| 1 (1a to 1e) | Architecture (done), foundations, light, land, stone and birches re-fitted. The gully's port alone is 13.5 to 17.5 Opus-days (`docs/research/building-blocks-decisions.md` §13); at the observed pace that is perhaps 2 to 3 weeks of the limit. Re-sized after next week from the usage log | 5 to 7 |
| 2 | Buildings: the house kit and the corner's five houses | 3 to 5 |
| 3 and 4 | The corner's ground and things; the corner through the years | 3 to 4 |
| | **The corner, complete** | **about 3 to 4 months** |
| 5 | People and the first scene | 6 to 10 |
| | **A first slice a game could stand on** (criteria 1 to 4 tested) | **about 5 to 7 months** |
| 6 to 10 | The heart at the city view, nature, interiors, weather and seasons, other towns, a foreign pack | 25 to 45 |
| | **The whole plan** | **about 1 to 1.5 years** |

Show from 1989 (22 October) saves an estimated one to two months over the whole plan, mostly in people and street things before 1989; the corner is unchanged. The first of each kind costs most. The corner is where every system and kind is made for the first time, so the rest of the town goes faster on the same foundations.

What shortens it: parallel sessions on independent work, and more usage.

What lengthens it:
- areas found unstudied;
- quality loops;
- the engine's pace, since buildings and homes are not modelled yet.

A world for many games has no end: new towns, eras and packs are open-ended content.

## Open, by area (taken up in the order above)

- **Stone:**
  - *The stairs' five faults* (`docs/experiments.md`, LT1, stairs as a kind):
    - the step-ramp's construction should come from its builder;
    - the sett bed should be shaped;
    - rough flights should be irregular;
    - neglect should take shapes below 0.3 care;
    - from 12 m, polish should be one ribbon and lichen one band.

    Also, a stair across a side slope needs a cut and a cheek wall.
  - *Waiting for the assembled corner:*
    - the faces' grain as two or three value plates;
    - a hollow down the old run's walking line;
    - the 1952 run's pointing as one pale field at the street stop;
    - the low-sun stone albedo against the board;
    - the bottom wedge and the blue-hour merge (setts, kerb, lamps).
  - The cheek walls are a first pass, not reviewed.
- **Trees** (`docs/trees.md`; Øystein trusts this work without approval per step, with strict reviews as the gate):
  - *The near tier for eye level:* real leaves near the camera, finer bark, real twigs, and the foot meeting the ground (root flare, soil, moss, litter).
  - *Fallen leaves:* each leaf's own fall date puts it on the ground, drifting downwind and gathering against walls, swept where footfall is busy, rotting over weeks.
  - *The downy birch:*
    - its crown as designed masses, broad above (reference 03);
    - its trunk as its own species at every distance;
    - its age: heavy low limbs and a ragged top.
  - *Polish:* the trunk review's list; the lobes' value step at the street in drizzle and from above.
  - *Systems:* variety (twelve seeds each), wind, distance levels (the 60-year-olds carry 60,000 to 70,000 branch triangles) and grounding, as town-wide systems.
  - *Species:* spruce, then beech, rowan and sycamore. Tower Wood as a beech park wood of about 1900 is a proposal for Øystein.
  - *For later (Øystein):* trees vary in build, from massive trunks to long and skinny; grow them open and crowded, and widen the genotype's range. Trees take the push dial (`stronger`); what it means for a tree is found in a look test.
  - *Measured crown spreads:* downy 42 at 12 m, 44 at the street and 19 from the city camera; silver 55, 46 and 29.
  - Look values live in `LT1Trees.Materials`.
  - *The camera favours side views* (Øystein): its tilt is flatter near the ground.
- **Light:** the morning and the drizzle fail the value test; they are retuned in step 1c on the sky model. The four debts are in `docs/foundations.md`.
- **Clay:**
  - the quay edges show as saw-teeth from afar (quay walls as geometry, step 1d and step 6);
  - the context massing is plain boxes;
  - from the Roads in sea fog the town is lost.

  Clay is structure only. The sketches of the night of 20 October (`blender/tools/grow_town.py`, `fixtures/lt1-town.json`, the terrain module, the light-ray pass, the dramatic rigs) are sketches to learn from, not a base. The last look Øystein judged a step forward is commit `4c7215a` (look P on Harbour Row).
- **Asset gate** (PL4): reached on 20 October and told to Øystein. Parts are made one at a time against their reference boards, with Øystein's OK before references are downloaded (given 21 October; each file is still listed with its source and size for his yes before it is downloaded).
- **Later experiments:** LT2, a small venue at night with two people talking; LT3, the street through the years with seasons and weather (`docs/experiments.md`).
- **After 1989** (needed before step 4, since the world on screen starts in 1989 and moves forward): the content after 1989 is missing. It needs research and the pack's catalogue (`docs/research/town-change.md`: the oil-money years, restored stairs, universal design's ramps and rails, cafés, graffiti), so the world has something to change into.
- **Waiting for Øystein:** in `NOW.md`.

## Running things

- Every Unity run, and every install into `unity/`, goes through the lock: `tools/unity_lock.py run --owner … --purpose … -- <command>`. Frame-time runs add `--timing` (the `unity-conventions` skill). Close the Unity editor on `unity/` first; the lock waits for it.
- **Blender** is `/Applications/Blender.app/Contents/MacOS/Blender -b --factory-startup --python <script> -- <args>`:
  - the stress test: `blender/tools/stress.py -- --n 50 --styles strong`;
  - the clay heart: `blender/blockouts/heart_build.py -- unity`, about 6 minutes;
  - the stone: `blender/generators/stone.py -- gully|variety <unity>`;
  - the quick sheets: `blender/tools/slab_sheet.py`, `sett_sheet.py` and `tree_sketch.py`;
  - a tree: `blender/generators/tree.py -- birch SEED AGE [quality] unity`;
  - the street: `blender/tools/export_street.py`.
- **Unity batch methods:**
  - the heart: `LT1Heart.Scene`, `.Frames`, `.LightFrames`, `.NightFrames`, `.StyleFrames`, `.TargetPasses`;
  - the stone: `LT1Stone.Frames [-paint] [-detail painted|real] [-history|-albedo|-normals]`, `LT1Stone.Variety`;
  - the trees: `LT1Trees.Frames`, `.Seasons`, `.Variety`, `.Pruned`, `.Character`;
  - the street: `LT1Setup.Project`, `LT1Setup.Scene`, `LT1Render.Checkpoint`, `LT1Render.Clay`.

  `blender/tools/light_sheet.py [night]` makes the light sheets.
- **Full-size frames are not in git;** rebuild them with these methods. Never commit `LT1_Heart.unity` or the heart's review frames. Run `git checkout unity/Assets/Art/Materials/M_Sky.mat` after Unity runs.
