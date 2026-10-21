# Painted marks in motion

How to keep a painted look stable when the world moves and changes: the camera gliding and pulling out, trees in wind, water, smoke, people, doors and windows that open, things that change over the years, and the hand-over between distance tiers. Our style rests on painted marks (`docs/visual-direction.md`, "true up close, painted from afar"), and two studies have already found the problem without studying it: the colour and shading study notes that stroke textures swim unless fixed to the world, and the characters study found that our brush is fixed to the world and would slide on a moving body (`docs/research/characters.md`, section 1). This study covers the research on temporal coherence in stylised rendering, how games and films keep marks on moving things, marks across distance and anti-aliasing, and the cost on our reference machine. It ends with our own shaders against all of it, one rule for where a mark lives, and what every part must carry.

Claims taken from a summary or a third party are marked (secondary); claims we could not confirm are marked (unverified). Numbers we worked out are marked (our arithmetic). The shared web-search budget ran out partway through the research, so some games and films are thinly covered; the gaps say which. Many talks sit behind GDC Vault's login, and the HAL archive and the ACM library sat behind bot walls; where a paper was read from another copy, it is still primary.

## In short

1. **The field knows the trade, and has measured which side matters.** Bénard, Bousseau and Thollot's survey names three goals that cannot all be met: marks that look flat on a canvas, marks that move with the scene, and no flicker. A mark fixed to the screen is flat but slides over the world (the "shower door"); a mark fixed to the surface moves right but grows and shrinks with distance. In the same group's user study, motion coherence tracked how pleasant viewers found the result (Kendall τ = 0.58). Marks belong on the thing, with their screen size controlled by levels.
2. **Every production that kept strokes stable stored them in the thing's own space.** Deep Canvas stored each stroke as a surface and its u and v; DreamWorks' stamp maps sit "in reference space"; Klaus's grain "travels with the character"; Spider-Verse's comp marks read 3D UV positions from a render pass. Guilty Gear Xrd's inner lines are texels in UV space. Obra Dinn's dither, pinned only to camera rotation, still swims when the camera travels.
3. **Our marks are fixed to the world, and that is right only for things that never move.** `OS_Brush`, the bark's lichen and mottle, and the leaves' cut-out dither read world or screen position. The moment wind, a hinge, a skeleton or a regenerated part moves a surface, its marks slide. Wind is the first to arrive.
4. **One world size cannot serve our camera.** Our 70 cm stroke spans about 1,450 pixels at eye level and 4 at 400 m (our arithmetic). Up close it is a smear; far off its 10 cm cross-stroke detail is half a pixel, aliases and crawls as the camera glides. The research answer is a stroke field anchored to the surface whose scale steps by octaves with distance, so marks stay within a factor of two on screen and fade to their mean before they alias.
5. **Our judging hides every one of these faults.** Every judged frame is a still rendered at twice the size and averaged down (`LT1Render.Still`). Supersampling smooths shader aliasing and per-pixel jitter, and footprint-driven fades sit at one and a half times the distance the player will see at 1440p. No mark of ours has been judged in motion.
6. **Anti-aliasing and upscalers decide where a mark may sit.** In Unity 6 URP, TAA and STP exclude MSAA, and transparent materials get no motion vectors. MSAA is cheap on the M4's tile-based GPU and fixes geometry only. So every mark must be stable on its own, band-limited by its footprint, and never rely on temporal accumulation.
7. **Full-screen painterly filters are out at runtime.** Anisotropic Kuwahara at full 1440p would cost tens of milliseconds on the M4, every neighbour-sampling pass breaks the tile GPU's merged render pass, and Japanese Unreal studios tried and dropped such filters as hard to direct and a constant cost. Painted marks belong in the materials, where they also hold under motion.

## 1. What the research knows

### The three goals

Bénard, Bousseau and Thollot's state-of-the-art report (Computer Graphics Forum, 2011) frames stylisation as marks (strokes, hatches, pigment) drawn over 2D primitives that depict a 3D scene. It names three goals and calls them "inherently contradictory":

| Goal | What it asks | What breaks it |
| --- | --- | --- |
| Flatness | the image looks made on a flat canvas: marks keep their size and spacing whatever the depth | marks fixed to surfaces grow and shrink with distance |
| Motion coherence | marks move with the scene's apparent motion | marks fixed to the screen: the scene seems seen through a sheet of marks, the "shower door", Meier's term (1996) |
| Temporal continuity | nothing changes abruptly from frame to frame | marks redrawn every frame flicker; marks that appear and vanish pop |

Plain texture mapping keeps motion and continuity and loses flatness. Static screen marks keep flatness and continuity and give the strongest shower door. Redrawing each frame gives flicker. Every method is a trade on these three axes. A user study in the same group's 2010 noise paper (below) found that motion coherence correlates with pleasantness (Kendall τ = 0.58); the report's conclusions call the two "strongly correlated" and judge motion coherence the goal most worth keeping. Flatness is the hardest to define.

The report also matches method to medium. Stochastic media (pigment, paper grain, canvas) survive the methods that blend scales. Near-regular marks (strokes, stipples) suffer badly under blending and suit methods that keep a few discrete marks. That is a direct input to our brush, which is a field of strokes in seeded directions, halfway between the two.

### Where a mark can live

| Family | How | Keeps | Loses | Real time on the M4 |
| --- | --- | --- | --- | --- |
| Screen fixed | a pattern on the image (paper, dither, hatching from pixel position) | flatness, continuity | motion: the shower door | free |
| Advected | an image-space texture pushed along motion or optical flow, regenerated now and then (Bousseau 2007; Kass and Pesare 2011) | flatness, mostly motion | continuity: drift, blending, distortion | Bousseau's takes seconds a frame; Kass and Pesare's is real time but isotropic noise only (secondary) |
| Per-object 2D pattern | a 2D pattern moved by each object's best-fit similarity transform (Breslav et al. 2007) | flatness | motion on long or turning objects | cheap: a CPU fit per object |
| Texture space, fixed scale | ordinary UV or object-space texture | motion, continuity | flatness | free |
| Texture space, scale by level | art maps and tonal art maps (Klein 2000; Praun 2001); fractalisation or "infinite zoom" (Bénard 2009) | motion, near-flatness | some contrast; structured marks blend visibly | cheap |
| Few discrete marks | particles on the surface, each drawing a 2D stroke (Meier 1996; Lu et al. 2010; Deep Canvas) | motion, flatness | continuity: strokes pop as they appear and change order | marginal at 1440p (below) |
| Many marks as noise | sparse convolution noise, Gabor kernels fixed in screen space at points fixed on the mesh (Bénard 2010) | all three, best balanced | stroke-level control | heavy fill; geometry shaders it was built on are not on Metal (unverified) |
| Image filters | Kuwahara, bilateral, XDoG on the finished frame | flatness | shows nothing in flat areas; flickers where its choices are hard | dear (section 6) |
| Example-based | patch synthesis or small networks guided by render passes (StyLit 2016; Jamriška 2019; Texler 2020) | the look of a painting | real time | seconds to minutes a frame (StyLit about 3 minutes a megapixel); Texler's network about 17 fps at 640 by 640 on an RTX 2080: for target frames only |

### The methods that matter to us

**Dynamic solid textures** (Bénard, Bousseau, Thollot, I3D 2009; read with its shader appendix). Coordinates come from object-space position, or the rest pose on a deforming mesh. The texture is a weighted sum of four octaves of one solid texture, sampled at scales a factor of two apart that are chosen by log2 of the camera depth. The weights hand each octave's share to the next, so the zoom cycles every time the apparent size doubles, and marks keep a near-constant screen size while staying attached. Fewer than four octaves made texels visibly appear and vanish. It cost about 10 percent over plain shading: four trilinear lookups a pixel. The authors list the price: a loss of contrast, structured textures visibly altered, distortion at grazing angles, and seams where neighbours at different depths sit at different points in the cycle. Four blended octaves keep about 0.55 to 0.62 of the original contrast, varying over the cycle, so contrast breathes unless renormalised (our arithmetic).

**Tonal art maps** (Praun, Hoppe, Webb, Finkelstein, SIGGRAPH 2001). Mip levels filtered one by one give "swimming strokes" as the camera comes and goes. Their mips keep strokes the same pixel width at every level; finer levels keep the tone by adding strokes into the gaps, and every stroke of a coarser level is in every finer one, so moving between levels changes a few pixels. The runtime cost is nothing; the cost is making the maps.

**The dynamic noise primitive** (Bénard and colleagues, EGSR 2010). Gabor kernels sized in screen space sit at points fixed on the mesh and seeded per triangle, so the same points come back every frame. Its level-of-detail rule is the one to copy: the target count N is rounded down to a power of two M, 2M points are drawn, and the second half fades in at a weight α with (1 + α²)M = N. Variance and spectrum hold through the change, so nothing pops and nothing loses contrast.

**Strokes as particles.** Meier (1996) fixed particles on the surface and drew each as a 2D stroke, so strokes stick to the object; spread evenly on the object they crowd far off and thin out close up, and changes in draw order pop (secondary, through Bousseau 2006 and OverCoat). Lu, Sander and Finkelstein (I3D 2010) ran it on the GPU with strokes that fade in and out as they are born and die: 60,000 strokes at 512 by 512 at over 30 fps on a GeForce 8800 GTS. At 1440p and that density, 500,000 to 800,000 blended sprites (our arithmetic).

**Watercolour and compositing.** Montesdeoca and colleagues (2017) paint effect strength per vertex in object space and keep pigment turbulence in the object's shader to avoid the shower door; their paper texture stays on the screen, and users asked for it to move. Garcia and colleagues (Eurographics 2021; project page only) anchor screen-space splats to a 3D grid over object positions read from the G-buffer, keep their density by fractalisation and fade them in and out: the closest paper to a game's pipeline, with no timings we could reach.

### Image filters, and why they flicker

The Kuwahara filter outputs the mean of whichever sub-region varies least. Kyprianidis, Kang and Döllner (2009) state why it flickers: the choice is unstable under noise or when two sub-regions tie, so near-ties flip between frames. Papari's generalised form (2007) blends sectors instead of choosing. The anisotropic form follows a smoothed structure tensor, and its authors report video filtered frame by frame as coherent with nothing added: 12 fps for 512 by 512 on a GTX 280. They say it suits a smooth look, not a "rough and brushy" one. Later timings at 512 by 512 on a GTX 480 were 5.6 ms with four sectors and 23 to 28 ms with eight (2010). The thread through all of them: flicker comes from discontinuous per-pixel decisions, and smooth weights, a smoothed tensor and soft thresholds cure it. A filter's brushwork is a function of the textures on screen, so it inherits their coherence and paints nothing on a flat wall.

## 2. How games keep the look in motion

**Return of the Obra Dinn** (Lucas Pope, Unity). A one-bit dither fixed to the screen shimmers as soon as the camera moves. Pope's devlog tried five fixes in turn (through a full translation, secondary). The pattern in each object's texels stuck, but its scale differed between objects and it would not filter. Per-pixel reprojection tore. An offset driven by camera rotation was exact only at the centre and chaotic on floors. A world-aligned cube round the camera failed at its corners. He shipped a sphere round the camera, tuned by hand, thresholded at twice the resolution and averaged down against moiré. Dithering is "not a technology that you want to use in a moving picture", he said, and he did not fix everything (Game Developer interview). The sphere pins the pattern when the camera turns, not when it travels (Johansen, secondary). Our camera mostly travels.

**Surface-stable dithering** (Rune Skovbo Johansen, Unity, 2024 and 2025; his page and code). Dots live in UV space and keep a roughly constant screen size by adding dots as a surface nears and removing them as it recedes, from self-similar Bayer levels in a 3D texture, under the tonal art maps' rule: growing, no dot vanishes; shrinking, none appears. Dots still get cut at transitions and stretch towards the screen's edges. It is the clearest public answer for a camera that travels.

**Guilty Gear Xrd** (Arc System Works; Motomura, GDC 2015, and the studio's own lecture). Outlines are an inverted hull pushed out along a second set of normals stored in the tangent slot, because vertex colours do not follow the bones. The push grows with camera distance times tan(FOV/2), so a line keeps its screen width from close-up to long lens. Inner lines are axis-aligned runs of texels with the UVs laid straight along them, crisp in close-up and fixed to the deforming body (secondary, through summaries of the handout). Marks on a body live in its own space, and a mark's screen size is a designed value.

**Hi-Fi Rush** (Tango Gameworks; GDC 2024 abstract, Epic Games Japan's slides). A deferred toon renderer at 60 fps; the shadow hatching was "added into Ambient Occlusion pass", so it rides on a lighting buffer, not the final colour. Outlines for all but the characters are a post-process (secondary). Where its halftones live could not be confirmed.

**Genshin Impact** (miHoYo, Unity Dojo 2021). Its console work aimed at stability: reflections get a temporal filter, fog is blended across frames "to increase stability", and "more stability" is still on the list.

**Sable** (Shedworks). Lines fade with distance; before the fade, objects would "just pop in". Fog was "really, really key" for the middle and far distance (Kythreotis, Game Developer).

**Firewatch** (Campo Santo, Unity; Jane Ng's GDC 2016 slides with notes). Wind response painted into vertex colour, one channel for sway and one for flutter. A shader lowers the leaves' alpha cutoff with distance: "This makes the tree more puffy looking when it's far." The far crown is drawn fuller and softer on purpose.

**Disco Elysium** (ZA/UM; Rostov's devblog, in `docs/research/lighting-and-colour.md`). A light map per hour was dropped because it "tended to overwrite any hand painted brushwork"; one painted image per scene is dimmed and coloured by a shadow render and a lightfield map. The marks never move; light moves over them.

**Sea of Thieves** (Ang et al., SIGGRAPH 2018). The foam buffer is blurred with feedback over frames "for a softer, more in-style mask"; distant clouds are thresholded to sharpen their edges, so the far sky reads drawn.

**Breath of the Wild** (CEDEC 2017, through a translated summary, secondary). Distance in three layers, objects simplified with distance because full detail "appeared cluttered and messy". No developer source confirms the brush filter players describe on distant terrain (unverified).

**Okami** lays a paper texture over the screen (secondary). It is the medium, so fixing it to the screen is honest. **3D pixel art** (David Holland) stops pixels creeping by snapping the camera to a texel grid and shifting the image by the snap error, which works only for orthographic travel.

### Painterly post-processes

Public anisotropic Kuwahara filters exist for Unity and Godot (Acerola's; a Godot port with eight sectors; Maxime Heckel's, who moved to polynomial weights because Gaussian ones were "quite expensive"). None publishes timings, and we found no shipped game that runs one over the whole screen in play. Epic Games Japan's survey of Japanese Unreal titles reports that studios tried hatching, Kuwahara, bilateral and posterising filters and dropped most of them: "no one-fits-all solution", hard tuning, and a "constant GPU cost" (slides, pp. 65 to 68). A hatch drawn from pixel position, as in Heckel's Moebius-style pass, is the shower door in its plainest form.

### Temporal anti-aliasing and upscalers

The vendors agree on where marks may sit. Unreal's TSR ghosts on panning or animated materials, which "lack any motion vectors", and Epic Games Japan found it blurs strongly when the camera moves in stylised titles. AMD's FSR 2 puts film grain, vignette and tonemapping after the upscaler and asks for vertex animation in the motion vectors and animated textures in a mask. Apple's MetalFX runs before post effects, with noise and particles drawn after it (WWDC 2022). So a mark fixed to a surface that writes correct motion reprojects; a mark fixed to the screen, or a texture that changes while its surface stays put (scrolling water, a flow map, a flipbook), smears or flickers under any temporal pass.

| Game or method | Where the marks live | How motion is handled | What it cost or accepted |
| --- | --- | --- | --- |
| Obra Dinn | a sphere round the camera | pinned when turning, swims when travelling | 800 by 450; threshold at double resolution |
| Surface-stable dither | UV space, self-similar levels | dots added and removed to hold screen size | dots cut at transitions |
| Guilty Gear Xrd | hull in mesh space; inner lines as texels in UV | width from distance and FOV | a second draw; hand-laid UVs |
| Hi-Fi Rush | hatching in the occlusion buffer | toon passes in deferred post | 60 fps |
| Firewatch | painted textures; wind in vertex colour | cutoff lowered with distance | 23 trees in all |
| Disco Elysium | one painted image per scene | marks hold, light moves | a fixed camera |
| Okami | paper on the screen | it is the medium | toned down on Wii |
| Kuwahara post | the finished image | smooth weights, smoothed tensor | constant cost; nothing on flat areas |

## 3. What film and animation do

**Deep Canvas** (Disney, *Tarzan*, 1999; its patent, US 6,268,865). Painters painted strokes over a 3D scene, and each stroke point was stored as a surface and its exact u and v, with a normal and a width in the surface's own frame, so strokes survive animated surfaces. Each frame the points are recomputed, projected through the new camera and repainted with the same brush; a width narrows as its surface turns away, capped near edge-on. Leaf strokes were mapped into a plane facing the camera, pivoting on their first point, as our leaf cards are. Stroke order is blended between painting order and depth order so changes do not pop, though the patent admits strokes "do not conform accurately to the surfaces" and order changes "may cause a pop". It painted backgrounds only.

**Paperman** (Disney, 2012; Whited et al.). Hand-drawn lines were carried between frames by motion fields rendered from the 3D scene. Silhouettes turning out of plane and limbs crossing the body broke it. A paper texture rode the same fields, with a "boil" setting for how much it changed over time, so the amount of boil was chosen.

**Spider-Verse** (Sony Pictures Imageworks, 2018 and 2023). Halftones and hatching were made largely in compositing, dot size following the light (Foundry). The lead compositor's rule: rim-light dots must track the character, or "he'll appear to be swimming through a pattern". The Patcher tool's patent shows how: a render pass stores 3D UV positions in its colour, so strokes cut from it track geometry. Ink lines live in a UV space per character; texture maps alone failed because the jawline stopped matching as the head turned (fxguide). On the second film, lines draw on and erase off as a surface turns, and paper texture is dissolved between two projections so it "never looks like it's locked on" (befores & afters). Characters ran mostly on twos while simulation ran on ones, which needed its own pipeline layer (Oskarsson and Chazot, SIGGRAPH 2023).

**Arcane** (Fortiche, 2021 and 2024). 3D characters carry painted textures and an overlay of painterly strokes, and smoke and fire were drawn by a 2D effects team (Cartoon Brew, VFX Voice; secondary). How its faces keep their brushwork from swimming could not be confirmed.

**Klaus** (SPA Studios, 2019). Light was built in layers under the line art and carried by tracking the lines. Texture "actually travels with the character", subtle and computed, never re-rolled each frame (befores & afters; Les Films du Poisson Rouge).

**Puss in Boots: The Last Wish** (DreamWorks, 2022; Mark Edwards). Painted images are projected onto a point cloud round each object in reference space: "It's temporally coherent, because it's in reference space." It works on characters too. "We can't have stuff shifting on the edges." Stamp strength is set by distance.

**The Wild Robot** (DreamWorks, 2024; Jeff Budsberg). "If you want a painterly bush, paint the bush": foliage is drawn as 3D strokes and rigged, so it moves in wind. Fur shows no fibres; accents appear only where light falls. Distant birds "almost look like blobs of paint", on simple rigs that must stay "temporally stable" (befores & afters).

**The Mitchells vs. the Machines** (Sony, 2021; Mike Lasker). A mapped look is "the kiss of death". The stroke layers are fixed and light moves through them, so shadow strokes "built up and fell away" as a light circled a face. Distant characters get larger strokes.

**Mutant Mayhem** (2023). Pencil lines are 3D ribbons whose shader holds their width with distance; without it they went "invisible after 30 meters". Stepped 2D effects must not strobe under a handheld camera.

**Loving Vincent** (2017). Each shot was painted on one canvas, frame over frame: about 65,000 frames by 125 painters. Strokes boil wherever anything moves. It is the one production that accepts full boil, because the film is its paintings.

**Background painting.** Classical animation painted the background once a shot and drew what moves simply on cels over it; the multiplane camera moved planes at different speeds so distant things did not grow as the camera came in (secondary).

**Rest position.** Houdini stores undeformed positions so "procedural textures stay put on the surface as it deforms"; Blender's generated coordinates do the same; RenderMan calls it Pref. In real time the bind pose is the rest pose.

What the productions agree on:
1. A mark that describes a thing lives in the thing's own space. Only lens and medium marks (grain, paper, misregistration) live on the screen.
2. A mark's screen size is designed: capped as a surface turns away, held by formula, enlarged for distant figures, tuned by distance.
3. Light moves through fixed marks; marks do not move with the light.
4. What must change with the view (silhouettes, lines, cards) changes by fading, not sliding.
5. Boil is a low, seeded dial or the whole medium, never free-running noise. Faces and silhouettes are where the eye catches swimming first.
6. The performance may step; the camera and simulation run on every frame.
7. What moves carries fewer, larger, steadier marks than what holds still.
8. Drawn effects break apart rather than fade (Turning Red's smoke subdivides; secondary, VFX Voice).

## 4. Marks on things that move and change

| Kind | Where its marks live | The craft | Cost |
| --- | --- | --- | --- |
| Static fabric and ground (walls, steps, setts, rock, roofs, the ground) | the world, or the part's own frame, which is the same while it holds still | as now | none |
| Rigid movers (doors, sashes, shutters, hatches, hanging signs, lanterns, boats, carts, cars) | the object's own space | a world-fixed mark stays put while the door swings through it, so its grain swims; weather that falls on it now (rain's direction, the waterline) stays in the world | none |
| Skinned bodies (people, animals) | the rest pose | Unreal ships a pre-skinned local position for exactly this; Unity has no node, so the bind-pose position goes in a spare UV channel (`Mesh.SetUVs` takes three or four floats in channels 0 to 7), with the rest normal if marks are projected | 12 bytes a vertex, 6 at half precision |
| Cloth, flags, laundry, ropes | UV space: a garment's pattern pieces are its rest shape | marks in UV hold under simulation by construction | none |
| Trees, shrubs, grass in wind | the position before the wind moves it, or each element's frame | the vertex shader passes the undisplaced position through before adding the wind; Pivot Painter's per-element pivots keep branch-local coordinates constant as branches turn | one interpolator |
| Leaf cards and other camera-facing cards | the card's own UV | painted once per card; lit by the mass, not the card (Peterson and Lee's aggregate normals, SIGGRAPH 2006, used on *Over the Hedge*); a card's turn to the eye changes by fading, never by a flip | none |
| Still water (the harbour) | the world, moved by the clock | ripples are the water's own; a lamp's column breaks by the wind field's slopes (`docs/research/animation-and-motion.md`) | as now |
| Flowing water (run-off down a lane, a beck, a tide race) | a flow map over the world | two layers half a phase apart, per-pixel phase noise against pulsing, strength scaled by speed (Vlachos, Portal 2, SIGGRAPH 2010) | 2 fetches and 21 instructions over two scrolled normal maps |
| Smoke, steam, splashes | a flipbook on a card fixed in the world | frames held on twos while the card travels smoothly; shapes break up rather than fade; light from six-way maps | Unity's six-way output costs about a lit sprite; VFX Graph needs compute |
| Rain and snow | the world, drawn where light is | as `docs/research/animation-and-motion.md` | as there |
| Things that change over years | the part's own frame, anchored at a point that does not move when it changes | U in metres along a member from its start, V across; an extension adds new U range and never moves old texels; seeds from the part's identity, never from vertex order or build order | none |

Notes on the harder rows.

**Trees.** SpeedTree's game wind sways the whole tree slowly, one or two branch levels faster and leaves fastest, rippling leaf vertices along their normals (SpeedTree manual). Pivot Painter 2 stores each element's pivot, axes, parent and depth in textures read through one UV set, up to 30,000 elements (Epic documentation). For marks the point is simple: anything sampled at the moved position slides over bark and leaves; anything sampled before the move rides with them.

**Flowing water and smoke.** Vlachos's flow map runs at about 4 texels a metre, made by a tool because it cannot practically be painted; in Left 4 Dead 2 playtests, visible flow cut wrong turns by 17 percent. Unity's VFX Graph plays flipbooks unblended, linearly blended or blended by motion vectors (Lozar stretched a 64-frame sheet more than ten times that way; secondary). A drawn look wants frames held, unblended, while the card travels smoothly, as Spider-Verse played its drawn explosions on twos from sprite sheets (SideFX, secondary). Neither a flow map nor a flipbook moves its surface, so neither writes motion vectors (section 5).

**Changing shapes.** The test is regeneration: when a generator rebuilds a house from its diary after an extension, every part that did not change must come out with the same mark coordinates and seed, or its marks jump although nothing happened to it. Ptex avoids UVs altogether but needs custom filtering in Unity (unverified); metric UVs from a stable origin and trim strips that tile along their length do the job for our parts.

## 5. Marks across distance

### What our brush becomes on screen

At 1440p with the street stop's 35 mm lens a pixel spans about 0.48 mm per metre of distance (`docs/research/performance-at-scale.md`). Our brush (`OS_Brush`) lays strokes about 70 cm long in patches about 71 cm square, with detail across each stroke on a lattice of about 10 cm (our reading of the shader).

| Distance | A 70 cm stroke | The 10 cm cross-stroke lattice |
| --- | --- | --- |
| 1 m (eye level) | about 1,450 px, the screen's height | 210 px |
| 5 m | 290 px | 42 px |
| 10 m (street stop) | 146 px | 21 px |
| 20 m | 73 px | 10 px |
| 80 m | 18 px | 2.6 px |
| 120 m (far stop, longer lens) | about 17 px | 2.5 px |
| 400 m | 3.7 px | 0.5 px |

(our arithmetic; face-on. On the lane's ground seen from the street stop, 2.8 m up, the footprint along the view grows with distance over height, so the cross-stroke lattice falls under two pixels by about 17 m.)

A single world size spans a factor of 400 on screen across our camera's range. A painter's stroke is sized to the canvas: the far hill and the near door get marks of similar size on the picture. The research's answers keep the mark attached and hold its screen size in a band:
- **Levels that nest** (tonal art maps; surface-stable dithering): each finer level only adds marks, so moving between levels changes a few pixels.
- **Octaves cycled by distance** (dynamic solid textures): sample the field at two or more scales a factor of two apart and cross-fade by the fractional part of log2 of the footprint. Cheap; costs some contrast, which can be renormalised.
- **Discrete marks by screen area** (the dynamic noise rule): the count follows screen area in powers of two, the extra half faded in with a weight that keeps the variance.

### Band-limiting what the shader draws

Inigo Quilez's rule for procedural detail: take the filter width w from the pixel footprint of each octave's coordinate (`fwidth`), and fade each octave by `smoothstep(1.0, 0.5, w)`, doubling w per octave, so nothing oscillates more than about once a pixel. Distance-based fades break under domain warping; footprint-based ones do not. MSAA does not help: it "doesn't fix shader aliasing" (Unity manual). Our footprint is already measured as the larger of the two screen derivatives of position, which captures a grazing view correctly.

### Mips of painted textures

Ordinary mips average strokes into their mean, so a painted texture loses contrast as it recedes until its marks are gone; levels filtered one by one swim (Praun et al.). For cut-outs, coverage must be kept per mip or foliage thins with distance: Castaño's method scales each mip's alpha so the share passing the cutoff matches the top level, built into Unity as `mipMapsPreserveCoverage`, which our importer already sets for the sprays. Firewatch's lowered cutoff is the stylised alternative: far crowns drawn fuller on purpose.

### Hand-over between tiers

URP's LOD cross-fade dithers in a Bayer, blue-noise or stencil pattern (Unity 6 manual). The pattern is fixed to the screen, so without TAA it reads as a screen door while the fade runs, and crawls if the camera moves during it (unverified as seen; it follows from the method). Three rules make a hand-over invisible:
1. Both tiers draw the same marks, read in the same space from the same field and seed, so the fade changes only geometry (`docs/research/materials-at-scale.md`: the same data at every tier).
2. The switch sits where the two tiers match in value, measured.
3. Fades are short and happen where the marks are already near their mean.

### Anti-aliasing

Today we run MSAA 4× with no temporal pass. In Unity 6 URP, TAA cannot be combined with MSAA, Camera Stacking or dynamic resolution; its Base Blend Factor trades anti-aliasing against ghosting and its Variance Clamp trades ghosting against flicker. STP, Unity's temporal upscaler, needs compute (Metal on Apple silicon qualifies, by the documentation's wording) and turns TAA on even at full resolution. FSR 1 is spatial and keeps MSAA. MetalFX is not among URP's upscaling filters. Motion vectors come only from opaque and alpha-clipped materials with a motion-vector pass; vertex animation needs its own. So under TAA or STP, our transparent water and smoke, any flow map or flipbook, and any wind without a motion-vector pass would ghost or flicker.

## 6. What it costs on the M4

The M4's 10-core GPU gives about 3.8 TFLOPS (secondary, Wikipedia) and 120 GB/s of memory bandwidth (Apple). At 1440p, a millisecond of GPU time is about a thousand floating-point operations a pixel at peak (our arithmetic). It draws in tiles, which changes the prices:
- Hidden surface removal is "pixel perfect and submission order independent", but a shader that discards or writes depth sends the GPU back to it; draw opaque first, then alpha-tested, then blended (Apple, WWDC 2020).
- Blending happens in tile memory; MSAA samples stay on chip and resolve on store, so MSAA is cheap.
- Unity's Render Graph merges passes into one native pass on tile GPUs. A pass that reads the previous pass's output as a texture, or changes resolution, ends the merge (Unity's SRP source, `PassBreakReason`). Framebuffer fetch reads only the current pixel.
- Each full-screen pass that leaves the tile reads and writes the frame: about 59 MB in half-float colour, a floor of about 0.5 ms at peak bandwidth, 0.25 ms in 8-bit colour (our arithmetic).

| Technique | Cost at 1440p on the M4 | Verdict |
| --- | --- | --- |
| A procedural brush field in the material, two octaves | a few hundred instructions a pixel at most: well under a millisecond (our estimate) | yes |
| Rest position in a UV channel | 12 bytes a vertex | yes, on everything that deforms |
| Undisplaced position for wind | one interpolator | yes |
| Tonal-art-map style nested levels | memory and authoring | yes, where a mark is a texture |
| Flow-mapped water | 2 fetches and 21 instructions more | yes, where water flows |
| Flipbook smoke, six-way lit | about a lit sprite | yes |
| Alpha-tested cards | defeat hidden surface removal | keep their screen coverage small; far crowns as fewer, larger cards (`docs/research/performance-at-scale.md`) |
| Stroke particles over the screen (Lu et al.) | 500,000 or more blended sprites at full density | no, beyond perhaps one far layer |
| Gabor-noise marks | heavy fill; built on geometry shaders | no |
| Anisotropic Kuwahara, 4 sectors, full resolution | about 25 ms; 8 sectors about 90 ms (our scaling of the published timings) | no |
| Kuwahara at half resolution, radius 3 | about 2 to 7 ms, plus a broken native pass (our estimate) | only as an experiment for the far tier |
| A per-pixel colour pass (the palette) by framebuffer fetch | stays on tile, under the pass floor; today `Palette.shader` is a blit and pays the floor | yes |
| A temporal history buffer (TAA, STP) | another half-float frame read and written, about 0.5 ms floor, plus its passes | only if the frame needs upscaling |
| Example-based stylisation | seconds a frame | for target frames only |

## 7. Our look against this

### What we do right

- **The town's marks are fixed to the world, never to the screen.** `OS_Stroke`, `OS_Brush` and `OS_Carve` say so in their comments. For standing things that is the right default, and it is how Disco Elysium and Deep Canvas held their brushwork.
- **History and material marks live in the piece's own plane** (`Growth.hlsl` reads `q`, the stone's piece-local metres in UV0). They ride with a piece wherever it is, and move into history maps with tiers unchanged (`docs/research/materials-at-scale.md`).
- **Fades by footprint, measured the right way.** `OS_Near`, lichen resolving to a film, setts to their mean tone, the water's chop flattening with distance: the band-limiting rule, already followed by most of the stone. The footprint is the larger screen derivative of position, so a grazing view counts.
- **Light moves through fixed marks.** The brush nudges the light's ramp as well as the colour, and the leaves are lit by their masses' planes, never by the cards (the Mitchells' and Disco Elysium's rule; Peterson and Lee's aggregate normals).
- **Foliage painted in UV, kept whole with distance.** The sprays are painted per card in their atlas (`blender/parts/trees/painting.py`, supersampled), their mips keep coverage, alpha-to-coverage sharpens the edge to a pixel, twigs are never drawn thinner than a pixel and motes never smaller than one.
- **Everything moves by the clock** (`_OS_Time`, the clouds' drift), never frame time, so any moment can be rebuilt.

### Where our marks will swim or pop

1. **The brush slides on anything that moves.** `OS_Brush` (`StreetLooks.hlsl`) reads world position, and every surface lit by `OS_ShadeP` takes it: stone, the street, the birches' bark. On a swaying limb, an opening door, a boat or a person, the strokes stay in the air while the surface moves under them.
2. **The brush switches projection abruptly.** It picks whichever world plane the normal most faces. On round things (trunks, limbs, posts, people) that leaves a seam at every quarter turn; on anything that turns (a door, a branch in wind) whole patches jump between projections as the normal passes 45 degrees.
3. **The brush draws a world grid.** Each 71 cm patch takes its own direction and offset, with no blend across its border, so every surface carries a grid of straight seams aligned to the world's axes. At today's strength (0.5) a seam can step the colour by up to about a tenth (our reading of the shader). That is visible tiling, against our own rule, and a grid of lines is what the eye catches first when it slides.
4. **The brush aliases with distance.** Nothing fades it by footprint. Its cross-stroke detail falls under two pixels at about 100 m face-on and about 17 m on the lane's ground (section 5). From the far stop it is pixel-scale noise and crawls as the camera glides. MSAA does not touch it.
5. **The bark's marks will slide in wind.** Lichen, mottle and the foot's rough plates sample world x + z and height (`Tree.shader`, the bark surface and its bump). x + z also mirrors the pattern on a trunk's far side, the fault already fixed for the foot's outline and not for the rest.
6. **Leaf cards flip.** `OS_CardWS` mirrors each card when its seeded side test changes sign, so as the camera orbits, cards across a crown pop one by one into their mirror images.
7. **Screen-fixed hashes.** The leaves' edge cut, the deep twigs' season cut and the fine twigs' coverage dither with `OS_Hash(positionCS.xy)`; the sun beams' march is jittered per pixel, which the shader's own comment says "the stills' supersampling smooths". In play, with no supersampling and no temporal pass, the jitter is a fixed grain on the beams, and leaf and twig edges slide through a fixed pattern.
8. **Unfiltered fine marks.** Moss cushions (`Growth.hlsl`) are about 3.6 cm across and their cover has no footprint fade (only their relief fades): under two pixels by about 37 m face-on and 10 m on the lane's ground (our arithmetic), where they will sparkle. The street's card cut (`OS_CardClip`, used four times in `Street.shader`) mixes the card's coordinates with world position and would crawl on a card that moves.
9. **Tier hand-overs are not yet safe.** `Stone.shader` has no cross-fade, and nothing yet guarantees that both sides of a switch draw the same marks.
10. **Our judging cannot see any of this.** Every judged frame goes through `LT1Render.Still`: rendered at 3840 by 2160 and averaged down to 1920 by 1080 after warm-up frames. That gives four shading samples a pixel, which averages away shader aliasing and jitter. It also gives a footprint two thirds of the game's at 1440p, so `OS_Near` fades between about 3.7 and 12.5 m in our stills against 2.5 and 8.3 m in play (our arithmetic). And every judged frame is a still. Mutant Mayhem's director judged by stills; a free camera cannot be.

Wind is the first mover to arrive (`docs/research/animation-and-motion.md`, what we should do, item 3). Items 1, 2, 5 and 6 break the day it lands on the birches.

### Where a mark lives: the rule

**A mark lives in the frame of the thing it describes, sampled before anything moves that thing. Its size on screen is held in a band by levels. Only the lens and the medium live on the screen.** By kind of thing, the frames are those in section 4's table. Decided on the evidence above:

- **The brush takes its coordinate from the part, not from the world.** Each part supplies a mark coordinate in two dimensions, in metres. It runs continuously across what should read as one painted surface (a stone's face, a board along its length, a wall run, the bark round and along its stem), from an anchor that does not move when the part changes. For deforming things it comes from the rest pose; for wind-moved things from the undisplaced position. The plane-picking projection goes; a metric UV has no seams at 45 degrees and no world grid.
- **The brush's patches blend across their borders,** so no straight seam is drawn (a smooth field of directions, or patches overlapped and cross-faded).
- **Every procedural mark is band-limited.** Each declares its smallest feature and fades to its mean as that feature nears two pixels, by footprint, as `OS_Near` and the lichen already do.
- **No mark that describes a thing reads screen position.** Cards and twigs dither from their own UV and seed. Screen-fixed patterns are for the lens (grain, vignette, glow) and come after any upscaler.
- **What must change with the view fades.** Leaf cards turn to the eye without a mirror flip, or cross-fade between the two faces over a band of headings.
- **Every mark must be stable without temporal accumulation.** MSAA 4× stays (cheap on the tile GPU); nothing may need TAA to look right. Every shader that moves vertices still writes motion vectors, so a temporal upscaler stays possible if the harness needs one.
- **No full-screen painterly filter at runtime.** Kuwahara stays an offline tool for target frames and for the far tier's bake, as `docs/research/materials-at-scale.md` (item 10) proposes.
- **People's brush lives in the rest pose,** sized by the same rule as everything else, and they carry fewer, steadier marks than what stands still (film's rule 7). That answers the characters study's open question about a 70 cm stroke on a head, once Øystein decides how the brush sizes (below).

### What every part must carry

This is the input to `docs/building-blocks.md`, beside the motion contract (`docs/research/animation-and-motion.md`).

| Data | Who carries it | Why |
| --- | --- | --- |
| A mark coordinate in metres, continuous where the paint should flow, anchored at a point that does not move when the part changes | every part | the brush and every procedural mark ride with the part and survive regeneration |
| An anchor class: static, rigid, skinned, flexible, card or fluid | every part (it joins the motion class) | the shader knows which frame its marks use |
| A seed from the thing's and the part's identity, never vertex order or build order | every part | an unchanged part keeps its marks when its neighbours change |
| Rest position and rest normal (three floats each, in UV channels) | people, garments, flags, laundry, ropes, anything simulated | marks stay on a deforming surface |
| The undisplaced position, passed through the vertex stage | everything the wind moves | bark and leaf marks ride with their branch |
| A motion-vector pass | every shader that moves vertices | a temporal pass stays possible; nothing ghosts if one comes |
| The same mark coordinate, seed and history address at every tier | every part with tiers | a hand-over changes geometry only |
| Each procedural mark's smallest feature | every shader that draws one | the shader fades it at two pixels |

### Look tests that would prove it

1. **The motion sheet** (the tool comes first). Fixed camera paths rendered at 2560 by 1440, MSAA 4×, one sample a pixel, as video at 60 fps, beside stills rendered at the game's footprint:
   - a glide along the gully's lane at the street stop, at walking pace;
   - a pull-out from eye level to the near-isometric view over ten seconds;
   - an orbit of a birch at 12 m in a force 5 wind (once wind exists);
   - a door opening and a boat rolling at its berth (once they exist).
2. **Two measures, in the performance harness.** A swim test: render the marks alone along a path, warp each frame onto the next by its motion vectors (exact for the camera and for vertex motion, wind and hinges included), and measure what is left. A mark that rides with its surface leaves nothing but its own aliasing; a mark fixed to the screen or to the world under a moving surface leaves its slide. A shimmer index: the high-frequency energy of that residual per material. Thresholds are set after the first run, against what Øystein sees.
3. A/B tests in the motion sheet: the brush as now against the brush re-anchored and band-limited; the octave-stepped brush against one world size (for Øystein); leaf flip against fade; screen dither against card dither; moss unfiltered against faded.
4. **What would change our minds.** If the octave-stepped brush visibly breathes during the pull-out, nested levels (the tonal art maps' rule) replace the cross-fade. If the brush cannot be seen in motion from the street stop at today's strength, it is doing no work, and the look lives in light and history marks alone. If an edge dither from the cards' own UV still crawls, the edge goes to alpha-to-coverage only.

## What we should do

Ranked by what each buys for what it costs. Days are Claude's working days, before review.

| # | Change | Cost | What it buys |
| --- | --- | --- | --- |
| 1 | **Judge in motion and at the game's pixel.** A motion-sheet renderer beside `LT1Render.Still`: fixed camera paths as 60 fps video at 1440p, MSAA 4×, one sample a pixel. A global footprint scale so supersampled stills fade where the game does. The swim test and shimmer index in the performance harness | 2 to 3 days | every later review sees what a player sees; faults 1 to 10 above become numbers |
| 2 | **The mark contract in `docs/building-blocks.md`** and the generator framework: mark coordinate, anchor class, seed by identity, rest pose, undisplaced position, motion vectors, the same marks at every tier, smallest feature per mark | 1 day | parts made from now on can move, change and be tiered without their marks breaking |
| 3 | **The brush re-anchored and band-limited:** its coordinate from the part (the stone's metric UV0, the bark's UV), patch borders blended, its fine octave faded by footprint, its strength handed to true detail within the near zone (by eye) | 2 days | no world grid, no slide on movers, no crawl from the far stop |
| 4 | **Trees made ready for wind,** before the wind work: bark marks from the undisplaced object position; card and twig dither from the card's UV; leaf cards without the mirror flip; a motion-vector pass that includes the wind | 1 to 2 days | the birches survive their first gust |
| 5 | **The rest band-limited:** moss cushions' cover and every noise octave in `Growth.hlsl`, `Stone.shader` and `Tree.shader` checked against the two-pixel rule; `OS_CardClip` cut from the card's own coordinates | 1 day | no sparkle on the lane's ground or the walls' feet at the street stop |
| 6 | **Beams without a screen grain:** the march's jitter averaged before it reaches the screen (a few more steps near the camera, or a half-resolution march with a depth-aware upsample, timed against the native-pass cost) | 1 to 2 days | light rays that hold in motion without TAA |
| 7 | **The octave-stepped brush,** if Øystein agrees (below): two octaves a factor of two apart, cross-faded by log2 of the footprint, contrast renormalised | 1 to 2 days | painted marks of one size on screen from the lane to the roofs |
| 8 | **Tier hand-overs:** the same marks on both sides, the switch where values match, short dithered fades, cross-fade in `Stone.shader` | within the tiers work, about a day a kind | no pop and no screen door at a switch |
| 9 | **Fluids by their own rules,** as each system arrives: flow maps where water runs; smoke and steam as flipbooks held on twos that break apart; every transparent mover judged without a temporal pass | within those systems | water and smoke whose marks read as drawn and never ghost |
| 10 | **The anti-aliasing stance written into `docs/foundations.md`:** MSAA 4× at native 1440p; FSR 1 (spatial, keeps MSAA) if the harness says the frame does not fit; STP only once every mover writes motion vectors | none now | the look we judge is the look we ship |

Items 1 to 4 come before the wind reaches the birches, and item 2 before any building block is made.

## For Øystein to decide

1. **How the brush is sized.** Today's rule says "a brush mark has a size in the world, the same on every object" (`docs/visual-direction.md`). Over our camera's range that one size runs from about 1,450 pixels to 4. A painter sizes strokes to the canvas, and the studies rank motion coherence first, which an anchored brush keeps either way. *Recommendation:* the brush stays fixed to each thing, and octaves hold its size on screen within a factor of two, so a wall in the lane and a roof seen from 120 m carry strokes of about the same painted size. The band is chosen by eye in the motion sheet's pull-out. It changes one line of the visual direction.
2. **Boil.** Marks can hold perfectly still, boil a little (re-seeded at a low rate, as Paperman's dial allowed), boil fully (Loving Vincent), or boil only on effects. *Recommendation:* nothing that stands boils; smoke, steam and splashes play as held frames on twos, as a look test (it joins the animation study's open item on stepped effects).
3. **The anti-aliasing default** (item 10). Temporal upscaling would buy frame time but smears every mark without motion vectors. *Recommendation:* MSAA 4× at native resolution, FSR 1 as the first fallback, STP last; the harness's numbers decide whether a fallback is needed at all.

## Gaps

- Sources that did not open. The web-search budget ran out partway through. Pope's devlog (403; a full translation was used, secondary). Meier 1996 (ACM's bot wall; cited through later papers). Bénard's *Stylizing animation by example* (2013) and Semmo's oil-paint filtering (closed). GDC Vault talks for Hi-Fi Rush and others (abstracts and Epic Japan's slides only). HAL copies of the INRIA papers (bot wall; read from INRIA's own servers instead).
- Games with no technique found: Tunic, Townscaper, Tiny Glade's marks, Planet of Lana, The Last Night, Kentucky Route Zero, Dordogne, Eastshade, The Witness, Mundaun, Wind Waker and Lethal Company. Breath of the Wild's distant brush look is unconfirmed by any developer; where Hi-Fi Rush's halftones live is unknown; Arcane is covered thinly.
- Unverified on our stack: that Unity 6's GPU skinning leaves extra UV channels untouched; STP's cost and ghosting on the M4, and which quality profile a Mac gets; whether URP's TAA has any reactive mask; how visible URP's cross-fade dither is without TAA; that Metal has no geometry shaders.
- Not measured: the brush's real visibility and aliasing in motion; the cost of `OS_Brush` and of a second octave; how often the leaf flip shows in an orbit; a half-resolution Kuwahara's real cost on the M4.
- Coverage: `docs/systems.md`'s research coverage should list this study (not edited here).

## Sources

**Papers.** [Bénard, Bousseau, Thollot, temporal coherence STAR (2011)](https://www-sop.inria.fr/reves/Basilic/2011/BBT11/paper.pdf) · [Dynamic solid textures (2009)](http://artis.inrialpes.fr/Publications/2009/BBT09/BBT09.pdf) · [A dynamic noise primitive (2010)](http://artis.inrialpes.fr/Publications/2010/BLVLDT10/BLVLDT10.pdf) · [Breslav et al., dynamic 2D patterns (2007)](http://artis.inrialpes.fr/Publications/2007/BSMBT07/d2d-s07.pdf) · [Klein et al., non-photorealistic virtual environments (2000)](https://www.cs.jhu.edu/~misha/MyPapers/SIG02.pdf) · [Praun et al., real-time hatching (2001)](https://hhoppe.com/hatching.pdf) · [Praun et al., lapped textures (2000)](https://hhoppe.com/lapped.pdf) · [Hertzmann, painterly rendering (1998)](https://www.mrl.nyu.edu/publications/painterly98/hertzmann-siggraph98.pdf) · [Hertzmann, stroke-based rendering survey](https://www.dgp.toronto.edu/~hertzman/sbr02/hertzmann-sbr02.pdf) · [Bousseau et al., watercolour (2006)](http://artis.inrialpes.fr/Publications/2006/BKTS06/watercolor.pdf) · [Bousseau et al., video watercolorization (2007)](http://artis.inrialpes.fr/Publications/2007/BNTS07/siggraph_video_watercolor.pdf) · [Lu, Sander, Finkelstein (2010)](https://www.cse.ust.hk/~psander/docs/stylize.pdf) · [Montesdeoca et al. (2017)](https://dr.ntu.edu.sg/bitstream/10356/86258/2/Art-directed%20watercolor%20stylization%20of%203D%20animations%20in%20real-time.pdf) and [MNPR](https://github.com/semontesdeoca/MNPR) · [Garcia et al., coherent splat stylization (2021)](https://typhomnt.github.io/research/coherent_splat_stylization/) · [Schmid et al., OverCoat (2011)](https://la.disneyresearch.com/wp-content/uploads/OverCoat-An-Implicit-Canvas-for-3D-Painting-Paper.pdf) · [StyLit (2016)](https://dcgi.fel.cvut.cz/home/sykorad/Fiser16-SIG.pdf) · [Jamriška et al. (2019)](https://dcgi.fel.cvut.cz/home/sykorad/Jamriska19-SIG.pdf) · [Texler et al. (2020)](https://dcgi.fel.cvut.cz/home/sykorad/Texler20-SIG.pdf) · [Kyprianidis et al., anisotropic Kuwahara (2009)](https://www.kyprianidis.com/p/pg2009/jkyprian-pg2009.pdf) · [polynomial weights (2010)](http://www.kyprianidis.com/p/tpcg2010/jkyprian-tpcg2010.pdf) · [multi-scale (2011)](https://www.kyprianidis.com/p/npar2011/jkyprian-npar2011.pdf) · [coherence-enhancing filtering (2011)](https://www.kyprianidis.com/p/eg2011/jkyprian-eg2011.pdf) · [XDoG (2012)](https://www.kyprianidis.com/p/cag2012/winnemoeller-cag2012.pdf) · [Peterson and Lee, aggregate normals (2006)](https://history.siggraph.org/learning/simplified-tree-lighting-using-aggregate-normals-by-peterson-and-lee) · [Vlachos, water flow in Portal 2 (2010)](https://www.advances.realtimerendering.com/s2010/Vlachos-Waterflow(SIGGRAPH%202010%20Advanced%20RealTime%20Rendering%20Course).pdf) · [Quilez, band-limiting](https://iquilezles.org/articles/bandlimiting/) · [Castaño, alpha mipmaps](https://www.ludicon.com/castano/blog/2010/09/computing-alpha-mipmaps/) · [Lozar, motion-vector frame blending](http://www.klemenlozar.com/frame-blending-with-motion-vectors/) · [Ptex](https://ptex.us/overview.html)

**Games.** [Obra Dinn devlog, translated](https://sudonull.com/post/64811-The-effect-of-dithering-in-a-three-dimensional-game) · [Pope interview (Game Developer)](https://www.gamedeveloper.com/design/for-lucas-pope-i-return-of-the-obra-dinn-i-was-a-bunch-of-appealing-design-problems) · [Johansen, surface-stable dithering](https://runevision.com/tech/dither3d) and [code](https://github.com/runevision/Dither3D) · [Arc System Works, Guilty Gear toon lines](https://docswell.com/s/ASW_Academy/5LVY67-GG-Toonline-Eng) · [Motomura, GDC 2015](https://gdcvault.com/play/1022031/GuiltyGearXrd-s-Art-Style-The) · [Guilty Gear Xrd handout notes](https://www.scribd.com/document/354898858/GuilltyGearXrd-shader-pdf) · [Hi-Fi Rush, GDC 2024](https://schedule.gdconf.com/session/3d-toon-rendering-in-hi-fi-rush/899802) · [Hi-Fi Rush at Unreal Fest Tokyo (Automaton)](https://automaton-media.com/articles/newsjp/20240511-293086/) · [Epic Games Japan, stylised rendering in Japanese titles](https://docswell.com/s/EpicGamesJapan/5DEVPV-2023-12-01-082936) · [Genshin Impact, Unity Dojo 2021](https://docswell.com/s/UnityJapan/KWRPQ5-210617-unity-dojo20211mihoyozhenzhongyi) · [Genshin community shaders](https://github.com/NoiRC256/URPSimpleGenshinShaders) · [Sable (Game Developer)](https://www.gamedeveloper.com/marketing/how-shedworks-refined-the-art-of-sable-in-pursuit-of-readability) · [Ng, Making the world of Firewatch (GDC 2016)](https://media.gdcvault.com/gdc2016/Presentations/Ng_Jane_MakingTheWorld.pdf) · [Ang et al., Sea of Thieves (SIGGRAPH 2018)](https://history.siggraph.org/wp-content/uploads/2022/09/2018-Talks-Ang_The-Technical-Art-of-Sea-of-Thieves.pdf) · [Breath of the Wild at CEDEC 2017 (summary)](https://thefamicast.com/2017/12/part-5-art-and-implementation-of-3d.html) · [Okami (Wikipedia)](https://en.wikipedia.org/wiki/Okami) · [Holland, 3D pixel art](https://www.davidhol.land/articles/3d-pixel-art-rendering/) · [Acerola's post-processing](https://github.com/GarrettGunnell/Post-Processing) · [Godot anisotropic Kuwahara](https://godotshaders.com/shader/anisotropic-kuwahara-filter/) · [Heckel, painterly shaders](https://blog.maximeheckel.com/posts/on-crafting-painterly-shaders) · [Heckel, Moebius post-process](https://blog.maximeheckel.com/posts/moebius-style-post-processing) · Disco Elysium: Rostov's devblog, as cited in `docs/research/lighting-and-colour.md`

**Film.** [Deep Canvas patent](https://patents.google.com/patent/US6268865B1/en) · [Deep Canvas in Tarzan (SIGGRAPH)](https://history.siggraph.org/learning/deep-canvas-in-disneys-tarzan) · [Whited et al., Paperman](https://media.disneyanimation.com/uploads/production/publication_asset/122/asset/pman.pdf) · [Paperman (fxguide)](https://www.fxguide.com/?p=39516) · [Spider-Verse in comp (Foundry)](https://www.foundry.com/insights/film-tv/graphic-look-in-comp-spiderman) · [Patcher patent](https://patents.google.com/patent/US11195308B2/en) · [Spider-Verse lines (fxguide)](https://www.fxguide.com/?p=246246) · [Imageworks (Cartoon Brew)](https://www.cartoonbrew.com/feature-film/if-its-not-broke-break-it-sony-imageworks-renegade-approach-to-spider-man-into-the-spider-verse-167321.html) · [Across the Spider-Verse inking](https://beforesandafters.com/2023/06/28/this-was-the-first-cg-animated-movie-ive-ever-heard-of-that-actually-had-a-dedicated-inking-team/) · [Across the Spider-Verse lines](https://beforesandafters.com/2024/01/10/giving-spider-man-across-the-spider-verse-that-crucial-hand-made-quality/) · [Oskarsson and Chazot (SIGGRAPH 2023)](https://history.siggraph.org/learning/fitting-variable-rate-animation-into-a-modern-feature-film-pipeline-by-oskarsson-and-chazot) · [Spider-Verse effects (SideFX)](https://www.sidefx.com/community/spider-man-into-the-spider-verse/) · [Klaus (befores & afters)](https://beforesandafters.com/2019/11/14/heres-what-made-the-2d-animation-in-klaus-look-3d/) · [MOE](https://www.lesfilmsdupoissonrouge.com/inhousetechnology/moe) · [Puss in Boots: The Last Wish](https://beforesandafters.com/2023/01/11/heres-how-dreamworks-lent-a-whole-new-brand-of-stylized-look-and-feel-to-puss-in-boots-the-last-wish/) · [The Wild Robot (befores & afters)](https://beforesandafters.com/2025/01/10/if-you-want-a-painterly-bush-paint-the-bush/) · [The Wild Robot (Keyframe)](https://keyframemagazine.org/2024/12/16/call-of-the-wild/) · [The Mitchells vs. the Machines](https://beforesandafters.com/2021/04/29/turning-a-painting-into-moving-images-reveals-a-lot-of-things/) and [SIGGRAPH blog](https://blog.siggraph.org/?p=13404) · [Mutant Mayhem](https://beforesandafters.com/2023/09/07/we-wanted-to-imply-teenage-imperfection-everywhere/) · [Arcane (Cartoon Brew)](https://www.cartoonbrew.com/streaming/series-craft-director-barth-maunoury-breaks-down-an-emotional-arcane-sequence-244539.html) · [Arcane season 2 (VFX Voice)](https://vfxvoice.com/riot-games-and-fortiche-get-revolutionary-with-arcane-season-2/) · [Hand-drawn effects (VFX Voice)](https://vfxvoice.com/the-return-of-hand-drawn-and-stylized-effects-animation/) · [Loving Vincent, the paintings](https://lovingvincent.com/the-paintings,2,pl.html) · [Multiplane camera (Wikipedia)](https://en.wikipedia.org/wiki/Multiplane_camera) · [Houdini rest position](https://www.sidefx.com/docs/houdini/nodes/sop/rest.html) · [Blender texture coordinates](https://docs.blender.org/manual/en/latest/render/shader_nodes/input/texture_coordinate.html)

**Engines and hardware.** [URP anti-aliasing](https://docs.unity3d.com/Manual/urp/anti-aliasing.html) · [URP camera settings](https://docs.unity3d.com/6000.0/Documentation/Manual/urp/camera-component-reference.html) · [URP motion vectors](https://docs.unity3d.com/Manual/urp/features/motion-vectors.html) · [STP](https://docs.unity3d.com/Manual/urp/stp/stp-upscaler.html) · [URP asset](https://docs.unity3d.com/Manual/urp/universalrp-asset.html) · [LOD Group](https://docs.unity3d.com/Manual/class-LODGroup.html) · [Preserve coverage](https://docs.unity3d.com/ScriptReference/TextureImporter-mipMapsPreserveCoverage.html) · [Mesh.SetUVs](https://docs.unity3d.com/ScriptReference/Mesh.SetUVs.html) · [Render Graph](https://docs.unity3d.com/Manual/urp/render-graph-introduction.html) · [Framebuffer fetch](https://docs.unity3d.com/Manual/urp/render-graph-framebuffer-fetch.html) · [Render Graph pass breaks (source)](https://raw.githubusercontent.com/Unity-Technologies/Graphics/master/Packages/com.unity.render-pipelines.core/Runtime/RenderGraph/Compiler/PassesData.cs) · [VFX Graph flipbooks](https://docs.unity3d.com/Packages/com.unity.visualeffectgraph@17.0/manual/Context-OutputSharedSettings.html) · [Six-way lighting](https://docs.unity3d.com/Packages/com.unity.visualeffectgraph@17.0/manual/six-way-lighting.html) and [blog](https://unity.com/blog/engine-platform/realistic-smoke-with-6-way-lighting-in-vfx-graph) · [SpeedTree game wind](https://docs.unity3d.com/speedtree-modeler/manual/wind-games.html) · [Unreal pre-skinned position](https://dev.epicgames.com/documentation/en-us/unreal-engine/vector-material-expressions-in-unreal-engine) · [Pivot Painter 2](https://dev.epicgames.com/documentation/en-us/unreal-engine/pivot-painter-tool-2.0-in-unreal-engine) · [Unreal TSR](https://dev.epicgames.com/documentation/en-us/unreal-engine/temporal-super-resolution-in-unreal-engine) · [FSR 2](https://github.com/GPUOpen-Effects/FidelityFX-FSR2) and [manual](https://gpuopen.com/manuals/fidelityfx_sdk/fidelityfx_sdk-page_techniques_super-resolution-temporal/) · [MetalFX (WWDC 2022)](https://developer.apple.com/videos/play/wwdc2022/10103/) · [Bring your game to Mac (WWDC 2023)](https://developer.apple.com/videos/play/wwdc2023/10125/) · [Harness Apple GPUs with Metal (WWDC 2020)](https://developer.apple.com/videos/play/wwdc2020/10602/) · [Optimize Metal performance for Apple silicon Macs (WWDC 2020)](https://developer.apple.com/videos/play/wwdc2020/10632/) · [Mac mini (2024) specifications](https://support.apple.com/en-us/121555) · [Apple M4 (Wikipedia)](https://en.wikipedia.org/wiki/Apple_M4)
