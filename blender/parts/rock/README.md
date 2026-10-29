# Rock and land (Nature, element 1)

## Where it stands (29 October)

- **Look-in 1 judged:** the boxed history (keyed fractures and topple) made crates. The big form starts again from ice-rounded masses. The history (plucked steps, a rockfall scar, foot boulders) acts on the mass and may not make it.
- **Look-in 2: the target frame** (`target_whaleback.py`). A coarse block-out with a painted finish, from the shelf along the face into the low sun:
  - Whalebacks of a few big planes, turfed.
  - A sheer face in facets drawn out along the steep foliation, with a cave slot.
  - Skerries, a shingle pocket, a swell with foam, the shore's zones.
  - Sheet: `cache/rock/whale/w11/sheet.png`. It holds the target, its grey, the floor (t04) and references 51, 48 and 49.
- **Floor:** grey c20 (`cache/rock/bluff/c20/`) for the history and the raised view; t04 is the old target.

## Build

    Blender -b --factory-startup -P blender/parts/rock/target_whaleback.py -- --out cache/rock/whale/wNN [--grey 1] [--rebuild 1] [--cam x,y,lx,ly,lz,lens]
    Blender -b --factory-startup -P blender/parts/rock/sheet.py -- OUT.png COLS IMG...

The land caches in `land.npz`. `--rebuild 1` remakes it after a form change (about 5 s).

## Next, after the target is approved

The big form in grey, beside the target. Masses first, then the history acting on them. Every still carries a cost line.

Budget: 60–100k triangles in view for the hero face, with the foliation in normals and LODs. The target's block-out is 857k rock faces at 0.25 m. It sets no cost; it is not the build.

## For the town

`centre_land.py` uses the CLIFFS sign the other way round. It is left as it is, and the term stays out of this folder's code. The town's owner fixes it.
