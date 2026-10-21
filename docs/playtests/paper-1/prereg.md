# Paper playtests, round 1: pre-registration

What we expect and how we will read the results, written before the sessions it governs. Each part is committed before the first session it covers: the calibration part before calibration, the concepts' part before wave 1. Nothing here is edited after its data exists; a later change is added below as a dated amendment with its reason.

## Calibration (committed 21 October, before calibration)

The model players rate kindly (`method.md`, "What a paper test cannot show"; `docs/research/playtesting.md`, section 6). Calibration gives each player two fixed points: its genre's well-loved **anchor** game (`calibration/<id>/`) and **Saltlight**, a known-weak game (`calibration/weak/gm.md`): a pretty, warm walking simulator with no goal, no failure, choices that converge and a meter that only rises, the failure Overstory rules out. Every player plays the anchor first, then Saltlight, in the same session with the same player agent.

**The kindness check.** A player passes if both hold:
1. its Saltlight pull (mean over its rounds, with the exit's overall pull counted as one more round) is at least 3 points below its anchor's, on the 0 to 10 scale;
2. its Saltlight exit names, in its own words, at least two of the three hollow features built in: nothing at stake (no goal, no failure, a meter that only rises); choices that converge; people, history and collectables that are décor.

A player that fails is flagged **kind**. Its taste measures (marks, pull, keep-playing and buy answers) are reported but count half in any ranking. Its headline measures (below) keep full weight, because they are scored against the engine's record, not against taste.

**The relative scale.** Each concept's pull for a player is also reported as `(concept − Saltlight) / (anchor − Saltlight)`, using the same means: 0 plays like the known-weak game, 1 like the genre's best. Where `anchor − Saltlight` is under 1 point the scale is undefined for that player and only raw pull is reported.

**Persona crossed with model.** Each kind plays on Sonnet in one cohort and Opus in the other (`reviews/lt1/playtests/paper-1/roster.md`). Anchors and Saltlight are identical across the twins, so their X against Y differences estimate the model effect per kind. We expect Opus players to write longer acts and name more needs, and Sonnet players to give higher pull. A model difference of 2 points or more in pull on the same anchor is reported, and concept results are then shown per cohort as well as pooled.

**The headline measures** for the whole round, chosen because a model player's taste is the least trustworthy thing it gives:
- **predictions:** each round's prediction scored right, partly or wrong against the record, with the cause of each misreading;
- **understanding:** the memory probe and the exit's claims about named people, scored the same way;
- **needs:** what each player wanted to know or see that the screen didn't give, coded into the must-improve register.

Marks, pull, the stakes probe and the exit's answers are secondary and always shown beside the calibration.

**The game master audited.** Each run's game master keeps a fact ledger (`gm-brief.md`, "Your files"): every claim on every screen with its source and how the player could know it. Per concept, a fresh Opus auditor checks every screen against its rows and a sample of at least 20 rows per run against the engine. A run with a leaked private fact that changed a player's decision, or a contradiction of the engine that changed an outcome, is **compromised**: reported, but left out of the lives on against off comparison. Calibration games are invented worlds and keep no ledger.

## The concepts (committed before wave 1, 21 October)

Written on Opus 5.5 before any concept session. The football, mystery and band cards exist; the other four concepts' hypotheses come from the panel and `method.md`, and are amended below, dated and reasoned, before their wave if their card changes a mechanic they rest on. Waves and arms follow `reviews/lt1/playtests/paper-1/roster.md` and `arms.md`, which supersede `method.md`'s order: cohort X plays lives on in football, the journalist and the rpg; cohort Y in the mystery and the band.

Right scores 1, partly 0.5, wrong 0; gaps are in percentage points, lives on minus lives off, over the six kinds. A **pair** is one kind's two runs of a concept. A result between the two thresholds is unsettled. Six runs an arm can't carry statistics: every result is a hypothesis for the greybox, and refutations are reported in full.

### Per concept

Football's spring 1989 is thin and its shift roll identical in both arms, so its gap should show after the jump; both halves are reported. The mystery's accuracy gap is partly built in (the off case has no reasons to find), so there the play measures decide. The restorer has no control, so R2 stands in for one.

| Hypothesis | Measure | Supported if | Refuted if |
| --- | --- | --- | --- |
| **Football** | | | |
| F1. Lives make forecasts (all panels) | prediction accuracy; the 1994 roll call | 15 points; a third of the missing named with reasons | within 5: the town is a skin |
| F2. The control arm is kind to the club and harsh to the paper (systems) | the relative-pull gap in football and in the journalist | football's under 0.1, the journalist's 0.2 or more | football's the larger, or 0.2 or more |
| F3. Ignoring the town costs (systems, card) | league points by the tenth hour: player 6's town-blind play (cover for all, the best seven) against players who read the town | town-blind finishes below | level or better; untested if not played |
| F4. The stakes reach people (systems) | the stakes probe | four of six lives-on exits name a person or promise | four name only the table |
| **Mystery** | | | |
| M1. Lives make it solvable (card, experience) | the case-2 close, 0 to 100, each arm on its own key | lives on 50 or more, with four reasoned facts (3, 5 to 10), 25 above lives off, fewer innocents named | lives on under 50 |
| M2. A death without a culprit holds (all panels) | the sceptic's and optimiser's pull against their anchors; "cheat" at the close | both within 3; under three cheats | three cheats, or both 3 below and naming no risk |
| M3. The engine's best mystery is its small wrongs (systems) | case-2 turns on the song's credit or the band place; the exit on Edward Baker and Sarah Lane | over half; both right with reasons in four of six lives-on exits | under a quarter of turns |
| M4. The screen is fair (card, narrative) | causes of wrong claims, such as joining Sarah's shout to Andy Shaw's death | a third or fewer trace to a screen or record | more than a third |
| **Band** | | | |
| B1. Chemistry can be read (card, experience) | predictions about members | 15 points | within 5 |
| B2. Refusals read as people (all panels) | refusals and departures explained: a cause, dice, or nothing | half right with lives on; "dice" in one exit at most | under half, or "dice" in two |
| B3. The rounds aren't empty (systems, card) | rounds with no costly decision; marks on the third gig | under 40% in both arms; under half bored at the third gig | 40% by round 4, or half bored in both arms |
| B4. Choices feel costly (narrative, card) | "I shouldn't have…" tied to the player's own decision | twice as many with lives on | as many or fewer |
| **Restorer** | | | |
| R1. Reading pays (all panels) | inspection accuracy against money at the jump and the tenth hour | the two best readers in the top three; the optimiser's blind flip earns less | the flip earns as much |
| R2. People enter the decisions (all panels) | buy, sell and works decisions citing an owner, tenant or neighbour | a fifth or more | under a fifth, as the panel predicts |
| **Family** | | | |
| Fa1. There is something to lose (systems) | the stakes probe | five of six name a loss | three name none |
| Fa2. Evenings cost (experience) | the spread of evenings; regret tied to one | uneven, with regret, in four of six | even and regret-free in four: the checklist |
| Fa3. The weakest game (all panels) | relative pull and ready today | last or second last on both | top three on either |
| **Journalist** | | | |
| J1. Checking pays only with lives (narrative, experience) | printed claims true, independently checked against unchecked | 20 points with lives on, under 10 off | the same difference in both arms |
| J2. Source judgement is learned (systems) | printed claims true, rounds 1 to 3 against 4 to 6 | up 15 with lives on, under half that off | no rise on, or the same rise off |
| J3. The edition's trade is real (systems) | unconfirmed claims printed under pressure; the optimiser's confirmed-only paper | four of six print one and it lands; confirmed-only loses sales or a story | confirmed-only loses nothing |
| J4. The town finds the story (systems, experience) | stories begun from something seen, against records | a quarter or more | under a quarter: the page wins |
| **Rpg** | | | |
| Rp1. The world remembers (systems, experience) | reactions a round to acts the reactor didn't see; pull in rounds without one | one a round with lives on; pull drops under 2 | under one, or a drop of 2: predicted, as the engine answers monthly |
| Rp2. A goal forms (systems, narrative) | the sceptic's goal and risk by round 3; rounds on one self-set goal | both; three rounds in four of six runs | neither, or four wander |
| Rp3. Six rounds can't tell the arms apart (systems) | relative pull and engaged marks of players 2 and 5 | a gap under 0.1 | 0.2 or more for lives on |

**Across the five,** the panel predicts the largest accuracy gaps in the journalist and the mystery, the smallest in football and the rpg; refuted if either of these has the largest.

### Lives on against lives off

The round's most important result, per concept and pooled over the five:
- **prediction accuracy;**
- **understanding accuracy** (memory probe, exit claims), "what happened" and "why" scored apart;
- **relative pull;**
- **reading payoffs:** turns resting on something read from a screen about a life or a place's history, true in that arm's record, whose outcome under the card beat the act's default (an offer that met a cause, a claim that held). Lives off pays the same rules on dice, so its count is the luck baseline;
- **costly decisions:** the player names, unprompted, what a decision gives up, and the card makes the cost real;
- **the stakes probe** naming a person or a promise.

Analysts code from folders known only by letter, though content often betrays the arm. A lives-off "why" can only be wrong, so understanding is compared on "what", and each cause a lives-off player asserts counts as a **confabulation**. If they tell causal stories as often as lives-on players, model players can't tell lives from noise.

**The confound.** Each kind's two runs of a concept are on different models. Each arm holds three Sonnet and three Opus players, so a model effect common to all kinds cancels within a concept; one that differs by kind doesn't. Over the five, each kind plays lives on three times on its cohort-X model and twice on its cohort-Y model, so pooling leaves a fifth of it. We report the raw difference; the difference adjusted by each kind's model gap in calibration (the twins' anchor and Saltlight pull, and prediction accuracy where scored), subtracted where lives on ran on Sonnet and added where on Opus; and the pairs by sign. Cohort memory (X met lives on first) can't be told from cohort; results are also shown per wave. The pooled difference always carries this caveat.

**The lives pay off in a concept** if prediction accuracy (the journalist: printed claims true) is 15 points higher with lives on, in all pairs but one at most, and 10 after the adjustment; and a play measure moves with it: a reading payoff or a costly decision more per run, or two more stakes probes naming a person. Accuracy alone is **reads better, plays the same**: a better book, not yet a better game. A relative-pull gap of 0.15 or more is shown beside, never decisive. The lives **don't pay** if accuracy is within 5 and no play measure moves. Pooled, they pay if two thirds of the pairs favour lives on in accuracy (20 of 30: a one-sided sign test at about 5%).

**If no concept pays.** Text favours reading lives more than any screen will, so this is the strongest negative the round can give. We conclude that today's export and cards don't bring the lives into play, and tell Øystein before more concept work; the register finds the broken link: the engine (too few knowable causes), the screens (causes unseen) or the cards (no rule rewarded reading). No concept built on reading lives goes to the greybox until a paper retest pays. A positive is weaker evidence, since kind models and text flatter reading.

### Ready today and potential

Two scores, 0 to 10, on the lives-on arm (a lives-off arm gets a ready-today score for reference). **0** plays like Saltlight; **10** like the nearest calibration anchor: the FM match week (club, band), the Papers, Please day (restorer, journalist), the Stardew day (family), the Obra Dinn deduction (mystery), the Baldur's Gate 3 quest (rpg). Relative pull, on the same scale, is the starting point.

- **Ready today:** what the sessions showed with today's engine and interface: relative pull (kind-flagged players at half weight), headline accuracy, payoffs, costly decisions, Juul's six in play, would-quit marks, the exit's keep, buy and return answers, whether the tenth hour held; beside it, the share of resolutions GM-simulated: play nobody has built yet.
- **Potential:** what the concept could be with its must-improve items done, judged from the causes of its failures. Each point above ready today names its register item and the failures it removes. A failure of structure (no valued outcome, a core that doesn't use the lives) caps it. Each potential names its costliest prerequisite, such as a town ten times larger.

Two scorers, blind to each other: the concept's analyst (fresh Opus) and a strict Fable reviewer on a lean packet after the usage reset (or, if Fable is out, a second fresh Opus, noted). Each gives both scores, a line of reason and its three weightiest pieces of evidence. Within a point, the mean stands; further apart, both are reported with reasons, unaveraged, with what would settle them in round 2. Øystein and his testers have the final word.

### The must-improve register

The round's main output, in four areas: the engine; Overstory's world and systems; the interface; the content. Each item gives area, level, evidence, effect, concepts served and owner: an engine request (its number in `docs/engine-requests.md`, or new) or Overstory (the owning doc or system).

- **Must:** its absence broke play or kept the lives from paying (a would-quit, a refuted hypothesis, a decision wanted and impossible, a misreading traced to a screen), in two runs, or in one plus a mechanism that makes it recur (a card rule, an export fact, an `engine-rules.md` line).
- **Should:** its absence lowered a secondary measure (pull, bored or confused marks, a repeated need) in two runs, without breaking play.
- **Could:** seen once without a mechanism, or a panel prediction neither borne out nor contradicted.

Evidence cites run, round and row. A need met later in its run drops out; one named as often in both arms belongs to the interface or the content, not the lives. Each panel must-item is marked borne out, not seen or contradicted; a panel alone never lifts an item above could. What only GM simulation supplied (the match, the edition, the works) goes under the domain model it needs. Items are ordered by level, then by concepts served.

### The ranking

The panel's mean rank: journalist 1.3, mystery 2.0, band 3.7, rpg 4.3, football 4.7, restorer 5.3, family 6.7. The round ranks by mean potential, ties broken by ready today. A controlled concept whose lives don't pay ranks below all whose lives do; the restorer passes only if R2 holds, and the family, all people, isn't gated. Text flatters the paper and the mystery and starves the band and the club (experience), so a tie within a point goes to the band or the club.

The order changes if the journalist's gap isn't among the two largest, or J1 or J4 fails; if the mystery draws three cheats or a close under 50; if football pays despite a kind control (the town then matters where the match carries the fun); if the family's Fa1 and Fa2 land. If the journalist and the mystery lead but fail differently, the panel's shared hybrid, the reporter who covers deaths, is tested against both failures.

### What would change our minds about the approach

Against paper playtesting here: four of the twelve players flagged kind (taste is noise; headlines stand); over a quarter of runs compromised (round 2 needs a tool that serves screens by visibility); predictions at the base rate in both arms everywhere (the measure separates nothing); a model gap larger than the arms' wherever both are measured (round 2 gives a kind's two arms to one model); outcomes tracking the dice more than the lives (we measured our simulations). For it: accuracy favouring lives on in three of the five concepts, in most pairs, with must-items converging; round 2 then runs the ablations.

On a lives-driven world: lives that pay in understanding but never in play make a better book than a game, the walking simulator `CLAUDE.md` rules out. Lives that pay in play in two concepts, one with a domain loop of its own (the club or the band), make the asset general.

### Exclusions and stopping

- **Compromised runs** (the audit above) are reported but left out of the comparison and the pair counts; arm means are shown with and without them.
- **Failed players** are restarted with the same message (`gm-brief.md`). A player that reads beyond its screens, or acts on a fact no screen gave, compromises its run. A run the harness stops before round 4 is excluded and, usage allowing, rerun from round 0 with its memory file restored. A run ended by the card's own failure (sacked, folded, the loft lost) is a result: its exit runs, and its measures cover the rounds played.
- **A usage cut** stops at a wave's end with everything pushed; the roster puts the controlled concepts first. A concept with one arm done gets no comparison; one not played is marked so, not placed by the panel.
- **Amendments** go below, dated and reasoned. One made after its data exists is marked post hoc, and what it adds is exploratory.

## Amendments

### 1. From 72 runs to 24 (21 October, 21:13, before any concept session)

**Why.** Calibration showed what the method costs. Between 20:22 and 21:10 the 5-hour window went from 16% to 75% and the weekly budget (all models) from 5% to 20%, with calibration, the cards and the setups the main users. A concept run costs about 1.2% of the week, so the 72 runs as designed would take about 90%. The week's budget also carries the architecture's port and the camera research, which come first (`NOW.md`). The figures are in `usage.md`. The lead session chose the lean design, A, and set its conditions.

**The design now.** Three concepts, each with its control. They are the panel's top two and the club, the concept with a domain loop of its own. Four kinds an arm: the sceptic (5), the optimiser (6), the explorer (4) and the concept's genre fan, the Football Manager devotee (1) for the club and the Baldur's Gate 3 player (2) for the paper and the mystery. The explorer is the mystery's own genre fan, so the mystery's fourth seat goes to the role-player.

| Concept | Kinds | Cohort X plays | Cohort Y plays | Cold start |
| --- | --- | --- | --- | --- |
| journalist | 2, 4, 5, 6 | b (on) | a (off) | 2 |
| mystery | 2, 4, 5, 6 | b (off) | a (on) | none (its cold kind, 3, no longer plays) |
| football | 1, 4, 5, 6 | b (on) | a (off) | 4 |

Arms, models and the twins' matched starts are as before (`arms.md`, `roster.md`). Each player keeps one order, and its two cohorts' twins play each concept at the same point in it. Kinds 2 and 4 play the mystery and then the paper; kinds 5 and 6 play the paper and then the mystery, so both decisive concepts run from the start and their order is counterbalanced across kinds. The club comes last for kinds 4, 5 and 6, and is kind 1's only concept. Runs go in that priority: the paper and the mystery, lives on and off, then the club.

**Not tested.** The band, the restorer, a life and its heirs, and the role in the town are not played. Their cards and the panel's notes stand as design work. In the report they are marked "not tested" and are never scored, ranked or placed by the panel. Their hypotheses (B1 to B4, R1 to R3, Fa1 to Fa4, Rp1 and Rp2) lapse, as does F2's half that rests on the journalist (it stands: football against the journalist). The other runs of options B and C wait until after Monday's reset, and run only if these results leave the ranking open. The report names them as a follow-up.

**What loses power.**
- Each arm has four runs, not six. Counts written "n of six" scale to the same share of four, rounded up: four of six becomes three of four, five of six becomes four of four, three of six becomes two of four. Point thresholds stay as written; with four pairs a concept's gap rests on fewer pairs, and a single pair moves it more.
- The cozy player plays no concept, so nothing here speaks for calm, low-punishment play. Three of the four kinds are the hardest judges (the sceptic, the optimiser, the explorer), which tilts taste measures down against the panel's six-kind expectation.
- The Football Manager devotee plays only the club, and the role-player plays only the paper and the mystery, so neither gives a comparison across all three concepts. The explorer, the sceptic and the optimiser do.
- The mystery has no cold start, so its first-minutes reading rests on the tutorial for every player.
- The ranking covers three concepts. It can't say where the untested four would fall.

**Stopping.** A run that has started is played to its end and committed. No new run starts while the weekly budget is above 55% or the 5-hour window above 90%; then the round stops, commits and reports what is left, resuming after the next 5-hour reset where only the window stopped it. The kindness check, the game master's audit, the measures and the models are unchanged. The second scorer of ready today and potential is the main session's Fable review, which this round's report leaves to it.
