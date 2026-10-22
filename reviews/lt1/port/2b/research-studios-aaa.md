# Stone: what the realistic AAA studios' own talks say

Research for the stone redraw (Q15), 22 October, Opus 5.5. Primary sources only: talk papers, slides, captions. (secondary) marks a summary or forum; (unverified) marks our inference.

## In short

1. **No source gives a stone bevel in millimetres.** Insomniac bevels no geometry: a 45° bevel lives in the normal map. Ready at Dawn used "a tiered system of beveling techniques by distance" plus custom vertex normals, with no sizes. Our 2 px rule stays our own.
2. **Tiling first; uniqueness from painted layers.** The Order: 90–95% tiling, up to 4 runtime layers by vertex colour over height maps. Naughty Dog: two vertex-colour sets, six layers; Uncharted 4's tiling maps capped at 1024², often 512. The Division 2: a painted world mask at 1 m a pixel.
3. **At most one unique map a piece.** Naughty Dog's rocks share a shader and three tiling textures; each rock's own map is a "one-to-one macronormal".
4. **Marks in waves, largest first, kept subtle.** Corner damage on some bricks only, no "overpowering details in the Albedo"; Uncharted 4's clutter was reined in.
5. **Joints are drawn in the texture**, as tiling height and normal softened by a bevelled mask. No talk gives a modelled joint.
6. **Kits on metric grids; plain pieces first.** Insomniac: 2, 4, 8, 12 m pieces, walls in 4 × 4 m modules. Bethesda: each piece inside its footprint, core walls "rock solid" early.
7. **Repetition hidden by turning, mixing and layers.** A Naughty Dog cliff is five pieces, six usable sides each; Bethesda mixes 11 hole halves in pairs; Spider-Man swaps texture variants for per-layer sliders.
8. **Generated work changes only through its inputs** (Insomniac).
9. **No talk gives a fade or LOD distance for stone.** Uncharted 4's moss goes subpixel "a few meters away".

## Evidence by studio

**Ready at Dawn.** Phail-Liff and Vitale, *Crafting Victorian London*, SIGGRAPH 2015 talk paper, §1–2:
- "highly crafted tiling materials derived from 3D sculpts";
- "90-95% tiling materials, with up to 4 runtime material layers authored using vertex blending, in conjunction with height maps";
- against aliasing, "a tiered system of beveling techniques by distance, a toolset for customizing vertex normal", and "any number of blending variants per instance".

Neubelt and Pettineo, SIGGRAPH 2013 course notes, p. 17: layer alphas "typically come from colors embedded in mesh vertices".

**Naughty Dog.** Benainous and Sobota, *The Material Art of The Last of Us*, Substance Days at GDC 2023 (captions):
- min 17–18: two colour sets for walls (cracks, moss, leaks; bigger cracks, wetness, damage);
- min 19–20: trims cut to measured sizes "to avoid having any stretching";
- min 28–31: a brick tile of 6 by 20, damage "in waves from largest to smallest", grout rounded by "a lightly beveled brick mask";
- min 48–49: rock shaders identical "except for the one-to-one macronormal"; the cliff of five pieces.

Olguin, *Texturing Uncharted 4*, GDC 2016 (captions, min 20, 46–47): sculpts baked to tiling maps in Substance Designer, "we cap them out [at] 1024", 512 where memory needs it. Brinck and Maximov, *Technical Art of Uncharted 4*, SIGGRAPH 2016, slides 45, 62–65: moss subpixel at a few metres; wetness a painted mask, storage not stated. Pangilinan and Nakata, *Cinematic Environment Production for Uncharted 4*, GDC (captions, min 24–25): clutter "is really easy to overdo".

**Insomniac.** Olsen, *The Ultimate Trim*, GDC 2015, slides 8, 17, 25: "a standardized trim layout", "45 degree normal map bevels along all edges", a trim plus a tileable per material; UV padding 1.5/1000; no texel density or sheet size.

*Look Creation of Manhattan*, Substance Days at GDC 2019 (captions):
- min 5–6: pieces of "two four eight twelve meters"; the bevel in the normal map "so you don't have to bevel in the geometry";
- min 9: walls in 4 × 4 m modules;
- min 64–67: one blend shader on vertex colour or a small 3D texture, with per-layer colour, AO, normal and gloss sliders.

*Procedurally Crafting Manhattan*, GDC 2019 (captions):
- min 10: 128 m streaming tiles;
- min 21: imposters, at most 12 zones at full detail;
- min 31: never hand-edit "anything that a procedural system generates";
- min 65: Houdini bakes wetness into vertex colour; artists paint over it.

**Bethesda.** Burgess and Purkeypile, *Fallout 4's Modular Level Design*, GDC 2016 (captions):
- min 6–7: the footprint "as a maximum extent", or coplanar faces flicker;
- min 23: core pieces first, "rock solid";
- min 45–47: 11 hole halves in pairs; decals and greebles placed apart.

No grid size is given.

**Ubisoft.** Haar and Aaltonen, SIGGRAPH 2015, slide 9: Assassin's Creed Unity used "Modular construction (partially automated)" and "~10x instances". The Odyssey ruins talk, GDC 2019 (captions, min 30, 55): "over 35 architecture kits"; level art placed by hand.

Red Storm, *The Division 2: A World of Materials*, Substance Days at GDC 2019 (captions):
- min 30–31: a top-down weather mask "at 1 meter per pixel";
- min 33: a world-space wall mask for grime, tints and "some bricks sticking out";
- min 35: grime masks baked per tile.

**The Coalition.** Penty and Wong, SIGGRAPH 2017 talk paper, §2–4: shared materials stacked and cooked by "the Smelter", after The Order. A detail normal can stay live "so the texel density is not lost on cook".

**Cloud Imperium, Guerrilla, DICE: unread.** Star Citizen's "med poly" is known only from Polycount, now behind a bot check. Guerrilla's placement deck is 239 MB, not fetched. DICE's Battlefront talk has no captions and members-only slides.

## What this means for our redraw

- **Edge.** Ready at Dawn's distance tiers match our rule: a real chamfer near, normals and filtering past about 10 m (`stone.md` 7). The normal-map bevel suits straight lengths such as copings and kerbs (unverified).
- **Face.** Shared sculpted tiling detail at 1024² a kind; a unique low-frequency map only where the geometry cannot carry the macro form. Our cut blocks can (unverified).
- **Layers and marks.** Six vertex layers is the most found; keep `channels.json` within it. Marks largest first, on some stones only, quiet in albedo.
- **Joints.** Closed surfaces; joint by height and normal, softened at the arris (`stone.md` 9).
- **Generator.** Change inputs, never output; every piece inside its footprint; plain steps and wall stones first.

## Claims confirmed, corrected, left unread

- The Order's sculpted tiling library (`stone.md` 6; production 1c): **confirmed**.
- Gears 4's cooked layers: **confirmed, scope corrected**: it composites materials and says nothing about chamfered blocks.
- The Last of Us Part I's vertex channels (secondary): **confirmed**, two sets, six layers.
- Uncharted 4's moss and wetness as vertex channels: **corrected in part**: a painted mask, storage not stated.
- The Division's world mask: **confirmed**, 1 m a pixel.
- Insomniac's trims "while the real chamfer carries the edge" (production 1d): **corrected**: the normal map carries the bevel on unbevelled geometry; a chamfer under a trim is our variant (unverified).
- Star Citizen's "med poly" and fragile custom normals, Elwood's booleans, Cyberpunk, Mitton: **unread**.

## Gaps

None of these sources gives bevel sizes in millimetres, joint dimensions, texel density in px/m, trim sheet sizes, fade or LOD distances, or triangles per stone, module or stair. There is no primary source on stone stairs.

yt-dlp hit HTTP 429 after five talks. Olguin (`UNxOxiR5T_M`), *Procedurally Crafting Manhattan* (`4aw9uyj9MAE`) and Fallout 4 (`QBAM27YbKZg`) were read from the Browser pane's caption track. That page played aloud, so the method is now barred. Those captions are not saved, and a second yt-dlp try also hit 429. Fetch them before a decision rests on them.

## Downloads

All files are in `~/code/overstory-sources/studios-aaa/`.

| Date | File | Source | Size | Read for |
| --- | --- | --- | --- | --- |
| 22 Oct | `order1886-crafting-victorian-london-2015.pdf` | history.siggraph.org | 1.0 MB | tiling, bevel tiers |
| 22 Oct | `order1886-material-pipeline-neubelt-pettineo-2013-notes.pdf` | blog.selfshadow.com | 9.4 MB | vertex layers |
| 22 Oct | `gears4-layered-materials-penty-wong-2017.pdf` | history.siggraph.org | 15.2 MB | cooked layers |
| 22 Oct | `uncharted4-techart-brinck-maximov-2016.pdf` | advances.realtimerendering.com | 13.3 MB | moss, wetness |
| 22 Oct | `insomniac-ultimate-trim-olsen-gdc2015.pdf` | media.gdcvault.com | 9.1 MB | trims |
| 22 Oct | `acunity-gpu-driven-haar-aaltonen-2015.pdf` | advances.realtimerendering.com | 4.4 MB | modularity |
| 22 Oct | `DEuYcOWNV2k.en.vtt` | youtube.com (The Last of Us) | 0.5 MB | layers, rocks |
| 22 Oct | `RgUaPmDJ2r4.en.vtt` | youtube.com (Spider-Man look) | 0.8 MB | kit sizes |
| 22 Oct | `KvdMY6XTVF8.en.vtt` | youtube.com (The Division 2) | 0.5 MB | world mask |
| 22 Oct | `DBqa7Um28m8.en.vtt` | youtube.com (Odyssey ruins) | 0.5 MB | kits |
| 22 Oct | `bEIX-EQNZuQ.en.vtt` | youtube.com (Uncharted 4 cinematics) | 0.5 MB | restraint |
