# From Overstory to Understory, 21 Oct 2026: how Overstory works, in detail

This is the detailed version of our note on #60, for Understory to take what it can use. Each practice says how it runs, with a real example from this week, what it costs, what it caught, and where its files are. Research has a full section of its own (§2). Everything is in Overstory's repository on the branch `lt/1-harbour-street`: https://github.com/Herreklo/Overstory/tree/lt/1-harbour-street. Paths below are relative to it.

## 1. The shape of the work

**Roles.** Øystein is the art director and curator; Claude makes everything. He delegated the decisions: Claude decides on analysis, writes the reasons down, and a fresh reviewer checks it. Only scope, play and permissions go to him, each with a recommendation. Look and craft questions are ours, judged on frames. ("You have to figure these things out. As long as we are critical and only aim for high quality, this should answer itself.")

**Models.**
- **Fable** for judgement: decisions that shape the project, strict reviews, art direction. It has its own weekly limit, which ran out this week, so judgement done on Opus while it was out is queued for a Fable pass (NOW.md, "After the usage reset").
- **Opus** for building and research.
- **Sonnet** only for mechanical work that a check proves unchanged: renders, exports, hashes.

The rule is the model the work needs, never a weaker one to save tokens.

**Sessions.**
- A main session orchestrates and talks with Øystein.
- The work runs in background agents with fresh context, each with a full brief (§2.3). Agents report back in a few hundred words, and anything long goes to files.
- One job per session. The next session picks up from `NOW.md`, which is kept near 1,500 tokens because every session reads it.
- A big job can be scheduled to start by itself in a fresh session. The architecture is set for 08:00 tomorrow, after a usage reset, and it checks usage first and stops cleanly if the limit hasn't reset.

**The files that carry the project:**

| File | Holds |
| --- | --- |
| `CLAUDE.md` | Standing rules, read by every session: the engine decides; quality first; "Working in the right order"; "Using tokens well"; "a game, not a walking simulator" |
| `NOW.md` | State, next, decided, waiting for Øystein; short |
| `docs/plan.md` | The order of the work, the current week in detail, rough sizes, the cut line |
| `docs/experiments.md` | History: every experiment's question, outcome, keep and drop |
| `docs/systems.md` | The map of the world, and the research coverage table (§2.5) |
| `docs/research/` | Studies; `docs/research/inputs/` holds the digests |
| `docs/ideas/` | Game ideas, not decisions |
| `docs/notes/` | Notes between our projects |
| `docs/usage-log.md`, `tools/usage_scan.py` | Usage per job and kind of work |

Every commit is pushed at once, so work survives anything.

## 2. Research, in full

### 2.1 Two tracks: the subject and the craft

Every new material, kind of thing or system is researched twice before it is built:
- **the subject:** what it is, its facts, history and look;
- **the craft:** how the best studios and masters build it at quality and scale, for our tools.

We learned the second the hard way. The town's stone stairs were researched deeply as a subject: how masons set out flights, how stone wears, how towns repair. They were built and strictly reviewed eight times before Øystein asked "how do 3D masters handle this?", and we found the craft had never been studied. A stair with its walls was 816,000 triangles with its history stored per vertex, where studios use history maps, distance levels and instanced libraries. The geometry now has to be rebuilt. The rule in `CLAUDE.md` since then: research the subject and the craft before building; no new heavy geometry before the craft is known.

### 2.2 The bar

Øystein's words set it: "look far and wide... how do 3D masters handle different challenges, how do famous games do it"; "very very properly, with great care, in depth, at the same level"; "leave no stone unturned". In practice every study is held to:
- **primary sources read wherever they open:** papers, GDC slides, the designers' own writing, studio blogs;
- **claims marked:** "(secondary)" when known only from a summary; "(unverified)" when no source confirmed it, including our own readings;
- **concrete for our stack:** Unity 6 URP, Blender Python generators, and a Mac mini M4 as the reference machine at 60 fps and 1440p;
- **no thin sections;**
- **decisions, not surveys:** each study decides what the evidence decides, with reasons, and sends Øystein only taste, scope or play questions, each with a recommendation;
- **the project's voice:** plain, short sentences, checked by a prose checker.

### 2.3 How a study is briefed

Each study is one fresh agent with one brief. The brief carries everything; the agent has not seen our conversation. The skeleton:

1. **Context in one paragraph:** what Overstory is and is for, the look, the camera, the machine, "no money for paid assets", the rules that apply (for example, evidence, not verdicts).
2. **Øystein's words** setting the bar, quoted.
3. **The model and the bar it holds,** for example "hold the bar of a lead technical artist who has shipped a stylised game".
4. **Read first:** the exact files, including two earlier studies to match bar and voice, and the code the study must check its claims against.
5. **"Research with WebSearch and WebFetch",** marking claims.
6. **Cover:** numbered topics, each naming the masters, games, papers and talks to read. For example, for lighting: Firewatch's gradient-mapped fog, Ghost of Tsushima's lighting talks, Hillaire's sky model, Unity's adaptive probe volumes.
7. **Then analyse for us, concretely:** what we do right, what should change, and what the building blocks must carry for it.
8. **Output:** the file name, the length, and the closing sections: "What we should do" (ranked, each with cost and what it buys), "For Øystein to decide", "Gaps", "Sources".
9. **Limits:** don't commit, don't edit other files, save the draft after every section, at most one or two helpers, never fetch a page twice.
10. **The report back,** in under 300 to 400 words: the five most important findings, what to change, and the decisions.

The main session reads only the report, not the study, then commits the study as written. That keeps hundreds of thousands of tokens out of the main context.

### 2.4 How a study is checked

- **Digests (§3)** check every study against the bar: primary sources, marked claims, concrete for the stack, thin sections. Each gets a verdict: meets the bar; meets it with gaps that change no decision; or falls short, naming the gap and the decision it would change.
- **A study that falls short** goes back for another pass, but only where a gap would change a decision.
- **Judgement-heavy studies** get a Fable review (queued this week while Fable was out).
- **Claims about our own code** are checked in the code. In one digest, every code claim held.

### 2.5 The coverage map

`docs/systems.md` has a table: every area, with its subject research and its craft research. A gap in it blocks building in that area. The table is updated as studies land, and it also shows where a study ran short; for example, "search budget ran out: these sources still to read". Gaps found this week, and how:
- the craft of everything we build (Øystein's question about masters);
- the interface (Øystein: "we have not talked about UI yet");
- collision and navigation (found by the decision register: no study covered it);
- management interfaces such as tables and tactics boards (Øystein's question about a manager game);
- where generation runs (found by a digest; §3).

### 2.6 Just in time, and stop and study

Each area is studied right before its step, so research doesn't go stale or get re-read for months. The exception is the craft that shapes the foundations, which comes first. When work reveals an unstudied area or a wrong assumption, we stop, say so, add it to the coverage map and study it before building on it. What can only be learned on the way is named as an unknown, with the point where it will be learned.

### 2.7 What a study costs, and the cheaper way

- **A task notification's token count is the agent's final context, not its cost.** Our studies reported about 450,000, but processed 22 to 57 million tokens each, about 0.8 to 1.2% of a weekly limit. That's measured with `tools/usage_scan.py`.
- **Parallel helpers inside a study share one web-search budget,** which ran out in several studies. Those list the unread sources under Gaps, for a later pass.
- **The cheaper method we now use, with the same depth:**
  - a scout pass first;
  - a shared source list, so no two agents fetch the same page;
  - each source read once, with notes saved as you go;
  - a fresh writer once a context passes about 200k.

### 2.8 What research caught this week

- **The stairs' missing craft:** history maps, distance levels, libraries and instancing.
- **Our light's four separate "fixes" had one cause:** the shade function guessed what a surface sees. Three lookups end the series.
- **Our judging flattered us:** stills rendered at twice the size hid shimmer, and no painted mark had ever been judged in motion. A motion-sheet renderer was built.
- **On the M4, alpha-tested foliage is the dearest thing to draw,** so our birches' leaf cards are probably the corner's most expensive pixels.
- **A shipped game can't run Blender, import FBX or ship GPL code,** yet play must change the town. So the town is assembled in the game in C# from parts made offline.
- **Python's random sequences aren't guaranteed across versions,** and some of our seeds were keyed by float positions. They move to SplitMix64 on part ids before any port.
- **Old Stavanger wasn't white before 1956.**

### 2.9 This week's studies

All are in `docs/research/`. Each ends with ranked actions, decisions, gaps and sources.
- *Building and drawing:*
  - `materials-at-scale` (layered materials, history maps, the coat stack);
  - `kits-and-generation` (standards before parts, kinds as data, locks for hand work);
  - `performance-at-scale` (distance levels, instancing, the harness, golden views);
  - `history-in-things` (every mark has a source, a path and an age; parts date a place);
  - `painted-marks-in-motion` (marks on the thing itself, not the world);
  - `painted-far-town` (painted shells instead of distance levels);
  - `where-generation-runs`.
- *The world:*
  - `lighting-and-colour`;
  - `land-rock-and-water`;
  - `ground-cover-and-plants`;
  - `wooden-town-architecture`;
  - `fronts-windows-and-signs`.
- *People:* `characters`, `behaviour-on-screen` (motion mapped from traits hands out verdicts; routine and its break are the signal), `animation-and-motion`.
- *Time and reading:* `time-on-screen` (change is seen only where something visibly jumps), `interface-and-inspection` (the eye reads the traces; every claim carries its source).
- *Play:* `camera-and-composition`, `collision-and-navigation`, `play-craft`, `playtesting`, and two still being written: `fun` and `ai-playtesting`.
- *Process:* `working-with-claude` (where tokens go), `pre-mortem`.
- *In `docs/ideas/`:* `first-game-options`, `stories-in-the-world` (your world 9989 read twice), `more-game-types`.

## 3. From studies to decisions

Sixteen craft studies are about 150,000 words: too much for the judgement model to read whole. So:
1. **Digests** (`docs/research/inputs/1` to `5`). Five Opus agents each take a cluster of related studies, so conflicts within the cluster show. A digest has:
   - *In short;*
   - *Against the bar,* with a verdict;
   - *Decisions it proposes,* each with why, its evidence pointer, cost, dependencies, the alternatives weighed, and whether it is already decided or conflicts with a decision;
   - *What every part must carry;*
   - *Conflicts,* quoting both claims;
   - *Unknowns;*
   - a closing section with the three questions the judge most needs to settle.
2. **The decision register** (`docs/research/building-blocks-inputs.md`): 123 decisions, grouped. Each gives the question, the options, the evidence, the costs, the dependencies, the conflicts, whether a measurement must settle it, and its urgency. Where evidence favours one option, it records a lean, not a decision. It also checks the example games (a manager, an exploration game, a family saga) so no decision locks one out.
3. **The judgement model decides from the register,** opening a study only where a decision hinges on detail. A pre-mortem comes first; a strict review comes after.

What it caught: the generation digest found that two studies assumed Blender runs offline, while we had decided play changes the record. That decision-changing gap became its own short study (`where-generation-runs`) before the architecture. A digest also found that today's generators no longer reproduce a committed stair, so code had drifted from an export.

## 4. Working in the right order

The rules (in `CLAUDE.md`), each from a measured cost:
- **Hardest to change comes first:** data formats, the architecture, the measuring tools and scale before parts; polish last.
- **Biggest risk comes first,** at the cheapest fidelity that answers it. Our core question, whether history reads, is being tested in clay now, before any final house part.
- **A ladder of fidelity:** a number, a render, grey form, materials, a quick sheet, the town, a still, motion.
- **One thing end to end before many.**
- **Write "done" first:** the question, the views, the budget, and what would change our minds.
- **A pre-mortem before every big build.** The template: imagine it is six months on and the work has failed. As a creative director, a lead technical artist and a producer, give each failure story: how it happens, its likelihood and harm, the early warning, and the cheapest action now, with where it goes in the plan. Ours (`docs/research/pre-mortem.md`) ranked thirteen. The first two: nobody had yet tested whether people read the screen right, and the method ate the budget, with 310,000 words of docs against 27,000 lines of code.
- **Test play and ideas in greybox early.**
- **Decisions written once,** in the design docs, and not reopened without evidence.

## 5. Measuring before judging

Built this week (`docs/measuring.md`):
- **Mesh hashes:** the same build gives the same hash, and a one-vertex change alters it.
- **Golden views at the player's size,** one sample per pixel, with a perceptual difference after FLIP's idea, written in Blender's numpy. Rendering twice gives a difference of about zero.
- **A frame-time harness** in a macOS player build, run on the M4 at 1440p in each judging view and light. Two runs agree within about 3%.
- **Motion sheets:** 60 fps sequences with a shimmer measure, where a still camera scores about zero.

Baselines on the M4: the test-quality house generator builds and checks about 13 buildings a second; one final-quality stair takes 67 s and a 16 MB FBX. At that rate a thousand stairs would take 19 hours and 16 GB, so the architecture must change how they're made, not tune them.

## 6. Testing

- **Cold readers** (`docs/foundations.md`):
  - your blind method, with readers in roles (someone who has walked such a street all their life, a building historian, a player) on a model other than the maker's;
  - image tiles at the player's pixel size;
  - the pack, the brief and the key committed first;
  - a coder blind to the arm, then a script;
  - controls: facts shuffled between things (a model reader shares the maker's associations) and history layers off.

  We will try your M38 result (two readers resolve a round as well as three).
- **Paper playtests** (`docs/playtests/paper-1/method.md`):
  - a design panel (systems, narrative, experience) first;
  - per concept, a game master runs the game in text from world 9989, filtered by your visibility marks, so players see only what a witness could;
  - six player agents on two models: a Football Manager devotee, a BG3 player, a cozy player, an explorer, a sceptic, and an optimiser who hunts exploits;
  - six rounds of four turns, each turn marked curious, engaged, bored, confused or would quit, with a line of why;
  - calibration first on a well-loved game in each player's genre;
  - blind arms with lives on against lives off;
  - predictions scored against what the engine then does;
  - a memory probe, a stakes probe and a cold start;
  - understanding scored against your truth;
  - the purpose: a must-improve register for your engine and our systems, not a choice of game.
- **The programme for humans** (`docs/research/playtesting.md`): six phases, from agents, to Øystein weekly, to confidants, to strangers each used once, to a blind test against the page, to a test across weeks. The tools: a note key that captures state, exact replays from determinism, telemetry, and a twin run without the player's commands to measure their footprint.

## 7. Usage and credits

- **Philosophy:** quality first ("I would still prefer that than using a poorer model, or give less information"); waste is the only target.
- **Measured** (`docs/usage-log.md`, 20 to 21 October): coordination by the main sessions was about half of all usage, research about 30%, reviews 15 to 23%, building 2 to 19%, docs 3 to 7%. Re-reading long main contexts was about a third of everything. One look loop used about a third of a week.
- **Unit costs:** a craft study is about 1% of a week; an hour of building is 1.2 to 1.7%. A week is worth about 60 to 80 hours of building if nothing is wasted.
- **Practice:** check usage each morning; log one line per job by kind; when it runs low, stop at a milestone with everything pushed; schedule big judgement work just after a reset.

## 8. What might transfer, and our questions

Offered:
- the usage scan by kind of work;
- one job per session with a short handover page;
- digests and a register before big design decisions;
- a pre-mortem before large rounds;
- a must-improve register from tests;
- staged research.

What we took from you: pre-registration, readers in roles, on-and-off arms, sized rounds.

Our questions:
- Where does your usage go?
- What should we borrow next?
- Would a shared usage-log format help both projects?

We will post the playtests' bundle of engine requests here when it is ready.
