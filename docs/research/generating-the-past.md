# Generating the past

How a town gets 150 years of believable, explainable history before a game starts. Part of the Game Lab research; see "A world that remembers" for the core building system.

## The idea

The past is an event log, not a simulation we replay. Every fact about the fabric (a street laid out, a plot split, a house built, a fire, a plan adopted) is a dated event that names its cause. Starting a game in any year is a query: take every event up to that year. The people simulation then appends to the same log.

## Principles

**Grow in eras, not with one rule.** Emilien et al. (2012) generate villages from a *growth scenario*: a list of timed events, each of which changes the village's type or seeds buildings. A fishing village is one of their worked examples. Each era brings its own street pattern, building types and weights for where people want to build. Beneš et al. (2014) show the same at city scale: minor streets follow a pattern that changes over time, so older districts look different from newer ones.

**Buildings first, then the road to them.** In Emilien's method each new building is placed by interest (road access, slope, water, neighbours) and joined to the network straight away by a path that prefers reusing existing roads. Its plot is claimed from its street frontage. Roads across hills follow Galin et al. (2010): a cost-weighted path over slope, water and curvature.

**Layers by how long they last.** Streets change slowest, then plots, then buildings, then uses (Conzen; Whitehand). The fabric cycles on plots that hardly move.

**Plans are dated layers, carried out piece by piece.** A plan claims geometry (a wider street, a building line, a new road) and is carried out only when a plot it touches changes hands or burns. That produces the visible scars of half-done plans: a street widened at one end, stepped building fronts, a lone modern block. Real precedents: Oslo dropped its 1624 masonry rule within a year and its poor suburbs stayed wooden; Boston set a harbour line that wharves filled up to. Lipp et al. (2011) store layouts as layers with anchored edits, which is the technical model.

**Fires reset the plan.** After Trondheim burned in 1681, Cicignon cut streets about 38 m wide where 15 m streets had failed to stop fire. Ålesund burned in 1904, was rebuilt in Art Nouveau, and Norway finally enforced its masonry requirement (murtvang). Stavanger lost 250 buildings in 1860. A fire event triggers a regulated replan of the burned area: wider streets, fire lanes, masonry from a set year.

**Waterfronts grow like a ratchet.** Wharf, extend, fill between the wharves, put streets on the fill, all inside a harbour line. Salem's Derby Wharf grew in stages from 1762 to about half a mile by 1806, and over 50 wharves once lined the harbour.

**Conservation follows economics.** Stavanger's 1956 plan protected the least wanted part of the old town, the run-down cottages, not its finest houses, after city architect Einar Hedén argued against clearance. Portsmouth's Strawbery Banke was formed in 1958 in reaction to the demolition of Puddle Dock. What survives is what was cheap to keep.

**Generate, then test and reject.** Dwarf Fortress rejects worlds that fail its checks and generates again. Our checks: every building reachable, every plot has frontage, no plan left orphaned, the mix of eras within set ranges, and the spread across seeds reported.

**Quantise decisions; write words last.** Geometry decisions use integers (centimetres, fixed angle steps), so floating-point differences can never change a fact (Gaffer on Games). Names and descriptions come from a grammar afterwards, as in Caves of Qud. Unlike Qud, causes are never invented after the fact.

## The pipeline

| Stage | Output | Owner |
| --- | --- | --- |
| 0. Site | Terrain, coastline, harbour line, cost fields | Engine (fabric pass) |
| 1. Era script | Dated eras, booms and busts, fires, plans, each with a cause | Engine |
| 2. Street growth, yearly | Street graph with a build and widening date per segment | Engine |
| 3. Plots | Dated plot graph: splits and merges | Engine |
| 4. Building diaries | Dated events per building, each with a cause | Engine |
| 5. Hand-off | Diaries at the people simulation's start year; people append | Engine |
| 6. Validation | Accept or reject; a hashed snapshot per decade | Engine tests |
| 7. Resolve | Parts list per building for year Y | Game |
| 8. Build | Meshes in Blender and Unity | Game |

Stages 0 to 6 decide facts, so they belong to the engine: a coarse "fabric pass" that runs before and alongside the people simulation and never contradicts it. They go in `docs/engine-requests.md`. The game owns resolving and drawing.

## Pitfalls

- Raster growth models (SLEUTH, TownSim) give plausible masses with no street logic.
- Pure emergence fights authorial control: TownSim's curves were "largely uncontrollable".
- One rule everywhere gives one texture everywhere.
- Slow passes: Lechner's agent model took hours. Budget for the plot graph, not pixels.

## Sources

[Emilien et al. 2012, villages](https://perso.liris.cnrs.fr/egalin/Articles/2012-villages.pdf) · [Beneš et al. 2014, road networks](https://cgg.mff.cuni.cz/~jaroslav/papers/2014-cities/2014-cities-paper.pdf) · [Galin et al. 2010, roads](https://perso.liris.cnrs.fr/egalin/Articles/2010-roads.pdf) · [Parish & Müller 2001](https://history.siggraph.org/?p=116923) · [Chen et al. 2008](https://www2.cs.uh.edu/~chengu/Publications/streetModeling/street_modeling.html) · [Nishida et al. 2016](https://diglib.eg.org/items/7a226fc0-3502-41ff-a14c-69b95d6e1dd0/full) · [Song & Whitehead 2019, TownSim](https://www.pcgworkshop.com/archive/song2019agentbased.pdf) · [Weber et al. 2009](https://diglib.eg.org/handle/10.2312/CGF.v28i2pp481-492) · [Lechner et al.](https://ccl.northwestern.edu/papers/2006/TR-2007-33.pdf) · [Lipp et al. 2011](https://www.cg.tuwien.ac.at/research/publications/2011/lipp2011a/) · [SLEUTH](https://people.geog.ucsb.edu/~kclarke/ucime/banff2000/533-jc-paper.htm) · [Whitehand, Conzenian tradition](https://journal.urbanform.org/index.php/jum/article/view/3896) · [Norske storbranner](https://snl.no/norske_storbranner) · [Stavanger wooden town](https://www.stavanger.kommune.no/siteassets/bolig-og-bygg/byantikvaren/trehusbykampanje-2021/trehusbyen-brosjyre-2021.pdf) · [Gamle Stavanger](https://en.wikipedia.org/wiki/Gamle_Stavanger) · [Salem wharves](https://www.nps.gov/sama/learn/historyculture/wharves.htm) · [Boston shoreline](https://www.wbur.org/news/2021/06/14/8-maps-that-explain-bostons-changing-shoreline) · [Puddle Dock](https://portsmouthexhibits.org/collections/show/23) · [Dwarf Fortress world gen](https://dwarffortresswiki.org/index.php/DF2014:World_gen) · [Caves of Qud](https://pcgworkshop.com/archive/grinblat2017subverting.pdf) · [Fowler, event sourcing](https://martinfowler.com/eaaDev/EventSourcing.html) · [Gaffer, floating-point determinism](https://gafferongames.com/post/floating_point_determinism/)
