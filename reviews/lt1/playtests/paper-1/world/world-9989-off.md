# World 9989, lives off

The control arm's world for paper playtest 1 (`docs/playtests/paper-1/method.md`, "The control: lives on against lives off"). Game masters only: players never read this page or its file, and never learn their arm.

- `world-9989-off.json`: the off world, in the same shape as `fixtures/engine/understory-world-9989.json`, and like it in engine years (town year = engine year - 37).
- `tools/lives_off.py`: `python3 -I tools/lives_off.py` rebuilds the file and prints the check; `check` checks it as it stands; `person NAME [FROM TO]` prints one person's real and off events side by side, in town years.

## How the arm was made

The off world keeps the real run's cast and replaces its lives. It is seeded (`world-9989-lives-off-1`): two runs give a byte-identical file.

The cast is kept with its dates and without reasons. That means names, sexes and births, and the four deaths ("Ellie Holmes died, aged 76."). It means every job and job change (hired, moved, promoted, retired, let go, walked out), households, and partners (seeing each other, married, split, divorced). It also means arrivals, departures and homecomings; bands and who joined, left or split; ventures' kinds, owners and dates; and the places of work.

The other 2,355 events are replaced. Each becomes one line from 212 generic templates, the kind a shallow life sim writes: "Larry Baker had a long week at the sawmill", "Maisie Myers twisted an ankle on the gully steps". A line keeps its real event's subject, year, visibility, notability and number of people. Its month is drawn again within the year, so lines don't bunch around a death or a divorce the way causes do.

The others in a line come from that year's pool of the real run's appearances, so everyone takes part in exactly as many events a year as before. Each line first draws its kind of tie (partner, family, workmate, bandmate, anyone) at the real run's shares, so people spend time with the same kinds of people. What they do together is generic.

Nothing carries. Causes lists are empty. There are no decision tags, no "Noticed:" reads, no gossip or telling, no promises, debts, secrets, wants or grudges, and no line refers back. A pair can fall out in March and have lunch in April.

Guards keep chance from writing an arc. There is no illness in the two years before a death, and no low mood for close family in the year after one. A couple has no rows in the year before they part, and nobody has trouble at work in the year before being let go. Children meet only family and other children, and the Anchor is for adults. Work lines need a job that month, and "got engaged" only happens to a couple who marry within two years. A car or boat bought in an off line joins that person's attachments.

Bands, festivals, harbour days and the open night keep their counts, dates and people. Their outcomes are dealt again at random from the real ones, so the rates stay exact: how a show or an open night went, whether a song caught on, each festival part and night, each harbour day. The council says yes at the real festival rate, 15 in 16. Song titles are generic. Festival helpers are drawn from outside the real crew, who came out of regard for the owner.

Routines are drawn fresh, as many per person as before, and never lapse. The town has no past: past ventures and the Sawmill Boys stay in the file for its shape, with no helpers or events, and are never shown.

## The check

```
events: real 2635, off 2635
per person-year (660 as subject, 678 taking part):
  events as subject      same in 660/660
  events taking part in  same in 678/678
  visibility mix         same in 660/660
  notability-band mix    same in 618/660   (the other 42 all had a re-dealt outcome or a festival line)
whole run: private 1271, local 1203, public 161; bands A 1157, B 569, C 780, D 129; each year the same
kept states the same, type by type; causes 2602 -> 0; decisions 1571 -> 0
shows great 14, good 10, plain 8; festival nights good 3, bad 2 (as real)
everyone alive and in town at every event; 0 lines that reach back or give a reason;
0 illnesses before a death, couple lines for non-couples, work lines without a job, children at the bar
```

Bands are notability under 500, 500 to 999, 1000 to 1999, and 2000 and over (per mille). Ties come close to the real run: partners 367 lines against 463, workmates 169 against 188, family 27 against 37, anyone else 674 against 538.

## How game masters run it

Same card, screens, verbs, clock and visibility filter as the lives-on arm. Only the record underneath differs.

- The why-probe gives what happened, when, and who could have seen it, then "nothing on record says why". Never supply a reason.
- A person's page shows name, age, job, household, partner, band, routines and events, and no reads of character. Asked why, a person has no reason to give. Simulated decisions are a seeded draw at the engine's base rates (`engine-rules.md`), since there is no character to decide from.
- The Courier writes generic local news from public off events, plus local ones as notable as the on arm uses, at the same number of items an issue. Its mistakes come at the same rate but at random (a wrong name or month), never bent by a motive.
- Posters come from off shows, open nights and festivals. Chatter at the Anchor comes from off local events, as often as in the on arm, retold plainly and wrong only at random.
- The corner's houses A to E keep their kind, era and age, and nothing else: even wear, paint some years old, one set of matching windows. A is a jugend house with a plain café below and no sign of an earlier shop. B is a kept functionalist house, C a chalet house, D a lived-in fisherman's house, E the oldest and smallest. Nothing is boarded or neglected. A house with no household cast in it is shut and kept.
- The town's places are working places of a plausible age, with no plaques, dated signs, photographs of past events or memorials. A grave shows a name and dates.
- Over the time jump, houses weather a little and may get a seeded repaint. Nothing changes because of anyone; the corner's shops stay as they were in 1989.

Nothing on screen points to a person or a past. There are no ghost signs, no repairs that tell a story, no boarded house with a reason, no worn path to a door and no flowers on a grave.

## What must not leak

Off-arm game masters read the off file, this page, `engine-rules.md` and only the cast tables of `atlas-9989.md` (people, households, places, who lives in A to E). Never its storylines, events or records, `records-9989.md`, `lives-a.md`, `lives-b.md` or `docs/ideas/stories-in-the-world.md`. None of this reaches a screen:

- any cause, reason, decision tag or "Noticed:" read from the real file;
- any real chain, such as the skipper's job between John Holmes and Ivan Tanner, Jonah Scott's confidence passed on, why Greta Brook was let go, Terry Sutton's expense claims, or Maisie and Harry Myers's rows and her leaving;
- grief: drinking after a death, visits, the hat at the Anchor, "never made things right";
- illness before a death, or any cause of death;
- debts, loans, promises, money troubles;
- feuds, grudges, rivalries, people keeping away, a quarrel that carries;
- secrets, skimming, being found out, blame, gossip;
- wants won "after years", plans to leave, the job in the city before someone goes;
- the real band's story: songs claimed as someone else's, the credit row, who praised whose song, why members left or Driftwood split, the real song titles;
- the real festival story: the same crew each year, who was late, why a night was a washout;
- the town's past: earlier cafés and festivals, the Sawmill Boys, how the Anchor opened, the 1986 crash, and every diary in the corner fixture (shops, the fire, windows, the boarding and the heirs, restorations).

## Three lives, 1989 to 1992

The engine's reasons are in brackets.

### John Holmes, sawmill foreman, in the Night Shift

- Real: passes on what Jonah Scott told him in confidence, and it gets back (1989). Goes cold on Ivan Tanner for weeks, the third time [passed over for skipper; still sore since 1977]. Lets Greta Brook go [her work poor for months; he dislikes her] (1990). Ellie Holmes dies of a heart attack (1992); he drinks more than is good for him, friends come round weekly, the hat goes round for him.
- Off: Sid Tanner shows him how to make pancakes (1989). Argues in the street with Una Waller, then Harry Myers; moans with Greta Brook about the week at the sawmill, lets her go, waves to her across the harbour (1990). Ellie Holmes dies, aged 76 (1992). Next month he spends a day in the city, then wins a little on the pools.

### Maisie Myers, teacher, then at the sawmill and the council office, married to Harry Myers

- Real: drags up what Gary Myers did, in front of the school, and looks for work [wants to be headteacher]; leaves for the sawmill (1989). Tells Harry how bad things are; he tells people. The same row about how little time he gives the family, for four years; each autumn he gives it another go. Doesn't pay Eve Vaughan back (1990). Moves to the council office [wanted more] (1992).
- Off: off sick for a week, falls out with Harry, moves to the sawmill (1989). Wins the Anchor's raffle (1990). Runs the harbour day, which goes smoothly (1991). Harry helps her move a wardrobe; she moves to the council office (1992).

### Terry Sutton, chief officer at the council office, married to Mona Sayer, runs the summer festival

- Real: the same friends count themselves in for the festival, as always (1989). He and Mona have stopped talking about anything that matters. The festival is the best night in years. He takes from the expense claims and is found out (1990); Lily Lyons drags it up, and later they become friends (1991). Retires after 34 years, and starts trying to put things right with John Holmes (1992).
- Off: six people say yes to the festival, none of them the real crew (1989). Cuts Mona's hair in the kitchen. A shouting match with Jonah Scott. The festival is a washout. An operation in the city, home within the week (1990). The next festival is a fine night; he wins the Anchor's raffle (1991). Retires and buys a new coat (1992).
