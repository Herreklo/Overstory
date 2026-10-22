# Visual direction

The current direction for how the world looks. Look tests decide the open points; `docs/experiments.md` records what each one kept and dropped.

## In short

- **VD1** North Atlantic timber harbour town, Stavanger-rooted, shown from 1989; painterly realism, Stålenhag leading. Silhouettes first; proportions pushed by eye between gentle and strong (disputed), deformation small; no round blobs. Evidence: Identity, Shape. Reopens: look tests; Øystein.
- **VD2** Shade and ambient take the light's colour, never the object's (SEASON); tested in drizzle (the default), low sun, blue hour. Every light is a fact. Four or five values, one darkest dark and one white; middle at most 60% (fog nocturne 75%, keeping both); read in grey at one-eighth size before colour. Evidence: `colour-and-shading.md`. Reopens: none named.
- **VD3** A mood moves only exposure, contrast, shade's chroma, lens; never a light's hue or weather; moods judged blind; `Style_game` the default. Evidence: Mood. Reopens: none named.
- **VD4** Free city camera; walk mode tested in 1g (disputed); street stop 2.5–3 m, 28–35 mm (Øystein); close 12–15 m, middle 35, far 120 m. Evidence: Views. Reopens: look tests.
- **VD5** Parts hold from eye level (1–5 m) to near-isometric (disputed: cost unmeasured); real detail near, painted marks from the street stop. Judged frames hold clay or approved parts; a paintover changes no fact. Evidence: How the look is built. Reopens: per-kind numbers.

## Identity

The world is a fictional **North Atlantic timber harbour town** (VD1): the family that includes the Norwegian west coast, New England, the Maritimes and the Faroes. Painted clapboard, steep gables, white trim, quays with warehouses, wet maritime light, long dusks. It could be several places and is clearly not just anywhere: no Mediterranean stucco, no brick-terrace Britain. Features that pin it to one country are accents, not the identity. The first town is rooted in Stavanger and first shown in 1989. The town is seen in its landscape: a narrow harbour basin with quays on both sides; the old town of white timber houses with red tile roofs on the slopes above it; the newer town beyond in its eras (post-war blocks, offices, the oil industry's tanks and cranes), with a landmark on a rock knoll; then low rocky islands and the open fjord, and mountains only far off. The land is low and rocky, not alpine: its height comes from slopes, knolls and rock faces. The setting is part of every wide picture. The rules engine is reusable across regions, but each region still needs real work on its own assets and data: building eras, regulations, geography, clothes, vehicles and signage.

The style is ours. It does not follow the cosy stylised-Unity look or AI-art trends. It is found in look tests and judged in Unity. Target frames, painted over our own Unity renders, set the bar; they are never the judgement.

The direction is painterly realism. Simon Stålenhag leads: real proportions, muted natural colour with one accent, heavy atmosphere, loose painted edges, the mundane made beautiful, grey days and dusk. Alongside him: Hopper (hard low sun on simple planes, lit rooms at night), Hammershøi (quiet grey light, few colours), Disco Elysium (a painted city in decline, visible brushwork) and Kawase Hasui's Tokyo prints (night, rain, lamplight in wet streets). It must hold from a village to a metropolis (in time, other towns and cities as large as London or New York), so it lives in light, air, shape discipline and generated surfaces, never in per-asset cartoon art; each setting brings its own parts under the same rules. Step by step: the style is nailed in one corner first. Not a cartoon village.

## Shape

- Shapes carry the style; shading finishes it. Silhouettes first: every building has its own outline from its volumes, roofs, chimneys and additions.
- Real proportions, exaggerated (VD1): the base is real, and the push (a steeper roof, a deeper eave, a bigger chimney, tall-and-narrow next to low-and-wide) is welcome as long as the town reads as a place, never as a toy. The push is chosen by eye in the beauty corner, between the strengths called gentle and strong. Deformation (lean, sag, bow) stays small, because it is what reads as caricature.
- A handmade feel from the seed: a lean, a sagging ridge, windows slightly out of line, soft bevels. The wobble lives inside each piece; edges stay on the grid.
- Detail where history is. Calm walls; rich junctions, signs, trims and traces of change. Human scale, never miniature.
- No round blobs. Shapes are considered and structured: planes, edges and silhouettes with intent, as a painter builds a tree or a roof, never a soft ball standing in for a form. Rounded, puffy shapes are the generic stylised look, not ours.
- Fewer things, each done well, beat many things done roughly.

## Materials

Mostly painted timber, with brick, stone and concrete where era, purpose, wealth or rules put them: brick canneries and a masonry belt from fire rules, stone banks and churches, functionalist render, oil-era concrete and glass. Landmarks tend to be the masonry ones. Each material ages in its own way.

## Areas

The town is made of areas, each with its own grain: what stands there, how close, on what ground.
- The waterfront: flat, made ground at the water. Quays, warehouses, workshops and shops with open, lit ground floors; the work's own clutter only where work happens. The densest and busiest area, and the one whose uses turn over fastest.
- The hill: houses on rock, in rows that follow the contours, with lanes, steps, yards, walls and trees between them, looser as it climbs.
- The crown: the high rock, where landmarks stand behind their walls (a church, a merchant's house), seen against the land. It makes the town's silhouette.
- The land beyond: heath, forest, mountains and the fjord, in layers of air.
- Roads wind round the rock rather than cutting through it. Areas meet at seams (a lane leaving the quay, a road climbing round a cliff), and the seams are where the town reads best.
- Areas change at their own speed as the town grows from village to city: the waterfront's uses turn over, the hill fills in, new areas grow at the edges. The town is a working town, not a postcard fishing village.

## Ground and nature

- The town stands on rock and climbs. Height difference is everywhere: lanes in flights of steps, houses on plinths that take up the slope, walls holding yards, bedrock breaking through where it was too hard to cut. Level ground is made (quays, yards, terraces) and shows it.
- Space between the houses is designed, not left over: lanes, alleys, gaps between neighbours, and small level places where lanes meet, even on the steepest ground. That is where light falls and people stop (Cullen's here and there).
- Nature is in every frame, not decoration around the town: bedrock, heath, moss, grass in the joints, self-seeded trees.
- Nature has a history, like a building, and changes with the years. Trees grow from their planting or seeding year; heath left ungrazed goes to juniper and birch; an empty yard grows over within a few summers; a busy step wears smooth while its quiet edge grows moss; lichen size shows how long stone has been bare (`docs/research/nature.md`). The same rule as for buildings holds: what reads as history must be a fact with a date.
- Rock is built in deliberate planes (Another World); ground cover in clusters with edges, never noise.

## Light and colour

- Light is the identity. The coast's daylight (grey drizzle, low winter sun, a blue hour that lasts, and hot summer days of thirty degrees with warm, golden light) and the light of the night (warm windows, street lamps by era, neon, stage light in haze). Warm light belongs to this place as much as cold; the look is not "Nordic" grey.
- Light is dramatic. In sun: deep shadow with little fill, coloured by the sky, and light rays where the sun streams past roofs and trees. At night: darker, with the town's own lights bright, casting real shadows, and lit rooms spilling warm light onto the lanes in front of them.
- Light follows a colour script keyed to facts: the date, hour and place set the sun (computed, never typed: `Daylight.cs`), the weather sets the cloud, the fog and the wet, the season the rest. The west coast's year is part of the identity: December's short blue days, June's light nights, October's low gold under cloud. Strong colour is for the moments that earn it; ordinary light must stand on its own.
- Physics underneath, art direction on top. The physics says where light comes from and what it falls on; the colour script chooses the palette: one dominant colour of air that carries the mood, one warm accent against it, little else.
- Every light in the town is a fact. Lamps are the kind their street was lit with (the old town's lanterns of 1955, warm; mercury of the 1960s; sodium of the 1970s on the quays and main streets; the harbour's red and white lights); lit windows, shops and signs are who is in and what is open at that hour. They are the warm accents, and they show where life is.
- The sky is designed from the hour and the weather, not generated noise: a gradient that darkens to the zenith and glows low at the sun's bearing, two or three bands of cloud flattened towards the horizon, their undersides caught by the last light or by the town's glow. Every material and tree is judged against it.
- Windows and lamps light the world round them: light spills from a lit window onto its reveal, the wall and the pavement; each window differs a little in warmth and brightness (seeded texture, claiming nothing); fog softens lamps and windows alike, and a lamp's halo grows larger and softer the more fog lies between. The lamps' eras read apart: sodium orange, incandescent warm white, mercury blue-green.
- Fog is a bank, not a filter: thick over the cold water, thinner over the land, roofs coming through it, the glow of lit streets in it.
- Shade sees the town. A sky map of the town, its height seen from above and redrawn whenever the town changes (`SkyMap.cs`), tells each point how much sky it sees: lanes, yards and the feet of walls darken, roofs and quays stay open, and the hidden sky is replaced by the town's own bounce. Shade takes the colour of the part of the sky it faces: warm towards the sun, cool away from it, blue from overhead.
- Drizzle is the default and the hardest test. The town must be beautiful in flat grey light, where the sky is the key light.
- Shadow and ambient colour come from the light, never from the object (VD2). Shadows go cool, not black.
- Value first (VD2): every frame is designed as four or five values before any colour: one darkest dark, one white (a light that means people), the middle no more than about sixty percent of the frame (a fog nocturne may hold up to about three quarters in a narrow middle band, as Whistler's do, so long as it keeps its one dark and its one white). It must read in greyscale at one-eighth size before colour is judged. Extreme lights and darks are kept for edges, highlights and windows; the nearest unlit mass is usually the darkest.
- Chroma is placed, not spread: richest at the focus, where the light that means people is, and drained elsewhere; shade cool and light warm at the focus.
- Muted base, small saturated accents: lit windows, signs, boats, stage light.
- White stays white: it shifts temperature with the light, never drops to grey.
- Atmosphere does distance: air in coloured layers (near, middle, far), and a low haze or sea fog that lies on the water and thins up the hill, so the hills stand out of it and distance steps back in flat layers of value. Fog and dusk are first-class, not exceptions. Each lamp lights the air round it with a halo, thrown forward as fog droplets throw it (`FogLights.shader`).
- Weather wets what it wets: paving darkens and shines, puddles lie only on paved ground, the town's lights glint in it.
- Neutral tonemapping with our own grade; windows and stage lights are bright emissives.
- Every colour difference also shows in value, pattern or wear, so it reads for colour-blind players.

## Mood

One style carries every atmosphere a story needs: sad, hopeless, gritty, hopeful, grand, success; in rain, wind, sun and snow; through the seasons. The mood comes first from what is true in the world (a struggling bar in drizzle, a family kitchen at blue hour, market day, a sold-out gig, sea fog on a Friday evening); then from how the scene is filmed.

The game's style sits between the light and the mood: how far colour, value and air are pushed beyond what the light gives, after the masters of colour (`docs/research/masters-of-colour.md`). It takes its hues from the hour's own light and pushes them, never replaces them; it spares saturated light, so a lit window stays warm. The direction (Øystein, 20 October): painted's restraint in chroma as the system, luminous's warm and cool split at the focus, nocturne's handling of fog. That is Stålenhag and Hopper: strong value, moderate chroma, one warm accent. The style built to that direction (`Style_game`) is the game's default (Øystein, 20 October); its numbers are refined in the frames.

Grading has four layers, each with one owner (VD3): exposure (the eye adjusting to the hour, from the light), the hour's balance (the camera stays balanced for daylight, so blue hour is blue and lamps are orange), the mood, and the lens (grain, glow round bright light, vignette). A mood moves only exposure, contrast and how much colour the shade keeps, and the lens; never the hue of a light, and nothing that reads as weather (thicker fog, blacks lifted into haze). So a mood can never change a fact: it cannot make night day, fog clear or a lit window dark; it only chooses how what is there is seen, as a cinematographer does. The moods are written as recipes until target paintings give their looks: a frame graded in a paint program with a reference strip in it becomes the game's lookup table, exactly. A mood is chosen per scene by the game's direction and blends over a few seconds. Moods are judged blind: a viewer names each, and reads the same weather, hour and lights in all of them. Intensity follows what is happening, like a film's colour script. Motion follows mood too: environment effects step on twos; what carries no fact stays still.

## Views

- The city view (VD4): a free perspective camera over the live town, navigated rather than staged: a city-builder's free camera (Cities: Skylines), but closer to the town (Øystein, 22 October). It is the main way to roam; eye level is the bottom of its range and where scenes play, never a switch to walking a person. It belongs inside the town, close enough to see the details and feel the place: it runs continuously from just above head height in a lane, where the player moves through the town, up past the roofs to the map. It follows the space under it: low along lanes, over quays and squares, higher over roofs. The player moves through the town as this free camera, not as a person they walk; what they do happens in scenes entered through doors. Most of the time it is among the houses, looking along lanes and streets, not at the town from a distance. Its tilt follows its zoom: steep and map-like when pulled out to navigate, the horizon in frame in the middle, just over the rooftops close in. Shots are composed: a near frame, a lit middle ground, a glimpse beyond (Another World, Cullen's here and there). Silhouettes, Lynch's paths, edges, districts, nodes and landmarks must read from it. The camera is designed early; it is part of the style.
- Every look is judged from the game's camera. Target frames and sheets use the city view's own stops, lens and tilt, never a place the player cannot put the camera. The player turns the camera any way, so a place is finished in the round as far as the camera can see, and a composed frame is checked against a strip of headings. Close in, the camera sees fronts and ground as much as roofs, because that is where history is read.
- Scene views: bounded, walkable, staged like a film or theatre set, every light motivated by a real source. Moving between views is a cut or a short move through a doorway.

## Open, decided by look tests

- The city camera (VD4): its zoom stops, tilt and lens (LT1). First values, judged in the beauty corner: the street stop 2.5 to 3 m over a lane or square with a 28 to 35 mm lens, gliding along it (decided, Øystein, 20 October: parts are made at the scale that reads from there); the close stop 12 to 15 m above the ground, just over the ridges, with the horizon in frame; the middle stop about 35 m; the far stop about 120 m, steep and map-like; a 35 mm lens close in (about 38° vertical), longer when pulled out, so the town flattens towards a map.
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
- **True up close, painted from afar** (Øystein, 22 October: "find our style, not only copy references... there might be a middle ground"). Within a couple of metres the real detail stays, as craft: lichen with its lobed, crumbling edge and crust, cement with its sand, moss in cushions, each mark still one shape. From the street stop up, the same facts are drawn as a few soft painted marks per thing, and light and air carry the image (the history budget, `docs/living-fabric.md`). The shaders fade one into the other by how much surface a pixel covers (`OS_Near`, `Growth.hlsl`), so no part needs two versions. Fully painted, a part goes soft and out of focus at eye level; fully detailed, it speckles from afar (`reviews/lt1/stone/gully/style-compare-*.png`).
- One focal point per frame, where the strongest value contrast, the hardest edge and the accent colour meet.
- A muted base, with light and air giving the colour.
- Painted rather than textured surfaces: calm areas and detail at edges and junctions. A brush mark has a size in the world, the same on every object, and never tiles visibly.
- One shading model and one air for everything: shade takes its colour from the light, never from the object (no material carries its own shadow tint).
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

**Final quality holds from eye level to the city camera's raised views** (VD5). A part is superb only if it holds up at eye level, a person's height in a lane with the part one to five metres away (Øystein, 22 October: so the camera can come down into the lanes, the game can be played in more ways, and the town's own parts are the sets for scenes played outdoors); a few metres away from the street stop; and from the city camera as the player roams: just over the ridges looking into it (about 12 m up), from the roofs, and higher and steeper as the camera pulls out, up to a near-isometric view, which is a main view: the player roams the town as the camera, usually without a character (Øystein, 21 October: everything has to look very nice from these views as well; close to isometric has to look great). The camera favours side views where it can (its tilt flatter near the ground), rather than every part being forced to look its best from straight down (Øystein, 22 October). Parts are judged from all of them. Close detail lives in a near tier drawn only round the camera (real leaves where a tree's cards would turn as you pass, finer bark and stone, the foot of a tree or a wall meeting the ground), so the town still holds its frame rate.

**Final quality is defined before it is built** (VD5). Three to five target frames, painted over clay renders of the beauty corner (one matte grey, from the game's cameras), show what final looks like, where a painter's hand is there to paint them. Where it is not (Claude makes everything, Øystein curates), light, value and colour are set by the masters and by value plans studied over the clay, and forms and materials by each part's reference board: a paintover in code cannot paint forms onto boxes (it reads as Minecraft; `docs/experiments.md`, LT1, the first target frame), so the corner built from approved parts is the first full target. A frame shown for judgement holds clay or approved parts, never placeholders: a frame full of placeholders cannot be judged. A paintover may change light, air, surfaces, detail and the forms of parts; it may not change a fact (which houses stand there, their eras and histories). Everything built so far, the house generator included, is test quality: programmer art, boxes from Python. Final quality is a render that holds up beside its target frame from the same camera.

**The beauty corner** is where final quality is reached first. Its layout is made with the same care as a part: blocked in by hand at the density of the place it stands for, judged in clay, and then the generator's layout rules are learned from it. one lane over rock, five houses, two trees, the ground's own cover, a wall and a lamp, in one light, from fixed cameras. Nothing scales to the town until the corner holds up beside its targets. Every new element is judged in the corner, so it belongs with the rest.

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
