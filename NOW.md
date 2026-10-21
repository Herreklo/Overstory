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
  - the shared systems: water, wear, growth, upkeep and repairs, detail by distance.
- **Designed:** the living fabric, the town system, upkeep and the foundations (`docs/`).
- **Researched:** the subject of most areas, and the craft of fourteen (`docs/research/`). Coverage and the remaining gaps are in `docs/systems.md`.
- **Why building stopped (22 October):** the craft research came after the stone was built, and the stone shows it. One stair with its walls is about 816,000 triangles, with no distance levels and its history stored per vertex. New heavy geometry is held until the building blocks are designed (Øystein: "these need extreme care... our building blocks; we need to do them perfect, so the rest becomes much easier").

## Next

**The building blocks started early.** The weekly limits reset on the evening of 21 October (all models at 4%, Fable at 3%), so the plan meant for the week of 26 October started then, in the same order. The goal, the days, the architecture's scope, the baselines, the cut line and the budget are in `docs/plan.md`.
1. **The architecture (1a):**
   - *Where:* a session started from the scheduled task `overstory-architecture`, on Opus, with Fable for the pre-mortem and the decisions (`docs/building-blocks.md`).
   - *Next:* the strict review, then Øystein's few questions in one message.
   - *The duplicates:* the task fired three times. The two extra sessions were stopped and archived, and the task is disabled.
2. **Done on 21 October:**
   - the measuring tools, built and accepted (`docs/measuring.md`);
   - the digests (`docs/research/inputs/`) and the decision register (`docs/research/building-blocks-inputs.md`);
   - 1f, the clay time test (`docs/experiments.md`, `reviews/lt1/time/`).
3. **Running in its own session:** the pass budget (what owns the 25 ms floor), the gully's new baseline, and the scale test. Results go to `docs/research/scale-test.md`, and the numbers settle where generation runs and how the town streams.
4. **Then the gully on the building blocks,** ending in a strict review and the proof sheet for Øystein.

## Running now

Each session commits its own work. If one stops, resume it from its files. Long work runs in its own session: the main chat's background agents seem to stop when the chat is cleared, as the playtests did on 21 October.
- **The paper playtests** (`docs/playtests/paper-1/`), resumed in a fresh Opus session.
  - *Done:* the method, the panel (all three rank the paper and the mystery on top), the world pack, calibration's openings, and the game masters' brief.
  - *Running:* the cards, the pre-registration, calibration, the sessions, the analysis, the redesign and the report (`README.md`).
  - *The report* scores each concept twice, ready today and potential.
  - *The AI-playtesting fixes apply:* persona crossed with model, the game master audited with a fact ledger, a known-weak calibration game, and predictions and needs as headline measures.
  - *Its main output* is the must-improve register.
- **The architecture** and **the scale test**, above.

When the playtest report lands:
1. An Opus agent checks it against the sessions.
2. Publish it as a private Artifact page for Øystein, with charts of engagement over rounds, lives on against lives off, and the ranking (promised to him).
3. One Fable review of what the playtests taught, from a lean packet. Opus agents digest the report first, then Fable judges the must-improve register and the first-game options' recommendation together.
4. Post the register on #60, short, with links.

Then, on Opus:
- a review of the playtest programme (`docs/research/playtesting.md`);
- the camera and play-craft studies' unread masters, before the greybox (1g): Naughty Dog, Insomniac, Mario Odyssey, the alley cameras, BG3's Lower City, the GDC slides.

Øystein's answers still open are listed under "Waiting for Øystein" below.

## Waiting for Øystein

**What goes to Øystein** (scope, play and permissions only, each with a recommendation; everything else is decided, recorded with its reasons, and shown to him as finished work he can overturn):
- the town system's scope and the eras after 1989 (`docs/town-system.md`);
- his OK for reference downloads (Stavanger's rock, water, city-archive photos for houses and dress, and the large GDC decks the studies could not open), each listed with its source and size first;
- the walk mode at eye level, and whether people react to the camera, are tested in the greybox too (`docs/plan.md`, 1g).
- the camera's play is settled by testing in the greybox, not by opinion (Øystein: "we have to test this"). See `docs/plan.md`, 1g.
- the people in the playtests (`docs/research/playtesting.md`). Recommended:
  - a neutral friend moderates sessions with strangers;
  - strangers are recruited without a budget, as the study suggests;
  - voice recordings only with consent.

  Method choices are ours: no reloading in tests, and the record shown only after scoring.
- which game comes first. Nothing is decided. The interface study designed for an observer (one of the three examples in `docs/living-world.md`, the three dials) as a test case; its play choices are defaults kept for when a game is designed (`docs/research/interface-and-inspection.md`, For Øystein).

**Look and craft questions are ours** (Øystein, 22 October: "You have to figure these things out. As long as we are critical and only aim for high quality, this should answer itself."). They are decided on frames and motion sheets, with strict reviews, and Øystein judges the milestones. This covers the night sky's colour, lamp glass and the tonemapper; the brush's size by octaves and any boil; and near ground cover as strokes or blades.

## Decided (22 October; don't reopen without Øystein)

- **The architecture's decisions are delegated** (Øystein: "I trust you know how to handle this feedback, and based on a good analysis make the correct decisions moving forward"). Only taste, scope and play go to him.
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
