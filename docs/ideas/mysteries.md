# Mysteries and investigation

Ideas, not decisions: no game is chosen (`NOW.md`). Every idea is catalogued in `README.md`; this page holds the full detail of this family's ideas.

## In short

- **A death in the town** is one idea in five forms: the death on today's engine (option 6 of `first-game-options.md`), the casebook, the long inquest, Columbo, and Inquest, the ghost who closes a hole (its own pages, `inquest.md` and `inquest-case-1.md`).
- **The Week** loops one week of 1989 to stop what happens on Sunday. **Shenmue, fulfilled** looks for someone who vanished years ago. **The round** reads the town from a daily route, as a postman or a paper boy.
- Their multiplayer modes that stand alone are in `multiplayer.md`: the Traitors with the town as host, one of them is a player, the daily case.
- An idea marked *(old game)* starts from an older game that reached for something its tech or its time could not give. The details of the old games are from memory and are checked before any idea is built on them.

Costs are rough weeks of the weekly usage limit, the plan's own unit, before the architecture. The criteria are the five in `CLAUDE.md` (What it is for). Claims about other games are sourced in `first-game-options.md` (Sources).

## A death in the town

### The game on today's engine (option 6)

**The game.** Someone has died, and what happened is unclear. You read the town to find out: the dead person's life, the people round them, the records, and the traces in the world over the years. Certainty may never come. On the real run (`stories-in-the-world.md`), the player reads the dead person's routines, money and ties from the street and from accounts: whom they leaned on, who wrote what, who stayed away.

**What carries it** (`stories-in-the-world.md`): absences in the dead person's routines, accounts with tellers, the hat that goes round at the Anchor, the headstone, the house left behind.

**Dials.** The town's detective, with records and a warrant to search; a relative who doubts the inquest, or a mortician's assistant finding the next of kin (Bad News), would set knowledge differently. Control: your own acts. Influence: asking, searching, accusing; people decide what to tell. Knowledge: witnesses and records, never the truth during play.

**Core loop.** The death is found at the foot of the gully steps on a November morning. You walk the town, watch, ask and read. Each claim goes on the case board with its source, content and reliability shown apart (as in Shadows of Doubt). What a witness saw is the engine's; what they tell you is an account, which may be mistaken or a lie. You give your account to the inquest, the family or the paper, who decide on the evidence, as in Paradise Killer.

**Time.** Weeks in 1989, then acts years apart in Pentiment's shape. In 1997 a house is renovated and a witness has moved. In 2012 it is a cold case: witnesses aged or dead, the 1989 police photographs held up where they were taken.

**The game in it.**
- *Goal:* an account of what happened that holds: at the inquest, with the family, and against the record shown when the case closes.
- *Resources:* days to the inquest; questions, each an act others hear of; each person's trust; warrants.
- *Opponents and pressure:* the clock; evidence that decays (rain, a house renovated, a witness who moves away); rumours your own questions start; people who lie to keep a secret.
- *Fail states:* the wrong person blamed, which the engine carries on (they lose work and friends); the inquest rejects your account; a source burned; the case closed open.
- *Mastery:* the sifter picks harder chains as you improve: more people with causes, more lies, older evidence. Case by case you read routines and traces faster, judge accounts better, and ask without tipping anyone off.

**What the engine can decide.** People die only of age and illness, at Norwegian rates. Work accidents (the saw, a car, going over the side) injure but never kill. There is no crime, no violence beyond words, no police and no inquest. The real run agrees: four deaths in ten years among 119 people, all of age or illness, sixteen skims, nobody hurt by anyone. So the idea grows in steps:
- *Now:* a death the engine makes, as an open question. Why was he on the quay at two in the morning? Perhaps a heart attack after the night he was let go, and a life that explains it. Bad News shows a death without a crime can carry the game.
- *Next:* fatal accidents, and risks taken for money, with their causes.
- *For murder:* a rare act of harm with weighed causes, concealment tied to places and things, where and when (request 28), the police, inquest and paper as makers of records (9), and who told whom (1). New requests, filed only if this idea is chosen.

**What a murder would need, in full** (`stories-in-the-world.md`). The engine's worst acts are taking a little at work, covering up a mistake, letting someone else take the blame and running a rival down. A murder mystery would need, within Rule 8:
1. A death with a human cause. An act family for harm, rare and weighed like the others, would take its intent from states the engine already has: a rivalry, a debt, a secret about to come out.
2. A place and a time (request 28), so who could have been there is a question the record answers.
3. Who saw and who was told (request 1), so accounts can be independent.
4. Lies that hold. The engine has `liecover` and `allfine`; a suspect's account must be able to be false and stay consistent.
5. Things with owners (request 17), so an object can place a person.
6. An accident that can kill. The setting already has "went over the side" and the storm. A fatal fall at the harbour, sometimes with someone nearby, asks the oldest small-town question: did he fall?

Overstory must not grow its own crime simulation (`docs/research/pre-mortem.md`). This is a request to the engine, and its scope is Øystein's call. Until then *Bad News*'s frame works on today's run. Andy Shaw's death leaves money two friends gave him, a disputed song, a feud ended three months before, a band that lost him, and a roof another man helped with.

**As a game on today's engine.** With only natural deaths, the question is not who killed him but what happened and who is answerable: who let him go that afternoon, who took the till money he was blamed for, who did not call for help. The engine already has what makes this a contest: skimming, lying to cover, blaming, secrets that get out. The stakes are blame, not guilt, and the opponents are people protecting their secrets. It is a smaller game, close to Bad News with Pentiment's ending, and the paper playtest must show that it holds.

**If murder is requested.** The game gains a true opponent: a person in the engine with a reason to hide, who lies, removes a trace, leaves town or turns suspicion on someone else. The arrest becomes the costliest decision, and a trial tests the account. The Rule 8 guard weighs more.

**Rule 8, without sensation.** The death is never shown; only its absence and aftermath: the empty seat at the Anchor, the funeral and who came (31). The sifter picks deaths from chains in lives, never by sex, ethnicity, orientation or class, and no victim type recurs. Suspicion comes only from causes in the record. Grief is part of the case.

**Repeatable without going stale.** Shadows of Doubt wears through learned patterns, templated documents, cases that fizzle or fall open, and a closing form: its cases come from templates and its documents repeat. Here:
- the case is a life, not a template: the sifter picks a death with a rich chain, more than one person with a cause. Cases come from chains, never from types (request 7): the café's six attempts, the till and the boat;
- count kinds, fold repeats: the engine's readers reward lives with more kinds of happening, and its pages repeat the festival, the hat and "count me in", so a sifter prefers chains of many kinds and folds the repeats;
- most deaths are not murders, and the player knows it, so "what happened" never presumes "who did it";
- evidence is drawn from the record into the world (a worn path, a window lit at three, a sign changed); written records are few, each with a maker and a purpose;
- a solver checks before play that the main facts can be learned from what a player can reach, and that no single clue gives them away;
- some cases end in "?": Arthur's debt and Harry's theft cannot be solved (`stories-in-the-world.md`, section 3). Saying so is honest and keeps solving from becoming routine;
- no form at the end, but an account given to someone, with consequences; then the record, marked as the record, scores it fact by fact (who, where, when, why), never a verdict on anyone's character, as the interface study allows after a chapter;
- the town ages between cases, so a detective's career is a long save among people already known. The same street holds different chains in 1989 and 1999, so a town that moves forward does not run out;
- the player's own traces: their acts enter the record and the fabric like anyone's (`docs/research/time-on-screen.md`, The player's own traces), so a later case can involve them.

**Needs.** The town at several dates, scene state by hour, records, a few interiors; the case board, the photograph, the journal.

**Only here.** Evidence that is the town's history: when this window was changed, who wore that path, who stopped coming on Fridays. A cold case read through a town that changed.

**Risks.** Players expect a murderer, and a natural death may feel like a cheat. Generated cases can be unfair. Interviews are written scenes, the expensive part.

**Cost on top of the plan.** 14 to 22 weeks: the sifter and the solver, the board, records, interviews, the inquest, the acts.

**Criteria.** 1 strong (a house as a witness); 2 strong (Obra Dinn's identification as play); 3 strong; 4 strongest, since not being misled is the game; 5 little.

**Greybox and paper playtest.** In the corner: three evenings of blockout routines, then a death at the foot of the steps, three days to the inquest and three questions a day. Each question is heard of by others (fixture, `authored`). The player gives an account, and the record scores it. On paper: one case from a real death in world 9989 (a heart attack at 76), with accounts drawn from its events, beside one murder built by hand and labelled `authored`. Does the case without a culprit hold as a game? Where does the board become a chore?

**Elsewhere in the repo.**
- The paper playtest's card for it is *Answerable* (`docs/playtests/paper-1/cards/mystery.md`); its outcome is in `README.md` (status).
- The greybox prototype of this form is called "the inquest" in `docs/research/playtesting.md` (section 10), beside "a human culprit" and "asking costs". It is not the ghost game Inquest below.
- Levers for its fun: `docs/research/fun.md` (section 7, A death in the town).
- What the town must give a murder mystery: `docs/town-plan.md` (A city to play in).
- Moss as the forensic clock, clues from the wear model, and first snow: `docs/research/nature.md` (the detective in the forest).
- The paper playtest panels' hybrids that join it to the paper: `README.md` (Combinations).

### The casebook

Øystein, 22 October, on the board games that could become our game: "actual a good idea. this could work very similar as well. The big thing is the story and mystery though, but maybe would could do this in a very clever generative way?"; "something fun for multiplayer stuff would also be nice."

**The model: Sherlock Holmes Consulting Detective.** A case, a map of the city, a directory of addresses and the day's newspaper. Each visit to an address costs time and gives a paragraph to read. At the end, questions, scored against how few visits Holmes needed.

**Adjusted for our town.**
- The town is the map and the directory, and every address is a real simulated household with its history.
- The newspaper is printed from the engine's events, and it can be wrong (perceived information).
- Reading from above and from the street is free. It tells you which doors are worth a visit, and a visit costs days.
- Mastery is solving with fewer visits, as in Return of the Obra Dinn.
- It sharpens the death in the town above.

**The mystery, generated.**
- **Simulate, then sift.** The engine runs the town for years. A sifter then searches the record for an event that makes a good case: several people with a motive and an opportunity, and traces spread over the town. The craft is already studied (`docs/research/behaviour-on-screen.md`, section 7: Ryan's story sifting, Kreminski's Felt and its Cozy Mystery Construction Kit, where each witness reads the same events by their own values). Ryan's Talk of the Town and Bad News are the nearest research towns (`first-game-options.md`, section 1).
- **Red herrings from true secrets.** Many people hide things unrelated to the case.
- **Fair by machine.** Before a case is offered, a solver checks that the reachable evidence gives one answer, and counts the fewest visits needed: the score to beat.
- **The nearest game is Shadows of Doubt (early access 2023).** It plans each citizen's day and logs every sighting as a fading memory (`behaviour-on-screen.md`). Its generated city is praised and its cases called random in motive (to be checked). Our motives come from developed lives.
- **The city as evidence,** true to the facts (`CLAUDE.md`, five kinds of thing on screen). Where someone grew up decides where they go and what they hide (`docs/town-plan.md`, TP6).

**Multiplayer.**
- **Co-op:** players split up to cover addresses on a shared clock, then argue the answer.
- **Rival reporters:** two players race on one case. A questioned witness clams up; a tip leaks into tomorrow's paper (the paper, `roles.md`).
- **The culprit is a player:** in `multiplayer.md` (One of them is a player).
- **A daily case:** in `multiplayer.md` (The daily case).

**What it would need from the engine.** In `docs/engine-requests.md`: how each holder knows each event, and habits as timetables, so sightings follow routines (1); story sifting (7); records such as the paper, which can be wrong (9). Not yet requested: secrets as facts, who hides what from whom.

### The long inquest: time is your lever

A death in 1989 that the town will not talk about. You can investigate now, or jump years ahead. The man people feared dies and tongues loosen; letters surface in an estate sale; there is a deathbed account. But the house was renovated, the witness emigrated, and memories fade and drift. Choosing *when* to look is the core decision, and no other game has a town that truly goes on living.

Multiplayer: two investigators in different decades, as in *The Past Within* (Rusty Lake, 2022). What the 1989 player files, photographs or tells someone is what the 2009 player can find.

It joins the death in the town and the casebook with jumps. It was written as a connection in the old games' round (Øystein, 22 October: "Now look at connections - could we combine stuff for a truly unique but potential amazing experience?").

### Columbo in a town that remembers

**Pitch.** You watch the death happen. Then you prove it, from a town where every witness has an account and every account has a source.

**The moment.** The proof turns on a trace nobody thought about: worn steps that say someone came every night.

**Why it works.** Inverted detection fits a simulation that always knows the truth. Knox and Van Dine's fair-play rules become a check that a generated case is fair.

**Engine.** Now: a TRUTH snapshot (#22). Grow toward: accounts (#20), records as accounts (request 9). It is one of the two of the seven games built on reading a world that only read a finished history (`game-layer-ideas.md`, Games that read a finished history), and was fifth in their ranking (`first-game-options.md`, section 7).

**Weakness.** Players say they prefer hand-made mysteries. The case must prove it is fair.

**Cheapest test.** One printed case from a fixture death: shown the culprit, can a player build the proof from the archive in 30 minutes?

### Inquest: the ghost who closes a hole

You are a ghost with one very specific death, your own. Work out every hole that lined up to kill you, then go back and close one, and see what the town became because of it. The full idea, with its board of inquiry mode, its earlier and other ghosts, and its multiplayer, is in `inquest.md`; a hand-built case for a paper test is in `inquest-case-1.md`.

## The Week *(old game)*

From *The Last Express* (1997) and *Majora's Mask* (2000). One week in 1989 repeats, and something terrible happens on Sunday. Each loop you learn more routines and use them to change the ending. Understory can copy a world and run it on (`clone`, `whatif`), so the loops are exact. A replayed week is dense, which answers the arithmetic risk in `docs/research/fun.md` (about one notable event a week).

**The Week, together.** Two to four players live the same looping week as different residents (the postman, the barmaid, the kid, the priest), each seeing a slice, and pool the notebook between loops. Optionally one player causes Sunday, loops too and learns too, as the invader does in *Deathloop* (2021): cat and mouse across loops (`multiplayer.md`, One of them is a player).

See also Inquest's precedents (`inquest.md`), where Twelve Minutes is kept as a warning about replaying the same steps.

## Shenmue, fulfilled *(old game)*

From *Shenmue* (1999). The harbour town of 1986 had routines for everyone, and the town was only a backdrop. Here you arrive looking for someone who vanished years ago: odd jobs at the harbour, asking around, people who remember you and talk to each other. The town is the plot.

## The round: the postman and the paper boy

### The postal carrier

**The loop.** Daily routes through the town. You notice routines and their breaks: mail piling up, a light not on, a new name on a door. Letters and parcels are records.

**What it uses.** Habits and their breaks (the strongest signal in the behaviour research), visibility, records, the outdoor town.

**Fit today (world 9989).** Strong: habits tied to places exist; no interiors needed.

**Risks.** Too passive without a hook. Pair it with a slow mystery or with small acts of care.

**Nearest games.** Lake, Death Stranding, Papers, Please.

Øystein's read (21 October) put it with the restorer and the photographer: "sounds a bit boring, but ok". The postal round is tested as the way into the murder mystery (`README.md`, Combinations).

### The paper round *(old game)*

From *Paperboy* (1985). You are 13 in 1989 with a paper round. The route is the daily loop, and you see everything: who stopped taking the paper, whose car is outside at six. Over the year, a mystery only a kid would notice.
