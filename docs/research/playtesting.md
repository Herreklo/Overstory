# Playtesting

Research and design, 21 October 2026, on Opus 5.5; Fable reviews and extends it after the usage reset. It designs the playtest for plan step 1g, the playable greybox of the corner (`docs/plan.md`), and the rounds after it. Øystein: "the playtest will be extremely important."

Claims read in the author's own words (an essay, a paper, a talk's slides, an interview) are unmarked. Claims from reporters, summaries or abstracts are marked (secondary); claims we could not confirm are marked (unverified). Two helpers gathered most sources, and no page was fetched twice.

## The bottom line

- **This world can score its own playtests.** Sessions replay exactly from seed, build, commands and camera path. Every claim a tester makes has an answer in the record. A twin run without the player's commands measures agency. The engine's own readers (base rate 58 per cent, calibrated witness 64.6) are a yardstick for human predictions. No other game we found has all of these, so the test is built round a sealed key: every claim coded as fact, fair interpretation, harmless flavour or false history.
- **Game first.** Every session starts with a goal card and asks, at the end, what the player gave up. The decisive test of the standing rule is whether better readers win more. Players who fail and then succeed rate a game highest, and those who blame the game rate it lowest (Juul), so failure is designed in and its blame recorded.
- **Watch in silence, ask later.** Miyamoto, Valve and Golden Idol's makers all watch without speaking. Players then talk over a replay of their own screen with two neutral prompts (Gow and colleagues). Our replays are exact, so this cued commentary replaces thinking aloud for everyone but Øystein and his confidants.
- **Fix fast, then check the fix** (Microsoft's RITE), against a written list of what every newcomer must manage. Friends test usability only: people favour what they think the interviewer made about 2.5 times over (Dell and colleagues). Readings count only from strangers, each used once per seed.
- **Misreading is the risk to measure.** One vivid act is read as a whole character; a cut invites a cause; a word plants a memory. Confident wrong answers are the key number, probes use plain words, and "how did it happen, step by step?" separates a reading from the feeling of one.
- **Commit before confirming.** Deduction games check answers in groups (Obra Dinn's threes, Golden Idol's "two or fewer wrong") and make players cite evidence (Ace Attorney). A solver checks before any human plays that a case can be solved from what the screen shows. Shadows of Doubt shows that the shape of a case wears out before its content, so staleness is tested across seeds.
- **Agents go first, never last.** They find unreachable facts, broken replays, exploits and ambiguous evidence. They can't show fun, calm, real misreadings or the wish to return.
- **A deterministic town lets a reloader learn the future.** Tests play forward. Players accept permanent failure they opted into: about 141,600 beat Baldur's Gate 3's single-save mode against some 1.2 million failed runs (secondary).
- **Start small.** The session file, the note key, the camera replay and the sealed key go into 1g's first build. The first prototypes are the inquest, with the missed evening as its control, and the wager and the census ride on both as probes.

## 1. What this world gives a playtest

Most playtests can only ask players what they understood. This world can check, because every claim has an answer in the record.

1. *Exact replays.* The engine and the town are deterministic, and people's positions are functions of the day plan and the clock (`collision-and-navigation.md`). A session is its seed, its build, the player's commands and the camera's path, and replays frame for frame.
2. *A ground truth for every reading.* Each event has its causes with weights, its visibility and who saw it. "He stopped swimming because he was ill" can be scored: Andy Shaw's swimming "just lapsed" six years before the cancer (`docs/ideas/stories-in-the-world.md`).
3. *Counterfactual twins.* Understory's `clone.ts` copies a world exactly, and `whatif.ts` measures what one choice changes three years on. Run without the player's commands, the twin shows the player's footprint.
4. *The engine's readers as a yardstick.* On the same decisions, the engine's base rate is right 58.0 per cent of the time and a notebook of what the witness last saw 61.3. A calibrated witness reaches 64.6, and a mind-reader that sees everything 79.0 (Understory `docs/STATUS.md`). A tester's prediction lands on that ladder.
5. *Claims sorted by kind.* The five kinds of thing on screen (`CLAUDE.md`) sort every claim. A history read into texture is the cardinal failure, and a coder can count it.

The page is a strong rival. It shows each impression with its count ("seen 4 times, once the opposite"). Championship Manager carried its genre on radio-style text until a 2D match arrived in 2003 (secondary). The screen has to win on what the page can't do: recognising people, noticing absences, showing consequences in place.

Every playtest asks three questions, in this order. Is it a game: goals, challenge, stakes, mastery, failure and decisions that cost (`CLAUDE.md`)? Can they read it, against criteria 1 to 4? Do they want more, judged by what they do? A fourth runs across them: which game comes first (`docs/ideas/first-game-options.md`).

## 2. How the best find the fun

The studios that find fun fastest share four habits. Each prototype answers one question in a fixed time. The core is built and played first. A prototype that fails is killed, and the kill counts as a result. Players are watched, early and often.

| Who | What they do | What we take |
| --- | --- | --- |
| Experimental Gameplay Project (2005) | Under seven days, one person, one theme; four students made over 50 games in a semester. "Build the toy first"; cut losses. Jesper Juul's answer: a week tests a mechanic, and a game needs a second week for goals. | A time box and one question; judged as a game only once it has a goal, a stake and a way to fail. |
| Double Fine, Amnesia Fortnight | Two weeks, small teams, new ideas and new leaders; Costume Quest and Stacking came out of it (secondary). | A greybox fortnight, prototypes side by side. |
| Supercell | Games killed on metric thresholds after soft launch, marked with champagne. Ilkka Paananen: "Maybe we should just call them, like, experiments." | Kill lines written before the build. |
| Daniel Cook, Lostgarden | A log of dated play notes, each problem with a proposed fix; kill gates he calls critical and politically hard; a loop must stand once everything meaningless on replay is stripped. | The playtest log. |
| Valve, Half-Life 2 | About fifteen minutes of rough play, tested, sets next week's work; playtests settle arguments. They felt done when testing "was no longer painful to watch". | A weekly build and test. |
| Nintendo | Miyamoto watches a colleague play over the shoulder, with no questions and no talk, for where they get hooked and where bored (Iwata at GDC 2009, secondary). | Silence before questions. |
| Blockmesh practice | Naughty Dog goes straight to blockmesh with the final camera and controller (secondary). Firewatch skipped blockout because it couldn't test narrative pacing (secondary). | Greybox with the real camera, and name what clay can't test. |
| IO Interactive, Hitman | Players had fun, but the learning curve was far too steep; guidance came without changing the sandbox (secondary). | Test learning a dense place apart from playing it. |
| Mobius, Outer Wilds | A paper prototype with Alex Beachum "essentially DMing". Testers began writing notes, which argued for the ship log; clues packed too tightly overwhelmed them; the log's layout changed how they read what they'd found. | Watch what testers write; space the clues. |
| Bad News (2016) | One actor plays every resident of a simulated 1979 town while a hidden "wizard" queries the simulation; the wizard's logs later showed which questions cluster. | A wizard console before the interface. |
| The Sims; Dwarf Fortress | Wright's testers rebuilt their own families, then fantasies. Zach Adams writes stories and Tarn Adams builds an engine where they could happen. | Watch what players make it about; write the stories a session should produce. |
| RimWorld | Tynan Sylvester: what doesn't reach the player's model "is worthless". | Measure what reaches the mind. |
| Pentiment | A detective prototype was tried and cut (Sawyer). | A mystery can do without a culprit if the game has teeth. |

Two warnings. Lucas Pope found playtesting "wasn't very helpful" for a game of many characters and clues, and built tools that graph clues against people; a person with no links meant missing clues. And asking players outright about their experience misleads (section 4). The tools carry half the load.

## 3. How the best playtest

### Watch first

Valve treats designs as hypotheses and playtests as experiments: what players do outweighs what they say (Ambinder, GDC 2009). On Half-Life, outside players sat over 200 two-hour sessions while the level's designer watched in silence, allowed only to start or reset the game. Each session gave about a hundred action items, and the first twenty or thirty taught the team what was fun (Birdwell, 1999). Logs of deaths, fights and puzzles, graphed across sessions, found the stretches that were boring, too easy or too hard. Valve learned most from what players did not experience (GDC 2006).

### Fix fast, then check the fix

Microsoft's RITE method (Rapid Iterative Testing and Evaluation; Medlock and colleagues, 2002) fixes a problem once its cause and fix are both clear, sometimes after one participant, and checks the fix on the next. The team first agrees what every player must manage, with zero tolerance. On Age of Empires II's tutorial, 16 newcomers to strategy games found 31 problems, and 30 were fixed across six builds. The missing-wood problem was fixed after participant 1 and never returned. Six of 36 fixes needed a second fix. RITE finds common faults: seeing one that hits a player in a hundred, with 80 per cent confidence, takes about 161 participants (secondary).

### Who tests

Tracy Fullerton orders testers as yourself, confidants, then strangers (secondary, through course notes). Jesse Schell names the biases: developers are too close, friends want to like it, experts aren't typical, and one-time "tissue" testers, overused, give a strong opening and a dull middle. Every tester hears the same introduction, and Ubisoft's labs give the public the same message.

Friends inflate. In 450 interviews, people were about 2.5 times as likely to prefer an artefact they believed the interviewer had made, even an identical or worse one (Dell and colleagues, CHI 2012). Nielsen's five users find about 85 per cent of usability problems only if each problem hits 31 per cent of users; other studies found five catching from 35 per cent to nearly all (secondary). Five finds the common confusions and can't judge preference.

### How to hear what they think

Thinking aloud finds more usability problems (secondary), but disturbs play. Gow and colleagues (2010) let players play undisturbed, then talk over a replay of their own screen, with two prompts only: what were you doing here, what did you feel here. The Mom Test (Fitzpatrick; secondary) asks about specific past behaviour and treats compliments as worthless: "tell me about the moment you chose the loft", never "would you play this?".

### Understanding as well as fun

Steve Bromley tests a story at storyboard, greybox and final. After each beat: what is happening, why, what do you expect next. Never "is this clear?". Testers are screened and used once, and recall is checked again weeks later. Celia Hodent, who led user experience at Epic, frames testing round three limits. Perception is subjective: prior knowledge decides what is seen. Attention is scarce: a message during a fight is missed. Memory is fallible, so Fortnite shows ammunition on the gun, for recognition over recall. She warns that the curse of knowledge makes designers poor judges of their own clarity. The maker of the corner can't test whether its history reads.

### Numbers, and their limits

Telemetry tells what, never why, and averages hide extremes (Valve). Ubisoft's thirteen labs combine observation, heat maps and pathing, eye tracking, and a logger that attaches ten seconds of video to every flag of confusion (secondary). Far Cry Primal's beast riding came from those tests, because crossing the map on foot "simply wasn't fun" (secondary).

Questionnaires mislead more often than they help. In 633 players, the Game Experience Questionnaire's seven factors found no support (Law, Brühlmann and Mekler 2018; secondary). Valve prefers forced choice and ranking: rate each enemy's difficulty, rank the twelve weapons.

Bodies show arousal, not whether it is pleasant (Valve 2011), and skin conductance correlated weakly with survey answers (about 0.1 to 0.39). Eye tracking shows where the eye went: more than 40 per cent of changes were missed with the eye on the spot (O'Regan and colleagues 2000, in `time-on-screen.md`). Calm needs low arousal and a second channel, such as a word list.

### Breakers and weeks

Some testers exist to break the game. Magic: The Gathering's R&D plays the format a year ahead to find decks too strong; six months ahead proved too late to fix them (secondary). Mega Crit balanced Slay the Spire through Early Access from a metrics server and warned that metrics mislead if read carelessly (secondary). EA's reinforcement-learning agents found exploits and stuck spots (Bergdahl and colleagues 2020). Our own exploit is waiting: in a deterministic town, a player who reloads learns the future.

The wish to return needs real time. Player Research runs diaries of 20 to 40 players over weeks beside telemetry: the logs give the what, the diaries the why.

## 4. Testing a simulation's stories

### Found, then told

James Ryan argues that emergent stories succeed when someone curates and retells them (secondary, through Emily Short; his thesis would not open). "Story sifting" finds tellable chains in a log; "apophenia hacking" builds on what the simulation produced without contradicting it. In Kreminski's Diarytown, each recognised pattern becomes an object the player can inspect or delete "if they reject the interpretation". Ryan's Talk of the Town, nearest to our witness layer, gives characters beliefs that are observed, told, misremembered or lied about, and still knows the true path of each. Its authors admit "considerable authoring challenges" in getting that knowledge to the surface.

### Retellings as data

Kreminski and colleagues (AIIDE 2019) coded player retellings of Civilization VI and Stellaris, and of Prom Week with its social reasoning made random. Players default to a flat chronicle. Up to three reversals made a retelling compelling; the random Prom Week gave eight or more and read as incoherent. Stellaris's persistent named leaders drew far more "extrapolated flavor": story invented round details the game doesn't model. Asking players directly misled.

That codebook is our instrument. Every claim is coded against the record as a fact, a fair interpretation, flavour that claims no history, or a false history. The first three are the world working. So is a false belief the tester took from someone who lied or misremembered in the record (`behaviour-on-screen.md`, section 9). A false history drawn from the screen is the screen lying.

### A reading or a projection

People bind one vivid act to a face as character within seconds, lastingly, and a bad act most of all (`behaviour-on-screen.md`). The engine's Quiz II showed the page making a skilled reader worse that way. Three findings shape how we ask. Wording plants memories: after "smashed", 16 people recalled broken glass that wasn't there, against 7 after "hit" (Loftus and Palmer 1974; secondary), so probes say "the house", never "the neglected house". Explaining exposes: people rate their understanding lower after writing a step-by-step account (Rozenblit and Keil; secondary). And impressions sour when retold: people judging from someone else's account judge worse than the first-hand observer (Ames and Kammrath).

### Testing a mystery

The murder-mystery route (`docs/ideas/mysteries.md`, A death in the town; option 6 of `first-game-options.md`) brings its own lessons.
- *Commit before confirming.* Obra Dinn confirms fates in threes, since instant feedback in Papers, Please made guessing easy (Pope, in translation); players found a loophole, cycling the third (secondary). Golden Idol's testers hated "all right or all wrong", so it says when two or fewer blanks are wrong, and never checks blanks one by one, which would invite brute force (Klavins).
- *Cite the evidence.* Ace Attorney charges a penalty for each wrong piece of evidence presented (secondary). A claim with no evidence is a guess; a rumour cited as fact is a misread source.
- *Keep the truth fixed.* Paradise Killer: "There must always be an immutable truth to the game's fiction." Pentiment cut alibis, which rule people out, so motive rules them in (secondary).
- *Fair means solvable from what is shown.* Golden Idol's makers couldn't un-know their answers, so testers were their only measure. Cases ran first as spreadsheets, then with four or five friends each, watched in silence and asked afterwards. They hid a will that made a case trivial and avoided players stuck for half an hour on a technicality. Research generators of mysteries mostly skip checking that cases can be solved (Jaschek and colleagues 2019; Cook 2020). Models fail mysteries people solve (MuSR, 2024), so an agent failing proves little and an agent solving by guessing proves a lot.
- *Shape wears out before content.* Shadows of Doubt's closed alpha of 250 testers found the generated cases interesting, the tutorial overloading, objectives unclear and the end of a case too thin (devlog 25). Reviewers later found cases samey once the pattern was learned: every killer a serial killer, the same form to close (secondary).
- *Labels must match intent.* L.A. Noire's choices didn't say what players meant to do (secondary). A reading game can fail at the button.

## 5. What reactive worlds teach

Role-playing games with deep reactivity share our problem: every player's world differs, and consequences land late.

- *Larian, Baldur's Gate 3.* Swen Vincke calls analytics a "gold mine": choices taken too often or too rarely, paths through dialogue (secondary report quoting him). Complaints about streaks of bad rolls led to a "Loaded Die". Larian published where players died and whom they killed; the wizard Gale died over 333,000 times in the first days (secondary). The team checked such logs against player reports and its testers before fixing. In Divinity: Original Sin they tried "system A in one week and system B in the next week". The ending's choices fill a spreadsheet that "takes a small army" to check (Chrystal Ding), and automated checks reject a change that breaks the game.
- *CD Projekt Red, The Witcher 3.* Kaer Morhen's battle has 9 to 16 allies in any combination, every one to work; it "turned out to be even worse than we expected" (Paweł Sasko).
- *Interplay, Fallout.* Tim Cain taught the team with small tabletop dungeons; every group had a different game, and the difference came from the players (secondary).
- *Ice-Pick Lodge, Pathologic 2.* Meant to be "grueling, stressful, and bleak". The studio shipped one route first to watch players and tune the others. Later it added sliders both ways, behind switching off "Intended Difficulty" (secondary).
- *Atlus, Persona 4.* Late in the year the calendar shows a month instead of days, so players feel their free days running out (Hashino, in translation).
- *Ultima VII and Kingdom Come.* "Yes, they all had schedules" (Raymond Benson). A home, work and tavern cycle carries most of the belief (secondary). Kingdom Come's people change routine after violence or theft (secondary).
- *Limits by choice.* Stardew Valley's Eric Barone dropped affairs because the whole town would hate the player (secondary). Toshihiro Nagoshi: repeating "similar experiences" is not modern.

For our tests: log which acts players try and which options nobody finds, and show the same failure map after each fix. Give two systems to the same testers in turn. Test one route deeply before widening. Since our consequences come from a simulation, the combinations can run headless: every act, across many seeds, must end in something the screen can show.

## 6. Agents as playtesters

Agents already test games for coverage: EA's reinforcement-learning agents reached every corner of a map and found exploits and stuck spots (Bergdahl and colleagues 2020). Language models play worse than people but rank difficulty like them. GPT-4 tracked human difficulty in Wordle (r = 0.62) and Slay the Spire's first bosses (0.87); an optimal solver didn't (0.08) (Xiao and Yang 2024). Agents playing from the screen remain poor; the best finished under one per cent of VideoGameBench (2025).

As stand-ins for people they fail in known ways. They portray groups as outsiders imagine them and flatten the spread of answers (Wang, Morgenstern and Dickerson 2025). Nielsen Norman Group's synthetic users claimed to finish every course, where real users finished three of seven. Assistants flatter (Sharma and colleagues 2023). Understory's `WHY.md`: a synthetic person "is not evidence of how real people will behave".

We use agents already: model readers as cold readers (`docs/foundations.md`), and the paper playtests running now with a game-master agent and five player agents (`docs/playtests/paper-1/method.md`).

| Agents can find first | Only people can show |
| --- | --- |
| Facts the camera can't reach or never shows | Fun, and where it drags over real hours |
| Replays that drift | Calm, boredom, delight |
| Hover and inspect targets that never answer | Misreadings from human priors and stereotypes |
| Facts ambiguous in principle: if a model with the evidence can't get it, a person won't | A face known again after a jump |
| Which of two scenes is harder to read | Whether the scene beats the page |
| Exploits: reloading for foreknowledge, asking everyone everything | The wish to come back |
| Whether probes, key and scorer run end to end | How a group talks itself into a reading |

Agents go first in every round. Their findings are hypotheses for people, never reported as player findings.

## 7. The programme

Six phases, from agents to strangers. A phase starts when the one before stops finding the same faults, and a prototype can be killed at any phase.

| Phase | Who | What it asks | Size |
| --- | --- | --- | --- |
| 0. Agents | model players, model readers, a coverage bot | Does it break? Is every fact reachable and readable in principle? | every build |
| 1. Øystein | Øystein; Claude reads the logs | Is it a game? Does the core decision bite? Feel, camera, taste | 30 to 45 minutes, weekly |
| 2. Confidants | three to five people Øystein invites | Can newcomers move, inspect, decide and reach the stakes? | three to five sessions a round |
| 3. Strangers | five per question, friends of friends, once per seed | First reading, misreadings, whether reading pays, mastery | 60 minutes |
| 4. Against the page | a pilot of three, then 20 to 40 strangers | Criterion 4, with 1 to 3 inside it | 40 minutes |
| 5. Across weeks | five to eight, with a build of two chapters | Do they come back? Do they know people after real days? | one to three weeks |

A seventh comes after a first game is chosen: an open test at scale, as Larian ran Early Access (section 10, the daily street).

Phase 0. A coverage bot sweeps every reachable camera pose and logs which records were ever on screen, and at what size; a history no pose shows is a fault. Model players drive the greybox through a text interface (look, inspect, ask, wait, jump, act) with a person's goal card, in the paper playtests' five kinds. One plays as an optimiser and tries every exploit, reloading first. Model readers take the probes, flagging facts no reader gets from the evidence. The output is faults and a ranking of scenes, never a verdict on fun.

Phase 1. Øystein knows the docs, so the curse of knowledge rules him out as a reader of history. He tests the game: is there a goal he cares about, a decision that costs, a way to fail, a skill he feels growing? He judges feel and taste, and may think aloud. Each session ends with ten minutes over the replay at three moments Claude picks from the logs, and his challenge card (section 11). Once per prototype he plays to break it, trying to win without reading.

Phase 2. Friends' preferences don't count; what they do does. Before the round, a zero-tolerance list in RITE's manner. For the corner: reach three named places in under a minute each, and open a card. Say what the goal is and how you could lose. Tell "you saw" from "Ruth said". Deliberate over at least one decision. A failure with a clear cause and quick fix is fixed before the next session and checked on the next player; one without a clear cause waits for data. Sessions can be remote. The build sends nothing; the tester returns the session file, as the engine's study page does.

Phase 3. The first readings that count. Testers are screened (not in games, not friends, haven't seen the town) and used once per seed. Each plays two cases of matched difficulty on different seeds, so the second shows the mastery curve. No thinking aloud, which disturbs calm looking.

Phase 4. The engine's own study protocol (Understory `docs/study.md`) and the cold readers' test (`behaviour-on-screen.md`, section 9). Each tester meets twelve chains: six as the playable scene, six as the engine's page with its counts, time-matched. Half start with scenes, no tester sees a chain both ways, and across testers each chain appears in both arms. Prediction items show the base rate in both arms; every answer has a confidence. Pack, key and analysis script are committed before the first tester, exclusions fixed in advance. Model readers take the pack first; where people and models disagree, people win. The bars are set in `behaviour-on-screen.md`: scenes find more second-order consequences, stay within five points on facts, mislead no more often, and over-read character less.

Phase 5. Testers keep a two-chapter build. After each session, a diary line: what happened, what you expect, whom you'd look for next. Recognition is tested after real days. The measure that matters is whether they open the build again unasked.

### The session

Every human session from phase 2 runs the same script, about an hour.

1. Logged before play: the seed, the build's hash, the engine's tag, the sealed key's hash, the probes.
2. The introduction, word for word: we're testing the game, not you; stop when you like; I won't help.
3. Warm-up, three minutes: go to three named places. It measures the camera.
4. The goal card: what you're after, what you have, how you can lose.
5. Play, 25 to 35 minutes, in silence. Stuck on the controls for three minutes, the tester hears one scripted line, and the log records it.
6. Probes at each chapter break: predict, commit readings, give confidence.
7. Retelling, five minutes: "What happened here? Step by step." Then: "How sure are you of each part?"
8. Commentary over the replay, ten minutes, at the longest look, the longest deliberation and the first probe answer the key marks wrong. Two prompts only.
9. Debrief, ten minutes. What were you trying to do? Tell me about the hardest decision: what did you give up? A moment you'd take back? Where did you nearly stop? What did you want to do and couldn't? Pick one person: what do you know about them, and how? This game in one sentence, for a friend? Never: did you like it, was it fun, was it clear.
10. The offer: "There's another case. Would you like to play it now?" Saying no costs nothing, and the answer is recorded.

### How Claude analyses a session

1. A script turns the session file into the session report (section 8).
2. Speech is transcribed on the machine.
3. Claims are pulled from the retelling, notes, probes and transcript. A fresh coder agent, on another model than the prototype's builder, codes each against the sealed key without knowing the arm.
4. A script scores the pre-registered measures before anyone looks again.
5. Claude writes findings, each with replay timestamps, the evidence against it, a RITE category (fix now, fix slowly, more data, maybe an artefact) and what would change our minds.
6. Findings enter the hypothesis register; at milestones Fable reviews the synthesis against the replays.

## 8. The tools the greybox needs

Most come cheap: positions are functions of plan and clock, and every drawn pixel will answer "which record?" (`collision-and-navigation.md`, `interface-and-inspection.md`).

| Tool | What it does | Cost (our days) |
| --- | --- | --- |
| The note key | One key freezes the frame and saves a screenshot at the player's size with the state: seed, build, engine tag, in-world date and hour, wall clock, camera pose and stop, the record under the cursor and every record in view, the open card, the knowledge store's hash, the replay frame. A number key tags it (confused, aha, bug, I want to); a typed or spoken line is optional. The ten seconds before are attached, as in Ubisoft's logger. World time pauses. | 1 |
| The exact replay | The session file holds seed, versions, fixture hashes, every input and command by frame, and the camera's pose every frame (poses as well as inputs, since floating point can differ between builds; Fiedler). People are recomputed from plan and clock. A hash of camera, knowledge store and record each second catches drift, as Factorio checks every tick. The viewer scrubs, shows other testers' paths on the seed as ghosts, replays a path with the history layers off (what there was to see), and outlines the key's facts for the maker only. | 2 to 3 |
| Telemetry | Camera pose and stop ten times a second; twice a second a small id render of the whole frame, giving each record's share of the screen; every hover with its dwell, every card, why, comparison, note, command, jump and probe. From these: attention on facts (screen time on records in the history budget), facts never seen, a path map, time at each stop. The id render is costed on the M4 first. | 1 to 2 |
| Probes | Cards at chapter breaks: predict, mark parts old, changed or neglected, same or different person, each with a confidence; grouped confirmation where the prototype confirms. | 1 |
| The sealed key | From the record: facts on show per view and chapter, chains, traps (false joins, quirks, vivid acts with situational causes), and prediction items with the engine readers' answers. Hashed before play. Grows from `time_key.py`. | 1 |
| The twin | The world run again without the player's commands; the change query between the two is the footprint. Fixture pairs until the engine runs beside the build with its first command (#22). | an engine request |
| The session report | One page: a summary paragraph for Øystein, a timeline of notes and decisions, the path map and attention on facts, the key's facts seen, inspected and claimed, coded claims with confidence, time to the first reading, predictions beside the base rate and the calibrated witness, deliberation times, the footprint, the offer, three moments for commentary, and how the tester compares with others on the seed. | 2 |
| The wizard console | For prototypes ahead of their systems: a hidden operator (Claude in a side session, or Øystein) answers "ask" and "why" from the record by hand, and every query is logged, as in Bad News. The clusters design the interface. | half |

Testers are numbers in the files, never names. Audio is transcribed on the machine and deleted after coding unless the tester agrees otherwise, and any tester can withdraw their file.

## 9. What to measure

Game-ness first, by the standing rule. Bars are set where research gives one; elsewhere the first round is the baseline.

| Is it a game? | How | Why |
| --- | --- | --- |
| Goal understood | "What were you trying to do?", coded against the goal card | Four in five, or the test isn't ready |
| Decisions that cost | Deliberation well above the tester's median, named unprompted as a trade-off | Sid Meier's game as "a series of interesting decisions" (secondary) |
| Split choices | How a decision divides across testers on one seed | Telltale rewrote what followed when one option looked "right" (secondary) |
| Stakes felt | Requests to undo; "I'd take that back"; hesitation before committing | Without risk, acts become a treadmill (Bartle; secondary) |
| Failure that teaches | After a loss: can they say why, is it right, whom do they blame? | Juul: fail-then-succeed rates highest; blaming the game rates lower |
| Mastery | Case two minus case one on matched seeds; reading skills used, used right, dropped | Cook's skill atoms and "burnout" |
| Reading pays | Correlation of reading score and outcome | If good readers don't win more, reading is decoration |
| Agency | The footprint, and whether the tester can name a change they caused, rightly | "My decision changed what happened" (`game-layer-ideas.md`) |
| Loops at three scales | Time per action, thread and question; does the middle loop vary? | Griesemer: Halo's "30 seconds of fun" meant a loop whose context never repeats |

| Can they read it? | How | Bar |
| --- | --- | --- |
| Criterion 1 | Parts marked old, changed, neglected; histories found; pairs ordered | `docs/foundations.md` |
| Criterion 2 | Same or different person across years, lookalikes mixed in; hits, false alarms, confidence | first round sets it |
| Criterion 3 | Second-order consequences named | more than the page |
| Criterion 4 | Phase 4 | `behaviour-on-screen.md` |
| Time to the first reading | Minutes to the first claim coded fact or fair interpretation beyond what hover names | falls each round, without more hand-holding |
| Misreadings | False histories per session; wrong answers held "sure"; trait as cause where the record names the situation; false joins taken (Grace Shaw's boat and the till) | none held "sure" |
| Better than the base rate | Predictions beside the engine's base rate, notebook and calibrated witness | above the base rate; the witness is the rival |
| Aha | Notes tagged "aha", checked against the key; reversals in retellings | three at most per retelling |

Wanting more is judged by behaviour: the offer taken, minutes played past the end, the build reopened unasked, the town retold to someone else. Fun likewise, then by ranking prototypes against each other, never by a lone fun scale. Calm attention counts inside the game: voluntary dwell at vantages, two restorativeness items ("being away", "fascination"; secondary, with mixed results) and a word list. Threats kept outside a cozy space deepen it, like rain on a window (Project Horseshoe; secondary). A calm street with a case on it is the aim.

## 10. Worth trying

Each is a mechanic inside a game with stakes. The brief's seeds are all here. The return after years becomes the wager's payout and the chosen jump. Shadowing, the photograph, asking why, the rumour, the nudge, the band, the club, the house, the detective and the remembering town each have a row. Costs are our days beyond the greybox's base.

| Prototype | Why it might be great | Cost | Keep if | Kill if |
| --- | --- | --- | --- | --- |
| The inquest (option 6) | A death at the foot of the steps; three days, three questions a day, each heard of by others; an account that cites its evidence, scored in groups. Misreading harms someone the engine remembers. Runs on today's engine. Try both endings: the truth shown, or your verdict stands. | 3 to 4 | case two beats case one; better readers win; testers take the next case | mostly looking, or the natural death feels a cheat in both endings |
| The wager | Before each jump, stake a small budget on what lives will do: who stays, which shop closes, whether the band lasts. The jump pays out; the calibrated witness bets against you. | 1 | bets beat the base rate, and testers agonise | bets fall to the base rate, or it feels like a quiz |
| The missed evening | Two things at once; you can be at one, and the other reaches you only as accounts. | 1 | testers deliberate, then act on what they missed | random choice, or the missed one never matters |
| Shadowing | Learn a routine to catch someone alone at the right moment, with a summons or an invitation. A broken routine is news. | 2 | after three evenings, the right moment unaided, and the break noticed | the interface must tell them |
| A roll of film | Twenty-four exposures for the case, in 1989. Photographs are evidence to cite or print, and held up in place years later. | 1 to 2 | shots chosen with care; an old photo settles a later question | souvenirs, never used |
| Asking costs | Every question is an act others hear of; trust spent doesn't return; answers only from sources, "?" where none; the people asked, helped or blamed act on it next chapter. Wizard console first. | 1 | questions rationed, chosen from what testers saw | asking everyone everything still wins |
| The paper against the eye | The Courier prints an account that contradicts what you saw: correct it, print your own, or let it stand. | 1 | eye and print weighed rightly; the cost of contradicting the paper felt | the print trusted over their own view, or never noticed |
| The favour and its twin | Three favours a chapter: a loan, an introduction, a word put in. After the jump, the twin shows the town without them, aligned in place. | 2 | testers name what their favour did, rightly | the footprint is invisible: then it goes to the engine bundle, since four in five weighty events lead to nothing traceable (Understory `STATUS.md`) |
| The band's first command | Invite a musician to the loft for the month's rent and a promise; accepted or refused with a reason; read the trace a week on. | 1 | a refusal reads as a person deciding | it reads as a dice roll |
| The club's scout | Three evenings among the town's lads: whom to sign, given shifts, families and drink. Saturday decides. | 2 | town-readers pick the better side | a table of numbers does as well |
| The inherited house | Price the works on house D from its traces; a misreading costs money; the bill comes in 1995. | 2 | readers of traces profit | it plays as decorating |
| Choosing the jump | The player sets each jump: a month, a year, five. Longer pays more bets and shows more change, while evidence decays and witnesses move. | 1 | jump length becomes a decision testers argue over | everyone picks the same |
| A human culprit | Before the engine has crime, Øystein or a second tester plays a resident with a secret within the record's rules: lies, removes a trace, leaves town. | 1 | a living opponent makes a contest, and the evidence backs the bundle's crime request | it plays like a natural death |
| Telephone | Tester A watches a scene and writes a note; B acts on it; C on B's. | none | drift is measurable and makes good play | no drift |
| The census | Name who lived in each house in 1989 from routines and traces, confirmed in threes: criteria 1 and 2 as a puzzle. | 1 to 2 | fast, fair, fresh across seeds | solved by elimination without looking |
| The daily street | One seed a day for everyone, one question, a score to compare; determinism makes a shared town, and testing at scale. | later | people come back for tomorrow's | answers spread online within the hour |

Try the inquest first, with the missed evening as its control, as `first-game-options.md` proposes. The wager and the census ride on any prototype as probes.

## 11. How Øystein and his testers pick it apart

### The challenge card

After every session, the tester and Øystein each fill in one card in under five minutes. Each line points at a moment in the replay.
- A moment that worked, and one that didn't.
- One belief about a person or a place, with its evidence.
- One decision you'd take back.
- One thing to cut, one to add.
- One bet: what the next tester will do, or what will happen to someone in the town.

Bets are checked, and checked bets show whose judgement to trust on what.

### Disagreements become hypotheses

When Øystein and a tester disagree, or two testers, or Claude and Øystein, the disagreement is written as a hypothesis with each side's prediction. The next round is built so the predictions differ. A register in `docs/playtests/` holds each: the claim, who holds it, the test, the measure, the line to keep or kill, the status, the evidence. Claude's findings go in it too, with the evidence against them.

Once per prototype, someone plays to break it: to win without reading, or to find a reading the screen forces that the record doesn't hold. A break is a result.

### How results move the plan

Every prototype has its kill line and time box before it is built. After phase 2, two or three prototypes go on; after phase 3, one leads, which feeds Øystein's choice of the first game. Phase 4 gives criterion 4 its first verdict. Engine needs found in play join the bundle for Understory with their evidence (`docs/engine-requests.md`). What we keep and drop goes in `docs/experiments.md`, and the plan and the ideas pages follow.

## What we should do

Ranked by what each buys for its cost, in our working days.

1. The session file, the note key and the camera replay, in 1g's first build (3 to 4). Every later test rests on them, and bug reports reproduce exactly.
2. The sealed key, coder and scorer, grown from `time_key.py` and the cold readers' method (1 to 2). Misreading becomes a number, scored as pre-registered.
3. Telemetry with the id render, and the session report (3). Attention on facts, and a report Øystein reads in a minute.
4. Phase 0's harness: a text interface for model players and the coverage sweep (2). A first pass before anyone's time is spent.
5. The inquest against the missed evening, with the wager and the census as probes (5 to 6). The first test of game and reading together, and the sharpest split between the options.
6. Øystein's weekly sessions with challenge cards and the register (his time; half a day of ours a week). A game that bites before strangers see it.
7. Confidants with their zero-tolerance list, then strangers once each (a week or two elapsed). Mastery curves and the first honest readings.
8. The blind test against the page once real chains exist (2, plus recruiting). Criterion 4.
9. A twin run, with and without the player's commands through the front door, added to the bundle for Understory (an hour). Agency as a number.
10. The wizard console for any prototype ahead of its systems (half). An interface designed from real questions.

## For Øystein to decide

1. *Who moderates.* Recommended: Øystein for his own sessions and the confidants; a neutral friend, reading Claude's script, for strangers. **Decided (Øystein, 21 October), as recommended.**
2. *Reloading in tests.* Recommended: none. Sessions play forward from their seed, since a reload in a deterministic town teaches the future.
3. *The record after a case.* Recommended: shown after scoring, marked as the record, never during play.
4. *Recruiting without a budget.* Recommended: friends of friends, thanked with credit in the game. **Decided (Øystein, 21 October), as recommended.**
5. *Recording voices.* Recommended: with consent only, transcribed on the machine, deleted after coding. **Decided (Øystein, 21 October), as recommended.**
6. *The first prototypes.* Recommended: the inquest, with the missed evening as its control.

## Gaps

- The shared search budget ran out before Blizzard's, Insomniac's and Riot's user research, Planescape: Torment, Josh Sawyer's testing of reactivity and Larian's own Early Access posts; Baldur's Gate 3's numbers come from reports of those posts.
- GDC Vault was down: the Hitman, Outer Wilds, Kingdom Come, Sid Meier, Deborah Hendersen and Naughty Dog talks are known from abstracts and reports.
- Fullerton's chapter, Hodent's book and Ryan's thesis were read through notes or summaries; Miyamoto's silent sessions through a report of Iwata's talk.
- The id render's cost on the M4 is unmeasured.
- Model players driving the greybox through text are untested; phase 0 must first measure how much of what people find they find.
- Calm attention has no validated measure in games.
- Phase 4's size is set by its pilot, as in the engine's study.

## Sources

Finding the fun: [Gabler and colleagues, How to Prototype a Game in Under 7 Days](https://www.gamedeveloper.com/game-platforms/how-to-prototype-a-game-in-under-7-days) · [Juul on the same](https://www.jesperjuul.net/ludologist/2005/10/29/how-to-prototype-a-game-in-under-7-days/) · [Double Fine, Amnesia Fortnight 2014](https://www.doublefine.com/news/amnesia-fortnight-2014-a-double-fine-production) · [Paananen, Sequoia podcast](https://www.sequoiacap.com/podcast/supercell-ft-ilkka-paananen-how-an-early-pivot-led-to-clash-of-clans-and-brawl-stars) · [Paananen's BAFTA lecture, PocketGamer.biz](http://www.pocketgamer.biz/5-lessons-from-ilkka-paananens-bafta-games-lecture/) · [Cook, Game Design Logs](https://lostgarden.com/2011/05/03/game-design-logs/) · [Cook, Rockets, Cars and Gardens](https://lostgarden.com/2007/02/19/rockets-cars-and-gardens-visualizing-waterfall-agile-and-stage-gate/) · [Cook, Loops and Arcs](https://lostgarden.com/2012/04/30/loops-and-arcs) · [Cook, The Chemistry of Game Design](https://www.gamedeveloper.com/design/the-chemistry-of-game-design) · [Valve, Half-Life 2 design process, GDC 2006](https://cdn.fastly.steamstatic.com/apps/valve/2006/GDC2006_HL2DesignProcess.pdf) · [Iwata at GDC 2009, MCV](https://mcvuk.com/?p=140722) · [The Level Design Book, blockout](https://book.leveldesignbook.com/process/blockout) · [Naughty Dog at GDC 2018](https://www.naughtydog.com/blog/naughty_dog_at_gdc_2018) · [Mobius, Demaking Outer Wilds](https://www.mobiusdigitalgames.com/news/demaking-outer-wilds) · [Mobius, October 2017](https://www.mobiusdigitalgames.com/news/archives/10-2017) · [Mobius, Planet progress](https://www.mobiusdigitalgames.com/news/planet-progress) · [Wright, Salon 2000](https://www.salon.com/2000/02/17/wright_5) · [Tarn Adams Q&A](https://www.gamedeveloper.com/design/q-a-dissecting-the-development-of-i-dwarf-fortress-i-with-creator-tarn-adams) · [Sylvester, The Simulation Dream](https://www.gamedeveloper.com/design/the-simulation-dream) · [The ingredient that turned Football Manager into a hit](https://www.gamedeveloper.com/design/the-ingredient-that-turned-i-football-manager-i-into-a-massive-hit) · [Sawyer on Pentiment, TheGamer](https://www.thegamer.com/interview-obsidian-josh-sawyer-pentiment/) · Hitman at GDC Europe 2016 (session abstract only).

Playtesting: [Ambinder, Valve's Approach to Playtesting, GDC 2009](https://cdn.fastly.steamstatic.com/apps/valve/2009/GDC2009_ValvesApproachToPlaytesting.pdf) · [Ambinder, Biofeedback in Gameplay, 2011](https://cdn.cloudflare.steamstatic.com/apps/valve/2011/ValveBiofeedback-Ambinder.pdf) · [Birdwell, The Cabal](https://www.gamedeveloper.com/design/the-cabal-valve-s-design-process-for-creating-i-half-life-i-) · [Medlock and colleagues, the RITE method](https://www.jpattonassociates.com/wp-content/uploads/2015/04/rite_method.pdf) · [MeasuringU on RITE](https://measuringu.com/?p=584) · [Schell, Playtesting 101](https://stewart.sdsu.edu/cs583_spr2013/LearningXNA4_lects/JesseSchell_playtesting101.pdf) · [TUM lecture notes on Fullerton's protocol](https://www.cs.cit.tum.de/fileadmin/w00cfj/cg/Teaching/SS22/ComputerGamesLaboratory/lecture03_playtesting.pdf) · [Ubisoft Montreal's playtest](https://montreal.ubisoft.com/en/ubisoft-montreals-playtest-how-does-it-work-and-how-to-participate/) · [Far Cry Primal's beast riding, Game Informer](https://gameinformer.com/b/news/archive/2016/03/15/far-cry-primals-beast-riding-was-added-late-in-development-because-of-ubisofts-user-research-group) · [Hodent, Developing UX Practices at Epic Games](https://celiahodent.com/ux-practices-epic-games/) · [Dell and colleagues, "Yours is better!"](https://www.microsoft.com/en-us/research/?p=162695) · [Nielsen, five users](https://www.nngroup.com/articles/why-you-only-need-to-test-with-5-users/) · [Gow and colleagues, post-game commentaries](https://www-users.york.ac.uk/~pc530/pubs/Gow_cgat2010.pdf) · [The Mom Test](https://www.momtestbook.com/) · [Bromley, How to playtest your game's story](https://gamesuserresearch.com/how-to-playtest-your-games-story/) · [Law, Brühlmann and Mekler on the GEQ](https://researcher.itu.dk/en/publications/systematic-review-and-validation-of-the-game-experience-questionn/) · [Player Research, diaries and data](https://www.gamedeveloper.com/design/better-games-from-diaries-and-data) · [Short, Designing for coziness](https://www.gamedeveloper.com/design/designing-for-coziness) · [Fiedler, Deterministic Lockstep](https://gafferongames.com/post/deterministic_lockstep/) · [Factorio, FFF 47](https://factorio.com/blog/post/fff-47) · [Magic's Future Future League, MTG Wiki](https://mtg.wiki/page/FFL) · [Slay the Spire's metrics-driven balance, GDC preview](https://gdconf.com/news/learn-slay-spires-successful-metrics-driven-approach-game-balancing-gdc-2019) · [Juul, Fear of Failing?](https://jesperjuul.net/text/fearoffailing/) · [Griesemer on Halo's thirty seconds, Engadget](https://www.engadget.com/2011-07-14-half-minute-halo-an-interview-with-jaime-griesemer.html) · [Sid Meier's interesting decisions, Game Developer](https://gamedeveloper.com/design/video-sid-meier-explores-interesting-decisions-in-gameplay) · [The Walking Dead's choices, Wikipedia](https://en.wikipedia.org/wiki/The_Walking_Dead_(video_game)) · [Permadeath, Wikipedia](https://en.wikipedia.org/wiki/Permadeath).

Stories and mysteries: [Ryan and colleagues, Talk of the Town](https://cdn.aaai.org/ojs/12825/12825-52-16341-1-2-20201228.pdf) · [Emily Short on Ryan's thesis](https://emshort.blog/2019/05/23/curating-simulated-storyworlds-james-ryan-2/) · [Kreminski and colleagues, Felt](https://mkremins.github.io/publications/Felt_SimpleStorySifter.pdf) · [Kreminski and colleagues, Evaluating AI-Based Games through Retellings](https://cdn.aaai.org/ojs/5223/5223-52-8321-1-10-20190920.pdf) · [Ames and Kammrath, secondhand impressions](https://business.columbia.edu/sites/default/files-efs/pubfiles/1117/ames_kammrath_secondhand.pdf) · [Pope, Automaton interview](https://automaton-media.com/articles/interviewsjp/20190719-97599/2/) · [Golden Idol's testing, Road to the IGF](https://www.gamedeveloper.com/road-to-igf-2023/-the-case-of-the-golden-idol-i-used-frequent-testing-to-improve-its-mystery-solving) · [Klavins on Golden Idol](https://www.gamedeveloper.com/design/case-of-the-golden-idol) · [Paradise Killer, VICE](https://vice.com/en/article/akdzvp/ritual-sacrifice-and-punk-skeletons-the-story-behind-paradise-killer) · [Pentiment's lack of an answer, Shacknews](https://www.shacknews.com/article/146276/pentiment-josh-sawyer-no-correct-answer) · [Shadows of Doubt devlog 25](https://colepowered.itch.io/shadows/devlog/267393/shadows-of-doubt-devblog-25-closed-alpha-conclusions) · [Shadows of Doubt devlog 30](https://colepowered.itch.io/shadows/devlog/354045/shadows-of-doubt-devblog-30-the-top-shadows-of-doubt-development-challenges-part-i) · [Jaschek and colleagues, Mysterious Murder](https://ieee-cog.org/2019/papers/paper_45.pdf) · [Cook, Generative Forensics](https://arxiv.org/abs/2004.01768) · [MuSR](https://arxiv.org/abs/2310.16049) · [L.A. Noire, Wikipedia](https://en.wikipedia.org/wiki/L.A._Noire) · [Ace Attorney, Wikipedia](https://en.wikipedia.org/wiki/Phoenix_Wright:_Ace_Attorney).

Reactive worlds: [Vincke, Destructoid](https://www.destructoid.com/larian-founder-swen-vincke-on-dice-druids-and-baldurs-gate-3/) · [Larian at the BAFTA evening](https://malaysia.news.yahoo.com/larian-gave-baldurs-gate-3-022539159.html) · [Early Access statistics, CGM](https://cogconnected.com/2020/10/baldurs-gate-iii-releases-deadly-fun-statistics/) · [Larian's launch learnings, Impulse Gamer](https://www.impulsegamer.com/larian-studios-shares-early-insights-into-baldurs-gate-3s-launch-learnings/) · [Vincke on QA, Yahoo](https://tech.yahoo.com/general/articles/swen-vincke-says-baldurs-gate-161420738.html) · [Larian on Original Sin's Early Access, GameBanshee](http://www.gamebanshee.com/kdp84) · [Larian on competing camps, GameBanshee](https://www.gamebanshee.com/3hrxw) · [Honour Mode statistics, Game World Observer](https://gameworldobserver.com/?p=16673) · [Witcher 3 quest designers, Shacknews](https://www.shacknews.com/article/94509/witcher-3-quest-designers-talk-design-process-most-difficult-quest-to-create) · [Kaer Morhen, Kotaku](https://kotaku.com/the-witcher-3s-big-battle-sounded-like-a-nightmare-to-m-1774809802) · [Kingdom Come 2's routines, Wccftech](https://wccftech.com/kingdom-come-deliverance-2-dev-talks-about-dynamic-npc-routines-and-emergent-storytelling-for-side-quests/amp/) · [Pathologic 2's sliders, Game Informer](https://www.gameinformer.com/2019/06/07/pathologic-2s-new-update-invites-you-to-adjust-your-level-of-suffering) · [Behind the design of Persona 4, Siliconera](https://www.siliconera.com/behind-the-design-of-persona-4/) · [Benson on Ultima VII, GameBanshee](http://www.gamebanshee.com/xhrr) · [Ultima NPC schedules, Ultima Codex](https://lycaeum.ultimacodex.com/npc-schedules/) · [Barone, Road to the IGF](https://gamedeveloper.com/design/road-to-the-igf-concernedape-s-i-stardew-valley-i-) · [Nagoshi, VGC](https://videogameschronicle.com/news/yakuza-creator-nagoshi-says-the-era-of-game-size-being-most-important-is-coming-to-an-end).

Agents: [Bergdahl and colleagues, deep RL for game testing](https://arxiv.org/abs/2103.15819) · [LLM difficulty prediction](https://arxiv.org/html/2410.02829v1) · [VideoGameBench](https://arxiv.org/abs/2505.18134) · [Wang, Morgenstern and Dickerson](https://arxiv.org/html/2402.01908v3) · [Nielsen Norman Group, synthetic users](https://www.nngroup.com/articles/synthetic-users/) · [Sharma and colleagues, sycophancy](https://arxiv.org/abs/2310.13548).

Understory, read through the GitHub API, read-only, on 21 October: `WHY.md`, `README.md`, `docs/STATUS.md`, `docs/study.md`, `docs/method/reading.md`. Ours: `CLAUDE.md`, `NOW.md`, `docs/plan.md`, `docs/living-world.md`, `docs/facts-contract.md`, `docs/engine-requests.md`, `docs/foundations.md`, `docs/measuring.md`, `docs/playtests/paper-1/method.md`, `docs/ideas/` (all), and in `docs/research/`: `interface-and-inspection.md`, `time-on-screen.md`, `behaviour-on-screen.md`, `history-in-things.md`, `camera-and-composition.md`, `collision-and-navigation.md`, `pre-mortem.md`. `play-craft.md` did not exist yet.
