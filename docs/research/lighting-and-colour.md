# Lighting and colour in real time

How masters of real-time light and colour build their worlds, and what that means for ours. One of the craft studies behind the building blocks (`NOW.md`), beside `materials-at-scale.md`, `kits-and-generation.md`, `performance-at-scale.md`, `history-in-things.md` and the study of motion. It builds on `colour-and-shading.md` (the art rules) and `masters-of-colour.md` (the painters and cinematographers), and does not repeat them. It is an input to the design, not a decision.

Claims read in a summary rather than the source are marked (secondary); claims not confirmed are marked (unverified). Facts about Unity are from Unity's documentation for 6.6 or from the URP 17.6 source in our own project (`unity/Library/PackageCache`), which is the version we run.

## The short of it

1. The masters put physics underneath and art direction on top, and the art acts on the whole light, never per material. Ghost of Tsushima, Red Dead Redemption 2 and Unreal's sky all do this; SEASON, Disco Elysium and Arcane each learned the hard way that light painted into colour breaks when the light changes. Our one shade function and our rule 1 are right.
2. Our four light debts share one cause: the shade function guesses what a face sees instead of looking. Each fix was a further guess. Three cheap lookups end the series: the sky's own radiance, the ground a face looks onto, and the town it looks at.
3. Our sky map is our own version of what Unity calls sky occlusion and what Sucker Punch bakes as sky visibility, with one advantage neither has: it is redrawn when the town changes. Unity's probe volumes cannot do that; they bake in the editor.
4. The rig is almost all hand-typed colour: only the sun's position comes from physics. The masters derive the sun's colour, the sky and the ambient from a model and art-direct a few pushes on top. That is what makes any date, hour and weather possible, and what would end the drizzle and morning retunes.
5. The night is where our pipeline is thinnest. The heart has 403 lights against Forward+'s 256, and no lamp casts a shadow. A lamp's reflection in a puddle is an order of magnitude too dim. The style pass runs after URP's dithering, which invites banding in the fog gradients a nocturne lives on.
6. Two regimes the corner does not show fit the planned record and shade, studied in LA (§10 to §12). Under a canopy, flecks are soft pictures of the sun and the leaves are a second, greener sky; leaf-sharp shadows belong only near. Many lamps need one list in the facts, a tier chosen per frame and our own binned buffer instead of URP's Forward+; low-CRI lamps drain colour by a 3 × 3 matrix per kind. The format must key art by the sun's elevation, derive the ambient, dome and reflections from one sky model, hold lamps by reference, keep whatever varies by place in maps, and step its caches by absolute time.

## 1. How painterly and stylised-realist games light their worlds

| Work | What they do with light and colour | What we take |
| --- | --- | --- |
| **Firewatch** (Campo Santo; Jane Ng, Olly Moss) | Colour in distinct layers, each a step of depth; fog is the tool that sets each layer's colour, and thick fog brings the 3D world close to Moss's graphic poster (secondary, Thumbsticks on Ng's GDC 2015 talk). The lighting is dynamic, so colours can change as the player moves (secondary); the sky's light came through Marmoset Skyshop (secondary). The fog's colour comes from a gradient texture looked up by depth, replacing Unity's own fog (secondary: community reconstructions of the talk). The sky is a procedural shader built for an artist, not for physics: a three-colour gradient, a sun disc, a sun halo and a horizon halo, each shown alone in a debug view. Unity 5's scattering sky was set aside because it was tied to the sun light and took physics knowledge to tune (Campo Santo's own blog). A colour script per story beat: "the colours ... really do drive the mood of the scene" (secondary). | Air as designed layers (we have it); a sky made of a few named parts an artist can see one at a time; a colour key per story moment. |
| **Ghost of Tsushima** (Sucker Punch; Jasmin Patry, SIGGRAPH 2021) | "Stylized realism": physically based lighting that "can deviate from physical correctness", adjusted globally. Probes store sky visibility; each frame the sky is projected to spherical harmonics (60 µs on a base PS4) and multiplied by it. Sun and moon light bounce off an "imaginary ground and wall" into the probes, scaled by cloud shadow. A 25% "directionality boost" in every weather, because the indirect light looked flat. 235 reflection probes, relit round-robin as the hour changes. Froxel haze 128×64×64 from 10 cm to 100 km, about 0.5 ms. Exposure from illuminance, not from the image, after an "exposure-albedo feedback loop" made earlier games' albedos too dark; a diffuse reference chart fixed it. Grading kept the art director's Photoshop LUTs; white balance became "pick the colour white should become". A Purkinje shift for night. | The closest master to our problem: a living world, a changing hour, a strong art direction. Directional ambient on purpose; sky visibility × a live sky; exposure from the light; a chart against albedo drift. |
| **Red Dead Redemption 2** (Rockstar; Fabian Bauer, SIGGRAPH 2019) | One integrated system for sky, clouds, fog and the sky's indirect light, physically based but built so artists "control the atmosphere in support of the story, missions and mood"; voxelised raymarching shared by the view, the reflections and a sky irradiance probe grid (from the abstract; the 232 MB slides were not read). | The sky, the fog and the ambient as one source, so they never disagree. |
| **Sable** (Shedworks) | Flat shading, so depth comes in layers: lighting, fog, lines. Distant fog "really, really key" for reading; the fog system is the framework of the day-night cycle; shadows kept so the player can read where they stand (secondary, Game Developer). | Fog is the first depth tool, not an effect. |
| **Disco Elysium** (ZA/UM; Aleksander Rostov's devblog, 2016) | Painted backgrounds lit by time of day in four states. First tried: an additive light map per hour over a neutral render; dropped because it multiplied assets and "tended to overwrite any hand painted brushwork". Shipped: a one-channel shadow render plus a small "lightfield map" (which way light moves at each pixel), which dim and colour the one painted image by hour and weather. Characters lit by the same lightfield plus real lamps. | The painted colour is the only colour; light is separate data laid over it. Our parts do the same with their bake. |
| **SEASON** (Scavengers) | Per-material shadow tints could not adapt to changing light; shadow colour was moved to the light (our rule 1, `colour-and-shading.md`). | Already law here. |
| **Sea of Thieves** (Rare, SIGGRAPH 2018) | Clouds as opaque meshes with per-vertex light, rendered off-screen, blurred and composited: art-directed shapes with no raymarching; harder edges far off for "a more distinct and cartoon-like appearance". | Clouds can be designed forms with lit tops and dark bellies, not noise. |
| **INSIDE** (Playdead) | Separate diffuse, specular and bounce-light entities placed by artists; analytic AO from primitives; local shadowed volumetrics (from the GDC 2016 abstract; the slides were too large to read). Mikkel Gjøl's banding talk: dither at every quantisation with triangular noise, or fog and glows band. | Bounce as a placed light where the engine has none; banding is a craft problem, solved on purpose. |
| **The Last of Us** (Naughty Dog; Vivian Ding, GDC 2014) | "Dominant directionality", ambient shadows to ground things, a flashlight that bounces (abstract only). | The same lesson as Ghost: indirect light needs a direction. |
| **Journey** (thatgamecompany) | Colour follows the arc of the journey (`colour-and-shading.md`); the sand's glitter is its own lighting term (secondary). | Colour as an arc keyed to what happens. |
| **The Witness** (Thekla) | "Minimize the amount of noise we put into the player's mind" (Luis Antonio, GDC 2014); baked light on a static island. | Simplification is a lighting choice too. Baking is not ours: our places change. |
| **Breath of the Wild** (Nintendo) | A style that "makes it easy to lie" while keeping a sense of reality (secondary, GDC 2017 report). Its lighting pipeline is unpublished. | The style exists so that the light can be simplified believably. |
| **Kentucky Route Zero** (Cardboard Computer) | Theatrical staging (Kemenczy, "The Scenography of Kentucky Route Zero", GDC 2014); the lighting technique is unpublished (unverified forum guesses). Gjøl uses it as an example of visible banding on good monitors. | Stage light motivated by sources; and a warning about gradients. |
| **Tiny Glade** (Pounce Light) | Real-time diffuse GI by software ray tracing, so it runs on old GPUs; a froxel fog that lanterns light (secondary, developer posts). | A small team can afford real GI if the world is small and the method scales down. |
| **Spider-Verse, Arcane** (film) | Graphic marks driven by light, not painted per object (`colour-and-shading.md`). Sony Imageworks lit Spider-Verse by sequence: one key rig over all of a sequence's shots, each shot a sparse override (SIGGRAPH 2018, GafFour). Arcane's painted look reportedly had to be repainted per lighting scenario (unverified). | Key lighting as data with sparse overrides (section 6); and once more, light painted into colour does not survive a change of light. |

**What they share:**
- Physics underneath, art on top, at the level of the whole light. Ghost and RDR2 are physically based with global art controls; Firewatch replaced a physical sky with an artist's tool but kept real lights and real shadows.
- Light painted into colour fails when the light changes: SEASON, Disco Elysium's first attempt and, reportedly, Arcane. Every one of them separated the painted colour from the light.
- Indirect light must have a direction. Ghost boosts it by a quarter; Naughty Dog names "dominant directionality". A uniform ambient reads as dead.
- The air is the main tool for depth and mood (Firewatch, Sable, INSIDE, Ghost's haze).
- The sky is a few designed parts, whether built on physics (Hillaire, RDR2) or not (Firewatch, Sea of Thieves).
- Colour is keyed to moments, not spread evenly (Firewatch, Journey, Ghost's "we weren't going for pure realism").

## 2. Real-time light: pipelines in URP and beyond

### Indirect light: what can carry it

| Method | How it works | Fits a town that changes? |
| --- | --- | --- |
| Lightmaps | Baked per surface in the editor | No: places change (`unity-conventions`). |
| Adaptive Probe Volumes (APV) | Probes placed by geometry density, baked in the editor | No for the town's own geometry: Unity's docs describe only editor baking (runtime baking unverified). |
| APV sky occlusion | Bakes how much sky each probe sees, once; at runtime the ambient probe's colour is multiplied in, so the sky's light can follow a day-night cycle. Treats all geometry as one grey, so dark and light walls bounce the same. In URP the ambient must be set as Gradient or Color for live updates; Skybox needs `DynamicGI.UpdateEnvironment`, which Unity warns is very expensive | Same idea as our sky map, but baked: it cannot follow a rebuilt street. |
| APV lighting scenarios | Several bakes, blended by script; only probe data | Assassin's Creed shows the price: Unity baked 4 time-of-day key frames, Syndicate 9, Shadows 11 times 3 to 4 for seasons, because snow cover and summer growth light a place differently; a uniform layout extrapolated to about 1.9 TB and a 624-day bake (secondary, SIGGRAPH 2025 summary). Shadows then moved to ray-traced GI. |
| Relightable probes | Probes store transfer, relit live as the sky changes: Far Cry 3's deferred radiance transfer volumes (GDC 2012), The Division (GDC 2016), Ghost's sky visibility | The right family. Still baked against static geometry. |
| Surface Cache GI (URP) | Unity's dynamic diffuse GI for URP: follows changing geometry and lights, day/night; hardware ray tracing on DirectX 12, a compute fallback elsewhere, Metal included; static batching off. Unity staff aim to ship it in 6.7 LTS; it is in our 17.6 package behind a define | Yes in principle. Diffuse only; a preview; not tested on our Mac. An extra layer at most, as the conventions say. |
| Our sky map and part bakes | Each part bakes what each face sees (sky, ground, openness: `bake.py`); the town's height from above is redrawn whenever the town changes, and each point marches it to find its open sky (`OS_TownSky`) | Yes. The sky map also lights moving things (people, boats), which carry no bake of their own. |

So our approach is the relightable-probe idea moved to where our world needs it: visibility is data, the sky's colour is live, and both survive a rebuilt street.

### The sky and the air

- **Sky models.** Model fits (Preetham, Hosek-Wilkie) give only views from the ground and no aerial perspective; table-based models (Bruneton, used in Ghost and RDR2) carry multiple scattering. Sébastien Hillaire's model (EGSR 2020, in Unreal) uses a few small tables, a cheap multiple-scattering term, and a froxel volume for aerial perspective that lights opaque and transparent surfaces alike: about 0.3 ms on a GTX 1080 (Hillaire's SIGGRAPH 2020 slides). It updates every frame, so any hour and any atmosphere density costs nothing extra.
- **Overcast skies are not uniform.** The CIE standard overcast sky, from Moon and Spencer (1942), adopted by the CIE in 1955, is three times brighter at the zenith than at the horizon, L = Lz (1 + 2 sin γ) / 3 (secondary, colour-science docs; NTNU's Nordic Light and Colour). An unobstructed vertical wall receives at most about 40% of what a roof receives (secondary, IESVE). Thin cloud also brightens round the hidden sun (unverified here; the CIE's later general sky standard has overcast types for it). Our first debt was this missing structure.
- **Fog.** Height fog with analytic integrals is the cheap base. Froxel volumes (Wronski, Assassin's Creed IV, 2014; Hillaire, Frostbite, 2015) let every light, shadow and density change scatter: Ghost's is 128×64×64 at about 0.5 ms; Tiny Glade's lets lanterns light the fog. URP has no volumetric fog of its own; a free MIT package (`Unity-URP-Volumetric-Light`) supports Unity up to 6000.6, Forward+, shadows and cookies, but lists no Metal testing.
- **Clouds.** Raymarched volumes (Schneider's Horizon Zero Dawn work; RDR2) are the photoreal route. Sea of Thieves shows the designed route: modelled forms, simple lighting, composited soft. A painter's cloud is a shape with a lit top and a dark belly, which suits our rule of planes and silhouettes better than noise.

### Shadows, occlusion and reflections

- **Cascades** set the sun's shadow up to a distance; beyond it Ghost uses a far shadow-map atlas. At our 16:00 sun, 8 degrees up, a 30 m knoll throws a shadow 210 m long, beyond any close cascade's reach.
- **Ambient occlusion.** URP 17.6 already has GTAO as a mode in its occlusion override (`ScreenSpaceAmbientOcclusionVolumeOverride`, "provides higher quality"); Unity calls it a preview to ship in 6.7. Jimenez and others (Activision, 2016) fit how much light a crevice really loses once bounces are counted: bright surfaces lose little, and the loss takes the surface's colour. The fit ships in our own SRP core as `GTAOMultiBounce(visibility, albedo)`. Frostbite's specular occlusion from AO, roughness and view (Lagarde and de Rousiers, 2014) ships beside it as `GetSpecularOcclusionFromAmbientOcclusion`.
- **Reflections.** Box-projected probes relit with the hour (Ghost relights its 235 probes round-robin in async compute, up to 128 at a time). Screen-space reflections are in URP 17.6 as a renderer feature, which we use. Neither knows what is off screen in a lane; Ghost adds horizon occlusion so probes do not shine where the sky is hidden.
- **Hand-made hemisphere light** goes back to Valve's ambient cube in Team Fortress 2 (`colour-and-shading.md`, rule 2). It is honest when its colours come from the sky; it drifts when they are typed.

## 3. Night and many lights

**The limits in URP.** Forward+ draws up to 256 lights per camera on desktop, the main light included (32 on mobile); the cap is a constant in the URP config package, `MAX_VISIBLE_LIGHT_COUNT_DESKTOP 256`, which Unity documents as a workaround to edit. Spot and point lights share one shadow atlas: a spot light takes one map, a point light six. The heart today holds 403 lights (304 shopfronts, 84 sodium, 12 lanterns, a mercury lamp and the two harbour lights), and none casts a shadow (`TownLights.cs`). Hopper's and Hasui's nights are made of cast shadows from lamps.

**What the lamps were.** High-pressure sodium burns at about 2000 to 2100 K with a colour rendering index of 10 to 25 (secondary, patents and guides); low-pressure sodium is nearly one wavelength, 589 nm, under which "colors of objects ... are difficult to distinguish" (Wikipedia); clear mercury is "distinctly greenish" and deficient in red, "not flattering to human skin color" (Wikipedia); White SON, from 1986, is about 2500 K with a CRI near 85, like incandescent. A low-CRI lamp does not only tint: it drains colour. A sodium street turns red brick and green paint to near-identical browns. A multiply by an orange cannot show that, and that is part of why the eras do not read apart.

**Lit windows.** Interior mapping (Joost van Dongen, 2008) casts a ray per pixel into virtual floors and walls behind the glass: rooms with depth, no geometry, no cost per room. SimCity (2013) and, reportedly, Marvel's Spider-Man use it (secondary). Each room can be lit or dark on its own, which is what our facts need: who is home, what is open.

**Wet streets.** Film crews wet streets for night exteriors because dry asphalt "eats light" (secondary, No Film School). Ours are wet by fact, which on this coast is most nights: Våland in Stavanger records 170 mm in a normal October and had 16 to 27 days with rain in the Octobers of 2021 to 2023 (secondary, yr.no's station statistics). A lamp's reflection in a puddle is nearly as bright as the lamp; on a rough wet street it stretches into a streak towards the viewer, a property of the microfacet highlight at grazing angles.

**Glare and bloom.** Call of Duty: Advanced Warfare's bloom uses no threshold, a wide pyramid and a mix of about 0.04, so "only very bright pixels will bloom noticeably". The whole image softens a little, which Jimenez judged more photographic (2014). Print film's halation adds a red fringe round strong highlights, from light bounced back into the red layer (secondary). Bloom is the lens; halos are the air. Our FogLights pass already gives each lamp an airlight halo that grows with the fog between, which is the better half of the craft.

**The night sky is a fact too.** A clear night is dark blue to black, lit by moon and stars. An overcast night over a lit town is not: clouds over Berlin made the sky up to ten times brighter than on clear nights (secondary, Kyba and others, PLoS ONE 2011). Under low cloud, a 1989 sodium town has an orange-grey sky. Our sky already lights cloud undersides with the town's glow; the ambient should follow.

**Night vision.** In low light the eye's rods take over and colour shifts blue (the Purkinje shift; Ghost models it; Khan and Pattanaik on blue shift). This licenses a blue night under a clear sky as perception, not as grade.

**Banding.** Fog, glows, falloffs and slow skies band in 8 bits. Gjøl's rule: dither "during quantisation (e.g. at tonemapping, or any write to an 8bit rt)" with triangular noise of about one step either way, and grain added after quantisation only hides banding if the signal is still high precision.

## 4. Colour pipelines

**Tone mapping in URP.** URP offers None, Neutral and ACES; no AgX (Unity 6.6 docs; free AgX LUTs exist). Neutral is, in our source, a per-channel Hable-style curve with its white at 5.3: each of red, green and blue is compressed on its own. Patry shows the cost of per-channel curves: saturated colours clip towards cyan, magenta and yellow; Christophe Brejon calls the same "hue skews". A bright sodium halo passes through yellow on its way to white, and our lamp glass, at an emission of 40, clips to plain white in every channel. That may be right for the glass (a photograph does it), but the hue of the light round it is a fact the curve may bend.

**The order of operations in URP.** In HDR grading, URP's internal table applies white balance in LMS, then contrast in log space, the colour filter, the channel mixer, the curves and saturation, and last the tonemapper; the user's lookup table (Color Lookup) is applied after that, in display space (`LutBuilderHdr.shader`, `UberPost.shader`). Our style pass (`Palette.shader`) is injected after all post-processing, after grain and after the dithering the heart's camera has switched on, and its value grouping posterises on purpose. That is the wrong place twice: it undoes the dither in the gradients where a fog nocturne lives, and it grades grain. Everything the style pass does depends only on a pixel's colour, so it can be baked into the Color Lookup table each time the light changes and run inside URP's own grading at no cost per pixel.

**LUTs and grading.** Ghost kept the art director's 32³ LUTs from Photoshop and added a white balance an artist sets by choosing what white becomes. Our visual direction already plans "a frame graded in a paint program with a reference strip in it becomes the game's lookup table". In URP that table is the Color Lookup override.

**Exposure.** Ghost exposes from illuminance (how much light falls), using image luminance only for very bright highlights. Our rigs type an exposure per hour (0.05 in the morning to 0.6 at night), and the style and mood add to it. Typed exposure and typed albedo push each other: Sucker Punch found the loop drove albedos too dark and stopped it with a reference chart.

**Value structure.** Painters squint and work in notan; we check five values at one-eighth in greyscale (`light_sheet.py notan`). Cinematographers use false colour, each band of exposure one colour, so a value plan can be checked live (secondary). Robert Yang (GDC 2018) asks lighters to check albedo histograms, because "darker albedos produce much darker rooms than you'd think". URP's Rendering Debugger flags albedo outside a luminance range, but it only sees URP's own Lit shaders: our shade function bypasses it, so we need our own views.

**Mood and weather states.** The masters blend: Ghost's indirect light follows every weather state; RDR2's atmosphere is one system. Our four grading layers with one owner each (`visual-direction.md`, Mood) are sound and match the cinematographer's rule that a mood never changes the hue of a source. What we lack is the blend between weather states and hours, because each rig is a separate hand-typed asset.

## 5. Weather and light

**Wet surfaces** (Sébastien Lagarde, 2013): only porous materials darken when wet, mostly through subsurface scattering; mid albedos darken most (0.12 dry to about 0.08 wet). In a game: diffuse times `lerp(1, 0.2, porosity)` by wetness; gloss raised towards water's, the boost held to half; smooth parts treated as non-porous; a thin film smooths the normal a little; a puddle is flat water with a mirror reflection. Drying is a sigmoid; a minute's lerp is enough in a game, and puddles dry last. Ripples show only where there is light to see them. Rain fog desaturates with heavier rain and is "a necessary feedback for the player". He budgeted 3 ms at 30 fps for rain's core effects. Our surface darkens porous stone to at most half (`StreetSurface.hlsl`) and our water layer (`water.py`, `Water.hlsl`) already knows where water lies and runs, which is more than Lagarde had.

**Fog and rain** soften every light; a lamp in rain throws a halo as in fog. Lagarde approximates it with bloom; our airlight pass does it from the fog's density, which is better.

**Snow** is the brightest common surface, about 0.9 albedo (Lagarde). Snow on the ground multiplies the light thrown up into every shade, and shade on snow goes blue from the sky. Assassin's Creed Shadows bakes its seasons separately for this reason (secondary). Our `_OS_SunBounce` assumes ground of a third albedo in every weather.

**The seasons' light at 59° north**, computed for Stavanger:

| Date | Sun at noon | Day | Civil twilight, each end | At midnight |
| --- | --- | --- | --- | --- |
| 21 December | 7.6° | about 6 hours | 55 minutes | deep night |
| 20 October | 19.6° | 9.6 hours | 42 minutes | deep night |
| 21 June | 54.5° | about 18.5 hours | 87 minutes | 7.6° below the horizon: nautical twilight all night |

The long blue hour is a fact of latitude, and so are the light nights of June.

## 6. How lighting artists work and judge

- **Key lighting, then propagation.** Sony Imageworks had Hotel Transylvania 3, Smallfoot and Spider-Verse in lighting at once (SIGGRAPH 2018). Each sequence is lit from one key rig over branches, one per key shot, each with sparse local overrides. "One change in the key gaffer can affect all shots", and the lighter sees the change on every shot at once. Master lighting sets the environment; shot lighting finishes the characters (secondary).
- **Big shapes first.** Ambient and key before secondary lights; big shapes, then middle, then small (secondary, a lighting artist's account). Robert Yang's level lighting order: greybox, global light and mood, light for the path, set pieces, then a texture and colour pass, then a review of who is lit well.
- **Three-point lighting depends on the camera.** "Three point light types depend on the light's orientation relative to the camera" (Yang): a rim from one heading is a key from another. With a free camera and lights that are facts, we cannot place rims per shot; the camera's favoured side views and the air towards the sun do that work.
- **Colour scripts and keys.** One key per sequence (Pixar); one per story beat (Firewatch); Pixar's chapter "Storytelling through Lighting" (Calahan, in Advanced RenderMan) sets the functions: direct the eye, convey time of day and season, carry mood (secondary, table of contents).
- **Reviews.** Daily reviews judge each shot beside its neighbours (secondary). Ghost's diffuse chart, false colour, histograms and greyscale are the instruments. Our contact sheets across cameras and hours are our dailies; what they lack is a chart and the light split into its terms.

## 7. Our light system against the craft

### What we do right

- **One shade function for every surface** (`OS_ShadeP`), shade from the light and never the object. SEASON, Disco Elysium and Arcane each paid to learn this; we started with it.
- **Parts carry visibility, not light.** `bake.py` writes what each face sees (sky, ground, openness), as Disco Elysium's shadow and lightfield maps and Ghost's sky visibility do. Colour stays the material's; light stays the rig's.
- **The sky map.** A runtime sky occlusion for a whole town, redrawn when the town changes, and read by anything that moves. APV sky occlusion is the same idea, frozen at bake time.
- **The sun from the clock** (`Daylight.cs`), never typed.
- **Air in coloured layers** (Firewatch), a fog bank thick over water, a town glow map that lights the fog from below, and halos computed as airlight that grow with distance (`FogLights.shader`). This is closer to RDR2's thinking than to a filter.
- **Grading in four layers with owners**, and a mood that may not change the hue of a light or the weather. Cinematographers work so.
- **The value rule, measured.** A five-value notan at one-eighth, with shares counted.
- **Lamps as facts by era** (`TownLights.cs`).

### The four debts, and the craft they point to

| Debt | Fix made | What it guessed | The masters' way | The lasting fix |
| --- | --- | --- | --- | --- |
| 1. Under uniform overcast an upright cylinder had no lit side | A typed sun-side horizon colour in the drizzle rig, a third brighter | That the sky's bright side is a horizon colour an artist types | Ghost's 25% directionality boost; Naughty Dog's dominant directionality; the CIE overcast sky, three times brighter at the zenith, brighter round the hidden sun | Derive the hemisphere terms from a sky model: CIE overcast with a sun indicatrix in drizzle, a physical clear sky otherwise. The bright side and the top-light come from the sky itself; a directionality dial stays for art. |
| 2. In low sun, shade sides took warm ground bounce beside blue ground shadow | `OS_GroundLight`: the ground counts as lit if the face turns towards the sun | That facing the sun means looking at lit ground | Ghost bounces sun off an imaginary ground and wall, scaled by cloud shadow; full GI traces what the face sees | Look: sample the sun's shadow at the ground point in front of the face (a metre or two out along its normal, dropped to the ground height from the sky map). One or two extra shadow lookups. |
| 3. Screen-space occlusion crushed contact shade to black | Lower intensity (0.6), short reach (0.3 m), high samples | That occlusion is a darkening to black | Occlusion removes only indirect light, and less on bright surfaces, in their colour (GTAO multi-bounce); specular occlusion keeps reflections out of crevices | GTAO mode (already in URP 17.6); no occlusion on the sun (today a quarter of it reaches direct light, `DirectLightingStrength 0.25`); `GTAOMultiBounce` with the albedo; specular occlusion from the bake, the town and the AO. |
| 4. No sunlit-ground bounce in cast shadow | A face in a cast shadow gets none of the lit ground's bounce | That a face in shadow looks onto ground in the same shadow | As 2 | As 2. The fix made is wrong in a painter's favourite case: the shade under an eave, an awning or a balcony looking onto a sunlit street, which glows warm (Sorolla's reflected light). |

The pattern: every debt was the shade function guessing what a face sees, and every fix was another guess, each right for the frame that found it. The craft the masters use is to look. Three lookups cover it, all cheap in our system:
1. The sky's own radiance for the sky term, derived when the light changes, never typed beside the sky.
2. The ground a face looks onto: the sun's shadow at that ground point, and the ground's albedo for the season and the wet.
3. The town a face looks at: `OS_TownSky` already marches the height map in eight directions to find the horizon; at the same step it can tell whether the wall it hit faces the sun and is lit. Then the bounce into a lane's shaded side is warm where the opposite wall is in sun and cool where it is not, a fact, instead of one typed `townBounce` colour.

### What else should change

- **Reflections leak the sky in lanes.** The sky probe sees only the sky (`cullingMask = 0`), and nothing occludes it by the town, so wet stone at the foot of two walls mirrors open sky. Specular occlusion from the bake's sky, the town's openness and the AO (Frostbite's formula, in our SRP core) closes it.
- **A lamp's reflection is about twenty times too dim.** The lamp highlight in `OS_ShadeP` is Blinn-Phong without normalisation: its peak can never exceed the light's radiance. At a puddle's smoothness (0.97, an exponent near 1,700) the normalised peak is (n + 8) / 8π ≈ 69 times the radiance. Take a lamp on a 4 m post across a puddle seen from eye height ten metres off: the light's angle and the water's Fresnel at that grazing view bring the right peak to about twenty times ours. "Wet doubles the light" (masters-of-colour, rule 7) cannot happen until it is normalised; URP's own GGX specular would also give the streak towards the viewer. On-screen lamp glass is mirrored by screen-space reflections already.
- **Lamps drain colour, not only tint.** Give each lamp kind a colour rendition (how much it drains chroma from what it lights), so sodium flattens colour, mercury greys reds and incandescent keeps them. The eras then read apart in what they light, not only in their own colour.
- **The style pass belongs inside the grade.** Bake `Palette.shader` into the Color Lookup table whenever the light changes; dither at the last 8-bit write; test the fog nocturne for banding at full size.
- **Tone mapping needs a judged choice.** Neutral is per-channel; test it against a hue-preserving transform (a free AgX table through Color Lookup) on the night frames, judging whether sodium halos stay orange and white paint stays white.
- **Exposure from the light.** Compute it from the rig's illuminance on a horizontal plane, with the style's and mood's offsets on top, and put a chart in every sheet: our pigments, a grey card, white paint, a skin swatch. White staying white becomes a measurement.
- **Light in tiers, like geometry.** Near the camera: shadowed spot lamps pointing down (one atlas slot each), perhaps eight to sixteen. In the street tier: unshadowed lights. Beyond: emission, the glow map, and the glow map's light laid on the ground as a pool texture. `FogLights` loops over every lamp for every pixel; bin lamps to screen tiles first.
- **Far shadows from the sky map.** When the sun moves, march the height map towards it once and keep a sun-visibility map: hill and roof shadows at low sun across the whole town, past the last cascade, at no per-pixel cost. Set the shadow distance by the camera's stop.
- **The sky-map march costs 64 texture reads per pixel** (eight directions by eight distances, in every opaque shader). Precompute horizon angles, or a coarse volume of sky visibility with its direction (a bent normal), each time the town changes; then the shade reads two or three values.
- **The rig is about sixty-five typed settings per hour, seventeen of them colours** (`LightRig.cs`). Only the sun's bearing and elevation are derived. The morning and the drizzle have needed retuning since 20 October; every new hour and weather will need its own. Section 8 is the structure that ends it.

## 8. How the light should be built: one system under everything

Six layers, each with one owner, each reading only the layers above it:

| Layer | What it holds | Owner | How it changes |
| --- | --- | --- | --- |
| 1. The world's state | Date, hour, place; cloud cover and kind, rain rate, fog, wind; hours since rain, wetness, snow cover; the season (ground cover, leaves); which lamps are on and which rooms are lit | The engine and the setting pack (facts); `Daylight.cs` | Continuously; never typed for a look |
| 2. The physical light | Sun and moon direction, colour and illuminance (from atmospheric transmittance); sky radiance (CIE overcast blended with a clear-sky model by cloud cover); the sky term as hemisphere colours or SH, with direction; ground albedo and the bounce it throws; fog density and colour from the weather; exposure from illuminance | Code, derived | Recomputed when layer 1 changes; cheap |
| 3. The art key (the colour script) | Per band of the hour and per weather: the air's hue and chroma in each depth layer; how much colour shade keeps; directionality; the turning edge; an exposure bias; the sky's art parts (gradient, sun halo, horizon halo, cloud forms); in OKLCH, as pushes on layer 2, never replacements | Claude, judged by Øystein | Keyframed across the hour and blended across weathers; sparse overrides per place or scene, as Imageworks does per shot |
| 4. The style | The game's one style (`Style_game`) | Øystein | Rarely |
| 5. The mood | Exposure, contrast, shade colour, the lens | The game's direction per scene | Blends over seconds |
| 6. The lens | Bloom, halation, grain, vignette | With the mood | With the mood |

**What every shader reads, and may not do.** Every material reads the same globals: the sky term (with direction), the sun, the seen-ground and seen-town bounce, the lights in its tier, the air, the exposure. A material brings pigment, form and its water profile; it may not tint shade, carry its own light colour or own a grade. That is today's rule 1 and `foundations.md`'s "one home", kept.

**One light state, one record.** Layers 1 to 3 together are a record that can be saved, diffed, hashed and replayed: the light of 20 October 1989 at 17:50 in sea fog is one record, and any frame made under it can be rebuilt. Our sheets then work as dailies do: the same cameras under the same record, each change shown beside the last approved frame.

**Debug views in the shade function.** The URP debugger cannot see inside `OS_ShadeP`, so the shade should show its own terms on demand. Albedo alone; light alone (every pigment one grey, as the clay already does); then each term: the sky, the ground and town bounce, the sun, the lamps, the reflections. And a false-colour view of the five value bands. A debt is then found in one view, not argued from a frame.

## 9. What the building blocks must carry for the light

Every part, material and kind joins the light through data, never through its own lighting code:

| Data | Carried by | Why |
| --- | --- | --- |
| Sky, ground, openness per face (the bake: r, g, b) | Every part, every tier: merged city-tier meshes and impostors keep it | The sky term and contact. An impostor baked with lit colour would freeze one hour (Disco Elysium's first attempt). Tree crowns stay out of other parts' sky seen, with the canopy's optical depth in its own channel, or the bake freezes the season (§10). |
| The direction of open sky (a bent normal, two channels) | Every part, from the same ray fan in `bake.py` | Directional ambient without guessing (debt 1); the overcast top-light on a cornice. |
| Weather exposure (the bake's a, reserved) | Every part | How wet, how snowed on, how stained: the water and weather layers. |
| Albedo within a validated range | Every material, checked against the chart | Stops the exposure-albedo loop; keeps white white. |
| Porosity, smoothness, water profile | Every material (`WaterPack`) | Lagarde's wet model: what darkens, what shines, how long. |
| Translucency | Leaves, curtains, paper, sailcloth, glass | Backlight through things, at dusk and from lit rooms. |
| Emission group and kind | Windows, lamp glass, signs, shopfronts | Which fact turns it on (a room, a lamp's schedule, a shop's hours). |
| Light sockets | Lamps (position, cone, kind, era, shadow flag, an emitter radius, a distribution profile, an upward light ratio, static or moving, a stable lamp id: §11); windows (spill position, direction, cookie); shopfronts | The tiers place real lights from the sockets near the camera and fall back to emission and the glow map far off. |
| Room data behind a window | Windows: a room index, its lit state, curtain, interior-map variant | Interior mapping; lit rooms as facts. |
| A record for every light | Lamps and rooms, from the engine or the fixture | "Every light in the town is a fact" (`visual-direction.md`). |

**Probes.** No baked probes for generated places. Town-scale sky visibility is a runtime volume or horizon map rebuilt with the sky map; reflection probes are placed by the town generator at nodes (squares, lane mouths, the quay) and relit when the light record changes, a few per frame, as Ghost does.

## 10. Light under a canopy

Studied in LA (22 October) only as far as the light record and the shade's terms need, for a birch wood at a summer noon; the tree's build is 1e's. "(ours)" marks our own arithmetic from sourced numbers.

**Flecks are pictures of the sun.** The sun spans 0.53°, about a 108th of a radian, so every gap in a canopy is a pinhole that throws an image of the sun a 108th of its path length across, stretched on flat ground by one over the sine of the elevation (LibreTexts, the tree projector; Wikipedia, sunfleck). At a June noon at 59° N the sun is 54° high, and a gap 12 m up throws a fleck about 14 by 17 cm; at a 10° sun the same gap throws a streak 0.6 m wide and 3.7 m long (ours). A 5 cm birch leaf loses its sharp shadow about 5 m below it (ours). So the floor of a wood shows soft round flecks over an even shade, never leaf shapes, and a shadow's softness grows with the height of what casts it.

**How much reaches the floor.** By Beer–Lambert the share of the floor in direct sun is exp(−G·Le / sin h), with G about 0.5 for random leaf angles and Le the effective, clumped leaf area index (METER application note, secondary); broadleaves lie flatter than random, so G varies by species (Pisek and others 2013, abstract). A mature silver birch stand in Estonia measured an effective plant area of 3.6 to 5.8 (secondary). For the measured 3.6 to 5.8, 3 to 11% of the floor is in fleck at a June noon and its openness to a uniform sky is 2 to 8%; a thinner stand, at an assumed 2, gives up to 29% and 22% (ours). At a 10° sun almost none reaches the floor. Under closed canopies flecks bring 37 to 68% of the understorey's light, each lasting minutes as the sun moves (Canham and others 1990, secondary); wind adds flecks that last under a second (Pearcy 1988, secondary).

**The colour.** A green leaf reflects about 15% at 550 nm and 5% in the red, and across visible light reflects about 9% and transmits about 6% (secondary). Light through leaves is yellow-green, with blue cut most. Endler names four light habitats in a wood: forest shade, yellow-green, lit through leaves; woodland shade, blue-grey, lit by sky through gaps; small gaps, reddish, the sun's own light; large gaps, white. Under cloud all four become one open light (Endler 1993, abstract).

**The canopy is a second sky.** Shade under a clear sky is about 20 klux and direct sun about 110 klux (Wikipedia, orders of magnitude), so the mean blue sky is about 6.4 kcd/m². A leaf lit from behind, at an assumed 10% transmittance, glows at about 3.5 kcd/m², half the sky; leaves in shade are about ten times darker (ours). At 10% openness the leaves' light in the shade matches or beats the sky's, and is far greener (ours, rough). The sky term under trees is two skies: the sky through the gaps and the canopy's own radiance in the rest of the upper hemisphere.

**The season.** A dense deciduous canopy in full leaf passes under 2% of the light; a bare wood blocks up to two thirds, and an oak–hickory canopy passed 47% before leaf-out (secondary). Bare birch is probably brighter (unverified). NIBIO's phenological garden at Fana, Bergen, has logged leaf-out, colouring and leaf fall since 1964 (read): the pack's phenology table can come from it. A birch leaf yellows within about a week and then falls, and trees turn unevenly (secondary).

**How studios build it.**
- *Firewatch* placed 23 hand-made tree models about 4,600 times as meshes, not terrain trees, for control over their shading, with a simplified foliage shader (80.lv, read; secondary on the shader). Banded fog makes the depth layers between trunks. Its god rays come from the visible sun disc, moved by one manager with the sun, the fog and the grade (secondary): a screen-space effect. The aspen grove Øystein singled out is golden hour.
- *Ghost of Tsushima* keeps sky visibility in mono SH2 probes about 12.5 m apart, multiplied by a sky projected each frame in 60 µs (Patry 2021, read): too coarse for one tree's shade. Translucency was raised as an art lever. *Ghost of Yōtei* drives its god rays from a light-space cloud shadow map (PlayStation Blog, read).
- *Horizon* casts vegetation into the normal shadow maps in the near cascades and a height field further out (secondary); *Forbidden West* added a visibility buffer to speed up its alpha-tested foliage (Guerrilla, read).
- *Crysis* shades translucency as a painted map times a wrapped backlight and shades grass per vertex for fill rate; *SpeedTree* shifts backlight toward yellow and bakes ambient occlusion per vertex (GPU Gems 3, chapters 16 and 4, read). *Frostbite's* cheap translucency is a power lobe with a thickness map (secondary); *Unreal's* two-sided foliage passes a leaf's front light to its back through a subsurface colour (secondary).
- What they share: leaf-detail shadows only near, something coarse and cached far off; translucency as cheap arithmetic; the tree's occlusion per vertex; shafts from a light-space map.

**On our machine.** Alpha-tested fragments defeat the M4's hidden-surface removal (Apple, WWDC 2020 session 10632; Imagination, read), and they do so in every shadow cascade they are drawn into. Leaf detail therefore belongs in cascade 0 only. Beyond it, a small light-space canopy map (a one-layer deep opacity map: where the sun's ray enters the canopy, where it leaves, the optical depth between) gives flecks, the canopy's mean transmittance and, through its mips, a penumbra that grows with height; the beams and the air read the same map. Noon shafts under trees are 15 to 20 times weaker than at golden hour for a phase g of 0.7 (ours), so they show only with haze, a low sun or an upward look.

**What it asks of the light.**
- *Facts:* the trees' crowns (lobes, height, leaf area, clumping, leaf angle) and their leaf state and dieback, from the tree records; a thinned crown is history.
- *Derived:* the leaf stage from the date and the pack's phenology; the canopy map, rebuilt when the sun moves about half a degree or a tree changes; the canopy's openness kept as optical depth, so the season scales it by one multiply; the canopy's radiance, one colour a frame; the ground bounce through the floor's mean transmittance.
- *Material data:* leaf reflectance and transmittance by stage; translucency with a thickness.
- *Art keys:* how green the shade may go, fleck softness, leaf glow, beam strength, the air's layers between rows of trunks.
- *Honest flecks.* A projected fleck pattern does not lie if it follows the sun, takes its size from height over 108, keeps the canopy's mean transmittance and stays inside the crowns as projected along the sun. A big gap (a dead limb, a felled neighbour) carries history and must come from a fact; the seed makes only small gaps.

## 11. Many lamps at city scale

Studied in LA (22 October) for a dense street at night with many lamps in view, and later a metropolis, only as far as the record and the shade need; it goes beyond §3.

**One lamp list, the tier chosen per frame.** GTA V, a deferred renderer, draws near lights as volumes that pay only for the pixels they cover, which gives its wet-road highlights; far lights are instanced 32 × 32 sprites (Courrèges 2015). Modding documentation shows that real lights live in each model's asset and that a bake derives two far tiers per district: "LOD lights" keep direction, falloff, cone and corona, "distant LOD lights" only position and colour, and streetlights are sorted first so they switch together (secondary). Cyberpunk 2077 renders a fixed number of local shadow maps a frame, chosen by visibility and distance, each split into a cached static slice and a dynamic one, since most city lights never move (Dybisz and Witanowski, SIGGRAPH 2021). Unreal's MegaLights samples a few lights per pixel by importance and barely grows with the count, but needs hardware ray tracing (Arm). The pattern: one list of lamps, and per frame each takes a tier: lit and shadowed; lit; a corona and a pool; emission; the town's glow on fog and cloud.

**URP on the M4.** From URP 17.6's own source in our package cache: Forward+ ANDs a 2D tile bitmask with a depth bin (Drobot's z-binning, 2017), both rebuilt each frame by CPU jobs. The tile grows with the number of lights and probes: at 2560 × 1440, 16 px up to 32 items, 32 px up to 128, 64 px beyond, so the heart, capped at 256 of its 403, runs on 64 px tiles. Past the cap URP keeps the first 256 in the engine's order. URP has no cached shadows, so lamp shadows are redrawn every frame; HDRP has them. URP's deferred paths could keep the G-buffer on tile, but any pass that samples depth or normals as a texture forces a store (Unity, on-tile rendering), and our SSR, SSAO and `FogLights` do; deferred lighting would also bypass `OS_ShadeP`. No measured costs on Apple GPUs were found; on a Quest, 30 lights cost 12 ms forward and 8.5 ms Forward+, against 7.5 ms at 5 (Meta). So `OS_ShadeP` should read our own lamp buffer, binned by our pass as `FogLights`' already is, with URP lights kept for the shadowed few; the cap, the tile size and the per-lamp data become ours, and a later deferred or stochastic path reads the same buffer.

**Wet streets.** A normalised GGX highlight reaches a puddle whatever the screen shows, which screen-space reflections do not: near lamp heads are usually above the frame. A crisp lamp image needs Karis's widening for a sphere light (Karis 2013, Real Shading in UE4), so each lamp needs an emitter radius; GGX makes the streak towards the viewer. Far lamps are not lights, so their images in puddles must be drawn: a mirrored sprite on wet ground, stretched by roughness and the view (our proposal, unsourced). A lamp's halo lies within the rays that pass inside its reach, so lamps bin to screen tiles by a circle and a depth test; Sun and others (2005) put a point light's airlight in even fog into small tables, which our forward-scattering phase would need fitted (unverified).

**Colour rendition.** Spectral renders show sodium light overriding surface colour almost completely, and one grade per scene fails once lamps mix (Peters, read). Ward and Eydelberg-Vileshin (2002) make RGB exact for direct light under one illuminant by prefiltering, and Mallett and Yuksel (2019) write any sRGB reflectance as a weighted sum of three fixed spectra (abstracts). So, by our derivation, a surface's colour under lamp kind k is a 3 × 3 matrix times its albedo, computed offline from the kind's spectrum; mixed lamps each apply their own; low-pressure sodium's matrix has rank one, so every colour becomes one yellow. The data is a kind index per lamp and 36 bytes per kind; the cost nine multiply-adds per pixel per lamp. Spectra: CIE 015:2018's lamp tables (in colour-science); low-pressure sodium is the 589 nm line. How far colour drains and the eye's adaptation stay art keys.

**A lamp is not a switch.** Low-pressure sodium strikes red-pink and yellows over minutes; an ageing high-pressure lamp cycles off and on (secondary). Output and colour follow time since switch-on, age and upkeep: history a viewer can read, so it comes from the lamp's facts.

**The town's glow.** Cloud made Berlin's night sky 10.1 times brighter in the city and 2.8 times at 32 km (Kyba and others 2011, secondary). The light sent up is the luminaire's upward ratio (0% for full cut-off, 2 to 5% for drop lenses, about 10% for acorn tops; US DOE, secondary) plus what the ground reflects, less when wet. A cached town light map (ground pools, upward flux, the mix's rendition), rebuilt when a circuit switches, feeds the far tier and a cloud-base glow that becomes the night's sky term.

**What it asks of the light.**
- *Facts:* each lamp's kind, circuit, watts, era and upkeep; times per circuit, with sparse overrides; static or moving.
- *Part data:* the socket's position, aim and height, an emitter radius, a distribution profile, an upward ratio, a stable lamp id.
- *Derived:* output now (warm-up, age, cycling, per frame on the CPU); the tier per lamp by importance (per frame, never stored); our tile list; the static shadow slice per town cell (cached until the cell changes); the town light map; the cloud-base glow; the rendition matrix per kind (offline).
- *Art keys:* halo strength, how far colour drains, the eye's adaptation.

## 12. The light's range: what it asks of the record

LA tested five regimes on paper against the planned record and the shade's terms: the Row at blue hour, a birch wood at a summer noon, open heath in drizzle, a dense street at night and snow at low sun (`reviews/lt1/light/la-report.md`, with the line-by-line check and a drafted record). All five fit if L1 fixes thirteen things in the format. Five of them would otherwise force a rebuild:
- **Art keys keyed by the sun's signed elevation,** a continuous morning-to-evening weight and the weather, never the clock hour. At 59° N the same hour is noon in one season and dusk in another; keyed by elevation, June's light nights take the blue-hour key, which is true.
- **One sky:** a model's parameters, from which the ambient's L2 spherical harmonics, the dome and the reflection probes all derive. Overcast directionality, twilight, the night's cloud glow and the canopy's second sky are then content in one slot, and reflections never show a second sky.
- **Lamps by reference and by circuit.** The record holds the sources' hashes and the street circuits on; the lamp list lives in the facts, shop and room light in the people's habits, and the tier in the renderer per frame.
- **Nothing that depends on place or camera.** Ground cover, the cloud glow, the canopy and the town's light vary across one frame, so they live in maps, never in the record's scalars.
- **Caches stepped by absolute time.** Maps tied to the sun are built at a step index from absolute time and cross-faded between neighbours, never rebuilt "when the sun has moved", which would make a frame depend on the path taken to it; far shadows compare the sun with the horizon angles, continuously.

The record's identity is its inputs (the world state, the sources' hashes, the key set, the derivation's version); derived values are stored and checked within a tolerance, never hashed, since two languages may differ in a float's last bits. And every term has a clock, after `performance-craft.md` §2: per pixel; per vertex; per frame; per sun step; per fact (cached until the town, a tree, the season or a switch changes); offline. The regimes the corner does not show add mostly cached maps and per-frame colours, and few per-pixel taps.

## What we should do

Ranked by what each buys for the corner and the town. Costs are working days for Claude, before review.

| # | What | Cost | What it buys |
| --- | --- | --- | --- |
| 1 | **Look, don't guess, for bounce:** the seen-ground lookup (sun shadow at the ground in front of a face, ground albedo by season and wet) and the seen-town bounce in `OS_TownSky` (lit or shaded wall in each direction) | 1 to 2 | Debts 2 and 4 fixed at the root; warm reflected light under eaves and awnings; lanes split warm and cool by fact. Judged in low sun at the gully and on Harbour Row. |
| 2 | **Occlusion done right:** GTAO mode, no occlusion on the sun, `GTAOMultiBounce` on the sky term, specular occlusion from bake × town × AO | 0.5 to 1 | Debt 3 for good; no open sky mirrored at the foot of lane walls. |
| 3 | **The sky as the source of the ambient:** a CIE overcast model with a sun indicatrix for drizzle and a Hillaire-style clear sky, the hemisphere terms derived from it whenever the light changes | 3 to 5 | Debt 1's lasting fix; drizzle and morning retuned by one model instead of by hand; the base for any hour and weather. |
| 4 | **The rig as layers:** world state → derived light → art keys (OKLCH pushes, keyframed by hour, blended by weather, sparse overrides per place); the light record saved and hashed | 3 to 4 | Any date, hour and weather; transitions; the typed part of the rig shrinks from about sixty-five settings to a dozen pushes; sheets become replayable dailies. |
| 5 | **The colour pipeline in order:** the style pass baked into Color Lookup; dither at the last write; a judged tone-mapping test (Neutral against a hue-preserving table) on the night frames | 1 to 2 | No banding in fog nocturnes; lamp hues that hold; the painted-target LUT and the style in one table. |
| 6 | **Exposure from illuminance and a chart in every sheet** | 1 | Albedo kept honest (Ghost's loop avoided); white staying white is measured. |
| 7 | **Debug views of the shade's terms** and a false-colour value view | 1 | Faults found by term; reviews argue less. |
| 8 | **Night in tiers:** shadowed spot lamps near the camera, unshadowed street tier, glow map and ground pools beyond; `FogLights` and `OS_ShadeP` reading our own lamp buffer, binned by tile (§11); normalised lamp specular with an emitter radius; colour rendition as a 3 × 3 matrix per lamp kind | 5 to 8, spread over plan steps 3 and 6 | The town at night at frame rate; lamps that throw shadows of railings and people; puddles that double the lights; eras that read in what they light. |
| 9 | **Far shadows and the sky-map cost:** a sun-visibility map from the height map; shadow distance by camera stop; horizon or visibility volume precomputed when the town changes | 3 to 4 | Low-sun shadows across the whole town from the far stop; most of 64 reads a pixel saved; a bent normal at town scale. |
| 10 | **Lit windows with interior mapping**, each room's state from facts | 3, with the window part (plan step 2) | Depth behind every window; the town's life shown truthfully at night. |
| 11 | **Weather's light** to Lagarde's numbers through the water profiles: drying curve, ripples only in light, rain fog desaturation, snow albedo into the bounce, the seasons' ground | Inside plan step 9 | Weather that changes the light, not only the surfaces. |
| 12 | **Tests, not dependencies:** Surface Cache GI when 6.7 LTS ships (lamp and shopfront bounce at night, timed on the Mac); the MIT froxel fog package for sea-fog nights with window shafts | 1 each | Know whether real GI or volumetrics earn their cost before designing around them. |

## Gaps

- Talks not read in full: Jane Ng's Firewatch talk (video only; its fog read through write-ups); Bauer's RDR2 slides (232 MB); the INSIDE rendering slides (over 10 MB); Siim Raidma's Disco Elysium GDC 2020 talk; Vivian Ding's Last of Us lighting talk (abstract only); Kemenczy's Kentucky Route Zero talk. Nothing published on Breath of the Wild's or Tears of the Kingdom's lighting was found. The Assassin's Creed Shadows numbers came through a summary of its slides.
- Not tested in our project: GTAO with our custom shaders (whether it feeds the same occlusion texture `OS_ShadeP` reads); Surface Cache GI on Metal; the froxel package on Metal; whether APV can be baked at runtime.
- Not yet measured: the cost of `OS_TownSky` and `FogLights` at 1440p with the heart's 403 lights; how many lights Forward+ actually sees from each camera stop; banding in the fog nocturne at full size.
- Not researched here: the moon's light and phases as facts (the record keeps a slot, §12); light through glass from inside rooms (the interiors step); lightning. The town's light at city scale is studied only as far as the format needs (§11).
- Not read for §10 and §11: Jane Ng's Firewatch talk, still; Horizon Zero Dawn's vegetation talk in full; the MegaLights slides; Insomniac's procedural lighting talk for Spider-Man (abstract only); Cyberpunk's "Bringing Light to Night City" (abstract only); the leaf spectra datasets of Hovi and others (a download, waiting for Øystein's OK). No primary source on forest light was found for Alan Wake 2, Red Dead Redemption 2, The Witcher 3 or Far Cry, nor on night lighting for Spider-Man, Watch Dogs, Assassin's Creed Unity, Arkham Knight, Mafia, Sleeping Dogs or Ghost of Tsushima.
- Not measured, for §10 and §11: milliseconds per lamp in `OS_ShadeP` on the M4 at 32, 128 and 256 lamps; a shadow slot's cost; the canopy map's cost; west-coast birch leaf area and openness. Where each is learned: `reviews/lt1/light/la-report.md`, Open unknowns.
- `docs/foundations.md` still lists two light debts; the third and fourth are recorded in `docs/experiments.md` and in commits only.

## Decisions for Øystein

1. **Derived light under the art.** Should the rigs move from typed colours to a physical base with art keys on top (layers 2 and 3)? It changes how the light is tuned: pushes on a model instead of colours by hand. Recommended.
2. **The overcast night sky.** Under low cloud, a sodium-lit town's sky is orange-grey, a fact; the blue nocturne belongs to clear nights and to blue hour. Accept that the fact wins under cloud?
3. **Lamp glass.** May a lamp's glass clip to white, as in a photograph, with its hue carried by the halo and the light it throws, or should the glass keep its hue, as a painter would?
4. **Tone mapping.** Judge Neutral against a hue-preserving transform on the night frames, side by side.
5. **Real-time GI as a later layer.** Plan a test of Surface Cache GI when Unity 6.7 LTS ships, without depending on it.

## Sources

**Games and studios**
- Campo Santo, Firewatch's sky shader: https://blog.camposanto.com/post/112703721804/this-blog-post-is-an-in-detail-explanation-of-part
- Thumbsticks, GDC 2015 The Art of Firewatch (secondary): https://www.thumbsticks.com/gdc-2015-the-art-of-firewatch/
- 80.lv, Creating the World of Firewatch (secondary): https://80.lv/articles/creating-the-world-of-firewatch
- Firewatch fog reconstructions (secondary): https://halisavakis.com/my-take-on-shaders-firewatch-multi-colored-fog/ · https://grrava.blogspot.com/2018/08/stylistic-fog-from-firewatch-with.html
- Jasmin Patry, Lighting, Atmosphere, and Tonemapping in Ghost of Tsushima (SIGGRAPH 2021): https://www.advances.realtimerendering.com/s2021/jpatry_advances2021/index.html
- Eric Wohllaib, Ambient Diffuse Lighting in Ghost of Yōtei (GDC 2026, abstract): https://gdcvault.com/play/1035740/Ambient-Diffuse-Lighting-in-Ghost
- Jason Connell interviews on Ghost's colour (secondary): https://www.dualshockers.com/ghost-tsushima-art-director/
- Fabian Bauer, Creating the Atmospheric World of Red Dead Redemption 2 (SIGGRAPH 2019, abstract): https://advances.realtimerendering.com/s2019/index.htm
- How Shedworks refined the art of Sable (secondary): https://www.gamedeveloper.com/marketing/how-shedworks-refined-the-art-of-sable-in-pursuit-of-readability
- Aleksander Rostov, ZA/UM devblog, February 2016: https://discoelysium.com/devblog/2016/02/01/so-the-first-month-of-2016-has-come-and-gone
- Disco Elysium, From Render to Paintover (secondary): https://www.gamebanshee.com/news/121823-disco-elysium-from-render-to-paintover.html
- Ang, Catling, Cifariello Ciardi, Kozin, The Technical Art of Sea of Thieves (SIGGRAPH 2018): https://history.siggraph.org/wp-content/uploads/2022/09/2018-Talks-Ang_The-Technical-Art-of-Sea-of-Thieves.pdf
- Gjøl and Svendsen, Low Complexity, High Fidelity: INSIDE Rendering (GDC 2016, abstract): https://gdcvault.com/play/1023002/Low-Complexity-High-Fidelity-INSIDE
- Mikkel Gjøl, Banding in Games: A Noisy Rant: http://loopit.dk/banding_in_games.pdf
- Vivian Ding, In-Game and Cinematic Lighting of The Last of Us (GDC 2014, abstract): https://gdcvault.com/play/1020475/In-Game-and-Cinematic-Lighting
- Luis Antonio, The Art of The Witness (GDC 2014): https://www.artofluis.com/wp-content/uploads/2014/03/gdc2014_luisantonio_theartofthewitness.pdf
- Thumbsticks, GDC 2017 Designing Zelda: Breath of the Wild (secondary): https://www.thumbsticks.com/gdc17-designing-zelda-breath-of-the-wild/
- Tamas Kemenczy, The Scenography of Kentucky Route Zero (GDC 2014): https://gamedeveloper.com/design/video-the-scenography-of-i-kentucky-route-zero-i-
- Tiny Glade rendering (secondary): https://x.com/h3r2tic/status/1813197502411092186 · https://steamcommunity.com/app/2198150/allnews/
- Nikolay Stefanov, Deferred Radiance Transfer Volumes: Global Illumination in Far Cry 3 (GDC 2012, abstract): https://gdcvault.com/play/1015326/Deferred-Radiance-Transfer-Volumes-Global
- Nikolay Stefanov, Global Illumination in Tom Clancy's The Division (GDC 2016, abstract): https://gdcvault.com/play/1023273/Global-Illumination-in-Tom-Clancy
- Raytracing the World of Assassin's Creed Shadows (SIGGRAPH 2025; numbers via summary, secondary): https://www.realtimerendering.com/advances/s2025/content/Advances%202025%20-%20Raytracing%20the%20world%20of%20Assassin's%20Creed%20Shadows.pdf
- Joost van Dongen, Interior Mapping (CGI 2008): https://www.proun-game.com/Oogst3D/CODING/InteriorMapping/InteriorMapping.pdf
- Interior mapping in Spider-Man (secondary): https://gamedeveloper.com/programming/interior-mapping-rendering-real-rooms-without-geometry

**Rendering research**
- Sébastien Hillaire, A Scalable and Production Ready Sky and Atmosphere Rendering Technique (EGSR 2020): https://diglib.eg.org/handle/10.1111/cgf14050 · slides: https://blog.selfshadow.com/publications/s2020-shading-course/hillaire/s2020_pbs_hillaire_slides.pdf
- Bart Wronski, volumetric fog in Assassin's Creed IV (GDC 2014): https://bartwronski.com/wp-content/uploads/2014/03/ac4_gdc.pdf
- Andrew Schneider, The Real-time Volumetric Cloudscapes of Horizon Zero Dawn (SIGGRAPH 2015): https://www.advances.realtimerendering.com/s2015/The%20Real-time%20Volumetric%20Cloudscapes%20of%20Horizon%20-%20Zero%20Dawn%20-%20ARTR.pdf
- Jimenez, Wu, Pesce, Jarabo, Practical Realtime Strategies for Accurate Indirect Occlusion (Activision, 2016): https://research.activision.com/publications/archives/practical-real-time-strategies-for-accurate-indirect-occlusion
- Lagarde and de Rousiers, Moving Frostbite to Physically Based Rendering 3.0 (SIGGRAPH 2014): https://ea.com/frostbite/news/moving-frostbite-to-pb
- Sébastien Lagarde, Water drop 3b, physically based wet surfaces: https://seblagarde.wordpress.com/2013/04/14/water-drop-3b-physically-based-wet-surfaces/
- Sébastien Lagarde, Water drop 2b, dynamic rain and its effects: https://seblagarde.wordpress.com/2013/01/03/water-drop-2b-dynamic-rain-and-its-effects/
- Jorge Jimenez, Next Generation Post Processing in Call of Duty: Advanced Warfare (SIGGRAPH 2014): https://www.iryoku.com/next-generation-post-processing-in-call-of-duty-advanced-warfare/
- Christophe Brejon, ACES and display transforms: https://chrisbrejon.com/cg-cinematography/chapter-1-5-academy-color-encoding-system-aces/
- Jensen and others, A Physically-Based Night Sky Model (SIGGRAPH 2001): https://graphics.ucsd.edu/~henrik/papers/nightsky/
- Khan and Pattanaik, Modeling Blue Shift in Moonlit Scenes by Rod Cone Interaction (title only, not read)

**Unity**
- Changing APV lighting at runtime: https://docs.unity3d.com/Manual/urp/probevolumes-understand-changing-lighting-at-runtime.html
- APV sky occlusion: https://docs.unity3d.com/Manual/urp/probevolumes-skyocclusion.html
- New ways of applying global illumination in Unity 6: https://unity.com/blog/engine-platform/new-ways-of-applying-global-illumination-in-unity-6
- Surface Cache GI preview: https://discussions.unity.com/t/surface-cache-gi-preview/1720494 · reference: https://docs.unity.com/en-us/engine/6000.7/manual/lighting-overview/lighting/surface-cache-gi-volume-override-reference
- URP GTAO preview: https://discussions.unity.com/t/preview-of-urp-ground-truth-ambient-occlusion-gtao/1724061/1
- Forward+ limits: https://docs.unity3d.com/Manual/urp/rendering/forward-plus-rendering-path-limitations.html · light limits: https://docs.unity3d.com/Manual/urp/lighting/light-limits-in-urp.html
- Shadow atlas: https://docs-alpha.unity3d.com/Manual/urp/set-size-shadow-atlases.html
- Tonemapping (6.6): https://docs.unity3d.com/Manual/urp/post-processing-tonemapping.html
- Color Lookup: https://docs.unity3d.com/Manual/urp/post-processing-color-lookup.html
- Light component, rendering layers, cookies: https://docs.unity3d.com/Manual/urp/light-component.html
- AgX LUTs for Unity (community): https://github.com/unitycoder/AgX-Tonemapping-Unity
- Unity-URP-Volumetric-Light (MIT): https://github.com/CristianQiu/Unity-URP-Volumetric-Light
- URP 17.6 source in this project: `ShaderLibrary/Color.hlsl` (`NeutralTonemap`), `Shaders/PostProcessing/LutBuilderHdr.shader`, `UberPost.shader`, `CommonLighting.hlsl` (`GTAOMultiBounce`, `GetSpecularOcclusionFromAmbientOcclusion`), `universal-config/ShaderConfig.cs.hlsl`, `Runtime/Overrides/ScreenSpaceAmbientOcclusionVolumeOverride.cs`, `Runtime/RendererFeatures/SurfaceCacheGIRendererFeature/`

**Light, sky and place**
- CIE overcast sky formula (secondary): https://colour.readthedocs.io/en/latest/generated/colour.phenomena.sky_luminance_distribution_overcast_CIE2003.html · CIE: https://www.cie.co.at/publications/cie-standard-overcast-sky-and-clear-sky
- Nordic Light and Colour (NTNU, 2012), the daylight factor: https://ntnu.no/trykk/publikasjoner/NordicLightAndColour_2012/files/assets/seo/page79.html
- Vertical sky component (secondary): https://help.iesve.com/ve2021/14_3__vertical_sky_component.htm
- Kyba and others, Cloud Coverage Acts as an Amplifier for Ecological Light Pollution (PLoS ONE 2011; secondary): https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3047560/
- Sodium-vapor lamp: https://en.wikipedia.org/wiki/Sodium-vapor_lamp · Mercury-vapor lamp: https://en.wikipedia.org/wiki/Mercury-vapor_lamp
- Stavanger, Våland observations: https://yr.no/en/statistics/graph/1-506436/Noreg/Rogaland/Stavanger?q=2023-10
- Solar positions for Stavanger: computed (Cooper's declination, refraction 0.833°), as `Daylight.cs` does

**How lighting artists work**
- Chen and Miller, GafFour and Sequence-based Lighting (Sony Imageworks, SIGGRAPH 2018): https://history.siggraph.org/wp-content/uploads/2022/09/2018-Talks-Chen_GafFour-and-Sequence-based-Lighting.pdf
- Robert Yang, GDC 2018 How To Light A Level: https://www.blog.radiator.debacle.us/2018/03/gdc-2018-how-to-light-level-slides-and.html
- Kahrs, Calahan, Carson, Poster, Pixel Cinematography (SIGGRAPH 1996, contents): https://history.siggraph.org/wp-content/uploads/2021/08/1996-30-Contents-Pixel-Cinematography-A-Lighting-Approach-for-Computer-Graphics.pdf · Advanced RenderMan, chapter 13 (secondary): https://shop.elsevier.com/books/advanced-renderman/apodaca/978-0-08-049882-9
- Master and shot lighting (secondary): https://theinterviewportal.com/2017/11/11/animation-film-lighting-professional-interview/ · https://intogames.org/news/how-do-you-become-a-lighting-artist-for-videogames
- Wet-downs in night cinematography (secondary): https://nofilmschool.com/dp-secret-weapon-water
- False colour exposure zones (secondary): https://www.newsshooter.com/2025/02/04/arri-logc-false-color-exposure-zones-key-white-paper/
- Halation (secondary): https://blog.dehancer.com/articles/halation/

**Light under a canopy (§10)**
- The tree projector: https://phys.libretexts.org/Bookshelves/Astronomy__Cosmology/Astronomy_for_Educators_(Barth)/12%3A_Safely_Observing_the_Sun/12.3%3A_The_Tree_Projector
- Sunfleck: https://en.wikipedia.org/wiki/Sunfleck
- Canham and others 1990, light beneath closed canopies (secondary): https://andrewsforest.oregonstate.edu/node/13447
- Pearcy 1988, lightflecks (secondary): https://publish.csiro.au/FP/PP9880223
- METER, leaf area and interception (secondary): https://library.metergroup.com/Application%20Notes/13427_Calculation%20of%20LAI%20INterception%20of%20Short%20Canopies_Print.pdf
- Pisek and others 2013, leaf inclination (abstract): https://cris.vtt.fi/en/publications/is-the-spherical-leaf-inclination-angle-distribution-a-valid-assu/
- Silver birch plant area at Järvselja (secondary): https://reference-global.com/article/10.2478/fsmu-2019-0007
- Seasonal transmittance of a deciduous forest (secondary): https://ams.confex.com/ams/pdfpapers/79972.pdf
- Baldocchi, radiation through vegetation (secondary): https://biometlab.cnr.berkeley.edu/biometlab/espm129/notes/Lecture_9_Solar_Radiation_Transfer_Through_Vegetation_part_2_Notes_2014.pdf
- Endler 1993, the colour of light in forests (abstract): https://deakin.figshare.com/articles/journal_contribution/The_color_of_light_in_forests_and_its_implications/20874970
- Orders of magnitude, illuminance: https://en.wikipedia.org/wiki/Orders_of_magnitude_(illuminance)
- NIBIO, phenological time series: https://nibio.no/tema/landskap/tidsseriar-for-fenologiske-observasjonar
- Hovi and Rautiainen 2020, spectra under canopies (not read): https://research.fi/en/results/publication/0368831920
- Patry 2021, Ghost of Tsushima: https://www.advances.realtimerendering.com/s2021/jpatry_advances2021/index.html
- Ghost of Yōtei's technology: https://blog.playstation.com/?p=411201
- Guerrilla, deferred texturing in Horizon Forbidden West: https://www.guerrilla-games.com/read/adventures-with-deferred-texturing-in-horizon-forbidden-west
- Horizon Zero Dawn vegetation (abstract): https://gdcvault.com/play/1025066/Between-Tech-and-Art-The
- GPU Gems 3, chapter 16 (Crysis vegetation): https://developer.nvidia.com/gpugems/gpugems3/part-iii-rendering/chapter-16-vegetation-procedural-animation-and-shading-crysis
- GPU Gems 3, chapter 4 (SpeedTree): https://developer.nvidia.com/gpugems/gpugems3/part-i-geometry/chapter-4-next-generation-speedtree-rendering
- Barré-Brisebois, cheap translucency (secondary): https://frostbite.com/frostbite/news/approximating-translucency-for-a-fast-cheap-and-convincing-subsurface-scattering-look
- Unreal, shading models (secondary): https://docs.unrealengine.com/4.27/RenderingAndGraphics/Materials/MaterialProperties/LightingModels
- Apple, WWDC 2020 session 10632: https://developer.apple.com/videos/play/wwdc2020/10632
- Imagination, do not use discard: https://docs.imgtec.com/starter-guides/powervr-architecture/html/topics/rules/do-not-use-discard.html
- Deep opacity maps (secondary): https://diglib.eg.org/handle/10.2312/CGF.v27i2pp675-680

**Many lamps at city scale (§11)**
- Courrèges, GTA V graphics study, part 2: https://www.adriancourreges.com/blog/2015/11/02/gta-v-graphics-study-part-2/
- Sollumz, LOD lights (secondary): https://docs.sollumz.org/documentation/maps/lod-lights
- Dybisz and Witanowski, shadows in Cyberpunk 2077 (SIGGRAPH 2021): https://history.siggraph.org/wp-content/uploads/2022/06/2021-Talks-Dybisz_Shadows-Optimizations-in-Cyberpunk-2077.pdf
- Arm, MegaLights on mobile: https://developer.arm.com/community/arm-community-blogs/b/mobile-graphics-and-gaming-blog/posts/lighting-at-scale-bringing-hundreds-of-dynamic-lights-to-mobile-with-unreal-megalights
- Drobot 2017, improved culling (secondary): https://www.advances.realtimerendering.com/s2017/2017_Sig_Improved_Culling_final.pdf
- URP 17.6 source, local: `ForwardLights.cs`, `UniversalRenderPipeline.cs`, `Clustering.hlsl`, `DeferredPass.cs`, `universal-config/ShaderConfig.cs`
- Unity, on-tile rendering (secondary): https://docs.unity3d.com/6000.6/Documentation/Manual/on-tile-rendering.html
- HDRP mixed cached shadows (secondary): https://github.com/Unity-Technologies/Graphics/pull/1559
- Apple, deferred lighting sample: https://developer.apple.com/documentation/metal/rendering-a-scene-with-deferred-lighting-in-objective-c
- Meta, Forward+ in Unity: https://developers.meta.com/horizon/documentation/unity/unity-forward-plus-rendering/
- Karis 2013, Real Shading in UE4: https://cdn2.unrealengine.com/Resources/files/2013SiggraphPresentationsNotes-26915738.pdf
- Sun and others 2005, airlight (abstract): https://www.cs.columbia.edu/~bosun/sig05.htm
- Peters, spectral rendering results: https://momentsingraphics.de/SpectralRendering3Results.html
- Ward and Eydelberg-Vileshin 2002 (abstract): https://diglib.eg.org/items/c0b94b25-e457-4ce8-91ca-9a7eab4a36e8/full
- Mallett and Yuksel 2019 (abstract): https://diglib.eg.org/items/bbffa865-e99c-4c1f-bd33-70102dc8af78/full
- colour-science, Mallett 2019: https://colour.readthedocs.io/en/latest/_modules/colour/recovery/mallett2019.html
- CIE, high-pressure discharge lamp spectra (secondary): https://cie.co.at/datatable/relative-spectral-power-distributions-high-pressure-discharge-lamp-illuminants
- Kyba and others 2011 (secondary): https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3047560/
- US DOE, sky glow (secondary): https://www.energy.gov/sites/prod/files/2017/08/f35/Sky-Glow-Technical-Webinar_8-03-17_1.pdf
