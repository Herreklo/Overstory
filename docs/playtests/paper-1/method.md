# Paper playtests, round 1: how the studio runs

Status: the method of plan step 1f+ (`docs/plan.md`), run 21 to 22 October 2026 on Opus and Sonnet (Fable reviews after the usage reset). Every agent in the studio reads this page first. The method was set before play; the hypotheses in `prereg.md` were committed before the first session.

Øystein asked: "can you playtest as well. like put a bunch of agents, really analyse the concepts, what feels fun, what feels engaging ... put yourself in the mind of a game developer in this sandbox, and really really push it". Then: "Really make these tests worth it." And the purpose: "We will not land on a game after this, but we will definitely know what's missing, and what we HAVE to improve." So the round's main output is a **must-improve register**: what the engine, Overstory's world, the interface and the content must gain, backed by the sessions. The ranking of concepts comes second.

Agents can't feel fun. Reasoning, comparison with the best games and careful simulation of players can find confusion, dead stretches, empty repetition, broken loops and missing motivation. Øystein and his testers have the final word.

## The standing rule

**A game, not a walking simulator** (`CLAUDE.md`, Øystein, 21 October). Every concept has goals, challenge, stakes, mastery, failure, and decisions that cost something. Reading the world is a skill that pays off in play, never the whole of the play. Each concept is judged against Jesper Juul's classic game model: rules, a variable outcome, values on the outcomes, player effort, attachment to the outcome, negotiable consequences.

## The world under every concept

- Overstory is the visual and game lab on the Understory engine. The engine simulates people's lives over decades; every event has causes with weights, a visibility (private, local or public: who could have seen it) and a notability. The engine decides; Overstory shows.
- Overstory's question (`CLAUDE.md`): can someone read people and history better from the world on screen than from the engine's page?
- Decided (`NOW.md`): the world on screen starts in 1989 and moves forward; the past is the starting record; the player's acts change the 3D world; the screen shows evidence, never verdicts; how years pass depends on the game; the town is a dense, steep harbour town of a few hundred buildings; people are blockout figures for now; signs and names are English placeholders; Rule 8 (no homophobic, sexist or racial content).
- The three dials (`docs/living-world.md`): control, influence, knowledge. The four layers of the record: facts, traces and records, beliefs, discoveries.

**The world the game masters run** (all in `reviews/lt1/playtests/paper-1/world/` unless named):
- **World 9989,** a real engine run: `fixtures/engine/understory-world-9989.json`. 119 people (76 in town), 51 households, 9 places of work (the sawmill, the harbour fleet, the garage, the clinic, the school, the Courier newspaper, the Anchor pub, the council office, the Old Bank Café), 25 ventures, 4 bands (the Sawmill Boys, the Night Shift, Driftwood, Pirate Radio), 2,635 events with causes, weights, visibility and notability. **Re-dated by -37 years:** the engine's 2026 to 2036 is the town's 1989 to 1999; its earlier dates are the town's past record. Its reads show the truth, so a game master filters by visibility for what a player could know. It has no buildings.
- `atlas-9989.md`: the run indexed for game masters (people, households, places, ventures, bands, storylines, public and local events by year), the corner's houses A to E cast with households, and the town's places.
- `records-9989.md`: the in-world records: the Courier's articles written from public events (sometimes wrong where the engine's `tell` chains distort), posters for gigs and festivals, chatter at the Anchor from local events.
- `engine-rules.md`: the engine's documented logic, as a rulebook. What it does not simulate must be marked **GM-simulated**.
- `lives-a.md`, `lives-b.md`: lives from the engine's published reading packs (other worlds), for colour and cross-checks.
- `docs/ideas/stories-in-the-world.md`: real lives read twice, trace patterns, mysteries that arise by themselves, what is missing.
- The corner's fixture `fixtures/lt1-corner.json` (houses A to E with dated diaries, labelled `authored`), the gully steps, Harbour Row and the quay.

## The concepts

| # | Slug | Concept | Arms |
| --- | --- | --- | --- |
| 1 | `football` | The club: a small-town amateur football club; the squad is the town's real people from world 9989 | lives on and off |
| 2 | `band` | The band: a band in a quay loft whose gigs change the street | lives on and off |
| 3 | `restorer` | The observer reshaped as a game: a restorer who returns to places, reads what lives did to them, and buys and restores against money and time (`first-game-options.md`, option 3) | lives on |
| 4 | `family` | A life and its heirs: a family across generations, an inherited house worn and changed | lives on |
| 5 | `journalist` | The paper: a reporter at the Courier finding out what happened to someone | lives on and off |
| 6 | `mystery` | A death in the town, read through lives, records and traces over the years (nearest: Shadows of Doubt, Pentiment) | lives on and off |
| 7 | `rpg` | A role in the living town with Baldur's Gate 3-like reactivity, whose acts and relationships play out over years | lives on and off |

Each concept's playable card is in `cards/<slug>.md`: the player's role, goal, resources, opponents or pressure, fail states, mastery curve, the three dials, the screens and verbs, the time jump, and the pitch a player sees.

## The control: lives on against lives off

The most important result of the round. For five concepts a second arm runs with the same card, the same screens and the same cast's names, jobs and places, but **the simulated lives are replaced by generic, cause-free events of the same density, and the town has no history** (`world/world-9989-off.md`). Players are blind to their arm: arm folders are named `a` and `b`, and which is which is held in `arms.md`, which players never read. If players don't engage more, read better or decide differently in the lives-on arm, the world's unique asset isn't paying off in that concept.

## The players

Six kinds, two cohorts (X and Y) of the same six. Each player agent stays with its cohort across concepts, keeping its own memory, so it calibrates once and can compare. Each cohort plays six concept arms; the two cohorts play the two arms of a concept at the same point in their order, so order effects match.

| Id | Kind | Model |
| --- | --- | --- |
| 1 | Football Manager devotee: spreadsheets, long saves, wants systems to master and a club to own | Sonnet |
| 2 | Baldur's Gate 3 and RPG player: wants reactivity, choices with teeth, companions, their character's story | Opus |
| 3 | Cozy-game player (Stardew Valley, Unpacking): calm routines, small kind acts, a place that grows, little punishment | Sonnet |
| 4 | Explorer (Outer Wilds, Pentiment, Return of the Obra Dinn): wants to understand, deduce, connect clues; hates being told | Opus |
| 5 | Sharp sceptic: has played everything, quits fast, names what is hollow. Asks every round: "what am I trying to win or achieve, and what do I risk?" | Opus |
| 6 | Optimiser: hunts the dominant strategy, the exploit, the loop a min-maxer would grind, what breaks or trivialises the game | Sonnet |

**The order** (X | Y; "on" is the lives-on arm):

| Wave | Cohort X | Cohort Y | Cold start |
| --- | --- | --- | --- |
| 1 | football, on | football, off | 4 |
| 2 | restorer | family | 1 |
| 3 | band, off | band, on | 6 |
| 4 | mystery, on | mystery, off | 3 |
| 5 | rpg, off | rpg, on | 5 |
| 6 | journalist, off | journalist, on | 2 |

**Calibration.** Before the concepts, each player plays a short paper version of a well-loved loop in its genre, run at the same text fidelity as our screens: an FM-style match week (1), a Baldur's Gate 3-style town quest (2), a Stardew day (3), an Obra Dinn-style deduction (4), a Papers, Please day (5), a Slay the Spire fight and its reward (6). Its marks and pull scores are the player's anchor; concept marks are reported relative to it, because agents tend to rate everything kindly.

**Robustness.** Different players get different households and corners of world 9989 (the same start for players 1 to 6 in both arms), so one lucky story doesn't carry a concept.

## Knowledge kept apart

- **Players see only their screen.** A player reads only the screen files its game master writes for it, and writes only its own action files. It never opens anything else: not the game master's files, other players' files, the repo's docs, the fixtures or the engine. A screen shows what the interface and a witness could show: what is visible on the street, what someone says (which may be wrong), records (which may be out of date), what the player has found. Never the truth.
- **The game master holds the truth** in `gm/`. It runs from world 9989 filtered by visibility, and the corner's fixture. Where it must simulate the engine (matches, music, crime, buildings, the player's influence) it follows `engine-rules.md` and labels the outcome **GM-simulated** in its log, never inventing an outcome against the engine's rules. Screens carry no labels; the log does.
- The game master doesn't steer players towards fun. It runs the concept as its card describes, honestly, including its dull parts, and keeps results plausible.

## A session

One game master per player run (Opus), so each run has its own state; all runs of a concept arm share one setup (`<slug>/setup-<arm>.md`).

- **Round 0:** the opening screen: the pitch as a store page and a first-minutes tutorial would give it (none for the cold-start player), then the first screen.
- **Rounds 1 to 6.** The player reads its screen and writes `rN-act.md`:
  - **marks** for each turn resolved last round: `curious`, `engaged`, `bored`, `confused` or `would quit`, one line of why, and **surprise**: none, a delight, or a cheat;
  - **pull,** 0 to 10: how much it wants to play the next round;
  - a short **think-aloud**;
  - one **prediction:** what will happen next to one person or place, and why;
  - **needs:** each thing it wanted to know or see that the screen didn't give;
  - up to **four turns.** A turn is one meaningful act: an inspection, a conversation, a decision, a journey, letting time pass. Each turn states what the player **expects** from it. Later turns may be conditional.

  The game master resolves the turns in order, may interrupt, follows the card's clock, and writes `rN-screen.md`: each turn's result, the new screen, and the prediction's outcome when it comes due.
- **Concrete screens.** A screen shows what the game would show, not a summary: the place (the corner's houses A to E, the gully steps, Harbour Row, the quay, the Anchor, the Courier, the sawmill, the Old Bank Café), who is there and what they are doing, what can be read on surfaces; then the verbs available and the interface (hover names, inspect, the journal, the why-probe that answers only from the record with its sources), and in-world records where they exist.
- **The time jump.** Every card has one jump (a year, or five) mid-session and a return to the same place, to test what only this world can do.
- **The memory probe.** The round 4 screen asks what the player remembers about three people met in rounds 1 and 2.
- **Round 6** ends with the **tenth hour:** the game master summarises the next twenty in-game turns of the player's own strategy, honestly, with the world's events continuing.
- **The exit interview** (`exit.md`): marks for round 6; would hour 10 still hold; would it keep playing, buy it, come back after a week; what kept it, where it nearly quit, what was hollow, which game does this better, what it would change; **the stakes probe** ("what would you lose if you stopped now?"); **understanding:** what it believes happened to two or three named people, and why.
- **Scoring.** The game master scores each prediction and each understanding claim against the engine's record: right, partly, wrong, and for each misreading its cause (a screen, a wrong record, a witness's error, the player's own leap). It logs every need.

## Files

Full transcripts in `reviews/lt1/playtests/paper-1/`:
- `world/`: the world pack;
- `calibration/`: the calibration runs;
- `<slug>/setup-on.md`, `setup-off.md`: the shared setups (game masters only);
- `<slug>/<a|b>/<player>/`: `r0-screen.md`, `r1-act.md`, `r1-screen.md` and so on to `exit.md`; the game master's `gm.md` (truth, state, log with labels), `turns.md` (one row per turn: round, turn, verb, target, expected, outcome, consequence, mark, surprise), `needs.md`, `scores.md` (predictions and understanding, scored), and `condensed.md`.

The design and the results in `docs/playtests/paper-1/`: `method.md`, `prereg.md`, `panel/`, `cards/`, `sessions/` (condensed logs per concept), `analysis/`, `redesign/`, `replay/`, and `README.md`.

## What a paper test cannot show

Physical feel (camera, pace, the look itself), timing and rhythm, true surprise (a model player can't be surprised as a person is), boredom over real hours, the feel of a match engine or a tactics board, and whether the world on screen reads better than the page, which only the greybox and the cold readers can test. Model players share biases: kindness, verbosity, fondness for what is written well, and the text medium favours concepts that read well as text. Every finding here is a hypothesis for the greybox (1g).

For round 2, without running them now: ablations beyond lives on and off (traces off, time jumps off, witness visibility off), to learn which parts of the world matter most.
