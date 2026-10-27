# LT1's harbour town from the city camera

**Light: 16:00 low sun** (`Heart_1600-low-sun`), picked on 27 October from r08 and r09.

We started from 17:50 sea fog, as the brief asked. With the street's rig it gives an even blue murk from the city camera, even with lit windows (r09). The bank doesn't show over the water, and walls and roofs fall to one value. At 16:00, the low sun picks out every wall, roof and window and sets the birches alight, and it sits closest to Dishonored 2's bay.

**Rounds:** grey r01–r06, light r07–r11 (`python3 tools/town.py light -- -out reviews/lt1/town/rNN -moment 1600-low-sun`).

- r10: windows, doors, corner boards and lit panes from the diaries; arks, porches and lean-tos grown on the houses.
- r11: trees as three to five faceted masses in clumps; birch past its peak, one in four bare. Small stills in `r11/small/`.
- r12: the harbour's water as a designed colour (the sky's hue, light over the shallows, dark at the foot of made things), a light line at every waterline.
- r13: wet bands on the quay and sjøhus feet; roofs relaid on their materials' cycles, so old roofs come back near new.
- r14: yards closed from the plots: hedges, plank and picket fences, dry-stone walls where the plot falls.
- r15: lanes and setts lighter and warmer than the grass, so the net of lanes reads from the hill; steps on the smau, cut into benched ground. Small stills in `r15/small/`.
- r16: the sun reaches the town: the bay's south-west mouth is a low coast of skerries, not headlands that shaded it from the 8° sun; a lower ridge, so the mid view holds a strip of sky; the air at the city's distances, in the art direction's bands.
- r17: the air clear for its first 180 m (`town.json`, air), so the quay and near water are not veiled; verge boards and fascias on the gables and eaves (`timber.json`'s working); chimneys with a corbelled crown. Small stills in `r17/small/`.
- r18: the crowns' fringe: a leaf stroke on each upper facet, turned to the eye and opened only where the crown turns from it (`Town.shader`, `_Card`), so the strokes break the outline and the sky seams; crowns muted a step below the walls; trunks by species, tapered, a birch's pale.
- r19: the masses' facets shaded part way to their round (lit and shaded sides, planes a hint); the water's light line only where the sun strikes.
- r20–r21: the water as a mirror for the screen's reflections, at 0.6 of their strength; r20 (glossy with chop) gave blurred glows, r21 (blobby swell) scattered colour into the bay.
- r22: parallel crests along the quay break the mirror into horizontal bands under each sjøhus; plots packed tighter along the lanes (narrower passages and front yards, more back houses and sheds). Small stills in `r22/small/`.
- r23–r24: at the street the houses' walls and roofs take none of the look's brushwork (`town.json`, houseBrush): a wall is one coat, its mark its weatherboards' laps and a roof's its courses, near only; panes are dark glass, soft in sheen, or curtained in one window in two (`materials/glass.json`). Small stills in `r24/small/`.
- r25: a house built to the room its plot has (shallower, then narrower) before it is left out, so the old lanes fill to joined rows (119 houses, from 106); relaid roofs keep part of their tiles' weathering (`materials/*.json`, relaidKeeps), so roofs sit below the walls; the water's crests gentler and straighter, a quiet mirror with its reflections under the sjøhus; the city camera keyed to a white wall in the sun (`town.json`, camera); chimneys a stack's size. Small stills in `r25/small/`.
