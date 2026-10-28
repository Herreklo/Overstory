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

## Designed places: production design in film

The sections above are light and air; this one is places and things. It answers the cold critic of the p2 colour still (`reviews/lt1/finish/p2/critic.md`): beige vinyl siding, nothing above chroma 10.

**Who, and what we take.**
- *Wes Anderson*, with Adam Stockhausen and Robert Yeoman. On Moonrise Kingdom every hue of set, prop and costume was chosen, no filter was used, and the grade only warmed and saturated it ([ASC, 2012](https://theasc.com/articles/moonrise-kingdom-cinematography-yeoman)). The Grand Budapest's pink stopped being seen when it was everywhere, so yellows cut it back ([Deadline, 2015](https://deadline.com/2015/02/grand-budapest-hotel-adam-stockhausen-wes-anderson-oscar-nominated-production-design-1201371523/), via [Far Out](https://faroutmagazine.co.uk/wes-anderson-red-yellow-films/), secondary). The 1960s lobby, orange and green, was built inside the 1930s one ([EW via Yahoo](https://www.yahoo.com/news/wes-andersons-production-designer-built-232521463.html)). Take: colour lives in the paint; each era has its palette, a layer over the last, not a fade of it.
- *Jacques Demy*, with Bernard Evein and Jacqueline Moreau. They repainted parts of Cherbourg, a real harbour town, to look more vivid and coordinated than in life, and matched clothes to walls ([Rosenbaum, 1996](https://jonathanrosenbaum.net/2025/08/songs-in-the-key-of-everyday-life/); [AnOther](https://www.anothermag.com/fashion-beauty/11265/the-technicolour-1960s-musical-that-launched-catherine-deneuves-career); both secondary). In Rochefort some 40,000 m² of fronts went white, the shutters left as patches of colour (Berthomé, quoted by [ADC](https://www.adcine.com/news/un-jour-un-decor-31)). Take: white is the ground; colour sits in the small parts, chosen as a set.
- *Roy Andersson*, with István Borbás. Every place is built in his studio, its colours and light planned before shooting; on You, the Living the negative was left unmanipulated ([MUBI](https://mubi.com/notebook/posts/figurative-and-abstract-an-interview-with-roy-andersson)). Shadowless light; scenes condensed as memory condenses ([Film Quarterly, 2015](https://filmquarterly.org/2015/09/24/the-trivialist-cinema-of-roy-andersson-an-interview/)); even floor tiles painted one by one ([Borbás, 2015](https://fourthreefilm.com/2015/06/a-pigeon-sat-on-a-branch-reflecting-on-existence-an-interview-with-cinematographer-istvan-borbas/)). Take: low chroma is not low design; his beige is exact, and value carries the frame.
- *Aki Kaurismäki*, with Timo Salminen. Plain rooms, docks and bars. "Blue-gray is my basic set design color," taken from Melville, plus a red because a red teapot looks good in Ozu; no splendour, nothing too clean ([Film Comment](https://www.filmcomment.com/article/aki-kaurismaki/)). He fixes the composition, then adds few objects and rare colours ([BOMB, 2011](https://bombmagazine.org/articles/2011/10/20/damaged-goods-aki-kaurism%C3%A4ki/)). Take: one base hue for walls, rare saturated accents in small things, wear on everything.

**Rules for the town.**
1. **Few hues per era.** Each era palette in the pack holds about five paints: two whites, two or three body colours (ox-red, ochre, grey-green or Stavangerblå), one accent family. Paint histories pick from it, so the town repeats few hues.
2. **Value under the hue.** Each paint carries its own L*, planned in grey first: whites high, ochre middle, ox-red and dark trim low. Hue never moves the value plan (VD2).
3. **The paint has its own chroma.** Earth paints sit near C* 30 to 45, door greens and blues near 25 to 40 (our estimate, unverified). The grade leans colour; it never supplies what the paint lacks.
4. **White is chosen, not tinted.** Each era's white has its bias (chalk titanium, yellowing linseed, 1980s off-white), high in value. It gets rich from the light (warm sun, sky-blue shade, the turning edge of rule 3 above) and from trim, door and window against it, never from yellow over middle grey.
5. **Accents are rare, small and facts.** A red door, a blue hull, a yellow sign, a lit window. The palette caps their share of a view, and each needs a fact. Rarity makes them seen.
6. **Kept and neglected differ in colour.** Kept: a recent coat at full chroma, clean edges between body and trim. Neglected: chroma falls and drifts (whites to grey, yellow or pink; darks fade: `wooden-town-architecture.md`), edges soften, repairs come in a near-miss white, the old colour showing where it wears.
7. **Shade keeps the paint's hue.** In shade ox-red goes deeper and cooler, white goes sky-blue, never grey (VD2). In flat drizzle and fog, as in Andersson's rooms, palette and values hold the frame alone.
8. **Few things, each chosen.** A budget of props per view (one sign, one boat, one bench), each prop's colour a pack entry.

**Where it would become pastiche.** Not Anderson's centred symmetry, sugared pinks or whimsy; not Demy's candy wallpaper; not Andersson's white faces and tableaux; not Kaurismäki's deadpan or 1950s things in the present. Stavanger in 1989 is mostly white, with colour in the few: ox-red sea houses, some ochre, doors, boats, signs. Pastels belong only to houses repainted in the 1980s, when they were the fashion (Westman, in `house-changes.md`). Every hue comes from the pack and a house's history, never from a film. We take how they work, never how they look.
