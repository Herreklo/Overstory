# GM notes: X1, Football Manager (paper)

Calibration run. Player kind: Football Manager devotee. Twin run: Y1 (same opening, same dice; outcomes may differ only through choices). Render FM at its best and no better: the inbox, assistant's advice, ranged scouting, morale arrows, text-commentary highlights, a stats panel, ratings, the table. Never reveal the hidden values below except through what the game would show.

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
- R0: player spawned (sonnet, general-purpose), agent a1c93ffb386eeb490. r1-act.md written; pull 7. Three turns: scout, Reid physio test, Ainsley promise. Training and press not taken as turns.
- R1 t1 CARD (plan "Asking the scout for more"): Voss heading 15–17; Platt pace 8–10, knock confirmed; "keeper flaps at crosses"; "they played Tuesday". GM-SIMULATED: knowledge 45→70% (one match watched, Tuesday's cup tie); "three games in eight days" is arithmetic from the fixture dates.
- R1 t2 CARD (plan "Reid"): physio test "Fitness 86%. Risk of aggravation: High." "Fine next Saturday if rested" from the plan's "If rested: back for the following Saturday". Rolls 1–2 not drawn yet (only if he plays).
- R1 t3 CARD (plan "Ainsley", promise talks): morale Poor→Okay. Wage room £300/wk shown. Roll 3 not drawn (only if talks are held).
- R1 no turn, training: GM-SIMULATED (FM default: assistant runs a general schedule, Medium): no focus modifier; roll 4 not drawn (knock roll only at High).
- R1 no turn, press: GM-SIMULATED (FM default: assistant attends, calm answer): plan "Calm or deflect: no effect".
- R1 GM-SIMULATED texture: assistant's name (Neil Hosken), Halsey's other eight starters' names, next fixture (Linton Rangers away, 31 Oct, no midweek), matchday weather and conditions (recovered over a Medium week). Mensah's loan playing time shown as FM shows it (plan: Kingsbridge expect him to start).
- R1 assistant's pre-match report: each line from a scouted or shown fact (Platt, Voss, Ince, high line, Garvey as captain and hub, Tuesday's game); nothing on Reid beyond the physio.
- State after R1: Ainsley Okay (S_w ±0); training no modifiers; press no effect; Reid 86% High, undecided. Dice: next unused match roll is roll 5 (82).
- R1 screen sent (958 words). Waiting for r2-act.md.
- R1→R2: r2-act.md written. Marks: 1.1 engaged (delight), 1.2 confused, 1.3 engaged. Pull 8.
- R2 t1 CARD: Fenwick starts (Q_w +3, S_w −3); Reid left out, rolls 1–2 never drawn. SETUP inconsistency: r0 says nine on the bench but the squad is 18, so only six could be named; stated on r2 in one line.
- R2 t2 CARD: crossing focus with Fenwick, Q_w +3 more. GM-SIMULATED: "focus down the right" and "line slightly deeper" have no modifier in the plan; none applied.
- R2 t3 CARD: tight-mark Voss with Adeyemi Q_h −5; close down Garvey S_h −3.
- R2 t4 CARD (team talks): calm "No pressure today" at home as underdog against the 4th-placed side, morale Okay to Superb: judged fitting as FM would, S_w +3 for blocks 1–3. Brandt "I have faith": motivated (no extra modifier in the plan).
- R2 thresholds, blocks 1–3: S_w 45 (45 −3 +3), Q_w 36 (30 +3 +3), S_h 47 (50 −3), Q_h 28 (33 −5). Training none, Ainsley Okay none, Balanced none.
- R2 B1 GM-SIMULATED match model: roll 5 = 82 vs S_w 45, no chance; roll 6 = 53 vs S_h 47, near thing (11', Voss flick-on, Pryce gathers).
- R2 B2: roll 7 = 15 ≤ 45, Wexborough chance; roll 8 = 82 vs Q_w 36, miss, not near (19', Fenwick header well over from Brandt's cross). Roll 9 = 2 ≤ 47, Halsey chance; roll 10 = 83 vs Q_h 28, miss (27', Ambrose wide). Roll 9 is 2, not 1: no card.
- R2 B3: roll 11 = 94, no chance; roll 12 = 51 vs 47, near thing (40', Cutts low shot, Pryce holds).
- R2 half-time 0–0. GM-SIMULATED texture: crowd 3,912, Mensah's long-range shot (34', no roll), stats, ratings, condition (Halsey lower: the plan's Tuesday cup tie and fade, shown as FM's opposition panel would), Voss's and Platt's feet, Ainsley's wage £950 (plan).
- R2 Halsey changes at half-time: none (no rule; no drama added). Shown on r3.
- State after R2: 0–0 at HT. Talk bonus expires after block 3. Next unused roll is roll 13 (66).
- R2 screen sent (753 words). Waiting for r3-act.md.
- R2→R3: r3-act.md written. Marks: 2.1–2.3 engaged (2.3 delight), 2.4 curious. Pull 8.
- R3 t1 CARD (team talks): assertive "Go out and win it" at 0–0 at home, morale Okay to Superb, after a fitting first half: judged fitting as FM would, S_w +3 for blocks 4–6. Individual praise to Adeyemi (7.1) and Kerr (7.0): fitting, no extra modifier.
- R3 t2 GM-SIMULATED: Mensah's dribble-more instruction has no modifier in the plan; narrative only.
- R3 t3 CARD: Lowe on at 58' (Fenwick at 72%, the trigger not reached); from block 5, Lowe S_w +5, Q_w −2 replace Fenwick's S_w −3, Q_w +3 and the crossing Q_w +3 (tied to Fenwick in the plan). Fatigue, blocks 5–6: S_h −5; tempo up and fresh legs, S_w +5 (counted once).
- R3 t4 CARD: Moran for Kerr at 65', close-down kept (S_h −3). Positive-if-behind never triggered.
- R3 thresholds: B4 S_w 45, Q_w 36, S_h 47, Q_h 28. B5–B6 S_w 58 (45 +5 +3 +5), Q_w 28, S_h 42 (50 −3 −5), Q_h 28.
- R3 B4 GM-SIMULATED match model: roll 13 = 66 vs 45, none; roll 14 = 79 vs 47, none.
- R3 B5: roll 15 = 70 vs 58, near thing (seed 'calibration-anchor-X1-r3-b5-wnear-minute' randint(61,75) = 72: Lowe nearly in, Ince first). Roll 16 = 47 vs 42, near thing (seed '...-b5-hnear-minute' = 73: Whitlock header wide).
- R3 B6: roll 17 = 25 ≤ 58, Wexborough chance; roll 18 = 24 ≤ Q_w 28, GOAL (seed '...-b6-goal-minute' randint(76,90) = 79). Scorer Lowe, the obvious man (the chance from his pace behind the line). Assist tie (Ainsley, Mensah): roll 20 = 13, low = the obvious man, Ainsley (passing 14, vision 13). Roll 19 = 71 vs 42, no Halsey chance. No roll of 1 or 100 all match: no cards, no injuries. Rolls used: 5–20.
- R3 GM-SIMULATED texture: Halsey's subs (Pardoe 64', Ambrose 78'; no modifier, fatigue already in the model), 46' Mensah free kick, stats, ratings (POTM Adeyemi 7.5), board "pleased", confidence Okay ↑, supporters Very good ↑, Echo headline, post-match condition. Reid fit for Linton (plan: rested, back the following Saturday). Mensah started: no Kingsbridge letter. Ainsley's promise shown as due; roll 3 not drawn (talks not held in this session).
- R3 CARD: other results fixed; table recomputed (one-goal margins unless stated). Plan issue: the fixed results don't pair (9 wins, 6 losses, 7 draws), so they are shown per club, not as fixtures.
- Final: Wexborough 1–0 Halsey (Lowe 79'). Wexborough 15th → 13th, 17 pts.
- R3 screen sent (exit questions; 1,150 words). Waiting for exit.md.
- R3→exit: exit.md written from the r3 screen (pull 8; marks 3.1 curious, 3.2 engaged/delight, 3.3 delight, 3.4 engaged). Exit message sent; player replied done (memory file is the player's; not read).
- Game 1 closed. turns.md, needs.md, scores.md, condensed.md written.
