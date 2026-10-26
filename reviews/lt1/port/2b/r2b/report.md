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

## The step: done, 26 October

- **The part:** `blender/parts/stone/slate/slabstep.py`, a slab step of split slate as reference 06 shows one. It is a slab the rise thick, laid on its bed. Its front and open ends are split across one to three laminae, each in or out of the next along the step, so their line comes and goes. Its nosing is rounded unevenly, more where the feet wear it. Sometimes a thin flake of the top is lost from the nosing: the break is sharp and the lamina beneath shows. Its corners are knocked. **The flight** (`tools/r2b_steps.py`) lays one to three slabs a tread, its joints clear of those below, each slab settled (its front sunk, rolled, turned). Every number is in the definition (`step.json`) or the working (`walling.json`, its steps).
- **The look:** `step/round01-sheet.jpg` is the start: plywood laminae, sharp nosings, a machined notch. `round08` passed the look, beside reference 06 in grey and in drizzle; `round11` is its patch after the strict review (below), its losses now sunk pockets (`round11-pockets.jpg`). In `lights-sheet.jpg` (round 08's) it holds in morning shade, low sun and blue hour, from eye level and the street stop to 12 m raised and near-isometric.
- **Budget:** L0 is at most 292 triangles by construction (nine front points at most). Over three seeds of 14 steps on a 2.3 m flight it is 62 to 262, under the 300 budget; `r2b_steps.py` fails any slab over it.
- **Switch:** L1 is L0. In low sun from 6 to 18 m, an L1 of one lamina, a one-facet round and no wear rows changed 8.6 to 28% of the flight's pixels by more than 3 L*. With its laminae and flake kept it changed 2.8 to 15%, and with only the round's middle facet dropped, 1.1 to 5.6% (`switch-d9-l0-round1facet-diff.jpg`). The step hands over to the chunk's L2.
- **Open:** `slabstep.py` is not yet wired into `context.py`. The joints between a tread's slabs are straight slots, where reference 06's are cracks.
- **Cost:** about 45 messages and 76 rendered frames.

## The coping: done, 26 October

- **The part:** `slabstep.py:coping`, the step's slab laid flat across a wall's top, sharing the step's faces and round, which stay byte-identical. Its front and back are split across one to three laminae. Its top's arris is rounded by the weather alone, and here and there a flake of the top is lost. It is thicker at one end and to one side. An open end is square and knocked; a joint end is ragged against the next. `r2b_wall.py --coping` lays the run level on the wall's top, whose top course is picked to the line; where a stone falls short, thin pinnings pack it. Its values are the coping's definition's and the working's (`copeVaryMm`, `copeSetDeg`, `copeBedMm`, `pin*`).
- **The look:** `coping/round01-sheet.jpg` is the start: a precast cap, ruler-straight. `round03` read as extruded plates. `round06` passed the look, beside study reference 33's level run in grey and in drizzle; `round08` is its patch after the strict review (below), the bed packed tight; `round06-end-sheet.jpg` shows the run's square end beside reference 29. In `lights-sheet.jpg` it holds in morning shade, low sun and blue hour, from eye level to near-isometric.
- **Budget:** L0 measured 36 to 220 triangles over 600 slabs (median 116), and 60 to 234 over 245 after the patch, under 240 (R2a's 120 had no laminae). `r2b_wall.py` fails any slab over it.
- **Switch:** L1 is L0. On the run alone, in low sun from 6 to 18 m, dropping only the round's middle facet changed 6.9 to 1.4% of its pixels by more than 3 L*, and one lamina changed 16.8 to 5.8% (`switch-d9-l0-noring-diff.jpg`).
- **Open:** `slabstep.py:coping` is not yet wired into `context.py`. The wall's end in the panel is a cut, not a head.
- **Cost:** about 40 messages and 50 rendered frames.

## The strict review: passed, 26 October

- **On Fable,** from each stone's final sheet, its lights sheet and these lines. The wall stone passed. The step and the coping were "fix, patch". The step's lost flakes read as raised outlines; they are now sunk pockets with a sharp back break (`step/round11-sheet.jpg`, `round11-pockets.jpg`). The coping hovered on a void band; its top course is now picked to the line and its bed packed tight (`coping/round08-sheet.jpg`). Fable's re-review passed both.
- **Left for a later round:**
  - The step's back breaks are straight polygons where a spall runs ragged and curved. Where the nosing's round stops at a pocket's slanted end, a crease shows like a saw kerf. The nosings vary as a softer or firmer bullnose, never as reference 06's chipped arris.
  - Along the coping's run, the packed dips come about one stone in two, not one in five. The pinnings are bright, even chips, where real ones sit back in shadow.
- **Open, beyond the three parts:**
  - Sameness, "the most of anything here": neighbouring stones are one value, so from 6 m the wall is a dark band, not stones. Fable's fix is a per-stone seed on the mesh, read by the material for about ±12 L* albedo and a lichen-cover bias, plus ±3° pitch in the laying.
  - The lichen: turn `Growth.hlsl` round (a pale crust with dark specks) before the gully is judged.
  - The set: the wall stone reads as blockier field rubble in the step's material. It needs laminated ends from the step's lamina function and a flatter face, or its own material.
- **Cost of the patches:** about 30 messages and 10 rendered frames. The reviews rendered none.

## The gully: the three stones laid, 26 October

- **Wired in:** `tools/r2b_gully.py` builds R1's gully laying with R2b's parts: the wall stones on each battered face, the copings and topstones, the step, rest and landing slabs, and the joints' soil. `context.py` builds only R2a's specimens, so the gully is a new export. `LT1R2b.Gully` draws it in place of the old gully, in memory only. The old FBX stays the regression reference. New hashes: walls `ff3fdbde119918d7` (125,350 triangles) and slabs `c8f1e87bf5da09bf` (50,834). Every piece is within budget. The walls and copings come to 143,030, 9% over the wall kind's L0 of 131,100: the kind assumed 40 triangles a stone where R2b's mean is 45, and the step ends add more. The gully's whole (176,184) is under R1's 182,100.
- **The look:** `gully/round01-sheet.jpg` is the start. The copings hung like ladder rungs over a hollow wall, so end stones now close each step in the wall's top. `round02-sheet.jpg` is the final round, beside the target in grey and in drizzle. `round02-eye-foot.jpg` shows the crust near. `lights-sheet.jpg` holds in drizzle, low sun and blue hour, from eye level, the street stop and 12 m.
- **Sameness:** each stone's seed comes from its stable id (UV1.y). `Stone.shader`'s new `_Piece` reads it for ±12 L* of value, applied in L* outside the old clamp, which could only darken. It also gives ±35% of lichen share. The amounts are in `slate.json`'s `piece`. The laying already pitches each stone −5° to +4° (`setPitchDeg`), so the pitch is unchanged.
- **The lichen:** `Growth.hlsl` now uses `_OS_LichenRate.z` (0.85) as what its comment says it is, the share of a quiet surface. The code had held it to a third. On a century's quiet stone the crust is now the surface, flecked dark with fruit and plate lines, with rock showing through in gaps. `growth-old-gully.jpg` shows the old gully's slate and rubble under it, with nothing broken. Only the variety sheet places granite, and it writes tracked frames, so granite was not rendered. It shares the same code path.
- **Open:** in the gully's shade the walls read darker and bluer than the target's, which is painted in lamplight. The wall stone still wears the rubble material (the set's open point above). At middling cover, the lichen on the treads still falls into fields. At each step, the copings read as thin plates.
- **Cost:** about 115 messages and 34 rendered frames.
