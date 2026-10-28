# p3: painted finish, house 107's corner

`sheet.png`: P1 | BASE (p2 step 1) | FINAL. Rows are the street stop, 12 m and eye level. Overcast is on the left, low sun on the right. `colour-eye.png`: the colour still beside its clay twin, at eye level and the street stop, in low sun.

p3 (commit de6e1c0) is the floor: beside BASE it holds as a whole (the coordinator, 28 October).

**Bad first**
- The tear still falls short of P1's, which Øystein called the more realistic one. P1's hard patches, board by board, read as real failed paint at the street stop and from 12 m. FINAL's are narrow and quiet, and they nearly vanish at 12 m.
- Board ends at eye level (the critic's point 3) were not done this round. They go to the street, which builds 107 whole from `corner.py`'s successor, along with the massing and the plinth gap.
- The plinth's corner still shows a recessed gap. The fault is in the model: in `corner.py` the gable's first stone starts before the corner stone's 180 mm return ends. The dark square is lighter now (`stone.underL` 16 → 50), but the gap remains.
- Colour: the lit wall reaches 85, not 88. The shade side sits in the 60s, in the sky's blue; the critic's 30 would read as charcoal on a white wall.
- Which end of the sill leaks is still a seed, not a fact.

**What changed, each one judged side by side with BASE**
- Laps stay at every distance (the sub-texel fix). The ply stays flat.
- No glow: the plinth's top under the drip board is dark again (junction 22, reach 0.1, as in BASE, not p2's 32), and the tops no longer lift (`up.L` 0, BASE had 4).
- The tear follows the water. The tongue's hard peel and its wash stay board by board, now hard-sided and broken (each board shifted and sized on its own), so there is no smudge and no cone. Narrow runs leave the sill's horns and each batten's lower end; each darkens toward its lap's drip edge and ends in a flake of bare wood. From the street stop, each run becomes one soft mark of its own (`runoff.far`, a shader blend by distance). Bare wood is P1's 52.
- Overcast: the key comes from the street side. The street face is about 74 and the side face 57; the plinth is 37 against the ground's 52. BASE's foundation (its wavering wet edge and stone brushwork) and its paint brushwork are back.
- Colour: the paint is a neutral aged white, so the gold is the sun's and the shade takes the sky's blue. The pantiles are muted, so rust on the nails is the one accent.
