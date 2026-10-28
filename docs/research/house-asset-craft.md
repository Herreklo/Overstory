# How games build a small house

How shipped games make a house as an asset, beside our pipeline, for house 107 (Øystein, 28 October: "do it with great care. look to how games actually do it"). What reads is in `houses-in-games.md`, `reviews/lt1/town/method.md` and `reviews/lt1/houses/hero/craft.md`.

Written on Opus, 28 October 2026, with three helper passes; nothing downloaded. A maker's own words are unmarked; write-ups are marked (secondary). ArtStation, Polycount and GDC Vault refused our reader, so Diablo IV's, Red Dead's and Tiny Glade's house methods stay unread.

## In short

1. **Buildings are mid-poly, not baked.** Artists model real chamfers and export face-weighted normals, which keep flat faces flat and let a chamfer shade as a soft roll. Epic sets Fortnite's chamfers at 0.5 cm or more [Epic]. Angelic's material lead puts more bevels where an asset is big on screen and bakes only masks for edges and dirt [Resenberger-Loosmann].
2. **Every surface is a tileable, a trim sheet and a mask.** A tileable repeats without seams. A trim sheet is one texture of strips that many pieces map onto. The Witcher 3 gives each district an array of tileables [Janiszewski]. Fortnite's architecture has a second UV set for texture sets [Epic]. Dredge's buildings in a biome share one sheet of 64 to 128 px colour blocks [Bastiaens].
3. **Edges catch light at every distance through data.** Insomniac bakes a 45° bevel into the normal map along every trim edge [Olsen]. Diablo IV's shaders read curvature to change colour and roughness at edges and cavities [Aikman].
4. **Noise goes; medium-sized variation stays.** Arkane hand-painted Dishonored 2 with medium-sized details and libraries of damp, mould and dirt [Gombart]. Dredge's textures are big lasso-cut shapes [Bastiaens]. Firewatch kept nature plain but gave its human-scale props simple shapes and rich, unique textures [Ng].
5. **Nothing is ruler-straight.** Artists warp a cottage with a lattice [Gresham; Soininen] and turn roof tiles at random [Devos]. Fortnite's look began from a lopsided house [Ellis] (secondary); Sea of Thieves wants props realistically wonky [Stevenson] (secondary).
6. **Gradients are authored.** Breakdowns drive masks by a gradient from the asset's bounds [Kayyali] and grow moss up from the foot [D'Adda]. Disco Elysium keeps painted colour apart from a shade map per time of day [Raidma].
7. **Marks that hold in motion live on the surface; light and air do the rest.** WoW keeps texture values neutral so lighting carries mood [Vergne]. Valorant lights from artist-drawn ramps [Wang]; Firewatch colours fog from a strip by distance [Ng]. Sunset Overdrive put brushstroke masks in its environment shader [Olsen]. Tales of Arise kept its painterly filter to the background and had to lighten it [Tomizawa].
8. **Budgets are modest.** A Cities: Skylines II low-density house averages 8,000 triangles (15,000 at most). Each lower level is under half the one above; the last has 500 at most and its own 512 to 1,024 px texture [Paradox]. Fortnite caps a wall module at 2,000 vertices and a roof at 4,300, at 1,024 px a metre [Epic]; Crytek's are mostly 512 [Crytek]. Triangles should cover 10 px or more [Android].
9. **Far levels are made from the made house.** Skylines II gives its last level its own texture. Fortnite swaps each 350 to 400-piece building for one generated proxy far off [80.lv] (secondary).
10. **Our triangles are in range; our steps are not.** House 109 is 52,600 triangles near, 10,700 at street and 1,900 at city. Past the near level we skip items 1 to 6 and 9, and that, more than missing detail, is the CAD look.

## Our pipeline beside theirs

| Step | Games | Ours | Verdict |
| --- | --- | --- | --- |
| Kit | a regional kit of hand-made modules | functions fed by facts | our strength |
| Edges | chamfers, weighted normals; 45° bevels in trims far off | 4 to 10 mm chamfers (`soup.bbox`), flat-shaded, near only | gap |
| Surfaces | tileable, trim, a mask on a second UV set | no textures: a 1,000-line procedural shader | gap past near |
| Occlusion | baked to texture | one linear field per board (`bake_soup`) | no pooling into corners |
| Variation | medium painted shapes, decals | grain, flakes and patches near; one coat in the town (houseBrush) | missing past near |
| Irregularity | lattice warps, skew | ridge sag 50 mm at most, board tilt 1.6 mm | under 3 px at the street stop |
| Windows | parallax rooms near, dark far | rooms behind glass near; flush dark quads in town | gap far |
| Levels | half each step, the last baked from the house | three levels, no bake; the town draws masses | gap |

The r36 town is the worst case: `LT1Town` draws each house as a box, a prism and a plinth, one colour each. House 109's near geometry is close to production, yet in grey (r02) it reads clean: equal boards, straight lines, one value from foot to eave.

## Is the one-coat rule part of it?

Yes, half of it. Banning photo, scan and fine noise is what Arkane and Epic did, and it stays. Painting a wall as one coat with no brushwork (r23 and r24, `town.json` houseBrush) also removed the band every reference keeps. That band is marks 10 to 50 cm across: board-to-board value, a repainted run, a dirty foot, streaks under sills. Most of our near marks fade before the street stop and our big shapes are flat, so nothing is left between. Bring the middle back from facts and seeded texture, sized in the world and locked to the surface (`painted-marks-in-motion.md`).

## Recipe: house 107

The record (`fixtures/lt1-street.json`): a fisherman builds in 1828, classical, 1.5 storeys, wealth 200, 7 × 7 m. A lean-to shed goes on the back in 1950, husmor windows (one big pivot pane) to the street in 1965. The owner dies in 1986 and the house is boarded and left. We see it in 1989.

1. **Blockout.** Massing from the record, judged black against the sky from the four views. Paint the target over this render.
2. **Model, mid-poly, in the generator.**
   - Chamfer each exposed arris to 2 px at the street stop: 15 to 20 mm on corner boards, verges, fascia and sills (old timber worn round), 6 mm on sashes. Export face-weighted normals.
   - Keep the classical 140 mm eave. Thicken the fascia and verge boards instead.
   - Bend, don't jitter. The 1828 ridge and eaves sag 80 to 120 mm, and one corner settles 40 mm on its stones. The 1950 lean-to stands 1 to 2° out of plumb. Boards follow the frame, and each bend shows 3 px or more at the street stop.
   - The 1986 boarding is the loudest fact: rough formwork boards nailed proud over every opening, geometry at every level.
   - Pantiles are instanced near. Verge, eave and ridge tiles stay geometry at every level, so the roof's edge keeps its thickness and wave.
3. **Texture space.** Unwrap the house once and bake its place and history pages (`history-pages.md`): one 1,024² page, about 50 px a metre over its 250 m². They hold occlusion with real falloff, curvature and sky. They also hold the eave's drip line, soil, moss on the north roof and the lean-to, and paint loss from the coat stack. Each material (painted boarding, pantile, fieldstone, formwork, felt) gets a tileable at 512 px a metre, and the working one trim sheet with 45° bevels. All are rendered from our own near parts, never photos. The shader keeps the history; fixed looks move into maps, likely cheaper to sample than compute (our estimate).
4. **Shade.**
   - Design each wall's value: a darker, cooler foot up to 0.6 m, darker under the verge, lighter toward the eave.
   - Boards differ by 3 to 5 L\* (lightness). A repainted run sits a step apart; flakes gather in 10 to 30 cm groups at laps, foot and sills.
   - Curvature lifts worn arrises toward grey wood and darkens cavities, at every level.
   - A brush field of 20 to 40 cm marks on the surface at near and street, falling to its mean beyond. No screen filter.
5. **Levels and budget.**

   | Level | Seen from | Triangles | Maps | Materials |
   | --- | --- | --- | --- | --- |
   | Near | within 8 m | 20,000 to 25,000 | tileables, shared 2,048² trim sheet, pages | 4 |
   | Street | about 20 m | 6,000 to 8,000; boards become planes with the lap in the normal map | the same | 2 |
   | City | 50 to 150 m | 500 to 800; masses, thick roof edge, chimney, boarding in relief | a 512² bake of the near look | 1 |

   The town's 119 houses at the city level come to under 0.1 million triangles.
6. **Judge** as always: grey light, four views, beside the target.

## What changes for 109

Its near model is built (r02), so it takes steps 3 to 5 without remodelling. The causes differ: a working sea house wears at the loading doors and hoist and takes splash at the quay foot. The street level falls to about 8,000 triangles and the city level to about 1,000, with the bake.

## Sources

Epic: [modeling tips](https://dev.epicgames.com/documentation/fortnite/modeling-tips-in-unreal-editor-for-fortnite), [architecture](https://dev.epicgames.com/documentation/fortnite/architectural-modeling-guidelines-in-unreal-editor-for-fortnite) · [80.lv, proxies](https://80.lv/articles/guide-proxy-lod-tool-in-unreal-4-20) · [Resenberger-Loosmann](https://80.lv/articles/creating-assets-within-the-mid-poly-workflow-in-ue5/) · [Janiszewski](https://80.lv/articles/world-building-of-witcher-3/) · [Bastiaens](https://unity.com/resources/crafting-dredge-cozy-atmospheric-horror) · Olsen and Ng, GDC 2015 (`~/code/overstory-sources/`) · [Aikman](https://news.blizzard.com/en-us/article/23964183/peeling-back-the-varnish-the-graphics-of-diablo-iv) · [Gombart](https://80.lv/articles/asset-material-production-in-dishonored-2/) · [Gresham](https://80.lv/articles/crafting-stylized-european-cottage-with-substance-3d-ue5) · [Soininen](https://80.lv/articles/making-a-stylized-fantasy-town-in-blender-substance-3d-unreal-engine) · [Devos](https://80.lv/articles/creating-a-stylized-medieval-building-in-3ds-max-UE5-substance-3D) · [Ellis](https://www.pcgameshardware.de/Fortnite-Spiel-16272/Specials/Epic-Games-Unreal-Engine-4-GDC-2018-1253176/) · [Stevenson](https://blog.habrador.com/2018/08/stylized-graphics-fortnite-sea-of-thieves.html) · [Kayyali](https://gamesartist.co.uk/viking-house-in-unreal-engine-egor-kayyali) · [D'Adda](https://80.lv/articles/making-a-ghibli-inspired-mountain-village-in-unreal-engine-5/) · [Raidma](https://discoelysium.com/devblog/2016/02/02/shedding-light) · [Vergne](https://80.lv/articles/the-strings-of-environment-design/) · [Wang](https://www.riotgames.com/en/news/valorant-shaders-and-gameplay-clarity) · [Tomizawa](https://en.bandainamcoent.eu/tales-of/news/tales-of-arise-tgs-2019) · [Paradox](https://cs2.paradoxwikis.com/Asset_Pipeline:_Buildings) · [Crytek](https://www.cryengine.com/docs/static/engines/cryengine-3/categories/1114113/pages/21267831) · [Android](https://developer.android.com/games/optimize/geometry).
