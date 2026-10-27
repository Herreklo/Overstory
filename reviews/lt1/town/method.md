# How we build each kind, so they match

The coordinator's pick, 27 October, from four studies of who builds houses, trees, land and water, and streets best in our range (Øystein: "who makes the best houses ... and then pick and choose and find our best way to do it, so everything matches in our world"). We take each leader's method, never its look. Our style makes the kinds match.

**The main finding.** Our effort went where the main camera cannot see: cladding laps, paint flakes, 4,200 leaf cards per birch. From the city camera, what reads is the massing, the roof planes, the shadow under the eaves, chimneys, crown masses, edges, and the small things of life.

## What makes everything match

1. **One shape language:** designed, faceted planes. Roofs, rock and crown masses are all planes. No blobs, no sphere normals, no toy proportions; everything at true scale.
2. **One light:** one shade function and one sky map. Matte except where wet (roofs, rock, glass, water). Contact shade at every foot and junction.
3. **One value plan:**
   - walls palest;
   - roofs darker than walls in every light;
   - tree crowns a clear step from the walls;
   - rock below timber, and wet rock darkest;
   - water in the sky's hue, darkest at the foot of things;
   - doors about 15 L\* off their walls;
   - small things inside the four or five bands.
   Accents only for washing, boat hulls and a kept door or roof. Muted colour, not a rainbow.
4. **One distance rule:** real detail within about 8 m, a few marks at the street stop, value and shape only from 12 m. Thin lines turn into ribbons or drop out past about 40 m. Nothing shimmers.
5. **One edge rule:** one chamfer class scaled to the part. A lit arris on tops. Edges are hard where a lit plane meets shadow and where a shape meets the sky. The tree fringe is the only loose edge.
6. **One mark per material:**
   - rock: a pigment band along its foliation;
   - birch: dark tears;
   - crown: a bold leaf stroke;
   - timber: lap shadow, near only;
   - ground: marks at its edges (a wet sheen, a worn line).

**Banned on sight:** photo or scan texture, fine noise, blobs, toy colours, even scatter, lines that crawl, black crown cores, detail in shadow, asset-store clutter.

## Each kind

**Houses.** From Embark (The Finals: generated structure, few supplied modules), Diablo IV (a culture kit per district, detail placed for a high camera), Stålberg (detail at corners, decoration on exposed edges) and Dredge (almost no texture, sharp modelled edges).
- **Take:**
  - massing from each house's diary: body, extensions, lean-tos, sheds, porches, dormers;
  - roofs over the combined footprint, with pitch and eave depth by era;
  - chimneys and gutters;
  - few modules, as profile sweeps (windows and doors by era);
  - matte coats from an era palette;
  - history as whole shapes: a renewed roof run, a peeled patch.
- **Leave until the near tier:** cladding laps and flakes.
- **Test:** a block of twelve houses with history in the massing only, then the same block ten years on, beside a uniform control. Blind readers name which houses are old, changed and neglected. If the massing does not read, surface work will not rescue it.

**Trees and plants.** From Firewatch (designed shapes; 2,484 triangles near, a 4-triangle card far), Disney's canopy shells, Horizon's card craft, and Tiny Glade (see-through from above).
- **Take:**
  - the growth timeline outputs 3 to 5 opaque faceted masses per year;
  - a fringe of cards only at the silhouette and the sky seams, turned to the camera or the sky;
  - the masses alone are the far level;
  - wind stored in vertex colour;
  - bushes as 1 to 3 masses; hedges as a hull plus the shoots grown since the last cut.
- **Leave:** dense card crowns (our birch costs 10 to 16 ms against its 1 ms line), sphere-normal blobs, paid tools.
- **Test:** the birch at 30 and 60 years, built three ways (cards, masses, masses with fringe), seen from 12 m and high. Cold readers judge, and overdraw is measured.

**Land and water.** From Firewatch (rock as a few chunky planes), Sea of Thieves (a designed water colour), Stålberg (crisp borders), Ghost of Tsushima (far land baked) and Horizon (placement by fields).
- **Take:**
  - rock as planes cut by its geology (`bedrock.py`), one value per plane;
  - ground from fields, cut to crisp edges;
  - opaque wave water, coloured by baked depth;
  - at every waterline, a dark wet band and one light line;
  - a fog strip, thicker over water.
- **Leave:** sculpting, scans, Unity Terrain, erosion simulation.
- **Test:** a 40 m shore patch. A script finds its value classes apart, the one-eighth thumbnail reads, and a cold reader names the rock, the waterline and the cut.

**Streets and life.** From Stålberg (a decoration pass after the structure), Tiny Glade (a path becomes stairs on a slope and a gate at a fence), Wildlands (rules per building) and Night City (clusters with rests between).
- **Take:** edges typed from facts and drawn by one line grammar:
  - a boundary between owners becomes a fence or wall;
  - a drop over 0.5 m becomes a retaining wall;
  - a steep grade becomes steps;
  - a quay gets coping and bollards.
- **Ground:** calm planes with marks at the edges.
- **Each household's things come from its facts:** a boat and crates for a fisher, a bike for children, flower boxes for a kept garden. They go into sockets, in clusters with rests between.
- **Props are tokens:** 50 to 300 triangles each, 0.05 M triangles in all at the city camera.
- **Leave:** hand dressing, even scatter, painted backdrops.
- **Test:** three yards (kept, children, fisher) against seeded scatter with the same count. Cold readers say whose yard is whose.

## Order in the town job

The kinds come in the order of what the main camera sees most:
1. houses' massing and roofs;
2. tree masses;
3. land and water;
4. street edges, then life.

Each kind's test is its gate. Cold readers are fresh model agents, blind.
