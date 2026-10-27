# How the best stylised games built their look

LT1, 27 October 2026. Input to the new art direction, beside the painters in [masters.md](masters.md). Sources are talks read from captions and the makers' own text; (secondary) marks a translation or a forum.

**In short.** Clean games that are not dull spend detail only where it means something and keep the rest as calm planes. Air and one colour script carry the mood, and edges come clean from geometry and vertex data. Their tools are cheap: a fog strip, a blur, a 64 px sheet, a vertex channel. The costly looks fail at distance (lines, fine marks) or need a fixed camera (painted backdrops).

## 1. Principles

*Best fit* marks the six that suit us most: clean but not dull, stylised, our own, history readable.

1. *Best fit.* **Refuse other games; research the place.** Antonov began Dishonored "by eliminating influences": no games or films, only paintings, photographs, books and field trips to London and Edinburgh. His enemy was the computer look, too smooth or too sharp; his cure was knowing where to concentrate detail [Antonov, Game Informer]. The Witness turned to architects and landscape studios rather than concept artists, for a "simplified reality" [Antonio, GDC 2014].
2. *Best fit.* **Detail means story.** Firewatch built its rocks and trees for their shapes, and the rocks carry almost no texture detail. Its story props are simple shapes with dense texture, so detail itself says "this matters" [Ng, GDC 2015]. This saves art time. *Ours:* fine marks go only where there is history.
3. *Best fit.* **Borders, not fields.** Bad North's rule is "smooth gradients, crisp lines". Detail goes where two areas meet, such as a cliff's edge or where something touches flat water. The field between stays quiet [Stålberg, Konsoll 2018]. Dishonored 2 set noisy parts against calm ones and placed wear by use [Gombart, 80.lv]. Masks from geometry make this cheap. *Ours:* wear at sills, corners and plinths; each wall's face is one clean value.
4. *Best fit.* **Measure noise, then cut it.** Ghost of Tsushima aimed at Hasui's prints and planted one species per place. It also built a view that showed textures that were too noisy in red [Connell, GDC 2021]. Dishonored 2 kept only medium-scale marks in its diffuse and normal maps [Gombart]. None of this costs anything at runtime. *Ours:* a noise check in `tools/check.py`.
5. *Best fit.* **The air is the colour script.** Firewatch's fog is one RGB strip sampled by distance in a post pass, under a painted sky that also lights the scene [Ng]. Journey drew its fog close where the player should feel fear and kept blue sky for the end [Nava, GDC 2013]. Breath of the Wild gives near, middle and far their own air [Takizawa and Dohta, via IGN Japan] (secondary). INSIDE caps its fog below 1 so lamps cut through, fakes scattering with one wide blur and dithers its passes against banding. Its volumetric light takes under 1 ms [Gjøl and Svendsen, GDC Europe 2016]. Firewatch's fog and INSIDE's blur each cost one full-screen pass. *Ours:* a distance-by-height lookup for each light.
6. *Best fit.* **Clean comes from geometry and vertices.** Dredge models detail into its low-poly forms and textures nearly a whole biome from one gradient sheet of 64 or 128 px [Bastiaens, Unity 2025]. Guilty Gear Xrd shifts the shade threshold by vertex colour, edits normals and sets the outline's width per vertex [Motomura, GDC 2015]. Townscaper's tiles carry no texture at all. *Ours:* the generator writes these channels from facts.
7. **Lines only near.** Obra Dinn put legibility first. Even so, Pope would drop outlines wherever a long draw distance lets far lines clutter [PlayStation Blog 2019]. Sable fades its lines into fog (our `materials-at-scale.md`).
8. **Masses, not leaves.** Bad North lights a wood as one blob from coarse voxel normals. Units and particles sample the same low-resolution 3D occlusion texture as the island [Stålberg]. Firewatch raises the foliage's alpha cutoff with distance to simplify the crowns [Ng]. Ghost of Tsushima drives grass, trees and cloth from one wind, and its far crowds and birds are GPU particles [Rockenbeck, GDC 2021]. All of these are cheap: one coarse texture, one wind, particles for the far.
9. **Light apart from paint; water and lamps as stages.** Disco Elysium paints over light-only renders and multiplies on shadow passes for morning, noon and evening [Rostov, Pixel Fabula]. Dishonored 2 paints grey and sets the colour by mask in the engine [Gombart]. Sea of Thieves foams calm water only around objects [Ang et al., SIGGRAPH 2018]. Kentucky Route Zero lights by attenuation alone, so each lamp is a flat pool (secondary).

## 2. Four opposed strategies

| Strategy | Age and neglect | People | 60 fps on the M4 | City scale |
| --- | --- | --- | --- | --- |
| **Shape-led, flat or gradient** (Townscaper, Bad North, Dredge, Journey) | Weak: no surface for coats or stains; age reads as new | Silhouette and palette | Best | Best, but monotonous; a Townscaper copy is close |
| **Painted texture on lit forms** (Dishonored, Sea of Thieves, The Long Dark) | Best: wear by use, coats, repairs | Strong: planes plus paint | Memory and authoring per kind | Weakest: fine marks become noise unless each mip is painted; a Dunwall copy is close |
| **Graphic line** (Sable, Obra Dinn, Guilty Gear Xrd) | Strong near, but each line is a claim, so false history is a risk | Strong near, lost far | An edge pass or a hull redraw | Worst: far lines clutter, and fog fights line |
| **Tonal-atmospheric** (INSIDE, Journey, Firewatch) | Found at the focus, lost in the air | Silhouettes and gait | Cheap; watch volumetrics and banding | Best, but gloom over long play |

**Recommendation.** Let the air frame every view (tonal). Build the fabric as clean planes (shape-led). Paint marks only where there is history (painted). Draw lines only at near silhouettes. Firewatch comes nearest, but in a wilderness. In a town whose history lives in its fabric the blend is ours, and the games above show each part of it is cheap.

## 3. Reference candidates for Øystein's yes

These images are unseen: they were picked from captions and filenames, so open each one first. † means ArtStation refused our fetch.

| # | Game | Image | Why |
| --- | --- | --- | --- |
| 1 | Dishonored 2 | ["The Bay"](https://bethesda.net/en/article/3VITzlfbNCm4gks4w8MA0a/dishonored-2-karnaca-art-gallery) | Harbour city painted in sun and rain at once |
| 2 | Dishonored 2 | "The Overlook", same gallery | A painted city held at distance |
| 3 | Dishonored | [Germer, Dunwall](https://www.artstation.com/artwork/nQJyxK) † | Painted textures in engine, harbour streets |
| 4 | Disco Elysium | [ZA/UM screenshot](https://strapi.zaumstudio.com/uploads/disco_elysium_screenshot_98e58416da.png) | Decay painted with restraint |
| 5 | Disco Elysium | [Tamsalu, Martinaise church](https://www.artstation.com/artwork/r9d8oO) † | Neglect in medium-scale marks |
| 6 | Sea of Thieves | [Coppens, Port Merrick](https://www.artstation.com/artwork/BXzyek) † | Stylised port: clean forms, no grunge |
| 7 | Dredge | `9_.png`, [press kit](https://www.dredge.game/press-kit) | Flat shapes and fog at sea |
| 8 | The Long Dark | [Boat in ice](https://cdn.sanity.io/images/ezejho6o/production/6af63474cb37967d205e3ce7e56e360d31c5cd4c-1920x1080.webp) | Northern light, painterly realism |
| 9 | Townscaper | [Raw Fury shot](http://rawfury.com/wp-content/uploads/2021/08/NewScreenshots_01-scaled.png) | Untextured town by water, organic asymmetry |
| 10 | Bad North | `rain1.jpg`, [badnorth.com](https://www.badnorth.com/) | Borders, not fields, in rain |
| 11 | Lake | [Town](https://gamious.com/wp-content/uploads/2019/06/town.jpg) | A 1980s small town, plain and clean |
| 12 | Firewatch | `firewatch_150305_01.png`, [media](http://www.firewatchgame.com/media/) | Gradient fog between planes |
| 13 | Sable | [Badlands](http://rawfury.com/wp-content/uploads/2020/10/02-Badlands.png) | Line and flat colour over a vista |
| 14 | Kentucky Route Zero | [Annapurna still](https://cdn.sanity.io/images/ahd04aec/production/213d78ba1fd8a9c0475df3c10c4d102e7160158a-1408x792.jpg) | Light as stage on flat planes |
| 15 | Breath of the Wild | `wp_desktop_01` to `06`, [Nintendo](https://www.nintendo.com/en-gb/Games/Nintendo-Switch-games/The-Legend-of-Zelda-Breath-of-the-Wild-1173609.html) | Painterly distance in tiers of air |
| 16 | Ghost of Tsushima | [Crafting Tsushima](https://www.flickr.com/photos/playstationblog/50090875163) | One species, one wind, strong colour |
| 17 | INSIDE | `INSIDE_01` to `08`, [Playdead](https://www.playdead.com/games/inside/) | Silhouettes in clamped fog |
| 18 | Journey | [Annapurna still](https://cdn.sanity.io/images/ahd04aec/production/ebfcfeb893ee19d4d52053193c801aac8be0e385-2000x1125.png) | Colour as progression, untextured planes |
| 19 | The Witness | `screenshot01` to `17`, [media](http://the-witness.net/news/media/) | Simplified reality, clean colour fields |
| 20 | Obra Dinn | [Ship-01](https://obradinn.com/img/shots/Ship-01.png) | Legibility from lines: the graphic extreme |
| 21 | Tiny Glade | Key art, [press kit](https://pouncelight.games/tiny-glade/) | Generated stone and timber, clean but worn |
| 22 | Season | [Caro downhill](https://scavengers.s3.ca-central-1.amazonaws.com/Caro_Downhill01.jpg) | Painterly village from a raised view |
| 23 | Arcane | [Fortiche s27](https://fortiche.b-cdn.net/wp-content/uploads/2025/04/Fortiche_projects_arcane_s27.jpg) | Paint on 3D city forms (offline) |

**Talks read:** [INSIDE](https://www.youtube.com/watch?v=RdN06E6Xn9E) (Gjøl, Svendsen) · [Firewatch](https://www.youtube.com/watch?v=SdxQ3HlhTE8) (Ng) · [Bad North look](https://www.youtube.com/watch?v=6JcFbivo8dQ) and [Townscaper](https://www.youtube.com/watch?v=1hqt8JkYRdI) (Stålberg) · [Tsushima's art](https://www.youtube.com/watch?v=n0MO-mjzczU) (Connell) and [wind](https://www.youtube.com/watch?v=d61_o4CGQd8) (Rockenbeck) · [Journey](https://www.youtube.com/watch?v=RoHrwAacTwo) (Nava) · [Guilty Gear Xrd](https://www.youtube.com/watch?v=yhGjCzxJV3E) (Motomura) · [Dredge](https://www.youtube.com/watch?v=1HO1U-d4G4c) (Bastiaens) · [Dishonored](https://www.youtube.com/watch?v=qtLfj6lQeJE) (Antonov) · [Disco Elysium](https://www.youtube.com/watch?v=6x4eYM5eizE) (Rostov). The captions of the Rockenbeck and Nava uploads read machine-translated, so we paraphrase them. **Text read:** [Antonio](https://artofluis.com/wp-content/uploads/2014/03/gdc2014_luisantonio_theartofthewitness.pdf) · [Gombart](https://80.lv/articles/asset-material-production-in-dishonored-2/) · [Pope](https://blog.playstation.com/archive/2019/10/17/lucas-pope-on-return-of-the-obra-dinns-art-style) · [Takizawa and Dohta](https://thefamicast.com/2017/12/part-5-art-and-implementation-of-3d.html) · [Ang et al.](https://history.siggraph.org/wp-content/uploads/2022/09/2018-Talks-Ang_The-Technical-Art-of-Sea-of-Thieves.pdf). **Not read:** Stevenson's Sea of Thieves art talk (GDC 2018) and the Breath of the Wild panel (GDC 2017), because no captions came.
