# Answerable (the mystery): setup, lives off

What every lives-off run of the mystery shares. Arm folder `b`, cohort X (`arms.md`). Game masters, auditors, analysts and the lead read it; players never do. Everything an off game master needs from the card is restated here, so the card's lists of the real run's events are not needed.

**Read only** this page, `world/world-9989-off.md` and `world/world-9989-off.json`, `world/engine-rules.md`, and the cast tables of `world/atlas-9989.md` (people, households, places, who lives where). Never the real run's lives, causes, records or storylines.

**Look facts up** with the off lines only:

    python3 -I world/tools/lives_off.py person "NAME" FROM TO | sed -n '/^  OFF$/,$p'

The tool prints the real run's lines first; the `sed` keeps only the off section. Always give it `person` and a name (run with no arguments, it rebuilds the JSON). Town year = engine year − 37. Event ids below are the off world's.

**Who plays.** Pre-registration amendment 1 cuts the mystery to kinds 2, 4, 5 and 6, with no cold start: X2, X4, X5 and X6 play here, each with the pitch and tutorial. All six starts are written; starts 1 and 3 have no run this round. Each run's own truth is in `b/<id>/gm.md`.

**The off world** (`world-9989-off.md`): the same people, births, deaths, jobs, households, partners, arrivals and departures, bands and dates, with generic doings in place of lives. Nobody has reasons, nothing carries, routines never lapse, there is no illness in the two years before a death, and the town has no past. Asked why, a person has none to give. A routine's start year is not reliable (some fall before the person's birth): never cite a start year or a duration from one.

## 1. The clock

| Round | Dates | Turns | What it covers |
| --- | --- | --- | --- |
| 1 | Mon 3 to Fri 7 March 1997 | 4 | Case 1, Mary Tanner. The opening is the evening of Monday 3 March. |
| 2 | Mon 10 to Fri 14 March 1997 | 3, then the hearing | The check is open (once). Turn 4 is the hearing, Friday 14 March at ten. |
| jump | 19 months | | To Monday 26 October 1998. Andy Shaw died on Wednesday 14 October. |
| 3 | Mon 26 Oct to Fri 6 Nov 1998 | 4 | Case 2, Andy Shaw. Opens where round 1 opened (section 9). |
| 4 | Mon 9 to Fri 20 Nov | 4 | The check is open (once, rounds 4 to 6). The memory probe ends this screen. |
| 5 | Mon 23 Nov to Fri 4 Dec | 4 | |
| 6 | Mon 7 to Fri 11 Dec | 3, then the hearing | Turn 4 is the hearing, Friday 11 December at ten. Then the tenth hour and the exit. |

A player names a day and a time of day (morning, afternoon, evening) for each act, in order. Acts can't go back in time, and the round's last day is its last.

**Authored days** (`authored`, logged SETUP once):
- Mary Tanner died on Monday 10 February 1997, at home: the house on the church hill where Mark Holmes lives. The screens never say who owns it. D-03′ ran on Thursday 13 February, the funeral was on Wednesday 19 February at eleven, and C-32′ ran on Thursday 20 February.
- **The quiz night** at the Anchor that Trevor Myers and Andy Shaw win (e-12132, March 1997) is on Friday 7 March 1997, in the evening.
- Andy Shaw died on Wednesday 14 October 1998, at home on the Gully Steps. D-04′ and C-35′ ran on Thursday 22 October. The funeral is on Tuesday 27 October at two, at the churchyard on the church hill, and Pirate Radio play at the Anchor afterwards.
- **Andy's evening walk**, every evening of case 1: out at about half past five, down the Gully Steps to Harbour Row, along the quay to the shore, and back up the steps at about seven (his shore-walk routine). It puts him alive in every start.
- Both hearings are held upstairs at the council office on Market Square, at ten.
- The Courier comes out on Thursdays. Its back room holds the bound volumes from June 1989 and this year's loose issues.

## 2. The case at the start

The player is the district's coroner's officer (authored; no life in the off world). By custom every death is heard, and the coroner asks the same six questions:

1. Of what did she (he) die?
2. Since when was she (he) unwell?
3. Was anyone answerable for the death?
4. Who stood by her (him) and the household?
5. Was there bad blood, and did it bear on the death? (Case 2 adds: and did anything settle it?)
6. Does the printed record of the death and the life stand?

Case 1 opens with the coroner's file: Mary Tanner, 77, died Monday 10 February at home on the church hill, and the notice D-03′. Case 2 opens in round 3 with Andy Shaw's file: Andy Shaw, 85, died Wednesday 14 October at home on the Gully Steps, with D-04′ and the same six questions.

## 3. The card's rules, instantiated

Every roll is seeded `mystery-b-<id>-r<N>-t<turn>-<what>` and logged.

| Rule | Instantiation |
| --- | --- |
| Turns | 4 a round, one act a turn; 8 turns for case 1 and 16 for case 2, each hearing the last. |
| **1. Yield** (`q<k>`, d6 a question) | 1: "I couldn't say." 2 to 5: one fact this person could know (section 6). 6: that, plus a join of their own from what they saw or heard, in telling's shape, and never a cause. **Kin** (case 1: Mark Holmes; case 2: none) start guarded: one question a visit, and on a 1 or 2 they say "Not today." If kin ever turn open, they take two questions at most. |
| **2. Bend** (`bend`, d6 a telling) | 1: softened, the subject's part left out or made smaller. 6: hardened, the subject's part put first. 2 to 5: told as seen. |
| **3. Wrong name** (`name`, d20) | Five tellers slip on 3 or less: Edward Baker, Colin Berry, Peter Scott, Oliver Brook, John Holmes (the same five as the other arm). The wrong name is drawn uniformly (`who`) from the other people in that account's event list. |
| **4. Heard** (`heard`, d6) | After each talk act, for each absent person the player asked about: they turn guarded on 4+ if the one asked is their partner, family or a friend, otherwise on a 6. A friend here is anyone who shares two or more non-private off events with them. Someone asked first, before anyone was asked about them, stays open. Guarded lasts to the end of the case. |
| **5. Complaint** (`complaint`, d6) | A second visit to close kin (Mark Holmes) in one round: on 4+, standing −1. |
| **6. Talk about the dead** | Takes telling's shape (`engine-rules.md`, How news travels): it starts with someone who was there; it goes to their partner or a friend; it may pass once more, less surely; and it bends by rule 2. A person can say only what a witness could know (section 6). |
| **7. Watches** | A watch shows who keeps a routine at that place in that month (section 5) and the month's local events that happen there. Routines never lapse in this world, so a watch shows no absence except of the dead or the away. Nobody hears of a watch. |
| **8. The coroner's test** | At the hearing, a claim stands on the player's own sighting (something on one of their screens), a first-hand witness (someone in the event, or a partner or coworker for a non-private event, named in the journal), a dated record (Courier, notice, poster), or two independent second-hand tellers (neither heard it from the other). Anything else is hearsay and is struck. Anyone named in the account is summoned. A summoned person gives first-hand evidence of what the record shows, honestly for public and local events. A private act of their own stays private, and their denial strikes any claim that rests on it. |
| **The ruling** | *Rejected:* the account names anyone answerable for the death. Standing −2, and that person, their partner, family and friends close to the player for the rest of the session (GM-simulated). *Adjourned:* two or more claims struck, or a claim that some act bore on the death (naming nobody answerable) struck. Standing −1, and the town knows (people turn guarded on a d6 of 5+ at the first visit of the next case). *Accepted:* anything else. At standing 0 the player is taken off the cases. |
| **9. The check** (`CARD`) | Once a case, from its second round, as one act. The player names three claims on the board. The game master compares them with the off record and answers only "all three stand" or "not all three stand". |
| **10. Andy alive** | Every start shows Andy Shaw alive in round 1, on his evening walk. What the player saw then is first-hand at his hearing. |
| **Standing** | Starts at 3 of 6. Complaint −1, adjourned −1, rejected −2. An accepted account with no claim struck: +1. |
| **Willingness** | Open, guarded (one question a visit) or closed. At the start, Mark Holmes is guarded and everyone else is open. Hover shows it. |
| **The why-probe** | Free. For a public event the player has found: "Nothing on record says why." For anything else: "Ask someone who was there." |
| **Local news by chance** | Staff of the Anchor, the clinic, the school and the Courier may know a local event they weren't in: the first time one is asked about it, d6 (`knows`) 4+, logged GM-simulated. |

**Scoring (the close, `scores.md`, against the off world).** Case 2: the ten facts (section 7) at 10 each; partly right 5; contradicted −5; an innocent named −20; clamped to 0 to 100. Naming anyone answerable is naming an innocent. "?" scores 10 only where no witness could know. Case 1: four facts, scored right, partly or wrong, and reported apart.

## 4. The record's slips

The off Courier, posters and chatter make mistakes at the other arm's rate but at random: a wrong name or a wrong month, drawn uniformly over the record's names and months with the seed `mystery-off-<record>`. Each twin below is fixed; the game master hands over its words as printed.

## 5. Routines that place people (March 1997; look up October 1998)

- **Tuesday cards at the Anchor:** Karen Holmes, Audrey Scott, Kate Holmes, Mona Sayer, Trevor Lane, Larry Baker, Susie Lyons, Alice Tanner, Ellen Vaughan, Sally Baker, Lynn Newman, Ellie Eden. (Jonah Scott is away; Stella Lane, 17, is too young for the bar.)
- **Two pints at the Anchor most evenings:** Sid Tanner, Audrey Scott, Kate Holmes, Molly Scott, Olive Shaw, Eric Lane, Tara Myers, Terry Sutton, Steve Baker, Leo Lyons, Neil Lyons, Eve Vaughan, Tess Lane, Alex Myers, Lily Lyons. (Vera Holmes is away.)
- **At the Anchor every Friday:** Andy Shaw, Hannah Tanner, Karen Holmes, Ken Scott, Mark Holmes, Matt Sayer, Molly Scott, Trevor Lane, Gary Myers, Terry Sutton, Greta Brook, Sam Brook, Neil Lyons, Grace Waller, Eve Vaughan, Colin Berry, Harry Myers, Bert Kemp, Una Waller, Trevor Myers.
- **Andy Shaw:** at the Anchor every Friday, reads late, runs the coast road every other day, his shed, the shore walk every evening.
- **Mary Tanner** (to her death): two pints at the Anchor most evenings, the coast road every other day, Thursday choir, swims in the harbour every morning.
- **Mark Holmes:** Sunday dinner, the Anchor on Fridays, the boat at weekends, the coast road.
- **The Gully Steps:** Hannah Tanner: Sunday dinner, the Anchor on Fridays, the garden, the boat, reads late, Thursday choir. Karen Holmes: the Anchor on Fridays, Tuesday cards, reads late, her shed.
- **Olive Shaw:** two pints, the boat, practises nightly, the coast road. She works behind the Anchor's bar until she retires in March 1998.
- **Oliver Brook:** first in at work, the garden, swims every morning.

In October 1998 Andy's Friday seat at the Anchor and his shore walk are absences.

## 6. The cast, and who could know what

Ages are March 1997 · October 1998. Willingness at the start: open unless marked. Partners and households as the off file keeps them.

| id | Name | Ages | Work | Household and family | What they could know (off events) |
| --- | --- | --- | --- | --- | --- |
| p-22 | Mary Tanner | died at 77 | retired | married Mark Holmes 1981 | subject, case 1 |
| p-17 | Andy Shaw | 83 · died at 85 | retired | widower of Stella Shaw (married 1957, died 1978); lives alone on the Gully Steps | Case 1: a lift from Mary, July 1996 (e-11939); an argument with her in the street, August 1996 (e-11977). Himself: his songs, the band, an operation in the city in August 1996 (e-11959). Subject, case 2. |
| p-25 | Mark Holmes | 76 · 78 | retired | widower of Mary; father of Vera Holmes with Kate Holmes; lives alone on the church hill | **Kin, guarded.** The death (e-12095); his own nights out with Mary (e-10320, e-10735, e-11251, e-11278); a chat with Sally Baker and words with Kate Holmes, February 1997 (e-12105, e-12107). |
| p-37 | Olive Shaw | 66 · 68 | Anchor bar staff; retired March 1998 | married Ben Reed 1992; mother of Eric, Oscar and Peter Lane with Trevor Lane | Case 1: an hour's talk with Mary in the shop, February 1990 (e-10238). Staff, by chance. A-12′, A-18′. |
| p-19 | Edward Baker | 81 · 83 | retired | father of John Holmes; lives alone | **Slips names.** Driftwood: songs, practices, shows, the split (e-11995). |
| p-55 | Oliver Brook | 40 · 42 | skipper, the harbour fleet | seeing Agnes Tanner from March 1997 (e-12126); son of Greta and Sam Brook | **Slips names.** Driftwood and Pirate Radio: most often with Andy. |
| p-39 | Eric Lane | 44 · 46 | crew, the fleet | son of Olive Shaw and Trevor Lane | Coworker of Oliver. |
| p-90, p-110, p-111, p-116 | Bert Kemp, Oscar Ash, Maisie Baker, Libby Fielding | 45, 41, 26, 23 | crew, the fleet | | Coworkers of Oliver and Eric. |
| p-2 | Hannah Tanner | 81 · 83 | retired | widow of Lily Tanner (married 1949); mother of Sid Tanner; the Gully Steps | Andy's neighbour: his comings and goings (GM-simulated sightings of routines). February 1997: fishing with Grace Waller (e-12106), the meat raffle (e-12109). |
| p-4 | Karen Holmes | 72 · 74 | retired | mother of Owen Lane with Rose Lane; the Gully Steps | Andy's neighbour, as Hannah. |
| p-81 | Evan Newman | 56 · 58 | manager, the Anchor | | Staff, by chance. A-25′. |
| p-96 | Peter Scott | 45 · 46 | bar staff, the Anchor | | **Slips names.** Staff, by chance. A-05′. |
| p-109 | Agnes Tanner | 29 · 31 | bar staff, the Anchor | seeing Oliver Brook | Staff, by chance. A-28′. |
| p-42 | Larry Baker | 75 · 77 | retired | married Kate Holmes 1984; father of Gary Myers | A-26′ (Tuesday cards). |
| p-78 | Tess Lane | 46 · 48 | the school | married Eddie Lane 1978; mother of Sarah and Sophie Lane | Case 1: the raffle with Mary (1989, e-10045), fishing off the quay (1995, e-11606). School staff, by chance. |
| p-80 | Sarah Lane | 20 · 21 | the sawmill | daughter of Tess and Eddie Lane | Case 2: Driftwood January to September 1996; words with Andy at the Anchor, July 1997 (e-12206); tried out for Pirate Radio, June 1998 (e-12451). |
| p-73 | Alice Tanner | 27 · 28 | the sawmill | daughter of Ivan Tanner and Molly Scott | Case 2: tried out for Pirate Radio, June 1998 (e-12450). |
| p-64 | Neil Lyons | 48 · 50 | the sawmill | married Eve Vaughan 1967 | Case 2: Pirate Radio; a party with Andy at the Anchor, May 1998 (e-12430). A-20′. |
| p-31 | Sean Hale | 45 · 47 | the Old Bank Café | son of Molly Scott | Case 2: Pirate Radio; "Salt Radio" (e-12523). |
| p-12, p-91, p-82 | Ken Scott, Toby Tanner, Colin Berry | 39 · 40; 39 · 41; 48 · 50 | the Courier (editor; reporters); Colin left it in October 1998 (e-12550) | Ken married Sylvia Waller 1992; Colin married Thea Waller 1991 | The paper's records. **Colin slips names.** |
| p-21 | John Holmes | 51 · 52 | foreman, the sawmill | son of Edward Baker and Ellie Holmes | **Slips names.** |
| p-38 | Trevor Lane | 69 · 71 | retired | father of Eric, Oscar and Peter Lane with Olive Shaw | A-29′, A-30′. |
| p-27 | Mona Sayer | 74 · 75 | retired | married Terry Sutton 1977 | Tuesday cards. |

Others appear by routine (section 5): look them up before they speak.

**The same-sex couples in this cast,** stated as the record states them: Lily and Hannah Tanner, married 1949 (Hannah is Lily's widow); Owen Lane's parents are Karen Holmes and Rose Lane.

## 7. The answers, and how a player could reach them

### Case 1, Mary Tanner (four facts, reported apart)

| Q | Fact | Record | Routes |
| --- | --- | --- | --- |
| 1 | Died aged 77; nothing on record says of what. | e-12095 (public); D-03′, C-32′ | The notice; the obituary; anyone; the why-probe ("Nothing on record says why"). |
| 2 | No illness on record. | none | Mark; anyone who saw her about: two pints most evenings, the coast road, the choir, the morning swim, to the end. |
| 3 | Nobody answerable. | none | No record or witness gives a cause. |
| 4 | Those most often with her: Mark Holmes, then Tess Lane and Andy Shaw. | e-10320, e-10735, e-11251, e-11278 (Mark); e-10045, e-11606 (Tess); e-11939, e-11977 (Andy); all local | Mark, Tess and Andy themselves; their partners and coworkers; staff by chance. |

Ruled on but not scored. **Q5, bad blood:** words with Susie Lyons at the Anchor (October 1992, e-10965) and an argument with Andy Shaw in the street (August 1996, e-11977). Nothing on record follows from either. **Q6:** D-03′ and C-32′ both stand.

### Case 2, Andy Shaw (ten facts, 10 points each)

| # | Fact | Record | Routes a player could have |
| --- | --- | --- | --- |
| 1 | Died aged 85; nothing on record says of what. | e-12549 (public); D-04′, C-35′ | The notice; the obituary; the why-probe. |
| 2 | No illness on record before his death. (An operation in the city in August 1996, home within the week, more than two years before.) | e-11959 (local; who: Andy) | Staff by chance; anyone who saw him about; Andy himself in case 1. |
| 3 | Nobody caused his death. | none | No record or witness gives a cause. |
| 4 | Two of the four most often with him in his last three years: Oliver Brook, Edward Baker, Sarah Lane, Neil Lyons. | non-private off events, October 1995 to October 1998 | The four themselves; the bands' records (C-26′, P-09′, C-30′, C-34′, P-13′); the Anchor's staff and regulars. |
| 5 | Sarah Lane had words with him at the Anchor, July 1997. | e-12206 (local) | Sarah; A-26′ (Larry Baker); her coworkers at the sawmill; staff by chance. |
| 6 | Alice Tanner and Sarah Lane both tried out for Pirate Radio in June 1998, and he got the place. | e-12450, e-12451 (local); e-12449 (public) | Alice; Sarah; their sawmill coworkers; A-28′ (Agnes Tanner); C-34′ prints only the place. |
| 7 | Nothing on record follows from either. | none after e-12206 or e-12451 between them | The why-probe on his death; anyone. |
| 8 | "Salt Lanterns" is Andy's (P-08′ credits it to Ash). | e-11503 (local: Andy, Oliver, Edward) | Oliver, Edward; C-26′ (right on this point); A-18′ (Olive); against: P-08′. |
| 9 | Driftwood split in September 1996, and nothing says why. His last band was Pirate Radio, from June 1998. | e-11995 (public); e-12449 (public) | The why-probe ("Nothing on record says why"); C-30′; C-34′; P-13′; the band. |
| 10 | His routines never stopped: C-35′'s "seldom out of his shed until May" is wrong. | his routines in the off file | Hannah Tanner and Karen Holmes, his neighbours on the steps (GM-simulated sightings); the Anchor on Fridays; against: C-35′. |

## 8. Records and chatter (the off twins)

Hand over the record's words only. Each slip is fixed; the `Truth` lines are for game masters.

**D-03′ · Courier, Thursday 13 February 1997**
> **TANNER, Mary.** Died aged 77. Wife of Mark Holmes. The funeral is on Wednesday at eleven. No flowers.

*Truth:* right (e-12095).

**C-32′ · Thursday 20 February 1997 · Mary Tanner · by Toby Tanner**
> Mary Tanner died last week. She was 77. She married Mark Holmes in 1981. She had two pints at the Anchor most evenings, ran the coast road every other day, sang with the choir on Thursdays and swam in the harbour every morning, whatever the weather. She won the Anchor's quiz night in 1989 and again in 1990.

*Truth:* right (e-12095; e-10106, e-10426; her routines).

**C-26′ · Thursday 16 March 1995 · Driftwood at the Anchor · by Toby Tanner**
> Friday's Driftwood night at the Anchor was an ordinary night. "Salt Lanterns", Andy Shaw's song from December, has gone straight into the set, beside "Grey Radio", also his, from last July. Sylvia Waller, Andy Shaw and Edward Baker have played together since Peter Lane left in June.

*Truth:* the line-up is a slip: Oliver Brook, not Sylvia Waller (seed `mystery-off-C-26`). The rest is right (e-11564, e-11503, e-11409, e-11388).

**P-08′ · for Friday 10 March 1995**
> **DRIFTWOOD**
> at the Anchor · Friday 10 March
> Oliver Brook · Andy Shaw · Edward Baker
> "Salt Lanterns" (Ash) · "Grey Radio" (Shaw) · "Open Water" (Baker) · "Green Weather" (Shaw)

*Truth:* the credit on "Salt Lanterns" is a slip: it is Shaw's (e-11503), not Ash's (seed `mystery-off-P-08`).

**P-09′ · for Friday 15 March 1996** (on the loft door above the fleet's berth, still up in March 1997)
> **DRIFTWOOD**
> with Sarah Lane · the Anchor · Friday 15 March
> Oliver Brook · Andy Shaw · Edward Baker · Sarah Lane
> "Cold Hours" · "Salt Lanterns"

*Truth:* right (e-11799, e-11842; e-11795, e-11503).

**C-30′ · Thursday 19 September 1996 · Driftwood calls it a day · by Colin Berry**
> Driftwood have split up after six years. Their last night at the Anchor was in March, when they were called back for more. Sarah Lane, who joined in January, Oliver Brook, Andy Shaw and Grace Waller have not said what comes next.

*Truth:* the last name is a slip: Edward Baker, not Grace Waller (seed `mystery-off-C-30`). The rest is right (e-11995, e-11842, e-11799).

**C-33′ · Thursday 26 March 1998 · A washout, a new band and a retirement · by Colin Berry**
> Saturday's festival on the quay, Ellie Eden's second, was a washout. Larry Baker, Lisa Myers and Andy Shaw helped. On a better note, Neil Lyons, Oliver Brook and Sean Hale have started a band and call it Pirate Radio. And Olive Shaw, 67, has retired after ten years behind the bar at the Anchor.

*Truth:* right (e-12368; Pirate Radio formed; Olive's retirement).

**C-34′ · Thursday 25 June 1998 · Open night · by Toby Tanner**
> At Friday's open night John Holmes, 52, played on his own and did well. Oliver Brook did well after him. Pirate Radio have a new member: Andy Shaw, 84, last seen with Driftwood.

*Truth:* right (the open night; e-12449). Not printed: the two tryouts (e-12450, e-12451, local).

**P-13′ · for Friday 18 September 1998** (on the Anchor's wall from September, still up in November)
> **PIRATE RADIO**
> first night at the Anchor · Friday 18 September
> Neil Lyons · Oliver Brook · Sean Hale · Andy Shaw
> with "Salt Radio"

*Truth:* right (e-12524, e-12523).

**D-04′ · Courier, Thursday 22 October 1998**
> **SHAW, Andy.** Died aged 85. Husband of the late Stella. The funeral is on Tuesday at two. Pirate Radio will play at the Anchor afterwards.

*Truth:* right (e-12549).

**C-35′ · Thursday 22 October 1998 · Andy Shaw, 1913 to 1998 · by Toby Tanner**
> Andy Shaw died last week. He was 85. Born in the town in 1913, he married Stella Shaw in 1957 and lost her in 1978. He walked the shore every evening, ran the coast road every other day, read late, was at the Anchor every Friday, and was seldom out of his shed until May. In 1990 he joined Driftwood and wrote "Salt Lanterns", "Grey Radio" and "Cold Hours". In June he joined Pirate Radio, and in September played the Anchor with them. Pirate Radio will go on without him.

*Truth:* "until May" is a slip: his shed routine never stopped (seed `mystery-off-C-35`). The rest is right (e-12549, e-11503, e-11409, e-11795, e-12449, e-12524, e-12555).

**C-36′ · Thursday 19 November 1998 · Changes at the Courier · by Ken Scott**
> Colin Berry has left the Courier after seven years. We thank him for his work and wish him well. Vera Holmes, 50, joins us this month. She and Jonah Scott came home in October after three years in the city.

*Truth:* right (e-12550, e-12583, e-12557).

**Chatter at the Anchor** (the speaker says it only when at the Anchor in its month, or later as memory in telling's shape):
- **A-05′ · February 1990 · Peter Scott, behind the bar.** "Olive and Ben Reed are seeing each other. Started in August." *Truth:* the month is a slip: they started that month, February (seed `mystery-off-A-05`).
- **A-06′ · February 1990 · Molly Scott, Friday.** "Olive Shaw and Alice Tanner were in the shop an hour, talking. I saw them." *Truth:* the name is a slip: it was Mary Tanner (e-10238; seed `mystery-off-A-06`).
- **A-12′ · February 1992 · Olive Shaw, behind the bar.** "Audrey Scott and Karen Holmes were up dancing last month, on the Saturday." *Truth:* right (e-10762).
- **A-18′ · January 1995 · Olive Shaw.** "Andy's 'Salt Lanterns' went straight into the set. They're up in that loft till all hours, him and Edward and Alex Myers." *Truth:* the last name is a slip: Oliver Brook (e-11503, e-11509; seed `mystery-off-A-18`).
- **A-20′ · March 1995 · Neil Lyons, Friday.** "Driftwood on Friday. Ordinary night. They've had better." *Truth:* right (e-11564).
- **A-25′ · March 1997 · Evan Newman.** "Mark and Kate Holmes had words in the street last month. And Sally Baker stopped him outside the shop." *Truth:* right (e-12107, e-12105).
- **A-26′ · July 1997 · Larry Baker, Tuesday cards.** "Sarah Lane and Andy Shaw had words in here the other night." *Truth:* right (e-12206).
- **A-28′ · June 1998 · Agnes Tanner, behind the bar.** "Alice Tanner and Sarah Lane both tried out for Pirate Radio, and Andy Shaw got the place. He's eighty-four." *Truth:* right (e-12450, e-12451).
- **A-29′ · July 1998 · Mona Sayer, Tuesday cards.** "Trevor Lane gave Sam Brook a lift into town." *Truth:* right.
- **A-30′ · November 1998 · Trevor Lane, Friday.** "Pirate Radio are going on without Andy." *Truth:* right (e-12555).

Any other record a player asks for is written generically from public off events, by the off file's rules, with slips at random.

**The windows.** Local and public off events a watch or a bar can show: in February and March 1997, look up 1997 (e-12091 to e-12132; e-12121 is private and never shown). In October to December 1998: Colin Berry left the Courier (e-12550), Jonah Scott came back (e-12557), Vera Holmes started at the Courier (e-12583), Pirate Radio went on (e-12555), and the rest by look-up.

**Never on a screen:** any private off event; any cause, reason, illness, history or lapse; anything from the other arm.

## 9. The six starts

Kind k starts the same in both arms. The list after the table is every place where an off screen differs from its on twin, and why; nothing else may differ.

| Kind | Door | Place, day, time | Who is there | Case-1 thread | Case-2 thread | Played this round |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | The Courier's back room | Market Square, Mon 3 March, 5:40 pm | Ken Scott (front office), Toby Tanner typing, Colin Berry laying out a page | D-03′, C-32′ and the bound volumes | the archive (C-26′, P-08′, C-30′); Colin's empty desk in round 3 | no (amendment 1) |
| 2 | The band | the fleet's berth on the quay, Mon 3 March, 5:45 pm | Oliver Brook and his crew; P-09′ on the loft door | Oliver's crew; Olive (Eric Lane's mother) | Driftwood, the split, Pirate Radio | X2 |
| 3 | Tuesday cards | the Anchor, Tue 4 March, 7 pm | the Tuesday tables; Olive at the bar | Karen Holmes, Mona Sayer at the tables | Larry Baker (A-26′), Mona (A-29′) | no (amendment 1) |
| 4 | The Gully Steps | Mon 3 March, 5:30 pm | Andy coming out; Hannah at her kitchen sink; Karen in her shed | Andy (the lift, the argument) | the neighbours; the dark house | X4 |
| 5 | The widower | Mark Holmes's kitchen, the church hill, Mon 3 March, 5:45 pm | Mark (guarded) | Mark; Kate Holmes, Sally Baker | the Anchor's Friday regulars; Larry Baker | X5 |
| 6 | The Anchor's bar | Mon 3 March, 7 pm | Evan, Olive, Peter; fourteen regulars | Evan, Olive; Tess Lane | Agnes (A-28′); P-13′; Olive gone | X6 |

**Where an off screen differs from its on twin, and why** (each because the two worlds' lives differ there, never for any other reason):
1. **The notice in every case file** (all starts): D-03′'s words. The off record gives no cause and keeps its own last line.
2. **Door 2, the poster on the loft door:** its two song titles. The off band's songs are its own.
3. **Door 3, the Tuesday tables:** who sits at them, who is at the bar, and where Olive Shaw sits. The off world's routines place different people there.
4. **Door 4, the two lit windows:** which neighbour is in her shed and which is at her kitchen sink. The off routines give the shed to the other neighbour.
5. **Door 6, the regulars:** who is drinking at the bar that evening, and so how many. The off world's two-pints regulars differ.
6. **Later screens:** every record and chatter line is its off twin (section 8); the why-probe's answers; the round-1 Friday event at the Anchor (the quiz night here, a different event in the other arm); the round-3 mark of Andy's absence follows his off routines (his empty Friday seat at the Anchor); the tenth hour's December event (below).

Doors 1 and 5 differ only in the notice.

**The starts in detail.**

**Start 1** (not played). The Courier's front office and back room on Market Square. Ken calls through: "If it's Mary Tanner, the notice was in the thirteenth and Toby's piece in the twentieth." The bound volumes run 1989 to 1996; the 1997 issues are loose in a box file, the newest Thursday 27 February. Through the back window, Andy walks the quay to the shore. Probe: Toby Tanner, Toby Waller, Andy Shaw. Round 3: Colin's desk is cleared; C-35′ is the newest issue.

**Start 2.** The boats are in. Oliver Brook, skipper, hoses down his deck; Eric Lane, Bert Kemp, Oscar Ash, Maisie Baker and Libby Fielding stack boxes. P-09′ is pasted on the padlocked loft door, sun-faded. Andy passes along the quay to the shore. Oliver: "Coroner's, is it? Give us ten minutes and I'm yours." Probe: Oliver Brook; Agnes Tanner or, if not met, the case-1 witness met most who returns in case 2; Andy Shaw. **Round 3** (Monday 26 October 1998, the same hour): the same crew, two years older; P-13′ pasted on the loft door over the corner of P-09′; no old man on the quay.

**Start 3** (not played). Cards night. Olive Shaw at the end of the bar with a pint. Tables: Karen Holmes, Audrey Scott, Kate Holmes and Trevor Lane; Susie Lyons, Alice Tanner, Ellen Vaughan and Lynn Newman; Mona Sayer, Larry Baker, Sally Baker and Ellie Eden. At the bar: Sid Tanner, Molly Scott, Terry Sutton and others. Staff: Evan Newman, Peter Scott, Agnes Tanner. Andy passes the front window at ten past seven. Probe: Olive Shaw, Mona Sayer, Andy Shaw.

**Start 4.** The lamps on the steps have just come on. Andy comes out of his door above the half-landing and goes down past the player. Across the steps, Hannah Tanner is at her kitchen sink; one house up, Karen Holmes's shed is lit and she is at the bench. The houses are plain and kept. Probe: Hannah Tanner, Karen Holmes, Andy Shaw. **Round 3** (Monday 26 October, half past five): Andy's windows are dark and his door shut; Karen's shed is lit as before; Hannah at her sink; nobody comes down the steps.

**Start 5.** Mark Holmes opens his door: "You'll be from the coroner. Come through." A plain kitchen with a table and two chairs, a range, a dresser and a garage calendar on this month. From the window, Andy walks the shore in the last of the light. Mark is guarded (kin). Probe: Mark Holmes, Larry Baker, Andy Shaw. **Round 3** (Monday 26 October, a quarter to six): Mark, two years older, at the same door; the same kitchen; nobody on the shore.

**Start 6.** An ordinary Monday at the Anchor. Behind the bar: Evan Newman, Olive Shaw, Peter Scott. Regulars with pints: Sid Tanner, Audrey Scott and Kate Holmes by the fire; Molly Scott, Eric Lane, Tara Myers and Terry Sutton along the bar; Steve Baker, Leo Lyons and Neil Lyons by the dartboard; Eve Vaughan, Tess Lane, Alex Myers and Lily Lyons by the window. Evan: "Mary Tanner? Ask away. I'm here till eleven." Andy passes the front window at about ten past seven. Probe: Evan Newman, Olive Shaw, Andy Shaw. **Round 3** (Monday 26 October, seven o'clock): Olive is gone from behind the bar (retired in March; she may be at a table with her two pints); Agnes Tanner is on with Evan and Peter; P-13′ is on the wall by the door; no one passes the window at ten past seven. On Fridays from 30 October, Andy's seat is empty.

## 10. The tenth hour and the exit

After round 6's hearing, the tenth hour (300 to 500 words) runs the next twenty turns as the player's own strategy would: the close (scores and the off record for each fact); the town's talk of the account (those named hear of it, by the rules); Mona Sayer and Terry Sutton's party at the Anchor (e-12598, December 1998); then, plainly, no death to the record's end, January 1999, so no third case. The exit question for understanding: "What do you believe happened to Andy Shaw, Edward Baker and Sarah Lane, and why?"

## Gaps

- **Two empty fact slots.** The card's list for the off case (no illness on record; nobody answerable; who was with him most; his last band; a row that carried nothing; the split's date; the obituary's random error; his routines) fills eight of the ten slots: 2, 3, 4, 5 and 7 (the row and that nothing came of it), 6 (the band place), 9 and 10. Slots 1 and 8 were empty. Filled from the off world only, with no cause and no history, matched to what the other arm's slots ask: **slot 1**, what he died of: "died aged 85; nothing on record says of what" (e-12549, D-04′); **slot 8**, whose a song is: "'Salt Lanterns' is Andy's, and P-08′'s credit to Ash is wrong" (e-11503, a random slip).
- **No cold start.** Amendment 1 drops kind 3; every played opening has the pitch and tutorial.
- **Case 2 has no kin,** so the kin rules touch nobody in case 2.
- **Kin start guarded in both arms,** though the off world simulates no grief: the card's rule, not a life.
- **Standing has no gain** on the card; +1 for an accepted account with no claim struck, as in the other arm.
- **Routine start years are unreliable** in the off file: never cite one, or a duration drawn from one.
- **The quiz night's Friday, the days, the home, the hearing room and Andy's walk** are authored (section 1).
- **The tenth hour's December event** is e-12598 here; the card names an event of the other arm.
