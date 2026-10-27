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

## Third round (27 October)

Stills: `../third-round/final/`: the street stop at the street tier, C's east and D's west walls at eye level, in blue hour and drizzle, and the 2005 pair. What changed:
- The plinth is split granite blocks, pointed flush.
- Unlit panes show their room by daylight and reflect the sky seen through the air.
- D's boarding is reused formwork boards nailed upright, each greying at its own pace, with rust run from its nails.
- Paint fails first where water works in: under a sill's run-off, at end grain, at the foot and on the rain side.
- Dirt gathers by the same water, and little on the open wall.
- The old town's white scheme from 1956 keeps a coat's white, so C's 1998 repaint reads the same white. It also turned C's, D's and E's 1989 colours to whites.
- Curtains fold.

`tools/check.py` passes every tier at 1989 and 2005.

**Strict review (Fable, 27 October): FAIL, close.** Of round 2's seven faults, these are fixed: the plinth (1), the panes (2), the boarding as louvres (4), the peel's distribution (5) and the cream (6). C's patch band (3) was the lamp post's shadow, which is the light's. The pantile against slate (7) is confirmed from the workings. The recheck of only the changed stills passed the plinth, the panes and the curtains and failed on three points:
- Coat age doesn't step from 2 to 6 or 7 to 22 years.
- D's boards need a wood material: mixed grey-browns, grain, rust streaks rather than dashes, and silvering by 2005 (wet silvered wood is mid grey-brown, not charcoal).
- The flakes are a noise field; they should be bounded by the boards, run long along the grain and be heaviest at the drip, the ends, below the sills and at the foot.

After the recheck, the soiling was driven by water: C's 2005 coat now shows run-off under its sills and D's 2005 wall no longer reads tarred. This has not been rechecked.

**Not the houses':** hard directional shadows in drizzle (the lamp post, a chimney stepped down a gable, the rafter tails); the lamps' pools and bounce; the gable's blue in blue hour; the wet ground; and the near air, which lifts every dark surface by about 0.04 (linear) and flattens the plinth and boarding.

**Owed (a fourth round):** the three recheck points; a light S-shaped mark at the foot of D's upper-left boarding in 1989; finer curtain folds and header. Still owed from before: C's bislag, D's lean-to, the pantile's wave, the frame time and the archive photos (these wait for Øystein's yes). About 60 views, each with a grey twin, were rendered in about 34 Unity runs.

## Fourth round (27 October)

What changed. The ten archive photos are in `docs/references/houses/`, logged in `docs/research/downloads.md`. The scheme's whites are one titanium white, so a 2-year, a 7-year and a 22-year coat now read apart. D's boarding is a weathered-softwood record (`materials/pine.json`): formwork stock, rough sawing, knots, silvering and nail rust. The boards are fitted in the openings, standing true behind out-of-level battens. Flakes follow the grain within each board, start at the end grain and gather low on the wall. The ray bake now samples each triangle corner. `tools/check.py` passes at 1989 and 2005. The stills are in `reviews/lt1/houses/fourth-round/final/`.

What is left for the rebuild. The round stopped at a pushed point, because the houses will be rebuilt to the new art direction, so Fable did not recheck it. The systems and data hold whatever look comes next: coat age by years, the schemes, the wood record and the photos. The look is open: the flakes' and boards' rendering, C's clapboard (it has no lap depth or nail heads), and the trim's single flakes. The light still owes three things: the drizzle's crisp cast shadows (the lamp box makes the "rectangle" by C), its exposure, and the near haze.

Fable's recheck arrived after the round was closed (FAIL, closer): points 1, 2, 5 and 6 of its first review are answered (the rectangle is the light's cast shadow; the cream is gone; D's boards read as boards behind battens, with knots and faint runs; the sill runs break per course). Left, heaviest first: the per-corner bake interpolates along the triangles' diagonals and shows on D as light-dark wedges along every course and on C 2005 as a diagonal hatch under the sills, so the bake must give one value per board segment or sample a map, and nothing on a wall may follow a triangle edge (this alone turns it to a pass); one isolated dark blob on D's door casing at the head in 2005 (casing paint fails at the foot and the end grain, in company, or not at all); D's 2005 wall is an even mottle at one-eighth, so the pale remnants should gather into a few islands and the boarded windows stay the darkest dark; C's 2005 end-grain loss is a column of equal width beside every window, a stencil; the 1989 patches run through courses under one edge, where every lap should break them. The street tier holds four values at one-eighth. These go to the rebuild.
