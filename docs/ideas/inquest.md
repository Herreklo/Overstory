# Idea: Inquest

Status: idea, not a decision; no game is chosen (`NOW.md`). It is one form of a death in the town (`README.md`; the other forms are in `mysteries.md`). A worked case for a paper test is in `docs/ideas/inquest-case-1.md`. The precedents behind it are in `docs/research/game-precedents.md`.

The idea was written with its own engine requests, numbered 11 to 17. Those numbers clashed with `docs/engine-requests.md`, so this page now names the current request where one covers the need, and says "not yet requested" where none does. The requests' full text is kept in `game-layer-ideas.md` (What the reading games need from the engine).

## In one line

You are a ghost with one very specific death, your own. Work out every hole that lined up to kill you, then go back and close one, and see what the town became because of it.

## What it should feel like

- **At first, a mystery.** A body in the harbour in someone else's coat. A watch that stopped half an hour before anyone found it. It looks like murder.
- **Then, an investigation.** Documents disagree. A witness remembers the wrong man. A newspaper leaves out the one thing that mattered. The player builds the night piece by piece.
- **Then, a turn.** Nobody killed you. Everybody did a little: a borrowed key, a broken lamp, a ladder at the welder's, a sister who had been laughed at once and would not call again. "It was all of them, and none of them."
- **Last, a choice.** You can close any one hole. Each one saves you, and each one changes other lives. The cemetery in 2019 shows who you saved, and who you didn't.

It should feel like Return of the Obra Dinn's deduction, with the weight of Our Town's third act: going back to an ordinary day, and seeing it.

## How it plays

### The case

Every case starts from one death with specific, odd details: where the body was found, what it was wearing, what was missing, what time the watch stopped. Each odd detail is a thread. The details are true facts from the world, never decoration.

### The model: holes that line up

Accident investigators use James Reason's Swiss cheese model: an accident happens only when the holes in several layers of defence line up. Some holes are acts on the night; others are conditions that waited for months. Inquest makes the model the game. A death has four to six holes, each owned by a different person. Close any one and the victim lives.

### Phase one: the inquiry

The player fills in a board of questions (why was he on the pier, why that coat, why did nobody call), each answered in their own words. The game confirms answers two at a time, never one alone, so guessing does not pay.

The evidence comes from three places:
- **Records:** police reports, logbooks, minutes, newspapers, letters, diaries. Each has a maker, a date and a stake, and records go wrong the way real ones do: something left out, a slant, two people merged into one, a page torn out.
- **The Afterward:** the town thirty years later. Graves, a parish register, an old woman in a care home who remembers half of it.
- **Returns:** the ghost can go back and watch a moment of the past year. Each return spends energy that does not come back, so the player chooses carefully. Returns confirm; documents deduce.

### Phase two: the change

With the board solved, the player spends returns to make changes, one at a time. Each change is a small act through a person: ask for a key back, walk a drunk man home, help carry a ladder, answer a sister at a funeral. The engine runs the town forward from that change, and the player walks the Afterward again.

**Ripples.** Everything that differs from the last Afterward is marked: a grave gone, a grave added, a house painted another colour, a shop still open. Any difference can be followed back through its causes to the change that made it.

**No right answer.** Every reachable change saves the victim. They differ in what else they do. One kills someone else. One saves a stranger years later. One mends a family. The game knows the smallest change, and can show how a player's choice compares, as Sherlock Holmes Consulting Detective compares a player's route with Holmes's. It never says which future is right.

## What makes it ours

**The engine tests every hole.** A hole is a cause the death needed. Because the world is deterministic, the engine can prove that: run the world again from before the cause with that one thing changed, and see whether the death still happens. Accident investigators can only argue about counterfactuals; this engine can run them. So every hole on the board is true, and every ripple in the Afterward is caused by the player's change and nothing else. Each person already draws from their own random stream, so a change spreads only through real causes.

**The case is generated, and changes every time.** A new seed is a new town, a new death and a new chain.

**The town is the noise.** Red herrings are not written. They are the true events around the victim that the death did not need: a debt, a raised insurance policy, a row about pay. The engine proves they were not causes, so the game knows they are herrings while the player does not.

## Generating a case

1. **Find the death.** Run the town and sift its record for deaths with four or more holes, each owned by a different person, at least one shared root (a person or a condition under several holes), and at least one odd detail (an object in the wrong place).
2. **Prove the holes.** For each candidate cause, branch the world without it. If the victim lives, it is a hole. This is also how the herrings are found: true, suspicious, and not needed.
3. **Write the records.** Each record is an account by someone who was there or was told, with their stake and their errors (records as accounts: request 9, Records, in `docs/engine-requests.md`; the six ways records go wrong are in `game-layer-ideas.md`). Words come last, from a grammar, and never invent a cause.
4. **Check that it is fair.** A case checker, reading the truth, makes sure every board answer rests on at least two independent pieces of evidence the player can reach, and that no wrong answer is better supported than the right one. Knox's and Van Dine's fair-play rules for detective fiction, the ones that still make sense, become checks.
5. **Find the changes.** For each hole, search the months before the death for acts the victim could take as a person, branch each one, and keep the ones that save them. Keep a case only if its changes differ in what they do.
6. **Precompute.** All branches are run when the case is made, not while the player waits, so a case is a pack: the seed, the death, the records and the Afterwards.

**Variety.** Deaths come from the sea, fire, roads, cold, illness and neglect, and the holes from the town's real economy, buildings and habits. Two cases share a kind of death but never a chain. Shadows of Doubt's reviewers found the same email in every office; records written from accounts, by different makers with different stakes, keep that from happening. Causes of death never include self-harm.

## Multiplayer

The case works as a round-table game for three to five players. The same round table for any death, with the town as host, is the Traitors, with the town as host (`multiplayer.md`).

- **Split archives.** Each player holds a different, true part of the evidence: the official records, the town in 2019, the family's letters, the returns. No one can solve it alone. This is The Past Within and the co-op card games that keep winning the Spiel des Jahres, with a simulated town as the source.
- **The Traitor.** One player is secretly the Tide, who wins if the inquiry records the wrong cause or commits a change that fails. Their best tools are the true herrings: the debt, the coat, the row. This is The Traitors and Blood on the Clocktower, where the lies are built from real evidence and the engine holds the truth.
- **Shared returns.** The team shares one budget of returns, and the round table votes on what to spend it on.
- **Share codes.** A case is a seed and a record of choices, so a group can play the same case and compare their futures, with no servers.

## Other shapes it could take

| Shape | What it is | Verdict |
| --- | --- | --- |
| The board of inquiry | The same game for any accident, not only the player's death: a cannery fire, a ferry that ran aground, a roof that fell. The player is an investigator. | A strong sequel or mode. Wider, but loses the ghost's personal stake. |
| The hand-over | One player causes the death without knowing it, by living a year in the town; a friend investigates it thirty years on. | The most original, and the furthest away: it needs player actions into the engine during a whole year. |
| Fate against the inquiry | Asymmetric: one player is Fate, moving through the past to keep the holes lined up, while the others close them, as Deathloop lets one player invade another's loop. | Exciting, but live, real-time and hard to balance. Later, if ever. |

The ghost and the board of inquiry are one game with two modes. That is the recommendation.

## Other ghosts

Two earlier forms of the ghost were written in other rounds of ideas. Each keeps what is its own.

### The ghost in the cemetery

**Pitch.** A ghost with no memory of its own death. The graves speak, and their epitaphs contradict each other. Enter a grave, return to the day that person died, change one small thing. Each return costs energy you cannot get back. Your own death is the last case, and only the lives you changed can solve it.

**The moment.** You save a fisherman. When you come back, his grave is still there, with a later date and a different cause, and his daughter's grave has appeared beside it.

**Why it works.** Spoon River Anthology's dead who speak and disagree, Ghost Trick's minutes before death, and Russian Doll's ending, where the loop breaks only when two people save each other. Every grave is a true fact, so the cemetery is a level select made of causes. A saved life changes its grave rather than erasing it, which keeps death from becoming trivial (Our Town's third act: returning to a life should hurt).

**Engine.** The engine already draws each person's choices from their own stream, so one change moves others only through real causes. Deaths already carry their reasons, and a wish to make things right becomes a regret on the record: the mourners' murmurs exist. Grow toward: deaths with a moment someone could change, and branching a world from a checkpoint (both not yet requested).

**Weakness.** Today's deaths come from age and illness; few have a moment worth returning to.

**Cheapest test.** Branch one fixture world at one death, change one decision, and diff the two cemeteries thirty years on. It dies if the change reaches everything (noise) or nothing (no game).

It was second of the seven games built on reading a world (`first-game-options.md`, section 7, Other recorded rankings).

### The ghost who cannot act *(old game)*

From *Murdered: Soul Suspect* (2014), which wasted its premise, and *Ghost Trick* (2010). You died in 1989. You cannot act, only be near and nudge: a draught that opens a letter, a light that flickers. Years pass, and grief moves through your family and the house (`stories-in-the-world.md`, A death, and grief). The goal: the truth found before the last person who knows it dies.

It was written as a connection in the old games' round (`README.md`, Combinations and connections).

## Precedents: what we take, what we change

| Game | What we take | What we change |
| --- | --- | --- |
| Return of the Obra Dinn (2018) | Reconstructing deaths; confirming answers in groups | The deaths are generated, and you can undo them |
| The Case of the Golden Idol (2022) | Filling in a frozen moment in your own words | The moment has a before and an after you can visit |
| The Sexy Brutale (2017) | Saving people from their deaths inside a loop | No authored puzzle per death; the chain is the town's |
| Ghost Trick (2010) | A ghost who goes back to the minutes before a death | The ghost reads the whole year, not four minutes |
| Outer Wilds (2019) | Only knowledge carries over | Returns are limited and spent deliberately |
| Twelve Minutes (2021) | A loop around one fatal night | Its warning: repeating the same steps killed the fun. Here returns are short visits, not replays |
| Hitman | Replaying one situation for different solutions | The solutions are generated and proven |
| Sherlock Holmes Consulting Detective (1981) | Being scored against the best route | The best route is computed by the engine |
| Shadows of Doubt (2023) | Generated cases in a simulated city | Its warning: repeated text breaks the spell |
| The Traitors, Blood on the Clocktower | A liar among the investigators, using true evidence | The engine is the referee |
| Spoon River Anthology (1915) | The dead of a town, contradicting each other | The graves are true, and change |
| Reason's Swiss cheese model (1990) | Accidents as holes lining up | The holes are proven by running the world again |

## Has it been done?

The parts have. Obra Dinn and Golden Idol reconstruct deaths; The Sexy Brutale and Ghost Trick save people from them; Shadows of Doubt generates cases. Each is either authored or unchecked. No game found generates a death, proves its causes by running the world again, and lets the player change one cause and see the true consequences decades later. That combination needs a deterministic simulation of people, which is what Understory is.

## Is it possible?

| Step | What it needs | When |
| --- | --- | --- |
| Paper test | Case 1 and a facilitator | Now |
| One authored case on screen | The case as fixtures; the Afterward and changes precomputed by hand; Overstory's cemetery, board and records | After LT2 |
| Engine-made case | Deaths with a moment (not yet requested), records as accounts (request 9), branching from a checkpoint (not yet requested), things in events (partly requests 17 and 20), the case checker (Overstory's own) | When the accounts arc (#20) is unpaused |
| Generated cases on demand | Story sifting (7), cases generated in packs | Later |

The ghost never acts in the world except through a chosen change, and every change is precomputed. So, unlike most ideas on our list, Inquest does not need live player commands: a case is a finished set of runs that the player reads. That makes it more reachable than it looks.

## Risks

- **The holes must be readable.** If the chain is too long or the holes too abstract, it reads as a spreadsheet. Four to six holes, each a person and a moment.
- **Generated sameness.** If cases rhyme too much, players will feel the template. Variety of deaths, makers and stakes is the defence, and it has to be measured across many seeds.
- **Fairness.** A generated case that cannot be solved, or can be solved by keyword matching, kills trust. The case checker is not optional.
- **Cost.** Every case needs dozens of branches run thirty years forward. Precomputed packs keep it off the player's machine, but the cost per case has to be measured.
- **Tone.** Deaths, drinking and grief need care. Nobody is a villain, and no cause is self-harm.

## The first two tests

1. **The paper test** of case 1, solo and as a group with a Traitor. It answers whether the inquiry and the choice are good play.
2. **The ripple test** in the engine: branch a fixture town at one death, remove one cause, and run thirty years. It answers whether a change spreads to a few lives, rather than none or all.
