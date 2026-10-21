# World pack B: lives for the football club, the band, the family and the RPG

Paper playtests, round 1 (`docs/playtests/paper-1/method.md`). For the game masters of concepts 1 (`football`), 2 (`band`), 4 (`family`) and 7 (`rpg`). The engine's rules are in `engine-rules.md`; the mystery, the journalist and the observer are in `lives-a.md`. Written 21 October 2026 from Understory's published reading packs, read through the GitHub API at `main`.

## How to use these lives

- **What they are.** Each life is one adult's page from an Understory reading pack: ten simulated years, one line per event, with the reasons the engine gave in square brackets. A line starting with ↳ is an earlier event that a reason points to. They are engine output, not written for the game.
- **Verbatim, with two changes.** Every year is shifted by **−37**, so the packs' 2026 is 1989 and their 2036 is 1999: the first year of every page is the first year on screen. The shift applies to every year in a line and its reasons ("together since 2011" becomes "together since 1974"); ages and spans stay as printed. Anachronisms are swapped and marked ‹period swap›. Nothing else is changed. Excerpts are cut from longer pages; each source names the page to read the rest.
- **Why −37, not `engine-rules.md`'s default −40.** Its rules allow one other shift per world, logged once, to meet the corner. These four worlds need it: the Anchor is open and busy in every pack's first year (11 to 34 lines a pack in 2026), and the fixture opens it in 1988. At −40, three years of Anchor nights would fall before it exists. At −37 nothing clashes, and all ten years play forward from 1989. Log it once per world as `re-dated −37`.
- **One world per concept.** Lives in a reading pack come in threes from one simulated world: each pack's key (`reports/<round>-reading-<pack>-key.json`) gives the same seed for P01 to P03, P04 to P06 and so on, and the on versions of one seed are one world. The pages confirm it: Karen joins Red Sky in her own page, in Susie's and in Alice's. So the three people of a concept below really know each other. Worlds still never meet (`engine-rules.md`, rule 7): names repeat across worlds as different people (there is a Karen, a Molly and a Gary in several). Never mix two worlds' people in one game without renaming, and label the renaming.
- **Which version.** Each pair in a pack shows one person twice, with a round's change on and off. The lives here are the **on** version (the engine as it now stands) unless the source says otherwise.
- **The pack is the world without the player.** Once a player acts on a thread (lends Jonah money, drops a player, backs a café), everything after that on the thread is **GM-simulated** by `engine-rules.md`, and the pack becomes what would have happened. The game master always knows the baseline the player is bending.
- **Years only.** The pack dates events by year. Which month they fall in is **GM-simulated**: spread them through the year, with the summer festival in summer and illness in winter if nothing says otherwise.
- **Labels.** Log each fact with `engine-rules.md`'s labels: `engine` (file, P-number, version), `authored` (the corner's diaries), `GM-simulated`, `re-dated` and `swapped`. This pack adds one: `casting`, where it proposes a life lives or what it touches. Casting is a proposal, never a fact; once used in play, its consequences are GM-simulated.

## The places the packs already share with the corner

- **The Anchor.** In every pack the Anchor is the town's bar and its only stage: cards on Tuesdays, Fridays, open nights, bands. The corner's fixture has it: across the basin, building 3000 (101's diary) "Ruth Hale takes the lease; Ruth opens a bar" in 1988. So the Anchor is open on the first day of every concept.
- **The quay loft.** Across the basin, building 3003 (109's diary): a herring salter's house of 1850, and in 1987 "a band rents the loft cheap". The diary does not say which band; the band section below casts it.
- **The corner's five houses** (`fixtures/lt1-corner.json`, authored). A (104), the jugend house at the foot of the lane, has a café opened in 1988 by a young couple, who buy the house in 1996. B (105), the functionalist house opposite, was painted by new owners in 1987 and lets its ground floor as a bakery in 1997. C (1203), the cooper's house of 1879 by the landing, is two flats: new owners of the upper flat put back copies of the old windows in 1998. D (1107), the fisherman's house of 1828 on the rock, has been boarded since its owner died in 1986; in 1995 the heirs still cannot agree to sell and the roof lets in water. E (304), the smallest house at the top, is kept in 1989 and left empty when its last owner dies in 1993. Casting below never contradicts these diaries; where a life fits a house, the fit is labelled.

---

## 1. The football club: the harbour fleet's side

**World:** Understory seed 3592 (`reports/41-reading-busiest-pack.txt`, pairs P22 to P24, version A, the on version). Three of the busiest adults of one world, all at the harbour fleet or near it. The engine has no sport: the club is cast as the fleet's works side, and every match is GM-simulated. What the record gives is the squad's lives.

### Harry, 35 in 1989

Source: `41-reading-busiest-pack.txt`, P24 version A.

```text
1989: Terry Waller was born to Harry and Agnes Rudd.
1989: Harry got what he had wanted for 4 years: a child.  [Terry Waller was born to Harry and Agnes Rudd.]
1990: Sid asked Harry straight out for money.  [in debt; asking for help worked last time; struggling]
1990: Harry gave Sid the money without being asked twice. It had happened before, in 1987.  [Sid asked Harry straight out for money.; could not stand to see Sid go without; money has never meant much to him]
1994: Harry went to pieces during the visit from head office at the harbour fleet.  [though he does not panic; dreads being looked at; falls apart when watched]
1994: Harry tells the story of the day he froze better than anyone, and always against himself.  [Harry went to pieces during the visit from head office at the harbour fleet.; genuinely quick]
1995: The summer festival that Maisie put on was a washout; Steve and Toby Scott never did their part.  [Maisie has started telling people she means to put on a summer festival on the quay.; though she likes things in order; 3 of the helpers let it down]
1995: Harry has let it be known he wants to be skipper.  [Steve will step down as skipper at the harbour fleet next year.; a strong record; the skipper's job is going]
1996: Harry became skipper at the harbour fleet.  [Steve wanted Harry to have it; the strongest record of 4; likes things done properly and on time]
1996: Harry froze at the first staff meeting.  [though he does not panic; dreads being looked at]
1996: Maisie was passed over for skipper; Harry got the job.  [Harry had the stronger record; had wanted it since 1995]
1996: Agnes Rudd was passed over for skipper; Harry got the job.  [Harry had the stronger record; had wanted it since 1995]
1996: Rose Newman was passed over for skipper; Harry got the job.  [Harry had the stronger record; had wanted it since 1995]
1996: Rose Newman walked out in front of everyone at the harbour fleet.  [Rose Newman was passed over for skipper; Harry got the job.; did not stop to think; comes alive in front of a crowd]
```

**What he leaves in the town (casting).** Two children (1989, 1990): a pram, then small bikes at the door. From 1996 he is skipper, his name on the fleet's board. His freezing is a story the town tells, and he tells it best, against himself. Home: corner **B** fits him and Agnes Rudd. New owners paint it in 1987; the ground floor is let as a bakery in 1997, a year after Agnes walks out of the fleet and the household loses a wage. The diary's cause ("as trade comes back to the quay road") stays the fact; the household's reason is GM-simulated.

### Agnes Rudd, 28 in 1989

Source: `41-reading-busiest-pack.txt`, P23 version A.

```text
1989: Terry Waller was born to Harry and Agnes Rudd.
1991: Agnes Rudd says she'll go too, if Beth goes.  [Beth took on extra work to pay for getting out.; would follow Beth anywhere; needed someone to lean on]
1992: Agnes Rudd went out into the storm.  [a storm came in; danger has never stopped her; wanted the money]
1992: Agnes Rudd took a little from the catch.  [said what would work; thought nobody would notice; wanted the money]
1992: Maisie dragged up what Agnes Rudd did a few months back in front of everyone at the harbour fleet.  [Agnes Rudd confronted Maisie about it in front of everyone at the harbour fleet.; felt slighted; Agnes Rudd confronted Maisie about it (1992)]
1993: Agnes Rudd let Harry take the blame for a mistake at work.  [said what would work; felt it was owed; thought nobody would notice]
1995: Agnes Rudd has let it be known she wants to be skipper.  [Steve will step down as skipper at the harbour fleet next year.; a strong record; the skipper's job is going]
1996: What Agnes Rudd had wanted for 1 year was gone.  [Harry became skipper at the harbour fleet.]
1996: Agnes Rudd was passed over for skipper; Harry got the job.  [Harry had the stronger record; had wanted it since 1995]
1996: Agnes Rudd said nothing and got on with it.  [Agnes Rudd was passed over for skipper; Harry got the job.; is fond of Harry; could wait it out]
1996: Agnes Rudd walked out of the harbour fleet to start again somewhere else.  [What Agnes Rudd had wanted for 1 year was gone.; it hit hard]
1996: Agnes Rudd started work at the garage.  [the only one looking for work]
1999: Agnes Rudd went in after Mona without a second's thought.  [Mona was pinned under a car at the garage.; danger has never stopped her; that is who Agnes Rudd is: not afraid of anything]
```

**What she leaves (casting).** The storm of 1992 is a town event: who went out is remembered. After 1996 she is seen at the garage, not on the fleet's quay. In 1999 she goes in after Mona under a car. Home with Harry (corner B).

### Mark, 35 in 1989

Source: `41-reading-busiest-pack.txt`, P22 version A.

```text
1989: Mark took a little from the medicine cupboard.  [said what would work]
1989: Mark was found out: taking from the medicine cupboard.  [Mark took a little from the medicine cupboard.; though he likes things in order]
1989: Mark walked out of the clinic to start again somewhere else.  [Mark was found out: taking from the medicine cupboard.; it hit hard; it happened at work]
1989: Mark started work at the Old Bank Café.  [the only one looking for work; Greta Tanner likes them]
1991: Mark has let it be known he wants to be owner too.  [Molly let slip she would want it, if it ever came up: to become owner at the Old Bank Café.; Molly is after it; a strong record]
1993: Mark let Molly take the blame for a mistake at work.  [said what would work; Greta Tanner heard what Greta Tanner had got wrong (1993)]
1994: Molly and Mark are both after the owner's job, and it shows.  [Mark has been taking on everything nobody else wants.; neither will give way]
1994: Molly dragged up what Mark did last year in front of everyone at the Old Bank Café.  [Mark let Molly take the blame for a mistake at work.; felt slighted; Mark let Molly take the blame for it (1993)]
1996: Mark told Amelia it was over.  [whether to stay with Amelia; the way Amelia had come to talk to him; they had grown apart]
1996: Mark and Amelia divorced.  [Mark told Amelia it was over.]
1996: Mark and Maisie started seeing each other.  [has energy for everything]
1998: Mark and Maisie got married.  [together since 1996; they had grown close]
```

**What he leaves (casting).** From the first year he is behind the counter of the Old Bank Café (in the town, not on the corner). The divorce of 1996 splits a household: a lit window fewer, or one more. The wedding of 1998 is a public day. The theft of 1989 travels only as people tell it (`engine-rules.md`); whether it reaches the café follows those rules, not the game master's wish.

### Cast and hooks

- **Who is in it.** Harry, the steady one who goes to pieces when watched. Agnes Rudd, fearless, short of money, and a grudge-carrier. Mark, who looks reliable and has a theft behind him. Named around them: Maisie, who puts on the summer festival and marries Mark in 1998; Steve, the skipper until 1996, who takes Harry's credit; Sid, who keeps borrowing from Harry; Rose Newman, who walks out when passed over; Toby Scott and Matt; Eric, who beat Agnes to chief officer; Molly, Mark's rival at the café (not Molly Dale, who lives in another world). Their ages are unknown; expect a random adult's quieter pace (see Pace).
- **Tensions the record already holds.** The skipper's job of 1996 sets four of the squad against each other: Harry wins; Maisie, Agnes and Rose lose; Agnes walks out of the fleet, Rose walks out in front of everyone, Maisie's joke falls flat. Agnes let Harry take the blame for her mistake (1993), and he said nothing. Steve took the credit for Harry's year twice (1990, 1994). Steve and Toby Scott did not do their part of Maisie's festival (1995). Sid owes Harry money (1990, 1994). Harry and Agnes's quiet row about "how little time she gave the family" (1995) is the only place the record touches the hours a player gives a club. Mark and Amelia divorce, and Mark and Maisie begin, in 1996.
- **GM-simulated.** The club itself, its league, fixtures, results, training, selection, form, injuries on the pitch, the pitch, kit, gate money, the clubhouse and any transfer. Model a player's match on the engine's own analogues (rules in `engine-rules.md`): performance when watched ("falls apart when watched", "does not panic"), the open night's outcomes (did well, the room went quiet, fell apart), danger ("danger has never stopped her", "froze while the others went in"), and contests for a place (the stronger record wins; the loser answers by temperament: confronts, walks out, says nothing). The three known players are 28 to 35 in 1989; young players have to be cast from named-only people, GM-simulated. Harry's son Terry Waller (born 1989) is the next generation, after the packs end.

---

## 2. The band: a quay loft and the Anchor's stage

**World:** Understory seed 3585 (`41-reading-busiest-pack.txt`, pairs P01 to P03, version A, the on version). This world has five bands: Red Sky, Low Tide, the Lanterns, the Sawmill Boys and the Mill Hands. Bands, places in them, songs, gigs at the Anchor and open nights are all in the engine.

**Casting the loft.** The record suggests Red Sky is the older band: in 1995 Peter Moore plays Susie's song as his own, and "it had happened before, in 1985". Cast Red Sky as the band that rented the loft in 1987. Low Tide forms in 1989, the first year on screen, with no room of its own. A manager can take either: the town's best band in the loft, or the new band that needs one.

### Susie, 33 in 1989

Source: `41-reading-busiest-pack.txt`, P02 version A.

```text
1989: Since the night the Lanterns played the Anchor, Susie has been teaching herself guitar.  [the Lanterns played the Anchor; people who had come for the beer stayed for the last song.; it stayed with them]
1989: Gary told Susie what Susie wanted to hear.  [Susie asked what he really thought of the plan to go over to computer typesetting and stop the Saturday edition ‹period swap, as in engine-rules.md: the pack says "go online and stop the Saturday print"›; thought nobody would notice]
1990: Alice asked Susie straight out for money.  [in debt; puts other people first; wanted the money]
1990: Susie gave Alice the money without being asked twice.  [Alice asked Susie straight out for money.; could not stand to see Alice go without; that is who Susie is: the one people come to]
1990: Peter Moore would not play Susie's song the way it was written.  [Susie brought a song to Red Sky, "The Empty Harbour", and it was good.; that is who Peter Moore is: meant for more than this; would say it to anyone]
1990: Susie said nothing and got on with it.  [Peter Moore would not play Susie's song the way it was written.; thinks highly of Peter Moore; did not think it was about her]
1992: Susie seized a spot at the Anchor's open night.  [has been playing guitar for years; does not panic; is moved by beautiful things]
1992: Susie played the Anchor's open night and did well.  [Susie seized a spot at the Anchor's open night.; guitar good, not great]
1994: Peter Moore went at Susie about the children, and it got personal fast.  [it had been building between them (the children)]
1994: Greta Eden was gone, and Red Sky had to go on without her.  [Tom left the town for the city. Greta Eden and the children went too.; they genuinely like each other]
    ↳ 1994: Tom left the town for the city. Greta Eden and the children went too.
1996: The summer festival that Eve Lyons put on was a washout; Susie and Andy never did their part.  [Eve Lyons has started telling people she means to put on a summer festival on the quay.; though she likes things in order; 2 of the helpers let it down]
1997: Peter Moore was the first to say Susie's song was the best thing they had.  [Susie brought a song to Red Sky, "What the Coat Knows", and it was good.; thinks the world of Susie]
```

**What she leaves (casting).** Her song titles on Red Sky's set lists and posters ("The Empty Harbour", "After Midnight"). Her name on the open night's board in 1992. Her lending shows only in who can still pay the rent. She works at the Courier, the local paper, which the journalist concept may also use.

### Karen, 21 in 1989

Source: `41-reading-busiest-pack.txt`, P01 version A.

```text
1989: Karen and Larry started a band: Low Tide.  [Karen had been wanting to be heard; they genuinely like each other; Karen is in a different class]
1989: Matt Berry would not hear it from Karen; not after the place in the Lanterns.  [Karen went to Matt Berry and offered to put the old business behind them.; does not forget; Karen was not picked for the Lanterns; Matt Berry got the place.]
1990: Low Tide played the Anchor to a full room, the first in a while.  [they genuinely like each other; Karen is in a different class]
1990: Toby Moore joined Low Tide, a better player than the one who left; it was not the same.  [Low Tide needed someone; the best player going; each brings something the others cannot]
1991: Karen was found out: taking from the medicine cupboard.  [Karen took a little from the medicine cupboard.; though she likes things in order]
1991: Karen would not play Toby Moore's song the way it was written.  [Toby Moore brought a song to Low Tide, "Ferry and Winter", and everyone knew at once it was the best thing they had.; that is who Karen is: meant for more than this; would not give ground]
1992: Toby Moore took Karen aside afterwards and said exactly what Toby Moore thought.  [Karen would not play Toby Moore's song the way it was written.; would not be talked down to; Karen would not play Toby Moore's song the way it was written (1991)]
1994: Ken Ash was born to Gary and Karen.
1994: Karen became head of the clinic.  [the strongest record of 4; likes things done properly and on time]
1996: Karen left Low Tide, quietly: there was a small child at home.  [Ken Ash was born to Gary and Karen.; they genuinely like each other]
1996: Karen was hospitalised with pneumonia.  [age 29]
1996: Karen joined Red Sky; it was not the same.  [Red Sky needed someone; they genuinely like each other]
1996: Alice was not picked for Red Sky; Karen got the place.  [Karen was the better player; had wanted to be heard since 1996; Karen joined Red Sky; it was not the same.]
1996: Alice confronted Karen about it in front of everyone at the Anchor.  [Alice was not picked for Red Sky; Karen got the place.; would not give ground; would say it to anyone]
```

**What she leaves (casting).** Low Tide's posters at the Anchor from 1989, the line-up changing as players come and go. In 1996 her name moves to Red Sky's poster: a record that shows a rift to anyone who knows who was passed over. From 1994 she runs the clinic; in 1998, the harbour day. Her home with Gary is not placed.

### Alice, 28 in 1989

Source: `41-reading-busiest-pack.txt`, P03 version A.

```text
1989: It came out that Alice had been running Matt Berry down.  [Alice made sure people heard about every one of Matt Berry's mistakes. It had happened before, in 1988.; thought rules are for people who get caught; Alice was passed over for foreman; Matt Berry got the job.]
    ↳ 1989: Alice made sure people heard about every one of Matt Berry's mistakes. It had happened before, in 1988.
1990: Alice asked Susie straight out for money.  [in debt; puts other people first; wanted the money]
1993: Alice seized a spot at the Anchor's open night.  [has been singing for years; does not panic; that is who Alice is: not made for one place]
1993: Alice played the Anchor's open night and did well.  [Alice seized a spot at the Anchor's open night.; vocals good, not great]
1994: Alice bets more on the darts than her wages can stand.  [did not stop to think]
1996: Alice walked out of the Old Bank Café to start again somewhere else.  [Mark Lee dragged up what Alice did a few months back in front of everyone at the Old Bank Café.; it had shaken her; it happened at work]
1996: Alice started work at the Anchor.  [the best of 3 looking for work]
1996: Alice was not picked for Red Sky; Karen got the place.  [Karen was the better player; had wanted to be heard since 1996; Karen joined Red Sky; it was not the same.]
1996: Alice confronted Karen about it in front of everyone at the Anchor.  [Alice was not picked for Red Sky; Karen got the place.; would not give ground; would say it to anyone]
1997: Alice was not picked for Low Tide; Gary got the place.  [Gary was the better player; had wanted to be heard since 1996; Gary joined Low Tide, a better player than the one who left.]
1997: Alice walked out in front of everyone at the Anchor.  [Alice was not picked for Low Tide; Gary got the place.; did not stop to think]
1998: Alice had to sell the boat.  [the money had run out; money worries]
```

**What she leaves (casting).** From 1996 she is behind the Anchor's bar on gig nights, serving the bands that would not take her. Her boat leaves its mooring in 1998, a notice of sale before it. The neighbours hear her practise from 1994.

### Cast and hooks

- **Who is in it.** Low Tide: Karen and Larry (1989), Toby Moore (1990), Oliver Lane (1993 to 1994), Gary (1997). Red Sky: Susie, Peter Moore, Stuart Sayer, Greta Eden (gone in 1994), Karen (from 1996). The Lanterns, with Matt Berry, who in 1987 took Karen's place in the band and Alice's foreman's job: one rival for two of the cast. Alice, the hungry outsider. Ruth Hale's Anchor as the stage (fixture).
- **Tensions the record already holds.** Toby Moore brings Low Tide its best songs and Karen will not play them as written (1991); he tells her what he thinks (1992). Peter Moore and Stuart Sayer will not play Susie's songs as written (1990, 1994). Karen steals from the clinic's medicine cupboard and is found out (1991). The place in Red Sky (1996) goes to Karen over her own partner Gary and over Alice, and both confront her in front of everyone at the Anchor. A small child ends Karen's time in Low Tide (1996). Alice borrows from Susie and does not pay it back. Matt Berry and Karen refuse each other's peace three times (1989, 1994, 1997). Greta Eden leaves for the city (1994), and Oliver Lane for university.
- **GM-simulated.** The manager and everything a manager does: bookings, money, the loft's rent and lease, tapes and records, travel, rivals' managers. Venues other than the Anchor. The size of a crowd beyond the record's words ("a full room", "the room went quiet"). What a gig does to the street: the queue on the quay, posters, noise, a neighbour's complaint, the council. The music itself beyond the engine's verdicts ("good", "the best thing they had", "did not come to much"). When gigs happen: these three pages record only 15 gigs and open nights in ten years across five bands (Low Tide four times, Red Sky twice), so a monthly gig is GM-simulated. Understory plans a band followed for a year (its Next 6, after homes); until then the band's week is ours.

---

## 4. The family: an inherited house

**World:** Understory seed 3586 (`41-reading-busiest-pack.txt`, pairs P04 to P06, version B, the on version). One household, Steve Kemp and Molly Dale with their daughters Lynn Dale and Ivy Kemp, and Andy, at the harbour fleet with Molly. Two of the older generation die in the decade: Karen Dale in 1992 and Olive Kemp in 1995.

**Kinship the pack does not state.** The pages never say "mother" for these two deaths. The record treats Molly Dale and Andy as Karen Dale's bereaved: people look in on Molly, Andy stops singing because "it hit hard" (and in the off version the hat goes round for Molly). It treats Steve as Olive Kemp's: he is at her side when she is ill and takes to swimming every morning after she dies. Read Karen Dale as Molly's and Andy's mother and Olive as Steve's, labelled GM-simulated, or confirm the ties through the engine's front door (`engine-bridge`) before play.

### Molly Dale, 32 in 1989

Source: `41-reading-busiest-pack.txt`, P04 version B.

```text
1990: Steve Kemp went at Molly about how little time she gave the family, and it got personal fast.  [it had been building between them (how little time she gave the family); it mattered too much to let go; says what is wrong with people, not with what they did]
1990: Molly met every word of it with a reason it was not her fault.  [Steve Kemp went at Molly about how little time she gave the family, and it got personal fast.; it came at them as an attack; everything Steve Kemp said sounded like an attack by now]
1990: Molly kept away just when Karen Dale needed people.  [Karen Dale was ill; has never been one to look back]
1991: Molly has let it be known she wants to be skipper too.  [Hilda Reed asked Andy straight out what it would take to be skipper.; a strong record; Hilda Reed is after it]
1991: Molly and Hilda Reed are both after the skipper's job, and it shows.  [Hilda Reed asked Andy straight out what it would take to be skipper.; so evenly matched]
1992: Karen Dale died of a sudden heart attack, aged 77.  [age 77; health had worn down]
1992: Toby looked in on Molly most days.  [Karen Dale died of a sudden heart attack, aged 77.; wanted to be there for Molly; that is who Toby is: never turns anyone away, because someone once did not turn him away (1990)]
1992: Thea wasn't there for Molly when it mattered.  [Karen Dale died of a sudden heart attack, aged 77.; had her own life to get on with; has held on tight to the people left since Tom died (1992)]
1992: Steve Kemp looked in on Molly most days.  [Karen Dale died of a sudden heart attack, aged 77.; thinks the world of Molly; Molly had promised Steve Kemp it, and did it (1991)]
1993: Molly brought a song to the Night Shift, "A Boat for Closing Time", and everyone knew at once it was the best thing they had.  [had an idea of her own; a real gift; they genuinely like each other]
1993: Steve Kemp played Molly's song as if it were Steve Kemp's own.  [Molly brought a song to the Night Shift, "A Boat for Closing Time", and everyone knew at once it was the best thing they had.; could wait it out; thinks highly of Molly]
1993: Steve Kemp would not play Molly's song the way it was written.  [Molly brought a song to the Night Shift, "Boat and Shift".; it was nothing special]
1994: Molly sulked about it for months.  [Steve Kemp would not play Molly's song the way it was written.]
```

**What she leaves (casting).** The Night Shift's songs. A chase for the skipper's job from 1991 that the pages never resolve. In 1996 she fixes the letterbox at home without being asked: a repair the upkeep system can show, one of several the record gives (a fence, a front door, help with a roof).

### Steve Kemp, 34 in 1989

Source: `41-reading-busiest-pack.txt`, P06 version B.

```text
1989: Steve Kemp seized a spot at the Anchor's open night.  [has been playing guitar for years]
1989: Steve Kemp played the Anchor's open night and did well.  [Steve Kemp seized a spot at the Anchor's open night.; guitar good, not great]
1991: Steve Kemp went to Sally and apologised.  [wanted to put things right with Sally; thinks the world of Sally; could wait it out]
1991: Steve Kemp got there: to make things right with Sally, after 2 years of wanting it.  [Steve Kemp and Sally are on speaking terms again.; will not leave a job half done; had wanted it since 1989]
1992: Steve Kemp had stopped bringing things up with Molly.  [Steve Kemp let how little time she gave the family go again.; together since 1974]
1992: Lynn Dale has taken to writing, like her father, Steve Kemp.  [grew up with Steve Kemp at it; wanted to know]
1994: Steve Kemp sat Olive Kemp down and asked what was going on. It had happened before, in 1985.  [Olive Kemp has not been herself for months; she keeps to herself and people have started to notice.; it mattered too much to let go; is fond of Olive Kemp]
    ↳ 1994: Olive Kemp has not been herself for months; she keeps to herself and people have started to notice.
1994: Olive Kemp told Steve Kemp it was nothing. It had happened before, in 1985.  [Steve Kemp sat Olive Kemp down and asked what was going on. It had happened before, in 1985.; wanted to be left alone; felt it was owed]
1994: Steve Kemp was at Olive Kemp's side within the hour.  [Olive Kemp was ill; could not let people down who mattered to him; likes things done properly and on time]
1995: Steve Kemp needed surgery.  [age 40]
1995: Olive Kemp died of a sudden heart attack, aged 73.  [age 73; health had worn down]
1995: Steve Kemp now swims in the harbour every morning, whatever the weather.  [Olive Kemp died of a sudden heart attack, aged 73.; it hit hard]
1998: Steve Kemp shied away from a spot at the Anchor's open night.  [has been playing guitar for years; that is who Steve Kemp is: rooted in the town, through and through; it mattered too much to let go]
```

**What he leaves (casting).** From 1995 a man swims off the quay every morning, whatever the weather: a routine anyone could see, and the trace of a death to those who know. He works at the Courier.

### Andy, 45 in 1989

Source: `41-reading-busiest-pack.txt`, P05 version B.

```text
1990: Andy cleared his week for Karen Dale.  [Karen Dale was ill; likes things done properly and on time; that is who Andy is: the one who holds things together]
1991: Andy told Hilda Reed the skipper's job would be hers to win when it came up.  [a strong record; thinks well of Hilda Reed]
1991: Andy has started telling people he means to put on a summer festival on the quay.  [is not one to hang back]
1992: Toby told Andy exactly what was wrong with the plan to put on a summer festival on the quay.  [Andy asked what he really thought of his plan to put on a summer festival on the quay; would rather be straight about it; had nothing to prove]
1992: The council said yes to Andy's summer festival.  [Andy has started telling people he means to put on a summer festival on the quay.; thinks well of Andy; 5 people behind it]
1992: The summer festival that Andy put on was the best night the town had had in years.  [Andy has started telling people he means to put on a summer festival on the quay.; likes things done properly and on time; 5 people pitched in]
1992: Karen Dale died of a sudden heart attack, aged 77.  [age 77; health had worn down]
1992: Andy buried himself in work.  [Karen Dale died of a sudden heart attack, aged 77.; would rather wait it out than fight; will not leave a job half done]
1992: Andy no longer sings with the choir every Thursday.  [Karen Dale died of a sudden heart attack, aged 77.; it hit hard]
1994: Andy tore into Thea in front of everyone at the harbour fleet.  [Thea's work had been poor for months; would say it in front of anyone]
1995: People have noticed: Andy splits things exactly even.  [wanted it to be fair]
1997: Toby told Andy exactly what was wrong with the plan to put on a summer festival on the quay. It had happened before, in 1992.  [Andy asked what he really thought of his plan to put on a summer festival on the quay; would rather be straight about it; had nothing to prove]
1998: The summer festival that Andy put on was the best night the town had had in years.  [Andy has started telling people he means to put on a summer festival on the quay.; likes things done properly and on time; 1 of the helpers let it down]
```

**What he leaves (casting).** The summer festival on the quay, "the best night the town had had in years" in 1992, 1994, 1996 and 1998: a stage, bunting and posters every second summer, and the council's permit as a record. The venture's people are in the record: who said "count me in" (Molly, Harry, Sally, Eric, Toby, Hilda Reed, Larry), who said what was wrong with it (Toby, twice), who said no (Eve, his partner, 1994), and the helper who let it down.

### The house (casting)

Karen Dale's house fits corner **C**, the cooper's house of 1879 by the landing, in two flats. Two heirs, two flats. The diary then holds: "the upper flat's new owners put back copies of the 1879 windows" (1998) means one heir's flat is sold by 1998, and the ground floor's factory "old style" windows (2011) mean the other heir keeps it, cheaply. Andy fits the keeper: "money has never meant much to him", he drives the same old car, he "splits things exactly even" (1995). The inheritance, the sale, who lives there and who pays for the roof are all GM-simulated, and the game master must land the 1998 sale or the casting breaks. Olive Kemp's house (1995) has no corner that fits; place it in the town. Corner **D** is the family's mirror: heirs who cannot agree, and a roof letting in water in 1995.

### Cast and hooks

- **Who is in it.** Steve Kemp, Molly Dale, Lynn Dale and Ivy Kemp; Karen Dale (dies 1992) and Olive Kemp (dies 1995); Andy and his partner Eve; Lily Kemp (tie not stated). The Night Shift as the household's other family: Gary, Beth Newman, Neil.
- **Tensions the record already holds.** Steve goes at Molly about "how little time she gave the family" (1990), and by 1992 he has stopped bringing it up: a silence the player can read. Molly kept away when Karen Dale was ill (1990) while Andy cleared his week for her: the care was unequal before anything is left to anyone. Molly wants the skipper's job (from 1991), and Andy told her rival it would be hers to win. Steve will not play Molly's song as written (1993); she sulks for months. Molly and Eve, Andy's partner, fall out (1991), make it up (1993) and lose touch (1997); the record does not say they are the same Eve, so confirm or label it. Steve's surgery and his mother's death come in the same year (1995). The daughters take after both parents: writing from him, figures and carpentry from her (1996).
- **GM-simulated.** The houses, ownership, wills and the division of the estate; who moves in or out; rooms, furniture and keepsakes; repairs, except the record's own (letterbox, fence, roof help); the corner's physical changes come from its diaries and must not be contradicted. Everything after 1999: the packs end there, so a second generation (Lynn and Ivy as adults) is wholly GM-simulated until the engine runs longer.

---

## 7. The RPG: a role in a living town

**World:** Understory seed 3594 (`reports/41-reading-random-pack.txt`, Jonah Vale P04 version B and Ellen P05 version A, both the on version). Random adults, not the busiest: this is the town's ordinary pace. A venture to back comes from another world (Eve, below); keep her quarter apart.

### Jonah Vale, 28 in 1989

Source: `41-reading-random-pack.txt`, P04 version B.

```text
1989: Jonah Vale bought a boat of his own.  [had been saving since 1984]
1989: Jonah Vale told Oliver Waller what Oliver Waller wanted to hear.  [Oliver Waller asked what he really thought of the plan to open on Sundays; thought nobody would notice; said what would work]
1990: Jonah Vale went to Matt and apologised.  [wanted to put things right with Matt; wanted to keep the peace; thinks the world of Matt]
1991: At the Anchor, Jonah Vale rounds things in their own favour.  [thought rules are for people who get caught]
1993: Jonah Vale put in the smallest coin he could find when the hat went round for Ellen.  [Ellen got caught in the saw at the sawmill.; did not want to part with it; short of money]
    ↳ 1993: Ellen got caught in the saw at the sawmill.
1993: Jonah Vale asked Rose straight out for money.  [in debt; wanted the money; asking for help worked last time]
1993: Rose gave Jonah Vale the money without being asked twice.  [Jonah Vale asked Rose straight out for money.; could not stand to see Jonah Vale go without; thought it only fair]
1995: Jonah Vale asked Evan straight out for money.  [in debt; wanted the money; asking for help worked last time]
1995: Evan gave Jonah Vale the money, and made sure Jonah Vale knew the cost.  [Jonah Vale asked Evan straight out for money.; thought it only fair; can spare it]
1995: Rose and Jonah Vale lost touch.  [Jonah Vale wasn't there for Rose when it mattered (1992); nothing brought them together any more]
    ↳ 1992: Jonah Vale wasn't there for Rose when it mattered.
1996: Sid Nash told Jonah Vale no.  [Jonah Vale asked Sid Nash straight out for money.; did not want to part with it; looks after his own first]
1996: Jonah Vale went to Rose and apologised.  [wanted to put things right with Rose; wanted to keep the peace; thinks the world of Rose]
1997: Jonah Vale took a little from the till.  [thought nobody would notice; wanted the money; said what would work]
```

**What he leaves (casting).** A boat at a mooring from 1989 and a car from 1992, bought on savings while he borrows. He works at the Anchor. The fixture makes Ruth Hale its leaseholder; the pack's Oliver Waller makes its plans (open on Sundays, a summer festival) and is caught at the till in 1994, so cast Oliver as her manager, never the owner. The till is short twice in the decade, once found out.

### Ellen, 25 in 1989

Source: `41-reading-random-pack.txt`, P05 version A.

```text
1989: Una Holmes was born to Colin and Ellen.
1990: Ellen became foreman at the sawmill.  [the strongest record of 3; likes things done properly and on time]
1990: Ivan was passed over for foreman; Ellen got the job.  [Ellen had the stronger record; had wanted it since 1990]
1990: Ivan confronted Ellen about it in front of everyone at the sawmill.  [Ivan was passed over for foreman; Ellen got the job.; that is who Ivan is: meant for more than this; felt it was owed]
1990: Ellen bought a house of her own.  [Colin and Ellen got married.; had the money put by; not worn down]
1993: Ellen got caught in the saw at the sawmill.  [an accident at work]
1993: Sam Baker went in after Ellen without a second's thought.  [Ellen got caught in the saw at the sawmill.; shrinks in front of a crowd]
1993: Gary froze while the others went in for Ellen.  [Ellen got caught in the saw at the sawmill.; was afraid of getting hurt; thought it through first]
1993: Sophie went in after Ellen without a second's thought.  [Ellen got caught in the saw at the sawmill.; danger has never stopped her; thinks the world of Ellen]
1993: Hal Holmes froze while the others went in for Ellen.  [Ellen got caught in the saw at the sawmill.; dreads being looked at]
1993: Oliver Waller had left the wallet at home when the hat went round for Ellen.  [Ellen got caught in the saw at the sawmill.; did not want to part with it; looks after his own first]
1993: Jonah Vale put in the smallest coin he could find when the hat went round for Ellen.  [Ellen got caught in the saw at the sawmill.; did not want to part with it; short of money]
1997: Ellen went in after Victor Lyons without a second's thought.  [Victor Lyons got caught in the saw at the sawmill.; is not one to hang back; thinks the world of Victor Lyons]
```

**What she leaves (casting).** The accident at the sawmill (1993) is this world's public test: who went in, who froze, who gave what when the hat went round. It travels as accounts, which may be wrong. A house of her own from 1990, in the town.

### Eve, 33 in 1989

Source: `reports/37-reading-pack.txt`, P23 version A: the version without round 37's change, from Understory seed 3384. A different world from Jonah's.

```text
1989: Eve and Libby lost the money they had put into the café.  [Sam gave up on the café: the council said no.]
    ↳ 1989: Sam gave up on the café: the council said no.
1992: Eve has started telling people she means to open a café in the old bank.  [has some money put by; the kind who makes things happen; is not one to hang back]
1992: Nora Myers put money into Eve's café.  [Eve has started telling people she means to open a café in the old bank.; could not stand to see Eve go without; thought it only fair]
1993: Tom Shaw told Eve in front of everyone that the town did not need the café.  [Eve has started telling people she means to open a café in the old bank.; the café would take trade from the Anchor; had not forgiven it]
1993: The council turned down Eve's café.  [Eve has started telling people she means to open a café in the old bank.; Toby and Ben and Tom Shaw against it; thought it through first]
1993: Nora Myers and Thea lost the money they had put into the café.  [Eve gave up on the café: the council said no.]
1993: Eve says the café is not finished, only waiting.  [Eve gave up on the café: the council said no.; felt it was owed; that is who Eve is: meant for more than this]
1995: Eve has started telling people she means to open a café in the old bank.  [has some money put by; had meant to bring the café back since 1993; the kind who makes things happen]
1996: It came out that Ben had been running Eve down over the café.  [Ben made sure people heard about every one of Eve's mistakes. It had happened before, in 1994.; thought rules are for people who get caught; Eve has started telling people she means to open a café in the old bank.]
1996: Ben and Eve split up.  [Eve had stopped wanting it; Ben ran Eve down behind Eve's back (1996); Eve can tell when someone is performing]
1996: The council turned down Eve's café.  [Eve has started telling people she means to open a café in the old bank.; thought it through first; Ben and Sophie Dale against it]
1996: Victor and Nora Myers lost the money they had put into the café.  [Eve gave up on the café: the council said no.]
1996: Eve blames Ken for what happened to the café.  [Eve gave up on the café: the council said no.; is easy in her own skin]
```

**What she leaves (casting).** Eve lost money backing Sam's café in the same building before she tried her own: the old bank has a history of refusals. It stays empty through the decade (it is in the town, not on the corner); two council refusals (1993, 1996) and the backers' losses are records. Eve runs the garage from 1995. Corner A's café of 1988 is unrelated; never claim a link.

### Cast and hooks

- **Who is in it.** Jonah Vale, the charming debtor, a natural companion. Karen, his partner since 1980, who comes to stop respecting him. Rose, who lends and is let down, and is won back. Oliver Waller, the Anchor's planner with his own hand in the till. Ellen, the foreman whose accident tests everyone. Sophie, Lynn and Sam Baker, who went in for her; Gary and Hal Holmes, who froze. And from Eve's world: Eve, Ben (her partner, who runs her down), Tom Shaw (who says the town does not need a café), and the backers Nora Myers, Thea and Victor.
- **Tensions the record already holds.** Jonah asks four people for money in six years; one says no. He tells Oliver Waller what Oliver wants to hear three times (1989, 1994, 1998). He takes from the till in 1997, three years after Oliver was caught doing it, and the page does not say he was found out. At the saw, Jonah gave the smallest coin he could find. Eve's café is fought by the people closest to her and by the Anchor's trade.
- **What the record offers a BG3-like role.** Every one of these threads is a choice point with a recorded baseline: lend to Jonah or not; be at the saw; back Eve or warn her; tell Oliver the truth. The engine's reasons say how each person would take it ("does not forget", "lets things go", "thinks the world of"), so reactions can follow the person rather than an approval meter.
- **GM-simulated.** The player character, their acts and their place in the record (the front door's game commands are paused at the engine); dialogue beyond the record's lines; how people answer the player, by `engine-rules.md`; and each thread's future once the player has touched it. Eve's world shares names with Jonah's (Karen, Victor, Ben, Sam, Neil, Sophie); rename on collision and label it.

---

## Pace: what the packs show

Counted on the published packs, the on version only: 48 random adults (rounds 40 and 41) and 24 of the busiest (round 41), ten full years each. A line is one event on the person's page, including others' acts toward them. The packs print no weights, so "life-changing" is our coarse class (a death, birth, marriage, split or new partner; a job won, lost or left; serious illness or accident; a big purchase or sale; a venture's verdict; joining or leaving a band; a theft found out). "Social turning points" are friendships made or lost, rows, apologies, refusals, loans and confidences.

| Per adult, per year (median) | Random adults | Busiest adults |
| --- | --- | --- |
| Lines | 4.9 (0.4 a month) | 7.0 (0.6 a month) |
| Life-changing | 0.3 | 0.6 |
| Social turning points | 1.3 | 1.9 |
| Everyday texture (habits, noticed, small kindnesses, "count me in") | 3.1 | 5.0 |
| Years of ten with nothing life-changing | 7 | 6 |
| Lines in the person's busiest year | 10 | 13 |

- One random adult in five gets fewer than three lines a year. The twelve lives above run from 4.7 lines a year (Agnes Rudd) to 9.6 (Karen), and from 0.2 life-changing events a year (Jonah Vale) to 1.4 (Eve). They were picked for incident; a real squad or band will have quieter members.
- About one line in ten says it has happened before ("It had happened before", "Nobody was surprised any more"). The summer festival, the harbour day and the café take 5 to 8% of lines; music takes 4 to 10% of a random adult's lines and 18% of the busiest.
- Understory's own summary adds what the pages cannot show: one weighty event in five leads to anything later, one in seventeen reaches anyone outside the people involved, and nearly half of adults pursue nothing in ten years. Friendships turn over slowly, at about 0.3 made and 0.3 ended per adult a year.

**Would a player watching one person month by month see enough happen? No.** One person gives something in at most four to seven months of twelve, mostly texture, and a life-changing event every one and a half to three years. The engine's record moves on a season-to-year beat. It is enough in three ways, and the concepts should be built on them:

- **Follow a cast, not a person.** Twelve people at these rates give five to seven lines a month and a life-changing event every two to three months. A squad, a band with its rivals, or a household with its circle is the natural unit.
- **Let a life move a season or a year at a time.** At a year a step, one person gives five to seven lines, one or two social turning points, and a life-changing event every second or third year: enough for a family's years, and close to the engine's own grain.
- **The concept's own loop carries the weeks, GM-simulated.** Matches every week, gigs every month, the house's upkeep: the engine supplies the turning points, and the game supplies the rhythm between them. A band's gig reaches these pages once every two to ten years, and there are no matches at all, so most of what a football or band manager does each week has no engine behind it yet.
