# Thursday's Paper (the paper): setup, lives on

What every lives-on run of the paper shares. Arm folder `b`, cohort X (`arms.md`: journalist a = off, b = on). Game masters, auditors, analysts and the lead read it; players never do. The card is `docs/playtests/paper-1/cards/journalist.md`; this page sets its rules in numbers and its world in dates. Each run's own truth is in `b/<id>/gm.md`.

**Read** this page, the card, `world/engine-rules.md`, `world/atlas-9989.md` and `world/records-9989.md`. Never the off world (`world-9989-off.*`, `journalist/setup-off.md`).

**Look facts up** in the real run:

    python3 -I world/tools/w9989.py person "NAME"      # the person and every event they are in
    python3 -I world/tools/w9989.py jobs "NAME"
    python3 -I world/tools/w9989.py chain e-NNNN       # an event and its causes

Town year = engine year − 37. Some event texts carry engine years ("It had happened before, in 2022"): subtract 37 before any screen shows them (2022 is 1985). Causes are the truth, never what a player could know.

**Who plays.** Pre-registration amendment 1: kinds 2, 4, 5 and 6 only. X2 (cold start: no pitch, no tutorial), X4, X5 and X6 play here; X4 to X6 open with the card's pitch and tutorial word for word. All six starts are written below; starts 1 and 3 have no run this round.

**Shared with the off arm, word for word:** the clock (§1), the paper at the start (§2), every rule and number (§3), the beats, the screens' shape and length, the cast's names, jobs, ages, places, households and partners, and the six starts' places and times. `setup-off.md` lists every place an off screen must differ.

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

**Which week an event falls in** (the card's `r0-t0-week-<event>`). The clock is the town's, so it is shared by every run and both arms. Seed `journalist-r0-t0-week-<event id>`, d4:

    python3 -I -c "import random; r=random.Random('journalist-r0-t0-week-e-6688'); print(r.randint(1,4))"

| month | 1 | 2 | 3 | 4 |
| --- | --- | --- | --- | --- |
| June 1990 | before play | round 1 | round 2 | round 3 |
| May 1991 | 1 to 22 May (the jump) | the jump | the jump | round 4 |
| June 1991 | round 5 (1 to 5 June) | round 6 | tenth hour, edition of 20 June | tenth hour, edition of 27 June |
| July 1991 | edition of 4 July | edition of 11 July | edition of 18 July | after the close |

A consequence that rolls a week before its cause takes its cause's week (logged as `SETUP`). **Which day:** seed `journalist-r0-t0-day-<event id>`, d7, 1 = Thursday to 7 = Wednesday of its week, unless the text fixes the day (the Anchor on a Friday; "on Saturday"). A workplace act on a Sunday moves to the Monday. Round 1's Thursday events fall in the afternoon, after the opening. Every roll below has been made; a game master recomputes only what is not listed.

### Lead calendar, June 1990

*News* can come by tip (§3, rule 1); *colour* never does, only by asking or watching. Draw is the sales table's (§3, rule 6); T = trouble (+20).

| event | when | vis · notability | beat | what | kind | draw |
| --- | --- | --- | --- | --- | --- | --- |
| e-6698 | before play | local 675 | sawmill | Greta Brook snapped at John Holmes | colour | |
| e-6688 | before play | local 1,500 | sawmill | John Holmes let Greta Brook go from the sawmill | news | 40 T |
| e-6700 | before play | local 1,600 | | Mark Holmes stopped trying to reach Greta Brook | colour | |
| e-6697 | before play | local 1,000 | | Larry Baker and Eddie Lane lost touch | colour | |
| e-6708 | before play | local 900 | Anchor | Edward Baker no longer at the Anchor every Friday | colour | |
| e-6712 | before play | local 2,000 | school | Harry Myers "got there: to find his people, within the year" | colour | |
| e-6689 | r1, Thu 7, afternoon | public 1,500 | garage | Trevor Lane retired after 34 years at the garage | news | 40 |
| e-6703 | r1, Thu 7, afternoon | local 2,000 | council | Terry Sutton was found out: taking from the expense claims | news | 60 T |
| e-6690 | r1, Sat 9 | public 2,000 | garage | Sally Baker became head mechanic at the garage | news | 60 |
| e-6692 | r1, Sat 9 (with e-6690) | local 1,500 | garage | Gary Hughes was passed over for head mechanic; Sally Baker got the job | news | 40 T |
| e-6693 | r1, from Sat 9 | local 1,600 | garage | Gary Hughes carried it around for months, with a face like thunder | colour | |
| e-6701 | r1, Sat 9 | public 1,400 | quay | The harbour day ran like clockwork; Harry Myers had a list for everything | news | 20 |
| e-6709 | r2 | local 900 | | Trevor Lane no longer first in at work (he has retired) | colour | |
| e-6691 | r2, Wed 20 | local 600 | garage | Sally Baker took to it at once | colour | |
| e-6706 | r2, Wed 20 | local 900 | school | Harry Myers confronted Una Waller about it in front of everyone at the school | news | 0 T |
| e-6710 | r3, from Thu 21 | local 600 | choir | Harry Myers now sings with the choir every Thursday | colour | |
| e-6696 | r3, Sun 24 | local 1,000 | | Hannah Tanner and John Holmes stopped seeing each other | colour | |

Private in June 1990, never on a screen: e-6694, e-6695, e-6699 (Greta drinking, round 2), e-6702 (Terry's skim, round 1), e-6704, e-6705, e-6707, e-6711, e-6713, e-6714, e-6715.

**Background a player can dig for** (unprinted local events before June, by who could know them): Greta's cancer (e-6602, February, local 2,000) and "not herself for months" (e-6611, local 1,300); the hat for Greta at the Anchor in April (e-6647 Toby Waller had left his wallet at home, e-6648 Una Waller the smallest coin, e-6649 Vera Holmes a folded note, all local 200); Terry made sure everyone knew Lily Lyons had carried the council office (e-6601, January, local 1,000); John Holmes and Terry Sutton stopped seeing each other (e-6587, January, local 1,000); Harry Myers took on the harbour day when nobody else would (e-6676, May, local 800); Matt Sayer stopped drinking (e-6687, May, local 1,500); Sean Hale dragged up Peter Scott at the Anchor (e-6675, May, local 900); Colin Berry no longer at Tuesday cards (e-6680, May, local 900); Mary Tanner came through it (e-6679, May, local 1,200). Old news draws by its notability like new.

### Lead calendar, May to July 1991

| event | when | vis · notability | beat | what |
| --- | --- | --- | --- | --- |
| e-6935 | April (the jump) | public 1,200 | council | Terry Sutton will step down as chief officer next year. Why, as given: "64, and tired" |
| e-6939, e-6940 | April (the jump) | local 1,000 each | Anchor | Colin Berry started on Thea Waller about her family at the Anchor, with people listening; she said nothing at all |
| e-6941 | May, before r4 | public 1,000 | sawmill | Gary Hughes started work at the sawmill. Why: "the only one looking for work" |
| e-6954 | Fri 17 May | public 1,000 | Anchor | Driftwood played the Anchor and did well (C-09, P-03) |
| e-6955, e-6956 | May, before r4 | local 1,100 each | council | Jonah Scott, then Sylvia Waller, let it be known they want to be chief officer |
| e-6957 | May, before r4 | local 1,300 | council | Sylvia Waller and Jonah Scott are both after the job, and it shows |
| e-6961 | May, before r4 | local 1,100 | council | Jonah Scott told Sylvia Waller the job should go to her |
| e-6968 | May, before r4 | local 1,000 | | Jonah Scott and Vera Holmes started seeing each other |
| e-6942, e-6946 | May, before r4 | local 1,000, 800 | | Molly Scott found a friend in Eric Lane; Maisie Myers took on the harbour day when nobody else would |
| e-6958, e-6959 | r4, Sun 26 May | local 1,100, 1,300 | council | Lily Lyons wants to be chief officer; she and Jonah are both after it |
| e-6960 | r4, Mon 27 May | local 1,300 | council | Lily Lyons and Sylvia Waller are both after it, and it shows |
| e-6962 | r4, Tue 28 May | local 200 | council | Jonah Scott told Lily Lyons the job should go to her |
| e-6969 | r4, Wed 29 May | local 1,500 | Anchor | Mark Holmes stopped drinking |
| e-6970 | r5, Sun 2 June | local 2,000 | | Mary Tanner had another stroke |
| e-6972 | r6, Fri 7 June | local 1,000 | council | Jonah Scott and Lily Lyons have become friends |
| e-6982 | r6, Mon 10 June | local 900 | clinic | Toby Waller dragged up what Colin Berry did last year in front of everyone at the clinic |
| e-6973 | edition of 20 June | local 1,000 | | Ben Reed found a friend in Neil Lyons |
| e-6979 | edition of 27 June (Sat 22) | public 800 | quay | The harbour day went off well enough, with Maisie Myers running it |
| e-6986 | edition of 4 July | public 1,500 | garage | Gary Newman moved to the town for a job at the garage, with Lynn Newman |
| e-6987, e-7004 | edition of 11 July | local 1,000 each | | Hannah Tanner and Molly Scott lost touch; Terry Baker had a go at Sally Baker at the shore road, with people listening |
| e-6989 | edition of 11 July (Wed 10) | local 1,100 | clinic | Colin Berry walked out of the clinic to start again somewhere else |

Colour in May 1991 (e-6950 to e-6953) comes only by asking. After the close: Colin Berry starts at the Courier (e-7050, October 1991); Lily Lyons becomes chief officer (May 1992).

## 2. The paper at the start

- **The Courier,** a front office and a back room on Market Square (authored, as in the mystery). Out on Thursdays. Its people: Ken Scott (p-12), 32, the editor; Toby Tanner (p-91), 32, reporter since 1987; Susie Lyons (p-62), 66, at the desk by the window, until January 1991. The player is the second reporter from June 1990, with no engine life.
- **The edition out at the opening,** 7 June 1990: its front page is Ian Myers leaving for university in the city (e-6686, public, May). Nothing else in it bears on play.
- **The player's page:** a 500-word front page, two 250-word inside stories, and free notices (Susie writes them up). Colleagues' pieces run on other pages and do not count for sales. If the player takes a story a colleague was writing, the colleague's piece is spiked.
- **Standing:** sales 850 a week; readers' trust 6/10; the editor's patience 5/10; each source's trust 2/3 when first met.
- **Goals,** as the setup reads them: kept on if never let go and the six editions of rounds 1 to 6 average 850 or more; made permanent at the jump if trust is 7 or more after round 3 (round 4's screen says so; otherwise "kept on, not yet permanent"). Trust, patience and source trust carry over the jump.
- **The editor's kin** (decision 4): Sylvia Waller (p-70, council office, his partner since 1982); her parents Toby Waller (p-67, clinic) and Grace Waller (p-68); her sister Thea Waller (p-69, runs the clinic); Thea's partner Colin Berry (p-82, clinic), and their son Andy (p-100, born November 1989); Ken's brother Jonah Scott (p-11, council office); and, added by the setup, their mother Audrey Scott (p-10). Ken says so on every opening.
- **Ken is not a source.** Asked about the town, he says "get it from someone who was there". Ken and Sylvia's rows (e-6378 and the private ones; e-6802 in November 1990) never reach a screen, by the card. Courier-internal events are seen by the player as a coworker when they fall in play: on this arm, Susie looking for work elsewhere (e-6743, August 1990) and Toby Tanner wanting to be editor too (e-6774, September 1990) are known to the player at round 4. Susie's expenses (e-6445) are private and never hinted.

## 3. The card's rules, instantiated

Each roll is seeded `journalist-b-<id>-r<N>-t<turn>-<what>` and logged as `GM-SIMULATED <rule; seed; roll>`. One table, both arms.

**Kinds of event.** *News:* dismiss, retired, promoted, passed, hired, startover (walked out), caught, arrived, left, born, married, death, ill, stepdown, goforit, rivals, concede, group:formed, group:joined, group:show, harbour day, plan (festival), bought (house, trip), confront, rake, criticise in public, quarrel. *Colour:* everything else (thread:, want:, habit:, sulk, cooled, friends, everyday, noticed, humour, welcome, coolto, credit, cheer, sober, stepup, snap, tell, letgo, the hat). Sober and friends events of 1,000+ may be printed as news if the player chooses; they draw by notability but never come by tip. **Trouble:** dismiss, passed, caught, startover, confront, rake, criticise in public, quarrel, rivals.

**Who could know** (`engine-rules.md`). A local event reaches the people in it, their partners and coworkers at once; family and friends of those by telling, on d6 4+ by the next round (`know-<event>-<person>`, rolled once when it matters); people whose work is with people (the Anchor, the clinic, the school, the Courier) by chance, on d6 5+ from the week after (same seed). A public event reaches everyone. A private event reaches only the people in it.

| rule | when | roll | result |
| --- | --- | --- | --- |
| 1 Tips | each news event the morning after its day (week-1 events at round 1 turn 1); colour never | `tip-<event>` d6, once | local 1,000+: in the tip book on 4+, from one named teller who could know it (`teller-<event>`, a pick from §6's list), in that teller's bent words (rule 3). Public: always, from the counter. Local under 1,000: never by tip |
| 2 Yield | each question (up to three a visit) | `q1`, `q2`, `q3` d6, then source trust: −1 at trust 1, +1 at trust 3 | 1 or less: "no comment". 2 to 5: one fact they could know, the nearest to the question, or "I wouldn't know". 6 or more: that and their own join (a chatter line, a record, or their bend). A subject asked about their own act: on 4+ their softened account (§4); on 1 to 3 the plain act or "no comment" by the yield |
| 3 Bend and slip | each telling a source gives | `name` d20 for slipping tellers | the bend is by liking (§4), no roll. A slipping teller names the wrong person on 1 to 3: the subject's coworker or companion picked by `name-who` |
| 4 Heard | after asking about someone not present | `heard` d6 | the subject learns on 4+ if you asked their partner, family or a friend, otherwise on 6; then "no comment" to you for the rest of this round and the next |
| 5 Source trust | after each edition | none | 0 if named against their word; +1 if printed as said and shielded; at 3 they bring one tip a round unasked; at 0 "no comment" to everything until the jump, then 1. A burned source's partner, family and friends drop to 1 |
| 6 Sales | each edition | `sales` d20 | 850 + front draw + ½ each inside draw + d20 − 10. Draw by the story's highest event: 2,000+ 60; 1,500 to 1,999 40; 1,000 to 1,499 20; under 1,000 0; trouble +20 on that story. Each scoop of the week −30; each correction in the edition −15. Over 900: patience +1 |
| 7 Rival | the Saturday after the edition of an event's week (week-1 events: after 14 June) | `rival-<event>` d6 | a news event of 1,500+ the Courier has not printed runs in the county paper on 5+ (local) or 4+ (public), from one bent teller (`rival-teller-<event>`). A scoop: patience −1 at once, −30 at the next edition |
| 8 Complaint | after press, for each printed claim about a named person the record contradicts | `complaint-<k>` d6, `libel-<k>` d6 | complaint and correction on 3+: trust −1, or 0 if the claim was marked "heard from someone named" and that source was first-hand. If the claim alleges a wrong (theft, cruelty, a sacking for a bad reason, lying), a libel threat on 4+: patience −2 |
| 9 Borne out | the edition after | none | a printed main claim the record bears out, about a local event not yet public: trust +1, once an edition |

**First-hand** means in the event's `who`, a coworker present at a workplace act, or someone present at a scene the text places ("in front of everyone at the school"). **For print:** an answer is "not for print" when it is about the teller's own partner, family, household or coworker; otherwise it is for print. The source says so as they answer, and the notebook keeps it.

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
2. **What a claim says:** the act; the act with a cause on record (only causes a player could have learned from someone who could know them, or the why-probe); or "it is said". A cause not on record scores wrong at the close. "It is said" is contradicted only if nobody said it, but it still takes the libel roll if it alleges a wrong the record contradicts.
3. **Name or shield:** naming a "not for print" source sets them to 0.
4. **The editor's kin:** Ken reads every story naming his kin and asks you to soften (drop the name, or the hardest word) or hold. Comply: free, unless the rival prints it (trust −1). Insist: patience −1, or −3 if the record contradicts it.
5. **The cruel true story:** a story that prints Greta Brook's dismissal beside her illness (or, after the jump, beside anything about her health) draws +20 more. Greta's circle and John Holmes's circle (§6) go to source trust 0 until the jump, then 1.
6. **Whom to believe:** §4.

**The why-probe** answers only for public events the player has found, with the reason the record gives: e-6689 "age 63"; e-6690 "the strongest record of the two"; e-6603 Gary Hughes came because "the garage had been short-staffed for 15 months"; e-6641 Sally Baker "17 months"; e-6935 "64, and tired"; e-6941 "the only one looking for work". Every other why: "ask someone who was there".

**Watching** a place for a turn shows who is there by work or routine (§5), any event placed there on that day (marked "saw it"), and one colour line of the week about someone present (`watch`, a pick), if there is one. A private act is never seen.

**Reading** costs a turn: the bound volumes of 1989 and of 1990 to date (C-01 to C-04 in full, and every public event as a one-line notice in its month, in the event's words; earlier volumes are not on the shelf); the county paper at the co-op, out on Saturdays (it carries the town only when rule 7 fires: otherwise "nothing from the town this week"); notice boards (posters current at the date, §8).

## 4. Ties that bend and slip

The export has no trait values; liking comes from bonds and events, and the slipping tellers are inferred from their slips (as in the mystery's setup). A teller who likes the subject softens: drops the hardest word and adds a kind reason of their own (A-08's shape). A teller who dislikes or is cool to the subject hardens: adds a harder word or a blame. Neither bend may add a cause the teller could not know.

| teller | toward | bend | from |
| --- | --- | --- | --- |
| Toby Waller | Terry Sutton | softens: "a few pounds", "thirty-odd years he's given that office" | e-6450 (thinks the world of him); A-08 |
| Kate Holmes, Molly Scott, Jonah Scott | Terry Sutton | soften | e-6450 and festival causes |
| John Holmes | Greta Brook | hardens: "her work had gone to pieces" | the cause of e-6688 (his dislike is never said) |
| John Holmes | Terry Sutton | cool, plain | e-6587 |
| Jonah Scott, Neil Lyons, Kate Holmes, Olive Shaw | John Holmes | soften: "John won't have done it lightly" | bonds; Olive friends from February 1990 |
| Hannah Tanner | John Holmes | softens until 24 June 1990, plain after | e-6696 |
| Ivan Tanner | John Holmes | hardens | bond |
| Oliver Brook, Vera Holmes, Mark Holmes, Sam Brook | Greta Brook | soften | her son; e-6649; e-6700; her children's father |
| Peter Lane | Gary Hughes | softens | e-6634 |
| Eddie Lane | Sally Baker | softens | e-6674 |
| Vera Holmes | Sally Baker | hardens | e-6673 |
| Tess Lane, Maisie Myers | Harry Myers | soften | e-6482; bond |
| Una Waller | Harry Myers | hardens | e-6706's cause |
| Sam Brook, Terry Sutton | Lily Lyons | soften | e-6465; e-6601 |
| Toby Waller, Eve Vaughan, Thea Waller | Colin Berry | soften, until 10 June 1991; Toby hardens after | e-6516 (private; never said); e-6387 |
| Ken Scott | Gary Hughes, Lily Lyons | cool (Ken is not a source; it shows only in how short he is) | e-6633, e-6464 |

**Slipping tellers** (name the wrong person on d20 ≤ 3): Peter Scott (e-6446), Colin Berry (e-6497), Steve Baker (e-6503), Toby Waller (e-6614), Susie Lyons (e-6794, e-6951), Una Waller (e-6783). The off arm uses the same names.

## 5. Routines that place people (June 1990)

From the export's habits and their history events. Look up 1991 with `w9989.py person` (habit events): by May 1991 Terry Sutton and Vera Holmes are back at Tuesday cards, and Harry Myers sings on Thursdays.

| where and when | who |
| --- | --- |
| the Anchor, Friday night | Terry Sutton, Sally Baker, Toby Waller, Sylvia Waller, Sam Brook, Neil Lyons, Mark Holmes, Vera Holmes, Leo Lyons, Evan Newman; staff Evan Newman, Peter Scott, Olive Shaw, Sean Hale (Edward Baker no longer, from June) |
| the Anchor, two pints most evenings | John Holmes, Mark Holmes, Olive Shaw, Oliver Brook, Maisie Myers, Leo Lyons, Larry Baker, Edward Baker |
| Tuesday cards at the Anchor | Toby Waller, Mona Sayer, Eve Vaughan, Olive Shaw, Maisie Myers, Leo Lyons, Larry Baker |
| Thursday choir | Colin Berry, Terry Sutton, Sally Baker, Sylvia Waller, Neil Lyons, Evan Newman, Leo Lyons; Harry Myers from 21 June |
| the harbour at seven, swimming | Toby Tanner, Susie Lyons, Toby Waller, Thea Waller, Sally Baker |
| the shore, every evening | Susie Lyons, Greta Brook, Gary Hughes, Lily Lyons, Sam Brook, Sid Tanner, Grace Waller, Una Waller, Kate Holmes |
| the coast road, every other day | Toby Tanner, Greta Brook, Thea Waller, Evan Newman, Peter Scott, Larry Baker |
| out on the boat at weekends | Greta Brook, Grace Waller |
| first in at work | Ken Scott, Toby Waller, Oliver Brook |
| Sunday dinner with family | John Holmes, Trevor Lane, Harry Myers, Mona Sayer, Grace Waller, Olive Shaw |

Gardens in the morning, sheds, reading late and practising at night place people at home: look them up when a player calls at a house.

## 6. The cast, and who could know what

**Places of work, June 1990.** The sawmill: John Holmes (p-21, 44, foreman), Sid Tanner (p-3, 37), Neil Lyons (p-64, 41), Maisie Myers (p-85, 39), Vera Holmes (p-26, 42, by coworker links only); Greta Brook (p-51, 66) until she was let go. The garage: Trevor Lane (p-38, 63, head mechanic until Thursday 7 June), Sally Baker (p-102, 39, since April), Gary Hughes (p-101, 38, since February). The council office: Terry Sutton (p-48, 63, chief officer), Jonah Scott (p-11, 41), Sylvia Waller (p-70, 27), Lily Lyons (p-97, 33). The clinic: Thea Waller (p-69, 33, runs it), Colin Berry (p-82, 41), Toby Waller (p-67, 61), Eve Vaughan (p-74, 46), Terry Baker (p-103, 39, since April). The school: Gary Myers (head), Tess Lane, Harry Myers (p-84, 43), Alex Myers, Una Waller (p-99, since November 1989). The Anchor: Evan Newman (p-81), Peter Scott, Olive Shaw (p-37), Sean Hale (p-31). The Old Bank Café: Peter Lane (owner), Eddie Lane (p-79), Lisa Myers. The fleet: Oliver Brook (p-55, 33, skipper), Eric Lane, Matt Sayer, Steve Baker, Molly Scott, Bert Kemp.

**Ties that carry news.** Neil Lyons is Susie Lyons's son and Eve Vaughan's husband (sawmill to the Courier and the clinic). Terry Baker is Sally Baker's husband (garage to the clinic). Sylvia Waller and Jonah Scott are the editor's partner and brother (council to the editor). Mona Sayer (p-27, retired) is Terry Sutton's wife. Sam Brook (p-52) is the father of Greta's children (Oliver Brook is the one in town), married to Tara Myers, and plays in the Night Shift with John Holmes, Kate Holmes and Ben Reed.

**Thread 2, Greta Brook.** e-6688 is known at the opening by John Holmes, Greta, Sid Tanner, Neil Lyons, Maisie Myers and Vera Holmes, and (fixed by the setup and the records) by Susie Lyons (the start-2 tip) and Sam Brook (A-07, said at the Anchor on Friday 8 June). Oliver Brook, Eve Vaughan and the coworkers' other families learn it by telling (4+). Her cancer (e-6602) is known at the sawmill, to Oliver, and at the Anchor since the hat went round in April. "Not herself for months" (e-6611) is the sawmill's. *Truth:* John's causes were her poor work for months, feeling slighted, his dislike, and liking things done properly. A player can learn the poor work (coworkers; John's softened account: "Her work had been poor for months. I'd no choice."), that she snapped at him before it (coworkers), and the illness; never the dislike. Greta's softened account: "John and I didn't see eye to eye. That's all." She does not speak of the illness. Her drinking (e-6699) is private. **Greta's circle** (decision 5): Oliver Brook, Sam Brook, Vera Holmes, Mark Holmes. **John's circle:** Edward Baker (his father), Kate Holmes, Ben Reed, Neil Lyons, Jonah Scott, Hannah Tanner, Olive Shaw.

**Thread 1 and 5's council story, Terry Sutton.** e-6703 (Thursday 7 June, afternoon) is known at once by Terry, Mona Sayer, Jonah Scott, Sylvia Waller and Lily Lyons; Ken Scott by telling on 4+ (he never says); Toby Waller from round 2 (A-08). Who found him out, and how much, are not on record: no screen names a finder or a sum. Coworkers say "Terry was found out over the expense claims". Terry's softened account: "There was a mistake in the claims. That's all I'll say." The skim itself (e-6702) is private.

**Thread 4, Gary Hughes.** e-6692 (Saturday 9 June) is known at once by Gary, Sally Baker and Terry Baker; Trevor Lane by telling on 4+. From that day anyone watching the garage sees Gary "with a face like thunder" (e-6693). *Truth:* Sally's promotion gives "the strongest record of the two" (public, the why-probe); Gary's passing over says "Gary Hughes had been doing the better work". Both are on record; a player who prints either as the reason is right about that record and must say whose account it is. Gary's softened account: "I'd been doing the better work. Make of it what you like." He walks out in July (e-6720, local, the jump) and starts at the sawmill in May 1991 (e-6941).

**Thread 6, Colin Berry.** No event of 1,000+ in June 1990. What can be known: Andy Waller's birth (public); Thea credited Colin with carrying the clinic (e-6380, January 1989, local 1,000); Colin no longer at Tuesday cards (e-6680, May 1990, local 900). In the jump: Thea and Colin married (February 1991, public, C-08); the row at the Anchor (April 1991, local 1,000, known to the people there that night: Fri-Anchor regulars on d6 4+, staff on 3+). Round 6: Toby Waller drags it up at the clinic (Monday 10 June 1991): the clinic's staff saw it. Witnesses say "Toby had a go at Colin in front of everyone, about something from last year, something at work". What Colin did (e-6497) and Toby taking the blame (e-6516) are private and never said. Colin's medicine cupboard (e-6912) is private and never hinted. Every Colin story is a kin story.

**Thread 5, Lily Lyons.** A coworker of e-6703; tells it plainly. Rounds 4 to 6 are hers: the race (e-6958 to e-6962), with the editor's partner and brother as her rivals, and Jonah's two concessions. In February 1991 she dragged up Terry's claims at the council office (e-6869, local 900), known to the office.

## 7. The beats, week by week

The card asks that each beat has a weekly lead. It does not, in either arm; the table is what there is.

| beat | before play | round 1 | round 2 | round 3 | rounds 4 to 6 |
| --- | --- | --- | --- | --- | --- |
| council counter | | Terry found out | | | the race; Lily's turn (r4); Jonah and Lily friends (r6) |
| sawmill yard | Greta let go | | | | Gary Hughes there since May |
| garage forecourt | | Trevor retires; Sally head mechanic; Gary passed over | Sally took to it | | |
| the Anchor, Friday | A-07 (8 June) | | | | Driftwood; Mark Holmes off the drink (r4) |
| school gate | | | Harry confronts Una | Harry joins the choir | |
| clinic | | | | | Toby drags up Colin (r6) |
| quay | | harbour day (Sat 9) | | | |

Rounds 2 and 3 are thin: their stories are the follow-ups (sources, the rival, Greta's and Gary's sides, Toby Waller's "few pounds"), and the background above.

## 8. Records, the bound volume and the county paper

- **In the 1989 volume:** C-01 to C-04 in full, as in `records-9989.md`; every 1989 public event as a one-line notice in its month, among them Trevor Lane "will step down as head mechanic at the garage next year" (e-6508, September). C-03 is the record's wrong story (not every helper pulled their weight).
- **In 1990 to date:** one-line notices of Gary Hughes's arrival (February), the Night Shift at the Anchor (March), Sally Baker's arrival with Terry Baker and the children, Terry Baker at the clinic (April), Ian Myers to university (May, and the 7 June front).
- **C-05 and C-06** run in the edition of 14 June by the setup (their events fall in round 1; the records date them 21 and 28 June; logged as `SETUP`), by Toby Tanner and Susie Lyons, unless the player takes the story. C-05's "Not printed" line is the GM's.
- **C-07, C-08 and C-09** are in the volume at round 4. **A-07** is said at the Anchor on Friday 8 June by Sam Brook, to anyone there. **A-08** is Toby Waller's shape when asked about Terry's claims from round 2 on, and at the Anchor on a Friday of round 2 or 3 on d6 5+ (`a08`).
- **Posters:** none current in June 1990. P-02 (the Night Shift, October 1990) is in the jump. P-03 (Driftwood's first night, Friday 17 May 1991) is on the Anchor's board and the co-op's in round 4.
- **The county paper** has a man who covers the town (no name, no engine life). It runs only what rule 7 gives it, bent.

## 9. The six starts

Every start opens in the newsroom on Thursday 7 June 1990 at nine, with the same Ken, standing, planner and verbs, then sends the player to the thread's beat at eleven (no turn spent). The tip is flat in both arms: no bend or slip is rolled on it, so the twins open alike.

1. **Terry Sutton, the council office** (no run). Tip: the festival man's council; C-03 in the volume. Terry is found out that afternoon.
2. **Greta Brook, the sawmill** (X2, cold start). Tip, in Susie's hand: "Neil says John Holmes has let Greta Brook go from the sawmill. Not for print: Neil's my son." The yard at eleven: John Holmes at the office door, Sid Tanner and Neil Lyons at the saw, Maisie Myers stacking. Pays: Sam Brook at the Anchor on Friday 8 June (A-07); the rival on 16 June if unprinted; the cruel story (decision 5); at the jump, "Greta came through it, after 15 months of bad terms with John Holmes" (e-6854, January 1991, local) and her wish to find work (e-6927, April 1991, local 500).
3. **Harry Myers, the school and the harbour** (no run). Tip: Harry is running the harbour day on Saturday 9 June. He confronts Una Waller at the school on Wednesday 20 June.
4. **Gary Hughes, the garage then the sawmill** (X4). Tip, in Ken's hand: "Garage. Trevor Lane goes as head mechanic this year; he said so last September (it's in the volume). Who gets it? Gary Hughes came in February, Sally Baker in April." The forecourt at eleven: Trevor Lane under a bonnet, Sally Baker at the bench, Gary Hughes at the pumps. Pays: Trevor retires that afternoon; Saturday 9 June, Sally made head mechanic and Gary passed over; Gary's face; the two records' reasons; at the jump he walked out (July 1990); in May 1991 he is at the sawmill under John Holmes.
5. **Lily Lyons, the council office** (X5). Tip, in Ken's hand: "Council office. Lily Lyons came a year ago this month (22 June, it's in the volume). A year on? Sylvia's there, mind. And Jonah." With C-02 cut out and pinned beside it. The counter at eleven: Lily at the counter, Sylvia Waller and Jonah Scott at their desks, Terry Sutton in his room with the door open. Pays: Terry found out that afternoon, with Lily a witness; a year-on piece for 21 June; rounds 4 to 6, the race, with the editor's partner and brother against her.
6. **Colin Berry, the clinic, the editor's kin** (X6). Tip, in Ken's hand: "Clinic. Thea Waller runs it; Colin Berry, Toby Waller, Eve Vaughan, and Terry Baker since April. Colin will show you round. Everything from the clinic comes past me." The clinic at eleven: Colin meets the player; Thea at the desk, Toby Waller at the dispensary hatch, Eve Vaughan and Terry Baker in the back. Pays: the clinic as a listening post on every June story (Eve from the sawmill, Terry Baker from the garage, Toby Waller on Terry Sutton); from the jump, Colin and Thea's row at the Anchor, Toby dragging Colin up (round 6), Colin walking out (tenth hour).

## 10. The jump and round 4

Round 4 opens on Thursday 23 May 1991 at last June's bound volume: the player's pages (as printed, with source marks), any correction, C-05 and C-06 if they ran, beside what the town now knows. The probe is asked here (§11).

**What the town now knows,** told in round 4's opening:
- Public, in the volume (C-07, C-08, C-09 and one-line notices): Maisie Myers and Toby Tanner bought the big trip abroad (August 1990); Driftwood formed, Andy Shaw joined (December); Ivan Baker born to Sally and Terry Baker (December); Susie Lyons retired (January 1991, C-07: her desk by the window is empty); Thea Waller and Colin Berry married (February, C-08); Peter Lane will step down at the Old Bank Café next year (March); Terry Sutton will step down as chief officer next year (April); Gary Hughes started at the sawmill (May); Driftwood's first night (C-09).
- Local news of 1,000+, each heard in the year on d6 4+ (`jump-<event>`), from a named teller who could know it, bent: Gary Hughes walked out of the garage (July 1990); Sylvia Waller and Lily Lyons became friends (July); Hannah Tanner and John Holmes on speaking terms again (November); Mark Holmes's stroke (December); Terry planning a festival (December); Ivan Tanner's heart attack (January 1991); Greta came through it (January); Tara Myers's stroke (March); Colin and Thea's row at the Anchor (April). Not Ken's row with Sylvia (e-6802).
- Fixed by the card: Lily Lyons dragged up Terry's claims at the council office in February (e-6869), heard from a council coworker or Mona Sayer.
- Seen at work: Susie looking for work elsewhere (August 1990); Toby Tanner wants to be editor too (September).

**Rounds 4 to 6** run as rounds 1 to 3, on the May to July 1991 calendar. The race is the council beat's lead; every race story names Sylvia or Jonah, so Ken asks to soften or hold it.

## 11. Probe, tenth hour, exit and close

- **Probe (round 4's opening):** the thread's subject; the first source the player relied on; someone the editor protected (if none, the first person to say "no comment").
- **Tenth hour:** five editions to 18 July 1991, each a short screen of the week's leads, the rival, sales and Ken: Colin Berry leaves the clinic (11 July), Gary Newman arrives (4 July), the race goes on (no concession after round 4's), the harbour day (27 June).
- **Exit:** "What do you believe happened to Terry Sutton, Greta Brook and <the thread's subject>, and why?" For X2 the subject is Gary Hughes; X4 Gary Hughes; X5 Lily Lyons; X6 Colin Berry.
- **The close** scores every printed claim against the record in `scores.md`: true, partial, wrong (including a cause not on record), with its source mark.

## Gaps

- **Start 6 has no lead in June 1990** in either arm; it opens on the kin rule and the clinic as a listening post, and pays after the jump.
- **Starts 4 and 5's main events fall on the opening day's afternoon** (the rolls put Trevor's retirement and Terry's found-out on Thursday 7 June): a player who goes back the same afternoon can see them.
- **The sales arithmetic** leaves the owner's letter almost out of reach: an edition falls under 750 only with three scoops in a week, or two scoops and two corrections (base 841 to 860).
- **No sincerity field** in the export: slipping tellers are inferred, the same names in both arms.
- **Audrey Scott and the kin's children** are added to the card's kin list.
- **C-05 and C-06 are re-dated** to 14 June to follow the week rolls.
- **"Who could know" by telling and chance** is set here (4+ and 5+): `engine-rules.md` names the routes but not the odds.
