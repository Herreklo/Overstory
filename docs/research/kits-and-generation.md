# Kits, assembly and generation

How the best studios build large, rich, varied worlds at quality and sane cost: modular kits, how parts are assembled and fitted, and procedural generation. It covers what shipped games generated and what they authored, the methods and their craft, how generated content is kept good, and how kits carry eras, alterations and age. Then it sets our approach against all of it and says what to change before the houses (plan step 2). Three sibling studies sit beside it and are not repeated here: materials, surface history and the painterly look (`docs/research/materials-at-scale.md`), performance and quality control at scale (`docs/research/performance-at-scale.md`), and environmental storytelling and weathering (`docs/research/history-in-things.md`). Layout of towns and plots is in `docs/research/urban-design.md` and `docs/town-system.md`.

Written on Opus while Fable was out. Sources are marked: (primary) for the makers' own slides, papers, docs, blog posts and interviews; (secondary) for reports and notes by others; (unverified) for claims we could not check against a source we opened. Many talks exist only as members-only video, so some gaps remain; they are listed at the end.

## The idea in one paragraph

The studios we read that build big places at quality all do three things. It fixes a few standards before any part exists (a grid, footprints, pivots, opening sizes, floor heights). It splits the world into a small number of authored heroes and a large generated or kit-built background, and makes the two fit on shared footprints. And it puts its effort where the eye goes: corners, junctions, transitions, the places where one thing meets another. Generation is never one algorithm. It is a chain of stages, each with its own method: curves and costs for roads, packing rules for plots, a grammar for façades, kits for parts, rules and hands for dressing. The stages run in a fixed order and deterministically, so a change upstream can regenerate everything below it. Where the best results differ from the oatmeal is that their variety is made of a few big decisions with causes behind them. We already have the causes (the diaries, the facts, the living fabric). What we lack is the kit discipline and a framework that every kind plugs into, so that a new kind takes days and not weeks.

## Five findings

1. Kits are systems with standards, and the standards come first. Bethesda fixed door frames, minimum widths and walkable slopes before a single piece, and kept every piece inside a footprint whose sizes are multiples of each other (Burgess and Purkeypile, GDC 2013, primary). Two kit artists fed eight level designers who built more than 400 dungeon cells in about 30 months. Our generators have rules but no shared standards: each kind invents its own.
2. Shipped cities are a chain of stages, with authored heroes and generated filler on one footprint. Epic's City Sample runs city layout, roads, freeway, lots, buildings and furniture in dependency order, styles each building volume with a shape grammar, and makes custom geometry only for odd roofs (primary). Rome Reborn hand-modelled about 250 known buildings and generated about 6,750 others on the same footprints (primary). Ghost Recon Wildlands built a boss site by hand and let the tool grow the village round it (primary).
3. Change rides on parts, never on whole-building swaps. Fallout 4 broke composite pieces into floors, walls, corners and ceilings so that damage and layout could vary, at about six times the object count (primary). Cities: Skylines replaces a building when it levels up, and added a "historical" flag that keeps a building's look (secondary). Lea Kronenberger splits a window into a cut-out wall, frames and glass, so the opening stays and the fill changes (primary). Our diaries already change parts, but the resolver deletes the old openings when a shop is fitted, so their history is lost.
4. Hand improvements to generated output survive only behind locks and anchors. Wildlands' leads say plainly that work built on top of procedural output is lost at the next update unless the generated layer is locked first (primary). Lipp and colleagues (2008, 2011) keep artists' local edits outside the grammar, attached to semantic places (the second column on the third row) so they survive regeneration (primary). We forbid hand placement, but curation still needs pinned choices that survive a rebuild.
5. Perceptual variety comes from few, large, correlated, discrete decisions with causes; seeds give only texture. Kate Compton separates telling two things apart from remembering one, and notes that people like seeing evidence of process and forces (primary). Boris the Brave's remedy for oatmeal is to take freedom away: a few big choices per output, discrete palettes, rare feature flags on a budget, correlation, variation by region (secondary, expert). This is our "fact decides that and why, rule decides how, seed decides which", and it argues for keeping seeds small.

## 1. Modular kits: the craft

### Bethesda: kits as systems

Joel Burgess (level design) and Nate Purkeypile (environment art) gave the most complete public account of kit building, for Skyrim at GDC 2013 and Fallout 4 at GDC 2016. The slide decks are on SlideShare and were read for slides 1 to 100 of each (primary).

- Scale and team. Skyrim: 2 kit artists, 8 level designers, 7 kits, more than 400 unique interior cells in about 30 months. Effort followed use: the cave kit was used about 200 times and had seven sub-kits; the Ratway kit was used twice and had three.
- Standards first. A character is 128 units, about 2 m. Before any piece: the door frame size, the narrowest passable width (two characters), the walkable slope (about 30 to 45 degrees reads best, 60 at most), jump and cover heights.
- Grid and footprint. The grid is the kit's foundation. Footprints are often equal-sided (512 cubed) and every sub-kit's footprint is a multiple of the others: a 256 hall fits a 512 room, a 384 room leaves a gap. A footprint is the full bounding volume, negative space included, and every piece stays inside it. Snap is large, about half a footprint, so misalignment shows. Floor thickness is fixed in advance so no two surfaces share a plane.
- Names and pivots. Names encode kit, sub-kit, role and position, with a variant number from 01 (`UtlBayCorInMidL01`). One opaque code made a Fallout 3 kit underused. Pivots sit at bottom centre and never move: a moved pivot breaks every placed copy.
- Phases. Concept (about a week), a proof piece (one to three weeks, stress-tested by designers and artists together), a graybox of the high-use pieces in every sub-kit (one to four weeks), build-out, then polish for the rest of the project. One piece is finished fully before any variant; hero pieces come last, because standard pieces appear constantly and heroes rarely.
- Stress tests. Never test in ideal conditions. Loop a kit back on itself (gaps), stack it (floors and ceilings on one plane), and build a room from hall pieces (stray pillars), then decide which misuses to support. Fix a footprint fault at its root; "patch-up" pieces bloat the kit and hide its rules.
- Repetition. Players notice repeated clutter sooner than repeated architecture. Oblivion's copy-pasted dungeon cells were called cookie-cutter, so from Fallout 3 the designers got finer-grained pieces and stopped copying whole assemblies. Kits were mixed across settings (ice caves in Dwarven halls) and kept separate from the people and stories in a space.
- Breaking the grid. Snap to a rotated reference, pivot-and-flange tunnels, free-placed walls over a grid shell, small "glue" kits between sub-kits; about one logic quirk per kit.
- Fallout 4. Fourteen kits were planned (retail, institutional, church, industrial, house, vault, cave and others). Like kits were consolidated after asking what problem each one solved, and traditional construction of every type went into one Building kit with standard sub-kits (rooms, halls, stairs, railings, platforms). Composite pieces exported from 3ds Max gave way to granular pieces assembled in the editor as prefabs (Pack-Ins): one space went from 20 placed objects to 123, in return for flexible layouts, interchangeable kits and destruction. Layered inserts sat on top of base kits. A Russian transcript of the talk adds more (secondary). Eleven wall types with holes could meet one another in any pairing, 121 combinations. Standard sockets and plug pieces joined one kit to another. Damage came as separate detail pieces over prefabs. The Building kit's material variants were added in about two weeks. The engine merged placed pieces into precombined meshes for runtime (secondary; the Creation Kit pages that describe it could not be opened).
- What it cost. Kit artists who are both artists and technicians are rare; one fix to a heavily used piece can break hundreds of placements; designers are slow without a good kit.

Burgess's "Iterative Level Design Process" (GDC 2014, primary) adds a rule we share: no art hacks in early passes, because a hack should expose a problem and not hide it.

### Daggerfall: the block kit and its limit

Daggerfall (1996) built its towns from premade city blocks. The game's data holds 920 exterior blocks, each about 102 m square with up to 32 buildings. Its 5,090 towns are assembled from them as grids of at most 8 by 8 blocks (UESP file documentation and the Daggerfall Unity source, primary as reverse-engineered data). A block name is type, style, size and variant, with a fallback to the nearest name. The same models swap texture sets by climate and season. Reviewers at the time found the world hard to care about (secondary). No source blames the blocks directly, but the lesson Bethesda drew (smaller pieces, no copied assemblies) is on the record above. Starfield's reuse of a few hand-built points of interest across planets drew the same complaint in 2023 (secondary, opinion pieces). Coarse units of reuse read as repetition however good each unit is.

### Masters' own breakdowns

Environment and technical artists who wrote their methods down agree on a small set of moves.

- Lea Kronenberger (3D art lead, Frictional Games; primary). Main pieces on a power-of-two grid (1, 2, 4 m), small pieces at half a unit. A pivot centred in a wall's thickness lets one corner piece serve inside and outside corners. Split pieces further to multiply combinations: a cut-out wall, a few frames and several glass pieces make more windows than three finished ones; stairs as start, middle and end pieces. Break the grid with free small parts (ledges, single bricks) and walls off 90 and 45 degrees. Age shared pieces with decals, world-position tint, world-space dirt, vertex-painted blends and edge wear, and add dust late. Not everything should be modular: sometimes a decal or a unique piece is simpler. Merge pieces into bigger chunks for performance. The more often a set appears, the more variants it needs.
- Philip Klevestav ("Working with modular sets", 2010; primary). Only the connecting edges need to sit on the grid; everything between may wander. Derive many units from two base shapes by turning, flipping and cutting. Keep one texture structure across the set so one change updates all.
- Ayi Sanchez (lead artist, MachineGames; primary). Wear needs a visible cause, and its transitions depend on how hard the material is. Volume gets its own geometry; flat areas take tiling texture; edges take trims. Tall objects are split into logical sections that reshuffle into new variants.
- Ioana Oprisan (Star Citizen; primary). Damage as vertex paint and decals, with a damage mask and two damage variants packed on a second UV set.
- Scot Daniel Burns (trim sheets; primary) and Morten Olsen (Insomniac, "The Ultimate Trim", GDC 2015; primary abstract). One trim layout with fixed strip heights lets a material swap re-date or re-skin a piece without touching its UVs. Texturing belongs to the materials study; the kit lesson is that a fixed UV layout makes material a swappable fact.
- Simon Schreibt (tech-art analyses; secondary). Cyberpunk 2077 breaks a plain wall's edge by pushing a detailed stone mesh into a bevelled box. One decal hides the intersection and a parallax decal changes the silhouette, at three extra draw calls (with a CD Projekt developer's reply). Fallout 3 wrapped edge-damage decal geometry slightly proud of simple meshes and dropped it at lower detail.

### Recurring problems and how masters solve them

| Problem | What masters do | Who |
| --- | --- | --- |
| The grid shows | snap to rotated references; glue pieces; free small parts over the grid; walls off the main angles; only connecting edges on the grid | Bethesda, Kronenberger, Klevestav |
| Corners and transitions look cheap | detail lives at corners (corner modules); a pivot centred in the wall's thickness; a separate decoration pass on what is exposed | Townscaper, Kronenberger |
| Repetition | finer pieces mixed across kits; never copy assemblies; more variants for the most used sets; clutter varies more than architecture | Bethesda, Kronenberger |
| Seams between pieces and the ground | dirt strips generated where walls meet the ground; decals over intersections | Wildlands, Cyberpunk |
| Age and damage on shared pieces | vertex blends, world-space masks, decals, separate damage pieces, material swaps on fixed UVs | Kronenberger, Oprisan, Fallout 4 |
| Many states multiply cost | change parts, not whole places; few states | Fallout 4; Deus Ex: Mankind Divided's Prague (three city states and a shop that closes for good multiplied the work; secondary) |
| One fix breaks hundreds of uses | fixed pivots and footprints; stress tests before build-out | Bethesda |
| Performance of many pieces | merge placed pieces per building or chunk at build time | Fallout 4, Kronenberger, The Division |

## 2. Shipped cities: what was generated and what was authored

### The games

| Game | Generated | Authored | How it was curated |
| --- | --- | --- | --- |
| Marvel's Spider-Man (Insomniac, 2018) | ground, buildings, traffic, vignettes and crimes, props, impostors, light probes by procedural systems in Houdini and in-house tools (primary abstracts) | landmarks and street details (primary interview) | systems scoped from the start so their output takes manual polish; hand-authored work is kept when it still meets its specification after a change (primary abstracts). About 800 tiles of 128 m; every piece of architecture tagged with web points (primary interview). How buildings were assembled is not public (unverified) |
| The Matrix Awakens / City Sample (Epic, 2021) | city outline, roads, freeway, lots, buildings, furniture, traffic and crowd data, in Houdini, in stages: layout, roads, freeway, lots and sidewalks, buildings and ground, furniture and decals (primary docs) | input curves and zones, the modular kit pieces, roofs of non-rectangular buildings, collision, the freeway deck | each building is a volume styled by a shape grammar per style, often a base style and an upper style; hundreds of kit instances per building; Houdini writes one point cloud and a "Rule Processor" turns it into instances, 15 to 60 minutes a run (primary docs). Counts of about 7,000 buildings are from memory (unverified) |
| Ghost Recon Wildlands (Ubisoft, 2017) | roads by a costed pathfinder; rivers downhill; settlements by a packing tool with more than 70 rules per building, landmarks first, outward from the centre; generic building structure with enforced metrics (window and door sizes, floor heights) and dirt strips at the ground (primary interviews) | windows, doors and props added by hand; some places wholly by hand, such as a boss site with the village generated round it | lock the generated layer before building on it, or mark a manual area and generate round it; a light instancer allows tweaks without a recook; the biggest town was rebuilt more than five times; four Houdini artists, never more than 15 level artists (primary interviews) |
| Far Cry 5 (Ubisoft, 2018) | biomes, terrain texture, fresh water, cliffs, fences and power lines along splines, in Houdini inside the editor, tools chained so one's output feeds the next (primary abstract; secondary notes) | houses and vehicles along roads; some riverbeds, where hand control proved better | identical output from the same inputs on any machine, so the whole world regenerates nightly (secondary notes) |
| Horizon Zero Dawn (Guerrilla, 2017) | vegetation and much of the dressing placed at run time on the GPU from rules written like shaders over world data maps (humidity, temperature, distance to river) (primary) | rock formations and mountains wholly by hand | a small team owned the rule sets; deterministic and locally stable placement (from the slides via search; the PDF was too large to open) |
| Assassin's Creed Unity (Ubisoft, 2014) | modular, partly automated construction of Paris (primary, SIGGRAPH 2015) | Notre-Dame and the landmarks (more than a year for Notre-Dame; secondary) | about ten times the instances of earlier games, drawn by a GPU-driven pipeline with 64-triangle clusters (primary). About a quarter of buildings enterable (Ubisoft's pre-release figure; unverified) |
| The Division (Massive, 2016) | façades from a building tool: draw a footprint, choose kits, choose a kit piece per wall tile (primary, Johannes Böhm's own article) | blockout to real street scale from Street View; street furniture, markings, patches and hundreds of shop signs placed or made by hand | "templates" (prefabs with exposed options such as snow and litter) by the hundred; a level analyzer counting unique and total objects per sector (primary) |
| Cyberpunk 2077 (CD Projekt Red, 2020) | a road tool on splines that also scattered decoration (primary interview) | everything else, placed by artists: procedural tools were tried and the leads were never satisfied | four chronological styles explain the city's history; a rule of contrast; negative space where the eye rests; some early areas became too noisy (primary interview). Assembled from a hierarchy of prefabs (primary abstract) |
| The Witcher 3 (CD Projekt Red, 2015) | none of note | districts by social layer, each with a backstory; modular meshes reused and repurposed; texture arrays per district | avoid rigid grids, so places look built by people (secondary, talk summary) |
| Dishonored 2 (Arkane, 2016) | none of note | a city with two centuries of written history: waves of settlers, districts with their own past, materials from the land round them (secondary, with the art director's quotes) | history written before building; modular façades with LODs (primary, an Arkane artist's Q&A) |
| Rome Reborn 2.0 (CityEngine, 2008) | about 6,750 ordinary buildings by CGA rules written with archaeologists; temples from about a hundred attributes in Vitruvius's proportions (primary paper) | about 250 known buildings, about 30 modelled by hand | same footprints for both, so they fit without fixing; three detail levels chosen by painted importance maps; the whole model regenerated when scholarship changes (primary paper) |
| Anno 1800 (Blue Byte, 2019) | none of note | every residence on the same 3 by 3 footprint across tiers; class read through palette and material; 250 polygons and a 256-pixel texture per grid tile (primary devblogs) | blockout checks that a building fits the cityscape before detail |
| Minecraft villages | villages from template pools joined at jigsaw connectors, with fallback end pieces; processors age a placed template (moss and cracks by a mossiness value) or remove blocks by an integrity value; 2 per cent of villages are abandoned, from separate piece lists with missing doors and mossy stone (secondary, the game's wiki docs) | every template | none beyond the pools |
| Daggerfall (Bethesda, 1996) | towns assembled from 920 premade blocks | every block | none; the world read as samey |

No developer source was found for Red Dead Redemption 2, Kingdom Come: Deliverance, Ghost of Tsushima, inFAMOUS Second Son or Hogwarts Legacy. Mafia III's New Bordeaux was compressed from archive photos with landmarks kept roughly in place as points to steer by (secondary); nothing public on kits.

### What the games share

- A chain of stages, each with its own method. Layout (curves, costs, zones), lots, massing (volumes), styling (a grammar), parts (a kit), dressing (rules plus hands). Each stage reads the one before, in a fixed order, so the world can be regenerated from its inputs. Insomniac's lesson is that the systems end up carrying far more than planned, so dependencies are designed from the first day.
- Heroes by hand, filler by rule, on one footprint. Rome's two classes, Wildlands' boss site, Horizon's rocks, City Sample's custom roofs, Spider-Man's landmarks. The filler is good because it is constrained by metrics (window and door sizes, floor heights) the heroes also obey.
- Hand polish survives only behind a lock or an anchor. Wildlands' leads put it in one line: "When you start to build on top of procedural you have to lock it." Insomniac keeps hand work that still meets its specification. None of them trusts regeneration alone.
- Determinism is what makes regeneration safe. Far Cry 5 rebuilds nightly because the same inputs give the same world on any machine; Horizon's placement changes only where an edit was made.
- Hand-built cities still rest on a grammar of eras. Night City's four styles, Karnaca's settler waves, Anno's tiers, Witcher's districts. In each, the variety reads because a written history explains it.

## 3. Methods and their craft

Town and plot layout (Parish and Müller's roads, Watabou, space syntax) is covered in `docs/research/urban-design.md`. This section is about buildings and parts.

### Shape grammars

CGA shape (Müller, Wonka, Haegler, Ulmer and Van Gool, 2006) builds a building as a hierarchy: a mass model of volumes, then façades by splitting faces, then detail. Its operations survive in Esri CityEngine's CGA (primary docs):

- Split divides a shape's scope along an axis into absolute, relative or floating sizes; a floating part absorbs what is left. Repeat fills a span with as many whole copies as fit, adjusting the count and floating sizes to the best fit.
- Component split turns a volume into faces, edges or vertices, selected by direction (front, side, top), by roof edge (eave, hip, valley, ridge) or by street-facing edge.
- Setback pulls chosen edges in by a distance, per edge.
- Occlusion queries (inside, overlaps, touches) test a shape against closed occluders in the same building or the neighbours' lots, so a window that would sit behind a neighbour's wall is dropped. CityEngine runs context queries in a deterministic two-pass process.
- Snap lines that align floors across separate volumes are part of the 2006 paper (unverified: its PDF was too large to open). A later paper that uses its notation confirms split, repeat and component split, and that CGA has no direct support for curved surfaces (primary).

Wonka and colleagues' "Instant Architecture" (2003) added a control grammar that spreads design decisions (a floor's window type) over a façade separately from the split rules, and attribute matching to choose rules (primary abstract; details unverified). Schwarz and Müller's CGA++ (2015) made shapes first-class so rules can act on several shapes and coordinate through events, because a rule refining one shape knows nothing about the others (primary abstract). Lipp, Wonka and Wimmer (2008) name the cost of local exceptions: each variation needs new rules and new variables, and the rule base explodes (checked in the paper's text). Their fix is locators stored outside the grammar: exact (a path through the derivation) or semantic (the second column on the third row), which can pin a random choice, choose a rule or replace a part. Semantic locators survive most edits; persistence is hardest when the rules themselves change (primary). Lipp, Scherzer, Wonka and Wimmer (2011) extend this to whole layouts with anchored assignments that re-attach to the nearest element of the same type when their anchor disappears (primary).

Unreal's PCG shape grammar (primary docs) brings the same idea to a one-dimensional line: symbols for modules, `*` for as many as fit, `+` for at least one, weighted choices, and `<A,B,C>` to place A if there is room and fall back to B, then C. Epic's worked example is a fence with broken sections. This is exactly the tool for kerbs, copings, gutters, railings and fences.

Good at: hierarchy, alignment, multi-scale detail, cheap deterministic variation on boxy architecture. Fails at: local exceptions (rule explosion), curves, context across lots without queries, persistence of edits, and history (a grammar says what a façade is, not how it came to be). A craftsperson adds: hand-made terminal parts, persistent local overrides, occlusion pruning, and a separate layer of irregularity that claims nothing.

### Wave function collapse and model synthesis

Maxim Gumin's wave function collapse (WFC) fills a grid cell by cell, always collapsing the most constrained cell and propagating what that rules out (primary README). It descends from Paul Merrell's model synthesis (2007), which assembles hand-made pieces on a 3D grid by adjacency; Merrell calls the two nearly identical (primary). His later journal paper with Dinesh Manocha (IEEE TVCG) has the useful comparison (primary). Model synthesis is good at detail at one scale and poor at several scales, where grammars do better. It keeps empty space honest, avoids self-intersection and closes paths, which grammars struggle with. It needs a grid and has trouble with curved and organic shapes. Boris the Brave adds four points (secondary, expert). WFC rarely makes large-scale structure, so layouts must come from elsewhere. Tiles are best designed by their corners. Fixed tiles, path constraints and region-by-region tilesets give control. Editing a WFC result in place is slow and unsatisfying. Corner-based tiling needs 16 tiles in two dimensions (6 with rotation); the "blob" set needs 47 (secondary).

For us WFC has one sensible job: local fit at junctions (where a roof meets a gable, where walls meet at odd angles), inside a structure another method decided. It should never decide a layout, and it must never fail silently, because a wrong piece is a false claim about history.

### Townscaper and Bad North

Oskar Stålberg's towns sit on an irregular quad grid (a hexagon grid split twice into quads and relaxed). Modules are corner segments chosen marching-cubes style, so the detail lives where things meet, and they are deformed into the irregular cells; pieces can be skewed a fair way before it shows. Structure is chosen first and decoration in a second pass on what is exposed; windows are cut afterwards with a stencil so none is split by a corner. Bad North used more than 300 tiles; a Townscaper reskin would need about 500. Stålberg wants the large shapes predictable and lets small shapes vary; Townscaper takes the highest-priority valid tile rather than a random one, so players can learn the rules (secondary: Tommy Thompson's interview-based article; Boris the Brave). The talks are video only.

The lesson for us is the corner: a kit authored by its junctions, fitted into irregular cells, with decoration as a separate pass. Our houses already decorate after the structure (`docs/building-system.md`, step 4).

### Tiny Glade

Pounce Light's generators assemble buildings brick by brick, and each element has its own generator and pipeline (primary, Steam dev diaries; 80.lv interview). Their first wooden wall was a texture and was rejected as not touchable enough. Planks are now placed one by one like the bricks and split round arches, windows, doors and roofs. Freeform walls take only vertical planks, to avoid an unsolved layout on curves. Roof tiles are individual pieces. Half-timbering adapts to where windows go, and large brackets give way to make room for windows and doors. Decorators recompute when the terrain changes. Stairs reached a fifth prototype before they felt right. Anastasia Opara writes every rule herself (primary interview). The craft lesson: parts are physical and individual, every part checks its context and has a fallback form, and only what an edit touches is recomputed. A claim that window damage is driven by a signed-distance attribute comes from an 80.lv summary and could not be checked (secondary).

### Watabou

Watabou's generators aim at a good-looking map rather than a true model of a town, and say so (primary). His house plan generator often fails to assign rooms that meet their requirements, and he notes it is not a planning tool (primary). The lesson: a generator that makes nice pictures and one whose output must be true are different machines.

### Interiors

- Interior mapping (Joost van Dongen, 2008): rooms behind windows drawn in the pixel shader by tracing rays against virtual floors and walls (primary). The number of rooms does not change the frame rate; cost scales with screen pixels; a corner room reads as one room from both sides. Spider-Man's windows are widely said to use it (unverified).
- Shadows of Doubt (Cole Jefferies): a city where every room in every building can be entered (primary devblog). Floors of 15 by 15 tiles of 1.8 m are zoned by hand into addresses. Rooms are placed in order of importance, each at the free position that scores best on floor space, a simple shape and windows. Hallways are drawn when the entrance is far from a corner, so no room is reached only through another. Some rooms may connect only to certain others.
- Merrell, Schkufza and Koltun (2010): a Bayesian network trained on 120 real plans turns a few requirements into rooms, adjacencies and sizes, and an optimiser lays them out. They learned the rules from data because architects' rules of thumb were too many and too vague to write down (primary). Their layouts start from the inside; ours must start from a façade that history has fixed, which is the harder direction.
- Assassin's Creed Unity built interiors entered without loading as massive instanced geometry (primary, SIGGRAPH 2015).

### Our toolset

Houdini runs every big pipeline above (Spider-Man, City Sample, Wildlands, Far Cry 5). It is out for us: Houdini Apprentice forbids commercial use and its digital assets cannot run in Houdini Engine, and Houdini Indie is paid, with a revenue cap (primary FAQ; price about 270 to 300 dollars a year, unverified). Our Houdini is Blender, Python and numpy, run headless, with the stages written as plain functions. What we lose and where to get it:

| Houdini gives | Our free equivalent |
| --- | --- |
| a node graph of stages, PDG to run them in parallel | plain Python stages with a hashed plan between each; `multiprocessing` for batches |
| point clouds with attributes as the hand-off to the engine | the plan as JSON, which Unity reads (as `street.json` already does) |
| straight skeleton for roofs over any footprint | `bpypolyskel`, a Python library used by the Blender OSM add-on and tested by its authors on 320,000 hipped roofs from OpenStreetMap, 99.99 per cent successful (secondary; licence unverified) |
| PolyReduce for detail levels | Blender's Decimate; Unity 6's Mesh LOD at import; meshoptimizer (MIT licence) through a wrapper (unverified) |
| shape grammar nodes, labs building tools | our resolver and a small split and one-dimensional grammar of our own |

Blender's Geometry Nodes are free and fast, and the free Buildify library shows a kit-based building generator in them (secondary). We should not move generation into node graphs: our generators are judged by diffs, hashes and stress tests, and Python text does that better. Geometry Nodes may still serve as a quick preview of instancing.

### Methods at a glance

| Method | Good at | Fails at | We use it for |
| --- | --- | --- | --- |
| Shape grammar (CGA, split grammar) | hierarchy, floors and bays, alignment, determinism | exceptions, curves, history | façades from the plan's volumes; the base and the upper floors as two styles |
| One-dimensional grammar along a line | anything linear with start, fill and end pieces and fallbacks | corners that are too tight | kerbs, copings, gutters, eaves, belt courses, railings, fences, quay edges |
| Packing with rules | plots, settlements, things in a yard | global taste | street things and yard things placed by rules (Wildlands-style) |
| WFC, model synthesis | local fit at one scale | layout, several scales, silent failure | junction detail inside a decided structure, if ever |
| Corner modules (Townscaper) | detail where things meet, irregular cells | thin parts | roof junctions, wall ends and corners |
| Growth and simulation | trees, settling, wear | speed | trees (built); the living fabric's fields |
| Allocation by priority and score | rooms behind a fixed façade | character | interiors (plan step 8) |

## 4. Keeping generated content good

### Oatmeal, and what makes things memorable

Kate Compton's "So you want to build a generator" (2016, primary) asks a generator's maker to name the artefact, list its good properties and its deal-breakers, and only then choose a method. Her oatmeal: it is easy to make ten thousand bowls that are each mathematically unique and all look like oatmeal. Perceptual differentiation (this one is not identical to the last) is enough for a row of trees; perceptual uniqueness (this one is memorable, a character rather than a face in a crowd) is much harder. People like to see evidence of process and forces, such as soil pushed up at a tree's foot. She suggests generate-and-test for the constraints a machine can check, and steering the generator away from bad output for the ones it cannot. Tiles cannot invent new tiles, grammars handle long-range relations poorly, and parametric methods give variation without surprise.

Evidence of process and forces is the living fabric's whole premise. Our facts are the forces; the generator draws the process. That is our way out of oatmeal, as long as the seed stays small.

Boris the Brave's "Oatmeal spice" (2026, secondary, expert) gives the working rules. Make interest by taking freedom away. Make a few big decisions per output, from short discrete lists rather than continuous ranges. Keep feature flags rare and budget them: flag chances summing to 50 per cent give about a 40 per cent chance that one fires. Correlate properties, and vary by region and at several scales. A rule must be established before it can be broken.

### Measuring a generator

Gillian Smith and Jim Whitehead (2010) plot thousands of outputs on two metrics as a heat map, the expressive range, and found a bias in their own level generator from a detail they had thought too small to matter (primary). The PCG textbook's chapter adds: pick metrics as far as possible from the input parameters, grow the sample until the plots stop moving, and pair the plots with people's judgements (primary). For us one metric should come from the facts and one from what is visible (`docs/research/tools-and-performance.md`, the range plotter), so variety is tested for readability.

### Hero, then generator

Every good pipeline above starts from one finished piece. Bethesda finishes a proof piece and one fully polished piece before variants. City Sample began from a benchmark building, whose maker also helped write the rules for where to break buildings into pieces (secondary: a search snippet of the artist's ArtStation page). Rome modelled its known buildings first. Wildlands set a boss site and grew the village round it. Our plan already makes each kind's first slice the corner's own. The rule to add: the hero is made by the generator from facts and pins, never as a separate hand version, so the generator cannot drift away from the hero.

### Curation without hand placement

We forbid placing things by hand for one frame. Curation still needs ways to say "this one, not that one" that survive a rebuild:

- Pins as facts. A pinned choice (this tread's slab, this house's door) is stored as data anchored to a stable semantic id, carried in the fixture with its own provenance, and checked again on every rebuild. Lipp's semantic locators and anchored assignments are the model; Wildlands' lock is the cruder version.
- Deterministic reseeding. When a generated part fails a check, the generator tries the next seed in a fixed sequence and records which one it took. Compton's generate-and-test, made repeatable.
- Stress tests per kind. Bethesda's loopback and stack tests are our `stress.py`; every kind gets one, with random facts inside their ranges.
- Counts and monitoring. The Division's level analyzer counted unique and total objects per sector. Each kind reports its part counts, unique meshes and triangles per tier, measured beside the performance study's budgets.

## 5. Buildings in particular

### Façades

Every shipped approach treats a façade as floors and bays filled from a kit. The Division draws a footprint, chooses kits and picks one kit piece per wall tile. Wildlands builds a generic structure with enforced window, door and floor metrics. City Sample styles a volume by a grammar per style, with a separate base style. Our resolver already does this in integers (columns and storeys, floor lines snapped across volumes of one era, parts from the shelf of the installing year). Two additions from the research:

- The ground floor as its own style. City Sample splits a volume into a base and an upper style. Our ground floors change far more often than the floors above (shopfronts fitted and stripped, doors moved, a dropped plinth), so the ground floor should be resolved as its own grammar over the same bay lines.
- A control layer of big decisions per building. Instant Architecture's control grammar, Boris's few big decisions. Per building, before any cell: its era's window family per floor, its trim set, its colour family, its care. Every cell then reads those, so a house is one coherent decision with texture inside it.

### Openings and fills

Kronenberger's split window, Townscaper's stencil-cut windows and Tiny Glade's adaptive windows agree: the hole in the wall and what fills it are separate things. History agrees too. An opening is structure and dates from the volume or from the event that cut it; a sash is skin and dates from its installing event; a husmorvindu is a 1960s sash set into an 1890s opening with the rest boarded in (`docs/research/house-changes.md`). Our resolver has the start of this: a cell holds its opening (position and size) and a part with its era and event, keeps the `original` part when windows are replaced, and marks `reduced` when a smaller standard window goes into an old opening.

Three gaps. The history is one step deep (`original` only), so a house whose windows were replaced twice forgets the middle. Fitting a shop deletes the window cells it covers, so when the shop is stripped the old openings cannot come back and leave no scar. And a fill that does not fit its opening has one remedy, `reduced`, for one style. The fix is to make every cell a dated record: the opening with its year and cause, and a list of fills, each with its event, its years and how it was fitted.

### Fitting a part into an opening

A part declares how it fits, and the generator chooses the first way that works, in order:

| Fit | What happens | Example |
| --- | --- | --- |
| exact | the part's size range covers the opening | a 1905 cross window in a 1905 opening |
| stretch | the part has fixed corners and stretchable rails and stiles (nine-slice); it stretches within its stated range | a sash 10 per cent wider than its model |
| adaptor | the part is smaller and the gap takes an infill (boards in the wall's cladding, a new reveal) from the installing year | the husmorvindu in an old opening |
| change the opening | the event itself recut the opening; the old reveal leaves a scar in the cladding | a 1930s funkis band window cut across two old openings |
| refuse | nothing fits; the building system's give-way order applies | a part the resolver chose with no room |

### Sockets as dated containers

Sockets exist in the design (`docs/building-system.md`: sign bands take signs, eaves take gutters, corners take downpipes) but not yet in code. A socket should hold its history the way a cell does: which part sat there and when, and what removing it left. Four fixing holes and a paler rectangle mark where a box sign hung; a capped stub, where a chimney stood; a ghost of lettering lies under the next coat. The leftover mark is a fact of the removal and comes from the removed part's own definition (a box sign knows its fixings). This is the kit form of the living fabric's rule that a removal leaves what it leaves, and the gentler cousin of Minecraft's processors: ours are never random.

### Roofs

City Sample made custom roofs for every non-rectangular footprint because its kit could not; Tiny Glade builds roofs from individual tiles cut to the slope; our builder already solves roofs over combined footprints and falls back to one roof per volume. A straight-skeleton library (`bpypolyskel`) would make hipped roofs over irregular footprints reliable. Tiles and slates are manufactured, repeated pieces: a small library instanced along courses near the camera, a painted surface further off.

### Alterations over time

No shipped game we found models a building's alterations decade by decade as data. What games do instead, and what it teaches:

| How change is carried | Game | Cost and lesson |
| --- | --- | --- |
| Separate detail pieces layered on a stable base | Fallout 4 (destruction, inserts) | cheap per state; the base never changes, so every state fits |
| Material swap on a fixed layout | Fallout 4, Daggerfall (climate and season), trim sheets | re-dates a part without new geometry; needs fixed UVs |
| Vertex paint, masks and decals per instance | Kronenberger, Oprisan, Cyberpunk | ages shared pieces; per-instance data |
| Post-assembly processors | Minecraft (moss, cracks, missing blocks; abandoned villages) | cheap and random; for us only texture may be random |
| Whole-building replacement | Cities: Skylines (levels), Anno 1800 (tiers) | loses identity; Cities: Skylines added a "historical" flag to keep a building's look |
| World states | Deus Ex: Mankind Divided's Prague, Witcher's burned villages (unverified) | each state multiplies the work |
| Regeneration from changed knowledge | Rome Reborn | the model follows the facts; only possible with rules |
| History written before building | Dishonored 2, City 17, Night City | variety reads because eras and settlers explain it |

The conclusion for diaries: change parts and layers, never whole buildings, and keep each change's record in its cell or socket. Let the junction where two eras meet carry the reading (`docs/living-fabric.md`, Moving through constructions, rule 3). Drop small marks at distance and keep the big ones (a reclad volume, a missing chimney) at every tier.

### Interiors

Interiors are plan step 8, but the house plan must make room for them now. "A window has a room behind it" is already a hard rule. The plan should carry, per window, the room behind it (its floor, its kind, lit or not, whose household), so lit windows tonight, interior mapping at the street stop and real rooms in a scene all read one fact. Then three tiers. Interior mapping goes behind every window, cheap at any count. A shallow real room goes behind ground-floor shop windows and the windows a scene looks into. Full interiors go only where a scene goes, allocated Shadows-of-Doubt style inside the openings history fixed.

## 6. Our approach against this

### What we do right

- Facts before generation. Diaries, flights and walls carry who built them, when, with what means, who kept them and what was done. No shipped game we found has this layer for its buildings. It is the causes that Compton's "evidence of process" needs, and it makes our variety mean something.
- A plan in integers between facts and meshes, for houses. The resolver turns a diary into a plan in grid cells, millimetres and enum ids, with a canonical signature for hashing (`plan_signature`). This is City Sample's point cloud and Far Cry 5's determinism in kind. The plan hasher that runs fixtures across years twice, the second time shuffled, is designed (`docs/building-system.md`) but not yet built.
- Parts from the decade they were installed, chosen by event. A new event re-picks only its cells: Fallout 4's granular change, at the level of facts.
- Big decisions from facts. `stair_facts.py` chooses construction, stone, finish and keeper by district and role: discrete, correlated, caused. The twelve-flight variety sheet is an expressive-range check by eye.
- Parts shaped alone on a quick sheet, then fitted. The slab, the wall stone and the sett are made once and judged on `slab_sheet.py` in seconds: Bethesda's proof piece.
- Checks and stress tests. `validate.py` and `stress.py` (1,564 random buildings) are Bethesda's loopback and stack tests made automatic, and failures are fixed at their cause.
- Shared systems. Wear, growth, water and upkeep are modules every generator calls, and their results are baked per vertex for one shader stack, much as Tiny Glade bakes context into vertex data.

### What is not yet right

1. Kinds are monoliths. `stone.lay` is about 480 lines in one function: it reads the lane, sets out the flight, lays the slabs, runs the upkeep, and inside a nested `put()` it applies wear, growth, moss, water and the sky bake per piece and writes the mesh. `wall.py` repeats much of it. A new kind (the kerb, the sett field, the plinth) today means copying and editing a generator. That is the "day per element" cost.
2. No plan stage for stone. Houses have a plan between facts and geometry; stone does not. Without it a flight cannot be drawn at two tiers from one decision, cannot be diffed between years cheaply, and cannot be assembled in Unity from parts.
3. Facts by name. `stair_facts.facts_for` chooses a flight's life by matching the lane's name ("passage at", "the way to ... empty since"). The town system already plans to read the plan unit instead (`docs/town-system.md`, section 6).
4. No shared standards. Each generator sets its own constants: the stride, a course's height, a storey of 3 m in the skill and 2,850 to 3,000 mm in `eras.py`. Nothing states the town's metrics in one place: storey heights by era, opening sizes, step rises, kerb heights, wall thicknesses, board widths.
5. One meaning of "part", unstated. The skill (`blender-generators`) says a part is modelled by hand in a `.blend` through the MCP and that a grid module is 1 m with colour from one palette. In practice our parts are scripted part functions (`slab(seed, width, depth, thick)`), shaped by eye on a sheet, called once per instance to make unique geometry, with painted grain textures. The practice is good; the written rule is out of date and silent on when a part is a fixed mesh and when a function.
6. Every stone unique, always. Each slab, wall stone and sett is its own mesh with its own baked history, merged per flight. The steps and walls carry about 600,000 triangles against a city-tier budget of about 2,000 per flight (`docs/foundations.md`). Uniqueness is right for a tread that a hundred years of feet have worn; it is waste for a sett, a roof slate or a wall stone nobody touches.
7. The channel layout drifts. `stone.py`'s header says UV2.y is the slab's variation; its code writes water there, as `docs/foundations.md` says. `wall.py`'s header repeats the stale line. The vertex streams are a contract with the shader and need one definition in one file.
8. Sockets and fills are designed but thin. No socket exists in code; a cell's history is one step deep; a fitted shop deletes the openings it covers (`_shop_fitted`), so its stripping cannot restore them or leave a scar.
9. Every generator has its own export. `stone.build`, `wall.build` and `export_street` each select, export FBX and write a JSON beside it in their own way.

### What should change before the houses

#### One pipeline every kind plugs into

Every kind runs the same stages. Each stage has one owner and its output is data that can be hashed, diffed and cached.

| Stage | In | Out | Owner |
| --- | --- | --- | --- |
| 1. Facts | the fixture or the engine; the town plan | the thing's record (`thing.json`, `docs/living-fabric.md`) | the engine; the pack; rules until the engine has them |
| 2. Plan | facts, the place (fields, terrain), the kind's layout rule | a list of part instances in integers: part id, variant, seed, placement, fit, which fact or event put it there, its sockets | the kind's rule |
| 3. Life | the plan, the record, the shared fields | per instance: years since each layer was reset, wear, damage and its fills, origin | the runner, `life(thing, tables)` |
| 4. Geometry | plan, life, the part library, a tier | meshes (unique where a part is fitted or worn) and instance lists (where it is not) | the parts and one assembler |
| 5. Bake | geometry, life, the fields | the vertex streams and instance data the shader reads | the shared systems (`wear.py`, `growth.py`, `water.py`) through one channel spec |
| 6. Export | meshes, instances, the plan | FBX or instance JSON, one manifest per thing | one export module |
| 7. Checks | everything above | pass or fail, with counts per tier | `validate.py` per kind, the stress test, the kit validator |

The plan is the contract with Unity, as `street.json` already is for the street: Unity places parts from the library at the plan's transforms and runs no generation (`unity-conventions`). The why-probe in `docs/living-fabric.md` falls out of stage 2, because every instance knows the fact that placed it.

#### A kind defined as data

A kind is a small module in `blender/kinds/` that registers what it is; the runner knows no kind. It declares:

| Field | What it holds | For the flight of steps |
| --- | --- | --- |
| facts | the record's schema and the pack's catalogue of constructions | built, `built_as`, stone, finish, keepers, works, footfall |
| layout | one function: facts and place to plan | `flights_of`, `step_plan`, `widths` (as they are today) |
| parts | the part families it uses and how each fits | slate slab (fitted, worn), sett (library), cement dab (repair part) |
| systems | which shared systems act on it and their tables | wear (feet), growth, water, upkeep (crack and fix tables) |
| channels | which vertex streams and instance fields it writes | polish, lichen, moss, water held, years bare, seed |
| tiers | what each tier draws and its budget | near: every slab; street: merged, simplified; city: one mesh with baked life |
| checks | its own validation and stress ranges | too steep to climb; no ladders; joints bridged |
| sheet | its quick sheet and variety sheet | `slab_sheet.py`, the twelve flights |

The existing code moves into this shape rather than being rewritten: `step_plan` becomes the stairs' layout, the body of `put()` becomes stages 3 and 5, `make` and the FBX code become stage 6.

#### Parts with metadata

Every part family gets a definition beside its code, the sidecar that `docs/research/tools-and-performance.md` proposed. A window, for instance:

```json
{
  "id": "window.cross_t",
  "family": "window",
  "era": [1865, 1915],
  "made_as": "fixed",
  "opening_mm": {"w": [700, 1100], "h": [1200, 1700]},
  "fit": ["exact", "stretch", "adaptor"],
  "stretch": {"w": 0.12, "h": 0.10},
  "pivot": "opening_bottom_left",
  "sockets": {"sill": ["flower_box"], "head": ["crown"], "sides": ["shutter"]},
  "leaves_on_removal": ["reveal_scar"],
  "tiers": {"near": 1800, "street": 300, "city": "baked"},
  "variants": 3
}
```

`made_as` says which of two kinds of part it is:

- fixed: a finite set of meshes made once and reviewed as they are (a window of an era, a lamp, a bracket, a sett, a roof slate, a gutter section). Variety comes from choosing among a few variants, from mirroring and turning where the part allows, from stretch zones, and from per-instance data (age, care, coat). Instanced wherever its history fits in instance data.
- fitted: a part function called per instance because its shape is a fact (a tread's width across a lane and its worn hollow; a wall's run; a board cut to a roof line). Unique geometry, merged per thing.

The rule between them: geometry that must fit a fact or carry wear is fitted; geometry that is texture comes from a library. Most hand-made pieces sit between: a split slab or a rubble face stone is shaped by the mason, so it should come from a large library (dozens, not three) fitted by a small stretch, with only the worn ones unique. Which instances are drawn instanced and which merged is the performance study's call; the part definition only has to make both possible.

#### Town metrics in one place

A `metrics` table per setting pack, with years, read by every kind. It holds storey heights by era, opening sizes by era and use, door widths, step rise and going, and kerb heights by year (5, 8 and 12 inches). It also holds wall and board thicknesses, plinth heights and the grid the resolver snaps to. Kronenberger's and Bethesda's first rule, with dates on it. The skill's 1 m module and 3 m storey go; the pack's metrics replace them.

#### Dated cells and sockets

As section 5 says: every cell and socket a dated record (an opening with its year and cause, and its fills over time), nothing deleted by a later event, every removal leaving what its part says it leaves. A plan for a year is the records read up to that year, which is what `resolve()` already does with events.

#### A one-dimensional grammar

One small library for everything laid along a line: start, fill and end modules, corner pieces, fallbacks when the run is too short, a fit rule (stretch the fills, or cut the last one, or add a closer). PCG's `<A,B,C>` is the model. It serves kerbs, copings, gutters and downpipes, eaves and barge boards, belt courses, railings, handrails and fences, quay edges, and courses of setts along a gutter.

## 7. How each kind should be assembled

| Kind (from `docs/systems.md`) | Layout | Parts | Repetition allowed | Notes |
| --- | --- | --- | --- | --- |
| Stairs (block, tread on riser, step-ramp) | the mason's set-out (`step_plan`): rise from the stone, going from the stride, landings | slabs fitted and worn; cheek walls as walls | none for treads; joints' fills from a library | keep as now, split into stages; the near tier unique, merged per flight |
| Dry-stone walls and copings | courses laid along the wall's line, joints bridged, biggest stones low, battered | face stones from a large library per size class, fitted by stretch; copings as slabs; end and corner stones fitted | face stones may repeat beyond a few metres apart, turned and mirrored | rebuilt panels as their own run with their own stock and pointing |
| Setts and flag gutters, paving | a pattern rule on a field: rows, arcs, fans, binding courses, cut pieces at the edges | setts from a library of about 16 to 32 per stone and size (manufactured by hand, cut to a standard) | yes, with turn and flip; wear and polish per instance and from the feet field | far tiers become a painted surface; trench strips and patches as their own fields |
| Kerbs | one-dimensional grammar along the kerb line | straight lengths by era width, radius pieces, dropped kerbs, closers | yes (dressed to size) | the dropped kerb is a dated work |
| Plinths | courses along the house's foot, stepping with the ground | stones or render panels by era | as walls | read the house's diary and the terrain |
| Quay walls and steps | courses along the edge; steps as stairs | dressed blocks from a library; the tide band from the water field | yes for dressed blocks | concrete toes as a dated work; the corner where two eras meet fitted |
| Bedrock, cliffs, boulders | from the terrain and the land's facts; rules on slope and exposure | a few sculpted hero rocks; a library of chunks for scree and cliff faces | yes for chunks | nature's, not a kit; Far Cry 5's cliffs from masks |
| Buildings | the resolver: massing, the façade grammar with a separate ground floor, the control layer of big decisions, dated cells | walls and roofs generated (fitted); cladding boards fitted to lines; windows, doors, shopfronts, brackets as fixed families with stretch zones; trims as profiles swept along edges | fixed parts repeat within an era, as they did from a joinery's catalogue | roofs by straight skeleton where footprints are irregular; heroes are corner houses built by the same generator with pins |
| Building parts (gutters, downpipes, chimneys, stoops, signs) | sockets on the plan; one-dimensional grammar for gutters, eaves and downpipes; stoops as the stairs kind | fixed families by era | yes | signs are records: their text from facts, their panel fitted to the band |
| Street things (lamps, posts, railings, fences, benches, bins, kiosks, wires, covers, bollards) | rules along ways and at doors and junctions (Wildlands-style packing with priorities); linear things by the one-dimensional grammar; wires as catenaries between their poles | fixed hero props by era, two or three variants each | yes, as manufactured | clutter repeats are noticed sooner than architecture, so props carry more variants and per-instance age |
| The underground's traces | covers and trench strips along each utility's route and years | covers by foundry and era (fixed) | yes | strips as fields on the paving, not kit pieces |
| Land | contours and the town system | none | n/a | quay edges as geometry, not a stepped ground mesh |
| Trees, ground cover, heath | growth timelines; fields and viability (`docs/research/vegetation.md`) | painted parts and clumps, instanced | clumps yes, trunks no | already built for birches |
| Moving and alive (people, boats, vehicles) | from the engine's people and goods | base bodies and clothing by era as kits; boats and vehicles as fixed models per era with owner's paint and wear | yes for models, never for owners' marks | people are plan step 5 |
| Interiors | allocation inside the openings history fixed; rooms by priority and score | shells fitted; furniture by era and household as fixed families placed by rules (big first, then what goes beside it) | yes, as bought furniture | interior mapping from the plan's room per window, until a scene needs real rooms |
| The region | far-tier masses and impostors per town | per-town simplified kits | yes | plan step 10 |

## What we should do

Ranked by what it buys before the houses. Costs are working days on Opus unless noted, for the framework only; each part still costs its own making and review.

1. Split the stone generator into the pipeline's stages, with a plan for stone, and build the plan hasher. Move `stone.lay` into layout, life, geometry, bake and export, and give the flight a hashed plan; then the walls the same way. Build the hasher for house and stone plans alike (the first tool in `docs/research/tools-and-performance.md`). Cost: about 4 days, plus a check that the gully's geometry is unchanged (Sonnet can run it). Quality: tiers from one decision; a cheap years sheet; the why-probe. Speed: the next stone kinds (landing setts, kerb, plinth) become a layout rule and parts, not a new generator.
2. Define a kind as data, with one runner, one export and one channel spec. `blender/kinds/`, a registry, a `generate(kind, thing, year, tier)` entry point, one `channels.py` that both Blender and the shaders' comments follow, one FBX and manifest writer. Cost: about 2 days. Quality: no drift between generator and shader. Speed: a new kind in days.
3. Write the pack's metrics table and the part definitions. Metrics by era in the setting pack; a sidecar per part family (era, sizes, fit modes, stretch, pivot, sockets, removal marks, tiers, variants); a kit validator that checks every part against both and makes its sheet. Cost: about 2 days, then minutes per part. Quality: every part fits every opening of its era. Speed: house parts can be made in parallel against a fixed spec.
4. Make cells and sockets dated records before the first house part. Openings with year and cause, fills as a list, sockets with history and removal marks; `_shop_fitted` stops deleting cells. Cost: about 2 days in the resolver, plus a hash migration for the fixtures. Quality: alterations read true, a stripped shop leaves its scar, restorations come back. Speed: every diary event becomes a fill change, so new event kinds are cheap.
5. Separate the ground floor and add the control layer. The ground floor as its own grammar over the same bays; per building a few big, discrete, correlated decisions read by every cell. Cost: about 2 days. Quality: houses read as one decision each, shops change without disturbing the floors above. Speed: neutral.
6. Decide fixed or fitted per part, and build libraries for the repeated ones. Setts, roof slates and tiles, boards, brackets, wall stones (large libraries), window families. Cost: about a day per family to convert, more for the first. Quality: reviewed, finite sets; the near tier keeps what is worn unique. Speed: generation and export time fall sharply (to be measured by the performance study, which also decides instancing against merging).
7. Build the one-dimensional grammar. Start, fill, end, corner and fallback modules along a line, with fit rules. Cost: 1 to 2 days. Quality: clean ends and corners everywhere linear. Speed: kerbs, copings, gutters, railings, fences and quay edges become rules over parts.
8. Curation that survives rebuilds. Pins as facts with semantic anchors and their own provenance, re-checked on rebuild; deterministic reseeding on a failed check, recorded; a stress test per kind; expressive-range plots with one fact metric and one visible metric; counts per tier per kind. Cost: about 2 days. Quality: strict reviews can ask for "this one" without hand placement. Speed: fewer review rounds.
9. Make the house's hero by the generator. House A built from its diary with pins, judged as the hero; then a variety sheet of twelve houses from the same parts and fresh diaries; then the other four corner houses. Cost: part of plan step 2. Quality: the generator and the hero cannot drift apart. Speed: the twelve come nearly free.
10. Reserve the interior seam. The plan carries a room per window (floor, kind, lit, household); interior mapping later reads it. Cost: half a day. Quality: lit windows, mapped rooms and scenes agree. Speed: saves a migration at plan step 8.
11. Add the free libraries we need, when we need them. A straight skeleton for irregular roofs (`bpypolyskel`, licence to check), meshoptimizer or Blender's Decimate and Unity's Mesh LOD for detail levels. Cost: a day each, with a check of licences. Quality: reliable roofs; tiers without hand work.
12. Update the `blender-generators` skill to match practice (not done here, by instruction): parts as fixed or fitted, scripted and shaped by eye on a sheet, the pack's metrics instead of the 1 m module, grain textures beside the palette. Cost: an hour.

## For Øystein to decide

1. Where repetition is allowed. Proposed: things (a flight, a wall, a house) never repeat unless their facts say so (one builder's row). Manufactured pieces (setts, dressed kerbs, factory windows, slates, Eternit sheets, lamps) repeat from small libraries, as they do in life. Hand-made pieces (split slabs, rubble stones, hand-cut boards) come from large libraries and are fitted. Only what wear has shaped is unique. This reads his "no two stairs alike unless manufactured like that" as a rule.
2. How parts are made. Proposed: scripted part functions shaped by eye on a quick sheet, as the stone and trees are made now, with the same review gate; hand modelling through the MCP where a form resists code (a carved bracket, a sculpted rock). The skill says the opposite today.
3. No Houdini. Apprentice cannot be used commercially and Indie is paid; Blender, Python and numpy are our Houdini. To confirm.
4. Interiors in three tiers. Interior mapping behind every window, a shallow room where the street stop looks in, full rooms only where a scene goes. To confirm before plan step 8; the plan's room-per-window seam is needed either way.

## Gaps

- Many primary talks are video only or members-only and were not read: Santiago's and Ruskin's Spider-Man talks (GDC 2019), Carrier's Far Cry 5 talk (read through notes), Stålberg's Bad North and Townscaper talks, Compton's GDC 2017 talk, Niepokólczycki's Night City and Beauclair talks. How Spider-Man's buildings were assembled is not known to us.
- Müller and colleagues' 2006 CGA paper and Wonka's 2003 paper were too large to open; snap lines, the control grammar's details and the Pompeii rule count rest on secondary accounts and memory.
- Bethesda's slides 101 to 274 of the Fallout 4 deck were not read; precombines and material swaps are described from secondary accounts.
- No developer source for Red Dead Redemption 2, Kingdom Come: Deliverance, Naughty Dog's streets (vertex-blended kit pieces are widely described but unconfirmed), Ghost of Tsushima, Hogwarts Legacy or Assassin's Creed Valhalla's settlement. City Sample's counts are from memory.
- Licences of `bpypolyskel` and any meshoptimizer wrapper are unchecked.
- Our own numbers are missing: time per kind today, triangles and unique meshes per part per tier, export time per thing. The performance study and the first kind moved into the pipeline should measure them.
- Web search ran out partway through this study; the last sources were reached through known URLs and site listings.

## Sources

Kits and their makers: [Burgess and Purkeypile, Skyrim's modular level design, GDC 2013 (slides)](https://www.slideshare.net/slideshow/gdc2013-kit-buildingfinal/17728576) · [Burgess, Skyrim's modular approach (article)](https://www.gamedeveloper.com/design/skyrim-s-modular-approach-to-level-design) · [Burgess and Purkeypile, Fallout 4's modular level design, GDC 2016 (slides)](https://www.slideshare.net/slideshow/gdc-2016-modular-level-design-of-fallout-4/59770460) · [GDC Vault: Fallout 4's modular level design](https://www.gdcvault.com/play/1023202/-Fallout-4-s-Modular) · [Fallout 4 modular design, Russian transcript (secondary)](https://dtf.ru/id31295/3788796-modulnyi-dizain-fallout-4) · [PC Games on Bethesda's kits (secondary)](https://www.pcgames.de/Spiele-Entwicklung-Thema-35261/Specials/So-entstehen-Skyrim-Fallout-und-Co-Das-modulare-Level-Design-von-Bethesda-erklaert-Teil-2-1067744/) · [Burgess, Iterative level design process, GDC 2014](https://www.slideshare.net/slideshow/3-10gdc2014-iterativeleveldesignprocess/34994256) · [The Level Design Book: modular kits](https://book.leveldesignbook.com/process/blockout/metrics/modular) · [UESP: Daggerfall locations](https://en.uesp.net/wiki/Daggerfall:Locations) · [UESP: BLOCKS.BSA](https://en.uesp.net/wiki/Daggerfall_Mod:BLOCKS.BSA) · [Daggerfall Unity: climate swaps](https://raw.githubusercontent.com/Interkarma/daggerfall-unity/master/Assets/Scripts/Utility/ClimateSwaps.cs) · [Kronenberger, Balancing modularity and uniqueness](https://www.beyondextent.com/articles/balancing-modularity-and-uniqueness-in-environment-art) · [Klevestav, Working with modular sets](http://www.philipk.net/tutorials/modular_sets/modular_sets.html) · [Sanchez, Texturing for believable storytelling](https://www.beyondextent.com/articles/texturing-for-believable-storytelling) · [Oprisan, Recreating historical environments](https://www.beyondextent.com/articles/recreating-historical-environments) · [Burns, Trim sheets](https://www.beyondextent.com/deep-dives/trimsheets) · [Olsen, The Ultimate Trim, GDC 2015](https://www.gdcvault.com/play/1022323/The-Ultimate-Trim-Texturing-Techniques) · [Schreibt, Cyberpunk's broken edges](https://simonschreibt.de/gat/cyberpunk-broken-edges/) · [Schreibt, Fallout 3 edges](https://simonschreibt.de/gat/fallout-3-edges/) · [Starfield's procedural generation (secondary)](https://exputer.com/features/starfield-procedural-generation-improvement/)

Shipped cities: [Insomniac on Spider-Man's tech (PlayStation Blog)](https://blog.playstation.com/2018/09/06/insomniac-interview-the-tech-behind-marvels-spider-man/) · [Santiago, Procedurally crafting Manhattan, GDC 2019](https://www.gdcvault.com/play/1026415/Procedurally-Crafting-Manhattan-for-Marvel) · [Ruskin, Spider-Man technical postmortem, GDC 2019](https://gdcvault.com/play/1026496/-Marvel-s-Spider-Man) · [Santiago, Procedural tool development for Spider-Man 2, GDC 2024](https://www.gdcvault.com/play/1034803/Technical-Artist-Summit-Procedural-Tool) · [Epic: City Sample](https://dev.epicgames.com/documentation/en-us/unreal-engine/city-sample-project-unreal-engine-demonstration) · [Epic: City Sample with Houdini](https://dev.epicgames.com/documentation/unreal-engine/city-sample-quick-start-for-generating-a-city-and-freeway-using-houdini) · [SideFX: The Matrix Awakens, generating a world](https://www.sidefx.com/learn/talks/the-matrix-awakens-generating-a-world/) · [Procedural technology in Ghost Recon Wildlands (80.lv)](https://80.lv/articles/procedural-technology-in-ghost-recon-wildlands) · [Procedural world building in Ghost Recon Wildlands (80.lv)](https://80.lv/articles/procedural-world-building-in-ghost-recon-wildlands/) · [Ubisoft on Wildlands' team](https://news.ubisoft.com/en-us/article/6llB99m1ShnsCf6GVSY5bp/ghost-recon-wildlands-how-to-keep-creativity-alive-on-a-massive-team) · [Carrier, Procedural world generation of Far Cry 5, GDC 2018](https://www.gdcvault.com/play/1025557/Procedural-World-Generation-of-Far) · [Notes on the Far Cry 5 talk (secondary)](https://christianjmills.com/posts/procedural-tools-far-cry-5-notes/) · [Guerrilla: GPU-based procedural placement](https://www.guerrilla-games.com/read/gpu-based-procedural-placement-in-horizon-zero-dawn) · [Horizon Zero Dawn team interview (80.lv)](https://80.lv/articles/horizon-zero-dawn-interview-with-the-team) · [Haar and Aaltonen, GPU-driven rendering pipelines, SIGGRAPH 2015](http://advances.realtimerendering.com/s2015/aaltonenhaar_siggraph2015_combined_final_footer_220dpi.pdf) · [Böhm, Building Manhattan for The Division (80.lv)](https://80.lv/articles/division-pt-1) · [Optimisation of content and levels in The Division (80.lv)](https://80.lv/articles/optimisation-of-content-and-levels-in-the-division) · [How Night City was built almost entirely by hand (80.lv)](https://80.lv/articles/interview-how-cyberpunk-2077-s-night-city-was-built-almost-entirely-by-hand/) · [Niepokólczycki, Building Night City, GDC 2022](https://gdcvault.com/play/1027571/Art-Direction-Summit-Building-Night) · [Tremblay, Building Night City: the technology, GDC 2023](https://www.gdcvault.com/play/1028981/Building-Night-City-The-Technology) · [World building of Witcher 3 (80.lv)](https://80.lv/articles/world-building-of-witcher-3/) · [Vice on Dishonored 2's world design](https://www.vice.com/en/article/dishonored-2-world-design/) · [Modular design in Dishonored 2 (80.lv)](https://80.lv/articles/modular-design-in-dishonored-2) · [Dylla, Frischer, Müller, Ulmer and Haegler, Rome Reborn 2.0, CAA 2009](http://proceedings.caaconference.org/files/2009/09_Dylla_et_al_CAA2009.pdf) · [Anno 1800: residential tiers](https://www.anno-union.com/devblog-residential-tiers/) · [Anno 1800: of 3D architects](https://www.anno-union.com/devblog-of-3d-architects-and-construction-workers/) · [Minecraft wiki: jigsaw block](https://minecraft.wiki/w/Jigsaw_Block) · [Minecraft wiki: processor list](https://minecraft.wiki/w/Processor_list) · [Minecraft wiki: zombie village](https://minecraft.wiki/w/Zombie_village) · [Cities: Skylines zoning](https://skylines.paradoxwikis.com/Zoning) · [Level design lessons from Deus Ex: Mankind Divided's Prague](https://www.gamedeveloper.com/design/level-design-lessons-learned-building-i-deus-ex-mankind-divided-i-s-prague) · [Building the Big Easy for Mafia III (Game Informer)](https://www.gameinformer.com/b/features/archive/2015/10/09/building-the-big-easy-how-hangar-13-reconstructed-new-orleans-for-mafia-iii.aspx)

Methods: [CityEngine CGA: split](https://doc.arcgis.com/en/cityengine/latest/cga/cga-split.htm) · [comp](https://doc.arcgis.com/en/cityengine/latest/cga/cga-comp.htm) · [setback](https://doc.arcgis.com/en/cityengine/latest/cga/cga-setback.htm) · [inside](https://doc.arcgis.com/en/cityengine/latest/cga/cga-inside-function.htm) · [context queries](https://doc.arcgis.com/en/cityengine/latest/cga/cga-context-queries.htm) · [Müller et al. 2006, Procedural modeling of buildings](https://history.siggraph.org/?p=113547) · [Wonka et al. 2003, Instant Architecture](https://www.cg.tuwien.ac.at/research/publications/2003/Wonka-2003-Ins/) · [Schwarz and Müller 2015, CGA++](https://history.siggraph.org/?p=112748) · [Lipp, Wonka and Wimmer 2008, Interactive visual editing of grammars](https://www.cg.tuwien.ac.at/research/publications/2008/LIPP-2008-IEV/LIPP-2008-IEV-paper.pdf) · [Lipp et al. 2011, Layers of procedural content](https://www.cg.tuwien.ac.at/research/publications/2011/lipp2011a/lipp2011a-draft.pdf) · [Unreal PCG shape grammar](https://dev.epicgames.com/documentation/en-us/unreal-engine/using-shape-grammar-with-pcg-in-unreal-engine) · [Gumin, WaveFunctionCollapse](https://github.com/mxgmn/WaveFunctionCollapse) · [Merrell, model synthesis](https://paulmerrell.org/model-synthesis/) · [Merrell and Manocha, IEEE TVCG](https://paulmerrell.org/wp-content/uploads/2021/06/tvcg.pdf) · [Boris the Brave, WFC explained](https://www.boristhebrave.com/2020/04/13/wave-function-collapse-explained/) · [WFC tips and tricks](https://www.boristhebrave.com/2020/02/08/wave-function-collapse-tips-and-tricks/) · [Editable WFC](https://www.boristhebrave.com/2022/04/25/editable-wfc/) · [Constraint-based tile generators](https://www.boristhebrave.com/2021/10/31/constraint-based-tile-generators/) · [Quarter-tile autotiling](https://www.boristhebrave.com/2023/05/31/quarter-tile-autotiling/) · [How Townscaper works (Game Developer)](https://www.gamedeveloper.com/game-platforms/how-townscaper-works-a-story-four-games-in-the-making) · [Tiny Glade dev diaries (Steam)](https://api.steampowered.com/ISteamNews/GetNewsForApp/v2/?appid=2198150) · [Tiny Glade developers on proceduralism (80.lv)](https://80.lv/articles/exclusive-tiny-glade-developers-discuss-bevy-proceduralism-publishers-cozy-games/) · [Tiny Glade's windows (80.lv)](https://80.lv/articles/procedural-windows-in-pounce-light-s-tiny-glade-get-an-upgrade) · [Watabou, Medieval Fantasy City Generator](https://watabou.itch.io/medieval-fantasy-city-generator) · [Watabou, Dwellings](https://watabou.itch.io/dwellings) · [bpypolyskel](https://github.com/prochitecture/bpypolyskel) · [bpypolyskel announcement (OSArch)](https://community.osarch.org/discussion/423/) · [Buildify (CG Channel)](https://www.cgchannel.com/2022/07/download-free-blender-3d-building-generator-buildify/) · [SideFX: Apprentice FAQ](https://sidefx.com/faq/apprentice) · [SideFX: Indie restrictions](https://sidefx.com/faq/question/indie-restrictions)

Quality and interiors: [Compton, So you want to build a generator](http://galaxykate0.tumblr.com/post/139774965871/so-you-want-to-build-a-generator) · [Compton's GDC talk reported (Game Developer)](https://gamedeveloper.com/design/practical-procedural-generation-for-everyone-) · [Boris the Brave, Oatmeal spice](https://www.boristhebrave.com/2026/07/05/oatmeal-spice/) · [Smith and Whitehead 2010](https://users.soe.ucsc.edu/~ejw/papers/smith-pcg-2010.pdf) · [PCG book, chapter 12](http://pcgbook.com/chapter12.pdf) · [Shadows of Doubt devblog 13](https://colepowered.com/shadows-of-doubt-devblog-13-creating-procedural-interiors/) · [Merrell, Schkufza and Koltun 2010](https://paulmerrell.org/wp-content/uploads/2021/06/floorplan-final.pdf) · [van Dongen 2008, Interior mapping](https://www.proun-game.com/Oogst3D/CODING/InteriorMapping/InteriorMapping.pdf)
