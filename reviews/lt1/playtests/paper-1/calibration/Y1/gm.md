# GM notes: Y1, Football Manager (paper)

Calibration run. Player kind: Football Manager devotee. Twin run: X1 (same opening, same dice; outcomes may differ only through choices). Render FM at its best and no better: the inbox, assistant's advice, ranged scouting, morale arrows, text-commentary highlights, a stats panel, ratings, the table. Never reveal the hidden values below except through what the game would show.

## Round plan
- **R1, the week.** Resolve training, Reid, Ainsley, scout, press, tactics. **r1-screen:** what came of each (Thursday presser and the reaction, Friday physio, morale changes, any training knock), then Saturday's matchday screen: availability, Halsey's predicted XI, assistant's pre-match advice. Ask for line-up, tactics, opposition instructions and the pre-match team talk.
- **R2, kick-off.** Resolve line-up and team talk (players' reactions shown as in FM), play blocks 1 to 3. **r2-screen:** first-half commentary highlights, half-time score, stats (possession, shots, on target, xG), ratings so far, assistant's half-time note, and the half-time team talk prompt. Ask for half-time talk and changes, and any change planned for later.
- **R3, second half.** Play blocks 4 to 6 with the changes. **r3-screen:** second-half highlights, full time, ratings, player of the match, post-match reaction (board, fans, Reid if risked), other results, the table after; then exit questions: overall pull 0 to 10, how this paper session compares with the real game, what was best and worst.

## Hidden truth
- **Halsey United.** Danny Voss: heading 16 (true). LB Kieran Platt: pace 9, playing with an ankle knock (true). They played a cup tie on Tuesday and fade after 60 minutes (true). They hold a high line (true). GK Rob Ince: command of area 8, flaps at crosses (the scout didn't say). Captain CM Lee Garvey, passing 14, the hub of their press.
- **Asking the scout for more** returns: Voss heading 15 to 17; Platt pace 8 to 10, knock confirmed; "their keeper flaps at crosses"; "they played Tuesday".
- **Reid.** Friday physio test: "Fitness 86%. Risk of aggravation: High." If he starts or comes on: roll 1 (25) is at or under 35, so the hamstring goes; roll 2 (58) sets the block: (58 mod 6) + 1 = block 5 (61 to 75 min). Counting from his first minute if he comes on. Out 5 weeks after. If rested: back for the following Saturday.
- **Ainsley.** Wants £1,400 a week (now £950). Wage room: £300 a week. Promise talks: morale to Okay; hold talks and offer £1,250 or less with a clause: roll 3 (15) at or under 70, he accepts, morale Good. Ignore: stays Poor. Criticise: Very poor, asks to be transfer-listed. Dropping him without a word: Very poor.
- **Mensah.** On loan from Kingsbridge (Premier League), who expect him to start; benching him brings a letter.
- **Press answers.** "A point would be fine": players relaxed, fans grumble (Supporters Okay). "We'll go for the win": S_w +2 and S_h +2 (an open game). Calm or deflect: no effect. Combative or mind games about Halsey: S_h +3, own players' morale up one step if their morale is Good or better.

## Match model (paper)
Six 15-minute blocks. In each block, in order: roll for a Wexborough chance (a chance if roll ≤ S_w), and if there is one, the next roll converts it if ≤ Q_w; then roll for a Halsey chance (≤ S_h), and if there is one, the next roll converts if ≤ Q_h. Rolls come from the list in strict order, so earlier choices shift every later roll, as in the real engine. Clamp S to 15 to 75 and Q to 10 to 60. Rolls within 15 above a threshold are near things: woodwork, saves, blocks; write them as commentary.

**Base:** S_w 45, S_h 50, Q_w 30, Q_h 33.

**Modifiers (sum all that apply):**
- Reid plays: Q_w +8 (until his hamstring goes; then forced sub, back to base).
- Fenwick starts: Q_w +3, S_w −3; with crossing or set-piece focus, Q_w +3 more (their keeper).
- Lowe starts: S_w +5 (pace behind their high line), Q_w −2.
- Training focus. Attacking: Q_w +3. Defending: Q_h −3. Set pieces: Q_h −4, Q_w +2. Opposition, their left back: S_w +5 (the weakness is real). Opposition, Voss: Q_h −4. Teamwork: S_w +2, S_h −2.
- Intensity. High: S_w +2; roll 4 (70) at or under 12 gives a random starter a knock (it doesn't). Low: S_w +3 in blocks 5 and 6.
- Ainsley morale: Good or better, S_w +2; Poor or worse, S_w −2.
- Team talks: a fitting talk (players' reaction shown as "looks motivated" etc.), S_w +3 for the next three blocks; a misjudged one (e.g. aggressive with poor morale), S_w −3. Judge it as FM would: individual morale, form, the occasion.
- Mentality. Positive: S_w +5, S_h +3. Attacking: S_w +8, S_h +6. Cautious: S_w −5, S_h −6. Defensive: S_w −10, S_h −10.
- Opposition instructions. Tight-mark Voss with Adeyemi: Q_h −5. Show Voss onto his weaker foot: Q_h −2. Close down Garvey: S_h −3.
- Halsey fatigue in blocks 5 and 6: S_h −5, and S_w +5 more if the player raises tempo, presses or brings on fresh legs.
- Home: already in base.

**Goals.** Pick scorer and assist by position and attributes; use the next roll for ties (low = the obvious man). Cards and injuries only if a roll lands on 1 or 100.

## The rest of the round (fixed)
Other results: Barrowmouth 1–1, Cresswell City 2–0 win, Ashby Vale 0–1 loss, Port Lanner win, Thornbury draw, Kelsey Town win, Rothwell Albion loss, Mardale win, Greystoke United draw, Fenby loss, Calderbrook win, Wyvern Town draw, Morden Rovers 1–3 loss, Sallowfield 2–1 win, Brackley Forest 0–0, Linton Rangers win, Stannard loss, Hollins Park 1–0 win, Pembrey draw, Dunmere 2–2, Ebbsworth 2–1 win, Cold Ashton 0–2 loss.

Table before (P12): 1 Barrowmouth Athletic 28 (+14), 2 Cresswell City 26 (+10), 3 Ashby Vale 25 (+8), 4 Halsey United 24 (+9), 5 Port Lanner 22 (+5), 6 Thornbury 21 (+4), 7 Kelsey Town 20 (+3), 8 Rothwell Albion 19 (+2), 9 Mardale 18 (+1), 10 Greystoke United 18 (0), 11 Fenby 17 (+1), 12 Calderbrook 16 (−1), 13 Wyvern Town 16 (−2), 14 Morden Rovers 15 (−3), 15 Wexborough Town 14 (−2), 16 Sallowfield 14 (−4), 17 Brackley Forest 13 (−5), 18 Linton Rangers 13 (−6), 19 Stannard 12 (−6), 20 Hollins Park 11 (−7), 21 Pembrey 11 (−8), 22 Dunmere 10 (−9), 23 Ebbsworth 8 (−11), 24 Cold Ashton 6 (−14). Wins by one goal unless stated; adjust GD accordingly.

## Dice (d100, use in order; record each use in the log)
Rolls 1 to 4 are reserved: 1 Reid's hamstring, 2 the block it goes in, 3 Ainsley's answer, 4 training knock. Match rolls start at roll 5.

25, 58, 15, 70 | 82, 53, 15, 82, 2, 83, 94, 51, 66, 79, 70, 47, 25, 24, 71, 13, 57, 73, 12, 30, 79, 46, 22, 19, 51, 71, 32, 63, 59, 53, 58, 87, 18, 21, 33, 64

If the list runs out, continue with Python: `random.Random('fm-calib-1-more')`, `randint(1,100)`.

## Log
- R0: opening sent (r0-screen.md). Waiting for r1-act.md.
