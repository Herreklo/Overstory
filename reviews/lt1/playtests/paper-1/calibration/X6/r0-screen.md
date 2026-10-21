# Round 0

A paper version of Slay the Spire.

**Act 1, floor 6. Elite.** You are the Ironclad. HP 58/80. Gold 99.

**Relics:** Burning Blood (heal 6 HP at the end of each combat). Bag of Marbles (at the start of each combat, apply 1 Vulnerable to all enemies).
**Potions:** Fire Potion (deal 20 damage to one enemy). Block Potion (gain 12 Block). One empty slot.

**Your deck, 13 cards**
- Strike ×5 (1 energy, Attack): deal 6 damage.
- Defend ×4 (1, Skill): gain 5 Block.
- Bash+ (2, Attack, upgraded at your last campfire): deal 10 damage, apply 3 Vulnerable.
- Anger (0, Attack): deal 6 damage; add a copy of this card to your discard pile.
- Pommel Strike (1, Attack): deal 9 damage, draw 1 card.
- Shrug It Off (1, Skill): gain 8 Block, draw 1 card.

**The enemy: Gremlin Nob.** HP 84/84. Vulnerable 1 (from your marbles).
**Intent: Buff.** He will do something to himself this turn; he isn't attacking.

**Turn 1.** Energy 3/3.
- **Hand:** Defend, Defend, Defend, Bash+, Defend.
- **Draw pile (8, order hidden):** Strike ×5, Anger, Pommel Strike, Shrug It Off.
- **Discard pile:** empty.

**How it runs.** Each turn you draw 5 cards and have 3 energy. Unplayed cards are discarded at the end of your turn, and your Block falls away at the start of your next. When the draw pile runs out, the discard pile is shuffled into a new one. Vulnerable: takes 50% more attack damage. Weak: deals 25% less attack damage. Both count down by one at the end of each round. Potions cost no energy.

**The map ahead.** From here you can go up to any node on floor 7. After that each column runs straight up, except that on floors 10 and 12 you may step to a neighbouring column.

```
16              Boss: Hexaghost
15   Rest            Rest            Rest
14   Monster         Elite           Unknown
13   Unknown         Rest            Monster
12   Merchant        Monster         Elite
11   Monster         Unknown         Monster
10   Unknown         Elite           Rest
 9   Treasure        Treasure        Treasure
 8   Rest            Monster         Merchant
 7   Unknown         Monster         Elite
 6            [ Gremlin Nob ]  <- you
```

Win, and you take gold, a relic from the elite and a choice of cards. Then you choose your path.

**What you can do:** play cards your energy allows, drink potions, end your turn. Turn 1 is in front of you. For turns 2 and 3, which you can't see yet, give a plan or a rule ("if he's attacking, block first"); I'll play it as written and stop to ask if a hand doesn't fit it.

Write your act file to calibration/X6/r1-act.md, up to three turns.
