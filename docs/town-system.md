# The town system

How every town and city in the game is laid out, how it changes, and how it plugs into what exists: the town-scale part of the living fabric (`docs/living-fabric.md`, Big change). It merges `docs/research/urban-design.md`, `city-forces.md`, `city-types.md` and `town-change.md`. Drafted by the design lead on Opus (Fable was out); Øystein's three decisions in section 9 are open. Research marks carry over; numbers are starting values.

## The idea in one paragraph

A town is a sequence of founding acts laid on land that already had lines on it. Each act lays one plan unit: an area of one type (a fire grid, a row of sea houses, a slope of owner-built lanes, an estate), laid by one founder in one year, with its own plot module and the building rules of its year. Plots then run their cycle on lines that hardly move: built, filled in behind, emptied, cleared, rebuilt, merged in booms, divided in hard times. Growth comes in pulses, and at each halt a belt of big plots and institutions forms against whatever stopped it. Plans are dated documents whose claims reach the ground only as their mechanism allows, so most leave scars. Under the street lies a dated stack of mains, cellars, tunnels and shelters. All of it is the living fabric's record at a larger scope, read at a year. Irregularity comes only from seams, land and history, never from noise.

## 1. The model

| Piece | What it is | Record |
| --- | --- | --- |
| Land and old lines | terrain, water, streams, field walls, farm lanes, a fishing village: what stood before each act | thing |
| Plan unit | one area of one type, laid by one act in one year | thing |
| Way | a street segment between junctions, with dates, width, rank and role; its surfaces, flights, kerbs and lamps are things of their own | thing |
| Plot | a frontage on a way, with a depth, cut from its unit's module | thing |
| Building | the diary (`docs/building-system.md`) | thing |
| Underground layer | a main, cable, sewer, tunnel, shelter or car park: route, depth band, owner | thing |
| Plan, regime | a dated document with claims and a mechanism; a dated building rule and its area | document |
| Halt | the years the edge stood still, and the fixation line | timeline event |
| Fringe belt, district, quarter state | the plots taken during a halt; units grouped by theme; a quarter filtering down or coming back | computed |
| Fields | access, price, nuisance, amenity, syntax, beside the living fabric's feet, water, sky, wind, care, vacancy | computed, cached by decade |

A unit is one dated instance of a type from the pack's catalogue. The type says "a fire grid of 60 by 100 m blocks"; the unit says "the Grid west of the head, laid by the town after the fires, bent where it meets the older lanes".

### On the living fabric's record

| | `made` | `keepers` | `uses` | `works` | `events` |
| --- | --- | --- | --- | --- | --- |
| Plan unit | year, founder, cause, type, module, regime, land taken, old lines kept, how much the founder held (streets, plots, buildings) | whoever holds its rules: the founder while it does (an estate, a company, a cooperative), then the town, or a conservator from the year of protection | computed from its plots | unit-wide: a paving campaign, a cooperative repainting together, protection, a street cut through | fire, flood, war, clearance |
| Way | year, by whom, width, rank, role (matrix, building, connecting, restructuring) | a road department, the harbour, owners | traffic; feet | widened, paved, relaid, pedestrianised, closed; utility cuts | |
| Plot | laid with its unit: frontage, fraction of the module, depth | owners: kind, horizon, resident or not, from, to, how acquired | occupation, use, occupants' income band | merged or split with year and cause, the old line kept as a trace | fire |
| Underground layer | year, owner, route, offset from the kerb, depth band | the utility | | renewed, abandoned, filled | burst |

Buildings keep their diaries. Plans and regimes have no life of their own; their effects land on the things above.

### On screen

| Kind | In the town system |
| --- | --- |
| Canonical fact | a unit's founding; plot lines, merges, splits; a way laid or widened; a plan adopted, each claim carried out or lapsed; a layer laid; a regime in force |
| Visual interpretation | back-fill and gaps from a plot's cycle; a belt's trees; a quarter's state through care and division; a stepped front; a trench strip aged from its year |
| Non-semantic texture | how far a house turns in its plot, within its type's spread (an owner-built slope varies, a fire grid does not): the type sets how much, the seed which |
| Perceived information | the plan's map, a notice of purchase, the paper on the road scheme, a developer's board, a street name that remembers a use |
| Local scene state | tonight's barriers round a dug street, cars on a fallow lot |

## 2. The forces as rules

The research names five forces: access, clustering and repulsion, durable capital, keepers, and cycles with succession. The engine decides who, why, how much money, which plan and who owns. Overstory derives the form by written, seeded rules.

| Force | The engine decides | Overstory derives (starting values, unverified) |
| --- | --- | --- |
| Access | transport works; each era's modes (request 26) | the access field; the town reaches as far as an era's speed goes in half an hour, about 2.5 km on foot |
| Clustering | where works and ventures locate (21) | nuisance by the wind rose (smoke, smell, noise); amenity (view, sun, height, water) |
| Land and money | owners, sales, prices, rents (24) | the price field: bid rent from access and amenity, less nuisance |
| Durable capital | demolition and rebuilding (14) | a building takes the next use its form allows; it is rebuilt only when the rent gap beats the cost |
| Keepers | care from means, tenure, horizon, neighbours (13, 24) | care curves by owner kind; a horizon under ten years cuts care sharply; care clusters |
| Cycles | booms, busts, halts, fires (3, 26) | waves of 15 to 20 years: booms merge core plots and grow the edge with housing, halts give it to institutions |
| Sorting | households choosing homes (15, 24) | filtering about 2.5% a year in let buildings, 0.5% in owned (Rosenthal; American rates); never by ethnicity (Rule 8) |
| Institutions | plans, rules, budgets, lenders (23) | each plan's scar by its mechanism; care by department |

Where the better-off live is a pack dial, set by what the centre offers that the edge lacks. Here: the Heights from 1880, upwind with the view, and the old town again once restored.

**Provenance.**
- `authored`: the pack's script and land, the heart's hand-drawn lines, fixtures.
- `generated-past`: what the fabric pass writes from the script: units with their ways, plots and first buildings; fires; plans adopted and lapsed; regimes; halts; utilities. Our stand-in runs the pass today; the label stays when the engine runs it.
- `derived`: what our rules decide in place of a person or actor, in any year, until the engine does: owners, tenure and care; merges and splits for money; back-fill; which plot a claim reached and when; clearance by the rent gap; the plot an institution or venture took; occupants' income; campaigns by rule. Each becomes `generated-past` or `simulated` once the engine decides it, and never carries a year a player can read unless a story pins it.
- Never stored: fields, syntax, coverage, cycle phases, belts, quarter states.

**Space syntax** is a field like the others: angular integration and choice per segment (NAIN at 800 m; NACH at 800 m, 2,000 m and the whole town), recomputed per decade and at each network change, with stairs, passages, bridges and ferries as links. It adds a climbing cost, so Herring Hill's stepped lanes do not read as well connected as the quay road; that departs from the method and is tested first against Stavanger's shops on OpenStreetMap. It ranks vacant space for ventures, seeds the feet field until request 16, and places shops in the generated past: a prior and a check, never a fact.

## 3. Growing the past, then playing forward

The grown past is the starting record only: it explains how the 1989 town looks, and it is generated once by rule and never rendered (Øystein, 22 October: show from 1989, remember from 1870).

1. **The frame:** the land and its old lines before the oldest act.
2. **The first routes:** the sea and the quay as the matrix; ridge and coast paths; the country road at a horse's grade.
3. **The script,** read from the pack's timeline. Empty years are skipped; plots step yearly from the first town-sized act (1800 here).
4. **Each year:**
   - *Founding.* A script act lays its unit; demand the existing units cannot hold founds one of a type the era allows, on land within reach that its founder holds, cheapest by the price field. The unit reads the old lines on its land, keeps those its founder had no reason to break, takes its module and regime, and is laid out by its type. Seams are computed with its neighbours, each with a kind and a cause.
   - *Halts:* the edge stops at the fixation line of the moment, and institutions founded meanwhile take big plots against it.
   - *Plots* step their cycle: infill as demand and the type's clock allow, then recession, clearance, a fallow lot, rebuilding when the rent gap beats the cost. Booms merge core plots; hard times divide houses.
   - *Plans* reach plots by their mechanism; owners under a claim get a short horizon (blight).
   - *Buildings* take the regime in force at their plot; diaries grow by the existing vocabulary.
   - *Networks:* utilities are laid along the streets of their year, paying streets first; syntax is recomputed.
5. **Checks** (section 5). A failed town is grown again from the next seed and the spread reported. Hand-laid units never change.
6. **Hand-off** at the people's start year (1959 for a game in 1989, #23): from then the engine decides people, owners, care and works.
7. **Hashes** per decade, run twice, the second in shuffled order.

About 20,000 plots over two centuries must run in minutes in pure Python. Geometry is in integers (millimetres, fixed angle steps), seeds from stable ids by SplitMix64, to the engine's portability rules (request 27).

**How a type lays its unit.** *Accreted:* least-cost paths over slope and water between what draws them (the quay, a spring, the church, the road); contour lanes and stepped gullies on a slope; plots claimed house by house. *Grid:* a surveyed frame oriented by the founder's rule (to the shore, the old road, the north), laid over the slope unless the type says otherwise; a street too steep becomes stairs, as at Priene; it bends or stops at a kept line. *Loops and cul-de-sacs:* roads branching from the arterial, curving on the contours. *Estate:* slabs at one angle in open ground, roads at the edge. Plots are cut along each frontage in the module and its simple fractions. Later splits halve or quarter a plot, and a merge keeps the old line as a trace: a party wall, a break in the roof, a change of window rhythm.

**Playing forward.** The engine decides a unit founded, a plan adopted, a sale, a venture's site; the library lays the form (`derived` until the engine runs it). Large works have phases (hoarding, pit, frame, scaffold), so a site stands for years. Only the chunk a change touches is rebuilt offline. In a session most change is small: a shop opens, a hoarding goes up, a plan is fought. The slow forces show across scenarios set years apart (`docs/town-plan.md`, What the player sees), and in the past the town carries on day one.

## 4. Setting packs

A pack holds:
- **Land and region:** terrain, water, old lines, settlements ranked by what each offers.
- **A timeline:** eras with modes, door-to-door speeds, building shelves and sector totals; dated events with causes (founding acts, fires, booms, busts, halts, plans, regimes), the same list the economy reads (request 3).
- **A plan-type catalogue:** per type the fields of `docs/research/city-types.md` (network, blocks, plots, buildings, density, open space, slope, water, edges, rules, change, read, measured from), plus how much its founder holds and which old lines it keeps.
- **Regimes** in one vocabulary (height to street width, storeys, coverage, smallest court, fire distance and material, building line, sky-exposure plane, floor-area ratio, parking, fit to the neighbours), each with exemptions and its area; and which mechanisms its plans use.
- **Owners and keepers** with horizons and care curves, departments with budgets by decade; **constructions by era**; **the underground** (services' years, depth bands below the frost line, shelters); **dials** (where the better-off live, climate, names); **measured exemplars** per type.

A pack never changes a rule; if it needs to, the rule was wrong.

### Worked example: the harbour town

Ground cover (GSI) for four types is measured (`docs/research/stavanger-centre.md`); mean storeys (L) are estimated from the plan's storeys.

| Type | Founder and control | Module | Network | GSI, L | Changes by |
| --- | --- | --- | --- | --- | --- |
| Market head | the church; many owners after | irregular | an irregular square open to the water | to measure, 2 to 3 | institutions gather |
| Wharf row | merchants, plot by plot | 8 to 12 × 18 to 26 m, gable to the quay | the quay is the street | 0.40, 3 to 4 | low road: stores, pubs, offices |
| Slope lanes | owners, house by house | none: houses 9.8 × 7.5 m | contour lanes, stepped gullies | 0.26, about 1.7 | house by house; protected from 1956 |
| Fire grid (the Holm, the Grid) | the town by regulation | to measure (Kristiansand: blocks about 60 × 120 m) | straight streets, a 30 m fire-break | 0.26, about 2.5 | fronts reclad, shops change |
| Workers' rows | the cannery and builders | small, repeated | rows along the slope | 0.34, about 2 | let go together when the company sells |
| Villa park | a landowner selling to merchants | large | winding roads on the crest | low | offices, consulates |
| Garden suburb | the town's land bank, then cooperatives | 10 to 20 m (unverified) | curves over farmland | low | house diaries; trees |
| Renewal centre | the town, by purchase | merged plots | restructuring streets | coarse | half empty after 1986 |
| Satellite estate, oil campus | Husbanken and a cooperative; developers | the estate or the fenced site | roads at the edge | open green; parking | reclad; boom and bust |

The script (setting content, not a claim about Stavanger):

| Year | Act | Leaves |
| --- | --- | --- |
| about 1125 | market head and cathedral, where the country road meets the harbour | the square |
| 1700s to 1860 | wharf rows; slope lanes on Herring Hill in the herring boom | gables to the quay; the old town |
| 1860 to 1900s | the Holm burns and is rebuilt to a regulation; the Grid after the fires | fire grids, the fire-break |
| 1870s to 1895 | the herring fails; a cannery at the mouth; the railway (1878), then a halt | the first belt: hospital, cemetery, upper school |
| 1880 to 1920s | villas on the Heights; workers' rows for the cannery | the Heights, Tin Town, Ropewalk |
| 1904 | masonry in the centre, after Ålesund | brick inside the zone, timber just outside |
| 1920s to 1950s | garden suburb on bought farmland; a halt in the 1930s | farm lanes as bends; the Mudbowl, the Plots |
| 1946 | the centre plan: four clearance areas and a harbour ring road, by purchase | New Town in two (1948 to 1962); the rest a scar |
| 1956 | the old town protected, after a fight | care rises; stone kept |
| 1960s to 1980s | satellite estate, the Bluff tunnel, oil, the High Bridge (1978) | |
| 1974, 1984 | the centre held to its streets and heights; the ring dropped | sea houses on the ring's line |
| 1986 | the crash, a halt | half-let offices, fallow lots |

The corner sits in it: E (1826) and D (1828) are among the slope lanes' first houses, C (1879) late infill, A (1912) a rebuilding on a wharf-row plot. The masonry zone's edge runs at the Basin's head, so Harbour Row's east shore and Herring Hill stay timber, as Stavanger's wooden houses after 1904 suggest (unverified as a zone), and the edge reads as a seam.

**A flow at town scale: the road never built.** In 1946 the centre plan draws a harbour ring along Barrel Quay through the Holm's sea houses, by purchase. The town buys two other areas first and runs out of money. The sea-house owners can neither sell at value nor plan past the road, so their horizon is short from 1948 (blight, `derived` until request 24). Care falls and the lofts empty. The ring is dropped in 1984; by then the warehouses are the cheapest big rooms by the water, and bars and a club have taken them (the vacancy field; Jacobs). In 1989 Holm Street is grey, its doors cheap, and a band plays its first gigs in a back room. On screen: sea houses on the line of a road never built, worn as the plan wore them and lit at night by what moved in. Every link is a fact, a field or a rule.

### A contrasting pack: New York

It tests what the harbour town lacks (numbers from `docs/research/city-types.md`). A plan carried out over a century: the 1811 grid (blocks 61 m deep, streets 18 m, avenues 30 m), opened as the city reached it. Height as the main dimension, set by the regimes of 1916 (setbacks) and 1961 (floor-area ratio). Merging as the usual verb: a lot becomes an Old Law tenement (1879), lots merge for a New Law tenement (1901), tenements for a tower. Transit as a plan element and a layer; owners keeping their own sidewalks. The proof is one block laid by the same library from 1811 to 1989, with no rule changed.

## 5. What makes it read as real

1. **Irregularity has a reason:** the land, an old line kept (a farm lane's bend, a quay's line), a seam, a scar. Inside a unit there is only the type's own spread.
2. **Seams carry the history:** a street kinks or narrows entering an older unit; plot grain doubles or halves; blocks meet at an angle and leave a wedge; a grid stops in a T against an old lane; one unit's back lane is the next one's front street; the building line and eaves step. The land makes seams where a type gives way to stairs or a quay.
3. **Repetition at the right scale:** an identical row is true when one founder built it; keepers bring variety later.
4. **A few strong streets over a quiet background,** and eras side by side, still used, with few anomalies, each with a cause.

**The history budget at town scale:**

| View | What tells | Budget |
| --- | --- | --- |
| Far, the map | each unit's type: network, grain, roof family; belts as rings of trees | one per unit |
| City camera | the unit's founding and its seams; one anomaly by weight (the plan's lone block, a fallow lot, a merged block) | one history per unit, plus at most one anomaly |
| 12 m | plot phases (back-fill, gaps, a gateway), breaks where plots merged, stepped fronts, a widened end, unit-wide coats | two per block face |
| Street stop | a kerb that remembers houses, one house set back, covers by era, trench strips, a stair head paved over | three per stretch |
| Eye level | the dates themselves: a portal's date stone, a cover's foundry, a street sign, a notice | all, clustered |

A change big enough to read from the city camera is a new unit with seams of its own. Marks from one cause are one shape: a cooperative repaints its blocks in one year, a claim leaves one stepped line.

**Checks a machine can run:**

| Check | Measure | Against |
| --- | --- | --- |
| Orientation order | φ = 1 − ((H − H_g) / (H_max − H_g))², H the entropy of street bearings in 36 bins, H_g a perfect grid's (Boeing 2019) | the type's exemplars; the town within the European band |
| Junctions | share of four-way junctions and dead ends; mean circuity | the type's exemplars |
| Spacematrix | GSI, FSI, L = FSI ÷ GSI, OSR = (1 − GSI) ÷ FSI, per unit | measured exemplars |
| Plot module | share of frontages within 10% of the module, its halves, quarters and doubles | strong for a grid, weak by design on an owner-built slope |
| Seams | each with a kind and a cause; seams per km of unit boundary | the heart's hand layout; a historical map |
| Belts, scars | a belt for every halt; a trace for every unfinished claim and closed layer | the script, the plans |
| Syntax | frontage grade and shops against NACH | Porta et al. 2009; Stavanger's shops |
| Scaling | shops, pubs, venues and road length against N^1.15 and N^0.85 | Bettencourt et al. 2007 |
| Reach, ages, budget | every plot a frontage and every door a way; building decades per street; marks per unit per view | `reach_check.py`; the type; the budget |

Exemplars are measured from OpenStreetMap with OSMnx, as `docs/research/stavanger-centre.md` did: Gamle Stavanger, Holmen and Skagen, Storhaug, Kristiansand's Kvadraturen, Trondheim's Midtbyen, Ålesund, Lambertseter, and Manhattan. A grown unit outside its type's range is rejected. Then people: a cold reader names Lynch's five elements from the city camera, names three types side by side, fails to pick the hand-laid unit from a grown one, and says which side of a seam is older.

## 6. Fitting what exists

**The heart's clay (`blender/blockouts/heart_layout.py`)** is one moment today: lanes, rows and blocks with no dates, plots or units. It changes in two steps.
- *Now, data only, geometry unchanged and a hash to prove it:* a table of the heart's units (type, founding, founder, module, regime); every lane, building, yard and detail tagged with its unit (`row()` on the terraces makes slope lanes, `grid_block()` the Grid, the Holm's sea houses its 1860s rebuild); seams listed with kind and cause; a founding year per building, so the clay can be shown by decade; lamps reading their unit's lighting works, not lane names.
- *At the plan's step 6, after the corner is judged:* the heart regrown as dated units. Hand-drawn lines and landmarks stay authored. The Grid takes its type's measured numbers (its blocks are 56 × 40 m today, smaller than any exemplar), the Holm its 1860s grid, New Town the renewal unit with its stepped line and lone block, and the sea houses stand on the ring road's line. The corner's lanes, five houses and gully are frozen as judged. `heart_layout.py` shrinks to authored input and a call to the library.

**The gully and the stairs.** The gully keeps its hand facts: a way of the slope-lanes unit, its flight made by the town in 1874. `stair_facts.facts_for` stops choosing years by lane name and reads the unit: the year from its founding or the town's paving campaign there, the builder from its founder (owners on passages, the town on a fire grid's stair-lanes; the society's Bluff walk stays an authored work), the stone from the founder's means and era. One error goes: the Holm's stair-lanes date from its 1860s rebuilding, not 1905 to 1925. The "too steep for steps" flag becomes a check on the unit: a contour-following type must not draw a way steeper than a stair, and a grid that ignores the slope turns such streets into stairs. The stride and ramp thresholds in `stone.py` stay as the way's choice of construction.

**Upkeep.** A thing's keeper is its plot's owner or its way's department. The town's care becomes one curve per department in the pack's timeline, shared by every public thing, replacing the drops `stair_facts` draws per flight, and scaled by the unit's standing: raised after protection, cut under a claim.

**The corner.** A and B stand on wharf-row plots, C, D and E on slope-lane plots; their diaries are unchanged. The corner through the years (plan step 4) reads its street works from its ways. Nothing here touches its geometry before it is judged.

**The rest.** The living fabric's fields gain access, price, nuisance, amenity and syntax. `blender/tools/grow_town.py` and `fixtures/lt1-town.json` stay a sketch, replaced by the pass. The library lives in `blender/town/`, pure Python like the resolver; grown facts in `fixtures/town/` with a hash per decade.

## 7. Engine requests

These are now requests 22 to 27 in `docs/engine-requests.md` (gathered 22 October), which is the source; this list is kept for its context.

22. **The town as founding acts** (extends 6). The fabric pass lays the town as plan units: each one area of one type from the pack's catalogue, with its year, founder (the town, a landowner, a company, a cooperative, a developer), cause and land. In play the council and developers found units as decisions with reasons, and Overstory's library lays out their streets and plots. The player would see a district's date and maker at a glance, and the seam where it meets the older town.
23. **Plans and rules as documents** (extends 14). Plans are sentences today ("to widen the harbour road"). We need documents: a kind, claims on geometry, a mechanism (on rebuild, purchase within a window, at once, by one actor) and a state (adopted, lapsed, replaced), with each claim's fate decided where it meets a plot (an owner who will not sell, money run out, a protest that wins). Building rules and protected areas the same way. An adopted claim shortens the horizon of the owners under it. The player would see sea houses on the line of a road never built, worn as the plan wore them, and could find out who stopped it.
24. **Owners with horizons, and prices** (beside 10, 13 and 15). Owners of each plot and building over time, with a kind (resident owner, landlord, heirs, the town, a cooperative, a company) and a horizon (a lease's end, an heir waiting to sell, a road reserve); sales and inheritance with reasons; prices and rents by year. Households choose among real addresses by price, access, neighbours and life stage; lenders' rules (Husbanken's norms) are facts of a bank; never by ethnicity (Rule 8). The player would see why one street is kept and the next let go.
25. **Neighbourhoods on the map, places by rank.** The engine's neighbourhoods (about 80 people each) need addresses: sets of plots, added as units are laid. Places should come by threshold, not one of each per neighbourhood: a town of 95,000 has about 1,200 such neighbourhoods but one cathedral, and a pub on most corners (Christaller). The player would see the street's pub round its corner, and one cathedral for the town.
26. **Transport and halts in the timeline** (extends 3). Each era's modes with door-to-door speeds and lines; each halt in growth with its years and cause. The player would see rings of hospitals, cemeteries and trees where the town once stopped, and a tram street that kept its width.
27. **The town library adopted** (extends 19). The layout rules (types, seams, plot cycles, plan mechanisms) and fields (access, price, syntax) written as a portable, deterministic library to the engine's portability rules, so the fabric pass can run it and the engine can read distances and vacancy without depending on the game. The player would see ventures, trips and feet land where the streets say.

## 8. The build order

Each step ends in something judged in Unity, then a strict review. The corner's geometry is never touched, and the heart's changes only at the plan's step 6.

| Step | What | Judged | Model, when |
| --- | --- | --- | --- |
| T0 | Records, validator, the harbour pack as data, the heart's units tagged, `stair_facts` reading the unit | the clay from the city camera by unit and founding decade; its hash unchanged | Opus, Sonnet; now |
| T1 | The measures on the heart and the exemplars | the heart's units against five real places | Sonnet; now |
| T2 | Slope lanes, fire grid and estate side by side in clay | far stop, blind: can a viewer name them? | Opus, Fable; beside step 2 |
| T3 | The old town regrown beside the hand-laid one | blind: which is hand-laid? | Opus, Fable; beside step 2 |
| T4 | Underground traces on one street: covers by era, trench strips | the street stop, with the landing's setts and kerb | Opus; with the setts |
| T5 | One block's plot cycle, 1850 to 1989 | 12 m years sheet: which plots merged, and when? | Opus; with step 4 |
| T6 | Seams: the Grid against the lanes, the Holm against the wharf row | city camera, 12 m: which side is older? | Opus, Fable; step 6 |
| T7 | The 1946 plan carried out in part, with the sea houses' blight | years sheet: where did it stop, and why are they shabby? | Opus, Fable; step 6 |
| T8 | The centre grown from the script, hand units kept | far-stop years sheet; checks pass; frame time | Opus, Sonnet; step 6 |
| T9 | One New York block, 1811 to 1989 | city camera, street stop; no rule changed | Opus, Fable; step 10 |
| T10 | A 1990 decision from a fixture, its chunk rebuilt live | the street before and after | Opus; after #22 |

## 9. Decisions

Merged across the four pages, these are fifteen decisions for the design lead, recorded as decided, and three for Øystein (the second decided by him).

### Decided

1. **Plan units are the top layer of the town's data;** every way, plot, building and yard belongs to one. All four pages converge on them, and they fit the living fabric's record without a new system.
2. **The heart's clay is tagged now, geometry unchanged, and regrown as units at step 6** with the corner kept. This fixes dates the corner leans on without slowing it.
3. **Syntax is Overstory's field, with a climbing cost,** reaching the engine only inside the library (27). It is computed from geometry like every field, and the engine never depends on the game.
4. **Plans and regimes come from the pack's script before the people start, from the engine after.** This follows the standing rule and the start year (#23).
5. **The underground is stored whole as data, traces shown first;** a place below (the shelter in Watch Knoll first) waits for a scenario that needs it. Traces are cheap and ride on the paving work.
6. **Belts, districts, quarter states and cycle phases are computed, never stored.** Nothing can drift from its plots.
7. **`generated-past` marks form from the script; `derived` marks a person's decision made by our rule.** That is one clear line for tools and the history budget.
8. **The hand-laid heart keeps its lines authored and lays plots and buildings by rule,** under the same checks, proved by the regrow test. Control stays where legibility is made.
9. **Growth is a coarse yearly step over plots,** not cellular automata or free agents. That structure matches the engine and gives streets, plots and causes.
10. **American rates stay starting values, marked unverified,** until Nordic numbers are found. Nothing better exists.
11. **The machine checks gate every grown unit.** They catch a town of one moment before a reader does.
12. **The foreign check is one New York block;** which metropolis the game builds stays Øystein's. Its research is done, and it tests height, merging and a century-long plan.
13. **The masonry zone's edge runs at the Basin's head.** The corner stays as designed, and the edge becomes a seam.
14. **Where the better-off live is a pack dial,** here the Heights, then the restored old town. This matches the town plan and the rule on amenity.
15. **The library follows the engine's portability rules,** so request 27 is a port, not a rewrite.

### For Øystein

1. **Where the town system enters the plan, and what he sees (scope).** Recommended: data and measures now beside the corner (T0, T1, no visuals); the clay tests beside the corner's buildings (T2, T3); the heart's geometry at step 6. It would run as the trees did, strict reviews as the gate, with Øystein seeing three milestones: the three types, the regrow, the plan stopped part way. It fixes facts the corner leans on without slowing it.
2. **How years pass in play: decided (Øystein, 22 October), per game.** It depends on the game: one game spans a week, another a year, another generations. Overstory is a world for many games, so the town system and the building blocks support every span. That sets these requirements:
   - The screen follows the record. With the same record and the same date, the town is drawn the same whether it was watched day by day or reached by a jump. Wear, growth and repairs are worked out from the record, never piled up frame by frame in the renderer, so a jump is cheap and a saved game reloads exactly.
   - Play changes the record. The player's acts and the outcomes of scenes are events like any other, so two playthroughs reach different towns, and the 3D world shows what the player did as it shows anyone's acts (Øystein: "they should definitely be reflected in the 3d environment").
   - Living through years may make a different history from jumping over them: events only scenes create, more detail where the player has been. Whether it does is the engine's to decide. Overstory draws whatever the record holds.
   - Every system answers at every resolution. Hours and days come from weather, light, scene state and a poster put up. Months and seasons come from growth, leaves, upkeep and a shop opening. Decades and generations come from plans, works, demolition and rebuilding.
   - What a span cannot show is still true. A week-long game shows wear it will never see grow, and a generations game passes over the week's posters.
   - How a jump is shown on screen is chosen by the game from what `docs/research/time-on-screen.md` finds.
3. **The eras after 1989 (scope).** Recommended: research only what the first scenario's years need (the corner's 2020 frame needs a handful of items), and let the library run to any year with the eras it has. That content is large and has no player yet.
