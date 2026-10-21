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

- **Next week (from Monday 26 October): the building blocks.**
  - *Monday:* the architecture (Fable, fresh session) and the measuring tools (Opus) in parallel.
  - *Tuesday:* the scale test, then the architecture's review.
  - *Wednesday to Friday:* the gully ported onto the building blocks as the proof, ending in a strict review and a before-and-after sheet for Øystein.

  The goal, the days, the architecture's scope, the baselines, the cut line and the budget are in `docs/plan.md`.
- **Who starts it:** the chat that wrote this plan starts both Monday sessions when Øystein says go. Otherwise any new session that reads this page can start them.
- **Before Monday (started 22 October, with the week's last budget):** Opus agents are digesting the fourteen studies into `docs/research/inputs/`: a bar check, the decisions each proposes, what every part must carry, the conflicts between studies and the unknowns. A consolidated decision register follows in `docs/research/building-blocks-inputs.md`, so Monday's Fable session starts straight on judgement. The measuring tools are being built (mesh hashes, golden views at the player's size, the frame-time harness, motion sheets; `docs/measuring.md`), so Monday's tools session may find them done. Each is committed as it lands; anything unfinished is picked up on Monday.

## Waiting for Øystein

**What goes to Øystein** (scope, play and permissions only, each with a recommendation; everything else is decided, recorded with its reasons, and shown to him as finished work he can overturn):
- the town system's scope and the eras after 1989 (`docs/town-system.md`);
- his OK for reference downloads (Stavanger's rock, water, city-archive photos for houses and dress, and the large GDC decks the studies could not open), each listed with its source and size first;
- **showing time passing: open, to be explored creatively** (Øystein, 22 October: "there are many cool ways to show time progressing, we should try to be very creative here"):
  - generate many ideas, wide;
  - prototype the best few on the corner through the years (step 4);
  - judge them for beauty by strict review and for readability by the cold readers.

  The perception findings in `docs/research/time-on-screen.md` are constraints, not the answer: change is found where something visibly jumps; hold everything but the year; a cut invites a cause.
- **the C# port** (scope; `docs/research/where-generation-runs.md`). Play changes the record, so the finished game rebuilds the town while it runs. That means plan, life at a date, placement and bakes in C#, with parts made offline in Blender. The port adds about 15 to 22 Opus-days around House A. Recommended: accept it; without it, the world can't change in play.
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
- **Signs and street text are in English** (Øystein, 22 October), lettered in each era's styles.
- **Scenes are written, not voiced.** No motion-capture sessions: motion comes from free libraries, edited against video (`docs/living-world.md`).
- **The town stands on Stavanger's phyllite** (`docs/stone.md`).
- **Nothing repeats unless it was factory-made** (Øystein, on stairs). No Houdini: its free version forbids commercial use, and there is no money for Indie. No commissions; free and open bases only.
- **Build for bigger cities:** every choice is costed per building and per kilometre of street.
- **The rules in `CLAUDE.md`:** reuse systems, never looks; research the subject and the craft before building; stop and reflect when work reveals a gap.

## Engine and the shared goal

- **Engine:** places are workplaces plus ventures that open new ones; places never close, and buildings and homes are not modelled. Read tag `r41` or later; its front door is read-only and shows the truth, for our tools. The engine's order: a reading that counts every fault, the first human test, rounds 42 and 43, then the band for a year with homes (#59), and #22 taken up again; #20 and #23 are paused. The living fabric's requests are tracked in engine issue #60. LT1 and LT2 run on fixtures labelled `authored`. Overstory's cold reader for criterion 1 can ride on the engine's human test (one task after the page). Details are in `docs/engine-requests.md`.
- **Shared goal:** `CLAUDE.md` ("What it is for") states Overstory's question and the draft exit criteria, to agree with Øystein. The band is proposed as a shared milestone with the engine (`docs/engine-requests.md`, open items).
