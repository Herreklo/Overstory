# The walked corner's houses: first pass (27 October)

Houses C, D and E are built from their facts by fitted parts (`blender/parts/house/`, `tools/houses.py`), with every era, paint and material value in the pack's records (`design.md`). Stills, current (round 11): `round11/cde-{1750-sea-fog,1300-drizzle}-{street,c-east,d-west}-material.png` and `round11/cde-sheet.png`; round 10 is what the strict review saw. The variant from data alone is `variant/red-sheet.png` (`variant/paint-red.json` plus `materials/paint-slam.json`, no code changed). About 44 frames were rendered in all.

**Strict review (Fable, 27 October): FAIL**, on five faults. Three are fixed in round 11, not yet re-reviewed: the kept coat flaked like the neglected one (`lapFactor` 0.8 to 0.3); the plinth read as a cobble cartoon (smaller rounding, dome and joints, and the joint's darkening fades with distance); and C still wore its 1879 colours, because care repaints never recoloured (`care.recolourShare` 0.5). Two are recorded: every house drew white or cream, where the target paints C ochre and E tan (a fair draw from the period lists, not forced); and the lit panes are flat orange, not the target's soft cream (glass and room colour, minor).

**Notes.** By their facts no house here shows long neglect in its paint in 1989: D was painted in 1983 by the care rule and boarded in 1986, so it reads empty from its boarding. The paint's neglect would show at a later date (`--date 2005`), not yet rendered. The black under C's eave in lamp light needs the lamps' bounce fill (the lamps element), and the gable's blue in blue hour is the light's. `tools/check.py` passes the near tier (C 34,979, D 32,364 and E 12,555 triangles of 40,000) and reports the street and city tiers as not built.

**Owed:** the re-review of round 11; the street and city tiers; doors, C's bislag, D's lean-to, the pantile's wave, glass waviness; the frame time on Øystein's Mac, once he says it is free. The new reference images wait for his yes: the ten candidates are at the end of `research-subject.md` (Stavanger byarkiv, 1983 to 1989).

## Second round (27 October)

Stills: `../second-round/final/`: the street stop at the street tier, C's east and D's west walls at eye level, in blue hour and drizzle, and the 2005 pair. Colour stays white by the evidence: the quarter is Gamle Stavanger, all white with white windows since the 1956 scheme, and the target's warm C and E are lamp-warmed cream. Lit panes draw a room behind the glass (`glass.json`, room). Doors are paired and panelled, with steps, and D's is boarded with the house (`timber.json`, doors). Paint fails board by board (`paint.json`, boardSpread). The street and city levels come from the same facts and seed (`timber.json`, levels), and `tools/check.py` passes every tier at 1989 and 2005: C has 34,472 triangles near, 7,874 at street and 1,436 at city. The street tier matches the near one from the street stop and from 12 m (`../second-round/levels/`).

**Strict review (Fable, 27 October): FAIL**, on seven faults. Kept and neglected read right in 2005, and C in blue hour reads as the target paints it. Worst first:

1. The plinth reads as cushions, busier than the wall. Flatter split faces, varied by seed, and quieter joints would fix it.
2. Unlit panes in drizzle are navy voids. They need the sky's reflection toward grazing.
3. C's 1971 patch runs as a grey band down to the wall foot, which reads as a drip stain the facts don't give. A patch should read as boards and end at the old opening.
4. D's boarding reads as louvred shutters. The boards should be butted and irregular, with one out of true.
5. 2005 D's peel is even, not weighted to exposure, and its paint and bare wood are hard to tell apart.
6. 2005 C's 1998 cream reads as a change of colour in daylight.
7. D's pantile roof against C's slate comes from the workings' data and needs confirming.

**Owed:** the seven faults. C's door and bislag and D's lean-to are in no still's view. Also owed: the pantile's wave and glass waviness; the frame time on Øystein's Mac; the archive photos, which wait for his yes; the lamps' bounce, which belongs to the lamps element. About 45 frames were rendered this round, in 23 Unity runs.
