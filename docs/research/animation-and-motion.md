# Animation and motion

The craft of making the world move: people, crowds, wind in trees and grass, water and boats, cloth and smoke, rain and snow, and scenes where two people talk. How masters and famous games do it, what it means for us, and what every part must carry so it can move later without being rebuilt. It builds on `what-moves.md` (the rule that everything moving carries a fact), `people-deep-dive.md` and `people.md` (people on free bases), `scenes-and-sound.md` (practices and staging idioms) and `docs/trees.md` (wind is open). Primary sources (talks, papers, developers' own posts, our own installed tools) are used where they opened; claims taken from summaries are marked (secondary), claims we could not confirm (unverified). Numbers we worked out ourselves are marked (our arithmetic).

## What the masters agree on

Across the studios, a few lessons repeat. They are the spine of this page.

1. **One cause, many movers.** Ghost of Tsushima's art direction asked that "everything needed to move", and drove grass, trees, particles, cloth and ropes from one wind (Sucker Punch, PlayStation Blog). Book of the Dead let the wind's sound drive the wind's strength (Unity). One field, sampled by everything, is what makes motion read as weather rather than as wiggle.
2. **Believable, not realistic; volume over accuracy.** God of War's wind aimed at "believable behavior rather than realistic" (Feeley, via 80.lv); Ghost of Tsushima chose heuristics and hacks over fluid simulation, putting volume before accuracy (Rockenbeck, via Game Developer).
3. **Direction must read.** One of God of War's three goals was that players see which way the wind blows; a study of game grass names "no obvious wind direction" and "exaggerated swaying" among the faults that make it look fake (Knowles & Fryazinov 2015).
4. **The body carries more than the face.** Somerville made performance "a pillar of the game no matter the camera distance" and dealt with faces only when the camera came close (Jumpship). Pentiment budgeted its hand-drawn expressions late, once story moments were known (Kennedy, Game Developer). Firewatch's other person is a voice on a radio.
5. **Generate the first pass, polish what matters.** The Witcher 3 shipped 1,463 conversations from a generator that placed idles, gestures, look-ats and cameras from the voice track, and kept 2.5 hours of hand-made cutscenes for the moments that earned them (Tomsiński, via GameAnim).
6. **Stylised timing is hand work.** Guilty Gear Xrd's held frames needed every frame posed by an animator and about 500 bones a character (Motomura, GDC 2015). South of Midnight stepped its characters procedurally in play, tuned per character, and found heavy settings made some players sick (Schneider, via SIGGRAPH blog).
7. **Realism exposes motion.** Viewers notice motion differences more on a polygonal body than on a stick figure (Hodgins et al. 1998), and the more human a character looks, the less natural its motion is judged (Chaminade et al. 2007). A painted, simplified figure forgives more than a realistic one.
8. **Detail where the camera is.** Assassin's Creed Unity ran 40 full AIs, 120 high-resolution bodies and 10,000 crowd figures at once (Cournoyer, GDC 2015). Cities: Skylines II shipped people without distance levels and was taken apart for it (Huhtala, secondary).

## 1. People

### Three ways to make a body move

| Way | Who | What it needs | What it gives | For us |
| --- | --- | --- | --- | --- |
| A library of clips, blended, with layers on top | most games; The Witcher 3's conversations | clips cut to start, loop and stop; a state machine or a blend graph | control, cheap at runtime | the base for scenes and the street |
| Motion matching: search a long take every few frames for the pose that best fits the current pose and the path ahead | For Honor (Clavet, GDC 2016), The Last of Us Part II (Mach & Zhuravlov, GDC 2021) | minutes of unstructured capture per style; markup for what cannot be inferred | movement "nearly indistinguishable from raw motion capture" (Clavet), starts, stops and turns for free | possible for the near tier on free data; to be measured |
| Procedural: few poses, springs, IK, physics | Overgrowth (Rosen, GDC 2014), Rain World, Ubisoft's IK Rig (Bereznyak, GDC 2016) | code and taste | adapts to any ground and body; tiny data | the layer that fits captured motion to our steps, bodies and states |

**Motion matching.** Clavet's team recorded "5 to 10 minutes of a person running around", imported it whole, and at runtime searched for the frame that matched both the current pose and the desired future trajectory, then blended to it briefly. They added "small structured markup to long animations" for what cannot be inferred, such as attack types, so starts, stops and turns needed no hand organisation (GDC Vault abstract). Zadziuk's "dance cards" list what a shoot must capture (walks, runs, starts, stops, plants at 45, 90, 135 and 180 degrees) so data can be reproduced and extended (secondary). Holden's analysis of the method names its core tension: the character's position comes either from game logic or from the data. Tying the body to the logic looks floaty and slides the feet; tying the logic to the body feels sluggish. His fixes are to damp the body back towards the logic, to clamp the gap, or to change the data (speed it up about 10% and mirror it). In his captures, walks ran about 1.75 m/s forwards, 1.5 sideways and 1.25 backwards (Holden, "Code vs Data Driven Displacement").

Our people are not steered by a player. Each walks a path the engine scheduled, at a speed we choose. That removes most of the tension: the path is known seconds ahead, so the search always has a true future trajectory. An MIT-licensed motion-matching package for Unity 6 exists, from a master's thesis, with inertialised blending and foot locking, its sample data in BVH, still maintained in 2026 (Ponton, `JLPM22/MotionMatching`). Its cost per character is not published, so it would be measured before use.

**Procedural.** Rosen's talk showed fluid, interactive motion from "very few key frames" (GDC Vault); one forum account counts 13 keyframes in all, spring-like rather than linear interpolation between them, with IK and ragdoll layered on (secondary). Rain World's creatures are points held at set distances, with a paper-doll set of parts drawn over them; Jakobsson moved from a mix of classical and procedural animation towards procedural, which gives the slugcat its "slippery feel" (Unity blog, secondary). Ubisoft's IK Rig took one base walk and produced, at runtime, a crouching, limping, gun-holding climb up stairs, and shared animation between bodies of different shape (Bereznyak, abstract and 80.lv).

**Layers.** The Witcher 3 reused gestures four ways: made additive so they ride on different idles, used as overrides, limited by bone masks, and weighted. Additive gestures broke when the idle under them strayed too far from the pose they were made on. Idles came in 35 variations per skeleton type, grouped by emotional state or social status (GameAnim). Gears of War 4 replaced blended transitions with inertialisation: only the new animation is evaluated, and the old pose's offset decays to nothing, "60% cheaper" overall (Bollo, SIGGRAPH 2017 sketch).

**Rule for us.** Captured motion is the base, never hand-keyed bodies. `reality-check.md` lists motion-capture quality animation among the things out of reach, and agents are weak at organic work; the free capture libraries below bring that quality within reach for walks and common acts, though not for acts no library holds. Procedural layers fit it to our world: feet on our treads, gaze at our people, posture from our facts. Motion matching is tried for the near tier, where it pays; blended clips serve the rest.

### Stylised against realistic motion

| Work | What they did with time | What it cost | What it tells us |
| --- | --- | --- | --- |
| Guilty Gear Xrd (Arc System Works) | No interpolation at all: "Every frame now is a key frame"; the mesh deformed every key to break 3D perfection; scale animation everywhere | about 500 bones a character; every frame posed by hand | Held frames are a drawing discipline, not a filter |
| Spider-Verse (Sony Pictures Imageworks) | Mostly on twos, no motion blur; Miles on twos, Peter B. on ones (secondary) | clashed with simulation, which expects every frame; a "non-destructive pipeline layer" was built for the second film (Oskarsson & Chazot, SIGGRAPH 2023) | Cloth and hair must follow the same steps, or the seams show |
| Arcane (Fortiche) | 3D characters "graphic... with imperfections" (Wanneroy, secondary); 2D effects drawn on twos (secondary) | hand-painted textures, hand-drawn effects | Effects drawn as frames can step; a character's look lives in its poses |
| South of Midnight (Compulsion, 2025) | Characters stepped procedurally in play over a stable 60 fps camera; "noticeable but not disruptive"; tuned per character | heavy settings made some players sick; cutscenes "had to be done by hand", and the team pivoted to "a much lighter treatment on the characters' bodies" (Schneider, via SIGGRAPH blog) | Procedural stepping of captured motion is fragile and needs per-case tuning |
| Disco Elysium (ZA/UM) | Plain figures in a painted city; character pipeline rebuilt three or four times (secondary) | portraits carry the faces | Two levels of detail for one person |
| Pentiment (Obsidian) | 157 rigged characters; "bones linked to the vertices"; hand-drawn expressions per character | about 13 developers at peak; expressions budgeted once story was known | Spend face work where the story is |

Unity users report the mechanical side: held keys imported as splines jitter where two identical frames meet, and stepping looks right only at one playback rate (Unity forum, secondary). The perception studies above point the same way: a figure with true proportions, like ours, exposes motion faults more than a cartoon would.

**What this means for us.** People move on ones, from captured data, smooth. Their style comes from what poses are chosen and held in the acting (a stillness, a clear silhouette at the moment of a gesture), not from dropping frames. This agrees with `what-moves.md` ("people and the camera stay smooth"). It contradicts one sentence in `docs/living-world.md` ("Stepped animation... makes library and captured motion look handmade"); the evidence says that would read as lag. Stepped effects are a look test, not a rule: smoke and steam flipbooks played without in-between blending, as drawn frames. Geometry that moves through space (trees, laundry, flags, boats) stays on ones, because a smoothly moving camera over stepped motion judders. This is for Øystein to decide.

### Faces on a budget

From `people-deep-dive.md`: a head is 120 to 160 pixels tall at 3 m, 24 to 32 at 15 m, 6 to 8 from the city camera pulled out. A face acts only in scenes. What reads far is **where the head points**: who looks at whom should still carry at 30 m, where no expression does (our reading of the table; to test).

| Approach | Example | Cost | Fit |
| --- | --- | --- | --- |
| No face shown | Firewatch (a voice on a radio), INSIDE | none | for the street and the city camera, always |
| A static painted portrait beside a plain figure | Disco Elysium | one painting a person | does not scale to thousands, nor to ageing |
| Hand-drawn expressions, budgeted late | Pentiment | per character and expression | for a few named people at most |
| Shape keys on the shared mesh | MPFB | small | the near tier |
| Run-time facial controls to fix close-ups | The Witcher 3 | an editor tool | scenes that matter |

What we already have, on this machine: MPFB in Blender 5.2 ships 34 expression shape targets (eyelids, brows inner and outer, mouth corners, lips, nose). They are stored three times under ancestry labels (`targets/expression/units/african|asian|caucasian`). MPFB can also load optional packs of 15 Meta-style visemes, 22 Microsoft visemes and the ARKit face units, 52 in its own list and 54 in its release notes (`services/faceservice.py`; release notes 2.0.15). MPFB's core assets are CC0; the optional packs' licences were not stated anywhere we found (unverified). The ancestry-keyed folders need the fairness audit of `people-deep-dive.md` rule 3: a face's expression targets follow its own shape, never a label.

Lip sync is needed only if scenes are voiced. If they are, Rhubarb Lip Sync is MIT-licensed and takes a WAV or Ogg file and an optional script (GitHub, licence file). It gives six basic mouth shapes and three optional ones: closed for P, B and M; slightly open on clenched teeth; open; wide open; slightly rounded; puckered; then F and V, a long L, and rest. Text scenes need no lip sync at all, which is how Pentiment and Kentucky Route Zero play, and how Disco Elysium played before its Final Cut added voices. Whether our scenes are voiced is a decision for Øystein; it changes the face work by an order of magnitude.

Eyes matter more than mouths. Lee, Badler and Badler (SIGGRAPH 2002) built eye movement from eye-tracking statistics, with separate talking and listening modes, and compared it with still eyes and random saccades (abstract); other character systems use it for talking eyes (SmartBody's documentation, secondary). For us that means: saccades from statistics, a blink with every larger gaze shift, and eyes that lead the head, which leads the body.

### How posture and gait show state and age

| What changes | By how much | Source | Drives it in our world |
| --- | --- | --- | --- |
| Comfortable walking speed | 1.27 m/s (women in their seventies) to 1.46 m/s (men in their forties) | Bohannon 1997 | age, sex, height, strength |
| Speed with age | about 0.2% a year to 63, then about 1.6% a year | review, 1996 (secondary) | age |
| Older walkers | shorter steps rather than slower cadence; wider base; more toe-out; longer double support; less toe clearance; less trunk and pelvis rotation | reviews (secondary) | age, health flags |
| Groups | 55 to 70% of pedestrians walk in groups; speed falls by 0.04 to 0.08 m/s per extra member; pairs walk side by side, threes in a forward V so each sees the others | Moussaïd et al. 2010 | company, closeness |
| Sadness | slow, head lowered (Roether et al. 2009, secondary); less arm swing (Montepare 1987, secondary) | | state, used sparingly |
| Weather and ground | resistance felt walking against force 7; progress impeded at force 8 | Beaufort land scale (NOAA) | the wind field |
| Identity | friends know each other's walk from lights on the joints | Cutting & Kozlowski 1977 | a gait seed set at birth |

**Evidence, not verdicts, in motion.** People read walks consistently and wrongly (Thoresen et al. 2012, in `people.md`), so a gait is a powerful and fallible claim. The rules:
- A body shows causes that are not feelings first: age, load, slope, cold, wet, wind, footwear, the hour's tiredness after a shift. These are facts, and they also blur any one-to-one reading of mood from gait, as in life.
- State shows as acts (stopping, sitting on a step, looking back at a door, walking past one's own shop) more than as a style of walk. A mood may shade a walk only as a small additive delta, never as a swapped "sad walk".
- Nothing about a walk is a moral verdict. A drunk walk appears only where the engine records drinking that evening; a limp only where it records an injury or a condition.
- Every person keeps a gait seed for life (stride ratio, arm swing, head carriage, toe-out, bounce, cadence offset). Age transforms it; it is never re-rolled. This is how identity holds across years at distances where faces are gone.

### From free bases and capture to good motion

**What we can use.**

| Source | Terms (as found) | What it holds | Caveat |
| --- | --- | --- | --- |
| CMU motion capture | "You may include this data in commercially-sold products, but you may not resell this data directly, even in converted form" (mocap.cs.cmu.edu) | 2,605 trials in 6 categories, 120 Hz Vicon, 41 markers, many subjects | noisy; many bodies and skeleton sizes; Hahne's free BVH conversions for MotionBuilder (cgspeed) |
| 100STYLE | CC BY 4.0; credit "The 100STYLE Dataset - Ian Mason" | 100 locomotion styles, 4 million frames at 60 fps; forwards, backwards, sideways, idle, transitions; BVH | one performer acting every style (secondary); some styles poorly processed (secondary) |
| Mixamo | royalty-free in commercial games; raw files not redistributed; not for training models (Adobe community copy of the FAQ, secondary) | thousands of clips: sitting, talking, smoking, drinking, carrying | kept out of the repository; check the current terms |
| Bandai Namco Research, LAFAN1 | CC BY-NC-ND 4.0 | | not usable |
| Our own capture | the tool's licence (FreeMoCap: AGPL, with a commercial option) covers the software, not our recordings (unverified) | acts no library has: a fish crate up the gully steps | needs a performer, two or more cameras, a calibration board |
| Rotoscoping from our own video | ours | Another World's movement came from Chahi filming himself (secondary) | slow; good for one gesture |

**What is already on this machine.** MPFB's rigs (`data/rigs/standard/`): `default` (163 bones, with face bones and IK helpers), `default_no_toes` (137), `game_engine` (53; MPFB's docs say it maps "100%" to Unity's Humanoid), `game_engine_with_breast` (55), `mixamo` (52), `mixamo_unity` (64), `cmu_mb` (31, the CMU MotionBuilder skeleton) and a Rigify meta-rig. So the CMU conversions and Mixamo clips each have a matching skeleton on our own base, and the game rig maps to Unity's retargeting. The base mesh is 19,158 vertices with helpers.

**Retargeting.** Unity's Humanoid system retargets any mapped clip to any mapped body through a normalised muscle space; root motion is carried on the body's centre of mass and projected to the ground, with options to keep idles from drifting and to pin height to the lowest foot (Unity manual, Root Motion). Known faults from users: feet tilt after retarget, fixed once in the avatar; sliding where hip height and leg proportion differ from the source, so the source's proportions should be matched at the hips first (secondary). Our bodies run from children to the old, so retarget faults will show most at the extremes; the deformation sheet in `people-deep-dive.md` (every target against the clip set) is the check.

**Unity's own state.** A new animation system was announced as an experimental package within the Unity 6 cycle, with procedural rigging for any skeleton, remapping across proportions and a layered state machine; the old system stays until the new one is "production ready enough" (Unity staff, Q1 2025). Animation Rigging 1.3 offers Two Bone IK, Multi-Aim, Damped Transform, Override and others on the C# Animation Jobs API. **So:** build on today's Humanoid, Playables and Animation Rigging, and keep our clips, markup and rules as engine-neutral data, so a move costs an import, not a rebuild.

## 2. Crowds and many people at a distance

| Production | Numbers | How |
| --- | --- | --- |
| Assassin's Creed Unity | 40 full AIs, 120 high-resolution models, 10,000 crowd figures on screen | a pool swaps low- and high-resolution people "without the player noticing"; a simplified brain for the many (Cournoyer, GDC 2015 abstract). Tier distances and bone counts quoted in `people.md` are unverified. |
| Hitman: Absolution | 1,200-character crowds at 30 fps on PS3-era consoles, each one interactive | GDC 2012 abstract (Fauerby); details not public |
| GPU Gems 3, ch. 2 | about 10,000 characters at 30 fps on a 2007 card in 160 draw calls instead of 59,726 | every bone matrix of every frame in one texture; each instance carries its clip and frame offset; distance levels at 20, 60 and 100 character radii; colour per instance from a painted mask; no blending between clips in the sample (Dudash, primary) |
| Cities: Skylines II | each pedestrian's teeth over 6,000 vertices, no distance levels | the developer said teeth were not the main cost but admitted the missing levels (secondary) |

**Two ways to bake motion for the far tiers.** A vertex animation texture stores every vertex's position (and normal) for every frame; a bone texture stores only the bones' matrices and skins on the GPU. For a distant figure of about 1,200 vertices, one second at 30 fps costs about 576 KB as vertex positions and normals in half floats, and about 29 KB as 20 bone matrices in full floats (our arithmetic). What decides it for us is reuse. A vertex texture belongs to one mesh, so every body shape and outfit would need its own. A bone texture is shared by every body on the same skeleton, and it allows blending two clips. **We bake bones, not vertices.**

**Unity specifics.** The GPU Resident Drawer handles only mesh renderers, not skinned ones (`people-deep-dive.md`). Skinned meshes are deformed on the GPU, and the "GPU (Batched)" mode, which groups meshes and blend shapes into shared compute dispatches, is the documented choice for "many skinned meshes" (Unity scripting reference, `PlayerSettings.meshDeformation`). Open bakers exist under MIT (`chenjd/Render-Crowd-Of-Animated-Characters`, `maxartz15/VertexAnimation`); our own is small enough to write, and must take its frame from the clock.

**Tiers for people (proposed, to be measured by the harness in `docs/foundations.md`).**

| Tier | Distance | A person is | Motion |
| --- | --- | --- | --- |
| Near | up to about 20 m (eye level, scenes, the street stop's foreground) | their own mesh, about 15,000 to 25,000 triangles with clothes and hair; 53 bones; face shape keys only in scenes | Animator and Playables; motion matching or blended clips; foot IK on treads; look-at; springs on coat and hair |
| Street | 20 to 80 m | their own shape, about 3,000 to 5,000 triangles, no face | GPU-skinned; blended loops; no IK except on steps; look-at as a head turn |
| City | 80 to 400 m | one of 8 to 12 archetype silhouettes, scaled to height and build, about 500 to 1,000 triangles, about 20 bones; hair mass and outer layer colour as instance data | bone texture, instanced; phase from distance walked |
| Far | beyond 400 m | not drawn one by one; a busy quay is a density of moving marks if anything | none, or a two-frame shimmer |

Identity across tiers holds through `people.md` rule 8: the far figure has the same height, build, hair mass, outer-layer colour and gait seed as the near one.

**Rhythm without noise.**
- *Every figure is a person.* Positions come from the engine's trips and the clock (`what-moves.md`), so a time jump gives the same street. Within a step, a body's phase comes from distance walked, not from accumulated time, which keeps feet planted and replays exactly.
- *Groups walk as groups.* Pairs side by side, threes in a forward V, slower than the lone walker (Moussaïd et al.). People stop at edges and doorways, where life already is (`between-buildings.md`, Gehl and Whyte).
- *Nothing in step.* Seeded phase, stride from leg length, cadence from the gait seed. Two figures swinging in time is a common crowd tell (our observation).
- *A budget of motion per view,* like the history budget in `living-fabric.md`. From the city camera, motion reads as a few classes: people as marks along paths, smoke, the water's value, the gust's patches in crowns. A view that moves everywhere has no focus.
- *Sparse is a strength.* One person on the gully steps at 17:50 is a fact a viewer can follow; three hundred extras are noise. Density is the engine's, never a slider.

## 3. Nature in motion

**What the studios bake and drive.**

| Who | Data on the mesh | Wind | Note |
| --- | --- | --- | --- |
| Crysis (Sousa, GPU Gems 3 ch. 16) | vertex colour: "red... stiffness of leaves' edges", "green... per-leaf phase variation", "blue... overall stiffness of the leaves", alpha ambient occlusion | per-instance wind vector summed from sources; main bending scaled by height and renormalised so the plant never stretches; detail bending by four smoothed triangle waves | the classic two levels |
| Pivot Painter 2 (Epic) | per element: pivot, X axis, extents, parent index, depth, a random value, in textures; "only one extra UV channel" | the same wind code run once per level, up to 4 levels and 30,000 elements; each child inherits its parent's motion | the general form |
| SpeedTree, games mode | per vertex wind data (format not documented) | shared sway (slowest, "almost always the only wind acting on the trunk"), independent branch motion on one or two levels "for performance reasons", ripple along normals from noise; strength and direction change with a response time; the simulation "does not loop" | shared slower than branches, leaves faster still |
| Book of the Dead (Unity) | green vertex colour: 0 trunk, between 0 and 1 first branches, 1 second branches; pivots baked by a script; flutter masks for alpha-cut branches | a wind control driven by area volumes; the wind sound's volume drives the strength | three methods: hierarchy pivot, single pivot, procedural |
| Ghost of Tsushima | joints on plants respond to local wind; trunks and branches separate; leaf ripple from layered noise | one direction; two gust layers (a large noise scrolling with the wind; a finer texture for grass); the coarse layer also drives trees and bushes; a damped wave stops pushed grass snapping back | volume over accuracy |
| God of War (Santa Monica) | "boneless" tree and leaf sway (abstract) | a fluid simulation run first each frame, read by hair, cloth, particles, foliage and audio; a velocity grid of 32×32×16 and a turbulence grid of 64×32×64 at one metre a cell (frame capture, secondary) | wind the player can see they caused |

**What real wind and real trees do.**
- *Gusts travel with the wind.* To a first approximation, turbulence is carried downwind at about the mean wind speed (Taylor's frozen turbulence hypothesis, 1938; textbook, not checked against the paper). A gust texture scrolling along the wind models exactly that.
- *Trees sway at their own pace.* In 602 measured trees, natural frequency followed trunk diameter over height squared. Pines swayed slower than spruce for their size, and internal damping was typically below 0.05 (Moore & Maguire 2004). The cantilever rule fits conifers better than broadleaves (Jackson et al. 2019). So each tree's slowest sway comes from its own timeline (`tree_growth.py` already knows diameter and height), and two neighbours never sway alike.
- *The scale of what moves is calibrated.* The Beaufort land scale (NOAA) runs: force 1 smoke drifts; force 2 leaves rustle; force 3 "leaves and small twigs constantly moving, light flags extended"; force 4 small branches move and paper lifts. At force 5 "small trees in leaf begin to sway"; at 6 larger branches move and wires whistle; at 7 "whole trees moving"; at 8 twigs break. That is our art-direction table: each level of the hierarchy wakes at its force, no earlier.
- *Wind shows as value as much as movement.* Turned leaves show their paler undersides, so a gust crossing a crown or a field is a travelling change of value. At the street stop and from the city camera this reads far better than displacement, and costs a colour term (our design, after the masters' preference for value over detail in `visual-direction.md`).
- *Seasons change the response.* A bare crown catches far less wind than a leafed one. In January the same gust whips twigs and barely moves the trunk; in July the crown heaves (our reading of the physics; to test).

**Our design.**
1. *One field.* The engine's weather gives direction and strength per hour (`what-moves.md`). The field is a pure function of position and absolute time: a large gust noise advected at the mean wind, a finer one, and a slowly varying direction. Never integrated frame by frame, so any time jump gives the same state. Local swirls only for local facts (a lorry passing, a ferry's wake).
2. *A response, not a copy.* Each element (trunk, limb, branch, spray) answers the field through its own oscillator: natural frequency from its size, damping, stiffness, phase seed. Kept deterministic by sampling the field at a few past times and weighting them by the oscillator's impulse response (a short filter), rather than by carrying state (our design).
3. *Levels wake by force.* Calibrated against Beaufort: sprays flutter from force 2, branches from 4, small trees sway from 5, whole trees from 7.
4. *Distance keeps the wind.* Far levels keep the shared sway and the value change and drop the flutter, which would only shimmer. An impostor sways as a whole by the same field. No tree freezes because it is far.
5. *Everything samples it:* trees, grass, heath, laundry, flags, hair and coats, smoke, rain and snow angle, the water's roughness, clouds (`Sky.shader` already drifts by a wind), and the wind's sound.

## 4. Water, cloth and secondary motion

**Harbour water.** A harbour basin is sheltered: short wind ripples, little swell. Its beauty is in reflection, and the physics is precise. Each glint is a mirror image of a light on a tilted facet. For a high source the path of glints is about four times the maximum wave slope long; its width is set by the slopes and the source's elevation, not the wave height; still water gives a single mirror image (NOAA; Shaw 1999). Most glitter forms on the small capillary waves the wind raises (Lynch et al. 2011, abstract). So at blue hour a quay lamp's reflection is a long, broken column, its length and breakup set by the wind field. A gust passing over the Basin is a patch where the reflections break up and the value changes. That is Kawase Hasui's water, from physics and one field. Sea of Thieves shows the stylised route: an FFT ocean after Tessendorf, with foam at wave peaks and round objects, blurred to sit with the art and set per sea state (calm, normal, stormy) (Ang et al., SIGGRAPH 2018).

**Tide is a fact.** Kartverket's predictions for Stavanger on Friday 20 October 1989 (UTC+1): high water 97.7 cm at 01:45, low 61.1 cm at 07:28, high 96.2 cm at 14:05, low 62.3 cm at 19:59, above chart datum. At 17:50 the water is falling, about 72 cm (our arithmetic). Across October 1989 the predictions run from 38.7 to 109.8 cm. A small tide, so small motion: the wet band on quay walls, the weed line, how far the ladders reach, the mooring lines' slack. It is computed from the date, like the sun.

**Boats.** A boat's place comes from its owner's record (`what-moves.md`). At its berth it moves by sampling the water at three or four hull points (bow, stern, both sides) for heave, pitch and roll, with its own lag. A rule of thumb gives a small boat's roll period in seconds about equal to its beam in metres (forum, unverified), so a sjark of about 3 m beam rolls in about three seconds. Boats on swing moorings all point into the wind: a field made visible. Mooring lines are catenaries that tighten and slacken; fenders squeeze. Unity's Boat Attack sample shows Gerstner water with a jobs-based buoyancy in URP (GitHub, secondary).

**Flags and washing.** A flag on a private pole is a fact: Norwegians fly it on official flag days and private occasions such as birthdays and weddings, by custom from morning to sunset (SNL; secondary). Laundry is a household's washday in drying weather; wet cloth hangs heavy and moves little, drying cloth begins to flutter, so the line tells how long it has been out. Light flags extend at force 3. Near the camera, cloth is a small Verlet grid with its constraints relaxed each step, the method Thomas Jakobsen of IO Interactive described at GDC 2001 (its use in Hitman, secondary). Further away a vertex shader pins the top edge and sways the rest by the field; from the city camera it is a flicker of value. Cities: Skylines II's clotheslines reportedly carried 25,000 vertices (secondary): a warning. Cloth is stateful, so whenever the camera arrives it is warm-started from rest through a few seconds of the current wind. It claims nothing, so small differences after a time jump are allowed.

**Smoke and steam.** A plume's shape tells the weather. In unstable sunny air it loops, and in neutral, cloudy or windy weather it cones. Under an evening inversion with light wind and clear sky it fans out flat; above an inversion it lofts; trapped between two it lies in a layer (meteorology lecture notes, secondary). A blue-hour sea fog is an inversion, so chimney smoke there should spread flat, not rise in a column. In 1989 chimney smoke is uncommon and means someone home with a wood stove (`what-moves.md`). Breath and exhaust steam below freezing are facts of the temperature. Unity's six-way lighting bakes how smoke responds to light from six directions and blends them by the scene's light at runtime, giving internal shadow and back-lit rims (Unity blog, VFX Graph manual). The smoke is lit by the town's light, not painted with its own, which is our rule (`docs/foundations.md`: shade is the light's). Smoking was a common small act in 1989: in 1987, 40% of Norwegian men and 33% of women aged 16 to 74 smoked daily (SSB, secondary). A cigarette in a scene is an act that shows the wind.

**Rain and snow.** Lagarde's rain for Remember Me drew streaks as four scrolling layers on a half cylinder round the camera. Particles must grow in number with the rain's strength, while a texture costs the same in any rain. A top-down depth map (256×256 over 20 m) kept rain out from under cover. Splashes ran at 20, 40 and 60 for light, moderate and heavy rain, and ripples were procedural, shown only under bright light. The whole cost about 2.8 ms at 720p on 2013 consoles. His observations: rain is hard to see except under bright light or in heavy rain; it is faint in bright areas and clearest against dark ones; splashes read best back-lit (Lagarde, "Water drop 2a" and "2b"). Tatarchuk's ToyShop added drips from edges and water trickling on glass (SIGGRAPH 2006). For us this fits the value rule exactly: rain is drawn where the light that means people is (a lamp's cone, a lit window, headlights), and falls by the field. The town height map behind our sky map (`TownHeight.shader`) can be the top-down map that keeps rain out of passages. `water.py` already knows every drip edge and splash line, so drips are emitters from facts. Snow falls slowly (about a metre a second, unverified) and drifts sideways in the field, visible in the same places.

**People's secondary motion.** Coat hems, scarves, hair ends and bags swing on springs (Damped Transform) near the camera; farther out a vertex weight lets the field move them without bones. Spider-Verse's lesson applies: if any layer of a person is ever stepped, all must be.

## 5. Scenes and staging

**How narrative games stage small acts.**

| Game | What carries the scene | What they avoid |
| --- | --- | --- |
| The Witcher 3 | a generator: idles, additive gestures with masks, look-ats on three levels (whole body, head, eyes) and cameras obeying the 180-degree rule, from the voice track; designers re-run it and polish; "Deny Areas" stop passers-by walking through (GameAnim, secondary) | hand-animating 35 hours |
| Oxenfree | long shots holding people, place and talk; choices as bubbles where the eyes already are; never taking control; silence is a choice (Krankel, GDC 2017, secondary) | cutscenes |
| Firewatch | a voice on a radio, and the world you look at: you report what you see (secondary) | faces |
| Kentucky Route Zero | sets like theatre flats; framing "done with rigid restraint"; light drops for transitions (`scenes-and-sound.md`) | detail on bodies |
| Disco Elysium | the words, and a portrait; the figure stands in the world | animating dialogue |
| Pentiment | tracks for walking, the camera almost always facing north; a small detail (hats passing between characters) grew into its own scenes (Kennedy) | finishing characters before the story is set |

**What makes them feel authored.** A held, composed frame with people small in it. Timing that allows pauses. One specific, observed act (a hat, a cup turned, a door not quite closed) rather than many generic gestures. Restraint in the camera. Light from real sources. And the Witcher's split: a system for the many conversations, hand care for the few that matter.

**The social craft.** Two or more people talking keep an F-formation: an empty o-space between them that each faces, a ring of bodies, and an outer zone watched for newcomers. Two people stand face to face, at right angles (an L), or side by side, and must keep the shape actively (Kendon 1977, 1990, via EMCA Wiki). Distances follow Hall's zones (intimate, personal, social, public; 1966), and they vary by country, age and sex (Sorokowska et al. 2017, 42 countries), so the setting pack holds them. In talk, the listener looks at the speaker more than the reverse; the speaker looks away early in a turn and seeks the listener's eyes at key points, the "gaze window" (Kendon 1967, Bavelas et al. 2002, secondary). Each kind of scene is a practice with roles (Versu), filmed by an idiom (the Virtual Cinematographer), as `scenes-and-sound.md` sets out; this page adds the bodies.

## 6. How motion is judged

Jonathan Cooper's five fundamentals of game animation are feel, fluidity, readability, context and elegance (*Game Anim*, ch. 4, via summaries). For people the player does not steer, feel matters least; readability (posing for the game's cameras, silhouettes), fluidity (blends, loops without a visible seam, settling) and context matter most.

**How masters review, and how we will.**
- *At the game's camera,* from every judging view in `docs/foundations.md`, not in a turntable.
- *In silhouette and greyscale at one-eighth.* A gesture that does not read as a shape does not read.
- *As point lights.* Johansson's displays (1973) strip appearance, and friends still know each other from them (Cutting & Kozlowski 1977); point lights were also the one style that changed viewers' sensitivity to motion in Chaminade et al. Render our walkers as joints only, and ask cold readers to tell two people apart and guess an age. This tests the gait seed without faces or clothes.
- *Looped, at speed and frame by frame, beside reference video,* sound off and then on.
- *Measured:* foot slide during contact (millimetres), ground penetration, joint limits, pairs of figures in phase, eyelines that miss their target, wind response against the Beaufort table at forces 2, 4 and 7, the count of moving things per view against the motion budget, and a time-jump test: jump an hour and back, and the street, the trees and the tide must match.

## What this means for us

### A scene with two people: the minimum

The first scene in the plan (step 5) is outdoors on the gully steps at night. A side-by-side F-formation suits it: two people sitting on a step or leaning on the wall, looking over the Basin. Their faces are in three-quarter view or profile, so no close-up is needed, and a long shot can hold them as Oxenfree does. The minimum, in order of what it buys:

1. Two people at the near tier, from the person generator, in era clothes, on the shared rig.
2. Blocking from the practice: the formation, a distance from the setting pack and the pair's closeness, a seat or lean point taken from the steps' data.
3. Base poses with life. Sitting and standing idles in four to six states (neutral, cold, tired, tense, at ease, old), with breathing and a weight shift now and then. Transitions to sit, stand and turn, joined by inertialisation.
4. Gaze on three levels (eyes, head, body), with listener and speaker rules, saccades and blinks. They also look at things in the world: a boat coming in, a lit window, the steps.
5. Gestures as additive layers with bone masks: ten to twenty beats, points, shrugs, nods and a hand to the face, timed to the words.
6. One or two small acts that are facts: a cigarette lit and smoked in the wind, a coffee cup, a hand on an arm, one standing up to leave. These are where the scene's evidence lives.
7. Secondary motion: coat and hair springs, breath vapour if it is cold, smoke on the field.
8. Faces only if the camera comes within about 3 m: brows, lids and mouth corners from the 34 shape targets; lip sync only if voiced.
9. A camera idiom: wide establishing, a two-shot, cuts only with reason, the 180-degree rule, the lamp as the key light.

About 40 to 60 clips in all (our estimate), most from Mixamo and CMU, the rest captured. The Witcher 3 needed 35 idles per skeleton for a whole game; we need far fewer for one practice.

### A living street: the minimum

1. People from the engine's schedules; position from trip and clock; a body's phase from distance walked.
2. Groups as groups, with group speeds and formations.
3. Stops where life is: doorways, landings, edges; a few sitting where the weather allows.
4. Weather on bodies: hunched and quicker in rain, leaning into a gale, hands in pockets in the cold, shorter steps on ice.
5. Feet on our steps: every tread known in advance, so each footfall is planned onto a tread, not found by a ray.
6. Desynchronised: seeded phases, strides from leg length.
7. Tiers that keep identity, and a motion budget per view.
8. The street's other movers on the same field and clock: one car whose trip is a fact, a gull flock on landed fish, smoke, laundry, a flag on a birthday, the tide.

### What every mesh must carry for motion

This is the input to `docs/building-blocks.md`. Parts made now must carry it, or they will be rebuilt later.

**How data gets into Unity.** Our parts go to Unity as FBX (`tree.py`, `export_street.py`). FBX from Blender carries 2D UV sets and one usable vertex colour, and our importer (`ArtImport.cs`) turns animation, blend shapes and rigs off. Trees already use UV0, UV1, UV2 and the colour (`Tree.shader`). Three-dimensional pivots do not fit well in 2D UVs, so the contract follows Pivot Painter 2's shape. **One UV channel holds each vertex's element index and depth. A sidecar file beside the FBX holds the element table. The importer bakes the table into a small float texture, or writes it into the mesh as Vector4 UVs.** People get their own import rule (Humanoid avatar, blend shapes on, clips imported).

**Every part.**

| Data | Why |
| --- | --- |
| A motion class: still, hinged, swinging, flexible, floating, emitting, or a mix by element | the runtime knows what may move, and by what |
| Its origin at its true base or hinge | so it can turn or sway without being moved |
| Distance levels that keep the same pivots, element ids and phase seeds | so the far version moves with the near one |
| Seeds for phase, from the thing's id | determinism; no two alike |

**Flexible parts** (trees, shrubs, grass tufts, heath, ivy, laundry, flags, awnings, ropes, wires). Per element: a pivot, a direction and length, parent and depth, stiffness or natural frequency, damping, a phase seed, and a mass or drag class (leafed or bare, wet or dry). Per vertex: the element index and a flutter weight (how free its tip is). Trees take all of this from their timeline, which already knows every node's birth year, width and parent (`docs/trees.md` step 4 promised it; not yet baked).

**Hinged and swinging parts** (doors, gates, windows and sashes, shutters, hatches, hanging signs, lanterns on brackets or span wires, cellar doors). Each carries its hinge axis, its limits, which side it opens and its closed rest. It also names the fact that opens it: someone home, a window aired, a shop open, a gale. A swinging lamp's light moves with it.

**Emitters** (chimney pots, flues, kitchen vents, exhausts, drip edges, gutter spouts, downpipe shoes, a fire): a socket with a position, a direction and the fact that feeds it. Drip edges and splash lines already come from `water.py`.

**Water-touching parts** (boats, buoys, fenders, ladders, quay faces): hull sample points, waterline and draught; berth and cleat or bollard positions as sockets for mooring lines; the quay's wet band follows the tide.

**Places people use.** The Sims put the intelligence in the objects: each object advertised what it offered and supplied the animations for its use (Wright, secondary). Our parts carry their affordances the same way:

| Part | Carries |
| --- | --- |
| Stairs and steps | every tread's front edge, depth and height; the walking line; landings; handrail lines and heights; where one may sit on a step |
| Doors | the stand point, the swing side, the threshold and step-up, the hinge; the joined point on a way (already checked by `reach_check.py`) |
| Walls, kerbs, sills, bollards, benches, quay edges | sit points (height, facing, width) and lean points (height, facing) |
| Windows | sill height, for leaning out or a face behind the glass |
| Counters, bars, kiosks | stand and serve points |
| Overhangs, porches, passages | shelter from rain, from the town height map |
| Lamps, posts | lean points; the lamp's cone for drawing rain |

**People.**

| Data | Why |
| --- | --- |
| The `game_engine` skeleton (53 bones), mapped to Unity Humanoid; a reduced skeleton of about 20 bones for the city tier | one rig for every body; retargeting; baked crowds |
| Up to four bone weights per vertex at every tier | GPU skinning and bone textures |
| Measurements as data: leg length, hip height, eye height, shoulder width, sitting height | stride, foot planning, seat fitting, eyelines |
| Sockets: both hands, head, back, hips, both soles, eyes | props (cup, cigarette, bag, umbrella), hats, contact, gaze origin |
| Per-vertex flex weight on hems, scarves, hair ends | wind on clothes without bones at a distance |
| Face shape keys at the near tier only | scenes |
| The gait seed and the person's facts | identity over years |
| The same height, build, hair mass and outer colour at every tier | recognition at distance |

### A pipeline for people's motion on free bases

1. **Rig.** Every person on MPFB's `game_engine` rig, bodies from MPFB and Anny shape targets; a Unity Humanoid avatar per person, generated.
2. **Sources.** CMU through Hahne's MotionBuilder BVH onto MPFB's `cmu_mb` rig; 100STYLE BVH, credited; Mixamo on the `mixamo` rig, raw files kept out of the repository; our own capture with FreeMoCap or rotoscoped reference for the town's own acts.
3. **Clean-up in Blender, by script, deterministic.** Resample CMU's 120 Hz and 100STYLE's 60 Hz to one rate. Filter rotations without killing accents. Find foot contacts by height and speed, and lock them with IK. Extract root motion from the hips projected to the ground, and facing from hips and shoulders. Trim, match loop ends and blend them; mirror for coverage; snap to our T-pose. Reject clips with foot slide or penetration beyond limits. Tag events (footfalls, gesture strokes, contacts) as markup, after Clavet.
4. **Library as data.** Clips grouped by practice and act, tagged by state, energy, age band and load, with their markup in JSON beside them; every tag a fact the engine can supply.
5. **Runtime in Unity.** A Playables graph whose time comes from the clock. The layers, bottom up: base locomotion (motion matching or a blend tree); an additive posture layer for age, cold, fatigue and load, as small deltas in The Witcher's way; an additive gesture layer with masks. Then Animation Rigging: Two Bone IK plants feet on planned treads, Multi-Aim turns eyes, head and chest, Damped Transform swings coats and bags. Inertialisation joins transitions.
6. **Age and identity.** Speed and stride come from Bohannon's norms and leg length. Older walkers' shorter steps, wider base and reduced rotation are deltas. 100STYLE's "Old", "WalkingStick" and "Limp" are used as scaled deltas, never as whole swaps, so no one becomes a caricature. The gait seed goes on top.
7. **Bake for distance.** Chosen loops (walks at three speeds per age band, with and without load; standing; sitting; talking) baked into bone textures at 30 fps for the reduced skeleton; instanced; frame from the clock and the person's phase.
8. **Judge.** The deformation sheet across the body range, the silhouette sheet, the point-light test, the measured checks above, the strict review, Øystein.

## What we should do

Ranked by what each buys for what it costs. Costs are Claude-days, rough.

1. Write the motion contract into the building-blocks architecture now: the tables above (element index and sidecar, motion classes, hinges, emitters, affordances, people's data), and `ArtImport.cs` extended to read sidecars. *Cost:* 1 to 2 days. *Buys:* stairs, walls, houses and trees made from today on can move and be used later without being rebuilt. It is the cheapest item here and the one that cannot wait.
2. Stairs export their treads and sit points; doors their stand points. *Cost:* half a day each, folded into the stairs kind now in review. *Buys:* feet that land on our treads, where games commonly show one foot sunk into a step and the other hovering (Burdka & Rohleder 2017, secondary); and a scene can sit two people on a step.
3. One wind field and the response filter, first on the two birches, with the value change in the crowns, calibrated against the Beaufort table and checked by the time-jump test. *Cost:* 4 to 6 days. *Buys:* the trees' open item, the base every other mover samples, and a direction that reads.
4. A people motion spike. One MPFB person on `game_engine`, with a dozen clips from CMU, 100STYLE and Mixamo through the clean-up script and Humanoid, walks up the gully steps with planned footfalls and looks at a lit window; then the same person at 17, 37 and 67. *Cost:* 1 to 2 weeks. *Buys:* proof that the free pipeline reaches our bar before step 5 of the plan, and the first numbers for the near tier.
5. The two-person scene on the steps at night, to the minimum above, judged as a scene. *Cost:* about 2 weeks after item 4. *Buys:* criterion 3's first test (a scene shows a consequence the page does not), and the clip list for practices.
6. The bone-texture crowd tier, measured at 500 and 2,000 figures in the performance harness. *Cost:* 1 to 2 weeks. *Buys:* the quay and a gig crowd at frame rate (criterion 5).
7. Harbour water with tide, glitter and boats at berths. *Cost:* 1 to 2 weeks. *Buys:* the Basin, Hasui's reflections from physics, and a fact (the tide) visible on every quay.
8. Smoke with six-way light and plume types, rain drawn in the light, laundry and flags by facts. *Cost:* 2 to 4 days each. *Buys:* the signs of life in `what-moves.md`, each one tied to a fact.
9. Judging tools: a point-light render of walkers, a foot-slide meter, a motion count per view, the time-jump test. *Cost:* 3 to 4 days. *Buys:* motion judged by measure as well as by eye, as every other system already is.

## For Øystein to decide

- People smooth or stepped. The evidence says captured motion on true proportions should run smooth (on ones), with style in the posing; `docs/living-world.md` says stepped. Environment effects on twos (`what-moves.md`, `visual-direction.md`) should become a look test rather than a rule.
- Voiced or written scenes. Written scenes need no lip sync and far less face work; voiced ones need visemes and close-up faces.
- Our own capture. Some of the town's acts are in no library: a fish crate up the steps, mending a net, sitting on a bollard. Would Øystein or friends perform them in front of two or three cameras, or do we live with the libraries and rotoscoped reference?
- Motion matching for the near tier against blended clips, if the spike shows its cost is fine.
- Licences to check before use: Mixamo's current terms, the MPFB face packs' licence, and FreeMoCap's terms for recordings.

## Gaps

- The craft talks most worth having were behind GDC Vault's membership: Clavet's and Zadziuk's motion matching, Rockenbeck's wind, Wohllaib's grass, Feeley's wind and vegetation, Sanders's Horizon vegetation, Cournoyer's crowds, Fauerby's Hitman crowds, Tomsiński's dialogues, Mach and Zhuravlov's Last of Us. We used their abstracts and the best write-ups; tier distances and bone counts for those crowds stay unverified.
- No primary source on Firewatch's tree wind, Sable's motion or Kentucky Route Zero's character animation.
- 100STYLE is one acted performer; whether its styles hold up on our bodies, and whether acted age reads as caricature, is untested.
- The cost per character of motion matching in Unity, of Animation Rigging on 20 people and of GPU-batched skinning at the street tier is unmeasured.
- Roll periods, snow fall speed and the Sorokowska distances for Norway are unverified; the plume types come from lecture notes.
- How a 1989 Stavanger street was peopled at each hour (counts, groups, what people carried) has no data yet; the engine's habits will give it.
- Hair: no study here of how planar hair masses should move.
- Animals beyond gulls (dogs on their walks, cats on walls) are not covered.

## Sources

**Motion and characters.** [Clavet, Motion Matching and the Road to Next-Gen Animation, GDC 2016](https://gdcvault.com/play/1023280/Motion-Matching-and-The-Road) · [Zadziuk and Buttner, via GameAnim](https://www.gameanim.com/?p=14043) · [DualShockers on Zadziuk's tests](https://www.dualshockers.com/ubisoft-introduces-motion-matching-the-first-step-to-next-gen-animation/) · [Holden, Code vs Data Driven Displacement](https://theorangeduck.com/page/code-vs-data-driven-displacement) · [Naughty Dog at GDC 2021](https://www.naughtydog.com/blog/naughty_dog_at_gdc_2021) · [Ponton, Motion Matching for Unity (MIT)](https://github.com/JLPM22/MotionMatching) and [thesis](https://arxiv.org/abs/2310.05215) · [Rosen, An Indie Approach to Procedural Animation, GDC 2014](https://www.gdcvault.com/play/1020583/Advanced-Animation-with) and [forum notes](https://discussions.unity.com/t/an-indie-approach-to-procedural-animation-gdc-video-talk/538228) · [Rain World, Unity blog](https://unity.com/en/blog/exploring-procedural-design-rain-world) · [Bereznyak, IK Rig, GDC 2016](https://gdcvault.com/play/1023279/IK-Rig-Procedural-Pose) and [80.lv](https://80.lv/articles/how-ubisoft-revolutionises-animation-in-games) · [The Witcher 3's dialogues, GameAnim](https://www.gameanim.com/?p=10962) and [GDC Vault](https://gdcvault.com/play/1022988/Behind-the-Scenes-of-Cinematic) · [Bollo, High Performance Animation in Gears of War 4, SIGGRAPH 2017](https://history.siggraph.org/wp-content/uploads/2022/09/2017-Talks-Bollo_High-Performance-Animation-in-Gears-of-War-4.pdf) · [Motomura, Guilty Gear Xrd's Art Style, GDC 2015](https://www.ggxrd.com/Motomura_Junya_GuiltyGearXrd.pdf) · [AWN on Spider-Verse](https://www.awn.com/animationworld/creating-stylized-universe-sonys-spider-man-spider-verse) · [Gizmodo on Spider-Verse](https://gizmodo.com/how-spider-man-into-the-spider-verses-technical-wizard-1831179866) · [Oskarsson & Chazot, variable rate animation, SIGGRAPH 2023](https://history.siggraph.org/?p=129530) · [Arcane, Enlo News](https://enloenews.org/7679/arts-entertainment/the-beauty-of-arcane/) · [Red Shark News on Fortiche](https://redsharknews.com/why-netflixs-arcane-looks-so-good-how-fortiche-ramped-up-the-animation-pipeline) · [South of Midnight, SIGGRAPH blog](https://blog.siggraph.org/2026/04/stop-motion-southern-gothic-and-games-the-visual-language-of-south-of-midnight.html/) · [VGC on South of Midnight](https://www.videogameschronicle.com/features/2025-south-of-midnight/) · [Unity forum on animating on twos](https://forum.unity.com/threads/3d-animation-on-twos-in-unity.707120/) · [Hodgins, O'Brien & Tumblin 1998](https://arxiv.org/pdf/2302.07489) · [Chaminade, Hodgins & Kawato 2007](https://academic.oup.com/scan/article/2/3/206/1631816) · [Pentiment, Game Developer](https://www.gamedeveloper.com/art/deep-dive-the-art-of-pentiment) · [Sawyer on Pentiment](https://gamebanshee.com/9ak6r) · [Disco Elysium, MCV](https://www.mcvuk.com/business-news/we-knew-immediately-that-we-needed-to-make-a-game-with-a-striking-and-unique-look-to-accompany-the-writing-a-look-that-would-balance-the-mundane-with-the-unfamiliar-and-strange-the-art) · [Somerville, Jumpship](https://blog.jumpship.co.uk/post/176054619715/developing-character-jumpship/amp) · [Another World](https://en.wikipedia.org/wiki/Another_World_(video_game)) and [Chahi's postmortem](https://www.gamedeveloper.com/game-platforms/gdc-2011-eric-chahi-s-retro-postmortem-i-another-world-i-) · Jonathan Cooper, *Game Anim: Video Game Animation Explained* (2nd ed., 2021), via [a summary](https://yufeizheng.myblog.arts.ac.uk/2021/10/24/thesis-research-week-3-the-five-fundamentals-of-game-animation/)

**Faces and eyes.** [MPFB lip sync](https://static.makehumancommunity.org/mpfb/docs/lipsync.html) · [MPFB 2.0.15](https://static.makehumancommunity.org/mpfb/releases/release_2015.html) · [MPFB exporting and rigs](https://static.makehumancommunity.org/mpfb/docs/exporting.html) · [MakeHuman licence](https://static.makehumancommunity.org/about/license.html) · MPFB's own files in Blender 5.2 (`data/rigs`, `data/targets/expression`, `services/faceservice.py`) · [Rhubarb Lip Sync](https://github.com/DanielSWolf/rhubarb-lip-sync) · [Lee, Badler & Badler, Eyes Alive, 2002](https://repository.upenn.edu/hms/51)

**Gait, state and age.** [Bohannon 1997](https://academic.oup.com/ageing/article/26/1/15/35875) · [Gait speed decline, 1996](https://deepblue.lib.umich.edu/bitstream/2027.42/111109/1/j.1532-5415.1996.tb06417.x.pdf) · [Ageing and gait parameters, review](https://pubmed.ncbi.nlm.nih.gov/26210370/) · [Roether's thesis](https://www.compsens.uni-tuebingen.de/compsens//files/publications/thesisroether2011.pdf) and [a review citing it](https://arxiv.org/pdf/2003.11461) · [Moussaïd et al. 2010](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0010047) · Cutting & Kozlowski 1977 and Thoresen et al. 2012, as cited in `people-deep-dive.md` and `people.md` · Gunnar Johansson, "Visual perception of biological motion and a model for its analysis", *Perception & Psychophysics* (1973)

**Data, licences, tools.** [CMU motion capture](http://mocap.cs.cmu.edu/) · [CMU resources](https://mocap.cs.cmu.edu/resources.php) · [Hahne's BVH conversions](https://www.sites.google.com/a/cgspeed.com/cgspeed/motion-capture/the-daz-friendly-bvh-release-of-cmus-motion-capture-database) · [100STYLE](https://www.ianxmason.com/100style/) and [paper](https://arxiv.org/abs/2201.04439) · [100STYLE review noting one performer](https://qeios.com/read/AS9PU7/pdf) · [Mixamo FAQ, community copy](https://community.adobe.com/questions-696/mixamo-faq-licensing-royalties-ownership-eula-and-tos-589400) · [Bandai Namco Research dataset](https://github.com/BandaiNamcoResearchInc/Bandai-Namco-Research-Motiondataset) · [FreeMoCap](https://pypi.org/project/freemocap/1.0.34/) · [Burdka & Rohleder 2017, foot adaptation on stairs](https://mgv.sggw.edu.pl/issue/download/147/90) · [Unity Root Motion](https://docs.unity3d.com/6000.0/Documentation/Manual/RootMotion.html) · [Unity Retargeting](https://docs.unity3d.com/6000.0/Documentation/Manual/Retargeting.html) · [Unity mesh deformation](https://docs.unity3d.com/ScriptReference/PlayerSettings-gpuSkinning.html) · [Animation Rigging constraints](https://docs.unity3d.com/Packages/com.unity.animation.rigging@1.3/manual/ConstraintComponents.html) · [Unity animation status, Q1 2025](https://discussions.unity.com/t/animation-status-update-q1-2025-gdc-roadmap/1614718)

**Crowds.** [Cournoyer, Massive Crowd on Assassin's Creed Unity, GDC 2015](https://gdcvault.com/play/1022141/Massive-Crowd-on-Assassin-s) · [GDC Vault listing with numbers](https://www.gdcvault.com/play/1022411/) · [Fauerby, Crowds in Hitman: Absolution, GDC 2012](https://gdcvault.com/play/1016443/Crowds-in-Hitman) and [preview](https://www.godisageek.com/?p=70593) · [Dudash, Animated Crowd Rendering, GPU Gems 3](https://developer.nvidia.com/gpugems/gpugems3/part-i-geometry/chapter-2-animated-crowd-rendering) · [SideFX, VAT for crowds](https://www.sidefx.com/learn/talks/vertex-animation-textures-for-crowds/) · [Cities: Skylines II autopsy](https://hothardware.com/news/cities-skylines-2-autopsy) and [the developer's reply](https://www.techradar.com/gaming/pc-gaming/no-cities-skylines-2s-performance-issues-arent-because-of-the-citizens-teeth-developer-confirms) · [Render-Crowd-Of-Animated-Characters (MIT)](https://github.com/chenjd/Render-Crowd-Of-Animated-Characters) · [Wright on smart objects](https://grandtextauto.soe.ucsc.edu/2008/03/13/ep-83-the-sims/)

**Nature.** [Ghost of Tsushima effects, PlayStation Blog](https://blog.playstation.com/?p=345372) · [Rockenbeck's vorticles, Game Developer](https://gamedeveloper.com/design/using-vorticles-to-simulate-wind-in-i-ghost-of-tsushima-i-) · [Wohllaib, Procedural Grass, GDC 2021](https://gdcvault.com/play/1027214/Advanced-Graphics-Summit-Procedural-Grass) · [God of War wind, 80.lv](https://80.lv/articles/santa-monica-studio-showed-how-interactive-wind-and-vegetation-were-made-for-god-of-war) · [Feeley, GDC 2019](https://gdcvault.com/play/1026036/Interactive-Wind-and-Vegetation-in) · [God of War frame capture](https://mamoniem.com/behind-the-pretty-frames-god-of-war/) · [Sousa, Vegetation in Crysis, GPU Gems 3](https://developer.nvidia.com/gpugems/gpugems3/part-iii-rendering/chapter-16-vegetation-procedural-animation-and-shading-crysis) · [Pivot Painter 2.0](https://dev.epicgames.com/documentation/en-us/unreal-engine/pivot-painter-tool-2.0-in-unreal-engine) · [SpeedTree games wind](https://docs.unity3d.com/speedtree-modeler/manual/wind-games.html) and [legacy wind](https://docs.unity3d.com/speedtree-modeler/manual/wind-legacy.html) · [Book of the Dead wind](https://unity.com/blog/industry/book-of-the-dead-quixel-wind-scene-building-and-content-optimization-tricks) · [Sanders, Horizon Zero Dawn vegetation, GDC 2018](https://gdcvault.com/play/1025066/Between-Tech-and-Art-The) · [Broken Roads vegetation](https://www.brokenroadsgame.com/dev-blog/vegetation-blog) · [Knowles & Fryazinov 2015](https://qastaffprofiles.bournemouth.ac.uk/display/poster/196919) · [Moore & Maguire 2004](https://www.napier.ac.uk/research-and-innovation/research-search/outputs/natural-sway-frequencies-and-damping-ratios-of-trees-concepts-review-and-synthesis-of) · [Jackson et al. 2019](https://discovery.ucl.ac.uk/10078184/1/Jackson%20et%20al%20%282019%29%20An%20architectural%20understanding%20of%20natural%20sway%20frequencies%20in%20trees%20-%20accepted.pdf) · [Beaufort land scale, NOAA](https://www.spc.noaa.gov/faq/tornado/beaufort.html) · [Beaufort scale, Met Office](https://weather.metoffice.gov.uk/guides/coast-and-sea/beaufort-scale)

**Water, cloth, smoke, rain.** [Ang et al., The Technical Art of Sea of Thieves, SIGGRAPH 2018](https://history.siggraph.org/wp-content/uploads/2022/09/2018-Talks-Ang_The-Technical-Art-of-Sea-of-Thieves.pdf) · [NOAA, glittering light on water](https://psl.noaa.gov/outreach/education/science/glitter) · [Shaw, Glitter patterns, 1999](https://www.montana.edu/jshaw/documents/Glitter_patterns_OPN1999.pdf) · [Atmospheric Optics, bent glitter paths](https://atoptics.co.uk/fz684.htm) · [Lynch et al., Glitter and glints on water](https://csuohio.elsevierpure.com/en/publications/glitter-and-glints-on-water/) · [Kartverket tide API, Stavanger, October 1989](https://vannstand.kartverket.no/tideapi.php?lat=58.974339&lon=5.730121&fromtime=1989-10-20T00:00&totime=1989-10-21T00:00&datatype=tab&refcode=cd&lang=en&interval=60&dst=0&tzone=1&tide_request=locationdata) · [Kartverket, Se havnivå](https://kartverket.no/sehavniva/) · [Roll period rule of thumb](https://www.boatdesign.net/goto/post?id=469605) · [Boat Attack](https://github.com/Unity-Technologies/BoatAttack) · [Jakobsen, Advanced Character Physics](https://gamedeveloper.com/programming/advanced-character-physics) · [SNL, flag rules](https://snl.no/flaggregler_-_Norge) · [Plume types, Penn State lecture](https://www.me.psu.edu/cimbala/me433web_Spring_2015/Lectures/Slides_Meteorology.pdf) · [NSW EPA meteorology module](https://www.epa.nsw.gov.au/sites/default/files/240162localgovernmentairqualitytoolkitmodule1scienceofairqualitypart1meteorologyairquality.pdf) · [Unity six-way smoke lighting](https://unity.com/blog/engine-platform/realistic-smoke-with-6-way-lighting-in-vfx-graph) · [SSB smoking tables](https://www.ssb.no/a/static/royk/tab-2004-02-02-02.html) · [SSB on smoking across generations](https://www.ssb.no/helse/artikler-og-publikasjoner/store-forskjeller-i-royking-mellom-generasjonene) · [Lagarde, Water drop 2a](https://seblagarde.wordpress.com/2012/12/27/water-drop-2a-dynamic-rain-and-its-effects/) and [2b](https://seblagarde.wordpress.com/2013/01/03/water-drop-2b-dynamic-rain-and-its-effects/) · [Tatarchuk, rain in city environments, SIGGRAPH 2006](https://advances.realtimerendering.com/s2006/Chapter3-Artist-Directable_Real-Time_Rain_Rendering_in_City_Environments.pdf)

**Staging.** [Oxenfree at GDC 2017, Thumbsticks](https://www.thumbsticks.com/gdc-17-creating-narrative-gameplay-oxenfree/) · [Oxenfree's dialogue](https://www.giantbomb.com/profile/darth_navster/blog/convo-interruptus-how-oxenfree-breaks-new-ground-f/113461/) · [Firewatch](https://en.wikipedia.org/wiki/Firewatch) · [F-formation, EMCA Wiki](https://emcawiki.net/F-formation) · [Bavelas, Coates & Johnson 2002](https://talkbank.org/ca/access/0docs/bavelas2002.pdf) · [Sorokowska et al. 2017](https://wrap.warwick.ac.uk/100226) · Edward T. Hall, *The Hidden Dimension* (1966) · Kentucky Route Zero, Versu and the Virtual Cinematographer as cited in `scenes-and-sound.md`
