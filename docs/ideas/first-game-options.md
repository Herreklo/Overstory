# The options for the first game

Status: ideas, not decisions. Øystein decides which game comes first; this page prepares the choice. It feeds the paper playtests (plan step 1f+) and tells the greybox (1g) what to test. Written on Opus, October 2026.

This page holds what the six options share: the tests, the givens, what the games teach, the comparison, the recommendation as it was recorded, and the greybox tests. Each option's full design now lives with its family of ideas, linked in section 2; the catalogue of every idea is `README.md`. Section 7 gathers the other rankings and recommendations recorded for game ideas. None is a decision.

## What this is for

Overstory is a world for many games. The first should answer Overstory's question best: can someone read people and history better from the world on screen than from the engine's page? Two tests hold together:
- **A game, not a walking simulator** (`CLAUDE.md`, Øystein, 21 October). Every option has goals, challenge, stakes, mastery, failure, and decisions that cost something. Reading the world is a skill that pays off in play, as deduction does in Obra Dinn or scouting in Football Manager, never the whole of it.
- **The town is not decoration** (`game-layer-ideas.md`, What each idea asks of Overstory). If the game would play as well as a spreadsheet, the world on screen adds nothing.

Game-ness is judged with Jesper Juul's classic game model (2003, read whole). A game has rules; a variable, quantifiable outcome; values on the outcomes; effort that changes the outcome; a player attached to it; and consequences that are negotiable. Open-ended simulations such as The Sims are borderline in it, because no outcome is valued over another. Each option below gives its goal, resources, opponents or pressure, fail states and mastery curve, so that all six features hold.

The givens:
- **The world on screen starts in 1989 and moves forward.** The past before it is a starting record, never drawn.
- **A dense harbour town,** a few hundred buildings in its heart, not a metropolis.
- **People are blockouts** (grey bodies, readable silhouettes, simple motion) until their own step.
- **Facts come from the engine;** the screen never invents one. Three dials set each role: control, influence and knowledge (`docs/living-world.md`).
- **The engine today** is Understory at round 41, read through the GitHub API. Its people have personalities, values, aptitudes and habits (as sentences). They form groups (the band is the pack's one kind) and contest a band place. Age and illness kill them; work accidents only injure. Their secret acts are skimming, lying to cover and blaming, and secrets get out. Accounts carry their teller, and every event says who saw or heard it. The engine has no buildings or homes yet; homes come after its next two rounds. It has no player command (the first, an invitation to a rehearsal, comes with #22), no records, no crime and no sport. Its first real run is in `fixtures/engine/understory-world-9989.json`.

Understory's `WHY.md` began with a band manager and names a football manager, a journalist and a detective as other ways in. It warns that each game needs real domain depth: rich people cannot carry a shallow game.

Game claims below come from press, wikis and interviews and are (secondary) unless marked (unverified). Two primary texts were read whole: Tynan Sylvester's "The Simulation Dream" and Jesper Juul's "The Game, the Player, the World". Two helper passes gathered most of the rest.

## 1. What the games teach

### Managers

| Game | Why its loop works | What it asks of a living, ageing town |
| --- | --- | --- |
| Football Manager | A day per click, a match a week, seasons for decades. Attributes show as ranges until scouted (fan guides); the match draws a result already decided. | True abilities, plus who knows what. Faces that hold for decades, or players read the numbers instead. |
| Motorsport Manager | Strategy is decided while the race is watched; drivers peak and decline. | Ability that rises and falls with age and life. |
| Rock Star Ate My Hamster (1988), Rock Manager (2001) | Recruit, record, tour, keep egos together; comic stock types. No well-known recent band manager was found. | Members as people who drift, marry, quit and age. |
| Game Dev Tycoon | An era clock: platforms come and go, and timing pays. | Era turnover caused by people, not scenery. |
| Two Point Hospital, Campus | A state readable on every figure (unverified; not researched). | Every such mark a fact. |

### Lives and generations

| Game | Why its loop works | What it asks of a living, ageing town |
| --- | --- | --- |
| The Sims | A household hour by hour. The Sims 2 added ageing and inherited looks; players resented The Sims 3 changing households they never saw. | Off-screen lives, and a return that shows what changed and why. |
| Crusader Kings III | Succession is the act break: you go on as the heir. | Inherited looks; parents known again in old age. |
| RimWorld | A storyteller paces incidents that linger. Sylvester: what never reaches the player's mind is worthless, and players read intent into anything. | Causes that can be seen; texture that claims no history. |
| Dwarf Fortress | Legends mode reads history; adventure mode walks into it. | A linked record, and places to visit it. |
| King of Dragon Pass | A few decisions a season; advisors who disagree. | Counsel from what each person witnessed. |
| Ultima V and VII | V gave the series its first day schedules (not IV); VII deepened them. | Routines from jobs and households. |
| Wildermyth | Heroes age between chapters and keep their scars. | Age and wounds that last across jumps. |

### Reading and exploring

| Game | Why its loop works | What it asks of a living, ageing town |
| --- | --- | --- |
| Pentiment | One town in acts, 1518, 1525 and 1543; too little time for every lead; accusations without certainty. Testers forgot people absent across a jump. | The same people across jumps, changed for stated reasons; someone who recurs. |
| Disco Elysium | Skills speak as fallible inner voices; knowledge is mostly on the page. | Readings of people as named, fallible voices. |
| Kentucky Route Zero | Choices set how people explain themselves; facts stay fixed. | Interpretation the player's, facts the engine's. |
| Citizen Sleeper | Daily dice as a visible budget of time (its clocks unverified). | A scarce day; lives that move without you. |
| Outer Wilds | Knowledge is the only progression; the log keeps what you saw, not what to conclude. | A learnable schedule. |
| Return of the Obra Dinn | Frozen deaths; fates confirmed in threes; chapters added when out-of-order scenes confused testers. | Scenes rich enough to identify people: criterion 2 as play. |
| Heaven's Vault | Guesses confirmed only when they recur elsewhere. | Readings settled by later evidence. |
| Her Story | A search over clips; the player assembles a life; no verdict. | A scene as the clip that answers a question. |
| Unpacking | A life read from objects at each move. | Possessions as dated facts. |
| What Remains of Edith Finch | A house grown by generation, its dead kept in their rooms; all authored. | Criterion 1 done by a system, not by hand. |

### Watching

| Game | Why its loop works | What it asks of a living, ageing town |
| --- | --- | --- |
| Hitman (2016 on) | Learn a place by watching; overheard talk opens chances; routines predictable, and nudged so nobody waits. | Schedules stable within a day, readable from bodies. |
| Townscaper | A toy: approved pieces fitted by a generator; no goal. | Our rule, plus facts: nothing in it is old, changed or neglected. |

### Role-playing games

| Game | Why its loop works | What it asks of a living, ageing town |
| --- | --- | --- |
| Baldur's Gate 3 | Reactivity to almost anything, authored and tracked in spreadsheets; testing grows with every combination. | Payoffs from the record, not authored line by line. |
| Divinity: Original Sin 2 | Systemic surfaces under authored people; companions with agendas who judge you. | A band member or captain as a companion with a goal. |
| Fallout: New Vegas | Reputation per faction; slides summarise the ending. | Consequences visited, not narrated; memory per person. |
| Planescape: Torment | The past self learned from those who knew him; its writer says it needed text. | A history held in what others remember. |
| The Witcher 3 | Consequences delayed and made visible. | Payoffs years later, in the street. |
| Kingdom Come: Deliverance I and II | Towns run on routines; witnesses report crimes. Memory is mostly of the player's crimes. | Memory between residents. |
| Pathologic 2 | Twelve days; time runs whether you act or not; people die if you fail them, some unseen. | Absence as a cost; every loss shown. |
| Persona 3 to 5 | A school year on a calendar; evenings spent on people; the arcs authored. | A season as an act, time with a person as the budget. |
| Stardew Valley | Schedules by weekday, weather, season and the town's own state; villagers barely age. | Learnable routines that also age. |
| Yakuza | One dense district across games and decades (Yakuza 0 is set in 1988); changes authored per game. | One place across eras, changed by the record. |

### Mysteries

| Game | Why its loop works | What it asks of a living, ageing town |
| --- | --- | --- |
| Shadows of Doubt | A generated city: every citizen with a name, home, job and routine; prints, call logs, bins, a case board. It went first-person because top-down cut players off from the simulation. It wears thin: learned patterns, repeated documents, cases that fizzle or fall open, a form to close. | Evidence from each life, never templates; a camera close to the lives. |
| The Case of the Golden Idol | Frozen scenes give words; an account's blanks are checked by segment; some critics brute-forced the last names. | A case proved fair before play. |
| Paradise Killer | Accuse anyone, but prove it; the game never says whether you were right. | The engine fixes the truth; the player reads it. |
| Bad News (Ryan, Samuel, Summerville) | A resident of a generated 1979 town has died alone; the player finds the next of kin by talking to the town, every resident played by one actor. IndieCade's Audience Choice. | A death as the frame for a whole life, without a crime. |
| Talk of the Town (Ryan) | A town simulated from 1839 to 1979, built on what people know and how it spreads; that its people misremember and lie is from a paper's title we remember but did not find (unverified). Ryan's "story sifting" finds the tellable chains. | The witness layer, and a sifter that picks the case. |

### What runs across them

- Knowledge is the progression. The facts stay fixed; the player's view grows.
- Confirmation is rationed or refused, and each game chooses on purpose.
- Compared moments work only if someone recurs.
- Routines can be watched when they are stable, readable and compressed.
- Time as a budget makes an evening the decision.
- A consequence nobody sees never happened, for the player.
- The page is strong. The screen must win on recognising people and showing consequences, not on density.

No game found lets residents remember each other across years, visibly. That is where Overstory fits.

## 2. Six options

The criteria are those in `CLAUDE.md`:
1. a building's history read at a glance;
2. a person recognised across scenes and years;
3. a consequence the page does not make obvious;
4. the scene preferred to the page, without misleading;
5. a street at city scale holding its look and frame rate.

Costs are rough weeks of the weekly usage limit, the plan's own unit, before the architecture.

Each option's full design (the game, core loop, dials, time, the game in it, needs, what is only here, risks, cost, criteria and greybox) is on its family's page.

1. **The club** (`groups.md`, The club). You run a harbour town's football club in the lower leagues from 1989; the players are amateurs with day jobs.
2. **The band** (`groups.md`, The band). You manage a band formed in 1989 in the loft on Harbour Row: Understory's origin game and the shared milestone (request 8).
3. **The restorer** (`roles.md`, The restorer). You buy, restore, let and sell houses in the old town after the crash, and decide what of each to keep. Reshaped from "the return", a photographer's visits.
4. **A life and its heirs** (`lives.md`, A family across generations). One resident through acts years apart, then their child: the family across generations, played as a role-playing game.
5. **The paper** (`roles.md`, The paper). The reporter on the town's weekly paper from 1989, an edition a week.
6. **A death in the town** (`mysteries.md`, A death in the town). Someone has died, and what happened is unclear; you read the town to find out.

## 3. Is there a role-playing game here?

Yes: option 4. The answer in full, with what the role-playing games bring and what they cost, is with option 4 in `lives.md` (Is there a role-playing game here?). The paper playtest's role concept is in `roles.md` (A role in the town).

## 4. Comparison

● strong, ○ some, · little.

| Option | Control, influence, knowledge | Span | Engine readiness | Cost on top (weeks) | Criteria 1 2 3 4 5 | Biggest risk |
| --- | --- | --- | --- | --- | --- | --- |
| The club | team and money; players and board; own squad | seasons, decades | needs a club kind, sporting skills, a match model | 16 to 26 | ○ ● ○ ○ ● | plays as well on the page; the match is its own big system |
| The band | own acts; the members; own band | album cycles, a career | best: band, contests and shows exist; band year and first command planned | 12 to 20, plus music | ○ ● ● ● ○ | the music |
| The restorer | money, houses, works; owners, tenants, council; inspection and records | projects, years | weak: no buildings, owners or prices (ours meanwhile) | 12 to 20 | ● ○ ● ● ○ | an economy that would make Overstory the engine |
| A life and its heirs | one person; family; a resident's | acts, generations | weakest: commands, homes, intervals, people who change | 24 to 40 | ● ● ● ○ · | scope; people barely change |
| The paper | own work; publication; sources | weeks, a career | records and publication needed | 12 to 18 | ○ ○ ● ● ● | the page wins |
| A death in the town | own acts; asking, accusing; witnesses and records | weeks, acts years apart | deaths and secrets now; crime later | 14 to 22 | ● ● ● ● · | expecting a murderer; fairness |

Game-ness, after Juul's six features, the challenge and mastery curve, and the stakes. The rank is this page's own, as recorded; no game is chosen:

| Option | Juul's six | Outcome that is won or lost | Challenge and mastery curve | Stakes | Rank |
| --- | --- | --- | --- | --- | --- |
| The club | all six, and proven | league place, promotion, the club's survival | survival, then building a squad; scouting and reading people sharpen | the club, your job, promises | 1 |
| A death in the town | all six with the scored close; the outcome is weak without it | the inquest's finding, scored against the record | the sifter raises difficulty by chain; reading and asking sharpen | an innocent blamed, trust, the case | 2 |
| The restorer | all six | money, houses, a street kept | from one cheap house to a street; reading buildings sharpens | money, houses, the street | 3 |
| The band | all six, the outcome softer | crowds, money, survival, legend counted apart | first gig to a career; reading chemistry sharpens | the band, debts, members' lives | 4 |
| The paper | all six | sales, stories won, corrections | leads to investigations; judging sources sharpens | the paper, sources, reputation | 5 |
| A life and its heirs | borderline without each act's goal | each act's goal; the family's fate | weak; little to get better at | the house, the family | 6 |

## 5. Recommendation

Recorded as this page's recommendation, not a decision: which game comes first waits for Øystein (`NOW.md`). The paper playtests that were to test its condition stopped at 11 of 24 runs; their interim outcome is in `README.md`.

**Recommended first game: a death in the town,** with the shared reading verbs as its tools. Ranked first overall: second on game-ness, first on Overstory's question, at a middling cost.

**As a game.**
- *The player wins* an account that holds: the inquest accepts it, the family can live with it, and the record, shown when the case closes, bears it out fact by fact.
- *The player risks* other people. Every question is an act others hear of. Trust spent does not come back, and a wrong account follows someone in the engine for years.
- *The player can fail:* the wrong person blamed, a source burned, the inquest unpersuaded, the case closed open.
- *The player gets better at* reading routines, traces and accounts, and at asking without giving themselves away. The sifter answers with harder cases: more people with causes, more lies, older evidence.

**Why it comes first.**
- Reading the world is the skill that wins, and criterion 4 (not being misled) is its scoring.
- It is made of what the plan builds anyway: the town through the years, records, the reading interface, the photograph held at its spot. It needs no match, no songs and few interiors.
- Evidence, not verdicts, is its natural law: accounts may be wrong, and nothing is confirmed during play.
- It starts on today's engine (natural deaths, secrets, lies, accounts), and gains an opponent if murder is requested.
- Each seed gives other lives and other deaths.

**The condition.** If the paper playtests find that the case without a culprit is mostly looking (low marks for agency and stakes against the club or the band), it is not ready as a first game. Then the choice moves to the band, or to the mystery with murder once the engine has it.

**The others.** The band is the alternative if Øystein wants the engine's origin game: the engine is building toward it, and its loft and bar stand on the corner's street. Choose it once the music has an answer. The club is the most proven game, but its core plays as well on the page and costs the most; it suits a later game, once people and crowds exist. The restorer makes criterion 1 the core skill, but its economy belongs to the engine. The paper shares the mystery's systems and could be its second role. A life and its heirs is the richest and the dearest, and the weakest as a game.

## 6. What the greybox should test first

The four tests share the corner, blockouts and fixtures. Each tests play: a choice that costs something, an outcome, and whether reading paid off. Each also separates options.
1. **A clock and a choice** (all six). Three evenings in the corner; each evening two things happen in different places, and the player can be at only one. On the fourth day they must predict who will be where, and act on it. Measure correct predictions, regret, and whether the players who read the routines best did best.
2. **A case with stakes** (the death, the paper). A death at the foot of the steps, three days to the inquest, three questions a day, each heard of by others. The player gives an account, and the record scores it. Run it twice with different seeds: do players get better on the second case? That is the mastery curve, and the test that separates the options most.
3. **A command with a cost** (the band, the club, the restorer, the life). Invite a musician to the loft at the price of the month's rent and a promise, or buy house D on a budget. The fixture accepts or refuses, with its reason. A week later, is the cost and its trace readable, and does it feel like agency or a dice roll?
4. **The jump as a payoff** (all). The corner in 1989, then 2000, the same blockouts. Did the 1989 choice pay off or cost, visibly, and does the player want to play the next act?

Tests 1 and 4 come almost free with 1g and 1f. Test 2 costs a day of fixtures and a scoring key from the record, test 3 a fixture that answers. Run 2 first, against 1 as its control.

For the paper playtests (1f+), where each may hold or turn into a chore:

| Option | Hour 1 | Hour 10 | Hour 100 | Won or lost | Turns into a chore at |
| --- | --- | --- | --- | --- | --- |
| The club | a lad found, a first match | a season; a life intrudes on the squad | the captain's son; the stand built | results, promotion, the club | weekly admin |
| The band | the first rehearsal | the first gig; a member lost | the reunion | crowds, money, the band | booking gigs |
| The restorer | house D bought or passed over | a project's profit or loss | a street kept or sold | money, houses | paperwork and crews |
| A life and its heirs | six evenings | a jump; a parent older | your child's act | each act's goal | evenings as a checklist |
| The paper | a lead and an edition | a story's consequence | a career's archive | sales, corrections | filling the edition |
| A death in the town | the death found; first accounts | the inquest and its score | the cold case | the account, an innocent | the board |

## 7. Other recorded rankings and recommendations

Each was written in its own round of ideas. They disagree, and none is a decision.

**Candidates for a second round of paper playtests** (21 October; `docs/plan.md`, 1f+), beside the first seven: football club, band, observer, family saga, journalist, murder mystery, and an RPG role. The candidates were nine: the postal carrier, the restorer, the town photographer and archivist, the Courier's editor or the Anchor's landlord, the councillor or planner, the town doctor, the café owner, a child growing up, and the house itself. Recommended for round 2, these four have the strongest loops on what exists today:
1. **The Courier's editor**, the information game. It uses the engine's most distinctive data.
2. **The postal carrier**, routines and absences, paired with a slow mystery.
3. **The restorer**, which tests criterion 1 directly through play.
4. **The town photographer**, time and records as play.

Two hybrids to try: the photographer as the journalist's tool; the postal carrier as the way into the murder mystery (`README.md`, Combinations). The ideas are in `roles.md`, `mysteries.md` (The round), `groups.md` (The venture) and `lives.md`. The first round stopped at 11 of 24 runs, and no second round has run.

**Seven games built on reading a world,** ranked by whether anyone would want to play them, then by how cleverly they use the engine. None has been built or played. The precedents and rules behind them are in `docs/research/game-precedents.md`.
1. The Traitors, with the town as host (`multiplayer.md`).
2. The ghost in the cemetery (`inquest.md`, Other ghosts).
3. The forger (`outlaws.md`).
4. The smuggler on the prohibition coast (`outlaws.md`).
5. Columbo in a town that remembers (`mysteries.md`).
6. The band (`groups.md`).
7. Heirs: friends inherit one town (`lives.md`).

**Building a group,** five concepts ranked by fit with the engine: the band, the club, the crew, the venture, the family. The band is the recommendation, with the venture as its home base (`groups.md`, The band; the family is in `lives.md`).

**Inquest:** the ghost and the board of inquiry are one game with two modes (`inquest.md`, Other shapes it could take).

**The paper playtest panels** each ranked the seven concepts of round 1 and named hybrids to try, before the sessions: `docs/playtests/paper-1/panel/experience.md`, `systems.md` and `narrative.md` (Ranking; Hybrids). Their hybrids are listed in `README.md` (Combinations).

## Sources

Game-ness: [Juul, The Game, the Player, the World (Level Up, 2003)](https://www.jesperjuul.net/text/gameplayerworld/).

Read through the GitHub API, read-only, on 21 October: Understory's `WHY.md`, `README.md`, `SUMMARY.md`, `src/setting.ts`, `src/body.ts`, `src/families.ts`, and `src/situations/danger.ts`, `temptation.ts` and `discovery.ts`; and `fixtures/engine/understory-world-9989.json`.

- Managers: [Football Manager](https://en.wikipedia.org/wiki/Football_Manager); [FM attributes (passion4fm)](https://www.passion4fm.com/football-manager-player-attributes/); [Motorsport Manager (motorsport.com)](https://www.motorsport.com/general/news/motorsport-manager-the-game-by-racing-fans-for-racing-fans-740431/740431/); [Rock Star Ate My Hamster](https://en.wikipedia.org/wiki/Rock_Star_Ate_My_Hamster); [Rock Manager](https://en.wikipedia.org/wiki/Rock_Manager); [Game Dev Tycoon review](https://www.useapotion.com/2020/10/game-dev-tycoon-review/).
- Lives: [The Sims 2](https://en.wikipedia.org/wiki/The_Sims_2); [The Sims 3](https://en.wikipedia.org/wiki/The_Sims_3); [Crusader Kings III](https://en.wikipedia.org/wiki/Crusader_Kings_III); [Sylvester, The Simulation Dream](https://gamedeveloper.com/design/the-simulation-dream); [How RimWorld fleshes out the Dwarf Fortress formula](https://gamedeveloper.com/design/how-i-rimworld-i-fleshes-out-the-i-dwarf-fortress-i-formula); [Dwarf Fortress](https://en.wikipedia.org/wiki/Dwarf_Fortress); [King of Dragon Pass](https://en.wikipedia.org/wiki/King_of_Dragon_Pass); [Ultima NPC schedules](https://lycaeum.ultimacodex.com/npc-schedules/); [Wildermyth review](https://gideonsgaming.com/wildermyth-review-a-legendary-fable/).
- Reading: [Pentiment](https://en.wikipedia.org/wiki/Pentiment_(video_game)); [Disco Elysium](https://en.wikipedia.org/wiki/Disco_Elysium); [Kentucky Route Zero](https://en.wikipedia.org/wiki/Kentucky_Route_Zero); [Citizen Sleeper 2 (NPR)](https://www.npr.org/2025/01/30/g-s1-45425/citizen-sleeper-2-gareth-damian-martin); [Outer Wilds](https://en.wikipedia.org/wiki/Outer_Wilds); [Return of the Obra Dinn](https://en.wikipedia.org/wiki/Return_of_the_Obra_Dinn); [Heaven's Vault (Emily Short)](https://emshort.blog/2019/07/23/heavens-vault-inkle/); [Her Story](https://en.wikipedia.org/wiki/Her_Story_(video_game)); [Unpacking at GDC 2022](https://www.gamedeveloper.com/gdc2022/gdc-2022-unpacking-a-narrative-through-1-000-household-items); [Ian Dallas on Edith Finch](https://www.godisageek.com/2017/04/interview-with-ian-dallas-creative-director-on-what-remains-of-edith-finch/).
- Watching: [The AI of Hitman (2016)](https://www.gamedeveloper.com/design/the-ai-of-hitman-2016-); [How Townscaper works](https://www.gamedeveloper.com/game-platforms/how-townscaper-works-a-story-four-games-in-the-making).
- Role-playing: [Larian on Baldur's Gate 3's reactivity](https://malaysia.news.yahoo.com/larian-gave-baldurs-gate-3-022539159.html); [Divinity: Original Sin II](https://en.wikipedia.org/wiki/Divinity:_Original_Sin_II); [Sawyer on New Vegas (GameBanshee)](https://gamebanshee.com/kwwc8); [Planescape: Torment](https://en.wikipedia.org/wiki/Planescape:_Torment); [Quest design of The Witcher 3 and Cyberpunk 2077](https://www.gamedeveloper.com/marketing/10-key-takeaways-from-the-quest-design-of-cyberpunk-2077-and-the-witcher-3); [Kingdom Come: Deliverance](https://en.wikipedia.org/wiki/Kingdom_Come:_Deliverance); [KCD II's reputation (GamingBolt)](https://gamingbolt.com/kingdom-come-deliverance-2-features-a-reputation-system-kuttenberg-detailed); [Pathologic 2](https://en.wikipedia.org/wiki/Pathologic_2); [Persona 5](https://en.wikipedia.org/wiki/Persona_5); [Behind the design of Persona 4](https://www.siliconera.com/behind-the-design-of-persona-4/); [Stardew Valley](https://en.wikipedia.org/wiki/Stardew_Valley); [Kamurochō](https://en.wikipedia.org/wiki/Kamuroch%C5%8D); [Yakuza 0](https://en.wikipedia.org/wiki/Yakuza_0).
- Mysteries: [Shadows of Doubt (PC Gamer)](https://www.pcgamer.com/uk/shadows-of-doubt-is-a-wildly-ambitious-murder-mystery-set-in-a-fully-simulated-sci-fi-city); [Shadows of Doubt review (GameCritics)](https://gamecritics.com/gc-staff/shadows-of-doubt-review/); [Shadows of Doubt review (Progameguides)](https://progameguides.com/shadows-of-doubt/shadows-of-doubt-review-indie-at-its-finest/); [The Case of the Golden Idol](https://en.wikipedia.org/wiki/The_Case_of_the_Golden_Idol); [Golden Idol's testing (Game Developer)](https://www.gamedeveloper.com/road-to-igf-2023/-the-case-of-the-golden-idol-i-used-frequent-testing-to-improve-its-mystery-solving); [Paradise Killer (PC Gamer)](https://pcgamer.com/how-a-new-indie-studio-created-one-of-the-best-detective-games-ever/); [Bad News (UCSC Expressive Intelligence Studio)](https://eis.ucsc.edu/media-experiences); [Ryan's dissertation, read through Emily Short](https://emshort.blog/2019/05/23/curating-simulated-storyworlds-james-ryan-2/).

Gaps: Bad News and Talk of the Town are known only from search summaries, and the dissertation's own page did not render. Two Point and Night in the Woods were not researched. Kingdom Come's GDC talk would not open. The shared web-search budget ran out before the Talk of the Town paper was found.
