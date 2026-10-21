# Stories in the world

Ideas, not decisions (21 October 2026, on Opus 5.5). Øystein asked us to "combine the physical world with the Understory parts, to see if there are potentials, details, mysteries etc." This page reads real simulated lives and asks what they would leave in the town Overstory draws. A story here is never written. It arises where a life leaves traces, and where traces, accounts and records disagree or fall silent.

The main source is the first real engine run, `fixtures/engine/understory-world-9989.json`: 119 people, 2,635 events, nine workplaces, 25 ventures, four bands. Beside it are the blind-reading packs of rounds 29 to 37 in Understory's `reports/` (216 versions of lives) and the engine's setting pack. Engine lines are quoted as written.

**Dates.** The engine's past starts in 1996 and its present runs from 2026 to 2036; a setting's own start year is engine issue #23. This page shifts every engine year back by 37. The engine's 1996 becomes our people's start year (1959), and its 2026 becomes the show year (1989). The three visits in section 3 are 1989, 1995 and 1999, all inside the run. Quoted lines keep the engine's years; the text gives the shifted ones.

## The bottom line

- **Routine is where lives show first.** In world 9989 about nine habits break, return or begin each year among the 76 people in town. Each is a lit window that stops, a swimmer missing from the harbour steps, a shed lit on new evenings, and most carry their cause in the record. It is the fastest true trace the town has.
- **Care is slow and ambiguous.** Debt, illness, grief and absence all lower care, and care shows over years in paint and gardens. A reader cannot tell which cause it was. Here the trace tells less than the page, and that is right.
- **Not every line about a thing is an act on it.** "Ben Reed had promised Andy Shaw to help with the roof, and did it" is a real act, one of 17 roof jobs kept in ten years, though it names no house. "Eric Lane painted over the old boathouse door" is a character quirk from a shared pool. Three people paint over the same door in world 9989, and drawing it would invent a story nobody lived.
- **Most weighty acts are private.** Of 2,635 events, 1,271 are private, 1,203 local and 161 public. All 16 thefts from work are private, and 5 were found out. Starting to drink is private; stopping is local. The town knows when someone stops drinking, not when they start.
- **Traces mislead in useful ways.** A garden taken up four years after a wife left reads as getting over her; the engine's cause is a public row at work. A boat bought a year after its owner was caught at the till reads as stolen money; the engine says ten years of saving. Both are fair mysteries if the counter-evidence is somewhere the player can reach.
- **The engine has no violent death and no crime beyond small dishonesty at work.** Deaths come from age and illness. Work accidents hurt but never kill. A murder mystery needs new engine facts. A death can still frame a mystery today, as in *Bad News*: who was this person, whom did they lean on, who wrote their songs.
- **Buildings remember what lives forget.** The old bank took six attempts and nineteen years (1960 to 1979) to become a café, and one woman opposed every attempt. The fabric shows only the 1979 front, and the export keeps the ventures before 1989 but not their reasons.
- **The biggest gaps are place, witnesses, homes and records.** Events have no place (request 28). The export has visibility but no witness list (request 1). Households have no address (request 15). The Courier never prints a line (request 9).

## 1. What the engine gives a story

| Kind of event | World 9989, shifted to 1989 to 1999 | Visibility | In the engine's words |
| --- | --- | --- | --- |
| Death | 4 | public | "died after a long illness", "in her sleep", "of a sudden heart attack"; "of liver failure" for a drinker under 72 (`body.ts`) |
| Illness | 33 | local | strokes, heart attacks, pneumonia, cancer and its return, a bad back |
| Work accident | none here; common in the packs | public | "got caught in the saw", "was pinned under a car", "went over the side"; two to six months off, never fatal (`danger.ts`) |
| Danger for money | 2 went out, 3 hung back | local | "went out into the storm"; in the packs, "badly hurt when the boat was caught by a wave" |
| Taking at work | 16 thefts, 5 found out | private, then local | "took a little from" the till, the catch, the timber account, the trip money, the medicine cupboard, the expense claims |
| Blame and cover-up | 8 and 1 | private | "let Olive Shaw take the blame for a mistake at work" |
| Purchases | 10 | public | a house, a boat, a car, the big trip abroad |
| Moves | 13 arrived, 7 left, 2 came back | public | "Maisie Myers left the town for the city. Harry Myers stayed, and that was the end of the marriage." |
| Drinking | 10 started, 9 stopped | private, then local | "started drinking more than was good for her" |
| Habits | 30 broke, 31 back, 13 new, 14 taken up after a blow | mostly local | fifteen kinds, from the Anchor on Fridays to swimming in the harbour every morning |
| Ventures | 5 festivals on the quay; a café opened in 1979 | public | "has started telling people he means to open a café in the old bank" |
| Bands | 4 | public and local | "Edward Baker let people think the best of Andy Shaw's song was Edward Baker's." |

Each event carries its month, who, its causes with weights, its visibility and a notability from 200 to 3,000 per mille. It lacks a place, a witness list in the export, and any record someone wrote.

## 2. Trace patterns

*System* is the Overstory system that draws the trace. *Appears* and *fades* are unverified starting values for the life runner. *Kind* uses the five kinds of thing on screen (`CLAUDE.md`). F is a canonical fact, I a visual interpretation of facts, P perceived information (an account or a record), S local scene state. A trace marked F needs the engine fact named; until then it is `authored` in fixtures.

### A death, and grief

| Trace | System | Appears | Fades | Kind |
| --- | --- | --- | --- | --- |
| The dead person's routines stop: no swimmer at seven, the late window dark, an empty place at cards | lit windows and the day; footfall | the next day | never; it is an absence | F |
| The bereaved break habits: "no longer rings his mother every Sunday evening", "is no longer out in the garden every morning" | the day | weeks | back after months or years ("things had settled") | F |
| Visitors: "came round to see Sam every week" | footfall to one door | the week | months | F, private |
| The hat that goes round at the Anchor | scene | the week | a night | S from a local fact |
| A headstone, a death notice, and who came to the funeral | records; the scene | days to months | the paper yellows; lichen on the stone over decades | P; F with request 31 |
| The house of someone who lived alone: garden first, then paint | care and upkeep | garden in one to three summers, paint in five to ten years | until a new keeper | I |

### Illness and accidents

| Trace | System | Appears | Fades | Kind |
| --- | --- | --- | --- | --- |
| Absence from work and habits for the engine's months off | the day | at once | when the months end | F |
| "Kept turning up at Andy Shaw's door with something or other" | footfall; the day | the week | as long as the illness | F, private |
| A stick, a stiff hand, a slower walk after a stroke | the person | at once | for life | F only with request 34 |
| A ramp, a rail, a bed moved downstairs | works; the room | months | for good | F with request 14; never by rule |
| Nothing at the sawmill after "caught in the saw" | none | | | a guard fitted would be a work (request 14) |

### Money: saving, buying, debt, theft

| Trace | System | Appears | Fades | Kind |
| --- | --- | --- | --- | --- |
| A boat at a mooring, and "now out on the boat every weekend" | added things; the day | the month | while owned | F with request 17 |
| A house bought: a new name by the door, care up, a garden dug | records; care | months | while owned | F with 15 and 17; care I |
| "Has stopped coming out; saving, she says" | the day; accounts | weeks | when the thing is bought | F (absence), P (the reason) |
| Debt: paint and garden let go, a habit at the Anchor dropped, "keeps to himself" | care; the day | habits at once, paint over years | when "the pressure had eased" | I and F |
| "Had to sell the house": a for-sale board, then strangers' curtains | records; the window's dressing | months | | F with 15 and 24 |
| Found out: a job left ("walked out of the clinic to start again somewhere else") | the day; footfall | at once | | F; the reason is P |

The theft itself leaves nothing: it is private, and a trace would claim a witness.

### Moves and partners

| Trace | System | Appears | Fades | Kind |
| --- | --- | --- | --- | --- |
| One household fewer: windows dark, the car gone | lit windows; added and removed | the month | until new tenants | F with 15 |
| Came home for the funeral and stayed: the parent's house lit again | lit windows | the month | | F with 15 |
| A couple drifting ("polite with each other, and that was all"): arriving apart, separate habits | the day | years | | F (habits), I (staging) |
| A row "at the co-op, with people listening" | accounts | the day | as long as it is told | P |
| Divorce: one window lit where there were two | lit windows; the household | the month | | F with 15 |

### Work, habits and the day

| Trace | System | Appears | Fades | Kind |
| --- | --- | --- | --- | --- |
| "Is first in at work every morning": one window lit early | lit windows | at once | when "it just lapsed" | F; the hour derived |
| A habit broken or begun: the shed lit, the harbour steps, the shore path at dusk, choir night | the day; footfall | at once | at once | F |
| A route walked for years: the shore path, the coast road | footfall | polish in two to five years | moss back about five years after it stops | I from F (request 16) |
| Reading late or practising "after the house has gone quiet": a window lit past midnight | lit windows; sound | at once | at once | F; the hour derived |

### Ventures, festivals and bands

| Trace | System | Appears | Fades | Kind |
| --- | --- | --- | --- | --- |
| A café opened: front fitted, sign up, lit at its hours, feet at the step | shopfronts; signs; footfall | months | while open; a ghost after | F (opening), I (fit) |
| A café refused by the council | none on the fabric | | | a council minute would be a record (requests 9, 23) |
| A festival on the quay: posters weeks before, the quay dressed, trodden grass, litter after | records; scene; footfall | weeks | posters in months, grass in weeks | P, S |
| "The best night the town had had in years" against "a washout" | accounts | the night after | years | P |
| Gig posters layered on the Anchor's wall | records | the week | pasted over | P; credits can be wrong |

### Feuds and small acts

| Trace | System | Appears | Fades | Kind |
| --- | --- | --- | --- | --- |
| "Goes out of her way to avoid Olive Shaw": the back way round, the far side of the room | footfall; the day | at once | when they bury the hatchet | F with 16 and 28 |
| "Fixed the front door for Libby without being asked", the letterbox, the garden fence | upkeep; added things | the month | ages from its year | F with request 20 |
| "Had promised Andy Shaw to help with the roof, and did it" | upkeep: a patch on the roof, or a leak left alone | the month | weathers in over decades | F with 15 and 20 |
| Quirks: "climbed out onto the roof in the rain to fix the gutter", "painted over the old boathouse door" | none | | | texture of character; drawing them invents history |

### Births and children

| Trace | System | Appears | Fades | Kind |
| --- | --- | --- | --- | --- |
| A pram at the door, washing on the line, a light at three in the morning | added things; lit windows; scene | weeks | a year or two | F, S |
| A swing, toys in the yard, a lean-to built; later a room dark when the child "left for university in the city" | added things; works; lit windows | years | when the children grow | F; the lean-to needs request 14 |

Two rules follow. The fastest true traces are habits, and they need habits as timetables (request 1) to be drawn at the right hour. Every slow trace (care, wear, growth) is shared by many causes, so it may never be read as one. The history budget and the why-probe must stop a player pinning a shabby front on grief when the record says debt.

## 3. Real lives, read twice

Each life is read first as the engine's page, then as a visitor would see the town in 1989, 1995 and 1999. Five readings come from world 9989. Three come from the reading packs: other worlds' versions of the same town.

### Andy Shaw (world 9989), 1913 to 1998

**The page.** He lives alone and is 76 in 1989. In January 1990 he "no longer swims in the harbour every morning, whatever the weather. [it just lapsed]". At 77 he joins Driftwood and writes its best songs; "The Fence at the Clinic" (1994) "got them called back twice" in 1995. In December 1994 "Edward Baker let people think the best of Andy Shaw's song was Edward Baker's", and Andy found out. From late 1993 he is in debt and asks Ben Reed and Oliver Brook for money, privately. In April 1996 he is diagnosed with cancer, and in November Ben Reed helps with his roof. When the hat goes round for him in 1997, "Colin Berry put in the smallest coin he could find". In June 1998 he wins a place in Pirate Radio over Alice Tanner and Sarah Lane, and Sarah shouts at him in front of everyone at the Anchor. In July Karen Holmes buries the hatchet with him, "27 years after the café". He dies in October 1998.

**1989.** An old man on the harbour steps at seven every morning, in all weathers. A window lit late every night ("reads late into every night", since 1986). Choir on Thursdays, the shore path every evening.

**1995.** One swimmer fewer at seven. A player who knew the town in 1989 may notice; one who came later cannot. Driftwood posters on the Anchor's wall. By our care rule his house shows a pensioner's upkeep and two years of debt: paint tired on the weather side. Nothing says why.

**1999.** The late window is dark. If the roof job of 1996 lands on his house as a fact (requests 15 and 20), a newer patch stands out on the slope. Pirate Radio's posters go on without him. A headstone reads 1913 to 1998.

**Where the traces tell more.** The page says the swimming "just lapsed". The street shows exactly when, as one gap among the morning swimmers. The roof patch would be the only lasting mark of Ben Reed's kindness, and would outlive them both.

**Where they tell less.** Debt is private, so the tired paint reads as age or illness, never as money. The row over "Christmas Fence" leaves nothing on the street.

**Where they mislead.** A player who learns of the cancer (1996) will date it back to the empty steps (1990) and decide he stopped swimming because he was ill. The record says otherwise. A cut from the empty steps to the headstone would invite that cause, so a years strip must not join them (`docs/research/time-on-screen.md`, rule 7).

### The old bank (world 9989), 1960 to 1999

A building read through six lives. Every venture in the run before 1989 is a café in the old bank or a festival on the quay.

**The page.**

| Shifted year | Venture | Opposed by | The council |
| --- | --- | --- | --- |
| 1960 | Olive Shaw's café | Ellie Holmes, Larry Baker, Karen Holmes, Molly Scott | no |
| 1965 | Molly Scott's café | Karen Holmes, Edward Baker, Larry Baker | no |
| 1968 | Molly Scott's café, again | Karen Holmes, Edward Baker | no |
| 1971 | Andy Shaw's café | Karen Holmes, Edward Baker, Larry Baker | no |
| 1975 | Larry Baker's café | Edward Baker, Karen Holmes, Sean Hale | no |
| 1978 | Larry Baker's café, again | Karen Holmes, Sean Hale (also a helper) | yes; opened May 1979 |

Karen Holmes opposed all six. Larry Baker opposed three cafés and then opened his own. In 1989 Olive Shaw is still "civil to Karen Holmes for weeks, and nothing more. Nobody was surprised any more: it had been happening since 1999" (1962). Olive tries to make peace in 1994 and is rebuffed, "not after the café". Larry and Karen bury the hatchet in 1995; Andy and Karen in 1998. "The council's plan to sell the old bank building" comes up in 1991, 1993 and 1998, once as a joke on the quay.

**1989.** A bank on the harbour with a ten-year-old café front in its ground floor. The 1979 front and sign sit in an older face, under the bank's own lettering if its era put it there. Lit at the café's hours, its step polished.

**1995.** The same, a little older. Two women who never stand at its counter together, if the player watches long enough and the engine gives places to its avoiding (request 28).

**1999.** The front is twenty years old. If the council's plan were a document (request 23), a notice could hang in the window.

**Where the traces tell more.** The front dates the café to its decade at a glance, and the lettering says the building was something else first.

**Where they tell less.** Nineteen years of hope, refusal and grudge leave nothing on the fabric. That is correct: "hope shows nowhere until it is a lease" (`docs/living-fabric.md`). Only records could hold it: a council minute, a letter to the Courier, a photograph of the empty bank.

**What is lost.** The ventures keep the ids of their events before 1989 (`v-0` holds `e-203` and others), but the export starts in 1989. Why Karen opposed every café, and why Larry changed sides, is not in the file. In pack 33 another world's old bank was refused in 1992 and opened in 1996 by the Anchor's new manager. A building's history must come from the run, never from the pack.

### Harry and Maisie Myers (world 9989)

**The page.** Harry teaches at the school; he and Maisie came to the town in 1984. In February 1989 "Harry Myers took a little from the trip money", and again in 1991. Nobody finds out. In May 1989 Maisie tells him "how bad things had got", and he tells people. "Every row between Maisie Myers and Harry Myers went the same way." Their son leaves for university in May 1990; Harry joins the choir that June, and Maisie buys the big trip abroad in August. From December 1992 Harry is at the Anchor every Friday. In May 1993 "Maisie Myers left the town for the city. Harry Myers stayed, and that was the end of the marriage." In January 1997 Harry drags up, in front of everyone at the school, that Gary Myers was found out taking from the trip money. Gary drags something back in May. In June: "Harry Myers is now out in the garden every morning from spring to autumn. [... it had shaken him]".

**1989.** A house of two with a light late into the night (Maisie reads late). Maisie at the Anchor most evenings for two pints, and at cards on Tuesdays.

**1995.** Maisie's late light is gone; one person lives there. Harry walks to the Anchor on Fridays and to choir on Thursdays. Nobody tends the garden.

**1999.** The garden dug and kept, two summers in, and a man out in it every morning from spring.

**Where the traces mislead.** A visitor who learns that Maisie left in 1993 reads the garden of 1997 as a man getting over his wife. The engine's cause is the row at the school. The four-year gap is the only clue, and dates are what readers handle worst.

**What is never knowable.** Harry took from the same trip money he later shamed Gary for. It was private and never found out, so no witness, account or trace exists. A game must never hint at it, because the hint would be a false claim. It belongs to the record, and to sandbox play after the end.

### The old boathouse door (world 9989), painted three times

**The page.** April 1989: "People have noticed: Eric Lane painted over the old boathouse door without a second look. [has no time for art]". In 1993 Terry Sutton does the same, and in 1996 Tara Myers. The line also appears in five lives of the reading packs. It is one of the engine's quirk patterns (`persona.ts`), chosen to show a trait and filled with a thing from the setting's words.

**If it were drawn.** 1989: one fresh, flat coat on a boathouse door among weathered ones. 1995: a second coat, two years old. 1999: three coats in seven years, each over something nobody is recorded putting there.

**Where it misleads.** Players read more than is there (`history-in-things.md`: the pocket watch, the sandstorm). A door painted over three times says someone keeps painting on it. Nobody does. Drawing the line would make an anomaly with no event.

**What it teaches.** Quirk lines ("Typical:", "People have noticed:") are evidence about a person, not acts on a thing. Arthur's gutter in pack 31 and Sally Baker's in world 9989 come from the same pool. They reach the fabric only when the engine names the thing and the act (request 20). The roof jobs are the opposite case. Of 22 promised in ten years, 17 were kept: real acts between two people, waiting only for a house to land on (request 15).

Eric Lane's own chain is invisible. He took a little from the catch in 1993 and 1994, and in December 1993 "finally told Oliver Brook what had been kept back". In August 1996 he and Oliver went out into the storm while Bert Kemp, Oscar Ash and Maisie Baker hung back. The street shows only his shed, lit most evenings since 1976.

### Peter Scott and Olive Shaw (world 9989)

In June 1989 Peter "let Olive Shaw take the blame for a mistake at work" at the Anchor, and was found out that month. In 1993 he bought a boat. In December 1995 "Olive Shaw and Peter Scott are friends now". The 1995 town shows a new boat at a mooring and two people from the Anchor walking together. Only someone who heard about 1989 knows the friendship began with a wrong. Traces cannot carry forgiveness; accounts can.

### Grace Shaw's boat (pack 33, version B)

**The page.** Grace works at the Anchor and starts saving for a boat in 1989. In 1992, while she and Ben compete for manager, she "took a little from the till" twice and was found out twice. Passed over in 1993, she "resigned on the spot". In 1994 "Grace Shaw bought a boat of her own. [had been saving since 2021]". From 1997 "the neighbours can hear" her practise every night. In 1998 she is let go from the council office and "started drinking more than was good for her".

**1989:** a woman behind the bar at the Anchor. **1995:** her new boat at a mooring, a year after the town learned about the till. **1999:** her window lit and a guitar heard late at night; since 1998, out of work.

**Where the traces mislead.** Till in 1992, boat in 1994: any reader joins them. The record joins the boat to saving it dates to 1984. This is the cleanest fair mystery in the packs. The counter-evidence is ordinary (her friends know how long she had wanted the boat), and an observer can find it.

### Eve and the saw (pack 29, version A)

In 1990 "Eve got caught in the saw at the sawmill." Jonah, Sam and Alex Shaw "went in after Eve without a second's thought"; Edward Hale and Olive Tanner froze. The year before, Eve had dragged up in front of everyone that Jonah was found out taking from the timber account. In 1994 Jonah becomes foreman over her, and "Eve took it, and kept her head down. [... thinks the world of Jonah]". The street shows nothing: Eve is off for months, and the sawmill gets no new guard. The story lives in five witnesses' memories of one minute.

### Arthur's house (pack 31, version A)

In 1989 "Arthur has not been himself for months; he keeps to himself and people have started to notice." In 1992 he tells his wife "it was nothing". In 1993 "People have noticed: Arthur climbed out onto the roof in the rain to fix the gutter. [danger has never stopped him]". In 1997 the withdrawal returns, now "[badly in debt]", and "Arthur had to sell the house. [the money had run out]". They divorce in 1998. Beside the sale, the man on his roof in the rain reads as someone too short of money to pay for the job. The engine's cause is a trait, and the line is a quirk from the shared pool: another misleading trace, and another reason quirks stay off the fabric.

### What the readings show

- Habits carry true, dated information that the page states flatly and the street shows as felt absence or presence.
- Care carries the most information and the least certainty. It is right that debt and illness look the same from the street.
- The misleading cases share a shape: two true traces a few years apart, joined by a link the reader supplies and the record lacks.
- The engine already writes good clues: "the neighbours can hear", "saving, she says", "with people listening". Each names a witness or a source.
- The old bank, the Anchor and the harbour steps are where the run's chains cross. That is where the history budget should be spent.

## 4. Mysteries that arise by themselves

None of these is written. Each comes from the record as it stands.

| Mystery | How a player notices | Evidence that exists | Solvable? | Never knowable | Fair? |
| --- | --- | --- | --- | --- | --- |
| Why did Andy Shaw stop swimming? (1990) | The harbour steps at seven, watched over weeks | The habit's end, "it just lapsed"; the cancer six years later | Yes, if the player can date both | Nothing more is there | Yes, if dates show at their precision; the trap is the false link |
| Who wrote "Christmas Fence"? | A poster or a set at the Anchor; friends who say otherwise | Edward Baker's claim and Andy finding out (both local); later Oliver Brook plays another of Andy's songs "as if it were Oliver Brook's own" | Through accounts, if who-told-whom is kept (request 1) | No manuscript; songs are not things | Yes, with accounts traced to tellers |
| Why did the old bank take nineteen years? | A 1979 café front in an older bank; two women who keep apart | The ventures and their opponents; "not after the café" | Partly: who opposed is in the run | Why (events before 1989 are not exported) | Only if the starting record keeps its reasons |
| Did Grace Shaw buy her boat with the till? | A new boat a year after the town learned about the till | Ten years of wanting; saving since 1984 | Yes | Nothing | Yes: the cleanest case |
| Why did Harry take up the garden? | A neglected garden kept from 1997 | The habit and its cause, the row at the school | Yes, through accounts of the row | Harry's own theft | Only if the game never hints at the theft |
| Who keeps painting on the boathouse door? | Three coats in seven years, if drawn | Three quirk lines | No answer: nobody paints on it | Everything | No: a false mystery, made by drawing a quirk |
| Who froze at the saw? | The accident is public, and the town tells who went in | Three went in, two froze | Yes, by accounts, if witnesses have places (28) | What Eve saw | Yes |
| Where did Arthur's money go? | A house sold | "Badly in debt", private; "it was nothing" | No: the cause is not in the record | The cause | Only as an honest "?" |
| Why do Olive Shaw and Karen Holmes keep apart? | Two women who never share a room for thirty years | The 1960 café; "still sore about the café" | Yes, from old accounts | What was said in 1960 | Yes |

The research supports four ways in: an absence in a known routine (`behaviour-on-screen.md`), a part from the wrong decade, a fresh coat among old ones, and a record that disagrees with an account. Change blindness means the first works only for players who watched the routine. The aligned toggle and the held-up photograph make the rest visible (`time-on-screen.md`).

Fairness has the same shape in every case: the counter-evidence is somewhere the player's role can reach, and the game never confirms a reading of a person. Unfairness has one shape too: a hint at a private act no witness saw, or a link made by a cut.

## 5. Details from the lives

From the run and the packs, never invented. Counts are of the 76 people in town in world 9989.

- **The swimmers.** Eight swim in the harbour every morning, whatever the weather. The harbour steps at seven have regulars, and a gap when one stops.
- **The hat.** When someone is ill, a hat goes round at the Anchor. Someone empties a wallet, someone slips a folded note in "when nobody was looking", someone puts in "the smallest coin he could find", someone "had left the wallet at home". The bar on those nights is a scene.
- **The week's clock.** Choir on Thursday (22), cards at the Anchor on Tuesday (23), the Anchor every Friday without fail (29). A lit hall and a busy door on fixed nights.
- **Sheds and late windows.** 18 spend "every spare hour fixing something in the shed"; 13 read late into every night; 12 practise "after the house has gone quiet". A dark street at midnight has a few lit windows, and each belongs to someone.
- **Paths.** 19 walk the shore every evening and 14 run the coast road every other day, so both wear along their lines.
- **Rows in public.** "At the co-op, with people listening", "at the end of the breakwater", "at the church hill". Private rows the town overhears become accounts.
- **Things on sills.** "Brought something back from the county fair, for no reason." "Spent a week's wages on a print for the wall." "Labels the jars in the porch, including the one that says labels." Each is an object with an owner and a year, for the window's dressing.
- **Small habits.** "Has eaten mustard for lunch every working day since 2024." At the school, "Una Waller has a score out of ten for everyone's mustard." "Tara Myers has moved seats at the end of the breakwater every time someone asked."
- **Stories told.** "The time the old compass went over the side", told at the co-op.
- **Roofs and gardens.** In ten years there are 22 promises to help with a roof and 21 with a garden, and 30 are kept. A neighbour up a ladder on someone else's house is the commonest act on a thing in the run.
- **Songs about the town.** "The Fence at the Clinic", "Your Father's Boat", "No Ferry Tonight". The titles name the town's own things and could head its posters.

## 6. Potentials for play

### Four games

| Game | The loop these patterns support | What carries it |
| --- | --- | --- |
| The murder mystery (today, a death mystery) | A death opens a case. The player reads the dead person's routines, money and ties from the street and from accounts: whom they leaned on, who wrote what, who stayed away | absences, accounts with tellers, the hat, the headstone, the house left behind |
| The journalist | The Courier has an editor, reporters, deadlines and a visit from head office. The player writes what the town reads; a report is a record that can be wrong | records (request 9); accounts against traces; the paper's own "plan to go online and stop the Saturday print" (pack 33) |
| The observer | Learn a street's routines, notice what changes, ask why, keep a journal (`interface-and-inspection.md`) | habits as timetables; the change query; the aligned toggle |
| The family saga | Follow a household across decades: who leaves for the city, who comes home for the funeral and stays, who sells the house | homes (15); facts as intervals (33); things that recur with their people |

The observer is cheapest on today's engine, because habits and their breaks already carry causes. The journalist fits the engine's own institutions best (the Courier, the council's plans, the harbour day), and records would switch it on. A family saga needs homes first.

### A death that is a mystery

The engine's worst acts are taking a little at work, covering up a mistake, letting someone else take the blame and running a rival down. A murder mystery would need, within Rule 8:

1. A death with a human cause. An act family for harm, rare and weighed like the others, would take its intent from states the engine already has: a rivalry, a debt, a secret about to come out.
2. A place and a time (request 28), so who could have been there is a question the record answers.
3. Who saw and who was told (request 1), so accounts can be independent.
4. Lies that hold. The engine has `liecover` and `allfine`; a suspect's account must be able to be false and stay consistent.
5. Things with owners (request 17), so an object can place a person.
6. An accident that can kill. The setting already has "went over the side" and the storm. A fatal fall at the harbour, sometimes with someone nearby, asks the oldest small-town question: did he fall?

Overstory must not grow its own crime simulation (`docs/research/pre-mortem.md`). This is a request to the engine, and its scope is Øystein's call. Until then *Bad News*'s frame works on today's run. Andy Shaw's death leaves money two friends gave him, a disputed song, a feud ended three months before, a band that lost him, and a roof another man helped with.

### Keeping it fresh

Shadows of Doubt goes stale because its cases come from templates and its documents repeat (`docs/ideas/first-game-options.md`). The run suggests five guards.

- **Cases come from chains, never from types.** A case is a sifted chain from the record (request 7): the café's six attempts, the till and the boat.
- **Count kinds, fold repeats.** The engine's readers reward lives with more kinds of happening, and its pages repeat the festival, the hat and "count me in". A sifter should prefer chains of many kinds and fold the repeats.
- **Let some cases end in "?".** Arthur's debt and Harry's theft cannot be solved. Saying so is honest and keeps solving from becoming routine.
- **The town ages under the cases.** The same street holds different chains in 1989 and 1999, so a town that moves forward does not run out.
- **The player's own traces.** Their acts enter the record and the fabric like anyone's (`NOW.md`, Decided), so a later case can involve them.

## 7. What is missing

| Need | Why | Where it is tracked |
| --- | --- | --- |
| Where and when an act happened | Who could have seen the saw; where a row happened; the back way round | engine request 28 |
| Who saw, heard or was told, in the export | The fixture has visibility only; independent accounts need tellers | request 1 (`eventsKnownBy`) |
| Habits as timetables | Seven in the morning, Thursday evening, past midnight | request 1 |
| Homes, owners and sales | Whose window and garden; "had to sell the house"; who lives in a dead man's house | requests 15 (engine #59) and 24 |
| Goods as things | The boat at a mooring, sold after a death | request 17 |
| Small acts on things, with the thing named | The mended roof, the fixed letterbox; and quirks kept apart from acts | request 20 |
| Records that can be wrong | The Courier's report, a council minute, a poster's credits, a death notice | request 9; plans as documents, request 23 |
| Rites with who came | Andy Shaw's funeral, and who stayed away | request 31 |
| A body over a life | A stiff hand after the saw; a stick after a stroke | request 34 |
| Events before the show year | The old bank's nineteen years have opponents but no reasons | new: export the starting record's weighty events with the past (beside request 33 and #23) |
| A death with a human cause; a fatal accident | Any murder or "did he fall?" mystery | new; scope for Øystein; within Rule 8 |
| The change query, the journal and the why-probe | "What changed here, and why"; accounts kept with sources; "?" for unknowns | `time-on-screen.md`, `interface-and-inspection.md`; the building blocks in `docs/plan.md` |
| A record system in Overstory | Posters, signs and notices with maker, date, claim and stack | `fronts-windows-and-signs.md`, section 8 |
| A case sifter | Chains, kinds, a ledger per person, nobody first seen at their worst | request 7 |

What would serve stories most comes first: habits as timetables and places for events (requests 1 and 28), since routine is the fastest true trace. Homes (15) come next, then small acts on things (20) and records (9).

## Sources

- `fixtures/engine/understory-world-9989.json` (Understory `af02971`, world seed 9989), read in small queries.
- Understory, through the GitHub API: `reports/` reading packs and readings of rounds 27 to 37, `friends-*.txt`, `37-aftermath-*.txt`, `reports/overstory/` (21 October), `SUMMARY.md`, `docs/method/reading.md`; `src/setting.ts`, `src/body.ts`, `src/situations/danger.ts`, `temptation.ts` and `discovery.ts`.
- Ours: `CLAUDE.md`, `NOW.md`, `docs/facts-contract.md`, `docs/living-fabric.md`, `docs/upkeep.md`, `docs/engine-requests.md`, `docs/ideas/first-game-options.md`, and in `docs/research/`: `history-in-things.md`, `behaviour-on-screen.md`, `fronts-windows-and-signs.md`, `time-on-screen.md`, `interface-and-inspection.md`.
