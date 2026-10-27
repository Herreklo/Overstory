# Houses: how the best small teams build them

For the hero-house rebuild, 27 October 2026. Sources are primary unless marked secondary. At 1440p a pixel spans 0.48 mm per metre [house-fronts.md].

## How they build

**Tiny Glade.** Generators synthesise no meshes but place hundreds of thousands of small modelled pieces (bricks, planks, tiles, shutters), each plank unique, in one GPU-driven draw per material [Stachowiak, GPC 2024]. A brick's last level is six triangles hiding an analytic chamfered box, so far bricks still catch light on their bevels. Screen-space contact shadows made bricks read as new geometry [same]. Plaster wears round windows from one float per vertex, the distance to the window [Opara via 80.lv].

**Townscaper.** About 200 hand-built tiles, heading for 300 to 400 [Stålberg, IndieCade 2019]. Textures are faint, so seams vanish; windows sit in real holes cut by a stencil trick; occlusion comes from a coarse voxel copy of the town, cheap enough to read per vertex [Stålberg, SGC 2021]. Where two colours meet, tiles add a trim or a drainpipe [IndieCade 2019].

**Dishonored 2.** Facades are kits of repeating windows and pillars; large forms are modelled, finer detail lives in the material [Gasperin, 80.lv]. Detail stays medium-sized, since fine noise kills style; above a certain size a thing is modelled; wear goes where use would put it, noisy places set against calm ones [Gombart, 80.lv]. The enemy is edges too smooth or too sharp [Antonov, Game Informer].

**Firewatch.** Flat shapes, strong silhouettes, abstracted inner detail; rocks nearly untextured but for dry-brushed edge highlights, soft occlusion and a normal map [Ng, GDC 2015].

**Lake.** Two artists, a 1986 town from photos and street view [Wikipedia; Willamette Week; secondary]. Flat colour, but windows deep under modelled hoods (our reading of a screenshot).

## What reads as well made

- **Depth before size.** Stavanger's surrounds: side boards 120 to 125 mm wide and 25 mm thick, the window set 30 mm in, water boards 30 mm thick projecting 120 and 180 mm [Heng, via wooden-town-architecture.md]. At the 20 m street stop that projection is 19 px; a 10 to 20 mm lap step is 1 to 2 px [house-fronts.md]. True sizes read; ours are flat. Eaves follow style: classical houses have almost none, sveitser deep ones; old barge boards are 28 to 34 by 195 to 220 mm [Mandal 2007; Brochure 2021; via the same].
- **Edges that catch light.** A bevel shows from about two pixels: 8 mm at 8 m, 20 mm at 20 m (ours). Blender's Harden Normals keeps faces flat while the bevel shades smooth [Blender manual]; Unity keeps them only on Import [Unity manual]. The Order: 1886 bevelled in tiers by distance and tuned vertex normals to save polygons [Phail-Liff & Vitale, SIGGRAPH 2015]. Far off, the bevel becomes data: 45° normal bevels on every trim edge [Olsen, GDC 2015], or Tiny Glade's chamfer.
- **Modelled, not painted.** Sills with drips, sashes, bars, brackets, gutters, pipe clips; a chamfer costs about what a hard edge's split vertices do [Polycount forum; secondary].
- **Honest irregularity.** Board widths vary to fit openings [Mandal 2007]. Stålberg found Night Call's pieces sometimes too skewed; Townscaper's pieces skew less [Townscaper tour; Thompson, secondary].
- **Trim sheets.** One fixed strip layout, plus a plain tileable per material, swaps any material with every edge in place [Olsen]: "no excuse for having ugly low poly edges".
- **Budgets.** Cities: Skylines (seen from above) gives buildings under 1,000 to about 5,000 triangles, far meshes 100 to 200 with a 128² texture [Paradox wiki]. Firewatch's main pine falls from 2,484 triangles to 4 [Ng, GDC 2016, via performance-at-scale.md]. Ours: 40,000 near, a 500 to 1,500 shell, 100 at block level; 2 million triangles and 3,000 draws a frame [foundations.md; building-blocks.md]. Not found: a shipped eye-level house's count, Tiny Glade's roof method, Arkane's trim layouts.

## For us

1. Whatever throws a shadow at the street stop is a part at its real thickness, in layers: trim over cladding, sash in frame, glass behind bars. Nothing flush; finer relief is vertex data.
2. Sizes come from facts. Push depth, not size, only where a shadow must hold at the street stop; never an overhang the style lacked.
3. The board shadow line is a real lap step, handed to normals before it shimmers.
4. Every exposed edge is chamfered to two pixels at its judging distance, normals hardened and imported; a check fails sharp edges. Past L1 the chamfer lives on as data.
5. Every junction is a part with contact shade: trim to cladding, wall to plinth, house to house.
6. Irregularity needs a cause: widths fit openings, a lean is seeded texture, sag comes from facts. Calm fields, few rough places, no uniform jitter.
7. The silhouette (ridge, chimneys, eaves, barge boards) is judged first, black against the sky, in grey light.
8. Only mass-made things repeat (tiles, slates, catalogue brackets), as instances; fitted parts stay unique.
9. The atlas holds shape, never stuff: one board-and-trim layout, flat materials.
10. Wear and paint loss read one float per vertex (distance to an opening, edge or ground), shaped in the shader from paint-coat data.

Sources: [Stachowiak, GPC 2024](https://www.youtube.com/watch?v=jusWW2pPnA0) · [80.lv, Tiny Glade windows](https://80.lv/articles/procedural-windows-in-pounce-light-s-tiny-glade-get-an-upgrade) · Stålberg, [IndieCade 2019](https://www.youtube.com/watch?v=1hqt8JkYRdI), [SGC 2021](https://www.youtube.com/watch?v=Uxeo9c-PX-w), [Townscaper tour](https://www.youtube.com/watch?v=sBMnM2-lOPs) · [Thompson, Game Developer](https://www.gamedeveloper.com/game-platforms/how-townscaper-works-a-story-four-games-in-the-making) · [Gombart, 80.lv](https://80.lv/articles/asset-material-production-in-dishonored-2) · [Gasperin, 80.lv](https://80.lv/articles/modular-design-in-dishonored-2) · [Antonov](https://www.youtube.com/watch?v=qtLfj6lQeJE) · [Ng, GDC 2015](https://www.youtube.com/watch?v=SdxQ3HlhTE8) (talks read as captions) · [Lake, Wikipedia](https://en.wikipedia.org/wiki/Lake_(video_game)) · [Willamette Week](https://www.wweek.com/technology/2021/05/05/how-did-game-designers-from-the-netherlands-capture-the-look-and-feel-of-small-town-oregon-better-than-any-other-video-game/) · Olsen, GDC 2015, and Phail-Liff & Vitale, SIGGRAPH 2015 (`~/code/overstory-sources/studios-aaa/`) · [Unity, Model tab](https://docs.unity3d.com/6000.0/Documentation/Manual/FBXImporter-Model.html) · Blender manual, Bevel · [Paradox wiki](https://skylines.paradoxwikis.com/Asset_Editor) · [Polycount](https://polycount.com/discussion/comment/2577208/).
