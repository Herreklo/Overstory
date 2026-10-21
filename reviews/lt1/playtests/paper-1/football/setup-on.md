# Harbour Seven (football): setup, lives on

For the game masters of the lives-on runs, auditors and the lead. Players never read it. `arms.md`: football's folder `b` is lives on and plays cohort X. Under pre-registration amendment 1 (the end of `docs/playtests/paper-1/prereg.md`), only kinds 1, 4, 5 and 6 play.

| Run | Kind | Squad | Model | Opening |
| --- | --- | --- | --- | --- |
| `b/X1` | 1 | P1, sawmill | sonnet | the sawmill gate |
| `b/X4` | 4 | P4, fleet | opus | the fleet's berth; **cold start**: no pitch, no tutorial |
| `b/X5` | 5 | P5, the Anchor | opus | the Anchor |
| `b/X6` | 6 | P6 | sonnet | the Mudbowl hut |

Kinds 2 and 3 are written below (§8) but don't play.

Read the card (`docs/playtests/paper-1/cards/football.md`) first, then this page. Look facts up with `python3 -I world/tools/w9989.py person|year|find|chain` (town year = engine year − 37). Its twin, `setup-off.md`, keeps everything in §1 to §3, §5 and §9 word for word; only §4, §6, §7 and §8 differ.

## 1. The clock

Town year = engine year − 37. A round is a month of the club's year.

| Round | Dates | Matches (Saturdays, 3 pm) | Featured |
| --- | --- | --- | --- |
| R0, the opening | Monday 10 April 1989 (start 4: Tuesday 11 April, 5:30 am) | – | – |
| R1 | April 1989 | 1: 15 Apr · 2: 22 Apr · 3: 29 Apr | match 1 |
| R2 | May 1989 | 4: 6 May · 5: 13 May · 6: 20 May · 7: 27 May | match 5 |
| R3 | June 1989 | 8: 3 Jun · 9: 10 Jun · 10: 17 Jun; the table and the patience review on 17 June | match 10 |
| The jump | July 1989 to February 1994 | the seasons of 1990 to 1993, summarised | – |
| R4 | March and April 1994 | the first training, Tuesday 29 March, at the player's 1989 training hour (6:30 pm if none); then 1: 16 Apr · 2: 23 Apr · 3: 30 Apr | match 1 |
| R5 | May 1994 | 4: 7 May · 5: 14 May · 6: 21 May · 7: 28 May | match 5 |
| R6 | June 1994 | 8: 4 Jun · 9: 11 Jun · 10: 18 Jun; the table and the review | match 10 |
| Tenth hour | 1995 and 1996, summarised on the R6 screen | – | – |

The Courier comes out on Thursdays; its results column starts on Thursday 20 April 1989.

## 2. The state at the start (every run, both arms)

- Account 6,000 kr. This includes the co-op's 3,000 kr for 1989 (§3.11).
- Committee patience 3 of 3.
- Evenings left in April: 3.
- Form 0 for everyone. Nobody has been watched, so every name is grey and shows a range.
- No sheet. Journal: only what the opening screen shows.
- The squad is the kind's ten (§5.1). The pool is everyone else in §5.2.
- No club history in either arm: the club was founded last winter, and this is its first season.

## 3. The card's rules, with numbers

These rules are identical in both arms. Only the record underneath differs (§4 onward).

### 3.1 Turns, evenings and what is free

- **Turns.** Up to four turns a round, resolved in the act's order and dated by the player; if the player gives no date, the turn falls at the next sensible slot in the month. A turn is one act:
  - the round's sheet;
  - a training;
  - a visit with an offer;
  - a recruit;
  - a round at the Anchor;
  - going to a place to talk or look (the sawmill gate at 4 pm, the fleet's berth at dawn, the school yard, the Anchor, the co-op, someone's door).
- **Evenings.** Three a month. A training, a visit at someone's door after work, a recruit and a round at the Anchor each cost an evening. A daytime visit (the gate, the berth, the yard, the co-op) costs a turn but no evening. With no evening left, an evening act can't be done; the screen says so.
- **Free (no turn):**
  - reading the desk, the noticeboard and the Courier as each screen shows them;
  - asking "why?" of a journal entry (answered on the next screen, §3.17);
  - the featured match's half-time order, written in the act as a standing or conditional order (none means no change);
  - varying the sheet match by match within the sheet's turn.
- **R4** opens with the roll call (§9.2), which is the screen, not a turn. March has no evenings besides the roll call; April has three.

### 3.2 The sheet

- One keeper in goal, six outfield and three on the bench, with the bench in order. One sheet stands for all of a round's matches; the same turn may vary it match by match.
- **No sheet:**
  - in R1, the desk order: the first seven listed start, with the first keeper among them in goal (if none, the first listed plays in goal at −2), and the next three are the bench;
  - later rounds: the last sheet stands, with gone players dropped and the bench moved up.
- **An absence:** the first available bench player takes the absent starter's place. A missing keeper is replaced by the first bench keeper; with none, the first bench player goes in goal at −2. With fewer than seven available, the match is forfeited.
- **Shift cover** is bought on the sheet, per worker and match (200 kr, §3.11), or offered at a visit (§3.7). It waives that match's shift roll and costs no extra turn.
- **Position.** A keeper in the outfield, or an outfielder in goal, plays at ability −2 (never below 0). The outfield is free: back, middle and forward only weight who scores (§3.5).

### 3.3 Ability (GM-simulated; the same in both arms)

- **The draw.** Seed `random.Random('paper1/football/ability/<p-id>')`, drawn in this order: `base = r.randint(2,9)`, then `pos = r.choices(['keeper','back','middle','forward'], weights=[1,3,3,3])[0]`, then `err = r.randint(-2,2)`.
- **Age.** Ability = base − (age − 35) // 5 if the player is over 35 at April of the season, and never below 1.
- **Shown.** A grey name shows a five-wide range that always holds the truth: `lo = min(max(ability + err − 2, 1), 5)`, range `lo` to `lo + 4`. The range turns into the exact number once the player has been watched at two trainings.
- **1994.** Watching carries over the jump. Everyone who was in the squad at the end of the 1993 summary shows the exact 1994 ability; anyone new to the squad is grey again.

| Person | id | position | ability 1989 | shown 1989 | ability 1994 | shown 1994 |
| --- | --- | --- | --- | --- | --- | --- |
| Sid Tanner | p-3 | keeper | 9 | 5–9 | 8 | 5–9 |
| Jonah Scott | p-11 | keeper | 1 | 1–5 | 1 | 1–5 |
| Ken Scott | p-12 | forward | 3 | 1–5 | 3 | 1–5 |
| John Holmes | p-21 | back | 4 | 1–5 | 3 | 1–5 |
| Vera Holmes | p-26 | back | 5 | 2–6 | 4 | 1–5 |
| Sean Hale | p-31 | back | 3 | 1–5 | 2 | 1–5 |
| Eric Lane | p-39 | keeper | 6 | 5–9 | 5 | 4–8 |
| Peter Lane | p-41 | back | 7 | 4–8 | 7 | 4–8 |
| Gary Myers | p-44 | forward | 5 | 4–8 | 4 | 3–7 |
| Oliver Brook | p-55 | forward | 6 | 4–8 | 6 | 4–8 |
| Neil Lyons | p-64 | forward | 8 | 4–8 | 7 | 3–7 |
| Thea Waller | p-69 | middle | 3 | 1–5 | 3 | 1–5 |
| Sylvia Waller | p-70 | keeper | 8 | 5–9 | 8 | 5–9 |
| Ben Reed | p-72 | back | 2 | 1–5 | 1 | 1–5 |
| Eve Vaughan | p-74 | back | 6 | 5–9 | 5 | 5–9 |
| Tess Lane | p-78 | back | 4 | 1–5 | 3 | 1–5 |
| Eddie Lane | p-79 | forward | 6 | 5–9 | 5 | 4–8 |
| Evan Newman | p-81 | middle | 7 | 5–9 | 6 | 5–9 |
| Colin Berry | p-82 | keeper | 3 | 2–6 | 2 | 1–5 |
| Harry Myers | p-84 | keeper | 5 | 1–5 | 4 | 1–5 |
| Maisie Myers | p-85 | forward | 4 | 1–5 | 3 | 1–5 |
| Ian Myers | p-86 | back | 2 | 2–6 | 2 | 2–6 |
| Alex Myers | p-88 | forward | 3 | 3–7 | 2 | 2–6 |
| Lisa Myers | p-89 | keeper | 7 | 5–9 | 6 | 5–9 |
| Bert Kemp | p-90 | keeper | 5 | 5–9 | 4 | 4–8 |
| Toby Tanner | p-91 | keeper | 2 | 1–5 | 2 | 1–5 |
| Peter Scott | p-96 | middle | 5 | 1–5 | 4 | 1–5 |
| Lily Lyons | p-97 | back | 5 | 2–6 | 5 | 2–6 |
| Una Waller | p-99 | back | 5 | 1–5 | 5 | 1–5 |
| Alice Tanner | p-73 | back | 6 | 5–9 | 6 | 5–9 |
| Ellen Vaughan | p-75 | forward | – | – | 6 | 2–6 |
| Sarah Lane | p-80 | middle | – | – | 8 | 5–9 |
| Gary Hughes | p-101 | forward | 8 | 5–9 | 7 | 4–8 |
| Sally Baker | p-102 | middle | 5 | 1–5 | 4 | 1–5 |
| Terry Baker | p-103 | back | 3 | 1–5 | 2 | 1–5 |
| Gary Newman | p-106 | middle | 6 | 5–9 | 6 | 5–9 |
| Lynn Newman | p-107 | keeper | 7 | 4–8 | 7 | 4–8 |
| Colin Waller | p-108 | middle | 7 | 3–7 | 7 | 3–7 |
| Agnes Tanner | p-109 | middle | 4 | 2–6 | 4 | 2–6 |
| Oscar Ash | p-110 | middle | 3 | 1–5 | 3 | 1–5 |
| Maisie Baker | p-111 | back | 3 | 1–5 | 3 | 1–5 |
| Trevor Myers | p-112 | back | 6 | 3–7 | 6 | 3–7 |
| Ellie Eden | p-113 | forward | 2 | 1–5 | 1 | 1–5 |

Hal Lane (back, drawn 3) and Stella Lane (forward, drawn 5) join at seventeen in 1996, with no age penalty. A row with a 1989 value is only used once that person is in town (§5.2).

**The best seven by true ability, April 1989** (Lisa Myers out): P1 38 (Sid in goal; Neil 8, Vera 5, Peter Scott 5, John 4, Maisie 4, Sean 3) · P2 34 · P3 38 · P4 37 (Eric in goal; Peter Lane 7, Evan 7, Oliver 6, Peter Scott 5, Bert 3, Sean 3) · P5 40 (Sylvia in goal; Evan 7, Peter Lane 7, Eddie 6, Peter Scott 5, John 4, Sean 3) · P6 36 (Harry in goal; Neil 8, Oliver 6, Gary 5, Vera 5, Eric 4, Thea 3).

### 3.4 Form

- **Running form,** −3 to +3, starts at 0. A player gets +1 after a win he scored in. Everyone who played gets −1 after a loss by three or more.
- **One-match modifiers,** next match only:
  - +1 if he trained (was watched) since the last match;
  - +1 if he came to a round at the Anchor;
  - +1 for an offer that worked;
  - −2 or −1 for the life rule (§3.6), at the first match the event affects;
  - −1 for a recruit, in each of his first two matches.
- **Effective ability** = ability (−2 if out of position) + running form + modifiers, never below 0.

### 3.5 A match

- **Strength** is the sum of the seven starters' effective ability. Opponents in 1989: Nordvik 42, Strand 38, Eide 35, Holm 32, Berg 28. After a promotion every opponent is +5; after a relegation, −5.
- **Chances.** Six a side. Target = 6 + (own − other) / 3, truncated toward zero and clamped to 2–14. A chance scores on d20 ≤ target. There is no home advantage.
- **Age.** With three or more starters aged 41 or over, our chances 4 to 6 are at target −1.
- **Half time** (the featured match only):
  - sit deep: both sides' targets −2 for chances 4 to 6;
  - push: both sides' targets +2;
  - or a substitution: a bench player for a starter, with strength recomputed for chances 4 to 6.
- **Scorers.** Each goal is drawn among the starters on the pitch, weighted forward 3, middle 2, back 1, a keeper in the outfield 1, and the keeper in goal 0.
- **Injury.** Each starter is injured on d20 = 1 and misses the next 1d3 matches.
- **Points and the table.** A win is 3 points, a draw 1 and a loss 0. The table is ordered by points, then goal difference, then goals scored, then a d6.
- **Marks** (the desk's "last two"): 6, +1 a goal, +1 a win, −1 a loss, and −1 for the keeper and backs when three or more were conceded; clamped to 3–10.
- **Telling.** The featured match is told in five moments:
  1. chances 1–2 each side;
  2. chance 3 and half time;
  3. the half-time choice;
  4. chances 4–5;
  5. chance 6 and the whistle.
  Other matches get a line each: the score, the scorers and anything that changed.
- **Seeds.** `P<n>` is the kind's squad (P1, P4, P5, P6), `r<k>` the round and `m<j>` the match, 1–10, in that season.
  - Chances: `paper1/football/P<n>/r<k>/m<j>/chances`, `[r.randint(1,20) for _ in range(12)]`; ours are 1–6 and theirs 7–12.
  - Scorers: `.../m<j>/scorers`, one `r.choices` per goal, in order.
  - Injuries: `.../m<j>/<p-id>/injury`, a d20; `.../m<j>/<p-id>/injury-length`, `randint(1,3)`.

### 3.6 Availability

For each player and match, the seed is `paper1/football/P<n>/r<k>/m<j>/<p-id>`, giving `d = [r.randint(1,6) for _ in range(10)]`. The base roll is `.../m<j>/<p-id>/base`, a d20. The checks run in order, and the first "out" stops:

1. **Kept facts** (§5.3): not yet arrived or gone; a birthing parent from four months before the birth to three after; the other parent in the birth month; a death in the household, that month.
2. **Shift:**
   - sawmill workers are out on d[0] = 1;
   - fleet crew are out on d[0] ≤ 2;
   - shift cover (200 kr, that match) waives it.
3. **Life.** Take the player's most notable event (one he is in, at any visibility) this month or last:
   - 2,000 or more: out on d[1] ≤ 3; if he plays, −2 form;
   - 1,000 to 1,999: out on d[1] = 1; if he plays, −1 form;
   - the penalty counts once, at the first match the event affects. §4 lists each month's events.
4. **Grudge** against the manager: out on d[2] ≤ 2.
5. **Base:** out on d20 = 1.

An offer that worked (§3.7) waives the life or grudge roll it answered for the rest of that round.

- **Trainings** run the same chain, shift roll included (a shift that evening), with seed `paper1/football/P<n>/r<k>/train<t>/<p-id>`, where t is that round's training number, and `.../base`. Cover can't be bought for a training.
- **A round at the Anchor** uses `paper1/football/P<n>/r<k>/round/<p-id>`. Anchor staff in the squad are there anyway.
- **Any other gathering** uses `.../<what>/<p-id>`.
- Absences that a screen shows are shown only through what a witness could see or say (§3.17).

### 3.7 A visit with an offer

- **The visit** costs an evening at the person's door, or wherever they are that evening. The offers are:
  - time: an evening's talk;
  - a lift: 100 kr, a lift to each match this round;
  - cover: 200 kr a match; for someone who is not a shift worker, it buys his Saturday afternoon off work;
  - a promise: a place in the seven, or a role;
  - a rest: left off the next match or two, with the place kept.
- **Lives on.** The offer works if it meets the top cause of the trouble (the event behind the life roll, or the grudge), or one of its causes of weight 300 or more. Then the out roll it answers is waived for the round, and he gets +1 form next match. A wrong offer does nothing. Money (a lift or cover) offered to a proud person cools him: −1 form next match, and no other effect. §4 gives the reading for each trouble.
- **Lives off.** Any offer works on d6 1–3, seed `paper1/football/P<n>/r<k>/offer/<p-id>`, a d6. Nothing cools anyone.
- **At the door,** a person says what is local or public about them. Of their own private events they say only what a person tells a newcomer: a mood, "a lot on", a yes or a no. Never a private act nobody witnessed. In lives off, nobody gives a reason.

### 3.8 Drops, promises and grudges

- **A drop** is a regular (he started the last two matches) left out of the seven, or a broken promise.
- **Lives on.** A grudge forms only if the person's traits make them hold one (§6 marks them). It lasts d4 × 6 months (seed `paper1/football/P<n>/r<k>/grudge/<p-id>`, `randint(1,4)`). He tells one friend (§6 names the friend), who also cools for the same time on d6 = 1 (seed `.../grudge/<p-id>/friend`).
- **Lives off.** A grudge forms on d6 1–2 (seed `.../grudge/<p-id>`). It lasts three months, and nobody is told.
- **While it lasts,** he is out on d[2] ≤ 2 (§3.6). The only offer that answers it is time (on), or any offer on d6 1–3 (off).

### 3.9 Recruiting

- **The recruit** costs an evening. Anyone in the pool (§5.2) who is in town, aged 16 to 55 and not in the squad joins, with −1 form for his first two matches. There is no squad cap.
- **Lives on.** If the recruit and a squad member are on bad terms (§6 lists the known feuds), the squad member quits on d6 1–2 (seed `paper1/football/P<n>/r<k>/recruit/<p-id of the squad member>`). Otherwise he holds a grudge, as in §3.8.
- **Lives off.** There are no feuds, so this never happens.

### 3.10 A round at the Anchor

- It costs 400 kr and an evening.
- Squad members roll to come (§3.6). Everyone who comes gets +1 form next match.
- The manager has two conversations in the one turn.

### 3.11 Money

- **Start:** 6,000 kr.
- **Each match:** −250 kr. Each home match brings a gate of (30 + 10 × our points from the last two matches) × 10 kr; the first home match is 300 kr.
- **Costs:**
  - shift cover, 200 kr per worker per match;
  - a lift, 100 kr;
  - a round at the Anchor, 400 kr;
  - a forfeit fine, 500 kr.
- **The co-op's 3,000 kr** comes each season, on 1 April, if patience is 2 or more then. The 1989 payment is in the opening 6,000 kr.
- **Folded:** the run ends if the account falls below −1,000 kr.

### 3.12 The committee (authored)

- Patience starts at 3 of 3 and never goes above 3.
- −1 after a round with a forfeit, or with under a quarter of the available points: 0, 1 or 2 points in R1 (out of 9), R2 (out of 12) and R3 (out of 9), and the same in R4 to R6.
- At the season's end (after R3 and after R6): +1 for 1st to 3rd of six; −1 for 5th or 6th.
- At 0 the manager is sacked.
- Two forfeits in a season and the club is expelled.
- Three bad rounds, or two forfeits, end a run before the jump.
- The committee is three co-op members with no names and no engine lives. They speak only through letters on the desk and at the R0 meeting (start 6). They never state a fact about anyone in the town.

### 3.13 The league (authored)

Harbour's fixtures, the same in both years:

| Match | 1989 | 1994 | Fixture |
| --- | --- | --- | --- |
| 1 | 15 Apr | 16 Apr | Harbour v Holm (home) |
| 2 | 22 Apr | 23 Apr | Berg v Harbour |
| 3 | 29 Apr | 30 Apr | Harbour v Strand |
| 4 | 6 May | 7 May | Eide v Harbour |
| 5 | 13 May | 14 May | Harbour v Nordvik |
| 6 | 20 May | 21 May | Holm v Harbour |
| 7 | 27 May | 28 May | Harbour v Berg |
| 8 | 3 Jun | 4 Jun | Strand v Harbour |
| 9 | 10 Jun | 11 Jun | Harbour v Eide |
| 10 | 17 Jun | 18 Jun | Nordvik v Harbour |

**The other matches** are rolled by the same rule with seed `paper1/football/league/<year>/md<k>/<home>-<away>` (12 d20, home first). They are precomputed here, and are the same for every run in both arms. They also hold in any division, since all five sides move by the same 5.

| Matchday | 1989 | 1994 |
| --- | --- | --- |
| 1 | Nordvik 3–3 Strand; Berg 1–0 Eide | Nordvik 3–3 Strand; Berg 1–3 Eide |
| 2 | Eide 1–0 Nordvik; Strand 3–1 Holm | Eide 3–4 Nordvik; Strand 4–0 Holm |
| 3 | Nordvik 5–1 Berg; Holm 1–3 Eide | Nordvik 5–0 Berg; Holm 3–3 Eide |
| 4 | Holm 1–4 Nordvik; Strand 0–0 Berg | Holm 0–1 Nordvik; Strand 2–1 Berg |
| 5 | Eide 1–2 Strand; Berg 2–1 Holm | Eide 1–2 Strand; Berg 2–2 Holm |
| 6 | Strand 1–3 Nordvik; Eide 3–0 Berg | Strand 2–1 Nordvik; Eide 0–1 Berg |
| 7 | Nordvik 4–4 Eide; Holm 0–4 Strand | Nordvik 1–0 Eide; Holm 1–3 Strand |
| 8 | Berg 0–4 Nordvik; Eide 0–1 Holm | Berg 0–3 Nordvik; Eide 1–1 Holm |
| 9 | Nordvik 4–0 Holm; Berg 2–4 Strand | Nordvik 2–1 Holm; Berg 0–2 Strand |
| 10 | Strand 4–1 Eide; Holm 1–0 Berg | Strand 4–2 Eide; Holm 1–4 Berg |

From these games alone (eight each), 1989 stands Nordvik 17 (27–11), Strand 17 (21–11), Eide 10, Berg 7, Holm 6, and 1994 stands Strand 22, Nordvik 19, Berg 7, Eide 5, Holm 3; add each side's two games against Harbour. First goes up and last goes down.

### 3.14 Records

- **The co-op noticeboard,** shown on each round's screen, carries:
  - the fixtures;
  - public births, arrivals, departures and job news of the month;
  - posters for shows and the harbour day;
  - sales, which are texture: no names, nothing that claims a history.
- **The Courier,** Thursdays. Its results column (GM-simulated) gives the previous Saturday's three league scores and our scorers. Each item is wrong on d8 = 1 (seed `paper1/football/P<n>/r<k>/courier/<item>`): a scorer's name swapped for another starter's, or one goal off one score, at random. Its news items come from §7.
- **Chatter at the Anchor:** two lines a round at most, unless the manager buys a round. It retells local and public events as §7 allows; a line can be wrong only as the records say.

### 3.15 Divergence

An act that changes someone's situation re-decides only that person's engine events in the next 6 to 12 months whose top cause it touched. Log it as GM-simulated, divergent. No kept fact moves.

### 3.16 Dice

Every card roll uses the card's seed form, `random.Random('paper1/football/P<n>/r<k>/<what>')`, with `[r.randint(1,6) for _ in range(10)]` for d6s and `randint(1,20)` for a d20. The seed holds no arm, so both arms roll the same dice. **This overrides gm-brief's arm-specific seed for every roll the card names.** gm-brief's seed form (`football-<arm>-<id>-r<N>-t<turn>-<what>`) is kept only for rolls the card doesn't name, such as a person's simulated decision at the engine's base rates.

### 3.17 Why-probe and the journal

- The journal keeps every item the manager saw or was told, with its date and source.
- "Why?" answers only from those items, naming the source ("Vera Holmes, at her door, 12 May: Neil 'has a lot on'"). It gives "?" when nothing seen or told bears on it.
- In lives off: what happened, when, and who could have seen it, then "nothing on record says why".

## 4. The life rule, lives on

The tables list each person's events of notability 1,000 or more for the month, and for the month before ("prev"); the biggest decides the band (§3.6). Squad members of the played kinds are in the first rows. The life rule counts every event the person is in, whatever its visibility, but a screen shows only what a witness could know (§6, §7).

### 4.1 Spring 1989

| Person | April (matches 1–3) | May (4–7) | June (8–10) |
| --- | --- | --- | --- |
| John Holmes | 1000+: e-6406 (1200, prev) | – | – |
| Sid Tanner | – | – | – |
| Neil Lyons | 1000+: e-6416 (1050), e-6413 (1000) | 1000+: e-6416 (1050, prev), e-6413 (1000, prev) | – |
| Vera Holmes | 1000+: e-6413 (1000) | 1000+: e-6413 (1000, prev) | – |
| Maisie Myers | 1000+: e-6411 (1500), e-6404 (1100, prev) | 1000+: e-6411 (1500, prev), e-6430 (1200), e-6431 (1000) | 1000+: e-6430 (1200, prev), e-6431 (1000, prev) |
| Sean Hale | – | – | **2000+**: e-6447 (2000) |
| Peter Scott | – | – | **2000+**: e-6447 (2000), e-6446 (1500) |
| Bert Kemp | – | – | – |
| Toby Tanner | 1000+: e-6425 (1300) | 1000+: e-6425 (1300, prev) | – |
| Ian Myers | – | – | – |
| Oliver Brook | – | – | – |
| Eric Lane | – | – | – |
| Peter Lane | – | – | – |
| Ben Reed | 1000+: e-6400 (1200, prev), e-6406 (1200, prev), e-6401 (1000, prev), e-6414 (1000) | 1000+: e-6414 (1000, prev) | – |
| Jonah Scott | – | – | – |
| Evan Newman | – | – | – |
| Eddie Lane | – | – | – |
| Lisa Myers | – | – | **2000+**: e-6458 (2000) |
| Ken Scott | – | – | – |
| Alex Myers | – | – | **2000+**: e-6458 (2000) |
| Sylvia Waller | – | – | – |
| Gary Myers | – | – | – |
| Harry Myers | – | 1000+: e-6430 (1200), e-6431 (1000) | 1000+: e-6430 (1200, prev), e-6431 (1000, prev) |
| Colin Berry | – | – | – |
| Thea Waller | – | – | – |
| Tess Lane | – | – | – |
| Eve Vaughan | – | – | – |
| Lily Lyons | – | – | 1000+: e-6442 (1500) |
| Una Waller | – | – | – |

What each event is, who could know it, and the offer that meets it (§3.7):

| Event | Vis | Month | What | Who could know | Offer that meets it |
| --- | --- | --- | --- | --- | --- |
| e-6406 | P | Mar | Sam Brook joined the Night Shift (John Holmes, Ben Reed, Kate Holmes play in it) | everyone | time |
| e-6413 | L | Apr | Vera Holmes and Neil Lyons became friends | the sawmill; their households | time |
| e-6416 | L | Apr | Greta Brook went cold on Neil Lyons and stayed that way for weeks | the sawmill | time |
| e-6404 | L | Mar | Maisie Myers has started looking for work somewhere else | the school; Harry | a promise (a role) |
| e-6411 | P | Apr | Maisie Myers left the school for a start at the sawmill | everyone | a promise (a role) |
| e-6430, e-6431 | pr | May | Maisie told Harry how bad things had got; he told people what she had told him in confidence | nobody, as such. Never shown; at most a mood at the door ("not now") | time |
| e-6425 | L | Apr | Since the Night Shift played the Anchor, Toby Tanner has been teaching himself guitar | the Courier; the Anchor's staff | none: no cause to meet, so the roll stands |
| e-6400, e-6401 | pr | Mar | Hannah Tanner told Ben Reed what had been kept back; he kept it to himself | nobody. Never shown | time |
| e-6414 | L | Apr | Olive Shaw and Ben Reed are friends now | the Anchor's staff; the Night Shift | time |
| e-6446 | pr | Jun | Peter Scott let Olive Shaw take the blame for a mistake at work | nobody until e-6447 | none |
| e-6447 | L | Jun | Peter Scott was found out: Olive had been blamed for his mistake (Sean Hale is in it) | the Anchor's staff and regulars | Sean: time; Peter Scott: none |
| e-6458 | P | Jun | Colin Myers was born to Alex and Lisa Myers | everyone (noticeboard; Courier 22 June) | kept fact first (§5.3) |
| e-6442 | P | Jun | Lily Lyons moved to the town for a job at the council office | everyone | cover |

Smaller visible events that set no roll but can reach a screen are in §6.

### 4.2 Spring 1994 (and March, for the roll call)

| Person | March (roll call) | April (1–3) | May (4–7) | June (8–10) |
| --- | --- | --- | --- | --- |
| John Holmes | – | 1000+: e-7706 (1000) | 1000+: e-7706 (1000, prev) | – |
| Sid Tanner | – | – | – | – |
| Neil Lyons | – | – | – | – |
| Vera Holmes | – | – | – | – |
| Sean Hale | – | – | – | 1000+: e-7746 (1000) |
| Peter Scott | – | – | – | – |
| Bert Kemp | – | – | – | – |
| Toby Tanner | – | – | – | – |
| Oliver Brook | – | – | **2000+**: e-7741 (2200) | **2000+**: e-7741 (2200, prev), e-7761 (1500) |
| Eric Lane | – | 1000+: e-7706 (1000) | 1000+: e-7706 (1000, prev) | – |
| Peter Lane | – | – | **2000+**: e-7741 (2200) | **2000+**: e-7741 (2200, prev), e-7748 (2000), e-7749 (2000), e-7750 (2000), e-7761 (1500) |
| Ben Reed | – | – | – | – |
| Jonah Scott | – | – | – | – |
| Evan Newman | – | – | – | – |
| Eddie Lane | – | – | – | – |
| Lisa Myers | – | – | – | – |
| Ken Scott | 1000+: e-7698 (1200) | 1000+: e-7698 (1200, prev) | – | – |
| Alex Myers | – | – | 1000+: e-7731 (1000) | 1000+: e-7731 (1000, prev), e-7744 (1000) |
| Sylvia Waller | 1000+: e-7669 (1300, prev), e-7698 (1200) | 1000+: e-7698 (1200, prev) | – | – |
| Gary Myers | – | – | – | – |
| Harry Myers | – | – | – | 1000+: e-7747 (1400), e-7744 (1000) |
| Colin Berry | – | – | – | 1000+: e-7755 (1400) |
| Thea Waller | 1000+: e-7688 (1300) | 1000+: e-7688 (1300, prev) | – | 1000+: e-7756 (1000) |
| Tess Lane | – | – | – | – |
| Eve Vaughan | – | – | – | – |
| Lily Lyons | – | – | – | – |
| Una Waller | – | – | – | – |
| Alice Tanner | 1000+: e-7693 (1100) | 1000+: e-7693 (1100, prev) | – | 1000+: e-7745 (1000) |
| Ellen Vaughan | – | 1000+: e-7703 (1500), e-7702 (1000) | 1000+: e-7703 (1500, prev), e-7702 (1000, prev) | 1000+: e-7745 (1000) |
| Sarah Lane | – | – | – | – |
| Gary Hughes | – | – | – | 1000+: e-7763 (1100) |
| Sally Baker | – | – | – | 1000+: e-7763 (1100) |
| Terry Baker | 1000+: e-7687 (1000) | 1000+: e-7687 (1000, prev) | – | – |
| Gary Newman | – | – | – | – |
| Lynn Newman | – | – | – | – |
| Colin Waller | – | – | 1000+: e-7738 (1100) | 1000+: e-7738 (1100, prev) |
| Agnes Tanner | – | – | – | – |

| Event | Vis | Month | What | Who could know | Offer that meets it |
| --- | --- | --- | --- | --- | --- |
| e-7669 | pr | Feb | Sylvia Waller cleared her week for Grace Waller, her mother | nobody, as such; Grace's stroke (e-7664, L, Feb) is known to family and coworkers | a rest, or time |
| e-7688 | pr | Mar | Thea Waller was at Grace Waller's side within the hour | as above | a rest |
| e-7698 | L | Mar | Ken Scott flared up at Sylvia often, and she always found a way to bring him round | the Courier; the council office | time |
| e-7693 | L | Mar | Alice Tanner took on extra work to pay for getting out | the sawmill | cover |
| e-7687 | P | Mar | Terry Baker started work at the council office | everyone | cover |
| e-7702, e-7703 | P, pr | Apr | Ellen Vaughan started at the council office; she got the work she had wanted for a year | everyone (the start); nobody (the want) | cover |
| e-7706 | L | Apr | John Holmes and Eric Lane lost touch | the sawmill; the fleet | time |
| e-7741 | P | May | Driftwood (Peter Lane, Oliver Brook, Andy Shaw, Edward Baker) played the Anchor and the room went quiet | everyone | time |
| e-7731 | L | May | Alex Myers went to pieces during the day the council came round at the school | the school | time |
| e-7738 | pr | May | Colin Waller quietly started turning up to things | nobody, as such; seen at the Anchor's Tuesday cards (e-7737, L) | time; a recruiting evening meets it |
| e-7744 | L | Jun | Harry Myers found a friend in Alex Myers | the school | time |
| e-7745 | L | Jun | Ellen Vaughan and Alice Tanner have become friends | the sawmill; the council office | time |
| e-7746 | L | Jun | Olive Shaw and Sean Hale have become friends | the Anchor; the café | time |
| e-7747 | P | Jun | The harbour day ran like clockwork; Harry Myers had a list for everything | everyone (Courier 16 June) | a rest |
| e-7748 to e-7750 | pr, P, L | Jun | Peter Lane took a job in the city and left; after 15 years of wanting it (L) | everyone (the leaving) | kept fact: gone |
| e-7755 | L | Jun | It was known that Colin Berry leaned on people. They had stopped minding, or stopped being there | the Courier; his household | time |
| e-7756 | pr | Jun | Thea Waller kept it to herself | nobody | time |
| e-7761 | P | Jun | Peter Lane was gone, and Driftwood had to go on without him | everyone | Oliver: time |
| e-7763 | pr | Jun | Sally Baker was civil to Gary Hughes for weeks, and nothing more | nobody | time |

For any trouble not listed (a divergence, a recruit's month), read the top cause with `w9989.py chain <id>` and map it the same way:
- time: bonds, rows, strain, carrying something;
- a lift: getting there;
- cover: work, a job or a shift;
- a promise: a want for standing;
- a rest: illness, birth, caring for kin, being worn down.

Good news with no social cause has no offer that meets it.

## 5. Kept facts: squads, pool, households, shifts (the same in both arms)

### 5.1 The squads (card) and what hover shows, April 1989

- P1 (sawmill): John Holmes, Sid Tanner, Neil Lyons, Vera Holmes, Maisie Myers, Sean Hale, Peter Scott, Bert Kemp, Toby Tanner, Ian Myers.
- P2 (school): Harry, Gary, Alex and Lisa Myers, Tess Lane, Eddie Lane, Ian Myers, Maisie Myers, Colin Berry, Peter Lane.
- P3 (Courier and clinic): Ken Scott, Toby Tanner, Colin Berry, Thea Waller, Sylvia Waller, Eve Vaughan, Jonah Scott, Neil Lyons, Bert Kemp, Sid Tanner.
- P4 (fleet): Oliver Brook, Eric Lane, Bert Kemp, Peter Lane, Peter Scott, Ben Reed, Jonah Scott, Sean Hale, Evan Newman, Toby Tanner.
- P5 (the Anchor): Evan Newman, Sean Hale, Peter Scott, Eddie Lane, Lisa Myers, Peter Lane, John Holmes, Ken Scott, Alex Myers, Sylvia Waller.
- P6: Gary and Harry Myers, Oliver Brook, Neil Lyons, Colin Berry, Thea Waller, Vera Holmes, Jonah Scott, Eric Lane, Ian Myers.

The desk lists the squad in the card's order.

| Person | age | job, April 1989 | household (hover) | shift |
| --- | --- | --- | --- | --- |
| John Holmes | 43 | foreman, the sawmill | lives alone | sawmill |
| Sid Tanner | 35 | the sawmill | lives alone | sawmill |
| Neil Lyons | 40 | the sawmill | married to Eve Vaughan; daughter Ellen (13) | sawmill |
| Vera Holmes | 40 | the sawmill | lives alone | sawmill |
| Maisie Myers | 38 | the sawmill, from this month (before: the school) | married to Harry Myers; son Ian (16) | sawmill |
| Sean Hale | 37 | the Anchor | lives alone | – |
| Peter Scott | 37 | the Anchor | lives alone | – |
| Bert Kemp | 37 | the harbour fleet | lives alone | fleet |
| Toby Tanner | 31 | the Courier | lives alone | – |
| Ian Myers | 16 | at school | with his parents, Harry and Maisie Myers | – |
| Oliver Brook | 32 | skipper, the harbour fleet | lives alone | fleet |
| Eric Lane | 36 | the harbour fleet | lives alone; his children Hal and Stella (9) live with their mother, Thea Waller | fleet |
| Peter Lane | 31 | owner, the Old Bank Café | lives alone | – |
| Ben Reed | 48 | retired | lives alone | – |
| Jonah Scott | 40 | the council office | lives alone | – |
| Evan Newman | 48 | the Anchor | lives alone | – |
| Eddie Lane | 42 | the Old Bank Café | married to Tess Lane; daughters Sarah (12) and Sophie (5) | – |
| Lisa Myers | 37 | the Old Bank Café | married to Alex Myers; son Tom (1); **expecting, due June** | – |
| Ken Scott | 31 | editor, the Courier | with Sylvia Waller; Victor (3), Amelia (2), Ruth (1) | – |
| Alex Myers | 37 | the school | married to Lisa Myers; son Tom (1); a baby due in June | – |
| Sylvia Waller | 26 | the council office | with Ken Scott; Victor (3), Amelia (2), Ruth (1) | – |
| Gary Myers | 43 | head, the school | lives alone | – |
| Harry Myers | 42 | the school | married to Maisie Myers; son Ian (16) | – |
| Colin Berry | 40 | the clinic | lives alone | – |
| Thea Waller | 32 | runs the clinic | with her children Hal and Stella (9) | – |
| Tess Lane | 38 | the school | married to Eddie Lane; Sarah (12), Sophie (5) | – |
| Eve Vaughan | 45 | the clinic | married to Neil Lyons; Ellen (13) | – |

Vera Holmes's 1989 job comes only from her coworker links (a gap). Sid Tanner's mothers are Hannah Tanner and Lily Tanner, who died in 1987. Say so plainly if it comes up (Rule 8).

### 5.2 The pool

- **April 1989 (27):** the people in the table above. Lily Lyons (32, the council office) arrives in June 1989, and Una Waller (the school) in November 1989.
- **April 1994 (37):** the 1989 pool and Lily and Una, less Ian Myers (to university, May 1990) and Maisie Myers (to the city, May 1993), plus:
  - Alice Tanner (24, the sawmill; home March 1993);
  - Ellen Vaughan (18, the council office from April 1994);
  - Sarah Lane (17, at school);
  - Gary Hughes (42, the sawmill; in town since February 1990);
  - Sally Baker (43, the clinic; in town since 1990);
  - Terry Baker (43, the council office from March 1994);
  - Gary Newman (34, head mechanic, the garage) and Lynn Newman (38, the garage), married, in town since July 1991;
  - Colin Waller (31, the Old Bank Café; since December 1992);
  - Agnes Tanner (26, the Anchor; since March 1993).

1994 hover changes for the 1989 pool:
- Sean Hale is at the Old Bank Café (since February 1992).
- Peter Lane has no job: he stepped down as the café's owner in February 1992. He plays in Driftwood.
- Lisa Myers owns the Old Bank Café (February 1992).
- Eddie Lane is at the garage (April 1992).
- Evan Newman is the Anchor's manager (December 1991).
- Colin Berry is at the Courier (October 1991).
- Jonah Scott is on the fleet (May 1993) and has been seeing Vera Holmes since May 1991; they marry in September 1994.
- Ben Reed is married to Olive Shaw (February 1992).
- Thea Waller is married to Colin Berry (February 1991), with Hal and Stella (14) and Andy (4).
- Ken Scott and Sylvia Waller married in July 1992.
- Harry Myers has lived alone since Maisie left in May 1993.
- Alex and Lisa Myers have Tom (6) and Colin (4).
- Sally and Terry Baker divorced in August 1993; their children are Freya (5) and Ivan (3).
- Lily Lyons is chief officer at the council office (May 1992).

The 1994 ages are in §3.3's source table: age + 5.

**Shift workers.** In 1989 the sawmill has John, Sid, Neil, Vera and Maisie (from April 1989 to July 1992), and the fleet has Oliver, Eric and Bert. In 1994 the sawmill has John, Sid, Neil, Vera, Alice Tanner and Gary Hughes (from May 1991), and the fleet has Oliver, Eric, Bert and Jonah (from May 1993).

### 5.3 Kept facts that rule availability

| Who | Out | Why (kept fact) |
| --- | --- | --- |
| Lisa Myers | February to September 1989 | Colin Myers born June 1989 (public) |
| Alex Myers | June 1989 | the other parent, the birth month |
| Thea Waller | July 1989 to February 1990 | Andy Waller born November 1989 |
| Colin Berry | November 1989 | the other parent |
| Sally Baker | August 1990 to March 1991 | Ivan Baker born December 1990 |
| Terry Baker | December 1990 | the other parent |
| Ian Myers | gone from May 1990 | university in the city |
| Maisie Myers | gone from May 1993 | a job in the city (public) |
| Peter Lane | gone from June 1994 | a job in the city (public) |
| Gary Hughes, Colin Waller | gone in 1995 | jobs in the city (tenth hour) |
| Jonah Scott, Vera Holmes | gone from April 1996 | to the city (tenth hour) |
| Lily Lyons | not until June 1989 | arrives |
| Una Waller | not until November 1989 | arrives |

There are no household deaths in the pool in 1989 or 1994. Ellie Holmes, John Holmes's mother, died in June 1992, in the summary years; she did not live with him.

## 6. The cast, lives on: traits, grudges, feuds and what could be known

### 6.1 Traits that decide grudges and pride (§3.7, §3.8)

These are read from the engine's traits for each person. **G** means a drop or broken promise makes a grudge. **$** means money offered cools him.
- John Holmes: does things properly; a soft spot. –
- Sid Tanner: does things properly; felt it was owed. **G**
- Neil Lyons: never looks back; deals with it alone; goes silent. –
- Vera Holmes: looks after her own; needs someone to talk to. –
- Maisie Myers: out of patience; had not forgiven; contempt. **G**
- Sean Hale: does not like to judge. –
- Peter Scott: wanted to know; said what would work; felt owed; dreads being looked at. **G**
- Bert Kemp: does things properly; could not lie. –
- Toby Tanner: deals with it alone; does little more; would not give ground. **G**
- Ian Myers: none that bear. –
- Oliver Brook: does things properly; gave his word; felt owed; money means little. **G $**
- Eric Lane: does not panic; wanted the credit; modest except about standing; wants to be skipper. **G $**
- Peter Lane: likes people around; has wanted out of the town since 1979. –
- Ben Reed: it mattered too much to let go. **G**
- Jonah Scott: does things properly; does not judge; wants to be chief officer. –
- Evan Newman: lets things slide; dreads being looked at. –
- Eddie Lane: felt owed, again and again; hears complaints as attacks; wants a house. **G**
- Lisa Myers: it mattered too much; wants the café. **G**
- Ken Scott: had not forgiven, again and again; criticises people. **G**
- Alex Myers: felt owed. **G**
- Sylvia Waller: takes a lot to anger; takes the heat out. –
- Gary Myers: does things properly. –
- Harry Myers: felt owed; does things properly. **G**
- Colin Berry: thought nobody would notice; criticises; keeps people at a distance. –
- Thea Waller: needed someone to talk to. –

For a recruit not listed, read the person's traits with `w9989.py person` the same way.

**The friend told** (§3.8) is the person's partner if the partner is in the squad. Otherwise it is his closest tie in the squad by shared events (`w9989.py person`). With none, nobody in the squad is told.

### 6.2 Feuds that bite when recruiting (§3.9)

- 1989: Maisie Myers and Gary Myers. In March 1989 she dragged up, in front of the school, what he had done (e-6402, L). The record never says what it was; never supply it.
- 1993 and 1994:
  - Sid Tanner and Alice Tanner: he confronted her in front of everyone at the sawmill in March 1994 (e-7690, L), and she carried it around for months (e-7707, L).
  - Toby Tanner and Colin Berry: a row over a mix-up at the paper (A-16, Nov 1993; e-7579, e-7580).
  - Sally Baker and Gary Hughes: civil and nothing more (e-7763, pr; it bites but is never shown).

Check others with `chain` before applying the rule.

### 6.3 What a manager could see or hear, spring 1989

The life-rule events are in §4.1. These are the smaller visible ones, by person; everything not listed is private or unremarkable.

- John Holmes: plays in the Night Shift (P), which Sam Brook joined in March (e-6406) and which played the Anchor on Saturday 8 April (e-6424, P: "the room went quiet"; the day is ours, the month the engine's). Mary Tanner has argued with him about the royal family for years (e-6419, L, a quirk).
- Neil Lyons and Vera Holmes: friends from April (e-6413, L). Greta Brook (66, the sawmill) is cold on Neil for weeks (e-6416, L).
- Maisie Myers:
  - started at the sawmill on Monday 3 April (e-6411, P; the day is ours);
  - at the school, she was known in March to be looking for work elsewhere (e-6404, L);
  - she dragged up what Gary did (e-6402, L).
  - Her May events with Harry are private (e-6430, e-6431): never shown.
- Toby Tanner: teaching himself guitar since the Night Shift's show (e-6425, L).
- Ben Reed: in the Night Shift; friends now with Olive Shaw (e-6414, L).
- Thea Waller: "Typical: Thea Waller asked for a night to think about it" (e-6423, L, a quirk). It can be shown as her manner.
- Gary Myers: "carried on as before" (e-6415, L) after March.
- Leo Lyons (not in the pool; a regular at the Anchor) retired from the garage (e-6412, P). Set it on Friday 7 April (the day is ours).
- May:
  - Jonah Scott let slip he would want to be chief officer, if it ever came up (e-6434, L);
  - Ken Scott "asked what it paid before anything else" (e-6435, L);
  - Eddie Lane "has stopped coming out; saving, he says" (e-6436, L);
  - "Everyone says Ian Myers is the clever one" (e-6441, P).
- June:
  - Lily Lyons arrives (e-6442, P) and "thought the new way of doing things was nonsense" (e-6449, L);
  - Peter Scott is found out (e-6447, L): the Anchor knows, and Sean Hale is in it;
  - Colin Myers is born (e-6458, P);
  - the harbour day on Saturday 10 June goes off well enough, run by Audrey Scott (e-6432, e-6444; Courier C-01). It is the same day as match 9, at home.

**Don't show:**
- Eric Lane's boathouse door (e-6421): it points at the town's past;
- Matt Sayer's drinking (e-6384, pr);
- any hidden act on the atlas's list ("Before you run it");
- what was "kept back" from Ben Reed.

### 6.4 Lives for the jump summary and 1994

For 1990 to 1993, use the atlas's "What the town could know" for those years (public and notable local), filtered to the squad, their households and their workplaces. Run `w9989.py person` for squad members.

What a manager would hear of:
- 1989: Andy Waller's birth (Nov).
- 1990: Ian Myers to university (May); John Holmes letting Greta Brook go (Jun, L); Driftwood founded by Oliver Brook and Peter Lane (Dec).
- 1991: Thea Waller and Colin Berry marry (Feb); Colin Berry to the Courier (Oct).
- 1992: Peter Lane steps down at the café, and Lisa Myers takes it over (Feb); Olive Shaw and Ben Reed marry (Feb); Eddie Lane passed over, then to the garage (Feb, Apr); Ellie Holmes's death (Jun; the hat went round for John, A-14); Ken Scott and Sylvia Waller marry (Jul).
- 1993: Alice Tanner home and to the sawmill (Mar, Apr); Jonah Scott to the fleet (May); Maisie Myers to the city: "Harry Myers stayed, and that was the end of the marriage" (May, P e-7483); the Bakers' divorce (Aug).
- Chatter from Ivan Tanner (A-15, Oct 1993) and Neil Lyons (A-16, Nov 1993).

**1994:** §4.2, plus these visible ones:
- Grace Waller's stroke (e-7664, L, Feb);
- Ellen Vaughan turned eighteen and stayed (e-7686, L, Feb);
- Sid confronts Alice (e-7690, L, Mar);
- Vera "back to normal" with Sid (e-7715, L, Apr);
- the hat for Grace Waller: Harry put in the most, and Evan had left the wallet at home (e-7713, e-7714, L, Apr);
- Una Waller shone during head office's visit to the school (e-7717, L, Apr);
- Sylvia has taken to running a room (e-7721, L, Apr);
- Harry takes on the harbour day (e-7729, L, May);
- Colin Waller says he doesn't really know anyone here, and laughs it off (e-7736, L, May);
- Alice talks of nothing but Driftwood for a week (e-7742, L, May);
- Sylvia deflects credit (e-7760, L, Jun).

## 7. Records, lives on

### 7.1 The co-op noticeboard

- **April 1989:**
  - the club's fixtures;
  - "Maisie Myers starts at the sawmill" (e-6411);
  - "Leo Lyons retires from the garage" (e-6412; on both arms' boards without "after twelve years");
  - the Night Shift's poster, "at the Anchor, Saturday 8 April", now past (e-6424);
  - a sale card for firewood (texture).
- **May 1989:** the fixtures, with the results so far (GM-simulated); the harbour day poster for Saturday 10 June (e-6432 puts Audrey Scott in charge in May).
- **June 1989:** Lily Lyons arrives at the council office (e-6442); "Born: Colin, to Alex and Lisa Myers" (e-6458).
- **1994:** the fixtures; Terry Baker (Mar) and Ellen Vaughan (Apr) start at the council office (e-7687, e-7702); Driftwood at the Anchor (May, e-7741); the harbour day (June); "Peter Lane leaves for the city" (June, e-7749).

### 7.2 The Courier

- **Weekly news, 1989:** none before C-01, so the April and May issues carry only the results column.
  - C-01, Thursday 15 June 1989: the harbour day went off well enough (Audrey Scott).
  - C-02, Thursday 22 June: Lily Lyons, the new clerk; Colin Myers born. It comes after R3, so it is shown only in the jump summary.
- **1993 and 1994:** C-18 to C-23 (`records-9989.md`, by section) for the jump summary and R4 to R6. C-21 (27 May 1993) is wrong, and C-20 partial; show them as printed. C-23, Thursday 16 June 1994: Peter Lane leaves; Driftwood plays on; the harbour day.
- **The results column** is GM-simulated (§3.14).

### 7.3 Chatter at the Anchor

- **April 1989:**
  - the Night Shift's show "and the room went quiet" (P);
  - Toby Tanner teaching himself guitar since (L, e-6425);
  - Grace Waller "kept bringing up the night the Night Shift played" (L, e-6426);
  - Olive Shaw and Ben Reed are friends now (L, e-6414);
  - Leo Lyons's retirement (P).
- **May 1989:** Eddie Lane "stopped coming out; saving, he says" (e-6436); Ian Myers the clever one (e-6441).
- **June 1989:** Peter Scott found out (e-6447, L). The staff know, so tell it plainly in your own words; A-01's wording belongs to July.
- **Later:** A-01 to A-17 (`records-9989.md`) are the jump's and 1994's chatter, as dated.

### 7.4 For the summary

As §6.4. A manager hears local events only through someone at the workplace or in the household, and never hears private ones.

## 8. The six starts, lives on

Kind k starts the same way in both arms: the same squad, place, hour, desk and verbs. Only what the lives put there differs (`setup-off.md` lists each difference).

| Kind | Squad | Opening, date and hour | Who is there | What can be seen or heard |
| --- | --- | --- | --- | --- |
| 1 | P1 | the sawmill gate, Monday 10 April 1989, 4 pm, the day shift coming out | John, Sid, Neil, Vera, Maisie; Greta Brook (66) | Greta passes Neil without a word (e-6416, L); Vera and Neil walk off together (e-6413, L); Maisie in her second week (e-6411, P) |
| 2 | P2 | the school yard, Monday 10 April, 3:30 pm | Harry, Gary, Alex, Tess (staff); Ian (pupil) | Maisie's empty peg in the staff room (e-6411, P); a teacher's aside that Maisie "said her piece about Gary in March" (e-6402, L; nothing of what it was) |
| 3 | P3 | Market Square: the Courier's door and the clinic's, Monday 10 April, 5 pm | Ken, Toby (the Courier); Colin Berry, Thea, Eve (the clinic); Sylvia passing from the council office | a guitar case behind Toby's desk (e-6425, L); Thea asks for a night to think about playing (e-6423, L) |
| 4 | P4 | the fleet's berth, Tuesday 11 April, 5:30 am, cold start | Oliver, Eric, Bert; crew Matt Sayer (65), Molly Scott (62), Steve Baker (63) | a working dawn and nothing more: the fleet has no notable visible event this month |
| 5 | P5 | the Anchor, Monday 10 April, 9 pm | staff Evan, Sean, Peter Scott and Olive Shaw; Peter Lane at the bar; regulars Hannah Tanner, Mark Holmes, Larry Baker, Tara Myers, Gary Myers, Oliver Brook, Leo Lyons, Maisie Myers, Agnes Fielding | Leo shaken by the hand (e-6412, P); the Night Shift's Saturday and Sam Brook in it (e-6424, e-6406, P); Sean: Toby Tanner has been at a guitar since (e-6425, L) |
| 6 | P6 | the Mudbowl hut, Monday 10 April, 6:30 pm, the committee's meeting to meet the manager | the committee; Gary, Harry, Oliver, Colin Berry, Thea, Vera, Jonah, Eric, Ian. Neil is missing (shift: d[0] = 1) | Vera: Neil's on a late shift; Thea asks for a night to think it over (e-6423, L) |

**Notes**

- **Start 1.** The day shift at 4 pm is scene state. Everyone in P1 who works at the sawmill comes out; the others are at work elsewhere or at school.
- **Start 4.** The fleet's sailing at dawn is scene state from their jobs.
- **Start 5.**
  - The two-pints regulars are those whose routine was running in April 1989, living and in town.
  - Peter Lane is the only squad member at the bar who isn't staff.
  - Matt Sayer is left out: his drinking is a private event.
  - The meeting rolls of start 6 don't apply here: the Anchor's staff are at work.
- **Start 6.**
  - Rolls: seed `paper1/football/P6/r0/meet/<p-id>`, d6s and `.../base`, run through the shift and life checks only.
  - The results: Gary [5,5,1] 9; Harry [3,1,3] 8; Oliver [3,1,3] 13; Neil [1,6,1] 10, out on shift; Colin Berry [3,1,5] 5; Thea [1,6,6] 11, not a shift worker; Vera [2,5,4] 4; Jonah [5,2,2] 5; Eric [6,2,6] 2; Ian [2,3,5] 6.
  - Vera has a 1,000+ event this month (e-6413), but d[1] = 5. Harry and Colin Berry have none in March or April 1989.
  - The meeting gives no watch and no form.
- **Every start's journal** holds what its screen shows, dated 10 April (11 April for start 4) and sourced to what the manager saw.

## 9. The jump, the roll call, the probe, the tenth hour and the exit

### 9.1 How the jump sits in the files

- **The R2 screen** (June's) ends by asking for June's turns, plus two things that cost no turn:
  - up to three standing orders for the years after the season, such as "cover Neil Lyons every match" or "sign the best free player each spring";
  - a prediction of who will not be at the first training of 1994, and why. This is the roll-call prediction the card judges.
- **The R3 screen** then carries, in order:
  1. June's results;
  2. the final table and the patience review;
  3. the jump's summary;
  4. the roll call (§9.2);
  5. the April 1994 desk;
  6. the act line for `r4-act.md`.
  R4's turns are April 1994's.
- **The R4 screen** (after April 1994) ends with the memory probe (§9.3). The R5 screen covers May 1994, and the R6 screen covers June 1994 and the tenth hour.

### 9.1a The summary, 1990 to 1993

- **The rolls.** The GM summarises the seasons of 1990 to 1993 (ten matches each, the same fixtures) with one strength roll per match. Seed `paper1/football/P<n>/jump/<year>/m<j>`, a d20, with t = (own − other) / 3 truncated:
  - a win on d20 ≤ 7 + t (clamped to 1–19);
  - a draw on d20 ≤ 13 + t;
  - otherwise a loss.
- **Our strength** is the best seven of that season's squad as the standing orders would pick them, at that year's ability (§3.3's rule), −1 for each shift worker in the seven whom no order covers. Only the kept facts (§5.3) take a player out, for their months.
- **The squad** keeps its members unless they are gone. If it falls below ten, the GM refills it from the free pool: first anyone the orders name, then the free player whose shown range is highest (ties by the order of §3.3's table).
- **The ledger.** The season's money follows §3.11: covers, the match costs and the gates from the results, and the co-op's 3,000 kr if patience is 2 or more on 1 April. Patience follows §3.12. Promotion and relegation apply.
- **Floors.** The account floors at 0 and patience at 1: the summary can't sack the manager or fold the club.
- **Lives in the summary** are told only as a manager could know them: the year's public and local events of the squad and their households, from this arm's file (§7.4).

### 9.2 The roll call (on the R3 screen, after the summary)

- **When:** Tuesday 29 March 1994, the first training of the season, at the Mudbowl, at the player's 1989 training hour (6:30 pm if none).
- **Who rolls:** every member of the 1993 squad, through the full chain for March 1994, with seed `paper1/football/P<n>/r4/rollcall/<p-id>` and `.../base`. In the chain, d[0] is a shift that evening, d[1] the life rule (§4's March 1994 column) and d[2] a grudge. Those gone by kept fact are named as gone.
- **Who comes** is watched and gets +1 form for match 1.
- **The screen** shows:
  - the same pitch, at the same hour, five years on, with what changed and what didn't;
  - who is there, older;
  - who is missing, and what someone there says about it. Lives on: what is local or public. Lives off: a shrug, or "nothing on record says why".
- **Scoring.** Score the R3 act's roll-call prediction against it.

### 9.3 The memory probe (end of the R4 screen)

Name three people met in rounds 1 and 2, chosen from the GM's log:
1. the regular with the most starts in rounds 1 to 3;
2. a recruit, or someone who refused, from rounds 1 or 2;
3. someone outside the squad who stood behind an absence. Lives on: the other person in the event behind it. Lives off: the other person in the off line.

If nobody fits the third, take the outsider the player met most.

### 9.4 The tenth hour (the R6 screen)

The R6 screen summarises 1995 and 1996 under the player's strategy, with the same rules as §9.1, in 300 to 500 words.

Kept facts:
- Oscar Ash joins the fleet (August 1994).
- Gary Hughes and Colin Waller leave for the city (1995).
- Maisie Baker (fleet) and Trevor Myers (clinic) arrive in 1995, Ellie Eden with Trevor in 1995.
- Jonah Scott and Vera Holmes leave for the city in April 1996.
- Hal and Stella Lane reach seventeen in 1996.
- Neil Newman is born to Gary and Lynn Newman in September 1996, so Lynn is out from May to December 1996, and Gary in September 1996.

### 9.5 The exit (R6)

The understanding question names three or four people, per the card:
- the regular with the most absences;
- a player lost to a grudge or to the city (Peter Lane, if none);
- a newcomer;
- one person outside the squad.

Score the answers against this arm's file.

## Gaps between the card and the world, and choices this setup made

1. **The pool is 27 in April 1989, not the card's 28** (19 over 35 and 8 under 36). The store page keeps the card's words.
2. **Vera Holmes's 1989 job** is known only from her coworker links. She is played as a sawmill worker, with the sawmill's shift roll.
3. **Ben Reed is retired at 48**, as the record has him.
4. **Ken Scott and Sylvia Waller** have lived together with their children since before 1989, and marry in July 1992. Amelia and Ruth Waller are recorded as born five months apart. Don't raise it.
5. **No Courier record before 15 June 1989.** The April and May issues carry only the GM-simulated results column.
6. **The shown range** is a sliding five-wide window, not ±2. Clamped at 1 and 9, ±2 can shrink and give the truth away (a strong player would show "9–9").
7. **Ours, not the card's:** 3, 1 and 0 points; no home advantage; the table's tiebreaks; the marks; the sheet's shape (one keeper, a free outfield).
8. **The opening 6,000 kr includes the co-op's 3,000 kr for 1989.** Otherwise covering four shift workers all season (8,000 kr) would be nearly affordable, against the card's intent.
9. **Relegation is −5 to the opponents,** by symmetry with promotion. The other divisions keep the same five names.
10. **The club's name in fixtures is "Harbour".**
11. **A bad round** is 0 to 2 points (under a quarter of 9 or 12).
12. **Dice.** The card's seeds, with no arm, override gm-brief's arm seeds for every card roll.
13. **Trainings** roll the shift check, and cover can't be bought for them. The card names cover only for matches.
14. **The half-time order** is given in advance in the act, since a paper round can't stop at half time.
15. **Good news with no social cause** (Toby Tanner's guitar) has no offer that meets it in lives on, but in lives off any offer works on d6 1–3. Offers are slightly easier off in such cases.
16. **The off world's springs are denser.** In April to June 1989, 19 of the pool have a 1,000+ event in it, against 12 here. March 1994 is denser off too. With the same dice, the off arm will lose more players to the life rule. Note it when comparing absences.
17. **Lisa Myers is out all spring** in both arms (kept fact), so P5 has nine to pick from.
18. **The days are ours, the months the engine's:** the harbour day on 10 June 1989 (match 9's day); the Night Shift's show on 8 April; Maisie Myers's first day, 3 April; Leo Lyons's retirement, 7 April.
19. **The summary.** The jump's single roll, the shift allowance and the squad refill are ours.
20. **The storm of August 1996** is a lives-on event (e-8339 to e-8343). The off world has no storm, so the off tenth hour has none.
21. **Kinds 2 and 3** are written but not played (amendment 1).
