# GM notes: X3, Stardew Valley (paper)

Calibration run. Player kind: cozy player. Twin run: Y3 (same opening, same dice). Render Stardew at its best and no better: the clock and energy budget, small warm dialogue, gift reactions with hearts, the shipping tally at night, the pleasure of a full field and a tidy plan, a little surprise. Villagers talk briefly and in character; nothing grand happens on an ordinary day.

## Round plan
- **R1, 6 am to about noon.** **r1-screen:** what got done, the clock, energy, gold, inventory changes, anyone met, and the farm and town as they stand at midday.
- **R2, noon to about 6 pm.** **r2-screen:** the same, with the evening ahead.
- **R3, the evening.** **r3-screen:** the evening, bed, the shipping tally overnight, the next morning (rain; Jodi's letter; anything that grew), then exit questions: overall pull 0 to 10, how this paper session compares with the real game, what was best and worst.

## Time and energy (paper costs)
- Harvest the 35 ready crops: 30 min, no energy. Water all 52 tiles with one refill: 1 h 20, about 90 energy. Hoe and plant 15 tiles: 40 min, 30 energy.
- Walk farm to Pierre's or the square: 20 min. To Pam's trailer: 25. To Clint's: 25. To the beach: 30. To the mines: 25. To the forest and Marnie's: 20. Picking salmonberries on the way: +20 min, about 12 berries (each restores 25 energy, sells for 5g).
- Mines: about an hour per 5 floors, 30 energy; good luck today: extra geodes and a better chance at ladders. Fishing: about 3 fish an hour at level 1, 30 energy.
- Smelting: 5 copper ore and 1 coal make a bar in 30 min; the player has coal for 3 more bars (5 bars total, exactly Clint's price).
- Talking to someone: +20 friendship points a day (250 points a heart).

## Hidden facts
- **Tomorrow rains:** nothing needs watering on Spring 19. Upgrading the watering can today is the sound play: Clint keeps it two days, and the rain covers one of them. Copper can: 55 water.
- **Pam today:** in the trailer 8:30 am to noon; noon to 4:30 pm on the bench by the bus stop, grumbling about the broken bus; 4:30 pm to midnight at the Saloon.
- **Pam's gifts (birthday ×8):** parsnip LOVED (+80 ×8 = +640: two hearts become four and a half; she's moved: "Nobody's bothered with my birthday in years. And a parsnip, of all things. My favourite."). Leek, potato, daffodil, amethyst, horseradish: liked (+45 ×8 = +360). Salmonberry, kale: neutral (+20 ×8 = +160). Quartz: disliked (−20 ×8 = −160; "Is this... a rock?"). A second gift today: refused, one a day.
- **Demetrius** takes the daffodil at his house (Robin's, up the mountain), 90g and a little friendship; he's mildly awkward and pleased.
- **The Saloon tonight:** Gus pours and is kind; Emily serves, chatty about dreams and fabric; Shane slouches at the back, rude unless spoken to gently (birthday in two days; he loves beer, pizza, hot peppers and pepper poppers). Pam at the bar from 4:30; if given her loved gift earlier, she buys the player a drink. Willy drops in. Clint stares at Emily.
- **Spring Crops bundle** (parsnip, green bean, cauliflower, potato): reward 20 Speed-Gro. The bundle completes only when beans (Spring 20) and cauliflower (tomorrow) are in.
- **Giant cauliflower:** roll at the night tally; a roll of 1 makes one. (It won't with these dice unless the order shifts.)
- **Next morning mail:** Jodi asks for a cauliflower ("Kent's back and I want to make his favourite"), reward 350g, within 2 days. If the player has one, a lovely beat.
- **Prices (base):** parsnip 35g, potato 80g, cauliflower 175g, green bean 40g, kale 110g, strawberry 120g, daffodil 30g, leek 60g, horseradish 50g, salmonberry 5g, copper bar 60g. Silver ×1.25, gold ×1.5.
- **Quality at Farming 3, no fertiliser:** each harvested batch, roll one d100: 1 to 9 a quarter of the batch gold, 10 to 26 a quarter silver, otherwise all normal. (Simplified for paper.)
- **Planting now:** parsnips and potatoes finish before summer; kale finishes on Spring 24; green beans on Spring 28; strawberries on Spring 26, once. Cauliflower planted now won't finish.

## Dice (d100, use in order; record each use in the log)
64, 76, 40, 66, 60, 41, 18, 18, 23, 74, 51, 44, 47, 10, 19, 100, 51, 90, 89, 66, 84, 42, 35, 79, 10, 72, 69, 3, 88, 12
More: Python `random.Random('sdv-calib-1-more')`.

## Log
- R0: opening sent (r0-screen.md). Waiting for r1-act.md.
- R0, 21 Oct: player spawn refused by the harness (concurrent subagent limit of 20 reached; told not to retry). No player started; nothing resolved. Game master stopped and reported to the lead.
- R0, 21 Oct (fresh start): new game master; earlier attempt's line above left as is. Opening checked (r0-screen.md). Player spawned fresh (sonnet, general-purpose, persona 3).
- R1 received r1-act.md (3 turns; pull 7; prediction: Pam home, pleased with the leek, 2 to about 3 hearts).
- R1 T1 water 52 tiles, one refill: CARD (1 h 20, 90 energy). 6:00 to 7:20; energy 270 to 180; can 28/40 left.
- R1 T2 harvest 35: CARD (30 min, 0 energy). Quality: GM-SIMULATED (plan's d100 rule; dice list #1 = 64 parsnips, all normal; #2 = 76 potatoes, all normal). Kept 1 parsnip, 1 potato; shipped 14 parsnips (490g) + 19 potatoes (1,520g) = 2,010g, pays overnight.
- R1 T2 replant 17 tiles (12 parsnip, 5 strawberry) on soil still tilled from the harvest: GM-SIMULATED (Stardew: planting tilled soil costs no energy; 20 min). 7:50 to 8:10. The 35 freed tiles were never watered (ready crops needed none), so the new seeds sit dry; shown on screen as visible dry soil only. Unwatered today: they start growing with tomorrow's rain (parsnips Spring 23, strawberries Spring 27, a day later than if watered). 18 tilled tiles left empty.
- R1 T3 walk farm to Pam's: CARD (25 min), 8:10 to 8:35; salmonberries seen, not picked (not in the turn). Pam home (CARD: trailer 8:30 to noon). Leek: CARD liked, +45 x8 = +360; Pam 500 to 860 points (3 hearts, 110 toward a fourth). Gift only, no chat. 8:40.
- R1 prediction: right (home, pleased, 3 hearts and a little).
- R1 note: the round plan expects R1 to end about noon; the player's three turns end at 8:40 am. Screen shows 8:40 honestly; no time skipped.
- R1 map times from the trailer: GM-SIMULATED (consistent with the plan's farm times).
- R2 received r2-act.md (3 turns; pull 8; R1 marks all engaged; prediction: bundle takes parsnip and potato, 2 of 4, dusty room, reward promised).
- R2 T1 walk trailer to square picking salmonberries: CARD (+20 min, about 12) + GM-SIMULATED (trailer to square 5 min). 8:40 to 9:05. 12 salmonberries. Energy 180, not "low": none eaten.
- R2 T2 Pierre's, 18 parsnip seeds x 20g = 360g: CARD prices. 2,315 to 1,955g. 9:15. Not planted (no turn).
- R2 T3 board request taken (daffodil to Demetrius, 2 days, 90g): CARD. Bundle: parsnip and potato placed, 2 of 4; reward shown on the bundle (20 Speed-Gro): CARD. 9:30.
- R2 prediction: right.
- R2 note: the plan's R2 runs noon to 6 pm; the turns end at 9:30 am. Shown honestly.
- R2 texture (Pierre, Caroline, Lewis watering, the cat, the Junimo glimpse): GM-SIMULATED texture, true to the game, claims nothing.
- R3 received r3-act.md (3 turns; pull 8; R2 marks all engaged; prediction: Robin pleased, will build when materials come, sells wood/stone; Demetrius absent-minded, 90g, mentions pollen). Player names a wish for "a little more at stake".
- R3 T1 talk to Lewis: CARD (+20 points; Lewis 750 to 770, still 3 hearts). His Flower Dance answer: GM-SIMULATED from the game (anyone may attend and watch; the dance is for paired young singles). 9:30 to 9:40.
- R3 T2 square to Robin's, 15 min: GM-SIMULATED map. Daffodil to Demetrius: CARD (90g, a little friendship, mildly awkward and pleased). 1,955 to 2,045g. Robin on the coop: CARD (4,000g, 300 wood, 100 stone); sells wood 10g, stone 20g: GM-SIMULATED from the game. 10:15.
- R3 T3 Robin's to farm 20 min (GM-SIMULATED), plant 18 parsnip seeds on tilled tiles 20 min, 0 energy (as R1). 10:55. All 35 new seed tiles dry today; tomorrow's rain waters them; no sprout on Spring 19 (a day lost; parsnips Spring 23, strawberries Spring 27).
- R3 rest of day: GM-SIMULATED, the player's own stated plan ("the afternoon free for chopping wood"; berries kept for tomorrow; no evening plan named). Basic axe, Foraging 3: 10 hits a tree at 1.7 energy, ~15 wood and ~15 min a tree. 10 trees: 150 wood (310 total), 170 energy (180 to 10), 10:55 to 1:25 pm. Too tired for rocks (stone 85). Evening at the farm; bed 9 pm. No Saloon (not chosen).
- R3 night: CARD tally 2,010g (14 parsnips 490, 19 potatoes 1,520). Gold 4,055g. Giant cauliflower: dice list #3 = 40, not 1: none. Energy 270 (slept before midnight).
- R3 morning Spring 19: CARD rain; 24 cauliflowers ready; Jodi's letter (one cauliflower, 350g, within 2 days). Beans and kale: tomorrow.
- R3 prediction: right (Robin pleased, sells wood and stone; Demetrius distracted, 90g, pollen).
- R3 screen sent with exit questions. Round message sent (so the player reads r3), then the exit message.
- R3 exit received: overall pull 8. Marks R3: engaged, engaged, bored; the GM-summarised afternoon marked would-quit and cheat (the player would have eaten berries and mined or bought the stone; "I did not say chop ten trees until I drop"). GM fault: the summary chose more than the player had said. Recorded in condensed.md.
- Exit message sent.
- Exit and memory done (player replied done). Game 1 complete.
