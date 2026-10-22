# Question test: the re-ask

This re-asks seven questions after the In shorts were fixed, answered from the updated `inshorts.md` with `CLAUDE.md`, `NOW.md` and the four skills unchanged, 22 October.

### Q12
How does the frame-rate gate work: what is its baseline, what does not count against it, what stops a step, and until when does it apply?

Milestones are walked in 1g and timed whole. The first walk is the baseline, and clay counts as scope, so only a rise outside a step's scope counts against the gate. An unscoped rise stops the step, and frame time must hold or fall until it is under 16.7 ms at every judging view in three lights (on the M4 at 1440p, 60 fps, timed in a built player, never the editor). Separately, 1.5 times a box forces a re-plan. The gate reopens if the walk runs over 1.5 times, on 16.6% noise, or on re-plans from boxes.

Source: `inshorts.md`, `docs/plan.md` P1, P9, P3, P7; `docs/foundations.md` F3; `docs/measuring.md` M1; `docs/building-blocks.md` S2.
Confidence: full. "Clay counting as scope" is read here as clay's cost being scoped and so not a rise against the gate. The In short gives the phrase but not that reading in words.

### Q13
Before the port's foundation steps (4 and 5) count as done, what must their formats pass, and when may a format change or gain a field?

Steps 4 and 5 are done when a House A front, a birch chunk and a 64 m land chunk with water validate against their formats unbuilt. A format changes only where a record fails it, and gains no field without a failing record to need it. Schemas are also parity-tested per stage before meshes.

Source: `inshorts.md`, `docs/plan.md` P8, `docs/building-blocks.md` D1.6; `NOW.md`, Running now (the gully port).
Confidence: full.

### Q15
What anti-aliasing does the port build for, what may nothing rely on, and when and how is the final filter chosen?

The port builds for SMAA at native resolution with depth priming, and for STP once every mover writes motion vectors. Nothing may rely on temporal accumulation or alpha-to-coverage. MSAA 4× stays until port step 5 so that step 3's A/B stays clean. At step 5, shimmer and golden views choose the filter on levelled geometry. S1 is disputed and reopens at step 5.

Source: `inshorts.md`, `docs/building-blocks.md` S1; `docs/measuring.md` M5.
Confidence: full.

### Q22
What can the engine's human test do for Overstory, which exit criterion can it not test, and what would that criterion need instead?

The human test can hold one visual task of ours, at most 10 minutes long, after the page reading. That fits exit criterion 1 (a building's history reads at a glance). Its results also outrank our model cold readers ("people win" reopens F2). It cannot test criterion 4, the blind test of scene against page. Criterion 4 needs its own readers, or half the readers seeing the scene first.

Source: `inshorts.md`, `docs/engine-requests.md` ER5, `docs/foundations.md` F2; `CLAUDE.md`, What it is for.
Confidence: full.

### Q25
What share of a frame may its middle values take, what exception is allowed and on what condition, and at what size must the frame read before colour is judged?

A frame has four or five values, with one darkest dark and one white, and the middle takes at most 60%. A fog nocturne may take up to 75%, on condition that it keeps both the darkest dark and the white. The frame must read in grey at one-eighth size before colour is judged.

Source: `inshorts.md`, `docs/visual-direction.md` VD2.
Confidence: full.

### Q26
What does a gap in the research coverage mean for building, and when is the craft of management and data interfaces studied?

A gap blocks building: subject and craft come first. The management screens are studied before the first game's choice or the greybox's need, whichever comes first. Other research is just in time, right before its step, except the craft that shapes the foundations.

Source: `inshorts.md`, `docs/systems.md` SY4; `CLAUDE.md`, Working in the right order.
Confidence: full. The packet says "management screens", not "data interfaces", and the answer treats them as the same gap.

### Q30
When the engine's facts disagree with Overstory's curated 1989 starting record, what happens to our facts, what is redrawn, and what becomes of a curation pin that contradicts them?

The engine's fact wins, since history has one owner. What was drawn from our facts is redrawn, and the span from S reruns on the engine's facts. A curation pin that contradicts them is dropped and reported. A broken rule changes our rules, never the engine, and replacements are logged. FC1 reopens on the engine's facts.

Source: `inshorts.md`, `docs/facts-contract.md` FC1, FC3, 36.
Confidence: full.
