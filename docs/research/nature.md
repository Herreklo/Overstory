# Nature with a history

Forests, heath, paths, walls and weather, generated so that the landscape remembers what people did in it. Part of the Game Lab research. Items from general knowledge are marked unverified.

## One ground-wear field

Footpaths, desire lines, scuffs at a crime scene and old sunken lanes all come from one model. Helbing et al. (Nature, 1997): each footstep raises a patch of ground's wear, with diminishing returns; unused ground recovers over a set time; walkers balance the direct line to their goal against nearby trails. One parameter decides between direct routes and a shared minimal network. Fed by the engine's walks, every path is a true fact.

Real numbers to tune against: about 10 to 25 people make an informal trail visible (Wikipedia cites about 15); on subalpine heath, 150 passes cut plant cover to about 59%. After walking stops, grasses and deciduous dwarf shrubs recover in about 2 years and evergreen dwarf shrubs in about 3, while mosses were still not recovered after 3 years. A visible path draws more walkers. Sunken lanes form from traffic and runoff, some within a decade or two, up to about 5 m deep.

**Moss is the long memory.** Because moss recovers slowest, a scuff in moss stays readable for years. That makes it the murder mystery's forensic clock: the age of a disturbance can be read from published recovery rates, so a clue is fair.

## Vegetation over time

**Plants as competing circles.** Deussen et al. (1998) model each plant as a circle of influence. Where circles overlap, the weaker plant is dominated and may die; strength comes from size and how well soil moisture suits the species; each species needs five parameters. The rules reproduce real self-thinning, and wet- and dry-loving species sort themselves apart. Rendering clusters similar plants and builds only representative models. This is a direct template for planting stands from land-use history.

**What was the land before?** The species and stages depend on it:
- Coastal heath is Norway's oldest cultural landscape, about 5,000 years old, kept open by year-round sheep grazing and burning every 15 to 20 years. Heather runs through four phases: pioneer (0 to 6 years), building (6 to 14), mature (14 to 25), degenerate (25 and older, with a collapsed centre). Abandoned, it goes to juniper and dwarf birch, then birch, then pine, spruce or planted Sitka spruce. Mass spruce planting began in the 1950s. About 80% of Europe's coastal heath has been lost in a century.
- Clear-cuts regrow birch-dominated, with rowan and spruce below (a Czech study at 13 years). Norwegian rotation ages are unverified.
- Abandoned pasture returns to birch first by sprouting near existing forest, away from the heavily grazed farmyards.

Heavier models (Synthetic Silviculture, 2019; Ecoclimates, 2022) show stand structure and forest edges emerging from competition and climate. We take the ideas (edges, slope, crown shape from history), not the full simulation.

## Traces of people

- Stone walls in New England mostly date from 1775 to 1825, built from cleared fields and frost-heaved stones. Abandoned pasture went quickly to pine and then hardwoods, and brush can hide a wall within about a decade. Lidar reveals whole networks of walls and roads under today's forest. Walls read best in January, with snow outlining them and low sun casting shadows. A dumped pile at a field edge and a carefully relaid double wall tell different stories.
- Lichen dates stone. *Rhizocarpon geographicum* grows about 0.3 to 0.9 mm a year, so lichen size on walls, cairns and foundations shows how long a surface has been exposed.
- The landscape is a palimpsest: field, then heath, then birch, then spruce, while the wall, the cellar hole and the track remain.

## Nature as a story space

- Theme-park storytelling (Carson, 2000): cause-and-effect vignettes, revisited places that have changed, following the trail of someone who went before, light and detail spent only on what matters.
- Forensic botany uses pollen, moss on shoes, tree rings and roots to set time and place.
- Clues that follow from the wear model: broken undergrowth, moss scuffed off a rock, a fresh path through heather, a disturbed patch where grass has regrown but moss hasn't.
- Fairness: Obra Dinn confirms answers only in sets of three to stop guessing. The same works outdoors.
- First snow reveals hidden things. Finnish planners read where people walk from footprints in the first snow, and old walls show under snow. That is a ready-made mechanic.

## Rendering

- Firewatch: colour in depth layers with fog, a sky that can fill half the screen, 23 hand-modelled tree types, and a sky built from a few parameters so time and weather can change live.
- Soft foliage: copy normals from a stretched hemisphere onto leaf cards so a crown shades as one soft mass; flip back-face normals; project ground normals onto moss. Blender can do this transfer.
- Ghost of Tsushima grows individual grass blades on the GPU, each animated.
- Unity 6's GPU Resident Drawer suits trees and rocks; grass needs its own test.

## Weather and light at 59°N

- Rain: Bergen's 1991 to 2020 normal is 2,495 mm a year, with roughly 170 to 235 wet days. Drizzle as the default is accurate.
- Light in Stavanger: about 6 hours of daylight in December (sunrise about 09:28, sunset 15:40) and about 18.5 hours in June, when the midnight sun sits only 5 to 7 degrees below the horizon and the sky stays near twilight all night.
- Autumn colour: yellow comes from carotenoids revealed as chlorophyll breaks down; red comes from anthocyanins made in bright light, strongest after bright days and cold, non-freezing nights. So each autumn's redness depends on that year's weather, which fits "every difference is a fact".
- Determinism: each day's weather comes from a hash of the world seed and the day plus the season's climate statistics, never from a running random stream.

## Nature-layer cheat sheet

| Element | Speed | Cause | 1 year | 10 years | 50 years |
| --- | --- | --- | --- | --- | --- |
| Footpath on heath | Fast | Walking (about 15 passes) | Bare line, moss gone | Used: worn groove. Abandoned: grass back, moss patchy | Used: a sunken lane begins (unverified). Abandoned: a faint line, seen only in snow |
| Clear-cut | Medium | Logging | Stumps, slash, herbs | Birch and rowan thicket, spruce under it | Spruce stand nearing harvest |
| Heath after burning | Fast to medium | Burning and grazing | Black, resprouting | Building-phase heather | Abandoned: juniper, birch, then conifers |
| Abandoned field | Medium | Farm ends | Grass seeds in | Brush; wall hidden | Birch or pine forest over the wall |
| Stone wall, foundation | Very slow | Built once | Crisp | Lichen starting | Lichen patches about 1.5 to 4.5 cm |
| Autumn colour | Yearly | Day length, cold nights | Varies with each year's weather | | |

## Sources

[Deussen et al. 1998](https://pharr.org/matt/assets/ecosys.pdf) · [Synthetic Silviculture](https://research.google/pubs/synthetic-silviculture-multi-scale-modeling-of-plant-ecosystems/) · [Ecoclimates](https://wp.faculty.wmi.amu.edu.pl/papers/Palubicki.etal-2022-Ecoclimates.html) · [Ecormier-Nocca et al. 2021](https://history.siggraph.org/?p=121220) · [Kystlynghei](https://snl.no/kystlynghei_-_naturtype) · [Viking landscape](https://partner.sciencenorway.no/bioforsk-cultural-history-farmland/the-viking-landscape--an-endangered-habitat/1376661) · [Calluna (USDA FEIS)](https://www.fs.usda.gov/database/feis/plants/shrub/calvul/all.html) · [Clear-cut succession](https://jfs.agriculturejournals.cz/artkey/jfs-202001-0004_spontaneous-development-of-early-successional-vegetation-improves-norway-spruce-forest-soil-after-clear-cutting.php) · [Hogstklasser](https://snl.no/hogstklasser) · [Birch return](https://ideas.repec.org/a/taf/clarxx/v42y2017i1p63-77.html) · [Helbing et al. 1997](https://ar5iv.labs.arxiv.org/html/cond-mat/9805158) · [Trampling study](https://www.sekj.org/PDF/anbf43/anbf43-129.pdf) · [Desire path](https://en.wikipedia.org/wiki/Desire_path) · [Hollow way](https://en.wikipedia.org/wiki/Hollow_way) · [New England stone walls](https://www.earthmagazine.org/article/history-science-and-poetry-new-englands-stone-walls) · [Lichenometry](https://en.wikipedia.org/wiki/Lichenometry) · [Carson, environmental storytelling](https://www.gamedeveloper.com/design/environmental-storytelling-creating-immersive-3d-worlds-using-lessons-learned-from-the-theme-park-industry) · [Forensic botany](https://en.wikipedia.org/wiki/Forensic_botany) · [Firewatch](https://80.lv/articles/creating-the-world-of-firewatch) · [Ghost of Tsushima grass](https://gdcvault.com/play/1027214/Advanced-Graphics-Summit-Procedural-Grass) · [Foliage normals](https://polycount.com/discussion/comment/2677432) · [GPU Resident Drawer](https://docs.unity3d.com/6000.0/Documentation/Manual/urp/gpu-resident-drawer.html) · [Bergen climate](https://www.bergen.kommune.no/omkommunen/fakta-om-bergen/klima/tall-som-beskriver-klima-i-bergen) · [Stavanger daylight](https://www.gaisma.com/en/location/stavanger-sandnes.html) · [Autumn leaf colour](https://en.wikipedia.org/wiki/Autumn_leaf_color)
