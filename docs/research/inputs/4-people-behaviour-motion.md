# Inputs 4: people, behaviour and motion

A digest of `characters.md`, `behaviour-on-screen.md` and `animation-and-motion.md` for the building-blocks architecture (`docs/plan.md`, What the architecture decides). The studies are checked against `CLAUDE.md`, `NOW.md`'s decisions, `docs/living-world.md`, `docs/systems.md`, and `painted-marks-in-motion.md` and `interface-and-inspection.md` where they touch. It decides nothing. Written on Opus.

Pointers: §7.1 is a section of the study named; WWSD is its "What we should do" list; our own readings are marked (our reading). Items 1 to 3 come per study. Items 4 to 6 overlap, so they come once, with the study named on each row.

## 1. characters.md

### In short

- Keep MPFB's machinery (the `hm08` topology, 1,258 targets, MHCLO fitting, a seeded batch, the `game_engine` rig) and replace everything visible (§2, §7.1).
- Identity is numbers, never a mesh: features from parents, pigments, grown height by cohort, a gait seed. A person at a date is identity + Δage(t) + body + hair + wardrobe (§7.1, §7.3).
- Cues by distance: silhouette, outer colour and hair mass far; the head's light pattern at the street stop; the inner face only in scenes (§3).
- A garment is a thing with the living fabric's record, and clothes change at the speed of their records (§7.2, §7.5).
- Style is chosen on unrigged stills of one person at 20, 45 and 70 in three stylisations, then a recognition test scored as d′ (§7.4).

### Against the bar

| Test | Finding |
| --- | --- |
| Primary sources | Strong on perception (Ellis, Toseeb, Rhodes, O'Toole, Simhi & Yovel, Rowland & Perrett), population (SSB, HUNT, Tromsø) and tools: MPFB 2.0.17 checked on this machine (§2). Game craft is mixed; secondary claims are marked, down to its own wear list ("unsourced", §5). |
| Our stack | Concrete for Blender and MPFB. Thinner for Unity: tier budgets are "provisional, to be measured" (§7.1.9), and the assembler's cost is framed "on a mid-range card" (Gaps), not the M4. |
| Thin sections | 1989 dress is broader than the known weak spot suggests: §5 has the 1989 shelves, youth dress, rain gear by date and the economy. Thin: fishing and fish-plant dress (secondary), pensioners and offshore colours (unverified), Stavanger's own scenes. 1980s hairstyles are missing outright (Gaps); §7.1.5 asks for "the era's cut" without naming one. Hair in motion is studied nowhere. |

**Verdict: meets the bar with gaps that change no building-block decision.** The dress and hair gaps change the kit's content, not its data: the garment record, slots, fitting and hair-mass library hold whatever 1989 wore. They must close before the kit (WWSD 5, 6). That pass should look for 1985 to 1990 street photographs in Stavanger byarkiv (Øystein's OK first, `NOW.md`), DigitaltMuseum's dated garments and hair, and industriminne for coveralls. Moving street footage from 1989 would also serve motion "edited against video" (our reading).

### Decisions it proposes

(a) For the building blocks now:

| Decision | Why | Cost | Depends on; note |
| --- | --- | --- | --- |
| A garment is a thing with the fabric's record; its wear and mends use the same history maps as stone (§7.5, §5) | one record and one history system for all made things | none if the schema admits it | the history-map decision |
| The person record holds identity as numbers: appearance seed, parents, features, pigments, grown height, build, gait seed (§7.1.2, §7.5) | 97,000 people across decades cannot ship baked meshes (§7.1.10) | a day: fixtures and a validator (WWSD 1) | engine appearance seed; gait seed's owner contested (C5) |
| Skinned things take an anchor class whose marks read a rest-pose coordinate (§1, §7.1.7) | a world-fixed brush slides on a moving body | in the mark contract | channel layout (Q1) |
| Skinned tiers are separate meshes from one set of targets; only the drawn one is skinned (§7.1.9) | Unity's Mesh LOD "deforms LOD0 regardless" | none; a constraint | distance levels |
| People generated at runtime, cached by a hash of record, age step and outfit (§7.1.10) | the living fabric's cache key | provisional | scale test; "where generation runs" |
| Material records carry a scatter value for the shade function's warm turn and wrap (§7.1.7) | shade stays the light's; deep tones right in every light | small | `OS_ShadeP` |
| HDR buffers, dithered grading, no lifted blacks (§6) | dark skin breaks first (Sims 4, Shirley cards) | a line in `foundations.md` | Rule 8 safeguard |
| (our reading) The pack's metrics table holds the body range by cohort (§6) | doors, sills and seats fit the people who use them | small | "standards per setting pack" |

(b) For the people step, with the study's costs:
- Race macro pinned; `idealproportions`, `cupsize` and `firmness` never used as controls; push from the family mean (§2, §6). Rule 8.
- Age keys at 35, 50, 65 and 80 as shape and value deltas, since smoothing de-ages (§4, §7.3): 3 to 5 days (WWSD 2).
- The head's light: tuned normals, a shade bias, a shared value map (§7.1.4): about a week (WWSD 3).
- Hair as planar masses from straight to coily, with equal care (Rule 8) (§7.1.5): 1 to 2 weeks (WWSD 5).
- Three stylisation stills and a control, across ten skin tones (§7.4): 1 to 2 weeks (WWSD 4).
- Era garments bound by MHCLO, and a 1989 kit of 12 to 15 pieces (§7.1.6): 2 to 3 weeks (WWSD 6).
- The recognition test (§7.4): a few days plus readers (WWSD 7; see C10). The population sampler and its trait-blind audit: about a week (WWSD 8).
- Tiers and the runtime assembler: 3 to 5 weeks (WWSD 9; figures contested, C4).

The order is the study's: the stills choose the style before rigging, garments or tiers are paid for (§7.4); the kit waits on the dress gaps; the assembler waits on the motion study's city tier.

**Flags.** Founders take a head from a curated set (§7.1.2), and Anny's authors warn its phenotypes "encode by design stereotypes of MakeHuman artists" (§2). The rule is right (audit every target, ancestry down family lines), but the audit itself is not specified. Body shape triggers trait judgements as faces do (§3, Simhi & Yovel), so the 8 to 12 build archetypes need the same trait-blind audit as faces.

## 2. behaviour-on-screen.md

### In short

- A person on screen is a witness's view of a life, on three clocks: years leave traces, days make routines, minutes stage acts (the idea, §6).
- Routine is the canvas. A change of routine is the strongest true signal, and grief shows mainly as absence (§4, §6).
- Strangers read a little extraversion and almost nothing else (Connelly & Ones; Carney), so motion's trait share is capped and state drives manner (§3; §7 rules 3, 4).
- The engine's 110 or so expressions collapse into about sixteen staged shapes. Each staged act needs an event, its visible situation in frame and the person's ordinary life around it (§6, §7).
- Five records, five engine requests (B1 to B5) and five checks: `act_check`, the lens audit, the swap test, the cut check and determinism hashes (§7, §8).

### Against the bar

| Test | Finding |
| --- | --- |
| Primary sources | The engine at r41, read through the API, is primary and the study's strongest part (§1). Connelly & Ones and Carney et al. read in full; several others from abstracts. Many load-bearing claims are secondary (Ambady, Funder, Gosling, Todorov & Uleman, the dilution effect). Games mostly from wikis. Marking is honest: Gehl, Jacobs and Whyte are "from memory" (Gaps). |
| Our stack | The least concrete, by its nature, though its records and checks are concrete. No cost on the M4: day plans are "computed ahead for a week and cached" (§7) for a starter town, with nothing for a city. Its ranked list carries no costs. |
| Thin sections | §4 (routines) rests on memory and lacks Norway's time-use data. §5 (staging) is short and secondary. Norway's proxemic values were not extracted. |

**Verdict: meets the bar with gaps that change no building-block decision.** What the building blocks take from it (stopping places, the feet field, provenance and determinism checks, nothing on bodies) holds without the missing sources. The gaps bear on people-step values: the view budget (Gehl's distances), day-plan hours, proxemic distances, staging. A pass before the people step should fetch Gehl's text, SSB's time-use surveys near 1980 and 1990 (unverified that both exist), Sorokowska's values for Norway, Kendon and Versu, and cost day plans at city scale.

### Decisions it proposes

(a) For the building blocks now:

| Decision | Why | Cost | Depends on; note |
| --- | --- | --- | --- |
| Places carry where people stop and stay: edges, steps, benches, a sunny wall, the shop door (§4) | acts happen where people stay | in the affordance schema | agrees with animation |
| The feet field is the sum of the year's day plans over the paths (§7, How it meets) | the worn step and its walkers agree | none now: walked surfaces register a walking line | `living-fabric.md`; engine B2, request 16 |
| `act_check` and the cut check beside `trace_check.py`; day plans hashed per person and day (§7 Checks) | every act names an event; replays match | small, when built | the check framework, the plan hasher |
| Social traces are things in the fabric: an empty mooring, a chair outside (§7, `trace`) | acts leave traces | none if the record admits them | request 20 |
| A behaviour budget per view: two non-routine acts at the street stop, one per street from the city camera (§7) | the history budget's twin | small | overlaps (C7) |
| Nothing on bodies; readings live in the world's own media (§7, rule 10) | evidence, not verdicts | none | wording clash (C8) |

(b) For the people step, none costed in the study:
- the records `person_behaviour`, `day_plan`, `moment` and `account` in the contract and fixtures (WWSD 1);
- day plans for a dozen people over two weeks (WWSD 2);
- the lens audit and swap test before any act animation (WWSD 3);
- the sixteen shapes, and the first moments in LT2 (§6, WWSD 4);
- B1 to B5, with B3 and B4 first, and the sifter's two rules (§7, §8);
- the two-arm cold reader test (§9).

All of it runs on `authored` fixtures until the engine's B1 to B5 land (§8); the cold reader test needs the corner through the years with people in it (WWSD 8).

State before trait (rule 4) is marked "still waiting for Øystein's view", but `docs/living-world.md` already adopts it. The camera as a witness with a place stays Øystein's, as play.

**Flags.** This study is the project's strongest guard: "Never a verdict" (§6) and rule 9 ("Same act, same body"; "Every couple is staged by the same rules"). It names two risks. Era manners from the pack ("how openly couples touch") must apply to everyone alike, or they become homophobic content by rule. Fixed personality types that follow sex (early Animal Crossing, §2) are the stereotype trap. One it does not name (our reading): the lens cap puts a share of extraversion into motion, so if the engine's traits differ by group, the lens audit must run per group.

## 3. animation-and-motion.md

### In short

- Captured motion is the base and procedural layers fit it to our world (feet on treads, gaze, posture from facts). People move smoothly, on ones, with style in the poses (§1).
- One wind field, a pure function of position and absolute time, is sampled by everything through each element's own oscillator; levels wake by Beaufort force (§3).
- Far people bake bones, not vertices, into textures shared by every body on the skeleton. Tiers break at 20, 80 and 400 m (§2).
- Every mesh carries a motion contract: class, true origin, per-element pivots and seeds kept across levels, hinges, emitters, hull points and affordances (What every mesh must carry).
- Motion is judged at the game's cameras, in silhouette and as point lights, and measured: foot slide, pairs in phase, the time-jump test (§6).

### Against the bar

| Test | Finding |
| --- | --- |
| Primary sources | Many: Bollo, Motomura, Holden, Dudash, Sousa, the Pivot Painter and SpeedTree docs, Unity's manuals, Lagarde, Bohannon, Moussaïd, the data licences, MPFB's files on this machine. The paywalled GDC talks (Clavet, Cournoyer, Tomsiński) are abstracts and write-ups, said so. |
| Our stack | The most concrete. FBX carries 2D UVs and one usable colour; `ArtImport.cs` turns animation, blend shapes and rigs off; trees use UV0 to UV2 and the colour; the Resident Drawer excludes skinned meshes; bone against vertex textures (29 KB against 576 KB a second). M4 costs for skinning, Animation Rigging and motion matching are unmeasured, said so. |
| Thin sections | Hair motion, animals, how a 1989 street was peopled. A later decision made one more: the study's route for acts no library holds is our own capture (§1), which `NOW.md` has since ruled out. How an agent edits library motion against video is unstudied. |

**Verdict: meets the bar with gaps that change no building-block decision.** The motion contract does not care where clips come from. The capture gap changes the people step: the town's own acts (a fish crate up the steps, mending a net) have no studied route, and `reality-check.md` rates "Motion-capture quality animation" out of reach. This is the area's biggest risk. A pass before the people spike should study scripted keyframe and layer editing in Blender, video pose estimation under licences that allow a commercial game, and additive layers on library bases (our reading).

### Decisions it proposes

(a) For the building blocks now:

| Decision | Why | Cost | Depends on; note |
| --- | --- | --- | --- |
| Every part: a motion class, its origin at its true base or hinge, levels that keep pivots, element ids and phase seeds, seeds from its id (What every mesh must carry; WWSD 1) | "the cheapest item here and the one that cannot wait" | 1 to 2 days | channel layout (Q1); in the plan, step 3.1 |
| Encoding: one UV channel for element index and depth; a sidecar element table; the importer bakes it into a float texture or Vector4 UVs; people get their own import rule | FBX carries only 2D UVs and one colour | same days, plus `ArtImport.cs` | the export route; texture or UVs left open |
| Per-kind data for flexible, hinged, emitting and water-touching parts (fields in section 4) | Pivot Painter 2's shape; doors open for reasons | per kind | trees' timeline (`trees.md` step 4) |
| Affordances: treads, door stand points, sit and lean points, sills, counters, shelter, lamps (WWSD 2) | feet on treads; two people on a step | half a day each for stairs and doors | sockets as dated records; in the plan |
| Motion as a function of the record and absolute time; cloth the one warm-started exception (§2, §3, §4) | a time jump gives the same street | the time-jump test (WWSD 9) | |
| A motion budget per view (§2) | a view that moves everywhere has no focus | small | overlaps (C7) |
| Clips, markup and rules as engine-neutral data (§1) | Unity's new animation system is coming | none | "kinds as data" |

(b) For the people step:
- the pipeline: MPFB's `game_engine` rig through Humanoid; CMU, 100STYLE (credited) and Mixamo (out of the repository, terms to check); a deterministic clean-up script (pipeline 1 to 4);
- the runtime layers: IK on planned treads, gaze, springs, inertialisation (pipeline 5);
- a gait seed for life, with age and mood only as small deltas (§1);
- bone textures for the city tier, about 20 bones (§2): 1 to 2 weeks;
- the motion spike (1 to 2 weeks), then the two-person scene (about 2 weeks) (WWSD 4, 5).

These depend on the licence checks (Mixamo, the face packs), on characters' person generator, and on the treads and sit points from the contract (WWSD 2).

The wind field on the birches (4 to 6 days, WWSD 3) belongs to the trees.

Already decided or in conflict: voicing is closed (written, `NOW.md`), so lip sync and Rhubarb drop. "Our own capture" (§1) conflicts with "No motion-capture sessions" (C11). Smooth or stepped is now ours to judge on frames (`NOW.md`). Its face method conflicts with `living-world.md` (C2).

**Flags.** MPFB's expression targets are "stored three times under ancestry labels" (§1, Faces); expressions must follow the face's own shape, never a label. 100STYLE is one performer acting every style (Gaps), so "Old" and "Limp" may read as caricature; the study limits them to scaled deltas, and a limp to a recorded injury (§1).

## 4. What every part or thing must carry

Unmarked rows come from `animation-and-motion.md` (What every mesh must carry).

| Carried | By |
| --- | --- |
| An id and seeds from it; picking back to its record at every tier, merged or instanced (`interface-and-inspection.md`) | every part and person |
| A motion class (still, hinged, swinging, flexible, floating, emitting) and an anchor class (static, rigid, skinned, flexible, card, fluid; `painted-marks-in-motion.md`); the origin at its true base or hinge | every part |
| Distance levels that keep pivots, element ids, phase seeds and marks (also characters §7.1.9) | every part and person |
| A metric mark coordinate; the rest or undisplaced position and normal for anything that deforms or sways; motion vectors from moving vertices (painted marks; characters §1) | every part; people and garments |
| Per element: pivot, axis, length, parent, depth, stiffness, damping, phase seed, drag class. Per vertex: element index, flutter weight | flexible parts |
| Hinge axis, limits, side, closed rest, the fact that opens it | doors, windows, shutters, gates, hanging signs, lanterns |
| Position, direction, feeding fact | chimneys, flues, vents, drip edges, spouts |
| Hull points, waterline, draught; berth, cleat and bollard sockets | boats, buoys, fenders, ladders, quay faces |
| Each tread's front edge, depth and height; walking line; landings; handrail lines; where one may sit (also behaviour §4) | stairs and steps |
| Stand point, swing side, threshold and step-up, the joined point on a way | doors |
| Sit points (height, facing, width) and lean points (height, facing) (also behaviour §4) | walls, kerbs, sills, bollards, benches, quay edges, lamps, posts |
| Sill height; stand and serve points; shelter; a lamp's cone | windows; counters; overhangs; lamps |
| A walking line registered to the feet field (behaviour §7; `living-fabric.md`) | every walked surface |
| The fabric's record with owners (characters §7.5; behaviour §6); a grip point to meet the hand sockets (our reading) | garments, carried things, gifts, social traces |
| The `game_engine` skeleton through Humanoid, about 20 bones at the city tier, up to four weights a vertex; measurements (leg, hip, eye, shoulder, sitting height); sockets (hands, head, back, hips, soles, eyes); flex weights on hems and hair ends; a face at the near tier only | people |
| Identity numbers and one gait seed, set at birth; the same height, build, hair mass and outer colour at every tier (characters §7.1, §7.5) | people |

## 5. Conflicts and overlaps

| # | Between | One says | The other says | To settle |
| --- | --- | --- | --- | --- |
| C1 | Smooth or stepped | animation §1: "People move on ones, from captured data, smooth"; "Geometry that moves through space (trees, laundry, flags, boats) stays on ones" | `what-moves.md`: "environment effects (smoke, flags, laundry, splashes) step on twos or threes"; `visual-direction.md`: "environment effects step on twos"; behaviour §7 lists "stepped timing" among what animation gives | `living-world.md` now says "judged on frames", so the study's quote of it is stale. Flags and laundry are claimed by both. Ours, on motion sheets |
| C2 | Faces | `living-world.md`: "expressions are swapped textures the engine's emotional state can choose" | animation: shape keys on the shared mesh, "brows, lids and mouth corners from the 34 shape targets"; characters §7.1.8: "Face units ... or painted expressions, as the motion study decides" | people step; behaviour adds "decide expressions per moment" (§2, Pentiment) |
| C3 | Face pack licence | characters §2: "the CC0 `faceunits01` pack" | animation §1: "the optional packs' licences were not stated anywhere we found (unverified)" | check before use |
| C4 | People's tiers | characters §7.1.9: near "about 25,000 to 40,000 triangles"; city a "`proxy741`-class shell" of the person's own shape | animation §2: near "about 15,000 to 25,000"; city "one of 8 to 12 archetype silhouettes" | archetypes clash with "Nothing repeats unless it was factory-made" (`NOW.md`); twenty near figures take 0.3 to 0.8 million of the frame's 2 million triangles (our arithmetic) |
| C5 | Who owns the gait seed | characters §7.2: "one seed, owned once", in `person_behaviour` | behaviour §7: `person_behaviour` is per "person, year"; animation §1: "a gait seed for life ... never re-rolled" | a per-year record invites a re-roll; one seed at birth, in identity (our reading) |
| C6 | The brush on bodies | characters §1: strokes "scaled to the body (a few centimetres on the face, a hand's width on a coat)" | `painted-marks-in-motion.md`: "sized by the same rule as everything else", "fewer, steadier marks" | both anchor in the rest pose; size waits on the octave-stepped brush, ours on frames |
| C7 | Three budgets per view | `living-fabric.md`: the history budget | behaviour §7: "a twin for behaviour"; animation §2: "a budget of motion per view" | one mechanism, three counts (our reading) |
| C8 | Labels | behaviour rule 10: "No labels, anywhere in the world view or the scenes" | `interface-and-inspection.md`: "hover names things"; characters §3: "a name on approach" | a name is a fact, not a reading; rule 10's wording needs narrowing to readings |
| C9 | Channel budget | animation: "One UV channel holds each vertex's element index and depth"; FBX carries 2D UVs and one colour | painted marks: rest position and normal, "three floats each, in UV channels", and a mark coordinate; characters: garment masks "in shared UV layouts"; history maps | nobody allocates the channels (Q1) |
| C10 | Readers | behaviour §9: "Ten to forty people ... Beside them, an in-house panel of model readers"; characters §7.4 recognition and trait ratings | `NOW.md`: "Cold readers are model readers" | face recognition and viewer bias are human perception; whether model readers stand in is untested |
| C11 | Capture | animation §1: "Our own capture"; 40 to 60 clips, "the rest captured" | `NOW.md`: "No motion-capture sessions" | decided; the route for missing acts is open |
| C12 | Walking speed with age | characters §4: "Flat to about 59, then down about 6 to 10% a decade" | animation §1: "about 0.2% a year to 63, then about 1.6% a year" | different secondary sources; settle in the people step |
| C13 | Skinned meshes left out | characters: Unity's Mesh LOD ignores skinning | animation: the Resident Drawer "handles only mesh renderers"; interface: instanced ids "must come from instance data we control" | people need their own tier and picking path (Q3) |

Overlaps that agree: identity as numbers (characters, animation); age reaching motion (characters §4, animation §1); no "shabby clothes overnight" (characters §7.2, behaviour §6); stopping places (behaviour §4, animation's affordances). Sorokowska is cited by both, and neither extracted Norway's value.

## 6. Unknowns

| Unknown | Learned where | Study |
| --- | --- | --- |
| Whether free library motion, edited against video, reaches the bar on true-proportion bodies and our steps, and covers the town's own acts | the people spike (WWSD 4), plan step 5 | animation |
| The M4's cost for GPU-batched skinning, Animation Rigging on about 20 people, motion matching, the runtime assembler | the harness during the spike; the crowd tier at 500 and 2,000 (WWSD 6) | animation, characters |
| Whether the rest-pose brush holds on a walking body, and at what size; how hair masses move | motion sheets of the first skinned figure and the first hair | characters, painted marks |
| Retarget faults at the body's extremes; whether gaze reads at 30 m | the spike's deformation sheet and views | animation |
| Identity across 25 years at 15 m; the push people need | the recognition test (§7.4) | characters |
| The lens cap's values; over-reading of gait | the lens audit and the first cold readers | behaviour |
| Whether model readers can stand in on faces and the swap test | the first recognition test, with some human readers beside it | characters, behaviour |
| Day-plan compute at city scale; who owns an act's day and place | after B2 and B1, from the engine | behaviour |
| Whether affordances cover interiors and practices (the head of a table) | plan step 8 | behaviour, animation |

**The cheapest early test.** A grey walker on the gully. During the gully's port (plan step 3.1), treads and sit points are exported anyway. Take one untextured MPFB body on `game_engine` and two library clips (a stair climb and a sit-down), retargeted through Humanoid. Plant its feet with Two Bone IK on the exported treads, and sit it on an exported sit point. Give it a rest-pose UV and run today's brush on it. Render it in the motion sheet at 1440p and 60 fps from eye level and the street stop. Measure foot slide and penetration in millimetres, and one skinned figure's frame cost. About one to two days (our estimate). It retires the costliest risk here: a tread or sit contract found wanting after a thousand stairs are generated. It is also the first look at library motion on our own steps.

## Across the three

**The contract parts must carry now.** The non-people rows of section 4, which the three studies and the painted-marks study agree on. Four things cut across them:
- every motion is a function of the record and absolute time, with the time-jump test among the checks;
- affordances are sockets, so they share the sockets' dating and picking;
- walked surfaces register a walking line to the feet field;
- the record schema admits garments, carried things and social traces, and the metrics table holds the body range by cohort.

**What waits for the people step.** Everything in the (b) lists: the person's look, wardrobe, tiers and assembler, rig and clips, faces, the lens cap, day plans, staged shapes, the behaviour records, B1 to B5 and the cold reader tests. Three gap passes come first: 1989 dress and hair; editing motion against video; routines, time use and proxemics.

**Three questions Fable most needs to settle.**
1. *One channel layout and class scheme.* Are the motion class and anchor class one field or two? Where do element index and depth, flutter weight, the mark coordinate, rest position and normal, and history-map UVs live? Which come through the export, and which does the importer write, given FBX's 2D UVs and one colour, and an export route that may change?
2. *Affordances as sockets.* Are they dated sockets like every other, and which must the schema hold now though they are filled later (sit, lean, stand, shelter, grip)? How do walked surfaces tie to the feet field, so wear built now agrees with walkers added later?
3. *People inside the tier and repetition rules.* Does each person keep their own shape at every tier (characters), or take an archetype at the city tier (animation), under "Nothing repeats unless it was factory-made"? People need their own skinned tier and picking path, and they are the one kind generated at runtime from weights. The scale test has no people, so how much of its budget should it reserve for them?
