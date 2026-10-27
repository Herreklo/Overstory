# Trees for the corner: how three studios build them

## Firewatch (Campo Santo, Unity)

23 hand-modelled trees, placed about 4,600 times (secondary), at real heights of 20 to 30 m. Each was built for its silhouette at distance; only the lower branches, within reach, get close care. Pines are abstracted into tufts of needles. The foliage shader changes the alpha-test cutoff with distance, so the crown swells and its outline simplifies (curve not given); a fog made from an RGBA colour strip indexed by distance does the rest. Draw calls were the limit: moving trees could not be batched, and a forest has no occluders.
[GDC 2015](https://gdcvault.com/play/1022295/The-Art-of) · [NYU lecture](https://www.youtube.com/watch?v=3yWIoRuwpm0) · [PC Gamer](https://www.pcgamer.com/why-less-is-more-when-it-comes-to-firewatchs-beautiful-trees/)

## Ghost of Tsushima (Sucker Punch)

Trees are modelled in SpeedTree, drawn by an in-house runtime. Each vertex stores the start and end of its branch and sub-branch; the vertex shader turns trunk, branch and twig with the local wind, plus a sway phased by a position hash. Far hillside impostors sway too. Art direction: few foliage species, strong colour, texture noise removed. Environment normals were too inconsistent to shade with directly, so the soft (fuzz) layer uses energy-conserving wrap, w = 0.2. Card normals, levels, alpha and budgets are not published.
[Rockenbeck, GDC 2021](https://gdcvault.com/play/1027124/Blowing-from-the-West-Simulating) · [Connell, GDC 2021](https://www.youtube.com/watch?v=n0MO-mjzczU) · [Patry, SIGGRAPH 2020](https://blog.selfshadow.com/publications/s2020-shading-course/patry/s2020_pbs_patry_slides.pdf)

## Breath of the Wild (Nintendo)

Not published: the CEDEC 2017 graphics talk banned photos and released no slides. Reports: plants drawn in full detail everywhere looked cluttered, so objects simplify with distance; the frame is built in near, middle and far layers (fog in the middle, lit haze far); over 200 look parameters were cut to 50. Trees are world objects that fall into logs and burn. "BotW-style" sphere-normal crowns are community guesses.
[CEDEC session](https://cedec.cesa.or.jp/2017/session/VA/s58eed7182c81b.html) · [Famicast translation](https://thefamicast.com/2017/12/part-5-art-and-implementation-of-3d.html) · [4Gamer](https://www.4gamer.net/games/341/G034168/20170303060/)

## Better on details: Horizon Zero Dawn, SpeedTree

Horizon transfers card normals from an isosurface around the canopy, turned toward the camera; it breaks lighting, so it is used selectively. Alpha first grew with distance in the shader, then moved into offline mips that keep coverage at the 0.5 clip (saving about 3% of the frame). An alpha-tested depth prepass lets colour skip the test. Six levels, cross-plane billboards at the last two, built lowest first; two separate shadow casters, the second neither alpha-tested nor animated; shadow levels fixed per cascade, which ended popping. SpeedTree drops to fewer, larger cards and fades to billboards with alpha-to-coverage.
[Sanders, GDC 2018](https://gdcvault.com/play/1025066/Between-Tech-and-Art-The) · [SpeedTree LOD](https://docs.unity3d.com/speedtree-runtime-sdk/manual/level-of-detail.html)

## What we take

- **Silhouette first.** The near birch gets care where the camera reaches (trunk foot, bark, first forks); its crown dissolves upward. The spruce and heath birches are shapes: no cards, one closed low-poly silhouette each at fog + 5.
- **Normals from masses.** Three to five hulls per crown; each card takes its own hull's normal, turned toward the camera. Cards are large: a quarter to a third of the mass's width, our value to test.
- **Three values a mass:** shade body, one lamp-lit side (wrap, w about 0.2 to start), a darker underside. Flat albedo, no leaf noise. Baked vertex shade at the trunk foot.
- **Alpha:** the frame has 4× MSAA, so alpha-to-coverage with coverage-preserving mips. Any closing of holes with distance goes into the mips.
- **Levels:** to 12 m, mesh and mass cards; to 50 m, fewer, larger cards, no bark, no twig motion; to 130 m, one silhouette mesh; beyond, a cross-plane or nothing. No impostors. Cheaper separate shadow casters.
- **Wind:** Tsushima's per-vertex hierarchy, hashed phase, strength from the day's weather; in calm fog only the near birch moves.
- **Budget:** none of the three gives a per-tree triangle count; draw calls and overdraw hurt. One bark and one card material a tree, instanced clumps; count with `tools/check.py`.
- **Trees are records:** a pruned or broken limb changes data, not the model.
