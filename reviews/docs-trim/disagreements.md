# Where the docs disagree

Found on 22 October while writing the In shorts for the plan review's P5 (`docs/research/plan-review-2026-10-22.md` §P5), for Friday's reviewer. Nothing here is settled in the docs, except the two skill lines in D2, which moved with `CLAUDE.md`'s rule. An In short line that rests on one side is marked `(disputed)`. The four "Docs that disagree" in the plan review are left out: they are settled at port steps 4 and 5.

- **A** (19): `building-blocks.md`, `measuring.md`, `foundations.md`, `trees.md`, `building-system.md`.
- **B** (12): `town-plan.md`, `living-fabric.md`, `town-system.md`, `upkeep.md`, `living-world.md`.
- **C** (21): `plan.md`, `engine-requests.md`, `visual-direction.md`, `systems.md`, `facts-contract.md`, `engine-contract.md`.
- **D** (4): the always-read files and the skills, from the trim itself.

Line numbers are as of 22 October, after the In shorts went in.

## A. Disagreements found in the In short pass, set A

Docs: `building-blocks.md`, `measuring.md`, `foundations.md`, `trees.md`, `building-system.md` (line numbers after the In shorts went in, 22 October). None is settled in the docs. Each In short line that touches one is marked `(disputed)`. Paths are under `docs/` unless they start with `NOW.md`, `reviews/` or `unity/`.

1. **What reopens the hand-split wall stones.** `NOW.md:87` and `research/building-blocks-decisions.md:393` (§14, Q2): a large library is asked about only if *the scale test's* memory for unique close chunks breaks the pool. `building-blocks.md:218`: only if *House A's final-quality chunks* break the pool does Øystein decide. The In short (D6.4) follows `building-blocks.md:218`: it is newer, written after the scale test found the pool fits at test quality (`research/building-blocks-decisions.md:179`; `building-blocks.md:285`, "House A checks the pool again").

2. **Who accepts a golden baseline.** `measuring.md:75`: "only Øystein accepts one; the AI proposes it". `building-blocks.md:378`: a strict review accepts one while building; Øystein accepts milestone sheets. The In short (D14.1) follows the decisions table (`research/building-blocks-decisions.md:319`, which says it overrules `measuring.md`'s rule; `building-blocks.md:434` lists that line as superseded). Note: Øystein in fact accepted both 22 October baselines (`measuring.md:43`, `:91`).

3. **Is the step 0b baseline accepted?** `measuring.md:43` and `:99`: "Accepted by Øystein (22 October)" (commit `03258f1`, 07:54). `measuring.md:55`: "Until it is accepted, `zsh tools/golden.sh` fails against the 22 October frames"; `measuring.md:138`: "Until then, the 22 October baseline stays the reference" (commit `a858766`, 06:30). `measuring.md:35` still names the earlier hashes (`babe291…`) as the baseline, while `unity/Assets/Art/Stone/mesh-hashes.json` holds `bff7858b…`, and the frames in `reviews/golden/baseline/gully/` are still those of `bb13eaa`. The In short (M3) follows the newer text: accepted, as the regression reference only. The copy step at `measuring.md:132` to `:136` seems not yet done.

4. **Blender's version.** `building-blocks.md:5` (and `research/building-blocks-decisions.md:7`): "Blender 4.x Python offline". `measuring.md:7`: "Blender 5.2.2 in the background". No In short line states a version.

5. **Whether the tools have anything installed.** `measuring.md:7` ("Nothing here needs anything installed"), `:67` ("written in numpy because FLIP is not installed") and `:322` ("Nothing was installed for these tools") against `measuring.md:335` to `:339` (FLIP and ffmpeg installed 21 October in `.venv/`). The In short (M2) says only "FLIP-like", true either way, so no line is marked.

6. **Is MSAA cheap on the M4?** `foundations.md:55`: on the tile GPU "opaque overdraw and MSAA are cheap". `measuring.md:222` and `:236` (MSAA 4× costs 4.9 to 6.5 ms and barely shrinks with the pixels) and `building-blocks.md:308` (3.4 to 6.5 ms against a 0.8 ms line). The In short (S1, marked) follows the harness's measurement of 21 October and decision S1 of 22 October.

7. **The anti-aliasing line.** `measuring.md:253` and `:260` give anti-aliasing a 0.5 ms line and call "MSAA 4× native" the architecture's decision. `building-blocks.md:249` and `:308`: the line is 0.8 ms and the port builds for SMAA (S1). The In short (S1, marked) follows `building-blocks.md`, which took the pass budget's own proposal.

8. **Tiers as switch distances and merge units.** `foundations.md:50` to `:53`: near within 20 m, street 20 to 80 m, city 80 to 400 m as "runs of parts merged (a flight, a wall, a house)", far beyond 400 m. `building-blocks.md:200` to `:210`: five levels switched by error under a pixel, L3 from about 50 m, L4 beyond about 200 m, merged by 4 m chunk, 32 m cell and 128 m block; "the tiers are judging bands, not switch distances". `building-blocks.md:428` lists the foundations table as superseded. The In short (F4) follows `building-blocks.md` (D6, FIRM as a scheme).

9. **A stone piece's near budget.** `foundations.md:50`: a stone piece up to 600 triangles near, about 120 at street. `building-blocks.md:205`: a tread goes from 1,100 triangles at L0 to 100 to 150 at L1. The In short (F4, marked) gives no number and points to the levels.

10. **Where water is stored.** `foundations.md:71`: each generator bakes the water layer per point, "UV2.y on stone". `building-blocks.md:116` (UV2 is the mark coordinate) and `:180` (static water is P0.G in the place pages). No In short line names the channel; F5 is not marked.

11. **How many cold readers, and who.** `foundations.md:28`: model readers, three a round while building and six at a gate (two per role, across two models). `research/history-in-things.md:372`: people outside the art team, five to eight a round, twenty or more for a gate. The In short (F2, marked) follows `foundations.md`: Øystein's decision of 22 October that model readers stand in for strangers is newer, and foundations takes only the tasks, controls and failures from the research.

12. **Leaf cards near the camera.** `trees.md:50`: clumps are cards that turn to the eye, placed on every living shoot tip, with density shells in the crown's core at distance. `building-blocks.md:336` and `:415`, and `research/building-blocks-decisions.md:303` (D9.1, FIRM): opaque first, no cards or shells near, cards only where few overlap, cut to outline, real leaves near; `foundations.md:50` also says real leaves near. The In short (D9.1, marked) follows the decisions table.

13. **The lights a tree is judged in.** `trees.md:67`: two lights, 16:00 and 17:50 in sea fog. `foundations.md:21`: three lights, drizzle, the 16:00 low sun and the blue hour; `foundations.md:3` says the systems' designs follow foundations. The In short (TR4, marked) follows `foundations.md`.

14. **Which view is the city camera.** `trees.md:67`: "the city camera just over the ridges looking into the crown (about 12 m up)". `foundations.md:19` and `:20`: 12 m is "into it"; the city camera is pulled out, steep and near-isometric. The In short (TR4, marked) names no view; it follows `foundations.md`.

15. **What the shader reads for a coat.** `building-system.md:39`: "one number per coat: years since it was applied". `building-blocks.md:333` (D4.3): coats are fills with their year, read against the date; `building-blocks.md:427` lists the statement as superseded. The In short (BS2, marked) follows D4.3.

16. **One part a cell.** `building-system.md:37`: a cell holds one part at a time, so a window replaced twice keeps only its first. `building-blocks.md:83` (D3.1): slots hold fills in date order and no cell holds a single `original`; the house record migrates before House A (`building-blocks.md:416`). The In short (BS2, marked) states only what both agree on (a later part never deletes what it covers).

17. **The `stronger` strength.** `building-system.md:56`: stylisation in gentle, strong and stronger. `building-blocks.md:360`: the `stronger` multipliers are gone. No In short line covers stylisation.

18. **Provenance of events the engine has not written.** `building-system.md:27`: they are labelled `authored`. `building-blocks.md:98` (D3.3): four values, with the pack script's past `generated-past`, rule-made facts `derived` and only hand-written ones `authored`. No In short line names the labels.

19. **When the house resolver is ported to C#.** `building-system.md:97`: "once its rules settle". `building-blocks.md:33` ("the house resolver before House A") and `:416` ("The house builder is ported to C# before House A"). The In short (BS5, marked) follows `building-blocks.md`, which carries the accepted port (`research/building-blocks-decisions.md` §1).


## B. Disagreements found while writing the In shorts (B)

Helper B, 22 October, for the plan review's P5. Docs: `town-plan.md`, `living-fabric.md`, `town-system.md`, `upkeep.md`, `living-world.md`. Line numbers are as of this writing, after the In shorts were added. Nothing here is settled in the docs; the In short lines named are marked `(disputed)`.

### 1. Care from character

- `docs/living-fabric.md:28` (`keepers[]`: care "from money, presence, age and character of the owner"), `:90` ("age, character"), `:280` (Decided: "the kind of person"); `docs/engine-requests.md:63` (request 13: care from "money, age, character, whether they live there"); `docs/living-world.md:40` (a visual difference carries "the owner's character").
- `docs/facts-contract.md:9` (FC1) and `:45`: care from money, presence, age and dated events, never character (Rule 8); `docs/building-blocks.md:102` and `docs/research/building-blocks-decisions.md:97`: the same, kept as a Rule 8 safeguard; `CLAUDE.md:71`: a read of character is someone's opinion, never the game's truth.
- **The In short follows "never character"** (LF5): the more specific rule, written as a safeguard in the architecture and the facts contract, under `CLAUDE.md`'s standing rule; `living-fabric.md:177` (How inner states show) agrees that inner states reach the fabric only through acts. The living fabric's text is dated later (agreed 22 October), so this needs a ruling, not a guess.

### 2. Who decides care

- `docs/living-fabric.md:28` (`keepers[]`, who decides: "engine") and `:109` (the care field is written by the engine).
- `docs/living-fabric.md:280` (the engine gives its quantities; the pack's curve turns them into care); `docs/engine-requests.md:63` (care derived in Overstory); `docs/facts-contract.md:45` (care is our rule on the engine's facts, unless request 19 adopts it).
- **The In short follows the pack's curve on the engine's quantities** (LF5): the doc's own Decided section, and the facts contract.

### 3. Where and when a life is computed

- `docs/living-fabric.md:240`: "Life is computed offline per thing"; the city tier bakes the life into the merged mesh's vertex data; fields "redrawn by decade" (also `:100`, "cached by decade", and `docs/town-system.md:29`).
- `docs/building-blocks.md:424` lists these statements as superseded; `docs/research/building-blocks-decisions.md:280` (D12.1): lives are written on change, in C# in the player, and the past to 1989 may ship as a cache.
- **The In short follows D12.1** (LF1): the architecture is newer and names the statement superseded.

### 4. Where a change is rebuilt

- `docs/town-system.md:101`: "Only the chunk a change touches is rebuilt offline"; `docs/living-fabric.md:127`: "regenerating the chunks a change touches, offline".
- `docs/building-blocks.md:425` lists the town system's statement as superseded; `docs/research/building-blocks-decisions.md:11` (§0.1): the town is assembled in the player, fitted geometry in C#.
- No In short line states it; LF1's "computed in the player on change" follows the architecture (newer, and it names the statement).

### 5. The 1989 town made once, or grown plot by plot

- `docs/town-system.md:85` (plots step yearly from 1800), `:97` (about 20,000 plots over two centuries in minutes), `:229` (T8, the centre grown from the script) and `:247` (§9.9, growth a coarse yearly step over plots).
- `docs/plan.md:70` (Leaner 2: "Make the 1989 town once, curated, with records by rule, instead of growing two centuries plot by plot", Øystein, decided) and `NOW.md:110`.
- **The In short follows Øystein's decision** (TS1): newer (22 October) and his. Whether §3's yearly growth stays as the rule that makes the record once, or goes, is the open point.

### 6. The town's size

- `docs/town-plan.md:67`: the town is the size of Stavanger in 1989, about 95,000 people over about 5 by 4 km; `docs/town-system.md:97` (about 20,000 plots) and `docs/engine-requests.md:80` (request 25: a town of 95,000, about 1,200 neighbourhoods).
- `NOW.md:105` and `docs/plan.md:73` (Leaner 5): a dense town of a few hundred buildings, not a metropolis, for now (Øystein, 22 October).
- **The In short follows the dense town** (TP3): newer and Øystein's. A population of 95,000 for the engine may still stand beside a drawn town of a few hundred buildings; the docs do not say.

### 7. Where variety comes from

- `docs/living-world.md:40`: "Variety comes from combination and history, not from more models: a few hundred pieces give hundreds of thousands of buildings."
- `NOW.md:109` and `docs/plan.md:71` (Leaner 3): variety from districts and eras, a kit per house type and era, libraries only where things were factory-made, bespoke parts for bespoke houses (Øystein, 22 October); `NOW.md:104`, nothing repeats unless it was factory-made.
- **The In short follows Øystein's decision** (TP3): newer and more specific.

### 8. Modelling at runtime

- `docs/living-world.md:25`: "Nothing is modelled at runtime."
- `docs/research/building-blocks-decisions.md:11` (§0.1): fitted parts are judged functions, and fitted geometry runs in C# in the player; `docs/building-blocks.md:408` (extensions and rebuilds are fitted geometry made in the player).
- No In short line states it; the architecture is newer and specific. Fixed parts are still made only offline, which may be what the line meant.

### 9. "Nothing is baked"

- `docs/living-world.md:83`: "generated places change, so nothing is baked."
- `docs/research/building-blocks-decisions.md:13` (§0.3: the far shell caches an output bake) and `:174` (D5.9: the shared weathering bake on every chunk).
- In context the line is about light, where D7.6 (no baked probes) agrees. No In short line states it; read as "no baked light".

### 10. When concrete steps were cast

- `docs/living-fabric.md:60`: steps in "cast concrete 1940 to 1980; precast after 1965".
- `docs/living-fabric.md:43` ("concrete steps and casts 1940 to 1965, precast units after"), `docs/upkeep.md:37` and `:72` (1940 to 1965), `docs/research/repairs.md:63`.
- **The In short follows 1940 to 1965** (UK1): three places and the research against one table row.

### 11. The runner's step

- `docs/upkeep.md:62`: `upkeep.py` runs a thing's parts decade by decade.
- `docs/living-fabric.md:116` (the life runs year by year; today's runner steps by decade) and its §5 (`life(thing, tables)`, yearly steps).
- **The In short follows the yearly runner** (LF1): the living fabric's decision; the upkeep line describes today's code.

### 12. How people are drawn

- `docs/living-world.md:59` to `:64`: one MPFB base, faces "painted rather than rigged", stated as the plan (the doc's status line calls it direction).
- `NOW.md:113` and `docs/plan.md:75` (Leaner 7): people are their own research project; how they are drawn is not settled by any shortcut; blockout figures until then.
- **The In short follows Øystein's decision** (LW5): the base and faces are direction until the people step.

### Notes, not disagreements

- `docs/town-plan.md:324` points to "`NOW.md`, Decided" for "the world on screen starts in 1989"; that decision now lives in `docs/town-system.md` (TS1).
- `docs/plan.md:10` (PL2–4) also states the 1989 town made once, libraries only where factory-made, and the dense town, which TS1 and TP3 now hold; one of the two should point to the other.
- `docs/experiments.md:212` (LT1f) says the history budget of one, two, three "stands"; `docs/living-fabric.md:278` still calls it provisional until the corner's years sheet, and `docs/plan.md` measures it at step 4. LF4 keeps it provisional.


## C. Disagreements found while writing the In shorts (helper C)

Docs: `plan.md`, `engine-requests.md`, `visual-direction.md`, `systems.md`, `facts-contract.md`, `engine-contract.md`. Line numbers are as of 22 October, after the In shorts were added. Nothing here is settled in the docs; an In short line that rests on one side is marked `(disputed)`. Dates come from `git blame` where the text gives none.

1. **Who carries requests to Understory.**
   - `docs/engine-requests.md:3`: Øystein takes the requests to the engine project; `:150`: Øystein carries the playtest bundle over, or asks us to comment.
   - `CLAUDE.md:45`: Overstory talks to Understory directly, by comments on its `overstory`-labelled issues (#60), without Øystein as the middle man (Øystein, 21 October; `d33621e`).
   - The In short (ER1) follows `CLAUDE.md`: it is newer (`:3` dates from 19 October, `:150` from 21 October 18:53, `d33621e` from 19:11) and quotes Øystein.

2. **The real run's request number.**
   - `docs/facts-contract.md:65`: "Request 10 in `docs/engine-requests.md` (one real run)".
   - `docs/engine-requests.md:51`: the real run is request 36; request 10 is vacancy and rent.
   - The request was filed as 10 (`4dbdb55`, 18:18) and renumbered 36 (`fb6c447`, 18:41); the facts contract's line is from 18:23. The In shorts (36 in both docs) follow `engine-requests.md`.

3. **What the real run holds, against what the facts contract plans with it.**
   - `docs/facts-contract.md:67`: the fixture asked for has events to 1989, and the corner is drawn from it at 1989.
   - `docs/engine-requests.md:51`: the run received has events from 2026 to 2036, no buildings, and the engine's present begins in 2026 until #23.
   - The facts contract's In short (36) keeps its procedure and is marked disputed; `engine-requests.md` records what arrived and is newer.

4. **The plan still waits for the run.**
   - `docs/plan.md:165`: 1g's blockout people are driven by the real engine run "when it arrives".
   - `docs/engine-requests.md:51`: received 21 October (`fixtures/engine/understory-world-9989.json`).
   - The In short (engine requests, 36) follows `engine-requests.md`, which is newer and matches the repo.

5. **The fixtures' label until the engine's items land.**
   - `docs/engine-requests.md:24`: until the items below land, LT1 and LT2 run on fixtures labelled `authored`.
   - `docs/facts-contract.md:70` and `docs/engine-requests.md:51`: the real run is committed as it came, labelled `simulated`.
   - The In short line "1, 2" keeps `authored` for the corner's own facts; line 36 carries the `simulated` run. Both read as current.

6. **The engine's order: the human test and round 42.**
   - `docs/engine-requests.md:26`: the first human test, then round 42 (21 October, 14:38).
   - `NOW.md:118` (21 October, 18:41) and `docs/notes/2026-10-21-8-overstory-to-understory.md:3`: the human test comes after round 42.
   - No In short states the order. `NOW.md` is the newer text.

7. **Requests still "pending the building-blocks architecture".**
   - `docs/engine-requests.md:33, 35, 46, 48, 63, 65, 67, 86`: "proposed; pending the building-blocks architecture"; `:90, :124, :132`: "next week's architecture".
   - `docs/research/building-blocks-decisions.md:3, 90`: the architecture was decided on 21 October, and D3.3 already gives Overstory's records precision, actor and where.
   - The In short (ER3) follows the decided architecture: it gives the order of need with no "pending".

8. **Building diaries by hand or by rule.**
   - `docs/engine-requests.md:47` (request 6): until the fabric pass exists, Overstory writes building diaries by hand.
   - `docs/plan.md:70`: the 1989 town is made once, curated, with records by rule (Øystein, 22 October); `docs/facts-contract.md:48`: by hand on the corner, grown elsewhere.
   - The In short (plan, PL2–4) follows `plan.md`: Øystein's decision, and newer.

9. **The facts contract's status.**
   - `docs/facts-contract.md:3`: a draft that "the architecture session (Fable, from 26 October) confirms or changes"; `:30`: "the architecture picks one word"; `:45`: the care rule is "proposed".
   - `docs/research/building-blocks-decisions.md:90, 97` (21 October): confirmed with three changes: four labels with `engine` retired, a row for each game's domain model, and the hand-off checks as rules of the record validator; the care rule stays as a Rule 8 safeguard.
   - The In short (D3.3, FC3) follows the decisions: newer and FIRM. The domain-model row is not in the facts contract's table or its In short.

10. **The engine contract's provenance values and version.**
    - `docs/engine-contract.md:48`: three provenance values (`simulated`, `authored`, `generated-past`); `:16`: `"schemaVersion": 1`.
    - `schemas/record.schema.json:81`: four values, with `derived`; `schemas/CHANGELOG.md:46`: every file moves from `schemaVersion` 1 to 2; D3.3 at `docs/research/building-blocks-decisions.md:90`.
    - The In short (D3.3 in the engine contract) follows the schemas, the decided format. `docs/building-blocks.md` lists `engine-contract.md` among the docs to change.

11. **Where the order lives.**
    - `docs/systems.md:3`: "The plan's steps are in `NOW.md`".
    - `docs/plan.md:3` and its section "The order" hold the order; `NOW.md:23` points to `docs/plan.md`, The order.
    - The In short (plan, PL1) follows `plan.md`, as the plan review sets.

12. **When distance tiers are built.**
    - `docs/systems.md:34`: distance tiers are "designed; next after the corner's stone".
    - `docs/research/building-blocks-decisions.md:382`: levels are the port's step 5, and `docs/plan.md:132` puts the port's steps 4 to 7 inside step 1, before the stone is complete.
    - No In short states it; the plan's order is the newer and governs.

13. **A kind's state, against P2's rungs.**
    - `docs/systems.md:83`: "birch done" and "birches built"; `:76`: stairs "in review".
    - `docs/plan.md:104–114` (P2): a kind is done only across its range (the birches over their ages and sites, with levels and wind at town scale), and until then its state is the rung it has reached; `NOW.md:12`: the birches closed as a look test.
    - The In short (SY3) follows P2, the plan review's verdict, and is marked disputed.

14. **Old step names.**
    - `docs/systems.md:97`: "the binding under the Resident Drawer at 3.4".
    - `docs/research/building-blocks-decisions.md:5`: 3.4 is the port's step 5; the plan review's "Contradictions found" notes that `plan.md` no longer uses 3.0 to 3.4.
    - No In short states it. The port's step numbers govern.

15. **The push dial.**
    - `docs/visual-direction.md:24` (20 October): the push is chosen by eye in the beauty corner, between gentle and strong.
    - For stronger: `NOW.md:9` ("Øystein chose stronger"), `docs/experiments.md:264` (19 October: stronger the default) and `docs/plan.md:263` ("Trees take the push dial (`stronger`)").
    - Against it: `docs/experiments.md:299` (20 October: look P exported at gentle, since stronger read as a toy village), `docs/experiments.md:133` (21 October: 1f at the corner's real proportions, gentle) and `docs/building-blocks.md:360` (the `stronger` multipliers are gone).
    - The In short (VD1) follows `visual-direction.md`, which agrees with the newest texts, and is marked disputed.

16. **Walking a person.**
    - `docs/visual-direction.md:84` (21 October): eye level is the bottom of the free camera's range, "never a switch to walking a person"; the player moves "not as a person they walk".
    - `docs/plan.md:170, 174`: 1g tests a walker or a drone, and a walk mode at eye level, as switches (Øystein: "we have to test this"); `docs/research/play-craft.md:41` names the tension.
    - The In short (VD4) follows `plan.md`: newer, and 1g was placed by the plan review. It says the walk mode is tested in 1g, marked disputed.

17. **Eye level for every part.**
    - `docs/visual-direction.md:127`: a part is superb only if it holds at eye level, one to five metres away; `:90` (20 October): parts are made at the scale that reads from the street stop.
    - `docs/plan.md:76` (21 October, 18:13): eye level for every part is open, measured per kind in the gully port and the first house, then decided with numbers.
    - The In short (VD5) keeps the bar and carries the plan's condition, marked disputed: the plan's line is newer on whether every part pays for it.

18. **One light and fixed cameras.**
    - `docs/visual-direction.md:131`: the beauty corner is judged "in one light, from fixed cameras".
    - `docs/plan.md:107, 146`: three lights, and each light change tested in drizzle, low sun and the blue hour; `docs/visual-direction.md:85`: a place is finished in the round and checked against a strip of headings; 1g's free camera.
    - The In shorts (P2, VD2) follow the plan: P2 and P6, newer.

19. **The shading model, still open.**
    - `docs/visual-direction.md:91`: open, a painted ramp against plain URP Lit as a control.
    - `docs/experiments.md:299` (20 October): painterly realism chosen, look P its first version with shade in the sky's colour; `docs/research/building-blocks-decisions.md` D7.4: one shade function, `OS_ShadeP`, provisional until a look test at 1c.
    - No In short states the shading model. VD2 states SEASON's rule, which both sides hold.

20. **When the plan is re-sized.**
    - `docs/plan.md:215`: step 1 is "re-sized after next week from the usage log".
    - `docs/plan.md:208`: the whole plan is re-estimated when the stone is complete, or on 13 November if that comes first.
    - The In short (P3) follows `:208`, the plan review's P3 verdict.

21. **`NOW.md`'s stale "Next".**
    - `NOW.md:41–46`: the week starts from "`docs/plan.md`, Next week", a section that no longer exists, and Friday's milestone is "steps 0 to 2 reviewed".
    - `docs/plan.md:16`: Friday 23 October's milestone is the walk of the clay town with the corner inside it.
    - The In short (plan, PL1 and P1) follows `plan.md`, the plan review's verdict. `NOW.md` is being trimmed separately.


## D. The always-read files and the skills

1. **Who judges an experiment's end.** The `game-lab-workflow` skill, Ending: "Send the contact sheet to Øystein and ask for his judgement. Do not judge beauty yourself and call it done", and its Before building: "wait for agreement before building anything large". Against `CLAUDE.md`, How work runs, and the skill's own What goes to Øystein (moved from `NOW.md`): look and craft questions are ours, decided on frames with strict reviews, and Øystein judges the milestones; work runs on without waiting for him. The plan's Done (P2) needs his acceptance of a kind, which may be how the two agree. The same skill's What goes to Øystein also carries `NOW.md`'s old line on the architecture, "Only taste, scope and play go to him", where `CLAUDE.md` names scope, play, permissions and milestones and puts the look with us. The question test's after-answerer flagged it (Q9). Not settled.
2. **Who carries requests to Understory.** The `engine-bridge` skill said comments on Understory's `overstory` issues "are allowed when Øystein asks" and that "Øystein takes it to the engine project", against `CLAUDE.md`'s rule of 21 October (Overstory talks to Understory directly). Settled by the move: `CLAUDE.md`'s channel rules now stand in the skill, and its two lines point at them. `engine-requests.md`'s own line is C1, not settled.
3. **The skill's light check and sheet folder.** The `game-lab-workflow` skill, Ending: a light check in "morning, a grey afternoon and evening", and sheets "saved to `reviews/LT1/`". Against `docs/foundations.md` (three lights: drizzle, the 16:00 low sun, the blue hour) and the repo's `reviews/lt1/`. Not settled.
4. **The wall stones' library trigger** (A1). `NOW.md`'s line ("the scale test's memory") is gone with the trim; the clash now stands between `research/building-blocks-decisions.md` §14 (Q2) and `building-blocks.md`'s Repetition.
