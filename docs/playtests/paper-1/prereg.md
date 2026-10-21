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
