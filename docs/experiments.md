# Experiments

Newest first. Each entry: the question, how it is judged, then the outcome: what we keep, what we drop, and for each reference that came up, what we take and what we leave.

---

## LT3: the street through the years

**Status:** planned, after LT2. The question and the rest of the entry are written when it starts.

**The bar:** a cold reader, shown each frame of a house through the years, can date it to within a decade and say what happened to it.

**Before it, a research pass:** what owners did to houses from 1900 to 1989, decade by decade: recladding, stripped ornament, new windows and doors, extensions, roofs, add-ons, signs and ageing. It becomes the diary's event vocabulary (`docs/building-system.md`, The diary) and the era shelves.

---

## LT1: the harbour street, 1989

**Status:** open.

**The question:** what makes a west-coast harbour town stunning from the city view, and does it hold up in ordinary light?

**The setting:** a fictional harbour town rooted in the Norwegian west coast, in 1989: three years after the oil-price crash, a boom town in a slump. White timber houses, quay warehouses, cobbles, 1980s shopfronts and streetlamps, some shops empty. The town in its landscape: it steps up from the quay, with hills, mountains and the fjord behind.

**What is built:**
- The building system's first version (`docs/building-system.md`): building diaries from fixtures, a resolver, and era shelves of parts for timber houses and a quay warehouse. Stylisation is a set of parameters; the strength is stronger.
- A hero slice, authored in the fixture for one camera: the quay with the Anchor and the oxred warehouse, the town stepping up behind in two or three levels with a stepped lane, and hills, mountains and the fjord mouth as layered landforms.
- The city camera: perspective, not isometric, free to orbit. Its tilt follows its zoom: steep and map-like far out, the horizon in frame at the middle stop, just over the rooftops close in.
- Light as a colour script keyed to facts (date, hour, weather, so sun height and cloud): one mood manager blends sun, sky, shadow colour, the colour of the air by distance, ambient light and grade.
- Two looks on the same geometry: A plain URP Lit (control) and B painted ramp (shadow colour from the light, flat wet colour). C soft toon and D graphic only if B disappoints. Everything else is shared: palette, wetness, glow, atmosphere, grade.

**How it is judged:**
1. *Shape step, in Blender:* done; the strength is stronger.
2. *Clay pass:* the hero slice in grey clay from the city camera at its middle stop, with a few variants of height and angle. Judged on composition, silhouette and layering only. A yes is a frame that has its bones in grey.
3. *Hero frame:* blue hour at the middle stop, look B against A, side by side with a north-star reference Øystein picks. A yes is a frame Øystein finds stunning.
4. *Colour script:* the hero frame across one October day (low morning sun, grey noon, golden late afternoon, blue hour, night) and the same hour through the year (December, March, June, October), each also in greyscale. A yes is a town beautiful because of its light, with ordinary light holding up.
5. *Robustness:* the hero frame in grey drizzle, and at the far and close zoom stops.
6. *Variety check:* the generator on 30 fresh diaries. No two alike; everything that reads as history traces to a diary entry, and seeded texture claims none; the same diary gives the same building after a reload.

**What it does not test:** people, interiors and scenes, history over time, snow cover, the final palette, and surface texture and wear (until a look is chosen).

**Shape step, so far (19 October):**
- Øystein picked strong over gentle.
- Wild is dropped. Its proportions were the attraction; its deformation (a lean of up to 4.5°, up to half a metre of sag, bowing walls) read as caricature and broke construction: walls stood outside roofs.
- Stronger is added: wild's proportions with strong's deformation. Strong and stronger are compared on the same street.
- The first wild sheet went out with a known fault. Since then, building checks and a stress test gate every sheet: 1,564 random buildings at strong and stronger pass, and the street fixtures pass in every year.
- A blind reviewer found what the checks could not see: floating ridge caps, merged double chimneys, window heads hidden by deep eaves, dangling barge ends, and bays that hit porches, cross-gables and the eave. Each became a rule (`docs/building-system.md`, Fitting), and bays became checked parts.
- Øystein picked stronger over strong. It is the default strength (`blender/resolver/eras.py`) and the shape language for the street. This ends the shape step.

**Unity step, so far (19 October):**
- The Unity 6 URP project is set up from code (`unity/Assets/Code/Editor/LT1Setup.cs`). Blender exports the street at 1989 (`blender/tools/export_street.py`); Unity places it and generates the ground. An axis check guards the hand-over: Unity's x, y, z is the street's x, z, y.
- The fixture has an authored street block (bands, lamps of three eras, bollards, the ground behind) and the lit floors at blue hour.
- At stronger proportions neighbours overlapped and porches stood in the road. The plots are re-spaced with at least 1.2 m clear, and the building line now holds what stands on the ground (steps, porches, bays), as a real building line does.
- Look A is URP's own lighting on a surface every look shares: palette, wetness by porosity, puddles on paving, window and lamp glow, our own height fog. Screen-space reflections are on.
- Checkpoint (`reviews/lt1/checkpoint/`): look A in drizzle from both cameras, exposed for the white walls, with greyscale copies. A fresh reviewer's findings were fixed at the cause: doors differ from their walls in lightness (a resolver rule), puddles lie only on paving, distant setts average to one tone instead of speckle, bollards stand on the coping, and the world carries on past the street's ends.
- Open: every surface is one flat colour per face, so everything reads as plastic. Also warehouse roofs without tile courses, steps the same value as their plinths, and the empty hillside behind the row (the fixture has nothing there).

**Plan revised (19 October):**
- The look A checkpoint showed the street's bones, not a look. Flat colour under physical lighting reads as plastic; one row on an empty plane makes no picture; and grey drizzle is the light to prove a look in, not to find one. The plan narrows: find stunning first in one composed frame in the most favourable light, then test it in ordinary light.
- The street-level camera leaves LT1. Eye level is closer than the city view, and scenes are their own subject, not yet discussed.
- References that came up:
  - *Overland:* take the high camera, flat colour, a strong colour script and the world dimmed outside the area in play; leave the cut-earth board edge.
  - *A lit cutaway of a warehouse home:* take warm interior light against a dark outside. Whether the closest zoom ever opens buildings stays open.
  - *A Coober Pedy overview:* take the density of props and the soft contact shadows; leave realistic ground textures for now.
  - *Firewatch:* take a colour script per hour and the air coloured by distance; leave saturating everything, since our base stays muted.

**Clay pass, so far (19 October):**
- The hero slice is authored in the fixture: two levels above Harbour Row with fifteen houses (older and smaller higher up), dry-stone retaining walls, lanes, a stepped lane from the quay, the hillside, hills on both sides of the bay and mountain ridges. The export checks gaps per level and keeps the stepped lane clear. Unity generates the terrain; a clay switch turns every surface one matte grey.
- First frames (`reviews/lt1/clay/`): the frontal middle stop is dull. Views along the shore, oblique, read in layers and are far stronger.
- Straight parallel terraces with houses in rows read as a stage. A bay with hills close on both sides gives the town a setting.
- Ridges built as extruded strips read as curtains, not rock: landforms need a real terrain generator.

**Look sketch, so far (20 October):**
- The research's shared foundations are in: what each face sees (sky, open ground, openness) is baked into every part by the generator; a sky term built from it; air in a designed colour ramp by distance (near, middle, far, as Firewatch's fog), thicker low down so hills grade from a hazy foot to a clearer crest.
- The ground is a height field generated from a few site facts (the bay, the hills beside it, the hillside behind, seeded roughness); the terraces fill the bay.
- Look D, the most promising: light cut into flat plates in the light's own colour (each plate one exposure step), thin indigo key lines on real edges, fading with distance. Carving and white-line engraving were tried and dropped: they read as pattern laid over the picture.
- The camera moved into the village, over the quay at roof height. From a distance the town read as a model; close, it reads as a place.
- Two lights carry it: blue hour (indigo air, warm windows) and a hot summer evening (low sun on the harbour fronts, warm haze). Frames in `reviews/lt1/looks/`.
- Cloud light: the weather's clouds cast their shadows along the sun from a layer overhead, so the low sun falls on the town and the land in pools (after a SEASON harbour still). Shade in look D takes a richer version of the sky's colour. Land and mountains are crisp facets that catch the light plane by plane.
- Open: the sky is still a plain gradient, where the references put half their drama (clouds with volume, light breaking through); the land is underworked; the shore is a straight line.

**Direction chosen, and where it stands (20 October):**
- Øystein chose painterly realism, with Simon Stålenhag leading (`docs/visual-direction.md`). Look P is its first version: soft wrapped light, shade in the sky's colour, a warm turn at the shadow's edge, muted base colours, world-fixed brushwork, grime where surfaces see the ground. The town was exported at real proportions (gentle) for it; real proportions read as a place where stronger read as a toy village.
- Trees: a first Blender generator (four species, autumn colours, size from planting year). Judged poor: made quickly, without the care the houses had.
- Øystein's verdict: the scene is now the limit, not the shading. The town's structure is weird and boring (rows on flat terraces), it has no logic and no places where light can do something (lanes, squares, gaps, overhangs), and the nature is a placeholder. Next: give the town a believable structure and the trees the same care as the houses, then judge look P again.
