# Characters: the people as models

How to build the town's people as models: their bodies, faces, hair, skin and clothes, from 20 to 70, in 1989 and the years either side, from free bases only. It serves criterion 2 (`CLAUDE.md`): a person is recognisable across scenes and years. It builds on the first survey (`people.md`) and the deep dive (`people-deep-dive.md`) and does not repeat them. Its siblings cover motion (`animation-and-motion.md`) and behaviour on screen (`behaviour-on-screen.md`); gait and posture appear here only as identity anchors.

Claims from a summary rather than the maker or the paper are marked (secondary); claims we could not confirm, (unverified). Facts about our own tools were checked on this machine (MPFB 2.0.17 in Blender 5.2, Unity 6000.6). The web search budget ran out before every thread was closed; what is missing is listed under Gaps.

## What the camera asks of a person

From the deep dive's table: through the 35 mm lens, a head is 120 to 160 pixels tall in a scene at 3 m, 24 to 32 at 15 m on the steps, 14 to 19 at 25 m, and 6 to 8 from the city camera pulled out. For most of the game a person is a figure 50 to 250 pixels tall. So the person is built in this order: silhouette and colour masses first, then the light pattern on the head, then the face itself, which only scenes see.

## 1. How the best build people in a stylised-real look

### What each one does

| Work | How its people are made | What we take | What we leave |
| --- | --- | --- | --- |
| Dishonored 1 and 2 (Arkane) | Sebastien Mitton: the work is "about finding the balance between realism and style"; models are worked for "legibility, silhouettes and planes, like academic sculptors"; the painterly feel comes from "the way we sculpt things" as much as from texture; no "procedural and direct use of photography". Dishonored 2's people are "very polygonal", their skin "not clean and shiny", guards "don't look like GQ models"; working people are the reference | Our closest relative: plane-built forms judged in light, ordinary working faces, weathered skin | The claim that Dishonored enlarges heads and hands is often repeated but unsourced (unverified) |
| Sea of Thieves (Rare) | The Infinite Pirate Generator randomised "body shape, wonkiness and age", sex, ethnicity, features and accessories; a team of at most four. Sculpts use "angular sharp edges" and asymmetry; with "no grunge overlays or pore detail", forms must be clean because nothing hides an error. Hair is sculpted. Players are shown eight generated pirates and choose (secondary) | A generator that offers a set for a person to curate; an asymmetry ("wonkiness") axis; forms that must be right because nothing covers them | The mechanism (morphs or swapped parts) is undocumented (unverified) |
| Team Fortress 2 (Valve) | Silhouettes from proportions, footwear, hats and folds; "clothing folds were explicitly designed to echo silhouette shapes". Hand-painted albedo with visible strokes holds up under magnification better than photo texture "due to their more intentional design". Shading through a painted ramp: cool shade, grey, "a small reddish terminator region". Distance simplifies through mips and fog, with no outlines | Folds that echo the outline; a warm turn at the terminator as part of the light; abstraction from distance, not from a second look | Its saturation and cartoon push |
| Guilty Gear Xrd (Arc System Works) | "The slightest difference in the surface normal may end up as a huge blotch", so normals on every major feature were edited by hand; a vertex channel biases where a form falls into shade, being "completely resolution independent" | Design the light pattern on the face; a baked "tends to shade" value per vertex | A shadow colour chosen per character (our shade belongs to the light) |
| Arcane (Fortiche) | 3D characters with highlights and shadows painted into the textures; faces cel-shaded; effects in 2D (secondary) | The deliberate, blocky stroke | Baked light: it works when every shot is lit once, and our light comes from the clock and the weather |
| Disco Elysium (ZA/UM) | Painted portraits in dialogue, small 3D figures in the world. The character pipeline "changed at least three or four times"; some styles were dropped "only after having modeled, textured and rigged, and animated the characters" | Two levels of one person, sharing silhouette, palette and costume; choose the style on stills before rigging | Hand-painted portraits do not scale to thousands |
| Hades (Supergiant) | "59 portraits, 68 models": illustrated portraits, 3D figures from a high camera | The same two-level split | As above |
| Kentucky Route Zero | Flat, low-poly figures without facial expression; the player supplies it (secondary) | Light and staging can carry a barely modelled person at distance | Not enough for scenes |
| Sable (Shedworks) | Masks let the designer make "a multitude of interesting characters without having to animate faces"; fog did the most for readability; outlines fade with distance (GDC 2022, secondary report) | The honest equivalent of a mask is weather and work: a sou'wester, a hood, a knitted cap | Outlines |
| Spider-Verse (Sony Imageworks) | Rule-based face lines failed; artists drew lines per pose, and a model trained on about 600 drawn frames per character predicted a first pass (secondary) | Confirms no outlines for a generated cast: good lines are drawn per pose | Everything line-based |
| Somerville (Jumpship) | Negative space carved out of every pose; costume accents at the joints so motion reads; faces dealt with only when the camera came close | Gaps between arms and body; accents at cuffs, collars, knees; the face last | |
| Pentiment (Obsidian) | "Our final (rigged) character count in-game is 157". Four leads set "the standard for the rest"; others start from a short bio (age, build, family, personality); every expression drawn by hand; hats pass between characters | One person built to final quality sets the bar; a short bio is enough to start a figure; objects that move between people carry identity | Hand-drawn expressions |
| The Last of Us Part II (Naughty Dog) | Capture-driven realism, about 15,000 facial poses (secondary); Ellie aged 14 to 19 by redesign, her eyes made less wide to read as older | Ageing a known face is redesign by hand there; we must generate it | The whole pipeline |
| Red Dead Redemption 2 (Rockstar) | About 1,200 actors (secondary). Arthur's hair and beard grow through stages and only a barber cuts them; weight follows eating; mud, blood and wet stay on clothes (secondary) | State that grows on a body over weeks reads as lived time, and each is a fact we can date | |
| Death Stranding | Scanned actors (secondary) | Nothing | Scans are one real person, need consent and money, give photoreal skin and no parameter space |
| The Sims 4 (Maxis) | Direct pushing and pulling of the body through morph targets, bone deformations and deformation maps (GDC 2015). Per modders, each garment has a second UV set that samples the body's deformation maps, so one deformation field fits every garment to every body (secondary) | One deformation field for body and clothes | |
| Baldur's Gate 3 (Larian) | Heads from 36 scanned models, sculpted, about six or seven days a head; skin shader built from "Hemoglobin, Melanin, Vein Map, and Yellowing Map", with layers for bruises, dirt, makeup, scars and tattoos; LODs generated in Houdini; hair moved from sculpted clay to strands | Skin as physical pigments, the strongest single technique here, for deep tones, ageing and weather alike; a curated head set plus layered marks | Strands: right for its realism, wrong at our distances |
| Wildermyth (Worldwalker) | "As your hero ages, their hair color changes and wrinkles slowly start to appear"; heroes have "their own 'colors' that tint almost everything that they wear"; faces kept "quite simple and cartoony" | A personal palette across outfits, as a fact of taste | |
| Crusader Kings II and III (Paradox) | DNA from both parents; CK2 had four age levels where portraits "grow wrinklier, get bigger ears and their hair thinning and becoming white"; CK3 adds age and illness overlays (CK3 secondary) | Heredity and age as separate layers on one face | Overlays that read as verdicts |
| Return of the Obra Dinn (Lucas Pope) | "Prioritise legibility above all else." About 60 crew are told apart by a face sketch, the manifest, where they stand and their role's clothes (secondary) | Recognition as evidence work: role, place and clothes as cues | |
| Watch Dogs: Legion (Ubisoft Toronto) | Every citizen spawns from tags (occupation, income, fashion, personality). Liz England: "we start with one fact about a person"; without constraints, "procedural soup", with too many, "full-on stereotypes"; her test was 100 lawyers who each "read as a lawyer" and "all look different" | Facts first, look second; job and income as loose constraints, never templates; the 100-of-a-kind sheet | Ancestry decided "when the character is spawned" (secondary): ours comes down family lines |
| Kingdom Come: Deliverance 1 and 2 (Warhorse) | 16 clothing slots with layers (secondary); an Adaptive Clothing System that fits stacked layers without intersecting (GDC Europe 2015); KCD2's dirt, blood and damage on garments through atlases, ID maps, UV-space decals and hiding groups (GDC 2025) | The technical shape of a period wardrobe | |

Not reached for want of searches: Clair Obscur, Valorant, Life is Strange's painted textures, Cyberpunk 2077's crowds, Firewatch's own reasoning (Firewatch shows no other human face; secondary).

### The craft, across them

- **Proportions.** The painterly-realist work stays near true proportions and gets its style from planes and edges. Where it pushes, it pushes the silhouette (build, height, posture, clothes), not the head. Big heads and hands belong to the stylised-3D family.
- **Planes, not pores.** Forms are planed like a sculptor's study and judged in light. Sea of Thieves shows the cost: with no surface noise, a wrong form shows at once. That is the "judge form in grey light" rule our trees already follow.
- **Faces at 15 to 30 pixels.** Those who ship faces that read at distance design the light on the face, not the features: edited normals and a shade bias (Guilty Gear Xrd), clean planes (Sea of Thieves). Others decline to fight for the face at distance (Kentucky Route Zero, Sable, Somerville). Both are open to us: design the head's light pattern, and let the near tier carry the rest.
- **Hair.** Stylised work sculpts hair as masses; realism goes to cards or strands. At 15 to 60 m, cards alias and strands become noise. Sculpted planar masses fit our rule against round blobs and the rule that marks from one cause are one shape (our reading).
- **Skin.** A narrow warm band where light turns to shade, cool shade (TF2), and colour from pigments (Baldur's Gate 3).
- **Cloth.** Folds designed to echo the outline, few and large; layers fitted by a shared deformation field; wear and dirt as decals tied to the garment.
- **Textures.** Painted, with deliberate strokes; no photo noise; no baked light in a world lit by a clock.
- **Distance.** Simplify by mips, fog and broader highlights, from one asset per tier (TF2, Sable).
- **Variety.** Sample within loose constraints and curate the result (Sea of Thieves, Legion); presets plus attachments (Baldur's Gate 3); heredity under age (Crusader Kings); a personal palette (Wildermyth).

One problem is ours alone. Our brush is fixed to the world (`OS_Brush`, strokes about 70 cm long), so every wall shares one brush. On a walking person a world-fixed texture slides across the body: the "shower-door effect", named in the painterly-animation literature since Meier (1996, not re-read). People need the same brush size, carried in their own rest-pose coordinates (stored in a UV channel), so the strokes move with them. A 70 cm stroke is also larger than a head. People's strokes must be scaled to the body (a few centimetres on the face, a hand's width on a coat), so the "one brush size" rule needs a reading for people. That is a decision for the look test, not a rule written ahead.

## 2. The free bases, as they are

### MPFB and MakeHuman (installed and checked here)

MPFB 2.0.17 is installed in Blender 5.2, with the MakeHuman system assets. The assets are CC0 and may ship in a closed commercial game ("All core assets (the base mesh, targets, skins…) are shared under CC0"); the add-on's code is GPL, and we ship only its output.

| Part | What is there |
| --- | --- |
| Base mesh `hm08` | 19,158 vertices with helpers; the body alone 13,380 vertices and 13,378 quads (about 26,800 triangles). Helpers: tights, skirt and hair shells for fitting, eyes, teeth, tongue, lashes, and 120-odd joint groups from which the skeleton is placed |
| Targets | 1,258 shape targets: macros (sex, age, muscle, weight, height, proportions, cup size, firmness, and a three-way "race" blend: african, asian, caucasian) and local ones by region (head shapes, 42 nose targets, brows, chin, ears, hands, feet, torso) |
| Age | 0 = 1 year, 0.1875 = 10, 0.5 = 25, 1.0 = 90, linear between (checked in MakeHuman's `human.py`). So ageing from 25 to 70 is one straight blend towards a single 90-year-old target, plus `head-age-incr` |
| Proxies | Same body, fewer vertices, fitted by the same mechanism: `proxy741` (741 vertices), `female1605` and `male1591`, and full-detail muscular proxies of about 13,300 |
| Rigs | `game_engine` (53 bones, the Unreal mannequin's names, no face bones), `mixamo_unity` (64), `default` (163, with face bones), `cmu_mb` (31, for CMU motion capture), Rigify |
| Clothes and hair | 20 garments (generic suits, shoes, a fedora), 10 hair meshes (card-based, with alpha textures), 12 brows, skins as photo textures named by "race", age and sex |
| Fitting (MHCLO) | Each garment vertex is bound to three body vertices with weights and an offset, scaled by reference distances, so any garment follows any body. A delete group hides the body under the garment. `create_mhclo_from_clothes_matching` makes a new garment from any mesh (MakeClothes) |
| Faces | `FaceService` loads visemes and ARKit's 52 face units (the CC0 `faceunits01` pack) as shape keys and carries them to garments and hair through the same bindings |
| Batch | `RandomizationService` is seeded, with a fixed draw order "so changing one slot's settings never shifts another slot's result" |
| Export | `ExportService` bakes modifiers while keeping shape keys |

### Anny (Naver Labs)

Version 0.6, 6 August 2026. The code is Apache 2.0. Its MakeHuman-derived assets are CC0, and its face units are the same CC0 pack. Its `smplx` topology is for non-commercial use only and is downloaded with the `smpl` extra. We install without it and never touch that topology. The mesh has 13,718 vertices (with tongue and eyes), a 163-bone MakeHuman rig or its own 104-bone rig, and a coarse 1,229-vertex version. It carries 564 artist-made blendshapes. It also ships a MakeHuman topology option, so its shapes should transfer to our base. That is to be checked by vertex count and order before relying on it.

Its value to us is the population, not the adult ageing. The age axis anchors child at one third and young adult at two thirds. Body parameters are drawn from Beta distributions by age and sex, fitted to the WHO's growth standards and BMI. That makes it good for children and teens and for sampling. Above 25 it inherits MakeHuman's single "old" anchor, so adult ageing is still one blend. The authors warn that the phenotypes "encode by design stereotypes of MakeHuman artists" and should not be expected "to faithfully encode any identity-related characteristics". Export is to PLY through trimesh, then into Blender.

### Blender Studio's Human Base Meshes

Version 1.4.1 (January 2025), CC0, Blender 4.2 or later: 17 meshes, realistic and stylised, whole bodies and heads, hands, feet and jaws, in clean quads with multiresolution detail and UDIM UVs. They are not on MakeHuman's topology. So they cannot take our targets or clothes directly. They can serve as sculpt references, and as the source of a *stylisation delta*: wrap one onto `hm08` (Blender's Surface Deform or a projected Shrinkwrap), subtract the default body, and the difference is a target every generated person can take at a chosen strength (our reading; untested).

### Others

| Source | Licence | For us |
| --- | --- | --- |
| Quaternius | Its own licence: free in commercial games, no credit, but never redistributed as assets "regardless of how much the Assets have been modified" | Not a base: the wrong topology, and the clause is awkward for a generator |
| Mixamo | Royalty-free in games; raw files not redistributed (`people.md`) | Clips and an auto-rig, for the motion study |
| SMPL, SMPL-X, Anny's `smplx` | Non-commercial | Never |

### How far they go

The machinery is good: the topology, a large target space, fitting that carries any garment and any face shape onto any body, proxies on the same bindings, a seeded batch generator, and a rig that maps to Unity's Humanoid. The surface is not ours. Its photo skins named by race, card hair, generic suits and a 90-year-old as the only ageing anchor would give a 2008 avatar. So we keep the machinery and replace everything visible: stylisation targets, age keys, hair masses, garments by era, a pigment skin in our shade function, and painted textures. The race macro is pinned at its neutral default and never used as a control.

## 3. Recognisability and identity

### What the research adds

The deep dive set the base: familiarity decides; known faces survive low resolution; at distance the body and gait take over. Added here:
- **For strangers, hair and outline count as much as the inner face; for the known, the inner face leads.** For famous faces the inner features beat hair and outline; for unfamiliar ones the two did equally well (Ellis, Shepherd & Davies 1979). Sinha and Poggio's 1996 image gave Gore Clinton's inner features under Gore's hair, and viewers saw Gore (secondary).
- **A haircut breaks a face.** In Toseeb, Keeble and Bryant (2012), switching a face between with and without hair cut recognition sharply. Hair seems to be stored with the face as a whole, so a change breaks the whole. A haircut, a hat or a hood is a switch that costs recognition of people the player knows only slightly.
- **Familiarity is built from variety.** An average of many images of one person recognises better than any single one, and better with more images (Burton et al. 2005). Meeting someone in many lights, angles and clothes builds a sturdier memory than one view repeated.
- **Decades are hard.** Faces keep enough of their own shape for "moderate levels" of age-independent recognition, and a little familiarisation makes it much sturdier (Mileva et al. 2020). For faces learnt at 20 to 30 and tested 20 or 40 years older, accuracy was poor but above chance (Sexton et al. 2024). Recognition of names and yearbook faces of classmates stayed near 90% for 15 years (Bahrick et al. 1975), but those faces were seen at the age they were learnt.
- **Caricature speeds recognition.** Caricatures of familiar faces were named faster than true drawings, with no loss of accuracy, and were chosen as the best likeness (Rhodes, Brennan & Carey 1987). The norm must be the person's own family mean, never a town average (`people-deep-dive.md`, D).
- **Body, face and gait add separately.** Accuracy was best for face and body together, moving (O'Toole et al. 2011). Face, body and gait each add something of their own (Simhi & Yovel 2021). That paper also notes that body shape triggers trait judgements just as faces do, so "Evidence, not verdicts" covers builds.
- **Clothes are a strong cue, and a fragile one.** A change of clothes lowered recognition of strangers at every age from 4 to adult (Seitz 2003, abstract). Machine re-identification drops 30 to 50% across a clothes change (secondary).
- **Where eyes go in a crowd.** Cloned appearance is spotted far more easily than cloned motion; colour variation hides clones (McDonnell et al. 2008). In eye tracking, the head and upper torso take most first fixations. Varying colour on those parts alone gave as much sense of variety as varying everything, and head accessories, the top's texture and the face's texture all worked; changing facial geometry did less (McDonnell et al. 2009, secondary).
- **Gait is a vector.** Walks can be decomposed into a space where each walker is a point (Troje 2002, secondary); people know their own and their friends' movement from points of light (Loula et al. 2005, secondary). A gait offset in that space is an identity anchor (the motion study owns it).

### How others keep a cast distinct

- Role, place and costume (Obra Dinn).
- A personal palette (Wildermyth).
- One mark carried through every redesign: Kratos's red tattoo (God of War).
- An object passed between people (Pentiment's hats).
- Recasting: *The Crown* changed its whole cast every two seasons. Peter Morgan: "the longest you can believe an actor in an aging part is about 20 years". Audiences accepted three Queens (secondary). What carried continuity (hair, costume, manner) we could not source (unverified). The lesson still stands: viewers follow a person across a complete change of face when context, role and manner hold.

### Rules for us

1. **Cues by distance.**
   - From the city camera: place, company and routine; height, build and posture; the outer layer's colour; head and hair mass.
   - At the street stop: the same, plus the head's light pattern (brows, sockets, hair frame) and the shape of the hair.
   - In scenes: the inner face, hands and expression.
2. **Variety goes where eyes go.** Head, headwear, hair and the upper torso's colour and texture first, then silhouette; facial geometry only near (McDonnell).
3. **A switch costs.** A new haircut, a hat, a hood: true facts, shown, knowing they cost recognition. The game can help with familiarity (a name on approach, `docs/research/interface.md`), never by freezing a person's look.
4. **Signatures are owned.** A coat worn for sixteen years becomes a signature because the record says it was kept. Nothing is added for recognition alone.
5. **Strangers are not recognised across decades.** For people the player knows, the inner face, the anchors and the context carry it. The test (section 7.4) checks exactly this.

## 4. Ageing, 20 to 70

### The body

| Change | Size | Source |
| --- | --- | --- |
| Stature | Starts about 30. By 70, about −3 cm in men and −5 cm in women; by 80, −5 and −8 | Sorkin et al. 1999, via Li et al. 2025 (secondary) |
| Thoracic curve (T5–T12) | About 26° under 40, 30° at 40 to 60, 33° over 60, spread about ±4° | Zappalà et al. 2021, 34 studies |
| Muscle | About 3 to 8% lost a decade after 30, faster after 60; physical work slows it | KJIM review (secondary for the range) |
| Weight in Norway | HUNT1 (1984–86): mean BMI 25.3 (men), 25.1 (women). Obese: men 7.7%, women 13.3%. At 60–69: 49% of men and 42% of women overweight; 11% and 24% obese. By 2006–08, mean BMI 27.5 and 26.9 | Midthjell et al. 2013 |
| Walking speed | Flat to about 59, then down about 6 to 10% a decade | Bohannon & Andrews 2011 (secondary); for the motion study |

### The face

- **Bone.** The orbit widens, its lower outer rim receding first and the upper inner rim in old age; the central rims hold. The upper jaw retrudes (its angle about 10° smaller from under 30 to over 60). Bone is lost at the lower edge of the nasal opening. The jaw angle opens, and the ramus and body of the jaw shorten, while its width holds. On the surface this gives the tear trough, a deeper fold from nose to mouth, a concave area in front of the jowl and jowls, and a longer nose with a falling tip (Mendelson & Wong 2012; Shaw & Kahn 2007).
- **Fat.** The face's fat lies in separate compartments: "The face does not age as a confluent or composite mass" (Rohrich & Pessa 2007). As they deflate one by one, the aged face divides into soft planes. That suits a planar head.
- **Ears and nose grow.** Ears lengthen about 0.22 mm a year (Heathcote 1995). The nose lengthened 1.4 to 1.7 mm over 12 years in one Korean CT study.
- **Skin.** Glogau's photoageing stages run from no wrinkles (about 28 to 35), through wrinkles in motion (35 to 50) and at rest (50 to 65), to wrinkles everywhere with yellow-grey skin (60 to 75) (secondary). The stages follow sun more than years. In 186 pairs of identical twins, longer smoking and more sun made a twin look older. Extra weight looked older under 55 and younger after it (Guyuron et al. 2009).
- **Colour carries age, and smoothing removes it.** Blends of older faces looked younger than their members. Strengthening a blend's colour differences made it look older (Burt & Perrett 1995). Our painterly smoothing will de-age faces. So age must be carried by large shapes and value (pockets under the eyes, hollows, the jowl's shadow, a mottled and greyer skin value, the hair's value), not by fine wrinkles, which belong to the near tier.

### Hair, teeth, glasses

- **Greying.** In 4,192 people, 74% of 45 to 65-year-olds had some grey, but only 6 to 23% were half grey at 50, depending on ancestry and hair colour. Europeans grey earlier than Asians and Africans, and men a little earlier than women (Panhard et al. 2012, L'Oréal-funded; secondary). The "50-50-50 rule" overstates it.
- **Balding.** Among men of European descent, Norwood stage III or worse affects about 16% at 18 to 29 and 53% in their forties (Rhodes 1998). One Norwegian sample of men aged 20 to 50 was 31% type I, 26% type II and 20% type V or worse (secondary). East Asian men bald about a decade later.
- **Female thinning** rises after menopause and is mostly mild. It shows as less volume and a wider parting (secondary).
- **Teeth.** In Bergen's nursing homes in 1988, 71% had no teeth (unchanged since 1975). In Trøndelag in 1973, 4.8% of 35 to 44-year-olds had none. Full dentures among people born before about 1925 are a fair inference for 1989 (unverified). Only scenes see the mouth.
- **Glasses.** Presbyopia begins at about 40 to 45 and reaches about 80% of people over 55 (secondary). About two thirds of Norwegians use some correction today (industry surveys; secondary). Frames are era items. At 15 m a pair of big 1980s frames reads as a dark bar across the face, an anchor in its own right.

### Dress with age

Twigg's *Fashion and Age* (2013) describes "age ordering": older women pressed towards toned-down, covered dress, with continuity of style as present as change. A small 2024 study finds dress taste imprinted in early adulthood lasting into later life. No study we found measures how long garments are kept.

### How games and films age people

| Work | Method | Lesson |
| --- | --- | --- |
| Crusader Kings II | Four age levels on the inherited portrait: wrinklier, bigger ears, thinner and whiter hair | Heredity and age as separate layers |
| Wildermyth | Hair colour and wrinkles change step by step; heroes retire at about 45 (secondary) | Small steps in tint and line |
| The Sims 4 | Discrete life stages; base-game age-ups distort faces enough that a popular mod fixes them (secondary) | Steps that break the face lose the person |
| RDR2 | Hair and beard grow; weight follows eating; an eight-year jump in the epilogue (secondary) | Weeks and years both show |
| The Last of Us Part II | Ellie redesigned from 14 to 19 | Hand redesign does not scale |
| *Benjamin Button* (Digital Domain) | Rick Baker's maquettes of Pitt at 80, 70 and 60, approved, scanned, then driven by Pitt's captured expressions; skin kept from looking "ashen or too pink or too red" (secondary, fxguide) | Keyed ages, approved one at a time, with identity driven through them |
| *The Irishman* | De-aged faces on old bodies: viewers read an old man in how De Niro "looks and moves" (secondary) | Age lives in posture and movement too; the age transform must reach the motion study |
| Dick Smith's age makeups | Thinning hair, jowls, spots, dark circles, sag round the eyes; trade teaching says hollow the cheeks, temples and under-eyes, keep high points light, and that restraint beats detail (secondary) | Age in a few big shapes |

### Ageing that keeps identity

Rowland and Perrett (1995) build a prototype for a group: its mean shape, plus its mean colour after every face is warped to that shape. A transform is the difference between two prototypes, added to one person: x' = x + α(young→old). Because the two prototypes differ only in the trait used to group them, "the transform itself will contain no information relating to identity". α can be partial or pushed. They also warn: Galton's composite of "criminal types" looked like everyone else. So an axis may only ever be a physical difference such as age, never a trait of character. That is Rule 8 and "Evidence, not verdicts" in one line.

Kemelmacher-Shlizerman et al. (2014) aged faces by chaining flows between neighbouring age groups rather than jumping straight across, which gave "more reliable flow fields". Or-El et al. (2020) used fixed age anchors with a continuous space between them. MPFB's single 25-to-90 blend does neither.

## 5. Clothing in a west-coast harbour town, 1950 to 1989 and after

### The weather sets the base

Stavanger gets about 1,256 mm of rain a year on 165 days, with a January mean of 2.2 °C and a July mean of 16.0 °C (1991–2020 normals). Rain gear, wool and layers are the normal dress, not the exception; winters are wet more than snowy.

### Materials and makers, dated

| Year | What | Source |
| --- | --- | --- |
| 1877 | Helly Hansen's linseed-oiled oilskins (oljehyre) and sou'westers (sydvest) | Helly Hansen; SNL |
| To mid-1900s | Oilskin: cotton painted with linseed oil; keeps rain out, does not breathe. The traditional sou'wester is yellow | SNL regntøy; MiA |
| 1949 | Helly Hansen's Helox PVC coats, about 30,000 a month; later the heavier Plarex for work wear | (secondary) |
| 1950s | PVC- or PU-coated cotton rain wear; Grundéns' heavy PVC Herkules overall (1954), orange from the 1950s to the 1970s | SNL; Grundéns |
| 1953 | The Marius sweater, sold to Sandnes Uldvarefabrik beside Stavanger the same year; about 5 million patterns by about 2010 | SNL |
| 1954–75 | Sandnes's knitting club, up to 50,000 members | SNL |
| Early 1960s | Hats leave everyday use: until the 1950s "it was unthinkable" for adults to go out bareheaded; "the big change came in the 1960s" | SNL hatt |
| Late 1950s–60s | A dark blue anorak with jeans, "almost a uniform" for young activists | SNL anorakk |
| 1970s | Breathable waterproofs start the fashion for all-weather clothes worn every day; Lifa polypropylene base layer (1975); Gore-Tex in Europe through Norrøna (1977, the firm's own claim) | SNL; Helly Hansen; Norrøna |
| 1980 | After the Kielland disaster (123 dead), survival suits required for everyone on mobile units and fixed installations, in the companies' colours; Kielland-era suits were red | Havtil; Kielland industriminne |
| 1980s | The lusekofte revival: young people in their parents' old sweaters; Dale's version is the Olympic jacket at Calgary, 1988 | SNL lusekofte |

### Work, in 1989

- **Fishing.** Oilskins have been fishermen's standard gear for decades (SINTEF 2005). In 1989 that means PVC overalls and smocks in orange or yellow, a sou'wester, rubber boots, and a wool sweater under them (secondary for the details).
- **Fish plants and canneries.** Canning was Stavanger's main industry from about 1890 to about 1960. Bjelland's Sjøhusgata factory ran from 1905 to 1983. So in 1989 cannery dress is mostly older women's past (our inference). Early dress was long skirts and white aprons (secondary). A Melbu fish-fillet kit from the 1980s and 90s held a polyester-cotton jacket with the company logo, trousers, rubber gloves, a plastic apron and a hairnet.
- **Oil.** Phillips came to Stavanger in 1965 and Ekofisk was found in 1969. 3,681 people came from the US in 1971 alone (secondary). By 1987 Norwegians were 99% of Phillips's offshore workers, 96% of its land staff and 72% of its senior executives. So by 1989 the Americans in town are mostly managers' families. Offshore coverall colours and helmets are unverified.
- **Offices.** Norwegian informality was noted by foreigners. At Statoil in 1976–77, staff in jeans and pullovers met suited Japanese bankers.

### 1989 itself

- **The economy.** Credit was deregulated in 1984, and household spending rose more than 18% in three years (the *jappetid*). The oil price halved in 1985–86, a hard time in Stavanger. So many adults' good clothes in 1989 were bought in the boom and are now three to five years old.
- **Fashion.** Shoulder pads, pastels, big hair and jewellery. The TV series *Dallas* and *Dynasty* set trends. The Norwegian fashion magazine *Tique* started in 1983.
- **Young people, late 1980s.** A Norsk Folkemuseum record (CC BY-SA) describes an oversized sweater tucked into Levi's 501s, a narrow belt, striped tennis socks, and sailing shoes or boots with rolled cuffs. Skaters wore a vest made from old jeans, painted with logos and a 1989 *Ghostbusters II* button. Jeans were patched, torn and holed.
- **Subcultures.** Punk came with the Sex Pistols in 1977; Blitz, Oslo's punk house, opened in 1982 (leather jackets, ripped jeans, coloured hair, mohawks). *Raggere* drove older, often American cars. Black metal's look comes mostly after 1989 (unverified). Stavanger's own scenes are unsourced.
- **Glasses.** Big plastic frames early in the decade, small metal ones from about 1984 to 85, tortoiseshell late (secondary).
- **The old.** Most pensioners in 1989 were born between 1900 and 1925 and were adults when hats were still compulsory. Caps and hats by habit, wool coats ten to twenty years old, and cardigans are likely but unsourced (unverified). The headscarf (*skaut*) had a revival in the 1970s as a reaction against the stiff hairstyles of the 1960s.
- **Children.** A Helly Hansen child's rain jacket in yellow PVC-coated cotton was made about 1958–70 and worn about 1965–68 by a girl born in 1955. The handwritten name in it is crossed out: a hand-me-down.

### How clothes age and are mended

- Darning was core household work until the 1960s; after that repair became more decorative, though socks were still darned (SNL stopping). Home knits are coarser and easier to darn.
- In surveys, the largest reason clothes go out of use is quality (37%): wear, shrinkage, tears, fading, broken zips (secondary).
- Wear signs we expect, unsourced:
  - wool felts at elbows and underarms;
  - PVC cracks at folds and goes tacky;
  - oilskin darkens;
  - denim fades at thighs, knees and seams;
  - wool trouser seats shine;
  - cuffs fray;
  - knits bag at the elbows;
  - boots crease at the ankle.
- Each is a function of the garment's years and uses, as wear is on stone.

### Archives

Stavanger's city archive holds Arne Kaada's photographs (435,736 numbers, from 1953), Høiland's (233,754) and others: probably the best record of street life from the 1950s to the 1980s. DigitaltMuseum licences vary by owner: Norsk Folkemuseum mostly "contact owner", some museums CC BY-SA or CC BY-NC-SA. They are for private study only, with Øystein's OK before any download (`NOW.md`).

### The 1989 shelves

| Shelf | In 1989 |
| --- | --- |
| New (1988–89) | Oversized tucked sweaters; 501s with rolled cuffs; striped socks; tortoiseshell or small metal frames; bright breathable shells |
| Current (bought 1983–87) | Shoulder pads, pastels, puffer jackets, big plastic frames, Lifa and pile layers |
| Old-fashioned but worn | 1970s polyester and flares on adults who stopped buying; men's hats and caps on those born before about 1925; PVC-coated cotton rain wear |
| Heirloom | Marius sweaters and lusekofter from the 1950s to the 1970s, now on the young too |

## 6. Variety with fairness

### Real spreads

| Fact | Value | Source |
| --- | --- | --- |
| Stavanger, 1 January 1989 | 96,948 people (49,344 women) | SSB 06913 |
| Ages | 0–9: 13.1%; 10–19: 13.6%; 20–29: 17.2%; 30–39: 16.2%; 40–49: 12.4%; 50–59: 8.5%; 60–69: 8.9%; 70–79: 7.1%; 80+: 3.0% | SSB 07459 |
| Born abroad | 8,006 (8.3%, against 3.4% nationally): Europe 4,495, Asia 1,520, North America 1,347, Africa 366, Latin America 213, Oceania 65 | SSB 07110 |
| Pregnant | 1,587 births in 1989, so about 3% of women aged 20 to 39 visibly pregnant at any moment | our arithmetic |
| Men's height at about 19 | Born 1911: 172.8 cm; 1932: 176.0; 1951: 178.7; 1970: 179.8 (SD about 6.5) | SSB conscripts, table 4.22 |
| Height at 30–49, Tromsø | Women: born in the 1930s 162.5 cm, the 1970s 165.9. Men: 175.9 and 179.3. The gap by education: 5.1 and 4.3 cm in the 1930s cohorts, 3.0 and 2.0 cm in the 1970s | Arntsen et al. 2023 |
| Adults, HUNT1 (1984–86) | Men 176.3 cm (SD 6.7); women 163.0 (SD 6.3); BMI SD 3.2 for men, 4.5 for women | Midthjell et al. 2013 |
| Left-handed | About 10.6% (more men); fewer among those schooled when the left hand was discouraged (unverified for Norway) | Papadatou-Pastou et al. (secondary) |
| Eye colour, northern Norway | 56% blue, 23.5% intermediate, about 20% brown | PMC8227851 |
| Hearing aids | 4.2% of adults in 1997 (HUNT) | (secondary) |

Three of these matter at once:
- **Cohort is a silhouette cue.** A 70-year-old man and his 19-year-old grandson differ by about 6 cm in grown height before any shrinking.
- **Women's weight varies about 40% more than men's.** A generator with one spread is wrong.
- **In 1989 the young were slim and heavy bodies mostly middle-aged and older.** Since then the young have gained the most, so a 2020 town needs a different spread.

### Where generation goes wrong, and the fixes

- **Ancestry rolled at spawn.** Legion's "ethnicity decided when the character is spawned" (secondary) makes ancestry decoration. Ours comes down family lines from founders and dated arrivals, which are facts.
- **Templates.** Generation by template gives stereotype; with no constraints at all it gives soup (England). Constraints are loose and facts lead.
- **Dark skin breaks first.** The Sims 4's darker tones banded and discoloured until a 2020 fix tied to texture compression (secondary). Film stock was calibrated on cards of white skin (Shirley cards, secondary). Ava Berkofsky lights dark skin on *Insecure* for its reflected sheen and does not push skin to the usual brightness target (secondary). Baldur's Gate 3 builds skin from melanin and haemoglobin, which gives better control of deep tones than a multiplied tint. For us:
  - skin as pigments;
  - near-tier skin textures at high precision;
  - HDR buffers and dithered grading;
  - sheen kept on darker skin;
  - albedo never greyed to "lift" a face, and blacks never lifted in the grade.
- **One-wavelength light.** Low-pressure sodium is nearly one wavelength, so under it every skin is one hue and differs only in value (physics, our reading). The quays' 1970s sodium lamps (`docs/visual-direction.md`) make that a real test.
- **Textured hair is the most often missing.** In a Dove survey, 85% of Black players said games represent textured hair poorly (brand survey, secondary). The Open Source Afro Hair Library's licence is for individuals only, so it is reference at most. Hair masses from straight to coily get equal care in our kit.
- **Looks read as character, wrongly.**
  - Childlike faces read as warm, weak and naive (Zebrowitz, secondary).
  - Scars and facial difference are over-used for villains: the BFI pledged in 2018 not to fund such portrayals after Changing Faces' campaign (secondary).
  - Fat bodies appear mostly as monsters and jokes (Harper, GDC 2015; Waszkiewicz, secondary).
  - Women's bodies drift thinner as realism rises (Martins et al. 2009, secondary).
  - The old, children and women are under-counted in games (Williams et al. 2009, secondary).
- **MPFB's sexualising macros.** `idealproportions`, `cupsize` and `firmness` are the kind of control Rule 8 rules out as a push.

### Inheritance

- **Face geometry.** Feature groups pass whole from one parent (Paralives' approach, secondary; the deep dive). Kinship is read most from the upper face.
- **Pigment.** Pigment is polygenic and continuous, with no category boundaries; variation within Africa alone is wide (Crawford et al. 2017, secondary). So skin melanin and haemoglobin, hair pigment and hair texture are each the parents' mean plus seeded noise.
- **Eye colour** has one major locus, so it may come out in two clusters (secondary).
- **Height** comes from one parent's category, then the childhood-wealth delta at its true size, which shrinks by cohort (Tromsø).

## 7. For us

### 7.1 The pipeline, end to end

1. **The record.** A person's facts and their garments' records (7.5) come from the engine, or a fixture labelled `authored`.
2. **Identity, at birth.** Feature groups from parents (founders take a head from a curated set), pigments as midparent plus noise, grown height from cohort, parents and childhood wealth, build archetype weights, an asymmetry seed, a gait seed. All are stored as numbers, never as a mesh.
3. **The target library (Blender, made once, approved one part at a time).**
   - *Identity:* MPFB's proportion targets, audited and trimmed to those that vary real people (face length, jaw, brow height, eye spacing, nose classes, ears), plus our own.
   - *Archetypes:* 8 to 12 builds (`people.md`).
   - *Stylisation:* one delta, from our own sculpt or a Blender Studio mesh wrapped onto `hm08`, applied at the push dial's strength.
   - *Age keys:* at 35, 50, 65 and 80, each a shape delta and a colour and value delta, after the anatomy in section 4.
   - *Weight and muscle* through MPFB's macros. The race macro stays pinned.
4. **The face's light.** On the shared topology, normals on the head tuned so brows, sockets, the nose's planes, the mouth and the jaw make a few clean shapes. A baked shade-bias value per vertex. A painted value map shared by every head (the same UVs), so brows and sockets read as one dark step at 15 to 25 m. The age keys carry their own deltas for it.
5. **Hair as masses.**
   - *Library:* sculpted planar masses, about four textures (straight, wavy, curly, coily) by length and by era's cut, each bound to the head by MHCLO.
   - *Form:* a lit top plane and a shaded underside, like the trees' lobes. Cards only at the silhouette in the near tier.
   - *Colour:* from two pigments plus a grey fraction, applied by region (temples first).
   - *Change:* balding as Norwood stage masks. Length grows from the date of the last cut. Facial hair the same way.
6. **Garments by era.**
   - *Making:* each garment modelled once on the base, bound by MHCLO, with a delete group under it, and every body target's delta carried over by fitting the garment at each extreme. That is the Sims' shared deformation field, done offline.
   - *Fit:* a few fit variants (loose, tight) and wear shapes (knees and elbows bagged) as targets.
   - *Slots:* base, knit, outer, legs, feet, head, hands, carry, work kit. Outer layers hide inner ones by masks, as KCD does.
   - *Paint:* by our painting module, in the garment's rest pose.
7. **Surfaces.** One person shader through the town's shade function (`OS_ShadeP`), so shade stays the light's (rule 1).
   - *Skin:* melanin, haemoglobin and yellowing, with weather and flush from outdoor years. Its terminator is the shade function's existing warm turn, strengthened by a material scatter value. The wrap is widened the same way. Never a shadow tint.
   - *Cloth:* fibre sheen for wool, gloss for PVC and oilskin, fade for denim.
   - *Hair:* value masses with a painted sheen band.
   - *Brush:* in rest-pose coordinates, so it does not swim.
   - *Wear:* garment masks in shared UV layouts, from each garment's record.
8. **The rig.** MPFB's `game_engine` (53 bones) to Unity's Humanoid; the joints are placed from the shaped body's joint groups, so a tall person gets a tall skeleton. Face units (ARKit's 52, CC0) only in the near tier, or painted expressions, as the motion study decides.
9. **Tiers.**

   | Tier | Distance | The person drawn as | Budget (provisional, to be measured) |
   | --- | --- | --- | --- |
   | Near | scenes and eye level, within about 20 m | the shaped `hm08` with covered skin deleted, fitted garments, hair masses with edge cards, face units | about 25,000 to 40,000 triangles |
   | Street | 20 to 80 m | a proxy body (`female1605`/`male1591`) with garments and hair merged into one shell, one atlas | about 3,000 to 5,000 |
   | City | 80 to 400 m | `proxy741`-class shell, baked animation, instanced | about 600 to 1,500 |
   | Far | beyond | a coloured mark in the right place | a few |

   Each tier takes the same targets through the same bindings, so it is the same person, never a different claim (`docs/foundations.md`). Unity's Mesh LOD will not do this for us: "a Skinned Mesh Renderer deforms LOD0 regardless of which LOD index Unity is currently using", and its simplifier ignores skin weights and blend shapes. So the tiers are separate meshes, and only the drawn one is skinned.
10. **Assembly.**
    - *For the look tests and LT2:* people built offline in Blender from their records and exported with baked shapes.
    - *For the town:* a small runtime assembler in Unity. It sums the shape weights on the shared base, the garments and the hair in a Burst job. It places the joints from the joint helpers, rebuilds the bind poses and makes the tiers' meshes. It caches by a hash of the record, the date's age step and the outfit, as the living fabric caches a thing's life.
    - *Why not bake every mesh:* a town of 97,000 people across decades cannot ship one baked mesh each; a few hundred kilobytes of weights can.
    - *Why not use UMA:* its licence is unverified, and ours is small and fits the record.

### 7.2 From facts to look

| Fact (owner) | What it sets |
| --- | --- |
| Born, sex (engine) | Grown height by cohort and sex; the era their taste formed in (about 16 to 25); which garments in the wardrobe are old |
| Parents, founders and arrivals (engine; setting pack) | Feature groups, pigments, hair texture, the tendencies to grey and to bald, the family's mean for the push |
| Childhood wealth (engine) | A height delta of up to about half an SD between extremes, smaller for later cohorts |
| Age at the date (derived) | The age keys; stature, curve of the back, muscle; hair grey and thinning; skin stage; reading glasses |
| Work history: load, outdoors (engine) | Muscle kept; hands and forearms; weathered skin and squint, tan lines; work kit at work; the work's stains on its garments |
| Weight trend, illness, injury, disability (engine) | Weight; weight lost in an illness with a date; a cast, a stick, a wheelchair, a hearing aid; scars only from dated injuries |
| Habits such as smoking, if the engine has them (engine) | Skin ageing rate; near-tier traces only |
| Money over time (engine) | Wardrobe tier; how old the clothes are; repair or replace; purchases dated at money events |
| Household (engine) | Hand-me-downs between siblings; knits made by a household member; children's sizes stepping up |
| Taste and subculture with years (engine request) | Style group, personal palette, signature items, hair cut by era |
| Season, weather, hour, activity, place (scene) | Which garments are worn now; wet hair and cloth; Sunday clothes; a dress code |

Clothes change at the speed of their records. Money trouble shows as garments kept longer, mended more and replaced cheaper over years, never as "shabby clothes overnight" (`behaviour-on-screen.md`, which owns the faster signs). The gait seed is the one its `person_behaviour` record carries: one seed, owned once.

What is never set: a face, body, skin or hair from a trait, a class or a verdict. Class and work show in clothes and their wear; character shows only through acts (`docs/living-fabric.md`, How inner states show). By the five kinds of thing on screen:
- *Canonical facts:* the garments owned, a cast on an arm.
- *Interpretations of facts:* a coat gone shabby from years and little money.
- *Seeded texture:* freckle placement, a fold's exact line.
- *Records:* a name tag, a company logo, a russ cap.
- *Local scene state:* today's outfit, wet hair.

### 7.3 Ageing across the years of play

A person at a date is identity + Δage(t) + body state + hair state + wardrobe:
- **Δage(t).** Interpolated between the neighbouring age keys, never one jump from 25 to 90. Each key is a shape delta and a colour and value delta, built once, approved like Benjamin Button's maquettes, and carrying no identity (Rowland & Perrett).
- **Personal rates.** From outdoor years, smoking and weight (Guyuron). They scale the skin and soft tissue, never the bone.
- **Schedules,** seeded within real spreads:

  | Change | Schedule |
  | --- | --- |
  | Stature | Flat to 30, then −3 cm (men) and −5 cm (women) by 70 |
  | Curve of the back | +4 to 7° from under 40 to over 60 |
  | Greying | Onset and rate from the family, by ancestry |
  | Balding | Pattern from the family; prevalence as above |
  | Glasses | Reading glasses at 40 to 45; distance glasses and their frames as owned items |
  | Teeth | Dentures for older cohorts, near tier only |

- **Body state from the engine.** Weight and muscle follow its trends, never a curve of our own.
- **Hair state.** The last haircut's date and the era's cut (RDR2's lesson at the scale of weeks).
- **Wardrobe.** Garments bought at dated money and life events, kept while their records say so, mended or replaced by money and household.
- **Taste.** Imprinted young, it drifts slowly, and the era's age ordering pulls older people towards plainer dress.
- **Continuity.** Every quantity is continuous in time except at a dated event (a haircut, a new coat, an illness), as with things. Two views a year apart differ a little; the event is the step.

### 7.4 Three stylisation tests, and a control

All three are on free bases. They are the same person at 20, 45 and 70 by our age keys, with five foils matched for build, colouring and era clothes. They are shown as posed, unrigged stills first (Disco Elysium's lesson), and only the winner is rigged and dressed in full.

| Test | What changes | Its bet |
| --- | --- | --- |
| A. Painted true | True proportions; the stylisation delta weak (about 0.3); the face's light designed; pigment skin; hair masses; painted garments | Stålenhag's people: our world's own proportions, identity from silhouette, colour and the head's light |
| B. Pushed planes | The same person on the houses' push dial at `stronger`: the stylisation delta full, build archetypes stretched, hands about +10%, harder planes at brow, cheek and jaw, chunkier hair masses, fewer and larger folds | Dishonored and Sea of Thieves: more readable at 15 to 25 m, still a real place |
| C. Graphic figure, painted near | Fewer planes, three values a form, the face only as value shapes beyond 15 m; in scenes a painted face over the same head (Disco Elysium's two levels) | The cheapest at scale: does identity survive without a modelled face? |
| Control | MPFB's default under our light: photo skin, card hair | What our work adds |

**How they are judged:**
- *Form first:* in grey light, every pigment one grey (form alone).
- *Then in colour, in four lights:* drizzle, low sun, blue hour, and a sodium lamp at night on the gully steps.
- *Across skin:* across a ten-tone range of skin (the Monk scale; licence unverified).
- *Cameras:* at 3 m, 5, 15 and 25 m from the street stop, from 12 m and from the city camera's close stop.
- *Reading:* in greyscale and at one-eighth size; beside the steps' target; in Øystein's judgement.

**The recognition test:**
1. Cold readers meet the person in three varied encounters, with a name.
2. They then pick the person from line-ups at each distance and at age gaps of 0, 25 and 50 years, both ways. The foils are aged by the same transform, and a haircut switch is varied deliberately.
3. Scored as d′.
4. A second arm pushes identity 0, 25 and 50% from the family mean.
5. Readers from mixed backgrounds also rate what traits each face and build suggest.

**What would change our minds:**
- If known people fail at 15 m across 25 years in A while B passes, people take more push than the houses.
- If C holds at the street and city distances, the near tier is the only place the face is modelled.
- If any build or face reliably reads as a trait, it is fixed before anything else.

### 7.5 The data a person carries

In the engine contract's style (years, per mille, provenance on every record); the fields under `identity` are Overstory's until the engine has an appearance seed (`people.md`):

```json
{
  "id": "p-812", "provenance": "authored", "seed": 81202,
  "born": { "year": 1931, "month": 4 }, "sex": "female", "parents": ["p-301", "p-302"],
  "identity": {
    "groups": { "brow_eyes": "p-301", "nose": "p-302", "mouth_jaw": "p-302", "build": "p-301" },
    "push": 250, "asymmetry": 140,
    "pigment": { "melanin": 180, "haemoglobin": 540, "carotene": 300 },
    "hair": { "eumelanin": 420, "pheomelanin": 260, "texture": 150, "grey_from": 43, "grey_rate": 800, "pattern": 0 },
    "eyes": { "lightness": 820 }, "grown_height_mm": 1648,
    "build": { "pear": 450, "stocky": 300, "beanpole": 0 }, "handed": "right", "gait": 5531
  },
  "life": [
    { "from": 1946, "to": 1962, "kind": "work", "at": "cannery", "load": 500, "outdoors": 100 },
    { "from": 1962, "to": 1996, "kind": "work", "at": "shop", "load": 250, "outdoors": 50 },
    { "year": 1974, "kind": "glasses", "item": "g-812-031" },
    { "year": 1988, "kind": "haircut", "cut": "short-perm" }
  ],
  "weight": [[1955, 450], [1975, 560], [1989, 610]],
  "taste": [{ "from": 1949, "style": "plain-good", "palette": ["navy", "grey", "rust"] }],
  "wardrobe": ["g-812-001", "g-812-007", "g-812-031"]
}
```

A garment is a thing with the living fabric's record (`docs/living-fabric.md`):

```json
{ "id": "g-812-007", "kind": "wool-coat", "shelf": "1979", "made": { "year": 1979, "by": "bought-new" },
  "cost": 700, "owners": [{ "id": "p-812", "from": 1979 }],
  "uses": [{ "from": 1979, "kind": "town", "per_week": 5 }],
  "works": [{ "year": 1984, "kind": "relined" }, { "year": 1988, "kind": "buttons" }] }
```

Overstory derives the rest from these by written rules: shape weights at the date, hair and skin state, which garments are worn for the weather and the activity, and each garment's fade, felt, shine and mends. The engine requests this implies:
- an appearance seed and parents for every person (asked in `people.md`);
- taste with years;
- outdoor exposure and physical load per job;
- weight trend, illness and injury dates;
- habits such as smoking;
- notable purchases, clothes included, as things with owners (request 17).

## What we should do

Ranked; each with its cost and what it buys.

1. **The person and garment records as fixtures, with a validator** (a day). Every later step keys off them, and criterion 2 becomes testable on facts.
2. **One person in Blender from a record, scripted on MPFB** (three to five days). The race macro pinned. Our four age keys roughed in from the anatomy, as shape and value deltas. Three ages as grey stills from every judging view. *Buys:* the first honest look at a person in our world, and the end of the 25-to-90 blend.
3. **The head's light and a pigment skin in the shade function** (about a week). Tuned normals, a shade bias and a value map on the shared head; skin from melanin, haemoglobin and yellowing; the warm turn and wrap widened by a scatter value. *Buys:* faces that read at 15 to 25 m without detail, and every skin tone right in every light from the start.
4. **The three stylisation stills and the control, judged** (one to two weeks). *Buys:* the style decision before any rigging or wardrobe money is spent in time.
5. **Hair masses, version one** (one to two weeks). Eight masses across straight to coily, short to long, with greying, thinning and the last-cut rule. *Buys:* the biggest identity cue at the street stop.
6. **The 1989 kit, version one** (two to three weeks). Twelve to fifteen garments for LT2 and the steps scene: a fisherman's PVC smock and sou'wester, a Marius or lusekofte, 501s, an oversized sweater, a padded blazer, a wool coat, a puffer, a child's rain suit, rubber boots, a flat cap, glasses frames of three eras. Each bound, painted and worn by its record. *Buys:* people who belong to a year and a class.
7. **The recognition test with cold readers** (a few days, plus readers). *Buys:* criterion 2 measured, not asserted.
8. **The population sampler and its checks** (about a week). Spreads from SSB and HUNT; Anny for children; the silhouette sheet; the 100-of-a-kind sheet; a clone check per frame; the distribution and trait-blind audits. *Buys:* variety that is true, and proof that it is fair.
9. **The tiers and the runtime assembler** (three to five weeks, after the style is chosen; city figures with the motion study). *Buys:* a town full of people at frame rate.
10. **Archive study** (a few days, with Øystein's OK). Kaada's and Høiland's photographs for dress, hair and posture by decade. *Buys:* closes this study's thinnest parts (the old, the crews, hair) from the town's own record.

## Gaps

- **Dress:**
  - offshore coverall colours and helmets;
  - fishermen's and fish-plant workers' daily dress, 1960 to 1989;
  - what pensioners wore in 1989;
  - Norwegian hairstyles of the 1980s;
  - when russ overalls began;
  - dates for Devold and Janus;
  - Stavanger's own youth scenes.
- **Population:**
  - Stavanger's origins by country in 1989 (only world regions are online);
  - glasses, mobility aids and disability rates in 1989;
  - hair-colour frequencies (unreliable numbers circulate; do not use them);
  - Rogaland's own BMI (HUNT is Trøndelag).
- **Ageing:**
  - lip thinning and brow descent;
  - eye colour and brows with age;
  - Lanitis (2002) and the forensic artists' list of stable features;
  - *Boyhood*, *Vice*, *Darkest Hour*;
  - the full CK3 genes.
- **Craft:**
  - Dishonored's proportions;
  - Kentucky Route Zero's and Firewatch's own reasoning;
  - Clair Obscur, Valorant, Life is Strange, Cyberpunk 2077;
  - the McDonnell papers' full thresholds;
  - Jimenez et al. 2010's pigment model (not re-read);
  - the Monk scale's licence.
- **Tools:**
  - whether Anny's `makehuman` topology matches `hm08` vertex for vertex;
  - the stylisation delta by wrapping, untested;
  - what a runtime assembler costs per person on a mid-range card, unmeasured;
  - UMA's licence.
- **Siblings:** the motion study was not yet written when this one closed; gait, posture and expression are its and the behaviour study's to settle with this one.

## Sources

Craft: [Mitton, Dishonored](https://news.sci-fi-london.com/news/games/2012/09/dishonored-interview-sebastien-mitton) · [Mitton, Dishonored 2](https://www.inverse.com/article/23269-dishonored-2-sebastien-mitton-art-director-arkane-studios-interview) · [Sea of Thieves character art](https://www.zbrushcentral.com/t/sea-of-thieves-character-art/208371) · [IPG](https://seaofthieves.wiki.gg/wiki/IPG) · [TF2, SIGGRAPH 2007](https://www.advances.realtimerendering.com/s2007/Mitchell-IllustrativeRenderingInTF2(Siggraph07%20Course%20Notes).pdf) · [Guilty Gear Xrd, GDC 2015](https://www.ggxrd.com/Motomura_Junya_GuiltyGearXrd.pdf) · [Arcane pipeline](https://redsharknews.com/why-netflixs-arcane-looks-so-good-how-fortiche-ramped-up-the-animation-pipeline) · [Disco Elysium's art](https://www.mcvuk.com/business-news/we-knew-immediately-that-we-needed-to-make-a-game-with-a-striking-and-unique-look-to-accompany-the-writing-a-look-that-would-balance-the-mundane-with-the-unfamiliar-and-strange-the-art) · [Hades](https://mcvuk.com/?p=216051) · [Kentucky Route Zero](https://www.bostonglobe.com/2020/03/05/arts/kentucky-route-zero-is-gorgeous-anti-capitalist-parable-form-video-game) · [Sable, Kythreotis](https://www.yahoo.com/lifestyle/mix-procreate-unity-create-moebius-070058581.html) · [Sable, GDC 2022](https://www.gamedeveloper.com/marketing/how-shedworks-refined-the-art-of-sable-in-pursuit-of-readability) · [Spider-Verse lines](https://www.fxguide.com/?p=246246) · [Somerville](https://blog.jumpship.co.uk/post/176054619715/developing-character-jumpship/amp) · [Pentiment, Kennedy](https://www.gamedeveloper.com/art/deep-dive-the-art-of-pentiment) · [TLOU2 character technology](https://gdcvault.com/play/1027376/Character-Technology-of-The-Last) · [Ellie, Neonakis](https://www.syfy.com/syfy-wire/artists-alley-alexandria-neonakis-ellie-last-of-us?amp) · [RDR2 hair](https://twinfinite.net/guides/red-dead-redemption-2-hair-change-hairstyles-grow-cut-how/) · [Death Stranding](https://en.wikipedia.org/wiki/Death_Stranding) · [The Sims 4, GDC 2015](https://gdcvault.com/play/1022085/Innovations-in-The-Sims-4) · [Sims 4 morph UVs](https://sims4studio.com/thread/18974/mesh-working-properly-sliders-help) · [Baldur's Gate 3 characters](https://80.lv/articles/creating-characters-for-baldur-s-gate-3/) · [Wildermyth interview](https://turnbasedlovers.com/10-turns-interview/with-wildermyth-developer) · [Wildermyth layers](https://wildermyth.com/wiki/Image_layers) · [CK2 portraits](https://admin-forum.paradoxplaza.com/forum/developer-diary/crusader-kings-ii-dev-diary-7-character-portraits-and-modding.530197/page-6) · [CK3 portraits](https://www.thesixthaxis.com/2020/07/31/crusader-kings-3-developer-diary-contracts-portraits/) · [Obra Dinn's style](https://blog.playstation.com/archive/2019/10/17/lucas-pope-on-return-of-the-obra-dinns-art-style) · [Watch Dogs: Legion, England](https://www.gamedeveloper.com/design/how-watch-dogs-legion-s-play-as-anyone-simulation-works) · [Census, GDC 2021](https://gdcvault.com/play/1027018/Census-The-Systemic-Backbone-Behind) · [Legion's census, Hocking](https://gamingbolt.com/watch-dogs-legion-census-system-detailed-creates-nearly-infinite-possibilities) · [KCD adaptive clothing](https://gdcvault.com/play/1022771/Adaptive-Clothing-System-in-Kingdom) · [KCD2 clothing](https://gdcvault.com/play/1035519/Dressed-to-Quest-Achieving-Dynamic) · [KCD slots](https://nichegamer.com/2014/02/witness-the-insane-customization-of-kingdom-come-deliverance/) · Meier 1996, [Painterly rendering for animation](https://doi.org/10.1145/237170.237288)

Recognition: [Ellis, Shepherd & Davies 1979](https://moodle2.units.it/pluginfile.php/336418/mod_resource/content/0/Ellis79.pdf) · [Sinha & Poggio](https://improbable.com/2012/09/10/we-recognize-politicians-by-their-hair-they-say) · [Toseeb et al. 2012](https://pmc.ncbi.nlm.nih.gov/articles/PMC3312903/) · [Burton et al. 2005](https://research.bond.edu.au/en/publications/robust-representations-for-face-recognition-the-power-of-averages/) · [Bahrick et al. 1975](https://users.cs.northwestern.edu/~paritosh/papers/KIP/ConwayLongTermRetention.pdf) · [Mileva et al. 2020](https://eprints.whiterose.ac.uk/154879) · [Sexton et al. 2024](https://sure.sunderland.ac.uk/id/eprint/17615/) · [Rhodes, Brennan & Carey 1987](https://www.harvardlds.org/wp-content/uploads/2018/05/Rhodes-Identification-and-ratings-of-caricatures-implications-for-mental-representations-of-faces..pdf) · [O'Toole et al. 2011](https://nvlpubs.nist.gov/nistpubs/Legacy/IR/nistir7721.pdf) · [Simhi & Yovel 2021](https://people.socsci.tau.ac.il/mu/galityovel/files/2024/11/Independentcontributionsofthefacebodyandgaittotherepresentationofthewholeperson.pdf) · [Seitz 2003](https://zendy.io/title/10.1002/acp.912) · [Re-identification across clothes](https://arxiv.org/pdf/2003.04070) · [Clone Attack!](https://research.gold.ac.uk/id/eprint/15203) · [Eye-catching crowds](https://www.tara.tcd.ie/items/9ffa2d7e-2a7a-4da5-8082-071b60ca0471) · [Troje's walkers](https://www.biomotionlab.ca/walking/) · [Loula et al., review](https://www.frontiersin.org/articles/10.3389/fpsyg.2025.1645218/full) · [The Crown](https://www.hollywoodreporter.com/live-feed/crown-casts-prince-charles-queen-mother-season-3-1129939) · [Kratos](https://en.wikipedia.org/wiki/Kratos_(God_of_War))

Ageing: [Stature, via Li et al. 2025](https://www.frontiersin.org/journals/endocrinology/articles/10.3389/fendo.2025.1542962/full) · [Kyphosis, Zappalà et al. 2021](https://pmc.ncbi.nlm.nih.gov/articles/PMC8268398/) · [Muscle](https://doi.org/10.3904/kjim.2016.193) · [Walking speed](https://www.physicaltherapy.utoronto.ca/sites/default/files/assets/files/11walking-speed-age-and-sex-specific-normative-values-final.pdf) · [Mendelson & Wong 2012](https://pmc.ncbi.nlm.nih.gov/articles/PMC3404279/) · [Shaw & Kahn, review](https://thieme-connect.de/products/ejournals/html/10.1055/s-0030-1265024) · [Rohrich & Pessa 2007](https://utsouthwestern.elsevierpure.com/en/publications/the-fat-compartments-of-the-face-anatomy-and-clinical-implication) · [Ears](https://jhanley.biostat.mcgill.ca/CommunicationCommunicationCommunication/bigears.pdf) · [Nose](https://pmc.ncbi.nlm.nih.gov/articles/PMC10933809) · [Glogau](https://www.mims.com/philippines/disease/rhytides-wrinkles/disease-background) · [Guyuron et al. 2009](https://pubmed.ncbi.nlm.nih.gov/19337100/) · [Burt & Perrett 1995](https://research-portal.st-andrews.ac.uk/en/publications/perception-of-age-in-adult-caucasian-male-faces-computer-graphic-) · [Greying](https://www.cosmeticsdesign-europe.com/Article/2012/10/02/50-shades-of-grey-Not-quite-as-L-Oreal-study-finds-grey-hair-less-common-than-previously-thought) · [Balding review](https://pmc.ncbi.nlm.nih.gov/articles/PMC3412231/) · [Female thinning](https://pubmed.ncbi.nlm.nih.gov/35357365/) · [Teeth, Bergen nursing homes](https://medicaljournalssweden.se/actaodontologica/article/view/38404) · [Teeth, HUNT4](https://medicaljournalssweden.se/actaodontologica/article/view/36383) · [Presbyopia](https://healio.com/clinical-guidance/presbyopia/epidemiology-overview) · [Twigg, Fashion and Age](https://kar.kent.ac.uk/34532) · [Prime aesthetic](https://iastatedigitalpress.com/itaa/article/17365/galley/15637/view) · [Rowland & Perrett 1995](https://people.eecs.berkeley.edu/~efros/courses/AP06/Papers/rowland-cga-95.pdf) · [Kemelmacher-Shlizerman et al. 2014](https://grail.cs.washington.edu/aging/Aging_CVPR14.pdf) · [Or-El et al. 2020](https://grail.cs.washington.edu/projects/lifespan_age_transformation_synthesis) · [Benjamin Button](https://www.fxguide.com/fxfeatured/the_curious_case_of_aging_visual_effects/) · [The Irishman](https://www.rogerebert.com/?p=19011) · [Dick Smith](https://en.wikipedia.org/wiki/Dick_Smith_(make-up_artist)) · [Ageing makeup](https://www.cinemamakeup.com/blogs/essential-special-effects-techniques-for-aging-makeup/) · [Sims 4 age-ups](https://snootysims.com/wiki/sims-4/genetics-overhaul-mod/) · [MakeHuman's age mapping](https://github.com/makehumancommunity/makehuman/blob/master/makehuman/apps/human.py)

Clothing: [Stavanger climate](https://en.wikipedia.org/wiki/Stavanger) · [SNL regntøy](https://snl.no/regnt%C3%B8y) · [SNL sydvest](https://snl.no/sydvest) · [MiA, Helly Hansen oilskin](https://mia.no/oslofjordmuseet/helly-hansen-oilskin) · [Helly Hansen](https://en.wikipedia.org/wiki/Helly_Hansen) · [Helly Hansen history](https://www.fundinguniverse.com/company-histories/helly-hansen-asa-history/) · [Child's rain jacket](https://digitaltmuseum.org/011023239456) · [Grundéns](https://grundens.com/pages/timeline) · [SINTEF, fishermen's clothing](https://www.sintef.no/en/latest-news/life-saving-clothing-for-fishermen) · [Viking, Askim](https://lokalhistoriewiki.no/wiki/Askim_Gummivarefabrik) · [Norrøna](https://en.wikipedia.org/wiki/Norr%C3%B8na) · [SNL anorakk](https://snl.no/anorakk) · [SNL kjeledress](https://snl.no/kjeledress) · [Marius sweater](https://en.wikipedia.org/wiki/Mariusgenser) · [SNL Sandnes Garn](https://snl.no/Sandnes_Garn) · [SNL lusekofte](https://snl.no/lusekofte) · [Dale of Norway](https://en.wikipedia.org/wiki/Dale_of_Norway) · [Knitting in Norway](https://www.oslomet.no/forskning/forskningsnyheter/overraskende-hvor-sent-strikking-kom-til-norge) · [Bjelland's factory](https://kulturnav.org/81fa0491-eaca-43e2-b487-2a9ea085c512) · [Fish-plant kit](https://digitaltmuseum.no/011024238976/sett-med-arbeidsantrekk) · [Norwegianisation of oil](https://ekofisk.industriminne.no/en/norwegianisation/) · [Survival suits](https://www.havtil.no/en/explore-technical-subjects2/technical-competence/features/2015/suited-for-safety/) · [The red survival suit](https://kielland.industriminne.no/en/the-red-survival-suit/) · [Statoil's informality](https://equinor.industriminne.no/en/misunderstandings-with-a-smile/) · [Russ](https://en.wikipedia.org/wiki/Russefeiring) · [SNL russ](https://snl.no/russ) · [SNL hatt](https://snl.no/hatt) · [SNL skaut](https://snl.no/skaut) · [SNL mote](https://snl.no/mote) · [SNL stopping](https://snl.no/stopping) · [SNL pønk](https://snl.no/p%C3%B8nk) · [SNL subkultur](https://snl.no/subkultur) · [SNL briller](https://snl.no/briller) · [Late-1980s sweater](https://digitaltmuseum.no/021029702508/genser) · [Skater vest](https://digitaltmuseum.no/0210216470604) · [Worn jeans](https://digitaltmuseum.org/011023246498) · [SSB, an oil-fuelled economy](https://www.ssb.no/nasjonalregnskap-og-konjunkturer/artikler-og-publikasjoner/en-oljesmurt-okonomi) · [The 1980s in Stavanger](https://www.norskolje.museum.no/en/nrks-award-winning-drama-series-about-the-oil-adventure-in-stavanger/) · [1980s glasses](https://en.wikipedia.org/wiki/1980s_in_fashion) · [Stavanger byarkiv](https://lokalhistoriewiki.no/wiki/Stavanger_Byarkiv) · [Arne Kaada](https://lokalhistoriewiki.no/wiki/Arne_Kaada) · [Why clothes go out of use](https://files.nettsteder.regjeringen.no/wpuploads01/sites/573/2024/11/Kirsi-Laitalai-Tekstiler-mobler-og-utstyr.pdf)

Population and fairness: [SSB 06913](https://data.ssb.no/api/v0/no/table/06913) · [SSB 07459](https://data.ssb.no/api/v0/no/table/07459) · [SSB 07110](https://data.ssb.no/api/v0/no/table/07110) · [SSB conscripts, 4.22](https://www.ssb.no/a/histstat/tabeller/4-22.html) · [Tromsø heights, Arntsen et al. 2023](https://pmc.ncbi.nlm.nih.gov/articles/PMC9876240/) · [HUNT, Midthjell et al. 2013](https://pmc.ncbi.nlm.nih.gov/articles/PMC3734732/) · [Bergen growth references](https://pubmed.ncbi.nlm.nih.gov/23414181/) · [Glasses survey](https://kommunikasjon.ntb.no/pressemelding/19092205/3-av-4-bruker-briller-eller-linser) · [Hearing aids, HUNT](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10867996/) · [Left-handedness](https://research-repository.st-andrews.ac.uk/handle/10023/19889) · [Eye colour in Norway](https://pmc.ncbi.nlm.nih.gov/articles/PMC8227851/) · [Sims 4 skin tones](https://www.gamesradar.com/new-sims-4-skin-tones) · [Shirley cards](https://99percentinvisible.org/episode/465-shirley-cards/transcript/) · [Berkofsky](https://slrlounge.com/ava-berkofsky-of-hbos-insecure-on-how-to-light-dark-skin) · [Textured hair](https://gdusa.com/?p=60358) · [Babyface overgeneralisation](https://pmc.ncbi.nlm.nih.gov/articles/PMC5473630/) · [Changing Faces](https://www.changingfaces.org.uk/news/our-call-on-bond-producers/) · [Harper, fatness in games](https://gdcvault.com/play/1022209) · [Martins et al. 2009](https://nature.berkeley.edu/garbelottoat/wp-content/uploads/martins-etal-2009.pdf) · [Williams et al. 2009](https://abcnews.go.com/Technology/GameOn/video-games-diverse-cast-characters/story?id=8639400) · [Crawford et al. 2017](https://carta.anthropogeny.org/node/315268) · [DeBruine, kin resemblance](https://research-portal.st-andrews.ac.uk/en/publications/social-perception-of-facial-resemblance-in-humans/) · [Paralives genetics](https://paralives.wiki.gg/wiki/Genetics) · [Monk Skin Tone Scale](https://skintone.google/)

Tools: [MPFB in closed-source games](https://static.makehumancommunity.org/mpfb/faq/use_in_closed_source.html) · [Anny paper](https://arxiv.org/html/2511.03589v2) · [Anny repository](https://github.com/naver/anny) · [Anny announcement](https://europe.naverlabs.com/blog/anny-a-free-to-use-3d-human-parametric-model-for-all-ages/) · [Blender Studio Human Base Meshes](https://www.cgchannel.com/2023/06/download-blender-studios-free-human-base-meshes) · [Blender asset bundles](https://www.blender.org/download/demo-files/) · [Quaternius licence](https://quaternius.com/license.html) · [Unity Mesh LOD](https://docs.unity3d.com/6000.2/Documentation/Manual/lod/mesh-lod-introduction.html)
