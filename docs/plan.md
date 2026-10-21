# The plan

The order of the work and the current week's plan in detail. `NOW.md` holds the state and links here; update this page when a step starts or ends.

## Next week: the building blocks (from Monday 26 October)

**The goal for Friday:**
- the architecture decided and reviewed;
- the tools that measure everything built;
- the scale test run;
- the gully's port begun on the new foundations, toward the proof (the same up close, a fraction of the cost at distance): steps 0 to 2 reviewed, step 3 as far as it gets (the cut line below).

Øystein sees two things: the architecture's few questions (Monday or Tuesday) and the proof sheet with its numbers (Friday).

**Why this shape:**
- *Measure before changing.* Nothing is judged without the frame-time harness and the golden views (`docs/research/performance-at-scale.md`). They also protect the gully's look while its generator is rebuilt.
- *Prove on one kind before generalising.* The gully is the best-known thing we have: six reviews, a known look, a known cost. Porting it end to end tests every part of the architecture at once, while errors are cheap.
- *Scale early.* The scale test can change the architecture (where generation runs, how the town streams), so it runs before the framework's details are fixed.
- *Fable for judgement only.* Its own weekly limit ran out this week. Opus builds; Sonnet runs the mechanical checks.

**Baselines (measured 22 October on the M4):**
- The house generator at test quality built and checked 129 buildings in 10.2 s (50 random diaries at four years, Blender's start included), about 13 a second.
- The gully's flight at final quality takes 67 s and makes one 16 MB FBX, without its walls.
- One stair with its walls is about 816,000 triangles.
- The repository is 2.2 GB of git history. Unity holds 407 MB of art, 373 MB of it in 222 FBX files, 272 MB of that stone.

**Frame time today** (the harness, 21 October; `docs/measuring.md`): the corner runs at 28 to 42 ms in drizzle, 84 to 96 ms in low sun, and 25 to 35 ms at the blue hour. That's 10 to 40 fps against the 60 fps target.
- About 15 million triangles a frame with sun shadows, and 5.5 million without.
- Something drawn only in low sun costs about 55 to 65 ms; the sun beams are the suspect.
- The birch costs 10 to 16 ms in view, and 25 ms when it fills the frame.
- The committed gully FBX is not what its generators build, even at its own commit, and the walls have drifted since. The gully is exported again and its golden views re-accepted before the port.
- URP's dither is redrawn every frame, so a still camera shimmers by about half a level. That is decided with the light (1c).

At today's rate a thousand stairs would take about 19 hours to generate and 16 GB of FBX. The architecture must change how they are made, not tune them.

**The days.** These are rough, in order of dependency. Each step ends in a commit and a pushed state, never mid-change.
1. *Monday: the architecture, and the measuring tools in parallel.* Both done on 21 October: the architecture is `docs/building-blocks.md` (reasons in `docs/research/building-blocks-decisions.md`), the tools are `docs/measuring.md`. Two sessions in the same checkout, on different files; each pulls with rebase before every push.
   - *The architecture* runs on Fable in a fresh session. Opus agents first check the fourteen studies against the bar, one study each. The bar: primary sources read where they open, claims marked (secondary) or (unverified), concrete for our stack, no thin sections. Each agent returns a compact digest: the study's decisions and costs, its dependencies, its conflicts with other studies, its weak spots, and pointers to its sections. A study goes back for another pass only where a gap would change a decision. The known weak spots:
     - behaviour-on-screen and kits-and-generation ran short of web searches;
     - land-rock-and-water had talks that would not open;
     - characters lacks 1989 dress;
     - performance's game figures are secondary;
     - any of the four newest studies may have been cut short by the budget.

     Fable then reads the digests, opens the original sections where a decision hinges on them, and writes `docs/building-blocks.md`.
   - *The tools* run on Opus in its own session:
     - the frame-time harness on the corner (`Overstory.Perf.PerfRunner`, a macOS player build at 1440p, the judging views in three lights; performance study, steps 1 and 8);
     - mesh hashes for every export;
     - the golden views of today's gully, the baseline every change is compared against with FLIP;
     - a motion-sheet renderer: 60 fps video at 1440p with one sample per pixel, plus stills scaled to the player's footprint. Every judged frame so far was rendered at twice the size and averaged down. That hid shimmer and crawling marks and set distance fades 1.5 times too far, and no mark has ever been judged moving (`docs/research/painted-marks-in-motion.md`). The golden views use it too.
2. *Tuesday: the scale test, then the architecture's review.*
   - *The scale test* generates a district several square kilometres across, drawn with the corner's real shaders rather than clay alone, so the look's cost at city scale is known before step 6 (`docs/research/pre-mortem.md`), from the test-quality house generator and the clay ground. The harness measures it for build time, memory, disk and frame time at the street stop, 12 m and the city camera. Its numbers settle where generation runs and how the town streams; the architecture leaves those provisional until then. It also measures three things for where generation runs (`docs/research/where-generation-runs.md`): the time to load and rebuild a chunk in a built player, the chunks a second the camera's movement demands, and the cache size per kilometre. It settles what the architecture leaves provisional (`docs/building-blocks.md`, Open until measured):
     - the per-pass frame budget, with the low-sun pass A/B'd first (its extra 55 to 65 ms is a bug, found before any triangle work);
     - chunk and unit sizes (4, 32, 64 and 128 m by default);
     - a shipped cache against building on demand;
     - map density (2, 4 and 8 cm against coarser, with synthetic maps) and the bake time of one page;
     - memory against the 6 GB pools, including a second date or record;
     - disk per kilometre;
     - the streaming budget: main-thread ms a frame for swaps, chunks and MB uploaded a frame, renderers resident. The harness also measures the birches in the corner, which the ground cover study estimates are the dearest pixels in the frame (their eye-facing cards are alpha-tested, which Apple's GPUs shade before they can be hidden; `docs/research/ground-cover-and-plants.md`).
   - *The review* (done 21 October: `docs/research/pre-mortem-architecture.md`, `docs/research/building-blocks-review.md`, ready after fixes, fixes applied) opens with a pre-mortem (`CLAUDE.md`, Working in the right order): a fresh reviewer imagines the architecture failed six months on, says why, and names what a studio's lead technical artist would say is missing. A strict review (Fable) follows, then Øystein's questions in one message, each with a recommendation.
   - *The skills follow the architecture:* `blender-generators`, `unity-conventions` and `CLAUDE.md`'s docs table and Practical line, updated 21 October.
3. *Wednesday to Friday: the gully on the building blocks (Opus).* Each step is checked against the golden views and the harness before the next, and ends in a commit and a pushed state. Re-estimated against the architecture (`docs/research/building-blocks-decisions.md` §13):

   | Step | What | Estimate | By Friday |
   | --- | --- | --- | --- |
   | 0a | A fresh export of today's gully and walls; golden views re-accepted by a strict review; the baseline | half a day | done |
   | 0b | Seeds: one hash spec, `Hash.cs` matched to `hashing.py`, the vector file; `stone.py`, `wall.py`, `upkeep.py` on SplitMix64 over part ids; a new baseline | 1 day | done |
   | 1 | The schema files, the naming grammar, the layer and map registries, the change query, the world state; the house kind and one window's slot record written and validated, not built; `validate_record.py`; `migrate.py` with migration 001 | 1 to 1.5 days | done |
   | 2 | Stone split into the seven stages as `kinds/stair.json` with one runner; facts from a fixture; the plan hasher and the hash chain; golden fixtures per stage; `diff_stage.py`; the geometry hash unchanged; the export carrying breaklines, joints, affordances and the motion class | 2 days | done or nearly |
   | 3 | History as a function: rates, reset years and age offsets into the place and history pages, the date a global, `OS_History` in the shaders; the A/B in grey light at eye level, FLIP within threshold; the years sheet shows jumps only at works | 2 to 3 days | **the cut line**: started, perhaps not accepted |
   | 4 | Materials as pack records; the editor step that writes the Unity assets | 1 day | next week |
   | 5 | Levels from the generator, 4 m chunks, the shell ribbon, caster proxies, the Drawer's pragmas and the highlight compare; the id test | 3 to 4 days | next week |
   | 6 | The picking spike (1 to 1.5 days) and the grey walker (1 to 2 days) | 2 to 3.5 days | next week |
   | 7 | Measure before and after at every judging view; the strict review; the proof sheet | 1 day | Friday, on whatever is honestly complete |

   The steps add to 13.5 to 17.5 Opus-days for the whole port, and 6.5 to 8 through step 3. The week has three. No stage is ported to C# this week; the only C# change is matching `Hash.cs` to the hash spec (0b).
4. *The cut line.* Friday's milestone is steps 0 to 2 reviewed, with step 3 as far as it has got and its A/B shown as it is. The architecture, the tools and the scale test do not move. Øystein sees the proof sheet with its numbers on whatever is honestly complete.

**What the architecture decides** is written once, in `docs/building-blocks.md`: the stages, the contracts, ids, what every part carries, levels, budgets and what changes in existing work.
Its reasons are in `docs/research/building-blocks-decisions.md`, and its open numbers in its table "Open until measured".
The questions left for Øystein are in `NOW.md`.

**Leaner without losing brilliance** (Øystein, 22 October: "we need to make the game leaner, I fear; is it possible without losing visual brilliance?"). The proposals and where each stands:
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
- the usage log by kind of work (build, measure, review, research, docs) and what each produced, with the plan re-sized by 13 November in per cent of the weekly limit per finished kind;
- the grey walker on the gully steps before step 2, the cheapest test of people.

**Budget:**
- The weekly limit resets on Monday at about 13:00 Oslo time.
- Rough shares: the architecture a fifth; the tools and the scale test a quarter; the gully's port a third; a fifth kept in reserve for Øystein's requests and fixes.
- Fable's own limit goes to the architecture and the two reviews.
- Usage is checked at the start of each day. When it runs low, work stops at a milestone boundary with everything pushed (`CLAUDE.md`, Using tokens well).
- Before relying on them, test the lean review packet blind (one past strict review re-run with it, its findings compared) and Haiku for search (spot audits) (`docs/research/working-with-claude.md`).

## The order (the plan agreed 22 October, reviewed by Fable)

Every system is treated the same way:
- research of the subject and the craft;
- a reference board, a design doc and a target;
- parts made one at a time, judged in grey light from eye level to the raised views, from several headings and in three lights;
- rules and generators, never hand placement, with the shared layers on top;
- frames measured and checked against the core rules;
- strict reviews (Fable, else Opus, noted), then Øystein's judgement.

The work is built round the beauty corner: each system's first slice is the corner's own. It is a world, not a town: the same systems serve a fishing village, the countryside and a metropolis through setting packs.

The steps keep their numbers, since other docs cite them. Step 1 is reopened on the building blocks (Øystein: "think about the order we do things"):
0. *The foundations page and the light's debts:* done. The lasting light fix is step 1c.
1. *The corner's stone, rebuilt on the building blocks:*
   - 1a, the architecture;
   - 1b, the foundations (the framework, materials as data, history storage, distance levels and instancing, the harness, golden views, the scale test);
   - 1c, the light's lasting fix (the lookups, the sky model, rigs as layers);
   - 1d, the corner's land (natural ground plus dated acts, breaklines, the rock knuckle);
   - 1e, the gully and walls re-fitted, then the birches. This is mostly porting, keeping their facts, rules, style and review findings.

   - 1f, the game's question tested early, in clay (`CLAUDE.md`, Working in the right order: biggest risk first). The corner's houses are built from their diaries at 1989, 2000, 2010 and 2020 by the test-quality generator. The diaries need events after 1988 first: none has any yet. Two or three of the most promising ways of showing time are prototyped, from a wide creative exploration. Cold readers read them (criteria 1 and 4) before any final house part is made. It needs none of the architecture, so it can start as soon as there is room, and its findings shape the houses and the history budget.

   - 1f+, paper playtests with agent players (Øystein: "can you playtest as well... really analyse the concepts, what feels fun, what feels engaging"). The round's purpose (Øystein): "We will not land on a game after this, but we will definitely know what's missing, and what we HAVE to improve." Its main output is a must-improve register for the engine, Overstory's systems, the interface and content, each item marked must, should or could with its evidence. The concepts' ranking comes second. The register becomes the bundle of engine requests and Overstory's next priorities.
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
     - showing time from 1f as a switch: repainted stroke by stroke (leading) against the toggle in place (the baseline it must beat), with more readers than 1f's one each.

     Its play questions are settled by testing variants side by side, never by opinion (Øystein, on the camera: "we have to test this"):
     - a walker or a drone in the lanes;
     - what counts as "you saw it" from a raised view;
     - good viewpoints discovered or marked;
     - how far eye level reaches;
     - a walk mode at eye level;
     - whether people react to the camera;
     - from `docs/research/play-craft.md`: whether the walker has a body; whether the clock runs while the player reads; whether it slows when someone followed acts; whether notices say only that something exists.

     Each variant is a switch in the greybox. The playtest programme compares them with agent players first, then Øystein and his testers.

     It is judged by playing it. It feeds the choice of the first game, and it can start once 1f has its clay corner. Before it starts, its play is researched at the same depth as the building blocks (Øystein: "we need to be extremely clever and do deep research how other games do things; master craftsmanship, finesse"). The studies are `camera-and-composition.md`, `collision-and-navigation.md`, `play-craft.md` (feel, focus, guidance, transitions, narrow streets) and `interface-and-inspection.md`, with the options in `docs/ideas/first-game-options.md`. The playtest itself is designed in `docs/research/playtesting.md` (Øystein: "the playtest will be extremely important"): the programme, the tools the greybox needs (a note key, exact replays from determinism, telemetry), what to measure, and what is worth trying. Opus writes it first; Fable reviews and extends it after the usage reset.

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

These are weeks of the weekly usage limit, which sets our pace more than the hours do. The studies' own day counts read like a human team's and overestimate our pace. In the week to 22 October, the stairs went from nothing to "close", with their upkeep, wear, water and growth systems, in about a day and a half of work. So these sizes come from the kinds left to make, the foundations, and what the stairs and birches took. They are re-estimated after next week from the usage log (`docs/usage-log.md`).

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
- **Asset gate:** reached on 20 October and told to Øystein. Parts are made one at a time against their reference boards, with Øystein's OK before references are downloaded.
- **Later experiments:** LT2, a small venue at night with two people talking; LT3, the street through the years with seasons and weather (`docs/experiments.md`).
- **After 1989** (needed before step 4, since the world on screen starts in 1989 and moves forward): the content after 1989 is missing. It needs research and the pack's catalogue (`docs/research/town-change.md`: the oil-money years, restored stairs, universal design's ramps and rails, cafés, graffiti), so the world has something to change into.
- **Waiting for Øystein:** in `NOW.md`.

## Running things

- Close the Unity editor on `unity/` before running it in batch mode.
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
