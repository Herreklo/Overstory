# Now

What is open and what is next. Every session reads this page first, so it stays near 1,500 tokens. The plan in detail is `docs/plan.md`; history is in `docs/experiments.md` and git.

## Where we are (22 October)

- **LT1, the harbour street in 1989,** on branch `lt/1-harbour-street` (`docs/experiments.md`). `main` takes the branch at milestones Øystein has judged: first the corner's stone, then the corner's houses, then LT1's end (decided 22 October; Øystein delegated it). Every commit is pushed to the branch meanwhile.
- **Built:**
  - the house generator at test quality (diaries resolve to plans and meshes, `validate.py`, the stress test passing at strong and stronger; Øystein chose stronger);
  - the heart in clay, with its land, ways and reach check;
  - the light, the style and the moods on the clay;
  - the birches, closed as a look test (Øystein judged them good);
  - the gully steps ("close" after the sixth strict review) and stairs as a kind ("close" after the third);
  - the cheek walls (first pass, not reviewed);
  - the shared systems: water, wear, growth, upkeep and repairs, detail by distance;
  - the measuring tools, built and accepted (`docs/measuring.md`);
  - 1f, the clay time test (`docs/experiments.md`, `reviews/lt1/time/`).
- **The architecture is written and reviewed:** `docs/building-blocks.md`, decided on Fable on 21 October; the strict review found it ready after fixes, and they are applied. Reasons: `docs/research/building-blocks-decisions.md`.
- **Designed:** the living fabric, the town system, upkeep and the foundations (`docs/`).
- **Researched:** the subject of most areas, and the craft of fourteen (`docs/research/`). Coverage and the remaining gaps are in `docs/systems.md`.
- **Why building stopped (22 October):** the craft research came after the stone was built. One stair with its walls is about 816,000 triangles, with no distance levels and its history per vertex (Øystein: "these need extreme care... our building blocks; we need to do them perfect, so the rest becomes much easier"). The gully is the first thing rebuilt on the building blocks.

## Next

The week's plan starts from the architecture (`docs/plan.md`, Next week; steps in `docs/research/building-blocks-decisions.md` §13).
1. **The gully port's first steps,** on Opus, a commit each: 0a a fresh export and baseline; 0b seeds on one hash spec; 1 the schema files; 2 the stage split (`kinds/stair.json`, geometry hash unchanged). Then 3, history as a function.
   - *Sequencing:* step 0a is the scale-test session's step 2 (the gully exported again, hashed, golden views accepted), so the port doesn't redo it.
   - *Start:* the port starts in its own fresh Opus session when the scale test reports, not before. Heavy Blender or Unity runs beside the harness would skew its frame times, and Unity's batch mode locks the project.
2. **The scale test,** in its own session (started 21 October, evening), with the pass budget and the measurements the architecture leaves provisional (`docs/building-blocks.md`, Open until measured). Results go to `docs/research/scale-test.md`.
3. **The cut line:** the port is 13.5 to 17.5 Opus-days, 6.5 to 8 through step 3, against three days. Friday's milestone is steps 0 to 2 reviewed, step 3 as far as it got.

## Tonight (21 to 22 October), for the main session

Øystein asked us to carry on without him tonight. The main chat was cleared at about 20:55 to keep it small. Its linked sessions report to it, and on each note it reads this page and acts:
- **The scale test reported** (22 October, about 01:30; `docs/research/scale-test.md`). It changes nine of the architecture's choices. Sessions can't be started over Remote Control, so the port runs as fresh Opus agents from the main session until Øystein next writes from the desktop: one folds the results into `docs/building-blocks.md` (Fable decides any change to a decided rule), and one does step 0b (seeds) beside it, since 0b touches neither. Steps 1 to 3 run in the port's own session (`gully-port`, started 22 October about 02:00), which starts step 1 when step A lands and step 2 when 0b lands, on the main session's go. Step A landed (`7962e2e`, `c4d3537`; Fable's four verdicts in `docs/research/building-blocks-decisions.md` §15) and step 1 is running. Step 0b is finished (`13e1b3b` to `a858766`). The stair kept dropping its landings on low rises, so Fable set the landing rule: the rise comes from the site, and `step_plan` now fails loudly instead. The new baseline (stairs `bff7858b698f3efd`, walls `0a3d7db3100df20b`, walls 35% more triangles) beat the 22 October build in 8 of 8 blind pairs, but is still below the bar, with four known faults in `docs/measuring.md`. Øystein accepted it on 22 October as the regression reference only. Its look is judged against the target frame, never only against the build before (his doubt). Step 2's stair work has its go. Step 3 started early on its own files (`eff830d` to `db34f2a`). Step 2's groundwork runs meanwhile on new files only. No agent runs in the main chat now, so it can be cleared. Øystein accepted the gully's new baseline (`bb13eaa`).
- **When the playtests report:** the four steps under "When the playtest report lands", below.
- **After the 5-hour window resets (00:30 Oslo):**
  - *Held (22 October): the week's budget goes to the port first; it starts once the port runs and the weekly allows.* The camera and play-craft research for 1g, in a fresh Opus session. It covers the talks and papers the studies could not open (GDC Vault was down): Designing Journey, Hitman's level design and crowds, Assassin's Creed Unity's crowds, Lemarchand, Smith's continuity paper, So's study of navigation speed and sickness, and the masters named under "Then, on Opus". The sources are listed in the Limits sections of `docs/research/play-craft.md`, `camera-and-composition.md` and `collision-and-navigation.md`. Read online only: a file download waits for Øystein's OK, listed with its source and size.
  - the date housekeeping below.
- **Pace by the 5-hour window:** at most three sessions working at once, and nothing new started above about 80%. Check with `get_usage`.

## Running now

Each session commits its own work. If one stops, resume it from its files. Long work runs in its own session: the main chat's background agents seem to stop when the chat is cleared, as the playtests did on 21 October.
- **The paper playtests** (`docs/playtests/paper-1/`), resumed in a fresh Opus session.
  - *Done:* the method, the panel (all three rank the paper and the mystery on top), the world pack, calibration's openings, and the game masters' brief.
  - *Running:* the cards, the pre-registration, calibration, the sessions, the analysis, the redesign and the report (`README.md`).
  - *The report* scores each concept twice, ready today and potential.
  - *The AI-playtesting fixes apply:* persona crossed with model, the game master audited with a fact ledger, a known-weak calibration game, and predictions and needs as headline measures.
  - *Its main output* is the must-improve register.
  - *Paused (22 October, about 01:45, Øystein agreed):* 11 of the 24 runs are played and scored (four mystery, seven paper; the last eight were in flight at the pause), then a short interim note (`docs/playtests/paper-1/analysis/interim.md`) says what they show and what the other 13 runs would add. Nothing more runs until Øystein decides. The note landed (`688f12f`). No concept held its players (exit interest about 3 of 10), the lives-on-against-off results are small or confounded by model, four method fixes are needed first, and the other 13 runs would cost 12 to 15% of the week. Decided (Øystein, 22 October, "continue" on the recommendation): don't run them now; redesign the concepts from the needs (kin, what moves the paper's meters, who found and certified the dead, which the engine doesn't record), then test, with people where possible. The handover is `paper-playtests-paused.md` in the notes folder. Why: nothing this week depends on the answer; half the AI players praised the known-weak game, so their taste answers are weak (predictions, understanding and needs still hold); and the weekly went from 27% to 34% in an hour. Real people playing the greybox (1g) should tell us more than more AI runs.
  - *Usage (21 October, 21:15):* the lean design was chosen: 24 runs (the paper, the mystery and the club; lives on and off; four kinds of player), about 30% of the week, from 00:30. The full 72 runs would take about 90%, and the port needs the rest. The most decisive runs go first. The playtests stop at a run boundary if the weekly passes 55%. The other 48 runs wait until after Monday's reset, and run only if the lean results leave the ranking open.
- **The gully port,** above (Tonight).

When the interim note lands, the main session reads it and puts the choice (resume, or wait for people in the greybox) to Øystein. When a full playtest report lands:
1. An Opus agent checks it against the sessions.
2. Publish it as a private Artifact page for Øystein, with charts of engagement over rounds, lives on against lives off, and the ranking (promised to him).
3. One Fable review of what the playtests taught, from a lean packet. Opus agents digest the report first, then Fable judges the must-improve register and the first-game options' recommendation together.
4. Post the register on #60, short, with links.

**Housekeeping: the dates.** Many labels say "22 October" for work done on 20 or 21 October; they were first written in the early hours of 21 October. Fix them from `git blame`, setting each label to the date of the commit that wrote it. Check each change by eye, since a line like "21 and 22 October" needs more than a swap. Leave real dates alone: the Bergen photo, the 1998 records, `usage_scan.py`'s range, and the playtests' own files while they run.

Then, on Opus:
- a review of the playtest programme (`docs/research/playtesting.md`);
- the camera and play-craft studies' unread masters, before the greybox (1g): Naughty Dog, Insomniac, Mario Odyssey, the alley cameras, BG3's Lower City, the GDC slides.

## Waiting for Øystein

**Decided by Øystein, 21 October, as recommended:** the town system's scope and the eras after 1989 (`docs/town-system.md` §9), and how people take part in the playtests: a neutral friend moderates strangers, recruits are friends of friends, voices are recorded only with consent (`docs/research/playtesting.md`). Method choices are ours: no reloading in tests, and the record shown only after scoring.

**What goes to Øystein** (scope, play and permissions only, each with a recommendation; everything else is decided, recorded with its reasons, and shown to him as finished work he can overturn):
- the walk mode at eye level, and whether people react to the camera, are tested in the greybox too (`docs/plan.md`, 1g).
- the camera's play is settled by testing in the greybox, not by opinion (Øystein: "we have to test this"). See `docs/plan.md`, 1g.
- after the port: installing Unity's IL2CPP module, to compare the player's rebuild times with Mono (scale test; `docs/research/building-blocks-decisions.md` §15). Recommended: yes, when step 5 needs it.
- the reference downloads: approved (21 October). Each file is listed for him with its source and size before it is downloaded: Stavanger's rock, water, city-archive photos for houses and dress, and the large GDC decks.
- which game comes first. Nothing is decided. The interface study designed for an observer (one of the three examples in `docs/living-world.md`, the three dials) as a test case; its play choices are defaults kept for when a game is designed (`docs/research/interface-and-inspection.md`, For Øystein).

**Look and craft questions are ours** (Øystein, 22 October: "You have to figure these things out. As long as we are critical and only aim for high quality, this should answer itself."). They are decided on frames and motion sheets, with strict reviews, and Øystein judges the milestones. This covers the night sky's colour, lamp glass and the tonemapper; the brush's size by octaves and any boil; and near ground cover as strokes or blades.

## Decided (22 October; don't reopen without Øystein)

- **The architecture's decisions are delegated** (Øystein: "I trust you know how to handle this feedback, and based on a good analysis make the correct decisions moving forward"). Only taste, scope and play go to him.
- **The architecture's four questions, answered as recommended** (Øystein, 21 October; `docs/research/building-blocks-decisions.md` §14):
  - every proper name is an English placeholder for now, kept in `packs/stavanger-1989/names.json`, with lettering ready for æ, ø and å;
  - hand-split wall stones stay unique; a large library is asked about only if the scale test's memory for unique close chunks breaks the pool;
  - the painted far town's look test runs after the gully port and before House A's far level;
  - git history isn't rewritten now; revisit at LT1's merge.
- **Work runs without waiting for Øystein** (21 October, evening: "I just want you to handle things tonight, unless it is super important, you can just continue working"). Sessions carry the plan on, start the next step when the one before reports, and bring him only what is truly his.
- **The reference machine** is an ordinary computer, the M4 Mac mini: 60 fps at 1440p at default settings, with no gaming PC needed (`docs/foundations.md`).
- **Cold readers are model readers,** in the engine's blind method (`docs/foundations.md`).
- **How years pass in play** depends on the game, from a week to generations. The screen follows the record, and play changes the record (`docs/town-system.md`).
- **Show from 1989, remember from 1870** (Øystein, 22 October: "things will change, grow older, deteriorate, trees will grow, stairs will be worn down, shops will open, but in the future, not 100 years in the past as well"):
  - The world on screen starts in 1989 and changes forward: ageing, wear, growth, works, and shops opening and closing.
  - The past exists only as the starting record that explains 1989's look: when each thing was built, repaired and kept, and by whom. It is generated once by rule and never rendered.
  - Era content is made only for what survives into 1989 (buildings and their parts, stone, trees, old signs).
  - A game that starts earlier adds its own eras.
- **The player's acts change the 3D world** as anyone's do, through the record (Øystein: "they should definitely be reflected in the 3d environment"). Whether the player's own mark is also made noticeable is part of the creative exploration of time.
- **Showing time: repainted stroke by stroke leads; the toggle in place is the baseline it must beat** (Øystein, 21 October, on 1f's sheet). In 1f, stroke by stroke found 7 of 8 changes with no false claim, against 6 for the toggle and 3 for the window. That was one reader each, so both go to more readers and to people as a switch in the greybox (1g). The photograph held at its spot stays, for close views only. The exploration stays wide (Øystein: "there are many cool ways to show time progressing, we should try to be very creative here"), within the constraints in `docs/research/time-on-screen.md`.
- **Signs and street text are in English** (Øystein, 22 October), lettered in each era's styles.
- **Scenes are written, not voiced.** No motion-capture sessions: motion comes from free libraries, edited against video (`docs/living-world.md`).
- **The town stands on Stavanger's phyllite** (`docs/stone.md`).
- **Nothing repeats unless it was factory-made** (Øystein, on stairs). No Houdini: its free version forbids commercial use, and there is no money for Indie. No commissions; free and open bases only.
- **A dense town, not a metropolis, for now** (Øystein, 22 October). The first world is a rich harbour town of a few hundred buildings. The architecture stays open to bigger cities, with every choice still costed per building and per kilometre of street, but no metropolis work until a game needs one.
- **The C# port is accepted** (Øystein: "you know best"). Parts are made offline in Blender; the town is assembled in the game in C#, so play can change it (`docs/research/where-generation-runs.md`).
- **Repetition only where things really were mass-produced** (Øystein: "you know best"). Bricks, roof tiles, factory windows and doors, catalogue houses, and setts (hand-split but to standard sizes) come from libraries. Each is always varied by placement, wear and history. Everything made by hand for one place is its own.
- **Names are English placeholders for now:** shops, streets, people, the town itself. Øystein will name things himself later, so every name lives as data in one place and can be replaced without touching anything else.
- **The town's variety comes from its districts and eras** (Øystein: "if we think Stavanger, you have Gamle Stavanger, Eiganes, 1970s and 80s factory built, as well as more fancy brick and masonry houses; limiting it too much would take something away"). Each house type and era gets its own kit: the old town's small wooden houses; the villas, which were often bespoke; the catalogue houses of the 1970s and 80s; brick and masonry. A part comes from a library only where it truly was factory-made, and bespoke houses get bespoke parts.
- **The 1989 town is made once and curated** (Øystein: "as long as we can change this later"), with records by rule. It is stored so it can be regenerated, edited, or replaced later by a growth simulation or the engine's own past.
- **History is concentrated where the stories are, and built to grow** (Øystein: "as long as we can build this out later"). A shared weathering bake keeps every surface true but quiet; the full layers go where a view's stories are; the layer stack lets any layer be added to any kind later without rebuilding it.
- **A game, not a walking simulator** (Øystein, 21 October; `CLAUDE.md`). Every concept needs goals, challenge, stakes, mastery, failure, and decisions that cost something. Reading the world is a skill that pays off in play, not the play itself.
- **People are their own research project, with great care** (Øystein). Until that step, people are blockout figures: grey bodies with readable silhouettes and simple motion. Gameplay and ideas are tested with them early, as in normal game development, before everything looks finished (Øystein, 22 October). How people are drawn and stylised is not settled by any shortcut; it is studied and tested in its own step.
- **The rules in `CLAUDE.md`:** reuse systems, never looks; research the subject and the craft before building; stop and reflect when work reveals a gap.

## Engine and the shared goal

- **Engine:** round 41 is kept (lines and reasons a reader can trust). The human test comes after round 42, and homes after round 43 with the front door's part two (Understory's SUMMARY.md and reports/overstory/, read on 21 October). Notes between the two projects live in Understory's reports/overstory/. **A real run is here:** `fixtures/engine/understory-world-9989.json`, with 119 people, 2,635 events from 2026 to 2036, places of work, cafés, festivals and four bands. It has no buildings yet, and its years start in 2026 until a setting's start year (#23). Requests and status are in `docs/engine-requests.md`.
- **Shared goal:** `CLAUDE.md` ("What it is for") states Overstory's question and the draft exit criteria, to agree with Øystein. The band is proposed as a shared milestone with the engine (`docs/engine-requests.md`, open items).
