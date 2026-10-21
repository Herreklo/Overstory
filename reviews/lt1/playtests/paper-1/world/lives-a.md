# Lives A: the mystery, the journalist, the observer

Real lives from Understory's reading packs for the three concepts that read the town backwards. How to run them, and how to fill what they lack, is in `engine-rules.md`.

- **Every excerpt is engine output** (`engine`): verbatim lines with their reasons. The only change is the date: every year is shifted by −40 (2026 becomes 1986, 2035 becomes 1995). Pack lines are the truth, secrets included; a player sees only what a witness could know.
- **Worlds.** A pack holds eight worlds of three people each. Each person is shown twice, in two versions of their world (A and B, which differ), and the letter is dealt per pair. Pages share a world only when their events show it.
  - **World X:** Olive, Oliver Waller and Eric share one; their pages share events (Mona Nash's death, Oliver's money in Eric's café, Olive's hospital stays).
  - **World Y:** Hilda's world has a second page in the pack, Maisie Sands.
  - **The other lives** each stand alone.
  - **Names repeat across worlds** as different people (a Ryan, an Olive, a Sid, a Hilda and an Amelia appear in more than one; Understory `docs/STATUS.md`, weaknesses 4 and 8). Lives from different worlds never meet unless the game master simulates the meeting.
- **Casting** is a suggestion, per world. It names the corner house a life could live in (A to E, `fixtures/lt1-corner.json`, `authored`). Where it clashes with an authored event, the engine's fact wins (`docs/facts-contract.md`).
- **The corner,** for reference:
  - **A:** 1912, over a café (1988–2009).
  - **B:** 1936; new owners paint it in 1987; a bakery in 1997.
  - **C:** 1879 two-family house; the upper flat restored in 1998; "old style" ground-floor windows in 2011.
  - **D:** 1828; boarded in 1986 when its owner died, heirs in Oslo; restored in 2007.
  - **E:** 1826; kept in 1989; its last owner dies in 1993; boarded after a break-in in 2008.

## 1. Olive, the reporter who told (World X)

`reports/41-reading-busiest-pack.txt`, P21 version A (pack lines 3465–3577); 75 in 1996. **For:** the journalist, the observer, the mystery (a witness who talks).

```text
1986: Stuart and Olive lost touch.  [Olive retired after 30 years at the Courier.]
1986: Vera finally told Olive what had been kept back.  [carrying something nobody knew; mostly trusts Olive; likes having people around]
1986: Olive told people what Vera had told Olive in confidence.  [Vera finally told Olive what had been kept back.; said what would work]
1988: Olive never made things right with Victor Myers (b. 1916). She had been meaning to for 3 years.  [Victor Myers (b. 1916) died after a long illness, aged 71.; had wanted to make things right with Victor Myers (b. 1916) since 1985]
1990: Olive was hospitalised with pneumonia.  [age 69; a weak constitution]
1990: Olive started drinking more than was good for her.  [Olive was hospitalised with pneumonia.; would rather wait it out than fight]
1991: Bert Tanner rolled his eyes at Olive and talked to Olive like a child about the drinking at the church hill, with people listening.  [it had been building between them (the drinking); it had been building; contempt: looks down on the people closest]
1993: Olive told Bert Tanner it was over.  [whether to stay with Bert Tanner; they had grown apart; the way Bert Tanner had come to talk to her]
1993: Olive and Bert Tanner divorced.  [Olive told Bert Tanner it was over.]
1994: By now Olive was someone who kept to herself; nobody remarked on it any more.  [years of ill]
1995: Eric sat Olive down and asked what was going on.  [Olive has not been herself for months; she keeps to herself and people have started to notice.; has a soft spot for anyone in trouble; thinks the world of Olive]
```

- **Holds:**
  - She retired from the Courier in 1986 and passed on Vera's confidence the same year.
  - Victor Myers died before she made peace with him.
  - She was drinking after pneumonia in 1990, was talked down to in public about it, divorced in 1993, and was withdrawn by 1994.
  - Eric is the one who asks her what is wrong.
  - What Vera told her is not in the record.
- **Traces:**
  - her byline in the Courier's back issues to 1986 (a record);
  - Victor Myers's grave (a fact);
  - bottles in her bin from 1990 (scene state from "drinking since 1990");
  - one name gone from the door in 1993;
  - the hat at the Anchor for her.
- **Casting:** C's upper flat with Bert Tanner (together since 1953). If the flat is sold after the divorce, that fits C's authored "new owners" in 1998; the sale is GM-simulated.

## 2. Oliver Waller, who lost Mona Nash and keeps nobody's secret (World X)

`reports/41-reading-busiest-pack.txt`, P19 version A (lines 3084–3183); 52 in 1996. **For:** the mystery, the journalist.

```text
1986: Mona Nash was gone, and Driftwood had to go on without her.  [Mona Nash died of liver failure, aged 65.; they genuinely like each other]
1986: Oliver Waller now reads late into every night.  [Mona Nash died of liver failure, aged 65.; it hit hard]
1987: Oliver Waller goes out of his way to avoid Leo Nash.  [Leo Nash was passed over for foreman; Oliver Waller got the job.; Leo Nash froze Oliver Waller out for weeks.; Leo Nash is still sore about the foreman's job (1980)]
1987: Oliver Waller put money into Eric's café.  [Eric has started telling people he means to open a café in the old bank.; could not stand to see Eric go without; thought it only fair]
1988: Susie let people think the best of Oliver Waller's song was Susie's. It was the third time, after 1977 and 1982.  [Oliver Waller brought a song to Driftwood, "No Harbour Tonight", and it was good.; said what would work; thought nobody would notice]
1988: Oliver Waller told people what Susie had told Oliver Waller in confidence.  [Susie finally told Oliver Waller what had been kept back.; said what would work]
1988: It got back to Susie that Oliver Waller had been talking.  [Oliver Waller told people what Susie had told Oliver Waller in confidence.]
1989: Eve Tanner and Oliver Waller got married.  [together since 1987; they had grown close]
1990: Oliver Waller talks about a house of his own the way other people talk about the weather.  [Nora was born to Eve Tanner and Oliver Waller.; wants a house of his own (since 1990)]
1993: Oliver Waller no longer talks about wanting a house of his own.  [had wanted it since 1990, and never went after it]
1994: Oliver Waller told people what Agnes had told Oliver Waller in confidence.  [Agnes finally told Oliver Waller what had been kept back.; said what would work]
```

- **Holds:**
  - A death blows only on close kin and the two friends who liked the dead most (Understory `src/aftermath.ts`), so he was one or the other to Mona Nash.
  - He has held the foreman's job against Leo Nash's grudge since 1980.
  - He bankrolled Eric's café.
  - Susie has passed off his songs as hers since 1977.
  - He betrayed Susie's confidence in 1988 and Agnes's in 1994.
  - He married in 1989 and had three children by 1990. He wanted a house of his own and never went after it.
- **Traces:**
  - Driftwood's posters: Mona Nash in the line-up until 1986 (a record);
  - setlists crediting Susie with his songs, a record that is wrong in a way consistent with the engine;
  - a lamp lit late every night from 1986 to 1991 (a habit);
  - a pram from 1989;
  - a row in public at the sawmill in 1994.
- **Casting:** A's upper floors, as tenants over the café. No clash.

## 3. Eric, who opened the café and keeps what he's told (World X)

`reports/41-reading-busiest-pack.txt`, P20 version B (lines 3373–3464); 55 in 1996. **For:** the mystery (the other mourner), the journalist.

```text
1986: Mona Nash died of liver failure, aged 65.  [age 65; health had worn down; drinking since 1985]
1986: Audrey kept turning up at Eric's door with something or other. It had happened before, in 1982.  [Mona Nash died of liver failure, aged 65.; thinks the world of Eric; Eric told Audrey how bad things had got (1984)]
1986: Eric now runs the coast road every other day.  [Mona Nash died of liver failure, aged 65.; it hit hard]
1987: Eric has started telling people he means to open a café in the old bank.  [has some money put by; had meant to bring the café back since 1984; is not one to hang back]
1987: Lily put money into Eric's café. It had happened before, in 1983.  [Eric has started telling people he means to open a café in the old bank.; money has never meant much to her; believes Eric can do it]
1988: Sophie told Eric in front of everyone that the town did not need the café.  [Eric has started telling people he means to open a café in the old bank.; the café would take trade from the Anchor; thought it needed saying]
1989: Eric opened the Old Bank Café in the old bank.  [Eric has started telling people he means to open a café in the old bank.; Oliver Waller and Lily put money in; is not one to hang back]
1990: Eric kept it to himself.  [Lily finally told Eric what had been kept back.; had given his word; thinks the world of Lily]
1992: Eric tore into Amelia in front of everyone at the Old Bank Café.  [Amelia's work had been poor for months; would say it in front of anyone]
1993: Eric had decided Amelia never liked him, and went cool. Amelia, who did, never understood why.  [Eric believed Amelia disliked him (wrongly)]
1994: At the Old Bank Café, Eric is always the last to leave.  [likes having people around]
```

- **Holds:**
  - Mona Nash's death started his running.
  - His café failed once: Lily's money went in in 1983, he "had meant to bring the café back since 1984", and money in a failed plan is lost (Understory `docs/STATUS.md`, Plans).
  - It opened in 1989 over objections for the Anchor's sake.
  - He keeps confidences, where Olive and Oliver tell them.
  - He misread Amelia; the record says wrongly.
  - Mystery trap: the "Mona" at his café in 1992 and 1993 is a different, living Mona.
- **Traces:**
  - a runner on the coast road at dawn every other day from 1986 (a habit);
  - the Old Bank Café's sign from 1989, the last light on the quay;
  - Sophie's public "the town does not need the café" in 1988 (witnessed).
- **Casting:** off the corner. The engine puts the café "in the old bank", which the corner lacks. A's authored Kaffebrenneriet (1988) is its rival, one year older, and the engine never mentions it.
- **Mona Nash:** cast to D, boarded since 1986. Clash: D's authored "heirs live in Oslo" holds only if neither Eric nor Oliver is her child. The packs do not say, so the game master decides once and logs it. The recommendation is that they were her two dearest friends.

## 4. Ryan, who left and came home for a funeral

`reports/41-reading-busiest-pack.txt`, P07 version B (lines 1099–1217); 46 in 1996. **For:** the observer, the journalist.

```text
1986: Ryan and Karen Dale got married.  [together since 1985; they had grown close]
1988: Ryan dropped everything for Amelia Lane.  [Amelia Lane was ill; would not let Amelia Lane down; could not let people down who mattered to him]
1993: Ryan left the town for the city. Karen Dale and the children went too.  [Ryan took a job in the city.]
1993: Ryan was gone, and Pirate Radio had to go on without him.  [Ryan left the town for the city. Karen Dale and the children went too.; they genuinely like each other]
1994: Amelia Lane died of liver failure, aged 71.  [age 71; health had worn down; drinking since 1982]
1994: Ryan came home for Amelia Lane's funeral and stayed.  [Amelia Lane died of liver failure, aged 71.; rooted here: the sea, the people, the house]
1994: Ryan now plays cards at the Anchor on Tuesdays.  [Amelia Lane died of liver failure, aged 71.; it hit hard]
1994: Ryan, Ben and Trevor started a band: Saltwater.  [Ryan had been wanting to be heard; they genuinely like each other; each brings something the others cannot]
1995: Ryan bought the big trip abroad.  [Amelia Lane died of liver failure, aged 71.; had the money put by; not worn down]
1995: Ryan started work at the Anchor.  [the best of 2 looking for work]
1995: Ryan told people what Andy had told Ryan in confidence.  [Andy told Ryan everything, the parts nobody else knew.; likes having people around]
```

- **Holds:**
  - He married in 1986 and had two children in 1987.
  - He looked after Amelia Lane when she was ill in 1988. Only a child living away is offered "came home for the funeral" (Understory `src/body.ts`), so she was his parent; she had been drinking since 1982.
  - He left for the city in 1993, and came home for her funeral in 1994 and stayed.
  - Then came a new band, the big trip abroad, and a job at the Anchor.
  - In 1995 he passed on Andy's confidence.
- **Traces:**
  - Pirate Radio's posters to 1993, Saltwater's from 1994 (records);
  - Amelia Lane's grave, 1994 (a fact);
  - a dark house for a year (GM-simulated: the engine has no homes);
  - a postcard from abroad in 1995.
- **Casting:** B. Its authored "new owners paint it" in 1987 fits a young family. The empty year from 1993 to 1994 is GM-simulated.

## 5. Hilda, who never made it up with Sally Sayer (World Y)

`reports/37-reading-pack.txt`, P12 version A (lines 2007–2076); 53 in 1996. Also P11 version A, Maisie Sands (lines 1870–1968): Sally apologises to her in 1987 and they pick up again in 1990. **For:** the mystery and the journalist.

```text
1986: Hilda started trying to put things right with Sally Sayer, and tells everyone.  [wants to make things right with Sally Sayer (since 1983); not worn down; wants it, but not badly]
1986: Hilda rounds things in their own favour.  [thought rules are for people who get caught]
1987: Hilda got there: to make things right with Sally Sayer, after 4 years of wanting it.  [Hilda and Sally Sayer picked up where they had left off.; though she rarely does more than she has to; had wanted it since 1983]
1989: Sally Sayer and Hilda drifted out of each other's lives.  [they stopped seeing each other]
1991: Hilda let Eddie take the blame for a mistake at work.  [thought nobody would notice; felt it was owed]
1991: Hilda finally told Toby what had been kept back.  [carrying something nobody knew; needed someone to talk to; trusts Toby]
1992: Hilda never made things right with Sally Sayer. She had been meaning to for 3 years.  [Sally Sayer died of liver failure, aged 46.; had wanted to make things right with Sally Sayer since 1989]
    ↳ 1992: Sally Sayer died of liver failure, aged 46.
1994: Hilda became head of the clinic.  [the strongest record of 4]
1994: Lynn made sure Ivan heard about every one of Hilda's mistakes.  [Lynn was passed over for head of the clinic; Hilda got the job.; thought nobody would notice; wants the credit, whatever they say]
1995: Eddie and Hilda buried the hatchet, 2 years after the head of the clinic's job.  [Eddie went to Hilda and offered to put the old business behind them.; lets things go; Eddie was passed over for head of the clinic; Hilda got the job.]
```

- **Holds:**
  - She made peace with Sally Sayer, lost her again, and wanted her back until Sally died at 46 of liver failure in 1992.
  - She "rounds things in their own favour". In 1991 she let Eddie take the blame at the clinic, and that year's confession to Toby was, by the engine's rule, her latest secret act (Understory `src/situations/discovery.ts`): that blame.
  - Lynn spreads her mistakes after Hilda wins head of the clinic in 1994.
  - When Sally began drinking is in the full record, not the pack: GM-simulated until a run is exported.
- **Traces:**
  - Sally Sayer's grave, 1992 (a fact);
  - Hilda's regret, a local event the clinic may know;
  - a new name on the clinic's door in 1994 (a record);
  - Lynn's whispers, told along close ties (accounts, possibly wrong).
- **Casting:** Sally Sayer to E. E's authored death moves from 1993 to 1992, because the engine's date wins. The game master decides once whether her heirs live away. Hilda lives off the corner.

## 6. Arthur, twice widowed

`reports/41-reading-random-pack.txt`, P18 version B (lines 2074–2155); 75 in 1996. **For:** the mystery (two sudden deaths, a row before one), the observer.

```text
1986: Audrey Moore was diagnosed with cancer.  [age 68]
1987: Audrey Moore died of a sudden heart attack, aged 69.  [age 69; health had worn down]
1987: Ryan found reasons to be busy while Arthur was going through it.  [Audrey Moore died of a sudden heart attack, aged 69.; had his own life to get on with]
1987: Arthur now has two pints at the Anchor most evenings.  [Audrey Moore died of a sudden heart attack, aged 69.; it hit hard]
1988: Arthur retired after 13 years at the harbour fleet.  [poor health]
1989: Arthur and Eve Hale started seeing each other.  [does not like to judge; has energy for everything]
1989: Eve Hale went at Arthur about it, and it got personal fast.  [Arthur had a go at Eve Hale about the bills, and it was not about the bills for long.; it mattered too much to let go; it came at them as an attack]
1989: Eve Hale died of a sudden heart attack, aged 78.  [age 78; health had worn down]
1989: Amelia put in the smallest coin she could find when the hat went round for Arthur.  [Eve Hale died of a sudden heart attack, aged 78.; looks after her own first; did not want to part with it]
1990: Arthur kept it to himself.  [Ryan told Arthur everything, the parts nobody else knew.; had given his word; is fond of Ryan]
1994: Arthur started drinking more than was good for him.  [Arthur had a heart attack.; would rather wait it out than fight; did not stop to think]
```

- **Holds:**
  - Audrey Moore was diagnosed with cancer in 1986 and died of a heart attack in 1987. The engine names the cause by her state at death (Understory `src/body.ts`), so the record is right and the town may still wonder.
  - He took to two pints most evenings and retired in poor health.
  - In 1989 came Eve Hale, a row about the bills, and her death at 78 that year.
  - He kept Ryan's secret, and drank after his own heart attack in 1994.
- **Traces:**
  - two graves in two years;
  - his evening seat at the Anchor from 1987 (a habit);
  - the hat twice, Amelia's "smallest coin" included;
  - bottles from 1994.
- **Casting:** A's upper floors in his world, near the Anchor. A's authored sale to the café owners in 1996 fits Arthur selling at 75 (GM-simulated).

## 7. Ivy, who carries other people's mistakes

`reports/41-reading-random-pack.txt`, P03 version A (lines 199–276); 57 in 1996. Her partner is Edward Kemp, together since 1959. **For:** the journalist, the mystery (an accident, and who froze).

```text
1986: Ivy lied to cover a mistake at work.  [Edward Kemp took the credit for Ivy's work (1982)]
1986: Ivy was found out: the cover-up came out.  [Ivy lied to cover a mistake at work.; had let it slide, as she does]
1986: Stuart Fielding let Ivy take the blame for a mistake at work.  [felt it was owed; said what would work; thought nobody would notice]
1986: Ivy went over the side at the harbour fleet.  [an accident at work]
1986: Edward Kemp went in after Ivy without a second's thought.  [Ivy went over the side at the harbour fleet.; thinks the world of Ivy]
1986: Stuart Fielding froze while the others went in for Ivy.  [Ivy went over the side at the harbour fleet.; bold about everything except physical danger]
1986: Thea went in after Ivy without a second's thought.  [Ivy went over the side at the harbour fleet.; is not one to hang back; puts other people first]
1986: Ivy dragged up what Stuart Fielding did a few months back in front of everyone at the harbour fleet.  [Stuart Fielding let Ivy take the blame for a mistake at work.; Stuart Fielding let Ivy take the blame for it (1986); would say it in front of anyone]
1989: Edward Kemp let Ivy take the blame for a mistake at work.  [felt it was owed; said what would work; thought nobody would notice]
1991: Ivy took it badly, and let everyone see it.  [Edward Kemp let Ivy take the blame for a mistake at work. It had happened before, in 1989.; Edward Kemp let Ivy take the blame for it (1991)]
1994: Ivy can't stand Maisie.  [Maisie let Ivy take the blame for it (1994); Maisie let Ivy take the blame for it (1994); had run out of patience]
```

- **Holds:**
  - In 1986 she was found out covering a mistake, took Stuart Fielding's blame, and went over the side.
  - Edward Kemp went in after her; Stuart Fielding froze.
  - From 1989, Edward lets her take the blame for his mistakes. It is a secret act (Understory `src/families.ts`): coworkers don't see it, but Ivy, its target, does.
  - In 1991 she "let everyone see it": the town saw the anger, not its cause.
- **Traces:**
  - the 1986 rescue on the quay (local);
  - a garden worked every morning from 1986 (a habit after being found out);
  - the 1991 outburst;
  - the 1994 feud with Maisie.
- **Casting:** a low-road context house beside D and E (the fixture's placeholders). D is boarded and E's owner dies in 1993, so neither fits.

## 8. Sid Ash, the teacher with the trip money

`reports/34-reading-pack.txt`, P21 version B (lines 3430–3507); 71 in 1996. **For:** the observer (a garden let go and taken back), the journalist.

```text
1986: Sid Ash took a little from the trip money.  [thought nobody would notice; said what would work; wanted the money]
1987: Hannah Sayer died of a sudden heart attack, aged 70.  [age 70; health had worn down]
1987: Sid Ash is no longer out in the garden every morning from spring to autumn.  [Hannah Sayer died of a sudden heart attack, aged 70.]
1987: Sid Ash now reads late into every night.  [Hannah Sayer died of a sudden heart attack, aged 70.; it hit hard; despite: not who Sid Ash thinks he is: rooted in the town, through and through]
1990: Sid Ash retired after 20 years at the school.  [age 66]
1992: Sid Ash has not been himself for months; he keeps to himself and people have started to notice.  [carrying something nobody knew; Sid Ash skipped the drink afterwards, again.]
1992: Ivan stopped trying to reach Sid Ash.  [5 times in 1 years: carrying something nobody knew; though slow to anger]
1993: Once again, Sid Ash is out in the garden every morning from spring to autumn.  [things had settled]
1993: Sid Ash came through it, after 2 years of carrying something nobody knew.  [Sid Ash skipped the drink afterwards, again.; the pressure had eased]
1993: Sid Ash went quiet when Hal's name came up.  [wants to make things right with Hal (since 1977); though he would rather be on his own]  (and once more between)
1995: Grace found out what Sid Ash had been saying about "The Morning at the Ferry".  [Sid Ash let people think the best of Grace's song was Sid Ash's.]
```

- **Holds:**
  - He took from the school trip money in 1986.
  - His partner Hannah Sayer (together since 1980) died in 1987; he dropped the garden and read late.
  - He retired in 1990.
  - From 1991 to 1993 he carried "something nobody knew", which by the engine's rule is his latest secret act. The latest on his page is the 1986 skim. Ivan gave up trying to reach him.
  - He has wanted to make up with Hal since 1977.
  - In 1995 he was found out claiming Grace's song.
- **Traces:**
  - a garden wild from 1987 and worked again from 1993, the observer's best return;
  - a window lit late every night;
  - no record of the trip money anywhere in the engine.
- **Casting:** C's ground floor in his world, the flat by the landing with the garden. No clash before 2011.

## What the engine can't give a murder mystery

- **A killing.** This is the biggest gap. Death has four natural causes (Understory `src/body.ts`). Accidents and storms injure, never kill (`src/situations/danger.ts`). There is no violent act: hostility is words, coldness and whispers (`src/families.ts`).
- **A death's circumstances.** The engine records no place, hour, finder or scene; there are no police, inquest or will. The month is the finest grain.
- **Dispute about a death.** A death is public, and everyone hears it. Telling stops once its subject is dead (`src/telling.ts`). Only the acts around a death are told and bent.
- **Objects, homes, letters, newspaper text.**
- **The dead person's own page,** for most deaths. Mona Nash, Sally Sayer and Amelia Lane have none here. Why they drank is in the full record only, until a run is exported (`src/tools/fixture.ts`, #68).

## How to stage a death honestly

1. **Take a death the record holds.** Never change its month, age or cause.
2. **Make the case about the acts around it,** which the engine records: who wasn't there when it mattered, what each gave to the hat, whose secret was told, who never made things right, who took up a habit the month after (the closest, by rule).
3. **Suspicion lives only as a belief someone tells.** It starts from a seen act and goes to one close hearer, maybe second hand once. It is bent by dislike. Only an insincere teller names the wrong person.
4. **Simulate what the engine lacks** (who found her, the state of the house) as GM-simulated, consistent with the record. It must never imply another cause: no poison, no fall, no blow.
5. **The answer must be reachable from what the world shows.** In an honest case, "who killed her?" is answered with "nobody; this is what happened instead".
6. **If the card needs a killer,** the crime is fiction outside the engine. Label it end to end, keep engine people out of the killer's role, and log it as a candidate engine request.

## Case seeds

**1. Two heart attacks** (mystery; Arthur's world, 1989).
- **The premise.** Eve Hale dies the year she and Arthur row about the bills; his first partner died two years before. A rumour says his temper did it. The rumour is GM-simulated in telling's shape, from someone who saw him snap, as he snapped at Ryan in 1987.
- **Evidence:**
  - two graves, aged 69 and 78;
  - Audrey's 1986 diagnosis (who knew follows the witness rules);
  - the row, private, so only the two knew it unless one told;
  - the hat;
  - his evening pints since 1987.
- **The solution.** Both deaths are natural and the record stands. The player traces the rumour to its teller and shows how it was bent.

**2. What Ivy carries** (journalist; Ivy's world, 1986–1994).
- **The question.** Why did a fisher who was saved in 1986 erupt at work in 1991?
- **Evidence:**
  - the crew's accounts of the rescue (who went in, who froze);
  - the public accusations between Ivy and Stuart Fielding in 1986 and 1987;
  - the 1991 outburst;
  - the 1994 feud.
- **The secret.** Only Ivy and Edward Kemp hold it, and either may confide in a friend (about 8% of months).
- **The solution.** The man who saved her lets her carry his mistakes. Anyone who says so gives an account, not a verdict.

**3. The boarded house on the rock** (mystery, cold case; World X).
- **The premise.** In 1989 D has been boarded since Mona Nash died in 1986 "of liver failure, aged 65", having drunk for a year. Who was she to the town?
- **Evidence:**
  - Driftwood's posters;
  - two habits begun the month after her death, Eric's dawn runs and Oliver's late lamp; by rule only her closest take the blow;
  - Audrey's and Matt's visits to Eric's door;
  - Leo Nash, with the same surname, a grudge against Oliver and no stated kinship: the namesake trap.
- **The solution.** Eric and Oliver were her closest; her heirs are away. Why she drank is GM-simulated until a run is exported: an answer to strain or a blow, logged.
