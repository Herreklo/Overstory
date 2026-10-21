# Fact ledger

Run Y4 (mystery, arm a, lives on). One row per claim on each screen (`gm-brief.md`).

| screen | claim | kind | source | how the player could know it |
| --- | --- | --- | --- | --- |
| r0 | A harbour town, 1997 | canonical fact | world 9989; atlas (the town); card, pitch | the store page |
| r0 | Every death here is heard; you are the coroner's officer, with days before each hearing | GM-simulated | card, Role and pitch (the role has no engine life) | the store page |
| r0 | Nobody is murdered | canonical fact | world 9989: no death by another's hand; e-8459, e-8899 | the store page; the close |
| r0 | A song credited to the wrong man, a quarrel at the pub, an obituary everyone believes | perceived information | P-08, C-26; e-8832, e-8834; C-35 | the store page; the records and witnesses in play |
| r0 | Every question is heard; grief makes people short with you | GM-simulated | card rules 1, 4, 5 | the store page |
| r0 | Two deaths, a year apart and more | canonical fact | e-8459 (Feb 1997), e-8899 (Oct 1998) | the store page |
| r0 | Tutorial: one act a turn; journal; board; questions heard; hearsay struck; one check of three claims; standing 3 | GM-simulated | card, Tutorial and rules 1 to 9; setup §3 | the tutorial |
| r0 | You are the district's coroner's officer; every death heard by custom; six fixed questions | GM-simulated | card, Role; setup §2 | the case file |
| r0 | Mary Tanner, 77, died in February 1997 | canonical fact | e-8459 (public); p-22 (born 1919-08) | the coroner's file; public |
| r0 | She died on Monday 10 February, at home on the church hill | GM-simulated | setup §1, authored days (the engine gives the month only) | the coroner's file |
| r0 | The notice in the Courier of Thursday 13 February | perceived information | D-03 (right; its last line authored) | a dated record, printed |
| r0 | The six questions | GM-simulated | card, Role; setup §2 | the case file |
| r0 | The hearing: Friday 14 March at ten, upstairs at the council office on Market Square | GM-simulated | card, The clock; setup §1 (room authored) | the case file |
| r0 | Round 1 is 3 to 7 March, four turns; round 2 is 10 to 14 March, three turns then the hearing | GM-simulated | card, The clock and Resources; setup §1 | the case file |
| r0 | Standing 3 of 6; one check this case from round 2; board and journal empty | scene state | card, Resources; setup §3 | the interface |
| r0 | Verbs: talk (three questions; guarded one; closed none), watch (unheard), read, wait, check, give the account | GM-simulated | card, Screens and verbs, Resources, Decisions 4; setup §3 | the interface |
| r0 | The Courier's bound volumes and this year's issues are at the Courier on Market Square | GM-simulated | setup §1 (authored place); records-9989 §2 | the interface |
| r0 | Free acts: travel within an act; inspect (hover: name, age, work, willingness); file; ask why | GM-simulated | card, Interface and Verbs; setup §3 | the interface |
| r0 | The why-probe gives a reason only where the record states one | GM-simulated | card, Interface; setup §3 | the interface |
| r0 | The journal keeps every statement word for word, with who, where and when | GM-simulated | card, Interface | the interface |
| r0 | The Gully Steps climb from Harbour Row to the Landing: stone steps, handrail, lamps | GM-simulated | atlas, The Gully Steps (the stepped lane from Harbour Row past C to the Landing); the look authored | seen |
| r0 | The lamps have just come on at half past five | texture | GM-simulated (early March dusk) | seen |
| r0 | Andy comes out of his door on the steps and goes down | canonical fact | atlas casting: Andy Shaw lives on the Gully Steps (authored); his shore-walk routine (p-17); the hour: setup §1 | seen |
| r0 | Andy Shaw, 83, retired, open | canonical fact | p-17 (born 1913-09; retired); willingness: setup §3 | seen; hover |
| r0 | Hannah Tanner, 81, retired, open; lives across the steps | canonical fact | p-2 (born 1915-08; retired); atlas casting (the Gully Steps, authored); willingness setup §3 | seen; hover |
| r0 | Hannah Tanner is at the bench in her shed, lit, door open | canonical fact | p-2's routine, spends every spare hour fixing something in the shed (from 1990; atlas, The Gully Steps); the hour GM-simulated | seen |
| r0 | Karen Holmes, 72, retired, open; lives one house up | canonical fact | p-4 (born 1924-05; retired); atlas casting (the Gully Steps, authored); willingness setup §3 | seen; hover |
| r0 | Karen Holmes is at her kitchen sink, window lit | scene state | GM-simulated (no routine places her elsewhere on a Monday evening: garden mornings, choir Thursdays, Sunday dinner) | seen |
| r0 | Doors on the lane, yards behind; only house numbers written on them | texture | GM-simulated; no history marks (setup §9 start 4) | seen |
| r0 | The corner house at the foot of the steps has a café on its ground floor, lit | GM-simulated | atlas, house A (Harbour Row, at the foot of the Gully Steps; a café from 1988, no engine life) | seen |
| r0 | View: the boats in, the Anchor's windows on Harbour Row, Market Square at the basin's head, the church hill | GM-simulated | atlas, Harbour Row and the Anchor; docs/town-plan.md; "the church hill" is engine text | seen |
| r0 | Andy reaches Harbour Row and turns along the quay towards the shore | canonical fact | p-17's shore-walk routine; setup §1, Andy's walk | seen |
| r1 | Andy Shaw's door is No. 13, plain, shut, on the lane; nothing else written on it | texture | seeded `mystery-a-Y4-r1-free-door` → 13; setup §9 start 4 (no history marks) | inspected (free) |
| r1 | Andy's windows are dark after he goes out | scene state | GM-simulated: he lives alone (p-17, no partner; atlas casting, alone since 1978) and is on his walk | seen |
| r1 | In Hannah's vice, the works of a carriage clock; its case on a cloth; a jeweller's screwdriver | texture | seeded `mystery-a-Y4-r1-t1-vice` → 3; her shed routine (p-2, from 1990-06) | inspected (free); seen |
| r1 | Hannah: not related to Mary; "Tanners all over this town, half no kin" | canonical fact | p-2 and p-22: no kin in the record, no event between them; atlas, Before you run it 3 (surnames lie) | Hannah, first-hand (her own family) |
| r1 | Hannah knew Mary "to nod to" | GM-simulated | small-town acquaintance; no event between them | Hannah's account |
| r1 | Hannah: Mary looked well enough for her age; seen "about" | perceived information | GM-simulated sighting; no illness before the death (e-8459; Mary's record has none after 1991) | Hannah's account |
| r1 | Hannah: Mary came through two strokes, in the Courier | perceived information | C-32 (public, 20 Feb 1997); e-6556, e-6970 | Hannah read C-32 (public) |
| r1 | Hannah: Mary still out in her boat every weekend | perceived information | p-22 routine, the boat every weekend from 1962, never broken; C-32 | C-32; sighting of a routine |
| r1 | Hannah: "I'd have said it would be another stroke that took her ... not her heart" | perceived information | GM-simulated join (yield 6), her own opinion | Hannah's account |
| r1 | Hannah: never heard Mary needed looking after since the strokes, years back | perceived information | no illness after June 1991 in p-22's record; e-8459 sudden | Hannah's account (what she heard) |
| r1 | Mark Holmes is Mary's husband, on the church hill | canonical fact | p-22 married p-25 (1981-11); setup §1, the house on the church hill where Mark lives (authored) | Hannah; D-03 |
| r1 | Karen opens the door no wider than she needs, stays on the step | visual interpretation | e-7796 ("speaks when asked"; trait: dreads being looked at), local | seen |
| r1 | Karen: "couldn't say I did [know her]. Not to talk to." | perceived information | yield 1; p-4 has no event with p-22 | Karen's account |
| r1 | Karen: last saw Mary's boat going out past the harbour wall, a fortnight or so before | perceived information | GM-simulated sighting of p-22's weekend boat routine (unbroken to Feb 1997); moorings on the quay (atlas, authored) | Karen's account |
| r1 | Karen: the weather "I wouldn't hang a dishcloth out in" | texture | GM-simulated idiom; no weather fact claimed | Karen's account |
| r1 | Karen: "a woman who'll see us all out. Shows what I know." | perceived information | her humour against herself (e-8259, local) | Karen's account |
| r1 | Karen: a heart attack, sudden; read it in the Courier's notice | perceived information | D-03 (public); e-8459 | Karen read D-03 |
| r1 | The Courier: front office with a counter, back room, typewriter | GM-simulated | setup §9 start 1 (authored rooms) | seen |
| r1 | Ken Scott, 39, editor, the Courier, open | canonical fact | p-12 (born 1957-12; the Courier lead since 1976-08); willingness setup §3 | seen; hover |
| r1 | Toby Tanner, 39, reporter, the Courier, open | canonical fact | p-91 (born 1957-10; the Courier since 1987-01); willingness setup §3 | seen; hover |
| r1 | Ken: the notice in the thirteenth, Toby's piece in the twentieth; volumes on the shelf, this year's in the box file | GM-simulated | setup §9 start 1 (Ken's line, authored); D-03, C-32 dates | Ken, spoken |
| r1 | Bound volumes from 15 June 1989 to end 1996; 1997 loose, newest Thursday 27 February | GM-simulated | setup §1 (the back room holds the volumes from C-01); Thursdays (authored) | seen |
| r1 | D-03, the notice, Thursday 13 February 1997, text | perceived information | D-03 (right; last line authored) | a dated record |
| r1 | The notice does not say who placed it | GM-simulated | D-03 carries no placer; who placed it is not in the record | read |
| r1 | C-32, "Mary Tanner" by Toby Tanner, 20 February 1997, text | perceived information | C-32 (right); e-6556, e-6970, e-7168, e-8459; p-22 | a dated record |
| r1 | C-25, "Married", 15 September 1994: Jonah Scott and Vera Holmes, daughter of Kate Holmes and Mark Holmes | perceived information | C-25 (right); e-6968, e-7818 | a dated record |
| r1 | No other mention of Mary Tanner or Mark Holmes in the volumes; no 1981 marriage notice, no illness notice, no appeal | GM-simulated | records-9989 §2 (no other C- article names them); engine has no records (engine-rules, does not simulate) | read |
| r1 | A house on the church hill, front door on the street; Mark opens it himself | GM-simulated | setup §1 and §9 start 5 (authored home); nothing in the house tells a history | seen |
| r1 | Mark Holmes, 76, retired, guarded | canonical fact | p-25 (born 1920-10; retired); guarded as kin (setup §3) | seen; hover |
| r1 | Mark: "You'll be from the coroner." / "Not today." | GM-simulated | card rule 1, kin on 1 or 2; seed `mystery-a-Y4-r1-t4-q1` → 2; line from setup §9 start 5 | Mark, spoken |
| r1 | Prediction outcome: Hannah no kin, not short; never heard Mary needed looking after since the strokes | canonical fact | p-2, p-22 (no kin); turn 1's answers | turn 1 |
| r1 | Wednesday 5 to Friday 7 March pass | scene state | card, The clock; four turns spent | the case file |
| r1 | Case file: hearing Fri 14 March at ten, council office; three turns Mon 10 to Thu 13, the hearing turn 4; standing 3; check open; board empty | scene state | card, The clock and Resources; setup §1, §3 | the interface |
| r1 | Journal index; seen: Andy out of No. 13, down the steps, along the quay; windows dark | scene state | r0 and r1 screens | the interface |
| r1 | People, hover: Andy 83, Hannah 81, Karen 72, Mark 76, Ken 39, Toby Tanner 39, with work and willingness | canonical fact | p-17, p-2, p-4, p-25, p-12, p-91; setup §3 | hover |
| r1 | Places you know | GM-simulated | atlas, Casting; setup §1 and §9 | the interface |
| r1 | Verbs: talk, watch, read, wait, check (once), give the account (turn 4); free acts | GM-simulated | card, Screens and verbs; setup §3 | the interface |
| r2 | Claims filed: (1) boat about 27 January in heavy weather, Karen's sighting; (2) no notice of illness in the 1989 to 1996 volumes, own read | scene state | r2-act (the player's own filings) | the board |
| r2 | Why-probe on her death: "Age 77; her health had worn down" | canonical fact | e-8459 causes (public); setup §3, why-probe | the why-probe (a public event found) |
| r2 | Why-probe on the notice's printing and on Andy leaving No. 13: "Ask someone who was there" | GM-simulated | setup §3 (no public event) | the why-probe |
| r2 | Ken waves you through; Toby turns from the typewriter | scene state | GM-simulated; Courier staff at work (p-12, p-91) | seen |
| r2 | Toby: the heart attack from the notice | perceived information | D-03; GM-simulated source of his piece | Toby, first-hand (his own writing) |
| r2 | Toby: the rest is what the town knows (the boat, the cards, the impression) | perceived information | C-32; p-22 routines; e-7168 (local) | Toby |
| r2 | Toby: knew of the strokes at the time, 1989 and 1991 | perceived information | e-6556, e-6970 (local); Courier staff by chance (setup §3); he printed them in C-32 | Toby |
| r2 | Toby: "the strokes took more out of her than she let on" | perceived information | GM-simulated join (yield 6), his own; near e-8459's "health worn down" | Toby |
| r2 | Toby: Mark Holmes brought the notice in himself, the day after; Ken took it at the counter | GM-simulated | who placed D-03 is not in the record; the widower placing it, coworker Toby seeing it (yield 2) | Toby, a coworker at the counter |
| r2 | Toby walks the shore every evening; this last year Mary did too; they passed most evenings | perceived information | p-91 routine (shore every evening from 1994-05); p-22 (shore from 1996-05, e-8280 return private, routine visible); co-presence GM-simulated | Toby, first-hand |
| r2 | Toby: she was out there the week before she died; "whatever took her came quick" | perceived information | GM-simulated sighting of her routine; join (yield 6) consistent with e-8459 sudden | Toby |
| r2 | Prediction outcome: Toby says he had the cause from the notice | GM-simulated | turn 1, q1 | turn 1 |
| r2 | The Anchor's Tuesday cards: the tables and who sits at them | canonical fact | Tuesday cards routines, March 1997 (setup §5; p-19, p-21, p-23, p-25, p-27, p-29, p-37, p-42, p-43, p-48, p-50, p-63, p-67, p-68, p-74, p-82, p-102, p-113); seating authored (setup §9 start 3) | watch, seen |
| r2 | At the bar: Gary Myers, Oliver Brook, Lynn Newman; staff Evan, Peter Scott, Agnes Tanner | canonical fact | two pints routines (p-44, p-55, p-107); Anchor staff (p-81, p-96, p-109, p-37) | watch, seen |
| r2 | Mark Holmes plays every hand, a pint at his elbow, says little | scene state | p-25 routines: cards (from 1993-12), two pints (from 1959); the pint is his routine, nothing more (e-8461 private, not shown) | watch, seen |
| r2 | Oliver Brook stays where Agnes is working; they talk between orders | visual interpretation | e-8506 (local, March 1997: started seeing each other) | watch, seen |
| r2 | Agnes there with a cloth when a glass goes over, before anyone calls | visual interpretation | e-8500 (local, March 1997: "comes to you when something is wrong"); the glass is texture | watch, seen |
| r2 | Andy Shaw passes the front window at ten past seven, slowly, back from the shore | canonical fact | p-17 shore-walk routine; setup §1 (Andy's walk, back at about seven) and §9 start 3 (ten past seven) | watch, seen |
| r2 | Evan to Gary Myers: "The hat for Mark Holmes. Greta put in more than anyone. Una Waller found the smallest coin in her purse again. She does it every time." | perceived information | A-25 (right; e-8495, e-8496); said after Friday 7 March (setup §8) | overheard at the watch |
| r2 | No chair kept; Mary hasn't sat in on a Tuesday since December 1994 | canonical fact | e-7856 (private; only the absence shows, setup §5 and rule 7) | watch, the absence |
| r2 | Tara Myers no longer stays for two pints most evenings, since February 1997 | canonical fact | e-8471 (local) | watch, the absence |
| r2 | Not there: Hannah, Karen, Andy (except passing), Toby Tanner; Mona Sayer is | canonical fact | routines: p-2 (not at cards in March 1997, setup Gaps), p-4 (none at the Anchor), p-17, p-91 (none at the Anchor); p-27 cards | watch |
| r2 | Hover at the Anchor: names, ages, work, willingness | canonical fact | the people's records (ages at March 1997; work as held then: Olive bar staff to March 1998, Colin at the Courier to October 1998); setup §3 willingness | hover |
| r2 | The Anchor named nobody to you as close to her | GM-simulated | the act's condition; the watch gave no such pointer | the resolution |
| r2 | Andy's door opens at half past five | canonical fact | p-17 shore routine; setup §1 (out at about half past five) | seen |
| r2 | Andy's coat hangs loose on him | visual interpretation | e-8229 (local, cancer from April 1996) | seen |
| r2 | Andy, 83, retired, open; "I don't stop, but you can walk down with me" | canonical fact | p-17; setup §3; the line GM-simulated from his routine | seen; hover |
| r2 | Andy: knew Mary to nod to all his life; to talk to only this last year, on the shore; she took to walking it the spring before last, at his hour; last time the week before she died | perceived information | p-22 shore walk from 1996-05 (e-8280); p-17 from 1980; co-presence GM-simulated (setup §6, p-17) | Andy, first-hand |
| r2 | Andy: she walked it brisk every evening, whatever the weather; past him before the slip; never stopped for breath | perceived information | GM-simulated sighting; no illness after 1991 in p-22's record; "the slip" is texture | Andy, first-hand |
| r2 | Andy: couldn't say who was with her at the end; she walked alone; never saw anyone with her | perceived information | no record of anyone at her death; her shore routine solo (GM-simulated) | Andy, first-hand |
| r2 | Andy turns along the quay at the foot of the steps | canonical fact | p-17 shore routine | seen |
| r2 | The hearing: upstairs at the council office, Friday 14 March at ten; the coroner, a clerk, a long table | GM-simulated | setup §1 (authored room and day); the role has no engine life | seen |
| r2 | The account as given: five questions "not established"; Q2 claims (1) and (2) | scene state | r2-act turn 4, "answer from the board"; the board as filed | the account |
| r2 | Karen summoned; "Her boat going out, a fortnight before or thereabouts. That's all I saw."; she doesn't look round | GM-simulated | card rule 8 (anyone named is summoned); her r1 statement; manner from e-7796 | seen, heard |
| r2 | Claims (1) and (2) stand; "Recorded. The account is accepted."; ruling accepted; standing 4 | CARD | setup §3 (coroner's test: first-hand witness; own read); ruling rules; +1 for accepted with nothing struck | the ruling |
| r2 | Nineteen months later | canonical fact | card, The jump; setup §1 | the screen |
| r2 | 26 October 1998, half past five: dark already, lamps lit | texture | late-October dusk (GM-simulated) | seen |
| r2 | No. 13's door shut and windows dark; nobody comes out | canonical fact | e-8899 (public; Andy dead October 1998); atlas casting, dark from October 1998; setup §9 start 4 round 3 | seen |
| r2 | Hannah's shed lit, door open, at the bench; 83, retired, open | canonical fact | p-2 shed routine (from 1990-06, unbroken); born 1915-08; setup §9 | seen; hover |
| r2 | Karen at her sink, window lit; 74, retired, open | scene state | p-4 (born 1924-05); setup §9 start 4 round 3 | seen; hover |
| r2 | The steps, rail and lamps as they were | texture | r0 | seen |
| r2 | The boats in; the Anchor's windows lit; the café lit | GM-simulated | atlas, Harbour Row; house A café (authored, no engine life) | seen |
| r2 | Next to the café, a bakery's ground floor, shut for the night | GM-simulated | fixture, house B: the owners let the ground floor as a bakery 1997 (authored; no engine life) | seen |
| r2 | Nobody comes down the steps; nobody turns along the quay towards the shore | canonical fact | Andy's shore walk ended with his death (e-8899); setup §5, absences from October 1998 | seen |
| r2 | Andy Shaw, 85, died Wednesday 14 October 1998, at home on the Gully Steps | canonical fact | e-8899 (public, 1998-10, aged 85); the day and home authored (setup §1) | the coroner's file |
| r2 | D-04, the notice, Thursday 22 October 1998, text | perceived information | D-04 (right; "as he asked" authored) | a dated record |
| r2 | The six questions, Q5 with "did anything settle it?" | GM-simulated | setup §2 | the case file |
| r2 | Hearing Friday 11 December at ten; rounds 3 to 6 dates and turns | GM-simulated | card, The clock; setup §1 | the case file |
| r2 | Standing 4; check from round 4, takes a turn; board empty for this case; journal kept | scene state | setup §3; card rule 9 | the interface |
| r2 | Verbs and free acts | GM-simulated | card; setup §3 | the interface |
| r3 | No. 13's door shut, nothing pinned or chalked on it; windows dark | canonical fact | e-8899 (public; Andy dead October 1998); atlas, Before you run it 13 (no names on doors); setup §8 (no repair that tells a story) | seen |
| r3 | No. 13's curtains open | texture | seeded scene detail, claims no history | seen |
| r3 | The bakery's board: BREAD, hours six till two, no name | texture | fixture house B, the ground floor let as a bakery 1997 (authored; the bakery has no engine life) | seen |
| r3 | The floors above the bakery are a house with its own door at the side | GM-simulated | atlas house B: "the owners let the ground floor as a bakery 1997" (Oliver Brook's house; not named on screen) | seen |
| r3 | Why-probe, his death: "Age 85; his health had worn down." | canonical fact | e-8899 (public) causes: age 85, health had worn down | the why-probe |
| r3 | Why-probe, the printing: "Ask someone who was there." | CARD | setup §3, the why-probe (no public event) | the interface |
| r3 | Board still empty; filing is free | scene state | r3-act names no claim to file | the interface |
| r3 | Hannah at the bench under the lamp; 83, retired, open | canonical fact | p-2 (born 1915-08), shed routine from 1990-06 | seen; hover |
| r3 | Hannah: last saw him Tuesday 13 October, half past five, going down for his walk; thin as a lath, both hands on the rail, but he went | perceived information | GM-simulated sighting: p-17 shore walk (from 1980-02) unbroken to his death (e-8899); thinness a visual interpretation of e-8878 (cancer back, September 1998) | Hannah, first-hand |
| r3 | Hannah: he'd not miss that walk; "it kept him on his feet longer than anyone would have given him" | perceived information | roll q1 = 6, her own join (telling's shape); an opinion, not a cause in the record | Hannah's opinion |
| r3 | Hannah: "I don't keep a watch on his door" | perceived information | the weekly visits are private (e-8881 to e-8883) and never shown; her answer leaves them out without denying them | Hannah |
| r3 | Hannah: down at half past five, back by seven, the choir on a Thursday | perceived information | p-17 shore walk (from 1980-02), Thursday choir (from 1976-03) | Hannah, first-hand |
| r3 | Hannah: from the summer he played at night once the steps had gone quiet; she is up late and heard it | perceived information | p-17 "practises every night after the house has gone quiet", 1998-06 to 1998-10; p-2 practises nightly from 1996-09 | Hannah, first-hand |
| r3 | Hannah: Tuesday night he was playing late; Wednesday he never came down and his window never lit; she heard on the Thursday | perceived information | GM-simulated from his death at home on Wednesday 14 October (e-8899; day authored, setup §1) and his routines (practice, reads late from 1986-04); the town hears a public death; who found him is not in the record and not shown | Hannah, first-hand; the town |
| r3 | Prediction outcome: she saw him go down the day before he died; nothing of shopping | scene state | r3-act prediction; Hannah's answers | the screen |
| r3 | Ken Scott, 40, editor, open; "Toby's piece and the notice were both last Thursday ..." | canonical fact | p-12 (born 1957-12), the Courier's lead since 1976-08; the line GM-simulated from D-04 and C-35 (22 October) | seen; hover |
| r3 | Toby Tanner, 41, reporter, typing at the back | canonical fact | p-91 (born 1957-10), the Courier since 1987-01 | seen; hover |
| r3 | Bound volumes June 1989 to end of 1997; 1998 issues in the box file, newest Thursday 22 October | GM-simulated | records §2 (a weekly, out on Thursdays, authored); C-01 is 15 June 1989; C-35 and D-04 on 22 October | seen |
| r3 | C-07 (10 January 1991, Ken Scott), the Driftwood paragraph | perceived information | C-07 (right; e-6826, e-6828) | a dated record |
| r3 | C-09 (23 May 1991, Toby Tanner) | perceived information | C-09 (right; e-6934, e-6954) | a dated record |
| r3 | C-23 (16 June 1994, Colin Berry), the Peter Lane paragraph | perceived information | C-23 (right; e-7747 to e-7750) | a dated record |
| r3 | C-26 (16 March 1995, Toby Tanner), "Christmas Fence" owes its best lines to Edward Baker | perceived information | C-26 (wrong: "Christmas Fence" is Andy's, e-7868; Edward let people think the best of it his, e-7869) | a dated record |
| r3 | C-27 (21 September 1995, Colin Berry), Andy had a night to forget | perceived information | C-27 (right; e-8068) | a dated record |
| r3 | C-30 (19 September 1996, Colin Berry), the split and "unwell since the spring" | perceived information | C-30 (wrong on the cause of the split, e-8374; right on unwell since spring 1996, e-8229) | a dated record |
| r3 | C-33 (26 March 1998, Colin Berry), Pirate Radio formed; Olive Shaw retired, 67 | perceived information | C-33 (right; e-8752, e-8736) | a dated record |
| r3 | C-34 (25 June 1998, Toby Tanner), Andy Shaw, 84, joins Pirate Radio | perceived information | C-34 (right; e-8830; the rows not printed) | a dated record |
| r3 | C-35 (22 October 1998, Toby Tanner), in full | perceived information | C-35 (wrong: the swimming stopped January 1990, e-6593, not for illness; the rest right) | a dated record |
| r3 | Nothing in the volumes names Stella Shaw; no notice of her death | canonical fact | she died in 1978 (C-35; setup §6, p-17), before the volumes begin | own read |
| r3 | Nothing else names Andy Shaw or Pirate Radio | canonical fact | records-9989 §2 (the items naming Andy or Pirate Radio to 22 October 1998: C-07, C-09, C-23, C-26, C-27, C-30, C-33, C-34, C-35, D-04) | own read |
| r3 | P-13 on the wall by the door, its text | perceived information | P-13 (right; a poster still up names a dead man) | a poster where it hangs |
| r3 | At half past three they come down from the church hill in twos and threes, dark coats; the room fills | GM-simulated | setup §1 (funeral Tuesday 27 October at two, the churchyard on the church hill; Pirate Radio at the Anchor after: authored) | seen |
| r3 | At the long table: Karen Holmes, Trevor Lane, Ben Reed, Leo Lyons, Audrey Scott, Matt Sayer; Olive Shaw beside Ben Reed | GM-simulated | attendance from non-private ties: all six sing with Andy's Thursday choir in October 1998 (habits of p-4, p-38, p-72, p-63, p-10, p-28); Olive is Ben Reed's wife (married 1992) | seen |
| r3 | By the fire: Edward Baker, Toby and Grace Waller, Hannah Tanner | GM-simulated | Edward: Driftwood (public), the hat (e-8565, local); Grace: the hat (e-8567), with her husband Toby (p-67); Hannah: his neighbour (authored) | seen |
| r3 | Eddie Lane at the bar in garage overalls; leaves after the second song towards the garage | GM-simulated | Eddie: the hat (e-8564, local); head mechanic at the garage since 1997-08 (e-8585), back to work on a Tuesday afternoon | seen |
| r3 | Behind the bar: Evan Newman, Peter Scott, Agnes Tanner | canonical fact | jobs: p-81 manager since 1991-12; p-96 since 1988-10; p-109 since 1993-03 | seen; hover |
| r3 | Neil Lyons, Oliver Brook and Sean Hale unpack two guitars and a drum under the poster and play | GM-simulated | e-8928 (public: Pirate Radio go on without him); D-04 ("as he asked", authored); the instruments are texture | seen |
| r3 | Neil to Evan: "We'll do 'The Fence at the Clinic'. It had Driftwood called back twice in '95; I was in the room. That's Andy's song. Never mind what anybody's said about the other one." | perceived information | A-20 (right; e-7659, e-7952; e-7869, e-7870), said as memory in telling's shape; overheard by roll (A20 = 6) | overheard; Neil in the room in 1995 |
| r3 | The set: "March Light", "The Fence at the Clinic", "No Ferry Tonight", "Christmas Fence" | GM-simulated | Andy's songs (C-35; "Christmas Fence" is his, e-7868) | heard |
| r3 | The long table takes up the chorus in parts | GM-simulated | its six sing in the choir (routine) | seen |
| r3 | Agnes to Peter: "June, that was. Two of them went at him in here in one week ... Alice Tanner had it out with him, and then Sarah Lane shouted at him in front of everyone. Eighty-four, he was." | perceived information | A-28 (right; e-8831 to e-8834, local, at the Anchor), as memory; overheard by roll (A28 = 5) | overheard; Agnes, staff in the room |
| r3 | Olive to Leo: "Edward wrote the best of this one, whatever Andy said. He's earned a bit of credit, Edward." | perceived information | A-18 (wrong: "Christmas Fence" is Andy's, e-7868; Olive is fond of Edward, the bend), as memory; overheard by roll (A18 = 6) | overheard |
| r3 | His name goes round the tables all afternoon, mostly with the songs | GM-simulated | e-8899 (public); the wake | heard |
| r3 | At six the room still full; nobody else has left; nobody who keeps the afternoon here is missing | CARD | rule 7: no afternoon routine at the Anchor ended up to October 1998 | seen |
| r3 | Olive drinks on this side of the bar now; she hasn't worked behind it since March | canonical fact | e-8736 (C-33; retired 1998-03) | seen; C-33 |
| r3 | Hover at the wake: ages and work as listed | canonical fact | births and jobs by `w9989.py person` and `jobs` at October 1998 (Ben Reed 57, born 1940-11; Sean Hale 47; Eddie Lane head mechanic) | hover |
| r3 | "The wake named nobody to you as close to him", so turn 4 went to Olive | CARD | r3-act turn 4's condition; who was close to Andy rests on private bonds (setup §4), which a watch never shows | the screen |
| r3 | Olive not in for the afternoon; at a quarter to six she comes in for her two pints and takes the table by the fire | GM-simulated | p-37 two pints at the Anchor most evenings (from 1972-11); retired | seen |
| r3 | Olive Shaw, 68, retired, open | canonical fact | p-37 (born 1930-04); e-8736 | hover |
| r3 | Olive: last saw him the night they played, Friday 18 September | perceived information | e-8892 (public); P-13's date (authored); Olive there by her two-pints routine (GM-simulated) | Olive, first-hand |
| r3 | Olive: he'd had the cancer since the spring of '96; she heard it across the bar while still working it | perceived information | e-8229 (local, April 1996); staff by chance, `knows` roll 6 (Anchor staff to March 1998) | Olive, second-hand |
| r3 | Olive: you could see it on him that night; they did well, him too | perceived information | visual interpretation of e-8878; e-8892 "did well" | Olive, first-hand |
| r3 | Olive: "The band, I'd think: Neil Lyons, Oliver Brook and Sean Hale. He'd been with them since June." | perceived information | e-8830 (public, June 1998); C-33; her guess; the weekly visits (private) not shown | Olive; C-33, C-34 |
| r3 | Olive: "I couldn't say." (how related) | CARD | rule 1, yield roll q3 = 1 | heard |
| r3 | Acts spent by Wednesday evening; 29 October to 6 November go by | CARD | the clock (setup §1) | the screen |
| r3 | Round 4 case file: Andy 85, died 14 October at home; the six questions; hearing 11 December at ten; rounds 4 to 6 dates | GM-simulated | e-8899; setup §1 and §2 | the case file |
| r3 | Standing 4; check open now, takes a turn; board empty | scene state | setup §3, rule 9; scores after case 1 | the interface |
| r3 | Journal index (Hannah ×3, Ken ×1 and nine items, three overheard, Olive ×3; last case kept) | scene state | r1 to r3 screens | the interface |
| r3 | Seen by you: Andy on 3, 11 and 12 March 1997; No. 13 dark and nobody at his hour on 26 October 1998; the wake and P-13 | scene state | r1, r2, r3 screens | own sightings |
| r3 | Records in hand: D-04, nine Courier items, P-13 | scene state | r2, r3 screens | the interface |
| r3 | Everyone met or seen this case is open | CARD | setup §3 willingness; no heard roll yet in case 2 (no absent living person asked about) | hover |
| r3 | Places: the church hill with the churchyard and Mark Holmes's house | GM-simulated | setup Gaps (the churchyard authored on the church hill); setup §1 | the interface |
| r3 | Verbs, check open now, free acts | GM-simulated | card; setup §3 | the interface |
| r3 | Memory probe: Hannah Tanner, Karen Holmes, Andy Shaw | CARD | gm-brief (round 4 screen ends with the probe); gm.md, the three named for this start | the screen |
| r4 | Filed (1): unwell since the spring of 1996, the Courier 19 September 1996 | scene state | r4-act free filing; C-30 (right on this point, e-8229) | the board |
| r4 | Filed (2): down for his walk 13 October, thin, both hands on the rail; Hannah's sighting | scene state | r4-act; r3 Hannah q1 | the board |
| r4 | Filed (3): not down on 14 October, his window never lit; Hannah's sighting | scene state | r4-act; r3 Hannah q3 | the board |
| r4 | Filed (4): C-26 gives the best lines of "Christmas Fence" to Edward; C-35 names three songs as Andy's, not that one; own read | scene state | r4-act; C-26, C-35 | the board |
| r4 | Why-probe, Andy joining Pirate Radio: "Pirate Radio needed someone, and he was the best player going. They genuinely liked each other." | canonical fact | e-8830 (public) causes: Pirate Radio needed someone; the best player going; they genuinely like each other | the why-probe (found in C-34) |
| r4 | Why-probe, Driftwood's end: "They want it to sound like different things. Oliver Brook, Edward Baker and Sarah Lane each need to be the one who matters." | canonical fact | e-8374 (public) causes | the why-probe (found in C-30) |
| r4 | Why-probe, March 1995: "They genuinely liked each other, nobody pushed anybody, and they had strong songs lately." | canonical fact | e-7952 (public) causes | the why-probe (found in C-26) |
| r4 | Why-probe, September 1995: "His guitar was good, not great, and he could not stop thinking about what might go wrong." | canonical fact | e-8068 (public) causes: guitar good, not great; could not stop thinking about what might go wrong | the why-probe (found in C-27) |
| r4 | Ken Scott, 40, editor, open | canonical fact | p-12 (born 1957-12); the Courier's lead | seen; hover |
| r4 | Ken: "I couldn't say." (who brought the notice in, and the day) | CARD | rule 1, yield q1 = 1 | heard |
| r4 | Ken: the notice came written out and was set as it came; "long illness" and "as he asked" are not his | perceived information | GM-simulated: who placed D-04 is not in the record; its wording authored (records §1, D-04) | Ken, first-hand to the Courier's own work |
| r4 | Ken's join: Toby had his "long illness" from the notice for his piece | perceived information | yield q2 = 6, join in telling's shape; C-35 repeats D-04's "long illness"; the GM note's mechanism for C-35 (the writer joins true facts) | Ken (coworker of Toby) |
| r4 | Ken: nobody told the Courier; it was round the town by the Thursday (15 October) | perceived information | e-8899 public (the whole town); the day GM-simulated, as Hannah's "I heard on the Thursday" | Ken |
| r4 | Ken's join: Toby said that morning he hadn't seen Andy on the shore the night before | perceived information | yield q3 = 6; GM-simulated from Toby Tanner's shore walk (p-91, every evening from 1994-05) and Andy's death on the 14th (no walk, Hannah) | Ken, second-hand from Toby |
| r4 | Prediction outcome: Ken couldn't say who brought the notice; nobody told the Courier | scene state | r4-act prediction; Ken's answers | the screen |
| r4 | The clinic's fence: white paling along the yard, a gate on a spring; nothing written on it | texture | seeded scene detail; claims no history (the song's name is Andy's, e-7659) | seen |
| r4 | Eve Vaughan, 54, the clinic, open; comes to the front desk | canonical fact | p-74 (born 1944-03), the clinic since 1982-03 | seen; hover |
| r4 | Eve: last saw him at choir, Thursday 8 October; he sat down for most of it, but he sang | perceived information | GM-simulated co-presence: both sing with the Thursday choir (p-74 from 1992, p-17 from 1976, his unbroken to his death); sitting a visual interpretation of e-8878 | Eve, first-hand |
| r4 | Eve: "I couldn't say." (what he was ill with) | CARD | rule 1, yield q2 = 1 (her `knows` roll for the cancer was 4: she knows, and does not say) | heard |
| r4 | Eve: it was said a year or two back that he leaned on people, and that they'd stopped minding, or stopped being there; who, she couldn't tell | perceived information | e-8492 (local, March 1997), clinic staff by chance, `knows` roll 6; the visits (private) not shown | Eve, second-hand |
| r4 | Eve's join: "My Neil played with him all summer; he'd know more than I would" | perceived information | yield q3 = 6, join in telling's shape (to her partner); p-74 married Neil Lyons 1967; Neil in Pirate Radio from 1998-03, Andy from 1998-06 (e-8830) | Eve |
| r4 | Tuesday cards; Olive dealing to Mark Holmes, Edward Baker and Leo Lyons | canonical fact | Tuesday cards habits in November 1998 (p-37, p-25, p-19, p-63); seating as setup §9 start 3 | seen |
| r4 | P-13 still by the door; no printer's line; nothing says who put it up; "Letting Go on a Monday" with no name against it | perceived information | P-13 as written (records §3); the song is Sean Hale's (e-8891, local), which the poster does not say | inspected |
| r4 | Edward Baker, 83, retired, open | canonical fact | p-19 (born 1915-08) | hover |
| r4 | Edward: "I wrote that one." ("The Fence at the Clinic") | perceived information | WITNESS-ERROR: the song is Andy's (e-7659; C-26; A-20); rule 3, `name` d20 = 2, `who` d3 = 3 from e-7659's others (Oliver Brook, Peter Lane, Edward Baker) → Edward | heard (against C-26, C-35 and Neil) |
| r4 | Edward: "Andy brought it to us. The best of the words are mine." ("Christmas Fence") | perceived information | wrong: the song is Andy's alone (e-7868); Edward's own claim (e-7869, local), the setup's "bends his own"; `name` d20 = 18, no slip | heard (against Neil; with C-26 and Olive) |
| r4 | Edward: last saw him the night they played, in September; he looked done in; he played well enough | perceived information | e-8892 (public); Edward there by his evening routines (GM-simulated); done in a visual interpretation of e-8878; `name` d20 = 3, a slip with nobody else in the account to misname: no effect | Edward, first-hand |
| r4 | The berths empty in the morning; the boats out since first light | GM-simulated | the fleet out by day, in at evening (setup §9 start 2: boats in at a quarter to six) | seen |
| r4 | Oliver at the end of the bar where Agnes works, with his first pint; 42, skipper, the harbour fleet, open | canonical fact | p-55 two pints most evenings; seeing Agnes Tanner since 1997-03 (e-8506, local); born 1956-08; the fleet's lead since 1981 | seen; hover |
| r4 | Oliver: "I couldn't say." (when he last saw him) | CARD | rule 1, yield q1 = 1 | heard |
| r4 | Oliver: "Since the spring of '96. It was the cancer." | perceived information | e-8229 (local, April 1996); first-hand (Andy told him; setup §7 fact 1); yield q2 = 2, one fact; the bend (he likes Andy) has nothing to soften here; `name` d20 = 15 | Oliver, first-hand |
| r4 | Oliver: "I couldn't say." (who wrote the two songs) | CARD | rule 1, yield q3 = 1 | heard |
| r4 | Acts spent by Wednesday evening; 12 to 20 November go by | CARD | the clock (setup §1) | the screen |
| r4 | Round 5 case file: Andy's death; the six questions; the hearing; rounds 5 and 6 | GM-simulated | e-8899; setup §1, §2 | the case file |
| r4 | Standing 4; check unused, takes a turn; board (1) to (4) as filed | scene state | setup §3; r4 filings | the interface |
| r4 | Journal index; seen by you; records in hand | scene state | r1 to r4 screens | the interface |
| r4 | Everyone met or seen this case open | CARD | setup §3 willingness; no heard roll in case 2 | hover |
| r4 | Places: adds the clinic and the fleet's berths | GM-simulated | atlas places; setup §9 start 2 | the interface |
| r4 | Verbs, check, free acts | GM-simulated | card; setup §3 | the interface |
| r5 | Filed (5): sat down for most of choir on 8 October, but sang; Eve's sighting | scene state | r5-act free filing; r4 Eve q1 | the board |
| r5 | Filed (6): Edward Baker wrote "The Fence at the Clinic"; Edward's statement | scene state | r5-act; r4 Edward q1 (WITNESS-ERROR: the song is Andy's, e-7659) | the board |
| r5 | Filed (7): the notice reached the Courier written out, and Toby's "long illness" came from it; Ken's account | scene state | r5-act; r4 Ken q2 | the board |
| r5 | Why-probe, the June quarrels: "Ask someone who was there." | CARD | e-8831 to e-8834 are local, not public | the why-probe |
| r5 | Why-probe, Eddie Lane leaving the wake: "Ask someone who was there." | CARD | no event (his leaving was GM-simulated from his job, r3) | the why-probe |
| r5 | Why-probe, the funeral on 27 October: "Ask someone who was there." | CARD | no event for the funeral's day (authored, setup §1) | the why-probe |
| r5 | Why-probe, Olive leaving the bar: "Age 67." | canonical fact | e-8736 (public) cause: age 67; found in C-33 | the why-probe |
| r5 | A quiet Monday; Agnes Tanner behind the bar; 31, bar staff, the Anchor, open | canonical fact | p-109 (born 1967-06), the Anchor's staff; her Monday shift GM-simulated | seen; hover |
| r5 | Agnes: saw both quarrels from behind the bar, the one week in June; Alice Tanner had it out with him first, then Sarah Lane shouted at him in front of the whole room | perceived information | e-8831 to e-8834 (local, June 1998); staff in the room (setup §7 fact 6, "those in the Anchor that week"); order by event id; yield q1 = 3 | Agnes, first-hand |
| r5 | Agnes: "I couldn't say." (what each was about) | CARD | rule 1, yield q2 = 1 | heard |
| r5 | Agnes: both at the sawmill | canonical fact | p-73 (the sawmill since 1993), p-80 (since 1995); yield q3 = 4 | Agnes |
| r5 | Alice Tanner and Sarah Lane stay open after Agnes is asked | CARD | rule 4: Agnes is no partner, family or friend of either; `heard` d6 = 2 and 5, needing 6 | hover (later) |
| r5 | Prediction outcome: Agnes saw both and knows where they work; what either was about she couldn't say | scene state | r5-act prediction; Agnes's answers | the screen |
| r5 | The saws stop at twelve; Neil Lyons on a stack of planks with a tin and a flask; back when the saws start | texture | the dinner break and its hour GM-simulated; claims no history | seen |
| r5 | Neil Lyons, 50, the sawmill, open | canonical fact | p-64 (born 1948), the sawmill (walks out January 1999, e-8982) | hover |
| r5 | Neil: last saw him the night they played the Anchor, 18 September; thin, tired by the end, played every song | perceived information | e-8892 (public); Neil in Pirate Radio (e-8752, e-8830); thin a visual interpretation of e-8878; the last sighting GM-simulated; no bend (no listed tie); yield q1 = 2 | Neil, first-hand |
| r5 | Neil: he lived on his own; Neil only saw him at the band | perceived information | Andy's household alone since Stella's death (1978, C-35); "only at the band" GM-simulated (the visits, e-8881 to e-8883, are private and not his); yield q2 = 2 | Neil |
| r5 | Neil: heard on the Thursday, at the mill, at dinner | perceived information | e-8899 (public); the day GM-simulated, as Hannah's and Ken's; yield q3 = 4 | Neil |
| r5 | The shift comes off at six; John Holmes, the foreman, locks the shed behind the last of them | GM-simulated | p-21 the sawmill's lead; the hour authored | seen |
| r5 | Sarah Lane, 21, the sawmill, open; comes out alone, collar up; goes off up the road to the town | canonical fact | p-80 (born 1977-03), the sawmill since 1995; collar and road texture | seen; hover |
| r5 | Sarah: last saw him in June at the Anchor, the night she shouted at him; thin as anything; he was 84 | perceived information | e-8834 (local, her own); thin a visual interpretation of e-8534; 84 in June 1998 (p-17); the last sighting GM-simulated (e-8859, private, not shown); no bend; yield q1 = 5 | Sarah, first-hand |
| r5 | Sarah: Pirate Radio wanted someone and took him, not her | perceived information | e-8833 (local, her own); e-8830 (public); yield q2 = 6 | Sarah, first-hand |
| r5 | Sarah's join: she had played with Oliver in Driftwood, thought the place was hers, and said so, loud | perceived information | join in telling's shape (her own view); Sarah in Driftwood January to September 1996 (C-30) | Sarah |
| r5 | Sarah: "No. He took it, and kept his head down." | perceived information | e-8841, e-8842 (local; fact 7); she was in the event; yield q3 = 2 | Sarah, first-hand |
| r5 | No band on Friday 27 November; the corner set with tables; the poster still by the door; "Letting Go on a Monday" not played; nobody where Andy stood | GM-simulated | no show in the record on that Friday: e-8960 (the Night Shift, public, November) placed on Friday 20 November by d4 = 3 (`mystery-a-Y4-r5-t4-e8960-friday`); P-13 still up (scene state from r4) | seen |
| r5 | Those at the Anchor: staff, by the fire, along the bar, at the tables, by the window | canonical fact | Friday and two-pints routines at pl-bar active in November 1998 (fixture habits); seating GM-simulated; Larry Baker (two pints, unbroken in the record) left out after his stroke (e-8897), GM ruling | seen |
| r5 | Eddie Lane, in garage overalls, has his two pints and is gone before eight | canonical fact | p-79 two pints most evenings from 1998-09; head mechanic; the hour GM-simulated | seen |
| r5 | Edward Baker stays at the fire all evening | canonical fact | p-19 Friday (since 1996-09) and two-pints routines | seen |
| r5 | Alice Tanner and Sarah Lane are not in | canonical fact | p-73 and p-80 keep no routine at the Anchor | seen |
| r5 | Trevor Lane in every Friday this month and never on a Friday before; at the bar beside Oliver Brook | canonical fact | p-38 Friday Anchor from 1998-11 (e-8943, private: the routine shows, its reason never); his place at the bar GM-simulated | seen |
| r5 | Nobody who keeps a Friday here is missing | CARD | rule 7: no Friday routine at the Anchor ended in 1998 | seen |
| r5 | Toby Waller to Sylvia Waller: Andy gave up his swim at New Year '90; twenty-odd years off the harbour steps every morning, then never again; "I said at the time he'd be poorly." | perceived information | A-05 as memory in telling's shape: the absence right (e-6593, private: only the absence); the guess wrong (no illness until e-8229, April 1996); `A05` d6 = 5, heard | overheard |
| r5 | Nothing else heard about him | GM-simulated | chatter device: A-30 (d6 2) and A-12 (d6 1) not heard; A-18, A-20, A-28 already heard at the wake | seen |
| r5 | Friday hovers: ages and jobs (Gary Myers head teacher; Lily Lyons chief officer; Colin Berry out of work) | canonical fact | fixture births and jobs for November 1998; the leads of the school and the council office; Colin without a job since e-8905 (October 1998) | hover |
| r5 | Acts spent by Friday; 28 November to 4 December go by | CARD | the clock (setup §1) | the screen |
| r5 | Round 6 case file: the questions, the hearing on 11 December, three turns then the hearing | CARD | setup §1, §2 | the case file |
| r5 | Standing 4; check unused, one of the three turns; board (1) to (7) | scene state | setup §3; filings r4, r5 | the interface |
| r5 | Journal index; seen by you; records in hand | scene state | r1 to r5 screens | the interface |
| r5 | Places: adds the sawmill | GM-simulated | atlas places | the interface |
| r5 | Verbs, check, free acts | GM-simulated | card; setup §3 | the interface |
| r6 | Filed (8): Agnes saw both quarrels in June from behind the bar | scene state | r6-act; r5 Agnes q1 | the board |
| r6 | Filed (9): Sarah shouted at him because Pirate Radio took him, not her, and nothing settled it | scene state | r6-act; r5 Sarah q2, q3 | the board |
| r6 | Filed (10): he lived on his own; Neil only saw him at the band | scene state | r6-act; r5 Neil q2 | the board |
| r6 | Filed (11): he played every song on 18 September, thin and tired by the end | scene state | r6-act; r5 Neil q1 | the board |
| r6 | Filed (12): he gave up his harbour swim at New Year 1990; Toby Waller, overheard | scene state | r6-act; r5 A-05 | the board |
| r6 | Why-probe, the swim: "Ask someone who was there." | CARD | e-6593 is private, not a public event | the why-probe |
| r6 | Why-probe, Trevor's Fridays: "Ask someone who was there." | CARD | e-8943 is private | the why-probe |
| r6 | Trevor's house found by asking along Harbour Row; he is in the shed at the back, a clock in pieces on the bench | GM-simulated | p-38 house since 1969 (atlas; no street named); "spends every spare hour fixing something in the shed" since 1981; the clock texture | seen |
| r6 | Trevor Lane, 71, retired, open | canonical fact | p-38 (born 1927-04) | hover |
| r6 | Trevor: "I couldn't say." (how he knew Andy) | CARD | rule 1, yield q1 = 1 | heard |
| r6 | Trevor: at choir the Thursday before, the eighth; sat for most of it, sang the lot and sang it well | perceived information | GM-simulated co-presence at Thursday choir (p-38 choir 1992 to November 1998; p-17 to his death); bend: he likes Andy, softens; yield q2 = 2 | Trevor, first-hand |
| r6 | Trevor: not missed a Friday since the start of November | canonical fact | p-38 Friday Anchor from 1998-11; yield q3 = 6 | Trevor |
| r6 | Trevor's join: years he'd not come in of a Friday; "Andy would have laughed at me" | perceived information | A-30 adapted as memory (right, e-8943); the routine's reason not said (private) | Trevor |
| r6 | Prediction outcome: open; couldn't say how he knew Andy; no music named; who found Andy not asked | scene state | r6-act prediction; Trevor's answers | the screen |
| r6 | Cards night; Toby Waller with Mona Sayer, Terry Sutton and Grace Waller | canonical fact | Tuesday cards habits (p-67, p-27, p-48, p-68); seating setup §9 start 3 | seen |
| r6 | Toby Waller, 69, retired, open | canonical fact | p-67 (born 1929-02) | hover |
| r6 | Toby: stopped coming down at New Year '90; he never said why, not to Toby | perceived information | e-6593 (private: the absence only, never its reason); Toby a 1989 swimmer (setup §5), first-hand to the absence; yield q1 = 4 | Toby, first-hand |
| r6 | Toby: same as ever that winter, right up to Christmas; in off the steps at seven, a towel round him, up home | perceived information | GM-simulated visual interpretation: no illness before e-8229 (1996); the swimmers at seven (setup §5); yield q2 = 5 | Toby, first-hand |
| r6 | Toby: last saw him the Friday they played, in September; thin; played well | perceived information | e-8892 (public); Toby's Friday routine; thin a visual interpretation of e-8878; yield q3 = 2 | Toby, first-hand |
| r6 | The check on claims 1, 6 and 12: not all three stand | CARD | rule 9: 1 stands (e-8229; C-30 right on this point), 6 does not (e-7659: Andy's song), 12 stands (e-6593, January 1990) | the check |
| r6 | The three dropped from the board, as the act said | scene state | r6-act turn 3 | the board |
| r6 | The hearing room: a long table, the coroner, a clerk, a jug of water | texture | authored (setup §1), as case 1 | seen |
| r6 | The account as given, six answers from the board | scene state | GM-composed from the board as r6-act turn 4 said, claims 1, 6, 12 dropped; mapping in gm.md | the screen |
| r6 | Summoned Hannah: the Tuesday he went down, the Wednesday he didn't | perceived information | her r3 statements; rule 8 | heard |
| r6 | Summoned Eve: at choir the eighth, sat for most of it | perceived information | her r4 statement; rule 8 | heard |
| r6 | Summoned Neil: the eighteenth, every song; lived on his own; saw him at the band | perceived information | his r5 statements; rule 8 | heard |
| r6 | Summoned Ken and Toby Tanner: it came written out; "long illness" from the notice | perceived information | r4 Ken q2 (GM-simulated) and its join; rule 8 | heard |
| r6 | Summoned Edward: "That's what the paper printed. The song is Andy's. I let people think the best of it was mine." | canonical fact | rule 8: a summoned person is honest about local events: e-7868, e-7869 (local); C-26 as printed | heard |
| r6 | Summoned Agnes: both, from behind the bar | perceived information | e-8831 to e-8834; rule 8 | heard |
| r6 | Summoned Sarah: they took him, not her; nothing settled it | perceived information | e-8833, e-8842; rule 8 | heard |
| r6 | The coroner: "Recorded. The account is accepted." Ruling accepted; no claim struck; standing 5 of 6 | CARD | the ruling: nobody named answerable, nothing struck; +1 (setup Gaps) | the screen |
| r6 | The close: 25 of 100; right on the quarrels and on nothing settling them, partly on the credit | scene state | scores.md, case 2 | the close |
| r6 | Close 1: cancer, April 1996, back June 1997 and September 1998; the record of death gives age 85 and his health worn down | canonical fact | e-8229, e-8534, e-8878 (local); e-8899 (public) causes | the close |
| r6 | Close 2: ill from spring 1996; C-30 right | canonical fact | e-8229; C-30 | the close |
| r6 | Close 3: nobody caused his death | canonical fact | e-8899 causes | the close |
| r6 | Close 4: the hat, Friday 11 July 1997, when the cancer came back; Oliver and Eddie most, Edward his wallet, Grace a note, Colin the smallest coin | canonical fact | e-8563 to e-8567 (local), cause e-8534; the Friday authored (setup §7) | the close |
| r6 | Close 5: Karen Holmes and he made peace, July 1998, 27 years after the café | canonical fact | e-8858 (local); who went to whom (e-8857, private) not said | the close |
| r6 | Close 6 and 7: Alice and Sarah each wanted the place, went at him at the Anchor; he took it, kept his head down, didn't think it was about him; nothing settled it | canonical fact | e-8831 to e-8834; e-8841, e-8842 (cause: did not think it was about him) | the close |
| r6 | Close 8: "Christmas Fence" is his; Edward let people think its best lines were his; Andy found out; "The Fence at the Clinic" is Andy's | canonical fact | e-7868 to e-7870; e-7659 (local) | the close |
| r6 | Close 9: Driftwood split over its sound, Oliver, Edward and Sarah each needing to matter, not his illness | canonical fact | e-8374 (public) causes; against C-30 | the close |
| r6 | Close 10: the swim stopped January 1990, six years before any illness; nobody in the town could have told you why | canonical fact | e-6593 (private: its reason never shown) | the close |
| r6 | The obituary's three errors: the swim, the credit, the split; the check held one wrong claim and two right | canonical fact | setup §7 and Gaps; rule 9 | the close |
| r6 | Mary Tanner: a sudden heart attack; strokes December 1989 and June 1991 survived; no illness before; nobody answerable; notice and Courier stand; the hat for Mark, 7 March 1997: Greta most, Una the smallest coin, Leo no wallet | canonical fact | e-8459 (public); e-6556, e-6970 (local); D-03, C-32; e-8494 to e-8496 (local) | the close |
| r6 | Twenty turns as played: Oliver on the songs, Toby Tanner on the 1989 swims; nobody can say who found Andy | GM-simulated | the player's strategy (r6-act needs); no finder in the record | the tenth hour |
| r6 | The town hears the account was accepted; nobody turns from the player | CARD | an accepted account carries no "town knows" pressure (ruling); it named nobody answerable | the tenth hour |
| r6 | Una Waller "goes into hospital with pneumonia", and the hat goes round for her: Sam Brook and Lynn Newman most | canonical fact | e-8973, e-8974 (local, December 1998). GM-ERROR in timing: she went in in October (e-8898), before the hearing; logged in gm.md | the tenth hour |
| r6 | Neil Lyons found out at the sawmill (a covered-up mistake); in January he walks out to start again | canonical fact | e-8969 (local, December 1998), cause: lied to cover a mistake at work; e-8982 (local, January 1999) | the tenth hour |
| r6 | Nobody dies before the end of January 1999; no third case | canonical fact | the fixture: no death after e-8899 to its end (2036-01) | the tenth hour |
| r6 | Exit questions | CARD | gm-brief, exit questions; the card's names for understanding (setup §10) | the screen |
