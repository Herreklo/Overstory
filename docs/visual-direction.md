# Visual direction

The current direction for how the world looks. Look tests decide the open points; `docs/experiments.md` records what each one kept and dropped.

## Identity

The world is a fictional **North Atlantic timber harbour town**: the family that includes the Norwegian west coast, New England, the Maritimes and the Faroes. Painted clapboard, steep gables, white trim, quays with warehouses, wet maritime light, long dusks. It could be several places and is clearly not just anywhere: no Mediterranean stucco, no brick-terrace Britain. Features that pin it to one country are accents, not the identity. The first town is rooted in Stavanger and first shown in 1989. The town is seen in its landscape: it steps up from the quay, with hills, mountains and the fjord behind, and the setting is part of every wide picture. The rules engine is reusable across regions, but each region still needs real work on its own assets and data: building eras, regulations, geography, clothes, vehicles and signage.

The style is ours. It does not follow the cosy stylised-Unity look or AI-art trends. It is found in look tests and judged in Unity. Target frames, painted over our own Unity renders, set the bar; they are never the judgement.

The direction is painterly realism. Simon Stålenhag leads: real proportions, muted natural colour with one accent, heavy atmosphere, loose painted edges, the mundane made beautiful, grey days and dusk. Alongside him: Hopper (hard low sun on simple planes, lit rooms at night), Hammershøi (quiet grey light, few colours), Disco Elysium (a painted city in decline, visible brushwork) and Kawase Hasui's Tokyo prints (night, rain, lamplight in wet streets). It must hold from a small town to a large city, so it lives in light, air and generated surfaces, never in per-asset cartoon art. Not a cartoon village.

## Shape

- Shapes carry the style; shading finishes it. Silhouettes first: every building has its own outline from its volumes, roofs, chimneys and additions.
- Real proportions, exaggerated: the base is real, and the push (a steeper roof, a deeper eave, a bigger chimney, tall-and-narrow next to low-and-wide) is welcome as long as the town reads as a place, never as a toy. The push is chosen by eye in the beauty corner, between the strengths called gentle and strong. Deformation (lean, sag, bow) stays small, because it is what reads as caricature.
- A handmade feel from the seed: a lean, a sagging ridge, windows slightly out of line, soft bevels. The wobble lives inside each piece; edges stay on the grid.
- Detail where history is. Calm walls; rich junctions, signs, trims and traces of change. Human scale, never miniature.
- No round blobs. Shapes are considered and structured: planes, edges and silhouettes with intent, as a painter builds a tree or a roof, never a soft ball standing in for a form. Rounded, puffy shapes are the generic stylised look, not ours.
- Fewer things, each done well, beat many things done roughly.

## Materials

Mostly painted timber, with brick, stone and concrete where era, purpose, wealth or rules put them: brick canneries and a masonry belt from fire rules, stone banks and churches, functionalist render, oil-era concrete and glass. Landmarks tend to be the masonry ones. Each material ages in its own way.

## Ground and nature

- The town stands on rock and climbs. Height difference is everywhere: lanes in flights of steps, houses on plinths that take up the slope, walls holding yards, bedrock breaking through where it was too hard to cut. Level ground is made (quays, yards, terraces) and shows it.
- Nature is in every frame, not decoration around the town: bedrock, heath, moss, grass in the joints, self-seeded trees.
- Nature has a history, like a building, and changes with the years. Trees grow from their planting or seeding year; heath left ungrazed goes to juniper and birch; an empty yard grows over within a few summers; a busy step wears smooth while its quiet edge grows moss; lichen size shows how long stone has been bare (`docs/research/nature.md`). The same rule as for buildings holds: what reads as history must be a fact with a date.
- Rock is built in deliberate planes (Another World); ground cover in clusters with edges, never noise.

## Light and colour

- Light is the identity. The coast's daylight (grey drizzle, low winter sun, a blue hour that lasts, and hot summer days of thirty degrees with warm, golden light) and the light of the night (warm windows, street lamps by era, neon, stage light in haze). Warm light belongs to this place as much as cold; the look is not "Nordic" grey.
- Light is dramatic. In sun: deep shadow with little fill, coloured by the sky, and light rays where the sun streams past roofs and trees. At night: darker, with the town's own lights bright, casting real shadows, and lit rooms spilling warm light onto the lanes in front of them.
- Light follows a colour script keyed to facts: the date and hour set the sun's height and colour, the weather sets the cloud. The west coast's year is part of the identity: December's short blue days, June's light nights, October's low gold under cloud. Strong colour is for the moments that earn it; ordinary light must stand on its own.
- Drizzle is the default and the hardest test. The town must be beautiful in flat grey light, where the sky is the key light.
- Shadow and ambient colour come from the light, never from the object. Shadows go cool, not black.
- Value first: every frame reads in greyscale; extreme lights and darks are kept for edges, highlights and windows.
- Muted base, small saturated accents: lit windows, signs, boats, stage light.
- White stays white: it shifts temperature with the light, never drops to grey.
- Atmosphere does distance: aerial perspective and height fog of our own.
- Neutral tonemapping with our own grade; windows and stage lights are bright emissives.
- Every colour difference also shows in value, pattern or wear, so it reads for colour-blind players.

## Mood

One style carries a range of moods: moody, cozy, alive, glam. The mood comes from what is true in the world (a struggling bar in drizzle, a family kitchen at blue hour, market day, a sold-out gig) through one mood manager that blends sun, sky, fog, ambient light and grade. Intensity follows what is happening, like a film's colour script. Motion follows mood too: environment effects step on twos; what carries no fact stays still.

## Views

- The city view: a free perspective camera over the live town, navigated rather than staged. It belongs inside the town: most of the time at roof height among the houses, looking along lanes and streets, not at the town from a distance. Its tilt follows its zoom: steep and map-like when pulled out to navigate, the horizon in frame in the middle, just over the rooftops close in. Shots are composed: a near frame, a lit middle ground, a glimpse beyond (Another World, Cullen's here and there). Silhouettes, Lynch's paths, edges, districts, nodes and landmarks must read from it. The camera is designed early; it is part of the style.
- Every look is judged from the game's camera. Target frames and sheets use the city view's own stops, lens and tilt, never a place the player cannot put the camera. The player turns the camera any way, so a place is finished in the round as far as the camera can see, and a composed frame is checked against a strip of headings. Close in, the camera sees fronts and ground as much as roofs, because that is where history is read.
- Scene views: bounded, walkable, staged like a film or theatre set, every light motivated by a real source. Moving between views is a cut or a short move through a doorway.

## Open, decided by look tests

- The city camera: its zoom stops, tilt and lens (LT1). First values, judged in the beauty corner: the close stop 12 to 15 m above the ground, just over the ridges, with the horizon in frame; the middle stop about 35 m; the far stop about 120 m, steep and map-like; a 35 mm lens close in (about 38° vertical), longer when pulled out, so the town flattens towards a map.
- The shading model: painted ramp against plain URP Lit as a control, soft toon and graphic if needed (LT1).
- The colour script through the day and the year (LT1).
- How visible history should be: ghost signs, wear, mismatched additions (LT3).
- People: stylisation, faces, animation (LT2 and the people deep dive).

## How the look is built

One style, its rules shared by every element; each element learned from its own lead reference, built and judged one at a time, in the beauty corner, against target frames.

**The rules every element must pass:**
- Deliberate planes and crisp silhouettes, never round blobs (Another World's discipline). A form reads first as one big shape, then a few medium ones, then small detail gathered in clusters, with calm areas between.
- Realistically exaggerated proportions.
- Three to five values per frame, reading in greyscale and at thumbnail size.
- Light and shadow stay two families: nothing in shadow is as light as anything in sun, and nothing in sun as dark as anything in shadow. Bounce lifts a shadow; it never brings it up to the light.
- Edges are chosen: hard where a lit plane turns into shadow and where a silhouette meets the sky; soft or lost inside shadow, in foliage and with distance. No drawn outlines: edges come from value and colour.
- Detail lives in the light and near the focal point. Shadows and distance are simplified, as a painter leaves them.
- One focal point per frame, where the strongest value contrast, the hardest edge and the accent colour meet.
- A muted base, with light and air giving the colour.
- Painted rather than textured surfaces: calm areas and detail at edges and junctions. A brush mark has a size in the world, the same on every object, and never tiles visibly.
- One shading model and one air for everything.
- Fewer things, each done well.

**Lead reference per element:**

| Element | Lead | Support |
| --- | --- | --- |
| Trees | Firewatch | Kazuo Oga (Ghibli backgrounds), Stålenhag |
| Rocks and cliffs | Another World | Firewatch, Norwegian coast photographs |
| Water | Kawase Hasui | Firewatch, Stålenhag |
| Sky | Firewatch | Sohlberg, Astrup |
| Roads and paths | Stålenhag | Disco Elysium |
| Moss and ground cover | Kazuo Oga | Firewatch |
| Buildings | Stålenhag, Hopper | the house generator |
| The town at night | Hasui, Hopper | Stålenhag |

**Final quality is defined before it is built.** Three to five target frames, painted over our own Unity renders of the beauty corner, show what final looks like. A paintover may change light, air, surfaces, detail and the forms of parts; it may not change a fact (which houses stand there, their eras and histories). Everything built so far, the house generator included, is test quality: programmer art, boxes from Python. Final quality is a render that holds up beside its target frame from the same camera.

**The beauty corner** is where final quality is reached first: one lane over rock, five houses, two trees, the ground's own cover, a wall and a lamp, in one light, from fixed cameras. Nothing scales to the town until the corner holds up beside its targets. Every new element is judged in the corner, so it belongs with the rest.

**Parts are made with care, one at a time.** Each part (house trims, windows and doors, a tree, a rock) is built in Blender against its reference board, shaped by eye rather than written as quick generator code. The generator chooses, fits, places and seeds approved parts; it does not invent their geometry. Because the world changes (villages grow into towns and cities, people open shops and cafés in old ground floors and close them, houses are extended and reclad), a part is made to fit the assembly rules: its era, its sockets and the range of sizes it must fit. A part that only fits one house in one frame is not done. The process, per part: a reference board (`docs/references/<element>/`, images for private study only); a note on what makes the references work; a written target Øystein agrees with; the part, built; a sheet in the corner's light, in greyscale and at thumbnail size; checks and a fresh reviewer; Øystein's judgement. Only then does it join the corner.

**Roles.** Øystein is the art director: he judges every part and every frame. Claude is the technical artist: shaders, light and air, assembly rules, tools, and the parts themselves, built to his targets.

## References

What we take and leave from each is recorded in `docs/experiments.md` as look tests meet them.

| Reference | What interests us |
| --- | --- |
| Simon Stålenhag (lead) | Painterly realism, muted colour, atmosphere, the mundane 1980s Scandinavia |
| Another World (Éric Chahi) | Shape from deliberate planes, silhouettes, a few values per screen, light as shape, composed shots |
| SEASON: A letter to the future | Light-derived shadow colour, authored atmosphere |
| Firewatch | Colour in depth layers, an artist-driven sky |
| Sable | Fog as the first readability tool, outlines that fade |
| Team Fortress 2 | Readable value and colour rules |
| Townscaper, Tiny Glade | Harmony from rules, detail at junctions |
| Kiki's Delivery Service | A harbour town, pushed proportions, life clutter |
| Disco Elysium | History visible in every wall |
| Kentucky Route Zero | Theatrical staging and light |
| Clay renders of a stylised European town | Flair from shape alone |
| Hopper, Hammershøi, Sohlberg, Astrup | Lit windows, grey light, the blue night, flat wet colour |
