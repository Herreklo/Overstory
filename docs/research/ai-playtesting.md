# AI playtesting

Research, 22 October 2026, on Opus 5.5. It gathers what the field knows about agents as playtesters. The aim is sound method for the paper playtests (`docs/playtests/paper-1/method.md`), the cold readers (`docs/foundations.md`) and the agents who play the greybox first (plan step 1g). It feeds `docs/research/playtesting.md`.

Claims read in the authors' full text are unmarked. Claims from abstracts, search summaries, reporters or vendors are marked (secondary); claims we could not confirm are marked (unverified). One helper gathered the game-playing agents and the industry practice. Each page was fetched once.

## The bottom line

- Agents are good at finding where a game breaks, stalls or hides what the player needs. They are weak judges of fun, and their raw scores drift towards the middle or towards praise.
- Agents rank difficulty much as people do, even when they play worse. Use them to order things, never to set levels. Their best runs predict people better than their average runs.
- Personas move behaviour less than we hope, fade over long sessions and flatten the groups they stand for. A persona shows what someone with that goal would try, not what that kind of player would feel.
- Two Anthropic models are not two independent opinions. Models share errors, and models from one maker share more.
- The game master is a model, and models are poor world simulators over long runs. Its slips look like design flaws unless they are audited.
- Agents play far better from structured state than from pixels. Pixels belong where the question is about pixels: can a reader see the history?
- Our world has what most studies lack, a ground truth. Predictions scored against the engine are our most trustworthy measure and should lead.
- A few humans, used well, make the agents' numbers usable: same material, rank agreement, chance-corrected statistics, and a log of where agents misled us.

## 1. The academic record

### Personas and generative player models

Holmgård, Green, Liapis and Togelius built "procedural personas" for MiniDungeons 2 (IEEE Transactions on Games, 2019). Each persona is a utility function. The Runner values reaching the exit in few steps. The Monster Killer weights kills at 0.7 and the Treasure Collector treasure; the Completionist values everything it can use. Monte Carlo tree search (MCTS) plays each, with its selection formula evolved per persona. The personas ran in seconds, fast enough for a design loop.

They were checked against the designers' intentions, never against human players; that was left as future work. And the Completionist avoided treasure and did worse than the Treasure Collector, which the authors traced to its own weights. When a persona acts oddly, check the persona before the game.

Later work widened the idea. Personas whose goals change during play told designers more than fixed ones (Ariyurek et al., 2021; secondary). EA's "Winning isn't everything" (Zhao et al., 2020) split human-likeness into skill and style, and chose the algorithm by which one a test needs (secondary). PathOS, a free navigation tester from Ontario Tech, drives agents by motives; designers found it useful but said its agents moved unlike players (secondary). Microsoft's Navigation Turing Test found classifiers can tell agent movement from human movement, while predicting graded human-likeness is unsolved (secondary). The chess model Maia was trained on millions of human games. Its lesson: matching a player's strength is different from matching their moves (secondary, via the 2026 survey "AI for Games in the Foundation Model Era").

### Search and reinforcement learning for difficulty and balance

Search agents measure balance by playing many games: Zook, Harrison and Riedl used MCTS agents of varied skill on Scrabble and a card game of their own (secondary). The industrial results point one way.

| Study | What predicted human difficulty | Finding |
| --- | --- | --- |
| King, Candy Crush (Gudmundsson et al., 2018) | A network trained on players' moves | Tracked level difficulty better than MCTS, at a fraction of the compute; a level in under a minute against days of playtesting (secondary) |
| Tactile Games, Lily's Garden (Kristensen et al., 2020) | An RL agent's moves in its best 5 per cent of runs | The best predictor of players' completion rate, by rank; the least skilled agent variant correlated best |
| Rovio, Angry Birds Dream Blast (Roohi et al., 2021) | RL plus tree search, with a simulated population | Best-case performance correlated more strongly than average; modelling skill, persistence and boredom helped (secondary) |
| Xiao and Yang (2024), Wordle and Slay the Spire | GPT-4 with chain of thought | Pearson r 0.62 on Wordle; 0.87 and 0.71 on Slay the Spire's first two acts, above a rule-based expert AI (0.74, 0.48). A near-optimal Wordle solver: 0.075 |

The near-optimal solver is the warning. An agent that plays too well plays unlike a person, and its sense of difficulty is useless. The agents that helped were human-trained or imperfect, and their rankings helped where their absolute rates did not.

### LLM agents as testers and critics

Xiao and Yang's title sums up their result: language models may not be human-level players, but they can be testers. They advise relative difficulty, strong models with reasoning, state written clearly as text, and small human pilots to calibrate.

TITAN (NetEase Fuxi with two universities, 2025) is the clearest production case. It plays an MMORPG from game state turned into compact text, and looks at screenshots only when reflecting. Against three professional testers on ten tasks per game it completed 96 and 94 per cent (the humans 100), found 15 bugs to their 5, and took less time. Without the text state its success fell to 72 per cent. Its bug detector raised false alarms 30 per cent of the time.

On judging experience the evidence is thin and mostly weak.

- MeepleLM (2026) predicts how five kinds of board-game player rate a game from its rulebook. Against real reviews of 207 unseen games, GPT-5.1's rank agreement was Kendall τ 0.26, a fine-tuned small model's 0.28. GPT-5.1's predictions bunched near the mean; on a polarising game the general models put everyone at 7 to 9 and missed those who hated it. Without personas, agreement fell to 0.13.
- PREFER (October 2026) has five LLM judges rate 91 card games on twelve experience dimensions. Their game rankings correlate 0.60 to 0.85 with each other, but no humans were tested. Models agreeing doesn't show they are right.
- Drake and Dong (2025) had six people and a GPT-4.1 judge rate generated game behaviours on the same scales. They correlated weakly (Spearman ρ 0.37 and 0.34) and not at all on emergence. Players enjoyed surprises the judge didn't reward, and the people were the more lenient raters.
- Stories (Chhun et al., 2024): LLM ratings of single stories correlated weakly with people's (Kendall 0.16 to 0.25). Their ranking of the systems that wrote them came close to human agreement (0.70 against 0.73). The models were far more self-consistent than people. A third of one model's written reasons made claims the story didn't support.
- Creative writing (Chakrabarty et al., 2024): experts passed New Yorker stories on 85 per cent of fourteen craft tests and GPT-4's on 28. No LLM judge correlated positively with the experts (secondary).

LLM judges rank groups of things moderately well and single items poorly. They agree with themselves more than people do, which is consistency without validity, and they miss surprise.

### Persona fidelity and its limits

- Personas explain little. Persona variables explain 1.4 to 10.6 per cent of the variance in people's annotations (Hu and Collier, 2024). Persona prompting gave small gains (about one point of explained variance on an irony dataset). Where personas explain under 10 per cent, the models' spread between personas often fell to near zero.
- Personas fade. Over hundred-round dialogues, seven models drifted back to their default assistant voice; distinctive persona patterns fell 41 per cent by the end ("Persistent Personas?", 2025). Larger models faded less, but all faded, and goal-driven dialogues faster. A playtest is goal-driven.
- Personas flatten. With 3,200 people across 16 identities, four LLMs misportrayed and flattened identity groups (Wang, Morgenstern and Dickerson, 2025; secondary).
- Simulations lack spread. Anthis et al. (ICML 2025) name five challenges for LLM social simulation: diversity, bias, sycophancy, alienness and generalisation. In one money-request game, models almost always chose 19 or 20; people's median was 17.

### Judges: sycophancy, leniency and other biases

- Assistants trained on human preferences learn to agree with the user, because people reward agreement (Sharma et al., 2023; secondary).
- LLM judges agree with people on chat answers over 80 per cent of the time, about as often as people agree with each other. They are swayed by an answer's position, prefer longer answers and favour their own (Zheng et al., 2023; secondary). The better a model recognises its own text, the more it prefers it (Panickssery et al., 2024; secondary).
- Of 13 judge models, only the largest aligned reasonably with people; percent agreement hid large score gaps, and judges leaned lenient (Thakur et al., 2024; secondary). Leniency is not universal: Drake and Dong's judge was stricter than the players, and a strict prompt moves scores more than a lenient one (2026; secondary). Calibration has to measure the direction.
- Across over 350 models, two models that were both wrong chose the same wrong answer 60 per cent of the time. Larger models and same-maker models were more alike (Kim et al., ICML 2025; secondary).
- Frontier models can often tell an evaluation from real use (Needham et al., 2025; secondary). A player agent knows it is in a playtest.
- Judge quality varies widely by task, so judges should be validated against people before use (Bavaresco et al., 2024; secondary).

### The game master is also a model

- World simulation. GPT-4 predicted the full next state of a text game correctly 59.9 per cent of the time with human-written rules (Wang et al., ACL 2024). Changes caused by the player's action were easier (77 per cent). Changes the world makes by itself were hardest (39 per cent), and those are what our engine is about: lives that go on without the player.
- Long-run consistency. NCP-Bench (2026) tests LLM narrators against a fact ledger. Contradicting an established fact happened in 40 to 68 per cent of sessions, by model; 3.5 per cent of runs reached a hundred turns without a conflict. Adding memory cut broken commitments from 26 to 4 per cent, but raised the rate of ignoring or rewriting the player's action from 13 to 38.

A player who says "this town makes no sense" may be reporting a slip by the game master.

## 2. Agents that play real games

| Agent | How it sees and acts | What it showed |
| --- | --- | --- |
| Voyager (2023), Minecraft | Game state as text through a code API; a library of code skills | Three times more unique items than earlier agents (secondary). It never reads the screen |
| Cradle (2024), Red Dead Redemption 2 | Screenshots in, keyboard and mouse out; GPT-4o | Following characters: 5 of 5 runs. Protecting Dutch in a fight: 1 of 5. Circled indoors, lost on cliff paths, misread icons. The game was paused while the model thought |
| SIMA 2 (DeepMind, 2025) | Pixels and a spoken instruction; keyboard and mouse | About 65 per cent task success against 31 for SIMA 1 and about 75 for people (secondary). DeepMind names long tasks, short memory, fine control and 3D understanding as limits |
| BALROG (2024) | Text, or text plus images, in six games up to NetHack | Images helped Claude 3.5 Sonnet a little (32.6 to 35.5) and hurt GPT-4o (32.3 to 22.6). Best NetHack progress 1.5 per cent. GPT-4o ate food it knew was rotten |
| VideoGameBench (2025) | Raw frames of 1990s games | Best models completed 0.48 per cent in real time, 1.6 with the game paused (secondary) |
| Gemini and Claude play Pokémon (2025) | Screen plus text read from memory, a map and notes | Long loops (Claude spent two to three days in one cave), hallucinated goals poisoning its notes, repetition once context passed about 100,000 tokens (secondary) |

Microsoft's Project Paidia, with Ninja Theory, built agents to play beside people rather than to test (secondary). Four lessons carry over.

1. State beats pixels for playing. TITAN lost 24 points of success without its text state. BALROG's images hurt as often as they helped. The Pokémon setups read the game's memory because the models read the screen badly.
2. Pause, and cut play into short tasks. Cradle paused the game and split missions into checkpoints; VideoGameBench's best score tripled when the game paused. Real-time play collapses.
3. Knowing is not doing. BALROG's agents named a danger and walked into it. Log what an agent does beside what it says.
4. Vision models miss fine detail. In VideoGameQA-Bench (NeurIPS 2025) the best of 16 models spotted a glitch in one image 82.8 per cent of the time. Scores fell to 45 on what changed between two frames and 40 on reading UI. The authors name the failures: posture, which way an object faces, whether a door is open. Clipping that wasn't there was the commonest false alarm. A sanded step or a renewed board is that kind of small property.

Exploring agents also move unlike people: BALROG's revisited rooms and got cornered, Cradle circled. Agent paths through the greybox show coverage and dead ends, not where people will walk or look. No primary source gives the cost of an hour of agent play.

## 3. Industry practice

| Who | What the agents do | Checked against people? | What worked, what failed |
| --- | --- | --- | --- |
| King | Predict Candy Crush level difficulty from a network trained on player moves | Yes, against players' success rates (secondary) | Beat MCTS bots, far cheaper. Figures not read |
| Tactile Games, Rovio | RL and search bots predict pass and churn rates | Yes, against player data (Lily's Garden: about 900,000 players) | Rankings and best-case runs; not absolute rates |
| EA SEED | RL agents beside scripted tests for coverage, exploits and stuck spots (Battlefield 2042, Dead Space) | Against seeded bugs | Curiosity plus imitation of experts found all 13 seeded bugs in one study. Development builds differ from the final game, and RL is not always practical for teams (secondary) |
| Ubisoft La Forge | RL bots and navigation agents (Far Cry New Dawn, Rainbow Six Siege) | Not published | (secondary) |
| Riot | RL agents play Legends of Runeterra decks to flag cards too strong or weak | Against designers' intuitions | 48 per cent win rate against top players; became a designers' measure (secondary, vendor blog) |
| NetEase (TITAN) | LLM agent tests an MMORPG from text state | Three professional testers | More bugs, nearly the same task success, 30 per cent false alarms |
| modl.ai, nunu.ai, Razer | Commercial agent testers, some from frames alone | No published validation | Claims of 20 to 50 per cent savings, unaudited (secondary) |

Studios use bots for difficulty, coverage, exploits and regressions. We found no studio that publishes agent ratings of fun validated against players, nothing from Blizzard, and did not cover Unity ML-Agents case studies. The studios that validated worked one way. People played the content first, at scale. Agents were trained or tuned on that play and judged by how well their rankings matched, and people kept playing. The bots took over repetitive checks.

## 4. Simulated people and social worlds

### Generative agents

Stanford's Generative Agents (Park et al., 2023) put 25 agents in a small town. Each keeps a memory stream, reflects on it and plans its day. About a hundred people ranked their interview answers for believability: the full architecture scored highest (TrueSkill 29.9), above humans role-playing the same agents (23.0). A Valentine's party spread from 1 agent's plan to 13 who knew of it in two game days; of 12 invited, 5 came. Our players and game master share its failures. Memories went unretrieved and details were embellished. World knowledge leaked in: a neighbour was credited with a famous book because of his name. Speech was stiff and over-cooperative, and choices grew odder as memory grew.

A follow-up built agents of 1,052 real people from two-hour interviews. They predicted those people's survey answers at 83 per cent of the consistency the people showed with themselves two weeks later, 86 with surveys added; demographics alone reached 74 (secondary). Rich context beats a label. People often could not tell Social Simulacra's generated community members from real ones (secondary). Believable still isn't faithful: believable fictional behaviour is no evidence of fidelity to a real person (secondary, the 2026 survey).

### Silicon samples

| Study | Finding |
| --- | --- |
| Argyle et al. (2023) | GPT-3 given real respondents' backstories reproduced subgroup patterns: "algorithmic fidelity" (secondary) |
| Aher, Arriaga and Kalai (2023) | Replicated classic experiments; on wisdom of crowds, models were too accurate to be human (secondary) |
| Bisbee et al. (2024) | Averages matched a national survey, but answers varied too little, and small prompt changes or three months shifted results (secondary) |
| Hewitt et al. (2024) | GPT-4 predicted about 470 effects from 70 preregistered experiments at r = 0.85, but overestimated their size and did worse for subgroups (secondary) |
| NN/g, synthetic users | Three real studies rerun: answers shallow and too favourable, every concept praised, every course claimed finished, no sense of what mattered most |
| Maier et al. (2025) | Direct numerical ratings from models gave unrealistic distributions; free text mapped to the scale reached 90 per cent of human test-retest reliability (secondary) |

Simulated people get the direction of an effect right more often than its size, the average more often than the spread, and the population more often than a subgroup. They suit pilots, sensitivity checks and hypotheses. NN/g's rule fits us: never present synthetic findings as research with people.

## 5. Methods that make agent playtests trustworthy

- Validate on the same material. The studies that earned trust in agents had people do the same task first, and measured agreement item by item, not by comparing averages.
- Compare ranks. Agents' difficulty rankings matched people's where their pass rates did not. Use Spearman or Kendall rank correlation.
- Use chance-corrected agreement. Percent agreement hides disagreement when most answers fall in one category (Thakur et al.). Report Krippendorff's alpha or Cohen's kappa.
- Calibrate in both directions. Leniency runs both ways, so put things of known quality, good and weak, through the same pipeline. A measure that can't separate them measures nothing.
- Keep arms blind. The cold readers already do this: a key committed first, a coder who doesn't know the arm, shuffled facts and layers off as controls.
- Diversify, knowing the limits. Same-maker models share errors, and personas add little spread. Vary temperature, prefer rich context to labels (Anthis et al.). More runs give a spread, not independence.
- Pre-register, and log drift. Anthis et al. recommend writing predictions down before running. People's criteria change as they grade ("criteria drift", Shankar et al., UIST 2024; secondary), so a pre-registered pass is followed by a labelled second pass.
- Combine few humans with many agents. Prediction-powered inference (Angelopoulos et al., 2023) and the mixed-subjects design (Broska, Howes and van Loon, 2025) use a small human sample to correct the bias in many model predictions. The intervals stay valid (secondary). A co-author puts the gain in effective sample size at only about 15 per cent (unverified). Its worth is the bias correction.
- Elicit ratings as words. Direct numbers from models bunch and skew. Free text coded afterwards, or a forced choice between two options, behaves better.

| Agents catch | Agents miss or distort |
| --- | --- |
| Missing information: what they asked for and couldn't find | Fun, delight, true surprise |
| Broken loops, dead ends, softlocks, contradictions | Boredom over real time; they claim to finish everything |
| Exploits and degenerate strategies | The negative tail: players who hate it |
| Relative difficulty, when calibrated | Absolute difficulty and pass rates |
| Bugs at scale with state access | Fine visual detail on screen |
| Coverage: places nobody went | Where people will look and walk |
| Consistency across runs | Spread between kinds of player; persona drift |

## 6. What this means for our programme

### The paper-playtest method

The method is sound in its bones. Players see only their screen, and the game master holds the truth and labels what it simulates. Players predict and name what they need, and calibration games run through the same studio. Seven changes would make it sounder.

1. Uncross persona and model. P1 and P3 always run on Sonnet; P2, P4 and P5 on Opus. A difference between the cozy player and the sceptic can't be told from a difference between the models. Run each persona on both, at least in the replay.
2. Run each cell three times. One run per persona per concept gives no spread. A finding in one run of three is a lead.
3. Add a weak anchor. Beside the well-loved calibration games, run a known-mediocre game, or one of ours with the lives switched to a fixed script. If marks and pull don't drop for it, they can't rank the concepts.
4. Audit the game master. Keep a fact ledger per player. A second model, from another maker where possible, checks a sample of resolved turns against the ledger and `world/engine-rules.md`, and counts contradictions. Confusion that traces to a game-master slip is struck from the register.
5. Check personas stay distinct. A blind coder reads round 1 and round 6 act files without names and says which persona wrote each. If it can't tell the sceptic from the cozy player by round 6, persona-specific findings fall away. Restate each persona in every screen's header.
6. Read numbers within a player. Keep marks and pull, but read them as change within each player and against the anchors, never as levels across players. Ask exit questions as choices: of this and yesterday's calibration game, which would you open next week?
7. Pre-register the analysis. Commit what each concept's analysis will count and what would kill it before the sessions, as the cold readers do. Later findings go in a labelled second pass.

The blind arm (lives on or off) is the method's strongest idea. Its value depends on the analyst coding before the arm's label appears in anything they read.

### Which measures to trust

| Measure | Trust | Use it as |
| --- | --- | --- |
| Predictions scored against the engine's record | High: ground truth | The headline, set against the engine's readers (base rate 58.0 per cent, calibrated witness 64.6) |
| Needs a player couldn't meet, checked against the screen | High once checked | The register's best source |
| Broken loops, dead ends, contradictions, exploits | High once the game-master audit clears them | Must-fix items |
| Lives on against off: differences in predictions and needs | Medium to high, if blind | Evidence for the engine's worth on screen |
| Concept ranking by calibrated marks and pull | Medium, if the anchors separate | An ordering to test with people |
| Marks and pull as levels | Low | Never averaged across personas |
| "Would buy", "would come back", fun, delight | Low | Hypotheses only |
| Persona claims ("an FM fan would love this") | Low | What each kind would try |
| Sonnet and Opus agreeing | Low: correlated errors | Not evidence alone |

### Validating against Øystein and his testers, cheaply

1. A ranking set. Ten short excerpts from the sessions (an opening and three rounds each, across concepts and anchors). Øystein and three to five testers rank them by "which would you keep playing". Compare with the agents' ranking by Kendall's τ. If τ is low, the agents' concept ranking carries no weight; the register stays.
2. A register sample. Øystein triages twenty items drawn at random from the must-improve register, without seeing how many players raised each. The share he accepts is the register's precision, tracked round by round.
3. One human player. A tester plays one concept through the same game master and opening as an agent persona. Compare needs, predictions and the round where pull fell. It shows the kinds of difference, not their size.
4. The cold readers' human test. Report agreement between people and the model panel as a number (Krippendorff's alpha on marked parts) each time people read.
5. A log of where agents misled us. One line each time people overturn an agent finding: what agents said, what people did, why. After a few rounds this list is the calibration we trust.

When we estimate a rate (turns marked confused, history found), 20 to 40 human-rated items let prediction-powered inference correct the agents' bias. That is cheap and honest, though it won't make a small human sample large.

### Agents in the greybox

Two kinds of agent, with different senses.

- Testers look for what breaks: stuck spots, missing routes, loops that end, inspections that answer nothing, frame drops. They get structured state, plus screenshots at moments of doubt. The state holds only what a player could perceive: what is in view, by record id and screen position, and what the interface shows. Facts the screen doesn't give stay out, or legibility tests are spoiled. They pause each step, move with a route tool on the town's graph (`collision-and-navigation.md`) rather than steering by keys, and work in short checkpointed tasks. Notes and a map live outside the context, which resets between tasks.
- Readers judge whether the screen shows history. They get only frames at the player's pixel size, scored against the key as the cold readers are. Before their misreadings count against a scene, a perception probe measures what the model can see at all. It uses frames with known answers: is this door open, is this board newer than its neighbours?

Deterministic replays let Øystein watch any agent session, then play the same seed himself. Log every action and outcome beside the agent's commentary. Record tokens, wall time and steps per task from the first run. Agent paths give coverage maps; human paths in the same build give attention maps.

## What we should do

1. Lead with what can be scored. Predictions against the engine and checked needs head every paper and greybox round. They need no judge.
2. Audit the game master with a fact ledger and a second-model check on a sample of turns.
3. Add a weak anchor beside the well-loved calibration games. Marks rank concepts only if they separate the two.
4. Uncross persona and model, three runs per cell.
5. Run the cheap human checks: the ranking set, Øystein's blind triage of twenty register items, the log of where agents misled us.
6. Pre-register each round's analysis and keep the blind arm blind until coding is committed.
7. Check persona distinctness with a blind coder.
8. Build the greybox's perception API before its agents: what a player could see, by record id, and nothing more. Then the pause, the route tool and action logs.
9. Run a perception probe before scoring scenes with reader agents.
10. Add a model from another maker where a free or open one can do the job, first as the game-master auditor. It is the cheapest way to break correlated errors.

## Gaps

- We found no study validating LLM ratings of fun or engagement against video-game players. The evidence covers difficulty, bugs and coverage, so our own claims on fun stay small.
- No study tests whether game personas (a Football Manager devotee, a cozy player) behave like those players. Persona research comes from surveys and chat.
- No primary source gives the cost of an hour of agent play.
- Whether vision models can read history in a 3D street is untested. VideoGameQA-Bench suggests trouble at our scale of detail; the perception probe will tell.
- How far paper findings carry to the greybox is unknown. It will be learned when the first greybox round repeats a paper finding.
- Not read: King's correlation figures, Unity ML-Agents QA case studies, Blizzard's practice, and the testing chapter of the 2026 survey. Several key papers were read only as abstracts and are marked.

## Sources

Agents as playtesters
- Holmgård, Green, Liapis, Togelius, Automated playtesting with procedural personas through MCTS with evolved heuristics, IEEE ToG 2019: https://arxiv.org/abs/1802.06881
- Ariyurek, Surer, Betin-Can, Playtesting: what is beyond personas (abstract): https://arxiv.org/abs/2107.11965
- Zhao et al., Winning isn't everything, IEEE ToG 2020 (search summary): https://arxiv.org/abs/1903.10545
- Devlin et al., Navigation Turing Test, ICML 2021 (abstract): https://arxiv.org/abs/2105.09637
- Stahlke, Mirza-Babaei, PathOS (thesis record): https://ir.library.ontariotechu.ca/handle/10155/1181
- Zook, Harrison, Riedl, MCTS for simulation-based strategy analysis (search summary): https://arxiv.org/abs/1908.01423
- Gudmundsson et al., Human-like playtesting with deep learning, CIG 2018 (abstract): https://www.academia.edu/40020341/Human_Like_Playtesting_with_Deep_Learning
- Kristensen, Valdivia, Burelli, player completion rate with RL, CoG 2020: https://arxiv.org/html/2306.14626v1
- Roohi et al., difficulty and churn in Angry Birds Dream Blast (search summary): https://arxiv.org/pdf/2107.12061
- Xiao, Yang, LLMs may not be human-level players, but they can be testers, 2024: https://arxiv.org/html/2410.02829v1
- TITAN, Leveraging LLM agents for automated video game testing, 2025: https://arxiv.org/html/2509.22170v1
- MeepleLM, 2026: https://arxiv.org/html/2601.07251v5
- PREFER, 2026: https://arxiv.org/html/2610.19213v1
- Drake, Dong, Real-time world crafting, 2025: https://arxiv.org/html/2510.16952v1
- AI for Games in the Foundation Model Era, survey, 2026 (first part read): https://arxiv.org/html/2609.16679

Judges, personas and game masters
- Chhun, Suchanek, Clavel, Do language models enjoy their own stories?, 2024: https://arxiv.org/html/2405.13769
- Chakrabarty et al., Art or artifice?, 2024: https://arxiv.org/html/2309.14556
- Hu, Collier, Quantifying the persona effect in LLM simulations, 2024: https://arxiv.org/html/2402.10811
- Persistent personas? Role-playing, instruction following and safety in extended interactions, 2025: https://arxiv.org/html/2512.12775v2
- Wang, Morgenstern, Dickerson, LLMs that replace human participants can harmfully misportray and flatten identity groups, Nature Machine Intelligence 2025 (abstract): https://arxiv.org/abs/2402.01908v3
- Sharma et al., Towards understanding sycophancy, 2023 (abstract): https://arxiv.org/abs/2310.13548
- Zheng et al., Judging LLM-as-a-judge, 2023 (abstract): https://arxiv.org/abs/2306.05685
- Panickssery et al., LLM evaluators recognise and favour their own generations, 2024 (abstract): https://arxiv.org/abs/2404.13076
- Thakur et al., Judging the judges, 2024 (abstract): https://arxiv.org/abs/2406.12624
- Bavaresco et al., LLMs instead of human judges?, 2024 (abstract): https://arxiv.org/abs/2406.18403
- Kim et al., Correlated errors in large language models, ICML 2025 (search summary): https://arxiv.org/abs/2506.07962v1
- Needham et al., LLMs often know when they are being evaluated, 2025 (search summary): https://arxiv.org/abs/2505.23836v2
- Shankar et al., Who validates the validators?, UIST 2024 (search summary): https://arxiv.org/abs/2404.12272
- Beyond consensus: strict and lenient judge prompts, 2026 (search summary): https://arxiv.org/pdf/2608.30373
- Wang et al., Can language models serve as text-based world simulators?, ACL 2024: https://arxiv.org/html/2406.06485
- NCP-Bench, Can LLM agents stick to the script?, 2026: https://arxiv.org/html/2608.08160

Agents that play games (gathered by the helper)
- Voyager: https://arxiv.org/abs/2305.16291
- Cradle: https://arxiv.org/html/2403.03186
- SIMA: https://arxiv.org/abs/2404.10179 and SIMA 2: https://deepmind.google/blog/sima-2-an-agent-that-plays-reasons-and-learns-with-you-in-virtual-3d-worlds/ (figures via https://decrypt.co/348569/google-deepmind-ai-agent-learns-adapts-plays-games-like-human)
- BALROG: https://arxiv.org/html/2411.13543v2
- VideoGameBench (abstract): https://arxiv.org/abs/2505.18134
- lmgame-Bench (abstract): https://arxiv.org/abs/2505.15146
- Gemini plays Pokémon (secondary): https://www.dbreunig.com/2025/06/17/an-agentic-case-study-playing-pokémon-with-gemini.html
- Claude plays Pokémon (secondary): https://www.lesswrong.com/posts/q9HoBo6LCkCkxavLZ/on-getting-unstuck
- VideoGameQA-Bench, NeurIPS 2025: https://arxiv.org/html/2505.15952v2

Industry
- EA SEED: Bergdahl et al. 2020, https://arxiv.org/abs/2103.15819; Sestini et al., https://arxiv.org/pdf/2202.10057; Gillberg et al. 2023, https://arxiv.org/abs/2307.11105v1; https://www.ea.com/technology/news/seed-ml-research-aaa-game-testing
- Ubisoft La Forge publications: https://www.ubisoft.com/en-us/studio/laforge/publications
- Riot and Legends of Runeterra (vendor blog): https://www.anyscale.com/blog/riot-games-and-deep-reinforcement-learning-in-gaming
- Microsoft and Ninja Theory, Project Paidia (secondary): https://www.cambridgenetwork.co.uk/index.php/news/microsoft-research-cambridge-collaborates-game-developer-ninja-theory
- Commercial testers (secondary): https://cloud.google.com/blog/products/gaming/co-op-mode-the-ai-partners-driving-the-the-future-of-gaming/ and https://esports.gg/news/tech/razer-announces-wyvrn-for-game-developers/
- GDC 2026 State of the Industry (secondary): https://www.businesswire.com/news/home/20260129438528/en/

Simulated people
- Park et al., Generative agents, 2023: https://arxiv.org/html/2304.03442v2
- Park et al., agents of 1,052 people (abstract): https://arxiv.org/abs/2411.10109
- Park et al., Social simulacra, 2022 (abstract): https://arxiv.org/abs/2208.04024
- Argyle et al., Out of one, many (abstract): https://arxiv.org/abs/2209.06899
- Aher, Arriaga, Kalai, Turing experiments (search summary): https://arxiv.org/abs/2208.10264v5
- Bisbee et al., Synthetic replacements for human survey data?, Political Analysis 2024 (search summary): https://www.cambridge.org/core/product/B92267DC26195C7F36E63EA04A47D2FE
- Hewitt et al., Predicting results of social science experiments (search summary): https://www.gsb.stanford.edu/faculty-research/publications/large-language-models-can-predict-results-social-science-experiments
- Anthis et al., LLM social simulations are a promising research method, ICML 2025: https://arxiv.org/html/2504.02234v2
- NN/g, Synthetic users: https://www.nngroup.com/articles/synthetic-users/
- Maier et al., purchase intent via semantic similarity (search summary): https://arxiv.org/abs/2510.08338

Statistics
- Angelopoulos et al., Prediction-powered inference, 2023 (abstract): https://arxiv.org/abs/2301.09633
- Broska, Howes, van Loon, The mixed subjects design, Sociological Methods & Research 2025 (search summary): https://ideas.repec.org/a/sae/somere/v54y2025i3p1074-1109.html
