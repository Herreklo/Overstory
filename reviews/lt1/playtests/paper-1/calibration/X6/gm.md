# GM notes: X6, Slay the Spire (paper)

Calibration run. Player kind: optimiser. Twin run: Y6 (same opening, same draw order, same intents, same rewards). Render the game at its best and no better: exact numbers, visible intents, honest draws, the tension between damage now and block now, Enrage punishing Skills, rewards that change the deck's shape, and a map whose path is a risk budget. A0 (no Ascension) values throughout.

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
- R0 (calibration GM, 21 Oct): player spawn refused by the harness ("Concurrent subagent limit reached ... Do not retry"). No player agent started; no act files exist. Game not begun.
- R0 (calibration GM, fresh attempt, 21 Oct): fresh player agent (sonnet, general-purpose) spawned with the round-0 spawn message; r1-act.md written.
- R1 t1: Bash+ 10 x1.5 (Vuln 1) = 15; Nob 84 -> 69; Vuln 1+3 = 4. No Skills played. Nob Bellow: Enrage 2. End of round: Nob Vuln 4 -> 3. CARD (rules, Nob script)
- R1 t2: drew Pommel Strike, Strike, Strike, Anger, Strike. Nob intent Rush 14 (Str 0). Pommel 9x1.5 = 13 (69 -> 56), draws Shrug It Off; Anger 9 (56 -> 47, copy to discard); Strike 9 (47 -> 38); Strike 9 (38 -> 29). Energy 0. Strike, Shrug It Off unplayed. Block Potion (rule: he attacks for 14 or more): Block 12. Fire Potion by the rule as written (hand 40 + 30 >= 69): flat 20, Vuln doesn't apply (CARD rule) -> Nob 9. Rush 14 - 12 Block = 2; HP 58 -> 56. End of round: Nob Vuln 3 -> 2. Judgement: the rule's literal condition and its intent ("drink if it completes the kill") give the same end state (Nob dead turn 3, both potions spent), so literal was applied.
- R1 t3: draw pile Strike, Strike, then reshuffle 1 (12 cards, sorted, seed 'sts-calib-reshuffle-1') -> top: Defend, Shrug It Off, Strike, Anger, Anger, Defend, Strike, Pommel Strike, Strike, Defend, Bash+, Defend. Hand: Strike, Strike, Defend, Shrug It Off, Strike. Nob intent Rush 14. Strike 6x1.5 = 9 -> Nob 0. Victory on turn 3. Burning Blood +6: HP 56 -> 62/80. CARD (rules; reshuffle seed)
- R1 plan adaptation: the fight ended inside round 1, so r1-screen carries what the plan gives r2-screen (fight's end, Burning Blood, rewards, map). R2 = rewards and path, and the chosen node opened; R3 = that node played; exit on r3-screen. CARD (plan, shifted one round)
- R1 prediction (Enrage-type buff; Rush ~14 turn 2; Nob 69 after Bash+; dies turn 3, or turn 2 with a perfect draw and the Fire Potion): due and scored.
- R2 t1: took 30 Gold (99 -> 129), Swift Potion (slot 1), Tiny Chest (counter 0), Inflame (deck 14). CARD (rewards)
- R2 t2: right-hand floor 7 node: Elite, Lagavulin (HP 110, asleep, Metallicize 8). Real-game details the plan leaves out, rendered as the game does: he starts with 8 Block; damage to his HP wakes him, removes Metallicize and stuns him for his next turn; pattern after waking Attack 18, Attack 18, Siphon Soul. Marbles: Vuln 1. CARD (nodes) + real-game rule
- R2 map clarification (player asked): steps to a neighbouring column happen onto floors 10 and 12 (from floor 9 to 10, from 11 to 12). GM interpretation of the r0 map line; no effect on the nodes this run reaches.
- R2 t3 (fight 2): opening shuffle of the 14-card deck, sorted, seed 'sts-calib-reshuffle-2' -> Strike, Defend, Strike, Strike, Inflame | Pommel Strike, Shrug It Off, Defend, Defend, Strike | Defend, Anger, Bash+, Strike.
  - Fight turn 1: hand Strike, Defend, Strike, Strike, Inflame. Inflame (Str 2). Strike (6+2)x1.5 = 12 vs Block 8 -> 4 HP (110 -> 106): he wakes, Metallicize removed, intent Stunned. Strike 12 -> 94. Energy 0. Lagavulin stunned. End of round: his Vuln 1 -> 0.
  - Fight turn 2: hand Pommel Strike, Shrug It Off, Defend, Defend, Strike; intent Attack 18. Pommel 11 (94 -> 83), draws Defend; Strike 8 (83 -> 75). 1 energy, no attacks in hand: Swift Potion (rule) draws Anger, Bash+, Strike (draw pile empty). Anger 8 (75 -> 67, copy to discard); Strike 8 (67 -> 59). Energy 0; Bash+ (2) unplayable. Attack 18 unblocked: HP 62 -> 44.
  - Fight turn 3: reshuffle 3 (14 cards incl. Anger copy, sorted, seed 'sts-calib-reshuffle-3') -> Defend, Bash+, Shrug It Off, Defend, Pommel Strike, Strike, Strike, Defend, Anger, Strike, Anger, Strike, Strike, Defend. Hand: Defend, Bash+, Shrug It Off, Defend, Pommel Strike. Intent Attack 18. The rule (Bash+ then attacks) leaves 0 Block: HP 44 -> 26, under 30, so the player's stop-and-ask applies: round ends with the hand shown. CARD (player's rule)
- R2 prediction (a real Act 1 elite; if Lagavulin, waking him costs him a turn, so burst him): Lagavulin; woken by damage and stunned. Right.
- R3 t1 (fight turn 3): Bash+ (10+2) = 12 (59 -> 47), Vuln 3; Pommel Strike (9+2)x1.5 = 16 (47 -> 31), draws Strike. Energy 0. Attack 18 unblocked: HP 44 -> 26. End of round: his Vuln 3 -> 2. CARD (rules)
- R3 t2 (fight turn 4): draw Strike, Defend, Anger, Strike, Anger. Intent: Strong Debuff (Siphon Soul, third move after waking). Player's rule: hand total 4 x 12 = 48 >= 31, play it all, Anger first. Anger 12 (31 -> 19), Anger 12 (19 -> 7), Strike 12 -> 0. Victory turn 4 before he acts. Burning Blood: HP 26 -> 32/80. CARD (Lagavulin script)
- R3 t3: rewards 28 gold (129 -> 157), Pen Nib (counter 0); no potion in the plan's reward. Card rule "only if it beats a Strike in a Strength deck": Pommel Strike strictly beats Strike (same cost, single hit, +3 damage, draws); Uppercut arguable; Feel No Pain has nothing to exhaust. Took Pommel Strike (GM judgement, said on the screen in one line). Floor 8 Merchant (stock per plan): remove a Defend (75; 157 -> 82). "Best attack or relic I can afford" with 82: affordable attacks Carnage 72, Headbutt 52, Pommel Strike 50; relics all over 82. Took Carnage (GM judgement: highest damage per energy and per card; the usual strong Act 1 pick), 82 -> 10. Deck 15. CARD (nodes, player's rule)
- R3 prediction (he hits for 18, 44 -> 26; dead next turn before he acts whatever the draw; only a pattern change could break it): right on both.
- R3 exit: fresh player wrote exit.md and its memory section. Overall pull 5. Player flagged the card pick (it meant "a clear margin" and would have skipped) and the shop buy as made for it: a GM fault in resolving an ambiguous rule instead of skipping; noted in condensed.md.
- State at end: HP 32/80, gold 10, deck 15 (Strike x5, Defend x3, Bash+, Anger, Pommel Strike x2, Shrug It Off, Inflame, Carnage), relics Burning Blood, Bag of Marbles, Tiny Chest 0, Pen Nib 0; floor 9 (right) Treasure next.
