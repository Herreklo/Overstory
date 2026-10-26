# R2b: the stones redrawn by make, look, fix

## The wall stone: done, 26 October

- **The part:** `blender/parts/stone/slate/split.py`, a split slate face stone. Its outline is fitted to its cell: the top sloping, the ends split on a slant and broken once, the top sometimes stepped, the top corners knocked. Its face rises to one or two points, its arrises are weathered round, and its sides run back into the joint. **The laying:** random coursed, as reference 10 is (`tools/r2b_wall.py`). Every number is in the definition (`wallstone.json`) or the working (`walling.json`).
- **The look:** `wallstone/round01-sheet.jpg` is the start; `round09` is the first round whose grey form read as split stone. `round11` is the final round, beside reference 10 in grey and in drizzle. Its joints are dark voids because a joint's sky is now a slit's (g/(g+2z) from the back of the arris), and lichen stops where the light does. In `lights-sheet.jpg` it holds in morning shade, low sun and blue hour, from eye level and the street stop to 12 m raised and near-isometric.
- **Budget:** L0 is 40 to 52 triangles (mean 45). `r2b_wall.py` fails any stone over the definition's budget; 1,532 stones over three seeds pass.
- **Switch:** L1 is L0. `switch-d6-l0-l1-diff.jpg` shows L0, the stone without its sides, and the difference. From an eye along the wall, each end's side shows where a stone stands proud of its neighbour, so without sides 4% of the wall's pixels change by more than 3 L* at every distance from 6 to 18 m (grey 1.3 to 2.1%). A one-surface L1 changed 28 to 42%. The stone hands over to the chunk's L2. The check is `tools/r2b_switch.py`; its floor (L0 against itself) is 0.
- **Not mine, open:**
  - The growth layer's near lichen reads as pale fields on dark rock. Reference 10 is the other way round: a pale crust with dark specks. That is a town system (`Growth.hlsl`), not changed here.
  - The faces' fan creases show faintly in grey under look P's ramp.
  - `split.py` is not yet wired into `context.py`, so the gully's export still builds R2a's stone.
- **Cost:** about 125 messages and 144 rendered frames, against R2a's 1,295 messages and 37,793 frames for all three stones.
