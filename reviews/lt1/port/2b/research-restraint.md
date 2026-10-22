# Stone: restraint and clean making

Research for the stone redraw (Q15), 22 October, Opus 5.5, online only; it adds to `docs/research/stone.md`. (secondary) marks summaries, forums or memory; (unverified) marks unconfirmed claims and our arithmetic. Pixel figures use the walker's lens, 46° vertical at 1440 px: 1 cm is about 17/d px at d metres, so 17 px at 1 m, 3.4 at 5 m, 1.4 at 12 m (unverified).

## In short

1. **Calm by default, detail where the story is.** One value per stone face, at most one accent where a fact puts it (worn hollow, lit arris, damp foot). The walking surface is the calmest part. Riot clamped value ranges; Arkane wanted parts "noisy" against parts "very calm".
2. **The one-pixel lines are specular aliasing on chamfers too thin to draw.** A chamfer must be at least 2 px wide at its tier's nearest view (about 8 mm to hold at 5 m, unverified); beyond that the shading carries it. None of our shaders has specular anti-aliasing. Unity's core library already has `GeometricNormalFiltering`; Stone.shader should call it.
3. **Close every joint.** Mortar or soil, no deeper than the joint is wide, its value above the cast-shadow floor. No open gap under 2 px at the nearest view; SSAO kept off direct light.
4. **Make stones as masons do.** Flat beds, straight square arrises, small chamfers only on exposed arrises; irregularity as a few planar chips, never per-vertex noise on edges. Wall heads of the biggest, most regular stones, ties and runners alternating; every joint bridged.
5. **Specks and orange rims: three suspects in turn.** Tiny glossy facets, unclamped bloom, and shadow normal bias leaking low sun past the course above.
6. **Band-limit every mark by its footprint** and fade it to its mean before it falls under 2 px, smallest first; the big shapes never fade.
7. **Automate seven checks:** one-eighth busyness against the clay, value histogram, joint darkness, thin-line and speck counts, shimmer under sub-pixel jitter, feature size per view, and mesh contact and hygiene.

## 1. Restraint in art direction

- **The Witness:** an art goal is to "minimize the amount of noise we put into the player's mind" (Antonio, GDC 2014 slides, via search excerpts).
- **Riot, Summoner's Rift (2014):** "controlling color and level of detail, clamping value ranges", because the environment "can compete visually with other game elements".
- **Dishonored 2:** Gombart (Arkane) says Mitton's main goal was to remove photo-texture noise. "Sebastien hates stones with big uniform joints"; they varied tile orientation in the normal map instead. Some parts should be noisy against others "very calm". Substance edge-wear masks were noisy, so he painted parts out.
- **Firewatch:** texture detail marks what "adds to your story"; flat shapes, strong silhouettes (Ng, GDC 2015, via Thumbsticks).
- **Sea of Thieves, Fortnite** (secondary): simplify structures, redraw photos by hand, wear "realistically wonky"; filtered photos were "too noisy"; nothing smaller than a mailbox.
- **Diablo III, Breath of the Wild, Ghost of Tsushima** (secondary): background dimmed so the action reads; playability first; style from masses of one kind.
- **Masonry agrees with the look:** a running joint is a building fault, "two cover one and one covers two" (secondary). A well-built wall never makes a grid.

Our reading (unverified): two to three values per stone, marks one value step from the stone except at the focal point. A deliberate mark covers at least a quarter of the face's short side, at most two per face, half of each face calm. Joints are broken accents, found only where a lit plane turns. Busyness on the steps no higher than the clay around them.

## 2. Clean making: causes and fixes

| Fault | Likely cause | Fix |
| --- | --- | --- |
| One-pixel lines on nosings; orange rims on courses in low sun | Specular aliasing: highlights far smaller than a pixel, and MSAA "only handles edge aliasing" (Hill 2011); narrow chamfers with fast-turning normals are the classic case (Kaplanyan et al. 2016). Rims may also be shadow light-leak: our normal bias is 0.5 (`PC_RPAsset`), and Unity warns normal bias lets light bleed in. | Chamfers at least 2 px at the tier's nearest view, face-weighted normals (secondary). At 45°: about 3.4 mm at 2 m, 8 mm at 5 m, 2 cm at 12 m (unverified). Call `GeometricNormalFiltering(smoothness, geomNormalWS, variance, threshold)` from Unity's core `CommonMaterial.hlsl`: `ddx`/`ddy` normal variance added to roughness, variance at most 0.25 (Filament defaults 0.15 and threshold 0.2). Grain normal map via `TextureNormalFiltering` (Toksvig). A/B a lower normal bias. |
| Black slots at tread joints | Deep narrow open joints crushed by shadow, full-size SSAO and a black interior into 1–3 px lines. | Fill them. Conservation guidance repoints once mortar has weathered back as deep as the joint is wide, new work flush or slightly recessed: depth at most width. A lighter fill value. SSAO "Direct Lighting Strength" low; GTAO's multi-bounce lifts AO on light albedos (Jimenez et al. 2016); bent normals next (Klehm et al. 2011). |
| Single bright specks | Sub-pixel glossy facets from vertex noise, enlarged by bloom. | Specular AA; URP Bloom "Clamp" and "High Quality Filtering"; in our own bloom, the Karis average (weights 1/(1+luma) on the first downsample, confirmed by Jimenez for Call of Duty). |
| Wavy nosing edges | Noise moving arris vertices. | Pitch-faced stone has "arrises all in the same plane". No noise on arrises; wear one smooth curve; chips planar cuts. Silhouette error under 0.5 px at the near view, about 0.3 mm at 1 m (unverified). |
| Pillows on undercut shadow | Big bevels all round; the joint becomes a cave. | Flat touching beds: a specification dresses rock-faced beds "full and square" at least 50 mm behind the face. The face may bulge; arrises stay on the wall plane. Planar, not blobby, sculpting (secondary). |
| Loose fan at a wall end | No bonding at the head. | Heads bear on two sides only, so "the biggest, most regular stones", ties and runners alternating. |
| Floating or intersecting stones | No contact rule. | Rest each stone on the one below; Whiting et al. (2009) solve compression-only forces at every block interface. |
| T-junctions; z-fighting | Unshared vertices on shared edges; coplanar faces. | Weld at the source (secondary); no coplanar overlap. |
| Mottled treads | High-contrast mid-frequency masks. Polish is per vertex (UV4.x), so it may blotch at vertex spacing (unverified); lichen on walked treads breaks the trampling fact. | Polish as one low-frequency hollow per tread along the walking line, one value step; lichen only on untrodden edges. |

## 3. Marks across distance

- **Band-limit by footprint.** Quílez multiplies a cosine by `smoothstep(2π, 0, fwidth(x))` (via LYGIA's `fcos`, secondary); each octave of a sum fades the same way. Norton, Rockwood and Skolmoski (1982) set out the principle: interpolate in object space between a signal and its local average. Normal maps fade by Toksvig or LEAN, never by flattening, which looks glossier (Hill).
- **Fade order, smallest first** (unverified): grain (about 1 cm) goes first. Chamfer highlights turn to roughness. Lichen and stains (3–10 cm) fall to the stone's mean. Joints: a 10 mm joint is 17 to 3.4 px at 1–5 m, but 1.4 px at 12 m, so it must turn soft, lighter and broken, or go. A 35 cm face is 120–600 px at eye level and about 50 px at 12 m: one value, no inner marks. Courses and silhouettes never fade.
- **"Few, large" in pixels** (unverified): a 35 cm tread at 3 m is about 200 px, 25 px at one-eighth size. A 3 cm splotch is 17 px, and 2 px at one-eighth: speckle. Only marks a quarter of a face or larger read as shapes there.

## 4. Checks we could automate

On harness frames at native 1440p with 4× MSAA (as played, not supersampled stills), with a stone mask and a mask of the clay around it. Thresholds are proposals (unverified).

1. **Busyness at one-eighth.** Area-downsample, convert to L*; per mask, edge density (Sobel above a threshold) and high-frequency share (energy of L minus its blur, over its variance). Pass: stone at most 1.25× clay. Basis: Rosenholtz et al. (2007) measure clutter by feature congestion, subband entropy and edge density; Machado et al. (2015) found edge density and compression error the best predictors of rated complexity (rs up to .77).
2. **Value histogram.** 5th–95th percentile L* of lit and of shaded stone must not overlap (the VD rule). Two or three modes per stone; three to five per frame.
3. **Joint darkness.** The generator writes a joint ID pass. Pass: 5th percentile of joint L* above the darkest cast shadow on open ground; in sun, at least half the L* of the face beside it.
4. **Thin lines and specks.** A white top-hat on L* keeps bright features under 3 px wide; elongated pieces (10 px or longer, ratio 4 or more) are one-pixel lines. A black top-hat finds slots; Frangi's Hessian filter (1998) is the published line detector. Specks: 2 px or smaller and brighter than the 5×5 median by k times the median absolute deviation.
5. **Shimmer.** Eight frames of a still camera on sub-pixel Halton offsets. Per-pixel spread of L*, and mean ꟻLIP between neighbouring frames, stone against clay. ꟻLIP judges differences seen when flipping between images (Andersson et al. 2020); using it for shimmer is our idea (unverified).
6. **Feature size per view.** Each chamfer strip and joint: px = width × f / distance × cos θ at each view's nearest distance. Flag under 2 px while still at full contrast (before `OS_Near` fades it).
7. **Mesh contact and hygiene** (Blender). BVH-tree overlap finds intersecting pairs. Rays from each bed to the stone below: a gap over 3 mm on 30% of the bed is loose; a centre of mass outside the contact polygon is unstable. Arris RMS deviation at wavelengths under a quarter of the stone below 0.5 px at the near view. T-junctions: a vertex on another edge, unshared. The 3D Print Toolbox already checks intersections, degenerate, distorted and thin faces, and sharp edges.

## Sources

- Antonio, The Art of The Witness, GDC 2014: artofluis.com/wp-content/uploads/2014/03/gdc2014_luisantonio_theartofthewitness.pdf
- Riot, Updating Summoner's Rift, 2014: surrenderat20.net/2014/06/update-to-summoners-rift-headed-to-pbe.html
- Gombart (Arkane), Dishonored 2 materials: 80.lv/articles/asset-material-production-in-dishonored-2/
- Ng, The Art of Firewatch: thumbsticks.com/gdc-2015-the-art-of-firewatch
- Sea of Thieves, Fortnite notes: blog.habrador.com/2018/08/stylized-graphics-fortnite-sea-of-thieves.html
- Diablo III: gamedeveloper.com/design/gdc-2012-diablo-iii-s-art-director-shows-off-design-process; Takizawa: zeldauniverse.net (14 March 2017); Connell: vfxvoice.com/creating-the-way-of-the-warrior-for-ghost-of-tsushima/
- Hill, Specular Showdown, 2011: blog.selfshadow.com/2011/07/22/specular-showdown/
- Kaplanyan et al., Filtering Distributions of Normals, HPG 2016: research.nvidia.com
- Tokuyoshi, Kaplanyan, I3D 2019 and JCGT 10(2) 2021: jcgt.org/published/0010/02/02/
- Toksvig, Mipmapping Normal Maps, 2005: developer.download.nvidia.cn/whitepapers/2006/Mipmapping_Normal_Maps.pdf
- Unity, CommonMaterial.hlsl: github.com/Unity-Technologies/Graphics; HDRP Geometric Specular AA; URP SSAO, Bloom and shadow troubleshooting: docs.unity3d.com
- Filament Materials: google.github.io/filament/Materials.md.html
- Jimenez et al., Accurate Indirect Occlusion, 2016: research.activision.com; Jimenez, CoD: AW post-processing: iryoku.com
- Klehm et al., Bent Normals and Cones, VMV 2011: diglib.eg.org
- Repointing: South Kesteven DC; NI Department for Communities technical note
- Connecticut DOT, Section 605: portal.ct.gov; pitch-faced: dictionary.com
- Wall heads: conservationhandbooks.com; Fine Homebuilding, Stone walls stay built
- Whiting, Ochsendorf, Durand, SIGGRAPH Asia 2009: people.csail.mit.edu/ewhiting
- Quílez, band-limiting: iquilezles.org; Norton et al., Clamping, SIGGRAPH 1982
- Rosenholtz et al., J. Vision 2007: dspace.mit.edu/handle/1721.1/37593; Machado et al., Acta Psychologica 2015
- Frangi et al., MICCAI 1998; Andersson et al., ꟻLIP, 2020: research.nvidia.com/publication/flip
- Blender manual, 3D Print Toolbox: docs.blender.org
