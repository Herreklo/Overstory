# Rock and land (Nature, element 1)

## Hand-over (29 October)

The lane is paused while Øystein and the coordinator rethink how nature runs: until now the rock was judged on its own, in Cycles, while the houses ran far ahead. The last round is s27 (`cache/rock/site/s27/`): grey and colour stills, sent as they are and not yet judged.

### What holds

- **Form by exposure (Øystein, 29 October).** Rock is round or sharp by where it is and what worked on it. It must look nice, and never read as melted or as tiles. In `target_site.py` this is the `WEAR` table, as data:
  - the plucked face crisp (0.1 m);
  - the storm-wash zone, to about 3.6 m over high water, worn round (1 m), with potholes on the shelf's crests;
  - the tops ice-rounded and under turf;
  - each block as sharp as it is fresh, rounded by its years in the sea.
- **Slabs along the foliation.** The face is the slabs between the steep foliation joints (dip 68° toward 250°).
  - Widths are lognormal, median 3.8 m.
  - Each slab is flush with its neighbour or stepped in or out, and more often stepped where the sea and the frost plucked the mass.
  - Each slab's face carries a low wave of about 0.2 m over 3–4 m, so no large plane is flat.
- **Sheet joints.** They dip 12° to the sea: close under the top, metres apart lower down.
  - They wander and step en echelon from slab to slab, so a ledge runs a few slabs and ends.
  - A face only recedes upward.
- **The zonation, from the sea up:**
  - the tide zone, even, dark and finely barnacled, below 0.95 m;
  - the storm-wash zone, round;
  - the plucked face, grey stone with dark run-off streaks and dark open joints;
  - pale crustose lichen, only on rock that faces the sky above about 5 m;
  - turf over the lip.
- **The site facts:**
  - the face on the town plan's bluff line round Herring Hill's point, its foot on the 3 m contour;
  - the Hundred Steps on the west shoulder and Cannery Bight at the east end;
  - the fresh scar (x 50, z 13), paler and sharp, with its blocks at the foot;
  - the sea caves in the crush zones;
  - the ribbed low-tide shelf;
  - the Teeth and the Pip;
  - the light: 21 June at 21:40, the sun 6° up at bearing 307.
- **The grey stone and the crisp edges.** The coordinator on look-in 3: "a yes".

### What failed and why

- **Look-in 1, the fracture network** (`bluff.py`, `cliff.py`): boxes, fins and a castle skyline. Any break smaller than about 4 voxels across melts at 0.3 m.
- **Look-in 2** (`target_whaleback.py`, w11): the composition holds (whalebacks, skerries). The faces melted, the site and the light weren't ours, and the paint was a filter.
- **s13:** rounding everything the same way read as melted ("like a mistake").
- **s22:** Voronoi chip facets read as crazy paving.
- **Lichen and barnacles thresholded from noise** read as camouflage.
- **Look-in 3** (s25): straight sheet joints across the steep foliation made a grid of panels (a dam, a quarry), and the flat slab faces read as poured concrete. s26–s27 answer both.
- **Open in s27:**
  - At 0.3 m voxels the wave is on the edge of looking lumpy.
  - The swell's undercut at the foot reads as a plinth in the shelf view.
  - The foam lace is not judged yet.
  - The scar's ledge reads as a ramp from the boat.
  - The frame's composition is weaker than w11's.
  - The Steps and the quay frame aren't built.
  - There is no cost line.
- **The method itself.** The face is a signed-distance block-out voxelled at 0.3 m: 900k triangles, about 2 minutes a still in Cycles. It can't carry an edge or a break under about 1.2 m. It is a target, not a build. The build budget is 60–100k triangles in view, with the foliation in normals. A build would need rigid slabs as parts (`hull.py`'s planes), not the field.

### Where everything is

- **Scripts** (`blender/parts/rock/`):
  - `target_site.py`: look-in 3 and this round, covering the site, the face, the shelf and potholes, the blocks, the materials, the foam and the paint. The command is in its docstring. It caches `band.npz` in each output folder (`--rebuild 1` remakes it, about 60 s).
  - `target_whaleback.py`: look-in 2, and the rock, turf, sea and foam materials that `target_site.py` wraps.
  - `target.py`: the node writer, the light and Cycles, and the Holm tip's target. `target_bluff.py`: the Bluff's first target.
  - `bluff.py` and `cliff.py`: look-in 1's Bluff from its joints and history.
  - `hull.py`: convex bodies cut by planes. `outcrop.py`: an outcrop as its jointing breaks it.
  - `blockin.py`: the Holm tip in grey. `views.json`: its views and lights. `run/render.sh`.
  - `sheet.py`: contact sheets.
- **Fixtures:** `fixtures/lt1-bluff.json` (the Bluff) and `fixtures/lt1-holm-tip.json` (the Holm tip).
- **The site's facts:** `cache/rock/site/bluff-site.json` and `ground.npz`, read once from `blender/blockouts`. `--site 1` remakes them, in about 3 minutes.
- **Renders:**
  - `cache/rock/site/s01`–`s27`: s25 is look-in 3, s27 the last round.
  - `cache/rock/whale/w01`–`w11`: w11 is look-in 2 and the floor.
  - `cache/rock/bluff`, `target`, `blockin`: look-in 1 and before.
- **Research:** `docs/research/land-rock-and-water.md`, `docs/research/stone.md`.
- **References** (`docs/references/stone/`): Nielsen 48, Tinganes 49, Hertervig 51, and Firewatch in `study/21`–`22`.
- **Unity:** `unity/Assets/Experiments/LT1/Nature/` holds `Editor/LT1Nature.cs`. The scene and `Generated/` (the Holm tip's export) are untracked.

## For the town

`centre_land.py` uses the CLIFFS sign the other way round. It is left as it is, and the term stays out of this folder's code. The town's owner fixes it.
