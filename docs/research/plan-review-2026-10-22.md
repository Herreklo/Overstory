# The plan review of 22 October

## In short

**What stays:**
- the order's ten steps and their numbers;
- the architecture, whose core held through step 3 (`613e1d1`);
- the port's own order;
- the stone first, then the birches, then House A;
- quality, fixed.

**What changes:**
- **The playable corner (1g) starts now,** on the existing play studies, as the standing frame. On Friday, Øystein walks a Mac build of the clay town with the corner inside it, measured whole. The port resumes inside it at 2b. The play comes next, on a case built from facts the engine records today.
- **The light and the colour grade (1c)** come first after the walk (Øystein: yes). They hold to SEASON's lesson, tested in three lights.
- **A kind is done only across its whole range,** walked in the corner, at the bar against its target frame and accepted by Øystein. Until then it is written as the rung it has reached, never "close".
- **The frame rate is a gate.** The walk's first run is the baseline, and each milestone holds it or brings it down until every view is under 16.7 ms.
- **Port steps 4 and 5 leave room for houses, trees and land.** Each is checked against three written records, not built (`reviews/lt1/port/foundation-needs.md`).
- **No dates past the next milestone** until the stone is done; then the plan is re-estimated from the real pace.

**How the work runs:**
- every step has a box in per cent of the week, written in `NOW.md`, with a re-plan at 1.5 times;
- the plan on Monday, a walk and a play on Friday, one Fable review per milestone;
- an "In short" on every design doc, and a smaller `CLAUDE.md` and `NOW.md`;
- the Unity lock is decided;
- rejected: a generated status page.

## How it was decided

Øystein asked: "are we still happy with this plan? based on what we now know, is there any changes we should make? How do we make this work super smooth, of the highest quality. Efficient, clear, stunning." `CLAUDE.md`'s rule is "decide once, answer from the plan": a change needs evidence, and a fresh reviewer decides the big ones.

The review ran on Opus, with two agents:
- an Opus agent read the docs for the inventory;
- one fresh Fable agent decided the proposals from a lean packet, without seeing the chat. It opened three sources: the playable brief, the port's handover, and `docs/plan.md`'s week and sizes.

During the review, Øystein decided two of the proposals himself (P4 and P6). He also added a cost lens: "Need to think about these things too, not just add a step, because another step said so without thinking." So each proposal also carries its standing cost: what every session and agent must read or do because of it. Changes that replace or merge are preferred over changes that add.

## The evidence

Each item was checked at its source.

| # | Evidence | Source |
| --- | --- | --- |
| E1 | **Pace.** The port was planned at 3 days and is re-estimated at 13.5 to 17.5 Opus-days. The rough sizes came from the stairs' pace before the craft research ("a day and a half"). | `building-blocks-decisions.md` §13; `plan.md`, Rough sizes |
| E2 | **Nothing is complete end to end.** The birches closed as a look test only, on alpha-tested cards that cost 10 to 16 ms in view (25 ms when they fill the frame). The stone is mid-port; its baseline is "still below the bar, with four known faults". The houses are at test quality, and the Variety stairs are stale. | `reviews/lt1/playable/brief.md`; `plan.md`; `systems.md` |
| E3 | **The frame rate.** The corner runs at 28 to 96 ms (10 to 40 fps) against a 16.7 ms target. "Every measured pass but the sky is over twice its line." The fixes that need no levels (the beams, the haze, the shader families, the birch) are "their own track", but no step, order or owner holds them. | `plan.md`; `building-blocks.md`, Budgets |
| E4 | **Isolated measurements misled twice.** R2 measured +0.52 to +0.85 ms for a history page on a quad, and R2b 1.2 to 1.6 ms a screen. R2c found about 0.04 ms: the cost came from the busy output, not the sample. The pass budget, measured on quiet frames, understates a busy screen by about 2.2 ms. And the whole corner is too noisy for A/B tests under a millisecond (round-to-round spread up to 16.6%). | `reviews/lt1/history/r2.md`; `measuring.md` |
| E5 | **Orchestration friction.** <ul><li>Step 2a's Unity overlapped 12 segment-rounds of a timing run.</li><li>Two `pgrep -f` wait loops deadlocked on their own command lines.</li><li>Background loads: mediaanalysisd at 50 to 86% CPU, mds_stores at 30 to 43%.</li><li>An installer rewrote FBX files that hadn't changed (now fixed).</li><li>Background agents die when a chat is cleared, and sessions can't be started over Remote Control.</li><li>Main sessions re-reading their own context took 34% of usage.</li></ul> | `r2.md`, The record; `port-handover.md`, Traps; `working-with-claude.md` |
| E6 | **Doc volume.** <ul><li>499,000 words in 112 docs (334,000 of them research), plus 795,000 words of notes under `reviews/`.</li><li>Only 2 of the 20 design docs have an "In short".</li><li>`NOW.md` is about 4,800 tokens against its own budget of 1,500, and `CLAUDE.md` about 4,500; every session and agent reads both.</li><li>`plan.md`'s "Next week" section was stale.</li><li>The playable brief lets the corner's three biggest costs choose the port's next steps, which makes a second order.</li><li>A session answered from memory against the order.</li></ul> | `find docs`; `NOW.md` line 3; `CLAUDE.md`; brief line 34 |
| E7 | **The paper playtests** (11 of 24 runs). <ul><li>No concept held its players: exit interest was about 3 of 10.</li><li>Half the AI players praised the known-weak game, so their answers on taste are weak.</li><li>The game masters leaked facts (4 of 5 saw real lines).</li><li>100 of 115 misreadings were the players' own leaps.</li><li>Some needs aren't recorded by the engine: kin, and who found and certified the dead.</li><li>The 11 runs cost about 14% of the week.</li></ul> | `docs/playtests/paper-1/analysis/interim.md`; `NOW.md` |
| E8 | **The architecture's core holds.** Step 3's early rungs corrected three decisions and settled one, without reopening the architecture. | `613e1d1`; `reviews/lt1/history/step-3-verdict.md` |
| E9 | **Usage.** At 07:45 UTC on 22 October, 52% of the week was used (Fable: 42%). The limit resets on 26 October at 12:00 UTC. At about 2% an hour at today's parallelism, the 48% left is about 24 working hours. Costs: an hour of building in a fresh agent is 0.8 to 1.2%, and a craft study 0.8 to 1.2%. 34 overnight Fable rounds on the birch took a third of a window. | `get_usage`; `docs/usage-log.md` |
| E10 | **The inventory** (below) found 19 foundation needs that stone alone wouldn't show. Seven places are already decided in the stone's shape, and four pairs of docs disagree. | The inventory; `reviews/lt1/port/foundation-needs.md` |
| E11 | **Øystein's wishes today:** <ul><li>the world first for now;</li><li>proof that we can build something whole;</li><li>playtests that really play;</li><li>the highest quality, efficient, clear and stunning;</li><li>plans that don't flip on a question.</li></ul> | Øystein, 22 October |

## Decided by Øystein during the review

- **P4, the Unity lock.** Øystein asked for it, and it is built: `tools/unity_lock.py`, described in the `unity-conventions` skill.
  - Every Unity run, and every Blender install into `unity/`, goes through it; `--timing` also waits until no Blender batch, other Unity run or player is running.
  - Standing cost: one command before each run. It replaces the `pgrep` traps and the "Unity is not yours yet" prose in briefs.
  - Background load: mds_stores and mediaanalysisd stay. The lock records them but never waits for a quiet machine. If Øystein wants, he can exclude the repo from Spotlight and pause Photos' media analysis on the reference machine; system settings are his to change.
- **P6, the light's lasting fix (1c), early, in the corner, with colour grading in scope.** Øystein: "yes lighting and color grading very important. (also remember Seasons shading philosophy)".
  - It holds to the core rules (`docs/research/colour-and-shading.md`), SEASON's lesson first: shadow and ambient colour come from the light, never from the object. The art and the grade act on the whole light, never on one material (`docs/research/lighting-and-colour.md`).
  - Each change is tested in at least drizzle, low sun and the blue hour.
  - It carries the low-sun pass's extra 55 to 65 ms (the beams) and the dither's shimmer.
  - Fable placed it first after the walk, since the light's A/B tests need the walk's whole-scene baseline (E4), and with P2 it gates every "done".

## The proposals and the verdicts

Each proposal is given as it went to Fable, with Fable's verdict after it.

### P1. The playable corner as the standing frame — amended

*Proposed:* 1g starts now, on the play studies that exist (the unread talks are still held), and takes Unity while the port stays paused after 2a. The port resumes at 2b inside the corner. Every later step ends in the corner, walked and measured whole, and new kinds are judged there. The brief's line letting the corner's three biggest costs choose the port's next steps is redirected to the frame-rate gate (P9); the port keeps its order.
- *Cost:* phase 0 about 4 to 6% of the week, with its creative round boxed. Phase 1 ("two working days") likely 13 to 19%.
- *Standing cost:* one walk capture and one whole-scene run per milestone.

*Fable: amend.* Most of this is already Øystein's, agreed in the brief. What is new and right:
- 1g starts now on the existing studies (phase 0 reads their In shorts);
- line 34 stops being a second order;
- milestones are judged whole.

Its amendments:
1. This week holds phase 0 (no Unity, in parallel) and phase 1. 1c's only work this week is the beams A/B on the walk's first whole-scene run; the rest starts after it, boxed.
2. Phase 2, the play, gets a place: the milestone after the walk, boxed, beside 2b (which runs on the Blender side, so the lock allows it).
3. The standing-frame rule is written once, inside P2's definition of done.

*Would change its mind:* the walk past 1.5 times its box, or the clay town's cost drowning the corner's numbers.

### P2. Done means across its range — accepted, with one addition

*Proposed:* one definition of done. A kind is done when it holds across its range in LT1's 1989 town: its variety, every distance level, three lights, motion at one sample a pixel, its count at town scale, inside its frame budget. It is judged at the bar against its target frame and accepted by Øystein. For example, the gully with the Variety stairs rebuilt, or the birches over ages and sites, with levels and wind at town scale.
- *Standing cost:* none; one definition replaces two lists.

*Fable: accept,* adding that a kind's state is always written as the rung reached, with what waits: a number, grey form, a sheet, levels, motion, count, three lights, accepted. So "close" is never a state. This makes 1c a prerequisite for any "done".

*Would change its mind:* a range the rung rule can't name.

### P3. Dates only to the next milestone, boxes and a stop rule — accepted, amended

*Proposed:*
- The rough sizes are marked as guesses made before the evidence, with no dates past the next milestone until the stone is complete.
- Then the plan is re-estimated in per cent of the weekly limit per finished kind. This merges the earlier pre-mortem's "re-sized by 13 November", whichever comes first.
- Each step gets a box from the usage log's unit costs. At 1.5 times its box it stops for a written re-plan.

*Fable: accept,* with three amendments:
- the box sits beside its step in `NOW.md`'s order, with no new table;
- the re-plan is a few lines in the same place;
- Øystein is told only when a re-plan moves a milestone or the scope.

*Would change its mind:* boxes causing more re-plans than they prevent in the first month.

### P5. An authoritative "In short" on every design doc, and trimming — accepted, amended

*Proposed:*
- Each design doc opens with an "In short" of at most 200 words stating its current decisions. The body must agree with it.
- `CLAUDE.md`'s line "start from a study's In short" widens to every doc.
- Stale sections are deleted at milestones.
- *Cost:* one Opus session.

*Fable: accept,* with three amendments:
- the In short is where a doc states its decisions, and the body holds the how and the why, so each decision is written once;
- `CLAUDE.md` gets a budget too, about half today's size, with the overflow moved into the skills it names and nothing lost;
- the stale week in `plan.md` is P7's job.

*Would change its mind:* In shorts drifting from their bodies at the first spot check.

### P7. A weekly rhythm and a page for Øystein — amended

*Proposed:*
- On Monday, after the reset, one session writes the week from `NOW.md`'s order, with the boxes. This replaces "Next week", and the same session checks the pre-mortems' warning signs.
- On Friday, Øystein walks the corner and plays any case there is.
- One Fable strict review per milestone.
- A private phone page, generated from `NOW.md` and the newest renders.

*Fable: amend.* It accepts the Monday block, which gives the producer's risk register without a new doc. It also accepts the Friday walk and play, and one Fable review per milestone (E9). It rejects the generated page: no evidence says Øystein wants one, and it is a second status surface that drifts, with a script to keep. `NOW.md`'s top, under its budget, is the one status source.

*Would change its mind:* Øystein asking for the page.

### P8. The fronts and the inventory reach the foundations, checked but not built — accepted, amended

*Proposed:*
- The house-front research and the inventory's 19 needs reach the port as one short section.
- Steps 4 and 5 leave room for them but build nothing for houses.
- Each step is done only when a House A front record and a birch chunk validate against its formats.
- *Cost:* about half a day per step.

*Fable: accept,* with three amendments:
- three clients, not two: add the 64 m land chunk with water faces, the widest gap;
- a format changes only where a written record fails, and no field is added without a record;
- the four disagreeing doc pairs are corrected in place when settled.

*Would change its mind:* the checking reopening the architecture's core, which E8 says holds.

### P9. The frame rate as a gate — accepted, amended

*Proposed:*
- The fixes that need no levels enter the order: the beams and haze with 1c, the shader families with port step 4, the birch's cost with 1e.
- The corner's whole-scene time is recorded at every milestone, and no step closes with a regression beyond noise.
- Questions under a millisecond are measured on their own, but always on the real output.

*Fable: accept,* with no new owner role. The number comes from the milestone's whole-scene run in the lock's timing mode and is judged by the milestone's strict review. The Monday session puts any fix first.
- The walk's first run is the new baseline. The clay town counts as scope, not as a regression.
- A rise without a change of scope is a P3 stop. The number must hold or fall at each milestone until the corner is under 16.7 ms at every judging view in three lights.

*Would change its mind:* noise above 16.6% even with the lock's timing mode.

### Fable's addition: the port's notes in git — accepted and applied

*Fable proposed* moving the port's plan and its four agent reports out of `~/Library/Application Support/Claude/side-session-notes/…` and into `reviews/lt1/port/`.
- *Evidence:* E5; the handover sent the next session outside git for the port's plan.
- *Cost:* minutes. *Standing cost:* none.

They are copied, and the handover points at them.

## The pre-mortem

It is April 2027 and the plan has failed. Why:
1. **The stone never finished, so nothing else started.** The port grew from 3 days to 17, and "done" kept widening. Each strict review found new faults, and the stone was "close" for the third time in January. The houses began in February. No one knew the real pace, and no step had a box. *Action:* P3, and P2's rungs.
2. **60 fps never arrived.** The corner ran at 10 to 40 fps in October. Its fixes were "their own track", with no step or owner, and every kind added cards and shader families. *Action:* P9.
3. **The foundations came out stone-shaped,** the stairs' blind spot again. Seven places were already decided in stone's shape (E10). The houses reopened the formats, and every golden view was rebaked. *Action:* P8.
4. **The plan flipped and the docs lied.** There were 1.3 million words, `NOW.md` at three times its budget, a stale week in the plan, and a second order in the brief. *Action:* P5, P7, and P1's redirect.
5. **The game never found its fun.** The case came late, AI taste was weak, and no human played until the look was finished. *Action:* phase 2 placed beside 2b; Øystein plays on Fridays.
6. **The one machine was the bottleneck.** Timing runs were spoilt by overlaps and background loads. *Action:* the lock (P4).
7. **The budget ran out mid-step.** *Action:* P3's boxes and one review per milestone.

Fable: ranked right, and stories 1 and 2 are one story seen from two sides. **The story it missed,** carried by E7 and the plan's "the engine's pace": the case needed facts the engine doesn't record (kin, who found and certified the dead). So the play ran on invented fixtures, and Overstory became the engine. *Action:* phase 0 picks a case from facts the engine records today, and what it lacks goes into the next request bundle, with no new step.

What a studio's **lead producer** would say we lack:
- a known pace and a burn-down per finished kind;
- timeboxes with stop rules;
- a scope lock for the first slice;
- one status source;
- a fixed rhythm with Øystein;
- a risk register with owners.

Answered by P3, P7 and P2. The slice's scope is the corner's, in the order.

What a **technical director** would say we lack:
- performance as a gate, not a document (P9);
- a second and a third client through every format before it freezes (P8);
- the iteration time, from a generator change to a walkable build, as a tracked number (open: phase 1 can time it once);
- timing on a quiet machine (P4's `--timing`);
- an owner for each shared system (answered by the milestone review, not a role).

## Friday, and the stone's path

**Friday 23 October** (Fable): a Mac build Øystein walks, on whatever is honestly complete. It holds:
- the clay town, with the corner at today's quality inside it;
- whole-scene numbers at the judging views in three lights, taken in the lock's timing mode (or by hand on a quiet machine, and said so);
- the case and the testing design, picked.

**Then, on the stone's path:**
1. 1c in the walked corner, the beams first, with 2b in parallel on the Blender side;
2. the strict review of steps 0 to 2 against the target frame;
3. R3 to R7;
4. `reviews/lt1/port/foundation-needs.md` checked before step 4 opens.

## Left to others

- `reviews/lt1/playable/brief.md` line 34 ("the port's next steps are chosen from them") now runs against the plan. The corner's three biggest costs go to the frame-rate gate; the brief's owner corrects the line.
- **P5's session** (box 2%):
  - In shorts for the design docs;
  - `CLAUDE.md` to about half, with the overflow moved into its skills;
  - `NOW.md` under 1,500 tokens (its "Tonight" section is stale);
  - `docs/systems.md`'s "How a new thing joins" to cite the plan's definition of done;
  - the order contradictions below.
- **Iteration time** (generator change to walkable build) is timed once in phase 1, and kept as a number only if it proves to be the bottleneck.

## The inventory

Everything the corner and LT1's harbour town in 1989 definitely need: 35 kinds, materials and shared systems. It was read on Opus from `docs/systems.md`, `docs/town-plan.md`, `docs/building-blocks.md`, the schemas and the studies, with `docs/research/house-fronts.md` cited as **HF n**. Interiors, other towns and content after 1989 are left out, except where step 4 of the plan needs them. The 19 needs stone alone would not reveal, marked ★ here, are listed for the port in `reviews/lt1/port/foundation-needs.md`.

**Shorthand used in the tables:**
- **M4:** port step 4, materials as pack records plus the editor step that writes the Unity assets.
- **L5:** port step 5: levels, 4 m chunks, the shell, the caster proxies, the pragmas and the id test.
- **HP:** the history pages (`maps.json`, `layers.json`, D5.x).
- **S** and **C:** the subject and craft research.
- **★:** a foundation need that the stone alone would not reveal.


| # | Item | Step | Shared systems | Needs from the foundations | Done means | Research |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Gully stairs, treads (slate) | 1e, port 0–7 | upkeep, feet and water fields, wear, growth | Piece clocks, P0 and H1, the hollow, the 32-byte piece table, casters per chunk. All decided, and all shaped by stone. | Port steps 0–7 done, the four faults fixed, held beside the target frame, then Øystein (`playable/brief.md`) | S and C covered. This is the reference row. |
| 2 | Cheek and dry-stone walls | 1e | upkeep (relaid courses), growth, contact | A disturbed clock per stone. ★ Joint lines and growth faces exported for the plant placer. ★ Climbable regions and keep-clear zones for climbers (`ground-cover-and-plants.md`). | Re-fitted with their facts; their joints carry plants at steps 3 and 7 | S covered. C: the hard-part outputs in ground-cover. |
| 3 | Mortar, pointing, cement repairs | 1e onward | upkeep (a repair is a material) | ★ Each repair needs a material record with its own ageing (cement goes half grey in six years, so pigment drifts with the years), not face kinds 4 and 5 in `Stone.shader` (`upkeep.md:57`). | A cement repair reads as a later repair of its decade, at eye level and at 12 m | S: `upkeep.md`, `repairs.md` |
| 4 | Setts, flags, gutters (the landing) | after 1g | swarms, rows by hash (D6.10), upkeep (trenches) | ★ The swarm facts have no reset year or page address (`channels.json:54`), yet "a library sett carries its own lane's years" (`building-blocks.md:167`). ★ A trench patch (setts relaid, asphalt blobs) is a region with its own clocks. ★ Swarms need a pick code. | The rows read their age and repairs from the street stop to near-isometric, at 60 fps | S: upkeep. C: D6.10, `ground-cover:249`. |
| 5 | Kerb, plinths | after 1g; plinths at 2 | splash, contact, upkeep | ★ A plinth meets a coated wall. Splash resets on "a new coat or plinth" (`layers.json:10`), across two kinds, and the host's flow must run on across the seam (D4.1, carriers). | The splash band runs on unbroken from plinth to wall at every level | S: `wooden-town` (plinths are ranked for step 2) |
| 6 | Rock knuckle, Watch Knoll ledges | 1d, 6 | land, lichen, moss, flow | ★ Rock is land, not pieces in 4 m chunks. Faces of ground only have no page group or piece clock, because page groups are defined over 4 m chunks (`maps.json:6`). ★ There is no `lc` merge unit (`kind.schema.json:127`). | Reads as natural ground with dated acts, in all four views | S and C: `land-rock-and-water` |
| 7 | Land, made ground | 1d, 6 | dated acts, breaklines, rings | ★ The 64 m land chunk carries the mats and the ground. ★ The far land needs a seasonal colour bake. | The corner's land at 1d; the heart's at step 6, within the frame time at the city view | S and C: `land-rock-and-water` |
| 8 | Quay walls, steps, bollards, rings, ladders | 6 | upkeep (concrete toes), tide, salt, carriers | ★ The tide band (lichen and wrack) follows the date and the hour, not only the date of the fabric. ★ Salt (`h3.b`) and the carrier (`h3.r`, rust from rings) are only reserved. ★ Iron needs metal records. | A quay reads its eras and the tide from the water's edge to 12 m | S gap: quays by era. C gap: before step 6 (`systems.md:100`). |
| 9 | Fire Watch (1853), cathedral (c. 1125) | 6 | stone, mortar, soot, far town | ★ Soot (`h3.g`) is only reserved. A landmark must keep its identity on an L4 shell beyond 200 m. | Each reads its age and kind from the city view | S: `town-plan` only |
| 10 | Ground cover: heath, grass, moss, joint weeds | 3, 7 | one placer (D9.2), feet, water, seasons | ★ Tufts need compute plus indirect draws (`ground-cover:249`), against the BatchRendererGroup that `building-blocks:133, 220` gives them. ★ The mats sit in the land chunk's mesh with crisp edges. ★ The material record needs a seasonal albedo range. | The corner complete in four lights (plan step 3) | S and C: ground-cover, with its gaps |
| 11 | Litter, fallen leaves | 3, 7 | deposit field, wind, seasons | ★ Litter is held per page group at 80 mm (`maps.json:79`), but areas of ground only have no page group. The trees feed the field. | Lies where wind and feet put it; stable on the motion sheet | S and C: ground-cover |
| 12 | D's yard and yard things (sheds, washing lines, butts, stoops) | 3 | yard texel, contact, splash, motion | ★ The yard texel keeps splash and contact fine, but both sit in the story page H2 (`layers.json:10–11`). ★ The chunk format has no section for kit instances. Washing is flexible motion. | The yard tells its household's use, at eye level and at 12 m | S: `town-plan`. C gap: before step 6. |
| 13 | Birches | 1e (re-fit), 7 | timeline, wind field, seasons, upkeep (pruning) | ★ Alpha-tested cards are drawn after the opaque pass, around opaque cores. Shadows are cast from the cores and lobes. The trees use the UV5 and UV6 layouts, and carry per-tree season, hue and wind phase. ★ The far form is undecided (`maps.json:84` against `trees.md:42` and `building-blocks:208`). ★ Bark and leaf need records (translucency, seasonal range). `paint.py` still has the seed debt (`systems.md:37`). | The judged sheet in `trees.md`: five ages, four seasons, twelve seeds, a street of 200 trees, a town of 5,000 | S and C: `trees.md`, ground-cover. Gap: bare winter lobes. |
| 14 | Other trees, bushes, hedges, climbers | 7 | one placer, growth, upkeep | ★ Bushes are cards on a core. Climbers read the walls' climbable regions. | Each species judged as the birch was | Ground-cover's gaps; the open list in `trees.md` |
| 15 | Clay houses at 1989, 2000, 2010, 2020 | 1f, 1g | diaries, runner, test generator | ★ Houses that change by year arrive before step 2. The place bake in the player and the GPU encoder (`chunk-format.md:134–139`) are first met here, not on the stone, which bakes offline (`maps.json:66`). | Two or three ways of showing time compared in clay (plan 1f) | S gap: house changes 1989–2020, "found by LT1f" (`systems.md:95`) |
| 16 | Walls, cladding, trims | 2 | coats, upkeep, levels, HP | ★ Charts in the wall's plane (HF 10). ★ Board courses drawn as band-limited patterns from a course table (HF 11–12, which extends D6.10). ★ Lap shadows drawn by the shader (HF 13). ★ Face kinds for end grain and drip edges, and edge distance on arrises (HF 19). ★ The trim atlas holds relief only, keyed by profile. Timber is keyed by source and working (HF 2). ★ Houses may need unwrapping (`history-pages:77`). | House A, twelve houses from its parts, then the five; a first cold reader (plan step 2); criterion 1 | S: `wooden-town`, `house-fronts`. C: `materials-at-scale`, `kits-and-generation`. Gaps: window sizes, roof pitches, paint failure on the coast. |
| 17 | Coats, paint | 2, 4 | upkeep, history, light | ★ A coating kind: binder, film, failure, adhesion by pair (HF 1). ★ A coat record: scope, preparation, film, mask, and a collapse past eight coats (HF 3, 6). ★ The visible coat's year as a clock per texel (HF 5, D5.4). ★ There is no coat layer (`layers.json`, `kinds/house.json:57`). ★ The GPU piece entry has no coat offset (`chunk-format.md:112–126`). ★ A replaced board needs its own coat list (HF 7), but coats are kept by wall id (`building-blocks:331`). ★ Four to five samples (HF 9). ★ Specular anti-aliasing per coat (HF 20). | House A's 6 to 13 coats from 1912 to 1989 read right to a cold reader, and a new board reads as new | S: `wooden-town` §3, HF. Gap: repaint and failure rates on this coast. |
| 18 | Windows, glass | 2 | light (lit rooms), coats, putty | ★ Glass is chosen per pane fill (HF 4). ★ The room box is instance data, with no chunk section (`building-blocks:356`). ★ Pane grids become patterns beyond about 45 m (HF 11–12). ★ Shell openings are inset (HF 15). ★ Library windows (from 1884) lack a page address and stretch (HF 16). | Each era's window reads from eye level to near-isometric; lit at the blue hour from its household | S: fronts §1 and §8. Gaps: glass dates, sizes. |
| 19 | Doors, stoops, porches | 2 | affordances, contact, coats | ★ Contact on handles and stoops sits in a story page. Polish by hands has no law (row 24). Porch roofs must cast (HF 14). | As for the houses | S: `wooden-town`, fronts |
| 20 | Roofs, eaves, chimneys | 2 | rows by hash, lichen, soot, upkeep | ★ A replaced tile has its own year and lichen (`materials-at-scale`), so tiles laid as rows by hash need clocks per tile. ★ The casters keep the eaves, verges, water boards and chimneys (HF 14). ★ There is no facing for soffits (`maps.json:14–21`). | Roof colour and eave depth read the era at every distance (`wooden-town` §6) | S: `wooden-town`. Gap: roof pitches. |
| 21 | Shopfronts (1931, 1962, 1988) | 2, 4 | coats, signs, keepers and uses | ★ Fronts are rebuilt by date. The invalidation table names an instance list that has no section (`chunk-format.md:92`). ★ A repaint rebakes a street's shells (HF 17). | House A's shopfront from its keepers and uses (plan, living fabric) | S: `wooden-town`, fronts |
| 22 | Signs, lettering, posters | 2, 4 | coats, decals, perceived information | ★ Painted letters are masked coats; mesh decals are for posters and plates (HF 8, D4.1). ★ An MSDF glyph atlas per typeface, with æøå. ★ No wrong letters on shells, where a 300 mm letter is 6 to 10 texels. ★ Decals have no chunk section and no pick code. ★ The id test must resolve the coat stack (HF 18). | Letters are right or a mark, never wrong; a ghost sign reads as old | S and C: fronts §6, HF. Gap: lettering by decade. |
| 23 | Gutters, downpipes, wires, poles | 2, 6 | carriers, flow | ★ Chunks are cut at piece boundaries, and no rule says how a run crosses a 4 m chunk. ★ The rule of a median visible triangle of ten pixels (`building-blocks:267`) cannot hold for them. The carrier is only reserved. | No crawl on motion sheets at one sample a pixel | C gap (`systems.md:100`) |
| 24 | Handrail, railings, picket fences | 3 | affordances, coats, contact | ★ Polish speed is footfall / 400,000 (`layers.json:5`), but a handrail is polished by hands. ★ Metal and coated timber need records. Thin and long, as in row 23. | The corner's handrail in four lights (plan step 3) | C gap before step 6, though it is built at step 3 |
| 25 | Lamps, benches, bins | 3, 6 | light, sockets, emitting motion | ★ Lights come from sockets in tiers, with tile-binned spill (`building-blocks:310`), but there is no socket section. ★ Emission and spectrum by era go in the record. ★ A section for kit instances. | The lamp in four lights; the hero frame at the blue hour | C gap before step 6 |
| 26 | Sea houses, warehouses | 6 | coats (tar, oxred), salt, quays | ★ Tar is a coating. Salt is only reserved. ★ There is no facing for water or undersides. | The oxred warehouse and its quay read from the Basin | S: `town-plan`, `wooden-town` |
| 27 | Render, brick (the Grid, the cannery) | 6 | coats (limewash), soot, rows | ★ The split between substrate and coating also covers render and limewash (HF 1). Brick courses are laid by hash. | Each reads its decade from the city view | `materials-at-scale`; planned |
| 28 | Concrete, asphalt | 6 | patches, hex-tiling (D4.5) | ★ A tiling mode in the record. ★ Patches as regions with their own clocks. ★ Puddles away from slate treads, since the hollow is a slate rule (`layers.json:17`). | Patches read as later repairs | S: upkeep. C: `materials-at-scale`. |
| 29 | Water (the Basin, the Roads, puddles) | 6 | light, wind fetch, tide | ★ Water is not a face class (`maps.json:14–21`). Depth, seabed, shore distance and exposure have no slot. ★ Light columns need lights listed across the whole town. ★ The tide runs on the hour. | The Basin at the blue hour, within the frame time | S and C: `land-rock-and-water`. Gap: tide tables. |
| 30 | Boats (Penny Ferry) | 6 | floating motion, water heights | ★ Boats read water heights on the CPU; wakes are decals. | The ferry crosses at 60 fps | C gap (`systems.md:100`) |
| 31 | People, picking | 1g, 5 | affordances, engine records | ★ Blockout people at 1g need affordances and a pick code, but the 2-bit path is full (`channels.json:46`, `building-blocks:143`). | The gully at night (criterion 3); criterion 2 | S: the engine |
| 32 | Light, emission | 1c, 3, 6 | every family | ★ Emitters: lamps, neon, lit rooms, light on water. | The lasting fix of 1c, in four lights | Covered for 1c |
| 33 | The corner through the years | 4 | history budget, story pages | ★ Story pages allocated by the weight of change, measured at step 4. ★ Records for materials after 1989. ★ A jump in years rebakes a street's shells (HF 17). | Cold readers read 1989 and the changes; checked against rH28 | S gap: researched just before step 4 |
| 34 | Far town, shells | 5, 6 | the painted far town | ★ No top-coat mask or window index (`maps.json:80, 83`). The window can come from the shell's uv3 part slot. ★ Live repaint against a rebake. ★ Lettering. | Criterion 5 | `painted-far-town` (a look test) |
| 35 | Weather, wetness, seasons | 9 | water, wind, seasons | ★ Every family reads wetness; seasons reach leaves, ground and the far land. | Moods judged blind (step 9) | Gap before step 9 |

### Contradictions found

**In the plan's order** (for P5's session)
- `docs/systems.md:100` puts the craft gap for street things "before plan step 6", but `docs/plan.md:162` builds the lamp and the handrail at step 3.
- `docs/systems.md:95` says the house changes from 1989 to 2020 are "found by LT1f, before plan step 4". Plan step 4 (`plan.md`) researches that content "just before this step". Yet plan 1f builds the corner's houses at 2000, 2010 and 2020 and needs diary events after 1988 first. So the research is needed by 1f, well before step 4.
- `docs/building-blocks.md:3`, `docs/research/building-blocks-decisions.md:298` ("needed by 3.3") and `schemas/chunk-format.md:139` ("before 3.4") cite step names 3.0 to 3.4. `plan.md` no longer uses them; port steps 4 and 5 are meant.

**Docs that disagree** (to settle at step 4 or 5; also in `reviews/lt1/port/foundation-needs.md`)
- `building-blocks.md:133, 220` (BatchRendererGroup for swarms, including tufts) against `research/ground-cover-and-plants.md:249` (not for millions of grass strokes).
- `docs/trees.md:43` (edges smoothed by alpha-to-coverage) against S1 at `building-blocks-decisions.md:403`, where shaders do not rely on alpha-to-coverage.
- `schemas/maps.json:80, 83` (shell albedo with no top-coat mask; index only "r thing, g reset year") against `research/painted-far-town.md:86, 89, 113` (a top-coat mask, a window index, a live repaint). HF 17 adds a third reading: a repaint rebakes.
- `maps.json:84` (impostor per species) against `trees.md:42` (an impostor that knows the tree's state) and `building-blocks.md:208` (opaque lobes beyond 200 m).

**Already decided in the stone's shape** (also in `reviews/lt1/port/foundation-needs.md`)
- `schemas/material.schema.json:16–24`: wear in µm a century, and cracks counted against slate.
- `schemas/layers.json`:
  - line 3: the constants are slate's;
  - line 5: polish speed comes from footfall;
  - line 17: the hollow is a slate rule;
  - line 21: stone is the only reader;
  - there is no coat layer.
- `schemas/chunk-format.md:88, 112–126`: the piece flags are walked, lifted by hands and reclaimed; the 16-byte GPU entry spends a byte on inherited polish and has no room for a coat offset or a room.
- `schemas/maps.json:14–21`: four facings only, so water and soffits are "an error".
- `schemas/kind.schema.json:127`: there is no merge unit for the land chunk.
- `docs/upkeep.md:57`: cement is drawn as face kinds 4 and 5 in `Stone.shader`.
- Flagged by HF 3–4:
  - `packs/stavanger-1989/parts/window/cross-arch.json` names crown glass, which ends about 1840, and uses cladding board for its joinery;
  - `packs/stavanger-1989/parts/coat/paint.json` fixes its binder as oil paint.
