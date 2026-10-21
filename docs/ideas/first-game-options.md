# The options for the first game

Status: ideas, not decisions. Øystein decides which game comes first; this page prepares the choice. It feeds the paper playtests (plan step 1f+) and tells the greybox (1g) what to test. Written on Opus, October 2026.

## What this is for

Overstory is a world for many games. The first should answer Overstory's question best: can someone read people and history better from the world on screen than from the engine's page? Two tests hold together:
- **A game, not a walking simulator** (`CLAUDE.md`, Øystein, 21 October). Every option has goals, challenge, stakes, mastery, failure, and decisions that cost something. Reading the world is a skill that pays off in play, as deduction does in Obra Dinn or scouting in Football Manager, never the whole of it.
- **The town is not decoration** (`worlds-on-screen.md`). If the game would play as well as a spreadsheet, the world on screen adds nothing.

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

### Option 1: The club

**The game.** You run a harbour town's football club in the lower leagues from 1989. The players are amateurs with day jobs at the cannery, the harbour and the oil base. The week is long and the match short.

**Core loop.** Two training evenings, the Saturday match, the Anchor after. Between them you find players where talent is unmeasured (school sports, the estate's sports hall), keep a squad together round shifts, families and injuries, and deal with the board and a sponsor.

**Dials.** Control: the team sheet, training, tactics, the club's money. Influence: players' choices (to sign, stay, train after a night shift), the board, the sponsor. Knowledge: your own squad well, as evidence; other clubs and the town thinly.

**Time.** Weeks inside a season that runs spring to autumn; the dark winter is the off-season, a natural jump. Seasons for decades, as in a long Football Manager save.

**The game in it.**
- *Goal:* the board's target each season, then promotion; a club that survives and grows.
- *Resources:* a small budget, two training evenings, your own evenings (one spent at a player's door is one not spent scouting), and promises: a job found, a place kept.
- *Opponents and pressure:* other clubs, the fixture list, the board's patience, a sponsor tied to the town's firms, and players' lives: the cannery closes, a striker takes the oil base's shifts.
- *Fail states:* relegation, the sack, debts, the club folding; a promise broken and remembered.
- *Mastery:* seeing who will hold up (shifts, a new baby, drink) before form shows it; finding unmeasured talent; tactics. Early seasons are survival, later ones building a squad over years. Reading the town is the scout's edge.

**Needs.**
- *World:* the Mudbowl in the railway's valley (planned, not built), a clubhouse, players' homes and workplaces, match-day streets and crowds.
- *Engine:* aptitudes, work, accidents, groups and contests for a place exist. Needed: a club as a group kind in the pack (the shape exists), sporting skills that rise and fall with age, and a match model. A result is a fact, so the model must be the engine's or a portable library it adopts (as request 19 proposes for derived works). Homes (#59) for the lives round the squad.
- *Interface:* players as acts with counts, never rating words; a team sheet; a match view.

**Only here.** A squad that is the town. The striker's week at the cannery shows on Saturday. The 1989 captain's son trains with the club in 2010, and you know him. The ground keeps the club's history: a stand built with oil money, sponsor boards that change with the town's firms.

**Risks.** The core decisions don't need the town on screen, and Football Manager proves the page carries the genre. Twenty-two people moving well is work after the people step.

**Cost on top of the plan.** 16 to 26 weeks: the match model, the match as staged moments (floodlights, the crowd as one organism), the league, the ground, scouting.

**Criteria.** 1 some; 2 strong (players across seasons, fathers and sons); 3 some; 4 some; 5 strong (match day across the town).

**Greybox.** The corner has no pitch, so test the town side. A boy kicks a ball against D's boarded wall every evening; three men's shifts change after the cannery news (fixtures, `authored`). After three evenings, can a player say who is worth approaching and who will miss Saturday, and be right?

### Option 2: The band

**The game.** You manage a band formed in 1989 in the loft on Harbour Row, for as long as it lasts: Understory's origin game and the shared milestone (request 8).

**Core loop.** Find people where music leaks out (a choir, a wedding, the pub; `talent-discovery.md`) and bring them together. Then shape conditions without controlling anyone: book the loft and the gigs, spend the money, make promises that are remembered (`game-layer-ideas.md`). The members' lives decide the rest.

**Dials.** Control: the manager's own acts (bookings, money, the van). Influence: each member's choices, starting with the first command, an invitation to a rehearsal, which the engine accepts or refuses. Knowledge: the band deeply but as evidence; the scene thinly.

**Time.** Weeks inside an album cycle of about eighteen months, then jumps of years back to the same venue. A career may run to a reunion in 2020, or end in 1991.

**The game in it.**
- *Goal:* the band's own ambition, set with its members: the big hall, a record deal, the crowd it draws (the engine's own measure), or lasting at all. Success and legend are counted apart.
- *Resources:* money (the loft's rent, the van, studio days), bookings, your evenings, and promises that are remembered.
- *Opponents and pressure:* rival bands for gigs and players, venues that close, landlords, money running out, the members' jobs, partners and children.
- *Fail states:* the band splits; debts; the loft lost; a member's life damaged by the push.
- *Mastery:* reading chemistry before it shows as rows; booking the right room at the right time; knowing when to step in and when to stay out.

**Needs.**
- *World:* the loft and the Anchor (both on the corner's street), a venue ladder, poster walls as coat stacks of gigs, the van, the walk home at three.
- *Engine:* the band as a group kind, contests for a place with the loser's answer, and shows exist; the real run holds four bands and 32 shows in ten years. Planned: the band for a year, homes, the first command. Later: cheap space (10), places that close (4), records (9).
- *Interface:* commands with their reasons, clocks for plans and debts, no trait labels even for your own band.
- *Music:* agents can't make the songs (`reality-check.md`), and there is no commission budget.

**Only here.** A band's history written on the town. The loft was cheap after the crash and is lost when flats go up. The one who wasn't picked turns up in the front row, or in a rival band. The reunion plays the same address, now another business.

**Risks.** Borrowed-sounding songs leave a hollow heart; the ways out are Øystein and local musicians, free licences, or music shown only through rooms, crowds and accounts (untested). The engine's band year has not run, and most of its events still lead nowhere (Understory's summary).

**Cost on top of the plan.** 12 to 20 weeks, plus the music: venues and gigs as scenes, the business (deals, radio, records), posters.

**Criteria.** 1 some; 2 strong; 3 strong (who wasn't chosen; the loft lost); 4 strong; 5 some (gig crowds).

**Greybox.** Invite a musician to the loft; the fixture accepts or refuses, with its reason. A week later, is the trace readable: who comes late, who leaves first, whose window is lit? Does a refusal feel like a person deciding or a dice roll?

### Option 3: The restorer

Reshaped from "the return", a photographer's visits, which was mostly looking. Its verbs (look, inspect, ask why, compare, keep, the photograph held at its spot) become the reading layer every option shares and the greybox's base. Here they pay off in money and houses.

**The game.** You come back to the town in 1989 with a small inheritance, three years after the crash, when old houses are cheap. You buy, restore, let and sell houses in the old town, and decide what of each to keep.

**Core loop.** Find a house worth buying and read it: what is original, what was changed, what is rotten, who the neighbours are, what the council's plans say. Buy at a price, choose the works and the crew, then let or sell. A wrong reading costs money.

**Dials.** Control: your money, your houses, the works. Influence: owners who may sell, tenants, neighbours, the council, crews. Knowledge: what you can see and inspect, records (deeds, plans, the archive's photographs), what people tell you.

**Time.** Months per project, years across the game, through the oil years' booms and slumps.

**The game in it.**
- *Goal:* a portfolio and a name; a street kept, a fortune made, or both.
- *Resources:* money and credit, crews of different skill, time before the rot spreads or the market turns.
- *Opponents and pressure:* rival buyers and developers, the council's plans and rules, the market, decay, objecting tenants and neighbours.
- *Fail states:* bankruptcy; a house condemned; a protected front stripped and fined; tenants pushed out who turn the street against you.
- *Mastery:* dating a window from across the street; seeing rot under paint; knowing which owner will sell, and when; reading the market.

**Needs.**
- *World:* the house generator and live rebuilds (the C# port), coats, works as sites, archive photographs.
- *Engine:* no buildings, owners or prices yet. Until it has them, the facts contract keeps owners, construction and works ours (`derived`, `authored`); requests 5, 10, 14, 23 and 24 hand them over later. The player's works become facts like anyone's.
- *Interface:* the field guide as a working tool; the photograph and compare; a ledger.

**Only here.** Criterion 1 as the core skill: a house's history read right is money, read wrong a loss. Your works change a street others live in: convert the warehouse loft, and a band loses its room.

**Risks.** Buildings matter more than people, so the engine's strength is underused. Prices and markets are the engine's domain, and building them here would make Overstory the engine (the pre-mortem's third story). It could tip into a decorating toy.

**Cost on top of the plan.** 12 to 20 weeks: the economy, works as commands with crews and costs, hidden condition as facts, the council's rules, a ledger.

**Criteria.** 1 strongest; 2 some (owners and tenants across years); 3 strong (what your works did to a street); 4 strong; 5 some (the street as the market's map).

**Greybox.** House D, empty since 1986: a budget, three inspections, an asking price. Buy or not, and choose two works. Then jump to 1995. Did players who read the traces right do better than those who did not?

### Option 4: A life and its heirs

**The game.** You play one resident, born around 1971 into a family in the old town, through acts years apart. When your character dies, or the next generation comes of age, you go on as a child: Persona's calendar inside an act, Pentiment's jumps between, Crusader Kings' succession. This is the family across generations, played as a role-playing game.

**Core loop.** An act is a season of evenings. Each evening is spent on a person or a place: your father at the Anchor, a friend's band, overtime, the house. What you do is an event, remembered by whoever saw it. Between acts the world runs, and you return to what your choices and other lives made.

**Dials.** Control: one person's acts (work, evenings, moving, the house's works). Influence: family and friends, through what they see you do. Knowledge: a resident's, with the family's own stories, which may be wrong.

**Time.** Acts of a season, years apart (1989, 1995, 2003, 2011, 2020); generations across the game.

**The game in it.** Without set goals this is The Sims, which Juul counts as borderline. So every act carries a dated goal.
- *Goal:* each act's: the mortgage due in March, a parent who needs care, a job to keep, a child through school. Across the game, a family and a house that last.
- *Resources:* a season's evenings, money, health, goodwill.
- *Opponents and pressure:* the calendar, the town's economy (the cannery, oil), rivals at work, the family's own wants.
- *Fail states:* the house sold, a bond broken, a parent left alone, debts, the family gone from the town.
- *Mastery:* seeing what each person needs before they say it; spending evenings where they count; planning a decade ahead.

**Needs.**
- *World:* interiors (step 8, pulled forward); people ageing on screen (step 5); the family house changed live by its works.
- *Engine:* the player's character with many commands (none exist yet); homes (#59); facts as dated intervals (33); body and work over a life (34); rites with who came (31); wants for later life (round 43); the two clocks settled, so an evening commits back to the month.
- *Interface:* a calendar, relationships as acts with counts, a family journal.

**Only here.** Your own traces in a street you watch age. A parent growing old, and a child who looks like you. A consequence that lands a decade later where you can see it.

**Risks.** The largest scope. The engine's own weakness hits it hardest: thirty years move a person only about 3% toward being someone else, and nearly half of adults pursue nothing in ten years (Understory's summary). Written scenes make conversation the expensive part.

**Cost on top of the plan.** 24 to 40 weeks.

**Criteria.** 1 strong (your own house); 2 strongest; 3 strong; 4 some; 5 little.

**Greybox.** The family in house C: six evenings, then a jump to 1995. Do players know their family again from silhouette, place and habit? Does an evening spent with someone show later?

### Option 5: The paper

**The game.** You are the reporter on the town's weekly paper from 1989. Each week an edition: what you chase, whom you ask, what you print and what you leave out.

**Core loop.** Leads come from the town: a shop dark two Saturdays running, a council plan, talk at the Anchor. You watch, ask and read records, then write, choosing each claim and its source. Printed, the piece is a record in the world: read, believed, resented. A source stops talking; a shop loses custom.

**Dials.** Control: your own work and the edition. Influence: publication, which the engine takes as a record people act on. Knowledge: sources, records, what you saw.

**Time.** Weekly editions; a year as a volume; jumps of years across a career, to the paper's decline.

**The game in it.**
- *Goal:* the paper's sales and survival; stories before the rival paper; a record that stands.
- *Resources:* days to the deadline, column space, each source's trust, the editor's patience.
- *Opponents and pressure:* the rival paper, the council, owners and firms who push back, the weekly deadline.
- *Fail states:* a false claim printed (a correction, a source burned, a threat of libel), a story missed, readers lost, the paper closing.
- *Mastery:* whom to trust and how far; finding the lead in the town before anyone tells you; when to print and when to wait.

**Needs.**
- *World:* much of the town, since a reporter goes everywhere (step 6 moves earlier); a newsroom; records in each era's type.
- *Engine:* accounts, witnesses and the council's plans in words exist. Needed: records (9), who told whom (1), plans as documents (23), and publication as a command.
- *Interface:* a notebook, source marks, the edition as the player's own page.

**Only here.** A record the player made, living in the world: your 1991 mistake in the archive and in people's memories.

**Risks.** Its output is text, so the page can win; the screen must matter for finding the story. A true story can be cruel: the game shows the consequences and passes no verdict, and no story targets anyone for who they are (Rule 8).

**Cost on top of the plan.** 12 to 18 weeks.

**Criteria.** 1 some; 2 some; 3 strong; 4 strong but at risk; 5 strong.

**Greybox.** The café in house A, opened in 1988: watch it for five days, then say whether it is in trouble and why. Is the player right against the record, and did watching beat reading?

### Option 6: A death in the town

**The game.** Someone has died, and what happened is unclear. You read the town to find out: the dead person's life, the people round them, the records, and the traces in the world over the years. Certainty may never come.

**Dials.** The town's detective, with records and a warrant to search; a relative who doubts the inquest, or a mortician's assistant finding the next of kin (Bad News), would set knowledge differently. Control: your own acts. Influence: asking, searching, accusing; people decide what to tell. Knowledge: witnesses and records, never the truth during play.

**Core loop.** The death is found at the foot of the gully steps on a November morning. You walk the town, watch, ask and read. Each claim goes on the case board with its source, content and reliability shown apart (as in Shadows of Doubt). What a witness saw is the engine's; what they tell you is an account, which may be mistaken or a lie. You give your account to the inquest, the family or the paper, who decide on the evidence, as in Paradise Killer.

**Time.** Weeks in 1989, then acts years apart in Pentiment's shape. In 1997 a house is renovated and a witness has moved. In 2012 it is a cold case: witnesses aged or dead, the 1989 police photographs held up where they were taken.

**The game in it.**
- *Goal:* an account of what happened that holds: at the inquest, with the family, and against the record shown when the case closes.
- *Resources:* days to the inquest; questions, each an act others hear of; each person's trust; warrants.
- *Opponents and pressure:* the clock; evidence that decays (rain, a house renovated, a witness who moves away); rumours your own questions start; people who lie to keep a secret.
- *Fail states:* the wrong person blamed, which the engine carries on (they lose work and friends); the inquest rejects your account; a source burned; the case closed open.
- *Mastery:* the sifter picks harder chains as you improve: more people with causes, more lies, older evidence. Case by case you read routines and traces faster, judge accounts better, and ask without tipping anyone off.

**What the engine can decide.** People die only of age and illness, at Norwegian rates. Work accidents (the saw, a car, going over the side) injure but never kill. There is no crime, no violence beyond words, no police and no inquest. The real run agrees: four deaths in ten years among 119 people, all of age or illness, sixteen skims, nobody hurt by anyone. So the option grows in steps:
- *Now:* a death the engine makes, as an open question. Why was he on the quay at two in the morning? Perhaps a heart attack after the night he was let go, and a life that explains it. Bad News shows a death without a crime can carry the game.
- *Next:* fatal accidents, and risks taken for money, with their causes.
- *For murder:* a rare act of harm with weighed causes, concealment tied to places and things, where and when (28), the police, inquest and paper as makers of records (9), and who told whom (1). New requests, filed only if this option is chosen.

**As a game on today's engine.** With only natural deaths, the question is not who killed him but what happened and who is answerable: who let him go that afternoon, who took the till money he was blamed for, who did not call for help. The engine already has what makes this a contest: skimming, lying to cover, blaming, secrets that get out. The stakes are blame, not guilt, and the opponents are people protecting their secrets. It is a smaller game, close to Bad News with Pentiment's ending, and the paper playtest must show that it holds.

**If murder is requested.** The game gains a true opponent: a person in the engine with a reason to hide, who lies, removes a trace, leaves town or turns suspicion on someone else. The arrest becomes the costliest decision, and a trial tests the account. The Rule 8 guard weighs more.

**Rule 8, without sensation.** The death is never shown; only its absence and aftermath: the empty seat at the Anchor, the funeral and who came (31). The sifter picks deaths from chains in lives, never by sex, ethnicity, orientation or class, and no victim type recurs. Suspicion comes only from causes in the record. Grief is part of the case.

**Repeatable without going stale.** Shadows of Doubt wears through learned patterns, templated documents, cases that fizzle or fall open, and a closing form. Here:
- the case is a life, not a template: the sifter picks a death with a rich chain, more than one person with a cause;
- most deaths are not murders, and the player knows it, so "what happened" never presumes "who did it";
- evidence is drawn from the record into the world (a worn path, a window lit at three, a sign changed); written records are few, each with a maker and a purpose;
- a solver checks before play that the main facts can be learned from what a player can reach, and that no single clue gives them away;
- no form at the end, but an account given to someone, with consequences; then the record, marked as the record, scores it fact by fact (who, where, when, why), never a verdict on anyone's character, as the interface study allows after a chapter;
- the town ages between cases, so a detective's career is a long save among people already known.

**Needs.** The town at several dates, scene state by hour, records, a few interiors; the case board, the photograph, the journal.

**Only here.** Evidence that is the town's history: when this window was changed, who wore that path, who stopped coming on Fridays. A cold case read through a town that changed.

**Risks.** Players expect a murderer, and a natural death may feel like a cheat. Generated cases can be unfair. Interviews are written scenes, the expensive part.

**Cost on top of the plan.** 14 to 22 weeks: the sifter and the solver, the board, records, interviews, the inquest, the acts.

**Criteria.** 1 strong (a house as a witness); 2 strong (Obra Dinn's identification as play); 3 strong; 4 strongest, since not being misled is the game; 5 little.

**Greybox and paper playtest.** In the corner: three evenings of blockout routines, then a death at the foot of the steps, three days to the inquest and three questions a day. Each question is heard of by others (fixture, `authored`). The player gives an account, and the record scores it. On paper: one case from a real death in world 9989 (a heart attack at 76), with accounts drawn from its events, beside one murder built by hand and labelled `authored`. Does the case without a culprit hold as a game? Where does the board become a chore?

## 3. Is there a role-playing game here?

Yes: option 4. The role-playing games bring four things the town can use. Time is a budget (Persona, Pathologic); consequences come late and visibly (The Witcher 3); companions have goals and judge you (Divinity); one dense place lasts across eras (Yakuza). They also bring a cost the town can't pay: reactivity authored line by line (Baldur's Gate 3). Ours comes from the engine's memory of who saw what. Any of the six can also be played as a role with a body in the town; the dials change, not the world.

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

Game-ness, after Juul's six features, the challenge and mastery curve, and the stakes:

| Option | Juul's six | Outcome that is won or lost | Challenge and mastery curve | Stakes | Rank |
| --- | --- | --- | --- | --- | --- |
| The club | all six, and proven | league place, promotion, the club's survival | survival, then building a squad; scouting and reading people sharpen | the club, your job, promises | 1 |
| A death in the town | all six with the scored close; the outcome is weak without it | the inquest's finding, scored against the record | the sifter raises difficulty by chain; reading and asking sharpen | an innocent blamed, trust, the case | 2 |
| The restorer | all six | money, houses, a street kept | from one cheap house to a street; reading buildings sharpens | money, houses, the street | 3 |
| The band | all six, the outcome softer | crowds, money, survival, legend counted apart | first gig to a career; reading chemistry sharpens | the band, debts, members' lives | 4 |
| The paper | all six | sales, stories won, corrections | leads to investigations; judging sources sharpens | the paper, sources, reputation | 5 |
| A life and its heirs | borderline without each act's goal | each act's goal; the family's fate | weak; little to get better at | the house, the family | 6 |

## 5. Recommendation

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
