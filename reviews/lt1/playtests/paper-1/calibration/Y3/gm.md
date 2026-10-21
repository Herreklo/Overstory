# GM notes: Y3, Stardew Valley (paper)

Calibration run. Player kind: cozy player. Twin run: X3 (same opening, same dice). Render Stardew at its best and no better: the clock and energy budget, small warm dialogue, gift reactions with hearts, the shipping tally at night, the pleasure of a full field and a tidy plan, a little surprise. Villagers talk briefly and in character; nothing grand happens on an ordinary day.

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
- R0: player spawned (agent a6f2bbcd487589b29, opus, persona 3). r1-act.md written: water all, harvest and ship, walk to Pam's with salmonberries, give a leek.
- R1 t1: CARD water 52 tiles with one refill: 1 h 20, 90 energy. 6:00 to 7:20. Energy 270 to 180.
- R1 t2: CARD harvest 35 crops: 30 min. 7:20 to 7:50. Quality d100 per batch: parsnips die 1 = 64 (all normal); potatoes die 2 = 76 (all normal). 1 parsnip and 1 potato kept for the bundle; 14 parsnips and 19 potatoes in the bin (2,010g overnight at base price).
- R1 t3: CARD walk to Pam's 25 min + salmonberries 20 min (12 berries). Arrive 8:35; Pam home (8:30 to noon). Leek: liked, birthday x8 = +360. Pam 2 hearts (taken as 500 pts) to 860 pts: 3 hearts, 110/250 to the 4th. No talk bonus: the act gave a gift only. 8:40.
- R1 GM-SIMULATED: travel times from the trailer (square and Pierre's 10, Saloon 10, Clint's 10, beach 10, farm 25, Robin's 25, forest and Marnie's 25, mines 35), not in the plan; chosen to fit the plan's farm-based times.
- R1 note: the plan says r1 ends about noon; the player's three turns end at 8:40, so the screen stands at 8:40 (the clock runs on the player's turns, not the plan's estimate). Act line kept at "up to three turns", as the opening set it.
- State after R1: 8:40 am at Pam's trailer. 2,315g; bin 14 parsnips, 19 potatoes. Energy 180/270. Pack: 12 salmonberries, 1 parsnip, 1 potato, 1 leek. Chest at home: the rest. Farm all watered; 35 tilled tiles empty. Pam 3 hearts (birthday gift given). Dice used: 2 (next: die 3 = 40).
- R2: r2-act.md read. R1 marks: engaged, engaged, engaged. Pull 8.
- R2 t1: CARD walk trailer to square 10 min (8:50). Talk Evelyn +20, Lewis +20 (10 min, 9:00). Request taken. Pierre's at 9: 18 parsnip seeds, 360g; 2,315 to 1,955g. 9:10. GM-SIMULATED: Evelyn shown at 1 heart (not listed in the opening).
- R2 t2: CARD walk to farm 20 min (9:30). Daffodil from the chest. GM-SIMULATED: planting 35 already-tilled tiles, 20 min, no energy (the plan's 40 min/30 energy is hoe and plant; these tiles stayed tilled after harvest). Watering 35 tiles, scaled from the plan (52 tiles, 1 h 20, 90 energy): 55 min, 60 energy; can had 28 left, one refill. 10:45. Energy 120.
- R2 t3: GM-SIMULATED walk farm to Community Center via town 20 min, CC to Robin's 10 min. Bundle takes partial deposits (as in the game): 2 of 4. CARD Demetrius takes the daffodil: 90g, a little friendship (GM-SIMULATED: Demetrius at 1 heart, no heart change). Robin: coop takes three days, starting the morning after it's ordered (as in the game); talk +20. Robin's shop shown (wood 10g, stone 20g), as in the game. 11:30. 2,045g.
- State after R2: 11:30 am at Robin's. 2,045g; bin unchanged. Energy 120/270. Pack: 12 salmonberries, 1 leek. Chest: 2 daffodils, 4 horseradish, quartz, amethyst, 31 copper ore, 2 copper bars, 3 coal, 160 wood, 85 stone, 40 fibre. Farm: 24 cauliflowers (tomorrow), 18 beans and 10 kale (2 days), 30 parsnips and 5 strawberries planted and watered. Bundle 2 of 4. Dice used: 2 (next: die 3 = 40).
- R2: r2-screen.md written. Round 3 player to be a fresh agent (gm-brief changed: fresh player each round, no SendMessage).
- R3: r3-act.md read (fresh player agent ae2c347c59abde639). R2 marks: engaged, engaged, engaged. Pull 8.
- R3 t1: GM-SIMULATED walk Robin's to farm 20 min (11:50). CARD smelting 5 ore + 1 coal = 1 bar, 30 min: 3 bars by 1:20, reloaded between chops; ore 31 to 16, coal 3 to 0, bars 2 to 5. GM-SIMULATED clearing (not in the plan; Stardew's basic tools at Foraging 3 / Mining 2): a tree 15 swings x 1.7 = ~25 energy, ~14 wood with its stump, ~12 game-min; a twig 1 wood, 1.7; a stone 1 stone, 1.8; weeds free (fibre). The patch by the house holds 4 trees, twigs, stones and weeds; 6 more trees at the edge of the uncleared land. 10 trees + 12 twigs = 152 wood (160 to 312); 24 stones (85 to 109); +18 fibre, 6 tree seeds. ~319 energy: 10 salmonberries eaten (2 left), energy ends ~50. Goal met at 3:20 pm; the player stops as the act says.
- R3 t2: CARD walk farm to the Saloon 20 min via the bus stop, where Pam sits noon to 4:30 (talk +20). Saloon 3:40. GM reading of intent: the act says "tonight" and "bed before 11", so the visit is the evening. Gus kind (talk +20); asked about Shane, Gus names what he serves Shane: beer and pizza (GM: what a barman would know; not hot peppers). Emily from 4, Pam in at 4:30 (no drink: no loved gift), Shane in after six (talk +20; curt at 0 hearts), Willy about seven, Clint staring at Emily (all CARD). Leave 10:15.
- R3 t3: walk home 20 min, bed 10:35. CARD night tally: 14 parsnips x 35 = 490, 19 potatoes x 80 = 1,520; 2,010g. 2,045 + 2,010 = 4,055g. Giant cauliflower: die 3 = 40 (not 1): none. Spring 19: rain, everything watered; cauliflowers ready; Jodi's letter (CARD). Energy 270 (bed before midnight).
- State after R3: Spring 19, 6:00 am, rain. 4,055g. Energy 270. Wood 312, stone 109, 5 copper bars, 16 ore. Bundle 2 of 4. 24 cauliflowers ready. Pam 3, Gus 3, Lewis 3, Robin 2, Evelyn 1, Demetrius 1, Shane 0. Dice used: 3 (next: die 4 = 66).
- R3: r3-screen.md written (turns, the Saloon evening, tally, Spring 19 morning, exit questions). Exit by fresh player agent aefcff1b09d7499fd: exit.md and memory.md written. R3 marks: engaged x3. Exit pull 8.
