# The living fabric

Agreed 22 October (Øystein delegated the decisions: "you know what to do here"). How the town's whole physical fabric (stone, streets, houses, shopfronts, interiors, yards, trees, quays, the land at the edge) changes because of the lives lived in it, and how those changes flow into each other. It takes the upkeep system (`docs/upkeep.md`, `blender/generators/upkeep.py`, the gully steps' life in `stone_gully.json`) all the way. Claims from outside sources that we could not check are marked (unverified).

## In short

- **LF1** One record (`made`, `keepers`, `uses`, `works`, `events`) and one yearly runner, `life(thing, tables)`, for everything made or planted; flow through shared fields, not links; lives computed in the player on change, D12.1 (disputed). Evidence: `research/world-that-remembers.md`. Reopens: none named.
- **LF2** A fact decides that and why, a rule how it looks, the seed which exactly; a derived patch carries `derived` and no year a player can read unless pinned as a fact. Evidence: `facts-contract.md`. Reopens: request 19 adopted.
- **LF3** Construction (`made.how`) is a fact only a renewal changes; quarters, the underground, demolition and slow works are the same record at larger scope; nothing may assume a frozen plan. Evidence: `research/town-change.md`. Reopens: none named.
- **LF4** History budget per thing: one at the city camera, two at 12 m, three at the street stop, all at eye level, clustered; one cause makes one shape; counted as well as reviewed. Evidence: `experiments.md`, LT1f. Reopens: provisional until the corner's years sheet.
- **LF5** Care: the engine's money, presence, age and events through the pack's curve (request 13), never character (disputed); feelings reach things only by recorded acts (20), care over years or a fallible record. Evidence: `facts-contract.md`. Reopens: none named.

## The idea in one paragraph

Every made or planted thing has a record of the same shape: when it was made and by whom, who kept it and how much they cared, what it was used for and how much, the works done on it, and the events that hit it. The engine decides the people's side of that record (who, why, how much money, which decision). Overstory derives the physical side by rules that are deterministic, written down and seeded (how deep the wear, how big the lichen, where the patches fell). Things do not talk to each other; they read and write a few shared fields over the town (feet, water, shade, wind and salt, care, vacancy), and a change flows by rebuilding what reads a field that changed. Most change is slow drift (wear, growth, fading); works reset some layers and leave the rest; so the town in 1989 contains the town of 1988. On screen each thing tells few histories per view, clustered where their causes cluster, so the read is history and not speckle.

This is mostly maintenance, not building. Real towns are made of upkeep: what gets patched, what gets a campaign, what is let go (Brand's "shearing layers"; Jackson and Mattern on repair as the normal state of things). The research already says so for steps (`docs/research/repairs.md`); the proposal is to make it the rule for everything.

## 1. The model

### The things and their record (LF1)

A thing is anything with a life: a flight of steps, a wall, a stretch of paving, a house, its shopfront, a sign, a room, a yard, a lawn, a tree, a quay, a boat, a field. Its record:

| Field | What it holds | Who decides |
| --- | --- | --- |
| `made` | year, by whom (the town, an owner, a builder), of what (the pack's shelf for that year), how (the era's practice), cause | engine (fabric pass); authored until then |
| `keepers[]` | who kept it from which year, and their care (per mille), decade by decade | engine: from money, presence, age and character of the owner, or the town's budget by department |
| `uses[]` | footfall a year, traffic, loads, occupation (lived in, let, empty), the business in it, grazing or mowing, each from a year, with its cause | engine: trips, homes, businesses, habits |
| `works[]` | dated works above patchwork: campaign, renewal, alteration, cleaning, pruning, with scope, material, who, cause | engine: a keeper's decision with reasons; the council's plans |
| `events[]` | one-off causes: a storm, a fire, a flood, a fall, a lorry at the gate, a pipe burst, a tree down | engine |
| `place` | computed, never authored: the fields sampled at the thing | Overstory |
| `life` | derived per part at the year: years since each layer was reset, wear, damage and its fills, origin of each part (original, depot, new) | Overstory, from the above |

The gully steps already carry `made`, `keepers` (as `upkeep`), `works` and `life`. The change is to give every thing the same shape and one runner.

### Construction is a fact (LF3)

A thing's `made.how` names its construction from the pack's catalogue, and the construction is a fact like the year. The gully has two already: one thick split slab a step, each resting on the one below (`block`), and thin treads on block risers (`tread_on_riser`). A catalogue entry holds everything that follows from how a thing was built: its parts and their sizes; its laying rules (bridged joints, a batter, bedding, overlap); what breaks in it and how (a thin tread cracks across; a block settles and tilts; a cast step spalls at the nosing and shows its aggregate; an Eternit sheet chalks and chips at its fixings); what its keepers do about it by era; its rates; and what it reads as at each tier.

Four facts and a seed choose it, by the same two-step choice the house parts use (filter by year, then pick with a seed from the installing event):

- **The era and its technology:** the catalogue's year ranges: cement from about 1890; concrete steps and casts 1940 to 1965, precast units after (unverified); asphalt from the 1920s; Eternit 1950 to 1978; concrete tile from 1950.
- **The builder's craft and means:** who built it and with what money (`made.by`, wealth per mille). The town's mason lays block steps with every joint bridged; an owner with little lays thin treads on rough risers, or whatever the yard had; a society building a lookout's steps sets slabs into the ground (Ålesund's Aksla). Craft shows as regularity, bridged joints and a true line; means as thickness, dressing and the stone's grade.
- **The material at hand:** the pack's stones and what the site gives: the lane's own rock split where it was cut, depot stone, granite brought in for money.
- **The town's tradition:** the pack's local practice: split slabs and dry-stone here; dressed granite blocks in Bergen; brownstone stoops in New York.

**Moving through constructions.** A work of kind `renewed` names a new construction and material from its own year: the split-slab flight recast in concrete in 1958, the timber stair replaced in steel in 1972, the slate roof re-covered in Eternit in 1961, then concrete tile in 1985, then slate again when it is restored. Rules:

1. The new construction starts its own life from its year, with its own damage, fixes and rates.
2. The old one leaves what it leaves. The recast flight keeps the old flight's line, width, landings and cheek walls, and often its lowest steps: a renewal has a scope, so a flight is slab below and concrete above from the landing where the crew started. The re-covered roof keeps its pitch, chimneys and eaves. The steel stair keeps the old opening and the timber's bolt holes in the wall.
3. Where two constructions meet, the generator fits the junction (concrete cast against a slab with a mortar fillet; a sheet cut at the old barge board), and the junction is where the history reads. It is never hidden.
4. Each construction's parts are made with care, one at a time, against their own board: a cast step with its formwork lines and arris is a part family of its own, not a slab in grey pigment.
5. A repair never changes a construction in place: a patch is a repair material on the old construction; only a renewal changes `how`.

Every element shares this. The house already does: its volumes take their material from era, purpose, wealth and local rules, and `reclad` and `reroofed` are moves through constructions (`docs/building-system.md`). The catalogue generalises the era shelf to the ground, the roofs and everything between:

| Element | Constructions in the first pack, by year | What moves it on |
| --- | --- | --- |
| Steps | split-slab block to about 1920; thin treads on risers in any year (means); slabs in the ground (a society, 1880s); dressed granite (money, from 1870); cast concrete 1940 to 1980; precast after 1965 (unverified) | frost and a failed run; a cheap owner; conservation from the 1980s |
| Walls | dry-stone (craft); mortared rubble in lime to 1930; coursed granite (money); concrete from the 1920s; block from the 1950s (unverified); a concrete cap on old dry-stone (the road department) | a bulge; a road widened; a car |
| Paving | field stone; setts in rows from 1850; small setts in arcs 1910 to 1950; concrete slabs from 1909; tarred gravel from 1908; asphalt from 1922, everywhere after 1960; stone again from 1980 | traffic; the town's budget; a main laid |
| Roofs | slate; curved red tile; flat tile; felt (funkis); concrete tile from 1950; Eternit sheet 1950 to 1978; tin on sheds; tile again in restoration | a leak; a shortage; a fashion; a conservator |
| Fences and yard edges | picket; iron railings (money); wire from the 1920s and chain-link from the 1950s (unverified); a hedge; a low wall; nothing, where a car took the garden | a car; a feud; a child |
| Stairs in houses | timber; concrete from the 1930s; steel from the 1960s (unverified) | a conversion; fire rules |

A pack's catalogue is content; the shape of an entry and the rules for choosing and moving are the system.

### Facts, interpretations and texture (LF2)

The five kinds of thing on screen (`CLAUDE.md`) sort the record's outputs:

| Kind | In this system |
| --- | --- |
| Canonical fact | everything in `made`, `keepers`, `uses`, `works`, `events` |
| Visual interpretation of facts | wear depth, polish, lichen size, moss, coat wear, the number and spread of patches, weeds since a yard was left: derived from facts by written rules, so each claims only "it was used and kept this way" |
| Non-semantic texture | the grain, which slab cracked at which point, a dab's exact outline, a lean |
| Perceived information | records: signs, posters, a notice in a window, the paper, a deed; a neighbour's account of why the house was let go |
| Local scene state | tonight's bins, a bike, chairs out, a window open, puddles; from habits and the hour, committed only when it matters |

One rule decides the boundary: **a fact decides that and why; a rule decides how it looks; the seed decides which exactly.** A derived thing may never read as more precise than its facts. A patch drawn from a keeper's care has a year inside that keeper's decade, and that year is texture; if a game needs the year (a restoration game, a detective), it is pinned as a fact, by the engine or in the fixture. Until the engine's fabric pass runs these rules, derived works carry a new provenance, `derived`, beside `simulated`, `authored` and `generated-past` (`docs/engine-contract.md`).

### The causes

| Cause | What the engine decides | What Overstory derives |
| --- | --- | --- |
| People's lives | births, deaths, moves, marriages, household size, money, who lives where | occupation, extensions and divisions, letting, emptiness, the stuff layer |
| Uses and footfall | trips: who goes where and how often (habits, work, school, the shop) | a footfall field over the path network; wear, polish, bare lines, litter, staying traces |
| Businesses | opened, closed, changed hands, state (struggling, thriving) | the shopfront fitted or stripped, the sign and its ghost, boards, posters, the doorstep's polish, light at night |
| Keepers' care | the owner's money, whether they live there or let it, age, character; the town's budget per department and decade | repaint cycles, patch rates, campaigns' likelihood, garden tending or neglect |
| The town's plans | a plan adopted, how far it was carried out, which plot it reached (the engine's plans and the council's own) | a widened end, a stepped building line, a lone block, the scar |
| Era and fashion | the setting's timeline: booms, busts, waves of modernising | which shelf a replacement part comes from, the repair material of the year, colours |
| Weather and nature | the storms, floods and hard winters that matter, as events | rates of wear, frost, growth and fading from the pack's climate; the hourly weather in scenes |
| Accidents | a fire, a collision, a fall | the damage's run and the rebuild in the era's material |

The engine today has people with savings and jobs, workplaces with vacancies, habits with a place, wants for a house, a boat and a car, ventures that open a place in a neighbourhood, a council that decides and has plans of its own ("to widen the harbour road"), groups, and events with causes. It has no buildings, homes, trips as geometry, weather or budgets. Section 7 says what we ask for; until then fixtures carry it, labelled `authored`.

### The fields

Flow runs through fields, not through links between things. A field is a map over the town, computed from facts at a year, cached by decade, with stable sampling, so a thing's `place` is deterministic.

| Field | From | Written by | Read by |
| --- | --- | --- | --- |
| Feet | trips over the path network (Helbing's model for lawns and heath; segment counts for lanes) | doors, shops, schools, venues, stops | steps, paving, thresholds, lawns, posters, litter, snow and leaves that get trodden |
| Water | rain on roofs and ground, down gutters and downpipes to drains, down slopes; the tide band | roofs, walls, kerbs, the land | stains, moss, settling, frost, puddles, rot |
| Sky | the sky map (`SkyMap.cs`) | buildings, trees, the hill | growth, algae, drying, paint failure |
| Wind and salt | the climate and the land: sea-facing, height, shelter | the land, buildings, trees | weathering rates, trees' lean, rust, chalking paint |
| Soil | the land | the land | nature, settling |
| Care | keepers by decade | engine | every thing's patch, repaint and tending rates |
| Vacancy | businesses closed, homes empty, lots fallow | engine | posters, weeds, the cheap space ventures take (an engine decision, read from the same field) |

SimCity's GlassBox ran its simulation on the same split, agents and maps that units read and write (GDC 2012); RimWorld's decay is a field too: a thing out of the roof and rain loses condition every day, filth comes from use and goes with a keeper's cleaning (RimWorld wiki). Ours differ in that every field value traces to a fact.

### Continuity

Every derived quantity is a continuous function of the year except at a dated work or event. The shader reads years since a layer was reset, so two views a year apart differ a little, and a work is the only step. The life runs year by year (today the runner steps by decade and draws a year inside it; yearly steps cost nothing and make the years sheet smooth).

### Big change: quarters, the underground, demolition, slow building

(Øystein, 22 October: "should the town make it possible to include big renovations, an entire residential quarter changed, underground things, removing historical buildings, slow building processes?") Yes: they are the same record at a larger scope, with four extensions, and nothing built before them may assume a frozen plan.

1. **The plan is dated.** Every street, plot and building carries its years (there from 1874, cleared in 1967, a block on its ground from 1971), and the generators read the plan at a year. A quarter cleared and rebuilt is the plan's own history; a scheme carried out in part leaves its scar (a widened end, a stepped building line, a lone block). Stavanger's 1946 centre plan ("tear down and build") and the fight that saved Gamle Stavanger are the setting's precedent.
2. **Works take time.** A large work has dated phases (hoarding, the excavation, the frame, scaffolding, the finished building), each a state of its site, so a site that runs from 1984 to 1987 stands in the world and changes the street round it (the feet field detours, the hoarding gathers posters). Building-site parts are a part family of their own.
3. **Demolition leaves what it leaves:** the neighbour's gable laid bare (old wallpaper, flue marks, a roof line), a fallow lot that becomes a car park, foundations in the grass, a kerb line that remembers the houses.
4. **The underground is things too:** water and sewer mains, gas, cables, the tunnel, cellars and shelters, each with its route and years, seen on the surface by their traces (covers by era, trench strips, vents, portals) and whole only in a scene that goes down.

Who decides is the engine's (requests 14 and 21: the council's plans, developers and money); what it costs is content (building-site parts, new building eras) and regenerating the chunks a change touches, offline.

## 2. Flow: worked examples

The vocabulary, so every chain is made of the same verbs:

| Verb (engine fact) | Writes | Overstory derives | Reads where |
| --- | --- | --- | --- |
| open, close, change hands | `uses`, a record | shopfront fit or strip, sign and ghost, doorstep polish, feet on the lane, posters on the boards | street stop; 12 m |
| build, extend, divide, demolish | `made`, the diary | massing and parts by era; a seam; a gap and its fallow lot | city camera |
| buy, inherit, let, leave, die | `keepers`, `uses` | care up or down: paint, garden, patches; two window types in a divided house | 12 m; street stop |
| pave, dig, light, widen | `works` on the street | asphalt over setts, a trench strip, lamps by era, a scar where a plan stopped | city camera; street stop |
| patch, reset, renew, clean, paint, prune | `works` or derived patchwork | each repair as its own material and date, aged from then | street stop; eye level |
| plant, fell, graze, mow, leave alone | `uses` on the ground | trees as clocks, succession, a worn path, a lawn gone to moss | city camera; 12 m |

**The cannery and its street, 1898 to 1989.** The timeline's canning years build a brick cannery on the quay (1898, `made`), workers' houses in Tin Town behind it (1900 to 1915), and the shift's walk from Tin Town across the heath, which Helbing's model wears into a path by 1902 and the town paves as a lane in 1925 (a work caused by the feet field). The lane's steps carry 200,000 feet a year: polished middle, no lichen on the walking line, moss only at the walls' feet. The cannery is low road: hoists and openings cut in the 1930s, a painted name on the chimney in 1931, lorries from the 1950s that break the kerb at the gate and get a concrete toe on the quay (1958, the harbour's work). In 1982 the works close (the timeline). The feet field drops to a few hundred: within five years silver moss is back in the lane's joints, the steps' polish dulls, willowherb then young birch fill the yard (`docs/nature.md`, succession), the gates rust, the name on the chimney fades through its coats, broken windows are boarded by a receiver who keeps nothing (care 0). In 1984 a band rents the loft for next to nothing (vacancy; Jacobs: new ideas use old buildings): one lit window on Friday nights, posters on the boarded ground floor, a thin path worn again to the side door. In 1989 a developer's board stands at the gate, one wing is demolished (a gap, a gravel lot), the chimney stays as a landmark with three owners' names ghosting on it. Every arrow is a fact, a field or a rule; nothing in it was placed by hand.

**A family's house, 1949 to 1989** (a chalet house of 1905 in Tin Town):

| Year | The life (engine) | The thing (derived or a work) | Reads from |
| --- | --- | --- | --- |
| 1949 | a couple buy it (the want for a house of their own, achieved) | care rises; repainted in the decade's grey-white over the 1920s ochre; the garden dug | 12 m; the coat stack at the street stop |
| 1952, 1955 | children | a lean-to at the back (1958); a swing; washing on the line (stuff) | city camera |
| 1963 | money and the wave of modernising | husmorvinduer to the street; the surrounds stripped; the attic window kept | street stop |
| 1968 | electric heat | one chimney taken down; the ridge bare on one end | city camera |
| 1971 | a car (the want for a decent car) | the picket fence gone, the front garden paved; a dropped kerb | city camera; street stop |
| 1982 | oil money | plastic cladding; the plinth now proud; a plastic gutter | 12 m |
| 1985 | the children leave | care eases: the lawn longer, the lean-to's roof patched not renewed | 12 m |
| 1989 | the husband dies | the boat sold (the mooring empty); a neighbour's son mows; one lit window at night | city camera at blue hour |

The same house let to two families instead gets two window types, floor by floor, and a worn common stair (`docs/research/house-changes.md`).

**The gully steps, 1874 to 1989.** The record stands as built (`stone_gully.json`): laid 1874, campaigns in 1911 (lime) and 1952 (cement, depot stone), the town's care falling from 0.5 to 0.25 by decade. The flow adds `uses`: the ironmonger opens below in 1931 (feet up by half: polish spreads a hand's width each side of the walking line within two years), closes in 1974 (feet fall: the polish dulls, nothing regrows on the line because lichen takes decades and moss stands no feet), the café opens in 1988 (polish back by 1990, and two chairs on the landing wear a ledge). The cooper's yard wall beside it follows its own keeper: the cooper's heirs let it bulge from the 1950s, and the town rebuilds one panel in 1961 where the lane's drainage was the cause (the water field), in depot stone with cement pointing. The lantern is the street's: electric from 1909, the 1955 lantern on the same bracket, a fixing scar from the old one.

**A corner shop that changes hands** (the corner's house A): Vik Jernvare fits a 1930s front in 1931, painted lettering on the band; repainted 1949; a lit box sign over the lettering in 1962; closed 1974: boards, the box taken down, four fixing holes and a pale rectangle, the lettering ghosting through the next coat; fourteen empty years: the doorstep's hollow holds water, posters paste over posters on the boards (records of the Holm's gigs), the feet field skips the door; 1988: a young couple open a café, money short after the crash, so the front is patched, not renewed: boards off, the old band painted with the new name over the ghost, the step scrubbed (growth reset, hollow kept), two tables outside, cigarette ends by the door. In the wet, the old name shows through.

### From a person to the world

Øystein's question: a person in Understory gets angry, hopeful, wants to open a shop; can that go straight into the 3D world? Yes for acts, no for feelings, and the engine today reaches further than its front door yet shows.

**What goes straight through now.** The engine records these as facts with reasons, and each has a verb in the vocabulary above:

- A venture that opens is a new place with jobs (`projects.ts`). Overstory gives it a building: the cheapest fitting vacant space nearest the founder's home, from the vacancy field, deterministic and explained; writes `business_opened` into that building's diary with the engine's own cause; and the front is fitted, the sign goes up, the windows are lit at the hours its habits say, feet come to the step. Which building is Overstory's choice until the engine knows buildings (requests 5, 6 and 21), so it is `derived`. A plan that fails leaves nothing on the fabric unless the engine recorded an act that touched it: hope shows nowhere until it is a lease.
- Money and presence become care (request 13): savings, a job lost, drink, retirement, letting, moving away. Care is slow, so its trace is slow: the paint fails over a decade, the garden goes in three summers, the patches stop. Nothing changes the week someone is sad.
- A house, a boat or a car bought (the engine's goods) is an owner's thing with a year: a mooring filled, a drive paved, a fence gone.
- Moves, marriages, births and deaths change a home's household (request 15). House D's diary is exactly this: the owner dies, the heirs live in Oslo, boarded, neglected. Children in a small house give a lean-to by a rule with a rate (`derived`) until the engine decides works (request 14).
- Habits with a place give the hours: who is at the bar, which windows are lit, whose car is outside; the feet field needs request 16.
- A band rehearses where space is cheap (the vacancy field) and plays where the bar's shows are; each show is a poster drawn from the booked fact, and the wall by the venue becomes the band's coat stack.
- The council's own plans ("to widen the harbour road") become works when the engine decides them (request 14), carried out in part.

**How inner states show** (LF5). Only through acts and the traces they leave (`CLAUDE.md`, evidence not verdicts). The engine keeps feelings, strain, sore spots and wants; none of them reaches the fabric on its own. A feeling reaches it in three ways, each a fact: an act on a thing (a window boarded, a hedge planted against a neighbour, a door repainted, a sign torn down); a change in care over years (grief, drink or debt that lets a house go; a new partner who digs the garden); or a record that claims a reason (the paper's line, a neighbour's account), which may be wrong. Never as mood lighting on a sad house, a decal for grief or a colour for anger: a mood grades how a scene is seen and may not change a fact (`docs/visual-direction.md`, Mood). The engine's own human test says why: a vivid act read as a whole character made readers worse. So the house shows the act, a record may claim the cause, and the reading is the player's. Anger that never becomes an act is invisible, and should be.

**Feasible now, next, and hard.**

- *Now, on fixtures:* every item above is already a diary event or a thing's fact in the corner (A's café after the crash, D's heirs in Oslo, C's cheap windows). The corner through the years (section 8, step 7) proves the mapping on authored facts: a life's events in, the corner out.
- *Next, as #22 and #23 land:* habits give the hours and the feet; the timeline gives openings, closings and the waves; keepers, homes and works as decisions (requests 13 to 15) make the mapping a read, with no Overstory choice left in it. Then a person who wants a shop and gets one is seen to get it, and one who fails is seen not to.
- *Hard:* the engine deciding works at the rate real towns do without its lives reading as upkeep (its blind readers already score lives made of maintenance lower, so fabric works should be quiet events of the texture kind, weighty only when they turn a life: the shop, the house lost); city scale, where background neighbourhoods live by a coarse yearly pass with a spine of big events and no texture, so the fabric there runs from the spine (a death, a move, a venture) and its patchwork is made at promotion, as the engine makes friendships then; the two clocks, where tonight's chairs outside are scene state committed only if a scene made them matter; and attribution, since one trace has many causes, so the history budget and the `derived` rule must stop a player inferring more than the engine decided. None of this is too ambitious: most of the mapping is the diary's existing vocabulary. What would be too ambitious is a feeling that changes the world without an act.

## 3. How it looks its best

### What carries the read at each view

| View | What tells the history | What must stay calm |
| --- | --- | --- |
| City camera | roof material and colour by era; chimneys present or gone; extensions in plan; the yard: lawn, paved, gone wild; a fallow lot; trees as clocks; setts against asphalt and trench strips; the polished middle of a flight as one pale shape; lit windows at night | walls, texture, small marks |
| 12 m | fronts' colour and coats by decade; window types per floor; shopfronts and signs; a wall's rebuilt panel; a reset run's straighter line; order against disorder in gardens | joints, lichen, dabs |
| Street stop | lichen size on quiet edges; cement dabs and smears; trench lines and covers; ghost signs; posters; the doorstep's hollow; a dropped kerb; fixing scars | the grain |
| Eye level | tooling, crazing, the cement's sand, moss cushions, a patch's shoulder, the worn paint on a door's handle side, the smoothed ledge where people sit | nothing: this is where detail lives, clustered |

### Rationing: the history budget (LF4)

The strict reviews keep finding even speckle. The cause is marks without a shared cause, spread evenly. The rule: **marks from one cause are one shape.** A reset run is one straighter line; a lichen colony is one field with lobed edges; the quiet edge of a flight is one dark band; neglect is one darker house. Then a budget per view: at the city camera each thing tells at most one history; at 12 m two; at the street stop three; at eye level all of them, but clustered at edges, junctions, the walking line and the drip line, with calm between (Night City's dressers and Townscaper found the same). Which histories a thing tells is chosen by weight (the research's principle 2: caused by a named person, inside the game's window, unusual, linked to the player), and the rest become ordinary ageing. The budget is measured, not only reviewed: a count of distinct marks per thing per tier, and the form's value spread (`crown_value.py` generalised), beside the three-value rule a stone already has.

### Where the stunning comes from

- **Contrast of eras side by side:** the 1970s block in an 1890s row; the new white front among the ochres; a concrete quay toe against granite. Each is a fact, so following it leads somewhere (the anomaly rule).
- **Rarity by budget:** one loud thing per street, picked by weight; everything else quiet. A street of loud things is noise.
- **Landmarks that accumulate:** the cannery chimney with three names ghosting on it; the water tower; the flight of a hundred steps that every era patched in its own material.
- **Light on history:** wet polish on the walking line at blue hour; low sun raking lichen on the quiet edges; one lit window in a boarded row; snow that lies only on the steps nobody uses.
- **Events of weight:** a quay pushed out, a demolished block's gap, a fallen tree across a lane after the gale, a fire's rebuilt corner in brick. Few, dated, and the camera finds them.
- **Seasons on use:** leaves gather where feet do not go; the feet field sweeps them from the line (`docs/trees.md`, fallen leaves).

Dishonored 2 built Karnaca from two centuries of backstory and read class as oppositions, clean and dirty, empty and crowded; Disco Elysium's Martinaise is its regimes stacked (Bethesda, 2016; Film Stories, 2020). We get the same contrast from facts rather than from a dresser's hand.

## 4. How it serves every element

| Element | It brings | It shares | First user |
| --- | --- | --- | --- |
| Stone: steps, walls, paving, kerbs, quays | parts; wear by hardness and feet; settling and frost; damage tables (crack, corner, bulge, slip, scour); fix tables (dab, smear, wedge, pointing, reset, panel, toe, recast) | the layers, upkeep, the feet and water fields, growth | the gully (built); the corner's wall next |
| Streets: carriageway, pavement, trenches, lamps, covers, wires, kiosks | paving programmes and lamps by era from the town's budget; utility cuts on each utility's schedule (water 1866, gas, electricity 1909, telephone, sewer); traffic as a use | upkeep (town and utilities), the feet field, vehicles as owners' goods | the landing's setts and kerb |
| Houses and shopfronts | the diary (built); keepers and uses added; coat cycles from care; the repair layer on timber, render, roof and iron; shopfront fit, strip and ghost; records on the band and in the window | the layers, upkeep, the water field (drips, the splash line), the sky field | house A's coats and front |
| Interiors | rooms as the space plan and stuff layers: furniture by era and money, the household's size, worn thresholds, a stove's soot, a damp corner under a failed gutter | keepers, uses, the water field | one flat in three decades (the reality check) |
| Yards and gardens | tending as uses (mown, dug, planted, paved); succession when it stops; the car's hard standing; a washing line; sheds | nature's fields, keepers, the feet field | D's yard since 1986 |
| Trees | planting as a work; pruning and pollarding campaigns (the town's); storms as events; a limb lopped for a view (an owner's) | the growth timeline (built), upkeep's campaigns, wind | the corner's two birches |
| Quays and boats | the harbour's budget; the tide band; scour and the concrete toe; bollards and ladders; boats as owners' goods with a mooring as a use | stone, upkeep, water, salt | the heart's quay edges |
| Nature at the edge | grazing as a use with a keeper (the farm); succession; the town's expansion as events over land that already had a history | the fields and clocks (built) | the heath above E |

Each brings its parts, its damage and fix tables, and its rates; the record shape, the runner, the fields, the layers and the budget are shared. A table of rates per element goes in that element's design page, starting values marked unverified, as `docs/upkeep.md` does now.

## 5. Making it nice to work with

**One schema.** `thing.json` holds the record (section 1), validated: no use or work before `made`, keepers contiguous, a work's material allowed by the pack's shelf for its year, every `cause` present. The gully's `FLIGHTS` dict in `stone.py` becomes the first such file in `fixtures/`.

**One runner.** `upkeep.flight` becomes `life(thing, tables)`: yearly steps; damage by the element's table and the fields; patchwork at the keeper's care and the era's material; works and events in their year; a `life` record per part. Each element registers its tables; the runner knows no element. `upkeep.py --thing gully --at 1935` prints the life table, so a change is checked before Blender runs.

**Years sheets.** `LT1Years.Frames -thing gully -years 1900,1935,1960,1989,2020 -view street` renders the fixed view across years as one strip (Pentiment's three years of one town). The same for the corner. This is how flow is judged: the strip must read as one place changing for reasons.

**Debug views.** The `-history` view (cement in orange) grows into a cause view with modes: by layer age, by keeper, by work year, by origin (original, depot, new), by feet, by water. A why probe: click a part and get its chain (laid 1874; lifted 1911, the lower run reset after frost; cracked 1965; filled 1971 by the town's workman, care 0.25). Tiny Glade places its props by context (near doors and windows, aligned to walls, by whether paths or grass are there; developer post, 2024); our cause view shows the context a mark came from.

**Determinism.** Seeds from stable ids by SplitMix64 as the resolver does; a life hasher runs every fixture thing across years twice, the second time in shuffled order, and compares with committed hashes. Rules and tables are versioned: a change to a rate is a new version, never a silent edit, because it rewrites every thing's past.

**A new element joins** by a checklist: its parts approved; its damage and fix tables with rates; which uses act on it; which fields it reads and which it writes; its tiers and counts; one foreign-pack part; a years sheet; the strict review. Nothing else is new.

**Tiers and performance.** Life is computed offline per thing, cached by a hash of its facts and the rules' version, and rebuilt only when a fact or a field it reads changes; a change flows to the chunk that reads it, never to the town. Fields are textures over the town, redrawn by decade. The near tier reads the life per part; the street tier its mips; the city tier bakes the life into the merged mesh's vertex data (the polished middle as one pale shape); the far tier takes one scalar per thing (condition and age) for its impostor's tint. Unity runs no simulation per frame; it reads records and instance data, as the trees and the gully do today.

## 6. Variation across towns

The rules stay; the pack brings the content:

- **Materials and shelves by era:** what things are made of and repaired with, by year (lime, cement, asphalt here; Portland stone and York flags in London; brownstone, bluestone and a cement skim on the stoop in New York).
- **Keepers:** who keeps what (the borough keeps London's pavements; a New York owner keeps the sidewalk in front of the house; our town took the pavements over from the owners), and care curves by era from the pack's timeline (Oslo after 1899; the 1960s asphalt habit).
- **Climate:** rates of wear, frost, growth and fading; salt; the prevailing wind.
- **Uses and customs:** pollarding, stoops sat on, washing lines, cars in front gardens, when shops close.
- **Fashion waves:** the decades' modernisings and their reversal.

The foreign-pack check from `docs/foundations.md` applies: each element proves itself once with a foreign part running the same life (a brownstone stoop with its rusting rail, a York flag pavement with a gas trench, a pollarded plane). A pack never changes a rule; if it needs to, the rule was wrong.

## 7. What the engine needs

In `docs/engine-requests.md` (items 13 to 21); summarised here.

13 keepers and care; 14 works as decisions; 15 homes; 16 feet per path; 17 goods as things; 18 weather that matters; 19 derived works adopted; 20 small acts on things; 21 ventures take a building.

## 8. The order to build it in

Each step ends in something judged in Unity from the views, then the strict review, then Øystein.

1. **The runner and the record.** `life()` from `upkeep.flight`, yearly; the gully's record as `fixtures/things/gully.json` with `uses` from the corner's diaries (1931, 1974, 1988); the life hasher. *Judged:* the gully's years sheet, 1930 to 1990: busier in 1989 than in 1980, and a viewer can say so.
2. **The wall.** The cooper's wall as the second user: bulge and panel, cement pointing, the cause view. *Judged:* which panel was rebuilt, and when, read blind.
3. **The landing's setts and the kerb.** Utility cuts on the utilities' schedule; asphalt blobs after 1960; a dropped kerb. *Judged:* the street stop and the city camera; the trench reads as one shape.
4. **The feet and water fields** for the corner, from the diaries and the roofs; the gully, the wall and the setts rebuilt from them. *Judged:* the moss line follows the drips and the polish follows the door.
5. **House A's coats and front.** Keepers and uses in the diary; coat cycles from care; the shopfront's fit, strip and ghost; the sign as a record. *Judged:* the corner shop's four states at 12 m and the street stop.
6. **D's yard and the heath.** Nature on care; the path to A's door. *Judged:* the yard's three years since 1986.
7. **The corner through the years** (the plan's step 4), forward from 1989: 1989, 2000, 2010 and 2020 rebuilt live (show from 1989, remember from 1870: the past is the starting record, never rendered). Cold readers read it, and the history budget is measured.
8. **One foreign part** through the same life.
9. **The cannery street at the city view** (the plan's step 6): a closed works and the street round it, the first flow at town scale.

## Decided

- **One record and one runner for everything.** The record's shape is section 1's; `upkeep.flight` becomes `life(thing, tables)`; a fact decides that and why, a rule how it looks, the seed which exactly.
- **Flow through fields, not links between things.** A thing's own record still drives its own changes directly (a shop's front follows its own business); the fields carry what spills over to its neighbours.
- **A history budget per view,** measured as well as reviewed: one history per thing at the city camera, two at 12 m, three at the street stop, all at eye level but clustered. The numbers are provisional until the corner's years sheet sets them.
- **Derived works** carry the provenance `derived` until the engine's fabric pass runs the rules (request 19); a derived patch never carries a year a player can read unless it is pinned as a fact.
- **Care:** the engine gives its quantities (money, presence, age, the kind of person); the setting pack's curve turns them into care.
- **Small acts** touch things only where the engine records an act on a thing (request 20), so a street never fills with fences by rule.
- **Weather:** the storms, floods and hard winters that matter are the engine's events (request 18); the hourly weather in a scene is ours.

## Sources

Beyond the research pages this builds on (`world-that-remembers.md`, `repairs.md`, `house-changes.md`, `between-buildings.md`, `generating-the-past.md`, `nature.md`): Stewart Brand, *How Buildings Learn* (1994; shearing layers, low and high road) · Christopher Alexander, *The Nature of Order* and *A Pattern Language* (structure-preserving change; site repair) · Steven Jackson, "Rethinking Repair" (2014) and Shannon Mattern, "Maintenance and Care", *Places Journal* (2018): repair as the normal state · Helbing et al. 1997, desire paths · [GlassBox at GDC 2012](https://gamedeveloper.com/design/gdc-2012-breaking-down-em-simcity-em-s-glassbox-engine): resources, units, maps, globals · [RimWorld wiki: deterioration, filth, roofs](https://rimworldwiki.com/wiki/Deterioration_Rate) · [Cities: Skylines: level and abandonment follow land value and services](https://steamcommunity.com/app/255710/discussions/0/1640912849413899210) (community accounts; unverified against the game's code) · [Kenshi's town overrides when leaders fall](https://raiderking.com/kenshi-town-overrides/) (fan guide) · [Dwarf Fortress: a reclaimed site shows when it was founded and how it fell](https://dwarffortresswiki.org/index.php/DF2014:Site) · [Creating Karnaca](https://bethesda.net/en-AU/news/dishonored-2-creating-karnaca) and [Game Developer on Dishonored 2's oppositions](https://www.gamedeveloper.com/design/space-place-and-the-art-of-designing-deep-levels) · [Film Stories on Revachol](https://filmstories.co.uk/?p=83234) · [Tiny Glade's context-aware props](https://steamcommunity.com/app/2198150/discussions/0/4844273660400957331) and [its window wear](https://80.lv/articles/procedural-windows-in-pounce-light-s-tiny-glade-get-an-upgrade). Wildermyth carries history on people, not places; noted and not used.
