# R2a's stones: the plan and the shared contract

Port step 2b, rung R2a, second half (`../../design.md`, The ladder; `../patches.md`, the read of 23 October). Written before building, 23 October. The report replaces this page's role once the stones are judged; this page stays as the contract the two builders worked to.

## In short

- **Question.** Do three stones made as SN1 and SN4 say (a rigid convex block cut by planes, few planar marks, chamfered arrises) with the six face patches on them (SN6) hold SN7's restraint and SN8's budgets at 1, 5 and 12 m? Does L1 (no chamfers, the lit line kept by the edge distance) pass for L0 at 8, 10 or 12 m in fog, in stills and in motion? And which split face does the wall stone want: the patches as built, facets ×2 (about 3 L* at 5 m), or the minor ledges off?
- **Done.** The three parts pass their checks and budgets. The sheets, the numbers and a report (In short first, honest faults, what a reviewer should judge) are in this folder. The A/B gives evidence for SN7's split-face number, proposed to the coordinator. A strict review on Fable passes before anything goes to Øystein.
- **The bar** is the reference board (`docs/references/stone/`: 05 and 10 for the faces, 06 for the stair) and the design's numbers. The street target (`reviews/lt1/heart/target/3-street-gully-steps-target.png`) gives only the light it was painted in, blue hour. It is not the look's bar (Øystein, 23 October: "why are you judging this image?"; his earlier "this very dead image", the revert `a122fac`).
- **Lights.** Every frame is rendered in all three of the heart's moments: 1300-drizzle, 1600-low-sun and 1750-blue-hour (the target's light). Grey (`_Grey`, every pigment one grey) comes first, then material. The core rule is to test in several lights.
- **Sizes.** The step comes from the stair's facts. The wall stone and the coping wait for R1's round-2 layout (commits starting `LT1: 2b R1 round 2`) and take typical stones from it.

## The export route, and why

FBX plus a sidecar JSON per part, with L0 and L1 as two objects, installed into `unity/Assets/Experiments/LT1/R2a/Generated/` (git-ignored, with its `.meta`). The mesh-hash manifest stays in git beside the part code (`blender/parts/stone/slate/stones.manifest.json`).
- `docs/building-blocks.md` sends library parts, which part functions make and the town instances, out as FBX plus a sidecar. These three stones are exactly that, judged alone.
- Chunks are never FBX, and the chunk format has no writer or reader until the port's step 5 (`schemas/chunk-format.md`).
- Generated binaries are rebuilt, not tracked, and their hashes are kept in git (D1.6).
- The installs go through `stone.py`'s `install_lock` and `_export_fbx` (imported, never edited), so a Unity run never sees a file rewritten under it.

## The vertex layout (Stone.shader's port layout, plus two channels)

The stones are drawn by `Stone.shader`, so they carry the gully's present layout. Building-blocks' chunk layout arrives with step 5. All channels are Float32 UVs, read back in Unity after import and compared with the sidecar.

| Channel | Holds |
| --- | --- |
| UV0 | metres in the face's own plane, with the face's patch offset and turn by seed already applied. A split face takes only a half turn or a mirror in u, with u along the cleavage; a bed face takes any turn. The shader samples the patch at UV0 / 1.024 (a patch is 1024 texels at 1 mm). |
| UV1 | (years / 200, seed), as the gully: years 1989 − 1874 = 115 |
| UV2 | (face kind, water layer): 0 the tread's top, 1 a chamfer, 2 a split face, 3 a bed face; water layer 0 |
| UV3 | bake (sky, ground): sky from the normal (0.5 + 0.5 n_z), ground 1. Loose stones have no neighbours to occlude them; the same for every arm. |
| UV4 | (polish, lichen / 200): polish from `wear.py` on the tread, else 0; lichen 0 (cut, SN7) |
| UV5 | (moss, water held): 0 |
| UV6 | (d0, d1): see UV7 |
| UV7 | (d2, code). d0 to d2 are, per face corner, its triangle's distances in metres to the three edges, as the solid-wireframe trick stores them: corner i carries its height over the opposite edge in component i, 0 in the others, so the interpolated value is the distance to each edge. code = slice + 8 × mask + 64 × chamfer, all integers: slice is the face's patch, 0 to 3 split-0..3 and 4 to 5 bed-0..1, 7 for none; mask's bit i is set when the edge opposite corner i is an exposed arris that L0 chamfers; chamfer is the stone's chamfer width in whole mm (10 to 12). L0 carries mask 0 everywhere. |

## The patch array

There are 14 slices, each with height, normal and value: the six as built, then facets ×2 on split-0..3, then minor ledges off on split-0..3. The mesh stores the as-built slice. A global `_OS_PatchArm` (0 as built, 1 facets ×2, 2 minor off) moves a split slice to its arm, and a bed slice never moves. The arms' maps are made by `patches.py` (`facet_gain=2.0`, and a new `minor=False`) into `cache/stone/patches/`.

## The judging set

- **Scene.** The heart staged in memory as `LT1Stone.Stage` does, and never saved. The stones are set on the street near the gully's foot, inside a lamp's pool. The step lies as a bottom step, the wall stone stands on its bed with its face to the street, and the coping lies top up. The lens is the 28 mm one (Lens28, 46.4° vertical): the harsher pixel size, which SN4 and SN8 are written against.
- **Each stone** in grey, then in material, at 1, 5 and 12 m, face-on with about 20° of top seen, plus a view from eye height (1.6 m) at 5 and 12 m.
- **The levels.** L0 against L1 at 8, 10 and 12 m with the town's fog on, in stills, and in motion: a dolly from 6 to 14 m, switching at each candidate distance, with the pop measured as the change at the switch frame against its neighbours. L1 casts shadows at every distance; L0 casts none (ShadowsOnly).
- **The arms,** on the wall stone at L0, at 1 and 5 m, with the footprint fade on: as built, facets ×2, and minor ledges off. Each arm is shown against as built, in grey and then in material.
- **Frames.** Native 2560×1440 (`PlayerFrame`: one sample a pixel, MSAA 4×, never supersampled), so never `LT1Render.Still`.

## The measures

- Lines and specks, as `tools/r0b_count.py` defines them, in each stone's mask.
- Floating lines: any line more than 2 px from a mesh edge, against a render of piece ids and normals (SN9). None is allowed.
- The face spread, L* p5 to p95 per face, in grey, as `../patches.md` defines it.
- The thin triangles and the median visible triangle at L0's 8 m and L1's 20 m (SN8).
- The chamfer's width in pixels at 8 m.

## Who builds what

- **Blender** (a fresh Opus agent): the shared block machinery, the step, then the wall stone and the coping; SN9's checks, the budgets, the export, the part definitions, the quick sheet, and the patches' arms.
- **Unity** (a fresh Opus agent): the patch array, the shader's keyword arm (`OS_PATCHES`, a shader_feature), `LT1R2a.cs`, the id and edge render, and the measures.
- **The coordinator** (this session): reads the frames and numbers, writes the report and the SN7 proposal, and runs the strict review (Fable).
