# Masters of colour: what they do that we can build

Øystein (20 October): stylise more, exaggerate, but keep it truly stunning; look to the true masters of colour, in painting and in film. This note is what they do, put as rules our light and grade can carry. It is an input to the design (`docs/visual-direction.md`, Light and colour, Mood), not a decision; the looks built from it are judged in the engine.

## Who, and what we take

**Painters of harbours, lamplight and dusk: our subject, painted.**
- *John Atkinson Grimshaw* (Leeds, 1836–1893): docks, quays and wet streets at dusk and by moonlight; gaslight in mist, every lamp doubled in wet stone, a sky of green-grey against umber darks. Take: the wet street as a second image of the lights, and a narrow palette of olive, umber and gold. The closest painter to our harbour at 17:50.
- *James McNeill Whistler*, the Nocturnes (Battersea, Valparaíso harbour): a few close values of blue, lamps as small points of gold; the picture is the air. Take: values compressed into a narrow band, distance as tone, restraint.
- *Eugène Jansson*: Stockholm's water and quays at night, in blues. Take: a Nordic harbour city carried by one blue, its lights strung along the water.
- *Harald Sohlberg* (Winter Night in the Mountains): a deep saturated blue night, big simple shapes, one small light. Take: saturated darks, not grey ones; masses before detail.
- *Kawase Hasui*: woodblock prints of rain, snow and lamplight; flat graded skies, light in puddles. Take: graded flat air, rain and snow as shapes.
- *Edward Hopper*: hard light as shapes on simple planes, lit rooms seen from the street at night. Take: light shapes designed, interiors as accents.

**Painters of light and coloured shadow.**
- *Joaquín Sorolla*, *John Singer Sargent*: sunlit white full of colour, shadows saturated and cool, the most intense colour where light turns into shade. Take: coloured, full-chroma shade, and a warm saturated band at the turning edge.
- *Claude Monet*'s series (the cathedral, the haystacks at each hour): one subject, the colour of the light changing everything. Take: the same view across hours is a colour study; our cameras across the colour script are that.
- *J. M. W. Turner*: atmosphere as the subject, form dissolving in light. Take: let the air carry the frame when the moment earns it (fog, low sun into haze).

**Stylists and colour scripts.**
- *Eyvind Earle*, *Mary Blair*: designed palettes, flat value masses, colour that shifts by value (darks to violet, lights to gold). Take: a gradient of colour by value as a designed ramp.
- *Pixar's colour scripts* (Ralph Eggleston, Lou Romano, Sharon Calahan as director of photography): the film's colour planned as an emotional arc, one key per sequence. Take: one colour key per scene, and the sequence of keys as the story's arc.
- *Kazuo Oga* (Ghibli backgrounds), *Makoto Shinkai*: luminous skies, saturated air, glow round light, the ordinary made radiant. Take: exaggerated glow and sky, and the light bleeding into the air round it.
- *Firewatch* (Olly Moss, Jane Ng): distance in flat layers of colour, the sky set by artists. Take: air laid in steps, each a designed colour.

**Cinematographers.**
- *Roger Deakins* (Blade Runner 2049, Skyfall, 1917): one dominant hue per scene, haze to shape light, silhouettes against light. Take: monochrome air with one accent; backlight through haze.
- *Vittorio Storaro*: colour as meaning, changing with the story. Take: the mood's colour belongs to the moment, and changes with it.
- *Christopher Doyle* (In the Mood for Love), *Greig Fraser* (The Batman, sodium orange), *Bradford Young* (Arrival, soft and low): saturated practical light, a whole film in one or two hues, underexposure as mood. Take: the town's own lights (sodium, lanterns, windows) as the palette at night.
- *Emmanuel Lubezki*: natural light at its best moments, magic hour. Take: the facts choose the hour; the camera chooses the moment in it.
- Film's own response (print film): rich colour in the middle tones, colour falling away towards black and towards white, a soft shoulder on the highlights. Take: chroma that rolls off at the ends of the value range.

## The rules

1. **A key, not a filter.** Each scene has one colour key: a dominant colour of air and shade, one warm accent of light, and a value plan. It comes from the hour and the weather, pushed by the style and the mood.
2. **Values in a few masses.** Three or four groups of value; detail inside a group is quiet, edges between groups carry the picture.
3. **Shade has full colour; light is warm and paler at its peak; the turning edge is the most saturated.**
4. **Colour shifts with value.** Darks lean violet or blue, lights lean gold: a designed ramp of colour by value, blended over the scene, never replacing what is a fact (a lit window stays warm; a red sign stays red).
5. **Distance steps back in layers**, each a designed colour, softer than a print and firmer than a photograph.
6. **Light earns glow.** Bright sources bleed their colour into the air and into the lens (halation), most where the air is thick.
7. **Wet doubles the light.** Reflections are a second image of the lights and the sky.
8. **Chroma lives in the middle.** Colour is richest in the middle values and falls away towards black and white, as film's does.
9. **Exaggerate one thing at a time.** A frame pushes colour, or value, or air, not all three; the others hold it up.
10. **Facts are never stylised away.** Whatever the style, the hour, the weather and every light still read true (`docs/visual-direction.md`, Mood).

## What it asks of the engine side

A style layer between the hour's grade and the mood (`Overstory.Scenes.Style`): a ramp of colour by value with its strength and a guard for saturated facts; value grouping; air in layers; the chroma of shade and the warmth of the turning edge; chroma that rolls off at the ends; a tint for the glow. A full-screen pass after the grade applies the ramp, the grouping and the roll-off (`Palette.shader`); the rest are settings of the light. Candidate styles are rendered beside the neutral look on the same frames and judged there.
