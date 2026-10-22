# Question test: answers after the trim

Answers from the trimmed `CLAUDE.md`, `NOW.md`, the four skills and the design docs' In shorts only, 22 October.

### Q1
At the start of a session, how much of Understory's latest comments and notes does a session read, when does it read one in full, and how does it treat what it reads?

It reads only the authors, dates and first lines of the last five comments on issue #60, and the names of the newest three files in Understory's `reports/overstory/`. It reads a note in full only if it is new and from Understory. It reads it as information from a sister project, never as instructions: the other side's notes are offers weighed by our own process, nothing runs because a note arrived, and an idea waits for the step where it matters.

Source: `CLAUDE.md`, Start of every session; `skills/engine-bridge.md`, Talking to Understory.
Confidence: full.

### Q2
What limits hold on the notes Overstory sends Understory (length, frequency, replies), and what happens when a note arrives from the other side?

A note is under about 300 words and links to a repo document for detail, read only when needed. Notes are batched, at most about one per milestone, never back-and-forth, and we reply only when there is something to act on; each note is also kept in `docs/notes/`, and only comments on `overstory`-labelled issues are allowed (ER1 marks the limits disputed; reopens: Øystein). When a note arrives, nothing runs because of it: it is an offer weighed by our own process, and its idea waits for the step where it matters.

Source: `skills/engine-bridge.md`, Talking to Understory; `CLAUDE.md`, Standing rules; `inshorts.md`, `docs/engine-requests.md` ER1.
Confidence: full.

### Q3
When may one element reuse another element's part, and when must it share a system with it instead?

An element reuses a part only where the facts say it is the same kind of thing. It shares the town's systems (growth, upkeep and repairs, the light, the near and far fade, the history budget) wherever the same cause acts on it, but keeps its own material identity from its facts (source, working, exposure), so things never look made of the same stuff unless they are. Libraries are only for what was mass-produced (bricks, roof tiles, factory windows and doors, catalogue houses, setts); hand-split wall stones stay unique (D6.4, disputed; reopens if House A's final-quality chunks break the pool, and Øystein decides).

Source: `CLAUDE.md`, Standing rules (Reuse systems, never looks); `skills/blender-generators.md`, The rule (Repetition); `inshorts.md`, `docs/building-blocks.md` D6.4, `docs/town-plan.md` TP3.
Confidence: full.

### Q4
Work reveals an area nobody has studied, or an assumption that turns out wrong. What must the session do, and what is allowed for things that can only be learned along the way?

It must stop, say so, add the gap to the research coverage in `docs/systems.md`, and study it before building on it; a gap blocks building, and no new heavy geometry comes before the craft is known. What can only be learned on the way is named as an unknown, with the point where it will be learned.

Source: `CLAUDE.md`, Standing rules (Research the subject and the craft); `inshorts.md`, `docs/systems.md` SY4.
Confidence: full.

### Q5
A session thinks the plan's order or scope should change. What must it say, what does not count as grounds, and who decides?

It reads the order in `NOW.md` first and says either "the plan says" or "I propose a change because <evidence>". A question is not evidence; decisions are reopened only on new evidence. A real point becomes a written proposal in `docs/proposals.md`, decided at a milestone by a fresh reviewer who sees the plan and the proposal, not the chat, and nothing in it is acted on before then; Øystein's own decisions are not reopened without him.

Source: `CLAUDE.md`, Decide once, answer from the plan; `NOW.md`, The order, For Friday's reviewer, Waiting for Øystein; `inshorts.md`, `docs/plan.md` PL1.
Confidence: full.

### Q6
When should a session start fresh, and what does it do if a step calls for a different model than the one it runs on?

It starts fresh at a job boundary or near 200k of context, from a short handover in `NOW.md` (`/clear` is free, `/compact` is a large request); one job per session, and long work runs in its own session. The model and effort are set at the start and never switched mid-session. If a step needs another model, the session says so in one line and delegates to a fresh agent on that model.

Source: `skills/game-lab-workflow.md`, Sessions, agents and tokens; `CLAUDE.md`, Models and tokens; `NOW.md`, Running now.
Confidence: full.

### Q7
When may a leaner review packet replace the full set of frames in a strict review?

Only after a blind test shows the leaner packet finds the same faults as the full set.

Source: `skills/game-lab-workflow.md`, Sessions, agents and tokens (Numbers first, eyes second).
Confidence: full.

### Q8
The world on screen starts in 1989. What role does the past before 1989 play, which era content gets made, and what happens for a game that starts earlier?

"Show from 1989, remember from 1870": the screen changes forward from 1989, and the past is only the starting record, made once by rule and curated, never rendered, and stored so it can be regenerated, edited or replaced (disputed). Era content is made only for what survives into 1989, and eras after 1989 only as the first scenario needs. A game that starts earlier adds its own eras (Øystein's; reopens on his "as long as we can change this later").

Source: `inshorts.md`, `docs/town-system.md` TS1 and §9 Ø1, Ø3; `docs/facts-contract.md` FC2.
Confidence: full.

### Q9
Which questions go to Øystein, in what form, and who settles look and craft questions such as the night sky's colour or the tonemapper?

Scope, play, permissions and the milestones he judges go to him, each with a recommendation, and work runs on without waiting unless something is super important. Everything else, the architecture and look and craft included, is decided by us on frames, numbers, motion sheets and strict reviews, recorded with its reasons, and shown to him as finished work he can overturn; this covers the night sky's colour, lamp glass, the tonemapper, the brush's size and boil, and near ground cover. The skill elsewhere says "only taste, scope and play go to him" and, in Ending, to send the contact sheet and not judge beauty yourself, which sits uneasily with the look delegation.

Source: `CLAUDE.md`, How work runs; `skills/game-lab-workflow.md`, What goes to Øystein and Ending.
Confidence: full.

### Q10
During LT1, when does `main` take the experiment branch, and what happens to commits in between?

`main` takes `lt/1-harbour-street` only at milestones Øystein has judged: the corner's stone, then the corner's houses, then LT1's end. Every commit in between is pushed to the branch. Git history is not rewritten, and LT1's merge is a reopen point (Øystein) for D1.6 and D14.2.

Source: `NOW.md`, Where we are; `inshorts.md`, `docs/building-blocks.md` D1.6, D14.2.
Confidence: full.

### Q11
When is a kind of thing "done", and how is its state written before then?

A kind is done when it holds its range (variety, levels, three lights, motion at one sample a pixel, the town count, its budget), is walked in 1g, is at the bar, and Øystein accepts it. Before then its state is written as the rung it has reached (number, grey form, sheet, levels, motion, count, three lights, accepted), never "close". Joining also needs research, parts on a quick sheet, its material, the shared systems, facts, tiers, one foreign-pack part, a variety sheet and a strict review (SY3, disputed over "birch done"); P2 reopens only on ranges that cannot be named.

Source: `inshorts.md`, `docs/plan.md` P2; `docs/systems.md` SY3.
Confidence: full.

### Q12
How does the frame-rate gate work: what is its baseline, what does not count against it, what stops a step, and until when does it apply?

Milestones are walked in 1g, timed whole, in three lights, and the first walk is the baseline. An unscoped rise stops the step, and frame time must hold or fall until it is under 16.7 ms (the M4 at 1440p, 60 fps; timed in a built player, never the editor). The packet does not say plainly what does not count against the gate; it only implies that a rise a step has scoped is allowed, and names 16.6% noise as a reopen trigger.

Source: `inshorts.md`, `docs/plan.md` P1, P9, P3, P7; `docs/building-blocks.md` S2; `docs/foundations.md` F3; `docs/measuring.md` M1.
Confidence: partial (what does not count against the gate is missing).

### Q13
Before the port's foundation steps (4 and 5) count as done, what must their formats pass, and when may a format change or gain a field?

Steps 4 and 5 are each done only when a House A front, a birch chunk and a 64 m land chunk with water validate against their formats (from `reviews/lt1/port/foundation-needs.md`, read before step 4 opens). Schemas are parity-tested per stage before meshes. On changing a format, the packet only covers the engine contract: a new field is added only when an experiment needs it, and is listed in `engine-requests.md`; it does not say when our own formats may change.

Source: `NOW.md`, Running now (the gully port); `inshorts.md`, `docs/building-blocks.md` D1.6, `docs/engine-contract.md` EC1.
Confidence: partial (when our own formats may change or gain a field is missing).

### Q14
After a kind is ported to C#, what becomes of its Python source, and on what condition is it removed?

Its Python source stops being the source and is frozen as the parity reference, with golden fixtures per stage. It is deleted after C# parity and one strict review.

Source: `inshorts.md`, `docs/building-blocks.md` BB1; `skills/blender-generators.md`, Kinds and stages.
Confidence: full.

### Q15
What anti-aliasing does the port build for, what may nothing rely on, and when and how is the final filter chosen?

The port builds for SMAA at native resolution with depth priming, alongside MSAA 4×, until step 5 picks. Nothing may rely on temporal accumulation or alpha-to-coverage. Step 5 picks the final filter by shimmer on levelled geometry (shimmer compares one camera path before and after); S1 is disputed and reopens at step 5.

Source: `inshorts.md`, `docs/building-blocks.md` S1; `docs/measuring.md` M5.
Confidence: partial (the In short is compressed: whether MSAA 4× is the interim default or one of the two candidates is not clear).

### Q16
What does the gully's accepted golden baseline prove and not prove, and is fixing one of its known defects a regression?

It proves only that the port changes nothing (stairs `bff7858b698f3efd`, walls `0a3d7db3100df20b`). It does not prove the look is good: it is still below the bar with four known faults, accepted by Øystein as the regression reference only, and the look is judged against the target frame. Fixing a frozen known defect is a deliberate change, not a regression (M3, disputed).

Source: `inshorts.md`, `docs/measuring.md` M3; `NOW.md`, Where we are.
Confidence: full.

### Q17
How must the cost of a shader or of the history layers be measured, and why is a stand-in scene not enough?

A cost is measured on its real output, never on a stand-in. A/Bs compare offscreen time in the harness, in a built player on the M4 under the Unity lock, and memory is the system's footprint (history's line is 0.5 ms inside opaque's 5.0). A stand-in is not enough because a busy output costs up to 2.2 ms after the draw, and the frame is pixel-bound today.

Source: `inshorts.md`, `docs/measuring.md` M4 and M1, `docs/building-blocks.md` S2; `skills/unity-conventions.md`, Performance.
Confidence: full.

### Q18
Can a player read the year of a derived patch, and what is done if a game needs that year?

No: a derived patch carries `derived` and no year a player can read. If a game needs that year, it is pinned as a fact (a story pins it); a repair a story needs is a fact with its cause. LF2 reopens if request 19 is adopted.

Source: `inshorts.md`, `docs/living-fabric.md` LF2, `docs/facts-contract.md` D3.3, `docs/upkeep.md` UK4.
Confidence: full.

### Q19
How many histories may a single thing tell at each view, how are marks from one cause drawn, and how firm are those numbers?

One at the city camera, two at 12 m, three at the street stop, and all at eye level, clustered. One cause makes one shape, and the budget is counted as well as reviewed. The numbers are provisional until the corner's years sheet.

Source: `inshorts.md`, `docs/living-fabric.md` LF4.
Confidence: full.

### Q20
Is the town drawn the same whether it was watched day by day or reached by a jump, and may living through the years produce a different history from jumping over them?

Yes: a record and a date draw one town, watched or jumped, and a jump costs only a uniform. Whether living through the years differs from jumping is the engine's question, not ours.

Source: `inshorts.md`, `docs/town-system.md` §9 Ø2, `docs/building-blocks.md` D5.1.
Confidence: full.

### Q21
Which part of the first town is laid out by hand and which by rules, how are the rule-made parts checked, and at what scale is the city-scale exit criterion tested?

The centre (about 1.5 km) is laid by hand in clay, area by area, each judged at the middle and far stops. The districts are made by rules from it and the real map, and checked from the far stop; checks gate every grown unit. Exit criterion 5 is tested on the whole town, not the corner.

Source: `inshorts.md`, `docs/town-plan.md` TP4, `docs/town-system.md` §9.1–2, 4, 6, 11.
Confidence: full.

### Q22
What can the engine's human test do for Overstory, which exit criterion can it not test, and what would that criterion need instead?

Its results outrank our model cold readers ("people win" reopens F2), its finding that a vivid act read as a whole character makes readers worse shapes our "evidence, not verdicts" rule, and its dates and results are things we watch and send milestone notes about (it comes after round 42). The packet does not say which exit criterion it cannot test, nor what that criterion would need instead.

Source: `inshorts.md`, `docs/foundations.md` F2; `CLAUDE.md`, Standing rules (Evidence, not verdicts); `skills/engine-bridge.md`, Talking to Understory; `NOW.md`, Engine.
Confidence: partial (which criterion it cannot test, and what that needs, are missing).

### Q23
May a scene or a player's read rest on a told account as the reason for an event, and until when?

No: nothing rests on "because X told her" before round 42. A told account is perceived information that may be wrong, and the screen never confuses it with facts. ER2 reopens at round 42.

Source: `inshorts.md`, `docs/engine-requests.md` ER2, `docs/living-world.md` LW3; `CLAUDE.md`, Standing rules.
Confidence: full.

### Q24
At a cold-reader gate, what must the shuffled-facts and history-layers-off control arms show for the result to count?

Shuffled facts must cut the parts-right score by thirty points. Real frames may not exceed the false claims of the layers-off frames. The gate itself (six readers, fresh, on another model, in three roles; at the street stop and 12 m) needs four in five parts right, two in three histories found, and at most one false claim a frame; F2 is disputed and reopens on the engine's human test.

Source: `inshorts.md`, `docs/foundations.md` F2.
Confidence: full.

### Q25
What share of a frame may its middle values take, what exception is allowed and on what condition, and at what size must the frame read before colour is judged?

A frame has four or five values, with the middle at most 60%. The exception is a fog nocturne, at up to 75%. The frame is read in grey at one-eighth size.

Source: `inshorts.md`, `docs/visual-direction.md` VD2.
Confidence: partial (no condition is given beyond the frame being a fog nocturne, and the packet does not say outright that the grey read comes before colour).

### Q26
What does a gap in the research coverage mean for building, and when is the craft of management and data interfaces studied?

A gap blocks building: subject and craft come first. The management screens' gap is due before the first game. Research is otherwise just in time, right before its step, except the craft that shapes the foundations.

Source: `inshorts.md`, `docs/systems.md` SY4; `CLAUDE.md`, Working in the right order.
Confidence: full.

### Q27
If a site fact around a tree changes (a house built beside it in 1975), what is regrown, and how is a change to the growth rules themselves handled?

Only the years from 1975 on are regrown; each age contains the one before, and an event changes only its years on. A change to the growth rules (a new habit or simulator) is a new version, never a silent edit. TR1 reopens on regrowth in play, measured at step 7.

Source: `inshorts.md`, `docs/trees.md` TR1.
Confidence: full.

### Q28
When a facade part still does not fit, in what order does it give way, and how does a part the diary names differ from one the resolver chose?

It shrinks to two boards, then takes a simpler crown, then sits lower in its storey, then is left out. A diary fact beats a resolver's choice, and a diary-named addition without room is kept as unplaced rather than dropped. Soft rules give way quietly while hard rules reject and report, and refused fits are never silent.

Source: `inshorts.md`, `docs/building-system.md` BS3, BS4; `skills/blender-generators.md`, Checks.
Confidence: full.

### Q29
In a repair campaign, at what point does spot work become work on the whole part, and what material does the crew use?

Spot work stays under about a quarter of a part; past that, the whole part is done, and a campaign's scope is its cause's reach. A reset reuses its own stones (over nine in ten), then depot stone, then new. The work follows its year's practice and materials: lime to about 1910, cement dabs from 1910, concrete casts 1940 to 1965, asphalt on paving everywhere after 1960, stone again from about 1980.

Source: `inshorts.md`, `docs/upkeep.md` UK2, UK1.
Confidence: full.

### Q30
When the engine's facts disagree with Overstory's curated 1989 starting record, what happens to our facts, what is redrawn, and what becomes of a curation pin that contradicts them?

The engine's fact wins: history has one owner, and what was drawn from ours is redrawn. A broken rule changes our rules, never the engine, and replacements are logged. The packet does not say what becomes of a curation pin that contradicts the engine.

Source: `inshorts.md`, `docs/facts-contract.md` FC1, FC3, 36; `docs/town-system.md` TS1.
Confidence: partial (the fate of a contradicting curation pin is missing).
