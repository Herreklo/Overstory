# A role in the town: card

Concept 7 (`rpg`) for paper playtest 1, for game masters, setup writers, analysts and the lead. Players see only the pitch.

## The question

Does holding one of the town's own lives give Baldur's Gate 3's reactivity when the engine answers monthly? From the panel: a round is the engine's month, whose one situation per life is the sifter; witnesses are named (Kingdom Come); the clock runs regardless (Pathologic 2); reads have counts (Disco Elysium); the goal and its date show in minute one.

**Judged by** prereg Rp1 to Rp4 (unseen acts answered, lives on; the sceptic's goal and risk by round 3; witnesses named, against lives off; the pull of players 2 and 5) and each round's scored prediction of how someone will treat you.

**What would change our minds.** For: lives-on players trace a coldness to an act a month back and name who carried it. Against: fewer than one unseen answer a round lives on, or equal care about witnesses in both arms.

## The pitch

**Store page.** *Word Gets Round.* A harbour town, spring 1992. You are one of its people, with a past you didn't choose: a job lost to a better record, a band you founded, a daughter who stayed away when you were ill. Each week you act: visit, help, give, keep a secret or tell it, make peace or refuse it. Each month the town answers, and nobody keeps it to themselves: what you say at the Anchor on Friday reaches your kitchen by June, told by someone who doesn't like you. You want one thing, by a date. A year on, you come back to see what your choices became.

**Tutorial.** A round is a month; each week is a turn, and a turn is one act: visit and talk (up to three things said or asked), help, give, ask, promise, keep or tell, make peace, keep away, watch a place, or wait. Some months the town puts a choice to you; answering takes a turn. Every act has witnesses, named on screen. At the month's end you see how people treat you now. Your journal keeps what you saw and heard, and your reads, with counts. Your goal and its date are on your page.

## Role, goal, resources

**Role:** one of six townspeople from March 1992, with household, job, band, routines and, lives on, their past as lived, their own private acts included.

**Goal:** one per start, the same in both arms, with a date; lives on, with the engine's reason.

**Resources:** four turns a month; ties with up to ten people on five steps (close, warm, easy, cool, cold), kept by the GM and never shown; a purse (comfortable, tight or short); routines, which keep contact; your secrets.

## Opponents and pressure

The goal's date; witnesses; telling, which travels and bends without you; ties that cool unmet; other people's wants; the town's own events.

## Failure

**Outright:** the goal is lost when its person goes cold or its date passes, and the screen says so; you play on without it. One session can do it: a public slight (two steps) and a told confidence that gets back.

**Partway:** a cooler tie, an ended friendship, a broken promise, a lapsed routine, a partner gone cold.

## Decisions that cost

1. **The month's situation.** Answer as the record did and its consequences follow; otherwise they are struck and simulated from the other side's page. Eddie Lane can walk out of the café in March 1992, as he did, or stay under Lisa Myers.
2. **Where, and before whom.** At the Anchor on Friday everyone sees and it travels; at a door, only the household. A slight in public costs two steps, not one.
3. **Keep or tell.** Telling warms the hearer, but half the time it gets back and the friendship ends.
4. **The week:** four turns between the goal, the circle and your routines, which lapse if skipped two months.
5. **The hat** (Kate Holmes, April 1992; Sam Brook, March 1993): a lot, the smallest coin, a note unseen, or nothing. People count who gave what.
6. **Through whom,** which lives make harder and better: a peace or favour carried by someone the target likes lands softer, by someone they dislike harder. Lives off, there are no likings to learn.

## Mastery

**Hour 1:** acts in public, tells confidences for quick warmth, takes one cold shoulder for the whole person. **Hour 5:** knows who sits with whom, chooses where to be seen, goes through people the target likes. **Hour 10:** plays the lag (a kindness in March for June), keeps ties met, treats counts as reads. Reading pays at the jump: how the town remembers you sets how your first acts land.

## Juul's six

- **Rules:** four acts a month, one situation, witnesses, telling, a date.
- **Variable outcome:** the goal won or lost; ties warmer or colder.
- **Valued outcomes:** the goal, the people kept, your name.
- **Effort:** where, before whom, through whom, when.
- **Attachment:** your life, and the people you'd lose.
- **Negotiable consequences:** a fictional town.

## The three dials

- **Control: medium.** Your acts and situations, never another's decision.
- **Influence: local but real.** Ties move by GM-simulated answers; the record changes only where its causes run through a choice you changed.
- **Knowledge:** your own life and what witnesses could know, bent; true standings at the close.

## Screens and verbs

**Screens:** the place at that week's hour (the Anchor on Friday, Tuesday cards, Thursday choir, the garage, the clinic, the sawmill yard, your kitchen) and who is there doing what, shown, never said (the far side of the room, a dish at the door); your page (goal, household, purse, routines, past, secrets); "A month on"; the Courier and posters.

**Verbs:** inspect, talk, watch, read, travel, wait; plus visit, help, give, ask, promise, keep, tell, make peace, keep away.

**Interface:** hover names; the journal, word for word; reads with counts ("cold to you twice since March"), yours and fallible; the why-probe, for public events found, giving the stated reason, otherwise "ask someone who was there".

## The clock

**Rounds 1 to 3:** March to May 1992. **The jump:** one year. **Round 4** opens in March 1993 where your costliest choice was made: who is there, who isn't, what changed. Lives on, the year lands: Ellie Holmes's death (D-02), the harbour day (C-15), the editor's wedding (C-16), Sam Brook's heart attack, the festival's yes (C-18). **Rounds 4 to 6:** March to May 1993, ending on the festival.

## What the engine feeds and what the game master simulates

**Engine (lives on), filtered by visibility:** the six lives, March 1992 to May 1993, with bonds from cause labels; the town's months (the Night Shift at the Anchor, e-7191; the hats, e-7204 to e-7208 and e-7443 to e-7445; Ivan Tanner's peace refused, e-7449; the washout, e-7499); records C-13 to C-21, P-05, P-06, D-02. **Never shown:** anyone else's private act (Larry Baker's money to Leo Lyons, what Larry carries) or a confidence's content. Rule 8: Hannah Tanner is Lily Tanner's widow, said plainly.

**GM-simulated**, seeded `rpg-<arm>-<id>-r<N>-t<turn>-<what>` and logged:
1. **Situation** (`sit`): the setup lists each month's engine situation and its options (`engine-rules.md`). As recorded, it stands; otherwise strike it and its forward chain, as the setup lists.
2. **Answer** (`ans-<person>`, d6): 3+ if a stated trait or bond (the carrier's included) favours the act, 5+ if one argues against it, else 4+; lives off, 4+.
3. **Witnesses:** those involved or present (the setup's routine lists), plus partner and coworkers unless the act is private.
4. **Gossip** (`gossip-<witness>`, d100): to a partner or friend on ≤ 25 × sociability; lives off, to household or band on ≤ 12.
5. **Telling** (`tell-<act>`): a weighty act (two steps, or public) goes from its target or a witness to the friend they like most who knows you, bent by liking, and again on 4+. Sincerity under −0.8 names the wrong person on d20 ≤ 3. Lives off, it goes to household or band, unbent, and the same tellers slip at random.
6. **Ties:** a step warmer for a kindness seen or heard, or a confidence told; a step cooler for a slight (two in public), a broken promise, or three months unmet. A told confidence gets back on 4+ and that friendship goes cold. A routine skipped two months running lapses. Start from the engine's bonds; lives off, at easy (partner, household and band warm).
7. **Promises** fall due in 1 to 4 months; a friend confides in you on d100 ≤ 8 a month (`confide`), its content never given.
8. **The festival** (`night`): good with every part in, a washout with two out, else good on 4+.
9. **The jump:** the record runs, minus struck chains, with illness and death as recorded; a raised tie keeps its gain only where household, work, band or a routine brings you together.

**Six starts and goals,** start n for player kind n:
1. **Terry Sutton**, council office, married to Mona Sayer: his thirteenth festival a good night (May 1993). Rows (e-7216, e-7255), retirement (e-7224), helpers (e-7302 to e-7349).
2. **John Holmes**, sawmill foreman, the Night Shift's founder: his name and band kept to May 1993. Susie drifts (e-7180), Ivan's peace (e-7448), Susie's apology (e-7471); lives on, he has run Ivan down since 1977 (e-6800).
3. **Kate Holmes**, after a heart attack, married to Larry Baker: Vera Holmes warm by May 1993. Vera kept away (e-7153), Kate's sulk (e-7181), the festival part (e-7495).
4. **Susie Lyons**, retired from the Courier: John Holmes back by May 1993. The drift (e-7180), Leo Lyons's word (e-7183), carrying on (e-7203), the apology (e-7471).
5. **Eddie Lane**, passed over for the café, married to Tess Lane: Larry Baker a friend by August 1993. The walk-out (e-7184), Tess's row (e-7218), the harbour day (e-7237), Larry (e-7247).
6. **Terry Baker**, clinic, married to Sally Baker: three friends by May 1993, family together. Rows (e-7221, e-7258), the hat (e-7205), whether to stay (e-7476).

## Lives on and lives off

**Lives off changes:** no past, reasons, bonds or wants; goals without reasons; answers at even odds; others' routines never lapse; the off world's situations, events and festival. **Identical:** cast, households, jobs, bands, dates, starts, goals, rules, rolls and screens. **The off arm** is a shallow life sim: people answer by the dice, and every why gets "nothing on record says why". **Expected if lives matter:** lives-on players learn how people take things and plan through those they like; lives off, answers read as noise.

## Memory probe, tenth hour, exit

- **Probe (round 4):** the goal's person, the first to answer an act they hadn't seen, and a household member.
- **Tenth hour:** June to October 1993 as your strategy would play it; lives on, the Night Shift called back (e-7511), Larry Baker not himself (e-7504), Peter Scott's boat (C-22) and, unless struck, John and Ivan's reckoning (e-7594, e-7608). Then the close: true standings, the goal, and what each changed choice became.
- **Exit:** "What do you believe happened between you and <the goal's person>, and to <two others>, and why?" Others by start: (1) Toby Waller, Mona Sayer; (2) Ivan Tanner, Susie Lyons; (3) Larry Baker, Hannah Tanner; (4) Leo Lyons, Steve Baker; (5) Lisa Myers, Tess Lane; (6) Sally Baker, Agnes Tanner.

## Honest weaknesses

- **Most reactivity is ours,** more so as play diverges: the engine answers only its own situations, so a gap may measure the GM.
- **Chosen lives:** six of 76 in their busiest months; the median adult does one notable, knowable thing a year.
- **John Holmes is in three starts.**
- **Confidences have no content,** and players know their own private acts.
- **The panel's risks stand:** ties gamed as meters, and no core challenge beyond people.
- **Cohort X met Terry Sutton's expense claims in the paper.**
