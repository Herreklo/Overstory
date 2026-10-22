# Ideas for the game layer

Status: ideas, not decisions; no game is chosen (`NOW.md`). The first six sections were collected from two external reviews of the Person Model Lab (October 2026) and discussion. The later sections gather what several game ideas share: what if, shown; records; what each idea asks of Overstory; the games that only read a finished history; and what the reading games need from the engine. The catalogue of ideas is `README.md`.

## In short

- **Promises** are remembered by the person they were made to, and tested years later.
- **Chemistry** is discovered by trying, never calculated; a replacement does not inherit it.
- **The rehearsal room** is a pressure cooker: the player shapes conditions and does not control people.
- **Legendary and successful** are two kinds of progress, and legend comes only from causal events.
- **People become important** before you know it.
- **Fun** must feel like discovery, agency and recognition, all three.
- **What if, shown:** one saved history, one changed decision, two towns side by side.
- **Records** are dated objects with a maker and a purpose, and can be wrong; they age like surfaces.
- **The fabric and records** are needed by nearly every idea.
- **Two games only read a finished history**; the others need player actions in the engine, rated Hard.
- **Seven engine needs** of the reading games, first written as requests 11 to 17 elsewhere, are mapped below to `docs/engine-requests.md`; five are not yet requested.

## Promises matter more than contracts

The player's promises become part of the simulation's memory. A promise made to a nineteen-year-old ("the band stays independent") is remembered by the person it was made to, and may be tested years later by an offer that would break it. Reputation is the sum of what people remember you promised, not what the contracts say. The core already has promises as small obligations; this would make them durable commitments with context and expectation.

## Chemistry is discovered, not calculated

A group's work comes from how its people fit, not from their skills added up. The best musicians are not always the best band. A replacement does not inherit the chemistry of the person they replace. The player finds out what works by trying: rehearsals, recordings, performances, conversations.

## The rehearsal room is a pressure cooker

Not a music mini-game: the place where the group's personalities collide. The player shapes conditions (shorten the session, bring someone in, talk to one person, stay out of it) and does not control the people. Constant intervention protects the group from conflict but stops it learning to work together; staying out lets resentment grow unnoticed.

## Legendary without successful

Two kinds of progress that are not two currencies: achievement (records, money, fame) and meaning (the night everyone remembers, the record that influenced others). A band can be either, both, or neither. Legend must come from causal events and relationships, never from awarding points to emotional moments.

## People become important before you know it

The teenager in the front row at the first show becomes the critic who decides the band's story twenty years later. Their opinion was shaped by moments the player barely remembers. Nothing about it is predetermined; their life was in the simulation all along.

## What fun must feel like

Three things the player must experience repeatedly:
- Discovery: "I think I understand this person."
- Agency: "My decision changed what happened."
- Recognition: "I remember when that started."

Discovery alone is an observation simulator. Agency alone is an optimisation game. Recognition alone is a moving story the player is not responsible for.

## A first playable slice

The first gig, a band slice of one album cycle with a jump back to the same venue, is in `groups.md` (The band).

## The test that matters

Put the prototype in front of ten people who know nothing about the implementation. Ask what happened, whom they liked, whom they trusted, which decisions they regret. Success sounds like "I knew that guitarist was trouble" or "I shouldn't have made that promise". Failure sounds like "interesting, but I can't tell how my choices mattered".

## What if, shown: the counterfactual observatory

One saved history, one changed decision, two versions of the same street side by side. The diff between the two towns' plans becomes a view: what changed, and what the town resisted.

It runs through other ideas. A group game can show at its end what would have happened if you had kept the drummer (`groups.md`, Our edge). Inquest proves each hole by running the world again without it (`inquest.md`). The prototype "the favour and its twin" shows the town without the player's favours after a jump (`docs/research/playtesting.md`, section 10). An aligned toggle between two playthroughs at one date is the same machinery as one record at two dates (`docs/research/time-on-screen.md`).

## Records follow the world's rules

- Each record is a dated object with a maker and a purpose, and it claims facts that may be wrong (`docs/living-world.md`, What the player can know).
- Records age like surfaces: sun-faded, rain-streaked, pasted over. A venue's wall is a coat stack of its gigs.
- Their words come last, from a grammar, and never invent a cause.
- A record that only restates a fact (a poster for a booked gig) is drawn by Overstory. A record that can be wrong (the paper's report) is an account, so it comes from the engine (`docs/engine-requests.md`, Records).
- Records go wrong in six ways: omission, bias, composite (several events merged), decay, sealing (locked for years) and self-suppression (the subject kept it out). The gap between a record and the event is the case (`docs/research/game-precedents.md`, rule 2).

## What each idea asks of Overstory

A game idea uses Overstory when the player's main act is reading the world: a street, a room, a person, a record. If the idea would play as well as a spreadsheet, the world on screen is decoration, and the idea belongs to the engine's side. These columns are the ideas of the Understory × Overstory open notebook (20 October 2026), a shared bank of game ideas for both projects.

● needed, ○ helps. A judgement, not a measurement; it changes as the ideas do.

| System | Music game | Detective | Restoration | Archivist | Social archaeology | Anthology | Scene builder | Journalism | Festival | Hotel |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Fabric through time (buildings, streets, coat stack) | ● | ● | ● | ● | ● | ● | ● | ○ | ○ | ● |
| Records (posters, papers, signs, directories, photos) | ● | ● | ● | ● | ● | ○ | ● | ● | ● | ○ |
| People (bodies, clothes, ageing) | ● | ● | ○ | ○ | ○ | ● | ● | ● | ● | ● |
| Interiors | ● | ● | ● | ○ | ● | ● | ● | ○ | | ● |
| World view and maps | ● | ● | ○ | ● | ● | ○ | ● | ● | ○ | ○ |
| Crowds and stage light | ● | | | | | ○ | ● | ○ | ● | ○ |
| Nature with history | ○ | ● | ○ | ○ | ● | ○ | | | ○ | |

Read across: the fabric and records are needed by nearly every idea; crowds and stage light by few. The building and history system is the most reusable thing either project makes, which is why it comes first. Records are the cheapest next shared system: mostly type, paper, ink and layout by era, and on every street they double as set dressing (posters, signs, notices in windows).

The festival and the hotel appear only in this table; no page describes them further.

## Games that read a finished history

Two of the seven games built on reading a world only read a finished history, so they can start on a snapshot once the front door's part two (#22) lands: the Traitors, with the town as host (`multiplayer.md`) and Columbo (`mysteries.md`). The other five need player actions to go back into the engine, which `docs/research/reality-check.md` rates Hard. Inquest is reachable for the same reason: every change is precomputed, so a case is a finished set of runs that the player reads (`inquest.md`, Is it possible?).

## What the reading games need from the engine

These needs come from the Traitors with the town as host, the ghost in the cemetery, the forger, the smuggler, Columbo, the band, Heirs, Inquest and the group games. They were first written as engine requests 11 to 17 on the branch where Inquest was kept, and those numbers clash with `docs/engine-requests.md`. They are not filed. This section keeps their wording, and says which current request covers each, or "not yet requested". `docs/engine-requests.md` is unchanged.

Most rest on the accounts arc (#20): people keeping their own version of what happened, with its source and confidence. It is the single engine change that most of those games share.

| Was | Need | Current request |
| --- | --- | --- |
| 11 | Records as accounts | 9 (Records). The six ways records go wrong are not spelled out in 9. |
| 12 | The archive of a source | Partly 1 (people as the player could know them; how each holder knows each event) and 9. An export per source: not yet requested. |
| 13 | Who could contradict a claim | Not yet requested. It would read on 1's holders. |
| 14 | Deaths with a moment | Not yet requested. Nearest: "Crime and its aftermath" among the playtest bundle's candidates (After the playtests), and 28 for where and when. |
| 15 | Branching from a checkpoint | Not yet requested. `docs/research/playtesting.md` says Understory's `clone.ts` copies a world exactly and `whatif.ts` measures what one choice changes three years on (The Week in `mysteries.md` rests on the same), so part of this may already exist. |
| 16 | Things in events | Partly 17 (goods as things) and 20 (small acts on things). Objects in any event: not yet requested. |
| 17 | Moments in focus | Not yet requested. It touches 1 (habits as timetables) and 28; LW2 in `docs/living-world.md` leaves the month boundary open. |

The needs in their own words:

- **Records as accounts.** A record is an account written down by someone with a purpose: a parish register, a newspaper report, a police file, a gravestone, a letter, a diary. It has a maker, a date and a stake, and it can be wrong in the ways real records are: something left out, a slant, two events merged into one, decay, sealed for years, or kept out by the person it is about. The record of events stays the truth; records are what the town wrote about it. The player would see two papers disagree about one death, and the gap between them is the case.
- **The archive of a source.** Everything one source could hold about one event or person: what the register, the paper, the police and a neighbour each have, as separate exports. It extends "people as the player could know them" (#22) from people to sources. The player would see each friend at the table holding a different, true part of the story.
- **Who could contradict a claim** (the liar's ledger). Given a claim (someone was at the quay that night; this letter is in her hand), the people alive and the records that would contradict or confirm it, each with the account behind it. The player would see a lie or a forgery hold until it meets the one person who was there.
- **Deaths with a moment.** Deaths today come from age and illness, each with its reasons, and an unmade amends becomes a regret on the record. Add deaths that happen at a moment involving other people (an accident at sea, a choice someone made, help that did not come), with who was present and what could have changed it. The player would see a grave whose cause points to a day worth returning to.
- **Branching from a checkpoint.** Run one world twice from the same month, with one decision changed, and return what differs between the two records. Each person already draws from their own random stream, so a change should move others only through real causes; this makes that a feature the player can use. The player would see a saved life change some graves and leave the rest of the cemetery as it was.
- **Things in events.** The objects an event involved and who had them: a coat taken from a rack, a spare key lent and never returned, a ladder taken away for welding, a part ordered and left on a shelf. Small things are how a death gets its odd details, and how one person's slip becomes another's hole. The player would see a body in someone else's coat, and the coat would be a true fact with a history.
- **Moments in focus** (`moments-in-focus.md`). Pressure builds over months, but ruptures happen in a moment. Each month, find the moments where pressure meets a situation (strained people at the same dinner, funeral or gig), expand them to hours from people's habits, resolve them as events with causes, and commit what matters back to the month. An outcome never depends on whether the player is watching. The player would see a marriage end at one dinner, with who said what and who was in the room.

Beside them, from the casebook: **secrets as facts,** who hides what from whom, not yet requested (`mysteries.md`, The casebook).

**A case checker is Overstory's own.** Given the archives a player could hold, it checks against the truth that a case can be solved, and solved only when the archives are pooled. It reads the truth through the front door, as our other tools do, and never reaches a player. Inquest's checker and the casebook's solver are the same tool (`inquest.md`, Generating a case; `mysteries.md`).

## Open questions

- Which of these could share the music game's town without bending it?
- How much of a record can be generated before reading it feels like reading a template?
- What does a player do with a record that turns out to be wrong: is finding the error the reward?
