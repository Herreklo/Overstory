# Stone: what the stylised studios' own talks say

Research for the stone redraw (Q15), 22 October, Opus 5.5, online only, from slides, papers, artists' own posts and talk captions. (secondary) marks a summary or press report; (unverified) our inference. L* figures are my measurements on the slide JPEGs (sRGB, 5th to 95th percentile; unverified).

## In short

1. **Every studio states restraint as a rule; none publishes a threshold.** The Witness: "Minimize the amount of noise we put into the player's mind" (slide 7). Sucker Punch built a tool that showed noisy areas in red. Arkane's art director's "main goal… was to remove noise".
2. **Stone faces carry almost nothing; form and light carry them.** The Witness's final wall: each stone one value (within 1.5 L*), neighbours 1 to 6 L* apart, the whole lit wall within 3.9 L*. Firewatch's rocks are "almost flat grey" with baked occlusion; much of the colour comes "from lighting + fog + color correction".
3. **The Witness drew our fault, then removed it.** Its earlier wall had joints 9 to 22 L* darker than the stone and light chipped rims 7 to 11 L* brighter round every stone. The final wall has neither: a joint is a plain value step, or a hairline 1 to 1.5 L* lighter.
4. **Detail sits at the corners of the mass and on edges, never evenly.** Antonio puts chipped bricks "on the corners"; Firewatch's rocks are "smooth surfaces interrupted by jagged edges and detailed divots"; Arkane: "details can't be everywhere in equal quantity".
5. **Medium frequency only.** Arkane: "concentrate on medium size details"; big frequencies from modelling and composition. Valve: "High frequency detail is omitted where possible".
6. **Edges are drawn with light, not dark lines.** Firewatch drybrushes rock edges; Valve emphasises silhouettes "with rim highlights rather than dark outlines".
7. **Distance is quieted by systems, and no one publishes the distances.** Firewatch's fog "serves to lower textural noise once an object is out of the foreground"; Kena merged distant meshes into proxies; Rare blends cloud noise frequencies by distance.
8. **Few kinds, quickly made.** Firewatch: "if you only need three rocks don't make a fourth", under 30 minutes' sculpting each; Arkane: three rock families; Ghost: one species per place.
9. **Judged in the game, in several lights, by removal.** Ng: in the game, "preferably with different lighting conditions". Antonio: "what details can I remove without losing any of its properties?" Valve checked its characters in silhouette "with no internal shading at all".
10. **No source gives texel density, bevel size, joint width or fade distance.** Arkane: when texel density rose, "our painting patterns became much smaller", so marks should be sized in world units, not texels (unverified).

## Evidence by studio

**Thekla, The Witness.** Antonio, *The Art of The Witness*, GDC 2014 slides: 27, "Simplified reality"; 29 to 31, one wall from photo to final (findings 2 and 3); 32 to 36, rocks as a few planar facets, the quarry photo's streaks dropped. Slide 29's posterised photo (unverified): lit face 3.4 L* spread, shaded 7.4, lit to shade about 45, quoins about 9 below the field. Antonio's own site, The Keep: "we need detail on the corners to show what the building is made off (in this case the chipped bricks)"; "reduce texture detail, keeping the bare minimum"; "our textures are so clean and the lightmaps are per entity". Detailed Textures: "textures are almost flat, relying on the mesh detail". Blow (PlayStation Blog, 21 September 2015): "If something grabs your attention, it had better be important."

**Campo Santo, Firewatch.** Ng, *The Art of Firewatch*, GDC 2015 captions: 6:57, "flat shapes with strong distinctive silhouette with abstracted internal details"; 19:21 to 20:25, alpha cutoff by distance, fog "great at cutting down texture detail"; 20:57 to 21:27, rocks with "almost no texture detail… other than some drybrushed highlights on the edges"; 22:30, a handful of rock modules; 23:32 to 24:34, texture detail on props "adds to your story". Campo Santo blog Q&A, 16 October, 22 October and 17 November 2014 (archived): findings 2, 7 and 8; "distant objects turn into mostly flat colors with clean silhouettes"; details of "3 hours… amount to maybe 3 pixels on the screen".

**Sucker Punch, Ghost of Tsushima.** Connell, *Creating Feudal Japan from Across the Pacific*, GDC 2021 captions: 36:23, Kawase's prints, "you don't really see the rocks in the sand"; 36:53, Breath of the Wild's "low noise feeling"; 39:25 to 40:25, "if it was red it was too noisy"; "a great rock texture but it was very noisy", simplified to "let it sit down"; "remove as much noise as possible so you see the details that matter". Patry, SIGGRAPH 2020, slide 13 notes: normal variance filtering, "like we already did for our isotropic specular normal and gloss maps".

**Arkane, Dishonored.** Gombart, 80.lv, 13 April 2017: "Sebastien hates stones with big uniform joints"; "we don't want to necessarily keep visible joints everywhere"; no "regular grids"; tile orientation varied in the normal map; Substance's metal edge-wear mask "often noisy", painted out (`research-restraint.md` omits that it was metal). Gasperin, 80.lv, 21 November 2017: "Micro and medium frequency were obtained by the material, big frequencies with modeling and assets composition".

**Valve, Team Fortress 2.** Mitchell, Francke and Eng, NPAR 2007: "the impression of repetition in the space is more important than representing every detail explicitly"; textures "maintain a minimum level of visual noise".

**Riot.** Brownell's 2014 dev blog, reproduced in full on a fan site: "clamping value ranges".

**Rare, Ember Lab, Epic.** Ang and others, SIGGRAPH 2018: Sea of Thieves' clouds blend noise frequencies by distance; nothing on stone. Josh Grier (80.lv, 2026): distant meshes combined into proxies. Fortnite: only a press report of Ellis's GDC 2018 talk, objects abstracted to basic shapes and set askew (secondary).

## What this means for our redraw

- **SN7's face patch.** One flat value per face, relief from a few planes, occlusion multiplied, no painted mottle. A starting budget from The Witness (unverified): at most about 2 L* within a face in even light, neighbours 1 to 6 L* apart.
- **SN7's wear and polish.** The one accent: light on the lit arris, as Firewatch's drybrush, never a dark line beneath it; on the flight's corners and nosings where the fact is, the middle of runs calm.
- **SN7's joints' fill and moss.** No dark lines or rims round every stone: a broken value step between faces, at most a lighter hairline where an arris catches light. Moss in medium patches on the shaded side, never a line along every joint.
- **R2a's judgement.** A noise map at the views, as Sucker Punch's (our one-eighth check against the clay); three lights; grey, then silhouette; Antonio's question for each mark; The Witness's slides 30 and 31 as the reference pair for "loose lines". Judge the L0 to L1 switch with fog on: these studios quiet distance with fog and proxies, not fades.

## Claims confirmed, corrected, left unread

- Witness "minimize the amount of noise" (`research-restraint.md`, via excerpts): **confirmed**, slide 7.
- Witness "chipping a cube's edges is enough" (`stone.md`, secondary): **corrected**: chips on the corners of the mass, none on the final wall's stones.
- "Two or three values" per stone (`stone.md`): **corrected** towards SN7's one value per face.
- Joints as broken accents where a lit plane turns (`research-restraint.md`, unverified): **supported** by The Witness's final wall.
- Firewatch via Thumbsticks (secondary): **confirmed** and extended.
- Firewatch's rocks under "unique high poly baked per stone" (`stone.md`'s table): **corrected**: a handful of sculpted modules, reused.
- Riot's clamped value ranges, Arkane (Gombart), Kena's merged distant meshes: **confirmed**, without numbers.
- Ghost "masses of one kind" (secondary): **confirmed**, and extended by the noise tool.
- Sea of Thieves "realistically wonky"; Fortnite "too noisy", "smaller than a mailbox"; Breath of the Wild "playability first"; Diablo III: **unread**; YouTube refused the captions (rate limit).
- A mark at least a quarter of the face's short side, at most two a face (unverified): **untested** by any source; The Witness keeps fewer.

## Gaps

No source read gives a texel density, bevel size, joint width, fade distance or noise threshold; Sucker Punch does not say how its tool measures noise. Rare's, Epic's and Nintendo's art talks stay unread.

## Downloads, to `~/code/overstory-sources/studios-stylised/`

| Date | File | Source URL | Size | Read for |
| --- | --- | --- | --- | --- |
| 22 October | `gdc2014_luisantonio_theartofthewitness.pdf` | artofluis.com/wp-content/uploads/2014/03/gdc2014_luisantonio_theartofthewitness.pdf | 10.1 MB | wall and rock slides, values |
| 22 October | `2015-Labs-Spanyol_The-Art-Of-The-Witness.pdf` | history.siggraph.org/wp-content/uploads/2022/06/2015-Labs-Spanyol_The-Art-Of-The-Witness.pdf | 2.7 MB | The Witness's art method |
| 22 October | `NPAR07_IllustrativeRenderingInTeamFortress2.pdf` | cdn.fastly.steamstatic.com/apps/valve/2007/NPAR07_IllustrativeRenderingInTeamFortress2.pdf | 2.8 MB | noise, frequency, silhouettes |
| 22 October | `2018-Talks-Ang_The-Technical-Art-of-Sea-of-Thieves.pdf` | history.siggraph.org/wp-content/uploads/2022/09/2018-Talks-Ang_The-Technical-Art-of-Sea-of-Thieves.pdf | 1.7 MB | distance handling |
| 22 October | `s2020_pbs_patry_slides.pdf` | blog.selfshadow.com/publications/s2020-shading-course/patry/s2020_pbs_patry_slides.pdf | 93.7 MB | specular filtering, detail maps |
| 22 October | `SdxQ3HlhTE8.en.vtt` | youtube.com/watch?v=SdxQ3HlhTE8 (Ng, GDC 2015) | 205 KB | rocks, fog, distance |
| 22 October | `cIIROyeTlbs.en.vtt` | youtube.com/watch?v=cIIROyeTlbs (Ng, Konsoll 2017) | 464 KB | art content (none) |
| 22 October | `n0MO-mjzczU.en.vtt` | youtube.com/watch?v=n0MO-mjzczU (Connell, GDC 2021) | 503 KB | noise tool, restraint |
