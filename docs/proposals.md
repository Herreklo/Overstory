# Proposals for the next milestone

Proposals wait here for the next milestone's fresh reviewer, who sees the plan and this page, not the chat. Each one gives its evidence, what it changes, its standing cost (every always-read line costs every session), and what would change our minds. A decided proposal leaves this page and goes into the doc it changes.

## Evidence for Q1 to Q5 (measured 22 October)

- The repo's history starts on 19 October. Since then there have been 378 commits, and 228 of them (60%) touch only docs and reviews.
- There are about 440,000 words in `docs/` and 835,000 in `reviews/`, against about 34,000 lines of code (21,000 Blender, 13,000 Unity). That is about 40 words for every line of code.
- `reviews/lt1/playable/pitches.md` holds about 20,000 words for one pick.
- The paper test took about 14% of a week for 11 runs and gave no verdict.
- The playable corner's Phase 2 was sized at about 16 Opus-days before anyone knew what it had to test. Øystein cut it: "we need to be more sure what to test - before comitting to something like this".
- The cause behind all of it: ideas, plans, rules and documents are nearly free for models to make, while building, playing and looking cost. The work drifts toward the cheap side.

## Q1. Output budgets for each kind of job

- **Change:** each kind of output gets a size, and a brief states it:
  - pitches: at most six, 300 words each;
  - a research study: an In short plus a body of at most 3,000 words, with the sources in a list;
  - a report: at most 500 words;
  - a strict review: at most 800 words.
  A `tools/` check prints any new file over its budget at commit time.
- **Standing cost:** one line in `CLAUDE.md`, and the check.
- **What would change our minds:** a study or review whose decision needed more than its budget. Raise that kind's budget; don't drop the rule.

## Q2. One game concept in test at a time

- **Change:**
  - One concept is in test at a time (today, "Before Friday").
  - New game ideas go to `docs/ideas/parking.md`, one line each, with no new idea doc until the current test answers.
  - Every test starts at the cheapest rung that answers its riskiest assumption, takes about a day, and ends in kill or continue.
- **Standing cost:** none in the always-read files beyond one line.
- **What would change our minds:** a parked idea whose test would answer a question the current concept can't.

## Q3. Rules become tools, and retire

- **Change:**
  - Each rule in `CLAUDE.md` names the failure it prevents.
  - At each milestone, a rule that a tool now enforces leaves the prose. The hashes already enforce determinism, and the Unity lock enforces one Unity at a time.
  - A new rule replaces or merges with an old one.
- **Standing cost:** negative; `CLAUDE.md` shrinks.
- **What would change our minds:** a retired rule's failure coming back with the tool in place.

## Q4. Briefs end in a thing

- **Change:**
  - Every brief's "done" is a render, a number, a walkable build or a played session. A document is a by-product, under Q1's budget.
  - Every report opens with what changed on screen or in play, and if nothing did, it says so first.
- **Standing cost:** one line in the `game-lab-workflow` skill.
- **What would change our minds:** a step whose only honest output is a decision, such as a pick. Its "thing" is then the decision's record, under budget.

## Q5. Two numbers beside Friday's walk

- **Change:** Friday's walk lists what changed on screen since the last one. Beside it go two numbers from a script:
  - the share of the week's commits that touched only docs;
  - the words added to `docs/` that week.
  Work missing from the walk is named as not landed.
- **Standing cost:** a script, and two lines in Friday's note.
- **What would change our minds:** the numbers falling while the walk doesn't improve. Then they measure the wrong thing.

## Q6. The format check covers the whole range of places

- **Evidence:**
  - Øystein, 22 October: "we need to build for the future. do one thing right one time, instead of medium many many times."
  - The plan review's biggest pre-mortem finding was that seven formats are already shaped around stone.
  - P8 checks port steps 4 and 5 against three written records: a House A front, a birch chunk, and a land chunk with water. None of them is a dense city block or a wood.
- **Change:** two written records join P8's three: a dense city block (many fronts, shared walls, many lamps) and a chunk of mixed wood. The light's LA already does this for the light record (`reviews/lt1/playable/outline.md`, 1b).
- **Standing cost:** none in the always-read files. About half an Opus-day before port step 4 opens.
- **What would change our minds:** the two records showing nothing that the three didn't already show.

## Evidence for Q7 to Q11 (22 October)

- Øystein, on making every asset ourselves: "it is very expensive", and he is "still a bit unsure it will look as good as i hope".
- Øystein, on the style: "the key is the balance between enough detail to tell a story, and simplicity without look cheap or boring. This game HAS to look stunning, but not be heavy or slow - very important."
- People already start from free bases: MPFB's CC0 MakeHuman body and Mixamo's clips (`docs/research/characters.md`). Scans are kept for study and form, never as surfaces, since their colour carries the photo's light (`docs/research/land-rock-and-water.md`).
- A post on Opus making 3D took four top-tier plans running for two weeks for one detailed model; its author put photogrammetry into Blender as a 3D reference layer.
- This Mac, the reference machine's class, is an M4 with 24 GB.

## Q7. Free meshes as starting forms for props

- **Change:** before plan step 3, a half-day scout of CC0 and CC-BY meshes for props (lamps, bollards, boats, crates, rope, cast iron): licence, tier budget, and how much fitting each needs to our part contract. A chosen mesh is a starting form, re-fitted or measured and rebuilt by our generator, painted by our materials, judged like any part. Placeholders for greybox play (Kenney, CC0) when a test needs an object not yet made. Never whole buildings, and never a finished look.
- **Standing cost:** none in the always-read files.
- **What would change our minds:** fitting a free mesh costing as much as making the part.

## Q8. Scans as references, found with each step's subject research

- **Change:** each step's subject research includes a search for scans and measured surfaces that match its kind, recorded with source, licence, scale and size: ambientCG's and Poly Haven's height maps for setts and paving, Sketchfab's CC0 and CC-BY heritage scans for steps, walls and kerbs, Kartverket's laser data for the land (1d), DigitaltMuseum's photographs for eras. A generator measures from them; they never appear on screen. Downloads wait for Øystein's OK; Google Earth is looked at, never extracted. Øystein's own phone scans come last, where nothing matches. Poly Haven's CC0 sky HDRIs serve as the sky model's ground truth (L6).
- **Standing cost:** one line in the `game-lab-workflow` skill.
- **What would change our minds:** scans of the wrong kind teaching the wrong wear.

## Q9. Detail where the story is, measured

- **Change:** a tool maps a frame's fine contrast and compares it with where its history facts are. A surface busier than its story fails, and so does a story point too quiet to read. It joins the eighth-size value read (VD2) in every target frame (L2) and strict review, before eyes.
- **Standing cost:** a tool, and a line in `docs/measuring.md`.
- **What would change our minds:** frames that pass it and still read as busy or empty to the strict reviewer.

## Q10. Vision models for the checks, later

- **Change:** after the light (1c), a test of SAM 3 and DINOv3 for segmenting renders, so each material's value spread and detail map are measured without hand masks. Licences checked and downloads approved first.
- **Standing cost:** none until adopted.
- **What would change our minds:** hand masks from the generators' own ids doing the same job.

## Q11. Local models, only if the mechanical share is large

- **Change:** `tools/usage_scan.py` measures what share of usage is mechanical work a check proves (renders, exports, hashes). Only if it is large does a local model for that work become a proposal, run when no frame time is being measured.
- **Standing cost:** one measurement.
- **What would change our minds:** the share being small, as the 20 and 21 October measurements suggest (context re-reading a third, helpers nearly half, Fable a sixth).

## Evidence for Q12 to Q15 (22 October, evening)

- The walk's first runs: the corner draws in about 30 to 45 ms on the M4 (GPU 45 ms at eye-foot in drizzle), against F3's 16.7. The beams alone cost about 60 ms in low sun; the birch 10 to 16; the opaque shaders 12.5, owner unknown.
- Drawn flat, the corner's 2.74 million triangles cost 1.9 ms; in their shaders, 14.5 (`docs/building-blocks.md`). Time goes to per-pixel work, but shadows, memory and scale still pay per triangle.
- The gully is about 960,000 triangles (stairs 354,126, walls 607,872, up 35% in its last rebuild), half the whole frame's 2 million for one flight and its walls. The triangle gate starts only in 1e, so the stone's export warns and never fails.
- The stone is sheared on the rake (non-rigid) in three places (BB3). The stairs took eight rounds, then a rebuild. Øystein, 22 October: "i do not want a slow game - or a game that needs a very good gaming pc"; "they look a bit buggy"; "if something is bad, sometimes it is better to start again"; "make sure we have a good process on this, and not just do the same mistake over and over".
- The frame-rate gate only asks the number to "hold or fall" at each milestone, with no date for 16.7 ms, and new scope may raise it.

## Q12. A frame-time budget for each element, before it is built

- **Change:** every new kind, system or effect gets a budget in milliseconds at the judging views on the M4, written in its "done" before building, and the harness checks it when the element joins the corner. The corner aims at about 12 ms, leaving room for people, the simulation and the interface. Over budget stops the step, as overrunning its box does. The gate gains a date: the corner under 16.7 ms by LT1's end.
- **The floor first:** W3 measured the shared per-pixel pipeline (our surface shader, MSAA, haze, post) above 16.7 ms before any detail arrives (the clay district at 21 to 25 ms with the beams off). So 1c starts with L5, the per-shader trace (0.25 d), and the performance craft study (`docs/research/performance-craft.md`, started 22 October) before L1; every later light stage builds on a known floor.
- **Standing cost:** a line in each brief; a harness arm per element.
- **What would change our minds:** elements whose cost cannot be known before a first build; then the budget is set at the first grey-form rung instead.

## Q13. The triangle gate on the stone in 2b, not 1e

- **Change:** the gate (`docs/plan.md`, 1e) starts with the port's 2b: the stair and cheek walls get a triangle budget per tier from `docs/foundations.md`, and their export fails above it. Detail beyond the budget moves into normal maps and the history pages.
- **Standing cost:** the gate's tool, earlier.
- **What would change our minds:** a blind review finding the budgeted stone worse at eye level than today's.

## Q14. Patch or start again: a test before each round of fixes

- **Change:** before fixing a part, ask whether its faults are in its foundation or in how it is made. Start again (keeping the pipeline, the facts, the hashes and the tools around it) when any one holds: the faults come from how the part is made rather than from settings; it is over its triangle or frame budget by more than half; a third round of fixes has not converged; or a rule it breaks is basic (rocks bend). Record which, with the evidence, in the experiment's entry.
- **Standing cost:** a line in the workflow skill.
- **What would change our minds:** restarts that cost more than the rounds they replaced, measured over the next three parts.

## Q15. The strict review of port steps 0 to 2 asks "start over or adjust?"

- **Change:** a fresh reviewer who has not seen our view answers it for the stair and cheek walls from frames at judged size, the code and Q14's test. Our proposal for it: redraw the stones (a rigid placement and shaping function under Q13's budget, judged against the target frame) and keep the port's stages, records, seeds and tools. A "start over" on more than the stones goes to Øystein as scope.
- **Standing cost:** none beyond the review already planned.
- **Øystein's verdict, 22 October evening:** "same with the stairs really. the look very buggy and not nice". His reasons: "nothing has any detail except those, and they are a bit much. also you see that they are poorly made. loose lines etc". So the redraw's done adds two tests: restraint (few, larger, deliberate marks, detail only where the story is, its busyness matched to the ensemble around it and checked by the eighth-size value read and Q9's map, which also cuts per-pixel cost and shimmer, `performance-craft.md` item 7), and clean making (no one-pixel lines, no black slots, no loose stones, closed joints and ends). 2b redraws the stones by Q14 (rigid placement and shaping under Q13's budget, from the target frame, his walk's notes as their done); the reviewer judges only whether more than the stones must go.
- **What would change our minds:** the reviewer finding the faults are settings, not the making.

## Q16. The birch is rebuilt in 1e, not re-fitted

- **Evidence:** Øystein, 22 October, looking at the walk's stills: "the tree looks not good in game". It costs 11 to 17 ms where it is in view (`reviews/lt1/playable/walk/w3-report.md`), as much as every material on screen. It was closed as a look test only, built on cut-out cards before the trees' craft was known, and cards are what the M4 draws worst (`docs/research/performance-craft.md`, item 4).
- **Change:** by Q14's test (faults in how it is made; far over budget; never converged in the real scene) 1e starts the birch again, keeping its facts, seeds and growth record: an opaque core and lobes of leaf clusters, a depth pass first and colour without `clip()`, the town's sky per vertex, a triangle and frame budget set first (Q12, Q13), Firewatch's trunks, light and leaf clusters as the bar, judged in the walk at eye level in three lights.
- **Standing cost:** none beyond 1e.
- **What would change our minds:** a blind review finding a re-fitted card tree equal at eye level within budget.

## Q17. Cutting away is tested, not ruled out

- **Evidence:** Øystein, 22 October, on the rule that nothing is cut away: "damage is actual damage on the building, not making it easy to see playable character. two different things. and this might be a nice way to do it?" The rule (`docs/research/camera-and-composition.md`, bottom line and Occlusion from raised views) rests on a guess that a cut reads as damage, and no reader was asked. A cut belongs to the camera, as the cursor does: it moves with the view and claims nothing about the building, so it is none of the five kinds of thing on screen (`CLAUDE.md`), and the history rule does not reach it. Players of The Sims, XCOM and Baldur's Gate 3 read cuts as the view (our reading; no study found). What is left of the worry is narrower, and Øystein agrees with it: a cut must never look like a state of the material, such as a ragged, broken edge in the wall's own colours, because what the building shows of its history must read truly (criterion 1). Reading wear may become a mechanic, but no game has been chosen yet ("it is not the, or a game yet").
- **Change:** the zoom test (1g's camera milestone) plays cutting beside moving the camera, as switches:
  - (a) a soft cut round the focus, like Baldur's Gate 3's sphere but with a clean, even edge that reads as the lens;
  - (b) walls between the camera and the focus faded, with the Sims' thick caps where a wall is cut;
  - (c) the focus's silhouette drawn through walls;
  - (d) the camera moving to see, which is the research's design.

  The focus is whatever the player follows or selects. It is judged three ways:
  - by playing it, Øystein first, then testers;
  - by cold readers asked what is old, changed or damaged in frames with cuts on (criterion 1); a cut read as damage fails that variant;
  - by its cost on the M4. A cut made with `clip()` costs the tile GPU as the birch's cards do, so it is measured, and a cheaper way is tried if it is over budget.
- **Standing cost:** three switches and one reader question in the zoom test.
- **What would change our minds:** readers reading a cut as damage at any of the camera's stops, or a cut that can't be made within budget.

## Q18. The world, its forms and their drawing are kept apart, and checked

- **Evidence:**
  - Øystein, 22 October: "ideally everythig is made in a way that making changes, adjustments, to style, to era, to world should as easy as possible, without adding more complexity". Then: "will this also male syling easier to change? say a different game require a different visual profile?"
  - Data, not code (`CLAUDE.md`, the pack is data; `d2b1697`) makes values easy to change: palette, era parts and sizes, the push, and the moods, which are already a profile (VD3, `Style_game`). It does not cover a different way of drawing, such as a one-bit dither, ink outlines with flat colour or a miniature. That is shading, the far town's brush, light and post, which is code.
  - The same night showed how such rules drift unchecked. The stone held 38 sizes in `masonry.py`, and the pack's `metrics.json` was never made. Growth's look lives in `Growth.hlsl`, written for this one style; R0b found growth's colour makes 53% of the gully's one-pixel lines (`cd79b22`).
  - The foundation is there: history is read from maps (the `unity-conventions` skill).
- **Change:** three layers kept apart:
  - the world: facts and history, the engine's;
  - the forms: parts and their history maps, held as data;
  - the drawing: shaders, light, brush and post, swappable as one look.

  Two steps make it real:
  - (a) `tools/check.py` gains one rule: no fact or history baked into a colour, and no shader deciding where something is, grows or wears; it only draws what the maps say.
  - (b) a paper check by a fresh Opus agent. For each built kind (stone, the house generator, trees, the street, the light) it lists what two contrasting styles would have to change, layer by layer. Anything that would have to change outside the drawing layer is a fault, fixed while it is cheap.

  No rendered test in a second style is proposed (Øystein: "yes not the test"). Øystein, on the proposal: "Yeah not sure about this, but we'll se on Monday".
- **Standing cost:** one rule in the check command. The paper check is about 1 to 2% of a week on Opus, once.
- **What would change our minds:** the paper check finding the layers already apart, so (a) alone is enough; or keeping them apart costing more than the parts it protects. A chosen game committing to this one style for good would not, since the town must make many games (`docs/town-plan.md`).

## Q19. Materials by family, member and finish, stone first

- **Evidence:**
  - `slate.json` describes phyllite under the name of its split stone. Mica schist, gneiss and erratic granite are in the town's ground (`docs/research/land-rock-and-water.md`) and have no member. Natural rock has no material, and `pine-board`, `crown-glass`, `plate-glass` and `oil-paint`, which the parts name, have no member file.
  - "Working" means a construction in `walling.json`, `walling.schema.json`, SN2 and `kinds/wall.json`, and a finish or a technique in SN1 and SN6. "Kind" means a type of thing in `kinds/`, a rock in `docs/stone.md` (Kind and finish), and a class of information in `CLAUDE.md`.
  - `walling.json`'s `dry-split-1874` carries a build year, and `cement-relaid-1961` is one wall's rebuild: events stored as constructions. The stair's constructions (`block`, `treadOnRiser`) sit in the system's `kinds/stair.json`.
  - Parts name members (`"materials": ["slate"]`), so a new stone has to be added by hand to every part that could use it, and the code defaults to slate (`stair_facts.py`, `stone.py`, `wall.py`).
  - Material numbers sit outside the members: slate's history constants in `schemas/layers.json`, the pack's growth rates in `GrowthPack.cs`.
- **Change**, in the shape of `docs/taxonomy.md`:
  - `families/<family>.json` at the repo root, beside `kinds/`: the family's properties, finishes and shader family, which changes act on it, and the numbers every member must state. The layers each change draws stay in `schemas/layers.json`. Stone first.
  - Members stay flat in `packs/<pack>/materials/<member>.json`, named by a bare word as `schemas/naming.md` has it, each with `family` and `source`. `slate.json` becomes `phyllite.json`, and a migration (`migrations/NNN_phyllite.py`, run by `tools/migrate.py`) renames `slate` in every record and fixture. Mica schist, gneiss and erratic granite join from their research when the land (1d) or a wall needs them. Window glass becomes one member with the finishes crown and plate.
  - `material.schema.json` gains `family`, `source`, the family's properties and the links `yields` and `madeOf`; a member missing a number its family requires fails validation. `part.schema.json`'s `materials` becomes `takes` (a family and the properties the part needs) with `finish`, and the construction or the record names the member.
  - Constructions move to the pack. The walls' `dry-split` names its techniques, member, sizes and the years it was used; the 1874 build and the 1961 relay of fl-0/r become events in the walls' records. The stair's `block` and `treadOnRiser` move from `kinds/stair.json` into `packs/<pack>/stairs.json`. "Working" leaves SN1, SN2, SN6, `kinds/wall.json` and the walling files, and `docs/stone.md`'s "Kind and finish" becomes "Member and finish".
  - Slate's history constants move from `schemas/layers.json` into the stone members, leaving each law's form there. The growth rates move from `GrowthPack.cs` into the pack's surface-growth members.
  - The code follows: `stones.py`, `stair_facts.py`, `stone.py`, `wall.py` and `tools/validate_record.py` read the family and the member, and the slate defaults go. The part code under `blender/parts/stone/slate/` keeps its path until the stone's port.
  - It lands between R2a and R2b, after Q22's paper check on wood, proved unchanged as the data move of 23 October was: the six FBX hashes and `stones.py check`. Opus, since code changes.
- **The shape**, with the values left to the data. `families/stone.json`:

  ```json
  {
    "family": "stone",
    "shaderFamily": "stone",
    "rigid": true,
    "properties": { "breaks": ["slabs", "blocks"], "chemistry": ["acid", "lime"] },
    "finishes": ["natural", "rough", "split", "hewn", "dressed", "sawn"],
    "changes": { "grows": false, "growsOn": true, "worn": true, "weathered": true, "worked": true, "struck": true },
    "requires": ["wearUmPerCentury", "cracksPerMille", "breaks", "chemistry"]
  }
  ```

  `packs/stavanger-1989/materials/phyllite.json`, a member:

  ```json
  { "material": "phyllite", "family": "stone", "source": "the town's bedrock", "breaks": "slabs", "chemistry": "acid", "wearUmPerCentury": "…", "cracksPerMille": "…" }
  ```

  `techniques/split-along-bed.json` (Q21) and a part that asks for properties:

  ```json
  { "technique": "split-along-bed", "family": "stone", "gives": "split", "needs": { "breaks": "slabs" }, "tools": ["hammer", "wedge"], "marks": "flat beds; split faces of few facets", "skill": ["regularity", "a true line"] }
  { "part": "stone/step", "takes": { "family": "stone", "breaks": "slabs" }, "finish": "split" }
  ```
- **Standing cost:** none in the always-read files.
- **What would change our minds:** the paper check, or later the houses' wood, not fitting the shape without a third level or a special case.

## Q20. One home for each fact, checked

- **Evidence:**
  - `docs/` holds about 108,000 words in 22 pages. The building system's design pages alone (`building-blocks.md`, `living-fabric.md`, `stone.md`, `systems.md`, `foundations.md`, `trees.md`, `building-system.md`, `upkeep.md`, `nature.md`) hold about 34,600.
  - Numbers live in two homes. SN4's chamfers of 10 to 12 mm are in `docs/stone.md` and in each stone part's `chamferMm`, where the wall stone's is 12 to 12. Slate's history constants are in `docs/building-blocks.md` and in `schemas/layers.json`.
  - Design pages carry their history. `docs/building-blocks.md` uses round and step names that need a key ("3.0 is the port's step 0b"), and `kinds/wall.json`'s `describes` holds dates and budget figures.
  - The docs-trim test (`reviews/docs-trim/score.md`): a fresh reader with `CLAUDE.md`, `NOW.md`, the skills and the design pages' In shorts, closed book, answered 23 of 30 hinge questions as the full docs do. After the In shorts were fixed, the same reader answered 6 of the 7 misses, for 29 against a target of 27.
- **Change:**
  - Each fact has one home by its type (`docs/taxonomy.md`, TX8). Design pages hold no dates, quotes, review rounds or step codes; those belong in `docs/experiments.md`. A page names a data field and leaves its value to the data. State lives in `docs/systems.md` only.
  - `tools/check_docs.py`, joining `tools/check.py` when it lands. In design pages it flags dates, quotes, review-round and step codes, and paths that don't exist, and it warns on a number with a unit that also sits in a data field the page names. It fails when a material family named in `docs/taxonomy.md` has no file, or a family file is missing from the page.
  - Pages are cleaned one at a time when their system is next worked, `docs/stone.md` and `docs/building-blocks.md` first, since the stone is open. Each cleaned page passes the docs-trim test (a fresh reader, 30 hinge questions, closed book) at 27 of 30 or better on first asking before it merges.
  - How-to steps (adding a member, a part or a kind) move into the skills, which load when the job needs them.
- **Standing cost:** the check, and 30 questions written once for each cleaned page. `CLAUDE.md`'s docs table points to the map instead of listing every page.
- **What would change our minds:** a cleaned page failing the question test twice. That nuance needs the body, so it stays there and is linked.

## Q21. Techniques, skill and means in the data

- **Evidence:**
  - Tool marks date work: granite split with flat wedges shows long slots, and granite split with plug and feathers round holes (`docs/research/taxonomy-precedents.md`). The face patches are chosen per member and finish, by seed (SN6), so a mark that dates a stone can't be told from texture.
  - Techniques live as prose in LF3's tables and `docs/stone.md`. The builder's craft and means (LF3) have no field: `record.schema.json` holds `keepers`, `care`, `use` and `events`, and nothing a part reads.
  - The engine sends no trades or skill, and `docs/engine-requests.md` asks for none.
- **Change:**
  - `techniques/<technique>.json` at the repo root: tools, marks, the finish it gives, what it needs from a member, and how skill shows. The first are the stone's: split along the bed by hand, flat wedges, plug and feathers, scrabbled, axed, boasted, frame saw, dry-stone walling, rubble in lime mortar.
  - A construction names its techniques and the years it was used; a technique reaches a world in the first year a construction uses it. Face patches are made per member and technique, and a piece carries its technique where one thing mixes techniques.
  - Each making and work in the record names who did it, with their skill and the means spent. Each technique turns skill into its own effects, in the form and in how fast the thing ages. Until the engine sends trades and skill (a request for its next bundle), fixtures author them.
  - Each kind names the sets its parts are replaced in (`kind.schema.json`), for UK5. `tools/check.py` gains UK5's reach check: a part whose era or technique differs from the rest of its set names the work that put it there, and a work smaller than its set names why.
  - The first test, at step 2: one shed at three skills and two means, and cold readers asked who built each. It dies if readers can't tell a careless builder from a generator fault.
  - For other worlds (step 10): `pack.json` gains `buildsOn`, and `packs/library/` holds real members and techniques for any pack to use. A world that remembers more than 256 years needs the shell index's year widened from one byte. The first town does not, since it remembers from 1870 and older stone brings its age (TS1; the piece table).
- **Standing cost:** none in the always-read files.
- **What would change our minds:** the shed test failing; or a second world needing a rule changed rather than data added, which means the rule was wrong, and it is fixed in the system.

## Q22. The taxonomy's work, each piece at the step that needs it

- **Evidence:**
  - The order builds hardest-to-change first and nothing ahead of its need: formats change only where a written record fails, and no field is added without one (P8).
  - `docs/taxonomy.md`, UK5 and Q19 to Q21 describe more than the next steps use. Built all at once, they would be the scope creep the plan review warned of; left unplaced, their pieces would arrive after the formats are fixed.
- **Change:** each piece joins at one step, and nothing earlier:
  - **Now, on paper:** the taxonomy and its sections in `docs/stone.md`, `docs/living-fabric.md`, `docs/foundations.md` and `docs/upkeep.md` (branch `docs/taxonomy`), merged into `lt/1-harbour-street` between rounds. Q19 to Q22 wait for this milestone's fresh reviewer.
  - **Before the stone moves:** a paper check of the shape on wood: a shed's timber written as a family, members by source, finishes, techniques and a construction. If it doesn't fit, the shape changes first (Q19's reopen).
  - **The port's 2b, between R2a and R2b:** Q19's stone move with its migration, and the first technique, splitting along the bed, which the face patches are made by today (SN6). Proved unchanged by the hashes. Q20 cleans `docs/stone.md` and `docs/building-blocks.md` as the stone's work touches them.
  - **Before the port's steps 4 and 5 fix the formats:** P8's House A front record carries what the formats must hold: its makings' and works' skill and means, its windows' replacement sets, a work that changes an opening across two cells, and a piece's technique where a thing mixes techniques. `tools/check.py` gains Q20's docs check and UK5's reach check once it exists.
  - **The landing's setts, the kerb and the plinths (the end of step 1):** granite's techniques (wedges, plug and feathers, axed, boasted) and their face patches.
  - **Step 2, before House A's first part:** the pack's `metrics.json` (the standards: openings, boards, storeys and grid, by era); the shed test; trades and skill in the next engine request bundle, with fixtures meanwhile. UK5 drives the resolver's cells for the houses' works.
  - **Step 6, the heart at the city view:** the cathedral and the monastery ruin, entering with the age they bring (TS1), on medieval techniques as data.
  - **Step 10, the foreign pack:** `buildsOn` and `packs/library/`, and a second world built only from data, as the proof. Invented worlds stay outside the plan until a game asks for one.
- **Standing cost:** none in the always-read files. Each piece is boxed by the Monday session with its step.
- **What would change our minds:** a piece needed before its step, shown by a written record that fails; it then moves earlier, and only that piece.
