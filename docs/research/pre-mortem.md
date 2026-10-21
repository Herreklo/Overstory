# Pre-mortem: the plan, seen from April 2027

It is April 2027 and Overstory has failed. The corner never reached a bar Øystein was proud of, or it did and people misread it, or it could not grow into a town, or the work stalled. This page tells the most plausible ways that happened, so we can stop them now. It covers the whole plan (`docs/plan.md`); the architecture gets its own pre-mortem on Tuesday.

Written 21 October 2026 on Opus 5.5 (Fable's limit is spent: the fallback rule), from the design docs, the digests and the usage log, with spot checks in the repository. The ranking is a judgement; Fable checks it when its limit resets.

## Where April 2027 sits

The rough sizes put the corner complete in 3 to 4 months and a first slice in 5 to 7. April is 23 weeks away: the first slice's due date. The base rate after three days: 232 commits; about 310,000 words in 69 docs against about 27,000 lines of code; the weekly limit at 83% by Wednesday, Fable's at 100%. Judged so far: the birches, and the gully steps at "close".

## The stories, ranked

By odds times harm. "Act by" is when the cheapest action must land.

| # | Story | Odds | Harm | Act by |
| --- | --- | --- | --- | --- |
| 1 | Nobody read it | High | Severe | end of November |
| 2 | The method ate the budget | High | High | this week |
| 3 | Overstory became the engine | High | High | before step 2 |
| 4 | The look was proven on the wrong screen | Medium-high | High | Monday and Tuesday |
| 5 | People never reached the bar | Medium-high | High | before step 2 |
| 6 | The look never converged: a closed loop of taste | Medium | High | the next milestone |
| 7 | The port split the source and slowed the loop | Medium-high | Medium-high | Monday |
| 8 | Nobody played it | Medium | Medium-high | before step 2 |
| 9 | The repository and the shared checkout broke | High | Medium | Monday |
| 10 | The docs stopped being true | High | Medium | Monday |
| 11 | A verdict slipped in | Low-medium | Severe | before step 2 |
| 12 | Baselines drifted | Medium | Medium | Wednesday |
| 13 | Licences were found late | Medium | Medium | before step 5's downloads |

### 1. Nobody read it

**How.** Whether history reads is the biggest risk, and no reading has run. Step 1f, the core idea in clay, "can start as soon as there is room", and there never is: the building blocks, the port, the light and the land each come first under "hardest to change first". 1f also waits on fixture gaps (B missing, no event after 1988, no reversal). When readers run, they are models reading stills. They know building history better than the public and share the maker's associations (`foundations.md`); the shuffled-facts control catches reading conventions, not people who see nothing at the street stop. People read only in the engine's human test: ten minutes, after the page, on the engine's schedule. And criterion 4 compares the scene with the engine's page, but the engine models no buildings: for the corner's main subject there is no page.

**Odds and harm.** High; severe. A beautiful corner that strangers misread fails Overstory's own question.

**Warning.** End of November with no reader numbers; 1f moved twice.

**Cheapest action.**
- One model-reader round now on frames we have (the gully's views and variety sheet): real, layers off, facts shuffled, scored by script. It tests the method and gates nothing. About a day of agents.
- 1f in a dated week, from 2 November, before the port's later stages. Its findings set the history budget, which sets what the history maps carry. The fixture gaps are half a day.
- The page for buildings written: each diary as plain text, so criterion 4 can be tested.
- Five volunteer human readers at 1f's gate, ten minutes each (for Øystein). People already win over the panel; this makes sure there are some.

*In `plan.md`:* The order, 1f (a date); The days, Tuesday.

### 2. The method ate the budget

**How.** Every kind runs the full method: two research tracks, a digest, a register, a quick sheet, strict reviews on Fable, a pre-mortem, docs. Each step is right; together they are a fixed cost per kind, and the corner has about twenty kinds and a dozen materials to go. The first week: fourteen studies at 22 to 57 million tokens each, main sessions 54% of usage, ten words of docs per line of code. The first-slice estimate of 7 to 11 months was re-based to 5 to 7 on the stairs reaching "close" in a day and a half, though "close" is not done and the stairs are being rebuilt. The studies put the gully's port at 16 to 22 Opus-days against three planned, and an Opus-day has no measured size in the weekly limit. By April the corner is in step 2, people have not started, and the pressure lands on the one thing that may not give: the bar.

**Odds and harm.** High; high.

**Warning.** The limit past 80% before Thursday again; a week with no measured number and no frame Øystein can judge; research, reviews and docs over half a week's usage.

**Cheapest action.**
- Two columns in `docs/usage-log.md`: the kind of work (build, measure, review, research, docs) and what the job left behind. After two weeks, set the shares and hold them.
- The plan re-sized by 13 November in one unit, per cent of the weekly limit per finished kind, measured on the port.
- The scout, source list and fresh writer adopted before the next study (`working-with-claude.md`, item 2).

*In `plan.md`:* Budget; Rough sizes (a date and a unit).

### 3. Overstory became the engine

**How.** The engine models no buildings or homes, and places never close. Homes (#59) come after the band year; buildings apart from businesses (request 5) and the fabric pass (6) are unfiled and unowned; the start year (#23) is paused. So Overstory writes the facts behind 1989's look: the past grown from 1870 over about 20,000 plots ("Our stand-in runs the pass today", `town-system.md`), owners, tenure and care (`derived`), footfall (`authored`), works. That is a second simulation. Two seams break later. At the hand-off in 1959, the engine's households must land in houses whose owners our rules already chose, and nobody owns that agreement. When homes land, the engine puts people at addresses that contradict the diaries the corner was built from (D boarded in 1986, the café in 1988). And no frame has been drawn from a real engine run; how its TypeScript process runs beside a shipped player is "the engine's question" (`where-generation-runs.md`).

**Odds and harm.** High that the facts drift; medium that it is fatal. Harm high: the record behind every frame redone, or "the engine decides" quietly untrue.

**Warning.** More of the corner's facts labelled `authored` or `derived`; #59 or #22 moving later; a new rule of ours that sets a person's state.

**Cheapest action.**
- The seam written now, half a page in `docs/engine-contract.md`: facts ours for good (how wear, growth and care look), placeholders the engine must own (owners, households, vacancy, works), and checks at the hand-off (every engine household has an address in the grown past; no plot has two owners).
- For Øystein: one real run exported by the engine project as a fixture, so one corner frame is drawn from the engine's people before step 4; and the engine-in-the-player question put to the engine project, with the band as the shared date.

*In `plan.md`:* The order, step 4's check against the front door moved before step 2.

### 4. The look was proven on the wrong screen

**How.** Every judged frame was a still at twice the size, averaged down, which hid shimmer and set fades 1.5 times too far. No mark has been judged moving, and the brush, fixed to a 71 cm world grid, will slide (`painted-marks-in-motion.md`). If "true up close, painted from afar" swims in motion, the style's mechanism changes, and with it the channels every part carries. Cost hides the same way. Tuesday's scale test is clay, but the look's cost is per pixel: `OS_TownSky`'s 64 reads, growth and noise, `FogLights` over the heart's 403 lamps, SSR, occlusion, MSAA 4× at native 1440p, birch cards stacked about fifty deep. A city view puts that stack on far more pixels and lamps, first measured in step 6, after the parts are approved. The reference machine is also the build machine, a 24 GB M4 running Blender, Unity and agents; the base M4 Mac mini has 16 GB, and `foundations.md` names no memory.

**Odds and harm.** Medium-high; high. Cutting the look late reopens every approved part.

**Warning.** The corner alone over about 8 ms of GPU at the street stop; a frame time without its commit; crawl in the first motion sheet.

**Cheapest action.**
- Tuesday: one more scale-test run, the clay district drawn by the corner's real shaders on synthetic channels with the heart's lamps, at the street stop and city camera. Half a day.
- A provisional GPU budget per pass, in milliseconds, in `foundations.md`. A look feature joins with its cost.
- The first motion sheet judges the style itself: a pull-out from eye level to the city camera over the gully and birches, before the port.
- The harness stamps the commit, refuses a dirty `unity/` or a busy machine, and treats 16 GB as the floor.

*In `plan.md`:* The days, Monday and Tuesday.

### 5. People never reached the bar

**How.** `reality-check.md` rates the base body and its stylisation "Needs a person"; the rules are no commissions and no capture. The route for acts no library holds was our own capture, now ruled out, and how an agent edits library motion against video is unstudied (inputs 4). People come at step 5, after the corner's style is fixed. If MakeHuman bodies under our light look like another game, either the people get a style the town was not made for or the town changes. Criteria 2, 3 and 4 all need people.

**Odds and harm.** Medium-high; high. Without people the first slice cannot be tested.

**Warning.** The first stylisation stills do not sit in the corner's light; feet slide on the treads.

**Cheapest action.**
- The grey walker on the gully (inputs 4): an MPFB body, two library clips, feet on the exported treads, a sit point, the brush on a rest-pose coordinate, in the motion sheet. One to two days in the port's week.
- The stylisation stills brought forward: one person at 20, 45 and 70, set into the corner's frames in three lights. Two to three days.
- A gap pass on editing library motion against video before step 5.

*In `plan.md`:* The order, a people spike between 1e and step 2.

### 6. The look never converged: a closed loop of taste

**How.** Claude paints the targets and builds the parts; Fable judges against those targets; model readers read them. Øystein is the only human eye, at milestones. Fresh reviewers start without memory and bring new lists: the gully took six strict reviews to reach "close". Every approval so far was made under a light fixed by four guesses, which step 1c replaces. Øystein's taste shows when he sees results (the restart of the visuals; painted, then a middle ground), each turn after work was built. In April the corner passes every review, and Øystein finds it competent but not his.

**Odds and harm.** Medium; high.

**Warning.** Øystein's verdict differs from Fable's last one; his corrections are about direction, not detail.

**Cheapest action.** Record Fable's verdict before Øystein sees a milestone, and track agreement; below four in five, the brief changes. A taste set of twenty frames Øystein ranks blind once a month in ten minutes, given to reviewers as calibration. Each review starts from the last one's list and adds only blocking faults. Approvals before 1c marked provisional.

*In `plan.md`:* The order, the line on strict reviews.

### 7. The port split the source and slowed the loop

**How.** The port waits on Øystein. Meanwhile the stairs' five faults, the trees' near tier and the cheek walls are fixed in Python, each fix code the port must copy: two sources by the back door. After the port, a quick sheet is no longer one Blender run but C# in Unity's batch mode: editor closed, one project, one run at a time. Sessions queue on Unity just as the houses, the kind with the most parts, begin.

**Odds and harm.** Medium-high; medium-high, mostly time.

**Warning.** `blender/generators/` growing after a kind's port starts; quick sheets twice as slow.

**Cheapest action.** The port decided now, with Python frozen per kind once its port starts. The C# core required to run under plain `dotnet` without Unity, with quick sheets rendered from its output: a requirement, not "if iteration needs one". A check that fails any branch, count or choice taken from `exp`, `sin` or `pow`.

*In `plan.md`:* What the architecture decides, where each stage runs.

### 8. Nobody played it

**How.** No one has moved through the town. The camera is "part of the style" and the main way to play, yet its craft is a research gap and the playable camera test is in step 5. A free camera at 2.8 m in lanes 3 to 4 m wide under deep eaves clips walls and finds backs no one built. The finding of 20 October (a camera at fixed height never sees the lanes) showed the camera decides what must be made. Which game comes first is open, so nothing tests whether reading history is something a player wants to do.

**Odds and harm.** Medium; medium-high.

**Warning.** The first person to fly the camera fights it instead of looking.

**Cheapest action.** A grey playable camera in the clay heart, in Monday's macOS player build: the height rule, collision with eaves, the judging paths. One to two days; then a playable build each month.

*In `plan.md`:* The order, beside 1f.

### 9. The repository and the shared checkout broke

**How.** `.git` is 2.3 GB after three days; `reviews/` is 1.0 GB, and FBX sits in plain git because LFS cannot reach the cloud workspace (`CLAUDE.md` still says LFS). GitHub asks for repositories under a few gigabytes and refuses files over 100 MB. Monday runs two sessions "in the same checkout": one index, one working tree, so one session's commit takes the other's half-done files. The tree already holds work in flight and Unity's rewrites of the URP asset, graphics settings and `M_Sky.mat`.

**Odds and harm.** High; medium: days lost, or a baseline taken on the wrong state.

**Warning.** `.git` growing over 100 MB a day; a commit with another session's files.

**Cheapest action.** A git worktree per parallel session, with Unity in one only. Generated meshes and full-size frames out of git now, with a hash manifest (`performance-at-scale.md`, P12, brought forward), and a pre-commit size check.

*In `plan.md`:* The days, Monday.

### 10. The docs stopped being true

**How.** The digests list about forty conflicts: the repetition rule in four forms, five sets of tier boundaries, a frame budget of 4 and of 2 million, whether generators make geometry, LFS, the engine's tag (`rH28` in the plan, `r41` in `NOW.md`). Decisions turn fast and live in several places. A session reads about 12,000 words before visual work, and every stale line is a chance to build to it.

**Odds and harm.** High; medium.

**Warning.** A review citing a superseded line; a question asked twice.

**Cheapest action.** Monday's register becomes the only home of "Decided" (id, decision, date, source, what it supersedes); other docs link by id. A grep for superseded phrases ("4 million", "runs no generation", "Life is computed offline") before every merge.

*In `plan.md`:* What the architecture decides.

### 11. A verdict slipped in

**How.** Keepers' care is derived from the owner's money, presence, age and character (`living-fabric.md`; request 13). A shabby front is the most vivid trace on a street, and readers read the owner from it: the failure the engine's human test found. If money or presence differs by group in the engine, neglect maps onto a group by rule: Rule 8 broken in aggregate, with no bad line anywhere. Generated in-world text (posters, the paper, graffiti) breaks it the day one line carries a slur or a stereotype.

**Odds and harm.** Low-medium; severe.

**Warning.** Cold readers naming who lives in a house ("poor", "a drunk", a nationality) from its front.

**Cheapest action.** Care from money, presence, age and dated events only; character reaches the fabric through acts, as `living-fabric.md` already says of feelings. An audit of the grown past: condition by any group variable. One task in the readers' brief, "who lives here, and what are they like?", with trait claims coded as false history. All in-world text from a catalogue in the pack, checked against a word list.

*In `plan.md`:* The order, steps 2 and 4.

### 12. Baselines drifted

**How.** Each port stage accepts a new golden baseline within FLIP's threshold; small drifts add up, and nobody compares the end with the start. Frames depend on the tree's state, since Unity rewrites assets during runs. By April, Fable and Opus may be replaced, so reviewers' and readers' scores from November and March do not compare. Dates are already off: 64 places in 17 docs date decisions to 22 October, written on 21 October.

**Odds and harm.** Medium; medium.

**Warning.** FLIP against the first golden view rising stage by stage; a reader score moving when the frames did not.

**Cheapest action.** Today's golden views kept as a permanent anchor, each stage reported against both, with a ceiling on the total. A frozen calibration set re-run whenever a model changes. Dates from the clock, and the 22 October entries corrected.

*In `plan.md`:* The days, Wednesday, step 0.

### 13. Licences were found late

**How.** No register exists, and "licences to check" sits in several studies. The people pipeline would mix MPFB (GPL add-on, CC0 assets), face packs with no licence found, CMU, 100STYLE, Mixamo (terms to check) and perhaps Quaternius, whose assets may never be redistributed however modified (`characters.md`). Era fonts are "licences to check"; the fronts study's 1989 chains are real firms. One bad clause at ship time means remaking the people.

**Odds and harm.** Medium; small now, medium-high late.

**Warning.** An asset with no entry; a "to check" older than a week.

**Cheapest action.** A third-party register (what, source, licence, offline or shipped, where used, checked when) and a build check that fails on anything unlisted. Fictional firms in the pack.

*In `plan.md`:* The order, steps 2 and 5.

## Not in any doc

No engine page for buildings (1); the 1959 seam (3); a 16 GB floor and a reference machine that is also the build machine (4); Unity as a single queue after the port (7); two sessions sharing one index (9); care from character as a path to Rule 8 (11); model churn and dates a day ahead (12).

## What a studio's lead technical artist would say

- "Your real building block is the channel layout, and nobody owns it." History, the mark coordinate, rest pose, element index, the light's bake and pick ids all claim channels; FBX brings 2D UVs and one colour (inputs 4, C9). Write one layout in bytes per vertex and per texel before the gully moves.
- "You have no budget sheet": milliseconds per pass, megabytes per kilometre at 16 GB, the 2 million triangles split by kind. The near tier alone is about 0.8 million before stone and houses (inputs 3).
- "Build a player every day, and measure on a quiet machine."
- "Pins are your content pipeline, and they are untested across a change of rules."

## What a producer would say

- "Every milestone is a quality gate without a date." Date 1f, the corner's first assembled frame and the first stranger.
- "Your burn rate is in the wrong unit": per cent of the weekly limit, and artefacts per week.
- "Øystein is a single queue." Batch download OKs, scope calls and judgements into one message a week.
- "The scope has no edge." A foreign-pack part in every done-list taxes every step; keep it a data check until step 10.
- "Write the cut list now": the six-level scheme, the foreign pack, the port beyond what play needs. Never the bar.

## What a creative director would say

- "Who painted the target?" The targets come from the hands they judge. Øystein picks three outside north-star frames, and the corner is judged beside them too.
- "Restraint is the hard part." A town where every surface tells a story reads as dressing. The history budget is the tool, and 1f first measures it.
- "Silent and empty reads as a diorama." A boom town in a slump is people, lit rooms and sound; both come late.
- "What does the player do in the first ten minutes?" Write it as a page before the corner is complete.

## For Øystein

1. Five volunteer readers at 1f's gate. *Recommended:* yes.
2. One engine run exported as a fixture by the engine project, and the engine-in-the-player question put to it. *Recommended:* yes, before step 2.
3. The C# port, with Python frozen per kind once its port starts. *Recommended:* accept now.
4. A ten-minute blind ranking each month. *Recommended:* yes.

## Not checked

The architecture (Tuesday's pre-mortem), the engine's code, the review frames, and every study in full. The odds are judgement, not measurement.
