# Colour and shading

How colour and shading should work in our world, drawn from painting, film, animation and games. Part of the Game Lab research.

## The core rules

1. Shadow and ambient colour come from the light, never from the object. SEASON's first shader gave each material its own shadow tint; it "couldn't adapt to lighting changes", so every time-of-day change meant hand edits. They moved to shadow colour derived from the light. Our weather and decades change constantly, so this is non-negotiable.
2. In drizzle the sky is the key light. Toon and ramp shading usually only shade the sun term (N·L), which goes flat when there is no sun. Our shading must also stylise the sky term: a hemisphere light from sky, horizon and ground colours, on the surface's facing (N·up), the way Team Fortress 2's ambient cube does. This is the test none of our reference games faced.
3. Value first. Every frame must read in greyscale. Extreme lights and darks are kept for edges, highlights and windows (Team Fortress 2; Gooch et al.).
4. Shadows go cool, not black. Team Fortress 2's rule, and the painters' observation that shadows take the colour of the sky.
5. Muted base, small saturated accents. Team Fortress 2: "muted colors dominating and small areas of saturation". Our saturation budget goes to lit windows, signs, boats and stage light.
6. White must stay white. Sorolla painted a sunlit white sail "butter yellow" and the same white in shade "dirty blue". Our white houses shift temperature with the light but never drop into mid-grey. That is the drizzle test.
7. Mood is the colour of light and air, scaled by what is happening. Pixar's colour scripts: "the colors got more intense when the emotions were more intense." Our version is driven by simulation facts, not a storyboard. Vittorio Storaro gave two characters' worlds two light colours; mood lives in light, not materials.
8. Atmosphere does distance. Aerial perspective and fog; lines fade with distance (Sable, SEASON, Firewatch).
9. Neutral tonemapping, our own grade, bright emissives. URP offers None, Neutral and ACES, and no native AgX. Neutral changes hue and saturation least and suits heavy grading; ACES is reported to push bright blues toward magenta, which would hurt stage light. Windows and stage lights are emissive at several times normal brightness, so the glow comes from light, not from bright paint.
10. Every colour difference has a second channel. Era, wealth and neglect also show in value, pattern or wear, so they read for colour-blind players (Xbox accessibility guidelines).

## Building palettes

- One person owns the palette, as Mary Blair and Eyvind Earle did for whole films.
- Era palettes as short pigment lists stored in OKLCH (a colour space where lightness, colour strength and hue change independently), with paint age as a drift in strength and lightness.
- Place palettes: a small hue range per district; wear and wealth shift strength and value only, never hue.
- Temperature and mood are left to light and atmosphere.
- Avoiding mud: muddy overcast scenes come from low value contrast and grey-brown base colours. Keep some colour strength in the base, keep darks cool, separate distance with fog.
- Avoiding sugary cosiness: that comes from saturated base colours under warm light. Cap strength per material and spend it on accents.

## Lessons by source

- Hammershøi built beauty from greys "from blue to ash" and believed colour works best "the fewer colours there are". Proof that an overcast palette can be beautiful.
- Sohlberg spent about 15 years on one cold blue night. The blue hour can carry one hue at low value.
- Astrup hand-painted each impression of his woodcuts, so every print from the same blocks is different. That is our generator: one base, each building's history its own impression.
- Hopper: "What I wanted to do was to paint sunlight on the side of a house." Low winter sun is the event that earns hard light on facades.
- Klaus painted up to eight light layers over 2D drawings and kept lines "only where they conveyed information". Value can do the work of outlines.
- Spider-Verse let halftone density follow the lighting. Any graphic texture we use should be driven by light, not painted per object.
- Wolfwalkers drew the town with a rigid, blocky line and the forest with a loose one. Line quality and colour strength can carry a fact about a place.
- Teal and orange grading has become a generic blockbuster look. Our warm and cool must come from real lights, never a global split.
- Journey and **Gris** let colour follow the story's arc. Gris starts without colour and unlocks it.
- Obra Dinn works in two colours because its value structure is strong.

## Shading catalogue

| Model | Look | Strengths | Weaknesses | In overcast light |
| --- | --- | --- | --- | --- |
| URP Lit (control) | Soft, realistic | Correct under any light | Generic | Good form, dull mood |
| Half-Lambert, wrap | Soft, full form | Nothing goes dead black | Low contrast | Fair |
| Warped ramp (TF2) | Illustrative, shaped edge between light and shadow | Global control in one ramp | The ramp must stay light-driven | Good if the sky term is shaped too |
| Soft toon | Two soft bands | Calm, clean | Flat when the sun is weak | Poor unless the sky term is stepped too |
| Hard cel with authored normals (Guilty Gear Xrd) | Crisp, anime | Strong graphic read | Hand-edited normals don't suit generators | Poor |
| Gooch warm-cool | Form through hue shift | Form without dark values | Fixed hues fight changing light | Good if warm and cool come from sun and sky colours |
| Flat with outlines (Sable) | Graphic, comic | Readable, cheap | Depth depends on fog and shadow | Fair with fog |
| Dither or hatch (Obra Dinn) | Printmaking | Distinctive with few colours | Swims unless fixed to the world | Good for value |
| Painterly stroke texture | Brushed | Handmade feel | Swims; baked light breaks | Fair |
| Stylised AO and fake bounce | Soft contact shadows | Grounds buildings in flat light | Screen-space halos | Essential |

## The first look test

Held equal for every look: the palette texture, one light rig per weather (sun colour and strength; sky, horizon and ground colours feeding a hemisphere light), the same shadows and ambient occlusion, the same fog, Neutral tonemapping with one shared grade, and bright window emissives.

| Look | Shading | Lines | What it tests |
| --- | --- | --- | --- |
| A. Control | URP Lit, matt | None | Does stylisation earn its cost? |
| B. Painted ramp | Half-Lambert through one global ramp, times sun colour; the sky term shaped the same way; a little extra colour at the shadow edge; a world-fixed stroke texture nudging the ramp | Rim light only | Can illustrated form survive drizzle and stay stable? |
| C. Soft toon | Two soft bands on the sun term, the same two bands on the sky term | None | Is calm and clean beautiful in flat light, or dead? |
| D. Graphic | C with hard steps | Edge lines from depth and normals, thin, dark oxide not black, fading with distance and fog | Do lines and hard shapes make the town readable and ours without the cosy look? |

Judge each in greyscale and colour, across drizzle, low sun, blue hour and night. Check that white paint stays white in every weather and that a neglected house reads as neglected without colour.

## Sources

[TF2 illustrative rendering](https://www.cs.princeton.edu/courses/archive/fall07/cos597B/papers/mitchell-team-fortress.pdf) · [TF2 slides](https://cdn.fastly.steamstatic.com/apps/valve/2007/NPAR07_IllustrativeRenderingInTeamFortress2_Slides.pdf) · [Stylization with a purpose](https://cdn.steamstatic.com/apps/valve/2008/GDC2008_StylizationWithAPurpose_TF2.pdf) · [Shading in Valve's Source engine](https://advances.realtimerendering.com/s2006/Mitchell-ShadingInValvesSourceEngine.pdf) · [Gooch et al. 1998](https://users.cs.northwestern.edu/~bgooch/PDFs/gooch98.pdf) · [Lake et al. 2000](https://isgwww.cs.uni-magdeburg.de/~stefans/npr/entry-Lake-2000-SRT.html) · [Hertzmann 1998](https://mrl.cs.nyu.edu/publications/painterly98/) · [Bénard et al.](https://artis.inrialpes.fr/Publications/2010/BLVLDT10/) · [Guilty Gear Xrd](https://www.ggxrd.com/Motomura_Junya_GuiltyGearXrd.pdf) · [SEASON](https://www.unrealengine.com/en-US/tech-blog/creating-the-illustrative-look-of-season-using-unreal-engine) · [Firewatch sky](https://blog.camposanto.com/post/112703721804/this-blog-post-is-an-in-detail-explanation-of-part) · [Sable](https://www.gamedeveloper.com/marketing/how-shedworks-refined-the-art-of-sable-in-pursuit-of-readability) · [Klaus](https://beforesandafters.com/2019/11/14/heres-what-made-the-2d-animation-in-klaus-look-3d/) · [Spider-Verse](https://www.awn.com/print/animationworld/rewriting-visual-rule-book-spider-man-spider-verse) · [Wolfwalkers](https://awardsradar.com/2021/03/04/interview-wolfwalkers-artists-on-creating-magic-between-the-lines/) · [Pixar colour scripts](https://www.moma.org/audio/playlist/192/2581) · [Storaro](https://theasc.com/articles/whos-afraid-of-red-green-and-blue) · [Hammershøi](https://apollo-magazine.com/vilhelm-hammershoi-jacquemart-andre-paris/) · [Sohlberg](https://www.nasjonalmuseet.no/en/collection/object/NG.M.01185) · [Astrup](https://clarkart.edu/microsites/nikolai-astrup-visions-of-norway/exhibition-(1)/blending-painting-and-print) · [Sorolla](https://spectator.com/article/master-of-white/) · [Hopper](https://www.historynewsnetwork.org/article/184994) · [Journey](https://www.cgw.com/Publications/CGW/2012/Volume-35-Issue-4-June-July-2012/Mysterious-Journey.aspx) · [The Witness](https://www.artofluis.com/wp-content/uploads/2014/03/gdc2014_luisantonio_theartofthewitness.pdf) · [Unity tonemapping](https://docs.unity.com/en-us/engine/6000.3/manual/post-processing-and-full-screen-effects/urp/effect-list/tonemapping) · [Unity ACES thread](https://discussions.unity.com/t/unitys-aces-implementation-is-outdated/1567683) · [Oklab](https://bottosson.github.io/posts/oklab/) · [Xbox accessibility 103](https://devdocs.xbox.com/gaming/accessibility/xbox-accessibility-guidelines/103)
