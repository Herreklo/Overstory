# Brick and render

How to build brick that reads as single bricks, and render on brick that cracks, spalls, gets patched and is repainted. Research for the houses not made of wood (the Eiganes villa, the tip's buildings, a red-brick cannery), 29 October 2026. Marks: (unverified) no source confirmed it; (ours) our arithmetic.

## In short

1. **In Stavanger, brick is the exception, and it has a date.** There were 12 private brick houses in 1868 (Byantikvaren 2017). After the 1904 law that followed Ålesund's fire, whole central blocks went up in brick (Stavangeren 1/2001). The Jugend *murhus* of about 1905–25 follow the timber town's plots (Byantikvaren 2021).
2. **Stavanger painted its brick.** "In Stavanger's wet climate it has proved hard to leave brick houses untreated" (Byantikvaren 2017, our translation). Kongsgata 47–49 (1867) was painted beige to pass for sandstone, then red about 1930, then pink in the 1970s. A coat stack over brick is the town's practice, so `care.py` reaches brick too.
3. **Norwegian clay fires red, and yellow brick was imported** (SNL; Narvestad 2026). The local brickworks closed by the mid-1920s. A yellow wall like ref 19 says where its bricks came from.
4. **The studios we found bake the bond offline and vary it at runtime** (Naughty Dog, The Division 2, Spider-Man, The Order). Tiny Glade instead instances every brick; Bluepoint adds real bricks only where a wall breaks, aligned to the painted bond. No shipped runtime bond shader with per-brick IDs was found.
5. **Our page holds each brick but not its joint (ours).** At 128 px/m a brick face is about 29×8 texels and a joint 1.3; at 3 m the page is magnified about five times. Bricks as instances everywhere cost two to seven times the near budget. So from 12 m out, shades and history live in the page; near the camera, joints and arrises need another source.

## How the best build it

**Baked bond, runtime variety.**
- *The Last of Us Part I* (GDC 2023): a Substance generator lays any bond into a tile 6 bricks by 20. Flood fill gives each brick a random mask for damage and a slight tilt. Two vertex-colour sets carry broken brick, mould and leaks, then plaster, efflorescence and cracks. "Caps" meshes take the corners.
- *The Division 2* (GDC 2019): a world-space mask breaks up the grime and undulates the normal, "so you'd have some bricks sticking out". Shifts in hue, value and roughness make about eight looks from one brick set.
- *Spider-Man* (GDC 2019): kit walls are blended in layers, newer paint with less occlusion. Far off, Houdini bakes "a very low res version" of each building: kit near and baked page far, shipped.
- *The Order: 1886* (SIGGRAPH 2015): tiling materials with up to four height-blended layers, decal damage, and bevels tiered by distance.

**Bricks as geometry.**
- *Tiny Glade* (Graphics Programming Conference 2024): every brick is an instance on a GPU-driven renderer. Its last level is 6 triangles whose pixel shader intersects a rounded box, so far bricks keep lit bevels. Three-tap contact shadows made the walls read as real. Plaster damage is one float per vertex, the distance to the window (80.lv).
- *Bluepoint* (GDC 2019): a Houdini tool cuts holes in tiling brick walls and places low-poly bricks from the same sculpt, aligned to the UVs.

**Bonds and joints.** Sperl (TU Wien 2013) writes bonds as row grammars and fits openings, but rescales bricks where masons keep the unit and use closers. Legakis and others (SIGGRAPH 2001) lay corners first, then edges, then faces. Parallax occlusion (Tatarchuk 2006) has no silhouettes and drops to plain bumps past a mip threshold. Uncharted 4 (SIGGRAPH 2016) moves detail from geometry to normals to roughness as it shrinks, and shades cracks with microshadow, which we already use (`_OS_PLANE`). Insomniac's Ultimate Trim (GDC 2015) bakes 45° bevels into one strip layout per material.

**Practice in Norway.**
- **Bonds:** *kryssforband* (English cross bond) was "the most common bond in Norway from 1600 to 1900", beside English and monk bond. Stretcher bond is only ever a cavity wall's skin. Solid walls were 2 bricks thick at the ground floor, 1½ above and 1 at the top (SNL). Cavity walls came after about 1890 (MUR 3/2003).
- **Bricks:** Linstow's 228×108×62 mm became the norm, but "5 buildings, 5 sizes from the same mould" (Narvestad 2026). Jæren had works at Sandnes (1783), Malde (1857), Graveren (c. 1852 to the mid-1920s) and Lura (1901–17) (Jærmuseet; Sandnes 2022).
- **Pointing:** flush was the old way, recessed mid-century cement, strap modern (HES Short Guide 6). Walls meant for render kept raked joints. Hard cement joints spall soft brick faces and stand proud (NPS Brief 2; Follo 2009).
- **Render:** KC render was 15–40 mm thick (MUR 3/2003). *Kvaderpuss*, render ruled as ashlar, went on ground floors (SNL). Mouldings were run in place with a profile sledge (Follo 2009); ornament was cast in gypsum and fixed on (Riksantikvaren).
- **Decay:** tight paint turns lime render to gypsum, so it falls in pieces and the drip noses go (ifi.no; Follo 2012). Cement render "can pull the brick face off", and 1960–90 did widespread harm (Riksantikvaren). Rusting iron over windows cracked the render (MUR 3/2003). Patches are cut square to the ruling and the whole elevation repainted (NPS Brief 22). Stavanger Museum's ornament was stripped in 1930 (Stavangeren 1/2001).

## The constraints for us

**The facts.** The house builder takes era, material, bond and coat, and assembles judged parts. `care.py` derives repaints from the record. The era table for the pack (Stavanger unverified where marked):

| Era | Bond | Brick | Mortar | Render | Paint | Repair |
| --- | --- | --- | --- | --- | --- | --- |
| 1850–1903 | cross, solid (unverified) | local red, hand-made | lime | often none, painted as stone | limewash | flush lime |
| 1904–25 | cavity (unverified) | local, then imported | lime, KC | KC, run mouldings, cast ornament | lime, silicate; brick painted red | lime or KC (unverified) |
| 1925–45 | cavity | imported | KC | ornament stripped, rendered over | oil | cement pointing |
| 1945–65 | one brick and board | poor, slurried or rendered | KC, cement | white KC | alkyd, latex (1952) | cement patches, recessed joints |
| 1965–89 | not found | imported | masonry cement | masonry cement | plastic, many coats | hard patches, strap joints |

Sources: SNL; Riksantikvaren; ifi.no; Byantikvaren 2017; Norsk Folkemuseum 2008; MUR 3/2003.

**Screen and page (ours).** At 1440p with a 35 mm lens, a metre covers 700 px at 3 m, 175 at 12 m, 60 at 35 m and 17 at 120 m. A brick face is 160×43 px at 3 m and 40×11 at 12 m. At 35 m it is 14×4: each shade still reads, no joint does, and course lines every 4.3 px risk moiré. At 120 m a course is about a pixel, and only field and bands read, as ref 19 does from across its square.

The page is 2048 or 4096 px at 64–128 px/m (`street.json`); a 4096 BC7 page with mips is 21.3 MiB. Triangle budgets: near (within 10 m) 20–25k, street (from 20 m) 6–8k, city (from 60 m) 500–800.

A 7×7 m house of two storeys has about 7,700 bricks. As flat quads that is 15k triangles; at Tiny Glade's 6 a brick, 46k; bevelled, over 150k. Each instance is drawn up to six times: the prepass, four shadow cascades and the forward pass.

**The frame on the M4.** The eye-level frame is already over budget (21–23.5 ms estimated). Discard or depth offset loses Apple's hidden-surface removal. URP's parallax node makes 2 + steps dependent fetches (about 18–21 a pixel at 16 steps) and may run again in the depth-normals prepass; height belongs in BC4 or R8. The GPU Resident Drawer is off here; it "slightly increases GPU workload" (Unity) and refuses MaterialPropertyBlocks. ASTC and virtual texturing are not available to us.

**Style and history.** Near, ref 11: each brick its own shade, the mortar a lighter network in overcast. Far, a few designed value shapes: the field, the bands, the arches, soot and streaks where water and smoke go. Bricks were mass-produced, so a library is true to D6.4 (disputed), but each wall's bond is laid from the brick's real size and never tiles. Every brick can carry its own history: its shade and works, a replacement and its year, repointing in its decade's mortar, a spalled face beside a hard joint, its coats of paint. Render is a coat over brick, so where it is lost the brick must already be there.

## Approaches worth prototyping

**A. The bond in the page, real bricks only where form needs them.** The generator lays each wall's bond, with real closers and per-brick shade and history, into the page. Near the camera a few 1 mm detail maps (normal and height) and microshadow carry the joints. Real bricks go only at corners, reveals, soldier arches, bands in relief and the edges of lost render, each aligned to its painted brick (Bluepoint; Naughty Dog's caps). Arches, sills, anchors, cornices and quoins are judged parts.

**B. The bond in the shader, the history from the page.** The shader finds each pixel's course and brick by the bond's rule from the wall's UV, and draws the joint analytically, filtered by the pixel's footprint, so it fades to the mean instead of making moiré. It reads each brick's shade, wear, repair year and coat from the page at the brick's centre. Joints stay crisp at every distance for a few ALU and no triangles; false ashlar and quoins are the same function with bigger units. No studio documents this.

**C. Course strips, like the boards' laps.** Each course is a strip whose bed joint is a recess that catches low sun, as the clapboard's laps do: about 700 triangles for a 7 m wall near (ours). Perpends and shades come from A's page or B's shader; the street level reads the laps from the page normal.

**Render, in all three:** a coat over brick on the timber wall's coat stack (`materials-at-scale.md`, "a wall's coats"). Loss follows water: under sills, round downpipes, the plinth's splash, cracked lintels. Patches are square to the ruling and in their decade's mix. Mouldings are profile sweeps, as the run mouldings were; cartouches and stucco come from a cast library.

**The cheapest test that decides:** one 2.4×2.4 m wall corner with a window under a soldier arch, a wall anchor, a red band and a hand's breadth of lost render, built the three ways. Stills in grey at 3, 12 and 35 m, in overcast and in low raking sun, beside crops of refs 11 and 19 and the street's best so far. They show whether single bricks read at 12 m, whether moiré appears at 35 m, and whether the joints hold at 3 m.

## The risks

- **Moiré at 35 m.** Any joint drawn as a line must be filtered.
- **The facts may choose painted brick.** Ref 11's bare hand-made brick may be rare in Stavanger, and yellow brick needs an import.
- **Triangles.** Real bricks everywhere blow the near budget.
- **Cost.** Parallax and discard are costly on Apple's GPU, and the frame is already over.
- **B is invention.**
- **Too clean.** Ref 27 was just restored. Decay must follow water and decades, not noise.
- **Not found:** Stavanger's 1904 zones and when brick compulsion (*murtvang*) ended; when skallmur came; Norwegian sources on segmental arches and dentils; kiln-sorted headers; any Norwegian yellow-brick works.

## Sources

**Studios and papers:** Benainous and Sobotta, The Last of Us Part I materials, GDC 2023; Lauf and Dixon, The Division 2 materials, GDC 2019; Benno, Mullen and McAuliffe, Manhattan look creation, GDC 2019; Phail-Liff and Vitale, The Order: 1886, SIGGRAPH 2015; Stachowiak, Tiny Glade, Graphics Programming Conference 2024 (YouTube jusWW2pPnA0), and 80.lv; House, Houdini at Bluepoint, GDC 2019; Olsen, Ultimate Trim, GDC 2015; Brinck and Maximov, SIGGRAPH 2016; Tatarchuk, SIGGRAPH 2006; Sperl, TU Wien 2013; Legakis, Dorsey and Gortler, SIGGRAPH 2001.

**Practice:** Store norske leksikon (*murverk*, *forband*, *helsteins vegg*, *teglstein*, *finpuss*); Riksantikvaren (*murgårder*, *kalkpussing*, *kalking*); Byantikvaren Stavanger, Kongsgata 47–49 (2017) and Trehusbyen (2021); Stavangeren 1/2001; Jærmuseet; Sandnes kommune 2022; Olsen and Monsen, MUR 3/2003; Narvestad, Bergen seminar 2026; Follo museum 2009 and 2012; Norsk Folkemuseum 2008; ifi.no; HES Short Guide 6; NPS Preservation Briefs 2 and 22.

**Cost:** Unity 6.6 manual; Apple WWDC20 sessions 10603 and 10632; Apple, Metal Feature Set Tables; `reviews/perf/2026-10-27/frame-rate/`.
