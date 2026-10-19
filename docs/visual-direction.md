# Visual direction

The current direction for how the world looks. Look tests decide the open points; `docs/experiments.md` records what each one kept and dropped.

## Identity

The world is a fictional **North Atlantic timber harbour town**: the family that includes the Norwegian west coast, New England, the Maritimes and the Faroes. Painted clapboard, steep gables, white trim, quays with warehouses, wet maritime light, long dusks. It could be several places and is clearly not just anywhere: no Mediterranean stucco, no brick-terrace Britain. Features that pin it to one country are accents, not the identity. The first town is rooted in Stavanger and first shown in 1989. The rules engine is reusable across regions, but each region still needs real work on its own assets and data: building eras, regulations, geography, clothes, vehicles and signage.

The style is ours. It does not follow the cosy stylised-Unity look or AI-art trends. It is found in look tests, judged in Unity, never on concept images.

## Shape

- Shapes carry the style; shading finishes it. Silhouettes first: every building has its own outline from its volumes, roofs, chimneys and additions.
- Pushed proportions: steeper roofs, deeper eaves, oversized chimneys, tall-and-narrow next to low-and-wide. How far to push is decided in the LT1 shape step.
- A handmade feel from the seed: a lean, a sagging ridge, windows slightly out of line, soft bevels. The wobble lives inside each piece; edges stay on the grid.
- Detail where history is. Calm walls; rich junctions, signs, trims and traces of change. Human scale, never miniature.

## Materials

Mostly painted timber, with brick, stone and concrete where era, purpose, wealth or rules put them: brick canneries and a masonry belt from fire rules, stone banks and churches, functionalist render, oil-era concrete and glass. Landmarks tend to be the masonry ones. Each material ages in its own way.

## Light and colour

- Light is the identity. Northern daylight (grey drizzle, low winter sun, a blue hour that lasts) and the light of the night (warm windows, street lamps by era, neon, stage light in haze).
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

- The neighbourhood view: a raised camera over a live neighbourhood. Silhouettes, Lynch's paths, edges, districts, nodes and landmarks must read from it. The camera is designed early; it is part of the style.
- Scene views: bounded, walkable, staged like a film or theatre set, every light motivated by a real source. Moving between views is a cut or a short move through a doorway.

## Open, decided by look tests

- How far to push the shapes (LT1 shape step).
- The shading model: painted ramp, soft toon or graphic, against plain URP Lit as a control (LT1).
- How visible history should be: ghost signs, wear, mismatched additions (LT3).
- People: stylisation, faces, animation (LT2 and the people deep dive).

## References

What we take and leave from each is recorded in `docs/experiments.md` as look tests meet them.

| Reference | What interests us |
| --- | --- |
| SEASON: A letter to the future | Light-derived shadow colour, authored atmosphere |
| Firewatch | Colour in depth layers, an artist-driven sky |
| Sable | Fog as the first readability tool, outlines that fade |
| Team Fortress 2 | Readable value and colour rules |
| Townscaper, Tiny Glade | Harmony from rules, detail at junctions |
| Kiki's Delivery Service | A Nordic harbour town, pushed proportions, life clutter |
| Disco Elysium | History visible in every wall |
| Kentucky Route Zero | Theatrical staging and light |
| Clay renders of a stylised European town | Flair from shape alone |
| Hopper, Hammershøi, Sohlberg, Astrup | Lit windows, grey light, the blue night, flat wet colour |
