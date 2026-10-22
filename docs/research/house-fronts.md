# House fronts: what the shared foundations must carry

Research for the fronts of wooden houses (22 October), written ahead of House A. Next week the gully's port builds the foundations that every kind uses: materials as pack records (port step 4) and levels, chunks, shells and caster proxies (step 5), on top of the history pages. This study asks what the fronts need from those contracts that the stone would never show. It fills gaps only. The subject is already covered by `wooden-town-architecture.md`, `house-changes.md`, `repairs.md` and `fronts-windows-and-signs.md`. The craft is covered by `kits-and-generation.md`, `materials-at-scale.md` and `performance-at-scale.md`. Findings are constraints, not answers. Where a study only gives the safe option, the open creative questions are named.

## In short

A front is coats on boards, and the shared foundations must carry that before House A. Stone hides it. A stone is one material whose history runs from its piece's clocks. A painted front is a substrate under dated coats, and each coat restarts wash, dirt and growth on the region it covers, which is not a piece. So step 4's material record needs two kinds, substrates and coatings, and a coating needs its binder, film, failure and adhesion to what lies under it. A painted face's clock is the year of the coat that shows, worked out per texel from the stack: the fifth clock that D5.4 says would change it. Painted lettering is a coat with a mask, so a ghost sign is an old coat that failure reveals, not a decal.

Step 5 meets features stone lacks. Boards, beads and glazing bars are thin and repeat. Without temporal accumulation they crawl before their geometric error passes a pixel: a 130 mm course is 5 pixels at 50 m, and a glazing bar is one pixel at about 45 m. They are facts (the story pole's courses, the window's pane grid). So the far levels can draw them as band-limited patterns, as D6.10 draws slates, from the same table that builds the near geometry. L0 and L1 never cast, so the shader draws the lap shadows. The caster proxies must keep the eaves, window heads and bays, because eave depth is the era cue that reaches every distance. Clad walls need charts in the wall's plane. Factory windows may repeat (from 1884), but an instance has no page rectangle or stretch channel yet.

The biggest unknown is cost: a front reads four or five pages and a coat stack, and the budget holds three samples.

## What the fronts need from the shared foundations

Each item gives the requirement, why stone does not reveal it, the risk if it is missed, and the decision it touches. The summary table at the end says when each one is needed.

### Step 4: materials as pack records

**1. Two kinds of material: substrates and coatings.** Today `material.schema.json` holds wear and cracking only. D4.2 lists the fields a record will hold (identity, pigment, grain, tooling, water profile, wear, growth affinity, paint failure, and more), but as one surface per material. A front is never one surface. What shows is the top coat where it holds, an older coat where it has failed, and bare wood where all of them have gone. The record therefore needs a kind:
- **substrate:** timber, render, brick, stone;
- **coating:** linseed oil, herring oil, alkyd, acrylic, stain, limewash, tar;
- **glass;**
- **metal;**
- **putty and sealant.**

Fields by kind:
- A **coating** carries its binder, its film build in micrometres, its failure modes, their onset and curves, its drift and its gloss over time. The failure modes are chalking, crazing (linseed's snakeskin after about ten years), flaking, blistering, and peeling in sheets. In drift, light colours go greyer, yellower or pinker and dark ones fade (`wooden-town-architecture.md` §3). It also carries **adhesion by pair**, which says how well it holds on what lies under it. Acrylic over linseed is the known bad pair.
- A **substrate** carries what it does bare (timber greys and checks), whether it traps water under a failed or vapour-tight coat (rot), and how its working takes dirt (unplaned boards hold dirt and mould).

*Risk:* a one-surface schema turns paint into a tint, and the coat stack cannot be written. If Øystein chooses rendered brick for House A, render and limewash need the same split.

**2. Identity comes from facts. Atlases hold shape, never stuff.** The rule that each element keeps its own material identity meets the trim sheet in D4.4 (a board-and-trim atlas, 4 by 1 m at 1 mm). Trim sheets fit unique history, because history lives in UV1's pages, not in the sheet. They only break identity if pigment or grain is baked into them. So:
- the D4.4 atlas holds relief only: normal, height and occlusion of profiles. Its strips are keyed by the profile, which is a part fact (dobbeltfals at 28° or at 60°, staffpanel, a cove);
- grain and pigment come from the material record through UV0's grain coordinate and the family's `Texture2DArray`;
- a timber record is keyed by source and working. Old boards are slow-grown pine, planed. Later ones are spruce, planed, and after 1960 rough-sawn (`wooden-town-architecture.md` §2). Two records share a grain slice only when the facts say they are the same stuff;
- `window/cross-arch.json` names `pine-board` for its frames, but joinery timber (selected and slow-grown) is not cladding board. It should be a record of its own.

*Risk:* a single painted trim sheet would make every house's trim read as one material.

**3. The coat record.** D4.3 says coats are fills with their year, up to eight a wall in a data texture by wall id. The fronts need more on each coat:
- year;
- binder (a coating record);
- colour, as a value in a palette, not a texture slice;
- film build;
- **scope**, meaning where on the front the coat lies. It can be the whole wall, the weather wall, one floor of a two-family house, a class of part slot (field, trim, sash, door), or a list of patches. Trim and windows are repainted on their own dates;
- **preparation:** a wash, scraping of loose flakes, or a full strip;
- an optional **mask** (item 8).

`coat/paint.json` fixes its material as `oil-paint` from 1800. The binder is a fact of each coat, so the part should take it from the fill. Alkyd and acrylic need to be possible on the same part.

**4. Glass by pane.** A pane is a piece with its own placed year, and it takes the glass of that year (`fronts-windows-and-signs.md` §1). So glass is chosen per pane fill, not per part. **Flag:** `window/cross-arch.json` (1905 to 1925) names `crown-glass`. In Norway crown glass ends about 1840, and cylinder glass runs to 1928, so the record should name cylinder glass.

### Repaint and repair as resets

**5. A painted face runs from its coat's year.** `layers.json` resets wash, deposit, splash and contact on "a new coat", and lichen and moss on "a new fill or coat". But D5.4 keeps clocks per piece in the piece table (placed, disturbed, cleaned, reserved). A repaint covers a region that crosses hundreds of boards and several 4 m chunks. On a flaked patch the coat that shows is older than the top one, and its own surface is newly exposed. Writing piece resets for every repaint is the wrong shape. The clock of a painted face is the year of the coat visible at the texel, read from the coat table. D5.4 says it is "changed by a kind needing a fifth clock". This is that kind. *Touches:* D5.4, and the resets and readers in `layers.json`.

**6. The stack is worked out once a pixel, oldest to newest.** At each repaint the scraping removes loose paint. So whether a coat lies on the coat below, on an older one, or on bare wood depends on how far the stack had failed at that date. The edges of old flakes telegraph through later coats as relief (painters' practice, unverified here). This is still a function of record and date (D5.1's "history as a function"), and it takes one pass of eight steps or fewer.

Repaints come every 6 to 8 years (TU) and up to 12 for paint (Klikk), so a 1912 house holds 6 to 13 coats by 1989, and an 1826 house more. The eight-coat limit is reached on most old houses. It needs a rule that collapses coats deterministically. For example, coats buried under a full strip go, and coats older than the eighth merge into one "under" coat that keeps the colour most likely to show. The resolver writes the collapsed stack.

**7. A replaced board shows only coats newer than its placed year.** A new board in a peeling wall reads bare or primed until the next repaint. After that repaint its film stays thinner than its neighbours', so its grain and arrises stay sharper. It is one of the strongest "changed" reads on a front, and it costs one comparison against the piece table.

**8. Painted lettering is a masked coat.** A painted fascia or a sign on boards fails and is painted over like any coat. A ghost sign is exactly an old coat that later failure reveals. So painted marks belong in the coat stack, as a coat with a mask, where the mask is an atlas glyph or shape plus a rectangle in wall-plane coordinates. They should not be geometry. Mesh decals (D4.1) stay for what has its own body and edge, such as paper posters and enamel plates, and for marks on unpainted stone. *Touches:* D4.1 and D4.3, which become one path for painted marks.

### The history budget

**9. The front family reads more than the stone.** The stone reads P0 and H1 (D5.10), at 0.17 ms a sample inside S2's 0.5 ms at overdraw 1, which is about three samples. A painted front needs:
- **P0:** sky and ground seen, and splash from the ground;
- **P1:** weather exposure, the main drive of paint failure;
- **H2:** wash, deposit, splash and contact;
- **the coat table;**
- **H1:** only where algae and moss grow, on north walls and on board ends near the ground.

That is four to five samples, on the kind that covers the most screen at the street stop. The 0.17 ms is a budget, not a measurement: R2 measured a minified sample at about 0.02 ms, and what costs is a busy output. So the line may hold, but it must be measured on a clad wall, not argued from the stone.

Options to weigh: a front page that packs the drives the fronts use; channel meanings per family, so that a painted face does not carry polish; the coat table as a structured buffer read once per wall rather than a sampled texture. *Touches:* D5.10, S2 and the page format in `maps.json`.

### Step 5: levels, chunks, shells and caster proxies

**10. Charts of clad walls lie in the wall's plane.** The pages are addressed by UV1 at every level (D5.2, D6.6). At L0 a lapped wall is a sawtooth. Unrolled, its chart is longer than the wall. Once L1 and L2 flatten the boards into a normal map, an unrolled chart no longer lines up. Charting the wall in its plane keeps a stain on board 7 at every level. The butts get stretched texels, which is acceptable, since they are narrow and mostly in shade. *Touches:* the chart rule in `maps.json` ("per run of one face kind").

**11. A second rule for switching levels, for thin features that repeat.** Levels switch where their geometric error is under about a pixel. A front fails that rule first through aliasing, not through error, because nothing relies on temporal accumulation (D7.2). At 1440p a pixel spans 0.48 mm per metre:

| Feature | Size | One pixel at | At the street stop (20 m) | At 50 m |
| --- | --- | --- | --- | --- |
| Board course (dobbeltfals 19 × 148) | about 130 mm exposure | 270 m | 13.5 px | 5.4 px |
| A lap's step | about 10 to 20 mm (working value) | 21 to 42 m | 1 to 2 px | under 1 px |
| Glazing bar | about 20 to 25 mm (working value) | 42 to 52 m | 2 to 2.6 px | under 1 px |
| A bead's quirk (staffpanel) | about 3 to 4 mm | 6 to 8 m | under 1 px | — |
| Upper water board's projection | 180 mm (Heng) | 375 m | 19 px | 7.5 px |

Thin lines a pixel or two wide, repeated, shimmer and form moiré in motion under MSAA. Mips flatten them to grey. The rule should be: a feature that repeats leaves geometry, and the normal map, before its period or its width reaches a threshold in pixels. It then fades to its mean by footprint, as D5.8 already does for fine marks. The threshold is a working value to measure on one-sample-a-pixel motion sheets (the lesson of the stills rendered at twice the size). *Touches:* the switch rule of the levels scheme and D6.6's motion sheet.

**12. Courses and pane grids are drawn from their facts.** The course layout is a fact the resolver can write. Carpenters set it with a story pole so that courses meet the sill and the head, adjusting the exposure a little per band (Fine Homebuilding). Norwegian old practice varied board widths to fit openings (`wooden-town-architecture.md` §2). A window's pane grid is a fact of its record, and it is an era cue: three panes a sash in classicism, small upper panes in jugend, no bars in funkis. So at L2 to L4 the shader can draw lap lines and glazing bars as patterns band-limited to the pixel footprint. It reads the wall's course table (for a 7 m wall, about 54 integers in mm) and the pane grid. This is how D6.10 draws slate courses and sett rows. L0 and L1 build their geometry from the same table, so the switch matches by construction. Analytic filtering of a repeating pattern over the pixel footprint is a known craft (Quilez, after Apodaca and Gritz). *Touches:* D6.10 (extended from slates and setts to board courses and pane grids), and what L2 means for clad walls ("relief into the maps' normal").

**13. Lap shadows without casting.** The low sun "needs the relief" (D4.4's reason). But L0 and L1 never cast (D6.8), so the shadow line under each lap has no shadow map to come from. URP has no contact shadows. Its Screen Space Shadows feature only resolves the main light's cascades into a screen texture, and it adds a depth prepass. Two routes:
- **micro-shadowing** from the normal map and own occlusion. This is Naughty Dog's Uncharted 4 approach, which HDRP ships as Micro Shadows, for directional light only. We would port it as shader math, since the sun is our directional light. UV4.w already carries own occlusion;
- **an analytic shadow from the profile.** The lap's depth and the course table are known, so the shadow band under each lap can be computed from the sun's angle in the wall's frame, exactly, at every level.

Bend Studio's screen-space shadows (Days Gone) solve the same problem in general. The code is public, but its licence is not stated, and D1.12 ships only permissive code. *Touches:* D6.8, which needs a line saying fine shadows come from the shader.

**14. The caster proxies keep the overhangs.** Eave depth and roof colour are the two cues that reach every distance (`wooden-town-architecture.md` §6). A proxy that loses its eave loses the house's era. A front's mandatory casters:
- the eave and verge, with the barge boards;
- the upper water boards (120 to 180 mm) and the cornice and belt;
- porch and bay roofs;
- chimneys.

The size rule is "at least two texels of the first cascade", a working value, once step 5 sets the cascade. *Touches:* D6.8's caster proxy per chunk.

**15. Openings at every level.** A shell (L3, 500 to 1,500 triangles a house) needs its openings inset, with a glass material class. It also needs a step under the head for its cast shadow, the strongest read of a window at distance. Each glass triangle carries its window's slot, so lit windows at night (D7.5's glow) come from the room's record. Shells have 10 bits of part slot and 6 of material class, which is enough. At about 15 triangles an opening and 20 to 30 openings a house, the openings take about a third of the shell. L4 keeps them in the atlas: a 1.2 m window is 12 pixels at 200 m.

**16. Library parts and instancing.** D6.4 lets only mass-produced things repeat. The fronts have real cases:
- Strømmen Trævarefabrik made doors, windows and mouldings from 1884, and prefab houses from 1887;
- Heng's System 2 blocks (about 1900 to 1915) were band-sawn and identical across whole streets;
- earlier joinery stays unique and fitted.

An instance's history depends on where it sits: the wash below its sill, the failure of its putty, its coats. The facts buffer (record, part, seed, reset year, care, season, wind phase, coat-table offset) has **no page rectangle**, and a library mesh's UV1 is fixed in its FBX. The "stretch" fit (fixed corners, stretchable rails, a sash 10 per cent wider) needs per-vertex weights and a size per instance, and the vertex layout has neither. The instance's page must also be baked from its host's flow field, so the wash is continuous across the seam (D4.1's carriers).

Two ways, to decide in step 5:
- (a) merge the copies into the 4 m chunks at L0 and L1, where chunks are rebuilt anyway and the stretch is done on the CPU, and instance only beyond;
- (b) add about 8 bytes of page address per instance, plus a stretch channel.

*Touches:* D6.7, the facts buffer and the vertex layout.

**17. A repaint invalidates a shell.** At L3 the shell caches pigment with slow history (D5.1b). A repaint changes it. A jump of thirty years repaints most of a street, so the rebake budget (D5.4b, 2 ms on the GPU for each 1024 × 512 page, behind the dated card) must hold a whole street at once. *Touches:* D5.4b's number, measured with a street, not one thing.

**18. Picking and the id test.** The topmost visible coat or painted sign at a pixel must pick its own record. The coat is not a piece, so the id render (`_OS_BAKE`'s ids) must work out the coat stack too. *Touches:* step 5's id test.

**19. Where paint fails first must be in the channels.** Paint and wood fail first at end grain, drip edges, arrises, board ends and the boards under sills (`wooden-town-architecture.md` §3). So the face-kind enumeration, which is not yet written, needs end grain, drip edge, putty and glass. Edge distance (UV3) must also be computed on the profile's arrises and board ends, not only on a piece's outline.

**20. Gloss on thin trims needs specular anti-aliasing.** Fresh oil and alkyd are glossy, and a trim or a glazing bar is thin. The front family needs geometric specular anti-aliasing: a roughness floor from the derivatives of the normal (Vlachos 2015, Kaplanyan 2016), and Toksvig-style roughness from the variance of the normal map at L2. Kaplanyan warns that both change how a material looks on surfaces of constant curvature, so the rule is judged in grey light. Smoothness is per coat, by binder and age, not per material.

### Summary: which decisions the fronts change

| Decision | Change the fronts ask for | Needed by |
| --- | --- | --- |
| D4.2 (material record) | substrate and coating kinds; binder, film, failure, adhesion by pair; timber keyed by source and working | port step 4 |
| D4.3 (coats) | scope, preparation, film, mask per coat; a deterministic collapse past eight | step 4's schema; used at House A |
| D4.4 (board-and-trim atlas) | relief only, keyed by profile; no pigment or grain | step 4's editor step |
| D4.1 (decals) | painted marks become masked coats; mesh decals for posters and plates | House A |
| D5.4, `layers.json` | a fifth clock: the visible coat's year, per texel | before House A; noted now |
| D5.10, S2 | the front family's four to five samples, measured on a clad wall | step 5's harness |
| Charts (`maps.json`) | clad walls charted in the wall's plane | step 5 |
| Levels switch rule, D6.6 | a second rule for thin features that repeat | step 5's motion sheet |
| D6.10 | extended to board courses and pane grids | step 5 (the rule); House A (the tables) |
| D6.8 (casters) | mandatory front casters; fine shadows from the shader | step 5 |
| D6.7, facts buffer, vertex layout | a page address and stretch for library parts, or copies merged at L0 and L1 | step 5 |
| Shell format | inset openings with glass class and slot | step 5's shell |
| Id test | coats and painted signs pick their records | step 5 |

## The gaps this closes

The coverage row for buildings named subject and craft studies, but none covered:
- how coats reset history, and how a repaint is a clock;
- painted marks against decals across levels;
- library parts against per-instance history;
- thin features that repeat, at distance without temporal accumulation;
- shadows of laps when near levels do not cast;
- what the material record must hold beyond stone;
- repaint practice and its cycle.

Still open from earlier studies are measured window sizes, the 1989 to 2020 content and the paint failure rates on this coast. Their state is in the last section.

## Craft findings

- **Trim sheets.** Insomniac's Ultimate Trim and Burns's trim-sheet method (already in `materials-at-scale.md` and `kits-and-generation.md`) let a material swap re-date a part without new UVs. Our layout already gives history its own UV1, so the conflict is only with identity, and item 2 solves it.
- **Decals.** DOOM (2016) keeps decals in an atlas and applies them in the forward pass for opaque geometry, "directly when meshes are rendered". Each pixel reads its cluster's decal list, and each cluster holds up to 256 decals (Courrèges's frame study). That is the shape of item 8: marks read in the host's shader from a list, not drawn as geometry. URP's Decal Projector does not support the SRP Batcher (it uses material property blocks, which we rule out) and does not project onto transparent surfaces (Unity manual). So it is out for glass and for the Resident Drawer, which confirms D4.1's limit to transient state. Cyberpunk's mesh decals draw only the triangles that carry decal texture (`performance-at-scale.md`). On boards, a mesh decal made against L0's sawtooth floats or z-fights by the lap's depth once L1 flattens it (our reasoning).
- **Kits at scale.** A level artist on Assassin's Creed Syndicate describes an architecture kit of hundreds of modules beside many unique buildings, with roof connection modules repeated to any length (Polycount, read through a search summary only; the page refused us). Insomniac's Manhattan talks describe procedural tools for marking up the city. In text they give nothing on facades: their detail is in the videos, a gap.
- **Fine shadow.** Naughty Dog's micro-shadowing, as HDRP's Micro Shadows, estimates small shadows from the normal map, ambient occlusion and specular occlusion, for directional lights only (Unity manual). Bend Studio's screen-space shadows complement shadow maps with distant detail. Days Gone was its first sunlit title, and the code is public with no licence stated. URP's Screen Space Shadows feature is not contact shadows (Unity manual).
- **Specular aliasing.** Kaplanyan (GDC 2016) frames sparkle as a shading problem from small highlights. He cites Toksvig's fit of normal spread, and Vlachos (GDC 2015) for a roughness floor from screen-space derivatives. Vlachos's slides could not be read as text, so his method is known here only through Kaplanyan and secondary accounts.
- **Filtered procedural patterns.** Quilez filters checkerboards and grids analytically over the pixel's footprint, after Apodaca and Gritz's treatment of pulse signals, without textures or mips. Golus's grid shader argues over the right derivative measure. Both are known through a search summary; neither page was read.

## Subject findings (only what bears on the contracts and House A's first sheet)

- **Courses are laid out from the openings.** Carpenters mark the exposures on a story pole, adjust them so the courses meet the window bottom and head, and transfer the marks to every corner and trim. Courses that line up with openings look better and perform better than courses notched round them (Fine Homebuilding). With Norwegian practice of varying widths to fit openings, this makes the course table a function of the facade grid (item 12).
- **Profiles.** The old dobbeltfals has a 28° bevel and the newer one 60°. The old profile comes from Vestlandet and is sold today as 19 × 148 spruce. "Matching" cladding varies by about ±2 mm, and old houses carry boards of varying widths, planed and unplaned (retailer and forum; secondary).
- **Repaint cycle.** Wash and paint every 6 to 8 years (TU, a practitioner's estimate). Paint lasts up to 12 years, and stain needs about twice as often (Klikk). Byggforsk's 700.320 (intervals) and 742.301 (upkeep of exterior timber cladding) hold the real figures, but they are paywalled and unread. Linseed crazes after about ten years and holds 30 to 40 before it breaks (SLKS, already in the repo).
- **Preparation.** On protected houses Riksantikvaren usually allows only scraping of loose flakes. A full strip is accepted only by the infrared method, and changing the paint type needs a dispensation. In 2024 alkyd was refused in place of linseed in Langesund's old town hall (Riksantikvaren decision; through byggebolig). Thorough scraping is usually enough, and old layers may hold lead white (Brænne). Pressure washing should be avoided on older houses, since water gets behind the cladding (Jotun). So protected houses keep deep stacks of one binder, while unprotected owners of the 1970s and 80s laid plastic over oil.
- **Plastic over oil.** On old unventilated cladding, vapour-tight water-borne paint is said to trap moisture and cause rot. That comes from forum discussion of a Bygg og Bevar article, and it is disputed. Treat it as a candidate adhesion and rot rule (item 1), unverified.
- **Factory joinery.** Strømmen Trævarefabrik (from 1884) made doors, windows, stairs and mouldings, and prefab houses from 1887. It was one of the largest exporters of prefab houses around 1900, burned in 1919 and went bankrupt in 1929 (lokalhistoriewiki, SNL). Local joinery works followed, such as Christoffersen in Mosjøen (1909) and Lunde in Lillestrøm (1919). This backs D6.4: factory joinery repeats after about 1884, and earlier joinery is unique.
- **The weather wall.** No climatology for Stavanger's driving rain was found. Forecast pages show south-east and west-south-west winds, which settles nothing. Met.no's normals (Seklima) are the source for `climate.json`.

For **House A's first sheet** (1912 jugend: beaded boards with vertical fields, small upper panes, a 1931 shopfront with a lettered fascia, a café in 1988), this means:
- the bead's quirk is sub-pixel beyond about 8 m;
- the upper glazing bars go below a pixel at about 45 m;
- the fascia's lettering is a masked coat that the café's repaint buries and failure may reveal;
- the stack from 1912 to 1989 is 6 to 13 coats, which needs the collapse rule;
- if the house is rendered brick instead, the substrate and coating split covers render and limewash.

## Open creative questions

- **How boards read beyond the street stop.** Every lap line, a few soft strokes as a painter would put them (the painted far town), or only a value change at each course? The study says only what must not happen: crawling.
- **Whether paint build reads age.** An old house repainted still has softened arrises and filled grain, while its new board stays sharp. Can a viewer tell an old repainted front from a new one by film alone?
- **Lap shadows:** analytic from the profile, against micro-shadowing from maps, judged in grey light at a low sun.
- **Flaking at eye level.** Film edges a tenth of a millimetre thick, as relief or as value, and how loud, given the rule that a vivid sign must not be read as the whole story.
- **Ghost signs.** How much of an old coat shows, and how a viewer can tell it is old rather than current. It is perceived information, a record that may be wrong.

## What stays unknown, and where it is learned

| Unknown | Why it matters | Where it is learned |
| --- | --- | --- |
| The front family's cost: coat stack plus four to five samples | the biggest risk: fronts fill the street stop | a synthetic clad wall in the port's harness at step 5, before House A's sheet |
| The pixel threshold for moving thin features to patterns | the switch rule (item 11) | one-sample-a-pixel motion sheets at step 5's first switch |
| The first cascade's texel and which casters survive | item 14 | step 5's caster proxies |
| Merged copies or instances with page addresses | item 16 | the scale test's memory for close chunks, step 5 |
| Repaint intervals and failure rates on this coast, by binder | coat stacks and collapse | Byggforsk 700.320 and 742.301 (paywalled: does Øystein have access?) or a painter's account; until then authored values marked as such |
| Stavanger's weather wall | the failure drive in P1 | met.no's normals, for `climate.json`, before House A's weathering |
| Measured window and door sizes | House A's parts | Heng's 1:10 drawings and the city archive's photographs (an existing gap) |
| Bend's code licence | whether its screen-space shadows could ship | the archive's licence file; fetching it is a download that needs Øystein's OK |
| What owners did from 1989 to 2020 | the content after the start year | the existing gap in `house-changes.md`, before plan step 4 |

## Sources

Read once each, in this pass. Primary means the maker's own account or an official document. Secondary means a report of it or a practitioner. Unverified means a forum, a search summary or a page we could not open.

Craft:
- Adrian Courrèges, [DOOM (2016) graphics study](https://www.adriancourreges.com/blog/2016/09/09/doom-2016-graphics-study/): decals in an atlas, cluster lists (secondary, from frame captures).
- id Software, Siggraph 2016 idTech 6 slides: over 10 MB, not fetched.
- Unity, [URP Decal Renderer Feature](https://docs.unity3d.com/6000.0/Documentation/Manual/urp/renderer-feature-decal.html) (primary).
- Unity, [URP Screen Space Shadows Renderer Feature](https://docs.unity3d.com/Manual/urp/renderer-feature-screen-space-shadows.html) (primary, through a search summary).
- Unity, [HDRP Micro Shadows](https://docs.unity3d.com/Packages/com.unity.render-pipelines.high-definition@17.0/manual/Override-Micro-Shadows.html) (primary).
- Bend Studio, [Inside Bend: screen space shadows](https://www.bendstudio.com/blog/inside-bend-screen-space-shadows/) (primary; code licence not stated).
- Kaplanyan, [Stable specular highlights, GDC 2016](https://developer.download.nvidia.com/gameworks/events/GDC2016/akaplanyan_specular_aa.pdf) (primary, through a search summary).
- Vlachos, [Advanced VR Rendering, GDC 2015](https://media.steampowered.com/apps/valve/2015/Alex_Vlachos_Advanced_VR_Rendering_GDC2015.pdf): text not extractable, known through Kaplanyan (secondary).
- 80.lv, [Marvel's Spider-Man: a technical postmortem](https://80.lv/articles/marvels-spider-man-a-technical-postmortem) (secondary; no facade detail).
- Polycount, [Assassin's Creed Syndicate industrial kit](https://polycount.com/discussion/comment/2386999/): 403, through a search summary only (unverified).
- Quilez, [Filtering checkerboards](https://iquilezles.org/articles/checkerfiltering/), and Golus, [The Best Darn Grid Shader (Yet)](https://bgolus.medium.com/the-best-darn-grid-shader-yet-727f9278b9d8): both through a search summary (unverified).

Subject:
- Fine Homebuilding, [Keep siding straight with a story pole](https://www.finehomebuilding.com/project-guides/siding-exterior-trim/keep-siding-straight-with-a-story-pole) and [How to install clapboard siding](https://www.finehomebuilding.com/project-guides/siding-exterior-trim/how-to-install-clapboard-siding) (practitioner; through a search summary).
- Byggforsk, [Drift, vedlikehold, reparasjon](https://byggforsk.no/innhold/452/drift_vedlikehold_reparasjon_ombygging): 700.320 and 742.301 named, contents paywalled.
- TU, [Trenger ikke maling](https://www.tu.no/artikler/trenger-ikke-maling/322376) (secondary).
- Klikk, [Sånn velger du maling eller beis](https://www.klikk.no/bolig/vedlikehold/sann-velger-du-maling-eller-beis-2478985) (secondary).
- Riksantikvaren, [Langesund gamle rådhus, klageavgjørelse 2024](https://riksantikvaren.no/content/uploads/2024/12/24_03974-2-Langesund-gamle-radhus-Cudriogarden-Klageavgjorelse-Maling-av-eldre-innvendi-633001_6_0.pdf) (primary, through a search summary).
- Byggebolig forum threads on Riksantikvaren's scraping rule, [plastic paint](https://byggebolig.no/eksterior-tak-ytterkledning-og-maling-(ute)/du-maler-det-rattent-bygg-og-bevar-riksantikvaren-om-plastma-1) and [dobbeltfals profiles](https://byggebolig.no/eksterior-tak-ytterkledning-og-maling-(ute)/bytte-panelbord-i-dobbel-fals-med-staff) (unverified).
- Karmøy kommune, [Praktisk malerarbeid](https://karmoy.kommune.no/_f/i97c5bec3-4a30-4c8d-93bf-bc378b92a320/2017-praktisk-malerarbeid.pdf) (Brænne's guidance; secondary, through a search summary).
- Jotun, [Linoljemaling](https://www.jotun.com/no-no/jotun/decorative/exterior/products/jotun-linoljemaling) (maker).
- Lokalhistoriewiki, [Strømmen Trævarefabrik](https://lokalhistoriewiki.no/wiki/Strømmen_Trævarefabrik), [Alfred Lunde & Sønn](https://lokalhistoriewiki.no/wiki/Alfred_Lunde_%26_Sønn._Snekkerifabrikk_(Lillestrøm)) and [Christoffersens Snekkerverksted](https://lokalhistoriewiki.no/wiki/Nygård_(snekkere_i_Mosjøen)) (secondary).
- SNL, [Strømmen Trævarefabrik](https://snl.no/Str%C3%B8mmen_Tr%C3%A6varefabrik) (secondary).
- IFI, *Farger til hus i sveitserstil og andre gamle hustyper* (Owren): text not extractable.

Two PDFs, Vlachos's slides and the IFI colour guide, were saved automatically by the fetch tool as binaries in this session's tool results. They were not opened or read, since a download needs Øystein's OK.
