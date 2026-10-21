# The plan

The order of the work and the current week's plan in detail. `NOW.md` holds the state and links here; update this page when a step starts or ends.

## Next week: the building blocks (from Monday 26 October)

**The goal for Friday:**
- the architecture decided and reviewed;
- the tools that measure everything built;
- the scale test run;
- the gully ported onto the new foundations end to end as the proof: the same up close, a fraction of the cost at distance.

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

At today's rate a thousand stairs would take about 19 hours to generate and 16 GB of FBX. The architecture must change how they are made, not tune them.

**The days.** These are rough, in order of dependency. Each step ends in a commit and a pushed state, never mid-change.
1. *Monday: the architecture, and the measuring tools in parallel.* Two sessions in the same checkout, on different files; each pulls with rebase before every push.
   - *The architecture* runs on Fable in a fresh session. Opus agents first check the fourteen studies against the bar, one study each. The bar: primary sources read where they open, claims marked (secondary) or (unverified), concrete for our stack, no thin sections. Each agent returns a compact digest: the study's decisions and costs, its dependencies, its conflicts with other studies, its weak spots, and pointers to its sections. A study goes back for another pass only where a gap would change a decision. The known weak spots:
     - behaviour-on-screen and kits-and-generation ran short of web searches;
     - land-rock-and-water had talks that would not open;
     - characters lacks 1989 dress;
     - performance's game figures are secondary;
     - any of the four newest studies may have been cut short by the budget.

     Fable then reads the digests, opens the original sections where a decision hinges on them, and writes `docs/building-blocks.md` (scope below).
   - *The tools* run on Opus in its own session:
     - the frame-time harness on the corner (`Overstory.Perf.PerfRunner`, a macOS player build at 1440p, the judging views in three lights; performance study, steps 1 and 8);
     - mesh hashes for every export;
     - the golden views of today's gully, the baseline every change is compared against with FLIP;
     - a motion-sheet renderer: 60 fps video at 1440p with one sample per pixel, plus stills scaled to the player's footprint. Every judged frame so far was rendered at twice the size and averaged down. That hid shimmer and crawling marks and set distance fades 1.5 times too far, and no mark has ever been judged moving (`docs/research/painted-marks-in-motion.md`). The golden views use it too.
2. *Tuesday: the scale test, then the architecture's review.*
   - *The scale test* generates a district several square kilometres across, drawn with the corner's real shaders rather than clay alone, so the look's cost at city scale is known before step 6 (`docs/research/pre-mortem.md`), from the test-quality house generator and the clay ground. The harness measures it for build time, memory, disk and frame time at the street stop, 12 m and the city camera. Its numbers settle where generation runs and how the town streams; the architecture leaves those provisional until then. It also measures three things for where generation runs (`docs/research/where-generation-runs.md`): the time to load and rebuild a chunk in a built player, the chunks a second the camera's movement demands, and the cache size per kilometre. The harness also measures the birches in the corner, which the ground cover study estimates are the dearest pixels in the frame (their eye-facing cards are alpha-tested, which Apple's GPUs shade before they can be hidden; `docs/research/ground-cover-and-plants.md`).
   - *The review* opens with a pre-mortem (`CLAUDE.md`, Working in the right order): a fresh reviewer imagines the architecture failed six months on, says why, and names what a studio's lead technical artist would say is missing. A strict review (Fable) follows, then Øystein's questions in one message, each with a recommendation.
   - *The skills follow the architecture:* `blender-generators` still says hand-modelled `.blend` files and a 1 m grid; `unity-conventions`; the docs table in `CLAUDE.md`.
3. *Wednesday to Friday: the gully on the building blocks (Opus).* Each step is checked against the golden views and the harness before the next:
   0. Move every seed off Python's `random.Random`, some of which are keyed by float positions, to SplitMix64 on part ids. Python does not keep those sequences across versions, and the C# port must match them. This is its own commit, with a new baseline.
   1. Split the stone generator into the shared stages, as a kind defined as data, with one channel spec. The spec includes the motion contract (treads, sit points), and the plan hasher comes with it. The gully's geometry hash must not change.
   2. Make history a function of the record and the date, written into history maps instead of per-vertex channels. The gully must look the same up close (FLIP within threshold).
   3. Move stone into the pack as material records.
   4. Add distance levels by measured error, cut the flight into chunks of a few metres, and cast shadows from proxies.
   5. Measure triangles and frame time at every judging view, before and after.
   6. *Friday:* a strict review (Fable), and the proof sheet for Øystein: the gully before and after at eye level, the street stop, 12 m and the city camera, with the numbers. This is the new foundations' first milestone.
4. *If the week runs short,* the cut comes from the end: the levels and proxies move to the next week. The architecture, the tools and the scale test do not move. The studies' own estimates put the full port of the gully at 16 to 22 Opus-days (`docs/research/inputs/2-generation-performance.md`), so the week should expect to reach the first stages (the stages split, the hashes unchanged, history as a function) rather than the whole port. Friday's milestone is whatever is honestly complete, reviewed.

**What the architecture decides** (`docs/building-blocks.md`; decided with reasons, nothing built in it):
- *The generator framework:*
  - every kind defined as data in `blender/kinds/`, with one runner through the same stages: facts, plan, life, geometry, bake, export, checks;
  - standards per setting pack first: grid, door sizes, slopes, a metrics table;
  - a definition per part: fixed or fitted, sizes, sockets, what removing it leaves;
  - cells and sockets as dated records, so nothing is ever deleted;
  - locks, so hand improvements survive regeneration;
  - one tool for everything laid along a line;
  - the plan hasher.
- *Materials as data:* one shared library with masks from facts. Each material keeps its identity from its source, its working and its exposure. The paint-coat stack; the board-and-trim atlas.
- *History:*
  - history maps instead of per-vertex channels;
  - history as a function of the record and the date;
  - the layers still missing: airborne deposits with washing, carried stains, the splash band, contact wear on every material;
  - newer marks over older ones as a check.
- *Distance levels and repetition:*
  - levels by measured error, chunks, and shadows from proxies;
  - libraries of judged pieces placed as instances with per-place facts;
  - budgets set on the reference machine;
  - repetition only where reality repeats: factory-made pieces from small libraries, hand-made ones from large libraries, unique only what wear has shaped.
- *What every part carries for the systems to come:* the light (the three lookups), motion (pivots, motion class, sockets), the painted look in motion, windows and what is behind them, signs, time, and the interface. For the interface, every drawn piece must be pickable back to its record, even when merged or instanced, for hovering, inspecting and asking why.
- *The land:* natural ground plus dated acts, mesh terrain with breaklines, natural stone as a kind.
- *Quality:*
  - the frame-time harness;
  - golden views compared automatically;
  - mesh hashes;
  - generated meshes rebuilt from their generators rather than kept in git;
  - the cold readers.
- *Scale, with numbers* (Øystein: "are we being clever for the future when we start building other, bigger cities?"):
  - where generation runs and how fast, per building and per kilometre of street: cached, deterministic, on demand near the camera;
  - what a new city's pack must bring, and what carries over;
  - memory, disk and streaming by chunk.
- *Open to every game:* Overstory is a world for many games (`docs/living-world.md`, the three dials). The architecture checks itself against three example games and must lock none of them out: a manager (a football club or a band, with a world around it), an exploration game, and a family across generations. These are examples, not a choice of game.
- *Where each stage runs* (raised by the generation digest): play changes the record, and the 3D world must show it. But a built game can't run Blender, import FBX at runtime or ship GPL code (`bpypolyskel`). So which stages run offline and which run inside the game is decided from `docs/research/where-generation-runs.md` and the scale test's numbers.
- *What changes in existing work:* the stairs and walls, the birches, and how the houses start (House A built by the generator, then twelve more from the same parts).

**Leaner without losing brilliance** (Øystein, 22 October: "we need to make the game leaner, I fear; is it possible without losing visual brilliance?"). The proposals and where each stands:
1. *Paint the far town:* past about 50 m, a painted backdrop baked from the near models for each date, instead of distance versions for every kind. Øystein: "I would have to see this, but sounds promising." It becomes a look test in the foundations: the corner's far view as a baked backdrop beside conventional distance versions, judged by Øystein.
2. *Make the 1989 town once,* curated, with records by rule, instead of growing two centuries plot by plot. Decided (Øystein: "as long as we can change this later"). The 1989 town is stored as records that can be regenerated, edited, or replaced later by a growth simulation or by the engine's own past. It also removes the pre-mortem's risk that Overstory becomes the engine.
3. *Libraries only where things were factory-made:* each house type and era gets its own kit (decided; see `NOW.md`).
4. *Concentrate the history:* the full set of history layers goes where a view's stories are; elsewhere one shared weathering bake (rain, sun, years, care) keeps every surface true but quiet. Decided (Øystein: "as long as we can build this out later"). The architecture designs the layer stack so specialised layers (soot, salt, rust runs, carried stains, splash bands, failing coats) can be added to any kind later without rebuilding it: a registry of layers, reserved channels in the history maps, and the shared bake as the base every layer sits on.
5. *A dense town, not a metropolis, for now:* decided.
6. *Moods:* withdrawn. The lighting study's way is already the leaner one: the light derived from a sky model for any hour and weather, with a few art keys on top, replaces about sixty-five hand-typed settings an hour. Every hour and weather then comes nearly free, and a mood is a set of art keys.
7. *People:* their own research project with great care (Øystein). No shortcut.
8. *Eye level for every part:* open. The cost of eye level is measured per kind during the gully port and the first house, then decided with numbers.

Also: build more, write less. Docs only where a decision needs recording; the building blocks proven in code and frames.

**From the pre-mortem** (`docs/research/pre-mortem.md`, ranked failure stories; on Opus, to be checked by Fable):
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

## Rough sizes (22 October, before the architecture; to be measured)

These are weeks of the weekly usage limit, which sets our pace more than the hours do. The studies' own day counts read like a human team's and overestimate our pace. In the week to 22 October, the stairs went from nothing to "close", with their upkeep, wear, water and growth systems, in about a day and a half of work. So these sizes come from the kinds left to make, the foundations, and what the stairs and birches took. They are re-estimated after next week from the usage log (`docs/usage-log.md`).

| Steps | What | Weeks |
| --- | --- | --- |
| 1f | **The core idea tested in clay:** the corner's houses at four years, ways of showing time, cold readers | 1 to 2, early |
| 1 (1a to 1e) | Architecture, foundations, light, land, stone and birches re-fitted | 4 to 6 |
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
