# Now

What is open and what is next. Every session reads this page first, so it stays short. History lives in `docs/experiments.md` and git, and the page as it stood before 22 October is in git.

## Where we are (22 October)

- **LT1, the harbour street in 1989,** on branch `lt/1-harbour-street` (`docs/experiments.md`). `main` takes the branch at milestones Øystein has judged: first the corner's stone, then the corner's houses, then LT1's end (decided 22 October; Øystein delegated it). Every commit is pushed to the branch meanwhile.
- **Built:**
  - the house generator at test quality (diaries resolve to plans and meshes, `validate.py`, the stress test passing at strong and stronger; Øystein chose stronger);
  - the heart in clay, with its land, ways and reach check;
  - the light, the style and the moods on the clay;
  - the birches, closed as a look test (Øystein judged them good);
  - the gully steps ("close" after the sixth strict review) and stairs as a kind ("close" after the third);
  - the cheek walls (first pass, not reviewed);
  - the shared systems: water, wear, growth, upkeep and repairs, detail by distance.
- **Designed:** the living fabric, the town system, upkeep and the foundations (`docs/`).
- **Researched:** the subject of most areas, and the craft of fourteen (`docs/research/`). Coverage and the remaining gaps are in `docs/systems.md`.
- **Why building stopped (22 October):** the craft research came after the stone was built, and the stone shows it. One stair with its walls is about 816,000 triangles, with no distance levels and its history stored per vertex. New heavy geometry is held until the building blocks are designed (Øystein: "these need extreme care... our building blocks; we need to do them perfect, so the rest becomes much easier").

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
   - *The scale test* generates a district several square kilometres across in clay, from the test-quality house generator and the clay ground. The harness measures it for build time, memory, disk and frame time at the street stop, 12 m and the city camera. Its numbers settle where generation runs and how the town streams; the architecture leaves those provisional until then. The harness also measures the birches in the corner, which the ground cover study estimates are the dearest pixels in the frame (their eye-facing cards are alpha-tested, which Apple's GPUs shade before they can be hidden; `docs/research/ground-cover-and-plants.md`).
   - *The review:* a fresh strict review of the architecture (Fable), then Øystein's questions in one message, each with a recommendation.
   - *The skills follow the architecture:* `blender-generators` still says hand-modelled `.blend` files and a 1 m grid; `unity-conventions`; the docs table in `CLAUDE.md`.
3. *Wednesday to Friday: the gully on the building blocks (Opus).* Each step is checked against the golden views and the harness before the next:
   1. Split the stone generator into the shared stages, as a kind defined as data, with one channel spec. The spec includes the motion contract (treads, sit points), and the plan hasher comes with it. The gully's geometry hash must not change.
   2. Make history a function of the record and the date, written into history maps instead of per-vertex channels. The gully must look the same up close (FLIP within threshold).
   3. Move stone into the pack as material records.
   4. Add distance levels by measured error, cut the flight into chunks of a few metres, and cast shadows from proxies.
   5. Measure triangles and frame time at every judging view, before and after.
   6. *Friday:* a strict review (Fable), and the proof sheet for Øystein: the gully before and after at eye level, the street stop, 12 m and the city camera, with the numbers. This is the new foundations' first milestone.
4. *If the week runs short,* the cut comes from the end: the levels and proxies move to the next week. The architecture, the tools and the scale test do not move.

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
- *What changes in existing work:* the stairs and walls, the birches, and how the houses start (House A built by the generator, then twelve more from the same parts).

**What goes to Øystein** (scope, play and permissions only, each with a recommendation; everything else is decided, recorded with its reasons, and shown to him as finished work he can overturn):
- the town system's scope and the eras after 1989 (`docs/town-system.md`);
- his OK for reference downloads (Stavanger's rock, water, city-archive photos for houses and dress, and the large GDC decks the studies could not open), each listed with its source and size first;
- how players compare years (play, defaults per game; `docs/research/time-on-screen.md`). Recommended:
  - an archive photograph, or the player's own, held up at its spot and toggled in place;
  - a time-lapse allowed as spectacle, but bracketed by dated stills and never the only passage;
  - the player's own acts never marked in the world, shown in the journal and the why-probe instead;
- the interface's play choices, once `docs/research/interface-and-inspection.md` is in.

**Look and craft questions are ours** (Øystein, 22 October: "You have to figure these things out. As long as we are critical and only aim for high quality, this should answer itself."). They are decided on frames and motion sheets, with strict reviews, and Øystein judges the milestones. This covers the night sky's colour, lamp glass and the tonemapper; the brush's size by octaves and any boil; and near ground cover as strokes or blades.

**Budget:**
- The weekly limit resets on Monday at about 13:00 Oslo time.
- Rough shares: the architecture a fifth; the tools and the scale test a quarter; the gully's port a third; a fifth kept in reserve for Øystein's requests and fixes.
- Fable's own limit goes to the architecture and the two reviews.
- Usage is checked at the start of each day. When it runs low, work stops at a milestone boundary with everything pushed (`CLAUDE.md`, Using tokens well).

**Who starts it:** the chat that wrote this plan starts both Monday sessions when Øystein says go. Otherwise any new session that reads this page can start them.

**Before Monday:** two studies are being written. One is on using fewer tokens without losing quality (`docs/research/working-with-claude.md`), which updates `CLAUDE.md`'s rules. The other is on the interface: hovering, inspecting and asking why (`docs/research/interface-and-inspection.md`; Øystein: "we have not talked about ui etc yet"). Four craft studies were started on 22 October: `painted-marks-in-motion.md`, `time-on-screen.md`, `ground-cover-and-plants.md` and `fronts-windows-and-signs.md`. Each saves its draft as it goes and is committed as it lands; one cut short is committed as a partial draft and finished on Monday.

## Decided (22 October; don't reopen without Øystein)

- **The architecture's decisions are delegated** (Øystein: "I trust you know how to handle this feedback, and based on a good analysis make the correct decisions moving forward"). Only taste, scope and play go to him.
- **The reference machine** is an ordinary computer, the M4 Mac mini: 60 fps at 1440p at default settings, with no gaming PC needed (`docs/foundations.md`).
- **Cold readers are model readers,** in the engine's blind method (`docs/foundations.md`).
- **How years pass in play** depends on the game, from a week to generations. The screen follows the record, and play changes the record (`docs/town-system.md`).
- **Signs and street text are in English** (Øystein, 22 October), lettered in each era's styles.
- **Scenes are written, not voiced.** No motion-capture sessions: motion comes from free libraries, edited against video (`docs/living-world.md`).
- **The town stands on Stavanger's phyllite** (`docs/stone.md`).
- **Nothing repeats unless it was factory-made** (Øystein, on stairs). No Houdini: its free version forbids commercial use, and there is no money for Indie. No commissions; free and open bases only.
- **Build for bigger cities:** every choice is costed per building and per kilometre of street.
- **The rules in `CLAUDE.md`:** reuse systems, never looks; research the subject and the craft before building; stop and reflect when work reveals a gap.

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

   Then the landing's setts, the kerb and the plinths.
2. *Buildings, built right the first time:* House A by the generator, twelve more from the same parts, then the corner's five houses; coats, windows and signs; a first cold reader.
3. *The corner's ground and things:* heath, D's yard, moss and grass, the lamp, the handrail; the corner complete in four lights.
4. *The corner through the years* (1935, 1960, 1989, 2020): cold readers date it, and it is checked against the engine's front door (`rH28`).
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
- **1989 to today** (Øystein): the systems run to any year, but the content after 1989 is missing: research and the pack's catalogue (`docs/research/town-change.md`), so the world has something to change into and a setting can start later (#23).
- **Waiting for Øystein:** the items under "What goes to Øystein" above.

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

## Engine and the shared goal

- **Engine:** places are workplaces plus ventures that open new ones; places never close, and buildings and homes are not modelled. Read tag `r41` or later; its front door is read-only and shows the truth, for our tools. The engine's order: a reading that counts every fault, the first human test, rounds 42 and 43, then the band for a year with homes (#59), and #22 taken up again; #20 and #23 are paused. The living fabric's requests are tracked in engine issue #60. LT1 and LT2 run on fixtures labelled `authored`. Overstory's cold reader for criterion 1 can ride on the engine's human test (one task after the page). Details are in `docs/engine-requests.md`.
- **Shared goal:** `CLAUDE.md` ("What it is for") states Overstory's question and the draft exit criteria, to agree with Øystein. The band is proposed as a shared milestone with the engine (`docs/engine-requests.md`, open items).
