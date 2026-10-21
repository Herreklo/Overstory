# Collision and navigation

How people and the camera move through a steep town that changes. It covers how people find their way, where they walk on a lane, where their feet land, and what stops the camera. This closes gap 6 of the decision register (`building-blocks-inputs.md`) and is one of the four studies step 1g waits for (`docs/plan.md`). The study follows `where-generation-runs.md` for where things run and `animation-and-motion.md` for bodies and feet.

Claims are marked as in the other studies. (primary) is a maker's own talk, paper, docs or code, and (secondary) a report, forum or summary. (unverified) means no source confirmed it; (ours) is our own arithmetic and reading. Costs are Opus working days. Written on Opus 5.5 in October 2026, with two helper passes. The shared web-search budget ran out before the end, and GDC Vault was down (Gaps).

## The answer in short

- People walk a graph of the town's ways, built from the record. There is no baked navigation mesh for them. The ways already exist as data (`heart_layout.py`) and are checked (`reach_check.py`). Routes are known hours ahead, because the engine decides where people go and the day plans put them in time. Cities: Skylines 2 and Unreal's City Sample also move people on lane networks.
- On a way, a person keeps to a line drawn from the function that wears the stone (`wear.walking` with the flight's lean). So the worn line and the people on it agree by construction.
- Positions are functions of the plan and the clock. Waiting at a narrow flight is settled when the day is planned. Passing is a sideways shift computed from the neighbours' planned positions at that moment. A jump to any hour or year shows the same people in the same places, with nothing simulated in between.
- Feet are planned onto treads from each flight's tread table, never found by a ray. A foot's height at a date is the tread's top minus its hollow, read from the closed form `wear.py` already uses.
- Collision serves the camera and any avatar, never the people. It is made of simple proxies generated from the plan: ramps over the nosings, boxes for walls and house volumes, a coarse mesh for the ground. A hollow of a few millimetres never reaches a collider.
- Navigation and collision are a stage of the C# pipeline, hashed like the others. Every element carries the years it is valid, so a jump of years is a filter. A discrete change patches the graph's edges and rebuilds the proxies of the one thing it touches.
- Unity's AI Navigation package is not used for people. Its agents step with the frame rate, its bakes may differ between machines, and its stair height data doesn't survive a local rebuild.
- For 1g: the graph, the movers, the proxies and four tests on the clay corner, about 5 to 7 days (ours).

## Where we stand

Checked on branch `lt/1-harbour-street`:

- Ways are data. `heart_layout.LANES` holds every lane, stair, quay, passage, bridge and road as a polyline with heights, a width and a kind. `reach_check.py` checks that every door lies within 3 m of a way, that nothing stands in a way, and that the network is one piece from Harbour Row.
- Stairs know their steps. `stone.py` sets each flight out by Blondel's stride: two rises and a going make about 0.63 m. It caps the rise at 0.20 m and keeps the going at 0.26 m or more. Gentle runs become step-ramps of one or two strides, and a flight too steep to climb is refused. Its sidecar JSON holds each flight's ends, width, rise, going and step fronts. It doesn't hold each tread's real top after settling.
- Wear knows where people walk. `wear.walking` gives the share of feet across a way. Under 1.8 m people walk single file down the middle. Wider flights get two lines, shifted by the flight's lean (a rail, a wall, the door it leads to). Footfall is one number a year per flight, authored by rule (`stair_facts.py`) until engine request 16.
- The clay stairs are boxes with risers of about 0.17 m (`heart_build.py`). Collision in Unity is borrowed: `LT1Trees.cs` adds mesh colliders to the clay for its rays and then removes them. Neither the AI Navigation package nor Cinemachine is installed.
- Picking is designed on the GPU: ids rendered round the cursor, not raycasts (`interface-and-inspection.md`).
- The register's open worry: a worn tread that the vertex shader moves by the date would need its collider to read the same date (`building-blocks-inputs.md`, section 5).

## 1. How games move people through towns

### Games

| Game | How people find their way | For us |
| --- | --- | --- |
| Hitman: Absolution | crowds of about 1,200 agents, about 500 on screen at 30 fps on the last console generation (secondary). A grid of cells over the navmesh answers neighbour and wall queries; panic flows are precomputed per exit; avoidance is mostly by speed, since the walk was driven by animation (secondary, from notes on the GDC 2012 talk; the slides would not open) | a crowd moving on precomputed data, steered by speed |
| Hitman (2016) and Hitman 2 | over 300 behaviour-tree people per level on top of the crowd; named people keep authored routines tied to places, which must stay predictable (secondary) | a routine is a promise to the player |
| Assassin's Creed Unity | about 10,000 crowd figures, with 40 full AIs and 120 detailed bodies swapped in unseen (secondary, the talk's abstract read through search). Beyond 40 m figures barely act; within 12 m they have full behaviour (secondary) | movement detail by distance |
| Watch Dogs: Legion | people exist as bodies only in a bubble round the player. Outside it each is a point moving over the map, as data. Schedules come from generated activities with their places (secondary, a report of the GDC 2021 talk) | our city tier: a position on a path at a time |
| Shadows of Doubt | each citizen's day is planned before it starts, four to ten journeys; the city of hundreds is planned in 10 to 15 seconds; only a handful are re-routed live (the developer's blog, as cited in `behaviour-on-screen.md`; not reread here) | plan routes with the day, not each frame |
| Cities: Skylines 2 | routes on the road and lane network, costed by time, comfort, money and behaviour and weighted by age: teens weigh money, adults time, seniors comfort. Agents re-route when a lane is blocked. The first game chose destinations by straight-line distance (primary, the developer's diary) | costs by capability; destinations from the engine |
| The Sims | an object advertises its use and owns a routing slot. To shower, a Sim first goes to the front of the shower, facing it; if that spot is blocked, the action fails and the Sim moves on (primary, Forbus and Wright). The Sims 4's objects carry routing footprints (secondary) | stand and sit points with a facing, and a defined failure |
| Red Dead Redemption 2 | townspeople keep fixed clock times: work in the morning, the bar at night, home after midnight (secondary, player observation; nothing from Rockstar found) | a schedule reads as a life when it is kept |
| Kingdom Come: Deliverance II | about 2,400 persistent people on daily schedules, about half of them in one city; the costs were performance and heavy hand placement (primary abstract) | hand placement doesn't scale; ours comes from data |
| Manor Lords | no evidence that feet wear paths. Players complain of villagers cutting through yards and fields and fence them out with no-walking zones (secondary, a Steam thread) | who may cross a yard is a fact |
| Unreal's City Sample | crowds and traffic follow ZoneGraph lanes: light corridors with tags, generated from the procedural city's data. Near people are full characters, far ones baked meshes (primary) | the closest shipped match to a graph of ways |

What they share:

- Big crowds are data moving on precomputed structure: cells, flows, lanes, points on a map. Full navigation is kept for the few near the player.
- Routines are planned ahead and kept. Players read a broken routine as a story, so a changed route needs a cause.
- Objects say how they are used: where to stand, which way to face, what happens when the spot is taken.
- No game publishes routes made from a dated record. Rebaking a navigation mesh because a stair was repaired is a problem no one shows a solution for.

### Tools

| Tool | What it gives | Limits for us |
| --- | --- | --- |
| Unity AI Navigation 2 | a NavMeshSurface baked from meshes or colliders; links; area costs; obstacles; agents with RVO avoidance; async updates that rebuild only the tiles whose sources changed (primary) | agents update once a frame in the player loop, so movement follows the frame rate (secondary). Unity warns a navmesh may bake differently on another processor architecture (primary). Stairs bake as slopes unless a height mesh is built, and a local update with `preserveTilesOutsideBounds` deletes the height mesh (primary). Carving is expensive and meant for blockers that stand still (primary). Measured updates: 4.5 ms for one box added, about 50 ms for a 250 m square of terrain with ten boxes (secondary, a 2.3 GHz Intel); stalls on the main thread reported (secondary) |
| Recast and Detour | voxels, regions, polygons, in tiles. The TileCache rebuilds one tile per update call, so a change spreads over frames; its obstacles are cylinders and boxes and can only remove ground (primary). DetourCrowd suggests starting at about 25 agents for 0.5 ms a frame (primary) | nothing said about determinism (unverified); C++ under zlib, so a native plugin or a port |
| A* Pathfinding Project | recast graphs in tiles, updates partly off the main thread, pathfinding mostly in integers and said to be deterministic (secondary, the author's answers) | navmesh cutting is in the paid version, and we have no budget for paid tools |
| Flow fields (Supreme Commander 2) | 1 m cells in 10 m sectors joined by portals; one field serves every agent heading to one goal; 50 to 70% of the walkable space was clear, and clear sectors share one field; changed sectors rebuild in fixed time slices (primary, Emerson in Game AI Pro) | flat: overlapping levels were left as future work, and our town stacks ways (a passage under a house, the footbridge over the Cut) |
| ORCA (RVO2) | each agent takes half the duty of avoiding the other; 5,000 agents in 8 ms on eight cores (primary) | can deadlock when packed tight; it steps through time, so a position is not a function of the clock |
| Unreal ZoneGraph | lanes as shapes with tags, followed point by point (primary) | Unreal only; we take the pattern |

## 2. Stairs, steps and steep ground

### Feet on treads

The animation study cites Burdka and Rohleder (Techland, 2017) for the sunk foot and the hovering one. The paper's title is "Applied Inverse Kinematics for Bipedal Characters Moving on the Diverse Terrain". For a standing foot it traces down under each foot, bends the leg with two-joint IK and lowers the pelvis when a leg can't reach. For a walking foot it predicts the landing point from the speed and from foot-down frames marked by hand (marking them automatically gave poor results). It traces there, reshapes the swing and moves the foot only up or down. The traces cost far more than the IK. The authors blame the character's capsule, a rough fit on stairs, for feet that hover or sink (primary).

Valve's Half-Life: Alyx (SIGGRAPH 2021) analyses each clip's strides offline. At runtime it finds when the next foot lands, moves that far along the path and casts a ray for the landing height; the planted foot is the IK target. Its motion matching samples the future by distance, not time, and changes clip only while a foot is down (primary). Perlin's patent (2005) nudges the walk's phase a little at each key so every footfall moves to the middle of a step. The nudge starts two keys ahead, and the pelvis follows a blurred height field (primary).

All three find the ground by tracing. We know it already: a flight is a record with every tread in it. The trace becomes a lookup, so the dearest part of Burdka's method goes. Perlin's nudge becomes exact, since each footfall's tread is known before the flight starts.

### Step limits and stairs as ramps

- Our steps: risers up to 0.20 m and goings from 0.26 m, so the steepest built flight is about 35 to 38 degrees (ours, from `stone.py`'s rules). The gully, at 0.17 m rises and goings of about 0.29 m, is about 30 degrees (ours). Step-ramps have goings of one or two strides (0.65 or 1.3 m) and low risers.
- Engines: Unity's guidance for its CharacterController is a step offset of 0.1 to 0.4 m for a 2 m person (primary). Unreal's default step height is reported as 45 cm (unverified). One guide sets it 2 cm above the riser to stop a stop-go stutter on stairs (secondary).
- Stairs as ramps: Catlike Coding collides a stair with a ramp cut through the middle of its steps, on a layer only movers see, while a detailed layer catches debris. It allows steeper slopes on stairs (50 degrees) than on ground (25) (secondary). That this is common practice in shipped games is unverified here; Burdka's capsule problem is the reason it is needed.

### Speeds and passing on flights

| Source | Finding |
| --- | --- |
| Goyal, Kahali and Rastogi 2019 (Delhi metro stairs, up to 17,647 people a site) | 0.78 to 0.94 m/s on stairs against 1.08 to 1.55 m/s on the level; down is faster than up; women about 15% slower; small children at 50 to 55% of a young adult's speed (primary) |
| Fujiyama and Tyler 2004, in Goyal's table | UK stairs: 0.54 m/s up, 0.61 m/s down (primary table) |
| Kretz 2008, in Goyal's table | people climb short stairs about twice as fast as long ones (secondary) |
| Fujiyama and Tyler 2009 | people detour at the foot of a flight to avoid someone already on it; most keep right on right-handed stairs; followers move aside when close (primary abstract) |
| Liu, Lu and Oeda 2024 | narrow stairs form an up lane and a down lane; a stronger keep-right habit sharply cuts deadlock; shoulders 0.37 to 0.40 m wide; personal space at least 0.20 m (primary) |
| SFPE, via the Pathfinder manual | 0.15 m kept clear at each side; a 1 m stair of 178/279 mm steps carries about 0.71 people a second (secondary) |

What follows for us (ours):

- Two people pass where a way has about 1.3 m clear: two shoulders of 0.40 m, 0.20 m between them and 0.15 m at each side. One fits in about 0.7 m. The heart's narrowest ways are the passages at 1.6 m, so two pass there with shoulders turned. A scaffold or two café chairs can close that.
- The gully's 50,000 feet a year are about 137 a day. Its 3.2 m would carry about 2.3 people a second. If a fifth of a day's feet came in one hour, that is under 1% of what it holds. Congestion on our stairs is an event (a gig letting out, a funeral), not the daily state.
- So daily life on a stair needs following, waiting and passing. It doesn't need a crowd simulation.

### How games make stairs look right

The craft is the same in all three sources. Footfalls are planned or predicted onto the step, and IK holds the planted foot. The pelvis drops to the lower foot, the swing lifts over the nosing, and the body's height follows a smoothed profile. On a slope Valve scales speed and step height together. Our tiers follow the animation study:

| Tier | On a flight |
| --- | --- |
| Near, to about 20 m | footfalls planned onto treads; Two Bone IK on the plant; the pelvis to the lower foot |
| Street, 20 to 80 m | the body's height from the treads; IK on steps only |
| City, 80 to 400 m | a position on the path at the time, its height from the way's polyline |

## 3. Collision for the camera and for people

What needs collision: the free camera of 1g; an avatar, if a game has one; things that are thrown or blown (litter, a ball). People don't. Their routes and footfalls come from data, and the A* project's author warns that a CharacterController or rigidbody on each agent is slow (primary).

Collision uses proxies. Unity ranks collider cost from sphere, capsule and box up to convex and then non-convex meshes (primary). Cooking a mesh collider at runtime can spike the CPU. `Physics.BakeMesh` is thread-safe and runs in jobs, and a collider reuses the bake only when its cooking options match and the mesh hasn't changed (primary). A stair with its walls is about 816,000 triangles today (`NOW.md`); it must never be a collider.

What a generated town carries for collision:

- walkable surfaces: a ramp over each run of a flight, landings, paving, quays, the ground's coarse level;
- step edges: each nosing line, for feet and for a camera at eye level;
- blockers: house volumes, walls, posts, trunks, bollards, kiosks;
- drop edges: quay edges, the tops of retaining walls, parapets, so nothing walks off by mistake;
- openings: doors and passages, left open in the blockers while the record says they are open.

Layers follow Catlike Coding. A walk layer holds ramps, ground and blockers for the avatar and the camera. The real steps sit on a detail layer, for things that bounce, such as a can rolling down. What the camera may not enter goes on a camera layer.

Chunks and distance levels. Physics has one level: distance levels change what is drawn, never what collides. Proxies exist only within a radius of the camera or avatar. They are grouped by thing (a flight, a house, a wall run), so a change to one thing rebuilds only its proxies. The ground uses its 64 m land chunks (D8.3) at the 2 m ring as a static mesh collider. It is cooked offline for the shipped start and baked in a job when a dated land act changes it. Unity's box pruning suits many static colliders, and a big change in the world's bounds forces a costly rebuild of the broadphase (primary). The cost of adding many static colliders at runtime is unmeasured (Gaps).

The worn tread. Hollows are millimetres: 4.6 mm at the gully's busiest point in 1989 (ours, from `wear.depth`). That uses our authored slate rate of 8 mm a century under 100,000 feet a year, itself unverified, and the gully's 50,000 feet a year for 115 years. A ramp over the nosings lies centimetres from the treads anyway. So colliders ignore the date and feet read the hollow. That settles the register's worry.

The camera. Cinemachine 3's Deoccluder keeps a line of sight with rays; its Decollider only pushes the camera out of colliders (primary). Both need the camera layer. A free camera needs one sphere cast a frame. Feel, height and framing belong to `camera-and-composition.md`.

Picking. In 1g, hover and inspect can raycast against the proxies, each carrying its record id and part path. The GPU id path replaces it after the picking spike.

Physics and determinism. Unity's Enhanced Determinism holds only when actors are inserted in a deterministic order (primary). Proxies are inserted sorted by stable id.

## 4. Change at runtime

What the tools do:

- Unity's `UpdateNavMeshDataAsync` hashes its sources and rebuilds what changed, but needs every source on every call. A second call cancels the first. The local mode drops the height mesh and the generated links (primary). It rebuilds geometry to learn what the record already says.
- Recast's TileCache rebuilds one tile per call, so the cost spreads over frames (primary). Flow fields rebuild dirty sectors in fixed time slices (primary). The lesson: keep each change local and bounded, and spread it.

Ours reads the record. A change in play is already a plan diff (`where-generation-runs.md` §5), and navigation reads the same diff:

| Change | The graph | The proxies | Cost (ours) |
| --- | --- | --- | --- |
| A stair repaired, two slabs reset | the flight's tread table rewritten | the run's ramp, only if a nosing moved beyond tolerance | microseconds |
| A flight closed for works | its edges carry the closed phase | the hoarding as a blocker for that phase | microseconds |
| A shop opens | its door gains opening hours and a stand point; the feet field follows | none | microseconds |
| A house extended | new blockers; a way it narrows gets a new clear width; a new door | the house's proxies | under 1 ms on a worker |
| A building demolished | its doors close at the year; the plot becomes a place only if the record says so (a gravel lot) | removed | under 1 ms |
| Thirty years across a district | the date filter moves; what the engine's run adds is patched in | the changed things inside the radius | the length of the change list, not the town |

Dated validity. Every node and edge carries the years and phases it is valid. The graph at a date is a filter over one structure, as the date is a global for drift. Nothing is rebuilt when only the date moves.

Determinism. Lengths and heights are integer millimetres, costs are integers, and ties break by stable id. A* runs in C# with no floats in its decisions (`where-generation-runs.md` §4, rules 2, 3 and 5). A person's taste in routes is a seeded integer bias from their id (SplitMix64), stable for life. Positions are a function of the schedule and the clock (D10.7). A jump from 1989 to 2020 and back gives the same paths, on any machine.

Avoidance that steps through time (ORCA, Unity's RVO) breaks this. We use it only for dense crowds at events, as scene state, at a fixed tick in id order. A jump places those people from the plan again.

## 5. Where navigation meets the facts

One network has three readers: routes, the feet field and wear. The feet field is the year's trips summed over path segments (request 16; `living-fabric.md`). When routes run on the same graph, the polish lies where people walk because it is counted from the routes they take.

People walk on the polish. Their sideways line is drawn from `wear.walking` with the flight's lean, the function that placed the wear.

The five kinds of thing on screen sort the rest:

| What | Kind | Source |
| --- | --- | --- |
| The trip: who goes from where to where, and when | canonical fact | the engine's habits and events; fixtures until then |
| The route through the ways; the walking speed | visual interpretation | our costs from capability, age, load, weather |
| The sideways offset, gait, stride | texture | the person's seed |
| Who waits at the landing tonight | scene state | the planner's reservations |

A changed route reads as history. Taking the back way round reads as avoiding someone (`behaviour-on-screen.md` §6). So a person's route changes only when the record gives a cause; otherwise the seeded preference holds for life.

Doors and thresholds are dated sockets (D3.1, D10.4). A door fill makes a node with its stand point outside, the facing, the step-up, the swing side and the way it joins. A door covered by a shopfront or blocked up closes the node for that interval. From The Sims: if the stand point is taken, wait or choose another, never stand inside someone.

Access is a fact: Hägerstrand's authority constraint (`behaviour-on-screen.md` §4). Each edge says who may use it and when: everyone; one household (a yard, a house's own passage); customers during opening hours; nobody after the park gate is locked. Manor Lords' villagers crossing yards show what happens without it.

Desire lines. In Helbing's active-walker model the ground keeps a trail value that each step raises and the weather wears back. Walkers lean towards trails they can see. One number, κ, decides between direct paths and a minimal network: a step's intensity times a trail's life, over the square of how far a walker sees. Trails bundle where routes meet (primary). `living-fabric.md` already names it for lawns and heath. In our graph a lawn or heath is a place with portals. A crossing is a straight line until the feet field wears a trail, which becomes an edge with its made year. The trail is a fact because its cause is counted.

## What we should do

### The model

| Layer | What it is | Built from | Rebuilt when |
| --- | --- | --- | --- |
| The way graph | nodes: junctions, landings, doors, sit, stand and lean points, a place's portals. Edges: way segments with kind, length, rise, clear width, surface, access and the years valid | the plan's ways, places, doors, flights and things | an element's plan changes; never when only the date moves |
| Corridors and treads | per edge, the sideways share of feet (`wear.walking` with the lean). Per flight, the tread table: each tread's front line, its top at front and back after settling, going, rise; landings; step-ramps. Per place, its polygon with its things as blockers | the stair and paving functions' own outputs | the flight or place is touched |
| Collision proxies | ramps over flights; tops of landings, paving and quays; boxes for house volumes and walls; capsules for posts and trunks; step and drop edges; the ground at the 2 m ring | each kind's proxy function, or a fixed part's sidecar | the thing changes; a dated land act |

Movers:

- Planning, with the day plan. A* on the graph at the date for the person's capability class. Costs are integers. Time comes from the edge's kind and direction and the speeds above. Comfort adds to it: steps cost more for the old and the laden, and prams and wheelchairs can't take them. Rain makes sheltered edges cheaper (passages, overhangs), and the person's seeded bias goes on top. Edges with under 1.3 m clear get reservations, so two people never meet head on there; one waits at the landing or the end. The result is a timed path, cached by person, day and graph hash.
- Each frame. The position comes from the timed path and the clock. The sideways offset comes from the person's seed and the corridor's share of feet. Passing is a pure function of the neighbours' planned positions at that moment. Groups walk side by side or in a V (animation study).
- Feet. At the near and street tiers, footfalls on a flight are planned onto its treads. A stair takes one per tread and a step-ramp one or two strides per going. The last level steps are nudged so the first footfall lands on the first tread. A foot's height is the tread's top minus the hollow at the date. The swing clears the nosing and the pelvis drops to the lower foot. Off the flights, feet take the ground's height under the path.

Unity's AI Navigation stays uninstalled. If a game later needs people to roam off the ways (children on the knoll), a navmesh over that one place is the fallback, tested then.

### For the greybox (1g)

| Item | What | Cost (ours) |
| --- | --- | --- |
| 1. The graph from the clay | `heart_layout`'s lanes, places and passages; doors from `reach_check`'s door points and the corner's diaries at 1989, 2000, 2010 and 2020; the date filter; integer A* in C#; a debug view | 1 to 1.5 d |
| 2. Movers | trips from fixtures, or from the engine's run (request 36), into timed paths; speeds by age and edge kind; sideways lines, passing, waiting at narrow ways; sitting and standing at sockets | 1.5 to 2 d |
| 3. Blockout bodies on the clay steps | the clay's step table (risers about 0.17 m); the body's height from the treads; feet planned onto them if the blockout has legs | 0.5 to 1 d |
| 4. Collision proxies | house volumes and walls as boxes; flights as ramps; the clay ground as one static mesh collider per 64 m; a camera layer; a record id on every proxy for picking | 0.5 to 1 d |
| 5. Tests 1 to 4 below, on the corner at four years | | 1 d |

About 5 to 7 days in all. It also serves the playtest's tools (`docs/plan.md`, 1g). Exact replays come free, since positions are functions of the plan and the clock. Telemetry can log the camera's path and the proxies it hits.

### Later

1. Plan 3.1, the gully's port. The stairs kind exports its tread table and walking line, and doors their stand points (half a day each; the animation study's item 2). The proxy function, step edges and drop edges join the contract beside them.
2. The grey walker (`inputs/4-people-behaviour-motion.md`): an MPFB body with two clips on the exported treads, which tests the tread contract with real IK.
3. The architecture: navigation as a stage output in C#, its hash in the chain; graph elements as dated sockets and fills (D3.1, D10.4).
4. Step 4 and request 16: the feet field from the graph's routes; trails on lawns and heath by Helbing's model.
5. Step 5: footfall planning with motion matching (Valve's sampling by distance) and IK on treads at the near tier.
6. Step 6 and events: a dense-crowd mover (ORCA in Burst, fixed tick, id order) for event scenes only, measured at 500 and 2,000 people.
7. An avatar, if a game has one. It is a kinematic capsule or a CharacterController on the walk layer. Its step offset is 0.25 m, above the 0.20 m riser cap and inside Unity's guidance. Ramps are allowed to about 40 degrees and natural ground to less. The same footstep planner places its feet.

### What every part and kind carries

| Part or kind | For navigation | For collision |
| --- | --- | --- |
| Every element | record id and part path; the years it is valid; its chunk | the same id on its proxy |
| Ways: lane, steps, passage, quay, bridge, road | centreline in millimetres with heights; width; kind; surface; lean; access; what each side is (wall, drop, kerb, open) | the walk surface; drop edges |
| Flights | the tread table; landings; step-ramps; handrail lines; places to sit on a step; the walking line | one ramp per run over the nosings; landing tops; cheek walls as blockers; nosing lines as step edges |
| Places: the Landing, squares, yards, lawns, heath | polygon; portals; access; things inside as blockers; trails as dated edges | the top surface; the things' blockers |
| Doors | stand point outside; facing; threshold height and step-up; width; swing side and hinge; the way node; hours from the business | an opening in the house's blocker while open |
| Buildings | volumes as blockers; stoops as small flights; passages under them as ways | boxes or convex hulls per volume |
| Walls: yard, retaining, cheek, parapet | blocker lines with height; sit and lean points; a drop edge on the low side | boxes |
| Street things: bench, lamp, bollard, kiosk, stall, bin | footprint as a blocker; sit, lean, stand and serve points with facing | capsule or box |
| Trees | the trunk's circle at the date | a capsule at the date; crowns never collide |
| Ground, by land chunk | walkable by slope class; water as no-go | static mesh at the 2 m ring |
| People | radius from shoulder width; height; leg length; capability class (age, load, stick, pram); gait seed | none, beyond a trigger capsule for picking |
| Fixed parts from Blender | sockets in the sidecar | proxies as primitives in the sidecar, never a mesh |

### Costs on the M4

Estimates (ours), all to be measured by the harness on the built player. For scale: Unity's navmesh took 4.5 ms to update for one small box on an older Intel (secondary).

| Work | Size | Estimate |
| --- | --- | --- |
| The heart's graph | a few thousand nodes | under 1 MB; built from the plan in milliseconds |
| One path | A* over the graph | well under 1 ms |
| A day's paths for the engine run's 119 people | four to ten trips each, 500 to 1,200 paths | under a second on one worker, once per planned day, cached |
| Movers each frame | 300 people in view, with passing | under 0.3 ms on the main thread (target) |
| Footfalls | a near person entering a flight | microseconds: a table lookup |
| The camera | one sphere cast | negligible |
| A change | a graph patch and one thing's proxies | microseconds; under 1 ms on a worker |
| Every tread table in the town | say 200 flights of 30 treads, at about 32 bytes a tread | about 200 KB |

Navigation, movers and camera collision together get 0.5 ms of the 16.7 ms frame.

### Tests

1. Every door is reachable. `reach_check.py` grows into a graph check at every fixture year. Every door that exists that year joins the network from Harbour Row for an adult on foot, and so does every sit and stand point. Every edge keeps at least 0.7 m clear, or it closes and the doors it serves are listed. Doors reached only by steps are reported for prams and wheelchairs as information, not failure.
2. No foot sinks into a tread. The check runs for the blockout walker in 1g and the grey walker later, on every flight of the corner. At each planted frame the sole's lowest point lies within 5 mm of the tread's surface at the date. No footfall lands within 4 cm of a nosing or of the riser above, and each plant slides less than 10 mm. These starting thresholds are ours and tighten with the people step.
3. The paths are the same after a jump. Plan a day in 1989, jump to 2020 and back, then plan it again in a fresh process with the people shuffled: the path hashes match. Positions at 50 sampled moments match to the millimetre whether the clock ran from 08:00 or jumped straight to 14:00. While `reach_check.py` and the C# graph both exist, they agree on what is reachable.
4. Collision agrees with the record. Rays down onto every flight hit its ramp within 3 cm of the nosing line. No proxy fills an open door or a passage. The camera's sphere can't enter a house volume. Every proxy names its record.
5. Cost: the harness logs planning, movers and physics per frame and per change, on the built player at 1440p.

### Decided here

By the evidence above:
- People move on a dated way graph built from the record. No navmesh serves people.
- Positions are functions of the plan and the clock. Passing is a pure function; waiting is planned. Avoidance that steps through time is kept for event crowds, as scene state.
- Feet are planned on tread tables, and a foot reads the hollow at the date. Colliders ignore the date.
- Collision comes from generated proxies per thing, inside a radius; the ground comes by land chunk; ids sit on every proxy; proxies are inserted in id order.
- Navigation and proxies are one C# stage in the hash chain, in integer millimetres, with ties broken by stable id.
- One graph serves routes, the feet field and wear.
- Access, doors and trails are dated facts. A route changes only with a cause.

Left to measurement:
- planner and mover times on the M4;
- the cost of static colliders added in play, and grouping proxies per thing or per streaming cell;
- whether pure-function passing looks natural on the gully from the street stop (a motion sheet);
- the foot thresholds, and whether 1g's blockout bodies need legs at all.

## For Øystein to decide

1. Does the player have a body in 1g? The plan has a free camera. A walk mode could sit beside it as a toggle. It would hold the camera at eye level, follow the ways, step on the treads and stop at drops and walls (1 to 1.5 days, ours). *Recommendation:* add the toggle. The steps are the town's character, and the playtest should feel the climb as well as see it. Camera feel stays with `camera-and-composition.md`.
2. Do people react to the camera? *Recommendation:* no. The camera is a witness (`behaviour-on-screen.md` §7), and people stepping aside for it would say it is there. An avatar, if one comes, is a person, and others yield to it as scene state.

## Gaps

- The shared web-search budget ran out before the study ended. GDC Vault was down, so the Hitman and Assassin's Creed Unity slides went unread, and the ZoneGraph manual page came back empty. Nothing primary was found on The Sims 4's routing or on Red Dead Redemption 2's scenario points.
- No navmesh or PhysX timing on Apple silicon was found. Every timing above comes from Intel machines or unstated hardware. The cost of adding many static colliders at runtime is unmeasured.
- Unity's default humanoid agent (radius 0.5 m, height 2 m, step height 0.75 m, slope 45 degrees) is unverified, and so is whether Recast is deterministic.
- The pedestrian numbers come from metro stations, not wet outdoor stone. Norway's keep-right habit on foot is unverified, and Fruin's table for stairs went unread.
- How people got prams and goods up the old town's steps in 1989 is unstudied.
- Hand-set treads vary in going within a flight. Whether library clips stretch to fit them is for the grey walker to find.
- Roaming off the ways (children on the knoll's rock), boats, ladders and gangways, and footing on ice and wet slate are not designed. Each waits for the step that needs it.

## Sources

Unity navigation: [NavMeshSurface](https://docs.unity3d.com/Packages/com.unity.ai.navigation@2.0/manual/NavMeshSurface.html) · [How navigation works](https://docs.unity3d.com/Packages/com.unity.ai.navigation@2.0/manual/NavInnerWorkings.html) · [Height mesh](https://docs.unity3d.com/Packages/com.unity.ai.navigation@2.0/manual/HeightMesh.html) · [NavMeshAgent](https://docs.unity3d.com/Packages/com.unity.ai.navigation@2.0/manual/NavMeshAgent.html) · [NavMeshLink](https://docs.unity3d.com/Packages/com.unity.ai.navigation@2.0/manual/NavMeshLink.html) · [NavMeshObstacle](https://docs.unity3d.com/Packages/com.unity.ai.navigation@2.0/manual/NavMeshObstacle.html) · [Navigation window](https://docs.unity3d.com/Packages/com.unity.ai.navigation@2.0/manual/NavigationWindow.html) · [UpdateNavMeshDataAsync](https://docs.unity3d.com/6000.0/Documentation/ScriptReference/AI.NavMeshBuilder.UpdateNavMeshDataAsync.html) · [CollectSources](https://docs.unity3d.com/6000.0/Documentation/ScriptReference/AI.NavMeshBuilder.CollectSources.html) · [preserveTilesOutsideBounds](https://docs.unity3d.com/ScriptReference/AI.NavMeshBuildSettings-preserveTilesOutsideBounds.html) · [buildHeightMesh](https://docs.unity3d.com/ScriptReference/AI.NavMeshBuildSettings-buildHeightMesh.html) · [tileSize](https://docs.unity3d.com/ScriptReference/AI.NavMeshBuildSettings-tileSize.html) · [voxelSize](https://docs.unity3d.com/ScriptReference/AI.NavMeshBuildSettings-voxelSize.html) · [Deterministic assets](https://docs.unity3d.com/Manual/build-deterministic-assets.html) · forum timings: [update bug and performance](https://discussions.unity.com/t/updatenavmeshdata-bug-and-performance/828779), [optimising async updates](https://discussions.unity.com/t/optimize-navmesh-using-navmeshbuilder-updatenavmeshdataasync/789438), [main-thread lock](https://discussions.unity.com/t/updatenavmeshdataasync-locking-main-thread/911940), [huge navmesh](https://discussions.unity.com/t/updating-a-huge-navmesh-with-many-build-sources-asynchronously/764343), [agent update timing](https://discussions.unity.com/t/controlling-when-the-navmeshagent-updates/831251), [agent limits](https://discussions.unity.com/t/nav-mesh-components-limitations-and-performance-issues/857674)

Recast and alternatives: [recastnavigation](https://github.com/recastnavigation/recastnavigation) · [rcConfig](https://recastnav.com/structrcConfig.html) · [DetourCrowd](https://recastnav.com/group__crowd.html) · [DetourTileCache source](https://raw.githubusercontent.com/recastnavigation/recastnavigation/main/DetourTileCache/Source/DetourTileCache.cpp) · [large worlds discussion](https://github.com/recastnavigation/recastnavigation/discussions/566) · [A* recast graph](https://arongranberg.com/astar/docs/recastgraph.html) · [A* graph updates](https://arongranberg.com/astar/documentation/stable/graphupdates.html) · [A* optimisation](https://arongranberg.com/astar/docs/optimization.html) · [A* determinism](https://forum.arongranberg.com/t/deterministic-for-multiplayer-rts/10342) · [A* against Unity's bake](https://forum.arongranberg.com/t/generating-navmesh-with-recastgraph-vs-unity/11175) · [Emerson, flow field tiles](http://www.gameaipro.com/GameAIPro/GameAIPro_Chapter23_Crowd_Pathfinding_and_Steering_Using_Flow_Field_Tiles.pdf) · [ORCA paper](https://gamma.cs.unc.edu/ORCA/publications/ORCA.pdf) · [RVO2](https://gamma.cs.unc.edu/RVO2/) · [HPA*](https://webdocs.cs.ualberta.ca/~mmueller/ps/hpastar.pdf) (abstract only) · [Unreal City Sample](https://dev.epicgames.com/documentation/unreal-engine/city-sample-project-unreal-engine-demonstration)

Physics and camera: [collider types](https://docs.unity3d.com/Manual/physics-optimization-cpu-collider-types.html) · [mesh cooking](https://docs.unity3d.com/Manual/physics-optimization-cpu-mesh-cooking-options.html) · [Physics.BakeMesh](https://docs.unity3d.com/6000.0/Documentation/ScriptReference/Physics.BakeMesh.html) · [broadphase](https://docs.unity3d.com/Manual/physics-optimization-cpu-broad-phase.html) · [Physics settings](https://docs.unity3d.com/6000.0/Documentation/Manual/class-PhysicsManager.html) · [CharacterController](https://docs.unity3d.com/6000.0/Documentation/Manual/class-CharacterController.html) · [CinemachineDeoccluder](https://docs.unity3d.com/Packages/com.unity.cinemachine@3.1/manual/CinemachineDeoccluder.html) · [CinemachineDecollider](https://docs.unity3d.com/Packages/com.unity.cinemachine@3.1/manual/CinemachineDecollider.html) · [Catlike Coding, surface contact](https://catlikecoding.com/unity/tutorials/movement/surface-contact/)

Games: [notes on Fauerby, Crowds in Hitman: Absolution](http://ohyecloudy.com/pnotes/archives/gdc12-crowds-in-hitman-absolution/) · [Thompson, the AI of Hitman](https://www.gamedeveloper.com/design/the-ai-of-hitman-2016-) · [Cournoyer, Assassin's Creed Unity's crowd](https://gdcvault.com/play/1022141/Massive-Crowd-on-Assassin-s) (abstract via search) and [a forum summary of its tiers](https://discussions.unity.com/t/how-to-can-i-create-a-crowd-system-in-by-game-similer-to-ac-u/647400) · [Colossal Order on CS2's pathfinding](https://colossalorder.fi/?p=1597) · [Forbus and Wright, Programming Objects in The Sims](https://qrg.northwestern.edu/papers/Files/Programming_Objects_in_The_Sims.pdf) · [4Gamer on Watch Dogs: Legion's Census](https://www.4gamer.net/games/464/G046433/20210726074/) · [Ubisoft on Legion's tools](https://news.ubisoft.com/en-us/article/4po3S9Pwp1YcgBmGPmQxAh/watch-dogs-legion-the-tools-that-built-london) · [KCD II at GDS 2024](https://2024.gdsession.com/index.php?action=kcd) · [Manor Lords players on paths](https://steamcommunity.com/app/1363080/discussions/0/3386168507489829201) · Shadows of Doubt: the sources in `behaviour-on-screen.md`

Stairs and feet: [Burdka and Rohleder 2017](https://mgv.sggw.edu.pl/issue/download/147/90) · [Heuvel, The Right Foot in the Wrong Place (Valve)](https://history.siggraph.org/wp-content/uploads/2022/06/2021-Talks-Heuvel_The-Right-Foot-in-the-Wrong-Place.pdf) · [Perlin, US8243078](https://patents.google.com/patent/US8243078B2/en) · [Unreal step height guide](https://bugnet.io/blog/fix-unreal-physics-character-step-up-stairs-stuttering)

Pedestrians and trails: [Goyal, Kahali and Rastogi 2019](https://www.wctrs-society.com/wp-content/uploads/abstracts/mumbai/WCTR2019_Mumbai_145.pdf) · [Fujiyama and Tyler 2009](https://ideas.repec.org/a/sae/envirb/v36y2009i1p128-148.html) · [Liu, Lu and Oeda 2024](https://pmc.ncbi.nlm.nih.gov/articles/PMC11089042/) · [Pouw et al. 2024](https://arxiv.org/abs/2307.15609) · [SFPE in the Pathfinder manual](https://www.thunderheadeng.com/docs/2026-1/pathfinder/appendices/technical-reference/sfpe) · [Helbing, Keltsch and Molnár 1997](https://ar5iv.labs.arxiv.org/html/cond-mat/9805158)

Ours: `docs/plan.md`, `docs/facts-contract.md`, `docs/living-fabric.md`, `docs/town-plan.md`, `docs/foundations.md`; `where-generation-runs.md`, `animation-and-motion.md`, `behaviour-on-screen.md`, `building-blocks-inputs.md`, `interface-and-inspection.md`, `inputs/4-people-behaviour-motion.md`; `blender/blockouts/heart_layout.py`, `heart_build.py`, `reach_check.py`; `blender/generators/stone.py`, `stair_facts.py`, `wear.py`; `unity/Assets/Code/Editor/LT1Trees.cs`, as checked in October 2026
