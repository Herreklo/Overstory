# Camera and composition

How the free camera should stand, move and frame in a painterly-realist harbour town, from eye level in a lane to the near-isometric city camera. The camera is "part of the style" and the main way to play (`docs/visual-direction.md`, Views), yet its craft was a gap (`docs/systems.md`). Step 1g, the playable greybox of the corner, needs it now (`docs/plan.md`). It serves criteria 1, 3 and 5 in `CLAUDE.md`. A separate study covers play feel, focus and transitions; this one keeps to the camera and says where they meet.

Written on Opus, 21 October 2026, with two helper passes beside the main one: one on how named games frame and move their cameras, one on camera craft and the science behind it. Claims from a maker's own words, a paper, official documentation or source code are unmarked. Those from reviews, wikis, translations, abstracts or search summaries are marked (secondary), and those no source confirmed (unverified). Our own arithmetic or reading is marked (our estimate). The shared web-search budget ran out partway through, and GDC Vault was down for maintenance, so several talks were reached only through others' notes. What would not open is under Gaps.

## The bottom line

- One value drives the camera. Height, tilt, field of view, rotation pivot and speed all follow the zoom and never change on their own. John Nesky's rule for Journey is that distance and field of view both set apparent size, so changing them separately makes things pulse (secondary). Cities: Skylines ties its tilt to distance in the same way.
- Painters, broadcasters and our own eye chose flat views. Frames picked by hand for the heart, from 3 m over the steps to 48 m above the harbour, look between 9° up and 7° down (our estimate). Hopper put the viewer on the pavement. Football is filmed from the side at 12 to 16° down, because going higher loses the read. So the tilt is flatter near the ground, as Øystein asked, and stops at 60° down.
- Our air needs a view along the ground. Distance is drawn as coloured layers of air (`docs/visual-direction.md`). A steep view sees everything at about the same distance, so the air has nothing to grade.
- At eye level and the street stop, verticals stay vertical through a lens shift. A tilted camera makes buildings lean back, which architectural photographers avoid (secondary), and Unity's physical camera shifts the lens without tilting.
- In narrow lanes the camera is a careful walker. It slides along walls on a coarse hull of its own, keeps a metre from every face, follows a smoothed line over the steps and slows where the walls are close. Zooming out cranes it up the lane; it crosses roofs only when it is above them. The sources agree: plan ahead rather than react, collide with a sphere a little larger than the near plane, and use springs, never clamps (Haigh-Hutchinson).
- Nothing is cut away in the town. A hole in a wall or a lifted roof would read as damage, a false history. The camera goes to see instead.
- The generator emits camera data from the facts it builds from: a hull, a tube for every lane and stair, each doorway's poses, no-go volumes and dated vantages. Level designers author camera volumes by hand (Super Mario 64's trigger boxes, Journey's hints). Ours come from the town's records, and they only shape limits and preferences. The player's input always wins.
- No depth-of-field blur from raised views. Blur that grows with depth makes a real scene look like a miniature (Held and colleagues, 2010). Our town must never read as a toy.
- Comfort comes first: no shake, no bob, no smoothing on direct mouse look, a field-of-view setting, turning speed scaled to the lens, and a speed cap in lanes set by how close the walls are.
- The camera's cost depends on where it may go and how close, more than on its lowest height. The plan's open item on eye level should be settled by a reach bake: sample every pose the camera may take, and record each part's closest approach and largest size on screen.

## 1. How painters and film-makers choose a view

Hopper's viewer stands where a person could. *Nighthawks* places the viewer on the pavement, and its viewpoint "is cinematic"; in *Room in New York* the viewer looks in through a window (secondary, Wikipedia). He reduced buildings to "everyday geometrics" and said his favourite thing was "painting sunlight on the side of a house" (Troyen, quoted on Wikipedia; secondary). Hammershøi turned his figures away and left his exteriors of Copenhagen and London "devoid of people", in a narrow range of greys (secondary). Hasui worked from sketches made on site and called himself a realist (secondary). Stålenhag starts most works from his own photographs (secondary). Our reading of the three is a person's view, from standing or window height, frontal or along a road (unverified). Hiroshige's *One Hundred Famous Views of Edo* used a vertical format and enlarged what stood in front (secondary): the repoussoir, a near dark shape framing a lit view beyond, which the visual direction already asks for.

Ozu kept his camera one or two feet off the ground and used a 50 mm lens throughout; between scenes he cut to the building where the next scene happened, instead of a fade (secondary). *Rear Window* is shot "almost entirely from within one room", watching the neighbours' routines, and Truffaut read its binoculars and telephoto as the camera itself (secondary). Tati shot *Playtime* in 70 mm so people stayed readable in the far background, "detested close-ups" and used sound to direct attention (secondary). Roy Andersson built a film from forty-six long tableaux (secondary). These are the models for watching a town: a held wide frame, many small acts in it, the eye free, sound pointing where to look. Here the camera meets the focus study.

Panoramic town maps of the nineteenth century were drawn "as if viewed from above at an oblique angle", from an imagined height, with the landmarks played up; some of it "bordered on the fraudulent" (secondary). The oblique bird's-eye is the city camera's ancestor, and its warning is ours: choose the view, never exaggerate a fact. True isometric looks down 35.264°, the 2:1 pixel form about 30° (secondary). Our city view in `LT1Time.cs` looks down 35.4°.

Football broadcasting gives the one numeric rule we found for reading many people moving. The main camera sits on the halfway line, 30 to 40 m back. It looks 20 to 30° down at the near touchline and 12 to 16° down at the centre spot. Coverage "is compromised by excessive distance from the field (d = 60 metres maximum) or excessive height" (Free TV Australia, OP-32). UEFA asks for 12 to 15° (secondary).

Tilting a camera at a building makes it lean back, which "is often considered undesirable"; architectural photographers shift the lens instead (secondary, Wikipedia). Unity's physical camera does the same: "If you shift the lens up instead of rotating the camera, you can change the composition … but parallel lines stay straight" (Unity manual).

| Finding | Source | For the camera |
| --- | --- | --- |
| A single object is preferred at the centre, whichever way it faces | Palmer lab | frame a thing of focus at the centre |
| A facing or moving object is preferred with room ahead of it | Palmer lab | lead room for a walking person |
| Objects seen from above are preferred low in the frame | Palmer lab | raised views put their subject low |
| Rule-of-thirds scores did not separate highly rated photos and paintings from others | Amirshahi and colleagues 2014 (secondary) | no thirds snapping |
| People agree on a best view of an object, commonly reported as three-quarter from slightly above | Blanz, Tarr and Bülthoff 1999; Palmer, Rosch and Chase 1981 (both secondary) | three-quarter, slightly raised views |
| Side light models form, front light flattens | `docs/town-plan.md`; `LT1Trees.cs` sets the sun about 60° off the view "as a painter judges form" | prefer the sun to one side |

The master's critique of 20 October found our cameras "composed to check layout, not to make pictures" (`docs/experiments.md`). The frames chosen since tell their own story. Measured from the shots in code (our estimate):

| Frame | Camera height | Tilt |
| --- | --- | --- |
| The street stop on Gully Steps | about 3 m over the steps | 9° up |
| Harbour Row's quay; along High Terrace | 4 and 12.5 m above the harbour | level |
| Into the light; over the roofs; Watch Knoll | 21 to 42 m above the harbour | 3 to 4° down |
| The middle stop | 48 m above the harbour | 7° down |
| The far stop | 320 m above the harbour | 25° down |
| The city view (`LT1Time.cs`) | about 84 m over the corner | 35° down |

Chosen for beauty, the views came out nearly level up to the roofs and beyond. The 20 October finding adds the other half. A camera held at one height over the old town sees only roofs, so it has to come down into the lanes and look along them.

## 2. Cameras in games with towns and worlds

Disco Elysium never turns. "Since the camera angle is always the same", its plants are hand-painted on transparent sheets over backgrounds rendered from 3D and painted over. Anything animated, pickable or dependent on time is real-time "instead of being painted into the background" (ZA/UM, via GameBanshee). A painted plate holds only what is stable, from a locked viewpoint: fit for staged scenes, never for the free camera. Pillars of Eternity is the same, 3D figures over pre-rendered backdrops (secondary). Kentucky Route Zero builds scenes as theatre flats, frames them "with rigid restraint", and changes views as a stage does: walls dissolve, lights drop, a bar lifts its rafters (secondary). Pentiment runs people on tracks for "control over camera framing" and keeps the camera facing north, so rooms connect without confusing stage left and right (Obsidian, Game Developer).

Firewatch's default field of view is 55, changed only outside the game (Panic's help page; the axis is not stated, and Unity's field is vertical). Obra Dinn plays each memory as sound over black, then lets the player walk a frozen moment (secondary): the strongest precedent for a scene that shows a consequence. Kingdom Come: Deliverance plays a whole town, modelled on a real one, in first person (secondary); it needs no occlusion rules, but every street must hold at eye level.

Townscaper orbits and zooms and allows a view straight down (secondary); Stålberg wanted it "readable at a distance", with outlines crisp "at any angle or distance". Tiny Glade's camera is bounded by the glade, its photo mode has a "See Through Trees" filter, and its first-person mode ignores collision with what you build (all secondary).

City builders split the street from the sky. In Cities: Skylines the tilt is the player's own up close and tends to straight down as the camera pulls out. The camera may not look above the horizon. It is kept out of buildings by a lift over a smoothed height field of terrain, buildings, roads, props and trees. A cushion above it grows with distance (all secondary, from mods that copy its camera code). Its near clip is 5 m, so it never reaches the street, and it carries a tilt-shift blur (secondary). Street level came from mods, and inside vehicles they show "ugly mesh parts" (secondary). Cities: Skylines II puts collision and depth of field in a photo mode (Paradox), and Manor Lords puts ground level in a separate visit mode with no interaction (secondary). Our camera runs continuously from 1.65 m to the city camera, which is rarer, and possible only where the street holds up wherever the camera can land.

Baldur's Gate 3 roams with WASD, turns on Q and E, zooms on the wheel and has a tactical view on O; edge panning is off by default (bg3.wiki; secondary). A reconstruction of its occlusion casts a sphere from the character to the camera about ten times a second. The pixels in between are cut away with a noisy edge, which also lets clicks through (secondary). What it does in the Lower City's tight streets beyond that, and how dialogue takes over, we could not confirm (unverified). Divinity: Original Sin 2 fixes its tilt and caps its zoom; a mod that lifts the cap "uncovers huge regions of the map" (secondary). The cap was doing information design. The Sims cuts away the room under the cursor, keeps the last three rooms cut and caps the cut walls with a sloped top (secondary, from the FreeSO reimplementation). Its design asked that walls "appear thick" (secondary). The thick cap makes the cut read as a drawing convention.

We reached no primary source on how Hitman, Assassin's Creed or Uncharted handle alleys and stairs. Nesky's list covers the ground for Journey (section 3), and our camera has no body to follow. Red Dead Redemption 2's cinematic camera composes "a montage of shots" while the horse rides itself, and hides what lies ahead when riding towards the camera (secondary). An auto-composed camera works only while the player has handed over steering.

| Game | Frames and limits | Forbids | Occlusion | We take |
| --- | --- | --- | --- | --- |
| Disco Elysium, Pillars | one angle; painted or pre-rendered plates | turning, tilting | painted in | plates only in staged scenes |
| Kentucky Route Zero, Pentiment | fixed, restrained; one facing | free looking; depth walks | composed | stage changes and one facing per place, in scenes |
| Firewatch, Obra Dinn, Kingdom Come | first person | a third person | none needed | colour in depth layers; the walkable held moment |
| Townscaper, Tiny Glade | orbit, zoom, bounded | leaving the land | a tree filter | a town that reads from every angle |
| Cities: Skylines | tilt tied to distance; lift over the town | the horizon; the street | the lift | the tilt curve and the lift; never its tilt-shift |
| Manor Lords, CS2 | a separate ground mode | acting at ground level | none | a warning: ground level as an afterthought |
| Baldur's Gate 3 | zoom, turn, tactical view | (unverified) | a sphere cut round the character | nothing for the town: the ragged hole reads as damage |
| Divinity: OS2 | fixed tilt, capped zoom | seeing too far | the caps | limits as information design |
| The Sims | stepped zooms and turns | (early games) free angles | room cutaway with thick caps | caps, if we ever cut |
| RDR2 | a montage while riding | steering while it composes | none | compose only when steering is handed over |
| Football broadcast | side-on, 12 to 16° down, within 60 m | going higher | none | the middle stop's geometry for watching |

## 3. Camera behaviour craft

### One value drives the rest

Nesky's list for Journey says it plainly (secondary, from a translation of his GDC 2014 talk). Don't use the same distance at every pitch (item 14). Widen the field as the camera tilts to the sky (15). Never change pitch, distance and field of view independently, or objects visibly pulse; tie them to one value and let other systems add to it (16). Cinemachine's FreeLook modifier does this across an orbit (Unity).

For us that value is the zoom, read as the logarithm of the height over the ground, so equal wheel notches feel like equal steps from 1.65 m to 120 m. Speed follows height, so the town passes under the camera at about the same rate on screen at every stop.

### Side views, lens shift and the pivot

The tilt is flat near the ground and steepens with height, stopping at 60° down. Above that the view shows only roofs and crowns, and the air has no depth to grade. The top of the zoom hands over to the illustrated map (`docs/living-world.md`), so the camera never needs to look straight down.

At eye level and the street stop the default framing uses the lens shift: the camera stays level and the frame slides down to show the ground, so verticals stay upright. When the player tilts, the camera rotates, so looking up a stair feels like looking up. The shift fades out between the street stop and 12 m. A full correction against a partial one is a look question, judged on frames (`NOW.md`). Picking rays and screen-space effects must use the shifted projection; `ScreenPointToRay` uses the projection matrix, and our sun-position pass must be checked (unverified).

Near the ground the camera turns about itself, as a head does; orbiting a point thirty metres ahead would swing it through the houses. From 12 m up it orbits the ground point at the screen's centre, no further than four times its height, so the town turns under it. Between the two the pivot slides.

### Collision, standoff and narrow lanes

The sources agree on the rules:
- Plan ahead. Predictive cameras "typically have better navigation results than reactive cameras" (Haigh-Hutchinson, *Real-Time Cameras*, excerpt).
- Collide against a camera-only mesh that leaves out small openings and clutter (Haigh-Hutchinson).
- Make the sphere a little larger than the distance to the near plane (Haigh-Hutchinson). Cinemachine's default radius is 0.4 m.
- Tag what may block the view and what may not; thin things are collided with but ignored for sight lines (Nesky 9).
- Rise over gentle slopes, and on hills look ahead and average the height change (Nesky 11 and 26).
- Use springs, never hard limits (Haigh-Hutchinson). A tube along a path lets the camera stray up to a set radius (Haigh-Hutchinson).
- Never leave the camera "on the wrong side of a closed door" (Haigh-Hutchinson).

With the near plane at 0.2 m and a 46° lens, the near plane's corners lie 0.26 m from the eye, so a 0.4 m sphere covers them (our estimate). The sphere is only the backstop. The working limit is a standoff of 1 m from every building face, held by a spring from 1.5 m. At 1 m a pixel covers 0.6 mm, about the near tier's half-millimetre texel (`docs/foundations.md`); closer, every texture would have to be finer. In a 3 m lane the standoff keeps the camera within half a metre of the middle.

In a lane the camera walks. It slides along the hull and follows a ground line smoothed over about two metres and looked ahead half a second, so single steps never bump it. On a stair it follows the nosing line and leans its default tilt by about half the slope. Up the gully's lower flight, about 26°, it looks some 13° up (Nesky 25 and 26; our estimate). Its speed is capped by the nearest wall. A wall d metres away passes at up to v/d radians a second. At 2.2 m/s and 1.5 m that is about 84° a second (our estimate), and the cap holds it near 90°.

Zooming out in a lane cranes the camera straight up. Above the eaves and ridges round it, plus a clearance, it crosses the roofs, lifted over a smoothed height field as in Cities: Skylines. The town's height map behind the sky map (`SkyMap.cs`) supplies the field. Zooming in from above aims at the cursor. Over a roof it aims at the nearest open ground instead, and comes down along a path that clears the roofs. The path is planned through the town's open spaces and then avoids obstacles locally, Haigh-Hutchinson's two levels.

At low height the camera never hops over a house. A hop is a fast vertical move, which Nesky warns makes people sick (items 45 and 46). It shows backs no one built (`docs/research/pre-mortem.md`, story 8). And it breaks Arkane's rule in the town plan: no view of a place the player cannot go. Whether players want a drone's freedom anyway is tested in the greybox (For Øystein, 1).

### Occlusion from raised views

| Strategy | Games | Fits a free camera | Reads as a fact here | Verdict |
| --- | --- | --- | --- | --- |
| Composed by hand | Disco Elysium, KRZ, Pentiment | no | yes | staged scenes |
| Room cutaway with thick caps | The Sims | yes | a drawing convention | not in the town: interiors are scenes |
| Sphere cut round the focus | Baldur's Gate 3 (secondary) | yes | no: reads as damage | no |
| Roofs or floors sliced off | XCOM, Mimimi's games (unverified) | yes | no: a ruin | no |
| Caps on zoom and tilt | Divinity: OS2 | partly | yes | yes, as the tilt cap |
| Lift over a smoothed height field | Cities: Skylines | yes | yes | yes |
| Silhouette through walls in a declared mode | Hitman's Instinct (unverified) | yes | a marked layer | only for the followed or selected person |
| A filter the player picks | Tiny Glade (secondary) | yes | a chosen filter | an accessibility option at most |

The town on screen is facts, and anything that reads as history must be one (`CLAUDE.md`). So the free camera removes nothing; to see into a lane, the player brings it down. A person the player follows under eaves may show as a quiet silhouette with no hue, direction or glow, judged in the interface study's highlight test. Leaves within about 0.6 m of the eye fade by dither, too close to be read as anything. Roofs lift only in staged scenes, as Kentucky Route Zero lifts its rafters, where the frame says theatre.

### Hints from the generator

Level designers author camera behaviour per space. Super Mario 64 places rotated boxes that set a camera mode while Mario is inside, with modes for spiral stairs, close interiors and parallel tracking. A box for one area beats one for the whole level, and modes change by timed transitions (the decompiled source). Metroid Prime slid its camera along invisible designer surfaces (secondary). Journey's tower is a hint with a clear centre (secondary). Nesky's reason (item 29): rays find a surface's shape, not what matters, and hints matter most in tight, cluttered spaces.

Our town is generated from facts, so the generator can emit what a level designer would author, for every lane, stair, square and doorway, in every town and at every date:

| Hint | Made from | Sets |
| --- | --- | --- |
| Camera hull | building masses, walls over 1.2 m, rock, trunks; clutter left out | collision and standoff |
| Lane tube | each way's centreline, width, eaves and slope | free width, ceiling, headings, speed cap, ground smoothing |
| Stair tube | the flight's nosing line and landings | the ground line, the tilt's lean, pause points |
| Open place | squares, quays, the landing | a pivot at the centre when still; a landmark's heading |
| Threshold | doorways, passages under houses | poses for entering and leaving a scene; a ceiling |
| Vantage | the town plan's sightlines; a best-view search | a composed pose: place, heading, tilt, lens, best light |
| No-go | unbuilt backs, private yards, under the quays | where the camera may not be |
| Occluder tag | every part | solid, thin or foliage |

The case for it is strong. The generator already holds every one of these facts, and it scales to any town without hand work, as the project's rules ask. Hints made from facts also carry meaning that rays cannot find: a node, a landmark, a planned view. The risks are real. Hints that pull different ways cancel out (Nesky 8). A hint that steers takes the camera from the player (Nesky 34). One bad rule repeats in every lane. Hints go stale as the town changes, so they are dated like parts. And a vantage placed where the stories are would be a reveal mode, the trap the interface study warns of.

So influences are grouped by what they act on (position, heading, tilt, height, lens) and ranked. The player's input comes first, then safety (hull, standoff, no-go), then a held pose, then hints, then the zoom's defaults. A hint changes limits and preferences and never moves a camera the player is steering. After the player lets go, it waits until the player moves again (Nesky 35), and a vantage switches off once seen (Nesky 36). Vantages are chosen for the picture (sightlines, landmarks, light), never for where the history is.

### Composition helpers

The evidence lets the helpers be few: centre a thing of focus, give a moving person room ahead, put a raised view's subject low, prefer three-quarter views with the sun to one side, and skip the rule of thirds. Nesky adds: never roll or turn in place to set a subject off-centre, since players aim from the centre; offset sideways, and only while still (item 27). Move sideways for a near target and turn for a far one (31 and 32). All three helpers run only on request:
1. *Frame this.* On inspect or a key, the camera finds a pose within its height band that centres the thing, or leads a moving person. The pose shows the thing three-quarter from its lit side, keeps verticals upright and keeps the horizon out of the frame's middle. It rejects poses where something near covers the thing, by rendering a few candidates small with the thing in a flat colour (Haigh-Hutchinson's visibility test). Two people use toric framing, which cuts the search for two targets to a few angles (Lino and Christie 2015; abstract).
2. *Watch.* The camera holds still and wide at the street or middle stop while the cursor roams. Following a person, it keeps them side-on with room ahead, without cuts. This is where the camera meets the focus study.
3. *Vantages,* found by the player and settled into gently when the player stops near one (For Øystein, 3).

### Smoothing, damping and comfort

Every smoothing is written as a half-life, the time to close half the gap. Daniel Holden's exact damper, `lerp(x, goal, 1 - exp(-ln2 * dt / halflife))`, does not depend on frame rate. His critically damped spring adds velocity, so motion starts and stops without a jolt, and it trails a steadily moving target by the half-life divided by ln 2. Across a switch, carry the offset and its velocity and let them decay (inertialization). Cinemachine's damping is exponential to one per cent, so its half-life is about 0.15 times its damping value. Its defaults come to about 0.15 s for following and a 2 s ease between cameras (source code). Direct mouse look is never smoothed: there should be no difference between the controller's movement and the camera's (Game Accessibility Guidelines). What the camera does by itself is smoothed. A stick gets an S-shaped response (Nesky 39).

| Comfort rule | Source |
| --- | --- |
| No shake, no bob, no motion blur by default; sliders for any we add | XAG 117; Nesky 43 and 44 |
| A field-of-view setting; never snap the field | XAG 117; Nesky 41 and 42 |
| A way to turn off automatic camera motion; separate sensitivities; inversion | XAG 117; Nesky 37 |
| Ease into tilt limits | Nesky 47 |
| A move too fast to follow is a cut: make it one | Nesky 46 |
| Turning speed scaled to the lens | from the arithmetic in de Vries and colleagues 2007 |
| Speed in lanes capped by the distance to the walls | our estimate, from optic flow |
| Test with beginners and strangers, who hide nausea out of politeness | Nesky 49 |

The field-of-view evidence is mixed. A narrow field turns rotation into a large flow on screen: at 10° wide a turn of 180° a second sweeps about 18 screen widths, at 60° three. Yet in the one controlled desktop study we read, matched rendered and displayed fields made 20 people sicker than mismatched ones, against the authors' own hypothesis (de Vries and colleagues 2007). A 27-inch screen at 65 cm covers about 29° vertically (our estimate), so a 46° lens shows about one and a half times that. We take the setting from the guidelines and leave the default to the playtest.

### Hand-over and held views

Nesky's rules for cuts (items 18 to 20, 34 and 46):
- keep the control frame continuous across a cut, or blend the input's direction;
- give a landmark after a cut;
- never flip 180° at the end of a scene;
- don't give control and take it back;
- if a move would be fast, cut.

Entering a scene, the camera eases to the threshold's outside pose in under a second, the house's front in frame, then cuts inside, as Ozu cut to the building first. Leaving, it cuts to the outside pose facing out into the street, as a person stepping out would. The subject keeps its side of the screen, any blend uses inertialization, and the stick keeps its old meaning until released. How it feels belongs to the transitions study; the poses belong to the threshold hint. Across a jump in years the camera does not move at all, since the time study's rule is to hold everything but the year (`docs/research/time-on-screen.md`, rule 2). Named poses are stored as data so a view can be found again.

### Depth of field

In Held, Cooper, O'Brien and Banks (2010), a blur gradient that followed the ground's depth made real scenes read as miniatures, nearly as strongly as true depth of field. Their camera was 500 m up, looking down 35°, much like our city camera. Natural blur at true scale is that of a pupil-sized aperture, about 4.6 mm, which at those distances is none. So the raised views have no depth of field; distance softens through air, value and the marks' fading detail. Depth of field at natural strength is allowed only at eye level and in staged scenes.

## 4. The camera and the painted look

The painting reads best where our chosen frames put it: nearly level up to the roofs, along a lane or over roofs to the Basin, the light to one side or ahead. Three reasons agree. Fronts and ground are where history is read (`docs/visual-direction.md`). The air's layers need depth along the view. And roofs, chimneys and crowns read as shapes against the sky only from the side.

The painted far town has no study yet (`docs/research/painted-far-town.md` does not exist). The camera's range splits it in two. Below about 12 m, the town past 50 m shows only down lane vistas and across the Basin, a hundred metres off or more, and the camera moves at walking pace. A backdrop baked per cell would hold there: a 10 m move against a view 300 m away shifts it about 2° (our estimate). From 35 m up the far town fills the frame, so it must be real geometry with painted textures, the city tier. A flat backdrop holds only near the point it was painted from, as Disco Elysium's locked plates show. The far-town look test should be judged in both cases.

What the camera's range costs depends on three things, and the height floor is the least of them:
1. How close it comes. At the 1 m standoff a pixel covers 0.6 mm, which the near tier meets. A 0.4 m sphere alone would allow 0.24 mm and ask for textures 2.5 times finer everywhere (our estimate).
2. Where it goes. On public ground it sees fronts, lanes and squares. Over walls it sees backs and yards that must then be built.
3. What it looks up at. At eye level the undersides of eaves, balconies and signs come within two metres.

In a 3 m lane the walls are 1 to 1.5 m away at eye level and at the street stop alike, so both need the near tier there. Eye level adds mostly the ground underfoot and the undersides. A reach bake settles the plan's item 8: sample many reachable poses under each rule, and record each part's closest approach, largest size on screen and faces seen.

## 5. The camera for each kind of game

| Game | Where it lives | What it needs | What it must not lock out |
| --- | --- | --- | --- |
| A manager (a club or a band) | the middle and city stops; scenes for matches and gigs | fast travel between its places; posters and crowds readable from the middle stop; the broadcast geometry in match scenes | the street stop, to walk past the posters |
| An exploration game | eye level and the street stop | lanes, stairs and squares at eye level; vantages found as rewards; no arrows (Nesky 30) | eye level anywhere public; rises fast enough, but no faster than streaming |
| A family across generations | the street stop and 12 m round the home | named poses kept like photographs, to compare years in place; a slow camera, held across jumps | the same pose finding the same view decades later |
| The observer (the interface study's case) | held views at the street and middle stops | watch and follow; a long lens to inspect, as in *Rear Window* | knowledge only from what a witness could see |

The last row raises a play question. The behaviour study treats the camera as a witness with a place (`docs/research/behaviour-on-screen.md`). From 12 m it sees over walls into yards no one in the street could see. What counts as "you saw" from there is for Øystein (For Øystein, 2).

## 6. The proposal

### The greybox camera

A small controller of our own on a plain Unity camera, read through the Input System already installed. Cinemachine's collision follows an avatar, which we do not have, so Cinemachine waits for the staged scenes of step 5, where its blends earn their keep. All values are first values, tuned by playing.

| Stop | Height over the ground | Default tilt | Tilt range | Vertical lens | Turns about | Pan speed |
| --- | --- | --- | --- | --- | --- | --- |
| Eye | 1.65 m | 2° down, by lens shift | 30° up to 40° down | 46° (28 mm) | itself | 2.2 m/s |
| Street | 2.8 m | 5° down, by lens shift | 25° up to 45° down | 46° | itself | 3 m/s |
| Close | 12 m | 10° down | 5° up to 50° down | 40° | a point ahead | 12 m/s |
| Middle | 35 m | 16° down | 5° up to 55° down | 34° | the ground at the centre | 35 m/s |
| City | 120 m | 35° down | level to 60° down | 24° | the ground at the centre | 120 m/s |

- *The ladder.* Each value is a smooth curve over the logarithm of height. The wheel covers eye level to the city camera in about twenty notches, with soft detents at the stops. The greybox stops at 160 m; in the game the map takes over there. The player's tilt is kept as an offset from the default, clamped to the band.
- *Height.* Measured over a ground smoothed over 2 m and looked ahead half a second. Below the eaves the camera slides along the hull; above the ridges plus 3 m it crosses roofs, lifted over the smoothed height field. Zooming out cranes up; zooming in aims at the cursor's nearest open ground.
- *Collision.* A 0.4 m sphere against the hull, a 1 m standoff from building faces held by a spring from 1.5 m, no-go volumes, and leaves fading within 0.6 m.
- *Motion.* Critically damped springs: 0.08 s half-life for panning, 0.25 s for height and the lift, 0.12 s per zoom notch. Key turning at 60° a second, scaled by the lens over 46°. In lanes, speed in metres a second capped at 1.6 times the distance to the nearest wall.
- *Lens.* The shift at eye level and the street stop, fading out by 12 m. A field setting of 10° either way at the low stops. Eye level tried at 28 mm and 35 mm.

| Act | Mouse and keyboard | Gamepad |
| --- | --- | --- |
| Move | WASD or arrows; Shift faster, Ctrl finer | left stick, S-curve |
| Look | hold the right button and drag, raw; Q and E turn, R and F tilt | right stick |
| Height | wheel, towards the cursor from 12 m up; Page Up and Down | triggers |
| Stops | 1 to 5, an eased crane | d-pad up and down |
| Go there | double-click the ground | hold A on the centre pick |
| Frame this | F, or on inspect | Y |
| Hold (no automatic motion) | Space | View |
| Back to the last view | Home | B, when no card is open |
| Inspect | left click (`interface-and-inspection.md`) | A, bubble pick |

Edge panning is off by default, as in Baldur's Gate 3. On the pad the heading turns gently with motion along a lane while the right stick is idle (Nesky 23); with the mouse it does not. The camera never rolls.

### The views it must hold

Every judging view must be a pose the camera can reach, or "never a place the player cannot put the camera" (`docs/visual-direction.md`) is broken. Eye level and the street stop on Gully Steps, 12 m up the lane and the city view at 35° fall inside the bands. So do the heart's frames up to the middle stop (our estimate). Their heights are above the harbour, so each camera stands lower over the ground under it. The lens setting covers the 35 mm eye-level views. Two do not fit. The trees' "steep" view at 70° is past the 60° cap: retire it, or keep it as a named stress view. The far stop at 320 m is above the greybox's ceiling but inside the game's ladder.

### What the building blocks must carry

1. A coarse camera hull per thing at every date, from its lifespan, each part tagged solid, thin or foliage.
2. The open-space record: lanes and stairs as tubes (centreline, width, eaves, slope, nosing line), squares and landings as places, doorways and passages with their outside and inside poses.
3. The town's height field on the CPU, smoothed, redrawn when the town changes.
4. No-go volumes, a public or private flag per open space, and unbuilt faces flagged so tests can find them.
5. Framing data per thing: the interface study's label anchor and screen bound, plus a front for lead room and its best sides.
6. Dated vantages from the town plan's sightlines and a best-view search.
7. Each part's closest approach and largest screen size from the reach bake, feeding its tiers.

### Tests that would prove it

1. *Paths in the motion sheet.* A glide along Low Terrace at the street stop; a climb of Gully Steps at eye level; a crane from eye level to the city camera; an orbit at 12 m; a zoom into a lane from above. Measured: the near plane never inside the hull, the standoff kept, wall flow under 90° a second, no jerk spikes, frame time throughout.
2. *A sweep:* ten thousand random reachable poses and walks in the corner. No pose inside anything, no pixel of an unbuilt face, every hint visited.
3. *The reach bake* under three rules: eye level on all public ground, the street stop as the floor, eye level everywhere.
4. *Playtests,* run by the protocol in `docs/research/playtesting.md`: Øystein first, then strangers and beginners. Camera tasks: the quay to the landing; follow a person up the steps; the city camera to D's door; find a remembered view again. Measured: time per task, moments of fighting the camera (the pre-mortem's warning), a sickness rating after fifteen minutes, and a log of heights, tilts and time per stop. Little time at eye level would be evidence for item 8 too.
5. *Lens shift:* tilted against shifted, partly and fully corrected, at eye level and the street stop, in three lights; a strict review.
6. *Composition:* frame-this poses against random reachable poses of the same thing, read by cold readers. Does the composed view read the history better (criterion 1)?
7. *Hold:* a jump in years leaves the camera's matrices bit for bit the same.

What would change our minds:
- players fight the walker and ask to hop roofs: the drone wins;
- the 60° cap hides things players need: the cap rises;
- the lens shift looks wrong in motion: the camera tilts plainly.

## What we should do

Ranked by what each buys for its cost. Days are Opus working days.

1. *Build the greybox camera* on the clay corner. It needs the ladder, the height rule, collision and standoff on a hull from the clay masses, springs, controls for mouse, keyboard and pad, stops, hold, go-there and a pose log. Two to three days. Buys the first time anyone moves through the town (pre-mortem, story 8).
2. *The generator's camera data* in the corner's export: hull, lane and stair tubes, thresholds, no-go volumes, the height field. A day to a day and a half. Buys hints from facts in every later town.
3. *Paths and checks* in the motion sheet and the harness (tests 1 and 2). A day.
4. *The first playtest* with Øystein, walker against drone, both eye-level lenses. Half a day plus his time.
5. *The reach bake* on the corner (test 3). A day. Buys the numbers for item 8.
6. *Lens-shift frames* and a strict review. Half a day.
7. *Frame this, watch and vantages,* once the greybox shows they are wanted. Two days.
8. *The camera's needs in the architecture* (the list above). Half a day inside that session.
9. *One doorway hand-over* to a placeholder room, in 1g if it fits, else at step 5. Half a day.
10. *The rules where they apply:* the views in `docs/visual-direction.md`, the judging views' lenses and the steep tree view in `docs/foundations.md`, the coverage in `docs/systems.md`. Not done here, by instruction. Half a day.

## For Øystein to decide

1. *How the camera moves low in the lanes (play).* Recommended: a walker. Below the eaves it slides along walls and climbs the stairs; it crosses roofs only when zoomed above them. The other way is a drone that rises over any house it meets. Both go into the greybox for you to play.
2. *The camera as a witness (play).* Recommended: an act counts as "you saw" only when the camera was where a person could stand. That means public ground, from eye level to the street stop, or a public lookout such as Watch Knoll. From higher, people are marks, and their acts reach the journal only through the town's other channels.
3. *Vantages (play and taste).* Recommended: found, never marked. When the player stops near one the camera settles into it gently, and an option turns that off.
4. *How far eye level reaches (scope).* Recommended: all public ground, never private yards or behind houses, with the 1 m standoff. The reach bake and the gully port's costs confirm or overturn it.

## Gaps

- The shared search budget ran out partway through. GDC Vault was down, so Nesky's talk was read through a Russian translation and a summary. The Naughty Dog, Insomniac and Santa Monica camera talks, the Kentucky Route Zero, Firewatch and Disco Elysium talks, and Super Mario Odyssey's camera volumes were not reached.
- No source was reached on alley cameras in Assassin's Creed, Hitman or Uncharted, or on Sable, Outer Wilds, XCOM, Diablo, Mimimi's games and Pillars of Eternity's occluders.
- For Baldur's Gate 3, only its controls and one reconstruction of its occlusion were reached, nothing on the Lower City or the hand-over to dialogue.
- Football Manager's camera heights, Disco Elysium's angle and zoom, and Townscaper's tilt curve were not found.
- The elevations behind canonical views were not read in the originals, and Amirshahi and colleagues only through an abstract.
- The vantages of Stålenhag, Hasui and Hammershøi are our reading of the works.
- No study was found on how much camera lag feels good, and no game that uses a lens shift.
- How the camera feels can be tested only with people; model readers can judge frames and paths, never comfort or control.

## Sources

Composition, painting and film: [Edward Hopper](https://en.wikipedia.org/wiki/Edward_Hopper) · [Nighthawks](https://en.wikipedia.org/wiki/Nighthawks_(Hopper)) · [Early Sunday Morning](https://en.wikipedia.org/wiki/Early_Sunday_Morning) · [Vilhelm Hammershøi](https://en.wikipedia.org/wiki/Vilhelm_Hammersh%C3%B8i) · [Kawase Hasui](https://en.wikipedia.org/wiki/Kawase_Hasui) · [Simon Stålenhag](https://en.wikipedia.org/wiki/Simon_St%C3%A5lenhag) · [One Hundred Famous Views of Edo](https://en.wikipedia.org/wiki/One_Hundred_Famous_Views_of_Edo) · [Yasujirō Ozu](https://en.wikipedia.org/wiki/Yasujir%C5%8D_Ozu) · [Rear Window](https://en.wikipedia.org/wiki/Rear_Window) · [Playtime](https://en.wikipedia.org/wiki/Playtime_(film)) · [Roy Andersson](https://en.wikipedia.org/wiki/Roy_Andersson) · [Panoramic map](https://en.wikipedia.org/wiki/Panoramic_map) · [Isometric video game graphics](https://en.wikipedia.org/wiki/Isometric_video_game_graphics) · [Perspective control lens](https://en.wikipedia.org/wiki/Perspective_control_lens) · [OP-32, Free TV Australia](https://www.freetv.com.au/wp-content/uploads/2019/08/OP-32-Outside-broadcast-requirements-for-rugby-league-rugby-union-and-soccer-Issue-4-January-2015..pdf) · [World Cup camera angles](https://whyisthisinteresting.substack.com/p/the-world-cup-camera-angles-edition) · [Palmer lab, spatial composition](https://palmerlab.berkeley.edu/spatial.html) · [Blanz, Tarr and Bülthoff 1999](https://pure.korea.ac.kr/en/publications/what-object-attributes-determine-canonical-views/) · [Held et al. 2010](https://pmc.ncbi.nlm.nih.gov/articles/PMC3088122)

Games: [Disco Elysium dev blog, GameBanshee](https://www.gamebanshee.com/k4fuh) · [Firewatch field of view, Panic](https://help.panic.com/firewatch/fov/) · [The art of Firewatch, Thumbsticks](https://www.thumbsticks.com/gdc-2015-the-art-of-firewatch) · [How Townscaper works](https://www.gamedeveloper.com/game-platforms/how-townscaper-works-a-story-four-games-in-the-making) · [Tiny Glade camera, Game Rant](https://gamerant.com/how-to-control-the-camera-in-tiny-glade/) · [Tiny Glade first person, 80.lv](https://80.lv/articles/cozy-castle-builder-tiny-glade-now-has-a-first-person-view-mode) · [Tiny Glade, Steam thread](https://steamcommunity.com/app/2198150/discussions/0/4844273660401824389/) · [ACME camera mod](https://github.com/algernon-A/ACME) · [CSkyL](https://github.com/Asu4ni/CSkyL) · [Cities: Skylines II photo mode](https://www.paradoxinteractive.com/games/cities-skylines-ii/features/cinematic-camera-photo-mode) · [CS2 first-person mod](https://github.com/Cities2Modding/FirstPersonCamera) · [Free Range Camera](https://github.com/algernon-A/FreeRangeCamera) · [Manor Lords preview, TechRadar](https://www.techradar.com/gaming/manor-lords-preview-camera-feature-brings-you-down-to-earth) · [FreeSO](https://github.com/riperiperi/FreeSO) · [Baldur's Gate 3 controls, bg3.wiki](https://bg3.wiki/wiki/Controls) · [Baldur's Gate 3 occlusion, 80.lv](https://80.lv/articles/artist-recreated-baldur-s-gate-3-occlusion-cutout-effect) · [Pillars of Eternity](https://en.wikipedia.org/wiki/Pillars_of_Eternity) · [Kingdom Come: Deliverance](https://en.wikipedia.org/wiki/Kingdom_Come:_Deliverance) · [Kentucky Route Zero, Inverse](https://www.inverse.com/gaming/video-games-drama-final-fantasy-kentucky-route-zero/amp) · [Theatrical spaces](https://bulletpointsmonthly.com/2020/03/18/theatrical-spaces) · [Kentucky Route Zero, Vice](https://www.vice.com/en/article/aeepwk/notes-from-gdc-kentucky-route-zero-and-the-theatre-of-games) · [The art of Pentiment](https://www.gamedeveloper.com/art/deep-dive-the-art-of-pentiment) · [Hitman shoulder, Hitman Forum](https://www.hitmanforum.com/t/aiming-issue-shoulder-view/10755) · [Hitman 3 shoulders, Gfinity](https://www.gfinityesports.com/article/hitman-3-how-to-change-shoulders-xbox-ps4-ps5-pc-stadia) · [RDR2 cinematic camera, Mein-MMO](https://mein-mmo.de/en/red-dead-redemption-2-kinokamera-fails,284278) · [Super Mario 64 camera.h](https://raw.githubusercontent.com/n64decomp/sm64/master/src/game/camera.h) · [Metroid Prime's camera, Nintendo Life](https://www.nintendolife.com/news/2022/05/ex-retro-studios-devs-laud-metroid-primes-camera-system)

Camera craft: [Nesky, 50 mistakes, part 1 (Habr)](https://habr.com/ru/post/272401/) · [part 2 (Habr)](https://habr.com/en/articles/272825/) · [talk summary](https://videohighlight.com/v/C7307qRmlMI) · [Nesky, Game Developer](https://www.gamedeveloper.com/design/video-50-common-game-camera-mistakes----and-how-to-fix-them) · [Real-Time Cameras, contents](https://www.routledge.com/Real-Time-Cameras-A-Guide-for-Game-Designers-and-Developers/Haigh-Hutchinson/p/book/9780429258190) · [Navigation and occlusion, excerpt](https://www.gamedeveloper.com/design/real-time-cameras---navigation-and-occlusion) · [Foreword](https://www.gamedeveloper.com/programming/-real-time-cameras-and-mark-haigh-hutchinson) · [Scroll Back, Keren](https://www.gamedeveloper.com/design/scroll-back-the-theory-and-practice-of-cameras-in-side-scrollers) · [Cinemachine 3.1 manual](https://docs.unity3d.com/Packages/com.unity.cinemachine@3.1/manual/CinemachineDeoccluder.html) · [Cinemachine source](https://github.com/Unity-Technologies/com.unity.cinemachine) · [Spring-It-On, Holden](https://theorangeduck.com/page/spring-roll-call) · [Mathf.SmoothDamp](https://docs.unity3d.com/ScriptReference/Mathf.SmoothDamp.html) · [Lens shift, Unity](https://docs.unity3d.com/6000.0/Documentation/Manual/PhysicalCameras-LensShift.html) · [Physical cameras, Unity](https://docs.unity3d.com/6000.0/Documentation/Manual/PhysicalCameras.html) · [de Vries et al. 2007](https://www.ieda.ust.hk/dfaculty/so/pdf/Pages89-95-VIMS2007.pdf) · [XAG 117](https://learn.microsoft.com/en-us/gaming/accessibility/xbox-accessibility-guidelines/117) · [Game Accessibility Guidelines](https://gameaccessibilityguidelines.com/full-list/) · [Virtual Cinematographer](https://www.microsoft.com/en-us/research/publication/the-virtual-cinematographer-a-paradigm-for-automatic-real-time-camera-control-and-directing/) · [Toric space, Lino and Christie 2015](https://history.siggraph.org/?p=112722)
