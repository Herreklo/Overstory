# Painted timber fronts: how studios build them (craft, first pass)

Scale, assuming a 60° vertical field at 1440 rows: a pixel spans 1 cm at 12 m, 2.8 cm at 35 m and 9.6 cm at 120 m. A board face of about 15 cm (to check against the houses note) is 16 px at 12 m, 5 px at 35 m and under 2 px at 120 m; its 2 cm lap falls below a pixel by 35 m.

## Boards

- **Polycount's working rule:** model only what changes the silhouette or sits near the camera; give flat or distant boarding a tiling texture with its height baked into normals.
- **Laps are cheap as geometry where they count.** In section the wall is an extruded sawtooth. By our estimate, a 10 × 6 m front of 40 courses split by its openings is about 400 triangles, or about 3,000 when each board is cut every 0.5 m to carry vertex fields. Modelled laps cast a true shadow line in low sun, which a normal map cannot.
- **Past about 25 m, the laps should move into the shader.** The 2 cm undersides become slivers thinner than a pixel, and the GPU shades whole 2×2 pixel quads for them for nothing. The shader then draws each course's tilt and lap line from height (no samples, about ten ALU), faded to the mean as the footprint nears the board pitch. Parallax occlusion would cost 8–32 dependent reads on every wall pixel; Naughty Dog kept it for small ornament (the Capitol gates in The Last of Us Part I).

## Trims

- **Insomniac's "Ultimate Trim"** (Sunset Overdrive): one standard strip layout for every material, with 45° bevels baked into the normal map along every edge. Low-poly trim gets a "high poly look", and any material swaps in with its edges in place.
- **Ready at Dawn** (The Order: 1886) bevelled in tiers by distance and wrote custom vertex normals to shade few triangles well.
- **For us:** corner boards, casings, sills and the eaves board stay geometry at every near tier. Far off they carry the read (coloured body, light frame lines, dark openings), so a level of detail should remove them last.

## Windows

- **Frames and glazing bars are geometry, never alpha cut-outs.** A `discard` defeats the tile GPU's hidden-surface removal, which our tree study also found.
- **The glass is opaque, with interior mapping** (van Dongen): the view ray hits three room planes and reads one texture, with no blending. SimCity (2013) used it with an atlas of rooms of varying depth. In the questions after their GDC talk, Insomniac said Spider-Man's windows used cube maps and stayed cheap at that count. A 1.2 m window is still about 40 px wide at 35 m; beyond that, each room collapses to its mean colour.
- **A lit room at night claims that someone is home,** so it comes from the occupants and the hour. The seed only picks which room.

## Paint coats and repainting

- **A coat is parameters, not pixels.** Spider-Man's blend shader layers one texture set against itself, giving each layer its own hue, saturation, AO strength, normal strength and gloss. New paint is brighter with its AO faded; old paint is yellower with its AO back.
- **Masks say where; shared height maps give each flake its shape.** The Order: 1886 ran up to four runtime layers by vertex blending, with height-aware edges, on 90–95% tiling materials. The Last of Us Part I paints six blend masks into two vertex colour sets. AC Valhalla (Ubisoft Sofia) blends two texture sets per material by vertex paint. Spider-Man reads its masks from vertex colour written by Houdini, or from a small 3D world texture times height. Tiny Glade damages plaster from one float per vertex: the signed distance to a window.
- **Grime is baked per kit part, by tool.** The Division 2 (Red Storm) baked a grime mask (AO and two grime channels) for each kit piece, catching streaks under overhangs and round windows. A world-projected mask broke the repeats.
- **Stack, then cook.** Gears of War 4 (The Coalition) cooked dozens of artist layers down to the fewest instructions and textures for 60 fps.
- **Building colour is a parameter on a grey mask.** Dishonored 2 (Arkane) tinted a grey diffuse in the engine. Cities: Skylines II gives each asset three colour masks, each with its own colour. In the first Cities: Skylines, colour and upgrades shared the building-ID seed, so upgraded buildings took the same colour (Paradox forum). Each decision needs its own seed or, for us, its own fact.

## The old claim, tested

The old studies say houses cannot carry history per vertex. That holds only for one-off marks. No studio we read gave a building its own paint texture: they put "where" on vertices or small masks, take "how" from a shared height threshold, and give one-off marks a decal.

Boards suit vertex data better than stone does, because each board is its own strip. A board's index, install year and coats fit per vertex, so a renewed board is just an attribute. A sill drip is a per-vertex distance (Tiny Glade's trick) times a shared streak texture. Only ghost signs and painted names need texture space.

Instanced kit parts share vertices across houses, so their per-house state comes through the 32-bit user value into a buffer.

## What we should do (ranked by value per cost)

1. **Coat stack as data.** Each wall gets its list of coats (date, pigment, quality) in a buffer reached from the user value. The shader picks the top coat for the date. Chalking and grain burial (the grain normal weakens with each coat) are functions of years, exposure and coat count. Cost: 0 samples, 1–2 buffer reads, about 30 ALU.
2. **Per-board vertex data from the generator:** board index, install year, exposure, distance below the nearest sill or eave. Cost: 8–12 bytes per vertex and about 3,000 triangles per front.
3. **Peel by threshold.** One shared, grain-aligned height texture, read at two scales, is compared with the loss field (years × exposure ÷ quality), with a dark band at the lifted edge. Underneath lies the previous coat, then primer, then silvered bare wood. Cost: 1–2 samples. At distance the threshold equals the peeled fraction, so with an equalised height map the mean colour is exact without a sample.
4. **Laps modelled to about 25 m,** analytic beyond and a flat mean by 120 m; no parallax. Cost: 0 samples past 25 m.
5. **One trim sheet with 45° bevels** for casings, sills, corner boards and eaves boards, which are kept to the last level of detail. Cost: 1–2 samples on trim pixels and about 100–300 triangles per window surround.
6. **Windows:** modelled bars, opaque interior-mapped glass, lit state from facts. Cost: about 1 sample and 30 ALU, on glass pixels only.
7. **Per-board value jitter** of a few percent, from a hash of board and house (non-semantic texture). Cost: about 5 ALU.
8. **Decals for one-off marks,** only where a fact asks for one.

About four texture reads per wall pixel: measure it in the fixed street view against today's 5 ms.

## Sources

- Olsen, "The Ultimate Trim", Sunset Overdrive, Insomniac, GDC 2015 (slides, `~/code/overstory-sources/studios-aaa/insomniac-ultimate-trim-olsen-gdc2015.pdf`)
- Benno, Mullen, McAuliffe, open-world art of Marvel's Spider-Man, Insomniac, GDC 2019 (captions, `studios-aaa/RgUaPmDJ2r4.en.vtt`)
- Phail-Liff, Vitale, "Crafting Victorian London" (The Order: 1886), Ready at Dawn, SIGGRAPH 2015 (local PDF)
- Penty, Wong, "Gears of War 4: Creating a Layered Material System for 60fps", The Coalition, SIGGRAPH 2017 (local PDF)
- Benainous, Sabota, material art of The Last of Us Part I, Naughty Dog, GDC 2023 (captions, `studios-aaa/DEuYcOWNV2k.en.vtt`)
- Red Storm, "The Division 2: World of Materials", Substance Days at GDC 2019 (captions, `studios-aaa/KvdMY6XTVF8.en.vtt`)
- Valkanova, Assassin's Creed Valhalla material workflow, 80.lv: https://80.lv/articles/a-look-at-the-material-workflow-in-assassin-s-creed-valhalla
- Gombart, Dishonored 2 asset and material production, 80.lv: https://80.lv/articles/asset-material-production-in-dishonored-2/
- Tiny Glade's windows and plaster damage, 80.lv: https://80.lv/articles/procedural-windows-in-pounce-light-s-tiny-glade-get-an-upgrade
- van Dongen, "Interior Mapping", Game Developer: https://www.gamedeveloper.com/programming/interior-mapping-rendering-real-rooms-without-geometry
- Colossal Order, "Adding custom assets", Cities: Skylines II: https://www.paradoxinteractive.com/games/cities-skylines-ii/news/adding-custom-assets
- Paradox forum, Cities: Skylines colour variation sharing the building-ID seed (seen via search; page did not load)
- Polycount, geometry vs normal maps for boards: https://polycount.com/discussion/comment/2225546
- Pixel footprints and triangle counts above are our own estimates, to be measured
