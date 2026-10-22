# A role or a trade in the town

Ideas, not decisions: no game is chosen (`NOW.md`). Every idea is catalogued in `README.md`; this page holds the full detail of this family's ideas.

## In short

- Games where the player has a job in the town and the job is how they read it: **the paper** (option 5 of `first-game-options.md`, with the editor's rumour game and the journalist), **the restorer** (option 3, with the restoration architect), **the observer, the photographer and the archivist** (with social archaeology), **the town doctor**, **the town's politics** (the councillor and the movement), and **a role in the town**, the playable role of the paper playtests.
- The postman and the paper boy are in `mysteries.md` (The round), since their round leads into a mystery.
- Øystein's read (21 October) on the postal carrier, the restorer and the photographer: "sounds a bit boring, but ok". It is in full in `README.md` (Combinations), with how each is tested inside a stronger game.

Costs are rough weeks of the weekly usage limit, the plan's own unit, before the architecture. The criteria are the five in `CLAUDE.md` (What it is for). Claims about other games are sourced in `first-game-options.md` (Sources). A "fit today" names how well world 9989, the real run, carries an idea now.

## The paper

### The game (option 5)

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

### The Courier's editor or the Anchor's landlord: rumour and information

- *The loop.* You hear who told whom and decide what to print or pass on. What the town believes shifts, and people's lives follow.
- *What it uses.* The engine's `tell` events and visibility; records that may be wrong; evidence, not verdicts.
- *Fit today (world 9989).* Very strong: 112 `tell` events, the Courier and the Anchor all exist.
- *Risks.* It must stay humane, with no cruelty games (Rule 8).
- *Nearest games.* Bad News, Prom Week, Papers, Please, Suzerain.

After Øystein's read (21 October), the Courier's editor stays a standalone candidate: deadlines, a rival paper, printing about people you know, and a town whose beliefs shift with every edition.

### The journalist, from the real run

From the four games the run supports (`stories-in-the-world.md`). The Courier has an editor, reporters, deadlines and a visit from head office. The player writes what the town reads; a report is a record that can be wrong. **What carries it:** records (request 9); accounts against traces; the paper's own "plan to go online and stop the Saturday print" (pack 33). The journalist fits the engine's own institutions best (the Courier, the council's plans, the harbour day), and records would switch it on.

### Elsewhere in the repo, for the paper

- The paper playtest's card is *Thursday's Paper* (`docs/playtests/paper-1/cards/journalist.md`); its outcome is in `README.md` (status).
- The camera as the journalist's tool, whose photos are evidence that can be printed: `README.md` (Combinations).
- Rival reporters racing on one case: `mysteries.md` (The casebook).
- The prototype "the paper against the eye": `docs/research/playtesting.md` (section 10).
- Levers for its fun, with the obituarist: `docs/research/fun.md` (section 7, The paper).
- The panels' hybrids that join it to the death (the obituarist, the Courier's beat, the reporter who covers deaths): `README.md` (Combinations).

## The restorer

### The game (option 3)

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

### The restorer, as a candidate for round 2

- *The loop.* Read a house's history layer by layer (coats, parts by era, ghost signs, a bricked window), then restore it truthfully, or not.
- *What it uses.* The fabric systems, the coat stack, parts dating a place, criterion 1 directly.
- *Fit today (world 9989).* Medium: our own fabric facts carry it, and the engine's homes come later.
- *Risks.* The craft can turn into a chore. It needs owners with lives and opinions.
- *Nearest games.* House Flipper, Unpacking, Pentiment.

### The restoration architect

One of the ideas that pass the spreadsheet test in Overstory's reading of the open notebook (20 October 2026; `game-layer-ideas.md`, What each idea asks of Overstory). You take on an old building or a block. You work out why it changed, which traces are original and which were later, and what to keep. The building system becomes the game: the coat stack is the evidence, the era shelves are the vocabulary, and a careless 1970s window is a clue and a choice. In the interface study the archivist and the restorer share one dial setting: records and traces, phase views from conservation practice (a colour per period, a dashed outline for what is gone, no colour for the undated), and conjecture drawn looser (`docs/research/interface-and-inspection.md`, section 7).

### Elsewhere in the repo, for the restorer

- The paper playtest's card is *Old Town* (`docs/playtests/paper-1/cards/restorer.md`), lives on only; the playtest's method calls it the observer reshaped as a game (`docs/playtests/paper-1/method.md`). Its status is in `README.md`.
- The prototype "the inherited house": `docs/research/playtesting.md` (section 10).
- Levers for its fun: `docs/research/fun.md` (section 7, The restorer).
- Restoration as a thread in the family saga, and the loft that joins it to the band: `README.md` (Combinations).

## The observer, the photographer and the archivist

### The observer

From the four games the run supports (`stories-in-the-world.md`). Learn a street's routines, notice what changes, ask why, keep a journal. **What carries it:** habits as timetables; the change query; the aligned toggle. The observer is cheapest on today's engine, because habits and their breaks already carry causes. Its five verbs (look, inspect, ask why, compare, keep) and its recommended play choices are designed in `docs/research/interface-and-inspection.md` (section 7, The observer game; For Øystein to decide); they stay defaults while no game is chosen (`NOW.md`). As a game, the observer was reshaped into the restorer (above).

### The town photographer and archivist

- *The loop.* Photograph the town and its people across years. The archive is your game: exhibitions, the paper, comparing in place. Your photos become records in the world.
- *What it uses.* Time, the toggle in place, records, the player's acts changing the world.
- *Fit today (world 9989).* Strong outdoors.
- *Risks.* It needs goals beyond collecting: commissions, a book, a mystery in the archive.
- *Nearest games.* Umurangi Generation, Pentiment, Here.

### The town archivist

One of the ideas that pass the spreadsheet test in Overstory's reading of the open notebook (20 October 2026; `game-layer-ideas.md`, What each idea asks of Overstory). A photograph, a deed, an old newspaper, a family name. You rebuild lives across generations from records that disagree, with the houses as one source among the papers. Traces cannot lie; records can, and the game is in the gap.

### Social archaeology

One of the ideas that pass the spreadsheet test in Overstory's reading of the open notebook (20 October 2026; `game-layer-ideas.md`, What each idea asks of Overstory). You arrive decades after a place changed and work out what it used to be: closed businesses, faded posters, renovated houses, a street widened halfway. The fabric pass's output is the level.

### Elsewhere in the repo, for the observer and the photographer

- The camera as the journalist's or detective's tool: `README.md` (Combinations).
- The prototype "a roll of film": `docs/research/playtesting.md` (section 10).
- The photograph held up at its spot, and the archivist's and restoration architect's comparison in play: `docs/research/time-on-screen.md`.

## The town doctor

- *The loop.* House calls across decades. You know families through generations, read homes and routines as signs, and diagnose from accounts that may be wrong.
- *What it uses.* Illness, ageing, grief, habits, homes and care, evidence.
- *Fit today (world 9989).* Medium: the clinic and illness events exist.
- *Risks.* Sensitive: privacy and dignity first; no misery tourism.
- *Nearest games.* Pathologic 2.

## The town's politics

### The councillor or planner

- *The loop.* Write the town's plans and rules (a square, a road, a demolition) and live with the consequences over decades: empty shops, a worn path, a protest.
- *What it uses.* The town system's dated plans, time jumps, the fabric.
- *Fit today (world 9989).* Medium: plans are ours until the engine has them.
- *Risks.* Abstract unless the consequences are personal and visible.
- *Nearest games.* Suzerain, Democracy, Frostpunk's laws.

### The movement *(old game)*

From *Republic: The Revolution* (2003). A country of individually simulated citizens was promised, and the game shipped late and cut down. Here you start with nobody and win the 1991 council election, recruiting person by person through who knows whom, across neighbourhoods of different class. Multiplayer: rival candidates. The details of the old game are from memory and are checked before the idea is built on.

What the town must give its politics (the town hall, the conservation fight, the bridge, the newspaper, the oil money) is in `docs/town-plan.md` (A city to play in).

## A role in the town

The seventh concept of the paper playtests: a role in the living town with Baldur's Gate 3-like reactivity, whose acts and relationships play out over years. Its card is *Word Gets Round* (`docs/playtests/paper-1/cards/rpg.md`); its status is in `README.md`.

Why the town can carry a role-playing game, and what it costs, is under option 4, the role-playing game of a life and its heirs (`lives.md`, Is there a role-playing game here?). Any of the six options can also be played as a role with a body in the town; the dials change, not the world. The systems panel's "the role as a dial" and the narrative panel's "the band as a role" are in `README.md` (Combinations).
