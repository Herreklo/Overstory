# People: first survey

A first map of how to make thousands of distinct, stylised people. People get their own deep dive and look tests before LT2; this is the groundwork. Part of the Game Lab research.

## The approach

Don't sculpt people from scratch. Start from a strong base, design the stylisation once by eye, and generate everyone else with parameters that come from facts. Judge one person at a time before any crowd.

## What we can build on

| Asset | Licence | Use |
| --- | --- | --- |
| MakeHuman / MPFB core assets (base mesh, targets, skins) | CC0; exported characters may be sold and used in closed games | Topology and parameter space. Already installed in Blender. |
| Anny (Naver Labs, Nov 2025) | Apache 2.0 | Built on MakeHuman assets; infants to elderly on continuous axes, calibrated to WHO growth data. The ageing axis. |
| Blender Studio Human Base Meshes | CC0 | 17 stylised and realistic base meshes, a starting sculpt |
| Kenney | CC0 | Simple kits |
| Quaternius | Own licence: free in games, never resold as a pack | Base characters and retargetable animation |
| Mixamo | Royalty-free in commercial games | Animation clips; check Adobe's terms on raw redistribution and ML use |
| CMU motion capture | May be used in commercial products, not resold | Reference and base motion |
| SMPL / SMPL-X | Non-commercial only | Not usable |
| Daz, VRoid | Game licence per product; generator clause | Not suitable |

Not yet verified: Reallusion's game licence and the Meta MHR model files.

**Commission one stylised base.** The single best investment is probably a stylised body and head from a character artist, built on MakeHuman/Anny topology so our parameters drive it, plus 8 to 12 extreme body shapes (see variety).

## Variety: people must not look alike

Random sliders around one base pile up near the average, which is why generated crowds look the same. Rules:
1. Archetypes as attractors. Define 8 to 12 extreme silhouettes (pear, barrel, inverted triangle, beanpole, stocky, round, bony). Each person blends two or three of them.
2. Real spreads, then exaggerate. Take height and build correlations from real data (ANSUR II, WHO), then stretch the spread so the extremes become caricature, not noise.
3. Silhouette gate. 50 generated people as black shapes on one sheet; if two look the same at thumbnail size, widen the ranges.
4. Faces vary in proportion first. Eye spacing, face length, jaw width and feature heights before noses and ears; then a feature library; then a small seeded asymmetry.
5. Every axis has a cause. Height from inheritance and childhood wealth; hands and muscle from work; posture from traits and age.
6. Families stay legible. A shared family face vector; build varies.
7. Clothes and posture carry the rest.
8. Crowd figures keep identity. A distant figure uses the same silhouette and colours as the full character it becomes up close.

## Bodies, ageing, inheritance

A child's shape is a weighted mix of the parents' shapes plus seeded noise per feature group. Age is a separate axis on top, which Anny shows can be kept apart from identity. The engine hands over both parents, so the game never invents a resemblance.

## Faces

Identity lives in geometry (skull, nose, jaw from blendshapes). Expression lives in painted eye, brow and mouth textures chosen by emotional state and swapped in steps. Age shows as painted lines driven by age and outdoor work. At a distance only brows and mouth read, so they are exaggerated.

## Clothes

Layers: base, knit or mid layer, outer layer (oilskin, parka, coat), head and feet, badges and patches. Each garment carries its year of manufacture, cost tier, work use and taste group. A wardrobe is sampled from what a person could afford, when: new money wears this year's things; old money wears good things kept up; poverty wears old things, mended. Wear and fading come from item age and work. Reference library: DigitaltMuseum (Norsk Folkemuseum), real dated garments. Regional anchors: Helly Hansen oilskins and North Sea survival suits; the Marius sweater (1953).

## Body language

- Smith & Neff (2017): bigger, higher gestures read as extraverted and open; lifted shoulders and stumbling, overshooting movements read as low emotional stability.
- Thoresen et al. (2012): people agree strongly on what a walk says (expansive and loose reads as extraverted; slow and relaxed as calm), though the impressions don't match the walkers' real personalities. For us that is useful: the engine's trait drives the cue people reliably read.
- EMOTE (Chi et al. 2000): Laban's effort and shape qualities applied as modifiers to existing poses. This is the layer between personality and animation.

## Animation on a small budget

A small clip library plus procedural layers (Unity Animation Rigging: gaze, foot planting, reaching, posture offsets). Posed on twos, with hair and cloth on ones, as in Spider-Verse. Motion matching needs minutes of capture per style and is not for us.

## Crowds

Assassin's Creed Unity used three tiers: cheap distant figures (about 2,000 polygons, 11 bones) beyond 40 m, puppets at 12 to 40 m, and up to 40 full AIs within 12 m, with up to 10,000 on screen. Baked GPU animation draws hundreds at once but without blending. A gig crowd moves as one body: a shared beat and swell, with each person's amplitude and delay scaled by their traits.

## What the engine must provide

Person and parent IDs and an appearance seed; birth date; childhood wealth; health flags; weight trend; work history with physical load and outdoor exposure; personality traits, mood and stress; money over time and big purchases; taste or subculture with years; closeness per pair; current activity and place; dated injuries and life events.

## Sources

[MakeHuman licence](https://static.makehumancommunity.org/about/license.html) · [MPFB closed-source FAQ](https://static.makehumancommunity.org/mpfb/faq/use_in_closed_source.html) · [Anny](https://europe.naverlabs.com/blog/anny-a-free-to-use-3d-human-parametric-model-for-all-ages/) · [Anny paper](https://arxiv.org/html/2511.03589v2) · [Blender Human Base Meshes](https://www.cgchannel.com/2023/06/download-blender-studios-free-human-base-meshes) · [Quaternius licence](https://quaternius.com/license.html) · [Mixamo FAQ](https://helpx.adobe.com/creative-cloud/faq/mixamo-faq.html) · [CMU mocap](http://mocap.cs.cmu.edu/) · [SMPL-X licence](https://smpl-x.is.tue.mpg.de/modellicense.html) · [ANSUR II](https://www.openlab.psu.edu/ansur2/) · [Wildermyth layers](https://wildermyth.com/wiki/Image_layers) · [Guilty Gear Xrd](https://www.ggxrd.com/Motomura_Junya_GuiltyGearXrd.pdf) · [Smith & Neff 2017](https://www.cs.ucdavis.edu/~neff/papers/GesturePersonality_SmithNeff_2017.pdf) · [EMOTE](https://www.cis.upenn.edu/~badler/siggraph00/emote.pdf) · [Thoresen 2012](https://bps.org.uk/research-digest/what-your-walk-says-about-you-wrong) · [Unity Animation Rigging](https://docs.unity3d.com/Packages/com.unity.animation.rigging@1.2/manual/ConstraintComponents.html) · [AC Unity crowds](https://gdcvault.com/play/1022141/Massive-Crowd-on-Assassin-s) · [Animation instancing](https://blog.unity.com/engine-platform/animation-instancing-for-skinnedmeshrenderer) · [Marius sweater](https://snl.no/Unn_Søiland_Dale) · [DigitaltMuseum example](https://digitaltmuseum.org/011023246498)
