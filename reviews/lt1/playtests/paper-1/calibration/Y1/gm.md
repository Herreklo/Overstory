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
- R0: player spawned (agent ae4f3a78b40cd4b10, opus, persona 1). r1-act.md received: pull 7; three turns (rest Reid; Opposition LB, Medium; Ainsley promise talks); press skipped.
- R1 t1: CARD Reid rested: not in squad, back next Saturday. Rolls 1 (25) and 2 (58) not used (he doesn't play). Interface note: undecided, he'd have stayed selectable (GM-SIMULATED, interface default).
- R1 t2: CARD Training Opposition LB: S_w +5. Medium: no knock roll; roll 4 (70) not used.
- R1 t3: CARD Ainsley promise talks: morale Poor → Okay (modifier 0). Roll 3 (15) not used (no offer made). Contract £950 and wage room £300 shown as FM's contract/finance panels would; his ask (£1,400) not shown.
- R1 press: CARD not taken; assistant deflects = no effect.
- R1 texture GM-SIMULATED: assistant name Steve Rudd; Halsey's other seven names (Fairley, Ridley, Baptiste, Danby, Tierney, Whitlock, Pell); form letters (Wex L D W L D; Halsey WWWWW from 'five straight wins'); weather; conditions back to 97-100%; Echo headline. None touches the match model.
- R1 GM decision: line-up named freely (not a turn), up to three turns for talk/tactics/OIs, keeping r0's cap of three. Bench is six (17 fit).
- State after R1: S_w 50 (45 +5 training), S_h 50, Q_w 30, Q_h 33, before line-up, mentality, OIs and talk. Ainsley Okay. Reid out. Promise due 30 Nov. Next roll in list: roll 5 (82).
- Prediction logged (due FT): Voss scores/assists from a cross or set piece, beating Shaw; Halsey fade after ~60; our late chances down the right via Brandt and fresh Lowe.
- R1: r1-screen.md written; round message sent.
- R2 act received: pull 8. XI with Lowe up front, Fenwick on bench; Mensah starts (no letter); Ainsley starts.
- R2 line-up: CARD Lowe starts: S_w +5, Q_w −2. Fenwick not starting: no modifier.
- R2 t1: CARD tight-mark Voss with Adeyemi: Q_h −5.
- R2 t2: CARD focus down the right + Lowe Advanced Forward (run in behind): no modifier in the plan; allowed as one tactical turn (one visit to the tactics screen). Shapes commentary only.
- R2 t3: CARD + GM judgement: calm "I have faith in you" to a 19-year-old on his first start, morale Good = a fitting talk; S_w +3 for blocks 1-3. Reaction "Looks focused". Rest of squad no talk (neutral).
- R2 blocks 1-3 values: S_w 58 (45 +5 LB training +5 Lowe +3 talk), S_h 50, Q_w 28, Q_h 28.
- R2 b1: roll 5 (82) Wex no chance; roll 6 (53) Halsey no chance, near (≤65) → near thing; type GM-SIMULATED seed 'calib-Y1-r2-b1-halsey-near' d3=2 (save): Garvey long shot held by Pryce.
- R2 b2: roll 7 (15) Wex chance; roll 8 (82) vs Q_w 28 no goal, not near (wide). Source GM-SIMULATED seed 'calib-Y1-r2-b2-wex-source' d6=1 (Lowe in behind): Lowe drags it wide, 22'. Roll 9 (2) Halsey chance; roll 10 (83) vs Q_h 28 no goal, not near (over). Source seed 'calib-Y1-r2-b2-halsey-source' d4=3 (turnover in the press): Garvey wins it off Kerr, Pell over, 26'.
- R2 b3: roll 11 (94) Wex no chance, not near; roll 12 (51) Halsey no chance, near → near thing; type seed 'calib-Y1-r2-b3-halsey-near' d3=2 (save): Whitlock cross, Pryce punches clear of Voss and Adeyemi, 41'.
- R2 HT 0-0. Next roll: roll 13 (66). No roll was 1 or 100: no cards or injuries.
- R2 texture GM-SIMULATED: crowd 3,912; 4' Lowe run and 33' Brandt cross (non-chances; Platt's weakness is true); stats, xG, ratings; Rudd's HT note; interface answers (preparation scale of five, set-piece takers, zonal marking); Pell/Ridley/Baptiste unscouted.
- R2: r2-screen.md written; round message sent.
- R3 act received: pull 8. No half-time talk (neutral; pre-match +3 lapsed after block 3).
- R3 t1: CARD close down Garvey: S_h −3 from block 4.
- R3 t2: CARD Brandt low crosses/cut-backs: no modifier in the plan; commentary only (54' cut-back). Replaced at 60' by the planned change.
- R3 t3: CARD planned change triggered at 60' (level): Fenwick on for Gallagher (Fenwick's modifiers applied while on the pitch: Q_w +3, S_w −3, crossing focus Q_w +3; GM reading of "starts" as "plays", as for Reid); Lowe stays on (S_w +5, Q_w −2 kept); Positive S_w +5, S_h +3; fresh legs with Halsey fatigue in blocks 5-6: S_w +5, S_h −5.
- R3 b4 values: S_w 55, S_h 47, Q_w 28, Q_h 28. Roll 13 (66) Wex no chance, near (≤70): seed 'calib-Y1-r3-b4-wex-near' d3=1 woodwork, source d6=3 Brandt right: cut-back, Mensah off the post 54'. Roll 14 (79) Halsey no chance, not near. 0-0 at 60'.
- R3 b5 values: S_w 62, S_h 45, Q_w 34, Q_h 28. Roll 15 (70) Wex no chance, near (≤77): seed b5-wex-near d3=1 woodwork, source d6=2 Fenwick cross: header off the bar 66' (Ince comes and misses: his true weakness). Roll 16 (47) Halsey no chance, near (≤60): seed b5-halsey-near d3=3 block, source d4=2 Pell second ball: blocked by Shaw 72'.
- R3 b6 values as b5. Roll 17 (25) Wex chance; roll 18 (24) ≤34 GOAL. Scorer by position and attributes, no tie: crosses aimed at the Heading 15 target man, so Fenwick; assist Brandt (the crossing instruction). No tie roll used. Roll 19 (71) Halsey no chance, not near. Minute seed 'calib-Y1-r3-b6-goal-minute' 76-90 = 90'. FT 1-0. No roll was 1 or 100. Next unused roll: roll 20 (13).
- R3 GM-SIMULATED: Halsey subs seeded ('calib-Y1-r3-halsey-subs-count' d3=2; who sample: Tierney, Danby; minutes 68', 80'); sub names Kyle Mabbott, Dean Ashworth; conditions (Halsey lowest: Tuesday cup tie is true; Platt's knock shown as moving stiffly and 61%); stats, xG, ratings, POTM Brandt (highest rating); board/supporters reaction kept modest (no confidence change: plan gives none); Echo headline.
- R3 CARD other results and table: as fixed. PROBLEM noted: the fixed list is not internally consistent (10 wins, 7 losses, 7 draws including ours); shown per club without pairings, as given.
- R3: r3-screen.md written with exit questions; round and exit messages sent together.
- Exit received (exit.md): overall pull 7. Would play next week, not a whole season at this pace. Best: scouting ranges, the Ainsley promise as a dated object, the conditional change at 60', the default stated. Worst: team talks a black box; "too obliging", every instruction got its confirming highlight; thin depth (attributes, results without scores). R3 marks: engaged, engaged (delight), engaged (cheat, in his favour: the 90' winner after two woodwork hits read as scripted).
- GM note on the "cheat" mark: the goal and both woodwork hits came from the list rolls in strict order (rolls 15, 17, 18; near things by rule), the minute from seed 'calib-Y1-r3-b6-goal-minute' (90). Each confirming highlight was chosen by GM-seeded source rolls or by the player's own instruction for that block; the flattery the player names is partly real: the paper model gives no instruction without its matching commentary. Logged for the analysts.
- Exit and memory message sent with the r3 round message. Game 1 done.
