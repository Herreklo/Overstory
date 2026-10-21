# Thursday's Paper (the paper): setup, lives off

What every lives-off run of the paper shares. Arm folder `a`, cohort Y (`arms.md`: journalist a = off, b = on). Game masters, auditors, analysts and the lead read it; players never do. The card (`docs/playtests/paper-1/cards/journalist.md`) holds for its role, goals, failure, decisions, screens and verbs; its lists of the real run's events do not. Everything an off game master needs from them is restated here. Each run's own truth is in `a/<id>/gm.md`.

**Read only** this page, `world/world-9989-off.md` and `world/world-9989-off.json`, `world/engine-rules.md`, and the cast tables of `world/atlas-9989.md` (people, households, places, who lives where). Never the real run's lives, causes, records, storylines, or `journalist/setup-on.md`.

**Look facts up** with the off lines only:

    python3 -I world/tools/lives_off.py person "NAME" FROM TO | sed -n '/^  OFF$/,$p'

The tool prints the real run's lines first; the `sed` keeps only the off section. Always give it `person` and a name (run with no arguments, it rebuilds the JSON). Town year = engine year − 37. Event ids here are the off world's (e-10xxx).

**Who plays.** Pre-registration amendment 1: kinds 2, 4, 5 and 6 only. Y2 (cold start: no pitch, no tutorial), Y4, Y5 and Y6 play here; Y4 to Y6 open with the card's pitch and tutorial word for word. All six starts are written below; starts 1 and 3 have no run this round.

**The off world:** the same people, births, deaths, jobs and job changes, households, partners, arrivals and departures, bands and shows (their outcomes dealt again) and ventures, with generic doings in place of lives. Nobody has reasons, nothing carries, nobody is found out, there are no races or rivals, nobody drags anything up, routines never lapse, and the town has no past before 1989. Asked why, a person has none to give. A routine's start year is not reliable: never cite one.

**Shared with the on arm, word for word:** the clock (§1), the paper at the start (§3), every rule and number (§4), the beats, the screens' shape and length, the cast's names, jobs, ages, places, households and partners (so the kin rule holds), and the six starts' places and times. §11 lists every place an off screen must differ from its on twin, and §12 says how much less there is to report.

## 1. The clock

**Days.** 1 June 1990 is a Friday. Rounds run Thursday to Wednesday; the paper goes to press on Wednesday night and is out on Thursday.

| round | covers | chase turns | press | edition | Friday at the Anchor | Thursday choir | Tuesday cards |
| --- | --- | --- | --- | --- | --- | --- | --- |
| before play | Fri 1 to Wed 6 June 1990 | | | 7 June (out at the opening) | 1 June | | 5 June |
| 0 (opening) | Thu 7 June, morning | | | | | | |
| 1 | Thu 7 June (after the opening) to Wed 13 June | 3 | Wed 13 | Thu 14 June | 8 June | 7 June | 12 June |
| 2 | Thu 14 to Wed 20 June | 3 | Wed 20 | Thu 21 June | 15 June | 14 June | 19 June |
| 3 | Thu 21 to Wed 27 June | 3 | Wed 27 | Thu 28 June | 22 June | 21 June | 26 June |
| the jump | 28 June 1990 to 22 May 1991 | | | | | | |
| 4 | Thu 23 May (opens at the bound volume) to Wed 29 May 1991 | 3 | Wed 29 | Thu 30 May | 24 May | 23 May | 28 May |
| 5 | Thu 30 May to Wed 5 June | 3 | Wed 5 | Thu 6 June | 31 May | 30 May | 4 June |
| 6 | Thu 6 to Wed 12 June | 3 | Wed 12 | Thu 13 June | 7 June | 6 June | 11 June |
| tenth hour | Thu 13 June to Wed 17 July | 15 (20 turns with the editions) | | 20 and 27 June, 4, 11 and 18 July | | | |

The player names the day and part of the day (morning, afternoon, evening) of each chase turn. If they don't, turn 1 is Thursday or Friday, turn 2 Saturday to Monday, turn 3 Tuesday or Wednesday. The edition is the fourth turn, made up on Wednesday.

**Which week an event falls in.** The clock is the town's, shared by every run and both arms: an event both worlds keep (a job, an arrival, a show, a harbour day) falls in the same week in both, and its roll is listed below. For any other event, seed `journalist-r0-t0-week-<event id>`, d4:

    python3 -I -c "import random; r=random.Random('journalist-r0-t0-week-e-10601'); print(r.randint(1,4))"

| month | 1 | 2 | 3 | 4 |
| --- | --- | --- | --- | --- |
| June 1990 | before play | round 1 | round 2 | round 3 |
| May 1991 | 1 to 22 May (the jump) | the jump | the jump | round 4 |
| June 1991 | round 5 (1 to 5 June) | round 6 | tenth hour, edition of 20 June | tenth hour, edition of 27 June |
| July 1991 | edition of 4 July | edition of 11 July | edition of 18 July | after the close |

**Which day:** seed `journalist-r0-t0-day-<event id>`, d7, 1 = Thursday to 7 = Wednesday of its week, unless the text fixes the day ("on Sunday", "on Saturday", the Anchor on a Friday). A workplace act on a Sunday moves to the Monday. Round 1's Thursday events fall in the afternoon, after the opening. Every roll below has been made.

## 2. The lead calendars

*News* can come by tip (§4, rule 1); *colour* never does, only by asking or watching. Draw is the sales table's; T = trouble (+20).

### June 1990

| event | when | vis · notability | beat | what | kind | draw |
| --- | --- | --- | --- | --- | --- | --- |
| e-10325 | before play | local 1,500 | sawmill | John Holmes let Greta Brook go from the sawmill | news | 40 T |
| e-10320 | before play | local 1,000 | Anchor | Mary Tanner and Mark Holmes sang a duet at the Anchor | colour | |
| e-10326 | r1, Thu 7, afternoon | public 1,500 | garage | Trevor Lane retired from the garage | news | 40 |
| e-10327 | r1, Sat 9 | public 2,000 | garage | Sally Baker became head mechanic at the garage | news | 60 |
| e-10329 | r1, Sat 9 | public 800 | quay | The harbour day went off well enough, with Harry Myers in charge | news | 0 |
| e-10331 | r1, Tue 12 | local 600 | school | Harry Myers worked a double shift at the school | colour | |
| e-10328 | r1, Wed 13 | local 1,000 | quay | Hannah Tanner took Greta Brook out on a boat for the afternoon | colour | |
| e-10319 | r2, Sun 17 | local 200 | | Ken Scott and Gary Hughes took the bus to the city together | colour | |
| e-10335 | r3, Sun 24 | local 1,200 | quay | Trevor Lane and Audrey Scott took the ferry for a day out | colour | |

Private in June 1990, never on a screen: e-10317, e-10318, e-10321, e-10322, e-10323, e-10324, e-10330, e-10332, e-10333, e-10334, e-10336.

**Background a player can dig for** (unprinted local events before June): Greta Brook had a bad fall on the steps and was laid up for a month (e-10296, May, local 2,000); Neil Lyons bought a second-hand car (e-10300, May, local 1,300); Lisa and Alex Myers took the ferry for a day out (e-10302, May, 1,200); Harry Myers is organising the harbour day this year (e-10304, May, local 800); Audrey Scott twisted an ankle on the gully steps (e-10310, May, 900); Hannah Tanner and Harry Myers went to the city for the day (e-10293, April, 1,300); John Holmes and Harry Myers argued in the street (e-10254, March, 1,000); Una Waller and John Holmes argued in the street (e-10229, January, 1,050); Ben Reed and Olive Shaw started seeing each other (e-10239, February, 1,000); Oliver Brook won the Anchor's quiz night (e-10269, March, 1,100). Old news draws by its notability like new. Ken Scott and Sylvia Waller's argument in the street (e-10271, March) never reaches a screen (the card's rule on the editor's rows).

### May to July 1991

| event | when | vis · notability | beat | what |
| --- | --- | --- | --- | --- |
| e-10576 | May, before r4 | public 1,000 | sawmill | Gary Hughes started work at the sawmill |
| e-10579 | Fri 17 May | public 200 | Anchor | Driftwood played the Anchor, and it went down well (C-09's twin, P-03's twin) |
| e-10577 | May, before r4 | local 800 | quay | Maisie Myers is organising the harbour day this year |
| e-10566 | May, before r4 | local 2,000 | Anchor | Ivan Tanner and Molly Scott won the big prize in the Anchor's raffle |
| e-10593 | May, before r4 | local 1,200 | council | Terry Sutton and Jonah Scott had words at the council office |
| e-10580 | May, before r4 | local 1,100 | | Jonah Scott had family to stay for a fortnight |
| e-10588 | a Saturday, before r4 | local 1,100 | Anchor | Sylvia Waller and Sally Baker danced together at the Anchor |
| e-10581 | May, before r4 | local 1,000 | | Jonah Scott and Vera Holmes started seeing each other |
| e-10574, e-10575 | May, before r4 | local 400, 500 | | Colin Berry had a pint at the Anchor; Greta Brook was off sick for a few days |
| e-10569 | r4, Tue 28 May | local 600 | quay | Oliver Brook had a busy week at the harbour fleet |
| e-10597 | r5, Sun 2 June | local 400 | | Susie Lyons walked the shore on Sunday |
| e-10605 | r5, Mon 3 June | local 400 | council | Lily Lyons had a busy week at the council office |
| e-10601 | r5, Wed 5 June | local 1,000 | | Hannah Tanner and Sally Baker argued in the street |
| e-10594 | r6, Fri 7 June | local 800 | quay | Sophie Lane and Tess Lane watched the boats come in |
| e-10604 | r6, Fri 7 June | local 200 | | Sylvia Waller hung out the washing |
| e-10599 | edition of 27 June (Sat 22 June) | public 1,400 | quay | The harbour day ran smoothly, with Maisie Myers in charge |
| e-10619 | edition of 4 July | public 1,500 | garage | Gary Newman moved to the town and started work at the garage, with Lynn Newman |
| e-10624 | edition of 4 July | local 2,000 | | Greta Brook had a bad fall on the steps and was laid up for a month |
| e-10621 | edition of 11 July | local 1,100 | clinic | Colin Berry left his job at the clinic |
| e-10617 | edition of 11 July | local 1,100 | choir | Lily Lyons sang a solo at the choir's spring concert |
| e-10616 | edition of 18 July | local 1,000 | Anchor | Colin Berry and Leo Lyons sang a duet at the Anchor |

After the close: Colin Berry starts at the Courier (October 1991, public). In April 1991, in the jump: Sylvia Waller and Ken Scott danced together at the Anchor on Saturday (e-10553, 1,300); Lily Lyons and Sylvia Waller took the ferry for a day out (e-10554, 1,300); Peter Lane brought a new song to Driftwood, "Winter Boats", and the others liked it (e-10552, local 200).

## 3. The paper at the start

The same as the on arm's, word for word:

- **The Courier,** a front office and a back room on Market Square (authored). Out on Thursdays. Ken Scott (p-12), 32, the editor; Toby Tanner (p-91), 32, reporter; Susie Lyons (p-62), 66, at the desk by the window, until January 1991. The player is the second reporter from June 1990, with no engine life.
- **The edition out at the opening,** 7 June 1990: its front page is Ian Myers leaving for university in the city (e-10306, public, May).
- **The player's page:** a 500-word front page, two 250-word inside stories, and free notices (Susie writes them up). Colleagues' pieces run on other pages and do not count for sales; if the player takes a story a colleague was writing, the colleague's piece is spiked.
- **Standing:** sales 850 a week; readers' trust 6/10; the editor's patience 5/10; each source's trust 2/3 when first met.
- **Goals:** kept on if never let go and the six editions of rounds 1 to 6 average 850 or more; made permanent at the jump if trust is 7 or more after round 3. Trust, patience and source trust carry over the jump.
- **The editor's kin:** Sylvia Waller (p-70, council office, his partner); her parents Toby Waller (p-67, clinic) and Grace Waller (p-68); her sister Thea Waller (p-69, runs the clinic); Thea's partner Colin Berry (p-82, clinic) and their son Andy (born November 1989); Ken's brother Jonah Scott (p-11, council office); their mother Audrey Scott (p-10).
- **Ken is not a source.** Asked about the town, he says "get it from someone who was there". His rows with Sylvia never reach a screen. Courier-internal events are seen by the player as a coworker: on this arm, Ken Scott and Toby Tanner had words at the Courier (e-10420, November 1990, local 1,000), known to the player at round 4.

## 4. The card's rules, instantiated

Identical to the on arm's in every number. Each roll is seeded `journalist-a-<id>-r<N>-t<turn>-<what>` and logged as `GM-SIMULATED <rule; seed; roll>`.

**Kinds of event.** *News:* dismiss, retired, promoted, hired, startover (left a job), arrived, left, born, married, death, health (an operation, a fall, hospital, off sick a week or more), band formed, joined, show, harbour day, festival, purchase (a house, a boat, a car, a trip), luck (a raffle or prize), party, quarrel. *Colour:* everything else (social, everyday, work, mood, away, band practice, a new song). Colour of 1,000+ may be printed as news if the player chooses; it draws by notability but never comes by tip. **Trouble:** dismiss, startover, quarrel (argued in the street, had words, a shouting match, fell out).

**Who could know.** A local event reaches the people in it, their partners and coworkers at once; family and friends of those by telling, on d6 4+ by the next round (`know-<event>-<person>`, rolled once when it matters); people whose work is with people (the Anchor, the clinic, the school, the Courier) by chance, on d6 5+ from the week after. A public event reaches everyone. A private event reaches only the people in it. **Friends,** in this world, are people with a local or public social event together in the twelve months before (there are no friendship events).

| rule | when | roll | result |
| --- | --- | --- | --- |
| 1 Tips | each news event the morning after its day (week-1 events at round 1 turn 1); colour never | `tip-<event>` d6, once | local 1,000+: in the tip book on 4+, from one named teller who could know it (`teller-<event>`, a pick from §8's lists), bent by rule 3. Public: always, from the counter. Local under 1,000: never by tip |
| 2 Yield | each question (up to three a visit) | `q1`, `q2`, `q3` d6, then source trust: −1 at trust 1, +1 at trust 3 | 1 or less: "no comment". 2 to 5: one fact they could know, the nearest to the question, or "I wouldn't know". 6 or more: that and a second plain fact about the same person or place, with no link said (people here give no reasons). A subject asked about their own act: on 4+ the act in their own mild words ("we parted ways"); on 1 to 3 the plain act or "no comment" by the yield |
| 3 Bend and slip | each telling a source gives | `bend` d6; `name` d20 for slipping tellers | the bend: 1 softer (drop the hardest word), 2 to 5 as it is, 6 harder (a harder word; never a cause). A slipping teller names the wrong person on 1 to 3: the subject's coworker or companion picked by `name-who` |
| 4 Heard | after asking about someone not present | `heard` d6 | the subject learns on 4+ if you asked their partner, family or a friend, otherwise on 6; then "no comment" to you for the rest of this round and the next |
| 5 Source trust | after each edition | none | 0 if named against their word; +1 if printed as said and shielded; at 3 they bring one tip a round unasked; at 0 "no comment" to everything until the jump, then 1. A burned source's partner, family and friends drop to 1 |
| 6 Sales | each edition | `sales` d20 | 850 + front draw + ½ each inside draw + d20 − 10. Draw by the story's highest event: 2,000+ 60; 1,500 to 1,999 40; 1,000 to 1,499 20; under 1,000 0; trouble +20 on that story. Each scoop of the week −30; each correction in the edition −15. Over 900: patience +1 |
| 7 Rival | the Saturday after the edition of an event's week (week-1 events: after 14 June) | `rival-<event>` d6 | a news event of 1,500+ the Courier has not printed runs in the county paper on 5+ (local) or 4+ (public), from one teller who could know it, bent by rule 3 (`rival-teller-<event>`). A scoop: patience −1 at once, −30 at the next edition |
| 8 Complaint | after press, for each printed claim about a named person the record contradicts | `complaint-<k>` d6, `libel-<k>` d6 | complaint and correction on 3+: trust −1, or 0 if the claim was marked "heard from someone named" and that source was first-hand. If the claim alleges a wrong, a libel threat on 4+: patience −2 |
| 9 Borne out | the edition after | none | a printed main claim the record bears out, about a local event not yet public: trust +1, once an edition |

**First-hand** means in the event's `who`, a coworker present at a workplace act, or someone present at a scene the text places. **For print:** an answer is "not for print" when it is about the teller's own partner, family, household or coworker; otherwise it is for print.

**Ledger of the dials.**

| what happens | trust | patience |
| --- | --- | --- |
| a correction | −1 (0 with a named first-hand source) | |
| a libel threat | | −2 |
| a scoop | | −1 |
| insist on a kin story Ken asked you to soften or hold | | −1, or −3 if the record contradicts it |
| comply, and the rival prints it | −1 | |
| an edition over 900 | | +1 |
| three editions under 750 (the owner's letter, once) | | −2 |
| a story borne out | +1, once an edition | |

Both dials run 0 to 10. At 0 of either the player is let go: the next screen says so and the run goes to its exit.

**The decisions.**
1. **Print now or check:** checking costs a turn; the rival rolls on what is held.
2. **What a claim says:** the act, or "it is said". There are no causes on record in this world, so any printed cause scores wrong at the close. "It is said" is contradicted only if nobody said it, but it still takes the libel roll if it alleges a wrong the record contradicts.
3. **Name or shield:** naming a "not for print" source sets them to 0.
4. **The editor's kin:** Ken reads every story naming his kin and asks you to soften (drop the name, or the hardest word) or hold. Comply: free, unless the rival prints it (trust −1). Insist: patience −1, or −3 if the record contradicts it.
5. **The cruel story:** a story that prints Greta Brook's dismissal beside her fall (or, after the jump, beside anything about her health) draws +20 more. Greta's circle and John Holmes's circle (§8) go to source trust 0 until the jump, then 1. Any "because" in it scores wrong.
6. **Whom to believe:** every teller bends at random (rule 3); the same six slip names.

**The why-probe** answers for every event: "Nothing on record says why." A person asked why their own act happened says "I couldn't tell you. It's done." Asked why someone else's, "I couldn't say."

**Watching** a place for a turn shows who is there by work or routine (§7), any event placed there on that day (marked "saw it"), and one colour line of the week about someone present (`watch`, a pick), if there is one. A private act is never seen.

**Reading** costs a turn: the bound volumes of 1989 and of 1990 to date (the off twins of C-01 to C-04 in full, §9, and every public event as a one-line notice in its month, in the event's words; earlier volumes are not on the shelf); the county paper at the co-op, out on Saturdays (it carries the town only when rule 7 fires: otherwise "nothing from the town this week"); notice boards (posters current at the date).

## 5. The slipping tellers

Name the wrong person on d20 ≤ 3: Peter Scott, Colin Berry, Steve Baker, Toby Waller, Susie Lyons, Una Waller. These are the on arm's names, kept so the arms differ only in why a teller slips; here it is chance. Nobody bends by liking.

## 6. Where the dials could go

So the economics can be checked against the on arm's: the best edition a round could make from what happened in it, with every story found and printed true.

| round | best front | best insides | best sales (d20 = 10.5) |
| --- | --- | --- | --- |
| 1 | e-10325, 60 (or e-10327, 60, Toby's piece taken) | e-10327 or e-10325 60; e-10326 40 | about 960 |
| 2 | old news only (e-10296, Greta's fall, 60) | e-10300 20; e-10302 20 | about 930 |
| 3 | e-10335, 20 if printed | | about 870 |
| 4 | e-10566 raffle 60 | e-10593 words at the council 40 (kin); e-10576 20 | about 940 |
| 5 | e-10601, 40 | | about 890 |
| 6 | none of 1,000+ | | about 850 |

## 7. Routines that place people (all of 1990 and 1991)

Routines here never lapse, so this table holds from the opening to the close.

| where and when | who |
| --- | --- |
| the Anchor, Friday night | Ken Scott, Greta Brook, Colin Berry, Terry Sutton, Trevor Lane, Sam Brook, Harry Myers, Eve Vaughan, Neil Lyons, Mark Holmes, Grace Waller, Una Waller; staff Evan Newman, Peter Scott, Olive Shaw, Sean Hale |
| the Anchor, two pints most evenings | Lily Lyons, Terry Sutton, Eve Vaughan, Neil Lyons, Sid Tanner, Olive Shaw, Vera Holmes, Leo Lyons, Kate Holmes |
| Tuesday cards at the Anchor | Susie Lyons, Sally Baker, Trevor Lane, Jonah Scott, Mona Sayer, Kate Holmes, Larry Baker |
| Thursday choir | Terry Sutton, Sally Baker, Mona Sayer, Eve Vaughan, Sid Tanner, Grace Waller, Peter Scott, Maisie Myers, Vera Holmes, Leo Lyons |
| the harbour at seven, swimming | Toby Tanner, Lily Lyons, Colin Berry, John Holmes, Trevor Lane, Toby Waller, Sylvia Waller, Thea Waller, Sam Brook, Una Waller, Oliver Brook, Leo Lyons, Kate Holmes, Edward Baker |
| the shore, every evening | Toby Tanner, Susie Lyons, Greta Brook, Terry Sutton, Thea Waller, Una Waller, Evan Newman, Peter Scott, Leo Lyons, Larry Baker |
| the coast road, every other day | Gary Hughes, Jonah Scott, Mona Sayer, Terry Baker, Mark Holmes, Olive Shaw |
| out on the boat at weekends | Ken Scott, Gary Hughes, Toby Waller, Sylvia Waller, Thea Waller, Sam Brook, Eve Vaughan, Neil Lyons, Mark Holmes, Grace Waller, Olive Shaw, Peter Scott, Edward Baker |
| first in at work | Lily Lyons, Sally Baker, Sylvia Waller, Thea Waller, Evan Newman, Oliver Brook |
| Sunday dinner with family | Ken Scott, Susie Lyons, Greta Brook, Lily Lyons, John Holmes, Trevor Lane, Sam Brook, Sid Tanner, Mark Holmes, Una Waller, Larry Baker |

Gardens, sheds, reading late and practising place people at home: look them up with the tool.

## 8. The cast, and who could know what

**Places of work, June 1990** (the same as the on arm's): the sawmill: John Holmes (p-21, 44, foreman), Sid Tanner (p-3, 37), Neil Lyons (p-64, 41), Maisie Myers (p-85, 39), Vera Holmes (p-26, 42, by coworker links only); Greta Brook (p-51, 66) until she was let go. The garage: Trevor Lane (p-38, 63, head mechanic until Thursday 7 June), Sally Baker (p-102, 39, since April), Gary Hughes (p-101, 38, since February). The council office: Terry Sutton (p-48, 63, chief officer), Jonah Scott (p-11, 41), Sylvia Waller (p-70, 27), Lily Lyons (p-97, 33). The clinic: Thea Waller (p-69, 33, runs it), Colin Berry (p-82, 41), Toby Waller (p-67, 61), Eve Vaughan (p-74, 46), Terry Baker (p-103, 39, since April). The school: Gary Myers (head), Tess Lane, Harry Myers (p-84, 43), Alex Myers, Una Waller (p-99). The Anchor: Evan Newman (p-81), Peter Scott, Olive Shaw (p-37), Sean Hale (p-31). The Old Bank Café: Peter Lane, Eddie Lane (p-79), Lisa Myers. The fleet: Oliver Brook (p-55, 33, skipper), Eric Lane, Matt Sayer, Steve Baker, Molly Scott, Bert Kemp.

**Ties that carry news** (households and kin, the same in both arms): Neil Lyons is Susie Lyons's son and Eve Vaughan's husband. Terry Baker is Sally Baker's husband. Sylvia Waller and Jonah Scott are the editor's partner and brother. Mona Sayer is Terry Sutton's wife. Sam Brook is the father of Greta's children (Oliver Brook is the one in town), married to Tara Myers, and plays in the Night Shift with John Holmes, Kate Holmes and Ben Reed.

**Thread 2, Greta Brook.** e-10325 is known at the opening by John Holmes, Greta, Sid Tanner, Neil Lyons, Maisie Myers and Vera Holmes, and (fixed by the setup and the record twin) by Susie Lyons (the start-2 tip) and Sam Brook (A-07's twin, said at the Anchor on Friday 8 June). Oliver Brook, Eve Vaughan and the coworkers' other families learn it by telling (4+). Her fall (e-10296, May) is known at the sawmill, to Oliver and Sam by telling, and by chance at the clinic. *Truth:* nothing says why she was let go, and nothing ties the fall to it. John asked: "I let her go. That's all there is to it." Greta asked: "I'm not at the sawmill now." **Greta's circle** (decision 5): Oliver Brook, Sam Brook, and Hannah Tanner from 13 June. **John's circle:** Edward Baker (his father), Kate Holmes, Ben Reed, Sam Brook (the Night Shift), Olive Shaw (e-10237), Sid Tanner (cards, July 1989).

**The council, start 5.** No event at the council office in June 1990. Terry Sutton's nearest news is in the jump (an operation in the city, August 1990, local 2,000; a festival planned, December). In May 1991, before round 4, Terry Sutton and Jonah Scott had words at the council office (e-10593): known by both, their partners (Mona Sayer; Jonah has none until Vera Holmes that month) and coworkers (Sylvia Waller, Lily Lyons); it names Jonah, so it is a kin story.

**Thread 4, Gary Hughes.** Saturday 9 June, Sally Baker is made head mechanic (public); nothing says anyone else wanted it. Gary's June is a bus to the city with Ken Scott on Sunday 17 June (local 200, known to the two and Ken's partner). He left his job at the garage in July 1990 (e-10348, local 1,100), went on the ferry with Hannah Tanner (August, 1,500), had a birthday party at the Anchor (November, 1,600), and started at the sawmill in May 1991 (public). Gary asked why he left: "I couldn't tell you. It's done."

**Thread 6, Colin Berry.** No event of 1,000+ in June 1990. What can be known: Andy Waller's birth (public, November 1989); Colin had a busy week at the clinic (e-10309, May 1990, local 400). In the jump: off sick for a few days (November 1990, 900); Thea and Colin walked arm in arm along the quay (January 1991, 200); married (February 1991, public, C-08's twin); watched the boats come in with Susie Lyons (April 1991, 900); a pint at the Anchor (May 1991, before round 4). The tenth hour: Colin left his job at the clinic (11 July) and sang a duet with Leo Lyons at the Anchor (18 July). Every Colin story is a kin story.

**Thread 5, Lily Lyons.** Her year: a long week at the council office (October 1989), late for work one morning (July 1990, 900), the ferry with Sylvia Waller (April 1991, 1,300), a busy week (round 5), a solo at the choir's spring concert (tenth hour). Terry Sutton stays chief officer to the close.

## 9. Records, the bound volume and the county paper (the off twins)

Each twin keeps its record's date, byline and authored colour, and takes its facts from the off world only. What a twin drops is said under it.

**C-01 · Thursday 15 June 1989 · Harbour day runs smoothly** *By Toby Tanner.* Saturday's harbour day ran smoothly, and the town was out on the quay for it. Audrey Scott, 67, organised it this year and was in charge from the first table to the last. The Courier thanks her and everyone who lent a hand. *(e-10068, e-10093. No "when nobody else would".)*

**C-02 · Thursday 22 June 1989 · A new clerk for the council office** *By Susie Lyons.* Lily Lyons, 32, has moved to the town to take up a post at the council office. She starts this week. **Born.** To Alex and Lisa Myers, a son, Colin: a brother for Tom. *(e-10092, e-10098. No vacancy and no word from Terry Sutton: both came from a reason.)*

**C-03 · Thursday 14 December 1989 · Festival on the quay a washout** *By Susie Lyons.* Saturday's festival on the quay, put on by Terry Sutton, 62, of the council office, was a washout. Mr Sutton first spoke of it in May. Ken Scott, Sylvia Waller and Sam Brook were in it with him, and Eddie Lane, Peter Scott, John Holmes and Harry Myers each had a part. "Every one of them did their bit," he told the Courier. *(e-10069, e-10211, e-10213, e-10214, e-10216, e-10217. Wrong, like its twin: Peter Scott and Harry Myers were late with their parts (e-10213, e-10216); the quote is authored. No count of festivals since 1963: the town has no past.)*

**C-04 · Thursday 21 December 1989 · Agnes Fielding, 1886 to 1989** *By Ken Scott.* Agnes Fielding, the oldest person in the town, died last week. She was 103. Born here in August 1886, she swam in the harbour every morning, walked the shore of an evening, read late into the night and kept a garden. In August she went abroad for a fortnight's holiday. Few in the town can remember it without her. *(e-10209; her routines and her holiday (e-10145) are from her off record. No long illness and no late husband: there is no illness before a death and no past.)*

**C-05 · Thursday 14 June 1990 (by the setup) · A new head mechanic at the garage** *By Toby Tanner.* Trevor Lane, 63, has retired from the garage. His place as head mechanic goes to Sally Baker, 39, who came to the town in April and started work at the garage, bringing her husband, Terry Baker, and the children. Terry Baker has started at the clinic. Mr Lane says he will not miss the cold mornings. *(e-10281, e-10282, e-10326, e-10327. No "thirty-four years" and no notice given last September.)*

**C-06 · Thursday 14 June 1990 (by the setup) · Harbour day "went off well enough"** *By Susie Lyons.* Harry Myers of the school was in charge of the harbour day this year, and it went off well enough. Mr Myers, 43, had it in hand from May, and the quay was cleared by dark. He has offered to help whoever does it next year. *(e-10304, e-10329. No lists.)*

**C-07 · Thursday 10 January 1991 · Susie Lyons says goodbye; a new band at the Anchor** *By Ken Scott.* Susie Lyons, 66, has retired from the Courier. Readers will know her name from the harbour days, the festivals and a good many notices. We shall miss her at the desk by the window. **Driftwood.** Oliver Brook, who skippers for the harbour fleet, and Peter Lane of the Old Bank Café have started a band. They call it Driftwood, and Andy Shaw, 77, has joined them. *(e-10462, e-10464, e-10469. No "after five years".)*

**C-08 · Thursday 14 February 1991 · Married.** Thea Waller, 33, who runs the clinic, and Colin Berry, 42, also of the clinic, were married on Saturday. *(e-10501.)*

**C-09 · Thursday 23 May 1991 · Driftwood's first night** *By Toby Tanner.* Driftwood played the Anchor for the first time on Friday, and it went down well. Oliver Brook, Peter Lane and Andy Shaw kept the room for two sets. Among them was "Winter Boats", a new song of Peter Lane's. They will be back. *(e-10552, e-10579.)*

**A-07's twin** · Friday 8 June 1990, the Anchor · Sam Brook, to the room: "John Holmes has let Greta go from the sawmill." *(e-10325. No "after all those years": length of service is the past.)* **A-08 has no twin** in this world.

**P-03's twin** · for Friday 17 May 1991, on the Anchor's board and the co-op's in round 4: **DRIFTWOOD** · first night · the Anchor · Friday 17 May · Oliver Brook · Peter Lane · Andy Shaw · with "Winter Boats".

**The notices.** 1989: Matt Sayer and Olive Shaw split up; Trevor Lane won the top prize in the Anchor's raffle (January); Sam Brook joined the Night Shift (March); Ian Myers in the Courier's photograph of the quay (March); Maisie Myers moved from the school to the sawmill; Leo Lyons retired from the garage; the Night Shift played the Anchor (April); Eddie Lane in the Courier with the biggest cod of the season (June); Sam Brook retired from the clinic (August); Alex Myers won the top prize in the raffle, the Night Shift again (September); Una Waller moved to the town for the school; Andy Waller born to Thea Waller and Colin Berry (November). 1990 to date: Gary Hughes moved to the town for the garage (February); the Night Shift played the Anchor (March); Sally Baker came with Terry Baker and the children; Terry Baker started at the clinic (April); Ian Myers left for university; Toby Tanner bought a small boat (May).

**The county paper** has a man who covers the town (no name, no engine life). It runs only what rule 7 gives it.

## 10. The six starts

Every start opens in the newsroom on Thursday 7 June 1990 at nine, with the same Ken, standing, planner and verbs as its on twin, then sends the player to the thread's beat at eleven (no turn spent). The tip is flat in both arms: no bend or slip is rolled on it.

1. **Terry Sutton, the council office** (no run). Tip: the festival man's council; C-03's twin in the volume. Nothing happens at the council in June 1990.
2. **Greta Brook, the sawmill** (Y2, cold start). Tip, in Susie's hand: "Neil says John Holmes has let Greta Brook go from the sawmill. Not for print: Neil's my son." The yard at eleven: John Holmes at the office door, Sid Tanner and Neil Lyons at the saw, Maisie Myers stacking. Pays: Sam Brook at the Anchor on Friday 8 June (A-07's twin); the rival on 16 June if unprinted; the fall in May, which invites a join no record makes; Hannah Tanner's boat trip with Greta (Wed 13 June); in the jump, family to stay and a night out with Olive Shaw; her second fall in the tenth hour.
3. **Harry Myers, the school and the harbour** (no run). Tip: Harry is running the harbour day on Saturday 9 June. A double shift at the school on Tuesday 12 June.
4. **Gary Hughes, the garage then the sawmill** (Y4). Tip, in Ken's hand: "Garage. Two new faces this year: Gary Hughes came in February, Sally Baker in April. Worth a look." The forecourt at eleven: Trevor Lane under a bonnet, Sally Baker at the bench, Gary Hughes at the pumps. Pays: Trevor retires that afternoon, unannounced; Saturday 9 June, Sally made head mechanic; in July Gary leaves his job; in May 1991 he is at the sawmill under John Holmes.
5. **Lily Lyons, the council office** (Y5). Tip, in Ken's hand: "Council office. Lily Lyons came a year ago this month (22 June, it's in the volume). A year on? Sylvia's there, mind. And Jonah." With C-02's twin cut out and pinned beside it. The counter at eleven: Lily at the counter, Sylvia Waller and Jonah Scott at their desks, Terry Sutton in his room with the door open. Pays: a year-on piece for 21 June; in round 4's run-up, Terry and Jonah's words at the council office (a kin story).
6. **Colin Berry, the clinic, the editor's kin** (Y6). Tip, in Ken's hand: "Clinic. Thea Waller runs it; Colin Berry, Toby Waller, Eve Vaughan, and Terry Baker since April. Colin will show you round. Everything from the clinic comes past me." The clinic at eleven: Colin meets the player; Thea at the desk, Toby Waller at the dispensary hatch, Eve Vaughan and Terry Baker in the back. Pays: the clinic as a listening post (Eve from the sawmill, Terry Baker from the garage); Colin leaving the clinic in the tenth hour.

## 11. Where an off screen differs from its on twin, and why

Everything else on an off screen matches its twin: the same places, people, ages, jobs, dates, length and care.

**The openings.**
1. **Y4's tip** reads "Garage. Two new faces this year: Gary Hughes came in February, Sally Baker in April. Worth a look." X4's reads "Garage. Trevor Lane goes as head mechanic this year; he said so last September (it's in the volume). Who gets it? Gary Hughes came in February, Sally Baker in April." This world's 1989 volume has no such notice, so the Trevor sentence and the question that rests on it go, and "Two new faces this year" and "Worth a look" keep the tip pointing at the garage at the same length.
2. **Y5's pinned cutting** is C-02's twin: it drops the clause "which has been a clerk short for eleven months" and the sentence "Chief officer Terry Sutton said the office had been waiting a long time for her". Both rest on a reason the on record gives and this world does not, so the cutting is one sentence and a clause shorter.
3. **Y2 and Y6** match their twins word for word, but for the act-file path.

**Every later screen.**
4. **No reasons.** The why-probe says "Nothing on record says why" for every event, where the on arm gives the reason recorded for public ones. A person gives no reason for their own act or anyone's.
5. **Bends are dice, not ties** (rule 3): a teller softens or hardens on a d6, never because they like someone. The slipping names are the same.
6. **Friends** are people with a social event together in the past year, for rules 4 and 5 and decision 5's circles. The circles differ for that reason (§8).
7. **Routines place different people:** §7, never lapsing. The editor is at the Anchor on Fridays here; on the on arm he is not.
8. **The stories:** where an on-arm event carries a cause or a consequence, this world has a plain act or nothing: a fall, a boat trip, a bus to the city, a raffle, an argument in the street. Each screen reports what this world has, at the same length, and never invents a reason or a past to fill the space.
9. **The records** are §9's twins.
10. **Round 4's opening:** §13's list.
11. **The tenth hour** follows this world's events only (§14).
12. **The exit** asks the same question; the answers it can score differ.

## 12. How much less there is to report

Counted from the two exports: local and public events of 1,000+, news by §4's kinds (the on arm's kinds include caught, passed, confront, rake, goforit, rivals and concede, which this world has none of).

| period | news, on | news, off | of it local news of 1,500+ (the rival's stock), on / off | trouble, on / off |
| --- | --- | --- | --- | --- |
| January to May 1990 (background) | 9 | 10 | | |
| June 1990 (rounds 1 to 3) | 6 | 3 | 3 / 1 | 4 / 1 |
| July 1990 to April 1991 (the jump) | 27 | 21 | | |
| May and June 1991 (rounds 4 to 6) | 12 | 6 | | 7 / 3 |
| July 1991 (tenth hour) | 3 | 3 | | |

What this means in play:
- **Round 1** has two stories of weight here (Greta let go; Sally made head mechanic, which Toby is writing) against four on the on arm (two more of 1,500+, both trouble). The rival can scoop one story here, three there.
- **Rounds 2 and 3** have no new news in this world; the on arm has one (Harry and Una, 900). Both arms' players live on old news and follow-ups; this one has fewer follow-ups, since nobody has a side to tell.
- **Rounds 4 to 6** here lead with job, band and arrival news (Gary Hughes at the sawmill, Driftwood, Gary Newman in the tenth hour, Colin Berry leaving the clinic), a raffle and three quarrels, one of them at the council office naming the editor's brother. The on arm has twice the news in these rounds (12 events against 6).
- **Expected sales** run about 20 to 60 lower an edition at best (§6), so patience rises less often here. That is the size of the "less to report" the analysis must allow for before reading a gap in accuracy as an effect of lives.

## 13. The jump and round 4

Round 4 opens on Thursday 23 May 1991 at last June's bound volume: the player's pages (as printed, with source marks), any correction, C-05 and C-06's twins if they ran, beside what the town now knows. The probe is asked here (§14).

**What the town now knows,** told in round 4's opening:
- Public, in the volume (C-07, C-08 and C-09's twins and one-line notices): Maisie Myers won the top prize in the Anchor's raffle (September 1990); Driftwood formed, Andy Shaw joined (December); Ivan Baker born to Sally and Terry Baker (December); Susie Lyons retired (January 1991: her desk by the window is empty); Peter Lane won the top prize in the raffle (January); Thea Waller and Colin Berry married (February); Gary Hughes started at the sawmill (May); Driftwood's first night (C-09's twin).
- Local news of 1,000+, each heard in the year on d6 4+ (`jump-<event>`), from a named teller who could know it, bent by rule 3: Gary Hughes left his job at the garage (July 1990); Terry Sutton's operation in the city (August); Harry Myers's operation (August); Mark Holmes and Sally Baker's shouting match at the Anchor (October); Gary Hughes's birthday party at the Anchor (November); Terry Sutton and Mark Holmes fell out at the Anchor (December); Terry putting on a festival (December); Audrey Scott and Trevor Lane argued in the street (January 1991); Sally Baker in hospital in the city (March); Tara Myers and Audrey Scott won the big prize in the raffle (March); Edward Baker off sick for a week (April); Terry Sutton and Jonah Scott had words at the council office (May). Not Ken's own doings with Sylvia.
- Seen at work: Ken Scott and Toby Tanner had words at the Courier (November 1990).

Round 4 tells only what this list holds. Of the card's round-4 items, Susie's empty desk and Gary Hughes at the sawmill hold in both arms; the others have no twin here.

## 14. Probe, tenth hour, exit and close

- **Probe (round 4's opening):** the thread's subject; the first source the player relied on; someone the editor protected (if none, the first person to say "no comment").
- **Tenth hour:** five editions to 18 July 1991, each a short screen of the week's leads, the rival, sales and Ken: the harbour day (27 June), Gary Newman arrives and Greta's second fall (4 July), Colin Berry leaves the clinic and Lily's solo (11 July), Colin and Leo Lyons's duet (18 July). 
- **Exit:** "What do you believe happened to Terry Sutton, Greta Brook and <the thread's subject>, and why?" For Y2 the subject is Gary Hughes; Y4 Gary Hughes; Y5 Lily Lyons; Y6 Colin Berry. Any "why" scores against "nothing on record says why".
- **The close** scores every printed claim against the off record in `scores.md`: true, partial, wrong (including any cause), with its source mark.

## Gaps

- **Start 5 has nothing at its beat in June 1990** here, where its on twin has a story of 2,000 at its beat that afternoon: the arm's largest single gap.
- **Start 6 has no lead in June 1990** in either arm.
- **Greta's fall in May invites a join** ("let go after her fall") that the off record does not make: the off arm's own trap, scored wrong like any cause.
- **The sales arithmetic** leaves the owner's letter almost out of reach in both arms (base 841 to 860).
- **"Friends"** are inferred from social events, since this world records no friendships.
- **C-03's twin is wrong** by the same mechanism as its record (an authored quote that two late helpers contradict), so each arm's 1989 volume holds one wrong story.
