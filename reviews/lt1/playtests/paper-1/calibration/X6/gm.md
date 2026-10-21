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
