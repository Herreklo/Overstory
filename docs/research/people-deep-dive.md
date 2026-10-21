# People: the deep dive

Draft, for Øystein. It asks four things. What makes someone recognisable across years and scenes at our cameras' distances? Which of three stylisations should we test first? What should we commission, and from whom? How do we make thousands of people without sameness or stereotype? It builds on the first survey (`people.md`). Claims taken from summaries are marked (secondary); claims we could not confirm, (unverified).

## What our cameras see

A figure 1.75 m tall through the 35 mm lens (38° vertical):

| View | Distance | Figure, 1080p / 1440p | Head |
| --- | --- | --- | --- |
| A scene | 3 m | 915 / 1220 px | 120 / 160 px |
| The steps, near | 5 m | 549 / 732 | 72 / 96 |
| The steps, middle | 15 m | 183 / 244 | 24 / 32 |
| The steps, far | 25 m | 110 / 146 | 14 / 19 |
| City camera, close stop | 30 m | 91 / 122 | 12 / 16 |
| City camera, pulled out | 60 m | 46 / 61 | 6 / 8 |

Distance removes detail as blur does (Loftus & Harley 2005), and night removes more (secondary). For most of the game a person is a figure 50 to 250 pixels tall with a head of 6 to 30. The face matters mainly in scenes.

## A. What makes a person recognisable

### Perception

- Familiarity decides. People who knew the targets recognised them from poor security video; strangers, police included, did badly (Burton et al. 1999). Sorting 40 photos of two strangers, people made 7.5 identities on average (Jenkins et al. 2011, secondary). For strangers, a change of clothes (Seitz 2003, secondary) or hairstyle (secondary) breaks recognition. So the game must make people familiar before it asks the player to recognise them.
- Known faces survive low resolution. Familiar faces were named more than half the time at 7×10 pixels, and at ceiling at 19×27 (Yip & Sinha 2002, in Sinha et al. 2006). The whole head carries it: internal features alone fail under blur and hair and jaw alone never pass 40%, but the full head holds up. Brows are among the most important features, and colour helps most when shape is degraded. On the steps, then, a well-known face helps to about 15 m and supports to 25 m (our reading of the table). From the city camera it is gone.
- The body takes over at distance. When the face is uninformative, people still identify the whole person, and their eyes move to the body without their knowing (Rice et al. 2013, secondary). The body adds to recognition at large distances, not close ones (Hahn, O'Toole & Phillips 2015, secondary).
- Gait identifies. Friends know each other from lights on their joints as they walk (Cutting & Kozlowski 1977), and walkers are learnt in simulated dusk (Stevenage et al. 1999, secondary). Gait carries age too: youthful gaits read as happier and more powerful, whatever the walker's age (Montepare & Zebrowitz, via a replication, secondary).
- Attention is thin. In one study, half of pedestrians missed that the stranger they were talking to had been swapped. The new man differed in height, build, hair and clothes (Simons & Levin 1998).
- Variety builds memory. Learning a person across varied looks gives sturdier recognition than one fixed view (Corpuz & Oriet, secondary).

### Artists

- Silhouette first. TF2's classes are told apart by silhouette, then by value (dark feet to a light chest where the hands work) and by rim light instead of outlines (Mitchell et al. 2007). Somerville began with readable silhouettes and costume accents at the joints so movement reads; it dealt with faces only when the camera came close (Jumpship).
- One accent. INSIDE's boy has no face; a red shirt in a grey world does the work (secondary). For us the accent must be a fact: a coat the person owns.
- McCloud asks for inner life, visual distinction and expressive traits such as posture, fidgets or a limp (secondary).
- Caricature helps memory. Faces seem to be stored slightly caricatured, and caricatures are recognised as well as true likenesses or better (Sinha et al.). It is also how racist caricature works; see D.
- Ageing in real time. Gasoline Alley aged its cast in real time: Skeezix, left on a doorstep in 1921, was middle-aged by the 1960s. In Love and Rockets, Maggie ages over decades, gains weight and comes to look like her aunt (secondary). Readers who have followed someone accept large change, and family likeness can grow with age.

### Games that age people

| Game | How identity holds | What we take |
| --- | --- | --- |
| Crusader Kings 3 | A DNA stream from both parents; portraits age and show lifestyle and illness as overlays (secondary) | Heredity and age as separate layers |
| The Sims 2, Paralives | Inherited features; Paralives passes each feature group whole from one parent so the likeness is easy to spot (secondary) | Inherit groups, not averages |
| Fable 2 | Good heroes tan and go fair, evil ones go pale with black hair; corruption brings horns (secondary) | What never to do: looks as a moral verdict, coded in skin and hair |
| Pentiment | 25 years, three acts; 157 rigged characters with hand-drawn expressions; class shown in each person's typeface (typeface secondary) | Identity can live outside the body; hand-made does not scale |
| Disco Elysium | A painted portrait in dialogue, a plain 3D figure in the world (secondary) | Two levels of detail for one person |
| Kentucky Route Zero | Flat, stencil-like figures, detail hidden by light (secondary) | Light can carry a barely modelled person |

Firewatch, Sable, Life is Strange and Hades have small hand-designed casts. They teach shape language, not generation.

### Rules for us

1. Identity anchors are set at birth and never re-rolled: grown height, head shape, the brow and eye region, base hair colour and texture, a gait seed. Age, weight, work and taste transform them. Nothing replaces them.
2. Cues by distance. From the city camera: silhouette (height, build, posture), hair mass and colour, the colour of the outer layer, gait, where they are and with whom. On the steps, add the whole head and the brows. In scenes, the face, hands and expression.
3. Contrast where it reads: hair against skin, brows, the outer layer against the town. Every colour on a person comes from their body or clothes, so it is a fact.
4. Taste is continuity. The engine's taste with years keeps a coat colour or a cap across a decade. A signature item exists only where the engine says it is owned.
5. Familiarity is designed. A person is met in varied scenes, lights and clothes, with a name, before the game relies on recognising them. Recognition is tested on viewers who have met the person.

## B. Three stylisations

| | 1. Painterly realism | 2. Stylised 3D | 3. Realistic base, toned |
| --- | --- | --- | --- |
| Best references | Stålenhag, Kentucky Route Zero, INSIDE, Disco Elysium's figures | Arcane, Sable, Somerville, SEASON | MetaHuman, Character Creator, Daz |
| Recognisable at 15 to 30 m | Silhouette, hair, colour, gait; face barely | Best: a bigger head brings the face into readable size | Weak: realistic faces at 15 px look alike |
| Close scenes | Weakest: needs a face that can act | Strong | Strong, but uncanny beside painted walls |
| Ageing | Anny's age axis as it is | Each age key redesigned | Built in |
| Thousands of people | Straight from MPFB/Anny targets | Needs a commissioned stylised target space | Targets exist; licences restrict generators |
| Animation | Library and mocap fit | Retarget fixes for head and hands | Mocap fits; realism raises expectations |
| Crowd cost | Low | Low | High: skin, hair, facial rig |
| Fit with our world | Best | Good if planar and restrained | Poor |
| Our cost | Lowest, mostly in-house | Highest, needs an artist | Cheap to start, dear to tame |

Painterly realism (1) keeps true proportions on the MakeHuman/Anny base. Forms are simplified into planes and painted with the world's brush size. The face is a few planes with painted brows, eye shadow and mouth: realism in shape, painting in material. That split matches a finding on rendered faces: shape drives how real a face looks and how strongly it shows expression, while material drives appeal (Zell et al. 2015). It costs least, since the base exists and our painting module can paint it. Its weakness is the close scene, where Stålenhag's faces would not carry a conversation. The answer is a near tier for the face, as Disco Elysium has two levels: the same head, with more painted detail and painted expressions near the camera.

Stylised 3D (2) uses planar, simplified forms with a push to head, hands and feet, and painted textures that sit in painted backgrounds, as Arcane's do (secondary). It reads best at distance and up close. But its references are hand-designed casts. A stylised target space for thousands is a commission of its own, and the round, puffy end of this family is the generic look our direction rejects.

A realistic base (3) is toned by our light. MetaHumans may now be used in Unity under the Unreal licence, free below $1 million a year in revenue (secondary). But they are made one at a time through Epic's cloud tools, with strand hair and a facial rig built for Unreal (unverified in Unity). Character Creator 5 costs $299, and store content needs export licences (secondary). Reallusion staff have said its content may not drive an in-game character generator without an enterprise licence (secondary), and our people system is one. Daz needs an interactive licence per product. Realistic skin and eyes in a painted world is the mixed realism people find eerie (MacDorman & Chattopadhyay 2016), and the reality check rules out photoreal anything.

Options 1 and 2 are the ends of one dial, as with the houses: true proportions to a modest push. The look test finds the setting.

## C. Commissioning

### What to commission

One stylised base, made as a system:
- A body built as shape targets on Anny's mesh (13,718 vertices, 163 bones, Apache 2.0), so its age, weight, muscle and height targets keep working.
- Stylised corrections at age keys (about 8, 15, 35 and 70) for both sexes, since a child is not a small adult.
- 8 to 12 archetype body targets (`people.md`).
- A head with 20 to 30 identity targets, proportions first: face length, jaw width, brow height, eye spacing, nose bridge. Brow shapes, painted expressions, a few mouth and brow shapes.
- Hands that read at 15 m; 6 to 10 hair masses as planar shells that fit every head.
- A fit test: a knit, an oilskin coat and trousers that follow every target.
- A rig that maps to Unity's Humanoid avatar and plays Mixamo and 100STYLE clips at the extremes of the target space without breaking.
- Three levels of detail, to the foundations page's budgets.

### Who, and what it costs

Vendor guides put a stylised game character at $2,000 to $5,000 and a cinematic one up to $20,000 (secondary; vendors' own figures). They put senior freelancers at $50 to $150 an hour. Forum figures for European freelance character artists start at $200 to $400 a day, and single listings run past $600 (secondary). Ours is a system, not one character. Our estimate is 40 to 80 artist-days at a senior rate of $400 to $750 a day: $16,000 to $60,000 over two to four months, after a paid trial.

Look first on ArtStation and Polycount, for freelancers whose work shows restrained stylisation and topology made to deform, and among Blender artists who know MPFB. Studios that make stylised and semi-realistic humans for Unity (ZE Studio, Room 8 and others, secondary) are a dearer fallback with more process. A paid trial from two or three artists chooses the artist: one head and one body target on Anny's topology.

### What we can do ourselves

| Tool | Licence | Use |
| --- | --- | --- |
| MPFB2 / MakeHuman | Assets CC0; code GPL, and we ship only exports | Base, targets, clothes fitting, rig |
| Anny | Apache 2.0 | The age axis, infants to elderly |
| Blender Studio base meshes | CC0 | Stylised starts for option 2 |
| Mixamo | Royalty-free in games; raw files not redistributed, not for training models (secondary) | Clip library |
| 100STYLE | CC BY 4.0, credit required; 100 styles, over 4 million frames | Walks by mood, age and state |
| CMU mocap | Commercial use allowed, not for resale | Base motion |
| Unity Animation Rigging | Unity | Gaze, foot planting, posture layers |
| UMA | Free on the Asset Store (licence unverified) | A runtime assembler with DNA and wardrobe recipes, if ours is slow to build |
| Character Creator 5, MetaHuman | See option 3 | Reference only |

Unity 6's GPU Resident Drawer handles only Mesh Renderers. Skinned crowds need their own path: animation baked into textures, or GPU skinning (Rukhanka, or GPU Instancer Pro's crowd module, both paid). Motion matching exists (a community MxM fork is tested on Unity 6) but is not needed.

### The brief, in outline

1. The game and the question: a person recognisable across years and scenes; our distances (the table above); the world's look, with our renders and reference board.
2. The style target: two or three paintovers of our grey figure in our scenes, agreed before modelling.
3. Deliverables as above, named and scaled by our conventions; `.blend` sources with every target; FBX.
4. Technical rules: Anny's topology, Unity Humanoid, target naming, triangle budgets. Textures follow our one shading model: colour only, no baked light, brush marks at world size.
5. Acceptance: a deformation sheet (every target against the clip set), the silhouette sheet, Unity renders at our cameras in grey light and three lights, a strict review, Øystein's judgement.
6. Fairness: the rules in D, tested across the full range of skin tones and hair types.
7. Rights: work for hire, or an exclusive perpetual licence that covers modifying, deriving and generating people from the work at runtime. No third-party content unless CC0 or cleared. Credit in the game.
8. Process: a paid trial, then fixed-price milestones with two rounds of changes each and weekly renders.

## D. Variety and fairness

### Thousands of distinct people

The survey's rules stand (archetypes as attractors, real spreads stretched, the silhouette gate). Three additions:
- Inherit groups, not averages. Averaging two parents makes children blander than either. Each feature group (brow and eyes, nose, jaw, build) comes whole from one parent with seeded noise, as in Paralives (secondary). Kinship is read mostly from the upper half of the face. Masking it cut sibling judgements by more than 65%, masking the lower half by 5% (Dal Martello & Maloney 2006, secondary). The brows sit there too, so a family's likeness lives in the brow and eye region.
- Height by category from one parent, then the engine's childhood wealth.
- Clothes carry class and work, not faces. A wardrobe is sampled by era, money, work and taste (`people.md`); wear and mending are history. Work clothes appear where the work happens.

### Fairness

Rule 8 and "Evidence, not verdicts" give these rules:
1. Appearance is never a verdict. No face, body, skin or hair says good, bad, clever or lazy; Fable 2's pale, black-haired evil is the failure to avoid. People judge character from faces with confidence and little accuracy (Todorov et al. 2008), so a face shaped by a trait would teach players a false lesson.
2. Push silhouettes, not ancestry. The push applies to build, height and posture. A face, if pushed at all, is pushed from its own family's mean and never from a town average, so no one's ancestry becomes what is exaggerated.
3. No race slider. MakeHuman's macros include ethnicity, and Anny's authors warn that its phenotypes "encode by design stereotypes of MakeHuman artists". Every target is audited before use. Skin, hair and face vary down family lines from founders; who the founders are, and who arrives when, are facts from the engine and the setting pack.
4. Bodies are not jokes. Weight, illness, disability and age come from engine facts and are shown plainly. No sexualised push: bodies are pushed by build, never by sexual features.
5. Every skin tone in every light. The Sims 4's darker skin tones looked ashy and banded until a 2020 fix that followed a player campaign (secondary). Our cool shade, blue hour and sodium light are tested on the full range before any stylisation passes.
6. Posture from state more than trait. The survey drives posture by traits because people read walks consistently (Thoresen et al. 2012). If a trait always shows, the body becomes the game's verdict on character. So state (tiredness, mood, age, injury, company) drives most of it and a trait only part, and a reader can be wrong. This needs Øystein's view.
7. Cold readers from different backgrounds see every people sheet.

## What we recommend

*Decided since (Øystein, 22 October): there is no money for a commission. Everything below that assumes one is set aside: people are built in-house on the free bases in section C, and the stylisation is chosen so that it does not hinge on detailed faces, the one thing a commission would have bought.*


**Test option 1 first, with the push dial:** painterly realism at true proportions on the MPFB/Anny base we already have, painted by our own module. Our people are seen mostly at 15 to 60 m, where silhouette, hair, colour and gait carry identity and the face does not. It fits the world and costs nothing to try. Its weakness, the close scene, has a known answer in a near tier for the face. Run it beside the other two, as planned. Option 2 is the same person pushed (head, hands, planes), started from the Blender Studio stylised meshes; option 3 is MPFB's realistic default under our light. All three are built in-house, so nothing is spent before Øystein has judged them.

The decision for Øystein is whether to commission the base system in the winning style once the test is judged. Our estimate: a paid trial with two or three artists at about $2,000 to $4,000 each, then the system at $16,000 to $60,000 over two to four months. Clothing shelves follow, partly in-house. Without a commission, faces and hands stay the weakest part of the world, as the reality check rates them.

The first look test:
- Question: which stylisation lets a viewer who has met a person recognise them across thirty years, at our cameras, while the person sits in the painterly world?
- Set-up: one person from a fixture at 17, 37 and 67 in era clothes, with five others of similar build and colouring, in each style. Shown on the gully steps at 5, 15 and 25 m, from the city camera's close stop and in a scene at 3 m. In drizzle and at night under a lamp, with skin tones across the range.
- Judging: cold readers meet the person in two scenes, then pick them out of line-ups at each distance and age, and we count the hits. The frames are judged beside the steps' target at thumbnail size and in greyscale, then by the strict review and Øystein.
- What would change our minds: if option 1 fails at 15 m where option 2 passes, people need more push than the houses' dial. If nothing passes at 25 m, identity at the city camera must come from colour, gait and routine, helped by the interface (a name on approach).

## Sources

Perception: [Burton et al. 1999](https://www.face-rec.org/interesting-papers/Other/bwcb99.pdf) · [Jenkins et al. 2011](https://eprints.gla.ac.uk/67032) · [Sinha et al. 2006](https://cs.utexas.edu/users/grauman/courses/spring2007/395T/papers/sinha_20results.pdf) · [Rice et al. 2013](https://news.utdallas.edu/?p=9200) · [Phillips, Rice & O'Toole 2013](https://www.nist.gov/node/575841) · [Hahn, O'Toole & Phillips 2015](https://www.nist.gov/publications/dissecting-time-course-person-recognition-natural-viewing-environments) · [Cutting & Kozlowski 1977](https://researchconnect.buffalo.edu/en/publications/recognizing-friends-by-their-walk-gait-perception-without-familia/) · [Stevenage et al. 1999](https://eprints.soton.ac.uk/250633) · [Montepare & Zebrowitz replication](https://accesson.kr/ksppa/v.10/1/137/25496?lang=en) · [Simons & Levin 1998](https://gwern.net/doc/psychology/cognitive-bias/illusion-of-depth/1998-simons.pdf) · [Seitz 2003](https://zendy.io/title/10.1002/acp.912) · [Hairstyle change, Frontiers 2012](https://doaj.org/article/3594eb0568f4425d80a524a399a084ca) · [Corpuz & Oriet](https://instrepo-prod7.cc.uregina.ca/items/3925f690-93f3-4b67-ac6b-d07382fe171c) · [Loftus & Harley 2005](https://www.washington.edu/news/2005/02/14/murder-case-research-shows-why-its-easier-to-identify-someone-close-than-far-away/) · [Loftus on night viewing](https://www.newsminer.com/news/local_news/expert-witness-reaffirms-original-testimony-in-fairbanks-four-innocence-case/article_a3d2f4c8-7240-11e5-9de6-a79fa08c7e06.html) · [Dal Martello & Maloney 2006](https://doi.org/10.1167/6.12.2) · [Maloney & Dal Martello 2006, kinship](https://www.sciencedaily.com/releases/2006/09/060919102033.htm) · [Zell et al. 2015](https://ls7-gv.cs.tu-dortmund.de/publications/2015-stylize.page/) · [MacDorman & Chattopadhyay 2016](https://www.evl.uic.edu/pubs/2351) · [Todorov et al. 2008](https://homepage.villanova.edu/diego.fernandezduque/Teaching/SocialNeuroSeminar/faces/Todorov_TiCS2008.pdf)

Artists and games: [TF2, Mitchell et al. 2007](https://www.advances.realtimerendering.com/s2007/Mitchell-IllustrativeRenderingInTF2(Siggraph07%20Course%20Notes).pdf) · [TF2, GDC 2008](https://cdn.fastly.steamstatic.com/apps/valve/2008/GDC2008_StylizationWithAPurpose_TF2.pdf) · [Somerville, Jumpship](https://blog.jumpship.co.uk/post/176054619715/developing-character-jumpship/amp) · [INSIDE](https://www.thedailystar.net/shout/game-review/inside-minimalistic-work-art-1260457) · [McCloud, Making Comics](https://fmspracticumspring2017.blogs.bucknell.edu/?p=214) · [Gasoline Alley](https://en.wikipedia.org/wiki/Gasoline_Alley_(comic_strip)) · [Love and Rockets](https://providencephoenix.com/archive/art/01/02/15/LOVE.html) · [CK3 portraits](https://www.thesixthaxis.com/2020/07/31/crusader-kings-3-developer-diary-contracts-portraits/) · [Paralives genetics](https://simscommunity.info/2026/01/10/paralives-genetics-announcement/) · [Fable II](https://en.wikipedia.org/wiki/Fable_II) · [Pentiment, Kennedy](https://www.gamedeveloper.com/art/deep-dive-the-art-of-pentiment) · [Pentiment typefaces](https://lettermatic.basement.studio/custom/pentiment) · [Disco Elysium](https://rpgamer.com/review/disco-elysium-review/) · [Kentucky Route Zero](https://www.bit-tech.net/reviews/gaming/pc/kentucky-route-zero-review/2/) · [Arcane](https://redsharknews.com/why-netflixs-arcane-looks-so-good-how-fortiche-ramped-up-the-animation-pipeline) · [Sims 4 skin tones](https://www.gamesradar.com/new-sims-4-skin-tones)

Tools and licences: [MPFB closed-source FAQ](https://static.makehumancommunity.org/mpfb/faq/use_in_closed_source.html) · [MakeHuman macros](https://static.makehumancommunity.org/makehuman.html) · [Anny paper](https://arxiv.org/html/2511.03589v2) · [MetaHuman licence](https://www.cgchannel.com/2025/06/you-can-now-sell-metahumans-or-use-them-in-unity-or-godot/) · [Character Creator 5](https://www.cgchannel.com/2025/07/reallusion-unveils-character-creator-5/) · [Reallusion generator limits](https://forum.reallusion.com/PrintTopic525669.aspx) · [Daz interactive licence](https://www.daz3d.com/interactive-license-info) · [Mixamo FAQ](https://community.adobe.com/questions-696/mixamo-faq-licensing-royalties-ownership-eula-and-tos-589400) · [100STYLE](https://www.ianxmason.com/100style/) · [UMA](https://assetstore-fallback.unity.com/packages/3d/characters/uma-2-35611) · [GPU Resident Drawer](https://docs.unity3d.com/6/Documentation/Manual/urp/gpu-resident-drawer.html) · [Rukhanka](https://discussions.unity.com/t/released-rukhanka-cpu-and-gpu-ecs-animation-system/908711) · [MxM for Unity](https://motion-matching-for-unity.readthedocs.io/en/latest/faq/)

Costs: [RocketBrush prices](https://rocketbrush.com/blog/3d-character-art-prices-guide) · [RetroStyle Games](https://retrostylegames.com/blog/game-character-design-cost/) · [Polycount day rates](https://polycount.com/discussion/comment/2115286/) · [ZE Studio](https://www.zbrushcentral.com/t/3d-character-animation-art-outsourcing-ze-studio/358896) · [Room 8](https://jobs.dou.ua/companies/room8studio/vacancies/333370/)
