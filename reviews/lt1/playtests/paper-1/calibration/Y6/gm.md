# GM notes: Y6, Slay the Spire (paper)

Calibration run. Player kind: optimiser. Twin run: X6 (same opening, same draw order, same intents, same rewards). Render the game at its best and no better: exact numbers, visible intents, honest draws, the tension between damage now and block now, Enrage punishing Skills, rewards that change the deck's shape, and a map whose path is a risk budget. A0 (no Ascension) values throughout.

## Round plan
- **R1:** combat turns 1 to 3, played by the player's rules. Stop and show the hand if a rule doesn't cover it (that ends the round early). **r1-screen:** each turn's plays and numbers, Nob's actions, HP, Block, statuses, piles, and the next hand with Nob's intent.
- **R2:** turns 4 to 6, or the end of the fight. **r2-screen:** the fight's end (or state), Burning Blood, then the rewards screen (below) and the map.
- **R3:** rewards and path, and the next node if reached. **r3-screen:** what was taken, the deck now, the chosen node played out briefly (event text, or the first turn of the next fight shown and summarised), then exit questions: overall pull 0 to 10, how this paper session compares with the real game, what was best and worst.

## Rules to apply exactly
- Damage = (base + attacker Strength) × 1.5 if the target is Vulnerable × 0.75 if the attacker is Weak, rounded down. Block absorbs first. Block is lost at the start of the owner's turn.
- Vulnerable and Weak count down by 1 at the end of each round (after the enemy acts). Bag of Marbles: Nob starts with Vulnerable 1. Bash+ adds 3 to whatever is there.
- Anger: when played, a copy goes into the discard pile (not the hand).
- Pommel Strike and Shrug It Off draw from the draw pile; if it's empty, shuffle the discard pile first.
- **Reshuffle:** sort the discard pile alphabetically by card name, then shuffle with Python `random.Random('sts-calib-reshuffle-<n>')` (n = 1, 2, ... in order) and `.shuffle(list)`. The first card of the list is the top.
- Potions cost no energy and are not cards (they never trigger Enrage). Fire Potion deals a flat 20: in the real game Vulnerable and Strength don't change it.
- Vulnerable or Weak applied by an enemy on its own turn doesn't tick down at the end of that same round.

## The draw pile (top first, fixed for both twins)
Defend, Defend, Defend, Bash+, Defend | Pommel Strike, Strike, Strike, Anger, Strike | Shrug It Off, Strike, Strike
(Turn 1's hand is the first five. Turn 2 draws the next five; Pommel Strike would draw Shrug It Off.)

## Gremlin Nob (A0)
HP 84. Turn 1: Bellow (gains Enrage 2: whenever the player plays a Skill, he gains 2 Strength; the intent icon showed only "Buff"). Then, by pre-roll: turn 2 Rush, 3 Rush, 4 Skull Bash, 5 Rush, 6 Rush, 7 Skull Bash, 8 Rush, 9 Rush, 10 Skull Bash.
- Rush: 14 damage (+ Strength).
- Skull Bash: 6 damage (+ Strength) and 2 Vulnerable on the player.
Show the intent as the game does: the attack number including his current Strength and the player's Vulnerable.

## Rewards on victory
- Gold: 30.
- Potion: Swift Potion (draw 3 cards). If all slots are full, the player may discard one or leave it.
- Relic: Tiny Chest (every 4th Unknown room is a Treasure room; counter starts at 0).
- Card, pick one or skip: Twin Strike (1, Attack: deal 5 damage twice), Iron Wave (1, Attack: gain 5 Block, deal 5 damage), Inflame (1, Power: gain 2 Strength).

## The nodes ahead (fixed)
- **Floor 7, Unknown (left):** an event. A man with a cart offers three things for nothing: a banana (heal a third of max HP), a doughnut (+5 max HP), or a box (a random relic, and a curse, Regret, added to the deck). Box relic if taken: Orichalcum (if you end your turn with no Block, gain 6 Block). Tiny Chest counter +1.
- **Floor 7, Monster (middle):** Jaw Worm, HP 42. Opens with Chomp (11). Pattern after: Bellow (+3 Strength, 6 Block), Thrash (7 damage, 5 Block), Chomp. Reward: 14 gold, card choice: Clothesline (2: 12 damage, 2 Weak), Armaments (1: 5 Block, upgrade a card in hand), Wild Strike (1: 12 damage, shuffle a Wound into the draw pile).
- **Floor 7, Elite (right):** Lagavulin, HP 110, asleep with 8 Metallicize. Wakes after 3 turns or when damaged. Then: Attack 18, Attack 18, Siphon Soul (−1 Strength, −1 Dexterity), repeating. Reward: 28 gold, relic Pen Nib (every 10th Attack played deals double damage), card choice: Uppercut, Pommel Strike, Feel No Pain.
- **Floor 8:** Rest (left): heal 30% of max HP (24) or upgrade a card. Monster (middle): two Louses (Red HP 12, Green HP 14; each curls up for 3-7 Block when first hit). Merchant (right): Shockwave 75, Headbutt 52, Battle Trance 80, Carnage 72, Pommel Strike 50; colourless Swift Strike 85; relics Orichalcum 155, Kunai 245, Membership Card 180; potions Strength 72, Fear 52, Blood 50; card removal 75.
- **Floor 9, Treasure:** left chest Vajra (start each combat with 1 Strength); middle Pen Nib; right Anchor (start each combat with 10 Block).

## Log
- R0: opening sent (r0-screen.md). Waiting for r1-act.md. HP 58/80, Nob 84, turn 1.
- R1 act read (3 turns: Bash+ then no-Skills race; potions only for lethal or HP<30).
- R1 T1: CARD Bash+ 10×1.5=15, Nob 84→69, Vuln 1+3=4; Defends unplayed. Nob Bellow: Enrage 2. End of round Vuln 4→3.
- R1 T2: CARD draw Pommel, Strike, Strike, Anger, Strike; intent Attack 14. Pommel 13 (9×1.5 rounded down) →56, draws Shrug It Off; Anger 9 →47 (copy to discard); Strike 9 →38; Strike 9 →29. Potions held (Fire not lethal; 58−14=44 ≥30). Nob Rush 14: player 58→44. Vuln 3→2. Nob Strength 0.
- R1 T3: CARD draw Strike, Strike; reshuffle 1. GM-SIMULATED reshuffle; seed sts-calib-reshuffle-1; sorted 12 discards → [Defend, Shrug It Off, Strike, Anger, Anger, Defend, Strike, Pommel Strike, Strike, Defend, Bash+, Defend]. Drew Defend, Shrug It Off, Strike. Intent Attack 14. Cards max 27 < 29 (Shrug+Anger line also 27), so lethal needs Fire Potion: Strike ×3 (29→2), Fire Potion flat 20 → dead. Victory turn 3, damage taken 14. Burning Blood +6: 50/80. Anger copy gone; deck 13.
- R1 state: HP 50/80, Gold 99 (+30 offered), potions Block (Fire used), rewards on offer: 30 gold, Swift Potion, Tiny Chest, card Twin Strike / Iron Wave / Inflame. Fight ended in R1, so the plan shifts one round earlier: r1 showed the fight's end, rewards and map; R2 = rewards and path, r2 plays the chosen floor-7 node out to its first decision; R3 = that node resolved, then exit.
- GM error in r1-screen: turn 3's explanation named the top card of the new hidden draw pile (Anger) when weighing Shrug It Off. The player flagged it as a leak ("cheat"). It changed no play (both lines came to 27). From r2 on, no hidden card is named before it is drawn.
- R2 act read: take all rewards + Inflame; floor 7 Elite (right); fight by rules (Inflame first, Bash+ on its turn, block only damage above 6, Swift Potion if hand has no attacks, Block Potion only if a hit puts HP <20; Lagavulin: wake with damage, no block while asleep; stop if HP <25).
- R2 T1: CARD rewards taken: gold 129, potions Block + Swift, Tiny Chest 0/4, deck 14 with Inflame.
- R2 T2: CARD floor 7 right = Lagavulin (plan). HP 110, Block 8 and Metallicize 8 at start (real A0 pre-battle), asleep, Vuln 1.
- R2 T3 shuffle: GM-SIMULATED combat-start shuffle of the 14-card deck; seed sts-calib-reshuffle-2 (next n of the plan's reshuffle rule, sorted alphabetically first) → [Strike, Defend, Strike, Strike, Inflame, Pommel Strike, Shrug It Off, Defend, Defend, Strike, Defend, Anger, Bash+, Strike].
- R2 T3 turn 1: Inflame (Str 2); Strike 12 into Block 8 → 4 HP, Lagavulin 106, wakes (CARD, real game: woken by HP loss, Metallicize removed, next move Stunned); Strike 12 → 94. Stunned turn. Vuln 1→0.
- R2 T3 turn 2: intent Attack 18. Pommel 11 →83 (drew Defend); Shrug 8 Block (drew Anger); Defend → 13 Block; Anger 8 →75. Rule read: block until damage taken ≤6 with fewest cards (Shrug+Defend 13; two Defends 10 would let 8 through). Took 5: HP 45.
- R2 T3 turn 3: draw Bash+, Strike; GM-SIMULATED reshuffle; seed sts-calib-reshuffle-3; 12 sorted discards → [Defend, Strike, Shrug It Off, Pommel Strike, Strike, Defend, Defend, Anger, Strike, Anger, Strike, Defend]; drew Defend, Strike, Shrug. Intent Attack 18. Conflict read: Bash+ first (12 → 63, Vuln 3), last energy to Shrug (Block 8, drew Pommel). Took 10: HP 35. Vuln 3→2.
- R2 T3 turn 4: drew Strike, Defend, Defend, Anger, Strike. Intent Strong Debuff. Anger 12 →51, Strike 12 →39, Strike 12 →27; 1 energy unspent, no Block. Siphon Soul: Str 2→1, Dex 0→−1. Vuln 2→1.
- R2 T3 turn 5: drew Anger, Strike, Defend; GM-SIMULATED reshuffle; seed sts-calib-reshuffle-4; 12 sorted discards → [Pommel Strike, Strike, Strike, Defend, Bash+, Shrug It Off, Anger, Strike, Defend, Strike, Anger, Defend]; drew Pommel, Strike. Intent Attack 18. Lethal: Pommel 15 →12 (drew Strike), Anger 10 →2, Strike 10 →0. Victory turn 5, 15 damage taken, no potions. Burning Blood: 41/80.
- R2 state: HP 41/80, gold 129 (+28 offered), relics Burning Blood, Bag of Marbles, Tiny Chest 0/4 (+ Pen Nib offered), potions Block, Swift; deck 14. Card offer Uppercut / Pommel Strike / Feel No Pain. Next nodes forced: floor 8 Merchant, floor 9 Treasure. Step rule confirmed on screen. R3 = rewards + Merchant played out (stock from plan, floor 8 right), Treasure if reached, then exit.
- R3 act read: take 28 gold, Pen Nib, Uppercut; go to the Merchant and stop before buying; standing Pen Nib rule.
- R3 T1: CARD rewards taken: gold 157, Pen Nib counter 0, deck 15 with Uppercut.
- R3 T2: CARD floor 8 right = Merchant, stock and prices from the plan shown in full (card texts and relic/potion texts as the real game words them); stopped before any purchase, as asked.
- R3 T3: standing rule acknowledged; no fight, not applied.
- R3: exit questions from the plan (pull, comparison with the real game, best and worst) plus round 3 marks. Session ends at the shop: HP 41/80, gold 157, deck 15.
- Exit read (pull 6; rules audited and held; fights became spectator rounds; GM lookahead and one hidden-card leak named as the format's faults; best: the shop). Exit message sent for the memory file.
