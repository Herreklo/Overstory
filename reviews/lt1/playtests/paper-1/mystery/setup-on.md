# Answerable (the mystery): setup, lives on

What every lives-on run of the mystery shares. Arm folder `a`, cohort Y (`arms.md`). Game masters, auditors, analysts and the lead read it; players never do. The design is the card, `docs/playtests/paper-1/cards/mystery.md`; this page instantiates it from world 9989. Where they differ, the card wins, and the difference is under Gaps.

**Who plays.** Pre-registration amendment 1 (`docs/playtests/paper-1/prereg.md`) cuts the mystery to kinds 2, 4, 5 and 6, with no cold start: Y2, Y4, Y5 and Y6 play here, each with the pitch and tutorial. The six starts below are all written; starts 1 and 3 have no run this round. Each run's own truth is in `a/<id>/gm.md`.

**Look facts up** with `python3 -I world/tools/w9989.py person|year|find|chain`. Town year = engine year − 37. Every event id below is the real run's.

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

**Authored days** (`authored`, logged SETUP once; the engine gives months only):
- Mary Tanner died on Monday 10 February 1997, at home: the house on the church hill where Mark Holmes lives. The screens never say who owns it. Notice D-03 ran on Thursday 13 February, the funeral was on Wednesday 19 February at eleven, and the obituary C-32 ran on Thursday 20 February.
- **The hat for Mark Holmes** went round on Friday 7 March 1997, in the evening, at the Anchor (e-8494 to e-8496, March 1997).
- Andy Shaw died on Wednesday 14 October 1998, at home on the Gully Steps. D-04 and C-35 ran on Thursday 22 October. The funeral is on Tuesday 27 October at two, at the churchyard on the church hill, and Pirate Radio play at the Anchor afterwards.
- **Andy's evening walk**, every evening of case 1, in both arms: out at about half past five, down the Gully Steps to Harbour Row, along the quay to the shore, and back up the steps at about seven. It instantiates his shore-walk routine and puts him alive in every start (card rule 10).
- Both hearings are held upstairs at the council office on Market Square, at ten.
- The Courier comes out on Thursdays. Its back room holds the bound volumes from Thursday 15 June 1989 (C-01) and this year's loose issues.

## 2. The case at the start

The player is the district's coroner's officer (authored; no engine life). By custom every death is heard, and the coroner asks the same six questions:

1. Of what did she (he) die?
2. Since when was she (he) unwell?
3. Was anyone answerable for the death?
4. Who stood by her (him) and the household?
5. Was there bad blood, and did it bear on the death? (Case 2 adds: and did anything settle it?)
6. Does the printed record of the death and the life stand?

Case 1 opens with the coroner's file: Mary Tanner, 77, died Monday 10 February at home on the church hill, and the notice D-03. Case 2 opens in round 3 with Andy Shaw's file: Andy Shaw, 85, died Wednesday 14 October at home on the Gully Steps, with D-04 and the same six questions. Neither file holds anything else.

## 3. The card's rules, instantiated

Every roll is seeded `mystery-a-<id>-r<N>-t<turn>-<what>` and logged.

| Rule | Instantiation |
| --- | --- |
| Turns | 4 a round, one act a turn; 8 turns for case 1 and 16 for case 2, each hearing the last. |
| **1. Yield** (`q<k>`, d6 a question) | 1: "I couldn't say." 2 to 5: one fact this person could know (section 6). 6: that, plus a join of their own, from their chatter (section 8) or in telling's shape (rule 6). **Kin** (case 1: Mark Holmes; case 2: none, see Gaps) start guarded: one question a visit, and on a 1 or 2 they say "Not today." If kin ever turn open, they take two questions at most. |
| **2. Bend** (`bend`) | By liking (section 4). A teller who likes the subject softens: leaves out the subject's fault and puts the best face on it. One who dislikes the subject hardens: their fault is put first. No listed tie, no bend. |
| **3. Wrong name** (`name`, d20) | The five tellers in section 4 slip on 3 or less: the account names the wrong person, drawn uniformly (`who`) from the other people in that account's event list. |
| **4. Heard** (`heard`, d6) | After each talk act, for each absent person the player asked about: they turn guarded on 4+ if the one asked is their partner, family or a friend (section 4), otherwise on a 6. Someone asked first, before anyone was asked about them, stays open. Guarded lasts to the end of the case. |
| **5. Complaint** (`complaint`, d6) | A second visit to close kin (Mark Holmes) in one round: on 4+, standing −1. |
| **6. Talk about the dead** | Takes telling's shape (`engine-rules.md`, How news travels). It starts with someone who was there or was wronged; it goes to the friend or partner they like most; it may pass once more, less surely; and it bends with liking. A person can say only what a witness could know (section 6). |
| **7. Watches** | A watch shows who keeps a routine at that place in that month (section 5), the month's local events that happen there, and an ended routine as an absence, to the month, without its reason ("Mary Tanner hasn't sat in since December '94"). Nobody hears of a watch. |
| **8. The coroner's test** | At the hearing, a claim stands on the player's own sighting (something on one of their screens), a first-hand witness (someone in the event, or a partner or coworker for a non-private event, named in the journal), a dated record (Courier, notice, poster), or two independent second-hand tellers (neither heard it from the other). Anything else is hearsay and is struck. Anyone named in the account is summoned. A summoned person gives first-hand evidence of what the record shows, honestly for public and local events. A private act of their own stays private, and their denial strikes any claim that rests on it. |
| **The ruling** | *Rejected:* the account names anyone answerable for the death. Standing −2, and that person, their partner, family and friends close to the player for the rest of the session (GM-simulated; engine lives unchanged). *Adjourned:* two or more claims struck, or a claim that some act bore on the death (naming nobody answerable) struck. Standing −1, and the town knows (people turn guarded on a d6 of 5+ at the first visit of the next case). *Accepted:* anything else. At standing 0 the player is taken off the cases. |
| **9. The check** (`CARD`) | Once a case, from its second round, as one act. The player names three claims on the board. The game master compares them with the record and answers only "all three stand" or "not all three stand". |
| **10. Andy alive** | Every start shows Andy Shaw alive in round 1, on his evening walk. What the player saw then is first-hand at his hearing. |
| **Standing** | Starts at 3 of 6. Complaint −1, adjourned −1, rejected −2. An accepted account with no claim struck: +1 (see Gaps). |
| **Willingness** | Open, guarded (one question a visit) or closed. At the start, Mark Holmes is guarded and everyone else is open. Hover shows it. |
| **The why-probe** | Free. It answers only for a public event the player has found, with the record's stated reason in plain words: Mary's death (e-8459), "age 77; her health had worn down"; Andy's death (e-8899), "age 85; his health had worn down"; the split (e-8374), "they want it to sound like different things; Oliver Brook, Edward Baker and Sarah Lane each need to be the one who matters". For anything else it says "Ask someone who was there." |
| **Local news by chance** | Staff of the Anchor, the clinic, the school and the Courier may know a local event they weren't in: the first time one is asked about it, d6 (`knows`) 4+, logged GM-simulated. |

**Scoring (the close, `scores.md`).** Case 2: the ten facts (section 7) at 10 each; partly right 5; contradicted −5; an innocent named −20; total clamped to 0 to 100. Naming anyone answerable is naming an innocent. "?" scores 10 only where no witness could know; for fact 10 this setup finds witnesses, so "?" scores 0. Case 1: its four facts, scored right, partly or wrong, and reported apart.

## 4. Ties that bend and slip

**Liking** (from bond causes in the record; most are private, so they shape tellers and never reach a screen):

| Subject | Liked by (softens) | Disliked by (hardens) |
| --- | --- | --- |
| Mary Tanner | Olive Shaw, Sylvia Waller, Terry Sutton; friends with Toby Waller since 1989 (e-6477, local) | Mona Sayer (local) |
| Mark Holmes | Edward Baker, Larry Baker, Leo Lyons, Greta Brook | |
| Andy Shaw | Trevor Lane, Oliver Brook, Ben Reed ("think the world of him") | |
| Edward Baker | Toby Waller (thinks the world of him), Olive Shaw (fond; she gives him money when he asks, private); Andy respects him | |
| Olive Shaw | Matt Sayer, Leo Lyons, Edward Baker, Sean Hale | |
| Colin Berry | Thea Waller, Eve Vaughan | Toby Tanner (local) |
| Karen Holmes | Terry Sutton, Mona Sayer | |
| Sarah Lane | Leo Holmes | Alice Tanner |

**Friends** for rule 4 are the liked-by column and any `friends` event between the two.

**Tellers who slip a name** (rule 3). The export has no sincerity field, so these are `GM-inferred` from their own record of passing something off or letting someone else carry it: Edward Baker (e-7869), Colin Berry (e-7580), Peter Scott (e-6446), Oliver Brook (e-8356), John Holmes (e-7594). The off arm uses the same five names.

## 5. Routines that place people

March 1997 (watches and who is where; `hab.py`-style reading of each person's habit events):
- **Tuesday cards at the Anchor:** Edward Baker, John Holmes, Ivan Tanner, Mark Holmes, Mona Sayer, Molly Scott, Olive Shaw, Larry Baker, Tara Myers, Terry Sutton, Steve Baker, Leo Lyons, Toby Waller, Grace Waller, Eve Vaughan, Colin Berry, Sally Baker, Ellie Eden. Mary Tanner played from 1969 and stopped in December 1994 (e-7856, private: only the absence shows).
- **Two pints at the Anchor most evenings:** Edward Baker, John Holmes, Mark Holmes, Olive Shaw, Larry Baker, Gary Myers, Oliver Brook, Leo Lyons, Colin Berry, Lynn Newman, Ellie Eden. Tara Myers stopped in February 1997 (e-8471, local).
- **Thursday choir:** Andy Shaw (since 1976), Karen Holmes, Terry Sutton, Leo Lyons, Colin Berry and others (look up).
- **Swims off the harbour steps at seven:** Toby Waller, Susie Lyons, Thea Waller, Toby Tanner, Bert Kemp, Libby Fielding. Andy swam from 1964 until January 1990 (e-6593, private): his absence shows, its reason never.
- **Shore walk every evening:** Andy Shaw; Mary Tanner from May 1996 to her death (e-8280, private return, visible as a routine).
- **Gully Steps:** Hannah Tanner, shed and practising nightly, Friday Anchor, reads late; Karen Holmes, garden every morning, Sunday dinner, Thursday choir.
- Toby Waller is out in the garden every morning from March 1997 (e-8486, private: only the routine shows).

October to December 1998: look each up. Olive Shaw retired from the bar in March 1998 (C-33) and still has two pints. Andy's Thursday choir chair and his shore walk are absences from October 1998. Trevor Lane is at the Anchor every Friday from November 1998 (e-8943, private: the routine shows, its reason never). Ben Reed reads late every night from November (e-8944, private).

## 6. The cast, and who could know what

Ages are March 1997 · October 1998. Willingness at the start: open unless marked. Households and couples as the record gives them.

| id | Name | Ages | Work | Household and family | What they could know |
| --- | --- | --- | --- | --- | --- |
| p-22 | Mary Tanner | died at 77 | retired | married Mark Holmes 1981; no children | subject, case 1 |
| p-17 | Andy Shaw | 83 · died at 85 | retired | widower of Stella Shaw (married 1957, died 1978); no children; lives alone on the Gully Steps | Case 1: Mary walked the shore at his hour from May 1996 (GM-simulated co-presence of two routines). Himself: unwell since spring 1996 (e-8229, his own), the song (e-7868 to e-7870), the split (e-8374). He gives the year his swimming stopped, never a reason. Subject, case 2. |
| p-25 | Mark Holmes | 76 · 78 | retired | widower of Mary; father of Vera Holmes with Kate Holmes; lives alone on the church hill | **Kin, guarded.** Mary's strokes, first-hand (e-6556, e-6970); his own stroke (e-6807); "polite, and that was all" (e-7598, local, his own); the death (e-8459); the hat for him (e-8494 to e-8496). Never his drinking (e-8461) or who stayed away (e-8462 to e-8464). |
| p-37 | Olive Shaw | 66 · 68 | Anchor bar staff; retired March 1998 | married Ben Reed 1992; mother of Eric, Oscar and Peter Lane with Trevor Lane | Case 1: the hat for Mary, 1990 (e-6616, hers); Mary's note in Olive's hat, 1995 (e-8048, local). Case 2: A-12 (right); A-18 (wrong, credits Edward); staff, by chance. |
| p-19 | Edward Baker | 81 · 83 | retired | father of John Holmes; lives alone | **Slips names.** Case 2: the song, first-hand (e-7868 to e-7870, his own claim), e-7890, e-8105, the split (e-8374), the hat for Andy (e-8565). |
| p-63 | Leo Lyons | 74 · 76 | retired | father of Neil and Beth Lyons with Susie Lyons | Case 1: his wallet at home for Mark's hat (e-8494). Two pints, cards, choir. |
| p-27 | Mona Sayer | 74 · 75 | retired | married Terry Sutton 1977 | Case 1: Mary's impression of her (e-7168, e-7695, local); hardens on Mary. Case 2: A-29 (right). |
| p-48 | Terry Sutton | 70 · 71 | retired | married Mona Sayer | Case 1: his folded note for Mary, 1990, unseen (e-6618); Mary's note for him, 1996 (e-8198, local). |
| p-67 | Toby Waller | 68 · 69 | retired from the clinic April 1996 | married Grace Waller 1965; father of Thea and Sylvia Waller | Case 1: Mary's friend from 1989 (e-6477). Case 2: a 1989 swimmer, first-hand to Andy's absence from January 1990; A-05 (absence right, guess wrong). Clinic, by chance, to April 1996. |
| p-68 | Grace Waller | 70 · 72 | retired | married Toby Waller | Case 2: a note in Andy's hat, not a small one (e-8567). |
| p-2 | Hannah Tanner | 81 · 83 | retired | widow of Lily Tanner (married 1949); mother of Sid Tanner; the Gully Steps | No tie to Mary in the record. Case 2: Andy's neighbour: his comings and goings, his practising from June 1998 (GM-simulated sightings of routines). |
| p-4 | Karen Holmes | 72 · 74 | retired | mother of Owen Lane with Rose Lane; the Gully Steps | No tie to Mary in the record. Case 2: the peace with Andy, July 1998, first-hand (e-8858, local; her approach e-8857 is private); the 1992 rebuff (e-7166, A-12). |
| p-12 | Ken Scott | 39 · 40 | editor, the Courier | married Sylvia Waller 1992; son of Audrey Scott | The paper's records. Case 2: Colin's coin dragged up (e-8886) and Colin walking out (e-8905). |
| p-91 | Toby Tanner | 39 · 41 | reporter, the Courier | lives alone | Wrote C-32 and C-35. A 1989 swimmer: first-hand to Andy's absence from January 1990, yet wrote C-35's join. Courier staff, by chance. |
| p-82 | Colin Berry | 48 · 50 | reporter, the Courier; walked out October 1998 | married Thea Waller 1991 | **Slips names.** Wrote C-30 and C-33. The smallest coin in Andy's hat (e-8566). |
| p-55 | Oliver Brook | 40 · 42 | skipper, the harbour fleet | seeing Agnes Tanner from March 1997 (e-8506); son of Greta and Sam Brook | **Slips names.** Driftwood 1990 to 1996, Pirate Radio 1998. The song (e-7868, e-7890), e-8105, the split, e-8356 (his own), Pirate Radio (e-8752, e-8830, e-8892), the most in Andy's hat (e-8563), the band-place rows at the Anchor. Never the visits or the money. |
| p-39 | Eric Lane | 44 · 46 | crew, the fleet | son of Olive Shaw and Trevor Lane | Case 1: emptied his wallet for Mary, 1990 (e-6615). |
| p-90, p-110, p-111, p-116 | Bert Kemp, Oscar Ash, Maisie Baker, Libby Fielding | 45, 41, 26, 23 | crew, the fleet | | Coworkers of Oliver and Eric. |
| p-81 | Evan Newman | 56 · 58 | manager, the Anchor | lives alone | Staff, by chance. A-01, A-04, A-25 (right). |
| p-96 | Peter Scott | 45 · 46 | bar staff, the Anchor | | **Slips names.** Staff, by chance. |
| p-109 | Agnes Tanner | 29 · 31 | bar staff, the Anchor | seeing Oliver Brook | Staff, by chance. A-28 (right). |
| p-42 | Larry Baker | 75 · 77 | retired | married Kate Holmes 1984; father of Gary Myers | Case 1: Mark's friend (never his visits, e-8462). Case 2: A-26 (right). A stroke, October 1998 (e-8897, local). |
| p-51 | Greta Brook | 73 · 75 | retired | mother of Oliver Brook | Case 1: the most in Mark's hat (e-8495). |
| p-99 | Una Waller | 30 · 32 | the school | | Case 1: the smallest coin in Mark's hat (e-8496). Pneumonia, October 1998 (e-8898). |
| p-21 | John Holmes | 51 · 52 | foreman, the sawmill | son of Edward Baker and Ellie Holmes | **Slips names.** Case 1: emptied his wallet for Mary, 1990 (e-6617); lost touch with her, 1994 (e-7837). |
| p-64 | Neil Lyons | 48 · 50 | the sawmill | married Eve Vaughan 1967 | Case 2: A-20 (right); Pirate Radio. Found out, December 1998 (e-8969). |
| p-74 | Eve Vaughan | 53 · 54 | the clinic | married Neil Lyons | Case 1: Mary stopped seeing her, October 1996 (e-8391, local). Clinic, by chance. |
| p-69 | Thea Waller | 40 · 41 | the clinic (lead) | married Colin Berry 1991 | A 1989 swimmer. Clinic, by chance. |
| p-38 | Trevor Lane | 69 · 71 | retired | father of Eric, Oscar and Peter Lane with Olive Shaw | Case 2: thinks the world of Andy; knew he was ill (first-hand; never the weekly visits). A-30 (right). |
| p-72 | Ben Reed | 56 · 57 | retired | married Olive Shaw | Case 2: thinks the world of Andy; knew he was ill. Never what Andy told him (e-8539, e-8880) or the money. |
| p-73 | Alice Tanner | 27 · 28 | the sawmill | daughter of Ivan Tanner and Molly Scott | Case 2: passed over, went at Andy at the Anchor (e-8831, e-8832, her own). |
| p-80 | Sarah Lane | 20 · 21 | the sawmill | daughter of Tess and Eddie Lane | Case 2: Driftwood January to September 1996; passed over, shouted at Andy (e-8833, e-8834). Leaning on everyone, November 1998 (e-8947). |
| p-79 | Eddie Lane | 49 · 51 | the garage | married Tess Lane 1978 | Case 2: the most in Andy's hat (e-8564). |
| p-31 | Sean Hale | 45 · 47 | the Old Bank Café | son of Molly Scott | Case 2: Pirate Radio. |
| p-62 | Susie Lyons | 72 · 74 | retired | with Steve Baker since 1981 | A 1989 swimmer. |

Others appear by routine (section 5): look them up before they speak.

**The same-sex couples in this cast,** stated as the record states them: Lily and Hannah Tanner, married 1949 (Hannah is Lily's widow); Owen Lane's parents are Karen Holmes and Rose Lane. Arthur Eden and Ryan Vaughan (1953) are not in this cast.

## 7. The answers, and how a player could reach them

### Case 1, Mary Tanner (four facts, reported apart)

| Q | Fact | Record | Routes |
| --- | --- | --- | --- |
| 1 | A sudden heart attack. | e-8459 (public); D-03, C-32 | The notice; the obituary; the why-probe; anyone. |
| 2 | Strokes in December 1989 and June 1991, survived; no illness before the death. | e-6556, e-6970 (local); C-32 | Mark (first-hand); C-32 (dated); the givers to her 1990 hat (Eric Lane, Olive, John Holmes, Terry Sutton); staff by chance; Andy saw her walk the shore every evening of her last nine months. |
| 3 | Nobody answerable. | e-8459 causes: age 77, health worn down | The why-probe; no record or witness gives a cause. |
| 4 | Who stood by her household: the hat for Mark, Friday 7 March: Greta Brook put in most, Una Waller the smallest coin, Leo Lyons had left his wallet at home. | e-8494 to e-8496 (local) | Being at the Anchor that evening (own sighting); the three and Mark; Friday regulars there; A-25 (Evan, after). |

Ruled on but not scored. **Q5, bad blood:** the marriage was polite and no more from October 1993 (e-7598, local); she stopped seeing Sylvia Waller (April 1990, e-6645) and Eve Vaughan (October 1996, e-8391), and lost touch with John Holmes (November 1994, e-7837). None bore on her death. These are the card's false joins. **Q6:** D-03 and C-32 both stand.

### Case 2, Andy Shaw (ten facts, 10 points each)

| # | Fact | Record | Routes a player could have |
| --- | --- | --- | --- |
| 1 | Cancer. | e-8229 (April 1996), e-8534 (June 1997), e-8878 (September 1998), all local; who: Andy | Trevor Lane, Oliver Brook, Ben Reed (first-hand: he told them; never the visits); clinic, Anchor, school and Courier staff by chance. No record names it. |
| 2 | Ill from spring 1996. | e-8229; C-30 ("unwell since the spring", September 1996) | C-30 (dated, right on this point); Andy himself in case 1; the above. |
| 3 | Nobody caused his death. | e-8899 (public): age 85, health worn down | The why-probe; D-04, C-35 ("after a long illness"). |
| 4 | Two of the four biggest givers to the hat, July 1997: Oliver Brook and Eddie Lane put in more than anyone, Edward Baker emptied his wallet, Grace Waller a note and not a small one. (Colin Berry the smallest coin.) | e-8563 to e-8567 (local) | The givers; A-26 (Larry Baker); Anchor regulars there that night (authored: Friday 11 July 1997). |
| 5 | Karen Holmes made peace with him, July 1998, 27 years after the café. | e-8858 (local; her approach e-8857 private) | Karen; A-29 (Mona Sayer); staff by chance. |
| 6 | Alice Tanner and Sarah Lane went at him at the Anchor, June 1998, over the place in Pirate Radio. | e-8831 to e-8834 (local) | Alice; Sarah; A-28 (Agnes Tanner); those in the Anchor that week; C-34 prints only the place. |
| 7 | Nothing settled it: he took it and kept his head down. | e-8841, e-8842 (local) | Staff by chance; the people at the Anchor after; the why-probe on his death. |
| 8 | "Christmas Fence" is Andy's, and Edward Baker let people think the best of it was his. | e-7868, e-7869, e-7870 (local); e-7878, e-7890; e-8105 (public) | Oliver (in the band); Edward (slips, bends his own); A-20 (Neil, right); against: A-18 (Olive, wrong), C-26 and P-08 (wrong). |
| 9 | Driftwood split over the sound, not over his illness. | e-8374 (public) | The why-probe; Oliver, Edward, Sarah; against: C-30 (wrong). |
| 10 | His swimming stopped in January 1990, six years before any illness. | e-6593 (private: only the absence shows) | The 1989 swimmers, first-hand to the absence: Toby Waller, Susie Lyons, Thea Waller, Toby Tanner; A-05 (absence right, guess wrong); Andy himself in case 1 (the year, no reason); against: C-35 (wrong). |

Facts 3 and 5 to 10 carry reasons. **The obituary's three errors** (the card's test) are C-35's swimming, the C-26/P-08 credit, and C-30's split.

## 8. Records and chatter

All are perceived information: hand over the record's words only, never its GM note. Courier texts are in `world/records-9989.md`.

| Record | Date | Right? | Use |
| --- | --- | --- | --- |
| C-26 | 16 March 1995 | wrong: "Christmas Fence" owes its best lines to Edward | fact 8 |
| P-08 | 10 March 1995 | wrong credit: (Shaw / Baker) | fact 8 |
| P-09 | 15 March 1996 | right | door 2's loft door, still up in March 1997 |
| C-30 | 19 September 1996 | wrong cause of the split; right that he was unwell from spring | facts 2, 9 |
| D-03 | 13 February 1997 | right | case 1 |
| C-32 | 20 February 1997 | right | case 1 |
| C-33 | 26 March 1998 | right | Pirate Radio formed; Olive retired |
| C-34 | 25 June 1998 | right, partial | the band place |
| P-13 | 18 September 1998 | right | on the Anchor's wall from September, still up in November; a poster naming a dead man |
| D-04 | 22 October 1998 | right ("as he asked" is authored) | case 2 |
| C-35 | 22 October 1998 | wrong: the swimming | fact 10 |
| C-36 | 19 November 1998 | partial | Colin gone; Vera at the Courier |

**Chatter** (`records-9989.md`, section 4; the speaker says it only when at the Anchor in the record's month, or later as memory in telling's shape): A-05 (Toby Waller, February 1990, the swimming), A-06 (Ivan Tanner, February 1990, the hat for Mary, wrong about Terry), A-12 (Olive, February 1992, Karen's rebuff), A-18 (Olive, January 1995, wrong), A-20 (Neil Lyons, March 1995, right), A-25 (Evan, March 1997, the hat for Mark: say it only after Friday 7 March), A-26 (Larry Baker, July 1997), A-28 (Agnes, June 1998), A-29 (Mona, July 1998), A-30 (Trevor Lane, November 1998).

**The windows.** Local and public events a watch or a bar can show: in February and March 1997, e-8471, e-8475 (the Night Shift's show), e-8481, e-8490 (Colin found out, Courier staff only), e-8492 (Andy leaned on people), e-8494 to e-8496, e-8500, e-8506. In October to December 1998: e-8897, e-8898, e-8901 (treat as a friendship already true), e-8902, e-8905, e-8921 to e-8923, e-8926, e-8927, e-8939, e-8940, e-8947, the hat for Larry (e-8951 to e-8954; Olive gave most), e-8960, e-8966, e-8969, e-8972, the hat for Una (e-8973 to e-8975), e-8977. Others by `w9989.py year`.

**Never on a screen,** in any wording or hint: Mary's doubts (e-7192), Mark's drinking (e-8461), who found reasons to be busy (e-6562, e-6978, e-8463, e-8464), Larry's visits (e-8462), Olive's and Mary's visits to each other (e-6977, e-8005), why Toby Waller took up the garden (e-8486); why Andy's swimming stopped (e-6593), his debts and the money friends gave him (e-7613, e-8093, e-8493, e-8677), the weekly visits (e-8540 to e-8542, e-8881 to e-8883), what he told Ben Reed (e-8539, e-8880), the roof help (e-8404, e-8430), Karen's approach (e-8857), and why Trevor and Ben took up their routines (e-8943, e-8944). Andy's house shows no repair that tells a story.

## 9. The six starts

Each start is a different door into the town, with a case-1 thread and a case-2 thread. Every start shows Andy Shaw alive on his evening walk. Kind k starts the same in both arms; `setup-off.md` lists where an off screen differs.

| Kind | Door | Place, day, time | Who is there | Case-1 thread | Case-2 thread | Played this round |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | The Courier's back room | Market Square, Mon 3 March, 5:40 pm | Ken Scott (front office), Toby Tanner typing, Colin Berry laying out a page | D-03, C-32 and the bound volumes; Toby Waller; the clinic | C-35's writer is a 1989 swimmer; the archive (C-26, C-30, P-08); Colin's empty desk in round 3 | no (amendment 1) |
| 2 | The band | the fleet's berth on the quay, Mon 3 March, 5:45 pm | Oliver Brook and his crew; P-09 on the loft door | Eric Lane's 1990 hat; his mother Olive | the song, the split, Pirate Radio, the hat | Y2 |
| 3 | Tuesday cards | the Anchor, Tue 4 March, 7 pm | Olive dealing to Mark, Edward and Leo; four more tables | Mary's empty chair since December 1994; Mona, Terry, Toby Waller | A-18, A-29; Edward | no (amendment 1; it was the cold start) |
| 4 | The Gully Steps | Mon 3 March, 5:30 pm | Andy coming out; Hannah in her shed; Karen at her kitchen sink | Andy (Mary on the shore, 1996) | Karen's peace; the neighbours; the dark house | Y4 |
| 5 | The widower | Mark Holmes's kitchen, the church hill, Mon 3 March, 5:45 pm | Mark (guarded) | the strokes; the hat for him on Friday | the Anchor's regulars; Larry Baker | Y5 |
| 6 | The Anchor's bar | Mon 3 March, 7 pm | Evan, Olive, Peter; ten regulars | Evan, Olive; the hat on Friday | Agnes (A-28); P-13; Olive gone; Trevor's Fridays | Y6 |

**Start 1** (not played). The Courier has a front office and a back room on Market Square. Ken calls through: "If it's Mary Tanner, the notice was in the thirteenth and Toby's piece in the twentieth." The bound volumes run 1989 to 1996, and the 1997 issues sit loose in a box file, the newest Thursday 27 February. Through the back window, across the basin, Andy walks the quay towards the shore. Probe: Toby Tanner, Toby Waller, Andy Shaw. Round 3: Colin Berry's desk is cleared, C-35 is the newest issue, and Vera Holmes starts in November.

**Start 2.** The boats are in. Oliver Brook, skipper, hoses down his deck; Eric Lane, Bert Kemp, Oscar Ash, Maisie Baker and Libby Fielding stack boxes. The warehouse loft door above the berth is padlocked, and P-09 is pasted on it, sun-faded. Andy passes along the quay to the shore without stopping. Oliver: "Coroner's, is it? Give us ten minutes and I'm yours." There is no active band of Oliver's in March 1997 (Driftwood split in September 1996). Probe: Oliver Brook; Agnes Tanner or, if not met, the case-1 witness met most who returns in case 2; Andy Shaw. **Round 3** (Monday 26 October 1998, the berth at the same hour): the same crew, two years older; P-13 pasted on the loft door over the corner of P-09; no old man on the quay.

**Start 3** (not played). Cards night. The tables: Olive Shaw dealing to Mark Holmes, Edward Baker and Leo Lyons nearest the bar; Mona Sayer, Terry Sutton, Toby Waller and Grace Waller; Ivan Tanner, Molly Scott, Steve Baker and Eve Vaughan; Larry Baker, Tara Myers, Colin Berry and John Holmes; Sally Baker and Ellie Eden two-handed by the window. At the bar: Gary Myers, Oliver Brook, Lynn Newman. Staff: Evan Newman, Peter Scott, Agnes Tanner. Andy passes the front window at ten past seven. Probe: Olive Shaw, Mona Sayer, Andy Shaw. Round 3: Tuesday 27 October, the funeral day, with Pirate Radio at the Anchor after.

**Start 4.** The lamps on the steps have just come on. Andy comes out of his door above the half-landing and goes down past the player, a hand on the rail. Across the steps, Hannah Tanner's shed is lit and she is at the bench (her shed routine); one house up, Karen Holmes is at her kitchen sink. No roof patches or repairs are described. Door 4 has no tie to Mary in the record (Gaps): its case-1 thread runs through Andy. Probe: Hannah Tanner, Karen Holmes, Andy Shaw. **Round 3** (Monday 26 October, half past five): Andy's windows are dark and his door is shut; Hannah's shed is lit as before; Karen at her sink; nobody comes down the steps.

**Start 5.** Mark Holmes opens his door: "You'll be from the coroner. Come through." A plain kitchen with a table and two chairs, a range, a dresser and a garage calendar on this month. From the window, down the hill, Andy walks the shore in the last of the light. Nothing in the house tells a history. Mark is guarded (kin); rule 5 applies to a second visit in a round. Probe: Mark Holmes, Larry Baker, Andy Shaw. **Round 3** (Monday 26 October, a quarter to six): Mark, two years older, opens the same door; the kitchen is the same; nobody on the shore.

**Start 6.** An ordinary Monday at the Anchor. Behind the bar: Evan Newman, Olive Shaw, Peter Scott. Regulars with pints: Mark Holmes, Edward Baker and Leo Lyons by the fire; John Holmes, Larry Baker and Gary Myers along the bar; Oliver Brook and Colin Berry by the dartboard; Lynn Newman and Ellie Eden by the window. Evan: "Mary Tanner? Ask away. I'm here till eleven." Andy passes the front window at about ten past seven. Probe: Evan Newman, Olive Shaw, Andy Shaw. **Round 3** (Monday 26 October, seven o'clock): Olive is gone from behind the bar (retired in March; she may be at a table with her two pints); Agnes Tanner is on with Evan and Peter; P-13 is on the wall by the door; no one passes the window at ten past seven.

The card's round-3 marks, used where the door allows: Olive gone from the bar; Pirate Radio's poster up; Andy's empty chair at Thursday choir (a watch of the choir shows it).

## 10. The tenth hour and the exit

After round 6's hearing, the tenth hour (300 to 500 words) runs the next twenty turns as the player's own strategy would: the close (scores, causes and weights, the truth about each fact); the town's talk of the account (those named hear of it, by the rules); Neil Lyons found out at the sawmill (e-8969, December 1998); then, plainly, no death to the record's end, January 1999, so no third case. The exit question for understanding: "What do you believe happened to Andy Shaw, Edward Baker and Sarah Lane, and why?"

## Gaps

- **No cold start.** Amendment 1 drops kind 3, the mystery's cold kind; every played opening has the pitch and tutorial. Starts 1 and 3 are written but have no run.
- **"The obituary's three errors"** in the card's test means the three wrong records about Andy (C-35's swimming, the C-26/P-08 credit, C-30's split), not three errors in one obituary.
- **The card's bar,** "4 of the 6 facts that have reasons", sits beside a list of seven facts with reasons (3, 5 to 10). Analysts read it as 4 of 7 unless the lead says otherwise.
- **Case 1 is thin** and its records are right: D-03 and C-32 hold no error. Q5's false joins are its only traps.
- **Case 2 has no kin.** Andy has no partner or children, so the kin rules (guarded at the start, "not today", complaint) touch nobody in case 2.
- **Standing has no gain** on the card, yet its middle goal is standing 5. Instantiated as +1 for an accepted account with no claim struck.
- **Sincerity is not exported.** The five tellers who slip are GM-inferred (section 4).
- **No band of Oliver's in March 1997.** Driftwood split in September 1996 and Pirate Radio forms in March 1998, so door 2 meets the band through its leader and a year-old poster.
- **Hannah Tanner is not at Tuesday cards in March 1997** (she is by October 1998). Door 4 has no tie to Mary in the record; its case-1 thread is Andy, through two evening routines.
- **The churchyard is not cast** in the atlas; "the church hill" is the engine's own phrase, and the churchyard is placed there (`authored`).
- **The days, the home, the hearing room, the hat's Friday and Andy's walk** are authored (section 1).
- **Off arm.** The off world has no hat, no illness, no reasons and no lapsed routines, so its fact slots hold who, when and where (`setup-off.md`).
