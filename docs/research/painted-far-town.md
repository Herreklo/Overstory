# The painted far town

How to draw the town past about 50 m as a painting baked from the near models, as films use matte paintings, instead of distance versions for every kind (`docs/plan.md`, Leaner without losing brilliance, item 1). Øystein: "I would have to see this, but sounds promising." This study makes the idea work under our constraints and designs the look test he will judge. Nothing is built here.

Written on Opus, October 2026, with one helper pass on matte painting, painterly far fields and painterly bakes. Claims from a maker's own words, a paper or official documentation are unmarked; those from write-ups, abstracts or search excerpts are marked (secondary), and those no source confirmed (unverified). Our own numbers are marked (our arithmetic) or (our estimate).

## In short

- **A picture cannot be our backdrop.** A painting projected from one view is right only there: when our free camera glides 20 m, a block 300 m away drifts about 24 pixels (our arithmetic).
- **So the painting goes onto geometry, in texture space.** Past the hand-over each thing (a house, a flight, a wall run, a crown, the ground) is drawn as a *shell*: a coarse mesh from its plan, merged per cell. It carries painted albedo and normals baked from its near model. Being real 3D, shells keep parallax exact from any camera.
- **The light stays live.** A shell stores no light. The town's one shade function lights it every frame, under the same sky model, art keys and air as everything else. Wetness, snow, season and lit windows come from channels and records.
- **Each mip is painted from its own guide** with a brush fixed in texels, so marks keep their size on screen and small marks dissolve into a thing's tone as it recedes: the painted-marks study's octave rule, baked.
- **A jump of years rebakes only what changed.** Repaints and drift are live. A change of shape or mark rebakes one thing, 5 to 15 ms of GPU per house, so a thirty-year jump costs about 0.3 s for the view, done before the cut (our estimates).
- **Every pixel stays pickable,** because a shell triangle carries its thing and part.
- **It replaces every kind's city, district and far levels with one baker and one shader,** so a new kind, era or district gets its far field for nothing. The price is memory: the painting is unique, about 1.6 MB a house at 3 cm a texel (our arithmetic).
- **The look test** sets the shell beside conventional distance versions in the corner's far views, in three lights, in stills and motion sheets at the player's size, with cold readers and the M4's frame time. Six findings would drop it; the fallback is the plan's own district level, made from the same data.

## 1. What the craft does

### Film: paintings on geometry

A 2.5D matte painting is cut into grounds: rough geometry for the near ones, flat cards for the far ones and the sky. Each is painted with what lies behind it, so no hole opens as they slide (Vittani, Nuke breakdown, 2020). A side the projector never saw breaks the shot; the fix is a second projector (shootfirst.art, secondary).

Shade and others state the limit: an image's error grows with the depth inside it and with how far the camera moves from where it was made, and falls with its distance (layered depth images, 1998). Hierarchical image caching drew parts of a forest scene as cached images, re-rendered when an error passed a threshold, for about a tenfold speed-up (Shade, 1996). These are real-time matte paintings, and each re-renders the geometry behind it when the camera moves.

Relighting also comes from geometry. Tears of Steel mapped its paintover onto low-resolution geometry, which "will allow for a certain level of relighting". Nuke's Relight lights an image from its normal and position passes (secondary). Deep Canvas stored each stroke on the surface it hit, but with the artist's colour, so its light was painted in.

### Games: the far field as its own object

GTA V draws Vinewood Hills, dozens of houses, as "a single draw-call pushing only 2500 triangles"; Cities: Skylines 1 bakes every building onto a far mesh of about 100 triangles with 128² textures (`performance-at-scale.md`). Spider-Man 2 found hand-made distant levels "no longer viable" and automated them (GDC 2024 abstract, secondary). Ghost of Yōtei "improved the appearance of distant mountains by baking models and detailed terrain materials into textures". Breath of the Wild draws distance in three layers and simplifies with distance, "like paintings omit information", with real-time haze (CEDEC 2017, secondary). Firewatch had "painterly distant mountains" shaders, whose technical post we never found (Campo Santo blog, 2014, search excerpt). None uses one painted image for a world the camera crosses.

### Impostors lit live

Octahedral impostors (Ryan Brucks, for Fortnite) capture a model from many directions and blend the three nearest views. Lit versions store albedo, a normal that replaces the mesh's in lighting, and depth for parallax (Unigine, secondary); hemi-octahedral layouts give more resolution to a camera above (Amplify, secondary). They pay for things that repeat. One Unity user saw frame time rise from 6.4 to 7.3 ms after cutting triangles fourfold (secondary). Our buildings are unique and boxy, and impostors are alpha-tested, which the M4 dislikes.

### Painting the albedo, not the light

Adobe's tutorial runs Substance Designer's anisotropic Kuwahara (2024) on the base colour *and* the normal map with one shared direction map. Victor Kam ran Kuwahara over a lit Unreal scene, stronger with distance, and concluded "no to runtime". Praun's tonal art maps take tone from the light and draw strokes unlit, nested across mips so that "existing strokes persist while a few new strokes fade in". Spider-Verse's hatching had to "react to both lighting and his movement" (Foundry, secondary).

What paints colour alone bakes the light in. What keeps the look under changing light lets the light shape the marks. Painted albedo and normals, lit live, sit between; no source tests them under a moving sun.

| Technique | Where the painting lives | Light | Parallax | For us |
| --- | --- | --- | --- | --- |
| Projected matte painting | one view | baked | right near the projector | not inside the land |
| Image cache with depth | one view, refreshed | live with a G-buffer | re-rendered as the camera moves | not leaner: needs the geometry anyway |
| Octahedral impostor | many views per object | live | approximate | repeated things, not unique houses |
| Proxy mesh with baked maps (HLOD) | texture space | live if inputs are baked | exact | the base of the design |
| Kuwahara on albedo and normals | texture space | live | exact | the painting |

## 2. Why a picture cannot be our backdrop

A projection's error at 1440p with the 35 mm lens, for a camera moved from where the painting was made (our arithmetic: move × depth ÷ distance², a first-order form of Shade's rule):

| Distance | Depth inside it | Camera moved | Error | Move allowed for 1 px |
| --- | --- | --- | --- | --- |
| 100 m, a block | 20 m | 5 m | 22 px | 0.23 m |
| 300 m, across the Basin | 50 m | 20 m | 24 px | 0.8 m |
| 1 km, the far shore | 200 m | 100 m | 44 px | 2.3 m |
| 30 km, the mountains | 5 km | 2.5 km | 30 px | 82 m |

A projected painting would need re-rendering every metre of travel, from geometry we would keep anyway. And from the far stop, 120 m up, everything in frame is past 50 m. There the "backdrop" is the whole picture the player navigates by, and must carry history, era and picking as the main view.

| Constraint | Rules out | Leaves |
| --- | --- | --- |
| Live light (`lighting-and-colour.md` §8 to 9) | lit colour in any bake | albedo, normals and light-bake channels, lit by `OS_ShadeP` |
| The date changes | one bake per town per date | bakes per thing, keyed by the record's hash; drift live |
| Free camera | single-view images and cards inside the town | world-space geometry at every distance |
| The M4's tiles | alpha-tested far cards, small triangles | opaque shells, few draws |
| No swimming | screen-space painterly filters | marks fixed in texture space, sized by mip |
| History from afar | averaging to grey | a painting that keeps edges between things and causes |
| Pickable | pixels with no owner | thing and part per triangle |
| A dense town | unique maps without streaming | mips streamed by distance, baked on demand |

## 3. The design: a painted shell

### What a shell is

A shell is one thing's coarse mesh, made from its plan's volumes, with relief that never makes a silhouette (trim, laps, joints) moved into its painted normals. A house keeps walls, roof planes, eaves, chimneys, dormers, porch and shallow window insets, since a reveal shows its side from an angle: about 500 to 1,500 triangles (our estimate). A flight becomes a stepped ribbon, a wall a ribbon with its true top line, the ground a terrain patch with breaklines and a skirt, a railing a thin ribbon. Things that move or carry a live light (lamps, boats, people, laundry, vehicles) keep their own cheap instanced levels and are culled by screen size, as planned.

Shells are merged per 32 m cell, one mesh and one atlas page each. Past about 200 m a block level of about 100 triangles a house is merged per 128 m. It samples the same atlas's small mips through UVs projected from the shell, so it needs no second bake (the pattern of Unreal's merged and simplified HLOD layers). Trees keep their own levels to about 200 m, where a 10 cm sway is about a pixel (our arithmetic). Beyond, a crown becomes a few opaque lobes with a notched edge and soft normals: Firewatch's "puffier" far tree without the cut-outs. The land runs to the horizon as coarse terrain shells, Ghost of Yōtei's route; a card is left only for what lies beyond the land model.

### What a texel stores

| Map | Channels | Format | Why |
| --- | --- | --- | --- |
| Albedo | painted pigment at the bake date, slow history composited (coats, repairs, stains, signs); A: top-coat mask | BC3 | the painting; a repaint shifts the top coat live |
| Normal | painted, small relief flattened into planes; lost relief folded into roughness (Toksvig) | BC5 | the light models planes, as a painter simplifies form |
| Light and weather | sky openness, ground seen, rain exposure, water | BC3 | the sky term, contact, wetness and snow, live |
| Index | window index; the year of the surface's last reset | R8G8, half resolution, unfiltered | lit windows from room records; drift from the date |
| Per triangle | cell-local thing index, part slot, material class | flat vertex data | picking, highlight, the material's rates |

About 3.5 bytes a texel, 4.7 with mips (our arithmetic); the bent normal is dropped. The pigment with its slow history is the one output baked, against the performance study's rule, because a painting must work on how a thing looks. Light and weather, the rule's reason, stay inputs.

### How it is painted

For each thing's rectangle in its cell's atlas:
1. **Project the near model onto each face.** Each planar face gets its own orthographic camera, square to it, and the near model is rendered unlit into the face's rectangle: albedo at the date, normal, history channels, thing and cause ids. It is the film's projection with a projector per face, so no face is seen from the side. Rock and crowns are baked by rays.
2. **Paint with a joint filter.** Anisotropic Kuwahara runs on the albedo, steered by albedo, normals and id edges. Its per-texel weights are applied to the normals and history channels too, so all share the strokes (our extension of Substance's shared direction map, untested). It never crosses a thing's edge and stops at a cause's edge: it may merge marks of one cause, never bleed a stain onto the next house. In flat areas it returns the mean, and strokes there follow the material (boards along, courses flat), never noise, so it adds no false runs.
3. **Paint each mip from its own guide,** at a fixed radius in texels, with the brush's strokes drawn into the pigment at a fixed length in texels. Trilinear filtering then cross-fades the octaves. If that breathes in the pull-out, coarser mips are painted from finer ones instead, so regions merge but never move (Praun's rule).
4. **Ramp the painting** from about 2 px on screen at the hand-over to about 10 px by 200 m. The shell then starts close to the near model and becomes a painting where it is only one (Kam's distance ramp).
5. **Compress and cache** on the GPU (Betsy, open source, covers BC1 to BC5), keyed by the thing's hash.

The 1989 town is made once and curated (`NOW.md`), so its shells ship as the starting cache. Play rebakes what play changes, in the player (`where-generation-runs.md`).

### What stays live

| Change | How the shell follows | Rebake |
| --- | --- | --- |
| Hour, sky, art keys, air | `OS_ShadeP`; the air's depth layers give the far colour, as Firewatch's did | none |
| Rain, wetness, snow | the material's water profile with the exposure and water channels; snow by normal | none |
| Season | tint by material class; bare winter crowns are a gap | none |
| Drift: lichen film, fading, silvering | closed forms from years since reset and the material's rates | when drift since the bake passes one value step |
| A repaint | the part's coat from its record, over the top-coat mask | none until the next rebake |
| Lit windows | room records in a per-cell buffer, by window index | none |
| A dormer, sign, roof, extension, felled tree | the thing's shell and rectangle | that thing only |

Shells cast into the cascades past the near ring, and block meshes into a last cascade stretched over the far stop's view, since a low sun's long shadows are part of the far read. The Basin's reflection redraws the shells, which are cheap to draw twice.

### The free camera and the hand-over

The hand-over is set by error in pixels (`performance-at-scale.md`, rule 1). A shell's silhouette is true to about 2.5 cm, safe where a pixel covers more: about 50 m with the 35 mm lens, 75 to 90 m with the far stop's longer lenses. Four rules keep it invisible:
1. **The same data on both sides.** Shell and near model come from one record at one date and one shade function. The near tier's far end (`OS_Near` let go, history as two or three plates) and the shell's top mip are designed as one picture.
2. **Switch where they match,** measured at one-eighth in greyscale in the three lights.
3. **Fade per cell.** Each 32 m cell is one LOD group, its near chunks against its shell; URP's dithered cross-fade by distance works with the Resident Drawer. A 10% band with hysteresis stops a hovering camera from flickering.
4. **No cracks.** A thing belongs to one cell; walls and stairs are cut at piece boundaries; shell borders are locked to the neighbour's terrain and skirted.

### Rebakes and jumps

The time study decides the jump: hold everything but the year, and change is seen only where something jumps, so a far town updating a second late is a false second jump. Therefore:
1. The change query lists the things whose shape or marks differ between the dates.
2. Their rectangles are baked for the target date into spare space, nearest first and only to the mips the view needs; a house 400 m off needs a sixty-fourth of its texels.
3. At the cut every cell swaps at once. Unchanged things keep identical pixels, so a difference image shows only the record's changes, which we can check.

Per house, all mips at 3 cm, Kuwahara takes about 3 ms with four sectors or 11 ms with eight (scaled from the painted-marks study's 25 and 90 ms at 1440p). Rendering adds 1 to 2 ms and compression 1 ms. If a third of 300 houses in view change, the twenty nearest at full mips and the rest at small ones take 0.15 to 0.3 s of GPU (our estimates). The rest of the town catches up before the camera can reach it.

### Picking, history and era

Shell triangles are cut at things and parts and carry a cell-local thing index and part slot, with a table per cell, as the interface study asks of merged chunks. Windows resolve through the index map; a sign painted into a wall resolves to the wall, as far tiers should. Ids come from the record, so they survive rebakes.

The history budget asks at the city camera for one history per thing (kept or let go, a gap, a different roof), and at 12 m for coats by decade, window types per floor, a rebuilt panel (`history-in-things.md`). These are large shapes: a rebuilt panel 2 m wide is 66 texels at the top mip, and Kuwahara keeps edges where blur loses them. Era lives in what the shell keeps as geometry (roof forms, dormers, window proportions) and in lit windows by era.

### What it costs on the M4

| | Shell (our arithmetic or estimate) |
| --- | --- |
| A house's maps | 1.6 MB with mips at 3 cm a texel; 0.6 MB at 5 cm |
| A kilometre of street, houses both sides | about 320 MB at 3 cm, 115 MB at 5 cm |
| Resident for one view | 30 to 55 MB in the frustum, 170 to 300 MB for the full circle, two to three times that with the cells' slack; mips by distance keep it logarithmic in range |
| Disk, the 1989 centre | about 1 GB at 3 cm, 0.4 GB at 5 cm, as a cache of the record |
| Triangles, close stop to 1.5 km | 0.1 to 0.3 million, of a 2 million budget |
| Draws | about 100: 20 cells near, 75 blocks beyond |
| Pixels | four fetches and the shade function: 0.3 to 0.8 ms at half the screen; one opaque material, no alpha |
| Bakes | 5 to 15 ms of GPU per changed house, only on change |

The base M4 Mac mini has 16 GB of shared memory. Until the scale test sets the textures' share, shells get a proposed 1 GB resident.

## 4. What it replaces, and what it saves

| In the plan now | With the shell |
| --- | --- |
| Four tiers per kind (`foundations.md`): street 20 to 80 m, city 80 to 400 m, far | close and near to 20 m, a short street level to 50 m, then one shell for every kind |
| Each kind's city and district levels and far shader path, each judged at its switch | one baker, one shader, one hand-over |
| The district level merged per block (`performance-at-scale.md`, rec 13, a week) | the shell's block level |
| Trees' octahedral impostors (rec 12, in part) | opaque lobes past 200 m |
| The Kuwahara bake experiment (`materials-at-scale.md`, item 10) | the look test's painting step |

Conventionally about ten far-field kinds (houses in four kits, warehouses, landmarks, stairs, walls and quays, paving, natural stone, the land, trees) each need a city and a district level. At about a day and a half each to build and judge, plus the district merge and the impostors, that is 35 to 40 days. The shell is 18 to 20 days once (baker and shader 6 to 8, painter 3, rebakes and jumps 3, ids 1, lobes 2 to 3, horizon 1 to 2; our estimates). Then every new kind, era and district gets its far field for nothing, which counts most in a town whose variety comes from districts and eras. Far pixels run one opaque material in about a hundred draws. The price is memory, disk and bake time; the conventional far tiers reuse the near maps' mips almost for free.

## 5. Where it fails, and the fallback

| Failure | Seen in | Fallback |
| --- | --- | --- |
| Painted normals under a moving sun look faceted, not painted | the time-lapse; the low sun | paint the albedo only; or keep the shell unpainted |
| The hand-over shows: another medium | the glide and the pull-out | move it out to 80 to 120 m and give heavy kinds a city level |
| The city camera loses history or era | readers at the far stop | denser texels where the city camera lives; or houses' own city level |
| Mips breathe | the swim index | nested mips; at worst box mips under painted top mips |
| Jumps bake too slowly | the jump's timing | precompute dated phases; lower mips first; hold the cut |
| Memory over budget | the harness | 5 cm texels, BC1 albedo, fewer channels |
| Lobes read as lollipops | strict review | the trees' planned impostors |

The worst case is the plan as it stands. An unpainted shell from 200 m is the conventional district level, built from the same rectangles, channels, ids and cells, so nothing made for the test is lost.

## 6. The look test

**Question.** Does a painted shell, baked from the near models and lit live, hold the corner's far views at least as well as conventional distance versions, in stills and in motion, with history and era still read right? It moves criteria 1 and 5.

**Content.** The heart in clay with the corner's houses from the test-quality generator at 1989 and 2020 (plan step 1f), under the shared weathering bake. Every arm draws the same content, so the comparison is fair in clay; a second round on the first approved houses judges the look itself.

**Views,** each as a strip of three headings:
1. *The street stop looking out:* 2.8 m up on the old town's lower lane by the Landing, over the roofs and across the Basin (the corner's camera 2 sightline, `town-plan.md`); and `9-harbour-row-quay`, along the quay.
2. *12 m:* the corner's `2-into-light` (`LT1Corner.cs`), against the low sun, where baked light shows first, and the heart's `1-over-the-roofs` (`LT1Heart.cs`).
3. *The city camera:* the corner's `3-middle` at 35 m and `4-far` at 120 m, where nearly everything is shell.

**Arms:**
- *R:* everything at its near level, no budget; the truth for value, picking and the readers' false-claims baseline.
- *A, conventional:* each kind's street, city and district levels by decimation and merging, with its history maps and own shader: what the plan would build.
- *B:* the shell unpainted, box mips, to isolate the painting.
- *C:* the painted shell at 3 cm a texel; *C5* at 5 cm.

**Light.** Grey drizzle, the 16:00 low sun after showers and the blue hour, one light record for all arms; and a time-lapse from 15:00 to 21:00 at view 2, as windows light with their rooms.

**Motion sheets** at 2560×1440, MSAA 4×, never supersampled:
- the pull-out from eye level to the far stop in ten seconds, through every hand-over and mip;
- a glide along Harbour Row's quay at walking pace;
- an orbit at 12 m, for parallax;
- the jump, 1989 to 2020, toggled in place at views 2 and 3.

**Measured.** On the M4: frame time, triangles, draws and resident memory on the harness's paths, and bake times. In the frames: value at the hand-over (one-eighth greyscale), the swim index, the jump's difference outside changed things, and picking against a raycast on R. By cold readers: all three views on A and C, with the shuffled-facts and layers-off controls (`foundations.md`).

**Judged** by the numbers, a strict review (Fable), then the readers. Øystein sees A beside C in every view and light, with the clips, the numbers in the margin.

**What would make us drop it:**
1. Øystein or the strict review prefers A in two of the three views, or the hand-over shows at every distance up to 120 m.
2. Readers find fewer budgeted histories from C than from A, or C makes more false claims than A or the layers-off baseline.
3. In any light or the time-lapse, the shell's value at the hand-over differs by more than one of the five value bands, or reads as lit by another light.
4. C swims more than A in the pull-out.
5. C is not faster than A on the close-stop and far-stop paths, needs more than 1 GB resident, or a thirty-year jump in view takes over a second to bake.
6. More than trees and moving things need a far path of their own (glass, signs or roofs); then it is not one system.

If B beats C, we keep the shell and drop the painting. If the hand-over holds only at 120 m, the shell starts there.

**Cost and timing** (our estimate): five to seven days for a shell baker in Python and Blender, the painter in numpy, the shell shader in URP, arm A by decimation, and the sheets. It runs in the foundations (step 1b), once the harness, the motion sheets and the 1f houses exist.

## What we should do

1. **Fix the shape now.** If the far town is painted, it is world-space shells painted in texture space and lit live, never a picture. The architecture reserves cells, per-thing atlas rectangles, per-triangle thing and part ids and the shell's channels in the chunk format (Monday, hours); the district level needs them anyway.
2. **Give every shader an unlit bake mode** that writes albedo at the date, normal, history channels and ids. The light study's debug views already ask for "albedo alone", and both arms need it (a day).
3. **Run the look test** (five to seven days) and show Øystein A beside C.
4. **If it is kept,** port the baker to the player (C#, compute, GPU compression), with per-thing rebakes and the jump's double buffer (eight to twelve days); then the lobes and the horizon.
5. **If it is dropped,** the same data, unpainted, becomes the district level, and each kind gets its city level, as planned.

## Gaps

- No primary source opened for Firewatch's distant mountains (403), Breath of the Wild's or Ghost of Tsushima's far fields (members-only), Spider-Man 2's distant levels (abstract only) or Brucks' write-up (no text). Serious Sam 4's GDC 2019 deck, which by its search excerpt splats the far forest into the terrain's far texture, was over 10 MB.
- No source tests painted albedo and normals under a moving sun; the joint Kuwahara is our proposal.
- Not measured: Kuwahara at 4096² on the M4; GPU compression inside Unity on Metal; mipmap streaming with hundreds of cell atlases; a stretched last cascade's cost.
- Bare winter crowns as lobes are undesigned; two lobe sets, leafed and bare, is the first idea.
- Whether dropping the bent normal hurts drizzle's top-light on far cornices.

## Sources

Film and research: [Vittani, camera mapping in Nuke](https://www.therookies.co/blog/matte-painting-tips-for-camera-mapping-3d-projection-and-element-integration-with-nuke/) · [Matte painting (shootfirst.art)](https://www.shootfirst.art/matte-painting) · [Shade et al., layered depth images](https://grail.cs.washington.edu/projects/ldi/ldi.pdf) · [Shade et al., hierarchical image caching](https://grail.cs.washington.edu/projects/hic) · [Deep Canvas patent](https://patents.google.com/patent/US6268865) · [Tears of Steel, The Dome](https://mango.blender.org/artwork/the-dome/) · [Nuke Relight](https://learn.foundry.com/nuke/content/comp_environment/3d_compositing/relighting_2d_images.html) · [Meier 1996](https://history.siggraph.org/?p=117028) · [Praun et al., real-time hatching](https://hhoppe.com/hatching.pdf)

Games: [GTA V graphics study](https://www.adriancourreges.com/blog/2015/11/02/gta-v-graphics-study/) · [Spider-Man 2 distant-city LODs (GDC 2024)](https://schedule.gdconf.com/session/applied-mesh-analysis-automating-distant-city-lods-in-marvels-spider-man-2/899260) · [Ghost of Yōtei tech deep dive](https://blog.playstation.com/?p=411201) · [Breath of the Wild at CEDEC 2017 (The Famicast)](https://www.thefamicast.com/2017/12/part-5-art-and-implementation-of-3d.html) · [Olly Moss on Firewatch (Campo Santo)](https://blog.camposanto.com/post/96702184522/hey-everybody-thanks-for-all-your-kind-words)

Impostors and HLOD: [Impostor Baker for UE4 (80.lv)](https://80.lv/articles/impostor-baker-for-ue4/) · [Unigine impostor material](https://developer.unigine.com/en/docs/latest/editor2/tools/impostors_creator/impostor_material) · [Amplify Impostors](https://amplify.pt/_AI) · [World Partition HLOD (Epic)](https://dev.epicgames.com/documentation/en-us/unreal-engine/world-partition---hierarchical-level-of-detail-in-unreal-engine) · [LOD cross-fade (Unity)](https://docs.unity3d.com/Manual/lod/lod-transitions-lod-group.html)

Painterly bakes and compression: [Substance Designer 14](https://experienceleague.adobe.com/en/docs/substance-3d-designer/using/release-notes/version-14-0) · [Quantize Color and Kuwahara nodes (Adobe)](https://www.adobe.com/learn/substance-3d-designer/web/quantize-color-kuwahara-nodes) · [Kam, automatic stylisation (80.lv)](https://80.lv/articles/automatic-stylization-for-realistic-assets) · [Spider-Verse (Foundry)](https://foundry.com/insights/film-tv/across-the-spider-verse-nuke-mari-katana) · [Betsy (Godot)](https://godotengine.org/article/betsy-gpu-texture-compressor/)
